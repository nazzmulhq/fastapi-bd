
# Coder { #coder }

/// note | এই পেজে যা শিখবেন

* `Coder` দিয়ে একটি এজেন্টকে codebase অনুসন্ধান, সম্পাদনা আর টেস্ট করার টুল ও নির্দেশনা দেওয়া।
* কমান্ডের environment (কোন environment variable যায়), আর একটি workspace একাধিক রান বা এজেন্টে ভাগ করা।
* `Coder` ভেতরে কোন কোন capability দিয়ে গঠিত, এর সাতটি টুল, sub-agent আর দীর্ঘ-চলা কমান্ড।
* prompt caching, durable execution আর আগের version থেকে আপগ্রেড।

///

`Coder` একটি Pydantic AI এজেন্টকে একটি codebase অনুসন্ধান, সম্পাদনা আর টেস্ট করার টুল আর নির্দেশনা দেয়।
এটি রানের workspace-এ কাজ করে, এই মেশিনে বা একটি sandbox-এ। এটি [`FileSystem`](filesystem.md), [`Shell`](shell.md), [`RepoContext`](repo-context.md), [`SubAgents`](subagents.md) আর [context management](compaction.md) capability দিয়ে তৈরি একটি সাধারণ জোড়া capability, তাই আপনি পুরোটা ব্যবহার করতে বা খুলে আলাদা করতে পারেন।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ব্যবহার { #usage }

ripgrep (`rg`) অন্তর্ভুক্ত করতে Coder extra ইনস্টল করুন, যা `list_files` আর `grep` টুলের পেছনে কাজ করে:

/// tab | pip

```bash
pip install "pydantic-ai-harness[coder]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[coder]"
```

///


extra-টি `ripgrep==14.1.0` ইনস্টল করে, Android ছাড়া, যেখানে `rg` আলাদাভাবে `PATH`-এ দিতে হয়।
`rg` ছাড়া একটি workspace-এ, যেমন এটি নেই এমন একটি sandbox image, `list_files` আর `grep` এর বদলে একটি একক POSIX git/grep/find কমান্ড ব্যবহার করে।

দূরের workspace-এর জন্য, shell `cat` দিয়ে পুরো ফাইল পাঠানোর বদলে ফাইল টুল (`grep`, `list_files`, `read_file`) ব্যবহার করুন। দ্রুত সার্চের জন্য sandbox image-এ `rg` আর `git` ইনস্টল করুন (Coder extra এজেন্টের host-এ `rg` ইনস্টল করে, একটি দূরের image-এ নয়)। বড় বা তৈরি-করা tree-এর জন্য, Shell দিয়ে `rg -n 'pattern' path` বা `rg --files` চালান আর এর আউটপুট সীমিত করুন। `rg` ছাড়া, কমান্ড-সক্ষম POSIX workspace `grep` আর `list_files`-এর জন্য একটি sandbox-এর-ভেতরের git/grep/find কমান্ড ব্যবহার করে (একটি প্রাথমিক `rg` যাচাইয়ের পর)। শুধু-filesystem backend সীমিত ফাইল-হাঁটা ব্যবহার করে। POSIX বিকল্প git উপলব্ধ থাকলে repository-তে nested `.gitignore` আর search-root `.ignore` মানে; nested `.ignore` নিয়ম POSIX বিকল্প প্রয়োগ করে না, আর rg-নির্দিষ্ট regex সুবিধার জন্য `rg` লাগে। git ছাড়া, POSIX বিকল্প ignore ফাইল প্রয়োগ করতে পারে না। সার্চ আংশিক ফলকে সম্পূর্ণ হিসেবে উপস্থাপন না করে আউটপুট আর ফলের সীমা জানায়।
দরকার হলে `[coder,anthropic]`-এর মতো একটি provider extra যোগ করুন।
`Coder` রানের [workspace](../workspace.md)-এ কাজ করে। এখানে সেটি আপনার মেশিনের বর্তমান ডিরেক্টরি:

<!-- Keep this blown-out example in sync across docs/coder.md, docs/index.md, README.md, pydantic_ai_harness/coder/README.md, and examples/coding_agent.py. -->

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness.coder import Coder

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('.'), Coder()],
)
result = agent.run_sync('Find out why tests/test_parser.py fails and fix the bug it caught.')
print(result.output)
```

ফাইল path workspace-এর working directory থেকে মীমাংসা হয়, আর কমান্ড সেখান থেকে শুরু হয়। এর বদলে একটি বিচ্ছিন্ন cloud মেশিনে কাজ করতে, `LocalWorkspace`-কে একটি sandbox capability (Modal, E2B, Sprites বা Daytona) দিয়ে বদলান; বাকি কোড একই থাকে। কমান্ড কোনো allowlist ছাড়া চলে, আর ফাইল টুলের path-সীমা এগুলোতে প্রযোজ্য নয়।

যেমন [Modal](modal-sandbox.md) দিয়ে:

```python
from pydantic_ai_harness.modal_sandbox import ModalSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[ModalSandbox(), Coder()])
```

`LocalWorkspace`-এ, [`agent.to_cli_sync()`](../cli.md) আর [`agent.to_web()`](../web.md) একই ডিরেক্টরিতে কাজ করে। একটি sandbox-এ, CLI session-এর জন্য একটি sandbox রাখে, কিন্তু `to_web()` প্রতিটি বার্তার জন্য একটি নতুন শুরু করে, কারণ web protocol workspace ref বহন করে না, তাই web বার্তার মধ্যে ফাইল টিকে থাকতে হলে `LocalWorkspace` ব্যবহার করুন।

রপ্তানি করা `pydantic_ai_harness.coder:coder_agent` একই এজেন্ট, মডেল-হীন আর নাম `coder`, import-এর সময় যে ডিরেক্টরি বর্তমান তাতে কাজ করে।
Pydantic AI CLI দিয়ে এটি ব্যবহার করুন:

```bash
uvx --with "pydantic-ai-harness[coder]" clai -a pydantic_ai_harness.coder:coder_agent -m anthropic:claude-opus-5-5
```

### কমান্ডের environment { #the-command-environment }

একটি `LocalWorkspace`-এর কমান্ড আপনার `PATH`, `HOME`, `LANG`, `LC_ALL` আর `LC_CTYPE` পায়, তাই এরা আপনার টুল আর তাদের কনফিগারেশন খুঁজে পায় আর আপনার locale ব্যবহার করে, আর আপনার environment-এর আর কিছু নয়। `python`, `pytest` আর অন্য টুল ওই `PATH` দিয়ে মীমাংসা হয়, তাই আপনি `uv run` দিয়ে এজেন্ট শুরু করলে এগুলো এজেন্ট project-এর virtualenv থেকে আসে, অগত্যা workspace-এর থেকে নয়; কমান্ডগুলোকে workspace-এর নিজস্ব interpreter-এ নির্দেশ করতে `LocalWorkspace('.', env={'PATH': ...})` দিন। `env=` দিয়ে শুধু যা দরকার তা দিন:

```python
import os

