
# StackOne { #stackone }

/// note | এই পেজে যা শিখবেন

* `StackOne` দিয়ে একজন ব্যবহারকারীর যুক্ত ব্যবসায়িক অ্যাপ্লিকেশনে (BambooHR, Salesforce, Zendesk...) কাজ করা।
* দুটি টুল মোড (`search_execute` বনাম `individual`), `actions` দিয়ে ছাঁকা, একাধিক অ্যাকাউন্ট আর অনুমোদন।

///

`StackOne` ব্যবহার করুন যখন একটি এজেন্টকে একজন ব্যবহারকারীর যুক্ত ব্যবসায়িক অ্যাপ্লিকেশনের একটির সাথে কাজ করতে হয়, যেমন BambooHR, Salesforce বা Zendesk। প্রতিটি instance একটি যুক্ত অ্যাকাউন্টে সীমিত, যা [StackOne](https://www.stackone.com) আর একটি provider-এর মাঝে একটি authenticate করা সংযোগ।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/stackone/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// tip | উদাহরণ দিয়ে বুঝি

StackOne হলো একটি "সার্বজনীন অ্যাডাপ্টার": BambooHR, Workday, Salesforce, Zendesk — প্রতিটির API আলাদা, কিন্তু StackOne সবগুলোকে একই ধাঁচের টুলে পরিণত করে। আপনার এজেন্টকে প্রতিটি সার্ভিসের আলাদা নিয়ম শিখতে হয় না।

///

## শুরুর আগে { #before-you-start }

[StackOne docs](https://docs.stackone.com) অনুসরণ করে:

1. একটি connector কনফিগার করে একটি অ্যাকাউন্ট যুক্ত করুন। আপনার প্রথম পরীক্ষার জন্য, শুধু দরকারি পড়ার action চালু করুন।
2. StackOne dashboard থেকে যুক্ত অ্যাকাউন্টের ID কপি করুন।
3. action চালাতে পারে এমন একটি StackOne API key তৈরি করুন।

আপনার এজেন্ট যে মডেল ব্যবহার করে তার জন্যও একটি API key লাগে।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[stackone]" "pydantic-ai-slim[openai,spec]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[stackone]" "pydantic-ai-slim[openai,spec]"
```

///


`openai` আর `spec` extra নিচের মডেল আর agent-spec উদাহরণ সমর্থন করে। ভিন্ন মডেল provider-এর জন্য, এর বদলে সেই provider-এর extra ইনস্টল করুন।

যে shell-এ উদাহরণ চালাবেন সেখানে credential সেট করুন:

```bash
export STACKONE_API_KEY='your-stackone-api-key'
export STACKONE_ACCOUNT_ID='your-linked-account-id'
export OPENAI_API_KEY='your-openai-api-key'
```

`StackOne` নিজে থেকে `STACKONE_API_KEY` পড়ে। উদাহরণ `STACKONE_ACCOUNT_ID` স্পষ্টভাবে পড়ে, যাতে অ্যাকাউন্ট ID hard-code না হয়। এর বদলে সরাসরি `api_key=` দিতে পারেন, কিন্তু secret source control-এর বাইরে রাখুন।

## আপনার প্রথম এজেন্ট চালান { #run-your-first-agent }

```python
import os

from pydantic_ai import Agent
from pydantic_ai_harness import StackOne

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        StackOne(account_id=os.environ['STACKONE_ACCOUNT_ID']),
    ],
)
result = agent.run_sync('List the first 5 employees')
print(result.output)
```

ডিফল্টভাবে, মডেল দুটি টুল পায়। এটি রিকোয়েস্টের সাথে মেলে এমন একটি action খোঁজে, তারপর ফেরত আসা action ID চালায়। চূড়ান্ত আউটপুট যুক্ত provider আর এর ডেটার ওপর নির্ভর করে।

## উপলব্ধ action নিয়ন্ত্রণ { #control-available-actions }

যুক্ত অ্যাকাউন্টের জন্য কোন action চালু তা StackOne নিয়ন্ত্রণ করে। সেই কনফিগারেশনকে প্রধান প্রবেশ-নিয়ন্ত্রণ হিসেবে ধরুন।

মডেল কোন টুল দেখবে তাও সীমিত করতে চাইলে `actions` ব্যবহার করুন। Pattern Python [`fnmatch`](https://docs.python.org/3/library/fnmatch.html) syntax ব্যবহার করে, যেখানে `*` একটি wildcard। এগুলো case উপেক্ষা করে আর পুরো `{connector}_{action}_{entity}` টুলের নাম মেলায়:

```python
from pydantic_ai_harness import StackOne

