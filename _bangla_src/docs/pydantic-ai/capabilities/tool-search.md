
# Tool Search { #tool-search }

/// note | এই পেজে যা শিখবেন

* `ToolSearch` capability কীভাবে বড় toolset থেকে মডেলকে শুধু দরকারি tool খুঁজে নিতে দেয়।
* native search বনাম local `search_tools`, আর `strategy` বাছাই।
* retry budget কীভাবে কাজ করে।

///

[`ToolSearch`][pydantic_ai.capabilities.ToolSearch] [capability](overview.md) `defer_loading=True` চিহ্নিত খোঁজযোগ্য tool-গুলোর মডেল-চালিত আবিষ্কার সামলায়, তাই বড় toolset-ওয়ালা agent শুধু মডেলের দরকারি tool-গুলোর জন্যই token খরচ করে। ওপরের [provider-adaptive tools](overview.md#provider-adaptive-tools)-এর মতো, এটি সক্রিয় মডেলের জন্য সেরা পথ বাছে — Anthropic আর OpenAI Responses-এ native server-চালিত search, অন্য জায়গায় একটি local `search_tools` function tool — আর খোঁজযোগ্য deferred tool থাকলে প্রতিটি agent-এ স্বয়ংক্রিয়ভাবে যুক্ত হয়। bundle-স্তরের প্রকাশ আলোচনা করা হয়েছে [on-demand capabilities](on-demand.md)-এ।

এটি ডিফল্ট `id` হিসেবে `'tool_search'` ঘোষণা করে, তাই দুটি instance ডুপ্লিকেট-id error না দিয়ে মিশে একটি হয় — মেশানোর নিয়মের জন্য দেখুন [building custom capabilities](custom.md)।

একটি নির্দিষ্ট [`strategy`][pydantic_ai.capabilities.ToolSearch.strategy] (`'keywords'`, `'bm25'`, `'regex'`, বা একটি কাস্টম callable) বাছতে বা local fallback ঠিকঠাক করতে একটি স্পষ্ট [`ToolSearch`][pydantic_ai.capabilities.ToolSearch] দিন:

```python title="tool_search_capability.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import ToolSearch

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[ToolSearch(strategy='keywords')])
```

local `search_tools` function tool ব্যবহার হলে, এর retry budget agent-এর tool budget অনুসরণ করে — তাই `Agent(retries={'tools': N})` মডেলকে একটি ভুল-গঠনের `queries` argument শোধরাতে `N`টি চেষ্টা দেয়, অন্য যেকোনো tool-এর মতো একই [precedence ladder](../tools-advanced.md#which-retry-limit-wins)-এ। কোনো মিল না পাওয়া search স্বাভাবিকভাবে ফেরত আসে আর কখনো retry খরচ করে না।

কখন এটি বেছে নেবেন, পুরো strategy তালিকা আর provider সাপোর্টের বিস্তারিত জানতে দেখুন [Tool Search](../tools-advanced.md#tool-search)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বিশাল লাইব্রেরিতে সব বই টেবিলে ছড়িয়ে রাখলে (সব tool-এর বর্ণনা প্রতি request-এ পাঠালে) জায়গা আর সময় দুটোই নষ্ট। `ToolSearch` হলো লাইব্রেরির ক্যাটালগ: মডেল আগে "ইমেইল পাঠানো" লিখে খোঁজে, তারপর শুধু সেই বইটিই (tool-টি) টেবিলে আসে।

///

/// check | সংক্ষেপে মনে রাখুন

* tool-এ `defer_loading=True` দিলে `ToolSearch` নিজে থেকেই যুক্ত হয় — আলাদা করে কিছু লাগে না।
* Anthropic আর OpenAI Responses-এ native search, বাকি সবখানে local `search_tools`।
* নির্দিষ্ট `strategy` (`'keywords'`, `'bm25'`, `'regex'`, কাস্টম) চাইলে স্পষ্টভাবে `ToolSearch(...)` দিন।
* মিল না পাওয়া search retry খরচ করে না; ভুল `queries` argument agent-এর tool retry budget খরচ করে।

///
