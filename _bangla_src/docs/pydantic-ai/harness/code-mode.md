
# Code Mode { #code-mode }

/// note | এই পেজে যা শিখবেন

* `CodeMode` কীভাবে অনেকগুলো আলাদা tool call-কে একটি sandbox-এ চলা Python program-এ পরিণত করে।
* কোন tool sandbox-এ যাবে তা বাছাই (selector, metadata) আর Tool Search-এর সাথে সম্পর্ক।
* return value, সীমা (সময়, memory, suspension, nested tool call), সমান্তরাল call আর REPL state।
* eager আর speculative execution, remote worker, Temporal, observability।
* filesystem/OS প্রবেশাধিকার (`mount`, `os_access`) আর sandbox-এর বিধিনিষেধ।

///

`CodeMode` আলাদা আলাদা tool call-এর জায়গায় একটিমাত্র sandbox-এ ঘেরা Python execution environment বসায়। মডেল প্রতিটি কাজের জন্য একটি করে tool call না দিয়ে একটি Python program লেখে, যা আপনার tool-গুলোকে function হিসেবে ডাকে — loop, শর্ত, variable আর `asyncio.gather`-সহ — সবকিছু একটি sandbox-এ ঘেরা [Monty](https://github.com/pydantic/monty) runtime-এর ভেতরে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/code_mode/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

প্রচলিত tool calling-এ প্রায়ই প্রতিটি নির্ভরশীল tool call ব্যাচের জন্য আরেকটি model turn লাগে। যে agent-কে 10টি item আনতে হবে আর তারপর সেগুলোর ফল প্রসেস করতে হবে, তার অনেকগুলো model turn লাগতে পারে — এতে latency, খরচ আর context ব্যবহার বাড়ে। মধ্যবর্তী ফলগুলোও কথোপকথনের history বড় করে।

## সমাধান { #the-solution }

`CodeMode` যোগ্য tool-গুলোকে একটিমাত্র `run_code` tool-এ মুড়ে দেয়। মডেল sandbox-এ চলা সমন্বয়-কোড লেখে, যা `asyncio.gather` দিয়ে call ছড়িয়ে দেয়, ফল ছাঁকে আর রূপান্তর করে, আর শুধু দরকারি অংশটুকু ফেরত দেয়। ওই কোড থেকে আসা call-গুলো Pydantic AI-এর মাধ্যমে host tool-এ পাঠানো হয়।

| প্রচলিত tool calling | Code mode |
|---|---|
| নির্ভরশীল tool ব্যাচ একাধিক model turn জুড়ে | একটি `run_code`-এ অনেকগুলো নির্ভরশীল call |
| সমান্তরাল শুধু মডেল একটি ব্যাচ দিলে | সমান্তরালতা Python-এ প্রকাশ করা |
| কোনো local হিসাব নেই | কোডে ছাঁকা, রূপান্তর, একত্রীকরণ |
| বড় কথোপকথন history | সংক্ষিপ্ত — কম message |

durable execution integration নির্ধারিত (deterministic) replay-এর জন্য nested call রেকর্ড করতে পারে।

/// tip | উদাহরণ দিয়ে বুঝি

দোকানে ফোন করে একবার "চাল আছে?", আবার "ডাল আছে?", আবার "দাম কত?" — প্রতিটি প্রশ্ন একটি model turn। Code Mode হলো পুরো বাজারের ফর্দ (script) একবারে পাঠিয়ে দেওয়া: "সব জিনিস একসাথে দেখো, দাম যোগ করো, শুধু মোট বিলটা জানাও।" মাঝের সব খুঁটিনাটি দোকানেই থাকে, আপনার কাছে আসে শুধু চূড়ান্ত ফল।

///

## ইনস্টলেশন { #installation }

Code mode-এর জন্য Monty sandbox লাগে, যা `codemode` extra দিয়ে পাওয়া যায় (`code-mode` extra-টি এর সমতুল্য alias):

/// tab | pip

```bash
pip install "pydantic-ai-harness[codemode]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[codemode]"
```

///


## ব্যবহার { #usage }

`capabilities`-এ `CodeMode()` দিয়ে একটি `Agent` তৈরি করুন, তারপর স্বাভাবিকভাবে tool রেজিস্টার করুন। প্রতিটি যোগ্য সাধারণ tool `run_code`-এর ভেতর থেকে ডাকা যায়:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[CodeMode()])


@agent.tool_plain
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {'city': city, 'temp_f': 72, 'condition': 'sunny'}


result = agent.run_sync("What's the weather in Paris and Tokyo, in Celsius?")
print(result.output)
```

একটিমাত্র `run_code` call-এর ভেতরে মডেল নিচের মতো কোড লেখে (উদাহরণমাত্র — মডেল ঠিক কোন কোড লিখবে তা বদলাবে):

```python
import asyncio

paris, tokyo = await asyncio.gather(
    get_weather(city='Paris'),
    get_weather(city='Tokyo'),
)
paris_c = round((paris['temp_f'] - 32) * 5 / 9, 1)
tokyo_c = round((tokyo['temp_f'] - 32) * 5 / 9, 1)
{'paris': paris_c, 'tokyo': tokyo_c}
```

দুটি আবহাওয়া খোঁজ সমান্তরালে চলে আর রূপান্তরগুলো Monty-র ভেতরে চলে, সবই একটি `run_code` call-এর মধ্যে।

/// info | কোডটি সহজ ভাষায়

| লাইন | কী ঘটে |
|---|---|
| `await asyncio.gather(get_weather(...), get_weather(...))` | Paris আর Tokyo-র আবহাওয়া একসাথে আনা — host-এর দুটি tool call |
| `round((... - 32) * 5 / 9, 1)` | Fahrenheit থেকে Celsius — sandbox-এর ভেতরেই হিসাব |
| শেষ লাইনের dict | শুধু এটিই মডেলের কাছে `run_code`-এর ফল হিসেবে ফেরে |

///

## বাছাই করে tool sandbox-এ নেওয়া { #selective-tool-sandboxing }

ডিফল্টভাবে `CodeMode(tools='all')` প্রতিটি যোগ্য সাধারণ tool sandbox-এ নেয়। framework-এর control tool, এখনও খুঁজে-না-পাওয়া deferred tool, native fallback আর অন্যান্য code-execution tool native-ই থাকে। shell-এর tool-গুলো code-execution tool হিসেবে গণ্য: `Shell`-এর `run_command` আর `start_command` `run_code`-এর ভেতরে নয়, পাশে বসে — তাই মডেলকে কখনো তৈরি করা Python string-এর ভেতরে shell command quote করতে হয় না। `CapabilityCreation`-এর `author_capability`-ও একই কারণে native থাকে: এর argument একটি সম্পূর্ণ Python module। এদের command-নয় এমন tool (`read_file`, `check_command` ইত্যাদি) অন্য যেকোনো tool-এর মতো `run_code`-এ ঢুকে যায়। `tools` field একটি Pydantic AI `ToolSelector`, তাই কোন যোগ্য tool sandbox দিয়ে যাবে তা আপনি নিয়ন্ত্রণ করতে পারেন। selector-এর সাথে মেলা tool `run_code`-এর ভেতরে callable হয়; না-মেলা tool মডেলের কাছে সাধারণ tool call হিসেবে দৃশ্যমান থাকে।

```python
from pydantic_ai_harness import CodeMode

# By name -- only these tools are available inside run_code
CodeMode(tools=['search', 'fetch'])

# By predicate -- (ctx, tool_def) -> bool | Awaitable[bool]
CodeMode(tools=lambda ctx, td: td.name != 'dangerous_tool')

# By metadata -- combine with SetToolMetadata or a toolset's .with_metadata()
CodeMode(tools={'code_mode': True})
```

### Metadata-ভিত্তিক বাছাই { #metadata-based-selection }

সিদ্ধান্তটি যখন একটি `CodeMode` instance-এর সাথে নয়, বরং একটি tool বা toolset-এর সাথেই চলা উচিত, তখন metadata ব্যবহার করুন। শেয়ার করা toolset-এর জন্য এটি মানানসই: toolset-এর লেখক সেই tool-গুলোতে tag দেন যেগুলো তৈরি করা কোড থেকে ডাকা নিরাপদ ও কাজের, আর প্রতিটি agent `CodeMode(tools={...})` দিয়ে সেই tag বেছে নেয়।

`CodeMode(tools={'code_mode': True})` প্রচলিত Pydantic AI [`ToolSelector`](../api/tools.md) metadata রূপ ব্যবহার করে। একটি tool sandbox-এ যায় যখন তার `ToolDefinition.metadata`-তে selector-এর সব key-value জোড়া থাকে। tool-এ বাড়তি metadata থাকলে সমস্যা নেই, আর নেস্টেড dictionary গভীর অন্তর্ভুক্তি (deep inclusion) দিয়ে মেলানো হয়।

প্রচলিত pattern হলো `.with_metadata(...)` দিয়ে পুরো একটি toolset-এ tag দেওয়া:

```python
from pydantic_ai import Agent
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai_harness import CodeMode


def search(query: str) -> str:
    """Search the web."""
    return f'results for {query}'


def fetch(url: str) -> str:
    """Fetch a URL."""
    return f'contents of {url}'


