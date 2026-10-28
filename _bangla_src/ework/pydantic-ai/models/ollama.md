# Ollama { #ollama }

/// note | এই পেজে যা শিখবেন

* নিজের কম্পিউটারে বা দূরের সার্ভারে চলা Ollama, আর Ollama Cloud দিয়ে `OllamaModel` ব্যবহার।
* `OLLAMA_BASE_URL` সেট করা, আর structured output (`NativeOutput`) কোথায় কাজ করে।

///

/// tip | উদাহরণ দিয়ে বুঝি

Ollama দিয়ে মডেলটি আপনার নিজের কম্পিউটারে চলে — ইন্টারনেট বা API-র বিল লাগে না, আর আপনার ডেটা বাইরে যায় না। শেখা, পরীক্ষা আর গোপনীয় ডেটার কাজে এটি চমৎকার; তবে বড় মডেল চালাতে ভালো GPU/RAM লাগে।

///

## ইনস্টল { #install }

[`OllamaModel`][pydantic_ai.models.ollama.OllamaModel] ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

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

Pydantic AI নিজে হোস্ট করা [Ollama](https://ollama.com/) সার্ভার (লোকালে বা দূরে চলা) আর [Ollama Cloud](https://ollama.com/cloud) দুটোই সমর্থন করে।

লোকালে চলা সার্ভারের জন্য, `http://localhost:11434/v1` base URL ব্যবহার করুন। Ollama Cloud-এর জন্য, `https://ollama.com/v1` ব্যবহার করুন আর একটি API key সেট থাকা নিশ্চিত করুন।

পেছনের সামঞ্জস্যের জন্য, [`OllamaModel`][pydantic_ai.models.ollama.OllamaModel] Ollama-র OpenAI-সামঞ্জস্যপূর্ণ Chat Completions API (`/v1/chat/completions`) ব্যবহার করে।

/// tip | Decision model

Ollama v0.35.0 আর পরের সংস্করণ Nimble আর Tev1-এর মতো [decision model](decision.md)-ও লোকালে চালায়, যা লেখা না লিখে
সম্ভাবনাসহ টাইপ করা প্রশ্নের উত্তর দেয়। এগুলো `OllamaModel` নয়,
[`SystemOneModel`](system-one.md#ollama) দিয়ে ব্যবহার করুন।

///

## Environment variable { #environment-variable }

`OLLAMA_BASE_URL` আর (ঐচ্ছিকভাবে) `OLLAMA_API_KEY` environment variable সেট করুন:

⟦CODE1⟧

তারপর নাম দিয়ে `OllamaModel` ব্যবহার করতে পারেন:

⟦CODE2⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE3⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE4⟧

Ollama Cloud-এর জন্য, `base_url='https://ollama.com/v1'` ব্যবহার করুন আর `OLLAMA_API_KEY` environment variable সেট করুন (বা সরাসরি `api_key=` দিন)।

## Structured output { #structured-output }

নিজে হোস্ট করা Ollama (v0.5.0+, ডিসেম্বর 2024-এ প্রকাশিত) `llama.cpp`-এর grammar-সীমিত decoder দিয়ে `json_schema`-সহ `response_format` প্রয়োগ করে, তাই [`NativeOutput`][pydantic_ai.output.NativeOutput] তৈরির সময়েই schema-বৈধ আউটপুট দেয়:

⟦CODE5⟧

/// note | Ollama Cloud এখনো `json_schema` প্রয়োগ করে না

Ollama Cloud-এর inference backend এরর ছাড়াই `json_schema`-সহ `response_format` নেয় কিন্তু grammar-সীমিত decoding প্রয়োগ করে না, তাই schema নিঃশব্দে প্রয়োগ হয় না। upstream ট্র্যাকিং issue-র জন্য দেখুন [ollama/ollama#12362](https://github.com/ollama/ollama/issues/12362)।

[`OllamaModel`][pydantic_ai.models.ollama.OllamaModel] একটি Cloud পথ চিনলে — হয় `ollama.com`-এ একটি `base_url` বা `-cloud`-এ শেষ হওয়া একটি মডেলের নাম — এটি নিজে থেকে profile-এ `supports_json_schema_output` বন্ধ করে।

একটি Ollama Cloud মডেলের সাথে [`NativeOutput`][pydantic_ai.output.NativeOutput] ব্যবহার করলে, একটি নিঃশব্দ retry loop-এর বদলে একটি স্পষ্ট [`UserError`][pydantic_ai.exceptions.UserError] পাবেন। বদলে ডিফল্ট [`ToolOutput`][pydantic_ai.output.ToolOutput] বা [`PromptedOutput`][pydantic_ai.output.PromptedOutput] ব্যবহার করুন — দুটোই Cloud-এ কাজ করে।

///

/// check | সংক্ষেপে মনে রাখুন

* লোকাল: `OLLAMA_BASE_URL=http://localhost:11434/v1`, তারপর `Agent('ollama:<model>')`।
* Cloud: `https://ollama.com/v1` আর `OLLAMA_API_KEY`।
* `NativeOutput` লোকাল Ollama-তে কাজ করে, Cloud-এ নয় (সেখানে `ToolOutput`/`PromptedOutput`)।

///
