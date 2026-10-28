
# Grain { #grain }

/// note | এই পেজে যা শিখবেন

* `Grain` দিয়ে [Grain](https://grain.com)-এর হোস্ট করা MCP সার্ভারে যুক্ত হয়ে মিটিং, transcript, নোট আর deal খোঁজা ও পড়া।
* OAuth token, প্রতি-ব্যবহারকারী credential, শুধু-পড়া মোড আর অনুমোদন।

///

`Grain` একটি এজেন্টকে [Grain](https://grain.com)-এর হোস্ট করা MCP সার্ভারে যুক্ত করে। এজেন্ট sign in করা ব্যবহারকারী যে মিটিং, transcript, নোট আর deal দেখতে পারেন সেগুলো খুঁজতে আর পড়তে পারে, আর আপনি `read_only=True` সেট না করলে clip তৈরি আর মিটিং ট্যাগ করতে পারে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/grain/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## শুরুর আগে { #before-you-start }

Grain MCP প্রতিটি Grain plan-এ কাজ করে। deal আর coaching টুলের জন্য Business বা Enterprise plan লাগে।

Grain MCP একটি OAuth access token নেয়, যা Grain শুধু মানক MCP authorization flow দিয়ে দেয়। সার্ভার dynamic client registration সমর্থন করে, তাই যেকোনো MCP OAuth client লাইব্রেরি ব্যবহারকারীকে sign in করাতে পারে। এটি যে token ফেরত দেয় তা `auth` বা `GRAIN_ACCESS_TOKEN` হিসেবে দিন।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[grain]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[grain]" "pydantic-ai-slim[openai]"
```

///


দ্বিতীয় প্যাকেজটি উদাহরণে ব্যবহৃত OpenAI provider ইনস্টল করে। অন্য মডেলের জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

## সংযোগ { #connect }

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Grain

agent = Agent('openai:gpt-6.1-sol', capabilities=[Grain()])
result = agent.run_sync('Summarize my most recent Grain meeting')
print(result.output)
```

`GRAIN_ACCESS_TOKEN` একটি Grain access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। একটি এজেন্ট থেকে কয়েকজন ব্যবহারকারীকে পরিবেশন করতে, এর বদলে একটি ফাংশন দিন (দেখুন [Per-user credentials](#per-user-credentials))।

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Grain অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `GRAIN_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি access token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Grain টুল থাকে না। একটি ফাংশন কখনো `GRAIN_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `GRAIN_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Grain অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai_harness import Grain


@dataclass
class Deps:
    grain_token: str | None


def grain_token(ctx: RunContext[Deps]) -> str | None:
    return ctx.deps.grain_token


agent = Agent('openai:gpt-6.1-sol', deps_type=Deps, capabilities=[Grain(auth=grain_token)])
```

ফাংশনটি প্রতি রানে একবার চলে, তাই প্রতিটি রান এর নিজের deps-এর token দিয়ে যুক্ত হয়।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Grain" বাটন যা [Before you start](#before-you-start)-এর OAuth flow চালিয়ে token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন: ফাংশনটি অন্য process-এ চলতে পারে।

Grain রান শুরু হলেই যুক্ত হয়, `defer_loading=True`-সহও। token অবৈধ বা মেয়াদোত্তীর্ণ হলে, রান status 401-সহ একটি `httpx.HTTPStatusError` তোলে, তাই আপনি জানলে যে token আর বৈধ নয়, ফাংশন থেকে `None` ফেরত দিন।

/// tip | পরামর্শ

একটি মেয়াদোত্তীর্ণ token পুরো রান ব্যর্থ করে (401)। আপনার `auth` ফাংশনে token-এর মেয়াদ যাচাই করুন: মেয়াদ শেষ হলে refresh করুন, আর refresh-ও ব্যর্থ হলে `None` ফেরত দিন — তখন রান Grain টুল ছাড়াই চলে, ভেঙে পড়ে না।

///

capability-র `id`-এর ডিফল্ট `grain`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। এক এজেন্টে দুটি Grain অ্যাকাউন্ট ব্যবহার করতে, প্রতিটি `Grain`-কে নিজের `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই। একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

`read_only=True` এজেন্টকে শুধু সেই টুল দেয় যা Grain-এর সার্ভার শুধু-পড়া হিসেবে লেবেল করে, আর বাকি সব বাদ দেয়। Grain এর পড়ার টুল লেবেল না করলে, এজেন্ট কোনো Grain টুল পায় না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে। token-এর অনুমতি তবুও ঠিক করে এজেন্ট কোথায় পৌঁছাতে পারবে।

transcript আর মিটিংয়ের শিরোনামে মিটিংয়ের সবার লেখা থাকে, বাইরের অতিথিসহ, আর সেই লেখা টুল আউটপুট হিসেবে মডেলে পৌঁছায়। এজেন্টের Grain ডেটা বদলানো উচিত না হলে `read_only=True` ব্যবহার করুন বা অনুমোদন চান। `include_instructions=False` সার্ভারের নিজস্ব instructions এজেন্টে পৌঁছানো বন্ধ করে।

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়, তাই আপনি ঠিক করেন কোন মিটিং ডেটা মডেলে পৌঁছাবে:

```python
from pydantic_ai import Agent
from pydantic_ai.messages import DeferredToolRequests
from pydantic_ai_harness import Grain

capability = Grain()
agent = Agent(
    'openai:gpt-6.1-sol',
    toolsets=[capability.get_toolset().approval_required()],
    output_type=[str, DeferredToolRequests],
)
```

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

নিজে সংযোগ নিয়ন্ত্রণ করতে `client` (একটি FastMCP client বা transport) দিন, যেমন একটি proxy বা MCP handler যোগ করতে। client URL আর authentication-এর মালিক, তাই এটি `auth`-এর সাথে জোড়া যায় না। `read_only` আর `include_instructions` তবুও প্রযোজ্য।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)।

## Telemetry { #telemetry }

`Grain` নিজের কোনো span তৈরি করে না। Core [instrumentation](../capabilities/instrumentation.md) প্রতিটি Grain টুল কল একটি tool span হিসেবে লেখে।

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
  - Grain: {}
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Grain

agent = Agent.from_file('agent.yaml', custom_capability_types=[Grain])
```

`custom_capability_types` দিন, যাতে loader ফাইল থেকে `Grain` তৈরি করতে পারে।

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.grain.Grain
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `Grain()` আর একটি OAuth token (`GRAIN_ACCESS_TOKEN` বা `auth=`); লোকালে `auth='oauth'`।
* রান শুরুতেই যুক্ত হয় — অবৈধ token-এ 401; ফাংশনে মেয়াদ যাচাই করে `None` ফেরত দিন।
* transcript-এ বাইরের অতিথিদের লেখাও থাকে — শুধু পড়তে হলে `read_only=True`।
* deal/coaching টুলের জন্য Business বা Enterprise plan।

///
