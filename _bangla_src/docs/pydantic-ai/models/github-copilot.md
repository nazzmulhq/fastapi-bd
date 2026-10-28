# GitHub Copilot { #github-copilot }

/// note | এই পেজে যা শিখবেন

* আপনার Copilot subscription দিয়ে `GitHubCopilotModel`-এর মাধ্যমে Claude, Gemini, GPT মডেল ব্যবহার।
* কোন token কাজ করে, device login, আর token environment variable-এ রাখা।
* আপনার প্ল্যানে কোন মডেল id পাওয়া যায়, thinking, নিজের endpoint, integration id আর সীমাবদ্ধতা।

///

[GitHub Copilot](https://docs.github.com/en/copilot) Anthropic, OpenAI, Google, xAI আর MoonshotAI-এর মডেল দেয়, যা আপনার Copilot subscription থেকে নেওয়া AI credit-এ মাপা হয়, প্রকাশিত প্রতি-মডেল token হারে। Pydantic AI Copilot-এর OpenAI-সামঞ্জস্যপূর্ণ Chat Completions API-র সাথে কথা বলে, যা শুধু সেখানে Copilot যে id দেখায় সেগুলোতেই পৌঁছায়: লেখার সময় Claude, Gemini আর Kimi id এবং `gpt-5.4`, অথচ প্রতিটি xAI Grok id আর বেশিরভাগ অন্য GPT id শুধু Responses API-তে পরিবেশিত আর Pydantic AI তা বলা পর্যন্ত নাগালের বাইরে। আপনারটি পরীক্ষা করতে দেখুন [Model ids depend on your plan](#model-ids-depend-on-your-plan)।

## ইনস্টল { #install }

[`GitHubCopilotModel`][pydantic_ai.models.github_copilot.GitHubCopilotModel] ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `openai` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

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

Copilot একটি bearer token দিয়ে প্রমাণীকরণ করে। একটি OAuth user token — যা `gh auth token` ছাপায়, বা `copilot login`-এর পরে Copilot CLI যা রাখে — সরাসরি inference API-তে কাজ করে; কোনো token বিনিময় লাগে না।

| Token-এর ধরন | অবস্থা |
| --- | --- |
| OAuth user token (`gho_`) | কাজ করে। |
| Copilot API token (`tid=…`) | কাজ করে, যে প্ল্যান একটি দেয় তাতে। |
| **Copilot Requests**-সহ fine-grained PAT (`github_pat_`) | [GitHub-এর Copilot SDK ডক](https://docs.github.com/copilot/how-tos/copilot-sdk/authenticate-copilot-sdk/authenticate-copilot-sdk)-এ তালিকাভুক্ত, কিন্তু আমাদের পরীক্ষা করা Individual প্ল্যানে ডিফল্ট `vscode-chat` [integration id](#integration-id)-এর অধীনে `401 unauthorized` দিয়ে প্রত্যাখ্যাত। |
| Classic PAT (`ghp_`) | GitHub সমর্থন করে না। |

/// tip | সবচেয়ে সহজ পথ

আপনার কম্পিউটারে `gh` CLI-তে লগইন করা থাকলে: `export GITHUB_COPILOT_API_KEY=$(gh auth token)` — ব্যস, তারপর `Agent('github-copilot:gpt-5.4')`।

///

## Device login { #device-login }

GitHub-এর device flow দিয়ে একটি token পেতে [`GitHubCopilotOAuthFlow`][pydantic_ai.providers.github_copilot.GitHubCopilotOAuthFlow] ব্যবহার করুন:

```python
import os
import sys

import anyio

from pydantic_ai import Agent
from pydantic_ai.models.github_copilot import GitHubCopilotModel
from pydantic_ai.providers.github_copilot import (
    GitHubCopilotOAuthFlow,
    GitHubCopilotProvider,
)


async def main() -> None:
    flow = GitHubCopilotOAuthFlow(client_id=os.environ['GITHUB_OAUTH_CLIENT_ID'])
    authorization = await flow.start()
    sys.stdout.write(f'Open {authorization.verification_uri}\nEnter code: {authorization.user_code}\n')
    sys.stdout.flush()
    credentials = await flow.wait_for_authorization()

    provider = GitHubCopilotProvider(api_key=credentials.access_token)
    async with provider:
        agent = Agent(GitHubCopilotModel('claude-haiku-4.5', provider=provider))
        result = await agent.run('Explain Python context managers in two sentences.')
    sys.stdout.write(f'{result.output}\n')


anyio.run(main)
```

[`GitHubCopilotOAuthFlow`][pydantic_ai.providers.github_copilot.GitHubCopilotOAuthFlow] GitHub.com-এর [device authorization flow](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow) বাস্তবায়ন করে। একটি OAuth অ্যাপ্লিকেশন নথিভুক্ত করুন আর এর সেটিংয়ে device flow চালু করুন। `GITHUB_OAUTH_CLIENT_ID` এই উদাহরণে ব্যবহৃত অ্যাপ্লিকেশন কনফিগারেশন, Pydantic AI নিজে থেকে পড়ে এমন কোনো ভ্যারিয়েবল নয়।

/// warning | শুধু নিজের লগইন চেষ্টার device code অনুমোদন করুন

CLI বা headless অ্যাপ্লিকেশনের মতো সীমিত client-এর জন্য device flow ব্যবহার করুন। যে অ্যাপ্লিকেশন browser redirect নিতে পারে তার বদলে PKCE-সহ authorization code ব্যবহার করা উচিত। একটি সর্বজনীন client ID দিয়ে যে কেউ একটি device grant শুরু করতে পারে; একজন আক্রমণকারীর দেওয়া একটি code লিখলে আপনার নয়, তার client অনুমোদিত হয়। ব্যবহারকারীদের বলুন শুধু যে অ্যাপ্লিকেশনে তারা লগইন করছেন তার দেখানো code অনুমোদন করতে, বার্তায় পাওয়া code নয়। দেখুন [RFC 8628-এর phishing নির্দেশনা](https://www.rfc-editor.org/rfc/rfc8628.html#section-5.4)।

///

Helper-টির আপনার অ্যাপ্লিকেশনের `client_id` লাগে; এটি অন্য অ্যাপ্লিকেশনের পরিচয় ধার করে না। এটি ডিফল্টভাবে কোনো scope চায় না। আপনার অ্যাপ্লিকেশনের GitHub অনুমতি লাগলে `scope=` দিন।

/// warning | GitHub অনুমোদন মানেই Copilot প্রবেশাধিকার নয়

একটি সফল লগইন একটি GitHub OAuth token ফেরত দেয়, প্রমাণ নয় যে Copilot সেই অ্যাপ্লিকেশনের token গ্রহণ করে বা account-এর একটি যোগ্য subscription আছে। আপনার অ্যাপ্লিকেশনের জন্য দুটোই যাচাই করুন। আপনার কাছে আগে থেকেই কাজ করা credential থাকলে নিচের বিদ্যমান-token উদাহরণগুলো উপলব্ধ থাকে।

///

`start()` একটি [`GitHubCopilotDeviceAuthorization`][pydantic_ai.providers.github_copilot.GitHubCopilotDeviceAuthorization] ফেরত দেয়। এর `user_code` আর `verification_uri` দেখান, তারপর `wait_for_authorization()` await করুন। Polling GitHub-এর বিরতি মানে আর GitHub `slow_down` দিয়ে উত্তর দিলে তা বাড়ায়। লোকাল সময়সীমা device-code উত্তর আসার `expires_in` সেকেন্ড পরে; code দেখাতে কাটানো সময়ও এতে গোনা হয়। মেয়াদ শেষ, প্রত্যাখ্যান আর অবৈধ উত্তর [`UserError`][pydantic_ai.exceptions.UserError] তোলে; transport এরর অপরিবর্তিত ছড়ায়। বাতিল করলে polling থামে। যেকোনো ফলের পরে আবার চেষ্টা করতে আবার `start()` ডাকুন, আর একই সময়ের প্রতিটি লগইনের জন্য আলাদা flow instance ব্যবহার করুন।

browser খোলা আর credential সংরক্ষণ আপনার অ্যাপ্লিকেশনের দায়িত্ব। [`GitHubCopilotCredentials`][pydantic_ai.providers.github_copilot.GitHubCopilotCredentials] `repr` থেকে token বাদ দেয়, কিন্তু serialize করা credential-এ তবুও গোপন তথ্য থাকে। সেগুলো আপনার অ্যাপ্লিকেশনের credential store-এ রাখুন, লগে নয়। একটি দেওয়া `http_client` caller-এর মালিকানায় থাকে; একটি ছাড়া, helper প্রতিটি রিকোয়েস্টের পরে তার অস্থায়ী client বন্ধ করে। OAuth redirect অনুসরণ করা হয় না, আর এই helper GitHub.com সমর্থন করে, enterprise authorization host নয়।

/// note | Credential নবায়ন অ্যাপ্লিকেশনের দায়িত্ব

কিছু OAuth অ্যাপ্লিকেশন মেয়াদোত্তীর্ণ হয় এমন access token দেয়। GitHub দিলে ফল `refresh_token`, `expires_in` আর `refresh_token_expires_in` রাখে; সময়কাল দেওয়ার মুহূর্ত থেকে সেকেন্ডে। credential সংরক্ষণ করলে এই মানগুলোর সাথে দেওয়ার সময়ও রাখুন। `GitHubCopilotProvider(api_key=...)` token নবায়ন করে না। আপনার অ্যাপ্লিকেশনকে GitHub-এর নথিভুক্ত flow দিয়ে সেগুলো refresh করতে হবে বা ব্যবহারকারীকে আবার লগইন করতে বলতে হবে।

///

## Environment variable { #environment-variable }

আপনার কাছে আগে থেকেই একটি token থাকলে, অ্যাপ্লিকেশন শুরুর আগে `GITHUB_COPILOT_API_KEY` সেট করুন:

```bash
export GITHUB_COPILOT_API_KEY='your-copilot-token'
```

`GITHUB_COPILOT_API_TOKEN` আর `COPILOT_GITHUB_TOKEN` বিকল্প হিসেবে পড়া হয়, কারণ GitHub-এর নিজের টুল সেই নাম ব্যবহার করে। সাধারণ-উদ্দেশ্যের `GITHUB_TOKEN`, `GH_TOKEN` আর `GITHUB_API_KEY` ভ্যারিয়েবল ইচ্ছাকৃতভাবে পড়া **হয় না**, তাই GitHub API-র জন্য সেট করা একটি token কখনো Copilot-এ পাঠানো হয় না।

তারপর নাম দিয়ে [`GitHubCopilotModel`][pydantic_ai.models.github_copilot.GitHubCopilotModel] ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('github-copilot:claude-haiku-4.5')
...
```

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.github_copilot import GitHubCopilotModel

model = GitHubCopilotModel('gpt-5.4')
agent = Agent(model)
...
```

অথবা [`GitHubCopilotProvider`][pydantic_ai.providers.github_copilot.GitHubCopilotProvider] দিয়ে token স্পষ্টভাবে দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.github_copilot import GitHubCopilotModel
from pydantic_ai.providers.github_copilot import GitHubCopilotProvider

model = GitHubCopilotModel(
    'claude-haiku-4.5',
    provider=GitHubCopilotProvider(api_key='your-copilot-token'),
)
agent = Agent(model)
...
```

## মডেল id আপনার প্ল্যানের ওপর নির্ভর করে { #model-ids-depend-on-your-plan }

Copilot-এর তালিকা subscription ভেদে আলাদা আর প্রায়ই বদলায়, তাই Pydantic AI কোনো নির্দিষ্ট তালিকা দেয় না — যেকোনো id গৃহীত হয় আর আপনি যেভাবে লিখেছেন হুবহু সেভাবে Copilot-এ পাঠানো হয়, ডটসহ। আপনার নিজের প্ল্যান যে id দেয় সেগুলোর তালিকা দেখুন:

```bash
curl -H "Authorization: Bearer $GITHUB_COPILOT_API_KEY" \
     -H "Copilot-Integration-Id: ${GITHUB_COPILOT_INTEGRATION_ID:-vscode-chat}" \
     https://api.githubcopilot.com/models
```

প্রতিটি এন্ট্রির `supported_endpoints` বলে কোন API এটি দেয়; Pydantic AI-এর সেই তালিকায় `/chat/completions` লাগে।

তালিকাটি `Copilot-Integration-Id` header-এর ওপর নির্ভর করে, যা `GitHubCopilotProvider` প্রতিটি রিকোয়েস্টে পাঠায় ([ডিফল্টভাবে `vscode-chat`](#integration-id)), তাই শুধু-`Authorization` একটি কল provider আসলে যতগুলোতে পৌঁছাতে পারে তার চেয়ে কম id ফেরত দেয় — লেখার সময়, Gemini id-গুলো।

দুটি `400` উত্তর বলে একটি id কেন কাজ করেনি:

- `model_not_supported` — আপনার প্ল্যানে সেই মডেল নেই। যেমন, `claude-sonnet-4.5` একটি Individual প্ল্যানে পাওয়া যায় না।
- `unsupported_api_for_model` — মডেল আছে কিন্তু Chat Completions-এ পরিবেশিত নয়। Pydantic AI এখনো Copilot-এর Responses API বলে না, তাই এই id-গুলো — লেখার সময়, প্রতিটি xAI Grok id — আপাতত নাগালের বাইরে।

## Thinking { #thinking }

Chat Completions-এ পৌঁছানো যায় এমন reasoning মডেল — যেমন লেখার সময় `gpt-5.4`, `claude-sonnet-5` আর `gemini-3.8-flash` — একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] সেটিং নেয়:

```python
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings

agent = Agent(
    'github-copilot:gpt-5.4',
    model_settings=ModelSettings(thinking='high'),
)
...
```

কোন id তাদের reasoning দেখায় তা পরিবার অনুযায়ী আলাদা। Copilot Anthropic আর Google-এর reasoning ফেরত দেয় একটি `reasoning_text` ফিল্ডে, OpenAI-সামঞ্জস্যপূর্ণ provider সাধারণত যে দুই ফিল্ড-নাম ব্যবহার করে তার কোনোটিতে নয়, আর Pydantic AI `claude-` আর `gemini-` id-এর জন্য সেই ফিল্ড চেনে, তাই তাদের reasoning stream আর stream নয় দুই পথেই একটি [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] হিসেবে আসে আর পরের দফায় একই ফিল্ডে ফেরত যায়। Copilot এর পাশাপাশি একটি `reasoning_opaque` signature ফেরত দেয়, যা Pydantic AI বহন করে না; Copilot এটি ছাড়াই পরের দফা গ্রহণ করে। OpenAI আর MoonshotAI id অন্য ক্ষেত্র: `gpt-5.4` আর `kimi-k3` আপনার দেওয়া effort-এ reasoning করে — `kimi-k3` এর জন্য reasoning token বিল করে — কিন্তু Copilot কোনো reasoning লেখাই ফেরত দেয় না, তাই সেই id-গুলো কখনো একটি `ThinkingPart` তৈরি করে না।

Claude id-গুলো *adaptive*-ভাবেও reasoning করে: আপনার সেট করা effort একটি নির্দেশ নয়, ছাদ, তাই Copilot যেকোনো effort-এ একটি সহজ প্রশ্নের উত্তর কোনো reasoning ছাড়াই দিতে পারে, আর প্রতিটি উত্তরে একটি `ThinkingPart` নিশ্চিত নয়।

`thinking` `reasoning_effort` হিসেবে পাঠানো হয় আর Copilot প্রতি মডেলে ঠিক করে কী গ্রহণ করবে: একটি id তালিকায় রাখে না এমন একটি স্তর চাইলে এটি যে স্তরগুলো রাখে তার নাম দিয়ে `400 invalid_reasoning_effort` উত্তর দেয়। জানার মতো চারটি ক্ষেত্র:

- `thinking=False` হয় `reasoning_effort='none'`, যা শুধু কিছু id দেয়। `claude-` আর `gemini-` id `low` থেকে ওপরে তালিকা করে আর কোনো `none` নেই, তাই সেখানে চুপচাপ কিছু না করে এটি `400` দেয়।
- `thinking=True` হয় `reasoning_effort='medium'`, যা `kimi-k3` তালিকায় রাখে না (এর স্তর `low`, `high`, `max`), তাই সেটির জন্য একটি স্পষ্ট স্তর বাছুন।
- `thinking='max'` হয় `reasoning_effort='xhigh'`, যা `kimi-k3`-ও তালিকায় রাখে না, তাই এর জন্য `openai_reasoning_effort='max'` সেট করুন।
- যে id-র এন্ট্রিতে কোনো `reasoning_effort` key-ই নেই, যেমন `claude-haiku-4.5`, প্রতিটি মান প্রত্যাখ্যান করে।

## নিজের endpoint { #custom-endpoints }

Copilot Enterprise host, GitHub Enterprise Server আর লোকাল proxy একই API ভিন্ন host-এ বলে। `base_url` দিয়ে, বা `GITHUB_COPILOT_BASE_URL`, `COPILOT_API_URL` বা `GITHUB_COPILOT_API_BASE` environment variable দিয়ে provider-কে একটির দিকে দেখান:

```python
from pydantic_ai import Agent
from pydantic_ai.models.github_copilot import GitHubCopilotModel
from pydantic_ai.providers.github_copilot import GitHubCopilotProvider

model = GitHubCopilotModel(
    'claude-haiku-4.5',
    provider=GitHubCopilotProvider(
        api_key='your-copilot-token',
        base_url='https://copilot.example.com',
    ),
)
agent = Agent(model)
...
```

## Integration id { #integration-id }

প্রতিটি রিকোয়েস্ট একটি `Copilot-Integration-Id` header বহন করে। Copilot ট্রাফিক এর নামে ধরে আর এর quota আর মডেলের অনুমোদিত তালিকা এর সাথে বাঁধে, তাই একটি ভিন্ন id `/models` তালিকা কোন মডেল ফেরত দেয় আর Copilot কোনগুলো দেয় তা বদলাতে পারে। এটি একটি credential গৃহীত হবে কিনা তাও ঠিক করতে পারে: GitHub Agentic Workflows api-proxy দিয়ে আমাদের পরীক্ষায়, Copilot `vscode-chat`-এর অধীনে একটি fine-grained PAT `400 Personal Access Tokens are not supported for this endpoint` দিয়ে প্রত্যাখ্যান করেছে, আর `agentic-workflows`-এর অধীনে গ্রহণ করেছে। provider ডিফল্টভাবে `vscode-chat` পাঠায়। আরেকটি id পাঠাতে `integration_id` দিন, বা `GITHUB_COPILOT_INTEGRATION_ID` environment variable সেট করুন, যে নাম [Copilot CLI পড়ে](https://docs.github.com/en/copilot/how-tos/copilot-sdk/setup/multi-tenancy#integration-id); আর্গুমেন্ট অগ্রাধিকার পায়। যেমন, GitHub Agentic Workflows নিজেকে `agentic-workflows` হিসেবে পরিচয় দেয়:

```python
from pydantic_ai import Agent
from pydantic_ai.models.github_copilot import GitHubCopilotModel
from pydantic_ai.providers.github_copilot import GitHubCopilotProvider

model = GitHubCopilotModel(
    'claude-haiku-4.5',
    provider=GitHubCopilotProvider(
        api_key='your-copilot-token',
        integration_id='agentic-workflows',
    ),
)
agent = Agent(model)
...
```

## যা সমর্থিত নয় { #not-supported }

Copilot-এর Responses (`/responses`) আর Messages (`/v1/messages`) API আর realtime বাস্তবায়িত নয়। embedding-ও নয়, তবে যেহেতু `github-copilot` একটি OpenAI-chat-সামঞ্জস্যপূর্ণ provider হিসেবে গোনা হয়, `Embedder('github-copilot:...')` এরর না তুলে তবুও একটি [`OpenAIEmbeddingModel`](../embeddings.md) বানায় — এটি gateway-র `/embeddings`-এর দিকে দেখায়, যা `400` উত্তর দেয়। খরচ আর context-window-এর ডেটাও পাওয়া যায় না: [genai-prices](https://github.com/pydantic/genai-prices) [genai-prices#683](https://github.com/pydantic/genai-prices/pull/683)-এ একটি `github-copilot` এন্ট্রি পেয়েছে, কিন্তু এখনো কোনো প্রকাশিত release এটি বহন করে না।

Copilot-এর Claude id Anthropic-এর sampling নিষেধাজ্ঞা উত্তরাধিকারসূত্রে পায়। Opus 4.7, Opus 4.8, Opus 5, Sonnet 5, Fable 5, Mythos 5 আর Haiku 5.5-এ — আর যে id-র নাম এগুলোর একটি দিয়ে শুরু তাতে — `temperature` আর `top_p` পাঠানো না হয়ে রিকোয়েস্ট থেকে নিঃশব্দে বাদ পড়ে, ঠিক যেমন [Anthropic API](anthropic.md) দিয়ে একই মডেলে পৌঁছালে হয়। শুধু এই দুটি key যায়: `top_k`-এর বাদ দেওয়ার মতো কোনো Chat Completions সমতুল্য নেই, আর `extra_body`-তে দেওয়া একটি `temperature`, বা যেকোনো `openai_*` সেটিং, তবুও পাঠানো হয়। বাকি প্রতিটি id — তাদের মধ্যে `claude-haiku-4.5` — দুটোই অপরিবর্তিত পাঠায়।

/// check | সংক্ষেপে মনে রাখুন

* `GITHUB_COPILOT_API_KEY`-এ একটি OAuth user token (`gh auth token`), তারপর `Agent('github-copilot:<id>')`।
* শুধু Chat Completions-এ পরিবেশিত id কাজ করে; `/models` তালিকায় আপনার প্ল্যানেরটি দেখুন।
* `thinking` → `reasoning_effort`; প্রতিটি মডেলের অনুমোদিত স্তর আলাদা।
* নিজের অ্যাপে লগইনে `GitHubCopilotOAuthFlow` (device flow); token নিরাপদে রাখুন।

///
