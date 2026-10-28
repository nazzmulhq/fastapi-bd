# xAI { #xai }

/// note | এই পেজে যা শিখবেন

* Grok মডেল `XaiModel` দিয়ে ব্যবহার: ইনস্টল, API key, provider, নিজের host/timeout/client।
* cache sticky routing, gRPC retry, ছবি তৈরি আর moderation।
* X Search, ফাইল সংযুক্তি, reasoning effort, server-side loop-এর সীমা, multi-agent মডেল।

///

## ইনস্টল { #install }

[`XaiModel`][pydantic_ai.models.xai.XaiModel] ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `xai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[xai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[xai]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [xAI](https://x.ai/api)-এর মডেল ব্যবহার করতে, একটি API key তৈরি করতে [console.x.ai](https://console.x.ai/team/default/api-keys)-এ যান।

[docs.x.ai](https://docs.x.ai/developers/models)-এ উপলব্ধ xAI মডেলের একটি তালিকা আছে।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export XAI_API_KEY='your-api-key'
```

তারপর নাম দিয়ে [`XaiModel`][pydantic_ai.models.xai.XaiModel] ব্যবহার করতে পারেন:

⟦CODE1⟧

/// tip | পরামর্শ

কণ্ঠের এজেন্টের জন্য, বদলে একটি [realtime session](../realtime/xai.md)-সহ Grok Voice ব্যবহার করুন।

///

অথবা সরাসরি মডেলটি তৈরি করুন:

⟦CODE2⟧

একটি নিজের provider দিয়েও [`XaiModel`][pydantic_ai.models.xai.XaiModel] নিজের মতো করতে পারেন:

⟦CODE3⟧

gateway, regional বা proxy deployment-এর জন্য provider-কে একটি নিজের host-এ দেখাতে আর একটি client-স্তরের ডিফল্ট timeout সেট করতে পারেন, দুটোই ভেতরের `xai_sdk.AsyncClient`-এ পাঠানো হয়:

⟦CODE4⟧

`api_host` হলো xAI API সার্ভারের hostname (SDK gRPC দিয়ে সংযোগ করে), আর `timeout` হলো client-এর প্রতিটি রিকোয়েস্টে প্রয়োগ হওয়া সেকেন্ডে ডিফল্ট timeout; এটি ছাড়ানো একটি রিকোয়েস্ট [`ModelTimeoutError`][pydantic_ai.exceptions.ModelTimeoutError] তোলে। অন্য provider-এর মতো নয়, xAI SDK প্রতি-রিকোয়েস্ট timeout সমর্থন করে না, তাই [`ModelSettings.timeout`][pydantic_ai.settings.ModelSettings.timeout] সমর্থিত নয় আর এর কোনো প্রভাব নেই। সেট না করলে দুটো অপশনই বাদ পড়ে, তাই SDK-র নিজের ডিফল্ট প্রযোজ্য হয়।

অথবা একটি নিজের `xai_sdk.AsyncClient` দিয়ে:

⟦CODE5⟧

`xai_client` হিসেবে দেওয়া একটি client বন্ধ করা আপনার দায়িত্ব, যেমন `async with` দিয়ে; Pydantic AI কখনো এটি বন্ধ করে না। এর gRPC channel যে event loop-এ তৈরি হয়েছে তার সাথে বাঁধা, তাই যে event loop এটি ব্যবহার করে তার ভেতরে client তৈরি করুন, ওপরের মতো।

## Cache sticky routing { #cache-sticky-routing }

provider-এর client-এর প্রতিটি রিকোয়েস্টে gRPC `metadata` জুড়ে দিতে পারেন। এর আদর্শ ব্যবহার হলো xAI prompt-cache sticky routing, যা একটি `x-grok-conv-id` দিয়ে একটি কথোপকথনকে একটি cache node-এ আটকে রাখে, যাতে বারবার আসা prefix আবার প্রক্রিয়া না হয়ে cache থেকে দেওয়া হয়:

⟦CODE6⟧

