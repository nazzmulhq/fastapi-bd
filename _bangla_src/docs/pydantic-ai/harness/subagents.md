
# Subagents { #subagents }

/// note | এই পেজে যা শিখবেন

* `SubAgents` দিয়ে একটি agent কীভাবে নাম-দেওয়া child agent-দের কাছে কাজ ভাগ করে দেয় (delegate)।
* একমাত্র tool `delegate_task`, আর deps, usage, tool ও capability কীভাবে child-এ যায় (বা যায় না)।
* `include_self=True` দিয়ে নিজের কাছেই কাজ পাঠানো, আর delegation-এর গভীরতা সীমা।
* প্রতি delegate-এর budget, timeout, model মেনু, ব্যর্থতা সামলানো আর event।
* ডিস্ক থেকে (`.md` / `.toml`) sub-agent লোড করা, আর background-এ চলা managed delegation session।

///

`SubAgents` একটি agent-কে স্বয়ংসম্পূর্ণ (self-contained) কাজ নাম-দেওয়া child agent-দের হাতে দিতে দেয়। এটি `SubAgent` entry-র একটি sequence নেয় আর একটিমাত্র `delegate_task(agent_name, task)` tool দেয়। প্রতিটি delegation বাছাই করা sub-agent-কে তার নিজের run-এ চালায় — নিজস্ব message history-সহ, তাই সে কখনো parent-এর কথোপকথন দেখে না — আর তার output parent-কে ফেরত দেয়।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/subagents/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

যে একটি agent সবকিছু করে, তার কাছে tool-এর বড় একটা সংগ্রহ আর লম্বা context জমে যায়। কাজটি বিশেষায়িত sub-agent-দের মধ্যে ভাগ করলে প্রতিটির context মনোযোগী থাকে; কিন্তু হাতে হাতে delegation জোড়া লাগাতে গেলে প্রতি agent-এর জন্য একটি tool লিখতে হয়, deps এগিয়ে দিতে হয়, usage limit সুতোর মতো গেঁথে নিতে হয়, আর মডেলকে বলে দিতে হয় সে কার কাছে কাজ দিতে পারে।

## সমাধান { #the-solution }

`SubAgents` `SubAgent` entry-র একটি sequence নেয় আর একটিমাত্র `delegate_task(agent_name, task)` tool দেয়। প্রতিটি delegation বাছাই করা sub-agent-কে তার নিজের run-এ চালায় — নিজস্ব message history-সহ, তাই সে কখনো parent-এর কথোপকথন দেখে না — আর তার output parent-কে ফেরত দেয়। উপলব্ধ sub-agent-দের তালিকা থাকে system prompt-এ, তাই তালিকাটি cache করা prefix-এর মধ্যেই থাকে; একই কথোপকথনের run-গুলোর মাঝে তালিকা বদলালে prefix নতুন করে না লিখে পরিবর্তনটি [শেষে জুড়ে দেওয়া হয়](../agent.md#appending-instruction-changes)।

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent, SubAgents

researcher = Agent('anthropic:claude-opus-5-5', name='researcher', description='Researches a topic and reports findings')
writer = Agent('anthropic:claude-opus-5-5', name='writer', description='Turns notes into polished prose')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agents=[SubAgent(researcher), SubAgent(writer)])],
)

result = orchestrator.run_sync('Research the history of TLS and write a one-paragraph summary.')
print(result.output)
```

একটি delegate-এর নাম — parent মডেল তাকে কী নামে ডাকে, আর prompt-এ কী নামে তালিকাভুক্ত — হলো agent-এর নিজের `name`, অথবা একটি `SubAgent(name=...)` override। দুটি delegate একই নামে দাঁড়ালে সেটি error, আর নাম বা override কোনোটিই নেই এমন agent প্রত্যাখ্যাত হয়।

/// tip | উদাহরণ দিয়ে বুঝি

একটি পত্রিকা অফিসের সম্পাদক (orchestrator) নিজে সব খবর খোঁজেন না। তিনি গবেষককে (researcher) বলেন "TLS-এর ইতিহাস খুঁজে আনো", তারপর লেখককে (writer) বলেন "এই নোট থেকে এক অনুচ্ছেদ লেখো"। প্রত্যেকে নিজের টেবিলে বসে কাজ করে — সম্পাদকের সব আলাপ তারা শোনে না, তাই নির্দেশটি (task) নিজেই পূর্ণাঙ্গ হতে হয়।

///

## Tool-টি { #the-tool }

| Tool | কাজ |
|---|---|
| `delegate_task(agent_name, task)` | নাম-দেওয়া sub-agent-কে একটি স্বয়ংসম্পূর্ণ কাজে চালায় আর তার output ফেরত দেয়। |

- sub-agent চলে নিজের message history নিয়ে, তাই `task` অবশ্যই স্বয়ংসম্পূর্ণ হতে হবে।
- অজানা `agent_name` দিলে `ModelRetry` raise হয়, যাতে মডেল নিজেকে শুধরে নিতে পারে।
- parent-কে ফেরত দেওয়া ফল হলো `str(result.output)`।
- `models` মেনু কনফিগার করা থাকলে tool-টি একটি বাড়তি `model` argument নেয় (নিচে দেখুন)।

/// warning | সাধারণ ভুল

মডেল প্রায়ই `task`-এ লেখে "ওপরে যে ফাইলটার কথা বললাম, সেটা ঠিক করো" — কিন্তু sub-agent parent-এর কথোপকথন দেখে না, তাই "ওপরে" বলতে সে কিছুই জানে না। agent-এর instructions-এ মনে করিয়ে দিন: task-এ ফাইলের নাম, লক্ষ্য আর প্রয়োজনীয় সব তথ্য নিজেই লিখে দিতে হবে।

///

## Deps, usage, tool আর capability { #deps-usage-tools-and-capabilities }

- **Deps এগিয়ে দেওয়া হয়।** parent run-এর `deps` প্রতিটি sub-agent-কে দেওয়া হয়, তাই sub-agent-রা parent-এর `AgentDepsT` শেয়ার করে (type signature এটি নিশ্চিত করে — প্রতিটি sub-agent একটি `AbstractAgent[AgentDepsT, Any]`)।
- delegate করা agent-রা parent-এর workspace-এ চলে, `ReadOnlyWorkspace`-এর মতো wrapper-সহ।
- **Usage ডিফল্টভাবে শেয়ার হয়।** parent-এর `usage` প্রতিটি sub-agent run-এ দেওয়া হয়, তাই token usage একসাথে যোগ হয় আর parent-এর `usage_limits` পুরো agent tree জুড়ে প্রযোজ্য হয়। প্রতিটি sub-agent run-কে নিজস্ব হিসাব দিতে `forward_usage=False` সেট করুন।
- **parent-এর tool হস্তান্তর হয় না।** sub-agent নিজের tool নিয়ে চলে। parent-এর সব tool আর capability আছে এমন agent-এর কাছে কাজ দিতে `include_self=True` ব্যবহার করুন (নিচে "নিজের কাছেই কাজ দেওয়া" দেখুন)।
- **Capability শেয়ার করা যায়।** `shared_capabilities` প্রতিটি sub-agent run-এ প্রয়োগ হয় — যেমন প্রতিটি `Agent` নতুন করে না বানিয়েই সব sub-agent-কে একটি সাধারণ guardrail, memory বা planning capability দিন।
- **Sub-agent-এর event stream করা যায়।** একটি `event_stream_handler` দিলে সেটি প্রতিটি sub-agent run-এ এগিয়ে দেওয়া হয়, তাই sub-agent-এর model-streaming আর tool event caller-এর কাছে পৌঁছায় (handler sub-agent-এর নিজের `RunContext` পায়)।

`inherit_tools=True` deprecated আর একটি `HarnessDeprecationWarning` দেয়। এটি parent agent-এর নিজের tool-গুলো (`tools=` বা `toolsets=` দিয়ে রেজিস্টার করা) প্রতিটি sub-agent run-এ যোগ করে, delegate tool বাদে — কিন্তু parent-এর capability-গুলোর দেওয়া tool নয়। বরং একটি নির্দিষ্ট sub-agent-এর যে tool লাগে সেটি সরাসরি তার `Agent`-এ বাঁধুন, agent-এর সাথে বাঁধা সবকিছুসহ নতুন run-এ কাজ দিতে `include_self=True` ব্যবহার করুন, অথবা ডিস্ক থেকে লোড করা agent-দের tool দিতে একটি `tool_resolver` ব্যবহার করুন।

/// info | এক নজরে: child-এ কী যায়

| জিনিস | ডিফল্ট আচরণ | বদলানোর উপায় |
|---|---|---|
| `deps` | এগিয়ে দেওয়া হয় | — (type-এ বাধ্যতামূলক) |
| workspace | parent-এরটাই (`ReadOnlyWorkspace`-এর মতো wrapper-সহ) | — |
| `usage` | শেয়ার, parent-এর limit পুরো tree-তে | `forward_usage=False` |
| parent-এর tool | যায় না | `include_self=True` বা `tool_resolver` |
| capability | যায় না | `shared_capabilities` |
| message history | যায় না | — (task স্বয়ংসম্পূর্ণ হতে হবে) |

///

## নিজের কাছেই কাজ দেওয়া { #delegating-to-the-agent-itself }

`include_self=True` দিলে তালিকায় চলমান agent নিজেও থাকে, `self` নামে। `self`-এর কাছে delegation ওই agent-এর (`RunContext.agent`) একটি নতুন run শুরু করে, parent run-এর মডেলে (বা parent যে `models` option বাছে তাতে), parent-এর কথোপকথন ছাড়াই। child একই `Agent` বলে, তার সাথে বাঁধা প্রতিটি capability, toolset আর instruction তার আছে, আর child run-এ সেগুলো আবার রেজিস্টার হয়: `SubAgents`-এর পাশে বাঁধা একটি guardrail, approval gate বা audit hook শুধু `delegate_task` call নয়, delegate যে tool call করে সেগুলোও দেখে। [`Coder`](coder.md) ডিফল্টভাবে এটিই ব্যবহার করে।

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgents

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(include_self=True)],
)
```

