# ইনস্টলেশন { #installation }

/// note | এই পেজে যা শিখবেন

* Pydantic AI ইনস্টল করা (`pip` বা `uv` দিয়ে)।
* পূর্ণ প্যাকেজ `pydantic-ai` বনাম ছোট প্যাকেজ `pydantic-ai-slim`, আর কোন extra কী ইনস্টল করে।
* উদাহরণগুলো চালানোর প্যাকেজ, আর কোম্পানির নেটওয়ার্কে TLS সার্টিফিকেটের সমস্যা।

///

Pydantic AI PyPI-তে [`pydantic-ai`](https://pypi.org/project/pydantic-ai/) নামে পাওয়া যায়, তাই ইনস্টল করা খুবই সহজ:

/// tab | pip

```bash
pip install pydantic-ai
```

///

/// tab | uv

```bash
uv add pydantic-ai
```

///


(Python 3.11 বা তার নতুন সংস্করণ লাগে)

এটি `pydantic_ai` প্যাকেজ, মূল dependency, আর OpenAI, Anthropic ও Google-এর মডেল ব্যবহারের লাইব্রেরি ইনস্টল করে, সাথে [CLI](cli.md), [MCP](mcp/client.md), [Evals](evals.md), [Web UI](ui/overview.md) আর [Logfire](logfire.md) integration।
অন্য কোনো মডেল বা integration ব্যবহার করতে, ইনস্টলের কমান্ডে সংশ্লিষ্ট extra যোগ করুন, যেমন `pydantic-ai[bedrock,temporal]`। বিকল্প হিসেবে, শুধু দরকারি extra-সহ [`pydantic-ai-slim`](#slim-install) প্যাকেজ ইনস্টল করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

`pydantic-ai` হলো পুরো রান্নাঘরের সেট: হাঁড়ি-পাতিল সব একসাথে। `pydantic-ai-slim` হলো খালি রান্নাঘর, যেখানে আপনি শুধু দরকারি জিনিস (extra) কিনে আনেন, যেমন শুধু `[openai]`। প্রোডাকশন সার্ভার বা Docker image ছোট রাখতে slim ভালো।

///

/// warning | সাধারণ ভুল

পুরনো Python (3.10 বা তার আগের) থাকলে ইনস্টল ব্যর্থ হবে বা পুরনো সংস্করণ নামবে। আগে `python --version` দেখে নিন, আর প্রতিটি প্রজেক্টে আলাদা virtual environment ব্যবহার করুন।

///

## পরের ধাপ { #next-steps }

[Agents গাইড](agent.md) দিয়ে আপনার প্রথম এজেন্ট বানান, অথবা একটি [উদাহরণ](examples/setup.md) থেকে শুরু করুন।
আপনার এজেন্ট কী করছে দেখতে, [Pydantic Logfire সেটআপ করুন](logfire.md#using-logfire), যার একটি [ফ্রি স্তর](https://pydantic.dev/pricing/) আছে (ক্রেডিট কার্ড লাগে না; শুধু একটি GitHub অ্যাকাউন্ট দিয়েই সাইন আপ)।
একটি API key দিয়ে কয়েকটি প্রোভাইডারের মডেলে পৌঁছাতে, [Pydantic AI Gateway](gateway.md) ব্যবহার করুন।
একটি কোডিং এজেন্ট আপনার সাথে কাজ করলে, [Pydantic AI skill](coding-agent-skills.md) ইনস্টল করুন।

## TLS সার্টিফিকেট { #tls-certificates }

Pydantic AI-এর নিজের HTTP রিকোয়েস্ট, আর [`httpx2`](https://httpx2.pydantic.dev/)-এ চলে যাওয়া প্রোভাইডারগুলোর রিকোয়েস্ট, একটি `certifi` bundle সাথে না এনে অপারেটিং সিস্টেমের trust store-এর বিপরীতে TLS সার্টিফিকেট যাচাই করে।
তাই ছোট container image আর ব্যক্তিগত CA-নির্ভর কোম্পানির proxy-তে সেই সার্টিফিকেটগুলো image-এ ইনস্টল থাকতে হবে (যেমন `ca-certificates` প্যাকেজ, সাথে আপনার proxy-র root CA)।
বিকল্প হিসেবে, এমন প্রোভাইডারকে তার `http_client` আর্গুমেন্টে নিজে কনফিগার করা একটি `httpx2.AsyncClient` দিন — কোন প্রোভাইডার কোন client নেয় তা দেখতে [প্রোভাইডারের ডকস](models/overview.md) দেখুন।
যে প্রোভাইডারের SDK এখনো পুরনো `httpx` ব্যবহার করে (যেমন Groq আর Cohere), সেগুলো `certifi`-ভিত্তিক যাচাই রাখে আর বদলে একটি পুরনো `httpx.AsyncClient` নেয়।

/// tip | কখন এটি দরকার

অফিসের নেটওয়ার্কে বা Docker-এ চালালে যদি `SSL: CERTIFICATE_VERIFY_FAILED` এর মতো এরর পান, তাহলে প্রায় নিশ্চিতভাবে এই কারণ। image-এ `ca-certificates` আর কোম্পানির root CA যোগ করলেই সাধারণত সমাধান হয়।

///

## উদাহরণ চালানো { #running-examples }

উদাহরণগুলো খুব সহজে নিজের মতো বদলানো আর চালানোর জন্য, আমরা [`pydantic_ai_examples`](https://github.com/pydantic/pydantic-ai/tree/main/examples/pydantic_ai_examples) ফোল্ডারটি একটি আলাদা PyPI প্যাকেজ ([`pydantic-ai-examples`](https://pypi.org/project/pydantic-ai-examples/)) হিসেবে প্রকাশ করি।

উদাহরণগুলো ইনস্টল করতে, `examples` ঐচ্ছিক দল ব্যবহার করুন:

/// tab | pip

```bash
pip install "pydantic-ai[examples]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai[examples]"
```

///


উদাহরণ চালাতে, [উদাহরণের ডকসে](examples/setup.md) দেওয়া নির্দেশনা অনুসরণ করুন।

## Slim ইনস্টল { #slim-install }

কোন মডেল ব্যবহার করবেন জানা থাকলে আর অপ্রয়োজনীয় প্যাকেজ ইনস্টল এড়াতে চাইলে, [`pydantic-ai-slim`](https://pypi.org/project/pydantic-ai-slim/) প্যাকেজ ব্যবহার করতে পারেন।
যেমন, শুধু [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] ব্যবহার করলে, চালাবেন:

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


`pydantic-ai-slim`-এর নিচের ঐচ্ছিক দলগুলো (extra) আছে; প্রতিটি কোন সুবিধার জন্য আর কোন প্যাকেজ ইনস্টল করে:

* `logfire` — [Pydantic Logfire](logfire.md) — dependency: `logfire` [PyPI ↗](https://pypi.org/project/logfire){:target="_blank"}
* `evals` — [Pydantic Evals](evals.md) — dependency: `pydantic-evals` [PyPI ↗](https://pypi.org/project/pydantic-evals){:target="_blank"}
* `openai` — [OpenAI Model](models/openai.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `google` — [Google Model](models/google.md) — dependency: `google-genai` [PyPI ↗](https://pypi.org/project/google-genai){:target="_blank"}
* `anthropic` — [Anthropic Model](models/anthropic.md) — dependency: `anthropic` [PyPI ↗](https://pypi.org/project/anthropic){:target="_blank"}
* `groq` — [Groq Model](models/groq.md) — dependency: `groq` [PyPI ↗](https://pypi.org/project/groq){:target="_blank"}
* `mistral` — [Mistral Model](models/mistral.md) — dependency: `mistralai` [PyPI ↗](https://pypi.org/project/mistralai){:target="_blank"}
* `cohere` — [Cohere Model](models/cohere.md) — dependency: `cohere` [PyPI ↗](https://pypi.org/project/cohere){:target="_blank"}
* `bedrock` — [Bedrock Model](models/bedrock.md) — dependency: `boto3` [PyPI ↗](https://pypi.org/project/boto3){:target="_blank"}
* `bedrock-mantle` — [Bedrock Mantle Model](models/bedrock.md#bedrock-mantle) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"} আর `botocore` [PyPI ↗](https://pypi.org/project/botocore){:target="_blank"}
* `xai` — [xAI Model](models/xai.md) — dependency: `xai-sdk` [PyPI ↗](https://pypi.org/project/xai-sdk){:target="_blank"}
* `openrouter` — [OpenRouter](models/openrouter.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `zai` — [Z.AI](models/zai.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `snowflake` — [Snowflake Cortex](models/snowflake.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `crusoe` — [Crusoe](models/crusoe.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `cerebras` — [Cerebras](models/cerebras.md) — dependency: `openai` [PyPI ↗](https://pypi.org/project/openai){:target="_blank"}
* `typesafe` — [TypeSafe (Jev)](models/typesafe.md) — dependency: `typesafe-sdk` [PyPI ↗](https://pypi.org/project/typesafe-sdk){:target="_blank"}
* `huggingface` — [Hugging Face Model](models/huggingface.md) — dependency: `huggingface-hub` [PyPI ↗](https://pypi.org/project/huggingface-hub){:target="_blank"}
* `sentence-transformers` — [Sentence Transformers Embedding Model](embeddings.md#sentence-transformers-local) — dependency: `sentence-transformers` [PyPI ↗](https://pypi.org/project/sentence-transformers){:target="_blank"}
* `voyageai` — [VoyageAI Embedding Model](embeddings.md#voyageai) — dependency: `voyageai` [PyPI ↗](https://pypi.org/project/voyageai){:target="_blank"}
* `duckduckgo` — [DuckDuckGo Search Tool](common-tools.md#duckduckgo-search-tool) — dependency: `ddgs` [PyPI ↗](https://pypi.org/project/ddgs){:target="_blank"}
* `tavily` — [Tavily Search Tool](common-tools.md#tavily-search-tool) — dependency: `tavily-python` [PyPI ↗](https://pypi.org/project/tavily-python){:target="_blank"}
* `exa` — [Exa Search Tool](common-tools.md#exa-search-tool) — dependency: `exa-py` [PyPI ↗](https://pypi.org/project/exa-py){:target="_blank"}
* `web-fetch` — [Web Fetch Tool](common-tools.md#web-fetch-tool) — dependency: `markdownify` [PyPI ↗](https://pypi.org/project/markdownify){:target="_blank"}
* `cli` — [CLI](cli.md) — dependency: `rich` [PyPI ↗](https://pypi.org/project/rich){:target="_blank"}, `prompt-toolkit` [PyPI ↗](https://pypi.org/project/prompt-toolkit){:target="_blank"}, আর `argcomplete` [PyPI ↗](https://pypi.org/project/argcomplete){:target="_blank"}
* `mcp` — [MCP](mcp/client.md) — dependency: `fastmcp-slim[client]` [PyPI ↗](https://pypi.org/project/fastmcp-slim){:target="_blank"}
* `mcp-tasks` — [MCP](mcp/client.md) FastMCP 4 tasks extension (`use_task=True`) — dependency: `fastmcp-tasks` [PyPI ↗](https://pypi.org/project/fastmcp-tasks){:target="_blank"}
* `ui` — [UI Event Streams](ui/overview.md) — dependency: `starlette` [PyPI ↗](https://pypi.org/project/starlette){:target="_blank"}
* `web` — [Web UI](ui/overview.md) — dependency: `starlette` [PyPI ↗](https://pypi.org/project/starlette){:target="_blank"} আর `uvicorn` [PyPI ↗](https://pypi.org/project/uvicorn){:target="_blank"}
* `ag-ui` — [AG-UI Event Stream Protocol](ui/ag-ui.md) — dependency: `ag-ui-protocol` [PyPI ↗](https://pypi.org/project/ag-ui-protocol){:target="_blank"} আর `starlette` [PyPI ↗](https://pypi.org/project/starlette){:target="_blank"}
* `retries` — [transport retries](retries.md#transport-retries) — dependency: `tenacity` [PyPI ↗](https://pypi.org/project/tenacity){:target="_blank"}, সাথে Pydantic AI v3 পর্যন্ত পুরনো `httpx` [PyPI ↗](https://pypi.org/project/httpx){:target="_blank"} সমর্থন
* `temporal` — [Temporal Durable Execution](durable_execution/temporal.md) — dependency: `temporalio` [PyPI ↗](https://pypi.org/project/temporalio){:target="_blank"}
* `dbos` — [DBOS Durable Execution](durable_execution/dbos.md) — dependency: `dbos` [PyPI ↗](https://pypi.org/project/dbos){:target="_blank"}
* `prefect` — [Prefect Durable Execution](durable_execution/prefect.md) — dependency: `prefect` [PyPI ↗](https://pypi.org/project/prefect){:target="_blank"}
* `spec` — [AgentSpec](agent-spec.md) — dependency: `pyyaml` [PyPI ↗](https://pypi.org/project/PyYAML){:target="_blank"} আর `pydantic-handlebars` [PyPI ↗](https://pypi.org/project/pydantic-handlebars){:target="_blank"}

একাধিক মডেল আর ব্যবহারের জন্যও dependency ইনস্টল করতে পারেন, যেমন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[openai,google,logfire]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[openai,google,logfire]"
```

///


/// check | সংক্ষেপে মনে রাখুন

* সবকিছুসহ: `pip install pydantic-ai`; শুধু দরকারিটুকু: `pip install "pydantic-ai-slim[openai]"`।
* একাধিক extra কমা দিয়ে: `"pydantic-ai-slim[openai,google,logfire]"`।
* Python 3.11+ লাগে; TLS এরর হলে সিস্টেমের সার্টিফিকেট দেখুন।

///
