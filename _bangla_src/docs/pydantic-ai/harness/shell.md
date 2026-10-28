
# Shell { #shell }

/// note | এই পেজে যা শিখবেন

* `Shell` দিয়ে এজেন্টকে shell কমান্ড চালানোর ক্ষমতা দেওয়া — allow/deny নিয়ন্ত্রণ, environment পরিষ্কার আর background process-সহ।
* পাঁচটি টুল (`run_command`, `start_command`, `check_command`, `stop_command`, ঐচ্ছিক `shell`)।
* কমান্ড নিয়ন্ত্রণ, ফাইল আর log-এর আকার-সীমা, environment নিয়ন্ত্রণ, স্থায়ী কমান্ড আর working directory।
* কেন এটি নিরাপত্তার সীমা নয়।

///

`Shell` একটি এজেন্টকে shell কমান্ড চালানোর ক্ষমতা দেয়, allow/deny নিয়ন্ত্রণ, environment পরিষ্কার আর পরিচালিত background process-সহ। এটি এজেন্টের workspace-এ চলা কমান্ড-চালানোর টুল দেয়, এমন background process-সহ যা একটি কথোপকথনের রান জুড়ে চলতে থাকে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/shell/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

এজেন্টদের প্রায়ই একটি build, একটি test suite, একটি linter বা একটি দ্রুত `grep` চালাতে হয়। subprocess সামলানো জোড়া দেওয়া -- আউটপুট stream করা, timeout, ছাঁটাই, নিয়ন্ত্রণহীন process মারা, আর রান জুড়ে background job ট্র্যাক করা -- হলো ঝামেলার boilerplate, যা প্রতিটি এজেন্ট নতুন করে আবিষ্কার করে।

`Shell` সেই ব্যবস্থা একটি একক [capability](../capabilities/overview.md)-তে বাঁধে: কনফিগার-যোগ্য allow/deny লিস্ট, কাজের শেষ অংশ রাখতে সমন্বয় করা আউটপুট ছাঁটাই, ঐচ্ছিক স্থায়ী working directory, তৈরি কমান্ড থেকে host-এর secret দূরে রাখতে পারে এমন environment নিয়ন্ত্রণ, আর ID দিয়ে মডেল যাচাই ও বন্ধ করতে পারে এমন background process।

## ব্যবহার { #usage }

`capabilities` প্যারামিটার দিয়ে একটি `Agent`-এ `Shell` দিন, কমান্ড চলার জন্য একটি workspace-সহ:

```python
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Shell

Path('./workspace').mkdir(exist_ok=True)
agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        LocalWorkspace('./workspace'),
        Shell(allowed_commands=['ls', 'cat', 'rg']),
    ],
)

result = agent.run_sync('List the Python files and summarize the largest one.')
print(result.output)
```

শুধু `Shell()`-ও কাজ করে, বিল্ট-ইন ধ্বংসাত্মক-কমান্ড denylist চালু রেখে।

## কমান্ড কোথায় চলে { #where-commands-run }

কমান্ড চলে রানের [workspace](../workspace.md)-এ: `LocalWorkspace`-এ আপনার মেশিনে, বা একটি sandbox-এ। workspace ছাড়া একটি রান শুরুতেই ব্যর্থ হয়। কমান্ড workspace-এর working directory-তে শুরু হয়; একটি সাবডিরেক্টরিতে চালাতে, এটি workspace-এ সেট করুন: `LocalWorkspace('./repo')`। একটি শুধু-পড়া workspace কমান্ড চালাতে পারে না, তাই সেই রানে `Shell` কোনো টুল দেয় না।

## টুল { #tools }

`Shell` ডিফল্টভাবে চারটি টুল দেয়, সাথে ঐচ্ছিক স্থায়ী `shell` টুল:

