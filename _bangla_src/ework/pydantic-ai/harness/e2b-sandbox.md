
# E2B Sandbox { #e2b-sandbox }

/// note | এই পেজে যা শিখবেন

* আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [E2B](https://e2b.dev) cloud sandbox-এ এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো।
* sandbox-এর আয়ু (1 ঘণ্টা, তারপর pause), template, একই sandbox-এ চালিয়ে যাওয়া আর পরে যুক্ত হওয়া।
* dev server preview, পরিষ্কার, কনফিগারেশন আর durable execution।

///

আপনার মেশিনের বদলে একটি বিচ্ছিন্ন [E2B](https://e2b.dev) cloud sandbox-এ আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/e2b_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[e2b,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[e2b,anthropic]"
```

///


`anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান। তারপর `E2B_API_KEY` আপনার E2B API key-তে সেট করুন, আর উদাহরণের জন্য `ANTHROPIC_API_KEY`।

## দ্রুত শুরু { #quick-start }

⟦CODE1⟧

`Coder`-এর shell আর ফাইল টুল এখন আপনার মেশিনে নয়, sandbox-এ চলে। `Coder`-এ, `RepoContext` রান শুরু হলে sandbox তৈরি করে, কোনো টুল কল ছাড়াই; অলস তৈরির জন্য `Coder(repo_context=False)` ব্যবহার করুন। রান শেষ হওয়ার পরও এটি চলতে থাকে, আর bill হতে থাকে; দেখুন [Clean up](#clean-up)।

একটি sandbox 1 ঘণ্টা বাঁচে (`sandbox_timeout=3600`, E2B-এর Hobby plan-এর সর্বোচ্চ), তারপর pause হয়; পরের রান এটি আবার চালু করে। Pro plan `E2BSandbox(sandbox_timeout=86400)` পর্যন্ত অনুমতি দেয়। আপনার plan-এর সীমার বেশি একটি আয়ু `WorkspaceUnavailableError` তোলে, বার্তায় সীমাসহ।

কমান্ড home ডিরেক্টরি `/home/user`-এ শুরু হয়, যাতে dotfile আর pip cache থাকে। একটি project ডিরেক্টরি দিন, যেমন `E2BSandbox(working_dir='/home/user/project')`, যাতে project home ডিরেক্টরি না হয়; একটি নতুন sandbox-এ এটি আপনার জন্য তৈরি হয়।

E2B-এর ডিফল্ট template-এ ripgrep (`rg`) নেই। `Coder` এটি ছাড়াও খুঁজতে পারে, কিন্তু `rg` ইনস্টল করলে সার্চ দ্রুত হয়। একটি এজেন্ট রানের বাইরে, একবার একটি পুনর্ব্যবহারযোগ্য [template](https://e2b.dev/docs/template/quickstart) তৈরি করুন (তৈরিতে এক মিনিট লাগতে পারে):

⟦CODE2⟧

ডিফল্ট template-এ Python আর git আছে কিন্তু আপনার project-এর dependency নেই, এমনকি pytest-ও নয়। এগুলো একটি নিজস্ব template-এ ইনস্টল করুন, বা রানের আগে `await workspace.run(['pip', 'install', ...])` দিয়ে, যেমন [Prepare a sandbox before the run](#prepare-a-sandbox-before-the-run)-এ।

/// info | এক নজরে: Modal বনাম E2B

| | Modal | E2B |
|--|-------|-----|
| ডিফল্ট আয়ু | 24 ঘণ্টা, তারপর বন্ধ | 1 ঘণ্টা, তারপর **pause** (পরের রান আবার চালু করে) |
| ডিফল্ট working dir | `/root` | `/home/user` |
| ডিফল্ট image-এ `rg` | আছে | নেই (template-এ যোগ করুন) |
| Credential | `modal token new` | `E2B_API_KEY` |

///

## একই sandbox-এ চালিয়ে যাওয়া { #continue-in-the-same-sandbox }

⟦CODE3⟧

পরের রান message history-তে sandbox খুঁজে পায় আর এতে কাজ করে, তাই clone তখনও সেখানে থাকে। history ছাড়া, একটি রান একটি নতুন sandbox শুরু করে। একটি pause করা sandbox আবার চালু হয়। sandbox মেরে ফেলা হলে, রান একটি খালি sandbox-এ নতুন করে শুরু না করে `WorkspaceUnavailableError` তোলে।

## টুল বাছাই { #choose-the-tools }

একটি সরু এজেন্টের জন্য, `Coder`-এর বদলে [`Shell`](shell.md) আর [`FileSystem`](filesystem.md) ব্যবহার করুন, বা নিজের টুল লিখুন:

⟦CODE4⟧

Shell কমান্ড `user` অ্যাকাউন্ট হিসেবে চলে, আর backend-এর তৈরি ফাইল এর মালিকানাধীন। E2B-এর file service তবুও নিজের root অনুমতিতে পড়ে আর লেখে, তাই Unix অনুমতি ফাইল কাজ সীমিত করে না; ফাইল টুলকে একটি path থেকে দূরে রাখতে এগুলোর ওপর নির্ভর করবেন না।

একটি FIFO পড়লে একজন লেখকের অপেক্ষা না করে `OSError` ওঠে। E2B-এর file API loop করা symlink ডিরেক্টরি তালিকা থেকে বাদ রাখে।

stdout বা stderr উত্তরাধিকারসূত্রে পাওয়া একটি background সন্তান মূল কমান্ড বেরোনোর পরও SDK stream বন্ধ হওয়ার জন্য `run()`-কে অপেক্ষায় রাখতে পারে। একটি দীর্ঘ-চলা job শুরুর সময় background আউটপুট একটি ফাইলে redirect করুন; `Shell.start_command` নিজের আউটপুট log পরিচালনা করে।

### একটি timeout কী থামায় { #what-a-timeout-stops }

একটি timeout বা বাতিলে, backend কমান্ডের process group-এ TERM, তারপর KILL পাঠায়, যাতে এর সন্তানরা অন্তর্ভুক্ত, যদি না তারা অন্য process group বা session-এ সরে যায়। নিজস্ব template-এ `/bin/bash` আর `/bin/sh` লাগে; `setsid` (util-linux) ছাড়া, শুধু কমান্ডের নিজের process থামে। sandbox চলতে থাকে। থামানো সর্বোত্তম-চেষ্টা: E2B-তে পৌঁছানো না গেলে, কমান্ড হয়তো চলতে থাকে, তাই sandbox পরীক্ষা বা মারতে ref রাখুন।

যে কমান্ডের মিলিত আউটপুট 10 MiB পেরোয় তা একইভাবে থামানো হয় আর `WorkspaceOutputLimitError` তোলে, `stdout` আর `stderr`-এ প্রতিটি stream-এর প্রথম 65,536 অক্ষরসহ। এর বদলে বড় আউটপুট একটি ফাইলে redirect করুন।

একটি signal-এ মারা একটি কমান্ড E2B-তে `exit_code=-1` ফেরত দিতে পারে; SDK signal চিহ্নিত করে না, তাই এটি `128+signal`-এ রূপান্তরিত হয় না।

E2B-তে একই path-এ একসাথে লেখা atomic নয়: আপলোড মিশে যেতে পারে, আর একজন পাঠক একটি আংশিক ফাইল দেখতে পারে। `FileSystem` বা `Coder` ব্যবহারের সময় লেখকদের সমন্বয় করুন বা আলাদা path-এ লিখুন।

আরও জানতে দেখুন [Workspaces](../workspace.md)।

## পরে আবার যুক্ত হওয়া { #reattach-later }

message history ছাড়া sandbox-এ ফিরে আসতে, রানের workspace ref রেখে `workspace=` হিসেবে ফেরত দিন:

⟦CODE5⟧

ref কোনো credential রাখে না, তাই আবার যুক্ত হওয়া process-এরও `E2B_API_KEY` লাগে। message history একটির নাম দিলেও একটি নতুন sandbox শুরু করতে `workspace='new'` দিন।

`template` আর `allow_internet_access` শুধু একটি নতুন sandbox গড়ে। `sandbox_timeout` আবার যুক্ত হওয়ার সময়ও প্রযোজ্য, আর `working_dir` ও `env` প্রতিটি কমান্ডে প্রযোজ্য।

আগে থেকেই একটি `e2b.AsyncSandbox` আছে? একটি রানে `workspace=E2BSandboxBackend(sandbox=sandbox)` দিন, `pydantic_ai_harness.e2b_sandbox` থেকে `E2BSandboxBackend`-সহ। `E2BSandbox`-এর সেটিং এতে প্রযোজ্য নয়; backend-এ `working_dir=` আর `env=` দিন।

## রানের আগে একটি sandbox প্রস্তুত করা { #prepare-a-sandbox-before-the-run }

এজেন্ট শুরুর আগে ফাইল বসাতে বা প্যাকেজ ইনস্টল করতে, নিজে backend তৈরি করুন, `Workspace` দিয়ে এতে কাজ করুন, আর রানে দিন:

⟦CODE6⟧

setup বা রান ব্যর্থ হলেও `finally` sandbox মারে। এর বদলে এটি রাখতে, `backend.ref` রেখে পরে আবার যুক্ত হতে `workspace=` হিসেবে দিন।

## একটি dev server preview { #preview-a-dev-server }

`Shell`-সহ, এজেন্টকে `npm run dev -- --host 0.0.0.0 --port 3000`-এর জন্য `start_command` ব্যবহার করতে বলুন, তারপর প্রস্তুত না হওয়া পর্যন্ত `check_command` আর `curl http://localhost:3000/health` poll করতে। ফেরত আসা কমান্ড ID রাখুন। workspace ref দেওয়া থাকলে, `sandbox = await capability.backend(ref).get_sandbox()` দিয়ে sandbox পান, যেখানে `capability` হলো এজেন্ট যে `E2BSandbox` দিয়ে চলে, যাতে এর `sandbox_timeout` প্রযোজ্য হয়, আর পাবলিক hostname-এর জন্য `sandbox.get_host(3000)` ব্যবহার করুন (preview URL-এর জন্য সামনে `https://` দিন)। শেষ হলে, workspace যুক্ত অবস্থায় ID দিয়ে `stop_command` ডাকুন, তারপর `await E2BSandbox().destroy(ref)` দিয়ে sandbox মুছুন। দরকারের চেয়ে বেশি সময় একটি পাবলিক preview চালু রাখবেন না।

/// warning | সতর্কতা

`get_host(3000)`-এর URL **পাবলিক** — লিংক জানা যে কেউ আপনার dev server-এ পৌঁছাতে পারে। এতে debug endpoint, পরীক্ষার ডেটা বা secret থাকলে ঝুঁকি। কাজ শেষ হলেই server আর sandbox বন্ধ করুন।

///

## পরিষ্কার { #clean-up }

রান শেষ হওয়ার পরও sandbox চলতে থাকে, আর bill হতে থাকে। Pydantic AI এটি মারে না। E2B sandbox তৈরি করার সময় একটি রান বাতিল হলে, E2B উত্তর দিলেই ref তবুও লেখা হয়; id-ও log হয় (দেখুন [Telemetry](#telemetry))। E2B-এর উত্তর কখনো না এলে, sandbox কোনো ref বা log entry ছাড়াই থাকতে পারে; E2B dashboard-এ এটি খুঁজে মারুন। অন্যগুলো আপনার রাখা ref দিয়ে মারুন:

⟦CODE7⟧

`E2BSandbox.backend(ref)` I/O ছাড়াই একটি যুক্ত backend তৈরি করে; `destroy(ref)` যুক্ত না হয়ে ID দিয়ে মারে। এটি একটি pause করা sandbox-ও মারে, আবার চালু না করেই। যে sandbox আপনি মারেন না তা এর `sandbox_timeout` ফুরোলে pause হয়। দেখুন [E2B's sandbox lifecycle](https://docs.e2b.dev/sandbox)।

একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই রাখার মতো কোনো ref নেই। এর sandbox বন্ধ করতে, একটি `on_run_error` hook-এ পরিষ্কার করুন; একটি রান ব্যর্থ হলে `after_run` চলে না:

⟦CODE8⟧

## কনফিগারেশন { #configuration }

| অপশন | যা করে |
| --- | --- |
| `template` | একটি নতুন sandbox-এর জন্য E2B template-এর নাম বা ID। ডিফল্ট: `None`, E2B-এর `base`। একটি অজানা template প্রথম ব্যবহারে ব্যর্থ হয়। |
| `allow_internet_access` | একটি নতুন sandbox ইন্টারনেটে পৌঁছাতে পারবে কিনা। ডিফল্ট: `True`। |
| `sandbox_timeout` | E2B pause করার আগে sandbox কত সেকেন্ড বাঁচে, তৈরি আর আবার যুক্ত হওয়ার সময় সেট হয়। ডিফল্ট: `3_600` (1 ঘণ্টা, E2B-এর Hobby plan-এর সর্বোচ্চ)। |
| `working_dir` | কমান্ড যে absolute ডিরেক্টরিতে শুরু হয় আর আপেক্ষিক path যার বিপরীতে মীমাংসা হয়। ডিফল্ট: `None`, sandbox-এর নিজস্ব (ডিফল্ট template-এ `/home/user`, যেখানে কমান্ড `user` হিসেবে চলে); বহনযোগ্য কোডের জন্য আপেক্ষিক path পছন্দ করুন বা `working_dir` সেট করুন। একটি নতুন sandbox-এ তৈরি হয়; একটি যুক্ত বা caller-দেওয়া sandbox-এ এটি আগে থেকেই থাকতে হবে। |
| `env` | প্রতিটি কমান্ড যে environment variable পায়। ডিফল্ট: `None`। যেকোনোভাবে আউটপুট UTF-8 হিসেবে decode হয়; ডিফল্ট template-এর locale POSIX, তাই `wc -m`-এর মতো একটি টুলের bytes-এর বদলে অক্ষর গোনা উচিত হলে `env={'LC_ALL': 'C.UTF-8'}` দিন। আপনার মেশিনের environment-এর কিছুই sandbox-এ পৌঁছায় না। এজেন্টের কমান্ড এই মান পড়তে পারে, আর একটি নতুন sandbox প্রতিটি process-এর জন্য এগুলো রাখে, তাই এজেন্টের দেখা উচিত নয় এমন secret বাদ দিন। |

`E2BSandbox`-এর asyncio লাগে: E2B SDK প্রতিটি রিকোয়েস্ট asyncio-তে চালায়, তাই Trio-র অধীনে প্রতিটি কাজ, `destroy`-সহ, E2B-তে পৌঁছানোর আগেই `UserError` তোলে।

## Durable execution { #durable-execution }

`temporal` extra-ও ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-harness[e2b,anthropic,temporal]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[e2b,anthropic,temporal]"
```

///


প্রথমে `localhost:7233`-এ একটি Temporal dev server চালান। activity নিবন্ধনের জন্য এজেন্ট আর workflow module স্তরে সংজ্ঞায়িত হতে হবে।

⟦CODE9⟧

এটি ব্যবহার করা workflow চলমান থাকা অবস্থায় একটি capability সরালে তাদের replay history বদলে যায়। পরিবর্তন deploy করার আগে ওই workflow drain করুন বা [Temporal worker versioning](https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning) ব্যবহার করুন।

## Telemetry { #telemetry }

`E2BSandbox` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ sandbox লেখে `pydantic_ai.workspace.provider` আর `pydantic_ai.workspace.id` হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে; রান শুরুর কাজ, যেমন `RepoContext`-এর repo instructions লোড, এজেন্ট run span-এ চলে। একটি sandbox তৈরি করলে `pydantic_ai_harness.e2b_sandbox._backend` logger-এ INFO-তে `Created E2B sandbox <id>`-ও log হয়, তাই এটি রাখার আগে রান শেষ হলেও id রেকর্ডে থাকে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.e2b_sandbox.E2BSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/e2b-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.e2b_sandbox.E2BSandboxBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/e2b-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[E2BSandbox(), Coder()]` আর `E2B_API_KEY` — কমান্ড আর ফাইল একটি E2B cloud sandbox-এ।
* ডিফল্ট আয়ু 1 ঘণ্টা, তারপর pause; রান শেষেও bill হয় — `destroy(ref)` দিয়ে মারুন।
* ডিফল্ট template-এ `rg` নেই; একটি নিজস্ব template-এ `rg` আর dependency যোগ করুন।
* `get_host(port)` দিয়ে পাবলিক preview URL — কাজ শেষে বন্ধ করুন।
* Unix অনুমতি ফাইল টুল সীমিত করে না; একই path-এ একসাথে লেখা atomic নয়।

///
