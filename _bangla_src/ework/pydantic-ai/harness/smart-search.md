
# Smart Search { #smart-search }

/// note | এই পেজে যা শিখবেন

* `SmartSearch` দিয়ে আচরণ দিয়ে কোড খোঁজা — "মেয়াদোত্তীর্ণ session কোথায় প্রত্যাখ্যান হয়?" এর মতো সাধারণ ভাষায়।
* সার্চের চারটি ধাপ: তালিকা → টুকরো → shortlist (BM25) → বিচার (judge মডেল)।
* বড় codebase-এ index cache, judge মডেল বাছাই, usage-সীমা আর telemetry।

///

`SmartSearch` একটি এজেন্টকে আচরণ দিয়ে কোড সার্চ দেয়: মডেল যে আচরণ খুঁজছে তা সাধারণ ইংরেজিতে বর্ণনা করে ("where do we reject expired sessions?") আর ফাইল ও লাইন-পরিসরসহ র‍্যাঙ্ক করা source অংশ ফেরত পায়, আগে একটি text সার্চের দরকারি symbol নাম অনুমান না করেই। প্রাসঙ্গিকতা ঠিক করে আপনার বাছা একটি judge মডেল: যেকোনো Pydantic AI মডেল কাজ করে, আর একটি [decision model](../models/decision.md), [System One API](../models/system-one.md) দিয়ে পরিবেশিত বা TypeSafe-এর Jev হিসেবে, সুপারিশকৃত ধরন।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/smart_search/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

একটি অপরিচিত repository-তে ফেলা একটি coding এজেন্ট এর প্রথম turn-গুলো কোড খুঁজতে খরচ করে: identifier অনুমান, অনুসন্ধানমূলক `grep` কলের শৃঙ্খল, আর জরুরি একটি ফাংশন খুঁজতে পুরো ফাইল তালিকা ও পড়া। প্রতিটি ব্যর্থতায় একটি round trip খরচ হয় আর context এমন কোডে ভরে যা এটি ফেলে দেবে। Text সার্চ শুধু তা-ই খোঁজে যার নাম আপনি আগে থেকেই জানেন।

/// tip | উদাহরণ দিয়ে বুঝি

`grep "expire"` শুধু সেই লাইন খোঁজে যেখানে ঠিক "expire" লেখা আছে। কিন্তু আসল কোড হয়তো `if now > token.valid_until: raise Unauthorized()` — কোথাও "expire" শব্দই নেই! Smart Search প্রশ্নের *অর্থ* বোঝে: আগে BM25 দিয়ে সম্ভাব্য 128টি টুকরো বাছে, তারপর একটি judge মডেলকে প্রতিটি জিজ্ঞেস করে "এই কোড কি সত্যিই মেয়াদোত্তীর্ণ session প্রত্যাখ্যান করে?"

///

## ব্যবহার { #usage }

