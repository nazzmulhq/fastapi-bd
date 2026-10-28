
# DBOS দিয়ে Durable Execution { #durable-execution-with-dbos }

/// note | এই পেজে যা শিখবেন

* DBOS কী: একটি হালকা লাইব্রেরি, যা আপনার process-এর ভেতরেই চলে আর state Postgres/SQLite-এ রাখে।
* `DBOSDurability` দিয়ে এজেন্টকে durable করা — আর কেন `agent.run()`-কে নিজের `@DBOS.workflow`-এ মোড়াতে হয়।
* ফাংশন টুল কেন নিজে থেকে step হয় না, আর কখন `@DBOS.step` দেবেন।
* streaming, timeout, সমান্তরাল টুল, step কনফিগারেশন আর retry।

///

[DBOS](https://www.dbos.dev/) একটি হালকা [durable execution](https://docs.dbos.dev/architecture) লাইব্রেরি, যা Pydantic AI-এর সাথে নেটিভভাবে যুক্ত।

## Durable Execution { #durable-execution }

DBOS workflow একটি ডেটাবেসে আপনার প্রোগ্রামের state চেকপয়েন্ট করে প্রোগ্রামকে **durable** করে। আপনার প্রোগ্রাম কখনো ব্যর্থ হলে, আবার শুরু হওয়ার সময় আপনার সব workflow নিজে থেকে শেষ সম্পন্ন step থেকে আবার চলবে।

* **Workflow** অবশ্যই deterministic হতে হবে আর সাধারণত I/O রাখতে পারে না।
* **Step** I/O করতে পারে (নেটওয়ার্ক, ডিস্ক, API কল)। একটি step ব্যর্থ হলে, এটি শুরু থেকে আবার চলে।

প্রতিটি workflow input আর step output system database-এ টেকসইভাবে রাখা হয়। workflow execution ব্যর্থ হলে, crash, নেটওয়ার্ক সমস্যা বা সার্ভার restart যা থেকেই হোক, DBOS এই চেকপয়েন্টগুলো কাজে লাগিয়ে workflow-কে তাদের শেষ সম্পন্ন step থেকে উদ্ধার করে।

DBOS **queue** Celery বা BullMQ-এর মতো সিস্টেমের টেকসই, ডেটাবেস-ভিত্তিক বিকল্প দেয়, concurrency সীমা, rate সীমা, timeout আর অগ্রাধিকারের মতো সুবিধা সমর্থন করে। বিস্তারিত দেখুন [DBOS ডক](https://docs.dbos.dev/architecture)-এ।

নিচের diagram DBOS-এ একটি agentic অ্যাপ্লিকেশনের সামগ্রিক architecture দেখায়।
DBOS একটি লাইব্রেরি হিসেবে পুরোপুরি process-এর ভেতরে চলে। ফাংশনগুলো সাধারণ Python ফাংশনই থাকে, কিন্তু একটি ডেটাবেসে (Postgres বা SQLite) চেকপয়েন্ট হয়।

```text
                    Clients
            (HTTP, RPC, Kafka, etc.)
                        |
                        v
+------------------------------------------------------+
|               Application Servers                    |
|                                                      |
|   +----------------------------------------------+   |
|   |        Pydantic AI + DBOS Libraries          |   |
|   |                                              |   |
|   |  [ Workflows (Agent Run Loop) ]              |   |
|   |  [ Steps (Tool, MCP, Model) ]                |   |
|   |  [ Queues ]   [ Cron Jobs ]   [ Messaging ]  |   |
|   +----------------------------------------------+   |
|                                                      |
+------------------------------------------------------+
                        |
                        v
+------------------------------------------------------+
|                      Database                        |
|   (Stores workflow and step state, schedules tasks)  |
+------------------------------------------------------+
```

আরও তথ্যের জন্য দেখুন [DBOS ডকুমেন্টেশন](https://docs.dbos.dev/architecture)।

/// tip | উদাহরণ দিয়ে বুঝি

Temporal-এর জন্য আলাদা একটি সার্ভার চালাতে হয়; DBOS-এর জন্য শুধু একটি ডেটাবেস লাগে, যা হয়তো আপনার আগে থেকেই আছে। এটি অনেকটা একটি "স্বয়ংক্রিয় ডায়েরি" — আপনার কোড যেভাবে চলত সেভাবেই চলে, শুধু প্রতিটি step-এর ফল ডেটাবেসে লেখা হয়ে যায়। crash-এর পর DBOS ডায়েরি পড়ে বলে, "step 1-3 শেষ, এই নাও তাদের ফল; step 4 থেকে আবার চালাও।"

///

## Durable এজেন্ট { #durable-agent }

যেকোনো [`Agent`][pydantic_ai.agent.Agent]-এ durable execution যোগ করুন [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability] [capability](../capabilities/overview.md) যুক্ত করে। এজেন্টটি একটি DBOS workflow-এর ভেতরে চললে, capability-টি [মডেল রিকোয়েস্ট](../models/overview.md) আর [MCP যোগাযোগ](../mcp/client.md) DBOS step দিয়ে পাঠায়। একটি রান durable করতে, একটি `@DBOS.workflow`-এর ভেতরে `agent.run()` ডাকুন।

এজেন্টটি সব জায়গায় একটি সাধারণ `Agent` থাকে — একটি DBOS workflow-এর বাইরে capability স্বচ্ছ, আর মূল এজেন্ট, মডেল আর MCP সার্ভার এখনও স্বাভাবিকভাবে ব্যবহার করা যায়।

এজেন্টে সরাসরি বা অন্য একটি capability দিয়ে নিবন্ধিত নিজস্ব টুল ফাংশন আর event stream handler DBOS **নিজে থেকে মোড়ায় না**। `DBOSDurability`-তে দেওয়া একটি `event_stream_handler=` একটি DBOS step-এর ভেতরে চলে আর লাইভ-stream করা event পায়।
এগুলো non-deterministic আচরণ করলে বা I/O করলে, আপনার উচিত এদের স্পষ্টভাবে `@DBOS.step` দিয়ে decorate করা।

একটি এজেন্টে durable execution যুক্ত করার একটি সহজ কিন্তু সম্পূর্ণ উদাহরণ এখানে। এর জন্য শুধু DBOS [ওপেন-সোর্স লাইব্রেরি](https://github.com/dbos-inc/dbos-transact-py)-সহ Pydantic AI ইনস্টল করতে হয়:

/// tab | pip

```bash
pip install pydantic-ai[dbos]
```

///

/// tab | uv

```bash
uv add pydantic-ai[dbos]
```

///


অথবা slim প্যাকেজ ব্যবহার করলে, `dbos` optional group দিয়ে ইনস্টল করতে পারেন:

/// tab | pip

```bash
pip install pydantic-ai-slim[dbos]
```

///

/// tab | uv

```bash
uv add pydantic-ai-slim[dbos]
```

///


এরপর, নিচের উদাহরণ কোড চালান:

```python title="dbos_durability.py"
from dbos import DBOS, DBOSConfig

from pydantic_ai import Agent
from pydantic_ai.durable_exec.dbos import DBOSDurability

dbos_config: DBOSConfig = {
    'name': 'pydantic_dbos_agent',
    'system_database_url': 'sqlite:///dbostest.sqlite',  # (1)!
}
DBOS(config=dbos_config)

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions="You're an expert in geography.",
    name='geography',  # (2)!
    capabilities=[DBOSDurability()],  # (3)!
)


@DBOS.workflow()  # (4)!
async def answer(question: str) -> str:
    result = await agent.run(question)
    return result.output


async def main():
    DBOS.launch()
    answer_text = await answer('What is the capital of Mexico?')
    print(answer_text)
    #> Mexico City (Ciudad de México, CDMX)
```

1. এই উদাহরণ SQLite ব্যবহার করে। প্রোডাকশনের জন্য Postgres সুপারিশকৃত।
2. এজেন্টের `name` এর workflow-গুলোকে অনন্যভাবে চিহ্নিত করতে ব্যবহৃত হয়।
3. `capabilities=[...]` দিয়ে durability যুক্ত করুন। এজেন্ট একটি workflow-এর ভেতরে চললে capability-টি মডেল রিকোয়েস্ট আর MCP যোগাযোগ DBOS step দিয়ে পাঠায়। যেহেতু DBOS workflow `DBOS.launch()`-এর আগে নিবন্ধিত হতে হয়, এজেন্টকেও `DBOS.launch()` ডাকার আগে তৈরি করতে হবে।
4. রানটি durable করতে `agent.run()`-কে আপনার নিজের `@DBOS.workflow`-এ মোড়ান।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// warning | সাধারণ ভুল

`DBOSDurability()` যোগ করে সরাসরি `await agent.run(...)` ডাকা। এটি কাজ করে, কিন্তু **durable নয়** — কারণ রানটি কোনো `@DBOS.workflow`-এর ভেতরে নেই। durability পেতে রানটিকে নিজের একটি `@DBOS.workflow` ফাংশনে রাখুন আর সেই ফাংশনটি ডাকুন।

///

যেহেতু একই এজেন্ট একটি DBOS workflow-এর ভেতরে আর বাইরে কাজ করে, [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability] অন্য সব [capability](../capabilities/overview.md)-র সাথে মিলে যায়, প্রতিটির জন্য একটি DBOS-নির্দিষ্ট wrapper রূপ ছাড়াই।

Python অ্যাপ্লিকেশনে DBOS কীভাবে ব্যবহার করবেন তার আরও তথ্যের জন্য, দেখুন তাদের [Python SDK guide](https://docs.dbos.dev/python/programming-guide)।

### Wrapper-agent পথ (অবচিত) { #wrapper-agent-path-deprecated }

/// warning | অবচিত (Deprecated)

[`DBOSAgent`][pydantic_ai.durable_exec.dbos.DBOSAgent] হলো DBOS ইন্টিগ্রেশনের মূল wrapper-agent পথ, যা v3-এ সরানো হবে। নতুন কোডে ওপরে দেখানো [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability] capability ব্যবহার করা উচিত।

**migrate করার সময়, রানটি আপনাকে নিজে একটি workflow-এ মোড়াতে হবে।** `DBOSAgent` `run` / `run_sync`-কে নিজে থেকে একটি DBOS workflow হিসেবে মোড়াত; `DBOSDurability` ইচ্ছে করে তা করে না — একটি রান শুধু তখনই durable যখন আপনার নিজের `@DBOS.workflow`-এর ভেতরে `agent.run()` ডাকা হয়। constructor আর্গুমেন্ট নিয়ে এসে কিন্তু সরাসরি `agent.run()` ডাকলে এমন একটি রান তৈরি হয় যা কাজ করে কিন্তু **durable নয়**।

migration-এর সময় চলমান wrapper-যুগের workflow উদ্ধার করতে, [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-তে `register_legacy_workflows=True` চালু করুন আর deploy জুড়ে DBOS `application_version` pin করুন (version gating যেকোনো DBOS কোড পরিবর্তনে প্রযোজ্য)। ওই workflow-গুলো শেষ হয়ে গেলে flag-টি সরিয়ে দিন।

///

যেকোনো এজেন্টকে একটি [`DBOSAgent`][pydantic_ai.durable_exec.dbos.DBOSAgent]-এ মোড়ানো যায়, এমন একটি durable এজেন্ট রূপ পেতে যা মডেল রিকোয়েস্ট আর MCP যোগাযোগ DBOS step দিয়ে পাঠায়:

```python title="dbos_agent.py"
from pydantic_ai import Agent
from pydantic_ai.durable_exec.dbos import DBOSAgent

agent = Agent('openai:gpt-6.1-sol', name='geography')
dbos_agent = DBOSAgent(agent)  # Use `dbos_agent` in place of `agent`.
```

capability-তে migrate করা মানে `DBOSDurability` যুক্ত করা আর সেই workflow decorator যোগ করা যা `DBOSAgent` আপনার জন্য প্রয়োগ করত:

```diff
-dbos_agent = DBOSAgent(agent)
-result = await dbos_agent.run(prompt)
+agent = Agent(..., capabilities=[DBOSDurability()])
+
+@DBOS.workflow()
+async def answer(prompt: str) -> str:
+    result = await agent.run(prompt)
+    return result.output
```

## DBOS ইন্টিগ্রেশনের বিবেচনা { #dbos-integration-considerations }

Pydantic AI এজেন্টের সাথে DBOS ব্যবহারের সময়, workflow আর toolset ঠিকভাবে আচরণ করছে তা নিশ্চিত করতে কয়েকটি জরুরি বিবেচনা আছে।

### এজেন্ট আর toolset-এর প্রয়োজনীয়তা { #agent-and-toolset-requirements }

প্রতিটি এজেন্ট instance-এর একটি অনন্য `name` থাকতে হবে, যাতে DBOS একটি ব্যর্থতা বা restart-এর পর workflow ঠিকভাবে আবার চালাতে পারে।

প্রতিটি [`MCPToolset`][pydantic_ai.mcp.MCPToolset]-এর একটি অনন্য [`id`][pydantic_ai.toolsets.AbstractToolset.id] থাকতে হবে, কারণ DBOS এর step নাম আর প্রতি-রান tool-defs cache key এটি থেকে তৈরি করে। এই ফিল্ড সাধারণত ঐচ্ছিক, কিন্তু DBOS ব্যবহারের সময় বাধ্যতামূলক, আর `id` ছাড়া একটি URL toolset যে hostname-কে `id` হিসেবে নেয় তা গণ্য হয় না। durable এজেন্ট প্রোডাকশনে deploy হওয়ার পর এটি বদলানো উচিত নয়, কারণ তাতে সক্রিয় workflow ভেঙে যাবে।

MCP টুল I/O করে আর সবসময় তাদের DBOS step-এ চলে। একটি টুলের `metadata={'dbos': False}` সেট করা workflow কোডে MCP কল inline চালানোর বদলে প্রত্যাখ্যাত হয়।

একটি MCP সার্ভার প্রতি step-এ একবারের বদলে প্রতি workflow-এ একবার সংযুক্ত হয়: যে প্রথম step-এর এটি দরকার সেটি এটি সংযুক্ত করে — একটি step-এর ভেতরে, তাই DBOS একটি ব্যর্থ সংযোগ অন্য যেকোনো step ব্যর্থতার মতো retry করে — আর রান শেষ না হওয়া পর্যন্ত workflow session ধরে রাখে। টুল খোঁজা তবুও এর `get_tools` step চালায়, আর এটি চলবে কিনা তা ঠিক হয় রানের নিজের লেখা ইতিহাস দিয়ে, একটি গরম process ঘটনাক্রমে কী ধরে রাখে তা দিয়ে নয়, তাই উদ্ধারের সময় step-এর ক্রম একই থাকে; সার্ভারের নিজস্ব
[`cache_tools`][pydantic_ai.mcp.MCPToolset.cache_tools] তখন রান ইতিমধ্যে যে session ধরে রেখেছে তা থেকে ওই step-গুলোর উত্তর দেয়, আরেকটি round trip ছাড়াই। এক process-এ একসাথে চলা রানগুলো একটি সার্ভারের session ভাগ করে, যেমন workflow-এর বাইরে করে, আর শেষটি শেষ হলে এটি বন্ধ হয়।

[`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset], একটি [`DynamicCapability`][pydantic_ai.capabilities.DynamicCapability]-এর দেওয়াগুলোসহ, মোড়ানো হয় আর একটি স্থিতিশীল `id` লাগে। টুল খোঁজা, আর্গুমেন্ট যাচাই আর কল চলে `{name}__dynamic_toolset__{id}.get_tools`, `{name}__dynamic_toolset__{id}.validate_args` আর `{name}__dynamic_toolset__{id}.call_tool` step হিসেবে। একটি টুলের [`args_validator`](../tools-advanced.md#args-validator) `validate_args` step-এ চলে, যা `call_tool`-এর মতো toolset আবার মীমাংসা করে; একটি ছাড়া টুল কোনো যাচাই step নির্ধারণ করে না। যাচাই চলে [অনুমোদন আর deferral](../deferred-tools.md)-এর আগে, তাই প্রত্যাখ্যাত আর্গুমেন্ট কখনো একজন অনুমোদনকারীর কাছে পৌঁছায় না। dynamic toolset-এর সব I/O — MCP যোগাযোগসহ — ওই step-গুলোর ভেতরে ঘটে, তাই এটি চেকপয়েন্ট হয়। factory `per_run_step=False` দিয়ে তৈরি হলে, রান toolset একবার মীমাংসা করে আর প্রতিটি step এটি পুনর্ব্যবহার করে, প্রথম যে step-এর এটি দরকার তখন এতে প্রবেশ করে আর রানের বাকি সময় প্রবেশ করা অবস্থায় রাখে। একটি toolset তৈরি করা আর এটি সংযুক্ত করা এক নয় — একটি `MCPToolset` প্রবেশ না করা পর্যন্ত কিছুই খোলে না — তাই সংযোগ একটি step-এর ভেতরে ঘটে, যেখানে এটি অন্য যেকোনো step ব্যর্থতার মতো retry হয়। factory নিজে workflow কোডে চলে আর যখনই সেটি replay হয় আবার চলে, তাই নিচের capability factory-র মতো রানের `deps` দেওয়া থাকলে এটিকে deterministic হতে হবে: factory-তে toolset তৈরি করুন আর এর I/O step-এর জন্য রাখুন। এটি সেই lifecycle যা একটি non-durable রান toolset-কে দেয়, তাই একটি toolset-এর নিজস্ব caching — যেমন factory-র ফেরত দেওয়া একটি `MCPToolset`-এ [`cache_tools`][pydantic_ai.mcp.MCPToolset.cache_tools] — step-এর মাঝে ফেলে না দিয়ে workflow-এর বাইরের মতোই কাজ করে। একটি `per_run_step=True` factory প্রতিটি step-এর ভেতরে আবার মীমাংসা হয়, যেমন এটি চায়। একটি `DynamicCapability`-এর জন্য, DBOS ওই step-গুলোর ভেতরে রানের জন্য মীমাংসা করা capability পুনর্ব্যবহার করে। capability factory নিজে workflow কোডে চলে আর একটি workflow উদ্ধার হলে আবার চলে, তাই সব workflow কোডের মতো রানের `deps` দেওয়া থাকলে এটিকে deterministic হতে হবে: factory-তে toolset তৈরি করুন আর এর I/O step-এর জন্য রাখুন।

একটি [capability](../capabilities/overview.md)-র দেওয়া একটি toolset — `tools=`-সহ একটি [`Capability`][pydantic_ai.capabilities.Capability], বা লোকালে চলা একটি [`MCP`][pydantic_ai.capabilities.MCP] সার্ভার — এর `id` capability-র নিজের [`id`][pydantic_ai.capabilities.AbstractCapability.id] থেকে তৈরি করে, তাই `Capability(id='...', tools=[...])` বা `MCP(id='...', url='...')` সেট করুন। একটি `MCP` এর `id` অগ্রাধিকার ক্রমে মীমাংসা করে: একটি স্পষ্ট `id=`, তারপর একটি `native=MCPServerTool(...)` id, তারপর সার্ভার URL-এর hostname। এক host-এ দুটি `MCP` capability প্রত্যাখ্যাত হয়, তাই প্রতিটিকে একটি স্পষ্ট `id` দিন। এগুলোর কোনোটি ছাড়া একটি খালি non-URL লোকাল client (যেমন `MCP(local=Path(...))`) id-হীন থাকে আর এখানে ব্যবহার করতে একটি স্পষ্ট `id` দিতে হবে।

এজেন্টে সরাসরি বা অন্য একটি capability দিয়ে নিবন্ধিত ফাংশন টুল আর event stream handler DBOS নিজে থেকে মোড়ায় না। `DBOSDurability`-তে দেওয়া একটি `event_stream_handler=` একটি DBOS step-এর ভেতরে চলে আর লাইভ-stream করা event পায়। সরাসরি নিবন্ধিত টুল আর handler-এর জন্য, আপনি ঠিক করতে পারেন কীভাবে যুক্ত করবেন:

* ফাংশনে non-determinism বা I/O থাকলে `@DBOS.step` দিয়ে decorate করুন।
* durability দরকার না হলে decorator বাদ দিন, যাতে বাড়তি DB চেকপয়েন্ট লেখা এড়ানো যায়।
* ফাংশনটির task enqueue করতে বা অন্য DBOS workflow ডাকতে হলে, এটি এজেন্টের মূল workflow-এর ভেতরে চালান (একটি step হিসেবে নয়)।

/// info | এক নজরে: টুল ফাংশনে কোনটি?

| টুল কী করে | কী করবেন |
|-----------|---------|
| বাইরের API ডাকে, ডেটাবেসে লেখে, র‍্যান্ডম সংখ্যা/সময় পড়ে | `@DBOS.step` দিন — ফল চেকপয়েন্ট হবে, replay-তে আবার চলবে না |
| শুধু হিসাব করে (deterministic, I/O নেই) | decorator দরকার নেই — বাড়তি DB লেখা এড়ান |
| অন্য DBOS workflow শুরু করে বা queue-তে কাজ দেয় | step বানাবেন না; মূল workflow-এ চলতে দিন |

///

অন্য সব এজেন্ট আর toolset সমর্থিত।

### এজেন্ট রান context আর dependency { #agent-run-context-and-dependencies }

ডিফল্টভাবে, DBOS workflow input/output আর step output একটি ডেটাবেসে [`pickle`](https://docs.python.org/3/library/pickle.html) দিয়ে চেকপয়েন্ট করে। তবে আপনি চাইলে DBOS কনফিগারেশন দিয়ে একটি [custom serializer](https://docs.dbos.dev/python/reference/contexts#custom-serialization) দিতে পারেন। এর মানে আপনাকে নিশ্চিত করতে হবে যে [`Agent.run()`][pydantic_ai.agent.Agent.run] / [`Agent.run_sync()`][pydantic_ai.agent.Agent.run_sync]-এ দেওয়া [dependencies](../dependencies.md) অবজেক্ট আর টুলের আউটপুট serialize করা যায়।
আপনি হয়তো input আর output ছোটও রাখতে চাইবেন (\~2 MB-এর নিচে)। PostgreSQL আর SQLite প্রতি ফিল্ডে 1 GB পর্যন্ত সমর্থন করে, কিন্তু বড় অবজেক্ট পারফরম্যান্সে প্রভাব ফেলতে পারে।

একটি workflow-এ [`Agent.run()`][pydantic_ai.agent.Agent.run]-এ `run_id` বা `conversation_id` না দিলে, ডিফল্টগুলো র‍্যান্ডমভাবে তৈরি না হয়ে workflow ID থেকে তৈরি হয়, তাই একটি উদ্ধার হওয়া workflow তার সম্পন্ন step-গুলোর আগেই দেখা ID রাখে।

### Workspace { #workspaces }

এজেন্ট তৈরির সময় [workspace](../workspace.md) capability যুক্ত করুন, যেমন `LocalWorkspace`, আর যেকোনো রানের মতো `ctx.workspace` ব্যবহার করুন। workflow কোডে করা প্রতিটি workspace কল, ফাংশন টুল থেকে করাগুলোসহ (যা DBOS workflow-এ চালায়), একটি step, তাই ফাইলের কনটেন্ট আর কমান্ডের আউটপুট [ওপরের আকার-নির্দেশনা](#agent-run-context-and-dependencies)-র মধ্যে গোনা হয়।

DBOS workflow-পক্ষের workspace কলের আর্গুমেন্ট (কমান্ড, `env=`, ফাইলের কনটেন্ট) ইতিহাসে রাখে।
secret workspace কলে না দিয়ে workspace capability-র `env=`-এ রাখুন;
ফাংশন টুল থেকে কলও workflow-এ চলে, তাই তাদের আর্গুমেন্টও সংরক্ষিত হয়। একটি উপযুক্ত payload codec দিয়ে সংরক্ষিত ইতিহাস সুরক্ষিত করুন।

একটি এজেন্টে workspace যোগ করা এর workflow-এর step বদলায়, তাই চলমান workflow শেষ হতে দিন বা
পরিবর্তনটি একটি নতুন application version হিসেবে deploy করুন; এর আগে শুরু হওয়া একটি workflow DBOS উদ্ধার করতে পারে না।

### রানের সময় মডেল বাছাই { #model-selection-at-runtime }

[`Agent.run(model=...)`][pydantic_ai.agent.Agent.run] মডেল string (যেমন `'openai:gpt-6.1-sol'`) আর মডেল instance দুটোই সমর্থন করে। একটি মডেল instance step সীমা পেরিয়ে serialize করা যায় না, আর এর `model_id` string থেকে একটি আবার তৈরি করলে একটি *ভিন্ন* মডেল তৈরি হবে — worker-এর environment যে provider বোঝায় তাতে একই মডেলের নাম, তাই রিকোয়েস্ট অন্য credential নিয়ে অন্য endpoint-এ যাবে। তাই আগে থেকে নিবন্ধিত নয় এমন একটি instance একটি `UserError` দিয়ে প্রত্যাখ্যাত হয়। একটি নির্দিষ্ট instance ব্যবহারের দুটি উপায় আছে: [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-তে একটি `models` dict দিয়ে এটি আগে নিবন্ধন করে key দিয়ে রেফারেন্স দিন (বা নিবন্ধিত instance দিন), বা একটি মডেল-নামের string দিন আর একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability দিয়ে step-এর ভেতরে instance তৈরি করুন — সঠিক পছন্দ যখন মডেল রানের `deps`-এর ওপর নির্ভর করে, যেমন প্রতি-ব্যবহারকারী credential। মডেল-নামের string নিজে কখনো নিবন্ধন করতে হয় না। তৈরির সময় সেট করা এজেন্টের নিজের মডেল সবসময় ডিফল্ট হিসেবে উপলব্ধ।

একটি মডেল string কীভাবে তৈরি হবে তা কাস্টমাইজ করতে — একটি নিজস্ব provider, বা রানের `deps`-এ বহন করা প্রতি-ব্যবহারকারী credential — `DBOSDurability`-র আগে একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability যোগ করুন: এটি প্রতিটি string-এ প্রথম সুযোগ পায়, আর resolver রানের আসল `deps` দিয়ে step-এর ভেতরে আবার চলে, তাই এটিকে একটি নির্দিষ্ট `(model_id, deps)`-এর জন্য deterministic হতে হবে আর বাইরের I/O করা চলবে না।

### রানের সময় capability { #capabilities-at-runtime }

এজেন্ট তৈরির সময় [capability](../capabilities/overview.md) যুক্ত করুন, যাতে অ্যাপ্লিকেশন শুরুর আগে `DBOSDurability.for_agent()` তাদের step নিবন্ধন করতে পারে। একটি workflow-এর ভেতরে `agent.run(capabilities=[...])` দিলে একটি `UserError` ওঠে: এত দেরিতে যোগ করা একটি capability-র দেওয়া toolset বা এর নিজের [`@durable_operation`][pydantic_ai.capabilities.durable_operation] মেথডের জন্য কোনো নিবন্ধিত step নেই।

যে capability শুধু রান পর্যবেক্ষণ করে সেগুলো প্রতি-রানে যুক্ত করা নিরাপদ: তাদের hook রান state পড়ে কিন্তু টুল, toolset বা durable operation দেয় না। [`Instrumentation`][pydantic_ai.capabilities.Instrumentation] হলো বিল্ট-ইন উদাহরণ আর বাধা থেকে মুক্ত। বর্তমান বাধা বেশি রক্ষণশীল, কারণ থার্ড-পার্টি capability এখনও ঘোষণা করতে পারে না যে তারা শুধু রান পর্যবেক্ষণ করে। একটি capability কোন hook override করে তা থেকে এটি বের করা ট্র্যাক হচ্ছে [#5477](https://github.com/pydantic/pydantic-ai/issues/5477)-এ; একটি workflow-এর ভেতরে প্রতি-রান capability দরকার হলে, দয়া করে সেখানে আপনার ব্যবহারের ক্ষেত্র জানান। একটি workflow-এর বাইরে durability capability স্বচ্ছ, তাই সেখানে প্রতি-রান capability ঠিক আছে।

### Streaming { #streaming }

[`Agent.run_stream()`][pydantic_ai.agent.Agent.run_stream] আর [`Agent.run_stream_events()`][pydantic_ai.agent.Agent.run_stream_events] একটি DBOS workflow-এর ভেতরে কাজ করে, কিন্তু তাদের event সাথে সাথে পৌঁছানোর বদলে জমা হয়। মডেল stream durable step-এর ভেতরে চলে, আর step শেষ হলে workflow এর চূড়ান্ত response replay করে: প্রতিটি অংশ মডেলের stream করা delta হিসেবে নয়, বরং এর পুরো কনটেন্টসহ একটি [`PartStartEvent`][pydantic_ai.messages.PartStartEvent] হিসেবে আসে, তাই delta-গুলো step-এর ফলে লেখা হয় না।

I/O side effect-যুক্ত handler-এর জন্য, [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-তে `event_stream_handler=` দিন। মডেল event প্রতিটি model-request step-এর ভেতরে লাইভ পৌঁছায়, আর প্রতিটি টুল event নিজের event-handler step-এ পৌঁছায়। যেকোনো DBOS step-এর মতো, এর step চেকপয়েন্ট হওয়ার আগে workflow উদ্ধার হলে একটি handler একাধিকবার চলতে পারে, তাই এর side effect idempotent রাখুন।

বিকল্পভাবে, [`ProcessEventStream`][pydantic_ai.capabilities.ProcessEventStream] নিবন্ধন করুন। এর handler workflow কোডে চলে আর deterministic হতে হবে, কারণ এটি workflow replay-তে আবার চলে। টুল আর চূড়ান্ত-আউটপুট event লাইভ আসে, আর মডেল event প্রতিটি মডেল রিকোয়েস্ট শেষ হওয়ার পর চূড়ান্ত response থেকে replay হয়। উদাহরণের জন্য দেখুন [streaming ডক](../agent.md#streaming-all-events)।

একটি durability `event_stream_handler=` আর আলাদাভাবে নিবন্ধিত একটি `ProcessEventStream` দুটি ভিন্ন handler, আর প্রত্যেকে একবার চলে। durability handler durable step-এর ভেতরে লাইভ event পায়, আর `ProcessEventStream` workflow কোডে জমানো replay দেখে।

`Agent.run(event_stream_handler=...)`-এ দেওয়া একটি প্রতি-রান handler-ও replay করা মডেল event-এর বিপরীতে workflow-পক্ষে চলে।

একটি DBOS step-এর ভেতর থেকে [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] দিয়ে তৈরি event — একটি MCP বা dynamic-toolset টুল, একটি `event_stream_handler`, বা আপনার `@DBOS.step` দিয়ে decorate করা একটি টুল — পৌঁছায় যখন step আসলে চলে, আর উদ্ধারের সময় এর লেখা ফল replay হলে আবার তৈরি *হয় না*। একটি step-এর ভেতরে লেখা একটি log লাইনের মতো, একটি তৈরি event step চালানোর একটি side effect, এর লেখা ফলের অংশ নয়। সাধারণ ফাংশন টুল আর [capability](../capabilities/overview.md) hook workflow কোডে চলে, যেখানে একটি emit workflow-এর বাকি অংশের সাথে আবার চলে। [`@on_event`][pydantic_ai.capabilities.on_event] দিয়ে নিবন্ধিত capability listener-ও workflow কোডে চলে, তাই এগুলো উদ্ধারের সময় আবার চলে আর deterministic হতে হবে; I/O একটি durability `event_stream_handler=`-এ রাখুন, যা নিজের step-এ চলে। [`ctx.enqueue()`][pydantic_ai.tools.RunContext.enqueue]-এর বিপরীতে, যা একটি step-এর ভেতরে প্রত্যাখ্যাত হয় কারণ এটি বাদ পড়লে মডেল যা দেখে তা বদলে যেত, একটি হারানো event মানে শুধু একজন পর্যবেক্ষককে জানানো হয়নি। একটি durable এককের তৈরি event এর লেখা আউটপুটে বহন করা, যাতে একটি replay সেগুলো পুনরুৎপাদন করে, ট্র্যাক হচ্ছে [pydantic-ai#7971](https://github.com/pydantic/pydantic-ai/issues/7971)-এ।

যেহেতু মডেল stream step-এর ভেতরে গ্রহণ হয়, workflow-পক্ষ থেকে এটি বাতিল করা (যেমন [`AgentStream.cancel()`][pydantic_ai.result.AgentStream.cancel] দিয়ে) durable সীমা জুড়ে পাওয়া যায় না।

[`CancellationToken`][pydantic_ai.CancellationToken] একটি DBOS durable রানে দেওয়া যায় না, আর [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel] একটি step-মোড়ানো এককের ভেতরে (একটি dynamic বা MCP টুল, বা একটি `event_stream_handler`) একটি স্পষ্ট [`UserError`][pydantic_ai.exceptions.UserError] তোলে, যার লেখা ফল উদ্ধারের সময় আবার না চলে replay হবে। DBOS-এর অধীনে একটি সাধারণ ফাংশন টুল workflow স্তরে চলে, যেখানে `cancel()` কাজ করে আর replay-সামঞ্জস্যপূর্ণ। বাইরে থেকে একটি রান থামাতে, DBOS workflow বাতিল করুন। DBOS একটি `asyncio.CancelledError`-এর বদলে নিজের exception দিয়ে রান বাতিল করে (`DBOSWorkflowCancelledError`, বা dbos 3.2 আর পরে `DBOSWorkflowConflictIDError`), কিন্তু রানের state তবুও এতে যুক্ত থাকে, তাই workflow-এর ভেতরে এটি ধরে [`RunCancelled.from_cancellation()`][pydantic_ai.exceptions.RunCancelled.from_cancellation] ডাকলে [বাতিলের পরের message history](../agent.md#message-history-after-cancellation) উদ্ধার হয়। workflow-এর caller যে `DBOSAwaitedWorkflowCancelledError` পায় তা এটি বহন করে না, কারণ DBOS ওই error workflow-এর লেখা অবস্থা থেকে তৈরি করে।

[`Agent.run_stream_sync()`][pydantic_ai.agent.Agent.run_stream_sync] workflow কোডের জন্য নয়: এর জন্য কোনো চলমান event loop না থাকা লাগে আর এটি `run_stream()` মোড়ায়। [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-এর অধীনে, ওপরের জমানো async streaming API বা একটি event stream handler-সহ [`Agent.run()`][pydantic_ai.agent.Agent.run] ব্যবহার করুন। একটি workflow-এর বাইরে, `DBOSDurability`-সহ একটি এজেন্ট একটি সাধারণ এজেন্টের মতো আচরণ করে, তাই `run_stream_sync()` স্বাভাবিকভাবে কাজ করে। (Wrapper `DBOSAgent` workflow-এর ভেতরে `run_stream` নিষেধ করে — সেখানে `run` + event stream handler ব্যবহার করুন।)

### রানের timeout { #run-timeouts }

একটি রানের [`timeout=`](../timeouts.md#bounding-a-whole-run) একটি workflow-এর ভেতরে কাজ করে। রানের শুরুর সময় একটি `{name}.run_start_time` step হিসেবে লেখা হয়, তাই একটি উদ্ধার হওয়া workflow রান যে সময়সীমা নিয়ে শুরু হয়েছিল তা রাখে, আর দেখতে পারে যে তা ইতিমধ্যে পেরিয়ে গেছে। সময়সীমা পেরোলে, রান workflow কোডে [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut] তোলে, যেখানে আপনি এটি ধরতে পারেন। অবচিত `DBOSAgent` `timeout=` প্রত্যাখ্যান করে।

সময়সীমা এজেন্ট রান সীমিত করে, workflow নয়। পুরো workflow-ও সীমিত করতে, এটি DBOS-এর `SetWorkflowTimeout`-এর ভেতরে শুরু করুন, যা মেয়াদ শেষ হলে workflow বাতিল করে।

### স্থগিত turn আর background mode { #suspended-turns-and-background-mode }

যখন একটি provider একটি মডেল turn মাঝপথে থামায় (Anthropic `pause_turn`) বা একে একটি সার্ভার-পক্ষের job হিসেবে চালায় যা প্রস্তুত না হওয়া পর্যন্ত poll করা হয় ([OpenAI background mode](../models/openai.md#background-mode)), প্রতিটি অংশ একটি আলাদা model request step-এ চলে, আর poll-এর মাঝের অপেক্ষা একটি টেকসই `DBOS.sleep` step, তাই উদ্ধারে সম্পন্ন অপেক্ষা বাদ পড়ে। স্থগিত [`ModelResponse`][pydantic_ai.messages.ModelResponse] আর background job ID অংশগুলোর মাঝে চেকপয়েন্ট হয়, আর চূড়ান্ত response মেলানো হয় আর usage একবার লেখা হয়। একটি স্থগিত response-এ শেষ হওয়া একটি [`message_history`](../message-history.md) প্রথম step-এ দেওয়া হয়। একটি provider round trip-এর জন্য step timeout ঠিক করুন। একটি error একটি স্থগিত job পরিত্যাগ করলে, এর provider teardown একটি নির্দিষ্ট cancellation step-এ চলে।

### সমান্তরাল টুল চালানো { #parallel-tool-execution }

DBOS-এর অধীনে, দেরি কমাতে টুল ডিফল্টভাবে সমান্তরালে চলে। deterministic replay আর নির্ভরযোগ্য উদ্ধার নিশ্চিত করতে, DBOS event **ক্রমানুসারে** তৈরির আগে সব সমান্তরাল টুল কল শেষ হওয়ার অপেক্ষা করে।
এটি [`with agent.parallel_tool_call_execution_mode('parallel_ordered_events')`][pydantic_ai.agent.AbstractAgent.parallel_tool_call_execution_mode]-এর আচরণের সমতুল্য।

আপনি কঠোর ক্রম চাইলে, [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-তে `parallel_execution_mode='sequential'` সেট করে এজেন্টকে টুল একটার পর একটা চালাতে কনফিগার করতে পারেন।
একটি [workspace](../workspace.md)-যুক্ত রান সবসময় এর টুল কল একটার পর একটা চালায়।

### রানের সময় toolset { #toolsets-at-runtime }

durable মোড়ানো লাগে এমন প্রতিটি চালানো toolset এজেন্ট constructor-এ দিন, যাতে workflow চলার আগে এর step নিবন্ধিত হয়। এতে [`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset] অন্তর্ভুক্ত: একে একটি স্পষ্ট `id` দিন আর `Agent(toolsets=[...])`-এ দিন। [`@agent.toolset`][pydantic_ai.agent.Agent.toolset] decorator engine-এর durable একক তৈরির পরে নিবন্ধন করে, তাই [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability]-এর অধীনে একটি workflow-এর ভেতরে এটি ব্যবহার করলে একটি `UserError` ওঠে। অবচিত `DBOSAgent` এই যাচাই চালায় না: একটি workflow-এর ভেতরে এটি মোড়ানোর সময় স্থির হওয়া step-মোড়ানো toolset তালিকা চালায়, তাই এত দেরিতে নিবন্ধিত একটি toolset নিঃশব্দে রান থেকে বাদ পড়ে।

`agent.run(toolsets=...)` দিয়ে প্রতি রানে বাড়তি toolset দেওয়া যায়। [`ExternalToolset`][pydantic_ai.toolsets.ExternalToolset]-এর মতো না-চালানো toolset, আর [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] যার টুল DBOS inline চালায়, সমর্থিত। রানের সময় দেওয়া [`MCPToolset`][pydantic_ai.mcp.MCPToolset] আর dynamic toolset একটি `UserError` তোলে।

একটি workflow-এর ভেতরে [`agent.override(toolsets=...)`][pydantic_ai.agent.AbstractAgent.override] দিয়ে বদলানো toolset-ও একই নিয়মে বাঁধা, কারণ এগুলোও এজেন্টের step নিবন্ধনের পরে আসে। রানের সময় যোগ করা একটি toolset এজেন্ট তৈরির সময়ের কোনোটির `id`-ও পুনর্ব্যবহার করতে পারে না, কারণ `id`-ই চিহ্নিত করে একটি টুল কল কোন নিবন্ধিত toolset-এর step-এ পাঠানো হবে।


## Step কনফিগারেশন { #step-configuration }

আপনি [`DBOSDurability`][pydantic_ai.durable_exec.dbos.DBOSDurability] constructor-এ [`StepConfig`][pydantic_ai.durable_exec.dbos.StepConfig] অবজেক্ট দিয়ে DBOS step-এর আচরণ, যেমন retry, কাস্টমাইজ করতে পারেন:

- `mcp_step_config`: MCP সার্ভারের যোগাযোগের জন্য ব্যবহারের DBOS step config। বাদ দিলে কোনো retry নেই।
- `model_step_config`: model request step-এর জন্য ব্যবহারের DBOS step config। বাদ দিলে কোনো retry নেই। model request step [durable-execution retry স্তর](../retries.md#the-layers) বহন করে — `StepConfig` retry SDK client আর transport-এর retry-র সাথে কীভাবে জমা হয় তা দেখুন [Retry multiplication](../retries.md#retry-multiplication)-এ।
- `event_stream_handler_step_config`: event stream handler step-এর জন্য ব্যবহারের DBOS step config (শুধু `DBOSDurability`)। বাদ দিলে কোনো retry নেই।

[Temporal](temporal.md#per-tool-activity-config) আর [Prefect](prefect.md#tool-wrapping) ইন্টিগ্রেশনের বিপরীতে, DBOS কোনো প্রতি-টুল config নেয় না: টুলের metadata (একটি `'dbos'` key বা অন্য কিছু) উপেক্ষিত হয়, আর একটি একক টুলকে step মোড়ানো থেকে বের করার কোনো উপায় নেই।

নিজস্ব টুলের জন্য, আপনি প্রয়োজনমতো সরাসরি [`@DBOS.step`](https://docs.dbos.dev/python/reference/decorators#step) বা [`@DBOS.workflow`](https://docs.dbos.dev/python/reference/decorators#workflow) decorator দিতে পারেন। এই decorator-গুলো DBOS workflow-এর বাইরে কোনো প্রভাব ফেলে না, তাই টুলগুলো non-DBOS এজেন্টে ব্যবহারযোগ্য থাকে।


## Step retry { #step-retries }

DBOS-এর করা রিকোয়েস্ট ব্যর্থতার স্বয়ংক্রিয় retry-র ওপরে, Pydantic AI আর বিভিন্ন provider API client-এরও নিজস্ব রিকোয়েস্ট retry লজিক আছে। এগুলো একসাথে চালু করলে রিকোয়েস্ট প্রত্যাশার চেয়ে বেশিবার retry হতে পারে, ভুল `Retry-After` সামলানোসহ।

DBOS ব্যবহারের সময়, [transport retries](../retries.md#transport-retries) ব্যবহার না করা আর আপনার provider API client-এর নিজস্ব retry লজিক বন্ধ করা সুপারিশকৃত, যেমন একটি [custom `OpenAIProvider` API client](../models/openai.md#custom-openai-client)-এ `max_retries=0` সেট করে।

আপনি [step configuration](#step-configuration) দিয়ে DBOS-এর retry policy কাস্টমাইজ করতে পারেন।

DBOS-এ বাছাই করে retry-অযোগ্য exception-এর সমর্থন নেই, তাই আপনি step retry (`retries_allowed`) চালু করলে, `UserError`-এর মতো framework ভুল-কনফিগারেশনের error-ও অন্য সব কিছুর সাথে retry হয়। Temporal আর Prefect ইন্টিগ্রেশন এগুলোকে retry-অযোগ্য চিহ্নিত করে; DBOS-এ, আশা করুন একটি ভুল-কনফিগার করা এজেন্ট ব্যর্থ হওয়ার আগে পুরো retry বাজেট শেষ করবে।

## Logfire দিয়ে Observability { #observability-with-logfire }

DBOS-কে প্রতিটি workflow আর step execution-এর জন্য OpenTelemetry span তৈরি করতে কনফিগার করা যায়, আর Pydantic AI প্রতিটি এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল কলের জন্য span তৈরি করে। আপনার অ্যাপ্লিকেশনে কী ঘটছে তার একটি পূর্ণ, শুরু-থেকে-শেষ ভিউ পেতে আপনি এই span-গুলো [Pydantic Logfire](../logfire.md)-এ পাঠাতে পারেন।

logging আর tracing-এর বিস্তারিতের জন্য দেখুন [DBOS ডক](https://docs.dbos.dev/python/tutorials/logging-and-tracing)।

/// check | সংক্ষেপে মনে রাখুন

* DBOS process-এর ভেতরে চলে, state রাখে Postgres (প্রোডাকশন) বা SQLite-এ — কোনো আলাদা সার্ভার নেই।
* `Agent(name=..., capabilities=[DBOSDurability()])`, আর `agent.run()` নিজের `@DBOS.workflow`-এর ভেতরে।
* এজেন্ট `DBOS.launch()`-এর আগে তৈরি করুন; `name` আর MCP toolset `id` অনন্য ও স্থির।
* মডেল রিকোয়েস্ট আর MCP নিজে থেকে step; ফাংশন টুলে I/O থাকলে নিজে `@DBOS.step` দিন।
* DBOS ডিফল্টভাবে `pickle` দিয়ে serialize করে; input/output ছোট রাখুন।
* retry একটি জায়গায়; DBOS-এ `UserError`-ও retry হয়, তাই সাবধানে `retries_allowed` চালু করুন।

///
