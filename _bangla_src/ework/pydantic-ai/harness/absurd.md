
# Absurd Durability { #absurd-durability }

/// note | এই পেজে যা শিখবেন

* `AbsurdDurability` দিয়ে শুধু Postgres-এর ওপর একটি এজেন্ট রান durable করা।
* কী checkpoint হয় আর কী replay-তে আবার চলে।
* সীমাবদ্ধতা, সমান্তরাল চালানো আর `pydantic-ai-absurd` থেকে migrate।

///

`AbsurdDurability` একটি এজেন্ট রানকে [Absurd](https://github.com/earendil-works/absurd)-এ durable করে,
যা একটি Postgres-ভিত্তিক durable-execution engine। একটি Absurd task handler-এর ভেতরে এজেন্ট চালান, আর প্রতিটি মডেল রিকোয়েস্ট, MCP কল আর ফাংশন টুল কল একটি step হিসেবে checkpoint হয়, তাই রানের মাঝে crash করা একটি worker শেষ হওয়া কাজে আবার token খরচ না করে শেষ সম্পন্ন step থেকে আবার চলে। একটি task-এর বাইরে capability স্বচ্ছ।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/absurd/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// tip | উদাহরণ দিয়ে বুঝি

আপনার অ্যাপে আগে থেকেই Postgres আছে, কিন্তু Temporal-এর মতো আলাদা সার্ভার চালাতে চান না? Absurd পুরো queue আর checkpoint ব্যবস্থাটাই Postgres-এর ভেতরে রাখে। একটি "producer" task তৈরি করে, একটি "worker" তা চালায়, আর প্রতিটি মডেল/টুল কলের ফল Postgres-এ লেখা হয়।

///

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[absurd]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[absurd]" "pydantic-ai-slim[openai]"
```

///


Absurd এর state Postgres-এ রাখে। প্রতি ডেটাবেসে একবার Absurd schema ইনস্টল করুন (দেখুন
[Absurd repository](https://github.com/earendil-works/absurd)), তারপর একটি queue তৈরি করুন:

⟦CODE1⟧

## দ্রুত শুরু { #quick-start }

এজেন্টকে একটি `name` দিন, এটি চালানো একটি task handler নিবন্ধন করুন, তারপর একটি producer থেকে task তৈরি করুন আর একটি worker-এ সেগুলো চালান:

⟦CODE2⟧

handler অবশ্যই async হতে হবে: একটি synchronous `TaskContext` একটি `UserError` তোলে।

## কী checkpoint হয় { #what-gets-checkpointed }

একটি crash-এর পর, Absurd task handler শুরু থেকে আবার চালায়। handler-এর সাধারণ Python আবার চলে, কিন্তু প্রতিটি সম্পন্ন step মডেল রিকোয়েস্ট বা টুল কল আবার না পাঠিয়ে এর সংরক্ষিত ফল ফেরত দেয়। Step-এর নাম তৈরি হয় এজেন্টের `name` আর প্রতিটি toolset-এর `id` থেকে:

| Step-এর নাম | কাজ |
|---|---|
| `{name}__model.request` | একটি মডেল রিকোয়েস্ট অংশ |
| `{name}__model.request_stream` | একটি stream করা মডেল রিকোয়েস্ট অংশ |
| `{name}__model.compact_messages` | একটি মডেল message-compaction কাজ |
| `{name}__model.cancel_suspended_response` | একটি স্থগিত response গুটিয়ে ফেলা |
| `{name}__capability__{capability_id}.{operation}` | অন্য একটি capability-র দেওয়া একটি কাজ |
| `{name}__function_toolset__{id}.validate_args` | একটি ফাংশন টুলের `args_validator` চালানো |
| `{name}__function_toolset__{id}.call_tool:{tool}` | একটি ফাংশন টুল কল |
| `{name}__mcp_server__{id}.get_tools` | একটি MCP সার্ভারের টুল তালিকা |
| `{name}__mcp_server__{id}.get_instructions` | একটি MCP সার্ভারের instructions |
| `{name}__mcp_server__{id}.call_tool` | একটি MCP টুল কল |
| `{name}__event_stream_handler` | একটি `event_stream_handler`-এ পাঠানো একটি event |

এজেন্টের ডিফল্ট ছাড়া অন্য একটি মডেল step নামে এর id যোগ করে
(`{name}__model.request.{model_id}`)। পুনরাবৃত্ত একটি step নাম, যেমন একই task-এ একটি দ্বিতীয় `agent.run()` বা একই টুল দুবার ডাকা, একটি সাক্ষাৎ-ক্রমের প্রত্যয় পায় (`#2`, `#3`, ...)। একই task-এ পরেরটি শুরুর আগে একটি রান await করুন।

এগুলো checkpoint হয় না আর replay-তে আবার চলে:

- যে টুল কল `ModelRetry`, `ToolFailed`, `CallDeferred` বা `ApprovalRequired` তোলে;
- একটি `DynamicToolset`-এর টুল।

## সীমাবদ্ধতা { #constraints }

- এজেন্টের একটি `name` লাগে (বা `AbsurdDurability`-তে `name=` দিন), আর প্রতিটি function, MCP বা dynamic toolset-এর একটি অনন্য `id` লাগে; অন্যথায় `Agent(...)` একটি `UserError` তোলে। deploy-এর পর কোনোটির নাম বদলাবেন না: চলমান task-গুলো যে step-এর নাম বদলেছে সেগুলো আবার চালায়।
- একটি checkpoint করা টুলের ফেরত মান JSON হিসেবে সংরক্ষিত হয়, তাই এটি JSON-serialize-যোগ্য হতে হবে।
- একটি step চলার পরে checkpoint হয়, তাই একটি টুলের side effect আর এর checkpoint-এর মাঝে একটি crash টুলটি আবার চালায়। টুলে আর একটি `event_stream_handler`-এ side effect idempotent রাখুন।
- একটি task-এর ভেতরে `run(toolsets=...)` দিয়ে প্রতি রানে দেওয়া function, MCP বা dynamic toolset একটি `UserError` তোলে; এর বদলে এজেন্টে নিবন্ধন করুন। `ExternalToolset` অনুমোদিত।
- একটি task-এর ভেতরে streaming লাইভ নয়: মডেল stream step-এর ভেতরে গ্রহণ হয়, তারপর এর চূড়ান্ত response caller-এর কাছে replay হয়, প্রতি অংশে একটি event।

## সমান্তরাল চালানো { #parallel-execution }

টুল কল ডিফল্টভাবে একটার পর একটা চলে। একসাথে চালাতে `parallel_execution_mode='parallel_ordered_events'` দিন; সাধারণ `'parallel'` সমর্থিত নয়। `before_tool_execute` বা `wrap_tool_execute`-এর মতো একটি capability hook টুল চলার আগে await করলে ক্রমিকই থাকুন, কারণ তা replay-তে একই টুলের একসাথে চলা কলের ক্রম বদলে দিতে পারে।

## Code Mode { #code-mode }

`AbsurdDurability` [Code Mode](code-mode.md)-এর সাথে মিলে যায়: `run_code` থেকে করা প্রতিটি টুল কল নিজের step, replay-তে এর checkpoint থেকে পরিবেশিত হয়, আর `run_code` body নিজে আবার চলে।

## `pydantic-ai-absurd` থেকে migrate { #migrating-from-pydantic-ai-absurd }

`pydantic_ai_absurd`-এর বদলে `pydantic_ai_harness.absurd` থেকে `AbsurdDurability` আর `AbsurdParallelExecutionMode` import করুন। Step-এর নাম আর checkpoint payload
[`pydantic-ai-absurd`](https://github.com/Kludex/pydantic-ai-absurd) 0.8-এর সাথে মেলে, তাই বদলের সময় চলমান task কাজ পুনরাবৃত্তি না করে আবার চলে। `id` ছাড়া একটি toolset-এর এখন একটি লাগে, আর এটি যোগ করলে চলমান task-এ ওই toolset-এর step আবার চলে। `AbsurdAgent`, `AbsurdModel`,
`AbsurdFunctionToolset` আর `AbsurdMCPToolset` আনা হয়নি; আগে capability-তে সরে যান।

## Step Persistence-এর সাথে সম্পর্ক { #relation-to-step-persistence }

`AbsurdDurability` একটি crash-এর পর একটি একক রান আবার চালায়। [Step Persistence](step-persistence.md)
রানগুলো লিখে রাখে, যাতে সেগুলো পরে আলাদা invocation হিসেবে আবার চালানো, fork বা replay করা যায়। দুটো একসাথে কাজ করে।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Absurd](https://github.com/earendil-works/absurd)

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.absurd.AbsurdDurability`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/absurd/)।

///

/// check | সংক্ষেপে মনে রাখুন

* Absurd = শুধু Postgres-এর ওপর durable execution; schema একবার ইনস্টল করে একটি queue তৈরি করুন।
* এজেন্টে `name` আর `AbsurdDurability()`; handler async হতে হবে।
* মডেল, MCP আর ফাংশন টুল কল checkpoint হয়; `ModelRetry`/deferral তোলা কল আর `DynamicToolset` টুল replay-তে আবার চলে।
* টুলের ফেরত মান JSON-serialize-যোগ্য আর side effect idempotent রাখুন।
* সমান্তরাল চাইলে `'parallel_ordered_events'`।

///
