
# Web Fetch { #web-fetch }

/// note | এই পেজে যা শিখবেন

* `WebFetch` capability দিয়ে এজেন্টকে URL-এর কনটেন্ট আনতে দেওয়া — নেটিভ টুল পছন্দ, অন্যত্র লোকাল বিকল্প।
* কোন সীমা লোকালেও প্রয়োগ হয় আর কোনটির জন্য নেটিভ লাগে।

///

[`WebFetch`][pydantic_ai.capabilities.WebFetch] [capability](overview.md) আপনার এজেন্টকে URL-এর কনটেন্ট আনতে দেয়। সব [provider-অনুযায়ী টুলের](overview.md#provider-adaptive-tools) মতো, এটি provider-এর নেটিভ web fetch টুল পছন্দ করে আর অন্য মডেলে একটি লোকাল বাস্তবায়নে ফিরে যেতে পারে।

[`WebFetch`][pydantic_ai.capabilities.WebFetch]-এর ডিফল্ট শুধু-নেটিভ। নেটিভ দিকে এর পেছনে আছে [`WebFetchTool`][pydantic_ai.native_tools.WebFetchTool] (provider সমর্থন আর কনফিগারেশনের জন্য দেখুন [Web Fetch Tool](../native-tools.md#web-fetch-tool)) — পূর্ণ নিয়ন্ত্রণের জন্য সরাসরি `native=WebFetchTool(...)` দিন।

লোকাল দিকের জন্য, বান্ডেল করা [markdownify-ভিত্তিক fetch টুলের](../common-tools.md#web-fetch-tool) জন্য `local=True` দিন (`web-fetch` optional group লাগে), বা যেকোনো callable, [`Tool`][pydantic_ai.tools.Tool] বা [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset]।

নেটিভ সীমার ফিল্ড: `allowed_domains`, `blocked_domains`, `max_uses`, `enable_citations`, `max_content_tokens`। শুধু `max_uses`-এর জন্য নেটিভ লাগে; নেটিভ উপলব্ধ না থাকলে, বা মডেলের নেটিভ web fetch এগুলো প্রয়োগ করতে না পারলে (Gemini-এর URL context এর কোনোটিই প্রয়োগ করে না), domain ছাঁকনি লোকালে প্রয়োগ হয়।

```python title="web_fetch.py"
from pydantic_ai.capabilities import WebFetch

# Native-only — raises on models without native web fetch
WebFetch()

# Native preferred; markdownify-based fallback (needs `pydantic-ai-slim[web-fetch]`)
WebFetch(local=True)

# Domain filters enforced locally when native isn't available
WebFetch(allowed_domains=['example.com'], local=True)
```

/// info | এক নজরে: WebSearch বনাম WebFetch-এ সীমা

| সীমা | `WebSearch` | `WebFetch` |
|------|-------------|------------|
| `allowed_domains` / `blocked_domains` | শুধু নেটিভে (নইলে `UserError`) | নেটিভে, না পারলে লোকালে প্রয়োগ |
| `max_uses` | শুধু নেটিভে | শুধু নেটিভে |

///

/// check | সংক্ষেপে মনে রাখুন

* `WebFetch()` ডিফল্টভাবে শুধু-নেটিভ; `local=True` দিয়ে markdownify-ভিত্তিক লোকাল fetch (`web-fetch` extra)।
* domain ছাঁকনি লোকালেও প্রয়োগ হয়; শুধু `max_uses`-এর জন্য নেটিভ লাগে।

///
