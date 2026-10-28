# Cohere { #cohere }

/// note | এই পেজে যা শিখবেন

* `CohereModel` ইনস্টল, API key আর মডেল ব্যবহার।
* নিজের provider/HTTP client, SDK-র নিজের retry আর মডেল সেটিং।

///

## ইনস্টল { #install }

`CohereModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `cohere` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[cohere]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[cohere]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Cohere](https://cohere.com/) ব্যবহার করতে, [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys)-এ যান আর API key তৈরির জায়গা খুঁজে না পাওয়া পর্যন্ত এগোতে থাকুন।

`CohereModelName`-এ সবচেয়ে জনপ্রিয় Cohere মডেলগুলোর একটি তালিকা আছে।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export CO_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `CohereModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('cohere:command-r7b-12-2024')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel

model = CohereModel('command-r7b-12-2024')
agent = Agent(model)
...
```

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.providers.cohere import CohereProvider

model = CohereModel('command-r7b-12-2024', provider=CohereProvider(api_key='your-api-key'))
agent = Agent(model)
...
```

একটি নিজের `http_client` দিয়েও `CohereProvider` নিজের মতো করতে পারেন:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel
from pydantic_ai.providers.cohere import CohereProvider

custom_http_client = AsyncClient(timeout=30)
model = CohereModel(
    'command-r7b-12-2024',
    provider=CohereProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

## SDK retry { #sdk-retries }

Cohere client ডিফল্টভাবে সার্ভার এরর, rate limit আর status 408 ও 409 দুবার আবার চেষ্টা করে, এখানে আপনি যে transport দেন তার ওপরে। এটি retry সংখ্যা প্রতি client-এ নয়, প্রতি রিকোয়েস্টে নেয়, তাই এটি বদলাতে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) সেট করুন, যেমন retry নীতি শুধু আপনার transport-এ রাখতে `0`। এই স্তর কোথায় বসে তা দেখুন [Provider SDK retries](../retries.md#provider-sdk-retries)-এ।

## মডেল সেটিং { #model-settings }

[`CohereModelSettings`][pydantic_ai.models.cohere.CohereModelSettings] দিয়ে মডেলের আচরণ নিজের মতো করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cohere import CohereModel, CohereModelSettings

model = CohereModel('command-r7b-12-2024')
settings = CohereModelSettings(
    temperature=0.2,
    top_k=40,
)
agent = Agent(model, model_settings=settings)
...
```

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[cohere]"`, `CO_API_KEY` সেট, তারপর `Agent('cohere:<model>')`।
* SDK নিজে দুবার retry করে; নিয়ন্ত্রণে `ModelSettings(max_retries=...)`।

///
