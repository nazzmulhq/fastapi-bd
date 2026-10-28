# File Understanding { #file-understanding }

/// note | এই পেজে যা শিখবেন

* `FileUnderstanding` দিয়ে এজেন্টকে এমন ছবি, ডকুমেন্ট, অডিও আর ভিডিও "পড়াতে" দেওয়া, যা এর মডেল নিজে পড়তে পারে না।
* কোন ফাইল বর্ণনা করতে হবে তা model profile থেকে কীভাবে ঠিক হয়।
* বর্ণনা কীভাবে message history-তে সংরক্ষিত হয় (প্রতি কথোপকথনে একবার), আর usage-সীমা।

///

[`FileUnderstanding`][pydantic_ai.capabilities.FileUnderstanding] [capability](overview.md) একটি এজেন্টকে এমন ছবি, ডকুমেন্ট, অডিও আর ভিডিও নিতে দেয় যা এর মডেল পড়তে পারে না। প্রতিটি রিকোয়েস্টের আগে, একটি user prompt বা একটি টুলের ফলে এমন প্রতিটি ফাইল এর একটি লেখা বর্ণনা দিয়ে বদলানো হয়, যা লিখেছে এমন একটি মডেল যে এটি পড়তে পারে। এজেন্টের মডেল ফাইলের জায়গায় বর্ণনাটি দেখে, আর যে ফাইল এটি গ্রহণ করে সেগুলো যেমন আছে তেমন পাঠানো হয়। capability ছাড়া, মডেল পড়তে পারে না এমন একটি টুলের ফেরত দেওয়া ফাইল [একটি নোট দিয়ে বদলানো হয়](../tools-advanced.md#tool-return-file-provenance) যা তা বলে, আর একটি user prompt-এর একটি রিকোয়েস্ট ব্যর্থ করে।

```python title="file_understanding_capability.py"
from pydantic_ai import Agent, DocumentUrl
from pydantic_ai.capabilities import FileUnderstanding

agent = Agent(
    'typesafe:jev-latest',
    output_type=bool,
    instructions='Is this document about animals?',
    capabilities=[FileUnderstanding(fallback_subagent_model='openai:gpt-6.1-sol')],
)
result = agent.run_sync([DocumentUrl('https://example.com/field-guide.pdf')])
print(result.output)
#> True
```

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন আপনার এজেন্টের মডেল শুধু লেখা পড়তে পারে, কিন্তু ব্যবহারকারী একটি মিটিংয়ের অডিও রেকর্ডিং পাঠাল। `FileUnderstanding` একজন অনুবাদকের মতো কাজ করে: একটি অডিও-বোঝা মডেলকে (যেমন Gemini) দিয়ে রেকর্ডিংয়ের বিস্তারিত লিখিত বর্ণনা বানায়, তারপর আপনার এজেন্টের মডেলকে অডিওর বদলে সেই লেখাটা দেয়। এজেন্টের মডেল মনে করে সে যেন অডিওটাই "শুনেছে"।

///

কোন ফাইলের বর্ণনা লাগে তা আসে মডেলের [profile](../models/overview.md#inspecting-a-models-profile) থেকে: [`supports_image_input`][pydantic_ai.profiles.ModelProfile.supports_image_input], [`supports_document_input`][pydantic_ai.profiles.ModelProfile.supports_document_input], [`supported_document_media_types`][pydantic_ai.profiles.ModelProfile.supported_document_media_types], [`supports_audio_file_input`][pydantic_ai.profiles.ModelProfile.supports_audio_file_input] আর [`supports_video_input`][pydantic_ai.profiles.ModelProfile.supports_video_input]। বেশিরভাগ মডেল ছবি আর ডকুমেন্ট গ্রহণ করে, তাই এদের সাথে capability মূলত অডিও আর ভিডিওর বর্ণনা করায়; [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel]-এ Word আর Excel ডকুমেন্টও। [Jev](../models/typesafe.md)-এর মতো একটি শুধু-লেখা মডেলের সবকিছুর বর্ণনা হয়।

একটি flag `True` যদি না একটি adapter বা একটি মডেল পরিবার সেই ধরনের ফাইল নেয় না বলে জানা থাকে, তাই এটি মডেল এটি পড়ে কিনা তার যাচাই নয়। ছবি পাঠায় এমন একটি adapter দিয়ে পরিবেশিত একটি শুধু-লেখা মডেল, যেমন vLLM-এর পেছনে একটি শুধু-লেখা Llama, এর profile-কে তা বলতে হবে, নইলে এর ছবি পাঠানো হয় আর provider সেগুলো প্রত্যাখ্যান করে:

```python title="file_understanding_text_only_profile.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import FileUnderstanding
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles import ModelProfile
from pydantic_ai.providers.vllm import VLLMProvider

model = OpenAIChatModel(
    'meta-llama/Llama-3.3-70B-Instruct',
    provider=VLLMProvider(base_url='http://localhost:8000/v1'),
    profile=ModelProfile(supports_image_input=False, supports_document_input=False),
)
agent = Agent(model, capabilities=[FileUnderstanding(fallback_subagent_model='openai:gpt-6.1-sol')])
```

`fallback_subagent_model` হলো সেই মডেল যা বর্ণনা লেখে, একটি `'provider:model'` নাম বা একটি [`Model`][pydantic_ai.models.Model] instance হিসেবে, আর এটিকে নিজে ফাইলগুলো গ্রহণ করতে হবে। `instructions` একটি বিস্তারিত বর্ণনার ডিফল্ট অনুরোধ বদলায়:

```python title="file_understanding_instructions.py"
from pydantic_ai.capabilities import FileUnderstanding

FileUnderstanding(
    fallback_subagent_model='anthropic:claude-sonnet-5-5',
    instructions='Transcribe the text in this file. Keep headings and tables.',
)
```

বর্ণনাটি মডেলে পৌঁছায় ফাইলের নাম দেওয়া `-----BEGIN FILE-----` আর `-----END FILE-----` লাইনের মাঝে, ঠিক যেভাবে attachment নেয় না এমন মডেলের জন্য text ফাইল inline করা হয়। একটি বর্ণনা গদ্য, তাই ফাইল যা-ই হোক এর ব্লক `text/plain` চিহ্নিত; একটি লেখার-মতো ডকুমেন্টের (plain text, CSV, JSON, XML, YAML) বর্ণনা লাগে না, যেমন আছে তেমন inline হয়, আর এর নিজের media type রাখে। একটি provider ফাইল রেফারেন্স ([`UploadedFile`][pydantic_ai.messages.UploadedFile]) ছেড়ে দেওয়া হয়, কারণ শুধু এর নিজের provider এটি পড়তে পারে।

একটি ফাইলের বর্ণনা প্রতি কথোপকথনে একবার হয়। বর্ণনাটি message history-তে লেখা হয়, যে রিকোয়েস্টে ফাইলটি আছে তার [`metadata`][pydantic_ai.messages.ModelRequest.metadata]-এ framework-এর সংরক্ষিত `__pydantic_ai__` namespace-এর নিচে (যা মডেলে পাঠানো হয় না), আর পরের প্রতিটি রিকোয়েস্ট ফাইলটি আবার বর্ণনা না করে সেই লেখা ব্যবহার করে। `message_history` থেকে চালিয়ে যাওয়া একটি turn, পরের turn পরিবেশন করা আরেকটি worker, আর এর ইতিহাস replay করা একটি [durable](../durable_execution/overview.md) রান — সবাই একই বর্ণনা পড়ে। তাই আগের রিকোয়েস্ট এক রিকোয়েস্ট থেকে পরেরটিতে একই কনটেন্ট রাখে, যা prompt cache বৈধ রাখে, আর বর্ণনাকারীর জন্য একবারই টাকা দিতে হয়। URL দিয়ে দেওয়া একটি ফাইল এর URL দিয়ে চিহ্নিত হয়, আর binary কনটেন্ট এর bytes আর media type দিয়ে। URL দিয়ে দেওয়া একটি text ডকুমেন্টের ডাউনলোড করা লেখাও একইভাবে লেখা হয়, তাই এটি আবার ডাউনলোড হয় না। একটি আলাদা কথোপকথন ফাইলটি আবার বর্ণনা করে। [UI adapters](../ui/overview.md) একটি client-কে পাঠানো ইতিহাস থেকে সেই namespace বাদ রাখে, আর [`sanitize_messages`][pydantic_ai.messages.sanitize_messages] একটি client-এর ফেরত পাঠানো [untrusted history](../message-history.md#loading-untrusted-history) থেকে এটি বাদ দেয়, তাই যে কথোপকথনের ইতিহাস client-এ থাকে সেখানে প্রতিটি turn-এ ফাইলটি আবার বর্ণনা হয়, আর একটি নতুন বর্ণনা ভিন্ন হতে পারে, যা আগের রিকোয়েস্ট বদলায় আর cache করা prefix-এর মূল্য নেয়।

/// warning | সাধারণ ভুল

একটি chat UI-তে, যেখানে পুরো ইতিহাস browser-এ থাকে আর প্রতি turn-এ ফেরত আসে, `FileUnderstanding` ব্যবহার করে ভাবা যে একটি বড় ভিডিওর বর্ণনা একবারই হবে। নিরাপত্তার কারণে client থেকে আসা ইতিহাসের `__pydantic_ai__` metadata বাদ পড়ে, তাই প্রতিটি turn-এ ভিডিওটি আবার বর্ণনা হয় — খরচ বারবার। ইতিহাস সার্ভারে রাখুন ([Persistence](../persistence.md) দেখুন)।

///

একটি রিকোয়েস্টের যে ফাইলগুলোর বর্ণনা লাগে সেগুলো একসাথে বর্ণনা হয়, প্রতিটি একবার, যতবারই দেখা দিক। একটি ফাইল বর্ণনা করা নিজস্ব একটি মডেল রান, কিন্তু এর রিকোয়েস্ট, token আর খরচ এজেন্ট রানের [usage][pydantic_ai.usage.RunUsage]-এ যোগ হয়, আর কোনো বর্ণনা-রিকোয়েস্ট পাঠানোর আগে রানের [usage limits][pydantic_ai.usage.UsageLimits] যাচাই হয়, যেন সেগুলো রানের পরের রিকোয়েস্ট: একটি `request_limit` এগুলোকে এজেন্টের নিজেরগুলোর সাথে একসাথে সীমিত করে।

একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর কোনো একক profile নেই, তাই capability এর ফাইলগুলো ছেড়ে দেয়, আর এটি যে প্রতিটি মডেল চেষ্টা করে তাকে সেই মডেল পড়তে পারে না এমন একটি টুলের ফাইলের জায়গায় একটি নোট পাঠানো হয়। ফাইলের বর্ণনা লাগলে একটি একক মডেলসহ capability ব্যবহার করুন।

/// check | সংক্ষেপে মনে রাখুন

* `FileUnderstanding(fallback_subagent_model='...')` — মডেল যে ফাইল পড়তে পারে না তার লেখা বর্ণনা আরেকটি মডেল দিয়ে বানিয়ে দেয়।
* কী বর্ণনা লাগবে তা model profile-এর `supports_*_input` flag থেকে; ভুল flag হলে profile ঠিক করুন।
* বর্ণনা প্রতি কথোপকথনে একবার, message history-র metadata-য় সংরক্ষিত — cache আর খরচ বাঁচে।
* client-এ রাখা ইতিহাসে বর্ণনা প্রতি turn-এ আবার হয়।
* বর্ণনার খরচ রানের usage-এ যোগ হয়; `FallbackModel`-এ capability কাজ করে না।

///
