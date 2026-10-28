
# SSH Workspace { #ssh-workspace }

/// note | এই পেজে যা শিখবেন

* আপনার নিজের `ssh` client দিয়ে অন্য একটি মেশিনে এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালানো।
* key দিয়ে login, কমান্ড কীভাবে চলে, আবার যুক্ত হওয়া আর নিরাপত্তা।

///

আপনার নিজের `ssh` client আর এর কনফিগারেশন দিয়ে, SSH-এর মাধ্যমে অন্য একটি মেশিনে আপনার এজেন্টের কমান্ড আর ফাইল সম্পাদনা চালান।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/ssh_workspace/)

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


SSH-এর জন্য কোনো extra লাগে না: capability আপনার মেশিনে আগে থেকে থাকা `ssh` client চালায়। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান।

## দ্রুত শুরু { #quick-start }

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Coder, SSHWorkspace

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SSHWorkspace('dev@build-box', working_dir='/srv/app', env={'UV_OFFLINE': '1'}), Coder()],
)
result = agent.run_sync('Run the test suite and fix the first failure.')
```

`Coder`-এর shell আর ফাইল টুল এখন `build-box`-এ চলে, আপনি যে ব্যবহারকারী হিসেবে login করেন সে হিসেবে, host-এ সেই ব্যবহারকারীর পূর্ণ কর্তৃত্বে। কমান্ড সীমাবদ্ধ করতে, capability-টি [`BubblewrapSandbox`](bubblewrap-sandbox.md)-এ মুড়ুন।

`working_dir`-এর ডিফল্ট login ডিরেক্টরি, আর একটি আপেক্ষিক সেখান থেকে শুরু হয়। ডিরেক্টরি আগে থেকেই থাকতে হবে। কমান্ড দূরের login environment আর `env=` পায়। একটি একক রানের জন্য, এর বদলে `agent.run`-এ `workspace=SSHWorkspaceBackend('dev@build-box')` দিন।

/// warning | সতর্কতা

SSH Workspace **কোনো বিচ্ছিন্নতা দেয় না** — এজেন্ট দূরের মেশিনে আপনার ব্যবহারকারীর সব কিছু করতে পারে (ফাইল মোছা, অন্য project ছোঁয়া, `sudo` থাকলে আরও বেশি)। একটি নিবেদিত, কম-অনুমতির ব্যবহারকারী ব্যবহার করুন, বা `BubblewrapSandbox` দিয়ে মুড়ুন।

///

## Login { #logging-in }

login-এর জন্য একটি key লাগে; password সমর্থিত নয়। `ssh` `BatchMode=yes` দিয়ে চলে, তাই password বা key passphrase চাওয়া একটি host রান আটকে না রেখে সাথে সাথে ব্যর্থ হয়, আর `ssh_args=` prompt আবার চালু করতে পারে না। passphrase ছাড়া একটি key ব্যবহার করুন, যেমন `ssh_args=['-i', key_path]` বা আপনার SSH কনফিগারেশনে `IdentityFile`, বা একটি passphrase-যুক্ত key `ssh-add` দিয়ে `ssh-agent`-এ লোড করুন। ব্যবহারকারী সেট করুন গন্তব্যে (`dev@build-box`), আপনার SSH কনফিগারেশনে `User` দিয়ে, বা `ssh_args=['-l', 'dev']` দিয়ে। আপনার SSH কনফিগারেশন (`~/.ssh/config`) port আর jump host-ও দেয়।

## কমান্ড কীভাবে চলে { #how-commands-run }

প্রতিটি কাজ একটি SSH সংযোগ খোলে, আর ফাইল কাজ host-এ shell কমান্ড হিসেবে চলে, তাই host-এ একটি POSIX `sh` আর সাধারণ ফাইল utility লাগে। এগুলো দ্রুত করতে আপনার SSH কনফিগারেশনে সংযোগ-ভাগাভাগি চালু করুন (একটি `ControlPersist` সময়সহ `ControlMaster auto`)।

/// tip | পরামর্শ

প্রতিটি টুল কলে নতুন SSH সংযোগ খোলা ধীর (প্রতিবার handshake)। `~/.ssh/config`-এ যোগ করুন:

```
Host build-box
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
```

এতে প্রথম সংযোগ খোলা থাকে আর পরের কমান্ডগুলো সেটি পুনর্ব্যবহার করে — অনেক দ্রুত।

///

প্রতিটি কমান্ড চালানো script host-এর `sh`-এ পৌঁছায় সংযোগের input-এ, এর command line-এ নয়, আর কমান্ড নিজে একটি খালি input পড়ে, লোকালে যেমন পড়ত। তাই একটি কমান্ড, এতে যত quote-ই থাকুক, host যতটা একটি প্রোগ্রাম আর্গুমেন্টকে অনুমতি দেয় ততটা লম্বা হতে পারে: Linux-এ 128 KiB। `ssh` এর input পাঠিয়ে না দিলে (`ssh_args`-এ `-n` বা `-f`, বা আপনার SSH কনফিগারেশনে `StdinNull`), script এর বদলে host-এর command line-এ যায়, যেখানে quote-ভরা একটি লম্বা কমান্ড শুরু করার জন্য খুব লম্বা হতে পারে।

পৌঁছানো যায় না এমন একটি host, একটি অনুপস্থিত working directory, বা কমান্ডের মাঝে হারানো একটি সংযোগ `WorkspaceUnavailableError` তোলে। exit code কমান্ডের নিজের, এমনকি যখন এটি 255, যা `ssh` নিজের error-এর জন্যও ব্যবহার করে।

একটি timeout বা বাতিলে, একটি দ্বিতীয় সংযোগ host-এ কমান্ডের process থামায়; নিজস্ব একটি session-এ বিচ্ছিন্ন হয়ে যাওয়া একটি কমান্ড, যেমন একটি [Shell](shell.md) background job, চলতে থাকে।

একটি background process-কে এর আউটপুট খোলা রাখতে দেওয়া একটি কমান্ড, যেমন server-এর আউটপুট redirect না করে `server &`, সেই process বেরোনো পর্যন্ত ফেরত আসে না, কারণ `sshd` আউটপুট বন্ধ হওয়ার অপেক্ষা করে: এটি redirect করুন, যেমন `server > server.log 2>&1 &`।

## পরে আবার যুক্ত হওয়া { #reattach-later }

ref হলো `WorkspaceRef(provider='ssh', id='dev@build-box:/srv/app')`, তৈরি থেকেই উপলব্ধ। `SSHWorkspace` শুধু নিজের host আর ডিরেক্টরির রেফারেন্স গ্রহণ করে, তাই message history-র একটি ref এটিকে অন্য মেশিনে নির্দেশ করতে পারে না। `SSHWorkspace(...).backend(ref)` সংযোগ না করে এমন একটি ref-এর জন্য backend তৈরি করে, আর অন্য যেকোনোটির জন্য `ValueError` তোলে।

## নিরাপত্তা { #security }

`SSHWorkspace`-এর দূরের ব্যবহারকারীর পূর্ণ কর্তৃত্ব আছে। `working_dir` বা একটি [FileSystem](filesystem.md) root কোনোটিই shell কমান্ডকে আটকায় না। আপনার লোকাল environment host-এ দেবেন না: কমান্ডের যে variable দরকার তা `env=` দিয়ে বাছুন, যা capability-র `repr`-এর বাইরে রাখা হয়।

`env=` মান `ssh`-এর পাঠানো script-এর ভেতরে যায়, যা এই মেশিন একটি লোকাল `sh`-কে আর্গুমেন্ট হিসেবে দেয়, তাই একটি কমান্ড চলার সময় এগুলো এই মেশিনের অন্য ব্যবহারকারীদের process তালিকায় (`ps`) দৃশ্যমান, আর `ssh` এর input পাঠিয়ে না দিলে host-এও (ওপরে দেখুন)। একটি ভাগ করা মেশিনে `env=`-এ secret রাখবেন না: এগুলো শুধু দূরের ব্যবহারকারী পড়তে পারে এমন একটি ফাইলে রাখুন, বা দূরের ব্যবহারকারীর login environment-এ।

## Platform { #platforms }

এজেন্ট চালানো মেশিন POSIX (Linux বা macOS) হতে হবে, [`LocalWorkspace`](../workspace.md#platforms)-এর মতো: Windows-এ `SSHWorkspace` তৈরি করলে `NotImplementedError` ওঠে। host-এ একটি POSIX `sh` আর সাধারণ ফাইল utility লাগে।

## Telemetry { #telemetry }

`SSHWorkspace` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ workspace লেখে `pydantic_ai.workspace.provider` (`ssh`) আর `pydantic_ai.workspace.id` (host আর ডিরেক্টরি, `include_content` ছাড়াও লেখা হয়, কারণ এটি কনটেন্ট নয়, environment চিহ্নিত করে) হিসেবে, আর একটি টুলের করা প্রতিটি কমান্ড বা ফাইল কাজ সেই tool call-এর span-এর ভেতরে চলে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.ssh_workspace.SSHWorkspace`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/ssh-workspace/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.ssh_workspace.SSHWorkspaceBackend`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/ssh-workspace/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `SSHWorkspace('dev@build-box')` — কমান্ড আর ফাইল দূরের মেশিনে, আপনার `ssh` client দিয়ে; কোনো extra লাগে না।
* শুধু key দিয়ে login (passphrase ছাড়া বা `ssh-agent`-এ); password নয়।
* দ্রুততার জন্য `ControlMaster`/`ControlPersist` চালু করুন।
* কোনো বিচ্ছিন্নতা নেই — দূরের ব্যবহারকারীর পূর্ণ কর্তৃত্ব; দরকারে `BubblewrapSandbox`।
* ভাগ করা মেশিনে `env=`-এ secret নয় — `ps`-এ দেখা যায়।

///
