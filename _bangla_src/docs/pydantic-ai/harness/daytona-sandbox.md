
# Daytona Sandbox { #daytona-sandbox }

/// note | এই পেজে যা শিখবেন

* আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [Daytona](https://www.daytona.io) cloud sandbox-এ এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো।
* Daytona-র idle-stop (ডিফল্ট 15 মিনিট), snapshot, আর sandbox কেন নিজে থেকে মোছা হয় না।
* একই sandbox-এ চালিয়ে যাওয়া, পরে যুক্ত হওয়া, পরিষ্কার, কনফিগারেশন আর durable execution।

///

আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [Daytona](https://www.daytona.io) cloud sandbox-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/daytona_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[daytona,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[daytona,anthropic]"
```

///


`anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান। তারপর `DAYTONA_API_KEY` আপনার Daytona dashboard-এর একটি API key-তে সেট করুন, আর উদাহরণের জন্য `ANTHROPIC_API_KEY`।

## দ্রুত শুরু { #quick-start }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
```

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, sandbox-এ চলে। `Coder`-এ, `RepoContext` রান শুরু হলে sandbox তৈরি করে, কোনো টুল কল ছাড়াই; অলস তৈরির জন্য `Coder(repo_context=False)` ব্যবহার করুন। রান শেষ হওয়ার পরও এটি চলতে থাকে যতক্ষণ না Daytona idle থাকার জন্য এটি থামায়, আর আপনি না মোছা পর্যন্ত এর ডিস্ক রাখে, আর টাকা খরচ হয়; দেখুন [Clean up](#clean-up)।

`DaytonaSandbox(working_dir='/home/daytona/project')` দিয়ে এজেন্টকে একটি project ডিরেক্টরি দিন: একটি নতুন sandbox-এ এটি আপনার জন্য তৈরি হয়, আর কমান্ড ও আপেক্ষিক path সেখান থেকে শুরু হয়।

Daytona-র ডিফল্ট snapshot-এ git, Python আর ripgrep (`rg`) থাকে, যা `Coder` সার্চের জন্য ব্যবহার করে। আপনার project-এর dependency-র জন্য, সেগুলো ইনস্টল করা একটি Daytona snapshot তৈরি করে `DaytonaSandbox(snapshot='my-snapshot')` দিন। Daytona চেনে না এমন একটি snapshot প্রথম ব্যবহারে `WorkspaceUnavailableError` দিয়ে ব্যর্থ হয়।

## একই sandbox-এ চালিয়ে যাওয়া { #continue-in-the-same-sandbox }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')

followup = agent.run_sync(
    'Which capability would you add next, and where would it live?',
    message_history=result.all_messages(),
)
```

পরের রান message history-তে sandbox খুঁজে পায় আর এতে কাজ করে, তাই clone তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন sandbox শুরু করে। idle থাকার সময় Daytona sandbox থামালে, পরের রান এটি আবার চালু করে। sandbox মুছে ফেলা হলে, রান একটি খালি sandbox-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা sandbox-এ চলা নিজের টুল লিখুন:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Shell(), FileSystem()])


@agent.tool
async def run_python(ctx: RunContext, code: str) -> str:
    """Run a Python snippet in the sandbox."""
    result = await ctx.workspace.run(['python', '-c', code], timeout=10)
    return result.stdout + result.stderr
