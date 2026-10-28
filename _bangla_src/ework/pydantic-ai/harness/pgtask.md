# pgtask Durability { #pgtask-durability }

/// note | এই পেজে যা শিখবেন

* `PGTaskDurability` দিয়ে একটি এজেন্ট রানকে crash থেকে বাঁচানো — pgtask (Postgres-ভিত্তিক task queue) দিয়ে।
* crash-এর পর কী ঘটে, step-এর নাম, আর মেনে চলার নিয়ম।
* একসাথে টুল চালানো, Code Mode আর tracing।

///

`PGTaskDurability` একটি এজেন্ট রানকে একটি crash থেকে টিকে থাকতে দেয়। এটি কাজ করে [pgtask](https://github.com/Kludex/pgtask)-এর সাথে,
একটি task queue যা এর state Postgres-এ রাখে।

একটি pgtask task-এর ভেতরে এজেন্ট চালান, আর প্রতিটি মডেল রিকোয়েস্ট আর টুল কল শেষ হলে Postgres-এ সংরক্ষিত হয়। worker crash করলে, pgtask task-টি আবার চালায়, আর এজেন্ট মডেল বা টুলকে দ্বিতীয়বার না ডেকে সংরক্ষিত ফল ফেরত পায়, তাই শেষ হওয়া কাজের জন্য আপনাকে দুবার টাকা দিতে হয় না।

একটি pgtask task-এর বাইরে কিছুই সংরক্ষিত হয় না আর এজেন্ট স্বাভাবিকভাবে চলে, শুধু টুল কল তবুও `parallel_execution_mode` মেনে চলে, যা ডিফল্টভাবে এগুলো একবারে একটি চালায় (দেখুন [একসাথে টুল চালানো](#running-tools-at-the-same-time))।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/pgtask/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[pgtask]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[pgtask]" "pydantic-ai-slim[openai]"
```

///


pgtask এর state আপনার ডেটাবেসের table-এ রাখে। প্রতি ডেটাবেসে একবার এগুলো তৈরি করুন:

⟦CODE1⟧

## দ্রুত শুরু { #quick-start }

এজেন্টকে একটি `name` দিন আর এটি চালানো একটি pgtask task লিখুন। তারপর queue-তে task যোগ করুন, আর সেগুলো প্রক্রিয়া করতে একটি worker চালান:

⟦CODE2⟧

## crash-এর পর কী ঘটে { #what-happens-after-a-crash }

pgtask প্রতিটি শেষ হওয়া কাজের অংশকে একটি *step* হিসেবে সংরক্ষণ করে: একটি নাম আর একটি ফল। একটি worker crash করলে, pgtask আপনার task ফাংশন শুরু থেকে আবার চালায়। ফাংশনের সাধারণ কোড আবার চলে, কিন্তু এজেন্ট যখন এমন একটি মডেল রিকোয়েস্ট বা টুল কলে পৌঁছায় যার সংরক্ষিত step আগেই আছে, তখন সংরক্ষিত ফল ব্যবহার করে আর কলটি বাদ দেয়।

- যে টুল `ModelRetry` বা `ToolFailed` তোলে, বা একটি টুলের ভেতরে একটি sub-agent রান যা নিজেকে বাতিল করে বা timeout হয় (`RunCancelled`), সেই ফলাফলও সংরক্ষিত হয়, তাই একটি crash-এর পর মডেল একই error পায় আর টুল আবার চলে না।
- যে টুল অন্য কোনো exception তোলে তার কিছুই সংরক্ষিত হয় না, তাই pgtask task retry করলে এটি আবার চলে।
- একটি MCP সার্ভার শুধু তখনই সংযুক্ত হয় যখন একটি কলের এটি দরকার। এতে প্রতিটি কলের যদি আগেই সংরক্ষিত ফল থাকে, সার্ভারে যোগাযোগই করা হয় না।

### Step-এর নাম { #step-names }

প্রতিটি step-এর নাম হয় এজেন্টের `name` আর toolset-এর `id` অনুযায়ী। এগুলোই সেই নাম যা আপনি Postgres-এ দেখেন, আর এগুলোই কারণ যে একটি এজেন্ট বা toolset-এর task চলমান থাকা অবস্থায় নাম বদলানো উচিত নয়।

| Step-এর নাম | যা সংরক্ষণ করে |
|---|---|
| `{name}__model.request` | একটি মডেল রিকোয়েস্ট |
| `{name}__model.request_stream` | একটি stream করা মডেল রিকোয়েস্ট |
| `{name}__model.compact_messages` | মডেলকে message history ছোট করতে বলা একটি রিকোয়েস্ট |
| `{name}__model.cancel_suspended_response` | মডেল provider এখনও background-এ কাজ করছে এমন একটি response বাতিল করা |
| `{name}__capability__{capability_id}.{operation}` | অন্য একটি capability-র যোগ করা কাজ |
| `{name}__function_toolset__{id}.validate_args` | একটি টুলের আর্গুমেন্ট এর `args_validator` দিয়ে যাচাই |
| `{name}__function_toolset__{id}.call_tool:{tool}` | একটি ফাংশন টুল কল |
| `{name}__dynamic_toolset__{id}.get_tools` | একটি `DynamicToolset`-এর টুল তৈরি |
| `{name}__dynamic_toolset__{id}.call_tool:{tool}` | একটি `DynamicToolset` টুল কল |
| `{name}__mcp_server__{id}.get_tools` | একটি MCP সার্ভারের টুল তালিকা আনা |
| `{name}__mcp_server__{id}.get_instructions` | একটি MCP সার্ভারের instructions আনা |
| `{name}__mcp_server__{id}.call_tool` | একটি MCP টুল কল |
| `{name}__event_stream_handler` | `event_stream_handler`-এ দেওয়া একটি event |

- এজেন্টের ডিফল্ট ছাড়া অন্য মডেল ব্যবহার করা একটি রান শেষে মডেলের id যোগ করে:
  `{name}__model.request.{model_id}`।
- pgtask step নামে যে অক্ষর অনুমতি দেয় না সেগুলো `_` হয়ে যায়। যেমন, `@agent.tool` দিয়ে যোগ করা টুল `_agent_` toolset id-র নিচে সংরক্ষিত হয়।
- একটি task-এ একই step নাম একাধিকবার এলে, যেমন একই টুল দুবার ডাকা বা `agent.run()` দুবার ডাকা, pgtask সেগুলোকে ঘটার ক্রমে 0, 1, 2 এভাবে নম্বর দেয়। একই task-এ পরেরটি শুরুর আগে একটি `agent.run()` শেষ করুন, যাতে একটি crash-এর পর নম্বরগুলো একই আসে।

## নিয়ম { #rules }

- এজেন্টের একটি `name` লাগে, বা `PGTaskDurability`-তে `name=` দিন। প্রতিটি function, MCP আর dynamic toolset-এর নিজের `id` লাগে। কোনোটি অনুপস্থিত থাকলে `Agent(...)` একটি `UserError` তোলে।
- একটি এজেন্ট বা toolset ব্যবহার করা task চলমান থাকা অবস্থায় এর নাম বদলাবেন না। এদের step পুরনো নামে সংরক্ষিত, তাই একটি crash-এর পর নাম-বদলানো কলগুলো আবার চলে।
- টুলের ফল JSON হিসেবে সংরক্ষিত হয়, তাই টুলকে এমন মান ফেরত দিতে হবে যা JSON-এ রূপান্তর করা যায়। যে ফল পারে না তা task ব্যর্থ করে, আর pgtask `max_attempts` শেষ না হওয়া পর্যন্ত এটি retry করে। একটি সংরক্ষিত ফল কল যে টাইপ ফেরত দেয় তার সাথে আর না মিললে, রান টুল আবার না চালিয়ে `CheckpointDecodeError` দিয়ে ব্যর্থ হয়।
- একটি ফল শুধু কল শেষ হওয়ার পরেই সংরক্ষিত হয়। একটি টুল কিছু করার পরে কিন্তু এর ফল সংরক্ষণের আগে worker crash করলে, টুলটি আবার চলে। টুল আর `event_stream_handler` এমনভাবে লিখুন যাতে দুবার চালালে কোনো ক্ষতি না হয়।
- একটি task-এর ভেতরে, `run(toolsets=...)` দিয়ে একটি একক রানে function, MCP বা dynamic toolset দিলে একটি `UserError` ওঠে। এর বদলে এজেন্টে যোগ করুন। `ExternalToolset` ঠিক আছে।
- একটি task-এর ভেতরে streaming লাইভ নয়: পুরো মডেল response আগে পাওয়া আর সংরক্ষণ করা হয়, তারপর এর event আপনাকে পাঠানো হয়।

/// warning | সাধারণ ভুল

একটি টুল থেকে একটি `datetime` অবজেক্ট বা নিজের একটি ক্লাসের instance ফেরত দেওয়া, যা সরাসরি JSON নয়। ফল সংরক্ষণ ব্যর্থ হয়ে task বারবার retry হতে পারে। টুল থেকে string, সংখ্যা, dict, list বা Pydantic model-এর মতো JSON-এ রূপান্তরযোগ্য মান ফেরত দিন।

///

## একসাথে টুল চালানো { #running-tools-at-the-same-time }

ডিফল্টভাবে এজেন্ট টুল কল একবারে একটি চালায়, task-এর ভেতরে হোক বা না হোক। একটি মডেল response-এর টুল কলগুলো একসাথে চালাতে, `parallel_execution_mode='parallel_ordered_events'` দিন। সবগুলো শেষ হলে, মডেল যে ক্রমে কলগুলো চেয়েছিল সেই ক্রমে এদের event পাঠানো হয়। সাধারণ `'parallel'` সমর্থিত নয়, কারণ একটি crash-এর পর step নম্বরগুলো একই আসতে হবে।

অন্য একটি capability-র `before_tool_execute` বা `wrap_tool_execute` hook টুল চলার আগে কোনো কিছুর অপেক্ষা করলে ডিফল্টই রাখুন। একসাথে টুল চললে, সেই অপেক্ষা একটি টুলের কোন কল কোন নম্বর পাবে তা বদলে দিতে পারে, তাই একটি crash-এর পর একটি কল আরেকটি কলের সংরক্ষিত ফল পেতে পারে।

## Code Mode { #code-mode }

[Code Mode](code-mode.md)-এ, `run_code` থেকে করা প্রতিটি টুল কল নিজের step হিসেবে সংরক্ষিত হয়। একটি crash-এর পর `run_code`-এর কোড আবার চলে, কিন্তু এর টুল কল তাদের সংরক্ষিত ফল ফেরত দেয়।

## Tracing { #tracing }

`PGTaskDurability` নিজের কোনো span যোগ করে না: সাধারণ এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল span কাজটি কভার করে। pgtask task যোগ করা কোড থেকে worker পর্যন্ত OpenTelemetry trace বহন করে, তাই রানের span `enqueue` কলের একই trace-এ দেখা যায়।

## `pydantic-ai-pgtask` থেকে migrate { #migrating-from-pydantic-ai-pgtask }

`pydantic_ai_pgtask`-এর বদলে `pydantic_ai_harness.pgtask` থেকে `PGTaskDurability`, `PGTaskParallelExecutionMode` আর `CheckpointDecodeError` import করুন। Step-গুলো [`pydantic-ai-pgtask`](https://github.com/Kludex/pydantic-ai-pgtask) 0.0.3-এর মতো একই নাম আর একই ফরম্যাটে সংরক্ষিত হয়,
তাই বদলের সময় চলমান task কাজ পুনরাবৃত্তি না করে চলতে থাকে। `DurableTaskContext` আর `current_context` আনা হয়নি।

## Step Persistence-এর সাথে সম্পর্ক { #relation-to-step-persistence }

`PGTaskDurability` একটি রানকে একটি crash-এর পর চলতে দেয়। [Step Persistence](step-persistence.md) রানগুলো লিখে রাখে, যাতে আপনি পরে সেগুলো আবার চালাতে, fork বা replay করতে পারেন। আপনি দুটো একসাথে ব্যবহার করতে পারেন।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [pgtask](https://github.com/Kludex/pgtask)

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.pgtask.PGTaskDurability`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/pgtask/)।

///

/// check | সংক্ষেপে মনে রাখুন

* pgtask = Postgres-ভিত্তিক task queue; table একবার তৈরি করুন, task যোগ করুন, worker চালান।
* প্রতিটি মডেল রিকোয়েস্ট আর টুল কল শেষ হলে সংরক্ষিত হয়; crash-এর পর সংরক্ষিত ফল ফেরত আসে।
* এজেন্টের `name` আর toolset `id` বাধ্যতামূলক; task চলাকালীন নাম বদলাবেন না।
* টুলের ফল JSON-যোগ্য রাখুন; side effect দুবার চললেও নিরাপদ রাখুন।
* একসাথে চালাতে `'parallel_ordered_events'`।

///
