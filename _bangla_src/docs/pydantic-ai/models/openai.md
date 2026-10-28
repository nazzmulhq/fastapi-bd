# OpenAI { #openai }

/// note | এই পেজে যা শিখবেন

* OpenAI মডেল ইনস্টল, API key সেট আর `openai:` (Responses API) বনাম `openai-chat:` (Chat Completions)।
* provider আর নিজের client কনফিগার করা, ছবি তৈরি, structured output-এর schema।
* মডেল সেটিং: service tier, prompt caching, moderation।
* Responses API-র সুবিধা: reasoning, নেটিভ টুল, আগের উত্তর থেকে চালিয়ে যাওয়া, compaction, background mode; আর Decisions API।

///

## ইনস্টল { #install }

OpenAI মডেল বা OpenAI-সামঞ্জস্যপূর্ণ API ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[openai]"
```

///


## কনফিগারেশন { #configuration }

OpenAI API দিয়ে OpenAI মডেল ব্যবহার করতে, [platform.openai.com](https://platform.openai.com/)-এ যান আর API key তৈরির জায়গা খুঁজে না পাওয়া পর্যন্ত এগোতে থাকুন।

/// tip | পরামর্শ

API key-র বদলে আপনার [ChatGPT/Codex subscription](openai-codex.md)-ও ব্যবহার করতে পারেন: `openai-codex:` উপসর্গ অফিসিয়াল Codex CLI-র মতো একই OAuth প্রবাহ দিয়ে Codex backend-এ প্রমাণীকরণ করে। আপনার open-source বা লোকাল অ্যাপের ব্যবহারকারীদের তাদের নিজের ChatGPT প্ল্যান ব্যবহার করতে দিতে, [Sign in with ChatGPT](openai-chatgpt.md) ব্যবহার করুন।

///

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export OPENAI_API_KEY='your-api-key'
```

