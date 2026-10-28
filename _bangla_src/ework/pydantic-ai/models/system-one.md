# System One API { #system-one-api }

/// note | এই পেজে যা শিখবেন

* decision model কী, আর `POST /v1/systemone` API-র পেছনের যেকোনো decision model `SystemOneModel` দিয়ে চালানো।
* Ollama দিয়ে লোকালে দ্রুত শুরু (Nimble), অন্য সার্ভারের কনফিগারেশন।
* মডেল সেটিং আর profile-এ সীমা ঘোষণা।

///

একটি [decision model](decision.md) একটি লেখা নিয়ে টাইপ করা প্রশ্নের উত্তর দেয়, প্রতিটি একটি সম্ভাবনা বা বিকল্পগুলোর ওপর একটি বণ্টনসহ, লেখা না লিখে: দ্রুত, এক-নজরের "System 1" বিচার, একটি ভাষা মডেলের ধাপে ধাপে "System 2" reasoning-এর পাশে। TypeSafe-এর Jev এই প্রশ্নগুলোর উত্তর দেয় একটি `POST /v1/systemone` API দিয়ে, আর একই API দিয়ে অন্য decision model-ও পাওয়া যায়, যেমন [Contrastive Language Models](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B) (CLM) আর [Laya](https://huggingface.co/convaiinnovations/laya), আর [Ollama](#ollama) এর মাধ্যমে লোকালে decision model চালায়।

/// tip | উদাহরণ দিয়ে বুঝি

একটি ভাষা মডেলকে "এই টিকিটটি কোন বিভাগের?" জিজ্ঞেস করলে সে একটি অনুচ্ছেদ লেখে। একটি decision model সরাসরি একটি ঘরে টিক দেয় — "বিলিং" — সাথে বলে সে কতটা নিশ্চিত (ধরুন ৯২%)। দ্রুত, সস্তা, আর আত্মবিশ্বাস কম হলে মানুষের হাতে পাঠানো সহজ।

///

[`SystemOneModel`][pydantic_ai.models.system_one.SystemOneModel] এই API-র পেছনের যেকোনো decision model-এর Pydantic AI মডেল ক্লাস, আর [`DecisionModel`][pydantic_ai.models.decision.DecisionModel]-এর একটি subclass, [`TypeSafeModel`](typesafe.md)-এর মতো। একটির জন্য তৈরি একটি এজেন্ট মডেল বদলেই অন্যটিতে চলে। এর শুধু API-র URL লাগে, আর থাকলে এর key।

Pydantic AI-এর প্রতিটি মডেলের মতো, কাজটি দুই ভাগে বিভক্ত:

- **মডেল**, [`SystemOneModel`][pydantic_ai.models.system_one.SystemOneModel], API বলে: এটি একটি এজেন্ট রানকে `/v1/systemone` রিকোয়েস্টে রূপান্তর করে আর উত্তর পড়ে।
- **Provider**, [`SystemOneProvider`][pydantic_ai.providers.system_one.SystemOneProvider], বলে API কোথায় আর কীভাবে প্রমাণীকরণ করতে হবে। সেখানের মডেলকে কী জিজ্ঞেস করা যায় তা যায় এর [profile](#limits)-এ।

[`TypeSafeModel`](typesafe.md) আর তার provider একইভাবে ভাগ হয়, TypeSafe-এর SDK দিয়ে Jev-এর জন্য।

/// tip | Decision models দিয়ে শুরু করুন

**একটি এজেন্টের আউটপুট টাইপ, টুল আর বার্তার ইতিহাস কীভাবে একটি decision model-এর প্রশ্নে ম্যাপ হয়, আর উত্তরের অর্থ কী, তা শেখার জায়গা হলো [Decision models](decision.md)।**

///

## ইনস্টল { #install }

`SystemOneModel` HTTP দিয়ে API-র সাথে কথা বলে আর `pydantic-ai-slim`-এর বাইরে কিছুই লাগে না।

## Ollama দিয়ে দ্রুত শুরু { #ollama }

[Ollama](https://ollama.com) v0.35.0 আর পরের সংস্করণ এই API দিয়ে লোকালে decision model চালায়, যেমন Bespoke Labs-এর [Nimble](https://ollama.com/library/nimble) আর Together AI-এর [Tev1](https://ollama.com/library/tev1)। Ollama চালু রেখে, Nimble নামান:

```bash
ollama pull nimble
```

Pydantic AI-কে Ollama-র দিকে দেখান। লোকাল রিকোয়েস্টে কোনো API key লাগে না, আর URL-এ কোনো `/v1` প্রত্যয় নেই, Ollama-র [OpenAI-সামঞ্জস্যপূর্ণ API](ollama.md)-রটির মতো নয়:

```bash
export SYSTEM_ONE_BASE_URL='http://localhost:11434'
```

তারপর Nimble-কে দিয়ে একটি support ticket-এ লেবেল দেওয়ান:

⟦CODE1⟧

Nimble এক রিকোয়েস্টে একটি লেবেল বাছে, আর প্রতিটিতে কতটা নিশ্চিত তা জানায় [`provider_details`](decision.md#confidence-and-thresholds)-এ।

## কনফিগারেশন { #configuration }

অন্য যেকোনো সার্ভার ব্যবহার করতে, API-র URL, পেছনে `/v1` থাকুক বা না থাকুক, আর থাকলে এর key, environment variable হিসেবে সেট করুন:

⟦CODE2⟧

তারপর নাম দিয়ে `SystemOneModel` ব্যবহার করুন, `system-one:` আর তারপর API যে নামে মডেল দেয়, যেমন `system-one:clm-latest`, বা শুধু সেই নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE3⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE4⟧

একটি নিজের `http_client` দিয়েও [`SystemOneProvider`][pydantic_ai.providers.system_one.SystemOneProvider] নিজের মতো করতে পারেন:

⟦CODE5⟧

## মডেল সেটিং { #model-settings }

`temperature`, `timeout`, `extra_headers` আর `extra_body` রিকোয়েস্টে পাঠানো হয়, আর অন্য সাধারণ সেটিং, যেমন `top_p`, উপেক্ষিত হয়। `temperature`-এর প্রভাব আছে কিনা তা মডেলের ওপর নির্ভর করে: যেখানে আছে, এটি একটি [threshold](decision.md#confidence-and-thresholds) যে প্রতিটি সম্ভাবনা পড়ে তা সরায়। [`SystemOneModelSettings`][pydantic_ai.models.system_one.SystemOneModelSettings] প্রতিটি decision model-এর দুটি threshold যোগ করে, `decision_boolean_threshold` আর `decision_route_threshold`।

⟦CODE6⟧

## সীমা { #limits }

প্রতিটি মডেলের নিজের সীমা আছে, যেমন একটি এক-বাছাইয়ে কতগুলো বিকল্প থাকতে পারে বা কত দীর্ঘ লেখা পড়ে, যা প্রকাশক নথিভুক্ত করে। এগুলো মডেলের, client-এর নয়, তাই এগুলো যায় মডেলের [profile](../api/profiles.md)-এ একটি [`DecisionModelProfile`][pydantic_ai.profiles.decision.DecisionModelProfile] হিসেবে:

- `decision_max_choice_options`: বেশি বিকল্পের একটি এক-বাছাই রিকোয়েস্ট পাঠানোর আগেই প্রত্যাখ্যাত হয়।
- `decision_max_score_levels`: বেশি স্তরের পূর্ণসংখ্যা একটি rubric-এর বদলে [এক-বাছাই হিসেবে জিজ্ঞেস করা হয়](decision.md#what-each-field-type-does)।
- `decision_requires_instructions`: ডিফল্টভাবে চালু, কারণ API প্রতিটি প্রশ্নে `instructions` চায়, তাই জিজ্ঞেস করার মতো আর কিছু নেই এমন একটি এক-বাছাই, একটি rubric বা বর্ণিত উত্তরসহ একটি হ্যাঁ/না `'Which of these applies?'` দিয়ে পাঠানো হয়। `instructions` ছাড়া একটি প্রশ্ন গ্রহণ করা সার্ভারের জন্য এটি `False` সেট করুন।

এগুলো `profile=` দিয়ে সেট করুন। যেমন, [Ollama](#ollama) একটি এক-বাছাইয়ে সর্বোচ্চ 26টি বিকল্প আর একটি rubric-এ 26টি স্তর নেয়:

⟦CODE7⟧

Ollama সর্বোচ্চ 64টি প্রশ্ন আর একটি 64 KiB রিকোয়েস্ট নেয়, আর শুধু লোকালে নামানো মডেল দিয়ে উত্তর দেয়; দেখুন [Ollama-র decision ডক](https://docs.ollama.com/capabilities/decision)।

profile জানে না এমন একটি সীমা ছাড়ানো একটি রিকোয়েস্ট API থেকে একটি এরর উত্তর পায়, যা একটি [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] হিসেবে ওঠে, তাই একটি [`FallbackModel`](overview.md#fallback-model) দায়িত্ব নিতে পারে। যেখানে একটি মডেল সীমিত সংখ্যক token পড়ে, তার [`context_window`][pydantic_ai.profiles.ModelProfile.context_window] একইভাবে সেট করুন, আর একটি processor যা [context window ভরে এলে compact করে](../message-history.md#compact-when-the-context-window-fills) ইতিহাস এর নিচে রাখে।

/// note | নিজের ডেটায় মাপুন

প্রতিটি মডেলের আত্মবিশ্বাস তার নিজস্ব, আর একটি মডেলে ঠিক করা একটি threshold আরেকটিতে খাটে না। ভরসা করার আগে নিজের লেবেল করা উদাহরণে
নির্ভুলতা, হস্তান্তরের হার আর যেকোনো threshold মাপুন।

///

/// check | সংক্ষেপে মনে রাখুন

* `SYSTEM_ONE_BASE_URL` (আর দরকারে key) সেট, তারপর `Agent('system-one:<model>')`।
* লোকালে: `ollama pull nimble`, `SYSTEM_ONE_BASE_URL='http://localhost:11434'`।
* মডেলের সীমা `DecisionModelProfile` দিয়ে `profile=`-এ; threshold নিজের ডেটায় মাপুন।

///
