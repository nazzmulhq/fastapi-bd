# Crusoe { #crusoe }

/// note | এই পেজে যা শিখবেন

* Crusoe Serverless Inference-এর open-weight মডেল `CrusoeModel` দিয়ে ব্যবহার।
* মডেলের নামে ল্যাবের উপসর্গ কেন জরুরি, আর `NativeOutput` সব মডেলে কাজ করে।

///

## ইনস্টল { #install }

`CrusoeModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `crusoe` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[crusoe]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[crusoe]"
```

///


## কনফিগারেশন { #configuration }

[Crusoe](https://crusoe.ai/) Serverless Inference ব্যবহার করতে, [Crusoe Cloud console](https://console.crusoecloud.com/)-এ গিয়ে Models বাছুন, আর `Get API Key`-এ ক্লিক করুন।

উপলব্ধ মডেলের তালিকার জন্য দেখুন [Crusoe Serverless Inference ডকুমেন্টেশন](https://docs.crusoecloud.com/serverless-inference/overview)।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export CRUSOE_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `CrusoeModel` ব্যবহার করতে পারেন:

⟦CODE1⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE2⟧

## মডেলের নাম { #model-names }

Crusoe একটি endpoint-এর পেছনে অনেক ল্যাবের open-weight মডেল দেয়, আর মডেলের নাম ল্যাবকে উপসর্গ হিসেবে বহন করে — `zai/GLM-5.2`, `deepseek-ai/DeepSeek-V4-Pro`, `meta-llama/Llama-3.3-70B-Instruct`, `openai/gpt-oss-120b`। সেই উপসর্গই [model profile](compatible-apis.md#model-profile) বাছে, তাই শুধু মডেল id না দিয়ে উপসর্গটি নামে রাখুন।

## Structured output { #structured-output }

Crusoe প্রতিটি মডেল guided decoding দিয়ে দেয়, তাই [`NativeOutput`][pydantic_ai.output.NativeOutput] পুরো তালিকাজুড়ে কাজ করে — এমন মডেল পরিবারসহ যারা তাদের নিজের provider দিয়ে পৌঁছালে নিজস্ব structured output সমর্থন করে না।

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE3⟧

একটি নিজের `httpx2.AsyncClient` দিয়েও `CrusoeProvider` নিজের মতো করতে পারেন:

⟦CODE4⟧

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[crusoe]"`, `CRUSOE_API_KEY`, তারপর `Agent('crusoe:zai/GLM-5.2')`-এর মতো ল্যাব-উপসর্গসহ নাম।
* guided decoding-এর কারণে `NativeOutput` সব মডেলে কাজ করে।

///