search_tools = FunctionToolset(tools=[search, fetch]).with_metadata(code_mode=True)

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    toolsets=[search_tools],
    capabilities=[CodeMode(tools={'code_mode': True})],
)
```

এখানে `search` আর `fetch` মডেলের সামনের tool তালিকা থেকে সরে যায় আর `run_code`-এর ভেতরে callable function হয়ে যায়। যে tool-গুলোর `metadata['code_mode'] == True` নেই, সেগুলো সাধারণ tool call হিসেবে দৃশ্যমান থাকে।

## Tool Search-এর সাথে সম্পর্ক { #tool-search-interaction }

tool বা পুরো toolset-কে `defer_loading=True` ([Tool Search](../tools-advanced.md#tool-search)) চিহ্নিত করলে, খুঁজে না পাওয়া পর্যন্ত `CodeMode` সেগুলোকে `run_code`-এর বাইরে রাখে — সেগুলো সরাসরি পার হয়ে যায়, তাই Tool Search স্বাভাবিকভাবেই সেগুলো চালায় (native tool search-ওয়ালা provider-এ `defer_loading`-সহ wire-এ পাঠানো হয়; অন্যথায় খুঁজে পাওয়া পর্যন্ত বাদ রাখা হয়, `run_code`-এর পাশে একটি `search_tools` tool-সহ)। ওই প্রকাশ-অবস্থা অনুসরণ করতে `CodeMode` `RunContext.is_tool_available` ব্যবহার করে। মডেল একটি tool খুঁজে পেলে — বা যে deferred capability সেটির মালিক তা লোড করলে — তখন থেকে `CodeMode` সেটিকে অন্য যেকোনো tool-এর মতো `run_code`-এ ঢুকিয়ে নেয়, তাই তৈরি করা কোড থেকে সেটি ডাকা যায়। (tool-টি `defer_loading=True` রাখে, যা এর লেখক কী চেয়েছিলেন তা রেকর্ড করে; বদলায় শুধু run-এর জন্য এর প্রাপ্যতা।)

ওই ঢুকিয়ে নেওয়া `run_code`-এর বর্ণনা বড় করে, যা খুঁজে পাওয়ার মুহূর্তে একবার prompt-cache prefix অকেজো করে (খুঁজে-না-পাওয়া turn-গুলো cache-উষ্ণ থাকে)। এই ভাঙন এড়ানোর দুটি উপায়:

- খুঁজে পাওয়াগুলো কথোপকথন নতুন করে না লিখে শেষে জুড়ে দিতে `dynamic_catalog=True` দিন। sandbox-এ নেওয়া tool-এর signature-এর catalog `run_code`-এর বর্ণনা থেকে সরে agent instructions-এ যায়, একটি dynamic [`InstructionPart`][pydantic_ai.messages.InstructionPart] হিসেবে, id `toolset:code_mode:catalog` আর [`on_change='append'`](../agent.md#appending-instruction-changes)-সহ: খুঁজে পাওয়া একটি function যোগ করলে হালনাগাদ catalog message history-তে শেষে জুড়ে দেওয়া হয়। Tool Search tool-টি খুঁজে পেলে, [`ctx.enqueue`][pydantic_ai.tools.RunContext.enqueue] দিয়ে পাঠানো একটি ছোট system prompt part-ও নতুন function-গুলোর নাম বলে; capability লোড করলে শুধু catalog আপডেট জুড়ে দেওয়া হয়। যে deferred tool-গুলো `run_code` নিয়ে নেবে, খুঁজে না পাওয়া পর্যন্ত সেগুলো wire-এ পাঠানো হয় না: মডেল এগুলো খুঁজে পায় local `search_tools` tool দিয়ে, বা যে capability এগুলোর মালিক তা লোড করে, আর তখন থেকে শুধু `run_code` থেকেই ডাকে। আগের request-গুলোর tool definition আর instructions যেমন পাঠানো হয়েছিল তেমনই থাকে, তাই খুঁজে পাওয়ার পরেও prompt cache টিকে থাকে:

  ```python
  from pydantic_ai_harness import CodeMode

  CodeMode(dynamic_catalog=True)
  ```

  catalog tool definition-গুলোকে instructions-এ render করে, একটি MCP server যে নাম, বর্ণনা আর schema দেয় সেগুলোসহ। tool definition হলো বিশ্বস্ত operator কনফিগারেশন: মডেল এগুলো আগে থেকেই request-এর tool definition-এ একই কর্তৃত্বে পায়, তাই instructions-এ সরানো এগুলোকে নতুন কোনো কর্তৃত্ব দেয় না। শুধু বিশ্বস্ত MCP server যুক্ত করুন। খুঁজে পাওয়ার ঘোষণা function-গুলোর নাম বলে শুধু তাদের Python identifier দিয়ে, আর tool-এর নাম রাখে তার metadata-তে যেমন পাওয়া গেছে।

  cache অক্ষত থাকে শুধু তখনই, যখন একটি callable `tools` selector একটি tool প্রকাশের আগে আর পরে একই উত্তর দেয়। যে selector একটি লুকানো tool-কে native রাখে আর প্রকাশের পর sandbox-এ নেয়, সেটি tool-টি ঘোষণা করে তারপর ঘোষণা বাদ দেয় — এতে cache করা prefix সরে যায়, `dynamic_catalog` ছাড়া যেমন হতো।

  catalog block-এর key হলো toolset id `code_mode`, যা `CodeModeToolset` নেয় শুধু `dynamic_catalog=True` থাকলে। agent-এ `code_mode` id-ওয়ালা আরেকটি toolset থাকলে যেটি instructions দেয়, তাহলে ডুপ্লিকেট id-র জন্য run একটি `UserError` raise করে। ওই toolset-এর নাম বদলান।

  দুটি সেটআপ এমন tool-কে তবুও native-ভাবে ঘোষণা করে, কারণ সেখানে শুধু provider-এর native tool search সেটি খুঁজে পেতে পারে: `'bm25'` আর `'regex'` Tool Search strategy, যাদের কোনো local `search_tools` নেই; আর এমন একটি `tools` selector যা অন্য একটি deferred tool-কে native রাখে, যা `search_tools`-এর বদলে native search wire-এ রাখে। ওই সেটআপগুলোতে tool `run_code`-এ গেলে ঘোষণা বাদ পড়ে, `dynamic_catalog` ছাড়া যেমন হয়।

  এটি লাভজনক Tool Search বা deferred capability-র সাথে, বড় system prompt-এর বিনিময়ে। স্থির toolset-এর ক্ষেত্রে ডিফল্টটি system prompt ছোট রাখে আর সেটিই ভালো বাছাই।

- বরং একটি Tool Search corpus পুরোপুরি native রাখতে — কখনো `run_code`-এ ঢোকানো হবে না, কিন্তু এর ভেতর থেকে ডাকাও যাবে না — একটি `tools` selector দিয়ে বাদ দিন; corpus-এর সদস্যরা `with_native` বহন করে, যা পরিচালনাকারী native tool-এ সেট করা:

  ```python
  from pydantic_ai_harness import CodeMode

  CodeMode(tools=lambda ctx, td: td.with_native is None)
  ```

/// info | এক নজরে: deferred tool আর Code Mode

| অবস্থা | ডিফল্ট | `dynamic_catalog=True` |
|---|---|---|
| খুঁজে পাওয়ার আগে | `run_code`-এর বাইরে, Tool Search চালায় | wire-এ নেই; local `search_tools` দিয়ে খোঁজা |
| খুঁজে পাওয়ার পরে | `run_code`-এ ঢোকে, বর্ণনা বড় হয় → cache একবার ভাঙে | catalog আপডেট history-তে জুড়ে যায় → cache টিকে থাকে |
| খরচ | ছোট system prompt | বড় system prompt |

///

## Return value { #return-values }

snippet-এর শেষ expression স্বয়ংক্রিয়ভাবে return value হিসেবে ধরা হয় — মডেলকে `print()` করতে হয় না। একটি assignment REPL-এ মান রাখে কিন্তু ফেরত দেয় না। যে শেষ expression `None` হয়, সেটিও কোনো ফল নয় বলে ধরা হয়। `None`-নয় এমন শেষ expression বা print output না থাকলে `run_code` `{}` ফেরত দেয়। assign করা নামটি শেষ লাইনে রাখুন:

```python
result = await get_weather(city='Paris')
result
```

`print()` রাখুন পরিপূরক logging-এর জন্য: print করা text আলাদাভাবে দেখানো হয়, শেষ-expression-এর ফলের পাশে মোড়া অবস্থায়।

| পরিস্থিতি | ফেরত |
|---|---|
| `None`-নয় শেষ expression, কোনো print output নেই | শেষ expression-এর মান |
| শেষে assignment বা `None` ফল, কোনো print output নেই | `{}` |
| print output আছে, শেষ expression নেই বা `None` ফল | `{'output': '<printed text>'}` |
| print output আছে, সাথে সাধারণ, `None`-নয় শেষ expression | `{'output': '<printed text>', 'result': <last expression>}` |
| multimodal শেষ expression, কোনো print output নেই | মডেলের প্রসেসিংয়ের জন্য native-ভাবে ফেরত |
| print output আছে, সাথে multimodal শেষ expression | print করা text, তারপর native multimodal content — একটি list |

print করা output 10 MiB-এ সীমিত। সীমা ছাড়ালে `run_code` একটি model retry ফেরত দেয়।

/// warning | সাধারণ ভুল

`result = await get_weather(city='Paris')` লিখে থেমে গেলে মডেল পায় `{}` — কারণ assignment কিছু ফেরত দেয় না। শেষ লাইনে শুধু `result` লিখুন (ওপরের কোডের মতো)।

///

sandbox execution `resource_limits` দিয়ে সীমায় বাঁধা, যার ডিফল্ট 30 সেকেন্ড execution সময়
আর একটি 256 MiB heap। `max_duration_secs` প্রতিটি `run_code` snippet-এ প্রযোজ্য: প্রতিটি snippet সর্বোচ্চ ততটুকুই
sandbox সময় পায়, আর এটিই নিয়ন্ত্রণহীন loop থামায়। nested tool-এর জন্য await করার সময়
বাদ যায়। সীমায় পৌঁছানো snippet থামানো হয় আর তার session reset হয়, তাই যেকোনো variable,
import আর definition আবার তৈরি করতে হয়। `run_code` যে retry ফেরত দেয় তা এটি জানায়, আর
snippet ইতিমধ্যে যে nested call করেছে সেগুলোর বিবরণ দেয়।

ঘুমানো (sleep) execution সময় নয়, তাই এর নিজের একই দৈর্ঘ্যের ভাতা আছে: একটি snippet মোট সর্বোচ্চ
`max_duration_secs` ঘুমাতে পারে। যে sleep এটি ছাড়িয়ে যেত, সেটি অপেক্ষা না করেই sandbox-এ `TimeoutError` raise করে,
আর session রাখা হয়। এই ভাতা Temporal workflow-এর ভেতরেও প্রযোজ্য, যেখানে execution-সময়ের সীমা বন্ধ;
শুধু `resource_limits='unlimited'` এটি সরায়।

Monty `max_suspensions` দিয়ে মোট suspension-ও সীমিত করে (ডিফল্ট প্রতি session-এ 1,000)।
বাইরের call, OS callback, নাম খোঁজা আর future resolution — প্রতিটি এই budget খরচ করে, তাই
এটি tool-call গণনা নয়। পরপর snippet-গুলো এটি শেয়ার করে। ফুরিয়ে গেলে পরের host
interaction ব্যর্থ হয়, যদিও বিদ্যমান state ব্যবহার করা বিশুদ্ধ Python তবুও কাজ করতে পারে। `run_code` দেয়
শুরু-হওয়া call-এর সারাংশ আর restart-এর স্পষ্ট নির্দেশনা: চালিয়ে যাওয়ার আগে আংশিক ফল পরীক্ষা করুন,
কারণ `restart: true` REPL state মুছে দেয় আর সম্পন্ন call আবার চালালে তাদের পার্শ্বপ্রতিক্রিয়া (side effect) পুনরাবৃত্ত হয়।
ফুরিয়ে যাওয়ার ক্ষেত্রে কোনো স্বয়ংক্রিয় restart বা replay নেই।

nested tool call আলাদাভাবে সীমায় বাঁধা `max_tool_calls` দিয়ে, যার ডিফল্ট প্রতি `run_code`
call-এ 100। প্রতিটি call নির্ধারণের আগেই budget সংরক্ষিত হয়, তাই একটি snippet অনুমতির বেশি কাজ
পাঠাতে পারে না। budget-এর বাইরের call sandbox-এর ভেতরে তার call-এর জায়গাতেই ব্যর্থ হয়। যে snippet
error-টি ধরে, সে ইতিমধ্যে সম্পন্ন call-গুলোর ফল রাখে আর সেগুলো ফেরত দিতে পারে। যে snippet
এটি ছড়িয়ে পড়তে দেয়, সে একটি model retry পায়, যাতে থাকে কতগুলো nested call শুরু হয়েছিল,
তারপর প্রতি-call বিবরণ: প্রতিটিকে কী দিয়ে ডাকা হয়েছিল, আর সেটি ফেরত এসেছে, শেষ হয়নি, নাকি
প্রত্যাখ্যাত হয়েছে। শেষ না হওয়া call-গুলোও অন্তর্ভুক্ত থাকে, ছেঁকে বাদ দেওয়া হয় না, কারণ একটি tool থামার আগেই
একটি পরিবর্তন করে ফেলতে পারে। সেই বিবরণ সীমিত — argument আর ফলের preview দেখানো হয়, আর তালিকা
একটি আকার-সীমায় থেমে জানায় কতগুলো entry বাদ রাখল — তাই বড় payload retry-কে
ফুলিয়ে দিতে পারে না। তালিকা কাটা হোক বা না হোক, জানানো মোট সংখ্যা নির্ভুল থাকে, আর এটিই
মডেলকে বলে যে কিছু call তার দেখার বাইরে রয়ে গেছে। তালিকাটি মডেলের জন্য context, পাহারা নয়:
মডেলকে ওই tool আবার ডাকতে কিছুই আটকায় না, তাই এটিকে পুনরাবৃত্তি ঠেকানোর উপায় নয়, বরং পরের
চেষ্টাকে জানানোর উপায় হিসেবে দেখুন।

এগুলো override করুন `resource_limits={'max_duration_secs': 10, 'max_memory': 134_217_728, 'max_suspensions': 10_000}` আর
`max_tool_calls=25` দিয়ে। `resource_limits='unlimited'` দিন শুধু তখনই, যখন অন্য কোনো execution সীমানা
সমতুল্য সীমা দেয়। এটি সময় আর memory-র সীমা সরায়, কিন্তু Monty-র ডিফল্ট
suspension budget রেখে দেয়; suspension সীমাহীন হতে পারে না।

nested tool call run-এর [`tool_calls_limit`](../agent.md#usage-limits)-এও গোনা হয়, সেগুলো যে
`run_code` call করে সেটিসহ। প্রতিটি nested call চলার আগে পরীক্ষা হয়, এখনও অপেক্ষমাণ call-গুলো গুনে,
আর যেটি সীমা ছাড়াত সেটি run শেষ করে
[`UsageLimitExceeded`][pydantic_ai.exceptions.UsageLimitExceeded] দিয়ে, শীর্ষ-স্তরের tool call-এর মতোই। snippet-এর ভেতরে
error ধরলেও এটি ঠেকানো যায় না।

`CodeMode` Temporal workflow-এর ভেতরে চললে এটি `max_duration_secs` নিষ্ক্রিয় করে, স্পষ্ট
override-সহ। `run_code` workflow code-এ replay হয়, তাই সেখানে অতিবাহিত সময় মাপলে
replay রেকর্ড করা workflow থেকে ভিন্ন পথ বেছে নিতে পারত। memory আর suspension সীমা তবুও প্রযোজ্য। সময়-সীমাবদ্ধ
কাজ বরং একটি Temporal activity-র পেছনে রাখুন।

/// info | এক নজরে: চারটি সীমা

| সীমা | ডিফল্ট | কী মাপে |
|---|---|---|
| `max_duration_secs` | 30 সেকেন্ড (প্রতি snippet) | sandbox-এর CPU সময়; tool-এর অপেক্ষা বাদ; sleep-এর আলাদা ভাতা |
| `max_memory` | 256 MiB | sandbox heap |
| `max_suspensions` | 1,000 (প্রতি session) | বাইরের call, OS callback, নাম খোঁজা… — tool গণনা নয় |
| `max_tool_calls` | 100 (প্রতি `run_code`) | nested tool call |

এর ওপরে run-এর `tool_calls_limit`-ও nested call গোনে।

///

## সমসাময়িক tool call { #concurrent-tool-calls }

sandbox-এ নেওয়া tool-গুলো `async def` function হিসেবে দেখানো হয়, তাই তৈরি করা কোড কয়েকটি call শুরু করে
`asyncio.gather` দিয়ে একসাথে await করতে পারে। সেই call-গুলো একই সময়ে চলবে কি না, তা run-এর
[parallel execution mode](../tools-advanced.md#parallel-tool-calls-concurrency) অনুসরণ করে:

- `'parallel'` (ডিফল্ট) আর `'parallel_ordered_events'` gather করা call-গুলো একসাথে চালায়।
  `'parallel_ordered_events'` শুধু শীর্ষ-স্তরের tool call-এর result event-গুলো সাজায়, যা nested
  call পাঠায় না। `DBOSDurability` ডিফল্টভাবে এই mode-ই ব্যবহার করে।
- `'sequential'` gather করা call-গুলো একে একে চালায়, কোড যে ক্রমে শুরু করেছিল সেই ক্রমে।

`sequential=True` চিহ্নিত tool একটি সাধারণ `def` হিসেবে দেখানো হয় আর প্রতিটি mode-এ একা চলে: এর আগে
কোড যে call-গুলো শুরু করেছিল, সেগুলো আগে শেষ হয়।

যে durable engine nested call-কে step হিসেবে রেকর্ড করে, সেগুলো শুরু হওয়ার সাথে সাথে নম্বর দেয়। যখন একটি tool বা
`before_tool_execute`-এর মতো একটি capability hook তার step শুরুর আগে await করে, তখন পুনরুদ্ধারের সময় সমসাময়িক call-গুলো
ভিন্ন ক্রমে তাদের step শুরু করতে পারে। nested call একে একে চালাতে durability capability-তে
`parallel_execution_mode='sequential'` দিন।

## REPL state { #repl-state }

একই agent run-এর মধ্যে `run_code` call-গুলোর মাঝে state টিকে থাকে — variable, import আর function definition পরের call-এ থেকে যায়। state reset করতে tool call-এ `restart: true` দিন। worker crash বা host-দিকের execution ব্যর্থতা session অকেজো করলে, `run_code` একটি model retry ফেরত দেয়, যা reset আর ইতিমধ্যে শুরু হওয়া nested call-গুলোর কথা জানায়; পরের snippet-কে প্রয়োজনীয় যেকোনো state আবার তৈরি করতে হয়।

### run-এর পর run REPL রাখা { #keep-the-repl-across-runs }

প্রতিটি agent run নিজের REPL শুরু করে, তাই কয়েকটি run দিয়ে গড়া একটি কথোপকথন run-গুলোর মাঝে তার sandbox state হারায়। এটি রাখতে একটি `repl_store` দিন: যে run `run_code` ডাকে, সেটি প্রথম snippet-এর আগে store-এর ফেরত দেওয়া state লোড করে, আর run শেষ হলে REPL store-এ সংরক্ষণ করে। store হলো async `load` আর `save` method-ওয়ালা যেকোনো object (`pydantic_ai_harness.code_mode.CodeModeReplStore`), আর state হলো REPL-এর Monty-র অস্বচ্ছ (opaque) dump। key হিসেবে `ctx.conversation_id` ব্যবহার করুন, যা `conversation_id` বা আগের run-এর `message_history` দিলে run-এর পর run একই থাকে:

```python
from pydantic_ai import Agent, RunContext
from pydantic_ai_harness import CodeMode


