# থার্ড-পার্টি টুল { #third-party-tools }

/// note | এই পেজে যা শিখবেন

* অন্য লাইব্রেরির (LangChain, MCP) আগে থেকে তৈরি টুল কীভাবে Pydantic AI এজেন্টে ব্যবহার করবেন।
* একটি LangChain টুল `tool_from_langchain` দিয়ে, আর অনেকগুলো একসাথে `LangChainToolset` দিয়ে।
* কেন এক্ষেত্রে আর্গুমেন্ট যাচাই Pydantic AI করে না।

///

Pydantic AI বিভিন্ন থার্ড-পার্টি টুল লাইব্রেরির সাথে ইন্টিগ্রেশন সমর্থন করে, যাতে আপনি এজেন্টে বিদ্যমান টুলের ইকোসিস্টেম কাজে লাগাতে পারেন। থার্ড-পার্টি টুল [capability](capabilities/third-party.md) হিসেবেও পাওয়া যায় — পুরো ইকোসিস্টেমের জন্য দেখুন [Extensibility](extensibility.md)।

/// tip | উদাহরণ দিয়ে বুঝি

চাকা নতুন করে আবিষ্কার করার দরকার নেই। LangChain-এর কমিউনিটি শত শত টুল বানিয়ে রেখেছে (Wikipedia, ArXiv, বিভিন্ন API)। Pydantic AI এগুলোকে একটা "অ্যাডাপ্টার" দিয়ে নিজের টুলে বদলে নেয় — অনেকটা বিদেশি প্লাগে কনভার্টার লাগানোর মতো।

///

## MCP টুল { #mcp-tools }

Pydantic AI-তে MCP সার্ভারকে [toolset](toolsets.md) হিসেবে কীভাবে ব্যবহার করবেন তা জানতে দেখুন [MCP Client](./mcp/client.md) ডকুমেন্টেশন।

## LangChain টুল { #langchain-tools }

আপনি যদি LangChain-এর [community tool library](https://python.langchain.com/docs/integrations/tools/) থেকে একটি টুল Pydantic AI-তে ব্যবহার করতে চান, তবে [`tool_from_langchain`][pydantic_ai.ext.langchain.tool_from_langchain] সুবিধাজনক মেথডটি ব্যবহার করতে পারেন। মনে রাখবেন, এক্ষেত্রে Pydantic AI আর্গুমেন্ট যাচাই করবে না -- LangChain টুলের দেওয়া schema-র সাথে মেলে এমন আর্গুমেন্ট দেওয়া মডেলের দায়িত্ব, আর আর্গুমেন্ট অবৈধ হলে এরর তোলা LangChain টুলের দায়িত্ব।

আপনাকে `langchain-community` প্যাকেজ আর সংশ্লিষ্ট টুলের দরকারি অন্য যেকোনো প্যাকেজ ইনস্টল করতে হবে।

LangChain-এর `DuckDuckGoSearchRun` টুল কীভাবে ব্যবহার করবেন তা এখানে দেখানো হলো, যার জন্য `ddgs` প্যাকেজ লাগে:

```python
from langchain_community.tools import DuckDuckGoSearchRun

from pydantic_ai import Agent
from pydantic_ai.ext.langchain import tool_from_langchain

search = DuckDuckGoSearchRun()
search_tool = tool_from_langchain(search)

agent = Agent(
    'google:gemini-3.8-flash',
    tools=[search_tool],
)

result = agent.run_sync('What is the release date of Elden Ring Nightreign?')  # (1)!
print(result.output)
#> Elden Ring Nightreign is planned to be released on May 30, 2025.
```

1. এই গেমের মুক্তির তারিখ 30 মে 2025, যা Gemini 2.0-এর knowledge cutoff (আগস্ট 2024)-এর পরে।

/// info | কোডটি সহজ ভাষায়

* LangChain টুলটি স্বাভাবিকভাবে তৈরি করা হয়, তারপর `tool_from_langchain(...)` একে Pydantic AI-এর একটি `Tool`-এ মোড়ায়।
* প্রশ্নটি ইচ্ছে করে এমন একটি ঘটনা নিয়ে, যা মডেলের প্রশিক্ষণের পরে ঘটেছে — তাই মডেল নিজে জানে না, তাকে সার্চ টুল ব্যবহার করতেই হবে।
* টুলের নাম, বর্ণনা আর আর্গুমেন্টের schema LangChain টুল থেকেই আসে।

///

/// warning | সাধারণ ভুল

ধরে নেওয়া যে মডেল ভুল আর্গুমেন্ট দিলে Pydantic AI নিজে থেকে [retry](tools-advanced.md#tool-retries) করাবে, যেমন সাধারণ ফাংশন টুলে হয়। এখানে যাচাই হয় না — ভুল আর্গুমেন্ট সরাসরি LangChain টুলে যায়, আর সেটি কীভাবে আচরণ করবে তা ওই টুলের ওপর নির্ভর করে।

///

একাধিক LangChain টুল বা একটি LangChain [toolkit](https://python.langchain.com/docs/concepts/tools/#toolkits) ব্যবহার করতে চাইলে, আপনি [`LangChainToolset`][pydantic_ai.ext.langchain.LangChainToolset] [toolset](toolsets.md) ব্যবহার করতে পারেন, যা LangChain টুলের একটি লিস্ট নেয়:

```python
from langchain_community.agent_toolkits import SlackToolkit

from pydantic_ai import Agent
from pydantic_ai.ext.langchain import LangChainToolset

toolkit = SlackToolkit()
toolset = LangChainToolset(toolkit.get_tools())

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
# ...
```

## আরও দেখুন { #see-also }

- [ফাংশন টুল](tools.md) - টুলের মৌলিক ধারণা আর রেজিস্ট্রেশন
- [Toolsets](toolsets.md) - টুলের সংগ্রহ পরিচালনা
- [MCP Client](mcp/client.md) - Pydantic AI-তে MCP সার্ভার ব্যবহার
- [LangChain Toolsets](toolsets.md#langchain-tools) - LangChain toolset ব্যবহার

/// check | সংক্ষেপে মনে রাখুন

* একটি LangChain টুল: `tool_from_langchain(lc_tool)`; অনেকগুলো বা একটি toolkit: `LangChainToolset([...])`।
* `langchain-community` আর টুলের নিজস্ব dependency আলাদা করে ইনস্টল করতে হয়।
* আর্গুমেন্ট যাচাই Pydantic AI করে না — দায়িত্ব মডেল আর LangChain টুলের।
* MCP সার্ভারের টুলের জন্য [MCP Client](mcp/client.md) দেখুন।

///
