# Anthropic { #anthropic }

/// note | এই পেজে যা শিখবেন

* Claude মডেল ইনস্টল, API key, provider আর নিজের HTTP client।
* মডেল সেটিং, service tier, আর AWS Bedrock / Google Cloud / Microsoft Foundry দিয়ে Claude।
* Task budget, prompt caching-এর সব উপায়, কথোপকথনের মাঝের system বার্তা।
* Fast mode, জোর করে টুল বাছাই, thinking block binding, compaction আর code execution।

///

## ইনস্টল { #install }

`AnthropicModel` ব্যবহার করতে, `pydantic-ai`, বা `anthropic` ঐচ্ছিক group-সহ `pydantic-ai-slim` ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[anthropic]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Anthropic](https://anthropic.com) ব্যবহার করতে, একটি API key তৈরি করতে [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)-এ যান।

`AnthropicModelName`-এ উপলব্ধ Anthropic মডেলের একটি তালিকা আছে।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export ANTHROPIC_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `AnthropicModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('anthropic:claude-sonnet-5-5')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

model = AnthropicModel('claude-sonnet-5-5')
agent = Agent(model)
...
```

/// note | Claude Opus 4.7 / 4.8 / 5 / 5.5-এ স্থানান্তর

Anthropic-এর [Claude Opus migration guide](https://platform.claude.com/docs/en/about-claude/models/migration-guide) Opus 4.7, 4.8, 5 আর 5.5-এর রিকোয়েস্ট থেকে `temperature`, `top_p` আর `top_k` সরিয়ে দেওয়ার পরামর্শ দেয়। Pydantic AI `claude-opus-4-7`, `claude-opus-4-8`, `claude-opus-5`, `claude-opus-5-5`, `claude-sonnet-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`, `claude-fable-5` আর `claude-mythos-5`-এর জন্য সেই key নিজে থেকে বাদ দেয়, `extra_body` override-সহ।

একই গাইড Opus 4.6 থেকে স্থানান্তরের সময় `max_tokens` আর token-সংখ্যার যেকোনো অনুমান আবার মূল্যায়ন করার পরামর্শও দেয়, কারণ Opus 4.7 হালনাগাদ tokenization এনেছে (4.8-এও বহাল)। `count_tokens()` বা `count_tokens_before_request`-এর ওপর নির্ভর করলে, নতুন মডেলের সাথে আপনার সীমা যাচাই করুন।

///

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

model = AnthropicModel(
    'claude-sonnet-5-5', provider=AnthropicProvider(api_key='your-api-key')
)
agent = Agent(model)
...
```

## নিজের HTTP client { #custom-http-client }

একটি নিজের `httpx2.AsyncClient` দিয়ে `AnthropicProvider` নিজের মতো করতে পারেন:

```python
from httpx2 import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

custom_http_client = AsyncClient(timeout=30)
model = AnthropicModel(
    'claude-sonnet-5-5',
    provider=AnthropicProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

একটি পুরনো `httpx.AsyncClient` গৃহীত হয় না: `anthropic` 1.0 `httpx2`-এর ওপর তৈরি আর client তৈরির সময়েই একটি প্রত্যাখ্যান করে।

provider যে `AsyncAnthropic` client বানায় সেটিও নিজে ব্যর্থ রিকোয়েস্ট আবার চেষ্টা করে — ডিফল্টভাবে `max_retries=2`, তাই আপনার কোড এরর দেখার আগে একটি রিকোয়েস্ট নেটওয়ার্কে সর্বোচ্চ তিনবার পৌঁছাতে পারে। retry নীতি শুধু আপনার transport-এ রাখতে, নিজে client বানালে (যেমন `anthropic_client=` হিসেবে) `max_retries=0` দিন, বা client না বানিয়ে সংখ্যা বদলাতে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) সেট করুন, একটি `AsyncAnthropicBedrock` বা `AsyncAnthropicVertex` client-সহ। এই স্তর কখন চলে তা দেখুন [Provider SDK retries](../retries.md#provider-sdk-retries)-এ।

## মডেল সেটিং { #model-settings }

[`AnthropicModelSettings`][pydantic_ai.models.anthropic.AnthropicModelSettings] দিয়ে মডেলের আচরণ নিজের মতো করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-sonnet-5-5')
settings = AnthropicModelSettings(
    anthropic_effort='low',
    service_tier='auto',
)
agent = Agent(model, model_settings=settings)
...
```

Anthropic-এ [`max_tokens`][pydantic_ai.settings.ModelSettings.max_tokens] বাধ্যতামূলক, আর thinking এতে গোনা হয়। আপনি সেট না করলে, Pydantic AI মডেলের সর্বোচ্চ আউটপুট পাঠায়, যেমন Claude Sonnet 4.5-এ 64,000 বা Claude Opus 5 আর Claude Haiku 5.5-এ 128,000, আর পেছনে রিকোয়েস্টটি stream করে, কারণ এত দীর্ঘ একটি উত্তরে 10 মিনিটের বেশি লাগতে পারে। একটি [`timeout`][pydantic_ai.settings.ModelSettings.timeout] তখন পুরো উত্তর নয়, stream করা টুকরোগুলোর মাঝের অপেক্ষা সীমিত করে। যে মডেলের সর্বোচ্চ জানা নেই সেটি পায় 16384, আর Claude Sonnet 4.5-এর চেয়ে পুরনো মডেল পায় 4096, কারণ যে রিকোয়েস্টের ইনপুট আর `max_tokens` মিলে context window ছাড়ায় সেগুলো তারা প্রত্যাখ্যান করে। মডেল নাম দিয়ে চেনা হয়, তাই একটি Bedrock ARN বা নিজের deployment নাম দিয়ে একটিতে পৌঁছালে নিজে `max_tokens` সেট করুন।

### Service tier { #service-tier }

দেরি আর throughput সামলাতে Anthropic [service tier](https://platform.claude.com/docs/en/api/service-tiers) নিয়ন্ত্রণ সমর্থন করে।
একীভূত [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] ফিল্ড বা provider-নির্দিষ্ট [`anthropic_service_tier`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_service_tier] ফিল্ড ব্যবহার করতে পারেন। দুটোই সেট থাকলে `anthropic_service_tier` একীভূত ফিল্ডের ওপর অগ্রাধিকার পায়, আর Anthropic-এর নিজস্ব মান নেয় (`'auto'` বা `'standard_only'`)।

Anthropic-এর জন্য একীভূত ফিল্ড এভাবে ম্যাপ হয়:

- `'auto'`: `'auto'` হিসেবে পাঠানো হয় (Anthropic-এর নিজস্ব মান — উপলব্ধ থাকলে priority ক্ষমতা ব্যবহার করে)।
- `'default'`: `'standard_only'`-এ ম্যাপ হয় (standard tier বাধ্য করে, priority ক্ষমতা থেকে বেরিয়ে আসে)।
- `'flex'` আর `'priority'` Anthropic-এর tier মডেলের অংশ নয় আর নিঃশব্দে উপেক্ষিত হয়।

## Cloud প্ল্যাটফর্মের সংযোগ { #cloud-platform-integrations }

[`AnthropicProvider`][pydantic_ai.providers.anthropic.AnthropicProvider]-এ একটি নিজের client দিয়ে cloud প্ল্যাটফর্মের মাধ্যমে Anthropic মডেল ব্যবহার করতে পারেন।

### AWS Bedrock { #aws-bedrock }

[AWS Bedrock](https://aws.amazon.com/bedrock/claude/) দিয়ে Claude মডেল ব্যবহার করতে, একটি Bedrock client কীভাবে সেট আপ করবেন তা নিয়ে [Anthropic ডকুমেন্টেশন](https://platform.claude.com/docs/en/build-with-claude/claude-in-amazon-bedrock) অনুসরণ করুন আর তারপর `AnthropicProvider`-এ দিন। নতুন `AsyncAnthropicBedrockMantle` client (Anthropic-এর প্রস্তাবিত, Messages API ব্যবহার করে) আর পুরনো `AsyncAnthropicBedrock` client (ARN-সংস্করণ মডেল ID-সহ `InvokeModel` API ব্যবহার করে) দুটোই সমর্থিত:

```python
from anthropic import AsyncAnthropicBedrockMantle

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

bedrock_client = AsyncAnthropicBedrockMantle()  # Uses AWS credentials from environment
provider = AnthropicProvider(anthropic_client=bedrock_client)
model = AnthropicModel('anthropic.claude-haiku-4-5', provider=provider)
agent = Agent(model)
...
```

/// note | Bedrock বনাম BedrockConverseModel

এই পদ্ধতি AWS Bedrock credential-সহ Anthropic-এর SDK ব্যবহার করে। সরাসরি AWS SDK (boto3) ব্যবহারের একটি বিকল্পের জন্য দেখুন [`BedrockConverseModel`](bedrock.md)।

///

/// note | পুরনো `AsyncAnthropicBedrock` client-এ tool search

`AsyncAnthropicBedrock` client-এ, `strategy` ছাড়া [`ToolSearch`][pydantic_ai.capabilities.ToolSearch] `'bm25'`-এর বদলে `'regex'` [tool search](../tools-advanced.md#tool-search) রূপ ব্যবহার করে। BM25 ব্যবহার করতে `ToolSearch(strategy='bm25')` দিন, যা পুরনো `InvokeModel` API-ও নেয়। এই client-এ যেকোনো রূপের জন্য Claude Sonnet 4.5-এর `tool-search-tool-2025-10-19` beta লাগে: [`AnthropicModelSettings`][pydantic_ai.models.anthropic.AnthropicModelSettings]-এ `anthropic_betas=['tool-search-tool-2025-10-19']` দিয়ে যোগ করুন। বার্তার ইতিহাসে রেকর্ড করা একটি `bm25` সার্চ এই client-এ `regex` হিসেবে আবার চলে, যদি না রান `ToolSearch(strategy='bm25')` ব্যবহার করে।

///

/// note | পুরনো `AsyncAnthropicBedrock` client-এ token গোনা

Anthropic SDK Bedrock-এ তার উচ্চ-স্তরের token-গোনার মেথড আটকে রাখে, তাই `count_tokens()` (আর `count_tokens_before_request`) বদলে Bedrock-এর নিজের `/model/{model}/count-tokens` endpoint ডাকে। সেই endpoint শুধু **মূল** foundation-model ID নেয় (যেমন `anthropic.claude-sonnet-4-20250514-v1:0`); cross-region inference profile ID (`us.`/`eu.`/`global.` উপসর্গ) আর জীবনকাল-শেষ মডেল সংস্করণ Bedrock প্রত্যাখ্যান করে।

///

/// note | পুরনো `AsyncAnthropicBedrock` client-এ structured output

Bedrock কিছু Claude মডেল থেকে structured output সরিয়ে রাখে যা সরাসরি Anthropic API-তে আছে, যেমন Claude Fable 5। `AsyncAnthropicBedrock` client-এ, সেই মডেলগুলো `strict` টুলের সংজ্ঞা পাঠায় না, একটি সাধারণ গোছানো `output_type` [Native Output](../output.md#native-output) ব্যবহার করে না, আর একটি স্পষ্ট [`NativeOutput`][pydantic_ai.output.NativeOutput] একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে, [`BedrockConverseModel`](bedrock.md#thinking-and-structured-output)-এর মতোই।

///

### Google Cloud { #google-cloud }

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude) দিয়ে Claude মডেল ব্যবহার করতে, একটি `AsyncAnthropicVertex` client কীভাবে সেট আপ করবেন তা নিয়ে [Anthropic ডকুমেন্টেশন](https://docs.anthropic.com/en/api/claude-on-vertex-ai) অনুসরণ করুন আর তারপর `AnthropicProvider`-এ দিন:

```python
from anthropic import AsyncAnthropicVertex

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

vertex_client = AsyncAnthropicVertex(region='us-east5', project_id='your-project-id')
provider = AnthropicProvider(anthropic_client=vertex_client)
model = AnthropicModel('claude-sonnet-5-5', provider=provider)
agent = Agent(model)
...
```

### Microsoft Foundry { #microsoft-foundry }

[Microsoft Foundry](https://ai.azure.com/) দিয়ে Claude মডেল ব্যবহার করতে, একটি `AsyncAnthropicFoundry` client কীভাবে সেট আপ করবেন তা নিয়ে [Anthropic ডকুমেন্টেশন](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry) অনুসরণ করুন আর তারপর `AnthropicProvider`-এ দিন:

```python
from anthropic import AsyncAnthropicFoundry

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider

foundry_client = AsyncAnthropicFoundry(
    api_key='your-foundry-api-key',  # Or set ANTHROPIC_FOUNDRY_API_KEY
    resource='your-resource-name',
)
provider = AnthropicProvider(anthropic_client=foundry_client)
model = AnthropicModel('claude-sonnet-5-5', provider=provider)
agent = Agent(model)
...
```

Entra ID প্রমাণীকরণসহ সেটআপের নির্দেশনার জন্য দেখুন [Anthropic-এর Microsoft Foundry ডকুমেন্টেশন](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry)।

## Task budget (Beta) { #task-budgets-beta }

Anthropic-এর [task budget](https://platform.claude.com/docs/en/build-with-claude/task-budgets) দিয়ে আপনি Claude-কে একটি পুরো এজেন্ট-loop-এর জন্য একটি পরামর্শমূলক token বাজেট দিতে পারেন — thinking, টুল কল, টুল ফল আর আউটপুটসহ — যাতে বাজেট খরচ হতে হতে মডেল নিজের গতি ঠিক করে আর সুন্দরভাবে শেষ করে। এগুলো কনফিগার করুন [`AnthropicModelSettings.anthropic_task_budget`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_task_budget] দিয়ে, যা একটি [`AnthropicTaskBudget`][pydantic_ai.models.anthropic.AnthropicTaskBudget] payload নেয় আর `output_config.task_budget`-এ ম্যাপ হয়।

এই সেটিং থাকলে Pydantic AI নিজে থেকে Anthropic-এর প্রয়োজনীয় `task-budgets-2026-03-13` beta চালু করে। বর্তমান সমর্থিত-মডেলের তালিকার জন্য দেখুন Anthropic-এর [task budget feature support](https://platform.claude.com/docs/en/build-with-claude/task-budgets#feature-support)। Task budget বর্তমানে Bedrock বা Vertex-এ সমর্থিত বলে নথিভুক্ত নয়। Microsoft Foundry-র জন্য, Microsoft-এর [Claude model capability list](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/claude-models#available-claude-models) দেখুন।

```python title="anthropic_task_budget.py"
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings

model = AnthropicModel('claude-opus-4-8')
settings = AnthropicModelSettings(
    anthropic_task_budget={'type': 'tokens', 'total': 20_000},
)
agent = Agent(model, model_settings=settings)
...
```

Task budget [`anthropic_effort`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_effort]-এর সাথে মেলে: effort প্রতি-ধাপের reasoning-এর গভীরতা ঠিক করে, অথচ task budget loop-জুড়ে মোট কাজ সীমিত করে। দুটো ফিল্ডই শেষে একই `output_config` অবজেক্টের নিচে যায়।

/// note | মনে রাখুন

Task budget পরামর্শমূলক, কঠিন সীমা নয়; একটি প্রয়োগ করা ছাদের জন্য এগুলোকে [`max_tokens`][pydantic_ai.settings.ModelSettings.max_tokens]-এর সাথে জুড়ুন।

///

### Compaction-জুড়ে বাজেট বহন { #carrying-budgets-across-compaction }

সার্ভার-পক্ষের compaction-এর জন্য [`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction] ব্যবহার করলে, এই অংশ বাদ দিতে পারেন: সার্ভার নিজেই গণনা রাখে, তাই `remaining` সেট না করে `total`-কে নিজে নিয়ন্ত্রিত হতে দিন।

`task_budget`-এর `remaining` ফিল্ড হলো *client-পক্ষের* compaction ধরনের জন্য, যেখানে আপনি রিকোয়েস্টের মাঝে নিজেই আগের দফার সারাংশ করেন, তাই নতুন করে লেখার আগে কত বাজেট খরচ হয়েছিল সার্ভারের মনে থাকে না। Pydantic AI আপনার হয়ে `remaining` ট্র্যাক করে না — রিকোয়েস্ট-জুড়ে token ব্যবহার নিজে জমা করুন (যেমন প্রতিটি রানের [`RunUsage`][pydantic_ai.usage.RunUsage] থেকে) আর পরের রিকোয়েস্টে হালনাগাদ মান দিন, যাতে গণনা `total`-এ রিসেট না হয়ে যেখানে থেমেছিল সেখান থেকে চলে। `remaining` সেট করলে বাজেট থাকা যেকোনো prompt-cache prefix-ও অবৈধ হয়, তাই caching রাখতে চাইলে, একবার `total` সেট করে সার্ভারকে চলমান গণনার বিপরীতে নিজে নিয়ন্ত্রিত হতে দিন।

/// warning | সতর্কতা

`task_budget.remaining` [`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction]-এর সাথে পরস্পর-বর্জনশীল: দুটো মেলানো রিকোয়েস্ট Anthropic প্রত্যাখ্যান করে, কারণ সার্ভার-পক্ষের compaction নিজেই বাজেট ট্র্যাক করে। এই মিশ্রণ কনফিগার করা থাকলে Pydantic AI রিকোয়েস্ট পাঠানোর আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে। একটি বাছুন: client-পক্ষের বাজেট ট্র্যাকিংয়ের জন্য `remaining`, বা সার্ভার-পক্ষের compaction-এর জন্য [`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction]।

///

## Prompt caching { #prompt-caching }

আপনার prompt-এর অংশ cache করে খরচ কমাতে Anthropic [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) সমর্থন করে। Pydantic AI একীভূত `cache` সেটিং, আর Anthropic-এর automatic caching, প্রতি-ব্লক বার্তা caching আর স্পষ্ট cache breakpoint সমর্থন করে:

### একীভূত `cache` সেটিং { #unified-cache-setting }

prompt caching চালুর provider-নিরপেক্ষ উপায় হলো একীভূত [`ModelSettings.cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং (বা [`Caching`][pydantic_ai.capabilities.Caching] capability), যা প্রতিটি সমর্থনকারী provider-এ একইভাবে কাজ করে:

```python title="anthropic_unified_cache.py"
from pydantic_ai import Agent

agent = Agent(
    'anthropic:claude-opus-5-5',
    instructions='You are a helpful assistant.',
    model_settings={'cache': True},
)
```

Anthropic-এ, `cache=True` (বা `cache='1h'`-এর মতো একটি ধরে রাখার সময়) টুলের সংজ্ঞা আর স্থির নির্দেশনার শেষে cache breakpoint বসায়, নিচের `anthropic_cache_tool_definitions` আর `anthropic_cache_instructions`-এর মতো, তাই একটি নতুন কথোপকথন আগেরগুলোর সাথে ভাগ করা prefix আবার পড়ে। এটি কথোপকথন cache করে automatic caching দিয়ে, `anthropic_cache`-এর মতো, বা, automatic caching সমর্থন করে না এমন মডেলসহ পুরনো `AsyncAnthropicBedrock` client-এ, কথোপকথনের শেষে একটি breakpoint দিয়ে (দেখুন [Automatic Caching](#automatic-caching))। cache লেখার খরচ 5-মিনিটের cache-এ input দামের 1.25 গুণ আর 1-ঘণ্টার cache-এ 2 গুণ, আর cache পড়া 0.1 গুণ; ভারসাম্য, Pydantic AI-এর prefix-স্থিতিশীলতার নিশ্চয়তা আর cache-এর দক্ষতা পর্যবেক্ষণের জন্য দেখুন [Caching](../capabilities/caching.md)। নিচের provider-নির্দিষ্ট `anthropic_cache*` সেটিং কোনোটি সেট থাকলে অগ্রাধিকার পায়, আর আরও সূক্ষ্ম নিয়ন্ত্রণ দেয়।

/// info | খরচের হিসাব, সহজ ভাষায়

ধরুন ১০,০০০ token-এর একটি স্থির prompt। প্রথমবার cache-এ লিখতে ১.২৫ গুণ দাম (৫ মিনিটের cache), কিন্তু পরের প্রতিটি রিকোয়েস্টে পড়তে মাত্র ০.১ গুণ। তাই একই prefix দুই-তিনবারের বেশি ব্যবহার হলেই caching লাভজনক।

///

### Automatic caching { #automatic-caching }

automatic caching ব্যবহারের Anthropic-নির্দিষ্ট উপায় হলো [`AnthropicModelSettings.anthropic_cache`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache]। এটি Anthropic-এর [automatic caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#automatic-caching) ব্যবহার করে, একটি শীর্ষ-স্তরের `cache_control` প্যারামিটার পাঠিয়ে, যাতে সার্ভার প্রতিটি রিকোয়েস্টের শেষ cache-যোগ্য ব্লকে নিজে থেকে একটি cache breakpoint প্রয়োগ করে:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

handbook = '...'  # a long document, above the model's minimum cacheable length

agent = Agent(
    'anthropic:claude-opus-5-5',
    instructions=f'Answer questions about this employee handbook:\n\n{handbook}',
    model_settings=AnthropicModelSettings(
        anthropic_cache=True,
    ),
)

result1 = agent.run_sync('How many vacation days do new employees get?')

result2 = agent.run_sync('And after five years?', message_history=result1.all_messages())
print(f'Cache write: {result1.response.usage.cache_write_tokens}')
print(f'Cache read: {result2.response.usage.cache_read_tokens}')
print(f'Cache hit ratio: {result2.response.usage.cache_hit_ratio}')
```

এটি বহু-দফার কথোপকথনের জন্য আদর্শ, যেখানে কথোপকথন বাড়ার সাথে cache breakpoint এগিয়ে যাওয়া উচিত। `anthropic_cache='1h'` দিয়ে একটি নিজের TTL-ও দিতে পারেন।

`AsyncAnthropicBedrockMantle`, `AsyncAnthropicVertex` আর `AsyncAnthropicFoundry` client automatic caching সমর্থন করে। পুরনো `AsyncAnthropicBedrock` client এটি ব্যবহার করে সেই মডেলগুলোতে যা Anthropic Messages API অবকাঠামো থেকে পরিবেশিত বলে [নথিভুক্ত করে](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy#api-model-ids)। অন্য মডেলে, `anthropic_cache` শেষ user বার্তায় প্রতি-ব্লক caching-এ ফিরে যায়, যা বহু-দফার কথোপকথনকে একই সুবিধা দেয়।

একটি মডেল automatic caching ব্যবহার করে কিনা তা আসে এর [profile](overview.md#models-and-providers)-এর `supports_auto_cache` থেকে, `anthropic_cache` আর একীভূত `cache` সেটিং দুটোর জন্যই। একটি মডেল বা প্ল্যাটফর্ম এটি সমর্থন করে তা Pydantic AI এখনো না জানলে, ফ্ল্যাগটি নিজে সেট করুন:

```python
from anthropic import AsyncAnthropicBedrock

from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.profiles.anthropic import AnthropicModelProfile
from pydantic_ai.providers.anthropic import AnthropicProvider

model = AnthropicModel(
    'us.anthropic.claude-sonnet-4-6',
    provider=AnthropicProvider(anthropic_client=AsyncAnthropicBedrock()),
    profile=AnthropicModelProfile(supports_auto_cache=True),
)
```

এটি `False` সেট করলে `anthropic_cache` প্রতি-ব্লক বিকল্প ব্যবহার করে, যা শীর্ষ-স্তরের প্যারামিটার নেয় না এমন Anthropic-সামঞ্জস্যপূর্ণ gateway-তে সাহায্য করতে পারে।

### প্রতি-ব্লক বার্তা caching { #per-block-message-caching }

`anthropic_cache`-এর বিকল্প হিসেবে, [`AnthropicModelSettings.anthropic_cache_messages`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_messages] Anthropic-এর শীর্ষ-স্তরের automatic caching প্যারামিটারের বদলে চূড়ান্ত বার্তার শেষ বিষয়বস্তু ব্লকে প্রতি-ব্লক `cache_control` যোগ করে। এটি ব্যবহার করুন Anthropic-সামঞ্জস্যপূর্ণ gateway আর proxy-র (যেমন MiniMax, OpenRouter বা LiteLLM) সাথে, যা Anthropic বার্তা ফরম্যাট নেয় কিন্তু শীর্ষ-স্তরের automatic caching সমর্থন করে না:

```python
from anthropic import AsyncAnthropic

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
from pydantic_ai.providers.anthropic import AnthropicProvider

client = AsyncAnthropic(
    api_key='your-api-key',
    base_url='https://your-anthropic-compatible-gateway.example.com',
)

model = AnthropicModel(
    'claude-sonnet-5-5',
    provider=AnthropicProvider(anthropic_client=client),
)
agent = Agent(
    model,
    model_settings=AnthropicModelSettings(
        anthropic_cache_messages=True,
    ),
)

result = agent.run_sync('What is the capital of France?')
print(result.output)
```

`anthropic_cache_messages='1h'` দিয়ে একটি নিজের TTL-ও দিতে পারেন। `anthropic_cache_messages` `anthropic_cache`-এর সাথে মেলানো যায় না।

### স্পষ্ট cache breakpoint { #explicit-cache-breakpoints }

automatic caching ছাড়াও, Pydantic AI নির্দিষ্ট বিষয়বস্তুতে cache breakpoint বসানোর কয়েকটি উপায় দেয়:

1. **[`CachePoint`][pydantic_ai.messages.CachePoint] দিয়ে user বার্তা cache করুন**: আগের সবকিছু cache করতে আপনার user বার্তায় একটি `CachePoint` চিহ্ন বসান
2. **চূড়ান্ত বার্তা ব্লক cache করুন**: [`AnthropicModelSettings.anthropic_cache_messages`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_messages] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন
3. **System নির্দেশনা cache করুন**: [`AnthropicModelSettings.anthropic_cache_instructions`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_instructions] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন
4. **টুলের সংজ্ঞা cache করুন**: [`AnthropicModelSettings.anthropic_cache_tool_definitions`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_tool_definitions] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন

এক-ঘণ্টার breakpoint একটি পাঁচ-মিনিটেরটির পরে এলে Anthropic রিকোয়েস্ট প্রত্যাখ্যান করে (এটি আগে টুল, তারপর system নির্দেশনা, তারপর বার্তা প্রক্রিয়া করে), তাই একটি এক-ঘণ্টার breakpoint, কথোপকথনের শেষের automatic caching-এরটিসহ, পাঁচ-মিনিটেরগুলোর পরে এলে, সেই আগের breakpoint-গুলো এক ঘণ্টায় তোলা হয়।

#### উদাহরণ: পূর্ণাঙ্গ caching কৌশল { #example-comprehensive-caching-strategy }

সর্বোচ্চ সাশ্রয়ের জন্য automatic caching-কে স্পষ্ট breakpoint-এর সাথে মেলান। automatic caching কথোপকথন সামলায়, অথচ স্পষ্ট breakpoint system নির্দেশনা আর টুলের সংজ্ঞা আটকে রাখে:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Detailed instructions...',
    model_settings=AnthropicModelSettings(
        anthropic_cache=True,                   # Server auto-caches last block
        anthropic_cache_instructions=True,      # Explicitly cache system instructions
        anthropic_cache_tool_definitions='1h',  # Explicitly cache tool definitions with 1h TTL
    ),
)

@agent.tool
def search_docs(ctx: RunContext, query: str) -> str:
    """Search documentation."""
    return f'Results for {query}'


result = agent.run_sync('Search for Python best practices')
print(result.output)
```

### বুদ্ধিমান নির্দেশনা caching { #smart-instruction-caching }

স্থির আর গতিশীল দুই ধরনের [নির্দেশনা](../agent.md#instructions)-সহ `anthropic_cache_instructions` ব্যবহার করলে, Pydantic AI নিজে থেকে cache সীমানা সর্বোত্তম বিন্দুতে বসায়। স্থির নির্দেশনা (`Agent(instructions=...)` থেকে) গতিশীল নির্দেশনার (`@agent.instructions` ফাংশন বা [toolset](../toolsets.md) থেকে) আগে সাজানো হয়, আর cache point শেষ স্থির নির্দেশনা অংশের পরে বসানো হয়।

অর্থাৎ আপনার স্থিতিশীল, স্থির নির্দেশনা দক্ষভাবে cache হয়, অথচ গতিশীল নির্দেশনা (যা রিকোয়েস্টের মাঝে বদলাতে পারে) cache সীমানার বাইরে থাকে, তাই একটি পরিবর্তন cache করা স্থির নির্দেশনা অবৈধ করে না। তবে এটি তাদের পরের cache করা কথোপকথন অবৈধ করে, তাই কথোপকথনের মাঝে বদলানো নির্দেশনার জন্য [`on_change='append'`](../agent.md#appending-instruction-changes) ব্যবহার করুন, যা বদলে প্রতিটি পরিবর্তন ইতিহাসে জোড়ে; [অবিশ্বস্ত লেখা নির্দেশনার বাইরে রাখুন](../agent.md#untrusted-instruction-text)।

```python
from datetime import date

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    deps_type=str,
    instructions='You are a helpful customer service agent. Follow company policy.',  # (1)!
    model_settings=AnthropicModelSettings(
        anthropic_cache_instructions=True,  # (2)!
    ),
)


@agent.instructions
def dynamic_context(ctx: RunContext[str]) -> str:  # (3)!
    return f"Customer name: {ctx.deps}. Today's date: {date.today()}."


result = agent.run_sync('What is your return policy?', deps='Alice')
print(result.output)
```

1. স্থির নির্দেশনা রিকোয়েস্ট-জুড়ে cache হয়।
2. স্থির/গতিশীল সীমানায় বুদ্ধিমান cache বসানো চালু করে।
3. গতিশীল নির্দেশনা প্রতি রিকোয়েস্টে বদলায় আর cache হয় না।

### CachePoint দিয়ে সূক্ষ্ম নিয়ন্ত্রণ { #fine-grained-control-with-cachepoint }

cache-এর জায়গা নিখুঁতভাবে নিয়ন্ত্রণ করতে হাতে বসানো `CachePoint` চিহ্ন ব্যবহার করুন:

```python
from pydantic_ai import Agent, CachePoint

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Instructions...',
)

# Manually control cache points for specific content blocks
result = agent.run_sync([
    'Long context from documentation...',
    CachePoint(),  # Cache everything up to this point
    'First question'
])
print(result.output)
```

### Cache usage-এর পরিসংখ্যান দেখা { #accessing-cache-usage-statistics }

`result.usage` দিয়ে cache usage-এর পরিসংখ্যান দেখুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Instructions...',
    model_settings=AnthropicModelSettings(
        anthropic_cache=True,
    ),
)

result = agent.run_sync('Your question')
usage = result.usage
print(f'Cache write tokens: {usage.cache_write_tokens}')
print(f'Cache read tokens: {usage.cache_read_tokens}')
```

`cache_write_tokens` সব cache লেখা গোনে। এগুলোর কিছু এক-ঘণ্টার TTL ব্যবহার করলে, যার বিল Anthropic পাঁচ-মিনিটের লেখার চেয়ে বেশি হারে করে, `cache_write_1h_tokens` সেগুলো গোনে, আর সেগুলোর খরচ এক-ঘণ্টার হারে হিসাব হয়। Anthropic-এর নিজের সংখ্যাও `usage.details`-এ আছে: `'ephemeral_1h_input_tokens'`, আর [message compaction](#message-compaction)-এর সময় করা লেখার জন্য `'compaction_ephemeral_1h_input_tokens'`।

### Cache diagnostics { #cache-diagnostics }

একটি রিকোয়েস্ট অপ্রত্যাশিতভাবে cache miss করলে, Anthropic-এর [cache diagnostics](https://platform.claude.com/docs/en/build-with-claude/cache-diagnostics) আপনাকে কারণ বলতে পারে। [`AnthropicModelSettings.anthropic_cache_diagnostics`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_diagnostics] `True` সেট করুন, আর প্রতিটি রিকোয়েস্ট বার্তার ইতিহাসের সবচেয়ে সাম্প্রতিক Anthropic উত্তরকে তুলনার জন্য নাম দেয়। prompt prefix ভিন্ন হলে, উত্তরের [`provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এ Anthropic-এর ফলসহ একটি `'cache_diagnostics'` key থাকে, যেমন `{'cache_miss_reason': {'type': 'tools_changed', 'cache_missed_input_tokens': 3713}}`:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Instructions...',
    model_settings=AnthropicModelSettings(anthropic_cache=True, anthropic_cache_diagnostics=True),
)

result1 = agent.run_sync('Your question')
result2 = agent.run_sync('Follow-up question', message_history=result1.all_messages())
diagnostics = (result2.response.provider_details or {}).get('cache_diagnostics')
if diagnostics and (reason := diagnostics['cache_miss_reason']):
    print(f"Cache miss: {reason['type']}, {reason.get('cache_missed_input_tokens')} tokens")
```

`type` হলো `model_changed`, `system_changed`, `tools_changed`, `messages_changed`, `previous_message_not_found` বা `unavailable`-এর একটি। Anthropic কোনো ভিন্নতা না পেলে key-টি থাকে না, আর তুলনা তখনো শেষ না হলে `{'cache_miss_reason': None}` থাকে।

Diagnostics বিনামূল্যে আর caching-এ প্রভাব ফেলে না, তবে ডিফল্টভাবে বন্ধ: Anthropic এগুলো চাওয়া প্রতিটি রিকোয়েস্টের একটি স্বল্পস্থায়ী fingerprint রাখে (hash আর token সংখ্যা, prompt-এর বিষয়বস্তু নয়), আর HIPAA-চালু প্রতিষ্ঠানের জন্য এগুলো প্রত্যাখ্যান করে। এগুলো শুধু Claude API-তে পাওয়া যায়, তাই Bedrock, Vertex AI আর Microsoft Foundry-তে সেটিংটি উপেক্ষিত হয়।

### Cache point-এর সীমা { #cache-point-limits }

Anthropic প্রতি রিকোয়েস্টে সর্বোচ্চ 4টি cache point প্রয়োগ করে। আপনার রিকোয়েস্ট যাতে সবসময় এরর ছাড়া মেনে চলে, Pydantic AI নিজে থেকে এই সীমা সামলায়।

#### Cache point কীভাবে বরাদ্দ হয় { #how-cache-points-are-allocated }

Cache point কয়েকটি উৎস থেকে আসতে পারে:

1. **Automatic caching**: `anthropic_cache` দিয়ে (সার্ভার শেষ cache-যোগ্য ব্লকে 1টি cache point প্রয়োগ করে)
2. **চূড়ান্ত বার্তা ব্লক**: `anthropic_cache_messages` সেটিং দিয়ে (শেষ বার্তার বিষয়বস্তু ব্লকে cache point যোগ করে)
3. **System prompt**: `anthropic_cache_instructions` সেটিং দিয়ে (শেষ system prompt ব্লকে cache point যোগ করে)
4. **টুলের সংজ্ঞা**: `anthropic_cache_tool_definitions` সেটিং দিয়ে (শেষ টুল সংজ্ঞায় cache point যোগ করে)
5. **বার্তা**: `CachePoint` চিহ্ন দিয়ে (বার্তার বিষয়বস্তুতে cache point যোগ করে)

প্রতিটি সেটিং **সর্বোচ্চ 1টি cache point** ব্যবহার করে, তবে এগুলো মেলাতে পারেন — `anthropic_cache` আর `anthropic_cache_messages` ছাড়া, যা পরস্পর-বর্জনশীল। মোট 4 ছাড়ালে, Pydantic AI নিজে থেকে পুরনো বার্তা থেকে বাড়তি cache point ছেঁটে ফেলে।

#### উদাহরণ: automatic আর স্পষ্ট caching মেলানো { #example-combining-automatic-and-explicit-caching }

automatic caching আর স্পষ্ট breakpoint-সহ একটি এজেন্ট সংজ্ঞায়িত করুন:

```python
from pydantic_ai import Agent, CachePoint
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Detailed instructions...',
    model_settings=AnthropicModelSettings(
        anthropic_cache=True,                   # 1 cache point (server-applied)
        anthropic_cache_instructions=True,      # 1 cache point
        anthropic_cache_tool_definitions=True,  # 1 cache point
    ),
)

@agent.tool_plain
def my_tool() -> str:
    return 'result'


# 3 of 4 slots used (1 automatic + 1 instructions + 1 tools)
# Room for 1 more explicit CachePoint marker
result = agent.run_sync([
    'Context', CachePoint(),  # 4th cache point - OK
    'Question'
])
print(result.output)
usage = result.usage
print(f'Cache write tokens: {usage.cache_write_tokens}')
print(f'Cache read tokens: {usage.cache_read_tokens}')
```

#### স্বয়ংক্রিয় cache point সীমা { #automatic-cache-point-limiting }

সব উৎস থেকে স্পষ্ট cache point (সেটিং + `CachePoint` চিহ্ন) উপলব্ধ বাজেট ছাড়ালে, Pydantic AI নিজে থেকে **পুরনো বার্তার বিষয়বস্তু** থেকে বাড়তি cache point সরায় (সবচেয়ে সাম্প্রতিকগুলো রেখে)।

সেটিং থেকে 2টি স্পষ্ট cache point-সহ একটি এজেন্ট সংজ্ঞায়িত করুন:

```python
from pydantic_ai import Agent, CachePoint
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    instructions='Instructions...',
    model_settings=AnthropicModelSettings(
        anthropic_cache_instructions=True,      # 1 cache point
        anthropic_cache_tool_definitions=True,  # 1 cache point
    ),
)

@agent.tool_plain
def search() -> str:
    return 'data'

# Already using 2 cache points (instructions + tools)
# Can add 2 more CachePoint markers (4 total limit)
result = agent.run_sync([
    'Context 1', CachePoint(),  # Oldest - will be removed
    'Context 2', CachePoint(),  # Will be kept (3rd point)
    'Context 3', CachePoint(),  # Will be kept (4th point)
    'Question'
])
# Final cache points: instructions + tools + Context 2 + Context 3 = 4
print(result.output)
usage = result.usage
print(f'Cache write tokens: {usage.cache_write_tokens}')
print(f'Cache read tokens: {usage.cache_read_tokens}')
```

**মূল বিষয়**:
- System আর টুলের cache point **সবসময় রক্ষিত** থাকে
- `anthropic_cache` 1টি cache point হিসেবে গোনা হয়, ঠিক `anthropic_cache_instructions` আর `anthropic_cache_tool_definitions`-এর মতো
- সীমা ছাড়ালে বার্তার বাড়তি `CachePoint` চিহ্ন সবচেয়ে পুরনো থেকে নতুনের দিকে সরানো হয়
- এতে বার্তা-স্তরের caching-এর সুবিধা পেয়েও গুরুত্বপূর্ণ caching (নির্দেশনা/টুল) বজায় থাকে

## বয়ে আনা thinking { #carried-over-thinking }

ইতিহাসের একটি [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] যা Anthropic-এর নিজস্ব reasoning চ্যানেলে চড়তে পারে না — বেশিরভাগ সময় কারণ এর signature আপনার storage-এর আসা-যাওয়ায় টেকেনি — তা পাঠানো হয় যে assistant দফা থেকে এসেছে তার আগে নিজস্ব একটি `user` বার্তায় লেখা হিসেবে, একটি `<assistant_thinking>` ট্যাগে মোড়া। এ কারণেই একটি রিকোয়েস্টে এমন একটি `user` দফা থাকতে পারে যা আপনি কখনো লেখেননি। assistant দফা কেন এর ভুল জায়গা, আর বেরিয়ে আসার উপায়, তা দেখুন [thinking পেজে](../capabilities/thinking.md#carried-over-thinking)।

## কথোপকথনের মাঝের system বার্তা { #mid-conversation-system-messages }

একটি দীর্ঘ session-এর মাঝপথে এজেন্টের `system_prompt`-এ একটি নির্দেশনা যোগ করলে prompt-এর সামনের অংশ নতুন করে লেখা হয়, যা তার পেছনের প্রতিটি cache করা prefix অবৈধ করে। Anthropic কথোপকথনের *ভেতরে* একটি system বার্তা নিয়ে তা এড়ায়, ইতিহাসে নির্দেশনার নিজের অবস্থানে, তার আগে নয়, তাই সেই বিন্দু পর্যন্ত cache করা সবকিছু cache-এ থাকে।

প্রথম [`ModelRequest`][pydantic_ai.messages.ModelRequest]-এর বাইরের যেকোনো [`SystemPromptPart`][pydantic_ai.messages.SystemPromptPart] কথোপকথনের মাঝের একটি নির্দেশনা — তা একটি সংরক্ষিত `message_history` থেকে আসুক বা একটি রানের সময় [`RunContext.enqueue`][pydantic_ai.tools.RunContext.enqueue] থেকে। বাড়তি কিছু চালু করতে হয় না:

```python title="mid_conversation_system_prompt.py"
from pydantic_ai import Agent, RunContext, SystemPromptPart

agent = Agent('anthropic:claude-opus-4-8', system_prompt='You are a code reviewer.')


@agent.tool
def require_type_annotations(ctx: RunContext) -> str:
    ctx.enqueue(SystemPromptPart(content='Every suggestion must include explicit type annotations.'))
    return 'rule added'
```

নির্দেশনাটি জায়গায় রাখলে তার আগের prefix আবার ব্যবহারযোগ্য থাকে, কিন্তু এটি নিজে caching চালু করে না — তা তবুও আসে [`anthropic_cache`](#automatic-caching), `anthropic_cache_messages`, বা একটি স্পষ্ট [`CachePoint`][pydantic_ai.messages.CachePoint] থেকে। একটি enqueue করা ব্যাচের শেষে একটি `CachePoint` সেই ব্যাচে তার আগের সবকিছু cache করে, নির্দেশনাসহ। পরে আরও বিষয়বস্তুসহ একটি `CachePoint` যেখানে রেখেছেন সেখান পর্যন্ত cache করে আর নির্দেশনাকে বাইরে রাখে: নির্দেশনাটি তার সঙ্গী বিষয়বস্তুর পরে পাঠানো হয়, তাই এটি এমন একটি সীমানার ভেতরে থাকতে পারে না যার বাইরে সেই বিষয়বস্তু।

সমর্থন মডেল আর transport ভেদে আলাদা — [Microsoft Foundry](#microsoft-foundry) সংযোগ role-টি দেয় না, আর কিছু Claude মডেল এন্ট্রিটি নেয় কিন্তু সে অনুযায়ী কাজ করে না। বর্তমান তালিকা আছে Anthropic-এর [mid-conversation system messages ডক](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)-এ। Pydantic AI আপনার ব্যবহৃত মডেল আর transport-এ কাজ করে এমন render বাছে, একই অবস্থানে একটি `<system>`-ট্যাগ করা user বার্তায় ফিরে গিয়ে, তাই যেকোনোভাবেই নির্দেশনাটি যেখানে রেখেছেন সেখান থেকে প্রযোজ্য।

দুটোর পার্থক্য দেখা দেয় এমন নির্দেশনায় যা একটি মডেলের তার user-এর কাছ থেকে নিতে সতর্ক থাকা *উচিত*: নিজস্ব এন্ট্রি পেলে, Claude তার শীর্ষ-স্তরের prompt-এর বসানো একটি নিষেধাজ্ঞা তুলে নেবে, আর একই লেখা একটি `<system>` ট্যাগে পেলে প্রত্যাখ্যান করে। অবিশ্বাসের কিছু নেই এমন নির্দেশনায়, যেমন ফরম্যাট বদল, দুটোই কাজ করে।

এগুলো provider-জুড়ে কেমন আচরণ করে, কীভাবে একটি লিখবেন, আর অবিশ্বস্ত বিষয়বস্তু কেন এতে রাখা উচিত নয়, তা দেখুন [mid-conversation system prompts](../message-history.md#mid-conversation-system-prompts)-এ।

/// note | অবস্থান

Anthropic চায় একটি system বার্তা একটি user দফা আর মডেলের উত্তরের মাঝে বসুক, তাই একটি ইতিহাস ইতিমধ্যে তা না মানলে Pydantic AI অবস্থান একটু সরায়: সাথে কোনো user বিষয়বস্তু ছাড়া আসা একটি নির্দেশনার পরে একটি ন্যূনতম `.` user বার্তা যোগ হয়, আর যেটি আরেকটি user দফার আগে বসত সেটি যে উত্তর নিয়ন্ত্রণ করে তার ঠিক আগে সরে। কোনোটিই বদলায় না নির্দেশনাটি কোন দফায় প্রযোজ্য — শুধু তারে কোথায় বসে।

///

### বারবার একই prompt-এ প্রত্যাখ্যান { #refusals-on-repeated-prompts }

মডেলের আগের reasoning প্রসঙ্গে থাকা অবস্থায় একই user prompt বারবার আসে এমন একটি কথোপকথন Claude-এর `reasoning_extraction` classifier প্রত্যাখ্যান করতে পারে, আর একটি নির্দেশনা বদলানোর ঠিক পরে প্রত্যাখ্যানের সম্ভাবনা বেশি, নির্দেশনা নতুন করে লেখা হোক বা [জোড়া](../agent.md#appending-instruction-changes)। বৈচিত্র্যময় prompt আর টুল loop-সহ কথোপকথন পরীক্ষায় প্রভাবিত হয়নি। প্রত্যাখ্যান একটি [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] হিসেবে ছড়ায়। এটি পেলে, একটি [fallback model](overview.md#fallback-model) কনফিগার করুন বা [`ProcessHistory`][pydantic_ai.capabilities.ProcessHistory] দিয়ে ইতিহাস থেকে thinking সরান।

### দফা-সীমিত system বার্তা { #turn-scoped-system-messages }

একটি [শুধু-রিকোয়েস্টের](../message-history.md#request-scoped-system-prompts) `SystemPromptPart` (`scope='request'`) পাঠানো হয় একটি [turn-scoped system message](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages#turn-scoped-system-messages) হিসেবে: `clear_at: 'next_user_message'`-সহ একটি `{'role': 'system'}` এন্ট্রি, যা পরের একটি user দফা থাকলে API render করা বন্ধ করে, শুধু টুল ফল বহন করা একটিসহ। Pydantic AI এগুলোর প্রতিটি প্রতিটি রিকোয়েস্টের সাথে পাঠায়, বর্তমান হোক বা না হোক, আর আপনার হয়ে `mid-conversation-system-clear-at-2026-08-21` beta header যোগ করে।

এটি সবচেয়ে গুরুত্বপূর্ণ [preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)-সহ মডেলে, যেমন Claude Opus 5.5, Sonnet 5.5 আর Fable 5.1: তারা প্রতিটি thinking ব্লক যে হুবহু কথোপকথনে তৈরি হয়েছে তার সাথে বাঁধে, তাই পরের একটি রিকোয়েস্ট থেকে একটি আগের reminder মুছলে তার পরের প্রতিটি thinking ব্লক অবৈধ হয়, অথচ জায়গায় রেখে দেওয়া একটি মোছা এন্ট্রি হয় না। একটি মোছা এন্ট্রির কোনো input token খরচ নেই আর কখনো cache key-র অংশ নয়, তাই `anthropic_cache_messages` আর `anthropic_cache` তাদের breakpoint এর আগের বিষয়বস্তুতে বসায়।

সমর্থন কথোপকথনের মাঝের system বার্তা অনুসরণ করে, একই মডেল আর transport-এ। অন্যত্র, `system` role নেয় না এমন মডেলসহ, একটি শুধু-রিকোয়েস্টের prompt শুধু নিজের রিকোয়েস্টে `<system>`-ট্যাগ করা user লেখা হিসেবে পাঠানো হয়, আর cache breakpoint এর আগে যায়। এটি আছে এমন একটি মডেলে beta থেকে বেরিয়ে আসতে, যেমন আপনার account-এর প্রবেশাধিকার না থাকলে, profile ফ্ল্যাগ বন্ধ করুন; তখন শুধু-রিকোয়েস্টের prompt শুধু বর্তমান থাকাকালীন পাঠানো হয়:

```python title="request_scoped_opt_out.py"
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.profiles.anthropic import AnthropicModelProfile

model = AnthropicModel(
    'claude-opus-5-5',
    profile=AnthropicModelProfile(supports_request_scoped_system_prompts=False),
)
```

## Fast mode { #fast-mode }

Fast mode প্রতি সেকেন্ডে বেশি output token দেয় আর বর্তমানে সমর্থিত **Claude Opus 4.6**, **Claude Opus 4.7**, **Claude Opus 4.8**, **Claude Opus 5** আর **Claude Opus 5.5**-এ। এটি একটি research preview। চালু করতে [`anthropic_speed`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_speed] `'fast'` সেট করুন; Pydantic AI নিজে থেকে প্রয়োজনীয় `fast-mode-2026-02-01` beta যোগ করে। সমর্থিত নয় এমন মডেলে, `anthropic_speed='fast'` একটি `UserWarning`-সহ উপেক্ষিত হয়। দাম, rate limit আর সমর্থিত মডেলের সর্বশেষ তালিকার জন্য দেখুন [Anthropic fast mode ডক](https://platform.claude.com/docs/en/build-with-claude/fast-mode)।

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-opus-4-8',
    model_settings=AnthropicModelSettings(anthropic_speed='fast'),
)
...
```

/// note | Prompt cache-এর সাথে সম্পর্ক

`'fast'` আর `'standard'`-এর মধ্যে বদলালে prompt cache অবৈধ হয়। ভিন্ন গতির রিকোয়েস্ট cache করা prefix ভাগ করে না, তাই cache-সংবেদনশীল প্রতিটি কথোপকথনে একটি গতি বাছুন।

///

/// note | Bedrock, Vertex আর Foundry

Fast mode শুধু সরাসরি Anthropic API-তে পাওয়া যায়। Bedrock, Vertex আর Foundry client `speed` প্যারামিটার সমর্থন করে না, তাই সেই client-গুলোতে `anthropic_speed='fast'` একটি `UserWarning`-সহ উপেক্ষিত হয়।

///

## জোর করে টুল বাছাই { #forced-tool-choice }

বেশিরভাগ Anthropic মডেল [`tool_choice='required'`][pydantic_ai.settings.ModelSettings.tool_choice] (বা টুলের নামের একটি তালিকা) দিয়ে একটি টুল কল বাধ্য করতে দেয়, শুধু [extended thinking](../capabilities/thinking.md#anthropic) চালু থাকাকালীন ছাড়া। [Adaptive thinking](../capabilities/thinking.md#adaptive-thinking-effort) বাধ্য করা গ্রহণ করে, তবে Claude একটি বাধ্য টুল বাছাইয়ের উত্তর thinking ছাড়া দেয়। Anthropic নথিভুক্ত করে যে **Claude Fable 5.1**, **Claude Mythos 5.1**, **Claude Opus 5.5** আর **Claude Sonnet 5.5** একটি বাধ্য টুল বাছাই শর্তহীনভাবে প্রত্যাখ্যান করে, thinking ছাড়াও, আর Pydantic AI সেগুলোকে [`supports_forced_tool_choice=False`][pydantic_ai.profiles.ModelProfile.supports_forced_tool_choice] দিয়ে চিহ্নিত করে।

বাধ্য করা সমর্থন করে না এমন একটি মডেলে, বা extended thinking চালু থাকাকালীন:

- একটি স্পষ্ট `tool_choice='required'` (বা টুলের নামের একটি তালিকা) একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে; বদলে `tool_choice='auto'` ব্যবহার করুন।
- Pydantic AI আপনার হয়ে নির্ধারণ করা একটি `required` বাছাই (যেমন একটি [আউটপুট টুল](../output.md#tool-output) থেকে) নরমভাবে `'auto'`-তে ফিরে যায়। নির্ধারিত বাছাই একটি একক টুলের নাম দিলে, `tool_choice` `'auto'` থাকা অবস্থায় উপলব্ধ টুলের তালিকা সেই টুলে ছাঁটা হয়, যা Anthropic-এর prompt cache অবৈধ করে, কারণ cache করা prefix-এ টুলের array থাকে। তাই মডেল এটি না ডেকে লেখায় উত্তর দিতে পারে; একটি আউটপুট টুল বাধ্যতামূলক হলে, Pydantic AI একটি টুল ডাকার prompt দিয়ে আবার চেষ্টা করে।

Adaptive thinking চালু থাকাকালীন, একটি স্পষ্ট বাধ্য-করা `tool_choice` তবুও পাঠানো হয়, আর সেই রিকোয়েস্ট thinking ছাড়া ফেরত আসে। Pydantic AI আপনার হয়ে নির্ধারণ করা একটি বাধ্য বাছাই বদলে `'auto'`-তে ফিরে যায়, ওপরের মতো, তাই মডেল thinking চালিয়ে যায়।

[Tool Output](../output.md#tool-output) লেখা দিয়ে শেষ হতে পারে না এমন প্রতিটি রিকোয়েস্টে আউটপুট টুলের একটি কল বাধ্য করে, তাই একটি সাধারণ গোছানো `output_type` [Native Output](../output.md#native-output) ব্যবহার করে, যেখানে মডেল সমর্থন করে, যখনই রিকোয়েস্টটি thinking করে: একটি thinking সেটিং দিয়ে, বা [ডিফল্টভাবে thinking করা](../capabilities/thinking.md#adaptive-thinking-effort) একটি মডেলে কোনো সেটিং ছাড়া, যেমন Claude Opus 5 আর পরেরগুলো, Claude Sonnet 5, Claude Haiku 5.5, আর Claude Fable ও Mythos মডেল। JSON schema সমর্থন নেই এমন একটি মডেলে, extended thinking [Prompted Output](../output.md#prompted-output)-এ ফিরে যায়, আর adaptive thinking `tool_choice='auto'`-এর অধীনে আউটপুট টুল দিয়ে Tool Output রাখে। Tool Output রাখতে, মডেল অনুমতি দিলে `thinking=False` দিয়ে thinking বন্ধ করুন। একটি স্পষ্ট `ToolOutput(...)` Tool Output রাখে, `tool_choice='auto'`-এর অধীনে আউটপুট টুল দিয়ে।

আউটপুট mode রানের প্রথম রিকোয়েস্টে বাছাই হয় আর রানের বাকিটায় থাকে (একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর পেছনে ছাড়া, যেখানে প্রতিটি মডেল প্রতিটি রিকোয়েস্টে বাছে), তাই ধাপে ধাপে বদলানো একটি thinking সেটিং (একটি [`model_settings`][pydantic_ai.agent.Agent.__init__] callable বা একটি capability দিয়ে) রিকোয়েস্টের মাঝে আউটপুট টুল যোগ বা সরায় না আর [prompt cache অবৈধ করে](../capabilities/caching.md#what-invalidates-a-cache) না। Tool Output দিয়ে শুরু হওয়া একটি রান thinking চালু হলেও তা রাখে, `tool_choice='auto'`-এর অধীনে আউটপুট টুল দিয়ে।

## Thinking block binding { #thinking-block-binding }

**Claude Fable 5.1**, **Claude Opus 5.5**, **Claude Sonnet 5.5** আর **Claude Haiku 5.5** প্রতিটি thinking ব্লক যে কথোপকথন-prefix তা তৈরি করেছে তার সাথে বাঁধে। `system`, `tools` বা আগের `messages` বদলানোর পরে ইতিহাস আবার চালালে Anthropic [একটি 400 নথিভুক্ত করে](https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting) (`The block is bound to a different conversation`)। দুটি সাধারণ Pydantic AI সুবিধা prefix বদলায়:

- একটি [গতিশীল নির্দেশনা](../agent.md#instructions) ফাংশন যার লেখা রানভেদে আলাদা, যদি না এটি [`on_change='append'`](../agent.md#appending-instruction-changes) ব্যবহার করে, আর
- একটি [ছাঁকা toolset](../toolsets.md#filtering-tools) যা কথোপকথনের মাঝে একটি নতুন টুল দেখায়, যদি না টুলটি [deferred loading](../toolsets.md#deferred-loading) ব্যবহার করে।

দুটোই সেই একই অস্থিরতা যা [একটি provider-এর prompt cache খোয়ায়](../capabilities/caching.md#what-invalidates-a-cache): দফার মাঝে বদলানো একটি রিকোয়েস্ট prefix। thinking ব্লক একে এমন একটি 400 বানায় যা আপনি দেখতে পান; cache একে এমন একটি বিল বানায় যা দেখতে পান না — পরিবর্তনের পরের প্রতিটি রিকোয়েস্ট নিঃশব্দে cache-ছাড়া দামে পুরো কথোপকথন আবার পাঠায়। যেখানে prefix স্থির রাখা যায়, তা প্রত্যাখ্যান সামলানোর চেয়ে বেশি মূল্যবান।

Anthropic পরীক্ষাটি প্রয়োগ করে 31 আগস্ট 2026 বা পরে তৈরি account-এ। পুরনো একটি account-এ এটি অমিল রেকর্ড করে কিন্তু এরর ফেরত দেয় শুধু রিকোয়েস্ট `thinking.block_binding.prefix_mismatch_behavior` সেট করলে।

**Pydantic AI ডিফল্টভাবে কিছুই সেট করে না**, তাই একটি পুরনো account তার reasoning অছোঁয়া আবার চালাতে থাকে। যেখানে পরীক্ষা প্রয়োগ হয়, প্রত্যাখ্যাত রিকোয়েস্ট একবার আবার চেষ্টা হয় `prefix_mismatch_behavior='drop_block'` দিয়ে: পুরনো ব্লকটি বাদ পড়ে, রান চলতে থাকে, আর একটি [`AnthropicStaleThinkingBlockWarning`][pydantic_ai.models.anthropic.AnthropicStaleThinkingBlockWarning] ব্যাখ্যা করে কী ঘটেছে। **মডেল আর সেই দফার reasoning দেখে না** — বিনিময় হলো একটি দফার thinking বনাম একটি ব্যর্থ রান। শুধু [`anthropic_binds_thinking_blocks=True`][pydantic_ai.profiles.anthropic.AnthropicModelProfile.anthropic_binds_thinking_blocks] চিহ্নিত মডেলগুলোই আবার চেষ্টা করে। যে রিকোয়েস্টের thinking টাইপ `adaptive` নয়, যেমন `anthropic_thinking={'type': 'between_tools'}`, তা আবার চেষ্টা হয় না, কারণ Anthropic `block_binding` নেয় শুধু adaptive thinking-এর সাথে: বদলে সেই কথোপকথনের prefix স্থির রাখুন।

Anthropic বাদ দেওয়া একটি রিকোয়েস্টেই প্রয়োগ করে। এর উত্তর রূপান্তরটি রেকর্ড করে, তাই প্রভাবিত কথোপকথনের বাকিটায় `drop_block` পাঠাতে থাকতে Pydantic AI সেই উত্তরের ইতিহাস ব্যবহার করে। এতে মডেলে পরিবর্তনশীল অবস্থা না রেখে বা একটি অসম্পর্কিত কথোপকথন না বদলে পরের প্রতিটি দফায় আরেকটি প্রত্যাখ্যাত রিকোয়েস্ট এড়ানো যায়। একই আচরণ [`count_tokens()`][pydantic_ai.models.Model.count_tokens]-এ প্রযোজ্য: token গোনা প্রথম মেলা প্রত্যাখ্যান একবার আবার চেষ্টা করে, আর উদ্ধারের ইতিহাস বহন করা পরের গণনা সাথে সাথে বাদ পাঠায়। শুধু গোনার সময় দেখা একটি উদ্ধার শুধু পরের গণনায় প্রযোজ্য, কারণ সেই endpoint সার্ভার-পক্ষের টুল বাদ দেয় আর তাই inference থেকে ভিন্ন prefix থাকতে পারে। একটি স্পষ্ট `block_binding` গোনা আর inference দুটোতেই জেতে।

স্বয়ংক্রিয় আচরণ পাওয়া যায় সরাসরি Anthropic API, Pydantic AI Gateway আর অন্য `AsyncAnthropic`-সামঞ্জস্যপূর্ণ proxy, AWS-এ Claude Platform, পুরনো Amazon Bedrock, আর Google Vertex AI-তে। এটি চালু নয় AWS-পরিচালিত Bedrock Messages API client-এ (`AsyncAnthropicBedrockMantle`), যা Anthropic beta header নেয় না, বা Microsoft Foundry-তে, যেখানে এই beta বর্তমানে নথিভুক্ত নয়। স্পষ্ট সেটিং প্রতিটি transport-এ সরাসরি পাঠানো হয়।

Anthropic প্রতিটি বাদ জানায়, আর Pydantic AI তা দুভাবে দেখায়। [Instrumentation](../logfire.md)-এর অধীনে Pydantic AI মডেল রিকোয়েস্ট span একটি `anthropic.input_transformations` event বহন করে, তাই ঘটার সাথে সাথে একটি বাদ trace-এ দেখা যায়; একটি অসম্পর্কিত পারিপার্শ্বিক অ্যাপ্লিকেশন span কখনো বদলানো হয় না। উত্তরে এটি সবসময় `provider_details`-এ রেকর্ড থাকে:

```python title="dropped_thinking_blocks.py"
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse

agent = Agent('anthropic:claude-fable-5-1')
result = agent.run_sync('What is the capital of France?')

for message in result.new_messages():
    if isinstance(message, ModelResponse) and message.provider_details:
        for transformation in message.provider_details.get('input_transformations', []):
            print(transformation['path'], transformation['reason'])
```

প্রত্যাখ্যাত রিকোয়েস্ট — আর সতর্কবার্তা — এড়াতে, আগেই বাদ চেয়ে নিন। Pydantic AI একটি স্পষ্ট `block_binding` যেমন দেওয়া তেমন পাঠায়, ফিল্ডের প্রয়োজনীয় beta-সহ, আর কখনো আবার চেষ্টা করে না:

```python title="drop_stale_thinking_blocks.py"
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

settings: AnthropicModelSettings = {
    'anthropic_thinking': {
        'type': 'adaptive',
        'block_binding': {'prefix_mismatch_behavior': 'drop_block'},
    }
}
agent = Agent('anthropic:claude-fable-5-1', model_settings=settings)
...
```

reasoning না হারিয়ে জোরে ব্যর্থ হতে, একই জায়গায় `'error'` সেট করুন। আবার চেষ্টা রেখে কিন্তু এ নিয়ে আর না শুনতে, সতর্কবার্তাটি ছেঁকে ফেলুন:

```python title="silence_stale_thinking_block_warning.py"
import warnings

from pydantic_ai.models.anthropic import AnthropicStaleThinkingBlockWarning

warnings.simplefilter('ignore', AnthropicStaleThinkingBlockWarning)
```

তৃতীয় কোনো আচরণ নেই: `prefix_mismatch_behavior` হয় `'error'`, নয়তো `'drop_block'`। `None` দেওয়া হলো স্পষ্টভাবে Anthropic-এর account ডিফল্ট চাওয়ার উপায়, যা ব্লক রাখে শুধু যেখানে পরীক্ষা প্রয়োগ হয় না।

যে মডেল thinking ব্লক বাঁধে না সেগুলো *ডিফল্টভাবে* প্রভাবিত নয়: কোনো স্পষ্ট `block_binding` ছাড়া, তাদের রিকোয়েস্ট ফিল্ড বা binding beta কোনোটিই বহন করে না, আর তাদের একটি 400 কখনো আবার চেষ্টা হয় না। নিজে `block_binding` সেট করলে যেকোনো মডেলের জন্য দুটোই তারে যায় — beta profile ফ্ল্যাগ নয়, ফিল্ড অনুসরণ করে — আর এমন রিকোয়েস্টও কখনো আবার চেষ্টা হয় না। Anthropic নথিভুক্ত করে যে **Claude Mythos 5.1** এই পরীক্ষা চালায় না, তাই এটিও চিহ্নিত নয়।

## বার্তা compaction { #message-compaction }

দীর্ঘ কথোপকথন সামলাতে Anthropic [স্বয়ংক্রিয় context compaction](https://docs.anthropic.com/en/docs/build-with-claude/compaction) সমর্থন করে। input token একটি কনফিগার করা সীমা ছাড়ালে, API নিজে থেকে একটি সারাংশ তৈরি করে যা প্রসঙ্গ রক্ষা করে পুরনো বার্তার জায়গা নেয়।

Compaction-এর পরে, পরের রিকোয়েস্টগুলো শুধু compact করা window পাঠায়, সর্বশেষ compaction ব্লক থেকে পরেরটুকু, যা রিকোয়েস্টের আকার কমায় — API এমনিতেও আগের বিষয়বস্তু উপেক্ষা করে। স্থায়ী system prompt প্রভাবিত হয় না: এটি আলাদা `system` প্যারামিটার হিসেবে পাঠানো হয়, যা compaction বদলায় না।

Compaction চালু করার সবচেয়ে সহজ উপায় হলো [`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction] capability:

```python title="anthropic_compaction.py"
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicCompaction

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[AnthropicCompaction(token_threshold=100_000)],
)
```

Capability-টি নেয়:

- **`token_threshold`** (ডিফল্ট: 150,000, সর্বনিম্ন: 50,000): input token এই মান ছাড়ালে compaction ঘটে।
- **`instructions`**: সারাংশ কীভাবে তৈরি হবে তার নিজের নির্দেশনা।
- **`pause_after_compaction`**: `True` হলে, উত্তর compaction ব্লকের পরে `stop_reason='compaction'`-সহ থামে, চালিয়ে যাওয়ার আগে স্পষ্টভাবে সামলানোর সুযোগ দিয়ে।

বিকল্পভাবে, [`anthropic_context_management`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_context_management] দিয়ে মডেল সেটিংয়ে সরাসরি compaction কনফিগার করতে পারেন:

```python title="anthropic_compaction_settings.py"
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent('anthropic:claude-sonnet-5-5')
result = agent.run_sync(
    'Hello!',
    model_settings=AnthropicModelSettings(
        anthropic_context_management={
            'edits': [{'type': 'compact_20260112', 'trigger': {'type': 'input_tokens', 'value': 100_000}}]
        }
    ),
)
```

/// note | মনে রাখুন

Anthropic-এর ফেরত দেওয়া compaction ব্লকে পড়া যায় এমন লেখার সারাংশ থাকে। বার্তার ইতিহাসে থাকলে পরের রিকোয়েস্টে এগুলো নিজে থেকে আসা-যাওয়া করে।

///

## সার্ভার-পক্ষের টুল loop { #server-side-tool-loops }

[web search](../native-tools.md#web-search-tool)-এর মতো একটি সার্ভার-পক্ষের টুলসহ, Anthropic এক রিকোয়েস্টের মধ্যে মডেলকে কয়েকবার sample করতে পারে, প্রতিটি টুল-দফায় একবার। উত্তরের usage প্রতিটি পাস যোগ করে, যা Anthropic বিল করে, কিন্তু প্রতিটি পাস এ পর্যন্ত কথোপকথন আবার পড়ে, তাই যোগফল মডেলকে দেওয়া প্রসঙ্গের কয়েক গুণ হতে পারে। যে উত্তরে [compaction](#message-compaction) চলেছে তা একইভাবে compaction পাস আর তার পরের পাস যোগ করে, যা শুধু compact করা প্রসঙ্গ দেখেছিল।

Anthropic প্রতিটি পাস জানায় শুধু এমন একটি beta-র অধীনে যা `usage.iterations` ফেরত দেয়। এটি থাকলে, [`ctx.context_window_used`][pydantic_ai.tools.RunContext.context_window_used], [`per_request_input_tokens_limit`][pydantic_ai.usage.UsageLimits.per_request_input_tokens_limit], আর [harness compaction](../harness/compaction.md) শেষ পাসের input token দিয়ে প্রসঙ্গ মাপে, cache করা token-সহ। এটি ছাড়া, তারা যোগফল usage পড়ে।

[`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction] আর [`anthropic_context_management`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_context_management] `compact-2026-01-12` beta পাঠায়, আর [`AdvisorTool`][pydantic_ai.native_tools.AdvisorTool] আর [`anthropic_task_budget`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_task_budget] যে beta পাঠায় সেগুলোও `usage.iterations` ফেরত দেয়। অন্যথায়, compaction beta নিজে পাঠান:

```python title="anthropic_server_tool_loop_context.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import WebSearch
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[WebSearch()],
    model_settings=AnthropicModelSettings(anthropic_betas=['compact-2026-01-12']),
)
```

উত্তরের usage, আর তাই এর খরচ, যেকোনোভাবেই পাসগুলোর যোগফল থাকে।

## Code execution টুলের সংস্করণ { #code-execution-tool-version }

ডিফল্টভাবে, Pydantic AI বাছা মডেলের জন্য একটি সামঞ্জস্যপূর্ণ Anthropic code execution টুলের সংস্করণ বাছে। একটি নির্দিষ্ট সমর্থিত Anthropic টুল সংস্করণ দরকার হলে [`AnthropicModelSettings.anthropic_code_execution_tool_version`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_code_execution_tool_version] দিয়ে এটি override করতে পারেন:

```python title="anthropic_code_execution_tool_version.py"
from pydantic_ai import Agent, CodeExecutionTool
from pydantic_ai.capabilities import NativeTool
from pydantic_ai.models.anthropic import AnthropicModelSettings

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[NativeTool(CodeExecutionTool())],
    model_settings=AnthropicModelSettings(anthropic_code_execution_tool_version='20260120'),
)
```

মডেল সমর্থন করে না এমন একটি টুল সংস্করণ স্পষ্টভাবে বাছলে Pydantic AI একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

### Code execution container { #code-execution-containers }

বার্তার ইতিহাস থেকে একটি রান চালিয়ে গেলে, Pydantic AI সেই ইতিহাসে রেকর্ড করা Anthropic code execution container নিজে থেকে আবার ব্যবহার করে। Anthropic container 30 দিন পরে মেয়াদোত্তীর্ণ হয়, আর মেয়াদোত্তীর্ণ একটি container-এর রেফারেন্স দেওয়া একটি রিকোয়েস্ট একটি এরর ফেরত দেয়।

একটি রিকোয়েস্ট [`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool] দিয়ে ফাইল আপলোড করলে আর Anthropic ইতিহাস-থেকে-পাওয়া একটি container-এর জন্য HTTP 500 ফেরত দিলে, Pydantic AI প্রত্যাখ্যাত container ID ছাড়া একবার আবার চেষ্টা করে, যাতে Anthropic একটি নতুন container তৈরি করে আপলোডগুলো নিতে পারে। অন্য এরর এই আবার-চেষ্টা ছাড়াই তোলা হয়। নতুন container-এ মেয়াদোত্তীর্ণ container-এর অবস্থা বা ফাইল থাকে না।

container-এর ধারাবাহিকতা বাধ্যতামূলক হলে [`anthropic_container`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_container] স্পষ্টভাবে সেট করুন। একটি স্পষ্টভাবে কনফিগার করা container কখনো নিজে থেকে বদলানো হয় না; বদলে Anthropic-এর মূল এরর তোলা হয়।

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[anthropic]"`, `ANTHROPIC_API_KEY`, তারপর `Agent('anthropic:claude-sonnet-5-5')`।
* `max_tokens` না দিলে মডেলের সর্বোচ্চ পাঠানো হয়; Bedrock/Vertex/Foundry-তে নিজের client `AnthropicProvider`-এ।
* Caching: সহজ উপায় `cache=True`; সূক্ষ্ম নিয়ন্ত্রণে `anthropic_cache*` আর `CachePoint`; প্রতি রিকোয়েস্টে সর্বোচ্চ ৪টি cache point।
* দীর্ঘ কথোপকথনে `AnthropicCompaction`; task budget দিয়ে পুরো loop-এর token পরামর্শ।
* নতুন Claude মডেলে স্থির prefix রাখুন (thinking block binding আর cache দুটোর জন্যই)।

///
