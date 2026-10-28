# AWS Bedrock { #aws-bedrock }

/// note | এই পেজে যা শিখবেন

* Bedrock-এ দুই পথ: Converse (`bedrock:`, প্রায় সব মডেল) আর Mantle (`bedrock-mantle:`, OpenAI মডেল)।
* AWS credential, data retention, output token-এর সীমা, thinking আর structured output।
* Service tier, prompt caching, application inference profile আর boto3 দিয়ে retry।

///

[Amazon Bedrock](https://aws.amazon.com/bedrock/) অনেক provider-এর foundation মডেল দেয়, আর Pydantic AI দুটি আলাদা AWS API দিয়ে এতে পৌঁছায়। মডেলের উপসর্গ দিয়ে পথ বাছুন:

- **[Bedrock Converse](#bedrock-converse)** (`bedrock:`) — সবচেয়ে বড় তালিকা, Anthropic, Amazon, Cohere, Meta, Mistral, DeepSeek, Qwen, বাছাই করা OpenAI মডেল আর [আরও অনেক][pydantic_ai.models.bedrock.BedrockModelName]-সহ, Bedrock Runtime Converse API দিয়ে। প্রায় প্রতিটি Bedrock মডেলের জন্য এটিই পথ।
- **[Bedrock Mantle](#bedrock-mantle)** (`bedrock-mantle:`) — [Mantle](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html)-এর OpenAI-সামঞ্জস্যপূর্ণ API দিয়ে OpenAI GPT-5.x, GPT-6 আর GPT-OSS মডেল।

দুই পথই একই AWS credential দিয়ে প্রমাণীকরণ করে। `bedrock:` উপসর্গ সবসময় Converse ব্যবহার করে; এটি দেয় না এমন একটি OpenAI মডেল চাইলে আপনাকে `bedrock-mantle:`-এর দিকে নির্দেশ করে একটি এরর ওঠে।

AWS [নতুন অ্যাপ্লিকেশনের জন্য `bedrock-runtime` endpoint-এর পরামর্শ দেয়](https://docs.aws.amazon.com/bedrock/latest/userguide/endpoints.html)। Pydantic AI-এর `bedrock:` পথ সেই endpoint-এ Converse ব্যবহার করে। এর OpenAI-সামঞ্জস্যপূর্ণ API বা শুধু Mantle-এ পাওয়া একটি মডেল দরকার হলে `bedrock-mantle:` বাছুন।

| পথ | উপসর্গ | মডেল | ঐচ্ছিক group | মডেল ক্লাস |
| --- | --- | --- | --- | --- |
| [Converse](#bedrock-converse) | `bedrock:` | Anthropic, Amazon, Cohere, Meta, Mistral, বাছাই করা OpenAI মডেল, আর [আরও][pydantic_ai.models.bedrock.BedrockModelName] | `bedrock` | [`BedrockConverseModel`][pydantic_ai.models.bedrock.BedrockConverseModel] |
| [Mantle](#bedrock-mantle) | `bedrock-mantle:` | OpenAI GPT-5.x, GPT-6 আর GPT-OSS | `bedrock-mantle` | [`BedrockMantleResponsesModel`][pydantic_ai.models.bedrock_mantle.BedrockMantleResponsesModel], [`BedrockMantleChatModel`][pydantic_ai.models.bedrock_mantle.BedrockMantleChatModel] |

## OpenAI মডেলের পথ { #bedrock-openai-model-routes }

GPT-OSS, GPT-5.6 Sol/Luna/Terra, GPT-6 Sol/Luna/Astra আর GPT-6.1 Sol দুই পথেই পাওয়া যায়। GPT-5.4, GPT-5.5 আর GPT-5.6 Cyber শুধু Mantle দিয়ে পাওয়া যায়।

Converse-এ, GPT-5.6-এর জন্য একটি cross-region inference-profile মডেল ID লাগে। Sol `us.openai.gpt-5.6-sol` আর `global.openai.gpt-5.6-sol` সমর্থন করে। Luna আর Terra `us.`, `in.` আর `global.` ID সমর্থন করে। GPT-6 Sol, Luna, Astra আর GPT-6.1 Sol `us.` আর `global.` ID সমর্থন করে, যেমন `global.openai.gpt-6-sol`। বর্তমান endpoint আর region-ভিত্তিক প্রাপ্যতার জন্য AWS মডেল কার্ড দেখুন: [GPT-5.6 Sol](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-sol.html), [GPT-5.6 Luna](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-luna.html), [GPT-5.6 Terra](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-terra.html), [GPT-6 Astra](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-6-astra.html), আর [GPT-6.1 Sol](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-6-1-sol.html)।

## Bedrock Converse { #bedrock-converse }

[`BedrockConverseModel`][pydantic_ai.models.bedrock.BedrockConverseModel] কথা বলে [Bedrock Runtime Converse API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html)-এর সাথে, যা Bedrock মডেলের সবচেয়ে বড় সেট দেয়।

### ইনস্টল { #install }

`BedrockConverseModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `bedrock` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[bedrock]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[bedrock]"
```

///


### কনফিগারেশন { #configuration }

[AWS Bedrock](https://aws.amazon.com/bedrock/) ব্যবহার করতে, Bedrock চালু থাকা একটি AWS account আর উপযুক্ত credential লাগবে। সরাসরি AWS credential বা একটি আগে কনফিগার করা boto3 client, যেকোনোটি ব্যবহার করতে পারেন।

[`BedrockModelName`][pydantic_ai.models.bedrock.BedrockModelName]-এ উপলব্ধ Bedrock মডেলের একটি তালিকা আছে, Anthropic, Amazon, Cohere, Meta আর Mistral-এর মডেলসহ।

### Data retention { #data-retention }

Claude Fable 5 আর 5.1-এর জন্য বাছা Region-এ account-এর data retention mode `aws_review` (বা পুরনো `provider_data_share`) হতে হবে। অন্যথায়, প্রতিটি রিকোয়েস্ট একটি 400 [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] দিয়ে ব্যর্থ হয়, বলে যে data retention mode মডেলটির জন্য উপলব্ধ নয়। এটি একটি account সেটিং, রিকোয়েস্ট সেটিং নয়; [AWS data retention ডকুমেন্টেশন](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)-এ যেমন বর্ণিত, Bedrock control plane দিয়ে কনফিগার করুন।

### Environment variable { #environment-variables }

আপনার AWS credential environment variable হিসেবে সেট করতে পারেন ([অন্য বিকল্পের মধ্যে](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#using-environment-variables)):

⟦CODE1⟧

তারপর নাম দিয়ে `BedrockConverseModel` ব্যবহার করতে পারেন:

⟦CODE2⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE3⟧

### Bedrock Runtime API নিজের মতো করা { #customizing-bedrock-runtime-api }

বাড়তি প্যারামিটার যোগ করে Bedrock Runtime API কল নিজের মতো করতে পারেন, যেমন [guardrail
কনফিগারেশন](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) আর [performance সেটিং](https://docs.aws.amazon.com/bedrock/latest/userguide/latency-optimized-inference.html)। কনফিগারযোগ্য প্যারামিটারের সম্পূর্ণ তালিকার জন্য
[`BedrockModelSettings`][pydantic_ai.models.bedrock.BedrockModelSettings]-এর ডকুমেন্টেশন দেখুন।

⟦CODE4⟧

guardrail কনফিগারেশনে `trace` `'enabled'` সেট থাকলে (যেমন ওপরের উদাহরণে), Bedrock-এর ফেরত দেওয়া guardrail মূল্যায়ন হুবহু রাখা হয় [`ModelResponse.provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এর `'trace'` key-এর নিচে, যেমন `result.all_messages()[-1].provider_details['trace']`।

### Output token-এর সীমা { #output-token-limit }

আপনি [`max_tokens`][pydantic_ai.settings.ModelSettings.max_tokens] সেট না করলে, Pydantic AI Claude-এর সর্বোচ্চ আউটপুট পাঠায়, যেমন Claude Sonnet 4.5-এ 64,000 বা Claude Opus 5.5-এ 128,000, ঠিক [Anthropic](anthropic.md)-এর মতো, তাই উত্তর শুধু মডেলের নিজের সীমায় কাটা পড়ে। Bedrock-এর নিজের ডিফল্ট অনেক কম হতে পারে (Claude Opus 5.5-এ 4,096), আর thinking এতে গোনা হয়। একটি inference profile বা foundation model ARN তার নাম দেওয়া মডেল হিসেবে গোনা হয়। Claude Sonnet 4.5-এর চেয়ে পুরনো মডেল, Claude ছাড়া অন্য মডেল, আর একটি application inference profile ARN দিয়ে নাম দেওয়া মডেল Bedrock-এর ডিফল্ট পায়, তাই সেগুলোর জন্য নিজে `max_tokens` সেট করুন, বা application inference profile ARN-টি মূল মডেলের নামসহ [`bedrock_inference_profile`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_inference_profile] হিসেবে দিন।

এমন একটি রিকোয়েস্ট পেছনে stream হয়, কারণ এত দীর্ঘ একটি উত্তরে client-এর read timeout-এর চেয়ে বেশি সময় লাগতে পারে ([`BedrockProvider`][pydantic_ai.providers.bedrock.BedrockProvider]-এ `aws_read_timeout`, ডিফল্ট 300 সেকেন্ড), যা তখন পুরো উত্তর নয়, stream করা টুকরোগুলোর মাঝের অপেক্ষা সীমিত করে। সেই অপেক্ষায় মডেলের thinking-এর সময়ও থাকে, যা একটি একক টুকরো হিসেবে আসতে পারে। Streaming-এর জন্য `bedrock:InvokeModelWithResponseStream` IAM অনুমতি লাগে, যা stream করা রানে আগে থেকেই লাগত, আর উত্তরের টুল কলের `args` একটি dict নয়, stream করা JSON স্ট্রিং, stream করা রানের মতো; [`args_as_dict()`][pydantic_ai.messages.BaseToolCallPart.args_as_dict] একই মান দেয়।

একটি রিকোয়েস্ট শুরু হলে Bedrock আপনার tokens-per-minute quota থেকে `maxTokens` সংরক্ষণ করে রাখে, তাই ছোট Claude quota-র একটি account বেশি `ThrottlingException` দেখতে পারে। কম সংরক্ষণ করতে আর একটি stream নয় এমন `Converse` রিকোয়েস্ট পাঠাতে, প্রত্যাশিত আউটপুটের কাছাকাছি `max_tokens` সেট করুন।

### Thinking আর structured output { #thinking-and-structured-output }

Claude একটি বাধ্য টুল বাছাইয়ের উত্তর thinking ছাড়া দেয়, আর হাতে চালু করা extended thinking
(`bedrock_additional_model_requests_fields={'thinking': {'type': 'enabled', ...}}`) এটি সরাসরি প্রত্যাখ্যান করে। তাই একটি
Claude রিকোয়েস্ট thinking করার সময়, একটি thinking সেটিংয়ের কারণে হোক বা মডেল ডিফল্টভাবে thinking করে বলে (Claude Opus 5 আর
পরেরগুলো, Claude Sonnet 5, Claude Haiku 5.5, Claude Fable 5), Pydantic AI আউটপুট টুল বাধ্য করে না:

- একটি সাধারণ গোছানো `output_type` [`NativeOutput`][pydantic_ai.output.NativeOutput] ব্যবহার করে, যেখানে Bedrock মডেলটির জন্য
  তা সমর্থন করে। অন্যথায় এটি টুল আউটপুট রাখে, `toolChoice={'auto': {}}`-এর অধীনে আউটপুট টুল দিয়ে আর একটি লেখার
  উত্তর আবার চেষ্টা করে। Extended thinking বদলে [`PromptedOutput`][pydantic_ai.output.PromptedOutput]-এ ফিরে যায়।
- একটি স্পষ্ট [`ToolOutput`][pydantic_ai.output.ToolOutput] `toolChoice={'auto': {}}`-এর অধীনে আউটপুট টুল দেয়।

বাধ্য টুল আউটপুট রাখতে, মডেল অনুমতি দিলে `thinking=False` দিয়ে thinking বন্ধ করুন।
দেখুন AWS-এর [adaptive thinking ডকুমেন্টেশন](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html)
আর [forced tool use restrictions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages-tool-use.html#model-parameters-anthropic-claude-forced-tool-use)।

আউটপুট mode রানের প্রথম রিকোয়েস্টে বাছাই হয় আর রানের বাকিটায় থাকে (একটি
[`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর পেছনে ছাড়া, যেখানে প্রতিটি মডেল প্রতিটি রিকোয়েস্টে বাছে), তাই ধাপে ধাপে বদলানো একটি thinking
সেটিং রিকোয়েস্টের মাঝে আউটপুট টুল যোগ বা সরায় না আর
[prompt cache অবৈধ করে](../capabilities/caching.md#what-invalidates-a-cache) না। টুল
আউটপুট দিয়ে শুরু হওয়া একটি Claude রান thinking চালু হলেও তা রাখে, `toolChoice={'auto': {}}`-এর অধীনে আউটপুট টুল দিয়ে। OpenAI GPT-5.6
আর GPT-6 thinking করার সময় আউটপুট টুল নেয়, তাই তারা টুল আউটপুট রাখে (বাধ্য `toolChoice` ছাড়া দেওয়া, যেমন
thinking ছাড়া এই মডেলগুলোতে)। Claude, xAI Grok, আর OpenAI GPT-5.6 ও GPT-6 ছাড়া অন্য মডেল thinking-এর পাশাপাশি
আউটপুট টুল নেয় না, তাই সেখানে thinking করা একটি রিকোয়েস্ট
[`NativeOutput`][pydantic_ai.output.NativeOutput] বা [`PromptedOutput`][pydantic_ai.output.PromptedOutput]-এ বদলে যায়।

xAI Grok 4.6 আর 4.7 (`us.xai.grok-4.6`, `global.xai.grok-4.6`, `us.xai.grok-4.7`, `global.xai.grok-4.7`) সবসময়
reasoning করে, আর Pydantic AI এগুলোর সাথে টুল বাছাই বাধ্য করতে থাকে, কারণ Converse reasoning-এর সময় Grok 4.6-এর সাথে
একটি বাধ্য টুল বাছাই নেয়। একটি `thinking` সেটিং এটি বদলায় না: `tool_choice='required'`, একটি একক বাধ্য টুল, আর
[`ToolOutput`][pydantic_ai.output.ToolOutput] কাজ করতে থাকে।

### Structured output-এ array শর্ত { #array-constraints-in-structured-output }

structured output সমর্থন করা Claude, GLM, Qwen আর Gemma মডেলে, [`NativeOutput`][pydantic_ai.output.NativeOutput] বা স্পষ্টভাবে strict টুল ব্যবহারের সময় Pydantic AI array-র `contains`
শর্ত ফিল্ডের বর্ণনায় সরিয়ে দেয়। Bedrock এই মডেলগুলোর জন্য এই
keyword প্রত্যাখ্যান করে। বর্ণনা শর্তটিকে একটি ইঙ্গিত হিসেবে রাখে; Bedrock তা প্রয়োগ করে না।
Claude-এর জন্য, এটি `type: ['array', 'null']` হিসেবে প্রকাশিত nullable array-তেও প্রযোজ্য।
Non-strict টুল মূল শর্ত রাখে।

### নিজের HTTP header { #custom-http-headers }

`Converse`, `ConverseStream` আর `CountTokens` রিকোয়েস্টে HTTP header যোগ করতে [`ModelSettings.extra_headers`][pydantic_ai.settings.ModelSettings.extra_headers] ব্যবহার করুন। নিজের header চায় এমন একটি API gateway বা proxy দিয়ে রিকোয়েস্ট পাঠাতে এটি কাজে লাগে:

⟦CODE5⟧

boto3-এর পরিচালিত header override করতে `extra_headers` ব্যবহার করবেন না, যেমন `Authorization`, `User-Agent`, `X-Amz-Date`,
`Host` বা `Content-Length`। এই মান উপেক্ষিত হতে পারে বা রিকোয়েস্ট ব্যর্থ করাতে পারে।

### Service tier { #service-tier }

throughput আর খরচ সামলাতে Bedrock [service tier](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html) নিয়ন্ত্রণ সমর্থন করে।
একীভূত [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] ফিল্ড বা provider-নির্দিষ্ট [`bedrock_service_tier`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_service_tier] ফিল্ড ব্যবহার করতে পারেন। দুটোই সেট থাকলে `bedrock_service_tier` একীভূত ফিল্ডের ওপর অগ্রাধিকার পায়।

Bedrock-এর জন্য একীভূত ফিল্ড এভাবে ম্যাপ হয়:

- `'auto'`: রিকোয়েস্ট থেকে `serviceTier` ফিল্ড বাদ পড়ে, তাই AWS তার সার্ভার-পক্ষের ডিফল্ট (Standard tier) প্রয়োগ করে।
- `'default'`: স্পষ্টভাবে `{'type': 'default'}` হিসেবে পাঠানো হয় — premium tier-এ ভবিষ্যতের যেকোনো সার্ভার-পক্ষের স্বয়ংক্রিয় উন্নয়ন থেকে বেরিয়ে আসে।
- `'flex'`: `{'type': 'flex'}` হিসেবে পাঠানো হয়।
- `'priority'`: `{'type': 'priority'}` হিসেবে পাঠানো হয়।

Bedrock-এর `'reserved'` tier চাইতে (যার জন্য আগে কেনা capacity reservation লাগে), সরাসরি [`bedrock_service_tier`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_service_tier] সেট করুন — একীভূত ফিল্ড দিয়ে এতে পৌঁছানো যায় না।

### Prompt caching { #prompt-caching }

Bedrock Anthropic মডেলে [prompt caching](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html) সমর্থন করে, যাতে রিকোয়েস্ট-জুড়ে ব্যয়বহুল প্রসঙ্গ আবার ব্যবহার করতে পারেন।

এটি চালুর provider-নিরপেক্ষ উপায় হলো একীভূত [`ModelSettings.cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং (বা [`Caching`][pydantic_ai.capabilities.Caching] capability): সমর্থনকারী Bedrock মডেলে, `cache=True` টুলের সংজ্ঞা, স্থির নির্দেশনা আর কথোপকথনের শেষে cache point বসায়, নিচের `bedrock_cache_instructions`, `bedrock_cache_tool_definitions` আর `bedrock_cache_messages`-এর সমতুল্য। প্রায় 20টির বেশি বিষয়বস্তু ব্লক যোগ করা একটি দফার পরে, যেমন এক ডজন সমান্তরাল টুল কল আর তাদের ফল, আগের রিকোয়েস্টের শেষেও একটি cache point বসে, কারণ Bedrock আগের রিকোয়েস্টের cache এন্ট্রির জন্য শুধু প্রায় 20টি ব্লক পেছনে দেখে। চাওয়া একটি `'1h'` ধরে রাখার সময় পাঠানো হয় সেই Claude মডেলে যাদের AWS 1-ঘণ্টার TTL দেয়, আর অন্যগুলোতে ডিফল্ট 5 মিনিটে মিলে যায়। খরচের ভারসাম্যের জন্য দেখুন [Caching](../capabilities/caching.md)। provider-নির্দিষ্ট `bedrock_cache_*` সেটিং কোনোটি সেট থাকলে অগ্রাধিকার পায়।

এর বাইরে, Pydantic AI prompt caching ব্যবহারের চারটি provider-নির্দিষ্ট উপায় দেয়:

1. **[`CachePoint`][pydantic_ai.messages.CachePoint] দিয়ে user বার্তা cache করুন**: বর্তমান user বার্তায় তার আগের সবকিছু cache করতে একটি `CachePoint` চিহ্ন বসান। একটি user prompt অংশের শুরুতে একটি `CachePoint`-এর সেই বার্তায় আগে কিছু নেই, তাই এটি বদলে আগের user বার্তার শেষ পর্যন্ত সবকিছু cache করে। বর্ধিত cache সময়কাল বেছে নিতে `CachePoint(ttl='1h')` দিন।
2. **System নির্দেশনা cache করুন**: [`BedrockModelSettings.bedrock_cache_instructions`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_instructions] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন। স্থির আর গতিশীল দুই ধরনের [নির্দেশনা](../agent.md#instructions) থাকলে, cache point শেষ স্থির নির্দেশনার পরে বসে, তাই গতিশীল নির্দেশনা স্থির cache অবৈধ না করে বদলাতে পারে।
3. **টুলের সংজ্ঞা cache করুন**: [`BedrockModelSettings.bedrock_cache_tool_definitions`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_tool_definitions] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন।
4. **সব বার্তা cache করুন**: শেষ user বার্তা নিজে থেকে cache করতে [`BedrockModelSettings.bedrock_cache_messages`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_messages] `True` সেট করুন (ডিফল্টভাবে 5m TTL ব্যবহার করে) বা সরাসরি `'5m'` / `'1h'` দিন।

এক-ঘণ্টার cache point একটি পাঁচ-মিনিটেরটির পরে এলে Anthropic মডেল রিকোয়েস্ট প্রত্যাখ্যান করে (cache point প্রক্রিয়া হয় টুল, তারপর system, তারপর বার্তার ক্রমে), তাই একটি এক-ঘণ্টার cache point পাঁচ-মিনিটেরগুলোর পরে এলে, সেই আগের cache point-গুলো এক ঘণ্টায় তোলা হয়।

/// note | ন্যূনতম token সীমা

একটি অংশ provider-নির্দিষ্ট ন্যূনতম token সীমা পেরোলেই শুধু AWS cache করা বিষয়বস্তু দেয় (দেখুন [Bedrock prompt caching ডক](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html))। সেই সীমার নিচের ছোট prompt বা টুলের সংজ্ঞা cache এড়িয়ে যাবে, তাই ছোট payload-এ সাশ্রয় আশা করবেন না।

///

#### উদাহরণ ১: স্বয়ংক্রিয় বার্তা caching { #example-1-automatic-message-caching }

শেষ user বার্তা নিজে থেকে cache করতে `bedrock_cache_messages` ব্যবহার করুন:

⟦CODE6⟧

#### উদাহরণ ২: পূর্ণাঙ্গ caching কৌশল { #example-2-comprehensive-caching-strategy }

সর্বোচ্চ সাশ্রয়ের জন্য একাধিক cache সেটিং মেলান:

⟦CODE7⟧

#### উদাহরণ ৩: CachePoint দিয়ে সূক্ষ্ম নিয়ন্ত্রণ { #example-3-fine-grained-control-with-cachepoint }

cache-এর জায়গা নিখুঁতভাবে নিয়ন্ত্রণ করতে হাতে বসানো `CachePoint` চিহ্ন ব্যবহার করুন:

⟦CODE8⟧

#### Cache usage-এর পরিসংখ্যান দেখা { #accessing-cache-usage-statistics }

[`RequestUsage`][pydantic_ai.usage.RequestUsage] দিয়ে cache usage-এর পরিসংখ্যান দেখুন:

⟦CODE9⟧

#### Cache point-এর সীমা { #cache-point-limits }

Bedrock প্রতি রিকোয়েস্টে সর্বোচ্চ 4টি cache point প্রয়োগ করে। আপনার রিকোয়েস্ট যাতে সবসময় এরর ছাড়া মেনে চলে, Pydantic AI নিজে থেকে এই সীমা সামলায়।

##### Cache point কীভাবে বরাদ্দ হয় { #how-cache-points-are-allocated }

Cache point তিনটি জায়গায় বসানো যায়:

1. **System prompt**: `bedrock_cache_instructions` সেটিং দিয়ে (শেষ system prompt ব্লকে cache point যোগ করে)
2. **টুলের সংজ্ঞা**: `bedrock_cache_tool_definitions` সেটিং দিয়ে (শেষ টুল সংজ্ঞায় cache point যোগ করে)
3. **বার্তা**: `CachePoint` চিহ্ন বা `bedrock_cache_messages` সেটিং দিয়ে (বার্তার বিষয়বস্তুতে cache point যোগ করে)

প্রতিটি সেটিং **সর্বোচ্চ 1টি cache point** ব্যবহার করে, তবে এগুলো মেলাতে পারেন। ব্যতিক্রম `bedrock_cache_messages`: প্রায় 20টির বেশি বিষয়বস্তু ব্লক যোগ করা একটি দফার পরে, এটি আগের রিকোয়েস্টের শেষও চিহ্নিত করে, কারণ Bedrock আগের রিকোয়েস্টের cache এন্ট্রির জন্য শুধু প্রায় 20টি ব্লক পেছনে দেখে।

##### স্বয়ংক্রিয় cache point সীমা { #automatic-cache-point-limiting }

সব উৎস থেকে cache point (সেটিং + `CachePoint` চিহ্ন) 4 ছাড়ালে, Pydantic AI নিজে থেকে **পুরনো বার্তার বিষয়বস্তু** থেকে বাড়তি cache point সরায় (সবচেয়ে সাম্প্রতিকগুলো রেখে)।

⟦CODE10⟧

**মূল বিষয়**:

- System আর টুলের cache point **সবসময় রক্ষিত** থাকে
- `bedrock_cache_messages`-এর তৈরি cache point **সবসময় রক্ষিত** থাকে (কারণ এটি সবচেয়ে নতুন বার্তা cache point)
- সীমা ছাড়ালে বার্তার বাড়তি `CachePoint` চিহ্ন সবচেয়ে পুরনো থেকে নতুনের দিকে সরানো হয়
- এতে বার্তা-স্তরের caching-এর সুবিধা পেয়েও গুরুত্বপূর্ণ caching (নির্দেশনা/টুল) বজায় থাকে

### `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `BedrockProvider` দিতে পারেন। সরাসরি credential দিতে বা একটি নিজের boto3 client ব্যবহার করতে চাইলে এটি কাজে লাগে:

⟦CODE11⟧

একটি আগে কনফিগার করা boto3 client-ও দিতে পারেন:

⟦CODE12⟧

### AWS Application Inference Profile ব্যবহার { #using-aws-application-inference-profiles }

খরচ ট্র্যাকিং আর রিসোর্স ব্যবস্থাপনার জন্য AWS Bedrock [নিজের application inference profile](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-create.html) সমর্থন করে। মডেলের সক্ষমতা চেনার জন্য মূল মডেলের নাম রেখে একটি inference profile দিয়ে রিকোয়েস্ট পাঠাতে [`bedrock_inference_profile`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_inference_profile] সেট করুন:

⟦CODE13⟧

### Retry কনফিগার করা { #configuring-retries }

এই boto3 retry হলো Bedrock-এর provider SDK retry স্তর — boto3 অন্য দিক থেকে গোনে, তাই `Config(retries={'max_attempts': N})` মোট `1 + N`টি প্রচেষ্টা অনুমোদন করে — আর boto3-এর নিচে কোনো `httpx2` transport স্তর নেই, তাই এজেন্টের retry বাজেট আর নেটওয়ার্কের মাঝে এটিই একমাত্র retry স্তর। স্তরগুলো কীভাবে একটির ওপর আরেকটি চাপে তা দেখুন [Retry multiplication](../retries.md#retry-multiplication)-এ।

Bedrock boto3-এর নিজস্ব retry ব্যবস্থা ব্যবহার করে, যা প্রতি client-এ কনফিগার হয়, তাই [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request)-এর Bedrock-এ কোনো প্রভাব নেই। retry সেটিংসহ একটি নিজের boto3 client দিয়ে retry আচরণ কনফিগার করতে পারেন:

⟦CODE14⟧

#### Retry mode { #retry-modes }

- `'legacy'` (ডিফল্ট): 5টি প্রচেষ্টা, মৌলিক retry আচরণ
- `'standard'`: 3টি প্রচেষ্টা, আরও বিস্তৃত এরর আওতা
- `'adaptive'`: client-পক্ষের rate limiting-সহ 3টি প্রচেষ্টা (`ThrottlingException` সামলাতে প্রস্তাবিত)

boto3 retry কনফিগারেশনের আরও বিস্তারিত জানতে দেখুন [AWS boto3 ডকুমেন্টেশন](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html)।

/// note | মনে রাখুন

HTTP রিকোয়েস্টে httpx ব্যবহার করা অন্য provider-এর মতো নয়, Bedrock boto3-এর নিজস্ব retry ব্যবস্থা ব্যবহার করে। [Transport retries](../retries.md#transport-retries)-এ বর্ণিত retry কৌশল Bedrock-এ প্রযোজ্য নয়।

///

## Bedrock Mantle { #bedrock-mantle }

[Amazon Bedrock Mantle](https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-mantle.html) একটি OpenAI-সামঞ্জস্যপূর্ণ API দিয়ে OpenAI GPT-5.x আর GPT-OSS মডেল দেয়। কোন মডেল Converse দিয়েও পাওয়া যায় তা দেখুন [OpenAI model routes](#bedrock-openai-model-routes)-এ। `bedrock-mantle:` উপসর্গ ব্যবহার করুন:

⟦CODE15⟧

এর জন্য `bedrock-mantle` ঐচ্ছিক group লাগে:

/// tab | pip

```bash
pip install "pydantic-ai-slim[bedrock-mantle]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[bedrock-mantle]"
```

///


[`BedrockMantleProvider`][pydantic_ai.providers.bedrock_mantle.BedrockMantleProvider] [Converse পথের](#environment-variables) মতো একই AWS credential দিয়ে প্রমাণীকরণ করে — `AWS_BEARER_TOKEN_BEDROCK` দিয়ে একটি bearer token, বা SigV4 দিয়ে AWS access key / profile — আর `region_name` (বা `AWS_DEFAULT_REGION` / `AWS_REGION` environment variable) থেকে তার endpoint বের করে।

মডেলের নাম endpoint পরিবার ঠিক করে:

| মডেলের নাম | Interface |
|---|---|
| GPT-5.4+, যেমন `bedrock-mantle:openai.gpt-5.6-luna` | `/openai/v1`-এ OpenAI Responses |
| GPT-OSS, যেমন `bedrock-mantle:openai.gpt-oss-120b` | `/v1`-এ OpenAI Responses |
| GPT-OSS Safeguard, যেমন `bedrock-mantle:openai.gpt-oss-safeguard-20b` | `/v1`-এ OpenAI Chat Completions |

একটি নিজের Mantle origin (যেমন একটি proxy) ব্যবহার করতে, [`BedrockMantleProvider`][pydantic_ai.providers.bedrock_mantle.BedrockMantleProvider]-এ একটি `base_url` দিন; এর origin (যেকোনো `/openai/v1` বা `/v1` প্রত্যয় বাদ দিয়ে) প্রতি মডেলে দুই endpoint পরিবারের মধ্যে পাঠাতে ব্যবহার হয়, ঠিক `region_name`-এর মতো:

⟦CODE16⟧

### সুবিধার সমর্থন { #feature-support }

Mantle মডেল Pydantic AI-এর OpenAI মডেল ক্লাস দিয়ে পরিবেশিত — [`BedrockMantleResponsesModel`][pydantic_ai.models.bedrock_mantle.BedrockMantleResponsesModel] আর [`BedrockMantleChatModel`][pydantic_ai.models.bedrock_mantle.BedrockMantleChatModel] — তাই এগুলো সরাসরি [OpenAI](openai.md) মডেলের মতো একই সেটিং নেয় ([`OpenAIResponsesModelSettings`][pydantic_ai.models.openai.OpenAIResponsesModelSettings] আর [`OpenAIChatModelSettings`][pydantic_ai.models.openai.OpenAIChatModelSettings])।

ওপরের Converse-পথের সুবিধা — [prompt caching](#prompt-caching), [service tier](#service-tier) আর [application inference profile](#using-aws-application-inference-profiles) — Converse API-র নিজস্ব আর Mantle পথে প্রযোজ্য নয়। বিশেষ করে [`bedrock_service_tier`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_service_tier] একটি Converse সেটিং; Mantle মডেল একীভূত [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] একই নামের OpenAI প্যারামিটার হিসেবে পাঠায়, কারণ এগুলো OpenAI মডেল ক্লাস দিয়ে পরিবেশিত।

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[bedrock]"`, AWS credential, তারপর `Agent('bedrock:<model-id>')`।
* OpenAI GPT-5.4/5.5 বা Mantle-এর OpenAI API দরকার হলে `bedrock-mantle:`।
* Claude Fable-এ account-এর data retention mode ঠিক করুন; বড় `max_tokens` quota আটকে রাখে।
* Caching: `cache=True` বা `bedrock_cache_*`; সর্বোচ্চ ৪টি cache point।
* Retry boto3 `Config(retries=...)` দিয়ে; `max_retries` সেটিং এখানে কাজ করে না।

///
