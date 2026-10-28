
# Docker Sandbox { #docker-sandbox }

/// note | এই পেজে যা শিখবেন

* একটি লোকাল Docker বা Podman container-এ এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো — কোনো SDK ছাড়া, আপনার `docker` CLI দিয়েই।
* একটি project ডিরেক্টরি mount করা, একটি দূরের Docker host ব্যবহার, আবার যুক্ত হওয়া আর পরিষ্কার।
* কমান্ড কীভাবে চলে আর কেন container একটি VM-এর চেয়ে দুর্বল সীমা।

///

আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা একটি লোকাল [Docker](https://www.docker.com/) বা Podman container-এ চালান, প্রথম ব্যবহারে তৈরি, আপনার মেশিনের ফাইল আর process থেকে দূরে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/docker_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[anthropic]"
```

///


Docker-এর জন্য কোনো extra লাগে না: capability আপনার মেশিনে আগে থেকে থাকা `docker` CLI চালায়, তাই ইনস্টল করার মতো কোনো SDK নেই। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান, আর উদাহরণের জন্য `ANTHROPIC_API_KEY` সেট করুন।

## দ্রুত শুরু { #quick-start }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DockerSandbox(image='python:3.13-slim'), Coder()])
result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')
```

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, একটি container-এ চলে। রানের প্রথম workspace ব্যবহারে container তৈরি হয়। `Coder`-এ, `RepoContext` রান শুরুতেই এটি ব্যবহার করে, তাই শুধু একটি টুলের দরকার হলে তৈরি করতে `Coder(repo_context=False)` ব্যবহার করুন। রান শেষ হওয়ার পরও container চলতে থাকে; দেখুন [Clean up](#clean-up)।

image-এ একটি POSIX `sh` আর সাধারণ ফাইল utility লাগে, আর Docker প্রথমবার এটি টেনে আনে। কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, সাধারণত `root`। এগুলো `/workspace`-এ শুরু হয়, যা না থাকলে তৈরি হয়।

একটি নতুন container Docker-এর ডিফল্ট bridge নেটওয়ার্কে থাকে, যা ইন্টারনেটে পৌঁছায়, কিন্তু আপনার লোকাল নেটওয়ার্ক আর এই মেশিনের সার্ভিসেও। `--network none` দিয়ে চালাতে `allow_internet_access=False` দিন।

/// warning | লক্ষ্য করুন

অন্য sandbox-এর বিপরীতে, Docker Sandbox-এ **ইন্টারনেট ডিফল্টভাবে চালু** (`allow_internet_access=True`) — আর এটি আপনার লোকাল নেটওয়ার্কেও পৌঁছাতে পারে। অবিশ্বস্ত কাজে `allow_internet_access=False` দিন।

///

## একই container-এ চালিয়ে যাওয়া { #continue-in-the-same-container }

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DockerSandbox(image='python:3.13-slim'), Coder()])
result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')

followup = agent.run_sync('Now make it print the first 100.', message_history=result.all_messages())
```

পরের রান message history-তে container খুঁজে পায় আর এতে কাজ করে, তাই script তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন container তৈরি করে। container সরানো হলে, রান একটি খালি container-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা নিজের টুল লিখুন:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness.docker_sandbox import DockerSandbox
from pydantic_ai_harness.filesystem import FileSystem
from pydantic_ai_harness.shell import Shell

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DockerSandbox(image='python:3.13-slim'), Shell(), FileSystem()])


@agent.tool
async def run_python(ctx: RunContext, code: str) -> str:
    """Run a Python snippet in the container."""
    result = await ctx.workspace.run(['python', '-c', code], timeout=10)
    return result.stdout + result.stderr
```

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## একটি project ডিরেক্টরিতে কাজ { #work-on-a-project-directory }

একটি নতুন container খালি শুরু হয়। এজেন্টকে আপনার মেশিনের একটি ডিরেক্টরিতে কাজ করতে দিতে, `docker_args` দিয়ে এটি mount করুন, বাড়তি `docker run` আর্গুমেন্ট:

```python
from pathlib import Path

from pydantic_ai_harness.docker_sandbox import DockerSandbox

project = Path('.').resolve()
sandbox = DockerSandbox(
    image='python:3.13-slim',
    docker_args=['--volume', f'{project}:/workspace', '--memory', '2g', '--cpus', '2'],
    allow_internet_access=False,
)
```

mount হলো আপনার মেশিনের ফাইলের একমাত্র অংশ যা কমান্ড বদলাতে পারে; নেটওয়ার্ক একটি আলাদা সেটিং। নিজের একটি নেটওয়ার্কের জন্য, `allow_internet_access` চালু রেখে `docker_args`-এ `--network` দিন, কারণ Docker `--network none`-এর পাশে একটি দ্বিতীয় `--network` প্রত্যাখ্যান করে। `docker_args` container-এর নাম, এর `ai.pydantic.workspace=true` লেবেল বা এর entrypoint বদলাতে পারে না। কমান্ড যে ডিরেক্টরিতে শুরু হয় তা `working_dir` দিয়ে সেট করুন।

একটি নতুন container `--pids-limit 2048` পায়, তাই একটি নিয়ন্ত্রণহীন fork loop Docker চালানো মেশিনের (বা VM-এর) process টেবিল শেষ করতে পারে না। এটিতে পৌঁছানো একটি কমান্ড `Cannot fork` বা `Resource temporarily unavailable` দিয়ে ব্যর্থ হয়; এটি বদলাতে `docker_args`-এ নিজের `--pids-limit` দিন, বা সরাতে `-1`।

## একটি দূরের Docker host ব্যবহার { #use-a-remote-docker-host }

capability আপনার মেশিনে `docker` CLI চালায়, তাই সেই CLI যে daemon-এ নির্দেশ করে সেটিই ব্যবহার করে। অন্য একটি host-এ container চালাতে, এজেন্ট শুরুর আগে CLI সেখানে নির্দেশ করুন; আপনার কোড বদলায় না:

```bash
export DOCKER_HOST=ssh://dev@build-box  # or: docker context use build-box
```

host-এ Docker লাগে, আর `ssh`-কে prompt ছাড়া login করতে হবে, একটি key বা আপনার SSH agent দিয়ে। `DOCKER_HOST` `DOCKER_CONTEXT`-কে override করে, যা `docker context use`-কে override করে, তাই যেগুলো ব্যবহার করেন না সেগুলো unset করুন। `docker_args`-এর path, যেমন একটি `--volume` উৎস, সেই host-এর path, আর `allow_internet_access` সেই host-এর নেটওয়ার্কে পৌঁছায়। প্রতিটি রান শুরুর সময় এই সেটিং পড়ে, আর `destroy` ডাকার সময়, তাই একটি container ব্যবহারে থাকার সময় এগুলো একই রাখুন।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া container-এ ফিরে আসতে, রানের workspace ref রেখে `workspace=` হিসেবে ফেরত দিন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DockerSandbox(image='python:3.13-slim'), Coder()])

result = agent.run_sync('Write a script that prints the first 10 primes, and run it.')
ref = result.workspace.ref  # store this, e.g. in your database

later = agent.run_sync('Now make it print the first 100.', workspace=ref)
```

ref হলো `WorkspaceRef(provider='docker', id='pydantic-ai-<hex>')`, container-এর নাম। যুক্ত হওয়া প্রথম ব্যবহারে একটি থামানো container চালু করে, তাই এটি এর ফাইলসহ ফিরে আসে। message history একটির নাম দিলেও একটি নতুন container তৈরি করতে `workspace='new'` দিন। `image`, `allow_internet_access` আর `docker_args` শুধু একটি নতুন container গড়ে। `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য।

