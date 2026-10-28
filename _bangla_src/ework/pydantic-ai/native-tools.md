# নেটিভ টুল { #native-tools }

/// note | এই পেজে যা শিখবেন

* নেটিভ টুল কী: যে টুল LLM provider নিজেই দেয় আর তাদের সার্ভারে চালায় (web search, code execution, ছবি তৈরি...)।
* `NativeTool` দিয়ে এজেন্টে যোগ করা, আর রানের প্রসঙ্গ অনুযায়ী গতিশীল কনফিগারেশন।
* প্রতিটি টুল — Web Search, X Search, Code Execution, Image Generation, Web Fetch, Memory, Advisor, MCP Server, File Search — আর কোন provider কী সমর্থন করে।

///

নেটিভ টুল LLM provider দেয় আর চালায়, অথচ [common tools](common-tools.md) হলো Pydantic AI-এর চালানো নিজের বাস্তবায়ন।

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ টুল হলো আপনার নিজের রান্নাঘরে রান্না করা খাবার — আপনি রাঁধেন (Python ফাংশন চলে আপনার সার্ভারে)। নেটিভ টুল হলো রেস্তোরাঁর নিজস্ব রান্নাঘরে তৈরি পদ — আপনি শুধু অর্ডার দেন ("web search চালাও"), provider-এর সার্ভারেই সব হয়। সুবিধা: কোনো কোড লিখতে হয় না, দ্রুত। অসুবিধা: শুধু যে provider সেই "পদ" রাখে সেখানেই পাওয়া যায়।

///

## এক নজরে { #overview }

Pydantic AI নিচের নেটিভ টুলগুলো সমর্থন করে:

- **[`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool]**: এজেন্টকে ওয়েবে সার্চ করতে দেয়
- **[`XSearchTool`][pydantic_ai.native_tools.XSearchTool]**: এজেন্টকে X/Twitter সার্চ করতে দেয় (শুধু xAI)
- **[`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool]**: এজেন্টকে একটি নিরাপদ পরিবেশে কোড চালাতে দেয়
- **[`ImageGenerationTool`][pydantic_ai.native_tools.ImageGenerationTool]**: এজেন্টকে ছবি তৈরি করতে দেয়
- **[`WebFetchTool`][pydantic_ai.native_tools.WebFetchTool]**: এজেন্টকে ওয়েব পেজ আনতে দেয়
- **[`MemoryTool`][pydantic_ai.native_tools.MemoryTool]**: এজেন্টকে memory ব্যবহার করতে দেয়
- **[`MCPServerTool`][pydantic_ai.native_tools.MCPServerTool]**: এজেন্টকে দূরের MCP সার্ভার ব্যবহার করতে দেয়, যোগাযোগ মডেল provider সামলায়
- **[`FileSearchTool`][pydantic_ai.native_tools.FileSearchTool]**: এজেন্টকে vector search দিয়ে আপলোড করা ফাইলে সার্চ করতে দেয় (RAG)
- **[`AdvisorTool`][pydantic_ai.native_tools.AdvisorTool]**: একটি দ্রুত executor মডেলকে তৈরির মাঝে একটি শক্তিশালী advisor মডেলের পরামর্শ নিতে দেয় (Anthropic, OpenRouter)

এই টুলগুলো এজেন্টের `capabilities` তালিকায় দেওয়া হয়, [`NativeTool`][pydantic_ai.capabilities.NativeTool]-এ মোড়া, আর মডেল provider-এর অবকাঠামোয় চলে।

কল আর ফল মডেলের উত্তরে দেখা দেয় [`NativeToolCallPart`][pydantic_ai.messages.NativeToolCallPart] আর [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart] হিসেবে। একটি নেটিভ টুল কলের আগে মডেল যে লেখা লেখে তা আউটপুট নয়, ভূমিকা হিসেবে ধরা হয়, যদি না শেষ নেটিভ টুল কলের পরে কোনো লেখা না থাকে: কিছু provider, যেমন Gemini 2.5-সহ Google, একটি উত্তরকে ভিত্তি দেওয়া সার্চগুলো এর লেখার পরে জানায়।

/// warning | Provider সমর্থন

সব মডেল provider নেটিভ টুল সমর্থন করে না। একটি অসমর্থিত provider-এর সাথে একটি নেটিভ টুল ব্যবহার করলে, এজেন্ট চালানোর চেষ্টার সময় Pydantic AI একটি [`UserError`][pydantic_ai.exceptions.UserError] তুলবে।

একটি provider এমন একটি নেটিভ টুল সমর্থন করলে যা বর্তমানে Pydantic AI সমর্থন করে না, অনুগ্রহ করে একটি issue জমা দিন।

///

/// tip | Provider-অনুযায়ী মানিয়ে নেওয়া capability

