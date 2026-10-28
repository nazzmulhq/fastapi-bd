
# Compaction { #compaction }

/// note | এই পেজে যা শিখবেন

* compaction কী, আর লম্বা কথোপকথন কেন context window-এ আটকে যায়।
* provider-native compaction (OpenAI, Anthropic) আর তার "দৃশ্যমানতার সীমানা"।
* client-এর কাছে রাখা history আর নিরাপত্তার দিক।
* যেকোনো মডেলে নিজে compaction করা, আর Pydantic AI Harness-এর তৈরি কৌশল।

///

কথোপকথন বড় হতে থাকলে এর message history মডেলের context window-এর কাছাকাছি পৌঁছাতে পারে। *Compaction* পুরোনো message ছোট করে (ছাঁটাই, মুছে ফেলা, বা সারাংশ বানিয়ে) এটিকে নিয়ন্ত্রণে রাখে, আর সাম্প্রতিক context ও tool-call-এর অখণ্ডতা বজায় রাখে। Pydantic AI এটি কয়েক স্তরে সাপোর্ট করে: [provider-native compaction API](#provider-native-compaction), আপনার নিজের লেখা [মডেল-নিরপেক্ষ history সম্পাদনা](#model-agnostic-compaction), আর [Pydantic AI Harness](#pydantic-ai-harness)-এর তৈরি মডেল-নিরপেক্ষ কৌশলের মেনু।

/// tip | উদাহরণ দিয়ে বুঝি

একটি লম্বা মিটিংয়ের সব কথা হুবহু খাতায় লিখতে থাকলে একসময় খাতা ভরে যায়। তখন পুরোনো পাতাগুলো ছিঁড়ে ফেলে দিলে জরুরি সিদ্ধান্ত হারিয়ে যায়; তাই বুদ্ধিমান সচিব পুরোনো আলোচনার একটি সংক্ষিপ্ত সারাংশ লিখে রাখেন, আর শুধু সাম্প্রতিক কথাগুলো বিস্তারিত রাখেন। compaction ঠিক এই কাজটিই করে।

///

## Provider-native compaction { #provider-native-compaction }

কিছু provider একটি বিল্ট-ইন compaction API দেয়, যা তাদের দিকেই চলে। Pydantic AI এগুলোকে [capability](overview.md) হিসেবে মুড়ে দেয়:

| Provider | Capability | বিস্তারিত |
|----------|-----------|---------|
| OpenAI Responses API | [`OpenAICompaction`][pydantic_ai.models.openai.OpenAICompaction] | [OpenAI compaction](../models/openai.md#message-compaction) |
| Anthropic | [`AnthropicCompaction`][pydantic_ai.models.anthropic.AnthropicCompaction] | [Anthropic compaction](../models/anthropic.md#message-compaction) |

প্রতিটি সংশ্লিষ্ট provider-এর API ব্যবহার করে, তাই শুধু সেই provider-এই পাওয়া যায়।

Pydantic AI একটি compaction part-কে ভবিষ্যৎ request-এ যাওয়া state-এর জন্য একটি দৃশ্যমানতার সীমানা হিসেবে ধরে। সীমানার আগের tool আবিষ্কার আর on-demand capability লোড reset হয়, তাই পরের request-গুলো সেগুলো আবার জানায়। capability আর toolset লেখকদের নিজেদের উদ্ভূত state-এও একই নিয়ম প্রয়োগ করা উচিত: মডেলের যা দেখা থাকা দরকার — ঘোষণা, প্রকাশ, catalog — তা instance attribute-এ মনে না রেখে [`post_compaction_window`][pydantic_ai.messages.post_compaction_window] থেকে হিসাব করুন, যাতে compaction যখন সেগুলো বহনকারী history বদলে দেয়, তখন এটি নিজে থেকেই ঠিক হয়ে যায়।

একটি tool call dispatch করার সময়, Pydantic AI সেই response যে provider দিয়েছিল তা দিয়ে ঠিক করে, provider আসলে request wire-এ সীমানাটি মেনেছিল কি না। অন্য provider-এর একটি compaction part, encrypted content ছাড়া একটি OpenAI part, বা summary content ছাড়া একটি Anthropic part আগের callability-র প্রমাণ লুকায় না, কারণ ওই provider আগের history মডেলের কাছে পাঠিয়েছিল। call-টি থাকা response-এর ভেতরে তৈরি হওয়া একটি সীমানাও সেই response-এর জন্য মডেল কী দেখেছিল তা প্রভাবিত করতে অনেক দেরি করে ফেলে। response-এ কোনো provider নাম না থাকলে, dispatch provider-নিরপেক্ষ সীমানায় ফিরে যায়।

### client-এর কাছে রাখা history { #client-held-history }

[`CompactionPart`][pydantic_ai.messages.CompactionPart] [UI adapter](../ui/overview.md)-গুলোর মধ্য দিয়ে আসা-যাওয়া করে, যাদের protocol-এ client প্রতিটি request-এ পুরো কথোপকথনের history পাঠায় — তাই compact করা কথোপকথন এমন frontend-এর সাথেও কাজ করতে থাকে। AG-UI-তে compaction item একটি activity message, যা `@ag-ui/client` ফেরত পাঠায় না; দেখুন [Records carried as activity messages](../ui/ag-ui.md#activity-records)। client-এর জমা দেওয়া একটি compaction item মানা হয় — কথোপকথন compact-ই থাকে — কিন্তু এটিকে কখনো agent-এর [system prompt](../agent.md#system-prompts)-এর বিকল্প হিসেবে বিশ্বাস করা হয় না: সেটি তবুও প্রতিটি request-এ মডেলের কাছে পৌঁছায়, যেমন বলা আছে [Loading untrusted history](../message-history.md#loading-untrusted-history)-এ।

একটি run যদি তার নিজের server-দিকের history-ও পায় — [server-side persistence pattern](../ui/overview.md#trust-model-for-client-submitted-messages), যেখানে সংরক্ষিত message `message_history` হিসেবে দেওয়া হয় আর client message শুধু সর্বশেষ turn দেয় — তাহলে client-এর জমা দেওয়া compaction item বরং উপেক্ষিত হয়। একটি compaction item এমন একটি সীমানা চিহ্নিত করে, যার আগের কিছুই মডেলের কাছে পাঠানো হয় না, তাই client-এরটি মানলে সেটি server-এর নিজের সংরক্ষিত history মডেলের কাছ থেকে লুকিয়ে তার জায়গায় নিজের সারাংশ বসিয়ে দিতে পারত। client-এর জমা দেওয়া compaction item মানা হয় শুধু তখনই, যখন client-এর পাঠানো message-গুলোই পুরো কথোপকথন।

তবুও, একটি client server-এর provider account কখনো তৈরি করেছে এমন যেকোনো compaction item আবার পাঠাতে পারে — OpenAI-তে অস্বচ্ছ encrypted state, Anthropic-এ সাধারণ-text summary। এটি প্রকৃতিতে সাধারণ-text history বানিয়ে নেওয়ার সমতুল্য, যা client-এর পাঠানো history সবসময় অনুমতি দেয় (দেখুন [Trust boundary for client-supplied history](../message-history.md#trust-boundary-for-client-supplied-history)) — একটি পার্থক্য ছাড়া: অস্বচ্ছ item-এ কী আছে server তা পরীক্ষা করতে পারে না। আপনার deployment-এ এটি গুরুত্বপূর্ণ হলে history server-দিকে রাখুন: কথোপকথন দিয়ে key করে পুরো message তালিকা সংরক্ষণ করুন, client-কে শুধু দেখানোর data পাঠান, আর প্রতিটি run-এ সংরক্ষিত message `message_history` হিসেবে দিন। compaction সীমানার চারপাশে সংরক্ষিত history নিজে ছাঁটবেন না — প্রতিটি model adapter আগে থেকেই বাদ দেয় যা তার নিজের provider-এর compaction প্রতিস্থাপন করে, আর অন্য provider-এর মডেল, যারা বিদেশি compaction item উপেক্ষা করে, তবুও তাদের দরকারি পুরো আগের history পায়।

/// danger | নিরাপত্তা

client পুরো history পাঠায় এমন সেটআপে client একটি পুরোনো compaction item আবার পাঠিয়ে মডেলের দেখা অতীত বদলে দিতে পারে। সংবেদনশীল অ্যাপে history server-এ রাখুন আর client-কে শুধু সর্বশেষ message পাঠাতে দিন — তখন client-এর compaction item এমনিতেই উপেক্ষিত হয়।

///

## মডেল-নিরপেক্ষ compaction { #model-agnostic-compaction }

যেকোনো মডেলে compact করতে, একটি [`ProcessHistory`][pydantic_ai.capabilities.ProcessHistory] capability হিসেবে মোড়ানো একটি [history processor](../message-history.md#processing-message-history) দিয়ে message history নিজে সম্পাদনা করুন — এটি প্রতিটি provider-এ কাজ করে। *কখন* compact করবেন তা ঠিক করতে [`ctx.context_window_used`][pydantic_ai.tools.RunContext.context_window_used] দেখুন: শেষ response অনুযায়ী মডেলের [`context_window`][pydantic_ai.profiles.ModelProfile.context_window]-এর কত ভাগ ভরেছে, বা অজানা হলে `None`। প্রচলিত pattern:

- [Keep only recent messages](../message-history.md#keep-only-recent-messages) — সবচেয়ে সাম্প্রতিক turn-গুলোর ওপর একটি বিনা-খরচের sliding window।
- [Summarize old messages](../message-history.md#summarize-old-messages) — একটি (সস্তা) মডেল দিয়ে পুরোনো message-গুলোকে একটি সারাংশে ঘনীভূত করা।

## Pydantic AI Harness { #pydantic-ai-harness }

[Pydantic AI Harness](../harness/index.md) তৈরি, মডেল-নিরপেক্ষ [compaction কৌশলের](../harness/compaction.md) একটি মেনু দেয়: বেশিরভাগই LLM-ছাড়া history সম্পাদনা (sliding-window ছাঁটাই, পুরোনো tool result মুছে ফেলা, বারবার পড়া ফাইলের ডুপ্লিকেট বাদ দেওয়া, অতিরিক্ত বড় message part সীমিত করা), সাথে তা যথেষ্ট না হলে LLM দিয়ে সারাংশ, আর একটি `TieredCompaction` orchestrator (প্রস্তাবিত ডিফল্ট), যা লক্ষ্যে আঁটাতে যতটুকু দরকার শুধু ততটুকুই সস্তা থেকে দামি কৌশলে ধাপে ধাপে ওঠে।

/// info | এক নজরে: কোন পথ কখন

| পথ | কোথায় চলে | কখন বাছবেন |
|---|---|---|
| `OpenAICompaction` / `AnthropicCompaction` | provider-এর server-এ | ওই একটি provider-ই ব্যবহার করেন |
| `ProcessHistory` + নিজের processor | আপনার কোডে | সম্পূর্ণ নিয়ন্ত্রণ চান, যেকোনো মডেলে |
| Harness-এর `TieredCompaction` | আপনার কোডে, তৈরি কৌশল | ঝামেলা ছাড়া যেকোনো মডেলে ভালো ডিফল্ট |

///

/// check | সংক্ষেপে মনে রাখুন

* compaction পুরোনো message ছোট করে context window-এ জায়গা রাখে, সাম্প্রতিক context আর tool-call অখণ্ড রেখে।
* provider-native: OpenAI Responses-এ `OpenAICompaction`, Anthropic-এ `AnthropicCompaction`।
* compaction part একটি দৃশ্যমানতার সীমানা — capability লেখকরা `post_compaction_window` থেকে state হিসাব করুন।
* server-দিকে history থাকলে client-এর compaction item উপেক্ষিত হয়; নিরাপত্তার জন্য সেটিই ভালো।
* যেকোনো মডেলে: `ProcessHistory` + `ctx.context_window_used`, অথবা Harness-এর `TieredCompaction`।

///
