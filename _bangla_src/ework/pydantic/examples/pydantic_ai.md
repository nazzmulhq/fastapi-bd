# Agent লাইব্রেরি – Pydantic AI { #agent-libraries-pydantic-ai }

/// note | এই পেজে যা শিখবেন

* Pydantic AI কী, আর LLM-এর উত্তরকে কীভাবে একটি Pydantic মডেলের গঠনে বাঁধা যায় (structured output)।
* validator ব্যর্থ হলে Pydantic AI কীভাবে মডেলকে আবার চেষ্টা করতে বলে।

///

[Pydantic AI](https://pydantic.dev/docs/ai/overview/) হলো Pydantic দলের তৈরি একটি Python agent framework, যা [structured output](https://pydantic.dev/docs/ai/core-concepts/output/#structured-output)-এর schema তৈরি আর যাচাইয়ে Pydantic validation ব্যবহার করে।
একটি Agent-এ `output_type` উল্লেখ করে, আপনি LLM-কে এমন ডেটা ফেরত দিতে বাধ্য করতে পারেন যা আপনার Pydantic মডেলের schema-র সাথে মেলে।

/// tip | উদাহরণ দিয়ে বুঝি

LLM-কে খোলা প্রশ্ন করলে সে গল্পের মতো উত্তর দেয়, যা কোডে ব্যবহার করা কঠিন। `output_type=list[City]` দেওয়া মানে তাকে একটি ছক কাটা খাতা দেওয়া: "নাম, দেশ, জনসংখ্যা, এই ঘরগুলো পূরণ করে দাও"। উত্তর ঘরের সাথে না মিললে (যেমন জনসংখ্যা ঋণাত্মক) খাতা ফেরত দিয়ে বলা হয় "আবার লেখো"।

///

## LLM-এর গোছানো আউটপুট { #llm-structured-output }

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

* `City` মডেল ঠিক করে দেয় প্রতিটি শহরের কী কী তথ্য লাগবে; `population`-এর `description` মডেলকে (LLM) বোঝায় ফিল্ডটি কী।
* `validation_context=[...]` শুধু Pydantic validator-এর জন্য (`info.context`), LLM-এ পাঠানো হয় না। এখানে এটি অনুমোদিত দেশের তালিকা।
* `result.output` সরাসরি `list[City]`, অর্থাৎ যাচাই হওয়া Python অবজেক্ট; লেখা পার্স করার ঝামেলা নেই।

///

যাচাই ব্যর্থ হলে (ধরুন মডেল এমন একটি দেশ ফেরত দিল যা আপনার validator প্রত্যাখ্যান করে), Pydantic AI যাচাইয়ের
এররগুলো মডেলের কাছে ফেরত পাঠায় আর তাকে আবার চেষ্টা করতে বলে। একটি আসল অ্যাপ্লিকেশনে এটি ঘটতে দেখতে,
[Logfire](../integrations/logfire.md) দিয়ে instrument করুন, যা
[Pydantic AI](https://pydantic.dev/docs/ai/integrations/logfire/)-এর run আর তার ভেতরের যাচাইগুলো রেকর্ড করে: প্রতিটি agent run-এ
দেখা যায় মডেল কী আউটপুট দিয়েছিল, আপনার validator কোন এরর তুলেছিল, আর তারপর যে পুনরায় চেষ্টা হয়েছিল।

/// check | সংক্ষেপে মনে রাখুন

* `Agent(..., output_type=YourModel)` দিলে LLM-এর উত্তর আপনার মডেলের গঠনে আসে আর যাচাই হয়।
* validator-এর এরর মডেলের কাছে ফেরত যায়, আর মডেল ঠিক করে আবার চেষ্টা করে।
* বাড়তি তথ্য validator-এ দিতে `validation_context`।

///
