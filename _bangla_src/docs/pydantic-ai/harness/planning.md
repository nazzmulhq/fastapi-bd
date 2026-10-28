
# Planning { #planning }

/// note | এই পেজে যা শিখবেন

* লম্বা agent run-এ মডেল কেন পথ হারায়, আর `Planning` কীভাবে একটি নিজে-হালনাগাদ-হওয়া task list দিয়ে তা সামলায়।
* prompt cache না ভেঙে প্রতি turn-এ মডেলকে প্ল্যান দেখানোর কৌশল।
* ছয়টি tool, subtask ও dependency, আর SQLite/Postgres/Redis-এ প্ল্যান সংরক্ষণ।
* এক agent দিয়ে প্ল্যান লিখে আরেক agent দিয়ে সেটি চালানো।
* event, durable execution আর `pydantic-ai-todo` থেকে migrate করা।

///

`Planning` একটি ছোট toolset-এর মাধ্যমে মডেলকে একটি গোছানো, নিজে-হালনাগাদ-হওয়া task list দেয় — আর prompt cache কখনো অকেজো না করেই প্রতি turn-এ বর্তমান প্ল্যানটি মডেলের সামনে তুলে ধরে। এটি একটি run-এর জন্য memory-তে থাকতে পারে, বা SQLite/Postgres-এ সংরক্ষিত হতে পারে; ধাপগুলোকে dependency-সহ subtask-এ ভাগ করতে পারে; আর খুঁটিনাটি পরিবর্তন থেকে event পাঠাতে পারে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/planning/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

লম্বা agentic run পথ থেকে সরে যায়: মডেল ভুলে যায় সে কী করতে শুরু করেছিল আর কী বাকি আছে। সাধারণ সমাধান — একটি চলমান প্ল্যান রাখা আর প্রতি turn-এ সেটি system prompt-এ আবার ঢোকানো — prompt cache অকেজো করে দেয়। system prompt থাকে request-এর একদম সামনে, তাই প্ল্যানের প্রতিটি সম্পাদনা cache করা prefix বদলে দেয়, আর পুরো কথোপকথন আবার পূর্ণ token-মূল্যে প্রসেস করতে বাধ্য করে।

## সমাধান { #the-solution }

মডেল `planning` toolset দিয়ে প্ল্যানের মালিকানা রাখে। বর্তমান প্ল্যানটি প্রতিটি request-এর শেষে (tail) জুড়ে দেওয়া একটি ক্ষণস্থায়ী (ephemeral) reminder হিসেবে ফিরে আসে, যার শুরুতে থাকে capability-র একমাত্র cache breakpoint:

- reminder-টি যোগ হয় স্থায়ী (durable) history সংরক্ষিত হওয়ার পরে, তাই এটি মডেলের কাছে পৌঁছায় কিন্তু কখনো `message_history`-তে লেখা হয় না। turn-এর পর turn reminder জমতে থাকে না।
- reminder খোলে একটি `CachePoint` দিয়ে, যা provider-রা ঠিক তার আগের content-এর সাথে জোড়ে: শেষ user prompt, বা tool loop-এ সর্বশেষ tool result। পরের request ঠিক ওই content দিয়েই শুরু হয়, তাই Anthropic, Bedrock আর OpenAI-তে প্রতিটি request আগেরটির prefix — tool result-সহ — cache থেকে পড়ে নেয়, আর শুধু reminder-টি cache ছাড়া পাঠানো হয়। OpenRouter-এ breakpoint থামে আগের user message-এ, তাই তার পরের assistant turn আর tool result-গুলো স্পষ্ট prefix-এর বাইরে থাকে।

