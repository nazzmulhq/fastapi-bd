
# Compaction { #compaction }

/// note | এই পেজে যা শিখবেন

* লম্বা agent run-এর history context window-এর মধ্যে রাখার কৌশলের "মেনু" — কোনটি বিনা খরচে, কোনটি LLM দিয়ে।
* trigger: `max_messages`, `max_tokens`, `max_fraction` — আর কেন `max_fraction` সব মডেলে কাজ করে।
* context window ভুল বা অজানা হলে কী করবেন, আর token কীভাবে গোনা হয়।
* `TieredCompaction` (প্রস্তাবিত ডিফল্ট), `FallbackCompaction`, `ClampOversizedMessages`, `ClearToolResults` ইত্যাদি।
* cache-এর বিনিময়, tracing, receipt, pinning আর cross-model bridge।

///

Compaction হলো একটি agent-এর কথোপকথনের history মডেলের context window-এর মধ্যে রাখার কৌশলের একটি মেনু। এই Pydantic AI `Capability` class-গুলো প্রতিটি request বের হওয়ার ঠিক আগে message history সম্পাদনা করে। `FallbackCompaction` ঐচ্ছিকভাবে একটি token সীমায় তার chain চালু করে, আর একটি সংযোজনযোগ্য `CompactionStrategy` হিসেবেও কাজ করে। সম্পাদনাগুলো run-এর message history-তে **স্থায়ী হয়**, তাই একটি ছাঁটাই, মুছে ফেলা বা সারাংশ পরের ধাপগুলোতেও থেকে যায় — প্রতি turn-এ পুরো history থেকে নতুন করে হিসাব হয় না।

সব কৌশল tool-call / tool-return-এর **জোড়া** অক্ষত রাখে। core এটি যাচাই করে না, আর provider একটি জোড়াহীন অংশ প্রত্যাখ্যান করে — তাই এই জোড়ার নিশ্চয়তাই এগুলোকে একটি agent-এ নিশ্চিন্তে বসানোর মতো করে। LLM-ছাড়া কৌশলগুলো কখনো মডেল ডাকে না; শুধু `SummarizingCompaction` আর `RelevanceCompaction` (আর `TieredCompaction` যখন এগুলোর একটিতে ওঠে) token খরচ করে।

OpenAI আর Anthropic-এ core [provider-native compaction](../capabilities/compaction.md)-ও দেয় — provider server-দিকে history-র সারাংশ করে। এই পেজের কৌশলগুলো মডেল-নিরপেক্ষ বিকল্প: এগুলো প্রতিটি মডেলে কাজ করে আর compaction-এর যুক্তি (আর তার খরচ) আপনার নিয়ন্ত্রণে রাখে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/compaction/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

অনেক turn ধরে চলা একটি agent history জমায়: tool output, ফাইল পড়া, মডেলের reasoning, পুনরাবৃত্ত content। নিয়ন্ত্রণ না করলে সেই history মডেলের context window ছাড়িয়ে যায় আর পরের request ব্যর্থ হয়। compaction history সীমার মধ্যে রাখে, আর সঠিক কৌশল নির্ভর করে ফোলাভাবটা কোথায় আর সেটি উদ্ধারে আপনি কতটা খরচ করতে পারেন তার ওপর।

/// tip | উদাহরণ দিয়ে বুঝি

একটি ছোট ব্যাগে লম্বা ভ্রমণের জিনিস রাখতে হলে আগে সহজ কাজগুলো করেন: পুরোনো রসিদ ফেলে দেন (`ClearToolResults`), একই জিনিসের দুটো কপি থাকলে একটা রাখেন (`DeduplicateFileReads`)। তাতেও না ধরলে তবেই ভারী কাজ — কাপড় ভাঁজ করে ভ্যাকুয়াম ব্যাগে ভরা (`SummarizingCompaction`, খরচ আছে)। `TieredCompaction` ঠিক এই ক্রমেই এগোয়।

///

## মেনু { #the-menu }

| Component | খরচ | কী করে | কখন বাছবেন |
|---|---|---|---|
| `ClampOversizedMessages` | LLM-ছাড়া | একটি অতিরিক্ত বড় part-এর (response text, tool-call args) মাথা/লেজ রেখে কাটে | একটি নিয়ন্ত্রণহীন generation context সীমা ছাড়িয়েছে আর অন্য কোনো কৌশল সেখানে পৌঁছাতে পারে না |
| `SlidingWindowCompaction` | LLM-ছাড়া | সবচেয়ে পুরোনো পুরো message বাদ দিয়ে একটি লেজ রাখে | শুধু সাম্প্রতিক turn দরকার আর পুরোনো context পুরোপুরি ফেলে দেওয়া যায় |
| `ClearToolResults` | LLM-ছাড়া | পুরোনো tool *result*-এর content জায়গাতেই খালি করে, শেষ `keep_pairs`টি রেখে | context-এ tool output-ই বেশি আর দরকারে আবার আনা যায় (সস্তা প্রথম স্তর) |
| `DeduplicateFileReads` | LLM-ছাড়া | একই ফাইলের নতুন পড়া এসে যাওয়া প্রতিটি পুরোনো পড়া খালি করে | agent ফাইল বারবার পড়ে আর শুধু সর্বশেষ সংস্করণ গুরুত্বপূর্ণ |
| `SummarizingCompaction` | একটি LLM call | পুরোনো message-গুলোর একটি গোছানো সারাংশ বানায়, সাম্প্রতিক লেজ রেখে | পুরোনো context এখনও জরুরি কিন্তু সংকুচিত করতে হবে; সস্তা স্তরগুলোর পেছনে ব্যবহার করুন |
| `RelevanceCompaction` | প্রতি নতুন ধাপে একটি judge request, সাথে ঐচ্ছিক সারাংশ | একটি judge মডেলের উত্তর অনুযায়ী প্রতিটি পুরোনো ধাপ রাখে, ছোট করে বা বাদ দেয় | কিছু পুরোনো tool result এখনও হুবহু দরকার আর বাকিগুলো অকেজো বোঝা |
| `TieredCompaction` | ধাপে ধাপে ওঠে | আগে সস্তা pass চালায়, তবুও `target_tokens`-এর ওপরে থাকলে তবেই সারাংশ | একটি যুক্তিসঙ্গত ডিফল্ট চান: দামি সারাংশে খরচ শুধু দরকার হলে |
| `FallbackCompaction` | chain-এর ওপর নির্ভর | একটি কৌশল raise করলে পরেরটি চেষ্টা করে | সারাংশ ব্যর্থ হতে পারে আর নির্ধারিত ছাঁটাই দিয়ে run বাঁচিয়ে রাখতে হবে |
| `WarnNearLimits` | LLM-ছাড়া | সীমা কাছে এলে একটি URGENT/CRITICAL সতর্কতা ঢোকায় | history নতুন করে লেখার বদলে agent-কে কাজ গুটিয়ে আনাতে চান |
| `ReportContextUsage` | LLM-ছাড়া | আপনার application-কে context usage জানায়; কখনো history সম্পাদনা করে না | UI-তে একটি সরাসরি context মিটার চান |

compaction স্থায়ী run history হালনাগাদ করে আর বর্তমান request view প্রতিস্থাপন করে। `Memory`-র মতো শুধু-request-এ-ঢোকানো capability compaction-এর পরে তালিকাভুক্ত করুন, যাতে সেগুলো compact করা request-এ প্রযোজ্য হয়। আগের শুধু-request সম্পাদনা বাদ পড়ে, এমনকি `ClampOversizedMessages`-এর ছোট করার মতো কিছু না থাকলেও।

/// warning | সাধারণ ভুল

`capabilities=[Memory(...), TieredCompaction(...)]` — এই ক্রমে Memory-র ঢোকানো অংশ compaction মুছে ফেলে। শুধু-request-এ-ঢোকানো capability সবসময় compaction-এর **পরে** রাখুন: `[TieredCompaction(...), Memory(...)]`।

///

## Trigger { #triggers }

instruction প্রতিস্থাপন আর প্রত্যাহারের record token হিসাবে তাদের পুরো render করা system text যোগ করে। একটি নতুন instruction ভিত্তির আগের বাতিল হওয়া হালনাগাদ বাদ যায়।

প্রতিটি আকার-ভিত্তিক কৌশল চালু হয় `max_messages`, `max_tokens` (আনুমানিক), বা `max_fraction`-এ। token গণনা নোঙর করে সবচেয়ে সাম্প্রতিক model response-এর provider-জানানো usage-এ, যখন সেটি পাওয়া যায়। সেই provider usage-এ নোঙর করা request-এ পাঠানো instructions, tool definition আর `FilePart` payload অন্তর্ভুক্ত; শুধু তার পরে যোগ হওয়া message-গুলো অনুমান করা হয়। নোঙরের পরের অংশ, বা usage নোঙর ছাড়া একটি history, `tokenizer` বা ~4-অক্ষর-প্রতি-token অনুমান ব্যবহার করে আর `FilePart` payload দেখতে পায় না। request-এর জন্য নতুন প্রকাশিত অপেক্ষমাণ tool schema implementation রক্ষণশীলভাবে অনুমান করে। কোনো trigger সেট না থাকলে `DeduplicateFileReads` প্রতিটি request-এ চলে (এটি সস্তা আর প্রায় ক্ষতিহীন)। `TieredCompaction` একটিমাত্র `target_tokens` / `target_fraction` budget-এ চালু হয় আর থামে। `ClampOversizedMessages` চালু হয় প্রতি *part*-এ (`max_part_tokens` / `max_part_chars`), পুরো history-তে নয় — এটি যে ব্যর্থতা লক্ষ্য করে সেটি একটি অতিরিক্ত বড় part, বড় মোট নয়।

### `max_fraction`: সব মডেলের জন্য একটি সেটিং { #max_fraction-one-setting-for-every-model }

একটি absolute `max_tokens` সঠিক শুধু সেই মডেলের জন্য, যার বিপরীতে এটি মাপা হয়েছিল। `180_000` কনফিগার করলে একটি 1M-context মডেল তার ক্ষমতার এক-পঞ্চমাংশে compact করে, অপ্রয়োজনীয় সারাংশের জন্য টাকা দিয়ে; আর `1_000_000`-এ কনফিগার করা একটি 128K মডেল provider request প্রত্যাখ্যান করার আগে কখনো compact করে না।

`max_fraction` প্রতি request-এ মডেলের আসল context window-এর বিপরীতে নির্ধারিত হয়, তাই একটি কনফিগারেশনই সব জায়গায় সঠিক:

⟦CODE1⟧

এটি 1M মডেলে 900K-তে আর 128K মডেলে 115K-তে compact করে। `WarnNearLimits` একই আকার নেয় `max_context_fraction` হিসেবে, আর `TieredCompaction` `target_fraction` হিসেবে। `max_tokens` আর `max_fraction` পরস্পর-বর্জনীয় — দুটো নেওয়া একটি কৌশলকে একটি বেছে অন্যটি ফেলে দিতে হতো, ফলে caller বুঝতে পারত না কোন budget কার্যকর ছিল।

