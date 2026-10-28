# Google { #google }

/// note | এই পেজে যা শিখবেন

* `GoogleModel` দিয়ে Gemini মডেল: Gemini API (`google:`) আর Google Cloud (`google-cloud:`)।
* API key, service tier, নিজের HTTP client আর retry।
* ডকুমেন্ট/ছবি/অডিও/ভিডিও ইনপুট, ছবি তৈরি, thinking, safety, logprobs, Model Armor, context caching।
* Long decode আর stream বাতিল।

///

`GoogleModel` এমন একটি মডেল যা ভেতরে [`google-genai`](https://pypi.org/project/google-genai/) প্যাকেজ ব্যবহার করে
Gemini API আর Google Cloud (আগে Vertex AI নামে পরিচিত) দুটো দিয়েই Google-এর Gemini মডেলে পৌঁছায়।

দুটি provider সেই endpoint-গুলো মুড়ে রাখে:

- [`GoogleProvider`][pydantic_ai.providers.google.GoogleProvider] — Gemini API (Google AI Studio), `'google:'` উপসর্গের অধীনে।
- [`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider] — [Google Cloud](google-cloud.md) (আগে Vertex AI নামে পরিচিত), `'google-cloud:'` উপসর্গের অধীনে।

[`gateway/google:<model>`](../gateway.md) আর [`gateway/google-cloud:<model>`](../gateway.md) দুটোই Pydantic AI Gateway দিয়ে [`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider] ব্যবহার করে। শুধু-Gemini API সুবিধা, যেমন [`FileSearchTool`][pydantic_ai.native_tools.FileSearchTool], [`GoogleProvider`][pydantic_ai.providers.google.GoogleProvider] দিয়ে সরাসরি Gemini API চায়।

/// tip | কোনটি বাছবেন?

শেখা আর ছোট প্রজেক্টে `google:` (AI Studio-র একটি API key-ই যথেষ্ট)। প্রতিষ্ঠানের নিরাপত্তা, region নিয়ন্ত্রণ, Provisioned Throughput বা Model Armor দরকার হলে `google-cloud:`।

///

## ইনস্টল { #install }

`GoogleModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `google` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[google]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[google]"
```

///



## কনফিগারেশন { #configuration }

`GoogleModel` দিয়ে Google-এর Gemini মডেল ব্যবহার করতে পারেন তাদের [Gemini API](https://ai.google.dev/api/all-methods) (`generativelanguage.googleapis.com`) বা [Google Cloud](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) (`*-aiplatform.googleapis.com`, আগে Vertex AI নামে পরিচিত) দিয়ে।

### API key (Gemini API) { #api-key-gemini-api }

Gemini API দিয়ে Gemini ব্যবহার করতে, [aistudio.google.com](https://aistudio.google.com/apikey)-এ গিয়ে একটি API key তৈরি করুন।

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করুন:

```bash
export GOOGLE_API_KEY=your-api-key
```

তারপর নাম দিয়ে `GoogleModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash')
...
```

/// tip | পরামর্শ

কণ্ঠের এজেন্টের জন্য, বদলে একটি [realtime session](../realtime/gemini.md)-সহ একটি Gemini Live মডেল ব্যবহার করুন।

///

অথবা স্পষ্টভাবে provider তৈরি করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

provider = GoogleProvider(api_key='your-api-key')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

### Google Cloud (Enterprise) { #google-cloud-enterprise }

Gemini আর Claude-এ প্রবেশ, প্রমাণীকরণ আর Model Garden সেটআপের জন্য দেখুন [Google Cloud](google-cloud.md)।

- <span id="application-default-credentials"></span>[Application Default Credentials](google-cloud.md#application-default-credentials)
- <span id="service-account"></span>[Service Account](google-cloud.md#service-account)
- <span id="api-key"></span>[API Key](google-cloud.md#api-key)
- <span id="customizing-location-or-project"></span>[Location বা Project নিজের মতো করা](google-cloud.md#customizing-location-or-project)

### Service tier (`service_tier`, `google_cloud_service_tier`) { #service-tier-service_tier-google_cloud_service_tier }

একীভূত [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] ফিল্ড দুই Google উপ-ব্যবস্থাতেই কাজ করে, আর আরও সূক্ষ্ম Google Cloud routing নিয়ন্ত্রণের জন্য [`google_cloud_service_tier`][pydantic_ai.models.google.GoogleModelSettings.google_cloud_service_tier] আছে। দুটোই সেট থাকলে provider-নির্দিষ্ট ফিল্ড জেতে।

**Gemini API** — রিকোয়েস্টের `service_tier` ফিল্ড হিসেবে পাঠানো হয়:

| `service_tier` | Gemini API-তে যা পাঠানো হয় |
|---|---|
| `'auto'` | _(বাদ — সার্ভারের ডিফল্ট)_ |
| `'default'` | `'standard'` |
| `'flex'` | `'flex'` |
| `'priority'` | `'priority'` |

**Google Cloud** — HTTP routing header হিসেবে পাঠানো হয়; `'flex'` আর `'priority'` সবসময় **PT-with-spillover** রূপ বাছে, তাই [Provisioned Throughput](https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput/use-provisioned-throughput) (PT) থাকা গ্রাহকেরা আগে তাদের সংরক্ষিত ক্ষমতা ব্যবহার করতে থাকেন:

| `service_tier` | Google Cloud routing header | কার্যকর আচরণ |
|---|---|---|
| `'auto'` / `'default'` | _(কিছু না)_ | আগে PT, তারপর standard on-demand spillover |
| `'flex'` | `X-Vertex-AI-LLM-Shared-Request-Type: flex` | আগে PT, তারপর [Flex PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/flex-paygo) spillover |
| `'priority'` | `X-Vertex-AI-LLM-Shared-Request-Type: priority` | আগে PT, তারপর [Priority PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/priority-paygo) spillover |

PT পুরোপুরি এড়াতে (বা শুধু এটিই ব্যবহার করতে, বা অন্য যেকোনো Google Cloud-নির্দিষ্ট routing মিশ্রণে) সরাসরি [`google_cloud_service_tier`][pydantic_ai.models.google.GoogleModelSettings.google_cloud_service_tier] সেট করুন — একীভূত ফিল্ড ইচ্ছাকৃতভাবে নিরাপদ PT-with-spillover রূপে সীমিত।

**Google Cloud — routing মানের পুরো সেট**

পুরো [`google_cloud_service_tier`][pydantic_ai.models.google.GoogleModelSettings.google_cloud_service_tier] মান এই HTTP header-গুলোতে ম্যাপ হয়:

- `'pt_only'`: শুধু PT (`X-Vertex-AI-LLM-Request-Type: dedicated`)।
- `'pt_then_flex'`: quota অনুমতি দিলে PT, তারপর [Flex PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/flex-paygo) spillover (`X-Vertex-AI-LLM-Shared-Request-Type: flex`)।
- `'pt_then_priority'`: quota অনুমতি দিলে PT, তারপর [Priority PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/priority-paygo) spillover (`X-Vertex-AI-LLM-Shared-Request-Type: priority`)।
- `'on_demand'`: শুধু standard on-demand (`X-Vertex-AI-LLM-Request-Type: shared`)।
- `'flex_only'`: শুধু [Flex PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/flex-paygo) (`X-Vertex-AI-LLM-Request-Type: shared` আর `X-Vertex-AI-LLM-Shared-Request-Type: flex`)।
- `'priority_only'`: শুধু [Priority PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/priority-paygo) (`X-Vertex-AI-LLM-Request-Type: shared` আর `X-Vertex-AI-LLM-Shared-Request-Type: priority`)।

**উদাহরণ**

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(location='global')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)

result = agent.run_sync(
    'Hello!',
    model_settings=GoogleModelSettings(google_cloud_service_tier='pt_then_flex'),
)
```

`'pt_then_flex'`-কে যেকোনো [`GoogleCloudServiceTier`][pydantic_ai.models.google.GoogleCloudServiceTier] মান দিয়ে বদলান — যেমন [Priority PayGo](https://cloud.google.com/vertex-ai/generative-ai/docs/priority-paygo) spillover-এর জন্য `'pt_then_priority'`, বা PT পুরোপুরি এড়াতে `'flex_only'` / `'priority_only'`।

রিকোয়েস্টের পরে, কোন tier এটি সামলেছে দেখতে [`ModelResponse`][pydantic_ai.messages.ModelResponse]-এর `provider_details.get('traffic_type')` দেখুন (যেমন `ON_DEMAND_FLEX`, `ON_DEMAND_PRIORITY`), API ফেরত দিলে।

#### Model Garden { #model-garden }

দেখুন [Google Cloud Model Garden](google-cloud.md#model-garden)।

## নিজের HTTP client { #custom-http-client }

Google provider ডিফল্টভাবে `httpx2` ব্যবহার করে। transport-এর সেটিং নিয়ন্ত্রণ করতে একটি নিজের `httpx2.AsyncClient` দিতে পারেন:

```python
from httpx2 import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

custom_http_client = AsyncClient(timeout=30)
model = GoogleModel(
    'gemini-3.8-flash',
    provider=GoogleProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

Google provider যে client তৈরি করে, [Gateway](../gateway.md) দিয়েসহ, তার timeout 20 মিনিট, যা
[long decode](#long-decode)-এর দরকার। আপনার দেওয়া একটি client-এ, `google-genai` প্রতিটি রিকোয়েস্টের প্রতিটি ধাপে client-এর read timeout প্রয়োগ করে, বা না থাকলে 600
সেকেন্ড, তাই long-decode মডেলের জন্য এটিকে অন্তত 20 মিনিটের read timeout দিন।

Pydantic AI v2-এর সময় Google provider একটি পুরনো `httpx.AsyncClient`-ও নেয়, তবে একটি deprecation সতর্কবার্তা দেয়। নতুন কোডে `httpx2.AsyncClient` ব্যবহার করুন; পুরনো HTTPX client-এর সমর্থন Pydantic AI v3-এ সরিয়ে ফেলা হবে।

## HTTP retry { #http-retries }

/// note | মনে রাখুন

বেশিরভাগ ক্ষেত্রে, মডেল-নিরপেক্ষ [transport retries](../retries.md#transport-retries) পদ্ধতি ভালো, কারণ এটি সব provider-এ একইভাবে কাজ করে। নিচের `retry_options` আর্গুমেন্ট একটি Google-নির্দিষ্ট বিকল্প, যা retry `google-genai` SDK-র নিজের HTTP স্তরে ছেড়ে দেয়। এই SDK-স্তরের retry কোথায় বসে তা দেখুন retries গাইডের [The layers](../retries.md#the-layers)-এ, আর এজেন্টের নিজের retry বাজেটের সাথে কীভাবে গুণ হয় তা দেখুন [Retry multiplication](../retries.md#retry-multiplication)-এ।

///

ডিফল্টভাবে, `google-genai` SDK সাময়িক HTTP এররে ব্যর্থ রিকোয়েস্ট আবার চেষ্টা করে না। `GoogleProvider` বা `GoogleCloudProvider`-এর `retry_options` আর্গুমেন্টে একটি [`HttpRetryOptions`](https://googleapis.github.io/python-genai/genai.html#genai.types.HttpRetryOptions) instance দিয়ে retry চালু করতে পারেন:

```python
from google.genai.types import HttpRetryOptions

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

retry_options = HttpRetryOptions(
    attempts=4,
    initial_delay=1.0,
    max_delay=60.0,
    http_status_codes=[408, 429, 500, 502, 503, 504],
)
model = GoogleModel(
    'gemini-3.8-flash',
    provider=GoogleProvider(api_key='your-api-key', retry_options=retry_options),
)
agent = Agent(model)
...
```

এটি অপশনগুলো SDK-র [`HttpOptions.retry_options`](https://googleapis.github.io/python-genai/genai.html#genai.types.HttpOptions.retry_options)-এ পাঠায়। [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) একটি মডেল, এজেন্ট বা রানের প্রচেষ্টার সংখ্যা override করে, এখানে সেট করা দেরি আর status code রেখে, বা `retry_options` সেট না থাকলে SDK-র ডিফল্ট (এক সেকেন্ডের প্রথম দেরি; status 408, 429, 500, 502, 503 আর 504)। মান বাছাইয়ের নির্দেশনার জন্য দেখুন [Vertex AI retry strategy ডকুমেন্টেশন](https://cloud.google.com/vertex-ai/generative-ai/docs/retry-strategy)।

## ডকুমেন্ট, ছবি, অডিও আর ভিডিও ইনপুট { #document-image-audio-and-video-input }

`GoogleModel` multi-modal ইনপুট সমর্থন করে, ডকুমেন্ট, ছবি, অডিও আর ভিডিওসহ।

YouTube ভিডিওর URL সরাসরি Google মডেলে দেওয়া যায়:

```python title="youtube_input.py"
from pydantic_ai import Agent, VideoUrl
from pydantic_ai.models.google import GoogleModel

agent = Agent(GoogleModel('gemini-3.8-flash'))
result = agent.run_sync(
    [
        'What is this video about?',
        VideoUrl(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
    ]
)
print(result.output)
```

ফাইল [Files API](https://ai.google.dev/gemini-api/docs/files) দিয়ে আপলোড করে URL হিসেবে দেওয়া যায়:

```python title="file_upload.py"
from pydantic_ai import Agent, DocumentUrl
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

provider = GoogleProvider()
file = provider.client.files.upload(file='pydantic-ai-logo.png')
assert file.uri is not None

agent = Agent(GoogleModel('gemini-3.8-flash', provider=provider))
result = agent.run_sync(
    [
        'What company is this logo from?',
        DocumentUrl(url=file.uri, media_type=file.mime_type),
    ]
)
print(result.output)
```

আরও বিস্তারিত আর উদাহরণের জন্য দেখুন [ইনপুট ডকুমেন্টেশন](../input.md)।

### এজেন্টিক ভিডিও প্রক্রিয়াকরণ { #agentic-video-processing }

এজেন্টিক ভিডিও প্রক্রিয়াকরণ Gemini-কে চাহিদামতো ভিডিওর প্রাসঙ্গিক অংশ পরীক্ষা করতে দেয়। `media_processing` ছাড়া, Gemini তার ডিফল্ট স্থির প্রক্রিয়াকরণ ব্যবহার করে। [Google পরামর্শ দেয়](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding#choose_a_processing_mode) ছোট ক্লিপ, পুরো-ভিডিওর সারাংশ, দেরি-সংবেদনশীল প্রশ্ন, বা পুরো ক্লিপজুড়ে frame-স্তরের নির্ভুলতার জন্য স্থির প্রক্রিয়াকরণ; দীর্ঘ ভিডিও বা নির্দিষ্ট মুহূর্ত বা বিষয় খুঁজে বের করতে এজেন্টিক প্রক্রিয়াকরণ। কাজ অনুযায়ী প্রক্রিয়াকরণের mode বাছুন।

[এজেন্টিক ভিডিও প্রক্রিয়াকরণ সমর্থন করা Gemini মডেলে](https://ai.google.dev/gemini-api/docs/video-understanding#agentic-video-understanding), একটি ভিডিও ইনপুটে `media_processing` সেট করুন:

```python title="agentic_video.py"
from pydantic_ai import Agent, VideoUrl
from pydantic_ai.models.google import GoogleModel

agent = Agent(GoogleModel('gemini-3.7-flash'))
result = agent.run_sync(
    [
        'Summarize the important moments with timestamps.',
        VideoUrl(
            url='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            vendor_metadata={'media_processing': 'AGENTIC'},
        ),
    ]
)
print(result.output)
```

ভিডিওর উৎস আর প্রক্রিয়াকরণের mode স্বাধীন। একটি YouTube [`VideoUrl`][pydantic_ai.messages.VideoUrl] Gemini-র [সরাসরি YouTube ইনপুট](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding#youtube) ব্যবহার করে: Pydantic AI ভিডিও ডাউনলোড বা আপলোড না করে URL পাঠায়, এজেন্টিক প্রক্রিয়াকরণ চালু থাকলেও। Google YouTube URL-কে [সমর্থিত এজেন্টিক ভিডিও উৎসের](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/video-understanding#agentic-video-processing-support) তালিকায় রাখে।

Gemini Developer API-তে, প্রতিটি প্রক্রিয়াকরণ ধাপ উত্তরে `media_processing` নামের একটি [`NativeToolCallPart`][pydantic_ai.messages.NativeToolCallPart] আর [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart] হিসেবে দেখা দেয়। Vertex AI এই ধাপগুলোর জন্য শুধু-signature অংশ ফেরত দেয়, তাই সেগুলো বার্তার ইতিহাসে দেখা দেয় না।

/// note | পরবর্তী ভিডিও প্রক্রিয়াকরণ

Pydantic AI পরের রিকোয়েস্ট থেকে media-processing ধাপ বাদ দেয়, কারণ Gemini বর্তমানে সেগুলো প্রত্যাখ্যান করে। সাধারণ চূড়ান্ত উত্তর আর তার thought signature ইতিহাসে থাকে। সেই ইতিহাসে মূল ভিডিও থাকলে, পরের রিকোয়েস্ট এটি আবার প্রক্রিয়া করে আর বাড়তি ভিডিও-প্রক্রিয়াকরণ token খরচ করতে পারে।

///

## ছবি তৈরি { #image-generation }

Gemini API দিয়ে সরাসরি ছবি তৈরি আর রেফারেন্স-ছবি সম্পাদনার জন্য একটি `google:` ছবির মডেলসহ, বা একই মডেল Vertex AI-তে চালাতে একটি `google-cloud:` মডেলসহ [`ImageGenerator`][pydantic_ai.images.ImageGenerator] ব্যবহার করুন:

```python title="google_image_generation.py"
from pydantic_ai import ImageGenerator
from pydantic_ai.images.google import GoogleImageGenerationSettings

settings = GoogleImageGenerationSettings(
    google_image_config={'aspect_ratio': '1:1', 'image_size': '1K'}
)

gemini_api_generator = ImageGenerator('google:gemini-3.1-flash-lite-image', settings=settings)
vertex_generator = ImageGenerator('google-cloud:gemini-3.1-flash-image', settings=settings)
```

Vertex project আর location স্পষ্টভাবে সেট করতে একটি
[`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider] দিয়ে [`GoogleImageGenerationModel`][pydantic_ai.images.google.GoogleImageGenerationModel] তৈরি করুন।

সরাসরি adapter দুই API-তেই inline ছবি আর ডাউনলোডযোগ্য ছবির URL নেয়, আর বাছা transport নিজে যে রেফারেন্স হোস্ট করে তা ডাউনলোড না করে একটি `fileData` অংশ হিসেবে পাঠায়, ঠিক [`GoogleModel`][pydantic_ai.models.google.GoogleModel]-এর মতো: Gemini Developer API-তে সেটি একটি Files API URI, একটি [`UploadedFile`][pydantic_ai.messages.UploadedFile] বা একটি
`ImageUrl` হিসেবে; Vertex AI-তে, যেখানে Files API নেই, সেটি একটি Cloud Storage `gs://bucket/path` URI, একটি
`UploadedFile` হিসেবে যার `file_id` `gs://` দিয়ে শুরু, বা একটি `ImageUrl` যার URL তা দিয়ে শুরু আর যা `force_download` নয়।
Vertex অবজেক্টটি সার্ভারে পড়ে, তাই একটি বহু-মেগাবাইটের রেফারেন্স কখনো আপনার প্রসেসের মধ্য দিয়ে যায় না, আর কোনো
transport অন্যটির রেফারেন্স নেয় না: Vertex-এ একটি Files API id
[`UserError`][pydantic_ai.exceptions.UserError] তোলে। একটি মডেল কোন API-র সাথে কথা বলে তা পড়া হয়
client থেকে, provider-এর নাম থেকে নয়, তাই
[`GoogleProvider`][pydantic_ai.providers.google.GoogleProvider]-এ দেওয়া একটি Vertex-ভিত্তিক client Vertex হিসেবে ধরা হয়, আর
[`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider]-এ দেওয়া একটি Gemini Developer API client Files API সমর্থন রাখে। সাধারণ API আর জ্যামিতির আচরণের জন্য দেখুন
[image-generation guide](../image-generation.md)। adapter একটি শুধু-ছবির উত্তর চায়, কারণ [`ImageGenerator`][pydantic_ai.images.ImageGenerator] Gemini-র ঐচ্ছিক কথোপকথনের লেখা নয়, তৈরি ছবি ফেরত দেয়।

প্রতিটি তৈরি ছবি একটি শর্তহীন
[SynthID watermark](https://ai.google.dev/responsible/docs/safeguards/synthid) বহন করে। Gemini 3-এর ছবির মডেলগুলো thinking
মডেল: thinking সবসময় চালু আর বিল হয়, আর এর token ফলের `usage`-এ থাকে।

## মডেল সেটিং { #model-settings }

[`GoogleModelSettings`][pydantic_ai.models.google.GoogleModelSettings] দিয়ে মডেলের আচরণ নিজের মতো করতে পারেন:

```python
from google.genai.types import HarmBlockThreshold, HarmCategory

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

settings = GoogleModelSettings(
    temperature=0.2,
    max_tokens=1024,
    top_k=40,
    google_safety_settings=[
        {
            'category': HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            'threshold': HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    ]
)
model = GoogleModel('gemini-3.8-flash')
agent = Agent(model, model_settings=settings)
...
```

### Thinking কনফিগার করা { #configure-thinking }

thinking চালু করতে provider-নিরপেক্ষ [`Thinking`][pydantic_ai.capabilities.Thinking] capability ব্যবহার করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking

agent = Agent('google:gemini-3.8-flash', capabilities=[Thinking(effort='medium')])
...
```

উন্নত ব্যবহারের জন্য, [`GoogleModelSettings.google_thinking_config`][pydantic_ai.models.google.GoogleModelSettings.google_thinking_config] দিয়ে Google-এর নিজস্ব thinking config দিতে পারেন:

```python
from google.genai.types import ThinkingLevel

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

model = GoogleModel('gemini-3.8-flash')
model_settings = GoogleModelSettings(google_thinking_config={'include_thoughts': True, 'thinking_level': ThinkingLevel.MEDIUM})
agent = Agent(model, model_settings=model_settings)
...
```

Pydantic AI Google-এর নথিভুক্ত thinking টেবিল থেকে প্রতিটি মডেলের সমর্থিত স্তর নির্ধারণ করে আর চাওয়া effort-কে
সবচেয়ে কাছের সমর্থিত স্তরে মিলিয়ে দেয়। `gemini-3.1-flash-image` ব্যতিক্রম: Google এর জন্য `minimal, high`
[নথিভুক্ত করে](https://ai.google.dev/gemini-api/docs/image-generation), কিন্তু শুধু Gemini
API সেগুলো প্রয়োগ করে, তাই Pydantic AI সেই স্তরগুলো প্রয়োগ করে শুধু যখন client Gemini API-র সাথে কথা বলে, আর Vertex AI
পুরো মাপ রাখে। টেবিল ঢাকে না এমন একটি মডেল id-র জন্য, এর
স্তর ঘোষণা করুন [`GoogleModelProfile.google_thinking_levels`][pydantic_ai.profiles.google.GoogleModelProfile.google_thinking_levels] দিয়ে
(ডিফল্ট: পুরো মাপ); সমর্থিত নয় এমন effort সবচেয়ে কাছের সমর্থিত স্তরে নির্ধারিত হয়।

`gemini-4-argon` `low`, `medium` আর `high` স্তর সমর্থন করে, তাই `thinking=False` আর `'minimal'` নির্ধারিত হয়
`low`-তে। Google Cloud-এ এটি `google_thinking_config`-এ একটি `thinking_budget` একটি 400 এরর দিয়ে প্রত্যাখ্যান করে: বদলে
`thinking_level` ব্যবহার করুন।

`thinking=False` যেখানে মডেল অনুমতি দেয় সেখানে thinking বন্ধ করে। Pro মডেলগুলো এটি বন্ধ করতে পারে না, তাই বদলে তারা যত কম সম্ভব
তত thinking করে: Gemini 3 Pro মডেল তাদের সর্বনিম্ন thinking স্তর ব্যবহার করে (`gemini-3.1-pro-preview`-এ `low`),
আর Gemini 2.5 Pro তার সর্বনিম্ন `thinking_budget` 128 token ব্যবহার করে। কোনোটিই thought ফেরত চায় না।
Google Cloud-এ, `gemini-3.1-pro-preview` `thinking_budget=0` নেয়, যা Gemini API এর জন্য প্রত্যাখ্যান করে, তাই
সেখানে `thinking=False` `thinking_budget=0` পাঠায় আর মডেল thinking করে না।

একীভূত API-র জন্য দেখুন [Thinking](../capabilities/thinking.md), আর Google-এর নিজস্ব thinking কনফিগারেশনের জন্য [Gemini API ডক](https://ai.google.dev/gemini-api/docs/thinking)।

### Safety সেটিং { #safety-settings }

`google_safety_settings` ফিল্ড সেট করে safety সেটিং নিজের মতো করতে পারেন।

```python
from google.genai.types import HarmBlockThreshold, HarmCategory

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

model_settings = GoogleModelSettings(
    google_safety_settings=[
        {
            'category': HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            'threshold': HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
    ]
)
model = GoogleModel('gemini-3.8-flash')
agent = Agent(model, model_settings=model_settings)
...
```

safety সেটিং নিয়ে আরও জানতে দেখুন [Gemini API ডক](https://ai.google.dev/gemini-api/docs/safety-settings)।


### Logprobs { #logprobs }

[`GoogleModelSettings`][pydantic_ai.models.google.GoogleModelSettings]-এ `google_logprobs` আর `google_top_logprobs` সেট করে উত্তরে মডেল থেকে logprobs ফেরত পেতে পারেন।

এই সুবিধা শুধু stream নয় এমন রিকোয়েস্ট আর Google Cloud-এ সমর্থিত।

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

model_settings = GoogleModelSettings(
    google_logprobs=True, google_top_logprobs=2,
)

model = GoogleModel(
    model_name='gemini-3.8-flash',
    provider=GoogleCloudProvider(location='europe-west1'),
)
agent = Agent(model, model_settings=model_settings)

result = agent.run_sync('Your prompt here')
# Access logprobs from provider_details
provider_details = result.response.provider_details or {}
logprobs = provider_details.get('logprobs')
avg_logprobs = provider_details.get('avg_logprobs')
```

আরও তথ্যের জন্য দেখুন [Google Dev Blog](https://developers.googleblog.com/unlock-gemini-reasoning-with-logprobs-on-vertex-ai/)।

### Model Armor (শুধু Google Cloud) { #model-armor-google-cloud-only }

[Model Armor](https://docs.cloud.google.com/model-armor/overview) হলো একটি Google Cloud নিরাপত্তা সার্ভিস, যা prompt injection, jailbreaking আর সংবেদনশীল ডেটা ফাঁসের মতো ঝুঁকির জন্য prompt আর উত্তর পরীক্ষা করে।

[`GoogleModelSettings`][pydantic_ai.models.google.GoogleModelSettings]-এর `google_model_armor_config` দিয়ে এটি কনফিগার করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

model_settings = GoogleModelSettings(
    google_model_armor_config={
        'prompt_template_name': 'projects/my-project/locations/europe-west4/templates/prompt-template',
        'response_template_name': 'projects/my-project/locations/europe-west4/templates/response-template',
    }
)

model = GoogleModel(
    model_name='gemini-3.8-flash',
    provider=GoogleCloudProvider(location='europe-west4'),
)
agent = Agent(model, model_settings=model_settings)
...
```

Template আগে থেকে [Google Cloud Console](https://console.cloud.google.com/security/modelarmor)-এ তৈরি করতে হবে আর মডেল endpoint-এর একই region-এ থাকতে হবে। সমর্থিত location-এর জন্য দেখুন [Model Armor Vertex AI integration ডক](https://docs.cloud.google.com/model-armor/model-armor-vertex-integration)।

একটি prompt বা উত্তর আটকানো হলে, একটি [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] ওঠে।

মনে রাখবেন Model Armor পরীক্ষা — prompt আর উত্তর দুই template-ই — শুধু stream নয় এমন রিকোয়েস্টে (`agent.run()`) কাজ করে। streaming-এ (`agent.run_stream()`), Google Cloud Model Armor প্রয়োগ করে না: prompt পরীক্ষা হয় না আর উত্তরের লেখা পরীক্ষা ছাড়াই ফেরত আসে। streaming দরকার আর Model Armor সুরক্ষাও দরকার হলে, এজেন্ট ডাকার আগে [`google-cloud-modelarmor` SDK](https://pypi.org/project/google-cloud-modelarmor/) দিয়ে prompt আগে পরীক্ষা করুন।

### Context caching (`google_cached_content`) { #context-caching-google_cached_content }

আপনি একটি Gemini [cached content resource](https://ai.google.dev/gemini-api/docs/caching) তৈরি করলে, রিকোয়েস্ট-জুড়ে আবার ব্যবহার করতে এর resource নাম [`google_cached_content`][pydantic_ai.models.google.GoogleModelSettings.google_cached_content] দিয়ে দিন। (Gemini নিজে থেকেও prompt cache করে, তাই একীভূত [`ModelSettings.cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং, যা অন্য provider-এ রিকোয়েস্ট-পক্ষের caching কনফিগার করে, একটি Google রিকোয়েস্টে কিছুই যোগ করে না।)

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings

model_settings = GoogleModelSettings(
    google_cached_content='projects/p/locations/global/cachedContents/your-cache-id',
)

agent = Agent(GoogleModel('gemini-3.8-flash'), model_settings=model_settings)
...
```

/// warning | Cache করা ফিল্ড cache resource-এর

Cache resource `system_instruction`, `tools` আর `tool_config`-এর মালিক — `google_cached_content` সেট থাকলে Pydantic AI বাইরে যাওয়া রিকোয়েস্ট থেকে সেগুলো সরিয়ে দেয়, তাই cache করা রিকোয়েস্টে এজেন্টের নির্দেশনা আর নথিভুক্ত টুল উপেক্ষিত হয়। সরানোয় কোনো ফিল্ড বাদ পড়লেই একটি `UserWarning` দেওয়া হয়, তাই অমিলটি ধরা যায়।

///

/// details | একটি cached content resource তৈরি করা
    type: tip

Pydantic AI cache-ব্যবস্থাপনার API মোড়ায় না — ভেতরের [google-genai](https://googleapis.github.io/python-genai/) SDK দিয়ে resource তৈরি করুন, তারপর এর নাম `google_cached_content` দিয়ে দিন:

```python
from google.genai.types import Content, CreateCachedContentConfig, Part

from pydantic_ai.providers.google import GoogleProvider

provider = GoogleProvider(api_key='your-api-key')

cache = provider.client.caches.create(
    model='gemini-3.8-flash',
    config=CreateCachedContentConfig(
        system_instruction='You are a geography expert. Be concise.',
        contents=[Content(role='user', parts=[Part(text='...long context to cache...')])],
        ttl='3600s',
    ),
)
print(cache.name)
#> cachedContents/abc123...
```

Cache-এর একটি ন্যূনতম আকার আছে (Gemini 2.5 সিরিজের মডেলে প্রায় 2048 token, Gemini 3 সিরিজে প্রায় 4096) আর একটি TTL — বর্তমান সীমা, দাম আর `list` / `update` / `delete` কাজের জন্য দেখুন [Gemini caching ডক](https://ai.google.dev/gemini-api/docs/caching)।

///

## Long decode { #long-decode }

`gemini-4-argon` প্রতিটি রিকোয়েস্টের আউটপুট সীমিত রাখে; Google-এর
[long decode ডক](https://ai.google.dev/gemini-api/docs/generate-content/long-decode) সীমা আর ডিফল্ট দেয়।
[`max_tokens`][pydantic_ai.settings.ModelSettings.max_tokens] সীমার ওপরে হলে, সীমায় পৌঁছানো একটি রিকোয়েস্ট একটি
continuation token ফেরত দেয়, আর `google-genai` SDK সেটি থেকে আরেকটি রিকোয়েস্টে উত্তর চালিয়ে যায়, যতক্ষণ না উত্তর
শেষ হয় বা `max_tokens` খরচ হয়ে যায়:

```python
from pydantic_ai import Agent

agent = Agent('google:gemini-4-argon', model_settings={'max_tokens': 100_000})
result = agent.run_sync('Write the complete specification.')
print(result.output)
```

SDK রিকোয়েস্টগুলো একটি [`ModelResponse`][pydantic_ai.messages.ModelResponse]-এ মেলায়, তাই Pydantic AI-এর কাছে একটি long
decode একটি মডেল রিকোয়েস্ট:

- এর usage রিকোয়েস্টগুলোর যোগফল, যা Google বিল করে। প্রতিটি রিকোয়েস্টের ইনপুট এ পর্যন্ত আউটপুট আবার
  গোনে।
- [Usage limits](../agent.md#usage-limits) এটিকে একটি রিকোয়েস্ট হিসেবে গোনে, আর stream নয় এমন একটি রান প্রতিটি রিকোয়েস্ট শেষ হলে একবার তার token
  সীমা পরীক্ষা করে: `max_tokens`-ই একটি long decode সীমিত করে।
  [`per_request_input_tokens_limit`][pydantic_ai.usage.UsageLimits.per_request_input_tokens_limit] পরীক্ষা হয়
  প্রথম রিকোয়েস্টের input token-এর বিপরীতে।
- Timeout প্রতিটি রিকোয়েস্টে প্রযোজ্য। Google provider তাদের client তৈরি করে Google-এর পরামর্শ দেওয়া 20-মিনিটের read timeout দিয়ে।
- পরের একটি রিকোয়েস্ট ব্যর্থ হলে, মডেল রিকোয়েস্ট ব্যর্থ হয়। stream নয় এমন একটি রান আগের রিকোয়েস্টের আউটপুট হারায়,
  যা ইতিমধ্যে বিল হয়েছে। একটি stream করা রান যা stream করেছে তা রাখে
  [`state='interrupted'`][pydantic_ai.messages.ModelResponse.state]-সহ একটি উত্তর হিসেবে, যা শেষ হওয়া রিকোয়েস্টগুলোর usage বহন করে, যা
  [`capture_run_messages()`][pydantic_ai.capture_run_messages] ফেরত দেয়।
- SDK একটি ছিন্ন stream তার শেষ continuation token থেকে আবার শুরু করে। সেই token-এর পরে আউটপুট stream হয়ে থাকলে,
  মডেল রিকোয়েস্ট বদলে ওপরের মতো ব্যর্থ হয়, কারণ আবার শুরু করা রিকোয়েস্ট সেই আউটপুট পুনরাবৃত্তি করত।
- [Temporal](../durable_execution/temporal.md#activity-configuration)-এ, পুরো long decode একটি মডেল
  রিকোয়েস্ট activity-তে চলে, তাই এর `start_to_close_timeout` প্রতিটি রিকোয়েস্ট ঢাকতে হবে। একটি আবার-চেষ্টা করা activity উত্তর
  নতুন করে শুরু করে। মেলানো উত্তর activity-র একটি ফল, তাই খুব দীর্ঘ একটি আউটপুট Temporal-এর
  [payload limit](../durable_execution/temporal.md#large-payloads) ছাড়াতে পারে।

`max_tokens` ছাড়া, Google-এর ডিফল্ট আউটপুট সীমা প্রযোজ্য, আর এতে পৌঁছানো একটি উত্তর শেষ হয়
`finish_reason='length'` দিয়ে।

[Google Cloud](google-cloud.md)-এ, `gemini-4-argon` পরিবেশিত হয় `global` location আর `us` ও `eu`
multi-region-এ, ডিফল্ট `us-central1`-এর মতো একক region-এ নয়: provider-এর
[`location`](google-cloud.md#customizing-location-or-project) হিসেবে এগুলোর একটি দিন।

## Stream বাতিল { #streaming-cancellation }

/// note | Transport বাতিল

[`cancel()`][pydantic_ai.result.StreamedRunResult.cancel] নিরাপদে একটি সক্রিয় লোকাল stream-টানা বাধা দেয়, আরেকটি task-এ চলা একটিসহ। `google-genai` SDK কোনো নথিভুক্ত প্রতি-stream transport handle দেয় না, তাই ফেরত আসা iterator বন্ধ করলে সাথে সাথে HTTP বন্ধের নিশ্চয়তা নেই বা দূরের তৈরি কখন থামে আর বিলিং কখন শেষ হয় তা বোঝা যায় না। দেখুন [googleapis/python-genai#2425](https://github.com/googleapis/python-genai/issues/2425)।

///

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[google]"`, `GOOGLE_API_KEY`, তারপর `Agent('google:gemini-3.8-flash')`।
* Enterprise/Vertex-এ `google-cloud:` উপসর্গ আর `GoogleCloudProvider`।
* SDK নিজে retry করে না; transport retry বা `retry_options` দিন।
* YouTube URL সরাসরি দেওয়া যায়; Thinking capability বা `google_thinking_config` দিয়ে thinking।
* Model Armor আর logprobs শুধু stream নয় এমন রিকোয়েস্টে; `google_cached_content` দিলে নির্দেশনা/টুল উপেক্ষিত।

///