| টুল | উদ্দেশ্য |
|---|---|
| `run_command` | একটি কমান্ড synchronously চালিয়ে লেবেল করা stdout/stderr আর exit code ফেরত দেয়। প্রতি-কল বা ডিফল্ট timeout মানে। |
| `start_command` | একটি দীর্ঘ-চলা কমান্ড (server, watcher) background-এ চালু করে; একটি ID ফেরত দেয়। |
| `check_command` | একটি background কমান্ডের অবস্থা আর জমা আউটপুট জানায়। |
| `stop_command` | একটি background কমান্ড বন্ধ করে এর চূড়ান্ত আউটপুট ফেরত দেয়। |
| `shell` | ঐচ্ছিক: একটি কমান্ড `foreground` (`timeout` পর্যন্ত অপেক্ষা, তারপর তখনও চলমান process ফেরত দেওয়া) বা `background` মোডে চালায়। PID আর এর আউটপুট log ও JSON status ফাইলের path ফেরত দেয়। |

`run_command` একটি ঐচ্ছিক `timeout_seconds` আর্গুমেন্ট নেয়, যা একটি একক কলের জন্য `default_timeout` override করে। `check_command` আর `stop_command` `start_command`-এর ফেরত দেওয়া `command_id` string নেয়।

আউটপুট `[stdout]` / `[stderr]` চিহ্ন আর অশূন্য exit-এ একটি `[exit code: N]` লাইন দিয়ে লেবেল করা। এটি `max_output_chars` ছাড়ালে **শেষ অংশ** রাখা হয় (শুরু বাদ পড়ে), তাই error, stack trace আর `[stderr]` অংশ -- যা সবই শেষে পড়ে -- ছাঁটাইয়ে টিকে থাকে। Background কমান্ডের অবস্থা আর exit metadata ধরা আউটপুটের পরে থাকে, যাতে এগুলো রাখা শেষ অংশে থাকে।

/// tip | উদাহরণ দিয়ে বুঝি

`pytest` চালালে প্রথমে শত শত "PASSED" লাইন আসে, আর আসল ব্যর্থতার কারণ থাকে একদম শেষে। আউটপুট বড় হলে Shell শুরুটা ফেলে দিয়ে শেষটা রাখে — ঠিক যেভাবে আপনি terminal-এ স্ক্রল করে নিচে গিয়ে error খোঁজেন।

///

## কমান্ড নিয়ন্ত্রণ { #command-controls }

দুটি পরস্পর-বর্জিত লিস্ট ঠিক করে কোন executable চলতে পারে, সাথে shell operator আর interactive কমান্ডের ছাঁকনি:

| ফিল্ড | প্রভাব |
|---|---|
| `allowed_commands` | খালি না হলে, শুধু এই executable চলতে পারে (allowlist)। |
| `denied_commands` | এই executable সবসময় প্রত্যাখ্যাত (denylist)। |
| `denied_operators` | যে shell operator (যেমন `>`, `>>`, `\|`) উপস্থিত থাকলে প্রত্যাখ্যাত। |
| `allow_interactive` | `False` হলে (ডিফল্ট), TTY চায় এমন কমান্ড (`vi`, `sudo`, `ssh`, ...) আটকানো। |

`allowed_commands` আর `denied_commands` পরস্পর-বর্জিত -- একটি সেট করুন, দুটো নয়। দুটোর জন্যই খালি-নয় মান সেট করলে toolset তৈরির সময় একটি `ValueError` ওঠে। `denied_commands`-এর ডিফল্ট ধ্বংসাত্মক কমান্ডের একটি লিস্ট (`rm`, `rmdir`, `mkfs`, `dd`, `format`, `shutdown`, `reboot`, `halt`, `poweroff`, `init`); এটি বন্ধ করতে একটি খালি লিস্ট দিন। executable-এর নাম `shlex` দিয়ে বের করা হয়, তাই আর্গুমেন্ট যাচাই এড়াতে পারে না।