from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness.coder import Coder

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('.', env={'GH_TOKEN': os.environ['GH_TOKEN']}), Coder()],
)
```

`os.environ` দেবেন না: তাতে মডেলের কমান্ড process-এর প্রতিটি secret পেয়ে যায়, LLM API key-সহ।

/// warning | সাধারণ ভুল

`LocalWorkspace('.', env=dict(os.environ))` — "সব কাজ করুক" ভেবে পুরো environment দিয়ে দেওয়া। এতে `OPENAI_API_KEY`, `AWS_SECRET_ACCESS_KEY`-এর মতো সব গোপন key মডেলের চালানো কমান্ডের নাগালে চলে যায়; একটি prompt injection দিয়েই সেগুলো `env | curl ...` দিয়ে বাইরে পাঠানো যায়। শুধু নির্দিষ্ট দরকারি variable দিন।

///

## একটি workspace ভাগ করা { #sharing-a-workspace }

একটি workspace একে ব্যবহার করা রানের চেয়ে বেশি দিন টেকে। একই ফাইলে কথোপকথন চালিয়ে যেতে, এর বার্তাগুলো দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness.coder import Coder

agent = Agent('anthropic:claude-opus-5-5', capabilities=[LocalWorkspace('.'), Coder()])
result = agent.run_sync('Add a --verbose flag to the CLI.')
result = agent.run_sync('Document the new flag in the README.', message_history=result.all_messages())
```

Message history একটি `LocalWorkspace`-কে অন্য ডিরেক্টরিতে সরাতে পারে না।

কাজটি অন্য একটি এজেন্টকে দিতে, বা একই ফাইলে একটি নতুন কথোপকথন শুরু করতে, workspace নিজেই দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.workspaces import ReadOnlyWorkspace
from pydantic_ai_harness.coder import Coder

coder = Agent('anthropic:claude-opus-5-5', capabilities=[LocalWorkspace('.'), Coder()])
reviewer = Agent('anthropic:claude-opus-5-5', capabilities=[Coder(instructions='Review the code for bugs.')])

