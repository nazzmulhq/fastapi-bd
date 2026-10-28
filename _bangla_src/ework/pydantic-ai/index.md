# Pydantic AI { #pydantic-ai }

⟦CODE1⟧

⟦CODE2⟧

/// note | এই পেজে যা শিখবেন

* Pydantic AI কী, আর এটি দিয়ে কী কী বানানো যায় (কোডিং এজেন্ট, ডেটা বের করা, টেকসই ওয়ার্কফ্লো, ভয়েস, ছবি তৈরি)।
* কেন Pydantic AI: যেকোনো মডেল, শুরু থেকে শেষ পর্যন্ত টাইপ, পরিমাপ, ক্যাপাবিলিটি, সব ইন্টারফেস।
* একটি পূর্ণ উদাহরণ: ব্যাংকের গ্রাহকসেবা এজেন্ট, প্রতিটি লাইনের ব্যাখ্যাসহ।
* Logfire দিয়ে এজেন্ট কী করছে তা দেখা, আর এরপর কোথায় যাবেন।

///

/// tip | উদাহরণ দিয়ে বুঝি

LLM (যেমন ChatGPT বা Claude) হলো একজন খুব জ্ঞানী কিন্তু হাত-পা বাঁধা পরামর্শদাতা: কথা বলতে পারে, কিন্তু নিজে ডেটাবেস দেখতে বা ইমেইল পাঠাতে পারে না। **এজেন্ট** হলো সেই পরামর্শদাতাকে কিছু যন্ত্রপাতি (টুল) দেওয়া আর একটি নিয়ম বেঁধে দেওয়া: "উত্তর এই ছকেই দেবে"। Pydantic AI সেই এজেন্ট বানানোর Python লাইব্রেরি, আর FastAPI যেমন Pydantic দিয়ে ইনপুট যাচাই করে, Pydantic AI-ও তেমনি LLM-এর উত্তর Pydantic দিয়ে যাচাই করে।

///

