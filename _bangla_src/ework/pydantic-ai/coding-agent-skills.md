# কোডিং এজেন্টের Skill { #coding-agent-skills }

/// note | এই পেজে যা শিখবেন

* Claude Code, Codex, Cursor-এর মতো কোডিং এজেন্টকে Pydantic AI-এর হালনাগাদ জ্ঞান দেওয়ার "skill" কী।
* তিনভাবে ইনস্টল: Claude Code plugin, agentskills.io, আর প্রজেক্টের dependency থেকে library-skills।

///

কোডিং এজেন্ট দিয়ে Pydantic AI অ্যাপ্লিকেশন বানালে, আপনার এজেন্টকে framework-এর হালনাগাদ জ্ঞান দিতে [`pydantic/skills`](https://github.com/pydantic/skills) repository থেকে Pydantic AI skill ইনস্টল করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

কোডিং এজেন্টের জ্ঞান তার প্রশিক্ষণের সময় পর্যন্ত; Pydantic AI দ্রুত বদলায়, তাই সে পুরনো নিয়মে কোড লিখতে পারে। skill হলো তার হাতে দেওয়া হালনাগাদ হ্যান্ডবুক: দরকার হলে খুলে দেখে নেয় নতুন নিয়ম কী।

///

[Agent skill](https://agentskills.io) হলো নির্দেশনা আর তথ্যসূত্রের প্যাকেজ, যা কোডিং এজেন্ট দরকার অনুযায়ী লোড করে। skill ইনস্টল থাকলে, কোডিং এজেন্ট Pydantic AI-এর প্যাটার্ন, কাঠামোর নির্দেশনা আর প্রচলিত কাজের তথ্যসূত্র পায়, যার মধ্যে আছে [টুল](tools.md), [ক্যাপাবিলিটি](capabilities/overview.md), [গোছানো আউটপুট](output.md), [স্ট্রিমিং](agent.md#streaming-events-and-final-output), [টেস্টিং](testing.md), [বহু-এজেন্টে দায়িত্ব ভাগ](multi-agent-applications.md), [hook](hooks.md) আর [agent spec](agent-spec.md)।

আপনার কোডিং এজেন্ট একটি নতুন Pydantic AI অ্যাপ্লিকেশন তৈরি করলে, skill-টি পর্যবেক্ষণের জন্য [Pydantic Logfire](logfire.md) সেটআপ করিয়ে নেয় (যদি না আপনি ইতিমধ্যে অন্য কোনো OpenTelemetry backend ব্যবহার করেন), ফলে প্রথম সংস্করণ থেকেই প্রতিটি এজেন্ট রান, মডেল রিকোয়েস্ট আর টুল কল দেখতে পান। এটি [Pydantic AI Gateway](gateway.md)-ও চেনে, যা কয়েকটি প্রোভাইডারের মডেলের জন্য একটি চাবি, আর সেটি ব্যবহার করা `gateway/` মডেল স্ট্রিং।

Logfire-এর বাকি কাজের জন্য, যেমন অ্যাপ্লিকেশনের বাকি অংশ instrument করা, trace খোঁজা বা eval চালানো, [`pydantic/skills`](https://github.com/pydantic/skills) repository-তে Logfire skill-ও আছে: `logfire` plugin ইনস্টল করুন, অথবা নির্দেশিত সেটআপের জন্য আপনার এজেন্টকে [pydantic.dev/ai-setup.md](https://pydantic.dev/ai-setup.md) দেখিয়ে দিন।

/// note | মনে রাখুন

আপনার Pydantic AI এজেন্টকে তার নিজের skill দিতে চাইলে, Pydantic AI Harness-এর [`Skills`](harness/skills.md) ক্যাপাবিলিটি দেখুন। (এই পেজের skill আপনার *কোডিং সহকারীর* জন্য, আর `Skills` ক্যাপাবিলিটি আপনার *বানানো এজেন্টের* জন্য।)

///

## ইনস্টলেশন { #installation }

### Claude Code { #claude-code }

Anthropic marketplace থেকে [অফিসিয়াল Pydantic AI plugin](https://claude.com/plugins/pydantic-ai) ইনস্টল করুন, যা ডিফল্টভাবেই পাওয়া যায়:

```bash
claude plugin install pydantic-ai@claude-plugins-official
```

বিকল্প হিসেবে, [`pydantic/skills`](https://github.com/pydantic/skills) marketplace থেকে ইনস্টল করতে পারেন, যেখানে Pydantic AI skill-এর পাশাপাশি Pydantic-এর রক্ষণাবেক্ষণ করা অন্য skill-ও আছে:

⟦CODE1⟧

### সব এজেন্টের জন্য (agentskills.io) { #cross-agent-agentskillsio }

[skills CLI](https://github.com/vercel-labs/skills) দিয়ে Pydantic AI skill ইনস্টল করুন:

```bash
npx skills add pydantic/skills
```

[agentskills.io](https://agentskills.io) মানকের মাধ্যমে এটি ৩০টির বেশি এজেন্টে কাজ করে, যার মধ্যে আছে Claude Code, Codex, Cursor আর Gemini CLI।

### Library Skills { #library-skills }

Pydantic AI তার skill-গুলো প্যাকেজের সাথেই দেয়, তাই [library-skills.io](https://library-skills.io) দিয়ে সরাসরি আপনার প্রজেক্টের dependency থেকে ইনস্টল করতে পারেন:

```bash
uvx library-skills --all
```

`--all` ফ্ল্যাগ দরকার, কারণ skill-গুলো `pydantic-ai-slim`-এর ভেতরে আছে, যা `pydantic-ai` meta-package-এর একটি পরোক্ষ (transitive) dependency। এটি ছাড়া `library-skills` শুধু সরাসরি dependency খোঁজে আর সেগুলো খুঁজে পাবে না।

ডিফল্ট `.agents/skills/` ফোল্ডারের পাশাপাশি `.claude/skills/`-এও ইনস্টল করতে `--claude` যোগ করুন, কারণ Claude Code `.agents/` থেকে পড়ে না।

এই ইনস্টলেশনে অন্য এজেন্ট framework থেকে Pydantic AI-তে অ্যাপ্লিকেশন সরানোর [migration skill](framework-migration.md)-ও থাকে।

## আরও দেখুন { #see-also }

- [`pydantic/skills`](https://github.com/pydantic/skills): মূল repository
- [agentskills.io](https://agentskills.io): agent skill-এর খোলা মানক
- [library-skills.io](https://library-skills.io): আপনার প্রজেক্টের dependency-র সাথে আসা agent skill ইনস্টল করুন
