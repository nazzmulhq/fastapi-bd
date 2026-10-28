# সমস্যা সমাধান { #troubleshooting }

/// note | এই পেজে যা শিখবেন

Pydantic AI ব্যবহারের সময় সবচেয়ে প্রচলিত এররগুলো আর তাদের সমাধান: Jupyter-এ event loop, বন্ধ হয়ে যাওয়া event loop, টুলের ভেতর থেকে `run_sync()`, API key, আর HTTP রিকোয়েস্ট দেখা।

///

Pydantic AI ব্যবহারের সময় যে প্রচলিত এররগুলো পেতে পারেন, নিচে সেগুলো ঠিক করার কিছু পরামর্শ দেওয়া হলো। আপনার সমস্যাটি নিচে না থাকলে বা ডকুমেন্টেশনে আলোচিত না হলে, নির্দ্বিধায় [Pydantic Slack](help.md)-এ জিজ্ঞাসা করুন বা [GitHub](https://github.com/pydantic/pydantic-ai/issues)-এ একটি issue তৈরি করুন।

## Jupyter Notebook-এর এরর { #jupyter-notebook-errors }

### `RuntimeError: This event loop is already running` { #runtimeerror-this-event-loop-is-already-running }

**আধুনিক Jupyter/IPython (7.0+)**: এই পরিবেশ নিজে থেকেই শীর্ষ-স্তরের `await` সমর্থন করে। বাড়তি সেটআপ ছাড়াই notebook cell-এ সরাসরি [`Agent.run()`][pydantic_ai.agent.Agent.run] ব্যবহার করতে পারেন:

⟦CODE1⟧

**পুরনো পরিবেশ বা নির্দিষ্ট integration**: event loop-এর সংঘাত হলে, [`nest-asyncio`](https://pypi.org/project/nest-asyncio/) ব্যবহার করুন:

⟦CODE2⟧

**মনে রাখুন**: এটি Google Colab আর [Marimo](https://github.com/marimo-team/marimo) পরিবেশেও প্রযোজ্য।

/// tip | উদাহরণ দিয়ে বুঝি

Jupyter নিজেই একটি event loop (async কাজের "চালক") চালাচ্ছে। `run_sync()` নিজের আরেকটি চালক চালাতে চায়, ফলে এক গাড়িতে দুই চালক। তাই notebook-এ সরাসরি `await agent.run(...)` লিখুন, এতে Jupyter-এর চালকই কাজটি করে।

///

## `RuntimeError: Event loop is closed` { #runtimeerror-event-loop-is-closed }

[`Agent.run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync]-এর মতো synchronous মেথড thread-এর বর্তমান event loop আবার ব্যবহার করে, আর অন্য কোড সেটি বন্ধ করে দিলে নতুন একটি বসায়। একটি মডেল রিকোয়েস্টের সময় এই এরর `httpx2` (বা পুরনো `httpx`)-এর ভেতর থেকে উঠলে, বুঝবেন এজেন্টটি তার event loop বন্ধ হওয়ার আগেই ব্যবহার হয়েছিল: প্রোভাইডারের HTTP connection pool তখনো মৃত loop-এ বাঁধা সংযোগ ধরে রেখেছে। এজেন্টটি তার মডেল আর প্রোভাইডারসহ নতুন করে তৈরি করুন (বা প্রোভাইডারকে একটি নতুন `http_client` দিন); বিদ্যমান একটি `Model` instance আবার ব্যবহার করলে মৃত connection pool থেকেই যায়। অন্য কোড এখনো ব্যবহার করছে এমন event loop বন্ধ করা এড়িয়ে চলুন।

## [`UserError`][pydantic_ai.exceptions.UserError]: `Agent.run_sync()` আর `Agent.run_stream_sync()` একটি synchronous টুল, আউটপুট ফাংশন, বা এজেন্ট রানের সময় ডাকা অন্য ফাংশনের ভেতরে ব্যবহার করা যায় না { #usererror-agentrun_sync-and-agentrun_stream_sync-cannot-be-used-inside-a-synchronous-tool-output-function-or-other-function-called-during-an-agent-run }

এই এররের মানে, একটি synchronous [টুল](tools.md), [আউটপুট ফাংশন](output.md#output-functions), বা এজেন্ট রানের সময় ডাকা অন্য ফাংশন [`Agent.run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync] বা [`Agent.run_stream_sync()`][pydantic_ai.agent.AbstractAgent.run_stream_sync] দিয়ে একটি নেস্টেড রান শুরু করার চেষ্টা করেছে। sync রান মেথডগুলো শুধু সাধারণ অ্যাপ্লিকেশন কোড থেকে, একটি রানের বাইরে ব্যবহার করা যায়: রানের ভেতরে, অভিভাবক রান তখনো আপনার ফাংশনের জন্য অপেক্ষা করছে আর নেস্টেড রান তাকে আটকে রাখে, যাতে deadlock (দুজনেই একে অপরের অপেক্ষায় চিরকাল আটকে থাকা) হতে পারে, তাই Pydantic AI বদলে এই এরর তোলে।

দায়িত্ব দেওয়া (delegating) ফাংশনটিকে `async def` করুন আর ভেতরের রানটি `await` করুন, যেমন দেখানো আছে [Agent delegation](multi-agent-applications.md#agent-delegation)-এ। অভিভাবক এজেন্ট তবুও সাধারণ synchronous অ্যাপ্লিকেশন কোড থেকে `run_sync()` দিয়ে শুরু করা যায়। দায়িত্ব দেওয়া ফাংশনে কিছু আটকে রাখা (blocking) কাজও করতে হলে, শুধু সেই অংশটি [`asyncio.to_thread()`][asyncio.to_thread]-এ পাঠান।

## API key কনফিগারেশন { #api-key-configuration }

### [`UserError`][pydantic_ai.exceptions.UserError]: `[PROVIDER]_API_KEY` environment variable সেট করুন বা প্রোভাইডারের `api_key=...` আর্গুমেন্টে দিন { #usererror-set-the-provider_api_key-environment-variable-or-pass-it-via-the-providers-api_key-argument }

আপনার মডেলের API key সেট করতে সমস্যা হলে, একটি environment variable সেট করা আর/অথবা `api_key` আর্গুমেন্ট দেওয়া নিয়ে আরও জানতে [Models](models/overview.md) পেজটি দেখুন।

API key ছাড়া Pydantic AI চেষ্টা করতে, built-in [`'test'` মডেল](testing.md#unit-testing-with-testmodel) ব্যবহার করুন: [`Agent('test')`][pydantic_ai.agent.Agent]।

/// tip | উদাহরণ

```bash
export OPENAI_API_KEY='sk-...'      # macOS / Linux
setx OPENAI_API_KEY "sk-..."        # Windows (নতুন টার্মিনালে কার্যকর হয়)
```

key কখনো কোডে সরাসরি লিখে git-এ তুলবেন না; environment variable বা `.env` ফাইল (git-এ না তুলে) ব্যবহার করুন।

///

## HTTPX রিকোয়েস্ট পর্যবেক্ষণ { #monitoring-httpx-requests }

চলার সময় নির্দিষ্ট রিকোয়েস্ট, রেসপন্স আর হেডার দেখতে আপনার মডেলে নিজের `httpx2` (বা পুরনো `httpx`) client ব্যবহার করতে পারেন।

এগুলো পর্যবেক্ষণে `logfire`-এর [HTTPX integration](logfire.md#monitoring-http-requests) ব্যবহার বিশেষভাবে কাজের।

/// check | সংক্ষেপে মনে রাখুন

* notebook-এ `await agent.run(...)`; সাধারণ script-এ `agent.run_sync(...)`।
* টুলের ভেতরে আরেকটি এজেন্ট চালাতে টুলটিকে `async def` করে `await other_agent.run(...)`।
* API key environment variable-এ; key ছাড়া পরীক্ষায় `Agent('test')`।

///
