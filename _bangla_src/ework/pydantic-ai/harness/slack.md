
# Slack { #slack }

/// note | এই পেজে যা শিখবেন

* `Slack` দিয়ে Slack-এর হোস্ট করা MCP সার্ভারের মাধ্যমে বার্তা পড়া ও পাঠানো, চ্যানেল দেখা আর canvas নিয়ে কাজ।
* user token (`xoxp-`) বনাম bot token, প্রতি-ব্যবহারকারী credential আর অনুমোদন।

///

একটি এজেন্টকে Slack বার্তা পড়তে আর পাঠাতে, চ্যানেল দেখতে আর canvas নিয়ে কাজ করতে দিন। `Slack` এজেন্টকে Slack-এর হোস্ট করা MCP সার্ভারের দেওয়া প্রতিটি টুল দেয়, পরিবর্তন করা টুলসহ। আপনি যে token দিয়ে যুক্ত হন তা ঠিক করে ওই টুলগুলো কোথায় পৌঁছাতে পারবে।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল আর সংযোগ { #install-and-connect }

/// tab | pip

```bash
pip install "pydantic-ai-harness[slack]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[slack]" "pydantic-ai-slim[openai]"
```

///


`SLACK_USER_TOKEN` একটি Slack user token-এ সেট করুন, বা `auth=`-এ একটি token দিন। দেখুন [provider setup](https://docs.slack.dev/ai/slack-mcp-server/)।

⟦CODE1⟧

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Slack অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `SLACK_USER_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি token | সেই token, প্রতিটি রানের জন্য। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Slack টুল থাকে না। একটি ফাংশন কখনো `SLACK_USER_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `SLACK_USER_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই Slack ব্যবহারকারী।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Slack অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

⟦CODE2⟧

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Slack" বাটন যা তাদের OAuth দিয়ে আপনার Slack app-এ sign in করিয়ে তাদের user token (`xoxp-`) তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

যখন ব্যবহারকারীরা তাদের credential-এর চেয়ে বেশি কিছুতে ভিন্ন, যেমন কিছু ব্যবহারকারীকে শুধু-পড়া প্রবেশ দেওয়া, তখন একটি [dynamic capability](../capabilities/custom.md#dynamically-building-a-capability) দিয়ে প্রতিটি রানের জন্য পুরো capability তৈরি করুন:

⟦CODE3⟧

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। capability-র `id`-এর ডিফল্ট `slack`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `Slack` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## Provider সেটিং { #provider-settings }

Slack-এর হোস্ট করা MCP সার্ভার user token (`xoxp-`) নেয়, bot token (`xoxb-`) নয়। একটি Slack app নিবন্ধন করে Slack-এর MCP ডকুমেন্টেশনের বর্ণনা মতো এর user-token scope দিন।

টুলগুলো token-এর ব্যবহারকারী হিসেবে কাজ করে, তাই এজেন্টের পোস্ট করা বার্তা আর সম্পাদিত canvas সেই ব্যবহারকারী হিসেবে দেখা দেয়। এই capability একটি এজেন্টকে Slack টুল দেয়; এটি Slack বার্তা গ্রহণ করে না বা এগুলো থেকে রান শুরু করে না।

/// tip | উদাহরণ দিয়ে বুঝি

`xoxp-` token হলো "আপনার নিজের হাতে লেখা" — এজেন্ট যা পোস্ট করে তা আপনার নামে দেখায়, যেন আপনিই লিখেছেন। তাই সহকর্মীরা বুঝবে না এটি একটি AI লিখেছে। এজেন্টকে বার্তা পাঠাতে দেওয়ার আগে অনুমোদন চাওয়া বা `read_only=True` বিবেচনা করুন। আর মনে রাখুন: এই capability Slack-এ কেউ এজেন্টকে mention করলে সাড়া দেয় না — সেজন্য আলাদা Slack bot লাগে।

///

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

`read_only=True` শুধু সার্ভার শুধু-পড়া হিসেবে চিহ্নিত করা টুল রাখে। সার্ভার এর পড়ার টুল চিহ্নিত না করলে, এজেন্ট কোনোটি পায় না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে। token-ই তবুও প্রবেশ নিয়ন্ত্রণ করে।

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়:

⟦CODE4⟧

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি ভিন্ন authentication পদ্ধতি, একটি proxy বা MCP handler-সহ একটি। client তখন URL আর authentication-এর মালিক, তাই `auth`-এর সাথে `client` দিলে একটি error ওঠে। `read_only` আর `include_instructions` তবুও প্রযোজ্য। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)। যে দুটি সংযোগের টুলের নাম মেলে সেগুলো ব্যবহার করতে, এদের আলাদা `id` দিন আর [PrefixTools](../capabilities/prefix-tools.md) যোগ করুন।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/slack/)

/// check | সংক্ষেপে মনে রাখুন

* `Slack()` আর `SLACK_USER_TOKEN` (`xoxp-` user token, bot token নয়) বা `auth=`।
* এজেন্ট token-এর ব্যবহারকারী হিসেবে পোস্ট করে; পাঠানোর আগে অনুমোদন বিবেচনা করুন।
* এটি Slack থেকে বার্তা গ্রহণ করে না — শুধু এজেন্টকে Slack টুল দেয়।
* multi-user অ্যাপে `auth=` একটি ফাংশন; ভিন্ন সেটিংয়ের জন্য dynamic capability।

///