একটি ref বিশ্বস্ত input: যে একটি দেয় সে সেই container-এ কমান্ড চালায়। `DockerSandbox` এর `ai.pydantic.workspace=true` লেবেল ছাড়া একটি container প্রত্যাখ্যান করে, তাই একটি ref Docker daemon-এর পরিবেশন করা অন্য container-এ পৌঁছাতে পারে না। তবে লেবেল উৎসের প্রমাণ নয়: এই মেশিনের যেকোনো `DockerSandbox`, বা `docker` চালাতে পারে এমন যে কেউ, এটিসহ একটি container তৈরি করতে পারে, তাই শুধু আপনার অ্যাপ্লিকেশনের নিজের রাখা ref দিন।

## রানের আগে একটি container প্রস্তুত করা { #prepare-a-container-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে বা প্যাকেজ ইনস্টল করতে, নিজে backend তৈরি করুন, `Workspace` দিয়ে এতে কাজ করুন, আর রানে দিন:

```python
import asyncio

from pydantic_ai import Agent
from pydantic_ai.workspaces import Workspace
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox, DockerSandboxBackend

agent = Agent('anthropic:claude-opus-5-5', capabilities=[DockerSandbox(image='python:3.13-slim'), Coder()])


async def main() -> None:
    backend = DockerSandboxBackend(image='python:3.13-slim')
    try:
        workspace = Workspace(backend)
        await workspace.write_text('calc.py', 'def add(a, b):\n    return a - b\n')
        install = await workspace.run(['pip', 'install', 'pytest'], timeout=300)
        if install.exit_code != 0:
            raise RuntimeError(f'pip install failed: {install.stderr}')
        result = await agent.run('Fix the bug in calc.py.', workspace=backend)
        print(result.output)
    finally:
        ref = backend.ref  # set once the container is being created
        if ref is not None:
            await DockerSandbox().destroy(ref)


if __name__ == '__main__':
    asyncio.run(main())
```

setup বা রান ব্যর্থ হলেও `finally` container সরায়। এর বদলে এটি রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন। `workspace=` হিসেবে দেওয়া একটি backend-এ `DockerSandbox`-এর সেটিং প্রযোজ্য নয়; backend-কে নিজস্বগুলো দিন।

## পরিষ্কার { #clean-up }

একটি রান কখনো এর container সরায় না। আপনার রাখা ref দিয়ে এটি সরান, এর anonymous volume-সহ:

```python
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.docker_sandbox import DockerSandbox


async def remove_container(ref: WorkspaceRef) -> None:
    await DockerSandbox().destroy(ref)
```

ইতিমধ্যে চলে যাওয়া একটি container সরালে চুপচাপ ফেরত আসে। একটি `image` ছাড়া `DockerSandbox()` ref দিয়ে container-এ যুক্ত হয় আর সরায়, আর ref ছাড়া একটি রান এজেন্টের অন্য workspace capability-র জন্য রেখে দেয়।

কিছুই আপনার জন্য একটি container সরায় না, আর কোনো idle বা আয়ু-সীমা নেই। `docker ps --all --filter label=ai.pydantic.workspace=true` `DockerSandbox`-এর তৈরি container খুঁজে দেয়, একটি রাখা ref ছাড়া পেছনে পড়ে থাকা যেকোনোটিসহ।

