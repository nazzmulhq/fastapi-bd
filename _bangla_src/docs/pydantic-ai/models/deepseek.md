# DeepSeek { #deepseek }

/// note | এই পেজে যা শিখবেন

* DeepSeek-এর Chat Completions (`deepseek:`) আর Responses API ব্যবহার।
* thinking চালু থাকলে structured output কেন অনির্ভরযোগ্য, আর কীভাবে ঠিক করবেন।
* DeepSeek-এর Responses API-তে কোন সুবিধা নিঃশব্দে কাজ করে না।

///

DeepSeek-কে তার Chat Completions বা Responses API দিয়ে ব্যবহার করুন। `deepseek:` উপসর্গ Chat Completions বাছে; Responses-এর জন্য স্পষ্টভাবে [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] ব্যবহার করুন।

বর্তমান Flash মডেলের জন্য `deepseek-flash` ব্যবহার করুন। DeepSeek পুরনো `deepseek-v4-flash` নামও নেয় আর [বর্তমান Flash মডেল দিয়ে তা দেয়](https://api-docs.deepseek.com/quick_start/pricing/)।

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

[DeepSeek](https://deepseek.com) provider ব্যবহার করতে, প্রথমে [Quick Start guide](https://api-docs.deepseek.com/) অনুসরণ করে একটি API key তৈরি করুন।

তারপর `DEEPSEEK_API_KEY` environment variable সেট করে নাম দিয়ে [`DeepSeekProvider`][pydantic_ai.providers.deepseek.DeepSeekProvider] ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('deepseek:deepseek-flash')
...
```

অথবা সরাসরি মডেল আর provider তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

model = OpenAIChatModel(
    'deepseek-flash',
    provider=DeepSeekProvider(api_key='your-deepseek-api-key'),
)
agent = Agent(model)
...
```

HTTP client নিজের মতো করতে পারেন:

```python
from httpx2 import AsyncClient

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

custom_http_client = AsyncClient(timeout=30)
model = OpenAIChatModel(
    'deepseek-flash',
    provider=DeepSeekProvider(
        api_key='your-deepseek-api-key', http_client=custom_http_client
    ),
)
agent = Agent(model)
...
```

Pydantic AI v2-এর সময় OpenAI-সামঞ্জস্যপূর্ণ provider একটি পুরনো `httpx.AsyncClient`-ও নেয়, তবে একটি deprecation সতর্কবার্তা দেয়। নতুন কোডে `httpx2.AsyncClient` ব্যবহার করুন; পুরনো HTTPX client-এর সমর্থন Pydantic AI v3-এ সরিয়ে ফেলা হবে।

## Structured output আর thinking { #structured-output-and-thinking }

`deepseek-flash` আর DeepSeek-এর V4 মডেল ডিফল্টভাবে thinking করে, আর thinking চালু থাকা অবস্থায় DeepSeek একটি বাধ্য টুল বাছাই প্রত্যাখ্যান করে, উত্তর দিয়ে `Thinking mode does not support this tool_choice`। তাই Pydantic AI সেই রিকোয়েস্টে `tool_choice='auto'` পাঠায়, যা মডেলকে আউটপুট টুল না ডেকে গদ্যে উত্তর দেওয়ার স্বাধীনতা দেয় — `deepseek-v4-pro`-তে এতে প্রায়ই এত retry লাগে যে retry বাজেট শেষ হয়ে যায়। নির্ভরযোগ্য [structured output](../output.md) দরকার হলে thinking বন্ধ করুন, তাহলে আবার বাধ্য করা ব্যবহার হয়:

```python
from pydantic import BaseModel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings


class Answer(BaseModel):
    text: str


agent = Agent(
    OpenAIChatModel('deepseek-v4-pro', provider='deepseek'),
    output_type=Answer,
    model_settings=OpenAIChatModelSettings(thinking=False),
)
...
```

thinking চালু থাকা অবস্থায় স্পষ্টভাবে `tool_choice='required'` দিলে API-তে ব্যর্থ না হয়ে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

DeepSeek একটি thinking রিকোয়েস্টও প্রত্যাখ্যান করে যখন শেষ user বার্তার পরে একটি টুল-কল করা assistant দফায় `reasoning_content` নেই, যেমন আরেকটি মডেলের দেওয়া বা thinking বন্ধ থাকা একটি। রিকোয়েস্ট thinking করলেই, [`DeepSeekProvider`][pydantic_ai.providers.deepseek.DeepSeekProvider] এটি নেই এমন প্রতিটি টুল-কল করা দফায় ফিল্ডটি খালি পাঠায়। আরেকটি endpoint থেকে DeepSeek-এর Chat Completions আকার দিলে, আপনার নিজের profile-এ `openai_chat_send_back_thinking_parts='field'` আর `openai_chat_thinking_field='reasoning_content'`-এর পাশাপাশি [`OpenAIModelProfile.openai_chat_thinking_requires_field_on_tool_calls`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_chat_thinking_requires_field_on_tool_calls] সেট করুন।

## Responses API { #responses-api }

ওপরে দেখানো Chat Completions API-র বিকল্প হিসেবে, DeepSeek [দুই V4 মডেলের জন্য](https://api-docs.deepseek.com/guides/responses_api) একটি OpenAI-সামঞ্জস্যপূর্ণ [Responses API](openai.md#responses-api-features)-ও দেয়। [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel]-কে [`DeepSeekProvider`][pydantic_ai.providers.deepseek.DeepSeekProvider]-এর সাথে জুড়ে এটি ব্যবহার করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.deepseek import DeepSeekProvider

model = OpenAIResponsesModel(
    'deepseek-flash',
    provider=DeepSeekProvider(api_key='your-deepseek-api-key'),
)
agent = Agent(model)
...
```

DeepSeek Responses API-র কোন অংশ বাস্তবায়ন করে তা [নথিভুক্ত করে](https://api-docs.deepseek.com/guides/responses_api), আর অসমর্থিত ফিল্ড প্রত্যাখ্যাত না হয়ে নিঃশব্দে উপেক্ষিত হয়, তাই কী কিছুই করে না তা জানা ভালো:

- API stateless, তাই [`openai_conversation_id`](openai.md#using-durable-conversations), [background mode](openai.md#background-mode) আর [message compaction](openai.md#message-compaction) পাওয়া যায় না। বদলে প্রতিটি রানে [বার্তার ইতিহাস](../message-history.md) ফেরত দিন।
- [`openai_previous_response_id`](openai.md#referencing-earlier-responses) সেট করবেন না। এটি সেট করলে Pydantic AI সেই আগের দফাগুলো বাদ দেয় যা সার্ভার রাখছে বলে ধরে নেয়, আর DeepSeek কিছুই রাখে না, তাই মডেল এরর না দিয়ে নিঃশব্দে কথোপকথন হারিয়ে ফেলে।
- [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] `deepseek-v4-pro`-তে কাজ করে আর `deepseek-flash`-এ উপেক্ষিত হয়। DeepSeek অন্য [নেটিভ টুল](../native-tools.md) এরর না জানিয়ে উপেক্ষা করে।
- ছবি আর ডকুমেন্ট ইনপুট প্রত্যাখ্যাত না হয়ে স্থানধারক লেখা দিয়ে বদলে যায়।
- Reasoning কনফিগার হয় `openai_reasoning_effort` (বা একীভূত [`thinking`](../capabilities/thinking.md) সেটিং) দিয়ে; `openai_reasoning_summary` গৃহীত হয় কিন্তু কোনো সারাংশ তৈরি করে না।
- [`NativeOutput`][pydantic_ai.output.NativeOutput] এখানে পাওয়া যায় কিন্তু Chat Completions-এ নয়: DeepSeek Responses API-তে একটি strict JSON Schema মানে, অথচ এর Chat Completions endpoint `This response_format type is unavailable now` দিয়ে একটি প্রত্যাখ্যান করে।

/// warning | সাধারণ ভুল

DeepSeek-এর Responses API-তে `openai_previous_response_id='auto'` দেওয়া। এরর আসে না, কিন্তু মডেল আগের কথা "ভুলে যায়", কারণ DeepSeek সার্ভারে কিছুই রাখে না। প্রতিবার `message_history` দিন।

///

একটি পার্থক্য Pydantic AI আপনার হয়ে সামলায়: DeepSeek প্রতিটি function call তার পাশের assistant বার্তায় মিলিয়ে দেয়। তাই thinking বা লেখার সাথে কল মেশানো একটি দফা আবার চালালে উত্তরহীন কলসহ আলাদা বার্তা তৈরি হতো, যা DeepSeek `No tool output found for tool call ...` দিয়ে প্রত্যাখ্যান করে। রিকোয়েস্ট তৈরির সময় Pydantic AI কলগুলো অন্য আইটেমের পরে সরায়। এটি শুধু রিকোয়েস্টের ক্রম বদলায়; আপনার [বার্তার ইতিহাস](../message-history.md) অপরিবর্তিত থাকে।

ক্রম বদল প্রযোজ্য শুধু যখন প্রতিটি function call-এর একটি ফল আছে আর দফায় provider-এর নিজস্ব নেটিভ টুল বা compaction আইটেম নেই। DeepSeek যেকোনো ক্রমে অমীমাংসিত কল প্রত্যাখ্যান করে, অথচ provider-এর নিজস্ব আইটেম অপরিবর্তিত রাখা হয়। আরেকটি endpoint থেকে DeepSeek-এর Responses আকার দিলে, বা ক্রম বদল বন্ধ করতে, আপনার নিজের profile-এ [`OpenAIModelProfile.openai_responses_supports_interleaved_function_calls`][pydantic_ai.profiles.openai.OpenAIModelProfile.openai_responses_supports_interleaved_function_calls] সেট করুন।

/// check | সংক্ষেপে মনে রাখুন

* `DEEPSEEK_API_KEY` সেট, তারপর `Agent('deepseek:deepseek-flash')` (Chat Completions)।
* নির্ভরযোগ্য structured output-এ thinking বন্ধ করুন।
* Responses API: `OpenAIResponsesModel` + `DeepSeekProvider`; stateless, তাই সবসময় পুরো ইতিহাস দিন।

///
