# Cerebras { #cerebras }

/// note | এই পেজে যা শিখবেন

* Cerebras-এর দ্রুত inference ব্যবহার করতে `CerebrasModel` ইনস্টল আর কনফিগার করা।
* API key environment variable, নাম দিয়ে বা সরাসরি মডেল তৈরি, আর নিজের provider/HTTP client।

///

## ইনস্টল { #install }

`CerebrasModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `cerebras` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[cerebras]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[cerebras]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Cerebras](https://cerebras.ai/) ব্যবহার করতে, [cloud.cerebras.ai](https://cloud.cerebras.ai/?utm_source=3pi_pydantic-ai&utm_campaign=partner_doc)-এ গিয়ে একটি API key তৈরি করুন।

উপলব্ধ মডেলের তালিকার জন্য দেখুন [Cerebras models ডকুমেন্টেশন](https://inference-docs.cerebras.ai/models)।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export CEREBRAS_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `CerebrasModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('cerebras:gpt-oss-120b')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cerebras import CerebrasModel

model = CerebrasModel('gpt-oss-120b')
agent = Agent(model)
...
```

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.cerebras import CerebrasModel
from pydantic_ai.providers.cerebras import CerebrasProvider

model = CerebrasModel(
    'gpt-oss-120b', provider=CerebrasProvider(api_key='your-api-key')
)
agent = Agent(model)
...
```

একটি নিজের `httpx2.AsyncClient` দিয়েও `CerebrasProvider` নিজের মতো করতে পারেন:

```python
from httpx2 import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.cerebras import CerebrasModel
from pydantic_ai.providers.cerebras import CerebrasProvider

custom_http_client = AsyncClient(timeout=30)
model = CerebrasModel(
    'gpt-oss-120b',
    provider=CerebrasProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[cerebras]"`, `CEREBRAS_API_KEY` সেট, তারপর `Agent('cerebras:<model>')`।
* key কোডে দিতে `CerebrasProvider(api_key=...)`; নিজের HTTP সেটিংয়ে `http_client=`।

///