StackOne(account_id='your-linked-account-id', actions=['*_list_*'])            # All matching list tools
StackOne(account_id='your-linked-account-id', actions=['workday_get_worker'])  # One exact tool
```

`actions` দিলে নিজে থেকে `individual` মোড বাছা হয়। `actions`-কে স্পষ্টভাবে `tool_mode='search_execute'`-এর সাথে জুড়লে একটি error ওঠে, কারণ সেই মোড শুধু search আর execute টুল নিবন্ধন করে।

## একটি টুল মোড বাছুন { #choose-a-tool-mode }

| মোড | মডেল যা পায় | কখন ব্যবহার করবেন |
|---|---|---|
| `search_execute` | দুটি টুল: একটি action খোঁজা, তারপর ID দিয়ে চালানো | অ্যাকাউন্টে অনেক চালু action থাকলে। `actions` বাদ দিলে এটিই ডিফল্ট। |
| `individual` | প্রতিটি চালু action-এর জন্য একটি টুল আর schema | সুনির্দিষ্ট action বাছতে বা প্রতি-টুল আচরণ যোগ করতে হলে। `actions` দিলে এই মোড বাছা হয়। |

`search_execute` মোডে, action ID রানের সময় search টুল ফেরত দেয় আর অনুমান করা উচিত নয়। `individual` মোডে, বাছা সব টুল schema মডেলে পাঠানো হয়, তাই বড় action সেট `actions` দিয়ে ছাঁকুন।

দরকার না হওয়া পর্যন্ত StackOne টুল মডেলের context-এর বাইরে রাখতে, `defer_loading=True` দিন। চাহিদামতো লোড হতে capability-র একটি `id` লাগে, আর এটি যুক্ত অ্যাকাউন্ট থেকে একটি তৈরি করে -- `StackOne(account_id='45320')` হলো `stackone-45320` -- তাই একটি এজেন্ট প্রতিটির নাম না দিয়েই কয়েকটি অ্যাকাউন্টে পৌঁছাতে পারে:

```python
from pydantic_ai_harness import StackOne

StackOne(account_id='your-linked-account-id', defer_loading=True)
```

*একই* অ্যাকাউন্টে দুটি capability সেই id ভাগ করে আর এজেন্ট তৈরির সময় প্রত্যাখ্যাত হয়, যা আপনি চান: একটি যুক্ত অ্যাকাউন্ট একটি সংযোগ। তৈরি-করাটি override করতে হলে একটি স্পষ্ট `id=` দিন।

### এক এজেন্টে দুটি অ্যাকাউন্ট { #two-accounts-on-one-agent }

আলাদা id দুটি capability-কে আলাদা রাখে, কিন্তু এদের টুলের নাম বদলায় না। StackOne-এর সার্ভার connector আর action অনুযায়ী টুলের নাম দেয় (`bamboohr_list_employees`), তাই একই provider-এর দুটি অ্যাকাউন্ট একই নাম তালিকা করে আর রান id-র বদলে টুলের নামে ব্যর্থ হয়:

```
UserError: StackOneToolset 'stackone-crm-account' defines a tool whose name conflicts with
existing tool from StackOneToolset: 'bamboohr_list_employees'
```

[`PrefixTools`](../capabilities/overview.md) দিয়ে এদের namespace দিন, যা ঠিক এই কাজের জন্যই:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import PrefixTools

from pydantic_ai_harness import StackOne

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        PrefixTools(StackOne(account_id='hr-account'), prefix='hr'),
        PrefixTools(StackOne(account_id='crm-account'), prefix='crm'),
    ],
)
```

মডেল দেখে `hr_bamboohr_list_employees` আর `crm_bamboohr_list_employees`, আর প্রতিটি নিজের যুক্ত অ্যাকাউন্টে যায়। *ভিন্ন* provider-এর দুটি অ্যাকাউন্ট আগে থেকেই ভিন্ন টুলের নাম তালিকা করে, তাই এদের কোনো prefix লাগে না।

### বড় টুল ফল সীমিত করা { #bound-large-tool-results }

