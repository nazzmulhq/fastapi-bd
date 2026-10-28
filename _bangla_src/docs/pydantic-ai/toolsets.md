# Toolset { #toolsets }

/// note | এই পেজে যা শিখবেন

* Toolset কী: একসাথে নথিভুক্ত করা যায় এমন টুলের একটি সংগ্রহ, আর এজেন্টকে এটি দেওয়ার চার উপায়।
* `FunctionToolset`, toolset-এর নিজস্ব নির্দেশনা, আর toolset জোড়া লাগানো: মেলানো, ছাঁকা, উপসর্গ, নাম বদল, অনুমোদন, deferred loading।
* বাইরের (frontend) টুলের জন্য `ExternalToolset`, গতিশীলভাবে toolset তৈরি, আর নিজের toolset লেখা।
* MCP, LangChain আর অন্য third-party toolset।

///

একটি toolset হলো [টুলের](tools.md) একটি সংগ্রহ যা একবারে একটি এজেন্টে নথিভুক্ত করা যায়। এগুলো বিভিন্ন এজেন্ট আবার ব্যবহার করতে পারে, চলার সময় বা টেস্টের সময় বদলানো যায়, আর জোড়া লাগিয়ে গতিশীলভাবে কোন টুল উপলব্ধ তা ছাঁকা, টুলের সংজ্ঞা বদলানো বা টুল চালানোর আচরণ বদলানো যায়। একটি toolset-এ লোকালে সংজ্ঞায়িত ফাংশন থাকতে পারে, সেগুলো দিতে একটি বাইরের সার্ভিসের ওপর নির্ভর করতে পারে, বা উপলব্ধ টুলের তালিকা আর সেগুলো ডাকা সামলাতে নিজের লজিক বাস্তবায়ন করতে পারে। Toolset [capabilities](capabilities/overview.md) দিয়েও দেওয়া যায়, যা hook, নির্দেশনা আর মডেল সেটিংসহ টুল বান্ডেল করে।

/// tip | উদাহরণ দিয়ে বুঝি

টুল যদি একটি স্ক্রুড্রাইভার হয়, toolset হলো পুরো টুলবক্স। একটি "আবহাওয়া টুলবক্স", একটি "ডেটাবেস টুলবক্স" — যেকোনো এজেন্টকে একবারে পুরো বাক্সটি দিন। আর বাক্সগুলো মোড়ানো যায়: "এই বাক্সের শুধু পড়ার টুলগুলো দাও" (ছাঁকা), "সবগুলোর নামের আগে `weather_` লাগাও" (উপসর্গ), "এগুলো চালানোর আগে অনুমোদন নাও" (approval)।

///

