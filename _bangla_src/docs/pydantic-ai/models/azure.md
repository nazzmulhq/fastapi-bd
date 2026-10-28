# Microsoft Azure / Foundry { #microsoft-azure-foundry }

/// note | এই পেজে যা শিখবেন

* Azure OpenAI আর Microsoft Foundry-র deployment Pydantic AI দিয়ে চালানো।
* `azure:` (Chat Completions) বনাম `azure-responses:` (Responses API)।
* পুরনো `api-version`-ভিত্তিক deployment, আর Foundry-তে Claude।

///

Pydantic AI Azure OpenAI আর Microsoft Foundry-র (আগে Azure AI Foundry) অন্য মডেল deployment সমর্থন করে, সাথে Anthropic SDK দিয়ে Claude।

| API | মডেল বাছাই |
| --- | --- |
| Chat Completions | `azure:<deployment-name>` |
| Responses | `azure-responses:<deployment-name>` |
| Anthropic Messages | [একটি Foundry client-সহ `AnthropicModel`](#claude-on-microsoft-foundry) |

মডেলের নাম হিসেবে আপনার Azure deployment-এর নাম ব্যবহার করুন। নিচের উদাহরণগুলো ধরে নেয় `gpt-5.2` নামের একটি deployment।

/// warning | সাধারণ ভুল

Azure-এ মডেলের নাম মানে আপনার দেওয়া **deployment-এর নাম**, OpenAI-এর মডেলের নাম নয়। আপনি `gpt-4o` মডেলটিকে `my-chat` নামে deploy করলে, `azure:my-chat` লিখতে হবে।

///

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

আপনার provider হিসেবে [Microsoft Foundry](https://ai.azure.com/) ব্যবহার করতে, `AZURE_OPENAI_ENDPOINT` এমন একটি URL-এ সেট করুন যার path `/v1`-এ শেষ হয় (যেমন `https://<resource>.openai.azure.com/openai/v1/` বা `https://<resource>.services.ai.azure.com/openai/v1/`), `AZURE_OPENAI_API_KEY` সেট করুন, আর নাম দিয়ে [`AzureProvider`][pydantic_ai.providers.azure.AzureProvider] ব্যবহার করুন:

```python
from pydantic_ai import Agent

agent = Agent('azure:gpt-5.2')
...
```

/// tip | পরামর্শ

কণ্ঠের এজেন্টের জন্য, বদলে একটি [realtime session](../realtime/azure.md)-সহ একটি Azure OpenAI realtime deployment বা Azure AI Voice Live ব্যবহার করুন।

///

অথবা সরাসরি মডেল আর provider তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

model = OpenAIChatModel(
    'gpt-5.2',
    provider=AzureProvider(
        azure_endpoint='https://your-resource.openai.azure.com/openai/v1/',
        api_key='your-api-key',
    ),
)
agent = Agent(model)
...
```

এটি লক্ষ্য করে [Azure OpenAI v1 API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle), যা Microsoft সব নতুন প্রজেক্টের জন্য পরামর্শ দেয়। এটি স্বাভাবিকভাবে Responses API-র সাথেও মেলে — দেখুন নিচের [Using Azure with the Responses API](#using-azure-with-the-responses-api)।

[`AzureProvider`][pydantic_ai.providers.azure.AzureProvider] `https://<model>.<region>.models.ai.azure.com`-এ [Microsoft Foundry serverless model deployment](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/concepts/endpoints)-ও চেনে আর একইভাবে সেগুলোতে সংযোগ করে।

## একটি বিদ্যমান `api-version`-ভিত্তিক deployment-এ সংযোগ { #connecting-to-an-existing-api-version-based-deployment }

আপনার resource এখনো তারিখযুক্ত `api-version` API ব্যবহার করলে, `api_version` দিন (বা `OPENAI_API_VERSION` environment variable সেট করুন) আর বদলে `azure_endpoint` resource-এর মূলে দেখান:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider

model = OpenAIChatModel(
    'gpt-5.2',
    provider=AzureProvider(
        azure_endpoint='https://your-resource.openai.azure.com/',
        api_version='2024-12-01-preview',
        api_key='your-api-key',
    ),
)
agent = Agent(model)
...
```

## Responses API-সহ Azure ব্যবহার { #using-azure-with-the-responses-api }

Microsoft Foundry [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] দিয়ে OpenAI Responses API-ও সমর্থন করে। ডকুমেন্ট ইনপুট ([`DocumentUrl`][pydantic_ai.DocumentUrl] আর [`BinaryContent`][pydantic_ai.BinaryContent]) নিয়ে কাজের সময় এটি বিশেষভাবে প্রস্তাবিত, কারণ Azure-এর Chat Completions API এই ইনপুট টাইপগুলো সমর্থন করে না।

নাম দিয়ে Responses API বাছতে `azure-responses:` উপসর্গ ব্যবহার করুন (`azure:` উপসর্গ Chat Completions API ব্যবহার করে):

```python
from pydantic_ai import Agent

agent = Agent('azure-responses:gpt-5.2')
...
```

/// note | মনে রাখুন

Azure-এর Responses API এখনো OpenAI-এর Responses API-র প্রতিটি সুবিধা সমর্থন করে না — যেমন, নেটিভ web search পাওয়া যায় না, আর ছবি সম্পাদনা ও ফাইল আপলোডে সীমা আছে। বর্তমান তালিকার জন্য দেখুন [Microsoft-এর Responses API ডক](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses)। এটি প্রযোজ্য আপনি `azure-responses:` সংক্ষিপ্ত রূপ ব্যবহার করুন বা সরাসরি `AzureProvider`-সহ `OpenAIResponsesModel` তৈরি করুন।

///

অথবা সরাসরি মডেল আর provider তৈরি করুন, যেমন একটি ডকুমেন্ট প্রক্রিয়া করতে:

/// details | Responses API দিয়ে Azure-এ ডকুমেন্ট প্রক্রিয়াকরণ
    type: tip

```python
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.azure import AzureProvider

pdf_bytes = b'%PDF-1.4 ...'  # Your PDF content

model = OpenAIResponsesModel(
    'gpt-5.2',
    provider=AzureProvider(
        azure_endpoint='https://your-resource.openai.azure.com/openai/v1/',
        api_key='your-api-key',
    ),
)
agent = Agent(model)
result = agent.run_sync([
    'Summarize this document',
    BinaryContent(data=pdf_bytes, media_type='application/pdf'),
])
```

///

## Microsoft Foundry-তে Claude { #claude-on-microsoft-foundry }

Claude-এর জন্য, `anthropic` ঐচ্ছিক group ইনস্টল করুন আর [`AnthropicProvider`][pydantic_ai.providers.anthropic.AnthropicProvider]-এ একটি `AsyncAnthropicFoundry` client দিন। উদাহরণ আর Entra ID প্রমাণীকরণের নির্দেশনার জন্য দেখুন [Claude on Microsoft Foundry](anthropic.md#microsoft-foundry)।

/// check | সংক্ষেপে মনে রাখুন

* `AZURE_OPENAI_ENDPOINT` (`/v1`-এ শেষ) আর `AZURE_OPENAI_API_KEY` সেট, তারপর `Agent('azure:<deployment-name>')`।
* ডকুমেন্ট ইনপুটে `azure-responses:` (Responses API)।
* পুরনো resource-এ `api_version` দিন; Claude-এ `AsyncAnthropicFoundry`।

///
