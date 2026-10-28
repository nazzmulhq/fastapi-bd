
# You.com { #youcom }

/// note | এই পেজে যা শিখবেন

* `YouSearch` (`web_search`, `get_page`) আর `YouResearch` (`answer`, `research`, `finance_research`) দিয়ে [You.com](https://you.com)-চালিত ওয়েব গবেষণা।
* গবেষণার মাত্রা (`research_effort`), কাঠামোবদ্ধ উদ্ধৃতি, একাধিক instance আর core `WebSearch`-এর সাথে সংঘর্ষ এড়ানো।

///

`YouSearch` আর `YouResearch` একটি এজেন্টকে [You.com](https://you.com) API-চালিত ওয়েব গবেষণার টুল দেয়। `YouSearch` যোগ করে `web_search` আর `get_page`, ওয়েব জরিপ আর একটি পেজ পুরো পড়ার জন্য। `YouResearch` যোগ করে `answer`, `research` আর `finance_research`, এমন প্রশ্নের উদ্ধৃতিসহ উত্তরের জন্য যা একটি একক খোঁজে মীমাংসা হয় না।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/youdotcom/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

কিছু সার্চ টুল শুধু একটি শিরোনাম আর একটি snippet ফেরত দেয়, তাই এজেন্টকে উৎস বিচার করার আগে পেজ আনতে হয়। অন্যগুলো পুরো পেজ ফেরত দেয়, যা context-কে এমন লেখায় ভরায় যা এজেন্ট ফেলে দেয়। আর কিছু প্রশ্ন একদমই একটি খোঁজ নয়: এদের উত্তরে অনেক সার্চ, ফল জুড়ে পড়া আর উদ্ধৃতিসহ একটি উত্তর লেখা লাগে।

`YouSearch` আর `YouResearch` You.com-এর সার্চ, পেজ আর গবেষণা API দুটি [capability](../capabilities/overview.md) হিসেবে মোড়ায়। প্রতিটি নিজের টুল, ওই টুল কতটা লেখা ফেরত দেয় তার একটি সীমা আর system prompt-এর জন্য সংক্ষিপ্ত গবেষণা-নির্দেশনা আনে।

## ব্যবহার { #usage }

`youdotcom` extra ইনস্টল করুন আর `YDC_API_KEY` environment variable সেট করুন (<https://api.you.com>-এ একটি key তৈরি করুন; পুরনো `YOU_API_KEY_AUTH`-ও মানা হয়)। নিচের উদাহরণগুলো একটি Anthropic মডেল আর `Agent.from_file` ব্যবহার করে, তাই এগুলো `anthropic` provider আর `spec` YAML সমর্থনও টেনে আনে:

/// tab | pip

```bash
pip install "pydantic-ai-harness[youdotcom,anthropic]" "pydantic-ai-slim[spec]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[youdotcom,anthropic]" "pydantic-ai-slim[spec]"
```

///


তারপর `capabilities` প্যারামিটার দিয়ে একটি `Agent`-এ capability দিন:

⟦CODE1⟧

শুধু সার্চ আর পেজ পড়া দরকার হলে একা `YouSearch` ব্যবহার করুন।

## টুল { #tools }

| টুল | Capability | উদ্দেশ্য |
|---|---|---|
| `web_search` | `YouSearch` | ওয়েবে সার্চ করে শীর্ষ `num_results` পেজ ফেরত দেয়, প্রতিটি শিরোনাম, URL আর এর সবচেয়ে প্রাসঙ্গিক অংশসহ। |
| `get_page` | `YouSearch` | একটি নির্দিষ্ট URL-এর markdown আনে -- একটি সম্ভাবনাময় `web_search` ফল, বা ব্যবহারকারীর দেওয়া একটি URL। |
| `answer` | `YouResearch` | এক কলে লাইভ ওয়েব ফলে ভিত্তি করে উদ্ধৃতিসহ একটি সংশ্লেষিত উত্তর। |
| `research` | `YouResearch` | অনেক উৎস জুড়ে পড়া বহু-ধাপের গবেষণা চালিয়ে একটি পুঙ্খানুপুঙ্খ, উদ্ধৃতিসহ উত্তর ফেরত দেয়। |
| `finance_research` | `YouResearch` | `research`-এর অর্থ-সমন্বিত প্রতিরূপ, কোম্পানি, বাজার আর instrument-এর জন্য। |

`web_search` পুরো পেজের বদলে প্রতিটি পেজের সংক্ষিপ্ত অংশ ফেরত দেয়, তাই কয়েকটি উৎস দেখা সস্তা থাকে। এজেন্ট তারপর এর বাছা একটি পেজ `get_page` দিয়ে পড়ে। এর বদলে প্রতিটি ফলের পুরো markdown পেতে `extraction_mode='full_page'` সেট করুন।

`get_page` আর পূর্ণ-পেজ `web_search`-এর লেখা `max_text_chars` অক্ষরে সীমিত, **শুরুর অংশ** রেখে (একটি পেজের শুরুতেই মূল কথা থাকে); একটি পেজ সীমা ছাড়ালে আউটপুট একটি `[... page text truncated at N characters]` চিহ্ন দিয়ে শেষ হয়। ফলের সংখ্যাও একইভাবে সীমিত: `num_results` You.com-এ পাঠানো হয়, আর ফেরত আসা response-এ আবার প্রয়োগ হয়।

কিছুই মেলে না এমন একটি `web_search` query একটি বৈধ উত্তর, error নয়: টুল `No results found for {query!r}.` ফেরত দেয়। অন্য ব্যর্থতা মডেলে একটি [`ModelRetry`](../tools-advanced.md#tool-retries) হিসেবে পৌঁছায়: খালি ফেরত আসা একটি URL বা প্রশ্ন, একটি rate limit, You.com-এর প্রত্যাখ্যাত একটি প্যারামিটার (422), বা একটি সাময়িক API বা নেটওয়ার্ক সমস্যা। রান চলতে থাকে, আর মডেল URL ঠিক করতে, প্রশ্ন নতুন করে লিখতে বা আবার চেষ্টা করতে পারে। authentication, billing আর অনুমতি ব্যর্থতা (401/402/403) আপনাকে নিজের সেটআপে ঠিক করতে হয়, তাই এগুলো রান থামায়।

## গবেষণা { #research }

এক কলে মীমাংসা হবে বলে আশা করেন এমন একটি সরাসরি প্রশ্নের জন্য `answer` ব্যবহার করুন। প্রশ্নে অনেক সার্চ আর উৎস জুড়ে একটি লেখা দরকার হলে `research` ব্যবহার করুন। `finance_research` হলো আর্থিক বিশ্লেষণের জন্য সমন্বিত `research`।

`research` poll করার জন্য একটি job ফেরত না দিয়ে এর ফলের অপেক্ষা করে, আর deep ও exhaustive গবেষণায় নিয়মিত কয়েক মিনিট লাগে, তাই `timeout_ms`-এর ডিফল্ট 10 মিনিট। এটি কতটা খাটে তা ঠিক করে `research_effort`: `lite`, `standard`, `deep` বা `exhaustive`। You.com-এর একটি `frontier` স্তরও আছে, কিন্তু এটি শুধু একটি background job হিসেবে চলে, তাই এই capability এটি দেয় না। `finance_research`-এর নিজস্ব `finance_effort` আছে: `deep` বা `exhaustive`।

⟦CODE2⟧

/// info | এক নজরে: কোন টুল কখন

| প্রশ্ন | টুল | আনুমানিক সময় |
|--------|------|---------------|
| "Python 3.13 কবে release হয়েছে?" | `web_search` বা `answer` | কয়েক সেকেন্ড |
| "এই তিনটি ডেটাবেসের তুলনা, সুবিধা-অসুবিধাসহ" | `research` (`standard`/`deep`) | এক থেকে কয়েক মিনিট |
| "এই কোম্পানির গত ৫ বছরের আর্থিক অবস্থা" | `finance_research` | কয়েক মিনিট |

///

`research`-কে গদ্যের বদলে কাঠামোবদ্ধ আউটপুট (JSON হিসেবে লেখা) ফেরত দেওয়াতে `output_schema` একটি JSON schema-তে সেট করুন। `research_effort` `'lite'` হলে You.com একটি `output_schema` প্রত্যাখ্যান করে, তাই দুটো একসাথে চাইলে capability তৈরির সময় একটি error ওঠে।

## কাঠামোবদ্ধ উদ্ধৃতি { #structured-citations }

প্রতিটি টুল একটি [`ToolReturn`](../tools-advanced.md#advanced-tool-returns) ফেরত দেয়। এর `return_value` হলো মডেল যে লেখা দেখে, টুলের উদ্ধৃতি থাকলে একটি `Sources:` ব্লক যোগ করে। এর `metadata['sources']` একই উৎস `YouSource` রেকর্ড হিসেবে রাখে (`{'url': ..., 'title': ...}`)। `web_search` tracing-এর জন্য response-এর `search_uuid` আর `latency`-ও metadata-য় রাখে। মডেল metadata দেখে না: আপনার অ্যাপ্লিকেশন এটি message history-র `ToolReturnPart` থেকে পড়ে, তাই আপনি কোনো লেখা পার্স না করে উদ্ধৃতি দেখাতে পারেন:

⟦CODE3⟧

## Instructions { #instructions }

`YouSearch` system prompt-এ সংক্ষিপ্ত গবেষণা-নির্দেশনা যোগ করে: প্রথমে `web_search` দিয়ে প্রশস্তভাবে সার্চ করো, সিদ্ধান্তে পৌঁছানোর আগে সবচেয়ে সম্ভাবনাময় পেজ `get_page` দিয়ে পুরো পড়ো, প্রাথমিক উৎস পছন্দ করো, আর ব্যবহৃত URL উদ্ধৃত করো। `YouResearch` কখন `answer`, `research` আর `finance_research` ব্যবহার করতে হবে তার নির্দেশনা যোগ করে। দুটোই মডেলকে এর আনা ওয়েব কনটেন্টকে মানার নির্দেশনা নয়, অবিশ্বস্ত ডেটা হিসেবে ধরতে বলে। যেকোনো capability-তে, ডিফল্ট বদলাতে `guidance` আপনার নিজের লেখায় সেট করুন, বা কিছু না যোগ করতে `''`।

## কনফিগারেশন { #configuration }

`YouSearch`-এর প্রতিটি ফিল্ড এর ডিফল্টসহ:

⟦CODE4⟧

`YouResearch`-এর প্রতিটি ফিল্ড এর ডিফল্টসহ:

⟦CODE5⟧

`include_domains` একটি allowlist, আর `exclude_domains` বা `boost_domains`-এর সাথে জোড়া যায় না। এগুলো জুড়লে capability তৈরির সময় একটি error ওঠে, যেমন ওঠে সীমার বাইরের মান আর একটি অবৈধ `freshness`-এ। domain, `freshness` আর `country` সেটিং `web_search`, `answer` আর `research`-এ প্রযোজ্য। `finance_research` শুধু এর input আর `finance_effort` নেয়।

## একাধিক instance { #multiple-instances }

একই capability-র দুটি instance একই টুলের নাম নিবন্ধন করে, আর ডিফল্ট `id` (`you_search` বা `you_research`) ভাগ করে, তাই ভিন্ন দুটি একটি error তোলে। একটি এজেন্টে একাধিক সেটআপ চালাতে -- ধরুন একটি খোলা ওয়েবে `YouSearch` আর একটি কয়েকটি domain-এ সীমিত -- প্রতিটি বাড়তিকে একটি আলাদা `id` দিন আর core-এর `PrefixTools` capability-তে মুড়ুন। এটি এদের টুলের নামের সামনে একটি prefix বসায়:

⟦CODE6⟧

মোড়ানো instance-এ `guidance=''` সেট করুন (বা এমন লেখা দিয়ে বদলান যা মডেলকে বলে কখন prefix-যুক্ত টুল ব্যবহার করতে হবে), কারণ প্রতিটি instance অন্যথায় একই ডিফল্ট গবেষণা-নির্দেশনা দেয়।

## Durable execution { #durable-execution }

[durable execution](../durable_execution/overview.md)-এর অধীনে, প্রতিটি You.com রিকোয়েস্ট লেখা হয়, তাই একটি উদ্ধার হওয়া রান রিকোয়েস্ট আবার না করে ফল পুনর্ব্যবহার করে। Temporal আর Prefect প্রতিটি টুল কল নিজস্ব activity বা task-এ লেখে। DBOS ফাংশন টুল workflow কোডে চালায়, তাই সেখানে রিকোয়েস্ট নিজস্ব step হিসেবে চলে।

Temporal-এ একটি activity ডিফল্টভাবে 60 সেকেন্ড পায়, যা `research` ছাড়াতে পারে: এটি `timeout_ms` পর্যন্ত অপেক্ষা করে, ডিফল্ট 600 সেকেন্ড। `TemporalDurability(toolset_activity_config={'you_research': ActivityConfig(...)})` দিয়ে টুল কলকে বেশি সময় দিন, capability-র `id` দিয়ে key করা, যেমন [Temporal timeouts](../durable_execution/temporal.md#harness-command-timeouts)-এ।

/// warning | সাধারণ ভুল

Temporal-এ `YouResearch(research_effort='deep')` চালিয়ে বারবার activity timeout দেখা। ডিফল্ট activity 60 সেকেন্ড, কিন্তু deep গবেষণায় কয়েক মিনিট লাগে। ওপরের মতো `you_research`-এর activity timeout অন্তত `timeout_ms`-এর সমান করুন।

///

রেকর্ডগুলোর নাম capability-র `id` অনুযায়ী, যার ডিফল্ট `YouSearch`-এর জন্য `you_search` আর `YouResearch`-এর জন্য `you_research`, তাই durable execution-এ কোনো কনফিগারেশন লাগে না। একটি `id` বদলালে রেকর্ডের নাম বদলে যায়, যা চলমান রান তখন খুঁজে পায় না।

## নিজস্ব client { #custom-client }

ডিফল্ট client হলো `YDC_API_KEY` environment variable থেকে তৈরি `youdotcom.You`। সেই variable সেট না থাকলে, capability তৈরি কীভাবে ঠিক করবেন বলা একটি বার্তাসহ ব্যর্থ হয়। নিজে API key সেট করতে, একটি ভিন্ন host-এ নির্দেশ করতে, বা টেস্টে একটি নকল ব্যবহার করতে, `YouClient` protocol-এ তালিকাভুক্ত মেথডসহ যেকোনো অবজেক্ট দিন:

⟦CODE7⟧

## YouSearch বনাম core WebSearch { #yousearch-vs-core-websearch }

Core একটি [`WebSearch`](../capabilities/overview.md#provider-adaptive-tools) capability দেয় যা মডেলের সাথে মানিয়ে নেয়: মডেলের একটি থাকলে এটি provider-এর নিজস্ব সার্চ ব্যবহার করে, আর অন্য মডেলে exception তোলে যদি না আপনি একটি `local=` বিকল্প দেন, যেমন DuckDuckGo-র জন্য `local=True`। আপনি যে মডেলই চালান তাকে অনুসরণ করা সার্চ চাইলে এটি ব্যবহার করুন। প্রতিটি মডেলে একই সার্চ চাইলে `YouSearch` ব্যবহার করুন: একটি vendor, প্রতিটি ফলের সাথে অংশ, আপনার চাওয়া পেজ পড়া, domain ছাঁকনি আর সতেজতা (freshness) নিয়ন্ত্রণ।

যেখানে provider-এর সার্চ আছে সেখানে সেটি আর অন্যত্র You.com-এরটি ব্যবহার করতে, হয়:

- `YouSearch(native=True)` সেট করুন। capability নেটিভ web search টুল যোগ করে, আর You.com-এর `web_search` শুধু একটি ছাড়া মডেলে পাঠানো হয়।
  `get_page` প্রতিটি মডেলে উপলব্ধ থাকে। `include_domains` আর `exclude_domains` নেটিভ টুলের `allowed_domains` আর `blocked_domains` হয়ে যায়।
  যে মডেলের নেটিভ সার্চ আপনার সেট করা একটি domain ছাঁকনি প্রয়োগ করতে পারে না, সে এর বদলে You.com-এর `web_search` পায়, তাই ছাঁকনি তবুও বজায় থাকে: Gemini-তে, যার নেটিভ সার্চ কোনো domain ছাঁকনি নেয় না, যেকোনো লিস্ট সেট করলে You.com সার্চ করে।
- অথবা core `WebSearch`-এর বিকল্প হিসেবে You.com-এর সার্চ দিন, `WebSearch`-এর নিজস্ব অপশন দিয়ে নেটিভ সার্চ কনফিগার করতে:

  ⟦CODE8⟧

অন্যথায়, একটি এজেন্টকে একটি web search capability দিন: core `WebSearch`, harness `ExaSearch`, বা `YouSearch`। এরা সবাই টুলের নাম একইভাবে দেয় -- `web_search`, আর দুটি harness-এরগুলোর জন্য `get_page` -- আর একটি এজেন্টের একই নামের দুটি টুল থাকতে পারে না, তাই তৈরির সময় এটি ব্যর্থ হয়। তবুও দুটি চাইলে, এর টুলের নাম বদলাতে একটি `PrefixTools`-এ মুড়ুন, যেমন [Multiple instances](#multiple-instances)-এ দেখানো। একটি বাড়তি ক্ষেত্র আছে: Anthropic মডেলে বিল্ট-ইন সার্চের নামও `web_search`, তাই সেখানে ডিফল্ট `YouSearch()`-এর সাথে `WebSearch` সংঘর্ষ করে, যদিও সার্চ Anthropic-এর দিকে চলে। এর বদলে `YouSearch(native=True)` ব্যবহার করুন, বা core-এর সার্চকে DuckDuckGo টুলে বদলাতে `WebSearch(native=False, local=True)` দিন, যার নাম `duckduckgo_search` আর সংঘর্ষ করে না।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`YouSearch` আর `YouResearch` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে, তাই আপনি Python-এর বদলে একটি config ফাইলে এগুলো ঘোষণা করতে পারেন:

⟦CODE9⟧

⟦CODE10⟧

`custom_capability_types` দিন, যাতে spec loader জানে capability-গুলো কীভাবে তৈরি করতে হয়। `client` ফিল্ড spec-serialize-যোগ্য নয়; spec-লোড instance সবসময় `YDC_API_KEY` থেকে ডিফল্ট client তৈরি করে। spec-এ, `output_schema` JSON-schema dict রূপ নেয়।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Toolsets](../toolsets.md)
- [You.com API documentation](https://documentation.you.com)

## API রেফারেন্স { #api-reference }

⟦CODE11⟧

⟦CODE12⟧

⟦CODE13⟧

⟦CODE14⟧

⟦CODE15⟧

/// check | সংক্ষেপে মনে রাখুন

* `YouSearch()` = `web_search` + `get_page`; `YouResearch()` = `answer` + `research` + `finance_research`; key `YDC_API_KEY`।
* `research_effort`: `lite`/`standard`/`deep`/`exhaustive`; `timeout_ms` ডিফল্ট 10 মিনিট।
* উৎস `ToolReturn.metadata['sources']`-এ।
* এক এজেন্টে একটিই web search capability — নইলে `PrefixTools`; Anthropic-এ `YouSearch(native=True)`।
* Temporal-এ `research`-এর activity timeout বাড়ান।

///