```

কমান্ড non-root `daytona` ব্যবহারকারী হিসেবে `sh -c`-এর অধীনে চলে। ফাইল পড়া একজন লেখকের অপেক্ষা না করে FIFO প্রত্যাখ্যান করে। ফাইল লেখা অনুপস্থিত parent ডিরেক্টরি তৈরি করে, একটি symlink দিয়ে এর লক্ষ্যে লেখে, আর একটি বিদ্যমান ফাইলের mode রাখে।

### একটি timeout কী থামায় { #what-a-timeout-stops }

একটি কমান্ড timeout sandbox প্রস্তুত হওয়ার পরে শুরু হয়। একটি timeout বা একটি বাতিল রান কমান্ড থামায়, আর sandbox অন্য কমান্ডের জন্য চলতে থাকে। `WorkspaceTimeoutError` এ পর্যন্ত প্রতিটি stream-এর আউটপুটের শেষ 4 KiB বহন করে। Daytona থামানো নিশ্চিত না করলে, কমান্ড হয়তো তখনও চলছে: sandbox পরীক্ষা করুন বা নিজে মুছুন। `timeout=None` কমান্ডের সময়সীমা সরায়, Daytona-র idle stop নয়।

একটি কমান্ডের আউটপুট এটি বেরোনোর পর সংগ্রহ হয়, তাই এটির শুরু করা একটি background সন্তান তখনও চললেও `run()` তখনই ফেরত আসে; সেই সন্তান পরে যে আউটপুট লেখে তা ফেরত আসে না। যে কমান্ডের মিলিত আউটপুট 10 MiB পেরোয় তা বেরোনোর পর `WorkspaceOutputLimitError` তোলে, `stdout` আর `stderr`-এ প্রতিটি stream-এর প্রথম 64 KiB-সহ। এর বদলে বড় বা background আউটপুট একটি ফাইলে redirect করুন; `Shell.start_command` নিজের আউটপুট log পরিচালনা করে।

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া sandbox-এ ফিরে আসতে, এর ref `workspace=` হিসেবে ফেরত দিন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Coder()])

result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
ref = result.workspace.ref  # store this, e.g. in your database

later = agent.run_sync('Which capability would you add next, and where would it live?', workspace=ref)
```

ref কোনো credential রাখে না, তাই আবার যুক্ত হওয়া process-এরও `DAYTONA_API_KEY` লাগে। message history একটির নাম দিলেও একটি নতুন sandbox শুরু করতে `workspace='new'` দিন।

`snapshot`, `auto_stop_interval` আর `allow_internet_access` শুধু একটি নতুন sandbox গড়ে; `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য, আবার যুক্ত হওয়ার পরেও। একটি নতুন sandbox-এর জন্য `working_dir` তৈরি হয়; একটি যুক্ত বা caller-দেওয়া sandbox-এ এটি আগে থেকেই থাকতে হবে, নইলে কমান্ড `WorkspaceError` দিয়ে ব্যর্থ হয়।

আগে থেকেই একটি `daytona.AsyncSandbox` আছে? একটি রানে `workspace=DaytonaSandboxBackend(sandbox=sandbox)` দিন, `pydantic_ai_harness.daytona_sandbox` থেকে `DaytonaSandboxBackend`-সহ। `DaytonaSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন।

একটি রান আপনার তৈরি backend খোলা রাখে। এটি দিয়ে কাজ শেষ হলে `await backend.aclose()` ডাকুন: এটি `DAYTONA_API_KEY` থেকে খোলা client বন্ধ করে, sandbox নয়, আর পরের একটি কাজ একটি নতুন খোলে। আপনার দেওয়া একটি `client=` বা `sandbox=` কখনো বন্ধ হয় না।

## রানের আগে একটি sandbox প্রস্তুত করা { #prepare-a-sandbox-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে, নিজে backend তৈরি করুন, একটি `Workspace` দিয়ে লিখুন, আর backend রানে দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox, DaytonaSandboxBackend

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Coder()])


async def run_in_prepared_sandbox() -> str:
    backend = DaytonaSandboxBackend(working_dir='/home/daytona/project')
    try:
        await Workspace(backend).write_text('TASK.md', 'Add a `--version` flag to cli.py.\n')
        result = await agent.run('Do the task in TASK.md.', workspace=backend)
        return result.output
    finally:
        await backend.aclose()
        ref = backend.ref  # set once the sandbox exists
        if ref is not None:
            await DaytonaSandbox().destroy(ref)
```

রান backend যেমন আছে তেমন ব্যবহার করে, তাই `DaytonaSandbox`-এর সেটিং এতে প্রযোজ্য নয়, আর এটি খোলা রাখে: `aclose()` দিয়ে বন্ধ করুন। এর বদলে sandbox রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন।

## পরিষ্কার { #clean-up }

Pydantic AI কখনো sandbox থামায় বা মোছে না। Daytona একটি container sandbox, যেমন ডিফল্ট snapshot থেকে একটি, ডিফল্টভাবে 15 idle মিনিটের পর থামায় (এটি বদলাতে `auto_stop_interval=` সেট করুন, বা চালু রাখতে `0`)। একটি থামানো sandbox এর ডিস্ক রাখে আর 7 দিন পর archive হয়। একটি VM snapshot থেকে একটি sandbox এর বদলে 60 idle মিনিটের পর pause হয়, আর কখনো archive হয় না। যেকোনোভাবে, পরের একটি রান এটি আবার চালু করে, আর Daytona কখনো এটি মোছে না। আপনার রাখা ref দিয়ে এটি মুছুন:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox


async def delete_sandbox(ref: WorkspaceRef) -> None:
    await DaytonaSandbox().destroy(ref)
```

