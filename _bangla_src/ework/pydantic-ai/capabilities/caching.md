
# Caching { #caching }

/// note | এই পেজে যা শিখবেন

* prompt caching কী, কেন agent run-এ এটি এত টাকা বাঁচায়, আর "prefix" মানে কী।
* `Caching` capability দিয়ে এক লাইনে caching চালু করা, retention আর `messages=False`।
* প্রতিটি provider (Anthropic, Bedrock, OpenAI, OpenRouter, Google…) কীভাবে cache করে।
* খরচের হিসাব, কী cache ভেঙে দেয়, আর cache কাজ করছে কি না কীভাবে মাপবেন।

///

Prompt caching provider-কে সাম্প্রতিক দেখা একটি request-এর শুরুর অংশে (tool definition, instructions আর এ পর্যন্ত কথোপকথন) করা কাজ আবার প্রসেস না করে পুনরায় ব্যবহার করতে দেয় — এতে লম্বা আর একাধিক turn-এর request সস্তা আর দ্রুত হয়। যেহেতু [agent run](../agent.md#running-agents) প্রতিটি ধাপে পুরো কথোপকথন আবার পাঠায়, caching প্রায়ই এই পার্থক্য গড়ে দেয়: history-র জন্য একবার টাকা দেবেন, নাকি প্রতিটি turn-এ।

cache hit মানে বর্তমান request-এর একটি অপরিবর্তিত শুরুর অংশ — এর *prefix* — পুনরায় ব্যবহার করা, যা provider আগের একটি request থেকে cache করেছিল। provider একটি request একটি নির্দিষ্ট ক্রমে পড়ে: আগে tool definition, তারপর system prompt, তারপর message। নতুন message শেষে যোগ করলে cache করা prefix ব্যবহারযোগ্য থাকে, কিন্তু আগের কিছু বদলালে সেই বিন্দু থেকে cache অকেজো হয়ে যায়, আর তার পরের সবকিছুর জন্য আবার টাকা লাগে।

**আপনার agent-এ [`Caching`][pydantic_ai.capabilities.Caching] capability যোগ করুন।** কয়েকটি provider request না চাইলে কিছুই cache করে না, তাই এটি ছাড়া একটি agent প্রতিটি request-এ তার instructions, tool আর কথোপকথনের জন্য পুরো দাম দেয়। caching ডিফল্টভাবে চালু নয়, কারণ এটি request-এর খরচ বদলে দেয়: cache-এ লেখার খরচ cache-ছাড়া input-এর চেয়ে বেশি, তাই যে request-এর prefix কখনো আবার পড়া হয় না, caching-সহ তার খরচ caching ছাড়ার চেয়ে বেশি। যে agent মূলত লম্বা instructions বা tool শেয়ার করা এককালীন request করে, তার জন্য [শুধু স্থির prefix cache করুন](#caching-only-the-stable-prefix)।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন প্রতিবার শিক্ষকের কাছে প্রশ্ন নিয়ে গেলে আপনাকে পুরো বইটা আবার পড়ে শোনাতে হয়। caching মানে শিক্ষক বইটা একবার পড়ে মনে রাখেন (cache write — একটু বেশি খরচ), পরের বার আপনি শুধু নতুন প্রশ্নটা বলেন (cache read — খুব সস্তা)। কিন্তু বইয়ের প্রথম পাতায় একটা শব্দ বদলালে শিক্ষককে সেখান থেকে বাকি সব আবার পড়তে হয় — তাই prefix (শুরুর অংশ) স্থির রাখাই আসল কৌশল।

///

## একীভূত caching সেটিং { #unified-caching-settings }

caching চালু করতে [`Caching`][pydantic_ai.capabilities.Caching] capability ব্যবহার করুন:

⟦CODE1⟧

[`ModelSettings`][pydantic_ai.settings.ModelSettings]-এর `cache` field দিয়ে এর সমতুল্য হলো `model_settings={'cache': True}`।

এটি কী করে, তা নির্ভর করে provider কীভাবে cache করে তার ওপর:

| `Caching()` ছাড়া | Provider | `Caching()`-সহ |
|---|---|---|
| কিছুই cache হয় না | Anthropic (Bedrock, Vertex AI আর Microsoft Foundry-তেও), Bedrock-এর Claude আর Nova মডেল, OpenRouter-এর Anthropic মডেল | tool definition, instructions আর কথোপকথন cache হয় |
| নিজে থেকেই (implicitly) cache হয় | OpenAI GPT-5.6 ও পরের মডেল, OpenRouter-এ Gemini 2.5 ও পরের মডেল | এর ওপর স্পষ্ট breakpoint যোগ হয়, যেমন instructions-এর পরে একটি, যাতে আলাদা কথোপকথনগুলো সেটি শেয়ার করে |
| নিজে থেকেই cache হয় | GPT-5.6-এর আগের OpenAI মডেল, Gemini, DeepSeek, xAI | কোনো প্রভাব নেই |

request-গুলো cache থেকে পড়ছে কি না নিশ্চিত হতে দেখুন [cache-এর কার্যকারিতা পর্যবেক্ষণ](#monitoring-cache-efficiency)।

### caching কনফিগার করা { #configuring-caching }

[`Caching.retention`][pydantic_ai.capabilities.Caching.retention] এই মানগুলো নেয়:

- `True` (capability-র ডিফল্ট) — provider-এর ডিফল্ট retention-এ cache করে
- `False` — library-পরিচালিত caching বন্ধ করে, যেমন মডেলের ডিফল্ট settings-এর একটি `cache` মান override করতে
- `'5m'` / `'30m'` / `'1h'` — একটি নির্দিষ্ট retention-এ cache করে, provider-এর সাপোর্ট করা নিকটতম স্তরে মিলিয়ে: ছোট স্তর থাকলে নিচে (`'30m'` Anthropic-এ `'5m'` হয়, যেখানে 5 মিনিট আর 1 ঘণ্টা আছে), নইলে সবচেয়ে ছোটটিতে ওপরে (OpenAI GPT-5.6 ও পরের মডেলে প্রতিটি মান `'30m'` হয়)

Retention, বা TTL (time to live), হলো শেষ ব্যবহারের পর provider একটি cache করা prefix কতক্ষণ রাখে। ডিফল্ট দিয়ে শুরু করুন। কথোপকথন যখন প্রায়ই শেষ request-এর পাঁচ মিনিটেরও বেশি পরে চলতে থাকে, তখন Anthropic-এর `'1h'` বিবেচনা করুন: এর cache write-এর খরচ বেশি, তাই cache-ছাড়া input-কে হারাতে একটি prefix-কে অন্তত দুবার পড়তে হয় (দেখুন [খরচ](#cost))।

ভেতরের `cache` model setting-ও ঠিক এই মানগুলো নেয়, যা ডিফল্টভাবে সেট করা থাকে না। provider-নির্দিষ্ট cache সেটিং, যেমন `anthropic_cache` বা `bedrock_cache_instructions`, অগ্রাধিকার পায়: এগুলোর যেকোনোটি সেট থাকলে (`False`-সহ), সেই request-এর জন্য একীভূত সেটিং উপেক্ষিত হয়।

`cache=False` Pydantic AI-এর পরিচালিত caching বন্ধ করে। message history-তে আপনার যোগ করা [`CachePoint`][pydantic_ai.messages.CachePoint] চিহ্ন আর provider-নির্দিষ্ট cache সেটিং তবুও প্রযোজ্য, আর যে provider নিজে থেকেই cache করে সেগুলো তবুও করে।

/// warning | সাধারণ ভুল

`Caching()` যোগ করেছেন, সাথে পুরোনো কোডে `anthropic_cache_instructions=True`-ও আছে? তাহলে একীভূত সেটিং পুরো request-এর জন্য উপেক্ষিত হয় — শুধু instructions cache হবে, tool বা কথোপকথন নয়। একটি পথ বেছে নিন: হয় শুধু `Caching()`, নয়তো provider-নির্দিষ্ট সব সেটিং নিজে।

///

### শুধু স্থির prefix cache করা { #caching-only-the-stable-prefix }

ডিফল্টভাবে caching ঢাকে tool definition, স্থির instructions আর কথোপকথন। একটি agent যখন অনেক ছোট, এককালীন কথোপকথন সামলায় যেগুলো লম্বা instructions বা tool শেয়ার করে, তখন প্রতিটি কথোপকথন cache-এ লেখার খরচ বাঁচানোর চেয়ে বেশি, কারণ সেটি কখনো আবার পড়া হয় না। শুধু স্থির prefix cache করতে `messages=False` দিন:

⟦CODE2⟧

যে provider-এ `Caching()`-এর কোনো প্রভাব নেই, সেখানে `messages=False`-এরও নেই: এটি তাদের নিজে থেকে করা caching বন্ধ করে না। `cache` model setting একই option নেয় একটি [`CacheConfig`][pydantic_ai.settings.CacheConfig] হিসেবে, সাথে একটি ঐচ্ছিক retention:

⟦CODE3⟧

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `handbook` instructions-এ | লম্বা, সব প্রশ্নে একই — স্থির prefix |
| `Caching(messages=False)` | শুধু tool আর instructions cache হয়, প্রতিটি কথোপকথন নয় |
| দুটি আলাদা `run_sync` | দ্বিতীয়টি handbook cache থেকে পড়ে; প্রশ্নগুলো cache-এ লেখা হয় না |

///

### provider-এ রূপান্তর { #provider-translation }

Pydantic AI cache breakpoint — যে চিহ্ন caching-যোগ্য content-এর শেষ নির্দেশ করে — বসায় tool definition, স্থির instructions আর কথোপকথনের শেষে, তাই স্থির prefix কথোপকথনগুলোর মধ্যে শেয়ার হয় আর প্রতিটি request আগেরটির cache করা সবকিছু আবার পড়ে। যেখানে provider-এর একটি automatic caching mode আছে, সেখানে কথোপকথন একটি স্পষ্ট breakpoint-এর বদলে সেটি দিয়েই cache হয়। স্পষ্ট `CachePoint` একটি request-কে provider-এর breakpoint সীমার বাইরে ঠেলে দিলে, সবচেয়ে পুরোনো message breakpoint আগে বাদ পড়ে; OpenAI-তে, যা client-দিকে request ছাঁটে না, server বরং সবচেয়ে আগের breakpoint-গুলো আগে বাদ দেয়, instruction breakpoint দিয়ে শুরু করে (দেখুন [OpenAI prompt caching](../models/openai.md#prompt-caching))।

| Provider | `Caching()` | `Caching('1h')` | `Caching(messages=False)` | নোট |
|---|---|---|---|---|
| Anthropic API, Vertex AI, Microsoft Foundry, Bedrock Messages API, আর legacy `AsyncAnthropicBedrock` client — যে মডেলগুলো এটি সাপোর্ট করে বলে নথিভুক্ত | `anthropic_cache`, `anthropic_cache_instructions` আর `anthropic_cache_tool_definitions` `'5m'`-এ সেট | একই, `'1h'`-এ সেট | `anthropic_cache` ছাড়া | |
| legacy `AsyncAnthropicBedrock` client-এ অন্য মডেলে Anthropic | `anthropic_cache_instructions`, `anthropic_cache_tool_definitions` আর `anthropic_cache_messages` `'5m'`-এ সেট | একই, `'1h'`-এ সেট | `anthropic_cache_messages` ছাড়া | যে মডেলগুলোকে AWS 1-ঘণ্টার TTL দেয় না, সেখানে `'1h'` `'5m'`-এ নামে |
| Bedrock (Claude আর Nova) | `bedrock_cache_instructions`, `bedrock_cache_tool_definitions` আর `bedrock_cache_messages` `True`-তে সেট | একই, `'1h'`-এ সেট | `bedrock_cache_messages` ছাড়া | যে মডেলগুলোকে AWS 1-ঘণ্টার TTL দেয় না, সেখানে `'1h'` `'5m'`-এ নামে |
| OpenRouter (Anthropic আর Gemini) | `openrouter_cache_instructions`, `openrouter_cache_tool_definitions` আর `openrouter_cache_messages` `'5m'`-এ সেট | একই, `'1h'`-এ সেট | `openrouter_cache_messages` ছাড়া | Gemini route কোনো tool definition breakpoint আর কোনো TTL নেয় না |
| OpenAI (GPT-5.6 ও পরের, OpenAI API-তে) | `openai_prompt_cache_options={'mode': 'implicit', 'ttl': '30m'}` আর `openai_cache_instructions=True` | একই | `mode='explicit'`, তাই শুধু instructions লেখা হয় | OpenAI শুধু `'30m'` TTL নেয়। যে request instruction breakpoint বহন করতে পারে না, যেমন server-দিকের state চালিয়ে যাওয়া request (`openai_previous_response_id` বা `openai_conversation_id`), সেগুলো `messages=False`-এর সাথে implicit breakpoint রাখে, তাই `Caching()`-এর মতো cache হয় |
| যে provider শুধু নিজে থেকে cache করে | কোনো প্রভাব নেই | কোনো প্রভাব নেই | কোনো প্রভাব নেই | যেমন Google আর GPT-5.6-এর আগের OpenAI মডেল |

### একীভূত সেটিংয়ের বাইরে যাওয়া { #going-beyond-the-unified-setting }

একীভূত সেটিং সাধারণ ক্ষেত্রগুলো সামলায়। আপনার যা দরকার তা এটি প্রকাশ করতে না পারলে নিচের স্তরের নিয়ন্ত্রণ ব্যবহার করুন:

- আপনার দেওয়া পুনঃব্যবহারযোগ্য context-এর পরে একটি user message-এ একটি [`CachePoint`][pydantic_ai.messages.CachePoint] যোগ করুন, যেমন একটি লম্বা document-এর পরে একটি পরিবর্তনশীল প্রশ্ন — তাহলে document-টি কথোপকথনের অংশ হলেও cache হয়।
- একীভূত সেটিং যে আচরণ ঢাকে না, তার জন্য provider-নির্দিষ্ট সেটিং ব্যবহার করুন, যেমন automatic caching সাপোর্ট করে না এমন gateway-এর জন্য Anthropic-এর [per-block message caching](../models/anthropic.md#per-block-message-caching), GPT-5.6-এর আগের মডেলে OpenAI-এর [retention policy](../models/openai.md#prompt-caching), বা Google-এর [cached content resource](../models/google.md#context-caching-google_cached_content)। যেহেতু একটি provider-নির্দিষ্ট সেটিং পুরো request-এর জন্য একীভূত সেটিংয়ের জায়গা নেয় (দেখুন [caching কনফিগার করা](#configuring-caching)), সেই provider-এ আপনার দরকারি প্রতিটি cache সেটিং সেট করুন।

## provider-রা কীভাবে cache করে { #how-providers-cache }

নিচের প্রতিটি অংশ একটি provider-এর নিজস্ব caching আচরণ আর তার provider-নির্দিষ্ট সেটিংয়ের সারাংশ দেয়। লিংক করা provider পেজগুলোতে সেই সেটিংগুলো বিস্তারিতভাবে আছে।

### Anthropic { #anthropic }

request কী cache করতে হবে তা চিহ্নিত না করলে Anthropic কিছুই cache করে না; ডিফল্ট TTL 5 মিনিট, আর চাইলে 1 ঘণ্টা। একটি request সর্বোচ্চ চারটি cache breakpoint বহন করে।

[`anthropic_cache`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache] Anthropic-এর [automatic caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching#automatic-caching) ব্যবহার করে, যা শেষ cache-যোগ্য block-এ breakpoint বসায় আর কথোপকথন বাড়ার সাথে সাথে এটিকে সামনে সরায়। Anthropic API, Vertex AI, Microsoft Foundry আর Bedrock Messages API (`AsyncAnthropicBedrockMantle` client) automatic caching সাপোর্ট করে; legacy `AsyncAnthropicBedrock` client-ও করে সেই মডেলগুলোতে, যেগুলো Anthropic Messages API infrastructure থেকে পরিবেশিত বলে [নথিভুক্ত](https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock-legacy#api-model-ids) করেছে। ওই client-এর অন্য মডেলে `anthropic_cache` শেষ user message-এ একটি breakpoint-এ ফিরে যায়। [`anthropic_cache_instructions`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_instructions], [`anthropic_cache_tool_definitions`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_tool_definitions] আর [`anthropic_cache_messages`][pydantic_ai.models.anthropic.AnthropicModelSettings.anthropic_cache_messages] প্রতি-block breakpoint বসায়, আর একটি user message-এ একটি [`CachePoint`][pydantic_ai.messages.CachePoint] স্পষ্টভাবে একটি চিহ্নিত করে।

বিস্তারিত জানতে দেখুন [Anthropic prompt caching](../models/anthropic.md#prompt-caching)।

### Bedrock { #bedrock }

Bedrock Converse API Claude আর Nova মডেলে স্পষ্টভাবে cache করে, ডিফল্ট 5-মিনিটের TTL-এ, আর AWS যে Claude মডেলগুলোকে দেয় সেগুলোতে 1-ঘণ্টার TTL-এ। Nova tool definition cache করে না। মডেলের ন্যূনতম token সীমার নিচের content cache হয় না, আর একটি request সর্বোচ্চ চারটি cache point বহন করে।

[`bedrock_cache_instructions`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_instructions], [`bedrock_cache_tool_definitions`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_tool_definitions] আর [`bedrock_cache_messages`][pydantic_ai.models.bedrock.BedrockModelSettings.bedrock_cache_messages] cache point বসায়, আর একটি [`CachePoint`][pydantic_ai.messages.CachePoint] স্পষ্টভাবে একটি চিহ্নিত করে। একটি cache point আগের request-এর cache entry খুঁজে পায় শুধু মোটামুটি 20টি content block-এর মধ্যে, তাই এর বেশি যোগ করা একটি turn-এর পরে `bedrock_cache_messages` আগের request-এর শেষও চিহ্নিত করে।

বিস্তারিত জানতে দেখুন [Bedrock prompt caching](../models/bedrock.md#prompt-caching)।

### OpenAI { #openai }

OpenAI prompt একটি ন্যূনতম দৈর্ঘ্য (GPT-5.6 ও পরের মডেলে 1,024 token) পার হলে নিজে থেকেই cache করে।

GPT-5.6-এর আগের মডেলে একটি cache করা prefix কতক্ষণ টেকে তা নির্ভর করে retention policy-র ওপর, যা [`openai_prompt_cache_retention`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_prompt_cache_retention] প্রতি request-এ override করে।

GPT-5.6 ও পরের মডেলে একটি cache করা prefix তার সর্বশেষ লেখা বা পড়ার পর 30 মিনিট পুনঃব্যবহারযোগ্য থাকে। [`openai_prompt_cache_options`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_prompt_cache_options] TTL আর mode সেট করে: ডিফল্ট implicit mode-এ OpenAI নিজেও একটি breakpoint বসায়, explicit mode-এ শুধু request-এর breakpoint-গুলোই cache হয়। একটি [`CachePoint`][pydantic_ai.messages.CachePoint] একটি user content block-এর পরে একটি breakpoint যোগ করে, আর [`openai_cache_instructions`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_cache_instructions] স্থির instructions-এর পরে একটি যোগ করে। OpenAI প্রতি request-এ সর্বোচ্চ চারটি breakpoint লেখে।

যেকোনো মডেলে, [`openai_prompt_cache_key`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_prompt_cache_key] একটি prefix শেয়ার করা request-গুলোকে দলবদ্ধ করে hit rate বাড়ায়।

বিস্তারিত জানতে দেখুন [OpenAI prompt caching](../models/openai.md#prompt-caching)।

### OpenRouter { #openrouter }

OpenRouter স্পষ্ট breakpoint Anthropic আর Gemini মডেলে পৌঁছে দেয়: [`openrouter_cache_instructions`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_instructions], [`openrouter_cache_tool_definitions`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_tool_definitions], [`openrouter_cache_messages`][pydantic_ai.models.openrouter.OpenRouterModelSettings.openrouter_cache_messages] আর [`CachePoint`][pydantic_ai.messages.CachePoint]। Anthropic route অনুরোধ করা TTL মানে। Gemini route এটি উপেক্ষা করে, কথোপকথনের শুধু শেষ breakpoint ব্যবহার করে, আর কোনো tool definition breakpoint নেয় না; এদের cache করা system instructions বদলাতে পারে না, তাই dynamic content instructions-এ না রেখে পরের একটি user message-এ রাখুন। OpenRouter-এ OpenAI মডেল নিজে থেকেই cache করে; GPT-5.6 breakpoint-এর জন্য OpenRouter provider-সহ একটি OpenAI model class ব্যবহার করুন।

বিস্তারিত জানতে দেখুন [OpenRouter prompt caching](../models/openrouter.md#prompt-caching)।

### Google { #google }

Gemini prompt নিজে থেকেই cache করে। [`CachePoint`][pydantic_ai.messages.CachePoint] চিহ্ন উপেক্ষিত হয়। একটি বড়, স্থির context স্পষ্টভাবে পুনরায় ব্যবহার করতে, একটি cached content resource তৈরি করুন আর তার নাম [`google_cached_content`][pydantic_ai.models.google.GoogleModelSettings.google_cached_content]-এ দিন। তখন resource-টিই system instructions আর tool-এর মালিক হয়, তাই agent-এর নিজের instructions আর tool ওই request-গুলো থেকে বাদ পড়ে।

বিস্তারিত জানতে দেখুন [Google context caching](../models/google.md#context-caching-google_cached_content)।

### অন্যান্য provider { #other-providers }

prompt cache করে এমন অন্য provider, যেমন DeepSeek আর xAI, নিজে থেকেই তা করে। কয়েকটি এমন ইঙ্গিত নেয় যা সম্পর্কিত request-গুলোকে একই cache-এ রাখে: xAI-এর [cache sticky routing](../models/xai.md#cache-sticky-routing) metadata, Mistral-এর [`mistral_prompt_cache_key`][pydantic_ai.models.mistral.MistralModelSettings.mistral_prompt_cache_key], আর OpenAI Codex মডেল কথোপকথন থেকে যে [prompt cache identity](../models/openai-codex.md#prompt-caching) তৈরি করে।

## খরচ { #cost }

Anthropic আর OpenAI GPT-5.6 ও পরের মডেলে, একটি prefix cache-এ লেখার খরচ cache ছাড়া পাঠানোর চেয়ে বেশি, আর আবার পড়ার খরচ অনেক কম:

| Provider | Cache write | Cache read |
|---|---|---|
| Anthropic (Bedrock, Vertex AI আর Foundry-সহ) | 5-মিনিটের cache-এ input দামের 1.25x, 1-ঘণ্টার cache-এ 2x | 0.1x |
| OpenAI GPT-5.6 ও পরের | 1.25x | 0.1x |

তাই একটি 5-মিনিটের cache (1.25x) একবার পড়ার পরেই সমান-সমান হয়, আর Anthropic-এর 1-ঘণ্টার cache (2x) দুবার পড়ার পরে। একটি cache করা prefix আবার পড়ে পরের সেই request, যা retention শেষ হওয়ার আগে এটি দিয়ে শুরু হয়: tool call-ওয়ালা একটি agent run-এ সেটি প্রথমটির পরের প্রতিটি request, আর [`message_history`](../message-history.md) দিয়ে চলতে থাকা একটি কথোপকথনে সেটি সময়মতো আসা প্রতিটি turn। কখনো পুনরাবৃত্তি না হওয়া একটি একক request শুধু লেখার বাড়তি দামটাই দেয়।

/// info | উদাহরণ দিয়ে হিসাব (5-মিনিটের cache)

ধরুন prefix-টি 10,000 token, আর input-এর দাম প্রতি token-এ 1 একক।

| পরিস্থিতি | caching ছাড়া | caching-সহ |
|---|---|---|
| শুধু 1টি request | 10,000 | 12,500 (লেখা 1.25x) — বেশি খরচ |
| 2টি request | 20,000 | 12,500 + 1,000 (পড়া 0.1x) = 13,500 |
| 5টি request | 50,000 | 12,500 + 4 × 1,000 = 16,500 |

যত বেশি বার prefix আবার পড়া হয়, সাশ্রয় তত বাড়ে।

///

## কী একটি cache অকেজো করে { #what-invalidates-a-cache }

### আপনার নিয়ন্ত্রণে থাকা পরিবর্তন { #changes-under-your-control }

- instructions বা system prompt-এ মিনিট-নির্ভুল timestamp বা অন্য প্রতি-request মান। নির্দিষ্ট সময় দরকার না হলে শুধু-তারিখের সূক্ষ্মতা বেছে নিন।
- যে instructions-এর text কথোপকথনের মাঝে বদলায়, যেমন একটি todo list বা memory। এগুলোকে [`on_change='append'`](../agent.md#appending-instruction-changes)-এ নিন, যাতে পরিবর্তন prefix নতুন করে না লিখে history-তে শেষে জুড়ে যায়, আর [অবিশ্বস্ত text instructions-এর বাইরে রাখুন](../agent.md#untrusted-instruction-text)।
- ধাপগুলোর মাঝে tool definition-এর ক্রম বদলানো বা পরিবর্তন করা। [run চলাকালীন দেখা দেওয়া](../tools-advanced.md#mid-run-tool-additions) একটি tool বরং message history-তে রেকর্ড হয়, যা OpenAI Responses আর Anthropic-এ prefix রক্ষা করে।
- যে history processor প্রতিটি request-এ ইতিমধ্যে পাঠানো message নতুন করে লেখে।
- কথোপকথনের মাঝে মডেল বা provider বদলানো। প্রতিটি provider আলাদা cache রাখে।

যে Anthropic মডেলগুলো thinking block-কে সেগুলো তৈরি করা prefix-এর সাথে বেঁধে দেয় (Claude Fable 5.1, Claude Opus 5.5 আর Claude Sonnet 5.5), সেখানে কথোপকথনের মাঝে একই পরিবর্তনগুলো শুধু cache miss নয়, একটি 400 error ঘটায়: দেখুন [Thinking block binding](../models/anthropic.md#thinking-block-binding)।

/// warning | সাধারণ ভুল

`instructions=f'আজ {datetime.now()}'` — প্রতি request-এ সেকেন্ড বদলায়, তাই instructions আর তার পরের সবকিছু প্রতিবার নতুন হয়ে যায়, cache কখনো কাজে লাগে না। শুধু তারিখ দিন (`date.today()`), বা পরিবর্তনশীল তথ্য user message-এ রাখুন।

///

### Provider retention { #provider-retention }

provider-এর cache অলস ফাঁকের পরে মেয়াদোত্তীর্ণ হয়। এটি এড়ানো যায় না, তবে এটি একটি কাজের সুযোগ তৈরি করে: history-পরিবর্তনকারী রক্ষণাবেক্ষণ [cache-ঠান্ডা সময়ে](../message-history.md#scheduling-maintenance-into-cache-cold-windows) নির্ধারণ করুন, যখন পরের request এমনিতেই পুরো input দাম দিত। প্রতিটি provider-এর নথিভুক্ত ডিফল্ট retention রেকর্ড করা থাকে [`ModelProfile.default_cache_retention`][pydantic_ai.profiles.ModelProfile.default_cache_retention] হিসেবে, settings দিয়ে চাওয়া দীর্ঘতর retention নির্ধারণ করে [`Model.resolve_cache_retention()`][pydantic_ai.models.Model.resolve_cache_retention], আর [`prompt_cache_outlook()`][pydantic_ai.profiles.prompt_cache_outlook] যেকোনো একটি নিয়ে পূর্বাভাস দেয় পরের request cache ঠান্ডা পাবে কি না।

## Prefix-স্থিরতার নিশ্চয়তা { #prefix-stability-guarantees }

provider-এর কাছে পাঠানো prompt prefix সম্পর্কে Pydantic AI নিচের নিশ্চয়তাগুলো দেয়:

- প্রতিটি request-এর জন্য [instructions নির্ধারিতভাবে (deterministically) জোড়া হয়](../agent.md#instructions)। `Agent(instructions=...)`-এর স্থির instructions সবসময় dynamic instructions-এর আগে সাজানো থাকে, তাই dynamic content বদলালেও স্থির prefix অক্ষত থাকে।
- [`on_change='append'`](../agent.md#appending-instruction-changes)-ওয়ালা instructions কথোপকথন যে prefix দিয়ে শুরু হয়েছিল তা রাখে: একটি পরিবর্তন history-তে শেষে জুড়ে যায়, আর prefix সরে শুধু তখনই যখন একটি নতুন ভিত্তি শুরু হয়, যেমন নতুন করে লেখা একটি block বদলালে বা history compact হলে। প্রতিটি ক্ষেত্রের জন্য দেখুন [Appending instruction changes](../agent.md#appending-instruction-changes)।
- একটি run-এর মধ্যে message history শুধু-যোগ-করা: Pydantic AI স্থির হয়ে যাওয়া message নতুন করে লেখে না বা ক্রম বদলায় না। আপনার যোগ করা [history processor](../message-history.md#processing-message-history), আর history নতুন করে লেখে এমন capability, যেমন [compaction](compaction.md), ব্যতিক্রম।
- একটি structured `output_type` নিজে কোনো [output mode](../output.md) না বাছলে যে mode পায়, সেটি প্রতিটি মডেলের কাছে run-এর প্রথম request-এ বাছা হয় আর run-এর বাকি অংশে রাখা হয় (একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর পেছনে ছাড়া, যেখানে প্রতিটি মডেল প্রতিটি request-এ বাছে), তাই ধাপগুলোর মাঝে বদলানো একটি [thinking](thinking.md) সেটিং output tool যোগ বা বাদ দেয় না। একটি নতুন run, একই কথোপকথন চালিয়ে যাওয়া একটিসহ, আবার বাছে।
- run ID, message timestamp আর deferred-tool flag-এর মতো ভেতরের হিসাবপত্র provider-এর wire-এ পৌঁছায় না, তাই prompt prefix সরাতে পারে না।
- [Vercel AI](../ui/vercel-ai.md) আর [AG-UI](../ui/ag-ui.md) adapter-এর আসা-যাওয়া পরীক্ষা করা হয়েছে, যাতে পুনর্গঠিত history wire-প্রাসঙ্গিক field-গুলোর (tool call argument, thinking signature) জন্য একই provider request-এ serialize হয়। পুরোনো UI protocol সংস্করণে তথ্য হারাতে পারে — যেমন reasoning বাহক ছাড়া AG-UI সংস্করণ thinking part বাদ দেয়, যা prefix সরায় — তাই client package হালনাগাদ রাখুন। `@ag-ui/client` compaction item আর tool-প্রাপ্যতার পরিবর্তন বহনকারী activity message-ও ফেরত পাঠায় না, যা prefix সরায়; দেখুন [Records carried as activity messages](../ui/ag-ui.md#activity-records)।
- Pydantic AI-এর test suite-এর প্রতিটি রেকর্ড করা provider কথোপকথন wire-স্তরের prefix স্থিরতার জন্য পরীক্ষা করা হয়, তাই যে framework পরিবর্তন prefix সরাতে শুরু করে, সেটি যে pull request-এ আসে সেখানেই CI ব্যর্থ হয়।

## cache-এর কার্যকারিতা পর্যবেক্ষণ { #monitoring-cache-efficiency }

caching কাজ করছে কি না দেখতে, একটি লম্বা শেয়ার করা prefix-সহ একটি request পাঠান, কথোপকথন চালিয়ে যান, আর দুটি response-এর usage তুলনা করুন:

⟦CODE4⟧

প্রথম request তার prefix cache-এ লেখে আর পরেরটি সেটি আবার পড়ে। provider-এর ন্যূনতম cache-যোগ্য দৈর্ঘ্যের নিচের prefix — provider আর মডেলভেদে মোটামুটি 1,024 থেকে 4,096 token — কখনো cache হয় না, তাই দুটি গণনাই শূন্যে থাকে। কিছু provider, যেমন GPT-5.6-এর আগের OpenAI, শুধু cache read জানায়।

প্রতিটি response-এর [`RequestUsage`][pydantic_ai.usage.RequestUsage] provider-নির্বিশেষে `cache_read_tokens` আর `cache_write_tokens` একই রূপে দেয়, আর একটি run-এর [`RunUsage`][pydantic_ai.usage.RunUsage] (`result.usage`) run-এর সব request জুড়ে এগুলো যোগ করে। `input_tokens`-এ cache read আর write অন্তর্ভুক্ত, তাই `cache_read_tokens / input_tokens` (`cache_hit_ratio` property) প্রতি request-এ একটি তুলনীয় hit ratio। একটি run-এর ratio হিসাব করুন শুধু তখনই, যখন এর সব request একই মডেলে গেছে: একাধিক মডেল জুড়ে যোগ করা ratio ব্যাখ্যাযোগ্য নয়।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `first` | handbook + প্রথম প্রশ্ন cache-এ লেখে → `cache_write_tokens` > 0 |
| `second` (`message_history`-সহ) | একই শুরু, তাই cache থেকে পড়ে → `cache_read_tokens` > 0 |
| দুটিই 0 | prefix খুব ছোট (ন্যূনতম সীমার নিচে), বা caching চালু নয় |

///

[instrumentation](../logfire.md) চালু থাকলে, model-request span-গুলো একটি প্রতি-request hit ratio আর প্রতিষ্ঠিত cache করা prefix-এর আকার বহন করে। যে request প্রতিষ্ঠিত prefix-এর একটি অর্থবহ অংশ হারায়, সেটি একটি শ্রেণিবদ্ধ কারণসহ cache collapse হিসেবে রেকর্ড হয়, যেমন একটি মেয়াদোত্তীর্ণ provider retention window বা provider-native compaction; আর শুধু একটি অপ্রত্যাশিত collapse একটি `pydantic_ai.cache.collapse` span event পাঠায়। cache করার মতো লম্বা একটি request, যা এমন মডেলে যায় যার caching কনফিগার করা দরকার কিন্তু কিছুই কনফিগার করা নেই, সেটি `pydantic_ai.cache.not_enabled` হিসেবে চিহ্নিত হয়। attribute, সীমা, collapse-এর কারণ আর প্রতিষ্ঠিত prefix কীভাবে খেয়াল রাখা হয় তার জন্য দেখুন [Prompt-cache health](../logfire.md#prompt-cache-health)।

development-এ আর CI-তে Python warning হিসেবে একই সংকেত পেতে Pydantic AI Harness-এর [Warn On Cache Busts](../harness/warn-on-cache-busts.md) capability ব্যবহার করুন: এটি একই detector আর শ্রেণিবিন্যাস শেয়ার করে, আর caching চালু না থাকলেও সতর্ক করে।

এই সংকেতগুলো ধরে যে একটি cache miss হয়েছে, কেন হয়েছে তা নয়। hit rate প্রত্যাশার চেয়ে কম হলে:

1. মডেলের জন্য caching চালু আছে কি না, আর কোনো provider-নির্দিষ্ট cache সেটিং একীভূতটিকে override করছে কি না দেখুন।
2. শেয়ার করা prefix provider-এর ন্যূনতম cache-যোগ্য দৈর্ঘ্যের ওপরে কি না দেখুন।
3. প্রতিটি response-এর `cache_read_tokens` আর `cache_write_tokens` তুলনা করুন: পরে পড়া ছাড়া লেখা মানে prefix পড়ার আগেই বদলে গেছে বা মেয়াদ শেষ হয়েছে।
4. prefix সরায় এমন [আপনার নিয়ন্ত্রণে থাকা পরিবর্তন](#changes-under-your-control) খুঁজুন, আর কথোপকথন তার পূর্ণ `message_history` নিয়ে চলছে কি না দেখুন।
5. request-গুলোর মাঝের ফাঁক provider-এর retention ছাড়াচ্ছে কি না, আর একটি কথোপকথনের request-গুলো একই cache-এ পৌঁছাচ্ছে কি না দেখুন (OpenRouter-এর provider routing, xAI-এর sticky routing, OpenAI-এর `openai_prompt_cache_key`)।
6. provider-কে জিজ্ঞেস করুন: Anthropic-এর [cache diagnostics](../models/anthropic.md#cache-diagnostics) আর OpenAI-এর [prompt cache diagnostics](../models/openai.md#prompt-caching) জানায় একটি request কেন miss করেছে।

warning না থাকা প্রমাণ করে না যে caching কাজ করছে: শনাক্তকরণ সীমার চেয়ে কম ঘাটতির একটি request, cache usage জানায় না এমন একটি provider, বা কখনো প্রতিষ্ঠিত না হওয়া একটি cache — সবই নীরব থাকে।

## extension লেখকদের জন্য নিয়ম { #rules-for-extension-authors }

tool, toolset আর capability-র লেখকদের একই চুক্তি রক্ষা করা উচিত:

- একটি run চলাকালীন কখনো cache করা prefix বদলাবেন না।
- প্রতি-turn dynamic content রাখুন user message-এ, tool result-এ, বা শেষ [`CachePoint`][pydantic_ai.messages.CachePoint]-এর পরে।
- ধাপগুলো জুড়ে tool definition আর তাদের ক্রম স্থির রাখুন।
- instructions-এ শুধু-তারিখের timestamp ব্যবহার করুন।
- কথোপকথনের মাঝে বদলায় এমন instructions-কে [`on_change='append'`](../agent.md#appending-instruction-changes) দিন, যার জন্য আপনার capability বা toolset-এ একটি `id` লাগে, আর [অবিশ্বস্ত text instructions-এর বাইরে রাখুন](../agent.md#untrusted-instruction-text)।

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[Caching()]` — Anthropic/Bedrock/OpenRouter-Anthropic-এ এটি ছাড়া কিছুই cache হয় না।
* cache কাজ করে prefix অপরিবর্তিত থাকলে: tool → system prompt → message; আগের কিছু বদলালে বাকিটা আবার পুরো দামে।
* লেখা 1.25x (Anthropic 1h-এ 2x), পড়া 0.1x — একবার পড়লেই (1h-এ দুবার) লাভ।
* এককালীন অনেক কথোপকথন হলে `Caching(messages=False)`।
* provider-নির্দিষ্ট cache সেটিং থাকলে একীভূত সেটিং পুরো request-এর জন্য উপেক্ষিত।
* instructions-এ timestamp, বদলানো tool তালিকা, মডেল বদল — cache ভাঙার সাধারণ কারণ।
* `cache_read_tokens` / `cache_write_tokens` দিয়ে যাচাই করুন; harness-এর Warn On Cache Busts CI-তে সতর্ক করে।

///
