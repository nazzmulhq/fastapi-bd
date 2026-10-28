# Agent Spec { #agent-specs }

/// note | এই পেজে যা শিখবেন

* Python কোড না লিখে YAML বা JSON ফাইলে একটি এজেন্টের সংজ্ঞা লেখা (মডেল, নির্দেশনা, capability...)।
* `Agent.from_file` আর `Agent.from_spec` দিয়ে লোড করা, আর keyword আর্গুমেন্ট দিয়ে spec-এর মান বদলানো।
* `{{নাম}}` ধরনের template string, `deps_schema` আর `output_schema`।
* `AgentSpec.to_file` দিয়ে spec সংরক্ষণ আর editor-এ autocomplete।

///

Agent spec দিয়ে আপনি YAML বা JSON-এ ঘোষণামূলকভাবে এজেন্ট সংজ্ঞায়িত করতে পারেন — [মডেল](models/overview.md), [নির্দেশনা](agent.md#instructions), [capability](capabilities/overview.md), সবকিছু। লোড করতে এক লাইন, Python-এ এজেন্ট তৈরির কোনো কোড লাগে না।

এটি কাজে লাগে:

- অ্যাপ্লিকেশনের কোড থেকে এজেন্টের কনফিগারেশন আলাদা রাখতে
- ডেভেলপার নন এমন মানুষদের (prompt engineer, বিষয়-বিশেষজ্ঞ) দিয়ে এজেন্ট কনফিগার করাতে
- অন্য কনফিগ ফাইলের পাশে এজেন্টের সংজ্ঞা রাখতে
- টিম বা প্রজেক্ট-জুড়ে এজেন্টের কনফিগারেশন ভাগ করতে

/// tip | উদাহরণ দিয়ে বুঝি

রান্নার রেসিপি কার্ড ভাবুন। রাঁধুনি (Python কোড) একই থাকে, কিন্তু কার্ড (YAML ফাইল) বদলালে ভিন্ন পদ তৈরি হয়। আপনার টিমের একজন prompt লেখক Python না জেনেও কার্ডে নির্দেশনা বা মডেল বদলে দিতে পারেন, কোড স্পর্শ না করেই।

///

## একটি spec সংজ্ঞায়িত করা { #defining-a-spec }

একটি spec ফাইল YAML বা JSON-এ এজেন্টের কনফিগারেশন সংজ্ঞায়িত করে:

⟦CODE1⟧

/// info | ফাইলটি সহজ ভাষায়

* `model`: কোন মডেল চলবে।
* `instructions`: এজেন্টের নির্দেশনা।
* `model_settings`: মডেলের সেটিং, এখানে উত্তরের সর্বোচ্চ token।
* `capabilities`: তালিকায় প্রতিটি একটি capability — এখানে DuckDuckGo দিয়ে ওয়েব সার্চ আর উচ্চ মাত্রার "thinking"।

///

## Spec লোড করা { #loading-specs }

[`Agent.from_file`][pydantic_ai.agent.Agent.from_file] একটি YAML বা JSON ফাইল থেকে spec লোড করে একটি এজেন্ট তৈরি করে:

⟦CODE2⟧

[`Agent.from_spec`][pydantic_ai.agent.Agent.from_spec] একটি dict বা [`AgentSpec`][pydantic_ai.agent.AgentSpec] instance নেয় আর বাড়তি keyword আর্গুমেন্ট সমর্থন করে, যা spec-কে পরিপূরক করে বা override করে:

{% raw %}
⟦CODE3⟧
{% endraw %}

Keyword আর্গুমেন্ট spec-এর ফিল্ডের সাথে এভাবে কাজ করে:

* **Scalar ফিল্ড** (`model`, `name`, `end_strategy` ইত্যাদি) — দেওয়া থাকলে keyword আর্গুমেন্ট spec-এর মান override করে। আবার-চেষ্টার বাজেটের জন্য, `retries` keyword আর্গুমেন্ট spec-এর `retries` মান override করে।
* **`instructions`** — মিলিত হয়: আগে spec-এর নির্দেশনা, তারপর keyword আর্গুমেন্টের নির্দেশনা।
* **`capabilities`** — মিলিত হয়: আগে spec-এর capability, তারপর keyword আর্গুমেন্টের capability।
* **`model_settings`** — যোগ করে মিলিত হয়: keyword আর্গুমেন্টের সেটিং spec-এর মেলা সেটিং override করে।
* **`output_type`** — spec-এর `output_schema`-র ওপর অগ্রাধিকার পায়।

spec-এ `model` না-ও থাকতে পারে; বদলে এটি `Agent.from_spec`-এ বা এজেন্ট চালানোর সময় দেওয়া যায়।

`deps_type` দেওয়া হলে, spec-এর `instructions`, `description` আর capability আর্গুমেন্টের [template string](#template-strings) তৈরির সময়েই deps টাইপের বিপরীতে compile আর যাচাই হয়।

spec লোডের ওপর আরও নিয়ন্ত্রণের জন্য, `Agent.from_spec`-এ দেওয়ার আগে spec আলাদাভাবে লোড করতে [`AgentSpec.from_file`][pydantic_ai.agent.AgentSpec.from_file] ব্যবহার করুন।

## Template string { #template-strings }

{% raw %}[`TemplateStr`][pydantic_ai.template.TemplateStr] Handlebars-ধরনের template (`{{variable}}`) দেয়, যা চলার সময় এজেন্টের [dependencies](dependencies.md)-এর বিপরীতে render হয়। spec ফাইলে, `{{` থাকা স্ট্রিং নিজে থেকে template string-এ রূপান্তরিত হয়:{% endraw %}

{% raw %}
```yaml
instructions: "You are assisting {{name}}, who is a {{role}}."
```
{% endraw %}

Template ভ্যারিয়েবল `deps` অবজেক্টের ফিল্ড থেকে নেওয়া হয়। একটি `deps_type` (বা [`deps_schema`](#deps_schema)) দেওয়া থাকলে, template ভ্যারিয়েবলের নাম তৈরির সময়েই যাচাই হয়।

/// tip | উদাহরণ দিয়ে বুঝি

Template string হলো ফাঁকা জায়গাসহ একটি ছাপানো চিঠি: "প্রিয় ____, আপনি একজন ____।" রান চলার সময় `deps=UserProfile(name='Alice', role='engineer')` দিলে ফাঁকা ঘরগুলো ভরে যায়। আর `deps_type` দিলে, তৈরির সময়েই ধরা পড়ে টেমপ্লেটে এমন কোনো নাম আছে কিনা যা `deps`-এ নেই (যেমন বানান ভুল)।

///

Python কোডে, [`TemplateStr`][pydantic_ai.template.TemplateStr] স্পষ্টভাবে ব্যবহার করা যায়, তবে IDE autocomplete আর type checking-এর জন্য সাধারণত [`RunContext`][pydantic_ai.tools.RunContext]-সহ একটি callable বেশি পছন্দনীয়:

{% raw %}
⟦CODE4⟧
{% endraw %}

## Capability spec-এর লেখার ধরন { #capability-spec-syntax }

spec-এ capability তিন রূপে লেখা যায়:

* `'MyCapability'` — কোনো আর্গুমেন্ট নেই, `MyCapability.from_spec()` ডাকে
* `{'MyCapability': value}` — একটি positional আর্গুমেন্ট, `MyCapability.from_spec(value)` ডাকে
* `{'MyCapability': {key: value, ...}}` — keyword আর্গুমেন্ট, `MyCapability.from_spec(**kwargs)` ডাকে

এই built-in capability-গুলো spec-এ ঘোষণা করা যায়: [`Thinking`][pydantic_ai.capabilities.Thinking], [`Caching`][pydantic_ai.capabilities.Caching], [`Instrumentation`][pydantic_ai.capabilities.Instrumentation], [`WebSearch`][pydantic_ai.capabilities.WebSearch], [`WebFetch`][pydantic_ai.capabilities.WebFetch], [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration], [`XSearch`][pydantic_ai.capabilities.XSearch], [`MCP`][pydantic_ai.capabilities.MCP], [`ToolSearch`][pydantic_ai.capabilities.ToolSearch], [`PrefixTools`][pydantic_ai.capabilities.PrefixTools], [`NativeTool`][pydantic_ai.capabilities.NativeTool], [`IncludeToolReturnSchemas`][pydantic_ai.capabilities.IncludeToolReturnSchemas], [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata], [`RaiseContentFilterError`][pydantic_ai.capabilities.RaiseContentFilterError], [`ReinjectSystemPrompt`][pydantic_ai.capabilities.ReinjectSystemPrompt], আর [`LocalWorkspace`][pydantic_ai.capabilities.LocalWorkspace]। অন্য [built-in capability](capabilities/overview.md#available-capabilities) এমন আর্গুমেন্ট নেয় যা serialize করা যায় না (callable, toolset অবজেক্ট), আর শুধু Python কোডেই ব্যবহার করা যায়।

/// info | তিন রূপ, YAML-এ

```yaml
capabilities:
  - Thinking                 # আর্গুমেন্ট ছাড়া: Thinking.from_spec()
  - WebSearch:               # keyword আর্গুমেন্ট: WebSearch.from_spec(local='duckduckgo')
      local: duckduckgo
```

`Thinking`-এর `effort` প্রথম ফিল্ড, তাই একটি positional মানও দেওয়া যায়: `- Thinking: high` মানে `Thinking.from_spec('high')`, অর্থাৎ `Thinking(effort='high')`।

///

## Spec-এ নিজের capability { #custom-capabilities-in-specs }

নিজের capability কীভাবে agent spec-এর সাথে কাজ করাবেন, তা দেখুন [Publishing capabilities](capabilities/custom.md#publishing-capabilities)-এ।

## `AgentSpec` রেফারেন্স { #agentspec-reference }

[`AgentSpec`][pydantic_ai.agent.AgentSpec] মডেল পুরো spec-এর গঠন প্রকাশ করে:

| ফিল্ড | টাইপ | বর্ণনা |
|---|---|---|
| `model` | `str \| None` | [মডেলের](models/overview.md) নাম |
| `name` | `str \| None` | এজেন্টের নাম |
| `description` | `str \| None` | এজেন্টের বর্ণনা ([template](#template-strings) সমর্থন করে) |
| `instructions` | `str \| list[str] \| None` | [নির্দেশনা](agent.md#instructions) ([template](#template-strings) সমর্থন করে) |
| `model_settings` | `dict \| None` | [মডেল সেটিং](agent.md#model-run-settings) |
| `capabilities` | `list` | [Capability](capabilities/overview.md) (দেখুন [spec-এর লেখার ধরন](#capability-spec-syntax)) |
| `deps_schema` | `dict \| None` | [Template string](#template-strings) যাচাইয়ের JSON Schema (নিচে দেখুন) |
| `output_schema` | `dict \| None` | [গোছানো আউটপুটের](output.md) JSON Schema (নিচে দেখুন) |
| `retries` | `int \| AgentRetries \| None` | [টুল](tools-advanced.md#tool-retries) আর [আউটপুট যাচাইয়ের](output.md#output-validator-functions) আবার-চেষ্টার বাজেট। দুটোর জন্য একই বাজেট দিতে একটি পূর্ণসংখ্যা দিন, বা আলাদাভাবে কনফিগার করতে [`AgentRetries`][pydantic_ai.agent.AgentRetries]। |
| `end_strategy` | `EndStrategy` | কখন থামবে (`'early'`, `'graceful'`, বা `'exhaustive'`) |
| `tool_timeout` | `float \| None` | ডিফল্ট [টুল](tools.md) timeout, সেকেন্ডে |
| `instrument` | `bool \| None` | [Logfire](logfire.md) instrumentation চালু করে |
| `metadata` | `dict \| None` | এজেন্টের [metadata](agent.md#run-metadata) |

### `deps_schema` { #deps_schema }

{% raw %}একটি Python `deps_type` ছাড়া spec ফাইল লোড করার সময়, `deps_schema` একটি JSON Schema দেয় যা তৈরির সময় [template string](#template-strings)-এর ভ্যারিয়েবলের নাম যাচাই করে। এটি চলার সময় আসল deps অবজেক্ট যাচাই **করে না** — শুধু নিশ্চিত করে যে `{{user_name}}`-এর মতো template ভ্যারিয়েবল schema-য় সংজ্ঞায়িত property-র সাথে মেলে।{% endraw %}

### `output_schema` { #output_schema }

দেওয়া থাকলে (আর `from_spec`-এ কোনো `output_type` keyword আর্গুমেন্ট না দেওয়া হলে), `output_schema` ঠিক করে মডেলকে চূড়ান্ত আউটপুট হিসেবে কোন গঠন তৈরি করতে হবে। ভেতরে ভেতরে, এটি একটি [`StructuredDict`][pydantic_ai.output.StructuredDict] আউটপুট টাইপ তৈরি করে: JSON Schema মডেল API-তে পাঠানো হয় যাতে মডেল জানে কোন গঠন তৈরি করতে হবে, আর উত্তর একটি `dict[str, Any]` হিসেবে ফেরত আসে।

/// note | মনে রাখুন

মডেলের উত্তর schema-র `properties` বা `required` ফিল্ডের বিপরীতে যাচাই হয় না — এটি একটি সাধারণ dict হিসেবে গৃহীত হয়। schema মডেলের জন্য একটি নির্দেশনা, চলার সময়ের যাচাইয়ের শর্ত নয়।

///

{% raw %}
⟦CODE5⟧
{% endraw %}

## Spec সংরক্ষণ { #saving-specs }

[`AgentSpec.to_file`][pydantic_ai.agent.AgentSpec.to_file] একটি spec YAML বা JSON-এ সংরক্ষণ করে আর চাইলে editor autocompletion-এর জন্য একটি সঙ্গী JSON Schema ফাইল তৈরি করে:

⟦CODE6⟧

তৈরি হওয়া JSON Schema ফাইল সেসব editor-এ autocompletion আর যাচাই চালু করে, যেগুলো [YAML Language Server](https://github.com/redhat-developer/yaml-language-server) protocol সমর্থন করে। schema তৈরি বাদ দিতে `schema_path=None` দিন।

/// check | সংক্ষেপে মনে রাখুন

* YAML/JSON-এ `model`, `instructions`, `capabilities` ইত্যাদি লিখে `Agent.from_file('agent.yaml')`।
* `Agent.from_spec(dict, ...)`-এর keyword আর্গুমেন্ট: scalar override করে, `instructions`/`capabilities` জোড়া লাগে।
* `{{নাম}}` template `deps` থেকে ভরে; `deps_type` বা `deps_schema` নামগুলো আগেই যাচাই করে।
* `output_schema` মডেলকে গঠন বলে, কিন্তু উত্তর যাচাই করে না (`dict` ফেরত দেয়)।
* callable বা toolset লাগে এমন capability spec-এ নয়, শুধু Python কোডে।

///
