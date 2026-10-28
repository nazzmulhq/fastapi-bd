# OpenAI ChatGPT প্ল্যানের ব্যবহার { #openai-chatgpt-plan-usage }

/// note | এই পেজে যা শিখবেন

* "Sign in with ChatGPT": আপনার অ্যাপের ব্যবহারকারীরা API key-র বদলে নিজের ChatGPT প্ল্যান দিয়ে রিকোয়েস্ট চালান।
* browser দিয়ে sign-in, credential সংরক্ষণ আর নবায়ন, আবার sign-in।
* এরর আর preview-এর সীমাবদ্ধতা।

///

[Sign in with ChatGPT](https://developers.openai.com/siwc/token-sharing-open-source) আপনার open-source বা লোকালে চলা অ্যাপের ব্যবহারকারীদের একটি API key-র বদলে তাদের ChatGPT প্ল্যান দিয়ে অ্যাপের রিকোয়েস্ট চালাতে দেয়। `openai-chatgpt` provider sign-in চালায়, sign-in করা ব্যবহারকারীর token দিয়ে Responses API রিকোয়েস্ট পাঠায়, আর মেয়াদ শেষ হতে থাকলে তা নবায়ন করে। একটি paid বা দূরে হোস্ট করা অ্যাপে প্ল্যানের ব্যবহার দিতে আগে OpenAI-এর অনুমোদন লাগে, তাদের [interest form](https://openai.com/form/sign-in-with-chatgpt-interest/) দিয়ে। আপনার ব্যবহার OpenAI-এর [শর্ত আর নীতি](https://openai.com/policies/) দিয়ে নিয়ন্ত্রিত।

এটি [`openai-codex` provider](openai-codex.md) থেকে আলাদা, যা Codex backend-এ আপনার নিজের subscription ব্যবহার করতে Codex CLI হিসেবে sign in করে। Sign in with ChatGPT-এ, প্রতিটি ব্যবহারকারী আপনার অ্যাপকে নাম ধরে অনুমোদন করেন, রিকোয়েস্ট সর্বজনীন OpenAI API-তে যায়, আর ব্যবহারকারীরা [ChatGPT settings](https://chatgpt.com/settings/usage)-এ আপনার অ্যাপের ব্যবহার দেখতে আর সীমিত করতে পারেন।

/// tip | কোনটি কার জন্য?

* **`openai`**: আপনার নিজের API key, প্রতি token-এ বিল।
* **`openai-codex`**: আপনার নিজের ChatGPT/Codex subscription, নিজের ব্যবহারের জন্য।
* **`openai-chatgpt`** (এই পেজ): আপনার অ্যাপের *প্রতিটি ব্যবহারকারী* তাদের নিজের ChatGPT প্ল্যান দিয়ে।

///

## ইনস্টল { #install }

ChatGPT provider ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

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


## Sign in করা { #signing-in }

[`OpenAIChatGPTOAuthFlow`][pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTOAuthFlow] browser sign-in চালায়। OpenAI `http://127.0.0.1:PORT/auth/callback`-এ একটি callback চায়, তাই [`exchange_code_from_callback()`][pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTOAuthFlow.exchange_code_from_callback] সেই port-এ শোনে (আপনি আরেকটি `redirect_uri` না দিলে 1455) যতক্ষণ না browser সেখানে redirect করে, তারপর code-টি credential-এর সাথে বিনিময় করে:

⟦CODE1⟧

provider-এর আপনার অ্যাপের credential লাগে, তাই এজেন্টকে একটি `'openai-chatgpt:...'` মডেল-নামের স্ট্রিং না দিয়ে, দেখানো মতো এটি দিয়ে মডেল তৈরি করুন।

`app_name` হলো আপনার অ্যাপ অনুমোদনের সময় ব্যবহারকারী যে নাম দেখেন। প্রতিটি ইনস্টলেশনে একই নাম ব্যবহার করুন। `host_id` আপনার অ্যাপের একটি ইনস্টলেশনের একটি অস্বচ্ছ পরিচয়-চিহ্ন, যেমন একটি laptop বা একটি VM; একবার তৈরি করে সেই ইনস্টলেশনের প্রতিটি sign-in-এ আবার ব্যবহার করুন। OpenAI অ্যাপদের এটি পাঠাতে বলে, তবে এখানে এটি ঐচ্ছিক, কারণ এটি পাঠানো sign-in-এর timeout হওয়ার খবর পাওয়া গেছে; আপনারগুলোতে হলে বাদ দিন।

একটি ChatGPT account-এ প্রথম sign-in আপনার অ্যাপকে এর সাথে নথিভুক্ত করে, আর OpenAI সেই নথিভুক্তির জন্য credential-এর `client_id` দেয়। ব্যবহারকারী আপনার অ্যাপকে তাদের প্ল্যান ব্যবহার করতে দিতে অস্বীকার করতে পারেন: sign-in তখনো credential ফেরত দেয়, যাতে আপনি নথিভুক্তি সংরক্ষণ করতে পারেন, কিন্তু [`plan_usage_granted`][pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTCredentials.plan_usage_granted] হয় `False` আর provider সেগুলো প্রত্যাখ্যান করে।

## Credential টিকিয়ে রাখা { #persisting-credentials }

`credentials` দিলে সেগুলো শুধু মেমরিতে থাকে, তাই পরের প্রসেসকে আবার sign in করতে হয়। provider মেয়াদোত্তীর্ণ token নিজে থেকে নবায়ন করে, আর refresh token একবার-ব্যবহারযোগ্য, তাই সংরক্ষিত কপিকে তাল মিলিয়ে চলতে হয়। provider-কে একটি [`OpenAIChatGPTCredentialSource`][pydantic_ai.providers.openai_chatgpt.OpenAIChatGPTCredentialSource] দিন, আর এটি প্রথম ব্যবহারে `load()` আর প্রতিটি নবায়নের পরে `save()` ডাকে:

⟦CODE2⟧

/// tip | Credential ফাইল রক্ষা করুন

ফাইলটিতে একটি refresh token থাকে যা ব্যবহারকারীর ChatGPT প্ল্যানে প্রবেশ দেয়, তাই অন্য যেকোনো গোপন তথ্যের মতো এটি সামলান: source control আর লগের বাইরে রাখুন, আর বর্তমান ব্যবহারকারীতে সীমিত করুন, যেমন লেখার পরে `self.path.chmod(0o600)` দিয়ে।

///

`save()` এরর তুললে, নবায়ন করা credential মেমরিতে সক্রিয় থাকে আর একটি [`CredentialsPersistenceError`][pydantic_ai.providers.openai_chatgpt.CredentialsPersistenceError] ওঠে। একটি প্রত্যাখ্যাত নবায়ন [`CredentialsRefreshError`][pydantic_ai.providers.openai_chatgpt.CredentialsRefreshError] তোলে; এর বার্তা যদি বলে grant প্রত্যাখ্যাত হয়েছে, ব্যবহারকারীকে আবার sign in করতে হবে। দুটোই [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]-এর subclass, তাই একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] একটি অব্যবহারযোগ্য sign-in-কে অন্য যেকোনো provider ব্যর্থতার মতো ধরে।

## আবার sign in করা { #signing-in-again }

একই ChatGPT account আবার sign in করাতে, যেমন এর refresh token মেয়াদোত্তীর্ণ হওয়ার পরে, সংরক্ষিত `client_id` দিন যাতে sign-in আরেকটি তৈরি না করে নথিভুক্তিটি আবার ব্যবহার করে, আর সংরক্ষিত `id_token` দিন যাতে ব্যবহারকারীকে account বাছতে না হয়:

⟦CODE3⟧

`id_token_hint`-সহ, ব্যবহারকারী একটি ভিন্ন ChatGPT account দিয়ে শেষ করলে sign-in ব্যর্থ হয়। authorization URL তখন ID token বহন করে, তাই এটি লগের বাইরে রাখুন।

একটি provider প্রতিটি রিকোয়েস্টের আগে প্ল্যানের ব্যবহার পরীক্ষা করে আর এটি ছাড়া credential প্রত্যাখ্যান করতে থাকে, তাই একটি নতুন sign-in-এর পরে, নতুন credential একটি নতুন provider-কে দিন।

## এরর { #errors }

token endpoint যে sign-in প্রত্যাখ্যান করে, বা যার ID token যাচাইয়ে ব্যর্থ হয়, তা [`CredentialsRefreshError`][pydantic_ai.providers.openai_chatgpt.CredentialsRefreshError] তোলে। `client_id=flow.client_id` দিয়ে একটি নতুন flow-এ আবার sign-in শুরু করুন: ব্যর্থ flow তার জন্য দেওয়া client id রাখে, তাই আবার চেষ্টা আরেকটি তৈরি না করে সেই নথিভুক্তি আবার ব্যবহার করে। `id_token_hint` যে account-এর নাম বলে তার চেয়ে ভিন্ন একটি account-এর জন্য শেষ হওয়া sign-in [`UserError`][pydantic_ai.exceptions.UserError] তোলে, আর এর credential বাদ পড়ে।

ব্যবহারকারীর প্ল্যান একটি রিকোয়েস্ট সামলাতে না পারলে, রিকোয়েস্টটি একটি [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] দিয়ে ব্যর্থ হয় যার body `subscription_sharing_usage_limit_exceeded`-এর মতো একটি এরর code বহন করে। OpenAI কখনো রিকোয়েস্টটি আরেকটি বিলিং পদ্ধতিতে সরায় না। [Errors and recovery](https://developers.openai.com/siwc/token-sharing-open-source/errors-and-recovery) code-গুলো আর ব্যবহারকারীকে কী বলবেন তার তালিকা দেয়; ব্যবহারের সীমার জন্য, তাদের [ChatGPT settings](https://chatgpt.com/settings/usage)-এ পাঠান।

## সীমাবদ্ধতা { #limitations }

ChatGPT প্ল্যানের ব্যবহার একটি preview, OpenAI-এর নথিভুক্ত [সীমাবদ্ধতা](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations)-সহ:

- রিকোয়েস্ট stream হয়; stream নয় এমন রানে লাইব্রেরি নিঃশব্দে একটি stream খালি করে, তাই `agent.run_sync()` আর এর সঙ্গীরা স্বাভাবিকভাবে কাজ করে।
- প্রতিটি রিকোয়েস্ট `store=false` দিয়ে পাঠানো হয়, আর একটি স্পষ্ট `openai_store=True` নিঃশব্দে override হয়: উত্তর কখনো সার্ভারে সংরক্ষিত হয় না। ফলে, একটি স্থগিত রান আবার শুরু করলে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।
- System prompt আর নির্দেশনা developer বার্তা হিসেবে পাঠানো হয়, কারণ system বার্তা প্রত্যাখ্যাত হয়।
- অসমর্থিত সাধারণ সেটিং (`max_tokens`, `service_tier`, `temperature` আর `top_p`) পাঠানোর আগে বাদ পড়ে। স্পষ্ট `openai_*` সেটিং অপরিবর্তিত পাঠানো হয়, তাই পথটি যেগুলো প্রত্যাখ্যান করে, যেমন `openai_truncation` আর `openai_user`, সেগুলো এরর হিসেবে দেখা দেয়।
- [নেটিভ টুলের](../native-tools.md) মধ্যে শুধু [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] সমর্থিত। [Tool search](../tools-advanced.md#tool-search) OpenAI-এর নিজস্ব tool search-এর বদলে লোকালে চলে।
- prompt caching সেটিংয়ের কোনো প্রভাব নেই, আর `count_tokens()` [`UserError`][pydantic_ai.exceptions.UserError] তোলে।
- callback browser চালানো কম্পিউটারে পৌঁছায়, তাই একটি দূরের VM-এর একটি অ্যাপের জন্য, লোকালে sign in করে credential সেখানে কপি করুন, যেমন বর্ণিত আছে [Self-hosted VMs](https://developers.openai.com/siwc/token-sharing-open-source/self-hosted-vms)-এ।

/// check | সংক্ষেপে মনে রাখুন

* `OpenAIChatGPTOAuthFlow` দিয়ে browser sign-in, তারপর credential দিয়ে provider আর মডেল তৈরি।
* refresh token একবার-ব্যবহারযোগ্য: `OpenAIChatGPTCredentialSource` দিয়ে প্রতিটি নবায়ন সংরক্ষণ করুন।
* paid বা দূরে হোস্ট করা অ্যাপে আগে OpenAI-এর অনুমোদন লাগে।

///