judge-কে `model` হিসেবে দিন, যা বাধ্যতামূলক (দেখুন [Choosing the judge](#choosing-the-judge))। `SmartSearch` রানের [workspace](../workspace.md) খোঁজে, তাই এর পাশে একটি যুক্ত করুন:

⟦CODE1⟧

workspace-কে কমান্ড চালাতে পারতে হবে আর এর `PATH`-এ [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) থাকতে হবে, যা খোঁজার ফাইল তালিকা করে। `coder` extra একটি লোকাল workspace-এর জন্য `rg` ইনস্টল করে; একটি sandbox image-এ এটি ইনস্টল করা লাগে। কমান্ড চালাতে পারে না এমন একটি workspace-এ টুলটি দেওয়া হয় না, আর workspace ছাড়া একটি রান শুরুতেই ব্যর্থ হয়।

## সেটিং { #settings }

| সেটিং | ডিফল্ট | অর্থ |
|---|---|---|
| `model` | বাধ্যতামূলক | judge: যেকোনো মডেল বা মডেলের নাম। নাম দিয়ে দেওয়া একটি judge প্রতিটি রিকোয়েস্ট 30 সেকেন্ড পরে timeout করে; একটি মডেল instance নিজের `settings` রাখে। |
| `threshold` | `0.5` | একটি snippet ফেরত দিতে যে প্রাসঙ্গিকতা (দুটি বিচারের গুণফল, 0 থেকে 1) লাগে। Jev-এর জন্য সমন্বয় করা; দেখুন [Choosing the judge](#choosing-the-judge)। |
| `concurrency` | `8` | একসাথে বিচার করা snippet। |
| `cache_index` | `False` | সার্চের মাঝে প্রতিটি খোঁজা ডিরেক্টরির index মেমরিতে রাখা; দেখুন [Large codebases](#large-codebases)। |
| `guidance` | `None` | টুল দেওয়া হলেই যোগ করা খোঁজার instructions: ডিফল্টের জন্য `None`, যা মডেলকে অনুসন্ধানমূলক text সার্চের আগে `smart_search` ধরতে বলে, কিছু না-র জন্য `''`। |

## টুল { #tool }

| টুল | উদ্দেশ্য |
|---|---|
| `smart_search` | কোড কী করে তা দিয়ে খোঁজা: সাধারণ ইংরেজিতে `query`, ঐচ্ছিকভাবে `directory` আর একটি ripgrep `glob` দিয়ে পরিসীমিত, সর্বোচ্চ `candidates` snippet বিচারের পর সর্বোচ্চ `limit` মিল ফেরত দেয়। |

একটি সার্চ চারটি ধাপে চলে:

1. **তালিকা** — `rg --files` দিয়ে `directory`-এর নিচের ফাইল, যা `.gitignore` মানে আর লুকানো ফাইল বাদ দেয়। Binary, non-UTF-8 আর minified ফাইল বাদ পড়ে আর গোনা হয়।
2. **টুকরো** — প্রতিটি ফাইল snippet-এ: সাধারণ লেখার overlapping 60-লাইনের window, Python বাদে, যা standard library দিয়ে পার্স হয় যাতে ফাংশন, মেথড আর ক্লাস snippet হয়, একটি লম্বা ফাংশনের ব্লকগুলো নিজস্ব snippet হিসেবে।
3. **Shortlist** — লোকাল [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) দিয়ে query-র সাথে সবচেয়ে ভালো মেলে এমন `candidates` snippet (ডিফল্ট 128, সর্বোচ্চ 256), path আর symbol নামে বেশি ওজন দিয়ে আর সাধারণ programming সমার্থক শব্দ বিস্তার করে।
4. **বিচার** — প্রতিটি shortlist করা snippet judge মডেল দিয়ে, যা মূল্যায়ন করে snippet-টি query যার নাম দেয় তার ওপর কতটা কাজ করে আর query যে কাজ বর্ণনা করে তা কতটা ভালোভাবে করে। একটি snippet-এর প্রাসঙ্গিকতা দুটির গুণফল, আর `threshold`-এর সমান বা ওপরেরগুলো ফেরত আসে, সেরাটি প্রথমে, প্রতিটি সর্বোচ্চ 12 লাইনের একটি কেন্দ্রীভূত অংশসহ।

ফল একটি `SmartSearchResult`: মিলগুলো, কতগুলো পেরিয়েছে কিন্তু `limit` দিয়ে কাটা পড়েছে, কভারেজের সংখ্যা (দেখা আর বাদ পড়া ফাইল, তৈরি আর বিচার করা snippet, আর shortlist সম্পূর্ণ ছিল কিনা) আর সতর্কবার্তা, যাতে মডেল একটি খালি ফল আর কিছুই না পাওয়া একটি সম্পূর্ণ সার্চের পার্থক্য বুঝতে পারে। টেস্ট ফাইলের মিল নিচে নামানোর বদলে `kind='test'` লেবেল পায়।

একটি ব্যর্থ বিচার পুরো সার্চ ব্যর্থ করে, আর error মডেলকে একটি টুল ব্যর্থতা হিসেবে জানানো হয়, যাতে এটি অর্ধেক-বিচার করা ফলের ওপর কাজ না করে নিয়মিত সার্চে ফিরে যেতে পারে।

## বড় codebase { #large-codebases }

একটি সার্চ 200,000 ফাইল (`glob`-এর পরে গোনা), 5 কোটি লাইন আর 2 GiB source-এ সীমিত, Linux kernel-এর জন্য যথেষ্ট; এর বেশি হলে এটি মডেলকে `directory` বা `glob` সরু করতে বলে। caching ছাড়া, প্রতিটি সার্চ এর ডিরেক্টরি শুরু থেকে পড়ে, টুকরো করে আর index করে।

সার্চের মাঝে, এজেন্টের জীবনকাল জুড়ে, প্রতিটি খোঁজা ডিরেক্টরির index রাখতে `cache_index=True` সেট করুন:

⟦CODE2⟧

একই ডিরেক্টরির পরের সার্চ তবুও প্রতিটি ফাইল পড়ে, যেকোনো workspace-এ content hash দিয়ে পরিবর্তন ধরতে, কিন্তু শুধু বদলানো ফাইল টুকরো আর index করে। এক ডিরেক্টরিতে সমান্তরাল `smart_search` কল পালা নেয়, তাই এর index প্রতিটি কলের বদলে একবার তৈরি হয়। Pydantic AI repository-তে (4,500 ফাইল, 20 লাখ লাইন, 126,000 snippet), প্রথম সার্চ index তৈরিতে প্রায় 9 সেকেন্ড খরচ করেছে আর পরেরগুলো এটি হালনাগাদে এক সেকেন্ডেরও কম, cache ছাড়া প্রতিটি সার্চের 10 থেকে 14 সেকেন্ডের বিপরীতে। সর্বোচ্চ চারটি ডিরেক্টরি (প্রতিটি এর `glob`-সহ) রাখা হয়, সবচেয়ে কম সম্প্রতি খোঁজাটি আগে বাদ পড়ে, আর মেমরি এরা যে source রাখে তার সাথে বাড়ে।

## Judge বাছাই { #choosing-the-judge }

judge বাধ্যতামূলক, আর যেকোনো Pydantic AI মডেল বা মডেলের নাম, `model` হিসেবে দেওয়া। এটি ঠিক করে কোন provider খোঁজা source পায়, তাই এটি কখনো আপনার জন্য বাছা হয় না।

/// warning | সতর্কতা

judge মডেল আপনার source code-এর টুকরো পায়। একটি গোপন codebase-এ একটি cloud judge দিলে আপনার কোড সেই provider-এর কাছে যায়। সংবেদনশীল কোডে একটি লোকাল judge (যেমন Ollama-চালিত একটি System One মডেল) বিবেচনা করুন।

///

একটি [decision model](../models/decision.md) সুপারিশকৃত judge: এটি প্রতিটি প্রাসঙ্গিকতা-প্রশ্নের উত্তর একটি সম্ভাবনা দিয়ে দেয়, একটি language model একটি লিখতে যে সময় নেয় তার ভগ্নাংশে, যা প্রতি সার্চে 128টি বিচারের দরকার। একটি ব্যবহারের দুটি উপায়:

- **[System One API](../models/system-one.md) দিয়ে পরিবেশিত যেকোনো decision model**, যেমন CLM, Laya, বা লোকালে [Ollama](../models/system-one.md#ollama)-চালিত একটি। `SYSTEM_ONE_BASE_URL` সেট করুন, আর API-র key লাগলে `SYSTEM_ONE_API_KEY`, তারপর `model='system-one:<name>'` দিন, বা একটি [`SystemOneModel`][pydantic_ai.models.system_one.SystemOneModel]। এর জন্য `pydantic-ai-slim`-এর বাইরে কিছু লাগে না।
- **TypeSafe-এর SDK দিয়ে [Jev](../models/typesafe.md)**, `model='typesafe:jev-latest'` হিসেবে, `TYPESAFE_API_KEY` সেট করে।

TypeSafe-এর SDK ইনস্টল করতে:

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


নাম দিয়ে দেওয়া একটি judge প্রতিটি রিকোয়েস্ট 30 সেকেন্ড পরে timeout করে; একটি মডেল instance নিজের `settings` রাখে, তাই একটি ধীর judge-এর জন্য, যেমন একটি লোকাল, এতে `settings={'timeout': ...}` সেট করুন।

যেকোনো language model-ও কাজ করে, কারণ দুটি মূল্যায়ন সাধারণ কাঠামোবদ্ধ আউটপুট। যেহেতু একটি সার্চ সর্বোচ্চ `candidates`-সংখ্যক judge রিকোয়েস্ট করে, একটি decision model ব্যবহার না করলে রানের নিজেরটির বদলে একটি ছোট, দ্রুত মডেল পছন্দ করুন।

`threshold` (ডিফল্ট 0.5) Jev-এর সম্ভাবনার জন্য সমন্বয় করা। অন্য একটি decision model-এর সম্ভাবনা, আর তার চেয়েও বেশি একটি language model-এর মূল্যায়ন, ভিন্নভাবে মাপা হতে পারে, তাই কয়েকটি সার্চ যাচাই করুন আর ফল খুব কম বা খুব কোলাহলপূর্ণ হলে এটি সমন্বয় করুন। এর বিপরীতে `threshold` সমন্বয় করার পর একটি মডেল version pin করুন (যেমন `'typesafe:jev-1.13.0'`)।

## Usage আর সীমা { #usage-and-limits }

প্রতিটি বিচার করা snippet রানের [usage](../agent.md#usage-limits)-এ একটি রিকোয়েস্ট হিসেবে গোনা হয়, আর judge-এর token এতে যোগ হয়, তাই `result.usage` আর রানের [`UsageLimits`][pydantic_ai.usage.UsageLimits] সার্চটি কভার করে। একটি সার্চ যাতে পুরো রান শেষ না করে, এটি রানের `request_limit`-এর বাকি রিকোয়েস্টের সর্বোচ্চ অর্ধেক বিচার করে, মডেলের পরের turn-এর জন্য একটি রাখার পর। shortlist-এর সেরা-র‍্যাঙ্কের snippet আগে বিচার হয়, আর একটি সতর্কবার্তা বলে কতগুলো অবিচারিত রয়ে গেছে। ডিফল্ট `request_limit` 50-এর অধীনে, একটি রানের প্রথম সার্চ 24টি snippet বিচার করে। পূর্ণ 128-snippet সার্চের জন্য সীমা বাড়ান, যেমন `agent.run(..., usage_limits=UsageLimits(request_limit=500))` দিয়ে। খরচ করার মতো কোনো রিকোয়েস্ট বাকি না থাকলে, সার্চ ব্যর্থ হয় আর মডেলকে নিয়মিত সার্চ ব্যবহার করতে বলা হয়।

/// info | হিসাবটি সহজ ভাষায়

ডিফল্ট `request_limit=50`। এক রিকোয়েস্ট মডেলের পরের turn-এর জন্য রাখা হয় → 49 বাকি। এর অর্ধেক (নিচে গোল করে) → **24**টি snippet বিচার হয়। তাই ডিফল্ট সীমায় Smart Search পুরো 128 নয়, শুধু সেরা 24টি দেখে। পূর্ণ শক্তিতে চালাতে `request_limit` বাড়ান।

///

## Telemetry { #telemetry }

প্রতিটি সার্চ এর tool call-এর নিচে রানের tracer-এ একটি `smart search` span খোলে। span-টির এই attribute আছে:

- `smart_search.judge_model`: judge মডেল।
- `smart_search.files`, `.skipped_files`, `.snippets` আর `.evaluated`: কভারেজের সংখ্যা।
- `smart_search.indexed_files`: সার্চ কতগুলো ফাইল টুকরো আর index করেছে। `cache_index`-সহ, শুধু নতুন আর বদলানো ফাইল হয়, তাই এটি দেখায় cache কতটা বাঁচিয়েছে।
- `smart_search.selection_complete`: কভারেজ সম্পূর্ণ ছিল কিনা।
- `smart_search.matches` আর `.omitted_matches`: কতগুলো মিল ফেরত এসেছে আর কাটা পড়েছে।
- `smart_search.query`: query, শুধু যখন রান trace-এ কনটেন্ট অন্তর্ভুক্ত করে।

একটি ব্যর্থ সার্চ এই span-এ কোনো exception লেখে না; ঘেরা tool span এটি জানায়, রানের `include_content` দিয়ে মুছে। judge রানগুলো নিজে instrument করা হয় না। এদের prompt source snippet বহন করে, তাই global instrumentation যেন host এজেন্টের নিজস্ব `instrument` বা `include_content` সেটিংয়ের বাইরে এগুলো export না করে। এদের usage তবুও রানের-টিতে যোগ হয়।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`SmartSearch` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে:

⟦CODE3⟧

⟦CODE4⟧

এজেন্ট চালানোর সময় workspace যুক্ত করুন, `agent.run(..., workspace=...)` দিয়ে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.smart_search.SmartSearch`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smart-search/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.smart_search.SmartSearchResult`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smart-search/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.smart_search.SmartSearchMatch`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smart-search/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.smart_search.SmartSearchCoverage`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smart-search/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `SmartSearch(model=...)` — অর্থ দিয়ে কোড খোঁজে; judge মডেল বাধ্যতামূলক (decision model সুপারিশকৃত)।
* workspace-এ কমান্ড চালানো আর `rg` লাগে।
* ধাপ: `rg --files` → snippet → BM25 shortlist (128) → judge-এর বিচার → `threshold`-এর ওপরেরগুলো।
* বড় repo-তে `cache_index=True`; ডিফল্ট `request_limit=50`-এ শুধু 24টি snippet বিচার হয়।
* judge আপনার source দেখে — গোপন কোডে লোকাল judge বিবেচনা করুন।

///