- **শুধু `Agent`-এর সাথে বাঁধা জিনিসই যায়।** parent-এর `run()`-এ দেওয়া capability, toolset, instruction আর model setting agent-এর অংশ নয়, তাই delegate সেগুলো পায় না। `SubAgents(include_self=True)` নিজেই `run()`-এ দিলে run শুরুর সময় `UserError` raise হয়, কারণ delegate তখন এটি ছাড়াই চালু হতো।
- **Delegation-এর গভীরতা সীমিত।** delegate-এর কাছেও `delegate_task` থাকে, তাই `max_depth` (ডিফল্ট `3`, শীর্ষ-স্তরের run-সহ গুনে) tree-কে সীমায় বাঁধে: শীর্ষ-স্তরের run কাজ দেয়, তার delegate-রা আরেকবার কাজ দেয়, আর সীমায় পৌঁছানো run `delegate_task` বা sub-agent তালিকা কোনোটিই পায় না। সীমাটি `SubAgents`-এর মাধ্যমে প্রতিটি delegation-এ প্রযোজ্য, স্পষ্ট তালিকাসহ।
- **Delegate সবকিছু উত্তরাধিকারে পায়, এমনকি যা একটি sub-task-এর সাথে মানানসই নয়।** agent-এর সাথে বাঁধা একটি `AskUser` capability delegation-এর ভেতর থেকেও ব্যবহারকারীকে প্রশ্ন করতে পারে, আর delegate ফেরত দেয় agent-এর নিজের `output_type`, `str()` দিয়ে রূপান্তর করে (যে delegate run [`DeferredToolRequests`](../deferred-tools.md)-এ শেষ হয়, সেটি বরং একটি steering message ফেরত দেয়, ব্যর্থতা সামলানোর অংশে যেমন বলা আছে)।
- deprecated `inherit_tools` `self`-এ প্রযোজ্য নয়, কারণ তার tool তো আগে থেকেই parent-এর। `self` নামটি সংরক্ষিত: ওই নামে একটি স্পষ্ট delegate error, আর ওই নামে ডিস্কের কোনো definition একটি warning-সহ বাদ পড়ে।
- **Temporal-এ শুধু `self`-এর কাছে কাজ দিন।** `agent_folders` থেকে পড়া sub-agent run-এর সময় একটি toolset যোগ করে, যা Temporal প্রত্যাখ্যান করে, তাই `SubAgents(include_self=True, agent_folders=None)` দিন; দেখুন [Temporal-এ delegation](../durable_execution/temporal.md#harness-workspace-capabilities)।

/// tip | উদাহরণ দিয়ে বুঝি

`include_self=True` মানে নিজের একটি "ক্লোন" বানিয়ে আলাদা ঘরে পাঠানো — ক্লোনের কাছে আপনার সব যন্ত্রপাতি (tool, capability, guardrail) আছে, কিন্তু আপনার মাথার স্মৃতি (কথোপকথন) নেই। `max_depth` নিশ্চিত করে যে ক্লোন আবার ক্লোন বানাতে বানাতে অসীম পর্যন্ত চলে না।

///

## প্রতি-delegate run নিয়ন্ত্রণ { #per-delegate-run-controls }

প্রতিটি `SubAgent` নিজের budget বহন করে, তাই এক delegate-এর নিয়ন্ত্রণ অন্যদের ছোঁয় না। কোনো নিয়ন্ত্রণ সেট না করা `SubAgent` চলে `SubAgents`-এর ডিফল্ট নিয়ে।

```python
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai_harness import SubAgent, SubAgents

reproducer = Agent('anthropic:claude-opus-5-5', instructions='Reproduce the reported bug from a minimal script.')
librarian = Agent('anthropic:claude-opus-5-5', instructions='Find relevant docs, issues, and prior art.')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        SubAgents(
            agents=[
                SubAgent(reproducer, usage_limits=UsageLimits(request_limit=35), timeout_seconds=600, max_calls=1),
                SubAgent(librarian, usage_limits=UsageLimits(request_limit=18), timeout_seconds=300, max_calls=2),
            ]
        )
    ],
)
```

| Field | প্রভাব |
|---|---|
| `models` | `SubAgents` model মেনুর কোন key-গুলোতে এই delegate চলতে পারবে, আর ডিফল্টভাবে কোনটিতে চলবে: তালিকার প্রথম key। নিচে "প্রতি-delegation মডেল বাছাই" দেখুন। |
| `usage_limits` | একটি delegation-এর request/token budget। child চলে নিজস্ব usage হিসাব নিয়ে, তাই budget শুধু ওই child-এর request আর token গোনে (parent-এর বা ভাইবোনদের নয়)। `forward_usage=True` থাকলে delegation-এর পরে child-এর usage parent-এর usage-এ যোগ হয়। budget-এ পৌঁছানো একটি নরম ফলাফল (নিচে দেখুন), run-থামানো `UsageLimitExceeded` নয়। |
| `timeout_seconds` | একটি delegation-এর ঘড়ি-সময়ের (wall-clock) budget। child এটি ছাড়িয়ে গেলে তার run বাতিল হয়, আর parent child-এর জন্য ঝুলে না থেকে একটি নরম steering message পায়। বাতিল হওয়া child-এর `event_stream_handler` (যদি থাকে) কোনো শেষ event ছাড়াই event পাওয়া বন্ধ করে। |
| `max_calls` | প্রতি parent run-এ এই sub-agent-এর কাছে সর্বোচ্চ কতবার কাজ দেওয়া যাবে। পৌঁছে গেলে পরের delegation child না চালিয়েই একটি নরম "budget শেষ" message ফেরত দেয়। গণনা একটি `Agent.run`-এর (একটি `run_id`) মধ্যে সীমিত আর সেটি শেষ হলে মুছে যায়, তাই প্রতিটি parent run আর নেস্টেড tree-র প্রতিটি স্তর আলাদাভাবে budget করে। |
| `on_failure` | এই delegate-এর যেকোনো নরম অবনতির ক্ষেত্রে parent-কে ফেরত দেওয়া একটি steering message, বিল্ট-ইন ডিফল্টের বদলে। এটি সেট করলে child-এর ব্যর্থতাও নরম হয়ে যায় (নিচে দেখুন)। |
| `contain_errors` | এই delegate-এ অপ্রত্যাশিত crash হলে সেটি ধরে parent run বাতিল না করে parent-কে একটি সীমাবদ্ধ `ModelRetry` হিসেবে ফেরত দেওয়া হবে কি না (নিচে দেখুন)। সেট না করলে `SubAgents(contain_errors=...)`-এর ডিফল্ট (বন্ধ) নেয়। |

/// info | কোডটি সহজ ভাষায়

| delegate | request সীমা | সময় সীমা | সর্বোচ্চ কতবার |
|---|---|---|---|
| `reproducer` (bug পুনরুৎপাদন) | 35 request | 600 সেকেন্ড | প্রতি parent run-এ 1 বার |
| `librarian` (docs/issue খোঁজা) | 18 request | 300 সেকেন্ড | প্রতি parent run-এ 2 বার |

যেকোনো সীমা ছুঁলে parent-এর run থামে না — parent একটি বার্তা পায় আর নিজে ঠিক করে এরপর কী করবে।

///

## প্রতি-delegation মডেল বাছাই { #per-delegation-model-selection }

orchestrator যখন কাজের বিবরণ (brief) লেখে, তখনই সে জানে কাজটি কতটা কঠিন — তাই কোন মডেল সেটি চালাবে তা ঠিক করার সঠিক জায়গা সে-ই। একটি `models` মেনু কনফিগার করুন, তাহলে delegate tool একটি `model` argument পায়, যা মেনুর একটি key-র নাম বলে।

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai_harness import SubAgent, SubAgents
from pydantic_ai_harness.subagents import ModelOption

reviewer = Agent('anthropic:claude-opus-5-5', name='reviewer', description='Reviews a diff')
linter = Agent('anthropic:claude-opus-5-5', name='linter', description='Runs the linter and reports failures')

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        SubAgents(
            agents=[SubAgent(reviewer), SubAgent(linter, models=['fast'])],
            models={
                'fast': 'anthropic:claude-haiku-5-5',
                'standard': 'anthropic:claude-sonnet-5-5',
                'deep': ModelOption(
                    'anthropic:claude-opus-5-5',
                    description='hard reasoning, multi-file changes',
                    settings=ModelSettings(thinking='xhigh'),
                ),
            },
        )
    ],
)
```

- **ডিফল্টভাবে বন্ধ।** `models` মেনু না থাকলে `model` argument tool schema-তেই থাকে না, আর প্রতিটি delegation ঠিক আগের মতোই চলে।
- **key-গুলোই interface।** এগুলো system prompt-এ প্রতিটি entry-র মডেল আর বর্ণনাসহ তালিকাভুক্ত হয়, আর tool schema এগুলোকে একটি enum হিসেবে দেয় — তাই মডেল নতুন মডেলের নাম বানিয়ে না নিয়ে মেনু থেকেই বাছে। নাম রাখুন কাজের ভিত্তিতে (`'fast'`, `'deep'`), vendor-এর ভিত্তিতে নয়।
- **একটি entry হলো একটি মডেল বা একটি `ModelOption`।** `ModelOption(model, description=..., settings=...)` একটি routing ইঙ্গিত আর প্রতি-option `ModelSettings` যোগ করে, তাই একটি key-র মানে হতে পারে "একই মডেল, বেশি ভাবনা"। এই সেটিংগুলো sub-agent-এর নিজের `model_settings`-এর ওপর মিশে যায়, আর option যে অংশগুলো সেট করে না সেগুলো অক্ষত থাকে।
- **নির্ধারণের ক্রম।** parent যে key দিয়েছে; না দিলে delegate-এর প্রথম অনুমোদিত key (নিচে দেখুন); না থাকলে delegate-এর নিজের মডেল; নইলে parent run-এর মডেল।
- **একটি delegate-কে সীমিত করা যায়।** `SubAgent(linter, models=['fast'])` ওই delegate-কে `fast`-এ বেঁধে দেয়: parent কোনো `model` না দিলে তালিকার প্রথম key-তেই এটি চলে, আর অন্যগুলো `ModelRetry` দিয়ে প্রত্যাখ্যাত হয়। সীমাবদ্ধতাটি prompt-এর তালিকায় দেখানো হয় (`- linter: Runs the linter (models: fast)`)। মেনুতে নেই এমন key-তে সীমিত করলে তৈরির সময়েই `ValueError` হয়।
- **প্রত্যাখ্যাত key-র কোনো খরচ নেই।** অজানা বা অনুপলব্ধ key ফিরে আসে বৈধ option-গুলোর তালিকাসহ একটি `ModelRetry` হিসেবে, delegate-এর `max_calls` budget থেকে কাটার আগেই।

/// tip | উদাহরণ দিয়ে বুঝি

রেস্তোরাঁর মেনুতে "ছোট / মাঝারি / বড়" লেখা থাকে, রাঁধুনির নাম নয়। ঠিক তেমনি `'fast'`, `'standard'`, `'deep'` হলো মেনু — orchestrator সহজ lint কাজের জন্য `'fast'` (Haiku), কঠিন multi-file পরিবর্তনের জন্য `'deep'` (Opus, `thinking='xhigh'`) অর্ডার দেয়। কাল vendor বদলালেও key-র নাম একই থাকে, prompt বদলাতে হয় না।

///

## ব্যর্থতা সামলানো { #failure-handling }

একটি *নরম ফলাফল* (soft outcome) parent-কে একটি সাধারণ tool result হিসেবে steering message ফেরত দেয়, তাই তার মডেল বার্তাটি পড়ে ঠিক করে এরপর কী করবে (সঙ্গে সঙ্গে আবার কাজ না দিয়ে — যা একটি `ModelRetry` উৎসাহিত করে)। timeout, `usage_limits` budget-এ পৌঁছানো, আর `max_calls` budget শেষ হওয়া সবসময় নরম। `on_failure` সেট থাকলে, এই ফলাফলগুলোর জন্য বিল্ট-ইন ডিফল্টের বদলে এর বার্তাটি যায়।

যে sub-agent run `DeferredToolRequests`-এ শেষ হয় (তার `output_type`-এ এটি আছে আর কোনো tool-এর approval লেগেছে বা সেটি deferred হয়েছে), সেটিও একটি নরম ফলাফল। parent child-এর tool call approve করতে বা তার run আবার চালু করতে পারে না, আর একই কাজ আবার দিলে সম্ভবত একইভাবে থামবে — তাই marker-টি output হিসেবে না ফিরিয়ে delegation একটি steering message ফেরত দেয়, যাতে sub-agent-এর নাম আর কেন থেমেছে তা থাকে, অথবা `on_failure` সেট থাকলে তার বার্তা। যে sub-agent নিজের deferred call নিজেই মীমাংসা করে, যেমন [`HandleDeferredToolCalls`](../capabilities/handle-deferred-tool-calls.md) দিয়ে, সেটি কখনো এভাবে শেষ হয় না আর স্বাভাবিকভাবে output ফেরত দেয়।

যে sub-agent run একটি *নরম model error*-এ (`ModelRetry`, `UnexpectedModelBehavior`, যেমন সে নিজের retry শেষ করে ফেলেছে) ব্যর্থ হয়, সেটি ডিফল্টভাবে parent-এর জন্য একটি `ModelRetry`-তে রূপান্তরিত হয় — তাই parent-এর মডেল দেখে `Sub-agent '<name>' failed: ...` আর আবার কাজ দিয়ে সাড়া দিতে পারে। delegate tool-এর ডিফল্ট `tool_retries=2`, তাই পরপর ততবার delegate ব্যর্থ হলেই কেবল parent বাতিল হয়; যেকোনো সফল delegation-এর পর গণনা আবার শূন্য হয়। বেশি অনির্ভরযোগ্য sub-agent সহ্য করতে `tool_retries` বাড়ান, অথবা parent agent-এর ডিফল্ট tool retries নিতে `None` দিন। কোনো delegate-এর ব্যর্থতা বরং নরম করতে তার জন্য `on_failure` সেট করুন: তখন child-এর error একটি সাধারণ tool result হিসেবে `on_failure` বার্তা ফেরত দেয়।

কঠিন (hard) error ছড়িয়ে পড়ে পুরো run থামিয়ে দেয়। যে child-এর প্রতি-delegate `usage_limits` *নেই* (তাই সে parent-এর হিসাব শেয়ার করে), তার থেকে আসা `UsageLimitExceeded` মানে পুরো tree-র budget শেষ, আর এটি ছড়িয়ে পড়ে; child নিজের `usage_limits`-এ পৌঁছালে সেটি নরম, ওপরে যেমন বলা হলো।

একটি *অপ্রত্যাশিত crash* — child-এর raise করা অন্য যেকোনো exception, যেমন provider-এর `ModelAPIError`/`FallbackExceptionGroup` বা ভুল tool argument থেকে একটি সাধারণ `ValueError` — ডিফল্টভাবে ছড়িয়ে পড়ে parent run বাতিল করে। এটি ধরে বরং parent-কে একটি সীমাবদ্ধ `ModelRetry` হিসেবে ফেরত দিতে `contain_errors=True` সেট করুন (প্রতি delegate-এ, বা `SubAgents`-এর ডিফল্ট হিসেবে), যাতে একটি delegate-এর crash পুরো run মেরে ফেলতে না পারে। আটকে রাখা হলেও এটি জোরালোভাবে জানান দেয়: exception-টি retry বার্তায় থাকে (`Sub-agent '<name>' crashed: ...`), standard `logging` module দিয়ে log হয়, আর `tool_retries` তখনও পরপর crash-গুলোকে একটি বাতিলে সীমাবদ্ধ করে। এটি `on_failure` থেকে স্বতন্ত্র — আটকানো crash সবসময় জোরালো retry তোলে, কখনো নরম `on_failure` ফেরত নয়, তাই একটি আসল bug কখনো সাফল্য হিসেবে লুকিয়ে যায় না। cancellation, শেয়ার করা `UsageLimitExceeded`, pydantic-ai-এর control-flow সংকেত (`CallDeferred`, `ApprovalRequired`, `Skip*` সংকেতগুলো) আর `UserError` — `contain_errors` যা-ই হোক, এগুলো আটকানো হয় না। cancellation দুই রকমই: বাইরের cancellation (`asyncio.CancelledError`) যেমন আছে তেমন ছড়িয়ে পড়ে, আর child-এর নিজের first-party cancellation (child-এর ভেতরে `RunContext.cancel()`, যা `RunCancelled` raise করে) delegate tool-কে আটকানো-হীন রাখে, তারপর pydantic-ai সেটিকে একটি ব্যর্থ `delegate_task` return হিসেবে আলাদা করে, যাতে parent মডেল সাড়া দিতে পারে — এমন crash retry হিসেবে নয় যা আবার কাজ দিতে উৎসাহিত করে।

/// info | এক নজরে: কোন ব্যর্থতা কেমন আচরণ করে

| ঘটনা | ডিফল্ট | পরিবর্তন |
|---|---|---|
| timeout, নিজের `usage_limits`, `max_calls` শেষ | নরম: steering message | `on_failure` বার্তা বদলায় |
| `DeferredToolRequests`-এ শেষ | নরম: steering message | `on_failure` |
| নরম model error (`ModelRetry`, `UnexpectedModelBehavior`) | parent-এর জন্য `ModelRetry` (`tool_retries=2`) | `on_failure` দিলে নরম |
| শেয়ার করা `UsageLimitExceeded` | কঠিন: পুরো run থামে | — |
| অপ্রত্যাশিত crash | কঠিন: parent বাতিল | `contain_errors=True` → জোরালো `ModelRetry` |

///

## Event { #events }

`SubAgents` `sub_agents` namespace-এ typed capability event পাঠায়, যাতে একটি host delegate tool-এর argument আর result parse না করেই একটি delegation চলার সময় আর কীভাবে শেষ হলো তা দেখাতে পারে:

| Event | Dispatch | কখন | Payload |
|---|---|---|---|
| `DelegationStartEvent` | stream | একটি delegation সব পরীক্ষা পার হয়েছে আর child run শুরু হতে চলেছে | `agent_name`, `task`, `truncated`, `model` (মেনুর key, বা `None`), `inherits_tools` |
| `DelegationEndEvent` | stream | delegation-টি parent যা পায় তাতে স্থির হয়েছে | `agent_name`, `outcome`, `output`, `truncated`, `usage`, `duration_seconds` |

দুটিই notification। একটি delegation মানে একটি `delegate_task` call, তাই একটি start আর তার end একই `tool_call_id` শেয়ার করে, যা core প্রতিটি event-এ বসিয়ে দেয়; মডেল সমান্তরালে কাজ দিলে subscriber এভাবেই জোড়া মেলায়।

`outcome` ওপরের ব্যর্থতা সামলানো অনুসরণ করে: `ok` (child-এর output parent-এর কাছে ফেরত গেছে), `timeout`, `budget` (child-এর নিজের `usage_limits`), `failed` (একটি নরম model error, `on_failure` হিসেবে ফেরত বা `ModelRetry` হিসেবে raise, অথবা `DeferredToolRequests`-এ শেষ হওয়া child run, steering message হিসেবে ফেরত), বা `contained` (`contain_errors` যে crash ধরেছে)। `output` হলো প্রতিটি ক্ষেত্রে delegate tool parent-কে যা ফেরত দেয়: child-এর output, steering message, বা retry text। এটি পাঠানো হয় tool-এর ভেতর থেকে, কোনো `ToolGuardrail` result guard মডেলের জন্য সেই text যাচাই করার আগে; যাচাই-করা সংস্করণ লাগলে host core-এর `FunctionToolResultEvent`-এর `ToolReturnPart` পড়ে। child-এর আলাদা হিসাব থাকলে (`usage_limits` সেট, বা `forward_usage=False`) `usage` হলো child-এর নিজের `RunUsage`, আর parent-এর usage-এ জমা হলে `None`, কারণ সেখানে তার ভাগ আলাদা করা যায় না।

child চলার আগেই প্রত্যাখ্যাত delegation (অজানা sub-agent, মেনুর বাইরের model key, `max_calls` budget শেষ) কিছুই পাঠায় না; tool result কারণ জানায়। delegate tool থেকে ছড়িয়ে পড়া exception (শেয়ার করা usage limit, আটকানো-হীন crash, cancellation) end event ছাড়াই শেষ হয়। `Agent(toolsets=[...])`-এ সরাসরি রেজিস্টার করা একটি `SubAgentToolset`-এর কোনো মালিক capability নেই আর সেটি কিছুই পাঠায় না। যেকোনো capability event-এর মতোই, যে listener raise করে সে parent run বাতিল করে দেয়।

`task` আর `output` `MAX_EVENT_TEXT_CHARS` (4096)-এ কাটা হয়, সাথে একটি `truncated` flag, যাতে একটি বাগাড়ম্বরপূর্ণ delegation সংরক্ষিত বা এগিয়ে দেওয়া event stream ভাসিয়ে দিতে না পারে।

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import AbstractCapability, on_event
from pydantic_ai_harness.subagents import DelegationEndEvent, SubAgent, SubAgents


class ReportDelegations(AbstractCapability):
    @on_event(DelegationEndEvent)
    async def on_delegation_end(self, ctx, event: DelegationEndEvent) -> None:
        print(f'{event.agent_name}: {event.outcome} in {event.duration_seconds:.1f}s')


researcher = Agent('anthropic:claude-opus-5-5', name='researcher')
agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agents=[SubAgent(researcher)]), ReportDelegations()],
)
```

