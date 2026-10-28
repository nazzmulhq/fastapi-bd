# Timeout (সময়সীমা) { #timeouts }

/// note | এই পেজে যা শিখবেন

* একটি রানের ভেতরের একটি ধাপ (মডেল রিকোয়েস্ট, টুল, hook, MCP) কতক্ষণ নিতে পারবে তা বেঁধে দেওয়া।
* `timeout` (প্রতি প্রচেষ্টা) বনাম `request_timeout` (পুরো রিকোয়েস্ট) — পার্থক্যটি কেন জরুরি।
* `run(timeout=...)` দিয়ে পুরো রানের সময়সীমা, আর `RunTimedOut`।
* একটি টুলের ভেতর থেকে রান থামানো: কোন exception তুললে কী হয়।

///

একটি রানের ভেতরে একটি ধাপ কতক্ষণ নিতে পারবে তা বাঁধা, পুরো রান বাঁধা, আর একটি টুলের ভেতর থেকে রান শেষ করা — এগুলোর উত্তর দেয় আলাদা ব্যবস্থা, আলাদা ব্যর্থতার ধরনসহ। এই পেজ সেগুলোর মানচিত্র। ইতিমধ্যে চলমান একটি রান থামাতে, দেখুন [Cancelling a Run](agent.md#cancelling-a-run)।

/// tip | উদাহরণ দিয়ে বুঝি

রান্নাঘরে কয়েকটি টাইমার ভাবুন: একটি প্রতিটি পদ চুলায় কতক্ষণ থাকবে (একটি ধাপ), একটি পুরো রাতের খাবার কখন টেবিলে আসতেই হবে (পুরো রান)। প্রতিটি পদের টাইমার ঠিক থাকলেও, দশটি পদ মিলে রাত গভীর হয়ে যেতে পারে — তাই দুই ধরনের টাইমারই দরকার।

///

## একটি ধাপ কতক্ষণ নেবে তা বাঁধা { #bounding-how-long-a-step-takes }

নিচের প্রতিটি নিয়ন্ত্রক একটি ভিন্ন কাজের একককে সীমিত করে।

| কী বাঁধতে চান | কীভাবে সেট করবেন | সময় পেরোলে কী হয় |
|---|---|---|
| একটি একক মডেল রিকোয়েস্টের প্রচেষ্টা — একটি provider SDK client-এর retry প্রতিটি প্রচেষ্টায় এটি আবার চালু করে | [`ModelSettings`][pydantic_ai.settings.ModelSettings]-এ `timeout` | [`ModelTimeoutError`][pydantic_ai.exceptions.ModelTimeoutError], একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError], যে মডেল ক্লাসগুলো [transport এরর ম্যাপ করে](models/overview.md#handling-model-api-errors) সেগুলোতে; একটি [`FallbackModel`](models/overview.md#fallback-model) বা একটি [transport retry](retries.md#transport-retries) না সামলালে রান ব্যর্থ হয় |
| একটি পুরো মডেল রিকোয়েস্ট — provider SDK আর transport-এর করা প্রতিটি প্রচেষ্টা, আর একটি stream করা উত্তর তার শেষ টুকরো পর্যন্ত পড়া | [`ModelSettings`][pydantic_ai.settings.ModelSettings]-এ `request_timeout` — দেখুন [Model request deadlines](#model-request-deadlines) | [`ModelRequestTimeout`][pydantic_ai.exceptions.ModelRequestTimeout], একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]; একটি [`FallbackModel`](models/overview.md#fallback-model) এতে fallback না করলে রান ব্যর্থ হয় |
| একটি ফাংশন টুল কল | `Agent(tool_timeout=...)`, বা একটি নির্দিষ্ট টুলে `timeout=` — দেখুন [Tool Timeout](tools-advanced.md#tool-timeout) | মডেল একটি retried টুল ফল পায় `'Timed out after N seconds.'`, যা সেই টুলের [retry বাজেট](retries.md#tool-retries) খরচ করে। একটি `def` টুল আসলে থামে না: সময়সীমা await-এর চারপাশে প্রয়োগ হয়, তাই worker thread শেষ পর্যন্ত চলে |
| একটি [hook](hooks.md) ফাংশন | `@hooks.on.*` decorator-এ `timeout=` | [`HookTimeoutError`][pydantic_ai.capabilities.HookTimeoutError], যা একটি [`AgentRunError`][pydantic_ai.exceptions.AgentRunError] আর রান বাতিল করে। একটি `def` টুলের মতো, একটি `def` hook আসলে থামে না: worker thread শেষ পর্যন্ত চলে |
| একটি MCP সার্ভারে সংযোগ | `MCPToolset(init_timeout=...)`, ডিফল্ট `5` সেকেন্ড | সংযোগ আর `initialize` handshake ব্যর্থ হয় |
| একটি একক MCP রিকোয়েস্ট | `MCPToolset(read_timeout=...)`, ডিফল্ট `300` সেকেন্ড | রিকোয়েস্ট ব্যর্থ হয়; ডিফল্ট [`tool_error_behavior='retry'`](mcp/client.md#tool-errors)-এ মডেল এটিকে retry-যোগ্য টুল এরর হিসেবে দেখে |
| একটি [realtime session](realtime/overview.md) খোলা | [`RealtimeModelSettings`][pydantic_ai.realtime.RealtimeModelSettings]-এ `handshake_timeout`, ডিফল্ট `30` সেকেন্ড — OpenAI, Azure OpenAI, xAI আর Gemini | session খোলার সময় [`RealtimeError`][pydantic_ai.realtime.RealtimeError] ওঠে। আবার সংযোগের সময় বদলে এটি একটি [`ReconnectPolicy`][pydantic_ai.realtime.ReconnectPolicy] প্রচেষ্টা খরচ করে |
| একটি রানের মোট কাজ | [`UsageLimits`][pydantic_ai.usage.UsageLimits] — রিকোয়েস্ট, টুল কল, token বা খরচ — দেখুন [Usage Limits](agent.md#usage-limits) | [`UsageLimitExceeded`][pydantic_ai.exceptions.UsageLimitExceeded] |
| একটি পুরো রানের ঘড়ি-সময় | যেকোনো রান মেথডে `timeout=` — দেখুন [Bounding a whole run](#bounding-a-whole-run) | [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut], রান যা শেষ করেছে তার সবকিছুসহ |

এগুলোর তিনটির ব্যাখ্যা দরকার:

- **`ModelSettings['timeout']` প্রতি মডেল ক্লাসে প্রয়োগ হয়, সর্বজনীনভাবে নয়।** যে মডেল ক্লাসগুলো এটি তাদের provider client-এ পাঠায় সেগুলো তালিকাভুক্ত আছে [`ModelSettings.timeout`][pydantic_ai.settings.ModelSettings.timeout]-এর নিচে; OpenAI-এর ওপর তৈরিগুলো পাঠানোটা উত্তরাধিকারসূত্রে পায় [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] / [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] থেকে। অন্য মডেল ক্লাস সেটিংটি উপেক্ষা করে, [`UnsupportedSettingWarning`][pydantic_ai.exceptions.UnsupportedSettingWarning] দিয়ে সতর্ক করে, আর বদলে তাদের যে HTTP client দিয়ে তৈরি করা হয়েছে তার timeout প্রযোজ্য হয়। Pydantic AI নিজে সেই client তৈরি করলে, ডিফল্ট হয় 600-সেকেন্ডের মোট timeout ([Google](models/google.md#long-decode)-এর জন্য 20 মিনিট), 5-সেকেন্ডের connect timeout-সহ। Google আর Mistral আরও একটি `httpx.Timeout` অবজেক্ট প্রত্যাখ্যান করে আর শুধু সেকেন্ডের একটি সংখ্যা নেয়।

    সেটিং উপেক্ষা করা একটি মডেল ক্লাসে একটি রিকোয়েস্ট বাঁধতে, সেই provider যেখানে আসলে timeout নেয় সেখানে কনফিগার করুন। বেশিরভাগ provider আপনার নিজের `http_client` নেয়, কিন্তু কয়েকটি নেয় না: [`XaiProvider`][pydantic_ai.providers.xai.XaiProvider] একটি client-স্তরের `timeout` নেয় (বা একটি আগে কনফিগার করা `xai_client`), [`BedrockProvider`][pydantic_ai.providers.bedrock.BedrockProvider] নেয় `aws_read_timeout` আর `aws_connect_timeout` (বা একটি আগে কনফিগার করা `bedrock_client`), আর [`HuggingFaceProvider`][pydantic_ai.providers.huggingface.HuggingFaceProvider] `hf_client`-এর পক্ষে `http_client` সরাসরি প্রত্যাখ্যান করে।

    Pydantic AI-এর তৈরি একটি client-এ, [`create_async_httpx2_client()`][pydantic_ai.models.create_async_httpx2_client] থেকে আসা একটিসহ, সেকেন্ডে দেওয়া একটি রিকোয়েস্ট timeout client-এর connect timeout (ডিফল্ট 5 সেকেন্ড) আর pool timeout (ডিফল্ট 600 সেকেন্ড, Google-এর জন্য 20 মিনিট) কমাতে পারে কিন্তু কখনো বাড়াতে পারে না। এর মধ্যে আছে google-genai প্রতিটি Gemini রিকোয়েস্টের সাথে যে timeout পাঠায়, যা client-এর read timeout-এর সমান। আরও দীর্ঘ সময় সংযোগ করতে, এমন একটি `httpx.Timeout` দিন যার `connect` অন্য ধাপগুলো থেকে আলাদা, বা আপনার নিজের `http_client`।
- **`ModelSettings['request_timeout']` Pydantic AI নিজে প্রয়োগ করে, প্রতিটি মডেলে।** এটি কখনো provider-কে পাঠানো হয় না, তাই সব জায়গায় একইভাবে কাজ করে, `timeout` উপেক্ষা করা মডেল ক্লাসসহ। দেখুন [Model request deadlines](#model-request-deadlines)।
- **টুল timeout শুধু [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] প্রয়োগ করে, আর প্রতিটি toolset নিজেরটি বহন করে।** `Agent(tool_timeout=...)` সেট করে *এজেন্টে* নথিভুক্ত টুলের ডিফল্ট — আপনার নিজের তৈরি আর `toolsets=[...]` দিয়ে দেওয়া একটি `FunctionToolset`-এ এটি পৌঁছায় না। সেই toolset-কে তার নিজের `FunctionToolset(timeout=...)` দিন, বা নির্দিষ্ট টুলগুলোতে `timeout=` সেট করুন। একটি [MCP সার্ভার](mcp/client.md), একটি [বাইরের toolset](deferred-tools.md), বা একটি নিজের [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] থেকে আসা টুল কোনোটিই পড়ে না; বদলে সার্ভার-পক্ষের বা transport-স্তরের timeout দিয়ে সেগুলো বাঁধুন।

একটি টুলের ভেতরে নিজে একটি সময়সীমা প্রয়োগ করলে, `TimeoutError` বেরিয়ে যেতে না দিয়ে ধরে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] বা [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] হিসেবে আবার তুলুন। একটি খালি `TimeoutError`-এর কী হয় তা নির্ভর করে সেই টুলের নিজের timeout আছে কিনা তার ওপর:

- **টুল বা তার toolset-এ কোনো `timeout` নেই।** এটি একটি সাধারণ exception আর এজেন্ট রান থেকে বেরিয়ে যায় — যদি না একটি [capability](capabilities/overview.md) `on_tool_execute_error` বাস্তবায়ন করে, যা এটিকে একটি বদলি টুল ফল বা একটি `ModelRetry`-তে রূপান্তর করতে পারে।
- **একটি `timeout` কনফিগার করা আছে।** কলটি `anyio.fail_after(timeout)`-এর ভেতরে চলে, যা মেয়াদ শেষ হওয়াও `TimeoutError` দিয়ে জানায়, তাই আপনার নিজের তোলা একটি `TimeoutError` সময়সীমা পেরোনো থেকে আলাদা করা যায় না আর একই `'Timed out after N seconds.'` retried টুল ফল হয়ে যায় — এমন একটি সময়সীমা জানিয়ে যা হয়তো কখনো পেরোয়নি।

টুলে আবার তোলাটাই বেশি স্থানীয় পছন্দ; hook হলো প্রতিটি টুলে একটি নীতি প্রয়োগ করার জন্য।

## মডেল রিকোয়েস্টের সময়সীমা { #model-request-deadlines }

[`ModelSettings['timeout']`][pydantic_ai.settings.ModelSettings.timeout] provider client প্রয়োগ করে একটি রিকোয়েস্টের একটি প্রচেষ্টায়: প্রতিটি SDK retry একটি নতুন পায়, আর একটি stream করা উত্তরে এটি শুধু প্রতিটি টুকরোর অপেক্ষা সীমিত করে, পুরো উত্তর নয়। `request_timeout` হলো একটি মডেলে পুরো রিকোয়েস্টের ওপর একটি ঘড়ি, Pydantic AI-এর প্রয়োগ করা: provider SDK আর [HTTP transport](retries.md#transport-retries)-এর করা প্রতিটি প্রচেষ্টা, তাদের মাঝের backoff, provider থামিয়ে রাখা একটি উত্তরের যেকোনো ধারাবাহিকতা, আর একটি stream করা উত্তর তার শেষ টুকরো পর্যন্ত পড়া। Temporal-এর ভাষায়, `timeout` হলো একটি প্রচেষ্টার start-to-close timeout, আর `request_timeout` রিকোয়েস্টের schedule-to-close timeout।

```python title="request_timeout.py"
from pydantic_ai import Agent, ModelRequestTimeout

agent = Agent(
    'openai:gpt-6.1-sol',
    model_settings={
        'timeout': 30,  # (1)!
        'request_timeout': 90,  # (2)!
    },
)


async def main():
    try:
        result = await agent.run('What is the capital of France?')
        print(result.output)
        #> The capital of France is Paris.
    except ModelRequestTimeout as e:
        print(f'{e.model_name} took longer than {e.timeout} seconds')
```

1. প্রতিটি প্রচেষ্টা 30 সেকেন্ড পায়, আর OpenAI SDK ডিফল্টভাবে একটি ব্যর্থ প্রচেষ্টা দুবার আবার চেষ্টা করে।
2. যতগুলো প্রচেষ্টাই লাগুক, 90 সেকেন্ড পরে রিকোয়েস্ট শেষ হয়।

/// info | কোডটি সহজ ভাষায়

শুধু `timeout=30` দিলে সবচেয়ে খারাপ ক্ষেত্রে ৩ প্রচেষ্টা × ৩০ সেকেন্ড = ৯০ সেকেন্ড, আর backoff-এর অপেক্ষা যোগ হলে আরও বেশি। `request_timeout=90` সেই মোট সময়ের ওপর একটি শক্ত ছাদ বসায়: প্রচেষ্টা যতই হোক, ৯০ সেকেন্ডে শেষ।

///

সময়সীমা পেরোলে, রিকোয়েস্ট বাতিল হয় আর [`ModelRequestTimeout`][pydantic_ai.exceptions.ModelRequestTimeout] ওঠে। এটি একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError], তাই একটি [`on_model_request_error`][pydantic_ai.capabilities.AbstractCapability.on_model_request_error] hook একটি stream নয় এমন রিকোয়েস্টের timeout থেকে উদ্ধার করতে পারে, অন্য যেকোনো ব্যর্থ রিকোয়েস্টের মতো। একটি একক প্রচেষ্টার timeout, যা provider client বা transport তোলে আর `timeout` নিয়ন্ত্রণ করে, একটি ভিন্ন এরর আর কখনো `ModelRequestTimeout` হিসেবে জানানো হয় না।

- **Streaming।** সময়সীমা রিকোয়েস্ট করার সময় স্থির হয় আর stream তার শেষ টুকরো পর্যন্ত পড়াকে ঢাকে, তাই event খরচ করতে আপনার কোডের সময়ও এতে গোনা হয়: সময়সীমা পেরোনোর সময়ও পড়তে থাকা একজন গ্রাহক stream থেকে `ModelRequestTimeout` পায়। এ পর্যন্ত যা stream হয়েছে তা বার্তার ইতিহাসে একটি `'interrupted'` উত্তর হিসেবে রাখা হয়। শেষ টুকরো পড়া হয়ে গেলে, সময়সীমা আর প্রযোজ্য নয়। এর মধ্যে পড়ে `run()` পেছনে যে streaming করে তা, যেমন একটি [event stream handler](agent.md#streaming-all-events)-সহ।
- **Fallback।** একটি [`FallbackModel`](models/overview.md#fallback-model) যে প্রতিটি মডেল চেষ্টা করে তাকে একটি নতুন সময়সীমা দেয়, আর একটির সময় শেষ হলে এর ডিফল্ট `fallback_on` পরের মডেলে যায়। সময় শেষ হওয়া প্রতিটি প্রচেষ্টা উত্তরের [`failed_attempts`][pydantic_ai.messages.ModelResponse.failed_attempts]-এ রেকর্ড হয়। এর বাছা মডেল তার উত্তর থামালে, ধারাবাহিকতাটি তখনো সেই মডেলে একই রিকোয়েস্ট আর তার সময়সীমা রাখে, অথচ বার্তার ইতিহাস থেকে থামানো উত্তর আবার শুরু করা পরের একটি রান একটি নতুন শুরু করে। একটি মডেলের নিজের `settings` তার জন্য একটি ভিন্ন `request_timeout` সেট করতে পারে। একটি stream করা উত্তর শুরু হয়ে গেলে, `FallbackModel` আর fallback করে না, তাই পড়ার সময় সময় শেষ হলে `ModelRequestTimeout` ওঠে।
- **Durable execution।** [Temporal](durable_execution/temporal.md)-এ, সময়সীমা workflow-এর ঘড়িতে চলে, একটি durable timer হিসেবে। এটি পেরোলে, মডেল রিকোয়েস্টের activity বাতিল হয়, যা তার activity retry-ও শেষ করে, আর workflow-এ `ModelRequestTimeout` ওঠে। একটি `FallbackModel` activity-র ভেতরে চলে, প্রতিটি মডেলকে দেওয়া সময়সীমাসহ। একটি থামানো উত্তরের প্রতিটি অংশ একটি আলাদা activity, আর বাছা মডেলের সময়সীমা একটি থেকে পরেরটিতে একটি ঘড়ি-সময়ের timestamp হিসেবে বয়ে যায়, তাই এটি তবুও পুরো ধারাবাহিকতা ঢাকে। [DBOS](durable_execution/dbos.md) আর [Prefect](durable_execution/prefect.md)-এ, একটি `FallbackModel`-এর সময়সীমা একইভাবে ধাপগুলোর মধ্যে বয়ে যায়। অন্যথায় সময়সীমা প্রসেসের ঘড়িতে, মডেল রিকোয়েস্ট ধাপের চারপাশে চলে, আর crash-এর পরে উদ্ধার হওয়া একটি workflow একটি নতুন শুরু করে।
- **রানের timeout।** একটি রান মেথডে `timeout=` [পুরো রান বাঁধে](#bounding-a-whole-run), তার মডেল রিকোয়েস্টসহ, তাই একটি রিকোয়েস্টে দুটো সময়সীমাই প্রযোজ্য আর আগেরটি জেতে। রানের সময়সীমা আগে পেরোলে, রিকোয়েস্ট রানের বাকিটার সাথে বাতিল হয়, যা `ModelRequestTimeout` নয়, [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut] তোলে, আর একটি `FallbackModel` fallback করে না।
- **সরাসরি রিকোয়েস্ট।** [`model_request()`][pydantic_ai.direct.model_request] আর [`model_request_stream()`][pydantic_ai.direct.model_request_stream]-ও এটি প্রয়োগ করে।

## পুরো রান বাঁধা { #bounding-a-whole-run }

রান যা কিছু করে তার সব বাঁধতে [`run()`][pydantic_ai.agent.AbstractAgent.run], [`run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync], [`run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream], [`run_stream_sync()`][pydantic_ai.agent.AbstractAgent.run_stream_sync], [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] বা [`iter()`][pydantic_ai.agent.Agent.iter]-এ `timeout=` (সেকেন্ডে) দিন: প্রতিটি মডেল রিকোয়েস্ট, টুল কল আর hook, আর streaming মেথডে stream খরচ করতে আপনার ব্যয় করা সময়। সময় শেষ হলে, রানটি [`CancellationToken`][pydantic_ai.CancellationToken]-এর মতো একইভাবে [বাতিল](agent.md#cancelling-a-run) হয়: চলমান মডেল রিকোয়েস্ট বা stream বন্ধ হয়, চলমান টুল কল বাতিল হয়, আর রান যা শেষ করেছে তার সবকিছুসহ [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut] তোলে:

```python title="run_timeout.py"
from pydantic_ai import Agent, RunTimedOut

agent = Agent('openai:gpt-6.1-sol')


async def main():
    try:
        result = await agent.run('What is the capital of France?', timeout=30)
    except RunTimedOut as exc:
        history = exc.all_messages()  # (1)!
        print(f'Timed out with {len(history)} messages to resume from')
        return
    print(result.output)
    #> The capital of France is Paris.
```

1. [`all_messages()`][pydantic_ai.exceptions.RunCancelled.all_messages]-এ থাকে শেষ হওয়া টুল ফল আর একটি বাধাপ্রাপ্ত stream-এর আংশিক উত্তর। আবার শুরু করতে এটি একটি নতুন রানে `message_history` হিসেবে দিন।

`RunTimedOut` হলো [`RunCancelled`][pydantic_ai.exceptions.RunCancelled]-এর subclass, তাই `except RunCancelled` ইচ্ছা করে একটি রান থামানোর প্রতিটি উপায় সামলায়। এটি `TimeoutError`-এরও subclass, যে এরর `asyncio.timeout()` তোলে। `asyncio.timeout()`-এর মতো নয়, এতে exception শৃঙ্খল থেকে রানের অবস্থা উদ্ধার করতে হয় না, আর সময়সীমা রানের ভেতরে দৃশ্যমান:

- [`RunContext.deadline`][pydantic_ai.tools.RunContext.deadline] হলো রান যে সময়ের মধ্যে শেষ করতে হবে, UTC-তে, আর [`RunContext.remaining_time()`][pydantic_ai.tools.RunContext.remaining_time] বাকি সেকেন্ড ফেরত দেয়, তাই একটি টুল নিজের কাজ বা timeout সেই অনুযায়ী মাপতে পারে।
- একটি টুল থেকে চালানো একটি এজেন্ট রান, যেমন [agent delegation](multi-agent-applications.md#agent-delegation)-এ, সময়সীমা উত্তরাধিকারসূত্রে পায়। এর নিজের `timeout=` একে আগে করতে পারে, কিন্তু পরে নয়। ভাগ করা সময়সীমা পেরোলে, parent `RunTimedOut` তোলে; একটি sub-agent-এর নিজের, ছোট timeout শুধু delegate টুলটিকে ব্যর্থ করে, যেমন একটি sub-agent [নিজেকে বাতিল করলে](agent.md#cancellation-and-sub-agents)।
- সময় শেষ হওয়া বাতিল, মডেল এরর নয়, তাই একটি [`FallbackModel`](models/overview.md#fallback-model) এতে fallback করে না। রান চলতে থাকা অবস্থায় একটি ধীর মডেল রিকোয়েস্ট ছেড়ে fallback করতে, [`request_timeout`](#model-request-deadlines)-ও ব্যবহার করুন: যে সময়সীমা আগে পেরোয় সেটিই প্রযোজ্য।
- সময়সীমা asyncio event loop-এর একটি timer দিয়ে প্রয়োগ হয়, তাই অন্য একটি async backend-এ, যেমন Trio, `timeout=` রান শুরুর আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

```python title="run_timeout_delegation.py"
from pydantic_ai import Agent, RunContext

research_agent = Agent('openai:gpt-6.1-sol')
agent = Agent('openai:gpt-6.1-sol')


@agent.tool
async def research(ctx: RunContext, topic: str) -> str:
    remaining = ctx.remaining_time()
    if remaining is not None and remaining < 10:
        return 'Not enough time left to research this topic.'
    result = await research_agent.run(topic)  # (1)!
    return result.output
```

1. sub-agent রান এই টুল ডাকা রানের একই সময়সীমায় থামে।

[UI adapter-গুলোর](ui/overview.md) [`run_stream()`][pydantic_ai.ui.UIAdapter.run_stream], [`run_stream_native()`][pydantic_ai.ui.UIAdapter.run_stream_native] আর [`dispatch_request()`][pydantic_ai.ui.UIAdapter.dispatch_request]-ও `timeout=` নেয়। `run_stream()` আর `dispatch_request()` সময় শেষ হওয়া একটি রান ক্লায়েন্টকে একটি প্রথম-পক্ষের বাতিলের মতোই জানায় (দেখুন [Vercel AI](ui/vercel-ai.md#cancellation) আর [AG-UI](ui/ag-ui.md#usage)), আর তাদের `on_cancel` callback-এ `RunTimedOut` দেয়। `run_stream_native()` এটি তোলে।

[Durable execution](durable_execution/overview.md)-এর অধীনে, সময়সীমা ঘড়ি-সময় হিসেবে সংরক্ষিত হয়, তাই আবার চালানো বা উদ্ধার হওয়া একটি রান যে সময়সীমা নিয়ে শুরু হয়েছিল তা-ই রাখে। `TemporalDurability`, `DBOSDurability` আর `PrefectDurability` capability এটি সামলায়; deprecated wrapper এজেন্টগুলো `timeout=` প্রত্যাখ্যান করে। নোট দেখুন [Temporal](durable_execution/temporal.md#run-timeouts), [DBOS](durable_execution/dbos.md#run-timeouts) আর [Prefect](durable_execution/prefect.md#run-timeouts)-এর জন্য।

## একটি টুলের ভেতর থেকে রান শেষ করা { #ending-a-run-from-inside-a-tool }

একটি টুল কী তোলে তা ঠিক করে রান চলবে কিনা, আর মডেল কী দেখবে:

| তুলুন | রান চলবে? | মডেল দেখে |
|---|---|---|
| [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] | হ্যাঁ | কলটি শুধরাতে বলা একটি [retried টুল ফল](retries.md#tool-retries) — সেই টুলের retry বাজেট খরচ করে |
| [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] | হ্যাঁ | মানিয়ে নেওয়ার জন্য একটি [ব্যর্থ টুল ফল](tools-advanced.md#tool-failed) — retry বাজেট খরচ করে না |
| [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] / [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] | একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট দিয়ে রান শেষ করে, যদি না একটি [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] handler কলটি সেখানেই মীমাংসা করে | এখনো কিছুই না — দেখুন [Deferred Tools](deferred-tools.md) |
| অন্য যেকোনো exception | না | ডিফল্টভাবে কিছুই না — এটি `agent.run()` থেকে বেরিয়ে যায়। `on_tool_execute_error` বাস্তবায়ন করা একটি [capability](capabilities/overview.md) এটি আগে দেখে আর একটি বদলি টুল ফল ফেরত দিতে বা `ModelRetry` তুলতে পারে, রান চালু রেখে |

একটি [realtime session](realtime/overview.md)-এর ভেতরে deferred সারিটি ভিন্নভাবে পড়ে, যার থামার কোনো উপায় নেই: একটি জীবন্ত কথোপকথন বাইরের একটি ফলের জন্য অপেক্ষা করতে পারে না। একটি `HandleDeferredToolCalls` handler তবুও কলটি সেখানেই মীমাংসার সুযোগ পায়, কিন্তু যেখানে একটি রান একটি `DeferredToolRequests` আউটপুট দিয়ে শেষ হতো, একটি session বদলে মডেলকে ব্যাখ্যা দিয়ে উত্তর দেয় যে session-এর সময় টুলটি শেষ করা যাবে না, আর চলতে থাকে। দেখুন [Deferred and approval-required tools](realtime/tools.md#deferred-and-approval-required-tools)। শেষ সারিটিও সেখানে ভিন্নভাবে পড়ে: একটি session মডেলকে একটি সাধারণ ব্যর্থতা দিয়ে উত্তর দেয়, কখনো exception-এর বার্তা নয়, আর চলতে থাকে, অথচ exception তবুও আপনার কাছে তোলা হয়। দেখুন [Function tools](realtime/tools.md#function-tools)।

একটি টুল exception না তুলেও রান শেষ করতে পারে, [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel] ডেকে — রান [`RunCancelled`][pydantic_ai.exceptions.RunCancelled] দিয়ে শেষ হয় আর টুলের ফেরত মান বাদ পড়ে। দেখুন [Cancelling the Run from a Tool](tools-advanced.md#cancelling-the-run-from-a-tool)।

এমন কোনো exception নেই যা একটি *সফল* আউটপুট দিয়ে রান আগেভাগে শেষ করে। একটি টুলকে একটি মান দিয়ে রান শেষ করতে দিতে, সেই মানটিকে রানের আউটপুট বানান: এজেন্টকে এমন একটি [আউটপুট টুল](output.md#tool-output) দিন যা মডেল ডাকতে পারে, বা একটি [আউটপুট ফাংশন](output.md#output-functions) যা ফল তৈরি করে।

/// check | সংক্ষেপে মনে রাখুন

* `ModelSettings(timeout=...)` = প্রতি প্রচেষ্টা (সব মডেলে নয়); `request_timeout=...` = পুরো রিকোয়েস্ট, সব মডেলে।
* টুলে `Agent(tool_timeout=...)` বা `timeout=`; সময় পেরোলে মডেল একটি retried ফল পায়।
* `agent.run(..., timeout=60)` পুরো রান বাঁধে; পেরোলে `RunTimedOut` (`e.all_messages()` দিয়ে আবার শুরু)।
* টুলে `ctx.remaining_time()` দিয়ে বাকি সময় দেখে কাজ মাপুন।
* টুল থেকে: `ModelRetry` (শুধরাও), `ToolFailed` (মানিয়ে নাও), অন্য exception (রান বন্ধ), `ctx.cancel()` (রান বাতিল)।

///