একটি খালি `allowed_commands` সংগ্রহ allowlist মোড বাছে না। কনফিগার করা `denied_commands` সক্রিয় থাকে; বাদ দিলে, এটি বিল্ট-ইন denylist। কমান্ড-নাম ছাঁকনি বন্ধ করতে `denied_commands=[]` দিন।

একটি প্রত্যাখ্যাত কমান্ড মডেলের কাছে একটি কঠিন error নয়, একটি [`ModelRetry`](../tools-advanced.md#tool-retries) হিসেবে প্রকাশিত হয়: রান চলতে থাকে আর মডেল এর বদলে একটি অনুমোদিত কমান্ড বাছতে পারে। মডেল যে অন্য প্রতিটি ব্যর্থতায় কাজ করতে পারে সেগুলোও তাই: একটি আগের কমান্ড মুছে ফেলা বা একটি ফাইল দিয়ে বদলানো একটি working directory, একটি NUL byte থাকায় বা operating system encode করতে পারে না এমন একটি অক্ষর থাকায় operating system চালু করতে অস্বীকার করা একটি কমান্ড, আর operating system চালু করার জন্য খুব লম্বা একটি কমান্ড, যা মডেলকে একটি ফাইলে লিখে চালাতে বলা হয়। মডেল যে ব্যর্থতায় কিছুই করতে পারে না সেগুলো তবুও রান বাতিল করে: একটি process বরাদ্দ করতে পারে না এমন একটি host, একটি ছোট কমান্ড চালু করার জন্যও খুব বড় একটি অ্যাপ্লিকেশন-দেওয়া `env`, আর একটি অ্যাপ্লিকেশন-দেওয়া `env`-এ একটি অবৈধ অক্ষর। এর timeout পেরিয়ে চলা একটি কমান্ড এ পর্যন্ত এর আউটপুট ফেরত দেয়, `[Command timed out after Ns]` দিয়ে শেষ। চলে যাওয়া একটি workspace রান শেষ করে।

/// warning | সর্বোত্তম-চেষ্টা, নিরাপত্তার সীমা নয়

`allowed_commands` দুর্ঘটনার বিরুদ্ধে একটি guardrail, একটি নিরাপত্তার সীমা নয়। যাচাই শুধু প্রথম token দেখে, আর `python`, `git`, `uv` আর `make`-এর মতো allowlist করা কমান্ড যেকোনো process চালু করতে পারে। allowlist এড়াতে চাওয়া একটি মডেল পারে। অবিশ্বস্ত কাজের জন্য, রানকে একটি বিচ্ছিন্ন workspace দিন, যেমন একটি [Modal sandbox](modal-sandbox.md) বা একটি container, যাতে কমান্ড এজেন্টের মেশিনের বদলে সেখানে চলে।

///

/// info | কেন allowlist এড়ানো যায়?

ধরুন `allowed_commands=['python']`। মডেল চালায় `python -c "import os; os.system('rm -rf data')"`। প্রথম token `python` — অনুমোদিত! কিন্তু ভেতরে যা খুশি চলল। তাই allowlist শুধু ভুল করে বিপজ্জনক কমান্ড চালানো ঠেকায়, ইচ্ছাকৃত অপব্যবহার নয়।

///

## কমান্ডের লেখা ফাইল সীমিত করা { #limit-files-written-by-commands }

`run_command` আর `start_command`-এর লেখা প্রতিটি নিয়মিত ফাইলের আকার সীমিত করতে `Shell(max_file_bytes=10_000_000)` সেট করুন, redirect করা আউটপুট আর background stdout/stderr log-সহ। `None` (ডিফল্ট) কোনো সীমা যোগ করে না। এটি `max_output_chars` থেকে আলাদা, যা ফেরত দেওয়া টুল ফল সীমিত করে।

সীমা কমান্ড আর এর চালু করা প্রতিটি process কভার করে, পূর্ণ 512-byte বা 1 KiB ব্লকে ওপরে গোল করা। workspace-এর নিজের সীমা কম হলে, কমান্ড `Unable to apply max_file_bytes.` দিয়ে ব্যর্থ হয়। এটি `persist_cwd=True` বা `tools=['shell']`-এর সাথে জোড়া যায় না।

ফাইল-আকারের signal-এ মারা একটি process একটি নির্ণয়-করা টুল ফল পায়; অন্য অশূন্য exit context হিসেবে কনফিগার করা সীমা অন্তর্ভুক্ত করে, কারণ প্রোগ্রাম লেখার error ধরে নিজের exit code বাছতে পারে। এজেন্ট এর আউটপুট কমিয়ে আবার চেষ্টা করতে পারে। Background ব্যর্থতা `check_command` বা `stop_command`-এ দেখা দেয়। error সামলে সফলভাবে বেরোনো কমান্ড তাদের exit status থেকে নির্ণয় করা যায় না। ফল তবুও `max_output_chars` মানে।

এটি একটি প্রতি-ফাইল সীমা, disk quota বা sandbox নয়: এটি আংশিক ফাইল সরায় না, বিদ্যমান ফাইল ছোট করে না, বা অনেক ছোট ফাইল তৈরি আটকায় না। সামগ্রিক ডিস্ক সুরক্ষা আর অবিশ্বস্ত কমান্ডের জন্য filesystem quota বা OS বিচ্ছিন্নতা ব্যবহার করুন। কোনো বাড়তি telemetry span তৈরি হয় না; বিদ্যমান tool-call ফল ব্যর্থতা আর সীমার context বহন করে।

## কমান্ডের log সীমিত করা { #limit-command-logs }

`start_command` আর `shell` কমান্ডের আউটপুট log `Shell(max_log_bytes=...)` দিয়ে সীমিত, ডিফল্ট 100 MB। একটি কমান্ড চলার সময় প্রতিটি log সেকেন্ডে একবার যাচাই হয় আর এটি শেষ হলে আরেকবার; সীমা পেরোনো একটি log খালি করা হয় আর এই বিজ্ঞপ্তি পায়
`[Log exceeded max_log_bytes=<n>; earlier output was cleared.]`। কমান্ড চলতে থাকে, তাই অনেক log করা একটি dev server থামানো হয় না, আর পরের আউটপুট স্বাভাবিকভাবে log হয়। এটি বন্ধ করতে `max_log_bytes=None` দিন।

এটি নিজের log পড়ে এমন একটি কমান্ডও থামায়, যেমন
`cat .pydantic-ai-harness/shell/*/output.log | grep failed`। এর আউটপুট এমন একটি log-এ যুক্ত হয় যা এটি এখনও পড়ছে, তাই সীমা ছাড়া এটি কখনো শেষে পৌঁছায় না আর ডিস্ক ভরা না হওয়া পর্যন্ত log বাড়ে। log খালি হলে, কমান্ড শেষ পর্যন্ত পড়ে বেরিয়ে যায়।

`max_file_bytes`-এর বিপরীতে, এটি `tools=['shell']`-এর সাথে কাজ করে আর শুধু log-এ প্রযোজ্য, কমান্ডের লেখা ফাইলে নয়। একটি log খালি হওয়ার আগে সীমা পেরিয়ে সর্বোচ্চ এক সেকেন্ডের আউটপুট বাড়তে পারে। একটি খালি করার জন্য কোনো telemetry span তৈরি হয় না: এটি log-এ বিজ্ঞপ্তি হিসেবে দেখা দেয় আর, একটি `shell` কল অপেক্ষার সময় ঘটলে, এর finished event-এ `truncated=True` হিসেবে।

## Environment নিয়ন্ত্রণ { #environment-control }

একটি কমান্ড পায় workspace-এর environment আর `Shell(env=...)`। `LocalWorkspace` আপনার `PATH`, `HOME`, `LANG`, `LC_ALL` আর `LC_CTYPE` পাঠায় আর আর কিছু নয়; একটি sandbox-এ থাকে এর provider যা কনফিগার করে। দুটি ফিল্ড ঠিক করে `Shell` কী যোগ করে:

| ফিল্ড | প্রভাব |
|---|---|
| `env` | workspace-এর নিজেরটির ওপরে প্রতিটি কমান্ডের environment-এ যোগ করা variable। |
| `denied_env_patterns` | `env` থেকে বাদ দেওয়া variable নামের glob pattern (`fnmatch`)। `denied_commands`-এর প্রতিচ্ছবি। |

`denied_env_patterns` শুধু `Shell(env=)` ছাঁকে, `LocalWorkspace(env=)` নয়, তাই আপনি একটি বড় mapping থেকে `env` তৈরি করে ঢোকার পথে সংবেদনশীল নাম বাদ দিতে পারেন। দুটোই খালি রাখলে কিছু যোগ হয় না।

```python
from pydantic_ai_harness import LLM_API_KEY_ENV_PATTERNS, Shell

# Add only the variables commands need.
Shell(env={'PYTHONUNBUFFERED': '1'})

# Or start from a larger mapping and drop LLM credentials from it (other secrets still pass).
app_env = {'PYTHONUNBUFFERED': '1', 'ANTHROPIC_API_KEY': 'sk-...'}
Shell(env=app_env, denied_env_patterns=LLM_API_KEY_ENV_PATTERNS)
```

`LLM_API_KEY_ENV_PATTERNS` সাধারণ provider prefix কভার করে (`ANTHROPIC_*`, `GATEWAY_*`, `GEMINI_*`, `GOOGLE_*`, `OPENAI_*`, `OPENROUTER_*`), সাথে `PYDANTIC_AI_GATEWAY_API_KEY`। এটি শুধু LLM credential লক্ষ্য করে -- এটি অন্য host secret কভার করে না (একটি `LOGFIRE_TOKEN`, একটি GitHub token, cloud credential), আর এর prefix মোটা দাগের, তাই `GOOGLE_*` `GOOGLE_APPLICATION_CREDENTIALS`-এর মতো non-credential var-ও সরায়। এটিকে একটি শুরুর বিন্দু ধরে নিজের pattern যোগ করুন।

কোনোটিই নিরাপত্তার সীমা নয়: `LocalWorkspace`-এ, একটি কমান্ড তবুও আপনার process-এর environment আর আপনার ফাইল পড়তে পারে। অবিশ্বস্ত কমান্ডের জন্য একটি sandbox ব্যবহার করুন।

## Background process { #background-processes }

`start_command` workspace-এর ভেতরে background-এ কমান্ড শুরু করে আর একটি ID ফেরত দেয়। এর আউটপুট working directory-তে `.pydantic-ai-harness/shell/`-এর নিচে log হয়, যা git-উপেক্ষিত। poll করতে `check_command(command_id)` আর বন্ধ করে চূড়ান্ত আউটপুট সংগ্রহ করতে `stop_command(command_id)` ব্যবহার করুন: পুরো process group `SIGTERM` পায়, তারপর একটি grace period-এর পর `SIGKILL`। `SIGTERM`-এ থামা একটি কমান্ড `[exit code: 143]` জানায়।

একটি background কমান্ড রানের সাথে বাঁধা নয়: একটি কথোপকথন কয়েকটি রান জুড়ে বিস্তৃত, তাই একই workspace-এ পরের একটি রান এর ID দিয়ে এটি যাচাই বা বন্ধ করতে পারে। এটি বেরোনো, `stop_command` থামানো বা workspace শেষ না হওয়া পর্যন্ত চলতে থাকে।

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Shell

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        LocalWorkspace('./app'),
        Shell(allowed_commands=['npm', 'curl']),
    ],
)

