
# Dependencies { #dependencies }

/// note | এই পেজে যা শিখবেন

* dependency injection কী, আর এজেন্টের নির্দেশনা, টুল আর আউটপুট validator-এ ডেটা ও সেবা (যেমন HTTP client, API key, ডেটাবেস সংযোগ) কীভাবে পৌঁছায়।
* `deps_type` আর `deps` দিয়ে dependency সংজ্ঞায়িত করা, `RunContext.deps` দিয়ে পড়া।
* async বনাম sync dependency, আর টেস্টে `agent.override()` দিয়ে dependency বদলানো।

///

আপনার এজেন্টের [নির্দেশনা](agent.md#instructions), [টুল](tools.md) আর [আউটপুট validator](output.md#output-validator-functions)-এ ডেটা আর সেবা পৌঁছে দিতে Pydantic AI একটি dependency injection ব্যবস্থা ব্যবহার করে।

Pydantic AI-এর dependency ব্যবস্থা Python-এর প্রতিষ্ঠিত রীতি মেনে চলে, ফলে dependency হয় টাইপ-নিরাপদ, বোধগম্য, পরীক্ষা করা সহজ, আর প্রোডাকশনে deploy করাও সহজ।

/// tip | উদাহরণ দিয়ে বুঝি

FastAPI-এর `Depends()` মনে আছে? এটাও একই ভাবনা। এজেন্ট চালানোর সময় আপনি একটি "ব্যাগ" (`deps`) দেন, যাতে থাকে সংযোগ, চাবি, ব্যবহারকারীর তথ্য। এজেন্টের প্রতিটি টুল বা নির্দেশনা ফাংশন `ctx.deps` থেকে সেই ব্যাগ খুলে দরকারি জিনিস নেয়। global variable লাগে না, আর টেস্টে ব্যাগটা নকল জিনিস দিয়ে বদলে দেওয়া যায়।

///

## Dependency সংজ্ঞায়িত করা { #defining-dependencies }

dependency যেকোনো python টাইপ হতে পারে। সহজ ক্ষেত্রে হয়তো একটিমাত্র অবজেক্টকে dependency হিসেবে দিতে পারেন (যেমন একটি HTTP সংযোগ), তবে আপনার dependency-তে একাধিক অবজেক্ট থাকলে সাধারণত [dataclass][dataclasses] একটি সুবিধাজনক পাত্র।

dependency দরকার এমন একটি এজেন্ট সংজ্ঞায়িত করার উদাহরণ।

(**মনে রাখুন:** এই উদাহরণে dependency আসলে ব্যবহার হয়নি, দেখুন নিচের [Dependency পড়া](#accessing-dependencies))

⟦CODE1⟧

1. dependency রাখতে একটি dataclass সংজ্ঞায়িত করুন।
2. [`Agent` constructor][pydantic_ai.agent.Agent.__init__]-এর `deps_type` আর্গুমেন্টে dataclass-এর টাইপটি দিন। **মনে রাখুন**: এখানে আমরা টাইপ দিচ্ছি, instance নয়; এই প্যারামিটার আসলে চলার সময় ব্যবহার হয় না, এটি আছে যাতে এজেন্টের পূর্ণ type checking পাওয়া যায়।
3. এজেন্ট চালানোর সময়, `deps` প্যারামিটারে dataclass-এর একটি instance দিন।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// warning | সাধারণ ভুল

`deps_type=MyDeps` (টাইপ) আর `deps=MyDeps(...)` (instance) গুলিয়ে ফেলবেন না। প্রথমটি এজেন্ট তৈরির সময়, দ্বিতীয়টি প্রতিটি রানে।

///

## Dependency পড়া { #accessing-dependencies }

dependency পড়া হয় [`RunContext`][pydantic_ai.tools.RunContext] টাইপের মাধ্যমে, যা নির্দেশনা ফাংশন ইত্যাদির প্রথম প্যারামিটার হওয়া উচিত।

⟦CODE2⟧

1. [`RunContext`][pydantic_ai.tools.RunContext] চাইলে একটি [`instructions`][pydantic_ai.agent.Agent.instructions] ফাংশনে একমাত্র আর্গুমেন্ট হিসেবে দেওয়া যায়।
2. [`RunContext`][pydantic_ai.tools.RunContext] dependency-র টাইপ দিয়ে প্যারামিটারযুক্ত; এই টাইপ ভুল হলে static type checker এরর দেবে।
3. [`.deps`][pydantic_ai.tools.RunContext.deps] অ্যাট্রিবিউট দিয়ে HTTP client পড়ুন।
4. একই অ্যাট্রিবিউট দিয়ে API key পড়ুন।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

[`.deps`][pydantic_ai.tools.RunContext.deps] ছাড়াও, [`RunContext`][pydantic_ai.tools.RunContext] [`.agent`][pydantic_ai.tools.RunContext.agent] দিয়ে চলমান এজেন্টে পৌঁছানোর সুযোগ দেয়, যা কাজে লাগে যখন [টুল](tools.md), [hook](hooks.md) বা [ক্যাপাবিলিটি](capabilities/overview.md)-কে [`name`][pydantic_ai.agent.Agent.name] বা [`output_type`][pydantic_ai.agent.Agent.output_type]-এর মতো এজেন্টের property পড়তে হয়। [`.realtime`][pydantic_ai.tools.RunContext.realtime] property মডেলের টাইপ পরীক্ষা ছাড়াই রিয়েলটাইম সেশন শনাক্ত করে, আর [`.realtime_session`][pydantic_ai.tools.RunContext.realtime_session] সংযুক্ত হওয়ার পরে টুল আর hook-এর কাছে লাইভ [`RealtimeSession`][pydantic_ai.realtime.RealtimeSession] খুলে দেয়।

| `RunContext`-এর অ্যাট্রিবিউট | কী দেয় |
| --- | --- |
| `ctx.deps` | রানে দেওয়া dependency |
| `ctx.agent` | চলমান এজেন্ট |
| `ctx.usage` | এ পর্যন্তের ব্যবহার (token, রিকোয়েস্ট) |
| `ctx.retry` | বর্তমান আবার-চেষ্টার সংখ্যা |
| `ctx.messages` | এ পর্যন্তের বার্তা |

{% raw %}dependency-র ফিল্ডগুলো [template string](agent-spec.md#template-strings) দিয়ে নির্দেশনা আর বর্ণনাতেও উল্লেখ করা যায় — যেমন, [`TemplateStr('Hello {{name}}')`][pydantic_ai.template.TemplateStr] চলার সময় deps অবজেক্ট থেকে `name` বসিয়ে দেয়। [agent spec](agent-spec.md)-এ, যেখানে callable পাওয়া যায় না, এটি বিশেষভাবে কাজে লাগে।{% endraw %}

### Asynchronous বনাম Synchronous dependency { #asynchronous-vs-synchronous-dependencies }

[নির্দেশনা ফাংশন](agent.md#instructions), [ফাংশন টুল](tools.md) আর [আউটপুট validator](output.md#output-validator-functions) সবই একটি এজেন্ট রানের async context-এ চলে।

এই ফাংশনগুলো synchronous হলে, অর্থাৎ `async def`-এর বদলে `def` দিয়ে সংজ্ঞায়িত হলে, Pydantic AI একটি thread pool-এ
[`run_in_executor`][asyncio.loop.run_in_executor] দিয়ে সেগুলো ডাকে। dependency I/O (নেটওয়ার্ক, ফাইল) করলে `async` ফাংশন ভালো,
যদিও synchronous dependency-ও কাজ করে।

/// note | `run` বনাম `run_sync` আর Asynchronous বনাম Synchronous dependency

synchronous নাকি asynchronous dependency ব্যবহার করবেন, তা আপনি `run` নাকি `run_sync` ব্যবহার করছেন তার থেকে সম্পূর্ণ স্বাধীন — `run_sync` শুধু `run`-এর একটি মোড়ক, আর এজেন্ট সবসময় একটি async context-এ চলে।

///

ওপরের একই উদাহরণ, তবে একটি synchronous dependency দিয়ে:

⟦CODE3⟧

1. এখানে আমরা asynchronous `httpx.AsyncClient`-এর বদলে একটি synchronous `httpx.Client` ব্যবহার করি।
2. synchronous dependency-র সাথে মেলাতে, নির্দেশনা ফাংশন এখন একটি সাধারণ ফাংশন, coroutine নয়।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

## পূর্ণ উদাহরণ { #full-example }

নির্দেশনার পাশাপাশি, dependency [টুল](tools.md) আর [আউটপুট validator](output.md#output-validator-functions)-এও ব্যবহার করা যায়।

⟦CODE4⟧

1. একটি টুলে `RunContext` দিতে, [`tool`][pydantic_ai.agent.Agent.tool] decorator ব্যবহার করুন।
2. `RunContext` চাইলে একটি [`output_validator`][pydantic_ai.agent.Agent.output_validator] ফাংশনে প্রথম আর্গুমেন্ট হিসেবে দেওয়া যায়।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

## Dependency বদলে দেওয়া (override) { #overriding-dependencies }

এজেন্ট পরীক্ষার সময় dependency নিজের মতো করতে পারা কাজের।

কখনো কখনো unit test-এর ভেতরে সরাসরি এজেন্ট ডেকে এটি করা যায়, তবে এজেন্টকে ডাকে এমন অ্যাপ্লিকেশন কোড
চালানোর সময়ও আমরা dependency বদলে দিতে পারি।

এটি করা হয় এজেন্টের [`override`][pydantic_ai.agent.Agent.override] মেথড দিয়ে।

⟦CODE5⟧

1. নির্দেশনা নিজের মতো করা সহজ করতে dependency-তে একটি মেথড সংজ্ঞায়িত করুন।
2. নির্দেশনা ফাংশনের ভেতর থেকে নির্দেশনা তৈরির ফাংশনটি (factory) ডাকুন।
3. এজেন্টকে ডাকা অ্যাপ্লিকেশন কোড; একটি আসল অ্যাপ্লিকেশনে এটি হয়তো একটি API endpoint।
4. অ্যাপ্লিকেশন কোডের ভেতর থেকে এজেন্ট ডাকুন; একটি আসল অ্যাপ্লিকেশনে এই ডাক হয়তো ডাকের স্তূপের অনেক গভীরে। মনে রাখুন, dependency বদলানো থাকলে এখানের `app_deps` ব্যবহার হবে *না*।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

⟦CODE6⟧

1. নির্দেশনা তৈরির ফাংশন নিজের মতো করতে টেস্টে `MyDeps`-এর একটি subclass সংজ্ঞায়িত করুন।
2. টেস্ট dependency-র একটি instance তৈরি করুন। এর `http_client` ব্যবহার হয় না, কারণ টেস্টের নির্দেশনা ফাংশন কোনো রিকোয়েস্ট পাঠায় না।
3. `with` ব্লক চলাকালীন এজেন্টের dependency বদলে দিন; এজেন্ট চলার সময় `test_deps` ব্যবহার হবে।
4. এখন আমরা নিরাপদে আমাদের অ্যাপ্লিকেশন কোড ডাকতে পারি; এজেন্ট বদলানো dependency ব্যবহার করবে।

## উদাহরণ { #examples }

নিচের উদাহরণগুলো দেখায় Pydantic AI-তে dependency কীভাবে ব্যবহার করতে হয়:

- [Weather Agent](examples/weather-agent.md)
- [SQL Generation](examples/sql-gen.md)
- [RAG](examples/rag.md)

/// check | সংক্ষেপে মনে রাখুন

* `Agent(..., deps_type=MyDeps)` আর `agent.run(..., deps=MyDeps(...))`।
* টুল/নির্দেশনা/validator-এ `ctx: RunContext[MyDeps]`, তারপর `ctx.deps.x`।
* I/O থাকলে `async def`; টেস্টে `with agent.override(deps=test_deps):`।

///
