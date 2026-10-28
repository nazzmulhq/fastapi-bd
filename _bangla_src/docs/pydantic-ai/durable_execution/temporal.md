# Temporal দিয়ে Durable Execution { #durable-execution-with-temporal }

/// note | এই পেজে যা শিখবেন

* Temporal-এর মূল ধারণা: **workflow** (deterministic) আর **activity** (I/O করে)।
* `TemporalDurability` capability দিয়ে একটি সাধারণ এজেন্টকে durable করা — একটি সম্পূর্ণ উদাহরণ।
* এজেন্টের নাম, toolset ID, dependency, workspace, বড় payload, streaming, timeout নিয়ে Temporal-এর বিশেষ বিবেচনা।
* activity কনফিগারেশন, retry, child workflow আর Logfire দিয়ে observability।

///

[Temporal](https://temporal.io) একটি জনপ্রিয় [durable execution](https://docs.temporal.io/evaluate/understanding-temporal#durable-execution) প্ল্যাটফর্ম, যা Pydantic AI নেটিভভাবে সমর্থন করে।

## Durable Execution { #durable-execution }

Temporal-এর durable execution বাস্তবায়নে, একটি মডেল বা API-এর সাথে কাজ করার সময় crash করা বা exception পাওয়া একটি প্রোগ্রাম সফলভাবে শেষ না হওয়া পর্যন্ত retry করবে।

ব্যর্থতা থেকে উদ্ধারের জন্য Temporal মূলত একটি replay পদ্ধতির ওপর নির্ভর করে।
প্রোগ্রাম এগোনোর সাথে সাথে, Temporal মূল input আর সিদ্ধান্তগুলো সংরক্ষণ করে, যাতে আবার শুরু হওয়া একটি প্রোগ্রাম ঠিক যেখানে থেমেছিল সেখান থেকে তুলে নিতে পারে।

এটি কাজ করানোর চাবি হলো অ্যাপ্লিকেশনের পুনরাবৃত্তিযোগ্য (deterministic) আর অ-পুনরাবৃত্তিযোগ্য (non-deterministic) অংশ আলাদা করা:

1. Deterministic অংশ, যাদের বলা হয় [**workflow**](https://docs.temporal.io/workflow-definition), একই input দিয়ে আবার চালালে একইভাবে চলে।
2. Non-deterministic অংশ, যাদের বলা হয় [**activity**](https://docs.temporal.io/activities), যেকোনো কোড চালাতে পারে, I/O আর অন্য যেকোনো কাজ করে।

Workflow কোড দীর্ঘ সময় চলতে পারে আর বাধা পেলে ঠিক যেখানে থেমেছিল সেখান থেকে আবার চলে।
গুরুত্বপূর্ণভাবে, workflow কোডে সাধারণত নেটওয়ার্ক, ডিস্ক ইত্যাদির কোনো ধরনের I/O রাখা _যায় না_।
Activity কোডে I/O বা বাইরের যোগাযোগে কোনো বাধা নেই, কিন্তু একটি activity মাঝপথে ব্যর্থ হলে এটি শুরু থেকে আবার চলে।

/// tip | উদাহরণ দিয়ে বুঝি

একজন রাঁধুনি (workflow) একটি রেসিপি মেনে চলেন: "ডিম আনো → ফেটাও → ভাজো"। তিনি নিজে বাজারে যান না — বাজার করে একজন সহকারী (activity)। রাঁধুনি প্রতিটি সহকারীর আনা জিনিসের রসিদ খাতায় লিখে রাখেন। রাঁধুনি অজ্ঞান হয়ে আবার জেগে উঠলে, খাতা দেখে রেসিপি শুরু থেকে "মনে মনে" আবার চালান — কিন্তু যে বাজার আগেই হয়েছে, সেটার জন্য সহকারীকে আবার পাঠান না, খাতা থেকে ফল নিয়ে নেন। তাই রেসিপি (workflow) প্রতিবার একইভাবে চলতে হয় — হঠাৎ "আজ মন চাইলে মাছ" ধরনের সিদ্ধান্ত (র‍্যান্ডম, সময়, নেটওয়ার্ক) রেসিপিতে রাখা যায় না।

///

/// note | মনে রাখুন

আপনি celery-র সাথে পরিচিত হলে, Temporal activity-কে celery task-এর মতো ভাবা সাহায্য করতে পারে, তবে যেখানে workflow-এর পরের ধাপে যাওয়ার আগে আপনি task শেষ হওয়ার অপেক্ষা করেন আর এর ফল নেন।
তবে Temporal workflow আর activity celery task-এর চেয়ে অনেক বেশি নমনীয়তা আর কার্যকারিতা দেয়।

আরও তথ্যের জন্য দেখুন [Temporal ডকুমেন্টেশন](https://docs.temporal.io/evaluate/understanding-temporal#temporal-application-the-building-blocks)

///

Pydantic AI এজেন্টের ক্ষেত্রে, Temporal-এর সাথে ইন্টিগ্রেশন মানে [মডেল রিকোয়েস্ট](../models/overview.md), I/O লাগতে পারে এমন [টুল কল](../tools.md), আর [MCP সার্ভারের সাথে যোগাযোগ](../mcp/client.md) — সবগুলোকে তাদের I/O প্রয়োজনের কারণে Temporal activity-তে পাঠাতে হয়, আর এদের সমন্বয় করা লজিক (অর্থাৎ এজেন্ট রান) থাকে workflow-তে। একটি নির্ধারিত job বা ওয়েব রিকোয়েস্ট সামলানো কোড তখন workflow চালাতে পারে, যা প্রয়োজনমতো activity চালাবে।

নিচের diagram Temporal-এ একটি agentic অ্যাপ্লিকেশনের সামগ্রিক architecture দেখায়।
Temporal Server প্রোগ্রাম চালানো ট্র্যাক করা আর সংশ্লিষ্ট state নির্ভরযোগ্যভাবে সংরক্ষিত থাকা নিশ্চিত করার দায়িত্বে (অর্থাৎ, একটি অভ্যন্তরীণ ডেটাবেসে রাখা, আর হয়তো cloud region জুড়ে প্রতিলিপি করা)।
Temporal Server ডেটা এনক্রিপ্ট করা রূপে পরিচালনা করে, তাই সব ডেটা প্রক্রিয়াকরণ হয় Worker-এ, যা workflow আর activity চালায়।


```text
            +---------------------+
            |   Temporal Server   |      (Stores workflow state,
            +---------------------+       schedules activities,
                     ^                    persists progress)
                     |
        Save state,  |   Schedule Tasks,
        progress,    |   load state on resume
        timeouts     |
                     |
+------------------------------------------------------+
|                      Worker                          |
|   +----------------------------------------------+   |
|   |              Workflow Code                   |   |
|   |       (Agent Run Loop)                       |   |
|   +----------------------------------------------+   |
|          |          |                |               |
|          v          v                v               |
|   +-----------+ +------------+ +-------------+       |
|   | Activity  | | Activity   | |  Activity   |       |
|   | (Tool)    | | (MCP Tool) | | (Model API) |       |
|   +-----------+ +------------+ +-------------+       |
|         |           |                |               |
+------------------------------------------------------+
          |           |                |
          v           v                v
      [External APIs, services, databases, etc.]
```

আরও তথ্যের জন্য দেখুন [Temporal ডকুমেন্টেশন](https://docs.temporal.io/evaluate/understanding-temporal#temporal-application-the-building-blocks)।

## Durable এজেন্ট { #durable-agent }

একটি রান durable করতে, একটি worker-এ চলা একটি Temporal workflow-এর ভেতরে `agent.run()` ডাকুন; এর বাইরে, এজেন্ট একটি সাধারণ, non-durable এজেন্ট হিসেবে চলে।

যেকোনো [`Agent`][pydantic_ai.agent.Agent]-এ durable execution যোগ করুন [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] [capability](../capabilities/overview.md) যুক্ত করে। এজেন্টটি সব জায়গায় একটি সাধারণ `Agent` থাকে — একটি workflow-এর বাইরে এটি স্বচ্ছভাবে আচরণ করে, আর একটি workflow-এর ভেতরে capability-টি মডেল রিকোয়েস্ট, টুল কল আর MCP সার্ভারের যোগাযোগ Temporal activity দিয়ে পাঠায়।

/// warning | একটি রান শুধু একটি workflow-এর ভেতরেই durable

`TemporalDurability` যুক্ত করা নিজে থেকে রান durable করে না — durability আসে আপনার অ্যাপ্লিকেশনের শুরু করা একটি Temporal workflow-এর ভেতরে রান চালানো থেকে (একটি Temporal client দিয়ে, যেমন নিচের উদাহরণে)। সাধারণ কোড থেকে `agent.run()` বা একটি streaming মেথড ডাকা — পরোক্ষভাবেও, যেমন একটি ওয়েব endpoint-এ একটি [UI adapter](../ui/overview.md) দিয়ে — একটি সাধারণ, non-durable এজেন্ট রান। একটি API-এর পেছনে একটি durable এজেন্ট পরিবেশন করতে, endpoint-এ এজেন্ট চালানোর বদলে endpoint দিয়ে একটি workflow শুরু (বা signal) করান আর এর ফল বা event client-এ ফেরত পৌঁছে দিন।

///

একটি এজেন্টে durable execution যুক্ত করা, durable execution লজিকসহ একটি Temporal workflow তৈরি করা, একটি Temporal সার্ভারে সংযোগ করা, আর non-durable কোড থেকে workflow চালানোর একটি সহজ কিন্তু সম্পূর্ণ উদাহরণ এখানে। এর জন্য শুধু `temporal` optional group-সহ Pydantic AI ইনস্টল করতে হয়:

/// tab | pip

```bash
pip install pydantic-ai[temporal]
```

///

/// tab | uv

```bash
uv add pydantic-ai[temporal]
```

///


অথবা slim প্যাকেজ ব্যবহার করলে, `temporal` optional group দিয়ে ইনস্টল করতে পারেন:

/// tab | pip

```bash
pip install pydantic-ai-slim[temporal]
```

///

/// tab | uv

```bash
uv add pydantic-ai-slim[temporal]
```

///


আপনার একটি Temporal সার্ভার [লোকালে চালু](https://github.com/temporalio/temporal#download-and-start-temporal-server-locally) থাকাও লাগবে:

```sh
brew install temporal
temporal server start-dev
```

```python title="temporal_durability.py"
import uuid

from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalDurability,
)

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions="You're an expert in geography.",
    name='geography',  # (1)!
    capabilities=[TemporalDurability()],  # (2)!
)


@workflow.defn
class GeographyWorkflow(PydanticAIWorkflow):  # (3)!
    __pydantic_ai_agents__ = [agent]  # (4)!

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await agent.run(prompt)  # (5)!
        return result.output


async def main():
    client = await Client.connect(  # (6)!
        'localhost:7233',  # (7)!
        plugins=[PydanticAIPlugin()],  # (8)!
    )

    async with Worker(  # (9)!
        client,
        task_queue='geography',
        workflows=[GeographyWorkflow],
    ):
        output = await client.execute_workflow(  # (10)!
            GeographyWorkflow.run,
            args=['What is the capital of Mexico?'],
            id=f'geography-{uuid.uuid4()}',
            task_queue='geography',
        )
        print(output)
        #> Mexico City (Ciudad de México, CDMX)
```

1. এজেন্টের `name` এর activity-গুলোকে অনন্যভাবে চিহ্নিত করতে ব্যবহৃত হয়।
2. `capabilities=[...]` দিয়ে durability যুক্ত করুন। এজেন্টে যুক্ত হওয়ার সময় capability-টি এজেন্টের নাম, মডেল আর toolset খুঁজে নেয়, আর প্রতিটির জন্য একটি activity নিবন্ধন করে। একটি workflow-এর বাইরে, capability স্বচ্ছ — এজেন্ট একটি সাধারণ `Agent`-এর মতো আচরণ করে।
3. Workflow একটি deterministic কোড অংশ প্রতিনিধিত্ব করে, যা I/O লাগা কাজের জন্য non-deterministic activity ব্যবহার করতে পারে। [`PydanticAIWorkflow`][pydantic_ai.durable_exec.temporal.PydanticAIWorkflow] subclass করা ঐচ্ছিক, কিন্তু `__pydantic_ai_agents__` class variable-এর জন্য ঠিক typing দেয়।
4. এই workflow-এ ব্যবহৃত এজেন্টগুলোর তালিকা দিন। [`PydanticAIPlugin`][pydantic_ai.durable_exec.temporal.PydanticAIPlugin] প্রতিটি এজেন্টের [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] capability-র দেওয়া activity আর child workflow নিজে থেকে worker-এ নিবন্ধন করে। বিকল্পভাবে, workflow ক্লাসের চেয়ে worker-এর শুরু বদলানো সহজ হলে, একটি এজেন্টের activity আর child workflow সরাসরি worker-এ নিবন্ধন করতে [`AgentPlugin`][pydantic_ai.durable_exec.temporal.AgentPlugin] ব্যবহার করতে পারেন। কোনো টুল `child_workflow` দিয়ে কনফিগার থাকলে এই plugin পথগুলোর একটি ব্যবহার করুন; শুধু `TemporalDurability.temporal_activities` নিবন্ধন করা প্রত্যাখ্যাত হয়, কারণ তাতে দরকারি workflow সংজ্ঞা বাদ পড়বে।
5. `agent.run()` স্বাভাবিকভাবে কাজ করে; workflow-এর ভেতরে, মডেল রিকোয়েস্ট, টুল কল আর MCP সার্ভারের যোগাযোগ Temporal activity দিয়ে যায়।
6. আমরা Temporal সার্ভারে সংযোগ করি, যা workflow আর activity চালানো ট্র্যাক করে।
7. এটি ধরে নেয় Temporal সার্ভার [লোকালে চলছে](https://github.com/temporalio/temporal#download-and-start-temporal-server-locally)।
8. [`PydanticAIPlugin`][pydantic_ai.durable_exec.temporal.PydanticAIPlugin] Temporal-কে serialization আর deserialization-এর জন্য Pydantic ব্যবহার করতে বলে, আর `__pydantic_ai_agents__`-এ তালিকাভুক্ত এজেন্টদের activity নিজে থেকে নিবন্ধন করে। Activity retry policy [`UserError`][pydantic_ai.exceptions.UserError], `PydanticUserError`, [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] আর [`FallbackExceptionGroup`][pydantic_ai.exceptions.FallbackExceptionGroup]-কে retry-অযোগ্য ধরে, সাথে Temporal-এর নিজস্ব সীমা-ছাড়ানো-payload ব্যর্থতার টাইপ `PayloadsTooLarge` আর (`temporalio` 1.31-এর আগে) `PayloadSizeError` (দেখুন [Large Payloads](#large-payloads)), আর workspace error `WorkspaceTimeoutError`, `WorkspaceOutputLimitError`, `WorkspaceReadOnlyError` আর `WorkspaceUnavailableError`; আর worker `UserError`, `PydanticUserError`, [`AgentRunError`][pydantic_ai.exceptions.AgentRunError], `UnsupportedEventLoopError` আর [`WorkspaceError`][pydantic_ai.workspaces.WorkspaceError]-কে `workflow_failure_exception_types` হিসেবে নিবন্ধন করে।
9. আমরা worker শুরু করি, যা নির্দিষ্ট task queue-তে শুনবে আর workflow ও activity চালাবে। একটি বাস্তব অ্যাপ্লিকেশনে, এটি হয়তো একটি আলাদা সার্ভিসে চলবে।
10. নির্দিষ্ট task queue-তে শুনছে এমন একটি worker-এ workflow চালাতে আমরা সার্ভারকে বলি।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// info | এক নজরে: তিনটি অংশ

| অংশ | কী করে | কোথায় চলে |
|-----|--------|------------|
| এজেন্ট + `TemporalDurability` | মডেল/টুল/MCP কলগুলোকে activity বানায় | worker (activity হিসেবে) |
| Workflow ক্লাস (`@workflow.defn`) | `await agent.run(...)` ডাকে — রানের সমন্বয় | worker (workflow হিসেবে, replay হয়) |
| Client (`Client.connect` + `execute_workflow`) | workflow শুরু করে আর ফল নেয় | আপনার অ্যাপ (ওয়েব সার্ভার, স্ক্রিপ্ট) |

///

যেহেতু একই এজেন্ট একটি workflow-এর ভেতরে আর বাইরে কাজ করে, [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] অন্য সব [capability](../capabilities/overview.md)-র (instrumentation, [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata], [`ProcessEventStream`][pydantic_ai.capabilities.ProcessEventStream] ইত্যাদি) সাথে মিলে যায়, প্রতিটির জন্য একটি Temporal-নির্দিষ্ট wrapper রূপ ছাড়াই।

Workflow কোডকে async API ব্যবহার করতে হয়: [`Agent.run_sync()`][pydantic_ai.agent.Agent.run_sync] নিজেই event loop চালায়, যা Temporal-এর workflow event loop অনুমতি দেয় না, তাই একটি workflow-এর ভেতরে এটি ডাকলে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে, যা আপনাকে এর বদলে `await agent.run()` করতে বলে। একটি workflow-এর বাইরে, `TemporalDurability`-সহ একটি এজেন্ট একটি সাধারণ এজেন্টের মতো আচরণ করে, তাই `run_sync()` স্বাভাবিকভাবে কাজ করে।

একটি বাস্তব অ্যাপ্লিকেশনে, এজেন্ট, workflow আর worker সাধারণত সেই কোড থেকে আলাদাভাবে সংজ্ঞায়িত হয়, যা একটি workflow চালাতে বলে।
যেহেতু Temporal workflow ফাইলের শীর্ষ স্তরে সংজ্ঞায়িত হতে হয়, আর এজেন্টকে workflow-এর ভেতরে আর worker শুরুর সময় (activity নিবন্ধনের জন্য) লাগে, তাই এটিকেও ফাইলের শীর্ষ স্তরে সংজ্ঞায়িত করতে হয়।

Python অ্যাপ্লিকেশনে Temporal কীভাবে ব্যবহার করবেন তার আরও তথ্যের জন্য, দেখুন তাদের [Python SDK guide](https://docs.temporal.io/develop/python)।

### Wrapper-agent পথ (অবচিত) { #wrapper-agent-path-deprecated }

/// warning | অবচিত (Deprecated)

[`TemporalAgent`][pydantic_ai.durable_exec.temporal.TemporalAgent] হলো Temporal ইন্টিগ্রেশনের মূল wrapper-agent পথ, যা v3-এ সরানো হবে। নতুন কোডে ওপরে দেখানো [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] capability ব্যবহার করা উচিত।

[`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] `TemporalAgent`-এর লেখা activity নাম আর payload রূপ গ্রহণ করে (যতক্ষণ এজেন্টের `name`, toolset-এর `id` আর `models=` registry key একই থাকে, আর `TemporalAgent`-যুগের workflow চলমান থাকা পর্যন্ত `event_stream_handler=` `TemporalDurability`-তে থাকে), তাই `TemporalAgent`-এর অধীনে শুরু হওয়া workflow বদলের পরও ঠিকভাবে replay হবে — আগে আপনার workflow drain বা version করার দরকার নেই। একটি event stream handler-সহ লেখা ইতিহাস প্রতি-event একটি activity নিবন্ধন করেছিল; ওই workflow শেষ হওয়ার আগে [`ProcessEventStream`][pydantic_ai.capabilities.ProcessEventStream]-এ সরে গেলে replay ভেঙে যায়।

///

যেকোনো এজেন্টকে একটি [`TemporalAgent`][pydantic_ai.durable_exec.temporal.TemporalAgent]-এ মোড়ানো যায়, একটি Temporal workflow-এর ভেতরে ব্যবহারযোগ্য একটি durable এজেন্ট রূপ পেতে। মোড়ানোর সময়, এজেন্টের মডেল আর toolset স্থির হয়ে যায়, প্রতিটির জন্য গতিশীলভাবে activity তৈরি হয়, আর মূল মডেল আর toolset মোড়ানো হয় যাতে workflow-এর ভেতরে সরাসরি কাজ না করে worker-কে সংশ্লিষ্ট activity চালাতে বলে। মূল এজেন্ট এখনও Temporal workflow-এর বাইরে স্বাভাবিকভাবে ব্যবহার করা যায়, কিন্তু মোড়ানোর পর এর মডেল বা toolset-এ কোনো পরিবর্তন durable এজেন্টে প্রতিফলিত হবে না।

```python title="temporal_agent.py"
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalAgent

agent = Agent('openai:gpt-6.1-sol', name='geography')
temporal_agent = TemporalAgent(agent)
# Use `temporal_agent` from inside a workflow, list it in `__pydantic_ai_agents__`,
# and connect with `PydanticAIPlugin()` exactly like the capability example above.
```

## Temporal ইন্টিগ্রেশনের বিবেচনা { #temporal-integration-considerations }

durable execution-এর জন্য Temporal ব্যবহারের সময় এজেন্ট আর toolset-এর জন্য নির্দিষ্ট কয়েকটি বিবেচনা আছে। আপনার এজেন্ট আর toolset Temporal-এর workflow আর activity মডেলের সাথে ঠিকভাবে কাজ করছে তা নিশ্চিত করতে এগুলো বোঝা জরুরি।

### এজেন্টের নাম আর Toolset ID { #agent-names-and-toolset-ids }

একটি activity ব্যর্থ বা বাধাপ্রাপ্ত হয়ে আবার শুরু হলে Temporal যাতে জানে কোন কোড চালাতে হবে — মাঝে আপনার কোড বদলালেও — প্রতিটি activity-র একটি স্থিতিশীল আর অনন্য নাম থাকা দরকার।

যখন [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] এজেন্টের মডেল রিকোয়েস্ট আর toolset-এর (নির্দিষ্টভাবে যেগুলো নিজের টুল তালিকা আর কল বাস্তবায়ন করে, অর্থাৎ [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] আর [`MCPToolset`][pydantic_ai.mcp.MCPToolset]) জন্য গতিশীলভাবে activity তৈরি করে, তাদের নাম আসে এজেন্টের [`name`][pydantic_ai.agent.AbstractAgent.name] আর toolset-গুলোর [`id`][pydantic_ai.toolsets.AbstractToolset.id] থেকে। এই ফিল্ডগুলো সাধারণত ঐচ্ছিক, কিন্তু Temporal ব্যবহারের সময় সেট করা বাধ্যতামূলক, আর `id` ছাড়া একটি URL `MCPToolset` যে hostname-কে `id` হিসেবে নেয় তা গণ্য হয় না। durable এজেন্ট প্রোডাকশনে deploy হওয়ার পর এগুলো বদলানো উচিত নয়, কারণ তাতে সক্রিয় workflow ভেঙে যাবে।

/// warning | সাধারণ ভুল

প্রোডাকশনে চলমান workflow থাকা অবস্থায় `Agent(name='support')`-কে `name='support_v2'` করা, বা একটি toolset-এর `id` বদলানো। পুরনো workflow replay করার সময় Temporal পুরনো নামের activity খুঁজবে — যা আর নেই — আর workflow আটকে যাবে। নাম একবার ঠিক করে স্থির রাখুন; বদলাতেই হলে Temporal worker versioning ব্যবহার করুন।

///

এই version-এ আপগ্রেড করা `args_validator`-যুক্ত টুলের activity ক্রম বদলায়, তাই এমন টুল ডাকা ইতিমধ্যে চলমান workflow-গুলোর [Temporal worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) বা একটি [patch](https://python.temporal.io/temporalio.workflow.html#patched) লাগে। `args_validator`-যুক্ত টুল না ডাকা workflow প্রভাবিত হয় না।

[`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset] আর [`DynamicCapability`][pydantic_ai.capabilities.DynamicCapability]-এর দেওয়া toolset সমর্থিত। টুল তালিকা আর কলের সময় activity-র ভেতরে এদের factory আবার মীমাংসা হয়, তাই রানের dependency দেওয়া থাকলে এটিকে deterministic হতে হবে। অন্য মোড়ানো toolset-এর মতো, প্রতিটি `DynamicToolset`-এর একটি স্পষ্ট `id` লাগে: সরাসরি তৈরি করলে `id=` দিন, বা `DynamicCapability`-তে একটি স্থিতিশীল capability `id` সেট করুন। মনে রাখবেন Temporal-এ, `per_run_step=False` মানা হয় না, কারণ toolset সবসময় activity-তে তাৎক্ষণিকভাবে তৈরি করতে হয়: একটি activity workflow-এর চেয়ে ভিন্ন worker process-এ চলতে পারে, তাই workflow-এর মীমাংসা করা একটি toolset পুনর্ব্যবহার করতে পারে না। যে engine-এর durable একক workflow-এর নিজের process-এ চলে, যেমন [DBOS](dbos.md) আর [Prefect](prefect.md), সেগুলো এটি পুনর্ব্যবহার করে, যা factory-র ফেরত দেওয়া একটি `MCPToolset`-কে রানের জন্য একটি session রাখতে দেয়।

একই কারণে, এজেন্টে যুক্ত একটি [`MCPToolset`][pydantic_ai.mcp.MCPToolset] এর টুল তালিকা বা কল করা প্রতিটি activity-র ভেতরে সংযুক্ত হয়: একটি activity workflow-এর ধরে রাখা session ব্যবহার করতে পারে না, আর এর worker হয়তো একটি session ধরে রাখা process নয়। প্রতিটি activity-র session এটি ফেরত দেওয়ার সময় বন্ধ হয়, তাই সার্ভারের [`cache_tools`][pydantic_ai.mcp.MCPToolset.cache_tools] শুধু সেই activity কভার করে যা এটি পূরণ করেছে। workflow তবুও এর `get_tools` activity-র লেখা টুল সংজ্ঞা রাখে (যতক্ষণ `cache_tools` চালু থাকে), তাই খোঁজার খরচ প্রতি মডেল রিকোয়েস্টে একটির বদলে প্রতি রানে একটি activity।

যে [capability](../capabilities/overview.md) একটি toolset দেয় — `tools=`-সহ একটি [`Capability`][pydantic_ai.capabilities.Capability], বা লোকালে চলা একটি [`MCP`][pydantic_ai.capabilities.MCP] সার্ভার — তারা toolset-এর `id` capability-র নিজের [`id`][pydantic_ai.capabilities.AbstractCapability.id] থেকে তৈরি করে, তাই `Capability(id='...', tools=[...])` বা `MCP(id='...', url='...')` সেট করুন। (`id` না দিলে `MCP` সার্ভার URL-এর hostname-এ ফিরে যায়।) `toolsets=` দিয়ে একটি capability-তে দেওয়া একটি toolset নিজের `id` রাখে, যা toolset-এই সেট করতে হবে।

অন্য সব এজেন্ট আর toolset সমর্থিত।

### টুলের আর্গুমেন্ট যাচাই { #tool-argument-validation }

একটি টুলের [`args_validator`](../tools-advanced.md#args-validator) একটি `validate_args` activity-তে চলে, তাই এটি I/O করতে পারে আর dynamic-tool validator workflow সীমা পেরিয়ে টিকে থাকে। একটি ছাড়া টুল কোনো বাড়তি activity নির্ধারণ করে না। যাচাই চলে [অনুমোদন আর deferral](../deferred-tools.md)-এর আগে, তাই প্রত্যাখ্যাত আর্গুমেন্ট কখনো একজন অনুমোদনকারীর কাছে পৌঁছায় না। একটি validator `ApprovalRequired` বা `CallDeferred`-ও তুলতে পারে; একটি অনুমোদিত কল আবার চালালে `tool_call_approved` সেট করে যাচাই আবার চলে।

প্রতিটি activity এর টাইপ করা আর্গুমেন্ট স্বাধীনভাবে তৈরি করে, তাই schema validator-কে idempotent হতে হবে। একটি Pydantic validation context [`Agent`][pydantic_ai.agent.Agent]-এ কনফিগার করা `validation_context` থেকে আবার তৈরি হয়; একটি callable context builder activity-র নিজের run context দিয়ে আবার চলে।

### এজেন্ট রান context আর dependency { #agent-run-context-and-dependencies }

যেহেতু workflow আর activity আলাদা process-এ চলে, তাদের মধ্যে পাঠানো যেকোনো মান serialize-যোগ্য হতে হয়। যেহেতু এই payload workflow execution event history-তে সংরক্ষিত হয়, Temporal ডিফল্টভাবে এদের আকার 2MB-তে সীমিত রাখে — এই বাজেটে আসলে কী আঁটে তা দেখুন [Large Payloads](#large-payloads)-এ।

এই সীমাবদ্ধতা মাথায় রেখে, activity-র ভেতরে চলা টুল ফাংশন আর [event stream handler](#streaming) এজেন্টের [`RunContext`][pydantic_ai.tools.RunContext]-এর একটি সীমিত রূপ পায়, আর [`Agent.run()`][pydantic_ai.agent.Agent.run]-এ দেওয়া [dependencies](../dependencies.md) অবজেক্ট Pydantic দিয়ে serialize করা যায় কিনা তা নিশ্চিত করা আপনার দায়িত্ব।

একটি activity-তে শুধু `deps`-ই যায় না: [`model_settings`](../agent.md#model-run-settings), `RunContext`-এর `metadata` আর `tool_call_metadata`, আর [tool metadata](#per-tool-activity-config)-ও যায়, আর সবগুলোকে Pydantic দিয়ে serialize-যোগ্য হতে হবে। না হলে একটি `UserError` ওঠে, যা serialize করতে না পারা টাইপের নাম বলে। এতে এমন কিছু মানও আছে যা অন্যথায় সমর্থিত: [`model_settings['timeout']`][pydantic_ai.settings.ModelSettings.timeout] একটি `httpx.Timeout`-এর বদলে সেকেন্ডের একটি সংখ্যা হিসেবে দিন।

যে মানগুলো Pydantic AI সীমা পেরিয়ে টাইপহীন dictionary হিসেবে বহন করে — [tool metadata](#per-tool-activity-config), `RunContext`-এর `metadata` আর `tool_call_metadata`, [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] আর [`CallDeferred`][pydantic_ai.exceptions.CallDeferred]-এর `metadata`, আর বার্তা ও তাদের অংশে বহন করা `metadata`, `provider_details` আর `vendor_metadata` — সেগুলো মূল Python অবজেক্টের বদলে তাদের JSON রূপে পৌঁছায়: একটি `set` বা `tuple` হয়ে যায় `list`, একটি dataclass বা Pydantic model হয়ে যায় `dict`, UTF-8-এ decode-যোগ্য `bytes` হয়ে যায় `str`, আর string নয় এমন dictionary key হয়ে যায় string। যেকোনো binary wire-এ একদমই যায় না — আগে base64-এ encode করুন। wire-এ এর কোনোটি ফিরিয়ে আনার মতো টাইপের তথ্য নেই, তাই এই payload JSON-native রাখুন, বা গ্রহণের দিকে প্রত্যাশিত টাইপে আবার যাচাই করুন (একটি [`TypeAdapter`](https://docs.pydantic.dev/latest/api/type_adapter/) দিয়ে)। ঘোষিত টাইপসহ প্রতিটি ফিল্ড — প্রতিটি বার্তার বাকি অংশ, [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] আর [`ModelRequestParameters`][pydantic_ai.models.ModelRequestParameters], আর run context-এর `usage`, `usage_limits`, `loaded_capability_ids` আর `discovered_tool_names` — বিশ্বস্তভাবে যাওয়া-আসা করে।

/// warning | সংরক্ষিত payload schema

Temporal সংরক্ষিত workflow আর activity payload deserialize করে বর্তমানে deploy করা worker-এ উপলব্ধ model আর type annotation দিয়ে, তাই এই model-গুলোকে deployment জুড়ে টেকসই চুক্তি হিসেবে ধরুন। একটি ডিফল্টসহ ঐচ্ছিক ফিল্ড যোগ করা সামঞ্জস্যপূর্ণ থাকে, কিন্তু একটি বাধ্যতামূলক ফিল্ড যোগ করা বা অন্য কোনো অসামঞ্জস্যপূর্ণ পরিবর্তন workflow বা activity body চলার আগেই payload decoding ব্যর্থ করাতে পারে। এটি বিশেষভাবে প্রাসঙ্গিক অ্যাপ্লিকেশনের নিজস্ব workflow input আর dependency model-এর জন্য: যেহেতু Pydantic AI Temporal workflow history-র মালিক নয় বা migrate করে না, দীর্ঘ-চলা workflow-যুক্ত অ্যাপ্লিকেশনের এগুলো বদলানোর সময় একটি versioning বা migration কৌশল নেওয়া উচিত।

///

নির্দিষ্টভাবে, শুধু `deps`, `run_id`, `conversation_id`, `metadata`, `retries`, `tool_call_id`, `tool_name`, `tool_call_approved`, `tool_call_metadata`, `retry`, `max_retries`, `run_step`, `partial_output`, `usage`, `usage_limits`, `trace_include_content`, `instrumentation_version`, `loaded_capability_ids`, `discovered_tool_names` আর `capability_active` ফিল্ড ডিফল্টভাবে পাওয়া যায়। `agent` আর `root_capability` worker-এর এজেন্ট instance থেকে আবার যুক্ত হয়, `tool_manager` হলো `None` (তাই [`available_tool_names`][pydantic_ai.tools.RunContext.available_tool_names] activity পাঠানোর সময় মীমাংসা করা snapshot ফেরত দেয়, আর শুধু এমন একটি subclass-এর জন্য `discovered_tool_names`-এ ফিরে যায় যার `serialize_run_context` এটি বহন করে না; [`active_capability_ids`][pydantic_ai.tools.RunContext.active_capability_ids] একইভাবে বহন হয়, যা [`is_tool_available`][pydantic_ai.tools.RunContext.is_tool_available]-কে একটি capability-র মালিকানাধীন টুলের জন্য উত্তর দিতে দেয়), আর `pending_messages` একটি পাহারা রাখে যা একটি activity-র ভেতরে [`ctx.enqueue()`][pydantic_ai.tools.RunContext.enqueue]-কে exception তোলায়, কারণ activity-র লেখা ফল আপনার কোড আবার না চালিয়ে replay হয় আর enqueue করা বার্তাগুলো হারিয়ে যেত।

অন্য যেকোনো ফিল্ড — `model`, `prompt`, `messages`, `model_settings`, `tracer`, বা `capabilities` — পড়ার চেষ্টা করলে ওই ফিল্ডের ডিফল্ট মান ফেরত দেওয়ার বদলে একটি `UserError` ওঠে, যাতে সীমা পার হয়নি এমন একটি ফিল্ডকে আসল রান state ভেবে ভুল করা না যায়। `validation_context`-ও serialize হয় না, তবে একটি activity-র ভেতরে প্রথমবার পড়ার সময় এজেন্টের `validation_context` সেটিং থেকে আবার তৈরি হয়। একটি multi-modal `prompt` বড় [`BinaryContent`][pydantic_ai.messages.BinaryContent] বহন করতে পারে, আর এটি বহন করলে সেই কনটেন্ট প্রতিটি activity payload-এ যেত, `messages`-এর মতো একই Temporal [payload size](#large-payloads) সমস্যা তৈরি করে।
এই attribute-গুলোর এক বা একাধিক activity-র ভেতরে দরকার হলে, আপনি নিজস্ব `serialize_run_context` আর `deserialize_run_context` class method-সহ একটি [`TemporalRunContext`][pydantic_ai.durable_exec.temporal.TemporalRunContext] subclass তৈরি করে [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-তে `run_context_type` আর্গুমেন্ট হিসেবে দিতে পারেন। একটি subclass `prompt` বহন করা বেছে নিতে পারে, যদি সে জানে তার prompt শুধু লেখা।

/// info | এক নজরে: activity-র ভেতরে `ctx`

| পাওয়া যায় | পাওয়া যায় না (`UserError`) |
|-------------|------------------------------|
| `ctx.deps` (serialize-যোগ্য হতে হবে), `run_id`, `conversation_id`, `metadata`, `retry`, `usage` (snapshot), `tool_name`, `tool_call_id` ... | `ctx.model`, `ctx.prompt`, `ctx.messages`, `ctx.model_settings`, `ctx.tracer`, `ctx.capabilities` |

টুলের ভেতরে আপনার যা লাগবে তা `deps`-এ রাখুন — আর `deps` ছোট আর JSON-serialize-যোগ্য রাখুন।

///

activity-র `RunContext` serialize করা payload থেকে আবার তৈরি হয়, তাই এর ফিল্ডগুলো অনুলিপি: একটি activity-র ভেতরে এগুলো বদলালে রান প্রভাবিত হয় না। বিশেষ করে, `usage` হলো activity নির্ধারণের সময় রানের usage-এর একটি snapshot। একটি টুল `usage=ctx.usage` দিয়ে [আরেকটি এজেন্টকে কাজ দিলে](../multi-agent-applications.md#agent-delegation), delegate-এর token আর রিকোয়েস্ট activity-তেই থেকে যায়: সেগুলো parent রানের [`result.usage`][pydantic_ai.agent.AgentRunResult.usage]-এ থাকে না আর এর [usage limits](../agent.md#usage-limits)-এর বিপরীতে কখনো গোনা হয় না। delegate-এর usage হিসাব করতে, নিজে বহন করুন: টুল থেকে delegate-এর [`result.usage`][pydantic_ai.agent.AgentRunResult.usage] ফেরত দিন, বা আপনার `deps`-এর নাগালের একটি বাইরের store-এ লিখুন। Temporal এই পরিবর্তনগুলো নিঃশর্তভাবে হারায়। [DBOS](dbos.md) আর [Prefect](prefect.md) তাদের in-process durable এককে জীবন্ত `RunContext` দেয়, তাই একটি step বা task body আসলে চলার সময় পরিবর্তন জমা হয় — কিন্তু সেখানেও হারায় যখনই body চলে না কারণ এর লেখা ফল replay হয় (DBOS workflow recovery) বা পুনর্ব্যবহৃত হয় (একটি Prefect task cache hit), যা একই কোডকে এক রান থেকে পরের রানে ভিন্নভাবে হিসাব করায়। in-process engine-এর আচরণের ওপর নির্ভর করবেন না; তিনটির জন্যই কাজ করে এমন একটি ফেরত-পথ নিয়ে আলোচনা চলছে [pydantic-ai#6886](https://github.com/pydantic/pydantic-ai/issues/6886)-এ।

একটি workflow-এ [`Agent.run()`][pydantic_ai.agent.Agent.run]-এ `run_id` বা `conversation_id` না দিলে, ডিফল্টগুলো র‍্যান্ডমভাবে তৈরি না হয়ে workflow রান থেকে তৈরি হয়, তাই Temporal workflow-টি অন্য worker-এ replay করলেও এগুলো একই থাকে, আর রানের প্রতিটি activity রানের ফলের মতো একই ID দেখে। workspace ছাড়া এজেন্টের জন্য Pydantic AI এই ডিফল্টগুলো তৈরি করার আগে শুরু হওয়া workflow র‍্যান্ডম ID রাখে, যাতে তাদের ইতিহাস অপরিবর্তিত replay হয়।

একটি টুলের [`prepare`](../tools-advanced.md#tool-prepare) ফাংশন এই সীমাবদ্ধতায় প্রভাবিত হয় না: একটি [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset]-এর টুলের জন্য (এজেন্টেই সংজ্ঞায়িতগুলোসহ), এটি পুরো `RunContext`-সহ workflow কোডে চলে, workflow-এর বাইরের মতোই প্রতি run step-এ একবার। এর ফেরত দেওয়া টুল সংজ্ঞা tool-call activity-তে পাঠানো হয়, যা এটি যেমন আছে তেমন ব্যবহার করে, তাই মডেল যে টুল দেখেছে সেটিই চলে, এর [`timeout`](../tools-advanced.md#tool-timeout) পর্যন্ত। একটি `DynamicToolset`-এর টুল ব্যতিক্রম: যেহেতু toolset activity-র ভেতরে আবার মীমাংসা হয়, তাদের `prepare` ফাংশনও সেখানে চলে আর সীমিত `RunContext` দেখে।

[`XSearch`][pydantic_ai.capabilities.XSearch] বা [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration]-এ একটি `native=` factory দুবার মীমাংসা হয়, সীমার দুই পাশে: একবার নেটিভ টুল কনফিগার করতে workflow কোডে, আর আবার fallback subagent-এর tool-call activity-র ভেতরে, যেখানে এটি সীমিত `RunContext` দেখে। সেখানে `ctx.messages` নয়, `ctx.deps` পড়ুন।

### Workspace { #workspaces }

এজেন্ট তৈরির সময় [workspace](../workspace.md) capability যুক্ত করুন, যেমন `LocalWorkspace`, আর যেকোনো রানের মতো `ctx.workspace` ব্যবহার করুন: একটি টুলে এটি activity-র ভেতরে আবার তৈরি হয় আর সরাসরি provider ডাকে, আর workflow কোডে (capability hook, output function, `result.workspace`) প্রতিটি কল একটি activity হিসেবে চলে। যেহেতু একটি activity যেকোনো worker-এ চলতে পারে:

- প্রতিটি worker-এর এজেন্ট workflow-এর মতো একই workspace capability দিয়ে তৈরি করুন।
- একটি নিজস্ব [`get_workspace`][pydantic_ai.capabilities.AbstractCapability.get_workspace]-এ, শুধু `deps` আর [ওপরে তালিকাভুক্ত run context ফিল্ড](#agent-run-context-and-dependencies) পড়ুন।
- বড় ফাইল একটি টুলের ভেতরে সরান: একটি workflow-পক্ষের কল ফাইলটি activity payload-এ বহন করে, যা [payload size limit](#large-payloads)-এর বিপরীতে গোনা হয়।
- `LocalWorkspace`-এ, প্রতিটি worker-কে একই absolute path-এ, ভাগ করা storage-এ ডিরেক্টরিটি দিন।

একটি এজেন্টে workspace যোগ করা এর workflow-এর ইতিহাস বদলায়, তাই আগে চলমান workflow drain করুন বা
পরিবর্তনটি Temporal worker versioning দিয়ে বা একটি নতুন task queue-তে deploy করুন।

Temporal workflow-পক্ষের workspace কলের আর্গুমেন্ট (কমান্ড, `env=`, ফাইলের কনটেন্ট) ইতিহাসে রাখে।
secret workflow-পক্ষের আর্গুমেন্ট হিসেবে না দিয়ে workspace capability-র `env=`-এ রাখুন বা একটি টুলের ভেতরে ব্যবহার করুন; ইতিহাস সুরক্ষিত রাখতে একটি [payload codec](#large-payloads) ব্যবহার করুন।

### Harness workspace capability { #harness-workspace-capabilities }

`Coder`, `Shell` আর `FileSystem`-এর মতো [Harness](../harness/index.md) workspace capability একটি
Temporal workflow-এ কাজ করে; [workspace guide](../workspace.md#harness-workspace-capabilities) দেখায় প্রতিটি engine-এ কী কাজ করে। তিনটি বিষয় Temporal-নির্দিষ্ট।

**লাইভ event।** ফাইল লেখা টুল অনুমোদন চায় আর workflow থেকে লেখাটি জানায়, তাই
`FileChangeRequestEvent`, `FileWrittenEvent`, `FileEditedEvent` আর `DirectoryCreatedEvent` ঘটার সাথে সাথে আপনার listener-এর কাছে পৌঁছায়। অন্য টুল activity-তে চলে আর তাদের event পৌঁছায় না: ফাইল টুলের `FileReadEvent`,
`DirectoryListedEvent` আর `FilesSearchedEvent`, আর `shell`-এর `CommandStartedEvent`,
`CommandOutputEvent` আর `CommandFinishedEvent`
([#7971](https://github.com/pydantic/pydantic-ai/issues/7971))। টুলগুলো তবুও কাজ করে আর তাদের ফল ফেরত দেয়। Temporal একটি workflow replay করলে, অনুমোদন listener আবার চলে, তাই তাদের বাইরের প্রভাব idempotent করুন।

**কাজ দেওয়া (Delegation)।** `Coder`-এর delegate, `self`, workflow-এ চলে, তাই child-এর মডেল রিকোয়েস্ট আর টুল একই এজেন্টের activity হয়ে যায়। `agent_folders` থেকে পড়া sub-agent সমর্থিত নয়: রানের শুরুতে ফোল্ডার পড়া রানের সময় একটি toolset যোগ করে, যা Temporal প্রত্যাখ্যান করে, তাই নিজে `SubAgents` গঠন করলে `SubAgents(include_self=True, agent_folders=None)` দিন।

#### কমান্ডের timeout { #harness-command-timeouts }

একটি activity ডিফল্টভাবে 60 সেকেন্ড পায়। `run_command` আর `shell` পায় 300 সেকেন্ড, যা `shell` টুলের 270-সেকেন্ডের foreground অপেক্ষা কভার করে। `Shell(default_timeout=...)` বা মডেলের `timeout_seconds` দিয়ে লম্বা timeout পাওয়া একটি `run_command`-এর একটি লম্বা activity লাগে। এজেন্টের capability-তে `SetToolMetadata` দিয়ে এটি সেট করুন:

```python
from datetime import timedelta

from pydantic_ai_harness.coder import Coder
from temporalio.workflow import ActivityConfig

from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace, SetToolMetadata
from pydantic_ai.durable_exec.temporal import TemporalDurability

agent = Agent(
    'openai:gpt-6.1-sol',
    name='coder',
    capabilities=[
        LocalWorkspace('.'),
        Coder(),
        TemporalDurability(),
        SetToolMetadata(tools=['run_command'], temporal=ActivityConfig(start_to_close_timeout=timedelta(minutes=30))),
    ],
)
```

আরও লম্বা কাজের জন্য, `start_command` বা `shell(mode='background')` ব্যবহার করুন, যা কমান্ড চলতে থাকা অবস্থায় ফেরত আসে।

### রানের সময় capability { #capabilities-at-runtime }

এজেন্ট তৈরির সময় [capability](../capabilities/overview.md) যুক্ত করুন, যাতে worker শুরুর আগে `TemporalDurability.for_agent()` তাদের activity নিবন্ধন করতে পারে। একটি workflow-এর ভেতরে `agent.run(capabilities=[...])` দিলে একটি `UserError` ওঠে: এত দেরিতে যোগ করা একটি capability-র দেওয়া toolset বা এর নিজের [`@durable_operation`][pydantic_ai.capabilities.durable_operation] মেথডের জন্য কোনো নিবন্ধিত activity নেই।

যে capability শুধু রান পর্যবেক্ষণ করে সেগুলো প্রতি-রানে যুক্ত করা নিরাপদ: তাদের hook রান state পড়ে কিন্তু টুল, toolset বা durable operation দেয় না। [`Instrumentation`][pydantic_ai.capabilities.Instrumentation] হলো বিল্ট-ইন উদাহরণ আর বাধা থেকে মুক্ত। বর্তমান বাধা বেশি রক্ষণশীল, কারণ থার্ড-পার্টি capability এখনও ঘোষণা করতে পারে না যে তারা শুধু রান পর্যবেক্ষণ করে। একটি capability কোন hook override করে তা থেকে এটি বের করা ট্র্যাক হচ্ছে [#5477](https://github.com/pydantic/pydantic-ai/issues/5477)-এ; একটি workflow-এর ভেতরে প্রতি-রান capability দরকার হলে, দয়া করে সেখানে আপনার ব্যবহারের ক্ষেত্র জানান। একটি workflow-এর বাইরে durability capability স্বচ্ছ, তাই সেখানে প্রতি-রান capability ঠিক আছে।

### বড় payload { #large-payloads }

Temporal এর লেখা প্রতিটি payload workflow execution event history-তে রাখে — একটি activity যা ফেরত দেয় আর যে আর্গুমেন্ট দিয়ে এটি নির্ধারিত হয়েছিল দুটোই — আর প্রতিটিকে ডিফল্টভাবে 2MB-তে সীমিত রাখে। দুটি জিনিস প্রায়ই ওই সীমা ভাঙে:

- **Binary কনটেন্ট**, যেমন একটি টুলের ফেরত দেওয়া বা একটি মডেলের response-এ রাখা একটি ছবি। Binary ডেটা payload-এ যাওয়ার পথে base64-এ encode হয়, তাই কাঁচা bytes-এর ব্যবহারযোগ্য বাজেট সীমার প্রায় তিন-চতুর্থাংশ — মোটামুটি 1.5MB। যে ছবির আকার আরামে 2MB-এর নিচে দেখায় তাও প্রত্যাখ্যাত হতে পারে।
- **একটি বড় [dependencies অবজেক্ট](../dependencies.md)**, যা Pydantic AI প্রতিবার একটি মডেল, টুল, MCP বা event-handler activity নির্ধারণ করার সময় ইতিহাসে কপি হয় — তাই অনেক টুলের একটি বড় fan-out ইতিহাস স্থায়ীভাবে ফুলিয়ে দিতে পারে আর প্রতি-payload সীমাও ভাঙতে পারে।

#### যখন একটি টুলের ফেরত বা মডেলের response খুব বড় { #when-a-tool-return-or-model-response-is-too-large }

একটি [`BinaryImage`][pydantic_ai.messages.BinaryImage] ফেরত দেওয়া একটি টুল — সরাসরি image generator হোক বা [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] capability-র পেছনের subagent fallback, বা আপনার নিজের `local=` টুল — ওই bytes activity-র ফলের payload হিসেবে ফেরত পাঠায়, আর Temporal তা প্রত্যাখ্যান করলে Pydantic AI টুলের নামসহ একটি `UserError` তোলে। একটি মডেল এর response-এ যে ছবি ফেরত দেয় তার ক্ষেত্রেও একই প্রযোজ্য, যেমন একটি [নেটিভ image generation টুলে](../native-tools.md#image-generation-tool), যেহেতু মডেল রিকোয়েস্ট নিজেই একটি activity; সেখানে `UserError` মডেলের নাম বলে।

আপনার নিয়ন্ত্রণের একটি টুলের জন্য, সবচেয়ে সহজ সমাধান হলো bytes ইতিহাস থেকে পুরোপুরি বাইরে রাখা: ছবিটি object storage-এ লিখুন আর একটি রেফারেন্স ফেরত দিন — একটি [`ImageUrl`][pydantic_ai.messages.ImageUrl], বা একটি key যা আপনার অ্যাপ্লিকেশন পরে মীমাংসা করে। ছোট payload workflow replay-ও দ্রুত রাখে, তাই এটি শুধু সীমার নিচে থাকার চেয়েও বেশি লাভ দেয়। যখন bytes একটি provider থেকে ফেরত আসে, বা payload মিডিয়ার বদলে একটি বড় `deps` অবজেক্ট, তখন এর বদলে external storage ব্যবহার করুন।

#### আপনার নিজের storage-এ payload সরানো { #offloading-payloads-to-your-own-storage }

Temporal এটি সাধারণভাবে সমাধান করে [external storage](https://docs.temporal.io/external-storage) দিয়ে, যা একটি আকার-সীমার ওপরের যেকোনো payload স্বচ্ছভাবে আপনার নিজের store-এ সরায় আর এর বদলে ইতিহাসে একটি রেফারেন্স রাখে। এটি দুই দিকেই প্রতিটি payload-এ প্রযোজ্য, তাই `UserError` যেগুলো পারে না সেই ক্ষেত্রগুলোও কভার করে। আপনার `DataConverter`-এ একটি [`ExternalStorage`](https://docs.temporal.io/develop/python/data-handling/external-storage) দিয়ে এটি কনফিগার করুন:

```python title="temporal_external_storage.py"
import dataclasses

from temporalio.client import Client
from temporalio.converter import DataConverter, ExternalStorage

from pydantic_ai.durable_exec.temporal import PydanticAIPlugin

from my_app.storage import my_storage_driver  # your `StorageDriver` implementation


async def connect() -> Client:
    data_converter = dataclasses.replace(
        DataConverter.default,
        external_storage=ExternalStorage(drivers=[my_storage_driver]),
    )
    return await Client.connect(
        'localhost:7233',
        data_converter=data_converter,
        plugins=[PydanticAIPlugin()],
    )
```

[`PydanticAIPlugin`][pydantic_ai.durable_exec.temporal.PydanticAIPlugin] শুধু Temporal-এর ডিফল্ট payload *converter*-কে এর Pydantic-সচেতন একটি দিয়ে বদলায়, তাই আপনার `external_storage` — একটি নিজস্ব `payload_codec` বা `failure_converter_class`-এর মতো — রক্ষিত থাকে।

সীমার নিচের payload (ডিফল্টভাবে 256 KiB) ছোঁয়া হয় না, তাই ছোট dependency-যুক্ত রানে এর কোনো খরচ নেই। উপলব্ধ storage driver আর নিজের লেখার জন্য Temporal-এর ডকুমেন্টেশন দেখুন; মনে রাখবেন external storage public preview-তে আছে, তাই এর API এখনও বদলাতে পারে।

/// warning | সংরক্ষিত payload আপনার workflow history-র অংশ

যে payload অনুপস্থিত, মেয়াদোত্তীর্ণ বা অপ্রবেশযোগ্য, তা worker-দের workflow decode আর replay করতে বাধা দেয়। সংরক্ষিত payload অন্তত ততদিন উপলব্ধ রাখুন যতদিন তাদের ইতিহাস replay হতে পারে।

///

যেহেতু সরানো হয় প্রতি payload-এ, N activity-র একটি fan-out তবুও N (ছোট) রেফারেন্স তৈরি করে। External storage আকারের সীমা আর ইতিহাস ফোলা সরায়; এটি একটি একক workflow-task সমাপ্তির ভেতরে একই dependency-র পুনরাবৃত্তি বাদ দেয় না।

আপনি একটি public-preview API নিতে না পারলে, Temporal [`PayloadCodec`](https://docs.temporal.io/develop/python/converters-and-encryption#custom-payload-codec)-এর ওপর তৈরি একটি হাতে-লেখা [claim check codec](https://docs.temporal.io/ai-cookbook/claim-check-pattern-python)-ও নথিভুক্ত করে, যা `PydanticAIPlugin` একইভাবে রক্ষা করে।

শেষ উপায় হিসেবে, bytes-কে সত্যিই workflow history-তে থাকতে হলে, আপনার Temporal সার্ভারে `limit.blobSize.error` [dynamic config](https://docs.temporal.io/references/dynamic-configuration) বাড়ান। মনে রাখবেন এর ওপরেও Temporal-এর নিজস্ব gRPC message সীমা প্রযোজ্য, তাই এটি সীমা সরায় না, বাড়ায় — দেখুন Temporal-এর [blob size limit](https://docs.temporal.io/troubleshooting/blob-size-limit-error) নির্দেশনা।

/// warning | শুধু একটি activity যা *ফেরত দেয়* তা-ই বন্ধুসুলভ error পায়

একটি activity-তে *যাওয়া* মান — একটি মডেল রিকোয়েস্টের বহন করা message history, বা একটি `event_stream_handler`-কে দেওয়া একটি stream-করা event — workflow কোডে encode হয়, যেখানে Temporal activity-র বদলে workflow *task* ব্যর্থ করে। ওই ব্যর্থতা কখনো Pydantic AI-তে পৌঁছায় না, আর যেহেতু এটি activity-র নয়, workflow-task ব্যর্থতা, retry policy-ও এটি সীমিত করে না: রান exception না তুলে অনির্দিষ্টভাবে retry করে। তাই আঁটে এমন একটি টুল ফেরতও *পরের* মডেল রিকোয়েস্টের ইতিহাসের অংশ হলে খুব বড় হতে পারে। External storage এখানে নির্ভরযোগ্য সমাধান, কারণ এটি দুই দিকেই প্রতিটি payload-এ প্রযোজ্য।

`UserError` একটি সীমা-ছাড়ানো payload চিনতে Temporal-এর ডিফল্ট failure converter-এর ওপরও নির্ভর করে, তাই আপনি নিজের `failure_converter_class` দিলে, বা worker-কে নিজের সীমা জানায় না এমন একটি সার্ভারের বিপরীতে চালালে এটি চালু হবে না।

///

/// note | ছবির output type একদমই সমর্থিত নয়

যে এজেন্টের [`output_type`](../output.md)-এ [`BinaryImage`][pydantic_ai.messages.BinaryImage] আছে, তা আকারে ব্যর্থ হওয়ার বদলে রিকোয়েস্ট করার আগেই একটি `UserError` তোলে: এমন প্রতিটি রানকে তৈরি ছবি সীমা পেরিয়ে বহন করতে হতো।

///

### Streaming { #streaming }

[`Agent.run_stream()`][pydantic_ai.agent.Agent.run_stream], [`Agent.run_stream_events()`][pydantic_ai.agent.Agent.run_stream_events] আর [`Agent.iter()`][pydantic_ai.agent.Agent.iter] একটি Temporal workflow-এর ভেতরে কাজ করে, কিন্তু তাদের event সাথে সাথে পৌঁছানোর বদলে জমা (buffer) হয়। মডেল stream durable activity-র ভেতরে চলে, আর activity শেষ হলে workflow এর চূড়ান্ত response replay করে: প্রতিটি অংশ মডেলের stream করা delta হিসেবে নয়, বরং এর পুরো কনটেন্টসহ একটি [`PartStartEvent`][pydantic_ai.messages.PartStartEvent] হিসেবে আসে, তাই delta-গুলো activity-র ফলে লেখা হয় না।

I/O side effect-যুক্ত handler-এর জন্য, [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-তে `event_stream_handler=` দিন। মডেল event প্রতিটি model-request activity-র ভেতরে লাইভ পৌঁছায়, আর প্রতিটি টুল event নিজের event-handler activity-তে পৌঁছায়। যেকোনো Temporal activity-র মতো, একটি activity retry করলে একটি handler একাধিকবার চলতে পারে, তাই এর side effect idempotent রাখুন।

বিকল্পভাবে, [`ProcessEventStream`][pydantic_ai.capabilities.ProcessEventStream] নিবন্ধন করুন। এর handler workflow কোডে চলে আর deterministic হতে হবে, কারণ এটি workflow replay-তে আবার চলে। টুল আর চূড়ান্ত-আউটপুট event লাইভ আসে, আর মডেল event প্রতিটি মডেল রিকোয়েস্ট শেষ হওয়ার পর চূড়ান্ত response থেকে replay হয়। উদাহরণের জন্য দেখুন [streaming ডক](../agent.md#streaming-all-events)।

একটি durability `event_stream_handler=` আর আলাদাভাবে নিবন্ধিত একটি `ProcessEventStream` দুটি ভিন্ন handler, আর প্রত্যেকে একবার চলে। durability handler durable activity-র ভেতরে লাইভ event পায়, আর `ProcessEventStream` workflow কোডে জমানো replay দেখে।

/// info | এক নজরে: event পাওয়ার তিন উপায়

| উপায় | কোথায় চলে | মডেল event | I/O করা যায়? |
|-------|-----------|------------|---------------|
| `TemporalDurability(event_stream_handler=...)` | activity-র ভেতরে | লাইভ (delta-সহ) | হ্যাঁ (idempotent রাখুন) |
| `ProcessEventStream` capability | workflow কোডে | শেষে replay | না (deterministic হতে হবে) |
| `event_stream_topic` (Workflow Streams) | বাইরের consumer | লাইভ | consumer-এ যা খুশি |

///

`Agent.run(event_stream_handler=...)`-এ দেওয়া একটি প্রতি-রান handler-ও replay করা মডেল event-এর বিপরীতে workflow-পক্ষে চলে।

যেহেতু streaming model request activity, workflow আর workflow execution কল — সবগুলো আলাদা process-এ ঘটে, তাদের মধ্যে ডেটা পাঠাতে কিছুটা সতর্কতা লাগে:

- workflow কল-সাইট বা workflow থেকে event stream handler-এ ডেটা পাঠাতে, আপনি একটি [dependencies অবজেক্ট](#agent-run-context-and-dependencies) ব্যবহার করতে পারেন।
- event stream handler থেকে workflow, workflow কল-সাইট বা একটি frontend-এ ডেটা পাঠাতে, আপনি একটি [Workflow Stream](#streaming-events-to-a-frontend-with-workflow-streams)-এ event প্রকাশ করতে পারেন (সুপারিশকৃত, কোনো বাড়তি infrastructure ছাড়া), বা একটি বাইরের সিস্টেম ব্যবহার করতে পারেন যেখানে event stream handler লিখতে আর event consumer পড়তে পারে, যেমন একটি message queue। সব প্রয়োজনীয় জায়গায় একই connection string বা অন্য অনন্য ID পাওয়া নিশ্চিত করতে আপনি dependency অবজেক্ট ব্যবহার করতে পারেন।

#### Workflow Streams দিয়ে একটি frontend-এ event stream করা { #streaming-events-to-a-frontend-with-workflow-streams }

একটি message queue দাঁড় করানোর বদলে, আপনি Temporal-এর বিল্ট-ইন [Workflow Streams](https://docs.temporal.io/develop/python/workflows/workflow-streams)-কে বাহক হিসেবে ব্যবহার করতে পারেন: workflow নিজেই হয়ে যায় টেকসই, offset-চিহ্নিত চ্যানেল, যাতে এর বাইরের একটি consumer subscribe করে।

[`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-তে `event_stream_topic` সেট করুন আর আপনার workflow-এ একটি [`AgentEventStream`][pydantic_ai.durable_exec.temporal.AgentEventStream] হোস্ট করুন। topic সেট করাই streaming চালু করে, আর এটি `event_stream_handler` থেকে স্বাধীন: আপনি একটি handler-ও দিলে, সেটি তবুও প্রতিটি event দেখে।

```python title="temporal_workflow_streams_workflow.py"
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from pydantic_ai import Agent
    from pydantic_ai.durable_exec.temporal import (
        AgentEventStream,
        PydanticAIWorkflow,
        TemporalDurability,
    )

durability = TemporalDurability(event_stream_topic='agent-events')
agent = Agent('openai:gpt-6.1-sol', name='assistant', capabilities=[durability])


@workflow.defn
class AssistantWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]  # registers the agent's activities with the worker

    @workflow.init
    def __init__(self, prompt: str) -> None:
        self.events = AgentEventStream()

    @workflow.run
    async def run(self, prompt: str) -> str:
        async with self.events:
            result = await agent.run(prompt)
        return result.output
```

শুধু একটি workflow handle ধরে রাখা একটি consumer তখন রানটি ঘটার সাথে সাথে পর্যবেক্ষণ করে,
[`stream_agent_events()`][pydantic_ai.durable_exec.temporal.TemporalDurability.stream_agent_events] দিয়ে।
এটি আর পরের snippet-গুলো ওপরের workflow module চালিয়ে যায় (এরা এর `agent`, `durability` আর workflow ক্লাস ব্যবহার করে) আর [`PydanticAIPlugin`][pydantic_ai.durable_exec.temporal.PydanticAIPlugin] দিয়ে সংযুক্ত একটি `client` নেয়, যেমন [প্রথম উদাহরণে](#durable-agent):

```python title="temporal_workflow_streams_consumer.py"
from uuid import uuid4

from temporalio.client import Client


async def relay_events(client: Client, prompt: str) -> str:
    handle = await client.start_workflow(
        AssistantWorkflow.run, prompt, id=f'assistant-{uuid4()}', task_queue='my-task-queue'
    )
    async for event in durability.stream_agent_events(client, handle, output_type=str):
        ...  # forward `event` to the frontend over SSE
    return await handle.result()
```

প্রতিটি স্বাধীন workflow শৃঙ্খলকে একটি অনন্য workflow ID দিন। Continue-as-new পুরো শৃঙ্খল জুড়ে ওই ID নিজে থেকে রাখে, তাই একটি সম্পর্কহীন workflow-এর জন্য এটি পুনর্ব্যবহার করবেন না।

এটি কার্যত workflow সীমা জুড়ে একটি durable [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events]: একই [`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent], ক্রমানুসারে, রানের ফল বহন করা [`AgentRunResultEvent`][pydantic_ai.run.AgentRunResultEvent] দিয়ে শেষ — শুধু event-গুলো এখানে পৌঁছাতে আরেকটি process পেরিয়ে এসেছে। তাই রান শেষ হলে `async for` নিজে থেকে শেষ হয়; কখন থামতে হবে জানতে আলাদা সংকেত লাগে না।

`async with` ব্লক থেকে বেরোনোই এটি কাজ করায়। একটি Workflow Stream workflow নিজেই পরিবেশন করে, তাই workflow ফেরত দিলে এর stream আর পড়া যায় না আর একজন subscriber যা এখনও poll করেনি তা হারিয়ে যায়। ব্লকটি workflow খোলা রাখে যতক্ষণ না একজন subscriber শেষ event স্বীকার করে — নিজে থেকে, `stream_agent_events()`-এর ভেতর থেকে। কেউ না দেখলে সেটা error নয়: অপেক্ষা `drain_timeout` (ডিফল্ট 30 সেকেন্ড) দিয়ে সীমিত, আর যেকোনো ক্ষেত্রে workflow-এর ফলই চূড়ান্ত।

##### একটি UI protocol চালানো { #driving-a-ui-protocol }

যেহেতু stream একটি `AgentRunResultEvent`-এ শেষ হয়, এটি ঠিক তা-ই যা একটি [`UIAdapter`][pydantic_ai.ui.UIAdapter] গ্রহণ করে, তাই একটি HTTP handler workflow শুরু করে topic থেকে সরাসরি একটি [UI event stream protocol](../ui/overview.md) পরিবেশন করতে পারে — `on_complete`-সহ, যা in-process রানের মতোই রানের ফল পায়।

adapter-এর দুটি কাজ সীমার দুই পাশে ভাগ হয়: HTTP handler রিকোয়েস্টকে একটি protocol stream-এ বদলায়, আর workflow একই রিকোয়েস্ট body থেকে রানের আর্গুমেন্ট আবার তৈরি করে।

```python title="temporal_workflow_streams_ui_workflow.py"
@workflow.defn
class ChatWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.init
    def __init__(self, body: bytes) -> None:
        self.events = AgentEventStream()

    @workflow.run
    async def run(self, body: bytes) -> str:
        adapter = VercelAIAdapter(agent=agent, run_input=VercelAIAdapter.build_run_input(body))
        async with self.events:
            result = await agent.run(
                message_history=adapter.messages,
                deferred_tool_results=adapter.deferred_tool_results,
                conversation_id=adapter.conversation_id,
            )
        return result.output
```

handler সেই workflow একটি ID-তে শুরু করে যাতে frontend ফিরে আসতে পারে, আর topic stream করে:

```python title="temporal_workflow_streams_ui_handler.py"
from starlette.requests import Request
from starlette.responses import Response

from pydantic_ai.ui.vercel_ai import VercelAIAdapter


async def post_chat(request: Request) -> Response:
    body = await request.body()
    run_input = VercelAIAdapter.build_run_input(body)

    handle = await client.start_workflow(
        ChatWorkflow.run,
        body,
        id=f'chat-{run_input.id}-{uuid4()}',
        task_queue='my-task-queue',
    )

    adapter = VercelAIAdapter(agent=agent, run_input=run_input)
    events = durability.stream_agent_events(client, handle, output_type=str)
    return adapter.streaming_response(adapter.transform_stream(events))
```

workflow-ই queue। এটি শুরু করা রানটি একটি Temporal worker-কে দেয়, আর HTTP রিকোয়েস্ট শুধু সেই worker যা তৈরি করে তার একজন subscriber: এটি রান না ছুঁয়ে চলে যেতে পারে, Temporal রানের activity নিজেই retry করে, আর রানটি একে শুরু করা process-এর পরও টিকে থাকে।

এর মানে frontend ফিরেও আসতে পারে। workflow ID কথোপকথনের পাশে রাখুন — কথোপকথনে আপনি আগে থেকে যে মালিকানা প্রয়োগ করেন তার অধীনে — আর একটি দ্বিতীয় endpoint একটি পুনঃসংযোগকারী client-কে এমন একটি রানে আবার যুক্ত করে যা সে শুরু করেনি:

```python title="temporal_workflow_streams_ui_reattach.py"
async def get_chat(request: Request) -> Response:
    # Resolve the run through the conversation the caller owns. A workflow ID taken
    # straight off the path would let anyone replay anyone else's conversation, since
    # a Temporal handle carries no authorization of its own.
    chat = await load_chat(request.path_params['chat_id'], user=request.state.user)
    handle = client.get_workflow_handle(chat.workflow_id)

    adapter = VercelAIAdapter(agent=agent, run_input=chat.run_input)
    events = durability.stream_agent_events(client, handle, output_type=str)
    return adapter.streaming_response(adapter.transform_stream(events))
```

ডিফল্ট `from_offset=0` থেকে subscribe করা রানের এ পর্যন্ত প্রকাশিত প্রতিটি event replay করে তারপর লাইভ চলতে থাকে, তাই একটি refresh করা tab বাক্যের মাঝখান থেকে না ধরে পুরো বার্তা আবার তৈরি করে। একটি client যার কাছে পাওয়া জিনিস এখনও আছে, সে এর বদলে `from_offset=offset + 1` দিয়ে বাকিটা ধারাবাহিকতা হিসেবে নিতে পারে; দেখুন [Reconnecting](#reconnecting)।

জানালাটি সীমিত: যে রানের শেষ event কেউ স্বীকার করে না, তা `AgentEventStream`-এর `drain_timeout` (ডিফল্ট 30 সেকেন্ড) পরে শেষ হয়, আর এর stream এর সাথে চলে যায়। এর চেয়ে দেরিতে পুনঃসংযোগকারী একটি client রানের ফলাফল topic থেকে নয়, `handle.result()` থেকে পায়; আপনার client-দের লম্বা জানালা দরকার হলে `drain_timeout` বাড়ান।

##### পুনঃসংযোগ { #reconnecting }

Workflow Streams offset-চিহ্নিত, তাই যে consumer বিচ্ছিন্ন হয় সে যেখানে থেমেছিল সেখান থেকে আবার শুরু করতে পারে — যা সাধারণ in-process streaming দিতে পারে তার চেয়ে বেশি। এগোনোর সাথে [`offset`][pydantic_ai.durable_exec.temporal.DurableAgentRunEvents.offset] চেকপয়েন্ট করুন আর `from_offset=offset + 1` দিয়ে আবার সংযোগ করুন:

```python title="temporal_workflow_streams_resume.py"
from temporalio.service import RPCError

last_offset = -1
while True:
    events = durability.stream_agent_events(client, handle, from_offset=last_offset + 1)
    try:
        async for event in events:
            print(event)  # forward to the frontend over SSE
            last_offset = events.offset
    except RPCError:
        continue  # the connection dropped: resubscribe at the next offset
    break  # the iterator ended on its own, so the run is over

return await handle.result()  # the output, or the workflow's failure
```

`async for`-এর একটি পরিষ্কার সমাপ্তি মানে রান শেষ, এটি একটি ফল দিক বা না দিক:
সফল হলে `events.result` হলো রানের `AgentRunResult` আর workflow অন্যভাবে শেষ হলে `None`, আর সেক্ষেত্রে `handle.result()` ব্যর্থতা বা বাতিল প্রচার করে। শুধু একটি বাধাপ্রাপ্ত iteration-এর জন্যই আবার subscribe করা মূল্যবান।

Offset প্রতি topic-এ নয়, পুরো stream জুড়ে চলে, তাই একটি topic-ছাঁকা subscription সেখানে ফাঁক দেখে যেখানে workflow অন্য একটি topic-এ প্রকাশ করেছে — এজন্যই এগুলো গোনার বদলে stream থেকে পড়তে হয়।

##### কী প্রকাশ করবেন তা বাছা { #choosing-what-to-publish }

একটি মডেল stream প্রতি token-এ একটি [`PartDeltaEvent`][pydantic_ai.messages.PartDeltaEvent] তৈরি করে, আর প্রতিটি প্রকাশিত event রানের পুরো সময় workflow-এর state-এ থাকে। খরচ আর workflow-এর আকার দুটোই কম রাখতে, একটি খালি নামের বদলে একটি [`WorkflowStreamTopic`][pydantic_ai.durable_exec.temporal.WorkflowStreamTopic] দিন আর ছাঁকুন:

```python title="temporal_workflow_streams_filter.py"
from pydantic_ai.durable_exec.temporal import TemporalDurability, WorkflowStreamTopic
from pydantic_ai.messages import PartDeltaEvent

TemporalDurability(
    event_stream_topic=WorkflowStreamTopic(
        'agent-events',
        events=lambda event: not isinstance(event, PartDeltaEvent),  # skip per-token deltas
    )
)
```

শেষ `AgentRunResultEvent` সবসময় প্রকাশিত হয়, কারণ এটিই একটি subscription শেষ করে।

ভেতরে, লাইভ মডেল stream প্রকাশ করে [`workflow_stream_event_handler()`][pydantic_ai.durable_exec.temporal.workflow_stream_event_handler], যা একটি সাধারণ `EventStreamHandler` ফেরত দেয়, যা আপনি নিজে জোড়া দিতে বা মোড়াতে পারেন। `event_stream_topic` পছন্দ করুন: এটি workflow কোড থেকে রানের workflow-পক্ষের event আর একটি subscription শেষ করা শেষ event-ও প্রকাশ করে, যার কোনোটিই একা একটি handler পারে না।

/// note | সতর্কতা

- Workflow Streams প্রতি roundtrip-এ মোটামুটি 100ms দেরি যোগ করে (topic-এর `batch_interval` দিয়ে সমন্বয়যোগ্য); এগুলো একটি UI চালানোর উপযোগী, রিয়েল-টাইম ভয়েসের মতো অতি-কম-দেরির ক্ষেত্রে নয়।
- প্রতিটি `stream_agent_events()` subscription Temporal সার্ভিসের বিপরীতে একটি long-poll ধরে রাখে, তাই প্রতি frontend সংযোগে একটি খুললে আপনার Temporal ব্যবহার ব্যবহারকারীর সংখ্যার সাথে বাড়ে আর Temporal Cloud-এর সংযোগ-সীমায় পড়তে পারে। প্রতি workflow রানে একটি consumer চালান আর এর event নিজে frontend সংযোগে ছড়িয়ে দিন (যেমন pub/sub বা একটি SSE broadcast দিয়ে); প্রতি subscriber-এ একটি subscription ডেভেলপমেন্টে কাজ করে আর সীমায় ভেঙে পড়ে।
- মডেল event model-request activity-র ভেতর থেকে প্রকাশিত হয়, তাই ওই activity retry করলে এর event নতুন offset-এ আবার প্রকাশিত হয়। Consumer-দের নকল সহ্য করা উচিত। workflow কোড থেকে প্রকাশিত event — টুল event আর শেষ event — প্রভাবিত হয় না, কারণ replay log-এ যোগ না করে log আবার তৈরি করে।
- stream টেকসই, তাই event ভিন্ন Pydantic AI version চালানো process তৈরি আর গ্রহণ করতে পারে। event-এর রূপ একটি major version-এর ভেতরে স্থিতিশীল; producer আর consumer একই major version-এ রাখুন।
- একটি iterator একটি এজেন্ট রান কভার করে। যে workflow এজেন্টকে বারবার চালায় তা প্রতি রানে একটি শেষ event প্রকাশ করে, তাই যে consumer পরেরটি চায় সে `from_offset=offset + 1` দিয়ে আবার সংযোগ করে।
- শেষ event প্রকাশিত হয় প্রতিটি capability ফল রূপান্তর করার পর, কিন্তু রান lifecycle-এর নিজস্ব সমাপ্তির আগে, যা capability সিস্টেমের কিছুই মোড়ায় না। ওই শেষ ধাপে বাতিল হওয়া একটি রান একটি ফল প্রকাশ করে তারপর ব্যর্থ হয়, তাই workflow-এর ফেরত মানই চূড়ান্ত ফলাফল থাকে।
- প্রাথমিক subscription অনুরোধকৃত workflow execution-এ আটকানো, কিন্তু continue-as-new-এর পর Temporal SDK একটি আটকানো-নয় workflow ID দিয়ে শৃঙ্খল অনুসরণ করে। একজন subscriber যখন এখনও শৃঙ্খল অনুসরণ করতে পারে, তখন একটি স্বাধীন execution-এর জন্য ওই workflow ID পুনর্ব্যবহার করবেন না, নইলে এটি নতুন execution-এ যুক্ত হয়ে যেতে পারে।
- লাইভ event শুধু workflow-এর বাইরের consumer-দের কাছে পৌঁছায়; workflow কোডের ভেতরে `run_stream_events()` তবুও জমায়।

///

একটি টুল বা একটি event stream handler থেকে [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] দিয়ে event তৈরি করা বর্তমানে সমর্থিত নয়, কারণ এগুলো এমন activity-র ভেতরে চলে যা রানের event stream-এ পৌঁছাতে পারে না; এটি করলে একটি `UserError` ওঠে। এটি অ্যাপ্লিকেশন টুলের তৈরি [custom event](../agent.md#custom-events) আর একটি capability-র নিজের টুলের তৈরি [capability event](../capabilities/overview.md#capability-events) দুটোই কভার করে। এর বদলে [capability](../capabilities/overview.md) hook থেকে event তৈরি করুন, যা workflow-এ চলে। activity থেকে তৈরির সমর্থন ট্র্যাক হচ্ছে [pydantic-ai#7971](https://github.com/pydantic/pydantic-ai/issues/7971)-এ।

[`@on_event`][pydantic_ai.capabilities.on_event] দিয়ে নিবন্ধিত capability listener একটি durable এককের বদলে workflow কোডে চলে, তাই এগুলো প্রতিটি workflow replay-তে আবার চলে আর deterministic হতে হবে। I/O একটি durability `event_stream_handler=`-এ রাখুন, যা নিজের activity-তে চলে।

যেহেতু মডেল stream activity-র ভেতরে গ্রহণ হয়, workflow-পক্ষ থেকে এটি বাতিল করা (যেমন [`AgentStream.cancel()`][pydantic_ai.result.AgentStream.cancel] দিয়ে) durable সীমা জুড়ে পাওয়া যায় না। একটি চলমান মডেল রিকোয়েস্ট থামাতে, Temporal workflow বাতিল করুন: বাতিলটি activity-তে পৌঁছায় (এর heartbeat দিয়ে), যা activity শেষ হওয়ার আগে যেকোনো সার্ভার-পক্ষের job বাতিল করে।

পুরো-রান বাতিল (দেখুন [Cancelling a Run](../agent.md#cancelling-a-run)) একই ভাগ মেনে চলে, Temporal-নির্দিষ্ট ফলাফলসহ:

- workflow কোড থেকে [`AgentRun.cancel()`][pydantic_ai.run.AgentRun.cancel] ডাকলে একটি সাধারণ অ্যাপ্লিকেশন ফলাফল হিসেবে [`RunCancelled`][pydantic_ai.exceptions.RunCancelled] ওঠে: যে workflow এটি ধরে তা *Cancelled* হিসেবে শেষ না হয়ে স্বাভাবিকভাবে শেষ হয়, আর রান replay-deterministic থাকে। একটি না-ধরা `RunCancelled` workflow-কে একটি টাইপ করা অ্যাপ্লিকেশন error হিসেবে ব্যর্থ করে, আর রান state ব্যর্থতার সীমা পেরোয় না -- [`all_messages()`][pydantic_ai.exceptions.RunCancelled.all_messages] দরকার হলে workflow-এর ভেতরে এটি ধরুন।
- [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel]-এর জন্য রানের একই process-এ থাকা লাগে, তাই একটি activity-র ভেতরে চলা একটি টুল থেকে এটি ডাকলে আটকে না থেকে একটি স্পষ্ট [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।
- [`CancellationToken`][pydantic_ai.CancellationToken]-ও একই-process state আর একটি Temporal durable রানে দেওয়া যায় না; এর বদলে Temporal workflow বাতিল করুন।
- Temporal workflow নিজেই বাতিল করা একটি বাইরের বাতিল থাকে: `CancelledError` প্রচারিত হতে থাকে আর workflow তবুও *Cancelled* হিসেবে শেষ হয়।

[`Agent.run_stream_sync()`][pydantic_ai.agent.Agent.run_stream_sync] workflow কোডের জন্য নয়: এর জন্য কোনো চলমান event loop না থাকা লাগে আর এটি `run_stream()` মোড়ায়। [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-এর অধীনে, ওপরের জমানো async streaming API বা একটি event stream handler-সহ [`Agent.run()`][pydantic_ai.agent.Agent.run] ব্যবহার করুন। একটি workflow-এর বাইরে, `TemporalDurability`-সহ একটি এজেন্ট একটি সাধারণ এজেন্টের মতো আচরণ করে, তাই `run_stream_sync()` স্বাভাবিকভাবে কাজ করে। (Wrapper `TemporalAgent` workflow-এর ভেতরে `run_stream` নিষেধ করে — সেখানে `run` + event stream handler ব্যবহার করুন।)

### রানের timeout { #run-timeouts }

একটি রানের [`timeout=`](../timeouts.md#bounding-a-whole-run) একটি workflow-এর ভেতরে কাজ করে। এর সময়সীমা হিসাব হয় `workflow.now()` থেকে আর একটি workflow timer দিয়ে প্রয়োগ হয়, তাই একটি replay করা workflow একই সময়সীমা হিসাব করে আর একই timer চালায়। এটি চালু হলে, চলমান activity এর `cancellation_type` অনুযায়ী বাতিল হয়, আর রান workflow কোডে [`RunTimedOut`][pydantic_ai.exceptions.RunTimedOut] তোলে। `RunCancelled`-এর মতো, একটি না-ধরা `RunTimedOut` workflow-কে একটি টাইপ করা অ্যাপ্লিকেশন error হিসেবে ব্যর্থ করে, তাই [`all_messages()`][pydantic_ai.exceptions.RunCancelled.all_messages] দরকার হলে workflow-এর ভেতরে এটি ধরুন।

[`RunContext.deadline`][pydantic_ai.tools.RunContext.deadline] activity-তে serialize হয়, তাই একটি activity-র ভেতরে একটি টুলের চালানো একটি এজেন্ট রানও সময়সীমা উত্তরাধিকারসূত্রে পায়। অবচিত `TemporalAgent` `timeout=` প্রত্যাখ্যান করে।

সময়সীমা এজেন্ট রান সীমিত করে, workflow নয়: একটি workflow-এর `execution_timeout` রানের ইতিহাস না লিখেই এটি শেষ করবে, তাই এটি শুধু একটি শেষ রক্ষাকবচ হিসেবেই ব্যবহার করতে থাকুন।

### স্থগিত turn আর background mode { #suspended-turns-and-background-mode }

কিছু provider একটি মডেল turn মাঝপথে থামাতে পারে (Anthropic `pause_turn`) বা একে একটি সার্ভার-পক্ষের job হিসেবে চালাতে পারে যা প্রস্তুত না হওয়া পর্যন্ত poll করা হয় ([OpenAI background mode](../models/openai.md#background-mode))। Pydantic AI এমন একটি স্থগিত turn শেষ না হওয়া পর্যন্ত স্বচ্ছভাবে চালিয়ে যায়। প্রতিটি অংশ একটি আলাদা model request activity-তে চলে, আর workflow অংশগুলোর মাঝে স্থগিত [`ModelResponse`][pydantic_ai.messages.ModelResponse] আর এর background job ID চেকপয়েন্ট করে। চূড়ান্ত response মেলানো হয় আর usage একবার লেখা হয়। একটি স্থগিত response-এ শেষ হওয়া একটি [`message_history`](../message-history.md) সেই response প্রথম activity-তে দিয়ে আবার চলে।

এর কয়েকটি পরিচালনাগত প্রভাব আছে:

- **Timeout আর heartbeat**: একটি provider round trip-এর জন্য `start_to_close_timeout` আর `heartbeat_timeout` ঠিক করুন। একটি [`request_timeout`](../timeouts.md#model-request-deadlines) মডেল সেটিং turn-এর সব অংশ কভার করে: এটি একটি workflow timer হিসেবে চলে, আর চালু হলে চলমান activity বাতিল করে। একটি [`FallbackModel`](../models/overview.md#fallback-model)-এ, সময়সীমা এর বদলে activity-র ভেতরে চলে, আর বাছা মডেলের সময়সীমা এক অংশের activity থেকে পরেরটিতে বহন হয়। Model request activity-কে ডিফল্টভাবে 30 সেকেন্ডের একটি `heartbeat_timeout` দেওয়া হয়; অন্য activity জুড়ে heartbeat কীভাবে কাজ করে তা দেখুন [Activity Configuration](#activity-configuration)-এ।
- **Retry আর অপেক্ষা**: একটি ব্যর্থ অংশ স্বাধীনভাবে retry করে। background poll-এর মাঝের দেরি টেকসই Temporal timer ব্যবহার করে আর activity-র wall-clock সময় খরচ করে না।
- **বাতিল**: একটি error একটি স্থগিত job পরিত্যাগ করলে, এর provider teardown একটি নির্দিষ্ট cancellation activity-তে চলে।

/// note | মনে রাখুন

আপনি যদি নিজের `serialize_run_context`-সহ একটি নিজস্ব [`TemporalRunContext`][pydantic_ai.durable_exec.temporal.TemporalRunContext] subclass ব্যবহার করেন, `usage` আর `usage_limits` ফিল্ড অন্তর্ভুক্ত রাখুন: activity-র ভেতরে চলা টুল আর capability এগুলো [`RunContext`][pydantic_ai.tools.RunContext] থেকে পড়ে, যেমন রানের বাকি [usage budget](../agent.md#usage-limits)-এর সাথে মানিয়ে নিতে।

///

### দীর্ঘ-চলা এজেন্টের জন্য Continue-as-new { #continuing-as-new-for-long-running-agents }

একটি Temporal workflow-এর execution history প্রায় 50,000 event বা 50MB-তে সীমিত। যথেষ্ট turn-যুক্ত একটি এজেন্ট রান শেষ পর্যন্ত সেই সীমায় পৌঁছাতে পারে। Temporal-এর উত্তর হলো [`continue_as_new`](https://docs.temporal.io/develop/python/continue-as-new), যা বর্তমান workflow execution শেষ করে আর আপনার দেওয়া আর্গুমেন্ট বহন করে একটি পরিষ্কার ইতিহাসসহ একটি নতুন শুরু করে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি খাতার পাতা শেষ হয়ে গেলে আপনি নতুন খাতা খোলেন, আর প্রথম পাতায় লিখে রাখেন "আগের খাতার সারাংশ: ..."। `continue_as_new` ঠিক তাই করে — পুরনো ইতিহাস বন্ধ, নতুন workflow শুরু, কিন্তু কথোপকথন (message history) আর usage আর্গুমেন্ট হিসেবে নতুনটিতে চলে যায়।

///

[`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] এটি এমন একটি বিন্দুতে করতে পারে যেখান থেকে এজেন্ট আবার চলতে পারে। `continue_as_new` দিন, একটি sync বা async ফাংশন যা রানের [`RunContext`][pydantic_ai.tools.RunContext] পায়। প্রতিটি মডেল রিকোয়েস্টের ঠিক আগে, capability `workflow.info().is_continue_as_new_suggested()` যাচাই করে। Temporal চালিয়ে যাওয়ার পরামর্শ দিলে, এটি আপনার ফাংশন ডাকে, যা আপনার workflow-এর `@workflow.run` মেথডের আবার চলার জন্য দরকারি আর্গুমেন্টসহ `workflow.continue_as_new()` ডাকে, এ পর্যন্ত কথোপকথনসহ। ওই বিন্দুতে, আগের ধাপের প্রতিটি টুল ফল ইতিমধ্যে ইতিহাসে আছে আর কিছুই চলমান নেই।

কখন চালিয়ে যাওয়ার পরামর্শ দেবে তা Temporal সার্ভার ঠিক করে, ইতিহাসের event সংখ্যা আর আকারের ভিত্তিতে। আগে বা পরে চালিয়ে যেতে, এর `limit.historyCount.suggestContinueAsNew` আর `limit.historySize.suggestContinueAsNew` [dynamic config](https://docs.temporal.io/references/dynamic-configuration) মান সমন্বয় করুন, যা প্রতি namespace-এ সেট করা যায়।

একটি async ফাংশন হিসেবে, আপনারটি প্রথমে [একটি activity চালাতে](https://docs.temporal.io/develop/python/core-application#activity-execution) পারে, যেমন ইতিহাস অন্য কোথাও রেখে এর বদলে একটি রেফারেন্স পাঠাতে। এটি `workflow.continue_as_new()` না ডেকেও ফেরত দিতে পারে, এমন একটি শর্তের অপেক্ষায় যা শুধু আপনার অ্যাপ্লিকেশন বিচার করতে পারে; তখন পরের মডেল রিকোয়েস্টের আগে এটি আবার ডাকা হয়। `continue_as_new=None` সেট করা, যা ডিফল্ট, সুবিধাটি বন্ধ রাখে।

/// warning | `continue_as_new` আর্গুমেন্ট Temporal-এর প্রতি-payload আকার-সীমা ভাগ করে

activity আর workflow input-এর মতো, `continue_as_new`-এ দেওয়া প্রতিটি আর্গুমেন্ট Temporal-এর প্রতি-payload আকার-সীমার বিপরীতে গোনা হয় (দেখুন [Large Payloads](#large-payloads))। আপনার বহন করা ইতিহাস সীমিত রাখুন, যেমন [`ProcessHistory`][pydantic_ai.capabilities.ProcessHistory]-এর মতো একটি history-processing capability দিয়ে compact করে, বা [বড় payload আপনার নিজের storage-এ সরিয়ে](#offloading-payloads-to-your-own-storage)।

///

```python title="temporal_continue_as_new.py"
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import (
    PydanticAIPlugin,
    PydanticAIWorkflow,
    TemporalDurability,
)
from pydantic_ai.messages import ModelMessage
from pydantic_ai.tools import RunContext
from pydantic_ai.usage import RunUsage, UsageLimits


def continue_as_new(ctx: RunContext) -> None:
    workflow.continue_as_new(
        args=[None, ctx.messages, ctx.usage, ctx.usage_limits],
    )


agent = Agent(
    'openai:gpt-6.1-sol',
    name='investigator',
    capabilities=[TemporalDurability(continue_as_new=continue_as_new)],
)


@workflow.defn
class InvestigatorWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(
        self,
        prompt: str | None,
        message_history: list[ModelMessage] | None = None,
        usage: RunUsage | None = None,
        usage_limits: UsageLimits | None = None,
    ) -> str:
        result = await agent.run(
            prompt,
            message_history=message_history,
            usage=usage,
            usage_limits=usage_limits,
        )
        return result.output


async def main():
    client = await Client.connect('localhost:7233', plugins=[PydanticAIPlugin()])
    async with Worker(client, task_queue='investigator', workflows=[InvestigatorWorkflow]):
        await client.execute_workflow(
            InvestigatorWorkflow.run,
            args=['Start the investigation.'],
            id='investigator-1',
            task_queue='investigator',
        )
```

ধারাবাহিকতা prompt হিসেবে `None` দেয়: বহন করা ইতিহাস ইতিমধ্যে সেই রিকোয়েস্টে শেষ হয় যা মডেল পেতে যাচ্ছিল (যেমন সর্বশেষ টুল ফল), তাই নতুন রান একটি নতুন user বার্তা যোগ না করে এটি যেমন আছে তেমন পাঠায়।

সীমা পেরিয়ে `usage` আর `usage_limits` বহন করা `request_limit`-এর মতো [usage limits](../agent.md#usage-limits)-কে প্রতিটি ধারাবাহিকতায় নতুন করে শুরু না করে পুরো যৌক্তিক রান সীমিত রাখতে দেয়। `message_history`, `usage` আর `usage_limits` এখানে সাধারণ workflow আর্গুমেন্ট, `TemporalDurability`-এর নিজস্ব কোনো সুবিধা নয়। ফাংশন আর এগুলো গ্রহণ করা `@workflow.run` signature আপনার মতো করে গড়ার।

### রানের সময় মডেল বাছাই { #model-selection-at-runtime }

[`Agent.run(model=...)`][pydantic_ai.agent.Agent.run] সাধারণত মডেল string (যেমন `'openai:gpt-6.1-sol'`) আর মডেল instance দুটোই সমর্থন করে। Temporal-এর অধীনে, replay পদ্ধতির জন্য একটি মডেল instance serialize করা যায় না, আর এর `model_id` string থেকে একটি আবার তৈরি করলে একটি *ভিন্ন* মডেল তৈরি হবে — worker-এর environment যে provider বোঝায় তাতে একই মডেলের নাম, তাই রিকোয়েস্ট অন্য credential নিয়ে অন্য endpoint-এ যাবে। তাই আগে থেকে নিবন্ধিত নয় এমন একটি instance একটি `UserError` দিয়ে প্রত্যাখ্যাত হয়। একটি workflow-এর ভেতরে একটি নির্দিষ্ট instance ব্যবহারের দুটি উপায় আছে:

- [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-তে একটি `models` dict দিয়ে এটি আগে নিবন্ধন করুন, তারপর নাম দিয়ে বা নিবন্ধিত instance সরাসরি `agent.run(model=...)`-এ দিয়ে এর রেফারেন্স দিন;
- একটি মডেল-নামের string দিন আর একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability দিয়ে worker-এ instance তৈরি করুন — সঠিক পছন্দ যখন মডেল রানের `deps`-এর ওপর নির্ভর করে, যেমন প্রতি-ব্যবহারকারী credential।

মডেল-নামের string নিজে কখনো নিবন্ধন করতে হয় না। তৈরির সময় সেট করা এজেন্টের নিজের মডেল সবসময় ডিফল্ট হিসেবে উপলব্ধ; তৈরির সময় এজেন্টের একটি মডেল সেট থাকা বাধ্যতামূলক।

মডেল string প্রত্যাশামতো কাজ করে। একটি মডেল string কীভাবে তৈরি হবে তা কাস্টমাইজ করতে — একটি নিজস্ব provider, কনফিগারেশন থেকে বসানো API key, রানের `deps`-এ বহন করা প্রতি-ব্যবহারকারী credential — `TemporalDurability`-র আগে একটি [`ResolveModelId`](../capabilities/resolve-model-id.md) capability যোগ করুন: এটি প্রতিটি string-এ প্রথম সুযোগ পায়, রান সেটআপের সময় আর activity-র ভেতরে মডেল আবার তৈরির সময় দুটোতেই, যেখানে resolver রানের আসল `deps` দিয়ে আবার চলে। যেহেতু resolver worker-এ আবার চলে, এটিকে একটি নির্দিষ্ট `(model_id, deps)`-এর জন্য deterministic হতে হবে আর বাইরের I/O করা চলবে না — credential `deps`-এ বহন করুন বা শুরুতে লোড করা কনফিগারেশনের ওপর close over করুন।

একাধিক মডেল আগে নিবন্ধন আর ব্যবহার কীভাবে করবেন তার একটি উদাহরণ:

```python title="multi_model_temporal.py"
import os

from temporalio import workflow

from pydantic_ai import Agent
from pydantic_ai.capabilities import ResolveModelId
from pydantic_ai.durable_exec.temporal import PydanticAIWorkflow, TemporalDurability
from pydantic_ai.models import Model, ModelResolutionContext, infer_model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

# Create models from different providers
default_model = OpenAIResponsesModel('gpt-6.1-sol')
fast_model = AnthropicModel('claude-haiku-5-5')
reasoning_model = GoogleModel('gemini-4-argon')


# Optional: customize how model-name strings are built.
def resolve_model(ctx: ModelResolutionContext, model_id: str) -> Model | None:
    if model_id.startswith('openai:'):
        provider = OpenAIProvider(api_key=os.environ['OPENAI_API_KEY'])
        return infer_model(model_id, provider_factory=lambda _: provider)
    return None  # everything else takes the default `infer_model` path


agent = Agent(
    default_model,
    name='multi_model_agent',
    capabilities=[
        ResolveModelId(resolve_model),  # Optional
        TemporalDurability(
            models={
                'fast': fast_model,
                'reasoning': reasoning_model,
            },
        ),
    ],
)


@workflow.defn
class MultiModelWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str, use_reasoning: bool, use_fast: bool) -> str:
        if use_reasoning:
            # Select by registered name
            result = await agent.run(prompt, model='reasoning')
        elif use_fast:
            # Or pass the registered instance directly
            result = await agent.run(prompt, model=fast_model)
        else:
            # Or pass a model string (resolved by `ResolveModelId` if it matches)
            result = await agent.run(prompt, model='openai:gpt-6-luna')
        return result.output
```

### রানের সময় toolset { #toolsets-at-runtime }

durable মোড়ানো লাগে এমন প্রতিটি চালানো toolset এজেন্ট constructor-এ দিন, যাতে workflow চলার আগে এর activity worker-এ নিবন্ধিত হতে পারে। এতে [`DynamicToolset`][pydantic_ai.toolsets.DynamicToolset] অন্তর্ভুক্ত: একে একটি স্পষ্ট `id` দিন আর `Agent(toolsets=[...])`-এ দিন। [`@agent.toolset`][pydantic_ai.agent.Agent.toolset] decorator engine-এর durable একক তৈরির পরে নিবন্ধন করে, তাই [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-এর অধীনে একটি workflow-এর ভেতরে এটি ব্যবহার করলে একটি `UserError` ওঠে। অবচিত `TemporalAgent` এই যাচাই চালায় না: একটি workflow-এর ভেতরে এটি মোড়ানোর সময় স্থির হওয়া toolset তালিকা চালায়, তাই এত দেরিতে নিবন্ধিত একটি toolset নিঃশব্দে রান থেকে বাদ পড়ে।

`agent.run(toolsets=...)` দিয়ে প্রতি রানে বাড়তি toolset দেওয়া যায়, কিন্তু শুধু সেই toolset সমর্থিত যাদের durable মোড়ানো লাগে না: [`ExternalToolset`][pydantic_ai.toolsets.ExternalToolset]-এর মতো না-চালানো toolset, যার টুল এজেন্ট রানের বাইরে চলে, আর [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] যার সব টুল [`metadata={'temporal': False}`](#per-tool-activity-config) দিয়ে activity মোড়ানো থেকে বেরিয়ে আসে। অন্য চালানো toolset ([`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] আর [`MCPToolset`][pydantic_ai.mcp.MCPToolset]) আর dynamic toolset এজেন্ট তৈরির সময় সেট করতে হবে, যাতে workflow চলার আগে এদের activity worker-এ নিবন্ধিত হতে পারে; রানের সময় এগুলো দিলে একটি `UserError` ওঠে।

একটি workflow-এর ভেতরে [`agent.override(toolsets=...)`][pydantic_ai.agent.AbstractAgent.override] দিয়ে বদলানো toolset-ও একই নিয়মে বাঁধা, কারণ এগুলোও এজেন্টের activity নিবন্ধনের পরে আসে। রানের সময় যোগ করা একটি toolset এজেন্ট তৈরির সময়ের কোনোটির `id`-ও পুনর্ব্যবহার করতে পারে না, কারণ `id`-ই চিহ্নিত করে একটি টুল কল কোন নিবন্ধিত toolset-এর activity-তে পাঠানো হবে।

## Activity কনফিগারেশন { #activity-configuration }

Timeout আর retry policy-র মতো Temporal activity কনফিগারেশন কাস্টমাইজ করা যায় [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] constructor-এ [`temporalio.workflow.ActivityConfig`](https://python.temporal.io/temporalio.workflow._activities.ActivityConfig.html) অবজেক্ট দিয়ে:

- `activity_config`: সব activity-র জন্য ব্যবহারের মূল Temporal activity config। কোনো config না দিলে, 60 সেকেন্ডের একটি `start_to_close_timeout` ব্যবহৃত হয়।
- `model_activity_config`: model request activity-র জন্য ব্যবহারের Temporal activity config। এটি মূল activity config-এর সাথে মেলানো হয়। Model request activity [durable-execution retry স্তর](../retries.md#the-layers) বহন করে: Temporal-এর ডিফল্ট `RetryPolicy.maximum_attempts` `0` মানে মডেল রিকোয়েস্টের সীমাহীন পুনরায় চালানো — SDK client আর transport-এর retry-র সাথে এটি কীভাবে জমা হয় তা দেখুন [Retry multiplication](../retries.md#retry-multiplication)-এ।
- `event_stream_handler_activity_config`: event stream handler activity-র জন্য ব্যবহারের Temporal activity config। এটি মূল activity config-এর সাথে মেলানো হয়।
- `toolset_activity_config`: ID দিয়ে চিহ্নিত নির্দিষ্ট toolset-এর get-tools আর call-tool activity-র জন্য ব্যবহারের Temporal activity config। এটি মূল activity config-এর সাথে মেলানো হয়।

যেহেতু `ActivityConfig` একটি `TypedDict`, একটি ভুল বানান বা ভুল জায়গার key রানের সময় Python ধরে না আর শুধু তখনই ব্যর্থ হবে যখন workflow-এর ভেতরে config Temporal-কে দেওয়া হয়, যেখানে ব্যর্থতা অনির্দিষ্টভাবে retry হয়। তাই [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] তৈরির সময় config key যাচাই হয়, তাই Temporal চেনে না এমন একটি key শুরুতেই একটি `UserError` তোলে।

প্রতি-টুল activity config টুলেই থাকে — নিচে দেখুন [Per-tool activity config](#per-tool-activity-config)।

Pydantic AI-এর নিবন্ধিত প্রতিটি activity চলার সময় background-এ heartbeat দেয়, যাতে একটি লম্বা-কিন্তু-সুস্থ activity-কে একটি crash করা worker ভেবে ভুল না হয় আর Temporal workflow বাতিল করা এতে পৌঁছাতে পারে — এটি কীভাবে একটি চলমান মডেল রিকোয়েস্ট থামায় তা দেখুন [Streaming](#streaming)-এ। ডিফল্টভাবে শুধু model request activity একটি `heartbeat_timeout` পায়, 30 সেকেন্ডের; অন্য যেকোনো activity-তে একটি সেট করা আপনার ওপর।

/// warning | event loop আটকাতে পারে এমন activity-তে `heartbeat_timeout` সেট করবেন না

Heartbeat একটি background task থেকে পাঠানো হয়, তাই যে activity ছাড় না দিয়ে event loop দখল করে রাখে — ধরুন একটি CPU-ভারী টুল ফাংশন — তা heartbeat দেওয়া বন্ধ করে আর timeout পেরোলে এর চেষ্টা ব্যর্থ হয়। এমন একটি activity-র জন্য শুধু `start_to_close_timeout` ভালো।

///

### প্রতি-টুল activity config { #per-tool-activity-config }

প্রতি-টুল activity config থাকে টুলের [`metadata`][pydantic_ai.toolsets.FunctionToolset.tool] ফিল্ডে — [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability] একটি `'temporal'` key খোঁজে। আপনি metadata সরাসরি টুল সংজ্ঞায় সেট করতে পারেন, বা [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] capability দিয়ে একগুচ্ছ টুলে প্রয়োগ করতে পারেন। পুরো selector শব্দভাণ্ডারের জন্য দেখুন [capabilities ডকুমেন্টেশন][pydantic_ai.capabilities.SetToolMetadata]।

```python title="temporal_per_tool_config.py"
from datetime import timedelta

from temporalio.workflow import ActivityConfig

from pydantic_ai import Agent
from pydantic_ai.capabilities import SetToolMetadata
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai.toolsets import FunctionToolset

toolset = FunctionToolset(id='research')


@toolset.tool_plain(metadata={'temporal': ActivityConfig(start_to_close_timeout=timedelta(minutes=5))})  # (1)!
async def fetch_paper(arxiv_id: str) -> str:
    ...


@toolset.tool_plain(metadata={'temporal': False})  # (2)!
async def now() -> str:
    ...


agent = Agent(
    'openai:gpt-6.1-sol',
    name='research',
    toolsets=[toolset],
    capabilities=[
        SetToolMetadata(  # (3)!
            tools=['fetch_paper', 'fetch_dataset'],
            temporal=ActivityConfig(start_to_close_timeout=timedelta(minutes=5)),
        ),
        TemporalDurability(),
    ],
)
```

1. Inline: টুল সংজ্ঞার পাশে activity config ঘোষণা করুন। প্রতি-টুল config toolset আর মূল config-এর ওপরে মেলানো হয়।
2. activity মোড়ানো পুরোপুরি এড়াতে `'temporal': False` সেট করুন (শুধু `async` টুলের জন্য বৈধ — sync টুলের সবসময় একটি activity লাগে, কারণ thread deterministic নয়)।
3. Selector-ভিত্তিক: [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] একগুচ্ছ টুলে একই metadata প্রয়োগ করে (`'all'`, একটি নামের লিস্ট, একটি dict, বা একটি callable)।

বেরিয়ে আসার এই সুযোগ শুধু function আর dynamic টুলে প্রযোজ্য। MCP টুল I/O করে আর সবসময় তাদের Temporal activity-তে চলে, তাই একটি MCP টুলে `metadata={'temporal': False}` একটি `UserError` তোলে।

/// tip | থার্ড-পার্টি টুল কনফিগার করা

যখন activity config টুল সংজ্ঞায় মানায় না — যেমন থার্ড-পার্টি প্যাকেজে সংজ্ঞায়িত টুল, বা একই timeout প্রোফাইল ভাগ করা কিন্তু ভিন্ন ফাইলে থাকা একগুচ্ছ টুল — তখন [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] সুপারিশকৃত পথ।

///

### Child workflow { #child-workflows }

একটি async ফাংশন টুল একটি activity-র বদলে একটি Temporal child workflow হিসেবে চলতে পারে। এটি কাজের
যখন টুলটি নিজের `TemporalDurability`-সহ একটি nested এজেন্ট চালায়: nested মডেল রিকোয়েস্ট আর
টুল কল নিজের timeout আর retry-সহ durable operation থাকে, parent-এর ইতিহাস না বাড়িয়ে child-এর আলাদা workflow history-তে লেখা হয়।

`'temporal'` metadata মান এমন একটি dictionary-তে সেট করুন যার একমাত্র key `'child_workflow'`। এর মান [`workflow.start_child_workflow()`](https://python.temporal.io/temporalio.workflow.html#start_child_workflow)-এর মতো একই অপশন নেয়:

```python title="temporal_child_workflow.py"
from datetime import timedelta

from temporalio import workflow
from temporalio.workflow import ChildWorkflowConfig

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import PydanticAIWorkflow, TemporalDurability
from pydantic_ai.toolsets import FunctionToolset

researcher = Agent(
    'openai:gpt-6.1-sol',
    name='researcher',
    capabilities=[TemporalDurability()],
)

delegation = FunctionToolset(id='delegation')


@delegation.tool_plain(
    metadata={
        'temporal': {
            'child_workflow': ChildWorkflowConfig(execution_timeout=timedelta(minutes=10))
        }
    }
)
async def research(topic: str) -> str:
    """Research a topic in depth."""
    result = await researcher.run(f'Research: {topic}')
    return result.output


lead = Agent(
    'openai:gpt-6.1-sol',
    name='lead',
    toolsets=[delegation],
    capabilities=[TemporalDurability()],
)


@workflow.defn
class LeadWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [lead, researcher]

    @workflow.run
    async def run(self, prompt: str) -> str:
        result = await lead.run(prompt)
        return result.output
```

প্রতিটি `research` কল একটি child workflow শুরু করে, আর `researcher` এজেন্টের মডেল রিকোয়েস্ট আর টুল কল parent-এর নয়, সেই child-এর ইতিহাসের activity। দুটি এজেন্টই `__pydantic_ai_agents__`-এ তালিকাভুক্ত করুন (বা প্রতিটির জন্য একটি [`AgentPlugin`][pydantic_ai.durable_exec.temporal.AgentPlugin] দিন), যাতে worker child workflow সংজ্ঞার পাশাপাশি nested এজেন্টের activity-ও নিবন্ধন করে।

`id` বাদ দিলে, child workflow ID হয় parent-এর workflow ID, তারপর workflow-এর deterministically তৈরি একটি UUID। `id`, `task_queue`, `execution_timeout`, `run_timeout`,
`task_timeout`, `id_reuse_policy`, `retry_policy`, `cron_schedule`, `cancellation_type`,
`parent_close_policy`, `memo`, `search_attributes`, `versioning_intent`, `static_summary`,
`static_details` আর `priority` অপশন Temporal-এ পৌঁছে দেওয়া হয়। টুলের body deterministic workflow কোড হিসেবে চলে, তাই একে I/O durable operation-এ দিতে হয়, যেমন একটি nested এজেন্টের activity। sync, dynamic বা MCP টুলের জন্য child workflow সমর্থিত নয়।

টুলের body-র তোলা একটি exception child workflow ব্যর্থ করে আর parent-এর টুল কলে পৌঁছায়, যেভাবে একটি ব্যর্থ activity পৌঁছাত। child এর `retry_policy` অনুযায়ী retry হয়, শুধু এমন error ছাড়া যা retry ঠিক করতে পারে না, যেমন একটি [`UserError`][pydantic_ai.exceptions.UserError], যা একটি activity-ও retry করে না।

plugin কনফিগার করার সময় একটি worker একটি toolset-এর child workflow নিবন্ধন করে, যদি ততক্ষণে toolset-এর একটি টুলে `child_workflow` metadata থাকে (`@agent.tool` দিয়ে যোগ করা টুলসহ) বা একটি
[`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] capability এটি সেট করে। এমন টুল ছাড়া এজেন্টের worker আগের মতোই শুধু তাদের activity নিবন্ধন করে। পরে প্রথম দেখা দেওয়া metadata, যেমন একটি রানের সময় টুল সংজ্ঞা নতুন করে লেখা একটি capability থেকে, টুল কলটি একটি `UserError` দিয়ে ব্যর্থ করে।

## Activity retry { #activity-retries }

Temporal-এর করা রিকোয়েস্ট ব্যর্থতার স্বয়ংক্রিয় retry-র ওপরে, Pydantic AI আর বিভিন্ন provider API client-এরও নিজস্ব রিকোয়েস্ট retry লজিক আছে। এগুলো একসাথে চালু করলে রিকোয়েস্ট প্রত্যাশার চেয়ে বেশিবার retry হতে পারে, ভুল `Retry-After` সামলানোসহ।

Temporal ব্যবহারের সময়, [transport retries](../retries.md#transport-retries) ব্যবহার না করা আর আপনার provider API client-এর নিজস্ব retry লজিক বন্ধ করা সুপারিশকৃত, যেমন একটি [custom `OpenAIProvider` API client](../models/openai.md#custom-openai-client)-এ `max_retries=0` সেট করে।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন Temporal 5 বার চেষ্টা করে, প্রতিটি চেষ্টায় SDK 2 বার retry করে (মোট 3), আর প্রতিটি SDK চেষ্টায় একটি retrying transport আরও 3 বার (মোট 4) — তাহলে মোট 5 × 3 × 4 = 60টি রিকোয়েস্ট একটি rate-limit ঘটনায়! তাই Temporal-এ retry একটি জায়গায় রাখুন: Temporal-এর retry policy-তে।

///

আপনি [activity configuration](#activity-configuration) দিয়ে Temporal-এর retry policy কাস্টমাইজ করতে পারেন।

একটি টুলের তোলা exception workflow কোডে পৌঁছায় Temporal-এর `ActivityError` হিসেবে, মূল exception-এর ক্লাসের নাম `cause.type`-এ।

একটি মডেল error ভিন্ন: [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-এ, একটি মডেল রিকোয়েস্টের তোলা একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError], যেমন একটি [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError], একটি `ActivityError` হিসেবে নয়, বরং নিজের রূপে, এর ফিল্ডসহ workflow কোডে পৌঁছায়। JSON-serialize-যোগ্য নয় এমন একটি ফিল্ডের মান, যেমন একটি অস্বাভাবিক response body, এর string রূপে পার হয়। এটি Pydantic AI-এর নিজস্ব error ক্লাসে প্রযোজ্য: আপনার সংজ্ঞায়িত একটি subclass তবুও একটি `ActivityError` হিসেবে আসে। এটিই `on_model_request_error` hook আর মডেল error সামলানো অন্য workflow-পক্ষের কোডকে Temporal থাকুক বা না থাকুক একইভাবে কাজ করতে দেয়। error workflow-এ পৌঁছানোর আগে Temporal তবুও ব্যর্থ activity-টি এর retry policy অনুযায়ী retry করে, আর মূল `ActivityError` হলো আবার তৈরি error-এর `__cause__`।

একটি retry policy আর workflow কোড একটি মডেল error ভিন্নভাবে দেখে। workflow কোড আর capability [error category](../models/overview.md#handling-model-api-errors) ক্লাস পায়, তাই একটি workflow-এ `except ModelTimeoutError` বা `except ModelRateLimitError` কাজ করে। একটি retry policy-র `non_retryable_error_types` শুধু error-এর `ApplicationError` টাইপ দেখে, যা HTTP status-যুক্ত একটি error-এর জন্য `ModelHTTPError` আর অন্য যেকোনো category-র জন্য `ModelAPIError` — category বাদে যে ক্লাস হিসেবে এটি তোলা হয়। তাই একটি category-র নাম দেওয়া policy, যেমন `'ModelRateLimitError'`, কিছুই মেলায় না। `'ModelHTTPError'` বা `'ModelAPIError'`-এর নাম দেওয়া একটি policy category আসার আগে যা মেলাত তা-ই মেলায়, শুধু সেই error-গুলো ছাড়া যেগুলো এখন একই error-এর জন্য provider-এর ব্যবহৃত HTTP status পায়, আর তাই এখন `ModelHTTPError` হিসেবেও তোলা হয়: Bedrock `ConverseStream` exception event (যেমন একটি throttling event 429 হিসেবে), একটি OpenAI-সামঞ্জস্যপূর্ণ বা OpenAI Responses stream-এর ভেতরের error অবজেক্ট, Hugging Face Text Generation Inference-এর stream-এর ভেতরের `OverloadedError`, আর xAI-এর `INVALID_ARGUMENT` (400 হিসেবে)। এগুলো এখন `ModelAPIError`-এর বদলে `ModelHTTPError` জানায়।

retry ঠিক করতে পারে না এমন একটি error category-তে Temporal-কে retry করা থেকে থামাতে, যেমন [`ModelContextWindowExceededError`][pydantic_ai.exceptions.ModelContextWindowExceededError], [`ModelQuotaExceededError`][pydantic_ai.exceptions.ModelQuotaExceededError] বা [`ModelAuthenticationError`][pydantic_ai.exceptions.ModelAuthenticationError], [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-তে `non_retryable_model_errors`-এ এর ক্লাস তালিকাভুক্ত করুন। একটি তালিকাভুক্ত ক্লাসের instance এমন একটি মডেল error retry policy যা-ই বলুক প্রথম চেষ্টাতেই model activity ব্যর্থ করে, আর তবুও নিজের ক্লাস হিসেবে workflow কোডে পৌঁছায়। যেহেতু ক্লাস `isinstance` দিয়ে মেলে, [`ModelUnavailableError`][pydantic_ai.exceptions.ModelUnavailableError] তালিকাভুক্ত করা [`ModelOverloadedError`][pydantic_ai.exceptions.ModelOverloadedError]-ও কভার করে, আর [`ModelRequestRejectedError`][pydantic_ai.exceptions.ModelRequestRejectedError] তালিকাভুক্ত করা [`ModelAuthenticationError`][pydantic_ai.exceptions.ModelAuthenticationError], [`ModelNotFoundError`][pydantic_ai.exceptions.ModelNotFoundError] আর [`ModelContextWindowExceededError`][pydantic_ai.exceptions.ModelContextWindowExceededError]-ও কভার করে। retry policy যে `ApplicationError` টাইপ দেখে তা বদলায় না।

```python title="temporal_non_retryable_model_errors.py"
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai.exceptions import (
    ModelAuthenticationError,
    ModelContextWindowExceededError,
    ModelQuotaExceededError,
)

agent = Agent(
    'openai:gpt-6.1-sol',
    name='assistant',
    capabilities=[
        TemporalDurability(
            non_retryable_model_errors=[
                ModelContextWindowExceededError,
                ModelQuotaExceededError,
                ModelAuthenticationError,
            ],
        ),
    ],
)
```

## Logfire দিয়ে Observability { #observability-with-logfire }

Temporal প্রতিটি workflow আর activity execution-এর জন্য telemetry event আর metric তৈরি করে, আর Pydantic AI প্রতিটি এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল কলের জন্য event তৈরি করে। আপনার অ্যাপ্লিকেশনে কী ঘটছে তার পূর্ণ ছবি পেতে এগুলো [Pydantic Logfire](../logfire.md)-এ পাঠানো যায়।

Temporal-এর সাথে Logfire ব্যবহার করতে, Temporal-এর `Client.connect()`-এ একটি [`LogfirePlugin`][pydantic_ai.durable_exec.temporal.LogfirePlugin] অবজেক্ট দিতে হবে:

```python title="logfire_plugin.py"
from temporalio.client import Client

from pydantic_ai.durable_exec.temporal import LogfirePlugin, PydanticAIPlugin


async def main():
    client = await Client.connect(
        'localhost:7233',
        plugins=[PydanticAIPlugin(), LogfirePlugin()],
    )
```

ডিফল্টভাবে, `LogfirePlugin` Temporal (metric-সহ) আর Pydantic AI instrument করবে আর সব ডেটা Logfire-এ পাঠাবে। এর tracing replay-নিরাপদ, তাই workflow history replay করলে নকল span তৈরি হয় না; span আর trace ID আসে Temporal-এর deterministic ID generator থেকে। আপনি একটি Temporal client, worker বা replayer তৈরি করার সময় plugin Logfire-এর tracer provider-কে replay-নিরাপদ করে, তাই এগুলো তৈরির আগে Logfire কনফিগার করুন: পরে `logfire.configure()` ডাকলে আপনি আরেকটি client, worker বা replayer তৈরি না করা পর্যন্ত replay-নিরাপত্তা আবার বন্ধ হয়ে যায়। Temporal metric প্রতি 60 সেকেন্ডে export হয়। `LogfirePlugin` constructor-এ `metric_periodicity` হিসেবে একটি `datetime.timedelta` দিয়ে আপনি বিরতি বদলাতে পারেন।

আপনার অ্যাপ্লিকেশন নিজেই আগে `logfire.configure()` ডেকে থাকলে, plugin সেই কনফিগারেশন বদলে না দিয়ে রাখে, তাই আপনার scrubbing অপশন, exporter, sampling আর console সেটিং অপরিবর্তিত থাকে। Logfire কনফিগারেশন আর instrumentation কাস্টমাইজ করতে, আপনি `LogfirePlugin` constructor-এ একটি `setup_logfire` ফাংশন দিয়ে একটি নিজস্ব `Logfire` instance (অর্থাৎ `logfire.configure()`-এর ফল) ফেরত দিতে পারেন। plugin তবুও এর ফেরত দেওয়া instance replay-নিরাপদ করে, আর আপনার ফাংশন শুধু একবার ডাকে, যাতে এর ভেতরের একটি `logfire.configure()` প্রতিটি client আর worker-এ Logfire রিসেট না করে। আপনার ফাংশন Pydantic AI instrumentation নিয়ন্ত্রণ করে, তাই plugin আপনার জন্য Pydantic AI instrument করে না।

Replay-নিরাপদ tracing Temporal-এর replay-নিরাপদ tracer provider-এর ওপর নির্ভর করে, যা Temporal এখনও পরীক্ষামূলক হিসেবে চিহ্নিত করে। এটি আপনার সেটআপে সমস্যা করলে, এর বদলে Logfire-এর সাধারণ tracer provider দিয়ে trace করতে `LogfirePlugin` constructor-এ `replay_safe=False` দিন; তখন replay আবার নকল span তৈরি করে, আর একটি `setup_logfire` ফাংশন প্রতিটি client connect-এ ডাকা হয়।

একটি [decision model](../models/decision.md)-এর [`decide` span](../logfire.md#decision-model-spans) model activity-র ভেতরে লেখা হয় শুধু তখনই যখন worker এজেন্টের নিজস্ব instrumentation দেখতে পায়: `Agent.instrument_all()` (যা `LogfirePlugin` সেট করে), `agent.instrument`, বা এজেন্টে একটি `Instrumentation` capability। শুধু `agent.run(..., capabilities=[Instrumentation(...)])` দিয়ে instrument করা একটি রান কোনো `decide` span পায় না।

Logfire-এ Temporal metric পাঠানো বন্ধ করতে, `LogfirePlugin` constructor-এ `metrics=False` দিন। অন্য Temporal telemetry অপশন কনফিগার করার দরকার হলে এটি আপনাকে `Client.connect()`-এ নিজের [`Runtime`](https://python.temporal.io/temporalio.runtime.Runtime.html) দিতেও দেয়; plugin তবুও tracing কনফিগার করবে।

## জানা সমস্যা { #known-issues }

### Pandas { #pandas }

একটি activity-র ভেতরে `logfire.info` ব্যবহার করলে আর `pandas` প্যাকেজ আপনার project-এর dependency-র মধ্যে থাকলে, আপনি নিচের error পেতে পারেন, যা একটি import race condition-এর ফল বলে মনে হয়:

```
AttributeError: partially initialized module 'pandas' has no attribute '_pandas_parser_CAPI' (most likely due to a circular import)
```

এটি ঠিক করতে, আপনি [`temporalio.workflow.unsafe.imports_passed_through()`](https://python.temporal.io/temporalio.workflow._sandbox.unsafe.html#imports_passed_through) context manager ব্যবহার করে প্যাকেজটি আগেভাগে import করতে পারেন, যাতে workflow sandbox-এ এটি আবার লোড না হয়:

```python title="temporal_activity.py"
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    import pandas
```

/// check | সংক্ষেপে মনে রাখুন

* workflow = deterministic সমন্বয় (replay হয়); activity = I/O (মডেল, টুল, MCP)।
* `Agent(name=..., capabilities=[TemporalDurability()])`; workflow-এ `__pydantic_ai_agents__` আর client-এ `PydanticAIPlugin`।
* রান শুধু workflow-এর ভেতরেই durable; workflow-এ `run_sync()` নয়, `await agent.run()`।
* এজেন্টের `name` আর toolset `id` বাধ্যতামূলক আর deploy-এর পর স্থির।
* `deps` serialize-যোগ্য আর ছোট রাখুন (2MB payload সীমা); বড় binary বাইরের storage-এ।
* streaming জমা হয়ে আসে; লাইভ event-এর জন্য `event_stream_handler=` বা `event_stream_topic`।
* retry একটি জায়গায় (Temporal) রাখুন; provider SDK-তে `max_retries=0`।
* observability: `Client.connect(..., plugins=[PydanticAIPlugin(), LogfirePlugin()])`।

///
