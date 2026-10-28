# ফাংশন টুল (Function Tools) { #function-tools }

/// note | এই পেজে যা শিখবেন

* টুল কী আর কেন: মডেল একটি কাজ করে বা বাড়তি তথ্য এনে উত্তর তৈরিতে সাহায্য নেয়।
* `@agent.tool`, `@agent.tool_plain` আর `tools=[...]` দিয়ে টুল নথিভুক্ত করা।
* ফাংশনের signature আর docstring থেকে টুলের schema কীভাবে তৈরি হয়, আর কোন docstring মডেলে পৌঁছায়।
* `Enum`-এর বিকল্পের বর্ণনা, আর টুল থেকে বাড়তি বার্তা পাঠানো।

///

ফাংশন টুল মডেলকে কাজ করার আর উত্তর তৈরিতে সাহায্যের জন্য বাড়তি তথ্য আনার একটি ব্যবস্থা দেয়।

এগুলো কাজে লাগে যখন আপনি চান মডেল কোনো কাজ করে তার ফল ব্যবহার করুক, যখন এজেন্টের দরকার হতে পারে এমন সব প্রসঙ্গ নির্দেশনায় রাখা অবাস্তব বা অসম্ভব, বা যখন উত্তর তৈরির কিছু লজিক আরেকটি (অবশ্যই AI-চালিত নয় এমন) টুলে ছেড়ে দিয়ে এজেন্টের আচরণ আরও নির্ধারিত বা নির্ভরযোগ্য করতে চান।

