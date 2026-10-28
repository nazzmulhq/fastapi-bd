# নিজস্ব capability তৈরি { #building-custom-capabilities }

/// note | এই পেজে যা শিখবেন

* `AbstractCapability` subclass করে নিজের capability বানানো: **কনফিগারেশন মেথড** (টুল, instructions, settings, মডেল) আর **lifecycle hook**।
* `id` কীভাবে কাজ করে — একই `id`-এর দুটি capability কখন মেলে আর কখন exception তোলে।
* run, node, model request, tool, output, error আর event stream hook।
* durable operation, প্রতি-রান state বিচ্ছিন্নতা, ক্রম, আর প্রকাশ (publishing)।

///

নিজের [capability](overview.md) তৈরি করতে, [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass করে আপনার দরকারি মেথড override করুন। দুটি শ্রেণি আছে: **কনফিগারেশন মেথড**, যা এজেন্ট তৈরির সময় ডাকা হয় — আর [`for_run`][pydantic_ai.capabilities.AbstractCapability.for_run] একটি প্রতিস্থাপন ফেরত দিলে রান সেটআপে সেই প্রতিস্থাপন instance-এ আবার চলে (দেখুন [Per-run state isolation](#per-run-state-isolation)); [`get_wrapper_toolset`][pydantic_ai.capabilities.AbstractCapability.get_wrapper_toolset] সবসময় প্রতি-রানে ডাকা হয় — আর **lifecycle hook**, যা প্রতিটি রানের সময় চলে।

/// tip | উদাহরণ দিয়ে বুঝি

কনফিগারেশন মেথড হলো একটি গাড়ির "কারখানার সেটিং" — কোন যন্ত্রাংশ লাগানো (টুল), কোন নির্দেশিকা (instructions), কোন ইঞ্জিন মোড (settings)। এগুলো গাড়ি বানানোর সময় (এজেন্ট তৈরি) একবার ঠিক হয়। Lifecycle hook হলো চলার সময়ের "সেন্সর" — প্রতিটি মোড়ে (মডেল রিকোয়েস্ট, টুল কল) এরা দেখে, দরকারে বদলায় বা থামায়।

///

নিজস্ব capability ক্লাস সাধারণ ক্লাস বা dataclass হতে পারে। ভাগ করা metadata attribute — [`id`][pydantic_ai.capabilities.AbstractCapability.id], [`description`][pydantic_ai.capabilities.AbstractCapability.description] আর [`defer_loading`][pydantic_ai.capabilities.AbstractCapability.defer_loading] — সবসময়-চালু capability-র জন্য capability অবজেক্টে ঐচ্ছিক ঘোষণা। সেখানে `id` বাদ দিলে, Pydantic AI ক্লাসের নাম থেকে একটি রান-স্থানীয় id তৈরি করে আর রানের ভেতরে নকলগুলো আলাদা করে। Deferred capability-র একটি স্পষ্ট স্থিতিশীল `id` লাগে।

যে capability একটি একক স্থির বিষয় কভার করে, সেগুলো এর বদলে একটি স্থিতিশীল ডিফল্ট `id` ঘোষণা করে — বিল্ট-ইন [`WebSearch`][pydantic_ai.capabilities.WebSearch] ব্যবহার করে `'web_search'`, [`Thinking`][pydantic_ai.capabilities.Thinking] ব্যবহার করে `'thinking'`, ইত্যাদি — যাতে [durable execution](../durable_execution/overview.md) এরা কী দেয় তা চিনতে পারে, আপনাকে এমন কিছুর নাম না দিতে হয় যা আপনি কখনো তৈরিই করেননি। আপনার নিজের capability একইভাবে একক হলে একে একটি ডিফল্ট `id` দিন।

যেহেতু id স্থির, এমন দুটি একটি id-র নিচে মিলিত হতে পারে, আর এর অর্থ নির্ভর করে তারা কোথা থেকে এসেছে তার ওপর।

**একই এজেন্টে দুটি** হলো একটি কনফিগারেশন দুবার বলা, তাই এরা ফিল্ড ধরে ধরে মেলে: শুধু একটি যে মান বলে তা রাখা হয়, আর দুটোই যে মান বলে তাতে পরেরটি নেওয়া হয়। এটাই দুটি প্যাকেজ করা capability-কে প্রত্যেকে একটি `WebSearch` আনতে আর এজেন্টকে দুই সেট domain-এই পৌঁছাতে দেয়। ডিফল্ট `id` নিজে ছাড়া ঘোষণা করার কিছু নেই — একটি লেখা *মানেই* এই ঘোষণা যে একটি এজেন্টের এমন একটি আছে:

⟦CODE1⟧

যখন দুটি instance একটি কনফিগারেশনের দুটি বিবৃতি নয় বরং দুটি *পরিচয়* — দুটি অ্যাকাউন্ট, দুটি credential — তখন একটি স্থির ডিফল্ট `id` ভুল রূপ, কারণ এদের মেলালে একটি নিঃশব্দে বাদ পড়বে। এর বদলে যা এদের আলাদা করে তা থেকে `id` তৈরি করুন: দুটি পরিচয় তখন দুটি id বহন করে আর দুটি capability থাকে, আর একটি id-র নিচে দুটি একটি সত্যিকারের ভুল যা জানানো হয়। [`MCP`][pydantic_ai.capabilities.MCP] এর সার্ভারের host আর শেষ path অংশ থেকে একটি তৈরি করে, তাই শুধু port বা আগের একটি path অংশে ভিন্ন সার্ভারের তবুও আলাদা স্পষ্ট `id` লাগে।

[`combine`][pydantic_ai.capabilities.AbstractCapability.combine] override করুন শুধু তখনই যখন জোড়ায় ফিল্ড মেলানোর চেয়ে বেশি কিছু লাগে — ধরুন একটি বাজেট যা দুটি মানের *ছোটটি* নেওয়া উচিত।
ডিফল্ট merge শুধু dataclass ফিল্ড দেখে, তাই একটি স্থির ডিফল্ট `id` আর instance কনফিগারেশনসহ একটি সাধারণ ক্লাসকে অবশ্যই `combine` override করতে হবে; অন্যথায় পুনরাবৃত্ত instance ওই কনফিগারেশন নিঃশব্দে বাদ না দিয়ে exception তোলে। শুরুর underscore এটি বদলায় না: যা গুরুত্বপূর্ণ তা হলো merge attribute-টি গুনতে পারে কিনা, এটি private কিনা নয়।

ওই ফিল্ড থেকে আপনি যে state *তৈরি* করেন তা ব্যতিক্রম, আর `cached_property` দিয়ে সেটা বলা হয়। মেলানো cache করা মান ফেলে দেয়, তাই পরের পড়া মেলানো ফিল্ডের বিপরীতে এটি আবার হিসাব করে — যে উত্তর `__post_init__` দিতে পারে না, কারণ মেলানো ইচ্ছে করে এটি আবার চালায় না। যে state-কে একটি ফিল্ড হতে হয়, তা আপনার নিজের `combine`-এ আবার হিসাব হয়।

**একটি রানের জন্য দেওয়া একটি capability** এর এজেন্ট-স্তরের সমনামীকে পুরোপুরি override করে — `agent.run(capabilities=[Thinking(effort='high')])` এজেন্টের `Thinking`-এর সাথে না মিলে এটি বদলে দেয়। একটি রান বলে *এই* রান কী করে, তাই মেলালে রান যে এজেন্ট-স্তরের সেটিং বদলাতে চেয়েছিল তা টিকে যেত, আর একটি এজেন্ট-স্তরের allow-list রানকে যে বাধা আরোপ করতে দেওয়া হয়েছিল তা প্রশস্ত করত। স্তর জুড়ে `combine` জিজ্ঞেস করা হয় না।
সম্পর্কহীন capability ক্লাস স্তর জুড়ে একটি `id` ভাগ করতে পারে না। একটি স্বচ্ছ wrapper যা এর মোড়ানো capability-র `id` রাখে, যেমন `prefix_tools()`, স্তর জুড়ে সেই capability বদলাতে পারে; এটি ভিন্ন wrapper ক্লাসকে একটি স্তরের ভেতরে মিলতে দেয় না।

সমাধান না করে দুটি রাখতে, প্রতিটিকে একটি আলাদা `id` দিন, বা তৈরি-আর-আলাদা-করা id-তে ফিরে যেতে `id=None` দিন। ডিফল্ট ঘোষণা করে না এমন একটি capability-তে আপনি যে `id` দেন তা আপনার বাছা নাম, তাই একই একটি দুবার দিলে মেলানোর বদলে সংঘর্ষ হিসেবে জানানো হয়।

একটি সীমা: একটি [native tool](../native-tools.md) দেওয়া একটি capability-র জন্য, এই পথগুলো নেটিভ টুলের নিজস্ব `id` বিলীন করে না। একটি `WebSearch`-এর ভিন্নভাবে কনফিগার করা দুটি নকল তবুও native-tool-id সংঘর্ষ তোলে, আপনি capability-গুলোকে আলাদা `id` দিন বা `id=None` — শুধু অভিন্ন কনফিগারেশন এটি এড়ায়।

/// info | এক নজরে: একই `id`-এর দুটি capability

| কোথায় | কী ঘটে |
|--------|--------|
| একই এজেন্টে, স্থির ডিফল্ট `id` (যেমন দুটি `WebSearch`) | ফিল্ড ধরে মেলে; দুটোতে থাকা মানে পরেরটি জেতে |
| এজেন্টে একটি, রানে (`run(capabilities=...)`) আরেকটি | রানেরটি পুরোপুরি বদলে দেয়, মেলে না |
| আপনার নিজের বাছা একই `id` দুবার | সংঘর্ষ — error |
| দুটি রাখতে চান | আলাদা `id` দিন, বা `id=None` |

///

⟦CODE2⟧

আপনার নিজের কনফিগারেশন ফিল্ড বা ভাগ করা metadata ফিল্ডের জন্য তৈরি constructor প্যারামিটার চাইলে একটি dataclass ব্যবহার করুন:

⟦CODE3⟧

আপনি একটি নিজস্ব `__init__` সংজ্ঞায়িত করলে, শুধু যে metadata প্রকাশ করতে চান তা সেট করুন। কোনো `super().__init__()` বা `__post_init__()` প্রয়োজনীয়তা নেই:

⟦CODE4⟧

[`defer_loading=True`](on-demand.md) হলে, একটি স্থিতিশীল স্পষ্ট `id` দিন; history replay এর ওপর নির্ভর করে, আর Pydantic AI একটি ছাড়া deferred capability প্রত্যাখ্যান করে। সবসময়-চালু capability-র জন্য, `id` বাদ দিলে তবুও ক্লাসের নাম থেকে একটি রান-স্থানীয় id তৈরি হয়।

## Dependency-র টাইপ { #typing-dependencies }

[`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] এজেন্টের dependency টাইপে generic — `AbstractCapability[MyDeps]` মানে capability-র hook একটি `RunContext[MyDeps]` পায়। capability যেকোনো dependency টাইপের সাথে কাজ করলে `AbstractCapability[Any]` ব্যবহার করুন, বা dependency ফিল্ডে প্রবেশ করতে হলে একটি নির্দিষ্ট টাইপ:

⟦CODE5⟧

## টুল দেওয়া { #providing-tools }

টুল দেওয়া একটি capability [`get_toolset`][pydantic_ai.capabilities.AbstractCapability.get_toolset] থেকে একটি [toolset](../toolsets.md) ফেরত দেয়। এটি আগে-তৈরি একটি [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] instance হতে পারে, বা একটি callable যা [`RunContext`][pydantic_ai.tools.RunContext] পেয়ে গতিশীলভাবে একটি ফেরত দেয়:

⟦CODE6⟧

[native tools](../native-tools.md)-এর জন্য, [`AgentNativeTool`][pydantic_ai.tools.AgentNativeTool] instance-এর একটি sequence ফেরত দিতে [`get_native_tools`][pydantic_ai.capabilities.AbstractCapability.get_native_tools] override করুন (যাতে [`AbstractNativeTool`][pydantic_ai.native_tools.AbstractNativeTool] অবজেক্ট আর [`RunContext`][pydantic_ai.tools.RunContext] পাওয়া callable দুটোই অন্তর্ভুক্ত)।

### Toolset মোড়ানো { #toolset-wrapping }

[`get_wrapper_toolset`][pydantic_ai.capabilities.AbstractCapability.get_wrapper_toolset] একটি capability-কে এজেন্টের পুরো গঠিত toolset একটি [`WrapperToolset`](../toolsets.md#changing-tool-execution) দিয়ে মোড়াতে দেয়। এটি টুল দেওয়ার চেয়ে বেশি শক্তিশালী — এটি টুল চালানো ধরতে, logging যোগ করতে, বা সব জায়গায় প্রযোজ্য আচরণ প্রয়োগ করতে পারে।

wrapper সমন্বিত non-output toolset পায় ([`prepare_tools`](#tool-preparation) hook এটি মোড়ানোর পর)। আউটপুট টুল আলাদাভাবে যোগ হয় আর প্রভাবিত হয় না।

⟦CODE7⟧

/// note | মনে রাখুন

`get_wrapper_toolset` non-output *toolset* প্রতি রানে একবার মোড়ায় (toolset গঠনের সময়)। [`prepare_tools`](#tool-preparation) আর [`prepare_output_tools`](#tool-preparation) hook-ও `PreparedToolset` wrapper দিয়ে প্রবাহিত হয়, তাই তিনটিই toolset স্তরে যুক্ত হয় — `get_wrapper_toolset` `prepare_tools`-এর চারপাশে চলে (এটি প্রস্তুত সংজ্ঞা দেখে), আর `prepare_output_tools` আউটপুট toolset স্বাধীনভাবে মোড়ায়।

///

## Instructions দেওয়া { #providing-instructions }

[`get_instructions`][pydantic_ai.capabilities.AbstractCapability.get_instructions] এজেন্টে [instructions](../agent.md#instructions) যোগ করে। যেহেতু এটি এজেন্ট তৈরির সময় একবার ডাকা হয়, গতিশীল মান লাগলে একটি callable ফেরত দিন:

⟦CODE8⟧

{% raw %}Instructions এজেন্টের [dependencies](../dependencies.md)-এর বিপরীতে রেন্ডার করা Handlebars-ধরনের template-এর জন্য [template strings](../agent-spec.md#template-strings) ([`TemplateStr('Hello {{name}}')`][pydantic_ai.template.TemplateStr])-ও ব্যবহার করতে পারে। Python কোডে, IDE autocomplete-এর জন্য সাধারণত [`RunContext`][pydantic_ai.tools.RunContext]-সহ একটি callable পছন্দনীয়।{% endraw %}

একটি [`id`][pydantic_ai.capabilities.AbstractCapability.id]-যুক্ত capability-র instructions মডেলে পৌঁছায় তাদের নিজস্ব [instruction part](../agent.md#instruction-parts) হিসেবে, `'capability:<capability id>'` দিয়ে চিহ্নিত — আক্ষরিক আর হিসাব করা দুটোই, তাই যে অ্যাপ্লিকেশন ওই key override করে সে capability মডেলকে যা বলে তার সবকিছু নিয়ন্ত্রণ করে। একটি অংশকে আলাদাভাবে চিহ্নিতযোগ্য করতে, [`@capability.instructions(name=...)`][pydantic_ai.capabilities.Capability.instructions] দিয়ে এর নাম দিন, যা এটিকে `'capability:<capability id>:<name>'` হিসেবে key করে। `id` ছাড়া একটি capability-র কোনোটির জন্য key নেই।

### কথোপকথনের মাঝে বদলানো instructions { #instructions-that-change-during-a-conversation }

একটি capability-র instructions একটি কথোপকথনের মাঝপথে বদলালে, আমরা সুপারিশ করি instruction prefix নতুন করে না লিখে পরিবর্তনগুলো ইতিহাসে [যুক্ত](../agent.md#appending-instruction-changes) করতে: prefix, আর এর পেছনে cache করা কথোপকথন, একই থাকে, প্রতিটি পরিবর্তনে ব্লকের পুরো নতুন লেখা ইতিহাসে যোগ হওয়ার মূল্যে। এর জন্য capability-র একটি `id` লাগে, আর লেখাটি আপনার নিয়ন্ত্রণের state থেকে আসতে হবে: [অবিশ্বস্ত লেখা instructions-এর বাইরে রাখুন](../agent.md#untrusted-instruction-text)।

রানের মাঝে বদলানো লেখার জন্য, `get_instructions()` থেকে `on_change='append'`-সহ একটি [`InstructionPart`][pydantic_ai.messages.InstructionPart] ফেরত দিন। এজেন্ট তৈরির সময় এটি পড়া হয় আর পুনর্ব্যবহৃত হয়, শুধু সেই রান ছাড়া যেখানে [`for_run`](#per-run-state-isolation) একটি প্রতিস্থাপন ফেরত দেয়, যা আবার পড়া হয়। তাই যে capability `for_run` রানের dependency থেকে আবার তৈরি করে তা এক রান থেকে পরের রানে এটি বদলাতে পারে:

⟦CODE9⟧

1. শুধু একটি নির্দিষ্ট মান-সেটের একটিই instructions-এ পৌঁছায়, কখনো মুক্ত লেখা নয়: দেখুন [keep untrusted text out of instructions](../agent.md#untrusted-instruction-text)।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

একটি রানের মাঝে বদলানো লেখার জন্য, যেমন একটি টুল হালনাগাদ করে এমন state, `get_instructions()` থেকে একটি callable ফেরত দিন যা `InstructionPart(..., name=..., on_change='append')` ফেরত দেয়, যেমন [current page উদাহরণে](../agent.md#appending-instruction-changes), বা capability-টি [`Capability`][pydantic_ai.capabilities.Capability]-এর ওপর তৈরি করে [`@capability.instructions(name=..., on_change='append')`][pydantic_ai.capabilities.Capability.instructions] দিয়ে ফাংশনটি নিবন্ধন করুন।

## Model settings দেওয়া { #providing-model-settings }

[`get_model_settings`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] [model settings](../agent.md#model-run-settings) একটি dict হিসেবে বা প্রতি-step সেটিংয়ের জন্য একটি callable হিসেবে ফেরত দেয়।

যখন model settings প্রতি step-এ বদলাতে হয় — যেমন শুধু retry-তে thinking চালু করা, বা একটি টুল ডাকা না হওয়া পর্যন্ত একটি নির্দিষ্ট [`tool_choice`](../tools-advanced.md#dynamic-tool-choice-via-capabilities) বাধ্য করা — একটি callable ফেরত দিন:

⟦CODE10⟧

callable একটি [`RunContext`][pydantic_ai.tools.RunContext] পায়, যেখানে `ctx.model_settings`-এ এই capability-র আগে মীমাংসিত সব স্তরের মেলানো ফল থাকে (মডেলের ডিফল্ট আর এজেন্ট-স্তরের সেটিং)।

## মডেল বাছাই { #selecting-the-model }

মডেল বাছাই যখন একটি বড় নিজস্ব capability-র একটি অংশ, তখন [`get_model()`][pydantic_ai.capabilities.AbstractCapability.get_model] override করুন। একটি [`Model`][pydantic_ai.models.Model], একটি model ID string, বা [`ModelSelectionContext`][pydantic_ai.models.ModelSelectionContext] নেওয়া একটি sync/async callable ফেরত দিন। এই উদাহরণ প্রতিটি রিকোয়েস্ট step-এ dependency থেকে একটি মডেল বাছে:

⟦CODE11⟧

[`get_model()`][pydantic_ai.capabilities.AbstractCapability.get_model] একটি synchronous কনফিগারেশন মেথড, কিন্তু এর ফেরত দেওয়া [`ModelSelector`][pydantic_ai.capabilities.ModelSelector] synchronous বা asynchronous হতে পারে। [`ModelSelectionContext`][pydantic_ai.models.ModelSelectionContext] [`RunContext`][pydantic_ai.tools.RunContext] থেকে আলাদা, কারণ একটি সম্পূর্ণ run context-এর জন্য বর্তমানে বাছা হচ্ছে সেই মডেলটি লাগে। এতে থাকে dependency, রিকোয়েস্ট step, রানের prompt, বাছা মডেলে যে বার্তা পাঠানো হবে (পাঠানো হচ্ছে সেই রিকোয়েস্ট দিয়ে শেষ), usage, রানের আউটপুট retry সংখ্যা আর বাজেট, আর এর usage limit, deadline, `run_id` আর `conversation_id`। `get_model()` নিজে সস্তা রাখুন; I/O একটি async selector-এ করুন।

`get_model()` থেকে সরাসরি ফেরত দেওয়া একটি মডেল বা model ID প্রতি রানে একবার মীমাংসা হয়। `get_model()` থেকে ফেরত দেওয়া একটি selector প্রতিটি যৌক্তিক মডেল রিকোয়েস্ট step-এর আগে মূল্যায়িত হয়।

একটি capability-র মডেল বসে একটি কল-সাইট `run(model=...)` আর্গুমেন্ট আর একটি রান-স্তরের `spec=` মডেলের নিচে, আর এজেন্ট constructor-এর মডেলের ওপরে। সর্বোচ্চ থেকে সর্বনিম্ন অগ্রাধিকার:

`run()`/`iter()` আর্গুমেন্ট › রান `spec=` মডেল › capability `get_model()` › এজেন্ট constructor।

একটি [`override(model=...)`][pydantic_ai.agent.AbstractAgent.override] তবুও এদের সবার ওপর জেতে। একটি স্পষ্ট মডেল capability বাছাই পুরোপুরি এড়িয়ে যায়।

পরের মডেল অবদান আগেরগুলোকে override করে। [`for_run()`][pydantic_ai.capabilities.AbstractCapability.for_run] capability অপরিবর্তিত রাখলে, এর bootstrap বাছাই step এক-এ পুনর্ব্যবহৃত হয়; এটি ভিন্ন selector-সহ একটি প্রতিস্থাপন ফেরত দিলে, সেই selector একটি নতুন step-এক বাছাই করে।

Fallback বাছাইয়ের পরিপূরক: রিকোয়েস্ট ব্যর্থতা অন্য একটি মডেলে retry করা উচিত হলে একটি কনফিগার করা [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] ফেরত দিন।

## Model ID মীমাংসা { #resolving-model-ids }

একটি অ্যাপ্লিকেশন-নির্দিষ্ট string-এর নিজস্ব provider তৈরি, credential বা registry খোঁজা লাগলে [`resolve_model_id()`][pydantic_ai.capabilities.AbstractCapability.resolve_model_id] override করুন। মডেল বাছাইয়ের বিপরীতে, মীমাংসায় প্রথমটি জেতে: capability ক্রমানুসারে চেষ্টা করা হয়, আর প্রতিটি resolver `None` ফেরত দিলে তবেই সাধারণ [`infer_model()`][pydantic_ai.models.infer_model] আচরণ ব্যবহৃত হয়।

⟦CODE12⟧

[`for_agent()`][pydantic_ai.capabilities.AbstractCapability.for_agent] পর্যন্ত constructor ID একটি string থাকে, তাই একটি বাঁধা capability একটি resolver বসাতে পারে, ডিফল্ট অনুমান আগে ভিন্ন কনফিগারেশন বা credential দিয়ে একটি provider তৈরি না করেই।

মীমাংসার ফল একটি রানের সময়কাল জুড়ে model ID আর resolver tree দিয়ে cache হয়। একটি প্রতি-step selector আবার একই string ফেরত দিলে, Pydantic AI resolver আবার না ডেকে একই মডেল, provider আর client পুনর্ব্যবহার করে। পরের একটি step-এ ইচ্ছে করে ভিন্নভাবে মীমাংসা করতে, একটি ভিন্ন ID বাছুন বা selector থেকে সরাসরি একটি [`Model`][pydantic_ai.models.Model] instance ফেরত দিন।

## মডেল বাছাইয়ের lifecycle আর সীমাবদ্ধতা { #model-selection-lifecycle-and-limitations }

Bootstrap মীমাংসা `for_agent()` বাঁধার পরে কিন্তু `for_run()`-এর আগে capability tree ব্যবহার করে, কারণ প্রথম মডেল মীমাংসা করাই একটি পূর্ণ [`RunContext`][pydantic_ai.tools.RunContext] সম্ভব করে। `for_run()` একটি প্রতিস্থাপন capability ফেরত দিলে, step এক বা পরের step-এর জন্য বাছা string সেই প্রতিস্থাপনের resolver শৃঙ্খল ব্যবহার করে। `for_run()` capability অপরিবর্তিত রাখলে, ইতিমধ্যে মীমাংসিত bootstrap মডেল step এক-এ পুনর্ব্যবহৃত হয়।

মডেল বাছাই আর মীমাংসা আগ্রহী (eager) hook, তাই deferred capability এগুলো দেয় না, লোড হওয়ার পরেও। Run-spec capability bootstrap-এর সময় জানা থাকে আর প্রথম মডেল দিতে পারে। একটি [`CapabilityFunc`][pydantic_ai.capabilities.CapabilityFunc], বা আরেকটি capability যার মডেল শুধু `for_run()` দিয়ে আসে, একটি বিদ্যমান bootstrap মডেল চায়, কারণ `for_run()` একটি পূর্ণ `RunContext` পায়; এটি step এক থেকে সেই মডেল বদলাতে পারে, কিন্তু একটি মডেল-হীন এজেন্টকে bootstrap করতে পারে না। একটি deferred capability লোডের পর একটি নতুন মডেল বাছা আপনার অ্যাপ্লিকেশনের জন্য কাজের হলে, দয়া করে কাঙ্ক্ষিত step আর ধারাবাহিকতার অর্থ বর্ণনা করে একটি issue খুলুন।

গতিশীল বাছাই বর্তমানে durable execution capability সমর্থন করে না। Durable রানের চালানোর আগে model ID নিবন্ধিত থাকা লাগে আর replay বা রান-জুড়ে আবার চালানোর সময় একই বাছা মডেল আবার তৈরি করতে হয়। durable execution-এর জন্য একটি স্পষ্ট নিবন্ধিত মডেল দিন। একটি আলাদা সাধারণ রানে একটি স্থগিত provider রিকোয়েস্ট আবার চালাতেও একটি স্পষ্ট মডেল লাগে, যখন আগের মডেল একটি selector থেকে এসেছিল।

## কনফিগারেশন মেথডের রেফারেন্স { #configuration-methods-reference }

| মেথড | Return type | উদ্দেশ্য |
|---|---|---|
| [`get_toolset()`][pydantic_ai.capabilities.AbstractCapability.get_toolset] | [`AgentToolset`][pydantic_ai.toolsets.AgentToolset] `| None` | নিবন্ধনের একটি [toolset](../toolsets.md) (বা [dynamic toolsets](../toolsets.md#dynamically-building-a-toolset)-এর জন্য একটি callable) |
| [`get_native_tools()`][pydantic_ai.capabilities.AbstractCapability.get_native_tools] | `Sequence[`[`AgentNativeTool`][pydantic_ai.tools.AgentNativeTool]`]` | নিবন্ধনের [Native tools](../native-tools.md) (callable-সহ) |
| [`get_wrapper_toolset()`][pydantic_ai.capabilities.AbstractCapability.get_wrapper_toolset] | [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] `| None` | [এজেন্টের গঠিত toolset মোড়ানো](#toolset-wrapping) |
| [`get_instructions()`][pydantic_ai.capabilities.AbstractCapability.get_instructions] | [`AgentInstructions`][pydantic_ai.agent.AgentInstructions] `| None` | [Instructions](../agent.md#instructions) (স্থির string, [`InstructionPart`][pydantic_ai.messages.InstructionPart], [template strings](../agent-spec.md#template-strings), বা callable) |
| [`get_model_settings()`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] | [`AgentModelSettings`][pydantic_ai.agent.AgentModelSettings] `| None` | [Model settings](../agent.md#model-run-settings) dict, বা প্রতি-step সেটিংয়ের জন্য একটি callable |
| [`get_workspace()`][pydantic_ai.capabilities.AbstractCapability.get_workspace] | [`WorkspaceBackend`][pydantic_ai.workspaces.WorkspaceBackend] `| None` | রানের [workspace](../workspace.md#supplying-a-workspace-from-a-capability): `ref`-এর জন্য একটি backend (`ref` `None` হলে নতুন), বা আপনি চেনেন না এমন একটি `ref`-এর জন্য `None`। Synchronous, কোনো I/O নয়। কয়েকটি workspace capability থাকলে, প্রথম যেটি একটি ফেরত দেয় সেটি জেতে |
| [`get_model()`][pydantic_ai.capabilities.AbstractCapability.get_model] | [`AgentModel`][pydantic_ai.capabilities.AgentModel] `| None` | স্থির বা প্রতি-step [model selection](#selecting-the-model) |
| [`resolve_model_id()`][pydantic_ai.capabilities.AbstractCapability.resolve_model_id] | [`Model`][pydantic_ai.models.Model] `| None` | এজেন্ট আর রান dependency দিয়ে [একটি বাছা model ID মীমাংসা](#resolving-model-ids) |
| [`get_default_run_id()`][pydantic_ai.capabilities.AbstractCapability.get_default_run_id] | `str | None` | একটি ছাড়া শুরু হওয়া রানের জন্য একটি replay-স্থিতিশীল `run_id` |
| [`get_default_conversation_id()`][pydantic_ai.capabilities.AbstractCapability.get_default_conversation_id] | `str | None` | উত্তরাধিকারসূত্রে পাওয়ার কিছু নেই এমন রানের জন্য একটি replay-স্থিতিশীল `conversation_id` |
| [`get_run_clock()`][pydantic_ai.capabilities.AbstractCapability.get_run_clock] | `Callable[[], datetime] | None` | রানের [deadline](../timeouts.md#bounding-a-whole-run)-এর জন্য একটি replay-নিরাপদ ঘড়ি |
| [`get_run_start_time()`][pydantic_ai.capabilities.AbstractCapability.get_run_start_time] | `datetime | None` | `timeout=` গোনার জন্য একটি replay-স্থিতিশীল শুরুর সময় |

শেষ চারটি আছে [durable execution](../durable_execution/overview.md) engine-এর জন্য, যাদের রান replay হয় আর প্রতিবার একই পরিচয় আর deadline পেতে হয়। কয়েকটি capability একটি মান ফেরত দিলে, শেষে তালিকাভুক্তটি জেতে।

## একটি এজেন্টে বাঁধা { #binding-to-an-agent }

একটি পুনর্ব্যবহারযোগ্য capability-র যে এজেন্টে এটি যুক্ত তা পরীক্ষা করার দরকার হলে [`for_agent()`][pydantic_ai.capabilities.AbstractCapability.for_agent] override করুন। hook-টি [`Agent`][pydantic_ai.Agent] তৈরির সময় একবার চলে, এজেন্টের নিজের মডেল, নাম আর toolset উপলব্ধ হওয়ার পরে আর capability-র অবদান বের করার আগে:

⟦CODE13⟧

`for_agent()` synchronous, কারণ এটি এজেন্ট তৈরির সময় কনফিগারেশন বাঁধে, রানের dependency বা একটি lifecycle context থাকার আগেই। একে I/O-মুক্ত রাখুন; asynchronous রান-নির্দিষ্ট সেটআপ [`for_run()`][pydantic_ai.capabilities.AbstractCapability.for_run]-এ থাকে।

একই capability একাধিক এজেন্টে যুক্ত হতে পারলে মূলটি বদলানোর বদলে একটি নতুন বাঁধা কপি ফেরত দিন। [`CombinedCapability`][pydantic_ai.capabilities.CombinedCapability] আর [`WrapperCapability`][pydantic_ai.capabilities.WrapperCapability] তাদের সন্তানদের কাছে বাঁধা প্রচার করে, আর বাঁধা কপি সব কনফিগারেশন hook-এ অংশ নেয়, `get_model()` আর `resolve_model_id()`-সহ।

প্যারামিটারের টাইপ [`AbstractAgent`][pydantic_ai.agent.AbstractAgent], যাতে পুনর্ব্যবহারযোগ্য capability শুধু বহনযোগ্য এজেন্ট interface-এর ওপর নির্ভর করে আর নিজস্ব এজেন্ট বাস্তবায়নের সাথে সামঞ্জস্যপূর্ণ থাকে। একটি [`WrapperAgent`][pydantic_ai.agent.WrapperAgent] দিয়ে রান এর মোড়ানো এজেন্টকে দেওয়া হয়, তাই Pydantic AI-এর বিল্ট-ইন wrapper capability-কে বাইরের wrapper-এ আবার বাঁধে না।

`for_agent()` constructor মডেল ঠিক সেভাবে দেখে যেভাবে caller দিয়েছে। বিশেষ করে, বাঁধা চলার সময় একটি model ID একটি string থাকে, তাই একটি বাঁধা capability ডিফল্ট অনুমান আগে ভুল কনফিগারেশন বা credential দিয়ে একটি provider তৈরি না করেই `resolve_model_id()` আনতে পারে। বাঁধা capability tree-তে কোনো resolver না থাকলে আর `defer_model_check=False` হলে, বাঁধার পরে সাধারণ মডেল অনুমান ঘটে।

সরাসরি [`run()`][pydantic_ai.agent.AbstractAgent.run]-এ বা একটি run spec দিয়ে দেওয়া capability সেই রানের জন্য bootstrap মডেল বাছাইয়ের আগে একবার বাঁধা হয়। একটি [`CapabilityFunc`][pydantic_ai.capabilities.CapabilityFunc] নিজে রানের আগে বাঁধা হয়; যেহেতু এর ফেরত মান সাধারণত একটি স্বাধীনভাবে পুনর্ব্যবহারযোগ্য capability, সেই মানও এর নিজের `for_run()` ডাকার আগে বাঁধা হয়। বিপরীতে, একটি সাধারণ capability-র [`for_run()`][pydantic_ai.capabilities.AbstractCapability.for_run]-এর ফেরত দেওয়া একটি বিশেষায়িত রান-বাঁধা capability আবার `for_agent()` দিয়ে যায় না।

## Capability-র lifecycle { #capability-lifecycle }

বাঁধার hook ঠিক করে কোন capability একটি রানে অংশ নেয়; lifecycle hook তারপর এর করা কাজ ধরে। উচ্চ-স্তরের ক্রম:

`for_agent()` → bootstrap মডেল বাছাই আর মীমাংসা → `get_workspace()` → `for_run()` → প্রতি-step বাছাই আর প্রস্তুতি → মডেল রিকোয়েস্ট → টুল/আউটপুট প্রক্রিয়া → রান সমাপ্তি

| পর্যায় | Capability-র কাজ | যা উপলব্ধ |
|---|---|---|
| এজেন্ট বাঁধা | [`for_agent()`][pydantic_ai.capabilities.AbstractCapability.for_agent] | এজেন্টের নাম, কাঁচা constructor মডেল, toolset আর অন্য constructor কনফিগারেশন; কোনো রান dependency বা `RunContext` নেই |
| রান bootstrap | [`get_model()`][pydantic_ai.capabilities.AbstractCapability.get_model], তারপর বাছাই একটি string হলে [`resolve_model_id()`][pydantic_ai.capabilities.AbstractCapability.resolve_model_id]; তারপর [`get_workspace()`][pydantic_ai.capabilities.AbstractCapability.get_workspace] | বাছাই/মীমাংসা context দিয়ে dependency, message history, usage আর কম-অগ্রাধিকারের মডেল। `get_workspace()` bootstrap মডেলসহ কিন্তু এখনও টুল ছাড়া একটি `RunContext` পায় |
| রান বাঁধা | [`for_run()`][pydantic_ai.capabilities.AbstractCapability.for_run] | bootstrap মডেলসহ একটি সম্পূর্ণ [`RunContext`][pydantic_ai.tools.RunContext]; একটি রান-পরিসরের প্রতিস্থাপন capability ফেরত দিতে পারে |
| প্রতিটি যৌক্তিক মডেল step | `for_run()`-পরবর্তী মডেল বাছাই/মীমাংসা, model settings, টুল প্রস্তুতি আর বার্তা প্রস্তুতি | বাছা মডেল এর settings, profile-সংবেদনশীল টুল আর মডেল-নির্দিষ্ট বার্তা প্রস্তুতি মূল্যায়নের আগে `RunContext`-এ বসানো হয় |
| মডেল রিকোয়েস্ট আর response | মডেল রিকোয়েস্ট, টুল, আউটপুট, node আর event-stream [hooks](#hooking-into-the-lifecycle) | lifecycle-এ প্রতিটি hook-এর অবস্থানে রিকোয়েস্ট context আর জীবন্ত রান state |
| রান সমাপ্তি | `wrap_run` handler রানের body শেষ করে, দরকারে `on_run_error` উদ্ধার প্রয়োগ করে, তারপর `after_run` চালায়; একটি wrapper handler সংক্ষিপ্ত করে দিতে পারে | চূড়ান্ত ফল বা error, জমা বার্তা আর usage |

`for_run()` মূল capability ফেরত দিলে, bootstrap মডেল বাছাই step এক-এ পুনর্ব্যবহৃত হয়। একটি প্রতিস্থাপন capability step এক-এর জন্য একটি ভিন্ন মডেল বাছতে পারে। একটি যৌক্তিক step-এর ভেতরে continuation polling সেই step-এর বাছা মডেলে আটকানো থাকে।

## Lifecycle-এ hook যুক্ত করা { #hooking-into-the-lifecycle }

Capability সাতটি lifecycle পর্যায়ে hook যুক্ত করতে পারে। প্রতিটি পর্যায়ের একই lifecycle:

```text
wrap_* enter → before_* → operation (on_*_error if it fails) → after_* → wrap_* exit
```

যে `wrap_*` hook এর handler না ডেকে ফেরত দেয়, তা এর ভেতরের সবকিছু বাদ দেয়। [`run_stream()` node hook ভিন্নভাবে সামলায়](#node-hooks)। চারটি hook রূপ:

* **`before_*`** — মূল কাজের আগে মোড়ানো handler-এর ভেতরে চলে, input বদলাতে পারে
* **`after_*`** — মূল কাজ সফল হলে বা `on_*_error` উদ্ধার করলে চলে (উল্টো capability ক্রমে), output বদলাতে পারে
* **`wrap_*`** — পুরো পর্যায়ের lifecycle ঘিরে পূর্ণ middleware নিয়ন্ত্রণ: একটি `handler` callable পায় আর ঠিক করে এটি চালাবে কিনা বা কীভাবে
* **`on_*_error`** — `wrap_*` সীমার ভেতরে মূল কাজের ব্যর্থতা সামলায়, wrapper-রা একটি অ-উদ্ধারকৃত ব্যর্থতা দেখার আগে

একটি সংক্ষিপ্ত-করা wrapper `before_*` বাদ দেয়, policy hook-সহ। বাধ্যতামূলক authorization একটি বাইরের wrapper-এ বা যেকোনো সংক্ষিপ্ত-করা-যায় cache-এর বাইরে রাখুন।

/// tip | উদাহরণ দিয়ে বুঝি

`wrap_*` হলো একটি পেঁয়াজের খোসা: বাইরের খোসা (প্রথম capability) ভেতরেরটাকে ঘিরে রাখে, ভেতরেরটা আরও ভেতরেরটাকে, আর মাঝখানে আসল কাজ (মডেলকে জিজ্ঞেস বা টুল চালানো)। প্রতিটি খোসা ভেতরে যাওয়ার আগে আর বেরোনোর পরে কিছু করতে পারে — বা ভেতরে না গিয়েই ফিরে আসতে পারে (cache-এর মতো)। এজন্যই বাধ্যতামূলক নিরাপত্তা-যাচাই সবচেয়ে বাইরের খোসায় রাখতে হয়, যাতে কোনো ভেতরের cache তা এড়িয়ে না যায়।

///

/// tip | পরামর্শ

subclass ছাড়াই দ্রুত, অ্যাপ্লিকেশন-স্তরের hook-এর জন্য, এর বদলে [`Hooks`](../hooks.md) capability ব্যবহার করুন।

///

### Run hook { #run-hooks }

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_run`][pydantic_ai.capabilities.AbstractCapability.before_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`) -> None` | একটি রান শুরু হচ্ছে তার শুধু-পর্যবেক্ষণ বিজ্ঞপ্তি |
| [`after_run`][pydantic_ai.capabilities.AbstractCapability.after_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, result: `[`AgentRunResult`][pydantic_ai.run.AgentRunResult]`) -> `[`AgentRunResult`][pydantic_ai.run.AgentRunResult] | চূড়ান্ত ফল বদলানো |
| [`wrap_run`][pydantic_ai.capabilities.AbstractCapability.wrap_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, handler: `[`WrapRunHandler`][pydantic_ai.capabilities.WrapRunHandler]`) -> `[`AgentRunResult`][pydantic_ai.run.AgentRunResult] | পুরো রান lifecycle মোড়ানো |
| [`on_run_error`][pydantic_ai.capabilities.AbstractCapability.on_run_error] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, error: BaseException) -> `[`AgentRunResult`][pydantic_ai.run.AgentRunResult] | রান-body error সামলানো (দেখুন [error hooks](#error-hooks)) |

`wrap_run` error উদ্ধার সমর্থন করে: `handler()`-এর ভেতরে রান-body ব্যর্থতা উদ্ধারের প্রথম সুযোগ পায় `on_run_error`। error অ-উদ্ধারকৃত থেকে `handler()` exception তুললে, `wrap_run` এটি ধরে এর বদলে একটি ফল ফেরত দিতে পারে। `on_run_error` শুধু রান-body ব্যর্থতা দেখে: যেকোনো capability-র `before_run` বা `after_run` থেকে একটি exception `wrap_run`-এ পৌঁছায় কিন্তু `on_run_error`-এ নয়, তাই `before_run`-এ নেওয়া resource `wrap_run` থেকে ছাড়ুন, `handler()`-এর চারপাশে একটি `try`/`finally`-তে। এগুলো [`for_run`][pydantic_ai.capabilities.AbstractCapability.for_run]-এ নেবেন না, যা যেকোনো run hook-এর আগে চলে। এটি [`agent.run()`][pydantic_ai.agent.AbstractAgent.run], [`agent.iter()`][pydantic_ai.agent.Agent.iter] আর [realtime sessions](../realtime/capabilities.md)-এর সাথে কাজ করে। একটি realtime session একটি রান, তাই চারটি hook-ই এর চারপাশে একবার চলে, session বন্ধ হলে `wrap_run`-এর handler মীমাংসা হয়। আচরণ ভাগ করতে [`ctx.realtime`][pydantic_ai.tools.RunContext.realtime] যাচাই করুন, আর জীবন্ত session-এর সাথে কাজ করতে [`ctx.realtime_session`][pydantic_ai.tools.RunContext.realtime_session] ব্যবহার করুন (session সংযুক্ত হলে সেট হয়)।

/// warning | আপনার শুরু করা task গুটিয়ে ফেলা

একটি রান বাতিল হয় — [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel], একটি [`CancellationToken`][pydantic_ai.CancellationToken], একটি `asyncio.wait_for` timeout, বা একটি ঘেরা task group দিয়ে — এটি চালানো একক asyncio task বাতিল করে। রান inline-এ যে কাজ `await` করে তা নিজে থেকে `CancelledError` পায়; আপনি `asyncio.create_task(...)` দিয়ে নিজে শুরু করা একটি task একটি **ভিন্ন** task-এ চলে আর **পায় না**, তাই task শুরু করা একটি capability-কে নিজেই সেগুলো গুটাতে হবে।

structured concurrency পছন্দ করুন (`async with`-সহ [`anyio.create_task_group()`](https://anyio.readthedocs.io/en/stable/tasks.html)): রানের বাতিল `async with`-এর মধ্য দিয়ে প্রবাহিত হয় আর পরিসর থেকে বেরোনোর সময় সন্তানরা বাতিল হয়, কোনো হাতে-পরিষ্কার ছাড়াই। আপনি কাঁচা task রাখলে, `wrap_run`-এ একটি `try`/`finally`-তে সেগুলো বাতিল আর নিঃশেষ করুন (প্রথমে প্রতিটি `task.cancel()` দিন, তারপর একটি একক `await asyncio.gather(*tasks, return_exceptions=True)`), আর সেই গুটানো `anyio.CancelScope(shield=True)`-এ মুড়ুন যাতে রান ইতিমধ্যে বাতিল হওয়ার সময়ও এটি শেষ হয়। একটি কাঁচা `task.cancel()` একটি shield করা পরিসরও ভেদ করতে পারে, তাই যে কাজ যেকোনো অবস্থায় শেষ হতে হবে, সেটি নিজের task-এ রেখে [`asyncio.shield()`](https://docs.python.org/3/library/asyncio-task.html#asyncio.shield) দিয়ে রক্ষা করুন (task-এর একটি শক্ত রেফারেন্স ধরে রেখে) — task সরাসরি await করলে সাহায্য হতো না, কারণ রানের task বাতিল করলে `CancelledError` এটি যে task await করছে তাতে প্রচারিত হয়। একটি background task-এ আপনার চালু করা একটি sub-agent রানও একইভাবে আপনাকেই বাতিল আর নিঃশেষ করতে হবে — শুধু আপনি inline-এ `await` করা sub-agent আপনার জন্য গুটানো হয়।

///

/// note | বাতিল পর্যবেক্ষণ

একটি বাতিল একটি capability-তে পৌঁছায় একটি `asyncio.CancelledError` হিসেবে: একটি `wrap_*` hook-এর `handler()` await দিয়ে (`await handler(...)`-এর চারপাশে এটি ধরুন), বা রানের শেষ ফানেল [`on_run_error`][pydantic_ai.capabilities.AbstractCapability.on_run_error]-এ, যার `error` একটি `BaseException`। এটি উদ্ধার-কেন্দ্রিক `Exception`-টাইপের hook-এ — [`on_tool_execute_error`][pydantic_ai.capabilities.AbstractCapability.on_tool_execute_error], [`on_node_run_error`][pydantic_ai.capabilities.AbstractCapability.on_node_run_error], [`on_model_request_error`][pydantic_ai.capabilities.AbstractCapability.on_model_request_error] — **পৌঁছায় না**, কারণ একটি বাতিল একটি চূড়ান্ত নিয়ন্ত্রণ-সংকেত, সেই step-এর এমন ব্যর্থতা নয় যা থেকে আপনি উদ্ধার করতে পারেন।

বাতিল চূড়ান্ত: একটি hook এটি পর্যবেক্ষণ করে পরিষ্কার করতে পারে, কিন্তু রান উদ্ধারে একটি ফল ফেরত দেওয়া কাজ করে না। রান পরের step সীমায় বাতিল আবার জোর দিয়ে প্রয়োগ করে।

///

### Node hook { #node-hooks }

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_node_run`][pydantic_ai.capabilities.AbstractCapability.before_node_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, node: `[`AgentNode`][pydantic_ai.capabilities.AgentNode]`) -> `[`AgentNode`][pydantic_ai.capabilities.AgentNode] | চালানোর আগে node পর্যবেক্ষণ বা বদলানো |
| [`after_node_run`][pydantic_ai.capabilities.AbstractCapability.after_node_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, node: `[`AgentNode`][pydantic_ai.capabilities.AgentNode]`, result: `[`NodeResult`][pydantic_ai.capabilities.NodeResult]`) -> `[`NodeResult`][pydantic_ai.capabilities.NodeResult] | ফল বদলানো (পরের node বা [`End`][pydantic_graph.basenode.End]) |
| [`wrap_node_run`][pydantic_ai.capabilities.AbstractCapability.wrap_node_run] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, node: `[`AgentNode`][pydantic_ai.capabilities.AgentNode]`, handler: `[`WrapNodeRunHandler`][pydantic_ai.capabilities.WrapNodeRunHandler]`) -> `[`NodeResult`][pydantic_ai.capabilities.NodeResult] | পুরো node lifecycle মোড়ানো |
| [`on_node_run_error`][pydantic_ai.capabilities.AbstractCapability.on_node_run_error] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, node: `[`AgentNode`][pydantic_ai.capabilities.AgentNode]`, error: Exception) -> `[`NodeResult`][pydantic_ai.capabilities.NodeResult] | মূল node-চালানোর error সামলানো (দেখুন [error hooks](#error-hooks)) |

[`wrap_node_run`][pydantic_ai.capabilities.AbstractCapability.wrap_node_run] [agent graph](../agent.md#iterating-over-an-agents-graph)-এর node ধরতে পারে ([`UserPromptNode`][pydantic_ai.agent.UserPromptNode], [`ModelRequestNode`][pydantic_ai.agent.ModelRequestNode], [`CallToolsNode`][pydantic_ai.agent.CallToolsNode])। node-এর পালাবদল পর্যবেক্ষণ, প্রতি-step logging যোগ, বা graph-এর অগ্রগতি বদলাতে এটি override করুন:

রান যেভাবেই চালানো হোক, node hook চলে: [`agent.run()`][pydantic_ai.agent.AbstractAgent.run], [`agent_run.next()`][pydantic_ai.run.AgentRun.next], আর [`agent.iter()`][pydantic_ai.agent.Agent.iter]-এর ওপর `async for node in agent_run:` — সবগুলো একই পথ নেয়।

/// note | মনে রাখুন

[`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] streaming-এর চারপাশে node lifecycle ভাগ করে: stream খোলার আগে `before_node_run` চলে। অ-চূড়ান্ত stream করা node-এর জন্য, `wrap_node_run` শুধু graph-এর অগ্রগতি ঘিরে রাখে; `on_node_run_error` আর `after_node_run` এর বাইরে চলে। চূড়ান্ত stream করা `ModelRequestNode` `wrap_node_run` আর `after_node_run` বাদ দেয়, কারণ `run_stream()` stream-এর মাঝে চূড়ান্ত আউটপুট পাওয়া মাত্রই ফেরত আসে। একটি hook-এর প্রতিটি node-এর জন্য পরিষ্কার বা ফল নতুন করে লেখা দরকার হলে, `agent.run()` বা `agent.iter()` ব্যবহার করুন।

///

⟦CODE14⟧

আপনি graph-এর অগ্রগতি বদলাতেও `wrap_node_run` ব্যবহার করতে পারেন — যেমন, প্রতি রানে মডেল রিকোয়েস্টের সংখ্যা সীমিত করা:

⟦CODE15⟧

agent graph আর এর node টাইপ সম্পর্কে আরও জানতে দেখুন [Iterating Over an Agent's Graph](../agent.md#iterating-over-an-agents-graph)।

### Model request hook { #model-request-hooks }

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_model_request`][pydantic_ai.capabilities.AbstractCapability.before_model_request] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, request_context: `[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext]`) -> `[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext] | মডেল কলের আগে বার্তা, settings, প্যারামিটার বা মডেল বদলানো |
| [`after_model_request`][pydantic_ai.capabilities.AbstractCapability.after_model_request] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, request_context: `[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext]`, response: `[`ModelResponse`][pydantic_ai.messages.ModelResponse]`) -> `[`ModelResponse`][pydantic_ai.messages.ModelResponse] | মডেলের response বদলানো |
| [`wrap_model_request`][pydantic_ai.capabilities.AbstractCapability.wrap_model_request] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, request_context: `[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext]`, handler: `[`WrapModelRequestHandler`][pydantic_ai.capabilities.WrapModelRequestHandler]`) -> `[`ModelResponse`][pydantic_ai.messages.ModelResponse] | পুরো model-request lifecycle মোড়ানো |
| [`on_model_request_error`][pydantic_ai.capabilities.AbstractCapability.on_model_request_error] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, request_context: `[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext]`, error: Exception) -> `[`ModelResponse`][pydantic_ai.messages.ModelResponse] | মূল মডেল-কলের error সামলানো (দেখুন [error hooks](#error-hooks)) |

[`ModelRequestContext`][pydantic_ai.models.ModelRequestContext] `model`, `messages`, `model_settings` আর `model_request_parameters`-কে একটি একক অবজেক্টে একত্র করে, signature-কে ভবিষ্যৎ-নিরাপদ করে। একটি নির্দিষ্ট রিকোয়েস্টের জন্য মডেল বদলাতে, `request_context.model` একটি ভিন্ন [`Model`][pydantic_ai.models.Model] instance-এ সেট করুন। আপনাকে দেওয়া context বদলান, বা এর একটি `dataclasses.replace()` কপি ফেরত দিন — যেকোনোভাবে, `model_id` আর `streaming` বহন হয়।

একটি wrapper-এর handler যে response ফেরত দেয় তা অগত্যা সেটি নয় যার জন্য provider bill করেছে: একটি ভেতরের hook হয়তো এটি বদলেছে বা প্রত্যাখ্যান করেছে। usage হিসাব করতে, [`ctx.usage`][pydantic_ai.tools.RunContext.usage] পড়ুন, যাতে provider bill করেছে এমন প্রতিটি response অন্তর্ভুক্ত, একটি hook পরে প্রত্যাখ্যান করেছে এমনটিও।

মডেল কল পুরোপুরি বাদ দিয়ে একটি প্রতিস্থাপন response দিতে, `before_model_request` বা `wrap_model_request` থেকে [`SkipModelRequest(response)`][pydantic_ai.exceptions.SkipModelRequest] তুলুন।

`before_model_request` hook পুরো `request_context.messages` লিস্ট দেখে, `agent.run()`-এ দেওয়া যেকোনো [message history](../message-history.md)-সহ। steering বার্তা আর রিমাইন্ডার কীভাবে যোগ করবেন, আর কীভাবে শুধু একটি রিকোয়েস্ট যা পাঠায় তা বদলাবেন, তা দেখুন [Changing what the model sees](#steering-messages-and-reminders)-এ।

একটি রিকোয়েস্টের [instructions](../agent.md#instruction-parts) বদলাতে, `request_context.model_request_parameters.instruction_parts` নতুন করে লিখুন — মডেলকে সেটিই পাঠানো হয়, আর hook চলার পর message history-তে লেখা [`ModelRequest`][pydantic_ai.messages.ModelRequest] এটি থেকে আবার রেন্ডার হয়, তাই ইতিহাস আর trace দেখায় আসলে কী পাঠানো হয়েছিল। ওই বার্তার `instructions`-এ মান বসালে তা part-গুলোতে ফেরত প্রচারিত হয় না আর মডেলে পৌঁছায় না।

#### মডেল যা দেখে তা বদলানো: steering বার্তা আর রিমাইন্ডার { #steering-messages-and-reminders }

`before_model_request` থেকে, একটি পরিবর্তন কোথায় যায় তা দুটি জিনিস ঠিক করে: মডেল এটি একবার দেখবে নাকি কথোপকথনের বাকি সময়, আর prompt cache আর মডেলের আগের যুক্তি এটি থেকে টিকে থাকবে কিনা।

| আপনি চান | `before_model_request` থেকে | কী ঘটে |
|---|---|---|
| মডেলকে এমন একটি বার্তা দিয়ে পথ দেখাতে যা এটি এখন দেখে আর কথোপকথনে থেকে যায় | [`ctx.enqueue(part)`][pydantic_ai.tools.RunContext.enqueue] | এটি প্রস্তুত হচ্ছে এমন রিকোয়েস্টে আর message history-তে যায়, নিজস্ব একটি [`ModelRequest`][pydantic_ai.messages.ModelRequest] হিসেবে, তাই পরের প্রতিটি রিকোয়েস্টও এটি পাঠায়। |
| মডেলকে এমন কিছু মনে করাতে যা শুধু এই রিকোয়েস্টের জন্য সত্য | `ctx.enqueue(SystemPromptPart(..., scope='request'))` | একটি [request-scoped prompt](../message-history.md#request-scoped-system-prompts): এটি এই রিকোয়েস্টে আর ইতিহাসে যায়। Anthropic এটি একটি turn-পরিসরের system বার্তা (`clear_at`) হিসেবে পাঠায় আর এর রিকোয়েস্টের উত্তর হয়ে গেলে মডেলকে দেখানো বন্ধ করে; অন্যত্র এটি শুধু নিজের রিকোয়েস্টে পাঠানো হয়। |
| মডেলের ট্র্যাক করা উচিত এমন state রাখতে, যেমন একটি todo লিস্ট বা নোট | [`on_change='append'`](#instructions-that-change-during-a-conversation)-সহ [Instructions](#providing-instructions) | প্রতিটি রিকোয়েস্টের জন্য নতুন করে রেন্ডার হয়। একটি পরিবর্তন একটি প্রতিস্থাপন হিসেবে ইতিহাসে যুক্ত হয়, তাই cache করা prefix টিকে থাকে। ডিফল্ট `on_change='rewrite'`-এ, একটি পরিবর্তন instructions-এর পরের সবকিছু cache ছাড়া আবার পাঠায়। |
| শুধু এই রিকোয়েস্ট যা পাঠায় তা বদলাতে: ছাঁটা, ছাঁকা, মুছে ফেলা | `request_context.messages`-এ একটি নতুন লিস্ট বসান | শুধু-রিকোয়েস্ট: ইতিহাস মূলটি রাখে। লিস্টটি নতুন, কিন্তু এর বার্তা আর part ইতিহাসে থাকা সেগুলোই, তাই জায়গাতেই বদলানোর বদলে প্রতিস্থাপন তৈরি করুন, নইলে ইতিহাসও বদলে যায়। |
| ইতিহাস নতুন করে লিখতে, যেমন compaction করে | [`ctx.messages`][pydantic_ai.tools.RunContext.messages]-এর বিষয়বস্তু বদলান (`ctx.messages[:] = ...`), আর এই রিকোয়েস্টে ফল পাঠানো উচিত হলে `request_context.messages`-ও বসান | স্থায়ী: পরের রিকোয়েস্ট নতুন করে লেখা ইতিহাস থেকে শুরু হয়। |

"Request-scoped" আর "request-only" ভিন্ন জিনিস। একটি request-scoped prompt ইতিহাসের একটি part, যা মডেলকে শুধু নিজের রিকোয়েস্টে দেখানো হয়; ইতিহাস এটি রাখে, তাই পরের রিকোয়েস্ট ঠিক তা-ই পাঠায় যা আগেরগুলো পাঠিয়েছিল। একটি request-only পরিবর্তন কখনো ইতিহাসে পৌঁছায়ই না, আর ঠিক এটাই cache করা prefix সরাতে পারে।

`before_model_request`-এ `request_context.messages.append(...)` (বা `extend`, বা `+=`) তবুও বার্তাটি ইতিহাসেও যোগ করে, request-only বার্তা আসার আগে যেমন করত, কিন্তু সেটা অবচিত আর একটি সতর্কবার্তা দেয়। এর বদলে `ctx.enqueue(...)` ব্যবহার করুন।

/// warning | Request-only পরিবর্তন আর prompt cache

একটি request-only পরিবর্তন যা একটি আগের রিকোয়েস্টের ইতিমধ্যে পাঠানো কনটেন্ট বাদ দেয় বা বদলায়, তা cache করা prefix সরায়: provider সেই বিন্দু থেকে সবকিছু আবার প্রক্রিয়া করে, প্রতিবার। যে মডেল তাদের যুক্তিকে হুবহু কথোপকথনের সাথে বাঁধে, যেমন [preserved thinking](https://platform.claude.com/docs/en/build-with-claude/preserved-thinking)-সহ Claude Opus 5.5, Sonnet 5.5 আর Fable 5.1, সেগুলোতে এটি মডেলের আগের যুক্তিও অকেজো করে। এজন্যই প্রতিটি রিকোয়েস্টে যোগ করা একটি রিমাইন্ডার enqueue করা উচিত, যাতে এটি ইতিহাসে থাকে আর পরের প্রতিটি রিকোয়েস্ট এটি অপরিবর্তিত পাঠায়, আর এককালীন হলে request-scoped, যাতে যে provider এটি মুছতে পারে তারা করে।

///

[`StayTerse` capability](../message-history.md#request-scoped-system-prompts) এভাবে তৈরি একটি সম্পূর্ণ রিমাইন্ডার capability।

/// note | Skip আর শৃঙ্খলের আচরণ

`before_*` থেকে তোলা একটি skip exception ([`SkipModelRequest`][pydantic_ai.exceptions.SkipModelRequest], [`SkipToolValidation`][pydantic_ai.exceptions.SkipToolValidation], বা [`SkipToolExecution`][pydantic_ai.exceptions.SkipToolExecution]) বাকি `before_*` hook, মূল কাজ আর `after_*` থামায়, তারপর ইতিমধ্যে প্রবেশ করা wrapper শৃঙ্খলের মধ্য দিয়ে বাইরের দিকে প্রচারিত হয়। এর handler না ডেকে একটি skip তোলা একটি wrapper সব ভেতরের wrapper আর পুরো `before_*`/মূল/`after_*` lifecycle এড়িয়ে যায়। wrapper exception তোলার আগে এর handler ফেরত দিলে, সেই lifecycle ইতিমধ্যে শেষ হয়ে গেছে।

///

### Tool hook { #tool-hooks }

টুল প্রক্রিয়ার দুটি পর্যায়: **যাচাই** (মডেলের JSON আর্গুমেন্ট পার্স করে টুলের schema-র বিপরীতে যাচাই) আর **চালানো** (টুল ফাংশন চালানো)। প্রতিটি পর্যায়ের নিজস্ব hook আছে।

সব tool hook [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-সহ একটি `tool_def` প্যারামিটার পায়।

**যাচাই hook** — `args` হলো যাচাইয়ের আগে মডেলের কাঁচা `str | dict[str, Any]`, বা পরে যাচাই করা `dict[str, Any]`:

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_tool_validate`][pydantic_ai.capabilities.AbstractCapability.before_tool_validate] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`RawToolArgs`][pydantic_ai.capabilities.RawToolArgs]`) -> `[`RawToolArgs`][pydantic_ai.capabilities.RawToolArgs] | যাচাইয়ের আগে কাঁচা args বদলানো (যেমন JSON মেরামত) |
| [`after_tool_validate`][pydantic_ai.capabilities.AbstractCapability.after_tool_validate] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs]`) -> `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs] | যাচাই করা args বদলানো |
| [`wrap_tool_validate`][pydantic_ai.capabilities.AbstractCapability.wrap_tool_validate] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`RawToolArgs`][pydantic_ai.capabilities.RawToolArgs]`, handler: `[`WrapToolValidateHandler`][pydantic_ai.capabilities.WrapToolValidateHandler]`) -> `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs] | পুরো যাচাই lifecycle মোড়ানো |
| [`on_tool_validate_error`][pydantic_ai.capabilities.AbstractCapability.on_tool_validate_error] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`RawToolArgs`][pydantic_ai.capabilities.RawToolArgs]`, error: ValidationError | `[`ModelRetry`][pydantic_ai.exceptions.ModelRetry]`) -> `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs] | মূল যাচাই error সামলানো (দেখুন [error hooks](#error-hooks)) |

যাচাই বাদ দিয়ে আগে-যাচাই করা args দিতে, `before_tool_validate` বা `wrap_tool_validate` থেকে [`SkipToolValidation(args)`][pydantic_ai.exceptions.SkipToolValidation] তুলুন।

একটি টুল কল শুধু এর আর্গুমেন্ট যাচাই হওয়ার পরেই [defer](../deferred-tools.md) করা যায়, কারণ যিনি deferral মীমাংসা করেন তাঁকে ওই আর্গুমেন্ট দেখানো হয়। তাই [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] আর [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] তোলা যায় `after_tool_validate` থেকে, আর `wrap_tool_validate` থেকে এর `handler()` ফেরত আসার পর; `before_tool_validate` থেকে, `handler()` ডাকার আগে `wrap_tool_validate` থেকে, বা `on_tool_validate_error` থেকে (যা শুধু যাচাই ব্যর্থ হওয়ায় চলে) একটি তুললে hook-এর নামসহ একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে। একটি অনুমোদিত deferral ঠিক একটি টুলের [`args_validator`](../tools-advanced.md#args-validator) থেকে আসা একটির মতো আচরণ করে: টুল চলে না, retry বাজেট অপরিবর্তিত থাকে, আর কলটি রানের [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests]-এ যোগ হয়।

টুলের `args_validator` defer করলেও `after_tool_validate` একটি নির্ভরযোগ্য দরজা থাকে: দরজা চলার সময় deferral ধরে রাখা হয়, তাই সেখানে প্রত্যাখ্যান করা (`ModelRetry` বা [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] দিয়ে) জেতে, সেখানে defer করা ধরে রাখা deferral বদলে দেয়, আর এটি যে args ফেরত দেয় সেগুলোই deferred কল বহন করে। এর handler ফেরত আসার পর `wrap_tool_validate`-এর তোলা একটি deferral এই দরজা চলার পরে ঘটে, তাই দরজা ওই wrapper deferral প্রত্যাখ্যান বা বদলাতে পারে না।

**চালানোর hook** — `args` সবসময় যাচাই করা `dict[str, Any]`:

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_tool_execute`][pydantic_ai.capabilities.AbstractCapability.before_tool_execute] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs]`) -> `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs] | চালানোর আগে args বদলানো |
| [`after_tool_execute`][pydantic_ai.capabilities.AbstractCapability.after_tool_execute] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs]`, result: Any) -> Any` | চালানোর ফল বদলানো |
| [`wrap_tool_execute`][pydantic_ai.capabilities.AbstractCapability.wrap_tool_execute] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs]`, handler: `[`WrapToolExecuteHandler`][pydantic_ai.capabilities.WrapToolExecuteHandler]`) -> Any` | পুরো চালানোর lifecycle মোড়ানো |
| [`on_tool_execute_error`][pydantic_ai.capabilities.AbstractCapability.on_tool_execute_error] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, call: `[`ToolCallPart`][pydantic_ai.messages.ToolCallPart]`, tool_def: `[`ToolDefinition`][pydantic_ai.tools.ToolDefinition]`, args: `[`ValidatedToolArgs`][pydantic_ai.capabilities.ValidatedToolArgs]`, error: Exception) -> Any` | মূল চালানোর error সামলানো (দেখুন [error hooks](#error-hooks)) |

চালানো বাদ দিয়ে একটি প্রতিস্থাপন ফল দিতে, `before_tool_execute` বা `wrap_tool_execute` থেকে [`SkipToolExecution(result)`][pydantic_ai.exceptions.SkipToolExecution] তুলুন।

যেকোনো চালানোর hook কলটি defer করতে পারে, কিন্তু `ApprovalRequired`/`CallDeferred` তুলুন `before_tool_execute` থেকে (বা `handler()` ডাকার আগে `wrap_tool_execute` থেকে), যাতে টুল ফাংশন না চলে: `after_tool_execute` থেকে, বা `handler()` ফেরত আসার পর `wrap_tool_execute` থেকে একটি deferral গ্রহণ করা হয়, কিন্তু টুল ইতিমধ্যে চলে গেছে, তাই এর side effect ঘটে গেছে আর এর ফল বাদ দেওয়া হয়।

/// warning | সাধারণ ভুল

একটি অনুমোদন-hook `after_tool_execute`-এ বসানো ("টাকা পাঠানোর পর অনুমোদন চাও")। ততক্ষণে টাকা চলে গেছে! মানুষের অনুমোদন সবসময় `before_tool_execute`-এ (বা `after_tool_validate`-এ) তুলুন, যাতে টুল চলার আগেই থামে।

///

Tool যাচাই আর চালানোর hook একটি retry চাইতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে, বা retry না করে একটি ব্যর্থ টুল ফল জানাতে [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] তুলতে পারে। পুরো ধরনের জন্য দেখুন [triggering retries and tool failures](../hooks.md#triggering-retries-with-modelretry)।

### Output hook { #output-hooks }

টুল প্রক্রিয়ার মতো, [output](../output.md) প্রক্রিয়ারও দুটি পর্যায়: **যাচাই** (মডেলের কাঁচা আউটপুট আউটপুট schema-র বিপরীতে পার্স করা) আর **প্রক্রিয়া** (মান বের করা আর যেকোনো [output function](../output.md#output-functions) ডাকা)। প্রতিটি পর্যায়ের নিজস্ব hook আছে।

সব output hook [`OutputContext`][pydantic_ai.capabilities.OutputContext]-সহ একটি `output_context` প্যারামিটার পায় (mode, output type, schema তথ্য, আর [tool output](../output.md#tool-output)-এর জন্য টুল কলের বিস্তারিত)।

**Validate hook** শুধু পার্স করা লাগে এমন কাঠামোবদ্ধ আউটপুটের জন্য চলে (prompted, native, tool, union output)। এগুলো সাধারণ লেখা বা ছবি আউটপুটের জন্য চলে না। **Process hook** চলে **সব আউটপুট টাইপের** জন্য, লেখা, কাঠামোবদ্ধ আর ছবি আউটপুটসহ। [tool output](../output.md#tool-output)-এর জন্য, শুধু output hook চলে — tool hook পুরোপুরি বাদ পড়ে।

**যাচাই hook** — শুধু কাঠামোবদ্ধ আউটপুটের জন্য চলে; `output` হলো `str` (কাঁচা লেখা) বা `dict` (টুলের args):

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_output_validate`][pydantic_ai.capabilities.AbstractCapability.before_output_validate] | `(ctx, *, output_context, output: RawOutput) -> RawOutput` | যাচাইয়ের আগে কাঁচা আউটপুট বদলানো (যেমন JSON মেরামত) |
| [`after_output_validate`][pydantic_ai.capabilities.AbstractCapability.after_output_validate] | `(ctx, *, output_context, output: Any) -> Any` | যাচাই করা আউটপুট বদলানো |
| [`wrap_output_validate`][pydantic_ai.capabilities.AbstractCapability.wrap_output_validate] | `(ctx, *, output_context, output: RawOutput, handler) -> Any` | পুরো যাচাই lifecycle মোড়ানো |
| [`on_output_validate_error`][pydantic_ai.capabilities.AbstractCapability.on_output_validate_error] | `(ctx, *, output_context, output: RawOutput, error: ValidationError | ModelRetry) -> Any` | মূল যাচাই error সামলানো (দেখুন [error hooks](#error-hooks)) |

**প্রক্রিয়া hook** — সব আউটপুট টাইপের জন্য চলে; `output` হলো যাচাই করা/কাঁচা আউটপুট। `wrap_output_process` handler `before_output_process`, `on_output_process_error` উদ্ধারসহ মূল প্রক্রিয়া, আর `after_output_process` চালায়। আউটপুট validator ([`@agent.output_validator`][pydantic_ai.agent.Agent.output_validator]) সেই মূল প্রক্রিয়ার অংশ, তাই wrapper এগুলো ঘিরে রাখে আর `after_output_process` পুরোপুরি যাচাই করা ফল দেখে:

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`before_output_process`][pydantic_ai.capabilities.AbstractCapability.before_output_process] | `(ctx, *, output_context, output: Any) -> Any` | প্রক্রিয়ার আগে আউটপুট বদলানো |
| [`after_output_process`][pydantic_ai.capabilities.AbstractCapability.after_output_process] | `(ctx, *, output_context, output: Any) -> Any` | প্রক্রিয়াকৃত ফল বদলানো |
| [`wrap_output_process`][pydantic_ai.capabilities.AbstractCapability.wrap_output_process] | `(ctx, *, output_context, output: Any, handler) -> Any` | পুরো প্রক্রিয়া lifecycle মোড়ানো |
| [`on_output_process_error`][pydantic_ai.capabilities.AbstractCapability.on_output_process_error] | `(ctx, *, output_context, output: Any, error: Exception) -> Any` | মূল প্রক্রিয়ার error সামলানো (দেখুন [error hooks](#error-hooks)) |

Output validate আর process hook একটি নিজস্ব বার্তাসহ মডেলকে আবার চেষ্টা করতে বলতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে — [output functions](../output.md#output-functions) আর [output validators](../output.md#output-validator-functions)-এ ব্যবহৃত একই ধরন। পুরো ধরনের জন্য দেখুন [Triggering retries with `ModelRetry`](../hooks.md#triggering-retries-with-modelretry)।

### টুল প্রস্তুতি { #tool-preparation }

Capability দুটি hook দিয়ে প্রতিটি step-এ মডেল কোন টুল সংজ্ঞা দেখে তা ছাঁকতে বা বদলাতে পারে:

- [`prepare_tools`][pydantic_ai.capabilities.AbstractCapability.prepare_tools] — শুধু **ফাংশন** টুল পায়। মডেল সরাসরি ডাকতে পারে এমন টুল ছাঁকা বা বদলানোর জন্য এটি ব্যবহার করুন।
- [`prepare_output_tools`][pydantic_ai.capabilities.AbstractCapability.prepare_output_tools] — শুধু [output tools][pydantic_ai.output.ToolOutput] পায়, `ctx.retry`/`ctx.max_retries` এজেন্টের retry বাজেটের **আউটপুট** দিক প্রতিফলিত করে, [output hook](#output-hooks) lifecycle-এর সাথে মিলে।

দুটি hook-ই toolset স্তরে কাজ করে — ফল মডেলের রিকোয়েস্ট প্যারামিটার আর `ToolManager.tools` দুটোতেই প্রবাহিত হয়, তাই ছাঁকা টুল চালানোও আটকায়।

/// note | একটি deferred capability-তে

`prepare_tools` শুধু capability [লোড](on-demand.md) হওয়ার পরে চলে, আর তখন প্রতিটি ফাংশন টুল পায়, ঠিক যেমন একটি সবসময়-চালু capability-র জন্য পেত। এর আগে এর নিয়ন্ত্রণের কিছু নেই: একটি অ-লোড capability-র টুল মডেলকে বিজ্ঞাপিতও হয় না, ডাকাও যায় না।

///

⟦CODE16⟧

সহজ ক্ষেত্রে, বিল্ট-ইন [`PrepareTools`][pydantic_ai.capabilities.PrepareTools] / [`PrepareOutputTools`][pydantic_ai.capabilities.PrepareOutputTools] capability একটি নিজস্ব subclass ছাড়াই একটি callable মোড়ায়।

### Event stream hook { #event-stream-hook }

event streaming-যুক্ত রানের জন্য ([`run_stream_events`][pydantic_ai.agent.AbstractAgent.run_stream_events], [`event_stream_handler`][pydantic_ai.agent.Agent.__init__], [UI event streams](../ui/overview.md)), capability event stream পর্যবেক্ষণ বা রূপান্তর করতে পারে:

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`wrap_run_event_stream`][pydantic_ai.capabilities.AbstractCapability.wrap_run_event_stream] | `(ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, *, stream: AsyncIterable[`[`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent]`]) -> AsyncIterable[`[`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent]`]` | stream করা event পর্যবেক্ষণ, ছাঁকা বা রূপান্তর |
| [`on_event`][pydantic_ai.capabilities.on_event] | একটি async `(self, ctx: `[`RunContext`][pydantic_ai.tools.RunContext]`, event: EventT) -> None` মেথডে `@on_event(*event_types)` | stream-এর বাকিটা না ছুঁয়ে বাছা event-এ সাড়া দেওয়া |

hook-টি stream যেখানে তৈরি হয় সেখানে মোড়ায়, তাই এটি প্রতিটি চালানোর মোডে চলে: [`agent.run()`][pydantic_ai.agent.AbstractAgent.run] (এই hook নিবন্ধিত থাকলে যা নিজে থেকে streaming চালু করে), [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] আর [`agent.iter()`][pydantic_ai.agent.Agent.iter] — আপনি এটি `async for node in agent_run:` দিয়ে, [`agent_run.next()`][pydantic_ai.run.AgentRun.next] দিয়ে, বা [নিজে একটি node stream করে](../agent.md#streaming-all-events) এগিয়ে নিন। একটি capability যে event বাদ দেয় বা যোগ করে তা একজন হাতে-চালানো `node.stream()` consumer যা দেখে তাতে প্রতিফলিত হয়, অন্য যেকোনো consumer-এর মতোই। এটি একটি [realtime session](../realtime/capabilities.md)-এর event iterator-ও মোড়ায়, যেখানে stream-এ বাড়তি শুধু-realtime [`RealtimeSessionEvent`][pydantic_ai.messages.RealtimeSessionEvent] সদস্য থাকে।

একজন consumer event stream শেষ না করেই বন্ধ করলে, Pydantic AI `wrap_run_event_stream`-এর ফেরত দেওয়া প্রতিটি wrapper-ও বন্ধ করে, যদি এটি একটি `aclose()` মেথড দেয়। নিজস্ব wrapper-এর গুটানোর জন্য `try`/`finally` ব্যবহার করা উচিত আর সেখানে নিরাপদে পরিষ্কার-কাজ await করতে পারে, কিন্তু `GeneratorExit` সামলানোর সময় event yield করা চলবে না, কারণ consumer চলে গেছে।

যেহেতু নিজের input বন্ধ করা একটি wrapper আর এর তৈরি প্রতিটি wrapper বন্ধ করা একটি জোড়া capability দুটোই একই stream-এ পৌঁছাতে পারে, `aclose()` একাধিকবার ডাকা হতে পারে। Async generator এখানে idempotent, তাই একটি `try`/`finally` wrapper-এর বাড়তি কিছু লাগে না; হাতে `aclose()` বাস্তবায়ন করা একটি wrapper-এর পুনরাবৃত্ত কলকে কিছু-না-করা বানানো উচিত।

/// warning | একটি processor পুরো stream গড়ে, শুধু handler-এর দৃশ্য নয়

রানের একটি event stream, তাই event বাদ দেওয়া বা নতুন করে লেখা একটি capability *প্রত্যেক* consumer যা দেখে তা বদলায় — একজন [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] caller [`stream_text()`][pydantic_ai.result.StreamedRunResult.stream_text] থেকে যে লেখা পান সেটিসহ।

কিছু event নিয়ন্ত্রণ-সংকেতও। [`FinalResultEvent`][pydantic_ai.messages.FinalResultEvent]
[`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream]-কে বলে যে চূড়ান্ত আউটপুট শুরু হয়েছে, তাই এটি বাদ দেওয়া একটি processor `run_stream()`-কে stream না করে ফল ফেরত দেওয়ার আগে পুরো মডেল response-এর অপেক্ষা করায়। রানের আউটপুট অপরিবর্তিত থাকে। ভেবেচিন্তে ছাঁকুন।

এটি রানের আউটপুটে পৌঁছায় না। একটি processor event দেখার আগেই কাঁচা মডেল stream থেকে [`ModelResponse`][pydantic_ai.messages.ModelResponse] জমা হয়, তাই [`stream_output()`][pydantic_ai.result.StreamedRunResult.stream_output] আর চূড়ান্ত যাচাই করা আউটপুট প্রভাবিত হয় না — event বাদ দেওয়া শুধু বদলায় কখন একটি আংশিক snapshot তৈরি হয়, এতে কী থাকে তা নয়। কিছু না বদলে পর্যবেক্ষণ করতে, stream নিয়ে প্রতিটি event অপরিবর্তিত yield করুন।

///

⟦CODE17⟧

[`ToolCallEvent`][pydantic_ai.messages.ToolCallEvent] আর [`ToolResultEvent`][pydantic_ai.messages.ToolResultEvent]-এর বিপরীতে মেলানো ফাংশন টুল কল ([`FunctionToolCallEvent`][pydantic_ai.messages.FunctionToolCallEvent] / [`FunctionToolResultEvent`][pydantic_ai.messages.FunctionToolResultEvent]) আর আউটপুট টুল কল ([`OutputToolCallEvent`][pydantic_ai.messages.OutputToolCallEvent] / [`OutputToolResultEvent`][pydantic_ai.messages.OutputToolResultEvent]) দুটোই সামলায়। এদের ভিন্নভাবে সামলাতে হলে নির্দিষ্ট subclass-এর বিপরীতে মেলান। [Deferred tool calls](../deferred-tools.md#observing-deferred-tool-calls-in-a-stream) বাড়তি ব্যাচ-স্তরের [`DeferredToolRequestsEvent`][pydantic_ai.messages.DeferredToolRequestsEvent] / [`DeferredToolResultsEvent`][pydantic_ai.messages.DeferredToolResultsEvent] তৈরি করে।

পুরো stream গড়ার বদলে কয়েকটি event টাইপে সাড়া দিতে, এর বদলে একটি async মেথডকে [`@on_event`][pydantic_ai.capabilities.on_event] দিয়ে চিহ্নিত করুন। এটি stream-এর একই বিন্দুতে event পায়, আপনার দেওয়া ক্লাসের বিপরীতে `isinstance` দিয়ে ছাঁকে, আর অন্য consumer যা দেখে তা বদলাতে পারে না। ক্লাসের নাম দেওয়া আপনার capability-কে বাকি সব কিছুর dispatch-এর বাইরেও রাখে — দেখুন [Reacting to events](overview.md#reacting-to-events)।

আপনার capability অন্য capability আর host অ্যাপ্লিকেশনের সাড়া দেওয়ার জন্য নিজের event-ও প্রকাশ করতে পারে, namespace-যুক্ত [`CapabilityEvent`][pydantic_ai.messages.CapabilityEvent] subclass সংজ্ঞায়িত করে আর একটি hook বা এর দেওয়া একটি টুল থেকে [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] await করে। দুই দিকের জন্য দেখুন [Capability events](overview.md#capability-events), আর একটি capability কেন অ্যাপ্লিকেশন [`CustomEvent`][pydantic_ai.messages.CustomEvent]-এর বদলে এগুলো প্রকাশ করে তার জন্য দেখুন [Which event type do I use?](../agent.md#which-event-type)।

stream করা event-কে protocol-নির্দিষ্ট ফরম্যাটে (যেমন SSE) রূপান্তর করা ওয়েব UI তৈরির জন্য, দেখুন [UI event streams](../ui/overview.md) ডকুমেন্টেশন আর [`UIEventStream`][pydantic_ai.ui.UIEventStream] base class।

### Error hook { #error-hooks }

প্রতিটি lifecycle বিন্দুর একটি `on_*_error` hook আছে — `after_*`-এর error প্রতিরূপ। এটি মোড়ানো handler-এর ভেতরে মূল কাজের ব্যর্থতা সামলায়, তাই wrapper-রা একটি অ-উদ্ধারকৃত ব্যর্থতা দেখার আগেই এটি চলে:

⟦CODE18⟧

`handler` না ডেকে ফেরত দেওয়া একটি wrapper এর ভেতরের সবকিছু বাদ দেয়। `before_X`, `after_X` বা `wrap_X` থেকে exception-ও `on_X_error`-এর পরিসরের বাইরে, যদিও বাইরের wrapper তবুও এগুলো ধরতে পারে।

Error hook **raise-to-propagate, return-to-recover** অর্থ ব্যবহার করে:

- **মূল error আবার তুলুন** — error অপরিবর্তিত প্রচার করে *(ডিফল্ট)*
- **একটি ভিন্ন exception তুলুন** — error রূপান্তর করে
- **একটি ফল ফেরত দিন** — error দমন করে আর ফেরত মান ব্যবহার করে

| Hook | কখন চলে | উদ্ধারের টাইপ |
|---|---|---|
| [`on_run_error`][pydantic_ai.capabilities.AbstractCapability.on_run_error] | রানের body ব্যর্থ হয় | [`AgentRunResult`][pydantic_ai.run.AgentRunResult] ফেরত |
| [`on_node_run_error`][pydantic_ai.capabilities.AbstractCapability.on_node_run_error] | মূল graph-node চালানো ব্যর্থ হয় | পরের node বা [`End`][pydantic_graph.basenode.End] ফেরত |
| [`on_model_request_error`][pydantic_ai.capabilities.AbstractCapability.on_model_request_error] | মূল মডেল কল ব্যর্থ হয় | [`ModelResponse`][pydantic_ai.messages.ModelResponse] ফেরত |
| [`on_tool_validate_error`][pydantic_ai.capabilities.AbstractCapability.on_tool_validate_error] | মূল টুল যাচাই ব্যর্থ হয় | যাচাই করা args `dict` ফেরত |
| [`on_tool_execute_error`][pydantic_ai.capabilities.AbstractCapability.on_tool_execute_error] | মূল টুল চালানো ব্যর্থ হয় | যেকোনো টুল ফল ফেরত |
| [`on_output_validate_error`][pydantic_ai.capabilities.AbstractCapability.on_output_validate_error] | মূল আউটপুট যাচাই ব্যর্থ হয় | যাচাই করা আউটপুট ফেরত |
| [`on_output_process_error`][pydantic_ai.capabilities.AbstractCapability.on_output_process_error] | মূল আউটপুট প্রক্রিয়া ব্যর্থ হয় | যেকোনো আউটপুট ফল ফেরত |

একাধিক capability থাকলে, `on_*_error` hook **উল্টো** capability ক্রমে চলে (`after_*`-এর মতো)। প্রথম যে capability একটি ফল ফেরত দেয় সেটি error **উদ্ধার** করে — বাকি capability-র error hook ডাকা হয় না। একটি handler আবার তুললে বা একটি নতুন exception তুললে, শৃঙ্খলের পরের capability সেই exception দেখে।

⟦CODE19⟧

### Deferred tool call { #deferred-tool-calls }

Capability [deferred tool calls](../deferred-tools.md) — যে কলে অনুমোদন লাগে, বা যা বাইরে চলে — সরাসরি এজেন্ট রান থেকে মীমাংসা করতে পারে, রান শেষ করে একটি পরবর্তী ধাপের অপেক্ষা না করে:

| Hook | Signature | উদ্দেশ্য |
|---|---|---|
| [`handle_deferred_tool_calls`][pydantic_ai.capabilities.AbstractCapability.handle_deferred_tool_calls] | `(ctx: RunContext, *, requests: DeferredToolRequests) -> DeferredToolResults \| None` | কিছু বা সব বাকি অনুমোদন/বাইরের কল inline মীমাংসা |

একাধিক capability প্রত্যেকে একটি উপসেট সামলাতে পারে: dispatch শৃঙ্খল জুড়ে ফল জমা করে, পরের capability-কে শুধু এখনও অমীমাংসিত রিকোয়েস্ট দেয়। `None` (বা কোনো entry ছাড়া একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults]) ফেরত দেওয়া সামলানো প্রত্যাখ্যান করে। তখনও অমীমাংসিত যেকোনো কিছু caller-এর সামলানোর জন্য একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট হিসেবে ওপরে ওঠে।

যে অ্যাপ্লিকেশন কোডের শুধু একটি handler বসানো দরকার, তার জন্য নির্দিষ্ট [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] capability ব্যবহার করুন — দেখুন [Resolving deferred calls with a handler](../deferred-tools.md#resolving-deferred-calls-with-a-handler)।

## Durable capability operation { #durable-capability-operations }

একটি capability [`durable_operation`][pydantic_ai.capabilities.durable_operation] দিয়ে I/O বা অন্য non-deterministic কাজ workflow কোড থেকে একটি durable activity, step বা task-এ সরাতে পারে। capability-কে একটি স্থিতিশীল [`id`][pydantic_ai.capabilities.AbstractCapability.id] দিন, কারণ engine সংরক্ষিত কাজ উদ্ধার আর replay করতে capability ID আর operation নাম ব্যবহার করে।

Runtime ইন্টিগ্রেশন মডেল আর টুল operation-এর মতো একই টাইপ করা backend দিয়ে এই operation পায়। একটি engine বাস্তবায়নের সময় দেখুন [Building a durable execution backend](../durable_execution/backends.md)।

⟦CODE20⟧

প্রতিটি operation মেথড `@durable_operation(name='...')` দিয়ে চিহ্নিত করুন। বাধ্যতামূলক নামটি সংরক্ষিত durable-unit নামের অংশ হয় আর স্থির থাকতে হবে, যখন Python মেথডের নাম স্বাধীনভাবে বদলানো যায়। একটি durability capability বাঁধা থাকলে, একটি রানের সময় মেথডটি ডাকলে এটি সেই engine দিয়ে পাঠানো হয়। durability ছাড়া, একই কল সরাসরি মূল মেথড await করে।

একটি [`for_run`][pydantic_ai.capabilities.AbstractCapability.for_run] override একটি নতুন instance ফেরত দিতে পারে — রান যে instance ব্যবহার করছে তাতেই operation পাঠানো হয়, `before_run` থেকে আর প্রতি-রিকোয়েস্ট hook থেকে সমানভাবে। প্রতিস্থাপনটিকে capability-র `id` রাখতে হবে, কারণ dispatch আর worker-পক্ষের উদ্ধার এটি দিয়েই একে মীমাংসা করে; একটি বাঁধা capability-র ID আর উপস্থিত না থাকলে Pydantic AI রানের শুরুতে একটি `UserError` তোলে। `for_run()` ফেরত দেওয়ার পরেই dispatch প্রতিষ্ঠিত হয়, তাই `for_run()`-এর ভেতর থেকে ডাকা একটি operation durable-ভাবে নয়, সরাসরি চলে।

একটি operation capability-র দেওয়া একটি টুল থেকেও ডাকা যায়। যেখানে engine আগে থেকেই টুলটি নিজের activity, step বা task-এ চালায়, যেমন Temporal, Prefect আর AWS Lambda করে, সেখানে operation এর ভেতরে সরাসরি চলে, নিজের বদলে সেই এককের timeout, retry আর cache কনফিগারেশনের অধীনে, কারণ সেই একক ফল লেখে। যেখানে টুল workflow কোডে চলে, যেমন DBOS-এর অধীনে ফাংশন টুল চলে, সেখানে operation নিজের একক। যেকোনোভাবে কাজটি একবার লেখা হয়, তাই যে capability-র টুল I/O করে সে সেই I/O একটি operation দিয়ে পাঠিয়ে প্রতিটি engine-এ durable থাকতে পারে।

আর্গুমেন্ট আর ফলকে durable টুলের মতো একই serialization নিয়ম মানতে হবে। Temporal এগুলো এর data converter দিয়ে পাঠায়; JSON-journal engine-এর JSON-সামঞ্জস্যপূর্ণ মান লাগে। Operation-এর নাম capability ID দিয়ে পরিসীমিত। কোনো পরিচয় বদলালে একটি ভিন্ন সংরক্ষিত operation তৈরি হয়, আর Prefect-এ এটি একটি ভিন্ন cache key-ও তৈরি করে।

এটি ব্যবহার করা রান deploy হওয়ার পর একটি capability-র `id` স্থির রাখুন, আপনি লেখেননি এমন একটির ডিফল্ট `id`-সহ: যে Harness capability তাদের টুল রিকোয়েস্টের রেকর্ড রাখে, যেমন [`ExaSearch`](../harness/exa-search.md), সেগুলো ওই রেকর্ডের নাম তাদের `id` অনুযায়ী দেয়।

একটি hook durable workflow কোডে চলছে কিনা তার ওপর ভাগ করতে, [`ctx.in_durable_context`][pydantic_ai.tools.RunContext.in_durable_context] যাচাই করুন। এজেন্টের একটি durability capability থাকলে একটি durable workflow বা flow-এর ভেতরে (যেমন একটি Temporal বা DBOS workflow) এটি `True`। durable execution-এর বাইরে আর Temporal activity ও DBOS step-এর ভেতরে, যেখানে টুল আর মডেল রিকোয়েস্ট চলে, এটি `False`। Prefect task তাদের flow-এর context উত্তরাধিকারসূত্রে পায়, তাই একটি Prefect task-এর ভেতরেও এটি `True`।

জীবন্ত-মানের hook `get_toolset`, `get_wrapper_toolset`, `wrap_run`, `wrap_node_run`, `wrap_model_request`, `wrap_tool_validate`, `wrap_tool_execute`, `wrap_output_validate`, `wrap_output_process` আর `wrap_run_event_stream` decorate করা যায় না, কারণ এদের handler বা মান একটি durable সীমা পার হতে পারে না। এজেন্ট তৈরির সময় Pydantic AI অসামঞ্জস্যপূর্ণ hook-এর নামসহ একটি `UserError` তোলে।

## Capability মোড়ানো { #wrapping-capabilities }

[`WrapperCapability`][pydantic_ai.capabilities.WrapperCapability] আরেকটি capability মোড়ায় আর সব মেথড তাকে দেয় — toolset-এর জন্য [`WrapperToolset`][pydantic_ai.toolsets.WrapperToolset]-এর মতো। বাকিটা দিয়ে নির্দিষ্ট মেথড override করতে এটি subclass করুন:

⟦CODE21⟧

বিল্ট-ইন [`PrefixTools`][pydantic_ai.capabilities.PrefixTools] একটি `WrapperCapability`-এর উদাহরণ — এটি আরেকটি capability মুড়ে এর টুলের নামে prefix দেয়।

## প্রতি-রান state বিচ্ছিন্নতা { #per-run-state-isolation }

তৈরির সময়ের [`for_agent()`][pydantic_ai.capabilities.AbstractCapability.for_agent] বাঁধার পর, ফলের capability instance একটি এজেন্টের সব রান জুড়ে ভাগ হয়। আপনার capability যদি এমন পরিবর্তনযোগ্য state জমা করে যা রানের মধ্যে ছড়ানো উচিত নয়, একটি নতুন instance ফেরত দিতে [`for_run`][pydantic_ai.capabilities.AbstractCapability.for_run] override করুন:

⟦CODE22⟧

/// warning | সাধারণ ভুল

একটি capability-তে `self.call_count += 1` রাখা কিন্তু `for_run` override না করা। একই এজেন্ট দুজন ব্যবহারকারীর জন্য একসাথে চললে দুজনের গণনা মিশে যাবে — কারণ capability instance সব রানে একটাই। প্রতি-রান state থাকলে `for_run` থেকে একটি নতুন instance ফেরত দিন।

///

`for_run` একটি নতুন instance ফেরত দিলে, রান সেটআপে সেই প্রতিস্থাপন থেকে capability-র কনফিগারেশন আবার বের করা হয়: [`get_instructions`][pydantic_ai.capabilities.AbstractCapability.get_instructions], [`get_toolset`][pydantic_ai.capabilities.AbstractCapability.get_toolset], [`get_native_tools`][pydantic_ai.capabilities.AbstractCapability.get_native_tools] আর [`get_model_settings`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] এতে আবার ডাকা হয়, আর [`get_wrapper_toolset`][pydantic_ai.capabilities.AbstractCapability.get_wrapper_toolset], [`get_description`][pydantic_ai.capabilities.AbstractCapability.get_description] আর সব lifecycle hook সবসময় এতে চলে। ব্যতিক্রম হলো মডেল আর workspace বাছাই: [`get_model()`][pydantic_ai.capabilities.AbstractCapability.get_model], bootstrap [`resolve_model_id()`][pydantic_ai.capabilities.AbstractCapability.resolve_model_id] আর [`get_workspace()`][pydantic_ai.capabilities.AbstractCapability.get_workspace] মূল instance-এ `for_run`-এর *আগে* চলে, তাই `for_run` ইতিমধ্যে `ctx.workspace` ব্যবহার করতে পারে। bootstrap মডেল বাছাই পুনর্ব্যবহৃত হয় যদি না প্রতিস্থাপন সত্যিই মডেলের অবদান বদলায় — দেখুন [Model selection lifecycle and limitations](#model-selection-lifecycle-and-limitations)। `for_run` এর আগে বাছা workspace বদলাতে পারে না; একটি রানের জন্য ভিন্ন একটি ব্যবহার করতে, এটি `workspace=` হিসেবে দিন।

`for_run`-এর ভেতরে কখনো `self` বদলাবেন না — এর বদলে একটি নতুন instance ফেরত দিন। `for_run` মূলটি অপরিবর্তিত ফেরত দিলে, এজেন্ট তৈরির সময় cache করা কনফিগারেশন পুনর্ব্যবহৃত হয়, তাই `self`-এ পরিবর্তন ধরা পড়বে না।

## গতিশীলভাবে একটি capability তৈরি { #dynamically-building-a-capability }

প্রতিটি এজেন্ট রানের আগে একটি ফাংশন দিয়ে capability গতিশীলভাবে তৈরি করা যায়, যা এজেন্টের [`RunContext`][pydantic_ai.tools.RunContext] নিয়ে একটি capability বা `None` ফেরত দেয়। এটি কাজের যখন capability — এর instructions, model settings, hook বা দেওয়া toolset — একটি রানের নির্দিষ্ট তথ্যের ওপর নির্ভর করে, যেমন এর [dependencies](../dependencies.md)।

একটি গতিশীল capability নিবন্ধন করতে, [`Agent`][pydantic_ai.Agent] constructor বা `agent.run()`-এর `capabilities` আর্গুমেন্টে [`RunContext`][pydantic_ai.tools.RunContext] নেওয়া একটি ফাংশন দিন। Sync আর async ফাংশন দুটোই সমর্থিত। ফাংশনটি প্রতি রানে একবার ডাকা হয় আর ফেরত দেওয়া capability রানের বাকি সময় এর জায়গা নেয়, তাই এর instructions, model settings, toolset, নেটিভ টুল আর hook সবই স্বাভাবিকভাবে প্রবাহিত হয়।

⟦CODE23⟧

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

একটি একক factory থেকে একাধিক capability ফেরত দিতে, এগুলো একটি [`CombinedCapability`][pydantic_ai.capabilities.CombinedCapability]-এ মুড়ুন।

/// note | Durable execution (Temporal, DBOS, Prefect)

গতিশীল capability, এদের দেওয়া toolset-সহ, durable execution-এর সাথে কাজ করে। তিনটি engine-এই [`DynamicCapability`][pydantic_ai.capabilities.DynamicCapability]-তে একটি স্থিতিশীল `id` সেট করুন, যাতে এদের activity, step বা task ধারাবাহিকভাবে নিবন্ধিত হতে পারে। যেহেতু সরাসরি `capabilities=`-এ দেওয়া একটি খালি [`CapabilityFunc`][pydantic_ai.capabilities.CapabilityFunc] একটি `id` বহন করতে পারে না, একে স্পষ্টভাবে মুড়ুন: `DynamicCapability(my_func, id='...')`।

DBOS গতিশীল টুল খোঁজা আর কল step-এ চালায়, যেকোনো MCP I/O checkpoint করে, আর Prefect গতিশীল টুল কল task-এ চালায় আর flow কোডে টুল মীমাংসা করে। দুটোই তাদের step বা task-এর ভেতরে রানের জন্য ইতিমধ্যে মীমাংসিত capability পুনর্ব্যবহার করে। Temporal activity-র ভেতরে factory আবার চালায়, কারণ activity সীমা রানের মীমাংসিত capability বহন করতে পারে না। তিনটি engine-এই factory নিজে workflow বা flow কোডে চলে, যা replay, উদ্ধার বা flow retry-তে আবার চলে — তাই রানের dependency দেওয়া থাকলে একে deterministic রাখুন আর I/O এর ফেরত দেওয়া toolset-এর জন্য রাখুন।

///

## জোড়া আর middleware অর্থ { #composition-and-middleware-semantics }

একটি এজেন্টে একাধিক capability দিলে, সেগুলো একটি একক [`CombinedCapability`][pydantic_ai.capabilities.CombinedCapability]-এ জোড়া হয়, যা **middleware অর্থ** মানে — Django আর Starlette-এর মতো ওয়েব framework-এ ব্যবহৃত একই ধরন:

* **কনফিগারেশন** মেলানো হয়: instructions জোড়া লাগে, model settings যোগাত্মকভাবে মেলে (পরের capability আগেরগুলোকে override করে), toolset একত্র হয়, নেটিভ টুল সংগৃহীত হয়।
* **`before_*`** hook capability ক্রমে চলে (বাইরে থেকে ভেতরে): `cap1 → cap2 → cap3`।
* **`after_*`** hook উল্টো ক্রমে চলে (ভেতর থেকে বাইরে): `cap3 → cap2 → cap1`।
* **`wrap_*`** hook middleware হিসেবে nest করে: `cap1` মোড়ায় `cap2`-কে, যা মোড়ায় `cap3`-কে, যা মোড়ায় পুরো `before_*`/মূল/`on_*_error`/`after_*` lifecycle। প্রথম capability হলো **সবচেয়ে বাইরের** স্তর।
* **`get_wrapper_toolset`** একই nesting মানে: প্রথম capability-র wrapper সবচেয়ে বাইরের।

hook পরিবারগুলো capability ধরে ধরে মিশে যায় না। পুরো ক্রম:

⟦CODE24⟧

প্রথম capability-র wrapper হলো পর্যায়ের চারপাশে প্রথম আর শেষ স্তর। ভেতরের lifecycle-এর মধ্যে, প্রথম capability-র `before_*` hook প্রথমে চলে আর এর `after_*` hook শেষে চলে। পরিবার-জুড়ে সীমার একটি ফল হলো `cap3.wrap`-ও `cap1.before`-এর আগে চলে।

## ক্রম { #ordering }

ডিফল্টভাবে, capability আপনি যে ক্রমে তালিকা করেন সেই ক্রমে জোড়া হয়। ব্যবহারকারী যেখানেই তালিকা করুক, একটি capability-র একটি নির্দিষ্ট অবস্থানে থাকা দরকার হলে, একটি [`CapabilityOrdering`][pydantic_ai.capabilities.CapabilityOrdering] ফেরত দিতে [`get_ordering`][pydantic_ai.capabilities.AbstractCapability.get_ordering] override করুন:

⟦CODE25⟧

উপলব্ধ বাধা:

* **`position`** — `'outermost'` বা `'innermost'`। ওই অবস্থান ছাড়া সব capability-র আগে (বা পরে) একটি স্তরে capability রাখে। একাধিক capability একটি স্তর ভাগ করতে পারে; মূল লিস্টের ক্রম এর মধ্যে সমতা ভাঙে।
* **`wraps`** — এটি যে capability-গুলো ঘিরে রাখে (যাদের বাইরে)। প্রতিটি entry একটি capability **টাইপ** হতে পারে (`issubclass` দিয়ে সব instance মেলায়) বা একটি নির্দিষ্ট **instance** (পরিচয় দিয়ে মেলায়)। আপনার capability-র আরেকটির আউটপুট দেখা দরকার হলে ব্যবহার করুন: `CapabilityOrdering(wraps=[OtherCapability])`।
* **`wrapped_by`** — যে capability-গুলো এটিকে ঘিরে রাখে (এর বাইরে)। `wraps`-এর মতো টাইপ বা instance নেয়। `wraps`-এর বিপরীত।
* **`requires`** — যে capability টাইপগুলো উপস্থিত থাকতে হবে। কোনোটি অনুপস্থিত থাকলে [`UserError`][pydantic_ai.exceptions.UserError] তোলে। ক্রম বোঝায় না।

বাধা ঘোষিত হলে, [`CombinedCapability`][pydantic_ai.capabilities.CombinedCapability] তৈরির সময় এর সন্তানদের topologically সাজায়, সমতা-ভাঙক হিসেবে ব্যবহারকারীর দেওয়া ক্রম রেখে।

[`Hooks`][pydantic_ai.capabilities.Hooks] `ordering` প্যারামিটার দিয়ে ক্রম সমর্থন করে, তাই আপনি subclass ছাড়াই ক্রমের বাধা ঘোষণা করতে পারেন:

⟦CODE26⟧


### capability-র মধ্যে state ভাগ করা { #sharing-state-between-capabilities }

Capability-রা একে অপরের সরাসরি নাগাল পায় না। অন্য capability-দের কিছু ঘটেছে জানাতে, একটি [capability event](overview.md#capability-events) প্রকাশ করুন: প্রকাশক [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] await করে আর আগ্রহী যেকোনো capability [`@on_event`][pydantic_ai.capabilities.on_event] দিয়ে সাড়া দেয়, তাদের মধ্যে কোনো ভাগ করা অবজেক্ট আর `capabilities` লিস্টে কোনো ক্রমের প্রয়োজনীয়তা ছাড়াই।

একটি ঘটনা ঘোষণার বদলে একটি মান ভাগ করতে, একটি async ফাংশন থেকে সেট করা একটি [`contextvars.ContextVar`][contextvars.ContextVar] ব্যবহার করুন: একটি capability এটি সেট করে (যেমন `wrap_run` বা `before_run`-এ), আর আরেকটি এর hook থেকে এটি পড়ে। একটি `before_*` পরিবারের মধ্যে, পাঠকের আগে লেখককে তালিকা করুন। কোনো `before_*` hook চলার আগে প্রতিটি wrapper-এ প্রবেশ করা হয়, তাই `handler` ডাকার আগে একটি wrapper যে মান সেট করে তা সব `before_*` hook-এ দৃশ্যমান, আর একটি wrapper `before_*` hook-এর সেট করা মান শুধু এর handler ফেরত আসার পরেই পড়তে পারে। একটি sync [`Hooks`](../hooks.md) ফাংশন লেখক হতে পারে না: এটি একটি আলাদা thread-এ চলে, তাই এর সেট করা মান রানের বাকি অংশে দৃশ্যমান নয়।

`run_stream()`-এ, একটি async `before_model_request` hook-এর সেট করা মান পরের টুল, আউটপুট আর run hook-এ উপলব্ধ। সেই মডেল রিকোয়েস্টে পরে সেট করা মান হয়তো নয়; রান জুড়ে ভাগ করতে হবে এমন state-এর জন্য পরিবর্তনযোগ্য [dependencies](../dependencies.md) ব্যবহার করুন।

### নিজস্ব capability টেস্ট { #testing-custom-capabilities }

নিজস্ব capability সেভাবেই টেস্ট করুন যেভাবে আপনি [এজেন্ট টেস্ট](../testing.md) করেন — [`TestModel`][pydantic_ai.models.test.TestModel] বা [`FunctionModel`][pydantic_ai.models.function.FunctionModel] দিয়ে। আপনার capability-সহ একটি এজেন্ট তৈরি করে রানের ফল, বার্তা বা আপনার hook-এর যেকোনো পর্যবেক্ষণযোগ্য side effect-এর ওপর assert করুন।

## উদাহরণ { #examples }

### Guardrail (PII মুছে ফেলা) { #guardrail-pii-redaction }

একটি guardrail হলো এমন একটি capability যা নিরাপত্তার নিয়ম প্রয়োগে মডেল রিকোয়েস্ট বা response ধরে। এখানে একটি যা মডেলের response-এ সম্ভাব্য PII (ব্যক্তিগত শনাক্তযোগ্য তথ্য) খুঁজে মুছে দেয়:

⟦CODE27⟧

### Logging middleware { #logging-middleware }

`wrap_*` ধরন কাজের যখন একটি কাজের input আর output দুটোই পর্যবেক্ষণ বা সময় মাপতে হয়। এখানে একটি capability যা প্রতিটি মডেল রিকোয়েস্ট আর টুল কল log করে:

⟦CODE28⟧


## Capability প্রকাশ { #publishing-capabilities }

একটি নিজস্ব capability-কে [agent specs](../agent-spec.md)-এ ব্যবহারযোগ্য করতে, এর একটি [`get_serialization_name`][pydantic_ai.capabilities.AbstractCapability.get_serialization_name] (ডিফল্ট ক্লাসের নাম) আর serialize-যোগ্য আর্গুমেন্ট নেওয়া একটি constructor লাগে। ডিফল্ট [`from_spec`][pydantic_ai.capabilities.AbstractCapability.from_spec] বাস্তবায়ন `cls(*args, **kwargs)` ডাকে, তাই সহজ dataclass-এর জন্য কোনো override লাগে না:

⟦CODE29⟧

ব্যবহারকারীরা [`Agent.from_spec`][pydantic_ai.agent.Agent.from_spec] বা [`Agent.from_file`][pydantic_ai.agent.Agent.from_file]-এর `custom_capability_types` প্যারামিটার দিয়ে নিজস্ব capability টাইপ নিবন্ধন করেন।

constructor এমন টাইপ নিলে যা YAML/JSON-এ প্রকাশ করা যায় না, তখন [`from_spec`][pydantic_ai.capabilities.AbstractCapability.from_spec] override করুন। spec ফিল্ড dataclass ফিল্ডের প্রতিচ্ছবি হওয়া উচিত, কিন্তু serialize-যোগ্য টাইপসহ:

⟦CODE30⟧

YAML-এ এটি হবে `- ConditionalTools: {hidden_tools: [dangerous_tool]}`। Python কোডে, পুরো constructor উপলব্ধ: `ConditionalTools(condition=my_check, hidden_tools=['dangerous_tool'])`।

প্যাকেজিংয়ের রীতি আর বৃহত্তর সম্প্রসারণ ইকোসিস্টেমের জন্য দেখুন [Extensibility](../extensibility.md)।

/// check | সংক্ষেপে মনে রাখুন

* `AbstractCapability` subclass করুন: কনফিগারেশন মেথড (`get_toolset`, `get_instructions`, `get_model_settings`, `get_model`...) আর lifecycle hook।
* প্রতিটি পর্যায়: `wrap_*` → `before_*` → মূল কাজ (`on_*_error`) → `after_*`; প্রথম capability সবচেয়ে বাইরের স্তর।
* `before_*` তালিকার ক্রমে, `after_*` আর `on_*_error` উল্টো ক্রমে; error hook-এ ফেরত দিলে উদ্ধার, তুললে প্রচার।
* অনুমোদন/deferral `before_tool_execute` বা `after_tool_validate`-এ — টুল চলার আগে।
* প্রতি-রান state থাকলে `for_run` থেকে নতুন instance; `self` কখনো বদলাবেন না।
* durable-এ `@durable_operation(name=...)` আর স্থিতিশীল `id`; ক্রম নিয়ন্ত্রণে `get_ordering`।

///
