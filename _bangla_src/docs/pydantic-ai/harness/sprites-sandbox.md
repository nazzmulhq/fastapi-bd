
# Sprites Sandbox { #sprites-sandbox }

/// note | এই পেজে যা শিখবেন

* আপনার মেশিনের বদলে একটি স্থায়ী [Fly.io Sprite](https://sprites.dev)-এ এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো।
* Sprite-এর আয়ুর কোনো সীমা নেই — idle হলে ঘুমায়, ফাইল রাখে, আর মোছা না পর্যন্ত খরচ হয়।
* একই Sprite-এ চালিয়ে যাওয়া, পরে যুক্ত হওয়া, প্রস্তুত করা, পরিষ্কার, কনফিগারেশন আর durable execution।

///

আপনার মেশিনের বদলে একটি স্থায়ী [Fly.io Sprite](https://sprites.dev)-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/sprites_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[sprites,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[sprites,anthropic]"
```

///


`anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান। তারপর `SPRITE_TOKEN` আপনার Sprites API token-এ সেট করুন, আর উদাহরণের জন্য `ANTHROPIC_API_KEY`।

## দ্রুত শুরু { #quick-start }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
```

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, একটি Sprite-এ চলে। `Coder`-এ, `RepoContext` রান শুরু হলে Sprite তৈরি করে, কোনো টুল কল ছাড়াই; অলস তৈরির জন্য `Coder(repo_context=False)` ব্যবহার করুন। এর কোনো আয়ু-সীমা নেই: idle হলে এটি ঘুমায় আর এর ফাইল রাখে, আর আপনি না মোছা পর্যন্ত টাকা খরচ হয়; দেখুন [Clean up](#clean-up)।

`SpritesSandbox(working_dir='/home/sprite/project')` দিয়ে এজেন্টকে একটি project ডিরেক্টরি দিন: একটি নতুন Sprite-এ এটি আপনার জন্য তৈরি হয়, আর কমান্ড ও আপেক্ষিক path সেখান থেকে শুরু হয়।

একটি নতুন Sprite-এ git, Python আর Node.js থাকে ([preinstalled tools](https://docs.fly.io/sprites/working-with-sprites/)), কিন্তু pytest বা ripgrep (`rg`) নয়। আপনার project-এর যা লাগে তা ইনস্টল করুন, যেমন pytest; Sprite ইনস্টল করা প্যাকেজ রাখে। দ্রুততর `Coder` সার্চের জন্য, Sprite-এ একবার `sudo apt-get update && sudo apt-get install ripgrep` চালান আর পরের রানে পুনর্ব্যবহারের জন্য এর ref রাখুন।

/// tip | উদাহরণ দিয়ে বুঝি

Modal/E2B একটি হোটেলের ঘরের মতো — নির্দিষ্ট সময় পরে চেক-আউট। Sprite একটি নিজের ভাড়া করা ফ্ল্যাটের মতো — আপনি না ছাড়া পর্যন্ত থাকে, আপনার জিনিসপত্র (ইনস্টল করা প্যাকেজ, ফাইল) সেভাবেই রেখে দেয়; ব্যবহার না করলে আলো নিভিয়ে ঘুমায় (কম খরচ), কিন্তু ভাড়া (storage) চলতে থাকে।

///

## একই sandbox-এ চালিয়ে যাওয়া { #continue-in-the-same-sandbox }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')

followup = agent.run_sync(
    'Which capability would you add next, and where would it live?',
    message_history=result.all_messages(),
)
```

পরের রান message history-তে Sprite খুঁজে পায় আর এতে কাজ করে, তাই clone তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন Sprite শুরু করে। Sprite মুছে ফেলা হলে, রান একটি খালি Sprite-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে। একটি কমান্ড চলার সময় Sprite মোছা হলে, কমান্ডও এই error তোলে, যে exit code-ই জানাক: প্রতিটি কমান্ডের পর, backend Sprites control plane-কে জিজ্ঞেস করে Sprite এখনও আছে কিনা। সেই খোঁজ কমান্ডের `timeout`-এর মধ্যে গোনা হয়, আর ব্যর্থ বা সময় ফুরোনো একটি খোঁজ কমান্ডের ফল ফেরত দেয়, তাই একটি জীবন্ত Sprite-এ SIGKILL করা একটি কমান্ড তবুও exit 137 ফেরত দেয়।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা Sprite-এ চলা নিজের টুল লিখুন:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Shell(), FileSystem()])