result = coder.run_sync('Add a --verbose flag to the CLI.')
review = reviewer.run_sync('Review the new --verbose flag.', workspace=ReadOnlyWorkspace(result.workspace))
```

reviewer আপনার দেওয়া workspace-এ কাজ করে। [`ReadOnlyWorkspace`](../workspace.md#hand-the-workspace-to-another-agent) কমান্ড আর ফাইল পরিবর্তন প্রত্যাখ্যান করে, তাই reviewer পায় `read_file`, `list_files`, `grep` আর `delegate_task`, কিন্তু কোনো shell বা সম্পাদনা টুল নয়; একে কমান্ড চালাতে আর ফাইল সম্পাদনা করতে দিতে `result.workspace` নিজেই দিন। একটি sandbox-এ, এভাবেই কয়েকটি এজেন্ট একটি বিচ্ছিন্ন মেশিন ভাগ করে। [`SubAgents`](subagents.md)-এর বাড়তি কিছু লাগে না: প্রতিটি delegate parent-এর workspace-এ চলে।

## গঠন { #composition }

`Coder()` হলো এই capability-গুলো, এই ক্রমে:

1. ডিফল্ট instructions বহন করা একটি `Capability`, সাথে আপনার দেওয়া যেকোনো `instructions=`।
2. [`FileSystem`](filesystem.md)`(content_hashes=False, max_read_chars=50000, tools=FILE_TOOL_NAMES, max_retries=5)`, যেখানে
   `FILE_TOOL_NAMES` হলো `read_file`, `write_file`, `edit_file`, `list_files` আর `grep`। এর `root_dir` হলো workspace-এর working directory।
   প্রতিটি ফাইল টুল এজেন্টের ডিফল্ট একটির বদলে পরপর পাঁচটি retry অনুমতি দেয় (একটি প্রত্যাখ্যাত path বা একটি পুরনো সম্পাদনার জন্য),
   তাই একটি পুনরাবৃত্ত সংশোধনযোগ্য ভুল একটি দীর্ঘ রান শেষ করে দেয় না।
3. [`Shell`](shell.md)`(denied_commands=[], allow_interactive=True, default_timeout=270, tools=['shell'])`।
4. repository instructions আর কাঠামোর জন্য [`RepoContext`](repo-context.md)`(expose_inventory_tool=False)`।
   এজেন্ট আগে থেকেই নিজের `RepoContext` বাঁধলে এটি বাদ দিতে `repo_context=False` দিন, যাতে instruction ফাইল দুবার লোড না হয়।
5. [`SubAgents`](subagents.md)`(include_self=True, agent_folders=None)`, যাতে এজেন্ট একটি স্বয়ংসম্পূর্ণ উপ-কাজ নিজের একটি নতুন রানকে দিতে পারে (নিচে দেখুন)। এটি বাদ দিতে `sub_agents=False` দিন।
   ডিস্ক-সংজ্ঞায়িত এজেন্টও লোড করতে `agent_folders=` দিন (`SubAgents`-এর মতো একই মান); এর ডিফল্ট `None`।

তারপর ভেতরের ব্যবস্থা, যা এজেন্ট কখনো সরাসরি ডাকে না:

6. [`ClearToolResults`](compaction.md)`(max_fraction=0.7)`।
7. একটি ব্যক্তিগত [`ToolOutputLimits`](tool-output-limits.md) বিশেষায়ন, যা 64,000 অক্ষরের বেশি যেকোনো টুল ফল ছাঁটে, কোনো spill-retrieval টুল যোগ না করে। এর স্থিতিশীল ID, `coder_tool_output_limits`, durability capability-কে আলাদাভাবে কনফিগার করা একটি `ToolOutputLimits`-এর সাথে সংঘর্ষ ছাড়াই এর উত্তরাধিকারসূত্রে পাওয়া operation বাঁধতে দেয়।
8. [`RepairToolArguments`](repair-tool-arguments.md) সাধারণ যাচাইয়ের আগে ত্রুটিপূর্ণ JSON টুল আর্গুমেন্ট মেরামত করে (নিচে দেখুন)।
9. Prompt caching, [`Caching()`](../capabilities/caching.md)-এর মতোই, যদি না মডেল, এজেন্ট বা `Coder`-এর আগে তালিকাভুক্ত একটি capability ইতিমধ্যে `cache` সেট করে (নিচে দেখুন)। এটি বাদ দিতে `caching=False` দিন।

প্রতিটি টুল আসে `FileSystem`, `Shell` বা `SubAgents` থেকে; ওই পেজগুলো প্রতিটি পুরোপুরি নথিভুক্ত করে। যেকোনো সেটিং বদলাতে অংশগুলো থেকে একই এজেন্ট তৈরি করুন, যেমন content hash রাখতে, `list_directory` যোগ করতে, বা কমান্ড allowlist করতে।

## টুল { #tools }

| টুল | আচরণ |
| --- | --- |
| `read_file(path, offset=0, limit=None)` | শূন্য-ভিত্তিক লাইন offset, এক-ভিত্তিক দেখানো লাইন নম্বর, `limit` অন্য কিছু না বললে 2,000 লাইন, আর সম্পূর্ণ লাইনের সর্বোচ্চ 50,000 অক্ষর; ধারাবাহিকতার ইঙ্গিত ঠিক পরের offset-এর নাম দেয়, আর window-এর জন্য খুব লম্বা একটি লাইনের নাম দেওয়া হয় আর বাদ দেওয়া যায়। কোনো hash header নেই। |
| `write_file(path, content)` | একটি বিদ্যমান ডিরেক্টরিতে একটি ফাইল তৈরি, বা একটি বদলানো। কোনো `expected_hash` নেই। |
| `edit_file(path, old_text, new_text)` বা `edit_file(path, replacements=[...])` | হুবহু প্রতিস্থাপন, প্রতিটি একবার মেলে; একটি ব্যাচ মেমরিতে যাচাই হয় আর শুধু প্রতিটি প্রতিস্থাপন মিললেই লেখা হয়। |
| `list_files(path='.', glob=None)` | `rg --files`, path অনুযায়ী সাজানো, ignore ফাইল মেনে আর লুকানো ফাইল বাদ দিয়ে। |
| `grep(pattern, ...)` | `path`, `glob`, `file_type`, `ignore_case`, `literal` আর `context` (0 থেকে 20)-সহ ripgrep সার্চ। |
| `shell(command, mode='foreground', timeout=270)` | workspace-এ শুরু হওয়া অসীমাবদ্ধ কমান্ড, যা রানের পরেও টেকে। |
| `delegate_task(agent_name, task)` | একটি স্বয়ংসম্পূর্ণ উপ-কাজ `self`-কে দেওয়া, এই এজেন্টের একটি নতুন রান। `sub_agents=False` না হলে উপস্থিত। |

ফল সীমিত থাকে `FileSystem`-এর সীমা (ডিফল্টভাবে প্রতি `read_file`-এ 2,000 লাইন আর 50,000 অক্ষর, প্রতি সার্চ বা তালিকায় 1,000 লাইন বা ফাইল) আর Coder-এর 64,000-অক্ষরের টুল-আউটপুট সীমা দিয়ে; একটি ছাঁটাই-চিহ্ন মানে আরও আউটপুট বাদ পড়েছে, তাই এটি সম্পূর্ণ ধরে না নিয়ে সার্চ সরু করুন। একটি `read_file` window আউটপুট সীমার নিচে থাকে, তাই `offset` দিয়ে পাতা ওল্টানো কখনো লাইন বাদ দেয় না। `mkdir`, `find`, process পরীক্ষা আর `kill`-এর জন্য `shell` ব্যবহার করুন। ফাইল লেখা আলাদা filesystem-এর শুধু-পড়া path নিয়ম (`.git`, `.env`, key আর secret) মানে; shell এই নিয়ম এড়িয়ে যেতে পারে। Coder-এ পরিকল্পনা বা `run_command` পরিবার অন্তর্ভুক্ত নয়।

/// info | এক নজরে: সীমাগুলো

| কী | সীমা |
|----|------|
| `read_file` | 2,000 লাইন / 50,000 অক্ষর প্রতি কলে |
| `grep`, `list_files` | 1,000 লাইন বা ফাইল |
| যেকোনো টুল ফল | 64,000 অক্ষর (এর বেশি ছাঁটা হয়) |
| `shell` foreground অপেক্ষা | 270 সেকেন্ড, তারপর চলমান process-এর handle |
| ফাইল টুল retry | পরপর 5 বার |
| delegate-এর গভীরতা | 3 স্তর (শীর্ষ রানসহ) |

///

## Sub-agent { #sub-agents }

`sub_agents=True` (ডিফল্ট) হলে, `Coder` [`SubAgents`](subagents.md)`(include_self=True, agent_folders=None)` যোগ করে, যা এজেন্টকে `delegate_task` আর একটি delegate দেয়, `self`: `Coder` যে এজেন্টে বাঁধা তার একটি নতুন রান। delegate এই কথোপকথন ছাড়া শুরু হয়, তাই এজেন্ট এর দরকারি সবকিছু একে দেয়, আর এজেন্টের যা আছে এরও তা আছে -- একই মডেল, workspace, instructions আর capability, `Coder`-এর পাশে বাঁধা একটি অনুমোদন-দরজা, guardrail বা audit hook-সহ, তাই সেগুলো একটি delegate-এর চালানো কমান্ডও দেখে। একটি delegate পালাক্রমে কাজ দিতে পারে, শীর্ষ-স্তরের রানসহ তিন স্তর পর্যন্ত (`SubAgents.max_depth`)।

শুধু `Agent`-এ যা বাঁধা তা-ই একটি delegate-এ বহন হয়; `run()`-এ দেওয়া capability, toolset, instructions আর model settings হয় না। তাই `Coder`-কে `Agent(capabilities=[...])` দিয়ে বাঁধুন: `run()`-এ দিলে একটি `UserError` ওঠে, যদি না আপনি `sub_agents=False`-ও দেন। ডিস্কের এজেন্ট সংজ্ঞা শুধু `agent_folders=` দিয়ে লোড হয়। `delegate_task` বাদ দিতে `sub_agents=False` দিন, বা একটি ভিন্ন তালিকা, প্রতি-delegate বাজেট বা একটি মডেল মেনুর জন্য নিজে [`SubAgents`](subagents.md) গঠন করুন।

/// tip | উদাহরণ দিয়ে বুঝি

একজন সিনিয়র ডেভেলপার একটি বড় কাজে আছেন, আর মাঝে একটি পাশের প্রশ্ন আসে: "এই লাইব্রেরির সব ব্যবহার কোথায় কোথায়?" তিনি নিজের মনোযোগ নষ্ট না করে একজন সহকর্মীকে (নতুন রানের `self`) পুরো নির্দেশনাসহ কাজটা দেন, আর শুধু সারাংশটা ফেরত নেন। এতে মূল কথোপকথনের context অপ্রাসঙ্গিক খুঁটিনাটিতে ভরে যায় না।

///

## Filesystem-এর পরিসর { #filesystem-scope }

ডিফল্টভাবে ফাইল টুল workspace-এর working directory-তে সীমিত। বিশ্বস্ত লোকাল ব্যবহারের জন্য,
`Coder(unrestricted_filesystem=True)` সেট করে `FileSystem(root_dir='/',
read_only_patterns=[])`: আপেক্ষিক path তবুও working directory থেকে মীমাংসা হয়, আর রানের workspace-এর যেকোনো জায়গার absolute path গ্রহণ করা হয়, যেমন `/tmp/example.py`। OS অনুমতি আর file-change event listener তবুও প্রযোজ্য। এটি secret আর repository metadata বদলানোর অনুমতি দেয়: শুধু তখনই ব্যবহার করুন যখন আপনি এজেন্ট আর এর input বিশ্বাস করেন। Shell কমান্ড আগে থেকেই অসীমাবদ্ধ ছিল।

## দীর্ঘ-চলা কমান্ড { #long-running-commands }

`shell` হলো [`Shell`](shell.md) capability-র স্থায়ী টুল। Foreground সর্বোচ্চ 270 সেকেন্ড অপেক্ষা করে (বা একটি ছোট ধনাত্মক `timeout`) আর তারপর একই চলমান process-এর handle ফেরত দেয়; background সাথে সাথে সেগুলো ফেরত দেয়। দুটোই শেষ হয় একটি PID, একটি absolute আউটপুট log path, আর একটি absolute JSON status path দিয়ে (workspace-এর ভেতরে), যার `exit_code` কমান্ড চলার সময় `null`; foreground এগুলোর আগে আউটপুটের শেষ 16,000 bytes রাখে। কমান্ড এজেন্ট রানের পরেও টেকে, তাই সার্ভার চলতে থাকে; একটি চূড়ান্ত response-এর পর কোনো সমাপ্তি-বিজ্ঞপ্তি বা স্বয়ংক্রিয় জাগরণ নেই। Shell পেজ supervisor, পরিষ্কার-কাজ আর `CommandStartedEvent`, `CommandOutputEvent` ও `CommandFinishedEvent` অগ্রগতি event আলোচনা করে, যাতে একটি UI subscribe করতে পারে।

ডিফল্ট instructions এজেন্টকে একটি চূড়ান্ত response দেওয়ার আগে দরকারি কাজ শেষ করতে বলে: অন্য কাজের কাজ করুন, তারপর সমাপ্তি বা একটি সত্যিকারের বাধা না আসা পর্যন্ত status আর আউটপুট poll করুন।
শুরু আর প্রস্তুতি যাচাইয়ের পর সার্ভার চলতে থাকতে পারে। কমান্ড শুধু workspace-এর দেওয়া environment পায় (দেখুন [The command environment](#the-command-environment)); একটি লোকাল workspace-এ host-এর ফাইল কমান্ডের নাগালে থাকে।

## Instructions { #instructions }

ডিফল্ট instructions ইঞ্জিনিয়ারিং নির্দেশনা সংক্ষিপ্ত রাখে: স্বয়ংক্রিয় অনুসন্ধান আর সমাপ্তি, কেন্দ্রীভূত পরিবর্তন আর যাচাই, আর বাস্তবসম্মত DRY, YAGNI, SOLID আর Zen of Python।
এগুলো এজেন্টকে project-এ শুধু অনুরোধ করা পরিবর্তনটুকুই রাখতে বলে: নতুন ফাইলের বদলে inline shell script দিয়ে আচরণ যাচাই করা, শুধু যেখানে project-এ আগে থেকে আছে সেখানেই টেস্ট যোগ করা, আর শেষ করার আগে খসড়া ফাইল মুছে ফেলা।
টুলের বর্ণনা টুলের ব্যবহার জানায়; `RepoContext` repository instructions আর কাঠামো জানায়।
instructions workspace-এর working directory-কে project হিসেবে নাম দেয়, যেখানে shell কমান্ড শুরু হয় আর ফাইল টুল কাজ করে।
`Coder(instructions='...')` ডিফল্ট বদলে না দিয়ে project-নির্দিষ্ট নির্দেশনা যুক্ত করে।
বাড়তি নীতির জন্য এটি ব্যবহার করুন, যেমন ফাইল-আকারের সীমা বা একটি পছন্দের যাচাই workflow।

## টুল আর্গুমেন্ট মেরামত { #tool-argument-repair }

`Coder` [`RepairToolArguments`](repair-tool-arguments.md) জোড়ে, যা Pydantic AI টুল schema যাচাইয়ের আগে ত্রুটিপূর্ণ JSON-এর জন্য `json-repair` ব্যবহার করে।
বৈধ JSON আর ইতিমধ্যে-পার্স করা আর্গুমেন্ট অপরিবর্তিত চলে যায়। অনুপস্থিত ফিল্ড আর অবৈধ টাইপ তবুও সাধারণ যাচাই আর retry আচরণ মানে। মেরামত Coder-এর পাশে যোগ করা টুলেও প্রযোজ্য।
মেরামত parser একটি value বা recursion error তুললে, মূল আর্গুমেন্ট সাধারণ যাচাইয়ে যায়।

মেরামত অনুমানভিত্তিক: ত্রুটিপূর্ণ input অস্পষ্ট হতে পারে, আর অনুমিত string মডেলের উদ্দেশ্য থেকে ভিন্ন হতে পারে। এটি মেরামত লাইব্রেরিকে কোনো schema দেয় না বা হুবহু সম্পাদনা-মেলানো এড়িয়ে যায় না।
প্রতিটি চেষ্টা `ctx.tracer` দিয়ে একটি `repair_tool_arguments` span তৈরি করে, আর্গুমেন্ট বা ফাইলের কনটেন্ট ছাড়া। Coder-এর অন্য কাজ core টুল span আর এর `FileSystem` ও `Shell` capability-র তৈরি event-এর ওপর নির্ভর করে।

## Prompt caching { #prompt-caching }

`Coder` একীভূত `cache` মডেল সেটিং `True` সেট করে [prompt caching](../capabilities/caching.md) চালু করে। একটি coding রান প্রতিটি রিকোয়েস্টে একই টুল সংজ্ঞা আর instructions পাঠায়, সাথে একটি কথোপকথন যা শুধু বাড়ে, তাই প্রতিটি রিকোয়েস্ট আগেরটির লেখা prefix পড়ে নিতে পারে। দেখুন [প্রতিটি provider-এ `cache=True` কী করে](../capabilities/caching.md#unified-caching-settings) আর [caching-এর খরচ কত](../capabilities/caching.md#cost)।

মডেলে, এজেন্টের `model_settings`-এ বা `Coder`-এর আগে তালিকাভুক্ত একটি capability-তে সেট করা একটি `cache` মান এই ডিফল্ট বদলে দেয়, আর তেমনি দেয় এর পরে তালিকাভুক্ত একটি capability আর রানের নিজস্ব `model_settings`। prompt cache এক ঘণ্টা রাখতে, বা একটি এজেন্টের জন্য বন্ধ করতে:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness.coder import Coder

agent = Agent(
    'anthropic:claude-opus-5-5',
    model_settings={'cache': '1h'},  # or `False`
    capabilities=[LocalWorkspace('.'), Coder()],
)
```

