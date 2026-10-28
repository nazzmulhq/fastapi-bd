
# Pydantic AI Harness { #pydantic-ai-harness }

*আপনার এজেন্টের প্রিয় harness, Pydantic AI-এর ওপর তৈরি*

⟦CODE1⟧

/// note | এই পেজে যা শিখবেন

* Pydantic AI Harness কী — Pydantic AI-এর অফিসিয়াল capability আর harness লাইব্রেরি।
* `Coder` দিয়ে কয়েক লাইনে একটি সম্পূর্ণ coding এজেন্ট, আর কীভাবে এটি সাধারণ capability-র জোড়া।
* Workspace (লোকাল বনাম sandbox), সব capability-র বিষয়ভিত্তিক তালিকা, ইনস্টল আর version policy।

///

**Pydantic AI Harness** হলো [Pydantic AI](../index.md)-এর অফিসিয়াল [capability](../capabilities/overview.md) আর harness লাইব্রেরি। প্রতিটি Pydantic AI এজেন্টের আগে থেকেই একটি হালকা harness আছে: টাইপ করা এজেন্ট loop, [যেকোনো মডেল](../models/overview.md), আপনার নিজের টুল, কাঠামোবদ্ধ আউটপুট। সহজ এজেন্টের জন্য এটুকুই যথেষ্ট। কিন্তু একটি এজেন্টকে জটিল, দীর্ঘ-চলা কাজে ছেড়ে দিন (একটি codebase ঠিক করা, একটি প্রশ্ন নিয়ে গবেষণা, ঘণ্টার পর ঘণ্টা তত্ত্বাবধান ছাড়া চলা), আর মডেলের চারপাশে এর যা লাগে তা বাড়তে থাকে: কাজ করার একটি [workspace](filesystem.md), হালনাগাদ রাখা একটি [পরিকল্পনা](planning.md), session জুড়ে বহন করা [memory](memory.md), কাজ দেওয়ার [sub-agent](subagents.md), দশম ঘণ্টাতেও টিকে থাকা [context ব্যবস্থাপনা](compaction.md), আর restart থেকে টিকে থাকা [durable execution](../durable_execution/overview.md)। **Pydantic AI Harness** সেই harness দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

"Harness" মানে ঘোড়ার সাজ — লাগাম, জিন, রেকাব। ঘোড়া (মডেল) শক্তিশালী, কিন্তু সাজ ছাড়া তাকে দিয়ে দীর্ঘ যাত্রায় কাজ করানো কঠিন। Harness হলো মডেলের চারপাশের সেই সব যন্ত্রপাতি — ফাইল পড়া-লেখা, shell, পরিকল্পনা, memory, sub-agent — যা একটি LLM-কে একটি কাজের এজেন্টে পরিণত করে।

///

