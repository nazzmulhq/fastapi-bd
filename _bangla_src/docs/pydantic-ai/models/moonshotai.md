# Moonshot AI / Kimi { #moonshot-ai-kimi }

/// note | এই পেজে যা শিখবেন

* `moonshotai:` উপসর্গ দিয়ে Kimi মডেল ব্যবহার, চীনা endpoint-সহ।
* Kimi-র thinking কীভাবে একীভূত `thinking` সেটিংয়ে ম্যাপ হয়।

///

[`MoonshotAIProvider`][pydantic_ai.providers.moonshotai.MoonshotAIProvider] আর OpenAI-সামঞ্জস্যপূর্ণ Chat Completions API দিয়ে Moonshot AI-এর Kimi মডেল ব্যবহার করুন। provider উপসর্গ `moonshotai:`।

[Kimi K3.1 Pro API guide](https://platform.kimi.ai/docs/guide/kimi-k3-1-pro-quickstart)
`kimi-k3.1-pro` আর `kimi-k3.1-pro-highspeed` ঢাকে।
একটি নথিভুক্ত reasoning effort বাছতে `thinking='low'`, `thinking='high'`, বা `thinking='max'` ব্যবহার করুন,
বা provider-এর ডিফল্ট ব্যবহারে `thinking` বাদ দিন।

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

[Moonshot Console](https://platform.moonshot.ai/console)-এ একটি API key তৈরি করুন।

`MOONSHOTAI_API_KEY` environment variable সেট করে নাম দিয়ে [`MoonshotAIProvider`][pydantic_ai.providers.moonshotai.MoonshotAIProvider] ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('moonshotai:kimi-k3.1-pro')
...
```

অথবা সরাসরি মডেল আর provider তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.moonshotai import MoonshotAIProvider

model = OpenAIChatModel(
    'kimi-k3.1-pro',
    provider=MoonshotAIProvider(api_key='your-moonshot-api-key'),
)
agent = Agent(model)
...
```

### নিজের base URL { #custom-base-url }

`MoonshotAIProvider` ডিফল্টভাবে `https://api.moonshot.ai/v1` ব্যবহার করে। চীনা endpoint ব্যবহার করতে,
`MOONSHOTAI_BASE_URL` আর [চীনা console](https://platform.kimi.com/console/api-keys) থেকে একটি API key সেট করুন:

```bash
export MOONSHOTAI_API_KEY="your-moonshot-api-key"
export MOONSHOTAI_BASE_URL="https://api.moonshot.cn/v1"
```

তারপর ওপরে দেখানো মডেল-স্ট্রিং কনফিগারেশন ব্যবহার করতে পারেন।

বিকল্পভাবে, [`MoonshotAIProvider`][pydantic_ai.providers.moonshotai.MoonshotAIProvider]-এ
`base_url='https://api.moonshot.cn/v1'` দিন।
একটি স্পষ্ট `base_url` `MOONSHOTAI_BASE_URL` override করে।

## Thinking { #thinking }

Kimi K2.5, K2.6, K2.7 Code আর K3 ডিফল্টভাবে reasoning করে। একীভূত [`thinking`](../capabilities/thinking.md) সেটিং Moonshot-এর রিকোয়েস্ট ফিল্ডে এভাবে ম্যাপ হয়:

- `thinking=False` Kimi K2.5 আর K2.6-এ `thinking={'type': 'disabled'}` পাঠিয়ে thinking বন্ধ করে। Kimi K3 thinking বন্ধ করতে পারে না, তাই এটি তার সর্বনিম্ন effort-এ reasoning করে, `reasoning_effort='low'`। Kimi K2.7 Code-ও thinking বন্ধ করতে পারে না আর এর কোনো effort সেটিং নেই, তাই `thinking=False` কিছুই পাঠায় না।
- `thinking=True` আর effort স্তরগুলো `reasoning_effort` হিসেবে পাঠানো হয় (`True` হিসেবে `'medium'`)। `'max'` পাঠানো হয় Kimi K3, K2.6 আর K2.7-এ `'max'` হিসেবে, আর অন্য Kimi মডেলে `'xhigh'` হিসেবে।

/// check | সংক্ষেপে মনে রাখুন

* `MOONSHOTAI_API_KEY` সেট, তারপর `Agent('moonshotai:<kimi-model>')`।
* চীনা endpoint-এ `MOONSHOTAI_BASE_URL` বা `base_url=`।
* `thinking=False` সব Kimi মডেলে thinking বন্ধ করে না; মডেলভেদে আচরণ আলাদা।

///