সব capability cache breakpoint-এর মতোই provider-অনুযায়ী mapping প্রযোজ্য: OpenAI মডেল `CachePoint` পায় শুধু তখনই, যখন model profile স্পষ্ট prompt cache breakpoint চালু করে; OpenRouter এটিকে tool result-এ না জুড়ে আগের user message-এ জোড়ে; আর যে মডেলগুলোর স্পষ্ট breakpoint নেই (যেমন Google-এর), সেগুলো এটি উপেক্ষা করে। Anthropic automatic caching (`anthropic_cache`) থাকলে automatic breakpoint বসে reminder-এর ওপর, যা পরের request-এ থাকে না; তার ঠিক আগের `Planning` breakpoint-টিই পরের request cache থেকে পড়ে। reminder-এর আগে কোনো content নেই এমন request (শুধু `instructions`-ওয়ালা প্রথম request) breakpoint ছাড়াই reminder পায়, কারণ সেখানে রক্ষা করার মতো কোনো prefix নেই।

`Planning`-এর আগে তালিকাভুক্ত কোনো capability যদি প্রতি request-এ একটি tail part জুড়ে দেয় (যেমন `SystemReminders`), তাহলে তার content বসে স্থায়ী history আর প্ল্যান reminder-এর মাঝে। তখন `Planning` breakpoint ওই content-টিকেও ঢেকে নেয়, তাই তার cache entry শুধু ততক্ষণ পড়া যায় যতক্ষণ ওই content একই থাকে। আগের capability-র নিজের breakpoint তখনও স্থায়ী history চিহ্নিত করে।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি লম্বা বই ফটোকপি করে রেখেছেন (cache)। প্রতিবার প্রথম পাতায় (system prompt) "আজকের কাজ" লিখে বদলালে পুরো বই আবার ফটোকপি করতে হয়। `Planning` বরং প্রতিবার বইয়ের শেষে একটি আলাদা চিরকুট (tail reminder) গুঁজে দেয় — বইটা অপরিবর্তিত থাকে, শুধু চিরকুটটা নতুন। আর চিরকুটটা বইয়ের সাথে বাঁধাই করা হয় না (history-তে সংরক্ষিত হয় না), তাই পুরোনো চিরকুট জমে না।

///

## ব্যবহার { #usage }

`capabilities`-এ `Planning()` দিয়ে একটি `Agent` তৈরি করুন। tool-গুলো স্বয়ংক্রিয়ভাবে রেজিস্টার হয়, আর system prompt-এ স্থির (static) ব্যবহার-নির্দেশনা যোগ হয়:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Planning

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[Planning()])

result = agent.run_sync('Refactor the auth module and add tests.')
print(result.output)
```

## Tool-গুলো { #the-tools }

| Tool | কাজ |
|---|---|
| `write_plan(items)` | পুরো প্ল্যান তৈরি বা প্রতিস্থাপন করে (পুরো তালিকা বদল)। |
| `read_plan()` | step id আর অগ্রগতির সারাংশসহ বর্তমান প্ল্যান পড়ে। |
| `add_task(content, active_form)` | একটি `pending` ধাপ শেষে যোগ করে। |
| `update_task_status(task_id, status)` | id ধরে একটি ধাপের status বদলায়। |
| `update_task_statuses(updates)` | এক call-এ কয়েকটি status বদল প্রয়োগ করে, all-or-nothing যাচাইসহ। |
| `remove_task(task_id)` | id ধরে একটি ধাপ মুছে ফেলে। |

প্রতিটি ধাপে থাকে একটি `content` string, একটি ঐচ্ছিক চলমান-কালের (present-continuous) `active_form` লেবেল, আর একটি `status` (`pending`, `in_progress`, `completed`, `cancelled`)। প্রচলিত নিয়ম — নির্দেশনায় আর tool-এর উত্তরে বলা আছে — হলো ঠিক একটি ধাপ `in_progress` রাখা।

ছয়টিই ডিফল্টভাবে রেজিস্টার হয়। `tools=` সেটিকে একটি অনুমোদিত তালিকায় (allowlist) সীমিত করে, আর বিল্ট-ইন নির্দেশনাও সেই অনুযায়ী বদলায়:

```python
from pydantic_ai_harness import Planning

