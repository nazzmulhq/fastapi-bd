# TypeSafe (Jev) { #typesafe-jev }

/// note | এই পেজে যা শিখবেন

* TypeSafe-এর Jev, একটি decision model, `TypeSafeModel` দিয়ে ব্যবহার।
* মডেলের নাম ও সংস্করণ pin করা, একটি পূর্ণ উদাহরণ, খরচ আর সীমা (32k token)।
* Jev কোথায় দুর্বল (আক্ষরিক পড়া, গণনা, প্রতিপক্ষ লেখা...), ফাইল, retry আর সেটিং।

///

[Jev](https://typesafe.ai) হলো TypeSafe-এর মডেল, আর একটি [decision model](decision.md): এটি একটি লেখা নিয়ে টাইপ করা প্রশ্নের উত্তর দেয়, প্রতিটি একটি সম্ভাবনা বা বিকল্পগুলোর ওপর একটি বণ্টনসহ, লেখা না লিখে। Pydantic AI-তে, একটি decision model-এ চলা এজেন্ট এটিকে গোছানো [আউটপুট](../output.md) তৈরি আর [টুল](../tools.md) ডাকা, দুটোতেই ব্যবহার করতে পারে।

[`TypeSafeModel`][pydantic_ai.models.typesafe.TypeSafeModel] হলো Jev-এর Pydantic AI মডেল ক্লাস, আর [`DecisionModel`][pydantic_ai.models.decision.DecisionModel]-এর একটি subclass। এই পেজ Jev আর TypeSafe-এর নিজস্ব বিষয় নিয়ে: সেটআপ, Jev-এর সীমা, আর এটি কোথায় খারাপ উত্তর দেয়।

/// tip | Decision models দিয়ে শুরু করুন

**একটি এজেন্টের আউটপুট টাইপ, টুল আর বার্তার ইতিহাস কীভাবে Jev-এর প্রশ্নে ম্যাপ হয়, আর উত্তরের অর্থ কী, তা শেখার জায়গা হলো [Decision models](decision.md)**, একটি [পূর্ণ উদাহরণসহ](decision.md#a-support-desk-end-to-end) যা এগুলো মেলায় আর Jev উত্তর দিতে না পারলে একটি ভাষা মডেলে পাঠায়।

///

## ইনস্টল { #install }

`TypeSafeModel` ব্যবহার করতে, `typesafe` ঐচ্ছিক group-সহ `pydantic-ai-slim` (বা `pydantic-ai`) ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[typesafe]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[typesafe]"
```

///


## কনফিগারেশন { #configuration }

[TypeSafe](https://typesafe.ai) API দিয়ে Jev ব্যবহার করতে, আপনার TypeSafe account থেকে একটি API key নিয়ে এটি একটি environment variable হিসেবে সেট করুন:

```bash
export TYPESAFE_API_KEY='your-api-key'
```

তারপর নাম দিয়ে `TypeSafeModel` ব্যবহার করতে পারেন, `typesafe:jev-latest` হিসেবে, বা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE1⟧

### মডেলের নাম { #model-names }

`jev-latest` আর `jev-preview` হলো alias, যা TypeSafe একটি release দিলে সরে যায়; preview build থাকলে `jev-preview` এগিয়ে চলে। একটি সংস্করণযুক্ত id-ও গৃহীত হয়, তালিকায় থাকুক বা না থাকুক:

⟦CODE2⟧

[`ModelResponse.model_name`][pydantic_ai.messages.ModelResponse.model_name] যে সংস্করণযুক্ত id উত্তর দিয়েছে তা জানায়, তাই `jev-latest`-এর বিপরীতে লগ করা একটি রান তবুও রেকর্ড রাখে কোন মডেল এটি তৈরি করেছে। যেহেতু `jev-latest` সরে, একটি নতুন release আপনার ঠিক করা একটি [threshold](decision.md#confidence-and-thresholds)-এর নিচের সংখ্যা বদলে দিতে পারে; একবার একটি ঠিক করলে, যে সংস্করণের বিপরীতে ঠিক করেছেন সেটি pin করুন (`typesafe:jev-1.13.0`) আর ভেবেচিন্তে এগোন।

/// warning | সাধারণ ভুল

production-এ `jev-latest` রেখে threshold (যেমন ০.৮) ঠিক করা। নতুন release এলে সংখ্যাগুলো সরে যায়, আর আপনার ০.৮ রাতারাতি অন্য অর্থ বহন করে। threshold ঠিক করার পরে নির্দিষ্ট সংস্করণ pin করুন।

///

## উদাহরণ { #example }

একটি এজেন্টকে একটি আউটপুট টাইপ দিন, আর Jev এক রিকোয়েস্টে এর প্রতিটি ফিল্ডের উত্তর দেয়, প্রতিটি নিজের আত্মবিশ্বাসসহ:

⟦CODE3⟧

prompt শুধু টিকিটটি; প্রশ্নগুলো আউটপুট টাইপে: এর docstring হলো লক্ষ্য, প্রতিটি ফিল্ডের নিচের docstring হলো সেই ফিল্ডের প্রশ্ন, আর `Enum` সদস্যদের docstring আর [`BoolCriteria`][pydantic_ai.output.BoolCriteria] বলে প্রতিটি উত্তরের অর্থ কী। Jev দল আর অ্যাপ সম্পর্কে নিশ্চিত, আর টিকিটটি জরুরি কিনা সে বিষয়ে অনেক কম নিশ্চিত, যা একজন মানুষ বা [এর পেছনের একটি ভাষা মডেলের](decision.md#falling-back-on-low-confidence) কাছে পাঠানোর উত্তর। প্রতিটি উত্তর টাইপের একটি মান, তাই পার্স করার মতো কোনো লেখা নেই আর বিকল্পের বাইরে কোনো উত্তর নেই।

## খরচ আর সীমা { #limits }

Jev এক রিকোয়েস্টের প্রশ্নগুলোর উত্তর সমান্তরালে দেয়, তাই কয়েকটি জিজ্ঞেস করার খরচ একটির চেয়ে সামান্যই বেশি: শুধু কিছু ইনপুটে দরকার এমন একটি ফিল্ডের খরচ সময় নয়, token।

একটি রিকোয়েস্ট কী বহন করতে পারে তা সীমিত, আর `TypeSafeModel` একটি রিকোয়েস্ট পাঠানোর আগে প্রথম দুটি মেনে চলে:

- **একটি এক-বাছাই প্রশ্নে 255টি বিকল্প।** একটি এক-বাছাই ফিল্ড তার নিজের বিকল্প গোনে, আর [route প্রশ্ন](decision.md#routes-which-thing-to-do) প্রতিটি টুল আর প্রতিটি আউটপুট টাইপ গোনে, তাই পাশে আউটপুট টাইপ গোনা হলে 255টি টুল ইতিমধ্যে একটি বেশি। 256তম বিকল্প API থেকে একটি 400, তাই এর বেশি একটি প্রশ্ন বদলে একটি [`UserError`][pydantic_ai.exceptions.UserError] দিয়ে প্রত্যাখ্যাত হয়।
- **একটি rubric-এ 10টি স্তর।** 11তম API থেকে একটি 400, তাই 0 থেকে এগারো বা ততোধিক পূর্ণসংখ্যা rubric নয়, আর বদলে [এক-বাছাই হিসেবে জিজ্ঞেস করা হয়](decision.md#what-each-field-type-does)।
- `jev-1.13`-এ state আর দীর্ঘতম প্রশ্ন মিলে **32k token**, আর state ও সব প্রশ্ন মিলে 64k। state প্রতি রিকোয়েস্টে একবার গোনা হয়, তাই 32k হলো একটি দীর্ঘ কথোপকথন যে সীমায় পৌঁছায়; 64k শুধু তখনই বাঁধে যখন প্রশ্নগুলো নিজেরাই খুব বড়। এর বেশি হলে রিকোয়েস্ট একটি [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] (`max_tokens_exceeded`) দিয়ে ব্যর্থ হয়, যা একটি `FallbackModel` অন্য যেকোনো API এররের মতো Jev-এর পেছনের মডেলে দেয়। দেখুন [keeping a conversation under the limit](#compaction)।

### একটি কথোপকথনকে সীমার নিচে রাখা { #compaction }

পুরো বার্তার ইতিহাসই state, তাই প্রতিটি দফা তার পরের প্রতিটি রিকোয়েস্টে যোগ হয়, আর টুল ফল, যা পুরোটা যায়, বাজেট সবচেয়ে দ্রুত ভরায়। একটি কথোপকথন সীমা পেরোলে, পরের প্রতিটি দফা Jev-এ ব্যর্থ হয়, তাই একটি `FallbackModel`-এর পেছনে ইতিহাস compact না হওয়া পর্যন্ত প্রতিটি ভাষা মডেলে যায়।

Jev-এর [`context_window`][pydantic_ai.profiles.ModelProfile.context_window] হলো 32k সীমা, যেকোনো মডেলের মতো [genai-prices](https://github.com/pydantic/genai-prices) থেকে ভরা, তাই [`ctx.context_window_used`][pydantic_ai.tools.RunContext.context_window_used] যে সীমা বাঁধে তার বিপরীতে মাপে, আর [context window ভরে এলে compact করা](../message-history.md#compact-when-the-context-window-fills) processor একটি Jev এজেন্টে অপরিবর্তিত কাজ করে। একটি `FallbackModel` তার মডেলগুলোর মধ্যে সবচেয়ে ছোট window-এর বিপরীতে মাপে, যা Jev-এর।

⟦CODE4⟧

বাদ পড়া দফাগুলো কী বলেছিল তা রাখতে, বদলে সেগুলোর সারাংশ করুন, [summarize old messages](../message-history.md#summarize-old-messages)-এর মতো একটি history processor বা [harness](../harness/compaction.md)-এর `SummarizingCompaction` দিয়ে। যেভাবেই হোক সারাংশ লিখতে হবে একটি ভাষা মডেলকে: Jev লেখা লেখে না, তাই `SummarizingCompaction`-কে এজেন্টেরটিতে ডিফল্ট হতে না দিয়ে `model=` হিসেবে একটি ভাষা মডেল দিন। একে 32k-এর নিচে ফাঁকা জায়গাসহ একটি `max_tokens=` দিন, যেমন `20_000`: এটি শেষ রিকোয়েস্টের জন্য Jev-এর জানানো usage থেকে গোনে, কিন্তু নতুন কিছু, আর জানানো usage নেই এমন যেকোনো ইতিহাস, প্রতি token প্রায় চার অক্ষর ধরে অনুমান করে, যা Jev-কে পাঠানো JSON প্রায় এক-চতুর্থাংশ কম গোনে।

সবকিছুর সারাংশ না করে কী রাখবেন তা বাছতে, harness-এর [`RelevanceCompaction`](../harness/compaction.md) একজন বিচারককে জিজ্ঞেস করে, যা Jev নিজেও হতে পারে, প্রতিটি পুরনো ধাপ এখনো দরকার কিনা, আর সেই অনুযায়ী রাখে, সারাংশ করে বা বাদ দেয়।

## Jev কোথায় খারাপ উত্তর দেয় { #what-jev-answers-badly }

নিচের সবকিছু এরর নয়, একটি উত্তর ফেরত দেয়, আর সেজন্যই জানা দরকার।

### TypeSafe-এর প্রকাশিত { #published-by-typesafe }

TypeSafe এগুলো প্রতি মডেল সংস্করণে প্রকাশ করে, তাদের [`jev-1.13`-এর jaggedness পেজে](https://docs.typesafe.ai/model-jaggedness/jev-1.13), আর মডেল বদলালে হালনাগাদ করে। পেজটি একটি প্রশ্নে কয়েকটি বিচার লুকানোর বিরুদ্ধেও সতর্ক করে, যাকে TypeSafe-এর গাইড বলে "probably the most important concept": দেখুন [ask one thing per field](decision.md#ask-one-thing-per-field)।

- **আক্ষরিক পড়া।** Jev "আপনি যে প্রশ্ন লিখেছেন তার উত্তর দেয়, যেটি বোঝাতে চেয়েছেন তার নয়": পরিসর-নির্দেশক শব্দ, না-বাচক আর অনুমিত শর্ত আক্ষরিকভাবে পড়া হয়। প্রশ্নে সঠিক শর্তটি লিখুন, আর সীমারেখার ক্ষেত্রগুলো একটি `bool` ফিল্ডের [criteria](decision.md#what-each-field-type-does)-য় বা একটি এক-বাছাইয়ের বিকল্পের বর্ণনায় রাখুন।
- **গণিত, গণনা আর তারিখ।** Jev ক্যালকুলেটর নয়, নির্ভরযোগ্যভাবে গোনে না, আর তারিখকে ক্রমিক পরিমাণ নয়, লেখা হিসেবে পড়ে। এগুলো Python-এ হিসাব করে ফল নিয়ে Jev-কে জিজ্ঞেস করুন।
- **পরোক্ষতা।** একটি বৈশিষ্ট্যের বৈশিষ্ট্য নিয়ে প্রশ্ন, বা কয়েক ধাপ লাগে এমন প্রশ্নে নির্ভুলতা কমে। যত সরাসরি সম্ভব জিজ্ঞেস করুন, আর প্রশ্নটি [state-এর কোন অংশ নিয়ে তার নাম দিন](decision.md#where-the-wording-comes-from)।
- **অপ্রয়োজনীয় প্রসঙ্গ।** প্রশ্নের সাথে সম্পর্কহীন বিবরণে state বাড়লে নির্ভুলতা কমে, তাই পাঠানোর পরে নয়, আগে ছাঁকুন, আর বিচারের আগে একটি দীর্ঘ কথোপকথন compact করুন।
- **প্রতিপক্ষ লেখা।** Jev state-কে ডেটা হিসেবে ধরে, শত্রু হিসেবে নয়: উত্তর চালিত করতে লেখা লেখা — একটি ঢোকানো নির্দেশনা, একটি বিভ্রান্তিকর উপস্থাপন, নিজের শ্রেণিবিন্যাসের পক্ষে একটি যুক্তি — এটিকে সরাতে পারে। TypeSafe বলে তারা এটি উন্নত করার আশা করে। Jev-এর ওপর তৈরি একটি পাহারা নির্ধারিত পরীক্ষার পাশাপাশি থাকা উচিত, বদলে নয়, আর আপনার নিজের প্রতিপক্ষ ইনপুটের বিপরীতে পরীক্ষা করা উচিত।
- **পরস্পরবিরোধী প্রশ্ন আর criteria।** যেখানে একটি ফিল্ডের প্রশ্ন আর এর criteria ভিন্ন জিনিস চায়, যেমন একটি [`BoolCriteria`][pydantic_ai.output.BoolCriteria] যার `true` একটি না বর্ণনা করে, Jev খারাপ উত্তর দেয়। criteria প্রশ্নের বর্ধিত রূপ হিসেবে লিখুন।
- **কাঠামোগত অপরিবর্তনীয়তা।** একটি প্রশ্ন আর তার নেতিবাচক রূপ যোগ করে এক হওয়ার দরকার নেই, আর একই প্রশ্ন একটি হ্যাঁ/না আর একটি এক-বাছাই হিসেবে জিজ্ঞেস করলে এমন সংখ্যা দেয় যা তুলনীয় নয়। প্রতিটি সিদ্ধান্ত এক উপায়ে জিজ্ঞেস করুন, অভেদ কোডে প্রয়োগ করুন, আর প্রতিটি সীমা যে ধরনের প্রশ্ন আটকায় তার ওপর [ঠিক করুন](decision.md#confidence-and-thresholds)।
- **লেখা তৈরি।** Jev লেখা লেখে না, তাই একটি `str` ফিল্ডসহ একটি route [একটি ভাষা মডেলে পাঠানো হয়](decision.md#escalating-to-a-language-model)।

### Pydantic AI-তে দেখা { #observed-in-pydantic-ai }

এগুলো এসেছে Pydantic AI-এর পেছনে Jev চালিয়ে, TypeSafe থেকে নয়।

- **একটি টুল কল যা পুনরাবৃত্তি হয়।** ইতিহাসে একটি টুলের কল আর ফল থাকলে, লেখা সাধারণত তখনো এটি চায়, তাই Jev আবার এটি বাছে। তাই একটি টুলের ফল দফায় এসে গেলে তা আর দেওয়া হয় না, আর পরের prompt-এ আবার দেওয়া হয়; অসমর্থিত আর্গুমেন্ট Jev-এর পেছনের মডেলে প্রস্তাব করা হয়, যে সিদ্ধান্ত নেয়। তবুও টুলসহ একটি Jev এজেন্টে একটি `UsageLimits(request_limit=...)` রাখুন, loop করা যেকোনো এজেন্টের মতো।
- **যা দেখতে পায় না তা নিয়ে সিদ্ধান্ত।** লেখা বলে না এমন একটি আর্গুমেন্ট চায় এমন একটি টুল — একটি refund-এর পরিমাণ, একটি তারিখ — Jev প্রস্তাব করবে আর একটি ভাষা মডেল ডাকতে অস্বীকার করতে পারে; দুজনে একই বিকল্প ভিন্নভাবে বিচার করে, আর ভাষা মডেলরা নিজেদের মধ্যেও এমন বাছাইয়ে প্রায় ততবারই দ্বিমত করে। কারও হস্তান্তরের হারে ভরসার আগে নিজের টিকিটে Jev আর তার পেছনের মডেল তুলনা করুন।
- **প্রশ্ন নিয়ে প্রশ্ন।** লেখা কী চায় তার বদলে সে উত্তর দিতে *পারে* কিনা জিজ্ঞেস করলে, Jev প্রায় সবকিছু হস্তান্তর করে, আর সেজন্যই আউটপুট টাইপ একটি কাজ হিসেবে দেওয়া হয়, [এর docstring দিয়ে বর্ণিত](decision.md#routes-which-thing-to-do)।

/// note | নিজের ডেটায় মাপুন

ভরসা করার আগে নিজের লেবেল করা উদাহরণে নির্ভুলতা, হস্তান্তরের হার আর যেকোনো threshold মাপুন।

///

## ফাইল { #files }

Jev শুধু লেখা পড়ে। একটি ডকুমেন্ট, ছবি বা ভিডিও নিয়ে জিজ্ঞেস করতে, এটি পড়তে পারে এমন একটি মডেলসহ [File Understanding](../capabilities/file-understanding.md) capability যোগ করুন, আর Jev ফাইলের জায়গায় একটি বর্ণনা পায়:

⟦CODE5⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE6⟧

একটি নিজের `http_client` দিয়েও [`TypeSafeProvider`][pydantic_ai.providers.typesafe.TypeSafeProvider] নিজের মতো করতে পারেন:

⟦CODE7⟧

## SDK retry { #sdk-retries }

TypeSafe SDK ডিফল্টভাবে সংযোগ এরর, timeout আর retry-যোগ্য HTTP status backoff-সহ দুবার আবার চেষ্টা করে। তা বদলাতে, নিজে client বানিয়ে provider-কে দিন:

⟦CODE8⟧

একটি মডেল, এজেন্ট বা রানের শুধু সংখ্যা বদলাতে, বদলে [`ModelSettings['max_retries']`](../retries.md#setting-the-sdk-retry-count-per-request) সেট করুন। রিকোয়েস্ট তখন client-এরটির বদলে সেই সংখ্যাসহ SDK-র ডিফল্ট `RetryPolicy` ব্যবহার করে। এটি Pydantic AI-এর নিজের retry-এর সাথে কীভাবে কাজ করে তা দেখুন [Provider SDK retries](../retries.md#provider-sdk-retries)-এ।

## মডেল সেটিং { #model-settings }

Jev-এর কোনো sampling নিয়ন্ত্রক নেই, তাই সাধারণ `temperature`, `top_p` আর এমন সেটিং উপেক্ষিত হয়। `timeout`, `extra_headers` আর `extra_body` রিকোয়েস্টে পাঠানো হয়। [`TypeSafeModelSettings`][pydantic_ai.models.typesafe.TypeSafeModelSettings] প্রতিটি decision model-এর দুটি [threshold](decision.md#confidence-and-thresholds) যোগ করে, `decision_boolean_threshold` আর `decision_route_threshold`।

আগের `typesafe_boolean_threshold` নামটি `decision_boolean_threshold`-এর একটি deprecated alias হিসেবে থাকে। আগের `typesafe_tool_call_threshold` deprecated আর উপেক্ষিত: Jev সবসময় সবচেয়ে সম্ভাব্য route নেয়, আর একটি [`FallbackModel`](decision.md#handing-off-an-unsure-route)-সহ `decision_route_threshold` বদলে যে বাছাইয়ে সে অনিশ্চিত সেগুলো একটি ভাষা মডেলে দেয়।

⟦CODE9⟧

/// check | সংক্ষেপে মনে রাখুন

* `TYPESAFE_API_KEY` সেট, তারপর `Agent('typesafe:jev-latest', output_type=...)`; threshold ঠিক করলে সংস্করণ pin করুন।
* প্রশ্ন আসে আউটপুট টাইপের docstring থেকে; প্রতিটি ফিল্ডে এক প্রশ্ন।
* সীমা: এক-বাছাইয়ে 255 বিকল্প, rubric-এ 10 স্তর, প্রায় 32k token — দীর্ঘ কথোপকথন compact করুন।
* গণনা/তারিখ Python-এ করুন; লেখা তৈরি বা কম আত্মবিশ্বাসে ভাষা মডেলে fallback।

///
