# Capabilities { #capabilities }

/// note | এই পেজে যা শিখবেন

* capability কী — এজেন্টের আচরণের একটি পুনর্ব্যবহারযোগ্য, জোড়া-লাগানো যায় এমন একক।
* Pydantic AI (Core) আর Pydantic AI Harness-এ উপলব্ধ সব capability-র বিষয়ভিত্তিক তালিকা।
* `Capability` দিয়ে subclass ছাড়াই আচরণ একত্র করা, capability event, আর provider-অনুযায়ী মানিয়ে নেওয়া টুল।

///

একটি capability হলো এজেন্ট আচরণের একটি পুনর্ব্যবহারযোগ্য, জোড়া-লাগানো যায় এমন একক। আপনার `Agent` constructor-এ একাধিক আর্গুমেন্ট গেঁথে দেওয়ার বদলে — এখানে [instructions](../agent.md#instructions), ওখানে [model settings](../agent.md#model-run-settings), অন্য কোথাও একটি [toolset](../toolsets.md), আরেকটি প্যারামিটারে একটি [history processor](../message-history.md#processing-message-history) — আপনি সম্পর্কিত আচরণ একটি একক capability-তে একত্র করে [`capabilities`][pydantic_ai.agent.Agent.__init__] প্যারামিটার দিয়ে দিতে পারেন।

Capability যেকোনো সমন্বয় দিতে পারে:

* **টুল** — [toolsets](../toolsets.md) বা [native tools](../native-tools.md) দিয়ে
* **Lifecycle hook** — মডেল রিকোয়েস্ট, টুল কল আর পুরো রান ধরে আর বদলায়
* **Instructions** — স্থির বা গতিশীল [instruction](../agent.md#instructions) সংযোজন
* **Model settings** — স্থির বা প্রতি-step [model settings](../agent.md#model-run-settings)
* **মডেল** — স্থির বা মানিয়ে নেওয়া মডেল বাছাই আর অ্যাপ্লিকেশন-নির্দিষ্ট model ID মীমাংসা

এটি এদের Pydantic AI-এর প্রধান সম্প্রসারণ-বিন্দু করে তোলে। আপনি একটি memory সিস্টেম, একটি guardrail, একটি খরচ ট্র্যাকার বা একটি অনুমোদন workflow — যা-ই বানান, একটি capability সঠিক বিমূর্তন।

/// tip | উদাহরণ দিয়ে বুঝি

একটি স্মার্টফোনের "অ্যাপ"-এর মতো ভাবুন। ফোন (এজেন্ট) একই থাকে; আপনি ক্যামেরা অ্যাপ, ম্যাপ অ্যাপ, ব্যাংক অ্যাপ ইনস্টল করেন। প্রতিটি অ্যাপ নিজের সাথে নিজের বোতাম (টুল), নিয়ম (instructions) আর সেটিং নিয়ে আসে। ঠিক তেমনি `capabilities=[WebSearch(), Thinking(), Memory()]` — প্রতিটি নিজের টুল, hook আর সেটিং এজেন্টে জুড়ে দেয়, আর একই capability অন্য এজেন্টেও বসানো যায়।

///

Capability সবসময়-চালু হতে পারে বা [মডেলের চাহিদামতো লোড](on-demand.md) হতে পারে। [নিচের capability সূচি](#available-capabilities) Pydantic AI আর [Pydantic AI Harness](../harness/index.md) কভার করে। [থার্ড-পার্টি প্যাকেজ](third-party.md) আরও অনেক capability দেয়, আর আপনি নিজেরটি [ঘোষণামূলকভাবে](#bundling-behavior-with-capability) বা [subclass করে](custom.md) সংজ্ঞায়িত করতে পারেন। ব্যর্থতা, restart আর দীর্ঘ অপেক্ষা জুড়ে এজেন্ট durable-ভাবে চালাতে, দেখুন [Durable Execution](../durable_execution/overview.md)।

## উপলব্ধ capability { #available-capabilities }

Capability দুটি প্যাকেজ থেকে আসে, আর এরা একে অপরের সাথে আর আপনার সংজ্ঞায়িত capability-র সাথে মিলে যায়। Core (`pydantic-ai`) সেই capability-গুলো দেয় যার মডেল বা framework সমর্থন লাগে: provider-নেটিভ টুল, provider API আর গভীর loop ইন্টিগ্রেশন। **[Pydantic AI Harness](../harness/index.md)**, Pydantic AI-এর অফিসিয়াল capability লাইব্রেরি আর harness, বাকি সব দেয়, একক capability থেকে [সম্পূর্ণ এজেন্ট](../harness/coder.md) পর্যন্ত। **Package** কলাম বলে কোনটি; প্রতিটি entry এর ডকুমেন্টেশনে লিংক করে।

### Harness { #harnesses }

সাধারণ সমন্বিত capability হিসেবে সম্পূর্ণ এজেন্ট stack: একটি import আপনাকে একটি কাজ করা এজেন্ট দেয়, আর আপনি যেকোনোটি নিচের ব্লকগুলোতে খুলে আলাদা করতে পারেন।

| Harness | Package | যা দেয় |
|---|---|---|
| [Coder](../harness/coder.md) | Harness | একটি সম্পূর্ণ coding-agent stack: ফাইল, shell, repo context, পরিকল্পনা, একটি শুধু-পড়া explorer sub-agent আর context নিয়ন্ত্রণ |
| [Researcher](../harness/researcher.md) | Harness | একটি সম্পূর্ণ ওয়েব-গবেষণা stack: সার্চ, পেজ আনা, একটি কাজ-দেওয়া sub-researcher আর সীমিত টুল আউটপুট |

### Execution environment { #execution-environments }

এজেন্ট যে workspace-এ কাজ করে: এটি যে ফাইল সম্পাদনা করে আর যে কমান্ড চালায়, লোকাল বা বিচ্ছিন্ন।

| Capability | Package | যা করে |
|---|---|---|
| [Local Workspace](../workspace.md) | Core | আপনার টুলকে এই মেশিনে কমান্ড চালাতে আর ফাইল সম্পাদনা করতে `ctx.workspace` দেয়; নিজে কোনো টুল যোগ করে না; কোনো বিচ্ছিন্নতা নেই |
| [FileSystem](../harness/filesystem.md) | Harness | একটি root-এর নিচে ফাইল পড়া, লেখা, সম্পাদনা, খোঁজা; path-traversal আর symlink নিরাপদ, secret শুধু-পড়া |
| [Smart Search](../harness/smart-search.md) | Harness | রানের workspace-এ আচরণ দিয়ে কোড সার্চ: সাধারণ-ইংরেজি query, র‍্যাঙ্ক করা অংশ, যেকোনো মডেল দিয়ে বিচার (System One-এর ওপর একটি decision model, বা TypeSafe-এর Jev, সুপারিশকৃত) |
| [Shell](../harness/shell.md) | Harness | allowlist, denylist, timeout আর credential-ছাঁটাইসহ কমান্ড চালানো |
| [Modal Sandbox](../harness/modal-sandbox.md) | Harness | একটি বিচ্ছিন্ন [Modal](https://modal.com) cloud sandbox-এ কমান্ড আর ফাইল |
| [E2B Sandbox](../harness/e2b-sandbox.md) | Harness | একটি বিচ্ছিন্ন [E2B](https://e2b.dev) cloud sandbox-এ কমান্ড আর ফাইল |
| [Sprites Sandbox](../harness/sprites-sandbox.md) | Harness | একটি স্থায়ী [Fly.io Sprite](https://sprites.dev)-এ কমান্ড আর ফাইল |
| [Daytona Sandbox](../harness/daytona-sandbox.md) | Harness | একটি বিচ্ছিন্ন [Daytona](https://www.daytona.io) cloud sandbox-এ কমান্ড আর ফাইল |
| [Smol Sandbox](../harness/smol-sandbox.md) | Harness | আপনার নিজের মেশিনে একটি [smolvm](https://github.com/smol-machines/smolvm) microVM-এ কমান্ড আর ফাইল; কোনো cloud অ্যাকাউন্ট নয় |
| [BoxLite Sandbox](../harness/boxlite-sandbox.md) | Harness | আপনার নিজের মেশিনে একটি [BoxLite](https://github.com/boxlite-ai/boxlite) micro-VM-এ কমান্ড আর ফাইল, ঐচ্ছিক egress allow-list-সহ; কোনো cloud অ্যাকাউন্ট নয় |
| [Docker Sandbox](../harness/docker-sandbox.md) | Harness | একটি লোকাল [Docker](https://www.docker.com/) বা Podman container-এ কমান্ড আর ফাইল |
| [SSH Workspace](../harness/ssh-workspace.md) | Harness | আপনার `ssh` client দিয়ে একটি দূরের host-এ কমান্ড আর ফাইল; কোনো বিচ্ছিন্নতা নেই |
| [Bubblewrap Sandbox](../harness/bubblewrap-sandbox.md) | Harness | আরেকটি workspace capability মোড়ায়, যাতে এর কমান্ড ওই workspace-এর host-এ একটি Linux [bubblewrap](https://github.com/containers/bubblewrap) sandbox-এ চলে |

### টুল আর নেটিভ ক্ষমতা { #tools-native-abilities }

যে ক্ষমতা provider নেটিভভাবে চালায়, আর যেকোনো MCP সার্ভারের সাথে সংযোগ।

| Capability | Package | যা করে |
|---|---|---|
| [MCP](mcp.md) | Core | যেকোনো MCP সার্ভারের টুল যুক্ত করে; ডিফল্টভাবে লোকাল, provider-নেটিভ connector ঐচ্ছিক |
| [Image Generation](image-generation.md) | Core | ছবি তৈরি আর সম্পাদনা; যেখানে সমর্থিত সেখানে provider-নেটিভ, অন্যত্র সরাসরি image-model বিকল্প |
| [File Understanding](file-understanding.md) | Core | মডেল পড়তে পারে না এমন ছবি, ডকুমেন্ট, অডিও আর ভিডিও বর্ণনা করে, পারে এমন একটি মডেল দিয়ে |
| [Native Tool](../native-tools.md) | Core | এজেন্টে যেকোনো provider-নেটিভ টুল নিবন্ধন করে |

### Integration { #integrations }

থার্ড-পার্টি সার্ভিসের টুল, বেশিরভাগ সার্ভিসের নিজস্ব হোস্ট করা MCP সার্ভার দিয়ে। [Integrations](../harness/integrations.md) পেজ এদের কীসের সাথে যুক্ত হয় তা অনুযায়ী ভাগ করে।

| Capability | Package | যা করে |
|---|---|---|
| [GitHub](../harness/github.md) | Harness | GitHub-এর হোস্ট করা MCP সার্ভার দিয়ে repository, issue আর pull request পড়া ও বদলানো |
| [Linear](../harness/linear.md) | Harness | Linear-এর হোস্ট করা MCP সার্ভার দিয়ে issue, project আর comment পড়া ও হালনাগাদ |
| [Macroscope](../harness/macroscope.md) | Harness | একটি লোকাল [Macroscope](https://docs.macroscope.com/cli) কোড রিভিউ চালিয়ে ফলাফল এজেন্টকে দেয় |
| [LocalStack](../harness/localstack.md) | Harness | AWS CLI টুলসহ একটি অনুকৃত AWS environment |
| [Google Workspace](../harness/google-workspace.md) | Harness | Google-এর হোস্ট করা MCP সার্ভার দিয়ে Gmail, Calendar, Drive, Docs, Sheets, Slides, Chat আর People ব্যবহার |
| [Notion](../harness/notion.md) | Harness | Notion-এর হোস্ট করা MCP সার্ভার দিয়ে একটি Notion workspace-এ পেজ খোঁজা আর সম্পাদনা |
| [Slack](../harness/slack.md) | Harness | Slack-এর হোস্ট করা MCP সার্ভার দিয়ে বার্তা পড়া ও পাঠানো, চ্যানেল দেখা আর canvas সম্পাদনা |
| [Day AI](../harness/day-ai.md) | Harness | [Day AI](https://day.ai)-এর হোস্ট করা MCP সার্ভার দিয়ে CRM রেকর্ড খোঁজা ও হালনাগাদ আর মিটিংয়ের প্রসঙ্গ পড়া |
| [Grain](../harness/grain.md) | Harness | [Grain](https://grain.com)-এর হোস্ট করা MCP সার্ভার দিয়ে মিটিং, transcript আর নোট খোঁজা ও পড়া, আর clip তৈরি ও মিটিং ট্যাগ করা |
| [Pylon](../harness/pylon.md) | Harness | [Pylon](https://www.usepylon.com)-এর হোস্ট করা MCP সার্ভার দিয়ে support issue, account আর contact নিয়ে কাজ |
| [StackOne](../harness/stackone.md) | Harness | [StackOne](https://www.stackone.com) দিয়ে যুক্ত SaaS অ্যাকাউন্টে (HRIS, ATS, CRM, …) কাজ |
| [PostHog](../harness/posthog.md) | Harness | PostHog-এর হোস্ট করা MCP সার্ভার দিয়ে product analytics query আর feature flag, experiment ও dashboard পরিচালনা |
| [Logfire MCP](../harness/logfire-mcp.md) | Harness | হোস্ট করা [Logfire](https://pydantic.dev/logfire) MCP সার্ভার দিয়ে trace আর telemetry query আর project পরিচালনা |
| [Ordinal](../harness/ordinal.md) | Harness | [Ordinal](https://www.tryordinal.com)-এর হোস্ট করা MCP সার্ভার দিয়ে সোশ্যাল পোস্টের খসড়া, নির্ধারণ আর বিশ্লেষণ |

### ওয়েব আর গবেষণা { #web-research }

খোলা ওয়েবে জিনিস খোঁজা আর পড়া।

| Capability | Package | যা করে |
|---|---|---|
| [Web Search](web-search.md) | Core | যেখানে পাওয়া যায় সেখানে provider-নেটিভ সার্চ, সব জায়গায় লোকাল DuckDuckGo বিকল্প |
| [Web Fetch](web-fetch.md) | Core | URL আনা আর পড়া, নেটিভ বা লোকাল |
| [X Search](x-search.md) | Core | X-এ সার্চ; xAI-তে নেটিভ, অন্যত্র subagent বিকল্প |
| [Citations](../citations.md) | Core | উত্তরের পেছনের ডকুমেন্ট আর পেজ উদ্ধৃত করতে provider-কে বলে |
| [Exa Search](../harness/exa-search.md) | Harness | [Exa](https://exa.ai) দিয়ে ওয়েব গবেষণা: অংশ-উদ্ধৃত সার্চ, পূর্ণ-পেজ পড়া, ঐচ্ছিক উদ্ধৃতিসহ গভীর সার্চ |
| [Exa Agent](../harness/exa-search.md) | Harness | খোলামেলা গবেষণা Exa Agent API-কে দেয় |
| [You.com Search](../harness/youdotcom.md) | Harness | [You.com](https://you.com) দিয়ে ওয়েব সার্চ আর পেজ পড়া: query-প্রাসঙ্গিক অংশ বা পূর্ণ-পেজ markdown |
| [You.com Research](../harness/youdotcom.md) | Harness | You.com Answer, Research আর Finance Research API দিয়ে উদ্ধৃতিসহ উত্তর আর বহু-ধাপের গবেষণা |
| [Browser Use](../harness/browser-use.md) | Harness | একটি আসল browser চালানো একটি স্বয়ংক্রিয় [browser-use](https://github.com/browser-use/browser-use) এজেন্টকে ওয়েব কাজ দেয় |
| [Playwright Browser](../harness/playwright.md) | Harness | নিজে একটি আসল Chromium পেজ চালান: navigate, click, type, পড়া আর পেজ কী করেছে তা পরীক্ষা |

### যুক্তি, পরিকল্পনা আর কাজ ভাগ { #reasoning-planning-delegation }

এজেন্ট কীভাবে ভাবে আর কাজ ভাগ করে।

| Capability | Package | যা করে |
|---|---|---|
| [Thinking](thinking.md) | Core | কনফিগার-যোগ্য মাত্রায় provider-অনুযায়ী বর্ধিত thinking |
| [Planning](../harness/planning.md) | Harness | একটি cache-নিরাপদ লাইভ রিমাইন্ডারসহ মডেল-নিয়ন্ত্রিত task পরিকল্পনা |
| [Subagents](../harness/subagents.md) | Harness | স্বয়ংসম্পূর্ণ কাজ নাম দেওয়া child এজেন্টকে দেয় |
| [Dynamic Workflow](../harness/dynamic-workflow.md) | Harness | মডেল একটি Python script থেকে sub-agent চালায়: একটি টুল কলে fan-out, chain, vote, কঠোর `max_agent_calls` বাজেটসহ |
| [Advisor](../harness/advisor.md) | Harness | একটি executor-কে রানের মাঝে একটি শক্তিশালী মডেলের পরামর্শ নিতে দেয় |
| [Background Tools](../harness/background-tools.md) | Harness | বাছা টুল একসাথে চালায়; ফল পরের বার্তা হিসেবে আসে |

### Context ব্যবস্থাপনা { #context-management }

এজেন্ট কীভাবে এর context window খরচ করে: এটিই পার্থক্য গড়ে একটি এজেন্টের মধ্যে যে দীর্ঘ রানে খারাপ হয়ে যায় আর যে হয় না, আর token-এর জন্য N বার বনাম একবার টাকা দেওয়ার মধ্যে।

| Capability | Package | যা করে |
|---|---|---|
| [Code Mode](../harness/code-mode.md) | Harness | মডেল একটি Python script লেখে যা একটি [Monty](https://github.com/pydantic/monty) sandbox-এর ভেতরে অনেক টুল ডাকে: N-এর বদলে একটি round-trip, আর মাঝের ফল কখনো context window-এ ঢোকে না |
| [Tool Search](tool-search.md) | Core | প্রতিটি prompt-এ শত শত বহন না করে চাহিদামতো টুল সংজ্ঞা লোড |
| [Caching](caching.md) | Core | কনফিগার-যোগ্য retention-এ টুল, instructions আর কথোপকথনের provider-অনুযায়ী prompt caching |
| [Compaction](compaction.md) | Core | OpenAI আর Anthropic-এ provider-নেটিভ compaction; provider সার্ভার-পক্ষে ইতিহাসের সারাংশ করে |
| [Compaction](../harness/compaction.md) | Harness | মডেল-নিরপেক্ষ কৌশল: টুল-ফল মোছা, sliding-window ছাঁটাই, LLM সারাংশ, স্তরভিত্তিক; সবই window-আপেক্ষিক, লাইভ usage রিপোর্টসহ |
| [Tool Output Limits](../harness/tool-output-limits.md) | Harness | বড় আকারের টুল ফেরত উৎসেই ছাঁটাই, একটি query-যোগ্য ফাইলে ঢালা, বা সারাংশ |
| [Warn On Cache Busts](../harness/warn-on-cache-busts.md) | Harness | provider-এর নিজের সংখ্যা থেকে রিকোয়েস্টের মাঝে prompt-cache prefix ভাঙন ধরে |

### জ্ঞান আর memory { #knowledge-memory }

এজেন্ট যা জানে আর মনে রাখে, প্রতিটি prompt-এ বহন না করে প্রাসঙ্গিক হলে লোড। [Persistence](../persistence.md) আলোচনা করে এগুলো কথোপকথনের ইতিহাসের পাশে কীভাবে বসে, যা নিজেই চলমান রান সম্পর্কে একটি এজেন্টের memory।

| Capability | Package | যা করে |
|---|---|---|
| [Memory](../harness/memory.md) | Harness | একটি স্থায়ী, namespace-ভিত্তিক নোটবুক: সীমিত prompt injection, চাহিদামতো সার্চ; in-memory/file/Postgres store |
| [Conversation Search](../harness/conversation-search.md) | Harness | সংরক্ষিত ইতিহাসে BM25 সার্চ, compaction-এ বাদ পড়া turn-সহ |
| [Skills](../harness/skills.md) | Harness | চাহিদামতো [Agent Skill](on-demand.md) (`SKILL.md`) instructions লোড |
| [Repo Context](../harness/repo-context.md) | Harness | রান দিকনির্দেশিত অবস্থায় শুরু: `AGENTS.md`/`CLAUDE.md` + repository কাঠামো |
| [Pydantic AI Docs](../harness/pydantic-ai-docs.md) | Harness | চাহিদামতো Pydantic AI ডকুমেন্টেশন খোঁজা |

### নিয়ন্ত্রণ আর নিরাপত্তা { #control-safety }

এজেন্ট কী করতে পারে তা সীমিত রাখা, আর একে instructions-এ রাখা।

| Capability | Package | যা করে |
|---|---|---|
| [Guardrails](../harness/guardrails.md) | Harness | ব্যবহারকারীর input, টুল কল, টুলের ফল আর আউটপুট যাচাই/আটকানো/মুছে দেওয়া, secret মাস্কিং আর সমান্তরাল async guard-সহ |
| [Prompt Injection Defender](../harness/prompt-injection-defender.md) | Harness | লোকাল টুল ফল পরোক্ষ prompt injection-এর জন্য শ্রেণিবদ্ধ করে আর ঐচ্ছিকভাবে উচ্চ-ঝুঁকির ফল আটকে রাখে |
| [Spend Limits](../harness/spend.md) | Harness | window-জুড়ে USD/token বাজেট আর প্রতি-response খরচ ট্র্যাকিং, প্রতি মডেল আর প্রতি tenant |
| [Ask User](../harness/ask-user.md) | Harness | মডেলকে রানের মাঝে ব্যবহারকারীকে বহু-নির্বাচনী প্রশ্ন করতে দেয়; উত্তরদাতা আপনি দেন (terminal, web, test) |
| [Tool approval](../deferred-tools.md#human-in-the-loop-tool-approval) | Core | চলার আগে মানুষের অনুমোদন লাগে এমন টুল কল চিহ্নিত করে |
| [Handle Deferred Tool Calls](handle-deferred-tool-calls.md) | Core | অনুমোদন-স্থগিত টুল কল প্রোগ্রাম দিয়ে মীমাংসা |
| [System Reminders](../harness/system-reminders.md) | Harness | instruction ফিকে হওয়া ঠেকাতে রানের মাঝে নির্দেশনার cache-নিরাপদ পুনঃসংযোজন |
| [Trajectory Judge](../harness/trajectory-judge.md) | Harness | একটি দ্বিতীয় মডেল প্রতি N রিকোয়েস্টে একটি sliding token window-এ লাইভ রান পর্যালোচনা করে আর মাঝপথে পথ দেখায় |

### নিজেকে সম্প্রসারণ { #self-extension }

| Capability | Package | যা করে |
|---|---|---|
| [Capability Creation](../harness/capability-creation.md) | Harness | এজেন্ট একটি রানের সময় *নতুন capability* লেখে, যাচাই করে আর সংরক্ষণ করে; host `store.load_active()` আর `capabilities=` দিয়ে পরের একটি রানে এগুলো লোড করে |

### Execution runtime { #execution-runtime }

loop-এর বাইরে: রান কীভাবে টিকে থাকে, ব্যর্থতা থেকে বাঁচে, আর প্রোডাকশনে পর্যবেক্ষিত ও কনফিগার হয়।

| Capability | Package | যা করে |
|---|---|---|
| [Durable execution](../durable_execution/overview.md) | Core | [Temporal](../durable_execution/temporal.md), [DBOS](../durable_execution/dbos.md) বা [Prefect](../durable_execution/prefect.md)-এ restart আর ব্যর্থতা থেকে টিকে থাকা রান, [Restate](../durable_execution/restate.md) আর [Airflow](../durable_execution/airflow.md) ইন্টিগ্রেশনসহ |
| [AWS Lambda durability](../harness/aws-lambda.md) | Harness | মডেল রিকোয়েস্ট আর টুল কল AWS Lambda durable function step-এ checkpoint |
| [Absurd durability](../harness/absurd.md) | Harness | মডেল রিকোয়েস্ট, MCP কল আর টুল কল PostgreSQL-এ Absurd step-এ checkpoint |
| [pgtask durability](../harness/pgtask.md) | Harness | মডেল রিকোয়েস্ট, MCP কল আর টুল কল PostgreSQL-এ pgtask step-এ checkpoint |
| [Render Workflows](../harness/render-workflows.md) | Harness | মডেল রিকোয়েস্ট আর টুল কল আলাদা retry, timeout আর compute সেটিংসহ শৃঙ্খলিত task run হিসেবে চালায়; এজেন্ট চালানো task retry করলে সম্পন্ন কাজ পুনরাবৃত্তি হতে পারে |
| [Step Persistence](../harness/step-persistence.md) | Harness | রান সংরক্ষণ, পুনরুদ্ধার, আবার চালানো (`continue_run`) আর fork (`fork_run`); file/SQLite/Mongo backend |
| [Instrumentation](instrumentation.md) | Core | প্রতিটি মডেল আর টুল কলের জন্য OpenTelemetry GenAI span; [Logfire](https://pydantic.dev/logfire) trace-এর কাঁচামাল |
| [Managed Prompt](../harness/managed-prompt.md) | Harness | instructions-কে একটি [Logfire](https://pydantic.dev/logfire)-পরিচালিত prompt দিয়ে চালায়; redeploy ছাড়াই version আর চালু |
| [Repair Tool Arguments](../harness/repair-tool-arguments.md) | Harness | schema যাচাইয়ের আগে ত্রুটিপূর্ণ JSON টুল আর্গুমেন্ট মেরামত |
| [Thread Executor](thread-executor.md) | Core | sync টুল একটি ভাগ করা thread pool-এ চালায় |

### Loop কাস্টমাইজেশন { #loop-customization }

Core এজেন্ট loop নিজে কাস্টমাইজ করার capability-ও দেয়, বেশিরভাগ প্রোডাকশন সার্ভারের জন্য:

| Capability | Package | যা করে |
|---|---|---|
| [Hooks](../hooks.md) | Core | decorator-ভিত্তিক lifecycle hook নিবন্ধন |
| [Select Model](select-model.md) | Core | একটি callable দিয়ে স্থির বা প্রতি-step মডেল বাছাই |
| [Resolve Model ID](resolve-model-id.md) | Core | একটি callable দিয়ে নিজস্ব, অ্যাপ্লিকেশন-নির্দিষ্ট model ID মীমাংসা |
| [Prepare Tools / Prepare Output Tools](prepare-tools.md) | Core | প্রতি step-এ function আর [output tool][pydantic_ai.output.ToolOutput] সংজ্ঞা ছাঁকা বা বদলানো |
| [Prefix Tools](prefix-tools.md) | Core | একটি capability মুড়ে এর টুলের নামে prefix যোগ |
| [Include Tool Return Schemas](include-tool-return-schemas.md) | Core | মডেলে পাঠানো টুল সংজ্ঞায় return type schema অন্তর্ভুক্ত |
| [Set Tool Metadata](set-tool-metadata.md) | Core | বাছা টুলে metadata key-value জোড়া মেলানো |
| [Raise Content Filter Error](raise-content-filter-error.md) | Core | একটি মডেল response-এ `finish_reason='content_filter'` থাকলেই [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] তোলে |
| [Reinject System Prompt](reinject-system-prompt.md) | Core | আগত message history-তে কনফিগার করা system prompt না থাকলে আবার বসায় |
| [Process History](process-history.md) | Core | একটি [history processor](../message-history.md#processing-message-history) মোড়ায় |
| [Process Event Stream](process-event-stream.md) | Core | [agent stream event](process-event-stream.md) একটি handler ফাংশনে পাঠায় |

লেখার মৌলিক উপাদান — [subclass ছাড়াই আচরণ একত্র করতে](#bundling-behavior-with-capability) [`Capability`][pydantic_ai.capabilities.Capability] আর একটি [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] মোড়াতে [`Toolset`][pydantic_ai.capabilities.Toolset] — নিচে আলোচিত। [ACP](../harness/acp.md) *(পরীক্ষামূলক, Harness)* [Agent Client Protocol](https://agentclientprotocol.com) দিয়ে Zed-এর মতো editor-এ যেকোনো এজেন্ট পরিবেশন করে। যে capability [YAML/JSON agent spec](../agent-spec.md#capability-spec-syntax)-এ ঘোষণা করা যায় সেগুলো সেখানে তালিকাভুক্ত।

```python title="native_capabilities.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import Thinking, WebSearch

agent = Agent(
    'anthropic:claude-fable-5-1',
    instructions='You are a research assistant. Be thorough and cite sources.',
    capabilities=[
        Thinking(effort='high'),
        WebSearch(local='duckduckgo'),
    ],
)
```

[Instructions](../agent.md#instructions) আর [model settings](../agent.md#model-run-settings) সরাসরি `Agent` (বা [`AgentSpec`][pydantic_ai.agent.AgentSpec])-এর `instructions` আর `model_settings` প্যারামিটার দিয়ে কনফিগার হয়। Capability হলো সাধারণ কনফিগারেশনের বাইরের আচরণের জন্য — টুল, lifecycle hook আর নিজস্ব সম্প্রসারণ। এরা ভালোভাবে মিলে যায়, বিশেষত যখন আপনি একাধিক এজেন্ট জুড়ে একই কনফিগারেশন পুনর্ব্যবহার করতে বা একটি [spec ফাইল](../agent-spec.md) থেকে লোড করতে চান।

## `Capability` দিয়ে আচরণ একত্র করা { #bundling-behavior-with-capability }

নিজের একটি capability সংজ্ঞায়িত করতে আপনার একটি subclass লাগে না: [`Capability`][pydantic_ai.capabilities.Capability] instructions, ফাংশন টুল আর [toolsets](../toolsets.md) ঘোষণামূলকভাবে একত্র করে — একে একটি skill সংজ্ঞায়িত করা হিসেবে ভাবুন:

```python title="capability_shorthand.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import Capability

refunds = Capability(
    id='refunds',
    description='Use for refund eligibility and refund status.',
    instructions='Always confirm the order ID before issuing a refund.',
)


@refunds.tool_plain
def refund_status(order_id: str) -> str:
    """Look up the refund status for an order."""
    return f'Order {order_id}: refund issued on 2026-05-01.'


agent = Agent('openai:gpt-6.1-sol', capabilities=[refunds])
```

`defer_loading=True` যোগ করুন, আর বান্ডেলটি একটি [on-demand capability](on-demand.md) হয়ে যায়, যা মডেল লোড না করা পর্যন্ত একটি এক-লাইনের ক্যাটালগ entry-তে গুটিয়ে থাকে — [Agent Skills](on-demand.md#loading-skills-from-markdown-files)-এর মতো, যা আপনি সরাসরি একটি `Capability`-তে মোড়াতে পারেন। পূর্ণ API-র জন্য দেখুন [The `Capability` convenience class](on-demand.md#the-capability-convenience-class)। instructions, টুল আর toolset-এর বাইরের আচরণের জন্য — lifecycle hook, model settings, নেটিভ টুল — [Building Custom Capabilities](custom.md)-এ আলোচিত মতো [`AbstractCapability`][pydantic_ai.capabilities.AbstractCapability] subclass করুন।

/// info | এক নজরে: কোন পথ?

| আপনার যা দরকার | পথ |
|---------------|-----|
| instructions + টুল + toolset একসাথে বাঁধা | `Capability(instructions=..., tools=[...])` |
| ওপরেরটা, কিন্তু মডেল চাইলে তবেই লোড | `Capability(..., defer_loading=True)` |
| lifecycle hook, model settings, নেটিভ টুল | `AbstractCapability` subclass |

///

## Capability event { #capability-events }

পুনর্ব্যবহারযোগ্য capability সমন্বয় আর পর্যবেক্ষণের জন্য টাইপ করা [`CapabilityEvent`][pydantic_ai.messages.CapabilityEvent] প্রকাশ করতে পারে। একটি event পরিবারকে একটি স্থিতিশীল namespace দিন, প্রতিটি payload একটি dataclass হিসেবে সংজ্ঞায়িত করুন, আর একটি async capability hook বা capability-র দেওয়া টুল থেকে [`ctx.emit()`][pydantic_ai.tools.RunContext.emit] await করে এটি তৈরি করুন:

```python title="capability_events.py"
from dataclasses import dataclass
from typing import Any

from pydantic_ai import CapabilityEvent, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.toolsets import AgentToolset, FunctionToolset

WORKSPACE = 'workspace'


@dataclass(kw_only=True)
class FileWriteEvent(CapabilityEvent, namespace=WORKSPACE):
    path: str
    bytes_written: int


workspace = FunctionToolset()


@workspace.tool
async def write_file(ctx: RunContext[Any], path: str, content: str) -> str:
    await ctx.emit(FileWriteEvent(path=path, bytes_written=len(content)))
    return f'Wrote {path}'


@dataclass
class Workspace(AbstractCapability[Any]):
    def get_toolset(self) -> AgentToolset[Any] | None:
        return workspace
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

namespace একটি module-স্তরের constant-এ রাখুন আর একে capability-র নাম বা [`id`][pydantic_ai.capabilities.AbstractCapability.id] দিন: পরিবারের প্রতিটি event এটি পুনরাবৃত্তি করে, আর এটিই সেই prefix যা subscriber-রা মেলায়।

একটি capability নির্দিষ্টভাবে capability event প্রকাশ করে, আর একটি থেকে একটি অ্যাপ্লিকেশন [`CustomEvent`][pydantic_ai.messages.CustomEvent] তৈরি করলে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে; ভাগটি দেখুন [Which event type do I use?](../agent.md#which-event-type)-এ। payload সেই ফিল্ডের নাম ব্যবহার করতে পারে না যা খামের নিজের দরকার: `data`, `capability_id`, `tool_call_id`, `tool_name` আর `event_kind` ক্লাস সংজ্ঞায়িত হওয়ার সময় প্রত্যাখ্যাত হয়।

Pydantic AI তৈরিকারী capability-র run id `capability_id` হিসেবে ছাপ দেয়। আপনি `id` দিয়েছেন এমন একটি capability-র জন্য, সেটিই `id`। দেননি এমন একটির জন্য, এটি framework-এর সেই রানের জন্য তৈরি একটি handle — `'<file_reader:4f3a9c>'` — যা প্রতি রানে আলাদা আর মেলানো উচিত নয়; একজন subscriber-এর এটি চিনতে হলে capability-কে একটি স্পষ্ট `id` দিন। এর টুলের তৈরি event `tool_call_id` আর `tool_name`-ও পায়। এগুলো [agent run event stream](../agent.md#streaming-all-events)-এ দেখা দেয় কিন্তু অভ্যন্তরীণ সমন্বয়ের সংকেত, তাই UI adapter ডিফল্টভাবে এগুলো পাঠায় না। একটি protocol adapter একটিকে নিজের protocol-এ ম্যাপ করতে [`handle_capability_event()`][pydantic_ai.ui.UIEventStream.handle_capability_event] override করতে পারে, payload নিজে তৈরি করে, কারণ `CapabilityEvent`-এর কোনো `to_payload()` নেই। যে অ্যাপ্লিকেশন একটি frontend-এ একটি প্রকাশ করতে চায়, সে এর বদলে [`@agent.on_event`][pydantic_ai.agent.Agent.on_event] দিয়ে এটি শুনে পাবলিক payload বহন করা একটি অ্যাপ্লিকেশন `CustomEvent` তৈরি করতে পারে:

```python title="republish_capability_event.py"
from dataclasses import dataclass

from pydantic_ai import Agent, CapabilityEvent, CustomEvent, RunContext

SEARCH_INDEX = 'search_index'


@dataclass(kw_only=True)
class IndexRebuiltEvent(CapabilityEvent, namespace=SEARCH_INDEX):
    documents: int


@dataclass(kw_only=True)
class SearchReadyEvent(CustomEvent):
    documents: int


agent = Agent('test')


@agent.on_event(IndexRebuiltEvent)
async def republish(ctx: RunContext, event: IndexRebuiltEvent) -> None:
    await ctx.emit(SearchReadyEvent(documents=event.documents))
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

listener একটি capability-র নয়, অ্যাপ্লিকেশনের, তাই এটি সেই জায়গাগুলোর একটি যেখানে অ্যাপ্লিকেশন `CustomEvent` তৈরি করা যায়। [`Hooks.on.event`][pydantic_ai.capabilities.Hooks] একই কাজ করে যখন আপনি এমনিতেই একটি `Hooks` capability চান — অন্য [hook পরিবারের](../hooks.md) জন্য, বা অন্য capability-র মধ্যে এটি কোথায় বসবে তা বাছতে।

namespace আর event নাম মিলে serialize করা `kind` গঠন করে (যেমন `workspace.file_read`), আর আপনি একটি স্পষ্ট `name=` না দিলে event নাম ক্লাসের নাম থেকে তৈরি হয়। একটি namespace বাধ্যতামূলক: একটি ছাড়া একটি `CapabilityEvent` subclass সংজ্ঞায়িত করলে সেখানেই `TypeError` ওঠে, একটি namespace-হীন event-কে stream-এ পৌঁছাতে না দিয়ে। তবে আপনি এটি প্রতি পরিবারে একবারই দেন — আরেকটি capability event subclass করা একটি event এর namespace উত্তরাধিকারসূত্রে পায় আর শুধু নিজের নাম যোগ করে, তাই একটি ভাগ করা base একটি পরিবার সংজ্ঞায়িত করার সবচেয়ে পরিপাটি উপায় — আর একটি subclass উত্তরাধিকারসূত্রে পাওয়াটি থেকে সরে যেতে নিজের `namespace=` দিতে পারে। যে base শুধু namespace আর পরিবারের সাধারণ ফিল্ড বহন করে তাকে `abstract=True` চিহ্নিত করুন, আর এটি registry-র বাইরে থাকে আর নিজে তৈরি করা যায় না, যখন এর subclass-গুলো স্বাভাবিকভাবে নিবন্ধিত হয়। অন্য যেকোনো event-এর মতো এটিকে `@dataclass` দিয়ে decorate করুন: একটি decorate-না-করা base কোনো ফিল্ডই দেয় না, যা ফিল্ডগুলো নিঃশব্দে হারানো একটি payload হিসেবে প্রকাশ পেতে না দিয়ে প্রত্যাখ্যাত হয়। `kind` হলো event-এর wire identifier, তাই ক্লাসের নাম বদলালে এর সাথে tag-ও বদলে যায়, যেখানেই event তৈরিকারী process-এর চেয়ে বেশি টেকে সেখানে সামঞ্জস্য ভেঙে — [durable execution](../durable_execution/overview.md)-এর ইতিহাস আর cache, সংরক্ষিত event log, kind মেলানো subscriber। একটি লাইব্রেরি হিসেবে প্রকাশিত একটি capability-র উচিত এর প্রতিটি event-এ `name=` pin করা। ক্লাস সংজ্ঞায়িত হওয়ার সময় kind নিবন্ধিত হয় আর process-এর মধ্যে অনন্য হতে হবে; একই ক্লাস সংজ্ঞা আবার চালালে (যেমন একটি notebook cell আবার চালালে) নিবন্ধন বদলে যায়। একটি event deserialize করা adapter তৈরির আগে event সংজ্ঞায়িত module import করুন, কারণ প্রতিটি pydantic `TypeAdapter` তৈরির সময় নিবন্ধিত kind-গুলো ধরে রাখে। অন্যথায় event-টি একটি [`UnknownCapabilityEvent`][pydantic_ai.messages.UnknownCapabilityEvent] হয়ে যায় আর একটি `UserWarning` আসে, payload ফিল্ড না হারিয়ে; এটি আবার serialize করলে wire রূপ রক্ষিত থাকে, যাতে পরের একজন consumer টাইপ করা event উদ্ধার করতে পারে।

### Event-এ সাড়া দেওয়া { #reacting-to-events }

বাছা event ক্লাসে সাড়া দিতে একটি async capability মেথডে [`@on_event`][pydantic_ai.capabilities.on_event] ব্যবহার করুন। যেমন, একটি file-system capability একটি repository নির্দেশনা ফাইল পড়ার খবর দেওয়ার সাথে সাথে একটি repository-context capability instructions enqueue করতে পারে:

```python title="react_to_capability_events.py"
from dataclasses import dataclass
from typing import Any

from pydantic_ai import CapabilityEvent, RunContext
from pydantic_ai.capabilities import AbstractCapability, on_event

REPO_CONTEXT = 'repo_context'


@dataclass(kw_only=True)
class FileReadEvent(CapabilityEvent, namespace=REPO_CONTEXT):
    path: str


@dataclass(kw_only=True)
class DirectoryListedEvent(CapabilityEvent, namespace=REPO_CONTEXT):
    path: str


class RepoContext(AbstractCapability[Any]):
    @on_event(FileReadEvent, DirectoryListedEvent)
    async def _follow_discovered_instructions(
        self,
        ctx: RunContext[Any],
        event: FileReadEvent | DirectoryListedEvent,
    ) -> None:
        if event.path.endswith('AGENTS.md'):
            ctx.enqueue(f'Follow the instructions in {event.path}.')
```

/// tip | উদাহরণ দিয়ে বুঝি

একটি অফিসের নোটিশবোর্ডের মতো: একটি ফাইল-পড়া capability বোর্ডে লেখে "আমি `AGENTS.md` পড়েছি"। `RepoContext` capability ওই ধরনের নোটিশের জন্য `@on_event(FileReadEvent)` দিয়ে কান পেতে আছে, দেখামাত্র এজেন্টকে প্রাসঙ্গিক নির্দেশনা দিয়ে দেয়। দুটি capability একে অপরকে সরাসরি চেনে না — শুধু event-এর মাধ্যমে কথা বলে।

///

ছাঁকা স্পষ্ট: decorator এতে দেওয়া ক্লাসের বিপরীতে `isinstance` ব্যবহার করে। একটি খালি `@on_event` পুরো [`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent] union পায়, মডেল response delta, টুল কল আর ফলের event, deferred আর [enqueued-message](../message-history.md#injecting-messages-mid-run) event, [custom event](../agent.md#custom-events) আর capability event-সহ।

পারলে ক্লাসগুলোর নাম দিন। type checker-এর জন্য `event` আর্গুমেন্ট সরু করা ছাড়াও, ক্লাসগুলোই dispatch-কে একটি capability-র ভেতরে না নেমে এটি এড়িয়ে যেতে দেয়: একটি capability শুধু সেই event-এর জন্য জাগে যা এর একটি listener গ্রহণ করে। একটি খালি `@on_event` — বা একটি override করা [`on_event()`][pydantic_ai.capabilities.AbstractCapability.on_event], যার dispatch আগে থেকে জানা যায় না — সেই capability-কে প্রতিটি event-এ যুক্ত করে, আর অন্যদের জোড়া একটি capability এর সন্তানদের union জানায়। আপনি `on_event()` override করলে আর এটি কী dispatch করে তা বর্ণনা করতে পারলে, তা বলতে এর পাশে [`listens_to()`][pydantic_ai.capabilities.AbstractCapability.listens_to] override করুন।

Listener capability-র ক্রমে একটার পর একটা চলে, আর একটি capability-র ভেতরে চিহ্নিত মেথড সংজ্ঞার ক্রমে চলে। তৈরিকারী capability নিজের event-ও পায়। ডিফল্টভাবে, listener চলে যখন event stream-এ এর অবস্থানে পৌঁছায়, তাই listener-এর ক্রম সবসময় stream-এর ক্রমের সাথে মেলে আর listener-এর কাজ তৈরিকারীর দেরিতে যোগ হয় না। টুল চালানোর সময় তৈরি event-এর জন্য, listener পরের মডেল রিকোয়েস্টের আগে চলে। `before_model_request`-এর সময় তৈরি একটি event হয়তো ওই রিকোয়েস্ট শুরু হওয়ার পরেই listener-দের কাছে পৌঁছায়, [`ctx.enqueue()`][pydantic_ai.tools.RunContext.enqueue]-এর মতো একই যত-তাড়াতাড়ি-সম্ভব সময়ে।

যে সিদ্ধান্ত-event-এর তৈরিকারী এগোনোর আগে listener-এর পরিবর্তন দরকার, সেগুলো event ক্লাসে `dispatch='immediate'` ঘোষণা করে:

ওপরের workspace capability-র ওপর ভিত্তি করে, একটি লেখা ঘটার আগে নিজেকে ঘোষণা করতে পারে আর একজন listener-কে তা বাতিল (veto) করতে দিতে পারে:

```python title="cancellable_capability_event.py"
from dataclasses import dataclass
from typing import Any

from pydantic_ai import CapabilityEvent, RunContext
from pydantic_ai.capabilities import AbstractCapability, on_event
from pydantic_ai.toolsets import FunctionToolset

WORKSPACE = 'workspace'


@dataclass(kw_only=True)
class FileWriteStartEvent(
    CapabilityEvent, namespace=WORKSPACE, dispatch='immediate'
):
    path: str
    cancelled: bool = False
    cancel_reason: str | None = None

    def cancel(self, reason: str | None = None) -> None:
        self.cancelled = True
        self.cancel_reason = reason


workspace = FunctionToolset()


@workspace.tool
async def write_file(ctx: RunContext[Any], path: str, content: str) -> str:
    event = await ctx.emit(FileWriteStartEvent(path=path))  # (1)!
    if event.cancelled:  # (2)!
        return f'Refused to write {path}: {event.cancel_reason}'
    return f'Wrote {path}'


class ProtectGitDirectory(AbstractCapability[Any]):
    @on_event(FileWriteStartEvent)
    async def _veto_writes_to_git(
        self, ctx: RunContext[Any], event: FileWriteStartEvent
    ) -> None:
        if event.path.startswith('.git/'):
            event.cancel('.git/ is managed by the repository, not the agent')
```

1. প্রতিটি listener চলার পরেই কেবল `emit` ফেরত আসে, আর যে instance এটি পেয়েছিল সেটিই ফেরত দেয়।
2. তাই সিদ্ধান্তটি ঠিক পরেই পড়া যায়, ফেরত আসা event-এ বা তৈরিকারীর নিজের রেফারেন্সে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

তাৎক্ষণিক dispatch-এর জন্য, Pydantic AI listener ডাকার আগে event-টি buffer করে, কিন্তু stream consumer এটি পায় কেবল সব listener চলার পর, তাই তারা কখনো অর্ধেক-নেওয়া সিদ্ধান্ত দেখে না। Attribution event-এর জায়গাতেই ছাপ দেওয়া হয়, তাই `await ctx.emit(event)`-এর পর তৈরিকারী নিজের রেফারেন্স থেকে `event.cancelled` পড়তে পারে (`emit` যে instance ফেরত দেয় সেটিই), আর একজন listener-এর তৈরি একটি event stream-এ সিদ্ধান্ত-event-এর পরে দেখা দেয়। Inline event তবুও ঠিক একবারই পৌঁছায়, একই event instance আবার তৈরি করলেও। Stream-dispatch listener ব্যবহারকারী-সংজ্ঞায়িত [`wrap_run_event_stream()`][pydantic_ai.capabilities.AbstractCapability.wrap_run_event_stream] wrapper-এর ভেতরে চলে।

/// note | মনে রাখুন

যেকোনো `on_event` listener অন্যথায় non-streaming একটি `agent.run()`-এর জন্য নিজে থেকে streaming চালু করে: মডেল রিকোয়েস্ট provider-এর streaming API দিয়ে করা হয়, যাতে শোনার মতো event থাকে। Provider-রা প্রায় সব দিক থেকে streaming আর non-streaming রিকোয়েস্ট একই রকম ধরে, তবে non-streamed রিকোয়েস্ট নিশ্চিত করতে হলে listener যুক্ত করবেন না।

///

## Provider-অনুযায়ী মানিয়ে নেওয়া টুল { #provider-adaptive-tools }

[`WebSearch`][pydantic_ai.capabilities.WebSearch], [`WebFetch`][pydantic_ai.capabilities.WebFetch], [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration], [`XSearch`][pydantic_ai.capabilities.XSearch] আর [`MCP`][pydantic_ai.capabilities.MCP] প্রত্যেকে একটি একক ক্ষমতা (web search, URL fetch, image generation, X search, MCP) দুটি বাস্তবায়ন জুড়ে কভার করে:

- **Native** — মডেল সমর্থন করলে মডেল provider ডাকে। কাজ ঘটে provider-এর দিকে (যেমন Anthropic-এর web search সার্ভার-পক্ষে চলে, ফল inline ফেরত দেয়)।
- **Local** — আপনার Python process-এ চলে। মডেল নেটিভ টুল সমর্থন না করলে ব্যবহৃত হয়; কাজ করে আপনার কোড (যেমন সরাসরি DuckDuckGo ডাকা)।

| Capability | লোকাল বিকল্প | নোট |
|---|---|---|
| [`WebSearch`][pydantic_ai.capabilities.WebSearch] | `local='duckduckgo'` বা `local=True` (DuckDuckGo) | `duckduckgo` optional group লাগে |
| [`WebFetch`][pydantic_ai.capabilities.WebFetch] | `local=True` (markdownify-ভিত্তিক fetch) | `web-fetch` optional group লাগে |
| [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] | `local=ImageGenerator(...)` বা `fallback_image_model='provider:image-model'` দিয়ে সরাসরি মডেল, বা `fallback_subagent_model=` দিয়ে subagent | সরাসরি পথগুলো subagent ছাড়াই [সরাসরি image-generation API](../image-generation.md) ব্যবহার করে |
| [`XSearch`][pydantic_ai.capabilities.XSearch] | `fallback_subagent_model=` দিয়ে subagent | কোনো ডিফল্ট non-xAI বিকল্প নেই; `fallback_subagent_model` এমন একটি xAI মডেলে সেট করুন যা [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] সমর্থন করে |
| [`MCP`][pydantic_ai.capabilities.MCP] | MCP সার্ভারে সরাসরি সংযোগ (ডিফল্ট) | যেকোনো [`MCPToolset`][pydantic_ai.mcp.MCPToolset] input নেয়; একটি URL থেকে transport নিজে থেকে চেনা হয় |

যেহেতু এই capability-গুলো মডেল-মুখী টুল দেয়, এদের `id`, `description` আর `defer_loading` ফিল্ড অর্থপূর্ণ: মডেল `load_capability` টুল দিয়ে মিলে যাওয়া workflow লোড না করা পর্যন্ত টুলটি লুকানো থাকা উচিত হলে `description` আর `defer_loading` সেট করুন। এদের প্রতিটি একটি একক স্থির বিষয় কভার করে, তাই `id` আগে থেকেই একটি স্থিতিশীল মানে ডিফল্ট (`'web_search'`, `'web_fetch'`, `'image_generation'`, `'x_search'`; `MCP` সার্ভার URL থেকে একটি তৈরি করে) — [durable execution](../durable_execution/overview.md) এদের দেওয়া toolset এটি দিয়েই চেনে, তাই এটি কনফিগারেশন ছাড়াই কাজ করে। শুধু নাম বদলাতে `id` সেট করুন, আর দুটি একই একটি ভাগ করলে কী হয় তা দেখুন [building custom capabilities](custom.md)-এ। এতে [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration]-ও অন্তর্ভুক্ত, যখন image generation শুধু একটি ছবি-নির্দিষ্ট workflow-এর জন্য উপলব্ধ থাকা উচিত, এটি একটি নেটিভ image টুল, একটি সরাসরি image-model বিকল্প বা subagent বিকল্পে মীমাংসা হোক।

একাধিক [toolsets](../toolsets.md) দেওয়া একটি [`Capability`][pydantic_ai.capabilities.Capability] প্রতিটির নাম দেয় `'{capability_id}_{index}'` — [durable execution](../durable_execution/overview.md) এগুলো এই id-তেই নিবন্ধন করে।

প্রতিটি দিক `native=` আর `local=` kwarg দিয়ে কনফিগার করুন। `native=` নেয় `True` (capability-র ডিফল্ট [native tool](../native-tools.md) instance ব্যবহার), `False` (নেটিভ বন্ধ), সূক্ষ্ম কনফিগারেশনের জন্য `WebSearchTool(...)`-এর মতো একটি স্পষ্ট instance, বা [`RunContext`][pydantic_ai.tools.RunContext] নিয়ে একটি নেটিভ টুল বা `None` ফেরত দেওয়া একটি callable (দেখুন [Dynamic Configuration](../native-tools.md#dynamic-configuration))। `None` ফেরত দেওয়া একটি factory সেই রিকোয়েস্টের জন্য নেটিভ টুল বাদ দেয়। `local=` নেয় `True` (বান্ডেল করা লোকাল বিকল্প, যে capability-র একটি আছে তাতে — `WebSearch` আর `WebFetch`), `False` (লোকাল বন্ধ), সমর্থিত জায়গায় একটি নাম-দেওয়া কৌশল string, বা যেকোনো callable, [`Tool`][pydantic_ai.tools.Tool] বা [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] — আর `ImageGeneration`-এ একটি [`ImageGenerator`][pydantic_ai.images.ImageGenerator]। লোকাল বিকল্পের জন্য দরকারি ঐচ্ছিক ইনস্টল নিজে বেছে নিতে হয় — আপনি এমন একটি লোকাল কৌশল চাইলে যার extra ইনস্টল নেই, capability তৈরির সময় (একটি ইনস্টল-ইঙ্গিতসহ) একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

/// note | একটি `fallback_subagent_model`-যুক্ত capability-তে `None`

[`XSearch`][pydantic_ai.capabilities.XSearch] আর [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] অসমর্থিত মডেলকে একটি লোকাল টুলের বদলে একটি subagent-এ পাঠায়। একবার একটি `fallback_subagent_model` সেট হলে, `None` ফেরত দেওয়া একটি factory আর কিছুই বাদ দেয় না: subagent টুল মডেলকে দেওয়া থাকে, এমনকি নেটিভ টুল সমর্থন করা একটি মডেলকেও, আর একে ডাকলে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে — দেখুন [X Search](x-search.md) আর [Image Generation](image-generation.md)।

///

```python title="provider_adaptive_tools.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import MCP, ImageGeneration, WebFetch, WebSearch, XSearch

agent = Agent(
    'anthropic:claude-fable-5-1',
    capabilities=[
        # Native when supported; DuckDuckGo fallback on unsupported models
        WebSearch(local='duckduckgo'),
        # Native when supported; markdownify-based fallback on unsupported models
        WebFetch(local=True),
        # Native when supported; direct image-model fallback otherwise
        ImageGeneration(fallback_image_model='openai:gpt-image-2.5-flare'),
        # Native on xAI; on other models, explicitly delegate to an xAI model
        XSearch(fallback_subagent_model='xai:grok-4.7'),
        # Runs the MCP server locally by default; pass `native=True` to also advertise native MCP
        MCP('https://mcp.example.com/api'),
    ],
)
```

`MCP`-এর ডিফল্ট অন্যদের উল্টো: যেহেতু MCP credential বহন করে, এটি ডিফল্টভাবে লোকালে চলে আর আপনি `native=True` দিয়ে নেটিভ MCP বেছে নেন। অন্যগুলো ডিফল্টভাবে নেটিভ আর আপনি `local=` দিয়ে লোকাল বেছে নেন।

[`XSearch`][pydantic_ai.capabilities.XSearch] [`WebSearch`][pydantic_ai.capabilities.WebSearch] আর [`WebFetch`][pydantic_ai.capabilities.WebFetch] থেকে একটু ভিন্ন: কোনো ডিফল্ট non-xAI বিকল্প নেই। আপনার এজেন্ট একটি xAI মডেলে না চললে, `fallback_subagent_model` স্পষ্টভাবে এমন একটি xAI মডেলে সেট করুন যা [`XSearchTool`][pydantic_ai.native_tools.XSearchTool] সমর্থন করে।

/// note | `fallback_model` অবচিত

[`XSearch`][pydantic_ai.capabilities.XSearch] আর [`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] দুটোতেই, `fallback_model` হলো `fallback_subagent_model`-এর আগের নাম। এটি কাজ করতে থাকে — Python-এ আর একটি [agent spec](../agent-spec.md)-এ — আর সতর্ক করে; দুটি নাম একসাথে দেওয়া প্রত্যাখ্যাত: capability তৈরির সময় [`UserError`][pydantic_ai.exceptions.UserError], আর একটি spec লোড করার সময় spec loader এটিকে যে `ValueError`-এ মোড়ায়। নতুন নামটি বলে এটি কোন বিকল্প কনফিগার করে: একটি বাড়তি এজেন্ট রান, আপনার নিজের process-এ চলা একটি `local=` টুলের — বা `ImageGeneration`-এ একটি `fallback_image_model`-এর — বিপরীতে।

///

কিছু সীমাবদ্ধতা-ফিল্ডের জন্য নেটিভ টুল লাগে (বান্ডেল করা লোকাল বিকল্প এগুলো প্রয়োগ করতে পারে না) — এগুলো দিলে capability নেটিভ পথে আটকে যায়। মডেল নেটিভ টুল সমর্থন না করলে, বা এর নেটিভ টুল সীমাবদ্ধতা প্রয়োগ করতে না পারলে (দেখুন [restricting parameters](../native-tools.md#restricting-parameters)), capability একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

```python title="constraints.py"
# Limit to 5 searches per run — requires native (the local fallback can't track call count)
WebSearch(max_uses=5)

# Only fetch example.com — enforced locally when native is unavailable or can't apply the filter
WebFetch(allowed_domains=['example.com'], local=True)
```

/// warning | সাধারণ ভুল

`WebSearch(max_uses=5)` দিয়ে ভাবা যে লোকাল DuckDuckGo বিকল্পেও কাজ করবে। লোকাল বিকল্প কলের সংখ্যা গুনতে পারে না, তাই এই ফিল্ড capability-কে নেটিভ পথে আটকে দেয় — নেটিভ web search সমর্থন না থাকা একটি মডেলে এটি চুপচাপ লোকালে না গিয়ে `UserError` তোলে।

///

### নিজেরটি তৈরি { #building-your-own }

পাঁচটি capability-ই [`NativeOrLocalTool`][pydantic_ai.capabilities.NativeOrLocalTool]-এর subclass, যা আপনি সরাসরি ব্যবহার করতে বা subclass করে নিজের provider-অনুযায়ী টুল তৈরি করতে পারেন। যেমন, [`CodeExecutionTool`][pydantic_ai.native_tools.CodeExecutionTool]-কে একটি লোকাল বিকল্পের সাথে জোড়া দিতে:

```python title="custom_native_or_local.py"
from pydantic_ai.native_tools import CodeExecutionTool
from pydantic_ai.capabilities import NativeOrLocalTool

cap = NativeOrLocalTool(native=CodeExecutionTool(), local=my_local_executor)
```

## থার্ড-পার্টি capability { #third-party-capabilities }

থার্ড-পার্টি প্যাকেজ নিজস্ব capability প্রকাশ করে — ইকোসিস্টেমের জন্য দেখুন [Third-Party Capabilities](third-party.md), আর নিজের capability অন্যদের জন্য উপলব্ধ করতে দেখুন [Publishing capabilities](custom.md#publishing-capabilities)।

/// check | সংক্ষেপে মনে রাখুন

* capability = টুল + hook + instructions + model settings একসাথে বাঁধা একটি পুনর্ব্যবহারযোগ্য একক; `capabilities=[...]` দিয়ে দিন।
* Core মডেল/framework-নির্ভর capability দেয়; বাকিটা Pydantic AI Harness-এ।
* subclass ছাড়া সহজ বান্ডেল: `Capability(instructions=..., tools=[...])`; চাহিদামতো লোড: `defer_loading=True`।
* capability event: namespace-সহ dataclass, `await ctx.emit(...)`; `@on_event(Class)` দিয়ে শুনুন।
* `WebSearch`/`WebFetch`/`ImageGeneration`/`XSearch` ডিফল্টভাবে নেটিভ, `local=` দিয়ে লোকাল বিকল্প; `MCP` ডিফল্টভাবে লোকাল।

///