class InMemoryReplStore:
    def __init__(self) -> None:
        self.states: dict[str, bytes] = {}

    async def load(self, ctx: RunContext) -> bytes | None:
        return self.states.get(ctx.conversation_id or '')

    async def save(self, ctx: RunContext, state: bytes | None) -> None:
        key = ctx.conversation_id or ''
        if state is None:
            self.states.pop(key, None)
        else:
            self.states[key] = state


agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[CodeMode(repl_store=InMemoryReplStore())])
```

- যে run কখনো `run_code` ডাকে না, সেটি লোড বা সংরক্ষণ কোনোটিই করে না।
- `restart: true` সংরক্ষিত state বাদ দেয়। run তখন তার নতুন REPL সংরক্ষণ করে, অথবা restart করা snippet REPL তৈরির আগেই ব্যর্থ হলে `save(ctx, None)` ডাকে।
- পুনরুদ্ধার করা REPL যে resource limit-এ সংরক্ষিত হয়েছিল তা-ই রাখে, তাই state run-এর নির্ধারিত `resource_limits` রেকর্ড করে। অন্য সীমায় সংরক্ষিত state, বা যেটি Monty লোড করতে পারে না — যেমন কাটা dump বা অসামঞ্জস্যপূর্ণ Monty সংস্করণের একটি — একটি log করা warning-সহ বাদ পড়ে, আর run একটি নতুন REPL শুরু করে।
- Monty একটি dump-এর সত্যতা যাচাই (authenticate) করে না। শুধু আপনার application-এর সংরক্ষিত state ফেরত দিন, এমন storage থেকে যেখানে অন্য কেউ লিখতে পারে না।
- timeout, worker crash, বা বাতিল হওয়া snippet REPL reset করলে run-এর আগে সংরক্ষিত state থেকে যায় — যদি না run-এর পরের কোনো snippet নতুন REPL বানায়, যা তখন সংরক্ষিত হয়। বাতিল হওয়া run তবুও একটি অলস (idle) REPL সংরক্ষণ করে।
- store error run ব্যর্থ করে না: ব্যর্থ `load` একটি নতুন REPL শুরু করে, আর ব্যর্থ `save` সংরক্ষিত state যেমন ছিল তেমন রাখে। 10 সেকেন্ড পরেও চলমান একটি `save` বাতিল হয়, তবে এটি কোনো thread-কে যে কাজ দিয়েছিল তা তবুও শেষ হতে পারে, তাই atomically লিখুন। প্রতিটি একটি warning হিসেবে log হয়।
- পুনরুদ্ধার করা state সেই type check এড়িয়ে যায়, যা নতুন REPL-এর প্রথম snippet পায়, কারণ checker পুনরুদ্ধার করা নামগুলো জানে না।
- dump-এ প্রতিটি জীবন্ত মান থাকে, তাই এটি বড় হতে পারে। সীমায় বাঁধতে `save`-কে দিয়ে অতিরিক্ত বড় state বাদ দিন আর পুরোনোটা ভুলে যান। `monty_sandbox`-এর সাথে, session রাখে এমন server বরং একটি record ID ফেরত দেয়, যা server যতদিন রাখে ততদিন টেকে; আর যে server কিছুই রাখে না, সেটি প্রতিটি save একটি log করা warning-সহ ব্যর্থ করে।
- durable execution-এ store ব্যবহার হয় না, কারণ সেখানে এর I/O replay করা workflow code-এ চলত।

/// danger | নিরাপত্তা

Monty dump যাচাই করে না — `load` যা ফেরত দেয়, sandbox সেটিকেই নিজের state হিসেবে মেনে নেয়। ব্যবহারকারী বা অন্য কেউ লিখতে পারে এমন জায়গা (যেমন client-এর পাঠানো cookie বা শেয়ার করা bucket) থেকে state লোড করবেন না।

///

## Eager execution { #eager-execution }

সাধারণত `CodeMode` কোনো কোড চালানোর আগে মডেলের একটি `run_code` call লেখা শেষ হওয়ার জন্য অপেক্ষা করে।
আগে শুরু করতে `eager=True` সেট করুন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[CodeMode(eager=True)],
)
```

