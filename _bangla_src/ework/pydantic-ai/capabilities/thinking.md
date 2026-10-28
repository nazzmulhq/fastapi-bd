
# Thinking { #thinking }

/// note | এই পেজে যা শিখবেন

* Thinking (reasoning) কী, আর এক লাইনে সেটি কীভাবে চালু করবেন।
* `Thinking` capability আর `thinking` model setting — দুই পথ।
* effort-এর মান (`True`, `False`, `'low'` … `'max'`) কী বোঝায়, আর প্রতিটি provider-এ সেটি কীসে রূপান্তরিত হয়।
* message history-তে thinking কীভাবে ফেরত যায়, আর কথোপকথনের মাঝখানে effort বদলানো।
* OpenAI, Anthropic, Google, xAI, Bedrock, Groq, OpenRouter সহ প্রতিটি provider-এর নিজস্ব সেটিং।

///

Thinking (বা reasoning) হলো সেই প্রক্রিয়া, যেখানে মডেল চূড়ান্ত উত্তর দেওয়ার আগে ধাপে ধাপে সমস্যাটি নিয়ে ভাবে।

বিভিন্ন provider-এ একসাথে thinking চালু করার সবচেয়ে সহজ উপায় হলো [`Thinking`][pydantic_ai.capabilities.Thinking] [capability](overview.md)।
যখন কোনো provider-এর নিজস্ব (native) thinking নিয়ন্ত্রণে সরাসরি হাত দেওয়া দরকার, তখন অ্যাডভান্সড ব্যবহারের জন্য provider-ভিত্তিক সেটিংও আছে।

/// tip | উদাহরণ দিয়ে বুঝি

একজন ছাত্রকে অঙ্ক দিলে সে খাতার পাশে "রাফ কাজ" করে, তারপর পরিষ্কার করে উত্তর লেখে। মডেলের thinking ঠিক ওই রাফ খাতা। effort মানে আপনি তাকে কতটা রাফ কাজ করতে দিচ্ছেন — `'low'` হলে দ্রুত একটু ভেবে উত্তর, `'high'` হলে সময় নিয়ে খুঁটিয়ে ভাবা (বেশি টোকেন, বেশি খরচ, সাধারণত ভালো ফল)।

///

## একীভূত thinking সেটিং { #unified-thinking-settings }

thinking চালু করতে [`Thinking`][pydantic_ai.capabilities.Thinking] capability ব্যবহার করুন:

⟦CODE1⟧

চাইলে [`ModelSettings`][pydantic_ai.settings.ModelSettings]-এর ভেতরের `thinking` field-টি সরাসরিও সেট করতে পারেন:

⟦CODE2⟧

[`Thinking.effort`][pydantic_ai.capabilities.Thinking.effort] এই মানগুলো নেয়:

- `True` — provider-এর ডিফল্ট effort level-এ thinking চালু করে
- `False` — thinking বন্ধ করে; যে মডেল thinking বন্ধ করতে পারে না, সেখানে মডেল যতটা কম ভাবতে দেয় ততটাই ভাবে (তার সবচেয়ে কম effort, level বা budget)। যে মডেলের কোনো thinking সেটিংই নেই, সেটি নিজের ডিফল্টেই থাকে
- `'minimal'` / `'low'` / `'medium'` / `'high'` / `'xhigh'` / `'max'` — নির্দিষ্ট effort level-এ thinking চালু করে (যে level সাপোর্টেড নয়, সেটি সবচেয়ে কাছের উপলব্ধ মানে map হয়)