planning = Planning(tools=['write_plan'])  # whole-plan replacement only -- one tool, no step ids to track
```

বর্তমান mode যে tool রেজিস্টার করে না তার নাম দিলে `ValueError` raise হয়; `descriptions`-এ অজানা key দিলেও তাই।

/// info | এক নজরে: একটি ধাপের গঠন

| field | উদাহরণ | মানে |
|---|---|---|
| `content` | "auth module-এ test যোগ করো" | ধাপটি কী |
| `active_form` | "test যোগ করছি" | চলমান অবস্থায় দেখানোর লেবেল (ঐচ্ছিক) |
| `status` | `pending` → `in_progress` → `completed` / `cancelled` | ধাপটি এখন কোথায় |

///

### Subtask আর dependency { #subtasks-and-dependencies }

`enable_subtasks=True` দিলে আরও তিনটি tool, `blocked` status, আর `read_plan`-এ একটি `hierarchical` view যোগ হয়:

| Tool | কাজ |
|---|---|
| `add_subtask(parent_id, content, active_form)` | একটি parent-এর নিচে child ধাপ যোগ করে। |
| `set_dependency(task_id, depends_on_id)` | একটি ধাপকে আরেকটির জন্য অপেক্ষা করায়; নির্ভরশীল ধাপটি তার পূর্বশর্ত মীমাংসা (completed বা cancelled) না হওয়া পর্যন্ত স্বয়ংক্রিয়ভাবে `blocked` থাকে। নিজের ওপর নির্ভরতা, চক্র (cycle) আর ডুপ্লিকেট প্রত্যাখ্যাত হয়। |
| `get_available_tasks()` | যে ধাপগুলোর কোনো অসম্পূর্ণ dependency নেই — যেগুলো এখনই শুরু করা যায় — তাদের তালিকা দেয়। |

`enable_subtasks` সেট না থাকলে `write_plan` `parent_id`, `depends_on` আর `blocked` status প্রত্যাখ্যান করে: subtask tool ছাড়া কেউ dependency মিলিয়ে দেখে না আর কোনো view hierarchy দেখায় না, তাই এগুলো সংরক্ষণ করা হতো এমন এক লেখা, যা প্ল্যানে প্রতিফলিত হয় না।

## সংরক্ষণ (Persistence) { #persistence }

ডিফল্টভাবে প্ল্যান প্রতি run-এর জন্য একটি নতুন, আলাদা in-memory প্ল্যান। সংরক্ষণ করতে একটি `store` দিন:

```python
from pydantic_ai_harness import Planning
from pydantic_ai_harness.planning import SqlitePlanStore

planning = Planning(store=SqlitePlanStore('plan.db', session='user-123'))
```

বিল্ট-ইন store হলো `InMemoryPlanStore`, `SqlitePlanStore`, `PostgresPlanStore` (caller-এর নিজের asyncpg pool-এর ওপর) আর `RedisPlanStore` (caller-এর নিজের `redis.asyncio` client-এর ওপর) — তাই harness-এর কোনো database driver লাগে না। যেকোনো `PlanStore` implementation কাজ করে, আর `store_resolver` প্রতি run-এ একটি বেছে নেয়। `SqlitePlanStore` তার database রাখে agent যে মেশিনে চলছে সেখানে, workspace-এ নয়। এর জন্য ফাইল-ভিত্তিক database লাগে; ক্ষণস্থায়ী প্ল্যানের জন্য `':memory:'` নয়, `InMemoryPlanStore` ব্যবহার করুন।

tail reminder প্রতিটি model request-এ store পড়ে, তাই store কোনো exception raise করলে run মান কমিয়ে চলতে থাকে না, বরং ব্যর্থ হয় — reminder "যতটা পারা যায়" (best-effort) ভিত্তিতে চলে না। এটি ইচ্ছাকৃত: যে প্ল্যান মডেল আর দেখতে পায় না, সেই অবস্থায় নীরবে চলতে থাকা ঠিক নয়। retry আর fallback নীতি store-এর দায়িত্ব, `Planning`-এর নয়; আর `PlanStore` একটি protocol ঠিক এই কারণেই, যাতে আপনি একটিকে মুড়ে (wrap) নিতে পারেন:

```python
class BestEffort:
    """Serve the last known plan when the backing store is unreachable."""

    def __init__(self, inner: PlanStore) -> None:
        self._inner, self._last = inner, []

    async def get_items(self) -> list[PlanItem]:
        try:
            self._last = await self._inner.get_items()
        except ConnectionError:
            pass
        return self._last

    # ... delegate the other five methods to `self._inner`