একটি উচ্চ-স্তরের, মডেল-নিরপেক্ষ পদ্ধতির জন্য, [provider-adaptive tool capabilities](capabilities/overview.md#provider-adaptive-tools) বিবেচনা করুন: [`WebSearch`][pydantic_ai.capabilities.WebSearch], [`WebFetch`][pydantic_ai.capabilities.WebFetch], [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] আর [`MCP`][pydantic_ai.capabilities.MCP]। এগুলো সমর্থিত হলে নিজে থেকে মডেলের নেটিভ টুল ব্যবহার করে আর আপনি `local=` দিয়ে চালু করা একটি লোকাল বাস্তবায়নে ফিরে যায়, তাই আপনার এজেন্ট কোড না বদলেই provider-জুড়ে কাজ করে। দুটি ভিন্নভাবে কাজ করে: `ImageGeneration` `fallback_image_model=` বা `fallback_subagent_model=` দিয়ে built-in বিকল্পও চালু করে, আর `MCP` ডিফল্টভাবে লোকালে চলে আর `native=True` দিয়ে নেটিভ MCP বেছে নেয়।

///

### Google-এ টুলের মিশ্রণ { #google-tool-combinations }

[Gemini 3 মডেল](https://ai.google.dev/gemini-api/docs/structured-output#structured_outputs_with_tools) নেটিভ টুলকে ফাংশন টুলের সাথে মেলানো সমর্থন করে, [আউটপুট টুল](output.md#tool-output) আর [`NativeOutput`][pydantic_ai.output.NativeOutput]-সহ। আগের Gemini মডেল এই মিশ্রণ ব্যবহার করতে পারে না; নেটিভ টুলের পাশাপাশি গোছানো আউটপুটের জন্য [`PromptedOutput`][pydantic_ai.output.PromptedOutput] ব্যবহার করুন।

## গতিশীল কনফিগারেশন { #dynamic-configuration }

কখনো কখনো [run context][pydantic_ai.tools.RunContext]-এর ভিত্তিতে (যেমন ব্যবহারকারীর dependencies) একটি নেটিভ টুল গতিশীলভাবে কনফিগার করতে হয়, বা শর্তসাপেক্ষে বাদ দিতে হয়। `capabilities`-এ [`NativeTool`][pydantic_ai.capabilities.NativeTool] দিয়ে একটি ফাংশন মুড়ে এটি করতে পারেন। ফাংশনটি [`RunContext`][pydantic_ai.tools.RunContext] আর্গুমেন্ট নেয় আর একটি [`AbstractNativeTool`][pydantic_ai.native_tools.AbstractNativeTool] বা `None` ফেরত দেয়।

এটি বিশেষভাবে কাজে লাগে [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool]-এর মতো টুলে, যেখানে আপনি বর্তমান রিকোয়েস্টের ভিত্তিতে ব্যবহারকারীর অবস্থান সেট করতে চাইতে পারেন, বা ব্যবহারকারী কোনো অবস্থান না দিলে টুলটি বন্ধ করতে চাইতে পারেন।

⟦CODE1⟧

/// note | একটি `fallback_subagent_model`-এর অধীনে `None` ফেরত দেওয়া

যেখানেই নেটিভ টুল একমাত্র পথ, সেখানে `None` মানে বাদ দেওয়া। [`XSearch`][pydantic_ai.capabilities.XSearch] আর [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] ব্যতিক্রম: একবার `fallback_subagent_model` সেট হলে, factory `None` ফেরত দিলেই তাদের subagent টুল মডেলকে দেওয়া হয়, আর এটি ডাকলে ডিফল্ট সেটিং দিয়ে চলার বদলে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে। দেখুন [X Search](capabilities/x-search.md) আর [Image Generation](capabilities/image-generation.md)।

///

## Web Search টুল { #web-search-tool }

/// tip | পরামর্শ

`local='duckduckgo'` দিয়ে একটি ঐচ্ছিক লোকাল বিকল্পসহ একটি মডেল-নিরপেক্ষ পদ্ধতির জন্য, দেখুন [`WebSearch`][pydantic_ai.capabilities.WebSearch] [capability](capabilities/overview.md#provider-adaptive-tools)।

///

[`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] আপনার এজেন্টকে ওয়েবে সার্চ করতে দেয়,
যা সর্বশেষ ডেটা দরকার এমন প্রশ্নের জন্য আদর্শ।

### Provider সমর্থন { #provider-support }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| OpenAI Responses | ✅ | পূর্ণ সমর্থন। [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে পাওয়া [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ সার্চের ফল রাখতে, [`OpenAIResponsesModelSettings.openai_include_web_search_sources`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_include_web_search_sources] [মডেল সেটিং](agent.md#model-run-settings) চালু করুন। |
| Anthropic | ✅ | পূর্ণ সমর্থন |
| Google | ✅ | কোনো প্যারামিটার সমর্থন নেই, তাই একটি [সীমিত-করা প্যারামিটার](#restricting-parameters) টুলটিকে অসমর্থিত করে। সার্চের উৎস হলো [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এর বিষয়বস্তু, শুধু Gemini API-সহ Gemini 3-এ ছাড়া, যেখানে সেগুলো শেষ web search ফেরতের বিষয়বস্তুর `sources` key-এর নিচে, কারণ Gemini বলে না কোন সার্চ কোন উৎস পেয়েছে। Gemini 2.5 আর Google Cloud তাদের সার্চ যে লেখাকে ভিত্তি দেয় তার পরে জানায়, তাই কল আর ফেরত লেখার পরে আসে। দেখুন [Google tool combinations](#google-tool-combinations)। |
| xAI | ✅ | `blocked_domains`, `allowed_domains` আর `user_location` প্যারামিটার সমর্থন করে। |
| Groq | ✅ | সীমিত প্যারামিটার সমর্থন। Groq-এর সাথে web search ব্যবহার করতে, [compound মডেল](https://console.groq.com/docs/compound) ব্যবহার করতে হবে। |
| OpenRouter | ✅ | OpenRouter-এর [Beta web-search server tool](https://openrouter.ai/docs/guides/features/server-tools/web-search) ব্যবহার করে। মডেল 0–N সার্চ করতে পারে। রেকর্ড করা রিকোয়েস্ট শুধু যাচাই করে যে OpenRouter প্যারামিটারের নাম গ্রহণ করে; নিচের প্রতি-engine প্রভাব OpenRouter-এর ডক অনুযায়ী: নিজস্ব সার্চ `search_context_size` উপেক্ষা করে; `user_location` শুধু-নিজস্ব; নিজস্ব OpenAI `blocked_domains` উপেক্ষা করে; আর `max_uses` নিজস্ব-নয় বা Anthropic নিজস্ব সার্চে কাজ করে। সার্চের উৎস `provider_details['annotations']`-এ দেখা দেয়, কিন্তু শুধু যখন একটি নিজস্ব-নয় engine সার্চ চালায়। |
| OpenAI Chat Completions | ❌ | সমর্থিত নয় |
| Bedrock | ❌ | সমর্থিত নয় |
| Mistral | ❌ | সমর্থিত নয় |
| Cohere | ❌ | সমর্থিত নয় |
| HuggingFace | ❌ | সমর্থিত নয় |

### ব্যবহার { #usage }

⟦CODE2⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

Anthropic-এ, সার্চের সংখ্যা জানানো হয় [`RequestUsage.details`][pydantic_ai.usage.RequestUsage.details]-এ `web_search_requests` হিসেবে আর [`RunUsage.cost`][pydantic_ai.usage.RunUsage.cost]-এ ধরা হয়।

Google-এ, Google Search grounding query-র সংখ্যা জানানো হয় [`RequestUsage.details`][pydantic_ai.usage.RequestUsage.details]-এ `web_search_requests` হিসেবে, আর বিল হওয়া সংখ্যা [`RequestUsage`][pydantic_ai.usage.RequestUsage]-এ `web_searches` হিসেবে: Gemini 3-এ প্রতি অনন্য query-তে একটি, আর Gemini 2.5 আর পুরনোগুলোতে একটি ওয়েব উৎস ফেরত দেওয়া প্রতি grounded রিকোয়েস্টে একটি। বিল হওয়া সংখ্যা [`RunUsage.cost`][pydantic_ai.usage.RunUsage.cost]-এ ধরা হয়, Google-এর বিনামূল্যের grounding বরাদ্দ বাদ না দিয়ে।

OpenAI-এ, web search টুলে পৌঁছাতে আপনাকে তাদের Responses API ব্যবহার করতে হবে। সার্চের সংখ্যা জানানো হয় [`RequestUsage.details`][pydantic_ai.usage.RequestUsage.details]-এ `web_search_requests` হিসেবে আর [`RunUsage.cost`][pydantic_ai.usage.RunUsage.cost]-এ ধরা হয়। মডেল যে পেজ খোলে বা যার ভেতরে সার্চ করে সেগুলো সার্চ হিসেবে গোনা হয় না।

⟦CODE3⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### কনফিগারেশন অপশন { #configuration-options }

`WebSearchTool` কয়েকটি কনফিগারেশন প্যারামিটার সমর্থন করে:

⟦CODE4⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### Provider সমর্থন { #provider-support_1 }

| প্যারামিটার | OpenAI | Anthropic | xAI | Groq | OpenRouter |
|-----------|--------|-----------|-----|------|------------|
| `search_context_size` | ✅ | ❌ | ❌ | ❌ | ✅ |
| `user_location` | ✅ | ✅ | ✅ | ❌ | ✅ |
| `blocked_domains` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `allowed_domains` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `max_uses` | ❌ | ✅ | ❌ | ❌ | ✅* |
| `external_web_access` | ✅ | ❌ | ❌ | ❌ | ❌ |

* OpenRouter-এর ডকুমেন্টেশন অনুযায়ী, নিজস্ব provider সার্চ `max_uses` শুধু Anthropic-এ পাঠায়; অন্য নিজস্ব provider এটি উপেক্ষা করে।

Google এই প্যারামিটারগুলোর কোনোটিই সমর্থন করে না।

#### সীমিত-করা প্যারামিটার { #restricting-parameters }

`allowed_domains`, `blocked_domains`, `max_uses` আর `external_web_access=False` সার্চ কী করতে পারে তা সীমিত করে, তাই
Pydantic AI এগুলো ছাড়া টুলটি পাঠায় না। একটি সেট থাকলে আর মডেল এটি প্রয়োগ করতে না পারলে (ওপরে একটি ❌), টুলটি
সেই মডেলে অসমর্থিত ধরা হয়: একটি দেওয়া থাকলে একটি [লোকাল বিকল্প](capabilities/overview.md#provider-adaptive-tools) এর
জায়গায় চলে, একটি `optional=True` টুল বাদ পড়ে, আর অন্যথায় একটি
[`UserError`][pydantic_ai.exceptions.UserError] সেটিংগুলোর নাম বলে। বাকি প্যারামিটার শুধু ফল সূক্ষ্ম করে আর যে মডেল সমর্থন করে না সেগুলোতে বাদ পড়ে।

/// warning | সাধারণ ভুল

নিরাপত্তার জন্য `allowed_domains=['আমার-সাইট.com']` দিয়ে ভাবছেন সব provider-এ কাজ করবে? Google এটি সমর্থন করে না, তাই সেখানে টুলটিই চালানো যায় না (এরর বা লোকাল বিকল্প)। Pydantic AI নিঃশব্দে সীমা বাদ দিয়ে সার্চ চালায় না — এটি ইচ্ছাকৃত, যাতে আপনার নিষেধাজ্ঞা উপেক্ষিত না হয়।

///

/// note | Anthropic domain ছাঁকা

Anthropic-এ, আপনি হয় `blocked_domains` নয়তো `allowed_domains` ব্যবহার করতে পারেন, দুটো একসাথে নয়।

///

/// note | Anthropic Web Search টুলের সংস্করণ

Pydantic AI কোনো `dynamic_filtering` অপশন দেয় না। Anthropic-এর জন্য, Pydantic AI model profile আর Anthropic client থেকে
web search টুলের সংস্করণ বাছে: Anthropic-এর dynamic-filtering web টুল সমর্থন করা মডেল আর প্ল্যাটফর্মের জন্য `web_search_20260209`,
আর অন্যথায় `web_search_20250305`।
পুরনো Amazon Bedrock client Anthropic web search সমর্থন করে না, তাই `AsyncAnthropicBedrock`-এর সাথে `WebSearchTool` ব্যবহার করলে Pydantic AI
একটি `UserError` তোলে।
Vertex AI-তে, `WebSearchTool` সবসময় `web_search_20250305` ব্যবহার করে, কারণ Anthropic সেখানে
dynamic-filtering সংস্করণ দেয় না, তাই অন্যথায় সমর্থিত মডেলেও dynamic filtering অনুপলব্ধ।
বর্তমান মডেল সমর্থন আর প্ল্যাটফর্মের প্রাপ্যতার জন্য দেখুন [Anthropic web search ডক](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
আর [tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference)।

[`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool] যোগ করুন শুধু যখন আপনি
Anthropic-এর একা code execution টুল চান; `web_search_20260209` ব্যবহারে এটি লাগে না।
`_20260209` web টুলের Zero Data Retention আচরণের জন্য, দেখুন Anthropic-এর
[server tools ডক](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers)।

///

## X Search টুল { #x-search-tool }

/// tip | পরামর্শ

একটি subagent বিকল্পসহ একটি মডেল-নিরপেক্ষ পদ্ধতির জন্য, দেখুন [`XSearch`][pydantic_ai.capabilities.XSearch] [capability](capabilities/overview.md#provider-adaptive-tools)।

///

[`XSearchTool`][pydantic_ai.native_tools.XSearchTool] আপনার এজেন্টকে তাৎক্ষণিক পোস্ট আর বিষয়বস্তুর জন্য X/Twitter সার্চ করতে দেয়। xAI মডেল নিজস্বভাবে সমর্থন করে; `fallback_subagent_model` সেট করা [`XSearch`][pydantic_ai.capabilities.XSearch] capability দিয়ে অন্য মডেলে ব্যবহারযোগ্য। আরও বিস্তারিত জানতে দেখুন [xAI X Search ডকুমেন্টেশন](https://docs.x.ai/developers/tools/x-search)।

### ব্যবহার { #usage_1 }

⟦CODE5⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### কনফিগারেশন অপশন { #configuration-options_1 }

`XSearchTool` কয়েকটি কনফিগারেশন প্যারামিটার সমর্থন করে:

⟦CODE6⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// note | Handle ছাঁকা

আপনি `allowed_x_handles` বা `excluded_x_handles`-এর একটিই ব্যবহার করতে পারেন, দুটো একসাথে নয়। প্রতিটি তালিকা সর্বোচ্চ 20টি handle-এ সীমিত।

///

/// note | কাঁচা সার্চ ফল রাখা

ডিফল্টভাবে, xAI শুধু সার্চের মডেলের লেখার সারাংশ ফেরত দেয়। ভেতরের পোস্ট, উৎস আর metadata প্রোগ্রাম দিয়ে পেতে, [`XSearchTool`][pydantic_ai.native_tools.XSearchTool]-এ `include_output=True` সেট করুন (OpenAI web search-এর জন্য [`OpenAIResponsesModelSettings.openai_include_web_search_sources`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_include_web_search_sources]-এর সমতুল্য)। কাঁচা ফল তখন [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে দেখানো [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ পাওয়া যায়। বিকল্প হিসেবে, [`XaiModelSettings.xai_include_x_search_output`][pydantic_ai.models.xai.XaiModelSettings.xai_include_x_search_output] [মডেল সেটিং](agent.md#model-run-settings) দিয়ে সব জায়গায় চালু করতে পারেন। প্রস্তাবিত `XSearch` capability-ভিত্তিক পদ্ধতির জন্য দেখুন [xAI ডক](models/xai.md#x-search)।

///

## Code Execution টুল { #code-execution-tool }

[`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool] আপনার এজেন্টকে একটি নিরাপদ পরিবেশে কোড চালাতে দেয়,
যা হিসাবের কাজ, ডেটা বিশ্লেষণ আর গাণিতিক কাজের জন্য চমৎকার।

### Provider সমর্থন { #provider-support_2 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| OpenAI Responses | ✅ | [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে পাওয়া [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ code execution-এর আউটপুট রাখতে, [`OpenAIResponsesModelSettings.openai_include_code_execution_outputs`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_include_code_execution_outputs] [মডেল সেটিং](agent.md#model-run-settings) চালু করুন। code execution ছবি তৈরি করলে, যেমন চার্ট, সেগুলো [`ModelResponse.images`][pydantic_ai.messages.ModelResponse.images]-এ [`BinaryImage`][pydantic_ai.messages.BinaryImage] অবজেক্ট হিসেবে পাওয়া যাবে। তৈরি ছবিটি এজেন্ট রানের [ছবির আউটপুট](output.md#image-output) হিসেবেও ব্যবহার করা যায়। |
| Google | ✅ | দেখুন [Google tool combinations](#google-tool-combinations)। |
| Anthropic | ✅ | সামঞ্জস্যপূর্ণ Anthropic মডেলে পাওয়া যায়। Pydantic AI নিজে থেকে একটি সামঞ্জস্যপূর্ণ code execution টুলের সংস্করণ বাছে; override করতে দেখুন [Anthropic code execution tool version](models/anthropic.md#code-execution-tool-version)। |
| xAI | ✅ | পূর্ণ সমর্থন। |
| Groq | ❌ | |
| Bedrock | ✅ | শুধু Nova 2.0 মডেলে পাওয়া যায়। |
| OpenAI Chat Completions | ❌ | সমর্থিত নয়; [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] ব্যবহার করুন। |
| Mistral | ❌ | |
| Cohere | ❌ | |
| HuggingFace | ❌ | |

### ব্যবহার { #usage_2 }

⟦CODE7⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

লেখার আউটপুটের পাশাপাশি, OpenAI-এর code execution তাদের উত্তরের অংশ হিসেবে ছবি তৈরি করতে পারে। [`ModelResponse.images`][pydantic_ai.messages.ModelResponse.images] বা [ছবির আউটপুট](output.md#image-output) দিয়ে এই ছবিতে পৌঁছাতে [`OpenAIResponsesModelSettings.openai_include_code_execution_outputs`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_include_code_execution_outputs] [মডেল সেটিং](agent.md#model-run-settings) চালু থাকতে হবে।

⟦CODE8⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### ফাইল আপলোড { #file-uploads }

provider-এর Files API দিয়ে ফাইল আপলোড করে code execution container-এ উপলব্ধ করতে পারেন। এতে এজেন্ট ডেটা ফাইল প্রক্রিয়া, CSV বিশ্লেষণ, ছবি নিয়ে কাজ আর আরও অনেক কিছু করতে পারে।
যে ফাইলের [`UploadedFile.provider_name`][pydantic_ai.messages.UploadedFile.provider_name] মডেল provider-এর সাথে মেলে না সেগুলো উপেক্ষিত হয়।

#### Anthropic { #anthropic }

⟦CODE9⟧

ফাইল ব্যবস্থাপনা, স্থায়িত্ব আর container-এর আচরণের বিস্তারিত জানতে দেখুন [Anthropic Files API ডকুমেন্টেশন](https://platform.claude.com/docs/en/build-with-claude/files)।

#### OpenAI { #openai }

⟦CODE10⟧

ফাইল ব্যবস্থাপনা, container-এর জীবনচক্র আর স্থায়িত্বের আচরণের বিস্তারিত জানতে দেখুন [OpenAI Responses API ডকুমেন্টেশন](https://platform.openai.com/docs/api-reference/responses)।

#### Provider সমর্থন { #provider-support_3 }

| প্যারামিটার | Anthropic | OpenAI | Google | xAI |
|-----------|-----------|--------|--------|-----|
| `files` | ✅ | ✅ | ❌ | ❌ |

## Image Generation টুল { #image-generation-tool }

/// tip | পরামর্শ

নির্দিষ্ট ছবির মডেল দিয়ে অ্যাপ্লিকেশন-নিয়ন্ত্রিত তৈরি আর সম্পাদনার জন্য, দেখুন
[সরাসরি image-generation API](image-generation.md)। মডেলের নিজস্ব ছবি তৈরি ব্যবহার করা আর সেই একই API-তে ফিরে যাওয়া একটি এজেন্ট টুলের জন্য — `local=ImageGenerator(...)` বা `fallback_image_model=` দিয়ে — দেখুন
[`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] [capability](capabilities/image-generation.md)।

///

[`ImageGenerationTool`][pydantic_ai.native_tools.ImageGenerationTool] আপনার এজেন্টকে ছবি তৈরি করতে দেয়।

### Provider সমর্থন { #provider-support_4 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| OpenAI Responses | ✅ | পূর্ণ সমর্থন। শুধু GPT-5.2-এর চেয়ে নতুন মডেলে সমর্থিত। তৈরি ছবির metadata, যেমন ভেতরের ছবির মডেলে পাঠানো [`revised_prompt`](https://platform.openai.com/docs/guides/tools-image-generation#revised-prompt), [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে পাওয়া [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ পাওয়া যায়। |
| Google | ✅ | সীমিত প্যারামিটার সমর্থন। শুধু `gemini-3.1-flash-image`-এর মতো [ছবি তৈরির মডেলে](https://ai.google.dev/gemini-api/docs/image-generation) সমর্থিত। এই মডেলগুলো [ফাংশন টুল](tools.md) সমর্থন করে না আর সবসময় ছবি তৈরির বিকল্প থাকবে, এমনকি এই নেটিভ টুল স্পষ্টভাবে দেওয়া না থাকলেও। |
| Anthropic | ❌ | |
| xAI | ❌ | |
| Groq | ❌ | |
| Bedrock | ❌ | |
| Mistral | ❌ | |
| Cohere | ❌ | |
| HuggingFace | ❌ | |

### ব্যবহার { #usage_3 }

তৈরি ছবি [`ModelResponse.images`][pydantic_ai.messages.ModelResponse.images]-এ [`BinaryImage`][pydantic_ai.messages.BinaryImage] অবজেক্ট হিসেবে পাওয়া যায়:

⟦CODE11⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

Google-এর [ছবি তৈরির মডেলে](https://ai.google.dev/gemini-api/docs/image-generation) ছবি তৈরির জন্য `ImageGenerationTool` নেটিভ টুল স্পষ্টভাবে দেওয়ার দরকার নেই:

⟦CODE12⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

[ছবির আউটপুট](output.md#image-output) পেতে `ImageGenerationTool` `output_type=BinaryImage`-এর সাথে একসাথে ব্যবহার করা যায়। `ImageGenerationTool` নেটিভ টুল স্পষ্টভাবে দেওয়া না থাকলে, এটি নিজে থেকে চালু হবে:

⟦CODE13⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### কনফিগারেশন অপশন { #configuration-options_2 }

`ImageGenerationTool` কয়েকটি কনফিগারেশন প্যারামিটার সমর্থন করে:

⟦CODE14⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

OpenAI Responses মডেলও `aspect_ratio` প্যারামিটার মানে। যেহেতু OpenAI API শুধু নির্দিষ্ট কয়েকটি ছবির আকার দেয়,
Pydantic AI `'1:1'` -> `1024x1024`, `'2:3'` -> `1024x1536` আর `'3:2'` -> `1536x1024` ম্যাপ করে। অন্য কোনো aspect ratio দিলে
একটি এরর হয়, আর আপনি `size`-ও সেট করলে তা হিসাব করা মানের সাথে মিলতে হবে।

OpenAI Responses-এর ছবি তৈরির টুলের ডিফল্ট `action='auto'`, যেখানে মডেল ঠিক করে একটি নতুন
ছবি তৈরি করবে নাকি প্রসঙ্গে আগে থেকে থাকা একটি সম্পাদনা করবে। যেকোনো আচরণ বাধ্য করতে `action='generate'` বা `action='edit'` ব্যবহার করুন। টুলের ব্যবহৃত ভেতরের ছবির মডেল বাছতে `model`-ও সেট করতে পারেন, যেমন `model='gpt-image-2.5-flare'`; এটি
এজেন্টের কথোপকথনের মডেল বদলায় না।

Gemini ছবির মডেল ব্যবহারের সময় aspect ratio নিয়ন্ত্রণ করতে, `ImageGenerationTool` স্পষ্টভাবে রাখুন:

⟦CODE15⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

Google ছবি তৈরির মডেলে (Gemini 3 Pro Image থেকে শুরু করে) ছবির resolution নিয়ন্ত্রণ করতে, `size` প্যারামিটার ব্যবহার করুন:

⟦CODE16⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

আরও বিস্তারিত জানতে, [API ডকুমেন্টেশন][pydantic_ai.native_tools.ImageGenerationTool] দেখুন।

#### Provider সমর্থন { #provider-support_5 }

| প্যারামিটার | OpenAI | Google |
|-----------|--------|--------|
| `action` | ✅ (auto (ডিফল্ট), generate, edit) | ❌ |
| `background` | ✅ | ❌ |
| `input_fidelity` | ✅ | ❌ |
| `moderation` | ✅ | ❌ |
| `model` | ✅ (একটি OpenAI ছবির মডেল ID, যেমন `gpt-image-2.5-flare`) | ❌ |
| `output_compression` | ✅ (100 (ডিফল্ট), শুধু jpeg বা webp) | ✅ (75 (ডিফল্ট), শুধু jpeg, শুধু Google Cloud) |
| `output_format` | ✅ | ✅ (শুধু Google Cloud) |
| `partial_images` | ✅ | ❌ |
| `quality` | ✅ | ❌ |
| `size` | ✅ (auto (ডিফল্ট), 1024x1024, 1024x1536, 1536x1024) | ✅ (512, 1K (ডিফল্ট), 2K, 4K) |
| `aspect_ratio` | ✅ (1:1, 2:3, 3:2) | ✅ (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9) |

/// note | নোট

- **OpenAI**: `auto` মডেলকে মান বাছতে দেয়।
- **Google Cloud**: `output_compression` সেট করলে, নির্দিষ্ট না থাকলে `output_format` ডিফল্ট `jpeg` হবে।

///

## Web Fetch টুল { #web-fetch-tool }

/// tip | পরামর্শ

`local=True` দিয়ে একটি ঐচ্ছিক লোকাল বিকল্পসহ একটি মডেল-নিরপেক্ষ পদ্ধতির জন্য, দেখুন [`WebFetch`][pydantic_ai.capabilities.WebFetch] [capability](capabilities/overview.md#provider-adaptive-tools)।

///

[`WebFetchTool`][pydantic_ai.native_tools.WebFetchTool] আপনার এজেন্টকে URL-এর বিষয়বস্তু তার প্রসঙ্গে টেনে আনতে দেয়,
ওয়েব থেকে সর্বশেষ তথ্য আনতে দিয়ে।

### Provider সমর্থন { #provider-support_6 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| Anthropic | ✅ | পূর্ণ সমর্থন। URL-এর বিষয়বস্তু আনতে ভেতরে Anthropic-এর [Web Fetch Tool](https://docs.claude.com/en/docs/agents-and-tools/tool-use/web-fetch-tool) ব্যবহার করে। |
| Google | ✅ | কোনো প্যারামিটার সমর্থন নেই। সীমা নির্দিষ্ট: প্রতি রিকোয়েস্টে 20টি URL, প্রতি URL-এ সর্বোচ্চ 34MB। দেখুন [Google tool combinations](#google-tool-combinations)। |
| xAI | ❌ | xAI-তে ওয়েব ব্রাউজিং [`WebSearchTool`](#web-search-tool)-এর অংশ হিসেবে বাস্তবায়িত। |
| OpenAI | ❌ | |
| Groq | ❌ | |
| Bedrock | ❌ | |
| Mistral | ❌ | |
| Cohere | ❌ | |
| HuggingFace | ❌ | |

### ব্যবহার { #usage_4 }

⟦CODE17⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### কনফিগারেশন অপশন { #configuration-options_3 }

`WebFetchTool` কয়েকটি কনফিগারেশন প্যারামিটার সমর্থন করে:

⟦CODE18⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### Provider সমর্থন { #provider-support_7 }

| প্যারামিটার | Anthropic | Google |
|-----------|-----------|--------|
| `max_uses` | ✅ | ❌ |
| `allowed_domains` | ✅ | ❌ |
| `blocked_domains` | ✅ | ❌ |
| `enable_citations` | ✅ | ❌ |
| `max_content_tokens` | ✅ | ❌ |

[web search](#restricting-parameters)-এর মতো, `max_uses`, `allowed_domains` আর `blocked_domains` টুল কী করতে পারে তা সীমিত করে: সেট করা একটি প্রয়োগ করতে পারে না এমন একটি মডেলে, টুলটি অসমর্থিত ধরা হয়, তাই একটি দেওয়া থাকলে একটি লোকাল বিকল্প
এর জায়গায় চলে, একটি `optional=True` টুল বাদ পড়ে, আর অন্যথায় একটি
[`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

/// note | Anthropic domain ছাঁকা

Anthropic-এ, আপনি হয় `blocked_domains` নয়তো `allowed_domains` ব্যবহার করতে পারেন, দুটো একসাথে নয়।

///

/// note | Anthropic Web Fetch টুলের সংস্করণ

Pydantic AI কোনো `dynamic_filtering` অপশন দেয় না। Anthropic-এর জন্য, Pydantic AI model profile আর Anthropic client থেকে
web fetch টুলের সংস্করণ বাছে: Anthropic-এর dynamic-filtering web টুল সমর্থন করা মডেল আর প্ল্যাটফর্মের জন্য `web_fetch_20260209`,
আর অন্যথায় `web_fetch_20250910`।
`WebFetchTool` পুরনো Amazon Bedrock আর Vertex AI Anthropic client-এ অনুপলব্ধ, তাই
`AsyncAnthropicBedrock` বা `AsyncAnthropicVertex`-এর সাথে এটি ব্যবহার করলে Pydantic AI একটি `UserError` তোলে।
বর্তমান মডেল সমর্থন আর প্ল্যাটফর্মের প্রাপ্যতার জন্য দেখুন
[Anthropic web fetch ডক](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool)
আর [tool reference](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference)।

[`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool] যোগ করুন শুধু যখন আপনি
Anthropic-এর একা code execution টুল চান; `web_fetch_20260209` ব্যবহারে এটি লাগে না।
`_20260209` web টুলের Zero Data Retention আচরণের জন্য, দেখুন Anthropic-এর
[server tools ডক](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools#zdr-and-allowed-callers)।

///

## Memory টুল { #memory-tool }

[`MemoryTool`][pydantic_ai.native_tools.MemoryTool] আপনার এজেন্টকে memory ব্যবহার করতে দেয়।

### Provider সমর্থন { #provider-support_8 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| Anthropic | ✅ | [নির্দিষ্ট sub-command](https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool#tool-commands) বাস্তবায়ন করা `memory` নামের একটি টুল সংজ্ঞায়িত থাকতে হবে। নিচে নথিভুক্ত মতো [`anthropic.lib.tools.BetaAbstractMemoryTool`](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/lib/tools/_beta_builtin_memory_tool.py)-এর একটি subclass ব্যবহার করতে পারেন। |
| Google | ❌ | |
| OpenAI | ❌ | |
| Groq | ❌ | |
| Bedrock | ❌ | |
| Mistral | ❌ | |
| Cohere | ❌ | |
| HuggingFace | ❌ | |

### ব্যবহার { #usage_5 }

Anthropic SDK একটি abstract [`BetaAbstractMemoryTool`](https://github.com/anthropics/anthropic-sdk-python/blob/main/src/anthropic/lib/tools/_beta_builtin_memory_tool.py) ক্লাস দেয়, যার subclass করে আপনি নিজের memory সংরক্ষণের সমাধান তৈরি করতে পারেন (যেমন ডেটাবেস, cloud storage, এনক্রিপ্ট করা ফাইল ইত্যাদি)। তাদের [`LocalFilesystemMemoryTool`](https://github.com/anthropics/anthropic-sdk-python/blob/main/examples/memory/basic.py) উদাহরণ একটি শুরুর বিন্দু হতে পারে।

নিচের উদাহরণ একটি নির্দিষ্ট memory লিখে রাখা একটি subclass ব্যবহার করে। Pydantic AI-এর নিজস্ব অংশ হলো `MemoryTool` নেটিভ টুল আর `memory` টুল সংজ্ঞা, যা কমান্ডগুলো `BetaAbstractMemoryTool` subclass-এর `call` মেথডে পাঠায়।

⟦CODE19⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## Advisor টুল { #advisor-tool }

[`AdvisorTool`][pydantic_ai.native_tools.AdvisorTool] একটি executor মডেলকে তৈরির মাঝে আরেকটি মডেলের পরামর্শ নিতে দেয়। বর্তমান মডেল সামঞ্জস্যের জন্য দেখুন [Anthropic](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) আর [OpenRouter](https://openrouter.ai/docs/guides/features/server-tools/advisor) ডকুমেন্টেশন।

/// tip | উদাহরণ দিয়ে বুঝি

একজন জুনিয়র কর্মী (দ্রুত, সস্তা মডেল) কাজ করতে করতে কঠিন জায়গায় একজন সিনিয়রকে (শক্তিশালী মডেল) জিজ্ঞেস করে নেয়, পুরো কাজটা সিনিয়রকে না দিয়ে। এতে খরচ কম থাকে, আর মান সিনিয়রের কাছাকাছি হয়।

///

### Provider সমর্থন { #provider-support_9 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| Anthropic | ✅ | Claude API আর AWS-এ Claude Platform-এ পাওয়া যায়। |
| OpenRouter | ✅ | যেকোনো executor মডেলের সাথে কাজ করে। |
| OpenAI | ❌ | |
| Google | ❌ | |
| xAI | ❌ | |
| Groq | ❌ | |
| Bedrock | ❌ | |
| Mistral | ❌ | |
| Cohere | ❌ | |
| HuggingFace | ❌ | |

### ব্যবহার { #usage_6 }

⟦CODE20⟧

OpenRouter-এর জন্য, যেকোনো `openrouter:` executor ব্যবহার করুন আর `model`-এ একটি OpenRouter মডেল slug দিন, যেমন `anthropic/claude-opus-4.8`। Pydantic AI `forward_transcript=false` পাঠায়; `max_uses` আর `caching` উপেক্ষিত হয়। Pydantic AI মোট পরামর্শের সংখ্যা দেখায় [`ModelResponse.provider_details`][pydantic_ai.messages.ModelResponse.provider_details]-এর `['server_tool_use']`-এ।

Anthropic-এ, Pydantic AI বার্তার ইতিহাসে সাধারণ-লেখা আর এনক্রিপ্ট করা advisor ফল রক্ষা করে, আর টুলটি আর চালু না থাকলে advisor ব্লক সরায়। advisor চলার সময় streaming থামে। Advisor-এর usage জানানো হয় [`RequestUsage.details`][pydantic_ai.usage.RequestUsage.details]-এ `advisor_*` key-এর নিচে আর executor-এর শীর্ষ-স্তরের token মোট থেকে বাদ থাকে।

### কনফিগারেশন অপশন { #configuration-options_4 }

| প্যারামিটার | Anthropic | OpenRouter |
|-----------|-----------|------------|
| `model` | ✅ (বাধ্যতামূলক — পরামর্শের advisor মডেল) | ✅ (বাধ্যতামূলক — একটি OpenRouter catalog slug) |
| `max_uses` | ✅ (প্রতি রিকোয়েস্টে advisor পরামর্শের সীমা) | ❌ (নির্দিষ্ট gateway সীমা; উপেক্ষিত) |
| `max_tokens` | ✅ (advisor-এর আউটপুট token-এর সীমা, সর্বনিম্ন 1024; ফলকে একটি `stop_reason` বহন করায়) | ✅ (`max_completion_tokens`-এ ম্যাপ হয়) |
| `caching` | ✅ (`'5m'` বা `'1h'` — advisor প্রসঙ্গের ক্ষণস্থায়ী caching) | ❌ (কোনো সমতুল্য নেই; উপেক্ষিত) |

## MCP Server টুল { #mcp-server-tool }

/// tip | পরামর্শ

স্বয়ংক্রিয় লোকাল বিকল্পসহ একটি মডেল-নিরপেক্ষ পদ্ধতির জন্য, দেখুন [`MCP`][pydantic_ai.capabilities.MCP] [capability](capabilities/overview.md#provider-adaptive-tools)।

///

[`MCPServerTool`][pydantic_ai.native_tools.MCPServerTool] আপনার এজেন্টকে দূরের MCP সার্ভার ব্যবহার করতে দেয়, যোগাযোগ মডেল provider সামলায়।

এর জন্য MCP সার্ভারটি provider পৌঁছাতে পারে এমন একটি সর্বজনীন URL-এ থাকতে হবে আর Pydantic AI-এর এজেন্ট-পক্ষের [MCP সমর্থনের](mcp/client.md) অনেক উন্নত সুবিধা সমর্থন করে না,
তবে Pydantic AI-তে ফেরত যাওয়া-আসা না থাকায় প্রসঙ্গের সর্বোত্তম ব্যবহার আর caching, আর দ্রুততর কর্মক্ষমতা দিতে পারে।

### Provider সমর্থন { #provider-support_10 }

| Provider | সমর্থিত | নোট                 |
|----------|-----------|-----------------------|
| OpenAI Responses | ✅ | পূর্ণ সমর্থন। একটি বিশেষ `x-openai-connector:<connector_id>` URL দিয়ে [Connector](https://platform.openai.com/docs/guides/tools-connectors-mcp#connectors) ব্যবহার করা যায়।  |
| Anthropic | ✅ | পূর্ণ সমর্থন |
| xAI | ✅ | পূর্ণ সমর্থন |
| Google  | ❌ | সমর্থিত নয় |
| Groq  | ❌ | সমর্থিত নয় |
| OpenAI Chat Completions | ❌ | সমর্থিত নয় |
| Bedrock | ❌ | সমর্থিত নয় |
| Mistral | ❌ | সমর্থিত নয় |
| Cohere | ❌ | সমর্থিত নয় |
| HuggingFace | ❌ | সমর্থিত নয় |

### ব্যবহার { #usage_7 }

⟦CODE21⟧

1. [DeepWiki MCP server](https://docs.devin.ai/work-with-devin/deepwiki-mcp)-এ কোনো অনুমোদন লাগে না।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

OpenAI-এ, MCP server টুলে পৌঁছাতে আপনাকে তাদের Responses API ব্যবহার করতে হবে:

⟦CODE22⟧

1. [DeepWiki MCP server](https://docs.devin.ai/work-with-devin/deepwiki-mcp)-এ কোনো অনুমোদন লাগে না।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### কনফিগারেশন অপশন { #configuration-options_5 }

`MCPServerTool` নিজের MCP সার্ভারের জন্য কয়েকটি কনফিগারেশন প্যারামিটার সমর্থন করে:

⟦CODE23⟧

1. [GitHub MCP server](https://github.com/github/github-mcp-server)-এর একটি অনুমোদন token লাগে।

OpenAI Responses-এ, একটি বিশেষ `x-openai-connector:` URL দিয়ে একটি [connector](https://platform.openai.com/docs/guides/tools-connectors-mcp#connectors) ব্যবহার করতে পারেন:

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

⟦CODE24⟧

1. OpenAI-এর Google Calendar connector-এর একটি [অনুমোদন token](https://platform.openai.com/docs/guides/tools-connectors-mcp#authorizing-a-connector) লাগে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### Provider সমর্থন { #provider-support_11 }

| প্যারামিটার             | OpenAI | Anthropic | xAI |
|-----------------------|--------|-----------|-----|
| `authorization_token` | ✅ | ✅ | ✅ |
| `allowed_tools`       | ✅ | ✅ | ✅ |
| `description`         | ✅ | ❌ | ✅ |
| `headers`             | ✅ | ❌ | ✅ |

## File Search টুল { #file-search-tool }

[`FileSearchTool`][pydantic_ai.native_tools.FileSearchTool] আপনার এজেন্টকে vector search দিয়ে আপলোড করা ফাইলে সার্চ করতে দেয়, একটি সম্পূর্ণ পরিচালিত Retrieval-Augmented Generation (RAG) ব্যবস্থা দিয়ে। এই টুল ফাইল সংরক্ষণ, টুকরো করা, embedding তৈরি আর prompt-এ প্রসঙ্গ ঢোকানো সামলায়।

/// tip | উদাহরণ দিয়ে বুঝি

আপনার কোম্পানির ১০০টি নীতিমালার PDF আছে। সবগুলো প্রতিবার prompt-এ পাঠানো অসম্ভব। File search হলো একজন গ্রন্থাগারিক: প্রশ্ন এলে তিনি শুধু প্রাসঙ্গিক কয়েকটি অনুচ্ছেদ খুঁজে মডেলকে দেন। আর এই গ্রন্থাগার provider নিজেই চালায় — আপনাকে vector database বানাতে হয় না।

///

### Provider সমর্থন { #provider-support_12 }

| Provider | সমর্থিত | নোট |
|----------|-----------|-------|
| OpenAI Responses | ✅ | পূর্ণ সমর্থন। [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) দিয়ে vector store-এ ফাইল আপলোড করতে হয়। [`ModelResponse.native_tool_calls`][pydantic_ai.messages.ModelResponse.native_tool_calls] দিয়ে পাওয়া [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ সার্চের ফল রাখতে, [`OpenAIResponsesModelSettings.openai_include_file_search_results`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_include_file_search_results] [মডেল সেটিং](agent.md#model-run-settings) চালু করুন। |
| Google (Gemini) | ✅ | [Gemini Files API](https://ai.google.dev/gemini-api/docs/files) দিয়ে ফাইল আপলোড করতে হয়। ফাইল 48 ঘণ্টা পরে নিজে থেকে মুছে যায়। প্রতি ফাইলে সর্বোচ্চ 2 GB আর প্রতি project-এ 20 GB সমর্থন করে। দেখুন [Google tool combinations](#google-tool-combinations)। |
| xAI | ✅ | xAI collections search-এ ম্যাপ করা। collection ID লাগে। [`NativeToolReturnPart`][pydantic_ai.messages.NativeToolReturnPart]-এ সার্চের ফল রাখতে, [`XaiModelSettings.xai_include_collections_search_output`][pydantic_ai.models.xai.XaiModelSettings.xai_include_collections_search_output] [মডেল সেটিং](agent.md#model-run-settings) চালু করুন। |
| Google Cloud | ❌ | সমর্থিত নয়; একই সীমাবদ্ধতা [Pydantic AI Gateway](gateway.md) দিয়ে Google পথেও প্রযোজ্য। |
| Anthropic | ❌ | সমর্থিত নয় |
| Groq | ❌ | সমর্থিত নয় |
| OpenAI Chat Completions | ❌ | সমর্থিত নয় |
| Bedrock | ❌ | সমর্থিত নয় |
| Mistral | ❌ | সমর্থিত নয় |
| Cohere | ❌ | সমর্থিত নয় |
| HuggingFace | ❌ | সমর্থিত নয় |

### ব্যবহার { #usage_8 }

#### OpenAI Responses { #openai-responses }

OpenAI-এ, আপনাকে প্রথমে [একটি vector store-এ ফাইল আপলোড](https://developers.openai.com/api/docs/guides/tools-file-search) করতে হবে, তারপর `FileSearchTool` ব্যবহারের সময় vector store ID-র রেফারেন্স দিতে হবে।

⟦CODE25⟧

#### Google (Gemini) { #google-gemini }

Gemini-তে, আপনাকে প্রথমে [Files API দিয়ে একটি file search store তৈরি](https://ai.google.dev/gemini-api/docs/files) করতে হবে, তারপর file search store-এর নামের রেফারেন্স দিতে হবে।

⟦CODE26⟧

#### xAI { #xai }

xAI-তে, `FileSearchTool` [collections search](https://docs.x.ai/developers/tools/collections-search) টুলে ম্যাপ হয়। collection ID `file_store_ids` হিসেবে দিন।

⟦CODE27⟧

xAI-এর collections search ফলের সংখ্যা, র‍্যাঙ্কিং নির্দেশনা আর খুঁজে আনার কৌশল নিয়ন্ত্রণের অপশনও নেয়। এগুলো [`FileSearchTool`][pydantic_ai.native_tools.FileSearchTool]-এর `max_num_results`, `instructions` আর `retrieval_mode` ফিল্ডে ম্যাপ হয়। বাদ দিলে, সার্ভার নিজের ডিফল্ট প্রয়োগ করে (10টি ফল, hybrid retrieval)।

⟦CODE28⟧

## Citation { #citations }

provider সমর্থন আর স্বাভাবিক করা ওয়েব আর ডকুমেন্ট citation কীভাবে ব্যবহার করবেন তা দেখুন [Citations](citations.md)-এ।

## API রেফারেন্স { #api-reference }

সম্পূর্ণ API ডকুমেন্টেশনের জন্য দেখুন [API Reference](api/native_tools.md)।

/// check | সংক্ষেপে মনে রাখুন

* নেটিভ টুল provider-এর সার্ভারে চলে; যোগ করুন `capabilities=[NativeTool(WebSearchTool())]` দিয়ে।
* সব provider সব টুল সমর্থন করে না — অসমর্থিত হলে `UserError`; provider-জুড়ে কাজ করতে `WebSearch`/`WebFetch`/`ImageGeneration`/`MCP` capability (লোকাল বিকল্পসহ)।
* OpenAI-এ বেশিরভাগ নেটিভ টুলের জন্য Responses API লাগে।
* সীমিত-করা প্যারামিটার (`allowed_domains`, `max_uses`...) প্রয়োগ না হলে টুলটি চলে না — নিঃশব্দে উপেক্ষিত হয় না।
* প্রসঙ্গ অনুযায়ী বদলাতে `NativeTool(lambda ctx: ...)`; `None` ফেরত দিলে টুল বাদ।

///
