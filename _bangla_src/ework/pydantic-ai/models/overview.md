# মডেল আর Provider { #models-and-providers }

/// note | এই পেজে যা শিখবেন

* `'provider:model'` নাম দিয়ে মডেল বাছাই, আর Model, Provider, Profile — তিনটি শব্দের অর্থ।
* একটি মডেল কী পারে (profile) তা দেখা, HTTP client-এর জীবনকাল আর কনফিগারেশন।
* নিজের মডেল ক্লাস, একসাথে কতগুলো রিকোয়েস্ট চলবে তা সীমিত করা।
* মডেল API এররের শ্রেণি, আর `FallbackModel` দিয়ে একটি মডেল ব্যর্থ হলে আরেকটিতে যাওয়া।

///

Pydantic AI মডেল নির্মাতা, cloud প্ল্যাটফর্ম, inference সার্ভিস, gateway আর লোকাল মডেল সার্ভার সমর্থন করে। নিচে আপনার সার্ভিস খুঁজুন আর ইনস্টলেশন, প্রমাণীকরণ আর সমর্থিত সুবিধার জন্য এর সেটআপ গাইড অনুসরণ করুন।

## Provider তালিকা { #provider-directory }

একটি provider তার উপসর্গ দিয়ে বাছতে [`Agent`][pydantic_ai.Agent]-কে `<provider>:<model>` রূপে একটি নাম দিন। কিছু পথে বদলে একটি স্পষ্ট মডেল বা client লাগে; প্রতিটি সেটআপ গাইড উপলব্ধ বিকল্প দেখায়।

⟦CODE1⟧

/// tip | প্রতিটি মডেলের জন্য একটি key

