
# Researcher { #researcher }

/// note | এই পেজে যা শিখবেন

* `Researcher` দিয়ে একটি এজেন্টকে উৎস-সমর্থিত উত্তরসহ বিস্তৃত ওয়েব গবেষণার stack দেওয়া।
* ভেতরে কী আছে (WebSearch, WebFetch, SubAgents, ToolOutputLimits), আর workspace কেন লাগে।
* কাঠামোবদ্ধ আউটপুট, Exa Search আর Dynamic Workflow দিয়ে একে আরও শক্তিশালী করা।

///

`Researcher` একটি Pydantic AI এজেন্টকে উৎস-সমর্থিত উত্তরসহ বিস্তৃত ওয়েব গবেষণার একটি সংক্ষিপ্ত stack দেয়।
এটি নিচের [capability](../capabilities/overview.md) দিয়ে তৈরি একটি সাধারণ [জোড়া capability](../capabilities/custom.md#composition-and-middleware-semantics), তাই আপনি এটি যেমন আছে তেমন ব্যবহার করতে বা খুলে আলাদা করতে পারেন।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ব্যবহার { #usage }

লোকাল সার্চ আর fetch বিকল্প ইনস্টল করুন (DuckDuckGo সার্চ, পেজ-থেকে-Markdown আনা):

/// tab | pip

```bash
pip install "pydantic-ai-harness[researcher]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[researcher]"
```

///


তারপর একে একটি প্রশ্ন করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import Researcher

agent = Agent('openai:gpt-6.1-sol', capabilities=[LocalWorkspace('.'), Researcher()])

result = agent.run_sync('What changed in the last three major releases of Django?')
print(result.output)
```

একই এজেন্ট প্রতিটি Pydantic AI interface-এ কাজ করে: terminal chat-এর জন্য [`agent.to_cli_sync()`](../cli.md), একটি browser chat UI-এর জন্য [`agent.to_web()`](../web.md)।
এটি [durable execution](../workspace.md#durable-execution)-এর অধীনেও কাজ করে: এজেন্ট তৈরির সময় `TemporalDurability()`, `DBOSDurability()` বা `PrefectDurability()`-এর পাশে `Researcher()` দিন, আর এর টুল-ফল ঢালার জন্য workspace যুক্ত রাখুন।

অথবা ফাইল পুরোপুরি বাদ দিয়ে রপ্তানি করা [`researcher_agent`](#api-reference) [`clai`](../cli.md#custom-agents) (Pydantic AI CLI) দিয়ে চালান, [`uvx`](https://docs.astral.sh/uv/guides/tools/) মাধ্যমে:

```bash
uvx --with 'pydantic-ai-harness[researcher]' clai -a pydantic_ai_harness.researcher:researcher_agent -m openai:gpt-6.1-sol
```

## ভেতরে কী আছে { #whats-inside }

এটি আক্ষরিক অর্থেই এই capability-গুলোর জোড়া, এই ক্রমে:

- সংক্ষিপ্ত ডিফল্ট গবেষণা instructions: নিচে দেখুন [Instructions](#instructions)
- Core [`WebSearch(local=True)`](../capabilities/web-search.md): মডেল সমর্থন করলে provider-এর নেটিভ web search, না করলে একটি লোকাল DuckDuckGo বিকল্প
- Core [`WebFetch(local=True)`](../capabilities/web-fetch.md): ফলের পেছনের পেজ পড়া, যেখানে সমর্থিত সেখানে নেটিভ আর একটি লোকাল বিকল্পসহ, যাতে দাবিগুলো তাদের উৎসের বিপরীতে যাচাই করা যায়
- [`SubAgents`](subagents.md): কাজ দেওয়া, ডিফল্টভাবে একটি কেন্দ্রীভূত ওয়েব `researcher` sub-agent-সহ
- [`ToolOutputLimits`](tool-output-limits.md): যেকোনো একক টুল ফল কতটা context খেতে পারে তা সীমিত করে, বড় আকারের ফল রানের workspace-এর ফাইলে ঢেলে

কাজ দেওয়া বন্ধ করতে `subagents=[]` দিন, বা নিজের `SubAgent` entry দিন।

বড় আকারের টুল ফল রানের [workspace](../workspace.md)-এ `.pydantic-ai-harness/tool-output/`-এর নিচে (git-উপেক্ষিত) রাখা হয়, তাই একটি ছাড়া একটি রান শুরুতেই ব্যর্থ হয়। `LocalWorkspace('.')` এগুলো বর্তমান ডিরেক্টরিতে রাখে আর একটি sandbox capability এগুলো sandbox-এ রাখে। workspace ছাড়া চালাতে, `Researcher(store=LocalFileStore())` দিন; তখন ঢালা এজেন্ট চালানো মেশিনেই থাকে, এর ডিফল্ট delegate-এর জন্যও। একটি নিজস্ব delegate-এর নিজস্ব store কনফিগার করা লাগে।

/// tip | উদাহরণ দিয়ে বুঝি

একজন গবেষক সহকারীর মতো: প্রথমে গুগলে খোঁজেন (WebSearch), তারপর ফলের আসল পেজ খুলে পড়েন (WebFetch) যাতে দাবি যাচাই হয়, বড় পাশের প্রশ্ন একজন জুনিয়রকে দেন (SubAgents), আর একটা বিশাল পেজের পুরোটা মাথায় না রেখে একটা নোটে ফাইল করে রাখেন (ToolOutputLimits)।

///

### Instructions { #instructions }

`Researcher` সংক্ষিপ্ত ডিফল্ট গবেষণা instructions নিয়ে আসে (`DEFAULT_RESEARCHER_INSTRUCTIONS`, নিচের [blown-out equivalent](#blown-out-equivalent)-এ পুরোটা লেখা)। এগুলো নিজের দিয়ে বদলাতে `instructions='...'` দিন, বা কোনো ডিফল্ট instructions ছাড়া শুধু ক্ষমতাগুলো পেতে `instructions=None`।

### একে আরও শক্তিশালী করা { #making-it-more-powerful }

- **নির্দিষ্ট ফরম্যাটে গবেষণা**: এজেন্টকে একটি টাইপ করা [`output_type`](../output.md) দিন: ফলাফলের একটি Pydantic model, প্রতিটি এর উৎসের লিংকসহ, আর researcher গদ্যের বদলে কাঠামোবদ্ধ ডেটা ফেরত দেয়।
- **উন্নত মানের সার্চ**: সার্চ backend হিসেবে [`Exa Search`](exa-search.md) বসান।
- **ছড়িয়ে দেওয়া (fan out)**: [`Dynamic Workflow`](dynamic-workflow.md) যোগ করুন, যাতে এজেন্ট সমান্তরালে টাইপ করা researcher sub-agent তৈরি করে তাদের কাঠামোবদ্ধ ফল একত্র করতে পারে।

## পূর্ণ রূপে সমতুল্য { #blown-out-equivalent }

<!-- Keep this in sync with pydantic_ai_harness/researcher; it intentionally shows the complete picture. -->

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace, WebFetch, WebSearch
from pydantic_ai_harness import SubAgent, SubAgents, ToolOutputLimits

instructions = """\
Search broadly before drawing conclusions.
Read the sources that support each important claim.
Prefer primary and authoritative sources.
Cite every factual claim with a direct source link.
Distinguish sourced facts from your own inference.
"""

sub_researcher = SubAgent(
    Agent(
        name='researcher',
        description='Research a focused sub-question on the web and report back with findings and source links',
        capabilities=[WebSearch(local=True), WebFetch(local=True), ToolOutputLimits()],
    )
)

agent = Agent(
    'openai:gpt-6.1-sol',
    instructions=instructions,
    capabilities=[
        LocalWorkspace('.'),  # where oversized tool results are spilled
        WebSearch(local=True),  # native provider search, DuckDuckGo fallback on models without it
        WebFetch(local=True),  # read the pages behind the results, native or local
        SubAgents(agents=[sub_researcher], agent_folders=None),
        ToolOutputLimits(),  # spills oversized results to the workspace
    ],
)
```

দেখুন [source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/researcher/)।

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.researcher.Researcher
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.researcher.researcher_agent
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `Researcher()` = WebSearch + WebFetch + একটি researcher sub-agent + ToolOutputLimits, সাথে ডিফল্ট instructions।
* ইনস্টল: `pydantic-ai-harness[researcher]` (DuckDuckGo আর পেজ-আনার লোকাল বিকল্প)।
* বড় ফল workspace-এ ঢালা হয়, তাই একটি workspace লাগে — বা `Researcher(store=LocalFileStore())`।
* কাঠামোবদ্ধ ফলের জন্য `output_type`, ভালো সার্চের জন্য Exa, সমান্তরালের জন্য Dynamic Workflow।

///