child run থেকে নেস্টেড model streaming event-এর বিষয় নয়; তার জন্য একটি `event_stream_handler` দিন।

`@on_event` কীভাবে কাজ করে, দেখুন [capability events](../capabilities/overview.md#capability-events)।

`SubAgents` নিজের কোনো OpenTelemetry span পাঠায় না: child run একটি core agent run, যার নিজের span parent-এর tool-call span-এর নিচে নেস্টেড থাকে, আর ওপরের event-গুলো সেই ফলাফল বহন করে যা একটি trace শুধু একটি exception বা tool result হিসেবে দেখাত।

## খুঁজে পাওয়া (Discovery) { #discovery }

sub-agent-দের তালিকা `get_instructions` দিয়ে system prompt-এ যায়, প্রতিটি agent-এর `description` (বা একটি `SubAgent(description=...)` override) ব্যবহার করে। বর্ণনা নেই এমন sub-agent শুধু নাম দিয়ে তালিকাভুক্ত হয়।

/// tip | পরামর্শ

parent মডেল কাকে কাজ দেবে তা বাছে মূলত এই `description` পড়ে। "Researches a topic and reports findings"-এর মতো স্পষ্ট, কাজ-ভিত্তিক বর্ণনা দিন — বর্ণনা ছাড়া শুধু নাম থাকলে মডেলকে অনুমান করতে হয়।

///

## ডিস্ক থেকে sub-agent লোড করা { #loading-sub-agents-from-disk }

কোনো `Agent` কোড না লিখেই একটি repo-র agent definition-গুলো delegate হয়ে উঠতে পারে। `agent_folders` সেট থাকলে, ওই folder-গুলোর নিচের প্রতিটি Claude-ধাঁচের `*.md` ফাইল আর Codex-ধাঁচের `*.toml` ফাইল sub-agent হিসেবে লোড হয়, স্পষ্টভাবে দেওয়া `agents`-এর পাশাপাশি। ফাইলগুলো পড়া হয় ফাইলনামের সাজানো ক্রমে।

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgents

orchestrator = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[SubAgents(agent_folders='agents')],  # loads .agents/agents/ from the run's workspace
)
```

definition-গুলো প্রতিটি run-এর শুরুতে run-এর [workspace](../workspace.md) থেকে পড়া হয়, তাই একটি sandbox-এর agent ফাইল খুঁজে পাওয়া যায় আর আপনার home directory থেকে কিছুই পড়া হয় না। অন্য কোথাও থেকে পড়তে — যেমন আপনার application-এর সাথে আসা definition — `workspace=LocalWorkspaceBackend('/app')` দিন।

`agent_folders` নিয়ন্ত্রণ করে কোন folder পড়া হবে:

- একটি folder-নামের `str` (`'agents'` হলো প্রচলিত বিন্যাস): workspace-এর working directory-র নিচে `.agents/<name>/`, `.claude/<name>/` আর `.codex/<name>/` থেকে, এই ক্রমে লোড করে — তাই যে workspace `.agents/` অন্য কিছুর (যেমন skill) জন্য ব্যবহার করে, সেটিও বাকিগুলো থেকে agent লোড করে। workspace ছাড়া run এগুলো বাদ দেয়।
- workspace path-এর একটি sequence, absolute বা working directory-র সাপেক্ষে, ঠিক ওই folder-গুলো থেকেই, ক্রমানুসারে লোড করে।
- `None`, ডিফল্ট, ডিস্ক থেকে লোড বন্ধ রাখে, শুধু স্পষ্টভাবে দেওয়া `agents` দেখায়।

আগের release-গুলো ডিফল্টভাবে প্রচলিত folder-গুলো লোড করত। সেভাবেই চালিয়ে যেতে `agent_folders='agents'` দিন।

এই release-এর আগ পর্যন্ত folder-গুলো পড়া হতো এই মেশিন থেকে, home folder `~/.agents/agents/`-সহ। এখন path sequence দেওয়া হলে workspace ছাড়া run শুরুতেই ব্যর্থ হয়। প্রচলিত বিন্যাসে খোঁজার সময় current বা home directory-র এমন কোনো folder বাদ পড়লে, যেখানে workspace পৌঁছায় না, একবার warning দেওয়া হয় — folder-টির নাম আর যে `workspace=` সেটি পড়বে তা জানিয়ে।

/// warning | সাধারণ ভুল

আপগ্রেডের পর হঠাৎ ডিস্কের agent-রা আর দেখা যাচ্ছে না? কারণ `agent_folders`-এর ডিফল্ট এখন `None`। পুরোনো আচরণ ফিরে পেতে `agent_folders='agents'` দিন — আর মনে রাখুন, এখন ফাইল পড়া হয় workspace থেকে, `~/.agents/` থেকে নয়।

///

### Definition ফরম্যাট { #definition-format }

একটি definition হলো ঐচ্ছিক frontmatter-সহ একটি Claude-ধাঁচের markdown ফাইল, অথবা একটি Codex-ধাঁচের TOML ফাইল। Markdown:

```markdown
---
name: researcher
description: Researches a topic and reports findings
tools: Read, Grep
---
You research topics. Report your findings, each with a source.
```

- `name` হলো delegate-এর নাম (parent তাকে কী নামে ডাকে আর কী নামে তালিকাভুক্ত)। না থাকলে ফাইলনামের stem ব্যবহার হয়।
- `description` prompt-এর তালিকা চালায়।
- markdown body হয়ে যায় agent-এর instructions।
- `tools` (বা `allowed-tools`) একটি কমা-বিভক্ত string বা একটি YAML block list। নিচে "Tool" দেখুন।
- `model` আর `color` উপেক্ষিত হয়: মডেল parent থেকে উত্তরাধিকারসূত্রে আসে (নিচে দেখুন), আর `color`-এর কোনো pyai সমতুল্য নেই।

frontmatter পড়ে একটি ছোট, dependency-মুক্ত parser, যা শুধু এই key-গুলোতে সীমিত (`pyyaml` harness-এর dependency নয়)। পূর্ণ YAML frontmatter সাপোর্টেড নয়।

একটি Codex-ধাঁচের স্বতন্ত্র TOML ফাইল:

```toml
name = "reviewer"
description = "Reviews code for bugs"
developer_instructions = "Inspect the code and report findings. Do not edit files."
tools = ["Read", "Grep"]
```

- `name`, `description` আর `developer_instructions` বাধ্যতামূলক, খালি-নয় এমন string।
- `tools` (বা `allowed-tools`) ঐচ্ছিক: string-এর একটি list বা একটি কমা-বিভক্ত string, তবে দুটি key একসাথে নয়।
- `model`, `effort`, `model_reasoning_effort` আর `color` একটি warning-সহ উপেক্ষিত হয়; মডেল আর effort-এর জন্য `agent_overrides` ব্যবহার করুন।
- অন্য যেকোনো key, sandbox বা permission সেটিংসহ, নীরবে বেশি ক্ষমতাসম্পন্ন tool দেওয়ার বদলে একটি warning-সহ ওই ফাইলটি বাদ দেয়। পুরোনো `[agents.<name>] config_file` বিন্যাস সাপোর্টেড নয়।
- TOML ফাইল parse হয় standard-library-র `tomllib` module দিয়ে।

definition ফাইলের কিছুই execute হয় না। ভুল গঠনের বা অবৈধ ফাইল একটি warning-সহ বাদ পড়ে, অন্যগুলোকে আটকায় না।

### মডেল আর effort { #models-and-effort }

ডিস্কের agent-রা ডিফল্টভাবে parent run-এর মডেল উত্তরাধিকারসূত্রে পায়। প্রতি agent-এ, caller `agent_overrides` দিয়ে — agent-এর নাম key ধরে — মডেল override করতে আর একটি thinking/effort level সেট করতে পারে:

```python
from pydantic_ai_harness import SubAgents
from pydantic_ai_harness.subagents import AgentOverride

