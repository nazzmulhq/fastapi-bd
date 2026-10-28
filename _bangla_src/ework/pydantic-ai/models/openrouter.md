# OpenRouter { #openrouter }

/// note | এই পেজে যা শিখবেন

* একটি key দিয়ে অনেক provider-এর মডেলে পৌঁছাতে `OpenRouterModel` ব্যবহার।
* App attribution, মডেল সেটিং, জোর করে টুল বাছাই।
* Prompt caching (Anthropic, Gemini, OpenAI GPT-5.6) আর web search।

///

/// tip | উদাহরণ দিয়ে বুঝি

OpenRouter হলো একটি মাল্টিপ্লাগ: একটি সকেটে (একটি API key) লাগিয়ে বিভিন্ন কোম্পানির যন্ত্র (OpenAI, Anthropic, Google, Meta...) চালানো যায়। মডেলের নাম লেখা হয় `কোম্পানি/মডেল` আকারে, যেমন `anthropic/claude-sonnet-5`।

///

## ইনস্টল { #install }

`OpenRouterModel` ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openrouter` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[openrouter]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[openrouter]"
```

///


## কনফিগারেশন { #configuration }

[OpenRouter](https://openrouter.ai) ব্যবহার করতে, প্রথমে [openrouter.ai/keys](https://openrouter.ai/keys)-এ একটি API key তৈরি করুন।

`OPENROUTER_API_KEY` environment variable সেট করে নাম দিয়ে [`OpenRouterProvider`][pydantic_ai.providers.openrouter.OpenRouterProvider] ব্যবহার করতে পারেন:

⟦CODE1⟧

অথবা সরাসরি মডেল আর provider তৈরি করুন:

⟦CODE2⟧

## App attribution { #app-attribution }

তাদের সর্বজনীন র‍্যাঙ্কিং আর বিশ্লেষণে আপনার অ্যাপ্লিকেশন ট্র্যাক করতে OpenRouter-এর একটি [app attribution](https://openrouter.ai/docs/app-attribution) সুবিধা আছে।

app attribution চালু করতে provider তৈরির সময় একটি `app_url` আর `app_title` দিতে পারেন। বাদ দিলে দুটোই `OPENROUTER_APP_URL` আর `OPENROUTER_APP_TITLE` environment variable-এ ফিরে যায়।

/// note | মনে রাখুন

environment-এর বিকল্প শুধু provider নিজে যে client বানায় সেগুলোতে প্রযোজ্য। আপনি নিজের
`openai_client` দিলে, তা যেমন আছে তেমন আবার ব্যবহার হয়, তাই সেই client-এ সরাসরি `HTTP-Referer` আর `X-Title` header
সেট করুন।

///

⟦CODE3⟧

## মডেল সেটিং { #model-settings }

[`OpenRouterModelSettings`][pydantic_ai.models.openrouter.OpenRouterModelSettings] দিয়ে মডেলের আচরণ নিজের মতো করতে পারেন:

⟦CODE4⟧

### Eager input streaming { #eager-input-streaming }

OpenRouter দিয়ে Anthropic মডেলে, বড় ইনপুটের টুল কলে দেরি কমাতে eager input streaming চালু করতে পারেন।
[`AnthropicModelSettings`][pydantic_ai.models.anthropic.AnthropicModelSettings]-এ [`anthropic_eager_input_streaming`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_eager_input_streaming] সেট করুন:

⟦CODE5⟧

## জোর করে টুল বাছাই { #forced-tool-choice }

Claude একটি বাধ্য [`tool_choice`][pydantic_ai.settings.ModelSettings.tool_choice]-এর উত্তর thinking ছাড়া দেয়, তাই `anthropic/` মডেলে Pydantic AI [সরাসরি Anthropic API-র নিয়ম](anthropic.md#forced-tool-choice) মানে: রিকোয়েস্ট thinking করার সময়, Pydantic AI আপনার হয়ে নির্ধারণ করা একটি `required` বাছাই (যেমন একটি [আউটপুট টুল](../output.md#tool-output) থেকে) `'auto'`-তে ফিরে যায়, আর একটি সাধারণ গোছানো `output_type` [Native Output](../output.md#native-output) ব্যবহার করে। এর মধ্যে পড়ে ডিফল্টভাবে thinking করা মডেলে thinking সেটিং ছাড়া রিকোয়েস্টও, যেমন `anthropic/claude-opus-5`।

একটি `anthropic/` মডেলে স্পষ্টভাবে thinking চাইলে, একটি স্পষ্ট `tool_choice='required'` (বা টুলের নামের একটি তালিকা)-ও একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে, যেখানে সরাসরি API এটি পাঠাত: OpenRouter সেই মিশ্রণ প্রত্যাখ্যান করে না, কিন্তু রিকোয়েস্ট থেকে নিঃশব্দে `reasoning` ফিল্ড বাদ দেয়, তাই উত্তর কোনো thinking ছাড়াই ফিরত। thinking বন্ধ করুন বা বদলে `tool_choice='auto'` ব্যবহার করুন।

নির্ধারিত একটি বাছাই একটি একক টুলের নাম দিলে, `tool_choice` `'auto'` থাকা অবস্থায় উপলব্ধ টুলের তালিকা সেই টুলে ছাঁটা হয়। তাই মডেল এটি না ডেকে লেখায় উত্তর দিতে পারে; একটি আউটপুট টুল বাধ্যতামূলক হলে, Pydantic AI একটি টুল ডাকার prompt দিয়ে আবার চেষ্টা করে।

## Prompt caching { #prompt-caching }

যে downstream provider বাস্তবায়ন করে সেগুলোর জন্য OpenRouter [prompt caching](https://openrouter.ai/docs/guides/best-practices/prompt-caching) সমর্থন করে।

এটি চালুর provider-নিরপেক্ষ উপায় হলো একীভূত [`ModelSettings.cache`][pydantic_ai.settings.ModelSettings.cache] সেটিং (বা [`Caching`][pydantic_ai.capabilities.Caching] capability): Anthropic আর Gemini downstream মডেলে, `cache=True` নিচের `openrouter_cache_instructions`, `openrouter_cache_tool_definitions` আর `openrouter_cache_messages`-এর সমতুল্য (Gemini কোনো TTL নেয় না, তাই চাওয়া ধরে রাখার সময় তার ডিফল্টে cache করে)। খরচের ভারসাম্যের জন্য দেখুন [Caching](../capabilities/caching.md)। provider-নির্দিষ্ট `openrouter_cache_*` সেটিং কোনোটি সেট থাকলে অগ্রাধিকার পায়।

Pydantic AI-এর OpenRouter cache সেটিং Anthropic আর Gemini মডেলের জন্য স্পষ্ট `cache_control` breakpoint নিয়ন্ত্রণ করে:

1. **System নির্দেশনা cache করুন**: [`OpenRouterModelSettings.openrouter_cache_instructions`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_instructions] `True` সেট করুন বা সরাসরি `'5m'` / `'1h'` দিন
2. **শেষ বার্তা cache করুন**: কথোপকথনের শেষ বার্তা নিজে থেকে cache করতে [`OpenRouterModelSettings.openrouter_cache_messages`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_messages] `True` সেট করুন
3. **টুলের সংজ্ঞা cache করুন**: [`OpenRouterModelSettings.openrouter_cache_tool_definitions`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_tool_definitions] `True` সেট করুন বা সরাসরি `'5m'` / `'1h'` দিন
4. **[`CachePoint`][pydantic_ai.messages.CachePoint] দিয়ে সূক্ষ্ম নিয়ন্ত্রণ**: আগের সবকিছু cache করতে user বার্তায় একটি `CachePoint` চিহ্ন বসান

/// note | Provider-এর পার্থক্য

- **Anthropic** মডেল system নির্দেশনা আর বার্তার বিষয়বস্তু দুটোতেই prefix-ভিত্তিক caching সমর্থন করে। TTL মান (`'5m'`, `'1h'`) provider-এ পাঠানো হয়।
- **Gemini** মডেল system নির্দেশনা আর সাধারণ বার্তার বিষয়বস্তুতে caching সমর্থন করে, কিন্তু [OpenRouter Gemini caching-এর জন্য সাধারণ বার্তার বিষয়বস্তু-জুড়ে শুধু শেষ breakpoint ব্যবহার করে](https://openrouter.ai/docs/guides/best-practices/prompt-caching#how-gemini-prompt-caching-works-on-openrouter)।
  সেই চূড়ান্ত বার্তা-সীমানা ইচ্ছাকৃত হলে `openrouter_cache_messages` বা [`CachePoint`][pydantic_ai.messages.CachePoint] ব্যবহার করুন; `openrouter_cache_instructions` শুধু পুরোপুরি স্থির system প্রসঙ্গের জন্য ব্যবহার করুন। Gemini TTL মান উপেক্ষা করে।
  cache করা Gemini `systemInstruction` বিষয়বস্তু অপরিবর্তনীয়, তাই গতিশীল prompt অংশ cache করা system নির্দেশনার পরে না রেখে পরের একটি user বার্তায় রাখুন।
- **OpenAI GPT-5.6** মডেল `cache_control` নয়, OpenAI-এর `prompt_cache_options` আর `prompt_cache_breakpoint` প্রোটোকল ব্যবহার করে। দেখুন নিচের [OpenAI GPT-5.6 explicit caching](#openai-gpt-56-explicit-caching)।
- **ন্যূনতম token সীমা** প্রযোজ্য; বর্তমান provider-নির্দিষ্ট মানের জন্য OpenRouter-এর [minimum token requirements](https://openrouter.ai/docs/guides/best-practices/prompt-caching#minimum-token-requirements) দেখুন।

///

### OpenAI GPT-5.6-এর স্পষ্ট caching { #openai-gpt-56-explicit-caching }

[`OpenRouterModel`][pydantic_ai.models.openrouter.OpenRouterModel] বর্তমানে [`CachePoint`][pydantic_ai.messages.CachePoint]-কে OpenAI-এর breakpoint প্রোটোকলে অনুবাদ করে না (OpenRouter-এ OpenAI মডেল তবুও স্বয়ংক্রিয় caching পায়)। স্পষ্ট GPT-5.6 breakpoint-এর জন্য, [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] (বা [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel])-কে [`OpenRouterProvider`][pydantic_ai.providers.openrouter.OpenRouterProvider]-এর সাথে মেলান:

⟦CODE6⟧

OpenRouter Responses API OpenAI-এর মতো একই রিকোয়েস্ট-জুড়ে TTL আর usage ফিল্ড ব্যবহার করে। downstream provider-কে `openai`-তে সীমিত রাখলে স্পষ্ট-cache রিকোয়েস্ট এমন endpoint-এ যাওয়া এড়ানো যায় যেখানে এই ফিল্ড নথিভুক্ত নয়। OpenRouter বর্তমানে স্পষ্ট breakpoint শুধু লেখার ব্লকে নথিভুক্ত করে, তাই `CachePoint` চিহ্ন লেখার বিষয়বস্তুর পরে বসান।

### মডেল সেটিং দিয়ে caching { #caching-via-model-settings }

system নির্দেশনা, কথোপকথনের শেষ বার্তা আর টুলের সংজ্ঞার জন্য স্পষ্ট caching চালু করতে [`OpenRouterModelSettings`][pydantic_ai.models.openrouter.OpenRouterModelSettings] ব্যবহার করুন:

⟦CODE7⟧

প্রতিটি সেটিং `True` বা একটি স্পষ্ট `'5m'` / `'1h'` TTL মান নেয়। `True` Anthropic মডেলের জন্য Anthropic-এর ডিফল্ট `'5m'` TTL পাঠায়; Gemini TTL মান উপেক্ষা করে আর নিজে cache-এর আয়ু সামলায়। এক-ঘণ্টার breakpoint একটি পাঁচ-মিনিটেরটির পরে এলে Anthropic রিকোয়েস্ট প্রত্যাখ্যান করে (এটি আগে টুল, তারপর system নির্দেশনা, তারপর বার্তা প্রক্রিয়া করে), তাই একটি Anthropic মডেলে এক-ঘণ্টার breakpoint পাঁচ-মিনিটেরগুলোর পরে এলে, সেই আগের breakpoint-গুলো এক ঘণ্টায় তোলা হয়। প্রথম লেখায় `result.usage.cache_write_tokens` আর পুনর্ব্যবহারে `result.usage.cache_read_tokens` দেখুন, `message_history=result.all_messages()`-সহ পরের কলসহ।

cache-এর স্থানিকতা বাড়াতে prompt-cache করা রিকোয়েস্টের পরে OpenRouter [provider sticky routing](https://openrouter.ai/docs/guides/best-practices/prompt-caching#provider-sticky-routing) ব্যবহার করে। কড়া provider নিয়ন্ত্রণ বা বন্ধ fallback চায় এমন cache-সংবেদনশীল কাজের প্রবাহের জন্য, [`openrouter_provider`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_provider]-ও সেট করুন, যেমন `{'order': ['anthropic'], 'allow_fallbacks': False}` দিয়ে।

### CachePoint দিয়ে সূক্ষ্ম নিয়ন্ত্রণ { #fine-grained-control-with-cachepoint }

cache সীমানা ঠিক কোথায় বসবে তা নিয়ন্ত্রণ করতে [`CachePoint`][pydantic_ai.messages.CachePoint] চিহ্ন ব্যবহার করুন:

⟦CODE8⟧

prompt তালিকাটি `agent.run_sync(prompt)`-এ দিন। `CachePoint()` চিহ্নের আগের সবকিছু cache হয়। cache সীমানার ওপর সূক্ষ্ম নিয়ন্ত্রণের জন্য একাধিক চিহ্ন বসাতে পারেন।

একটি user বার্তা খোলা একটি `CachePoint` বদলে আগের user বার্তার শেষ চিহ্নিত করে, সেখানে আগে থেকে থাকা দীর্ঘতর TTL রেখে। Anthropic, Bedrock আর OpenAI-এর মতো নয়, মাঝের একটি টুল ফল এটি বহন করে না, কারণ OpenRouter টুল ফলে `cache_control` নথিভুক্ত করে না; আগের কোনো user বার্তা না থাকলে breakpoint বাদ পড়ে। যার আগে শুধু system নির্দেশনা (বা কিছুই নেই), বা যার বার্তায় পরে কিছুই নেই, তা একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

/// warning | Anthropic cache-breakpoint-এর ক্রম

Anthropic একটি নির্দিষ্ট ক্রমে cache breakpoint প্রক্রিয়া করে — টুলের সংজ্ঞা, তারপর system নির্দেশনা, তারপর বার্তা — আর সেই ক্রমে একটি `'5m'`-এর *পরে* আসা একটি `'1h'` breakpoint প্রত্যাখ্যান করে। একটি Anthropic মডেলে `CachePoint` চিহ্ন বা cache সেটিং-জুড়ে TTL মেশালে, দীর্ঘতর (`'1h'`) breakpoint ছোটগুলোর (`'5m'`) আগে বসান। Anthropic প্রতি রিকোয়েস্টে সর্বোচ্চ চারটি স্পষ্ট breakpoint অনুমোদন করে; বাড়তি breakpoint রিকোয়েস্ট পাঠানোর আগে বাদ পড়ে (সবচেয়ে পুরনো আগে)।

///

## Web search { #web-search }

OpenRouter তার [Beta server tool](https://openrouter.ai/docs/guides/features/server-tools/web-search) দিয়ে web search সমর্থন করে। [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] দিয়ে এটি চালু করুন। মডেল ঠিক করে সার্চ করবে কিনা, আর একটি রিকোয়েস্টে শূন্য বা একাধিক সার্চ করতে পারে।

Pydantic AI v2.30.0-এর আগে, [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] OpenRouter-এর `web` plugin চালু করত, যা প্রতিটি রিকোয়েস্টে সার্চ করত আর প্রতিটির জন্য একটি নির্দিষ্ট ফি বিল করত, প্রশ্নের ওয়েব দরকার থাকুক বা না থাকুক। সেই সবসময়-চালু grounding চাইলে, OpenRouter-এর plugin deprecated হলেও নিজে দিয়ে তবুও পৌঁছানো যায়:

⟦CODE9⟧

### Web search-এর প্যারামিটার { #web-search-parameters }

[`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] দিয়ে সার্চের প্রসঙ্গ, ব্যবহারকারীর আনুমানিক অবস্থান, domain ফিল্টার আর সার্চের একটি সীমা কনফিগার করতে পারেন:

⟦CODE10⟧

Pydantic AI প্রতি-রিকোয়েস্টের web-search সংখ্যা দেখায় [`ModelResponse.provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এর `['server_tool_use']['web_search_requests']`-এ।

### সার্চের উৎস { #search-sources }

OpenRouter যখন downstream provider-এর নিজের সার্চে না দিয়ে নিজে সার্চ চালায়, তখন সে যে উৎস ব্যবহার করেছে তা বার্তায় `url_citation` annotation হিসেবে জুড়ে দেয়। Pydantic AI সেগুলো হুবহু দেখায় [`ModelResponse.provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এর `['annotations']`-এ, প্রতিটি ফলের `url`, `title` আর মডেলকে দেওয়া উদ্ধৃতিসহ:

⟦CODE11⟧

/// note | শুধু নিজস্ব-নয় এমন সার্চ তার উৎস জানায়

যে মডেলের downstream provider নিজস্বভাবে সার্চ চালায় — তাদের মধ্যে OpenAI আর Anthropic — সেগুলো কোনো annotation-ই ফেরত দেয় না, তাই সেগুলোর `provider_details`-এ কোনো `annotations` এন্ট্রি থাকে না। সাধারণ OpenRouter provider details পাওয়া যায়। OpenRouter কোন engine বাছে তা বর্তমানে Pydantic AI থেকে কনফিগার করা যায় না।

///

/// note | Engine-নির্দিষ্ট প্যারামিটার

একটি রেকর্ড করা রিকোয়েস্ট শুধু যাচাই করে যে OpenRouter এই প্যারামিটারের নাম গ্রহণ করে। নিচের প্রতি-engine প্রভাব এসেছে OpenRouter-এর [Beta server-tool ডকুমেন্টেশন](https://openrouter.ai/docs/guides/features/server-tools/web-search) থেকে, এই প্রজেক্টে রেকর্ড করা উত্তর থেকে নয়: নিজস্ব provider সার্চ `search_context_size` উপেক্ষা করে; `user_location` শুধু নিজস্ব সার্চে কাজ করে; আর domain-ফিল্টারের সমর্থন আলাদা (নিজস্ব OpenAI `excluded_domains` উপেক্ষা করে)। মডেলের কাছে উপলব্ধ থাকলে server tool শূন্য বা কয়েকটি সার্চ করতে পারে। OpenRouter একটি নিজস্ব-নয় এমন সার্চ engine বা Anthropic-এর নিজস্ব সার্চ ব্যবহার করলে `max_uses` একটি রিকোয়েস্ট সীমিত করে; অন্য নিজস্ব provider, এই উদাহরণের OpenAI মডেলসহ, এটি উপেক্ষা করে। OpenRouter [`WebSearchTool.external_web_access`][pydantic_ai.native_tools.WebSearchTool.external_web_access] সমর্থন করে না।

///

/// check | সংক্ষেপে মনে রাখুন

* `OPENROUTER_API_KEY` সেট, তারপর `Agent('openrouter:anthropic/claude-sonnet-5')`-এর মতো `কোম্পানি/মডেল` নাম।
* Caching: `cache=True` বা `openrouter_cache_*`; GPT-5.6-এর স্পষ্ট breakpoint-এ `OpenAIResponsesModel` + `OpenRouterProvider`।
* `WebSearchTool` দিয়ে web search; Anthropic মডেলে thinking আর `tool_choice='required'` একসাথে নয়।

///