```

/// warning | সাধারণ ভুল

`SqlitePlanStore(':memory:')` দিয়ে "অস্থায়ী" প্ল্যান বানানোর চেষ্টা করবেন না — `SqlitePlanStore`-এর ফাইল-ভিত্তিক database লাগে। অস্থায়ী প্ল্যান চাইলে `InMemoryPlanStore` ব্যবহার করুন (বা `store` একদম না দিলেই ডিফল্টভাবে তাই হয়)।

///

### আলাদা run-এ প্ল্যান করা আর চালানো { #planning-and-executing-in-separate-runs }

একটি শেয়ার করা store-ই দুই run-এর মধ্যে হস্তান্তরের পুরো ব্যবস্থা। এক agent প্ল্যান লেখে, দ্বিতীয়টি সেটি চালায়, আর তাদের মধ্যে একমাত্র যে অবস্থা পার হয় তা হলো প্ল্যানটি:

```python
store = SqlitePlanStore('plan.db', session='issue-403')

planner = Agent('anthropic:claude-opus-5-5', capabilities=[Planning(store=store)])
executor = Agent('anthropic:claude-sonnet-5-5', capabilities=[Planning(store=store)])

await planner.run('Investigate the issue and write a plan. Do not implement anything.')
await executor.run('Implement the plan.')
```

executor শুরু হয় কোনো `message_history` ছাড়া, তাই planner-এর অনুসন্ধানের খরচ তাকে কখনো দিতে হয় না। এর প্রথম request-এ থাকে শুধু নতুন prompt আর প্ল্যান reminder, যা capability store থেকে আবার তৈরি করে। এই কারণেই দুই agent আলাদা মডেলে চলতে পারে: বড় context-এর একটি মডেল পড়া আর ভাবার কাজ করতে পারে, আর ছোট একটি মডেল ফলাফলের checklist ধরে কাজটি সম্পন্ন করতে পারে।

planner-এর "শুধু পড়বে, কিছু বদলাবে না" শৃঙ্খলা নির্ভর করে আপনি ওই agent কীভাবে কনফিগার করেছেন তার ওপর (কোন toolset পায়, আর তার instructions কী বলে) — capability এটি জোর করে প্রয়োগ করে না।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `SqlitePlanStore('plan.db', session='issue-403')` | দুই agent-এর শেয়ার করা প্ল্যান, একটি নির্দিষ্ট session-এ |
| `planner` (Opus 5.5) | খুঁজে দেখে, প্ল্যান লেখে — কিছু implement করে না |
| `executor` (Sonnet 5.5) | কোনো history ছাড়াই শুরু করে, শুধু প্ল্যান দেখে কাজ করে |

///

## Event { #events }

`Planning` tool দিয়ে করা পরিবর্তনে সাড়া দিতে typed plan event-এ subscribe করুন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Planning
from pydantic_ai_harness.planning import PlanCompletedEvent

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[Planning()])

@agent.on_event(PlanCompletedEvent)
async def announce(ctx, event):
    print('done:', event.item.content)
```

এই family-তে আছে
`PlanCreatedEvent`, `PlanUpdatedEvent`, `PlanStatusChangedEvent`, `PlanCompletedEvent` আর
`PlanDeletedEvent`; প্রতিটি প্রভাবিত `item` বহন করে, আর আপডেটের ক্ষেত্রে `previous_state`-ও।