@agent.tool
async def run_python(ctx: RunContext, code: str) -> str:
    """Run a Python snippet in the Sprite."""
    result = await ctx.workspace.run(['python', '-c', code], timeout=10)
    return result.stdout + result.stderr
```

একটি Sprite কমান্ডের মাঝে process থামিয়ে রাখে, যদি না আপনি এগুলো একটি [Sprites service](https://docs.fly.io/sprites/concepts/services/) হিসেবে চালান।

কমান্ড non-root `sprite` ব্যবহারকারী হিসেবে চলে, কিন্তু Unix অনুমতি একে সীমিত করে না: mode `000`-এর একটি ফাইল তবুও পাঠযোগ্য। টুলকে একটি path থেকে দূরে রাখতে এগুলোর ওপর নির্ভর করবেন না।

ফাইল পড়া একজন লেখকের অপেক্ষা না করে FIFO প্রত্যাখ্যান করে। ফাইল লেখা Sprites filesystem API দিয়ে যায়, যা একটি symlink দিয়ে এর লক্ষ্যে লেখে আর অনুপস্থিত parent ডিরেক্টরি তৈরি করে।

### একটি timeout কী থামায় { #what-a-timeout-stops }

একটি কমান্ড timeout Sprite প্রস্তুত হওয়ার পরে শুরু হয়। backend সেই কমান্ডের exec সংযোগ বন্ধ করে আর এক সেকেন্ড পরে Sprites-কে এটি থামাতে বলে; এটি Sprite মোছে না। থামানো সর্বোত্তম-চেষ্টা: কমান্ডের process group, একটি shell-এর সাধারণ `&` সন্তানসহ, থেমেছে এমন নিশ্চয়তা নেই। থামানো অনিশ্চিত হলে, Sprite পরীক্ষা করুন বা স্পষ্টভাবে মুছুন। `timeout=None` কমান্ডের সময়সীমা সরায়, Sprite-এর idle pause বা transport সীমা নয়।

stdout বা stderr উত্তরাধিকারসূত্রে পাওয়া একটি background সন্তান সেই সন্তান বেরোনো পর্যন্ত `run()`-কে অপেক্ষায় রাখে, কারণ Sprites আউটপুট stream বন্ধ হওয়ার পরেই exit status জানায়। একটি দীর্ঘ-চলা job শুরুর সময় background আউটপুট একটি ফাইলে redirect করুন; `Shell.start_command` নিজের আউটপুট log পরিচালনা করে।

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া Sprite-এ ফিরে আসতে, এর ref `workspace=` হিসেবে ফেরত দিন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Coder()])

result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and summarize how capabilities work.')
ref = result.workspace.ref  # store this, e.g. in your database

later = agent.run_sync('Which capability would you add next, and where would it live?', workspace=ref)
```

ref কোনো credential রাখে না, তাই আবার যুক্ত হওয়া process-এরও `SPRITE_TOKEN` লাগে। message history একটির নাম দিলেও একটি নতুন Sprite শুরু করতে `workspace='new'` দিন।

`runtime` শুধু একটি নতুন Sprite গড়ে, আর একটি অজানা runtime প্রথম ব্যবহারে একটি স্পষ্ট error তোলে; `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য, আবার যুক্ত হওয়ার পরেও। একটি নতুন Sprite-এর জন্য `working_dir` তৈরি হয়; একটি যুক্ত বা caller-দেওয়া Sprite-এ এটি আগে থেকেই থাকতে হবে, নইলে কমান্ড `WorkspaceError` দিয়ে ব্যর্থ হয়।

আগে থেকেই একটি `sprites.AsyncSprite` আছে? একটি রানে `workspace=SpritesSandboxBackend(sandbox=sprite)` দিন, `pydantic_ai_harness.sprites_sandbox` থেকে `SpritesSandboxBackend`-সহ। `SpritesSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন।

একটি রান আপনার তৈরি backend খোলা রাখে। এটি দিয়ে কাজ শেষ হলে `await backend.aclose()` ডাকুন: এটি `SPRITE_TOKEN` থেকে খোলা client বন্ধ করে, Sprite নয়, আর পরের একটি কাজ একটি নতুন খোলে। আপনার দেওয়া একটি `client=` বা `sandbox=` কখনো বন্ধ হয় না।

## রানের আগে একটি Sprite প্রস্তুত করা { #prepare-a-sprite-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে, নিজে backend তৈরি করুন, একটি `Workspace` দিয়ে লিখুন, আর backend রানে দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox, SpritesSandboxBackend

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Coder()])


