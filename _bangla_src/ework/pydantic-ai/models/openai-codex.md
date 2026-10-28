# OpenAI Codex { #openai-codex }

/// note | এই পেজে যা শিখবেন

* প্রতি-token API key-র বদলে আপনার ChatGPT/Codex subscription দিয়ে Pydantic AI চালানো।
* `codex login` বা `OpenAICodexOAuthFlow` দিয়ে লগইন, credential সংরক্ষণ আর নিরাপদ tracing।
* prompt caching আর সীমাবদ্ধতা।

///

প্রতি-token-এ বিল হওয়া একটি API key-র বদলে Pydantic AI-এর সাথে আপনার [ChatGPT/Codex subscription](https://chatgpt.com/codex) ব্যবহার করুন। `openai-codex` provider অফিসিয়াল [Codex CLI](https://developers.openai.com/codex/cli/)-র মতো একই OAuth প্রবাহ দিয়ে লগইন করে; API key-র জন্য, বদলে [`openai` provider](openai.md) ব্যবহার করুন, আর আপনার অ্যাপের ব্যবহারকারীদের তাদের নিজের ChatGPT প্ল্যান ব্যবহার করতে দিতে, [Sign in with ChatGPT](openai-chatgpt.md) ব্যবহার করুন। Codex backend-এর আপনার ব্যবহার OpenAI-এর সাথে আপনার চুক্তি দিয়ে নিয়ন্ত্রিত; আপনার subscription-এর জন্য প্রযোজ্য [usage policies](https://openai.com/policies/) দেখে নিন।

## ইনস্টল { #install }

Codex provider ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

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


## ব্যবহার { #usage }

[Codex CLI](https://developers.openai.com/codex/cli/) দিয়ে একবার `codex login` চালান, তারপর `openai-codex:` উপসর্গ ব্যবহার করুন:

⟦CODE1⟧

এটি [`OpenAICodexProvider`][pydantic_ai.providers.openai_codex.OpenAICodexProvider]-সমর্থিত [`OpenAICodexModel`][pydantic_ai.models.openai_codex.OpenAICodexModel]-এ নির্ধারিত হয়, যা `~/.codex/auth.json` (বা `$CODEX_HOME/auth.json`) থেকে CLI-র credential পড়ে। ফাইলটিতে কখনো লেখা হয় না; নবায়ন করা token প্রসেসের বাকি সময় মেমরিতে থাকে।

## Codex CLI ছাড়া লগইন { #logging-in-without-the-codex-cli }

Codex CLI-র ওপর নির্ভর করতে না চাইলে, [`OpenAICodexOAuthFlow`][pydantic_ai.providers.openai_codex.OpenAICodexOAuthFlow] একই browser লগইন চালায়। Codex client তার redirect URI `http://localhost:1455/auth/callback`-এ আটকে রাখে, তাই [`exchange_code_from_callback()`][pydantic_ai.providers.openai_codex.OpenAICodexOAuthFlow.exchange_code_from_callback] সেই port-এ শোনে যতক্ষণ না browser সেখানে redirect করে, তারপর code-টি credential-এর সাথে বিনিময় করে:

⟦CODE2⟧

`credentials` দিলে সেগুলো শুধু মেমরিতে থাকে, তাই পরের প্রসেসকে আবার লগইন করতে হয়। একবার লগইন করতে, নিচে বর্ণিত মতো সেগুলো টিকিয়ে রাখুন।

## Credential টিকিয়ে রাখা { #persisting-credentials }

provider মেয়াদোত্তীর্ণ token নিজে থেকে নবায়ন করে, আর refresh token একবার-ব্যবহারযোগ্য, তাই সংরক্ষিত কপিকে তাল মিলিয়ে চলতে হয়। provider-কে একটি [`OpenAICodexCredentialSource`][pydantic_ai.providers.openai_codex.OpenAICodexCredentialSource] দিন, আর এটি প্রথম ব্যবহারে `load()` আর প্রতিটি নবায়নের পরে `save()` ডাকে। store খালি থাকলেই শুধু লগইন flow চালান:

⟦CODE3⟧

/// tip | Credential ফাইল রক্ষা করুন

ফাইলটিতে একটি refresh token থাকে যা আপনার subscription-এ প্রবেশ দেয়, তাই অন্য যেকোনো গোপন তথ্যের মতো এটি সামলান: আপনার অ্যাপ যেখানে গোপন তথ্য রাখে সেখানে রাখুন (`~/.codex`-এ নয়, যা Codex CLI-র), আর বর্তমান ব্যবহারকারীতে সীমিত করুন, যেমন লেখার পরে `self.path.chmod(0o600)` দিয়ে।

///

`save()` এরর তুললে, নবায়ন করা credential মেমরিতে সক্রিয় থাকে আর একটি [`CredentialsPersistenceError`][pydantic_ai.providers.openai_codex.CredentialsPersistenceError] ওঠে। এটি আর [`CredentialsRefreshError`][pydantic_ai.providers.openai_codex.CredentialsRefreshError] দুটোই [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]-এর subclass, তাই একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] একটি অব্যবহারযোগ্য লগইনকে অন্য যেকোনো provider ব্যর্থতার মতো ধরে।

## Credential প্রকাশ না করে tracing { #tracing-without-exposing-credentials }

[Logfire instrumentation](../logfire.md) OAuth credential না ধরেই এজেন্ট রান trace করতে পারে। দরকার না হলে HTTP body ধরা বন্ধ রাখুন: `logfire.instrument_httpx(capture_all=True)` authorization code আর token উত্তর ধরে, যার জন্য বাড়তি মুছে-ফেলার ধরন লাগে।

পুরো HTTP ধরা চালু করলে, OAuth flow শুরুর আগে scrubbing কনফিগার করুন:

⟦CODE4⟧

বাড়তি ধরনগুলো OAuth credential আর account identifier মুছে দেয়; Logfire-এর ডিফল্ট ধরন ইতিমধ্যে authorization header মুছে দেয়।

## Prompt caching { #prompt-caching }

অফিসিয়াল Codex client-এর prompt-cache ঘনিষ্ঠতা অনুকরণ করতে, [`OpenAICodexModel`][pydantic_ai.models.openai_codex.OpenAICodexModel] `session-id`, `thread-id` আর `x-client-request-id` header আর `prompt_cache_key` রিকোয়েস্ট ফিল্ড পাঠায়। চারটিই বার্তার ইতিহাসের [`conversation_id`](../message-history.md) থেকে বের করা, তাই একই কথোপকথন চালিয়ে যাওয়া রান একটি স্থির পরিচয় আবার ব্যবহার করে। একটি স্পষ্ট `openai_prompt_cache_key` মডেল সেটিং বা স্পষ্টভাবে দেওয়া `extra_headers` সবসময় বের করা মানের ওপর জেতে। এটি একটি cache hit নিশ্চিত করে না।

Codex backend নিজে থেকে prompt cache করে আর OpenAI API-র স্পষ্ট prompt caching ফিল্ড প্রত্যাখ্যান করে, তাই একীভূত [`cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং, [`CachePoint`][pydantic_ai.messages.CachePoint] আর `openai_cache_instructions`-এর কোনো প্রভাব নেই।

## সীমাবদ্ধতা { #limitations }

- Codex backend শুধু-streaming; stream নয় এমন রানে লাইব্রেরি নিঃশব্দে একটি stream খালি করে, তাই `agent.run_sync()` আর এর সঙ্গীরা স্বাভাবিকভাবে কাজ করে।
- অসমর্থিত সাধারণ সেটিং (`max_tokens`, `temperature` আর `top_p`) পাঠানোর আগে বাদ পড়ে। Codex profile স্পষ্ট `openai_top_logprobs`, `openai_truncation` আর `openai_user` সেটিং সাধারণ OpenAI সামলানোর ওপর ছেড়ে দেয়, তাই backend-এর অসামঞ্জস্য এরর হিসেবে দেখা দেয়। log probability-র ওপর reasoning-সংক্রান্ত সাধারণ নিষেধাজ্ঞা তবুও প্রযোজ্য।
- backend `store=false` চায়, তাই প্রতিটি রিকোয়েস্ট এটি দিয়ে পাঠানো হয় আর একটি স্পষ্ট `openai_store=True` নিঃশব্দে override হয়: উত্তর কখনো সার্ভারে সংরক্ষিত হয় না। ফলে, একটি স্থগিত রান আবার শুরু করলে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে, কারণ চালিয়ে যাওয়ার মতো কোনো সংরক্ষিত উত্তর নেই।
- `count_tokens()` [`UserError`][pydantic_ai.exceptions.UserError] তোলে: subscription auth-এর অধীনে input-tokens endpoint পরিবেশিত নয়।
- কোনো device flow নেই: ওপরের browser লগইনই Codex client-এর সমর্থিত একমাত্র লগইন flow।

/// check | সংক্ষেপে মনে রাখুন

* `codex login` একবার, তারপর `Agent('openai-codex:<model>')` — CLI-র credential `~/.codex/auth.json` থেকে পড়া হয়।
* CLI ছাড়া: `OpenAICodexOAuthFlow` আর `OpenAICodexCredentialSource` দিয়ে সংরক্ষণ।
* `max_tokens`/`temperature` বাদ পড়ে; caching নিজে থেকে, স্পষ্ট cache সেটিং অকেজো।

///
