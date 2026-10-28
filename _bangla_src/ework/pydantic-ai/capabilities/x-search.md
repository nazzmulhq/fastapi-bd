
# X Search { #x-search }

/// note | এই পেজে যা শিখবেন

* `XSearch` capability দিয়ে X (Twitter)-এর পোস্টে সার্চ — শুধু xAI মডেলে নেটিভ।
* অন্য মডেলে `fallback_subagent_model` দিয়ে একটি xAI subagent-কে সার্চের কাজ দেওয়া।
* `native=` factory, `None` ফেরত দেওয়া আর Temporal-এর অধীনে আচরণ।

///

[`XSearch`][pydantic_ai.capabilities.XSearch] [capability](overview.md) আপনার এজেন্টকে X (Twitter) পোস্টে সার্চ দেয়। এটি একটি [provider-অনুযায়ী টুল](overview.md#provider-adaptive-tools), নেটিভ দিকে [`XSearchTool`][pydantic_ai.native_tools.XSearchTool]-চালিত — কনফিগারেশন অপশনের জন্য দেখুন [X Search Tool](../native-tools.md#x-search-tool)।

[Web Search](web-search.md) আর [Web Fetch](web-fetch.md)-এর বিপরীতে, কোনো ডিফল্ট non-xAI বিকল্প নেই: X সার্চ শুধু xAI মডেলে নেটিভভাবে পাওয়া যায়। আপনার এজেন্ট একটি xAI মডেলে না চললে, `fallback_subagent_model` স্পষ্টভাবে এমন একটি xAI মডেলে সেট করুন যা [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] সমর্থন করে, আর সার্চ রিকোয়েস্ট একটি subagent টুল হিসেবে সেই মডেলকে দেওয়া হয়:

⟦CODE1⟧

/// tip | উদাহরণ দিয়ে বুঝি

আপনার এজেন্ট Claude-এ চলে, কিন্তু X-এ খোঁজার ক্ষমতা শুধু Grok (xAI)-এর আছে। `fallback_subagent_model='xai:...'` দিলে Claude দরকার হলে একটি "সার্চ টুল" ডাকে, যা পর্দার আড়ালে একটি ছোট Grok এজেন্ট চালিয়ে X-এ খোঁজে আর ফল Claude-কে দেয়। Claude-এর মনে হয় সে নিজেই একটা টুল ডেকেছে।

///

/// note | `fallback_model` অবচিত

`fallback_model` হলো `fallback_subagent_model`-এর আগের নাম। এটি কাজ করতে থাকে, Python-এ আর একটি [agent spec](../agent-spec.md)-এ, আর সতর্ক করে; দুটি নাম একসাথে দেওয়া প্রত্যাখ্যাত: capability তৈরির সময় [`UserError`][pydantic_ai.exceptions.UserError], আর একটি spec লোড করার সময় spec loader এটিকে যে `ValueError`-এ মোড়ায়।

///

`native=` একটি factory হতে পারে: [`RunContext`][pydantic_ai.tools.RunContext] নিয়ে [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] বা `None` ফেরত দেওয়া একটি callable — [`XSearchNativeTool`][pydantic_ai.common_tools.x_search.XSearchNativeTool] হলো `fallback_subagent_model` subagent যে টাইপ গ্রহণ করে। এটি প্রতিটি মডেল রিকোয়েস্টে মীমাংসা হয়, আর subagent চলার সময় আবার — তাই একে এককালীন side effect-মুক্ত রাখুন। দুটি মীমাংসাই একই রানের আর একই `deps` বহন করে, কিন্তু একটি [`RunContext`][pydantic_ai.tools.RunContext] ভাগ করে না: subagent এর নিজের টুল কল থেকে মীমাংসা করে, তাই `tool_call_id` আর `tool_name` `None` না হয়ে সেই কলের নাম দেয়, আর `messages` এ পর্যন্ত রান রাখে। দুটোতে মিলতে হবে এমন কনফিগারেশনের জন্য `ctx.deps` পড়ুন। subagent-এ, `include_output`-এর মতো capability-স্তরের ফিল্ড factory-র ফল override করে। দেখুন [Dynamic Configuration](../native-tools.md#dynamic-configuration)।

/// note | `None` ফেরত দেওয়া একটি factory

`None` সেই রিকোয়েস্টের জন্য টুল বাদ দেয় শুধু তখনই যখন কোনো `fallback_subagent_model` সেট নেই। একটি `fallback_subagent_model`-সহ, factory `None` ফেরত দিলেই subagent টুল মডেলকে দেওয়া হয় — এমনকি নেটিভভাবে [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] সমর্থন করা একটি মডেলেও — আর একে ডাকলে ডিফল্ট সেটিং দিয়ে X-এ সার্চ না করে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

///

/// note | Temporal-সহ durable execution

`fallback_subagent_model` subagent-এর টুল কল একটি Temporal activity-র ভেতরে চলে, তাই সেখানে মীমাংসা হওয়া একটি `native=` factory সীমিত [`TemporalRunContext`][pydantic_ai.durable_exec.temporal.TemporalRunContext] পায়: `ctx.messages`, বা Temporal বহন করে না এমন অন্য কোনো ফিল্ড পড়লে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে। `ctx.deps` সীমা পার হয়, তাই factory শুধু `deps` পড়ুক। কোন ফিল্ড উপলব্ধ তা দেখুন [Agent Run Context and Dependencies](../durable_execution/temporal.md#agent-run-context-and-dependencies)-এ। [DBOS](../durable_execution/dbos.md) আর [Prefect](../durable_execution/prefect.md) জীবন্ত `RunContext` দেয় আর প্রভাবিত হয় না।

///

/// check | সংক্ষেপে মনে রাখুন

* `XSearch()` শুধু xAI মডেলে নেটিভ; অন্য মডেলে `fallback_subagent_model='xai:...'` দিন।
* `native=` factory প্রতি রিকোয়েস্টে আর subagent-এ আবার মীমাংসা হয় — side effect-মুক্ত রাখুন, শুধু `ctx.deps` পড়ুন।
* `fallback_subagent_model` থাকলে factory-র `None` টুল বাদ দেয় না, ডাকলে `UserError`।

///