`destroy(ref)` একটি থামানো sandbox চালু না করে sandbox ID দিয়ে মোছে, আর আর নেই এমন একটি sandbox চুপচাপ ফেরত আসে। শুধু আপনার মালিকানাধীন sandbox মুছুন। একটি বিদ্যমান sandbox-এর জন্য একটি অলস backend তৈরি করতে `backend(ref)` ব্যবহার করুন; `get_sandbox()` এতে যুক্ত হয়ে এর নেটিভ `daytona.AsyncSandbox` ফেরত দেয় (এখনও sandbox নেই এমন একটি backend-এ, এটি একটি তৈরি করে)।

/// info | এক নজরে: Daytona sandbox-এর জীবনচক্র

| ধরন | idle হলে | এরপর | মোছা |
|------|----------|-------|------|
| Container (ডিফল্ট snapshot) | 15 মিনিট পর থামে | 7 দিন পর archive | কখনো নিজে থেকে নয় |
| VM snapshot | 60 মিনিট পর pause | কখনো archive হয় না | কখনো নিজে থেকে নয় |

যেকোনোটিতে পরের রান আবার চালু করে — তাই অব্যবহৃত sandbox `destroy(ref)` দিয়ে মুছুন।

///

একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই। এর sandbox মুছতে, একটি `on_run_error` hook-এ পরিষ্কার করুন; একটি রান ব্যর্থ হলে `after_run` চলে না:

```python
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.run import AgentRunResult
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox

hooks = Hooks()


@hooks.on.run_error
async def delete_failed_run_sandbox(ctx: RunContext[None], *, error: BaseException) -> AgentRunResult[Any]:
    if ctx.workspace.ref is not None:
        await DaytonaSandbox().destroy(ctx.workspace.ref)
    raise error


agent = Agent('anthropic:claude-opus-5-5', capabilities=[DaytonaSandbox(), Coder(), hooks])
```

