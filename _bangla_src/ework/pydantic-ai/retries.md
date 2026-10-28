# আবার চেষ্টা (Retries) { #retries }

/// note | এই পেজে যা শিখবেন

* একটি এজেন্ট রানে "retry" সাতটি আলাদা স্তরে ঘটে, আর তাদের বাজেট আলাদা — এই পেজ সেই মানচিত্র।
* কেন retry গুণ হয়ে যায় (একটি কলে বহু রিকোয়েস্ট), আর কীভাবে তা নিয়ন্ত্রণে রাখবেন।
* Transport retry (`tenacity` দিয়ে HTTP স্তরে), provider SDK retry, fallback মডেল।
* টুল আর আউটপুট retry (মডেলকে শুধরে নিতে বলা), আর মডেলের কাছে কোন feedback যায়।

///

একটি এজেন্ট রানে "Retry" মানে সাতটি ভিন্ন জিনিস, সাতটি ভিন্ন স্তরে, আর তারা বাজেট ভাগ করে না। এগুলো গুলিয়ে ফেলাই সাধারণত এমন রানের কারণ যা প্রত্যাশার চেয়ে অনেক বেশি (বা অনেক কম) আবার চেষ্টা করে। এই পেজটি হলো মানচিত্র; প্রতিটি স্তর যে পেজে বিস্তারিত কনফিগার হয় সেখানে লিংক করে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি চিঠি পাঠানোর কথা ভাবুন। ডাকপিয়ন রাস্তা বন্ধ পেলে নিজেই আবার যায় (transport retry) — আপনি টেরও পান না। ডাকঘর নিজেও আবার পাঠাতে পারে (SDK retry)। এক ডাকঘর বন্ধ থাকলে অন্য ডাকঘর দিয়ে পাঠানো (fallback)। আর প্রাপক চিঠি পড়ে বললেন "ঠিকানা ভুল লিখেছ, আবার লেখো" — এটি টুল/আউটপুট retry, যেখানে চিঠির লেখক (মডেল) নিজেই শুধরে নেয়। প্রতিটি আলাদা, আর একসাথে মিলে বহুগুণ হতে পারে।

///

## স্তরগুলো { #the-layers }