Toolset ব্যবহার হয় (আরও অনেক কিছুর মধ্যে) একটি এজেন্টের কাছে উপলব্ধ [MCP সার্ভার](mcp/client.md) সংজ্ঞায়িত করতে। Pydantic AI-তে অনেক ধরনের toolset আছে যা নিচে বর্ণিত, আর আপনি [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset] ক্লাস থেকে উত্তরাধিকার নিয়ে একটি [নিজের toolset](#building-a-custom-toolset) সংজ্ঞায়িত করতে পারেন।

একটি এজেন্ট রানের সময় যে toolset উপলব্ধ থাকবে তা চারটি ভিন্ন উপায়ে নির্দিষ্ট করা যায়:

* এজেন্ট তৈরির সময়, `Agent`-এর [`toolsets`][pydantic_ai.agent.Agent.__init__] keyword আর্গুমেন্ট দিয়ে, যা toolset instance আর এজেন্টের [run context][pydantic_ai.tools.RunContext]-এর ভিত্তিতে [গতিশীলভাবে](#dynamically-building-a-toolset) toolset তৈরি করা ফাংশন দুটোই নেয়
* এজেন্ট চলার সময়, [`agent.run()`][pydantic_ai.agent.AbstractAgent.run], [`agent.run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync], [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] বা [`agent.iter()`][pydantic_ai.agent.Agent.iter]-এর `toolsets` keyword আর্গুমেন্ট দিয়ে। এই toolset-গুলো `Agent`-এ নথিভুক্তগুলোর বাড়তি হবে
* [গতিশীলভাবে](#dynamically-building-a-toolset), [`@agent.toolset`][pydantic_ai.agent.Agent.toolset] decorator দিয়ে, যা আপনাকে এজেন্টের [run context][pydantic_ai.tools.RunContext]-এর ভিত্তিতে একটি toolset তৈরি করতে দেয়
* একটি প্রাসঙ্গিক override হিসেবে, [`agent.override()`][pydantic_ai.agent.Agent.override] context manager-এর `toolsets` keyword আর্গুমেন্ট দিয়ে। এই toolset-গুলো context manager-এর আয়ুষ্কালে এজেন্ট তৈরি বা চলার সময় দেওয়াগুলোর জায়গা নেবে

```python title="toolsets.py"
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel


def agent_tool():
    return "I'm registered directly on the agent"


def extra_tool():
    return "I'm passed as an extra tool for a specific run"


def override_tool():
    return 'I override all other tools'


agent_toolset = FunctionToolset(tools=[agent_tool]) # (1)!
extra_toolset = FunctionToolset(tools=[extra_tool])
override_toolset = FunctionToolset(tools=[override_tool])

test_model = TestModel() # (2)!
agent = Agent(test_model, toolsets=[agent_toolset])

result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['agent_tool']

result = agent.run_sync('What tools are available?', toolsets=[extra_toolset])
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['agent_tool', 'extra_tool']

with agent.override(toolsets=[override_toolset]):
    result = agent.run_sync('What tools are available?', toolsets=[extra_toolset]) # (3)!
    print([t.name for t in test_model.last_model_request_parameters.function_tools])
    #> ['override_tool']
```

1. [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] পরের অংশে বিস্তারিত ব্যাখ্যা করা হবে।
2. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।
3. এই `extra_toolset` উপেক্ষিত হবে কারণ আমরা একটি override context-এর ভেতরে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## Function toolset { #function-toolset }

নাম থেকেই বোঝা যায়, একটি [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] লোকালে সংজ্ঞায়িত ফাংশনকে টুল হিসেবে উপলব্ধ করে।

ফাংশন চারটি ভিন্ন উপায়ে টুল হিসেবে যোগ করা যায়:

* [`@toolset.tool`][pydantic_ai.toolsets.FunctionToolset.tool] decorator দিয়ে — যে টুলের এজেন্টের [context][pydantic_ai.tools.RunContext]-এ প্রবেশ লাগে তার জন্য
* [`@toolset.tool_plain`][pydantic_ai.toolsets.FunctionToolset.tool_plain] decorator দিয়ে — যে টুলের এজেন্টের [context][pydantic_ai.tools.RunContext]-এ প্রবেশ লাগে না তার জন্য
* constructor-এর [`tools`][pydantic_ai.toolsets.FunctionToolset.__init__] keyword আর্গুমেন্ট দিয়ে, যা সাধারণ ফাংশন বা [`Tool`][pydantic_ai.tools.Tool]-এর instance নিতে পারে
* [`toolset.add_function()`][pydantic_ai.toolsets.FunctionToolset.add_function] আর [`toolset.add_tool()`][pydantic_ai.toolsets.FunctionToolset.add_tool] মেথড দিয়ে, যা যথাক্রমে একটি সাধারণ ফাংশন বা [`Tool`][pydantic_ai.tools.Tool]-এর একটি instance নিতে পারে

`add_function()` আর `add_tool()` মেথড একটি টুল ফাংশন থেকেও ব্যবহার করা যায়, একটি রানের সময় গতিশীলভাবে নতুন টুল নথিভুক্ত করতে যা পরের রান ধাপে উপলব্ধ হবে।

```python title="function_toolset.py"
from datetime import datetime

from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.models.test import TestModel


def temperature_celsius(city: str) -> float:
    return 21.0


def temperature_fahrenheit(city: str) -> float:
    return 69.8


weather_toolset = FunctionToolset(tools=[temperature_celsius, temperature_fahrenheit])


@weather_toolset.tool
def conditions(ctx: RunContext, city: str) -> str:
    if ctx.run_step % 2 == 0:
        return "It's sunny"
    else:
        return "It's raining"


datetime_toolset = FunctionToolset()
datetime_toolset.add_function(lambda: datetime.now(), name='now')

test_model = TestModel()  # (1)!
agent = Agent(test_model)

result = agent.run_sync('What tools are available?', toolsets=[weather_toolset])
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['temperature_celsius', 'temperature_fahrenheit', 'conditions']

result = agent.run_sync('What tools are available?', toolsets=[datetime_toolset])
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['now']
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

প্রথম মডেল রিকোয়েস্টের পরে রানে যোগ দেওয়া একটি টুল, যেভাবেই সেখানে পৌঁছাক, বার্তার ইতিহাসে একটি [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart] হিসেবে রেকর্ড হয়, যদি না আগের কোনো সরাসরি দৃশ্যমান টুল স্থির রাখার জন্য তখনো উপস্থিত না থাকে। `defer_loading=True`-সহ একটি নতুন টুল বদলে [tool search](tools-advanced.md#tool-search) corpus-এ যোগ দেয়। প্রতিটি provider এটি কীভাবে পৌঁছে দেয় তা দেখুন [Tools that appear mid-run](tools-advanced.md#mid-run-tool-additions)-এ।

### Toolset-এর নির্দেশনা { #toolset-instructions }

একটি [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] এমন নির্দেশনা দিতে পারে যা নিজে থেকে মডেল রিকোয়েস্টে যোগ হয়। এতে প্রতিটি toolset তার টুলের পাশাপাশি নিজের ব্যবহারের নির্দেশনা বহন করে, তাই toolset ব্যবহার করা প্রতিটি এজেন্টে নির্দেশনা পুনরাবৃত্তি করতে হয় না।

নির্দেশনা দেওয়া যায় স্ট্রিং, ফাংশন (sync বা async, [`RunContext`][pydantic_ai.tools.RunContext]-সহ বা ছাড়া), বা দুটোর মিশ্রণ হিসেবে:

```python title="toolset_instructions.py"
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

search_toolset = FunctionToolset(
    instructions='Always use the search tool before answering factual questions.',
)


@search_toolset.tool_plain
def search(query: str) -> str:
    """Search for information."""
    return f'Results for: {query}'


test_model = TestModel()
agent = Agent(test_model, toolsets=[search_toolset])
result = agent.run_sync('What is the capital of France?')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> Always use the search tool before answering factual questions.
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

run context-এ পৌঁছাতে পারে এমন গতিশীল নির্দেশনা ফাংশন নথিভুক্ত করতে [`@toolset.instructions`][pydantic_ai.toolsets.FunctionToolset.instructions] decorator-ও ব্যবহার করতে পারেন। [`@agent.instructions`][pydantic_ai.agent.Agent.instructions]-এর মতো, এটি `name=` আর [`on_change='append'`](agent.md#appending-instruction-changes) নেয়, যা কথোপকথনের মাঝে নির্দেশনা বদলালে cache করা prefix রাখে:

```python title="toolset_instructions_decorator.py"
from pydantic_ai import Agent, FunctionToolset, ModelRequest, RunContext
from pydantic_ai.models.test import TestModel

math_toolset = FunctionToolset[str]()


@math_toolset.instructions
def math_instructions(ctx: RunContext[str]) -> str:
    return f'You are helping: {ctx.deps}. Always show your work when using the calculator.'


@math_toolset.tool_plain
def calculator(expression: str) -> str:
    """Evaluate a math expression."""
    return '4'


test_model = TestModel()
agent = Agent(test_model, toolsets=[math_toolset], deps_type=str)
result = agent.run_sync('What is 2+2?', deps='Alice')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> You are helping: Alice. Always show your work when using the calculator.
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

নির্দেশনাসহ একটি toolset এজেন্ট-স্তরের [`instructions`][pydantic_ai.agent.Agent.__init__]-এর পাশাপাশি ব্যবহার হলে, toolset-এর নির্দেশনা এজেন্টের নির্দেশনার পরে জোড়া হয়:

```python title="toolset_instructions_combined.py"
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

toolset = FunctionToolset(instructions='Use the greeting tool for all greetings.')


@toolset.tool_plain
def greeting(name: str) -> str:
    """Greet someone."""
    return f'Hello, {name}!'


test_model = TestModel()
agent = Agent(
    test_model,
    instructions='You are a friendly assistant.',
    toolsets=[toolset],
)
result = agent.run_sync('Hi there!')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
"""
You are a friendly assistant.

Use the greeting tool for all greetings.
"""
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

নির্দেশনাসহ একাধিক toolset একটি এজেন্টে নথিভুক্ত হলে, তাদের সব নির্দেশনা মেলানো হয়:

```python title="toolset_instructions_multiple.py"
from pydantic_ai import Agent, FunctionToolset, ModelRequest
from pydantic_ai.models.test import TestModel

weather_toolset = FunctionToolset(instructions='Use weather tools for forecasts.')


@weather_toolset.tool_plain
def forecast(city: str) -> str:
    """Get weather forecast."""
    return 'Sunny'


calendar_toolset = FunctionToolset(instructions='Use calendar tools for scheduling.')


@calendar_toolset.tool_plain
def schedule(event: str) -> str:
    """Schedule an event."""
    return 'Scheduled'


test_model = TestModel()
agent = Agent(test_model, toolsets=[weather_toolset, calendar_toolset])
result = agent.run_sync('Plan my day')
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
"""
Use weather tools for forecasts.

Use calendar tools for scheduling.
"""
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### বদলায় এমন toolset নির্দেশনা { #toolset-instructions-that-change }

নির্দেশনা ফাংশন প্রতিটি মডেল রিকোয়েস্টের আগে চলে, তাই তাদের লেখা একটি রানের সময় বদলাতে পারে, যেমন একটি টুল কিছু অবস্থা হালনাগাদ করার পরে। ডিফল্টভাবে প্রতিটি পরিবর্তন নির্দেশনার prefix নতুন করে লেখে, যা provider-কে এর পেছনের cache করা কথোপকথন আবার ব্যবহার করা থেকে থামায়। কথোপকথনের মাঝে বদলানো নির্দেশনার জন্য, আমরা পরিবর্তনগুলো বদলে ইতিহাসে [জোড়ার](agent.md#appending-instruction-changes) পরামর্শ দিই: prefix cache-এ থাকে, প্রতিটি পরিবর্তনে ব্লকের সম্পূর্ণ নতুন লেখা ইতিহাসে যোগ হওয়ার বিনিময়ে। এগুলো শুধু আপনার নিয়ন্ত্রিত অবস্থা থেকে তৈরি করুন: [অবিশ্বস্ত লেখা নির্দেশনার বাইরে রাখুন](agent.md#untrusted-instruction-text)।

যোগ দিতে, toolset-কে একটি [`id`][pydantic_ai.toolsets.AbstractToolset.id] দিন আর ফাংশনটি `@toolset.instructions(name=..., on_change='append')` দিয়ে নথিভুক্ত করুন। একটি [নিজের toolset](#building-a-custom-toolset) বদলে [`get_instructions()`][pydantic_ai.toolsets.AbstractToolset.get_instructions] থেকে `on_change='append'`-সহ একটি [`InstructionPart`][pydantic_ai.messages.InstructionPart] ফেরত দিতে পারে:

```python title="toolset_instruction_changes.py"
from dataclasses import dataclass, field

from pydantic_ai import Agent, FunctionToolset, RunContext
from pydantic_ai.messages import InstructionDeltaPart, ModelRequest
from pydantic_ai.models.test import TestModel


@dataclass
class Cart:
    items: list[str] = field(default_factory=list[str])


cart_toolset = FunctionToolset[Cart](id='cart')


@cart_toolset.instructions(name='count', on_change='append')
def cart_count(ctx: RunContext[Cart]) -> str:
    return f'Items in the cart: {len(ctx.deps.items)}.'  # (1)!


@cart_toolset.tool
def add_to_cart(ctx: RunContext[Cart], item: str) -> str:
    """Add an item to the cart."""
    ctx.deps.items.append(item)
    return 'Added.'


agent = Agent(TestModel(), deps_type=Cart, toolsets=[cart_toolset])
result = agent.run_sync('Add an apple.', deps=Cart())
first_request = result.all_messages()[0]
assert isinstance(first_request, ModelRequest)
print(first_request.instructions)
#> Items in the cart: 0.
print(
    [
        part.content
        for message in result.all_messages()
        if isinstance(message, ModelRequest)
        for part in message.parts
        if isinstance(part, InstructionDeltaPart)
    ]
)
#> ['Items in the cart: 1.']
```

1. নির্দেশনায় শুধু সংখ্যাটি যায়, আইটেমের নাম নয়, যা মডেলের টুল আর্গুমেন্ট থেকে আসে: [অবিশ্বস্ত লেখা নির্দেশনার বাইরে রাখুন](agent.md#untrusted-instruction-text)।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## Toolset জোড়া লাগানো { #toolset-composition }

Toolset জোড়া লাগিয়ে গতিশীলভাবে কোন টুল উপলব্ধ তা ছাঁকা, টুলের সংজ্ঞা বদলানো বা টুল চালানোর আচরণ বদলানো যায়। একাধিক toolset একটিতে মেলানোও যায়।

### Toolset মেলানো { #combining-toolsets }

[`CombinedToolset`][pydantic_ai.toolsets.CombinedToolset] toolset-এর একটি তালিকা নিয়ে সেগুলো একটি হিসেবে ব্যবহার করতে দেয়।

```python title="combined_toolset.py"
from pydantic_ai import Agent, CombinedToolset
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset

combined_toolset = CombinedToolset([weather_toolset, datetime_toolset])

test_model = TestModel() # (1)!
agent = Agent(test_model, toolsets=[combined_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['temperature_celsius', 'temperature_fahrenheit', 'conditions', 'now']
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### টুল ছাঁকা { #filtering-tools }

[`FilteredToolset`][pydantic_ai.toolsets.FilteredToolset] একটি toolset মুড়ে রাখে আর রানের প্রতিটি ধাপের আগে উপলব্ধ টুল ছাঁকে, একটি ব্যবহারকারী-সংজ্ঞায়িত ফাংশনের ভিত্তিতে যা এজেন্টের [run context][pydantic_ai.tools.RunContext] আর প্রতিটি টুলের [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] পায় আর একটি boolean ফেরত দেয় যা বলে একটি নির্দিষ্ট টুল উপলব্ধ থাকা উচিত কিনা।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`filtered()`][pydantic_ai.toolsets.AbstractToolset.filtered] ডাকুন।

```python title="filtered_toolset.py"
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from combined_toolset import combined_toolset

filtered_toolset = combined_toolset.filtered(lambda ctx, tool_def: 'fahrenheit' not in tool_def.name)

test_model = TestModel() # (1)!
agent = Agent(test_model, toolsets=[filtered_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['weather_temperature_celsius', 'weather_conditions', 'datetime_now']
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### টুলের নামে উপসর্গ { #prefixing-tool-names }

[`PrefixedToolset`][pydantic_ai.toolsets.PrefixedToolset] একটি toolset মুড়ে রাখে আর ভিন্ন toolset-এর মধ্যে টুলের নামের সংঘর্ষ এড়াতে প্রতিটি টুলের নামে একটি উপসর্গ যোগ করে।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`prefixed()`][pydantic_ai.toolsets.AbstractToolset.prefixed] ডাকুন।

```python title="combined_toolset.py"
from pydantic_ai import Agent, CombinedToolset
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset

combined_toolset = CombinedToolset(
    [
        weather_toolset.prefixed('weather'),
        datetime_toolset.prefixed('datetime')
    ]
)

test_model = TestModel() # (1)!
agent = Agent(test_model, toolsets=[combined_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
"""
[
    'weather_temperature_celsius',
    'weather_temperature_fahrenheit',
    'weather_conditions',
    'datetime_now',
]
"""
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### টুলের নাম বদল { #renaming-tools }

[`RenamedToolset`][pydantic_ai.toolsets.RenamedToolset] একটি toolset মুড়ে রাখে আর নতুন নাম থেকে মূল নামের একটি dictionary mapping দিয়ে টুলের নাম বদলাতে দেয়। এটি কাজে লাগে যখন একটি toolset-এর দেওয়া নাম অস্পষ্ট বা অন্য toolset-এর সংজ্ঞায়িত টুলের সাথে সংঘর্ষ করত, কিন্তু [উপসর্গ যোগ করা](#prefixing-tool-names) অপ্রয়োজনীয়ভাবে দীর্ঘ বা মডেলের কাছে বিভ্রান্তিকর একটি নাম তৈরি করে।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`renamed()`][pydantic_ai.toolsets.AbstractToolset.renamed] ডাকুন।

```python title="renamed_toolset.py"
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from combined_toolset import combined_toolset

renamed_toolset = combined_toolset.renamed(
    {
        'current_time': 'datetime_now',
        'temperature_celsius': 'weather_temperature_celsius',
        'temperature_fahrenheit': 'weather_temperature_fahrenheit'
    }
)

test_model = TestModel() # (1)!
agent = Agent(test_model, toolsets=[renamed_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])
"""
['temperature_celsius', 'temperature_fahrenheit', 'weather_conditions', 'current_time']
"""
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### গতিশীল টুল সংজ্ঞা { #preparing-tool-definitions }

[`PreparedToolset`][pydantic_ai.toolsets.PreparedToolset] এজেন্ট রানের প্রতিটি ধাপের আগে উপলব্ধ টুলের পুরো তালিকা বদলাতে দেয়, একটি ব্যবহারকারী-সংজ্ঞায়িত ফাংশন দিয়ে যা এজেন্টের [run context][pydantic_ai.tools.RunContext] আর [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এর একটি তালিকা নেয় আর সেই ধাপে দেখানোর টুল সংজ্ঞা ফেরত দেয়।

এটি [`prepare_tools`](tools-advanced.md#prepare-tools) capability hook-এর toolset-নির্দিষ্ট সমতুল্য, যা toolset-জুড়ে একটি এজেন্টে নথিভুক্ত সব টুল সংজ্ঞা প্রস্তুত করে।

মনে রাখবেন `PreparedToolset` দিয়ে টুল যোগ বা নাম বদল সম্ভব নয়। বদলে, [`FunctionToolset.add_function()`](#function-toolset) বা [`RenamedToolset`](#renaming-tools) ব্যবহার করতে পারেন।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`prepared()`][pydantic_ai.toolsets.AbstractToolset.prepared] ডাকুন।

```python title="prepared_toolset.py"
from dataclasses import replace

from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.models.test import TestModel

from renamed_toolset import renamed_toolset

descriptions = {
    'temperature_celsius': 'Get the temperature in degrees Celsius',
    'temperature_fahrenheit': 'Get the temperature in degrees Fahrenheit',
    'weather_conditions': 'Get the current weather conditions',
    'current_time': 'Get the current time',
}

async def add_descriptions(ctx: RunContext, tool_defs: list[ToolDefinition]) -> list[ToolDefinition]:
    return [
        replace(tool_def, description=description)
        if (description := descriptions.get(tool_def.name, None))
        else tool_def
        for tool_def
        in tool_defs
    ]

prepared_toolset = renamed_toolset.prepared(add_descriptions)

test_model = TestModel() # (1)!
agent = Agent(test_model, toolsets=[prepared_toolset])
result = agent.run_sync('What tools are available?')
assert test_model.last_model_request_parameters is not None
print(test_model.last_model_request_parameters.function_tools)
"""
[
    ToolDefinition(
        name='temperature_celsius',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the temperature in degrees Celsius',
    ),
    ToolDefinition(
        name='temperature_fahrenheit',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the temperature in degrees Fahrenheit',
    ),
    ToolDefinition(
        name='weather_conditions',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {'city': {'type': 'string'}},
            'required': ['city'],
            'type': 'object',
        },
        description='Get the current weather conditions',
    ),
    ToolDefinition(
        name='current_time',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {},
            'type': 'object',
        },
        description='Get the current time',
    ),
]
"""
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।

### টুল অনুমোদন বাধ্যতামূলক করা { #requiring-tool-approval }

[`ApprovalRequiredToolset`][pydantic_ai.toolsets.ApprovalRequiredToolset] একটি toolset মুড়ে রাখে আর একটি নির্দিষ্ট টুল কলের জন্য গতিশীলভাবে [অনুমোদন বাধ্যতামূলক](deferred-tools.md#human-in-the-loop-tool-approval) করতে দেয়, একটি ব্যবহারকারী-সংজ্ঞায়িত ফাংশনের ভিত্তিতে যা এজেন্টের [run context][pydantic_ai.tools.RunContext], টুলের [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] আর যাচাই করা টুল কলের আর্গুমেন্ট পায়। কোনো ফাংশন দেওয়া না হলে, সব টুল কলে অনুমোদন লাগবে।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`approval_required()`][pydantic_ai.toolsets.AbstractToolset.approval_required] ডাকুন।

অনুমোদন লাগে এমন টুল ডাকা এজেন্ট রান কীভাবে সামলাবেন আর ফল কীভাবে দেবেন তার আরও তথ্যের জন্য দেখুন [Human-in-the-Loop Tool Approval](deferred-tools.md#human-in-the-loop-tool-approval) ডকুমেন্টেশন।

```python title="approval_required_toolset.py"
from pydantic_ai import Agent, DeferredToolRequests, DeferredToolResults
from pydantic_ai.models.test import TestModel

from prepared_toolset import prepared_toolset

approval_required_toolset = prepared_toolset.approval_required(lambda ctx, tool_def, tool_args: tool_def.name.startswith('temperature'))

test_model = TestModel(call_tools=['temperature_celsius', 'temperature_fahrenheit']) # (1)!
agent = Agent(
    test_model,
    toolsets=[approval_required_toolset],
    output_type=[str, DeferredToolRequests],
)
result = agent.run_sync('Call the temperature tools')
messages = result.all_messages()
print(result.output)
"""
DeferredToolRequests(
    calls=[],
    approvals=[
        ToolCallPart(
            tool_name='temperature_celsius',
            args={'city': 'a'},
            tool_call_id='pyd_ai_tool_call_id__temperature_celsius',
        ),
        ToolCallPart(
            tool_name='temperature_fahrenheit',
            args={'city': 'a'},
            tool_call_id='pyd_ai_tool_call_id__temperature_fahrenheit',
        ),
    ],
    metadata={},
)
"""

result = agent.run_sync(
    message_history=messages,
    deferred_tool_results=DeferredToolResults(
        approvals={
            'pyd_ai_tool_call_id__temperature_celsius': True,
            'pyd_ai_tool_call_id__temperature_fahrenheit': False,
        }
    )
)
print(result.output)
#> {"temperature_celsius":21.0,"temperature_fahrenheit":"The tool call was denied."}
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে কোন টুল ডাকতে হবে তা নির্দিষ্ট করা সহজ।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### Deferred loading { #deferred-loading }

[`DeferredLoadingToolset`][pydantic_ai.toolsets.DeferredLoadingToolset] একটি toolset মুড়ে রাখে আর এর টুলগুলো deferred loading-এর জন্য চিহ্নিত করে, [tool search](tools-advanced.md#tool-search) দিয়ে আবিষ্কার না হওয়া পর্যন্ত মডেলের কাছ থেকে লুকিয়ে। বড় toolset-এর জন্য (যেমন অনেক endpoint-সহ MCP সার্ভার) এটি কাজে লাগে, যেখানে সব টুল সংজ্ঞা মডেলের প্রসঙ্গে লোড করা অপচয় হতো।

[`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset] তার constructor-এ সব টুল deferred loading-এর জন্য চিহ্নিত করতে `defer_loading=True`-ও নেয়। অন্য toolset-এর জন্য, [`.defer_loading()`][pydantic_ai.toolsets.AbstractToolset.defer_loading] ডাকুন — শুধু নির্দিষ্ট টুল লুকাতে টুলের নামের একটি তালিকা দিন, বা সব লুকাতে `None` (ডিফল্ট)।

```python title="deferred_loading_toolset.py"
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

mcp = MCPToolset('http://localhost:8000/mcp')
agent = Agent('openai:gpt-6.1-sol', toolsets=[mcp.defer_loading()])
```

### ফেরত schema রাখা { #including-return-schemas }

[`IncludeReturnSchemasToolset`][pydantic_ai.toolsets.IncludeReturnSchemasToolset] একটি toolset মুড়ে রাখে আর এর সব টুলে `include_return_schema=True` সেট করে, যাতে মডেল ফেরত টাইপের তথ্য পায়। নিজস্বভাবে ফেরত schema সমর্থন করা মডেলে (যেমন Google Gemini), schema একটি গোছানো API ফিল্ড হিসেবে পাঠানো হয়। অন্য মডেলে, এটি JSON লেখা হিসেবে টুলের বর্ণনায় ঢোকানো হয়।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`.include_return_schemas()`][pydantic_ai.toolsets.AbstractToolset.include_return_schemas] ডাকুন।

```python title="include_return_schemas_toolset.py"
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel


def get_temperature(city: str) -> float:
    """Get the temperature for a city."""
    return 21.0


toolset = FunctionToolset(tools=[get_temperature])

test_model = TestModel()
agent = Agent(test_model, toolsets=[toolset.include_return_schemas()])
result = agent.run_sync('What is the temperature?')
params = test_model.last_model_request_parameters
assert params is not None
assert params.function_tools[0].include_return_schema is True
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

এটি [`IncludeToolReturnSchemas`][pydantic_ai.capabilities.IncludeToolReturnSchemas] capability-র toolset-স্তরের সমতুল্য, যা সব toolset বা একটি বাছা উপসেট-জুড়ে প্রযোজ্য।

### টুলের metadata সেট করা { #setting-tool-metadata }

[`SetMetadataToolset`][pydantic_ai.toolsets.SetMetadataToolset] একটি toolset মুড়ে রাখে আর এর সব টুলে metadata key-value জোড়া মেলায়। অন্য capability বা নিজের লজিক পরীক্ষা করতে পারে এমন কনফিগারেশন দিয়ে টুলে ট্যাগ দিতে এটি কাজে লাগে।

রূপান্তর শৃঙ্খলিত করতে, যেকোনো toolset-এ [`.with_metadata()`][pydantic_ai.toolsets.AbstractToolset.with_metadata] ডাকুন।

```python title="set_metadata_toolset.py"
from pydantic_ai import Agent, FunctionToolset
from pydantic_ai.models.test import TestModel


def search(query: str) -> str:
    """Search for information."""
    return f'Results for: {query}'


toolset = FunctionToolset(tools=[search])

test_model = TestModel()
agent = Agent(test_model, toolsets=[toolset.with_metadata(sensitive=True)])
result = agent.run_sync('Search for something')
params = test_model.last_model_request_parameters
assert params is not None
assert params.function_tools[0].metadata is not None
assert params.function_tools[0].metadata['sensitive'] is True
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

এটি [`SetToolMetadata`][pydantic_ai.capabilities.SetToolMetadata] capability-র toolset-স্তরের সমতুল্য, যা সব toolset বা একটি বাছা উপসেট-জুড়ে প্রযোজ্য।

### টুল চালানো বদলানো { #changing-tool-execution }

[`WrapperToolset`][pydantic_ai.toolsets.WrapperToolset] আরেকটি toolset মুড়ে রাখে আর সব দায়িত্ব তাকে দেয়।

এটি ডিফল্টভাবে কিছুই করে না, তবে [`call_tool()`][pydantic_ai.toolsets.AbstractToolset.call_tool] মেথড override করে মোড়ানো toolset-এর টুল চালানোর আচরণ বদলাতে `WrapperToolset`-এর subclass করতে পারেন।

```python title="logging_toolset.py"
import asyncio
from typing import Any

from pydantic_ai import Agent, RunContext, ToolsetTool, WrapperToolset
from pydantic_ai.models.test import TestModel

from prepared_toolset import prepared_toolset

LOG = []

class LoggingToolset(WrapperToolset):
    async def call_tool(self, name: str, tool_args: dict[str, Any], ctx: RunContext, tool: ToolsetTool) -> Any:
        LOG.append(f'Calling tool {name!r} with args: {tool_args!r}')
        try:
            await asyncio.sleep(0.1 * len(LOG)) # (1)!

            result = await super().call_tool(name, tool_args, ctx, tool)
            LOG.append(f'Finished calling tool {name!r} with result: {result!r}')
        except Exception as e:
            LOG.append(f'Error calling tool {name!r}: {e}')
            raise e
        else:
            return result


logging_toolset = LoggingToolset(prepared_toolset)

agent = Agent(TestModel(), toolsets=[logging_toolset]) # (2)!
result = agent.run_sync('Call all the tools')
print(LOG)
"""
[
    "Calling tool 'temperature_celsius' with args: {'city': 'a'}",
    "Calling tool 'temperature_fahrenheit' with args: {'city': 'a'}",
    "Calling tool 'weather_conditions' with args: {'city': 'a'}",
    "Calling tool 'current_time' with args: {}",
    "Finished calling tool 'temperature_celsius' with result: 21.0",
    "Finished calling tool 'temperature_fahrenheit' with result: 69.8",
    'Finished calling tool \'weather_conditions\' with result: "It\'s raining"',
    "Finished calling tool 'current_time' with result: datetime.datetime(...)",
]
"""
```

1. সব ডক উদাহরণ CI-তে টেস্ট হয় আর তাদের আউটপুট যাচাই হয়, তাই এই কোড যখনই চলুক `LOG`-এর সবসময় একই ক্রম থাকা দরকার। যেহেতু টুলগুলো যেকোনো ক্রমে শেষ হতে পারে, আমরা কততম টুল কল তার ভিত্তিতে ক্রমবর্ধমান সময় ঘুমাই, যাতে সেগুলো যে ক্রমে ডাকা হয়েছে সেই ক্রমে শেষ (আর লগ) হয়।
2. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করি কারণ এটি নিজে থেকে প্রতিটি টুল ডাকবে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// info | এক নজরে: কোন wrapper কী করে

| পদ্ধতি | কাজ |
| --- | --- |
| `.filtered(fn)` | শর্ত অনুযায়ী কিছু টুল লুকায় |
| `.prefixed('x')` | সব নামের আগে `x_` যোগ করে |
| `.renamed({...})` | নির্দিষ্ট নাম বদলায় |
| `.prepared(fn)` | প্রতি ধাপে সংজ্ঞা বদলায় |
| `.approval_required(fn)` | চালানোর আগে অনুমোদন চায় |
| `.defer_loading()` | tool search-এর পেছনে লুকায় |
| `.with_metadata(...)` | metadata ট্যাগ দেয় |
| `WrapperToolset` subclass | `call_tool()` override করে চালানো বদলায় |

///

## External toolset { #external-toolset }

আপনার এজেন্টের যদি এমন [বাইরের টুল](deferred-tools.md#external-tool-execution) ডাকতে পারা দরকার যা একটি upstream সার্ভিস বা frontend দেয় আর চালায়, তাহলে টুলের নাম, আর্গুমেন্টের JSON schema আর বর্ণনাসহ [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এর একটি তালিকা থেকে একটি [`ExternalToolset`][pydantic_ai.toolsets.ExternalToolset] তৈরি করতে পারেন।

মডেল একটি বাইরের টুল ডাকলে, কলটি ["deferred"](deferred-tools.md#deferred-tools) ধরা হয়, আর এজেন্ট রান একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট অবজেক্ট দিয়ে শেষ হবে, যার একটি `calls` তালিকায় থাকে টুলের নাম, যাচাই করা আর্গুমেন্ট আর একটি অনন্য টুল কল ID-সহ [`ToolCallPart`][pydantic_ai.messages.ToolCallPart], যা ফল তৈরি করবে এমন upstream সার্ভিস বা frontend-এ পাঠানো হবে বলে আশা করা হয়।

upstream সার্ভিস বা frontend থেকে টুল কলের ফল পেলে, একটি `calls` dictionary-সহ একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] অবজেক্ট তৈরি করতে পারেন, যা প্রতিটি টুল কল ID-কে ম্যাপ করে মডেলে ফেরত দেওয়ার একটি যেকোনো মানে, একটি [`ToolReturn`](tools-advanced.md#advanced-tool-returns) অবজেক্টে, বা টুল কল ব্যর্থ হলে একটি exception-এ: মডেলের [আবার চেষ্টা করা](tools-advanced.md#tool-retries) উচিত হলে একটি [`ModelRetry`][pydantic_ai.exceptions.ModelRetry], বা ব্যর্থতা মডেলকে একটি [ব্যর্থ ফল](tools-advanced.md#tool-failed) হিসেবে জানানো উচিত হলে (টুলের retry বাজেট খরচ না করে) একটি [`ToolFailed`][pydantic_ai.exceptions.ToolFailed], যাতে এটি কীভাবে এগোবে তা ঠিক করতে পারে। এই `DeferredToolResults` অবজেক্ট তারপর মূল রানের [বার্তার ইতিহাসের](message-history.md) পাশাপাশি `deferred_tool_results` হিসেবে এজেন্ট রান মেথডগুলোর একটিতে দেওয়া যায়।

মনে রাখবেন `Agent`-এর বা `agent.run()`-এর [`output_type`](output.md#structured-output)-এ `DeferredToolRequests` যোগ করতে হবে, যাতে এজেন্ট রানের আউটপুটের সম্ভাব্য টাইপ সঠিকভাবে অনুমিত হয়। আরও তথ্যের জন্য দেখুন [Deferred Tools](deferred-tools.md#deferred-tools) ডকুমেন্টেশন।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি টুল ব্রাউজারের ভাষা জানতে চায় (`navigator.language`) — এটি সার্ভারে চালানো সম্ভব নয়, শুধু ব্যবহারকারীর ব্রাউজারে। তাই এজেন্ট বলে "এই টুলটি চালাতে হবে" আর থেমে যায় (`DeferredToolRequests`)। frontend টুলটি চালিয়ে ফল (`DeferredToolResults`) পাঠায়, আর এজেন্ট সেখান থেকে চালিয়ে যায়।

///

দেখাতে, চলুন প্রথমে deferred টুল _ছাড়া_ একটি সহজ এজেন্ট সংজ্ঞায়িত করি:

```python title="deferred_toolset_agent.py"
from pydantic import BaseModel

from pydantic_ai import Agent, FunctionToolset

toolset = FunctionToolset()


@toolset.tool_plain
def get_default_language():
    return 'en-US'


@toolset.tool_plain
def get_user_name():
    return 'David'


class PersonalizedGreeting(BaseModel):
    greeting: str
    language_code: str


agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset], output_type=PersonalizedGreeting)

result = agent.run_sync('Greet the user in a personalized way')
print(repr(result.output))
#> PersonalizedGreeting(greeting='Hello, David!', language_code='en-US')
```

এরপর, চলুন একটি ফাংশন সংজ্ঞায়িত করি যা একটি কাল্পনিক "run agent" API endpoint-এর প্রতিনিধিত্ব করে, যা frontend ডাকতে পারে আর মডেলে পাঠানোর বার্তার একটি তালিকা, frontend টুল সংজ্ঞার একটি তালিকা, আর ঐচ্ছিক deferred টুল ফল নেয়। এখানেই `ExternalToolset`, `DeferredToolRequests` আর `DeferredToolResults` আসে:

```python title="deferred_toolset_api.py"
from pydantic_ai import (
    DeferredToolRequests,
    DeferredToolResults,
    ExternalToolset,
    ModelMessage,
    ToolDefinition,
)

from deferred_toolset_agent import PersonalizedGreeting, agent


def run_agent(
    messages: list[ModelMessage] = [],
    frontend_tools: list[ToolDefinition] = [],
    deferred_tool_results: DeferredToolResults | None = None,
) -> tuple[PersonalizedGreeting | DeferredToolRequests, list[ModelMessage]]:
    deferred_toolset = ExternalToolset(frontend_tools)
    result = agent.run_sync(
        toolsets=[deferred_toolset], # (1)!
        output_type=[agent.output_type, DeferredToolRequests], # (2)!
        message_history=messages, # (3)!
        deferred_tool_results=deferred_tool_results,
    )
    return result.output, result.new_messages()
```

1. [Deferred Tools](deferred-tools.md#deferred-tools) ডকুমেন্টেশনে যেমন বলা হয়েছে, এই `toolsets` `Agent` constructor-এ দেওয়াগুলোর বাড়তি
2. [Deferred Tools](deferred-tools.md#deferred-tools) ডকুমেন্টেশনে যেমন বলা হয়েছে, এই `output_type` `Agent` constructor-এ দেওয়াটি override করে, তাই আমাদের নিশ্চিত করতে হবে যেন এটি না হারাই
3. আমরা কোনো `user_prompt` keyword আর্গুমেন্ট রাখি না কারণ আমরা আশা করি frontend এটি `messages` দিয়ে দেবে

এখন, কল্পনা করুন নিচের কোডটি frontend-এ বাস্তবায়িত, আর `run_agent` এজেন্ট চালানো backend-এর একটি API কলের প্রতিনিধি। এখানেই আমরা আসলে deferred টুল কল চালাই আর নতুন ফলসহ একটি নতুন রান শুরু করি:

```python title="deferred_tools.py"
from pydantic_ai import (
    DeferredToolRequests,
    DeferredToolResults,
    ModelMessage,
    ModelRequest,
    ModelRetry,
    ToolDefinition,
    UserPromptPart,
)

from deferred_toolset_api import run_agent

frontend_tool_definitions = [
    ToolDefinition(
        name='get_preferred_language',
        parameters_json_schema={'type': 'object', 'properties': {'default_language': {'type': 'string'}}},
        description="Get the user's preferred language from their browser",
    )
]

def get_preferred_language(default_language: str) -> str:
    return 'es-MX' # (1)!

frontend_tool_functions = {'get_preferred_language': get_preferred_language}

messages: list[ModelMessage] = [
    ModelRequest(
        parts=[
            UserPromptPart(content='Greet the user in a personalized way')
        ]
    )
]

deferred_tool_results: DeferredToolResults | None = None

final_output = None
while True:
    output, new_messages = run_agent(messages, frontend_tool_definitions, deferred_tool_results)
    messages += new_messages

    if not isinstance(output, DeferredToolRequests):
        final_output = output
        break

    print(output.calls)
    """
    [
        ToolCallPart(
            tool_name='get_preferred_language',
            args={'default_language': 'en-US'},
            tool_call_id='pyd_ai_tool_call_id',
        )
    ]
    """
    deferred_tool_results = DeferredToolResults()
    for tool_call in output.calls:
        if function := frontend_tool_functions.get(tool_call.tool_name):
            result = function(**tool_call.args_as_dict())
        else:
            result = ModelRetry(f'Unknown tool {tool_call.tool_name!r}')
        deferred_tool_results.calls[tool_call.tool_call_id] = result

print(repr(final_output))
"""
PersonalizedGreeting(greeting='Hola, David! Espero que tengas un gran día!', language_code='es-MX')
"""
```

1. কল্পনা করুন এটি frontend-এর [`navigator.language`](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/language) ফেরত দেয়।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## গতিশীলভাবে একটি toolset তৈরি { #dynamically-building-a-toolset }

প্রতিটি এজেন্ট রান বা রান ধাপের আগে এমন একটি ফাংশন দিয়ে toolset গতিশীলভাবে তৈরি করা যায় যা এজেন্টের [run context][pydantic_ai.tools.RunContext] নিয়ে একটি toolset বা `None` ফেরত দেয়। এটি কাজে লাগে যখন একটি toolset (যেমন একটি MCP সার্ভার) একটি এজেন্ট রানের নির্দিষ্ট তথ্যের ওপর নির্ভর করে, যেমন এর [dependencies](./dependencies.md) — যেমন [প্রতি-ব্যবহারকারী credential দিয়ে একটি MCP সার্ভারে সংযোগ](mcp/client.md#per-user-authentication) করতে।

একটি গতিশীল toolset নথিভুক্ত করতে, `Agent` constructor-এর `toolsets` আর্গুমেন্টে [`RunContext`][pydantic_ai.tools.RunContext] নেয় এমন একটি ফাংশন দিতে পারেন, বা একটি মানানসই ফাংশন [`@agent.toolset`][pydantic_ai.agent.Agent.toolset] decorator-এ মুড়তে পারেন।

ডিফল্টভাবে, ফাংশনটি প্রতিটি এজেন্ট রান ধাপের আগে আবার ডাকা হবে। decorator ব্যবহার করলে, toolset পুরো রানের জন্য শুধু একবার তৈরি করতে হবে বোঝাতে ঐচ্ছিকভাবে একটি `per_run_step=False` আর্গুমেন্ট দিতে পারেন।

ফাংশনটি যে toolset ফেরত দেয় তার নির্দেশনা গতিশীল toolset-এর নামে ধরা হয়, তাই সেগুলো `on_change='append'` ব্যবহার করতে, decorator-কে একটি `id` দিন: `@agent.toolset(id='orders')`।

```python title="dynamic_toolset.py"
from dataclasses import dataclass
from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset


@dataclass
class ToggleableDeps:
    active: Literal['weather', 'datetime']

    def toggle(self):
        if self.active == 'weather':
            self.active = 'datetime'
        else:
            self.active = 'weather'

test_model = TestModel()  # (1)!
agent = Agent(
    test_model,
    deps_type=ToggleableDeps  # (2)!
)

@agent.toolset
def toggleable_toolset(ctx: RunContext[ToggleableDeps]):
    if ctx.deps.active == 'weather':
        return weather_toolset
    else:
        return datetime_toolset

@agent.tool
def toggle(ctx: RunContext[ToggleableDeps]):
    ctx.deps.toggle()

deps = ToggleableDeps('weather')

result = agent.run_sync('Toggle the toolset', deps=deps)
assert test_model.last_model_request_parameters is not None
print([t.name for t in test_model.last_model_request_parameters.function_tools])  # (3)!
#> ['toggle', 'now']

result = agent.run_sync('Toggle the toolset', deps=deps)
print([t.name for t in test_model.last_model_request_parameters.function_tools])
#> ['toggle', 'temperature_celsius', 'temperature_fahrenheit', 'conditions']
```

1. আমরা এখানে [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করছি কারণ এতে প্রতিটি রানে কোন টুল উপলব্ধ ছিল তা দেখা সহজ।
2. `RunContext` আর্গুমেন্ট দিয়ে `toggle` টুলকে `active`-এ প্রবেশ দিতে আমরা এজেন্টের dependencies ব্যবহার করছি।
3. এটি `toggle` টুল চলার _পরে_ উপলব্ধ টুল দেখায়, কারণ "শেষ মডেল রিকোয়েস্ট" ছিল সেটি যা মডেলে `toggle` টুলের ফল ফেরত দিয়েছিল।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## একটি নিজের toolset তৈরি { #building-a-custom-toolset }

উপলব্ধ টুলের তালিকা আর সেগুলো ডাকা সামলানোর নিজস্ব লজিকসহ একটি পুরোপুরি নিজের toolset সংজ্ঞায়িত করতে, [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset]-এর subclass করে [`get_tools()`][pydantic_ai.toolsets.AbstractToolset.get_tools] আর [`call_tool()`][pydantic_ai.toolsets.AbstractToolset.call_tool] মেথড বাস্তবায়ন করতে পারেন।

toolset-এর টুল কীভাবে ব্যবহার করতে হবে তার একটি বর্ণনা দিতে [`get_instructions()`][pydantic_ai.toolsets.AbstractToolset.get_instructions] মেথডও override করতে পারেন। এটি এজেন্টের নির্দেশনায় ঢোকানো হবে আর মডেলকে আপনার toolset-এর টুল কার্যকরভাবে কীভাবে ব্যবহার করবে তা বুঝতে সাহায্যে কাজে লাগে।

toolset-এর একটি [`id`][pydantic_ai.toolsets.AbstractToolset.id] থাকলে আর এটি নির্দেশনা দিলে, সেই id একটি এজেন্টে নথিভুক্ত toolset-এর মধ্যে অনন্য হতে হবে, একটি [capability](capabilities/overview.md)-র দেওয়াগুলো গুনে। এর নির্দেশনা মডেলে পৌঁছায় `'toolset:<toolset id>'` দিয়ে চিহ্নিত [instruction parts](agent.md#instruction-parts) হিসেবে, তাই একটি অ্যাপ্লিকেশন তাদের শব্দের চেয়ে দীর্ঘজীবী একটি key দিয়ে সেগুলোতে পৌঁছাতে পারে। toolset যে প্রতিটি অংশ ফেরত দেয় তা সেই একটি key বহন করে; একটি অংশকে আলাদাভাবে পৌঁছানোযোগ্য চাইলে, আপনার toolset-এর সাপেক্ষে একটি `name`-সহ (`'limits'`) একটি [`InstructionPart`][pydantic_ai.messages.InstructionPart] ফেরত দিন, যা framework `'toolset:weather:limits'`-এ যোগ্য করে। নিজের id লিখে দেবেন না — framework আগেই যা জানে তা পুনরাবৃত্তি করতেন, আর আপনার নিজের একটি নাম একটি শীর্ষ-স্তরের key-এর সাথে গুলিয়ে যেতে পারে না।

একটি `id`-সহ একটি [wrapper toolset](#changing-tool-execution) যা `get_instructions()` override করে, `super().get_instructions(ctx)` তাকে যে অংশ-অবজেক্ট দিয়েছে হুবহু সেগুলো অপরিবর্তিত ফেরত দিয়ে যা মোড়ায় তা এগিয়ে দিতে পারে: সেগুলো যে toolset লিখেছে তাদের id রাখে, বা তাদের toolset-এর id না থাকলে কোনো id নয়। বাকি প্রতিটি অংশ wrapper-এর নিজের id দিয়ে key করা: যেগুলো এটি যোগ করে, যেগুলো জায়গায় বদলায়, আর কপিগুলো, এমনকি `replace(part)`-এর মতো একটি অপরিবর্তিত কপি যা তখনো যে অংশ থেকে এসেছে তার id বহন করে। একটি [গতিশীল toolset](#dynamically-building-a-toolset) যে toolset তৈরি করে তা এভাবে মোড়ানো হয় না, তাই এটি যা বলে তার সবকিছু গতিশীল toolset-এর id দিয়ে key করা।

`get_instructions()` প্রতিটি মডেল রিকোয়েস্টের আগে ডাকা হয়। এটি যা ফেরত দেয় তা একটি কথোপকথনের সময় বদলাতে পারলে, `InstructionPart`-এ `on_change='append'` সেট করুন যাতে পরিবর্তনগুলো cache করা prefix নতুন করে না লিখে ইতিহাসে [জোড়া](agent.md#appending-instruction-changes) হয়; দেখুন [Toolset instructions that change](#toolset-instructions-that-change)।

/// tip | পরামর্শ

আপনার toolset-এর মডেল সেটিং বা hook-ও দেওয়া দরকার হলে, বদলে একটি [নিজের capability](capabilities/custom.md) তৈরির কথা ভাবুন।

///

toolset-এর জীবনচক্র বিভিন্ন পরিসরে অবস্থা সামলানোর hook দেয়:

- [`for_run()`][pydantic_ai.toolsets.AbstractToolset.for_run]: প্রতিটি এজেন্ট রানের আগে একবার ডাকা হয়। প্রতি-রান অবস্থা বিচ্ছিন্ন করতে একটি নতুন instance ফেরত দিন (যেমন গণক রিসেট, একটি নতুন session তৈরি)। framework ফেরত দেওয়া instance-এ ঢোকে আর বেরোয়।
- [`for_run_step()`][pydantic_ai.toolsets.AbstractToolset.for_run_step]: প্রতিটি রান ধাপের শুরুতে ডাকা হয়। প্রতি-ধাপের অবস্থা-পরিবর্তনের জন্য একটি বদলানো instance ফেরত দিন। ভেতরের toolset-এর পরিবর্তন সামলালে (যেমন একটি toolset আরেকটি দিয়ে বদলানো), ভেতরের জীবনচক্রের দায়িত্ব আপনার (পুরনোটি থেকে বেরোনো, নতুনটিতে ঢোকা)।
- [`__aenter__()`][pydantic_ai.toolsets.AbstractToolset.__aenter__] আর [`__aexit__()`][pydantic_ai.toolsets.AbstractToolset.__aexit__]: এজেন্ট রানের সময়কাল পর্যন্ত টিকে থাকা উচিত এমন রিসোর্স (যেমন নেটওয়ার্ক সংযোগ) সেট আপ আর বন্ধ করা।

### প্রতি-রান আর প্রতি-ধাপের জীবনচক্র { #per-run-and-per-step-lifecycle }

Toolset প্রতি-রান বিচ্ছিন্নতা আর প্রতি-ধাপের অবস্থা ব্যবস্থাপনার জন্য জীবনচক্র hook সমর্থন করে:

- [`for_run(ctx)`][pydantic_ai.toolsets.AbstractToolset.for_run] -- প্রতিটি এজেন্ট রানে একবার ডাকা হয়, `__aenter__`-এর আগে। রানগুলোর মধ্যে অবস্থা বিচ্ছিন্ন করতে একটি নতুন instance ফেরত দিন। ডিফল্ট: `self` ফেরত দেয়।
- [`for_run_step(ctx)`][pydantic_ai.toolsets.AbstractToolset.for_run_step] -- প্রতিটি রান ধাপের শুরুতে ডাকা হয়। ভেতরের পরিবর্তন (যেমন টুলের উপলব্ধতা হালনাগাদ) জায়গায় সামলান। ডিফল্ট: `self` ফেরত দেয়।

## Third-party toolset { #third-party-toolsets }

Third-party toolset-কেও [capabilities](capabilities/overview.md) হিসেবে মোড়ানো যায়, যা hook, নির্দেশনা আর মডেল সেটিংসহ টুল বান্ডেল করে। পুরো ইকোসিস্টেমের জন্য দেখুন [Extensibility](extensibility.md)। skills, পরিকল্পনা, file system আর shell প্রবেশ, sandbox-এ কোড চালানো আর আরও অনেক কিছুর জন্য, দেখুন [capability index](capabilities/overview.md#available-capabilities), যা Pydantic AI আর [Pydantic AI Harness](harness/index.md) ঢাকে।

### MCP সার্ভার { #mcp-servers }

Pydantic AI লোকাল আর দূরের MCP সার্ভারে সংযোগ আর তাদের টুল ডাকার জন্য [`MCPToolset`][pydantic_ai.mcp.MCPToolset] দেয়, প্রস্তাবিত উচ্চ-স্তরের প্রবেশপথ হিসেবে [`MCP` capability](capabilities/mcp.md)-সহ। বিস্তারিত জানতে দেখুন [MCP overview](./mcp/overview.md) আর [MCP client](./mcp/client.md) ডকুমেন্টেশন।

### LangChain টুল { #langchain-tools }

LangChain-এর [community tool library](https://python.langchain.com/docs/integrations/tools/) থেকে টুল বা একটি [toolkit](https://python.langchain.com/docs/concepts/tools/#toolkits) Pydantic AI-এর সাথে ব্যবহার করতে চাইলে, [`LangChainToolset`][pydantic_ai.ext.langchain.LangChainToolset] ব্যবহার করতে পারেন, যা LangChain টুলের একটি তালিকা নেয়। মনে রাখবেন এই ক্ষেত্রে Pydantic AI আর্গুমেন্ট যাচাই করবে না -- LangChain টুলের নির্দিষ্ট schema মেনে আর্গুমেন্ট দেওয়া মডেলের দায়িত্ব, আর আর্গুমেন্ট অবৈধ হলে একটি এরর তোলা LangChain টুলের দায়িত্ব।

আপনাকে `langchain-community` প্যাকেজ আর সংশ্লিষ্ট টুলের দরকারি অন্যগুলো ইনস্টল করতে হবে।

```python
from langchain_community.agent_toolkits import SlackToolkit

from pydantic_ai import Agent
from pydantic_ai.ext.langchain import LangChainToolset

toolkit = SlackToolkit()
toolset = LangChainToolset(toolkit.get_tools())

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
# ...
```

### pydantic-ai-ejentum { #ejentum-tools }

[`pydantic-ai-ejentum`](https://pypi.org/project/pydantic-ai-ejentum/) [Ejentum Reasoning Harness](https://ejentum.com)-কে একটি `FunctionToolset` subclass হিসেবে মোড়ায়। `EjentumToolset` চারটি এজেন্ট-ডাকার-যোগ্য টুল নথিভুক্ত করে (`harness_reasoning`, `harness_code`, `harness_anti_deception`, `harness_memory`)। এজেন্ট তৈরির আগে একটি ডাকে; প্রতিটি কল একটি গোছানো cognitive scaffold ফেরত দেয় (নামযুক্ত ব্যর্থতার ধরন, চালানোযোগ্য পদ্ধতি, দমনের দিক, মিথ্যা প্রমাণের পরীক্ষা) যা মডেল তার পরের উত্তর গড়তে ভেতরে পড়ে।

আপনাকে `pydantic-ai-ejentum` প্যাকেজ ইনস্টল করতে হবে আর আপনার Ejentum API key `EJENTUM_API_KEY` environment variable-এ সেট করতে হবে (বিনামূল্যে আর paid tier আছে <https://ejentum.com/pricing>-এ), বা constructor-এ `api_key=` দিন।

```python
from pydantic_ai import Agent
from pydantic_ai_ejentum import EjentumToolset

toolset = EjentumToolset()

agent = Agent('openai:gpt-6.1-sol', toolsets=[toolset])
```

toolset Pydantic AI `instructions` দেয়, যা এজেন্টকে তৈরির আগে মেলা `harness_*` টুল ডাকতে ঠেলে দেয়। দমন করতে আর নিজের system prompt থেকে routing নির্দেশনা দিতে `add_instructions=False` দিন।

/// check | সংক্ষেপে মনে রাখুন

* toolset = টুলের বাক্স; `Agent(toolsets=[...])`, `agent.run(toolsets=[...])`, `@agent.toolset` বা `agent.override(toolsets=...)`।
* `FunctionToolset` লোকাল ফাংশনের জন্য; নিজস্ব `instructions`-ও বহন করতে পারে।
* `.filtered()`, `.prefixed()`, `.renamed()`, `.prepared()`, `.approval_required()`, `.defer_loading()` দিয়ে জোড়া লাগানো।
* frontend-এর টুলে `ExternalToolset` + `DeferredToolRequests`/`DeferredToolResults`।
* নিজের toolset-এ `get_tools()` আর `call_tool()`; প্রতি-রান অবস্থায় `for_run()`।

///
