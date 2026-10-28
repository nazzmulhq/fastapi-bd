
# সাধারণ টুল { #common-tools }

/// note | এই পেজে যা শিখবেন

* Pydantic AI-এর সাথে আসা তৈরি-করা "সাধারণ টুল" কী — যেগুলো আপনাকে নিজে লিখতে হয় না।
* DuckDuckGo আর Tavily দিয়ে ওয়েব সার্চ, আর web fetch দিয়ে যেকোনো ওয়েবপেজ পড়া।
* প্রতিটির জন্য কোন optional group ইনস্টল করতে হবে।
* web fetch-এ credential (`Authorization` header) পাঠানোর নিরাপত্তা-ঝুঁকি।

///

Pydantic AI কিছু সাধারণ টুলসহ আসে, যা আপনার এজেন্টের ক্ষমতা বাড়ায়।

/// tip | উদাহরণ দিয়ে বুঝি

[নেটিভ টুল](native-tools.md) চলে মডেল provider-এর সার্ভারে, তাই সব মডেলে পাওয়া যায় না। সাধারণ টুল হলো সাধারণ Python [ফাংশন টুল](tools.md) — চলে **আপনার** কম্পিউটারে, তাই যেকোনো মডেলের সাথে কাজ করে। যেমন Ollama-র একটি লোকাল মডেলেও `duckduckgo_search_tool()` দিয়ে ওয়েব সার্চ করা যায়।

///

## DuckDuckGo Search টুল { #duckduckgo-search-tool }

