
# Dynamic Workflow { #dynamic-workflow }

/// note | এই পেজে যা শিখবেন

* sub-agent-দের মধ্যে সমন্বয়ই যখন আসল কাজ, তখন `DynamicWorkflow` কীভাবে সেটি একটি Python script-এ সরিয়ে নেয়।
* `SubAgents`-এর সাথে পার্থক্য, আর কখন কোনটি বাছবেন।
* মডেল script-এ কী লেখে, structured output, আর ফল কীভাবে ফেরে।
* budget: `max_agent_calls`, `sub_agent_usage_limits`, `resource_limits`।
* `WorkflowAgent`, `reveal()`, `defer_loading`, sandbox-এর সীমা, Temporal আর observability।

///

`DynamicWorkflow` সেই ক্ষেত্রের জন্য, যেখানে sub-agent-দের *মধ্যকার* সমন্বয়টাই আসল কাজ। ধরুন আপনার কয়েকজন বিশেষজ্ঞ আছে — একজন code review করে, একজন findings-এর সারাংশ বানায়, একজন চূড়ান্ত নোট লেখে। আলাদাভাবে প্রত্যেককে ডাকা সহজ; কঠিন অংশ হলো নৃত্য-পরিকল্পনা (choreography): একসাথে তিনটি ফাইল review করো, শুধু যে report-গুলো কিছু পেয়েছে সেগুলো রাখো, সেগুলোর সারাংশ করো, আর সারাংশটি লেখকের হাতে দাও। এই capability তখনই বেছে নিন, যখন সেই সমন্বয়ে fan-out, chaining, voting বা retry loop থাকে, যা আপনি একবারে একটি model turn করে চালাতে চান না — যেখানে প্রতিটি মধ্যবর্তী ফল orchestrator-এর context দিয়ে ফিরে আসে।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ধারণাটি { #the-idea }

sub-agent সমন্বয়ের প্রচলিত উপায় হলো প্রতি ধাপে একটি tool call। agent reviewer-কে ডাকে আর অপেক্ষা করে, ফল পড়ে, আবার reviewer-কে ডাকে, আবার অপেক্ষা করে — এভাবে চলতে থাকে। প্রতিটি মধ্যবর্তী ফল agent-এর context-এ ফিরে আসে, আর আগেরটির ওপর নির্ভরশীল প্রতিটি ধাপ একটি আলাদা model turn।

`DynamicWorkflow` ভিন্ন পথ নেয়। আপনি এটিকে নাম-দেওয়া sub-agent-দের একটি catalog দেন, আর এটি মডেলকে একটিমাত্র tool দেয়, `run_workflow`। ওই tool-এর ভেতরে মডেল সাধারণ Python লেখে: আপনার প্রতিটি sub-agent একটি `async` function, যেটি সে ডাকতে, loop চালাতে আর একসাথে মেলাতে পারে। script-টি একটি tool call-এ শেষ পর্যন্ত চলে, আর শুধু তার চূড়ান্ত মান মডেলের কাছে ফেরে। সমন্বয় কথোপকথন থেকে বেরিয়ে কোডে চলে যায়।

[Code Mode](code-mode.md) দেখে থাকলে এটি পরিচিত লাগবে — একই [Monty](https://github.com/pydantic/monty) sandbox আর একই ধারণা: অনেকগুলো tool call-এর বদলে একটি script লেখো। পার্থক্য হলো script কী ডাকতে পারে। Code Mode-এ এটি agent-এর নিজের tool ডাকে; এখানে এটি পুরো sub-agent ডাকে।

/// tip | উদাহরণ দিয়ে বুঝি

একজন ম্যানেজার যদি প্রতিটি কাজের পর ফোন করে জিজ্ঞেস করেন "এবার কী করব?", তাহলে প্রতিটি ফোনকল একটি model turn। `DynamicWorkflow` বরং ম্যানেজারকে একটি লিখিত কর্মপরিকল্পনা (script) লিখতে দেয়: "তিনজন একসাথে ফাইল দেখো, যারা সমস্যা পেয়েছ শুধু তাদের রিপোর্ট সারাংশকারীকে দাও, তারপর লেখককে দাও।" দল পুরো পরিকল্পনা নিজেরাই চালায়, আর ম্যানেজার শুধু চূড়ান্ত ফলটি পান।

///

## Subagents-এর সাথে সম্পর্ক { #how-this-relates-to-subagents }

harness-এ দুটি delegation capability আছে। দুটির লেনদেন একই মুদ্রায় — নাম-দেওয়া, বিচ্ছিন্ন sub-agent run — তবে ভিন্ন উচ্চতায়:

- [`SubAgents`](subagents.md) একটি `delegate_task(agent_name, task)` tool দেয়। প্রতিটি delegation তার নিজের tool call আর নিজের model turn। delegation মাঝে মাঝে হলে, বা পরেরটির আগে প্রতিটি ফলের ওপর parent-এর বিচার লাগলে এটিই উপযুক্ত।
- `DynamicWorkflow` সমন্বয়টি একটি script-এ সরিয়ে নেয়। fan-out, chaining, voting আর retry loop সব একটি tool call-এর ভেতরে চলে, আর parent-এর কাছে পৌঁছায় শুধু script যা ফেরত দেয় বা print করে (সাথে ব্যর্থতা বা budget শেষ হলে সম্পন্ন ফলগুলোর সীমিত preview)।

নিশ্চিত না হলে `SubAgents` দিয়ে শুরু করুন। একটি `delegate_task` orchestrator sub-agent-দের নিজেদের না বদলেই একটি workflow catalog-এ রূপান্তরিত হয়।

/// info | এক নজরে: কোনটি কখন

| বিষয় | `SubAgents` | `DynamicWorkflow` |
|---|---|---|
| tool | `delegate_task` | `run_workflow` (Python script) |
| প্রতি delegation | একটি tool call, একটি model turn | একটি script-এ অনেকগুলো |
| মধ্যবর্তী ফল | parent-এর context-এ ফেরে | sandbox-এর ভেতরেই থাকে |
| উপযুক্ত যখন | মাঝে মাঝে delegation, প্রতি ধাপে বিচার লাগে | fan-out, chaining, voting, retry loop |

///

## ইনস্টলেশন { #installation }

script চলে Monty sandbox-এর ভেতরে, তাই extra-টি ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-harness[dynamic-workflow]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[dynamic-workflow]"
```

///


## আপনার প্রথম workflow { #your-first-workflow }

দুটি sub-agent, একটি orchestrator:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import DynamicWorkflow

reviewer = Agent('openai:gpt-6.1-sol', name='reviewer', description='Reviews code for bugs.')
summarizer = Agent('openai:gpt-6.1-sol', name='summarizer', description='Summarizes findings.')

orchestrator = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[DynamicWorkflow(agents=[reviewer, summarizer])],
)
```

`reviewer` আর `summarizer` সাধারণ agent — যে `Agent` আপনি আগে থেকেই চেনেন। এদের `name` হয়ে যায় script-এ মডেল যে function ডাকে তার নাম, তাই বৈধ Python identifier এমন নাম বাছুন। এদের `description` মডেলকে বলে প্রতিটি কীসের জন্য; একটি function-এর documentation যেভাবে লেখেন, সেভাবে লিখুন। `DynamicWorkflow(agents=[...])` এদের একটি capability-তে বেঁধে orchestrator-কে একটিমাত্র `run_workflow` tool দেয়।

## মডেল এটি দিয়ে কী করে { #what-the-model-does-with-it }

orchestrator tool-টি ব্যবহার করবে ঠিক করলে, সে আপনার sub-agent-দের একে একে ডাকে না। সে একটি script লেখে:

```python
import asyncio

reports = await asyncio.gather(
    reviewer(task="Review auth.py for bugs:\n<file contents>"),
    reviewer(task="Review parser.py for bugs:\n<file contents>"),
)
await summarizer(task="Summarize these review findings:\n" + "\n\n".join(reports))
```

যে অংশগুলো গুরুত্বপূর্ণ:

- প্রতিটি sub-agent একটি `async` function। এটি `await` দিয়ে ডাকা হয়।
- কাজটি দেওয়া হয় একটিমাত্র keyword argument, `task` দিয়ে। সবসময় keyword দিয়ে — `reviewer(task="...")`, `reviewer("...")` নয়।
- `asyncio.gather(...)` দুটি review একটির পর একটি না চালিয়ে একসাথে চালায়।
- শেষ expression-এর মানই মডেলের দেখা ফল হয়। মধ্যবর্তী `reports` list কখনো sandbox ছাড়ে না।

প্রতিটি call একটি পূর্ণ `Agent.run`, নিজস্ব model loop, message history, tool আর typed output-সহ। এর দুটি ফল: call-গুলো **বিচ্ছিন্ন** (একটি sub-agent আগের call-এর কিছুই মনে রাখে না, তাই যা লাগে সব `task`-এ দিন), আর call-গুলো **token খরচ করে আর সময় নেয়** (এই কারণেই এই capability আপনাকে budget দেয়, নিচে দেখুন)।

/// info | কোডটি সহজ ভাষায়

| লাইন | কী ঘটে |
|---|---|
| `asyncio.gather(reviewer(...), reviewer(...))` | দুটি ফাইল একসাথে review — দুটি আলাদা sub-agent run |
| `reports` | দুটি review-এর ফল, sandbox-এর ভেতরেই থাকে |
| `await summarizer(task=... + "\n\n".join(reports))` | সব report জুড়ে সারাংশকারীকে দেওয়া |
| শেষ লাইনের মান | শুধু এটিই orchestrator মডেলের কাছে ফেরে |

///

## sub-agent structured data ফেরত দিতে পারে { #sub-agents-can-return-structured-data }

একটি sub-agent তার `output_type` যা তৈরি করে তা-ই ফেরত দেয়। ডিফল্ট হলো string, তবে একটি sub-agent-কে Pydantic model দিলে script একটি `dict` পায়:

```python
from pydantic import BaseModel

class Score(BaseModel):
    value: int
    reason: str

critic = Agent('openai:gpt-6.1-sol', name='critic', description='Scores an answer 0-10.', output_type=Score)
```

script-এর ভেতরে মডেল field-গুলো subscript দিয়ে পড়ে, যেভাবে একটি JSON object পড়ত:

```python
result = await critic(task="Score this answer: ...")
result["value"]   # not result.value
```

মডেল যে catalog দেখে তা প্রতিটি output type-কে একটি `TypedDict` হিসেবে দেখায়, তাই সে field-গুলো জানে আর নিজে থেকেই subscript দিয়ে পড়ে।

একটি `output_type`-এ [`DeferredToolRequests`](../deferred-tools.md) থাকতে পারে, যাতে শীর্ষ-স্তরের caller tool approve করে run আবার চালু করতে পারে। workflow script এর কোনোটিই পারে না, তাই catalog sub-agent-এর return type থেকে `DeferredToolRequests` বাদ রাখে, আর যে sub-agent run এটি দিয়ে শেষ হয়, সেটি script-এ একটি `RuntimeError` raise করে — অন্য যেকোনো sub-agent ব্যর্থতার মতো।

## ফল কীভাবে ফেরে { #how-results-come-back }

script-এর শেষ expression-এর মান tool result হয় — মডেল এটি `print()` করে না।

| script... | মডেল পায় |
| --- | --- |
| একটি মানে শেষ, কোনো print নেই | সরাসরি ওই মান (`None` হলে `{}`) |
| print করে আর একটি মানে শেষ | `{"output": "<printed text>", "result": <value>}` |
| print করে আর `None`-এ শেষ | `{"output": "<printed text>"}` |

`print()` debug logging-এর জন্য; এটি string বানিয়ে ফেলে, তাই আসল ফল শেষ expression-কেই বহন করতে দিন।

## sub-agent-এর মডেল বাছাই { #choosing-sub-agent-models }

ডিফল্টভাবে প্রতিটি sub-agent সেই মডেল ব্যবহার করে, যা দিয়ে সেটি তৈরি হয়েছিল। host যখন parent agent-কে প্রতি-run model override দেয় (যেমন একটি `/model` command থেকে) আর প্রতিটি sub-agent dispatch সেই নির্ধারিত parent মডেল অনুসরণ করা উচিত, তখন `inherit_model=True` সেট করুন। কোনো sub-agent ইচ্ছাকৃতভাবে ভিন্ন মডেলে বাঁধা থাকলে এটি `False` রাখুন।

## নিরাপদ রাখা: budget { #keeping-it-safe-budgets }

একটি sub-agent অনির্ধারিত (non-deterministic), token খরচ করে, আর আরও sub-agent-এ ছড়িয়ে পড়তে পারে। `DynamicWorkflow` আপনাকে একটি কঠোর গণনা-ঊর্ধ্বসীমা, token budget, আর নিয়ন্ত্রণহীন sandbox script-এর বিরুদ্ধে একটি পাহারা দেয়।

### `max_agent_calls` -- একটি নির্ভুল গণনা { #max_agent_calls-an-exact-count }

```python
DynamicWorkflow(agents=[...], max_agent_calls=50)  # 50 is the default
```

একটি parent run-এ sub-agent run-এর সংখ্যার ওপর host-এর প্রয়োগ করা কঠোর ঊর্ধ্বসীমা। ওই run-এর প্রতিটি `run_workflow` call জুড়ে এটি একটি শেয়ার করা budget, আর script `asyncio.gather` দিয়ে ছড়িয়ে পড়লেও এটি হুবহু মানা হয়। budget ফুরিয়ে গেলে workflow sub-agent ডাকা বন্ধ করে আর একটি চূড়ান্ত ফল ফেরত দেয়, যাতে সর্বশেষ সম্পন্ন সর্বোচ্চ 20টি ফলের সীমিত preview থাকে। run-এর সংখ্যা নির্ভুলভাবে বাঁধে কেবল এই knob-টিই।

### `sub_agent_usage_limits` আর `forward_usage` -- খরচ সীমায় বাঁধা { #sub_agent_usage_limits-and-forward_usage-bounding-cost }

`sub_agent_usage_limits` হলো প্রতিটি sub-agent run-এ প্রয়োগ করা একটি `UsageLimits`। `forward_usage` নিয়ন্ত্রণ করে পুরো tree একটি usage counter শেয়ার করবে কি না:

| `forward_usage` | Counter | সীমার মানে |
| --- | --- | --- |
| `True` (ডিফল্ট) | parent-এর `usage` পুরো tree জুড়ে শেয়ার | tree-জোড়া সীমা। সমসাময়িক fan-out-এ এটি best-effort: কেউ গণনায় যোগ করার আগেই কয়েকটি sub-agent পরীক্ষা পার হয়ে যেতে পারে। |
| `False` | প্রতিটি sub-agent run নিজে গোনে | প্রতি-run সীমা। প্রতি-run `total_tokens_limit` `T` আর `max_agent_calls` `N` হলে tree মোটামুটি `N * T` token-এ সীমিত থাকে। |

/// warning | parent `run()`-এর usage limit এগিয়ে দেওয়া হয় না

parent `run()`-এ দেওয়া `usage_limits` sub-agent-দের মধ্যে এগিয়ে দেওয়া হয় না — এটি আবার পরীক্ষা হয় শুধু parent-এর নিজের request-এর সীমানায়। sub-agent-দের সীমায় বাঁধতে `sub_agent_usage_limits` সেট করুন; run-এর সংখ্যার নির্ভুল ঊর্ধ্বসীমার জন্য `max_agent_calls` ব্যবহার করুন।

///

### `resource_limits` -- script-কেই পাহারা দেওয়া { #resource_limits-guarding-the-script-itself }

এই সীমাগুলো orchestration script-এর নিজের memory পাহারা দেয়, এটি যে sub-agent-দের ডাকে তাদের নয়। ডিফল্ট রক্ষাকবচ (backstop) হলো 256 MB, কোনো সময়-সীমা ছাড়া। print করা output আলাদাভাবে সংগ্রহ হয়, Monty-র ডিফল্ট 10 MiB সীমায়।

```python
DynamicWorkflow(agents=[...], resource_limits={'max_duration_secs': 30})
```

`max_duration_secs` মাপে আপনার script sandbox code চালাতে কত সময় ব্যয় করে, ঘড়ির সময় (wall-clock) নয়। script যখন কোনো sub-agent-এর জন্য অপেক্ষা করে, তখন সেটি স্থগিত থাকে আর সেই সময় গোনা হয় না — তাই sub-agent যত সময়ই নিক, স্বাভাবিক workflow-তে এই সীমা কখনো চালু হবে না। এর একমাত্র কাজ বিশুদ্ধ-CPU-র নিয়ন্ত্রণহীনতা ধরা — এমন একটি `while True:` loop যা কখনো await করে না, যাকে কোনো sub-agent budget থামাতে পারে না কারণ সে কখনো sub-agent ডাকে না। সব sandbox resource limit সরাতে `'unlimited'` দিন; আলাদা 10 MiB print সীমা থেকেই যায়। একটি আংশিক dict রক্ষাকবচের ওপর মিশে যায়, তাই আপনি শুধু যে সীমাগুলোর নাম বলেন সেগুলোই বদলায়।

/// info | এক নজরে: তিন রকম budget

| knob | কী সীমায় বাঁধে | নির্ভুল? |
|---|---|---|
| `max_agent_calls` (ডিফল্ট 50) | sub-agent run-এর সংখ্যা | হ্যাঁ, `gather`-এর মধ্যেও |
| `sub_agent_usage_limits` + `forward_usage` | token/request খরচ | `True`-তে best-effort, `False`-তে প্রতি run |
| `resource_limits` | script-এর memory আর CPU সময় | sub-agent-এর অপেক্ষার সময় গোনে না |

///

### workflow নেস্ট হয় না { #workflows-do-not-nest }

একটি sub-agent নিজের workflow শুরু করতে পারে না: `DynamicWorkflow` capability-ওয়ালা কোনো sub-agent workflow-এর ভেতরে চলার সময় `run_workflow` পায় না। ব্যবহারিক নিয়ম: আপনার catalog-এর sub-agent-দের `DynamicWorkflow` capability দেবেন না। তারা সমন্বয়ের পাতা (leaf), orchestrator নয়।

## sub-agent-এর নাম বদলানো: `WorkflowAgent` { #renaming-a-sub-agent-workflowagent }

ডিফল্টভাবে একটি sub-agent তার নিজের `name` আর `description` দিয়ে দেখা দেয়। agent-টি নিজে না বদলে একটি workflow-এর জন্য ভিন্ন নাম বা বর্ণনা দিতে, এটিকে একটি `WorkflowAgent`-এ মুড়ে দিন:

```python
from pydantic_ai_harness.dynamic_workflow import WorkflowAgent

DynamicWorkflow(
    agents=[
        WorkflowAgent(
            reviewer,
            name='check',
            description='Checks one code change and returns actionable review findings.',
        ),
    ],
)
```

এখন মডেল ডাকে `check(task=...)`। শুধু agent দেওয়া মানে কোনো override ছাড়া এটিকে একটি `WorkflowAgent`-এ মোড়ানোর সংক্ষিপ্ত রূপ।

## run চলাকালীন sub-agent যোগ করা: `reveal()` { #adding-sub-agents-mid-run-reveal }

run শুরু হলে catalog স্থির হয়ে যায়, যা turn-এর পর turn এটিকে prompt-cache prefix-এ রাখে। run চলাকালীন একটি নতুন sub-agent উপলব্ধ করতে (যেমন একটি fixer agent প্রস্তুত হওয়ার পর), `DynamicWorkflow` instance-এর একটি reference রাখুন আর `reveal()` ডাকুন:

```python
workflow = DynamicWorkflow(agents=[reviewer])
orchestrator = Agent('openai:gpt-6.1-sol', deps_type=MyDeps, capabilities=[workflow])

# later, from the host or from another tool:
workflow.reveal(fixer)
```

প্রকাশিত sub-agent পরের ধাপ থেকে ডাকা যায়; মডেল এটির কথা জানতে পারে একটি ছোট system-স্তরের ঘোষণা-বার্তা থেকে, যাতে নতুন function-এর signature থাকে। `run_workflow`-এর বর্ণনা নিজে run শুরুর সময় উপস্থিত agent-দের অবস্থাতেই স্থির থাকে, তাই runtime-এর reveal কখনো prompt-cache prefix সরায় না। compaction বা একটি history processor ঘোষণাটি সরিয়ে দিলে, capability পরের ধাপে sub-agent-টির কথা আবার ঘোষণা করে। `reveal()` শুধু-যোগ-করা (append-only) আর সঙ্গে সঙ্গে যাচাই করে — নাম না থাকা, অবৈধ identifier, সংরক্ষিত keyword, বা নামের সংঘাত হলে call-এর জায়গাতেই `UserError` raise হয়।

## শুধু দরকার হলে লোড করা: `defer_loading` { #loading-it-only-when-needed-defer_loading }

`DynamicWorkflow` বেশ খানিকটা instruction text বহন করে, আর বেশিরভাগ turn-এ সেটি লাগে না। মডেল আসলে লোড না করা পর্যন্ত এটিকে এক-লাইনের একটি entry-তে গুটিয়ে রাখুন:

```python
DynamicWorkflow(
    agents=[reviewer, summarizer],
    id='workflow',
    defer_loading=True,
)
```

`defer_loading=True`-এর জন্য একটি স্থির `id` লাগে। পুরো চিত্রের জন্য দেখুন [on-demand capabilities](../capabilities/on-demand.md)।

## sandbox-এ কী চলে { #what-runs-in-the-sandbox }

script চলে Monty-তে, যা Python-এর একটি উপসেট। সীমানাগুলো জানা জরুরি:

- কোনো third-party library নেই।
- import করা যায় এমন standard-library module-এর মধ্যে আছে `sys`, `typing`, `asyncio`, `math`, `json`, `re`, `unicodedata`, `datetime`, `time` আর `random`। যা ব্যবহার করবেন তা import করুন। কোনো filesystem বা environment প্রবেশাধিকার নেই।
- কোনো ঘড়ি বা এলোমেলোতা নেই: `datetime.datetime.now()`, `datetime.date.today()`, `time.time()` আর
  seed ছাড়া `random` ব্যর্থ হয়। `time.sleep` আর `asyncio.sleep` সত্যিই অপেক্ষা করে; `max_duration_secs` সেট থাকলে,
  একটি script মোট সর্বোচ্চ ততক্ষণই ঘুমাতে পারে।
- `asyncio.gather(...)` positional awaitable দিয়ে sub-agent একসাথে চালায়, কিন্তু কোনো keyword
  argument নেয় না, `return_exceptions=True`-সহ। অন্য task তৈরি আর wait API উপলব্ধ নয়।

চালানোর আগে script-টি sub-agent signature-এর বিপরীতে স্থিরভাবে (statically) type-check করা হয়। একটি সাধারণ, স্থিরভাবে প্রমাণযোগ্য ভুল — যেমন ভুল বানানের function, positional `task`, বা ভুল-type-এর argument — একটি retry খরচ করে, কিন্তু কোনো sub-agent budget বা sandbox execution নয়। `Any` type-এর মান runtime validation পর্যন্ত পৌঁছাতে পারে; তবুও সেগুলো কোনো sub-agent চলার আগেই প্রত্যাখ্যাত হয়।

/// warning | ধরা-না-পড়া error পুরো script বাতিল করে

একটি sub-agent ব্যর্থতা `RuntimeError` হিসেবে দেখা দেয়। script এটি `try`/`except RuntimeError` দিয়ে ধরতে পারে; ধরা না পড়লে পুরো script বাতিল হয় আর মডেল আবার চেষ্টা করে। কিছু sub-agent ইতিমধ্যে শেষ হওয়ার পর script ব্যর্থ হলে, retry prompt-এ সর্বশেষ সম্পন্ন সর্বোচ্চ 20টি ফলের সীমিত preview থাকে। মডেল একই call-এর জন্য আবার খরচ না করে একটি অকর্তিত preview সাধারণ মান হিসেবে আবার ব্যবহার করতে পারে।

///

/// warning | সাধারণ ভুল

sub-agent-কে positional argument দিয়ে ডাকা (`reviewer("...")`), বা `asyncio.gather(..., return_exceptions=True)` লেখা — দুটোই sandbox-এ চলে না। প্রথমটি type-check-এই ধরা পড়ে (একটি retry খরচ), দ্বিতীয়টি keyword argument বলে অসমর্থিত। ব্যর্থতা সামলাতে বরং প্রতিটি call `try`/`except RuntimeError` দিয়ে মুড়ুন।

///

## Temporal workflow-এর ভেতরে চালানো { #running-inside-a-temporal-workflow }

orchestrator agent-এ `DynamicWorkflow`-এর পাশাপাশি `TemporalDurability` যুক্ত করুন, আর প্রতিটি
sub-agent-এও, যার model request activity হিসেবে চলা উচিত; তারপর প্রতিটি agent-কে তার নিজের
`AgentPlugin` দিয়ে রেজিস্টার করুন। script চলে workflow code-এ, [Code Mode-এর `run_code`](code-mode.md#temporal-durability)-এর মতো,
আর replay-এর সময় রেকর্ড করা sub-agent ফলের বিপরীতে আবার execute হয়।
Code Mode-এর বিপরীতে, আপনার সেট করা `max_duration_secs` workflow-এর ভেতরেও প্রযোজ্য থাকে, তাই যে script
এর কাছাকাছি সময় চলে, সেটি replay-তে ভিন্ন জায়গায় থেমে একটি `NondeterminismError` ঘটাতে পারে।

## Observability { #observability }

একটি workflow কী করেছে তা দেখার সবচেয়ে ভালো উপায় [Logfire](https://pydantic.dev/logfire) trace। প্রতিটি sub-agent run `run_workflow` span-এর নিচে নেস্টেড দেখা যায়, আর span-টি মডেলের লেখা হুবহু `code` argument বহন করে, তাই আপনি আসলে যে script চলেছে সেটি পড়তে পারেন। প্রথম-শ্রেণির অগ্রগতি streaming আসার আগ পর্যন্ত, একটি tool call-এর ভেতরের sub-agent run দেখতে প্রতিটি sub-agent `Agent`-এ `event_stream_handler` সেট করুন।

## API { #api }

```python
DynamicWorkflow(                  # all parameters are keyword-only
    agents=[...],                 # Sequence[AbstractAgent | WorkflowAgent], required
    tool_name='run_workflow',
    max_agent_calls=50,
    max_retries=3,
    forward_usage=True,
    inherit_model=False,          # True -> sub-agents run with the parent run's resolved model
    sub_agent_usage_limits=None,  # UsageLimits per sub-agent run; None -> pydantic-ai default
    resource_limits=None,         # None -> backstop (256 MB, no time cap);
                                  # 'unlimited' -> sandbox limits off; a dict merges onto the backstop
    id=None,                      # required when defer_loading=True
    description=None,             # one-line catalog entry shown while deferred
    defer_loading=False,
)

workflow.reveal(agent)            # AbstractAgent | WorkflowAgent; validates before appending

WorkflowAgent(
    agent,                        # AbstractAgent, required, positional
    name=None,                    # sandbox function name; falls back to agent.name
    description=None,             # function docstring; None falls back to agent.description, '' hides it
)
```

`DynamicWorkflowToolset` আর `WorkflowResourceLimits`-ও অ্যাডভান্সড ব্যবহারের জন্য module থেকে export করা আছে।

Source: [`pydantic_ai_harness/dynamic_workflow/`](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/dynamic_workflow/).

## আরও পড়ুন { #further-reading }

- [Code Mode](code-mode.md) -- একই sandbox, তবে sub-agent-এর বদলে agent-এর নিজের tool ডাকে।
- [Subagents](subagents.md) -- প্রতি tool call-এ একটি delegation-এর sub-agent, script-করা সমন্বয় ছাড়া।
- [Rewriting Bun in Rust](https://bun.com/blog/bun-in-rust) (Bun) -- একই pattern বড় পরিসরে, Claude Code-এর dynamic workflow দিয়ে।
- [Capabilities](../capabilities/overview.md) আর [on-demand capabilities](../capabilities/on-demand.md)।

/// check | সংক্ষেপে মনে রাখুন

* `DynamicWorkflow(agents=[...])` → একটি `run_workflow` tool, যেখানে মডেল Python script লেখে আর sub-agent-রা `async` function।
* ডাকুন `await name(task="...")` দিয়ে — সবসময় keyword; একসাথে চালাতে `asyncio.gather`।
* শুধু শেষ expression-এর মান মডেলের কাছে ফেরে; মধ্যবর্তী ফল sandbox-এই থাকে।
* প্রতিটি call বিচ্ছিন্ন — যা লাগে সব `task`-এ দিন।
* `max_agent_calls` (ডিফল্ট 50) নির্ভুল সীমা; খরচের জন্য `sub_agent_usage_limits`; CPU-loop-এর জন্য `resource_limits`।
* sub-agent-দের `DynamicWorkflow` দেবেন না — workflow নেস্ট হয় না।
* অনিশ্চিত হলে আগে `SubAgents` দিয়ে শুরু করুন।

///
