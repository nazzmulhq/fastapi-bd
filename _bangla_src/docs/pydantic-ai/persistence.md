
# Persistence { #persistence }

/// note | এই পেজে যা শিখবেন

* "persistence", "memory", "session" — এক নামের আড়ালে চারটি আলাদা সমস্যা, আর প্রতিটির সঠিক সমাধান।
* একটি কথোপকথন (`Conversation`) নিজের ডেটাবেসে কীভাবে রাখবেন আর পরে আবার চালাবেন।
* কেন শুধু বার্তা নয়, পুরো `Conversation` রাখা উচিত।
* কথোপকথন-জুড়ে মনে রাখা (`Memory`), `StepPersistence`, আর provider-এর কাছে state রাখা।

///

একটি প্রোডাকশন এজেন্ট প্রতিটি কথোপকথন অনেক রিকোয়েস্ট, process আর restart জুড়ে পরিবেশন করে, তাই এর state-কে process ছাড়া অন্য কোথাও থাকতে হয়।

"Persistence", "memory", "sessions": কয়েকটি ভিন্ন সমস্যা এই নামগুলোতে পরিচিত, আর তাদের উত্তরও ভিন্ন। এখান থেকে শুরু করুন:

| আপনি চান… | ব্যবহার করুন | কোথায় থাকে |
|---|---|---|
| একটি কথোপকথন সংরক্ষণ করে পরে আবার তুলে নিতে — একটি chat thread, একটি support ticket, গতকালের কথা মনে রাখা একটি assistant | [এর `Conversation` রাখুন](#storing-a-conversation-yourself) আপনার নিজের ডেটাবেসের একটি কলামে | Core |
| প্রতিটি রান কী করেছে তার একটি log, আর একটি রান চালিয়ে যাওয়া বা fork করার snapshot | [`StepPersistence`](harness/step-persistence.md) | [Pydantic AI Harness](harness/index.md) |
| এজেন্ট কারো সম্পর্কে যা শিখেছে তা শুধু একটির ভেতরে নয়, কথোপকথন *জুড়ে* মনে রাখুক | [`Memory`](harness/memory.md) | [Pydantic AI Harness](harness/index.md) |
| একটি রান টুল কলের মাঝে process মরে গেলেও টিকে থাকুক, শেষ হওয়া ধাপগুলো replay করে আর চলমানটি আবার চেষ্টা করে | [Durable execution](durable_execution/overview.md) | Core |

checkpoint-ধরনের persistence-এর জন্য, [`StepPersistence`](harness/step-persistence.md) একটি রানের প্রতিটি স্থির টুল-কল সীমায় একটি message-history snapshot সংরক্ষণ করে, তাই আপনি পরে রানটি চালিয়ে যেতে বা একটি সংরক্ষিত snapshot থেকে fork করতে পারেন; একটি ধাপের মাঝপথে crash করা রান আবার চালাতে, [durable execution](durable_execution/overview.md) ব্যবহার করুন।

প্রথম দুটি সারি "আমার এজেন্টকে কীভাবে memory দেব?" প্রশ্নেরও উত্তর, মানুষ সাধারণত যা বোঝায় তার বেশিরভাগের জন্য: চলমান কথোপকথন সম্পর্কে একটি এজেন্টের memory-*ই* হলো এর message history। এর জন্য যোগ করার মতো আলাদা কোনো memory সিস্টেম নেই — ইতিহাস রাখা আর ফেরত দেওয়াই পুরো পদ্ধতি। Memory [নিজস্ব একটি বিষয়](#remembering-across-conversations) হয়ে ওঠে কেবল তখনই, যখন একে thread-এর চেয়ে বেশি দিন টিকতে হয়।

সারিগুলো একসাথে কাজ করে: একটি durable engine একটি রান জীবিত রাখে, `StepPersistence` প্রতিটি রান কী করেছে তা লেখে, একটি সংরক্ষিত কথোপকথন হলো যা আপনি পরের রানকে দেন, আর `Memory` হলো thread শেষ হলে যা থাকে। একটি chat thread সংরক্ষণ করতে চেয়ে durable engine ধরা — এটাই সাধারণ ভুল; এর জন্য একটি `jsonb` কলামই যথেষ্ট।

/// tip | উদাহরণ দিয়ে বুঝি

একজন ডাক্তারের কথা ভাবুন:

* **Conversation** = আজকের রোগী-দেখার নোট। পরের ভিজিটে ফাইলটা খুলে আগের কথা থেকে শুরু করেন।
* **StepPersistence** = প্রতিটি পরীক্ষা-নিরীক্ষার ধাপের লগবুক — কোন টেস্ট দেওয়া হলো, কোনটার ফল এসেছে।
* **Memory** = রোগীর স্থায়ী মেডিকেল প্রোফাইল ("পেনিসিলিনে অ্যালার্জি") — যেকোনো ভিজিটে কাজে লাগে।
* **Durable execution** = অপারেশনের মাঝে বিদ্যুৎ গেলে জেনারেটর — চলমান কাজটাই যেন থেমে না যায়।

///

## কথোপকথন নিজে সংরক্ষণ করা { #storing-a-conversation-yourself }

Pydantic AI ইচ্ছে করে আপনার ডেটাবেস নিয়ে কোনো মত চাপায় না। এটি আপনাকে একটি পূর্ণ-বিশ্বস্ততার serialization সীমা দেয় আর schema আপনার ওপর ছেড়ে দেয়, কারণ এখানে টিমগুলোর পছন্দ framework যতটা কাজে লাগার মতো অনুমান করতে পারে তার চেয়ে বেশি ভিন্ন: ইতিহাস কোন table-এর সাথে যুক্ত, কোন tenant কলাম লাগে, কতদিন রাখবেন।

রাখার জিনিসটি হলো একটি [`Conversation`][pydantic_ai.conversation.Conversation]। প্রতিটি রান আপনাকে একটি দেয় [`result.conversation`][pydantic_ai.agent.AgentRunResult.conversation] হিসেবে, আর প্রতিটি রান `conversation=` হিসেবে একটি ফেরত নেয়। এটি বার্তাগুলো আর তাদের বাইরে যা থাকে তা রাখে: চলমান [`usage`][pydantic_ai.conversation.Conversation.usage], key হিসেবে ব্যবহারের [`conversation_id`][pydantic_ai.conversation.Conversation.conversation_id], আর শেষ রান যে [deferred tool request](deferred-tools.md#pausing-a-conversation)-এ থেমেছিল সেগুলো। এটি আপনার নিজের একটি Pydantic model-এর ফিল্ড হিসেবে রাখুন, বা [`ConversationTypeAdapter`][pydantic_ai.conversation.ConversationTypeAdapter] দিয়ে আলাদাভাবে:

```python title="storing_a_conversation.py"
from pydantic_ai import Agent, ConversationTypeAdapter

agent = Agent('openai:gpt-6.1-sol', instructions='Be a helpful assistant.')

result = agent.run_sync('Tell me a joke.')
stored = ConversationTypeAdapter.dump_json(result.conversation)  # (1)!

conversation = ConversationTypeAdapter.validate_json(stored)
result = agent.run_sync('Explain?', conversation=conversation)
print(result.usage.requests)  # (2)!
#> 2
```

1. একটি `jsonb` কলাম বা সমতুল্যের জন্য JSON bytes, `result.conversation_id` দিয়ে key করা।
2. দ্বিতীয় রান প্রথমটি থেকে গুনতে থাকে, তাই একটি [`UsageLimits`][pydantic_ai.usage.UsageLimits] বাজেট প্রতিটি রানের বদলে পুরো কথোপকথন কভার করে। প্রতিটি রান শুধু তার সময়ে provider যা bill করেছে তা যোগ করে, তাই আগের একটি রানের স্থগিত রাখা একটি turn যখন একটি রান আবার চালায়, তখনও এটি কথোপকথনের সত্যিকারের মোট থাকে।

এটি message history-র নিজস্ব [`ModelMessagesTypeAdapter`](message-history.md#storing-and-loading-messages-to-json)-এর মতো একই বিশ্বস্ততায় যাওয়া-আসা করে, এমন ফিল্ডসহ যা কখনো মডেলে পাঠানো হয় না, যেমন একটি part-এর শুধু-অ্যাপ্লিকেশন `metadata`। যেহেতু ওই ফিল্ডের টাইপ `Any`, JSON রূপ নেই এমন মান যাওয়ার পথে স্বাভাবিক করা হয়: একটি `tuple` আবার লোড হয় `list` হিসেবে, একটি `datetime` এর ISO string হিসেবে, আর কাঁচা `bytes` এর base64 string হিসেবে। ["What survives a round-trip"](message-history.md#storing-and-loading-messages-to-json) নোট সীমার ক্ষেত্রগুলো আলোচনা করে। Pydantic AI একটি message part যোগ করলে কোনো schema migration লাগে না, কারণ পুরনো version-এ serialize করা একটি কথোপকথন এখনও deserialize হয়।

প্রতিটি turn-এ পুরো কথোপকথন আবার লেখা কোড সহজ রাখে, কিন্তু প্রতিটি লেখাকে এ পর্যন্ত কথোপকথনের সমান বড় করে। লেখাকে turn-এর অনুপাতে রাখতে, বার্তাগুলো তাদের নিজস্ব একটি table-এ রাখুন, প্রতিটি রানের [`new_messages()`][pydantic_ai.agent.AgentRunResult.new_messages] `ModelMessagesTypeAdapter` দিয়ে যোগ করে, আর কথোপকথনের বাকিটা তাদের পাশে রাখুন: এর `usage`, এর `conversation_id`, আর এর `deferred_tool_requests`, যা ছাড়া একটি থামা কথোপকথন আবার চালানো যায় না। চালিয়ে যেতে `Conversation(messages=..., usage=..., conversation_id=..., deferred_tool_requests=...)` হিসেবে আবার জোড়া লাগান। [Persisting sessions](message-history.md#persisting-sessions) দুটোই ধাপে ধাপে দেখায়।

একটি শেষ হওয়া রানের আউটপুট এর কথোপকথনের পাশে রাখতে, [`AgentRunResult`][pydantic_ai.agent.AgentRunResult] নিজেই রাখুন: দেখুন [Storing complete run results](message-history.md#storing-complete-run-results)।

/// info | এক নজরে: দুটি সংরক্ষণ-কৌশল

| কৌশল | কীভাবে | সুবিধা | অসুবিধা |
|------|--------|--------|---------|
| পুরো conversation একটি কলামে | প্রতি turn-এ `ConversationTypeAdapter` দিয়ে পুরোটা আবার লেখা | কোড খুব সহজ | লম্বা কথোপকথনে প্রতিটি লেখা বড় |
| বার্তা আলাদা table-এ | প্রতি রানে শুধু `new_messages()` যোগ, পাশে `usage`/`conversation_id`/`deferred_tool_requests` | লেখা ছোট থাকে | পড়ার সময় আবার জোড়া লাগাতে হয় |

///

### একটি chat UI-এর পাঠানো ইতিহাস সংরক্ষণ করা { #storing-a-history-a-chat-ui-sent-you }

[Vercel AI](ui/vercel-ai.md) বা [AG-UI](ui/ag-ui.md)-এর একটি frontend নিজের একটি message list রাখে, আর একে পরিবেশন করা adapter হাতে কোনো রিকোয়েস্ট ছাড়াই দুই দিকে রূপান্তর করে: [`load_messages`][pydantic_ai.ui.UIAdapter.load_messages] protocol-এর বার্তাগুলোকে [`ModelMessage`][pydantic_ai.messages.ModelMessage]-এ বদলায়, আর [`dump_messages`][pydantic_ai.ui.UIAdapter.dump_messages] সেগুলো আবার ফেরত বদলায়।

```python title="storing_ui_history.py"
from pydantic_ai.ui.vercel_ai import VercelAIAdapter
from pydantic_ai.ui.vercel_ai.request_types import TextUIPart, UIMessage

sent_by_the_browser = [
    UIMessage(id='1', role='user', parts=[TextUIPart(text='Tell me a joke.')])
]

history = VercelAIAdapter.load_messages(sent_by_the_browser)  # (1)!
for_the_browser = VercelAIAdapter.dump_messages(history)  # (2)!
```

1. browser যা পাঠিয়েছে, একটি ইতিহাস হিসেবে যার বিপরীতে একটি এজেন্ট চলতে পারে — আর এটিই রাখার রূপ।
2. browser যা ফেরত পায়, ডেটাবেসে যাওয়ার পথে নয়, প্রান্তে রূপান্তরিত।

protocol-এর রূপ রাখার বদলে Pydantic AI-এর দিক রাখুন আর প্রান্তে রূপান্তর করুন। wire ফরম্যাটে একটি ইতিহাসের বহন করা সব কিছুর জায়গা নেই — প্রতিটি কী রাখে আর কী ফেলে দেয় তা লেখা আছে [Vercel AI message metadata](ui/vercel-ai.md#message-metadata) আর [AG-UI preserving files across round-trips](ui/ag-ui.md#preserving-files-across-round-trips)-এর নিচে — আর তারা যে ফিল্ডগুলো ফেলে দেয় সেগুলোই পরের মডেল রিকোয়েস্টের দরকার।

/// note | client-এর দেওয়া ইতিহাস বিশ্বস্ত state নয়

আপনার লোড করা ইতিহাস একটি browser থেকে এলে, একটি এজেন্টে দেওয়ার আগে তা পরিষ্কার (sanitize) করুন। দেখুন [Loading untrusted history](message-history.md#loading-untrusted-history) আর [trust boundary](message-history.md#trust-boundary-for-client-supplied-history)।

///

### কেন বার্তার বদলে একটি কথোপকথন { #why-a-conversation-rather-than-its-messages }

বার্তাগুলো দেখতে যতটা মনে হয় তার চেয়ে বেশি বহন করে: [`run_id` আর `conversation_id`](message-history.md#correlating-runs-with-run_id-and-conversation_id) প্রতিটিতে ছাপ দেওয়া থাকে, তাই storage থেকে আবার লোড করা একটি ইতিহাস আপনার নিজের কোনো হিসাব-রক্ষা ছাড়াই [Logfire](logfire.md)-এ সম্পর্কিত থাকে।

তারা যা বহন করতে পারে না সেটাই [`Conversation`][pydantic_ai.conversation.Conversation] থাকার কারণ। এর [`usage`][pydantic_ai.conversation.Conversation.usage] হলো কথোপকথনের চলমান মোট, [`tool_calls`][pydantic_ai.usage.RunUsage.tool_calls]-সহ, যা কোনো বার্তা লেখে না; শুধু বার্তা থেকে চালিয়ে গেলে প্রতিটি turn-এর [`UsageLimits`][pydantic_ai.usage.UsageLimits] বাজেট শূন্য থেকে আবার শুরু হয়। আর যে রান [deferred টুলের জন্য থেমেছিল](deferred-tools.md#pausing-a-conversation), সেটি এমন কল রেখে যায় যা বার্তাগুলো উত্তরহীন দেখায়, কিন্তু বলে না কোনটির অনুমোদন লাগবে আর কোনটির একটি বাইরের ফল, বা কোন metadata দিয়ে সেগুলো defer করা হয়েছিল। কথোপকথন দুটোই বহন করে। usage বহন করা আপনার trace যা দেখায় তার কিছুই বদলায় না: প্রতিটি রানের span যেকোনো ক্ষেত্রে সেই রানের নিজের token জানায়, তাই একটি কথোপকথনের খরচ হলো এর রানগুলোর যোগফল।

/// warning | সাধারণ ভুল

শুধু `result.all_messages()` সংরক্ষণ করে পরের রানে `message_history=` দেওয়া। কাজ চলে, কিন্তু: (১) `UsageLimits(request_limit=20)` প্রতিটি turn-এ নতুন করে শুরু হয়, তাই পুরো কথোপকথনে সীমা থাকে না; (২) কোনো টুল অনুমোদনের অপেক্ষায় থাকলে সেই তথ্য হারিয়ে যায়। `result.conversation` রাখুন আর `conversation=` দিয়ে ফেরত দিন।

///

একটি ইতিহাস এর নিজের কথোপকথনের বাইরেও পৌঁছায় না। একটি এজেন্টকে সেই ধারাবাহিকতা দিতে গতকালের thread-গুলো replay করা কাজ করে — যতক্ষণ না আর করে: prompt সীমাহীনভাবে বাড়ে, প্রতিটি রিকোয়েস্ট এর দাম দেয়, আর [compaction](capabilities/compaction.md) সেই অংশগুলো ফেলে দেয় যার ওপর আপনি নির্ভর করছিলেন। [কথোপকথন জুড়ে মনে রাখা](#remembering-across-conversations) একটি ভিন্ন পদ্ধতি।

## ওই কোড নিজে না লেখা { #not-writing-that-code-yourself }

[`StepPersistence`](harness/step-persistence.md) এই ধরনটিকে একটি capability হিসেবে প্যাকেজ করে, যা আপনি একটি এজেন্টে যোগ করেন, তাই load আর save কল আপনাকে লিখতে হয় না। এটি in-memory, file, SQLite, PostgreSQL আর MongoDB backend-সহ আসে, আর এর store একটি protocol, যা আপনি নিজের ডেটাবেসের বিপরীতে বাস্তবায়ন করতে পারেন। এর snapshot শুধু বার্তা রাখে, `Conversation`-এর বহন করা usage আর বাকি থাকা deferred tool request নয়, তাই সেগুলো দরকার হলে `Conversation`-ও রাখুন।

এটি বার্তার চেয়ে বেশি লেখে: প্রতিটি সীমায় এজেন্ট কী করেছে তার একটি append-only event log, চালিয়ে যাওয়া যায় এমন snapshot যা থেকে আপনি একটি কথোপকথন আবার চালাতে বা fork করতে পারেন, আর একটি tool-effect খাতা যা লেখে প্রতিটি টুল কল শুরু হয়েছিল, ফেরত দিয়েছিল নাকি exception তুলেছিল। একটি crash-এর পর, যে কল কখনো শেষ হয়নি তার ফলাফল অজানা, আর যেটি exception তুলেছিল তারও হয়তো প্রভাব পড়েছে, তাই আবার চালানোর আগে বাইরের সিস্টেম যাচাই করুন।

[`ConversationSearch`](harness/conversation-search.md) নিজের কিছু না রেখে এর ওপর তৈরি হয়: এটি `StepPersistence`-এর আগেই লেখা ইতিহাসকে র‍্যাঙ্ক করে আর মডেলকে চাহিদামতো আগের turn প্রসঙ্গে ফিরিয়ে আনার একটি টুল দেয়, [compaction](capabilities/compaction.md)-এ বাদ পড়া turn-সহ। দুটিকে একটি store instance-এ জোড়া দিন, তাহলে স্মরণের জন্য কোনো বাড়তি লেখার পথ লাগে না।

## কথোপকথন জুড়ে মনে রাখা { #remembering-across-conversations }

ওপরের সব কিছু একটি কথোপকথনের পরিসরে। কথোপকথনের *মাঝে* একটি এজেন্ট কারো সম্পর্কে যা জানে — তাদের পছন্দ, গত সপ্তাহের একটি সিদ্ধান্ত, একটি সংশোধন যা তাদের বারবার বলতে হওয়া উচিত নয় — তার key আর আয়ু ভিন্ন।

[`Memory`](harness/memory.md) হলো এর জন্য capability। এটি এজেন্টকে Markdown ফাইলের একটি নোটবুক দেয়, যা এটি নিজের টুল দিয়ে লেখে, পড়ে আর খোঁজে, আর প্রতিটি রিকোয়েস্টে পুরো নোটবুকের বদলে একটি সীমিত অংশ বসায়। এর key হলো একটি namespace, যা আপনি আপনার [dependencies](dependencies.md) থেকে মীমাংসা করেন — সাধারণত একটি user বা tenant ID — `conversation_id` নয়, আর ঠিক এটাই একে thread-এর চেয়ে বেশি দিন টিকতে দেয়। এর store-গুলো টেকসই: একটি ফাইল ডিরেক্টরি, SQLite, PostgreSQL, বা আপনার নিজের ডেটাবেসের বিপরীতে বাস্তবায়ন করা একটি।

এটি নিজের একটি store-সহ নিজস্ব একটি capability থাকে, `StepPersistence` লেখে এমন কিছু নয়: একটি version-করা নোটবুক আর একটি append-only run log-এর মধ্যে মিল সামান্য। কিন্তু দুটি একই ডেটাবেস নেয়, তাই একটি এজেন্টের নোট এর কথোপকথনের পাশে রাখা মানে একটি সংযোগ আর backup নেওয়ার একটি জিনিস।

Anthropic API-র নিজের দিকে একটি memory টুল দেয়: [`MemoryTool`](native-tools.md#memory-tool) মডেলকে provider-এর সংজ্ঞায়িত একটি টুল চুক্তির মাধ্যমে memory ফাইলের একটি ডিরেক্টরি চালাতে দেয়, যার পেছনের storage তবুও আপনাকেই দিতে হয়।

/// note | Memory হলো মডেলের লেখা কনটেন্ট

একটি এজেন্টের নিজের জন্য রাখা নোট পরের prompt-এ আবার ঢোকে, আর একটি নোট ভুল হতে পারে বা এজেন্ট যার সাথে কথা বলছিল সে বসিয়ে দিতে পারে। `Memory` এগুলো instructions হিসেবে নয়, user-role কনটেন্ট হিসেবে বসায়, যা তাদের কর্তৃত্ব কমায়, কিন্তু সেটা prompt-injection-এর কোনো কঠিন সীমা নয়। capability-টির [security and provenance notes](harness/memory.md#security-and-provenance) এটি কী নিশ্চিত করে আর কী করে না তা আলোচনা করে।

///

## একটি provider-কে এটি রাখতে দেওয়া { #letting-a-provider-hold-it }

কিছু provider কথোপকথনের state নিজেদের দিকে রাখে আর তা থেকে আগের turn পুনর্গঠন করে, তাই প্রতিটি রিকোয়েস্ট শুধু নতুনটুকু বহন করে — OpenAI Responses API-তে সেটি হলো [`openai_conversation_id`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_conversation_id], যা [durable conversations](models/openai.md#using-durable-conversations)-এর নিচে আলোচিত।

এটিকে আপনার নিজের একটি store-এর সাথে তুলনা করে দেখুন: এটি একটি provider-এর সুবিধা, OpenAI নথিভুক্ত করে যে একটি শৃঙ্খলের আগের input token-এর জন্যও bill হয়, আর Zero Data Retention চালু থাকা প্রতিষ্ঠানের জন্য এটি অনুপলব্ধ।

## যা এখানে নেই { #what-isnt-here }

এখানের কিছুই একটি ধাপের মাঝখানে state-এর snapshot নেয় না, তাই একটি রানের ভেতরে "অর্ধেক-শেষ একটি রানের ধাপ 4-এ ফিরে গিয়ে সেখান থেকে replay" নেই। Snapshot নেওয়া হয় একটি রানের ভেতরে স্থির টুল-কল সীমায়, একটি node-এর মাঝে নয়। যে রানকে *চলার সময়* crash থেকে টিকতে হবে, তার জন্যই আছে [durable execution](durable_execution/overview.md)।

/// check | সংক্ষেপে মনে রাখুন

* chat thread রাখতে durable engine নয় — `result.conversation`-কে `ConversationTypeAdapter` দিয়ে একটি `jsonb` কলামে রাখুন, পরে `conversation=` দিয়ে দিন।
* শুধু বার্তা নয়, পুরো `Conversation` — এতে usage (বাজেটের জন্য) আর বাকি থাকা deferred কল থাকে।
* chat UI-এর ইতিহাস Pydantic AI-এর রূপে রাখুন, প্রান্তে রূপান্তর করুন; browser-এর ইতিহাস অবিশ্বস্ত।
* রানের log আর snapshot: `StepPersistence`; কথোপকথন-জুড়ে স্থায়ী জ্ঞান: `Memory` (user/tenant দিয়ে key করা)।
* চলমান রানকে crash থেকে বাঁচাতে: durable execution।

///