SubAgents(
    agent_folders='agents',
    agent_overrides={'researcher': AgentOverride(model='anthropic:claude-opus-5-5', effort='high')},
)
```

`effort` সেট না থাকলে ডিস্কের agent কোনো thinking সেটিং যোগ করে না, তাই উত্তরাধিকারে পাওয়া মডেলের ডিফল্টই প্রযোজ্য। একটি স্পষ্ট মান, `False` বা `'minimal'`-সহ, Pydantic AI-এর `ModelSettings.thinking` দিয়ে অপরিবর্তিত অবস্থায় পাঠানো হয়।

`MINIMUM_EFFORT_FLOOR` আর `clamp_effort(level, floor=...)` সামঞ্জস্যের জন্য এখনও import করা যায়, তবে deprecated। `SubAgents` আর এগুলো ব্যবহার করে না। কোনো ডিস্ক agent-এর স্পষ্ট level লাগলে `AgentOverride(effort=...)` দিন, অথবা capability-র বাইরে একটি application-নির্দিষ্ট ন্যূনতম সীমা প্রয়োগ করুন।

### Tool { #tools }

`tool_resolver` ছাড়া ডিস্কের agent কোনো tool পায় না আর তার `tools` frontmatter উপেক্ষিত হয়। frontmatter-এর tool-নামগুলো toolset-এ map করতে একটি `tool_resolver` দিন: এটি প্রতিটি tool-নাম পায় (তাই `Bash(git:*)`-এর মতো entry মানতে পারে) আর যে toolset-গুলো সেটি দেয় সেগুলো ফেরত দেয়, অথবা অজানা নামের জন্য `None`, যা একটি warning-সহ বাদ পড়ে।

```python
from collections.abc import Sequence