result = agent.run_sync(
    'Start the dev server with `npm run dev`, wait for it to boot, '
    'then curl http://localhost:3000/health and report the status.'
)
print(result.output)
```

/// warning | সাধারণ ভুল

একটি dev server `start_command` দিয়ে চালু করে ভুলে যাওয়া। এটি রান শেষ হলেও মারা হয় না — পরের দিন port 8000 "already in use" দেখাবে। কাজ শেষে `stop_command` দিয়ে (বা নিজের পরিষ্কার-কোড দিয়ে) background process বন্ধ করুন।

///

## স্থায়ী কমান্ড { #persistent-commands }

ওপরের চারটি টুলের বদলে স্থায়ী টুল নিবন্ধন করতে `tools`-এ `shell`-এর নাম দিন:

```python
from pydantic_ai_harness import Shell

Shell(tools=['shell'])
```

`shell(command, mode='foreground', timeout=None)` একটি ছোট supervisor-এর অধীনে কমান্ড শুরু করে, যা এর মিলিত আউটপুট একটি log-এ আর এর exit status একটি JSON ফাইলে লেখে (`{"pid": ..., "exit_code": ...}`, চলার সময় `exit_code` null)। টুলটি PID আর দুটি path ফেরত দেয়, তাই মডেল এর ফাইল টুল দিয়ে অগ্রগতি পড়ে আর ফলের নাম দেওয়া `kill` কমান্ড দিয়ে কমান্ড থামায়। Foreground exit status-এর জন্য সর্বোচ্চ `timeout` সেকেন্ড অপেক্ষা করে (ডিফল্ট `default_timeout`, সর্বোচ্চ `MAX_FOREGROUND_WAIT`, 270) আর log-এর শেষ 16,000 bytes, তারপর handle ফেরত দেয়, কমান্ড এখনও চললেও। log লম্বা হলে, ফল একটি লাইন থেকে শুরু হয় আর বলে কত আগের bytes বাদ দেয়; background সাথে সাথে handle ফেরত দেয়। handle শেষে আসে যাতে `max_output_chars`, যা একটি অতি-লম্বা ফলের শেষ অংশ রাখে, এগুলো বাদ দিতে না পারে। 270-সেকেন্ডের সীমা একটি টুল কলকে সাধারণ provider রিকোয়েস্ট timeout-এর চেয়ে ছোট রাখে, তাই একটি লম্বা build বা test run কথোপকথন আটকায় না: মডেল handle ফেরত পায়, অন্য কাজ করে আর status ফাইল poll করে।

কমান্ড এজেন্ট রান আর event loop-এর পরেও টেকে, তাই মডেলের শুরু করা একটি server workspace যতদিন টেকে ততদিন পরিবেশন করতে থাকে। কমান্ড শেষ হলে কিছুই এজেন্টকে জাগায় না; মডেল poll করে। একটি foreground কল বাতিল করলে কমান্ড মারা যায়। ফেরত দেওয়া log কখনো মোছা হয় না: নিজে পরিষ্কার করুন, আর বাচাল কমান্ডের আউটপুট সীমিত রাখুন।

`allowed_commands`, `denied_commands`, `denied_operators`, `allow_interactive`, `env` আর `denied_env_patterns` `shell`-এ ঠিক `run_command`-এর মতোই প্রযোজ্য। `persist_cwd` নয়: প্রতিটি `shell` কমান্ড workspace-এর working directory-তে শুরু হয়, `run_command` যা-ই ট্র্যাক করুক। কমান্ড আর log workspace-এ থাকে; এগুলো শুরু আর poll করা workspace কল replay-নিরাপদ নয়।

প্রতিটি `shell` কল `shell` namespace-এ অগ্রগতি event তৈরি করে, তাই একটি UI টুলের ফল পার্স না করে আউটপুট আসার সাথে সাথে দেখাতে পারে:

| Event | Dispatch | Payload |
|---|---|---|
| `CommandStartedEvent` | stream | `command`, `pid` |
| `CommandOutputEvent` | stream | `text`: মিলিত log-এর একটি অংশ, ধাপে ধাপে decode করা |
| `CommandFinishedEvent` | stream | `pid`, `output_path`, `status_path`, `exit_code`, `truncated`, `total_lines` |

একটি foreground কল অপেক্ষার সময় আউটপুট event তৈরি হয়: প্রতি কলে log-এর সর্বোচ্চ প্রথম 16,000 bytes, সর্বোচ্চ 4,096 bytes-এর অংশে, প্রতি 50 ms থেকে 1 s-এ poll করা। একটি background কল শুধু started আর finished event তৈরি করে। `finished` মানে টুল অপেক্ষা থামিয়েছে, কমান্ড বেরিয়েছে তা নয়: কোনো status প্রকাশিত না হওয়া পর্যন্ত `exit_code` `None`, আর `truncated` বলে event যা দেখিয়েছে log-এ তার চেয়ে বেশি ছিল। `total_lines` 1 MiB পর্যন্ত log-এ যৌক্তিক লাইন গোনে আর বড় log-এর জন্য `None`, যা scan করা হয় না। কলের সময় `max_log_bytes` log খালি করলে, আউটপুট event এর বিজ্ঞপ্তি থেকে আবার শুরু হয়, `truncated` সত্য আর `total_lines` `None`। একটি বাতিল কল হয়তো কোনো finished event তৈরি করে না। event কমান্ডের লেখা আর কমান্ডের আউটপুট বহন করে, তাই রেন্ডারের সময় এগুলোকে অবিশ্বস্ত ধরুন। এগুলো কোনো telemetry span যোগ করে না; core আগেই tool call trace করে।

## Working directory { #working-directory }

ডিফল্টভাবে প্রতিটি কমান্ড workspace-এর working directory-তে চলে আর `cd`-এর কোনো স্থায়ী প্রভাব নেই। কল জুড়ে `cd` স্থায়ী করতে `persist_cwd=True` সেট করুন: প্রতিটি কমান্ড এমনভাবে মোড়ানো হয় যে এটি চলার পর, এর চূড়ান্ত working directory workspace-এর ভেতরে একটি ব্যক্তিগত ফাইলে লেখা হয়, আর সেই ডিরেক্টরি পরের কলে বহন হয়। path শুধু তখনই হালনাগাদ হয় যখন কমান্ড `0` দিয়ে বেরোয়। লেখা ডিরেক্টরি অদৃশ্য হলে, পরের কমান্ড একটি retry জানায় আর workspace-এর working directory-তে রিসেট হয়। রেকর্ডটি আলাদা পথে লেখা হয় (stdout-এ নয়), তাই কমান্ডের আউটপুট কখনো ট্র্যাক করা ডিরেক্টরি নকল করতে পারে না।

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Shell

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('.'), Shell(persist_cwd=True, allowed_commands=['cd', 'ls', 'pwd'])],
)
```