**Pydantic AI** হলো Python-এর AI SDK: একটি টাইপসহ, [বাড়ানো যায় এমন](extensibility.md) এজেন্ট লুপ, যেখানে [যেকোনো মডেল](models/overview.md) শুধু একটি স্ট্রিং বদলালেই বদলে যায়। একই এজেন্ট [যেখানে দরকার সেখানেই চলে](interfaces.md): একটি [ওয়েব ফ্রন্টএন্ডের](ui/overview.md) পেছনে, [টার্মিনালে](cli.md), [ভয়েস কলে](realtime/overview.md), একটি [টেকসই ব্যাকগ্রাউন্ড কিউতে](durable_execution/overview.md), [GitHub Actions-এ](harness/gh-aw.md), অথবা একটি সাধারণ অবজেক্ট হিসেবে, যার ওপর আপনি [`run()`](agent.md#running-agents) ডাকেন। [ছবি তৈরি](image-generation.md) আর [embedding](embeddings.md)-ও একই বাক্সে আসে।

**[Pydantic AI Harness](harness/index.md)**-এ আছে জটিল, দীর্ঘ কাজের জন্য একটি এজেন্টের যা যা দরকার, [ক্যাপাবিলিটি](capabilities/overview.md) হিসেবে লাগিয়ে নেওয়া যায়: [স্মৃতি](harness/memory.md), [গার্ডরেইল](harness/guardrails.md) আর [সাব-এজেন্ট](harness/subagents.md) থেকে শুরু করে [পরিকল্পনা](harness/planning.md), [কনটেক্সট ব্যবস্থাপনা](harness/compaction.md) আর [সংরক্ষণ (persistence)](persistence.md), এমনকি একটি সম্পূর্ণ [কোডিং এজেন্ট](harness/coder.md) পর্যন্ত।

[Pydantic Evals](evals.md) একটি এজেন্টের চূড়ান্ত আউটপুট আর [টুল-কলের ধারাবাহিকতা (trajectory)](evals/evaluators/agentic.md) মূল্যায়ন করে, ডেটাসেটের ওপর বা [প্রোডাকশনের আসল ট্রাফিকে](evals/online-evaluation.md); আর একটি এজেন্ট লুপ যথেষ্ট না হলে [Pydantic Graph](graph.md) দেয় টাইপসহ নিয়ন্ত্রণ-প্রবাহ। দুটোই আলাদা open-source প্যাকেজ, তেমনি [genai-prices](https://github.com/pydantic/genai-prices), যা মডেলের দাম হালনাগাদ রাখে, আর [Monty](https://github.com/pydantic/monty), মডেলের লেখা কোড চালানোর নিরাপদ (sandboxed) Python interpreter।

[Pydantic Logfire](https://pydantic.dev/logfire) হলো AI ইঞ্জিনিয়ারিং প্ল্যাটফর্ম, যা শুধু LLM কল নয়, আপনার পুরো অ্যাপ দেখে; আর [Pydantic AI Gateway](gateway.md) হলো সব মডেলের জন্য একটি চাবি (key), সাথে তাৎক্ষণিক খরচ পর্যবেক্ষণ আর বাজেট নিয়ন্ত্রণ। আমাদের [instrumentation](logfire.md) সাধারণ OpenTelemetry, তাই আপনার আগে থেকে চালানো যেকোনো backend কাজ করে।

## আপনি কী বানাচ্ছেন? { #what-are-you-building }

সাধারণ টাইপসহ ডেটা বের করা থেকে শুরু করে জটিল, দীর্ঘ সময় ধরে চলা বহু-এজেন্টের সহযোগিতা পর্যন্ত, Pydantic AI আর [Pydantic AI Harness](harness/index.md) সব সামলায়।

//// tab | কোডিং এজেন্ট

আপনার টার্মিনালে একটি সম্পূর্ণ কোডিং এজেন্ট: workspace-এর ভেতরে সীমিত [ফাইল অ্যাক্সেস](harness/filesystem.md), অনুমোদিত কমান্ডের [shell](harness/shell.md), [রিপোর ধারণা (repo orientation)](harness/repo-context.md), [পরিকল্পনা](harness/planning.md), আর দীর্ঘ সেশনেও টিকে থাকা [কনটেক্সট ব্যবস্থাপনা](harness/compaction.md)। এখানে সাথে লাগানো হয়েছে [ওয়েব সার্চ](capabilities/web-search.md) আর দ্বিতীয় মতামত দেওয়া একজন [উপদেষ্টা (advisor)](harness/advisor.md):

/// tab | pip

```bash
pip install pydantic-ai pydantic-ai-harness
```

///

/// tab | uv

```bash
uv add pydantic-ai pydantic-ai-harness
```

///


⟦CODE3⟧

[`Coder`](harness/coder.md) একটি সাধারণ [সম্মিলিত ক্যাপাবিলিটি](capabilities/custom.md#composition-and-middleware-semantics), কোনো রহস্যময় বাক্স নয়: পুরোটা ব্যবহার করুন, অথবা এর ভেতরের অংশগুলো সরাসরি ব্যবহার করুন; দুটোই সমান:

⟦CODE4⟧

ফাইলটি চালালেই টার্মিনালে এজেন্টের সাথে কথা বলতে পারবেন। কোনো কোড লেখার আগেই চেষ্টা করে দেখতে, প্রকাশিত [`coder_agent`](harness/coder.md#api-reference)-টি [`clai`](cli.md#custom-agents) (Pydantic AI CLI) দিয়ে [`uvx`](https://docs.astral.sh/uv/guides/tools/)-এর মাধ্যমে চালান:

```bash
uvx --with pydantic-ai-harness clai -a pydantic_ai_harness.coder:coder_agent -m anthropic:claude-fable-5-1
```

**এটি বানান →** [Coder](harness/coder.md), [Harness](harness/index.md) থেকে

**GitHub-এ চালান →** [GitHub Agentic Workflows](harness/gh-aw.md), issue, pull request বা নির্দিষ্ট সময়সূচিতে

////

//// tab | ডেটা বের করা

এজেন্টকে একটি [আউটপুট টাইপ](output.md) আর কিছু [টুল](tools.md) দিন, তাহলে প্রতিটি রান যাচাই হওয়া, টাইপসহ ফল ফেরত দেবে:

/// tab | pip

```bash
pip install pydantic-ai
```

///

/// tab | uv

```bash
uv add pydantic-ai
```

///


⟦CODE5⟧

[`@agent.tool`](tools.md) ফাংশনটি একটি [`RunContext`][pydantic_ai.tools.RunContext] পায়, যা আপনার [dependencies](dependencies.md) বহন করে আনে; এর বাকি signature আর docstring হয়ে যায় টুলের schema, আপনার কোড চলার আগেই আর্গুমেন্টগুলো [যাচাই হয়](tools.md#function-tools-and-schema), আর রানটি নিশ্চিতভাবে একটি `Sentiment` ফেরত দেয়, ফলে আপনার IDE, type checker আর LLM সবাই ফেরত টাইপ নিয়ে একমত।

**এটি বানান →** [Agents](agent.md), [Function Tools](tools.md), আর [Structured Output](output.md)

////

//// tab | টেকসই ওয়ার্কফ্লো

[`TemporalDurability`](durable_execution/temporal.md) লাগালে একই এজেন্ট একটি [Temporal](durable_execution/temporal.md) ওয়ার্কফ্লোর ভেতরে [টেকসই এক্সিকিউশনে](durable_execution/overview.md) চলে: প্রতিটি মডেল আর টুল কল একটি টেকসই activity হয়ে যায়, ফলে ব্যাকগ্রাউন্ড কিউতে চলা একটি রান রিস্টার্ট, ব্যর্থতা আর দীর্ঘ অপেক্ষার পরেও টিকে থাকে:

/// tab | pip

```bash
pip install "pydantic-ai[temporal]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai[temporal]"
```

///


⟦CODE6⟧

[DBOS](durable_execution/dbos.md) আর [Prefect](durable_execution/prefect.md) একইভাবে লাগানো যায়, নিজস্ব আর যৌথভাবে রক্ষণাবেক্ষণ করা; সাথে আছে [Restate, AWS Lambda, Airflow, Absurd আর pgtask](durable_execution/overview.md)-এর integration।

একটি রান সংরক্ষণ, আবার শুরু আর ভাগ (fork) করতে কোনো ইঞ্জিন লাগে না: Pydantic AI Harness-এর [`StepPersistence`](harness/step-persistence.md) প্রতিটি সম্পন্ন ধাপের ছবি (snapshot) আপনার বেছে নেওয়া ভাণ্ডারে রাখে, যেমনটা একটি checkpointer করে (দেখুন [Persistence](persistence.md))। ইঞ্জিন দরকার শুধু এমন রান উদ্ধারের জন্য, যা একটি ধাপের মাঝপথে ক্র্যাশ করেছে।

**এটি বানান →** [Durable Execution](durable_execution/overview.md)

////

//// tab | রিয়েলটাইম ভয়েস

একই এজেন্টকে একটি লাইভ ভয়েস সেশনে বসান, [টুল](realtime/tools.md) আর [ক্যাপাবিলিটি](realtime/capabilities.md)সহ:

/// tab | pip

```bash
pip install "pydantic-ai[openai-realtime]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai[openai-realtime]"
```

///


⟦CODE7⟧

কথা চালিয়ে যেতে যেতেই মডেল কথোপকথনের মাঝে আপনার টুল ডাকে, আর প্রতিটি সেশন [instrument করা](logfire.md) থাকে; ভয়েস হলো আরেকটি ফ্রন্টএন্ড মাত্র, OpenAI Realtime, Gemini Live, Azure আর xAI Grok Voice-এ।

**এটি বানান →** [Realtime Voice](realtime/overview.md), শুরু করুন [ভয়েস অ্যাসিস্ট্যান্ট উদাহরণ](examples/realtime-voice.md) থেকে

////

//// tab | ছবি তৈরি

একটি নির্দিষ্ট ছবির মডেল দিয়ে ছবি তৈরি করুন, কোনো এজেন্ট রান ছাড়াই:

/// tab | pip

```bash
pip install pydantic-ai
```

///

/// tab | uv

```bash
uv add pydantic-ai
```

///


⟦CODE8⟧

সেই [আলাদা ছবির API](image-generation.md) তখনকার জন্য, যখন সিদ্ধান্ত নেয় আপনার অ্যাপ্লিকেশন; যখন সিদ্ধান্ত নেয় একটি এজেন্ট রান, তখন আছে টাইপসহ ছবির [আউটপুটের](output.md#image-output) জন্য `output_type=BinaryImage` দিয়ে [প্রোভাইডারের নিজস্ব ছবি তৈরি](native-tools.md#image-generation-tool), আর যে মডেল নিজে ছবি তৈরি করতে পারে না তাদের জন্য বিকল্পসহ [`ImageGeneration` ক্যাপাবিলিটি](capabilities/image-generation.md)।

**এটি বানান →** [Image Generation](image-generation.md)

////

/// tip | Logfire-এ আপনার প্রথম রান দেখুন

এই এজেন্টগুলোর যেকোনোটি চলার আগে দুটি লাইন যোগ করুন, তাহলে প্রতিটি মডেল কল আর টুল কল [Pydantic Logfire](https://pydantic.dev/logfire)-এ দেখা যাবে। Logfire-এর একটি [ফ্রি স্তর](https://pydantic.dev/pricing/) আছে, যাতে ক্রেডিট কার্ড লাগে না, আর শুধু একটি GitHub অ্যাকাউন্ট দিয়েই সাইন আপ করা যায়। প্রথমে একবার `uvx logfire auth` আর `uvx logfire projects new` চালান, অথবা আপনার কোডিং এজেন্টকে [Logfire সেটআপ skill](https://pydantic.dev/ai-setup.md) দেখিয়ে দিন, সে নিজেই করে দেবে। বিস্তারিত আছে [Logfire গাইডে](logfire.md#using-logfire), আর বদলে [যেকোনো OpenTelemetry backend](logfire.md#using-opentelemetry)-ও কাজ করে।

⟦CODE9⟧

///

/// tip | এখনো API key নেই?

এগুলোর কোনোটি চেষ্টা করতে কোনো প্রোভাইডারের API key লাগবে না। built-in [`'test'` মডেল](testing.md#unit-testing-with-testmodel) (`Agent('test')`) দিন, যা কোনো LLM না ডেকে পুরোপুরি অফলাইনে চলে, ফলে আগে আপনার এজেন্ট, টুল আর আউটপুট পরখ করে নিতে পারেন। আসল মডেলের জন্য প্রস্তুত হলে, [Pydantic AI Gateway](gateway.md) আপনাকে OpenAI, Anthropic, Google Cloud, Groq আর AWS Bedrock-এর মডেলের জন্য একটিই চাবি দেয়; অথবা একটি প্রোভাইডার বেছে তার নিজের API key সেট করতে দেখুন [মডেল ও প্রোভাইডার](models/overview.md)।

///

## কেন Pydantic AI { #why-pydantic-ai }

- **যেকোনো মডেল, একটিই Python API।** [প্রায় সব মডেল আর প্রোভাইডার](models/overview.md) (OpenAI, Anthropic, Google, Bedrock, Azure AI Foundry, Groq, Mistral, xAI, Ollama আর আরও কয়েক ডজন), একটি স্ট্রিং দিয়ে বদলানো যায়, অথবা [Pydantic AI Gateway](gateway.md) দিয়ে: সবগুলোর জন্য একটি চাবি, বিকল্পে চলে যাওয়া (failover) আর খরচ পর্যবেক্ষণসহ। কোনো প্রধান সুবিধা একটি কোম্পানিতে আটকে নেই।

- **শুরু থেকে শেষ পর্যন্ত টাইপসহ।** [গোছানো আউটপুট](output.md), টাইপসহ [dependency injection](dependencies.md), [টাইপসহ টুল](tools.md): আপনার IDE, type checker আর কোডিং এজেন্ট সবাই জানে আপনার এজেন্ট কী ফেরত দেয়, ফলে অনেক ধরনের এরর চলার সময় থেকে সরে লেখার সময়েই ধরা পড়ে। সাধারণ নিয়ন্ত্রণ-প্রবাহ যথেষ্ট না হলে, [Pydantic Graph](graph.md) গ্রাফ-ভিত্তিক ওয়ার্কফ্লোতে একই টাইপের সুবিধা আনে।

- **আন্দাজে নয়, মেপে।** OpenTelemetry-নির্ভর [instrumentation](logfire.md) যেকোনো OTel backend-এর সাথে কাজ করে; একটি লাইনেই [Pydantic Logfire](https://pydantic.dev/logfire) চালু হয়, তাৎক্ষণিক ডিবাগিং, ট্রেসিং আর [genai-prices](https://github.com/pydantic/genai-prices)-ভিত্তিক খরচ হিসাবের জন্য। [Pydantic Evals](evals.md) চূড়ান্ত আউটপুট আর [টুল-কলের ধারাবাহিকতা](evals/evaluators/agentic.md) মূল্যায়ন করে, কোডে রাখা ডেটাসেটের ওপর, অথবা [অনলাইন মূল্যায়ন](evals/online-evaluation.md) দিয়ে প্রোডাকশনের আসল ট্রাফিকের একটি নমুনার ওপর।

- **সব সরঞ্জাম, জোড়া লাগানোর মতো করে।** একটিই মৌলিক উপাদান, [ক্যাপাবিলিটি](capabilities/overview.md), [টুল](tools.md), [নির্দেশনা (instructions)](agent.md#instructions), [hook](hooks.md) আর [মডেল সেটিংস](agent.md#model-run-settings)-কে বারবার ব্যবহারযোগ্য একক হিসেবে বাঁধে। মূল প্যাকেজে আছে [MCP](capabilities/mcp.md) আর [ওয়েব সার্চের](capabilities/web-search.md) মতো মৌলিক জিনিস, [Harness](harness/index.md)-এ আছে বাকি সব, আর [Coder](harness/coder.md) ও [Researcher](harness/researcher.md)-এর মতো সম্পূর্ণ এজেন্টও শুধু ক্যাপাবিলিটি জোড়া লাগিয়ে তৈরি: যেভাবে জোড়া হয়েছে, সেভাবেই খোলা যায়। অথবা কোড ছাড়াই [YAML/JSON agent spec](agent-spec.md) দিয়ে লিখুন।

- **[সব ইন্টারফেস](interfaces.md)।** একটি এজেন্টের সংজ্ঞা চলে [CLI](cli.md), একটি [built-in ওয়েব চ্যাট](web.md), বা [রিয়েলটাইম কথোপকথন](realtime/overview.md) হিসেবে; [UI ইভেন্ট স্ট্রিম](ui/overview.md) (AG-UI, Vercel AI) একে আপনার নিজের ফ্রন্টএন্ড বা অন্য যেকোনো কিছুর সাথে যুক্ত করে; [ACP](harness/acp.md) একে editor এজেন্ট হিসেবে চালায়; আর [GitHub Agentic Workflows](harness/gh-aw.md) একে issue, pull request বা সময়সূচিতে স্ক্রিন ছাড়া (headless) চালায়।

- **টেকসই এক্সিকিউশন।** আটটি ইঞ্জিনে [টেকসই এক্সিকিউশন](durable_execution/overview.md): Temporal, DBOS, Prefect, Restate, AWS Lambda, Airflow, Absurd আর pgtask, এর প্রথম পাঁচটি সংশ্লিষ্ট কোম্পানির দলের সাথে যৌথভাবে রক্ষণাবেক্ষণ করা। এজেন্ট রিস্টার্টের পরেও টিকে থাকে আর আপনার ইতিমধ্যে চালানো ইঞ্জিনে দিনের পর দিন চলতে পারে, সাথে আছে [মানুষের অনুমোদন (human-in-the-loop)](deferred-tools.md#human-in-the-loop-tool-approval)।

- **অন্য framework থেকে আসছেন?** [তুলনাগুলো](comparisons/index.md) দেখায় LangChain, Google ADK, Claude Agent SDK আর আরও সাতটির থেকে Pydantic AI কোথায় আলাদা, আর [migration skill](framework-migration.md) দিয়ে আপনার কোডিং এজেন্ট একটি বিদ্যমান অ্যাপ্লিকেশন নিয়ে আসতে পারে।

[Pydantic](https://docs.pydantic.dev) দলের তৈরি: [Pydantic Validation](https://pydantic.dev/docs/) হলো OpenAI SDK, Anthropic SDK, Google ADK, LangChain আর AI জগতের বেশিরভাগের যাচাই-স্তর (আর FastAPI যার ওপর তৈরি তার ভিত্তি)। Pydantic AI এজেন্টের জগতে সেই একই অনুভূতি নিয়ে আসে।

**আমাদের নিউজলেটার *The Pydantic Stack*-এ সাইন আপ করুন, Pydantic AI, Logfire আর Pydantic নিয়ে হালনাগাদ খবর ও টিউটোরিয়ালের জন্য:**

  ⟦CODE10⟧

## সব একসাথে: একটি ব্যাংকের গ্রাহকসেবা এজেন্ট { #putting-it-together-a-bank-support-agent }

এখানে একটি ব্যাংকের গ্রাহকসেবা এজেন্ট, যা কয়েকটি সুবিধা একসাথে কাজ করতে দেখায়: [dependency injection](dependencies.md) নির্দেশনা আর টুলে ডেটাবেস সংযোগ বহন করে, [ফাংশন টুল](tools.md) যা মডেল ডাকে, প্রতিটি রানে যাচাই হওয়া [গোছানো আউটপুট](output.md), গ্রাহকের প্রেক্ষাপট বাঁধা একটি বারবার ব্যবহারযোগ্য [ক্যাপাবিলিটি](capabilities/overview.md), আর একটি [চাহিদামতো ক্যাপাবিলিটি](capabilities/on-demand.md), যা মডেল শুধু কথোপকথনে দরকার হলে লোড করে:

⟦CODE11⟧

1. `SupportDependencies` dataclass দিয়ে সেই ডেটা, সংযোগ আর যুক্তি মডেলে পাঠানো হয়, যা [নির্দেশনা](agent.md#instructions) আর [টুল](tools.md) ফাংশন চালানোর সময় লাগবে। Pydantic AI-এর [dependency injection](dependencies.md) ব্যবস্থা আপনার এজেন্টের আচরণ নিজের মতো করার একটি [টাইপ-নিরাপদ](agent.md#static-type-checking) উপায় দেয়, আর [unit test](testing.md) ও eval চালানোর সময় বিশেষভাবে কাজে লাগে।
2. উদাহরণটি ছোট আর পাঠযোগ্য রাখতে এটি একটি ডেটাবেস সংযোগের সরল খসড়া। বাস্তবে, গ্রাহকের তথ্য পেতে আপনি একটি বাইরের ডেটাবেসে (যেমন PostgreSQL) সংযোগ করবেন।
3. এজেন্টের ফেরত দেওয়া গোছানো ডেটা সীমিত রাখতে এই [Pydantic](https://docs.pydantic.dev) মডেল ব্যবহার হয়। এই সহজ সংজ্ঞা থেকেই Pydantic JSON Schema বানায়, যা LLM-কে বলে কীভাবে ডেটা ফেরত দিতে হবে, আর রানের শেষে ডেটা সঠিক কিনা তা নিশ্চিত করতে যাচাই করে।
4. একটি [`Capability`][pydantic_ai.capabilities.Capability] সম্পর্কিত নির্দেশনা আর টুলকে একটি বারবার ব্যবহারযোগ্য এককে বাঁধে: [ওয়েব সার্চের](capabilities/web-search.md) মতো [built-in ক্যাপাবিলিটি](capabilities/overview.md) আর [Harness](harness/index.md)-এর সবকিছুর পেছনে এই একই মৌলিক উপাদান। এটি গ্রাহকের প্রেক্ষাপট বহন করে; যেমন আছে তেমনই অন্য যেকোনো এজেন্টের `capabilities` তালিকায় বসিয়ে দিতে পারেন।
5. গতিশীল [নির্দেশনা](agent.md#instructions) dependency injection ব্যবহার করতে পারে। dependency আসে [`RunContext`][pydantic_ai.tools.RunContext] আর্গুমেন্টের মাধ্যমে, যা ওপরের `deps_type` দিয়ে প্যারামিটারযুক্ত। এখানের টাইপ annotation ভুল হলে static type checker তা ধরবে।
6. [`tool`](tools.md) decorator এমন একটি ফাংশন নথিভুক্ত করে, যার signature হয়ে যায় একটি টুল, যা উত্তর দেওয়ার সময় LLM ডাকতে পারে। আবারও, dependency আসে [`RunContext`][pydantic_ai.tools.RunContext] দিয়ে; বাকি যেকোনো আর্গুমেন্ট হয়ে যায় LLM-এ পাঠানো টুলের schema। এই আর্গুমেন্টগুলো যাচাইয়ে Pydantic ব্যবহার হয়, আর এরর LLM-এর কাছে ফেরত যায় যাতে সে আবার চেষ্টা করতে পারে।
7. একটি টুলের docstring-ও টুলের বর্ণনা হিসেবে LLM-এ যায়। প্যারামিটারের বর্ণনা docstring থেকে [বের করে](tools.md#function-tools-and-schema) LLM-এ পাঠানো প্যারামিটারের schema-য় যোগ করা হয়।
8. `defer_loading=True` একে একটি [চাহিদামতো ক্যাপাবিলিটি](capabilities/on-demand.md) বানায়, একটি [Agent Skill](capabilities/on-demand.md#loading-skills-from-markdown-files)-এর মতো। prompt-এ এটি এক লাইনের একটি তালিকা-এন্ট্রিতে গুটিয়ে থাকে, আর এর টুলগুলো লুকানো থাকে যতক্ষণ না মডেল একে প্রাসঙ্গিক মনে করে framework-এর দেওয়া `load_capability` টুল দিয়ে লোড করে।
9. এই [এজেন্টটি](agent.md) একটি ব্যাংকে প্রথম স্তরের গ্রাহকসেবা দেবে। এজেন্ট কোন ধরনের dependency নেবে আর কোন ধরনের আউটপুট ফেরত দেবে, তাতে এটি generic। এক্ষেত্রে গ্রাহকসেবা এজেন্টের টাইপ `#!python Agent[SupportDependencies, SupportOutput]`।
10. এখানে আমরা এজেন্টটিকে একটি [OpenAI](api/models/openai.md) মডেল ব্যবহার করতে কনফিগার করছি; এজেন্ট চালানোর সময়েও মডেল ঠিক করা যায়।
11. এজেন্টের উত্তর নিশ্চিতভাবে একটি `SupportOutput` হবে। এজেন্টটি generic বলে, static type checking-এর সুবিধার জন্য এর টাইপও `SupportOutput` থাকবে। যাচাই ব্যর্থ হলে, এজেন্টকে [আবার চেষ্টা করতে বলা হয়](agent.md#reflection-and-self-correction)।
12. এজেন্টে ক্যাপাবিলিটিগুলো লাগান। আরও [ক্যাপাবিলিটি](capabilities/overview.md), যেমন [ওয়েব সার্চ](capabilities/web-search.md) বা [Harness](harness/index.md)-এর যেকোনো কিছু, একই তালিকায় পাশাপাশি বসে যায়।
13. বাস্তব ব্যবহারে, এজেন্টের প্রেক্ষাপট আর সেবা বাড়াতে আপনি আরও টুল আর বড় নির্দেশনা যোগ করবেন।
14. চূড়ান্ত উত্তরে না পৌঁছানো পর্যন্ত LLM-এর সাথে কথোপকথন চালিয়ে, এজেন্টটি asynchronous ভাবে [চালান](agent.md#running-agents)। এই মোটামুটি সহজ ক্ষেত্রেও, আউটপুট পেতে টুল ডাকার সাথে সাথে এজেন্ট LLM-এর সাথে কয়েকটি বার্তা আদান-প্রদান করবে।
15. এই পালাটি চাহিদামতো ক্যাপাবিলিটি পরখ করে: মডেল `refunds` তালিকা-এন্ট্রি দেখে, `id='refunds'` দিয়ে `load_capability` ডাকে, আর তার পরেই উত্তর দেওয়ার জন্য `refund_status` টুলটি পায়: [চাহিদামতো লোডিং](capabilities/on-demand.md) কাজে।

/// info | কোডটি সহজ ভাষায়

ভাবুন ব্যাংকের একজন নতুন কর্মী। `SupportDependencies` হলো তাকে দেওয়া চাবির গোছা (কোন গ্রাহক, ডেটাবেসের সংযোগ)। টুলগুলো (`customer_balance` ইত্যাদি) হলো সে যে খাতাগুলো খুলে দেখতে পারে। `SupportOutput` হলো ব্যাংকের নির্দিষ্ট ফর্ম, যা দিয়েই তাকে উত্তর দিতে হবে। আর `refunds` ক্যাপাবিলিটি হলো একটি আলমারি, যা শুধু ফেরতের প্রশ্ন এলে খোলা হয়, যাতে সাধারণ কাজের সময় টেবিলে ভিড় না থাকে।

///

[dependencies](dependencies.md) dataclass পূর্ণ টাইপ-নিরাপত্তাসহ ডেটাবেস সংযোগকে [নির্দেশনা](agent.md#instructions) আর [টুলে](tools.md) বহন করে: একটি পরীক্ষার নকল (test double) বসিয়ে দিলে একই এজেন্ট [unit test](testing.md) আর eval-এ চলে। আর গ্রাহকের প্রেক্ষাপট যেহেতু একটি [ক্যাপাবিলিটি](capabilities/overview.md), এটি জোড়া লাগানো যায়: একই একক কোনো পরিবর্তন ছাড়াই একটি ভয়েস এজেন্ট বা ওয়েব অ্যাপে বসে যায়।

/// tip | সম্পূর্ণ `bank_support.py` উদাহরণ

সংক্ষেপের জন্য এখানের কোডটি অসম্পূর্ণ (`DatabaseConn`-এর সংজ্ঞা নেই); সম্পূর্ণ `bank_support.py` উদাহরণটি পাবেন [এখানে](examples/bank-support.md)।

///

## Pydantic Logfire দিয়ে instrumentation { #instrumentation-with-pydantic-logfire }

Pydantic AI [OpenTelemetry](https://opentelemetry.io/)-নির্ভর: [Instrumentation](capabilities/instrumentation.md) ক্যাপাবিলিটি প্রতিটি মডেল কল আর টুল কলের জন্য মানক OTel span তৈরি করে, আর [যেকোনো OTLP backend কাজ করে](logfire.md#alternative-observability-backends)। সবচেয়ে সহজ সেটআপ হলো [`logfire` SDK](logfire.md#using-logfire), যা সাধারণ OpenTelemetry বোঝে আর [Pydantic Logfire](https://pydantic.dev/logfire) বা অন্য যেকোনো backend-এ পাঠাতে পারে।

মাত্র কয়েকটি টুলওয়ালা একটি সহজ এজেন্টেও LLM-এর সাথে অনেক আদান-প্রদান হতে পারে, ফলে শুধু কোড পড়ে কী ঘটছে তা নিশ্চিত হওয়া প্রায় অসম্ভব। ওপরের রানগুলো চলতে দেখতে, [Logfire সেটআপ করুন](logfire.md#using-logfire) আর কোডে নিচেরটি যোগ করুন:

⟦CODE12⟧

1. Logfire SDK কনফিগার করুন; project সেটআপ না থাকলে এটি ব্যর্থ হবে।
2. এটি এখন থেকে ব্যবহৃত সব Pydantic AI এজেন্টকে instrument করবে। শুধু একটি নির্দিষ্ট এজেন্ট instrument করতে, এজেন্টের `capabilities=[...]`-এ একটি [`Instrumentation`][pydantic_ai.capabilities.Instrumentation] এন্ট্রি যোগ করুন।
3. আমাদের ডেমোতে, `DatabaseConn` একটি PostgreSQL ডেটাবেসে সংযোগ করতে [`sqlite3`][] ব্যবহার করে, তাই ডেটাবেসের query লগ করতে [`logfire.instrument_sqlite3()`](https://logfire.pydantic.dev/docs/integrations/databases/sqlite3/)
   ব্যবহার হয়েছে।

এতেই আপনার এজেন্টকে কাজ করতে দেখার নিচের দৃশ্যটি পাওয়া যায়:

/// info | Logfire trace

[Logfire instrumentation for the bank agent](https://logfire-eu.pydantic.dev/public-trace/a2957caa-b7b7-4883-a529-777742649004?spanId=31aade41ab896144)

///

আরও জানতে দেখুন [Monitoring and Performance](logfire.md)।

## `llms.txt` { #llmstxt }

Pydantic AI ডকুমেন্টেশন [llms.txt](https://llmstxt.org/) ফরম্যাটে পাওয়া যায়।
এই ফরম্যাট Markdown-এ সংজ্ঞায়িত আর LLM, AI কোডিং সহকারী ও এজেন্টের জন্য উপযোগী।

দুটি ফরম্যাট পাওয়া যায়:

- [`llms.txt`](https://pydantic.dev/docs/ai/llms.txt): প্রজেক্টের একটি সংক্ষিপ্ত বর্ণনা আর
  ডকুমেন্টেশনের বিভিন্ন অংশের লিংকসহ একটি ফাইল। এই ফাইলের গঠন
  [এখানে](https://llmstxt.org/#format) বিস্তারিত বর্ণিত।
- [`llms-full.txt`](https://pydantic.dev/docs/ai/llms-full.txt): `llms.txt` ফাইলের মতোই,
  তবে প্রতিটি লিংকের বিষয়বস্তু ভেতরে দেওয়া। মনে রাখুন, কিছু LLM-এর জন্য এই ফাইলটি খুব বড় হতে পারে।

আজ পর্যন্ত, IDE বা কোডিং এজেন্ট এই ফাইলগুলো নিজে থেকে কাজে লাগায় না, তবে আপনি লিংক বা পুরো লেখাটি দিলে সেগুলো ব্যবহার করবে।


## পরের ধাপ { #next-steps }

**এখনই কিছু চালান।** একটি কমান্ডেই আপনার টার্মিনালে একটি সম্পূর্ণ [কোডিং এজেন্ট](harness/coder.md) চলে আসে:

```bash
uvx --with pydantic-ai-harness clai -a pydantic_ai_harness.coder:coder_agent -m anthropic:claude-fable-5-1
```

অথবা [Pydantic AI ইনস্টল করুন](install.md), একটি [মডেল](models/overview.md) বেছে নিন ([Pydantic AI Gateway](gateway.md) হলো সবগুলোর জন্য একটি চাবি), আর আপনার নিজের কোডিং এজেন্টকে কাজে লাগান: হালনাগাদ framework জ্ঞান দিতে [Pydantic AI skill](coding-agent-skills.md) ইনস্টল করুন, তাকে [উদাহরণগুলো](examples/setup.md) আর [Harness সূচি](harness/index.md) দেখিয়ে দিন, তারপর বলুন আপনি কী বানাতে চান।

**আপনার এজেন্ট কী করল দেখুন।** [একে instrument করুন](logfire.md): এক লাইনের সেটআপ, আর প্রতিটি মডেল কল ও টুল কল দেখা যায়। এটি মানক OpenTelemetry: [Pydantic Logfire](https://pydantic.dev/logfire), যার একটি [ফ্রি স্তর](https://pydantic.dev/pricing/) আছে (ক্রেডিট কার্ড লাগে না; শুধু একটি GitHub অ্যাকাউন্ট দিয়েই সাইন আপ), দেখার সবচেয়ে সহজ উপায়; তবে যেকোনো OTLP backend কাজ করে।

**চালু করুন।** [প্রোডাকশনে যাওয়া](production.md) সেই প্রশ্নগুলোর উত্তর দেয় যা দল একটি এজেন্ট চালুর আগে জিজ্ঞাসা করে: ক্র্যাশ থেকে উদ্ধার আর মানুষের অনুমোদন থেকে শুরু করে খরচের সীমা, ট্রেসিং আর deploy পর্যন্ত।

**একটি রিপোজিটরিতে কাজে লাগান।** সেই একই এজেন্ট, বা আপনার নিজের লেখা একটি, [GitHub Agentic Workflow](harness/gh-aw.md) হিসেবে issue, pull request বা সময়সূচিতে চলে: স্ক্রিন ছাড়া, একটি sandbox-এ, নিরাপদ আউটপুটের মাধ্যমে লিখে।

**আরও গভীরে যান।** [Agents গাইড](agent.md) হলো মূল পথনির্দেশ; [API রেফারেন্স](api/agent.md) পুরো ইন্টারফেস বর্ণনা করে; [Harness](harness/index.md)-এ আছে সব সরঞ্জাম।

**সাহায্য নিন।** [Slack](https://logfire.pydantic.dev/docs/join-slack/)-এ যোগ দিন বা [GitHub](https://github.com/pydantic/pydantic-ai/issues)-এ একটি issue খুলুন।

## Pydantic Stack-এর অংশ { #part-of-the-pydantic-stack }

প্রোডাকশন-মানের AI এজেন্ট চালু করতে আপনার যা যা দরকার:

- [Pydantic Validation](https://pydantic.dev/docs/validation/latest/): সবকিছুর নিচের যাচাই-স্তর
- [Pydantic AI Harness](harness/index.md): অফিসিয়াল ক্যাপাবিলিটি লাইব্রেরি আর harness, একক ক্যাপাবিলিটি থেকে সম্পূর্ণ এজেন্ট পর্যন্ত
- [Pydantic Logfire](https://pydantic.dev/logfire): AI-কেন্দ্রিক, পুরো অ্যাপের পর্যবেক্ষণ
- [Pydantic AI Gateway](gateway.md): সব মডেলের জন্য একটি চাবি, খরচ পর্যবেক্ষণ আর খরচের সীমাসহ
- [Pydantic Evals](evals.md): এজেন্টসহ যেকোনো Python ফাংশন মূল্যায়ন, চূড়ান্ত আউটপুট থেকে [টুল-কলের ধারাবাহিকতা](evals/evaluators/agentic.md) পর্যন্ত, ডেটাসেটে বা [লাইভ ট্রাফিকে](evals/online-evaluation.md) ([Logfire-এ প্রোডাকশন eval](https://pydantic.dev/logfire/evals) সহ)
- [Pydantic Graph](graph.md): টাইপসহ গ্রাফ নিয়ন্ত্রণ-প্রবাহ
- [genai-prices](https://github.com/pydantic/genai-prices): মডেলের দামের তথ্য, হালনাগাদ রাখা
- [Monty](https://github.com/pydantic/monty): মডেলের লেখা কোডের জন্য একটি sandboxed Python interpreter

/// check | সংক্ষেপে মনে রাখুন

* Pydantic AI = টাইপসহ এজেন্ট: `Agent(model, output_type=..., deps_type=..., capabilities=[...])` আর `@agent.tool`।
* মডেল বদলাতে শুধু স্ট্রিং বদলান; API key ছাড়া পরীক্ষায় `Agent('test')`।
* টুলের আর্গুমেন্ট আর চূড়ান্ত আউটপুট দুটোই Pydantic দিয়ে যাচাই হয়; ভুল হলে মডেল আবার চেষ্টা করে।
* কী ঘটছে দেখতে Logfire (বা যেকোনো OpenTelemetry backend)।

///