`metadata` হলো `(key, value)` স্ট্রিং tuple-এর একটি ক্রম, যা হুবহু ভেতরের `xai_sdk.AsyncClient`-এ পাঠানো হয়, তাই xAI SDK-র নিজের [maximizing cache hits](https://docs.x.ai/developers/advanced-api-usage/prompt-caching/maximizing-cache-hits) ডকুমেন্টেশন প্রযোজ্য। যেহেতু এটি client-সীমিত, এটি provider দিয়ে করা *প্রতিটি* রিকোয়েস্টে প্রযোজ্য — একটি নির্দিষ্ট `x-grok-conv-id` দিয়ে কনফিগার করা একটি provider অসম্পর্কিত কথোপকথনের মধ্যে ভাগ করা উচিত নয়, নইলে সেই কথোপকথনগুলো একই cache node-এ সংঘর্ষ করবে। metadata কথোপকথন-নির্দিষ্ট হলে প্রতিটি কথোপকথনে আলাদা provider ব্যবহার করুন। `api_host` আর `timeout`-এর মতো, সেট না করলে এটি বাদ পড়ে আর একটি নিজের `xai_sdk.AsyncClient` দিলে উপেক্ষিত হয়।

## SDK retry { #sdk-retries }

`xai_sdk.AsyncClient` gRPC-র নিজের retry চালু করে: `UNAVAILABLE` দিয়ে ব্যর্থ একটি রিকোয়েস্ট সর্বোচ্চ 5 বার চেষ্টা হয়, 0.1 থেকে 1 সেকেন্ডের backoff-সহ। gRPC সার্ভারে কখনো পৌঁছায়নি এমন একটি প্রচেষ্টাও নিঃশব্দে আবার চেষ্টা করে। এই retry gRPC channel-এর ভেতরে ঘটে, তাই Pydantic AI এগুলো দেখতে বা গুনতে পারে না। retry নীতি নিজের কোডে রাখতে, gRPC retry বন্ধ থাকা একটি client দিন:

⟦CODE7⟧

retry নীতি channel-এর আর প্রতি রিকোয়েস্টে বদলাতে পারে না, তাই [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request)-এর xAI-তে কোনো প্রভাব নেই। এই স্তর কোথায় বসে তা দেখুন [Provider SDK retries](../retries.md#provider-sdk-retries)-এ।

## ছবি তৈরি { #image-generation }

অফিসিয়াল xAI SDK দিয়ে সরাসরি ছবি তৈরি আর রেফারেন্স-ছবি সম্পাদনার জন্য একটি `xai:` ছবির মডেলসহ [`ImageGenerator`][pydantic_ai.images.ImageGenerator] ব্যবহার করুন:

⟦CODE8⟧

xAI inline বা দূরের রেফারেন্স ছবি আর [`UploadedFile`][pydantic_ai.messages.UploadedFile] হিসেবে প্রকাশিত xAI Files API ID নেয়। মেশানো রেফারেন্স ইনপুটে SDK-কে ক্রম বদলাতে হবে এমন হওয়া চলবে না। সাধারণ API আর জ্যামিতির আচরণের জন্য দেখুন [image-generation guide](../image-generation.md)।

### Moderate করা ছবি { #moderated-images }

xAI নিঃশব্দে moderate করে: এটি একটি ছবি চিহ্নিত করলে, রিকোয়েস্ট তবুও সফল হয় আর চিহ্নিত ঘরটি একটি এরর নয়, খালি ফেরত আসে। Pydantic AI চিহ্নিত হয়নি এমন ছবিগুলো ফেরত দেয়, তাই একটি চিহ্নিত ছবি আপনার বিল হওয়া একটি batch-এর বাকিটা বাতিল করে না, আর চিহ্নিত অবস্থানগুলো জানায় `provider_details['moderated_image_indices']`-এ।

সেই key-তে থাকে batch-এর যে শূন্য-ভিত্তিক অবস্থান xAI চিহ্নিত করেছে, আর এটি থাকে শুধু অন্তত একটি ছবি চিহ্নিত হলে, তাই `len(result.images)` আর চিহ্নিত অবস্থানের সংখ্যা মিলে আপনার চাওয়া `xai_n`-এর সমান। একটি [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] ওঠে শুধু প্রতিটি ছবি চিহ্নিত হলে, কারণ তখন ফেরত দেওয়ার মতো কোনো ফল নেই।

## X Search { #x-search }

xAI মডেল তাৎক্ষণিক পোস্ট আর বিষয়বস্তুর জন্য X (আগে Twitter) সার্চ সমর্থন করে। এটি চালুর প্রস্তাবিত উপায় হলো [`XSearch`][pydantic_ai.capabilities.XSearch] capability — provider-জুড়ে ব্যবহারসহ আরও বিস্তারিতের জন্য দেখুন [capability ডকুমেন্টেশন](../capabilities/overview.md#provider-adaptive-tools)। সমর্থিত অপশনের পুরো তালিকার জন্য দেখুন [xAI X Search ডকুমেন্টেশন](https://docs.x.ai/developers/tools/x-search)।

⟦CODE9⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

`XSearch` capability নেয়:

- **`allowed_x_handles`** / **`excluded_x_handles`**: সর্বোচ্চ 20টি X handle-এ (বা সেগুলো বাদ দিয়ে) ফল ছাঁকে। এগুলো পরস্পর-বর্জনশীল।
- **`from_date`** / **`to_date`**: দেওয়া datetime পরিসরে তৈরি পোস্টে ফল সীমিত করে (naive datetime UTC হিসেবে ধরা হয়)।
- **`enable_image_understanding`** (ডিফল্ট: `False`): পোস্টে সংযুক্ত ছবি বিশ্লেষণ করে।
- **`enable_video_understanding`** (ডিফল্ট: `False`): পোস্টে সংযুক্ত ভিডিওর বিষয়বস্তু বিশ্লেষণ করে।
- **`include_output`** (ডিফল্ট: `False`): [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে পাওয়া [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ কাঁচা X সার্চ ফল রাখে। এটি ছাড়া, মডেল সার্চ ফল ভেতরে ব্যবহার করে কিন্তু শুধু তার লেখার সারাংশ ফেরত দেয়; এটি চালু করলে সার্চ করা পোস্ট, উৎস আর metadata প্রোগ্রাম দিয়ে পাওয়া যায়।

capability-র বিকল্প হিসেবে, নিম্ন-স্তরের [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] সরাসরি `capabilities=[NativeTool(XSearchTool(...))]` দিয়ে দিতে পারেন — দেখুন [X Search Tool ডকুমেন্টেশন](../native-tools.md#x-search-tool) — বা [`XaiModelSettings.xai_include_x_search_output`][pydantic_ai.models.xai.XaiModelSettings.xai_include_x_search_output] [মডেল সেটিং](../agent.md#model-run-settings) দিয়ে সব জায়গায় কাঁচা আউটপুট চালু করতে পারেন।

## ফাইল সংযুক্তি { #file-attachments }

একটি user prompt-এ একটি ডকুমেন্ট রাখলে, xAI [সমর্থিত agentic মডেলে](https://docs.x.ai/developers/files) নিজে থেকে তার `attachment_search` টুল উপলব্ধ করে। মডেল টুলটি ব্যবহার করলে, Pydantic AI মডেলের উত্তরের পাশাপাশি এর জীবনচক্র দেখায়। xAI প্রতিটি ফাইল [48 MB](https://docs.x.ai/developers/files#limitations)-এ সীমিত রাখে। সমর্থিত ইনপুট রূপের জন্য দেখুন [document input](../input.md#document-input)।

[`NativeToolCallPart`][pydantic_ai.messages.NativeToolCallPart] আর [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এর `tool_name` হলো `'attachment_search'`, আর কলের `provider_details['function_name']`-এ থাকে এটি যে কাজ চালিয়েছে তার xAI-র নিজের নাম (যেমন `'pdf_browse'`)। xAI-কে [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ ঘাঁটা বিষয়বস্তু রাখতে বলতে [`XaiModelSettings.xai_include_attachment_search_output`][pydantic_ai.models.xai.XaiModelSettings.xai_include_attachment_search_output] `True` সেট করুন। এর ডিফল্ট `False`, তাই আপনি চালু না করলে অপশনটি পাঠানো হয় না।

Attachment search সরাসরি একটি কথোপকথনে সংযুক্ত ফাইলে প্রযোজ্য। বদলে স্থায়ী xAI collection সার্চ করতে, [`FileSearchTool`][pydantic_ai.native_tools.FileSearchTool] ব্যবহার করুন।

## Reasoning effort { #reasoning-effort }

Grok 4.3 `reasoning_effort` মান `'none'`, `'low'`, `'medium'` আর `'high'` সমর্থন করে। এটি সরাসরি [`XaiModelSettings.xai_reasoning_effort`][pydantic_ai.models.xai.XaiModelSettings.xai_reasoning_effort] দিয়ে কনফিগার করতে পারেন, বা provider-জুড়ে [`ModelSettings.thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং ব্যবহার করতে পারেন:

⟦CODE10⟧

Grok 4.3-এ reasoning বন্ধ করতে `xai_reasoning_effort='none'` বা `thinking=False` সেট করুন। xAI কয়েকটি অবসরপ্রাপ্ত লেখার মডেল slug `grok-4.3`-এ পাঠায়; অনুমেয় আচরণ আর খরচ দরকার হলে `grok-4.3` আর একটি স্পষ্ট reasoning effort বাছুন। বিস্তারিত জানতে দেখুন [xAI May 15 retirement guide](https://docs.x.ai/developers/migration/may-15-retirement)।

Grok 3 Mini (`grok-3-mini` আর `grok-3-mini-fast`)-ও `'none'` নেয়, তাই `thinking=False` সেখানেও reasoning বন্ধ করে; `thinking=True` আর অন্য স্তরগুলো এর `'low'` আর `'high'`-এ ম্যাপ হয়।

Grok 4.5 আর 4.6 `'low'`, `'medium'` আর `'high'` সমর্থন করে কিন্তু `'none'` নয়, তাই সেগুলো সবসময় reasoning করে: `thinking=False` সর্বনিম্ন effort `'low'` পাঠায়, আর `thinking=True` `'medium'`-এ ম্যাপ হয়। Grok 4.7 একই মান সমর্থন করে কিন্তু `'none'` নয়; `thinking=False`-ও `'low'` পাঠায়, অথচ `thinking=True` `reasoning_effort` বাদ দেয় যাতে xAI তার নথিভুক্ত `'high'` ডিফল্ট প্রয়োগ করে। xAI `'xhigh'` নেয়, কিন্তু Pydantic AI বর্তমানে এটিকে (আর একীভূত `'max'`-কে) `'high'`-এ ম্যাপ করে; নিজস্ব সমর্থনের জন্য দেখুন [issue #9744](https://github.com/pydantic/pydantic-ai/issues/9744)।

## Agentic দফা { #agentic-turns }

একটি রিকোয়েস্ট xAI-এর সার্ভার-পক্ষের [নেটিভ টুল](../native-tools.md) (যেমন web search, code execution, X search) ব্যবহার করলে, xAI একটি চূড়ান্ত উত্তর ফেরত দেওয়ার আগে নিজের loop চালায় — সেই টুলগুলো ডেকে আর তাদের ফল প্রক্রিয়া করে। সেই সার্ভার-পক্ষের loop কতগুলো দফা নিতে পারে তা [`XaiModelSettings.xai_max_turns`][pydantic_ai.models.xai.XaiModelSettings.xai_max_turns] দিয়ে সীমিত করতে পারেন:

⟦CODE11⟧

`xai_max_turns` শুধু xAI-এর সার্ভার-পক্ষের নেটিভ-টুল loop নিয়ন্ত্রণ করে। সাধারণ client-পক্ষের টুল বা Pydantic AI-এর নিজের এজেন্ট loop-এ এর কোনো প্রভাব নেই — সেগুলো সীমিত করতে, [`UsageLimits`][pydantic_ai.usage.UsageLimits] ব্যবহার করুন।

মনে রাখবেন সমান্তরাল টুল কল চালু থাকলে, একটি দফায় একাধিক টুল কল ঘটতে পারে, তাই `xai_max_turns` মোট টুল কলের সংখ্যার সমান না-ও হতে পারে।

## Multi-agent মডেল { #multi-agent-models }

xAI-এর [multi-agent মডেল](https://docs.x.ai/developers/model-capabilities/text/multi-agent) (যেমন `grok-4.20-multi-agent`) উত্তর দেওয়ার আগে কয়েকটি এজেন্ট দিয়ে সমান্তরালে একটি প্রশ্ন নিয়ে গবেষণা করে। এগুলো কতগুলো এজেন্ট ব্যবহার করবে তা [`XaiModelSettings.xai_agent_count`][pydantic_ai.models.xai.XaiModelSettings.xai_agent_count] দিয়ে বাছতে পারেন, যা `4` বা `16` নেয়:

⟦CODE12⟧

বেশি এজেন্ট মানে গভীর গবেষণা, বেশি token আর বেশি দেরির বিনিময়ে। অন্য xAI মডেল সেটিংটি উপেক্ষা করে।

## Stream বাতিল { #streaming-cancellation }

/// note | Transport বাতিল

[`cancel()`][pydantic_ai.result.StreamedRunResult.cancel] নিরাপদে একটি সক্রিয় লোকাল stream-টানা বাধা দেয়, আরেকটি task-এ চলা একটিসহ। বর্তমান `xai-sdk` release সেই বাতিল দিয়ে একটি সক্রিয় gRPC পড়া বাতিল করে, কিন্তু SDK কোনো নথিভুক্ত প্রতি-stream RPC handle দেয় না। তাই লোকাল iterator বন্ধ হওয়ার পরে দূরের তৈরি বা বিলিং কখন থামে তার নিশ্চয়তা নেই। দেখুন [xai-org/xai-sdk-python#142](https://github.com/xai-org/xai-sdk-python/issues/142)।

///

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[xai]"`, `XAI_API_KEY`, তারপর `Agent('xai:grok-4.3')`।
* timeout প্রতি client-এ (`XaiProvider(timeout=...)`); `ModelSettings.timeout` আর `max_retries` কাজ করে না।
* X সার্চে `XSearch` capability; reasoning-এ `thinking=` বা `xai_reasoning_effort`।
* সার্ভার-পক্ষের টুল loop সীমিত করতে `xai_max_turns`।

///