DuckDuckGo search টুল আপনাকে ওয়েবে তথ্য খুঁজতে দেয়। এটি
[DuckDuckGo API](https://github.com/deedy5/ddgs)-এর ওপর তৈরি।

### ইনস্টলেশন { #installation }

[`duckduckgo_search_tool`][pydantic_ai.common_tools.duckduckgo.duckduckgo_search_tool] ব্যবহার করতে, আপনাকে
`duckduckgo` optional group-সহ [`pydantic-ai-slim`](install.md#slim-install) ইনস্টল করতে হবে:

/// tab | pip

```bash
pip install "pydantic-ai-slim[duckduckgo]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[duckduckgo]"
```

///


### ব্যবহার { #usage }

একটি এজেন্টের সাথে DuckDuckGo search টুল কীভাবে ব্যবহার করবেন তার একটি উদাহরণ:

```python title="duckduckgo_search.py"
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

agent = Agent(
    'openai:gpt-6.1-sol',
    tools=[duckduckgo_search_tool()],
    instructions='Search DuckDuckGo for the given query and return the results.',
)

result = agent.run_sync(
    'Can you list the top five highest-grossing animated films of 2025?'
)
print(result.output)
"""
I looked into several sources on animated box‐office performance in 2025, and while detailed
rankings can shift as more money is tallied, multiple independent reports have already
highlighted a couple of record‐breaking shows. For example:

• Ne Zha 2 – News outlets (Variety, Wikipedia's "List of animated feature films of 2025", and others)
    have reported that this Chinese title not only became the highest‑grossing animated film of 2025
    but also broke records as the highest‑grossing non‑English animated film ever. One article noted
    its run exceeded US$1.7 billion.
• Inside Out 2 – According to data shared on Statista and in industry news, this Pixar sequel has been
    on pace to set new records (with some sources even noting it as the highest‑grossing animated film
    ever, as of January 2025).

Beyond those two, some entertainment trade sites (for example, a Just Jared article titled
"Top 10 Highest-Earning Animated Films at the Box Office Revealed") have begun listing a broader
top‑10. Although full consolidated figures can sometimes differ by source and are updated daily during
a box‑office run, many of the industry trackers have begun to single out five films as the biggest
earners so far in 2025.

Unfortunately, although multiple articles discuss the "top animated films" of 2025, there isn't yet a
single, universally accepted list with final numbers that names the complete top five. (Box‑office
rankings, especially mid‑year, can be fluid as films continue to add to their totals.)

Based on what several sources note so far, the two undisputed leaders are:
1. Ne Zha 2
2. Inside Out 2

The remaining top spots (3–5) are reported by some outlets in their "Top‑10 Animated Films"
lists for 2025 but the titles and order can vary depending on the source and the exact cut‑off
date of the data. For the most up‑to‑date and detailed ranking (including the 3rd, 4th, and 5th
highest‑grossing films), I recommend checking resources like:
• Wikipedia's "List of animated feature films of 2025" page
• Box‑office tracking sites (such as Box Office Mojo or The Numbers)
• Trade articles like the one on Just Jared

To summarize with what is clear from the current reporting:
1. Ne Zha 2
2. Inside Out 2
3–5. Other animated films (yet to be definitively finalized across all reporting outlets)

If you're looking for a final, consensus list of the top five, it may be best to wait until
the 2025 year‑end box‑office tallies are in or to consult a regularly updated entertainment industry source.

Would you like help finding a current source or additional details on where to look for the complete updated list?
"""
```

/// info | কোডটি সহজ ভাষায়

`duckduckgo_search_tool()` একটি তৈরি-করা টুল **ফেরত দেয়** (এটি একটি factory ফাংশন), তাই এটি `tools=[...]`-এ ডাকা অবস্থায় (`()`-সহ) দিতে হয়। মডেল প্রশ্নের উত্তর দিতে দরকার মনে করলে নিজেই সার্চ কোয়েরি লিখে টুলটি ডাকে, আর ফলাফল (শিরোনাম, লিংক, সারাংশ) পড়ে উত্তর বানায়। DuckDuckGo-তে কোনো API key লাগে না — তাই শুরু করার জন্য এটিই সবচেয়ে সহজ।

///

## Web Fetch টুল { #web-fetch-tool }

web fetch টুল আপনার এজেন্টকে ওয়েবপেজের বিষয়বস্তু আনতে আর তা markdown-এ রূপান্তর করতে দেয়।
server-side request forgery আক্রমণ ঠেকাতে এটি [SSRF সুরক্ষা](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery) ব্যবহার করে।

/// info | SSRF মানে কী?

মডেল নিজে URL বাছে। কেউ prompt-এ কৌশল করে মডেলকে দিয়ে `http://localhost:8000/admin` বা আপনার অভ্যন্তরীণ নেটওয়ার্কের কোনো ঠিকানা খোলাতে পারে — যা বাইরে থেকে পৌঁছানো যায় না, কিন্তু আপনার সার্ভার থেকে যায়। একে বলে Server-Side Request Forgery (SSRF)। এই টুল এমন private/অভ্যন্তরীণ ঠিকানায় রিকোয়েস্ট আটকে দেয়।

///

### ইনস্টলেশন { #installation_1 }

[`web_fetch_tool`][pydantic_ai.common_tools.web_fetch.web_fetch_tool] ব্যবহার করতে, আপনাকে
`web-fetch` optional group-সহ [`pydantic-ai-slim`](install.md#slim-install) ইনস্টল করতে হবে:

/// tab | pip

```bash
pip install "pydantic-ai-slim[web-fetch]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[web-fetch]"
```

///


### ব্যবহার { #usage_1 }

একটি এজেন্টের সাথে web fetch টুল কীভাবে ব্যবহার করবেন তার একটি উদাহরণ:

```python title="web_fetch.py"
from pydantic_ai import Agent
from pydantic_ai.common_tools.web_fetch import web_fetch_tool

agent = Agent(
    'openai:gpt-6.1-sol',
    tools=[web_fetch_tool()],
    instructions='Fetch web pages and summarize their content.',
)

result = agent.run_sync('What is on https://ai.pydantic.dev?')
print(result.output)
```

/// tip | WebFetch capability দিয়ে স্বয়ংক্রিয় বিকল্প

আপনাকে [`web_fetch_tool`][pydantic_ai.common_tools.web_fetch.web_fetch_tool] সরাসরি ব্যবহার করতে হবে না — 
[`WebFetch`][pydantic_ai.capabilities.WebFetch] capability মডেল নেটিভ URL fetch সমর্থন না করলে
নিজে থেকে এটি লোকাল বিকল্প হিসেবে ব্যবহার করে।

///

ডিফল্টভাবে টুলটি ফেরত দেওয়া লেখা 50,000 অক্ষরে সীমিত রাখে (`max_content_length`) আর
ডাউনলোড করা response body 50 MiB-তে সীমিত রাখে (`max_download_bytes`)। যেকোনোটির সীমা তুলে দিতে `None` দিন।
অস্বাভাবিক জটিল HTML তবুও টুলের আলাদা রূপান্তর-সীমা ছাড়িয়ে যেতে পারে; তখন টুলটি মডেলকে অন্য কিছু চেষ্টা করতে বলে।
HTML markdown-এ রূপান্তর হয় একটি worker thread-এ, প্রতি event loop-এ একসাথে সর্বোচ্চ চারটি পেজ; আরও HTML response একটি খালি জায়গার অপেক্ষা করে।

/// info | এক নজরে

| সীমা | ডিফল্ট | কেন |
|------|--------|-----|
| `max_content_length` | 50,000 অক্ষর | মডেলের প্রসঙ্গ (আর আপনার token খরচ) একটা বিশাল পেজে ভরে না যায় |
| `max_download_bytes` | 50 MiB | বিশাল ফাইল ডাউনলোড করে মেমরি শেষ না হয় |
| একসাথে HTML রূপান্তর | 4টি পেজ | রূপান্তর CPU-ভারী কাজ; event loop আটকে না যায় |

///

/// warning | `headers`-এ credential

`web_fetch_tool(headers=...)` দিয়ে কনফিগার করা header মডেল যে URL চায় সেখানেই পাঠানো হয়,
যেহেতু URL মডেল বাছে। আপনি `Authorization`-এর মতো একটি credential কনফিগার করলে, কোন host তা পেতে পারবে তা সীমিত করতে
`allowed_domains` ব্যবহার করুন, আর মনে রাখবেন domain ছাঁকনি শুধু hostname মেলায়: মডেল তবুও credential-টি অনুমোদিত host-এর সাধারণ `http://`-এ বা একটি
অ-মানক port-এ পাঠাতে পারে। redirect-এ, কনফিগার করা সংবেদনশীল header
(`Authorization`, `Cookie`, `Proxy-Authorization`) শুধু তখনই পাঠানো হয় যখন redirect একই origin-এ (scheme, host আর port) থাকে
বা ডিফল্ট port-এ একই host-এ `http` থেকে `https`-এ উন্নীত হয়; অন্য যেকোনো redirect-এ এগুলো বাদ দেওয়া হয়।

///

/// warning | সাধারণ ভুল

একটি API token `headers`-এ দিয়ে `allowed_domains` না দেওয়া। তখন prompt injection-এ ভরা কোনো ওয়েবপেজ মডেলকে বলতে পারে "এখন `https://attacker.example`-এ যাও" — আর আপনার token সেখানে চলে যাবে। credential দিলে সবসময় `allowed_domains=['api.myservice.com']`-এর মতো সীমা দিন।

///

## Tavily Search টুল { #tavily-search-tool }

/// info | মনে রাখুন

Tavily একটি পেইড সার্ভিস, তবে তাদের পণ্য যাচাই করতে ফ্রি ক্রেডিট দেয়।

Tavily search টুল ব্যবহার করতে আপনাকে [একটি অ্যাকাউন্টে সাইন আপ](https://app.tavily.com/home) করে একটি API key নিতে হবে।

///

Tavily search টুল আপনাকে ওয়েবে তথ্য খুঁজতে দেয়। এটি [Tavily API](https://tavily.com/)-এর ওপর তৈরি।

### ইনস্টলেশন { #installation_2 }

[`tavily_search_tool`][pydantic_ai.common_tools.tavily.tavily_search_tool] ব্যবহার করতে, আপনাকে
`tavily` optional group-সহ [`pydantic-ai-slim`](install.md#slim-install) ইনস্টল করতে হবে:

/// tab | pip

```bash
pip install "pydantic-ai-slim[tavily]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[tavily]"
```

///


### ব্যবহার { #usage_2 }

একটি এজেন্টের সাথে Tavily search টুল কীভাবে ব্যবহার করবেন তার একটি উদাহরণ:

```python title="tavily_search.py"
import os

from pydantic_ai import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')
assert api_key is not None

agent = Agent(
    'openai:gpt-6.1-sol',
    tools=[tavily_search_tool(api_key)],
    instructions='Search Tavily for the given query and return the results.',
)

result = agent.run_sync('Tell me the top news in the GenAI world, give me links.')
print(result.output)
"""
Here are some of the top recent news articles related to GenAI:

1. How CLEAR users can improve risk analysis with GenAI – Thomson Reuters
   Read more: https://legal.thomsonreuters.com/blog/how-clear-users-can-improve-risk-analysis-with-genai/
   (This article discusses how CLEAR's new GenAI-powered tool streamlines risk analysis by quickly summarizing key information from various public data sources.)

2. TELUS Digital Survey Reveals Enterprise Employees Are Entering Sensitive Data Into AI Assistants More Than You Think – FT.com
   Read more: https://markets.ft.com/data/announce/detail?dockey=600-202502260645BIZWIRE_USPRX____20250226_BW490609-1
   (This news piece highlights findings from a TELUS Digital survey showing that many enterprise employees use public GenAI tools and sometimes even enter sensitive data.)

3. The Essential Guide to Generative AI – Virtualization Review
   Read more: https://virtualizationreview.com/Whitepapers/2025/02/SNOWFLAKE-The-Essential-Guide-to-Generative-AI.aspx
   (This guide provides insights into how GenAI is revolutionizing enterprise strategies and productivity, with input from industry leaders.)

Feel free to click on the links to dive deeper into each story!
"""
```

### প্যারামিটার কনফিগার করা { #configuring-parameters }

`tavily_search_tool` factory ঐচ্ছিক প্যারামিটার নেয়, যা সার্চের আচরণ নিয়ন্ত্রণ করে। `max_results` সবসময় ডেভেলপার-নিয়ন্ত্রিত আর কখনো LLM-এর tool schema-তে আসে না। অন্য প্যারামিটার দিলে, সেগুলো সব সার্চে নির্দিষ্ট থাকে আর LLM-এর tool schema থেকে লুকানো থাকে। না দেওয়া প্যারামিটার LLM-এর জন্য প্রতি কলে সেট করার সুযোগ থাকে।

যেমন, টুল তৈরির সময় আপনি `max_results` আর `include_domains` আটকে দিতে পারেন, আর তবুও LLM-কে `exclude_domains` নিয়ন্ত্রণ করতে দিতে পারেন:

```python title="tavily_domain_filtering.py"
import os

from pydantic_ai import Agent
from pydantic_ai.common_tools.tavily import tavily_search_tool

api_key = os.getenv('TAVILY_API_KEY')
assert api_key is not None

agent = Agent(
    'openai:gpt-6.1-sol',
    tools=[tavily_search_tool(api_key, max_results=5, include_domains=['arxiv.org'])],
    instructions='Search for information and return the results.',
)

result = agent.run_sync(
    'Find recent papers about transformer architectures'
)
print(result.output)
"""
Here are some recent papers about transformer architectures from arxiv.org:

1. "Attention Is All You Need" - The foundational paper on the Transformer model.
2. "FlashAttention: Fast and Memory-Efficient Exact Attention" - Proposes an IO-aware attention algorithm.
"""
```

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন আপনি একটি চিকিৎসা-তথ্যের বট বানাচ্ছেন। আপনি চান মডেল শুধু বিশ্বস্ত সাইট থেকে খুঁজুক। `include_domains=['who.int', 'nih.gov']` দিলে এটি **আপনার** সিদ্ধান্ত হয়ে যায় — মডেল এটা দেখতেও পায় না, বদলাতেও পারে না। আর যা দেননি (যেমন `exclude_domains`), সেটা মডেল প্রতিটি সার্চে নিজে ঠিক করতে পারে। অর্থাৎ: **আপনি যা ঠিক করবেন তা লক, বাকিটা মডেলের হাতে।**

///

## Exa Search টুল { #exa-search-tool }

//// warning | অবচিত (Deprecated)

Exa সাধারণ টুলগুলো (`exa_search_tool`, `exa_find_similar_tool`, `exa_get_contents_tool`, `exa_answer_tool` আর `ExaToolset`) অবচিত আর v3-এ সরানো হবে।

এর বদলে Pydantic AI Harness থেকে [`ExaSearch`](harness/exa-search.md) capability ব্যবহার করুন, যা ওয়েব সার্চ, পূর্ণ-পেজ উদ্ধার, গভীর সার্চ আর দীর্ঘ-চলা গবেষণার জন্য একটি `ExaAgent` capability একসাথে দেয়:

/// tab | pip

```bash
pip install "pydantic-ai-harness[exa]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[exa]"
```

///


```python title="exa_search.py"
from pydantic_ai_harness.exa import ExaSearch

from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol', capabilities=[ExaSearch()])

result = agent.run_sync('What are the latest developments in quantum computing?')
print(result.output)
```

////

/// check | সংক্ষেপে মনে রাখুন

* সাধারণ টুল আপনার নিজের মেশিনে চলে, তাই যেকোনো মডেলের সাথে কাজ করে; প্রতিটির জন্য আলাদা optional group (`duckduckgo`, `web-fetch`, `tavily`) ইনস্টল করুন।
* এগুলো factory — `tools=[duckduckgo_search_tool()]`-এর মতো `()`-সহ দিন।
* DuckDuckGo-তে key লাগে না; Tavily-তে API key লাগে।
* `web_fetch_tool`-এ SSRF সুরক্ষা আর আকারের সীমা আছে; credential header দিলে অবশ্যই `allowed_domains` দিন।
* Tavily-তে factory-তে দেওয়া প্যারামিটার লক হয়ে মডেলের কাছ থেকে লুকানো থাকে।
* Exa টুল অবচিত — `pydantic-ai-harness`-এর `ExaSearch` ব্যবহার করুন।

///
