
# Advisor { #advisor }

/// note | এই পেজে যা শিখবেন

* executor মডেল উত্তর দেওয়ার বা সিদ্ধান্ত নেওয়ার আগে কীভাবে আলাদা একটি advisor মডেলের পরামর্শ নেয়।
* structured উত্তর (`output_type`) আর native বনাম local পথ।
* `max_uses`, `max_tokens`, `caching`, `forward_history` — option-গুলোর মানে।
* advisor কী context পায়, usage/ব্যর্থতা/observability, আর durable execution-এ সীমাবদ্ধতা।

///

একটি executor মডেলকে উত্তর দেওয়ার বা কোনো সিদ্ধান্তে প্রতিশ্রুতিবদ্ধ হওয়ার আগে আলাদা একটি advisor মডেলের পরামর্শ নেওয়ার উপায় দিন।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/advisor/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// tip | উদাহরণ দিয়ে বুঝি

একজন জুনিয়র ইঞ্জিনিয়ার (executor — দ্রুত, সস্তা মডেল) রোজকার কাজ নিজেই করেন, কিন্তু বড় সিদ্ধান্তের আগে একজন সিনিয়রকে (advisor — শক্তিশালী মডেল) একবার জিজ্ঞেস করে নেন। প্রতিটি লাইন সিনিয়রকে দিয়ে লেখালে খরচ বেশি; শুধু কঠিন মোড়ে পরামর্শ নিলে ভালো মান কম খরচে মেলে।

///

## ব্যবহার { #usage }

advisor মডেলটি প্রথম argument হিসেবে দিন। মডেলটি Pydantic AI-এর গ্রহণযোগ্য যেকোনো model নাম বা model instance হতে পারে:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import Advisor

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        Advisor(
            'anthropic:claude-opus-5-5',
            max_uses=1,
            max_tokens=4096,
        )
    ],
)

result = agent.run_sync(
    'Design a zero-downtime database migration. Consult the advisor before choosing a plan.'
)
print(result.output)
```

কখন পরামর্শ নেবে তা executor নিজেই ঠিক করে। পরামর্শ নেওয়া বাধ্যতামূলক হলে user prompt-এ বা agent-এর instructions-এ স্পষ্টভাবে বলে দিন।

/// info | কোডটি সহজ ভাষায়

| অংশ | মানে |
|---|---|
| `'openai:gpt-6.1-sol'` | executor — আসল কাজটি করে |
| `Advisor('anthropic:claude-opus-5-5', ...)` | advisor — দরকার হলে পরামর্শ দেয় |
| `max_uses=1` | প্রতি executor model request-এ সর্বোচ্চ একবার পরামর্শ |
| `max_tokens=4096` | প্রতিটি পরামর্শের output-এর সর্বোচ্চ token |
| prompt-এ "Consult the advisor..." | executor-কে পরামর্শ নিতে স্পষ্টভাবে বলা |

///

## Structured উত্তর { #structured-answers }

`output_type`-এ সেই output specification দিন, যা আপনি একটি Pydantic AI `Agent`-কে দিতেন — যেমন একটি Pydantic model, একটি scalar type, বা `NativeOutput(...)`। ডিফল্ট হলো `str`। advisor মডেলকে বাছাই করা output mode সাপোর্ট করতে হবে।

provider-native advisor tool কোনো output schema নেয় না। তাই অ-ডিফল্ট `output_type` `auto` mode-এ local execution বেছে নেয়; এটিকে `mode='native'`-এর সাথে মেলালে `ValueError` raise হয়।

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai_harness.advisor import Advisor


class Decision(BaseModel):
    proceed: bool
    risk_score: float


agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[Advisor('anthropic:claude-opus-5-5', output_type=Decision)],
)
```

executor tool result হিসেবে যাচাই-করা object-টি পায়। `max_uses` ফুরিয়ে গেলে tool বরং একটি সাধারণ-text সীমা-বার্তা ফেরত দেয়।

## Provider-অনুযায়ী মানিয়ে নেওয়া { #provider-adaptation }