একাধিক provider-এর মডেল চেষ্টা করার সবচেয়ে সহজ উপায় হলো [Pydantic AI Gateway](../gateway.md): OpenAI, Anthropic, Google Cloud, Groq আর AWS Bedrock-এর মডেলের জন্য একটি API key, [Pydantic Logfire](../logfire.md)-এ খরচের সীমা আর খরচ পর্যবেক্ষণসহ। `PYDANTIC_AI_GATEWAY_API_KEY` সেট করুন আর মডেলের স্ট্রিংয়ে `gateway/` উপসর্গ যোগ করুন, যেমন `Agent('gateway/anthropic:claude-fable-5-1')`। একটি key কীভাবে তৈরি করবেন তা দেখায় [Gateway quick start](../gateway.md#quick-start)।

///

সার্ভিসের বর্ণনা আপনাকে একটি deployment বিকল্প খুঁজে পেতে সাহায্য করে; একটি কোম্পানি একাধিক ধরনের সার্ভিস দিতে পারে। দুটি সার্ভিস একই API ফরম্যাট ব্যবহার করলেও, সুবিধার সমর্থন আপনার বাছা মডেল আর API-র ওপর নির্ভর করে।

এখানে তালিকাভুক্ত নয় এমন একটি OpenAI-সামঞ্জস্যপূর্ণ endpoint-এর জন্য, দেখুন [Other endpoints](compatible-apis.md#other-endpoints); অন্য যেকোনো API-র জন্য, একটি [নিজের মডেল](#custom-models) বাস্তবায়ন করুন।

টেস্ট আর ডেভেলপমেন্টের জন্য, [`TestModel`](../api/models/test.md) বা [`FunctionModel`](../api/models/function.md) ব্যবহার করুন।

### OpenAI-সামঞ্জস্যপূর্ণ Provider { #openai-compatible-providers }

তালিকার অনেক এন্ট্রি OpenAI-সামঞ্জস্যপূর্ণ API ব্যবহার করে। তাদের সেটআপ গাইড বলে কোন মডেল ক্লাস ব্যবহার করবেন; [Other compatible APIs](compatible-apis.md) নিজের endpoint আর মডেল profile ব্যাখ্যা করে।

## মডেল, provider আর profile { #models-and-providers }

বিভিন্ন LLM-এর সাথে কীভাবে কাজ করে তা বর্ণনা করতে Pydantic AI কয়েকটি মূল শব্দ ব্যবহার করে:

- **Model**: এটি সেই Pydantic AI ক্লাস যা একটি নির্দিষ্ট LLM API মেনে রিকোয়েস্ট করে
  (সাধারণত একটি vendor-এর দেওয়া SDK মুড়ে, যেমন `openai` python SDK)। এই ক্লাসগুলো একটি
  vendor-SDK-নিরপেক্ষ API বাস্তবায়ন করে, যাতে একটি Pydantic AI এজেন্ট অন্য কোনো কোড না বদলে
  শুধু ব্যবহৃত Model বদলে ভিন্ন LLM vendor-এ নেওয়া যায়। Model ক্লাসের নাম
  মোটামুটি `<VendorSdk>Model` ধাঁচে, যেমন আমাদের আছে `OpenAIChatModel`, `AnthropicModel`, `GoogleModel`
  ইত্যাদি। একটি Model ক্লাস ব্যবহারের সময়, আসল LLM মডেলের নাম (যেমন `gpt-6.1-sol`,
  `claude-sonnet-5-5`, `gemini-3.8-flash`) একটি প্যারামিটার হিসেবে দেন।
- **Provider**: এটি provider-নির্দিষ্ট ক্লাস, যা একটি LLM vendor-এর সাথে প্রমাণীকরণ আর সংযোগ
  সামলায়। একটি Model-কে প্যারামিটার হিসেবে একটি ডিফল্ট নয় এমন _Provider_ দিয়েই আপনি নিশ্চিত করেন
  যে আপনার এজেন্ট একটি নির্দিষ্ট endpoint-এ রিকোয়েস্ট করবে, বা প্রমাণীকরণের একটি নির্দিষ্ট পদ্ধতি
  ব্যবহার করবে (যেমন `AzureProvider` দিয়ে `OpenAIChatModel`-এর সাথে Azure auth ব্যবহার করতে পারেন)।
  বিশেষ করে, এভাবেই একটি AI gateway, বা এমন একটি LLM vendor ব্যবহার করতে পারেন যা একটি বিদ্যমান Model
  (যেমন `OpenAIChatModel`)-এর ব্যবহৃত vendor SDK-র সাথে API সামঞ্জস্য দেয়।
- **Profile**: এটি একটি বর্ণনা, যে একটি নির্দিষ্ট মডেল বা মডেল-পরিবারে সেরা ফলের জন্য রিকোয়েস্ট কীভাবে
  তৈরি করতে হবে, ব্যবহৃত মডেল আর provider ক্লাস থেকে স্বাধীনভাবে।
  যেমন, টুলের জন্য ব্যবহারযোগ্য JSON schema-য় বিভিন্ন মডেলের বিভিন্ন সীমাবদ্ধতা আছে,
  আর Gemini মডেলের জন্য একই schema transformer ব্যবহার করতে হয়, আপনি `GoogleModel` ব্যবহার করুন
  বা `OpenRouterProvider`-সহ `OpenAIChatModel`।

/// tip | উদাহরণ দিয়ে বুঝি

**Model** হলো একজন দোভাষী যিনি একটি নির্দিষ্ট ভাষা (API ফরম্যাট) বলেন। **Provider** হলো কোন অফিসে (endpoint) আর কোন পরিচয়পত্র (API key) নিয়ে তিনি কথা বলতে যাবেন। **Profile** হলো সেই নির্দিষ্ট শ্রোতার (মডেল) পছন্দ-অপছন্দের তালিকা: কোন ধরনের প্রশ্ন সে ভালো বোঝে, কোনটি বোঝে না। একই দোভাষী (`OpenAIChatModel`) ভিন্ন অফিসে (OpenRouter, Azure) গিয়ে ভিন্ন শ্রোতার (Gemini, GPT) সাথে কথা বলতে পারেন।

///

আপনি যখন একটি [`Agent`][pydantic_ai.Agent] শুধু `<provider>:<model>` রূপের একটি নাম দিয়ে তৈরি করেন, যেমন `openai:gpt-6.1-sol` বা `openrouter:google/gemini-3-pro-preview`,
Pydantic AI নিজে থেকে উপযুক্ত মডেল ক্লাস, provider আর profile বেছে নেয়।
একটি ভিন্ন provider বা profile ব্যবহার করতে চাইলে, সরাসরি একটি মডেল ক্লাস তৈরি করে `provider` আর/বা `profile` আর্গুমেন্ট দিতে পারেন।

### একটি মডেলের profile দেখা { #inspecting-a-models-profile }

একটি মডেলের [`ModelProfile`][pydantic_ai.profiles.ModelProfile] মডেলটি কী পারে তাও বর্ণনা করে। এটি একটি `TypedDict` যার সব key ঐচ্ছিক, তাই `model.profile`-এ `.get()` দিয়ে সক্ষমতার ফ্ল্যাগ পড়েন — যেমন [`supports_text_output`][pydantic_ai.profiles.ModelProfile.supports_text_output], [`supports_tools`][pydantic_ai.profiles.ModelProfile.supports_tools], [`supports_json_schema_output`][pydantic_ai.profiles.ModelProfile.supports_json_schema_output], আর [`supported_native_tools`][pydantic_ai.profiles.ModelProfile.supported_native_tools]। রিকোয়েস্টের সময় একটি সীমাবদ্ধতা আবিষ্কার না করে একটি সক্ষমতার ওপর শাখা তৈরি করতে চাইলে এটি কাজে লাগে — যেমন ভরসা করার আগে একটি মডেল লেখা তৈরি, টুল কলিং, নেটিভ JSON-schema আউটপুট, বা একটি নির্দিষ্ট নেটিভ টুল সমর্থন করে কিনা পরীক্ষা করা:

⟦CODE2⟧

Profile আরও বলে মডেল কোন ধরনের ফাইল নেয়: [`supports_image_input`][pydantic_ai.profiles.ModelProfile.supports_image_input], [`supports_document_input`][pydantic_ai.profiles.ModelProfile.supports_document_input] ([`supported_document_media_types`][pydantic_ai.profiles.ModelProfile.supported_document_media_types] দিয়ে নির্দিষ্ট ডকুমেন্ট টাইপে সংকুচিত), [`supports_audio_file_input`][pydantic_ai.profiles.ModelProfile.supports_audio_file_input] আর [`supports_video_input`][pydantic_ai.profiles.ModelProfile.supports_video_input]। প্রতিটি মডেল ক্লাস তার API যা নিতে পারে না তা বন্ধ করে, profile যা-ই বলুক: যেমন [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel] অডিও বা ভিডিও কোনোটিই পড়ে না, আর শুধু PDF আর সাধারণ-লেখার ডকুমেন্ট পড়ে। মডেল নিতে পারে না এমন একটি টুলের ফেরত দেওয়া ফাইল [তার নাম লেখা একটি নোট হিসেবে পাঠানো হয়](../tools-advanced.md#tool-return-file-provenance), আর [File Understanding](../capabilities/file-understanding.md) capability কোন ফাইল আগে লেখায় বর্ণনা করবে তা ঠিক করতে একই ফ্ল্যাগ পড়ে।

`model.profile` সাধারণত পুরোপুরি *নির্ধারিত* profile: [`DEFAULT_PROFILE`][pydantic_ai.profiles.DEFAULT_PROFILE]-এর key provider-এর ডিফল্টের সাথে মেলানো হয়, তাই `profile.get('supports_tools')` একটি মান ফেরত দেয়। `profile=` একটি callable হিসেবে দিলে (বা অন্যভাবে একটি আংশিক profile dict থাকলে), অনুপস্থিত key সহ্য করতে ডিফল্টটি বিকল্প হিসেবে দিন, `profile.get('supports_tools', DEFAULT_PROFILE['supports_tools'])` (`DEFAULT_PROFILE` import করার পরে)।
প্রতিটি মডেল adapter তার নির্ধারিত profile একইভাবে দেয়, তাই মডেলটি একটি `<provider>:<model>` নাম থেকে নিজে বাছাই হোক বা সরাসরি তৈরি হোক, একই পরীক্ষা কাজ করে। একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] আলাদা: এর একক কোনো profile নেই, কারণ এর প্রার্থী মডেলগুলোর ভিন্ন সক্ষমতা থাকতে পারে। বদলে `fallback_model.models`-এর প্রতিটি মডেলের profile দেখুন। profile-কে [Capabilities](../capabilities/overview.md)-এর সাথে গুলিয়ে ফেলবেন না, যা টুল, hook আর সেটিংয়ের পুনর্ব্যবহারযোগ্য বান্ডেল, যা আপনি একটি এজেন্টে যোগ করেন — profile বর্ণনা করে ভেতরের মডেলটি নিজে কী সমর্থন করে।

Profile মডেলের [`context_window`][pydantic_ai.profiles.ModelProfile.context_window]-ও বহন করে: একটি রিকোয়েস্টে এটি সর্বোচ্চ কত token সামলাতে পারে, বা অজানা হলে `None`। প্রতিটি মডেল, একটি `FallbackModel` আর [`InstrumentedModel`][pydantic_ai.models.instrumented.InstrumentedModel]-এর মতো wrapper-সহ, এটি [`model.context_window`][pydantic_ai.models.AbstractModel.context_window] হিসেবে দেয়; একটি fallback মডেল তার প্রার্থীদের মধ্যে সবচেয়ে ছোট window জানায়, তাই এতে আঁটা ইতিহাস যে প্রার্থীই উত্তর দিক তাতে আঁটে। একটি রানের ভেতরে, [`ctx.context_window_used`][pydantic_ai.tools.RunContext.context_window_used] ব্যবহৃত ভগ্নাংশ জানায়, বা হিসাব না করা গেলে `None`। এই ক্ষেত্রটি সামলানো একটি উদাহরণের জন্য দেখুন [Compact when the context window fills](../message-history.md#compact-when-the-context-window-fills)।

## HTTP client-এর জীবনকাল { #http-client-lifecycle }

একটি [`Provider`][pydantic_ai.providers.Provider] নিজের HTTP client তৈরি করলে (অর্থাৎ আপনি নিজের `http_client` না দিলে), সেই client-এর জীবনকাল তার দায়িত্বে। [`Agent`][pydantic_ai.Agent]-কে একটি async context manager হিসেবে ব্যবহার করলে ব্লকের ভেতরের প্রতিটি রানজুড়ে HTTP client খোলা থাকে, তাই রানগুলো এর সংযোগ আবার ব্যবহার করে, আর বেরোনোর সময় এটি পরিষ্কারভাবে বন্ধ হয়:

⟦CODE3⟧

একই ফলের জন্য একটি [`Model`][pydantic_ai.models.Model] বা [`Provider`][pydantic_ai.providers.Provider]-ও সরাসরি async context manager হিসেবে ব্যবহার করতে পারেন। একটি দীর্ঘজীবী সার্ভিসে, যেমন একটি web server, সার্ভিস শুরুর সময় একবার এজেন্টে ঢুকুন আর সেই ব্লকের ভেতরে চালান।

/// tip | FastAPI-তে

একটি FastAPI অ্যাপে, `lifespan`-এর ভেতরে `async with agent:` লিখুন, যাতে অ্যাপ চালুর সময় এজেন্টে ঢোকা হয় আর বন্ধের সময় বেরোনো হয়; মাঝের প্রতিটি রিকোয়েস্ট একই সংযোগ আবার ব্যবহার করে।

///

সেই ব্লক ছাড়া কী ঘটে তা নির্ভর করে একটি রানের মডেল কোথা থেকে আসে তার ওপর:

- **এজেন্টের নিজের মডেল, বা একটি রানে দেওয়া একটি `Model` instance:** provider মডেলের সাথে তার HTTP client তৈরি করে, আর একই event loop-এর রানগুলো এটি আবার ব্যবহার করে। আপনি এজেন্ট, মডেল বা provider-এ ঢুকে বেরোনো পর্যন্ত কিছুই client বন্ধ করে না। `defer_model_check=True` দিয়ে তৈরি একটি এজেন্ট তার মডেলের নামকে একটি রানে দেওয়া মডেলের নামের মতো ধরে।
- **একটি রানে দেওয়া মডেলের নাম**, যেমন `agent.run(..., model='openai:gpt-6.1-sol')`, বা একটি [model selector](../capabilities/select-model.md)-এর ফেরত দেওয়া: রান একটি নতুন HTTP client-সহ একটি নতুন provider তৈরি করে, আর শেষে client বন্ধ করে, তাই কোনো সংযোগ আবার ব্যবহার হয় না। `async with agent:`-এর ভেতরে, এজেন্ট বদলে প্রতিটি মডেলের নামের জন্য একটি provider তৈরি করে আর ব্লক থেকে বেরোনো পর্যন্ত পরের রানে সেটি আবার ব্যবহার করে। একটি [`resolve_model_id`](../capabilities/resolve-model-id.md) capability প্রতিটি রানে একই নাম ভিন্নভাবে নির্ধারণ করতে পারে, তাই এটি থাকলে প্রতিটি রান নামটি আবার নির্ধারণ করে।
- **একটি model selector-এর ফেরত দেওয়া একটি `Model` instance:** প্রতিটি রান মডেলে ঢোকে আর বেরোয়, যা রানের শেষে তার provider-এর HTTP client বন্ধ করে আর পরেরটির জন্য একটি নতুন তৈরি করে। `async with agent:`-এর ভেতরে, আবার বাছা একটি মডেল, যা এজেন্ট পরিচয় দিয়ে আলাদা করে চেনে, বদলে এজেন্ট নিজে ঢোকে আর ব্লক থেকে বেরোনো পর্যন্ত খোলা রাখে। selector একটি একক রানের জন্য যে নতুন instance বানায় তা তবুও সেই রান শেষে বন্ধ হয়। একটি `resolve_model_id` capability থাকলে, প্রতিটি রান আবার মডেলে ঢোকে আর বেরোয়।

একটি HTTP client-এর সংযোগ সেই event loop-এর, যা সেগুলো খুলেছে, তাই রানের মাঝে খোলা থাকা একটি client আরেকটি event loop থেকে ব্যবহার করা যায় না। এক thread-এ বারবার [`run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync] কল একটি event loop ভাগ করে, তাই client-ও ভাগ করে। যে এজেন্টে ঢোকা হয়নি তার একটি রান একটি নতুন event loop-এ হলে আর client শেষবার যেটিতে ব্যবহার হয়েছিল সেটি না চললে, যেমন একটি দ্বিতীয় `asyncio.run(agent.run(...))`-এ, provider এর জন্য একটি নতুন client তৈরি করে। পুরনোটি বন্ধ হয় না, কারণ আরেকটি event loop থেকে তা বন্ধ করা যায় না, আর এর নিজেরটি সাধারণত আগেই বন্ধ হয়ে গেছে। তাই প্রতিটি রান যখন নিজের event loop পায়, তার event loop বন্ধ হওয়ার আগে client বন্ধ করতে এর ভেতরে এজেন্টে ঢুকুন। এর মধ্যে পড়ে worker thread-এর একটি pool থেকে `run_sync()` কল, যেমন একটি FastAPI `def` endpoint, একটি Django বা Flask view বা একটি `ThreadPoolExecutor`-এ: প্রতিটি thread-এর নিজের event loop আছে, তাই শেষটির চেয়ে ভিন্ন একটি thread-এ কল client বদলে দেয়, আর পুরনোটি garbage collect না হওয়া পর্যন্ত তার সংযোগ খোলা রাখে। প্রতিটি thread-কে তার নিজের মডেল দিন, বা প্রতিটি thread-এ এজেন্টে ঢুকুন। একই সময়ে চলা event loop client ভাগ করত, তাই প্রতিটিকেও তার নিজের মডেল দিন। একটি durable execution রান client-গুলো ছুঁয়ে দেখে না, কারণ এর রিকোয়েস্ট engine-এর activity, step বা task থেকে পাঠানো হয়।

Pydantic AI শুধু নিজের তৈরি HTTP client-ই বন্ধ করে বা বদলায়। আপনার দেওয়া client বন্ধ করা আপনার দায়িত্ব, সেটি একটি `http_client` হোক বা একটি provider SDK client, যেমন `openai_client`, `anthropic_client` (`AsyncAnthropicVertex`-সহ), Google-এর `client`, Hugging Face-এর `hf_client`, বা `xai_client`। একটি রান আরেকটি event loop-এ হলেও এটি রাখা হয়, যেখানে এটি provider SDK-র নিজের এরর দিয়ে ব্যর্থ হতে পারে, যেমন `RuntimeError: Event loop is closed`।

### HTTP client কনফিগার করা { #configuring-the-http-client }

Pydantic AI-এর তৈরি HTTP client-এর timeout 600 সেকেন্ড ([Google](google.md#long-decode)-এর জন্য 20 মিনিট), 5-সেকেন্ডের connect timeout-সহ, আর সর্বোচ্চ 1000টি সংযোগের একটি connection pool, যার মধ্যে অলস অবস্থায় সর্বোচ্চ 100টি সচল রাখা হয়। এগুলো OpenAI আর Anthropic SDK-র নিজের client-এর ডিফল্ট। এগুলো বদলাতে, [`create_async_httpx2_client()`][pydantic_ai.models.create_async_httpx2_client] দিয়ে একটি client তৈরি করুন, যা বাকি ডিফল্ট আর Pydantic AI-এর `User-Agent` রাখে, আর এটি provider-কে `http_client` হিসেবে দিন:

⟦CODE4⟧

যেহেতু client আপনি তৈরি করেছেন, বন্ধও আপনিই করবেন, এখানে `async with` ব্লক ছেড়ে। একই client একাধিক provider-কে দিলে তারা এর connection pool ভাগ করে। এটি একটি `transport`-ও নেয়, যেমন একটি retry-করা: দেখুন [A retrying client](../retries.md#a-retrying-client)।

Groq, Cohere আর GitHub provider বদলে একটি পুরনো `httpx.AsyncClient` নেয়, যা একই আর্গুমেন্ট দিয়ে নিজে বানান, যেমন `httpx.AsyncClient(timeout=httpx.Timeout(120, connect=5), limits=httpx.Limits(max_connections=200, max_keepalive_connections=50))`।

## নিজের মডেল { #custom-models }

/// note | মনে রাখুন

একটি মডেল API OpenAI API-র সাথে সামঞ্জস্যপূর্ণ হলে, নিজের মডেল ক্লাস লাগবে না, বদলে নিজের [custom provider](compatible-apis.md) দিতে পারেন।

///

এখনো সমর্থিত নয় এমন একটি মডেল API-র সমর্থন বাস্তবায়ন করতে, [`Model`][pydantic_ai.models.Model] abstract base class-এর subclass করতে হবে।
Streaming-এর জন্য, [`StreamedResponse`][pydantic_ai.models.StreamedResponse] abstract base class-ও বাস্তবায়ন করতে হবে।

dataclass সমতাসহ একটি subclass, উত্তরাধিকারসূত্রে পাওয়া একটিসহ, তার dataclass ফিল্ডের সাথে তার `settings` আর `profile` তুলনা করে। পরিচয় দিয়ে hash করা একটি subclass, যেমন `Model`-এর একটি সরাসরি non-dataclass subclass বা একটি সরাসরি `@dataclass(eq=False)` subclass, পরিচয় দিয়ে তুলনা করে। এর `repr` এর `model_name`, যেকোনো dataclass ফিল্ড, আর সেট থাকলে এর `settings` আর `profile` দেখায়। যেকোনোটি বদলাতে subclass-এ `__eq__` বা `__repr__` সংজ্ঞায়িত করুন।

শুরু করার সবচেয়ে ভালো জায়গা হলো বিদ্যমান বাস্তবায়নের source code দেখা, যেমন [`OpenAIChatModel`](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai_slim/pydantic_ai/models/openai.py)।

Pydantic AI-তে নতুন মডেল যোগের অবদান আমরা কখন গ্রহণ করব তার বিস্তারিত জানতে দেখুন [contributing guidelines](../contributing.md#new-model-rules)।

## HTTP রিকোয়েস্টের সমান্তরালতা { #http-request-concurrency }

[`ConcurrencyLimitedModel`][pydantic_ai.ConcurrencyLimitedModel] wrapper দিয়ে একটি মডেলে একসাথে চলা HTTP রিকোয়েস্টের সংখ্যা সীমিত করতে পারেন।
অনেক এজেন্ট একসাথে চালানোর সময় rate limit মানতে বা রিসোর্সের ব্যবহার সামলাতে এটি কাজে লাগে।

⟦CODE5⟧

`limiter` প্যারামিটার নেয়:

- সাধারণ সীমার জন্য একটি পূর্ণসংখ্যা (যেমন `limiter=5`)
- backpressure নিয়ন্ত্রণসহ উন্নত কনফিগারেশনের জন্য একটি [`ConcurrencyLimit`][pydantic_ai.ConcurrencyLimit]
- একাধিক মডেলজুড়ে সীমা ভাগ করতে একটি [`ConcurrencyLimiter`][pydantic_ai.ConcurrencyLimiter]

### ভাগ করা সমান্তরালতার সীমা { #shared-concurrency-limits }

একাধিক মডেলজুড়ে একটি সমান্তরালতার সীমা ভাগ করতে (যেমন একই provider-এর ভিন্ন মডেল),
একটি [`ConcurrencyLimiter`][pydantic_ai.ConcurrencyLimiter] তৈরি করে
একাধিক `ConcurrencyLimitedModel` instance-এ দিতে পারেন:

⟦CODE6⟧

একটি এজেন্ট আর তার নিজের মডেল রিকোয়েস্টে ব্যবহৃত `ConcurrencyLimitedModel`-কে আলাদা
`ConcurrencyLimiter` instance ব্যবহার করতে হবে। আপনি `Agent(max_concurrency=...)` আর
`ConcurrencyLimitedModel(limiter=...)` দুটোই সেট করলে, একই instance ব্যবহার করলে
[`UserError`][pydantic_ai.exceptions.UserError] ওঠে।
একটির ভেতরে আরেকটি `ConcurrencyLimitedModel` wrapper-এরও ভিন্ন limiter instance লাগে।

একই task-এ একটি এজেন্টের মধ্য দিয়ে একটি `ConcurrencyLimiter`-এ আবার ঢুকলে `RuntimeError` ওঠে; ভেতরের রানের জন্য একটি আলাদা limiter
ব্যবহার করুন। একটি এজেন্ট একটি টুলের মাধ্যমে আরেকটি এজেন্টকে কাজ দিলে, প্রতিটি রান বা মডেল
রিকোয়েস্ট নিজের slot নেয়। একটি ভাগ করা pool-এর parent আর ভেতরের কাজ একই সময়ে চালানোর মতো
যথেষ্ট ক্ষমতা থাকতে হবে।

Instrumentation চালু থাকলে, একটি সমান্তরালতার slot-এর জন্য অপেক্ষমাণ রিকোয়েস্ট span হিসেবে দেখা দেয়,
সারির গভীরতা আর কনফিগার করা সীমা দেখানো attribute-সহ। `ConcurrencyLimiter`-এর `name` প্যারামিটার
trace-এ ভাগ করা limiter চিনতে সাহায্য করে।

<!-- TODO(Marcelo): We need to create a section in the docs about reliability. -->

## মডেল API-র এরর সামলানো { #handling-model-api-errors }

একটি model provider-এ রিকোয়েস্ট ব্যর্থ হলে, Pydantic AI provider SDK-র নিজের exception না তুলে একটি
[`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] তোলে, আর SDK-রটি `__cause__` হিসেবে পাওয়া যায়।
provider বললে কী ভুল হয়েছে, এররটি এই শ্রেণিগুলোর একটির instance হয়, যে provider থেকেই আসুক:

| Exception | কখন ওঠে |
|---|---|
| [`ModelRateLimitError`][pydantic_ai.exceptions.ModelRateLimitError] | একটি rate limit-এ পৌঁছানো হয়েছে, যেমন একটি HTTP 429। অপেক্ষা করে আবার চেষ্টা করলে কাজ হতে পারে। |
| [`ModelQuotaExceededError`][pydantic_ai.exceptions.ModelQuotaExceededError] | provider বলেছে account-এর quota, credit বা বিলিং শেষ, যেমন একটি HTTP 402 বা OpenAI-এর `insufficient_quota`। অপেক্ষায় লাভ নেই। |
| [`ModelUnavailableError`][pydantic_ai.exceptions.ModelUnavailableError] | provider বা মডেল সাময়িকভাবে অনুপলব্ধ, যেমন একটি HTTP 503 বা provider-এর পাঠানো একটি gRPC `UNAVAILABLE`। |
| [`ModelOverloadedError`][pydantic_ai.exceptions.ModelOverloadedError] | provider বলেছে অতিরিক্ত চাপের কারণে সে অনুপলব্ধ, যেমন একটি HTTP 529 বা Anthropic-এর `overloaded_error`। `ModelUnavailableError`-এর একটি subclass। |
| [`ModelServerError`][pydantic_ai.exceptions.ModelServerError] | provider অন্য একটি সার্ভার এরর দিয়ে ব্যর্থ হয়েছে, যেমন একটি HTTP 500, 502 বা 504। |
| [`ModelConnectionError`][pydantic_ai.exceptions.ModelConnectionError] | রিকোয়েস্ট provider-এ পৌঁছাতে পারেনি, বা এর উত্তর পড়া যায়নি। এর [`phase`][pydantic_ai.exceptions.ModelConnectionError.phase] বলে রিকোয়েস্ট provider-এ পৌঁছে থাকতে পারে কিনা। |
| [`ModelTimeoutError`][pydantic_ai.exceptions.ModelTimeoutError] | একটি প্রচেষ্টা transport স্তরে সময় পেরিয়েছে। `ModelConnectionError`-এর একটি subclass। সব প্রচেষ্টাজুড়ে একটি [`request_timeout`](../timeouts.md#model-request-deadlines) সময়সীমা বদলে [`ModelRequestTimeout`][pydantic_ai.exceptions.ModelRequestTimeout] তোলে। |
| [`ModelRequestRejectedError`][pydantic_ai.exceptions.ModelRequestRejectedError] | provider রিকোয়েস্টটিই প্রত্যাখ্যান করেছে, যেমন একটি HTTP 400 বা 422, তাই অপরিবর্তিত আবার পাঠালে সফল হবে না। |
| [`ModelContextWindowExceededError`][pydantic_ai.exceptions.ModelContextWindowExceededError] | ইনপুট মডেলের context window ছাড়িয়ে গেছে। `ModelRequestRejectedError`-এর একটি subclass। |
| [`ModelAuthenticationError`][pydantic_ai.exceptions.ModelAuthenticationError] | provider credential প্রত্যাখ্যান করেছে, বা সেগুলো দিয়ে রিকোয়েস্টটি করতে দেয় না, যেমন একটি HTTP 401 বা 403। `ModelRequestRejectedError`-এর একটি subclass। |
| [`ModelNotFoundError`][pydantic_ai.exceptions.ModelNotFoundError] | রিকোয়েস্টে নাম দেওয়া মডেল, deployment বা অন্য রিসোর্স provider খুঁজে পায়নি, যেমন একটি HTTP 404। `ModelRequestRejectedError`-এর একটি subclass। |

একই status code ভাগ করা শ্রেণিগুলোর মধ্যে provider-এর নিজের সংকেত সিদ্ধান্ত নেয়: একটি 429 হলো rate limit, যদি না
provider বলে quota শেষ, আর একটি 503 শুধু অনুপলব্ধ, যদি না provider বলে সে অতিরিক্ত চাপে। একটি 400 হলো
একটি `ModelRequestRejectedError`, বা provider কারণ বললে এর একটি subclass: একটি `ModelContextWindowExceededError`,
একটি `ModelNotFoundError` (OpenAI-এর Responses API `model_not_found` একটি 400 হিসেবে পাঠায়), বা একটি `ModelAuthenticationError` (Gemini
API `API_KEY_INVALID` একটি 400 হিসেবে পাঠায়)। শেষ হয়ে যাওয়া credit বদলে একটি `ModelQuotaExceededError`, এমনকি যখন
provider সেগুলো একটি 400 হিসেবে পাঠায়, যেমন Anthropic পাঠায়।

অন্য এরর একটি সাধারণ `ModelAPIError` বা [`ModelHTTPError`](#handling-http-errors) হিসেবে ওঠে, যেমন সবসময় উঠত।
শ্রেণি দেওয়া হয় provider-এর এরর code বা type থেকে যেখানে সে একটি পাঠায়, আর এরর বার্তা থেকে
শুধু যেখানে provider আর কিছুই দেয় না। প্রতিটি `ModelAPIError` উপলব্ধ থাকলে provider-এর
[`provider_error_code`][pydantic_ai.exceptions.ModelAPIError.provider_error_code],
[`provider_error_type`][pydantic_ai.exceptions.ModelAPIError.provider_error_type], আর এররের
[`body`][pydantic_ai.exceptions.ModelAPIError.body]-ও দেয়।

[Embedding মডেল](../embeddings.md#handling-errors) একই এরর তোলে।

একটি এরর একইভাবে জানানো হয়, provider সেটি একটি stream খোলার আগে পাঠাক বা ইতিমধ্যে খোলা একটি
stream-এর ভেতরে। যেমন, Bedrock-এর একটি HTTP 503 আর একটি Bedrock stream-এর একটি `serviceUnavailableException`, দুটোই
status 503-সহ একটি `ModelHTTPError` তোলে যা একটি `ModelUnavailableError`-ও। দ্বিতীয়টিতে
[`in_stream`][pydantic_ai.exceptions.ModelAPIError.in_stream] সেট থাকে, তাই আপনি তবুও সেগুলো আলাদা করতে পারেন।

এতে কোন provider থেকে এসেছে না জেনেই একটি ব্যর্থতা নিয়ে কী করবেন তা ঠিক করতে পারেন:

⟦CODE7⟧

[`retry_after`][pydantic_ai.exceptions.ModelAPIError.retry_after] হলো provider আপনাকে যত সেকেন্ড অপেক্ষা করতে বলেছে,
একটি `float` হিসেবে, বা না বললে `None`।

একটি কথোপকথনকে শুরু থেকেই context window-এর নিচে রাখতে দেখুন [Compaction](../capabilities/compaction.md),
যা `ModelContextWindowExceededError`-এর অপেক্ষার চেয়ে ভালো: মডেলের কর্মক্ষমতা সাধারণত কঠিন সীমার অনেক আগেই
কমে যায়।

শ্রেণিগুলো এমন একটি ব্যর্থতা, যা চলে যেতে পারে, তাকে এমন একটি থেকে আলাদা করে যা চলে যাবে না। আপনি নিজে মডেল রিকোয়েস্ট আবার চেষ্টা করলে,
সেগুলো বাদ দিন যা একই মডেলে একই রিকোয়েস্ট আবার পাঠালে ঠিক হতে পারে না:

⟦CODE8⟧

[`ModelAuthenticationError`][pydantic_ai.exceptions.ModelAuthenticationError],
[`ModelNotFoundError`][pydantic_ai.exceptions.ModelNotFoundError] আর
[`ModelContextWindowExceededError`][pydantic_ai.exceptions.ModelContextWindowExceededError] সবই একটি
`ModelRequestRejectedError`, তাই `should_retry` এগুলোও বাদ দেয়। [Temporal](../durable_execution/temporal.md#activity-retries)-এর অধীনে, activity-কে এগুলো আবার চেষ্টা করা থেকে থামাতে
`non_retryable_model_errors`-এ একই ক্লাসগুলো তালিকা করুন।

/// info | এক নজরে: আবার চেষ্টা করবেন কিনা

| এরর | আবার চেষ্টা? |
| --- | --- |
| `ModelRateLimitError` | হ্যাঁ, `retry_after` অনুযায়ী অপেক্ষা করে |
| `ModelUnavailableError` / `ModelOverloadedError` / `ModelServerError` | হ্যাঁ, কিছু পরে; বা অন্য মডেলে fallback |
| `ModelConnectionError` / `ModelTimeoutError` | সাধারণত হ্যাঁ |
| `ModelQuotaExceededError` | না — টাকা/credit যোগ করুন |
| `ModelRequestRejectedError` (আর এর subclass) | না — রিকোয়েস্ট, key বা মডেলের নাম ঠিক করুন |

///

### HTTP এরর { #handling-http-errors }

একটি provider একটি 4xx বা 5xx উত্তর ফেরত দিলে, এররটি একটি
[`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError], আর ওপরের যে এরর শ্রেণির এটি অন্তর্গত, থাকলে
তারও একটি instance। exception-টি দেয়
[`status_code`][pydantic_ai.exceptions.ModelHTTPError.status_code], উত্তরের
[`body`][pydantic_ai.exceptions.ModelAPIError.body], আর provider-এর
**উত্তরের header** [`headers`][pydantic_ai.exceptions.ModelHTTPError.headers]
attribute দিয়ে (ছোট-হাতের key-সহ একটি `dict[str, str]`, বা header দেয় না এমন provider-এর জন্য
`None`, যেমন gRPC-ভিত্তিক provider)। এর
[`retry_after`][pydantic_ai.exceptions.ModelAPIError.retry_after] পার্স হয় `retry-after-ms` বা
`Retry-After` header থেকে, পূর্ণসংখ্যার delta-seconds আর HTTP-date দুই ফরম্যাটই সামলে, আর
[`provider_retry_hint`][pydantic_ai.exceptions.ModelHTTPError.provider_retry_hint] `x-should-retry` header থেকে,
যা OpenAI আর Anthropic পাঠায় আবার চেষ্টায় কাজ হতে পারে কিনা বলতে।

[OpenAI](openai.md), [Anthropic](anthropic.md), [Google Gemini API](google.md),
[Amazon Bedrock](bedrock.md), বা [Groq](groq.md) যখন জানায় যে চাওয়া একটি মডেল identifier
অনুপলব্ধ, Pydantic AI একটি কাছাকাছি জানা মিল থাকলে এরর বার্তায় তা যোগ করে।
পরামর্শটি [`suggested_model_id`][pydantic_ai.exceptions.ModelHTTPError.suggested_model_id] হিসেবেও পাওয়া যায়। এটি
provider একটি রিকোয়েস্ট প্রত্যাখ্যান করার পরে যথাসাধ্য নির্দেশনা, লোকাল যাচাই নয়: অজানা মডেল
identifier বৈধ থাকে, যাতে নিজের deployment আর নতুন প্রকাশিত মডেল কাজ করতে থাকে।

একটি provider এররের যখন রিকোয়েস্টের বাইরে একটি জানা সমাধান থাকে, যেমন কিছু মডেলের জন্য Amazon Bedrock-এর চাওয়া [data retention](bedrock.md#data-retention)
মোড, Pydantic AI এরর বার্তায় নির্দেশনা যোগ করে। এটি
[`hint`][pydantic_ai.exceptions.ModelHTTPError.hint] হিসেবেও পাওয়া যায়।

/// note | মনে রাখুন

কিছু `ModelHTTPError`-এর নিজস্ব HTTP status থাকে না, আর বদলে একই এররের জন্য provider যে status ব্যবহার করে
তা পায়, তাই সেগুলো একইভাবে সামলানো হয়:

- xAI-এর gRPC status code তাদের HTTP সমতুল্যে ম্যাপ হয়, যেমন `RESOURCE_EXHAUSTED` থেকে 429। এগুলোর
  `headers=None`। client নিজে যে gRPC এরর তোলে, কারণ সংযোগ করতে পারেনি, সংযোগ হারিয়েছে, বা তার
  `timeout`-এ পৌঁছেছে, তা বদলে একটি `ModelConnectionError` বা `ModelTimeoutError`, অন্য provider-এর মতোই।
- একটি 200-OK উত্তর থেকে পার্স করা OpenRouter এরর এররের নিজের `code` জানায়।
- ইতিমধ্যে খোলা একটি stream-এর ভেতরে পাঠানো একটি এরর stream খোলার আগে একই এররের status পায়, যেমন
  Anthropic-এর `overloaded_error`-এর জন্য 529। এগুলোর
  [`in_stream`][pydantic_ai.exceptions.ModelAPIError.in_stream] সেট থাকে, আর এদের `headers`, থাকলে,
  stream-এর।
  একটি রিকোয়েস্ট আপনি না চাইলেও stream হতে পারে (যেমন এজেন্টের একটি event stream handler থাকলে), আর
  সেজন্যই এরর অন্যথায় এর ওপর নির্ভর করে না।

///

একটি [নিজের মডেল](#custom-models) [`ModelHTTPError.for_category`][pydantic_ai.exceptions.ModelHTTPError.for_category] দিয়ে একই এরর তুলতে পারে, যা একটি `ModelHTTPError`
বানায় যা দেওয়া শ্রেণিরও একটি instance, তাই যেকোনোটি সামলানো কোড এটি ধরে। এর ক্লাসের নাম
শ্রেণির নামে, তাই traceback, `repr()`, OpenTelemetry span আর [`failed_attempts`][pydantic_ai.messages.ModelResponse.failed_attempts] এটিকে দেখায়, ধরুন,
`ModelRateLimitError` হিসেবে:

⟦CODE9⟧

## Fallback মডেল { #fallback-model }

একটি সফল না হওয়া পর্যন্ত একাধিক মডেল ক্রমানুসারে চেষ্টা করতে [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] ব্যবহার করতে পারেন।
বর্তমান মডেল একটি exception তুললে (যেমন একটি 4xx/5xx API এরর) **বা** উত্তরের বিষয়বস্তু একটি অর্থগত
ব্যর্থতা নির্দেশ করলে (যেমন একটি কাটা উত্তর বা একটি ব্যর্থ নেটিভ টুল কল) Pydantic AI পরের মডেলে যেতে পারে।

/// tip | উদাহরণ দিয়ে বুঝি

বিদ্যুৎ গেলে জেনারেটর চালু হওয়ার মতো: প্রধান মডেল (ধরুন OpenAI) বন্ধ বা rate limit-এ আটকে থাকলে, `FallbackModel` নিজে থেকে পরের মডেলে (ধরুন Anthropic) চলে যায়, আর ব্যবহারকারী টেরও পান না।

///

ডিফল্টভাবে, fallback ঘটে [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]-এ (4xx/5xx API এরর, আর উত্তর শুরুর আগে
সংযোগ ব্যর্থতা বা timeout), তাই সবচেয়ে সাধারণ ব্যবহারে কিছুই কনফিগার করতে হয় না। এর মধ্যে পড়ে প্রতিটি [এরর শ্রেণি](#handling-model-api-errors): rate limit, শেষ হওয়া quota,
অনুপলব্ধ বা অতিরিক্ত চাপের provider, সার্ভার এরর, সংযোগ ব্যর্থতা আর timeout,
আর প্রত্যাখ্যাত রিকোয়েস্ট, [context window overflow](#context-window-overflow)-সহ: আরেকটি মডেল বা provider
হয়তো এমন রিকোয়েস্ট, credential বা মডেলের নাম গ্রহণ করবে যা প্রথমটি প্রত্যাখ্যান করেছে, আর বড় context window-এর একটি মডেল
হয়তো এমন ইনপুট গ্রহণ করবে যা আরেকটি মডেলে উপচে পড়েছিল। শুধু কয়েকটিতে fallback করতে, সেই শ্রেণিগুলো
`fallback_on` হিসেবে দিন, যেমন `fallback_on=(ModelRateLimitError, ModelUnavailableError, ModelServerError)`।

এই আচরণ নিয়ন্ত্রণ করে `fallback_on` প্যারামিটার (দেখুন
[`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]), যা নেয় exception টাইপ,
exception handler, আর response handler — সবগুলোই sync বা async হতে পারে।

/// note | মনে রাখুন

যে provider SDK-র ওপর Model তৈরি (যেমন OpenAI, Anthropic ইত্যাদি) সেগুলোতে প্রায়ই নিজস্ব retry লজিক থাকে, যা `FallbackModel` সক্রিয় হতে দেরি করাতে পারে।

`FallbackModel` ব্যবহারের সময়, সাথে সাথে fallback নিশ্চিত করতে provider SDK retry বন্ধ রাখার পরামর্শ দেওয়া হয়, এজেন্টে, বা শেষটি ছাড়া প্রতিটি প্রার্থী মডেলে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) `0` সেট করে। Bedrock আর xAI এটি উপেক্ষা করে আর [`UnsupportedSettingWarning`][pydantic_ai.exceptions.UnsupportedSettingWarning] দিয়ে সতর্ক করে, তাই এগুলোর একটি প্রার্থী হলে, অন্য প্রার্থীদের ওপর সেট করুন। পুরো retry মানচিত্রের জন্য retries গাইডের [The layers](../retries.md#the-layers) দেখুন।

বদলে fallback কতক্ষণ দেরি হতে পারে তা সীমিত করতে, মডেল সেটিংয়ে [`request_timeout`](../timeouts.md#model-request-deadlines) সেট করুন: প্রতিটি মডেল তার সব প্রচেষ্টাজুড়ে ততটুকু সময় পায়, আর সময় শেষ হলে ফলস্বরূপ [`ModelRequestTimeout`][pydantic_ai.exceptions.ModelRequestTimeout] পরের মডেলে fallback ঘটায়, যা একটি নতুন সময়সীমা পায়।

///

নিচের উদাহরণে, এজেন্ট প্রথমে OpenAI মডেলে একটি রিকোয়েস্ট করে (যা একটি অবৈধ API key-র কারণে ব্যর্থ হয়),
আর তারপর Anthropic মডেলে fallback করে।

⟦CODE10⟧

ওপরের `ModelResponse` বার্তা `model_name` ফিল্ডে দেখায় যে আউটপুটটি Anthropic মডেল ফেরত দিয়েছে, যা `FallbackModel`-এ দেওয়া দ্বিতীয় মডেল।

/// note | মনে রাখুন

প্রতিটি মডেলের অপশন আলাদাভাবে কনফিগার করা উচিত। যেমন, `base_url`, `api_key` আর নিজের client প্রতিটি মডেলেই সেট করা উচিত, `FallbackModel`-এ নয়।

///

### প্রতি-মডেল সেটিং { #per-model-settings }

প্রতিটি মডেল তৈরির সময় `settings` প্যারামিটার দিয়ে একটি fallback শৃঙ্খলের প্রতিটি মডেলের জন্য ভিন্ন [`ModelSettings`][pydantic_ai.settings.ModelSettings] কনফিগার করতে পারেন। ভিন্ন provider-এর ভিন্ন সর্বোত্তম কনফিগারেশন থাকলে এটি বিশেষভাবে কাজে লাগে:

⟦CODE11⟧

এই উদাহরণে, OpenAI মডেল ব্যর্থ হলে, এজেন্ট নিজে থেকে Anthropic মডেলে তার নিজের কনফিগার করা সেটিংসহ fallback করবে। `FallbackModel`-এর নিজের কোনো সেটিং নেই — যে মডেল সফলভাবে রিকোয়েস্ট সামলায় তার নিজের সেটিং ব্যবহার করে।

### Exception সামলানো { #exception-handling }

পরের উদাহরণটি `FallbackModel`-এর exception সামলানোর ক্ষমতা দেখায়।
সব মডেল ব্যর্থ হলে, একটি [`FallbackExceptionGroup`][pydantic_ai.exceptions.FallbackExceptionGroup] ওঠে, যাতে
`run` চলার সময় পাওয়া সব exception থাকে।

⟦CODE12⟧

ডিফল্টভাবে, বর্তমান মডেল একটি
[`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] তুললেই শুধু `FallbackModel` পরের মডেলে যায়, যার মধ্যে আছে
[`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError]। `FallbackModel` constructor-এ একটি নিজের `fallback_on` আর্গুমেন্ট দিয়ে
এই আচরণ বদলাতে পারেন।

/// note | মনে রাখুন

যাচাইয়ের এরর ([গোছানো আউটপুট](../output.md#structured-output) বা [টুল প্যারামিটার](../tools.md) থেকে) fallback ঘটায় **না**। এই এররগুলো বদলে [retry ব্যবস্থা](../agent.md#reflection-and-self-correction) ব্যবহার করে, যা একই মডেলকে আবার চেষ্টা করতে বলে। এটি ইচ্ছাকৃত: যাচাইয়ের এরর আসে LLM-এর অনির্ধারিত প্রকৃতি থেকে আর আবার চেষ্টায় সফল হতে পারে, অথচ API এরর (4xx/5xx) সাধারণত এমন সমস্যা নির্দেশ করে যা একই রিকোয়েস্ট আবার চেষ্টায় মেটে না।

///

### Context window উপচে পড়া { #context-window-overflow }

একটি মডেল [`ModelContextWindowExceededError`][pydantic_ai.exceptions.ModelContextWindowExceededError] তুললেও `FallbackModel` fallback করে, কারণ শৃঙ্খলের পরের একটি মডেলের
বড় context window থাকতে পারে। পুরো শৃঙ্খল ব্যর্থ হলে, উপচে পড়াটি থাকে
[`FallbackExceptionGroup`][pydantic_ai.exceptions.FallbackExceptionGroup]-এ, যেখানে `except* ModelContextWindowExceededError`
এটিতে পৌঁছায়। আপনার কোনো মডেলের বড় window না থাকলে, `fallback_on` থেকে উপচে পড়া বাদ দিয়ে প্রতিটিতে
অতিরিক্ত বড় রিকোয়েস্ট পাঠানো এড়াতে পারেন, যাতে এটি যেমন আছে তেমন ছড়িয়ে পড়ে:

⟦CODE13⟧

### ব্যর্থ প্রচেষ্টা আর usage { #failed-attempts-and-usage }

যে উত্তরটি সাড়া দেয় তা `FallbackModel` যে প্রতিটি প্রচেষ্টা পেরিয়ে এসেছে সেগুলো [`failed_attempts`][pydantic_ai.messages.ModelResponse.failed_attempts]-এ ক্রমানুসারে তালিকা করে। প্রতিটি [`ModelRequestAttempt`][pydantic_ai.messages.ModelRequestAttempt] রেকর্ড করে কোন মডেল আর provider চেষ্টা হয়েছিল, এটি একটি এরর তুলেছিল কিনা (এররটি `'ExceptionType: message'` হিসেবে) বা এমন একটি উত্তর ফেরত দিয়েছিল যা একটি [response handler](#response-based-fallback) প্রত্যাখ্যান করেছে, কখন শুরু হয়েছিল আর কতক্ষণ নিয়েছে, আর provider এর জন্য যে usage জানিয়েছে। এরর তোলা একটি প্রচেষ্টার কোনো usage নেই, কারণ provider কিছুই জানায়নি। প্রতিটি মডেল ব্যর্থ হলে, একই প্রচেষ্টাগুলো থাকে [`FallbackExceptionGroup`][pydantic_ai.exceptions.FallbackExceptionGroup]-এর `attempts`-এ।

একটি প্রত্যাখ্যাত উত্তর তবুও তৈরি আর বিল হয়েছিল, তাই এর token আর খরচ রানের [`RunUsage`][pydantic_ai.usage.RunUsage]-এ যোগ হয় আর [`UsageLimits`][pydantic_ai.usage.UsageLimits]-এর token আর খরচের সীমায় গোনা হয়। এগুলো সাড়া দেওয়া উত্তরের `usage`-এ মেশানো না হয়ে প্রচেষ্টাতেই থাকে, আর প্রত্যাখ্যাত উত্তর নিজে বার্তার ইতিহাসে যোগ হয় না। একটি fallback প্রচেষ্টা এমন উত্তর নয় যার ওপর এজেন্ট কাজ করেছে, তাই এটি [`request_limit`][pydantic_ai.usage.UsageLimits.request_limit]-এ গোনা হয় না।

প্রতিটি মডেল ব্যর্থ হলেও প্রত্যাখ্যাত উত্তরের usage গোনা হয়। এটি একটি সীমা পেরোলে, `FallbackExceptionGroup`-কে `__cause__` হিসেবে রেখে [`UsageLimitExceeded`][pydantic_ai.exceptions.UsageLimitExceeded] ওঠে।

/// note | মনে রাখুন

প্রত্যাখ্যাত উত্তরের usage রেকর্ড হয় না যখন পরের একটি মডেল এমন একটি এরর তোলে যা `fallback_on` ঢাকে না, বা, [Temporal](../durable_execution/temporal.md)-এর অধীনে, যখন প্রতিটি মডেল ব্যর্থ হয়: exception group তার প্রচেষ্টা ছাড়াই workflow-এ পৌঁছায়।

///

⟦CODE14⟧

এজেন্ট [instrument করা](../logfire.md) থাকলে, মডেল রিকোয়েস্টের (`chat`) span সাড়া দেওয়া মডেলটি বর্ণনা করে আর OK দিয়ে শেষ হয়। `FallbackModel` যে প্রতিটি প্রচেষ্টা পেরিয়ে এসেছে তা নিজের child span পায়, `model request attempt <model name>`, যা একটি ERROR status দিয়ে শেষ হয়, যেভাবে একটি সফল এজেন্ট রানের ভেতরে একটি ব্যর্থ টুল কল নিজের span পায়। একটি এরর সেই span-এ একটি exception হিসেবে রেকর্ড হয়, আর একটি [response handler](#response-based-fallback)-এর প্রত্যাখ্যাত একটি উত্তর বদলে তার usage, খরচ আর finish reason বহন করে, যেমন একটি `chat` span করত। প্রতিটি প্রচেষ্টার span তার চেষ্টা করা মডেলের নাম `gen_ai.provider.name` আর `gen_ai.request.model` attribute-এ দেয়, আর রিকোয়েস্টের প্রচেষ্টাগুলোর মধ্যে তার শূন্য-ভিত্তিক অবস্থান `pydantic_ai.model_request.attempt`-এ। [`include_content=False`](../logfire.md#excluding-prompts-and-completions)-এ, exception শুধু তার টাইপ রাখে। প্রচেষ্টার span তৈরি হয় প্রচেষ্টা ব্যর্থ হওয়ার পরে, তাই চেষ্টা করা মডেল নিজে যে span খোলে, যেমন একটি [decision model](decision.md)-এর `decide` span, সেগুলো এর ভেতরে নয়, `chat` span-এর নিচে এর পাশে বসে।

### উত্তর-ভিত্তিক fallback { #response-based-fallback }

exception-ভিত্তিক fallback ছাড়াও, একটি মডেলের উত্তরের **বিষয়বস্তু**-র ভিত্তিতেও fallback ঘটাতে পারেন। এটি কাজে লাগে যখন একটি মডেল একটি সফল HTTP উত্তর ফেরত দেয় (কোনো exception নেই), কিন্তু উত্তরের বিষয়বস্তু একটি অর্থগত ব্যর্থতা নির্দেশ করে — যেমন একটি অপ্রত্যাশিত finish reason বা একটি নেটিভ টুলের ব্যর্থতা জানানো।

/// note | শুধু stream নয় এমন রিকোয়েস্টে

উত্তর-ভিত্তিক fallback শুধু stream নয় এমন রিকোয়েস্টে কাজ করে। একটি stream করা উত্তর বিচার করার মতো সময় হওয়ার আগেই আপনার কাছে পৌঁছে গেছে, তাই এতে response handler প্রয়োগ হয় না: এটি যেমন আছে তেমন গৃহীত হয়, আর একটি `UserWarning` দেওয়া হয়। stream তার প্রথম event তৈরি না করা পর্যন্ত exception-ভিত্তিক fallback তবুও প্রযোজ্য, কোনো আউটপুটের আগে একটি provider stream-এ যে এরর জানায় সেগুলোসহ, যেমন রিকোয়েস্ট গৃহীত হওয়ার পরে একটি overload। এর পরের একটি এরর আপনার কাছে পৌঁছায়, কারণ আউটপুট ইতিমধ্যে stream হয়ে গেছে।

একটি রিকোয়েস্ট stream হয় যখনই কিছু রানের event খরচ করে: [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream], [`agent.run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] (যা [UI adapter-গুলো](../ui/overview.md) ব্যবহার করে), `node.stream()`-সহ [`agent.iter()`][pydantic_ai.agent.Agent.iter], আর একটি `event_stream_handler`, একটি [`agent.on_event`][pydantic_ai.agent.Agent.on_event] listener, বা event-এ সাড়া দেওয়া একটি capability, যেমন [event stream hooks](../hooks.md#event-stream-hooks)-সহ [`agent.run()`][pydantic_ai.agent.AbstractAgent.run] বা [`agent.run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync]।

///

`fallback_on` প্যারামিটার নেয়:

- exception টাইপের একটি tuple: `(ModelAPIError, ModelHTTPError)`
- একটি exception handler (sync বা async): `lambda exc: isinstance(exc, MyError)`
- একটি response handler (sync বা async): `def check(r: ModelResponse) -> bool`
- ওপরের সবগুলো মেশানো একটি তালিকা: `[ModelAPIError, exc_handler, response_handler]`

Handler-এর টাইপ নিজে থেকে চেনা হয় প্রথম প্যারামিটারের type hint দেখে। প্রথম প্যারামিটারের hint [`ModelResponse`][pydantic_ai.messages.ModelResponse] হলে, এটি একটি response handler। অন্যথায় (টাইপহীন handler আর lambda-সহ), এটি একটি exception handler।

যেহেতু hint চলার সময় নির্ধারিত হয়, handler-এর signature-এর প্রতিটি annotate করা টাইপ শুধু `if TYPE_CHECKING:`-এর নিচে নয়, চলার সময়ে import করা থাকতে হবে। কোনো annotation নির্ধারিত না হলে, handler-কে নিঃশব্দে একটি exception handler ধরার বদলে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

#### Finish reason-এর উদাহরণ { #finish-reason-example }

একটি সহজ ব্যবহার হলো মডেলের finish reason পরীক্ষা করা — যেমন, দৈর্ঘ্যের সীমার কারণে উত্তর কাটা পড়লে fallback করা:

⟦CODE15⟧

/// warning | একা response handler ডিফল্ট exception fallback বদলে দেয়

`fallback_on` হিসেবে একটি একক response handler দিলে (ওপরের মতো), এটি ডিফল্ট `(ModelAPIError,)` exception fallback পুরোপুরি **বদলে দেয়**। অর্থাৎ API এরর (4xx/5xx) পরের মডেলে fallback না ঘটিয়ে exception হিসেবে ছড়িয়ে পড়বে।

একটি response handler-এর পাশাপাশি exception-ভিত্তিক fallback রাখতে, সেগুলো একসাথে একটি তালিকা হিসেবে দিন — দেখুন [নিচের মেশানো উদাহরণ](#combining-handlers)।

///

/// note | মনে রাখুন

[এজেন্ট loop](../agent.md) একটি finish reason-এর ওপর কাজ করে শুধু যখন উত্তরে কাজে লাগানোর মতো
কোনো আউটপুট নেই। একটি খালি বা শুধু-thinking উত্তরে একটি `'length'` finish reason
[`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] তোলে (সাধারণত মডেল thinking-এর মাঝে
token সীমায় পৌঁছেছে), আর একটি `'content_filter'` finish reason-সহ একটি খালি বা শুধু-thinking উত্তর
[`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] তোলে। অন্য খালি বা শুধু-thinking
উত্তর আবার জিজ্ঞেস করা হয়, আউটপুট retry সীমা পর্যন্ত। খালি নয় এমন উত্তর finish reason যা-ই হোক স্বাভাবিকভাবে
সামলানো হয় — আর্গুমেন্টের মাঝে কাটা একটি টুল কল অন্য যেকোনো
অবৈধ-আর্গুমেন্ট ব্যর্থতার মতো আবার জিজ্ঞেস করা হয়, আর শুধু এর retry বাজেট শেষ হলেই এটি
[`IncompleteToolCall`][pydantic_ai.exceptions.IncompleteToolCall] (`UnexpectedModelBehavior`-এর একটি
subclass) হিসেবে দেখা দেয়।

এগুলো সবই এজেন্ট loop থেকে ওঠে, `model.request()` সফলভাবে ফেরত আসার পরে,
তাই কোনো exception-ভিত্তিক `fallback_on` এগুলো ধরতে পারে না — ডিফল্ট
`fallback_on=(ModelAPIError,)` নয় (যা এমনিতেও মিলত না, কারণ `ContentFilterError`
[`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] নয়, `UnexpectedModelBehavior` থেকে উত্তরাধিকারসূত্রে আসে), আর একটি
স্পষ্ট `fallback_on=(ContentFilterError,)`-ও নয়। বদলে একটি খারাপ finish reason-এ fallback করতে,
এমন একটি response handler ব্যবহার করুন (দেখুন [ওপরের উদাহরণ](#finish-reason-example)) যা
[`finish_reason`][pydantic_ai.messages.ModelResponse.finish_reason] দেখে: এটি এজেন্ট loop দেখার আগেই
`FallbackModel`-এর ভেতরে উত্তরটি প্রত্যাখ্যান করে, তাই একটি exception তোলার বদলে পরের মডেল চেষ্টা হয়।
মনে রাখবেন এটি সেই finish reason-সহ *প্রতিটি* উত্তর প্রত্যাখ্যান করে, এজেন্ট loop গ্রহণ করত এমন খালি নয়
এমনগুলোসহ। বদলে আংশিক বা প্রত্যাখ্যানের লেখা তখনো বহন করা `content_filter` উত্তরে এরর তুলতে,
[`RaiseContentFilterError`][pydantic_ai.capabilities.RaiseContentFilterError] capability যোগ করুন।

///

#### নেটিভ টুল ব্যর্থতার উদাহরণ { #native-tool-failure-example }

একটি আরও জটিল ব্যবহার হলো web search বা URL fetch-এর মতো নেটিভ টুল ব্যবহারের সময়। যেমন, Google-এর [`WebFetchTool`][pydantic_ai.native_tools.WebFetchTool] একটি সফল উত্তর ফেরত দিতে পারে, যার status বলে URL fetch ব্যর্থ হয়েছে:

⟦CODE16⟧

Response handler মডেলের ফেরত দেওয়া [`ModelResponse`][pydantic_ai.messages.ModelResponse] পায় আর পরের মডেলে fallback ঘটাতে `True`, বা উত্তরটি গ্রহণ করতে `False` ফেরত দেওয়া উচিত।

#### কাজে লাগানোর মতো আউটপুট ছাড়া উত্তর প্রত্যাখ্যান { #rejecting-responses-without-actionable-output }

Handler ছাড়া, একটি খালি বা শুধু-thinking উত্তর একই মডেলে আবার জিজ্ঞেস করা হয়, আউটপুট retry সীমা পর্যন্ত (ওপরের নোট দেখুন)। একটি response handler বদলে এটিকে backup মডেলে পাঠাতে পারে, কোনো লেখা বা টুল কল নেই এমন একটি সফল উত্তর প্রত্যাখ্যান করে। এই শর্তটি একটি লেখা-আউটপুটের এজেন্টের জন্য; আপনার আউটপুট টাইপ অন্য উত্তর-অংশ গ্রহণ করলে, শর্তে সেই অংশগুলোও রাখুন। handler তালিকায় [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] রাখুন যাতে API এররও fallback করে; দেখুন [Combining Handlers](#combining-handlers)।

⟦CODE17⟧

#### Handler মেলানো { #combining-handlers }

একটি একক তালিকায় exception টাইপ, exception handler আর response handler মেলাতে পারেন:

⟦CODE18⟧

### Middleware আর decorator-এ exception সামলানো { #exception-handling-in-middleware-and-decorators }

`FallbackModel` ব্যবহারের সময়, বোঝা জরুরি যে [`FallbackExceptionGroup`][pydantic_ai.exceptions.FallbackExceptionGroup]
Python-এর [`ExceptionGroup`](https://docs.python.org/3/library/exceptions.html#ExceptionGroup) থেকে উত্তরাধিকারসূত্রে আসে। অর্থাৎ
নির্দিষ্ট exception (যেমন `ModelAPIError`) ধরা বিদ্যমান exception-সামলানো কোড group-এর ভেতরে মোড়া
আলাদা exception-গুলো নিজে থেকে ধরবে না।

যেমন, আপনার যদি এমন middleware বা decorator থাকে যা `ModelAPIError` ধরে:

⟦CODE19⟧

`FallbackModel` ব্যবহারের সময় এই decorator `ModelAPIError` exception ধরতে পারবে না, কারণ সেগুলো একটি
`FallbackExceptionGroup`-এ মোড়া, যাতে প্রতিটি ব্যর্থ মডেলের জন্য একটি exception থাকে, মডেলগুলো যে ক্রমে চেষ্টা হয়েছে সেই ক্রমে।

দুটো ক্ষেত্রই সামলাতে, Python 3.11+-এর `except*` syntax ব্যবহার করতে পারেন, যা exception group থেকে মেলা
exception আর সাধারণ exception দুটোই ধরে। মনে রাখবেন `except*` সবসময় ধরা exception একটি
`ExceptionGroup` হিসেবে দেয় (মূলটি সাধারণ exception হলেও), তাই আবার তুললে একটি `ExceptionGroup` ছড়াবে,
মূল exception টাইপ নয়:

⟦CODE20⟧

বিশেষভাবে সামলাতে চাইলে সরাসরি `FallbackExceptionGroup`-ও ধরতে পারেন:

⟦CODE21⟧

/// check | সংক্ষেপে মনে রাখুন

* `Agent('provider:model')` নিজে মডেল ক্লাস, provider আর profile বাছে; ভিন্ন endpoint বা auth-এ মডেল ক্লাসে `provider=` দিন।
* `model.profile.get('supports_tools')` ইত্যাদি দিয়ে সক্ষমতা দেখুন; `model.context_window` সর্বোচ্চ token।
* দীর্ঘজীবী সার্ভিসে `async with agent:` দিয়ে HTTP সংযোগ আবার ব্যবহার করুন; নিজের দেওয়া client নিজেই বন্ধ করুন।
* এরর শ্রেণি (`ModelRateLimitError`, `ModelRequestRejectedError`...) দিয়ে ঠিক করুন আবার চেষ্টা করবেন কিনা।
* `FallbackModel(m1, m2)` একটি ব্যর্থ হলে পরেরটিতে যায়; SDK retry বন্ধ রাখুন (`max_retries=0`); সব ব্যর্থ হলে `FallbackExceptionGroup` — `except*` দিয়ে ধরুন।

///
