
# প্রোডাকশনে নেওয়া { #going-to-production }

/// note | এই পেজে যা শিখবেন

* একটি এজেন্ট প্রোডাকশনে পাঠানোর আগে টিমগুলো যে প্রশ্নগুলো করে — আর প্রতিটির ছোট উত্তর ও বিস্তারিত পেজের লিংক।
* একটি চালানো-যায় এমন সম্পূর্ণ সার্ভিস: FastAPI + অনুমোদন-অপেক্ষারত টুল + DBOS durable execution + OpenTelemetry।
* crash, মানুষের অনুমোদন, কথোপকথনের state, খরচের সীমা, provider বিভ্রাট, API key, observability, টেস্ট, নিরাপত্তা, frontend আর deploy।

///

[Pydantic AI](index.md), [Pydantic Evals](evals.md) আর [Pydantic AI Harness](harness/index.md) হলো ওপেন-সোর্স, MIT-লাইসেন্সপ্রাপ্ত Python প্যাকেজ, যা আপনার নিজের process-এ চলে, আর durable execution চলে আপনার পরিচালিত একটি engine-এ (বা সেই engine-এর নিজস্ব cloud-এ): Pydantic-হোস্ট করা কোনো এজেন্ট runtime নেই। দুটি হোস্ট করা Pydantic সার্ভিস আপনি চাইলে কয়েক লাইনে যুক্ত হয়: [Pydantic Logfire](logfire.md), যা প্রতিটি রান, মডেল রিকোয়েস্ট আর টুল কল আপনার অ্যাপ্লিকেশনের বাকি অংশের পাশে একটি trace হিসেবে দেখায়, একটি [ফ্রি টায়ার](https://pydantic.dev/pricing/)-সহ (এর বদলে যেকোনো OpenTelemetry backend কাজ করে); আর [Pydantic AI Gateway](gateway.md), খরচের সীমাসহ provider-জুড়ে মডেলের জন্য একটি key, যার বদলে সরাসরি provider ডাকাও কাজ করে।

/// tip | উদাহরণ দিয়ে বুঝি

Pydantic AI একটি লাইব্রেরি, কোনো হোস্টিং প্ল্যাটফর্ম নয় — ঠিক FastAPI-র মতো। আপনার এজেন্ট আপনার নিজের সার্ভারে, আপনার নিজের কোডের ভেতরে একটি সাধারণ Python অবজেক্ট। তাই "প্রোডাকশনে নেওয়া" মানে নতুন কোনো প্ল্যাটফর্ম শেখা নয়; বরং কয়েকটি প্রশ্নের ভালো উত্তর ঠিক করা: crash হলে কী হবে, খরচ কীভাবে আটকাব, কী ঘটল কীভাবে দেখব।

///

পেজের বাকি অংশ একটি এজেন্ট পাঠানোর আগে টিমগুলো যে প্রশ্ন করে সেগুলোর উত্তর দেয়, প্রতিটি ছোট উত্তর আর বিস্তারিত পেজের লিংকসহ, উত্তরগুলো একসাথে করা [একটি চালানো-যায় সার্ভিসের](#end-to-end) পরে।

| পাঠানোর আগে, আপনি জানতে চান... | ছোট উত্তর | ইনস্টল |
|---|---|---|
| [রানের মাঝে process crash করলে কী হয়?](#crash) | এজেন্টকে একটি [durable execution](durable_execution/overview.md) engine-এ চালান | একটি engine-এর extra-সহ `pydantic-ai-slim`, যেমন `[dbos]` বা `[temporal]` |
| [একজন মানুষ কীভাবে একটি ঝুঁকিপূর্ণ কাজ অনুমোদন করে, আর রান কয়েক দিন পরে আবার চলে?](#approval) | [Deferred টুল](deferred-tools.md) রান শেষ করে; পরের একটি রান তা আবার চালায় | `pydantic-ai` |
| [কথোপকথনের state কীভাবে রাখব?](#state) | রানের `Conversation` আপনার ডেটাবেসে রাখুন | `pydantic-ai` |
| [খরচ আর অনিয়ন্ত্রিত লুপ কীভাবে সীমিত করব?](#cost) | প্রতি রানে `UsageLimits`, প্রতি দিন, tenant বা মাসে `SpendLimits` | `pydantic-ai`, আর `SpendLimits`-এর জন্য `pydantic-ai-harness` |
| [একটি provider বন্ধ থাকলে কী হয়?](#outages) | একটি fallback মডেল, transport retry, বা Gateway failover | `pydantic-ai`, বা হোস্ট করা [Gateway](gateway.md) |
| [API key কোথায় যায়?](#keys) | Environment variable, বা প্রতিটি provider-এর জন্য একটি Gateway key | `pydantic-ai`, বা হোস্ট করা [Gateway](gateway.md) |
| [কী ঘটেছে তা কীভাবে দেখব?](#observability) | প্রতিটি রানের OpenTelemetry trace, [Logfire](logfire.md)-এ বা যেকোনো OTel backend-এ | `pydantic-ai` (`logfire`-সহ) |
| [পরিবর্তন কীভাবে টেস্ট আর মূল্যায়ন করব?](#quality) | `TestModel` দিয়ে unit test, তারপর dataset আর লাইভ ট্রাফিকে eval | `pydantic-ai` (`pydantic-evals`-সহ) |
| [এজেন্ট কী কী ছুঁতে পারবে তা কীভাবে সীমিত করব?](#safety) | প্রতি-কলার টুল, অনুমোদন, আর মডেলের লেখা কোডের জন্য একটি sandbox | `pydantic-ai`, আর sandbox-এর জন্য `pydantic-ai-harness` |
| [একটি frontend-এ কীভাবে পরিবেশন করব?](#frontend) | যেকোনো ASGI অ্যাপ থেকে [AG-UI](ui/ag-ui.md) বা [Vercel AI](ui/vercel-ai.md) stream | `pydantic-ai` |
| [কীভাবে deploy করব?](#deploy) | আপনার নিজের Python process হিসেবে: একটি ওয়েব অ্যাপ, একটি worker বা একটি function | আপনার infrastructure |

## একটি শুরু-থেকে-শেষ সার্ভিস { #end-to-end }

একটি ফাইলে বেশিরভাগ প্রোডাকশন এজেন্টের দরকারি অংশগুলো: একটি HTTP API, একজন মানুষের অনুমোদনের অপেক্ষা করা একটি টুল, [DBOS](durable_execution/dbos.md)-এ durable execution, আর OpenTelemetry trace। এর জন্য একটি মডেল provider-এর API key ছাড়া আর কিছু লাগে না: DBOS এখানে নিজের state একটি SQLite ফাইলে রাখে (প্রোডাকশনে Postgres ব্যবহার করুন), আর trace যায় [Logfire](logfire.md)-এ যখন একটি Logfire token পাওয়া যায় — `LOGFIRE_TOKEN` থেকে বা `logfire auth`-এর লোকালে সংরক্ষিত credential থেকে — অথবা `OTEL_EXPORTER_OTLP_ENDPOINT`-এ নাম দেওয়া যেকোনো OTel collector-এ। ছোট রাখতে, এটি সেগুলো বাদ দেয় যা প্রকাশ্যে আনার আগে আপনি যোগ করবেন: authentication আর কলার রানটির মালিক কিনা তার যাচাই, একই রিকোয়েস্ট বারবার আসা আটকানো (deduplication), আর [usage limit](#cost)।

/// tab | pip

```bash
pip install "pydantic-ai[dbos]" fastapi uvicorn
```

///

/// tab | uv

```bash
uv add "pydantic-ai[dbos]" fastapi uvicorn
```

///


⟦CODE1⟧

এটি চালান `uvicorn production_service:app` দিয়ে, `POST /runs?prompt=...` দিয়ে একটি রান শুরু করুন, `GET /runs/{run_id}` দিয়ে এর অবস্থা আর বাকি থাকা কল পড়ুন, আর `POST /runs/{run_id}/approvals` আর `{"<tool_call_id>": true}`-এর মতো একটি body দিয়ে বাকি থাকা refund অনুমোদন বা প্রত্যাখ্যান করুন। যেকোনো সময় সার্ভার বন্ধ করে আবার চালু করুন: DBOS workflow-টি উদ্ধার করে, ইতিমধ্যে শেষ হওয়া মডেল রিকোয়েস্ট আর `issue_refund` ধাপ নিজের ডেটাবেস থেকে আবার চালায় (replay), আর যদি সেখানেই থাকে তবে অনুমোদনের অপেক্ষায় ফিরে যায়। HTTP রিকোয়েস্টগুলো শুধু workflow শুরু করে, পড়ে আর সংকেত দেয়, তাই রানটি এদের কোনোটি খোলা থাকার ওপর নির্ভর করে না। নিচের অংশগুলো প্রতিটি অংশ আর বিকল্পগুলো ব্যাখ্যা করে।

/// info | এক নজরে: সার্ভিসের প্রবাহ

| ধাপ | HTTP | কী ঘটে |
|-----|------|--------|
| 1 | `POST /runs?prompt=...` | একটি durable workflow শুরু হয়, একটি `run_id` ফেরত আসে |
| 2 | `GET /runs/{run_id}` | রানের অবস্থা আর অনুমোদনের অপেক্ষায় থাকা টুল কল দেখা |
| 3 | `POST /runs/{run_id}/approvals` | মানুষ `true`/`false` দিয়ে সিদ্ধান্ত পাঠায়, workflow আবার এগোয় |
| — | সার্ভার crash | DBOS শেষ হওয়া ধাপ ডেটাবেস থেকে replay করে; মডেলের জন্য আবার টাকা লাগে না |

///

## রানের মাঝে process crash করলে কী হয়? { #crash }

[durable execution](durable_execution/overview.md) ছাড়া, চলমান একটি রান process-এর সাথে মরে যায়: আপনি এটি আবার শুরু করেন, বা শেষ [`StepPersistence`](#checkpointer) snapshot থেকে চালিয়ে যান। এটি থাকলে, একটি engine প্রতিটি মডেল রিকোয়েস্ট আর এর মোড়ানো বা আপনার চিহ্নিত প্রতিটি টুল কলের journal রাখে, আর আবার শুরু হওয়া একটি রান শেষ হওয়া ধাপগুলো journal থেকে replay করে আর যেটি চলছিল সেটি আবার চেষ্টা করে, শেষ হওয়া মডেল রিকোয়েস্টের জন্য আবার টাকা না দিয়ে। একটি engine আপনার জন্য কোন টুল কল মোড়ায় তা ভিন্ন হয় (DBOS ফাংশন টুল আপনার ওপর ছেড়ে দেয়, যেমন [ওপরের সার্ভিসে](#end-to-end))। Pydantic AI আর Harness-এর সাথে আসা engine-গুলো একটি সাধারণ এজেন্টে একটি [capability](capabilities/overview.md) হিসেবে যুক্ত হয় আর কার্যকর হয় যখন রানটি engine-এর workflow বা handler-এর ভেতরে চলে; Restate এর বদলে এজেন্টকে নিজের একটি ক্লাসে মোড়ায়, আর Airflow একটি operator-এ।

process মরার সময় চলমান একটি ধাপ শুরু থেকে আবার চলে, তাই side effect-যুক্ত একটি টুলকে বারবার চালানোর জন্য নিরাপদ করুন, যেমন এটি যে API ডাকে তাতে একটি idempotency key দিয়ে। একটি রান [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior]-এর মতো একটি exception দিয়ে ব্যর্থ হওয়ার আগে মডেল রিকোয়েস্ট, টুল কল আর আউটপুট যাচাই প্রত্যেকে [নিজের স্তরে retry করে](retries.md); দেখুন [Model errors](agent.md#model-errors)।

/// warning | সাধারণ ভুল

একটি "টাকা ফেরত দাও" টুল যা প্রতিবার ডাকলেই নতুন refund তৈরি করে। crash-এর পর ধাপটি আবার চললে গ্রাহক দুবার টাকা পাবেন! সমাধান: `idempotency_key=f"refund-{order_id}"`-এর মতো একটি স্থির key পাঠান, যাতে payment API দ্বিতীয় কলটিকে একই কাজ হিসেবে চিনে উপেক্ষা করে।

///

[ওপরের সার্ভিস](#end-to-end) DBOS ব্যবহার করে কারণ এটি আপনার process-এ Postgres বা SQLite-এর বিপরীতে চলে, পরিচালনার জন্য কোনো সার্ভার ছাড়া; [Temporal](durable_execution/temporal.md) আর [Restate](durable_execution/restate.md) একটি সার্ভার চালায় যেখানে আপনার worker-রা যুক্ত হয়, [Prefect](durable_execution/prefect.md) আর [Airflow](durable_execution/airflow.md) মানানসই যখন আপনি আগে থেকেই এগুলো দিয়ে orchestrate করেন, আর [Absurd](harness/absurd.md) আর [pgtask](harness/pgtask.md) (Harness) শুধু Postgres-এ চলে। [Durable Execution](durable_execution/overview.md) প্রতিটি engine আর প্রতিটি আপনার জন্য কী মোড়ায় তা তালিকা করে; একটি এজেন্ট একবারে একটি engine নেয়।

### একটি checkpointer-এর তুলনায় আপনি কী পান { #checkpointer }

checkpointer-কেন্দ্রিক framework-এ, একটি পদ্ধতি প্রতিটি ধাপের পর state সংরক্ষণ করে আর crash থেকে উদ্ধার, মানুষের জন্য থামা আর একটি thread আবার চালানো — সব সামলায়। Pydantic AI এই কাজগুলো ভাগ করে:

- **একটি রানের ভেতরে crash থেকে উদ্ধার** হলো durable execution, একটি মডেল রিকোয়েস্ট বা journal-করা টুল কলের সূক্ষ্মতায়।
- **মানুষের জন্য থামা**-য় কোনো জীবন্ত process লাগে না: [deferred টুল](#approval) রান শেষ করে আর পরের একটি রান তা তুলে নেয়।
- **রানের মাঝে চালিয়ে যাওয়া** হলো সংরক্ষিত [`Conversation`](#state)। [`StepPersistence`](harness/step-persistence.md) (Harness) প্রতিটি স্থির টুল-কল সীমায় message-history snapshot যোগ করে, যেখান থেকে একটি রান চালিয়ে যাওয়া বা fork করা যায়, আর একটি tool-effect খাতা যা লেখে প্রতিটি টুল কল শুরু হয়েছিল, ফেরত দিয়েছিল নাকি exception তুলেছিল: যে কল কখনো শেষ হয়নি তার ফলাফল অজানা, তাই আবার চালানোর আগে বাইরের সিস্টেম যাচাই করুন। Snapshot শুধু বার্তা রাখে, `Conversation`-এর বহন করা usage আর বাকি থাকা deferred কল নয়, তাই এগুলো এটি সংরক্ষণের পরিপূরক, বিকল্প নয়।

[Persistence](persistence.md) দেখায় কোন অংশ কোন প্রশ্নের উত্তর দেয়।

## একজন মানুষ কীভাবে একটি ঝুঁকিপূর্ণ কাজ অনুমোদন করে, আর রান কয়েক দিন পরে আবার চলে? { #approval }

[টুলটিকে অনুমোদন-প্রয়োজনীয় হিসেবে চিহ্নিত করুন](deferred-tools.md#human-in-the-loop-tool-approval)। মডেল এটি ডাকলে, রান শেষ হয় বাকি থাকা কলগুলোর তালিকাসহ একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট দিয়ে, আর অপেক্ষার সময় মেমরিতে কিছুই থাকে না। রানের [`Conversation`][pydantic_ai.conversation.Conversation] সংরক্ষণ করুন, যা বাকি থাকা কলগুলো [`deferred_tool_requests`][pydantic_ai.conversation.Conversation.deferred_tool_requests] হিসেবে রাখে, একজন মানুষকে জিজ্ঞেস করুন, আর তিনি উত্তর দিলে, কয়েক মিনিট বা সপ্তাহ পরে, তাঁর সিদ্ধান্তসহ কথোপকথন চালিয়ে যান:

⟦CODE2⟧

প্রতিটি continuation-এর পর ফেরত আসা conversation সংরক্ষণ করুন: মডেল আরেকটি অনুমোদন চাইতে পারে, আর conversation-ই তার উত্তর দেয়।

একই পদ্ধতি একটি কল [একটি frontend বা একটি background worker-কে](deferred-tools.md#external-tool-execution) চালাতে দেয়, আর একটি অনুমোদন সম্পাদিত আর্গুমেন্ট বা মডেলের দেখা একটি প্রত্যাখ্যান-বার্তাসহ ফিরতে পারে। [UI adapter](ui/overview.md) আর [CLI](cli.md) অনুমোদন বহন করে; একটি durable engine-এর অধীনে workflow নিজেই সিদ্ধান্তের অপেক্ষা করতে পারে, যেমন [ওপরের সার্ভিসে](#end-to-end) `support_run` করে; আর অনুমোদনকারী একই process-এ থাকলে, একটি [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] handler রান শেষ না করে কলগুলো সাথে সাথে মীমাংসা করে। সব কিছু আছে [Deferred Tools](deferred-tools.md)-এ।

কেউ নজর রাখছে না এমন একটি এজেন্টের জন্য, [`ToolCallJudge`](harness/tool-call-judge.md) (Harness) একটি দ্বিতীয় মডেলকে জিজ্ঞেস করে একটি কল চলতে পারে কিনা, আর যে কল নিয়ে এটি নিশ্চিত নয় সেগুলো একজন মানুষের কাছে পাঠায়; [`ApprovalReviewer`](harness/approval-reviewer.md) (Harness) একটি দ্বিতীয় মডেলকে কম-ঝুঁকির কল অনুমোদন করতে দেয় আর বাকিগুলো মানুষের জন্য রাখে।

/// warning | অনুমোদন মডেলের বিরুদ্ধে সুরক্ষা দেয়, client-এর বিরুদ্ধে নয়

একটি client-এর পাঠানো অনুমোদন যেমন দেওয়া তেমনই বিশ্বাস করা হয়। endpoint-এ authentication দিন, আর সংবেদনশীল কাজের জন্য টুলের ভেতরে authorization যাচাই করুন; দেখুন [client-supplied history-র trust boundary](message-history.md#trust-boundary-for-client-supplied-history)।

///

## কথোপকথনের state কীভাবে রাখব? { #state }

একটি কথোপকথনের state হলো এর [`Conversation`][pydantic_ai.conversation.Conversation]: [বার্তাগুলো](message-history.md), চলমান usage যা [`UsageLimits`](#cost) টার্ন আর অনুমোদন জুড়ে গুনতে থাকে, [এর রানগুলোকে মেলানো](message-history.md#correlating-runs-with-run_id-and-conversation_id) `conversation_id`, আর যেকোনো বাকি থাকা deferred কল। [`result.conversation`][pydantic_ai.agent.AgentRunResult.conversation] আপনার নিজের ডেটাবেসে রাখুন, [`ConversationTypeAdapter`][pydantic_ai.conversation.ConversationTypeAdapter] দিয়ে serialize করে আর এর `conversation_id`-কে key করে (একটি `jsonb` কলামই যথেষ্ট), আর পরের রানে এটি `conversation=` হিসেবে ফেরত দিন।

একটি conversation ID একটি key, credential নয়: লোড করার আগে যাচাই করুন কলার কথোপকথনটিতে প্রবেশ করতে পারে কিনা, আর একটি কথোপকথনের একসাথে আসা আপডেটগুলো ক্রমানুসারে করুন, যেমন একটি version কলাম বা প্রতি-কথোপকথন lock দিয়ে, যাতে দুটি instance একই সংরক্ষিত version চালিয়ে না যায়। [Persistence](persistence.md) একটি append-only রূপ, [`StepPersistence`](#checkpointer), আর কথোপকথন জুড়ে একজন ব্যবহারকারী সম্পর্কে এজেন্টের যা মনে রাখা উচিত তার জন্য [`Memory`](harness/memory.md) (Harness) নিয়ে আলোচনা করে; [compaction](capabilities/compaction.md) একটি দীর্ঘ কথোপকথনকে context window-এর ভেতরে রাখে।

/// warning | সাধারণ ভুল

URL থেকে আসা `conversation_id` দিয়ে সরাসরি ডেটাবেস থেকে কথোপকথন লোড করা। ID অনুমান বা ফাঁস হলে একজন ব্যবহারকারী আরেকজনের পুরো চ্যাট পড়তে পারবে। সবসময় `WHERE conversation_id = ? AND user_id = ?`-এর মতো মালিকানা যাচাই করুন।

///

## খরচ আর অনিয়ন্ত্রিত লুপ কীভাবে সীমিত করব? { #cost }

[`UsageLimits`][pydantic_ai.usage.UsageLimits] একটি রানের agent-loop রিকোয়েস্ট, সফল টুল কল, token আর USD-তে খরচ সীমিত করে, আর একটি সীমা ছুঁলে [`UsageLimitExceeded`][pydantic_ai.exceptions.UsageLimitExceeded] তোলে। `request_limit` agent loop-এর টার্ন গোনে, provider-এ পাঠানো প্রতিটি চেষ্টা নয়, আর token আর খরচ একটি response আসার পরে যাচাই হয়, তাই যে রিকোয়েস্ট একটি সীমা পেরোয় তার দাম ইতিমধ্যে দেওয়া হয়ে গেছে:

⟦CODE3⟧

খরচ হিসাব সর্বোত্তম-চেষ্টা মাত্র: যে মডেলের দামের তথ্য [genai-prices](https://github.com/pydantic/genai-prices)-এ নেই তা গোনা হয় না, তাই `cost_limit`-এর পাশাপাশি `request_limit` রাখুন আর [মডেলের দাম হালনাগাদ](agent.md#keeping-model-prices-up-to-date) রাখুন; দেখুন [usage limits](agent.md#usage-limits)।

/// tip | উদাহরণ দিয়ে বুঝি

`UsageLimits` হলো একটি ট্যাক্সির মিটারে "সর্বোচ্চ ৫০০ টাকা" লিখে রাখার মতো — একটি **একক যাত্রার** সীমা। কিন্তু আপনার পুরো মাসের ট্যাক্সি বাজেট ১০,০০০ টাকা হলে, তার জন্য দরকার `SpendLimits` — যা অনেক যাত্রা জুড়ে মোট হিসাব রাখে। আর মিটার শুধু যাত্রা শেষে দেখে, তাই শেষ যাত্রাটা একটু বেশি হয়ে যেতে পারে।

///

একটি রানের চেয়ে দীর্ঘ বাজেটের জন্য, যেমন একটি দৈনিক, মাসিক বা প্রতি-tenant সীমা, [`SpendLimits`](harness/spend.md) (Harness) একটি বাজেট শেষ হলে পরের রিকোয়েস্ট প্রত্যাখ্যান করে। এটি একটি ব্রেক, সংরক্ষণ নয়: যে রিকোয়েস্ট সীমা পেরোয় তা শেষ হয় আর একসাথে চলা রানগুলো প্রত্যেকে যাচাই পেরিয়ে যেতে পারে, তাই খরচ সীমা ছাড়াতে পারে; worker process বা restart জুড়ে বিস্তৃত বাজেটের জন্য ডিফল্ট in-memory store-এর বদলে একটি ভাগ করা store লাগে; আর দাম-না-জানা একটি response বিনামূল্যে গোনা হয় যদি না আপনি `on_unpriced='raise'` সেট করেন। [Gateway](gateway.md#key-features) একটি রিকোয়েস্ট provider-এ পৌঁছানোর আগে প্রতি project, ব্যবহারকারী আর API key-তে দৈনিক, সাপ্তাহিক আর মাসিক খরচের সীমা প্রয়োগ করে।

[Timeouts](timeouts.md) [প্রতিটি মডেল রিকোয়েস্ট, টুল কল আর hook](timeouts.md#bounding-how-long-a-step-takes) আর [একটি পুরো রান](timeouts.md#bounding-a-whole-run) সীমিত করে (ওপরের `tool_timeout=30` একটি উদাহরণ), [বাতিল করা](agent.md#cancelling-a-run) একটি stop বাটন বা একটি timer থেকে রান থামায়, [`max_concurrency`](agent.md#concurrency-limiting) একটি এজেন্ট একসাথে কতগুলো রান চালায় তা সীমিত করে, আর [`ConcurrencyLimitedModel`][pydantic_ai.ConcurrencyLimitedModel] একটি process-এর ভেতরে [একটি মডেলে একসাথে রিকোয়েস্ট](models/overview.md#http-request-concurrency) সীমিত করে (এটি concurrency, প্রতি মিনিটে রিকোয়েস্ট নয়, তাই provider-এর rate-limit response তবুও সামলান)।

[`Caching`][pydantic_ai.capabilities.Caching] capability [prompt caching](capabilities/caching.md) চালু করে, যাতে একটি বহু-টার্ন রান প্রতিটি রিকোয়েস্টে এর instructions, টুল আর ইতিহাসের জন্য পুরো দাম দেওয়া বন্ধ করে; প্রতিটি request span-এ [prompt-cache health](logfire.md#prompt-cache-health) দেখায় কখন একটি পরিবর্তন cache ভেঙে দেয়, আর [token আর খরচের metric](logfire.md#emitted-metrics) provider আর মডেল অনুযায়ী খরচ ভাগ করে দেখায়।

## একটি provider বন্ধ থাকলে কী হয়? { #outages }

[`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] পরের মডেলটি চেষ্টা করে যখন একটি রিকোয়েস্ট একটি API error-এ ব্যর্থ হয়, বা যখন একটি non-streamed response আপনার সংজ্ঞায়িত একটি যাচাইয়ে ব্যর্থ হয় (streamed response, যেমন একটি [frontend](#frontend) পায়, যেমন আছে তেমনই গ্রহণ করা হয়); দেখুন [Fallback Model](models/overview.md#fallback-model):

⟦CODE4⟧

[Provider SDK client](retries.md#provider-sdk-retries) আগে থেকেই কিছু ব্যর্থতায় নিজেরা retry করে। rate limit আর 5xx response-এর জন্য `Retry-After` মেনে backoff-সহ retry চাইলে, HTTP client-এ একটি [retrying transport](retries.md#transport-retries) বসান; ডিফল্টভাবে ওই স্তরে কিছুই retry করে না। [Retries](retries.md) ব্যাখ্যা করে স্তরগুলো কীভাবে গুণিত হয়। [Gateway](gateway.md) নিজের দিকে একই মডেল পরিবেশন করা provider-দের মধ্যে failover আর load balancing করতে পারে, [gateway endpoints](gateway.md#gateway-endpoints) হিসেবে কনফিগার করা।

## API key কোথায় যায়? { #keys }

প্রতিটি provider নিজের key একটি environment variable থেকে পড়ে, যেমন `OPENAI_API_KEY` বা `ANTHROPIC_API_KEY` (প্রতিটি [model page](models/overview.md) নিজেরটির নাম বলে), বা এর provider ক্লাসে `api_key=` নেয়, তাই আপনি অন্য যেকোনো credential-এর মতো আপনার secret manager থেকে key লোড করেন। [Gateway](gateway.md) দিয়ে, অ্যাপ্লিকেশন প্রতিটি provider-এর জন্য একটি `PYDANTIC_AI_GATEWAY_API_KEY` রাখে, আর প্রতিটি Gateway key নিজের খরচের সীমা বহন করতে পারে, তাই আপনি প্রতি সার্ভিস বা environment-এ একটি দিতে পারেন; দেখুন [Gateway quick start](gateway.md#quick-start)।

/// warning | সাধারণ ভুল

API key সরাসরি কোডে `api_key='sk-...'` লিখে git-এ commit করা। একবার push হলে key ফাঁস ধরে নিন। key সবসময় environment variable বা secret manager থেকে নিন।

///

## কী ঘটেছে তা কীভাবে দেখব? { #observability }

Pydantic AI প্রতিটি রানের OpenTelemetry trace তৈরি করে: প্রতিটি মডেল রিকোয়েস্ট এর token আর খরচসহ, প্রতিটি টুল কল এর আর্গুমেন্ট আর ফলসহ, আর এদের ঘিরে রানটি। এগুলো [Logfire](logfire.md)-এ বা [যেকোনো OpenTelemetry backend](logfire.md#otel-without-logfire)-এ পাঠান:

⟦CODE5⟧

Logfire-এ, সেখানে পৌঁছাতে আপনার মেশিনে `logfire auth` আর `logfire projects new` (বা বিদ্যমান project-এর জন্য `logfire projects use`) আর প্রোডাকশনে একটি write token লাগে; একটি coding agent [pydantic.dev/ai-setup.md](https://pydantic.dev/ai-setup.md) থেকে আপনার জন্য এটি করে দিতে পারে, আর ফ্রি টায়ার শুরু করার জন্য যথেষ্ট। একই SDK [FastAPI](https://logfire.pydantic.dev/docs/integrations/web-frameworks/fastapi/) আর [provider-এ HTTP রিকোয়েস্ট](logfire.md#monitoring-http-requests) instrument করে, তাই একটি রান যে রিকোয়েস্ট এটি শুরু করেছে তার ভেতরে দেখা যায়, এর পাঠানো কাঁচা prompt-সহ। [Using Logfire](logfire.md#using-logfire) ধাপে ধাপে দেখায়।

Logfire SDK ছাড়া, [`Agent.instrument_all()`][pydantic_ai.agent.Agent.instrument_all] বা [`Instrumentation`](capabilities/instrumentation.md) capability আপনার নিজের tracer provider-এর বিপরীতে একই কাজ করে; দেখুন [OTel without Logfire](logfire.md#otel-without-logfire)। প্রতিটি রান এর [`run_id` আর `conversation_id`](message-history.md#correlating-runs-with-run_id-and-conversation_id) বহন করে, আর একটি tenant বা user ID-র মতো [run metadata](agent.md#run-metadata) run span-এ পড়ে, তাই আপনি এটি দিয়ে trace ছাঁকতে পারেন।

Telemetry ডিফল্টভাবে prompt, completion আর টুলের আর্গুমেন্ট অন্তর্ভুক্ত করে। এগুলো Pydantic AI-এর span থেকে বাদ রাখতে, [`InstrumentationSettings`][pydantic_ai.models.instrumented.InstrumentationSettings]-এ [`include_content=False`](logfire.md#excluding-prompts-and-completions) সেট করুন, আর [`include_binary_content=False`](logfire.md#excluding-binary-content) ছবি, অডিও আর ডকুমেন্টের bytes বাদ দেয়। কোনোটিই run metadata, আপনার নিজের span বা ধরা HTTP request body ছোঁয় না, তাই সেগুলো আলাদাভাবে কনফিগার করুন।

## পরিবর্তন কীভাবে টেস্ট আর মূল্যায়ন করব? { #quality }

**Unit test** মডেলটি বদলে দেয় [`TestModel`][pydantic_ai.models.test.TestModel] দিয়ে, যা আপনার টুল ডাকে আর আপনার আউটপুট টাইপের সাথে মেলে এমন ডেটা ফেরত দেয়, বা [`FunctionModel`][pydantic_ai.models.function.FunctionModel] দিয়ে, যা আপনার লেখা একটি ফাংশন দিয়ে উত্তর দেয়। [`Agent.override`][pydantic_ai.agent.Agent.override] আপনার অ্যাপ্লিকেশন কোড না ছুঁয়ে এটি বসায়, আর [`ALLOW_MODEL_REQUESTS = False`][pydantic_ai.models.ALLOW_MODEL_REQUESTS] যেকোনো আসল মডেল রিকোয়েস্টে টেস্টটি ব্যর্থ করায়:

⟦CODE6⟧

[Testing](testing.md) [pytest fixtures](testing.md#overriding-model-via-pytest-fixtures), একটি রানের আদান-প্রদান করা বার্তার ওপর assert করা, আর [`FunctionModel`](testing.md#unit-testing-with-functionmodel) নিয়ে আলোচনা করে।

**Evals** তা যাচাই করে যা unit test পারে না: মডেলের উত্তরগুলো ভালো কিনা। [Pydantic Evals](evals.md) আপনার এজেন্টকে কোডে থাকা কেসের একটি dataset-এর বিপরীতে চালায় আর ফলাফলগুলো আপনার নিজের evaluator, বিল্ট-ইন যাচাই বা একটি [LLM judge](evals/evaluators/llm-judge.md) দিয়ে নম্বর দেয়, আর [trajectory evaluator](evals/evaluators/agentic.md) এজেন্টের টুল কলগুলোকে মূল্যায়ন করে, শুধু এর চূড়ান্ত উত্তর নয়।

**একটি prompt বা মডেল পরিবর্তন চালু করতে**, একই dataset এর বিপরীতে চালান আর রিপোর্টগুলো তুলনা করুন; [experiment Logfire-এ পাঠানো](evals/how-to/logfire-integration.md) প্রতিটি রানকে প্রতিটি কেসের trace-এর পাশাপাশি রাখে। [`ManagedPrompt`](harness/managed-prompt.md) (Harness) instructions-কে একটি Logfire-পরিচালিত prompt দিয়ে চালায়, যা আপনি Logfire UI থেকে redeploy ছাড়াই version, label আর চালু করেন, আর একটি [agent spec](agent-spec.md) মডেল, instructions আর capability কোডের বদলে একটি YAML বা JSON ফাইলে রাখে।

**[Online evaluation](evals/online-evaluation.md)** একই evaluator প্রোডাকশন ট্রাফিকে যুক্ত করে, background-এ নম্বর দিয়ে আর ফলগুলো OpenTelemetry event হিসেবে তৈরি করে। ওই background কাজ আপনার process-এ থাকে, একটি job queue-তে নয়: একটি LLM judge-এর মতো দামি evaluator-এর [নমুনা নিন](evals/online-evaluation.md#sampling) আর [concurrency সীমিত করুন](evals/online-evaluation.md#concurrency-control), আর বন্ধ হওয়ার সময় [`wait_for_evaluations()`][pydantic_evals.online.wait_for_evaluations] await করুন যাতে বাকিগুলো শেষ হয়। একটি দীর্ঘ রান চলার সময় তাকে পথ দেখাতে, [`TrajectoryJudge`](harness/trajectory-judge.md) (Harness) প্রতি কয়েকটি মডেল রিকোয়েস্টে এটি পর্যালোচনা করে।

## এজেন্ট কী কী ছুঁতে পারবে তা কীভাবে সীমিত করব? { #safety }

- **টুল আর কথোপকথনে প্রবেশ অনুমোদন করুন**: এজেন্টকে শুধু সেই টুলগুলো দিন যা বর্তমান কলার ব্যবহার করতে পারে, [প্রতি রানে toolset তৈরি করে](toolsets.md#dynamically-building-a-toolset) বা আপনার [dependencies](dependencies.md)-এ থাকা ব্যবহারকারীর বিপরীতে [এটি ছেঁকে](toolsets.md#filtering-tools); যাচাই করুন কলার যে [কথোপকথন](#state) চালিয়ে যাচ্ছে তাতে প্রবেশ করতে পারে কিনা; আর একটি client-এর পাঠানো ইতিহাসকে [অবিশ্বস্ত input](message-history.md#loading-untrusted-history) হিসেবে ধরুন।
- **সংবেদনশীল কাজে অনুমোদন বাধ্যতামূলক করুন**: [deferred টুল](#approval) কলের সামনে একজন মানুষ, বা [`ToolCallJudge`](harness/tool-call-judge.md)-সহ একটি দ্বিতীয় মডেল বসায়।
- **মডেলের লেখা কোড আলাদা রাখুন**: shell কমান্ড আর তৈরি কোড একটি [sandbox](harness/index.md#execution-environments)-এ চালান, যেমন লোকালে [bubblewrap](harness/bubblewrap-sandbox.md) বা দূরে [E2B](harness/e2b-sandbox.md) বা [Modal](harness/modal-sandbox.md)। [`FileSystem`](harness/filesystem.md) path pattern মডেলের ফাইল টুল কী লেখে তা পাহারা দেয়, কিন্তু এগুলো যাচাই, বিচ্ছিন্নতা নয়, আর shell কমান্ড সীমিত করে না।

[Pydantic AI Harness](harness/index.md#capabilities) আরও যোগ করে, যেমন secret আর PII detector-সহ [guardrails](harness/guardrails.md) আর টুলের ফলের জন্য একটি [prompt injection defender](harness/prompt-injection-defender.md)।

## একটি frontend-এ কীভাবে পরিবেশন করব? { #frontend }

একটি [UI adapter](ui/overview.md) আপনার frontend-এর একটি রিকোয়েস্টকে একটি এজেন্ট রানে বদলায় আর এর লেখা, thinking আর টুল কল [AG-UI](ui/ag-ui.md) বা [Vercel AI](ui/vercel-ai.md) protocol-এ ফেরত stream করে, FastAPI বা যেকোনো Starlette অ্যাপ থেকে:

⟦CODE7⟧

[deferred টুলের](#approval) অনুমোদন একই stream-এ যাতায়াত করে। adapter endpoint কোনো authentication সীমা নয়: এটি আপনার নিজের authenticated route-এর ভেতরে চালান, যেমন [client-submitted message-এর trust model](ui/overview.md#trust-model-for-client-submitted-messages) ব্যাখ্যা করে। একটি durable রান বা একটি background job-এর জন্য, endpoint রানটি অন্য কোথাও শুরু করে আর [এর event ফেরত stream করে](ui/overview.md#running-the-agent-elsewhere)। [Interfaces](interfaces.md) একটি এজেন্ট পরিবেশনের অন্য সব উপায় তালিকা করে; বিল্ট-ইন [web chat UI](web.md) লোকাল ডেভেলপমেন্টের জন্য, প্রোডাকশনের জন্য নয়।

## কীভাবে deploy করব? { #deploy }

একটি এজেন্ট আপনার process-এর একটি Python অবজেক্ট, তাই আপনি এটি সেভাবেই deploy করেন যেভাবে আপনার বাকি Python deploy করেন: হোস্ট করার মতো Pydantic-নির্দিষ্ট কিছু নেই। সাধারণ রূপ:

- **একটি ওয়েব সার্ভিস**: এজেন্টকে আপনার FastAPI, Starlette, Django বা Flask handler-এর ভেতরে চালান, যেমন [ওপরে](#frontend), আর অন্য যেকোনো ওয়েব অ্যাপের মতো scale করুন। একটি কথোপকথনের state থাকে আপনি যা [সংরক্ষণ করেন](#state) তাতে বা durable engine-এ, process-এ নয়, তাই যেকোনো instance যেকোনো কথোপকথন চালিয়ে যেতে পারে।
- **একটি worker**: একটি queue বা schedule থেকে রান শুরু করুন, [Temporal](durable_execution/temporal.md), [DBOS queues](durable_execution/dbos.md#durable-execution) বা [Prefect deployments](durable_execution/prefect.md#deployments-and-scheduling)-এর মতো একটি durable engine-এর worker-এ, বা [Render Workflows](harness/render-workflows.md) (Harness)-এ, যা মডেল রিকোয়েস্ট আর সমর্থিত টুল কল আলাদা task হিসেবে চালায়।
- **একটি serverless function**: [AWS Lambda durable functions](harness/aws-lambda.md)-এ চালান যাতে timeout হওয়া বা retry করা একটি invocation শুরু থেকে না চলে আবার এগোয়।
- **একটি voice agent**: দেখুন [realtime deployment](realtime/deployment.md)।
- **একটি repository-তে একটি এজেন্ট**: [GitHub Agentic Workflows](harness/gh-aw.md) issue, pull request বা একটি schedule-এ একটি এজেন্ট চালায়।

একটি দীর্ঘ-চলা সার্ভারে, রানগুলো async আর একটি event loop ভাগ করে: [`max_concurrency`](agent.md#concurrency-limiting) একসাথে কতগুলো চলবে তা সীমিত করে (backpressure-এর জন্য একটি queue সীমাসহ), [`UseThreadExecutor`](capabilities/thread-executor.md) sync টুলকে একটি সীমিত thread pool দেয়, আর একটি ধীর টুল একটি [background tool](harness/background-tools.md) (Harness) হিসেবে চলতে পারে যখন এজেন্ট কাজ চালিয়ে যায়।

আপনার version pin করুন: Pydantic AI এর [version policy](version-policy.md) মেনে চলে, আর Pydantic AI Harness [0.x release](harness/index.md#version-policy)-এ আছে, যার API minor version-এর মধ্যে বদলাতে পারে। একটি durable engine-এ, একটি deploy চলমান রানগুলো কীসের বিপরীতে replay করে তাও বদলায়: একটি টুল যোগ করা বা engine-এর সংরক্ষিত একটি টাইপ বদলানো পুরনো কোডে শুরু হওয়া একটি রান ভেঙে দিতে পারে, তাই ওই রানগুলোকে পুরনো version-এ শেষ হতে দিন বা engine-এর versioning নির্দেশনা মেনে চলুন, যেমন [Temporal-এর](durable_execution/temporal.md#agent-run-context-and-dependencies) বা [AWS Lambda-র](harness/aws-lambda.md#constraints)।

/// check | সংক্ষেপে মনে রাখুন

* Pydantic AI আপনার নিজের process-এ চলে; Logfire আর Gateway ঐচ্ছিক হোস্ট করা সার্ভিস।
* crash থেকে বাঁচতে durable execution (DBOS, Temporal...); side-effect টুলে idempotency key দিন।
* মানুষের অনুমোদন: deferred টুল রান শেষ করে, `Conversation` সংরক্ষণ করুন, পরে সিদ্ধান্তসহ চালিয়ে যান।
* খরচ: প্রতি রানে `UsageLimits` (`request_limit` + `cost_limit`), দীর্ঘ সময়ে `SpendLimits` বা Gateway।
* বিভ্রাট: `FallbackModel` আর retrying transport; key environment variable-এ।
* trace: Logfire বা যেকোনো OTel; সংবেদনশীল ডেটা বাদ দিতে `include_content=False`।
* টেস্টে `TestModel` + `ALLOW_MODEL_REQUESTS = False`; মানের জন্য evals।
* নিরাপত্তা: প্রতি-কলার টুল, মালিকানা যাচাই, model-written কোডের জন্য sandbox।

///