| স্তর | কী আবার চেষ্টা করে | কী দিয়ে কনফিগার হয় | বার্তার ইতিহাসে কী যোগ করে |
|---|---|---|---|
| [Transport](#transport-retries) | provider-এ একই HTTP রিকোয়েস্ট | আপনার HTTP client-এ [`AsyncHTTPX2TenacityTransport`][pydantic_ai.retries.AsyncHTTPX2TenacityTransport] | কিছুই না — এজেন্ট কখনো প্রচেষ্টাগুলো দেখে না |
| [Provider SDK](#provider-sdk-retries) | একই HTTP রিকোয়েস্ট, provider SDK-র নিজের client দিয়ে আবার পাঠানো | SDK client নিজে; ডিফল্ট আর কনফিগারেশন provider-নির্দিষ্ট | কিছুই না — এজেন্ট কখনো প্রচেষ্টাগুলো দেখে না |
| [Durable execution](durable_execution/overview.md) | পুরো মডেল রিকোয়েস্ট, workflow engine-এর আবার চালানো — তারের কাছের প্রতিটি স্তরে আবার ঢুকে; Temporal-এ ডিফল্টভাবে সীমাহীন (`maximum_attempts=0`) | Temporal-এর `ActivityConfig`-এ `retry_policy`, DBOS-এর `StepConfig`-এ `max_attempts`, Prefect-এর `TaskConfig`-এ `retries` | কিছুই না — engine ধাপটি আবার চালায় |
| [Model fallback](#model-fallback-is-not-a-retry) | একই রিকোয়েস্ট একটি *ভিন্ন* মডেলে | [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] | শুধু জয়ী উত্তর, যা ব্যর্থ প্রচেষ্টাগুলো `failed_attempts`-এ তালিকা করে |
| [Tool](#tool-retries) | একটি টুল কল, মডেলকে তা শুধরাতে বলে | `retries={'tools': N}` আর প্রতি-টুলের সীমা | সেই কলের ফল হিসেবে `outcome='retried'`-সহ একটি [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] |
| [Output](#output-retries) | মডেলের চূড়ান্ত উত্তর, মডেলকে তা শুধরাতে বলে | `retries={'output': N}` আর [`ToolOutput(max_retries=N)`][pydantic_ai.output.ToolOutput.max_retries] | একটি [`RetryFeedbackPart`][pydantic_ai.messages.RetryFeedbackPart], বা একটি retried `ToolReturnPart` — দেখুন [নিচে](#output-retries) |
| [Model-request hooks](hooks.md) | মডেল রিকোয়েস্ট, `before_model_request`, `after_model_request`, `wrap_model_request` বা `on_model_request_error` থেকে `ModelRetry` তুলে | hook নিজে; এটি **আউটপুট** বাজেট থেকে খরচ করে | একটি `RetryFeedbackPart` বহন করা একটি নতুন রিকোয়েস্ট |

শুধু শেষ তিনটি "এজেন্ট retry" — প্রতিটির খরচ একটি মডেল-যাওয়া-আসা, কারণ একটি retry মানেই আরেকটি রিকোয়েস্ট। বাকি চারটি মডেলের কাছে অদৃশ্য: সে কখনো একটি প্রচেষ্টা ব্যর্থ হতে দেখে না।

## Retry-এর গুণন { #retry-multiplication }

স্তরগুলো বাজেট ভাগ করে না, কিন্তু একটির ওপর আরেকটি চাপে: একটি স্তরের retry তারের কাছের প্রতিটি স্তরের প্রচেষ্টাকে মুড়ে রাখে। একটি যৌক্তিক কল যদি সর্বোচ্চ `N`টি মডেল রিকোয়েস্ট করতে পারে — প্রথম প্রচেষ্টা, প্রতিটি টুল কলের জন্য একটি পরবর্তী রিকোয়েস্ট, আর [টুল](#tool-retries) আর [আউটপুট](#output-retries) retry বাজেট যা যোগ করে — প্রতিটি মডেল রিকোয়েস্ট একটি [fallback মডেল](#model-fallback-is-not-a-retry) দিয়ে সর্বোচ্চ `F`টি মডেলে চেষ্টা হতে পারে, সেগুলোর প্রতিটি একটি provider SDK client পাঠায় যার সর্বোচ্চ `M`টি প্রচেষ্টা অনুমোদিত, আর প্রতিটি প্রচেষ্টা এমন একটি transport-এ যায় যার সর্বোচ্চ `K`টি প্রচেষ্টা অনুমোদিত, তাহলে একটি যৌক্তিক কল নেটওয়ার্কে সর্বোচ্চ `N`×`F`×`M`×`K`টি তারের রিকোয়েস্ট পাঠাতে পারে। [Durable execution](durable_execution/overview.md)-এর অধীনে মডেল রিকোয়েস্ট চালানো ধাপটিও আবার চেষ্টা করে, প্রতিবার `M` আর `K`-তে আবার ঢুকে — আর Temporal-এ সেই retry সংখ্যা সীমাহীন, যদি না আপনি নিজে `maximum_attempts` সেট করেন।

- `N` — প্রতি যৌক্তিক কলে মডেল রিকোয়েস্ট: প্রথম প্রচেষ্টা, প্রতিটি টুল কলের জন্য একটি পরবর্তী রিকোয়েস্ট (একটি সফল টুল কলও আরেকটি রিকোয়েস্ট সারিতে রাখে), আর [টুল](#tool-retries) আর [আউটপুট](#output-retries) বাজেট যে retry যোগ করে
- `F` — প্রতি মডেল রিকোয়েস্টে মডেল: একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর মডেলের সংখ্যা, বা না থাকলে `1`
- `M` — provider SDK client-এর ভেতরে প্রতি মডেল রিকোয়েস্টে প্রচেষ্টা। SDK এই বাজেট ঠিক করে; যেমন, `max_retries=N` দিয়ে কনফিগার করা একটি OpenAI client `1 + N`টি প্রচেষ্টা অনুমোদন করে, আর [`ModelSettings['max_retries']`](#setting-the-sdk-retry-count-per-request) প্রতি রিকোয়েস্টে এটি override করে। provider-নির্দিষ্ট সেটিংয়ের জন্য দেখুন [provider SDK retries](#provider-sdk-retries)।
- `K` — তারে প্রতি রিকোয়েস্টে প্রচেষ্টা: transport-এর থামার কৌশল, তাই `stop_after_attempt(N)` মোট `N`টি প্রচেষ্টা অনুমোদন করে (`K = N`), এক যোগ retry নয় — দেখুন [transport retries](#transport-retries)

প্রতিটি তারের রিকোয়েস্ট নিজের দেরি বহন করে — আর রিকোয়েস্ট মডেলে পৌঁছালে token-এর বিল হয় — তাই সুখী পথ নয়, সবচেয়ে খারাপ ক্ষেত্রটিই আপনার বাজেটকে শুষে নিতে হবে। [`UsageLimits`][pydantic_ai.usage.UsageLimits] শুধু `N` সীমিত করে: এর `request_limit` (ডিফল্ট `50`) প্রতি রানে এজেন্ট যে মডেল উত্তরের ওপর কাজ করে সেগুলো গোনে, আর তাদের নিচের fallback প্রচেষ্টা, SDK client retry আর transport retry কখনো দেখে না। তাদের token আর খরচ এর token আর খরচের সীমায় গোনা হয় যখনই provider সেগুলো জানায়, যেমন একটি fallback মডেলের প্রত্যাখ্যাত উত্তরে জানায়, কিন্তু সাধারণত একটি ব্যর্থ রিকোয়েস্টে নয়। [`ModelSettings.timeout`][pydantic_ai.settings.ModelSettings.timeout] প্রতি প্রচেষ্টায় প্রযোজ্য — একটি retry করা SDK client প্রতিটি retry-এ এটি আবার চালু করে — আর শুধু [যে মডেল ক্লাসগুলো এটি পাঠায়](timeouts.md#bounding-how-long-a-step-takes) সেগুলোতে। বদলে [`ModelSettings.request_timeout`][pydantic_ai.settings.ModelSettings.request_timeout] একটি মডেলে একটি রিকোয়েস্টের সব `M × K` প্রচেষ্টা সীমিত করে, প্রতিটি মডেল ক্লাসে: দেখুন [Model request deadlines](timeouts.md#model-request-deadlines)। সময়ের দিকের জন্য দেখুন [Timeouts](timeouts.md#bounding-how-long-a-step-takes)।

`retries={'output': 2}` (শুধু চূড়ান্ত উত্তরের জন্যই সর্বোচ্চ 3টি মডেল রিকোয়েস্ট), OpenAI SDK-র ডিফল্ট `max_retries=2` (প্রতি রিকোয়েস্টে 3টি প্রচেষ্টা), আর `stop_after_attempt(2)` দিয়ে থামানো একটি transport (প্রতি তারের রিকোয়েস্টে 2টি প্রচেষ্টা)-সহ একটি রান fallback মডেল ছাড়া নেটওয়ার্কে `3` × `1` × `3` × `2 = 18`টি রিকোয়েস্ট পাঠাতে পারে, আর দুটি মডেলের একটি fallback মডেলসহ তার দ্বিগুণ। প্রতিটি নিজের `ModelSettings(timeout=10)` সময়সীমা বহন করে — সবচেয়ে খারাপ ক্ষেত্রে 180 সেকেন্ড রিকোয়েস্ট-সময়, retry-এর মাঝের backoff অপেক্ষার আগেই।

/// warning | সাধারণ ভুল

transport-এ retry বসিয়ে SDK-র নিজের retry-ও চালু রাখা। দুটোই চালু থাকলে প্রচেষ্টা গুণ হয়ে যায় (৩ × ৩ = ৯)। একটি স্তরেই retry রাখুন: transport ব্যবহার করলে `ModelSettings(max_retries=0)` দিয়ে SDK-রটি বন্ধ করুন।

///

## Transport retry { #transport-retries }

Transport retry থাকে মডেল client-এর নিচে: একটি ব্যর্থ HTTP রিকোয়েস্ট এজেন্ট টের না পেয়েই আবার পাঠানো হয়। আপনি provider-কে দেওয়া HTTP client-এ একটি retry-করা transport না বসালে এই স্তরে কিছুই আবার চেষ্টা হয় না, আর কোন এরর এর যোগ্য তা আপনি ঠিক করেন।

Rate limit, সংযোগ রিসেট আর 5xx উত্তরের জন্য এটিই সঠিক স্তর। Transport-গুলো [tenacity](https://github.com/jd/tenacity)-র ওপর তৈরি আর [`httpx2`](https://httpx2.pydantic.dev/) client-এ লাগানো যায়, তাই যে provider-এর SDK একটি নিজের `httpx2` client নেয় তার সাথে কাজ করে। [AWS Bedrock](#aws-bedrock) ব্যতিক্রম: এটি বদলে boto3 দিয়ে আবার চেষ্টা করে।

transport-এর বাইরে নিজের backoff বানালে, [`ModelAPIError.retry_after`][pydantic_ai.exceptions.ModelAPIError.retry_after] provider যে অপেক্ষা চেয়েছে তা দেয়, আগে থেকেই সেকেন্ডে পার্স করা, আর [এররের শ্রেণি](models/overview.md#handling-model-api-errors) বলে কোন ব্যর্থতা একটি retry ঠিক করতে পারে না, যেমন একটি প্রত্যাখ্যাত API key বা অজানা মডেলের জন্য একটি [`ModelRequestRejectedError`][pydantic_ai.exceptions.ModelRequestRejectedError]।

### ইনস্টলেশন { #installation }

retry transport ব্যবহার করতে `tenacity` ইনস্টল করতে হবে, যা `retries` dependency group দিয়ে করতে পারেন:

/// tab | pip

```bash
pip install 'pydantic-ai-slim[retries]'
```

///

/// tab | uv

```bash
uv add 'pydantic-ai-slim[retries]'
```

///


### একটি retry-করা client { #a-retrying-client }

retry-করা transport-টি [`create_async_httpx2_client()`][pydantic_ai.models.create_async_httpx2_client]-এ দিন, যাতে client-টি Pydantic AI-এর তৈরি client-এর timeout আর user agent রাখে, আর client-টি provider-কে দিন। তারপর [`ModelSettings['max_retries']`](#setting-the-sdk-retry-count-per-request) `0` সেট করুন, যাতে transport-ই একমাত্র retry-করা স্তর হয়, এমন একটি নয় যার প্রচেষ্টা provider SDK-র নিজেরগুলোর সাথে [গুণ হয়](#retry-multiplication):

⟦CODE1⟧

আপনার দেওয়া transport client-এর নিজে বানানোটির জায়গা নেয়, তাই connection pool এর অধীনে। `wrapped` ছাড়া, একটি retry-করা transport তার প্রচেষ্টা পাঠায় নিজের তৈরি একটি `httpx2.AsyncHTTPTransport` দিয়ে, Pydantic AI-এর নিজের client-এর মতো একই pool সীমাসহ (1000টি সংযোগ, সর্বোচ্চ 100টি সচল রাখা)। একটি client-এর transport থাকলে HTTPX `HTTP_PROXY`, `HTTPS_PROXY` আর `ALL_PROXY` environment variable থেকে proxy পড়াও বন্ধ করে, তাই proxy দরকার হলে retry-করা transport-কে একটি `proxy`-সহ নিজের `wrapped` transport দিন। আপনার তৈরি একটি `wrapped` transport-এ HTTPX-এর ডিফল্ট pool থাকে, 100টি সংযোগ, 20টি সচল রাখা, যদি না এর `limits`-ও সেট করেন: `wrapped=httpx2.AsyncHTTPTransport(proxy=..., limits=httpx2.Limits(max_connections=1000, max_keepalive_connections=100))`।

### অপেক্ষার কৌশল { #wait-strategies }

#### wait_retry_after { #wait_retry_after }

`wait_retry_after` ফাংশন একটি বুদ্ধিমান অপেক্ষার কৌশল, যা নিজে থেকে HTTP `Retry-After` header মানে:

⟦CODE2⟧

এই অপেক্ষার কৌশল:

- HTTP 429 উত্তর থেকে `Retry-After` header নিজে থেকে পার্স করে
- সেকেন্ড ফরম্যাট (`"30"`) আর HTTP তারিখ ফরম্যাট (`"Wed, 21 Oct 2015 07:28:00 GMT"`), দুটোই সমর্থন করে
- OpenAI আর Anthropic যে `retry-after-ms` header (মিলিসেকেন্ড) পাঠায় সেটিকে অগ্রাধিকার দেয়, যেমন তাদের SDK দেয়
- header না থাকলে বা পার্স করা না গেলে আপনার বাছা কৌশলে ফিরে যায়
- অতিরিক্ত দেরি ঠেকাতে `max_wait` সীমা মানে

/// info | Backoff সহজ ভাষায়

"Exponential backoff" মানে প্রতিবার ব্যর্থ হলে আগের চেয়ে বেশি অপেক্ষা: ১ সেকেন্ড, ২, ৪, ৮... — যাতে ব্যস্ত সার্ভারকে আরও চাপ না দেওয়া হয়। আর 429 উত্তরে সার্ভার নিজেই যদি বলে "৩০ সেকেন্ড পরে এসো" (`Retry-After`), `wait_retry_after` ঠিক সেটিই মানে।

///

### Transport ক্লাস { #transport-classes }

#### AsyncHTTPX2TenacityTransport { #asynchttpx2tenacitytransport }

asynchronous HTTP client-এর জন্য (বেশিরভাগ ক্ষেত্রে প্রস্তাবিত):

⟦CODE3⟧

#### HTTPX2TenacityTransport { #httpx2tenacitytransport }

synchronous HTTP client-এর জন্য:

⟦CODE4⟧

### সাধারণ retry ধরন { #common-retry-patterns }

#### `Retry-After` সমর্থনসহ rate limit সামলানো { #rate-limit-handling-with-retry-after-support }

⟦CODE5⟧

`wait_retry_after` ফাংশন 429 (rate limit) উত্তরে `Retry-After` (বা `retry-after-ms`) header নিজে থেকে চেনে আর নির্দিষ্ট সময় অপেক্ষা করে। কোনো header না থাকলে, exponential backoff-এ ফিরে যায়।

#### নেটওয়ার্ক এরর সামলানো { #network-error-handling }

⟦CODE6⟧

#### নিজের retry লজিক { #custom-retry-logic }

⟦CODE7⟧

### `httpx2`-সামঞ্জস্যপূর্ণ provider-এর সাথে ব্যবহার { #using-with-httpx2-compatible-providers }

retry transport সেই যেকোনো provider-এ কাজ করে যার `http_client` আর্গুমেন্ট একটি `httpx2.AsyncClient` নেয়। প্রতিটি
[provider-এর ডক](models/overview.md) দেখুন সে কোন client টাইপ নেয়; [Bedrock](#aws-bedrock) boto3 ব্যবহার করে আর নিজের উপায়ে
retry কনফিগার করে।

যে provider-এর SDK এখনো একটি পুরনো `httpx.AsyncClient` চায় (যেমন Groq আর Cohere), তারা Pydantic AI v2-এর সময় সেই client-এ
deprecated [`TenacityTransport`][pydantic_ai.retries.TenacityTransport] আর
[`AsyncTenacityTransport`][pydantic_ai.retries.AsyncTenacityTransport] ব্যবহার করতে পারে; দুটোই
v3-এ পুরনো client সমর্থনের সাথে সরিয়ে ফেলা হবে।

#### OpenAI { #openai }

⟦CODE8⟧

#### যেকোনো OpenAI-সামঞ্জস্যপূর্ণ provider { #any-openai-compatible-provider }

⟦CODE9⟧

#### Anthropic { #anthropic }

⟦CODE10⟧

### ভালো অভ্যাস { #best-practices }

1. **সংযত দিয়ে শুরু করুন**: অল্প কয়েকটি retry (3-5) আর যুক্তিসঙ্গত অপেক্ষার সময় দিয়ে শুরু করুন।

2. **Exponential backoff ব্যবহার করুন**: বিভ্রাটের সময় সার্ভারকে চাপে ডুবিয়ে দেওয়া এড়াতে এটি সাহায্য করে।

3. **সর্বোচ্চ অপেক্ষার সময় সেট করুন**: যুক্তিসঙ্গত সর্বোচ্চ অপেক্ষার সময় দিয়ে অনির্দিষ্ট দেরি ঠেকান।

4. **Rate limit ঠিকভাবে সামলান**: সম্ভব হলে `Retry-After` header মানুন।

5. **Retry প্রচেষ্টা লগ করুন**: production-এ retry আচরণ পর্যবেক্ষণে লগিং যোগ করুন। (`httpx2` instrument করলে Logfire এটি নিজে থেকে ধরবে।)

6. **Circuit breaker বিবেচনা করুন**: বেশি ট্রাফিকের অ্যাপ্লিকেশনে, circuit breaker ধরন বাস্তবায়ন বিবেচনা করুন।

/// tip | Production-এ retry পর্যবেক্ষণ

অতিরিক্ত retry ভেতরের সমস্যা নির্দেশ করতে পারে আর খরচ বাড়ায়। [Logfire](logfire.md) আপনাকে retry-এর ধরন ট্র্যাক করতে সাহায্য করে:

- কোন রিকোয়েস্ট retry ঘটিয়েছে দেখুন
- retry-এর কারণ বুঝুন (rate limit, সার্ভার এরর, timeout)
- সময়ের সাথে retry-এর হার পর্যবেক্ষণ করুন
- retry কমানোর সুযোগ চিহ্নিত করুন

[HTTPX instrumentation](logfire.md#monitoring-http-requests) চালু থাকলে, retry প্রচেষ্টা নিজে থেকে আপনার trace-এ ধরা পড়ে।

///

### এরর সামলানো { #error-handling }

সব retry প্রচেষ্টা ব্যর্থ হলে retry transport শেষ exception আবার তোলে। আপনার অ্যাপ্লিকেশনে এগুলো উপযুক্তভাবে সামলাতে ভুলবেন না:

⟦CODE11⟧

### Performance নিয়ে বিবেচনা { #performance-considerations }

- Retry রিকোয়েস্টে দেরি যোগ করে, বিশেষ করে exponential backoff-এ
- retry আচরণ কনফিগার করার সময় আপনার অ্যাপ্লিকেশনের মোট timeout বিবেচনা করুন
- পদ্ধতিগত সমস্যা ধরতে retry-এর হার পর্যবেক্ষণ করুন
- একাধিক রিকোয়েস্ট সামলানোর সময় ভালো concurrency-র জন্য async transport ব্যবহার করুন

আরও উন্নত retry কনফিগারেশনের জন্য, [tenacity ডকুমেন্টেশন](https://tenacity.readthedocs.io/) দেখুন।

### AWS Bedrock { #aws-bedrock }

AWS Bedrock provider `httpx2`-এর বদলে boto3-এর নিজস্ব retry ব্যবস্থা ব্যবহার করে। Bedrock-এর retry কনফিগার করতে, boto3-এর `Config` ব্যবহার করুন:

⟦CODE12⟧

সম্পূর্ণ উদাহরণের জন্য দেখুন [Bedrock: Configuring Retries](models/bedrock.md#configuring-retries)।

## Provider SDK retry { #provider-sdk-retries }

transport আর মডেলের মাঝে আরও একটি স্তর আছে যা এজেন্ট কখনো দেখে না: provider SDK-র নিজের client, যা আপনার কোড জানার আগেই ব্যর্থ রিকোয়েস্ট আবার পাঠায়। এর ডিফল্ট, retry-যোগ্য এরর আর কনফিগারেশন provider ভেদে আলাদা, তাই আপনি যে client ব্যবহার করেন তা থেকে `M` মাপুন। একটি [retry-করা transport](#transport-retries) এই client-এর *নিচে* বসে, তাই দুটো একে অপরকে বদলে না দিয়ে একটির ওপর আরেকটি চাপে: একটি কনফিগার করলে অন্যটি কখনো বন্ধ হয় না।

provider-নির্দিষ্ট সেটিং দেখুন [OpenAI](models/openai.md#custom-openai-client), [Anthropic](models/anthropic.md#custom-http-client), [Google](models/google.md#http-retries), [Groq](models/groq.md#sdk-retries), [Cohere](models/cohere.md#sdk-retries), [TypeSafe](models/typesafe.md#sdk-retries), [xAI](models/xai.md#sdk-retries), আর [AWS Bedrock](models/bedrock.md#configuring-retries)-এর জন্য।

### প্রতি রিকোয়েস্টে SDK retry সংখ্যা সেট করা { #setting-the-sdk-retry-count-per-request }

[`ModelSettings['max_retries']`][pydantic_ai.settings.ModelSettings.max_retries] নিজে client না বানিয়েই ঠিক করে SDK client একটি রিকোয়েস্ট কতবার আবার চেষ্টা করবে। `0` একটিমাত্র প্রচেষ্টা করে। SDK তবুও ঠিক করে কোন ব্যর্থতা সে আবার চেষ্টা করবে আর প্রচেষ্টার মাঝে কতক্ষণ অপেক্ষা করবে। অন্য যেকোনো মডেল সেটিংয়ের মতো, এটি প্রতি মডেল, প্রতি এজেন্ট বা প্রতি রানে প্রযোজ্য:

⟦CODE13⟧

অন্য একটি স্তর retry-এর দায়িত্ব নিলে এটি `0` সেট করুন, যাতে প্রচেষ্টার বাজেট হয় সেখানে আপনার কনফিগার করাটি, SDK-রটি দিয়ে গুণ করা সেই বাজেট নয়:

- HTTP client-এ একটি [retry-করা transport](#transport-retries);
- একটি [durable execution](durable_execution/overview.md) engine-এর retry নীতি;
- একটি [fallback মডেল](#model-fallback-is-not-a-retry), যার একটি ব্যর্থ হওয়ামাত্র পরের মডেলে যাওয়া উচিত।

একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এ, এজেন্ট বা রানে সেট করা `max_retries` প্রতিটি প্রার্থীতে প্রযোজ্য, আর প্রতিটি প্রার্থীর নিজের সেটিংয়ের ওপর অগ্রাধিকার পায়। শেষ প্রার্থীতে, যার fallback করার আর কিছু নেই, SDK retry রাখতে, বদলে অন্য প্রার্থীদের ওপর এটি সেট করুন:

⟦CODE14⟧

প্রতিটি SDK প্রতি রিকোয়েস্টে সেটিংটি নিতে পারে না:

| মডেল | সমর্থিত | নোট |
|---|---|---|
| OpenAI, আর এর ওপর তৈরি মডেল ক্লাস | ✅ | পূর্ণ সমর্থন, একটি `AsyncAzureOpenAI` client-সহ। |
| Anthropic | ✅ | পূর্ণ সমর্থন, `AsyncAnthropicBedrock`, `AsyncAnthropicVertex` আর `AsyncAnthropicFoundry` client-সহ |
| Groq | ✅ | পূর্ণ সমর্থন |
| Cohere | ✅ | পূর্ণ সমর্থন |
| Google | ✅ | সীমিত প্যারামিটার সমর্থন: provider-এর `retry_options`-এর দেরি আর status code রাখে, বা সেগুলো সেট না থাকলে SDK-র ডিফল্ট |
| Mistral | ✅ | সীমিত প্যারামিটার সমর্থন: শুধু `0`। SDK retry সংখ্যা দিয়ে নয়, পেরোনো সময় দিয়ে সীমিত করে, তাই `0` client-এ সেট করা একটি `retry_config` বন্ধ করে আর অন্য মান উপেক্ষিত হয় |
| TypeSafe | ✅ | সীমিত প্যারামিটার সমর্থন: রিকোয়েস্টের অন্য `RetryPolicy` অপশন SDK-র ডিফল্ট, client-এর নয় |
| AWS Bedrock | ❌ | boto3 প্রতি client-এ retry করে; দেখুন [Configuring Retries](models/bedrock.md#configuring-retries) |
| xAI | ❌ | gRPC প্রতি channel-এ retry করে; দেখুন [SDK retries](models/xai.md#sdk-retries) |
| Hugging Face | ❌ | client কোনো retry করে না |

যে মডেল ক্লাসগুলো এটি মানে সেগুলো তালিকাভুক্ত আছে [`ModelSettings.max_retries`][pydantic_ai.settings.ModelSettings.max_retries]-এর নিচে; বাকিগুলো তাদের retry বদলায় না, আর [`UnsupportedSettingWarning`][pydantic_ai.exceptions.UnsupportedSettingWarning] দিয়ে সতর্ক করে যে তারা এটি উপেক্ষা করছে। এমন একটি প্রার্থীসহ একটি `FallbackModel`-এ, ওপরের মতো, এজেন্ট বা রানে নয়, অন্য প্রার্থীদের নিজের সেটিংয়ে `max_retries` সেট করুন।

## Model fallback retry নয় { #model-fallback-is-not-a-retry }

বর্তমান মডেল ব্যর্থ হলে [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] *পরের* মডেলে যায়; সে কখনো একই মডেলে আবার চেষ্টা করে না। এটিকে বিকল্প না ভেবে transport retry-এর সাথে জুড়ে দিন: সাময়িক ব্যর্থতায় একই provider-এ আবার চেষ্টা করুন, provider সত্যিই বন্ধ থাকলে একটি ভিন্ন provider-এ যান। যে উত্তরটি সাড়া দেয় তা fallback মডেল যে প্রচেষ্টাগুলো পেরিয়ে এসেছে সেগুলো [`failed_attempts`][pydantic_ai.messages.ModelResponse.failed_attempts]-এ তালিকা করে, প্রতিটির মডেল, সময়কাল, এরর আর যেকোনো usage-সহ। দেখুন [Fallback Model](models/overview.md#fallback-model)।

## টুল retry { #tool-retries }

একটি টুল retry হলো মডেলের কাছে একটি বার্তা: কলটি কাজ করেনি, এই হলো কারণ, আবার চেষ্টা করো। এটি ঘটে টুলের আর্গুমেন্টে একটি Pydantic `ValidationError`-এ, টুল (বা তার `args_validator`, বা একটি টুল hook) [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুললে, একটি [টুল timeout](timeouts.md#bounding-how-long-a-step-takes)-এ, আর মডেল এমন একটি টুল ডাকলে যা নেই।

[Tool Execution, Retries, and Failures](tools-advanced.md#tool-retries) কনফিগারেশন নথিভুক্ত করে: ডিফল্ট বাজেট `1`, প্রতি-টুল / প্রতি-toolset / প্রতি-রান / এজেন্ট-জুড়ে অগ্রাধিকারের সিঁড়ি, আর `ModelRetry` আর [`ToolFailed`][pydantic_ai.exceptions.ToolFailed]-এর মধ্যে বাছাই। একটি রান নিয়ে যুক্তি করার সময় *গণক*-এর তিনটি বৈশিষ্ট্য গুরুত্বপূর্ণ:

- **গণক টুলের নাম দিয়ে চিহ্নিত, আর সাফল্যে রিসেট হয়।** প্রতিটি টুলের নিজের গণনা; পুরো রানের কোনো টুল-retry বাজেট নেই। একটি টুল সফল হলে, তার গণনা মুছে যায় — তাই যে টুল পালাক্রমে ব্যর্থ আর সফল হয়, সে `1`-এর বাজেট কখনো শেষ না করেই এক রানে বহুবার ব্যর্থ হতে পারে।
- **`max_retries=N` N টি retry অনুমোদন করে, অর্থাৎ N+1 টি প্রচেষ্টা।** `max_retries=0` মডেলকে শুধরাতে না বলেই প্রথম ব্যর্থতায় এরর তোলে।
- **মডেলের বানানো একটি টুলের নাম নিজের বাজেট পায়।** একটি অজানা টুলের নামের জবাব হয় উপলব্ধ টুলের তালিকাসহ একটি retried টুল ফল, আর এটি বানানো নামের অধীনে একটি বাজেট খরচ করে, এজেন্ট-জুড়ে `tools` বাজেট দিয়ে সীমিত। তাই যে মডেল প্রতিবার একটি *ভিন্ন* নাম কল্পনা করে, সে প্রতিবার নতুন বাজেট পায়।

একটি টুলের বাজেট শেষ হলে [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] ওঠে।

### বার্তার ইতিহাসে একটি retry দেখতে কেমন { #what-a-retry-looks-like-in-message-history }

একটি টুল কলের retry-ই হলো সেই কলের ফল: কলের `tool_call_id` বহন করা, `outcome='retried'` চিহ্নিত একটি [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart]। তাই ইতিহাসে একটি retried কল আর একটি সফল কল outcome ছাড়া দেখতে একই, আর ফলের জায়গায় কখনো দ্বিতীয় কোনো অংশ থাকে না:

⟦CODE15⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

অংশটির `content` হলো feedback নিজেই — `ModelRetry` বার্তা, বা সাধারণ JSON ডেটা হিসেবে serialize করা একটি `ValidationError`-এর এররের বিবরণ — আর এটি মডেলের কাছে পৌঁছায় provider-এর নিজস্ব এরর চ্যানেলে, একটি ব্যর্থ ফল যেটি ব্যবহার করে সেটিই: Anthropic-এর `is_error`, Bedrock-এর `status='error'`, Gemini-র `error` key, বা যেখানে provider-এর এমন কিছু নেই সেখানে একটি `{"error": ...}` wrapper। যে retry কোনো কলের জবাব দেয় না তা বদলে একটি [`RetryFeedbackPart`][pydantic_ai.messages.RetryFeedbackPart] — দেখুন [Feedback that belongs to no tool call](#feedback-that-belongs-to-no-tool-call)।

যেহেতু retry ইতিহাসে থেকে যায়, পরের একটি রানে [সেই ইতিহাস আবার ব্যবহার](message-history.md) করলে মডেলের কাছে ব্যর্থতাগুলো আবার চলে। মডেল তার আগের ভুল না দেখুক চাইলে, একটি [`ProcessHistory`](capabilities/process-history.md) capability দিয়ে সেগুলো ছেঁকে ফেলুন।

[`ToolFailed`][pydantic_ai.exceptions.ToolFailed] একই ধরনের অংশ রেকর্ড করে বদলে `outcome='failed'`-সহ, আর retry বাজেট খরচ **করে না**, তাই বারবার ব্যর্থতা একটি retry সংখ্যা দিয়ে নয়, [`UsageLimits`][pydantic_ai.usage.UsageLimits] দিয়ে সীমিত। outcome-ই পুরো পার্থক্য: `'retried'` মডেলকে কলটি শুধরাতে বলে, `'failed'` তাকে মানিয়ে নিতে বলে। দেখুন [Reporting a Failed Tool Result](tools-advanced.md#tool-failed)।

### প্রত্যাখ্যাত টুল কলের নিরীক্ষা { #auditing-rejected-tool-calls }

একটি retried ফল আরও রেকর্ড করে কেন কলটি আবার করতে হবে আর এটি তার বাজেটের কতদূর, তার [`retry`][pydantic_ai.messages.ToolReturnPart.retry]-এ (একটি [`RetryInfo`][pydantic_ai.messages.RetryInfo])। এর `cause` (একটি [`ToolRetryCause`][pydantic_ai.messages.ToolRetryCause]) হলো `'validation_error'`, `'model_retry'`, বা, কোনো টুল চলার আগেই framework যে কল প্রত্যাখ্যান করে তার জন্য, `'unknown_tool'` (মডেল নামটি বানিয়েছে) বা `'unavailable_tool'` (টুলটি আছে কিন্তু এই ধাপে ডাকা যায় না)। শেষ দুটো কোনো টুল hook দেখে না, কারণ দেওয়ার মতো কোনো নির্ধারিত টুল নেই, তাই বদলে রেকর্ড করা অংশটি মেলান। `attempt` হলো সেই টুলের এটি কততম retry, 1 থেকে গোনা, আর `max_retries` যে সীমার বিপরীতে এটি পরীক্ষা হয়েছে, তাই `attempt == max_retries` চিহ্নিত করে এরর তোলার আগে রানের করা শেষ retry; বাজেটে গোনা হয় না এমন retry-এর জন্য দুটোই `None`, যেমন একটি টুলের প্রথম `'unavailable_tool'` প্রত্যাখ্যান। এর কিছুই মডেলকে পাঠানো হয় না, তাই এটি রেকর্ড করলে রিকোয়েস্ট বদলায় না।

[Instrumentation](logfire.md) চালু থাকলে, টুলের span একই তথ্য বহন করে `pydantic_ai.tool.retry.cause`, `pydantic_ai.tool.retry.attempt` আর `pydantic_ai.tool.retry.max_retries` attribute হিসেবে, আর কোনো টুল কলের জবাব দেয় না এমন আউটপুটের retry-এর জন্য একটি [আউটপুট ফাংশনের](output.md#output-functions) span `pydantic_ai.output.retry.*` বহন করে।

একটি capability রানের তৈরি প্রতিটি রিকোয়েস্ট থেকে [`after_node_run`](capabilities/custom.md#hooking-into-the-lifecycle)-এ এগুলো সংগ্রহ করতে পারে, যা [`on_event`][pydantic_ai.capabilities.AbstractCapability.on_event]-এর মতো রানকে streaming পথে সরায় না:

⟦CODE16⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

একটি টুলের retry বাজেট শেষ হলে, রান আরেকটি retried ফল রেকর্ড না করে [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] তোলে, তাই সেই শেষ প্রত্যাখ্যান শুধু exception হিসেবে দেখা যায়।


## আউটপুট retry { #output-retries }

আউটপুট বাজেট টুল বাজেট থেকে আলাদা, আর এটি কীভাবে প্রয়োগ হয় তা নির্ভর করে মডেল তার চূড়ান্ত উত্তর কীভাবে ফেরত দেয় তার ওপর। [How output retries are enforced](agent.md#how-output-retries-are-enforced) দুটো পথই ঢাকে; বার্তার ইতিহাসের জন্য যে পার্থক্য গুরুত্বপূর্ণ:

- **লেখার পথ** (`output_type=str`, [`TextOutput`](output.md#text-output), [`NativeOutput`](output.md#native-output), [`PromptedOutput`](output.md#prompted-output), আর ব্যবহারযোগ্য আউটপুট ছাড়া উত্তর): পুরো রানজুড়ে একটি বাজেট ভাগ করা। জবাব দেওয়ার মতো কোনো টুল কল নেই, তাই retry একটি নতুন [`ModelRequest`][pydantic_ai.messages.ModelRequest] হয়ে যায় যার একমাত্র অংশ একটি [`RetryFeedbackPart`][pydantic_ai.messages.RetryFeedbackPart] — দেখুন [Feedback that belongs to no tool call](#feedback-that-belongs-to-no-tool-call)।
- **টুলের পথ** ([`ToolOutput`](output.md#tool-output)): আউটপুট বাজেট কাজ করে *প্রতি আউটপুট টুলের* ডিফল্ট সীমা হিসেবে, [`ToolOutput(max_retries=N)`][pydantic_ai.output.ToolOutput.max_retries] দিয়ে override করা যায়। retry আউটপুট টুলের `tool_call_id`-তে বাঁধা আর দেখতে হুবহু একটি ফাংশন টুলের মতো।

দুটোই ঘটে যাচাইয়ের ব্যর্থতায়, একটি [আউটপুট ফাংশন](output.md#output-functions) বা [আউটপুট validator](output.md#output-validator-functions) `ModelRetry` তুললে, আর এমন একটি মডেল উত্তরে যাতে কাজে লাগানোর মতো কিছু নেই। বাজেট শেষ হলে দুটোই [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] তোলে।

সেই শেষ কারণের একটি ব্যতিক্রম আছে: আউটপুট টাইপ যদি `None` অনুমোদন করে — যেমন `output_type=str | None` — একটি খালি বা শুধু-thinking উত্তর retry নয়, `None`-এর একটি বৈধ চূড়ান্ত ফল। যে মডেল একটি টুল কলে কাজ শেষ করে তারপর শুধু thinking দেয়, তাকে অন্যথায় ফাঁকা লেখা তৈরিতে ঠেলে দেওয়া হতো। আউটপুট validator তবুও সেই `None`-এ চলে, তাই তারা `ModelRetry` তুলে নিজেরাই একটি retry বাধ্য করতে পারে।

দুটো বাজেটই একটি আর্গুমেন্ট দিয়ে কনফিগার হয়:

⟦CODE17⟧

1. শুধু একটি `int` টুল আর আউটপুট দুটো বাজেটই সেট করে।
2. একটি [`AgentRetries`][pydantic_ai.agent.AgentRetries] dict শুধু তার নাম দেওয়া key সেট করে; নাম না দেওয়া key ডিফল্ট `1` রাখে।

একই আর্গুমেন্ট প্রতি রানে গৃহীত হয় — `agent.run(..., retries=...)` আর এর সঙ্গীরা — আর [`agent.override()`][pydantic_ai.agent.Agent.override] দিয়ে একগুচ্ছ রানের জন্য। পুরো অগ্রাধিকারের টেবিল আছে [Which retry limit wins](tools-advanced.md#which-retry-limit-wins)-এ।

/// info | এক নজরে: কোনটি কোন বাজেট খরচ করে

| ঘটনা | বাজেট |
| --- | --- |
| টুলের আর্গুমেন্ট যাচাই ব্যর্থ / টুলে `ModelRetry` | সেই টুলের (`tools`) |
| মডেল অজানা টুল ডাকল | বানানো নামের (`tools`) |
| আউটপুট যাচাই ব্যর্থ / আউটপুট validator-এ `ModelRetry` | `output` |
| মডেল-রিকোয়েস্ট hook-এ `ModelRetry` | `output` |
| টুলে `ToolFailed` | কোনোটিই নয় (`UsageLimits` সীমিত করে) |

///

### কোনো টুল কলের নয় এমন feedback { #feedback-that-belongs-to-no-tool-call }

একটি লেখার-পথের retry, আর একটি [মডেল-রিকোয়েস্ট hook](hooks.md#triggering-retries-with-modelretry)-এর একটি `ModelRetry`-এর জবাব দেওয়ার মতো কোনো টুল কল নেই। এগুলো একটি [`RetryFeedbackPart`][pydantic_ai.messages.RetryFeedbackPart] হয়, যা রেকর্ড করে উত্তরটি *কেন* ব্যবহার করা যায়নি, আর কীভাবে বলতে হবে সে বিষয়ে কিছুই না:

⟦CODE18⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

সংরক্ষিত অংশে কোনো শব্দই থাকে না; রিকোয়েস্ট তৈরির সময় প্রতিটি মডেল এটিকে একটি পাঠানোযোগ্য অংশে রূপান্তর করে, আর এর [`retry`][pydantic_ai.messages.RetryFeedbackPart.retry]-এর `cause` ঠিক করে কোনটিতে। এ কারণেই একই ইতিহাস যেকোনো মডেলে আবার চালানো যায়। একই [`RetryInfo`][pydantic_ai.messages.RetryInfo] রানের আউটপুট-retry বাজেটে `attempt` আর যে `max_retries`-এর বিপরীতে এটি পরীক্ষা হয়েছে তা রেকর্ড করে; attempt হলো পরের আউটপুট যাচাই যে [`ctx.retry`][pydantic_ai.tools.RunContext.retry] দেখে।

| `cause` | মডেলকে কী পাঠানো হয় | কেন |
|---|---|---|
| `'validation_error'` | একটি user দফা, যা শুরু হয় এক লাইনে এই বলে যে অ্যাপ্লিকেশনের যাচাই কথা বলছে, ব্যবহারকারী নয়, তারপর `<validation_errors>…</validation_errors>`-এ মোড়া এররগুলো | feedback মডেলের নিজের লেখা আউটপুট উদ্ধৃত করে, যা আবার অবিশ্বস্ত ব্যবহারকারী-ইনপুট উদ্ধৃত করতে পারে। ট্যাগটিই সেই শব্দগুলোকে একজন মানুষের দফা থেকে আলাদা করে। |
| `'model_retry'` | একই কৃতিত্ব-দেওয়া user দফা, `<retry_feedback>…</retry_feedback>`-এ মোড়া `ModelRetry` বার্তাসহ | আউটপুট validator নিয়মিতভাবে প্রত্যাখ্যাত আউটপুট বার্তায় বসায়, তাই এটি যাচাইয়ের এররের মতোই মডেলের নিজের শব্দ বহন করতে পারে। |
| `'no_output'` | কথোপকথনের মাঝের একটি system prompt, যেখানে provider কথোপকথনের মাঝে system বার্তা নেয় না সেখানে `<system>`-ট্যাগ করা user লেখায় নামানো | লেখাটি ব্যবহারযোগ্য আউটপুটের জন্য framework-এর নিজের নির্দিষ্ট অনুরোধ, আর মডেলের লেখা কিছুই বহন করে না। অন্য যেকোনো বিষয়বস্তুসহ একটি `'no_output'` অংশ, যেমন আপনার নিজের কোডের বানানো একটি, একটি `'model_retry'`-এর মতো `<retry_feedback>`-এ ঘেরা হয়ে যায়। |

এই wrapper-গুলোর যেকোনোটির ভেতরে একটি বন্ধ ট্যাগ escape করা হয়, তাই যে লেখায় মডেলের হাত ছিল তা তাকে বহন করা বক্তব্য শেষ করতে পারে না, আর দুটি user-কণ্ঠের ঘেরের ভেতরে একটি `<system>` ট্যাগও, খোলা বা বন্ধ, তাই মডেলের নিজের শব্দ নিজেকে framework-এর কথা বলে চালাতে পারে না।

/// note | Feedback কখনো স্থায়ী prompt-এ যোগ হয় না

Feedback কখনো রানের স্থায়ী prompt-এ যোগ হয় না, এমনকি যখন এটি ইতিহাসের শুরুতে থাকে — একটি হাতে বানানো `message_history`, একটি adapter লোড, [compaction](capabilities/compaction.md), [`ProcessHistory`](capabilities/process-history.md) ছাঁকা, বা কোনো user prompt ছাড়া একটি রানের প্রথম রিকোয়েস্ট আবার চেষ্টা করা একটি মডেল-রিকোয়েস্ট hook-এর মধ্য দিয়ে। শুধু ইতিহাস যে [`SystemPromptPart`][pydantic_ai.messages.SystemPromptPart] দিয়ে লেখা হয়েছিল সেগুলোই provider-এর নিজের system ফিল্ডে যায়; সেই অবস্থানে `'no_output'` feedback `<system>`-ট্যাগ করা user লেখা হিসেবে যায়, provider যা-ই হোক।

///

/// note | `RetryPromptPart` deprecated

দুই ধরনের retry আগে একটি [`RetryPromptPart`][pydantic_ai.messages.RetryPromptPart] ছিল, যা deprecated আর v3-এ সরিয়ে ফেলা হবে। একটি সংরক্ষিত ইতিহাস ওপরের দুটি অংশ হিসেবে লোড হয়, তাই ইতিহাস থেকে একটি retry পড়তে, বদলে `outcome='retried'`-সহ [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] বা `RetryFeedbackPart` মেলান। বিস্তারিত জানতে দেখুন [upgrade guide](changelog.md#deprecated-in-v2-to-be-removed-in-v3)।

///

## যা কখনো আবার চেষ্টা হয় না { #what-is-never-retried }

- **`prepare` callback।** একটি প্রতি-টুল `prepare=`, [`PrepareTools`](capabilities/prepare-tools.md), বা একটি [dynamic toolset](toolsets.md)-এর তোলা exception রান থেকে অপরিবর্তিত বেরিয়ে যায় — `ModelRetry`-সহ, যা সেখানে retry-তে রূপান্তরিত *হয় না*। একটি দফার জন্য একটি টুল লুকাতে, exception না তুলে callback থেকে `None` ফেরত দিন।
- **`ModelRetry` আর `ToolFailed` ছাড়া অন্য exception।** একটি টুল আর যা-ই তোলে তা retry না হয়ে রান থেকে বেরিয়ে যায় — *যদি না* একটি [capability](capabilities/overview.md) `on_tool_execute_error` বাস্তবায়ন করে, যা exception-টি আগে দেখে আর একটি বদলি টুল ফল ফেরত দিতে বা রান চালু রাখতে `ModelRetry` তুলতে পারে। [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] আর [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] দুটোর কোনোটিই নয়: এগুলো নিয়ন্ত্রণ-প্রবাহ, এরর নয়, আর বাইরে ছড়ানোর বদলে একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট দিয়ে রান শেষ করে — শুধু একটি [realtime session](realtime/overview.md)-এ ছাড়া, যা থামতে পারে না আর বদলে মডেলকে ব্যাখ্যা দিয়ে উত্তর দেয় যে session-এর সময় টুলটি শেষ করা যাবে না। পুরো টেবিল আছে [Ending a run from inside a tool](timeouts.md#ending-a-run-from-inside-a-tool)-এ।
- **পুরো এজেন্ট রান।** কিছুই আপনার হয়ে একটি এজেন্ট আবার চালায় না। একটি evaluation-এর সময় একটি পুরো task বা evaluator আবার চেষ্টা করতে [Pydantic Evals](evals.md)-এর নিজের `retry_task` আর `retry_evaluators` অপশন আছে — দেখুন [Retry Strategies](evals/how-to/retry-strategies.md)। সেগুলো এজেন্টের বাইরে বসে, তাই একটি আবার চেষ্টা করা task নতুন টুল আর আউটপুট বাজেট নিয়ে শুরু হয়।

/// check | সংক্ষেপে মনে রাখুন

* সাত স্তর: transport, provider SDK, durable execution, fallback, টুল, আউটপুট, মডেল-রিকোয়েস্ট hook — বাজেট আলাদা আর একটি আরেকটিকে গুণ করে।
* শুধু শেষ তিনটি মডেলকে দেখা যায় (প্রতিটি একটি নতুন রিকোয়েস্ট)।
* নেটওয়ার্ক/429/5xx-এ transport retry (`AsyncHTTPX2TenacityTransport` + `wait_retry_after`), আর তখন `max_retries=0`।
* `retries=3` বা `retries={'tools': 2, 'output': 1}`; `max_retries=N` মানে N+1 প্রচেষ্টা।
* ইতিহাসে টুল retry = `outcome='retried'`; লেখার-পথের retry = `RetryFeedbackPart`।
* `UsageLimits(request_limit=...)` শুধু মডেল রিকোয়েস্ট গোনে, নিচের স্তরগুলো নয়।

///
