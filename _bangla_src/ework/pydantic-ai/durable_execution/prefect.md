
# Prefect দিয়ে Durable Execution { #durable-execution-with-prefect }

/// note | এই পেজে যা শিখবেন

* Prefect-এর মূল ধারণা: **flow** (শীর্ষ স্তর) আর **task** (আলাদাভাবে retry, cache আর পর্যবেক্ষণযোগ্য কাজের একক)।
* `PrefectDurability` দিয়ে এজেন্টকে durable করা, আর কেন `agent.run()`-কে নিজের `@flow`-এ রাখতে হয়।
* টুল কীভাবে নিজে থেকে task হয়, আর প্রতি-টুল task কনফিগারেশন।
* caching, retry, observability আর `serve()` দিয়ে deploy ও schedule।

///

[Prefect](https://www.prefect.io/) হলো Python-এ টেকসই data pipeline তৈরির একটি workflow orchestration framework, যা Pydantic AI-এর সাথে নেটিভভাবে যুক্ত।

## Durable Execution { #durable-execution }

Prefect 3.0 আপনার Python workflow-এ [transactional semantics](https://www.prefect.io/blog/transactional-ml-pipelines-with-prefect-3-0) আনে: প্রতিটি task একটি transaction-এর ভেতরে চলে, যা ঠিক করে কখন আর কোথায় এর ফলের রেকর্ড সংরক্ষিত হবে।

* **Flow** হলো আপনার workflow-এর শীর্ষ-স্তরের প্রবেশপথ। এতে task আর অন্য flow থাকতে পারে।
* **Task** হলো কাজের আলাদা একক, যা স্বাধীনভাবে retry, cache আর মনিটর করা যায়।

একটি task একই context-এ আবার চললে, যেমন একই flow run-এর একটি retry, এটি আবার না চলে এর লেখা ফল লোড করে। এটি বাইরের side effect-কে ঠিক-একবার করে না; দেখুন [Caching and Idempotency](#caching-and-idempotency)।

নিচের diagram Prefect-সহ একটি agentic অ্যাপ্লিকেশনের সামগ্রিক architecture দেখায়।
Prefect ডিফল্টভাবে client-পক্ষের task orchestration ব্যবহার করে, scheduling আর monitoring-এর মতো উন্নত সুবিধার জন্য ঐচ্ছিক সার্ভার সংযোগসহ।

⟦CODE1⟧

আরও তথ্যের জন্য দেখুন [Prefect ডকুমেন্টেশন](https://docs.prefect.io/)।

/// tip | উদাহরণ দিয়ে বুঝি

Prefect-এর caching একটি "রান্নার খাতা"-র মতো: প্রতিটি task-এর ফল তার input-এর (মেসেজ, আর্গুমেন্ট, deps) "চাবি"-তে লেখা থাকে। flow আবার চললে, একই চাবির task খাতা থেকে ফল নিয়ে নেয় — মডেলকে আবার জিজ্ঞেস করে না। কিন্তু যে task ফল লেখার আগেই থেমে গেছে, সেটা আবার চলবে — তাই টাকা পাঠানো, ইমেল পাঠানোর মতো টুল idempotent রাখুন।

///

## Durable এজেন্ট { #durable-agent }

যেকোনো [`Agent`][pydantic_ai.agent.Agent]-এ durable execution যোগ করুন [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability] [capability](../capabilities/overview.md) যুক্ত করে। এজেন্টটি একটি Prefect flow-এর ভেতরে চললে, capability-টি [মডেল রিকোয়েস্ট](../models/overview.md), [টুল কল](../tools.md) আর [MCP যোগাযোগ](../mcp/client.md) Prefect task দিয়ে পাঠায়। একটি রান durable করতে, একটি `@flow`-এর ভেতরে `agent.run()` ডাকুন।

এজেন্টটি সব জায়গায় একটি সাধারণ `Agent` থাকে — একটি Prefect flow-এর বাইরে capability স্বচ্ছ, আর মূল এজেন্ট, মডেল আর MCP সার্ভার এখনও স্বাভাবিকভাবে ব্যবহার করা যায়।

task আর flow কোডের ভেতরে event সামলানোর জন্য দেখুন [Streaming](#streaming)।

একটি এজেন্টে durable execution যুক্ত করার একটি সহজ কিন্তু সম্পূর্ণ উদাহরণ এখানে। এর জন্য শুধু Prefect-সহ Pydantic AI ইনস্টল করতে হয়:

/// tab | pip

```bash
pip install pydantic-ai[prefect]
```

///

/// tab | uv

```bash
uv add pydantic-ai[prefect]
```

///


অথবা slim প্যাকেজ ব্যবহার করলে, `prefect` optional group দিয়ে ইনস্টল করতে পারেন:

/// tab | pip

```bash
pip install pydantic-ai-slim[prefect]
```

///

/// tab | uv

```bash
uv add pydantic-ai-slim[prefect]
```

///


⟦CODE2⟧

1. এজেন্টের `name` এর flow আর task-গুলোকে অনন্যভাবে চিহ্নিত করতে ব্যবহৃত হয়।
2. `capabilities=[...]` দিয়ে durability যুক্ত করুন। এজেন্ট একটি flow-এর ভেতরে চললে capability-টি মডেল রিকোয়েস্ট, টুল কল আর MCP যোগাযোগ Prefect task দিয়ে পাঠায়।
3. রানটি durable করতে `agent.run()`-কে আপনার নিজের `@flow`-এ মোড়ান।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

যেহেতু একই এজেন্ট একটি Prefect flow-এর ভেতরে আর বাইরে কাজ করে, [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability] অন্য সব [capability](../capabilities/overview.md)-র সাথে মিলে যায়, প্রতিটির জন্য একটি Prefect-নির্দিষ্ট wrapper রূপ ছাড়াই।

Python অ্যাপ্লিকেশনে Prefect কীভাবে ব্যবহার করবেন তার আরও তথ্যের জন্য, দেখুন তাদের [Python ডকুমেন্টেশন](https://docs.prefect.io/v3/how-to-guides/workflows/write-and-run)।

### Wrapper-agent পথ (অবচিত) { #wrapper-agent-path-deprecated }

/// warning | অবচিত (Deprecated)

[`PrefectAgent`][pydantic_ai.durable_exec.prefect.PrefectAgent] হলো Prefect ইন্টিগ্রেশনের মূল wrapper-agent পথ, যা v3-এ সরানো হবে। নতুন কোডে ওপরে দেখানো [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability] capability ব্যবহার করা উচিত।

**migrate করার সময়, রানটি আপনাকে নিজে একটি flow-এ মোড়াতে হবে।** `PrefectAgent` `run` / `run_sync`-কে নিজে থেকে একটি Prefect flow হিসেবে মোড়াত; `PrefectDurability` ইচ্ছে করে তা করে না — একটি রান শুধু তখনই durable যখন আপনার নিজের `@flow`-এর ভেতরে `agent.run()` ডাকা হয়। constructor আর্গুমেন্ট নিয়ে এসে কিন্তু সরাসরি `agent.run()` ডাকলে এমন একটি রান তৈরি হয় যা কাজ করে কিন্তু **durable নয়**।

**চলমান flow run migration জুড়ে cache থেকে আবার চলবে না।** `PrefectAgent`-এর অধীনে লেখা task ফল task-এর source code-এর ওপর key করা, তাই migration deploy করার পর retry করা একটি flow run লেখা ফল replay না করে এর মডেল রিকোয়েস্ট আর টুল কল লাইভ আবার চালায়। পুনরায় চালানো আপনার কাছে জরুরি হলে বদলানোর আগে চলমান flow run শেষ হতে দিন।

///

যেকোনো এজেন্টকে একটি [`PrefectAgent`][pydantic_ai.durable_exec.prefect.PrefectAgent]-এ মোড়ানো যায়, এমন একটি durable এজেন্ট রূপ পেতে যা মডেল রিকোয়েস্ট, টুল কল আর MCP যোগাযোগ Prefect task দিয়ে পাঠায়:

⟦CODE3⟧

capability-তে migrate করা মানে `PrefectDurability` যুক্ত করা আর সেই flow decorator যোগ করা যা `PrefectAgent` আপনার জন্য প্রয়োগ করত:

⟦CODE4⟧

## Prefect ইন্টিগ্রেশনের বিবেচনা { #prefect-integration-considerations }

Pydantic AI এজেন্টের সাথে Prefect ব্যবহারের সময়, workflow ঠিকভাবে আচরণ করছে তা নিশ্চিত করতে কয়েকটি জরুরি বিবেচনা আছে।

### এজেন্টের প্রয়োজনীয়তা { #agent-requirements }

প্রতিটি এজেন্ট instance-এর একটি অনন্য `name` থাকতে হবে, যাতে Prefect এর flow আর task ঠিকভাবে চিহ্নিত আর ট্র্যাক করতে পারে।

যে toolset নিজের টুল তালিকা আর কল বাস্তবায়ন করে (অর্থাৎ [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset], [`MCPToolset`][pydantic_ai.mcp.MCPToolset] আর [`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset]), সেগুলোর একটি অনন্য [`id`][pydantic_ai.toolsets.AbstractToolset.id] সেট থাকতে হবে, যা flow-এর ভেতরে তাদের task চিহ্নিত করতে ব্যবহৃত হয়। `id` ছাড়া একটি URL `MCPToolset` যে hostname-কে `id` হিসেবে নেয় তা গণ্য হয় না।

### রানের সময় capability { #capabilities-at-runtime }

Temporal আর DBOS-এর বিপরীতে, Prefect এর durable একক আগে থেকে নিবন্ধন না করে প্রতি কলে একটি task তৈরি করে, তাই একটি flow-এর ভেতরে `agent.run(capabilities=[...])`-এ দেওয়া [capability](../capabilities/overview.md) গ্রহণযোগ্য। একটি চালানো toolset দেওয়া একটি capability তবুও প্রত্যাখ্যাত হয়, সেই একই পাহারায় যা `run(toolsets=...)` প্রত্যাখ্যান করে: toolset-টি এজেন্টের toolset মোড়ানোর পরে আসে। এগুলো এজেন্ট তৈরির সময় যুক্ত করুন।

### Durable capability operation { #durable-capability-operations }

Capability task-এর cache key-তে এজেন্টের নাম থাকে, তাই এক flow-এ দুটি এজেন্ট কখনো একটি cache করা ফল ভাগ করে না।

নিজস্ব [`@durable_operation`][pydantic_ai.capabilities.durable_operation] কল তাদের task cache key-তে রানের [`run_id`][pydantic_ai.tools.RunContext.run_id] আর একটি প্রতি-operation কল ক্রম ব্যবহার করে। আলাদা, স্থিতিশীল স্পষ্ট `run_id=` মান প্রতিটি রানের ফল সেই রানের সাথে যুক্ত রাখে, এমনকি একটি flow retry-তে রানগুলো ভিন্ন ক্রমে এলেও। একটি রানের ভেতরে একই কলের পুনরাবৃত্তি আলাদা লেখা ফল রাখে। নিজে থেকে তৈরি run ID তবুও আসার ক্রমের ওপর নির্ভর করে, তাই যে শাখাগুলো ক্রম বদলাতে পারে সেগুলোর জন্য স্পষ্ট ID দিন।

/// warning | নিজস্ব capability task cache key আপগ্রেড করা

এই পরিবর্তনের আগের version-এর সংরক্ষিত নিজস্ব capability task ফল ভিন্ন cache key ব্যবহার করে। আপগ্রেড জুড়ে একটি চলমান flow retry করলে এই operation-গুলো আবার চলে, যা তাদের বাইরের প্রভাব পুনরাবৃত্তি করতে পারে। আপগ্রেডের আগে নিজস্ব durable capability operation ব্যবহার করা চলমান flow শেষ হতে দিন। হাতে cache মোছার দরকার নেই। এই হালনাগাদে মডেল, টুল, workspace আর event stream handler-এর cache key অপরিবর্তিত।

///

### Workspace { #workspaces }

এজেন্ট তৈরির সময় [workspace](../workspace.md) capability যুক্ত করুন, যেমন `LocalWorkspace`, আর যেকোনো রানের মতো `ctx.workspace` ব্যবহার করুন। flow কোডে করা প্রতিটি workspace কল (capability hook, output function, `result.workspace`) একটি task হিসেবে চলে; একটি task-এর ভেতরে, যেমন একটি টুলে, কল সরাসরি provider-এ যায়।

একটি এজেন্টে workspace যোগ করা এর flow-এর চালানো task বদলায়, তাই পরিবর্তন deploy করার আগে চলমান flow শেষ হতে দিন।

Workspace task cache key-তে রানের [`run_id`][pydantic_ai.tools.RunContext.run_id] আর একটি প্রতি-রান কল ক্রম থাকে। আলাদা, স্থিতিশীল স্পষ্ট `run_id=` মান দিয়ে, একসাথে চলা রানগুলো flow retry-তে তাদের আসার ক্রম বদলালেও নিজের environment রাখে। নিজে থেকে তৈরি run ID তবুও আসার ক্রমের ওপর নির্ভর করে, তাই ক্রম বদলাতে পারে এমন একসাথে চলা শাখার জন্য স্পষ্ট ID দিন।

/// warning | Workspace task cache key আপগ্রেড করা

এই পরিবর্তনের আগের version-এর সংরক্ষিত workspace task ফল ভিন্ন cache key ব্যবহার করে।
আপগ্রেড জুড়ে একটি চলমান flow retry করলে workspace কল আবার চলে, যা মূলটিতে আবার যুক্ত না হয়ে একটি নতুন environment তৈরি করতে পারে। আপগ্রেডের আগে চলমান workspace flow শেষ হতে দিন। হাতে cache মোছার দরকার নেই।

///

Event stream handler task-এর cache key-তে এজেন্টের নাম থাকে, তাই এক flow-এ দুটি এজেন্ট কখনো একটি cache করা ফল ভাগ করে না। এটি চালু করা আপগ্রেড জুড়ে retry করা একটি flow ওই task-গুলো cache থেকে না পড়ে একবার আবার চালায়।

### রানের সময় মডেল বাছাই { #model-selection-at-runtime }

[`Agent.run(model=...)`][pydantic_ai.agent.Agent.run] মডেল string (যেমন `'openai:gpt-6.1-sol'`) আর মডেল instance দুটোই সমর্থন করে। একটি মডেল instance task সীমা পেরিয়ে serialize করা যায় না, আর এর `model_id` string থেকে একটি আবার তৈরি করলে একটি *ভিন্ন* মডেল তৈরি হবে — worker-এর environment যে provider বোঝায় তাতে একই মডেলের নাম, তাই রিকোয়েস্ট অন্য credential নিয়ে অন্য endpoint-এ যাবে। তাই আগে থেকে নিবন্ধিত নয় এমন একটি instance একটি `UserError` দিয়ে প্রত্যাখ্যাত হয়। একটি নির্দিষ্ট instance ব্যবহারের দুটি উপায় আছে: [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability]-তে একটি `models` dict দিয়ে এটি আগে নিবন্ধন করে key দিয়ে রেফারেন্স দিন (বা নিবন্ধিত instance দিন), বা একটি মডেল-নামের string দিন আর একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability দিয়ে task-এর ভেতরে instance তৈরি করুন — সঠিক পছন্দ যখন মডেল রানের `deps`-এর ওপর নির্ভর করে, যেমন প্রতি-ব্যবহারকারী credential। মডেল-নামের string নিজে কখনো নিবন্ধন করতে হয় না। তৈরির সময় সেট করা এজেন্টের নিজের মডেল সবসময় ডিফল্ট হিসেবে উপলব্ধ।

একটি মডেল string কীভাবে তৈরি হবে তা কাস্টমাইজ করতে — একটি নিজস্ব provider, বা রানের `deps`-এ বহন করা প্রতি-ব্যবহারকারী credential — `PrefectDurability`-র আগে একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability যোগ করুন: এটি প্রতিটি string-এ প্রথম সুযোগ পায়, আর resolver রানের আসল `deps` দিয়ে task-এর ভেতরে আবার চলে, তাই এটিকে একটি নির্দিষ্ট `(model_id, deps)`-এর জন্য deterministic হতে হবে আর বাইরের I/O করা চলবে না।

### টুল মোড়ানো { #tool-wrapping }

এজেন্টের টুল নিজে থেকে Prefect task হিসেবে মোড়ানো হয়, যার মানে এগুলো পায়:

* **Retry লজিক**: ব্যর্থ টুল কল নিজে থেকে retry করা যায়
* **Caching**: টুলের ফল তাদের input-এর ভিত্তিতে cache হয়
* **Observability**: টুল চালানো Prefect UI-তে ট্র্যাক হয়

একটি [`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset]-এর জন্য, একটি [`DynamicCapability`][pydantic_ai.capabilities.DynamicCapability]-এর দেওয়াটিসহ, টুল খোঁজা আর প্রতিটি টুল কল Prefect task হিসেবে চলে, আর flow retry লেখা খোঁজা আর টুল ফল replay করে। factory `per_run_step=False` দিয়ে তৈরি হলে, রান toolset একবার মীমাংসা করে আর প্রতিটি task এটি পুনর্ব্যবহার করে, প্রথম যে task-এর এটি দরকার তখন এতে প্রবেশ করে আর রানের বাকি সময় প্রবেশ করা অবস্থায় রাখে। একটি toolset তৈরি করা আর এটি সংযুক্ত করা এক নয় — একটি `MCPToolset` প্রবেশ না করা পর্যন্ত কিছুই খোলে না — তাই সংযোগ একটি task-এর ভেতরে ঘটে, যেখানে এটি অন্য যেকোনো task ব্যর্থতার মতো retry হয়। factory নিজে flow কোডে চলে আর যখনই সেটি replay হয় আবার চলে, তাই নিচের capability factory-র মতো রানের `deps` দেওয়া থাকলে এটিকে deterministic হতে হবে: factory-তে toolset তৈরি করুন আর এর I/O task-এর জন্য রাখুন। এটি সেই lifecycle যা একটি non-durable রান toolset-কে দেয়, তাই একটি toolset-এর নিজস্ব caching — যেমন factory-র ফেরত দেওয়া একটি `MCPToolset`-এ [`cache_tools`][pydantic_ai.mcp.MCPToolset.cache_tools] — task-এর মাঝে ফেলে না দিয়ে flow-এর বাইরের মতোই কাজ করে। একটি `per_run_step=True` factory প্রতিটি task-এর ভেতরে আবার মীমাংসা হয়, যেমন এটি চায়।

একটি [`MCPToolset`][pydantic_ai.mcp.MCPToolset]-এর জন্য, টুল খোঁজা আর প্রতিটি টুল কল Prefect task হিসেবে চলে, আর সার্ভার flow কোডে নয়, বরং যে প্রথম task-এর এটি দরকার তার ভেতরে সংযুক্ত হয়, তাই একটি ব্যর্থ সংযোগ সেই task-এর retry policy-তে কভার হয়। flow তখন রান শেষ না হওয়া পর্যন্ত session ধরে রাখে, তাই সার্ভার প্রতি রানে একবার সংযুক্ত হয় আর এর নিজস্ব
[`cache_tools`][pydantic_ai.mcp.MCPToolset.cache_tools] পরের খোঁজার task-এর উত্তর দেয়। এক process-এ একসাথে চলা রানগুলো একটি সার্ভারের session ভাগ করে, যেমন flow-এর বাইরে করে, আর শেষটি শেষ হলে এটি বন্ধ হয়।

[`args_validator`](../tools-advanced.md#args-validator)-যুক্ত একটি টুল একটি `Validate Tool Args: {name}` task পায়, তাই validator-এর I/O টুল কলের মতোই চেকপয়েন্ট হয়। একটি ছাড়া টুল কোনো বাড়তি task পায় না, আর `metadata={'prefect': False}`-যুক্ত একটি টুল এর কলের পাশে flow কোডে যাচাই হয়। যাচাই চলে [অনুমোদন আর deferral](../deferred-tools.md)-এর আগে, তাই প্রত্যাখ্যাত আর্গুমেন্ট কখনো একজন অনুমোদনকারীর কাছে পৌঁছায় না। Validator task-এর ভেতর থেকে defer-ও করতে পারে; অনুমোদনসহ আবার চালালে `tool_call_approved` সেট করে যাচাই আবার চলে।

সব টুলের জন্য একটি ডিফল্ট [`TaskConfig`][pydantic_ai.durable_exec.prefect.TaskConfig] [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability] constructor-এ `tool_task_config` হিসেবে দেওয়া যায়। প্রতি-টুল config থাকে টুলের [`metadata`][pydantic_ai.toolsets.FunctionToolset.tool] ফিল্ডে — `PrefectDurability` একটি `'prefect'` key খোঁজে। আপনি metadata সরাসরি টুল সংজ্ঞায় সেট করতে পারেন, বা [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] capability দিয়ে একগুচ্ছ টুলে প্রয়োগ করতে পারেন। পুরো selector শব্দভাণ্ডারের জন্য দেখুন [capabilities ডকুমেন্টেশন][pydantic_ai.capabilities.SetToolMetadata]।

⟦CODE5⟧

1. Inline: টুল সংজ্ঞার পাশে task config ঘোষণা করুন। প্রতি-টুল config মূল `tool_task_config`-এর ওপরে মেলানো হয়।
2. ওই টুলের task মোড়ানো পুরোপুরি এড়াতে `'prefect': False` সেট করুন।
3. Selector-ভিত্তিক: [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] একগুচ্ছ টুলে একই metadata প্রয়োগ করে (`'all'`, একটি নামের লিস্ট, একটি dict, বা একটি callable)।
4. `tool_task_config` প্রতিটি টুলের ডিফল্ট config সেট করে।

বেরিয়ে আসার এই সুযোগ শুধু function আর dynamic টুলে প্রযোজ্য। MCP টুল I/O করে আর সবসময় তাদের Prefect task-এ চলে, তাই একটি MCP টুলে `metadata={'prefect': False}` একটি `UserError` তোলে।

### Streaming { #streaming }

[`Agent.run_stream()`][pydantic_ai.agent.Agent.run_stream], [`Agent.run_stream_events()`][pydantic_ai.agent.Agent.run_stream_events] আর [`Agent.iter()`][pydantic_ai.agent.Agent.iter] একটি Prefect flow-এর ভেতরে কাজ করে, কিন্তু তাদের event সাথে সাথে পৌঁছানোর বদলে জমা হয়। মডেল stream durable task-এর ভেতরে চলে, আর task শেষ হলে flow এর চূড়ান্ত response replay করে: প্রতিটি অংশ মডেলের stream করা delta হিসেবে নয়, বরং এর পুরো কনটেন্টসহ একটি [`PartStartEvent`][pydantic_ai.messages.PartStartEvent] হিসেবে আসে, তাই delta-গুলো task-এর ফলে লেখা হয় না।

I/O side effect-যুক্ত handler-এর জন্য, [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability]-তে `event_stream_handler=` দিন। মডেল event প্রতিটি model-request task-এর ভেতরে লাইভ পৌঁছায়, আর প্রতিটি টুল event নিজের event-handler task-এ পৌঁছায়। ওই প্রতি-event task `event_stream_handler_task_config=` দিয়ে কনফিগার করুন। যেকোনো Prefect task-এর মতো, একটি task retry করলে একটি handler একাধিকবার চলতে পারে, তাই এর side effect idempotent রাখুন।

বিকল্পভাবে, [`ProcessEventStream`][pydantic_ai.capabilities.ProcessEventStream] নিবন্ধন করুন। এর handler flow কোডে চলে আর deterministic হতে হবে, কারণ এটি flow replay-তে আবার চলে। টুল আর চূড়ান্ত-আউটপুট event লাইভ আসে, আর মডেল event প্রতিটি মডেল রিকোয়েস্ট শেষ হওয়ার পর চূড়ান্ত response থেকে replay হয়। উদাহরণের জন্য দেখুন [streaming ডক](../agent.md#streaming-all-events)।

একটি durability `event_stream_handler=` আর আলাদাভাবে নিবন্ধিত একটি `ProcessEventStream` দুটি ভিন্ন handler, আর প্রত্যেকে একবার চলে। durability handler durable task-এর ভেতরে লাইভ event পায়, আর `ProcessEventStream` flow কোডে জমানো replay দেখে।

`Agent.run(event_stream_handler=...)`-এ দেওয়া একটি প্রতি-রান handler-ও replay করা মডেল event-এর বিপরীতে flow-পক্ষে চলে।

একটি durable task-এর ভেতর থেকে [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] দিয়ে তৈরি event — একটি capability-র নিজের টুলের তৈরি একটি [capability event](../capabilities/overview.md#capability-events)-সহ — পৌঁছায় যখন task আসলে চলে, আর একটি flow retry বা cache hit-এ এর লেখা ফল replay হলে আবার তৈরি *হয় না*। একটি task-এর ভেতরে লেখা একটি log লাইনের মতো, একটি তৈরি event task চালানোর একটি side effect, এর লেখা ফলের অংশ নয়। একজন listener-কে প্রতিটি চেষ্টায় event দেখতে হলে flow-স্তরের কোড থেকে emit করুন, যেমন একটি [capability](../capabilities/overview.md) hook। [`@on_event`][pydantic_ai.capabilities.on_event] দিয়ে নিবন্ধিত capability listener একটি task-এর বদলে flow কোডে চলে, তাই এগুলো একটি flow retry-তে আবার চলে আর deterministic হতে হবে; I/O একটি durability `event_stream_handler=`-এ রাখুন, যা নিজের task-এ চলে। [`ctx.enqueue()`][pydantic_ai.tools.RunContext.enqueue]-এর বিপরীতে, যা একটি task-এর ভেতরে প্রত্যাখ্যাত হয় কারণ এটি বাদ পড়লে মডেল যা দেখে তা বদলে যেত, একটি হারানো event মানে শুধু একজন পর্যবেক্ষককে জানানো হয়নি। একটি durable এককের তৈরি event এর লেখা আউটপুটে বহন করা, যাতে একটি replay সেগুলো পুনরুৎপাদন করে, ট্র্যাক হচ্ছে [pydantic-ai#7971](https://github.com/pydantic/pydantic-ai/issues/7971)-এ।

যেহেতু মডেল stream task-এর ভেতরে গ্রহণ হয়, flow-পক্ষ থেকে এটি বাতিল করা (যেমন [`AgentStream.cancel()`][pydantic_ai.result.AgentStream.cancel] দিয়ে) durable সীমা জুড়ে পাওয়া যায় না।

[`CancellationToken`][pydantic_ai.CancellationToken] আর [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel] একই-process বাতিলের handle আর Prefect durable সীমা পেরোতে পারে না; এর বদলে Prefect flow বাতিল করুন।

[`Agent.run_stream_sync()`][pydantic_ai.agent.Agent.run_stream_sync] flow কোডের জন্য নয়: এর জন্য কোনো চলমান event loop না থাকা লাগে আর এটি `run_stream()` মোড়ায়। [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability]-এর অধীনে, ওপরের জমানো async streaming API বা একটি event stream handler-সহ [`Agent.run()`][pydantic_ai.agent.Agent.run] ব্যবহার করুন। একটি flow-এর বাইরে, `PrefectDurability`-সহ একটি এজেন্ট একটি সাধারণ এজেন্টের মতো আচরণ করে, তাই `run_stream_sync()` স্বাভাবিকভাবে কাজ করে। (Wrapper `PrefectAgent` flow-এর ভেতরে `run_stream` নিষেধ করে — সেখানে `run` + event stream handler ব্যবহার করুন।)

### রানের timeout { #run-timeouts }

একটি রানের [`timeout=`](../timeouts.md#bounding-a-whole-run) একটি flow-এর ভেতরে কাজ করে। রানের শুরুর সময় একটি cache করা `{name}__run_start_time` task দিয়ে লেখা হয়, তাই একটি flow retry রান যে সময়সীমা নিয়ে শুরু হয়েছিল তা রাখে, আর দেখতে পারে যে তা ইতিমধ্যে পেরিয়ে গেছে। সময়সীমা পেরোলে, রান flow কোডে [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut] তোলে, যেখানে আপনি এটি ধরতে পারেন। অবচিত `PrefectAgent` `timeout=` প্রত্যাখ্যান করে।

সময়সীমা এজেন্ট রান সীমিত করে, flow নয়। পুরো flow-ও সীমিত করতে, flow-এ Prefect-এর নিজস্ব `timeout_seconds` সেট করুন।

### স্থগিত turn আর background mode { #suspended-turns-and-background-mode }

যখন একটি provider একটি মডেল turn মাঝপথে থামায় (Anthropic `pause_turn`) বা একে একটি সার্ভার-পক্ষের job হিসেবে চালায় যা প্রস্তুত না হওয়া পর্যন্ত poll করা হয় ([OpenAI background mode](../models/openai.md#background-mode)), প্রতিটি অংশ একটি আলাদা model request task-এ চলে। স্থগিত [`ModelResponse`][pydantic_ai.messages.ModelResponse] আর background job ID অংশগুলোর মাঝে চেকপয়েন্ট হয়, আর চূড়ান্ত response মেলানো হয় আর usage একবার লেখা হয়। একটি স্থগিত response-এ শেষ হওয়া একটি [`message_history`](../message-history.md) প্রথম task-এ দেওয়া হয়। [Task Configuration](#task-configuration)-এ `timeout_seconds` একটি provider round trip-এর জন্য ঠিক করুন। একটি error একটি স্থগিত job পরিত্যাগ করলে, এর provider teardown একটি নির্দিষ্ট cancellation task-এ চলে। Prefect-এর কোনো টেকসই sleep নেই, তাই poll-এর মাঝের অপেক্ষা flow কোডে একটি সাধারণ sleep, যা একটি retry করা flow run আবার ঘুমায়।

### রানের সময় toolset { #toolsets-at-runtime }

durable মোড়ানো লাগে এমন প্রতিটি চালানো toolset এজেন্ট constructor-এ দিন, যাতে flow চলার আগে এর task নিবন্ধিত হয়। এতে [`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset] অন্তর্ভুক্ত: একে একটি স্পষ্ট `id` দিন আর `Agent(toolsets=[...])`-এ দিন। [`@agent.toolset`][pydantic_ai.agent.Agent.toolset] decorator engine-এর durable একক তৈরির পরে নিবন্ধন করে, তাই [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability]-এর অধীনে একটি flow-এর ভেতরে এটি ব্যবহার করলে একটি `UserError` ওঠে। অবচিত `PrefectAgent` এই যাচাই চালায় না: একটি flow-এর ভেতরে এটি মোড়ানোর সময় স্থির হওয়া task-মোড়ানো toolset তালিকা চালায়, তাই এত দেরিতে নিবন্ধিত একটি toolset নিঃশব্দে রান থেকে বাদ পড়ে।

`agent.run(toolsets=...)` দিয়ে প্রতি রানে বাড়তি toolset দেওয়া যায়, কিন্তু শুধু সেই toolset সমর্থিত যাদের durable মোড়ানো লাগে না: [`ExternalToolset`][pydantic_ai.toolsets.ExternalToolset]-এর মতো না-চালানো toolset, যার টুল এজেন্ট রানের বাইরে চলে, আর [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] যার সব টুল `metadata={'prefect': False}` দিয়ে task মোড়ানো থেকে বেরিয়ে আসে। রানের সময় দেওয়া অন্য চালানো toolset ([`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] আর [`MCPToolset`][pydantic_ai.mcp.MCPToolset]) আর dynamic toolset একটি `UserError` তোলে।

একটি flow-এর ভেতরে [`agent.override(toolsets=...)`][pydantic_ai.agent.AbstractAgent.override] দিয়ে বদলানো toolset-ও একই নিয়মে বাঁধা, কারণ এগুলোও এজেন্টের task নিবন্ধনের পরে আসে। রানের সময় যোগ করা একটি toolset এজেন্ট তৈরির সময়ের কোনোটির `id`-ও পুনর্ব্যবহার করতে পারে না, কারণ `id`-ই চিহ্নিত করে একটি টুল কল কোন নিবন্ধিত toolset-এর task-এ পাঠানো হবে।

## Task কনফিগারেশন { #task-configuration }

আপনি [`PrefectDurability`][pydantic_ai.durable_exec.prefect.PrefectDurability] constructor-এ [`TaskConfig`][pydantic_ai.durable_exec.prefect.TaskConfig] অবজেক্ট দিয়ে Prefect task-এর আচরণ, যেমন retry আর timeout, কাস্টমাইজ করতে পারেন:

- `mcp_task_config`: MCP সার্ভার যোগাযোগ task-এর কনফিগারেশন
- `model_task_config`: model request task-এর কনফিগারেশন
- `event_stream_handler_task_config`: event stream handler task-এর কনফিগারেশন
- `tool_task_config`: সব টুল কলের ডিফল্ট কনফিগারেশন (প্রতি-টুল override যায় টুলের `'prefect'` metadata-তে — ওপরে দেখুন [Tool Wrapping](#tool-wrapping))

উপলব্ধ `TaskConfig` অপশন:

- `retries`: task-এর সর্বোচ্চ retry সংখ্যা (ডিফল্ট: `0`)
- `retry_delay_seconds`: retry-র মাঝে সেকেন্ডে দেরি (একটি একক মান বা exponential backoff-এর জন্য একটি লিস্ট হতে পারে, ডিফল্ট: `1.0`)
- `timeout_seconds`: task শেষ হওয়ার সর্বোচ্চ সময়, সেকেন্ডে
- `cache_policy`: task-এর জন্য নিজস্ব Prefect cache policy
- `persist_result`: task-এর ফল সংরক্ষণ করা হবে কিনা
- `result_storage`: task-এর জন্য Prefect result storage (যেমন `'s3-bucket/my-storage'` বা একটি `WritableFileSystem` block)
- `log_prints`: task-এর print statement log করা হবে কিনা (ডিফল্ট: `False`)

উদাহরণ:

⟦CODE6⟧

1. task কনফিগারেশন শুধু একটি Prefect flow-এর ভেতরে প্রযোজ্য। এর বাইরে, এজেন্ট Prefect task ছাড়া সরাসরি এর মডেল রিকোয়েস্ট চালায়।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

### Retry-র বিবেচনা { #retry-considerations }

Pydantic AI আর provider API client-এর নিজস্ব retry লজিক আছে। Prefect ব্যবহারের সময়, আপনি হয়তো চাইবেন:

* Pydantic AI-তে [transport retries](../retries.md#transport-retries) বন্ধ করতে
* আপনার provider API client-এর retry লজিক বন্ধ করতে (যেমন একটি [custom OpenAI client](../models/openai.md#custom-openai-client)-এ `max_retries=0`)
* সামঞ্জস্যের জন্য Prefect-এর task-স্তরের retry কনফিগারেশনের ওপর নির্ভর করতে

এটি রিকোয়েস্টকে বিভিন্ন স্তরে একাধিকবার retry হওয়া থেকে আটকায়। স্তরগুলো *গুণিত* হয়: হিসাবের জন্য দেখুন [Retry multiplication](../retries.md#retry-multiplication)।

একটি flow-এ [`Agent.run()`][pydantic_ai.agent.Agent.run]-এ `run_id` বা `conversation_id` না দিলে, ডিফল্টগুলো র‍্যান্ডমভাবে তৈরি না হয়ে flow run থেকে তৈরি হয়, তাই একটি flow retry প্রতিটি এজেন্ট রানকে আগের চেষ্টার মতো একই ID দেয়।

## Caching আর Idempotency { #caching-and-idempotency }

Prefect 3.0 বিল্ট-ইন caching আর transactional semantics দেয়। যে task-এর ফল একই cache key-তে আগেই লেখা আছে তা আবার না চলে সেই ফল লোড করে, তাই একটি retry করা flow run সম্পন্ন মডেল রিকোয়েস্ট আর টুল কল replay করে। এর ফল লেখার আগে বাধা পাওয়া একটি task আবার চলে, এর বাইরের side effect ইতিমধ্যে ঘটে থাকলেও, তাই side effect-যুক্ত টুল idempotent হওয়া উচিত (যেমন বাইরের সার্ভিসে একটি idempotency key দিয়ে)।

/// warning | Dynamic-tool cache key বদলেছে

Dynamic-tool task key-তে এখন প্রস্তুত টুল সংজ্ঞা থাকে। dynamic টুলের বিদ্যমান cache করা ফল আপগ্রেডের পর একবার miss করে আবার হিসাব হবে। একটি prefix বা rename-এর অধীনে তালিকাভুক্ত একটি dynamic toolset-এর খোঁজা, আর্গুমেন্ট-যাচাই আর টুল-কল task-ও ওই prefix আর rename-এর ওপর key করে, আর একইভাবে আপগ্রেডের পর একবার miss করে। হাতে cache মোছার দরকার নেই; পরের কলগুলো নতুন মান-ভিত্তিক key পুনর্ব্যবহার করে।

///

* **Task input**: একটি মডেল রিকোয়েস্টের বার্তা, সেটিং আর প্যারামিটার; একটি টুল কলের নাম, আর্গুমেন্ট, সংজ্ঞা আর [`tool_call_id`][pydantic_ai.tools.RunContext.tool_call_id] (তাই একই আর্গুমেন্ট দিয়ে একই টুলে দুটি সমান্তরাল কল প্রত্যেকে চলে); একটি dynamic toolset যে prefix আর rename-এর অধীনে তালিকাভুক্ত (তাই দুটি prefix-এর অধীনে একটি dynamic toolset প্রতি prefix-এ একটি ফল রাখে); আর task-এর কাজ যে রান state-এর ওপর নির্ভর করতে পারে: dependency, [`metadata`][pydantic_ai.tools.RunContext.metadata], [`validation_context`][pydantic_ai.tools.RunContext.validation_context], prompt আর message history।

মডেল আর টুল task cache key ইচ্ছে করে [`run_id`][pydantic_ai.tools.RunContext.run_id] আর [`conversation_id`][pydantic_ai.tools.RunContext.conversation_id]-এর মতো প্রতি-রান identifier আর বার্তার timestamp বাদ দেয়, তাই একই input একই flow-এর এজেন্ট রান জুড়ে ফল পুনর্ব্যবহার করতে পারে। একটি [`timeout=`](#run-timeouts)-যুক্ত রান ব্যতিক্রম: এর টুল task রানের [`deadline`][pydantic_ai.tools.RunContext.deadline]-এর ওপর key করে, তাই যে টুল বাকি সময় অনুযায়ী তার কাজ ঠিক করে সে ভিন্ন বাজেটে হিসাব করা একটি ফল replay করে না। একটি flow retry সময়সীমা রাখে, তাই এর টুল ফল তবুও replay হয়। ডিফল্ট cache policy Prefect flow run ID অন্তর্ভুক্ত করে, তাই একটি আলাদা flow run-এর নিজস্ব cache পরিসর থাকে আর এর task নতুন করে চালায়।

**নোট**: ব্যবহারকারীর dependency, `metadata` আর `validation_context` cache key-তে অন্তর্ভুক্ত হতে, এগুলোকে serialize-যোগ্য হতে হবে (যেমন Pydantic model বা মৌলিক Python টাইপ)। serialize-অযোগ্য মান নিজে থেকে cache হিসাব থেকে বাদ পড়ে।

## Prefect আর Logfire দিয়ে Observability { #observability-with-prefect-and-logfire }

Prefect flow run, task execution আর ব্যর্থতা মনিটর করার একটি বিল্ট-ইন UI দেয়। আপনি পারেন:

* রিয়েল-টাইমে flow run-এর অবস্থা দেখতে
* পুরো stack trace দিয়ে ব্যর্থতা ডিবাগ করতে
* alert আর notification সেট করতে

Prefect UI-তে প্রবেশ করতে, আপনি হয়:

1. [Prefect Cloud](https://www.prefect.io/cloud) ব্যবহার করুন (পরিচালিত সার্ভিস)
2. `prefect server start` দিয়ে একটি লোকাল [Prefect server](https://docs.prefect.io/v3/how-to-guides/self-hosted/server-cli) চালান

বিস্তারিত observability-র জন্য আপনি [Pydantic Logfire](../logfire.md)-ও ব্যবহার করতে পারেন। Prefect আর Logfire দুটোই ব্যবহার করলে, আপনি পরিপূরক ভিউ পাবেন:

* **Prefect**: Workflow-স্তরের orchestration, task-এর অবস্থা আর retry ইতিহাস
* **Logfire**: এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল কলের সূক্ষ্ম tracing

Prefect-এর সাথে Logfire ব্যবহারের সময়, আপনি distributed tracing চালু করতে পারেন, যাতে আপনার এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল কলের সাথে আপনার Prefect রানের span-ও দেখা যায়।

Prefect মনিটরিং সম্পর্কে আরও তথ্যের জন্য, দেখুন [Prefect ডকুমেন্টেশন](https://docs.prefect.io/)।

## Deployment আর Scheduling { #deployments-and-scheduling }

একটি Prefect-durable এজেন্ট deploy আর schedule করতে, এটি একটি Prefect flow-এ মোড়ান আর flow-এর [`serve()`](https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments#create-a-deployment-with-serve) বা [`deploy()`](https://docs.prefect.io/v3/how-to-guides/deployments/deploy-via-python) মেথড ব্যবহার করুন:

⟦CODE7⟧

1. প্রতিটি flow run একটি বিচ্ছিন্ন process-এ চলে, আর সব input আর dependency serialize-যোগ্য হতে হবে। যেহেতু Agent instance serialize করা যায় না, এজেন্টকে module স্তরে না বানিয়ে flow-এর ভেতরে তৈরি করুন।

`serve()` মেথড scheduling অপশন নেয়:

- **`cron`**: Cron schedule string (যেমন প্রতিদিন সকাল 9টার জন্য `'0 9 * * *'`)
- **`interval`**: সেকেন্ডে বা একটি timedelta হিসেবে schedule-এর বিরতি
- **`rrule`**: iCalendar RRule schedule string

Docker, Kubernetes বা অন্য infrastructure-এ প্রোডাকশন deployment-এর জন্য, flow-এর [`deploy()`](https://docs.prefect.io/v3/how-to-guides/deployments/deploy-via-python) মেথড ব্যবহার করুন। আরও তথ্যের জন্য দেখুন [Prefect deployment ডকুমেন্টেশন](https://docs.prefect.io/v3/how-to-guides/deployments/create-deployments)।

/// check | সংক্ষেপে মনে রাখুন

* Prefect-এ flow = শীর্ষ স্তর, task = retry/cache-যোগ্য একক; একই cache key-র task আবার চলে না।
* `Agent(name=..., capabilities=[PrefectDurability()])`, আর `agent.run()` নিজের `@flow`-এর ভেতরে।
* মডেল, টুল আর MCP সব নিজে থেকে task; প্রতি-টুল config `metadata={'prefect': TaskConfig(...)}` বা `SetToolMetadata` দিয়ে।
* `TaskConfig`-এর ডিফল্ট `retries` হলো `0`; retry একটি স্তরে রাখুন।
* side-effect টুল idempotent রাখুন — ফল লেখার আগে থেমে যাওয়া task আবার চলে।
* `flow.serve(cron=...)` দিয়ে schedule; এজেন্ট flow-এর ভেতরে তৈরি করুন।

///