run event আসে planning tool-এর পথ থেকে, `write_plan`-সহ। কোনো `PlanStore`-এ application-এর সরাসরি পরিবর্তনের
কোনো run context নেই, তাই সেগুলো run event তৈরি করে না। `PlanEventEmitter`, `EventCallback`
আর store-এর `event_emitter` parameter এখনও সাপোর্টেড, তবে deprecated।

## কেন পুরো প্ল্যান প্রতিস্থাপন { #why-whole-plan-replacement }

পরিবর্তনশীল integer index দিয়ে ধাপ ধরা (insert/remove/reorder) কোড আর মডেল — দুজনের জন্যই ভুলপ্রবণ। `write_plan` প্রতিটি call-এ পুরো প্ল্যানটি নতুন করে বলে, তাই কোনো index খেয়াল রাখতে হয় না। আর খুঁটিনাটি সম্পাদনা (`add_task`, `update_task_status`, `remove_task`) বরং `read_plan`-এ দেখানো স্থির `id` ধরে কাজ করে।

/// tip | উদাহরণ দিয়ে বুঝি

"তিন নম্বর কাজটা মুছে দাও" বললে, আগে একটা কাজ মুছে গিয়ে থাকলে তিন নম্বর এখন অন্য কাজ — ভুল জিনিস মুছে যায়। তাই `Planning` হয় পুরো তালিকা নতুন করে লেখায়, নয়তো প্রতিটি কাজের একটি স্থায়ী "রোল নম্বর" (`id`) দিয়ে কাজ করে, যা তালিকা বদলালেও বদলায় না।

///

## Caching-এর নিশ্চয়তা { #caching-guarantee }

প্ল্যান কখনো system prompt বা instructions-এ ঢোকানো হয় না। সেখানে যায় স্থির ব্যবহার-নির্দেশনা (cache-স্থির); শুধু পরিবর্তনশীল প্ল্যানটি যায় ক্ষণস্থায়ী tail reminder-এ, যা শুধু প্রতি-request-এর কপিতে থাকে আর কখনো সংরক্ষিত হয় না। এটি বন্ধ করতে `inject=False` সেট করুন। যে মডেলগুলোর profile prompt caching সাপোর্ট করে, Pydantic AI সেগুলোর জন্য `CachePoint` map করে; অন্য মডেলে এটি উপেক্ষিত হয়।

একটি durable-execution capability যুক্ত থাকলে, প্রতিটি plan store call একটি journal-ভুক্ত capability
operation: reminder তৈরির জন্য প্ল্যান পড়া, আর plan tool-গুলোর প্রতিটি পড়া ও লেখা।
replay তখন store আবার না ডেকে রেকর্ড করা ফল ব্যবহার করে, তাই run পুনরুদ্ধারের সময় স্থায়ী store-এ একই ধাপ
দ্বিতীয়বার যোগ হয় না। যে engine function tool workflow code-এর ভেতরে চালায়,
যেমন DBOS, সেখানে একটি plan tool call একা চলে, অন্য tool call-এর সাথে একসাথে নয়, আর তার শেষ store call-এর পরে run
event পাঠায়। ফলে replay-তে তার রেকর্ড করা store call-গুলোর ক্রম একই থাকে,
ওই event-গুলোর জন্য `event_stream_handler` যে ধাপগুলো চালায় সেগুলোর তুলনাতেও।
`Planning`-এর একটি স্থির ডিফল্ট `id='planning'` আছে, তাই durable পুনরুদ্ধার কোনো
কনফিগারেশন ছাড়াই কাজ করে।
যে engine tool আর capability operation আলাদা worker-এ চালায়, যেমন Temporal, সেগুলো
run-এর in-memory প্ল্যান সেখানে বহন করে না: প্রতিটি call run context থেকে নিজের store খুঁজে নেয়। ধাপগুলোর মধ্যে প্ল্যান ধরে রাখতে
একটি স্থায়ী `store` বা একটি `store_resolver` (যেমন `SqlitePlanStore` বা `PostgresPlanStore`)
দিন।