এখানকার সবকিছু একটি মৌলিক উপাদান: একটি [capability](../capabilities/overview.md), এজেন্ট আচরণের একটি স্বয়ংসম্পূর্ণ একক, যা আপনি যেকোনো এজেন্টের `capabilities=[...]`-এ যোগ করেন। এমন [30+টি আছে](#capabilities), আর [Coder](coder.md) আর [Researcher](researcher.md)-এর মতো সম্পূর্ণ এজেন্ট নিজেরাই capability-র জোড়া: যেভাবে জোড়া লেগেছে সেভাবেই খুলে আলাদা করা যায়। একটি একক ব্লক লাগান, নিজের stack গড়ুন, বা পুরো coding এজেন্ট দিয়ে শুরু করে পরে খুলে ফেলুন।

## দ্রুত শুরু { #quick-start }

[`uv`](https://docs.astral.sh/uv/) দিয়ে ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-harness[coder,anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[coder,anthropic]"
```

///


<!-- Keep this blown-out example in sync across docs/coder.md, docs/index.md, README.md, pydantic_ai_harness/coder/README.md, and examples/coding_agent.py. -->

⟦CODE2⟧

`LocalWorkspace('.')` হলো যেখানে এজেন্ট কাজ করে: এর ফাইল টুল আর কমান্ড আপনার মেশিনে, এই ডিরেক্টরিতে চলে। এটি একটি sandbox নয়, তাই কমান্ড আপনি যা যা ছুঁতে পারেন তার সবকিছুতে পৌঁছাতে পারে। একই এজেন্ট একটি বিচ্ছিন্ন cloud মেশিনে চালাতে, এটি একটি sandbox capability (Modal, E2B, Sprites বা Daytona) দিয়ে বদলান; দেখুন [Workspaces](#workspaces)।

যেমন [Modal](modal-sandbox.md) দিয়ে:

⟦CODE3⟧

/// warning | সতর্কতা

`LocalWorkspace`-এ `Coder`-এর `shell` টুল **অসীমাবদ্ধ** — মডেল আপনার ব্যবহারকারী-অনুমতিতে যেকোনো কমান্ড চালাতে পারে (`rm -rf` সহ)। অবিশ্বস্ত ইনপুট বা অপরিচিত কোডবেসে কাজ করালে একটি sandbox (Modal, E2B, Docker...) ব্যবহার করুন।

///

Coder ছয়টি টুল দেয়: `read_file`, `write_file`, `edit_file`, `list_files`, `grep` আর `shell`, সাথে একই এজেন্টের একটি নতুন রানকে একটি উপ-কাজ দিতে `delegate_task`, repository context আর context নিয়ন্ত্রণ। Shell কমান্ড অসীমাবদ্ধ আর আলাদা রানের পরেও টিকে থাকতে পারে। ডিফল্ট instructions স্বয়ংক্রিয় অনুসন্ধান, সম্পাদনা আর যাচাইয়ের পথ দেখায়; নিজের নির্দেশনা যোগ করতে `instructions=` দিন।

```bash
uvx --with "pydantic-ai-harness[coder]" clai -a pydantic_ai_harness.coder:coder_agent -m anthropic:claude-opus-5-5
```

বান্ডেল করা `coder_agent` হলো ওপরের উদাহরণ, মডেল ছাড়া।

প্রতিটি মডেল কাজ করে: string-টি [যেকোনো provider-এর](../models/overview.md) একটিতে বদলান। আরও লাগবে? লিস্টে capability যোগ করুন; এখানে একই coder `gpt-6.1-sol`-এ, web search আর session-জুড়ে memory-সহ:

/// tab | pip

```bash
pip install "pydantic-ai-slim[openai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[openai]"
```

///


⟦CODE4⟧

[Skills](skills.md) (আপনার `SKILL.md` পদ্ধতি, চাহিদামতো লোড; একটি `skills/` ডিরেক্টরিতে নির্দেশ করুন আর `skills` extra যোগ করুন), [Web Fetch](../capabilities/web-fetch.md), [Guardrails](guardrails.md) আর [Dynamic Workflow](dynamic-workflow.md) একইভাবে বসে যায়।

## কোনো জাদু নেই: আগাগোড়া শুধু capability { #no-magic-its-capabilities-all-the-way-down }

`Coder` একটি সাধারণ জোড়া capability: [`FileSystem`](filesystem.md), এর পাঁচটি টুলসহ আর content hash বন্ধ, [`Shell`](shell.md), এর স্থায়ী `shell` টুলসহ আর কোনো allowlist ছাড়া, [`RepoContext`](repo-context.md), এজেন্টকে নিজেকেই কাজ দেওয়া [`SubAgents`](subagents.md), [`ClearToolResults`](compaction.md), আর একটি সীমিত [`ToolOutputLimits`](tool-output-limits.md), সাথে এর ডিফল্ট instructions আর JSON আর্গুমেন্ট মেরামত। পুরোটা ব্যবহার করুন, বা যেকোনো সেটিং বদলাতে ওই capability-গুলো থেকে একই এজেন্ট তৈরি করুন; [Coder পেজ](coder.md) সঠিক কনফিগারেশন, টুলের signature, কাজ দেওয়া আর স্থায়ী shell lifecycle তালিকা করে।

একটি দূরের sandbox-এ, `Coder` রানের শুরুতে repo instructions লোড করে আর প্রথম মডেল টুল কলের আগেই sandbox তৈরি করতে পারে। অলসভাবে (দরকার হলে তবেই) তৈরির জন্য `Coder(repo_context=False)` ব্যবহার করুন।

## Workspace { #workspaces }

একটি [workspace](../workspace.md) হলো যেখানে এজেন্টের ফাইল আর কমান্ড থাকে: `LocalWorkspace`-এ আপনার মেশিন, বা একটি বিচ্ছিন্ন sandbox। Harness capability কখনো আপনার জন্য একটি বেছে নেয় না। একটি যুক্ত করুন, নইলে রান শুরুতেই ব্যর্থ হয় আর বলে কী যুক্ত করতে হবে।

[Coder](coder.md), [FileSystem](filesystem.md), [Shell](shell.md), [Repo Context](repo-context.md) আর [Macroscope](macroscope.md) রানের workspace-এ কাজ করে, এর working directory থেকে শুরু করে। একটি সাবডিরেক্টরিতে কাজ করতে, সেটি workspace-এ সেট করুন: `LocalWorkspace('./repo')`। পরের একটি রান বা অন্য একটি এজেন্ট থেকে একই ফাইলে চালিয়ে যেতে, দেখুন [Sharing a workspace](coder.md#sharing-a-workspace)।

Skills, SubAgents, ToolOutputLimits আর Memory-র `FileStore` নিজের ফাইলের জন্যও রানের workspace ব্যবহার করে। এজেন্ট একটি sandbox-এ কাজ করার সময় ওই ফাইলগুলো আপনার মেশিনে রাখতে, এদের একটি লোকাল অবস্থানে নির্দেশ করুন:

⟦CODE5⟧

ডিফল্টভাবে, harness ফাইল (Shell-এর background job log, টুল-আউটপুট ঢালা) workspace-এর working directory-তে `.pydantic-ai-harness/`-এ যায়, যা git-এ উপেক্ষিত।

Step Persistence-এর file আর SQLite store, Media-র disk আর SQLite store, আর Code Mode mount এজেন্ট চালানো মেশিনের path ব্যবহার করে, রানের workspace নয়।

`FileSystem`-এর `root_dir` শুধু ফাইল টুল সীমিত করে, `Shell` কমান্ড নয়।

আগের একটি release থেকে আপগ্রেড করছেন? কী বদলেছে তা [Coder পেজ](coder.md#upgrading) তালিকা করে।

## Capability { #capabilities }

প্রতিটি capability একটি স্বয়ংসম্পূর্ণ একক যা আপনি `capabilities=[...]`-এ বসান, আর এরা সবাই মিলে যায়, একে অপরের সাথে আর আপনার নিজেরগুলোর সাথে। কিছু [`pydantic-ai`](../index.md)-এর সাথেই আসে, বাকিগুলো এই প্যাকেজের সাথে; **Package** কলাম বলে কোনটি। মোট 50+, আপনার এজেন্টকে যা দেয় তা অনুযায়ী ভাগ করা:

### Harness { #harnesses }

সাধারণ জোড়া capability হিসেবে সম্পূর্ণ এজেন্ট stack: একটি import আপনাকে একটি কাজ করা এজেন্ট দেয়, আর আপনি যেকোনোটি নিচের ব্লকগুলোতে খুলে আলাদা করতে পারেন।

| Harness | Package | যা দেয় |
|---|---|---|
| [Coder](coder.md) | Harness | ছয়টি coding টুল, স্থায়ী shell কমান্ড, নিজেকে কাজ দেওয়া, স্বয়ংক্রিয় নির্দেশনা আর context নিয়ন্ত্রণ |
| [Researcher](researcher.md) | Harness | একটি সম্পূর্ণ ওয়েব-গবেষণা stack: সার্চ, পেজ আনা, একটি কাজ-দেওয়া sub-researcher আর সীমিত টুল আউটপুট |

### Execution environment { #execution-environments }

এজেন্ট যে workspace-এ কাজ করে: এটি যে ফাইল সম্পাদনা করে আর যে কমান্ড চালায়, লোকাল বা বিচ্ছিন্ন।

| Capability | Package | যা করে |
|---|---|---|
| [FileSystem](filesystem.md) | Harness | রানের workspace-এ একটি root-এর নিচে ফাইল পড়া, লেখা, সম্পাদনা, তালিকা আর খোঁজা, ঐচ্ছিক ripgrep টুলসহ; path-traversal যাচাই করা, secret শুধু-পড়া |
| [Smart Search](smart-search.md) | Harness | রানের workspace-এ আচরণ দিয়ে কোড সার্চ: সাধারণ-ইংরেজি query, র‍্যাঙ্ক করা অংশ, যেকোনো মডেল দিয়ে বিচার (System One-এর ওপর একটি decision model, বা TypeSafe-এর Jev, সুপারিশকৃত) |
| [Shell](shell.md) | Harness | রানের workspace-এ allowlist, denylist, timeout, credential-ছাঁটাই আর রানের পরেও টিকে থাকা ঐচ্ছিক কমান্ডসহ কমান্ড চালানো |
| [Modal Sandbox](modal-sandbox.md) | Harness | একটি বিচ্ছিন্ন [Modal](https://modal.com) cloud sandbox-এ কমান্ড আর ফাইল |
| [E2B Sandbox](e2b-sandbox.md) | Harness | একটি বিচ্ছিন্ন [E2B](https://e2b.dev) cloud sandbox-এ কমান্ড আর ফাইল |
| [Sprites Sandbox](sprites-sandbox.md) | Harness | একটি স্থায়ী [Fly.io Sprite](https://sprites.dev)-এ কমান্ড আর ফাইল |
| [Daytona Sandbox](daytona-sandbox.md) | Harness | একটি বিচ্ছিন্ন [Daytona](https://www.daytona.io) cloud sandbox-এ কমান্ড আর ফাইল |
| [Smol Sandbox](smol-sandbox.md) | Harness | আপনার নিজের মেশিনে একটি [smolvm](https://github.com/smol-machines/smolvm) microVM-এ কমান্ড আর ফাইল; কোনো cloud অ্যাকাউন্ট নয় |
| [BoxLite Sandbox](boxlite-sandbox.md) | Harness | আপনার নিজের মেশিনে একটি [BoxLite](https://github.com/boxlite-ai/boxlite) micro-VM-এ কমান্ড আর ফাইল, ঐচ্ছিক egress allow-list-সহ; কোনো cloud অ্যাকাউন্ট নয় |
| [Docker Sandbox](docker-sandbox.md) | Harness | একটি লোকাল [Docker](https://www.docker.com/) বা Podman container-এ কমান্ড আর ফাইল |
| [SSH Workspace](ssh-workspace.md) | Harness | আপনার `ssh` client দিয়ে একটি দূরের host-এ কমান্ড আর ফাইল; কোনো বিচ্ছিন্নতা নেই |
| [Bubblewrap Sandbox](bubblewrap-sandbox.md) | Harness | আরেকটি workspace capability মোড়ায়, যাতে এর কমান্ড ওই workspace-এর host-এ একটি Linux [bubblewrap](https://github.com/containers/bubblewrap) sandbox-এ চলে |

### টুল আর নেটিভ ক্ষমতা { #tools-native-abilities }

যে ক্ষমতা provider নেটিভভাবে চালায়, আর যেকোনো MCP সার্ভারের সাথে সংযোগ।

| Capability | Package | যা করে |
|---|---|---|
| [MCP](../capabilities/mcp.md) | Core | যেকোনো MCP সার্ভারের টুল যুক্ত করে; ডিফল্টভাবে লোকাল, provider-নেটিভ connector ঐচ্ছিক |
| [Image Generation](../capabilities/image-generation.md) | Core | ছবি তৈরি আর সম্পাদনা; যেখানে সমর্থিত সেখানে provider-নেটিভ, অন্যত্র sub-agent বিকল্প |

### Integration { #integrations }

থার্ড-পার্টি সার্ভিসের টুল, বেশিরভাগ সার্ভিসের নিজস্ব হোস্ট করা MCP সার্ভার দিয়ে। [Integrations](integrations.md) পেজ এদের কীসের সাথে যুক্ত হয় তা অনুযায়ী ভাগ করে।

| Capability | Package | যা করে |
|---|---|---|
| [GitHub](github.md) | Harness | GitHub repository, issue, pull request আর অন্যান্য প্রবেশযোগ্য resource পড়া ও বদলানো। |
| [Linear](linear.md) | Harness | Linear issue, project, team আর comment পড়া ও বদলানো। |
| [Macroscope](macroscope.md) | Harness | একটি লোকাল [Macroscope](https://docs.macroscope.com/cli) কোড রিভিউ চালিয়ে ফলাফল এজেন্টকে দেয় |
| [LocalStack](localstack.md) | Harness | AWS CLI টুলসহ একটি অনুকৃত AWS environment |
| [Google Workspace](google-workspace.md) | Harness | Gmail, Calendar, Drive আর অন্য Google Workspace টুল ব্যবহার। |
| [Notion](notion.md) | Harness | Notion workspace-এর কনটেন্ট খোঁজা আর বদলানো। |
| [Slack](slack.md) | Harness | একটি এজেন্টকে Slack বার্তা, চ্যানেল আর canvas টুল দেয়। |
| [Day AI](day-ai.md) | Harness | [Day AI](https://day.ai)-এর হোস্ট করা MCP সার্ভার দিয়ে CRM রেকর্ড আর মিটিং context খোঁজা ও হালনাগাদ |
| [Grain](grain.md) | Harness | [Grain](https://grain.com)-এর হোস্ট করা MCP সার্ভার দিয়ে মিটিং, transcript আর নোট খোঁজা ও পড়া, আর clip তৈরি ও মিটিং ট্যাগ করা |
| [Pylon](pylon.md) | Harness | [Pylon](https://www.usepylon.com)-এর হোস্ট করা MCP সার্ভার দিয়ে support issue, account আর contact নিয়ে কাজ |
| [StackOne](stackone.md) | Harness | [StackOne](https://www.stackone.com) দিয়ে যুক্ত SaaS অ্যাকাউন্টে (HRIS, ATS, CRM, …) কাজ |
| [PostHog](posthog.md) | Harness | [PostHog](https://posthog.com)-এর হোস্ট করা MCP সার্ভার দিয়ে product analytics query আর feature flag, experiment ও dashboard পরিচালনা |
| [Logfire MCP](logfire-mcp.md) | Harness | Logfire telemetry query আর observability resource পরিচালনা। |
| [Ordinal](ordinal.md) | Harness | [Ordinal](https://www.tryordinal.com)-এর হোস্ট করা MCP সার্ভার দিয়ে সোশ্যাল পোস্টের খসড়া, নির্ধারণ আর বিশ্লেষণ |

### ওয়েব আর গবেষণা { #web-research }

খোলা ওয়েবে জিনিস খোঁজা আর পড়া।

| Capability | Package | যা করে |
|---|---|---|
| [Web Search](../capabilities/web-search.md) | Core | যেখানে পাওয়া যায় সেখানে provider-নেটিভ সার্চ, সব জায়গায় লোকাল DuckDuckGo বিকল্প |
| [Web Fetch](../capabilities/web-fetch.md) | Core | URL আনা আর পড়া, নেটিভ বা লোকাল |
| [X Search](../capabilities/x-search.md) | Core | X-এ সার্চ; xAI-তে নেটিভ, অন্যত্র subagent বিকল্প |
| [Exa Search](exa-search.md) | Harness | [Exa](https://exa.ai) দিয়ে ওয়েব গবেষণা: অংশ-উদ্ধৃত সার্চ, পূর্ণ-পেজ পড়া, ঐচ্ছিক উদ্ধৃতিসহ গভীর সার্চ |
| [Exa Agent](exa-search.md) | Harness | খোলামেলা গবেষণা Exa Agent API-কে দেয় |
| [You.com Search](youdotcom.md) | Harness | [You.com](https://you.com) দিয়ে ওয়েব সার্চ আর পেজ পড়া: query-প্রাসঙ্গিক অংশ বা পূর্ণ-পেজ markdown |
| [You.com Research](youdotcom.md) | Harness | You.com Answer, Research আর Finance Research API দিয়ে উদ্ধৃতিসহ উত্তর আর বহু-ধাপের গবেষণা |
| [Browser Use](browser-use.md) | Harness | একটি আসল browser চালানো একটি স্বয়ংক্রিয় [browser-use](https://github.com/browser-use/browser-use) এজেন্টকে ওয়েব কাজ দেয় |
| [Playwright Browser](playwright.md) | Harness | নিজে একটি আসল Chromium পেজ চালান: navigate, click, type, পড়া আর পেজ কী করেছে তা পরীক্ষা |

### যুক্তি, পরিকল্পনা আর কাজ ভাগ { #reasoning-planning-delegation }

এজেন্ট কীভাবে ভাবে আর কাজ ভাগ করে।

| Capability | Package | যা করে |
|---|---|---|
| [Thinking](../capabilities/thinking.md) | Core | কনফিগার-যোগ্য মাত্রায় provider-অনুযায়ী বর্ধিত thinking |
| [Planning](planning.md) | Harness | একটি cache-নিরাপদ লাইভ রিমাইন্ডারসহ মডেল-নিয়ন্ত্রিত task পরিকল্পনা |
| [Subagents](subagents.md) | Harness | স্বয়ংসম্পূর্ণ কাজ নাম দেওয়া child এজেন্টকে দেয় |
| [Dynamic Workflow](dynamic-workflow.md) | Harness | মডেল একটি Python script থেকে sub-agent চালায়: একটি টুল কলে fan-out, chain, vote, কঠোর `max_agent_calls` বাজেটসহ |
| [Advisor](advisor.md) | Harness | একটি executor-কে রানের মাঝে একটি শক্তিশালী মডেলের পরামর্শ নিতে দেয় |
| [Background Tools](background-tools.md) | Harness | বাছা টুল একসাথে চালায়; ফল পরের বার্তা হিসেবে আসে |

### Context ব্যবস্থাপনা { #context-management }

এজেন্ট কীভাবে এর context window খরচ করে: এটিই পার্থক্য গড়ে একটি এজেন্টের মধ্যে যে দীর্ঘ রানে খারাপ হয়ে যায় আর যে হয় না, আর token-এর জন্য N বার বনাম একবার টাকা দেওয়ার মধ্যে।

| Capability | Package | যা করে |
|---|---|---|
| [Code Mode](code-mode.md) | Harness | মডেল একটি Python script লেখে যা একটি [Monty](https://github.com/pydantic/monty) sandbox-এর ভেতরে অনেক টুল ডাকে: N-এর বদলে একটি round-trip, আর মাঝের ফল কখনো context window-এ ঢোকে না। টুল-কলের token ফোলার উত্তর |
| [Tool Search](../capabilities/tool-search.md) | Core | প্রতিটি prompt-এ শত শত বহন না করে চাহিদামতো টুল সংজ্ঞা লোড |
| [Compaction](../capabilities/compaction.md) | Core | OpenAI আর Anthropic-এ provider-নেটিভ compaction; provider সার্ভার-পক্ষে ইতিহাসের সারাংশ করে |
| [Compaction](compaction.md) | Harness | মডেল-নিরপেক্ষ কৌশল: টুল-ফল মোছা, sliding-window ছাঁটাই, LLM সারাংশ, স্তরভিত্তিক; সবই window-আপেক্ষিক, লাইভ usage রিপোর্টসহ |
| [Tool Output Limits](tool-output-limits.md) | Harness | বড় আকারের টুল ফেরত উৎসেই ছাঁটাই, একটি query-যোগ্য ফাইলে ঢালা, বা সারাংশ |
| [Warn On Cache Busts](warn-on-cache-busts.md) | Harness | provider-এর নিজের সংখ্যা থেকে রিকোয়েস্টের মাঝে prompt-cache prefix ভাঙন ধরে |

### জ্ঞান আর memory { #knowledge-memory }

এজেন্ট যা জানে আর মনে রাখে, প্রতিটি prompt-এ বহন না করে প্রাসঙ্গিক হলে লোড।

| Capability | Package | যা করে |
|---|---|---|
| [Memory](memory.md) | Harness | একটি স্থায়ী, namespace-ভিত্তিক নোটবুক: সীমিত prompt injection, চাহিদামতো সার্চ; in-memory/file/Postgres store |
| [Conversation Search](conversation-search.md) | Harness | সংরক্ষিত ইতিহাসে BM25 সার্চ, compaction-এ বাদ পড়া turn-সহ |
| [Skills](skills.md) | Harness | চাহিদামতো [Agent Skill](../capabilities/on-demand.md) (`SKILL.md`) instructions লোড |
| [Repo Context](repo-context.md) | Harness | রান দিকনির্দেশিত অবস্থায় শুরু: `AGENTS.md`/`CLAUDE.md` + repository কাঠামো |
| [Pydantic AI Docs](pydantic-ai-docs.md) | Harness | চাহিদামতো Pydantic AI ডকুমেন্টেশন খোঁজা |

### নিয়ন্ত্রণ আর নিরাপত্তা { #control-safety }

এজেন্ট কী করতে পারে তা সীমিত রাখা, আর একে instructions-এ রাখা।

| Capability | Package | যা করে |
|---|---|---|
| [Repair Tool Arguments](repair-tool-arguments.md) | Harness | schema যাচাইয়ের আগে ত্রুটিপূর্ণ JSON টুল আর্গুমেন্ট মেরামত। |
| [Guardrails](guardrails.md) | Harness | ব্যবহারকারীর input, টুল কল, টুলের ফল আর আউটপুট যাচাই/আটকানো/মুছে দেওয়া, secret মাস্কিং আর সমান্তরাল async guard-সহ |
| [Prompt Injection Defender](prompt-injection-defender.md) | Harness | লোকাল টুল ফল পরোক্ষ prompt injection-এর জন্য শ্রেণিবদ্ধ করে আর ঐচ্ছিকভাবে উচ্চ-ঝুঁকির ফল আটকে রাখে |
| [Spend Limits](spend.md) | Harness | window-জুড়ে USD/token বাজেট আর প্রতি-response খরচ ট্র্যাকিং, প্রতি মডেল আর প্রতি tenant |
| [Ask User](ask-user.md) | Harness | মডেলকে রানের মাঝে ব্যবহারকারীকে বহু-নির্বাচনী প্রশ্ন করতে দেয়; উত্তরদাতা আপনি দেন (terminal, web, test) |
| [Tool approval](../deferred-tools.md#human-in-the-loop-tool-approval) | Core | চলার আগে মানুষের অনুমোদন লাগে এমন টুল কল চিহ্নিত করে |
| [Tool Call Judge](tool-call-judge.md) | Harness | একটি দ্বিতীয় মডেল প্রতি টুল কলে একটি ঝুঁকি-প্রশ্নের উত্তর দেয় আর টুল ফাংশন চলার আগে কলটি আটকায় |
| [Approval Reviewer](approval-reviewer.md) | Harness | একটি দ্বিতীয় মডেল অনুমোদনের অপেক্ষায় থাকা প্রতিটি কলে একটি ঝুঁকি-প্রশ্নের উত্তর দেয়, কম-ঝুঁকিরগুলো অনুমোদন করে আর বাকিগুলো একজন মানুষের জন্য রাখে |
| [Handle Deferred Tool Calls](../capabilities/handle-deferred-tool-calls.md) | Core | অনুমোদন-স্থগিত টুল কল প্রোগ্রাম দিয়ে মীমাংসা |
| [System Reminders](system-reminders.md) | Harness | instruction ফিকে হওয়া ঠেকাতে রানের মাঝে নির্দেশনার cache-নিরাপদ পুনঃসংযোজন |
| [Trajectory Judge](trajectory-judge.md) | Harness | একটি দ্বিতীয় মডেল প্রতি N রিকোয়েস্টে একটি sliding token window-এ লাইভ রান পর্যালোচনা করে আর মাঝপথে পথ দেখায় |

### নিজেকে সম্প্রসারণ { #self-extension }

| Capability | Package | যা করে |
|---|---|---|
| [Capability Creation](capability-creation.md) | Harness | এজেন্ট একটি রানের সময় *নতুন capability* লেখে, যাচাই করে আর সংরক্ষণ করে; host `store.load_active()` আর `capabilities=` দিয়ে পরের একটি রানে এগুলো লোড করে |

### Execution runtime { #execution-runtime }

loop-এর বাইরে: রান কীভাবে টিকে থাকে, ব্যর্থতা থেকে বাঁচে, আর প্রোডাকশনে পর্যবেক্ষিত ও কনফিগার হয়।

| Capability | Package | যা করে |
|---|---|---|
| [Durable execution](../durable_execution/overview.md) | Core | restart আর ব্যর্থতা থেকে টিকে থাকা রান, আটটি engine-এ: [Temporal](../durable_execution/temporal.md), [DBOS](../durable_execution/dbos.md), [Prefect](../durable_execution/prefect.md), [Restate](../durable_execution/restate.md), [Airflow](../durable_execution/airflow.md), আর পরের সারিগুলোর তিনটি Harness engine। Coder, Shell আর FileSystem-এর জন্য দেখুন [workspace guide](../workspace.md#durable-execution) |
| [AWS Lambda durability](aws-lambda.md) | Harness | মডেল রিকোয়েস্ট আর টুল কল AWS Lambda durable function step-এ checkpoint |
| [Absurd durability](absurd.md) | Harness | মডেল রিকোয়েস্ট, MCP কল আর টুল কল PostgreSQL-এ Absurd step-এ checkpoint |
| [pgtask durability](pgtask.md) | Harness | মডেল রিকোয়েস্ট, MCP কল আর টুল কল PostgreSQL-এ pgtask step-এ checkpoint |
| [Render Workflows](render-workflows.md) | Harness | মডেল রিকোয়েস্ট আর টুল কল আলাদা retry, timeout আর compute সেটিংসহ শৃঙ্খলিত task run হিসেবে চালায়; এজেন্ট চালানো task retry করলে সম্পন্ন কাজ পুনরাবৃত্তি হতে পারে |
| [Step Persistence](step-persistence.md) | Harness | রান সংরক্ষণ, পুনরুদ্ধার, আবার চালানো (`continue_run`) আর fork (`fork_run`); file/SQLite/Mongo backend |
| [Instrumentation](../capabilities/instrumentation.md) | Core | প্রতিটি মডেল আর টুল কলের জন্য OpenTelemetry GenAI span; [Logfire](https://pydantic.dev/logfire) trace-এর কাঁচামাল |
| [Managed Prompt](managed-prompt.md) | Harness | instructions-কে একটি [Logfire](https://pydantic.dev/logfire)-পরিচালিত prompt দিয়ে চালায়; redeploy ছাড়াই version আর চালু |
| [Thread Executor](../capabilities/thread-executor.md) | Core | sync টুল একটি ভাগ করা thread pool-এ চালায় |

Core প্রোডাকশন সার্ভারের জন্য loop-কাস্টমাইজেশন capability-ও দেয়: [Select Model](../capabilities/select-model.md), [Resolve Model ID](../capabilities/resolve-model-id.md), [Prepare Tools / Prepare Output Tools](../capabilities/prepare-tools.md), [Prefix Tools](../capabilities/prefix-tools.md), [Set Tool Metadata](../capabilities/set-tool-metadata.md), [Include Tool Return Schemas](../capabilities/include-tool-return-schemas.md), [Process History](../capabilities/process-history.md), [Process Event Stream](../capabilities/process-event-stream.md), [Reinject System Prompt](../capabilities/reinject-system-prompt.md) আর [Raise Content Filter Error](../capabilities/raise-content-filter-error.md)।

আর এজেন্ট যেকোনো interface-এ যুক্ত হয়: [ACP](acp.md) *(পরীক্ষামূলক, Harness)* [Agent Client Protocol](https://agentclientprotocol.com) দিয়ে Zed-এর মতো editor-এ এটি পরিবেশন করে, আর core দেয় [web chat UI](../web.md), [CLI](../cli.md), [frontend adapters](../ui/overview.md) (AG-UI, Vercel AI) আর [realtime voice](../realtime/overview.md)।

কমিউনিটি প্যাকেজ একই capability ব্যবস্থাকে আরও সম্প্রসারিত করে; দেখুন [third-party capabilities](../capabilities/third-party.md)।

## Harness কখন দরকার? { #when-do-you-need-the-harness }

"Harness" হলো মডেলের চারপাশের সবকিছুর জন্য এই ক্ষেত্রের শব্দ যা একে একটি এজেন্টে পরিণত করে: loop, টুল, context ব্যবস্থাপনা। এই প্যাকেজ ধরুন যখন আপনার এজেন্টের core-এর হালকা harness যা কভার করে তার চেয়ে বেশি *করা* উচিত: ফাইল ছোঁয়া, কোড চালানো, browse করা, মনে রাখা, কাজ দেওয়া, বা ঘণ্টাব্যাপী রান জুড়ে সুসংগত থাকা। প্যাকেজগুলোর সীমা যান্ত্রিক, পরিপক্বতার স্তর নয়: core সেই capability-গুলো দেয় যার মডেল বা framework সমর্থন লাগে (provider-নেটিভ টুল যেমন [image generation](../capabilities/image-generation.md), provider API যেমন [compaction](../capabilities/compaction.md), গভীর loop ইন্টিগ্রেশন যেমন [tool search](../capabilities/tool-search.md), আর মৌলিক জিনিস যেমন [thinking](../capabilities/thinking.md), [MCP](../capabilities/mcp.md) আর [web search](../capabilities/web-search.md)) আর Harness বাকি সব দেয়, একটি আলাদা প্যাকেজ হিসেবে, যাতে capability এই ক্ষেত্রের গতিতে এগোতে পারে আর Pydantic AI নিজে হালকা থাকে।

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install pydantic-ai-harness
```

///

/// tab | uv

```bash
uv add pydantic-ai-harness
```

///


এটি এর সাথে [`pydantic-ai-slim`](../install.md) ইনস্টল করে, তাই এটি একাই কাজ করে; Pydantic AI আলাদাভাবে ইনস্টল করার দরকার নেই। মডেল provider আর CLI আসে extra দিয়ে, যা Pydantic AI-তে পৌঁছে দেওয়া হয়: `pydantic-ai-harness[anthropic]`, `[cli]`। কিছু capability-র ঐচ্ছিক dependency-র জন্য নিজস্ব extra লাগে; প্রতিটি capability-র পেজ এর সঠিক ইনস্টল লাইন দেয়। Python 3.11+ লাগে।

Pydantic AI-তে নিজেই নতুন? [এর ডক](../index.md) দিয়ে শুরু করুন: যে এজেন্টে আপনি এই capability বসান তা সেখানে সংজ্ঞায়িত।

## Observability { #observability }

harness যা করে তার সবকিছু পর্যবেক্ষণযোগ্য: core-এর [Instrumentation](../capabilities/instrumentation.md) capability (বা `logfire.instrument_pydantic_ai()`) প্রতিটি রানের একটি পূর্ণ trace তৈরি করে: প্রতিটি মডেল কল আর টুল কল, token আর খরচ ট্র্যাকিংসহ। এটি মানক OpenTelemetry, তাই যেকোনো OTLP backend কাজ করে; ডেভেলপমেন্টের সময় দেখার সবচেয়ে সহজ উপায় [Logfire](https://pydantic.dev/logfire)।

## নিজেরটি তৈরি { #build-your-own }

[Capabilities](../capabilities/custom.md) Pydantic AI-এর প্রধান সম্প্রসারণ-বিন্দু, আর এই লাইব্রেরির প্রতিটি capability একটি কাজ করা উদাহরণও। একটি আলাদা প্যাকেজ প্রকাশ করছেন? `pydantic-ai-<name>` নামকরণ রীতি ব্যবহার করুন; দেখুন [Publishing capability packages](../extensibility.md#publishing-capability-packages)।

## Version policy { #version-policy }

Pydantic AI Harness **0.x versioning** ব্যবহার করে, আর এটি API-র স্থিতিশীলতা নিয়ে একটি বিবৃতি, পরিপক্বতা নিয়ে নয়: এই capability-গুলো শুরু-থেকে-শেষ টেস্ট করা আর প্রোডাকশন ব্যবহারের জন্য, কিন্তু এদের API এখনও minor release-এর মধ্যে (0.1 -> 0.2) সরতে পারে: নাম-বদলানো প্যারামিটার, বদলানো ডিফল্ট, পুনর্গঠিত API, যেখানে বাস্তবসম্মত সেখানে সবসময় deprecation warning-সহ। Patch release ইচ্ছে করে বিদ্যমান আচরণ ভাঙবে না, আর প্রতিটি ভাঙা পরিবর্তন release note-এ migration নির্দেশনাসহ নথিভুক্ত, যা আপনার এজেন্ট অনুসরণ করতে পারে। Harness-কে [Pydantic AI](https://github.com/pydantic/pydantic-ai) থেকে আলাদা প্যাকেজ রাখা, যার একটি [কঠোরতর version policy](../version-policy.md) আছে, এটাই capability-কে এই ক্ষেত্রের গতিতে এগোতে দেয়।

/// tip | পরামর্শ

প্রোডাকশনে `pydantic-ai-harness`-এর version pin করুন (একটি সুনির্দিষ্ট `==` version, বা একটি minor release-এর মধ্যে সীমিত রাখা একটি শর্ত দিয়ে), যাতে একটি minor আপগ্রেড হঠাৎ কোনো প্যারামিটারের নাম বদলে আপনার এজেন্ট না ভাঙে। আপগ্রেডের সময় release note আর deprecation warning দেখুন।

///

## Pydantic AI রেফারেন্স { #pydantic-ai-references }

- [Capabilities](../capabilities/overview.md): capability কী, বিল্ট-ইন capability, নিজেরটি তৈরি
- [Hooks](../hooks.md): lifecycle hook রেফারেন্স, ক্রম, error সামলানো
- [Extensibility](../extensibility.md): প্যাকেজ প্রকাশ, থার্ড-পার্টি ইকোসিস্টেম
- [Toolsets](../toolsets.md): capability-র জন্য টুল তৈরি
- [API reference](../api/capabilities.md): পূর্ণ API ডক

/// check | সংক্ষেপে মনে রাখুন

* Harness = Pydantic AI-এর অফিসিয়াল capability লাইব্রেরি; সবকিছু `capabilities=[...]`-এ বসানো capability।
* `Coder(...)` + `LocalWorkspace('.')` = কয়েক লাইনে coding এজেন্ট; এটি FileSystem + Shell + RepoContext + SubAgents... এর জোড়া।
* `LocalWorkspace` sandbox নয় — অবিশ্বস্ত কাজে Modal/E2B/Docker sandbox ব্যবহার করুন।
* ইনস্টল: `pip install pydantic-ai-harness` (সাথে `pydantic-ai-slim` আসে); Python 3.11+।
* 0.x version — minor release-এ API বদলাতে পারে, তাই version pin করুন।

///
