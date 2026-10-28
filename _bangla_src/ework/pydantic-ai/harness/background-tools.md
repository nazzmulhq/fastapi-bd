
# Background Tools { #background-tools }

/// note | এই পেজে যা শিখবেন

* `BackgroundTools` দিয়ে ধীর tool background-এ চালানো, যাতে agent অপেক্ষা না করে অন্য কাজ চালিয়ে যায়।
* কোন tool background-এ যাবে তা বাছাই — সবসময়, বা মডেলের ইচ্ছায় (`'optional'`)।
* run চলাকালীন কী ঘটে: "শুরু হয়েছে" বার্তা, task ID, আর পরে ফল।
* সীমাবদ্ধতা, tracing আর durable execution।

///

`BackgroundTools` বাছাই করা tool-গুলোকে background-এ চলতে দেয়, আর agent অপেক্ষা না করে
এগিয়ে যায়। যখন ফল তৈরি হওয়া পর্যন্ত মডেল অন্য কিছু নিয়ে কাজ করতে পারে, তখন এটি ব্যবহার করুন।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/background_tools/)

এই উদাহরণ চালানোর আগে OpenAI provider ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[openai]" pydantic-ai-harness
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[openai]" pydantic-ai-harness
```

///


⟦CODE1⟧

ডিফল্টভাবে, `metadata={'background': True}`-ওয়ালা যেকোনো tool background-এ চলে। tool চলার সময় কীভাবে এগিয়ে যেতে হবে, `BackgroundTools` তা মডেলকে বলে দেয়।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// tip | উদাহরণ দিয়ে বুঝি

ওয়াশিং মেশিনে কাপড় দিয়ে আপনি পাশে দাঁড়িয়ে থাকেন না — রান্না শুরু করেন, মেশিন শেষ হলে বিপ দেয়। `slow_research` হলো সেই ওয়াশিং মেশিন: মডেল এটি চালু করে একটি task ID (রসিদ) পায়, অন্য কাজ চালিয়ে যায়, আর ফল তৈরি হলে একই task ID-সহ একটি বার্তা পায়।

///

## কোন tool background-এ চলবে তা বাছাই { #selecting-which-tools-run-in-the-background }

`BackgroundTools(tools=...)` প্রচলিত [`ToolSelector`][pydantic_ai.tools.ToolSelector] নেয়:

⟦CODE2⟧

### মডেলকে সিদ্ধান্ত নিতে দেওয়া { #letting-the-model-decide }

প্রতিটি call-এর জন্য মডেলকে সিদ্ধান্ত নিতে দিতে `metadata={'background': 'optional'}` ব্যবহার করুন। মডেল একটি
`run_in_background` argument দেখে, কিন্তু আপনার function সেটি পায় না।

`BackgroundTools(tools=...)` দিয়ে বাছাই করা tool সবসময় background-এ চলে। sequential tool,
realtime session, আর code mode-এর `run_code` তার sandbox থেকে যে call করে — এগুলো `run_in_background` থাকলেও
স্বাভাবিকভাবে চলে। `run_in_background`-কে আপনার function-এর নিজের কোনো parameter হিসেবে ব্যবহার করবেন না।

⟦CODE3⟧

/// info | এক নজরে: কখন background-এ চলে

| চিহ্ন | আচরণ |
|---|---|
| `metadata={'background': True}` (ডিফল্ট selector) | সবসময় background-এ |
| `BackgroundTools(tools=...)`-এ বাছাই করা | সবসময় background-এ |
| `metadata={'background': 'optional'}` | মডেল `run_in_background` দিয়ে প্রতি call-এ ঠিক করে |
| sequential tool, realtime session, `run_code`-এর ভেতরের call | সবসময় স্বাভাবিকভাবে (foreground) |

///

### একসাথে অনেক tool চিহ্নিত করা { #marking-tools-in-bulk }

আলাদা আলাদা definition না ছুঁয়েই কয়েকটি tool-কে background হিসেবে চিহ্নিত করতে [`SetToolMetadata`](../capabilities/set-tool-metadata.md) বা `FunctionToolset.with_metadata(...)`-এর সাথে মেলান:

⟦CODE4⟧

## run চলাকালীন কী ঘটে { #what-happens-during-a-run }

মডেল প্রথমে একটি বার্তা পায়, যাতে বলা থাকে tool শুরু হয়েছে। বার্তায় একটি task ID থাকে।
tool শেষ হলে মডেল একই task ID-সহ ফলটি পায়।

প্রতিটি পরবর্তী বার্তা (follow-up) হলো একটি [`ModelRequest`][pydantic_ai.messages.ModelRequest], যাতে একটি
[`UserPromptPart`][pydantic_ai.messages.UserPromptPart] থাকে, যার প্রথম content item হলো
[`TextContent`][pydantic_ai.messages.TextContent], সাথে
`metadata={'origin': 'pydantic-ai-harness.background_tools.result.v1', 'tool_call_id': original_tool_call_id}` — সামলানো
ব্যর্থতার notification-সহ। এটি পুরো completion part-কে চিহ্নিত করে, যেকোনো ফাইল আর বাড়তি
content-সহ। metadata মডেলের কাছে পাঠানো হয় না, আর native message serialization ও পরপর request মেশানোর পরেও
টিকে থাকে। Vercel AI আর AG-UI message রূপান্তর এই metadata বাদ দেয়। সেগুলো থেকে আবার লোড করা
history text আর তার ফ্রেম রাখে, কিন্তু follow-up তখন একটি সাধারণ user
prompt হয়ে যায়।

follow-up tool যা ফেরত দিয়েছে তা `<tool_result tool_name="..." tool_call_id="...">`
tag-এ মুড়ে দেয় — একই tag যা Pydantic AI user channel-এ পাঠানো tool ফাইলের চারপাশে বসায়। এটি
মডেলকে বলে যে text-টি tool-এর output, ব্যবহারকারীর বলা কিছু নয়, আর কোন অপেক্ষমাণ call এটি
সম্পূর্ণ করে। output-এর ভেতরে একটি closing `</tool_result>` tag escape করা হয়, তাই output ফ্রেম
আগেভাগে শেষ করতে পারে না। একটি ব্যর্থ call-ও একইভাবে ফ্রেম করা হয় `outcome="failed"`-সহ, যা
`ModelRetry` বা `ToolFailed`-এর বার্তা মুড়ে রাখে।

tool-এর ফেরত দেওয়া text আর ফাইল মডেলের কাছে পাঠানো হয়। [`ToolReturn.metadata`][pydantic_ai.messages.ToolReturn.metadata]
বাদ দেওয়া হয়।
`ModelRetry`, `ToolFailed`, approval আর deferral error মডেলকে text হিসেবে জানানো হয় — একটি
`before_tool_execute` বা `after_tool_execute` hook এগুলো raise করলেও। এমন hook থেকে আসা একটি `ValidationError`-ও
জানানো হয়, যেমন একটি sequential tool সেটি retry করে। অন্য যেকোনো tool exception মূল exception দিয়ে
run শেষ করে, sequential tool-এর মতোই।
retry ফুরিয়ে গেলে বা `CancelledError` raise হলেও run শেষ হয়। run শেষ হয় তার পরের ধাপে, তাই
ইতিমধ্যে চলমান একটি model request আগে শেষ হয়। একটি tool `ctx.cancel()` ডেকে run আর
অন্য background tool-গুলো থামাতে পারে।

একটি স্বাভাবিক run তার background tool-গুলো শেষ হওয়ার জন্য অপেক্ষা করে। একটি অপেক্ষমাণ call
`tool_calls_limit`-এ গোনা হয়। run deferred tool-এর জন্য থামলে বা আগেভাগে বন্ধ হলে, অসম্পূর্ণ tool
বাতিল হয়, আর যে ফলগুলো এখনও পৌঁছানো হয়নি সেগুলো বাদ পড়ে — এমনকি শেষ হয়ে যাওয়া tool-এর ফলও।
run আবার চালু করলে সেগুলো পৌঁছায় না। async tool-কে cancellation মেনে নিতে হবে; উপেক্ষা করলে
run থামতে নাও পারে।

/// warning | সতর্কতা

Python একটি synchronous tool ফেরত আসার আগে সেটি থামাতে পারে না। run বাতিল করলেও
ওই tool-এর জন্য অপেক্ষা করা হবে।

একটি synchronous background tool agent বা অন্য কোনো tool-এর সাথে একই সময়ে শেয়ার করা data বদলে
ফেলতে পারে। শেয়ার করা data-কে সমসাময়িক পরিবর্তন থেকে রক্ষা করুন।

///

/// info | এক নজরে: মডেল যা দেখে

| মুহূর্ত | মডেলের কাছে যা আসে |
|---|---|
| tool call-এর সাথে সাথে | "tool শুরু হয়েছে" বার্তা + একটি task ID |
| tool সফলভাবে শেষ হলে | user message-এ `<tool_result tool_name="..." tool_call_id="...">…</tool_result>` |
| tool ব্যর্থ হলে (`ModelRetry` / `ToolFailed`) | একই ফ্রেম, সাথে `outcome="failed"` |
| run আগেভাগে থামলে | অসম্পূর্ণ tool বাতিল, না-পৌঁছানো ফল বাদ |

///

## সীমাবদ্ধতা { #limitations }

- `run_stream()` আর `run_stream_sync()` background tool-এর জন্য অপেক্ষা করে কিন্তু তাদের ফল পৌঁছে দেয় না।
  stream করা response হয়তো শুধু বলবে যে কাজ শুরু হয়েছে। চূড়ান্ত response-এ ফল লাগলে `run_stream_events()`, `run()`,
  `run_sync()` ব্যবহার করুন, অথবা পুরো `agent.iter()` গ্রহণ করুন।
- একটি sequential tool আগে শুরু হওয়া background কাজের সাথে একই সময়ে চলতে পারে। যে tool-গুলো একসাথে চলা উচিত নয়,
  সেগুলোর উচিত শেয়ার করা data রক্ষা করা, বা background-এ না চলা।
- realtime session আগে থেকেই tool সমসাময়িকভাবে চালায়, তাই `BackgroundTools` সেগুলো অপরিবর্তিত রাখে।
- একটি background tool, বা তার execute hook থেকে আসা `ModelRetry` tool-এর
  `retries`-এ গোনা হয় শুধু তখনই, যখন tool agent-এর পরের ধাপের আগে শেষ হয়। ধীর tool-এর retry
  গোনা হয় না, তাই যে মডেল বারবার এটি retry করে, তাকে সীমায় বাঁধে `UsageLimits.request_limit`।
- `BackgroundTools`-এর পরে তালিকাভুক্ত capability-গুলোর `after_tool_execute`, `on_tool_execute_error` আর `wrap_tool_execute` hook
  background task-এর ভেতরে চলে আর আসল ফল দেখে।
  এর আগে তালিকাভুক্ত capability-গুলোর `wrap_tool_execute` hook, আর tool result event, দেখে
  "শুরু হয়েছে" বার্তা।
- ফল মডেলের কাছে পৌঁছায় একটি user message হিসেবে, সাধারণ text-এ, যাতে tool আর task-এর নাম থাকে। যে
  tool অবিশ্বস্ত content ফেরত দেয়, যেমন fetch করা একটি web page, সে ওই content-কে
  অন্য কোনো task-এর ফলের মতো দেখাতে পারে। এমন output tool-এর ভেতরেই সীমানা-চিহ্নিত বা পরিষ্কার (sanitize) করুন।
- `RepairToolArguments`, বা যে `Coder` এটি অন্তর্ভুক্ত করে, `BackgroundTools`-এর আগে তালিকাভুক্ত করুন। নইলে
  `run_in_background` সেট করা একটি ভুল-গঠনের call মেরামত না হয়ে retry হয়। মেরামত করা call চলে
  foreground-এ।

/// warning | সাধারণ ভুল

`run_stream()` দিয়ে চালিয়ে দেখছেন উত্তরে শুধু "গবেষণা শুরু হয়েছে" লেখা, আসল ফল নেই? কারণ `run_stream()` background tool-এর ফল পৌঁছে দেয় না। ফল দরকার হলে `run()`, `run_sync()` বা `run_stream_events()` ব্যবহার করুন।

///

## Tracing { #tracing }

`BackgroundTools` কোনো tracing span যোগ করে না। Pydantic AI-এর tool span শেষ হয় যখন "শুরু হয়েছে" বার্তা
ফেরত যায়, তাই এটি tool-এর কাজ ঢাকে না বা কোনো ব্যর্থতা রেকর্ড করে না। সম্পূর্ণ ফল থেকে যায়
agent-এর message history-তে।

## Durable execution { #durable-execution }

`BackgroundTools` Temporal-এর সাথে কাজ করে।

DBOS-এর সাথে, durable কাজ একটি স্পষ্ট DBOS step-এ রাখুন আর background tool থেকে সেই step ডাকুন।

durable activity বা task-এর ভেতরে `ctx.enqueue()` ডাকবেন না। replay-এর সময় এর message-গুলো
পুনরুদ্ধার করা যায় না।

## API { #api }

```python
BackgroundTools(tools: ToolSelector = {'background': True})
```

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

এই উদাহরণ ব্যবহারের আগে Agent spec সাপোর্ট ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[spec]" pydantic-ai-harness
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[spec]" pydantic-ai-harness
```

///


⟦CODE5⟧

⟦CODE6⟧

## আরও পড়ুন { #further-reading }

- [Injecting messages during a run](../message-history.md#injecting-messages-mid-run)
- [Pydantic AI capabilities](../capabilities/overview.md)

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[BackgroundTools()]` + tool-এ `metadata={'background': True}` → tool background-এ চলে, মডেল অপেক্ষা করে না।
* `'optional'` দিলে মডেল প্রতি call-এ `run_in_background` দিয়ে ঠিক করে; আপনার function এই argument পায় না।
* মডেল আগে task ID-সহ "শুরু হয়েছে" বার্তা পায়, পরে user message-এ `<tool_result>` ফ্রেমে ফল।
* `run_stream()` ফল পৌঁছে দেয় না — `run()` / `run_sync()` / `run_stream_events()` ব্যবহার করুন।
* run আগেভাগে থামলে অসম্পূর্ণ tool বাতিল আর না-পৌঁছানো ফল হারিয়ে যায়।
* অবিশ্বস্ত content ফেরত দেওয়া tool-এর output tool-এর ভেতরেই পরিষ্কার করুন।

///
