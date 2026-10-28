
# Day AI { #day-ai }

/// note | এই পেজে যা শিখবেন

* `DayAI` দিয়ে [Day AI](https://day.ai)-এর হোস্ট করা MCP সার্ভারে যুক্ত হয়ে CRM রেকর্ড খোঁজা ও হালনাগাদ, মিটিংয়ের context পড়া আর ইমেলের খসড়া।
* OAuth token কীভাবে পাবেন, প্রতি-ব্যবহারকারী credential, আর কেন `read_only` অপশন নেই।

///

`DayAI` একটি এজেন্টকে [Day AI](https://day.ai)-এর হোস্ট করা MCP সার্ভারে যুক্ত করে, যাতে এটি sign in করা ব্যবহারকারীর workspace-এ CRM রেকর্ড খুঁজতে ও হালনাগাদ করতে, মিটিংয়ের context পড়তে আর ইমেলের খসড়া করতে পারে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/day_ai/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## শুরুর আগে { #before-you-start }

Day AI MCP-র জন্য একটি পেইড Day AI Agent tier লাগে; আপনার tier আর workspace role-এর টুল ও সীমা প্রযোজ্য। Day AI MCP একটি OAuth access token নেয়; কপি করার মতো কোনো API key নেই।

Day AI এই token শুধু OAuth দিয়ে দেয়। আপনার অ্যাপ্লিকেশন মানক MCP authorization flow চালিয়ে একটি পায়: সার্ভার এর authorization server-এর নাম দেয় আর dynamic client registration সমর্থন করে, তাই যেকোনো MCP OAuth client লাইব্রেরি ব্যবহারকারীকে sign in করাতে পারে। এটি যে token ফেরত দেয় তা রাখুন আর `auth` বা `DAY_AI_ACCESS_TOKEN` হিসেবে দিন।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[day-ai]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[day-ai]" "pydantic-ai-slim[openai]"
```

///


দ্বিতীয় প্যাকেজটি উদাহরণে ব্যবহৃত OpenAI provider ইনস্টল করে। অন্য মডেলের জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

## সংযোগ { #connect }

```python
from pydantic_ai import Agent
from pydantic_ai_harness import DayAI

agent = Agent('openai:gpt-6.1-sol', capabilities=[DayAI()])
result = agent.run_sync('Which Day AI opportunities are in the proposal stage?')
print(result.output)
```

`DAY_AI_ACCESS_TOKEN` একটি Day AI access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। একটি এজেন্ট থেকে কয়েকজন ব্যবহারকারীকে পরিবেশন করতে, এর বদলে একটি ফাংশন দিন (দেখুন [Per-user credentials](#per-user-credentials))।

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Day AI অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `DAY_AI_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি access token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Day AI টুল থাকে না। একটি ফাংশন কখনো `DAY_AI_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `DAY_AI_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Day AI অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai_harness import DayAI


@dataclass
class Deps:
    day_ai_token: str | None


def day_ai_token(ctx: RunContext[Deps]) -> str | None:
    return ctx.deps.day_ai_token


agent = Agent('openai:gpt-6.1-sol', deps_type=Deps, capabilities=[DayAI(auth=day_ai_token)])
```

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Day AI" বাটন যা [Before you start](#before-you-start)-এর OAuth flow চালিয়ে token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। Temporal deps workflow history-তে রাখে, তাই সেখানে token রাখার আগে একটি [payload codec](https://docs.temporal.io/develop/python/converters-and-encryption#custom-payload-codec) দিয়ে history এনক্রিপ্ট করুন।

/// warning | সতর্কতা

Temporal-এ token-সহ `deps` workflow history-তে **সাধারণ লেখা হিসেবে** সংরক্ষিত হয় — Temporal UI বা history দেখার অনুমতি থাকা যে কেউ সেটি পড়তে পারে। প্রোডাকশনে একটি এনক্রিপ্টিং payload codec ব্যবহার করুন।

///

capability-র `id`-এর ডিফল্ট `day_ai`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `DayAI` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

Day AI-এর সার্ভার কোনো টুলকে শুধু-পড়া হিসেবে চিহ্নিত করে না, তাই কোনো `read_only` অপশন নেই: এজেন্ট আপনার tier আর role অনুমতি দেয় এমন প্রতিটি টুল পায়, CRM রেকর্ড বদলানো আর বিজ্ঞপ্তি পাঠানো টুলসহ।

টুলের ফলে আপনার workspace-এর বাইরে লেখা থাকতে পারে, যেমন আগত ইমেল আর মিটিংয়ের নোট, আর সেই লেখা মডেলকে ওই টুল ডাকতে প্ররোচিত করতে পারে। টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়:

```python
from pydantic_ai import Agent, DeferredToolRequests
from pydantic_ai_harness import DayAI

capability = DayAI()
agent = Agent(
    'openai:gpt-6.1-sol',
    toolsets=[capability.get_toolset().approval_required()],
    output_type=[str, DeferredToolRequests],
)
```

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি proxy বা MCP handler-সহ একটি। client তখন URL আর authentication-এর মালিক, তাই `auth`-এর সাথে `client` দিলে একটি error ওঠে। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)।

## Telemetry { #telemetry }

`DayAI` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) আগে থেকেই প্রতিটি Day AI টুল কল একটি tool span হিসেবে লেখে, আর সংযোগে নিজস্ব একটি span-এর যোগ্য কোনো সিদ্ধান্ত নেই।

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


```yaml
# agent.yaml
model: openai:gpt-6.1-sol
capabilities:
  - DayAI: {}
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import DayAI

agent = Agent.from_file('agent.yaml', custom_capability_types=[DayAI])
```

`custom_capability_types` দিন, যাতে loader ফাইল থেকে `DayAI` তৈরি করতে পারে।

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.day_ai.DayAI
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `DayAI()` — পেইড Day AI Agent tier আর একটি OAuth access token (`DAY_AI_ACCESS_TOKEN` বা `auth=`) লাগে; লোকালে `auth='oauth'`।
* কোনো `read_only` নেই — CRM বদলানো টুলও থাকে; অনুমোদন wrapper দিয়ে সুরক্ষিত করুন।
* আগত ইমেল আর মিটিং নোট অবিশ্বস্ত লেখা।
* Temporal-এ deps-এর token এনক্রিপ্ট করতে payload codec।

///
