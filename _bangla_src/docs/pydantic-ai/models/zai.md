# Z.AI { #zai }

/// note | এই পেজে যা শিখবেন

* Z.AI (Zhipu AI)-র GLM মডেল `ZaiModel` দিয়ে ব্যবহার।
* Thinking mode, আগের দফার thinking রাখা, আর নিজের provider/base URL।

///

## ইনস্টল { #install }

[`ZaiModel`][pydantic_ai.models.zai.ZaiModel] ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `zai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[zai]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[zai]"
```

///


## কনফিগারেশন { #configuration }

API দিয়ে [Z.AI](https://z.ai/) (Zhipu AI) ব্যবহার করতে, [z.ai](https://z.ai/manage-apikey/apikey-list)-এ গিয়ে একটি API key তৈরি করুন।

উপলব্ধ মডেলের তালিকার জন্য দেখুন [Z.AI ডকুমেন্টেশন](https://docs.z.ai/)।

## Environment variable { #environment-variable }

API key পাওয়ার পরে, এটি একটি environment variable হিসেবে সেট করতে পারেন:

```bash
export ZAI_API_KEY='your-api-key'
```

তারপর নাম দিয়ে [`ZaiModel`][pydantic_ai.models.zai.ZaiModel] ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('zai:glm-5')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.zai import ZaiModel

model = ZaiModel('glm-5')
agent = Agent(model)
...
```

## Thinking mode { #thinking-mode }

Z.AI-এর `glm-5.3`, `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`, `glm-4.6` (hybrid thinking) আর `glm-4.5` (interleaved thinking) মডেল thinking/reasoning mode সমর্থন করে, যেখানে মডেল চূড়ান্ত উত্তরের আগে reasoning বিষয়বস্তু তৈরি করে। এর মধ্যে আছে `glm-4.6v` আর `glm-4.5v` vision মডেল। একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং দিয়ে এটি কনফিগার করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

agent = Agent(
    'zai:glm-5',
    model_settings=ModelSettings(thinking=True),
)
...
```

`thinking=True` thinking চালু করে আর `thinking=False` বন্ধ করে (GLM-5.3 ছাড়া, যা সবসময় reasoning করে, তাই `thinking=False` এর সর্বনিম্ন effort `low`-এ thinking চালু রাখে)। GLM-5.2 আর GLM-5.3-এ, একটি স্পষ্ট effort স্তর (`'minimal'`/`'low'`/`'medium'`/`'high'`/`'xhigh'`/`'max'`) Z.AI-তে `reasoning_effort` হিসেবে পাঠানো হয়; GLM-5.3 শুধু `low`/`high`/`max` নেয়, তাই অন্য স্তরগুলো সবচেয়ে কাছেরটিতে ম্যাপ হয় (`minimal` থেকে `low`, `medium` থেকে `high`, আর `xhigh` থেকে `max`)। অন্য GLM মডেলে, যা effort-এর সূক্ষ্মতা দেয় না, সব effort স্তর চালু-তে মিলে যায়। প্রতিটি মডেলের ডিফল্ট আচরণ ব্যবহার করতে ফিল্ডটি বাদ দিন।

### রক্ষিত thinking { #preserved-thinking }

thinking-সক্ষম মডেলে, আগের assistant উত্তরের reasoning বিষয়বস্তু **ডিফল্টভাবে রক্ষিত** থাকে — কোনো কনফিগারেশন লাগে না — বহু-দফায় ভালো সুসংগতি আর অন্য provider-এর সাথে সামঞ্জস্যের জন্য। আগের দফার সম্পূর্ণ, অপরিবর্তিত `reasoning_content` Pydantic AI নিজে থেকে API-তে ফেরত পাঠায়।

বদলে প্রতিটি দফা নতুন করে শুরু করতে চাইলে, Z.AI-নির্দিষ্ট [`ZaiModelSettings`][pydantic_ai.models.zai.ZaiModelSettings]-এ `zai_clear_thinking=True` দিয়ে এটি **বন্ধ** করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.zai import ZaiModelSettings

agent = Agent(
    'zai:glm-5',
    # Opt out of the default preserved thinking:
    model_settings=ZaiModelSettings(thinking=True, zai_clear_thinking=True),
)
...
```

আরও বিস্তারিত জানতে দেখুন [Z.AI thinking mode ডকুমেন্টেশন](https://docs.z.ai/guides/capabilities/thinking-mode#preserved-thinking)।

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের [`Provider`][pydantic_ai.providers.Provider] দিতে পারেন। সবচেয়ে সরল ক্ষেত্রে, শুধু একটি API key-সহ [`ZaiProvider`][pydantic_ai.providers.zai.ZaiProvider] দিন। ভেতরের `httpx2.AsyncClient`-ও নিজের মতো করতে চাইলে, provider তৈরির সময় এটি দিন:

```python
from httpx2 import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.zai import ZaiModel
from pydantic_ai.providers.zai import ZaiProvider

custom_http_client = AsyncClient(timeout=30)
model = ZaiModel(
    'glm-5',
    provider=ZaiProvider(api_key='your-api-key', http_client=custom_http_client),
)
agent = Agent(model)
...
```

নিজের HTTP client না লাগলে, `http_client=custom_http_client` আর্গুমেন্ট বাদ দিন।

### নিজের base URL { #custom-base-url }

`ZaiProvider` ডিফল্টভাবে আন্তর্জাতিক সাধারণ API endpoint `https://api.z.ai/api/paas/v4` ব্যবহার করে। একটি ভিন্ন endpoint ব্যবহার করতে, যেমন [GLM Coding Plan](https://docs.z.ai/devpack/overview)-এরটি বা চীনমুখী `https://open.bigmodel.cn/api/paas/v4`, একটি নিজের `base_url` দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.zai import ZaiModel
from pydantic_ai.providers.zai import ZaiProvider

model = ZaiModel(
    'glm-5',
    provider=ZaiProvider(
        api_key='your-api-key',
        base_url='https://api.z.ai/api/coding/paas/v4',  # GLM Coding Plan
    ),
)
agent = Agent(model)
...
```

/// check | সংক্ষেপে মনে রাখুন

* `pip install "pydantic-ai-slim[zai]"`, `ZAI_API_KEY`, তারপর `Agent('zai:glm-5.2')`।
* `thinking=` দিয়ে reasoning; আগের thinking ডিফল্টভাবে রাখা হয় (`zai_clear_thinking=True` দিয়ে বন্ধ)।
* Coding Plan বা চীনা endpoint-এ `ZaiProvider(base_url=...)`।

///
