
# Web Search { #web-search }

/// note | এই পেজে যা শিখবেন

* `WebSearch` capability — যেখানে পারে provider-এর নেটিভ web search, অন্যত্র একটি লোকাল বিকল্প (DuckDuckGo, Tavily, Exa বা নিজের টুল)।
* নেটিভ কনফিগারেশন ফিল্ড, আর কেন domain/`max_uses` সীমা দিলে লোকাল বিকল্প বন্ধ হয়।

///

[`WebSearch`][pydantic_ai.capabilities.WebSearch] [capability](overview.md) আপনার এজেন্টকে web search দেয়। সব [provider-অনুযায়ী টুলের](overview.md#provider-adaptive-tools) মতো, মডেল সমর্থন করলে এটি provider-এর নেটিভ web search ব্যবহার করে আর অন্য মডেলে একটি লোকাল বাস্তবায়নে ফিরে যেতে পারে।

[`WebSearch`][pydantic_ai.capabilities.WebSearch]-এর ডিফল্ট শুধু-নেটিভ। নেটিভ দিকে এর পেছনে আছে [`WebSearchTool`][pydantic_ai.native_tools.WebSearchTool] (provider সমর্থন আর কনফিগারেশনের জন্য দেখুন [Web Search Tool](../native-tools.md#web-search-tool)) — নেটিভ instance-এর ওপর পূর্ণ নিয়ন্ত্রণ দরকার হলে সরাসরি `native=WebSearchTool(...)` দিন।

লোকাল দিকের জন্য, একটি [DuckDuckGo](../common-tools.md#duckduckgo-search-tool) বিকল্পের জন্য `local='duckduckgo'` (বা `local=True`) দিন (`duckduckgo` optional group লাগে); অন্য সার্চ provider-এর জন্য, [`common_tools`](../common-tools.md) থেকে একটি [Tavily][pydantic_ai.common_tools.tavily.tavily_search_tool] wrapper, Pydantic AI Harness থেকে [`ExaSearchToolset`](../harness/exa-search.md), বা যেকোনো callable, [`Tool`][pydantic_ai.tools.Tool] বা [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] ব্যবহার করুন।

/// tip | উদাহরণ দিয়ে বুঝি

`WebSearch(local='duckduckgo')` একটি "দুই-স্তরের" সার্চ: Claude বা GPT-এর মতো নেটিভ-সার্চ মডেলে provider-এর নিজের সার্চ চলে (দ্রুত, উচ্চমানের); কিন্তু একটি লোকাল Ollama মডেলে, যার নেটিভ সার্চ নেই, এজেন্ট স্বয়ংক্রিয়ভাবে DuckDuckGo ব্যবহার করে। আপনার কোড একই থাকে, শুধু মডেল বদলান।

///

নেটিভ কনফিগারেশন ফিল্ড: `search_context_size`, `user_location`, `blocked_domains`, `allowed_domains`, `max_uses`, আর OpenAI Responses-এর `external_web_access`। domain আর `max_uses` সীমার জন্য এমন একটি নেটিভ web search লাগে যা এগুলো প্রয়োগ করে, যেমন লাগে `external_web_access=False`-এর জন্য, কারণ একটি লোকাল বিকল্প cache করা বা শুধু-index-করা সার্চ নিশ্চিত করতে পারে না। এমন একটি মডেলে যার নেটিভ সার্চ সেট করা একটি প্রয়োগ করতে পারে না (Gemini এর কোনোটিই প্রয়োগ করে না; দেখুন [restricting parameters](../native-tools.md#restricting-parameters)), `WebSearch` সীমা ছাড়া সার্চ না করে একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে।

`WebSearch`-এ নিজেই এই ফিল্ড সেট করলে `local` বিকল্প বন্ধ হয়, কারণ বান্ডেল করা লোকাল টুল এগুলো প্রয়োগ করতে পারে না। এমন মডেলে নিজেই সীমা প্রয়োগ করে এমন একটি লোকাল সার্চে ফিরে যেতে, এর বদলে সীমাটি নেটিভ টুলে রাখুন:

```python title="web_search_restricted_fallback.py"
from pydantic_ai.capabilities import WebSearch
from pydantic_ai.native_tools import WebSearchTool


def search_pydantic_docs(query: str) -> str:
    """Search pydantic.dev only."""
    return f'pydantic.dev results for {query}'


web_search = WebSearch(native=WebSearchTool(allowed_domains=['pydantic.dev']), local=search_pydantic_docs)
```

```python title="web_search.py"
from pydantic_ai.capabilities import WebSearch

# Native-only — raises on models without native web search
WebSearch()

# Native preferred; DuckDuckGo fallback (needs `pydantic-ai-slim[duckduckgo]`)
WebSearch(local='duckduckgo')

# Native preferred; custom callable as fallback
def my_search(query: str) -> str: ...
WebSearch(local=my_search)
```

/// warning | সাধারণ ভুল

`WebSearch(allowed_domains=['docs.python.org'], local='duckduckgo')` লিখে ভাবা যে Gemini-তে DuckDuckGo দিয়ে শুধু ওই domain-এ খোঁজা হবে। capability-তে সীমা দিলে লোকাল বিকল্প বন্ধ হয়ে যায় আর Gemini-তে `UserError` ওঠে। ওপরের উদাহরণের মতো সীমাটি `native=WebSearchTool(allowed_domains=...)`-এ রাখুন, আর নিজে সীমা প্রয়োগ করে এমন একটি লোকাল টুল দিন।

///

/// check | সংক্ষেপে মনে রাখুন

* `WebSearch()` ডিফল্টভাবে শুধু-নেটিভ; `local='duckduckgo'` বা নিজের টুল দিয়ে বিকল্প।
* domain/`max_uses`/`external_web_access=False` সীমা নেটিভ সার্চে প্রয়োগ হয় — না পারলে `UserError`, সীমা ছাড়া সার্চ নয়।
* capability-তে সীমা দিলে লোকাল বিকল্প বন্ধ; বিকল্প চাইলে সীমা নেটিভ টুলে রাখুন।

///
