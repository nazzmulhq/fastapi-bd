
# Durable Execution { #durable-execution }

/// note | এই পেজে যা শিখবেন

* Durable execution কী, আর কখন দরকার (আর কখন দরকার নেই)।
* Pydantic AI-এর সমর্থিত আটটি engine, প্রতিটির ইনস্টল আর কোন ক্লাস দিয়ে এজেন্টকে durable করবেন।
* একটি এজেন্টে কেন শুধু একটি engine।

///

প্রোডাকশনে durable execution ব্যবহার করুন যখন একটি চলমান রানকে এর process বন্ধ হওয়ার পরও টিকে থাকতে হয় — একটি deploy, একটি crash বা একটি সাময়িক API ব্যর্থতার মধ্য দিয়ে — বা যখন একটি workflow একজন মানুষ বা অন্য সিস্টেমের জন্য কয়েক ঘণ্টা বা দিন অপেক্ষা করে। একটি durable engine এজেন্টের মডেল রিকোয়েস্ট আর এর মোড়ানো টুল কলগুলোর journal রাখে, আর আবার শুরু হওয়া একটি রান শেষ হওয়াগুলো journal থেকে replay করে আর চলমানটি আবার চেষ্টা করে। একটি engine আপনার জন্য কোন টুল কল (ফাংশন টুল, [MCP](../mcp/client.md) সার্ভার) মোড়ায় আর কীভাবে [streaming](../agent.md#streaming-all-events) দেয় তা engine অনুযায়ী ভিন্ন; নিচের প্রতিটি পেজ তা বলে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি ভিডিও গেমের "save point"-এর কথা ভাবুন। একটি এজেন্ট রানে ৫টি ধাপ: মডেল → টুল → মডেল → টুল → মডেল। ধাপ ৪-এর মাঝে সার্ভার crash করল। Durable execution ছাড়া: পুরো রান আবার শুরু থেকে, আগের ৩টি মডেল কলের টাকা আবার। Durable execution-সহ: engine-এর journal-এ লেখা আছে ধাপ ১-৩ শেষ আর তাদের ফল কী — তাই সেগুলো (টাকা ছাড়া) replay হয়, আর শুধু ধাপ ৪ আবার চলে।

///

/// note | Durability মানে storage নয়

একটি durable engine একটি রানকে জীবিত রাখে যখন এটি একটি ধাপের মাঝপথে crash করে, retry আর journal-করা মডেল ও টুল কলসহ। একটি রান সংরক্ষণ, পরে আবার চালানো আর আগের একটি ধাপ থেকে fork করায় কোনো engine লাগে না: Pydantic AI Harness-এর [`StepPersistence`](../harness/step-persistence.md) প্রতিটি স্থির ধাপের snapshot আপনার বাছা একটি store-এ নেয়, একটি checkpointer যেভাবে করে, আর [Persistence](../persistence.md) বিকল্পগুলো দেখায়।

///

Pydantic AI আটটি durable execution engine সমর্থন করে, আর অন্য যেকোনো engine-এর জন্য একটি [builder](./backends.md)। নিচের প্রতিটি পেজে একটি সম্পূর্ণ উদাহরণ আছে:

| Engine | ইনস্টল | এজেন্টকে durable করুন |
|---|---|---|
| [Temporal](./temporal.md) | `pydantic-ai-slim[temporal]` | `pydantic_ai.durable_exec.temporal` থেকে `TemporalDurability` |
| [DBOS](./dbos.md) | `pydantic-ai-slim[dbos]` | `pydantic_ai.durable_exec.dbos` থেকে `DBOSDurability` |
| [Prefect](./prefect.md) | `pydantic-ai-slim[prefect]` | `pydantic_ai.durable_exec.prefect` থেকে `PrefectDurability` |
| [Restate](./restate.md) | `restate_sdk[serde]` | `restate.ext.pydantic` থেকে `RestateAgent` |
| [AWS Lambda](../harness/aws-lambda.md) | `pydantic-ai-harness[aws-lambda]` | `pydantic_ai_harness.aws_lambda` থেকে `AWSLambdaDurability` |
| [Absurd](../harness/absurd.md) | `pydantic-ai-harness[absurd]` | `pydantic_ai_harness.absurd` থেকে `AbsurdDurability` |
| [pgtask](../harness/pgtask.md) | `pydantic-ai-harness[pgtask]` | `pydantic_ai_harness.pgtask` থেকে `PGTaskDurability` |
| [Apache Airflow](./airflow.md) | `apache-airflow-providers-common-ai` | `airflow.providers.common.ai.operators.agent` থেকে `AgentOperator(..., durable=True)` |

Temporal, DBOS, Prefect, Restate আর AWS Lambda Pydantic আর vendor টিম মিলে রক্ষণাবেক্ষণ করে। AWS Lambda, Absurd আর pgtask আসে [Pydantic AI Harness](../harness/index.md)-এ; Restate আর Airflow আসে engine-এর নিজস্ব প্যাকেজে।

/// info | কোনটি বাছবেন?

| আপনার অবস্থা | ভালো পছন্দ |
|-------------|-----------|
| আলাদা কোনো সার্ভার চালাতে চান না, Postgres/SQLite আছে | DBOS, বা শুধু Postgres-এ Absurd / pgtask |
| বড় মাপের, বহু-সার্ভিস workflow, পরিপক্ব টুলিং চান | Temporal |
| আগে থেকেই Prefect বা Airflow দিয়ে pipeline চালান | Prefect / Airflow |
| serverless (AWS) | AWS Lambda |

প্রতিটির বিস্তারিত আর সীমাবদ্ধতা নিজের পেজে দেখুন।

///

/// warning | প্রতি এজেন্টে একটি durable execution engine

প্রতিটি engine মডেল রিকোয়েস্ট আর এর মোড়ানো টুল কলগুলোকে নিজের durable একক হিসেবে journal করে, তাই একটি দ্বিতীয়টি যুক্ত করলে — এজেন্টে, একটি একক রানের জন্য, বা একটি agent spec দিয়ে — কোনোটি যুক্ত হওয়ার আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

///

Capability লেখকরা [durable capability operations](../capabilities/custom.md#durable-capability-operations) দিয়ে নিজস্ব hook-এর কাজ engine-এর activity, step বা task-এ সরাতেও পারেন।

[Append-on-change instructions](../agent.md#appending-instruction-changes) সংরক্ষিত ইতিহাস থেকে তাদের ভিত্তি আর প্রতিস্থাপন তৈরি করে। Instruction callback তবুও engine-এর replay নিয়ম মানে: বাইরের পড়ার জন্য একটি durable operation ব্যবহার করুন, যাতে replay একই মান ব্যবহার করে আর একই রূপের ইতিহাস তৈরি করে।

/// warning | সাধারণ ভুল

একটি instructions ফাংশনে সরাসরি `datetime.now()` বা একটি ডেটাবেস query ব্যবহার করা। replay-এর সময় এটি ভিন্ন মান দেয়, তাই ইতিহাস আগের রানের সাথে মেলে না আর engine বিভ্রান্ত হয়। এমন বাইরের পড়া durable operation-এ রাখুন, যাতে replay-এ সংরক্ষিত মানটিই ফেরত আসে।

///

থার্ড-পার্টি runtime লেখকরা Pydantic AI-এর ভেতরের অংশ import না করে আরেকটি engine যুক্ত করতে স্থিতিশীল [durable execution backend builder](./backends.md) ব্যবহার করতে পারেন।

`Coder`, `Shell` আর `FileSystem`-এর মতো Harness workspace capability-ও একটি durable এজেন্টের ভেতরে চলে; [workspace guide](../workspace.md#durable-execution) দেখায় কীভাবে, আর প্রতিটি engine-এ কী কাজ করে।

/// check | সংক্ষেপে মনে রাখুন

* Durable execution = চলমান রানকে crash/deploy থেকে বাঁচানো; শেষ হওয়া ধাপ journal থেকে replay হয়, টাকা আবার লাগে না।
* রান সংরক্ষণ/fork-এর জন্য engine লাগে না — `StepPersistence` বা `Conversation` সংরক্ষণ।
* আটটি engine: Temporal, DBOS, Prefect, Restate, AWS Lambda, Absurd, pgtask, Airflow; বাকিদের জন্য builder।
* এক এজেন্টে একটির বেশি engine দিলে `UserError`।
* replay-তে একই ফল পেতে বাইরের পড়া durable operation-এ রাখুন।

///
