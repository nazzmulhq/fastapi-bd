# Notion { #notion }

/// note | এই পেজে যা শিখবেন

* `Notion` দিয়ে Notion-এর হোস্ট করা MCP সার্ভারের মাধ্যমে একটি Notion workspace-এ কনটেন্ট খোঁজা আর বদলানো।
* প্রতি-ব্যবহারকারী OAuth token, কেন integration token কাজ করে না, শুধু-পড়া মোড আর অনুমোদন।

///

একটি এজেন্টকে একটি Notion workspace-এ কনটেন্ট খুঁজতে আর বদলাতে দিন। `Notion` এজেন্টকে Notion-এর হোস্ট করা MCP সার্ভারের দেওয়া প্রতিটি টুল দেয়, পরিবর্তন করা টুলসহ। এজেন্ট যে Notion ব্যবহারকারী হিসেবে যুক্ত হয় তার অনুমতিতে কাজ করে।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল আর সংযোগ { #install-and-connect }

/// tab | pip

```bash
pip install "pydantic-ai-harness[notion]" "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[notion]" "pydantic-ai-slim[openai]"
```

///


`NOTION_ACCESS_TOKEN` একটি Notion OAuth access token-এ সেট করুন, বা `auth=`-এ একটি token দিন। আপনার নিজের মেশিনে, `auth='oauth'` এর বদলে browser দিয়ে আপনাকে sign in করায়। দেখুন [provider setup](https://developers.notion.com/guides/mcp/build-mcp-client)।

```python
from pydantic_ai import Agent
from pydantic_ai_harness.notion import Notion

agent = Agent('openai:gpt-6.1-sol', capabilities=[Notion()])
result = agent.run_sync('Summarize the resources I can access')
print(result.output)
```

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

`auth` ঠিক করে প্রতিটি রান কোন Notion অ্যাকাউন্ট ব্যবহার করে:

| `auth` | ব্যবহৃত অ্যাকাউন্ট |
| --- | --- |
| সেট নয়, `None`, বা `''` | `NOTION_ACCESS_TOKEN`। সেটিও সেট না থাকলে, এজেন্ট তৈরির সময় একটি error ওঠে। |
| একটি access token | সেই token, প্রতিটি রানের জন্য। |
| `'oauth'` | browser দিয়ে আপনি যে অ্যাকাউন্টে sign in করেন। এটি শুধু আপনার নিজের মেশিনে কাজ করে। |
| একটি ফাংশন | প্রতিটি রানের শুরুতে ডাকা হয়, আর async হতে পারে। এর ফেরত দেওয়া token সেই রানের জন্য ব্যবহৃত হয়। এটি `None` বা `''` ফেরত দিলে, সেই রানে কোনো Notion টুল থাকে না। একটি ফাংশন কখনো `NOTION_ACCESS_TOKEN` ব্যবহার করে না, আর `'oauth'` ফেরত দেওয়া চলবে না। |

একটি স্থির token বা `NOTION_ACCESS_TOKEN` একটি script বা আপনার নিজের মেশিনের একটি এজেন্টের জন্য মানানসই, যেখানে প্রতিটি রান একই অ্যাকাউন্ট।

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারী নিজের Notion অ্যাকাউন্ট যুক্ত করেন, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই এজেন্ট তৈরির সময় token স্থির করা যায় না। রানের deps থেকে বর্তমান ব্যবহারকারীর token পড়া একটি ফাংশন দিন:

```python
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.notion import Notion


@dataclass
class Deps:
    notion_token: str | None


def notion_token(ctx: RunContext[Deps]) -> str | None:
    return ctx.deps.notion_token


agent = Agent('openai:gpt-6.1-sol', deps_type=Deps, capabilities=[Notion(auth=notion_token)])
```

প্রতিটি রান নিজের ব্যবহারকারী হিসেবে যুক্ত হয়, তাই একসাথে চলা রান কখনো একটি অ্যাকাউন্ট ভাগ করে না। `read_only` প্রতিটি ব্যবহারকারীর জন্য প্রযোজ্য।

আপনার অ্যাপ প্রতিটি ব্যবহারকারীর token পায়, রাখে আর হালনাগাদ করে। যেমন, একটি "Connect Notion" বাটন যা তাদের Notion OAuth দিয়ে sign in করিয়ে access token তাদের অ্যাকাউন্টে সংরক্ষণ করে। প্রতিটি রানের আগে, এটি deps-এ রাখুন, বা একটি async `auth` ফাংশনে লোড করুন।

Temporal-এর মতো durable execution-এ, credential একটি global থেকে নয়, রানের deps থেকে পড়ুন, কারণ ফাংশনটি অন্য process-এ চলতে পারে। capability-র `id`-এর ডিফল্ট `notion`, তাই একটি ছাড়াই `defer_loading=True` কাজ করে। একটি এজেন্টে একাধিক `Notion` যোগ করতে, প্রতিটিকে একটি আলাদা `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ এদের টুলের নাম একই; একটি `id` ভাগ করা কিন্তু ভিন্ন দুটি একটি error তোলে।

## Provider সেটিং { #provider-settings }

একটি Notion OAuth access token দিয়ে যুক্ত হন। Notion integration token একটি ভিন্ন ধরনের credential আর হোস্ট করা MCP সার্ভারের সাথে কাজ করে না। ব্যবহারকারী কোন পেজ আর টুলে পৌঁছাতে পারবে তা Notion ঠিক করে। কিছু সার্চ আর যুক্ত-উৎসের টুলের জন্য একটি মিলে যাওয়া Notion plan আর অনুমতি লাগে।

/// warning | সাধারণ ভুল

Notion-এর "Internal Integration" পেজ থেকে `secret_...` ধরনের integration token নিয়ে `NOTION_ACCESS_TOKEN`-এ বসানো। হোস্ট করা MCP সার্ভার এটি গ্রহণ করে না — একটি OAuth access token লাগে (লোকালে `auth='oauth'` দিয়ে সহজেই পাওয়া যায়)।

///

## টুল বাছাই আর অনুমোদন { #tool-selection-and-approval }

`read_only=True` শুধু সার্ভার শুধু-পড়া হিসেবে চিহ্নিত করা টুল রাখে। সার্ভার এর পড়ার টুল চিহ্নিত না করলে, এজেন্ট কোনোটি পায় না আর একটি `MCPReadOnlyNoToolsWarning` তৈরি করে। credential-ই তবুও প্রবেশ নিয়ন্ত্রণ করে।

আপনার অ্যাপ্লিকেশনে টুল ছাঁকতে বা অনুমোদন চাইতে, বিদ্যমান [toolset wrappers](../toolsets.md) দিয়ে toolset মুড়ুন। যেমন, এটি প্রতিটি টুল কলের আগে অনুমোদন চায়:

```python
from pydantic_ai import Agent
from pydantic_ai.messages import DeferredToolRequests
from pydantic_ai_harness.notion import Notion

capability = Notion()
agent = Agent(
    'openai:gpt-6.1-sol',
    toolsets=[capability.get_toolset().approval_required()],
    output_type=[str, DeferredToolRequests],
)
```

[deferred tools workflow](../deferred-tools.md) দিয়ে অনুমোদনের অনুরোধ সামলান। টুল আউটপুটের আকার সীমিত করতে, [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## সংযোগ কাস্টমাইজেশন { #connection-customization }

প্রায় সব ক্ষেত্রে `auth` ব্যবহার করুন। `client` দিন শুধু যখন আপনার সংযোগের ওপরই নিয়ন্ত্রণ দরকার: আপনার নিজের FastMCP client বা transport, যেমন একটি ভিন্ন authentication পদ্ধতি, একটি proxy বা MCP handler-সহ একটি। client তখন URL আর authentication-এর মালিক, তাই `auth`-এর সাথে `client` দিলে একটি error ওঠে। `read_only` তবুও প্রযোজ্য। `include_instructions=False` সার্ভারের instructions মডেলে পৌঁছানো বন্ধ করে।

একটি `client` প্রতিটি রানের ভাগ করা একটি সংযোগ; প্রতিটি ব্যবহারকারীকে আলাদাভাবে যুক্ত করতে দেখুন [Per-user credentials](#per-user-credentials)। যে দুটি সংযোগের টুলের নাম মেলে সেগুলো ব্যবহার করতে, এদের আলাদা `id` দিন আর [PrefixTools](../capabilities/prefix-tools.md) যোগ করুন।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/notion/)

/// check | সংক্ষেপে মনে রাখুন

* `Notion()` আর `NOTION_ACCESS_TOKEN` (OAuth token, integration token নয়) বা `auth=`; লোকালে `auth='oauth'`।
* multi-user অ্যাপে `auth=` একটি ফাংশন যা deps থেকে token পড়ে।
* এজেন্ট যুক্ত Notion ব্যবহারকারীর অনুমতিতে কাজ করে; শুধু পড়তে হলে `read_only=True`।

///