`Advisor` দুটি execution পথের মাধ্যমে একটি যৌক্তিক tool দেয়, Pydantic AI-এর [native-or-local tool selection](../capabilities/overview.md#provider-adaptive-tools) ব্যবহার করে:

- **Native:** executor আর advisor দুজনেই একটি সামঞ্জস্যপূর্ণ Anthropic provider-এ থাকলে, বা দুজনেই OpenRouter ব্যবহার করলে, Pydantic AI-এর provider-native [`AdvisorTool`](../native-tools.md#advisor-tool) পরামর্শটি চালায়।
- **Local fallback:** বাকি প্রতিটি জুটি একটি `advisor` function tool পায়। এটি ডাকলে কনফিগার করা advisor মডেল দিয়ে একটি আলাদা Pydantic AI agent চলে।

ডিফল্ট `auto` mode-এ native বাছাই সতর্ক। capability একটি স্পষ্ট provider-যুক্ত model নাম আবার ব্যবহার করে শুধু তখনই, যখন executor আর advisor একই provider শেয়ার করে — তাই এটি অনুমান করে না যে একটি Anthropic model ID কোন OpenRouter catalog slug-এ map হয়। যেমন:

```python
from pydantic_ai_harness import Advisor

# Native for an Anthropic executor; local for OpenAI, Google, and other executors.
anthropic_advisor = Advisor('anthropic:claude-opus-5-5')

# Native for an OpenRouter executor.
openrouter_advisor = Advisor('openrouter:anthropic/claude-opus-4.8')
```

`auto` mode-এ একটি `Model` instance local-ভাবে চলে আর নিজের provider, client, credential, base URL আর instrumentation রাখে। একটি model নাম resolve হয় শুধু তখনই, যখন পরামর্শ local-ভাবে চলে, তাই native পরামর্শ executor provider-এর কনফিগারেশন ব্যবহার করে। native ব্যবহারের জন্য executor মডেলের profile-কেও advisor tool সাপোর্ট করতে হয়; নইলে `auto` local-এ ফিরে যায়।

/// info | এক নজরে: কোন জুটিতে কোন পথ (`auto` mode)

| executor | advisor | পথ |
|---|---|---|
| Anthropic | `'anthropic:...'` (নাম string) | native (profile সাপোর্ট করলে) |
| OpenRouter | `'openrouter:...'` | native (`max_uses` সেট না থাকলে) |
| OpenAI, Google, অন্য | যেকোনো | local `advisor` function tool |
| যেকোনো | `Model` instance | local |
| যেকোনো | অ-ডিফল্ট `output_type` | local |

///

## Option { #options }

| Option | ডিফল্ট | আচরণ |
|---|---:|---|
| `model` | বাধ্যতামূলক | advisor model নাম বা `Model` instance। |
| `mode` | `'auto'` | execution নীতি: `'auto'`, `'native'`, বা `'local'`। |
| `output_type` | `str` | local advisor-এর output specification। অ-ডিফল্ট মানের জন্য local execution লাগে। |
| `max_uses` | `None` | একটি executor model request-এ সর্বোচ্চ কতবার পরামর্শ। অন্তত `1` হতে হবে। |
| `max_tokens` | `None` | প্রতিটি পরামর্শের সর্বোচ্চ output token। অন্তত `1024` হতে হবে। |
| `caching` | `None` | Anthropic-native prompt-cache TTL: `'5m'` বা `'1h'`। |
| `forward_history` | `False` | executor-এর সম্পন্ন message history local পরামর্শে এগিয়ে দেয়। |

পরামর্শ যখন অবশ্যই executor provider-এর ভেতরে থাকতে হবে তখন `mode='native'` ব্যবহার করুন, আর কনফিগার করা advisor provider-কে যখন আলাদা request পেতেই হবে তখন `mode='local'`। native mode-এর জন্য একটি `anthropic:<model>` বা `openrouter:<model>` string আর ওই একই provider-এ একটি executor লাগে। executor-এর সাপোর্ট না থাকলে এটি fallback করে না।

`max_uses` প্রতি executor model request-এ পরামর্শ সীমিত করে — Anthropic-এর native tool-এর একই পরিসর — আর পরের request-এ আবার শূন্য হয়। local পথে, একটি call তার argument যাচাই হওয়ামাত্র গোনা হয়, এমনকি পরামর্শ পরে ব্যর্থ হলেও। সমান্তরাল call সীমা ছাড়াতে পারে না। `max_uses` ছাড়া, run-এর usage limit একটি request-এর ভেতরের local পরামর্শ সীমায় বাঁধে।

OpenRouter-এর native tool `max_uses` উপেক্ষা করে আর নিজের স্থির প্রতি-request সীমা প্রয়োগ করে। তাই `auto` mode-এ OpenRouter advisor-এর সাথে `max_uses` সেট করলে local fallback বাছাই হয়। `mode='native'`-এ এটি `ValueError` raise করে।

`caching` একটি সুযোগমতো Anthropic-native অপ্টিমাইজেশন। OpenRouter আর local fallback-এ এর সমতুল্য কোনো নিয়ন্ত্রণ নেই।

`forward_history` শুধু local execution পথে প্রভাব ফেলে, স্পষ্টভাবে বাছাই করা হোক বা `auto` fallback হিসেবে। এটি native tool কনফিগারেশন বা native-বনাম-local বাছাই বদলায় না। চালু থাকলে local advisor বর্তমান response-এর আগে executor-এর সম্পন্ন message history পায়। বর্তমান response, আংশিক text আর অমীমাংসিত tool call-সহ, এগিয়ে দেওয়া হয় না — তাই পরামর্শের prompt-এ তবুও সম্পূর্ণ বর্তমান প্রশ্নটি থাকতে হবে।

`custom_capability_types`-এ `Advisor` দিলে string model কনফিগারেশন YAML বা JSON agent spec থেকে লোড করা যায়। runtime `Model` instance আর কাস্টম output specification শুধু Python-এই থাকে।

/// warning | সাধারণ ভুল

OpenRouter advisor-এ `max_uses=1` দিয়ে ভাবছেন native পথে চলছে? চলছে না — OpenRouter-এর native tool `max_uses` মানে না, তাই `auto` চুপচাপ local fallback বেছে নেয় (আর `mode='native'` দিলে `ValueError`)। একইভাবে `output_type=Decision` দিলেও native পথ বন্ধ হয়ে যায়।

///

## advisor-কে দেওয়া context { #context-passed-to-the-advisor }

context নির্ভর করে execution পথের ওপর:

| পথ | advisor-এর context |
|---|---|
| Anthropic native | provider পুরো transcript দেয়: system instructions, tool definition, আগের turn আর ফল, আর এ পর্যন্ত executor-এর লেখা text। |
| OpenRouter native | executor একটি পরামর্শ-prompt দেয়। Pydantic AI `forward_transcript=false` কনফিগার করে। |
| Local fallback | executor `advisor` function tool দিয়ে একটি পরামর্শ-prompt দেয়। `forward_history=True` থাকলে advisor executor-এর সম্পন্ন message history-ও পায়। |

local advisor-এর নিজস্ব instructions আছে, আর executor-এর dependency, tool বা toolset-এ কোনো প্রবেশাধিকার নেই। সব জায়গায় একই আচরণের জন্য executor-কে বলুন, প্রশ্নটি আর সব প্রাসঙ্গিক প্রমাণ পরামর্শ-prompt-এ দিতে; local tool-এর বর্ণনাও এটিই চায়।

local পরামর্শ যায় advisor মডেলের provider-এর কাছে। `forward_history=True` থাকলে সেই request executor-এর আগের message-গুলোও structured message history হিসেবে বহন করে — যেকোনো `system_prompt` part, তার tool call আর সেগুলোর ফলসহ। native পরামর্শ executor-এর provider-এর কাছেই থাকে।

/// danger | গোপনীয়তা

`forward_history=True` দিলে executor-এর আগের সব message — system prompt, tool call আর tool-এর ফলসহ — advisor-এর provider-এর কাছে যায়, যা executor-এর provider থেকে আলাদা কোম্পানি হতে পারে। history-তে সংবেদনশীল তথ্য থাকলে এটি চালু করার আগে ভাবুন।

///

## Usage, ব্যর্থতা আর observability { #usage-failures-and-observability }

local advisor request parent run-এর [`RunUsage`][pydantic_ai.usage.RunUsage] আর [`UsageLimits`][pydantic_ai.usage.UsageLimits] শেয়ার করে, তাই তাদের request আর token agent tree-র স্বাভাবিক সীমার মধ্যে গোনা হয়। একটি local advisor run parent run-এর `conversation_id`-এর অধীনেও নথিভুক্ত হয়, তাই এর request আর span যে কথোপকথনে পরামর্শ দেয় তার সাথেই দলবদ্ধ হয়। native provider-রা advisor usage নিজেদের protocol অনুযায়ী জানায়। Anthropic advisor-নির্দিষ্ট মান `RequestUsage.details`-এ রাখে, আর OpenRouter response-এর provider details-এ মোট server-tool গণনা দেখায়।

অবৈধ option সমন্বয় `Advisor` তৈরির সময়েই ব্যর্থ হয়। executor আর provider-এর সামঞ্জস্য যাচাই হয় যখন একটি run তার model request প্রস্তুত করে। Anthropic native advisor error tool result হিসেবে জানায়, যাতে executor চালিয়ে যেতে পারে। local advisor অবৈধ model আচরণ করলে executor একটি সাধারণ tool retry পায়, Pydantic AI-এর অন্যান্য subagent-ভিত্তিক tool-এর মতো। এ ছাড়া local model resolution, authentication, provider, request আর usage-limit error ছড়িয়ে পড়ে আর run থামাতে পারে। একটি local call `max_uses` ছাড়ালে tool একটি সীমিত বার্তা ফেরত দেয়, যা executor-কে আর পরামর্শ ছাড়াই চালিয়ে যেতে বলে।

`Advisor` নিজের কোনো span পাঠায় না। Pydantic AI instrumentation বিশ্বব্যাপী (globally) চালু থাকলে, যেমন `logfire.instrument_pydantic_ai()` দিয়ে, একটি local পরামর্শ `advisor` নামের একটি agent run হিসেবে দেখা যায়; executor-এ প্রতি-agent `instrument=` ওই run পর্যন্ত পৌঁছায় না। native পরামর্শ executor-এর model request-এরই অংশ।

## একসাথে ব্যবহার (Composition) { #composition }

advisor tool সবসময় দৃশ্যমান আর [Tool Search](../tools-advanced.md#tool-search)-এর মাধ্যমে deferred হয় না। এটি tool নাম আর toolset ID `advisor` সংরক্ষণ করে রাখে। একটি agent-এর একজনই advisor, তাই দুটি `Advisor` capability মিশে একটি হয়। `None`-এ রাখা একটি option (`max_uses`, `max_tokens`, `caching`) অন্য instance-এর মান নেয়, দুটি list `output_type` একত্রিত হয়, আর বাকি প্রতিটি option পরের instance-এর মান নেয়। মেশানোর ফলে যদি `mode='native'`-এর একটি OpenRouter `Advisor` একটি `max_uses` পায় — যা কোনো একক `Advisor` মেনে নেয় না — তাহলে `max_uses` একটি `HarnessDeprecationWarning`-সহ উপেক্ষিত হয়; ভবিষ্যতের একটি release-এ এটি `UserError` raise করবে।

streaming-এর সময়, advisor পরামর্শ চলাকালীন executor stream থেমে থাকে আর সম্পূর্ণ পরামর্শ পাওয়া গেলে আবার চলে। local fallback advisor মডেলের token delta executor stream-এ জুড়ে দেয় না।

native পরামর্শ durable execution-এর সাথে সামঞ্জস্যপূর্ণ, কারণ এটি executor model request-এরই অংশ থাকে। local execution এখনও প্রতিটি durable backend জুড়ে একই semantics রাখতে পারে না। Temporal আর Prefect ফেরত আসা পরামর্শ checkpoint করতে পারে, কিন্তু activity-local বা task-local [`RunUsage`][pydantic_ai.usage.RunUsage]-এর পরিবর্তন বাইরের run-এ মিশে ফেরে না। DBOS সাধারণ function-tool call checkpoint করে না, তাই workflow replay-এর সময় একটি local advisor request আবার চলতে পারে।

durable run-এ একটি সাপোর্টেড provider-সহ `mode='native'` ব্যবহার করুন। সেখানে local execution, `auto` fallback-সহ, অসমর্থিত। `Advisor` durable run শনাক্ত করতে পারে না, কারণ Pydantic AI এখনও কোনো public durable-context চুক্তি প্রকাশ করে না — তাই এটি সেখানে local execution প্রত্যাখ্যানও করে না।

/// check | সংক্ষেপে মনে রাখুন

* `Advisor('anthropic:claude-opus-5-5')` → executor একটি advisor tool পায়; কখন ডাকবে তা নিজে ঠিক করে।
* executor আর advisor একই Anthropic বা OpenRouter provider-এ হলে native; বাকি সব local `advisor` function tool।
* `output_type`, `Model` instance, বা OpenRouter-এ `max_uses` → `auto`-তে local পথ।
* `max_uses` প্রতি executor request-এ সীমা; `max_tokens` অন্তত 1024।
* local advisor executor-এর tool/deps পায় না — প্রশ্ন আর প্রমাণ prompt-এ দিন; `forward_history=True` আগের history পাঠায়।
* durable run-এ শুধু `mode='native'`; local সেখানে অসমর্থিত, আর `Advisor` নিজে তা আটকায় না।

///

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.advisor.Advisor
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