Provider action বড় export ফেরত দিতে পারে। এজেন্ট-জুড়ে বড় টুল ফেরত কমাতে StackOne-কে [Tool Output Limits](tool-output-limits.md) capability-র সাথে জুড়ুন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import StackOne, ToolOutputLimits
from pydantic_ai_harness.tool_output_limits import LocalFileStore

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[
        StackOne(account_id='your-linked-account-id'),
        ToolOutputLimits(store=LocalFileStore()),
    ],
)
```

### অনুমোদন চাওয়া { #require-approval }

অনুমোদন নিজে থেকে চালু হয় না। মানুষের নিশ্চিতকরণ লাগে এমন কাজের জন্য, Pydantic AI-এর [tool approval](../toolsets.md#requiring-tool-approval)-সহ পাবলিক `StackOneToolset` ব্যবহার করুন:

```python
import os

from pydantic_ai import Agent
from pydantic_ai_harness.stackone import StackOneToolset

stackone_tools = StackOneToolset(
    account_id=os.environ['STACKONE_ACCOUNT_ID'],
    actions=['workday_create_worker'],
).approval_required()

agent = Agent('openai:gpt-6.1-sol', toolsets=[stackone_tools])
```

লিংক করা guide-এ বর্ণিত মতো ফলের deferred অনুমোদন-অনুরোধ সামলান।

/// warning | সাধারণ ভুল

একটি HR এজেন্টে অনুমোদন ছাড়া StackOne দেওয়া, যেখানে BambooHR-এ `update_employee` বা `terminate_employee`-এর মতো action চালু। একটি ভুল বোঝা prompt-এ এজেন্ট একজন কর্মীর বেতন বা অবস্থা বদলে ফেলতে পারে। StackOne dashboard-এ শুধু দরকারি action চালু রাখুন আর লেখার কাজে অনুমোদন চান।

///

## YAML বা JSON-এ এজেন্ট সংজ্ঞায়িত করা { #define-the-agent-in-yaml-or-json }

capability YAML বা JSON-এর জন্য Pydantic AI-এর [agent spec](../agent-spec.md) ফরম্যাটের সাথেও কাজ করে। API key ফাইলে না রেখে `STACKONE_API_KEY`-এ রাখুন:

```yaml
# agent.yaml
model: openai:gpt-6.1-sol
capabilities:
  - StackOne:
      account_id: 'your-linked-account-id'
      actions: ['*_list_*']
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import StackOne

agent = Agent.from_file('agent.yaml', custom_capability_types=[StackOne])
```

`custom_capability_types` দিন, যাতে spec loader জানে `StackOne` কীভাবে তৈরি করতে হয়।

[`Agent(toolsets=[...])`](../toolsets.md) বা অন্য toolset wrapper দরকার হলে নিচু-স্তরের `StackOneToolset` সরাসরি ব্যবহার করুন।

নিজস্ব `base_url` আর URL-মানের `client` মান HTTPS ব্যবহার করতে হবে। toolset auth header যোগ করে আর URL মানের জন্য অনুপস্থিত থাকলে `tool-mode` query প্যারামিটার যুক্ত করে। URL-এর `tool-mode` কনফিগার করা মোডের সাথে সংঘর্ষ করলে এটি একটি error তোলে, কারণ নতুন করে লেখা signed URL অকেজো করত। একটি signed URL-সহ `search_execute` ব্যবহার করলে, sign করার আগে `tool-mode=search_execute` অন্তর্ভুক্ত করুন। আগে-তৈরি client যেমন আছে তেমন ব্যবহৃত হয়; এদের HTTPS transport, auth, অ্যাকাউন্ট বাছাই আর টুল মোড নিজে কনফিগার করুন।

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.stackone.StackOne
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.stackone.StackOneToolset
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `StackOne(account_id=...)` আর `STACKONE_API_KEY` — একটি instance একটি যুক্ত অ্যাকাউন্ট।
* ডিফল্ট `search_execute` (দুটি টুল); `actions=[...]` দিলে `individual` মোড।
* প্রধান প্রবেশ-নিয়ন্ত্রণ হলো StackOne-এ কোন action চালু।
* একই provider-এর দুটি অ্যাকাউন্টে `PrefixTools`; লেখার কাজে `StackOneToolset` + অনুমোদন।

///