প্রতিটি রান একটি নতুন toolset instance পায়, তাই ট্র্যাক করা ডিরেক্টরি একসাথে চলা রানের মধ্যে বিচ্ছিন্ন আর সবসময় workspace-এর working directory থেকে আবার শুরু হয়।

`stop_command` পুরো process group-কে signal দেয়, wrapper বেরোনোর পর রয়ে যাওয়া সন্তানসহ, তারপর job-এর আউটপুট ফাইল সরায়। `setsid` ছাড়া একটি workspace-এ, যেখানে job নিজস্ব একটি process group পেতে পারে না, শুধু wrapper process signal পায়, যা কমান্ড বা এর সন্তানদের থামায় না।

Background কমান্ড আর `shell` টুল তাদের status আর আউটপুট ফাইলে রাখে, যার জন্য workspace-এর `PATH`-এ `mv` আর `base64` লাগে। এগুলো ছাড়া কল সাথে সাথে ব্যর্থ হয় আর অনুপস্থিত টুলের নাম দেয়।

মডেল কমান্ড আউটপুটের একটি সীমিত preview দেখে। বড় আউটপুটের জন্য, এটি workspace-এর একটি ফাইলে redirect করুন, তারপর পুরো ফাইল ছাপার বদলে সীমিত অংশ পরীক্ষা করতে `grep` বা `tail` ব্যবহার করুন।