ভেতরের `thinking` model setting-ও ঠিক এই মানগুলোই নেয়।
বাদ দিলে মডেল তার ডিফল্ট আচরণ ব্যবহার করে। দুটোই সেট থাকলে provider-ভিত্তিক সেটিং (নিচের সেকশনগুলোতে বর্ণিত) অগ্রাধিকার পায় — ব্যতিক্রম শুধু এটুকু: Cerebras আর Groq-এর qwen3 মডেলে `thinking=False` তবুও reasoning বন্ধ করে। provider-ভিত্তিক সেটিং যদি `thinking`-এর চেয়ে বড় পরিসর (scope) থেকে আসে (যেমন সেটি মডেলের `settings`-এ, অথচ `thinking` এসেছে এই capability, `agent.run()` বা সরাসরি request থেকে), তাহলে একটি `UserWarning` দুটোর নামই জানিয়ে দেয়। callable হিসেবে দেওয়া সেটিং ([dynamic model settings](../agent.md#dynamic-model-settings)) এই পরীক্ষার আওতায় পড়ে না; আর কোনো capability-র সেটিং callable হলে বা `defer_loading` দিয়ে পিছিয়ে দেওয়া হলে, capability সেটিংগুলো (এই capability-র `thinking`-সহ) আর পরীক্ষা হয় না।

/// info | এক নজরে: effort-এর মান

| মান | মানে |
|---|---|
| বাদ দেওয়া | মডেলের নিজের ডিফল্ট আচরণ |
| `True` | thinking চালু, provider-এর ডিফল্ট effort |
| `False` | thinking বন্ধ (না পারলে সবচেয়ে কম) |
| `'minimal'` … `'max'` | নির্দিষ্ট effort; না থাকলে নিকটতম level |

///

### Provider-এ রূপান্তর { #provider-translation }

`Thinking` capability প্রতিটি effort মানকে নির্বাচিত provider-এর নিজস্ব ফরম্যাটে map করে:

⟦CODE3⟧

অনেক provider জানায়, একটি response-এর output token-গুলোর মধ্যে কতগুলো ছিল reasoning token। Pydantic AI এই সংখ্যাটি response-এর usage-এ [`output_reasoning_tokens`][pydantic_ai.usage.RequestUsage.output_reasoning_tokens] হিসেবে দেখায়, আর পুরো run জুড়ে যোগফল রাখে [`RunUsage`][pydantic_ai.usage.RunUsage]-এ। এটি `output_tokens`-এর মধ্যেই ধরা থাকে, আর মডেল reasoning না করলে বা provider আলাদা করে সংখ্যাটি না জানালে এর মান `0` হয়।

/// tip | পরামর্শ

খরচ হিসাব করার সময় `output_reasoning_tokens`-কে `output_tokens`-এর সাথে আলাদা করে যোগ করবেন না — এটি `output_tokens`-এর একটি অংশ মাত্র। শুধু জানতে কাজে লাগে, output-এর কতটা "ভাবনায়" গেল।

///

## message history-তে thinking { #thinking-in-message-history }

Pydantic AI message history-র [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] বাদ না দিয়ে মডেলের কাছে ফেরত পাঠায়। reasoning সাধারণত পরের turn-গুলোর জন্য ভারবাহী (load-bearing) — বাদ দিলে মডেল নিজের জন্য যে context তৈরি করেছিল, তা হারিয়ে যেত। এটি পাঠানো বন্ধ করার একমাত্র profile মান হলো [`openai_chat_send_back_thinking_parts`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_send_back_thinking_parts]-এ `False`, যা Pydantic AI-এর সাথে আসা কোনো মডেলই সেট করে না।

যেখানে provider-এর নিজস্ব reasoning channel আছে — signed thinking block, encrypted reasoning item, বা আলাদা `reasoning` field — সেখানে সেটিই reasoning বহন করে। এই প্রতিটি channel provider-এর নিজের তৈরি একটি প্রমাণপত্র (credential) যাচাই করে — একটি signature, বা item-টির জন্য সে যে id দিয়েছিল — তাই channel শুধু সেই part-এর জন্যই খোলা, যার কাছে সেটি এখনও আছে আর যেটি ঠিক সেই provider থেকেই এসেছে। যে part storage-এ ঘুরে আসার সময় সেটি হারিয়েছে, [history processor](../message-history.md#processing-message-history) দিয়ে নতুন করে তৈরি হয়েছে, বা [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] chain-এর অন্য কোনো মডেল থেকে এসেছে, সেটি ওই channel ব্যবহার করতে পারে না; তখন Pydantic AI reasoning বাদ না দিয়ে মডেলের thinking tag-এর ভেতরে text হিসেবে লিখে দেয়।

এই text *কোথায়* যায় আর *কীভাবে* tag করা হয় — দুই ক্ষেত্রেই Anthropic ব্যতিক্রম — দেখুন [Carried-over thinking](#carried-over-thinking)।

/// tip | উদাহরণ দিয়ে বুঝি

provider-এর signature অনেকটা অফিসের সিল-মারা কাগজের মতো। সিল অক্ষত থাকলে কাগজটি "অফিসিয়াল চ্যানেলে" জমা দেওয়া যায়। সিল মুছে গেলে (ডাটাবেসে রাখতে গিয়ে signature হারালে) বা অন্য অফিসের কাগজ হলে, Pydantic AI কাগজটি ফেলে দেয় না — লেখাটা সাধারণ নোট হিসেবে জুড়ে দেয়, যাতে মডেল অন্তত বিষয়বস্তুটা পায়।

///

## কথোপকথনের মাঝখানে effort বদলানো { #changing-effort-mid-conversation }

effort level এক run থেকে আরেক run-এ বদলাতে পারে, অথবা `model_settings` callable বা কোনো capability-র [`get_model_settings`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] দিয়ে এক ধাপ থেকে আরেক ধাপে বদলাতে পারে:

⟦CODE4⟧

request-level effort provider-এর [prompt cache](caching.md) key-এর অংশ, তাই নতুন level সেখানে পাঠালে provider-কে পুরো কথোপকথন আবার প্রসেস করতে হয়। যেখানে API কথোপকথনের একটি নির্দিষ্ট বিন্দু থেকে effort বদলাতে দেয়, Pydantic AI পরিবর্তনটি সেভাবেই পাঠায়, আর প্রতিটি request কথোপকথন যে effort দিয়ে শুরু হয়েছিল সেটিই রাখে:

| API | পরিবর্তনটি কীভাবে পাঠানো হয় | মডেল |
|---|---|---|
| OpenAI Responses | একটি `configuration_update` input item | GPT-6 family |
| Anthropic | একটি শুধু-effort `system` entry, সাথে প্রতি-message `output_config`, `mid-conversation-output-config-2026-07-01` beta-র অধীনে | Claude API আর Google Cloud-এ Claude Fable 5.1, Mythos 5.1, Opus 5.5, Opus 5, Sonnet 5.5 আর Haiku 5.5; legacy Bedrock InvokeModel client-এ Fable 5.1 আর Opus 5.5 |

বাকি সব API আর মডেল নতুন level-টি আগের মতোই request-level সেটিং হিসেবে পায়। নিচের ক্ষেত্রগুলোতেও তাই হয়, কারণ সেখানে API মাঝপথের পরিবর্তন নেয় না:

- `openai_reasoning_effort` বা `anthropic_effort`-এর মতো কোনো provider-ভিত্তিক effort সেটিং সেট করা আছে।
- OpenAI truncation (`openai_truncation='auto'`) বা server-side compaction ব্যবহার হচ্ছে।
- Anthropic thinking adaptive নয়, যেমন Claude Sonnet 5.5-এ `between_tools` বা Claude Haiku 5.5-এ `disabled`।
- পরিবর্তনটি `True` বা `False`-এ (বা সেখান থেকে) — এগুলো কোনো effort level-এর নাম বলে না।

framework প্রতিটি পরিবর্তন message history-তে একটি [`ModelSettingsDeltaPart`][pydantic_ai.messages.ModelSettingsDeltaPart] হিসেবে লিখে রাখে, যে request-এ সেটি প্রযোজ্য তার শেষে; আর যে প্রথম request কোনো effort level-এর নাম বলে, সেটিও একটি রেকর্ড করে। part-টি বদলানো সেটিংগুলো একীভূত [`ModelSettings`][pydantic_ai.settings.ModelSettings] key দিয়ে রাখে, যেমন `{'thinking': 'high'}`; কোন key রেকর্ড করা যায় তার তালিকা [`RecordedModelSettings`][pydantic_ai.settings.RecordedModelSettings]-এ — আজকের দিনে কেবল `thinking` effort level। প্রতিটি model adapter যে key-গুলো মাঝপথে বদলাতে পারে সেগুলো জায়গামতো পাঠায়, বাকিগুলো request-level সেটিং হিসেবে। `message_history` থেকে চলা পরের কোনো run এই part-গুলো পড়ে জানে, কথোপকথন কোন effort দিয়ে শুরু হয়েছিল আর কোন পরিবর্তনগুলো আবার পাঠাতে হবে। Vercel AI adapter এগুলো client-এর মধ্য দিয়ে বহন করে। AG-UI adapter এগুলো `pydantic_ai_model_settings_delta` activity message হিসেবে stream আর dump করে, যা `@ag-ui/client` ফেরত পাঠায় না; দেখুন [Records carried as activity messages](../ui/ag-ui.md#activity-records)।

/// note | Anthropic পরিবর্তনটি পরের user turn থেকে প্রয়োগ করে

Anthropic প্রতি-message effort পরিবর্তন প্রয়োগ করে নতুন input-সহ পরের user turn থেকে। যে ধাপ শুধু tool result ফেরত দেয়, সেখানে রেকর্ড করা পরিবর্তন কার্যকর হয় পরের user prompt-এ — তাই একটি run-এর ধাপগুলোর মাঝে effort বদলানো শুধু OpenAI Responses-এই সাপোর্টেড।

///

/// info | কোডটি সহজ ভাষায়

| ধাপ | কী ঘটে |
|---|---|
| প্রথম `run_sync` | `'low'` effort-এ দ্রুত একটি migration পরিকল্পনা |
| দ্বিতীয় `run_sync` | আগের `message_history`-সহ, এবার `'high'` effort-এ খুঁটিয়ে ঝুঁকি যাচাই |
| ভেতরে | সাপোর্টেড API-তে পরিবর্তনটি মাঝপথের আপডেট হিসেবে যায়, তাই prompt cache নষ্ট হয় না |

///

## OpenAI { #openai }

[`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] ব্যবহার করলে `<think>` tag-এর ভেতরের text output [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] object-এ রূপান্তরিত হয়।
[model profile](../models/compatible-apis.md#model-profile)-এর [`thinking_tags`][pydantic_ai.profiles.ModelProfile.thinking_tags] field দিয়ে tag-গুলো নিজের মতো বদলাতে পারেন।

কিছু [OpenAI-compatible model provider](../models/overview.md#openai-compatible-providers) এমন native thinking part-ও সাপোর্ট করতে পারে, যা tag দিয়ে আলাদা করা থাকে না; বরং API-তে আলাদা, কাস্টম field হিসেবে পাঠানো ও গ্রহণ করা হয়। সাধারণত `<provider>:<model>` সংক্ষিপ্ত রূপে মডেল ডাকলে Pydantic AI নিজেই এটি সামলে নেয়। তবুও [`openai_chat_thinking_field`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_thinking_field] দিয়ে field-গুলো কনফিগার করতে পারেন।

আপনার provider যদি caching বা interleaved thinking-এর জন্য এই কাস্টম field-গুলো অপরিবর্তিত অবস্থায় ফেরত পাঠানোর পরামর্শ দেয়, তাহলে [`openai_chat_send_back_thinking_parts`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_send_back_thinking_parts] ব্যবহার করুন।

### OpenAI Responses { #openai-responses }

[`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] native thinking part তৈরি করতে পারে।
native thinking part চালু করতে [model settings](../agent.md#model-run-settings)-এ [`OpenAIResponsesModelSettings.openai_reasoning_effort`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_effort] আর [`OpenAIResponsesModelSettings.openai_reasoning_summary`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_reasoning_summary] সেট করুন।
যে মডেলগুলো সাপোর্ট করে, সেগুলো অতিরিক্তভাবে একটি `pro` [reasoning mode](../models/openai.md#reasoning-mode)-ও ব্যবহার করতে পারে — এটি effort থেকে স্বাধীন, আর একীভূত `thinking` সেটিং কখনো এটি সেট করে না।

ডিফল্টভাবে message history-র reasoning, text আর function call part-গুলোর অনন্য ID মডেলের কাছে পাঠানো হয়। আপনি যে message history পাঠাচ্ছেন সেটি যদি Responses API-র আগের response থেকে পাওয়া জিনিসের সাথে হুবহু না মেলে — যেমন [history processor](../message-history.md#processing-message-history) ব্যবহার করলে — তাহলে `"Item 'rs_123' of type 'reasoning' was provided without its required following item."`-এর মতো error হতে পারে।
এটি বন্ধ করতে [`OpenAIResponsesModelSettings.openai_send_reasoning_ids`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_send_reasoning_ids] [model setting](../agent.md#model-run-settings)-টি নিষ্ক্রিয় করুন।

⟦CODE5⟧

/// note | summary ছাড়া raw reasoning

কিছু OpenAI-compatible API (যেমন LM Studio, vLLM, বা gpt-oss মডেলসহ OpenRouter) reasoning summary ছাড়াই raw reasoning content ফেরত দিতে পারে। সেক্ষেত্রে [`ThinkingPart.content`][pydantic_ai.messages.ThinkingPart.content] খালি থাকবে, তবে raw reasoning পাওয়া যাবে `provider_details['raw_content']`-এ। raw reasoning সরাসরি ব্যবহারকারীকে দেখানো উচিত নয় — [OpenAI-এর এই নির্দেশনা](https://cookbook.openai.com/examples/responses_api/reasoning_items) মেনে আমরা এটি মূল `content` field-এ না রেখে `provider_details`-এ রাখি।

///

/// warning | সাধারণ ভুল

history processor দিয়ে message বাদ দিলে বা বদলালে Responses API-তে `"Item 'rs_...' ... without its required following item"` error আসে। তখন মডেলকে দোষ না দিয়ে `openai_send_reasoning_ids=False` সেট করুন — reasoning item-এর ID আর পাঠানো হবে না, ফলে অমিলের কারণে আর আটকাবে না।

///

## Anthropic { #anthropic }

thinking চালু করতে [`AnthropicModelSettings.anthropic_thinking`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_thinking] [model setting](../agent.md#model-run-settings) ব্যবহার করুন।

/// note | মনে রাখুন

Extended thinking (`type: 'enabled'`, সাথে `budget_tokens`) `claude-opus-4-6`-এ deprecated, আর `claude-opus-4-7`, `claude-opus-4-8`, `claude-opus-5`, `claude-opus-5-5`, `claude-sonnet-5`, `claude-sonnet-5-5` ও `claude-haiku-5-5`-এ সরিয়ে ফেলা হয়েছে। এই মডেলগুলোর জন্য বরং [adaptive thinking](#adaptive-thinking-effort) ব্যবহার করুন।

///

⟦CODE6⟧

thinking budget [`max_tokens`][pydantic_ai.settings.ModelSettings.max_tokens]-এর মধ্যে গোনা হয়, আর Anthropic চায় `max_tokens` budget-এর চেয়ে বড় হোক। আপনি `max_tokens` সেট না করলে Pydantic AI প্রয়োজনমতো তার [ডিফল্ট](../models/anthropic.md#model-settings) বাড়িয়ে নেয়, যাতে budget-এর পরেও অন্তত 4096 token জায়গা থাকে।

Anthropic কতগুলো thinking token ব্যবহার করল, Pydantic AI তা জানায় `output_reasoning_tokens` হিসেবে, আর [`RunUsage.details`][pydantic_ai.usage.RunUsage.details]-এ `thinking_tokens` key-তেও। এগুলোর বিল হয় `output_tokens`-এর ভেতরেই, তাই এগুলো output মোটের একটি পড়ার মতো অংশ — বাড়তি যোগ নয়; আর কোনো response-এ thinking token ব্যবহার না হলে key-টি পুরোপুরি বাদ যায়।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `AnthropicModel('claude-sonnet-4-5')` | পুরোনো একটি Claude মডেল, যেটি budget-ভিত্তিক thinking নেয় |
| `'type': 'enabled'` | extended thinking চালু |
| `'budget_tokens': 1024` | ভাবার জন্য সর্বোচ্চ 1024 token |
| `max_tokens` | না দিলে Pydantic AI নিজেই budget + অন্তত 4096 পর্যন্ত বাড়ায় |

///

### Carried-over thinking { #carried-over-thinking }

যে reasoning Anthropic-এর native reasoning channel দিয়ে যেতে পারে না — কখন এমন হয় তা দেখুন [message history-তে thinking](#thinking-in-message-history)-এ — সেটি text হিসেবে পাঠানো হয়, তবে যে turn-এ তৈরি হয়েছিল সেখান থেকে নয়। Claude-এর *নিজের* reasoning-ও এই পথে যায় যখনই তার signature টিকে থাকেনি — আর সেটিই সাধারণ ঘটনা: যে history আপনার storage-এ ঘুরে এসেছে।

/// warning | assistant turn-এ যে ফরম্যাট দেখে, Claude তা নকল করে

ওই text assistant turn-এ পাঠালে Claude শিখে ফেলে যে thinking tag লেখা তার নিজের "লেখার ধরন"-এর অংশ, আর সে আপনার ব্যবহারকারীরা যে উত্তর পড়ে তাতেও সেগুলো লিখতে শুরু করে — আর history-তে সংরক্ষিত হওয়ার পর প্রতি turn-এ এটি নিজেকেই আরও জোরালো করে।

তাই যে মডেলগুলোর profile [`mimics_assistant_message_formatting`][pydantic_ai.profiles.ModelProfile.mimics_assistant_message_formatting] সেট করে, সেগুলোর জন্য Pydantic AI এমন reasoning বহন করে *assistant turn-এর আগে একটি user message-এ* — এতে নকল করা বন্ধ হয়। পুরো Anthropic family-র জন্য এই flag সেট করা, আর [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel] ও [`BedrockConverseModel`][pydantic_ai.models.bedrock.BedrockConverseModel] এটি মেনে চলে।

user message-এ পাঠানো reasoning পড়লে মনে হবে যেন এটি আপনার ভাবনা, তাই এটি মডেলের নিজের thinking tag-এ নয়, একটি `<assistant_thinking>` tag-এ মোড়ানো হয়। tag-টিতে কোনো attribute নেই, তাই কোনো [UI adapter](../ui/overview.md) দিয়ে ফিরে আসা history একইভাবে render হয় আর [prompt cache](../models/anthropic.md#prompt-caching) অক্ষত থাকে। tag-টি প্রতিটি request-এর জন্য render হয়, কখনো আপনার message history-তে সংরক্ষিত হয় না; আর reasoning-এর ভেতরে কোনো `</assistant_thinking>` থাকলে সেটি escape করা হয়, যাতে block আগেভাগে শেষ না হয়ে যায়। এর বিনিময় (trade-off) হলো, carried reasoning কে লিখেছে Claude তা বুঝতে পারে না, আর জিজ্ঞেস করলে নিজের বলে দাবি করে (`claude-opus-4-5`-এ মাপা)।

বরং assistant turn-এই পাঠাতে চাইলে, আপনার মডেলের জন্য flag-টি বন্ধ করুন:

⟦CODE7⟧

///

/// tip | উদাহরণ দিয়ে বুঝি

শিশুর সামনে বড়রা যেভাবে কথা বলে, শিশু সেভাবেই বলা শেখে। Claude-এর আগের উত্তরে (assistant turn-এ) thinking tag দেখলে সে ভাবে "আমি তো এভাবেই লিখি" — আর পরের উত্তরেও tag লিখে ফেলে। তাই Pydantic AI ওই পুরোনো ভাবনাগুলো Claude-এর মুখে না বসিয়ে, আলাদা একটি "চিরকুট" (user message-এ `<assistant_thinking>`) হিসেবে হাতে দেয়।

///

### Interleaved Thinking { #interleaved-thinking }

[interleaved thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking) চালু করতে model settings-এ beta header যোগ করতে হবে:

⟦CODE8⟧

### Adaptive Thinking ও Effort { #adaptive-thinking-effort }

`claude-opus-4-6` থেকে Anthropic [adaptive thinking](https://docs.anthropic.com/en/docs/build-with-claude/adaptive-thinking) সাপোর্ট করে — এখানে মডেল প্রতিটি request কতটা জটিল তা দেখে নিজেই ঠিক করে কখন আর কতটা ভাববে। এটি extended thinking-এর (`type: 'enabled'`, সাথে `budget_tokens`) জায়গা নেয়, যা Opus 4.6-এ deprecated আর Opus 4.7, 4.8, 5, 5.5, Sonnet 5 ও 5.5, এবং Haiku 5.5-এ সরিয়ে ফেলা হয়েছে। Claude Opus 4.7, 4.8, 5, 5.5, Sonnet 5 ও 5.5, এবং Haiku 5.5 এর সাথে `xhigh` effort level-ও যোগ করে। একীভূত `thinking='max'` পাঠায় `effort='max'`, যা Claude Opus 4.5 ছাড়া effort সেটিংওয়ালা প্রতিটি Claude মডেল নেয়। adaptive thinking স্বয়ংক্রিয়ভাবে interleaved thinking-ও চালু করে।

Claude Opus 5 ও পরের মডেল, Claude Sonnet 5, Haiku 5.5, আর Claude Fable ও Mythos মডেলগুলো কোনো thinking সেটিং ছাড়াই adaptive-ভাবে ভাবে। Claude Opus 5, Sonnet 5 আর Haiku 5.5-এ একীভূত `thinking=False` সেটিং `anthropic_thinking={'type': 'disabled'}` পাঠিয়ে সেটি বন্ধ করে, আর Claude Sonnet 5.5-এ পাঠায় `{'type': 'between_tools'}`। Claude Opus 5.5 আর Fable ও Mythos মডেলগুলো thinking বন্ধ করতে পারে না, তাই `thinking=False` সবচেয়ে কম effort `low`-এ adaptive thinking পাঠায়; Claude Mythos Preview-এর কোনো effort সেটিং নেই, তাই সেটি নিজের ডিফল্টেই থাকে। forced tool choice Claude-কে ভাবতে দেয় না বলে, এই মডেলগুলোতে structured `output_type` Tool Output-এর বদলে Native Output ব্যবহার করে — যদি না thinking বন্ধ থাকে; দেখুন [Forced tool choice](../models/anthropic.md#forced-tool-choice)।

/// note | thinking বন্ধ থাকলে Claude Opus 5, Sonnet 5.5 আর Haiku 5.5 effort সীমিত করে

`thinking=False` বা `anthropic_thinking={'type': 'disabled'}` দিয়ে thinking বন্ধ থাকলে Claude Opus 5 আর Haiku 5.5 `xhigh` ও `max` effort প্রত্যাখ্যান করে; Claude Sonnet 5.5-ও তাই করে `thinking=False` বা `anthropic_thinking={'type': 'between_tools'}`-এর সাথে। `high` বা তার নিচের effort ব্যবহার করুন, অথবা thinking চালু রাখুন। Claude Opus 4.8 এই সমন্বয় মেনে নেয়, তাই migrate করার সময় যে request-গুলো thinking বন্ধ করে সেগুলো যাচাই করুন। Anthropic-এর 400 দেখানোর বদলে Pydantic AI request পাঠানোর আগেই একটি `UserError` raise করে।

///

/// note | Claude Opus 5.5 সবসময় ভাবে

Claude Opus 5.5 thinking বন্ধ করতে পারে না: Anthropic যেকোনো effort level-এ `anthropic_thinking={'type': 'disabled'}` প্রত্যাখ্যান করে। একীভূত `thinking=False` সেটিং বরং `low` effort-এ adaptive thinking পাঠায় — মডেলটি যতটা কম ভাবা মেনে নেয়, ততটাই।

///

/// note | Claude Sonnet 5.5 `between_tools` দিয়ে শুরুর thinking বন্ধ করে

Claude Sonnet 5.5 `anthropic_thinking={'type': 'disabled'}` প্রত্যাখ্যান করে। এর সবচেয়ে নিচের সেটিং হলো `anthropic_thinking={'type': 'between_tools'}`, যা শুরুর (up-front) thinking বাদ দেয় আর শুধু tool call-গুলোর মাঝে মডেল যে ছোট অগ্রগতি-নোট লেখে সেগুলো রাখে। Anthropic এটি শুধু `low`, `medium` আর `high` effort-এ মেনে নেয়। একীভূত `thinking=False` সেটিং `between_tools` পাঠায়।

adaptive thinking-এ Claude Sonnet 5.5 tool call-এর মাঝে লেখা নোটগুলো text হিসেবে নয়, thinking block হিসেবে ফেরত দেয়, আর Anthropic-এর ডিফল্ট `display: 'omitted'`-এ সেগুলো খালি অবস্থায় আসে। দেখাতে চাইলে `anthropic_thinking={'type': 'adaptive', 'display': 'summarized'}` সেট করুন; `between_tools` এগুলো এটি ছাড়াই ফেরত দেয়।

///

⟦CODE9⟧

[`anthropic_effort`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_effort] সেটিং নিয়ন্ত্রণ করে মডেল তার response-এ কতটা effort দেবে (thinking থেকে স্বাধীনভাবে)। বিস্তারিত জানতে দেখুন [Anthropic effort docs](https://docs.anthropic.com/en/docs/build-with-claude/effort)।

/// note | মনে রাখুন

পুরোনো মডেলগুলো (`claude-sonnet-4-5`, `claude-opus-4-5` ইত্যাদি) adaptive thinking সাপোর্ট করে না, আর [ওপরে](#anthropic) দেখানো মতো `{'type': 'enabled', 'budget_tokens': N}` চায়।

///

thinking token Anthropic-এর পুরো-loop জুড়ে [task budget](../models/anthropic.md#task-budgets-beta)-এর মধ্যে গোনা হয়, তাই budget ফুরিয়ে আসার সাথে সাথে adaptive thinking স্বাভাবিকভাবেই কমে আসে।

/// info | এক নজরে: Claude মডেলে `thinking=False` কী পাঠায়

| মডেল | `thinking=False`-এর ফল |
|---|---|
| Opus 5, Sonnet 5, Haiku 5.5 | `{'type': 'disabled'}` — thinking বন্ধ |
| Sonnet 5.5 | `{'type': 'between_tools'}` — শুরুর thinking বন্ধ, মাঝের নোট থাকে |
| Opus 5.5, Fable, Mythos | বন্ধ করা যায় না → `low` effort-এ adaptive |
| Mythos Preview | effort সেটিং নেই → কিছুই পাঠানো হয় না |

///

## Google { #google }

অ্যাডভান্সড ব্যবহারের জন্য [`GoogleModelSettings.google_thinking_config`][pydantic_ai.models.google.GoogleModelSettings.google_thinking_config] [model setting](../agent.md#model-run-settings) ব্যবহার করুন।

⟦CODE10⟧

আরও বিস্তারিত জানতে দেখুন [Google model docs](../models/google.md#configure-thinking)।

## xAI { #xai }

xAI-এর reasoning মডেলগুলো (Grok) native thinking সাপোর্ট করে। একাধিক turn-এর কথোপকথনে thinking content ধরে রাখতে [`XaiModelSettings.xai_include_encrypted_content`][pydantic_ai.models.xai.XaiModelSettings.xai_include_encrypted_content] চালু করুন।

⟦CODE11⟧

## Bedrock { #bedrock }

Claude Sonnet 4.6+, Opus 4.6+ আর Haiku 5.5-এর জন্য Pydantic AI-এর একীভূত `thinking` সেটিং স্বয়ংক্রিয়ভাবে AWS-এর প্রয়োজনীয় [adaptive thinking](https://docs.aws.amazon.com/bedrock/latest/userguide/claude-messages-adaptive-thinking.html) আকারে রূপান্তরিত হয় — [`ModelSettings.thinking`][pydantic_ai.settings.ModelSettings.thinking] সেট করলেই কাজ শেষ।

Bedrock দিয়ে চালানো Claude Anthropic model profile উত্তরাধিকারসূত্রে পায়, তাই history থেকে আবার পাঠানো reasoning এখানেও [Carried-over thinking](#carried-over-thinking) মেনে চলে।

পুরোনো Claude মডেলের জন্য, বা নির্দিষ্ট একটি `budget_tokens` বেঁধে দিতে চাইলে, এখনও [`BedrockModelSettings.bedrock_additional_model_requests_fields`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_additional_model_requests_fields] [model setting](../agent.md#model-run-settings) দিয়ে provider-ভিত্তিক কনফিগারেশন সরাসরি পাঠাতে পারেন:

/// tab | Claude

⟦CODE12⟧

///
/// tab | OpenAI

⟦CODE13⟧

///
/// tab | Qwen

⟦CODE14⟧

///

/// tab | Deepseek

DeepSeek মডেলে reasoning [সবসময় চালু](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-reasoning.html) থাকে।

⟦CODE15⟧

///

## Groq { #groq }

Groq thinking part পাওয়ার জন্য কয়েকটি আলাদা ফরম্যাট সাপোর্ট করে:

- `"raw"`: thinking part text content-এর ভেতরে `<think>` tag-এ থাকে, যা স্বয়ংক্রিয়ভাবে [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] object-এ রূপান্তরিত হয়।
- `"hidden"`: thinking part text content-এ থাকে না।
- `"parsed"`: response-এ thinking part-এর নিজস্ব structured part থাকে, যা একটি [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] object-এ রূপান্তরিত হয়।

একীভূত [`ModelSettings.thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং সব provider-এ কাজ করে: এটি `reasoning_format='parsed'` বেছে নেয় যাতে thinking part ফেরত আসে, আর gpt-oss family-র ক্ষেত্রে এর effort level Groq-এর `reasoning_effort`-ও চালায় (`minimal`/`low` → `'low'`, `medium` → `'medium'`, `high`/`xhigh`/`max` → `'high'`, `True` → `'medium'`)।

দুটি একসাথে-ব্যবহারযোগ্য [model settings](../agent.md#model-run-settings) আরও সূক্ষ্ম নিয়ন্ত্রণ দেয়: [`GroqModelSettings.groq_reasoning_format`][pydantic_ai.models.groq.GroqModelSettings.groq_reasoning_format] বেছে নেয় thinking part কীভাবে ফেরত আসবে (ওপরের ফরম্যাটগুলো), আর [`GroqModelSettings.groq_reasoning_effort`][pydantic_ai.models.groq.GroqModelSettings.groq_reasoning_effort] (Groq-এ `reasoning_effort` হিসেবে যায়) নিয়ন্ত্রণ করে মডেল কতটা reasoning করবে — এটি একীভূত `thinking` mapping-এর চেয়ে অগ্রাধিকার পায়:

⟦CODE16⟧

/// note | মনে রাখুন

বেশিরভাগ Groq reasoning মডেল সত্যিকার অর্থে thinking বন্ধ করা সাপোর্ট করে না। একীভূত সেটিং দিয়ে `thinking=False` দিলে আচরণ family অনুযায়ী আলাদা: qwen3 family `reasoning_effort='none'` দিয়ে সত্যিই reasoning বন্ধ করে (আর qwen3-এ একটি স্পষ্ট `groq_reasoning_effort`-এর সাথে মিললে বন্ধ করাটাই জেতে, `groq_reasoning_effort` উপেক্ষিত হয়, সাথে একটি warning); gpt-oss family সবসময় reasoning করে আর তা বন্ধ করা যায় না, তাই `thinking=False` এর সবচেয়ে কম effort `reasoning_effort='low'` পাঠায়, সাথে `reasoning_format='hidden'`, যাতে reasoning response-এর বাইরে থাকে।

///

/// note | মনে রাখুন

গ্রহণযোগ্য `reasoning_effort` মান family অনুযায়ী আলাদা (দেখুন [Groq docs](https://console.groq.com/docs/reasoning#reasoning-effort)): gpt-oss family নেয় `'low'`, `'medium'` আর `'high'`, তাই একীভূত `thinking` effort level-গুলো সেগুলোতে map হয়; qwen3 family শুধু `'none'` আর `'default'` নেয়, তাই সেখানে একীভূত চালু-level-গুলো `reasoning_format` নিয়ন্ত্রণ করে কিন্তু কোনো `reasoning_effort` পাঠায় না (map করার মতো কোনো ধাপ নেই)। একটি স্পষ্ট `groq_reasoning_effort` একীভূত mapping-এর চেয়ে অগ্রাধিকার পায় — ব্যতিক্রম শুধু qwen3 family, যেখানে `thinking=False` তবুও জেতে আর `reasoning_effort='none'` পাঠায়।

///

/// info | এক নজরে: Groq-এর দুই family

| family | effort মান | `thinking=False` |
|---|---|---|
| gpt-oss | `'low'`, `'medium'`, `'high'` | বন্ধ হয় না → `'low'` + `reasoning_format='hidden'` |
| qwen3 | শুধু `'none'`, `'default'` | সত্যিই বন্ধ → `reasoning_effort='none'` |

///

## OpenRouter { #openrouter }

thinking চালু করতে [`OpenRouterModelSettings.openrouter_reasoning`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_reasoning] [model setting](../agent.md#model-run-settings) ব্যবহার করুন।

⟦CODE17⟧

/// note | wire ফরম্যাটের খুঁটিনাটি

truthy [`thinking`][pydantic_ai.settings.ModelSettings.thinking] মান wire-এ `effort` আর `enabled: True` দুটোই পাঠায়। যে মডেলগুলো ডিফল্টভাবেই reasoning করে, সেখানে স্পষ্ট `enabled: True`-এর কোনো প্রভাব নেই; কিন্তু reasoning-ঐচ্ছিক route-গুলোর (যেমন `google/gemma-*` family-র কিছু অংশ) জন্য এটি জরুরি, কারণ না দিলে `effort` সেট থাকা সত্ত্বেও তারা reasoning বন্ধ রাখে।

[`thinking=False`][pydantic_ai.settings.ModelSettings.thinking] পাঠায় `reasoning={'effort': 'none'}` — এটি [OpenRouter-এর নথিভুক্ত বন্ধ করার সংকেত](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens) — সেই route-গুলোতে যাদের upstream বন্ধ করা মানতে পারে (যেমন `anthropic/claude-sonnet-4.5`, `z-ai/glm-4.6`)। যে route-গুলোর upstream reasoning বন্ধ করতে পারে না (যেমন `openai/o3`, `openai/gpt-5`, `deepseek/deepseek-r1-0528`), সেখানে OpenRouter `effort='none'` প্রত্যাখ্যান করে ("Reasoning is mandatory"), তাই `thinking=False` বরং `reasoning={'effort': 'low'}` পাঠায় — route-টি যতটা কম reasoning দেয়, ততটাই। `anthropic/claude-sonnet-5.5`-এর ক্ষেত্রেও একই: OpenRouter এর reasoning বাধ্যতামূলক করে রেখেছে, আর Anthropic API-র `between_tools`-এর মতো কিছু তার নেই। প্রতি route-এ স্পষ্ট নিয়ন্ত্রণ চাইলে [`OpenRouterModelSettings.openrouter_reasoning`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_reasoning] সরাসরি সেট করুন।

///

## Z.AI { #zai }

thinking চালু করতে একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] [model setting](../agent.md#model-run-settings) ব্যবহার করুন। একাধিক turn-এর কথোপকথনে thinking content ধরে রাখতে [`ZaiModelSettings.zai_clear_thinking`][pydantic_ai.models.zai.ZaiModelSettings.zai_clear_thinking]-ও `False`-এ সেট করুন।

⟦CODE18⟧

## GitHub Copilot { #github-copilot }

Copilot একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিংটি `reasoning_effort` হিসেবে নেয়, যা [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] থেকে উত্তরাধিকারসূত্রে পাওয়া। কোনো নির্দিষ্ট id এটি নেয় কি না, আর কোন level-গুলো নেয় — এটি প্রতি-মডেলের তথ্য, যা Copilot নিজের catalog-এ জানায় আর নিজেই প্রয়োগ করে; [`GitHubCopilotModel`][pydantic_ai.models.github_copilot.GitHubCopilotModel] নিজের কোনো বাধা যোগ করে না।

Copilot-এর Anthropic আর Google id-গুলো তাদের reasoning একটি অপ্রচলিত `reasoning_text` field-এ ফেরত দেয়, যা Pydantic AI একটি [`ThinkingPart`][pydantic_ai.messages.ThinkingPart]-এ map করে আর পরের turn-গুলোতে সেই field-এই ফেরত পাঠায়। এর OpenAI আর MoonshotAI id-গুলো সেটিংটি নেয় আর সেই অনুযায়ী reasoning-ও করে, কিন্তু Copilot তাদের জন্য কোনো reasoning text ফেরত দেয় না, তাই সেগুলো কোনো `ThinkingPart` দেয় না। Anthropic id-গুলো এর ওপর adaptive-ভাবেও ভাবে, তাই effort একটি নির্দেশ নয়, বরং ঊর্ধ্বসীমা — সহজ প্রশ্নের উত্তর কোনো reasoning ছাড়াই আসতে পারে। এদের `reasoning_effort` তালিকায় `none`-ও নেই, তাই `thinking=False` `reasoning_effort='none'` হিসেবে যায় আর Copilot উত্তর দেয় `400 invalid_reasoning_effort`। দেখুন [GitHub Copilot](../models/github-copilot.md#thinking)।

/// warning | সাধারণ ভুল

GitHub Copilot-এর `claude-` বা `gemini-` id-তে `thinking=False` দিলে `400 invalid_reasoning_effort` আসে — কারণ Pydantic AI এখানে নিজে কিছু আটকায় না, Copilot নিজেই প্রত্যাখ্যান করে। এই id-গুলোতে thinking কমাতে চাইলে `False`-এর বদলে সবচেয়ে কম যে level id-টি নেয়, সেটি দিন।

///

## Snowflake Cortex { #snowflake-cortex }

Claude মডেলে thinking চালু করতে একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] [model setting](../agent.md#model-run-settings) ব্যবহার করুন, অথবা reasoning token budget নিয়ন্ত্রণ করতে সরাসরি [`SnowflakeModelSettings.snowflake_reasoning`][pydantic_ai.models.snowflake.SnowflakeModelSettings.snowflake_reasoning] সেট করুন:

⟦CODE19⟧

OpenAI মডেলে একীভূত `thinking` সেটিং বা [`openai_reasoning_effort`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_reasoning_effort] ব্যবহার করুন।

thinking চালু থাকলে Claude চায় `temperature` ঠিক 1 হোক, কিন্তু request-এ না থাকলে Cortex অন্য একটি ডিফল্ট বসায় — তাই reasoning চালু থাকলে আর আপনি নিজে `temperature` সেট না করলে `SnowflakeModel` স্বয়ংক্রিয়ভাবে `temperature` 1-এ সেট করে।

## Mistral { #mistral }

Mistral নিচের adjustable-reasoning মডেলগুলোর পক্ষে `magistral` family-কে [deprecated](https://docs.mistral.ai/resources/deprecated/native-reasoning) করেছে: `magistral-medium-latest` আর `magistral-small-latest` এখন Mistral Medium 3.5 আর Small 4-কে নির্দেশ করে, আর শুধু চাইলে reasoning করে। তারিখযুক্ত `magistral` id-গুলো সবসময় reasoning করত আর কোনো reasoning সেটিং দিত না, তাই `thinking` তাদের জন্য কিছুই পাঠায় না।

adjustable reasoning-ওয়ালা মডেলগুলো (Mistral Large 4, Small 4 আর Medium 3.5 family: `mistral-large-4`, `mistral-large-4-0`, `mistral-small-latest`, `mistral-small-2603`, `mistral-medium-latest`, `mistral-medium`, `mistral-medium-3`, `mistral-medium-3-5`, `mistral-medium-3.5`, `mistral-medium-2604`, `magistral-medium-latest`, `magistral-small-latest`) একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং দিয়ে নিয়ন্ত্রিত হয়, যা Mistral-এর `reasoning_effort`-এ map হয়। Mistral শুধু `'high'` (পূর্ণ thinking) আর `'none'` (thinking বন্ধ) দেয়, তাই প্রতিটি চালু level `'high'`-এ map হয় আর শুধু `thinking=False` `'none'`-এ। পুরোনো `mistral-small-*` / `mistral-medium-*` snapshot আর `mistral-large-latest` reasoning সাপোর্ট করে না, তাই তাদের জন্য `thinking` নীরবে উপেক্ষিত হয়। adjustable reasoning প্রযোজ্য শুধু native Mistral provider ব্যবহার করলে; যে OpenAI-compatible provider-গুলো এই মডেলগুলো চালায় (যেমন LiteLLM বা Azure), সেগুলো এটি সাপোর্ট করে না আর সেখানে `thinking` উপেক্ষিত হয়। OpenRouter ব্যতিক্রম: এটি যেকোনো মডেলে route করার সময় একীভূত `thinking` সেটিংকে নিজের `reasoning` parameter-এ map করে।

## Cohere { #cohere }

Thinking সাপোর্ট করে `command-a-reasoning-08-2025` মডেল, যা ডিফল্টভাবেই ভাবে। একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং Cohere-এর [`thinking` parameter](https://docs.cohere.com/docs/reasoning)-এ map হয়: `thinking=False` `type='disabled'` দিয়ে reasoning বন্ধ করে, আর একটি effort level একটি `token_budget` দিয়ে সেটির সীমা বাঁধে (`'minimal'` → 512 token, `'low'` → 2048, `'medium'` → 8192, `'high'` → 16384, `'xhigh'` আর `'max'` → 31000)।

## Hugging Face { #hugging-face }

`<think>` tag-এর ভেতরের text output স্বয়ংক্রিয়ভাবে [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] object-এ রূপান্তরিত হয়।
[model profile](../models/compatible-apis.md#model-profile)-এর [`thinking_tags`][pydantic_ai.profiles.ModelProfile.thinking_tags] field দিয়ে tag-গুলো নিজের মতো বদলাতে পারেন।

/// check | সংক্ষেপে মনে রাখুন

* সবচেয়ে সহজ পথ: `capabilities=[Thinking(effort='high')]` বা `model_settings={'thinking': 'high'}` — সব provider-এ একই কোড।
* `True` = ডিফল্ট effort, `False` = বন্ধ (না পারলে সবচেয়ে কম), level নাম = নির্দিষ্ট effort (না থাকলে নিকটতম)।
* provider-ভিত্তিক সেটিং (যেমন `anthropic_thinking`, `openai_reasoning_effort`) একীভূত `thinking`-এর চেয়ে অগ্রাধিকার পায়।
* `output_reasoning_tokens` হলো `output_tokens`-এর অংশ, আলাদা যোগ নয়।
* `ThinkingPart` history থেকে ফেরত যায়; signature হারালে text হিসেবে যায় — Claude-এর বেলায় user message-এ `<assistant_thinking>` tag-এ।
* মাঝপথে effort বদলানো OpenAI Responses (GPT-6) আর নতুন Claude মডেলে prompt cache না ভেঙে হয়।
* নতুন Claude মডেলে budget-ভিত্তিক extended thinking নেই — adaptive thinking আর effort ব্যবহার করুন।

///