from pydantic_ai.toolsets import AgentToolset
from pydantic_ai_harness import SubAgents

TOOLSETS: dict[str, Sequence[AgentToolset[object]]] = {}  # your tool name -> toolsets mapping


def resolve(tool_name: str) -> Sequence[AgentToolset[object]] | None:
    return TOOLSETS.get(tool_name)

SubAgents(agent_folders='agents', tool_resolver=resolve)
```

### অগ্রাধিকার { #precedence }

একই নাম একাধিক উৎসে থাকলে বেশি অগ্রাধিকারেরটি জেতে আর বাকিগুলো একটি warning-সহ বাদ পড়ে: সবার আগে স্পষ্টভাবে দেওয়া `agents`; প্রচলিত বিন্যাসে খোঁজার ক্ষেত্রে workspace-এর `.agents/` folder তার `.claude/` folder-এর আগে; আর স্পষ্ট path sequence-এর ক্ষেত্রে আগের folder পরেরগুলোর আগে। স্পষ্টভাবে দেওয়া `agents` তালিকার ভেতরে ডুপ্লিকেট নাম তবুও error।

/// info | এক নজরে: ডিস্কের agent

| বিষয় | `.md` (Claude-ধাঁচ) | `.toml` (Codex-ধাঁচ) |
|---|---|---|
| instructions | markdown body | `developer_instructions` |
| বাধ্যতামূলক | কিছুই নয় (`name` না থাকলে ফাইলনাম) | `name`, `description`, `developer_instructions` |
| `model` | উপেক্ষিত | warning-সহ উপেক্ষিত |
| tool | `tool_resolver` থাকলে তবেই | `tool_resolver` থাকলে তবেই |
| অজানা key | সাপোর্টেড key ছাড়া কিছু পড়ে না | পুরো ফাইল warning-সহ বাদ |

///

## কনফিগারেশন { #configuration }

```python
from pydantic_ai_harness import SubAgents