window হলো মডেলের নিজের [`context_window`](../models/overview.md#inspecting-a-models-profile): এর profile যে মান সেট করে, `profile={'context_window': ...}` হিসেবে আপনার দেওয়া একটিসহ; কোনো profile না দিলে [`genai-prices`](https://github.com/pydantic/genai-prices) থেকে পূরণ করা। একটি `FallbackModel` তার মডেলগুলোর মধ্যে সবচেয়ে ছোট window জানায়, কারণ যেকোনোটিই উত্তর দিতে পারে। সংখ্যাটি নিজে চাইলে `resolve_context_window` export করা আছে। কিছুই cache হয় না: শুধু মডেল বা registry যে window বলে, সেটিকেই কখনো আসল ধরা হয়।

যে মডেলের সাথে পরামর্শ করা হয় সেটি `ModelRequestContext.model` — request যার কাছে যাবে, run যেটি দিয়ে শুরু হয়েছিল সেটি নয়। আগে সাজানো একটি capability এটি বদলে দিতে পারে, আর budget তা অনুসরণ করে।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `max_fraction=0.9` | context window-এর 90% ভরলে compact করো — 1M মডেলে 900K, 128K মডেলে ~115K |
| `keep_messages=20` | সারাংশের পরে সাম্প্রতিক 20টি message হুবহু রাখো |
| `SummarizingCompaction` | পুরোনো অংশের একটি LLM-তৈরি সারাংশ বানায় |

///

### window নির্ধারণ না হলে { #when-the-window-does-not-resolve }

প্রতিটি মডেলের window জানা থাকে না। একটি local endpoint, একটি কাস্টম deployment, registry জানে কিন্তু window রেকর্ড নেই এমন মডেল, আর যে `FallbackModel`-এর কোনো মডেলেরই window নেই — সবই কিছুতেই নির্ধারিত হয় না। তখন ভগ্নাংশটি নেওয়া হয় `fallback_context_window` থেকে, যার ডিফল্ট একটি রক্ষণশীল 200K (`DEFAULT_CONTEXT_WINDOW`): প্রয়োজনের আগে compact করার খরচ একটি সারাংশ, বেশি অনুমান করার খরচ পুরো request।

ভগ্নাংশ নেয় এমন প্রতিটি capability fallback-ও নেয়, তাই যে মডেলের আকার আপনি জানেন তাতে 200K-এ আটকে থাকতে হয় না:

⟦CODE2⟧

এটি দেখা হয় শুধু নির্ধারণ ব্যর্থ হলে, তাই registry যে মডেল জানে তাতে এর কোনো খরচ নেই।

`TestModel` নির্ধারিত না হওয়া মডেলগুলোর একটি: এর `model_id` হলো `test:test`, তাই ভগ্নাংশটি `fallback_context_window` থেকে নেওয়া হয় আর `max_fraction=0.9` একটি 180,000-token trigger হয়ে যায়। শুধু `TestModel`-এর বিপরীতে পরীক্ষা করা একটি compaction config দেখে মনে হবে কখনো চালু হয় না; trigger-টি নাগালে আনতে test-এ `context_window=` বা `fallback_context_window=` দিন।

### window ভুল সংখ্যায় নির্ধারিত হলে { #when-the-window-resolves-to-the-wrong-number }

নির্ধারণ সফল হয়েও ভুল হতে পারে, যেখানে `fallback_context_window` কোনো সাহায্য করে না — এটি প্রযোজ্য শুধু নির্ধারণ ব্যর্থ হলে। তিনটি ক্ষেত্র:

- **registry-র entry নিজেই ভুল।** Harness `genai-prices` পড়ে আর এটি যাচাই করতে পারে না। `genai-prices` 0.1.3-এর বিপরীতে মাপা:

  | model id | registry রেকর্ড করে | আসল window |
  |---|---|---|
  | `anthropic:claude-sonnet-4-5` | 1,000,000 | 200,000 |
  | `anthropic:claude-opus-4-6` | 200,000 | 1,000,000 |

  বেশি রেকর্ড করা window-ই সেই দিক যা একটি run ভাঙে। `anthropic:claude-sonnet-4-5`-এ `max_fraction=0.9` একটি 200,000-token window-এর বিপরীতে 900,000-token trigger-এ নির্ধারিত হয়: compaction কখনো চালু হয় না, আর provider বরং request প্রত্যাখ্যান করে। **`claude-sonnet-4-5`-এ স্পষ্টভাবে `context_window=200_000` দিন।** `claude-sonnet-5`-এর রেকর্ড করা 1,000,000 Anthropic-এর model documentation-এর সাথে মেলে, তাই override লাগে না; অন্য কোনো Sonnet id ব্যবহার করলে নির্ধারিত সংখ্যার ওপর ভরসা করার আগে provider-এর নিজের documentation-এর সাথে মিলিয়ে নিন। কম রেকর্ড করা window নিরাপদ কিন্তু অপচয়ী — দরকারের আগেই compact করে।
- registry একটি মডেলকে যতটা মানানো যায় তার সর্বোচ্চ রেকর্ড করে। যেখানে সেই সর্বোচ্চ শর্তসাপেক্ষ — একটি beta header, একটি pricing tier — সেখানে সাধারণ request কম পায়, আর রেকর্ড করা সংখ্যার একটি ভগ্নাংশ provider request প্রত্যাখ্যান করার আগে কখনো চালু হয় না।
- একটি self-hosted বা proxy করা endpoint এমন একটি model id জানায়, যার registry entry অন্য কারো deployment বর্ণনা করে।

`context_window` নির্ধারণকে সরাসরি override করে, ভগ্নাংশ নেয় এমন প্রতিটি capability-তে:

⟦CODE3⟧

/// info | এক নজরে: window কোথা থেকে আসে

| পরিস্থিতি | কী ব্যবহার হয় | আপনি কী দেবেন |
|---|---|---|
| registry/profile সঠিক window জানে | সেই window | কিছু না |
| window অজানা (local, `TestModel`…) | `fallback_context_window` (ডিফল্ট 200K) | আসল আকার জানলে `fallback_context_window=` |
| registry ভুল জানে (যেমন `claude-sonnet-4-5`) | ভুল সংখ্যা! | `context_window=` দিয়ে সরাসরি override |

///

### ভগ্নাংশে কী গোনা হয় { #what-counts-toward-the-fraction }

একটি usage নোঙর থাকলে, provider-জানানো usage নোঙর করা request-এর জন্য বিল করা সবকিছু ঢাকে,
তার instructions, tool definition আর `FilePart` payload-সহ। যে response-এর বিল করা usage
কয়েকটি model request যোগ করে, সেটি নোঙর করে তার context মাপে এমন একটির input token-এ, সাথে
তার output: একটি [Google long decode](../models/google.md#long-decode)-এর প্রথম request, যার
বিল করা input আগের request-গুলোর output আবার গোনে, অথবা একটি
[Anthropic response that reports its passes](../models/anthropic.md#server-side-tool-loops)-এর শেষ sampling pass, যার
বিল করা input প্রতিটি pass-এর context আবার গোনে। নোঙরের পরের অংশের জন্য,
আর usage নোঙর ছাড়া পুরো একটি history-র জন্য, estimator `tokenizer` দেওয়া থাকলে সেটি ব্যবহার করে,
নইলে ~4-অক্ষর-প্রতি-token অনুমান। সেই অনুমান করা অংশ `FilePart` payload দেখতে পায় না, আর
একটি tool return-এর ভেতরের ফাইলকে গোনে তার জায়গায় থাকা `See file <identifier>.` reference হিসেবে।
নোঙরের পরে instructions বদলালে, নতুন সেটটি অনুমানে পুরোনোটির জায়গা নেয়,
যোগ হয় না, কারণ একটি request শুধু একটিই পাঠায়। request-এর জন্য নতুন প্রকাশিত অপেক্ষমাণ tool schema
implementation রক্ষণশীলভাবে অনুমান করে, কারণ আগের নোঙর সেগুলো ঢাকে না।

**আপনি আগে থেকে একটি absolute `max_tokens` সেট করে থাকলে, আবার যাচাই করুন।** estimator আগে শুধু user আর system prompt, tool return, response text আর tool call গুনত। এখন `ThinkingPart` / `CompactionPart` content, retry content, `NativeToolCallPart` / `NativeToolReturnPart`, আর সবচেয়ে সাম্প্রতিক `ModelRequest.instructions`-ও গোনা হয়, তাই একই history বেশি মাপে আর অপরিবর্তিত `max_tokens` আগে compact করে। কতটা আগে, তা নির্ভর করে history-র কতটা thinking block, retry আর instructions তার ওপর; thinking-ভারী tool-calling history-তে এটি পুরোনো গণনার কয়েক গুণ হতে পারে। প্রতিটি কৌশল কী মোছে তা অপরিবর্তিত — শুধু কখন চলে তা বদলেছে।

### `keep_tokens`-এ কী গোনা হয় { #what-counts-toward-keep_tokens }

রাখা লেজটি প্রতি message-এ `estimate_message_tokens` দিয়ে মাপা হয়, তাই `keep_tokens` মানে
provider যেভাবে গোনে সেই token। একটি response অন্তত তার জানানো `output_tokens` গোনে, যাতে
এমন thinking-ও আছে যা কিছু provider শুধু একটি signature-সহ খালি part হিসেবে ফেরত দেয়। usage বহন করা দুটি response-এর
মাঝের message-গুলো তাদের `input_tokens`-এর পার্থক্য ভাগ করে নেয়, যা
ঠিক সেটাই যা provider তাদের জন্য গুনেছিল। যে response-এর বিল করা usage কয়েকটি model
request যোগ করে, সেটি ওই পার্থক্যে ঢোকে তার context মাপে এমন একটির input token দিয়ে: একটি
[Google long decode](../models/google.md#long-decode)-এর প্রথম request, বা একটি [Anthropic response that reports its passes](../models/anthropic.md#server-side-tool-loops)-এর শেষ sampling pass।
সেই শেষ pass response-এর নিজের আগের pass-গুলোও পড়েছিল, তাই পার্থক্য সেগুলোকে
তার আগের message-গুলোর নামে জমা করে, আর লেজটি বেশি মাপে। এমন প্রথম response-এর আগে, শেষটির পরে, আর
যেখানে দুটির মাঝে history বাড়েনি (যেমন আগের একটি compaction জুড়ে), সেখানে `tokenizer` বা
~4-অক্ষর-প্রতি-token অনুমান প্রযোজ্য। instructions লেজের অংশ নয়। provider usage ছাড়া একটি
history আগের মতোই অনুমান দিয়ে মাপা হয়।

**আপনি `keep_tokens` সেট করে থাকলে, আবার যাচাই করুন।** আগে এটি শুধু অনুমান দিয়ে মাপা হতো, যা
thinking-ভারী history-তে আসল token-এর এক-তৃতীয়াংশ বা তারও কম দেখতে পারে, তাই একই budget
তার বলা পরিমাণের কয়েক গুণ বেশি history রাখত। এখন এটি বলা পরিমাণই রাখে, তাই কম message।

## usage জানানো: `ReportContextUsage` { #reporting-usage-reportcontextusage }

একটি কৌশল জানে কখন কাজ করতে হবে, কিন্তু run সীমার কতটা কাছে তা কিছুই বলে না — তাই যে application `context: 73%` দেখাতে চায়, সে history আবার গুনে আর হর (denominator) অনুমান করে বসে। `ReportContextUsage` এর কোনোটিই করে না — এটি একই estimator আর একই নির্ধারিত window আবার ব্যবহার করে, আর শুধু পর্যবেক্ষণ করে:

⟦CODE4⟧

প্রতিটি পাঠ বহন করে `used_tokens`, `window_tokens`, `fraction` আর `resolved` — window মডেলের আসলটি না হয়ে fallback হলে `False`, তাই একটি মিটার দেখাতে পারে যে শতাংশটি অনুমান। Migration: `on_usage` এখনও সাপোর্টেড তবে deprecated। এর callback-এর ভেতরের কোড একটি `ContextUsageEvent` subscription-এ সরিয়ে নিন। ক্রম গুরুত্বপূর্ণ: একই চক্রের compaction-এর পরে সংশোধিত বর্তমান history দেখতে monitor-টি একটি compaction capability-র *পরে* রেজিস্টার করুন, আর compaction কী চালু করেছিল তা দেখতে আগে।

`used_tokens` ওপরের হিসাব অনুসরণ করে: provider usage নোঙরে নোঙর করা request-এর instructions, tool
definition আর `FilePart` payload অন্তর্ভুক্ত। নোঙরের পরের অংশ, বা নোঙর ছাড়া একটি
history, `tokenizer` বা ~4-অক্ষর-প্রতি-token অনুমান ব্যবহার করে আর
`FilePart` payload দেখতে পায় না। অপেক্ষমাণ নতুন প্রকাশিত tool schema implementation রক্ষণশীলভাবে
অনুমান করে। একই চক্রে আগে একটি compaction capability চললে, তার পরে রেজিস্টার করা monitor
পুনর্লিখনের অনুমিত উদ্ধার বাদ দেয়, আর নোঙরের স্থির provider
overhead রেখে দেয়।

## run-এর বাইরে compact করা: `compact_now` { #compacting-outside-a-run-compact_now }

একটি কৌশলের `compact` একটি `RunContext` নেয়, যা run-গুলোর *মাঝে* একটি কথোপকথন ধরে রাখা application-এর কাছে থাকে না — আর ঠিক তখনই ব্যবহারকারী `/compact` টাইপ করে। `compact_now` একটি ফেলে-দেওয়া context বানায়, যাতে agent যে কৌশল ব্যবহার করে সেটিই একটি command handler থেকে চালানো যায়:

⟦CODE5⟧

`compact_now` নিজের কোনো trigger প্রয়োগ করে না, তাই যে কৌশলের `compact` শর্তহীন, সেটি history-র আকার যা-ই হোক চলে। যে কৌশল নিজের থামার শর্ত সংজ্ঞায়িত করে, সেটি তবুও তা মানে: `TieredCompaction` শুধু ততক্ষণ ওঠে যতক্ষণ না history তার লক্ষ্যে আঁটে, তাই ইতিমধ্যে লক্ষ্যের নিচে থাকা history অপরিবর্তিত ফেরে। যা-ই হোক চালাতে চাইলে স্তরটি সরাসরি দিন।

`focus` সেই কৌশলগুলোকে চালিত করে যেগুলো গদ্য লেখে বা প্রাসঙ্গিকতা বিচার করে — `SummarizingCompaction` আর `RelevanceCompaction`, export করা `SupportsFocus` protocol-এর `with_focus` দিয়ে — আর যেগুলো নিয়ম মেনে content বাদ দেয় বা খালি করে, সেগুলো একে পাশ কাটায়, কারণ তাদের চালানোর মতো কিছু নেই। `TieredCompaction` focus নেয় যখন এর কোনো স্তর নেয়, তাই একটি focus wrapper-এ থেমে না গিয়ে সারাংশের স্তরে পৌঁছায়।

history বদলানো একটি compaction সেই একই `compact_messages` span পাঠায় যা run-এর ভেতরের পথ পাঠায়, তাই compaction যেভাবেই চালু হোক, একটি instrumented application একই আকার দেখে। রেকর্ড করতে `tracer=` দিন; না দিলে span একটি কিছু-না-করা tracer-এ যায়।

compact করা কথোপকথনের id দিয়ে `conversation_id=` দিন। এটি ফেলে-দেওয়া context-এ সেট হয়, তাই `SummarizingCompaction`-এর সারাংশ run নিজের নতুন id-র বদলে সেই কথোপকথনের অধীনে রেকর্ড হয় (এর message আর এর `gen_ai.conversation.id` span attribute)। একটি run-এর ভেতরে, এটি ছাড়াই সারাংশ run parent run-এর `conversation_id` নেয়।

## প্রস্তাবিত ডিফল্ট: `TieredCompaction` { #the-recommended-default-tieredcompaction }

এই ক্ষেত্রের সাধারণ ঐকমত্য (Anthropic, OpenCode, Letta) হলো আগে মুছে ফেলা আর ডুপ্লিকেট বাদ দেওয়া, আর তা যথেষ্ট না হলে তবেই সারাংশ করা। সারাংশ input token-কে output token-এ পরিণত করে, যা বাড়তি দামে বিল হয় আর একটির পর একটি তৈরি হয় — তাই এটি সত্যিই দামি। LLM-ছাড়া কৌশলগুলো শুধু সস্তা input দিকটা ছোঁয়।

`TieredCompaction` এই ধাপে ধাপে ওঠা ধারণ করে: এটি প্রতিটি স্তর ক্রমানুসারে চালায়, প্রতিটির পরে token গণনা আবার মাপে, আর কথোপকথন `target_tokens`-এ আঁটামাত্র থামে। স্তরগুলো সস্তা-থেকে-দামি ক্রমে সাজান, যাতে দামি সারাংশের স্তরে পৌঁছানো হয় শুধু তখনই যখন সস্তা pass-গুলো যথেষ্ট উদ্ধার করতে পারে না।

⟦CODE6⟧

`TieredCompaction`-এর ভেতরের একটি স্তর সরাসরি orchestrator চালায়, যা প্রতিটি স্তরের পরে আবার মাপে আর `target_tokens`-এর নিচে এলেই থামে। তাই `TieredCompaction`-এর ভেতরে চললে একটি স্তরের নিজের `max_*` trigger অপ্রাসঙ্গিক — যেকোনো বৈধ মান দিন (যেমন `ClearToolResults(max_tokens=1)`)। `async def compact(messages, ctx) -> list[ModelMessage]` (`CompactionStrategy` protocol) আছে এমন যেকোনো object একটি স্তর হতে পারে, তাই আপনি নিজেরটিও জুড়ে দিতে পারেন।

/// info | কোডটি সহজ ভাষায়

| স্তর | কী করে | খরচ |
|---|---|---|
| 1. `DeduplicateFileReads(file_key=my_file_key)` | একই `path`-এর পুরোনো `read_file` ফল খালি করে | বিনা মূল্যে |
| 2. `ClearToolResults(max_tokens=1, keep_pairs=3)` | শেষ 3টি ছাড়া পুরোনো tool result খালি করে (`max_tokens=1` শুধু constructor-এর জন্য) | বিনা মূল্যে |
| 3. `SummarizingCompaction(..., keep_messages=20)` | তবুও বড় থাকলে পুরোনো অংশের সারাংশ, শেষ 20টি message রেখে | একটি LLM call |
| `target_tokens=120_000` | history এর নিচে নামলেই পরের স্তর আর চলে না | — |

///

## `FallbackCompaction`: একটি কৌশল ব্যর্থ হলে উদ্ধার { #fallbackcompaction-recover-when-a-strategy-fails }

একটি সফল স্তর যথেষ্ট উদ্ধার না করলে `TieredCompaction` এগিয়ে যায়। `FallbackCompaction` এগোয় শুধু তখনই, যখন একটি কৌশল `fallback_on`-এ বাছাই করা একটি exception raise করে, যার ডিফল্ট Pydantic AI-এর `ModelAPIError` আর `FallbackExceptionGroup`। শেষেরটি raise হয় যখন একটি `FallbackModel`-এর প্রতিটি মডেল ব্যর্থ হয়। প্রতিটি চেষ্টা মূল message object-গুলো থাকা একটি নতুন list পায়, তাই একটি ব্যর্থ কৌশলের list-স্তরের পরিবর্তন তার fallback-কে প্রভাবিত করে না। কৌশলগুলোকে তবুও `CompactionStrategy` চুক্তি মানতে হবে আর message object বদলানো এড়াতে হবে। প্রতিটি কৌশল ব্যর্থ হলে শেষ exception আবার raise হয়। না-মেলা exception, cancellation আর অন্য `BaseException` subclass সঙ্গে সঙ্গে পার হয়ে যায়; `Exception` থেকে আসে না এমন type `fallback_on` প্রত্যাখ্যান করে।

সারাংশ যখন নির্ধারিত ছাঁটাইয়ে ফিরে যাওয়া উচিত, তখন এটি সরাসরি রেজিস্টার করুন:

⟦CODE7⟧

`fallback` সরাসরি `Agent(..., capabilities=[fallback])` দিয়ে রেজিস্টার করুন। এর ঐচ্ছিক
`max_tokens` বা `max_fraction` trigger chain চালায় শুধু তখনই, যখন আনুমানিক context token
সীমা ছাড়ায়। ভগ্নাংশ request-এর মডেলের বিপরীতে নির্ধারিত হয়; `context_window`
তার window override করে আর `fallback_context_window` অজানা মডেলের window দেয়।
`tokenizer` token অনুমান কাস্টমাইজ করে। hook-টি pin করা part রক্ষা করে আর compact করা
history স্থায়ী করে, history বদলালে প্রচলিত `compact_messages` span পাঠিয়ে।

কোনো trigger কনফিগার না থাকলে request hook কিছুই করে না। সরাসরি `compact()` আর
`compact_now()` call সীমা যা-ই হোক chain চালায়, তাই এটি অন্য সংযোজনকারী কৌশলের ভেতরে
আর হাতে করা compaction-এর জন্য ব্যবহারযোগ্য থাকে। chain যখন প্রতিটি child-এর `compact()` method ডাকে,
তখন child-এর নিজের trigger পাশ কাটানো হয়।

/// tip | উদাহরণ দিয়ে বুঝি

`TieredCompaction` হলো "যথেষ্ট না হলে পরের ধাপ" — সস্তা থেকে দামি। `FallbackCompaction` হলো "ভেঙে পড়লে বিকল্প" — সারাংশকারী মডেল যদি নেটওয়ার্ক error-এ পড়ে, run মরে না গিয়ে sliding window দিয়ে পুরোনো অংশ কেটে চলতে থাকে। একটি "উন্নতির সিঁড়ি", অন্যটি "জরুরি নির্গমন পথ"।

///

## `ClampOversizedMessages`: একটি নিয়ন্ত্রণহীন generation থেকে বাঁচা { #clampoversizedmessages-surviving-a-runaway-generation }

পুনরাবৃত্ত whitespace-এর একটিমাত্র model response, বা বিশাল payload-ওয়ালা একটিমাত্র tool call, এমন একটি part তৈরি করতে পারে যা এত বড় যে *পরের* request provider-এর context সীমা ছাড়িয়ে যায়। অন্য কোনো কৌশল সেখানে পৌঁছাতে পারে না: `SlidingWindowCompaction` সবচেয়ে পুরোনো message বাদ দেয় কিন্তু অপরাধীটি সবচেয়ে নতুন; `ClearToolResults` শুধু tool *result* ছোঁয়; `WarnNearLimits` কখনো history সম্পাদনা করে না; আর history `SummarizingCompaction`-কে দিলে একই সীমায় আটকায়।

`ClampOversizedMessages` অপরাধী part-টি জায়গাতেই কাটে, একটি মাথার অংশ আর একটি লেজের অংশ রেখে, মাঝে একটি `[clamped: removed N of M characters]` চিহ্নসহ। বিকৃত generation হলো কম-entropy-র পুনরাবৃত্তি, তাই মাথা/লেজের অংশ রাখলে সামান্যই হারায়।

⟦CODE8⟧

একটি part সীমিত (clamp) হয় শুধু তখনই, যখন এটি অতিরিক্ত বড় *আর* clamp আসলেই এটিকে ছোট করে, তাই `keep_head_chars + keep_tail_chars` আপনার প্রতি-part সীমার অনেক নিচে রাখুন।

এটি প্রতিটি `ModelResponse`-এর ভেতরে দুই ধরনের part সীমিত করে:

- **Response text** (`TextPart`) — জরুরি ক্ষেত্র, একটি নিয়ন্ত্রণহীন model-response text part।
- **Tool-call args** (`ToolCallPart`), যখন `clamp_tool_call_args=True` (ডিফল্ট) — বিশাল payload-এর একই ব্যর্থতার আকার (যেমন একটি নিয়ন্ত্রণহীন `write_plan`)। args একটি ছোট JSON object `{"_clamped": "<head>...<tail>"}` দিয়ে প্রতিস্থাপিত হয়, যাতে সেগুলো বৈধ function argument থাকে; মূল call ইতিমধ্যে চলেছে, তাই এটি শুধু history-র কপি ছোট করে। শুধু response text সীমিত করতে `clamp_tool_call_args=False` সেট করুন। framework-typed call part — core-এর `search_tools` আর `load_capability` call — কখনো সীমিত হয় না, কারণ সংরক্ষিত history পুনরুদ্ধারের সময় (যেমন একটি `StepPersistence` resume) এদের typed args যাচাই হয়, আর `_clamped` object সেই আসা-যাওয়ায় ব্যর্থ হতো।

request-দিকের part (user prompt, tool *return*, system prompt) ইচ্ছাকৃতভাবে আওতার বাইরে: user input নীরবে নতুন করে লেখা উচিত নয়, আর অতিরিক্ত বড় tool return হলো [`ToolOutputLimits`](tool-output-limits.md)-এর কাজ, যা tool তৈরি করার সময়েই return ছোট করে। `ClearToolResults` সবচেয়ে নতুন `keep_pairs`টি ফল অক্ষত রাখে, আর `keep_pairs=0`-এ এটি একটি নতুন return ছোট না করে সরাসরি খালি করে।

এটি `TieredCompaction`-এর প্রথম স্তর হিসেবে ব্যবহার করুন, `ClearToolResults`-এর আগে:

⟦CODE9⟧

## `ClearToolResults`: সস্তা প্রথম স্তর { #cleartoolresults-the-cheap-first-tier }

একটি agent-এর context-এ সাধারণত tool output-ই বেশি থাকে, আর data আবার দরকার হলে agent সাধারণত tool-টি আবার চালাতে পারে। `ClearToolResults` সবচেয়ে পুরোনো tool *result*-গুলোর content একটি ছোট placeholder দিয়ে প্রতিস্থাপন করে, আর সবচেয়ে সাম্প্রতিক `keep_pairs`টি tool-call / tool-return জোড়া অক্ষত রাখে। tool call-গুলো তাদের এখন-খালি ফলের সাথে জোড়া থাকে, তাই history বৈধ থাকে। একটি retry করা return, যা মডেলকে call-টি আবার করতে বলে, একটি ফল নয়: এটি কখনো মোছা হয় না আর `keep_pairs`-এ গোনা হয় না, আর `DeduplicateFileReads` একটি retry করা পড়াকে আগেরটির জায়গা নিতে দেয় না।

framework-typed tool result — core-এর `search_tools` আর `load_capability` return — অক্ষত রাখা হয় (একটি ছোট token মেঝে), কারণ পরের request-এ এদের structured content আবার parse হয়, আর `dataclasses.replace` দিয়ে নতুন করে লিখলে validation পাশ কাটিয়ে part নষ্ট হতো। [`FileSystem`](filesystem.md)-এর typed `read_file` result (`ReadFileReturnPart`) অন্য যেকোনো ফলের মতোই মোছা হয় আর তাদের type রাখে, যদি না তাদের `metadata` `None` বা একটি `dict` ছাড়া অন্য কিছু হয়: একটি মোছা ফল তার `metadata`-তে চিহ্নিত হয়, তাই যার metadata চিহ্নটি ধরতে পারে না সেটি না-মোছা থাকে।

⟦CODE10⟧

মোছা call-গুলোর argument-ও খালি করতে `clear_tool_inputs=True` সেট করুন, আর যে tool-গুলোর ফল কখনো মোছা হবে না তাদের নামের একটি set `exclude_tools`-এ দিন।

`max_messages`-এর ক্ষেত্রে, গণনা শুরু হয় শেষ মোছা ফলের পরে, কারণ মোছা content খালি করে কিন্তু কোনো message সরায় না। তখন মোছা হয় ব্যাচে: একবার মোছার পর, পরেরটি অপেক্ষা করে যতক্ষণ না শেষ মোছা ফলের পরে `max_messages`-এর বেশি message আসে, তাই মাঝের request-গুলো cache করা prefix নতুন করে না লিখে বাড়ায়। রাখা জোড়াগুলো এতে গোনা হয়: একবার মোছার ঠিক পরে, শেষ মোছা ফলের পরে মোটামুটি `2 * keep_pairs`টি message থাকে, আর প্রতিটি tool ধাপ আরও দুটি যোগ করে। তাই প্রতিটি মোছার পর মোটামুটি `(max_messages - 2 * keep_pairs) / 2`টি tool ধাপ পরে আরেকটি আসে, আর `2 * keep_pairs` বা তার নিচে হলে এটি প্রতিটি request-এ মোছে। এই ফাঁক মাথায় রেখে মান বাছুন।

/// info | উদাহরণ দিয়ে হিসাব

ধরুন `ClearToolResults(max_messages=30, keep_pairs=5)`। মোছার পর শেষ মোছা ফলের পরে প্রায় `2 × 5 = 10`টি message থাকে। পরের মোছা আসবে প্রায় `(30 − 10) / 2 = 10`টি tool ধাপ পরে — মাঝের 10টি request cache থেকে পড়তে পারবে। কিন্তু `max_messages=10` দিলে (`2 × keep_pairs`-এর সমান) প্রতিটি request-এই মুছবে আর cache প্রতিবার ভাঙবে।

///

## `DeduplicateFileReads`: বাতিল হয়ে যাওয়া পড়া বাদ দেওয়া { #deduplicatefilereads-drop-superseded-reads }

একই ফাইল একাধিকবার পড়া হলে শুধু সর্বশেষ পড়াটিই তার content রাখে; আগের পড়াগুলো একটি placeholder দিয়ে খালি করা হয়, জোড়া অক্ষত রেখে।

কোনো ডিফল্ট `file_key` নেই: একটি ফাইল পড়া চেনা agent-নির্দিষ্ট, আর ভুল অনুমান জীবন্ত data বাদ দিয়ে ফেলত। একটি callable দিন, যা একটি `ToolCallPart`-কে একটি স্থির ফাইল key-তে map করে, বা call-টি ফাইল পড়া না হলে `None` দেয়:

⟦CODE11⟧

কোনো `max_messages` বা `max_tokens` trigger সেট না থাকলে `DeduplicateFileReads` প্রতিটি request-এ চলে। এটি সস্তা আর প্রায় ক্ষতিহীন, তাই সাধারণত এই ডিফল্টই আপনি চান।

## `SlidingWindowCompaction`: শুধু সাম্প্রতিক লেজ রাখা { #slidingwindowcompaction-keep-only-the-recent-tail }

কথোপকথন কনফিগার করা সীমা ছাড়ালে, `SlidingWindowCompaction` সবচেয়ে পুরোনো পুরো message বাদ দিয়ে একটি লেজ রাখে, tool-call / tool-return জোড়া অক্ষত রেখে। শুধু সাম্প্রতিক turn দরকার আর পুরোনো context পুরোপুরি ফেলে দেওয়া যায় — তখন এটি বেছে নিন।

⟦CODE12⟧

ডিফল্টভাবে `preserve_first_user_message=True` প্রথম user turn রাখে (system prompt-এর পাশাপাশি), এমনকি সেটি window-এর বাইরে পড়লেও, যাতে agent মূল কাজটি না হারায়। `keep_messages=0` তবুও সবচেয়ে নতুন message — যে request-এর উত্তর দেওয়া হচ্ছে — রাখে। message-এর সংখ্যার বদলে মূল message text-এর একটি ন্যূনতম পরিমাণ রাখতে `keep_messages`-এর বদলে `keep_tokens` দিন।

### স্বয়ংক্রিয় compaction-এর পরে token রাখা { #token-retention-after-automatic-compaction }

`max_tokens` ঠিক করে compaction কখন চলবে; একটি ধনাত্মক `keep_tokens` ঠিক করে মূল সাম্প্রতিক history-র কতটা টিকে থাকবে। `SlidingWindowCompaction` আর `SummarizingCompaction` দুটোই সেই পুরো message অন্তর্ভুক্ত করে যা রাখার লক্ষ্য পার করে, মেলানো tool call আর tool-নির্দিষ্ট retry response-এর জন্য পেছনে বাড়িয়ে।

যেমন, `max_tokens=170_000`-এ স্বয়ংক্রিয় compaction এমন একটি 190k-token history পেতে পারে, যাতে আছে 139k পুরোনো token, একটি সাম্প্রতিক 48k-token message, আর একটি 3k-token নতুনতম লেজ। `keep_tokens=50_000` দিলে এটি 51k-token শেষাংশ রাখে, লক্ষ্য পার করা message-সহ। summarizing compaction পুরোনো prefix-এর সারাংশ করে; sliding-window compaction সেটি ফেলে দেয়।

শেষাংশটি মাপা হয় [`keep_tokens`-এ কী গোনা হয়](#what-counts-toward-keep_tokens)-এ বর্ণিত উপায়ে: history-তে থাকলে provider-জানানো usage, নইলে কনফিগার করা `tokenizer` বা message-part text-এর ওপর ডিফল্ট অক্ষর-ভিত্তিক অনুমান, system-prompt part-সহ। যুক্ত `ModelRequest.instructions` রাখার লক্ষ্য পূরণ করে না। পুরো history লক্ষ্যের নিচে হলে, compaction কোনো সারাংশ call ছাড়াই এটি অপরিবর্তিত রাখে। `keep_tokens=0` একটি ন্যূনতম-রাখার মেঝের বদলে শূন্য-token লক্ষ্য ব্যবহার করে; `None` `keep_messages` ব্যবহার করে।

পুরো message আর tool নির্ভরতা লক্ষ্য ছাড়িয়ে যেতে পারে। সারাংশ, receipt, আবার ঢোকানো pin আর রাখা পুরোনো user turn বাড়তি; এগুলো সুরক্ষিত শেষাংশকে সরায় না। সেই শেষাংশের ভেতরে থাকা বিদ্যমান receipt অপরিবর্তিত থাকে। এটি context-window-এ আঁটার নিশ্চয়তা নয়: caller-দের বাকি request budget পরীক্ষা করতে হবে আর দরকার হলে থামতে, মডেল বদলাতে, বা স্পষ্টভাবে রাখার লক্ষ্য কমাতে হবে। যে প্রতিটি fallback-কে এটি রক্ষা করতে হবে, তাতে একই রাখার লক্ষ্য কনফিগার করুন।

একটি বড় message রাখা শেষাংশ আর সারাংশকে `max_tokens`-এর ওপরে রাখতে পারে। যতক্ষণ না নতুন message-গুলো এটি ছাড়াই লক্ষ্য পূরণ করে, শেষাংশের আগের সবকিছু ইতিমধ্যে হিসাবে আছে: একটি আগের সারাংশ, receipt, pin, আর এমনিতেই হুবহু রাখা message, যেমন সংরক্ষিত প্রথম user turn। `SummarizingCompaction`-এর তখন সারাংশ করার মতো নতুন কিছু থাকে না, তাই প্রতিটি request-এ নিজের সারাংশের আবার সারাংশ না করে এটি কোনো সারাংশ call ছাড়াই history অপরিবর্তিত রাখে। request তবুও trigger-এর ওপরে বের হয়; দরকার হলে `ClampOversizedMessages` একটি অতিরিক্ত বড় message ছোট করতে পারে।

## `SummarizingCompaction`: সংকুচিত করুন, ফেলে দেবেন না { #summarizingcompaction-compress-do-not-discard }

পুরোনো context যখন এখনও জরুরি কিন্তু সংকুচিত করতে হবে, `SummarizingCompaction` একটি আলাদা model call দিয়ে পুরোনো message-গুলোর সারাংশ করে আর সেগুলোকে একটি গোছানো সারাংশ দিয়ে প্রতিস্থাপন করে, সাম্প্রতিক লেজ আর tool-call-এর অখণ্ডতা রেখে। এটি দামি স্তর, তাই সস্তা pass-গুলোর পেছনে ব্যবহার করাই ভালো (দেখুন `TieredCompaction`)।

⟦CODE13⟧

`model` একটি model নাম বা একটি `Model` নেয়; `None` রাখলে চলমান agent-এর মডেল উত্তরাধিকারে পায়। সেই মডেলকে text লিখতে হয়, তাই যে agent এমন মডেল চালায় যা পারে না — যেমন TypeSafe-এর Jev-এর মতো একটি decision model — তার `model=`-এ একটি language model সেট করা লাগে; না দিলে প্রথম compaction সেটি জানিয়ে একটি `UserError` raise করে। খালি বা শুধু whitespace-এর সারাংশ সারাংশ run-এর output retry-র মধ্যে আবার চেষ্টা করা হয়। সেই retry ফুরিয়ে গেলে history একটি খালি সারাংশ দিয়ে প্রতিস্থাপন না করে `UnexpectedModelBehavior` raise হয়। এর নেস্টেড সারাংশ run parent-এর usage limit উত্তরাধিকারে পায়, আর অপেক্ষমাণ parent request-এর জন্য একটি সসীম request limit থেকে একটি request সংরক্ষণ করে রাখে। এই সীমা retry-তেও প্রযোজ্য: সারাংশ run আগে তার budget ফুরিয়ে ফেললে বরং `UsageLimitExceeded` raise করে। যেকোনো ব্যর্থতায় fallback করতে `FallbackCompaction`-এর `fallback_on=(UnexpectedModelBehavior, UsageLimitExceeded)` সেট করুন, ভালো হয় এমন একটি fallback কৌশল দিয়ে যা কোনো model request করে না। এটি parent run-এর সীমা বাড়ায় না। আলাদা সারাংশ call-কে ওই মডেলের ডিফল্ট থেকে ভিন্ন সেটিং দিতে `model_settings` দিন; দেওয়া সেটিং মডেল বা settings dictionary না বদলেই মডেলের ডিফল্টের ওপর মিশে যায়। সারাংশ agent-এ capability যুক্ত করতে `summarization_capabilities` দিন; বাইরের agent-এর capability সারাংশ call-এ চলে না। ডিফল্টভাবে `incremental=True` সবচেয়ে নতুন বিদ্যমান সারাংশকে একটি নোঙর হিসেবে হালনাগাদ করে। এটি আগের release-গুলো থেকে সারাংশ-call-এর prompt বদলায়; আগের নতুন-করে-তৈরি আচরণ রাখতে `incremental=False` সেট করুন। `keep_messages=0` তবুও সারাংশের পাশে সবচেয়ে নতুন message — যে request-এর উত্তর দেওয়া হচ্ছে — রাখে।

সারাংশ request-এর দুটি prompt-পৃষ্ঠই field: `summary_prompt` হলো user-turn template (এতে একটি `{messages}` placeholder থাকতে হবে আর অন্য কোনো replacement field নয়; অন্য যেকোনো prompt একটি `HarnessDeprecationWarning` দেয় আর ভবিষ্যতের release-এ `ValueError` raise করবে), আর `instructions` ভেতরের agent-এর স্থির instructions সেট করে, যা Pydantic AI request-এর system prompt-এ পাঠায়। সারাংশকারী endpoint একটি স্থির শুরুর instruction চাইলে `instructions` override করুন।

সেই template-এ দেওয়া message-গুলো একটি transcript হিসেবে render হয়, প্রতি part-এ একটি `<message>` element (প্রতিটি user prompt, system prompt, response text, tool call আর tool return), তার role আর — tool call বা return হলে — tool নাম দিয়ে tag করা। transcript-এর নিজের tag-এর মতো দেখায় এমন content, যেকোনো case বা spacing-এ, escape করা হয়, তাই একটি tool return তার message বন্ধ করে আরেকটি জাল করতে বা transcript আগেভাগে শেষ করতে পারে না। প্রতিটি tool return, সেই escape-এর পরে, `tool_return_max_chars`-এ (ডিফল্ট 500) অক্ষরে সীমিত, রাখা user turn-এর মতো একই স্পষ্ট কাটা-চিহ্ন দিয়ে। সারাংশকারীর context window payload ধরার মতো বড় হলে এটি বাড়ান, বা প্রতিটি return পুরো render করতে `None` সেট করুন। একটি harness capability user channel-এ যোগ করেছে আর তার `TextContent.metadata`-তে `pydantic-ai-harness.` দিয়ে শুরু হওয়া একটি `origin` দিয়ে tag করেছে এমন content user message নয়। আজকের দিনে সেটি একটি [`BackgroundTools`](background-tools.md) result, [`TrajectoryJudge`](trajectory-judge.md) feedback আর একটি [`Memory`](memory.md) snapshot, পুরোনো একটি release সাধারণ string দিয়ে চিহ্নিত করা একটিসহ। tag করা content `role="user"` হিসেবে নয়, একটি `<harness_data origin="...">` element হিসেবে render হয়, tool return-এর মতো সীমিত। transcript-এ এমন content থাকলে, সারাংশ request সারাংশকারীকে এটিকে ব্যবহারকারীর অনুরোধ বা স্থায়ী শর্ত হিসেবে না ধরতেও বলে; অন্য সারাংশ request অপরিবর্তিত। `max_tokens` আর `keep_tokens` নিয়ন্ত্রণ করে compaction কখন চলবে আর কোন history message রাখা হবে; এগুলো সারাংশ-request payload সীমিত করে না।

`event_stream_handler` সেট না থাকলে সারাংশ request non-streaming। সারাংশ লেখা হওয়ার সময় দেখতে একটি handler দিন, অথবা event না সামলে streaming request পথ নিতে `drain_summary_events` দিন — non-streaming request প্রত্যাখ্যান করা সারাংশকারী endpoint-এর এটিই দরকার:

⟦CODE14⟧

কোনো transport সব জায়গায় কাজ করে না, তাই এটি ডিফল্ট নয়, বাছাইয়ের বিষয়: কিছু endpoint non-streaming request প্রত্যাখ্যান করে আর অন্যগুলো streaming। handler সারাংশ run-এর নিজের `RunContext` আর event stream পায়; বাইরের `Agent.run(...)`-এর handler উত্তরাধিকারে আসে না আর কখনো সারাংশের token delta দেখে না।

### Usage-এর হিসাব { #usage-accounting }

সারাংশ call মডেলের কাছে একটি আসল request, তাই এর পুরো usage — token **আর** request নিজে — run-এর `ctx.usage`-এ যোগ হয়। এটি ইচ্ছাকৃত: এটি খরচ সৎ রাখে, request গণনা সামঞ্জস্যপূর্ণ রাখে (একটি model request যা একটি হিসেবে গোনা হয়নি, সেটিই হতো আশ্চর্যের), আর একটি `UsageLimits` request limit-কে একটি নিয়ন্ত্রণহীন compaction ধরতে দেয়। নেস্টেড run parent-এর অন্য সীমাগুলো অপরিবর্তিত পায়; সসীম request limit এক কমানো হয়, যাতে এটি parent request-এর জন্য ইতিমধ্যে অনুমোদিত slot খরচ করতে না পারে। সারাংশ run parent run-এর `conversation_id`-এর অধীনে নথিভুক্ত হয়, তাই এর request, span আর খরচ যে কথোপকথন compact করে তার সাথে দলবদ্ধ হয়। একটি run-request বা iteration limiter তাই তার request-গুলোর মধ্যে compaction call দেখবে।

একটি durable-execution capability যুক্ত থাকলে, সারাংশ call একটি অবদান রাখা durable
operation হিসেবে চলে, তাই replay আবার মডেল না ডেকে রেকর্ড করা সারাংশ ব্যবহার করে। `model`
সেট না থাকলে operation run-এর মডেল ব্যবহার করে। capability একটি স্থির ডিফল্ট `id` বহন করে, যা
durable execution একই পরিচয়ে operation পুনরুদ্ধারে ব্যবহার করে। একটি কাস্টম
মান দিয়ে override করলে চলমান workflow-এর রেকর্ড করা operation অনাথ হয়ে যায়, তাই একটি workflow চালু হলে এটি স্থির রাখুন।

/// warning | সাধারণ ভুল

`UsageLimits(request_limit=10)` দিয়ে ভাবছেন agent 10টি "নিজের" request পাবে? সারাংশ call-ও একটি request হিসেবে গোনা হয় — তাই compaction ঘন ঘন চললে আপনার request budget আগেই ফুরাবে। সীমা ঠিক করার সময় compaction-এর call-এর জন্য জায়গা রাখুন।

///

## `RelevanceCompaction`: কাজের যা এখনও দরকার তা রাখা { #relevancecompaction-keep-what-the-task-still-needs }

`RelevanceCompaction` history-র প্রতিটি পুরোনো ধাপ নিয়ে একটি judge মডেলকে প্রশ্ন করে, আর উত্তরের ভিত্তিতে ধাপটি হুবহু রাখে, ছোট করে, বা বাদ দেয়। পুরোনো context যখন অসমান — কিছু tool result-এ এমন code বা error text আছে যা agent-এর এখনও হুবহু লাগবে, অন্যগুলো অকেজো বোঝা, আর সবকিছুর একটি সারাংশ হুবহু অংশগুলো হারিয়ে ফেলত — তখন এটি বেছে নিন।

⟦CODE15⟧

judge, `model`, বাধ্যতামূলক। একটি [decision model](../models/decision.md), যেমন [System One](../models/system-one.md)-এ `system-one:<model>` (Ollama local-ভাবে যে মডেল চালায় সেগুলোসহ) বা TypeSafe-এর `typesafe:jev-latest`, একটি সম্ভাবনা (probability) দিয়ে উত্তর দেয়। structured output সাপোর্ট করে এমন অন্য যেকোনো মডেল একই দুটি field পূরণ করে, তাই `model` একটি `FallbackModel`-ও নেয়, যা আগে একটি decision model আর তারপর একটি language model চেষ্টা করে।

একটি *ধাপ* হলো একটি model response, সাথে যে request-গুলো তার উত্তর দেয়: তার tool result, retry feedback, আর পরের user prompt। একটি ধাপ পুরোটাই রাখা বা সরানো হয়, তাই একটি tool call কখনো তার ফল হারায় না। প্রথম response-এর আগের সবকিছু (system prompt, প্রথম user message, আর একটি আগের সারাংশ) আর history-র সবচেয়ে সাম্প্রতিক `keep_tokens` (ডিফল্ট 8,000) কখনো বিচার করা হয় না। pin করা content টিকে থাকে, এমনকি তার ধাপ সরানো হলেও।

বাকি প্রতিটি ধাপ একটি request-এ দুটি প্রশ্ন দিয়ে বিচার করা হয়:

- `needed_verbatim`: "Will the agent need the exact content of this earlier step, such as code, file contents, identifiers, numbers, commands or error text, to finish the current task?" (বর্তমান কাজ শেষ করতে agent-এর কি এই আগের ধাপের হুবহু content — code, ফাইলের content, identifier, সংখ্যা, command বা error text — লাগবে?)
- `still_matters`: "Does this earlier step record a fact, decision, change, result or user instruction that still matters for the current task?" (এই আগের ধাপ কি এমন কোনো তথ্য, সিদ্ধান্ত, পরিবর্তন, ফল বা ব্যবহারকারীর নির্দেশ রেকর্ড করে যা বর্তমান কাজের জন্য এখনও গুরুত্বপূর্ণ?)

judge-কে দেখানো হয় বর্তমান কাজ (প্রথম আর সর্বশেষ user prompt, সাথে `compact_now`-এ দেওয়া যেকোনো `focus`), কথোপকথনের সবচেয়ে সাম্প্রতিক অংশ, আর ধাপটি নিজে, তার tool result-সহ। `judge_step_tokens`-এর (ডিফল্ট 2,000) চেয়ে লম্বা একটি ধাপ তার শুরু আর শেষ দিয়ে দেখানো হয়, আর কাজ আর সাম্প্রতিক কথোপকথন প্রতিটি `judge_context_tokens`-এ (ডিফল্ট 500) সীমিত। ডিফল্টগুলো একটি request-কে ছোট local decision model-এর 8,192-token input-এর মধ্যে রাখে, কারণ code আর JSON ~4-অক্ষর-প্রতি-token অনুমানের প্রায় দ্বিগুণ token নেয়। judge-কে বলা হয় এর সবই অবিশ্বস্ত data, আর prompt-এর নিজের tag-এর মতো দেখায় এমন text escape করা হয়।

ধাপগুলো বাছা হয় একটি token budget-এর বিপরীতে র‍্যাঙ্ক দিয়ে, কখনো একটি স্থির সীমার সাথে সম্ভাবনা তুলনা করে নয়: request-এর আকারের সাথে একটি judge-এর সম্ভাবনাগুলো সামগ্রিকভাবে সরে যায়, কিন্তু সে ধাপগুলোকে যে ক্রমে সাজায় তা টিকে থাকে। history compact হয় `target_tokens`-এ (বা `target_fraction`), যার ডিফল্ট trigger-এর অর্ধেক:

1. লক্ষ্যে আঁটা পর্যন্ত ধাপগুলো `needed_verbatim`-এর ক্রমে হুবহু রাখা হয়।
2. বাকিগুলো `still_matters`-এর ক্রমে ছোট করা হয়। একটি `summarizer` থাকলে, সেগুলো history-র মাথার পরে বসানো একটি সারাংশে লেখা হয়, প্রতি compaction-এ সর্বোচ্চ `summary_input_tokens` (ডিফল্ট 30,000) পরিমাণ ধাপ। না থাকলে, যতক্ষণ লক্ষ্যে আঁটে, প্রতিটির tool result তার প্রথম `truncated_result_chars` (ডিফল্ট 300) অক্ষরে কাটা হয়, সাথে একটি নোট যে tool-টি আবার ডাকা যায়।
3. যা বাকি থাকে তা বাদ পড়ে, user prompt থাকা ধাপ ছাড়া: summarizer ছাড়া এটি কাটা হয়, আর summarizer থাকলে `summary_input_tokens`-এ আঁটা পর্যন্ত সারাংশ হয়, নইলে হুবহু রাখা হয়।

`summarizer` হলো একটি `SummarizingCompaction`, যা ব্যবহার হয় তার মডেল, prompt আর সেটিংয়ের জন্য; এর trigger আর `keep_*` field কখনো দেখা হয় না, তাই `max_messages=1`-এর মতো যেকোনো trigger চলে। summarizer-এর `incremental=True` (ডিফল্ট) থাকলে আগের সারাংশ হালনাগাদ হয়; `incremental=False` থাকলে সেটি ধাপগুলোর সাথে আবার সারাংশ হয়। ধাপ সারাংশ বা বাদ হলে `receipts=True` একটি [receipt](#compaction-receipts) যোগ করে।

judge request একসাথে চলে, একবারে সর্বোচ্চ `judge_concurrency` (ডিফল্ট 8)টি। প্রতিটি রায় instance-এ কাজ আর ধাপের content-এর অধীনে মনে রাখা হয়, তাই একই কাজ নিয়ে পরের একটি compaction শুধু নতুন ধাপগুলো বিচার করে। একটি compaction-এর সব judge request একটি `UsageLimits` request limit-এর বিপরীতে একটি request হিসেবে গোনা হয়, কোনোটি পাঠানোর আগে পরীক্ষা করা হয়। এদের token run-এর usage-এ যোগ হয় আর ফিরে এলে তার token আর খরচের সীমার বিপরীতে পরীক্ষা হয়, সারাংশ request-এর মতো। Ollama চালানো একটি ল্যাপটপে, কয়েক হাজার token-এর একটি ধাপের জন্য একটি judge request 5 থেকে 10 সেকেন্ড নিয়েছিল, তাই সেখানে লম্বা একটি history-র প্রথম compaction কয়েক মিনিট নিতে পারে; পরেরগুলো শুধু নতুন ধাপ বিচার করে।

একটি judge error ছড়িয়ে পড়ে, যেমন একটি সারাংশ error পড়ে। কোনো model request করে না এমন একটিতে fallback করতে কৌশলটি `FallbackCompaction`-এ মুড়ে দিন:

⟦CODE16⟧

`TieredCompaction`-এর স্তর হিসেবে, এর `target_tokens` স্পষ্টভাবে সেট করুন: একটি স্তরের `compact` তার নিজের লক্ষ্য দিয়ে চলে, আর trigger যখন শুধু constructor সন্তুষ্ট করতে আছে, তখন trigger-এর অর্ধেকের ডিফল্টের কোনো মানে নেই।

একটি durable-execution capability যুক্ত থাকলে, রায় আর সারাংশ চলে capability-র স্থির ডিফল্ট `id` `relevance_compaction`-এর durable operation `judge` আর `summarize` হিসেবে, তাই replay আবার মডেল না ডেকে সেগুলো পুনরায় ব্যবহার করে।

দুই-প্রশ্নের বিভাজন আর সমসাময়িক প্রতি-ধাপ request এসেছে [fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) (MIT) থেকে, যা TypeSafe-এর Jev দিয়ে Claude Code transcript compact করে। এর পরিমাপই judge-কে প্রতিটি ধাপের content দেখানো আর র‍্যাঙ্ক দিয়ে ধাপ বাছার প্রেরণা দিয়েছে। কোনো code শেয়ার করা হয়নি।

/// info | এক নজরে: প্রতিটি পুরোনো ধাপের ভাগ্য

| ধাপ | কী হয় |
|---|---|
| `needed_verbatim` উঁচু র‍্যাঙ্ক (code, error text…) | লক্ষ্যে আঁটা পর্যন্ত হুবহু রাখা |
| `still_matters` উঁচু র‍্যাঙ্ক | summarizer থাকলে সারাংশে, নইলে tool result 300 অক্ষরে কাটা |
| বাকি | বাদ (user prompt থাকলে কাটা বা সারাংশ) |
| প্রথম response-এর আগে, শেষ 8,000 token, pin | কখনো বিচার হয় না, সবসময় থাকে |

///

## `WarnNearLimits`: নতুন করে লেখার বদলে সতর্ক করা { #warnnearlimits-warn-instead-of-rewrite }

`WarnNearLimits` কখনো history সম্পাদনা করে না। run একটি কনফিগার করা সীমার কাছে এলে, এটি প্রতিটি request-এ একটি URGENT (তারপর CRITICAL) সতর্কতা যোগ করে, যাতে মডেলের নিচ থেকে তার context নতুন করে লেখা না হয়ে বরং মডেল কাজ গুটিয়ে আনে। প্রতিটি সতর্কতা একটি [request-scoped system prompt](../message-history.md#request-scoped-system-prompts): মডেল এটি শুধু নিজের request-এর জন্য দেখে, আর এটি message history-তে থাকে, তাই আগের request-গুলো অপরিবর্তিত পাঠানো হয় আর prompt cache ও মডেলের আগের reasoning বৈধ থাকে। পুরোনো সংস্করণ যে সতর্কতা user prompt হিসেবে পাঠাত, সংরক্ষিত history-তে সেগুলো থাকলে request থেকে বাদ রাখা হয়। এগুলো চেনা হয় part-এর metadata দিয়ে, text দিয়ে নয়, তাই একটি সতর্কতা উদ্ধৃত করা user prompt কখনো সরানো হয় না।

⟦CODE17⟧

সতর্কতা শুরু হয় `warning_threshold`-এ (ডিফল্ট `0.7`, সীমার একটি ভগ্নাংশ) আর বাকি request সংখ্যা `critical_remaining_iterations`-এ (ডিফল্ট `3`) নামলে iteration-এর জন্য CRITICAL হয়ে যায়। এটি তিন রকম সীমা দেখে — `max_iterations`, `max_context_tokens` (বা `max_context_fraction`), আর `max_total_tokens` — আর ডিফল্টভাবে যেগুলো কনফিগার করা সেগুলোতে সতর্ক করে; `warn_on` দিয়ে তা সংকুচিত করুন।

## cache-এর বিনিময় { #cache-tradeoff }

মুছে ফেলা, ডুপ্লিকেট বাদ দেওয়া, সীমিত করা আর সারাংশ করা — সবই message content নতুন করে লেখে, যা সম্পাদনার বিন্দু থেকে provider-এর prompt cache অকেজো করে — পরের request একটি cache-write-এর দাম দেয়। `ClearToolResults`-এর জন্য, যে মোছা cache ভাঙার মতো যথেষ্ট উদ্ধার করে না তা এড়াতে `min_clear_tokens` ব্যবহার করুন। `ClampOversizedMessages`-এর জন্য cache ভাঙা অনিবার্য, কারণ বিকল্পটি হলো একটি ব্যর্থ request।

## Tracing { #tracing }

core instrumentation সক্রিয় থাকলে (`Instrumentation` capability, `agent.instrument`, বা `Agent.instrument_all()`), প্রতিটি কৌশল আসলে compact করার মুহূর্তে run-এর tracer-এ একটি `compact_messages` span পাঠায় — অর্থাৎ `before_model_request`-এ, কৌশলের সীমা ছাড়ালে (`ClampOversizedMessages` পাঠায় শুধু একটি part আসলে সীমিত হলে)। `TieredCompaction` প্রতি স্তরে একটি না পাঠিয়ে পুরো ওঠার জন্য একটি span পাঠায়, কারণ এটি প্রতিটি স্তরের `compact` সরাসরি চালায়। instrumentation ছাড়া tracer কিছুই করে না, তাই span কোনো বাড়তি ভার যোগ করে না।

span-এর নাম স্থির `compact_messages`; span-এর বৈচিত্র্য (cardinality) কম রাখতে কৌশলটি নামের অংশ নয়, একটি attribute। Attribute:

| Attribute | Type | মানে |
|---|---|---|
| `gen_ai.conversation.compacted` | bool | সবসময় `true`; compact করা context-এর জন্য OpenTelemetry GenAI convention-এর flag |
| `compaction.strategy` | str | কৌশলের class নাম (যেমন `SlidingWindowCompaction`, `SummarizingCompaction`) |
| `compaction.messages_before` | int | compaction-এর আগে message সংখ্যা |
| `compaction.messages_after` | int | compaction-এর পরে message সংখ্যা |
| `compaction.tokens_before` | int | compaction-এর আগে আনুমানিক token সংখ্যা |
| `compaction.tokens_after` | int | compaction-এর পরে আনুমানিক token সংখ্যা |

`gen_ai.conversation.compacted` হলো GenAI semantic convention-এর flag; বাকিগুলো harness-নির্দিষ্ট। token গণনা সেট থাকলে কৌশলের `tokenizer` ব্যবহার করে, নইলে ~4-অক্ষর-প্রতি-token অনুমান। কাঁচা message content রেকর্ড হয় না।

`SummarizingCompaction` তার summarizer চালায় `summarizing_compaction` নামের একটি নেস্টেড `Agent` হিসেবে, তাই `Agent.instrument_all()` (বা `logfire.instrument_pydantic_ai()`)-এর অধীনে এর run-গুলো `agent_name = summarizing_compaction` বহন করে। parent agent থেকে আলাদা করে সারাংশের usage আর খরচ দেখতে এটি দিয়ে filter করুন।

`RelevanceCompaction` `compact_messages`-এর ভেতরে একটি `select compaction steps` span যোগ করে। এটি রেকর্ড করে ধাপের সংখ্যা আর কতগুলো মনে রাখা নয়, বিচার করা হয়েছে (`relevance_compaction.steps`, `relevance_compaction.steps_judged`), প্রতিটি স্তরের ধাপ আর token (`relevance_compaction.keep.steps`, `relevance_compaction.keep.tokens`, আর `reduce` ও `drop`-এর জন্যও একই), আর প্রতি ধাপে একটি `relevance_compaction.step` event, তার অবস্থান, আকার, দুটি উত্তর, মনে রাখা ছিল কি না, আর তার স্তরসহ। কোনো message content রেকর্ড হয় না। judge-এর নিজের run instrument করা হয় না, কারণ এদের prompt কথোপকথন বহন করে।

## Compaction receipt { #compaction-receipts }

compaction হলো এমন একটি স্মৃতি-মোছা যা মডেল আটকাতে পারে না আর প্রায়ই টেরও পায় না — যা *resumption drift* ডেকে আনে: মডেল এমন history-র সাথে ধারাবাহিকতা বানিয়ে বলে যা তার কাছে আর নেই। একটি receipt মোছাটিকে পাঠযোগ্য করে: একটি সীমানা-পার-করা কৌশল history নতুন করে লেখার পর এটি একটি ছোট, নির্ধারিত নোট শেষে জুড়ে দেয়, যা রেকর্ড করে কতটা compact হয়েছে, সতর্ক করে যে যা টিকে আছে তা পরোক্ষ, আর — একটি handle provider যুক্ত থাকলে — সংরক্ষিত run history-র একটি identifier দেয়।

⟦CODE18⟧

receipt-এর text-এ কোনো timestamp থাকে না, তাই এটি compaction-এর একটি বিশুদ্ধ function। message part-এর তবুও তার সাধারণ request timestamp থাকে।

শব্দচয়ন অনুসরণ করে আসলে কী টিকে আছে। `SummarizingCompaction` একটি সারাংশ রেখে যায়, তাই এর receipt বলে ওপরের সারাংশটি পরোক্ষ; `SlidingWindowCompaction` সরাসরি history বাদ দেয়, তাই এর receipt বলে সেই context নেই। জায়গাতেই-খালি-করা কৌশলগুলো (`ClearToolResults`, `DeduplicateFileReads`, `ClampOversizedMessages`) প্রতিটি message রাখে আর কোনো সীমানা পার করে না, তাই কোনো receipt পাঠায় না।

`SlidingWindowCompaction` তার receipt `keep_messages`-এ গোনে, তাই `keep_messages=40` receipt আর 39টি message রাখে। receipt কখনো শেষ slot নেয় না: `keep_messages=1` receipt আর সবচেয়ে নতুন message রাখে।

`compaction_transcript_handle() -> str | None` দেখায় এমন যেকোনো capability — `TranscriptHandleProvider` protocol — যুক্ত করুন, আর receipt একটি `Persisted run handle: <handle>` নির্দেশক পায়। `StepPersistence` এটি implement করে, তার `run_id` ফেরত দিয়ে, তাই এটি যুক্ত করাই যথেষ্ট। প্রতিটি receipt `compact_messages` span-এ একটি `compaction.receipt` event হিসেবেও পাঠানো হয়, যা বহন করে `compaction.receipt.strategy`, `compaction.receipt.messages_dropped`, `compaction.receipt.tokens_dropped`, `compaction.receipt.by`, আর handle পাওয়া গেলে `compaction.receipt.handle`।

handle-টি **সংরক্ষিত run**-কে নির্দেশ করে, একটি অক্ষত transcript নয়। compaction-এর সম্পাদনা run-এর message history-তে স্থায়ী হয়, তাই run-এর সর্বশেষ snapshot *compact করা* history প্রতিফলিত করে — এটি আবার পড়লে receipt যা বাদ পড়েছে বলে তা ফেরত আসে না। প্রতি-ধাপ snapshot রাখা একটি store হয়তো তবুও compaction-এর আগের ধাপ রাখে, তার নিজের retention সাপেক্ষে (দেওয়া store-গুলোতে `max_snapshots_per_run`)। handle-কে run-এর নির্দেশক হিসেবে ধরুন, আর একটি agent-কে মূলটি পড়তে পারবে বলে প্রতিশ্রুতি দেওয়ার আগে আপনার store-এর retention দেখে নিন।

receipt-এর `by` কৃতিত্ব bridge prefix-এর মতো একই মোটা family অনুমান ব্যবহার করে, একই আনুমানিকতা-সহ — দেখুন [নিচের নোট](#anchored-incremental-summarization-and-the-cross-model-bridge)।

receipt ঐচ্ছিক (`receipts=False` ডিফল্ট), কারণ receipt-এর text হলো content: সঠিক শব্দচয়ন একটি benchmark eval-rig pass-এর অপেক্ষায় অস্থায়ী, যদিও কৌশলটি কাঠামোগত।

## Pinning: compaction-এর পরেও টিকে থাকা content { #pinning-content-that-survives-compaction }

`pin` এমন content চিহ্নিত করে যা দেওয়া প্রতিটি কৌশলকে রক্ষা করতে হবে:

⟦CODE19⟧

একটি pin করা part কখনো সারাংশে হারিয়ে যায় না বা বাদ পড়ে না; কোনো কৌশল সেটি ফেলে দিত এমন হলে, কৌশলটি সেটিকে টিকে থাকা history-র মাথার কাছে আবার ঢুকিয়ে দেয়। একটি part চিহ্নটি বহন করে কি না `is_pinned` জানায়।

pin মডেল-অদৃশ্য `TextContent.metadata` ব্যবহার করে, তাই এদের content সাধারণ user context থাকে অথচ compaction এগুলোকে user turn থেকে আলাদা করতে পারে।

`Planning` capability-র pinning লাগে না: এর প্ল্যান `wrap_model_request`-এ প্রতিটি request-এ ক্ষণস্থায়ীভাবে আবার ঢোকানো হয়, তাই গঠনগতভাবেই এটি compaction-এর পরে টিকে থাকে। pinning হলো স্থায়ী task state আর scratchpad-এর জন্য, যা history-র *ভেতরে* থাকে।

/// tip | উদাহরণ দিয়ে বুঝি

`pin` হলো নোটিশ বোর্ডে লাল পিন দিয়ে আটকানো কাগজ — পরিষ্কারের দিনে (compaction) পুরোনো সব কাগজ সরানো হলেও লাল-পিনেরটা থেকে যায়, দরকার হলে বোর্ডের ওপরে আবার লাগিয়ে দেওয়া হয়।

///

## user message রাখা (`keep_user_messages`) { #keeping-user-messages-keep_user_messages }

user turn হলো একটি কথোপকথনের প্রতি-token সবচেয়ে বেশি সংকেতওয়ালা content, আর এগুলো হারানোই resumption drift-এর প্রধান কারণ। `SummarizingCompaction(keep_user_messages=True)` সারাংশ করা prefix থেকে সবচেয়ে নতুন user turn-গুলো সারাংশের পাশে রাখে। message-সংখ্যা mode-এ, এগুলো বিদ্যমান `keep_messages` লেজের budget খরচ করে, তাই সর্বোচ্চ ততগুলো রাখা user message আর লেজের message একসাথে টিকে থাকে — শুধু এটুকু ছাড়া যে, রাখা user turn অন্যথায় যে slot খরচ করে ফেলত, সেখানে উত্তর দেওয়া request-এর জন্য একটি লেজের slot সংরক্ষিত থাকে; তাই compaction প্রতি চক্রে রাখা কপি বাড়ায় না। একটি ধনাত্মক `keep_tokens` থাকলে, মূল শেষাংশ অগ্রাধিকার পায়: `keep_messages` শুধু বাড়তি পুরোনো user turn সীমিত করে, যা রাখা লেজ কমায় না। `keep_tokens=0` থাকলে, রাখা user কপিগুলোকে একটি শূন্য-token budget-এ আঁটতে হয়, আর সবচেয়ে নতুন লেজের message তবুও টিকে থাকে। প্রতিটি রাখা turn `keep_user_messages_max_chars`-এ (ডিফল্ট 20k) সীমিত, ছাড়ালে একটি স্পষ্ট কাটা-চিহ্নসহ। অক্ষরের budget প্রযোজ্য প্রতি part-এ আর একটি বহু-part prompt-এর text item-গুলোর মধ্যে শেয়ার হয়; ছবি, অডিও আর cache point অক্ষত পার হয়। user channel-এ harness-এর যোগ করা content, যেমন একটি background tool-এর ফল, user turn নয়: `keep_user_messages` আর `preserve_first_user_message` সারাংশ করা prefix থেকে (আগের একটি compaction যে turn রেখেছিল তাসহ) যা বহন করে, তা থেকে এটি বাদ থাকে, আর ব্যবহারকারীর উদ্দেশ্য হিসেবে নয়, data হিসেবে সারাংশ হয়। compaction যে সাম্প্রতিক শেষাংশ সারাংশ ছাড়া রেখে যায়, তা harness content-সহ যেমন আছে তেমন থাকে। এটি `preserve_first_user_message`-এর জায়গা নেয়, যা শুধু প্রথম turn রাখে।

⟦CODE20⟧

user turn রাখলে সারাংশ, যেকোনো receipt, আর রাখা turn-গুলো পাশাপাশি `ModelRequest` হিসেবে থাকে। যে provider-রা প্রতি turn-এ একটি request চায় — তাদের মধ্যে Bedrock Converse আর Gemini — তারা কখনো সেই আকার দেখে না: `before_model_request` hook চলার পরে Pydantic AI `_merge_consecutive_messages` দিয়ে history স্বাভাবিক করে, dispatch-এর আগে পাশাপাশি request-গুলো একটি turn-এ মিলিয়ে। তাই `keep_user_messages`-এর কোনো provider-নির্দিষ্ট ব্যবস্থা লাগে না।

## নোঙর করা ক্রমিক সারাংশ আর cross-model bridge { #anchored-incremental-summarization-and-the-cross-model-bridge }

`incremental=True` (ডিফল্ট) থাকলে, আগের সারাংশ আবার সারাংশ করা হয় না — সারাংশের সারাংশ পরপর compaction-এ ক্ষয়ে যায়। এটি একটি নোঙর করা `<previous-summary>` block হিসেবে ফেরত দেওয়া হয়, একটি *হালনাগাদ* নির্দেশসহ: এখনও-সত্য খুঁটিনাটি রাখো, পুরোনো হয়ে যাওয়াগুলো সরাও, নতুন তথ্য মেশাও। সারাংশটি একটি জীবন্ত document হয়ে ওঠে, যা একটি স্থির কাঠামোর অধীনে জায়গাতেই হালনাগাদ হয়।

/// note | আচরণ পরিবর্তন: `incremental=True` এখন ডিফল্ট

এই release থেকে প্রতিটি বিদ্যমান `SummarizingCompaction` ব্যবহারকারী একটি ভিন্ন সারাংশ-call prompt পায়: একবার একটি আগের সারাংশ থাকলে, summarizer-কে কথোপকথন থেকে নতুন করে বানানোর বদলে `<previous-summary>`-এর অধীনে সেটি *হালনাগাদ* করতে বলা হয়। এর তৈরি সারাংশগুলো ভিন্নভাবে পড়বে। আগের শূন্য-থেকে-নতুন-করে-তৈরি আচরণ রাখতে `incremental=False` সেট করুন।

///

`bridge_prefix=True` সারাংশের আগে এক-লাইনের একটি নোট জুড়ে দেয় শুধু তখনই, যখন summarizer-এর model family history তৈরি করা family থেকে আলাদা — history-র `model_name` আর summarizer config থেকে নির্ণীত। এটি সারাংশটিকে একটি cross-model হস্তান্তর হিসেবে চিহ্নিত করে, যাতে আবার শুরু করা মডেল কাজটি নিজেই করেছে বলে বানিয়ে না বলে বরং এর ওপর গড়ে তোলে। সাধারণ একই-মডেলের ক্ষেত্রে এটি কখনো চালু হয় না, তাই সস্তা। এর ডিফল্ট `False`, কারণ নোটটি prompt content।

family token একটি মোটা আনুমানিকতা: যেকোনো `provider:` prefix বাদ দাও, তারপর প্রথম `-` বা `/`-এর আগের শুরুর token নাও। সাধারণ reference-এ এটি `gpt`-কে `claude` থেকে আলাদা করে (`openai:gpt-5.6-luna` -> `gpt`, `google:gemini-3.6-flash` -> `gemini`) আর কয়েকটি আসল reference ভুল পড়ে — `us.anthropic.claude-sonnet-4-5-v1:0` হয়ে যায় `0`, `ollama/llama3` হয় `ollama`, আর একটি `fallback:` model *string* তার প্রথম নয়, শেষ তালিকাভুক্ত মডেলে। একটি `FallbackModel` object সঠিকভাবে পড়া হয়, তার প্রথম মডেল থেকে। তাই bridge আর receipt-এর কৃতিত্ব best-effort: ভুল পড়া family একটি bridge নোট চাপা দিতে পারে বা একই family-র দুটি মডেলের মাঝে একটি চালু করতে পারে। কোনো ফলাফলই compaction কী রাখে বা বাদ দেয় তা বদলায় না।

receipt-এর মতোই, হালনাগাদ নির্দেশ আর bridge-prefix-এর শব্দচয়ন হলো content, eval-rig pass-এর অপেক্ষায় ন্যূনতম আর নিরপেক্ষভাবে দেওয়া; নোঙর আর family-বাছাইয়ের কৌশল কাঠামোগত।

## আওতার বাইরে { #out-of-scope }

এই কৌশলগুলো window-এর *ভেতরে* context সংকুচিত করে বা বাদ দেয়। বড় tool output window-এর *বাইরে* সরানো — এমন একটি ফাইলে উপচে দেওয়া যা agent (বা একটি subagent) দরকারমতো query করতে পারে — একটি আলাদা capability ([tool output limits](tool-output-limits.md)), ক্ষতিকর ছাঁটাই নয়। `SummarizingCompaction`-এর ভেতরে `tool_return_max_chars` summarizer-এর প্রতি-return সীমা পরিবর্তনযোগ্য করে (বা return পুরো render করতে `None`), কিন্তু সারাংশ request তবুও একটি ক্ষতিকর রূপ পড়ে; একটি payload পুরোটা query করার মতো থাকতে হলে tool output limits বেছে নিন।

/// check | সংক্ষেপে মনে রাখুন

* সব কৌশল tool-call/return জোড়া অক্ষত রাখে; সম্পাদনা history-তে স্থায়ী হয়।
* trigger হিসেবে `max_fraction` দিন — সব মডেলে সঠিক; registry ভুল হলে `context_window=`, অজানা হলে `fallback_context_window=`।
* ডিফল্ট হিসেবে `TieredCompaction`: সস্তা স্তর (dedupe, clear) আগে, সারাংশ শেষে; ব্যর্থতায় বাঁচতে `FallbackCompaction`।
* একটি বিশাল part-এর জন্য `ClampOversizedMessages`; অসমান পুরোনো context-এর জন্য `RelevanceCompaction`।
* `Memory`-র মতো শুধু-request capability compaction-এর পরে রাখুন।
* সারাংশ call usage আর request limit-এ গোনা হয়।
* `pin` দিয়ে জরুরি state রক্ষা করুন; `receipts=True` মডেলকে জানায় কী মুছে গেছে।

///

## API রেফারেন্স { #api-reference }

প্রস্তাবিত ডিফল্ট হলো `TieredCompaction`; নিচের অন্য কৌশলগুলো আলাদাভাবে ব্যবহার করা যায় বা এর স্তর হিসেবে জুড়ে দেওয়া যায়।

⟦CODE21⟧

⟦CODE22⟧

⟦CODE23⟧

⟦CODE24⟧

⟦CODE25⟧

⟦CODE26⟧

/// info | API রেফারেন্স

`pydantic_ai_harness.compaction.RelevanceCompaction`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/compaction/)।

///

⟦CODE27⟧

⟦CODE28⟧

⟦CODE29⟧

⟦CODE30⟧

⟦CODE31⟧

⟦CODE32⟧

⟦CODE33⟧