প্রথম কাজ container তৈরি শুরু করলে `backend.ref` সেট হয়, আর একটি container থাকার আগেই তৈরি ব্যর্থ হলে `None`-এ ফিরে যায়। তৈরি বাতিল হলে, `destroy` সরানোর কিছু না পাওয়ার পরও Docker হয়তো container তৈরি শেষ করে; ওপরের লেবেল ছাঁকনি এটি খুঁজে দেয়। একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই। একটি `on_run_error` hook-এ container সরান, যেমন [E2B](e2b-sandbox.md#clean-up)-এর জন্য দেখানো, বা [Prepare a container before the run](#prepare-a-container-before-the-run)-এর মতো নিজে backend তৈরি করুন।

/// tip | পরামর্শ

পুরনো সব ভুলে যাওয়া container একবারে দেখতে terminal-এ চালান: `docker ps --all --filter label=ai.pydantic.workspace=true`। নিশ্চিত হয়ে সেগুলো `docker rm -f <name>` দিয়ে সরাতে পারেন।

///

## কমান্ড কীভাবে চলে { #how-commands-run }

container image-এর নিজস্ব entrypoint বা কমান্ড চালায় না, তাই boot-এ image যে সার্ভিস চালু করত তা চলছে না; একটি কমান্ড দিয়ে এটি শুরু করুন। container তৈরি বা চালু করা, image টানাসহ, একটি কমান্ডের `timeout` দিয়ে সীমিত নয়। ফাইল কাজ container-এ কমান্ড হিসেবে চলে, তাই বড় ফাইল পড়া আর লেখা ধীর: বড় ডেটার জন্য `docker_args` দিয়ে একটি ডিরেক্টরি mount করুন।

তৈরি বা চালু করা যায় না, বা কমান্ডের মাঝে থেমে যায় এমন একটি container `WorkspaceUnavailableError` তোলে। exit code কমান্ডের নিজের, এমনকি যখন এটি এমন একটি যা `docker` নিজের error-এর জন্যও ব্যবহার করে।

একটি timeout বা বাতিলে, container-এ কমান্ড আর এর শুরু করা process থামানো হয়; নিজস্ব একটি session-এ বিচ্ছিন্ন হয়ে যাওয়া একটি কমান্ড, যেমন একটি [Shell](shell.md) background job, চলতে থাকে।

Docker-এ, একটি background process-কে এর আউটপুট খোলা রাখতে দেওয়া একটি কমান্ড, যেমন server-এর আউটপুট redirect না করে `server &`, সেই process বেরোনো পর্যন্ত ফেরত আসে না: এটি redirect করুন, যেমন `server > server.log 2>&1 &`। Podman-এ, কমান্ড নিজে বেরোলেই ফেরত আসে।

Podman-ও কাজ করে: `executable='podman'` দিন। capability বা backend তৈরির সময় CLI একবার `PATH`-এ খোঁজা হয়। `docker` client আপনার environment থেকে পায় `DOCKER_HOST`, `DOCKER_CONTEXT`, `DOCKER_CONFIG`, `SSH_AUTH_SOCK` আর একটি daemon বাছা ও পৌঁছানোর অন্য variable, প্রতিটি লোকাল কমান্ড যে `PATH`, `HOME` আর locale পায় তার পাশাপাশি, আর এর বাইরে কিছু নয়।

## নিরাপত্তা মডেল { #security-model }

একটি container আপনার মেশিনের kernel ভাগ করে, তাই এটি [Smol Sandbox](smol-sandbox.md), [E2B](e2b-sandbox.md) বা [Modal](modal-sandbox.md)-এর মতো একটি VM-এর চেয়ে দুর্বল সীমা। ভেতরে, কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, সাধারণত `root`, তাই এজেন্ট যা চালায় তা container-এর যেকোনো কিছু বদলাতে পারে।

- Docker socket বা secret রাখা ডিরেক্টরি mount করবেন না। একটি লেখা-যোগ্য mount কমান্ডকে আপনার মেশিন পরে চালায় এমন ফাইলও বদলাতে দেয়, যেমন একটি virtualenv, এর ভেতরের `docker` CLI, বা git hook। image অনুমতি দিলে `docker_args` দিয়ে `--cap-drop ALL`, `--user` বা `--read-only`-এর মতো শক্তিবৃদ্ধি যোগ করুন।
- একটি অনুপস্থিত `working_dir` container-এর ব্যবহারকারী হিসেবে তৈরি হয়, তাই `--user`-সহ, `working_dir`-কে সেই ব্যবহারকারী লিখতে পারে এমন একটি ডিরেক্টরিতে নির্দেশ করুন, যেমন একটি mount, বা image-এর নিজস্বটি ব্যবহার করতে `working_dir=None` দিন। `--read-only`-সহ, একটি লেখা-যোগ্য working directory mount করুন।
- Linux-এ, একটি mount করা ডিরেক্টরিতে কমান্ডের লেখা ফাইল আপনার মেশিনেও container-এর ব্যবহারকারীর মালিকানাধীন হয়, যা `root`, যদি না আপনি নিজের ID-সহ `--user` দেন, যেমন `id -u` আর `id -g` থেকে `--user 1000:1000`।
- একটি কমান্ড চলার সময়, এর `env` মান আপনার মেশিনে process তালিকায় (`ps`) দৃশ্যমান।
- Docker আপনার `~/.docker/config.json`-এর proxy সেটিং প্রতিটি নতুন container-এ environment variable হিসেবে যোগ করে।
- `image` tag দিয়ে টানা হয়; প্রতিবার একই image পেতে একটি digest pin করুন, যেমন `python:3.13-slim@sha256:...`।

/// warning | সাধারণ ভুল

সুবিধার জন্য `docker_args=['-v', '/var/run/docker.sock:/var/run/docker.sock']` দেওয়া। এতে container-এর ভেতরের এজেন্ট আপনার মেশিনের Docker নিয়ন্ত্রণ পায় — একটি privileged container চালিয়ে আপনার পুরো মেশিনে প্রবেশ করতে পারে। Docker socket কখনো mount করবেন না।

///

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `image` | একটি নতুন container-এর image, যেমন `'python:3.13-slim'`। ডিফল্ট: `None`, যা শুধু ref দিয়ে container-এ যুক্ত হয় আর সরায়। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়, না থাকলে প্রথম ব্যবহারে তৈরি হয়। ডিফল্ট: `/workspace`; `None` image-এর নিজস্বটি ব্যবহার করে (`WORKDIR`, বা `/`)। |
| `env` | image-এর ওপরে প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। Docker-এর proxy সেটিং ছাড়া আপনার মেশিনের environment-এর কিছুই container-এ পৌঁছায় না, আর `env` capability-র `repr`-এর বাইরে রাখা হয়, কিন্তু এজেন্টের কমান্ড এটি পড়তে পারে। |
| `allow_internet_access` | একটি নতুন container Docker-এর ডিফল্ট bridge দিয়ে বাইরের নেটওয়ার্ক প্রবেশ পায় কিনা। ডিফল্ট: `True`; `False` একে `--network none` দিয়ে চালায়। |
| `docker_args` | একটি নতুন container-এর জন্য বাড়তি `docker run` আর্গুমেন্ট, যেমন mount, `--memory` বা `--user`; এখানে একটি `--pids-limit` 2048-এর ডিফল্ট বদলে দেয়। ডিফল্ট: `()`। |
| `executable` | চালানোর container CLI, যেমন `'podman'`, capability তৈরির সময় `PATH`-এ খোঁজা হয়। ডিফল্ট: `'docker'`। |

## Platform { #platforms }

এজেন্ট চালানো মেশিন POSIX (Linux বা macOS) হতে হবে, [`LocalWorkspace`](../workspace.md#platforms)-এর মতো। Windows-এ, তৈরির সময় `DockerSandboxBackend` `NotImplementedError` তোলে, তাই `DockerSandbox`-সহ একটি রানও তোলে।

## Telemetry { #telemetry }

`DockerSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ container লেখে `pydantic_ai.workspace.provider` (`docker`) আর `pydantic_ai.workspace.id` (এর নাম) হিসেবে। একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.docker_sandbox.DockerSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/docker-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.docker_sandbox.DockerSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/docker-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[DockerSandbox(image='python:3.13-slim'), Coder()]` — আপনার `docker` CLI দিয়েই, কোনো SDK নয়; Podman-এ `executable='podman'`।
* ইন্টারনেট ডিফল্টভাবে চালু — অবিশ্বস্ত কাজে `allow_internet_access=False`।
* project ডিরেক্টরি `docker_args`-এ `-v` দিয়ে mount; Docker socket কখনো নয়।
* container kernel ভাগ করে — VM-এর চেয়ে দুর্বল সীমা।
* container নিজে থেকে সরানো হয় না — `destroy(ref)` বা `docker ps --filter label=ai.pydantic.workspace=true`।

///
