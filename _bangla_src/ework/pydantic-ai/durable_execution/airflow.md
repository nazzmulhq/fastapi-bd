
# Apache Airflow দিয়ে Durable Execution { #durable-execution-with-apache-airflow }

/// note | এই পেজে যা শিখবেন

* Airflow-এ durable একক হলো একটি **Airflow task** — আর কীভাবে step-স্তরের cache একটি retry-কে শেষ সম্পন্ন ধাপ থেকে আবার চালায়।
* `AgentOperator(..., durable=True)` আর `@task.agent` দিয়ে একটি durable এজেন্ট।
* টুল আর side effect, human-in-the-loop, streaming আর সীমাবদ্ধতা।

///

[Apache Airflow](https://airflow.apache.org) একটি workflow orchestrator। এর Pydantic AI ইন্টিগ্রেশন `pydantic_ai.durable_exec` দিয়ে নয়, বরং [`apache-airflow-providers-common-ai`](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/index.html) প্যাকেজের `airflow.providers.common.ai` দিয়ে দেওয়া হয়।

এই পেজের wrapper-অবজেক্ট ইন্টিগ্রেশনের বিপরীতে, Airflow-এর durable একক হলো একটি **Airflow task**। আপনি একটি সাধারণ Pydantic AI এজেন্ট লেখেন আর একে একটি task হিসেবে চালান; Airflow-এর retry ব্যবস্থা আর একটি step-স্তরের cache পুরো রান replay না করে এজেন্টকে এর শেষ সম্পন্ন মডেল রিকোয়েস্ট বা টুল কল থেকে আবার চালায়।

## Durable Execution { #durable-execution }

একটি এজেন্ট durable Airflow task হিসেবে চললে, Airflow প্রতিটি সম্পন্ন **মডেল রিকোয়েস্ট** আর **টুল কল** একটি cache entry হিসেবে লেখে। একটি retry-তে, Airflow সম্পন্ন কাজ বাদ দিতে এই entry-গুলো replay করে: প্রতিটি entry এটি তৈরি করা রিকোয়েস্টের একটি fingerprint রাখে, আর সেই fingerprint আর না মিললে (আগের চেষ্টার পর কথোপকথন ভিন্ন পথে গেছে), step একটি পুরনো ফল ফেরত না দিয়ে লাইভ আবার চলে। Airflow 3.3 আর তার ওপরে (`apache-airflow-providers-common-ai` 0.7.0 বা নতুনতর-সহ) cache হলো Airflow-এর নিজস্ব প্রতি-task-instance task state store, তাই এর কোনো storage কনফিগারেশন লাগে না। task সফল হলে এটি মুছে যায়, আর শেষ পর্যন্ত ব্যর্থ হওয়া একটি রানের রেখে যাওয়া entry DAG run মোছার সময় সরানো হয়। 3.3-এর চেয়ে পুরনো Airflow-এ, বা 0.7.0-এর চেয়ে পুরনো `apache-airflow-providers-common-ai`-এ, cache এর বদলে আপনার কনফিগার করা object storage-এ (local, S3, GCS বা Azure) থাকে।

যেমন, কল্পনা করুন একটি এজেন্ট একটি মডেল ডাকে, একটি কাজের response পায়, একটি টুল কল শুরু করে, আর তারপর worker crash করে। durable execution ছাড়া, Airflow-এর সাধারণ retry task শুরু থেকে আবার চালায় আর মডেল রিকোয়েস্ট ও পরের যেকোনো side effect পুনরাবৃত্তি করে। durable execution-সহ, retry রানটি replay করে, ইতিমধ্যে সম্পন্ন মডেল রিকোয়েস্টের cache করা ফল পুনর্ব্যবহার করে, আর প্রথম অসম্পন্ন কাজ থেকে চলতে থাকে।

এটি কাজের দীর্ঘ-চলা এজেন্টের জন্য আর এমন রানের জন্য যেখানে একটি পুনরাবৃত্ত মডেল রিকোয়েস্ট বা বাইরের টুল কল টাকা খরচ করবে, সময় নেবে বা একটি side effect দ্বিগুণ করবে।

/// tip | উদাহরণ দিয়ে বুঝি

fingerprint হলো রিকোয়েস্টের একটি "আঙুলের ছাপ"। retry-তে Airflow জিজ্ঞেস করে: "এবারের রিকোয়েস্ট কি আগেরবারের সাথে হুবহু মেলে?" মিললে খাতা থেকে পুরনো উত্তর; না মিললে (যেমন মাঝে ইনপুট বদলেছে) নতুন করে মডেলকে জিজ্ঞেস। এতে পুরনো, ভুল ফল ফেরত আসার ঝুঁকি থাকে না।

///

## Durable এজেন্ট { #durable-agent }

আপনি একটি এজেন্টকে durable করেন Airflow-এর `AgentOperator` (বা `@task.agent` decorator) দিয়ে `durable=True` সহ চালিয়ে। Airflow-এর পাশে provider ইনস্টল করুন:

```bash
uv add "apache-airflow-providers-common-ai"
```

এজেন্টের মডেল আর credential আসে একটি Airflow connection থেকে (উদাহরণগুলো `pydanticai_default` ব্যবহার করে)। একটি কীভাবে কনফিগার করবেন তা দেখুন [Pydantic AI connection](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/connections/pydantic_ai.html)-এ।

Airflow 3.3 আর তার ওপরে (`apache-airflow-providers-common-ai` 0.7.0 বা নতুনতর-সহ) durable execution-এ কোনো storage কনফিগারেশন লাগে না। step cache রাখা হয় Airflow-এর task state store-এ, task instance-এর পরিসরে। ডিফল্টভাবে এই entry-গুলো Airflow metadata database-এ রাখা হয়। `[state_store] max_value_storage_bytes`-এর (ডিফল্ট 64 KB) ওপরের মান worker লেখার জন্য প্রত্যাখ্যাত হয় না। এগুলো একটি সতর্কবার্তা log করে আর তবুও রাখা হয়, তাই একটি বড় টুল ফল metadata database-এ গিয়ে পড়তে পারে। বড় payload বাইরের storage-এ সরাতে, `[workers] state_store_backend` সেট করুন।

অন্যথায়, 3.3-এর চেয়ে পুরনো Airflow-এ বা 0.7.0-এর চেয়ে পুরনো `apache-airflow-providers-common-ai`-এ, durable execution-কে এর step cache রাখার একটি জায়গা দিতে হবে। `[common.ai] durable_cache_path`-কে একটি object-storage অবস্থানে নির্দেশ করুন:

⟦CODE1⟧

একটি Airflow task হিসেবে সবচেয়ে ছোট durable Pydantic AI এজেন্ট:

⟦CODE2⟧

`AgentOperator` ভেতরের Pydantic AI এজেন্ট বদলায় না। এটি আপনার connection আর toolset থেকে এজেন্ট তৈরি করে, তারপর মডেল আর toolset মোড়ায়, যাতে task চলার সময় এটি উদ্ধারযোগ্য কাজগুলো লেখে:

* মডেল রিকোয়েস্ট;
* Pydantic AI টুল কল।

`@task.agent` decorator-এও একই প্রযোজ্য, যেখানে decorate করা ফাংশন prompt ফেরত দেয়:

⟦CODE3⟧

এজেন্টের retry হলো Airflow task retry: task-এর `retries` আর `retry_delay` দিয়ে এগুলো কনফিগার করুন। প্রতিটি retry-তে cache করা step replay হয় আর রান প্রথম অসম্পন্ন কাজ থেকে চলতে থাকে। পূর্ণ রেফারেন্সের জন্য, দেখুন Airflow-এর [`AgentOperator` durable execution ডক](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/operators/agent.html#durable-execution)।

/// warning | সাধারণ ভুল

`durable=True` দিয়ে task-এ `retries` সেট না করা। Airflow-এ উদ্ধার ঘটে task retry দিয়েই — `retries=0` (বা না দেওয়া) হলে crash-এর পর কোনো retry হবে না, আর cache কখনো কাজে লাগবে না।

///

## টুল আর side effect { #tools-and-side-effects }

Durable execution প্রতিটি Pydantic AI টুল কলের ফল cache করে, Airflow toolset-চালিত টুলসহ (`SQLToolset`, `HookToolset`, `MCPToolset` আর অন্যান্য)। replay-তে টুল আবার না ডেকে cache করা ফল ফেরত দেওয়া হয়, তাই বাইরের সিস্টেমে লেখা একটি টুল একটি রানের সব retry জুড়ে প্রতি সম্পন্ন step-এ সর্বোচ্চ একবার চলে।

## Human-in-the-loop { #human-in-the-loop }

Airflow-এর `AgentOperator`-এর একটি আলাদা human-in-the-loop পর্যালোচনা মোড আছে (`enable_hitl_review=True`), যা Airflow-এর HITL UI দিয়ে মানুষের অনুমোদন, প্রত্যাখ্যান বা পরিবর্তন-অনুরোধের জন্য একটি এজেন্ট রান থামায়।

/// warning | সতর্কতা

`durable=True` আর `enable_hitl_review=True` এখন একসাথে ব্যবহার করা যায় না। একটি durable রান এর cache থেকে deterministically replay করে আর মানুষের input-এর জন্য থামে না; একটি human-in-the-loop রান interactive আর এখনও step cache-এ ধরা পড়ে না। প্রতি task-এ একটি বাছুন।

///

## Streaming { #streaming }

`durable=True`-এর অধীনে streaming এখনও সমর্থিত নয়। durable মডেল wrapper সম্পূর্ণ মডেল রিকোয়েস্ট লেখে, stream করা event নয়। streaming এজেন্ট non-durable task হিসেবে চালান।

## প্রয়োজনীয়তা আর সীমাবদ্ধতা { #requirements-and-constraints }

একটি Pydantic AI এজেন্টকে durable Airflow task হিসেবে চালানোর সময়:

* durable একক হলো Airflow task; উদ্ধার ঘটে Airflow task retry দিয়ে, তাই task-এ `retries` (আর একটি `retry_delay`) সেট করুন।
* একটি নির্দিষ্ট মডেল দিয়ে এজেন্ট সংজ্ঞায়িত করুন, যেমন `Agent('openai:gpt-6-luna', ...)`-এ মীমাংসা হওয়া একটি connection দিয়ে। `durable=True` হলে মডেল সেট থাকতে হবে।
* Airflow 3.3 আর তার ওপরে `apache-airflow-providers-common-ai` 0.7.0 বা নতুনতর-সহ কোনো cache storage কনফিগারেশন লাগে না, কারণ step cache task state store ব্যবহার করে। অন্যথায় (পুরনো Airflow, বা একটি পুরনো provider), `[common.ai] durable_cache_path` এমন একটি object-storage অবস্থানে সেট করুন যা worker-রা পড়তে আর লিখতে পারে।
* একটি retry-তে, একটি cache করা মডেল রিকোয়েস্ট বা টুল কল replay হয় যখন এর সংরক্ষিত fingerprint বর্তমান রিকোয়েস্টের সাথে মেলে, আর ভিন্ন হলে লাইভ আবার চলে। যে রিকোয়েস্ট একটি fingerprint-এ serialize করা যায় না তা অযাচাইকৃত অবস্থান-ভিত্তিক replay-তে ফিরে যায়, তাই retry জুড়ে রান deterministic রাখুন।
* `durable=True` আর `enable_hitl_review=True` পরস্পর-বর্জিত।
* `durable=True`-এর অধীনে streaming সমর্থিত নয়।
* step cache একটি একক task instance-এর পরিসরে আর task সফল হলে মুছে যায়। Airflow 3.3 আর তার ওপরে এটি task state store-এ থাকে, আর শেষ পর্যন্ত ব্যর্থ হওয়া একটি রানের রেখে যাওয়া entry DAG run মোছার সময় সরানো হয়।

/// check | সংক্ষেপে মনে রাখুন

* Airflow-এ durable একক = একটি task; `AgentOperator(..., durable=True)` বা `@task.agent`।
* প্রতিটি সম্পন্ন মডেল রিকোয়েস্ট আর টুল কল fingerprint-সহ cache হয়; retry-তে মিললে replay।
* Airflow 3.3+ (provider 0.7.0+)-এ storage কনফিগারেশন লাগে না; পুরনোতে `durable_cache_path` দিন।
* উদ্ধারের জন্য task-এ `retries` সেট করুন।
* durable-এ HITL পর্যালোচনা আর streaming চলে না।

///