শুধু `'openai:'` উপসর্গ [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel]-এ নির্ধারিত হয়, যা আধুনিক [Responses API](https://platform.openai.com/docs/api-reference/responses) ব্যবহার করে।

```python
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')
...
```

/// tip | পরামর্শ

কণ্ঠের এজেন্টের জন্য, বদলে একটি [realtime session](../realtime/openai.md)-সহ একটি GPT-Live বা `gpt-realtime` মডেল ব্যবহার করুন।

///

বদলে পুরনো [Chat Completions API](https://platform.openai.com/docs/api-reference/chat)-এ আটকে থাকতে, `'openai-chat:'` উপসর্গ ব্যবহার করুন, যা [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel]-এ নির্ধারিত হয়।
`gpt-6-sol` আর `gpt-6-luna`-র জন্য, Chat Completions function calling সমর্থন করে শুধু `openai_reasoning_effort='none'` হলে। reasoning আর টুল একসাথে দরকার হলে Responses API ব্যবহার করুন। `gpt-6.1-sol` আর `gpt-6-astra` `'none'` নেয় না, তাই এগুলোর সাথে function calling-এর জন্য Responses API ব্যবহার করুন।

/// info | কোনটি বাছবেন?

* `openai:` → Responses API (ডিফল্ট, প্রস্তাবিত): reasoning + টুল একসাথে, নেটিভ টুল, compaction, background mode।
* `openai-chat:` → Chat Completions API: পুরনো কোড বা OpenAI-সামঞ্জস্যপূর্ণ সার্ভারের সাথে মেলাতে।

///

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model)
...
```

ডিফল্টভাবে, মডেলটি `base_url` `https://api.openai.com/v1` সেট করা `OpenAIProvider` ব্যবহার করে।

## Provider কনফিগার করা { #configure-the-provider }

provider-কে কোডে প্যারামিটার দিতে চাইলে, প্রোগ্রাম দিয়ে
[OpenAIProvider][pydantic_ai.providers.openai.OpenAIProvider] তৈরি করে মডেলে দিতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIResponsesModel('gpt-6.1-sol', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model)
...
```

## নিজের OpenAI client { #custom-openai-client }

`OpenAIProvider` `openai_client` প্যারামিটার দিয়ে একটি নিজের `AsyncOpenAI` client-ও নেয়, তাই [OpenAI API ডক](https://platform.openai.com/docs/api-reference)-এ সংজ্ঞায়িত `organization`, `project`, `base_url` ইত্যাদি নিজের মতো করতে পারেন।

Client এজেন্টের retry বাজেট থেকে স্বাধীনভাবে নিজেই ব্যর্থ রিকোয়েস্ট আবার চেষ্টা করে। এর ডিফল্ট `max_retries=2`, তাই একটি মডেল রিকোয়েস্ট নেটওয়ার্কে সর্বোচ্চ তিনবার পৌঁছাতে পারে। এটি `x-should-retry` উত্তর header মানে; সেই header ছাড়া, এটি status 408, 409, 429 বা 5xx, আর timeout ও সংযোগ এরর আবার চেষ্টা করে, কিন্তু 400 বা 401-এর মতো অন্য 4xx উত্তর নয়। retry নীতি শুধু আপনার transport-এ রাখতে `max_retries=0` সেট করুন, বা client নিজে না বানিয়ে একটি মডেল, এজেন্ট বা রানের সংখ্যা বদলাতে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) সেট করুন। স্তরগুলো কীভাবে একটির ওপর আরেকটি চাপে তা দেখুন [Retry multiplication](../retries.md#retry-multiplication)-এ।

```python title="custom_openai_client.py"
from openai import AsyncOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncOpenAI(max_retries=3)
model = OpenAIResponsesModel('gpt-6.1-sol', provider=OpenAIProvider(openai_client=client))
agent = Agent(model)
...
```

Azure OpenAI API ব্যবহার করতে [`AsyncAzureOpenAI`](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoints) client-ও
ব্যবহার করতে পারেন। মনে রাখবেন `AsyncAzureOpenAI` হলো `AsyncOpenAI`-এর একটি subclass।

```python
from openai import AsyncAzureOpenAI

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

client = AsyncAzureOpenAI(
    azure_endpoint='...',
    api_version='2024-07-01-preview',
    api_key='your-api-key',
)

model = OpenAIChatModel(
    'gpt-6.1-sol',
    provider=OpenAIProvider(openai_client=client),
)
agent = Agent(model)
...
```

## ছবি তৈরি { #image-generation }

সরাসরি ছবি তৈরি আর রেফারেন্স-ছবি সম্পাদনার জন্য একটি `openai:` ছবির মডেলসহ [`ImageGenerator`][pydantic_ai.images.ImageGenerator] ব্যবহার করুন। এটি একটি কথোপকথনের Responses মডেলের বদলে OpenAI-এর Images API ব্যবহার করে:

```python title="openai_image_generation.py"
from pydantic_ai import ImageGenerator
from pydantic_ai.images.openai import OpenAIImageGenerationSettings

generator = ImageGenerator(
    'openai:gpt-image-2',
    settings=OpenAIImageGenerationSettings(
        dimensions=(1280, 720),
        openai_quality='low',
        openai_output_format='jpeg',
    ),
)
```

OpenAI [`BinaryImage`][pydantic_ai.messages.BinaryImage] আর
[`ImageUrl`][pydantic_ai.messages.ImageUrl] রেফারেন্স ইনপুট নেয়। এর ছবি-সম্পাদনার endpoint-এ ফাইলের বিষয়বস্তু লাগে আর একটি
[`UploadedFile`][pydantic_ai.messages.UploadedFile] provider ফাইল ID নেয় না। স্বচ্ছ পটভূমির সমর্থন মডেলভেদে আলাদা
আর এর জন্য PNG বা WebP আউটপুট লাগে। provider-নির্দিষ্ট সেটিং OpenAI-তে পাঠানো হয়, যাতে নতুন সমর্থিত মান
পুরনো client-পক্ষের পরীক্ষায় আটকে না যায়। তৈরি, সম্পাদনা, জ্যামিতি আর স্বাভাবিক করা সেটিংয়ের জন্য দেখুন [image-generation guide](../image-generation.md)।

GPT Image মডেলের জন্য একটি paid usage tier-এ যাচাই করা প্রতিষ্ঠান লাগে: যাচাই না করা প্রতিষ্ঠানে কিছু তৈরি হওয়ার আগেই প্রতিটি রিকোয়েস্ট
একটি rate-limit এরর দিয়ে ব্যর্থ হয়। জটিল prompt প্রক্রিয়া হতে দুই মিনিট পর্যন্ত লাগতে পারে।

## Structured output-এর schema { #structured-output-schemas }

[`OpenAIProvider`][pydantic_ai.providers.openai.OpenAIProvider] বা
[`OpenAIChatGPTProvider`][pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTProvider] (যা একই সর্বজনীন
OpenAI API দেয়)-এর সাথে ব্যবহৃত সাধারণ, fine-tune না করা মডেলে, `min_length` বা `max_length`-সহ স্ট্রিং ফিল্ড strict structured output-এ সেই সীমা রাখে। Fine-tune করা
`ft:` মডেল একটি রক্ষণশীল schema transformer ব্যবহার করে, কারণ OpenAI সেই মডেলগুলোর জন্য বাড়তি Structured Outputs সীমাবদ্ধতা
নথিভুক্ত করে।
এখানে বর্ণিত strict tuple আর স্ট্রিং-সীমার সমর্থন Codex backend-এর বিপরীতে যাচাই করা হয়নি, তাই
[`OpenAICodexProvider`][pydantic_ai.providers.openai_codex.OpenAICodexProvider] তার বিদ্যমান schema সামলানো রাখে।

`tuple[int]`-এর মতো এক-আইটেমের একটি tuple strict থাকতে পারে: এর একক অনুমোদিত উপাদান একটি টাইপ করা array
`items` schema হিসেবে প্রকাশ হয়। `tuple[int, int, int, int]`-এর মতো বহু-আইটেমের নির্দিষ্ট tuple এখনো `prefixItems` ব্যবহার করে; OpenAI strict mode
সেই tuple schema সমর্থন করে না, তাই অনুমিত strictness non-strict mode-এ ফিরে যায় আর স্পষ্টভাবে strict
[`ToolOutput`][pydantic_ai.output.ToolOutput] বা [`NativeOutput`][pydantic_ai.output.NativeOutput] একটি
[`UserError`][pydantic_ai.exceptions.UserError] তোলে। একই নিয়ম [strict mode](../tools-advanced.md#strict-mode)-এ ফাংশন টুলের প্যারামিটারে
প্রযোজ্য। strict mode-এ একটি নির্দিষ্ট আইটেম সংখ্যা রাখতে, একটি সীমিত list ব্যবহার করুন:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    coordinates: Annotated[list[int], Field(min_length=4, max_length=4)]
```

## মডেল সেটিং { #model-settings }

[`OpenAIResponsesModelSettings`][pydantic_ai.models.openai.OpenAIResponsesModelSettings] দিয়ে মডেলের আচরণ নিজের মতো করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(
    openai_reasoning_effort='low',
    service_tier='flex',
)
agent = Agent(model, model_settings=settings)
...
```

### Service tier { #service-tier }

দেরি আর খরচের মধ্যে ভারসাম্য করতে OpenAI [service tier](https://platform.openai.com/docs/api-reference/responses/create#responses-create-service_tier) নিয়ন্ত্রণ সমর্থন করে।
একীভূত [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] ফিল্ড বা provider-নির্দিষ্ট [`openai_service_tier`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_service_tier] ফিল্ড ব্যবহার করতে পারেন। দুটোই `'auto'`, `'default'`, `'flex'` আর `'priority'` নেয়, অপরিবর্তিত পাঠানো হয়। দুটোই সেট থাকলে `openai_service_tier` একীভূত ফিল্ডের ওপর অগ্রাধিকার পায়।

OpenAI চাওয়াটির চেয়ে ভিন্ন একটি tier-এ রিকোয়েস্ট সামলাতে পারে, যেমন একটি `'priority'` রিকোয়েস্ট নামিয়ে দিলে। যে tier আসলে রিকোয়েস্টটি সামলেছে তা রাখা হয় `ModelResponse.provider_details['service_tier']`-এ, আর রিকোয়েস্টের খরচ সেই tier-এর দামে হিসাব হয়।

### Prompt caching { #prompt-caching }

OpenAI সব সমর্থিত মডেলে [নিজে থেকে prompt cache করে](https://developers.openai.com/api/docs/guides/prompt-caching#how-caching-works): কোনো সেটিং বা চিহ্ন লাগে না, আর cache hit [`cache_read_tokens`][pydantic_ai.usage.RequestUsage.cache_read_tokens]-এর মতো স্বাভাবিক usage ফিল্ডে জানানো হয়। GPT-5.6 আর পরেরগুলোতে, একীভূত [`ModelSettings.cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং (বা [`Caching`][pydantic_ai.capabilities.Caching] capability) স্পষ্ট caching-ও কনফিগার করে: `cache=True` পাঠায় `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` আর [`openai_cache_instructions`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_cache_instructions] চালু করে (নিচে বর্ণিত), যাতে আলাদা কথোপকথন cache করা নির্দেশনা ভাগ করে। OpenAI শুধু `'30m'` TTL নেয়, তাই চাওয়া যেকোনো ধরে রাখার সময় এতে মিলে যায়। নিজে `openai_prompt_cache_options` বা `openai_cache_instructions` সেট করলে তা একীভূত সেটিংয়ের ওপর অগ্রাধিকার পায়। খরচের ভারসাম্য, Pydantic AI-এর prefix-স্থিতিশীলতার নিশ্চয়তা আর cache-এর দক্ষতা কীভাবে পর্যবেক্ষণ করবেন তা দেখুন [Caching](../capabilities/caching.md)-এ।

/// tip | উদাহরণ দিয়ে বুঝি

Prompt cache হলো দোকানদারের মনে রাখা: একই খদ্দের বারবার একই লম্বা ফর্দ (system prompt, নির্দেশনা, আগের কথোপকথন) দিলে, দোকানদার প্রথমবার পড়ে মনে রাখেন, পরের বার শুধু নতুন অংশটুকু পড়েন। ফলে দ্রুত আর সস্তা হয়। কিন্তু ফর্দের শুরুতে একটি শব্দ বদলালে পুরোটা আবার পড়তে হয় — তাই শুরুর অংশ (prefix) স্থির রাখা জরুরি।

///

একটি cache করা prefix কতক্ষণ টেকে তা নির্ভর করে কার্যকর [ধরে রাখার নীতির](https://developers.openai.com/api/docs/guides/prompt-caching#cache-lifetime) ওপর: `in_memory` সাধারণত 5–10 মিনিট নিষ্ক্রিয়তা পর্যন্ত রাখে, সর্বোচ্চ এক ঘণ্টা, অথচ `24h` এক দিন পর্যন্ত রাখতে পারে। GPT-5.6-এর আগের মডেলে, একীভূত সেটিং রিকোয়েস্টে কিছুই যোগ করে না, আর ডিফল্ট ধরে রাখার সময় আপনার প্রতিষ্ঠানের data-retention কনফিগারেশন মানে — zero data retention ছাড়া `24h`, সহ `in_memory`। [`openai_prompt_cache_retention`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_prompt_cache_retention] এটি প্রতি রিকোয়েস্টে সেট করে:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.5')
settings = OpenAIResponsesModelSettings(openai_prompt_cache_retention='24h')
agent = Agent(model, model_settings=settings)
...
```

GPT-5.6 আর পরেরগুলোর জন্য, OpenAI `prompt_cache_retention` deprecated করে [`openai_prompt_cache_options`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_options]-এর `ttl`-এর পক্ষে, যা সর্বোচ্চ নয়, একটি ন্যূনতম আয়ু সেট করে: একটি cache করা prefix তার সর্বশেষ লেখা বা পুনর্ব্যবহারের পরে 30 মিনিট পুনর্ব্যবহারের যোগ্য থাকে, যদিও OpenAI এটি আরও বেশি সময় রাখতে পারে।

GPT-5.6 আর GPT-6 মডেল Responses আর Chat Completions দুই API-তেই OpenAI-এর [implicit আর explicit prompt cache breakpoint](https://developers.openai.com/api/docs/guides/prompt-caching#choose-a-caching-mode) সমর্থন করে। OpenAI ডিফল্টভাবে একটি implicit breakpoint তৈরি করে। cache-যোগ্য prefix সূক্ষ্মভাবে নিয়ন্ত্রণ করতে, যে user বিষয়বস্তু ব্লকে prefix শেষ হওয়া উচিত তার পরে [`CachePoint`][pydantic_ai.messages.CachePoint] বসান:

```python
from pydantic_ai import Agent, CachePoint
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

settings = OpenAIResponsesModelSettings(
    openai_prompt_cache_key='product-docs-v1',
    openai_prompt_cache_options={'mode': 'explicit', 'ttl': '30m'},
)
agent = Agent('openai:gpt-5.6-sol', model_settings=settings)

result = agent.run_sync([
    'Long-lived reference material...',
    CachePoint(),
    'Answer using the reference material.',
])
```

একটি user বার্তা খোলা একটি `CachePoint` বদলে আগের বার্তার শেষ চিহ্নিত করে, যেমন তার আগের টুল ফল, Anthropic আর Bedrock-এর মতোই। Responses API-তে, assistant আউটপুট একটি breakpoint বহন করতে পারে না, তাই এটি বদলে সবচেয়ে কাছের আগের ইনপুটে যায়। কথোপকথনে আগের কোনো বিষয়বস্তু ছাড়া একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

একীভূত সেটিং ছাড়া নির্দেশনা cache করতে, [`openai_cache_instructions`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_cache_instructions] সেট করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

settings = OpenAIResponsesModelSettings(
    openai_prompt_cache_key='support-app:kb-v1',
    openai_cache_instructions=True,
)
agent = Agent(
    'openai:gpt-5.6-sol',
    instructions='Long-lived support policies...',
    model_settings=settings,
)

result = agent.run_sync('Where is order 1234?')
```

breakpoint শেষ স্থির নির্দেশনার পরে বসানো হয়, তাই গতিশীল [নির্দেশনা](../agent.md#instructions) (`@agent.instructions` ফাংশন বা [toolset](../toolsets.md) থেকে) cache করা prefix-এর বাইরে থাকে আর বদলালে সেটি অবৈধ করে না। তবে এগুলো তাদের পরের cache করা কথোপকথন অবৈধ করে, তাই কথোপকথনের মাঝে বদলানো নির্দেশনার জন্য [`on_change='append'`](../agent.md#appending-instruction-changes) ব্যবহার করুন, আর [অবিশ্বস্ত লেখা নির্দেশনার বাইরে রাখুন](../agent.md#untrusted-instruction-text)। কোনো স্থির নির্দেশনা না থাকলে, এটি বদলে শেষ [system prompt](../agent.md#system-prompts)-এ যায়, যা সমান স্থির। `openai_prompt_cache_options` তার ডিফল্ট `mode='implicit'`-এ রাখুন যাতে OpenAI বাড়তে থাকা কথোপকথনও cache করে।

Responses API-তে শীর্ষ-স্তরের `instructions` ফিল্ড একটি breakpoint বহন করতে পারে না, তাই নির্দেশনা বদলে শুরুর ইনপুট বার্তা হিসেবে পাঠানো হয়। যেহেতু একটি সংরক্ষিত উত্তর তার ইনপুট রাখে আর যে রিকোয়েস্ট তাকে চালিয়ে যায় তাতে আবার চালায়, এর কিছু সীমা আছে:

- এটি শুধু সেই রিকোয়েস্টে ঘটে যা সার্ভার-পক্ষের অবস্থা চালিয়ে যায় না। [`openai_previous_response_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id] বা [`openai_conversation_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id] সেট থাকলে, বা ইতিহাস [compact](../capabilities/compaction.md) করা হলে, সেটিংটি নির্দেশনা যেখানে অন্যথায় যেত সেখানেই রাখে (সাধারণত শীর্ষ-স্তরের ফিল্ড) আর কোনো breakpoint যোগ করে না।
- `openai_previous_response_id='auto'`-এ, এর মধ্যে প্রথম রিকোয়েস্টও পড়ে, যার চালিয়ে যাওয়ার মতো কোনো উত্তর এখনো নেই। অন্যথায় এর সরানো নির্দেশনা পরের প্রতিটি রিকোয়েস্টের নিজের [নির্দেশনার](../agent.md#instructions) পাশে আবার চলত, যা একটি ভিন্ন এজেন্টের হতে পারে।
- `openai_cache_instructions` দিয়ে (যা `cache=True` চালু করে) তৈরি একটি উত্তর পরে `openai_previous_response_id` দিয়ে চালিয়ে যাবেন না, কারণ এর সংরক্ষিত ইনপুটে যে নির্দেশনা দিয়ে এটি তৈরি হয়েছিল তা থাকে।
- সার্ভার-পক্ষের অবস্থা চালিয়ে যাওয়া রিকোয়েস্ট ডিফল্ট `mode='implicit'`-এ তবুও OpenAI-এর implicit breakpoint পায়। তারা যা হারায় তা হলো নির্দেশনার শেষে একটি breakpoint, যা আলাদা কথোপকথনকে cache করা নির্দেশনা ভাগ করতে দেয়। এজেন্ট রান ডিফল্টভাবে পুরো বার্তার ইতিহাস পাঠায়, তাই এটি শুধু সার্ভার-পক্ষের অবস্থা বেছে নেওয়া রানে প্রভাব ফেলে।

Caching-এর জন্য অন্তত 1024 token-এর prefix লাগে; ছোট prefix স্পষ্টভাবে চিহ্নিত হলেও cache হয় না। `mode='implicit'`-এ (ডিফল্ট), OpenAI একটি implicit আর সর্বোচ্চ তিনটি explicit breakpoint লিখতে পারে। `mode='explicit'`-এ, এটি সর্বোচ্চ চারটি explicit breakpoint লিখতে পারে আর কোনো implicit নয়। একটি রিকোয়েস্ট এর চেয়ে বেশি breakpoint সেট করলে, OpenAI শুধু শেষ চারটি লেখে, আর নির্দেশনার breakpoint একটি রিকোয়েস্টে সবচেয়ে আগেরটি, তাই সেটিই প্রথম বাদ পড়ে। TTL রিকোয়েস্ট-জুড়ে: OpenAI বর্তমানে শুধু `'30m'` নেয়, [`openai_prompt_cache_options`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_options] দিয়ে কনফিগার করা, আর সাধারণ প্রতি-চিহ্নের [`CachePoint.ttl`][pydantic_ai.messages.CachePoint.ttl] মান উপেক্ষা করে।

GPT-5.6 আর পরেরগুলোতে, OpenAI রিকোয়েস্ট নিজে থেকে cache-এ পাঠায়, তাই cache hit পেতে [`openai_prompt_cache_key`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_key] লাগে না। ভিন্ন key-র রিকোয়েস্ট একে অপরের cache করা prefix আবার ব্যবহার করে না, তাই প্রতিটি নতুন key আবার cache লেখার দাম দেয়। key সেট না করে রাখুন যাতে সব রিকোয়েস্ট একটি সাধারণ prefix ভাগ করে, বা আলাদাভাবে cache করতে চাওয়া প্রতিটি দলের জন্য একটি স্থির key সেট করুন, যেমন একজন গ্রাহক। প্রতি রিকোয়েস্ট বা কথোপকথনে নতুন key সেট করবেন না। আগের মডেলে, একটি স্থির key OpenAI-কে একই prefix-এর রিকোয়েস্ট একই cache-এ পাঠাতে সাহায্য করে; OpenAI প্রতি key-তে মিনিটে প্রায় 15টি রিকোয়েস্টের পরামর্শ দেয়।

OpenAI prompt cache লেখা জানালে, Pydantic AI সেগুলো [`result.usage.cache_write_tokens`][pydantic_ai.usage.RunUsage.cache_write_tokens] হিসেবে দেয়। Cache পড়া পাওয়া যায় [`result.usage.cache_read_tokens`][pydantic_ai.usage.RunUsage.cache_read_tokens] হিসেবে। GPT-5.6 আর পরের মডেল পরিবারে, OpenAI cache লেখার বিল করে cache-ছাড়া input token-এর হারের 1.25 গুণে।

cache miss ব্যাখ্যা করতে সাহায্য করতে, Pydantic AI OpenAI API-তে নিজেই (Azure, OpenRouter বা অন্য OpenAI-সামঞ্জস্যপূর্ণ provider নয়) Responses API-সহ GPT-5.6 আর পরের মডেলে OpenAI-এর [prompt cache diagnostics](https://developers.openai.com/api/docs/guides/prompt-caching/diagnostics) চায়: প্রতিটি রিকোয়েস্ট নিজেকে বার্তার ইতিহাসের সবচেয়ে সাম্প্রতিক OpenAI উত্তরের সাথে তুলনা করে, যদি না সেই উত্তর [message compaction](#message-compaction) থেকে আসে। ফলটি উত্তরের [`provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এ `'prompt_cache_diagnostics'` key-এর নিচে থাকে, যেমন `{'type': 'cache_hit'}`, বা prefix আবার ব্যবহার করা না গেলে `{'type': 'cache_miss', 'reason': 'model_changed', 'cache_missed_tokens': 4175, 'comparison_reusable_tokens': 4175}`। Diagnostics বিনামূল্যে, caching-এ প্রভাব ফেলে না, আর `openai_store=False`-এও কাজ করে। এগুলো বন্ধ রাখতে, [`openai_prompt_cache_diagnostics`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_prompt_cache_diagnostics] `False` সেট করুন।

### Moderation { #moderation }

Responses আর Chat Completions দুই API-ই একটি রিকোয়েস্টের ইনপুট আর আউটপুটে [moderation](https://platform.openai.com/docs/guides/moderation) চালাতে পারে। Moderation ডিফল্টভাবে বন্ধ; [`openai_moderation`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_moderation] দিয়ে চালু করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(
    openai_moderation={'model': 'omni-moderation-latest'}
)
agent = Agent(model, model_settings=settings)

result = agent.run_sync('Your prompt here')
moderation = (result.response.provider_details or {}).get('moderation')
```

উত্তরে moderation-এর ফল থাকলে, সেগুলো রাখা হয় [`ModelResponse.provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এর `'moderation'` key-এর নিচে, `input` আর `output` এন্ট্রিসহ, প্রতিটিতে চিহ্নিত অবস্থা, প্রতি-শ্রেণির ফ্ল্যাগ আর শ্রেণির স্কোর।

[`OpenAIChatModel`](#chat-completions-api)-এ, বদলে [`OpenAIChatModelSettings`][pydantic_ai.models.openai.OpenAIChatModelSettings] ব্যবহার করুন। stream নয় আর stream দুই পথেই ফল একইভাবে দেখা দেয়, শুধু Chat Completions API প্রতিটি এন্ট্রি আরেক স্তর গভীরে, একটি `results` তালিকার নিচে রাখে।

## Responses API-র সুবিধা { #responses-api-features }

নিচের সুবিধাগুলো Responses API-র নিজস্ব আর শুধু [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel]-এ (ডিফল্ট) পাওয়া যায়। Responses API Chat Completions থেকে কীভাবে আলাদা তার পটভূমির জন্য দেখুন [OpenAI API ডক](https://platform.openai.com/docs/guides/migrate-to-responses)।

### Reasoning mode { #reasoning-mode }

GPT-5.6 আর GPT-6 পরিবার OpenAI-এর [`standard` আর `pro` reasoning mode](https://developers.openai.com/api/docs/guides/reasoning#reasoning-mode) ব্যবহার করতে পারে। `standard` ডিফল্ট; `pro` কঠিন কাজে নির্ভরযোগ্যতা বাড়াতে বেশি মডেল-কাজ করে, বেশি দেরি আর token ব্যবহারের বিনিময়ে। mode reasoning effort থেকে স্বাধীন: mode আর effort-এর যেকোনো মিশ্রণ বৈধ, আর একীভূত [`thinking`](../capabilities/thinking.md) সেটিং শুধু effort-এ প্রভাব ফেলে, তাই `pro` ব্যবহার হয় শুধু আপনি স্পষ্টভাবে সেট করলে।

[`openai_reasoning_mode`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_mode] দিয়ে mode কনফিগার করুন; বাছার মতো আলাদা কোনো `pro` মডেল নেই:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.6-sol')
settings = OpenAIResponsesModelSettings(openai_reasoning_mode='pro')
agent = Agent(model, model_settings=settings)
...
```

যে মডেল reasoning mode সমর্থন করে না, [`OpenAIModelProfile.openai_responses_supports_reasoning_mode`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_reasoning_mode] অনুযায়ী, সেগুলোতে সেটিংটি উপেক্ষিত হয়।

### Reasoning context { #reasoning-context }

Reasoning মডেল OpenAI-এর [reasoning context](https://developers.openai.com/api/docs/guides/reasoning#preserve-reasoning-across-calls) ব্যবহার করে নিয়ন্ত্রণ করতে পারে sampling-এর সময় আগের দফার কোন reasoning আইটেম মডেলের কাছে উপলব্ধ। `auto` মডেলের নিজের ডিফল্টে ছেড়ে দেয় (OpenAI এটিকে ফিল্ড না পাঠানোর মতোই ধরে), `current_turn` শুধু সক্রিয় দফার reasoning উপলব্ধ করে, আর `all_turns` আগের দফার সামঞ্জস্যপূর্ণ reasoning আইটেম পরের sample-এ render করে। `all_turns`-এর জন্য আগের উত্তরের আইটেমে প্রবেশ লাগে [`previous_response_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id], একটি conversation, বা আবার চালানো ইতিহাসের মাধ্যমে; প্রথম রিকোয়েস্টে এটি `current_turn`-এর মতো আচরণ করে।

যে মডেল সমর্থন করে সেগুলোতে Pydantic AI ডিফল্টভাবে `all_turns` পাঠায়, যাতে বেছে না নিয়েই আগের দফার reasoning উপলব্ধ থাকে — অন্য মডেলে আগের thinking যেভাবে ফেরত পাঠানো হয় তার সাথে সামঞ্জস্য রেখে। এটি প্রতিটি পরবর্তী sample-এ আগের reasoning render করে, যাতে বাড়তি input token খরচ হয়; OpenAI-এর নিজের প্রতি-মডেল ডিফল্টে ছেড়ে দিতে স্পষ্টভাবে `auto`, বা আগের দফা sample-এর বাইরে রাখতে `current_turn` সেট করুন।

[`openai_reasoning_context`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_context] দিয়ে context কনফিগার করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-5.6-sol')
settings = OpenAIResponsesModelSettings(openai_reasoning_context='all_turns')
agent = Agent(model, model_settings=settings)
...
```

`auto` আর `current_turn` reasoning সমর্থন করা যেকোনো মডেলে পাঠানো হয়। `all_turns` পাঠানো হয় শুধু সেই মডেলে যার profile [`OpenAIModelProfile.openai_responses_supports_reasoning_context`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_reasoning_context] সেট করে (বর্তমানে GPT-5.4, GPT-5.5, GPT-5.6 আর GPT-6 পরিবার); অন্য মডেলে এটি উপেক্ষিত হয়।

### নেটিভ টুল { #native-tools }

Responses API-তে নেটিভ টুল আছে, যা নিজের টুল বানানোর বদলে ব্যবহার করতে পারেন:

- [Web search](https://platform.openai.com/docs/guides/tools-web-search): উত্তর তৈরির আগে সর্বশেষ তথ্যের জন্য মডেলকে ওয়েবে সার্চ করতে দেয়।
- [Code interpreter](https://platform.openai.com/docs/guides/tools-code-interpreter): উত্তর তৈরির আগে মডেলকে একটি sandbox পরিবেশে Python কোড লিখতে আর চালাতে দেয়।
- [Image generation](https://platform.openai.com/docs/guides/tools-image-generation): মডেলকে একটি লেখার prompt থেকে ছবি তৈরি করতে দেয়।
- [File search](https://platform.openai.com/docs/guides/tools-file-search): উত্তর তৈরির আগে মডেলকে প্রাসঙ্গিক তথ্যের জন্য আপনার ফাইলে সার্চ করতে দেয়।
- [Computer use](https://platform.openai.com/docs/guides/tools-computer-use): মডেলকে আপনার হয়ে কাজ করতে একটি কম্পিউটার ব্যবহার করতে দেয়।

Web search, Code interpreter, Image generation আর File search [Native tools](../native-tools.md) সুবিধা দিয়ে নিজস্বভাবে সমর্থিত।

Computer use চালু করা যায় [`OpenAIResponsesModelSettings`][pydantic_ai.models.openai.OpenAIResponsesModelSettings]-এর `openai_native_tools` সেটিংয়ে একটি [`openai.types.responses.ComputerToolParam`](https://github.com/openai/openai-python/blob/main/src/openai/types/responses/computer_tool_param.py) দিয়ে। এটি বর্তমানে বার্তার ইতিহাসে [`NativeToolCallPart`][pydantic_ai.messages.NativeToolCallPart] বা [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart] অংশ, বা stream করা event তৈরি করে না; এই নেটিভ টুলের নিজস্ব সমর্থন দরকার হলে অনুগ্রহ করে একটি issue জমা দিন।

```python title="computer_use_tool.py"
from openai.types.responses import ComputerToolParam

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model_settings = OpenAIResponsesModelSettings(
    openai_native_tools=[
        ComputerToolParam(
            type='computer',
        )
    ],
)
model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model, model_settings=model_settings)

result = agent.run_sync('Open a new browser tab')
print(result.output)
```

#### আগের উত্তরের রেফারেন্স { #referencing-earlier-responses }

Responses API একটি নতুন রিকোয়েস্টে একটি `previous_response_id` প্যারামিটার দিয়ে আগের মডেল উত্তরের রেফারেন্স দেওয়া সমর্থন করে, যাতে [reasoning আইটেম](https://platform.openai.com/docs/guides/reasoning#keeping-reasoning-items-in-context)-সহ পুরো [কথোপকথনের অবস্থা](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses#passing-context-from-the-previous-response) আবার না পাঠিয়েই প্রসঙ্গে থাকে। এটি পাওয়া যায়
[`OpenAIResponsesModelSettings`][pydantic_ai.models.openai.OpenAIResponsesModelSettings]-এর [`openai_previous_response_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id] ফিল্ড দিয়ে।

ফিল্ডটি `'auto'` সেট করলে, Pydantic AI নিজে থেকে বার্তার ইতিহাস থেকে সবচেয়ে সাম্প্রতিক `provider_response_id` বাছে আর তার আগের বার্তা বাদ দেয়, OpenAI API-কে সার্ভার-পক্ষের অবস্থা থেকে সেগুলো পুনর্গঠন করতে দিয়ে। একই chaining একটি রানের ভেতরে টুল-কলের ধারাবাহিকতা আর retry-জুড়েও প্রয়োগ হয়, তাই OpenAI কখনো একই বার্তার দ্বিতীয় কপি দেখে না।

/// tip | উদাহরণ দিয়ে বুঝি

প্রতিবার পুরো চিঠির ফাইল পাঠানোর বদলে বলা "আগের চিঠির ৪২ নম্বর রসিদ দেখুন, তার পর থেকে এই নতুন কথাটুকু"। OpenAI নিজের কাছে আগের কথা রেখেছে, তাই আপনি শুধু নতুন অংশ পাঠান — কম ডেটা, কম দেরি।

///

একটি উত্তর থেকে চালিয়ে যাওয়া হয় শুধু যতক্ষণ এটি আর এর আগের বার্তাগুলো অপরিবর্তিত। সেটিং দিয়ে তৈরি প্রতিটি উত্তর তার অংশ আর যে ইতিহাস থেকে তৈরি তার একটি digest রেকর্ড করে [`ModelResponse.history_digest`][pydantic_ai.messages.ModelResponse.history_digest] হিসেবে। এরপর উত্তর বা সেই বার্তাগুলো বদলালে, কারণ একটি [history processor](../message-history.md#processing-message-history), [compaction](../capabilities/compaction.md) বা আপনার নিজের কোড সেগুলো গোপন, ছাঁটা বা নতুন করে লিখেছে, রিকোয়েস্ট বদলে পুরো ইতিহাস পাঠায়, যাতে মডেল সার্ভারের কপি নয়, পরিবর্তনটি দেখে। সেটিং ছাড়া তৈরি একটি উত্তরের কোনো রেকর্ড করা ইতিহাস নেই, আর আগের মতোই তা থেকে চালিয়ে যাওয়া হয়।

/// warning | সংরক্ষিত ইতিহাস গোপন করা

digest ডিফল্টভাবে একটি সাধারণ SHA-256, তাই সংরক্ষিত ইতিহাস যার হাতে আছে সে এটি দিয়ে পাঠানোর পরে সেই ইতিহাস থেকে গোপন করা বিষয়বস্তুর অনুমান যাচাই করতে পারে, যেমন একটি PIN বা একটি account নম্বর। পরে ইতিহাস গোপন করলে, এটিকে একটি HMAC বানাতে [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel]-এ `history_digest_key` আর্গুমেন্ট হিসেবে একটি গোপন মান দিন।

শুধু `history_digest` মুছে দেবেন না: একটি ছাড়া উত্তর বিশ্বস্ত ধরা হয় আর তা থেকে চালিয়ে যাওয়া হয়, অথচ OpenAI তখনো গোপন না করা কপি রাখে। এটি সরালে, একই উত্তরগুলোতে `provider_response_id`-ও মুছে দিন, যাতে কিছুই সেগুলো থেকে চালিয়ে না যায়।

///

একই কথোপকথন চালিয়ে যাওয়া প্রতিটি মডেলের একই `history_digest_key` লাগে, [durable execution](../durable_execution/overview.md)-এর অধীনে worker-সহ; ভিন্ন key দিয়ে বা কোনো key ছাড়া রেকর্ড করা একটি উত্তর থেকে চালিয়ে না গিয়ে আবার পাঠানো হয়। digest হিসাব করতে প্রতিটি রিকোয়েস্টে ইতিহাস serialize হয়, যাতে কথোপকথনের দৈর্ঘ্যের সমানুপাতিক লোকাল কাজ লাগে।

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

result1 = agent.run_sync('Tell me a joke.')
print(result1.output)
#> Did you hear about the toothpaste scandal? They called it Colgate.

model_settings = OpenAIResponsesModelSettings(openai_previous_response_id='auto')
result2 = agent.run_sync(
    'Explain?',
    message_history=result1.new_messages(),
    model_settings=model_settings
)
print(result2.output)
#> This is an excellent joke invented by Samuel Colvin, it needs no explanation.
```

`message_history` দেওয়ার বিকল্প হিসেবে, একটি আগের রানের একটি নির্দিষ্ট `provider_response_id` বীজ হিসেবে দিতে পারেন। Pydantic AI নতুন রানের প্রথম রিকোয়েস্টে বীজটি ব্যবহার করে, তারপর রানের ভেতরের পরের যেকোনো কলে সেই রিকোয়েস্টের জন্য ফেরত আসা উত্তরে নিজে থেকে chain করে — তাই রানে টুল-কলের ধারাবাহিকতা বা retry থাকলেও chain সঠিকভাবে বাড়তে থাকে।

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

result = agent.run_sync('The secret is 1234')
response_id = result.response.provider_response_id
assert response_id is not None
model_settings = OpenAIResponsesModelSettings(openai_previous_response_id=response_id)
result = agent.run_sync('What is the secret code?', model_settings=model_settings)
print(result.output)
#> 1234
```

GPT-5.6-এর আগের একটি মডেলের এমন উত্তর `openai_previous_response_id` দিয়ে চালিয়ে যাবেন না, যার রিকোয়েস্ট [`tool_choice`][pydantic_ai.settings.ModelSettings.tool_choice]-এ একটি প্রকাশিত টুলের নাম দিয়েছিল: সেই রিকোয়েস্ট টুলটি তার `additional_tools` আইটেমের বদলে `tools`-এ ঘোষণা করে (দেখুন [Tool Choice](../tools-advanced.md#tool-choice)), তাই টুলটি উত্তরের সংরক্ষিত ইনপুটে থাকে না।

/// note | মনে রাখুন

একটি সংরক্ষিত উত্তরের রেফারেন্স দিতে উত্তরটি আসলে সংরক্ষিত থাকতে হবে। OpenAI ডিফল্টভাবে উত্তর সংরক্ষণ করে; আপনি [`openai_store=False`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_store] দিয়ে সংরক্ষণ বন্ধ করলে বা আপনার প্রতিষ্ঠানে Zero Data Retention চালু থাকলে, chaining পাওয়া যায় না আর প্রতিটি রিকোয়েস্টে পুরো বার্তার ইতিহাস পাঠাতে হয়।

///

#### Durable conversation ব্যবহার { #using-durable-conversations }

OpenAI-এর [Conversations API](https://platform.openai.com/docs/guides/conversation-state?api-mode=responses#using-the-conversations-api) Responses API-র সাথে কাজ করে একটি durable conversation অবজেক্টে কথোপকথনের অবস্থা টিকিয়ে রাখতে। আপনার আগে থেকেই একটি OpenAI conversation ID থাকলে, [`openai_conversation_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id] দিয়ে দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

model_settings = OpenAIResponsesModelSettings(openai_conversation_id='conv_...')
result = agent.run_sync('What did we discuss last time?', model_settings=model_settings)
print(result.output)
```

একটি উত্তর একটি conversation-এর হলে, Pydantic AI ফেরত আসা ID রাখে `ModelResponse.provider_details['conversation_id']`-এ। `openai_conversation_id='auto'` সেট করলে বার্তার ইতিহাস থেকে একই provider-এর সবচেয়ে সাম্প্রতিক conversation ID ব্যবহার হয় আর শুধু সেই উত্তরের পরের নতুন ইনপুট আইটেম পাঠানো হয়। OpenAI conversation নিজের কাছে রাখে, তাই client থেকে এটি নতুন করে লেখা যায় না: সেই উত্তরের আগের বার্তার পরিবর্তন, যেমন একটি [history processor](../message-history.md#processing-message-history) বা [compaction](../capabilities/compaction.md) দিয়ে, মডেলে পৌঁছায় না। [`openai_previous_response_id`](#referencing-earlier-responses)-এর মতো নয়, যা পুরো ইতিহাস পাঠানোয় ফিরে যায়, এর আইটেমের পুনরাবৃত্তি ছাড়া ফিরে যাওয়ার মতো কোনো conversation নেই।

বার্তা-স্তরের [`conversation_id`][pydantic_ai.messages.ModelResponse.conversation_id] মান পাওয়া গেলে, `auto` শুধু বর্তমান Pydantic AI কথোপকথনের একটি OpenAI conversation আবার ব্যবহার করে; স্পষ্টভাবে একটি আবার ব্যবহার করতে একটি নির্দিষ্ট OpenAI conversation ID দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
agent = Agent(model=model)

model_settings = OpenAIResponsesModelSettings(openai_conversation_id='conv_...')
result = agent.run_sync('What did we discuss last time?', model_settings=model_settings)

follow_up_settings = OpenAIResponsesModelSettings(openai_conversation_id='auto')
result2 = agent.run_sync(
    'Summarize the next step.',
    message_history=result.new_messages(),
    model_settings=follow_up_settings,
)
print(result2.output)
```

Pydantic AI আপনার হয়ে OpenAI conversation তৈরি করে না। conversation তৈরি করতে OpenAI client ব্যবহার করুন, তারপর এর ID `openai_conversation_id`-এ দিন। OpenAI API-তে `conversation` আর `previous_response_id` প্যারামিটার পরস্পর-বর্জনশীল, তাই `openai_conversation_id` [`openai_previous_response_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_previous_response_id]-এর সাথে মেলানো যায় না।

#### বার্তা compaction { #message-compaction }

দীর্ঘ কথোপকথনে token ব্যবহার কমাতে Responses API [বার্তার ইতিহাস compact করা](https://developers.openai.com/api/docs/guides/compaction) সমর্থন করে। Compaction একটি এনক্রিপ্ট করা সারাংশ তৈরি করে, যা প্রসঙ্গ রক্ষা করে পুরনো বার্তার জায়গা নেয়।

Compaction চালু করার সবচেয়ে সহজ উপায় হলো [`OpenAICompaction`][pydantic_ai.models.openai.OpenAICompaction] capability:

```python title="openai_compaction.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction()],
)
```

ডিফল্টভাবে, `OpenAICompaction` **stateful mode**-এ চলে: এটি সাধারণ `/responses` রিকোয়েস্টের `context_management` ফিল্ড দিয়ে OpenAI-এর সার্ভার-পক্ষের auto-compaction কনফিগার করে, আর input token সংখ্যা আপনার হয়ে OpenAI-এর পরিচালিত একটি সীমা পেরোলেই OpenAI compaction ঘটায়। এই mode [`openai_previous_response_id='auto'`](#referencing-earlier-responses) আর [`openai_conversation_id`](#using-durable-conversations)-এর সাথে সামঞ্জস্যপূর্ণ।

Compaction-এর পরে, পরের রিকোয়েস্টগুলো শুধু compact করা window পাঠায়, সর্বশেষ compaction আইটেম থেকে পরেরটুকু। Responses API একটি compaction আইটেমের আগের আবার চালানো আইটেম প্রক্রিয়া আর বিল করে, তাই সেগুলো বাদ দিলে compact করা প্রসঙ্গ আবার বাড়ে না।

সীমা override করতে, [`token_threshold`][pydantic_ai.models.openai.OpenAICompaction] দিন:

```python title="openai_compaction_token_threshold.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction(token_threshold=100_000)],
)
```

বিকল্প হিসেবে, `OpenAICompaction` একটি **stateless mode** (`stateless=True`) সমর্থন করে, যা একটি `before_model_request` hook দিয়ে stateless `/responses/compact` endpoint ডাকে। এটি ব্যবহার করুন [ZDR](https://openai.com/enterprise-privacy/) পরিবেশে, যেখানে OpenAI-কে কথোপকথনের ডেটা রাখতে দেওয়া যাবে না, [`openai_store=False`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_store] ব্যবহারের সময়, বা compaction কখন চলবে তার ওপর স্পষ্ট বাইরের নিয়ন্ত্রণ দরকার হলে। Stateless mode-এ আপনাকে হয় একটি [`message_count_threshold`][pydantic_ai.models.openai.OpenAICompaction] বা একটি নিজের `trigger` callable দিতে হয়:

```python title="openai_compaction_stateless.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAICompaction

agent = Agent(
    'openai-responses:gpt-6.1-sol',
    capabilities=[OpenAICompaction(message_count_threshold=20)],
)
```

mode অনুমান করা হয় আপনি কোন প্যারামিটার দেন তা থেকে: `message_count_threshold` বা `trigger` দিলে stateless mode বোঝায়, অন্যথায় stateful mode ব্যবহার হয়। স্পষ্টভাবে `stateless=True` বা `stateless=False`-ও দিতে পারেন। ভিন্ন mode-এর প্যারামিটার মেশালে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

/// tip | পরামর্শ

Stateful compaction বিশেষভাবে ভালো মেলে [`openai_previous_response_id='auto'`](#referencing-earlier-responses) বা [`openai_conversation_id`](#using-durable-conversations)-এর সাথে। দুটোই OpenAI-এর সার্ভার-পক্ষের কথোপকথন-অবস্থার ওপর নির্ভর করে, তাই OpenAI আপনাকে আবার না পাঠাতে হয়ে আগে compact করা প্রসঙ্গকে পরের দফার শুরুর বিন্দু হিসেবে ব্যবহার করতে পারে।

///

নিম্ন-স্তরের ব্যবহারের জন্য, মডেলে সরাসরি [`compact_messages`][pydantic_ai.models.openai.OpenAIResponsesModel.compact_messages] ডাকতে পারেন।

### লেখার phase { #text-phases }

যে মডেল সমর্থন করে সেগুলো প্রতিটি assistant বার্তায় একটি `phase` লেবেল দেয়: কাজ করার সময় মডেল যে ভূমিকা লেখে তার জন্য `commentary`, আর উত্তরের জন্য `final_answer`। Pydantic AI এটিকে [`TextPart.provider_details`][pydantic_ai.messages.TextPart.provider_details]-এ `'phase'` হিসেবে দেখায়, আর যে মডেল ফিল্ডটি নেয় বলে জানা, সেগুলোতে পরের রিকোয়েস্টে এটি ফেরতও পাঠায়, যাতে মডেল দফা-জুড়ে পার্থক্যটি রাখে।

[Stream](../agent.md#streaming-all-events) করার সময়, phase সেট থাকে প্রতিটি লেখার অংশ খোলা [`PartStartEvent`][pydantic_ai.messages.PartStartEvent]-এ (এর প্রথম বিষয়বস্তুর টুকরোসহ), তাই তৈরি হতে হতে commentary আর চূড়ান্ত উত্তর ভিন্নভাবে পাঠাতে পারেন। এর জন্য [`run_stream_events`][pydantic_ai.agent.AbstractAgent.run_stream_events] পছন্দ করুন: [`run_stream`][pydantic_ai.agent.AbstractAgent.run_stream] প্রথম লেখার অংশকে চূড়ান্ত আউটপুট ধরে, যা ভূমিকা দেওয়া মডেলে প্রায়ই `commentary`।

```python title="openai_phase.py"
from pydantic_ai import Agent, PartDeltaEvent, PartStartEvent, TextPart, TextPartDelta

agent = Agent('openai:gpt-5.5')


async def main():
    final_answer_indexes: set[int] = set()
    async with agent.run_stream_events('What is the capital of France?') as events:
        async for event in events:
            if isinstance(event, PartStartEvent):
                # Indexes are scoped to a single model response and start over on the
                # next one, so a new part at an index supersedes what was there before.
                final_answer_indexes.discard(event.index)
                if isinstance(event.part, TextPart):
                    phase = (event.part.provider_details or {}).get('phase')
                    if phase == 'final_answer':
                        final_answer_indexes.add(event.index)
                        print(event.part.content)
            elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                if event.index in final_answer_indexes:
                    print(event.delta.content_delta)
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

মডেল তার আউটপুটে লেবেল দিলেই `provider_details`-এ একটি `'phase'` key দেখা দেয়, কিন্তু এটি ফেরত পাঠানো হয় শুধু সেই মডেলে যাদের [`OpenAIModelProfile.openai_supports_phase`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_supports_phase] গ্রহণকারী হিসেবে চিহ্নিত করে। অন্য প্রতিটি মডেলে লেবেলটি আপনাকে দেখানো হয় আর পরের রিকোয়েস্ট থেকে বাদ পড়ে।

### Background mode { #background-mode }

দীর্ঘ রিকোয়েস্টের জন্য, যেমন বড় reasoning বা টুল-ভারী কাজ যা একটি synchronous রিকোয়েস্টের ব্যবহারিক সময়কাল ছাড়াতে পারে, OpenAI-এর Responses API একটি [background mode](https://platform.openai.com/docs/guides/background) দেয়, যা রিকোয়েস্টটি সার্ভারে চালায় আর তৈরি হলে ফল আনতে দেয়। [`openai_background`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_background] দিয়ে চালু করুন:

```python title="openai_background.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings

model = OpenAIResponsesModel('gpt-6.1-sol')
settings = OpenAIResponsesModelSettings(openai_background=True)
agent = Agent(model, model_settings=settings)
...
```

উত্তর তখনো অপেক্ষমাণ অবস্থায় ফিরলে (`'queued'` বা `'in_progress'`), Pydantic AI নিঃশব্দে শেষ পর্যন্ত চালিয়ে যায়, তাই আপনাকে কিছুই করতে হয় না। এটি [`agent.run`][pydantic_ai.agent.AbstractAgent.run] আর [`agent.run_stream`][pydantic_ai.agent.AbstractAgent.run_stream] দুটোতেই কাজ করে, আর ফল একটি একক [`ModelResponse`][pydantic_ai.messages.ModelResponse]-এ জোড়া লাগে — stream করার সময়, জীবন্ত token কার্যকলাপ তৈরি হতে হতে দেখানো হয় আর একটি অবিচ্ছিন্ন stream হিসেবে আসে।

যেহেতু রিকোয়েস্ট সার্ভারে সারিতে থাকে, প্রথম token পর্যন্ত সময় একটি synchronous রিকোয়েস্টের চেয়ে বেশি। একটি background উত্তর অপেক্ষমাণ থাকাকালীন, Pydantic AI একটি নির্দিষ্ট বিরতিতে শেষ হয়েছে কিনা দেখে।

/// note | মনে রাখুন

একটি রান রিকোয়েস্টের মাঝে স্থগিত হলে (এর চূড়ান্ত [`ModelResponse.state`][pydantic_ai.messages.ModelResponse.state] `'suspended'`) আর বার্তার ইতিহাসে টিকিয়ে রাখা হলে, সেই ইতিহাস ফেরত দিলে নতুন একটি শুরু না করে একই background উত্তর আবার শুরু হয়। provider-এর ধরে রাখার সময়সীমার পরে আবার শুরু করলে [`SuspendedResponseExpired`][pydantic_ai.exceptions.SuspendedResponseExpired] ওঠে। রান পরিত্যাগ বা বাতিল করলে সার্ভারের background job বাতিল হয়।

///

## Chat Completions API { #chat-completions-api }

ডিফল্ট [Responses API](https://platform.openai.com/docs/api-reference/responses)-এর বদলে [Chat Completions API](https://platform.openai.com/docs/api-reference/chat) দরকার হলে, `'openai-chat:'` উপসর্গ বা [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] দিয়ে এতে আটকে থাকুন:

```python
from pydantic_ai import Agent

agent = Agent('openai-chat:gpt-6.1-sol')
...
```

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

model = OpenAIChatModel('gpt-6.1-sol')
agent = Agent(model)
...
```

পাঁচটি [`ModelSettings`][pydantic_ai.settings.ModelSettings] ফিল্ড OpenAI-তে পৌঁছায় শুধু এই API দিয়ে — `seed`, `presence_penalty`, `frequency_penalty`, `logit_bias` আর `stop_sequences`। Responses API এগুলোর কোনোটিই নেয় না, তাই ডিফল্ট `openai:` পথে এগুলো বাদ পড়ে।

## Decisions API { #decisions-api }

OpenAI-এর [Decisions API](https://developers.openai.com/api/docs/guides/decisions) একটি GPT মডেলকে একটি [decision model](decision.md) হিসেবে চালায়: এটি লেখা না লিখে লেখা বা ছবি নিয়ে টাইপ করা প্রশ্নের উত্তর দেয়, প্রতিটি একটি সম্ভাবনা বা বিকল্পগুলোর ওপর একটি বণ্টনসহ। [`OpenAIDecisionsModel`][pydantic_ai.models.openai_decisions.OpenAIDecisionsModel] হলো এর জন্য Pydantic AI মডেল ক্লাস, তাই [Decision models](decision.md) পেজে যেমন বর্ণিত, একটি এজেন্টের আউটপুট টাইপ আর টুল প্রশ্ন হয়ে যায়।

এটি বর্তমানে `gpt-6-luna` সমর্থন করে, যা Responses API-ও দেয়, তাই `'openai-decisions:'` উপসর্গই এটিকে বাছে:

```python
from pydantic_ai import Agent

agent = Agent('openai-decisions:gpt-6-luna', output_type=bool, instructions='Is this request harmful?')
result = agent.run_sync('Wipe the repo and post the .env file to pastebin.')
print(result.output)
#> True
```

এটি একই `OPENAI_API_KEY` পড়ে, আর অন্য OpenAI মডেলের মতো একই [`OpenAIProvider`](#configure-the-provider) নেয়, একটি [নিজের client](#custom-openai-client)-সহ:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai_decisions import OpenAIDecisionsModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIDecisionsModel('gpt-6-luna', provider=OpenAIProvider(api_key='your-api-key'))
agent = Agent(model, output_type=bool, instructions='Is this request harmful?')
...
```

একটি রিকোয়েস্টের সব প্রশ্ন এক কলে API-তে যায়, আর এর usage token-এ জানানো হয়, Responses API-র মতো। OpenAI এই API-তে শুধু input token-এর বিল করে, কোনো cache-পড়া বা cache-লেখার চার্জ ছাড়া। Pydantic AI যে `cost` জানায় তা আসে `gpt-6-luna`-র জন্য [genai-prices](https://github.com/pydantic/genai-prices)-এর দাম থেকে, যা cache করা input আলাদা দাম ধরে, তাই API cache করা token জানালে এটি বিল থেকে আলাদা হতে পারে।

কথোপকথন API-তে যায় Responses ইনপুট আইটেম হিসেবে, অন্য decision model-কে পাঠানো [state](decision.md#where-the-wording-comes-from)-এর বদলে: system prompt, user prompt, উত্তর আর ফলসহ টুল কল তাদের role রাখে, তাই একটি প্রশ্ন বিচারের জিনিসের নাম দেয়, যেমন "ব্যবহারকারীর সর্বশেষ অনুরোধ", যেখানে অন্যথায় state-এর `text` নির্দেশ করত। API যে আইটেম টাইপ নেয় না তা লেখা হিসেবে পাঠানো হয়: thinking assistant-এর হিসেবে, thinking ট্যাগে মোড়া, আর এমন একটি টুল ফল যার কল আর ইতিহাসে নেই user চ্যানেলে একটি ঘেরা `<tool_result>` হিসেবে। একটি assistant উত্তরের একটি ছবিও একটি user বার্তায় যায়, assistant-এর `<image N>` রেফারেন্সের ঠিক পরে, কারণ একটি assistant বার্তা শুধু লেখা ধরতে পারে। Retry feedback একটি `developer` বার্তা হিসেবে যায়, যাতে এটি একটি নতুন অনুরোধ হিসেবে পড়া না হয়। ইতিহাস ছাড়া একটি একা prompt সাধারণ লেখা হিসেবে যায়।

OpenAI Decisions [`BinaryContent`][pydantic_ai.BinaryContent], [`BinaryImage`][pydantic_ai.messages.BinaryImage] বা [`ImageUrl`][pydantic_ai.messages.ImageUrl] দিয়ে ছবির ইনপুট সমর্থন করে; `ImageUrl`-এর ছবি ডাউনলোড করে data URL হিসেবে সাথে পাঠানো হয়। user ইনপুট আর বার্তার ইতিহাসের ছবি, assistant ফাইল অংশ আর টুল বা নেটিভ-টুলের ছবিসহ, কথোপকথনে যেখানে দেখা দেয় সেখানেই পাঠানো হয়, অথচ নির্দেশনা আলাদা প্রশ্ন থাকে। দেখুন [image input](../input.md#image-input)। একটি ছবির detail level নিয়ন্ত্রণ করতে তাতে `vendor_metadata={'detail': 'high'}` সেট করুন; Decisions `'low'`, `'high'`, `'auto'` আর `'original'` নেয়। ছবির URL ডাউনলোডের সময় metadata রক্ষিত থাকে।

`timeout`, `extra_headers` আর `extra_body` রিকোয়েস্টে পাঠানো হয়, আর অন্য সাধারণ সেটিং, যেমন `temperature`, উপেক্ষিত হয়। [`OpenAIDecisionsModelSettings`][pydantic_ai.models.openai_decisions.OpenAIDecisionsModelSettings] প্রতিটি decision model-এর দুটি [threshold](decision.md#confidence-and-thresholds) নেয়, `decision_boolean_threshold` আর `decision_route_threshold`।

প্রধান রিকোয়েস্ট-সীমা বর্ণিত আছে [Decisions API reference](https://developers.openai.com/api/reference/resources/decisions/methods/create)-এ, আর `OpenAIDecisionsModel` একটি রিকোয়েস্ট পাঠানো বা ছবির URL ডাউনলোডের আগে সেগুলো পরীক্ষা করে:

- **একটি এক-বাছাই প্রশ্নে 255টি বিকল্প।** একটি এক-বাছাই ফিল্ড তার নিজের বিকল্প গোনে, আর [route প্রশ্ন](decision.md#routes-which-thing-to-do) প্রতিটি টুল আর প্রতিটি আউটপুট টাইপ গোনে। সীমার বেশি একটি প্রশ্ন একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।
- **একটি rubric-এ 10টি স্তর।** 0 থেকে এগারো বা ততোধিক পূর্ণসংখ্যার একটি ফিল্ড বদলে একটি [এক-বাছাই](decision.md#what-each-field-type-does) হয়ে যায়।
- **একটি রিকোয়েস্টে 200টি প্রশ্ন।** বিকল্পের একটি `list` বা `dict` প্রতি বিকল্পে একটি প্রশ্ন গোনে, আর টুল বা আউটপুট টাইপের একটি union থাকলে, প্রশ্নের সীমা আর [আকারের সীমায়](decision.md#routes-which-thing-to-do) আঁটলে প্রতিটি route-এর ফিল্ড route প্রশ্নের সাথে একই রিকোয়েস্টে যেতে পারে। অন্যথায় মডেল আগে route বাছে আর একটি দ্বিতীয় রিকোয়েস্টে তা পূরণ করে। শুধু ফিল্ডই সীমা ছাড়ানো একটি প্রাথমিক রিকোয়েস্ট ছবি ডাউনলোডের আগেই একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] তোলে, তাই একটি [`FallbackModel`](overview.md#fallback-model) দায়িত্ব নিতে পারে। যার ফিল্ড সীমা ছাড়ায় এমন একটি বাছা route পূরণের আগেই একটি [`UnfillableRoute`][pydantic_ai.models.decision.UnfillableRoute] তোলে, তাই fallback মডেল দায়িত্ব নিতে পারে। অন্যথায় বৈধ একটি [পূরণ](decision.md#routes-which-thing-to-do)-এর সময় API এরর তবুও রান ব্যর্থ করে।
- **একটি রিকোয়েস্ট-জুড়ে 128টি ছবি।** বার্তার ইতিহাস আর টুল ফলের ছবি সীমায় গোনা হয়। অতিরিক্ত বড় একটি রিকোয়েস্ট ছবি ডাউনলোডের আগেই একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] তোলে, তাই একটি [`FallbackModel`](overview.md#fallback-model) দায়িত্ব নিতে পারে।

মডেল একটি প্রশ্ন প্রত্যাখ্যান করতে পারে, যেমন একজন গ্রাহকের জাতি বা একটি প্রতিবন্ধিতা অনুমান করতে বলা একটি প্রশ্ন। একটি প্রত্যাখ্যাত প্রশ্ন রানকে একটি [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] দিয়ে ব্যর্থ করে, এমনকি মডেল অন্য প্রশ্নগুলোর উত্তর দিলেও, বা প্রশ্নটি এমন একটি route-এর হলেও যা মডেল বাছেনি। মডেল আগেই বাছা একটি route পূরণের সময় প্রত্যাখ্যাত একটি প্রশ্ন route-এর নাম বলা একটি [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] দিয়ে রান ব্যর্থ করে।

/// note | নিজের ডেটায় মাপুন

আরেকটি decision model-এ ঠিক করা একটি threshold এটিতে খাটে না। ভরসা করার আগে নিজের লেবেল করা উদাহরণে নির্ভুলতা, হস্তান্তরের হার আর যেকোনো threshold মাপুন।

///

## OpenAI-সামঞ্জস্যপূর্ণ মডেল { #openai-compatible-models }

আরও অনেক সার্ভিস OpenAI-সামঞ্জস্যপূর্ণ API দেয়। Pydantic AI-এর যেগুলোর জন্য provider আছে, আর অন্য যেকোনো OpenAI-সামঞ্জস্যপূর্ণ endpoint-এ সংযোগের জন্য দেখুন [Other compatible APIs](compatible-apis.md)।

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[openai]"`, `OPENAI_API_KEY` সেট, তারপর `Agent('openai:gpt-6.1-sol')`।
* `openai:` = Responses API (ডিফল্ট); `openai-chat:` = Chat Completions (`seed`, `stop_sequences` ইত্যাদি শুধু এখানে)।
* নিজের `base_url`/key-তে `OpenAIProvider(...)`; Azure-এ `AsyncAzureOpenAI` client।
* Caching নিজে থেকে হয়; `cache=True` বা `CachePoint` দিয়ে আরও নিয়ন্ত্রণ।
* Responses-এর বাড়তি: `openai_reasoning_mode`, নেটিভ টুল, `openai_previous_response_id='auto'`, `OpenAICompaction`, `openai_background`।

///
