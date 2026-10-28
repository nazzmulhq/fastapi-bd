
# Smol Sandbox { #smol-sandbox }

/// note | এই পেজে যা শিখবেন

* কোনো cloud অ্যাকাউন্ট ছাড়া আপনার নিজের মেশিনে একটি [smolvm](https://github.com/smol-machines/smolvm) microVM-এ এজেন্টের কমান্ড আর ফাইল চালানো।
* VM-এর ডিফল্ট (নেটওয়ার্ক বন্ধ, Alpine), একই VM-এ চালিয়ে যাওয়া, ডিস্ক flush করা আর পরিষ্কার।
* কমান্ড কীভাবে চলে, নিরাপত্তা মডেল আর কোন কোন platform সমর্থিত।

///

আপনার নিজের মেশিনে একটি [smolvm](https://github.com/smol-machines/smolvm) microVM-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান, আপনার ফাইল আর process থেকে বিচ্ছিন্ন, কোনো cloud অ্যাকাউন্ট ছাড়া।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/smol_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[smol,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[smol,anthropic]"
```

///


`smol` extra [smolmachines](https://github.com/smol-machines/smol) ইনস্টল করে, যে SDK smolvm engine ধারণ করে। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান, আর উদাহরণের জন্য `ANTHROPIC_API_KEY` সেট করুন।

smolmachines Apple silicon-এর macOS আর x86_64 ও aarch64-এর Linux-এর (glibc 2.34 বা নতুনতর) জন্য wheel দেয়। Linux-এ, এজেন্ট চালানো ব্যবহারকারীর `/dev/kvm`-এ পড়া আর লেখার অনুমতি লাগে। দেখুন [Platforms](#platforms)।

## দ্রুত শুরু { #quick-start }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.smol_sandbox import SmolSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SmolSandbox(image='python:3.12-alpine'), Coder()])
result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')
```

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, নিজস্ব kernel আর filesystem-সহ একটি VM-এ চলে। রানের প্রথম workspace ব্যবহারে VM boot হয়; `Coder`-এ, `RepoContext` রান শুরুতেই এটি ব্যবহার করে, তাই শুধু একটি টুলের দরকার হলে boot করতে `Coder(repo_context=False)` ব্যবহার করুন। রান শেষ হওয়ার পরও VM চলতে থাকে; দেখুন [Clean up](#clean-up)।

একটি `image` ছাড়া, VM smolvm-এর নিজস্ব Alpine Linux চালায়, যাতে BusyBox আছে কিন্তু Python, git বা ripgrep নেই, আর কোনো download লাগে না। একটি `image` যেকোনো OCI image, যেমন `python:3.12-alpine`; smolvm প্রথমবার এই মেশিনে এটি টেনে আনে। কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, যা দুটোতেই `root`, আর `/workspace`-এ শুরু হয়, যা না থাকলে তৈরি হয়।

একটি নতুন VM-এর কোনো নেটওয়ার্ক প্রবেশ নেই। এজেন্টকে প্যাকেজ ইনস্টল বা repository clone করতে দিতে `SmolSandbox(allow_internet_access=True)` দিন। সেই প্রবেশ অসীমাবদ্ধ আর এই মেশিন থেকে আসে, তাই একে শুধু ইন্টারনেট নয়, এই মেশিন যা যা পৌঁছাতে পারে তার সবকিছুতে প্রবেশ হিসেবে ধরুন, যেমন আপনার লোকাল নেটওয়ার্ক বা একটি cloud metadata endpoint। (smolmachines 1.22.2-এর একটি পরীক্ষায়, এই মেশিনের নিজস্ব loopback ঠিকানা VM-কে প্রত্যাখ্যান করেছে।)

/// tip | উদাহরণ দিয়ে বুঝি

Docker container আর আপনার মেশিন একই kernel ভাগ করে; একটি microVM-এর নিজস্ব kernel আছে — যেন আপনার কম্পিউটারের ভেতরে একটি ছোট্ট আলাদা কম্পিউটার। এজেন্ট এর ভেতরে `rm -rf /` চালালেও শুধু সেই ছোট কম্পিউটারটাই নষ্ট হবে, আপনার আসল ফাইল নয়। আর এটি cloud-এ নয়, আপনার মেশিনেই চলে — কোনো অ্যাকাউন্ট বা bill নেই।

///

## একই VM-এ চালিয়ে যাওয়া { #continue-in-the-same-vm }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.smol_sandbox import SmolSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SmolSandbox(image='python:3.12-alpine'), Coder()])
result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')

followup = agent.run_sync('Now make it print the first 100.', message_history=result.all_messages())
```

পরের রান message history-তে VM খুঁজে পায় আর এতে কাজ করে, তাই script তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন VM boot করে। VM মুছে ফেলা হলে, রান একটি খালি VM-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা নিজের টুল লিখুন:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell
from pydantic_ai_harness.smol_sandbox import SmolSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SmolSandbox(image='python:3.12-alpine'), Shell(), FileSystem()])


@agent.tool
async def run_python(ctx: RunContext, code: str) -> str:
    """Run a Python snippet in the VM."""
    result = await ctx.workspace.run(['python', '-c', code], timeout=10)
    return result.stdout + result.stderr
```

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া VM-এ ফিরে আসতে, রানের workspace ref রেখে `workspace=` হিসেবে ফেরত দিন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.smol_sandbox import SmolSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SmolSandbox(image='python:3.12-alpine'), Coder()])

result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')
ref = result.workspace.ref  # store this, e.g. in your database

later = agent.run_sync('Now make it print the first 100.', workspace=ref)
```

message history একটির নাম দিলেও একটি নতুন VM boot করতে `workspace='new'` দিন। `image`, `cpus`, `memory_mb` আর `allow_internet_access` শুধু একটি নতুন VM গড়ে, তাই নেটওয়ার্ক প্রবেশসহ boot হওয়া একটি VM আবার যুক্ত হলেও তা রাখে; `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য।

এই মেশিনে আগে থেকেই একটি `smol.Machine` বা `smol.AsyncMachine` আছে? রানে `workspace=SmolSandboxBackend(sandbox=machine)` দিন, `pydantic_ai_harness.smol_sandbox` থেকে `SmolSandboxBackend`-সহ, বা VM-এর নামসহ `SmolSandboxBackend(ref=WorkspaceRef(provider='smol', id=...))`। backend এর id দিয়ে VM-এর নিজস্ব একটি handle খোলে, যা এই মেশিনে এর নাম। `SmolSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন। backend কখনো VM মোছে না। প্রতিটি উপায় কী গ্রহণ করে তা দেখুন [Which VMs a run can use](#which-vms-a-run-can-use)-এ।

VM স্থায়ী, তাই একটি ref অন্য একটি process থেকেও কাজ করে, যা চলমান না থাকলে VM আবার boot করে। কিন্তু একটি VM ব্যবহার করা process বেরোলে smolmachines এর ডিস্ক flush করে না, তাই VM boot হওয়ার পর থেকে ফাইলের পরিবর্তন হারিয়ে যেতে পারে। এগুলো রাখতে, process বেরোনোর আগে VM থামান:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.smol_sandbox import SmolSandbox


async def stop_vm(ref: WorkspaceRef) -> None:
    machine = await SmolSandbox().backend(ref).get_sandbox()
    await machine.stop()
```

/// warning | সাধারণ ভুল

একটি script-এ এজেন্ট চালিয়ে VM না থামিয়েই বেরিয়ে যাওয়া, তারপর পরের দিন ref দিয়ে আবার যুক্ত হয়ে দেখা যে এজেন্টের লেখা ফাইল নেই। smolmachines ডিস্ক flush করে না — process বেরোনোর আগে ওপরের উদাহরণের মতো VM থামান।

///

## রানের আগে একটি VM প্রস্তুত করা { #prepare-a-vm-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে বা প্যাকেজ ইনস্টল করতে, নিজে backend boot করুন, `Workspace` দিয়ে এতে কাজ করুন, আর রানে দিন:

```python
import asyncio

from pydantic_ai import Agent
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.smol_sandbox import SmolSandbox, SmolSandboxBackend

agent = Agent('anthropic:claude-opus-5-5', capabilities=[SmolSandbox(), Coder()])


async def main() -> None:
    backend = SmolSandboxBackend(image='python:3.12-alpine', allow_internet_access=True)
    try:
        workspace = Workspace(backend)
        await workspace.write_text('calc.py', 'def add(a, b):\n    return a - b\n')
        install = await workspace.run(['pip', 'install', 'pytest'], timeout=300)
        if install.exit_code != 0:
            raise RuntimeError(f'pip install failed: {install.stderr}')
        result = await agent.run('Fix the bug in calc.py.', workspace=backend)
        print(result.output)
    finally:
        ref = backend.ref  # set once the VM exists
        if ref is not None:
            await SmolSandbox().destroy(ref)


if __name__ == '__main__':
    asyncio.run(main())
```

setup বা রান ব্যর্থ হলেও `finally` VM মোছে। এর বদলে এটি রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন। `workspace=` হিসেবে দেওয়া একটি backend-এ `SmolSandbox`-এর সেটিং প্রযোজ্য নয়; backend-কে নিজস্বগুলো দিন। workspace API কভার করে না এমন smol সুবিধার জন্য `backend.get_sandbox()` SDK-র `smol.AsyncMachine` ফেরত দেয়।

## পরিষ্কার { #clean-up }

একটি রান কখনো এর VM মোছে না, আর মোছা না পর্যন্ত একটি VM এই মেশিনে এর ডিস্ক রাখে। আপনার রাখা ref দিয়ে এটি মুছুন:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.smol_sandbox import SmolSandbox


async def delete_vm(ref: WorkspaceRef) -> None:
    await SmolSandbox().destroy(ref)
```

ইতিমধ্যে চলে যাওয়া একটি VM মুছলে চুপচাপ ফেরত আসে। smolmachines একটি যুক্ত handle দিয়ে একটি লোকাল VM মোছে, আর যুক্ত হওয়া একটি থামানো VM boot করে, তাই `destroy` আগে একটি থামানো VM boot করে। একবার শুরু হলে, একটি মোছা এর caller বাতিল হলেও শেষ হয়। `SmolSandbox.backend(ref)` কিছু boot না করে একটি যুক্ত backend তৈরি করে।

কিছুই আপনার জন্য একটি VM মোছে না, আর কোনো idle বা আয়ু-সীমা নেই। একটি VM boot করা process বেরোলে VM বন্ধ হয়, কিন্তু এর ডিস্ক এই মেশিনে থাকে। একটি VM boot করলে এর id log হয় (দেখুন [Telemetry](#telemetry)), তাই একটি রাখা ref ছাড়া পেছনে ফেলে যাওয়া একটি খুঁজে পেতে পারেন, যেমন boot করার পর crash করা একটি durable execution worker-এর।

VM boot শুরু হওয়ামাত্র `backend.ref` সেট হয়, আর `destroy` এই process-এ এখনও চলমান একটি boot-এর অপেক্ষা করে, তাই [Prepare a VM before the run](#prepare-a-vm-before-the-run)-এর `finally` boot-এর মাঝে রান বাতিল হলেও VM মোছে। একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই: একটি `on_run_error` hook-এ VM মুছুন, যেমন [E2B](e2b-sandbox.md#clean-up)-এর জন্য দেখানো, বা [Prepare a VM before the run](#prepare-a-vm-before-the-run)-এর মতো নিজে backend boot করুন।

## কমান্ড কীভাবে চলে { #how-commands-run }

প্রতিটি কমান্ড VM-এর `/bin/sh` দিয়ে চলে, যা একটি argv ক্রম `exec` দিয়ে শুরু করে, একে আক্ষরিক রেখে, আর একটি অনুপস্থিত প্রোগ্রামকে exit code 127 দেয়। যে প্রোগ্রামের নাম `-` দিয়ে শুরু হয় তা আগে `PATH`-এ খোঁজা হয়, তাই `exec` এটিকে একটি অপশন হিসেবে পড়তে পারে না। একটি `shell=True` string `/bin/sh -c`-এর অধীনে চলে। নিজস্ব image-এ একটি POSIX `/bin/sh` লাগে।

একটি timeout বা বাতিলে, backend কমান্ডের আউটপুট stream বন্ধ করে, আর smolvm কমান্ড আর এর শুরু করা process মারে। যে job তাদের শুরু করা কমান্ডের চেয়ে বেশি টেকে, যেমন একটি [Shell](shell.md) background job, চলতে থাকে। event loop খুব ব্যস্ত থাকলে সেজন্য smolvm নিজেও এর timeout-এর 5 সেকেন্ড পরে একটি কমান্ড মারে। যে কমান্ডের মিলিত আউটপুট 10 MiB পেরোয় তা একইভাবে থামানো হয় আর `WorkspaceOutputLimitError` তোলে, `stdout` আর `stderr`-এ প্রতিটি stream-এর প্রথম 65,536 অক্ষরসহ। এর বদলে বড় আউটপুট একটি ফাইলে redirect করুন। সীমাটি backend যা রাখে তা সীমিত করে, এই process যে মেমরি ব্যবহার করে তা নয়: smolvm একটি কমান্ডের stdout আর stderr 11 MiB পেরোলে থামায়, কিন্তু VM backend পড়ার চেয়ে দ্রুত যে আউটপুট event পাঠায় smolmachines সেগুলো নিজের কোনো সীমা ছাড়াই queue করে, তাই ওই event-এর বাড়তি খরচ সীমিত নয়।

backend-এর নিজস্ব কমান্ড, `working_dir`-এর জন্য `mkdir -p` আর `pwd -P`, 60 সেকেন্ড পরে `WorkspaceTimeoutError` তোলে, তাই একটি ভাঙা image রান আটকাতে পারে না।

ফাইল কাজ VM-এ shell কমান্ড হিসেবে চলে (দেখুন [Writing a backend](../workspace.md#writing-a-backend)), তাই image-এ সাধারণ ফাইল utility লাগে, যা Alpine-এর BusyBox-এ আছে। ফাইল প্রতি কমান্ডে 64 KiB সরে, তাই কয়েক MiB-এর একটি ফাইল পড়তে বা লিখতে কয়েক সেকেন্ড লাগে।

একটি মোছা বা থামানো VM `WorkspaceUnavailableError` তোলে; সরানো একটি `working_dir` `WorkspaceError` তোলে। অন্য smolmachines ব্যর্থতা `smol.SmolError` হিসেবে প্রচারিত হয়, durable execution engine-এর retry করার জন্য।

smol SDK এর কল asyncio thread-এ চালায়, তাই backend-এর asyncio event loop লাগে: Trio-র অধীনে, কাজ `UserError` তোলে।

## নিরাপত্তা মডেল { #security-model }

VM-ই সীমা: এর নিজস্ব kernel আর filesystem আছে, এই মেশিনের কিছুই এতে mount করা নেই, কোনো port প্রকাশিত নয়, আর আপনার কোনো environment variable এতে পৌঁছায় না। ভেতরে, কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, smolvm-এর নিজস্ব Alpine আর বেশিরভাগ image-এ `root`, তাই এজেন্ট যা চালায় তা VM-এর যেকোনো কিছু বদলাতে পারে।

- smolvm আপনার process-এ আপনার OS ব্যবহারকারীর অনুমতিতে চলে। `SMOLVM_*` environment variable এটি কনফিগার করে, আর কিছু, যেমন `SMOLVM_SECCOMP=off`, Linux-এ এর নিজস্ব বন্দিত্ব বন্ধ করে, তাই অবিশ্বস্ত input-কে এগুলো সেট করতে দেবেন না।
- `image` tag দিয়ে টানা হয়; প্রতিবার একই image পেতে একটি digest pin করুন, যেমন `python:3.12-alpine@sha256:...`।
- `cpus` আর `memory_mb` একটি VM সীমিত করে; এর ডিস্কের আকার smolvm-এর ডিফল্ট, আর একটি process কতগুলো VM boot করে তা কিছুই সীমিত করে না।

### একটি রান কোন VM ব্যবহার করতে পারে { #which-vms-a-run-can-use }

যে একটি ref দেয় সে এর নাম দেওয়া VM-এ কমান্ড চালায়। smolmachines এই মেশিনে আপনার OS ব্যবহারকারীর যেকোনো VM নাম দিয়ে খুলতে পারে, অন্য টুলের আপনার ফোল্ডার mount করে তৈরি VM-সহ। তাই কী গ্রহণযোগ্য তা নির্ভর করে VM কোথা থেকে আসে তার ওপর:

| VM কোথা থেকে আসে | কী গ্রহণযোগ্য |
| --- | --- |
| `SmolSandbox`: message history-তে একটি ref, `workspace=ref`, `backend(ref)` বা `destroy(ref)` | শুধু `SmolSandbox`-এর boot করা VM, নাম `pydantic-ai-` আর 32টি hex অঙ্ক। অন্য যেকোনো নাম কিছু চলার আগেই `ValueError` তোলে। |
| আপনার কোডের তৈরি `SmolSandboxBackend(sandbox=machine)` বা `SmolSandboxBackend(ref=...)` | এই মেশিনের যেকোনো VM, mount বা নেটওয়ার্কসহ একটিও, কারণ আপনার কোড এটি বেছেছে। একটি Smol Cloud machine, যেমন এর পরে মোছা একটি VM, `WorkspaceUnavailableError` তোলে, যদি না এই মেশিনের একটি VM এর id-র মতো নামে থাকে। |

- আপনার দেওয়া একটি VM-এ একটি রান সেই VM-এর নাম message history-তে লেখে। শুধু সেই history দেওয়া পরের একটি রান `ValueError` তোলে; এটি VM খোলে না বা একটি নতুন boot করে না। আবার backend দিন, বা একটি নতুন VM-এর জন্য `workspace='new'`।
- Durable execution এর ref থেকে workspace আবার তৈরি করে, তাই এটি শুধু `SmolSandbox`-এর boot করা VM-এ কাজ করে।
- নাম প্রমাণ করে না একটি VM কোথা থেকে এসেছে: আপনার OS ব্যবহারকারী হিসেবে চলা যেকোনো প্রোগ্রাম এমন নামের একটি VM boot করতে পারে, আর smolmachines একটি বিদ্যমান VM কীভাবে কনফিগার হয়েছিল তা জানাতে পারে না। শুধু আপনার অ্যাপ্লিকেশনের নিজের রাখা ref দিন, আর ব্যবহারকারীর input থেকে `SmolSandboxBackend(ref=...)` তৈরি করবেন না।

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `image` | একটি নতুন VM-এর OCI image। ডিফল্ট: `None`, smolvm-এর নিজস্ব Alpine Linux। |
| `cpus` | একটি নতুন VM-এর vCPU। ডিফল্ট: `None`, smolvm-এর ডিফল্ট। |
| `memory_mb` | একটি নতুন VM-এর মেমরি, MiB-তে। ডিফল্ট: `None`, smolvm-এর ডিফল্ট। |
| `allow_internet_access` | একটি নতুন VM-এর এই মেশিনের নেটওয়ার্ক থেকে অসীমাবদ্ধ বাইরের নেটওয়ার্ক প্রবেশ আছে কিনা। ডিফল্ট: `False`। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়, না থাকলে তৈরি হয়। ডিফল্ট: `/workspace`; `None` VM-এর নিজস্বটি ব্যবহার করে (image ছাড়া `/`)। |
| `env` | image-এর ওপরে প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। আপনার মেশিনের environment-এর কিছুই VM-এ পৌঁছায় না, আর `env` capability-র `repr`-এর বাইরে রাখা হয়, কিন্তু এজেন্টের কমান্ড এটি পড়তে পারে। |

## Platform { #platforms }

smolvm macOS-এ Apple-এর Hypervisor framework আর Linux-এ KVM দিয়ে VM চালায়, তাই এটি Apple silicon-এর macOS আর glibc 2.34 বা নতুনতর-সহ x86_64 ও aarch64-এর Linux-এ চলে। অন্য platform-এ `smol` extra কিছুই ইনস্টল করে না আর `pydantic_ai_harness.smol_sandbox` import করলে `ImportError` ওঠে। VM চালাতে পারে না এমন একটি host, যেমন `/dev/kvm`-এ প্রবেশ ছাড়া Linux, প্রথম ব্যবহারে `WorkspaceUnavailableError` তোলে। একটি VM boot না করে `smol.local_availability()` দিয়ে একটি host যাচাই করুন।

## Telemetry { #telemetry }

`SmolSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ VM লেখে `pydantic_ai.workspace.provider` (`smol`) আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে। একটি VM boot করলে boot শুরুর আগে `pydantic_ai_harness.smol_sandbox._backend` logger-এ INFO-তে `Creating smol VM <id>`-ও log হয়, তাই এটি রাখার আগে রান শেষ হলেও id রেকর্ডে থাকে। এই মেশিনে, একটি VM-এ যুক্ত হতে আপনার OS ব্যবহারকারীর process-এর শুধু এর id লাগে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.smol_sandbox.SmolSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smol-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.smol_sandbox.SmolSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/smol-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[SmolSandbox(), Coder()]` — আপনার মেশিনেই একটি microVM, নিজস্ব kernel-সহ; কোনো cloud অ্যাকাউন্ট নয়।
* macOS (Apple silicon) বা Linux (KVM) লাগে।
* ডিফল্ট: smolvm-এর Alpine, নেটওয়ার্ক বন্ধ, `/workspace`; প্যাকেজের জন্য `image` আর `allow_internet_access=True`।
* VM নিজে থেকে মোছা হয় না; process বেরোনোর আগে থামান, নইলে ফাইলের পরিবর্তন হারাতে পারে।
* শুধু নিজের রাখা ref দিন — ব্যবহারকারীর input থেকে `SmolSandboxBackend(ref=...)` নয়।

///
