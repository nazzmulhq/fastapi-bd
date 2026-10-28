# অন্য সামঞ্জস্যপূর্ণ API { #other-compatible-apis }

/// note | এই পেজে যা শিখবেন

* OpenAI Chat Completions API মানা সার্ভিস (Alibaba, Fireworks, Heroku, LiteLLM, Nebius, OVHcloud, SambaNova, Together, Vercel, vLLM) ব্যবহার।
* provider নেই এমন যেকোনো OpenAI-সামঞ্জস্যপূর্ণ endpoint-এ সংযোগ।
* Model profile দিয়ে অনুরোধের আকার ঠিক করা, আর সাধারণ সমস্যা (একাধিক system বার্তা, অসম্পূর্ণ stream)।

///

অনেক inference প্ল্যাটফর্ম, gateway আর নিজে হোস্ট করা সার্ভার OpenAI Chat Completions API বাস্তবায়ন করে। এই পেজের প্রতিটি সার্ভিসের জন্য Pydantic AI-এর একটি provider আছে, তাই একটি ব্যবহার করা OpenAI ব্যবহারের মতোই কাজ করে: সার্ভিসের API key environment variable সেট করুন আর [`Agent`][pydantic_ai.Agent]-কে `<provider>:<model>` দিন:

⟦CODE1⟧

