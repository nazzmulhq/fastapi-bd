
# Linear { #linear }

/// note | এই পেজে যা শিখবেন

* `Linear` capability দিয়ে Linear-এর হোস্ট করা MCP সার্ভারের মাধ্যমে issue, project, team আর comment পড়া ও বদলানো।
* প্রতি-ব্যবহারকারী credential (`auth=` ফাংশন), একাধিক সংযোগ, শুধু-পড়ার মোড আর অনুমোদন।

///

Linear-এর হোস্ট করা MCP সার্ভার দিয়ে একটি এজেন্টকে Linear issue, project, team আর comment পড়তে আর বদলাতে দিন। এজেন্ট সার্ভারের দেওয়া প্রতিটি টুল পায়, লেখার টুলসহ, যুক্ত অ্যাকাউন্টের পরিসরে। শুধু পড়ার টুলের জন্য `read_only=True` দিন।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল আর সংযোগ { #install-and-connect }

/// tab | pip

```bash
pip install "pydantic-ai-harness[linear]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[linear]" "pydantic-ai-slim[openai]"
```

///


`LINEAR_ACCESS_TOKEN` একটি Linear API key বা OAuth access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। দেখুন [provider setup](https://linear.app/docs/mcp)।

```python
from pydantic_ai import Agent
from pydantic_ai_harness.linear import Linear

agent = Agent('openai:gpt-6.1-sol', capabilities=[Linear(read_only=True)])
result = agent.run_sync('List my open issues, highest priority first')
print(result.output)
```

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Linear অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `LINEAR_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি API key বা OAuth token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Linear টুল থাকে না। একটি ফাংশন কখনো `LINEAR_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `LINEAR_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Linear অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.linear import Linear


@dataclass
class Deps:
    linear_token: str | None


def linear_token(ctx: RunContext[Deps]) -> str | None:
    return ctx.deps.linear_token


agent = Agent('openai:gpt-6.1-sol', deps_type=Deps, capabilities=[Linear(auth=linear_token)])
```

প্রতিটি রান নিজের সংযোগ খোলে। `read_only=True` তবুও প্রতিটি রানে প্রযোজ্য।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে: ব্যবহারকারীর paste করা একটি Linear API key, বা আপনার নিজের Linear OAuth flow থেকে একটি access token। রানের আগে এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, token একটি global থেকে নয়, রানের deps থেকে পড়ুন: ফাংশনটি অন্য process-এ চলতে পারে।

## একাধিক সংযোগ { #multiple-connections }

capability-র `id`-এর ডিফল্ট `linear`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। `None` বা `''`-সহ এটি তবুও `linear`-এর অধীনে যুক্ত হয়, কিন্তু সেই `Linear` অন্যদের সাথে মেলানো হয় না। এক এজেন্টে দুটি Linear অ্যাকাউন্ট ব্যবহার করতে, প্রতিটি `Linear`-কে নিজের `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই। একই `id` কিন্তু ভিন্ন সেটিংসহ দুটি এজেন্ট তৈরির সময় exception তোলে।

## Provider সেটিং { #provider-settings }

`read_only=True` পূর্ণটির বদলে Linear-এর শুধু-পড়ার endpoint-এ যুক্ত হয়। OAuth token-এর scope প্রবেশ আরও সীমিত করতে পারে।

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

issue-এর বর্ণনা আর comment-এ অন্যদের লেখা থাকে, যেমন সহকর্মী, অতিথি আর গ্রাহকের অনুরোধ sync করে আনা integration, আর সেই লেখা টুল আউটপুট হিসেবে মডেলে পৌঁছায়। এজেন্টের Linear ডেটা বদলানো উচিত না হলে `read_only=True` ব্যবহার করুন বা অনুমোদন চান।

/// tip | উদাহরণ দিয়ে বুঝি

একটি "সাপ্তাহিক রিপোর্ট" এজেন্ট যা শুধু issue পড়ে সারাংশ লেখে — তার লেখার টুল লাগেই না। `Linear(read_only=True)` দিলে এজেন্ট (বা একটি issue-তে লুকানো দুষ্ট নির্দেশনা) ভুল করেও কোনো issue বন্ধ বা মুছতে পারবে না।

///

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়:

```python
from pydantic_ai import Agent
from pydantic_ai.messages import DeferredToolRequests
from pydantic_ai_harness.linear import Linear

capability = Linear()
agent = Agent(
    'openai:gpt-6.1-sol',
    toolsets=[capability.get_toolset().approval_required()],
    output_type=[str, DeferredToolRequests],
)
```

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

নিজে সংযোগ নিয়ন্ত্রণ করতে `client` (একটি FastMCP client বা transport) দিন, যেমন একটি proxy, আরেকটি authentication পদ্ধতি বা MCP handler যোগ করতে। client URL আর authentication-এর মালিক, তাই এটি `auth`-এর সাথে জোড়া যায় না। একটি `client`-সহ, `read_only=True` শুধু সার্ভার শুধু-পড়া হিসেবে চিহ্নিত করা টুল রাখে। কোনোটি চিহ্নিত না থাকলে, এজেন্ট কোনো Linear টুল পায় না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে।

সার্ভারের নিজস্ব instructions, একটি `client`-এর সার্ভারেরগুলোসহ, এজেন্টের instructions-এ যোগ হয়। এগুলো বাদ দিতে `include_instructions=False` দিন।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)। যে দুটি সংযোগের টুলের নাম মেলে সেগুলো ব্যবহার করতে, এদের আলাদা `id` দিন আর [PrefixTools](../capabilities/prefix-tools.md) যোগ করুন।

## Telemetry { #telemetry }

`Linear` নিজের কোনো span তৈরি করে না। Core [instrumentation](../capabilities/instrumentation.md) প্রতিটি Linear টুল কল একটি tool span হিসেবে লেখে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/linear/)

/// check | সংক্ষেপে মনে রাখুন

* `Linear()` আর `LINEAR_ACCESS_TOKEN` (বা `auth=`); লোকালে `auth='oauth'` browser sign-in।
* multi-user অ্যাপে `auth=` একটি ফাংশন যা deps থেকে token পড়ে।
* শুধু পড়তে হলে `read_only=True`; লেখার টুলে অনুমোদন।
* দুটি অ্যাকাউন্ট: আলাদা `id` + `PrefixTools`।

///
