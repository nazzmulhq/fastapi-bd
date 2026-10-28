# Mistral { #mistral }

/// note | এই পেজে যা শিখবেন

* `MistralModel` ইনস্টল, API key, provider আর নিজের HTTP client।
* Mistral-এর ৯-অক্ষরের টুল কল ID-র নিয়ম, আর Pydantic AI কীভাবে তা সামলায়।

///

## ইনস্টল { #install }

`MistralModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `mistral` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[mistral]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[mistral]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Mistral](https://mistral.ai) ব্যবহার করতে, [console.mistral.ai/api-keys/](https://console.mistral.ai/api-keys/)-এ যান আর API key তৈরির জায়গা খুঁজে না পাওয়া পর্যন্ত এগোতে থাকুন।

`LatestMistralModelNames`-এ সবচেয়ে জনপ্রিয় Mistral মডেলগুলোর একটি তালিকা আছে।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export MISTRAL_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `MistralModel` ব্যবহার করতে পারেন:

⟦CODE1⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE2⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE3⟧

একটি নিজের `httpx2.AsyncClient` দিয়েও provider নিজের মতো করতে পারেন:

⟦CODE4⟧

Pydantic AI v2-এর সময় Mistral provider একটি পুরনো `httpx.AsyncClient`-ও নেয়, তবে একটি deprecation সতর্কবার্তা দেয়। নতুন কোডে `httpx2.AsyncClient` ব্যবহার করুন; পুরনো HTTPX client-এর সমর্থন Pydantic AI v3-এ সরিয়ে ফেলা হবে।

## টুল কল ID { #tool-call-ids }

Mistral-এর টুল-কলিং chat template ঠিক 9টি ASCII অক্ষর আর অঙ্কের টুল কল ID ব্যবহার করে, আর যে মডেল এগুলো যাচাই করে সেগুলো অন্য যেকোনো ID একটি 400 এরর দিয়ে প্রত্যাখ্যান করে। এর মধ্যে আছে আরেকটি provider-এর ID, যেমন OpenAI-এর `call_...` বা Anthropic-এর `toolu_...`, আর Pydantic AI-এর তৈরি `pyd_ai_...` ID। আরেকটি মডেলে শুরু হওয়া একটি [বার্তার ইতিহাস](../message-history.md), বা Mistral-এ বদলে যাওয়া একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এ এমন ID থাকতে পারে।

এই ইতিহাসগুলো কাজ করাতে, প্রতিটি Mistral মডেল profile [`tool_call_id_length`][pydantic_ai.profiles.ModelProfile.tool_call_id_length] `9` সেট করে। প্রতিটি রিকোয়েস্টের আগে, না আঁটা একটি ID এর একটি স্থির hash দিয়ে বদলানো হয় যা আঁটে, আর যে ID আগেই আঁটে তা অপরিবর্তিত পাঠানো হয়। Mistral মডেল দেওয়া অন্য provider, যেমন Azure AI Foundry, OpenRouter বা vLLM, একই profile ব্যবহার করে। সংরক্ষিত বার্তার ইতিহাস মূল ID রাখে।

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[mistral]"`, `MISTRAL_API_KEY`, তারপর `Agent('mistral:<model>')`।
* অন্য provider-এর ইতিহাস Mistral-এ চালালেও সমস্যা নেই: টুল কল ID নিজে থেকে ৯ অক্ষরে রূপান্তরিত হয়।

///
