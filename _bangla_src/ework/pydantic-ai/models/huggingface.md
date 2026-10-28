# Hugging Face { #hugging-face }

/// note | এই পেজে যা শিখবেন

* Hugging Face Inference Providers দিয়ে DeepSeek R1-এর মতো open-source মডেল চালানো।
* account আর `HF_TOKEN` সেটআপ, provider আর নিজের `AsyncInferenceClient`।

///

[Hugging Face](https://huggingface.co/) হলো সব প্রধান open source মডেল, dataset, MCP আর demo-সহ একটি AI প্ল্যাটফর্ম। বাড়ানো-কমানো যায় এমন serverless অবকাঠামোয় DeepSeek R1-এর মতো open source মডেল চালাতে [Inference Providers](https://huggingface.co/docs/inference-providers) ব্যবহার করতে পারেন।

/// tip | Sentence Transformers দিয়ে লোকাল embedding

এই পেজ Hugging Face Inference Providers দিয়ে chat completion নিয়ে। Hugging Face-এর **embedding** মডেল লোকালভাবে চালাতে (কোনো API key নেই, কোনো নেটওয়ার্ক কল নেই), দেখুন [Sentence Transformers embedding model](../embeddings.md#sentence-transformers-local), যা [sentence-transformers লাইব্রেরি](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)-র যেকোনো মডেলের সাথে কাজ করে।

///

## ইনস্টল { #install }

`HuggingFaceModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `huggingface` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[huggingface]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[huggingface]"
```

///


## কনফিগারেশন { #configuration }

[Hugging Face](https://huggingface.co/) inference ব্যবহার করতে, একটি account সেট আপ করতে হবে, যা আপনাকে [Inference Providers](https://huggingface.co/docs/inference-providers)-এ [free tier](https://huggingface.co/docs/inference-providers/pricing) বরাদ্দ দেবে। inference সেট আপ করতে, এই ধাপগুলো অনুসরণ করুন:

1. [Hugging Face](https://huggingface.co/join)-এ গিয়ে একটি account-এর জন্য সাইন আপ করুন।
2. [Hugging Face](https://huggingface.co/settings/tokens)-এ একটি নতুন access token তৈরি করুন।
3. `HF_TOKEN` environment variable এইমাত্র তৈরি করা token-এ সেট করুন।

একটি Hugging Face access token পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export HF_TOKEN='hf_token'
```

## ব্যবহার { #usage }

তারপর নাম দিয়ে [`HuggingFaceModel`][pydantic_ai.models.huggingface.HuggingFaceModel] ব্যবহার করতে পারেন:

⟦CODE1⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE2⟧

ডিফল্টভাবে, [`HuggingFaceModel`][pydantic_ai.models.huggingface.HuggingFaceModel]
[`HuggingFaceProvider`][pydantic_ai.providers.huggingface.HuggingFaceProvider] ব্যবহার করে, যা মডেলের জন্য উপলব্ধ inference provider-দের (Cerebras, Together AI, Cohere ইত্যাদি) মধ্যে প্রথমটি নিজে থেকে বাছে, https://hf.co/settings/inference-providers-এ আপনার পছন্দের ক্রম অনুযায়ী সাজানো।

## Provider কনফিগার করা { #configure-the-provider }

provider-কে কোডে প্যারামিটার দিতে চাইলে, প্রোগ্রাম দিয়ে
[`HuggingFaceProvider`][pydantic_ai.providers.huggingface.HuggingFaceProvider] তৈরি করে মডেলে দিতে পারেন:

⟦CODE3⟧

## নিজের Hugging Face client { #custom-hugging-face-client }

[`HuggingFaceProvider`][pydantic_ai.providers.huggingface.HuggingFaceProvider] `hf_client` প্যারামিটার দিয়ে একটি নিজের
[`AsyncInferenceClient`](https://huggingface.co/docs/huggingface_hub/v0.29.3/en/package_reference/inference_client#huggingface_hub.AsyncInferenceClient) client-ও নেয়, তাই [Hugging Face Hub python লাইব্রেরির ডক](https://huggingface.co/docs/huggingface_hub/package_reference/inference_client)-এ সংজ্ঞায়িত `headers`, `bill_to` (আপনি সদস্য এমন একটি HF প্রতিষ্ঠানে বিল করা), `base_url` ইত্যাদি নিজের মতো করতে পারেন।

⟦CODE4⟧

## Stream বাতিল { #streaming-cancellation }

/// note | Transport বাতিল

[`cancel()`][pydantic_ai.result.StreamedRunResult.cancel] নিরাপদে একটি সক্রিয় লোকাল stream-টানা বাধা দেয়, আরেকটি task-এ চলা একটিসহ। `huggingface_hub.AsyncInferenceClient` HTTP উত্তর একটি client-মালিকানাধীন exit stack-এ রাখে আর কোনো নথিভুক্ত প্রতি-stream transport handle দেয় না, তাই ফেরত আসা iterator বন্ধ করলে সাথে সাথে HTTP বন্ধের, বা দূরের তৈরি আর বিলিং কখন থামে তার নিশ্চয়তা নেই। দেখুন [huggingface/huggingface_hub#4224](https://github.com/huggingface/huggingface_hub/issues/4224)।

///

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[huggingface]"`, `HF_TOKEN` সেট, তারপর `Agent('huggingface:<org>/<model>')`।
* inference provider নিজে বাছাই হয় আপনার HF সেটিংয়ের ক্রমে; নিজের সেটিংয়ে `hf_client=AsyncInferenceClient(...)`।

///