`anthropic_cache`-এর মতো provider-নির্দিষ্ট cache সেটিং স্বাভাবিকভাবে `cache`-এর ওপর অগ্রাধিকার পায়।
`Coder(caching=False)` ডিফল্ট বাদ দেয়।

## Durable execution { #durable-execution }

`Coder` Temporal, DBOS আর Prefect-এর অধীনে কাজ করে: workspace আর durability capability-র পাশে এটি যুক্ত করুন, যেমন [workspace guide](../workspace.md#durable-execution) প্রতিটি engine-এ কী কাজ করে তাসহ দেখায়। Temporal-এ, `delegate_task` শুধু `self`-কে কাজ দেয়; দেখুন [delegation on Temporal](../durable_execution/temporal.md#harness-workspace-capabilities)।

## আপগ্রেড { #upgrading }

`Coder` এখন prompt caching চালু করে; পুরনো আচরণ রাখতে `caching=False` দিন বা নিজে `cache` সেট করুন (দেখুন [Prompt caching](#prompt-caching))।

এই release workspace-কে একমাত্র জায়গা বানায় যা ঠিক করে একটি এজেন্ট কোথায় কাজ করে। সরানো আর্গুমেন্ট এখনও গ্রহণ করা হয়, সমাধানের নামসহ একটি `HarnessDeprecationWarning` দেয়, আর উপেক্ষিত হয়।

- **একটি workspace যুক্ত করুন।** একটি ছাড়া `Coder`, `FileSystem`, `Shell`, `RepoContext` আর `Macroscope` রানের শুরুতে ব্যর্থ হয়, তেমনি `Skills`, `PydanticAIDocs` (একটি লোকাল checkout-সহ) আর `ToolOutputLimits` (যখন এটি ঢালতে পারে), যদি না নিজস্ব `workspace=` বা store দেওয়া থাকে। এজেন্টের capability-তে `LocalWorkspace('.')` যোগ করুন, যেমন [Usage](#usage)-এ।
- **ডিরেক্টরি workspace-এ সেট করুন।** `Coder('dir')`, `Shell(cwd=)`, `FileSystem(cwd=)`, `Macroscope(cwd=)` আর `RepoContext(workspace_dir=)` উপেক্ষিত হয়; `LocalWorkspace('./dir')` ব্যবহার করুন।
- **কমান্ডের environment দিন।** কমান্ড আগে আপনার পুরো environment উত্তরাধিকারসূত্রে পেত (`Coder` এটি থেকে LLM API key সরাত)। এখন এরা পায় শুধু আপনার `PATH`, `HOME`, `LANG`, `LC_ALL` আর `LC_CTYPE`, সাথে workspace-এর `env` আর `Shell(env=)`। এদের যা দরকার, যেমন একটি SSH agent socket, একটি `gh` token বা proxy সেটিং, `LocalWorkspace('.', env={...})` দিয়ে দিন (দেখুন [The command environment](#the-command-environment))।
- **`denied_env_patterns` `LocalWorkspace(env=)` ছাঁকে না।** এটি শুধু `Shell(env=)` থেকে নাম বাদ দেয়, তাই workspace-কে পুরো `os.environ` দেবেন না।
- **`FileSystem(root_dir=)`** ডিফল্টভাবে working directory আর আপেক্ষিক মান এটি থেকে মীমাংসা করে। এতে working directory থাকতে হবে, এর বাইরে নিয়ে যাওয়া symlink প্রত্যাখ্যাত হয়, আর `root_dir='/'` যাচাই বন্ধ করে।
- **Harness ফাইল working directory-তে সরেছে।** টুল-আউটপুট ঢালা আর Shell background-job ফাইল `$TMPDIR`-এর বদলে `.pydantic-ai-harness/`-এর নিচে (git-উপেক্ষিত)। `.pydantic-ai-harness/tool-output/`-এর ঢালা কখনো ছাঁটা হয় না; আর দরকার না হলে ডিরেক্টরিটি মুছে দিন। `ToolOutputLimits(store=LocalFileStore())` workspace ছাড়াই এই মেশিনের একটি temp ডিরেক্টরিতে ঢালা রাখে।
- **Background কমান্ড রানের পরেও টেকে।** রান শেষ হলে `start_command` job আর মারা হয় না, তাই কথোপকথনের পরের একটি রান এগুলো যাচাই করতে পারে; `stop_command` বা নিজের পরিষ্কার-কাজ দিয়ে এগুলো থামান।
- **লোকাল ফাইল আর shell টুলের একটি POSIX host লাগে।** `LocalWorkspace` Windows-এ চলে না; সেখানে একটি sandbox capability ব্যবহার করুন, বা WSL।
- **Skills** রানের শুরুতে workspace থেকে পড়া হয় আর deferred capability হিসেবে লোড হয়। [`Skills(workspace=LocalWorkspaceBackend('/app'))`](skills.md) অন্য কোথাও থেকে এগুলো পড়ে।
- **[`Researcher`](researcher.md)** বড় আকারের টুল ফল `$TMPDIR`-এর বদলে workspace-এ ঢালে, তাই এরও একটি লাগে। একটি শুধু-ওয়েব এজেন্ট `Researcher(store=LocalFileStore())` দিয়ে পুরনো আচরণ রাখতে পারে।
- **Sub-agent সংজ্ঞা** রানের শুরুতে workspace থেকে পড়া হয়, আর `~/.agents/agents/` আর পড়া হয় না। [`SubAgents(workspace=LocalWorkspaceBackend('/app'))`](subagents.md) অন্য কোথাও থেকে এগুলো পড়ে।
- **[Memory-র `FileStore`](memory.md)** এর ফাইল workspace-এ রাখে, আর `.memory-operations.json`-এর রসিদ এর SQLite journal-এর জায়গা নেয়। `FileStore('.', workspace=LocalWorkspaceBackend('/path'))` এগুলো এই মেশিনে রাখে।
- **Capability Creation** শুধু তখনই চলে যখন workspace একটি লেখা-যোগ্য `LocalWorkspace`।
- **চলমান durable রান।** একটি workspace যোগ করা একটি durable রান এর শুরুতে কী লেখে তা বদলায়, তাই পরিবর্তনের আগে শুরু হওয়া Temporal আর DBOS রান আর replay হয় না। এগুলো শেষ হতে দিন বা আগে deployment version করুন; দেখুন workspace guide-এর [Durable execution](../workspace.md#durable-execution) অংশ।

`aclose()` প্রকাশ করা একটি provider backend-সহ একটি রানের পর `result.workspace` ধরে রাখলে, এটি ব্যবহার শেষ করে এর client session ছাড়তে `await result.workspace.backend.aclose()` ডাকুন। এটি client বন্ধ করে, অগত্যা sandbox নয়; নিজের মালিকানাধীন sandbox-এর জন্য সেই provider-এর মোছার API অনুসরণ করুন।

Sandbox ref বিদ্যমান environment চিহ্নিত করে; provider-নির্দিষ্ট পরিষ্কার-কাজে আপনার অ্যাপ্লিকেশনের মালিকানাধীন ref-এর জন্য একটি শুধু-ID মোছার API ব্যবহার করা উচিত (যেখানে সেই provider একটি দেয়)। শুধু একটি sandbox মুছতে একটি backend তৈরি বা যুক্ত করবেন না। ডিরেক্টরি আপলোড আর preview URL provider SDK-এর ওপর নির্ভর করে।

`ModalSandbox(working_dir='/workspace')`-এর মতো একটি দূরের sandbox-এ, `Coder` রানের শুরুতে repo instructions লোড করে, যা মডেলের প্রথম টুল কলের আগেই sandbox তৈরি করে। sandbox অলসভাবে তৈরি হওয়া উচিত হলে `Coder(repo_context=False)` ব্যবহার করুন; instructions তখন working directory-র নাম দেয় না। একটি নতুন sandbox আপনার জন্য এর `working_dir` তৈরি করে।

## Benchmarking { #benchmarking }

Harbor-এর ভেতরে Coder চালানো, adapter আর harness pin করা আর trial-এর ফল পরীক্ষার জন্য দেখুন [Terminal-Bench 2.1 playbook](https://github.com/pydantic/pydantic-ai/blob/main/src/pydantic_ai_harness/pydantic_ai_harness/coder/TERMINAL_BENCH.md)।

দেখুন [source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/coder/)।

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.coder.Coder
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `Agent(model, capabilities=[LocalWorkspace('.'), Coder()])` — একটি সম্পূর্ণ coding এজেন্ট; `pydantic-ai-harness[coder]` ইনস্টল করুন।
* সাতটি টুল: `read_file`, `write_file`, `edit_file`, `list_files`, `grep`, `shell`, `delegate_task`।
* `shell` অসীমাবদ্ধ আর রানের পরেও টেকে; অবিশ্বস্ত কাজে sandbox ব্যবহার করুন।
* কমান্ড শুধু `PATH`/`HOME`/locale পায়; দরকারি জিনিস `LocalWorkspace(env={...})` দিয়ে দিন, কখনো `os.environ` নয়।
* `Coder`-কে `Agent(capabilities=...)`-এ বাঁধুন, `run()`-এ নয়; prompt caching ডিফল্টভাবে চালু।
* একই ফাইলে চালিয়ে যেতে message history বা `result.workspace` দিন; reviewer-এর জন্য `ReadOnlyWorkspace`।

///