provider endpoint আর প্রমাণীকরণ সেট করে, আর একটি [model profile](#model-profile) বাছে যা সার্ভিসের মডেলের নাম আর API-র আচরণ বিবেচনা করে। নিজস্ব গাইড আছে এমন সার্ভিস, যেমন [DeepSeek](deepseek.md), [OpenRouter](openrouter.md) আর [Ollama](ollama.md), তালিকাভুক্ত আছে [provider directory](overview.md#provider-directory)-তে।

Pydantic AI-এর provider নেই এমন একটি endpoint-এ সংযোগ করতে, দেখুন [Other endpoints](#other-endpoints)।

/// tip | উদাহরণ দিয়ে বুঝি

"OpenAI-সামঞ্জস্যপূর্ণ" মানে সার্ভিসটি OpenAI-এর মতো একই ভাষায় (একই URL পথ, একই JSON আকার) কথা বলে। তাই একই দোভাষী (`OpenAIChatModel`) শুধু ঠিকানা (`base_url`) আর চাবি (`api_key`) বদলে সেখানে কাজ করতে পারে। তবে প্রতিটি সার্ভিসের নিজস্ব খুঁটিনাটি আছে — সেগুলো সামলায় profile।

///

## ইনস্টল { #install }

এই সংযোগগুলো OpenAI SDK ব্যবহার করে:

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


## Alibaba Cloud Model Studio (DashScope) { #alibaba-cloud-model-studio-dashscope }

[Alibaba Cloud Model Studio (DashScope)](https://www.alibabacloud.com/en/product/modelstudio) দিয়ে Qwen মডেল ব্যবহার করতে, `ALIBABA_API_KEY` (বা `DASHSCOPE_API_KEY`) environment variable সেট করে নাম দিয়ে [`AlibabaProvider`][pydantic_ai.providers.alibaba.AlibabaProvider] ব্যবহার করতে পারেন:

⟦CODE2⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE3⟧

`AlibabaProvider` ডিফল্টভাবে আন্তর্জাতিক DashScope সামঞ্জস্যপূর্ণ endpoint `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` ব্যবহার করে। একটি নিজের `base_url` দিয়ে এটি override করতে পারেন:

⟦CODE4⟧

/// note | ডকুমেন্ট ইনপুট সমর্থিত নয়

DashScope compatible-mode Chat Completions API ডকুমেন্ট বিষয়বস্তুর অংশ নেয় না, তাই [`AlibabaProvider`][pydantic_ai.providers.alibaba.AlibabaProvider]-সমর্থিত একটি [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel]-এ একটি [`DocumentUrl`][pydantic_ai.messages.DocumentUrl] বা ডকুমেন্ট [`BinaryContent`][pydantic_ai.messages.BinaryContent] দিলে একটি `UserError` ওঠে।

///

## Fireworks AI { #fireworks-ai }

[Fireworks.AI](https://fireworks.ai/)-এ গিয়ে account সেটিংয়ে একটি API key তৈরি করুন।

`FIREWORKS_API_KEY` environment variable সেট করে নাম দিয়ে [`FireworksProvider`][pydantic_ai.providers.fireworks.FireworksProvider] ব্যবহার করতে পারেন:

⟦CODE5⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE6⟧

Fireworks-এর schema-সীমিত structured output-এর জন্য [`NativeOutput`][pydantic_ai.output.NativeOutput] ব্যবহার করুন।
Fireworks তার OpenAI-সামঞ্জস্যপূর্ণ `response_format` প্যারামিটার দিয়ে schema প্রয়োগ করে।
[Fireworks structured output ডকুমেন্টেশন](https://docs.fireworks.ai/structured-responses/structured-response-formatting)-এ যেমন বর্ণিত, `pattern` প্রয়োগ যথাসাধ্য: অসমর্থিত regex গঠন, যেমন lookahead আর lookbehind, উপেক্ষিত হয়, ফিল্ডটিকে একটি সীমাহীন স্ট্রিং রেখে। Pydantic AI তবুও আউটপুট যাচাই করে, তাই pattern-এর সাথে না মেলা একটি মান একটি আউটপুট retry ঘটায়।

## Heroku AI { #heroku-ai }

[Heroku AI](https://www.heroku.com/ai) ব্যবহার করতে, প্রথমে একটি API key তৈরি করুন।

`HEROKU_INFERENCE_KEY` আর (ঐচ্ছিকভাবে) `HEROKU_INFERENCE_URL` environment variable সেট করে নাম দিয়ে [`HerokuProvider`][pydantic_ai.providers.heroku.HerokuProvider] ব্যবহার করতে পারেন:

⟦CODE7⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE8⟧

## LiteLLM { #litellm }

/// note | `litellm` প্যাকেজের ওপর নির্ভরতা নেই

`LiteLLMProvider` `litellm` Python প্যাকেজ ইনস্টল বা import করে না। এটি OpenAI client দিয়ে HTTP-তে একটি LiteLLM proxy-র সাথে কথা বলে।

///

[`LiteLLMProvider`][pydantic_ai.providers.litellm.LiteLLMProvider] একটি [LiteLLM proxy](https://docs.litellm.ai/docs/simple_proxy)-তে সংযোগ করে, যা এর সাথে কনফিগার করা upstream provider-দের জন্য রিকোয়েস্ট অনুবাদ করে। proxy-র URL (যেমন `http://localhost:<port>`) `api_base` হিসেবে আর আপনার LiteLLM key (বা একটি স্থানধারক) `api_key` হিসেবে দিন। রিকোয়েস্ট Chat Completions হিসেবে যেমন আছে তেমন `api_base`-এ পাঠানো হয়, তাই আপনি এটিকে সরাসরি একটি OpenAI-সামঞ্জস্যপূর্ণ upstream-এও দেখাতে পারেন, যেমন আপনার OpenAI key-সহ `https://api.openai.com/v1`, কিন্তু এমন একটি API-তে নয় যা শুধু LiteLLM অনুবাদ করতে পারে। নিজের LLM-এর জন্য `custom/` মডেল-নামের উপসর্গ ব্যবহার করুন।

⟦CODE9⟧

/// note | মনে রাখুন

আপনার মডেল একাধিক শুরুর system বার্তাসহ রিকোয়েস্ট প্রত্যাখ্যান করলে (যেমন আপনি
`System message must be at the beginning.` দেখলে), এর profile-এ
`openai_chat_supports_multiple_system_messages=False` সেট করুন। বিস্তারিত জানতে দেখুন
[Models that accept only one leading system message](#models-that-accept-only-one-leading-system-message)।

///

## Nebius AI Studio { #nebius-ai-studio }

[Nebius AI Studio](https://studio.nebius.com/)-এ গিয়ে একটি API key তৈরি করুন।

`NEBIUS_API_KEY` environment variable সেট করে নাম দিয়ে [`NebiusProvider`][pydantic_ai.providers.nebius.NebiusProvider] ব্যবহার করতে পারেন:

⟦CODE10⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE11⟧

## OVHcloud AI Endpoints { #ovhcloud-ai-endpoints }

OVHcloud AI Endpoints ব্যবহার করতে, একটি নতুন API key তৈরি করতে হবে। এর জন্য [OVHcloud manager](https://ovh.com/manager)-এ গিয়ে, তারপর Public Cloud > AI Endpoints > API keys-এ যান। `Create a new API key`-এ ক্লিক করে নতুন key কপি করুন।

কোন মডেল পাওয়া যায় তা খুঁজতে [catalog](https://endpoints.ai.cloud.ovh.net/catalog) দেখতে পারেন।

`OVHCLOUD_API_KEY` environment variable সেট করে নাম দিয়ে [`OVHcloudProvider`][pydantic_ai.providers.ovhcloud.OVHcloudProvider] ব্যবহার করতে পারেন:

⟦CODE12⟧

provider কনফিগার করতে হলে, [`OVHcloudProvider`][pydantic_ai.providers.ovhcloud.OVHcloudProvider] ক্লাস ব্যবহার করতে পারেন:

⟦CODE13⟧

## SambaNova { #sambanova }

[SambaNova Cloud](https://cloud.sambanova.ai/) ব্যবহার করতে, [SambaNova Cloud dashboard](https://cloud.sambanova.ai/dashboard) থেকে একটি API key নিতে হবে।

SambaNova দ্রুত inference-সহ Meta Llama, DeepSeek, Qwen আর Mistral মডেলসহ একাধিক মডেল পরিবারে প্রবেশ দেয়।

`SAMBANOVA_API_KEY` environment variable সেট করে নাম দিয়ে [`SambaNovaProvider`][pydantic_ai.providers.sambanova.SambaNovaProvider] ব্যবহার করতে পারেন:

⟦CODE14⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE15⟧

উপলব্ধ মডেলের সম্পূর্ণ তালিকার জন্য দেখুন [SambaNova supported models ডকুমেন্টেশন](https://docs.sambanova.ai/docs/en/models/sambacloud-models)।

## Together AI { #together-ai }

[Together.ai](https://www.together.ai/)-এ গিয়ে account সেটিংয়ে একটি API key তৈরি করুন।

`TOGETHER_API_KEY` environment variable সেট করে নাম দিয়ে [`TogetherProvider`][pydantic_ai.providers.together.TogetherProvider] ব্যবহার করতে পারেন:

⟦CODE16⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE17⟧

`deepseek-ai/DeepSeek-V4-*` মডেল thinking চালু থাকাকালীন একটি বাধ্য টুল বাছাই প্রত্যাখ্যান করে, আর thinking তাদের ডিফল্ট। তাই Together-এ Pydantic AI এই মডেলগুলোর জন্য কখনো টুল বাছাই বাধ্য করে না: স্পষ্ট `tool_choice='required'` বা একটি টুলের তালিকা একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে, আর নির্ধারিত আউটপুট-টুল বাধ্য করা `tool_choice='auto'` হিসেবে পাঠানো হয়; [`DeepSeekProvider`][pydantic_ai.providers.deepseek.DeepSeekProvider]-এর মতো নয়, এই নিষেধাজ্ঞা শর্তহীন, কারণ Together DeepSeek-এর thinking টগল মানে কিনা তা যাচাই করা নয়।

## Vercel AI Gateway { #vercel-ai-gateway }

[Vercel-এর AI Gateway](https://vercel.com/docs/ai-gateway) ব্যবহার করতে, প্রথমে একটি API key বা OIDC token পাওয়ার জন্য [ডকুমেন্টেশন](https://vercel.com/docs/ai-gateway)-এর নির্দেশনা অনুসরণ করুন।

`VERCEL_AI_GATEWAY_API_KEY` বা `VERCEL_OIDC_TOKEN` environment variable সেট করে নাম দিয়ে [`VercelProvider`][pydantic_ai.providers.vercel.VercelProvider] ব্যবহার করতে পারেন:

⟦CODE18⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE19⟧

## vLLM { #vllm }

[vLLM](https://docs.vllm.ai/) একটি OpenAI-সামঞ্জস্যপূর্ণ API-সহ উচ্চ-throughput-এর একটি inference সার্ভার। [`VLLMProvider`][pydantic_ai.providers.vllm.VLLMProvider] দিয়ে সংযোগ করুন, সরাসরি বা `VLLM_BASE_URL` দিয়ে `base_url` সেট করে। প্রমাণীকরণ লাগে এমন সার্ভারের জন্য, `api_key` বা `VLLM_API_KEY` সেট করুন।

⟦CODE20⟧

সেই environment variable সেট থাকলে, বদলে নাম দিয়ে provider-এর রেফারেন্স দিতে পারেন:

⟦CODE21⟧

/// note | টুল কলিংয়ে সার্ভার কনফিগারেশন লাগে

যে এজেন্ট মডেলকে টুল ডাকবে কিনা ঠিক করতে দেয়, তার জন্য vLLM `--enable-auto-tool-choice` দিয়ে শুরু করুন আর `--tool-call-parser` দিয়ে মডেল-নির্দিষ্ট parser বাছুন। সমর্থিত মডেল আর parser মানের জন্য দেখুন [vLLM tool calling guide](https://docs.vllm.ai/en/stable/features/tool_calling/)।

///

/// note | একাধিক system বার্তা ডিফল্টভাবে মিলিত হয়

কিছু vLLM chat template একাধিক শুরুর system বার্তা প্রত্যাখ্যান করে, তাই `VLLMProvider` ডিফল্টভাবে সেগুলো মেলায়। বেরিয়ে আসতে, `openai_chat_supports_multiple_system_messages=True`-সহ একটি [`OpenAIModelProfile`][pydantic_ai.profiles.openai.OpenAIModelProfile] দিন। দেখুন [Models that accept only one leading system message](#models-that-accept-only-one-leading-system-message)।

///

## অন্য endpoint { #other-endpoints }

Pydantic AI-এর provider নেই এমন একটি OpenAI-সামঞ্জস্যপূর্ণ সার্ভিস বা সার্ভারের জন্য, এর `base_url` আর `api_key`-সহ [`OpenAIProvider`][pydantic_ai.providers.openai.OpenAIProvider] ব্যবহার করুন, বা `OPENAI_BASE_URL` আর `OPENAI_API_KEY` environment variable সেট করুন। একটি Chat Completions endpoint-এর জন্য [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] ব্যবহার করুন, বা সার্ভিস Responses API বাস্তবায়ন করলে [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel]:

⟦CODE22⟧

একটি API-র সাথে সামঞ্জস্য মানে অন্যটির বা প্রতিটি OpenAI সুবিধার সমর্থন নয়। `OpenAIProvider` OpenAI-এর মডেলও ধরে নেয়: এটি মডেলের নাম থেকে একটি profile বাছে যেন এটি একটি OpenAI মডেল, `base_url` যা-ই হোক। অন্য মডেলের জন্য, [model profile](#model-profile) কনফিগার না করা পর্যন্ত `thinking` বা structured output-এর মতো সুবিধা উপেক্ষিত বা প্রত্যাখ্যাত হতে পারে।

## অ-মানক finish reason { #non-standard-finish-reasons }

একটি OpenAI-সামঞ্জস্যপূর্ণ API OpenAI-এর সংজ্ঞায়িত পাঁচটির বাইরে একটি `finish_reason` ফেরত দিলে, `OpenAIChatModel` উত্তরটি রাখে, একে `None`-এর একটি [`finish_reason`][pydantic_ai.messages.ModelResponse.finish_reason] দেয়, আর কাঁচা মানটি [`provider_details['finish_reason']`][pydantic_ai.messages.ModelResponse.provider_details]-এ রাখে।

## Model profile { #model-profile }

একটি model profile মডেল ক্লাসকে বলে একটি নির্দিষ্ট মডেল আর API-র জন্য রিকোয়েস্ট কীভাবে গঠন করতে হবে: এর টুলের সংজ্ঞার কোন JSON schema সীমাবদ্ধতা আছে, টুল strict হিসেবে চিহ্নিত করা যায় কিনা, reasoning কীভাবে কনফিগার হয়, ইত্যাদি। ওপরের provider-রা মডেলের নামের ভিত্তিতে নিজে থেকে একটি বাছে, তাই এই অংশ আপনার দরকার শুধু যদি একটি নিজের endpoint-এর পেছনের একটি মডেল শুরুতেই ঠিকভাবে কাজ না করে।

রিকোয়েস্ট কীভাবে তৈরি হয় তা বদলাতে আপনার নিজের [`ModelProfile`][pydantic_ai.profiles.ModelProfile] (সব মডেল ক্লাসে ভাগ করা আচরণের জন্য) বা [`OpenAIModelProfile`][pydantic_ai.profiles.openai.OpenAIModelProfile] (OpenAI মডেল ক্লাসের নিজস্ব আচরণের জন্য) দিন:

⟦CODE23⟧

একটি মডেল reasoning সমর্থন করে মানেই endpoint OpenAI-এর `reasoning_effort` মান নেয় না, তাই শুধু মডেল কী পারে তা নয়, endpoint কী নেয় সেই অনুযায়ী ফ্ল্যাগ সেট করুন।

### একাধিক মডেল পরিবার দেওয়া gateway { #custom-openai-compatible-provider }

আপনি নিজের এমন একটি gateway চালালে যার কোনো provider ক্লাস নেই আর যা কয়েকটি নির্মাতার মডেলে পাঠায়, প্রতিটি মডেলে `profile=` না দিয়ে আপনি [`OpenAIProvider`][pydantic_ai.providers.openai.OpenAIProvider]-এর subclass করে [`model_profile()`][pydantic_ai.providers.Provider.model_profile] override করতে পারেন, প্রতিটি মডেলের নাম থেকে একটি profile বাছতে। [`pydantic_ai.profiles`](../api/profiles.md)-এর সহায়ক ফাংশন প্রতিটি মডেল পরিবারের profile ফেরত দেয়:

⟦CODE24⟧

মডেলের নাম শুধু profile খোঁজার জন্য স্বাভাবিক করা হয়; gateway-তে পাঠানো নাম অপরিবর্তিত থাকে। Pydantic AI ফেরত আসা profile [`DEFAULT_PROFILE`][pydantic_ai.profiles.DEFAULT_PROFILE]-এর সাথে মেলায়, আর আপনি [`merge_profile()`][pydantic_ai.profiles.merge_profile]-এর শেষ আর্গুমেন্ট হিসেবে gateway-নির্দিষ্ট override দিতে পারেন। profile-এর সাথে মডেল ক্লাস বদলায় না: gateway যে মডেল পরিবারেই পাঠাক, `OpenAIChatModel` তবুও একটি Chat Completions রিকোয়েস্ট পাঠায়।

### অসম্পূর্ণ stream করা উত্তর ধরা { #detect-incomplete-streamed-responses }

কিছু OpenAI-সামঞ্জস্যপূর্ণ API একটি শেষের `finish_reason` ছাড়াই একটি Chat Completions stream পরিষ্কারভাবে বন্ধ করতে পারে,
যাতে একটি আংশিক উত্তর সম্পূর্ণ মনে হয়: finish reason ছাড়া একটি stream নয় এমন উত্তরের মতো,
এটি `'stop'`-এর একটি [`finish_reason`][pydantic_ai.messages.ModelResponse.finish_reason] পায়। আপনার provider নিশ্চয়তা দিলে যে সম্পূর্ণ
stream-এ একটি finish reason থাকে, model profile-এ
[`openai_chat_streaming_requires_finish_reason=True`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_streaming_requires_finish_reason]
সেট করুন। তাহলে stream একটি ছাড়াই EOF-এ পৌঁছালে Pydantic AI [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]
তুলবে। অপশনটির ডিফল্ট `False`, কারণ কিছু সামঞ্জস্যপূর্ণ API
ফিল্ডটির নিশ্চয়তা দেয় না।

### শুধু একটি শুরুর system বার্তা নেয় এমন মডেল { #models-that-accept-only-one-leading-system-message }

কিছু মডেল এমন একটি chat template দিয়ে পরিবেশিত হয় (সার্ভারে প্রয়োগ করা, যেমন [vLLM](https://docs.vllm.ai/), [LiteLLM](#litellm) বা TGI দিয়ে) যা কথোপকথনের শুরুতে শুধু একটি system বার্তা নেয় আর বাড়তিগুলো প্রত্যাখ্যান করে। একাধিক পাঠালে একটি `400` এরর দিয়ে ব্যর্থ হয়, যেমন `System message must be at the beginning.` বা `Conversation roles must alternate ...`, যা দেখা গেছে কিছু নতুন Qwen, Mistral, Gemma আর Command-R মডেলে। না চেয়েও এতে পড়া সহজ, কারণ কয়েকভাবে একাধিক শুরুর system বার্তা তৈরি হতে পারে।

রিকোয়েস্ট পাঠানোর আগে শুরুর system বার্তাগুলো দুটি নতুন লাইন দিয়ে জুড়ে একটিতে মেলাতে মডেলের [`OpenAIModelProfile`][pydantic_ai.profiles.openai.OpenAIModelProfile]-এ `openai_chat_supports_multiple_system_messages=False` সেট করুন (যেমন দেখানো হয়েছে [Model profile](#model-profile)-এ)। মেলানো ক্ষতিহীন, তাই একটি backend একাধিক system বার্তা প্রত্যাখ্যান করলেই এটি চালু করা নিরাপদ।

/// check | সংক্ষেপে মনে রাখুন

* তালিকাভুক্ত সার্ভিসে: API key environment variable + `Agent('<provider>:<model>')`।
* তালিকার বাইরে: `OpenAIChatModel(name, provider=OpenAIProvider(base_url=..., api_key=...))`।
* অপরিচিত মডেলে সুবিধা ঠিকমতো না চললে `profile=OpenAIModelProfile(...)` দিয়ে ঠিক করুন।
* `System message must be at the beginning.` এরর পেলে `openai_chat_supports_multiple_system_messages=False`।

///
