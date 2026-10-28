
# Macroscope { #macroscope }

/// note | এই পেজে যা শিখবেন

* `Macroscope` দিয়ে একটি এজেন্টের ভেতর থেকে লোকাল [Macroscope](https://docs.macroscope.com/cli) কোড রিভিউ চালিয়ে ফলাফল কাঠামোবদ্ধ ডেটা হিসেবে পাওয়া।
* CLI সেটআপ, `run_macroscope_review` টুল, অপশন, durable execution আর ডেটা ও বিশ্বাস।

///

`Macroscope` একটি এজেন্টের ভেতর থেকে একটি লোকাল [Macroscope](https://docs.macroscope.com/cli) কোড রিভিউ চালায়: একটি টুল রানের workspace-এ ইনস্টল করা `macroscope` CLI চালায়, stream করা ফলাফল পার্স করে আর কাঠামোবদ্ধ ডেটা হিসেবে ফেরত দেয়। এজেন্ট প্রতিটি ফলাফল যাচাই করে আর এর আগে থেকে থাকা টুল দিয়ে আসলগুলো ঠিক করে -- এই capability শুধু ফলাফল সামনে আনে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/macroscope/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

Macroscope বর্তমান branch-এর diff রিভিউ করে আর ফলাফল stream করে, কিন্তু এটি editor plugin হিসেবে আসে (Claude Code, Codex, Cursor, OpenCode)। এই capability একটি Pydantic AI এজেন্টকে একই রিভিউ-আর-ঠিক-করার loop দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

একজন সিনিয়র রিভিউয়ার (Macroscope) আপনার PR দেখে বলেন "এই 5টি জায়গায় সমস্যা মনে হচ্ছে"। এজেন্ট প্রতিটি নিজে খুলে দেখে — কোনটা সত্যিই bug, কোনটা ভুল সতর্কতা — আর আসলগুলো ঠিক করে। Macroscope শুধু আঙুল দেখায়; ঠিক করে এজেন্ট, নিজের `FileSystem`/`Shell` টুল দিয়ে।

///

## ব্যবহার { #usage }

⟦CODE1⟧

রিভিউ চলে এজেন্টের [workspace](../workspace.md)-এ, এর working directory-তে, যা repository হওয়া উচিত: `LocalWorkspace`-এ আপনার মেশিন, বা রান একটি ব্যবহার করলে sandbox। workspace ছাড়া একটি রান শুরুতেই ব্যর্থ হয়। `macroscope` CLI আগে workspace-এ ইনস্টল আর authenticate করা থাকতে হবে:

1. ইনস্টল: `curl -sSL https://raw.githubusercontent.com/prassoai/macroscope-local/main/install.sh | bash`
2. একবার `macroscope` চালিয়ে sign in করুন আর একটি Macroscope workspace বাছুন।

capability আপনার হয়ে ইনস্টল বা authenticate করতে পারে না। মডেলও এই সেটআপ-সমস্যা ঠিক করতে পারে না, তাই টুল এগুলোতে টুল retry খরচ না করে `UserError` তোলে আর রান থামে। একটি অনুপস্থিত binary ইনস্টল কমান্ড জানায় (বা `command` একটি path হলে path-এর নাম দেয়), চালু করা যায় না এমন একটি binary OS error জানায়, আর কখনো শুরু না হওয়া একটি রিভিউ (সাধারণত আপনি sign in না করায়) আপনাকে সেটআপ শেষ করতে `macroscope` চালাতে বলে, বা CLI একটি অজানা ref জানালে কনফিগার করা `base` ঠিক করতে বলে। ব্যতিক্রম হলো মডেলের দেওয়া একটি `base` দিয়ে শুরু হতে ব্যর্থ একটি রিভিউ: সেটি মডেলকে একটি retry হিসেবে জানানো হয়, যাতে এটি ref বাদ দিতে বা বদলাতে পারে।

টুল `macroscope codereview --raw` চালায়। `--raw` ছাড়া build খুব পুরনো; ব্যবহারের সময় CLI নিজেকে হালনাগাদ করে।

## টুল { #the-tool }

| টুল | উদ্দেশ্য |
|---|---|
| `run_macroscope_review` | বর্তমান branch-এ `macroscope codereview` চালিয়ে review id, চূড়ান্ত অবস্থা আর ফলাফল ফেরত দেয়। একটি ঐচ্ছিক `base` git ref নেয়। |

প্রতিটি ফলাফল একটি `MacroscopeIssue`, `issue_id`, `sequence`, `path`, `line`, `severity`, `category` আর `body`-সহ। capability-র ডিফল্ট instructions এজেন্টকে প্রতিটি ফলাফল অবিশ্বস্ত ধরতে বলে: একটি সমস্যা আসল কিনা নিশ্চিত করতে প্রভাবিত কোড পড়া, ভুল সতর্কতা আর নকল বাদ দেওয়া, আর প্রতিটি সংশোধন যাচাই করা।

`status` হলো CLI-র জানানো অবস্থা, যেমন `completed` বা `failed`। একটি জানানোর আগে CLI থামলে, টুল তবুও আসা ফলাফল ফেরত দেয় আর কেন তা বলতে `status` সেট করে: রিভিউ `timeout`-এ পৌঁছালে `timed_out`, বা CLI একটি error দিয়ে বেরোলে `interrupted`। একটি রিভিউ শুরুর আগেই timeout হলে, মডেল একটি retry পায়।

## অপশন { #options }

`Macroscope`-এর প্রতিটি ফিল্ড এর ডিফল্টসহ:

⟦CODE2⟧

একটি প্রতি-কল `base` আর্গুমেন্ট ফিল্ডের ওপর অগ্রাধিকার পায়। রিভিউ একটি দূরের সার্ভিস ডাকে, তাই timeout ডিফল্টভাবে উদার; timeout-এ workspace CLI থামায় আর মডেল আসা ফলাফল পায় (দেখুন [The tool](#the-tool))। workspace কমান্ড চালাতে না পারলে (যেমন একটি শুধু-পড়া) টুলটি দেওয়া হয় না। `-` দিয়ে শুরু হওয়া একটি `base` প্রত্যাখ্যাত। `command` `-` দিয়ে শুরু হতে বা `=` রাখতে পারে না; এর বদলে CLI workspace-এর `PATH`-এ রাখুন।

## পরিসর আর মিলন { #scope-and-composition }

এই capability শুধু ফলাফল সামনে আনে: এটি ফাইল সম্পাদনা করে না, worktree তৈরি করে না, বা commit করে না। এজেন্ট যাতে কোড পড়তে আর সংশোধন প্রয়োগ করতে পারে সেজন্য এটি `FileSystem` বা `Shell`-এর সাথে জোড়া দিন। সংশোধন আপনার working tree থেকে দূরে রাখতে, এজেন্টকে এর workspace হিসেবে একটি আলাদা worktree দিন। টুল একটি রিভিউর ফলাফল এক ফলে ফেরত দেয়, যা বড় হতে পারে; এর আকার সীমিত করতে [Tool Output Limits](tool-output-limits.md) যোগ করুন।

## Durable execution { #durable-execution }

Temporal-এ [durable execution](../durable_execution/overview.md)-এর অধীনে, প্রতিটি রিভিউ নিজের activity-তে চলে, যা `timeout` যোগ 30 সেকেন্ড পায়। তাই workspace একটি ধীর রিভিউ আগে থামায়, আর মডেল তবুও আসা ফলাফল পায়। একটি ভিন্ন activity সীমা সেট করতে, [Temporal command timeouts](../durable_execution/temporal.md#harness-command-timeouts)-এর মতো [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] ব্যবহার করুন।

activity-গুলোর নাম capability-র `id` অনুযায়ী, যার ডিফল্ট `macroscope`, তাই durable execution-এ কোনো কনফিগারেশন লাগে না। `id` বদলালে এদের নাম বদলে যায়, যা চলমান রান তখন খুঁজে পায় না।

## ডেটা আর বিশ্বাস { #data-and-trust }

রিভিউ branch-এর diff Macroscope-এর সার্ভিসে আপলোড করে। ফলাফলের body সেই diff থেকে Macroscope-এর মডেলের লেখা, তাই আপনি বিশ্বাস করেন না এমন একটি branch-এ এগুলোকে অবিশ্বস্ত input ধরুন: এজেন্টকে একটি sandbox workspace-এ চালান, বা এর shell আর লেখার টুলের জন্য [approval](../deferred-tools.md) চান।

/// warning | সতর্কতা

রিভিউর সময় আপনার পুরো branch diff Macroscope-এর সার্ভারে যায়। গোপন বা নিয়ন্ত্রিত (regulated) কোডে চালানোর আগে আপনার প্রতিষ্ঠানের নীতিমালা যাচাই করুন।

///

## Telemetry { #telemetry }

`Macroscope` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) প্রতিটি `run_macroscope_review` কল একটি tool span হিসেবে লেখে, আর capability নিজস্ব একটি span-এর যোগ্য কোনো সিদ্ধান্ত নেয় না।

## এর দুটি { #two-of-them }

`Macroscope` ডিফল্ট `id` `'macroscope'` ঘোষণা করে। `id` capability-র instructions-এর key, যাতে এগুলো চিহ্নিত করা যায়, আর একটি ছাড়াই `defer_loading=True` কাজ করতে দেয়। এটি ভাগ করা এক এজেন্টে দুটি `Macroscope` একটি রিভিউ কনফিগারেশন দুবার বলা: মিললে এরা এক হয়ে যায়, আর ভিন্ন হলে এজেন্ট তৈরির সময় একটি `UserError` তোলে। দুটি রাখতে, প্রতিটিকে নিজের `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ দুটোই `run_macroscope_review` নিবন্ধন করে।

আগের release কোনো ডিফল্ট `id` ঘোষণা করত না, তাই রান শুরুর সময় দুটি সবসময় টুলের নামে ব্যর্থ হতো। এখন দুটি অভিন্ন এক হয়ে যায়, আর ভিন্ন দুটি এজেন্ট তৈরির সময় ব্যর্থ হয়।

## Agent spec { #agent-spec }

`Macroscope` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে, তাই আপনি Python-এর বদলে একটি config ফাইলে এটি ঘোষণা করতে পারেন:

⟦CODE3⟧

⟦CODE4⟧

`custom_capability_types` দিন, যাতে spec loader জানে `Macroscope` কীভাবে তৈরি করতে হয়।

## আরও পড়ুন { #further-reading }

- [Macroscope CLI documentation](https://docs.macroscope.com/cli)
- [Pydantic AI capabilities](../capabilities/overview.md)
- [Toolsets](../toolsets.md)

## API রেফারেন্স { #api-reference }

⟦CODE5⟧

⟦CODE6⟧

⟦CODE7⟧

/// check | সংক্ষেপে মনে রাখুন

* `Macroscope()` একটি টুল দেয়: `run_macroscope_review` — শুধু ফলাফল, সম্পাদনা নয়; সাথে `FileSystem`/`Shell` দিন।
* `macroscope` CLI আগে workspace-এ ইনস্টল আর sign in করা থাকতে হবে।
* প্রতিটি ফলাফল অবিশ্বস্ত — এজেন্ট কোড পড়ে যাচাই করে তবেই ঠিক করে।
* diff Macroscope-এর সার্ভারে যায়; অবিশ্বস্ত branch-এ sandbox বা অনুমোদন।

///