## কনফিগারেশন { #configuration }

`Shell`-এর প্রতিটি ফিল্ড এর ডিফল্টসহ:

```python
from pydantic_ai_harness.shell import RUN_SCOPED_TOOL_NAMES, Shell

Shell(
    allowed_commands=[],           # allowlist (mutually exclusive with denied)
    denied_commands=[...],         # denylist (defaults to destructive commands)
    denied_operators=[],           # blocked shell operators
    default_timeout=30.0,          # seconds, per run_command
    max_output_chars=50_000,       # output cap returned to the model
    max_file_bytes=None,           # per-file size limit for commands (None = no limit)
    max_log_bytes=100_000_000,     # background and `shell` log size limit (None = no limit)
    persist_cwd=False,             # make cd sticky across calls
    allow_interactive=False,       # allow TTY-style commands
    env=None,                      # variables added to the workspace's environment
    denied_env_patterns=[],        # glob patterns dropped from env
    tools=RUN_SCOPED_TOOL_NAMES,   # which tools to register ('shell' for persistent commands)
)
```

`tools=['shell']`-সহ, `default_timeout` foreground অপেক্ষাও আর শূন্যের বেশি এবং সর্বোচ্চ 270 সেকেন্ড হতে হবে; তৈরির সময় এটি যাচাই হয়।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`Shell` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে, তাই আপনি Python-এর বদলে একটি config ফাইলে এটি ঘোষণা করতে পারেন:

```yaml
# agent.yaml
model: anthropic:claude-opus-5-5
capabilities:
  - Shell:
      allowed_commands: ['ls', 'cat', 'rg', 'pytest']
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Shell

agent = Agent.from_file('agent.yaml', custom_capability_types=[Shell])
```

`custom_capability_types` দিন, যাতে spec loader জানে `Shell` কীভাবে তৈরি করতে হয়, আর রানে একটি workspace যুক্ত করুন (রান মেথডে `workspace=`, বা Python-এ একটি workspace capability)।

## Durable execution { #durable-execution }

`Shell` Temporal, DBOS আর Prefect-এর অধীনে কাজ করে, background job আর `persist_cwd`-সহ; [workspace guide](../workspace.md#durable-execution) দেখায় প্রতিটি engine-এ কী কাজ করে। Temporal-এ একটি কমান্ড এর activity-র timeout-এর মধ্যে চলে, `run_command` আর `shell`-এর জন্য 300 সেকেন্ড; এটি বাড়াতে দেখুন [command timeouts](../durable_execution/temporal.md#harness-command-timeouts)।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Toolsets](../toolsets.md)

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.Shell
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `Shell()` = `run_command` + background-এর জন্য `start_command`/`check_command`/`stop_command`; বা `tools=['shell']` দিয়ে স্থায়ী `shell`।
* ডিফল্ট denylist `rm`, `dd`, `shutdown`... আটকায়; `allowed_commands` আর `denied_commands` একসাথে নয়।
* allowlist একটি guardrail, নিরাপত্তার সীমা নয় — `python -c` দিয়ে এড়ানো যায়; অবিশ্বস্ত কাজে sandbox।
* আউটপুট বড় হলে শেষ অংশ রাখা হয়; ফাইল আর log-এর আকার `max_file_bytes`/`max_log_bytes` দিয়ে সীমিত।
* `LocalWorkspace` শুধু `PATH`/`HOME`/locale দেয়; `Shell(env=...)` + `denied_env_patterns` দিয়ে নিয়ন্ত্রণ।
* background কমান্ড রানের পরেও চলে — `stop_command` দিয়ে বন্ধ করুন।

///
