
# On-Demand Capability { #on-demand-capabilities }

/// note | এই পেজে যা শিখবেন

* `defer_loading=True` দিয়ে একটি capability-কে এক লাইনের ক্যাটালগ entry-তে গুটিয়ে রাখা, যা মডেল দরকার হলে `load_capability` দিয়ে খোলে।
* কী কী defer করা যায় (instructions, টুল, model settings, hook, নেটিভ টুল), আর কখন এটি ব্যবহার করবেন।
* রান জুড়ে আবার চালানো, `RunContext`-এর state, provider-ভেদে আচরণ আর prompt cache-এর প্রভাব।
* Markdown skill ফাইল থেকে capability লোড আর "আগে পড়ো, তারপর কাজ" নিয়ম প্রয়োগ।

///

একটি capability হলো instructions আর/বা টুলের একটি বান্ডেল, ঐচ্ছিকভাবে সেটিং আর hook-সহ। একটি বহু-workflow এজেন্ট সাধারণত প্রতিটি turn-এ প্রতিটি workflow-এর instructions আর tool schema পাঠায়, আর পুরো রানের জন্য প্রতিটি workflow-এর সেটিং আর hook প্রয়োগ করে — যদিও বেশিরভাগ রিকোয়েস্টে মাত্র একটি workflow লাগে। প্রতিটি workflow যোগ করার সাথে এই খরচ বাড়ে: বেশি input token, আর দৃশ্যমান টুলের সংখ্যা ~30–50-টুলের সীমা পেরোলে খারাপ টুল বাছাই, যেখানে মডেল ভুলটি বাছতে শুরু করে (একই চাপ [tool search](../tools-advanced.md#tool-search)-এর পেছনে)।

একটি [capability](overview.md)-কে `defer_loading=True` দিয়ে চিহ্নিত করুন আর একটি স্থিতিশীল `id` দিন, আর এটি একটি এক-লাইনের ক্যাটালগ entry-তে গুটিয়ে যায় — এর `id` আর একটি ঐচ্ছিক `description` — যা মডেল চাহিদামতো টেনে আনে। ন্যূনতম সেটআপ:

⟦CODE1⟧

/// tip | উদাহরণ দিয়ে বুঝি

একটি রেস্তোরাঁর মেনুর মতো: মেনুতে শুধু খাবারের নাম আর এক লাইনের বর্ণনা থাকে ("রিফান্ড — অর্ডারের টাকা ফেরত")। পুরো রেসিপি (instructions), বিশেষ যন্ত্রপাতি (টুল) আর রান্নার সেটিং রান্নাঘরে থাকে। অতিথি (মডেল) একটি খাবার অর্ডার করলে (`load_capability`), তখনই রান্নাঘর থেকে সেটার সবকিছু বের হয়। প্রতিটি টেবিলে সব রেসিপির বই রাখতে হয় না।

///

প্রথম turn-এ, refund workflow একটি ক্যাটালগ entry-তে গুটিয়ে থাকে। মডেল এর মূল instructions, framework-পরিচালিত `load_capability` টুল আর instructions-এর সাথে যুক্ত ক্যাটালগ দেখে:

⟦CODE2⟧

ক্যাটালগে tag দেওয়া থাকে, যাতে একটি কথোপকথনের রানের মাঝে এটি বদলালে, যেমন একটি capability যোগ হওয়ায়, পরিবর্তনটি cache করা prompt নতুন করে না লিখে [যুক্ত](../agent.md#appending-instruction-changes) হয়।

মডেল এখনও refund instructions বা `refund_status` টুল সংজ্ঞা পায় না, তাই এর টুলটি ডাকার কোনো কারণ নেই। সক্রিয় মডেলের ওপর নির্ভর করে, লুকানো state রক্ষা করতে Pydantic AI provider/tool-search-এর কিছু ব্যবস্থাও পাঠাতে পারে; capability লোড না হওয়া পর্যন্ত সেই ব্যবস্থা refund টুল সংজ্ঞা প্রকাশ করে না। আদান-প্রদানটি একটি একক `agent.run_sync` কলের ভেতরে মডেল রিকোয়েস্ট জুড়ে এভাবে ঘটে:

1. **রিকোয়েস্ট 1.** মডেল ওপরের ক্যাটালগ আর ব্যবহারকারীর prompt দেখে। এটি `id='refunds'` দিয়ে `load_capability` টুল ডাকে।
2. **লোড।** Pydantic AI capability-র instructions — *"Always confirm the order ID before issuing a refund."* — টুলের ফল হিসেবে ফেরত দেয় আর পরের রিকোয়েস্টে `refund_status` সংজ্ঞা প্রকাশ করে।
3. **রিকোয়েস্ট 2.** মডেল এখন ইতিহাসে ওই instructions আর এর টুল তালিকায় `refund_status` দেখে। এটি `refund_status(order_id='ABC-123')` ডাকে আর ফল থেকে ব্যবহারকারীকে উত্তর দেয়।

ইতিমধ্যে লোড হওয়া capability রানের বাকি সময় লোড থাকে — মডেলকে কখনো একটি আবার খুলতে হয় না। ইতিমধ্যে সক্রিয় একটি capability-র জন্য, বা একই response-এর আগের একটি কল ইতিমধ্যে লোড করছে এমন একটির জন্য একটি `load_capability` টুল কলের উত্তর এর instructions-এর দ্বিতীয় কপির বদলে একটি retry prompt দিয়ে দেওয়া হয়।

সার্চ একটি capability-র মালিকানাধীন টুল প্রকাশ করতে পারে না: এর capability লোড না হওয়া পর্যন্ত এটি লুকানো থাকে। যে রানে সার্চযোগ্য deferred টুলও আছে, সেখানে ক্যাটালগ মডেলকে স্পষ্টভাবে এর টুল খোঁজার বদলে capability লোড করতে বলে; শুধু-capability রানে — যেখানে কোনো সার্চ পৃষ্ঠতল নেই — ক্যাটালগ সার্চের কোনো উল্লেখ বাদ দেয়।

লোড করা শুধু instructions নয়, পুরো বান্ডেল সক্রিয় করে: capability-র ফাংশন টুল, model settings আর lifecycle hook একসাথে চালু হয় (দেখুন [What you can defer](#what-you-can-defer))। আপনি ইতিমধ্যে নিবন্ধন করা একটি capability-তে এটি এক লাইনের পরিবর্তন, এটি [প্রতিটি provider-এ](#cross-provider-behavior) কাজ করে, আর এটি [history replay-তে টিকে থাকে](#resumable-across-runs)।

/// note | মনে রাখুন

যেকোনো on-demand capability উপস্থিত থাকলে `load_capability` টুলের নাম সংরক্ষিত। Capability-র `id` মান স্থিতিশীল হতে হবে — একটি স্পষ্টভাবে সেট করুন, যদি না capability নিজেই একটি স্থিতিশীল `id` তৈরি করে, যেমন [`MCP`][pydantic_ai.capabilities.MCP] এর সার্ভার URL থেকে করে। দেখুন [Resumable across runs](#resumable-across-runs)।

///

/// note | Deferred instructions client-মুখী message history-তে পৌঁছায়

একটি deferred capability-র instructions `load_capability` টুলের *ফল* হিসেবে ফেরত আসে, তাই এগুলো রানের message history-তে পড়ে — একটি [UI adapter](../ui/overview.md) client-এ যে কপি serialize করে সেটিসহ। একটি সবসময়-চালু capability-র instructions এর বদলে সার্ভার-পক্ষের system prompt-এ থাকে। একটি capability-র instructions client-এর কাছে প্রকাশ করা উচিত না হলে, এটি deferred না রেখে সবসময়-চালু রাখুন।

যেহেতু এগুলো [`InstructionPart`][pydantic_ai.messages.InstructionPart] হিসেবে নয় বরং টুল-ফলের লেখা হিসেবে আসে, এগুলো [`id`][pydantic_ai.messages.InstructionPart.id] দিয়েও চিহ্নিত করা যায় না: `ModelRequestParameters.instruction_parts` নতুন করে লেখা একটি `before_model_request` hook কখনো এগুলো দেখে না, তাই এর ওপর তৈরি যেকোনো কিছু — দূরের instruction override-সহ — একটি সবসময়-চালু capability-র instructions-এ পৌঁছায় কিন্তু একটি deferred-এরটিতে নয়। একটি capability-র instructions চিহ্নিতযোগ্য থাকা দরকার হলে এটি সবসময়-চালু রাখুন।

///

## যা defer করা যায় { #what-you-can-defer }

একটি capability বান্ডেলের প্রতিটি অংশ একটি একক হিসেবে একসাথে সক্রিয় হয়:

| অংশ | লোডের আগে | লোডের পরে |
|---|---|---|
| Instructions (স্থির বা গতিশীল) | পাঠানো হয় না | `load_capability` টুলের ফল হিসেবে ফেরত; পরের রিকোয়েস্টে অন্তর্ভুক্ত |
| ফাংশন টুল | প্রকাশিত নয় | পরের রিকোয়েস্টে প্রকাশিত |
| Model settings (স্থির বা প্রতি-step) | প্রয়োগ হয় না | পরের রিকোয়েস্টের জন্য রানের সেটিংয়ে মেলানো |
| Lifecycle [hooks](custom.md#hooking-into-the-lifecycle) | চলে না | capability লোডের পর চলে |
| [Native tools](../native-tools.md) | প্রকাশিত নয় | পরের রিকোয়েস্টে প্রকাশিত — দেখুন [Cache implications](#cache-implications) |

## কখন ব্যবহার করবেন { #when-to-use-it }

**On-demand capability ব্যবহার করুন যখন:**

- এজেন্ট একাধিক আলাদা workflow পরিবেশন করে (refund, return, fraud পর্যালোচনা, account নিরাপত্তা…), যেখানে বেশিরভাগ turn-এ একটি লাগে
- একটি workflow-এর *instructions-এর চেয়ে বেশি* লাগে — নিজের টুল, বাড়ানো reasoning effort, একটি অনুমোদন hook — আর সেগুলো একক হিসেবে একসাথে যাওয়া উচিত
- আপনি skill-ধরনের ধাপে ধাপে প্রকাশ চান, কিন্তু লোড হওয়া বান্ডেল শুধু একটি runbook নয়, টুল আর সেটিংও আনুক

**বাদ দিন যখন:**

- capability বেশিরভাগ turn-এ ব্যবহৃত হয় — খোঁজার round-trip-এর খরচ এটি যে token বাঁচায় তার চেয়ে বেশি
- আপনার কাছে কোনো ভাগ করা instructions ছাড়া আলাদাভাবে খোঁজা-যোগ্য টুলের একটি সমতল ক্যাটালগ আছে — এর বদলে [tool search](../tools-advanced.md#tool-search) ব্যবহার করুন, যা বান্ডেল লোড না করে নাম দিয়ে আলাদা টুল খোঁজে

আপনি [Anthropic-এর Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) ব্যবহার করে থাকলে, এটি একই ধারণার সাধারণীকৃত রূপ: একটি skill হলো একটি markdown ফাইল যা মডেল চাহিদামতো টেনে আনতে পারে। একটি on-demand capability তা করে, *সাথে* টাইপ করা ফাংশন টুল, প্রতি-step model settings আর lifecycle hook।

## একটি বিদ্যমান capability-তে যোগ করা { #retrofitting-an-existing-capability }

`defer_loading=True` [`Capability`][pydantic_ai.capabilities.Capability] সুবিধাজনক ক্লাসের জন্য নির্দিষ্ট নয়। ভাগ করা ফিল্ডগুলো থাকে [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability]-এ, আর বিল্ট-ইন capability তৈরির সময় `id`, `description` আর `defer_loading` দেয়। নিজস্ব capability-র জন্য, instance-এ ওই attribute সেট করুন।

⟦CODE3⟧

মডেল `analytics-mcp` লোড না করা পর্যন্ত, MCP সার্ভারের কোনো টুল সংজ্ঞা prompt-এ ঢোকে না। একই flag কাজ করে [`WebSearch`][pydantic_ai.capabilities.WebSearch], [`WebFetch`][pydantic_ai.capabilities.WebFetch], [`Hooks`][pydantic_ai.capabilities.Hooks] আর যেকোনো নিজস্ব [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass-এ — নিজের subclass-এ `defer_loading` যোগ করতে দেখুন [Building custom capabilities](custom.md)।

/// note | Deferred `MCP`: একটি স্থিতিশীল `id` সেট করুন

আপনি একটি না দিলে [`MCP`][pydantic_ai.capabilities.MCP] সার্ভার URL থেকে এর `id` তৈরি করে, তাই স্পষ্ট `id` ছাড়াই `defer_loading=True` কাজ করে। তবুও একটি দিন, যদি আপনি কথোপকথন সংরক্ষণ করে [আবার চালান](#resumable-across-runs): URL-থেকে-তৈরি একটি id URL বদলালে বদলে যায় (ভিন্ন environment, path version, …), যা আবার চালানো capability-র লোড হওয়া state নিঃশব্দে ভেঙে দেয়।

///

## রান জুড়ে আবার চালানো যায় { #resumable-across-runs }

লোড-হওয়া-capability আর টুল-উপলব্ধতার state থাকে message history-তে, এজেন্টে নয়। একটি কথোপকথন একটি ডেটাবেসে সংরক্ষণ করে পরে আবার চালালে — হয়তো একটি ভিন্ন process, মেশিন বা মডেলে — Pydantic AI `load_capability` কল/ফেরত জোড়া থেকে লোড হওয়া capability ID আর [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart] থেকে প্রকাশিত টুলের নাম আবার তৈরি করে। মডেল আগে যে capability লোড করেছিল সেগুলো লোড থাকে; যেগুলো কখনো লোড করেনি সেগুলো ক্যাটালগে গুটিয়ে থাকে। আবার চালানোর সময় আবার খোঁজার কোনো round-trip নেই।

এজন্যই deferred capability-র একটি স্থিতিশীল স্পষ্ট `id` লাগে: history replay id দিয়ে কলকে capability-র সাথে মেলায়, তাই একটি ক্লাস-থেকে-তৈরি id একটি ক্লাসের নাম বদলানোর মুহূর্তে নিঃশব্দে ভেঙে যেত। একই বৈশিষ্ট্য provider-জুড়ে replay কাজ করায় — Anthropic-এ `refunds` লোড করে OpenAI Responses-এ চালিয়ে যাওয়া একটি রান বদলের পর `refunds` লোড রাখে।

ইতিহাস বহন করে *কোন* capability id লোড হয়েছিল, capability-গুলো নিজে নয়: আবার চালানো এজেন্ট একই capability (মিলে যাওয়া `id`) দিয়ে তৈরি হতে হবে, ঠিক যেমন এটি একই টুল দিয়ে তৈরি হতে হয়। State থাকে ইতিহাসে; সংজ্ঞা থাকে কোডে।

## `RunContext`-এ রানের সময়ের state { #runtime-state-in-runcontext }

কয়েকটি [`RunContext`][pydantic_ai.tools.RunContext] ফিল্ড টুল, hook আর capability-র মালিকানাধীন callback-এ ধাপে ধাপে-প্রকাশের state দেখায়:

- `ctx.loaded_capability_ids` — `load_capability` টুল দিয়ে স্পষ্টভাবে লোড হওয়া deferred capability ID, প্রতিটি মডেল রিকোয়েস্টের আগে message history থেকে আবার তৈরি। একটি step-এর সময় লোড হওয়া একটি capability *পরের* step থেকে দেখা দেয়, যা সেই প্রথম step-ও যেখানে এর instructions আর টুল মডেলে পৌঁছায়।
- `ctx.active_capability_ids` — বর্তমানে চালু capability ID: সবসময়-চালু capability আর `ctx.loaded_capability_ids`।
- `ctx.capability_active` — শুধু তখনই অর্থপূর্ণ যখন Pydantic AI একটি capability-র মালিকানাধীন hook বা callback চালাচ্ছে। এটি সেই capability-র পরিসরে; এই মান সত্য না হওয়া পর্যন্ত deferred hook আর callback বাদ পড়ে। সক্রিয়, লোড নয়: একটি সবসময়-চালু capability-র hook `True` পড়ে, যদিও কিছুই এটি লোড করেনি।
- `ctx.discovered_tool_names` — টেকসই ইতিহাস দিয়ে প্রকাশিত deferred ফাংশন টুল, tool search, [`ToolReturn.tools`][pydantic_ai.messages.ToolReturn] বা একটি capability লোড — যেভাবেই হোক।
- `ctx.available_tool_names` — বর্তমানে উপলব্ধ হিসেবে জানা ফাংশন টুলের নাম: বর্তমান step-এর গঠিত tool manager-এর সবসময়-দৃশ্যমান টুল আর ইতিহাসে প্রকাশিত নাম। `before_run`-এর মতো শুরুর দিকের hook টুল সংজ্ঞা প্রস্তুত হওয়ার আগে হয়তো শুধু ইতিহাস-থেকে-তৈরি নাম দেখে, বা কিছু না থাকলে একটি খালি সেট। hook-এর সময় কী পূরণ হয় তাতে কীভাবে প্রভাব ফেলে তা দেখুন [Hook ordering](../hooks.md#hook-ordering)-এ।
- `ctx.is_tool_available(tool)` — একটি ফাংশন টুল বর্তমানে দৃশ্যমান কিনা। মোড়ানো toolset-এর উচিত তাদের ধরে রাখা [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] দেওয়া; model-request hook আর টুল চালানো বর্তমান `ctx.tools` snapshot থেকে একটি নাম দিতে পারে।
- `ctx.usage_limits` — রান যে [`UsageLimits`][pydantic_ai.usage.UsageLimits] প্রয়োগ করছে (কিছু না দিলে ডিফল্ট `UsageLimits()`, তাই এটি শুধু একটি রানের বাইরে `None`), এ পর্যন্ত usage-এর জন্য `ctx.usage`-এর পাশাপাশি। একটি capability রানের সীমা পড়ে বাকি বাজেট প্রকাশ বা এর সাথে মানিয়ে নিতে পারে (যেমন বাজেট প্রকাশ), একটি নকল কপি দিয়ে কনফিগার না হয়েই। একে শুধু-পড়া ধরুন: এটি সেই জীবন্ত অবজেক্ট যার বিপরীতে রান প্রয়োগ করে, তাই একটি ফিল্ড বদলালে পরের রিকোয়েস্টে রান যা প্রয়োগ করে তা বদলে যাবে।

একটি capability লোড করা capability state সাথে সাথে হালনাগাদ করে, কিন্তু লোড হওয়া বান্ডেলের ফাংশন টুল, নেটিভ টুল আর model settings পরের মডেল রিকোয়েস্টে কার্যকর হয়।

## Provider-ভেদে আচরণ { #cross-provider-behavior }

On-demand capability প্রতিটি মডেলে কাজ করে, আর যেখানে provider একটি উপলব্ধতা-পরিবর্তন নেটিভভাবে প্রকাশ করতে পারে, সেখানে একটি লোড করলে prompt prefix অক্ষত থাকে।

একটি capability-র মালিকানাধীন টুল এর capability লোড না হওয়া পর্যন্ত লুকানো থাকে, আর এটি কখনো সার্চযোগ্য নয় — মডেল একে চেয়ে নয়, capability লোড করে পৌঁছায়। একীভূত নিয়ম হলো একটি অপ্রকাশিত deferred টুল মডেলের ব্যবহারযোগ্য context-এর বাইরে থাকে; প্রতিটি provider-এর প্রকাশ-পদ্ধতি এর wire রূপ ঠিক করে।

- **Anthropic `tool_addition_mode='by_reference'`** একটি `tool_addition` ব্লকে প্রকাশিত নামের রেফারেন্স দেয়। একটি শুধু-capability রান `defer_loading=True` দিয়ে সংজ্ঞা আগে থেকে বিজ্ঞাপিত করে; একটি সার্চ পৃষ্ঠতলসহ মিশ্র রান এটি আটকে রাখে, তারপর প্রকাশের একই রিকোয়েস্টে deferred সংজ্ঞা যুক্ত করে।
- **OpenAI Responses `tool_addition_mode='with_definitions'`** একটি যুক্ত `additional_tools` input item-এ পুরো প্রকাশিত সংজ্ঞা বহন করে আর `tools` থেকে এটি বাদ রাখে।
- **কোনো provider-নেটিভ reveal-item সমর্থন নেই (`tool_addition_mode=None`)** schema দৃশ্যমান হলে `The following tool(s) are now available: {names}` ঘোষণা করে। একটি দূরের MCP সার্ভার নিজের টুলের নাম বাছে, তাই যে টুলের নামে `</system>`-এর মতো একটি framing tag আছে তা তবুও পাঠানো হয় কিন্তু ঘোষণায় নাম দেওয়া হয় না। এটি একটি `search_tools` আদান-প্রদান তৈরি করে শুধু তখনই যখন একটি ফলকে এমন একটি schema প্রকাশ করতে হয় যা এখনও আটকানো।

একই রানে একটি আলাদা `defer_loading=True` টুল যোগ করুন, আর এর জন্য tool search ফিরে আসে, যেহেতু সেটি সত্যিই সার্চযোগ্য। একটি সার্চ পৃষ্ঠতল উপস্থিত থাকার সময় capability-র মালিকানাধীন টুল পুরোপুরি wire-এর বাইরে থাকে, তাই সার্চ পুরোপুরি নেটিভ থাকে — যেখানে মডেল সমর্থন করে সেখানে সার্ভারে চলে — আর কোনো query এমন একটি টুল প্রকাশ করতে পারে না যার capability লোড হয়নি।

### Cache-এর প্রভাব { #cache-implications }

`load_capability` টুল ডাকা রিকোয়েস্টের মাঝে capability-র আচরণ প্রকাশ করে। এটি provider-এর prompt-cache prefix ভাঙে কিনা তা নির্ভর করে কী প্রকাশিত হচ্ছে তার ওপর:

`load_capability` লোড হওয়া capability-র ফাংশন-টুলের নাম [`ToolReturn.tools`][pydantic_ai.messages.ToolReturn] দিয়ে ফেরত দেয়, আর executor টুলের ফলের পাশে উপলব্ধতার পরিবর্তন (delta) লেখে। যেকোনো ব্যবহারকারী টুল একই উৎস ব্যবহার করতে পারে। এর delta ছাড়া একটি সম্পূর্ণ capability-লোড আদান-প্রদান থাকা ইতিহাস পরের মডেল রিকোয়েস্টের আগে অনূদিত হয়।

| যা লোড হয় | Cache prefix |
|---|---|
| শুধু instructions | **স্থির** — instructions message history-তে পড়ে, রিকোয়েস্ট prefix-এ নয়। |
| provider-নেটিভ reveal-item সমর্থনসহ ফাংশন টুল (`tool_addition_mode='by_reference'` বা `'with_definitions'`) | **Anthropic আর OpenAI Responses-এ স্থির** — deferred Anthropic entry এর cache key-র বাইরে, আর OpenAI Responses `tools[]` না বদলে `additional_tools` যুক্ত করে। |
| provider-নেটিভ reveal-item সমর্থন ছাড়া ফাংশন টুল (`tool_addition_mode=None`, যেমন OpenAI Chat Completions) | **প্রতি লোডে একবার ভাঙে** — লোড হওয়া টুল `tools[]`-এ যোগ হয়, যা ইতিমধ্যে পাঠানো বার্তার আগে আসে, তাই লোডের পরের রিকোয়েস্টে prefix সরে যায় আর তখন থেকে স্থির থাকে। |
| নেটিভ টুল | **লোডে সবসময় prefix ভাঙে** — নেটিভ টুল সংজ্ঞা প্রতিটি provider-এ রিকোয়েস্ট prefix-এর অংশ। |
| লোড ছাড়া দেখা দেওয়া ফাংশন টুল (একটি capability-র dynamic toolset বা MCP সার্ভার রানের মাঝে একটি টুল যোগ করছে) | **first-party OpenAI Responses-এ আর tool search-সহ Anthropic মডেলে স্থির**, একটি ব্যতিক্রমসহ: এই Anthropic মডেলের কিছু একটি এককালীন ভূমিকা যোগ করে যখন একটি রানের প্রথম deferred টুল একজন নবাগত, যা সেই রিকোয়েস্টে prefix সরায়। অন্যত্র টুলটি `tools[]`-এ যোগ হয়। পরিবর্তনটি একটি উপলব্ধতা delta হিসেবে লেখা হয়; দেখুন [Tools that appear mid-run](../tools-advanced.md#mid-run-tool-additions)। |

GPT-5.6-এর আগের OpenAI Responses মডেলে, যে রিকোয়েস্টের `tool_choice` একটি প্রকাশিত টুলের নাম দেয় তা এটি `tools`-এ ঘোষণা করে আর cache miss করে; দেখুন [Prompt caching implications](../tools-advanced.md#tool-choice-caching)। `openai_previous_response_id` বা `openai_conversation_id` সেট থাকলে, টুলটি `tools`-এর বাইরে থাকে আর API রিকোয়েস্ট প্রত্যাখ্যান করে; দেখুন [Tool Choice](../tools-advanced.md#tool-choice)।

cache prefix রক্ষা জরুরি হলে, এমন একটি মডেলে শুধু-instructions বা শুধু-ফাংশন-টুল on-demand capability পছন্দ করুন যা নেটিভভাবে একটি উপলব্ধতা-পরিবর্তন প্রকাশ করতে পারে। prefix স্থির রাখার provider-নির্দিষ্ট কৌশল আছে [Tool search and prompt caching](../tools-advanced.md#tool-search-caching)-এ।

## `Capability` সুবিধাজনক ক্লাস { #the-capability-convenience-class }

[`Capability`][pydantic_ai.capabilities.Capability] subclass ছাড়াই instructions, ফাংশন টুল আর toolset একত্র করে। [`@agent.tool`](../tools.md#registering-function-tools-via-decorator)-এর প্রতিচ্ছবি decorator দিয়ে টুল নিবন্ধন করুন:

⟦CODE4⟧

`@capability.tool` আর `@capability.tool_plain` ছাড়াও, আপনি `tools=` দিয়ে বিদ্যমান ফাংশন বা [`Tool`][pydantic_ai.tools.Tool] instance দিতে পারেন, বা `toolsets=` দিয়ে এক বা একাধিক [toolsets](../toolsets.md) দিতে পারেন। গতিশীল instructions-এর জন্য, [`@capability.instructions`][pydantic_ai.capabilities.Capability.instructions] decorator ব্যবহার করুন। একটি গতিশীল ক্যাটালগ entry-র জন্য, `description=` হিসেবে একটি callable দিন।

`@capability.tool` আর `@capability.tool_plain` হুবহু [`@agent.tool`](../tools.md#registering-function-tools-via-decorator)-এর প্রতিচ্ছবি, `defer_loading` আর্গুমেন্টসহ। একটি deferred capability-তে ওই প্রতি-টুল flag-এর কোনো প্রভাব নেই — capability এর সব টুল একটি একক হিসেবে নিয়ন্ত্রণ করে — তাই এর প্রভাব শুধু একটি non-deferred `Capability`-তে, যেখানে এটি একটি একক টুলকে [tool search](../tools-advanced.md#tool-search) খোঁজায় যুক্ত করে।

instructions, ফাংশন টুল, toolset আর বর্ণনার বাইরের যেকোনো কিছুর জন্য — model settings, hook, নেটিভ টুল, wrapper toolset, বা নিজস্ব প্রতি-রান লজিক — সরাসরি [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass করুন। subclass করার সময়, ক্যাটালগ entry রান অনুযায়ী বদলানো দরকার হলে [`get_description`][pydantic_ai.capabilities.AbstractCapability.get_description] override করুন।

/// note | durable execution-এর জন্য `id` সেট করা

একটি capability-র দেওয়া একটি toolset — `Capability(tools=[...])` দিয়ে বা লোকালে চলা একটি [`MCP`](mcp.md) সার্ভার — এর `id` capability-র [`id`][pydantic_ai.capabilities.AbstractCapability.id] থেকে উত্তরাধিকারসূত্রে পায়। [Durable execution](../durable_execution/overview.md) প্রতিটি পাতা-স্তরের toolset এর `id` দিয়ে চেনে, তাই Temporal, DBOS বা Prefect-এর সাথে একটি capability জুড়লে `Capability(id='...', tools=[...])` বা `MCP(id='...', url='...')` দিন। Temporal-এর প্রতিটি পাতা-স্তরের toolset-এর জন্য আর DBOS-এর প্রতিটি MCP সার্ভারের জন্য একটি `id` লাগে — একটি ছাড়া দুটোই তৈরির সময় exception তোলে। (`id` না দিলে `MCP` সার্ভার URL-এর hostname থেকেও একটি তৈরি করে।) একই host-এ দুটি সার্ভার (`https://a.com/api` আর `https://a.com/v2/api` দুটোই `a.com` তৈরি করে) এজেন্ট তৈরির সময় প্রত্যাখ্যাত হয়, তাই প্রতিটিকে একটি স্পষ্ট `id` দিন।

///

## instructions-এর বাইরে: টুল, সেটিং, hook, নেটিভ টুল { #beyond-instructions }

ওপরের [`Capability`][pydantic_ai.capabilities.Capability] উদাহরণ instructions আর একটি ফাংশন টুল defer করেছে, কিন্তু একই flag পুরো বান্ডেল নিয়ন্ত্রণ করে — মডেল কী জানে, কী করতে পারে আর কীভাবে করে (দেখুন [What you can defer](#what-you-can-defer))। নিচের snippet-গুলো বাকি অংশ পালাক্রমে দেখায়: model settings, hook আর নেটিভ টুল।

### Deferred model settings { #deferred-model-settings }

[`get_model_settings`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] capability গঠনের সময় সংগৃহীত হয়, কিন্তু এর সেটিং শুধু deferred capability লোড হওয়ার পরে প্রয়োগ হয়। এর মানে বাড়ানো reasoning effort-এর মতো প্রতি-step সেটিং শুধু সেই workflow-এ প্রয়োগ হয় যা মডেল বেছে নেয়:

⟦CODE5⟧

### Deferred workflow-সহ lifecycle hook { #lifecycle-hooks-with-deferred-workflows }

Hook-ও deferred capability-তে থাকতে পারে। মালিক capability মডেল লোড না করা পর্যন্ত এগুলো চলে না:

⟦CODE6⟧

/// note | অন্য capability যাচাই করা

`ctx.capability_active` সেই capability-র পরিসরে, যার hook বর্তমানে চলছে। একটি সবসময়-চালু hook capability-র জন্য, এটি সবসময় সত্য। আরেকটি deferred capability লোড হয়েছে কিনা যাচাই করতে, `ctx.loaded_capability_ids`-এ এর ID খুঁজুন, যেমন `if 'account-security' in ctx.loaded_capability_ids:`। একটি workflow লোডের আগেই একটি hook-কে একটি নিয়ম প্রয়োগ করতে হলে, ওই hook একটি সবসময়-চালু capability-তে রাখুন আর `ctx.loaded_capability_ids` পরীক্ষা করুন।

///

### Deferred নেটিভ টুল { #deferred-native-tools }

যেকোনো [provider-অনুযায়ী capability](overview.md#provider-adaptive-tools) (`WebSearch`, `WebFetch`, `MCP`, …) একইভাবে defer করা যায়। নেটিভ টুল সংজ্ঞা শুধু `load_capability` টুল capability লোড করার পরে রিকোয়েস্টে ঢোকে — বিনিময়ের জন্য দেখুন [Cache implications](#cache-implications):

⟦CODE7⟧

## সব একসাথে: একটি বহু-workflow support এজেন্ট { #putting-it-together-a-multi-workflow-support-agent }

একটি বাস্তবসম্মত on-demand capability খুব কমই শুধু একটি অংশ নিয়ে গঠিত। নিচের উদাহরণ দুটি deferred workflow-সহ একটি customer-support এজেন্ট সংজ্ঞায়িত করে, যা বান্ডেলের ভিন্ন অংশ চালায়:

- `orders` — instructions আর একটি ফাংশন টুল, [`Capability`][pydantic_ai.capabilities.Capability] দিয়ে inline সংজ্ঞায়িত।
- `account-security` — instructions, একটি ফাংশন টুল, বাড়ানো reasoning effort, *আর* একটি অনুমোদন hook, সব একটি [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass হিসেবে একত্র।

ওই workflow-গুলোর জন্য, turn 1 শুধু দুই-লাইনের ক্যাটালগ প্রকাশ করে। মূল instructions, সবসময়-চালু টুল, framework-পরিচালিত `load_capability` টুল আর যেকোনো provider/tool-search ব্যবস্থা স্বাভাবিকভাবে দেখা দেয়। `account-security` লোড করলে runbook, ধ্বংসাত্মক টুল, বেশি reasoning effort *আর* অনুমোদন-দরজা একসাথে সক্রিয় হয় — বান্ডেল-স্তরের প্রকাশ বলতে আমরা এটাই বোঝাই।

⟦CODE8⟧

একটি "আমার অর্ডার কোথায়?" রিকোয়েস্ট শুধু `orders` লোড করে। একটি "কেউ আমার অ্যাকাউন্টে লগইন করছে" রিকোয়েস্ট শুধু `account-security` লোড করে — আর সেই মুহূর্ত থেকে, রানের প্রতিটি টুল কল অনুমোদন hook দিয়ে যায় *আর* বাড়ানো reasoning effort-এর সুবিধা পায়, যে রিকোয়েস্ট কখনো workflow-টি ছোঁয়নি সেগুলোতে মডেলের কাছে কোনোটি দৃশ্যমান না হয়েই।

## আগে-পড়ো-তারপর-কাজ প্রয়োগ { #enforcing-read-before-act }

চান যে মডেল একটি ধ্বংসাত্মক কাজের আগে সত্যিই *runbook পড়ুক*? runbook-কে একটি deferred capability বানান, তারপর একটি এক-মেথডের hook-এ `ctx.loaded_capability_ids` যাচাই করুন:

⟦CODE9⟧

মডেল turn 1 থেকেই `issue_refund` দেখে। `refund-policy` খোলার আগে এটি ডাকার চেষ্টা করলে, hook কলটি ঠিক কোন `load_capability` টুল কল করতে হবে তা নির্দেশ করা একটি বার্তাসহ ফিরিয়ে দেয়। মডেল নীতি লোড করে, নীতির লেখা এর সাম্প্রতিক context-এ পড়ে, আর refund নিয়মের *ভেতরে* চলে — আর শুধু তখনই। একই ধরন যেকোনো টুল-আর-runbook জোড়ায় কাজ করে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি ব্যাংকের নতুন কর্মী টাকা ফেরতের বোতাম দেখতে পান, কিন্তু চাপলে সিস্টেম বলে "আগে refund নীতিমালা খুলে পড়ুন"। তিনি নীতিমালা পড়েন, তারপর বোতাম কাজ করে। এখানে `ctx.loaded_capability_ids` হলো সেই "নীতিমালা পড়া হয়েছে কিনা" রেকর্ড।

///

যেহেতু লোড হওয়া সেট শুধু [`RunContext`][pydantic_ai.tools.RunContext]-এর রানের সময়ের ডেটা, ধরনটি সাধারণীকরণ করা যায়: গতিশীল instructions একটি ঝুঁকিপূর্ণ workflow জোড়া খোলা থাকলে সতর্ক করতে পারে, audit hook লোড হওয়া সেট দিয়ে trace-এ tag দিতে পারে, escalation hook `payments` আর `account-security` দুটোই সক্রিয় থাকলে একটি বাড়তি নিশ্চিতকরণ চাইতে পারে।

## Markdown ফাইল থেকে skill লোড { #loading-skills-from-markdown-files }

আপনি যদি আগে থেকেই আপনার skill YAML frontmatter-সহ Markdown ফাইল হিসেবে রাখেন — [Anthropic Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)-এর ব্যবহৃত ফরম্যাট — আপনি কয়েক লাইনের জোড়া-কোড দিয়ে প্রতিটি একটি [`Capability`][pydantic_ai.capabilities.Capability]-তে মোড়াতে পারেন।

একটি skill ফাইল `skills/refunds.md` দেওয়া থাকলে:

⟦CODE10⟧

এটি একটি on-demand capability হিসেবে একটি এজেন্টে লোড করুন:

⟦CODE11⟧

প্রতিটি ফাইল মডেলের ক্যাটালগে এর `id` আর `description` হিসেবে দেখা দেয়; body শুধু মডেল `load_capability` টুল ডাকার পরেই পাঠানো হয়। instructions-এর বাইরে যেতে — একটি নির্দিষ্ট skill-এর জন্য ফাংশন টুল, model settings বা hook যোগ করতে — ওপরের উদাহরণগুলোর মতো [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass করুন।

/// note | যার সাথে মিলে যায়

On-demand capability framework-এর বাকি অংশ থেকে স্বাধীন — এগুলো আপনি হয়তো ইতিমধ্যে ব্যবহার করছেন এমন সুবিধার ওপর স্তর হিসেবে বসে:

- **[Tool search](../tools-advanced.md#tool-search)** — capability-স্তরের `defer_loading=True` পুরো বান্ডেল একটি একক হিসেবে নিয়ন্ত্রণ করে; প্রতি-*টুল* খোঁজার জন্য, একটি non-deferred capability-তে বা `@agent.tool`-এ টুল-স্তরের `defer_loading=True` সেট করুন।
- **[MCP servers](../mcp/client.md)** — [`MCP`][pydantic_ai.capabilities.MCP] capability `defer_loading=True` নেয়, মডেল বেছে না নেওয়া পর্যন্ত সার্ভারের পুরো টুল তালিকা লুকিয়ে রাখে।
- **[Native tools](../native-tools.md)** — [`WebSearch`][pydantic_ai.capabilities.WebSearch], [`WebFetch`][pydantic_ai.capabilities.WebFetch], [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] আর [`MCP`][pydantic_ai.capabilities.MCP] সবগুলো ফাংশন টুলের মতোই defer হয় (দেখুন [Cache implications](#cache-implications))।
- **[Hooks](../hooks.md)** — একটি deferred capability-তে (বা একটি deferred [`Hooks`][pydantic_ai.capabilities.Hooks] capability দিয়ে) ঘোষিত lifecycle hook মডেল বেছে না নেওয়া পর্যন্ত সুপ্ত থাকে।
- **[Message history](../message-history.md)** — লোড হওয়া state ইতিহাসের মধ্য দিয়ে যাওয়া-আসা করে, তাই সংরক্ষিত কথোপকথন একই state-এ আবার চলে (দেখুন [Resumable across runs](#resumable-across-runs))।

যেকোনো উৎস থেকে একটি ফাংশন-টুল প্রকাশ একটি [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart] হিসেবে সংরক্ষিত হয়, তাই একটি আবার-চালু বা durable রান উপলব্ধ টুল সেট আবার তৈরি করতে পারে, অ্যাপ্লিকেশন-চালিত নিয়ন্ত্রণকে মডেলের করা একটি tool search হিসেবে লেখা না হয়েই।

///

/// check | সংক্ষেপে মনে রাখুন

* `defer_loading=True` + স্থিতিশীল `id` → capability একটি এক-লাইনের ক্যাটালগ entry; মডেল `load_capability` দিয়ে খোলে।
* লোডে পুরো বান্ডেল (instructions, টুল, settings, hook, নেটিভ টুল) একসাথে চালু হয়, রানের বাকি সময় থাকে।
* অনেক আলাদা workflow থাকলে ব্যবহার করুন; প্রায় প্রতি turn-এ লাগলে নয়।
* লোড-state ইতিহাসে থাকে, তাই সংরক্ষিত কথোপকথন একই state-এ আবার চলে — `id` কখনো বদলাবেন না।
* deferred instructions client-এর message history-তে যায়; গোপন হলে সবসময়-চালু রাখুন।
* `ctx.loaded_capability_ids` দিয়ে "আগে নীতি পড়ো" নিয়ম প্রয়োগ করুন।

///