SubAgents(
    agents=(),             # Sequence[SubAgent[AgentDepsT]] -- each pairs an agent with its run controls
    models={},             # Mapping[str, Model | str | ModelOption] -- per-delegation model menu (off when empty)
    agent_folders=None,    # folder-name str ('agents' is conventional) | Sequence[str | Path] workspace paths | None
    agent_overrides={},    # Mapping[str, AgentOverride] -- per-disk-agent model/effort override
    tool_resolver=None,    # Callable[[str], Sequence[AgentToolset[object]] | None] -- disk-agent tool mapping
    forward_usage=True,    # share the parent's usage with sub-agent runs
    inherit_tools=False,   # deprecated: use include_self=True, or tool_resolver for disk agents
    shared_capabilities=(),# capabilities applied to every sub-agent run
    event_stream_handler=None,  # forwarded to each sub-agent run to stream its events
    tool_name='delegate_task',
    tool_retries=2,        # extra delegate-tool attempts after a sub-agent error before aborting (None inherits the agent default)
    contain_errors=False,  # default for SubAgent.contain_errors: contain an unexpected crash as a bounded retry
    workspace=None,        # WorkspaceBackend to read agent_folders from instead of the run's workspace
    include_self=False,    # also list the running agent itself as the delegate `self`
    max_depth=3,           # delegation levels, counting the top-level run
)
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import SubAgent

