# Hooks { #hooks }

/// note | এই পেজে যা শিখবেন

* Hook কী: একটি রানের প্রতিটি ধাপে (মডেল রিকোয়েস্ট, টুল কল, আউটপুট, event) নিজের কোড ঢোকানোর জায়গা।
* `Hooks` capability-তে `@hooks.on.*` decorator বা constructor আর্গুমেন্ট দিয়ে hook নথিভুক্ত করা।
* প্রতিটি ধাপের জীবনচক্র: `wrap_*` → `before_*` → কাজ (ব্যর্থ হলে `on_*_error`) → `after_*`।
* টুল ছাঁকা, timeout, hook-এর ক্রম, error hook, আর `ModelRetry`/`ToolFailed` দিয়ে আবার চেষ্টা বা ব্যর্থতা জানানো।

///

Hook দিয়ে একটি রানের প্রতিটি পর্যায়ে — মডেল রিকোয়েস্ট, টুল কল, stream-এর event — এজেন্টের আচরণ মাঝপথে ধরতে আর বদলাতে পারেন, সাধারণ decorator বা constructor আর্গুমেন্ট দিয়ে। কোনো subclass তৈরি করতে হয় না।

লগিং, মেট্রিক্স আর হালকা যাচাইয়ের মতো অ্যাপ্লিকেশন-স্তরের বিষয়ে [lifecycle hooks](capabilities/custom.md#hooking-into-the-lifecycle) যোগ করার প্রস্তাবিত উপায় হলো [`Hooks`][pydantic_ai.capabilities.Hooks] capability। hook-এর সাথে টুল, নির্দেশনা বা মডেল সেটিং মিলিয়ে পুনর্ব্যবহারযোগ্য capability বানাতে, বদলে [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability]-এর subclass করুন — দেখুন [Building custom capabilities](capabilities/custom.md)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি কারখানার অ্যাসেম্বলি লাইন ভাবুন: কাঁচামাল আসে, যন্ত্রে যায়, পণ্য বেরোয়। Hook হলো লাইনের নির্দিষ্ট জায়গায় দাঁড় করানো পরিদর্শক: কেউ যন্ত্রে ঢোকার আগে দেখে ("before"), কেউ বেরোনোর পরে ("after"), কেউ গোলমাল হলে সামলায় ("error"), আর কেউ পুরো যন্ত্রটিকেই ঘিরে থাকে ("wrap") — চাইলে সে যন্ত্র চালানোই বাদ দিতে পারে। লাইনটি (এজেন্ট) না বদলেই আপনি এই পরিদর্শকদের বসাতে পারেন।

///

## Hook-এর জীবনচক্র { #hook-lifecycle }

একটি রানের প্রতিটি পর্যায়ের (রান নিজে, প্রতিটি node, মডেল রিকোয়েস্ট, টুল কল আর আউটপুট) একই hook জীবনচক্র:

```text
wrap_* enter → before_* → operation (on_*_error if it fails) → after_* → wrap_* exit
```

অর্থাৎ: `wrap_*` ঢোকে → `before_*` → মূল কাজ (ব্যর্থ হলে `on_*_error`) → `after_*` → `wrap_*` বেরোয়।

একটি `wrap_*` hook তার handler না ডেকে ফেরত এলে, তার ভেতরের সবকিছু বাদ পড়ে। [`run_stream()` node hook ভিন্নভাবে সামলায়](#node-hooks), আর একাধিক hook আর capability কীভাবে মেলে তা আছে [Hook ordering](#hook-ordering)-এ।

## দ্রুত শুরু { #quick-start }

একটি [`Hooks`][pydantic_ai.capabilities.Hooks] instance তৈরি করুন, `@hooks.on.*` decorator দিয়ে hook নথিভুক্ত করুন, আর সেটি আপনার এজেন্টকে দিন:

```python title="hooks_decorator.py"
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()


@hooks.on.before_model_request
async def log_request(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    print(f'Sending {len(request_context.messages)} messages to the model')
    #> Sending 1 messages to the model
    return request_context


agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello!')
print(result.output)
#> success (no tool calls)
```

## Hook নথিভুক্ত করা { #registering-hooks }

### Decorator দিয়ে নথিভুক্তি { #decorator-registration }

`hooks.on` namespace প্রতিটি জীবনচক্র hook-এর জন্য decorator মেথড দেয়। এগুলো খালি decorator হিসেবে বা প্যারামিটারসহ ব্যবহার করুন:

```python
# Bare decorator
@hooks.on.before_model_request
async def my_hook(ctx, request_context):
    return request_context

# With parameters (timeout, tool filter)
@hooks.on.before_model_request(timeout=5.0)
async def my_timed_hook(ctx, request_context):
    return request_context
```

একই event-এর জন্য একাধিক hook নথিভুক্ত করা যায় — সেগুলো নথিভুক্তির ক্রমে চলে।

### Constructor kwargs { #constructor-kwargs }

hook ফাংশন সরাসরি [`Hooks`][pydantic_ai.capabilities.Hooks] constructor-এও দিতে পারেন:

```python title="hooks_constructor.py"
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks


async def log_request(ctx: RunContext, request_context: ModelRequestContext) -> ModelRequestContext:
    print(f'Sending {len(request_context.messages)} messages to the model')
    #> Sending 1 messages to the model
    return request_context


agent = Agent('test', capabilities=[Hooks(before_model_request=log_request)])
result = agent.run_sync('Hello!')
print(result.output)
#> success (no tool calls)
```

sync আর async দুই ধরনের hook ফাংশনই গ্রহণযোগ্য। sync ফাংশন একটি thread pool-এ চলে, তাই একটি ধীর ফাংশন রানের বাকি অংশ আটকে রাখবে না।

/// note | Sync hook একটি আলাদা thread-এ চলে

Pydantic AI ধরে নেয় যে একটি sync hook-এ blocking কোড আছে (না থাকলে সেটি async হতে পারত), তাই রানের বাকি অংশ সাড়া দেওয়ার মতো রাখতে sync hook একটি worker thread-এ চালায়। এর দুটি ফল: hook-টি একটি [`contextvars.ContextVar`][contextvars.ContextVar]-এ যে মান সেট করে তা hook-এর বাইরে দেখা যায় না, আর `asyncio.get_running_loop()`-এর মতো asyncio API এরর তোলে, কারণ worker thread-এ কোনো event loop নেই। context variable পড়া তবুও কাজ করে, কিন্তু লেখার এই সীমাবদ্ধতা সেসব লাইব্রেরিতেও প্রযোজ্য যারা ভেতরে এগুলো ব্যবহার করে, যেমন tracing আর logging integration। আপনার hook-এর এগুলোর কোনোটি দরকার হলে, সেটি async করুন।

///

### চাহিদামতো hook (On-demand hooks) { #on-demand-hooks }

[`Hooks`][pydantic_ai.capabilities.Hooks] একটি capability, তাই অন্য যেকোনো capability-র মতোই চাহিদামতো লোড করা যায়। ঐচ্ছিক, ব্যবহারকারীর চাওয়া আচরণে এটি কাজে লাগে, যেমন বিস্তারিত রিকোয়েস্ট লগিং:

```python title="deferred_hooks_capability.py"
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks

request_logging_hooks = Hooks(
    id='request-logging',
    description='Use when the user asks for verbose request diagnostics.',
    defer_loading=True,
)


@request_logging_hooks.on.before_model_request
async def log_request(
    ctx: RunContext,
    request_context: ModelRequestContext,
) -> ModelRequestContext:
    print(f'Model request at step {ctx.run_step}: {len(request_context.messages)} messages')
    return request_context


agent = Agent('openai-responses:gpt-6.1-sol', capabilities=[request_logging_hooks])
```

একটি deferred `Hooks` instance-এর hook, তার capability লোড না হওয়া পর্যন্ত Pydantic AI এড়িয়ে যায়।

ঐচ্ছিক যে আচরণ capability লোড হওয়ার পরেই প্রযোজ্য, তার জন্য চাহিদামতো hook ব্যবহার করুন। human-in-the-loop টুল অনুমোদনের জন্য, একটি টুল নথিভুক্ত করার সময় [`requires_approval=True`](deferred-tools.md#human-in-the-loop-tool-approval) দিন, শর্তসাপেক্ষ অনুমোদনের জন্য [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] তুলুন, বা একটি toolset [`ApprovalRequiredToolset`][pydantic_ai.toolsets.ApprovalRequiredToolset]-এ মুড়ে দিন।

## Hook-এর ধরন { #hook-types }

নিচের প্রতিটি টেবিলে একই hook-এর তিনটি নাম আছে: `hooks.on.` decorator-এ যে নাম, `Hooks(...)` constructor-এ যে keyword আর্গুমেন্ট, আর নিজের `AbstractCapability` subclass-এ যে মেথড override করবেন।

### রান hook { #run-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_run` | `before_run=` | `before_run` |
| `after_run` | `after_run=` | `after_run` |
| `run` | `run=` | `wrap_run` |
| `run_error` | `run_error=` | `on_run_error` |

রানের জীবনচক্র প্রতিটি এজেন্ট রানে একবার পাঠানো হয়। `wrap_run` (`hooks.on.run` দিয়ে নথিভুক্ত) একবার চলে আর `before_run`, `on_run_error` উদ্ধারসহ graph iteration, আর `after_run`-কে ঘিরে রাখে; যে wrapper তার handler ডাকে না, সে ভেতরের hook-গুলো বাদ দেয়।

একটি [realtime session](realtime/capabilities.md) একটি রান: একই চারটি hook session-এর চারপাশে একবার চলে, session বন্ধ হলে `wrap_run` উদ্ধার আর `after_run` ফল-রূপান্তর প্রয়োগ হয়।

### Node hook { #node-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_node_run` | `before_node_run=` | `before_node_run` |
| `after_node_run` | `after_node_run=` | `after_node_run` |
| `node_run` | `node_run=` | `wrap_node_run` |
| `node_run_error` | `node_run_error=` | `on_node_run_error` |

Node hook প্রতিটি graph ধাপে চলে ([`UserPromptNode`][pydantic_ai.agent.UserPromptNode], [`ModelRequestNode`][pydantic_ai.agent.ModelRequestNode], [`CallToolsNode`][pydantic_ai.agent.CallToolsNode])।

রান যেভাবেই চালানো হোক, node hook চলে: [`agent.run()`][pydantic_ai.agent.AbstractAgent.run], [`agent_run.next()`][pydantic_ai.run.AgentRun.next], আর [`agent.iter()`][pydantic_ai.agent.Agent.iter]-এর ওপর `async for node in agent_run:` — সবই রানকে একইভাবে এগিয়ে নেয়।

/// note | মনে রাখুন

[`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] stream-এর চারপাশে node জীবনচক্র ভাগ করে: stream খোলার আগে `before_node_run` চলে। চূড়ান্ত নয় এমন stream করা node-এ, `wrap_node_run` শুধু graph এগোনোকে ঘিরে রাখে; `on_node_run_error` আর `after_node_run` এর বাইরে চলে। চূড়ান্ত stream করা `ModelRequestNode` `wrap_node_run` আর `after_node_run` বাদ দেয়, কারণ `run_stream()` stream-এর মাঝে চূড়ান্ত আউটপুট পাওয়া মাত্র ফেরত আসে।

///

### মডেল রিকোয়েস্ট hook { #model-request-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_model_request` | `before_model_request=` | `before_model_request` |
| `after_model_request` | `after_model_request=` | `after_model_request` |
| `model_request` | `model_request=` | `wrap_model_request` |
| `model_request_error` | `model_request_error=` | `on_model_request_error` |

মডেল রিকোয়েস্ট hook প্রতিটি LLM কলের চারপাশে চলে। [`ModelRequestContext`][pydantic_ai.models.ModelRequestContext] একসাথে বাঁধে `model`, `messages`, `model_settings` আর `model_request_parameters`। একটি নির্দিষ্ট রিকোয়েস্টের মডেল বদলাতে, `request_context.model`-কে একটি ভিন্ন [`Model`][pydantic_ai.models.Model] instance-এ সেট করুন।

`before_model_request` আর `model_request` (wrap) বার্তা-সংরক্ষণের একই নিয়ম মানে। প্রতিটি বার্তার দুটি শীর্ষ-স্তরের দৃশ্য পায়:

- `request_context.messages` বদলালে বা নতুন করে assign করলে শুধু বর্তমান মডেল রিকোয়েস্ট বদলায় (নিচের deprecated append ছাড়া)।
- `ctx.messages` তালিকা বদলালে `all_messages()`-এর ফেরত দেওয়া আর পরের রিকোয়েস্টে ব্যবহৃত স্থায়ী ইতিহাস বদলায়, কিন্তু বর্তমান মডেল রিকোয়েস্ট নয়।
- দুটোই বদলাতে, দুটোই স্পষ্টভাবে হালনাগাদ করুন।

/// info | দুই দৃশ্য, সহজ ভাষায়

`request_context.messages` = "এই একটি চিঠিতে কী যাবে"। `ctx.messages` = "খাতায় স্থায়ীভাবে কী লেখা থাকবে"। একটি সাময়িক নির্দেশনা শুধু এই রিকোয়েস্টে জুড়তে চাইলে প্রথমটি বদলান; ইতিহাসেই কিছু রেখে দিতে চাইলে দ্বিতীয়টি।

///

/// note | Deprecated: `before_model_request`-এ `request_context.messages`-এ সরাসরি যোগ করা

পেছনের সামঞ্জস্যের জন্য, `before_model_request` যে বার্তা `append`, `extend` বা `+=` দিয়ে `request_context.messages`-এ যোগ করে, সেগুলো এখনো `ctx.messages`-এর শেষেও যোগ হয়, একটি [`PydanticAIDeprecationWarning`][pydantic_ai.exceptions.PydanticAIDeprecationWarning]-সহ। সতর্কবার্তা ছাড়া একটি বার্তা দুই জায়গাতেই রাখতে, `request_context.messages`-এ একটি নতুন তালিকা assign করুন আর বার্তাটি `ctx.messages`-এ যোগ করুন।

///

[`ProcessHistory`][pydantic_ai.capabilities.ProcessHistory] আর compaction ইচ্ছাকৃতভাবে দুটোই হালনাগাদ করে, তাদের বিদ্যমান ইতিহাস-পুনর্লিখনের চুক্তি বজায় রেখে। যেহেতু একটি history processor বর্তমান রিকোয়েস্টের দৃশ্য রূপান্তর করে আর তার পুরো ফল স্থায়ী করে, অন্য বার্তা hook-এর তুলনায় এর অবস্থান গুরুত্বপূর্ণ থাকে।

/// warning | বার্তার অবজেক্ট তবুও ভাগাভাগি হতে পারে

[`ModelRequestContext.messages`][pydantic_ai.models.ModelRequestContext.messages] একটি স্বাধীন অগভীর (shallow) শীর্ষ-স্তরের তালিকা, স্বাধীন অবজেক্ট-গাছ নয়। ওপরের deprecated append ছাড়া, সেই বাইরের তালিকা বদলালে শুধু বর্তমান রিকোয়েস্টে প্রভাব পড়ে। রাখা বার্তা আর তাদের ভেতরের অংশ `ctx.messages`-এর বার্তার সাথে একই অবজেক্ট হতে পারে, তাই ভেতরের একটি বার্তা বা অংশ সরাসরি বদলালে স্থায়ী ইতিহাস আর পরের রিকোয়েস্টও বদলে যেতে পারে। তালিকার স্তরের নিচে একটি বিচ্ছিন্ন পরিবর্তনের জন্য, যে স্তর বদলাচ্ছেন সে পর্যন্ত বদলি বার্তা আর অংশ তৈরি করুন, যেমন [`dataclasses.replace`](https://docs.python.org/3/library/dataclasses.html#dataclasses.replace) দিয়ে।

///

মডেল কল পুরোপুরি বাদ দিতে, `before_model_request` বা `model_request` (wrap) থেকে [`SkipModelRequest(response)`][pydantic_ai.exceptions.SkipModelRequest] তুলুন।

/// note | মনে রাখুন

প্রতিটি মডেল-রিকোয়েস্ট জীবনচক্র **প্রতি মডেল দফায় একবার** চলে, এমনকি একটি provider দফার মাঝে থেমে গেলেও (Anthropic `pause_turn`) বা একটি background উত্তর ফেরত দিলেও (OpenAI background mode) আর এজেন্ট নিঃশব্দে তা চালিয়ে গেলেও। `wrap_model_request` সবচেয়ে বাইরের স্তর: এর handler চালায় `before_model_request`, যেকোনো ধারাবাহিকতাসহ পুরো দফা, আর তারপর `after_model_request`, যা একক সম্পূর্ণ [`ModelResponse`][pydantic_ai.messages.ModelResponse] পায়।

একটি রান যখন [`message_history`](message-history.md) থেকে একটি স্থগিত দফা আবার শুরু করে, `before_model_request` আর `wrap_model_request` সেই স্থগিত [`ModelResponse`][pydantic_ai.messages.ModelResponse]-কে `request_context.messages`-এর শেষ এন্ট্রি হিসেবে দেখে: এটি সেই ধারাবাহিকতার বীজ যা provider-কে ফেরত পাঠানো হবে, তারে আসলে যা যায় তারই প্রতিফলন।

///

/// note | stream করা মডেল রিকোয়েস্টে context variable

[`run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream]-এ, একটি async `before_model_request` hook-এর সেট করা context-variable মান পরের টুল, আউটপুট আর রান hook-এ পাওয়া যায়, stream নয় এমন রানের মতোই। সেই মডেল রিকোয়েস্টে পরে সেট করা মান (যেমন, একটি wrapper-এর handler ফেরত আসার পরে) না-ও পাওয়া যেতে পারে। পুরো রানজুড়ে ভাগ করতে হবে এমন অবস্থার জন্য পরিবর্তনযোগ্য [dependencies](dependencies.md) ব্যবহার করুন।

///

### টুল যাচাইয়ের hook { #tool-validation-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_tool_validate` | `before_tool_validate=` | `before_tool_validate` |
| `after_tool_validate` | `after_tool_validate=` | `after_tool_validate` |
| `tool_validate` | `tool_validate=` | `wrap_tool_validate` |
| `tool_validate_error` | `tool_validate_error=` | `on_tool_validate_error` |

মডেলের JSON আর্গুমেন্ট পার্স আর যাচাই হওয়ার সময় যাচাইয়ের hook চলে। সব টুল hook `call` ([`ToolCallPart`][pydantic_ai.messages.ToolCallPart]) আর `tool_def` ([`ToolDefinition`][pydantic_ai.tools.ToolDefinition]) প্যারামিটার পায়।

/// note | মনে রাখুন

টুল যাচাই আর চালানোর hook শুধু ফাংশন টুলে চলে। ভেতরের আউটপুট টুল (গোছানো আউটপুট দিতে ব্যবহৃত) ব্যবহারকারীর সামনে আসে না, আর বাদ পড়ে।

///

যাচাই বাদ দিতে, `before_tool_validate` বা `tool_validate` (wrap) থেকে [`SkipToolValidation(args)`][pydantic_ai.exceptions.SkipToolValidation] তুলুন।

একটি টুল কল শুধু তার আর্গুমেন্ট যাচাই হওয়ার পরেই [deferred](deferred-tools.md) করা যায়, কারণ যে deferral মীমাংসা করবে তাকে সেই আর্গুমেন্ট দেখানো হয়। তাই [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] আর [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] তোলা যায় `after_tool_validate` থেকে (আর `tool_validate` থেকে তার `handler()` ফেরত আসার পরে), কিন্তু `before_tool_validate` থেকে, `handler()` ডাকার আগে `tool_validate` থেকে, বা `tool_validate_error` থেকে তুললে তা একটি [`UserError`][pydantic_ai.exceptions.UserError]। একটি টুলের [`args_validator`](tools-advanced.md#args-validator) থেকে আসা deferral ততক্ষণ আটকে রাখা হয়, যতক্ষণ না `after_tool_validate` যাচাই হওয়া আর্গুমেন্ট পরীক্ষা করে; handler ফেরত আসার পরে `tool_validate`-এর তোলা deferral সেই দরজা পেরোনোর পরে ঘটে।

### টুল চালানোর hook { #tool-execution-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_tool_execute` | `before_tool_execute=` | `before_tool_execute` |
| `after_tool_execute` | `after_tool_execute=` | `after_tool_execute` |
| `tool_execute` | `tool_execute=` | `wrap_tool_execute` |
| `tool_execute_error` | `tool_execute_error=` | `on_tool_execute_error` |

টুল ফাংশন চলার সময় চালানোর hook চলে। `args` সবসময় যাচাই হওয়া `dict[str, Any]`।

চালানো বাদ দিতে, `before_tool_execute` বা `tool_execute` (wrap) থেকে [`SkipToolExecution(result)`][pydantic_ai.exceptions.SkipToolExecution] তুলুন।

প্রতিটি চালানোর hook কলটি [defer](deferred-tools.md) করতে পারে — এই সময়ে আর্গুমেন্ট যাচাই হয়ে গেছে — তবে `ApprovalRequired`/`CallDeferred` তুলুন `before_tool_execute` থেকে (বা `handler()` ডাকার আগে `tool_execute` থেকে)। `after_tool_execute` থেকে, বা `handler()` ফেরত আসার পরে `tool_execute` থেকে deferral গ্রহণ করা হয়, কিন্তু কাজে আসার জন্য তা অনেক দেরিতে ঘটে: টুল ফাংশন আগেই চলেছে, তাই তার পার্শ্বপ্রতিক্রিয়া ঘটে গেছে আর তার ফল বাদ পড়ে।

/// warning | সাধারণ ভুল

"টাকা পাঠানোর আগে অনুমোদন নাও" নিয়ম `after_tool_execute`-এ বসালে টাকা আগেই চলে যাবে! অনুমোদন বা বাধা দেওয়ার যেকোনো নিয়ম `before_tool_execute`-এ (বা `handler()` ডাকার আগে) রাখুন।

///

### আউটপুট যাচাইয়ের hook { #output-validation-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_output_validate` | `before_output_validate=` | `before_output_validate` |
| `after_output_validate` | `after_output_validate=` | `after_output_validate` |
| `output_validate` | `output_validate=` | `wrap_output_validate` |
| `output_validate_error` | `output_validate_error=` | `on_output_validate_error` |

গোছানো আউটপুট আউটপুট schema অনুযায়ী পার্স হওয়ার সময় আউটপুট যাচাইয়ের hook চলে। সাধারণ লেখা বা ছবির আউটপুটে এগুলো চলে **না**। সব আউটপুট hook একটি `output_context` ([`OutputContext`][pydantic_ai.capabilities.OutputContext]) প্যারামিটার পায়।

/// note | মনে রাখুন

stream করার সময়, আউটপুট **যাচাইয়ের** hook প্রতিটি আংশিক যাচাইয়ের চেষ্টায় আর চূড়ান্ত ফলে চলে। আউটপুট **প্রক্রিয়াকরণের** hook শুধু আংশিক যাচাই সফল হলে, আর চূড়ান্ত ফলে চলে। আংশিক আর চূড়ান্ত ফল আলাদা করতে আর আংশিকে ব্যয়বহুল কাজ এড়াতে আপনার hook-এ `ctx.partial_output` পরীক্ষা করুন।

///

### আউটপুট প্রক্রিয়াকরণের hook { #output-processing-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `before_output_process` | `before_output_process=` | `before_output_process` |
| `after_output_process` | `after_output_process=` | `after_output_process` |
| `output_process` | `output_process=` | `wrap_output_process` |
| `output_process_error` | `output_process_error=` | `on_output_process_error` |

আউটপুট প্রক্রিয়া হওয়ার সময় আউটপুট প্রক্রিয়াকরণের hook চলে — মান বের করা, আউটপুট ফাংশন ডাকা, আর আউটপুট validator চালানো।

পুরো জীবনচক্র, signature, আর আউটপুট validator কীভাবে প্রক্রিয়াকরণের hook-এর সাথে কাজ করে তার বিস্তারিত জানতে দেখুন [Output hooks](capabilities/custom.md#output-hooks)।

### টুল প্রস্তুতি { #tool-preparation }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `prepare_tools` | `prepare_tools=` | `prepare_tools` |
| `prepare_output_tools` | `prepare_output_tools=` | `prepare_output_tools` |

প্রতিটি ধাপে মডেল যে টুলের সংজ্ঞা দেখে তা ছাঁকে বা বদলায়।

`prepare_tools` **ফাংশন** টুল সামলায়; `prepare_output_tools` [আউটপুট টুল][pydantic_ai.output.ToolOutput] আলাদাভাবে সামলায়, যেখানে `ctx.max_retries` **আউটপুট** আবার-চেষ্টার বাজেট দেখায়। দুটোই `PreparedToolset` wrapper হিসেবে চলে — ফল মডেলের রিকোয়েস্টে *আর* `ToolManager.tools`-এ যায়, তাই ছাঁকলে টুল চালানোও আটকে যায়।

### Deferred টুল কল hook { #deferred-tool-call-hook }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `deferred_tool_calls` | `deferred_tool_calls=` | `handle_deferred_tool_calls` |

একটি রানের মধ্যেই [deferred টুল কল](deferred-tools.md) (অনুমোদন-প্রয়োজন বা বাইরে-চালানো) মীমাংসা করে। hook-টি একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] পায় আর একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] ফেরত দেয় (বা প্রত্যাখ্যান করতে `None`)। একাধিক নথিভুক্ত hook জমা হয়: প্রতিটি এখনো মীমাংসা না হওয়া রিকোয়েস্টগুলো পায় আর কিছু বা সবগুলো মীমাংসা করতে পারে।

```python title="hooks_deferred_tool_calls.py"
from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()


@hooks.on.deferred_tool_calls
async def auto_approve(
    ctx: RunContext, *, requests: DeferredToolRequests
) -> DeferredToolResults:
    return requests.build_results(approve_all=True)


agent = Agent('test', capabilities=[hooks])


@agent.tool_plain(requires_approval=True)
def delete_file(path: str) -> str:
    return f'File {path!r} deleted'
```

অন্য hook ছাড়া শুধু অ্যাপ্লিকেশন-স্তরের handler নথিভুক্তির জন্য, বিশেষ [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] capability আরও সংক্ষিপ্ত — দেখুন [Resolving deferred calls with a handler](deferred-tools.md#resolving-deferred-calls-with-a-handler)।

### Event stream hook { #event-stream-hooks }

| `hooks.on.` | Constructor kwarg | `AbstractCapability` মেথড |
|---|---|---|
| `run_event_stream` | `run_event_stream=` | `wrap_run_event_stream` |
| `event` | `event=` | _(প্রতি-event-এর সুবিধা)_ |

`run_event_stream` পুরো event stream-কে একটি async generator হিসেবে মুড়ে রাখে। `event` প্রতিটি আলাদা event দেখে, capability-র [`on_event`][pydantic_ai.capabilities.on_event] listener-এর একই পাঠানোর জায়গায়। callback sync বা async হতে পারে আর `None` ফেরত দেয়।

এই stream দিয়ে টুল আর মডেলের event যায়, সাথে framework-এর event যেমন [`EnqueuedMessagesEvent`][pydantic_ai.messages.EnqueuedMessagesEvent], যখন [`ctx.enqueue()`][pydantic_ai.tools.RunContext.enqueue] দিয়ে [রানের মাঝে ঢোকানো](message-history.md#injecting-messages-mid-run) বার্তা রানের ইতিহাসে ঢোকে, অ্যাপ্লিকেশনের [custom event](agent.md#custom-events), আর capability-দের প্রকাশ করা [capability event](capabilities/overview.md#capability-events)। যেহেতু একটি `event` callback কোনো capability-র নয়, অ্যাপ্লিকেশনের, তাই এটি আপনার নিজের একটি [`CustomEvent`][pydantic_ai.messages.CustomEvent] [emit](agent.md#custom-events) করারও জায়গা, আর এভাবেই একটি [capability-র ভেতরের event আবার প্রকাশ](capabilities/overview.md#capability-events) করে frontend-এ পাঠানো যায়। একটি `event` callback [সাথে সাথে পাঠানো](capabilities/overview.md#reacting-to-events) capability-র সিদ্ধান্ত-event-এও অংশ নেয়, তাই emitter এগোনোর আগে অ্যাপ্লিকেশনের কোড সিদ্ধান্তের ফিল্ড সেট করতে পারে। একটি [realtime session](realtime/capabilities.md)-এর সময় দুটো hook-ই চলে, আর শুধু-realtime [`RealtimeSessionEvent`][pydantic_ai.messages.RealtimeSessionEvent] সদস্যরাও একই stream দিয়ে যায়।

callback ছাঁকতে event ক্লাসগুলো দিন:

```python title="hooks_event.py"
from pydantic_ai import Agent, PartStartEvent, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()
event_count = 0


@hooks.on.event(PartStartEvent)
async def count_events(ctx: RunContext, event: PartStartEvent) -> None:
    global event_count
    event_count += 1


agent = Agent('test', capabilities=[hooks])
```

অথবা প্রতিটি event দেখতে খালি ব্যবহার করুন, তখন `event`-এর টাইপ হয় পুরো [`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent] union:

```python title="hooks_event_bare.py"
from pydantic_ai import Agent, AgentStreamEvent, RunContext
from pydantic_ai.capabilities import Hooks

hooks = Hooks()
event_log: list[str] = []


@hooks.on.event
async def log_events(ctx: RunContext, event: AgentStreamEvent) -> None:
    event_log.append(event.event_kind)


agent = Agent('test', capabilities=[hooks])
```

ক্লাসগুলোর নাম দেওয়াই ভালো। টাইপ দিয়ে ছাঁকা শুধু type checker-এর জন্য `event` আর্গুমেন্ট সরু করার ব্যাপার নয়: ক্লাসগুলোই পাঠানোর ব্যবস্থাকে সেই capability পুরোপুরি এড়িয়ে যেতে দেয় যেসব event-এ সে শোনে না, তাই অনেক capability-র একটি রানে গাছের যেকোনো জায়গায় একটি খালি callback মানে প্রতিটি event সবার কাছে পাঠানো হবে।

`hooks.on.event` থেকে একটি বদলি event ফেরত দেওয়া deprecated। event রূপান্তর, বদল বা ছাঁকতে `hooks.on.run_event_stream` ব্যবহার করুন।

#### `Hooks` capability ছাড়া শোনা { #listening-without-a-hooks-capability }

শুধু event দেখতে চাইলে, [`@agent.on_event`][pydantic_ai.agent.Agent.on_event] সরাসরি এজেন্টে একটি listener নথিভুক্ত করে, একই ছাঁকা, টাইপিং আর `timeout=`-সহ:

```python title="agent_on_event.py"
from pydantic_ai import Agent, FunctionToolCallEvent, RunContext

agent = Agent('test')
called_tools: list[str] = []


@agent.on_event(FunctionToolCallEvent)
async def track_tools(ctx: RunContext, event: FunctionToolCallEvent) -> None:
    called_tools.append(event.part.tool_name)
```

খালি ব্যবহারও একইভাবে কাজ করে: শুধু `@agent.on_event` প্রতিটি event দেখে।

এজেন্টে নথিভুক্ত listener এজেন্টের নিজের capability-দের পরে যোগ হয়, তাই সেগুলোর emit করা event তারা দেখে, আর একটি override করা root capability-র পরেও টিকে থাকে। capability-র ক্রম তবুও প্রযোজ্য: যে `position='innermost'` চায় সে সেই অবস্থান রাখে আর তার listener এগুলোর পরে চলে। যে এজেন্ট কখনো `on_event` ডাকে না, তার কোনো প্রভাব নেই: কিছু নথিভুক্ত না থাকলে listener capability রানে যোগই হয় না।

`hooks.on.event`-এর মতো, এগুলো `run_event_stream`-এর *আগে* (upstream) পাঠানো হয়: একটি listener প্রতিটি event দেখে যেমন emit হয়েছে, শেষে যেমন পৌঁছায় তেমন নয়, তাই যে capability তার stream wrapper-এ event নতুন করে লেখে বা বাদ দেয়, সে তা করে প্রতিটি listener চলার পরে — আর একটি listener এমন event দেখতে পারে যা কোনো গ্রাহক কখনো পায় না। পৌঁছানো stream দরকার হলে, সেটি `run_event_stream` দিয়ে মুড়ুন বা [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] ব্যবহার করুন।

এভাবে শুধু event নথিভুক্ত করা যায়। অন্য hook পরিবারগুলো interceptor — এরা একটি wrap শৃঙ্খলে বসে, মান নেয় আর ফেরত দেয়, আর অন্য capability-র তুলনায় এরা কোথায় বসবে তা আপনাকেই ঠিক করতে হয় — তাই এগুলো যায় একটি `Hooks` capability-তে, যার `capabilities=`-এ অবস্থান আপনি বেছে নেন।

## টুল hook ছাঁকা { #tool-hook-filtering }

টুল hook (যাচাই আর চালানো) নির্দিষ্ট টুলকে নাম দিয়ে লক্ষ্য করতে একটি `tools` প্যারামিটার সমর্থন করে:

```python title="hooks_tool_filter.py"
from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.capabilities import Hooks, ValidatedToolArgs
from pydantic_ai.messages import ToolCallPart

hooks = Hooks()
call_log: list[str] = []


@hooks.on.before_tool_execute(tools=['send_email'])
async def audit_dangerous_tools(
    ctx: RunContext,
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: ValidatedToolArgs,
) -> ValidatedToolArgs:
    call_log.append(f'audit: {call.tool_name}')
    return args


agent = Agent('test', capabilities=[hooks])


@agent.tool_plain
def send_email(to: str) -> str:
    return f'sent to {to}'


result = agent.run_sync('Send an email to test@example.com')
print(call_log)
#> ['audit: send_email']
```

`tools` প্যারামিটার টুলের নামের একটি ক্রম নেয়। hook শুধু মেলা টুলে চলে — অন্য টুল কল প্রভাবিত না হয়ে পেরিয়ে যায়।

## Timeout { #timeouts }

প্রতিটি hook সেকেন্ডে একটি ঐচ্ছিক `timeout` সমর্থন করে। hook timeout পেরোলে একটি [`HookTimeoutError`][pydantic_ai.capabilities.HookTimeoutError] ওঠে:

```python title="hooks_timeout.py"
import asyncio

from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks, HookTimeoutError

hooks = Hooks()


@hooks.on.before_model_request(timeout=0.01)
async def slow_hook(
    ctx: RunContext, request_context: ModelRequestContext
) -> ModelRequestContext:
    await asyncio.sleep(10)  # Will be interrupted by timeout
    return request_context  # pragma: no cover


agent = Agent('test', capabilities=[hooks])
try:
    agent.run_sync('Hello')
except HookTimeoutError as e:
    print(f'Hook timed out: {e.hook_name} after {e.timeout}s')
    #> Hook timed out: before_model_request after 0.01s
```

Timeout সেট করা হয় decorator প্যারামিটার দিয়ে (`@hooks.on.before_model_request(timeout=5.0)`) বা kwargs ব্যবহার করলে constructor দিয়ে।

## Wrap hook { #wrap-hooks }

Wrap hook একটি পর্যায়ের সবচেয়ে বাইরের স্তর, তাই এরা পুরো জীবনচক্রকে প্রস্তুতি আর শেষ-পরিষ্কারের লজিক দিয়ে ঘিরে রাখতে পারে। দেওয়া `handler` ডাকলে `before_*` শৃঙ্খল, `on_*_error` উদ্ধারসহ মূল কাজ, আর `after_*` শৃঙ্খল চলে। handler না ডেকে ফেরত এলে সেই ভেতরের জীবনচক্র বাদ পড়ে।

একটি শর্টকাট-নেওয়া wrapper `before_*`-এর নীতি-hook-ও বাদ দেয়। বাধ্যতামূলক অনুমোদন একটি বাইরের wrapper-এ রাখুন, বা শর্টকাট নেওয়া যায় এমন যেকোনো cache-এর বাইরে রাখুন।

`hooks.on` namespace-এ, wrap hook `wrap_` উপসর্গ বাদ দেয় — `hooks.on.model_request` মানে `wrap_model_request`:

```python title="hooks_wrap.py"
from pydantic_ai import Agent, ModelRequestContext, RunContext
from pydantic_ai.capabilities import Hooks, WrapModelRequestHandler
from pydantic_ai.messages import ModelResponse

hooks = Hooks()
wrap_log: list[str] = []


@hooks.on.model_request
async def log_request(
    ctx: RunContext, *, request_context: ModelRequestContext, handler: WrapModelRequestHandler
) -> ModelResponse:
    wrap_log.append('before')
    response = await handler(request_context)
    wrap_log.append('after')
    return response


agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello!')
print(wrap_log)
#> ['before', 'after']
```

/// tip | উদাহরণ দিয়ে বুঝি

Wrap hook হলো একটি স্যান্ডউইচের দুই পিঠ রুটি: `handler()` ডাকার আগে উপরের রুটি (যেমন টাইমার চালু), পরে নিচের রুটি (টাইমার বন্ধ, সময় লগ)। আর যদি `handler()` না-ই ডাকেন (যেমন cache-এ উত্তর পেয়ে গেলেন), তাহলে ভেতরের পুরো পুর (মডেল কল) বাদ — এভাবেই cache বা মক বানানো যায়।

///

## Hook-এর ক্রম { #hook-ordering }

প্রতিটি পর্যায়ে, `wrap_*` hook [hook জীবনচক্রের](#hook-lifecycle) বাকিটা ঘিরে রাখে।

একটি একক [`Hooks`][pydantic_ai.capabilities.Hooks] instance-এর মধ্যে, `before_*`, `after_*` আর `on_*_error` ফাংশন **নথিভুক্তির ক্রমে** চলে (যে ক্রমে সংজ্ঞায়িত বা constructor-এ দেওয়া হয়েছে)। নথিভুক্ত `wrap_*` ফাংশন middleware হিসেবে একটির ভেতরে আরেকটি বসে, প্রথম নথিভুক্ত wrapper সবচেয়ে বাইরে।

একাধিক capability-জুড়ে, [composition-এর নিয়ম](capabilities/custom.md#composition-and-middleware-semantics) প্রযোজ্য: `before_*` capability-র ক্রমে চলে, `after_*` আর `on_*_error` উল্টো capability-ক্রমে চলে, আর `wrap_*` প্রথম capability-কে সবচেয়ে বাইরে রেখে একটির ভেতরে আরেকটি বসে। এই পরিবারগুলো capability ধরে ধরে মেশে না: যেকোনো `before_*` hook-এর আগে সব wrapper-এ ঢোকা হয়, তাই সবচেয়ে ভেতরের capability-র wrapper-ও সবচেয়ে বাইরের capability-র `before_*` hook-এর আগে চলে।

| capability-র ক্রম `[A, B]` | চলার ক্রম |
| --- | --- |
| `wrap_*` | A-র wrap ঢোকে → B-র wrap ঢোকে → ... → B বেরোয় → A বেরোয় |
| `before_*` | A, তারপর B |
| `after_*` আর `on_*_error` | B, তারপর A |

Hook-এর সময় [`RunContext`][pydantic_ai.tools.RunContext]-এ কী ভরা থাকে তাতেও প্রভাব ফেলে। শুরুর দিকের রান আর node hook বর্তমান ধাপের tool manager আর মডেল রিকোয়েস্ট প্যারামিটার জোড়া লাগার আগেই চলতে পারে। সেই সময়ে `ctx.available_tool_names`-এ তবুও ইতিহাস থেকে পুনর্গঠিত tool-search-এর আবিষ্কার থাকতে পারে, কিন্তু `ctx.tools` আর বর্তমান রিকোয়েস্ট প্যারামিটার খালি থাকতে পারে বা আগের ধাপের অবস্থা দেখাতে পারে। `before_model_request` আর পরের মডেল-রিকোয়েস্ট hook পাঠানোর ঠিক আগের রিকোয়েস্টটি দেখে, বর্তমান ফাংশন টুল, নেটিভ টুল আর মডেল সেটিংসহ। টুল আর আউটপুট hook বর্তমানে প্রক্রিয়াধীন কল বা আউটপুটের অবস্থা দেখে।

চাহিদামতো capability-র জন্য, `ctx.loaded_capability_ids` প্রতিটি মডেল রিকোয়েস্টের আগে বার্তার ইতিহাস থেকে বের করা হয়, তাই একটি ধাপের মধ্যে লোড হওয়া capability দেখা দেয় *পরের* ধাপ থেকে — একই ধাপ যেখানে প্রথম তার নির্দেশনা মডেলের কাছে যায়, আর তাই প্রথম যেখানে তার টুল ডাকা যায়। লোড হওয়া capability-র ফাংশন টুল, নেটিভ টুল আর মডেল সেটিংও সেই রিকোয়েস্টে দেখা দেয়, আর তখন থেকে যেসব hook point আসে সেগুলোতে capability-র নিজের hook চলে। যে hook একটি capability-কে ঠিক যে দফায় লোড হয়েছে সেই দফাতেই খোঁজে, সে তাকে পাবে না।

## Error hook { #error-hooks }

Error hook (`hooks.on` namespace-এ `*_error`, `AbstractCapability`-তে `on_*_error`) **"raise করলে ছড়ায়, return করলে উদ্ধার"** নিয়ম মানে:

- **মূল এররটিই raise করুন** — অপরিবর্তিত ছড়িয়ে পড়ে *(ডিফল্ট)*
- **একটি ভিন্ন exception raise করুন** — এররটি রূপান্তরিত হয়
- **একটি ফল return করুন** — এররটি চাপা পড়ে

এগুলো মূল কাজের ব্যর্থতার চারপাশে চলে, মোড়ানো handler-এর ভেতরে। তাই উদ্ধার ঘটে `wrap_*` শৃঙ্খল দিয়ে নিয়ন্ত্রণ ফেরার আগেই: wrapper উদ্ধার হওয়া ফল দেখে, আর শুধু উদ্ধার না হওয়া ব্যর্থতাই তাদের মধ্য দিয়ে বাইরে ছড়ায়। `before_*`, `after_*` বা `wrap_*` থেকে আসা exception সংশ্লিষ্ট error hook-এর আওতার বাইরে।

পুরো ধরন আর উদ্ধারের টাইপের জন্য দেখুন [Error hooks](capabilities/custom.md#error-hooks)।

## `ModelRetry` দিয়ে আবার চেষ্টা আর `ToolFailed` দিয়ে ব্যর্থতা জানানো { #triggering-retries-with-modelretry }

একটি নিজের বার্তাসহ মডেলকে আবার চেষ্টা করতে বলতে hook [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে — [টুল ফাংশন](tools-advanced.md#tool-retries) আর আউটপুট validator-এ ব্যবহৃত একই exception। `ModelRetry` মানে সবসময় "মডেলকে আবার জিজ্ঞেস করো": বদলে একটি hook থেকে রান বাতিল করতে, অন্য যেকোনো exception তুলুন, আর তা caller পর্যন্ত ছড়িয়ে যাবে।

**মডেল রিকোয়েস্ট hook** (`before_model_request`, `after_model_request`, `wrap_model_request`, `on_model_request_error`):

- আবার-চেষ্টার বার্তা মডেলের কাছে একটি [`RetryFeedbackPart`][pydantic_ai.messages.RetryFeedbackPart] হিসেবে ফেরত যায়, ব্যবহারকারীর নয়, Pydantic AI-এর নিজের কণ্ঠে — দেখুন [Feedback that belongs to no tool call](retries.md#feedback-that-belongs-to-no-tool-call)
- `before_model_request`: কোনো উত্তর সংরক্ষিত হয় না, কারণ মডেল ডাকা হয়নি। পরের রিকোয়েস্ট বিদ্যমান ইতিহাসে আবার-চেষ্টার বার্তা যোগ করে, আর তার জন্য `before_model_request` hook আবার চলে, তাই যে hook সবসময় raise করে সে আবার-চেষ্টার বাজেট শেষ করে ফেলে
- `after_model_request`: মূল উত্তরটি বার্তার ইতিহাসে রাখা হয়, যাতে মডেল দেখতে পারে সে কী বলেছিল
- `wrap_model_request`: উত্তর রাখা হয় শুধু handler ডাকা হলে
- আবার-চেষ্টাগুলো এজেন্টের আবার-চেষ্টার বাজেটের আউটপুট দিক থেকে গোনা হয়
- [`run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] চূড়ান্ত আউটপুট হিসেবে আগেই stream করা একটি উত্তর আবার চেষ্টা করতে পারে না, তাই সেটিকে বাতিল করা একটি `ModelRetry` `async with` ব্লক থেকে বেরোনোর সময় [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] তোলে। [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] আর [`iter()`][pydantic_ai.agent.Agent.iter] এটি আবার চেষ্টা করে

**টুল hook** (`before/after_tool_validate`, `wrap_tool_validate`, `on_tool_validate_error`, `before/after_tool_execute`, `wrap_tool_execute`, `on_tool_execute_error`):

- আবার-চেষ্টা করা টুল ফলে রূপান্তরিত হয়, ঠিক যেমন একটি টুল ফাংশন `ModelRetry` তুললে হয়
- আবার-চেষ্টাগুলো টুলের `max_retries` সীমা থেকে গোনা হয়

**আউটপুট hook** (`before/after_output_validate`, `wrap_output_validate`, `on_output_validate_error`, `before/after_output_process`, `wrap_output_process`, `on_output_process_error`):

- আবার-চেষ্টায় রূপান্তরিত হয়, ঠিক যেমন একটি আউটপুট ফাংশন `ModelRetry` তুললে হয়
- টুল আউটপুটে, আবার-চেষ্টাগুলো টুলের `max_retries` সীমা থেকে গোনা হয়
- লেখার আউটপুটে, আবার-চেষ্টাগুলো এজেন্টের আবার-চেষ্টার বাজেটের আউটপুট দিক থেকে গোনা হয়

একটি `on_*_error` hook শুধু তার পর্যায়ের মূল কাজ ঢাকে। তাই একটি `before_*`, `after_*` বা `wrap_*` hook-এর তোলা [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] একে পাশ কাটায়। একটি মূল কাজ থেকে, `ModelRetry` `on_tool_validate_error` আর `on_output_validate_error`-এ পাঠানো হয়, কিন্তু নিয়ন্ত্রণ-প্রবাহ হিসেবে `on_model_request_error`, `on_tool_execute_error` আর `on_output_process_error` পাশ কাটায়।

[`ToolFailed`][pydantic_ai.exceptions.ToolFailed] টুল-যাচাই আর টুল-চালানোর error hook পাশ কাটায়। মূল মডেল কল বা মূল আউটপুট প্রক্রিয়াকরণ থেকে এটি একটি সাধারণ exception, যা `on_model_request_error` বা `on_output_process_error`-এ পাঠানো হয়; একটি `before_*`, `after_*` বা `wrap_*` hook তুললে, এটি সংশ্লিষ্ট error hook-এর আওতার বাইরে।

টুল যাচাই আর চালানোর hook টুলের আবার-চেষ্টার বাজেট খরচ না করে একটি ব্যর্থ টুল ফল জানাতে [`ToolFailed`][pydantic_ai.exceptions.ToolFailed]-ও তুলতে পারে। এর মডেলের কাছে দৃশ্যমান ফল আর আবার-চেষ্টার বাজেটের আচরণ টুল ফাংশন নিজে `ToolFailed` তোলার মতোই, আর এটি কাজে লাগে যখন একটি error hook একটি third-party exception-কে মডেল দেখতে পারে এমন একটি ব্যর্থতায় রূপান্তর করে।

```python title="hooks_model_retry.py"
from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.exceptions import ModelRetry
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models import ModelRequestContext

hooks = Hooks()


@hooks.on.after_model_request
async def check_response(
    ctx: RunContext,
    *,
    request_context: ModelRequestContext,
    response: ModelResponse,
) -> ModelResponse:
    if 'PLACEHOLDER' in str(response.parts):
        raise ModelRetry('Response contains placeholder text. Please provide real data.')
    return response


agent = Agent('test', capabilities=[hooks])
result = agent.run_sync('Hello')
print(result.output)
#> success (no tool calls)
```

ডিফল্টভাবে, একটি টুলের ভেতরে তোলা `ModelRetry` বা `ToolFailed` ছাড়া অন্য যেকোনো exception
টুলের সীমানা পেরিয়ে পুরো রান বাতিল করে। একটি টুল-চালানোর hook আপনাকে এগুলো এক জায়গায় ধরতে দেয়
— প্রতিটি টুল না বদলেই — আর বেছে নিতে দেয় প্রতিটি মডেলের কাছে কীভাবে দেখা দেবে। পার্থক্যটি
[আবার চেষ্টা চাওয়া](tools-advanced.md#tool-retries) আর
[ব্যর্থতা জানানো](tools-advanced.md#tool-failed)-র অর্থগত পার্থক্য:

- **সাময়িক** এররে `ModelRetry` তুলুন, যেখানে একই কল আবার চেষ্টা করলে সফল হতে পারে;
- **নিশ্চিত** ব্যর্থতায় `ToolFailed` তুলুন, যেখানে আবার চেষ্টায় লাভ নেই আর মডেলের উচিত
  ফলটি দেখে মানিয়ে নেওয়া (অন্য পদ্ধতি বাছা, ব্যবহারকারীকে জানানো ইত্যাদি)।

নিচের hook একটি upstream status code দেখে সেই সিদ্ধান্ত নেয় — MCP-র [`tool_error_behavior`](mcp/client.md#tool-errors) সেটিংয়ের প্রতি-এররের সংস্করণ:

```python title="hooks_convert_tool_errors.py"
from typing import Any

from pydantic_ai import Agent, RunContext, ToolCallPart, ToolDefinition, ToolReturnPart
from pydantic_ai.capabilities import Hooks
from pydantic_ai.exceptions import ModelRetry, ToolFailed
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import AgentInfo, FunctionModel


class UpstreamError(Exception):
    """Stand-in for an HTTP client error that carries the response status code."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


hooks = Hooks()


@hooks.on.tool_execute_error
async def convert_upstream_errors(
    ctx: RunContext,
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: dict[str, Any],
    error: Exception,
) -> Any:
    if isinstance(error, UpstreamError):
        if error.status_code >= 500 or error.status_code == 429:
            # Transient: the same call might succeed, so ask the model to try again.
            raise ModelRetry(f'Upstream returned {error.status_code}, please try again.')
        # Definitive (e.g. 404, 403): retrying won't help — report it so the model can adapt.
        raise ToolFailed(f'Upstream returned {error.status_code}: {error}')
    raise error  # unrelated errors still abort the run


def model_fn(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    last_part = messages[-1].parts[-1]
    if isinstance(last_part, ToolReturnPart):
        return ModelResponse(parts=[TextPart(f'Could not fetch the document ({last_part.content}).')])
    return ModelResponse(parts=[ToolCallPart('get_document', {'doc_id': 42}, tool_call_id='call-1')])


agent = Agent(FunctionModel(model_fn), capabilities=[hooks])


@agent.tool_plain
def get_document(doc_id: int) -> str:
    raise UpstreamError(404, f'document {doc_id} not found')


result = agent.run_sync('Fetch document 42')
print(result.output)
#> Could not fetch the document (Upstream returned 404: document 42 not found).
```

যেহেতু ব্যর্থতাটি `ModelRetry` নয়, `ToolFailed` হিসেবে তোলা হয়েছে, মডেল এটি `outcome='failed'`-সহ একটি
[`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] হিসেবে পায় আর পরে কী
করবে তা ঠিক করে, সফল হতে পারবে না এমন একটি কলে একটি আবার-চেষ্টা নষ্ট না করে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি আবহাওয়া API 503 ("এখন ব্যস্ত") দিলে — `ModelRetry`: "আরেকবার চেষ্টা করো"। 404 ("এই শহর নেই") দিলে — `ToolFailed`: আবার চেষ্টা বৃথা, মডেল বরং ব্যবহারকারীকে বলুক শহরের নাম ঠিক করতে। এই বাছাই প্রতিটি টুলে আলাদা করে না লিখে একটি `tool_execute_error` hook-এ একবারই লেখা যায়।

///

## কখন `Hooks` আর কখন `AbstractCapability` { #when-to-use-hooks-vs-abstractcapability }

| [`Hooks`][pydantic_ai.capabilities.Hooks] ব্যবহার করুন | [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] ব্যবহার করুন |
|---|---|
| অ্যাপ্লিকেশন-স্তরের hook (লগিং, মেট্রিক্স) | পুনর্ব্যবহারযোগ্য, প্যাকেজ করা capability |
| দ্রুত এককালীন interceptor | টুল + hook + নির্দেশনা + সেটিং একসাথে |
| কোনো কনফিগারেশন-অবস্থা লাগে না | জটিল প্রতি-রান অবস্থা ব্যবস্থাপনা |
| এক-ফাইলের স্ক্রিপ্ট | একাধিক এজেন্টে ভাগ করা আচরণ |

/// check | সংক্ষেপে মনে রাখুন

* `hooks = Hooks()` বানিয়ে `@hooks.on.<নাম>` দিয়ে hook নথিভুক্ত করুন, তারপর `Agent(..., capabilities=[hooks])`।
* প্রতিটি পর্যায়: `wrap_*` → `before_*` → কাজ (`on_*_error`) → `after_*`; `handler()` না ডাকলে ভেতরের সব বাদ।
* পর্যায়গুলো: রান, node, মডেল রিকোয়েস্ট, টুল যাচাই, টুল চালানো, আউটপুট যাচাই, আউটপুট প্রক্রিয়া, event।
* টুল hook `tools=[...]` দিয়ে নির্দিষ্ট টুলে সীমিত করা যায়; প্রতিটি hook-এ `timeout=` দেওয়া যায়।
* Error hook: raise = ছড়াও, return = উদ্ধার। সাময়িক এররে `ModelRetry`, নিশ্চিত ব্যর্থতায় `ToolFailed`।
* sync hook আলাদা thread-এ চলে; `ContextVar`-এ লিখতে বা asyncio লাগলে async লিখুন।

///