async def run_in_prepared_sprite() -> str:
    backend = SpritesSandboxBackend(working_dir='/home/sprite/project')
    try:
        await Workspace(backend).write_text('TASK.md', 'Add a `--version` flag to cli.py.\n')
        result = await agent.run('Do the task in TASK.md.', workspace=backend)
        return result.output
    finally:
        await backend.aclose()
        ref = backend.ref  # set once the Sprite exists
        if ref is not None:
            await SpritesSandbox().destroy(ref)
```

রান backend যেমন আছে তেমন ব্যবহার করে, তাই `SpritesSandbox`-এর সেটিং এতে প্রযোজ্য নয়, আর এটি খোলা রাখে: `aclose()` দিয়ে বন্ধ করুন। এর বদলে Sprite রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন।

## পরিষ্কার { #clean-up }

রান শেষ হওয়ার পরও Sprite এর ফাইল আর ইনস্টল করা প্যাকেজ রাখে। Pydantic AI কখনো এটি মোছে না। idle হলে এটি ঘুমায় আর পরের কমান্ডে জাগে: সক্রিয় থাকার সময় আপনি compute-এর জন্য দেন আর না মোছা পর্যন্ত storage-এর জন্য। আপনার রাখা ref দিয়ে এটি মুছুন:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox


async def delete_sprite(ref: WorkspaceRef) -> None:
    await SpritesSandbox().destroy(ref)
```

