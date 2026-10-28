# LLMs { #llms }

/// note | এই পেজে যা শিখবেন

* AI টুলকে (ChatGPT, Claude, Copilot...) Pydantic ডকুমেন্টেশন দেওয়ার জন্য `llms.txt` আর `llms-full.txt` ফাইল।
* ডকুমেন্টেশনের বদলে আপনার অ্যাপের চলমান ডেটা AI-কে দিতে Logfire MCP server।

///

Pydantic ডকুমেন্টেশন [llms.txt](https://llmstxt.org/) ফরম্যাটে পাওয়া যায়।
এই ফরম্যাট Markdown-এ সংজ্ঞায়িত আর বড় ভাষা মডেলের (LLM) জন্য উপযোগী।

দুটি ফরম্যাট পাওয়া যায়:

* [llms.txt](https://pydantic.dev/docs/validation/latest/llms.txt): প্রজেক্টের একটি সংক্ষিপ্ত বর্ণনা আর
  ডকুমেন্টেশনের বিভিন্ন অংশের লিংকসহ একটি ফাইল। এই ফাইলের গঠন
  [ফরম্যাট ডকুমেন্টেশনে](https://llmstxt.org/#format) বিস্তারিত বর্ণিত।
* [llms-full.txt](https://pydantic.dev/docs/validation/latest/llms-full.txt): `llms.txt` ফাইলের মতোই,
  তবে প্রতিটি লিংকের বিষয়বস্তু ভেতরে দেওয়া। মনে রাখুন, কিছু LLM-এর জন্য এই ফাইলটি খুব বড় হতে পারে।

/// tip | কীভাবে কাজে লাগাবেন

AI চ্যাটে Pydantic নিয়ে প্রশ্ন করার আগে `llms-full.txt`-এর লিংক বা বিষয়বস্তু দিয়ে দিন। তাহলে AI পুরনো (V1) নিয়মে উত্তর না দিয়ে সর্বশেষ ডকুমেন্টেশন অনুযায়ী উত্তর দেবে।

///

আজ পর্যন্ত, LLM framework বা IDE এই ফাইলগুলো নিজে থেকে কাজে লাগাতে *পারে না*। বিকল্প হিসেবে,
`llms.txt` ফাইল ঠিকভাবে পার্স করতে একটি [MCP server](https://modelcontextprotocol.io/) বাস্তবায়ন করা যায়।

যেখানে `llms.txt` একটি AI টুলকে Pydantic-এর *ডকুমেন্টেশন* দেয়, সেখানে
[Logfire MCP server](https://pydantic.dev/docs/logfire/guides/mcp-server/) একে দেয় আপনার
অ্যাপ্লিকেশনের *চলার সময়ের ডেটা*: একটি agent আপনার নিজের সার্ভিসের trace, metric আর রেকর্ড হওয়া যাচাই
query করতে পারে, আর যেমন, আপনাকে ঠিক করতে সাহায্য করার সময় একটি [`ValidationError`][pydantic_core.ValidationError]-এর
পেছনের ইনপুট বের করে আনতে পারে।