agent = Agent('anthropic:claude-opus-5-5')

SubAgent(
    agent,                 # AbstractAgent[AgentDepsT, Any] -- the child agent to run
    name=None,             # delegate name; defaults to the agent's own `name`
    description=None,      # prompt-listing description; defaults to the agent's own `description`
    models=None,           # Sequence[str] -- menu keys this delegate may run on; the first is its default
    usage_limits=None,     # per-delegation request/token budget (isolated accounting)
    timeout_seconds=None,  # per-delegation wall-clock budget
    max_calls=None,        # max delegations to this sub-agent per parent run
    on_failure=None,       # steering message for soft degradations of this delegate
    contain_errors=None,   # contain an unexpected crash as a bounded retry; None inherits the SubAgents default
)
```

`SubAgents` [agent spec](../agent-spec.md) দিয়ে serialize করা যায় না (এটি জীবন্ত `Agent` instance ধরে রাখে), তাই `get_serialization_name()` `None` ফেরত দেয়।

## নোট { #notes }

- sub-agent-দের নিজেদেরও `SubAgents` থাকতে পারে, ফলে একটি tree তৈরি হয়। প্রতিটি `SubAgents` run তার নিজের `max_depth`-এ পৌঁছালে delegation দেওয়া বন্ধ করে, তাই বেশি সীমার একটি delegate তার parent-এর চেয়ে গভীরে যেতে পারে। পুরো tree সীমায় বাঁধতে `usage` শেয়ার করুন (ডিফল্ট) আর শীর্ষ-স্তরের run-এ একটি `usage_limits` সেট করুন।
- মডেল সমান্তরালে যে delegation দেয়, সেগুলো স্বাধীন sub-agent run হিসেবে চলে।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Multi-agent applications](../multi-agent-applications.md)

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.subagents.SubAgents
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.subagents.SubAgent
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.subagents.ModelOption
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.subagents.AgentOverride
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.subagents.DelegationStartEvent
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.subagents.DelegationEndEvent
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

## Managed delegation session { #managed-delegation-sessions }

caller স্পষ্টভাবে `DelegationTasks` খুলে bind না করা পর্যন্ত `SubAgents` তার বিদ্যমান, শুধু-foreground আচরণ রাখে। এই owner delegate tool-এর schema-তে `background` আর `resume` যোগ করে, প্রতিটি child-কে একটি স্থির conversation ID দেয়, আর shutdown পর্যন্ত প্রতিটি worker-এর মালিক থাকে। মীমাংসিত background report core-এর queued-message API দিয়ে পৌঁছে দিতে parent run-এ `DelegationReports` ব্যবহার করুন। প্রতিটি report হলো একটি `UserPromptPart`-এ child-এর output, `<task_output task_id="..." agent_name="...">` data হিসেবে ফ্রেম করা; কাজ সফল না হলে `outcome="..."` যোগ হয় — একটি background tool-এর `<tool_result>`-এর মতো। output-টি একটি মডেলের লেখা, তাই এটি কখনো system-এর কণ্ঠে ঢোকে না, আর এর ভেতরের একটি closing tag ফ্রেম আগেভাগে শেষ করতে পারে না। ফ্রেমের আগে কিছুই থাকে না: launch-এর সময় parent যে গ্রহণের রসিদ পেয়েছিল, সেটিই বলে দিয়েছিল যে একটি report আসবে। output part চিনতে `is_task_report(part)` ব্যবহার করুন, যেমন ব্যবহারকারী যা টাইপ করেছে তার transcript থেকে এটি বাদ রাখতে। `BackgroundTools` completion-এর মতো, metadata কখনো মডেলের কাছে পাঠানো হয় না, কিন্তু Vercel AI আর AG-UI message রূপান্তর এটি বাদ দেয়: এগুলোর মধ্য দিয়ে ঘুরে আসা history report-টি সাধারণ user text হিসেবে ফেরত দেয়, আর `is_task_report` তখন আর মেলে না। `message_history`-তে দেওয়া history caller-এর নিজের হিসেবে বিশ্বস্ত ধরা হয়, এই metadata-সহ। অবিশ্বস্ত client থেকে history লোড করুন একটি UI adapter দিয়ে, যা কখনো message content-এ client metadata বসায় না; [#10943](https://github.com/pydantic/pydantic-ai/pull/10943) মার্জ হলে `sanitize_messages`-ও একটি নিরাপদ পথ হবে; ততদিন এটি `TextContent.metadata` রেখে দেয়। কোনো বাড়তি agent loop implement করা নেই। report-গুলোর ডিফল্ট `priority='when_idle'`, তাই সক্রিয় parent আগে নিজের বর্তমান কাজ শেষ করে। যে host একটি idle continuation শুরু করে, তার উচিত `DelegationReports(..., priority='asap')` আর `agent.run(None, ...)` ব্যবহার করা: তখন অপেক্ষমাণ report-গুলো প্রথম model request-এ ঢোকে, কোনো কৃত্রিম user prompt ছাড়াই। run-গুলোর মাঝে জাগিয়ে তোলার সময়সূচি host-এর দায়িত্ব।

```python
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai_harness.subagents import DelegationReports, DelegationTasks, SubAgents

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[SubAgents(include_self=True)])
tasks = DelegationTasks(directory=Path('.task-history'))

async def converse():
    async with tasks.opened():
        with tasks.bind():
            result = await agent.run(
                'Delegate an independent investigation in the background.',
                conversation_id='review',
                capabilities=[DelegationReports(tasks, conversation_id='review')],
            )
            print(result.output)
            # Keep this owner open across subsequent parent turns.
