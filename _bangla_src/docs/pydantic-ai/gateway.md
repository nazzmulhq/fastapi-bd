# Pydantic AI Gateway { #pydantic-ai-gateway }

/// note | এই পেজে যা শিখবেন

* Gateway কী: একটি key দিয়ে অনেক AI provider-এর মডেল, খরচের সীমা আর পর্যবেক্ষণসহ।
* account আর key তৈরি, আর Pydantic AI-তে `gateway/` উপসর্গ দিয়ে ব্যবহার।
* Claude Code, Codex, OpenAI/Anthropic/Vercel AI SDK-কে gateway দিয়ে চালানো।
* Gateway endpoint: provider-দের মধ্যে failover আর load balancing।

///

**[Pydantic AI Gateway](https://pydantic.dev/ai-gateway)** হলো একটি key দিয়ে একাধিক AI provider-এ পৌঁছানোর একটি একীভূত interface, [Pydantic Logfire](https://pydantic.dev/logfire) দিয়ে পরিচালিত। এর সুবিধার মধ্যে আছে built-in OpenTelemetry পর্যবেক্ষণ, তাৎক্ষণিক খরচ পর্যবেক্ষণ, failover ব্যবস্থাপনা, আর [Pydantic stack](https://pydantic.dev/)-এর অন্য টুলের সাথে নিজস্ব সংযোগ।

[logfire.pydantic.dev](https://logfire.pydantic.dev/)-এ সাইন আপ করুন।

/// note | প্রশ্ন আছে?

প্রশ্ন আর মতামতের জন্য, [Slack](https://logfire.pydantic.dev/docs/join-slack/)-এ আমাদের সাথে যোগাযোগ করুন।

///

/// tip | উদাহরণ দিয়ে বুঝি

আলাদা আলাদা দোকানের আলাদা আলাদা সদস্য-কার্ড রাখার বদলে, একটি শপিং মলের একটি কার্ড: সব দোকানে চলে, মাসিক খরচের সীমা বসানো যায়, আর কোথায় কত খরচ হলো তার একটি হিসাব পাওয়া যায়। Gateway হলো AI মডেলের জন্য সেই এক কার্ড।

///

## ডকুমেন্টেশনে সংযোগ { #documentation-integration }

Pydantic AI Gateway দিয়ে শুরু করতে সাহায্য করতে, Pydantic AI ডকুমেন্টেশনের কিছু কোড উদাহরণে একটি "Via Pydantic AI Gateway" ট্যাব থাকে, সাধারণ Pydantic AI মডেল স্ট্রিংসহ একটি "Direct to Provider API" ট্যাবের পাশে। দুটোর প্রধান পার্থক্য হলো, Gateway ব্যবহার করলে মডেলের স্ট্রিং `gateway/` উপসর্গ ব্যবহার করে।

## প্রধান সুবিধা { #key-features }

- **API key ব্যবস্থাপনা**: একটি Gateway key দিয়ে একাধিক LLM provider-এ প্রবেশ।
- **খরচের সীমা**: project, user আর API key স্তরে দৈনিক, সাপ্তাহিক আর মাসিক সীমাসহ খরচের সীমা বসান।
- **BYOK আর পরিচালিত provider:** LLM provider-দের নিজের API key আনুন (BYOK), বা প্ল্যাটফর্মের মাধ্যমে সরাসরি inference-এর টাকা দিন।
- **বহু-provider সমর্থন:** OpenAI, Anthropic, Google Vertex, Groq আর AWS Bedrock-এর মডেলে প্রবেশ। _আরও provider শীঘ্রই আসছে_।
- **Gateway endpoint:** একই মডেল দেওয়া provider-দের মধ্যে failover, বা ওজন অনুযায়ী তাদের মধ্যে ট্রাফিক ভাগ করতে [gateway endpoint](#gateway-endpoints) কনফিগার করুন।
- **Backend পর্যবেক্ষণ:** প্রতিটি রিকোয়েস্ট [Pydantic Logfire](https://pydantic.dev/logfire) বা যেকোনো OpenTelemetry backend-এ লগ করুন (_শীঘ্রই আসছে_)।
- **শূন্য অনুবাদ**: সবকিছু একটি সাধারণ schema-য় অনুবাদ করা প্রথাগত AI gateway-র মতো নয়, **Pydantic AI Gateway** রিকোয়েস্টকে প্রতিটি provider-এর নিজস্ব ফরম্যাটে সরাসরি যেতে দেয়। এতে নতুন মডেলের সুবিধা প্রকাশ হওয়ামাত্র সেগুলো পান।
- **Enterprise-এর জন্য প্রস্তুত**: Logfire-এর enterprise সুবিধা উত্তরাধিকারসূত্রে পায়, SSO, নিজের role আর অনুমতিসহ।
- **Cloud বা self-hosted**: Logfire Cloud প্ল্যানে আর self-hosted Logfire-এ পাওয়া যায়; দেখুন [Logfire AI Gateway ডক](https://pydantic.dev/docs/logfire/manage/ai-gateway/)।

```python title="hello_world.py"
from pydantic_ai import Agent

agent = Agent('gateway/openai:gpt-6.1-sol')

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

## দ্রুত শুরু { #quick-start }

আপনার account সেট আপ করুন আর Pydantic AI Gateway credential দিয়ে আপনার অ্যাপ চালান।

### একটি account তৈরি করুন { #create-an-account }

1. [logfire.pydantic.dev](https://logfire.pydantic.dev/)-এ সাইন আপ করুন
2. একটি region বেছে একটি account তৈরি করুন।
3. আপনার প্রতিষ্ঠানের সেটিংয়ে Gateway চালু করুন।

### Gateway API key তৈরি করুন { #create-gateway-api-keys }

Logfire-এ আপনার প্রতিষ্ঠানের Gateway সেটিংয়ে গিয়ে একটি API key তৈরি করুন।

## ব্যবহার { #usage }

ওপরের নির্দেশনা দিয়ে account সেট আপ করার পরে, আপনি Pydantic AI Gateway দিয়ে একটি AI মডেল রিকোয়েস্ট করতে পারবেন।
নিচের কোডের টুকরোগুলো দেখায় বিভিন্ন framework আর SDK-র সাথে Pydantic AI Gateway কীভাবে ব্যবহার করবেন।

ভিন্ন মডেল ব্যবহার করতে, মডেলের স্ট্রিং `gateway/<api_format>:<model_name>` সমর্থিত provider-দের দেওয়া অন্য মডেলে বদলান।

ব্যবহারযোগ্য provider আর মডেলের উদাহরণ:

| **Provider** | **API ফরম্যাট**  | **উদাহরণ মডেল**                        |
| --- |-----------------|------------------------------------------|
| OpenAI | `openai`        | `gateway/openai:gpt-6.1-sol`                 |
| Anthropic | `anthropic`     | `gateway/anthropic:claude-sonnet-5-5`    |
| Google Cloud (আগে Vertex AI) | `google-cloud`, `google` | `gateway/google-cloud:gemini-3.8-flash` |
| Groq | `groq`          | `gateway/groq:openai/gpt-oss-120b`       |
| AWS Bedrock | `bedrock`       | `gateway/bedrock:amazon.nova-micro-v1:0` |

[ছবি তৈরি](image-generation.md) gateway দিয়ে যায় `gateway/google:<model>` হিসেবে, যা Google Cloud-এর মাধ্যমে Gemini-র ছবির মডেল দেয়।

### Pydantic AI { #pydantic-ai }

শুরুর আগে, নিশ্চিত করুন আপনি `pydantic-ai`-এর 1.16 বা পরের সংস্করণে আছেন। সর্বশেষ সংস্করণে হালনাগাদ করতে চালান:

/// tab | uv

```bash
uv sync -P pydantic-ai
```

///

/// tab | pip

```bash
pip install -U pydantic-ai
```

///

`PYDANTIC_AI_GATEWAY_API_KEY` environment variable আপনার Gateway API key-তে সেট করুন:

```bash
export PYDANTIC_AI_GATEWAY_API_KEY="pylf_v..."
```

নিচের কোডের টুকরোয় যেমন দেখানো হয়েছে, একই API key দিয়ে একাধিক মডেলে পৌঁছাতে পারেন।

```python title="hello_world.py"
from pydantic_ai import Agent

agent = Agent('gateway/openai:gpt-6.1-sol')

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

#### API key সরাসরি দেওয়া { #passing-api-key-directly }

[`gateway_provider`][pydantic_ai.providers.gateway.gateway_provider] দিয়ে আপনার API key সরাসরি দিন:

```python title="passing_api_key.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.gateway import gateway_provider

provider = gateway_provider('openai', api_key='pylf_v...')
model = OpenAIChatModel('gpt-6.1-sol', provider=provider)
agent = Agent(model)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

#### একটি ভিন্ন upstream provider ব্যবহার { #using-a-different-upstream-provider }

একটি বিকল্প provider বা gateway endpoint ব্যবহার করতে, `route` প্যারামিটারে সেটি দিতে পারেন:

```python title="routing_via_provider.py"
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.gateway import gateway_provider

provider = gateway_provider(
    'openai',
    api_key='pylf_v...',
    route='builtin-openai'
)
model = OpenAIChatModel('gpt-6.1-sol', provider=provider)
agent = Agent(model)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

### Claude Code { #claude-code }

শুরুর আগে, `/logout` দিয়ে Claude Code থেকে log out করুন।

আপনার Logfire region-এর সাথে মেলা base URL ব্যবহার করে gateway credential environment variable হিসেবে সেট করুন:

/// tab | US

```bash
export ANTHROPIC_BASE_URL="https://gateway-us.pydantic.dev/proxy/anthropic"
export ANTHROPIC_AUTH_TOKEN="YOUR_GATEWAY_API_KEY"
```

///

/// tab | EU

```bash
export ANTHROPIC_BASE_URL="https://gateway-eu.pydantic.dev/proxy/anthropic"
export ANTHROPIC_AUTH_TOKEN="YOUR_GATEWAY_API_KEY"
```

///

`YOUR_GATEWAY_API_KEY`-কে আপনার Logfire প্রতিষ্ঠানের Gateway সেটিং থেকে পাওয়া API key দিয়ে বদলান।

`claude` টাইপ করে Claude Code চালু করুন। এখন সব রিকোয়েস্ট Pydantic AI Gateway দিয়ে যাবে।

### Codex { #codex }

Codex OpenAI Responses API ব্যবহার করে, তাই এটি Gateway-র `openai-responses` route ব্যবহার করা উচিত।

আপনার gateway API key একটি environment variable হিসেবে সেট করুন:

```bash
export PYDANTIC_AI_GATEWAY_API_KEY="YOUR_GATEWAY_API_KEY"
```

তারপর আপনার Logfire region-এর সাথে মেলা base URL ব্যবহার করে `~/.codex/config.toml`-এ নিচের কনফিগারেশন যোগ করুন:

/// tab | US

```toml
model = "gpt-6.1-sol"
model_provider = "pydantic_gateway"

[model_providers.pydantic_gateway]
name = "Pydantic AI Gateway"
base_url = "https://gateway-us.pydantic.dev/proxy/openai-responses"
env_key = "PYDANTIC_AI_GATEWAY_API_KEY"
env_key_instructions = "Create a Gateway API key in your Logfire organization's Gateway settings."
wire_api = "responses"
```

///

/// tab | EU

```toml
model = "gpt-6.1-sol"
model_provider = "pydantic_gateway"

[model_providers.pydantic_gateway]
name = "Pydantic AI Gateway"
base_url = "https://gateway-eu.pydantic.dev/proxy/openai-responses"
env_key = "PYDANTIC_AI_GATEWAY_API_KEY"
env_key_instructions = "Create a Gateway API key in your Logfire organization's Gateway settings."
wire_api = "responses"
```

///

Codex-এ নিজের provider কনফিগার করার আরও বিস্তারিত জানতে দেখুন [Codex custom model providers ডক](https://developers.openai.com/codex/config-advanced#custom-model-providers) আর [Codex configuration reference](https://developers.openai.com/codex/config-reference/)।

আপনার আগে থেকেই একটি `~/.codex/config.toml` থাকলে, পুরো ফাইল বদলে না দিয়ে `[model_providers.pydantic_gateway]` ব্লক যোগ করুন আর `model_provider` হালনাগাদ করুন। Codex যে OpenAI Responses মডেল ব্যবহার করুক চান তা দিয়ে `gpt-6.1-sol` বদলান।

`codex` টাইপ করে Codex চালু করুন। এখন সব রিকোয়েস্ট Pydantic AI Gateway দিয়ে যাবে।

### SDK { #sdks }

#### OpenAI SDK { #openai-sdk }

আপনার Logfire region-এর সাথে মেলা base URL ব্যবহার করুন (`gateway-us` বা `gateway-eu`)।

/// tab | US

```python title="openai_sdk.py"
import openai

client = openai.Client(
    base_url='https://gateway-us.pydantic.dev/proxy/chat/',
    api_key='pylf_v...',
)

response = client.chat.completions.create(
    model='gpt-6.1-sol',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
print(response.choices[0].message.content)
#> Hello user
```

///

/// tab | EU

```python title="openai_sdk.py"
import openai

client = openai.Client(
    base_url='https://gateway-eu.pydantic.dev/proxy/chat/',
    api_key='pylf_v...',
)

response = client.chat.completions.create(
    model='gpt-6.1-sol',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
print(response.choices[0].message.content)
#> Hello user
```

///

#### Anthropic SDK { #anthropic-sdk }

আপনার Logfire region-এর সাথে মেলা base URL ব্যবহার করুন (`gateway-us` বা `gateway-eu`)।

/// tab | US

```python title="anthropic_sdk.py"
import anthropic

client = anthropic.Anthropic(
    base_url='https://gateway-us.pydantic.dev/proxy/anthropic/',
    auth_token='pylf_v...',
)

response = client.messages.create(
    max_tokens=1000,
    model='claude-sonnet-5-5',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
content = response.content[0]
assert isinstance(content, anthropic.types.TextBlock)
print(content.text)
#> Hello user
```

///

/// tab | EU

```python title="anthropic_sdk.py"
import anthropic

client = anthropic.Anthropic(
    base_url='https://gateway-eu.pydantic.dev/proxy/anthropic/',
    auth_token='pylf_v...',
)

response = client.messages.create(
    max_tokens=1000,
    model='claude-sonnet-5-5',
    messages=[{'role': 'user', 'content': 'Hello world'}],
)
content = response.content[0]
assert isinstance(content, anthropic.types.TextBlock)
print(content.text)
#> Hello user
```

///

#### Vercel AI SDK { #vercel-ai-sdk }

[Vercel AI SDK](https://ai-sdk.dev/) প্রতিটি provider-এর `baseURL`-কে মেলা proxy path-এ (যেমন `/proxy/openai` বা `/proxy/anthropic`) দেখিয়ে Gateway দিয়ে যেতে পারে। আপনার Logfire region-এর সাথে মেলা base URL ব্যবহার করুন (`gateway-us` বা `gateway-eu`)।

/// tab | US

```typescript
import { createOpenAI } from "@ai-sdk/openai";
import { generateText } from "ai";

const apiKey = process.env.PYDANTIC_AI_GATEWAY_API_KEY;
if (!apiKey) throw new Error("set PYDANTIC_AI_GATEWAY_API_KEY");

const openai = createOpenAI({
  apiKey,
  baseURL: "https://gateway-us.pydantic.dev/proxy/openai",
});

async function main() {
  const openaiResult = await generateText({
    model: openai("gpt-6.1-sol"),
    prompt: "what color is the sky? reply concisely",
  });
  console.log("openai:", openaiResult.text);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

///

/// tab | EU

```typescript
import { createOpenAI } from "@ai-sdk/openai";
import { generateText } from "ai";

const apiKey = process.env.PYDANTIC_AI_GATEWAY_API_KEY;
if (!apiKey) throw new Error("set PYDANTIC_AI_GATEWAY_API_KEY");

const openai = createOpenAI({
  apiKey,
  baseURL: "https://gateway-eu.pydantic.dev/proxy/openai",
});

async function main() {
  const openaiResult = await generateText({
    model: openai("gpt-6.1-sol"),
    prompt: "what color is the sky? reply concisely",
  });
  console.log("openai:", openaiResult.text);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
```

///

## Gateway endpoint { #gateway-endpoints }

একটি **gateway endpoint** একটি একক slug-এর অধীনে এক বা একাধিক provider-জুড়ে রিকোয়েস্ট পাঠায়। প্রতিটি যুক্ত provider-এর একটি **priority**, একটি **weight** আর একটি **active** ফ্ল্যাগ থাকে, আর এই তিনটি মান মিলে একটি একক endpoint-কে দুটি ভিন্ন routing কৌশল প্রকাশ করতে দেয়:

- **Failover / fallback**: provider-দের ভিন্ন priority দিন। Gateway সবসময় প্রথমে সর্বোচ্চ-priority-র সক্রিয় provider চেষ্টা করে, আর উচ্চতরটি অনুপলব্ধ হলেই শুধু নিম্ন-priority-র provider-এ নামে (যেমন সেটি বন্ধ, rate-limited, বা একটি এরর ফেরত দিলে)।
- **Load balancing**: দুই বা ততোধিক provider-কে একই priority দিন আর প্রতিটিকে একটি weight দিন। Gateway সেই provider-দের মধ্যে তাদের weight-এর অনুপাতে ট্রাফিক ভাগ করে।

দুটি কৌশল একসাথে মেলে: যেমন, আপনার একটি শীর্ষ priority স্তরে দুটি provider 70/30 load-balance করা থাকতে পারে, আর একটি দ্বিতীয় priority স্তর, যা শুধু তখনই ট্রাফিক পায় যখন শীর্ষ স্তরের দুটি provider-ই ব্যর্থ হয়।

### একটি gateway endpoint তৈরি { #creating-a-gateway-endpoint }

Gateway endpoint Logfire-এ আপনার প্রতিষ্ঠানের Gateway সেটিং থেকে পরিচালিত হয়:

1. **Gateway -> Endpoints** খুলে **New Endpoint**-এ ক্লিক করুন।
2. endpoint-কে একটি slug দিন (যেমন `anthropic-routing`) আর একটি ঐচ্ছিক বর্ণনা।
3. endpoint-এর **Providers** পেজ খুলে এক বা একাধিক provider যোগ করুন। প্রতিটি provider-এর জন্য সেট করুন:
    - **Priority** - বড় মান আগে চেষ্টা হয়। failover-এর জন্য provider-দের ভিন্ন priority দিন।
    - **Weight** - একই priority-র provider-দের মধ্যে ব্যবহৃত load-balancing weight।
    - **Active** - routing-এর সময় নিষ্ক্রিয় provider বাদ পড়ে।

### একটি gateway endpoint ব্যবহার { #using-a-gateway-endpoint }

`route` প্যারামিটার (endpoint-এর slug) দিয়ে Gateway provider-কে endpoint-এর দিকে দেখান:

```python title="gateway_endpoint.py"
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.gateway import gateway_provider

provider = gateway_provider(
    'anthropic',
    api_key='pylf_v...',
    route='anthropic-routing',  # (1)!
)
model = AnthropicModel('claude-sonnet-5-5', provider=provider)
agent = Agent(model)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)
"""
The first known use of "hello, world" was in a 1974 textbook about the C programming language.
"""
```

1. Logfire-এ আপনার তৈরি gateway endpoint-এর slug।

## সমস্যা সমাধান { #troubleshooting }

### খরচ হিসাব করা যাচ্ছে না { #unable-to-calculate-spend }

খরচের অন্তর্দৃষ্টি দিতে আর খরচের সীমা প্রয়োগ করতে gateway-কে একটি রিকোয়েস্টের খরচ জানতে হয়।

প্রতিটি provider-এর সেটিংয়ে একটি **Require pricing data** টগল আছে। চালু থাকলে (ডিফল্ট), gateway যে মডেলের দামের ডেটা নেই তার রিকোয়েস্ট upstream-এ পাঠানোর আগেই প্রত্যাখ্যান করে। বন্ধ থাকলে, সেই রিকোয়েস্ট যেতে দেওয়া হয়, কিন্তু তাদের খরচ ট্র্যাক হবে না আর খরচের সীমায় গোনা হবে না।

প্রত্যাখ্যানের উত্তর provider-এর ধরনের ওপর নির্ভর করে:

- **Built-in provider** (Pydantic-পরিচালিত): `404`, একটি বার্তাসহ যা আপনাকে Slack-এ আমাদের জানাতে বলে যাতে আমরা মডেলটি যোগ করতে পারি।
- **Custom provider** (আপনার নিজের API key): `400`, জানিয়ে যে দামের ডেটা লাগবে, আর তবুও রিকোয়েস্ট যেতে দিতে চাইলে টগলটি বন্ধ করার ইঙ্গিতসহ।

আমরা আরও provider আর মডেল সমর্থনে সক্রিয়ভাবে কাজ করছি। নির্দিষ্ট কোনো provider বা মডেলের সমর্থন চাইলে, [Slack](https://logfire.pydantic.dev/docs/join-slack/)-এ আমাদের জানান বা [`genai-prices`-এ একটি issue খুলুন](https://github.com/pydantic/genai-prices/issues/new)।

/// check | সংক্ষেপে মনে রাখুন

* Logfire-এ account আর Gateway key তৈরি করে `PYDANTIC_AI_GATEWAY_API_KEY` সেট করুন।
* মডেলের স্ট্রিংয়ে `gateway/` উপসর্গ: `Agent('gateway/openai:gpt-6.1-sol')`।
* Claude Code, Codex আর অন্য SDK-ও gateway-র base URL দিয়ে চলে (region অনুযায়ী US/EU)।
* Gateway endpoint: ভিন্ন priority = failover, একই priority + weight = load balancing; `route=` দিয়ে ব্যবহার।

///