যেমন, ধরুন মডেল এই কোড এক লাইন করে তৈরি করছে:

```python
first = await fetch_item(item_id=1)
second = await fetch_item(item_id=2)
[first, second]
```

eager mode-এ, প্রথম লাইন সম্পূর্ণ হওয়ামাত্র `fetch_item`-এর প্রথম call শুরু হতে পারে। একই সময়ে
`CodeMode` বাকি লাইনগুলো পেতে থাকে। eager mode ছাড়া, মডেল পুরো snippet তৈরি না করা পর্যন্ত
কোনো call-ই শুরু হয় না।

কোডটি তবুও একটি `run_code` call হিসেবে গোনা হয়। এটি একটি REPL session, একটি tool-call সীমা,
আর একটি সম্মিলিত ফল ব্যবহার করে। `fetch_item` আর কোডের ডাকা অন্য tool-গুলোর hook তবুও চলে।
`run_code`-এর চারপাশের hook চলে শুধু মডেল call লেখা শেষ করার পরে, তাই
eager mode ইতিমধ্যে যে লাইনগুলো চালিয়েছে সেগুলো তারা approve বা পরিবর্তন করতে পারে না।

কনফিগার করা Monty resource limit তবুও প্রযোজ্য, তবে `max_duration_secs` আর sleep ভাতা
প্রতি খণ্ডে (fragment) গোনা হয়: প্রতিটি eager খণ্ড আর বাকি কোড নিজের ভাতা পায়, তাই একটি eager
call মোট হিসেবে eager mode ছাড়া একই কোডের চেয়ে বেশি সময় চলতে পারে। memory
session শেয়ার করে।

এই সীমাবদ্ধতাগুলো মনে রাখুন:

- ইতিমধ্যে চলে যাওয়া কোডের পার্শ্বপ্রতিক্রিয়া eager mode ফেরাতে পারে না।
- একটি [parallel `InputGuardrail`](guardrails.md#parallel-input-guards) থাকলে, একটি eager statement থেকে আসা nested tool call
  চলার আগে guard-এর রায়ের জন্য অপেক্ষা করে, তাই আটকানো prompt
  কোনো tool চালায় না।
- মডেল পরে `restart: true` চাইলে কিছু কাজ আবার চলতে পারে।
- streaming-এর সময় মডেল আগের কোনো লাইন বদলালে `CodeMode` REPL reset করে আর
  মডেলকে কোডটি আবার পাঠাতে বলে।
- eager mode বিশ্বাস করে যে provider stream করা `run_code` part আর তার tool
  নাম অক্ষত রাখে। কোনো provider part-টি সরিয়ে দিলে বা নাম বদলালে, ইতিমধ্যে চলা কাজ ফেরানো
  যায় না।
- eager execution ব্যবহার হয় শুধু তখনই, যখন `run_code` একটি model response-এর প্রথম tool call।
  পরের tool call-গুলো স্বাভাবিক dispatch-এর জন্য অপেক্ষা করে, যাতে মডেল যে ক্রমে চেয়েছে সেই ক্রমে চলে।
- Temporal বা DBOS-এর মতো durable execution ব্যবহার করলে eager mode নিষ্ক্রিয় থাকে।
- বাকি sandbox executor-এর মতো eager mode-এরও asyncio লাগে।
- একটি statement শেষ হওয়ার আগেই বাধাপ্রাপ্ত হলে, যেমন call-টি validation-এ ব্যর্থ হওয়ায়,
  session restart হয় আর পরের snippet-কে তার state আবার তৈরি করতে হয়।
- eager statement থেকে ডাকা nested tool-কে asyncio cancellation মেনে চলতে হবে। যখন
  একটি run শেষ হয় বা একটি stream করা call অকেজো হয়, `CodeMode` চলমান কাজ বাতিল করে আর
  সেটি ছেড়ে দেওয়ার জন্য একটি সীমিত সময় (বর্তমানে 5 সেকেন্ড) অপেক্ষা করে। সময়মতো না ছাড়া কাজ
  পরিত্যক্ত হয়; সেটি আর নতুন tool call শুরু করতে পারে না।
- আগেভাগে চলা statement থেকে ডাকা tool-গুলো `run_code` span খোলার আগেই trace হয়।

/// tip | উদাহরণ দিয়ে বুঝি

রাঁধুনিকে পুরো রেসিপি লেখা শেষ হওয়া পর্যন্ত বসিয়ে না রেখে, প্রথম লাইন "চাল ধুয়ে ভিজিয়ে রাখো" লেখামাত্র কাজ শুরু করতে দেওয়া — এটিই eager mode। তবে মনে রাখুন: চাল একবার ভিজিয়ে ফেললে, পরে রেসিপি বদলালেও সেটা আর শুকনো হবে না (পার্শ্বপ্রতিক্রিয়া ফেরানো যায় না)।

///

## Speculative execution { #speculative-execution }

`speculate` পার্শ্বপ্রতিক্রিয়াহীন tool call শুরু করে, যখন মডেল এখনও
`run_code` call লিখছে। `code` argument stream হয়ে আসার সাথে সাথে, `CodeMode` নাম-দেওয়া
tool-গুলোর এমন call খোঁজে, যার সব argument keyword literal। প্রতিটি শুরু হয় যে লাইন সেটি সম্পূর্ণ করে
তা stream হওয়ামাত্র, এমনকি তার চারপাশের statement (একটি `if` শাখা, একটি `with` body) এখনও শেষ না
হলেও। সম্পূর্ণ snippet চলে একই call-এ পৌঁছালে, ঠান্ডা অবস্থা থেকে tool শুরু না করে
ইতিমধ্যে চলমান ফলটি নেয়। এতে tool-এর latency
model generation-এর সাথে একই সময়ে কাটে (speculative programmatic tool calling,
<https://alexzhang13.github.io/blog/2026/spec-ptc/>)।

### আগেভাগে চালানো নিরাপদ এমন tool বাছুন { #choose-tools-that-are-safe-to-run-early }

একটি speculate করা call এমন শাখার জন্যও চলতে পারে, যা snippet কখনো নেয় না। শুধু-পড়া হওয়া জরুরি, কিন্তু
যথেষ্ট নয়: পরিবর্তনশীল state আগে পড়লে ভিন্ন উত্তর আসতে পারে। এমন tool বাছুন,
যার ফল আর বাইরের আদান-প্রদান launch-এর সময়েই গ্রহণযোগ্য, কখনো ব্যবহার না হলেও।
অব্যবহৃত request-ও API চার্জ ঘটাতে, rate limit খরচ করতে, আর একটি
বাইরের service-এ argument পাঠাতে পারে। ইতিমধ্যে পাঠানো request cancellation ফেরাতে পারে না।

এই উদাহরণ স্থির data-র ওপর দুটি স্বাধীন খোঁজ রেজিস্টার করে। চালাতে provider
credential লাগে, যেমন `OPENAI_API_KEY`। এই local function-গুলোর চেয়ে আসল network খোঁজে latency
একসাথে কাটানোর সুযোগ বেশি।

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode


def lookup_author(*, title: str) -> str:
    """Find a book's author in a fixed catalog."""
    return {'Frankenstein': 'Mary Shelley'}.get(title, 'Unknown')


def lookup_year(*, title: str) -> int | None:
    """Find a book's publication year in a fixed catalog."""
    return {'Frankenstein': 1818}.get(title)


code_mode = CodeMode(speculate=['lookup_author', 'lookup_year'])
agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[code_mode],
    tools=[lookup_author, lookup_year],
)
result = agent.run_sync(
    'Use run_code to look up the author and publication year of Frankenstein. '
    'Call both tools independently with the literal keyword argument title="Frankenstein".'
)
print(result.output)
print(code_mode.speculation_stats)
```

snippet মডেল বাছে, তাই prompt speculative launch নিশ্চিত করে না।
snippet সফলভাবে শেষ হলে, snippet কখনো দাবি করেনি এমন call বাতিল হয়। চলার আগেই ব্যর্থ snippet
(syntax বা type error) তার launch রেখে দেয়, যাতে retry সেগুলো দাবি করতে পারে;
retry যা অদাবিকৃত রাখে, তা পরের model ধাপ শুরু হলে বাতিল হয়।

tool-এর নাম না দিয়ে, tool-গুলো নিজেদের সম্পর্কে যা বলে তাতে বিশ্বাস রাখতে `speculate='declared'` দিন:
`Tool(..., metadata={'read_only': True})` চিহ্নিত tool, আর যে MCP tool-গুলোর
server `readOnlyHint` annotation প্রকাশ করে। idempotence যথেষ্ট নয় — idempotent
delete তবুও মুছে ফেলে — তাই `idempotent` ঘোষণা গোনা হয় না। একটি ঘোষণা হলো tool-লেখকের
দাবি, প্রমাণ নয়; তাই `'declared'` লেখকদের সেই একই বিশ্বাস দেয়, যা একটি
স্পষ্ট তালিকা আপনার ওপর রাখে।

```python
from pydantic_ai import Agent, Tool
from pydantic_ai_harness import CodeMode


def search(query: str) -> str:
    """Look something up."""
    return f'results for {query}'


agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[CodeMode(speculate='declared')],
    tools=[Tool(search, metadata={'read_only': True})],
)
```

/// info | কোডটি সহজ ভাষায় (`speculate` উদাহরণ)

| অংশ | মানে |
|---|---|
| `lookup_author`, `lookup_year` | স্থির catalog থেকে পড়া — পার্শ্বপ্রতিক্রিয়াহীন, তাই আগেভাগে চালানো নিরাপদ |
| `CodeMode(speculate=['lookup_author', 'lookup_year'])` | শুধু এই দুটি tool-কে speculate করার অনুমতি |
| prompt-এ "literal keyword argument `title="Frankenstein"`" | speculate হতে argument literal keyword হতে হয় |
| `code_mode.speculation_stats` | কতগুলো launch হলো, কতগুলো কাজে লাগল — দেখার জন্য |

///

### execution-এর ক্রম বোঝা { #understand-execution-order }

snippet execution-এর সময় Code Mode ইতিমধ্যে চলমান নয় এমন যোগ্য literal call-ও খোঁজে,
launch সীমা আর ক্রমের বাধা সাপেক্ষে। সেই call-গুলো প্রতিটি `await`-এর জন্য পালাক্রমে অপেক্ষা না করে
একই সময়ে চলতে পারে। একটি `if`/`else`-এর দুই শাখার যোগ্য call-ই শুরু হতে পারে; নেওয়া
শাখা তার ফল দাবি করে আর অন্য launch বাদ পড়ে।

সামনে-দেখা (lookahead) থেমে যায় একটি পরিচিত tool call-এ, যা যোগ্য নয় — একটি `sequential` tool-সহ।
যেমন, `update_record` যোগ্য না হলে আর `search` যোগ্য হলে:

```python
await update_record(key='status', value='ready')
await search(query='status')  # Runs after the update, not speculatively ahead of it.
```

কোড একটি অযোগ্য tool-এ তার নাম না নিয়েও পৌঁছাতে পারে, যেমন আগের একটি snippet-এ সংজ্ঞায়িত
helper দিয়ে। একটি launch ব্যবহার হয় না, যদি একটি অযোগ্য tool-এর call — native বা `run_code`-এর ভেতরে —
launch-এর পরে শুরু বা শেষ হয়। dispatch তখন tool-টি স্বাভাবিকভাবে চালায়
আর একটি miss হিসেবে গোনা হয়; launch-টি নষ্ট কাজ হিসেবে বাদ পড়ে।
শুধু tool call-ই এই সীমানা সরায়: sandbox `mount` বা `os_access` দিয়ে যা লেখে, তা
সরায় না — তাই যে tool এমন state পড়ে যা ওই লেখাগুলো বদলায়, তাকে যোগ্য করবেন না।

আগের একটি আটকে-রাখা পড়াকে পরের call-গুলোর সাথে একই সময়ে চালাতে, সেই পড়াটিকেও যোগ্য হতে হবে।
অন্য একটি model tool call-এর পরে আসা stream করা `run_code` part স্বাভাবিক dispatch-এর জন্য অপেক্ষা করে।
যোগ্যতা একটি বিশ্বাসের সিদ্ধান্ত, ইচ্ছেমতো Python পার্শ্বপ্রতিক্রিয়ার বিশ্লেষণ নয়।

এই সীমাবদ্ধতাগুলো মনে রাখুন:

- শুধু literal keyword argument-ওয়ালা call-ই আগেভাগে শুরু হতে পারে। যে call-এর argument
  আগের একটি statement থেকে আসে, সেটি ওই statement-এর জন্য অপেক্ষা করে।
- call খোঁজা হয় stream করা text-এ, তাই একটি string literal বা
  comment-এর ভেতরে লেখা call-ও শুরু হতে পারে। snippet শেষ হলে সেটি বাদ পড়ে।
- `sequential` tool কখনো speculate করে না, আর run-এর parallel
  execution mode `sequential` হলে কিছুই speculate করে না।
- একটি [parallel `InputGuardrail`](guardrails.md#parallel-input-guards) থাকলে, একটি speculate করা call
  চলার আগে guard-এর রায়ের জন্য অপেক্ষা করে, তাই আটকানো prompt সেগুলোর কোনোটিই চালায় না।
- speculate করা tool-এর hook চলে সেটি শুরু হলে, snippet দাবি করলে নয়। `run_code`-এর নিজের hook,
  approval আর guardrail চলে শুধু মডেল call লেখা শেষ করার পরে,
  তাই আগেভাগে শুরু হয়ে যাওয়া call তারা থামাতে পারে না; এটি eager mode-এর একই
  চুক্তি।
- প্রতি `run_code` call-এ সর্বোচ্চ `max_tool_calls`টি call (আর কখনো 32-এর বেশি নয়) আগেভাগে শুরু হয়;
  পরেরগুলো ঠান্ডা অবস্থা থেকে চলে। এই speculative ভাতা snippet-এর dispatch
  budget থেকে আলাদা: অদাবিকৃত launch বাড়তি কাজ, `max_tool_calls`-এর বিপরীতে সংরক্ষণ নয়।
- একটি `tool_calls_limit`-এর অধীনে, একটি call আগেভাগে শুরু হওয়ার মুহূর্ত থেকেই সীমায় গোনা হয়,
  snippet কখনো দাবি না করলেও। সীমা যে launch প্রত্যাখ্যান করেছে, snippet চাইলে সেটি ঠান্ডা অবস্থা থেকে চলে।
- speculate করা tool-কে asyncio cancellation মেনে চলতে হবে। cleanup cancellation চায়
  আর প্রতি stream করা call-এ পাঁচ সেকেন্ড পর্যন্ত অপেক্ষা করে, তারপর অপেক্ষা বন্ধ করে। যে tool
  cancellation চেপে রাখে, সেটি run-এর পরেও টিকে থাকতে পারে; এই timeout জোর করে তার কাজ থামায় না।
- `speculate` চালু করলে run streaming mode-এ যায়, আর Temporal বা DBOS-এর মতো durable
  execution-এ option-টি নিষ্ক্রিয় থাকে।

`speculate` `eager=True`-এর সাথে মেলে: eager execution সেই statement-গুলো চালায় যা মডেল
লেখা শেষ করেছে, আর speculation এখনও পৌঁছানো হয়নি এমন call শুরু করে (শাখা, ধীর একটি statement-এর
পরের call)। eager mode যে statement চালায়, সেগুলোও ওই launch দাবি করে।

/// info | এক নজরে: eager বনাম speculate

| বিষয় | `eager=True` | `speculate=[...]` / `'declared'` |
|---|---|---|
| কী আগে চালায় | মডেলের লেখা শেষ হওয়া statement | literal keyword argument-ওয়ালা যোগ্য tool call |
| কোন tool | যেকোনো | শুধু অনুমোদিত / read-only ঘোষিত |
| না-নেওয়া শাখা | চলে না | চলতে পারে (পরে বাদ) |
| durable execution | নিষ্ক্রিয় | নিষ্ক্রিয় |

///

### speculation কাজে লাগছে কি না দেখা { #check-whether-speculation-helps }

`CodeMode.speculation_stats` ওই capability instance ব্যবহার করা প্রতিটি run জুড়ে launch গোনে,
আর speculation নিষ্ক্রিয় থাকলে এর counter শূন্যে থাকে। প্রতি-run তুলনার জন্য আগে/পরে
snapshot নিন। সফল `run_code` return-ও শুধু-history metadata-তে একটি `speculation` entry বহন করতে পারে,
`tool_calls` আর `tool_returns`-এর পাশে। মডেল-দৃশ্যমান content অপরিবর্তিত থাকে।

| Metric | পরিসর | মানে |
| --- | --- | --- |
| `launched` | Capability instance | speculatively শুরু হওয়া call, streaming বা execution-এর সময়। |
| `adopted` | Capability instance | আসল dispatch যে speculative ফলগুলো গ্রহণ করেছে, tool error-সহ। |
| `evicted` | Capability instance | অদাবিকৃত launch যা বাদ পড়েছে বা যাকে cancellation অনুরোধ পাঠানো হয়েছে। |
| `hits` | `run_code` return | যে dispatch একটি speculative ফল গ্রহণ করেছে। |
| `misses` | `run_code` return | যোগ্য tool-এ dispatch, যা ব্যবহারযোগ্য launch পায়নি আর স্বাভাবিকভাবে চলেছে। |
| `wasted` | `run_code` return | এই call সফলভাবে শেষ হওয়ার সময় বাদ পড়া অদাবিকৃত launch। |
| `hidden_ms` | `run_code` return | গৃহীত call-গুলোর launch থেকে মীমাংসা পর্যন্ত সময়ের যোগফল। |

`hidden_ms` **শুরু থেকে শেষ পর্যন্ত মাপা বাঁচানো সময় নয়**: call একই সময়ে চলতে পারে, আর এতে এমন
সময়ও থাকে যখন দাবি করার মুহূর্তে চলমান একটি launch-এর জন্য, বা একটি parallel
`InputGuardrail`-এর রায়ের জন্য অপেক্ষা করা হয়েছে। speculation চালু আর বন্ধ রেখে মোট run latency আর বাইরের request-এর খরচ
তুলনা করুন। `evicted` বা `wasted` কোনোটিই প্রমাণ করে না যে একটি অব্যবহৃত call শেষ হয়েছে, থেমেছে, বা
তার খরচ এড়িয়েছে।

জীবনচক্রটি `code_mode`
namespace-এ [capability event](../hooks.md) হিসেবেও পাঠানো হয়, তাই UI আর অন্য capability run-এর event stream থেকে সরাসরি এটি অনুসরণ করতে পারে:
`SpeculativeCodeUpdateEvent` (এ পর্যন্ত decode করা snippet, তার বন্ধ-statement
সীমানাসহ), `SpeculativeCallLaunchedEvent` (launch করা statement-এর লাইন-পরিসর আর
`streaming` বা `execution` `phase`-সহ), `SpeculativeCallSettledEvent` (শুধু stream
চলমান থাকা অবস্থায়; পরে শেষ হওয়া call তার অবস্থা জানায় দাবি বা বাদ পড়ার
event-এ), আর snippet চললে, `SpeculativeCallClaimedEvent`,
`SpeculativeCallMissedEvent` আর `SpeculativeCallEvictedEvent`।

### একটি call কেন speculate করছে না? { #why-isnt-a-call-speculating }

- tool-টি কি রেজিস্টার করা আর `run_code`-এর ভেতরে দেখানো, native রাখা নয়?
- এর মূল tool নাম কি অনুমোদিত তালিকায় আছে, বা এটি কি একটি বিশ্বস্ত read-only ঘোষণা বহন করে?
- তৈরি করা call কি variable বা positional argument নয়, literal keyword argument ব্যবহার করছে?
- আগের কোনো অযোগ্য tool call কি lookahead আটকাচ্ছে, বা আগের একটি model tool call এটিকে পিছিয়ে দিচ্ছে?
- tool-টি কি `sequential` চিহ্নিত, বা run কি বিশ্বব্যাপী sequential execution ব্যবহার করছে?
- durable execution কি সক্রিয়, বা প্রতি-call speculative launch সীমায় কি পৌঁছে গেছে?

এই পরীক্ষাগুলো পার হলে, তৈরি করা কোড আর launch event পরীক্ষা করুন। অতিরিক্ত বড় stream করা argument
আর ফুরিয়ে যাওয়া parser-work budget-ও stream scanning থামায়; speculation একটি অপ্টিমাইজেশন,
প্রতিটি যোগ্য call আগেভাগে শুরু হবে এমন নিশ্চয়তা নয়।

## WebSocket-এর মাধ্যমে remote worker { #remote-workers-over-websockets }

sandbox-এর কোড local subprocess-এর বদলে একটি remote Monty worker-এ চালাতে `monty_sandbox`-এ একটি `ws://` বা `wss://` URL
সেট করুন:

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[CodeMode(monty_sandbox='wss://sandbox.example.com/monty')],
)
```

একটি URL কোনো key ছাড়াই সংযুক্ত হয়। header পাঠাতে বা অন্য pool option সেট করতে, বরং একটি sync বা async
function দিন, যা একটি `pydantic_monty.AsyncMontyWebsocket` ফেরত দেয়; Code Mode প্রতিটি run-এর জন্য এটি থেকে একটি pool
বানায়। ওই pool-এর `request_timeout`, ডিফল্ট 10 সেকেন্ড, `max_duration_secs`-এর বদলে
tool call-গুলোর মাঝে কোড কতক্ষণ চলবে তা সীমিত করে।

server বিশ্বস্ত network-এ না থাকলে `wss://` ব্যবহার করুন: সংযোগটি আপনার agent-এর tool
call আর তাদের ফল বহন করে।