`destroy(ref)` যুক্ত না হয়ে বা না জাগিয়ে Sprite id দিয়ে মোছে, আর আর নেই এমন একটি Sprite চুপচাপ ফেরত আসে। শুধু আপনার মালিকানাধীন Sprite মুছুন। একটি বিদ্যমান Sprite-এর জন্য একটি অলস backend তৈরি করতে `backend(ref)` ব্যবহার করুন; `get_sandbox()` এতে যুক্ত হয়ে এর নেটিভ `sprites.AsyncSprite` ফেরত দেয় (এখনও Sprite নেই এমন একটি backend-এ, এটি একটি তৈরি করে)। একটি রানের বাইরে আপনার নিজে তৈরি একটি backend নিজের client খোলে, যা আপনি `aclose()` দিয়ে বন্ধ করেন; এরপর, একটি কাজের handle-এর জন্য আবার `get_sandbox()` ডাকুন। দেখুন [Sprite lifecycle](https://docs.sprites.dev/concepts/lifecycle/)।

একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই। এর sandbox বন্ধ করতে, একটি `on_run_error` hook-এ পরিষ্কার করুন; একটি রান ব্যর্থ হলে `after_run` চলে না। তৈরির উত্তর হারিয়ে গেলে, ref হয়তো এমন একটি Sprite চিহ্নিত করে যা এখনও API-তে দৃশ্যমান নয়; একটি খোঁজ ব্যর্থ হওয়া প্রমাণ করে না যে এটি কখনো তৈরিই হয়নি:

```python
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import Hooks
from pydantic_ai.run import AgentRunResult
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox

hooks = Hooks()


@hooks.on.run_error
async def terminate_failed_run(ctx: RunContext[None], *, error: BaseException) -> AgentRunResult[Any]:
    if ctx.workspace.ref is not None:
        await SpritesSandbox().destroy(ctx.workspace.ref)
    raise error


agent = Agent('anthropic:claude-opus-5-5', capabilities=[SpritesSandbox(), Coder(), hooks])
```

Modal আর E2B sandbox-এর বিপরীতে, একটি Sprite-এর কোনো আয়ু timeout নেই: মোছা না পর্যন্ত এটি টেকে। তাই এর ref রাখার আগে শেষ হওয়া একটি রান, যেমন তৈরির ঠিক পরে একটি crash, Ctrl-C বা মারা worker, Sprite পেছনে ফেলে যায়। তৈরির সময় এর id INFO-তে `Created Sprite <id>` হিসেবে log হয়; `await SpritesSandbox().destroy(WorkspaceRef(provider='sprites', id=...))` দিয়ে এটি মুছুন।

/// warning | সাধারণ ভুল

পরীক্ষার জন্য বারবার নতুন Sprite তৈরি করে ref না রাখা। প্রতিটি Sprite চিরকাল থাকে আর storage-এর খরচ জমতে থাকে। সবসময় `result.workspace.ref` রাখুন আর কাজ শেষে `destroy` করুন; হারিয়ে গেলে log-এ `Created Sprite <id>` খুঁজুন।

///

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `client` | একটি event loop-এ রান জুড়ে ভাগ করতে, বা এর base URL বা timeout সেট করতে একটি `sprites.AsyncSpritesClient`। ডিফল্ট: `None`, প্রতিটি রান `SPRITE_TOKEN` থেকে একটি client খোলে আর শেষে বন্ধ করে। আপনার দেওয়া একটি client আপনি বন্ধ করেন; `SpritesSandbox` কখনো করে না। |
| `runtime` | একটি নতুন Sprite-এর runtime। ডিফল্ট: `None`, Sprites-এর ডিফল্ট। একটি অজানা runtime প্রথম ব্যবহারে ব্যর্থ হয়। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়। ডিফল্ট: `None`, Sprite-এর নিজস্ব (`/home/sprite`, যেখানে কমান্ড non-root `sprite` হিসেবে চলে); একটি project ডিরেক্টরি সেট করুন, বা বহনযোগ্য কোডের জন্য আপেক্ষিক path ব্যবহার করুন। একটি নতুন Sprite-এ তৈরি হয়; একটি যুক্ত বা caller-দেওয়া Sprite-এ এটি আগে থেকেই থাকতে হবে। |
| `env` | প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। আপনার মেশিনের environment-এর কিছুই Sprite-এ পৌঁছায় না। |

Sprites শুধু asyncio event loop-এ চলে: এর SDK asyncio task ব্যবহার করে, তাই Trio-র অধীনে backend `UserError` তোলে।

## Durable execution { #durable-execution }

exec socket সংযোগের পরে কিন্তু একটি exit status আসার আগে বিচ্ছিন্ন হলে, কমান্ড হয়তো চলেছে। এটি একটি সম্ভাব্য non-idempotent কমান্ড replay না করে একটি retry-অযোগ্য workspace error তোলে। socket খোলার আগে ব্যর্থ হওয়া একটি handshake কমান্ড শুরু করতে পারে না: backend প্রায় পাঁচ সেকেন্ডে তিনবার এটি retry করে, তারপর retry-যোগ্য হিসেবে প্রচারিত হতে দেয়।

একটি ভাগ করা client module import-এর সময় তৈরি হয়, যাতে এই worker-এর activity এটি পুনর্ব্যবহার করে। worker থামলে এটি বন্ধ করুন। প্রথমে `localhost:7233`-এ একটি Temporal dev server চালান।

```python
import asyncio
import os
import uuid


from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import PydanticAIPlugin, PydanticAIWorkflow, TemporalDurability
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.sprites_sandbox import SpritesSandbox
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

# The provider SDK must not be re-imported inside Temporal's restricted workflow sandbox.
with workflow.unsafe.imports_passed_through():
    from sprites import AsyncSpritesClient

CLIENT = AsyncSpritesClient(token=os.environ['SPRITE_TOKEN'])
agent = Agent(
    'anthropic:claude-opus-5-5',
    name='sprites_coder',
    capabilities=[SpritesSandbox(client=CLIENT), Coder(), TemporalDurability()],
)


@workflow.defn
class SandboxWorkflow(PydanticAIWorkflow):
    __pydantic_ai_agents__ = [agent]

    @workflow.run
    async def run(self, prompt: str) -> str:
        return (await agent.run(prompt)).output


async def main() -> None:
    client = await Client.connect('localhost:7233', plugins=[PydanticAIPlugin()])
    async with CLIENT:
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

`SpritesSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ Sprite লেখে `pydantic_ai.workspace.provider` আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে; রান শুরুর কাজ, যেমন `RepoContext`-এর repo instructions লোড, এজেন্ট run span-এ চলে। একটি Sprite তৈরি করলে `pydantic_ai_harness.sprites_sandbox._backend` logger-এ `INFO`-তে এর নাম log হয় (`Created Sprite <name>`), তাই এর রানের চেয়ে বেশি টেকা একটি Sprite তবুও খুঁজে পাওয়া যায়।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.sprites_sandbox.SpritesSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/sprites-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.sprites_sandbox.SpritesSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/sprites-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[SpritesSandbox(), Coder()]` আর `SPRITE_TOKEN` — কমান্ড আর ফাইল একটি স্থায়ী Fly.io Sprite-এ।
* কোনো আয়ু-সীমা নেই: idle হলে ঘুমায়, মোছা না পর্যন্ত storage খরচ — ref রাখুন আর `destroy` করুন।
* git, Python, Node.js আছে; pytest/rg নিজে ইনস্টল করুন — Sprite এগুলো রেখে দেয়।
* কমান্ডের মাঝে process থামে (service ছাড়া); Unix অনুমতি সীমা দেয় না।
* নিজে তৈরি backend `aclose()` দিয়ে বন্ধ করুন।

///
