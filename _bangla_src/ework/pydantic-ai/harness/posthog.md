# PostHog { #posthog }

/// note | এই পেজে যা শিখবেন

* `PostHog` দিয়ে [PostHog](https://posthog.com)-এর হোস্ট করা MCP সার্ভারে product analytics query, SQL আর feature flag, experiment, dashboard পরিচালনা।
* personal API key, প্রতি-ব্যবহারকারী credential, `features` আর `read_only` দিয়ে সংকীর্ণ করা।

///

`PostHog` একটি এজেন্টকে [PostHog](https://posthog.com)-এর হোস্ট করা MCP সার্ভারে যুক্ত করে, যাতে এটি product analytics query করতে, SQL চালাতে আর feature flag, experiment, dashboard, survey ও error tracking পরিচালনা করতে পারে, পরিবর্তন করা টুলসহ। আপনি যে key দিয়ে যুক্ত হন তা ঠিক করে ওই টুলগুলো কোথায় পৌঁছাতে পারবে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/posthog/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## শুরুর আগে { #before-you-start }

MCP Server preset দিয়ে একটি personal API key তৈরি করুন ([US](https://us.posthog.com/settings/user-api-keys?preset=mcp_server) বা [EU](https://eu.posthog.com/settings/user-api-keys?preset=mcp_server) Cloud)। US আর EU Cloud অ্যাকাউন্ট একই সার্ভার ব্যবহার করে। দেখুন [provider setup](https://posthog.com/docs/model-context-protocol)।

কিছু PostHog টুল PostHog-এর দিকে একটি LLM ব্যবহার করে। সেগুলোর জন্য আপনার organization-এ AI data processing চালু থাকা লাগে আর PostHog AI usage হিসেবে bill হতে পারে।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[posthog]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[posthog]" "pydantic-ai-slim[openai]"
```

///


দ্বিতীয় প্যাকেজটি উদাহরণে ব্যবহৃত OpenAI provider ইনস্টল করে। অন্য মডেলের জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

## সংযোগ { #connect }

⟦CODE1⟧

`POSTHOG_PERSONAL_API_KEY` একটি PostHog personal API key-তে সেট করুন, বা `auth=`-এ একটি key দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। একটি এজেন্ট থেকে কয়েকজন ব্যবহারকারীকে পরিবেশন করতে, এর বদলে একটি ফাংশন দিন (দেখুন [Per-user credentials](#per-user-credentials))।

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন PostHog অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `POSTHOG_PERSONAL_API_KEY`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি personal API key বা OAuth access token | সেই key, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া key সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো PostHog টুল থাকে না। একটি ফাংশন কখনো `POSTHOG_PERSONAL_API_KEY` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির key বা `POSTHOG_PERSONAL_API_KEY` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের PostHog অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় key স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর key পড়া একটি ফাংশন দিন:

⟦CODE2⟧

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না। `read_only` আর `features` তবুও প্রতিটি রানে প্রযোজ্য।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর key পায়, রাখে আর, এটি একটি OAuth token হলে, হালনাগাদ করে। যেমন, একটি সেটিং পেজ যেখানে প্রতিটি ব্যবহারকারী নিজের personal API key paste করেন, বা একটি "Connect PostHog" বাটন যা তাদের PostHog OAuth দিয়ে sign in করিয়ে access token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, key একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। capability-র `id`-এর ডিফল্ট `posthog`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `PostHog` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## Provider সেটিং { #provider-settings }

ডিফল্টভাবে সার্ভার সবকিছু একটি একক `posthog` টুল দিয়ে দেয়, যা এজেন্ট কমান্ড দিয়ে চালায়, তাই সার্ভারে এটি কোথায় পৌঁছাতে পারবে তা সংকীর্ণ করুন:

- `features=['flags', 'insights', 'sql']` সার্ভারকে ওই [feature groups](https://github.com/PostHog/posthog/blob/master/services/mcp/README.md#feature-filtering)-এ সীমিত করে। প্রতিটি গ্রুপের জন্য এটি সেট করবেন না।
- `read_only=True` সার্ভারকে এর শুধু-পড়া মোড চায়, যা পরিবর্তন করা প্রতিটি টুল বাদ দেয়।

key-এর scope, আর এটি যে organization ও project-এ পৌঁছাতে পারে, তবুও ঠিক করে এজেন্ট কোথায় প্রবেশ করতে পারবে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি "সাপ্তাহিক মেট্রিক রিপোর্ট" এজেন্টের শুধু insight আর SQL দরকার — feature flag বন্ধ করা বা experiment মোছার কোনো দরকার নেই। `PostHog(features=['insights', 'sql'], read_only=True)` দিলে এজেন্ট শুধু ডেটা পড়তে পারে; ভুল করেও একটি প্রোডাকশন flag বন্ধ করতে পারবে না।

///

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়:

⟦CODE3⟧

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি self-hosted instance-এর জন্য আপনার চালানো একটি PostHog MCP সার্ভারে নির্দেশ করা একটি, একটি proxy বা MCP handler। client তখন URL আর authentication-এর মালিক, তাই `auth` বা `features`-এর সাথে `client` দিলে একটি error ওঠে। একটি client-সহ, `read_only=True` সার্ভারকে শুধু-পড়া মোড না চেয়ে শুধু সার্ভার শুধু-পড়া হিসেবে চিহ্নিত করা টুল রাখে। PostHog-এর ডিফল্ট মোড একটি `posthog` টুল দেয় যা শুধু-পড়া হিসেবে চিহ্নিত নয়, তাই এই ছাঁকনি কোনো PostHog টুল রাখে না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে; এর বদলে আপনার client দিয়ে `x-posthog-read-only: true` header পাঠান। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)।

## Telemetry { #telemetry }

`PostHog` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) আগে থেকেই প্রতিটি PostHog টুল কল একটি tool span হিসেবে লেখে, আর সংযোগে নিজস্ব একটি span-এর যোগ্য কোনো সিদ্ধান্ত নেই।

## YAML বা JSON-এ এজেন্ট সংজ্ঞায়িত করা { #define-the-agent-in-yaml-or-json }

একটি YAML ফাইল লোড করতে `spec` extra-ও লাগে:

/// tab | pip

```bash
pip install "pydantic-ai-slim[spec]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[spec]"
```

///


⟦CODE4⟧

⟦CODE5⟧

`custom_capability_types` দিন, যাতে loader ফাইল থেকে `PostHog` তৈরি করতে পারে।

## API রেফারেন্স { #api-reference }

⟦CODE6⟧

/// check | সংক্ষেপে মনে রাখুন

* `PostHog()` আর `POSTHOG_PERSONAL_API_KEY` (MCP Server preset-এর key) বা `auth=`।
* ডিফল্টভাবে একটি `posthog` টুল সব করে — `features=[...]` আর `read_only=True` দিয়ে সংকীর্ণ করুন।
* কিছু টুল PostHog-এর LLM ব্যবহার করে আর আলাদা bill হতে পারে।
* `client`-সহ শুধু-পড়ার জন্য `x-posthog-read-only: true` header।

///
