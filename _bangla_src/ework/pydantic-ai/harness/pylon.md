
# Pylon { #pylon }

/// note | এই পেজে যা শিখবেন

* `Pylon` দিয়ে [Pylon](https://www.usepylon.com)-এর হোস্ট করা MCP সার্ভারে support issue, account আর contact নিয়ে কাজ।
* কোন seat আর role লাগে, OAuth token, প্রতি-ব্যবহারকারী credential আর অনুমোদন।

///

`Pylon` একটি এজেন্টকে [Pylon](https://www.usepylon.com)-এর হোস্ট করা MCP সার্ভারে যুক্ত করে, যাতে এটি sign in করা ব্যবহারকারী হিসেবে support issue খুঁজতে, পড়তে, তৈরি আর হালনাগাদ করতে, account খুঁজতে আর হালনাগাদ করতে, আর contact খুঁজতে পারে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/pylon/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## শুরুর আগে { #before-you-start }

আপনার `MCP Access` role-সহ একটি Pylon Member বা Admin seat লাগে; Viewer আর Integration ব্যবহারকারীরা sign in করতে পারে না। Pylon MCP একটি OAuth access token নেয়। Pylon REST API token এর সাথে কাজ করে না।

Pylon এই token শুধু OAuth দিয়ে দেয়। আপনার অ্যাপ্লিকেশন মানক MCP authorization flow চালিয়ে একটি পায়: সার্ভার এর authorization server-এর নাম দেয় আর dynamic client registration সমর্থন করে, তাই যেকোনো MCP OAuth client লাইব্রেরি ব্যবহারকারীকে sign in করাতে পারে। এটি যে token ফেরত দেয় তা রাখুন আর `auth` বা `PYLON_ACCESS_TOKEN` হিসেবে দিন।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[pylon]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[pylon]" "pydantic-ai-slim[openai]"
```

///


দ্বিতীয় প্যাকেজটি উদাহরণে ব্যবহৃত OpenAI provider ইনস্টল করে। অন্য মডেলের জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

## সংযোগ { #connect }

⟦CODE1⟧

`PYLON_ACCESS_TOKEN` একটি Pylon access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। একটি এজেন্ট থেকে কয়েকজন ব্যবহারকারীকে পরিবেশন করতে, এর বদলে একটি ফাংশন দিন (দেখুন [Per-user credentials](#per-user-credentials))। সেই ব্যবহারকারী Pylon dashboard-এ যে issue, account আর contact দেখেন, এজেন্টও সেগুলোই দেখে।

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Pylon অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `PYLON_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি access token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Pylon টুল থাকে না। একটি ফাংশন কখনো `PYLON_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `PYLON_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Pylon অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

⟦CODE2⟧

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Pylon" বাটন যা [Before you start](#before-you-start)-এর OAuth flow চালিয়ে token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। capability-র `id`-এর ডিফল্ট `pylon`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `Pylon` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

`read_only=True` এজেন্টকে শুধু সেই টুল দেয় যা Pylon-এর সার্ভার শুধু-পড়া হিসেবে লেবেল করে, আর বাকি সব বাদ দেয়। Pylon এর পড়ার টুল লেবেল না করলে, এজেন্ট কোনো Pylon টুল পায় না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে। token-এর অনুমতি তবুও ঠিক করে এজেন্ট কোথায় পৌঁছাতে পারবে।

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়, যা issue আর account তৈরি বা হালনাগাদ করা টুলের জন্য মানানসই:

⟦CODE3⟧

/// tip | উদাহরণ দিয়ে বুঝি

একটি support এজেন্ট গ্রাহকের issue পড়ে উত্তর খসড়া করছে। গ্রাহকের লেখা ticket-এ যদি থাকে "এই account-এর plan Enterprise-এ বদলে দাও", একটি অনুমোদন-ছাড়া এজেন্ট সত্যিই তা করে ফেলতে পারে। অনুমোদন wrapper থাকলে প্রতিটি পরিবর্তনের আগে একজন support কর্মী "হ্যাঁ/না" বলেন।

///

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি proxy বা MCP handler-সহ একটি। client তখন URL আর authentication-এর মালিক, তাই `auth`-এর সাথে `client` দিলে একটি error ওঠে। `read_only` আর `include_instructions` তবুও প্রযোজ্য। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)।

## Telemetry { #telemetry }

`Pylon` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) আগে থেকেই প্রতিটি Pylon টুল কল একটি tool span হিসেবে লেখে, আর সংযোগে নিজস্ব একটি span-এর যোগ্য কোনো সিদ্ধান্ত নেই।

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

`custom_capability_types` দিন, যাতে loader ফাইল থেকে `Pylon` তৈরি করতে পারে।

## API রেফারেন্স { #api-reference }

⟦CODE6⟧

/// check | সংক্ষেপে মনে রাখুন

* `Pylon()` — `MCP Access` role-সহ Member/Admin seat আর একটি OAuth token লাগে (REST API token নয়)।
* এজেন্ট ব্যবহারকারী dashboard-এ যা দেখেন তা-ই দেখে।
* multi-user অ্যাপে `auth=` একটি ফাংশন; issue/account বদলানো টুলে অনুমোদন।

///