/// warning | সাধারণ ভুল

Temporal-এর মতো আলাদা worker-ভিত্তিক engine-এ ডিফল্ট in-memory প্ল্যান রাখলে এক ধাপে লেখা প্ল্যান পরের ধাপে পাওয়া যায় না। durable execution-এ সবসময় একটি স্থায়ী `store` (বা `store_resolver`) দিন।

///

## কনফিগারেশন { #configuration }

```python
from pydantic_ai_harness import Planning

Planning(
    guidance=None,           # static system-prompt guidance; None = default, '' = omit
    cache_ttl='5m',          # TTL for the cache breakpoint leading the plan reminder ('5m' | '1h')
    store=None,              # None = fresh in-memory plan per run; or a PlanStore to persist
    enable_subtasks=False,   # add subtask/dependency tools and the 'blocked' status
    inject=True,             # surface the current plan as a cache-safe tail reminder
    tools=None,              # None = every tool the mode registers; or an allowlist of names
    descriptions=None,       # optional per-tool description overrides, keyed by tool name
)
```

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`Planning` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে:

```yaml
# agent.yaml
model: anthropic:claude-sonnet-5-5
capabilities:
  - Planning: {}
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Planning

agent = Agent.from_file('agent.yaml', custom_capability_types=[Planning])
result = agent.run_sync('...')
print(result.output)
```

## `pydantic-ai-todo`-এর সাথে সম্পর্ক { #relationship-to-pydantic-ai-todo }

`Planning` [Vstorm](https://vstorm.co/)-এর একটি community package [`pydantic-ai-todo`](https://github.com/vstorm-co/pydantic-ai-todo)-এর task-list ফিচারগুলো — স্থায়ী store, subtask, dependency আর event — নিজের মধ্যে নিয়েছে, আর সেটির জায়গা নিয়েছে। `pydantic-ai-todo` থেকে migrate করলে, tool-গুলোর নাম বদলেছে:

| `pydantic-ai-todo` | `Planning` |
|---|---|
| `write_todos` | `write_plan` |
| `read_todos` | `read_plan` |
| `add_todo` | `add_task` |
| `update_todo_status` / `update_todo_statuses` | `update_task_status` / `update_task_statuses` |
| `remove_todo` | `remove_task` |
| `add_subtask`, `set_dependency`, `get_available_tasks` | অপরিবর্তিত |

দুটি পার্থক্যের জন্য প্রস্তুত থাকুন: connection-string-এর সুবিধা নেই (`create_storage(backend=...)` আর সংশ্লিষ্টগুলো সরানো হয়েছে — আপনি নিজের asyncpg pool বা Redis client বানান, আর এটিই harness-কে driver-মুক্ত রাখে), আর `PlanEvent`-এ কোনো `timestamp` নেই, তাই যে consumer এটি দিয়ে ক্রম সাজাত বা log করত, তাকে নিজের ঘড়ি ব্যবহার করতে হবে।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Anthropic prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
- [Code Mode](code-mode.md) -- prompt cache-সচেতন আরেকটি harness capability

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[Planning()]` — মডেল নিজেই একটি task list রাখে আর হালনাগাদ করে।
* প্ল্যান যায় request-এর শেষে ক্ষণস্থায়ী reminder-এ, system prompt-এ নয় — তাই prompt cache ভাঙে না, history-তেও জমে না।
* ছয়টি মূল tool; `enable_subtasks=True` দিলে subtask, dependency আর `blocked` status।
* `store=SqlitePlanStore(...)` / Postgres / Redis দিয়ে সংরক্ষণ; শেয়ার করা store দিয়ে planner আর executor আলাদা মডেলে চলতে পারে।
* store ব্যর্থ হলে run-ও ব্যর্থ হয় — retry/fallback store-এর দায়িত্ব।
* durable execution-এ স্থায়ী store দিন; `id='planning'` ডিফল্টে পুনরুদ্ধার কাজ করে।

///

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.planning.Planning
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