এর ref রাখার আগে শেষ হওয়া একটি রান, যেমন তৈরির ঠিক পরে একটি crash, Ctrl-C বা মারা worker, sandbox পেছনে ফেলে যায়। backend-এর তৈরি প্রতিটি sandbox `created-by=pydantic-ai` লেবেল পায়, আর এর ID `INFO`-তে `Created Daytona sandbox <id>` হিসেবে log হয়; `await DaytonaSandbox().destroy(WorkspaceRef(provider='daytona', id=...))` দিয়ে এটি মুছুন।

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `client` | একটি event loop-এ রান জুড়ে ভাগ করতে, বা এর API URL বা target কনফিগার করতে একটি `daytona.AsyncDaytona`। ডিফল্ট: `None`, প্রতিটি রান `DAYTONA_API_KEY` থেকে একটি client খোলে আর শেষে বন্ধ করে। আপনার দেওয়া একটি client আপনি বন্ধ করেন; `DaytonaSandbox` কখনো করে না। |
| `snapshot` | একটি নতুন sandbox যে Daytona snapshot থেকে শুরু হয়। ডিফল্ট: `None`, Daytona-র ডিফল্ট। একটি অজানা snapshot প্রথম ব্যবহারে ব্যর্থ হয়। |
| `auto_stop_interval` | Daytona একটি নতুন sandbox থামানোর আগে idle মিনিট; `0` এটি বন্ধ করে। ডিফল্ট: `None`, Daytona-র ডিফল্ট: একটি container-এর জন্য 15 মিনিট, আর একটি VM এর বদলে 60 মিনিট পর pause হয়। |
| `allow_internet_access` | একটি নতুন sandbox ইন্টারনেটে পৌঁছাতে পারবে কিনা। `False` হলে, কী আটকানো হয় তা আপনার Daytona organization-এর tier-এর ওপর নির্ভর করে: Tier 3 আর 4-এ সবকিছু, আর নিচের tier প্যাকেজ registry, GitHub আর AI API নাগালে রাখে, তাই সেখানে এটি একটি তথ্য-পাচারের সীমা নয়। দেখুন [Daytona's network limits](https://www.daytona.io/docs/en/network-limits/)। ডিফল্ট: `True`। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়। ডিফল্ট: `None`, sandbox-এর নিজস্ব (`/home/daytona`, যেখানে কমান্ড non-root `daytona` হিসেবে চলে); একটি project ডিরেক্টরি সেট করুন, বা বহনযোগ্য কোডের জন্য আপেক্ষিক path ব্যবহার করুন। একটি নতুন sandbox-এ তৈরি হয়; একটি যুক্ত বা caller-দেওয়া sandbox-এ এটি আগে থেকেই থাকতে হবে। |
| `env` | প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। আপনার মেশিনের environment-এর কিছুই sandbox-এ পৌঁছায় না। |

Daytona শুধু asyncio event loop-এ চলে: এর SDK asyncio task ব্যবহার করে, তাই Trio-র অধীনে backend `UserError` তোলে।

## Durable execution { #durable-execution }

প্রতিটি activity নিজের Daytona client খোলে আর এর কাজ শেষ হলে বন্ধ করে, তাই worker-এর বন্ধ করার কিছু নেই। প্রথমে `localhost:7233`-এ একটি Temporal dev server চালান।

```python
import asyncio
import uuid

from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import PydanticAIPlugin, PydanticAIWorkflow, TemporalDurability
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.daytona_sandbox import DaytonaSandbox
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

agent = Agent(
    'anthropic:claude-opus-5-5',
    name='daytona_coder',
    capabilities=[DaytonaSandbox(), Coder(), TemporalDurability()],
)


@workflow.defn
class SandboxWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        return (await agent.run(prompt)).output


async def main() -> None:
    client = await Client.connect('localhost:7233', plugins=[PydanticAIPlugin()])
    async with Worker(client, task_queue='sandbox', workflows=[SandboxWorkflow]):
        print(
            await client.execute_workflow(
                SandboxWorkflow.run,
                'Use the shell tool to run pwd.',
                id=f'sandbox-{uuid.uuid4()}', task_queue='sandbox',
            )
        )


if __name__ == '__main__':
    asyncio.run(main())
```

`Coder`, `Shell` আর `FileSystem` DBOS, Temporal আর Prefect-এর অধীনে কাজ করে। engine-নির্দিষ্ট সীমার জন্য দেখুন [Coder](coder.md#durable-execution), [Shell](shell.md#durable-execution) আর [FileSystem](filesystem.md#durable-execution) guide।

এটি ব্যবহার করা workflow চলমান থাকা অবস্থায় একটি capability সরালে তাদের replay history বদলে যায়। পরিবর্তন deploy করার আগে ওই workflow drain করুন বা [Temporal worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) ব্যবহার করুন।

## Telemetry { #telemetry }

`DaytonaSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ sandbox লেখে `pydantic_ai.workspace.provider` আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে; রান শুরুর কাজ, যেমন `RepoContext`-এর repo instructions লোড, এজেন্ট run span-এ চলে। একটি sandbox তৈরি করলে `pydantic_ai_harness.daytona_sandbox._backend` logger-এ `INFO`-তে এর ID log হয় (`Created Daytona sandbox <id>`), তাই এর রানের চেয়ে বেশি টেকা একটি sandbox তবুও খুঁজে পাওয়া যায়।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.daytona_sandbox.DaytonaSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/daytona-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.daytona_sandbox.DaytonaSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/daytona-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[DaytonaSandbox(), Coder()]` আর `DAYTONA_API_KEY` — কমান্ড আর ফাইল একটি Daytona cloud sandbox-এ।
* ডিফল্ট snapshot-এ git, Python, `rg` আছে; dependency-র জন্য নিজস্ব snapshot।
* idle হলে থামে (15 মিনিট) কিন্তু কখনো নিজে থেকে মোছা হয় না — ref রাখুন আর `destroy` করুন।
* `allow_internet_access=False` নিচের tier-এ সম্পূর্ণ বন্ধ নয়।
* নিজে তৈরি backend `aclose()` দিয়ে বন্ধ করুন।

///