```

`opened()` বের হওয়ার সময় worker-গুলো খালি (drain) করে। workspace আর plugin resource ওই scope-এর বাইরে জীবিত রাখুন। run-এর মালিকানাধীন non-local workspace-এর জন্য বিচ্ছিন্ন (detached) execution প্রত্যাখ্যাত হয়; foreground delegation তবুও কাজ করে। `max_depth=4` মূল run-সহ গোনে আর তিন স্তর child অনুমোদন করে। স্পষ্টভাবে কনফিগার করা অ-ডিফল্ট `SubAgents.max_depth` তবুও অগ্রাধিকার পায়। সাধারণ `SubAgents` তার মূল depth ডিফল্টই রাখে।

`restore(task)` অন্য কোথাও তৈরি একটি শেষ হওয়া `DelegationTask` যোগ করে, যেমন অন্য agent-এর session থেকে import করা একটি, যাতে parent সেটিকে ID দিয়ে আবার চালু (resume) করতে পারে। এটি `opened()`-এর আগেও কাজ করে; owner খোলার সময় task-টি লোড করে। একই ID-র কোনো task যদি এর মধ্যে ভিন্ন `run_id`-এর অধীনে চলে থাকে, সেটি প্রতিস্থাপিত না হয়ে রাখা হয়, আর `restore` `False` ফেরত দেয়।

`background(task_id)` child আবার শুরু না করেই একটি foreground অপেক্ষাকারীকে মুক্ত করে। `await cancel(task_id)` ওই child আর তার বংশধরদের থামায় ও খালি করে। ব্যবহারকারী থামালে, application স্পষ্টভাবে `await allow_resume(task_id)` না ডাকা পর্যন্ত মডেল-অনুরোধ করা resume আটকে থাকে। `one_shot` নামগুলো কখনো resume হয় না। একটি resume একই child ID আর তার স্বাধীন history, একটি নতুন run ID, আর বর্তমান সরাসরি parent ব্যবহার করে। একটি child নিজের বংশধরদের জন্য অপেক্ষা করে আর তার চূড়ান্ত output স্থির হওয়ার আগে তাদের report গ্রহণ করে। report-গুলো যায় সরাসরি parent-এর কাছে; একটি idle parent অপেক্ষমাণ report পায় তার পরের স্পষ্টভাবে শুরু করা run-এ। enqueue পৌঁছানো স্বীকৃত হয় শুধু তখনই, যখন core `EnqueuedMessagesEvent` পাঠায়, আর স্বীকৃতিগুলো সংরক্ষিত হয়।

`steer(task_id, text)` একটি চলমান child-কে তার নিজের run-এর queue-তে `priority='asap'`-সহ একটি user message পাঠায়: child এটি তার পরের model request-এ পড়ে, আর যেটি শেষ হতে চলেছে সেটি এটি নিয়ে আরও চালিয়ে যায়। child না চললে এটি `False` ফেরত দেয়, যাতে application সেটিকে resume করার প্রস্তাব দিতে পারে। child-এর run শুরুর আগে পাঠানো বার্তা তার জন্য অপেক্ষা করে; child-এর চূড়ান্ত response স্থির হওয়ার মুহূর্তে পাঠানো বার্তা পড়ার জন্য খুব দেরিতে পৌঁছাতে পারে।

একজন observer পায় `DelegationTaskEvent`, task-এর পরিচয় আর একটি ঐচ্ছিক সম্পর্কিত child stream event-সহ। managed start/end event-গুলো `task_id` আর `parent_id` বহন করে। managed cancellation আর আটকানো-হীন exception চূড়ান্ত outcome তৈরি করে; unmanaged event আর exception ছড়িয়ে পড়া তাদের মূল চুক্তি বজায় রাখে। metadata আর চূড়ান্ত/বাধাপ্রাপ্ত history `directory`-এর নিচে atomically সংরক্ষিত হয়। `StepPersistence`-এর মাধ্যমে checkpoint করতে আর process-killed child-এর সর্বশেষ অবস্থান (frontier) পুনরুদ্ধার করতে `step_store` দিন। একটি বাধাপ্রাপ্ত record লোড করা কখনো তার tool execute করে না। স্পষ্ট resume-এর আগে সম্ভাব্য আংশিক প্রভাবগুলো পরীক্ষা করুন। একটি resume বাধার কারণে উত্তরহীন থেকে যাওয়া tool call-গুলো একটি `interrupted` tool return দিয়ে বন্ধ করে, তাই child দেখে যে সেগুলো সম্পূর্ণ হয়নি।

`forward_usage=True`-সহ managed child-রা জীবন্ত usage হিসাব শেয়ার করে আর parent-এর ঊর্ধ্বসীমা উত্তরাধিকারে পায়। প্রতি-child budget launch-এর সময় একটি absolute ঊর্ধ্বসীমায় রূপান্তরিত হয়; সমসাময়িক ভাইবোনদের খরচ সেই সীমায় আগেভাগে পৌঁছাতে পারে, কিন্তু parent-এর budget এড়াতে পারে না। সাধারণ unmanaged প্রতি-child হিসাবের চুক্তি অপরিবর্তিত।

`agents`, `aliases` আর `instructions` তালিকা আর নির্দেশনা বাড়ায় শুধু bind করা scope-এর ভেতরে; `SubAgents` ছাড়া কোনো agent-এ এগুলো delegation যোগ করে না। `SubAgent(read_only=True)` child-এর workspace-কে `ReadOnlyWorkspace`-এ মুড়ে দেয়। ওই agent-কে শুধু বিশ্বস্ত শুধু-পড়ার capability-ও দিন: ইচ্ছেমতো Python tool workspace API এড়িয়ে যেতে পারে। CLAI-এর Explore আর Plan বিশেষজ্ঞরা filesystem reader ব্যবহার করে আর কোনো shell, code execution বা parent plugin tool দেখায় না।

core-এর agent/model/tool span execution telemetry দেয়; task ID, parent ID আর child run ID সম্পর্ক জোড়া দেয়। এই owner কোনো logging exporter যোগ করে না।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `DelegationTasks(directory=Path('.task-history'))` | background task-গুলোর মালিক, history এই folder-এ সংরক্ষিত |
| `async with tasks.opened()` | owner চালু; বের হলে worker-গুলো খালি করে |
| `with tasks.bind()` | এই scope-এ `delegate_task` `background`/`resume` পায় |
| `DelegationReports(tasks, conversation_id='review')` | শেষ হওয়া background report parent-এর কাছে পৌঁছে দেয় |

///

/// check | সংক্ষেপে মনে রাখুন

* `SubAgents(agents=[SubAgent(a), SubAgent(b)])` → একটিমাত্র `delegate_task(agent_name, task)` tool।
* child parent-এর কথোপকথন দেখে না — `task` স্বয়ংসম্পূর্ণ হতে হবে; deps যায়, usage ডিফল্টে শেয়ার হয়, tool যায় না।
* `include_self=True` → নিজের একটি নতুন run (`self`), সব capability-সহ; `max_depth` (ডিফল্ট 3) গভীরতা বাঁধে।
* প্রতি delegate: `usage_limits`, `timeout_seconds`, `max_calls`, `on_failure`, `contain_errors`, `models`।
* `models` মেনু (`'fast'`, `'deep'` …) দিয়ে orchestrator প্রতি কাজে মডেল বাছে।
* timeout/budget নরম; crash ডিফল্টে কঠিন, `contain_errors=True` দিলে জোরালো `ModelRetry`।
* ডিস্ক থেকে লোড করতে `agent_folders='agents'` দিন (ডিফল্ট এখন `None`); ফাইল পড়া হয় workspace থেকে, কিছুই execute হয় না।

///
