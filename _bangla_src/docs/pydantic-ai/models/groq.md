# Groq { #groq }

/// note | এই পেজে যা শিখবেন

* Groq-এর দ্রুত inference `GroqModel` দিয়ে ব্যবহার: ইনস্টল, API key, provider।
* Groq SDK-র নিজের retry কীভাবে নিয়ন্ত্রণ করবেন।

///

## ইনস্টল { #install }

`GroqModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `groq` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[groq]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[groq]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Groq](https://groq.com/) ব্যবহার করতে, [console.groq.com/keys](https://console.groq.com/keys)-এ যান আর API key তৈরির জায়গা খুঁজে না পাওয়া পর্যন্ত এগোতে থাকুন।

`GroqModelName`-এ উপলব্ধ Groq মডেলের একটি তালিকা আছে।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export GROQ_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `GroqModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('groq:llama-3.3-70b-versatile')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

model = GroqModel('llama-3.3-70b-versatile')
agent = Agent(model)
...
```

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

model = GroqModel(
    'llama-3.3-70b-versatile', provider=GroqProvider(api_key='your-api-key')
)
agent = Agent(model)
...
```

একটি নিজের `httpx.AsyncClient` দিয়েও `GroqProvider` নিজের মতো করতে পারেন:

```python
from httpx import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

custom_http_client = AsyncClient(timeout=30)
model = GroqModel(
    'llama-3.3-70b-versatile',
    provider=GroqProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

## SDK retry { #sdk-retries }

provider যে `AsyncGroq` client বানায় সেটিও নিজে ব্যর্থ রিকোয়েস্ট আবার চেষ্টা করে — ডিফল্টভাবে `max_retries=2`, যে OpenAI client-এর আদলে এটি তৈরি তার মতো। retry নীতি শুধু আপনার transport-এ রাখতে `groq_client=AsyncGroq(max_retries=0)` দিন, বা client না বানিয়ে সংখ্যা বদলাতে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) সেট করুন। এই স্তর কোথায় বসে তা দেখুন [Provider SDK retries](../retries.md#provider-sdk-retries)-এ।

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[groq]"`, `GROQ_API_KEY`, তারপর `Agent('groq:<model>')`।
* Groq provider এখনো পুরনো `httpx.AsyncClient` নেয়; SDK নিজে দুবার retry করে।

///