শুধু code execution worker-এ যায়। আপনার tool, `mount` directory, `os_access` আর `print`
output আপনার process-এই থাকে, আর REPL state local-এর মতোই `run_code` call-গুলোর মাঝে টিকে থাকে।

## Temporal durability { #temporal-durability }

দুটি integration-ই ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-harness[codemode,temporal]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[codemode,temporal]"
```

///


নাম-দেওয়া agent আর তার স্থির-ID toolset-গুলো workflow-এর বাইরে তৈরি করুন, তারপর
`CodeMode`-এর পাশে `TemporalDurability` যুক্ত করুন:

```python
from pydantic_ai import Agent
from pydantic_ai.durable_exec.temporal import TemporalDurability
from pydantic_ai_harness import CodeMode

agent = Agent(
    'openai:gpt-6.1-sol',
    name='coding-agent',
    capabilities=[CodeMode(), TemporalDurability()],
)
```

workflow থেকে সাধারণ agent ডাকতে আর `PydanticAIPlugin` এবং
`__pydantic_ai_agents__` বা `AgentPlugin` দিয়ে তার activity রেজিস্টার করতে [Pydantic AI Temporal guide](../durable_execution/temporal.md) অনুসরণ করুন।

`PydanticAIPlugin` `pydantic_monty`-কে Temporal-এর workflow sandbox-এর মধ্য দিয়ে যেতে দেয়। এতে Monty
সেখানে চালানো যায়, তবে `run_code` তবুও workflow code-এ চলে আর replay-এর সময় আবার execute হয়।
এটি local worker আর `monty_sandbox` দুটোর সাথেই কাজ করে। remote worker-এর ক্ষেত্রে replay আবার
worker-এ সংযুক্ত হয়, তাই workflow যখনই replay হয় তখন সেটি পৌঁছানোর মতো থাকতে হবে।
model request আর, ডিফল্টভাবে, nested tool call Temporal activity-র সীমানা পার হয়;
`asyncio.gather` nested tool activity একসাথে নির্ধারণ করতে পারে। REPL হলো এক agent run-এর
process-local state, durable storage নয়। replay রেকর্ড করা activity ফলের বিপরীতে রেকর্ড করা snippet-গুলো আবার চালিয়ে এটি
পুনর্গঠন করে।

workflow-দিকের কোড নির্ধারিত (deterministic) রাখুন। `mount`-এর পড়া-লেখা, `os_access` callback আর
host-ঘড়ির call replay-এর সময় আবার ঘটে; এদের ফল বদলালে workflow কোন activity নির্ধারণ করবে
তা বদলে যেতে পারে আর একটি `NondeterminismError` ঘটতে পারে। বাইরের পড়া, লেখা, ঘড়ি ব্যবহার আর
অন্য পার্শ্বপ্রতিক্রিয়া মোড়ানো tool-এ রাখুন, যাতে Temporal সেগুলোকে activity হিসেবে রেকর্ড করে। একই activity history-র
একই জায়গায় থাকলে replay বদলানো argument চিহ্নিত নাও করতে পারে, তাই replay validation
এই সীমানার বিকল্প নয়। Temporal activity timeout প্রযোজ্য nested tool-এ, `run_code`-এর ভেতরের বিশুদ্ধ
হিসাবে নয়। sandbox হিসাব করার সময় workflow অপেক্ষা করে, আর যে workflow task 2 সেকেন্ডের মধ্যে
ছেড়ে দেয় না Temporal সেটি ব্যর্থ করে — তাই ভারী হিসাব একটি tool-এ সরিয়ে নিন।
ঘড়ি, environment আর এলোমেলোতার call workflow-এর নিজের thread-এ `os_access`-এ পৌঁছায়, তাই একটি
handler `datetime.now()`-এর উত্তর `workflow.now()` দিয়ে দিতে পারে আর replay-নিরাপদ থাকতে পারে। ফাইল call-এর উত্তর
Monty আগে mount থেকে দেয়, আর সেগুলো অন্য একটি thread-এ handler-এ পৌঁছায়।

/// warning | সাধারণ ভুল

Temporal-এ `run_code`-এর ভেতরে বড় হিসাব (যেমন লাখো সারির loop) চালালে workflow task 2 সেকেন্ডে ছেড়ে না দেওয়ায় Temporal সেটি ব্যর্থ করে। আর `mount` বা host-ঘড়ি থেকে পড়া মান replay-তে বদলালে `NondeterminismError`। ভারী কাজ আর বাইরের I/O tool-এ (activity-তে) রাখুন।

///

## Observability { #observability }

[Logfire](https://pydantic.dev/logfire) বা যেকোনো OpenTelemetry backend দিয়ে instrument করলে `run_code`-এর ভেতরের nested tool call নিজস্ব span তৈরি করে — code mode আসলে কী করেছে তা বোঝার এটিই সবচেয়ে সহজ উপায়, কারণ প্রতিটি `run_code` span মডেল sandbox-এর ভেতর থেকে যে tool call দিয়েছে সেগুলোতে ছড়িয়ে পড়ে। সেটআপের জন্য দেখুন [Pydantic AI Logfire docs](../logfire.md)।

suspension-সীমার retry আলাদা capability span ব্যবহার না করে বিদ্যমান `run_code` error span আর nested tool span ব্যবহার করে।
retry-তে সীমিত শুরু-হওয়া-call context আর পুনরুদ্ধারের
নির্দেশনা থাকে। Monty-র কোনো typed ফুরিয়ে-যাওয়া চিহ্ন নেই, তাই হুবহু একই শব্দের একটি tool error
নিশ্চিত ফুরিয়ে-যাওয়া event-এর বদলে শর্তসাপেক্ষ নির্দেশনা পায়।

`run_code` tool return প্রতিটি nested call-সহ metadata-ও বহন করে, call id দিয়ে key করা:

```python
from pydantic_ai import Agent
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai_harness import CodeMode

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[CodeMode()])


