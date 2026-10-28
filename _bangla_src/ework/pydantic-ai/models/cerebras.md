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

⟦CODE1⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE2⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE3⟧

একটি নিজের `httpx2.AsyncClient` দিয়েও `CerebrasProvider` নিজের মতো করতে পারেন:

⟦CODE4⟧

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[cerebras]"`, `CEREBRAS_API_KEY` সেট, তারপর `Agent('cerebras:<model>')`।
* key কোডে দিতে `CerebrasProvider(api_key=...)`; নিজের HTTP সেটিংয়ে `http_client=`।

///
