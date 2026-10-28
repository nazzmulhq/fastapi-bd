
# BoxLite Sandbox { #boxlite-sandbox }

/// note | এই পেজে যা শিখবেন

* কোনো cloud অ্যাকাউন্ট বা daemon ছাড়া আপনার নিজের মেশিনে একটি [BoxLite](https://github.com/boxlite-ai/boxlite) micro-VM-এ এজেন্টের কমান্ড আর ফাইল চালানো।
* নেটওয়ার্ক প্রবেশ আর `allowed_hosts` দিয়ে শুধু নির্দিষ্ট host-এ যেতে দেওয়া।
* একই box-এ চালিয়ে যাওয়া, অন্য BoxLite অপশন, পরিষ্কার, নিরাপত্তা মডেল আর platform।

///

আপনার নিজের মেশিনে একটি [BoxLite](https://github.com/boxlite-ai/boxlite) micro-VM-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান, আপনার ফাইল আর process থেকে বিচ্ছিন্ন, কোনো cloud অ্যাকাউন্ট ছাড়া।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/boxlite_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[boxlite,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[boxlite,anthropic]"
```

///


`boxlite` extra [BoxLite-এর Python SDK](https://github.com/boxlite-ai/boxlite/tree/main/sdks/python) ইনস্টল করে, যা BoxLite runtime ধারণ করে: চালানোর মতো কোনো daemon নেই। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান, আর উদাহরণের জন্য `ANTHROPIC_API_KEY` সেট করুন।

BoxLite Apple silicon-এ macOS 14 বা নতুনতর আর x86_64 ও aarch64-এর Linux-এর (glibc 2.28 বা নতুনতর) জন্য, Python 3.14 পর্যন্ত wheel দেয়। Linux-এ, এজেন্ট চালানো ব্যবহারকারীর `/dev/kvm`-এ পড়া আর লেখার অনুমতি লাগে। দেখুন [Platforms](#platforms)।

## দ্রুত শুরু { #quick-start }

⟦CODE1⟧

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, নিজস্ব kernel আর filesystem-সহ একটি VM-এ চলে। রানের প্রথম workspace ব্যবহারে box boot হয়; `Coder`-এ, `RepoContext` রান শুরুতেই এটি ব্যবহার করে, তাই শুধু একটি টুলের দরকার হলে boot করতে `Coder(repo_context=False)` ব্যবহার করুন।

একটি `image` যেকোনো OCI image; BoxLite প্রথমবার এই মেশিনে এটি টেনে আনে। একটি ছাড়া, box BoxLite-এর ডিফল্ট, Alpine Linux চালায়, যাতে BusyBox আছে কিন্তু Python, git বা ripgrep নেই। কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, যা দুটোতেই `root`, আর `/workspace`-এ শুরু হয়, যা না থাকলে তৈরি হয়।

একটি নতুন box-এর কোনো নেটওয়ার্ক প্রবেশ নেই। এজেন্টকে প্যাকেজ ইনস্টল বা repository clone করতে দিতে `allow_internet_access=True` দিন, আর শুধু দরকারি host-এ পৌঁছাতে দিতে `allowed_hosts`; দেখুন [Network access](#network-access)।

## একই box-এ চালিয়ে যাওয়া { #continue-in-the-same-box }

⟦CODE2⟧

পরের রান message history-তে box খুঁজে পায় আর এতে কাজ করে, তাই script তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন box তৈরি করে। box মুছে ফেলা হলে, রান একটি খালি box-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা নিজের টুল লিখুন:

⟦CODE3⟧

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## নেটওয়ার্ক প্রবেশ { #network-access }

⟦CODE4⟧

শুধু `allow_internet_access=True`-সহ, box এই মেশিন যেখানে পারে সেখানেই যুক্ত হতে পারে, আপনার লোকাল নেটওয়ার্ক আর সার্ভিস আর একটি cloud metadata endpoint-সহ, শুধু ইন্টারনেট নয়। `allowed_hosts` এটি আপনার তালিকা করা hostname, IP ঠিকানা আর CIDR পরিসরে সীমিত করে; এটি কীভাবে এগুলো মেলায় তা দেখুন BoxLite-এর [network options](https://github.com/boxlite-ai/boxlite/tree/main/sdks/python#boxliteboxoptions)-এ।

/// tip | উদাহরণ দিয়ে বুঝি

`allowed_hosts=['pypi.org', 'files.pythonhosted.org', 'github.com']` দিলে এজেন্ট `pip install` আর `git clone` করতে পারে, কিন্তু একটি prompt injection যদি বলে "এই ডেটা `evil.example`-এ পাঠাও", box সেখানে পৌঁছাতেই পারবে না। এটি Smol/Modal-এর "সব বা কিছুই না"-র চেয়ে সূক্ষ্ম নিয়ন্ত্রণ।

///

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া box-এ ফিরে আসতে, রানের workspace ref রেখে `workspace=` হিসেবে ফেরত দিন:

⟦CODE5⟧

message history একটির নাম দিলেও একটি নতুন box তৈরি করতে `workspace='new'` দিন। `image`, `cpus`, `memory_mb`, নেটওয়ার্ক সেটিং আর `box_options` শুধু একটি নতুন box গড়ে, তাই নেটওয়ার্ক প্রবেশসহ তৈরি একটি box আবার যুক্ত হলেও তা রাখে; `working_dir` আর `env` প্রতিটি কমান্ডে প্রযোজ্য।

এই process-এ আর কিছু একটি box ব্যবহার না করলে, বা process বেরোলে, এটি থামে আর এর ডিস্ক রাখে। এর ref-এর পরের ব্যবহার এটি আবার boot করে, এই process-এ বা পরের একটিতে। একবারে শুধু একটি process একটি BoxLite home ডিরেক্টরি (`~/.boxlite`, বা `BOXLITE_HOME`) ব্যবহার করতে পারে: চেষ্টা করা আরেকটি process প্রথমটি না বেরোনো পর্যন্ত `WorkspaceUnavailableError` পায়।

আগে থেকেই `boxlite.Boxlite.default()` থেকে একটি `boxlite.Box` আছে? রানে `workspace=BoxLiteSandboxBackend(sandbox=box)` দিন, `pydantic_ai_harness.boxlite_sandbox` থেকে `BoxLiteSandboxBackend`-সহ, বা box-এর নামসহ `BoxLiteSandboxBackend(ref=WorkspaceRef(provider='boxlite', id=...))`, বা এর নাম না থাকলে এর id। `BoxLiteSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন। backend কখনো box মোছে না। প্রতিটি উপায় কী গ্রহণ করে তা দেখুন [Which boxes a run can use](#which-boxes-a-run-can-use)-এ।

## অন্য BoxLite অপশন { #other-boxlite-options }

`box_options` একটি নতুন box-এ যেকোনো অন্য [`boxlite.BoxOptions`](https://github.com/boxlite-ai/boxlite/tree/main/sdks/python#boxliteboxoptions) আর্গুমেন্ট দেয়। এটি বর্তমান ডিরেক্টরি box-এ শুধু-পড়া mount করে:

⟦CODE6⟧

অন্য সাধারণগুলো হলো এজেন্টের শুরু করা একটি server-এ পৌঁছাতে `ports`, আপনার নাম দেওয়া host-এ box-এর HTTPS রিকোয়েস্টে BoxLite-কে credential যোগ করতে দিতে `secrets`, `disk_size_gb` আর `user`। `BoxLiteSandbox`-এর নিজস্ব সেটিং `image`, `cpus`, `memory_mib`, `network`, `working_dir`, `env` আর `auto_delete` (আর এর অবচিত `auto_remove`) নিয়ন্ত্রণ করে, তাই `box_options`-এ এর একটি দিলে `UserError` ওঠে।

runtime-জুড়ে সেটিং, যেমন ব্যক্তিগত registry login বা BoxLite-এর home ডিরেক্টরি, প্রথম box ব্যবহারের আগে ডাকা `boxlite.Boxlite.init_default(boxlite.Options(...))`-এ যায়।

## রানের আগে একটি box প্রস্তুত করা { #prepare-a-box-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে বা প্যাকেজ ইনস্টল করতে, নিজে backend তৈরি করুন, `Workspace` দিয়ে এতে কাজ করুন, আর রানে দিন:

⟦CODE7⟧

setup বা রান ব্যর্থ হলেও `finally` box মোছে। এর বদলে এটি রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন। `workspace=` হিসেবে দেওয়া একটি backend-এ `BoxLiteSandbox`-এর সেটিং প্রযোজ্য নয়; backend-কে নিজস্বগুলো দিন। workspace API কভার করে না এমন BoxLite সুবিধার জন্য, যেমন `copy_in`, `snapshot` বা `stop`, `backend.get_sandbox()` SDK-র `boxlite.Box` ফেরত দেয়।

## পরিষ্কার { #clean-up }

একটি রান কখনো এর box মোছে না, আর মোছা না পর্যন্ত একটি box BoxLite-এর home ডিরেক্টরিতে এর ডিস্ক রাখে। আপনার রাখা ref দিয়ে এটি মুছুন:

⟦CODE8⟧

ইতিমধ্যে চলে যাওয়া একটি box মুছলে চুপচাপ ফেরত আসে। একবার শুরু হলে, একটি মোছা এর caller বাতিল হলেও শেষ হয়। `BoxLiteSandbox.backend(ref)` কিছু boot না করে একটি যুক্ত backend তৈরি করে।

কিছুই আপনার জন্য একটি box মোছে না। একটি তৈরি করলে এর id log হয় (দেখুন [Telemetry](#telemetry)), তাই একটি রাখা ref ছাড়া পেছনে ফেলে যাওয়া একটি খুঁজে পেতে পারেন, যেমন তৈরির পর crash করা একটি durable execution worker-এর, `await boxlite.Boxlite.default().list_info()` দিয়ে।

box তৈরি শুরু হওয়ামাত্র `backend.ref` সেট হয়, তাই [Prepare a box before the run](#prepare-a-box-before-the-run)-এর `finally` রান যা দিয়েই শেষ হোক box মোছে। box boot হওয়ার আগে বাতিল হওয়া একটি রান বাতিল রান শেষ করার আগে সেই box নিজেই মোছে। একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই: একটি `on_run_error` hook-এ box মুছুন, যেমন [E2B](e2b-sandbox.md#clean-up)-এর জন্য দেখানো, বা [Prepare a box before the run](#prepare-a-box-before-the-run)-এর মতো নিজে backend তৈরি করুন।

## কমান্ড কীভাবে চলে { #how-commands-run }

প্রতিটি কমান্ড box-এর `/bin/sh` দিয়ে চলে, image-এ `setsid` থাকলে নিজস্ব একটি session-এ, যেমন BusyBox আর util-linux image-এ থাকে। একটি অনুপস্থিত প্রোগ্রাম exit code 127 দেয়, আর একটি signal-এ মারা একটি প্রোগ্রাম 128 যোগ এর নম্বর। একটি `shell=True` string `/bin/sh -c`-এর অধীনে চলে। নিজস্ব image-এ একটি POSIX `/bin/sh` লাগে।

একটি timeout বা বাতিলে, backend কমান্ড আর এর শুরু করা process মারে, আর `WorkspaceTimeoutError`-এ এ পর্যন্ত আউটপুট ফেরত দেয়। যে job তাদের শুরু করা কমান্ডের চেয়ে বেশি টেকে, যেমন একটি [Shell](shell.md) background job, চলতে থাকে; কমান্ড বেরোনোর সর্বোচ্চ দুই সেকেন্ড পরে ফেরত আসে, এমন একটি job এর আউটপুট খোলা রাখলেও। `setsid` ছাড়া একটি image-এ, শুধু কমান্ড নিজে মারা যায়, আর একটি shell builtin-এর মতো নামের প্রোগ্রাম, যেমন `echo`, builtin-টি চালায়।

মিলিত আউটপুট 10 MiB পেরোলে, backend কমান্ড থামায় আর `WorkspaceOutputLimitError` তোলে, `stdout` আর `stderr`-এ প্রতিটি stream-এর প্রথম 65,536 অক্ষরসহ; এর বদলে বড় আউটপুট একটি ফাইলে redirect করুন। BoxLite পুরোটা পৌঁছাতে ব্যর্থ হওয়া আউটপুট কাটা অবস্থায় ফেরত না এসে `WorkspaceError` তোলে। backend-এর নিজস্ব `mkdir -p` আর `pwd -P` 60 সেকেন্ড পরে timeout করে, তাই একটি ভাঙা image রান আটকাতে পারে না।

ফাইল কাজ box-এ shell কমান্ড হিসেবে চলে, প্রতি কমান্ডে 64 KiB (দেখুন [Writing a backend](../workspace.md#writing-a-backend)), তাই image-এ সাধারণ ফাইল utility লাগে, যা Alpine-এর BusyBox-এ আছে।

একটি মোছা box `WorkspaceUnavailableError` তোলে, আর তেমনি একটি থামানো বা মোছায় শেষ হওয়া একটি কমান্ড; পরের কমান্ড একটি থামানো box আবার boot করে। সরানো একটি `working_dir` `WorkspaceError` তোলে। অন্য BoxLite ব্যর্থতা `boxlite.BoxliteError` হিসেবে প্রচারিত হয়, durable execution engine-এর retry করার জন্য। BoxLite SDK asyncio future ফেরত দেয়, তাই backend-এর asyncio event loop লাগে: Trio-র অধীনে, কাজ `UserError` তোলে।

## নিরাপত্তা মডেল { #security-model }

VM-ই সীমা: এর নিজস্ব kernel আর filesystem আছে, আর `box_options` `volumes` বা `ports` যোগ না করলে, এই মেশিনের কিছুই এতে mount করা নেই, কোনো port প্রকাশিত নয়, আর আপনার কোনো environment variable এতে পৌঁছায় না। ভেতরে, কমান্ড image-এর ব্যবহারকারী হিসেবে চলে, বেশিরভাগ image-এ `root`, তাই এজেন্ট যা চালায় তা box-এর যেকোনো কিছু বদলাতে পারে।

- BoxLite runtime আপনার process-এ আপনার OS ব্যবহারকারীর অনুমতিতে চলে, আর এর state এর home ডিরেক্টরিতে রাখে।
- `image` tag দিয়ে টানা হয়; প্রতিবার একই image পেতে একটি digest pin করুন, যেমন `python:3.12-slim@sha256:...`।
- `cpus` আর `memory_mb` একটি box সীমিত করে; একটি process কতগুলো box তৈরি করে তা কিছুই সীমিত করে না।

### একটি রান কোন box ব্যবহার করতে পারে { #which-boxes-a-run-can-use }

যে একটি ref দেয় সে এর নাম দেওয়া box-এ কমান্ড চালায়। BoxLite এই মেশিনের যেকোনো box নাম দিয়ে খুলতে পারে, অন্য টুলের আপনার ফোল্ডার mount করে তৈরি box-সহ। তাই কী গ্রহণযোগ্য তা নির্ভর করে box কোথা থেকে আসে তার ওপর:

| box কোথা থেকে আসে | কী গ্রহণযোগ্য |
| --- | --- |
| `BoxLiteSandbox`: message history-তে একটি ref, `workspace=ref`, `backend(ref)` বা `destroy(ref)` | শুধু `BoxLiteSandbox`-এর তৈরি box, নাম `pydantic-ai-` আর 32টি hex অঙ্ক। অন্য যেকোনো নাম কিছু চলার আগেই `ValueError` তোলে। |
| আপনার কোডের তৈরি `BoxLiteSandboxBackend(sandbox=box)` বা `BoxLiteSandboxBackend(ref=...)` | এই process-এর ডিফল্ট BoxLite runtime-এর যেকোনো box, mount বা প্রকাশিত port-সহ একটিও, কারণ আপনার কোড এটি বেছেছে। অন্য একটি runtime-এর box `UserError` তোলে: এর বদলে `boxlite.Boxlite.init_default(...)` দিয়ে ডিফল্টটি কনফিগার করুন। |

- আপনার দেওয়া একটি box-এ একটি রান সেই box-এর নাম message history-তে লেখে। শুধু সেই history দেওয়া পরের একটি রান `ValueError` তোলে; এটি box খোলে না বা একটি নতুন তৈরি করে না। আবার backend দিন, বা একটি নতুন box-এর জন্য `workspace='new'`।
- Durable execution এর ref থেকে workspace আবার তৈরি করে, তাই এটি শুধু `BoxLiteSandbox`-এর তৈরি box-এ কাজ করে।
- নাম প্রমাণ করে না একটি box কোথা থেকে এসেছে: আপনার OS ব্যবহারকারী হিসেবে চলা যেকোনো প্রোগ্রাম এমন নামের একটি box তৈরি করতে পারে। শুধু আপনার অ্যাপ্লিকেশনের নিজের রাখা ref দিন, আর ব্যবহারকারীর input থেকে `BoxLiteSandboxBackend(ref=...)` তৈরি করবেন না।

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `image` | একটি নতুন box-এর OCI image। ডিফল্ট: `None`, BoxLite-এর ডিফল্ট, Alpine Linux। |
| `cpus` | একটি নতুন box-এর vCPU। ডিফল্ট: `None`, BoxLite-এর ডিফল্ট। |
| `memory_mb` | একটি নতুন box-এর মেমরি, MiB-তে। ডিফল্ট: `None`, BoxLite-এর ডিফল্ট। |
| `allow_internet_access` | একটি নতুন box-এর এই মেশিনের নেটওয়ার্ক থেকে বাইরের নেটওয়ার্ক প্রবেশ আছে কিনা। ডিফল্ট: `False`। |
| `allowed_hosts` | `allow_internet_access`-সহ, একটি নতুন box যে একমাত্র hostname, IP ঠিকানা আর CIDR পরিসরে যুক্ত হতে পারে। ডিফল্ট: `None`, যেকোনো। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়, না থাকলে তৈরি হয়। ডিফল্ট: `/workspace`; `None` box-এর নিজস্বটি ব্যবহার করে (Alpine-এ `/`)। |
| `env` | image-এর ওপরে প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। আপনার মেশিনের environment-এর কিছুই box-এ পৌঁছায় না, আর `env` capability-র `repr`-এর বাইরে রাখা হয়, কিন্তু এজেন্টের কমান্ড এটি পড়তে পারে। |
| `box_options` | একটি নতুন box-এর জন্য অন্য `boxlite.BoxOptions` আর্গুমেন্ট, যেমন `volumes`, `ports`, `secrets` বা `disk_size_gb`। ডিফল্ট: `None`। capability-র `repr`-এর বাইরে রাখা হয়। |

## Platform { #platforms }

BoxLite macOS-এ Apple-এর Hypervisor framework আর Linux-এ KVM দিয়ে VM চালায়, তাই এটি Apple silicon-এ macOS 14 বা নতুনতর আর glibc 2.28 বা নতুনতর-সহ x86_64 ও aarch64-এর Linux-এ চলে। অন্য platform-এ, আর Python 3.15-এ, `boxlite` extra কিছুই ইনস্টল করে না আর `pydantic_ai_harness.boxlite_sandbox` import করলে `ImportError` ওঠে। Linux-এ, প্রথম রানের আগে `ls -l /dev/kvm` যাচাই করুন: VM চালাতে পারে না এমন একটি host রান প্রথম box ব্যবহার করার সময় `WorkspaceUnavailableError` তোলে। Ubuntu 24.04-এ, AppArmor সেই bubblewrap-কে user namespace তৈরি থেকে থামায় যার অধীনে BoxLite এর VM engine চালায়, তাই আপনি `bubblewrap` আর BoxLite-এর [troubleshooting guide](https://github.com/boxlite-ai/boxlite/blob/main/docs/guides/troubleshooting.md)-এর AppArmor profile ইনস্টল না করা পর্যন্ত box চালু হতে ব্যর্থ হয়; নতুনতর Ubuntu release সেই profile সহ আসে।

## Telemetry { #telemetry }

`BoxLiteSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ box লেখে `pydantic_ai.workspace.provider` (`boxlite`) আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে। একটি box তৈরি করলে তৈরি শুরুর আগে `pydantic_ai_harness.boxlite_sandbox` logger-এ INFO-তে `Creating BoxLite box <id>`-ও log হয়, তাই এটি রাখার আগে রান শেষ হলেও id রেকর্ডে থাকে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.boxlite_sandbox.BoxLiteSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/boxlite-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.boxlite_sandbox.BoxLiteSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/boxlite-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[BoxLiteSandbox(), Coder()]` — আপনার মেশিনে একটি micro-VM; কোনো daemon বা cloud অ্যাকাউন্ট নয়।
* ডিফল্ট: Alpine, নেটওয়ার্ক বন্ধ; `allow_internet_access=True` + `allowed_hosts=[...]` দিয়ে শুধু নির্দিষ্ট host।
* box নিজে থেকে মোছা হয় না — ref রাখুন আর `destroy` করুন।
* একবারে একটি process একটি BoxLite home ডিরেক্টরি ব্যবহার করতে পারে।
* Ubuntu 24.04-এ AppArmor profile লাগতে পারে।

///
