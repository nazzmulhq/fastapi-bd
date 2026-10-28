
# Modal Sandbox { #modal-sandbox }

/// note | এই পেজে যা শিখবেন

* আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [Modal](https://modal.com) cloud sandbox-এ এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো।
* একই sandbox-এ চালিয়ে যাওয়া, পরে আবার যুক্ত হওয়া, রানের আগে প্রস্তুত করা আর **পরিষ্কার করা** (sandbox নিজে থেকে বন্ধ হয় না!)।
* কনফিগারেশন, durable execution, telemetry আর আগের version থেকে migrate।

///

আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [Modal](https://modal.com) cloud sandbox-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/modal_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[modal,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[modal,anthropic]"
```

///


/// tab | pip

```bash
modal token new
```

///

/// tab | uv

```bash
uv run modal token new
```

///


এটি আপনার Modal credential সংরক্ষণ করে; CI-তে, এর বদলে `MODAL_TOKEN_ID` আর `MODAL_TOKEN_SECRET` সেট করুন। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান, আর উদাহরণের জন্য `ANTHROPIC_API_KEY` সেট করুন।

## দ্রুত শুরু { #quick-start }

⟦CODE1⟧

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, sandbox-এ চলে। `Coder`-এর `RepoContext` রান শুরু হলে sandbox তৈরি করে; এর বদলে প্রথম টুল কলে তৈরি করতে `Coder(repo_context=False)` দিন। রান শেষ হওয়ার পরও sandbox চলতে থাকে, আর bill হতে থাকে; দেখুন [Clean up](#clean-up)।

একটি নতুন sandbox সর্বোচ্চ 24 ঘণ্টা বাঁচে, Modal-এর সর্বোচ্চ; এটি আগে শেষ করতে `ModalSandbox(sandbox_timeout=3600)` দিন। Modal একটি image তৈরি বা আনার সময় প্রথম ব্যবহারে কয়েক মিনিট লাগতে পারে। Modal sandbox চালু করতে না পারলে, যেমন image না থাকায়, প্রথম ব্যবহার কারণ বলা একটি error তোলে।

ডিফল্ট image `root` হিসেবে `/root`-এ চলে, home ডিরেক্টরি, Python 3.12, `git` আর `rg`-সহ, কিন্তু আপনার project-এর কোনো dependency নেই, এমনকি `pytest`-ও নয়। এগুলো একটি নিজস্ব `image`-এ ইনস্টল করুন, বা রানের আগে `await workspace.run(['pip', 'install', ...])` দিয়ে, যেমন [Prepare a sandbox before the run](#prepare-a-sandbox-before-the-run)-এ। project home ডিরেক্টরির বাইরে রাখতে `ModalSandbox(working_dir='/root/project')` দিন; একটি নতুন sandbox এটি তৈরি করে। একটি নিজস্ব image এর নিজের working directory-তে কমান্ড শুরু করে।

/// warning | সতর্কতা: খরচ

রান শেষ হলেও sandbox **বন্ধ হয় না** আর Modal bill করতে থাকে — ডিফল্টভাবে 24 ঘণ্টা পর্যন্ত! কাজ শেষে `await ModalSandbox().destroy(result.workspace.ref)` দিয়ে বন্ধ করুন, বা `idle_timeout=` দিন যাতে অব্যবহৃত sandbox আগে বন্ধ হয়। দেখুন [Clean up](#clean-up)।

///

## একই sandbox-এ চালিয়ে যাওয়া { #continue-in-the-same-sandbox }

⟦CODE2⟧

পরের রান message history-তে sandbox খুঁজে পায় আর এতে কাজ করে, তাই clone তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন sandbox শুরু করে। sandbox বন্ধ বা মেয়াদোত্তীর্ণ হয়ে গেলে, রান একটি খালি sandbox-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা sandbox-এ চলা নিজের টুল লিখুন:

⟦CODE3⟧

আরও জানতে দেখুন [Workspaces](../workspace.md)।

বাতিল আর কমান্ডের সময়সীমা sandbox শেষ না করে foreground কমান্ড থামানোর চেষ্টা করে; সর্বোত্তম-চেষ্টার সতর্কতার জন্য দেখুন [What a timeout stops](#what-a-timeout-stops)। `Shell` একটি 30-সেকেন্ডের timeout সেট করে; আপনার নিজের টুলে, ওপরের মতো একটি `timeout` দিন।

শুধু আপনার নিজের টুল sandbox ব্যবহার করলে, অনুপস্থিত-টুলের সতর্কবার্তা চুপ করাতে `ModalSandbox(warn_if_no_tools=False)` দিন, বা এর শ্রেণি `ModalSandboxNoToolsWarning` ছাঁকুন।

ফাইল পড়া FIFO, device আর নিয়মিত ফাইল নয় এমন যেকোনো কিছুর জন্য `OSError` তোলে, লোকাল backend যেমন করে।

### একটি timeout কী থামায় { #what-a-timeout-stops }

`run(timeout=...)` sandbox অর্জনের পরে এর ঘড়ি শুরু করে আর কমান্ড শুরু, চালানো আর আউটপুট সংগ্রহ অন্তর্ভুক্ত করে। এর সময়সীমায় বা বাতিলে, backend কমান্ডের foreground process group থামানোর চেষ্টা করে, ভাগ করা sandbox বা বিচ্ছিন্ন background job নয়। আংশিক stdout আর stderr `WorkspaceTimeoutError`-এ পাওয়া যায়; stop RPC ব্যর্থ হলে, কমান্ড হয়তো তবুও চলে, তাই স্পষ্ট পরিষ্কার-কাজের জন্য sandbox ref রাখুন। `timeout=None`-এর কোনো কমান্ড সময়সীমা নেই; sandbox-এর নিজস্ব আয়ু আর idle সেটিং তবুও প্রযোজ্য। util-linux-এর `setsid` ছাড়া একটি নিজস্ব বা যুক্ত image-এ, একটি সময়সীমা বা বাতিল শুধু wrapper process থামায়, কমান্ডের সন্তানদের নয়; সেগুলোও থামাতে image-এ util-linux ইনস্টল করুন।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া sandbox-এ ফিরে আসতে, এর ref রেখে `workspace=` হিসেবে ফেরত দিন:

⟦CODE4⟧

ref কোনো credential রাখে না, তাই আবার যুক্ত হওয়া process-এরও আপনার Modal credential লাগে। message history একটির নাম দিলেও একটি নতুন sandbox শুরু করতে `workspace='new'` দিন।

`image`, `app_name`, `create_app_if_missing`, `sandbox_timeout` আর `idle_timeout` শুধু একটি নতুন sandbox গড়ে; `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য, আবার যুক্ত হওয়ার পরেও।

আগে থেকেই একটি `modal.Sandbox` আছে? একটি রানে `workspace=ModalSandboxBackend(sandbox=sandbox)` দিন, `pydantic_ai_harness.modal_sandbox` থেকে `ModalSandboxBackend`-সহ। `ModalSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন। workspace API কভার করে না এমন Modal সুবিধার জন্য একটি backend-এর `get_sandbox()` এর `modal.Sandbox` ফেরত দেয়; এখনও sandbox নেই এমন একটি backend-এ এটি একটি তৈরি করে, প্রথম কাজের মতো। এটি বদলায় না কে sandbox বন্ধ করে: যার হাতে ref, সে।

## রানের আগে একটি sandbox প্রস্তুত করা { #prepare-a-sandbox-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে বা প্যাকেজ ইনস্টল করতে, নিজে backend তৈরি করুন, `Workspace` দিয়ে এতে কাজ করুন, আর রানে দিন:

⟦CODE5⟧

setup বা রান ব্যর্থ হলেও `finally` sandbox বন্ধ করে। Modal sandbox তৈরি করার সময় task বাতিল হলে, সেখানে `backend.ref` তখনও `None`, আর Modal যে sandbox তৈরি করতে থাকে তা চলতে থাকে; এর ID `WARNING`-এ log হয় (দেখুন [Telemetry](#telemetry)), তাই `ModalSandbox().destroy(WorkspaceRef(provider='modal', id=...))` দিয়ে এটি বন্ধ করুন। এর বদলে এটি রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন।

## পরিষ্কার { #clean-up }

রান শেষ হওয়ার পরও sandbox চলতে থাকে, আর bill হতে থাকে। Pydantic AI কখনো এটি বন্ধ করে না। আপনার রাখা ref দিয়ে এটি বন্ধ করুন:

⟦CODE6⟧

`ModalSandbox().backend(ref)` I/O ছাড়াই একটি বিদ্যমান ref-এর জন্য একটি backend তৈরি করে। `destroy(ref)` sandbox ID সরাসরি ব্যবহার করে; এটি একটি মেয়াদোত্তীর্ণ sandbox আবার চালু করে না বা এর টুল চালায় না, আর আর নেই এমন একটি sandbox চুপচাপ ফেরত আসে। যে sandbox-এর image কমান্ড Modal-এর stop signal উপেক্ষা করে (যেমন একটি খালি `python` image), সেটি `destroy` ফেরত আসার পর প্রায় 30 সেকেন্ড চলতে পারে। শুধু আপনার মালিকানাধীন sandbox মুছুন।

যে sandbox আপনি বন্ধ করেন না তা শেষ হয় এর `sandbox_timeout` ফুরোলে, বা আপনি একটি সেট করলে `idle_timeout` সেকেন্ড কার্যকলাপ ছাড়া কাটার পর। দেখুন [Modal's timeouts](https://modal.com/docs/guide/sandbox#timeouts)।

একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই, আর `after_run` চলে না। Modal sandbox তৈরি করার সময় বাতিল হওয়া একটি রান কোনো hook-এর জন্য কোনো ref রেখে যায় না; দেখুন [Telemetry](#telemetry)। একটি ব্যর্থ রানের sandbox বন্ধ করতে, একটি `on_run_error` hook-এ পরিষ্কার করুন:

⟦CODE7⟧

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `image` | একটি নতুন sandbox-এর image: একটি registry tag বা একটি `modal.Image`। ডিফল্ট: Python 3.12, `git` আর `ripgrep`-সহ Debian slim। |
| `app_name` | একটি নতুন sandbox যে Modal app-এর। ডিফল্ট: `'pydantic-ai-harness'`। |
| `create_app_if_missing` | সেই app না থাকলে তৈরি করা। ডিফল্ট: `True`। |
| `sandbox_timeout` | Modal থামানোর আগে একটি নতুন sandbox কত সেকেন্ড বাঁচে (10-86,400)। ডিফল্ট: `86_400` (24 ঘণ্টা, Modal-এর সর্বোচ্চ)। |
| `idle_timeout` | Modal একটি নতুন sandbox থামানোর আগে কার্যকলাপ ছাড়া কত সেকেন্ড। ডিফল্ট: `None`, কোনো idle সীমা নেই। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়। ডিফল্ট: ডিফল্ট image-এ `/root`, অন্যথায় image-এর নিজস্ব working directory। একটি নতুন sandbox-এ তৈরি হয়; একটি যুক্ত বা caller-দেওয়া sandbox-এ এটি আগে থেকেই থাকতে হবে। |
| `env` | প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। আপনার মেশিনের environment-এর কিছুই sandbox-এ পৌঁছায় না। |
| `warn_if_no_tools` | এজেন্টের কোনো `Shell` বা `FileSystem` টুল না থাকলে সতর্ক করা। ডিফল্ট: `True`। |

Modal শুধু asyncio event loop-এ চলে: এর SDK asyncio task ব্যবহার করে, তাই Trio-র অধীনে backend `UserError` তোলে।

sandbox আপনার মেশিন থেকে বিচ্ছিন্ন, নেটওয়ার্ক থেকে নয়: এতে বাইরের দিকে ইন্টারনেট প্রবেশ আছে, আর প্রতিটি `env` মান মডেল আর এটি যা চালায় তার সবকিছু পড়তে পারে, এটি clone করা একটি repository-র কোডসহ। secret `env`-এ রাখুন শুধু তখনই যখন এজেন্টের সেগুলো পাওয়া উচিত। Modal-এর `block_network`-এর মতো নেটওয়ার্ক বাধার জন্য, নিজে `modal.Sandbox` তৈরি করে `workspace=` হিসেবে `ModalSandboxBackend(sandbox=...)` দিন।

## Durable execution { #durable-execution }

`temporal` extra-ও ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-harness[modal,anthropic,temporal]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[modal,anthropic,temporal]"
```

///


প্রথমে `localhost:7233`-এ একটি Temporal dev server চালান। activity নিবন্ধনের জন্য এজেন্ট আর workflow module স্তরে সংজ্ঞায়িত হতে হবে।

⟦CODE8⟧

এই উদাহরণের বাইরে অলসভাবে তৈরি sandbox-এর জন্য, `Coder(repo_context=False)` ব্যবহার করুন; ডিফল্টভাবে Coder রান শুরুর সময় repository instructions পড়ে।

এটি ব্যবহার করা workflow চলমান থাকা অবস্থায় একটি capability সরালে তাদের replay history বদলে যায়। পরিবর্তন deploy করার আগে ওই workflow drain করুন বা [Temporal worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) ব্যবহার করুন।

## Telemetry { #telemetry }

`ModalSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ sandbox লেখে `pydantic_ai.workspace.provider` আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে; রান শুরুর কাজ, যেমন `RepoContext`-এর repo instructions লোড, এজেন্ট run span-এ চলে। একটি sandbox তৈরি করলে `pydantic_ai_harness.modal_sandbox._backend` logger-এ `INFO`-তে এর ID log হয় (`Created Modal sandbox <id>`)। একটি নতুন sandbox-এর অপেক্ষায় থাকা প্রতিটি caller Modal এটি তৈরি শেষ করার আগে বাতিল হলে, কোনো পরিষ্কার-কাজ এর ref দেখে না, আর একই logger `WARNING`-এও এর ID log করে।

## আগের `ModalSandbox` থেকে আপগ্রেড { #upgrading-from-the-previous-modalsandbox }

আগের `ModalSandbox` নিজের `run_command`, `read_file`, `write_file` আর `list_directory` টুল নিবন্ধন করত আর রান শেষ হলে এর sandbox বন্ধ করত। এখন এটি শুধু sandbox দেয়, তাই ওপরে দেখানো মতো `Coder()`, বা `Shell()` আর `FileSystem()` যোগ করুন। পুরনো আর্গুমেন্ট এখনও তৈরি হয়, প্রতিস্থাপনের নাম দেওয়া একটি deprecation warning-সহ, আর উপেক্ষিত হয় (`sandbox_id` এখনও যুক্ত করে)। সরানো import প্রতিস্থাপনের নাম দেওয়া একটি error দিয়ে ব্যর্থ হয়। warning-গুলো `pydantic_ai_harness` থেকে `HarnessDeprecationWarning` ব্যবহার করে।

### Lifecycle-এ কী বদলেছে { #what-changed-in-the-lifecycle }

- একটি রান আর sandbox বন্ধ করে না। আপনি বন্ধ না করা পর্যন্ত বা এর `sandbox_timeout` শেষ না করা পর্যন্ত এটি চলে (দেখুন [Clean up](#clean-up))। Modal-কে একটি অব্যবহৃত sandbox আগে থামাতে `idle_timeout=` সেট করুন, বা কাজ শেষে `await ModalSandbox().destroy(result.workspace.ref)` ডাকুন।
- `sandbox_timeout`-এর ডিফল্ট এখন 5 মিনিটের বদলে 24 ঘণ্টা, যাতে পরের একটি রান একই sandbox-এ চালিয়ে যেতে পারে।
- একটি `message_history` চালিয়ে যাওয়া একটি রান আগের রানের sandbox-এ আবার যুক্ত হয়। একটি নতুনের জন্য `workspace='new'` দিন।
- একটি মেয়াদোত্তীর্ণ বা বন্ধ sandbox-এ আবার যুক্ত হলে `WorkspaceUnavailableError` ওঠে। কোনো খালি প্রতিস্থাপন তৈরি হয় না। কমান্ডের মাঝে sandbox বন্ধ হওয়ায় একটি কমান্ড 137 দিয়ে বেরোলে, এটি একই error তোলে; একটি চলমান sandbox-এ একটি SIGKILL করা কমান্ড exit 137 ফেরত দেয়।

### Migration টেবিল { #migration-table }

| আগের API | এখন |
| --- | --- |
| রান শেষ হলে sandbox বন্ধ | আর নয়: এর `sandbox_timeout` (ডিফল্ট 24 ঘণ্টা) এটি শেষ না করা পর্যন্ত চলে আর bill হয়। `idle_timeout=` সেট করুন, বা `await ModalSandbox().destroy(result.workspace.ref)` ডাকুন। |
| `image`, `app_name`, `create_app_if_missing`, `env` | অপরিবর্তিত। `image` একটি `modal.Image`-ও নেয়, আর এর ডিফল্টে এখন `git` আর `ripgrep` আছে। |
| `sandbox_timeout` | নাম অপরিবর্তিত। ডিফল্ট এখন `300`-এর বদলে `86_400` (24 ঘণ্টা)। |
| `workdir` | নাম বদলে `working_dir`। `workdir=` এখনও কাজ করে, একটি deprecation warning-সহ। |
| ডিফল্ট working directory | ডিফল্ট image-এ `/root`, যেখানে পুরনো ডিফল্ট image (`python:3.12-slim`) `/`-এ কমান্ড শুরু করত। একটি নিজস্ব image এর নিজস্ব `WORKDIR` রাখে। |
| `sandbox_id` | অবচিত; রানের নিজের কোনো ref না থাকলে এখনও সেই sandbox-এ যুক্ত করে, `workspace='new'`-সহও। `agent.run(..., workspace=WorkspaceRef(provider='modal', id=sandbox_id))` ব্যবহার করুন। |
| `session`, `ModalSandboxSession` | `session` অবচিত আর উপেক্ষিত; `ModalSandboxSession` সরানো। `agent.run(..., workspace=ModalSandboxBackend(sandbox=<modal.Sandbox>))` ব্যবহার করুন। |
| `default_command_timeout` | অবচিত আর উপেক্ষিত। `Shell(default_timeout=...)` ব্যবহার করুন। |
| `max_command_timeout` | অবচিত আর উপেক্ষিত, কোনো সরাসরি সমতুল্য ছাড়া: মডেলের চাওয়া একটি timeout কিছুই সীমিত করে না। `Shell(default_timeout=...)` একটি না দেওয়া কমান্ডের timeout সেট করে; `sandbox_timeout` একটি নতুন sandbox-এর আয়ু সীমিত করে আর যুক্ত sandbox-এ প্রযোজ্য নয়। |
| `max_output_bytes`, `max_output_lines` | অবচিত আর উপেক্ষিত। `Shell(max_output_chars=...)` বা `ToolOutputLimits` ব্যবহার করুন। যে কমান্ডের মিলিত stdout আর stderr 10 MiB পেরোয় তা থামানো হয় আর `WorkspaceOutputLimitError` তোলে। |
| `max_read_bytes` | অবচিত আর উপেক্ষিত। `FileSystem(max_read_lines=..., max_read_chars=...)` ব্যবহার করুন। |
| `instructions` | অবচিত আর উপেক্ষিত। এজেন্টের `instructions` ব্যবহার করুন। |
| `run_command` টুল | সরানো। `Shell()` ব্যবহার করুন। |
| `read_file`, `write_file`, `list_directory` টুল | সরানো। `FileSystem()` ব্যবহার করুন। এটি শুধু working directory আর এর নিচে পৌঁছায়; `FileSystem(root_dir='/')` পুরো sandbox-এ পৌঁছায়, পুরনো টুলগুলোর মতো। `read_file`-এর `offset` এখন শূন্য-ভিত্তিক: পুরনো টুল 1 থেকে লাইন গুনত। |
| `Shell()` বা `FileSystem()`-এর পাশে `PrefixTools(ModalSandbox(...), prefix='modal')` | `modal_*` টুল চলে গেছে, আর prefix-ছাড়া `Shell` আর `FileSystem` টুল, যা আগে আপনার মেশিনে কাজ করত, এখন sandbox-এ চলে। `PrefixTools` বাদ দিন। |
| `ModalSandboxExecResult` | সরানো। `pydantic_ai.workspaces.CommandResult` ব্যবহার করুন। |
| `ModalSandboxError` | সরানো। `pydantic_ai.workspaces.WorkspaceError` ধরুন। এটি কভার করে না 10 মিনিটের মধ্যে শেষ না হওয়া sandbox তৈরি (`TimeoutError`), বা সংযোগ ব্যর্থতার মতো সাময়িক Modal error, যা অপরিবর্তিত প্রচারিত হয় যাতে একটি durable engine এগুলো retry করতে পারে। `modal` প্যাকেজ ছাড়া, `pydantic_ai_harness.modal_sandbox` import করলে `ImportError` ওঠে। |
| `ModalSandboxTerminalError`, `ModalSandboxUnavailableError`, `ModalSandboxAuthError` | সরানো। `pydantic_ai.workspaces.WorkspaceUnavailableError` ধরুন। |

## API রেফারেন্স { #api-reference }

⟦CODE9⟧

/// info | API রেফারেন্স

`pydantic_ai_harness.modal_sandbox.ModalSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/modal-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.modal_sandbox.ModalSandboxNoToolsWarning`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/modal-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[ModalSandbox(), Coder()]` — কমান্ড আর ফাইল একটি বিচ্ছিন্ন Modal cloud sandbox-এ চলে; `modal token new` দিয়ে credential।
* sandbox রান শেষে বন্ধ হয় না আর bill হতে থাকে (ডিফল্ট 24 ঘণ্টা) — `destroy(ref)` বা `idle_timeout=` ব্যবহার করুন।
* একই sandbox-এ চালিয়ে যেতে message history দিন; history ছাড়া ফিরতে `result.workspace.ref` রাখুন।
* ডিফল্ট image-এ শুধু Python 3.12, `git`, `rg` — dependency নিজে ইনস্টল করুন।
* sandbox-এর ইন্টারনেট আছে; `env`-এর সবকিছু মডেল পড়তে পারে।

///