আপনি যদি চান মডেল তার শেষ কাজ হিসেবে একটি ফাংশন ডাকতে পারুক, ফল মডেলে ফেরত না পাঠিয়ে, তাহলে বদলে একটি [আউটপুট ফাংশন](output.md#output-functions) ব্যবহার করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

LLM একজন বুদ্ধিমান কিন্তু ঘরে আটকে থাকা পরামর্শদাতা: সে আজকের আবহাওয়া জানে না, আপনার ডেটাবেস দেখতে পায় না, পাশা ছুড়তে পারে না। টুল হলো তার হাতে দেওয়া ফোন: "আবহাওয়া অফিসে ফোন করো", "ডেটাবেসে খোঁজো"। মডেল ঠিক করে কখন কোন নম্বরে ফোন করবে আর কী বলবে (আর্গুমেন্ট); আপনার Python ফাংশন আসল কাজটি করে আর ফল ফেরত দেয়।

///

একটি এজেন্টে টুল নথিভুক্ত করার কয়েকটি উপায় আছে:

- [`@agent.tool`][pydantic_ai.agent.Agent.tool] decorator দিয়ে — যে টুলের এজেন্টের [context][pydantic_ai.tools.RunContext]-এ প্রবেশ লাগে তার জন্য
- [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain] decorator দিয়ে — যে টুলের এজেন্টের [context][pydantic_ai.tools.RunContext]-এ প্রবেশ লাগে না তার জন্য
- `Agent`-এর [`tools`][pydantic_ai.agent.Agent.__init__] keyword আর্গুমেন্ট দিয়ে, যা সাধারণ ফাংশন বা [`Tool`][pydantic_ai.tools.Tool]-এর instance নিতে পারে

আরও উন্নত ব্যবহারের জন্য, [toolsets](toolsets.md) সুবিধা দিয়ে আপনি টুলের সংগ্রহ সামলাতে পারেন (আপনার বানানো বা একটি [MCP server](mcp/client.md) বা অন্য [third party](third-party-tools.md#third-party-tools)-এর দেওয়া) আর `Agent`-এর [`toolsets`][pydantic_ai.agent.Agent.__init__] keyword আর্গুমেন্ট দিয়ে একবারে একটি এজেন্টে নথিভুক্ত করতে পারেন। ভেতরে, সব `tools` আর `toolsets` একটি একক [মিলিত toolset](toolsets.md#combining-toolsets)-এ জড়ো হয় যা মডেলের কাছে উপলব্ধ করা হয়।

/// info | ফাংশন টুল বনাম RAG

ফাংশন টুল মূলত RAG (Retrieval-Augmented Generation)-এর "R" — এগুলো মডেলকে বাড়তি তথ্য চাইতে দিয়ে সে যা পারে তা বাড়ায়।

Pydantic AI টুল আর RAG-এর প্রধান অর্থগত পার্থক্য হলো RAG vector search-এর সমার্থক, অথচ Pydantic AI টুল আরও সাধারণ-উদ্দেশ্যের। vector search-এর জন্য, একাধিক provider-জুড়ে embedding তৈরি করতে আমাদের [embeddings](embeddings.md) সমর্থন ব্যবহার করতে পারেন।

///

/// info | ফাংশন টুল বনাম গোছানো আউটপুট

নাম থেকেই বোঝা যায়, ফাংশন টুল মডেলকে কী ডাকার জন্য উপলব্ধ তা জানাতে মডেলের "tools" বা "functions" API ব্যবহার করে। ডিফল্ট [tool output mode](output.md#tool-output) ব্যবহারের সময় [গোছানো আউটপুটের](output.md) schema সংজ্ঞায়িত করতেও টুল বা ফাংশন ব্যবহার হয়, তাই একটি মডেলের কাছে অনেক টুল থাকতে পারে, যার কিছু ফাংশন টুল ডাকে আর কিছু রান শেষ করে একটি চূড়ান্ত আউটপুট তৈরি করে।

///

## Decorator দিয়ে নথিভুক্তি { #registering-function-tools-via-decorator }

`@agent.tool`-কে ডিফল্ট decorator ধরা হয়, কারণ বেশিরভাগ ক্ষেত্রে টুলের এজেন্টের [context][pydantic_ai.tools.RunContext]-এ প্রবেশ লাগবে।

দুটোই ব্যবহার করে একটি উদাহরণ:

⟦CODE1⟧

1. এটি বেশ সহজ একটি কাজ, তাই আমরা দ্রুত আর সস্তা Gemini flash মডেল ব্যবহার করতে পারি।
2. উদাহরণ সহজ রাখতে আমরা ব্যবহারকারীর নাম একটি স্ট্রিং dependency হিসেবে দিই।
3. এই টুলের কোনো context লাগে না, এটি শুধু একটি এলোমেলো সংখ্যা ফেরত দেয়। এই ক্ষেত্রে সম্ভবত গতিশীল নির্দেশনা ব্যবহার করতে পারতেন।
4. এই টুলের খেলোয়াড়ের নাম লাগে, তাই এটি dependencies-এ পৌঁছাতে `RunContext` ব্যবহার করে, যা এই ক্ষেত্রে শুধু খেলোয়াড়ের নাম।
5. খেলোয়াড়ের নাম dependency হিসেবে দিয়ে এজেন্ট চালান।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// info | কোডটি সহজ ভাষায়

* `roll_dice` কোনো context চায় না, তাই `@agent.tool_plain` — শুধু 1 থেকে 6-এর একটি সংখ্যা ফেরত দেয়।
* `get_player_name` `ctx.deps` (এখানে `'Anne'`) পড়ে, তাই প্রথম প্যারামিটার `RunContext[str]` আর `@agent.tool`।
* মডেল নিজে ঠিক করে কখন কোন টুল ডাকবে: পাশা ছোড়ে, নাম জানে, তারপর অনুমানের সাথে মিলিয়ে উত্তর লেখে।
* docstring ("Roll a six-sided die...") মডেলকে বলে টুলটি কী করে — তাই docstring ভালো করে লিখুন।

///

চলুন সেই খেলার বার্তাগুলো ছাপিয়ে দেখি কী ঘটেছে:

⟦CODE2⟧

এটি একটি চিত্র দিয়ে দেখাতে পারি:

⟦CODE3⟧

## Agent আর্গুমেন্ট দিয়ে নথিভুক্তি { #registering-function-tools-via-agent-argument }

decorator ব্যবহারের পাশাপাশি, [`Agent` constructor][pydantic_ai.agent.Agent.__init__]-এর `tools` আর্গুমেন্ট দিয়েও টুল নথিভুক্ত করতে পারি। টুল আবার ব্যবহার করতে চাইলে এটি কাজে লাগে, আর টুলের ওপর আরও সূক্ষ্ম নিয়ন্ত্রণও দিতে পারে।

⟦CODE4⟧

1. `Agent` constructor দিয়ে টুল নথিভুক্ত করার সবচেয়ে সহজ উপায় হলো ফাংশনের একটি তালিকা দেওয়া, ফাংশনের signature পরীক্ষা করে ঠিক করা হয় টুলটি [`RunContext`][pydantic_ai.tools.RunContext] নেয় কিনা।
2. `agent_a` আর `agent_b` হুবহু এক — কিন্তু টুলের সংজ্ঞা আবার ব্যবহার করতে আর টুল কীভাবে সংজ্ঞায়িত হবে তার ওপর আরও সূক্ষ্ম নিয়ন্ত্রণ দিতে [`Tool`][pydantic_ai.tools.Tool] ব্যবহার করতে পারি, যেমন তাদের নাম বা বর্ণনা সেট করা, বা একটি নিজের [`prepare`](tools-advanced.md#tool-prepare) মেথড ব্যবহার করা।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## টুলের আউটপুট { #function-tool-output }

Pydantic JSON-এ serialize করতে পারে এমন যেকোনো কিছু টুল ফেরত দিতে পারে। multi-modal বিষয়বস্তু আর metadata-সহ উন্নত আউটপুট অপশনের জন্য দেখুন [Advanced Tool Features](tools-advanced.md#function-tool-output)।

## টুলের schema { #function-tools-and-schema }

ফাংশনের প্যারামিটার ফাংশনের signature থেকে বের করা হয়, আর `RunContext` ছাড়া সব প্যারামিটার সেই টুল কলের schema তৈরিতে ব্যবহার হয়।

আরও ভালো, Pydantic AI ফাংশন থেকে docstring বের করে আর ([griffe](https://mkdocstrings.github.io/griffe/)-এর কল্যাণে) docstring থেকে প্যারামিটারের বর্ণনা বের করে schema-য় যোগ করে।

[Griffe সমর্থন করে](https://mkdocstrings.github.io/griffe/reference/docstrings/#docstrings) `google`, `numpy` আর `sphinx` ধাঁচের docstring থেকে প্যারামিটারের বর্ণনা বের করা। Pydantic AI docstring দেখে কোন ফরম্যাট ব্যবহার করবে তা অনুমান করে, তবে আপনি [`docstring_format`][pydantic_ai.tools.DocstringFormat] দিয়ে স্পষ্টভাবে সেট করতে পারেন। `require_parameter_descriptions=True` সেট করে প্যারামিটারের শর্তও প্রয়োগ করতে পারেন। একটি প্যারামিটারের বর্ণনা অনুপস্থিত থাকলে এটি একটি [`UserError`][pydantic_ai.exceptions.UserError] তুলবে।

docstring-এর তিনটি অংশ মডেলে পৌঁছায়: শুরুর বর্ণনা, প্যারামিটারের বর্ণনা, আর returns অংশের প্রথম এন্ট্রি। Griffe পার্স করতে পারে এমন অন্য অংশ, যেমন `Raises`, `Examples`, `Notes`, `Warnings` আর `Yields`, বাদ পড়ে, তাই মডেলের যার ওপর কাজ করতে হবে তা শুরুর বর্ণনা, একটি প্যারামিটারের বর্ণনা, বা প্রথম returns এন্ট্রিতে রাখুন।

একটি টুলের schema দেখাতে, এখানে আমরা একটি মডেল যে schema পেত তা ছাপাতে [`FunctionModel`][pydantic_ai.models.function.FunctionModel] ব্যবহার করি:

⟦CODE5⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// warning | সাধারণ ভুল

`Raises:` বা `Examples:` অংশে লেখা "এই টুল শুধু কর্মদিবসে ডাকো" — মডেল তা কখনো দেখে না। মডেলের জানা দরকার এমন নিয়ম docstring-এর শুরুর বর্ণনায় বা প্যারামিটারের বর্ণনায় লিখুন।

///

একটি টুলের একটি একক প্যারামিটার থাকলে যা JSON schema-য় একটি অবজেক্ট হিসেবে প্রকাশ করা যায় (যেমন dataclass, TypedDict, pydantic model), টুলের schema সরল হয়ে শুধু সেই অবজেক্টটি হয়।

এখানে একটি উদাহরণ যেখানে আমরা মডেলে পাঠানো হতো এমন টুলের schema দেখতে [`TestModel.last_model_request_parameters`][pydantic_ai.models.test.TestModel.last_model_request_parameters] ব্যবহার করি।

⟦CODE6⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### Docstring { #docstrings }

একটি প্যারামিটার, একটি ফিল্ড বা একটি enum সদস্যের নিচে লেখা একটি docstring এর অর্থ বলার স্বাভাবিক জায়গা,
কিন্তু প্রতিটি মডেলে পৌঁছায় না:

| কিসের নিচে লেখা | কী বর্ণনা করে | মডেলে পাঠানো হয় |
| --- | --- | --- |
| একটি টুল বা [আউটপুট ফাংশন](output.md#output-functions) | সেই টুল | সবসময় |
| এর docstring-এ একটি `Args:` এন্ট্রি | সেই প্যারামিটার | সবসময় |
| একটি প্যারামিটার বা [আউটপুট টাইপ](output.md) হিসেবে ব্যবহৃত একটি ক্লাস | সেই অবজেক্ট | সবসময় |
| একটি `dataclass` বা `TypedDict`-এর একটি ফিল্ড | সেই ফিল্ড | একটি ফাংশনের প্যারামিটার হিসেবে |
| একটি Pydantic মডেল বা `pydantic.dataclasses.dataclass`-এর একটি ফিল্ড | সেই ফিল্ড | ক্লাসে `use_attribute_docstrings`-সহ |
| একটি `Enum` সদস্য | সেই বিকল্প | [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings]-সহ |

একটি ফাংশন signature থেকে Pydantic AI যে schema তৈরি করে — একটি টুল বা একটি আউটপুট ফাংশন — তা Pydantic-এর
[`use_attribute_docstrings`](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.use_attribute_docstrings) চালু করে,
আর তা তার নিচের প্রতিটি টাইপে পৌঁছায় যা নিজের config আনে না, যেকোনো গভীরতায়। একটি Pydantic মডেল আর
একটি `pydantic.dataclasses.dataclass` একটি আনে, যা জেতে, তাই সেগুলো এটি উপেক্ষা করে — তাদের নিজের ফিল্ড আর
তাদের ভেতরে nested যেকোনো কিছুর জন্য। যেখানেই ব্যবহার হোক সেখানে যোগ দিতে ক্লাসেই এটি সেট করুন, একটি
[আউটপুট টাইপ](output.md) হিসেবেসহ, যা একটি signature নয়, টাইপ থেকে তৈরি হয় আর তাই কখনো এটি উত্তরাধিকারসূত্রে পায় না:

⟦CODE7⟧

`Field(description=...)` হিসেবে লেখা একটি বর্ণনার কোনো config লাগে না আর docstring-এর ওপর অগ্রাধিকার পায়।

/// tip | সহজ নিয়ম

নিশ্চিত হতে চাইলে Pydantic মডেলে `model_config = ConfigDict(use_attribute_docstrings=True)` লিখুন, আর `Enum`-এ `UseEnumMemberDocstrings` mix-in করুন। অথবা সবসময় `Field(description=...)` ব্যবহার করুন — এটি সব জায়গায় কাজ করে।

///

#### Enum-এর বিকল্প { #enum-options }

একটি `Enum` প্যারামিটার মডেলে পৌঁছায় তার মানগুলোর তালিকা হিসেবে, যা বলে বিকল্পগুলো কী কিন্তু সেগুলোর অর্থ কী তা বলে না। প্রতিটি সদস্যের নিচে লেখা docstring সেই বিকল্পের বর্ণনা হিসেবে পাঠাতে enum-এ [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করুন। এমন একটি enum একটি সাধারণ `enum` তালিকার বদলে `const` মানের `anyOf` হিসেবে render হয়:

⟦CODE8⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

`Enum` হলো একমাত্র ক্ষেত্র যেখানে একটি config ফ্ল্যাগের বদলে একটি mix-in লাগে: এর বহন করার মতো কোনো `model_config` নেই, আর একটি সাধারণ ক্লাস attribute-ও বহন করতে পারে না — annotate করা হোক বা না হোক, assign করা যেকোনো মান একটি সদস্য হয়ে যায় — তাই একটি base class-ই বাকি একমাত্র চিহ্ন। এটি ছাড়া docstring উপেক্ষিত হয় আর schema হুবহু Pydantic নিজে যা তৈরি করে তা-ই, তাই একটি enum-কে যোগ দেওয়ানোই একমাত্র জিনিস যা মডেল যা দেখে তা বদলায়।

docstring ছাড়া সদস্য একটি সাধারণ `const` রাখে, আর একটি alias-এর নিচের docstring (`high = 'high'`-এর পাশে `urgent = 'high'`) যে বিকল্পের জন্য লেখা তা বর্ণনা করে। একটি `Literal`-এর docstring লেখার জায়গা নেই, তাই এটি প্রভাবিত হয় না।

Pydantic AI যেখানেই একটি যোগ দেওয়া enum একটি মডেলকে বর্ণনা করে — একটি টুল প্যারামিটার, একটি [আউটপুট টাইপ](output.md), বা আপনার নিজের একটি মডেলের একটি ফিল্ড — বর্ণনাগুলো সাথে আসে।

docstring enum-এর source থেকে পড়া হয়, তাই চলার সময় তৈরি একটি enum-এর কোনোটি নেই। বিকল্পগুলোই রান চলার পরেই জানা গেলে, [`Choices()`](output.md#choices) ব্যবহার করুন, যা আপনি যেখানে তৈরি করেন সেখানে তৈরি একটি mapping বর্ণনা করে আর হুবহু এই `const`-এর `anyOf` schema তৈরি করে।


/// tip | টুল কল debug করা

এজেন্ট ডেভেলপমেন্টে টুলের আচরণ বোঝা অত্যন্ত গুরুত্বপূর্ণ। আপনার এজেন্টকে [Logfire](logfire.md) দিয়ে instrument করলে, দেখতে পাবেন:

- প্রতিটি টুলে কী আর্গুমেন্ট দেওয়া হয়েছে
- প্রতিটি টুল কী ফেরত দিয়েছে
- প্রতিটি টুল চলতে কত সময় নিয়েছে
- যেকোনো এরর যা ঘটেছে

এই দৃশ্যমানতা আপনাকে বুঝতে সাহায্য করে একটি এজেন্ট কেন নির্দিষ্ট সিদ্ধান্ত নিয়েছে আর টুলের বাস্তবায়নে সমস্যা চিহ্নিত করতে।

///

## একটি টুল থেকে পরবর্তী বার্তা ঢোকানো { #injecting-follow-up-messages-from-a-tool }

একটি টুল [`RunContext.enqueue`][pydantic_ai.tools.RunContext.enqueue] দিয়ে কথোপকথনে বাড়তি বার্তা ঢোকাতে পারে — কাজে লাগে যখন একটি টুল পরবর্তী প্রসঙ্গ যোগ করতে, এজেন্টের পরিকল্পনা ঘোরাতে, বা মডেলের সাড়া দেওয়া উচিত এমন একটি ঘটনা দেখাতে চায়। পুরো ধরনের জন্য দেখুন [Injecting messages mid-run](message-history.md#injecting-messages-mid-run)।

## আরও দেখুন { #see-also }

আরও টুল সুবিধা আর সংযোগের জন্য দেখুন:

- [Advanced Tool Features](tools-advanced.md) - নিজের schema, গতিশীল টুল, টুল চালানো আর retry
- [Toolsets](toolsets.md) - টুলের সংগ্রহ সামলানো
- [Native Tools](native-tools.md) - LLM provider-দের দেওয়া নেটিভ টুল
- [Common Tools](common-tools.md) - ব্যবহারের জন্য প্রস্তুত টুলের বাস্তবায়ন
- [Third-Party Tools](third-party-tools.md) - MCP, LangChain আর অন্য টুল লাইব্রেরির সাথে সংযোগ
- [Deferred Tools](deferred-tools.md) - অনুমোদন বা বাইরে চালানো লাগে এমন টুল

/// check | সংক্ষেপে মনে রাখুন

* `@agent.tool` (প্রথম প্যারামিটার `ctx: RunContext[...]`) বা `@agent.tool_plain` (context ছাড়া), বা `Agent(tools=[...])`।
* schema আসে signature (type hint) আর docstring থেকে; `RunContext` schema-য় যায় না।
* docstring-এর শুরুর বর্ণনা, `Args:` আর প্রথম returns মডেলে যায়; বাকি অংশ বাদ।
* Enum বিকল্পের অর্থ পাঠাতে `UseEnumMemberDocstrings`; Pydantic মডেলের ফিল্ডে `use_attribute_docstrings`।

///