@agent.tool_plain
def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return {'city': city, 'temp_f': 72}


result = agent.run_sync("What's the weather in Paris?")

for msg in result.all_messages():
    for part in msg.parts:
        if isinstance(part, ToolReturnPart) and part.tool_kind == 'code_mode.run_code':
            metadata = part.metadata or {}
            tool_calls = metadata['tool_calls']    # dict[str, ToolCallPart]
            tool_returns = metadata['tool_returns']  # dict[str, ToolReturnPart]
```

## `run_code` call চেনা { #recognizing-run_code-calls }

`run_code` tool `'code_mode.run_code'` [tool kind](../tools-advanced.md#typed-tool-parts) ঘোষণা করে, তাই এর call part-গুলো `RunCodeCallPart`-এ (`pydantic_ai_harness.code_mode` থেকে) উন্নীত হয়। একটি hook বা history processor tool-এর নাম মেলানোর বদলে `isinstance` দিয়ে এগুলো চিনতে পারে, আর জমা দেওয়া কোড `code` থেকে পড়তে পারে (বা এর সব argument, `RunCodeArgs` হিসেবে যাচাই করা, `typed_args` থেকে):

```python
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.capabilities import AbstractCapability, ValidatedToolArgs, WrapToolExecuteHandler
from pydantic_ai.messages import ToolCallPart
from pydantic_ai_harness import CodeMode
from pydantic_ai_harness.code_mode import RunCodeCallPart


@dataclass
class RecordSnippets(AbstractCapability[Any]):
    snippets: list[str] = field(default_factory=list)

    async def wrap_tool_execute(
        self,
        ctx: RunContext[Any],
        *,
        call: ToolCallPart,
        tool_def: ToolDefinition,
        args: ValidatedToolArgs,
        handler: WrapToolExecuteHandler,
    ) -> Any:
        if isinstance(call, RunCodeCallPart) and call.code is not None:
            self.snippets.append(call.code)
        return await handler(args)


agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[CodeMode(), RecordSnippets()])
```

`CodeMode` এই kind ঘোষণা করার আগে রেকর্ড করা `run_code` call সাধারণ `ToolCallPart` হিসেবে লোড হয়। `ToolCallPart.narrow_type(part, tool_kind='code_mode.run_code')` একটিকে উন্নীত করে।

## বাস্তবে { #in-practice }

একটি প্রতিনিধিত্বমূলক run `CodeMode`-কে একটি MCP server আর একটি web search-এর সাথে জুড়ে দেয়, আর তিনটি feed জুড়ে সবচেয়ে আলোচিত Hacker News story খুঁজতে, comment thread আর submitter-এর profile আনতে, আর পরবর্তী কভারেজের জন্য web খুঁজতে বলে। `CodeMode` এটিকে দুটি `run_code` call-এ গুটিয়ে আনে: প্রথমটি `asyncio.gather` দিয়ে সমান্তরালে তিনটি feed আনে, id দিয়ে ডুপ্লিকেট বাদ দেয়, score দিয়ে ছাঁকে, আর comment সংখ্যা দিয়ে র‍্যাঙ্ক করে — সাধারণ Python-এ; দ্বিতীয়টি তিনটি পরবর্তী call (`hn_get_thread`, `hn_get_user`, `duckduckgo_search`) একসাথে ব্যাচ করে।

<!-- Trace screenshot removed until it is Tinified: https://github.com/pydantic/pydantic-ai/issues/8824 -->

**[পুরো Logfire trace দেখুন ->](https://logfire-us.pydantic.dev/public-trace/84bcf123-2106-49da-9f6f-5c26395339bb?spanId=7650806a0785b946)** প্রতিটি `run_code` span মডেল sandbox-এর ভেতর থেকে যে tool call দিয়েছে সেগুলোতে ছড়িয়ে পড়ে।

## Filesystem আর OS প্রবেশাধিকার { #filesystem-and-os-access }

sandbox-এর কোড host-এর ফাইল, environment বা ঘড়িতে কোনো প্রবেশাধিকার ছাড়াই শুরু হয়। দুটি parameter নিয়ন্ত্রিত filesystem, environment বা ঘড়ির আচরণ যোগ করে।

দুটি parameter-ই capability তৈরির সময় স্থির হয়, তাই কনফিগার করা প্রবেশাধিকার একটি request-এ সীমিত রাখতে প্রতি request-এ `CodeMode` তৈরি করুন।

### `mount` -- host directory শেয়ার করা { #mount-share-host-directories }

agent যখন আসল ফাইল নিয়ে কাজ করে তখন `mount` বেছে নিন: একটি folder-এ রাখা dataset বিশ্লেষণ করে একটি report আবার লেখা, একটি checkout সম্পাদনা, বা একগুচ্ছ document প্রসেস করা। sandbox-এর `pathlib` কোড mount করা path-এর নিচে পড়ে আর লেখে। (environment variable বা ঘড়ির জন্য বরং `os_access` ব্যবহার করুন।)

mount হলো agent যে মেশিনে চলছে সেখানকার directory, run-এর workspace নয়। `ModalSandbox`-এর মতো remote sandbox-এর ক্ষেত্রে `Shell` আর `FileSystem` sandbox-এ কাজ করে, অথচ mount করা `pathlib` কোড তবুও host-এ পড়ে আর লেখে। মডেল তার command-গুলোর সাথে যে ফাইল শেয়ার করে, সেগুলোর জন্য workspace tool ব্যবহার করুন।

```python
from pydantic_ai import Agent
from pydantic_monty import MountDir
from pydantic_ai_harness import CodeMode

# The agent can read /work/data.csv and write /work/summary.md back to the host:
agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[CodeMode(mount=MountDir(virtual_path='/work', host_path='/tmp/agent-workspace', mode='read-write'))],
)
```

একটি `MountDir`-এর ডিফল্ট copy-on-write `mode='overlay'`: sandbox host-এর ফাইল পড়ে আর বর্তমান `run_code` call-এ করা লেখা দেখে, কিন্তু পরের call-এর আগে Monty সেই লেখাগুলো বাদ দেয় আর সেগুলো host-এ **পৌঁছায় না**। পরের call-গুলোকে লেখাগুলো পড়তে হলে `mode='read-write'` দিন, অথবা লেখা নিষেধ করতে `mode='read-only'`। একাধিক mount point-এর জন্য `mount` `MountDir`-এর একটি list-ও নেয়।

/// info | এক নজরে: `MountDir`-এর mode

| `mode` | sandbox পড়ে | sandbox লেখে | লেখা host-এ পৌঁছায়? |
|---|---|---|---|
| `'overlay'` (ডিফল্ট) | হ্যাঁ | হ্যাঁ, শুধু চলতি `run_code`-এ দেখা যায় | না |
| `'read-write'` | হ্যাঁ | হ্যাঁ | হ্যাঁ |
| `'read-only'` | হ্যাঁ | না | — |

///

### `os_access` -- sandbox-এর OS call-এর উত্তর নিজে দেওয়া { #os_access-answer-the-sandboxs-os-calls-yourself }

agent-এর যখন environment variable, বর্তমান তারিখ ও সময়, বা আপনার নিয়ন্ত্রিত filesystem আচরণ লাগে, তখন `os_access` বেছে নিন। এটিকে একটি তৈরি OS implementation (`AbstractOS`) দিন, অথবা একটি callback, যা প্রতিটি call-এর সিদ্ধান্ত নেয় — তাই আপনি শুধু দরকারি secret-গুলো ঢোকাতে, পুনরুৎপাদনযোগ্য run-এর জন্য "এখন"-কে স্থির করতে, বা ফাইল প্রবেশাধিকার নিজের store-এ পাঠাতে পারেন।

```python
from pydantic_ai import Agent
from pydantic_monty import OSAccess
from pydantic_ai_harness import CodeMode

