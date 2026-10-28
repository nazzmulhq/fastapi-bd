# Meta { #meta }

/// note | এই পেজে যা শিখবেন

* Meta-র Muse মডেল `meta:` উপসর্গ আর Responses API দিয়ে ব্যবহার।
* Reasoning effort, tool choice-এর সীমা আর web search।

///

[`MetaProvider`][pydantic_ai.providers.meta.MetaProvider] আর [Meta Model API](https://dev.meta.ai/docs) দিয়ে Meta-র Muse মডেল ব্যবহার করুন। provider উপসর্গ `meta:`, আর এটি OpenAI-সামঞ্জস্যপূর্ণ Responses API ব্যবহার করে।

## ইনস্টল { #install }

এই সংযোগে ব্যবহৃত OpenAI SDK-সহ Pydantic AI ইনস্টল করুন:

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


## কনফিগারেশন { #configuration }

[Meta developer platform](https://dev.meta.ai)-এ একটি API key তৈরি করুন।

`META_API_KEY` environment variable সেট করে নাম দিয়ে [`MetaProvider`][pydantic_ai.providers.meta.MetaProvider] ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('meta:muse-spark-1.3')
...
```

অথবা সরাসরি মডেল আর provider তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.meta import MetaProvider

model = OpenAIResponsesModel(
    'muse-spark-1.3',
    provider=MetaProvider(api_key='your-meta-api-key'),
)
agent = Agent(model)
...
```

Contributor mode মডেল (`muse-spark-1.3-contributor`, `muse-spark-1.2-contributor`) নিজস্ব [দাম](https://dev.meta.ai/docs/pricing-rate-limits)-সহ আলাদা মডেলের নাম।

## Responses আর Chat Completions { #responses-and-chat-completions }

`meta:` উপসর্গ [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] ব্যবহার করে। Muse একটি টুল কলের আগে যে অগ্রগতির হালনাগাদ লেখে তা `commentary` লেবেল দেয়, আর Pydantic AI পরের রিকোয়েস্টে সেই লেবেল আর Muse-এর এনক্রিপ্ট করা reasoning ফেরত পাঠায়, যা দীর্ঘ টুল-কল করা রানকে একটি অগ্রগতির হালনাগাদে শেষ হওয়া থেকে রক্ষা করে।

Meta Chat Completions API-ও দেয়, যা একই provider-সহ [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] দিয়ে ব্যবহার করতে পারেন। এটি reasoning ফেরত দেয় না (usage-এ শুধু একটি `reasoning_tokens` সংখ্যা), তাই আপনি [thinking](../capabilities/thinking.md) অংশ পাবেন না।

## Reasoning { #reasoning }

Muse মডেল সবসময় reasoning করে: Meta `reasoning_effort='none'` প্রত্যাখ্যান করে, তাই `thinking=False` সর্বনিম্ন effort পাঠায়, `'minimal'`। `'minimal'` থেকে `'max'` পর্যন্ত effort `openai_reasoning_effort` দিয়ে সমর্থিত। একীভূত `thinking` সেটিং একই পরিসর ঢাকে, শুধু `'max'` পাঠানো হয় `'xhigh'` হিসেবে। Meta reasoning-এর সারাংশ stream করে শুধু আপনি চাইলে:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModelSettings

agent = Agent(
    'meta:muse-spark-1.3',
    model_settings=OpenAIResponsesModelSettings(openai_reasoning_effort='high', openai_reasoning_summary='auto'),
)
...
```

OpenAI-এর reasoning মডেলের মতো নয়, Muse reasoning-এর সময় `temperature` আর `top_p` নেয়, তাই সেগুলো যেমন কনফিগার করা তেমন পাঠানো হয়।

## Tool choice { #tool-choice }

Meta শুধু `tool_choice='auto'` নেয়। Pydantic AI নিজে একটি টুল বাধ্য করতে গেলে, যেমন একটি [আউটপুট টুল](../output.md#tool-output), এটি `'auto'`-তে ফিরে যায়। একটি স্পষ্ট বাধ্য-করা `tool_choice` (`'required'` বা নির্দিষ্ট টুল) একটি `UserError` তোলে, আর `tool_choice='none'` API প্রত্যাখ্যান করে: এটি `'none'` হিসেবে পাঠানো হয়, বা Responses API-র কিছু থাকলে আউটপুট টুলে একটি `allowed_tools` সীমা হিসেবে, আর API শুধু `'auto'` নেয়।

## Web search { #web-search }

Muse [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] সমর্থন করে, token usage-এর ওপরে প্রতি সার্চে বিল করা।

/// check | সংক্ষেপে মনে রাখুন

* `META_API_KEY` সেট, তারপর `Agent('meta:<muse-model>')` (Responses API)।
* Muse সবসময় reasoning করে; `thinking=False` মানে `'minimal'`।
* শুধু `tool_choice='auto'`; স্পষ্ট `'required'` এরর দেয়।

///
