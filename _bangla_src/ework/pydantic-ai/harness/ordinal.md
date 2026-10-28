
# Ordinal { #ordinal }

/// note | এই পেজে যা শিখবেন

* `Ordinal` দিয়ে [Ordinal](https://www.tryordinal.com)-এর হোস্ট করা MCP সার্ভারে সোশ্যাল পোস্টের খসড়া, নির্ধারণ আর বিশ্লেষণ।
* OAuth token, পুরনো সার্ভার সরানো, প্রতি-ব্যবহারকারী credential আর প্রকাশের আগে অনুমোদন।

///

`Ordinal` একটি এজেন্টকে [Ordinal](https://www.tryordinal.com)-এর হোস্ট করা MCP সার্ভারে যুক্ত করে, যাতে এটি sign in করা ব্যবহারকারীর workspace-এ সোশ্যাল পোস্টের খসড়া, নির্ধারণ আর বিশ্লেষণ করতে পারে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/ordinal/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## শুরুর আগে { #before-you-start }

Ordinal MCP-র জন্য Pro plan বা তার ওপরে লাগে, REST API-র মতোই। আপনার অন্তত একটি workspace-এ প্রবেশসহ একটি Ordinal অ্যাকাউন্ট লাগে। Ordinal MCP একটি OAuth access token নেয়; কপি করার মতো কোনো API key নেই।

Ordinal এই token শুধু OAuth দিয়ে দেয়। আপনার অ্যাপ্লিকেশন মানক MCP authorization flow চালিয়ে একটি পায়: সার্ভার এর authorization server-এর নাম দেয় আর dynamic client registration সমর্থন করে, তাই যেকোনো MCP OAuth client লাইব্রেরি ব্যবহারকারীকে sign in করাতে পারে। এটি যে token ফেরত দেয় তা রাখুন আর `auth` বা `ORDINAL_ACCESS_TOKEN` হিসেবে দিন।

আপনি যদি একটি workspace API key দিয়ে `https://app.tryordinal.com/api/mcp`-এ পুরনো সার্ভার সেটআপ করে থাকেন, সেটি সরিয়ে দিন। পুরনো আর নতুন সার্ভার একসাথে ব্যবহার করবেন না, কারণ এদের নকল টুলের নাম এজেন্টকে বিভ্রান্ত করে।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[ordinal]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[ordinal]" "pydantic-ai-slim[openai]"
```

///


দ্বিতীয় প্যাকেজটি উদাহরণে ব্যবহৃত OpenAI provider ইনস্টল করে। অন্য মডেলের জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

## সংযোগ { #connect }

⟦CODE1⟧

`ORDINAL_ACCESS_TOKEN` একটি Ordinal access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। একটি এজেন্ট থেকে কয়েকজন ব্যবহারকারীকে পরিবেশন করতে, এর বদলে একটি ফাংশন দিন (দেখুন [Per-user credentials](#per-user-credentials))। তারপর workspace তালিকা করে শুরু করুন। অন্য প্রতিটি Ordinal টুলের `ordinal_get_workspace_context` থেকে একটি `workspaceSlug` লাগে।

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Ordinal অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `ORDINAL_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি access token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Ordinal টুল থাকে না। একটি ফাংশন কখনো `ORDINAL_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `ORDINAL_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Ordinal অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

⟦CODE2⟧

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Ordinal" বাটন যা [Before you start](#before-you-start)-এর OAuth flow চালিয়ে token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। capability-র `id`-এর ডিফল্ট `ordinal`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `Ordinal` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়, যা পোস্ট প্রকাশ বা নির্ধারণ করা টুলের জন্য মানানসই:

⟦CODE3⟧

/// warning | সাধারণ ভুল

একটি সোশ্যাল মিডিয়া এজেন্টকে অনুমোদন ছাড়া প্রকাশের টুল দেওয়া। একটি ভুল টোন, ভুল তথ্য বা একটি ভুল সময়ে নির্ধারিত পোস্ট সরাসরি আপনার ব্র্যান্ডের পাবলিক অ্যাকাউন্টে চলে যায় — আর মুছলেও screenshot থেকে যায়। প্রকাশ আর নির্ধারণের আগে সবসময় একজন মানুষের অনুমোদন রাখুন।

///

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি proxy বা MCP handler-সহ একটি। client তখন URL আর authentication-এর মালিক, তাই `auth`-এর সাথে `client` দিলে একটি error ওঠে। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)।

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

`custom_capability_types` দিন, যাতে loader ফাইল থেকে `Ordinal` তৈরি করতে পারে।

## API রেফারেন্স { #api-reference }

⟦CODE6⟧

/// check | সংক্ষেপে মনে রাখুন

* `Ordinal()` — Pro plan আর একটি OAuth token (`ORDINAL_ACCESS_TOKEN` বা `auth=`) লাগে।
* পুরনো workspace-API-key সার্ভারের সাথে একসাথে ব্যবহার করবেন না।
* প্রথমে `ordinal_get_workspace_context` থেকে `workspaceSlug`।
* প্রকাশ/নির্ধারণের আগে অনুমোদন রাখুন।

///