# Give the agent a fixed set of environment values:
agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[CodeMode(os_access=OSAccess(environ={'API_BASE': 'https://api.example.com'}))],
)
```

একটি callback প্রতিটি OS call পায় আর তার ভাগ্য ঠিক করে:

```python
from pydantic_ai import Agent
from pydantic_monty import NOT_HANDLED
from pydantic_ai_harness import CodeMode

allowed_env = {'API_KEY': 'sk-...'}


def my_os(*, name, args, kwargs, **_):
    if name == 'os.getenv':
        # Answer the call: allow-listed keys resolve, every other key reads back
        # as None -- absent, exactly like a real unset variable.
        return allowed_env.get(args[0])
    # Refuse everything else: NOT_HANDLED makes the call fail in the sandbox.
    return NOT_HANDLED


agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[CodeMode(os_access=my_os)])
```

callback keyword argument নেয় আর `async` হতে পারে। পুরোনো positional রূপ, `my_os(name, args, kwargs)`,
এখনও কাজ করে তবে deprecated, আর পরের breaking release-এ সরানো হবে।

আপনার callback-এর return value call-এর ভাগ্য ঠিক করে, আর দুটি ফলাফল সহজেই গুলিয়ে যায়:

- **যেকোনো মান ফেরত দিন** — `None`, `''` বা `0`-সহ — আর সেটিই sandbox-এর দেখা ফল হয়। `None` ফেরত দেওয়া `os.getenv` হুবহু একটি সাধারণ সেট-না-করা variable-এর মতো দেখায়, তাই agent-এর কোড চলতে থাকে। কোনো কিছু *লুকানোর* উপায় এটিই: একটি খালি মান দিয়ে উত্তর দিন।
- **`NOT_HANDLED` ফেরত দিন**, আর call-টি অসমর্থিত হিসেবে গণ্য হয়: এটি sandbox-এর ভেতরে raise করে আর মডেল একটি retry পায়। এটি একটি ক্ষমতা সরাসরি *প্রত্যাখ্যান* করে — আটকাতে এটি ব্যবহার করুন, "কোনো মান নেই" বলতে নয়। agent যুক্তিসঙ্গতভাবে আশা করে এমন key-র জন্য `NOT_HANDLED` ফেরত দিলে retry খরচ হবে।

/// warning | host প্রবেশাধিকার কনফিগারেশনের ওপর নির্ভর করে

`mount` বাছাই করা host directory দেখায়। বিল্ট-ইন `OSAccess` একটি বিচ্ছিন্ন in-memory filesystem আর environment ব্যবহার করে, তবে ডিফল্টভাবে host-এর ঘড়ি; একটি কাস্টম handler বা `CallbackFile` অন্য host resource দেখাতে পারে। প্রতি request-এ `CodeMode` তৈরি করাই ভালো, যাতে দেওয়া যেকোনো প্রবেশাধিকার ওই request-এ সীমিত থাকে।

///

/// note | Monty-নির্দিষ্ট type

এই parameter-গুলো `pydantic_monty` থেকে Monty-র `AbstractOS`/`MountDir` type ব্যবহার করে।

///

/// tip | উদাহরণ দিয়ে বুঝি

`os_access` callback অনেকটা অফিসের রিসেপশনিস্ট। কেউ এসে জিজ্ঞেস করল "`API_KEY` আছে?" — অনুমোদিত হলে রিসেপশনিস্ট দিয়ে দেন; না হলে বলেন "এমন কিছু নেই" (`None` — প্রশ্নকারী স্বাভাবিকভাবে এগিয়ে যায়)। কিন্তু কেউ যদি সার্ভার রুমে ঢুকতে চায়, রিসেপশনিস্ট সরাসরি বলেন "এটা এখানে করা যাবে না" (`NOT_HANDLED` — call ব্যর্থ, মডেল retry পায়)।

///

## sandbox-এর বিধিনিষেধ { #sandbox-restrictions }

কোড চলে [Monty](https://github.com/pydantic/monty)-র ভেতরে, যা sandbox-এ ঘেরা Python-এর একটি উপসেট। মূল বিধিনিষেধ:

- কোনো third-party import নেই। অনুমোদিত stdlib module: `sys`, `typing`, `asyncio`, `math`, `json`, `re`, `unicodedata`, `datetime`, `time`, `random`, `os`, `pathlib`, `collections`, `itertools`, `functools`, `dataclasses`, `copy`, `base64`, `binascii` (প্রতিটি ব্যবহারের আগে import করতে হবে)।
- `asyncio.gather(...)` positional awaitable নেয় কিন্তু কোনো keyword argument নেয় না। অন্য task তৈরি আর wait API উপলব্ধ নয়।
- ডিফল্টভাবে কোনো ঘড়ি বা এলোমেলোতা নেই: `datetime.datetime.now()`, `datetime.date.today()`, `time.time()` আর seed ছাড়া `random` ব্যর্থ হয়। একটি `os_access` handler এগুলো implement করলে (বিল্ট-ইন `OSAccess` করে) এগুলো পাওয়া যায়। `time.sleep` আর `asyncio.sleep` সত্যিই অপেক্ষা করে, resource limit-এর অংশে বর্ণিত ভাতা পর্যন্ত; Temporal workflow-এর ভেতরে একটি sleep হলো একটি durable timer।
- `import *` নেই।
- filesystem I/O-র জন্য একটি `os_access` handler বা একটি `mount` লাগে; `os.getenv` / `os.environ`-এর জন্য একটি `os_access` handler লাগে।
- approval লাগে বা deferred (`CallDeferred`) execution-ওয়ালা tool অন্য যেকোনো tool-এর মতোই sandbox-এ নেওয়া হয়; agent-এ এগুলো ভেতরেই মীমাংসা করার মতো একটি `HandleDeferredToolCalls` (বা সমতুল্য) capability না থাকলে, `run_code` থেকে এমন একটি ডাকলে একটি error raise হয়, যা মডেলের কাছে retry হিসেবে আসে।
- tool-এর ফল sandbox-এ পৌঁছায় তার তৈরি stub যে JSON আকার ঘোষণা করে সেই আকারে, কারণ stub tool-এর JSON schema থেকে তৈরি। `Decimal`, `UUID` আর `datetime` string হিসেবে আসে, আর mapping-এর key string বানানো হয়, তাই `{1: 'a'}`-এর একটি `dict[int, str]` আসে `{'1': 'a'}` হিসেবে। `bytes` আর `bytearray` ব্যতিক্রম: Monty binary নিজস্বভাবে বহন করে, তাই stub এগুলোর জন্য `str` ঘোষণা করলেও এগুলো অপরিবর্তিত পার হয়।
- return schema ছাড়া একটি tool তবুও ডাকা যায়, তবে এর তৈরি signature দেখায় `-> Any`, তাই মডেলকে ফলের আকার অনুমান করতে হয়। `CodeMode` প্রতি run-এ এমন tool-গুলোর নাম একটি `CodeModeReturnSchemaWarning`-এ (একটি `UserWarning` subclass) জানায়। একটি function tool-কে return annotation দিন, অথবা আপনার MCP server-কে একটি `outputSchema` ঘোষণা করান; server আপনার না হলে, শুধু এই শ্রেণিটি চুপ করান `warnings.filterwarnings('ignore', category=CodeModeReturnSchemaWarning)` দিয়ে।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

YAML বা JSON-এ agent সংজ্ঞায়িত করার জন্য `CodeMode` Pydantic AI-এর [agent spec](../agent-spec.md) feature-এর সাথে কাজ করে:

```yaml
# agent.yaml
model: anthropic:claude-sonnet-5-5
capabilities:
  - CodeMode: {}
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import CodeMode

agent = Agent.from_file('agent.yaml', custom_capability_types=[CodeMode])
result = agent.run_sync('...')
print(result.output)
```

spec loader যাতে জানে কীভাবে `CodeMode` instantiate করতে হয়, সেজন্য `custom_capability_types` দিন। argument YAML-এও দেওয়া যায়:

```yaml
capabilities:
  - CodeMode:
      tools: ['search', 'fetch']
      max_retries: 5
```

## আরও পড়ুন { #further-reading }

- [Tool use via code](https://www.anthropic.com/engineering/code-execution-with-mcp) (Anthropic)
- [Code mode in production](https://blog.cloudflare.com/code-mode/) (Cloudflare)
- [Pydantic AI capabilities](../capabilities/overview.md)

/// check | সংক্ষেপে মনে রাখুন

* `capabilities=[CodeMode()]` → যোগ্য tool-গুলো একটি `run_code`-এ, মডেল Python লিখে সেগুলো `await` করে ডাকে।
* `tools=` (selector বা `{'code_mode': True}` metadata) দিয়ে কোন tool sandbox-এ যাবে তা বাছুন; shell tool পাশে থাকে।
* শেষ expression-ই ফল; assignment কিছু ফেরত দেয় না (`{}`)।
* সীমা: 30 সেকেন্ড/snippet, 256 MiB, 1,000 suspension, 100 nested tool call — সাথে run-এর `tool_calls_limit`।
* `repl_store` দিয়ে run-এর পর run REPL রাখুন — শুধু বিশ্বস্ত storage থেকে লোড করুন।
* `eager=True` লেখা শেষ হওয়া লাইন আগে চালায়; `speculate` পার্শ্বপ্রতিক্রিয়াহীন tool আগে শুরু করে — দুটোই durable execution-এ বন্ধ।
* host ফাইলের জন্য `mount` (ডিফল্ট overlay — host-এ লেখে না), env/ঘড়ির জন্য `os_access`; লুকাতে `None`, আটকাতে `NOT_HANDLED`।

///

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.CodeMode
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// info | API রেফারেন্স

`pydantic_ai_harness.code_mode.CodeModeReplStore`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/code-mode/)।

///
