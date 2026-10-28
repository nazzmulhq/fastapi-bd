# আউটপুট (Output) { #output }

/// note | এই পেজে যা শিখবেন

* এজেন্টের "আউটপুট" কী: সাধারণ লেখা, গোছানো ডেটা (Pydantic মডেল ইত্যাদি), ছবি, বা একটি ফাংশনের ফল।
* `output_type` দিয়ে উত্তরের গঠন ঠিক করা, আর আউটপুট ফাংশন।
* আউটপুটের তিনটি মোড: Tool, Native, Prompted — কোনটি কখন।
* `StructuredDict`, চলার সময় জানা বিকল্প (`Choices`), আউটপুট validator, আর আউটপুট stream করা।

///

"আউটপুট" বলতে বোঝায় [একটি এজেন্ট চালানোর](agent.md#running-agents) শেষে ফেরত পাওয়া চূড়ান্ত মান। এটি হতে পারে সাধারণ লেখা, [গোছানো ডেটা](#structured-output), একটি [ছবি](#image-output), বা মডেলের দেওয়া আর্গুমেন্ট দিয়ে ডাকা একটি [ফাংশনের](#output-functions) ফল।

আউটপুটটি [`AgentRunResult`][pydantic_ai.agent.AgentRunResult] বা [`StreamedRunResult`][pydantic_ai.result.StreamedRunResult]-এ মোড়ানো থাকে, যাতে অন্য তথ্যও পেতে পারেন, যেমন রানের [ব্যবহার][pydantic_ai.usage.RunUsage] আর [বার্তার ইতিহাস](message-history.md#accessing-messages-from-results)।

`AgentRunResult` আর `StreamedRunResult` দুটোই যে ডেটা মোড়ায় তাতে generic, তাই এজেন্টের ফেরত দেওয়া ডেটার টাইপের তথ্য রক্ষিত থাকে।

একটি রান শেষ হয় যখন মডেল আউটপুট টাইপগুলোর একটি দিয়ে উত্তর দেয়, অথবা, কোনো আউটপুট টাইপ দেওয়া না থাকলে বা `str` অনুমোদিত বিকল্পগুলোর একটি হলে, যখন একটি সাধারণ লেখার উত্তর আসে। ব্যবহারের সীমা পেরোলেও একটি রান বাতিল হতে পারে, দেখুন [Usage Limits](agent.md#usage-limits)।

/// tip | উদাহরণ দিয়ে বুঝি

LLM-কে খোলা প্রশ্ন করলে সে রচনা লেখে: "লন্ডন একটি সুন্দর শহর, যার জনসংখ্যা প্রায়..."। `output_type` হলো তাকে একটি ছক কাটা ফর্ম দেওয়া: "শহর: ___, দেশ: ___"। Pydantic সেই ফর্ম যাচাই করে; ভুল থাকলে মডেলকে আবার লিখতে বলে। ফলে আপনার কোড পায় একটি নির্ভরযোগ্য Python অবজেক্ট, লেখা থেকে তথ্য ছেঁকে বের করতে হয় না।

///

আমাদের নির্ধারিত গঠনের সাথে মেলে এমন ডেটা দিয়ে মডেলকে উত্তর দিতে বাধ্য করে, `output_type` হিসেবে একটি Pydantic মডেল ব্যবহারের উদাহরণ:

```python title="olympics.py"
from pydantic import BaseModel

from pydantic_ai import Agent


class CityLocation(BaseModel):
    city: str
    country: str


agent = Agent('google:gemini-3.8-flash', output_type=CityLocation)
result = agent.run_sync('Where were the olympics held in 2012?')
print(result.output)
#> city='London' country='United Kingdom'
print(result.usage)
#> RunUsage(cost=Decimal('0.00007275'), input_tokens=57, output_tokens=8, requests=1)
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## গোছানো আউটপুট ডেটা { #structured-output }

[`Agent`][pydantic_ai.Agent] ক্লাসের constructor একটি `output_type` আর্গুমেন্ট নেয়, যা এক বা একাধিক টাইপ বা [আউটপুট ফাংশন](#output-functions) নেয়। এটি সমর্থন করে সাধারণ scalar টাইপ, list আর dict টাইপ (`TypedDict` আর [`StructuredDict`](#structured-dict)-সহ), dataclass আর Pydantic মডেল, সাথে টাইপের union -- সাধারণভাবে একটি Pydantic মডেলে type hint হিসেবে সমর্থিত সবকিছু। একাধিক বিকল্পের একটি তালিকাও দিতে পারেন।

ডিফল্টভাবে, মডেলকে গোছানো ডেটা ফেরত দেওয়াতে Pydantic AI মডেলের টুল-কল ক্ষমতা কাজে লাগায়। একাধিক আউটপুট টাইপ দেওয়া হলে (একটি union বা তালিকায়), schema-র জটিলতা কমাতে আর মডেলের সঠিক উত্তর দেওয়ার সম্ভাবনা বাড়াতে প্রতিটি সদস্য মডেলের কাছে আলাদা আউটপুট টুল হিসেবে নথিভুক্ত হয়। বিভিন্ন ধরনের মডেলে এটি ভালো কাজ করে বলে দেখা গেছে। আউটপুট টুলের নাম বদলাতে, মডেলের নিজস্ব structured output সুবিধা ব্যবহার করতে, বা মডেলের [নির্দেশনায়](agent.md#instructions) আউটপুট schema দিতে চাইলে, একটি [আউটপুট মোড](#output-modes) চিহ্নিতকারী ক্লাস ব্যবহার করতে পারেন।

কোনো আউটপুট টাইপ দেওয়া না থাকলে, বা আউটপুট টাইপগুলোর মধ্যে `str` থাকলে, মডেলের যেকোনো সাধারণ লেখার উত্তর আউটপুট ডেটা হিসেবে ব্যবহার হবে।
আউটপুট টাইপগুলোর মধ্যে `str` না থাকলে, মডেলকে গোছানো ডেটা ফেরত দিতে বা একটি আউটপুট ফাংশন ডাকতে বাধ্য করা হয়।

আউটপুট টাইপের schema যদি `"object"` টাইপের না হয় (যেমন `int` বা `list[int]`), আউটপুট টাইপটি একটি এক-উপাদানের অবজেক্টে মোড়ানো হয়, যাতে মডেলের কাছে নথিভুক্ত সব টুলের schema অবজেক্ট schema হয়।

গোছানো আউটপুট (টুলের মতোই) টুলের জন্য ব্যবহৃত JSON schema তৈরি করতে আর মডেলের ফেরত দেওয়া ডেটা যাচাই করতে Pydantic ব্যবহার করে।

/// note | Type checking নিয়ে বিবেচনা

Agent ক্লাস তার আউটপুট টাইপে generic, আর এই টাইপ `AgentRunResult.output` আর `StreamedRunResult.output`-এ বহন করা হয়, যাতে আপনার কোড ওই আউটপুটগুলোর সম্ভাব্য সব মান ঠিকভাবে বিবেচনা না করলে আপনার IDE বা static type checker সতর্ক করতে পারে।

pyright আর mypy-এর মতো static type checker আপনার দেওয়া `output_type` থেকে এজেন্টের আউটপুট টাইপ বের করতে যথাসাধ্য চেষ্টা করে, কিন্তু আপনি ফাংশন বা একটি union বা তালিকায় একাধিক টাইপ দিলে তারা সবসময় সঠিকভাবে তা পারে না, যদিও Pydantic AI সঠিকভাবেই কাজ করবে। এমন হলে, আপনি নিশ্চিত যে একটি বৈধ `output_type` দিয়েছেন তবুও আপনার type checker আপত্তি করবে, আর `Agent` constructor-এ generic প্যারামিটার স্পষ্টভাবে দিয়ে type checker-কে সাহায্য করতে হবে। এটি দেখানো আছে নিচের দ্বিতীয় উদাহরণে আর আরও নিচের আউটপুট ফাংশনের উদাহরণে।

বিশেষ করে, `output_type`-এর তিনটি বৈধ ব্যবহারে আপনাকে এটি করতে হবে:

1. mypy বা 1.1.412-এর আগের Pyright-এ: সাধারণ ক্লাস নয় এমন একটি টাইপ-প্রকাশ ব্যবহার করলে, যেমন একটি union `output_type=Foo | Bar`, একটি `Literal['a', 'b']`, বা একটি শর্তযুক্ত `Annotated[float, Field(ge=0, le=1)]`। Pyright 1.1.412 আর পরের সংস্করণ এগুলোকে [PEP 747](https://peps.python.org/pep-0747/) type form হিসেবে গ্রহণ করে আর এরা যে টাইপ বোঝায় তা বের করে, কিন্তু mypy আর পুরনো Pyright সংস্করণ এগুলোকে `output_type`-এর বৈধ মান মনে করে না। `Agent` constructor-এর generic প্যারামিটারের পাশাপাশি, `output_type`-এ টাইপ-প্রকাশ দেওয়া লাইনে `# type: ignore` যোগ করতে হবে। একটি union-এর ক্ষেত্রে, বিকল্প হিসেবে একটি তালিকা ব্যবহার করতে পারেন: `output_type=[Foo, Bar]`।
2. mypy-তে: একটি তালিকা ব্যবহার করলে, একটি union-এর কার্যত সমতুল্য বিকল্প হিসেবে, বা কারণ আপনি [আউটপুট ফাংশন](#output-functions) দিচ্ছেন। Pyright এটি সঠিকভাবে সামলায়, আর এটি ঠিক করাতে আমরা mypy-তে [একটি issue](https://github.com/python/mypy/issues/19142) খুলেছি।
3. mypy-তে: একটি async আউটপুট ফাংশন ব্যবহার করলে। Pyright এটি সঠিকভাবে সামলায়, আর এটি ঠিক করাতে আমরা mypy-তে [একটি issue](https://github.com/python/mypy/issues/19143) খুলেছি।

///

লেখা বা গোছানো ডেটা, যেকোনো একটি ফেরত দেওয়ার একটি উদাহরণ:

```python title="box_or_error.py"

from pydantic import BaseModel

from pydantic_ai import Agent


class Box(BaseModel):
    width: int
    height: int
    depth: int
    units: str


agent = Agent(
    'openai:gpt-6-luna',
    output_type=[Box, str], # (1)!
    instructions=(
        "Extract me the dimensions of a box, "
        "if you can't extract all data, ask the user to try again."
    ),
)

result = agent.run_sync('The box is 10x20x30')
print(result.output)
#> Please provide the units for the dimensions (e.g., cm, in, m).

result = agent.run_sync('The box is 10x20x30 cm')
print(result.output)
#> width=10 height=20 depth=30 units='cm'
```

1. এটি একটি union-ও হতে পারত: `output_type=Box | str`। তবে ওপরের "Type checking নিয়ে বিবেচনা" অংশে যেমন ব্যাখ্যা করা হয়েছে, mypy বা পুরনো Pyright সংস্করণে সঠিকভাবে type check হতে এর জন্য `Agent` constructor-এ স্পষ্টভাবে generic প্যারামিটার দেওয়া আর এই লাইনে `# type: ignore` যোগ করা লাগত।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

একটি union ফেরত টাইপ ব্যবহারের একটি উদাহরণ, যা একাধিক আউটপুট টুল নথিভুক্ত করবে আর অবজেক্ট নয় এমন schema একটি অবজেক্টে মোড়াবে:

```python title="colors_or_sizes.py"
from pydantic_ai import Agent

agent = Agent[object, list[str] | list[int]](
    'openai:gpt-6-luna',
    output_type=list[str] | list[int],  # (1)!
    instructions='Extract either colors or sizes from the shapes provided.',
)

result = agent.run_sync('red square, blue circle, green triangle')
print(result.output)
#> ['red', 'blue', 'green']

result = agent.run_sync('square size 10, circle size 20, triangle size 30')
print(result.output)
#> [10, 20, 30]
```

1. ওপরের "Type checking নিয়ে বিবেচনা" অংশে যেমন ব্যাখ্যা করা হয়েছে, mypy বা পুরনো Pyright সংস্করণে, একটি তালিকার বদলে একটি union ব্যবহার করলে সঠিকভাবে type check হতে `Agent` constructor-এ স্পষ্টভাবে generic প্যারামিটার দেওয়া আর এই লাইনে `# type: ignore` যোগ করা লাগে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### আউটপুট ফাংশন { #output-functions }

সাধারণ লেখা বা গোছানো ডেটার বদলে, আপনি হয়তো চাইবেন আপনার এজেন্ট রানের আউটপুট হোক মডেলের দেওয়া আর্গুমেন্ট দিয়ে ডাকা একটি ফাংশনের ফল, যেমন আর্গুমেন্ট দিয়ে আসা ডেটা আরও প্রক্রিয়া বা যাচাই করতে (মডেলকে আবার চেষ্টা করতে বলার সুযোগসহ), বা আরেকটি এজেন্টের হাতে তুলে দিতে।

আউটপুট ফাংশন [ফাংশন টুলের](tools.md) মতোই, তবে মডেলকে এগুলোর একটি ডাকতে বাধ্য করা হয়, ডাকটি এজেন্ট রান শেষ করে, আর ফল মডেলের কাছে ফেরত পাঠানো হয় না।

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ টুল হলো রান্নার মাঝে মশলার কৌটা খোলা: ফল দেখে রাঁধুনি (মডেল) রান্না চালিয়ে যায়। আউটপুট ফাংশন হলো পরিবেশনের থালা: মডেল এটি ডাকলেই রান্না শেষ, আর থালায় যা উঠল সেটিই চূড়ান্ত ফল।

///

টুল ফাংশনের মতোই, মডেলের দেওয়া আউটপুট ফাংশনের আর্গুমেন্ট Pydantic দিয়ে যাচাই হয় (ঐচ্ছিক [validation context](#validation-context)-সহ), চাইলে প্রথম আর্গুমেন্ট হিসেবে [`RunContext`][pydantic_ai.tools.RunContext] নিতে পারে, আর বদলানো আর্গুমেন্ট দিয়ে (বা ভিন্ন আউটপুট টাইপ দিয়ে) মডেলকে আবার চেষ্টা করতে বলতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে।

আউটপুট ফাংশন [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] সমর্থন করে না, যা [ফাংশন-টুলের ব্যর্থতার](tools-advanced.md#tool-failed) জন্য সংরক্ষিত। এখানে `ToolFailed`-কে যেকোনো সাধারণ exception-এর মতোই ধরা হয়: একটি [`on_output_process_error` hook](hooks.md#error-hooks) এটি থেকে উদ্ধার করতে পারে, নইলে এটি রান থামিয়ে দেয়।

আউটপুট ফাংশন দিতে, এজেন্টের `output_type` হিসেবে একটি একক ফাংশন (বা bound instance মেথড), বা ফাংশনের একটি তালিকা দিন। তালিকায় সাধারণ scalar বা পুরো Pydantic মডেলের মতো অন্য আউটপুট টাইপও থাকতে পারে।
সাধারণত আপনার আউটপুট ফাংশনটিকে একটি টুল হিসেবেও (`@agent.tool` decorator বা `tools` আর্গুমেন্ট দিয়ে) নথিভুক্ত করতে চাইবেন না, কারণ এতে মডেল বিভ্রান্ত হতে পারে কোনটি ডাকা উচিত।

এই সব সুবিধা একসাথে কাজ করার একটি উদাহরণ:

```python title="output_functions.py"
import re

from pydantic import BaseModel

from pydantic_ai import Agent, ModelRetry, RunContext, UnexpectedModelBehavior


class Row(BaseModel):
    name: str
    country: str


tables = {
    'capital_cities': [
        Row(name='Amsterdam', country='Netherlands'),
        Row(name='Mexico City', country='Mexico'),
    ]
}


class SQLFailure(BaseModel):
    """An unrecoverable failure. Only use this when you can't change the query to make it work."""

    explanation: str


def run_sql_query(query: str) -> list[Row]:
    """Run a SQL query on the database."""

    select_table = re.match(r'SELECT (.+) FROM (\w+)', query)
    if select_table:
        column_names = select_table.group(1)
        if column_names != '*':
            raise ModelRetry("Only 'SELECT *' is supported, you'll have to do column filtering manually.")

        table_name = select_table.group(2)
        if table_name not in tables:
            raise ModelRetry(
                f"Unknown table '{table_name}' in query '{query}'. Available tables: {', '.join(tables.keys())}."
            )

        return tables[table_name]

    raise ModelRetry(f"Unsupported query: '{query}'.")


sql_agent = Agent[object, list[Row] | SQLFailure](
    'openai:gpt-6.1-sol',
    output_type=[run_sql_query, SQLFailure],
    instructions='You are a SQL agent that can run SQL queries on a database.',
)


async def hand_off_to_sql_agent(ctx: RunContext, query: str) -> list[Row]:
    """I take natural language queries, turn them into SQL, and run them on a database."""

    # Drop the final message with the output tool call, as it shouldn't be passed on to the SQL agent
    messages = ctx.messages[:-1]
    try:
        result = await sql_agent.run(query, message_history=messages)
        output = result.output
        if isinstance(output, SQLFailure):
            raise ModelRetry(f'SQL agent failed: {output.explanation}')
        return output
    except UnexpectedModelBehavior as e:
        # Bubble up potentially retryable errors to the router agent
        if (cause := e.__cause__) and isinstance(cause, ModelRetry):
            raise ModelRetry(f'SQL agent failed: {cause.message}') from e
        else:
            raise


class RouterFailure(BaseModel):
    """Use me when no appropriate agent is found or the used agent failed."""

    explanation: str


router_agent = Agent[object, list[Row] | RouterFailure](
    'openai:gpt-6.1-sol',
    output_type=[hand_off_to_sql_agent, RouterFailure],
    instructions='You are a router to other agents. Never try to solve a problem yourself, just pass it on.',
)

result = router_agent.run_sync('Select the names and countries of all capitals')
print(result.output)
"""
[
    Row(name='Amsterdam', country='Netherlands'),
    Row(name='Mexico City', country='Mexico'),
]
"""

result = router_agent.run_sync('Select all pets')
print(repr(result.output))
"""
RouterFailure(explanation="The requested table 'pets' does not exist in the database. The only available table is 'capital_cities', which does not contain data about pets.")
"""

result = router_agent.run_sync('How do I fly from Amsterdam to Mexico City?')
print(repr(result.output))
"""
RouterFailure(explanation='I am not equipped to provide travel information, such as flights from Amsterdam to Mexico City.')
"""
```

#### লেখার আউটপুট (Text output) { #text-output }

আপনি একটি স্ট্রিং নেওয়া আউটপুট ফাংশন দিলে, Pydantic AI ডিফল্টভাবে অন্য যেকোনো আউটপুট ফাংশনের মতোই একটি আউটপুট টুল তৈরি করবে। বদলে যদি চান মডেলটি সাধারণ লেখার আউটপুট দিয়ে স্ট্রিংটি দিক, তাহলে ফাংশনটিকে [`TextOutput`][pydantic_ai.output.TextOutput] চিহ্নিতকারী ক্লাসে মুড়ে দিতে পারেন।

চাইলে, এই চিহ্নিতকারী ক্লাস `output_type`-এ দেওয়া একটি তালিকায় এক বা একাধিক [`ToolOutput`](#tool-output) চিহ্নিতকারী ক্লাসের (বা চিহ্নহীন টাইপ বা ফাংশনের) পাশাপাশি ব্যবহার করা যায়।

অন্য আউটপুট ফাংশনের মতো, লেখার আউটপুট ফাংশন চাইলে প্রথম আর্গুমেন্ট হিসেবে [`RunContext`][pydantic_ai.tools.RunContext] নিতে পারে, আর বদলানো আর্গুমেন্ট দিয়ে (বা ভিন্ন আউটপুট টাইপ দিয়ে) মডেলকে আবার চেষ্টা করতে বলতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে।

কিছু মডেল একেবারেই লেখা তৈরি করতে পারে না, আর তাদের profile-এ [`supports_text_output=False`][pydantic_ai.profiles.ModelProfile.supports_text_output] দিয়ে তা জানায় — [decision model](models/decision.md), যেমন [TypeSafe-এর Jev](models/typesafe.md), এমন। সেগুলোতে, লেখার আউটপুট খোলা রাখে এমন যেকোনো `output_type` রিকোয়েস্ট পাঠানোর আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError]: ডিফল্ট `str`, কয়েকটি আউটপুট টাইপের মধ্যে একটি `str`, একটি `TextOutput` ফাংশন, আর [`PromptedOutput`](#prompted-output), যা তার গোছানো ডেটা লেখা হিসেবে চায়। বদলে এমন মডেলকে একটি গোছানো `output_type` দিন, যেমন একটি `BaseModel` বা সেগুলোর একটি union।

/// note | মনে রাখুন

stream করার সময়, [`stream_text()`][pydantic_ai.result.StreamedRunResult.stream_text] `TextOutput` ফাংশন প্রয়োগ **করে না**। এটি যে মান তৈরি করে তা stream করতে, বদলে [`stream_output()`][pydantic_ai.result.StreamedRunResult.stream_output] ব্যবহার করুন। বিস্তারিত জানতে দেখুন [Streaming Text](#streaming-text)।

///

```python title="text_output_function.py"
from pydantic_ai import Agent, TextOutput


def split_into_words(text: str) -> list[str]:
    return text.split()


agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=TextOutput(split_into_words),
)
result = agent.run_sync('Who was Albert Einstein?')
print(result.output)
#> ['Albert', 'Einstein', 'was', 'a', 'German-born', 'theoretical', 'physicist.']
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### আউটপুট ফাংশনে আংশিক আউটপুট সামলানো { #handling-partial-output-in-output-functions }

`run_stream()` বা `run_stream_sync()` দিয়ে stream করার সময়, আউটপুট ফাংশন **একাধিকবার** ডাকা হয় — মডেল থেকে পাওয়া প্রতিটি আংশিক আউটপুটের জন্য একবার, আর চূড়ান্ত সম্পূর্ণ আউটপুটের জন্য একবার।

আপনার আউটপুট ফাংশনে যদি এমন **পার্শ্বপ্রতিক্রিয়া** থাকে (যেমন নোটিফিকেশন পাঠানো, লগ করা, ডেটাবেস হালনাগাদ) যা শুধু চূড়ান্ত আউটপুটে চলা উচিত, তাহলে [`RunContext.partial_output`][pydantic_ai.tools.RunContext.partial_output] ফ্ল্যাগ পরীক্ষা করুন।

stream করার সময়, প্রতিটি আংশিক আউটপুটের জন্য `partial_output` `True` আর চূড়ান্ত সম্পূর্ণ আউটপুটের জন্য `False`।
[অন্য সব রান মেথডে](agent.md#running-agents), `partial_output` সবসময় `False`, কারণ ফাংশনটি সম্পূর্ণ আউটপুট দিয়ে শুধু একবার ডাকা হয়।

```python title="output_function_with_side_effects.py"
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext


class DatabaseRecord(BaseModel):
    name: str
    value: int | None = None  # Make optional to allow partial output


def save_to_database(ctx: RunContext, record: DatabaseRecord) -> DatabaseRecord:
    """Output function with side effect - only save final output to database."""
    if ctx.partial_output:
        # Skip side effects for partial outputs
        return record

    # Only execute side effect for the final output
    print(f'Saving to database: {record.name} = {record.value}')
    #> Saving to database: test = 42
    return record


agent = Agent('openai:gpt-6.1-sol', output_type=save_to_database)


async def main():
    async with agent.run_stream('Create a record with name "test" and value 42') as result:
        async for output in result.stream_output(debounce_by=None):
            print(output)
            #> name='test' value=None
            #> name='test' value=42
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// warning | সাধারণ ভুল

stream মোডে `partial_output` পরীক্ষা না করলে, একটি "ইমেইল পাঠাও" আউটপুট ফাংশন একটি রানে দশবার ইমেইল পাঠিয়ে ফেলতে পারে। পার্শ্বপ্রতিক্রিয়ার আগে লিখুন `if ctx.partial_output: return ...`।

///

### আউটপুট মোড { #output-modes }

মডেলকে দিয়ে গোছানো ডেটা আউটপুট করাতে Pydantic AI তিনটি ভিন্ন পদ্ধতি বাস্তবায়ন করে:

1. [Tool Output](#tool-output), যেখানে আউটপুট তৈরিতে টুল কল ব্যবহার হয়।
2. [Native Output](#native-output), যেখানে মডেলকে একটি দেওয়া JSON schema মেনে লেখার বিষয়বস্তু তৈরি করতে হয়।
3. [Prompted Output](#prompted-output), যেখানে কাঙ্ক্ষিত JSON schema-সহ একটি prompt মডেলের নির্দেশনায় বসানো হয়, আর আমরা মডেলের সাধারণ-লেখার উত্তর যথাযথভাবে পার্স করার চেষ্টা করি।

| মোড | কীভাবে | নির্ভরযোগ্যতা | কখন |
| --- | --- | --- | --- |
| Tool Output (ডিফল্ট) | একটি বিশেষ "আউটপুট টুল"-এর আর্গুমেন্ট হিসেবে | খুব ভালো, প্রায় সব মডেলে | শুরুতে এটিই |
| Native Output | মডেলের নিজস্ব JSON schema মোড | schema-মানা নিশ্চিত, তবে সব মডেলে নেই | মডেল সমর্থন করলে |
| Prompted Output | নির্দেশনায় schema লিখে দেওয়া | সবচেয়ে কম নিশ্চিত | টুল বা native সমর্থন নেই এমন মডেলে |

#### Tool Output { #tool-output }

ডিফল্ট Tool Output মোডে, প্রতিটি আউটপুট টাইপের (বা ফাংশনের) আউটপুট JSON schema একটি বিশেষ আউটপুট টুলের প্যারামিটার schema হিসেবে মডেলকে দেওয়া হয়। এটিই ডিফল্ট, কারণ এটি প্রায় সব মডেল সমর্থন করে আর খুব ভালো কাজ করে বলে দেখা গেছে।

আউটপুট টুলের নাম বদলাতে, মডেলকে সাহায্য করতে নিজের বর্ণনা দিতে, বা [strict mode](tools-advanced.md#strict-mode) চালু বা বন্ধ করতে চাইলে, টাইপ(গুলো)কে [`ToolOutput`][pydantic_ai.output.ToolOutput] চিহ্নিতকারী ক্লাসে মুড়ে উপযুক্ত আর্গুমেন্ট দিতে পারেন। মনে রাখুন, ডিফল্টভাবে বর্ণনা নেওয়া হয় একটি Pydantic মডেল বা আউটপুট ফাংশনের docstring থেকে, তাই চিহ্নিতকারী ক্লাস দিয়ে তা দেওয়া সাধারণত দরকার হয় না।

ফিল্ডের বর্ণনা মডেলের কাছে পৌঁছায় [টুলের schema](tools.md#docstrings)-র মতোই, একটি Pydantic মডেলের ফিল্ডের docstring-সহ যখন সেটি `use_attribute_docstrings` সেট করে। [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করা একটি `Enum` বাড়তি হিসেবে তার প্রতিটি বিকল্পকে সেই সদস্যের নিচে লেখা docstring দিয়ে বর্ণনা করে, enum যেখানেই থাকুক — একটি আউটপুট মডেলে, একটি টুলের প্যারামিটারে, বা একটি খালি `Enum` `output_type` হিসেবে। mix-in ছাড়া docstring উপেক্ষিত হয়; দেখুন [enum options](tools.md#enum-options)।

আউটপুট টুল ব্যবহার করলে, প্রতিটি টুল নিজের আবার-চেষ্টার গণনা পায় — এজেন্টের আবার-চেষ্টার বাজেটের আউটপুট দিক ([`AgentRetries`][pydantic_ai.agent.AgentRetries] দিয়ে `Agent(retries={'output': N})`-এ, বা প্রতি রানে `agent.run(retries={'output': N})`-এ দেওয়া) হলো *প্রতি-টুলের ডিফল্ট সীমা*। একটি নির্দিষ্ট আউটপুট টুলের সীমা বদলাতে, `ToolOutput`-এ [`max_retries`][pydantic_ai.output.ToolOutput.max_retries] দিন: `ToolOutput(Fruit, max_retries=2)`। লেখার আউটপুটের পথের global বাজেটের সাথে সম্পর্কের জন্য দেখুন [How output retries are enforced](agent.md#how-output-retries-are-enforced)।

একটি এজেন্ট রানের সময় উপলব্ধ আউটপুট টুল গতিশীলভাবে বদলাতে বা ছাঁকতে, একটি এজেন্ট-জুড়ে `prepare_output_tools` ফাংশন সংজ্ঞায়িত করতে পারেন, যা রানের প্রতিটি ধাপের আগে ডাকা হবে। এই ফাংশন [`ToolsPrepareFunc`][pydantic_ai.tools.ToolsPrepareFunc] টাইপের হওয়া উচিত, যা [`RunContext`][pydantic_ai.tools.RunContext] আর [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এর একটি তালিকা নিয়ে সেই ধাপে দেখানোর আউটপুট টুলের সংজ্ঞা ফেরত দেয়। কোনো আউটপুট টুল না দেখাতে `[]` ফেরত দিন। এটি আউটপুট নয় এমন টুলের [`prepare_tools` ফাংশনের](tools-advanced.md#prepare-tools) সমতুল্য।

```python title="tool_output.py"
from pydantic import BaseModel

from pydantic_ai import Agent, ToolOutput


class Fruit(BaseModel):
    name: str
    color: str


class Vehicle(BaseModel):
    name: str
    wheels: int


agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=[ # (1)!
        ToolOutput(Fruit, name='return_fruit'),
        ToolOutput(Vehicle, name='return_vehicle'),
    ],
)
result = agent.run_sync('What is a banana?')
print(repr(result.output))
#> Fruit(name='banana', color='yellow')
```

1. কাস্টম টুলের নাম ছাড়া শুধু `Fruit` আর `Vehicle` দিলে, একটি union ব্যবহার করতে পারতাম: `output_type=Fruit | Vehicle`। তবে `ToolOutput` একটি টাইপ নয়, অবজেক্ট বলে আমাদের একটি তালিকা ব্যবহার করতে হয়।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### Native Output { #native-output }

Native Output মোড মডেলের নিজস্ব "Structured Outputs" সুবিধা (ওরফে "JSON Schema response format") ব্যবহার করে, যেখানে মডেলকে শুধু দেওয়া JSON schema-র সাথে মেলে এমন লেখা আউটপুট করতে বাধ্য করা হয়। মনে রাখুন, সব মডেল এটি সমর্থন করে না, আর কখনো কখনো সীমাবদ্ধতাও থাকে। যেমন, [Gemini 3](https://ai.google.dev/gemini-api/docs/structured-output#structured_outputs_with_tools) ফাংশন আর নেটিভ টুলের পাশাপাশি Native Output সমর্থন করে, কিন্তু আগের Gemini মডেলগুলো Native Output-কে ফাংশন টুলের সাথে মেলাতে পারে না।

এই মোড ব্যবহার করতে, আউটপুট টাইপ(গুলো)কে [`NativeOutput`][pydantic_ai.output.NativeOutput] চিহ্নিতকারী ক্লাসে মুড়ে দিতে পারেন, যা টাইপ বা ফাংশনের নাম আর docstring যথেষ্ট না হলে একটি `name` আর `description` দিতেও দেয়।

```python title="native_output.py"
from pydantic_ai import Agent, NativeOutput

from tool_output import Fruit, Vehicle

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=NativeOutput(
        [Fruit, Vehicle], # (1)!
        name='Fruit_or_vehicle',
        description='Return a fruit or vehicle.'
    ),
)
result = agent.run_sync('What is a Ford Explorer?')
print(repr(result.output))
#> Vehicle(name='Ford Explorer', wheels=4)
```

1. এটি একটি union-ও হতে পারত: `output_type=Fruit | Vehicle`। তবে ওপরের "Type checking নিয়ে বিবেচনা" অংশে যেমন ব্যাখ্যা করা হয়েছে, mypy বা পুরনো Pyright সংস্করণে সঠিকভাবে type check হতে এর জন্য `Agent` constructor-এ স্পষ্টভাবে generic প্যারামিটার দেওয়া আর এই লাইনে `# type: ignore` যোগ করা লাগত।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### Prompted Output { #prompted-output }

এই মোডে, মডেলকে তার [নির্দেশনা](agent.md#instructions) দিয়ে দেওয়া JSON schema-র সাথে মেলে এমন লেখা আউটপুট করতে বলা হয়, আর সেই নির্দেশনা সঠিকভাবে বোঝা মডেলের দায়িত্ব। এটি সব মডেলে ব্যবহার করা যায়, তবে প্রায়ই সবচেয়ে কম নির্ভরযোগ্য পদ্ধতি, কারণ মডেলকে schema মানতে বাধ্য করা হয় না।

সাধারণভাবে আমরা tool বা native output দিয়ে শুরু করার পরামর্শ দিলেও, কিছু ক্ষেত্রে এই মোড আরও উচ্চমানের আউটপুট দিতে পারে, আর নিজস্ব টুল-কল বা structured output সমর্থন নেই এমন মডেলের জন্য গোছানো আউটপুট তৈরির এটিই একমাত্র বিকল্প।

মডেলের API যদি মডেলকে বৈধ JSON আউটপুট করাতে "JSON Mode" সুবিধা (ওরফে "JSON Object response format") সমর্থন করে, তাহলে এটি চালু হয়, তবে schema মানা তখনো মডেলের ওপর। Pydantic AI ফেরত দেওয়া গোছানো ডেটা যাচাই করবে আর যাচাই ব্যর্থ হলে মডেলকে আবার চেষ্টা করতে বলবে, তবে মডেল যথেষ্ট বুদ্ধিমান না হলে এটি যথেষ্ট না-ও হতে পারে।

এই মোড ব্যবহার করতে, আউটপুট টাইপ(গুলো)কে [`PromptedOutput`][pydantic_ai.output.PromptedOutput] চিহ্নিতকারী ক্লাসে মুড়ে দিতে পারেন, যা টাইপ বা ফাংশনের নাম আর docstring যথেষ্ট না হলে একটি `name` আর `description` দিতেও দেয়। এছাড়া, `template` দিয়ে [ডিফল্টের][pydantic_ai.profiles.ModelProfile.prompted_output_template] বদলে ব্যবহারের জন্য একটি নিজের নির্দেশনা-ছাঁচ দিতে পারেন, বা schema-র prompt পুরোপুরি বন্ধ করতে `template=False`।

```python title="prompted_output.py"
from pydantic import BaseModel

from pydantic_ai import Agent, PromptedOutput

from tool_output import Vehicle


class Device(BaseModel):
    name: str
    kind: str


agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=PromptedOutput(
        [Vehicle, Device], # (1)!
        name='Vehicle or device',
        description='Return a vehicle or device.'
    ),
)
result = agent.run_sync('What is a MacBook?')
print(repr(result.output))
#> Device(name='MacBook', kind='laptop')

agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=PromptedOutput(
        [Vehicle, Device],
        template='Gimme some JSON: {schema}'
    ),
)
result = agent.run_sync('What is a Ford Explorer?')
print(repr(result.output))
#> Vehicle(name='Ford Explorer', wheels=4)
```

1. এটি একটি union-ও হতে পারত: `output_type=Vehicle | Device`। তবে ওপরের "Type checking নিয়ে বিবেচনা" অংশে যেমন ব্যাখ্যা করা হয়েছে, mypy বা পুরনো Pyright সংস্করণে সঠিকভাবে type check হতে এর জন্য `Agent` constructor-এ স্পষ্টভাবে generic প্যারামিটার দেওয়া আর এই লাইনে `# type: ignore` যোগ করা লাগত।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

#### চূড়ান্ত ফলের পাশাপাশি টুল কল { #parallel-output-tool-calls }

মডেল একটি চূড়ান্ত ফল তৈরি করলে একটি রান শেষ হয়। সেই ফল সাধারণত আসে একটি [আউটপুট টুল](#tool-output) কল থেকে, তবে [Native Output](#native-output), [Prompted Output](#prompted-output), সাধারণ লেখা, বা [ছবির আউটপুট](#image-output) থেকেও আসতে পারে। মডেল একই উত্তরে *অন্য* টুল কল দিলে, সেগুলোর কী হবে তা ঠিক করে এজেন্টের [`end_strategy`][pydantic_ai.agent.Agent.end_strategy]। বেশিরভাগ এজেন্টকে এ নিয়ে ভাবতেই হয় না, কারণ বেশিরভাগ উত্তর একটি চূড়ান্ত ফলকে অন্য টুল কলের সাথে মেশায় না — কিন্তু মেশালে, `end_strategy` নিয়ন্ত্রণ করে সেই কলগুলো কীভাবে চলবে আর কোনটি চূড়ান্ত ফল হবে।

/// warning | stream মেথডে আউটপুট আর deferred টুলের অগ্রাধিকার

[`run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] আর [`run_stream_sync()`][pydantic_ai.agent.AbstractAgent.run_stream_sync] মেথড [আউটপুট টাইপের](output.md#structured-output) সাথে মেলা প্রথম আউটপুটকেই (যা লেখা, একটি [আউটপুট টুল](output.md#tool-output) কল, বা একটি [deferred](deferred-tools.md) টুল কল হতে পারে) এজেন্ট রানের চূড়ান্ত আউটপুট ধরে, এমনকি এই "চূড়ান্ত" আউটপুটের পরে মডেল (আরও) টুল কল তৈরি করলেও।

অর্থাৎ এই মেথডগুলো ব্যবহারের সময় মডেল আউটপুট টুলের আগে deferred টুল ডাকলে, deferred টুল কলগুলোই এজেন্ট রানের চূড়ান্ত আউটপুট ঠিক করে, অথচ অন্য [রান মেথডগুলো](agent.md#running-agents) টুল আউটপুটকে অগ্রাধিকার দিত। `end_strategy` যা-ই হোক, এই মেথডগুলো প্রথম মেলা আউটপুট stream হওয়ার মুহূর্তেই চূড়ান্ত করে, তাই এরা `'early'`-র মতো আচরণ করে: সেই ফল আটকে যায়, আর নিচের [টুল-ব্যর্থতার-পরে-আবার-চেষ্টা](#retrying-after-a-tool-failure) আচরণ প্রযোজ্য হয় না।

///

| কৌশল | আউটপুট টুল | ফাংশন টুল — আউটপুট সফল | ফাংশন টুল — প্রতিটি আউটপুট ব্যর্থ |
|---|---|---|---|
| `'graceful'` (ডিফল্ট) | পাঠানোর ক্রমে চলে; প্রথম সফলটি চূড়ান্ত ফল, পরের আউটপুট টুল বাদ | চলে, যেখানে সম্ভব একসাথে, পাঠানোর ক্রমে | চলে; রান চলতে থাকে |
| `'early'` | পাঠানোর ক্রমে চলে; প্রথম সাফল্যেই রান শেষ | বাদ | চলে; রান চলতে থাকে |
| `'exhaustive'` | সব চলে, একসাথে; পাঠানোর ক্রমে প্রথম বৈধ ফল জেতে | চলে, একসাথে | চলে; রান চলতে থাকে |

বেশিরভাগ এজেন্টের জন্য `'graceful'`-ই ডিফল্ট আর সঠিক পছন্দ: মডেল একটি আউটপুট টুলের পাশাপাশি যে ফাংশন টুল চেয়েছে সেগুলো তবুও চলে, তাই তাদের পার্শ্বপ্রতিক্রিয়া ঘটে আর রান চলতে থাকলে তাদের ফল মডেলের কাছে পাওয়া যায়। শুধু প্রথম সফল আউটপুট টুলটি ব্যবহার হয়; পরের আউটপুট টুলগুলো বাদ পড়ে, যাতে তাদের পার্শ্বপ্রতিক্রিয়া একাধিকবার না ঘটে।

একটি আউটপুট টুল সফল হওয়ার মুহূর্তেই রান শেষ করতে `'early'` বেছে নিন — তখন একই উত্তরে চাওয়া ফাংশন টুলগুলো পুরোপুরি বাদ পড়ে। ফল পাওয়ার পরে সেই ফাংশন টুলগুলো চালানোর কখনো দরকার না হলে এটিই সবচেয়ে দ্রুত বিকল্প।

প্রতিটি টুল চালাতে `'exhaustive'` বেছে নিন, এমন বাড়তি আউটপুট টুলসহ যাদের ফল ব্যবহার হবে না। এতে মডেল পুরোপুরি দেখতে পায় যে প্রতিটি টুল চলেছে, তবে এর খরচ হলো শেষ পর্যন্ত বাদ পড়া আউটপুট-টুলের পার্শ্বপ্রতিক্রিয়াও ঘটে।

*প্রতিটি* আউটপুট টুল ব্যর্থ হলে, তিনটি কৌশলেই ফাংশন টুলগুলো চলে আর রান চলতে থাকে: শেষ করার মতো কোনো ফল নেই, তাই আউটপুটের ব্যর্থতাগুলো আবার-চেষ্টা হিসেবে মডেলের কাছে ফেরত যায় আর মডেলের চাওয়া ফাংশন টুলগুলোও চলে, ফলে পরের দফায় সে দুটোতেই সাড়া দিতে পারে।

/// note | টুল কলের পাশাপাশি Native, prompted আর ছবির আউটপুট

আপনার `output_type` [Native Output](#native-output), [Prompted Output](#prompted-output) বা [ছবির আউটপুট](#image-output) ব্যবহার করলে, চূড়ান্ত ফল আসে একটি আউটপুট টুল কলের বদলে মডেলের ফেরত দেওয়া লেখা বা ছবি থেকে। যেহেতু মডেলকে সরাসরি সেই আউটপুট তৈরি করতে বলা হয়, এটি সাধারণত একাই তা ফেরত দেয় — কিন্তু কিছু মডেল মাঝে মাঝে একই উত্তরে এটি *আর* একটি [ফাংশন টুল](tools.md#function-tools) কল দুটোই ফেরত দেয়। `'early'`-তে, একটি *বৈধ* আউটপুট রান শেষ করে আর সাথে পাঠানো ফাংশন টুলগুলো বাদ পড়ে, ঠিক একটি সফল আউটপুট টুলের মতো; যাচাই ব্যর্থ আউটপুট বদলে স্বাভাবিক টুল চালানোয় চলে যায়। `'graceful'` আর `'exhaustive'`-তে, ফাংশন টুলগুলো চলে আর ([streaming](#parallel-output-tool-calls)-এর বাইরে) রান চলতে থাকে, তাই তাদের ফল মডেলের শেষ আউটপুটকে প্রভাবিত করতে পারে।

এটি শুধু *ফাংশন* টুলে প্রযোজ্য। উত্তরে একটি [আউটপুট টুল](#tool-output) কল বা একটি [deferred টুল](deferred-tools.md) কলও থাকলে, সেই কল অগ্রাধিকার পায়: আউটপুট টুল তবুও চূড়ান্ত ফল তৈরি করে, আর একটি deferred কল তবুও `DeferredToolRequests` হিসেবে দেখা দেয়।

**সাধারণ লেখার আউটপুট ভিন্নভাবে ধরা হয়।** `output_type=str` বা [`TextOutput`](#text-output)-এ — একটি বড় আউটপুট টাইপের ভেতরে `str` বিকল্পসহ — মডেলকে বলা *হয় না* যে তার লেখা চূড়ান্ত ফল হিসেবে ধরা হবে, তাই একটি টুল কলের পাশাপাশি সে যে লেখা দেয় তা সাধারণত কাজের আগের বর্ণনা ("দেখে নিচ্ছি…"), একটি সম্পূর্ণ উত্তর নয়। এতে রান শেষ করলে টুলটি চুপচাপ বাদ পড়ত, তাই সাধারণ লেখা কখনো সাথে পাঠানো ফাংশন টুলকে টপকায় না: টুলটি `'early'`-তে ঠিক `'graceful'`-এর মতোই চলে। (ওপরে যেমন বলা হয়েছে, [stream মেথডগুলো](#parallel-output-tool-calls) তবুও stream হতে হতেই প্রথম লেখা চূড়ান্ত করে।)

///

##### টুল ব্যর্থ হওয়ার পরে আবার চেষ্টা { #retrying-after-a-tool-failure }

`'graceful'` আর `'exhaustive'` [শেষের কৌশলে](#parallel-output-tool-calls), একটি আউটপুট টুলের পাশাপাশি চাওয়া ফাংশন টুলগুলো তবুও চলে। এগুলোর একটি যদি একটি সফল আউটপুট টুলের একই উত্তরে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তোলে (বা এর আর্গুমেন্টের যাচাই ব্যর্থ হয়), তাহলে আউটপুটের ফল চূড়ান্ত ফল হিসেবে ব্যবহার **হয় না**। বদলে, আবার-চেষ্টাটি মডেলের কাছে ফেরত পাঠানো হয় যাতে সে সমস্যা ঠিক করতে পারে, কারণ আউটপুটটি হয়তো ব্যর্থ টুল কলের ওপর ভিত্তি করে তৈরি হয়েছিল। এটি প্রযোজ্য নয় `'early'`-তে, যেখানে একটি আউটপুট সফল হলে ফাংশন টুল চলে না, আর [streaming](#parallel-output-tool-calls)-এও নয়, যেখানে প্রথম মেলা আউটপুট সাথে সাথে চূড়ান্ত হয়।

##### আউটপুট টুলের একসাথে চলা নিয়ন্ত্রণ { #controlling-output-tool-parallelism }

ফাংশন টুলের মতো, [আউটপুট টুলও](#tool-output) একসাথে চলে। `'exhaustive'` [শেষের কৌশলে](#parallel-output-tool-calls), যেখানে একাধিক আউটপুট টুল একসাথে চলতে পারে, [`ToolOutput(sequential=True)`][pydantic_ai.output.ToolOutput] দিয়ে একটি আউটপুট টুলকে একটি বাধা (barrier) বানাতে পারেন — কাজে লাগে যখন চান আউটপুট টুল চলার আগে একটি উত্তরের সব ফাংশন টুল শেষ হোক। এটি ফাংশন টুলের `sequential=True` ফ্ল্যাগের আউটপুট-টুল সংস্করণ; বাধাটি কীভাবে আচরণ করে আর একটি পুরো রানের টুল কীভাবে ক্রমানুসারে চালাবেন, তা দেখুন [Parallel tool calls & concurrency](tools-advanced.md#parallel-tool-calls-concurrency)-তে।

### নিজের JSON schema { #structured-dict }

আপনার কাঙ্ক্ষিত গোছানো আউটপুট অবজেক্ট একটি Pydantic `BaseModel`, dataclass বা `TypedDict` দিয়ে সংজ্ঞায়িত করা সম্ভব না হলে, যেমন একটি বাইরের উৎস থেকে JSON schema পেলে বা গতিশীলভাবে তৈরি করলে, [`StructuredDict()`][pydantic_ai.output.StructuredDict] সহায়ক ফাংশন দিয়ে একটি JSON schema যুক্ত `dict[str, Any]` subclass তৈরি করতে পারেন, যা Pydantic AI মডেলকে পাঠাবে।

মনে রাখুন, Pydantic AI পাওয়া JSON অবজেক্টের কোনো যাচাই করবে না, আর schema আর তাতে প্রকাশিত শর্তগুলো, যেমন বাধ্যতামূলক ফিল্ড বা পূর্ণসংখ্যার পরিসর, সঠিকভাবে বোঝা মডেলের দায়িত্ব।

আউটপুট টাইপ হবে একটি `dict[str, Any]`, আর মডেল ভুল করলে তা সাবধানে পড়া আপনার কোডের দায়িত্ব। যাচাইয়ের এরর মডেলের কাছে ফেরত পাঠিয়ে তাকে আবার চেষ্টা করাতে একটি [আউটপুট validator](#output-validator-functions) ব্যবহার করতে পারেন।

JSON schema-র সাথে, মডেলকে বাড়তি প্রেক্ষাপট দিতে চাইলে `name` আর `description` আর্গুমেন্টও দিতে পারেন:

```python
from pydantic_ai import Agent, StructuredDict

HumanDict = StructuredDict(
    {
        'type': 'object',
        'properties': {
            'name': {'type': 'string'},
            'age': {'type': 'integer'}
        },
        'required': ['name', 'age']
    },
    name='Human',
    description='A human with a name and age',
)

agent = Agent('openai:gpt-6.1-sol', output_type=HumanDict)
result = agent.run_sync('Create a person')
#> {'name': 'John Doe', 'age': 30}
```

### শুধু চলার সময় জানা বিকল্প (Choices) { #choices }

কখনো কখনো মডেলকে এমন একটি সেট থেকে একটি বেছে নিতে হয়, যা রান চলার আগে থাকেই না: একটি এজেন্টের সামনের স্ক্রিনে উপলব্ধ কাজগুলো, একটি সার্চের ফেরত দেওয়া রেকর্ড। একটি `Literal` বা একটি `Enum` (সদস্যদের বর্ণনা দিতে [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings]-সহ) কোড লেখার সময় জানা একটি সেট সামলায়, আর এমন সম্পূর্ণতা-পরীক্ষা দেয় যা চলার সময়ের একটি সেট দিতে পারে না। বাকি সবকিছুর জন্য আছে [`Choices()`][pydantic_ai.output.Choices], যা প্রতিটি বিকল্প থেকে তার অর্থের একটি mapping নেয়:

```python title="choices.py"
from pydantic_ai import Agent, Choices

Intent = Choices(
    {
        'refund': 'The customer wants their money back.',
        'replace': 'The customer wants a working unit instead.',
        'escalate': 'Nobody on this tier can resolve it.',
    },
    name='customer_intent',
    description='What the customer is asking for.',
)

agent = Agent('openai:gpt-6.1-sol', output_type=Intent)
result = agent.run_sync('The blender arrived smashed. Just send me another one.')
print(result.output)
#> replace
```

বর্ণনাগুলোই একে একটি সহায়ক হিসেবে মূল্যবান করে: প্রতিটি বিকল্প তার অর্থ মডেলের পাওয়া schema-য় নিয়ে যায়, আর আউটপুট হয় key-গুলোর একটি, যাচাই হওয়া আর `str` টাইপের। একটি mapping-এর বদলে key-গুলোর একটি ক্রম দিলে কিছুই বর্ণনা হয় না, আর একটি সাধারণ `enum` দিয়ে একই প্রশ্ন করা হয়।

[`StructuredDict()`](#structured-dict)-এর মতো, `Choices()` একটি টাইপ ফেরত দেয়, তাই একই মান একটি `output_type`, একটি Pydantic মডেলের ফিল্ড, আর একটি [টুলের](tools.md) প্যারামিটার হিসেবে কাজ করে। তবে একটি type checker annotation-এ চলার সময় তৈরি টাইপ গ্রহণ করবে না, তাই ফিল্ড বা প্যারামিটার হিসেবে, যেকোনোটিকে তার ফেরত দেওয়া মানের টাইপে `Annotated`-এ রাখুন: [অন্য কিছুর প্রতিনিধি নয়](#choices-that-stand-for-something-else) এমন বিকল্পের জন্য `Annotated[str, Intent]`, আর একটি `StructuredDict()`-এর জন্য `Annotated[dict[str, Any], Person]`। Pydantic metadata থেকে schema আর যাচাই পড়ে, আর type checker একটি সাধারণ `str` বা `dict` দেখে:

```python title="choices_annotated.py"
from typing import Annotated

from pydantic import BaseModel

from pydantic_ai import Agent, Choices

Intent = Choices(
    {
        'refund': 'The customer wants their money back.',
        'replace': 'The customer wants a working unit instead.',
        'escalate': 'Nobody on this tier can resolve it.',
    }
)


class Triage(BaseModel):
    intent: Annotated[str, Intent]
    summary: str


agent = Agent('openai:gpt-6.1-sol', output_type=Triage)


@agent.tool_plain
def open_ticket(intent: Annotated[str, Intent], summary: str) -> str:
    """Open a ticket with the team that handles this intent."""
    return f'Opened a {intent} ticket.'


result = agent.run_sync('The kettle leaks everywhere. I just want my money back.')
print(result.output)
#> intent='refund' summary='Leaking kettle, customer wants a refund.'
```

#### অন্য কিছুর প্রতিনিধি এমন বিকল্প { #choices-that-stand-for-something-else }

একটি বিকল্প তার নিজের key-এর বদলে একটি মানের প্রতিনিধি হতে পারে, [`Choice`][pydantic_ai.output.Choice]-কে বর্ণনার পাশাপাশি মানটি দিয়ে। মডেল তবুও একটি key বাছে, আর আউটপুট হয় সেই key যার প্রতিনিধি:

```python title="choices_value.py"
from dataclasses import dataclass

from pydantic_ai import Agent, Choice, Choices


@dataclass
class Doc:
    id: str
    title: str


docs = [
    Doc(id='rfc-6265', title='HTTP State Management Mechanism'),
    Doc(id='rfc-9110', title='HTTP Semantics'),
]

agent = Agent('openai:gpt-6.1-sol')
result = agent.run_sync(
    'Which one covers cookies?',
    output_type=Choices({doc.id: Choice(doc.title, value=doc) for doc in docs}),
)
print(result.output)
#> Doc(id='rfc-6265', title='HTTP State Management Mechanism')
```

#### কিছু করে এমন বিকল্প { #choices-that-do-something }

মানটি একটি callable হলে, সেটি বাছাই করলে সেটি *ডাকা* হয়, যেভাবে একটি [আউটপুট ফাংশন](#output-functions) ডাকা হয়, তাই রানের আউটপুট হয় কাজটির ফেরত দেওয়া মান, আর মডেলের উত্তর আর তার উদ্দিষ্ট জিনিসের মাঝে কোনো dispatch টেবিল লাগে না:

```python title="choices_action.py"
from functools import partial

from pydantic_ai import Agent, Choice, Choices


class Screen:
    def click(self, target: str) -> str:
        return f'clicked {target}'

    async def observe(self) -> str:
        return 'the login page'


screen = Screen()
targets = {'login': 'The Login button, top right.', 'forgot': 'The "forgot password" link.'}

actions = {
    target: Choice(description, value=partial(screen.click, target))
    for target, description in targets.items()
}
actions['reobserve'] = Choice('Look again before deciding.', value=screen.observe)

agent = Agent('openai:gpt-6.1-sol')
result = agent.run_sync(
    'Sign in as the admin.',
    output_type=Choices(actions, description='Which action to take on the screen.'),
)
print(result.output)
#> clicked login
```

কাজটি কোনো আর্গুমেন্ট নেয় না, তাই এর যা দরকার তা `functools.partial` বা একটি closure দিয়ে বেঁধে দিন, আর এটি `async` হতে পারে। একটি আউটপুট ফাংশনের মতো, মডেলকে আবার বাছাইয়ের জন্য ফেরত পাঠাতে এটি [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে।

/// note | মনে রাখুন

একটি callable মান শুধু `output_type` হিসেবেই অর্থবহ, কারণ শুধু সেখানেই Pydantic AI এটি ডাকতে পারে। এমন একটি সেট একটি মডেলের ফিল্ড বা একটি টুলের প্যারামিটার হিসেবে ব্যবহার করলে ফাংশনটি নিজে ফেরত না দিয়ে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

[stream করার](#streamed-results) সময়, কাজটি চূড়ান্ত আউটপুটের জন্য একবারই চলে; তার আগের আংশিক আউটপুটগুলো হলো মডেলের বাছা key।

///

/// note | মনে রাখুন

`from __future__ import annotations` থাকা একটি মডিউলে, একটি `Choices` টাইপ একটি annotation-এ শুধু তখনই ব্যবহার করা যায় যখন annotation যেখানে মূল্যায়ন হয় সেখান থেকে নাম ধরে সেটি পাওয়া যায়, তাই মডিউল-স্তরের একটি assignment কাজ করে কিন্তু একটি ফাংশনের ভেতরে তৈরি করলে করে না। এটি [`StructuredDict()`](#structured-dict)-এও প্রযোজ্য, তবে `output_type=` আর্গুমেন্টে নয়, যা একটি annotation নয়, একটি মান নেয়।

///

### Validation context { #validation-context }

কিছু যাচাই একটি বাড়তি Pydantic [context](https://docs.pydantic.dev/latest/concepts/validators/#validation-context) অবজেক্টের ওপর নির্ভর করে। এমন একটি অবজেক্ট সংজ্ঞার সময় একটি `Agent`-কে তার [`validation_context`][pydantic_ai.agent.Agent.__init__] প্যারামিটার দিয়ে দিতে পারেন। এটি গোছানো আউটপুট আর [টুলের আর্গুমেন্ট](tools-advanced.md#tool-retries), দুটোর যাচাইয়েই ব্যবহার হবে।

এই validation context হতে পারে:

- context অবজেক্টটি নিজেই (`Any`), যা আউটপুট যাচাইয়ে যেমন আছে তেমন ব্যবহার হয়, অথবা
- একটি ফাংশন, যা [`RunContext`][pydantic_ai.tools.RunContext] নিয়ে একটি context অবজেক্ট (`Any`) ফেরত দেয়। প্রতিটি যাচাইয়ের আগে এই ফাংশন নিজে থেকে ডাকা হবে, ফলে আপনি একটি গতিশীল validation context তৈরি করতে পারেন।

/// warning | এই _validation_ context-কে _LLM_ context-এর সাথে গুলিয়ে ফেলবেন না

এই Pydantic validation context অবজেক্ট Pydantic AI শুধু ভেতরে ভেতরে টুলের আর্গুমেন্ট আর আউটপুট যাচাইয়ে ব্যবহার করে। বিশেষ করে, এটি ভাষা মডেলকে পাঠানো prompt বা বার্তায় যোগ **হয় না**।

///

```python title="validation_context.py"
from dataclasses import dataclass

from pydantic import BaseModel, ValidationInfo, field_validator

from pydantic_ai import Agent


class Value(BaseModel):
    x: int

    @field_validator('x')
    def increment_value(cls, value: int, info: ValidationInfo):
        return value + (info.context or 0)


agent = Agent(
    'google:gemini-3.8-flash',
    output_type=Value,
    validation_context=10,
)
result = agent.run_sync('Give me a value of 5.')
print(repr(result.output))  # 5 from the model + 10 from the validation context
#> Value(x=15)


@dataclass
class Deps:
    increment: int


agent = Agent(
    'google:gemini-3.8-flash',
    output_type=Value,
    deps_type=Deps,
    validation_context=lambda ctx: ctx.deps.increment,
)
result = agent.run_sync('Give me a value of 5.', deps=Deps(increment=10))
print(repr(result.output))  # 5 from the model + 10 from the validation context
#> Value(x=15)
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি validator যাচাই করে "দাম যেন এই দোকানের সর্বোচ্চ দামের বেশি না হয়"। সর্বোচ্চ দাম প্রতিটি দোকানে আলাদা, আর তা মডেলের জানার দরকার নেই। validation context হলো validator-এর পকেটে রাখা সেই তথ্যের চিরকুট: মডেল দেখে না, কিন্তু যাচাইয়ের সময় validator পড়ে নেয়।

///

### আউটপুট validator { #output-validator-functions }

কিছু যাচাই Pydantic validator-এ করা অসুবিধাজনক বা অসম্ভব, বিশেষ করে যখন যাচাইয়ে IO লাগে আর তা asynchronous। Pydantic AI [`agent.output_validator`][pydantic_ai.agent.Agent.output_validator] decorator দিয়ে যাচাই ফাংশন যোগ করার একটি উপায় দেয়।

এখানে তোলা প্রতিটি [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] রানের আউটপুট আবার-চেষ্টার বাজেট থেকে এক একক খরচ করে। বাজেটের ডিফল্ট `1`, আর এটি এজেন্টে [`AgentRetries`][pydantic_ai.agent.AgentRetries] দিয়ে `Agent(retries={'output': N})`-এ, একটি একক রানে `agent.run(retries={'output': N})`-এ, বা প্রতিটি আউটপুট টুলে [`ToolOutput(max_retries=N)`](#tool-output) দিয়ে ঠিক করা যায়। validator-এর ভেতরে, [`ctx.max_retries`][pydantic_ai.tools.RunContext.max_retries] সেই সীমা দেখায় যা আসলে আপনাকে থামাবে (লেখার পথে global বাজেট, বা টুলের পথে প্রতি-টুলের সীমা), আর [`ctx.retry`][pydantic_ai.tools.RunContext.retry] হলো global আবার-চেষ্টার গণনা, তাই একটি রানের মধ্যে আউটপুট টুল বদলালেও এটি সামঞ্জস্যপূর্ণ থাকে। পুরো প্রয়োগের নিয়মের জন্য দেখুন [How output retries are enforced](agent.md#how-output-retries-are-enforced)।

আউটপুট validator [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] সমর্থন করে না। মডেলের কাছে আরেকটি আউটপুট চাইতে `ModelRetry` তুলুন। এখানে `ToolFailed`-কে যেকোনো সাধারণ exception-এর মতো ধরা হয়: একটি [`on_output_process_error` hook](hooks.md#error-hooks) এটি থেকে উদ্ধার করতে পারে, নইলে এটি রান থামিয়ে দেয়।

ভিন্ন ভিন্ন আউটপুট টাইপের জন্য আলাদা যাচাইয়ের নিয়ম চাইলে, বদলে [আউটপুট ফাংশন](#output-functions) ব্যবহারের পরামর্শ দেওয়া হয়, যাতে আউটপুট validator-এর ভেতরে `isinstance` পরীক্ষা করতে না হয়।
আপনি যদি চান মডেল সাধারণ লেখা দিক, আপনি নিজে প্রক্রিয়া বা যাচাই করবেন, আর তারপর এজেন্টের চূড়ান্ত আউটপুট হবে আপনার ফাংশনের ফল, তাহলে [`TextOutput` চিহ্নিতকারী ক্লাসসহ](#text-output) একটি [আউটপুট ফাংশন](#output-functions) ব্যবহারের পরামর্শ দেওয়া হয়।

এখানে [SQL Generation উদাহরণের](examples/sql-gen.md) একটি সরল রূপ:

```python title="sql_gen.py"
from fake_database import DatabaseConn, QueryError
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ModelRetry


class Success(BaseModel):
    sql_query: str


class InvalidRequest(BaseModel):
    error_message: str


Output = Success | InvalidRequest
agent = Agent[DatabaseConn, Output](
    'google:gemini-3.8-flash',
    output_type=Output,
    deps_type=DatabaseConn,
    instructions='Generate PostgreSQL flavored SQL queries based on user input.',
)


@agent.output_validator
async def validate_sql(ctx: RunContext[DatabaseConn], output: Output) -> Output:
    if isinstance(output, InvalidRequest):
        return output
    try:
        await ctx.deps.execute(f'EXPLAIN {output.sql_query}')
    except QueryError as e:
        raise ModelRetry(f'Invalid query: {e}') from e
    else:
        return output


result = agent.run_sync(
    'get me users who were last active yesterday.', deps=DatabaseConn()
)
print(result.output)
#> sql_query='SELECT * FROM users WHERE last_active::date = today() - interval 1 day'
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// info | কোডটি সহজ ভাষায়

মডেল একটি SQL লিখল। validator সেটি সত্যিকারের ডেটাবেসে `EXPLAIN` দিয়ে চালিয়ে দেখে বৈধ কিনা; ভুল হলে `ModelRetry` তুলে ডেটাবেসের এরর বার্তাসহ মডেলকে ফেরত পাঠায়, যাতে সে ঠিক করে আবার লেখে। এই কাজ (ডেটাবেসে async কল) সাধারণ Pydantic validator-এ করা কঠিন, তাই আউটপুট validator।

///

#### আউটপুট validator-এ আংশিক আউটপুট সামলানো { #handling-partial-output-in-output-validators }

`run_stream()` বা `run_stream_sync()` দিয়ে stream করার সময়, আউটপুট validator **একাধিকবার** ডাকা হয় — মডেল থেকে পাওয়া প্রতিটি আংশিক আউটপুটের জন্য একবার, আর চূড়ান্ত সম্পূর্ণ আউটপুটের জন্য একবার।

মাঝের আংশিক মান নয়, **শুধু সম্পূর্ণ ফল যাচাই** করতে চাইলে [`RunContext.partial_output`][pydantic_ai.tools.RunContext.partial_output] ফ্ল্যাগ পরীক্ষা করা উচিত।

stream করার সময়, প্রতিটি আংশিক আউটপুটের জন্য `partial_output` `True` আর চূড়ান্ত সম্পূর্ণ আউটপুটের জন্য `False`।
[অন্য সব রান মেথডে](agent.md#running-agents), `partial_output` সবসময় `False`, কারণ validator সম্পূর্ণ আউটপুট দিয়ে শুধু একবার ডাকা হয়।

```python title="partial_validation_streaming.py"
from pydantic_ai import Agent, ModelRetry, RunContext

agent = Agent('openai:gpt-6.1-sol')


@agent.output_validator
def validate_output(ctx: RunContext, output: str) -> str:
    if ctx.partial_output:
        return output

    if len(output) < 50:
        raise ModelRetry('Output is too short.')
    return output


async def main():
    async with agent.run_stream('Write a long story about a cat') as result:
        async for message in result.stream_text():
            print(message)
            #> Once upon a
            #> Once upon a time, there was
            #> Once upon a time, there was a curious cat
            #> Once upon a time, there was a curious cat named Whiskers who
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore the world around
            #> Once upon a time, there was a curious cat named Whiskers who loved to explore the world around him...
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

## ছবির আউটপুট { #image-output }

কিছু মডেল তাদের উত্তরের অংশ হিসেবে ছবি তৈরি করতে পারে, যেমন যেগুলো [Image Generation নেটিভ টুল](native-tools.md#image-generation-tool) সমর্থন করে, আর চার্ট তৈরি করতে বললে [Code Execution নেটিভ টুল](native-tools.md#code-execution-tool) ব্যবহারকারী OpenAI মডেল।

তৈরি ছবিটি এজেন্ট রানের আউটপুট হিসেবে ব্যবহার করতে, `output_type`-কে [`BinaryImage`][pydantic_ai.messages.BinaryImage] সেট করতে পারেন। কোনো ছবি-তৈরির নেটিভ টুল স্পষ্টভাবে দেওয়া না থাকলে, [`ImageGenerationTool`][pydantic_ai.native_tools.ImageGenerationTool] নিজে থেকে চালু হবে।

```python title="image_output.py"
from pydantic_ai import Agent, BinaryImage

agent = Agent('openai-responses:gpt-6.1-sol', output_type=BinaryImage)

result = agent.run_sync('Generate an image of an axolotl.')
assert isinstance(result.output, BinaryImage)
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

একটি এজেন্টকে সবসময় ছবি তৈরি করতে না হলে, `BinaryImage` আর `str`-এর একটি union ব্যবহার করতে পারেন। মডেল দুটোই তৈরি করলে, আউটপুট হিসেবে ছবিটি অগ্রাধিকার পাবে আর লেখাটি [`ModelResponse.text`][pydantic_ai.messages.ModelResponse.text]-এ পাওয়া যাবে:

```python title="image_output_union.py"
from pydantic_ai import Agent, BinaryImage

agent = Agent('openai-responses:gpt-6.1-sol', output_type=BinaryImage | str)

result = agent.run_sync('Tell me a two-sentence story about an axolotl, no image please.')
print(result.output)
"""
Once upon a time, in a hidden underwater cave, lived a curious axolotl named Pip who loved to explore. One day, while venturing further than usual, Pip discovered a shimmering, ancient coin that granted wishes!
"""

result = agent.run_sync('Tell me a two-sentence story about an axolotl with an illustration.')
assert isinstance(result.output, BinaryImage)
print(result.response.text)
"""
Once upon a time, in a hidden underwater cave, lived a curious axolotl named Pip who loved to explore. One day, while venturing further than usual, Pip discovered a shimmering, ancient coin that granted wishes!
"""
```

## ঐচ্ছিক আউটপুট (`None` অনুমোদন) { #optional-output }

কিছু এজেন্ট তাদের সব কাজ টুল কল দিয়েই করে আর একটি চূড়ান্ত আউটপুট তৈরির দরকার হয় না — যেমন, একটি এজেন্ট যে একটি টুল দিয়ে একটি রেকর্ড হালনাগাদ করে থেমে যায়। কিন্তু `output_type`-এ `str` থাকলে — ডিফল্টসহ — মডেলকে তার শেষ দফা লেখা দিয়ে শেষ করতে হয়। সে যদি মনে করে তার কাজ শেষ আর বলার কিছু বাকি নেই, তাহলে সে একটি খালি উত্তর ফেরত দেবে, বা শুধু [thinking](capabilities/thinking.md) বিষয়বস্তু থাকা একটি উত্তর (যেমন [Anthropic](models/anthropic.md) মডেলগুলো উল্লেখযোগ্যভাবে করে), আর Pydantic AI তবুও তাকে লেখা দিতে বলবে।

আপনার এজেন্টের জন্য একটি চূড়ান্ত বার্তা ছাড়া শেষ করা যখন একটি বৈধ ফল, আর মডেলকে শুধু বলার খাতিরে কিছু বলানোর চেয়ে `None` পাওয়াই ভালো, তখন `output_type`-এ `None` রাখুন:

```python title="optional_output.py"
from pydantic_ai import Agent

agent = Agent('anthropic:claude-opus-5-5', output_type=str | None)


@agent.tool_plain
def mark_task_done(task_id: int) -> str:
    """Mark the task as done."""
    return f'Task {task_id} marked done.'


result = agent.run_sync('Mark task 1 as done, then stop without saying anything.')
print(result.output)
#> None
```

মডেল একটি খালি উত্তর ফেরত দিলে আর `None` একটি অনুমোদিত আউটপুট টাইপ হলে, এজেন্ট আবার চেষ্টা না করে `None` ফেরত দেবে। [আউটপুট validator ফাংশন](#output-validator-functions) তবুও `None` আর্গুমেন্ট নিয়ে চলে, তাই দরকার হলে তা বাতিল করতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারেন।

`output_type=str | None` হলো আদর্শ ক্ষেত্র: এটি সাধারণ লেখার আউটপুট হিসেবে ধরা হয়, আর মডেলের `None` বোঝানোর **একমাত্র** উপায় হলো লেখার আউটপুট ছাড়া একটি উত্তর ফেরত দেওয়া — একটি খালি উত্তর, এমন একটি যার লেখার অংশগুলো সব খালি স্ট্রিং (যেমন কিছু OpenAI-সামঞ্জস্যপূর্ণ gateway তৈরি করে), বা শুধু [thinking](capabilities/thinking.md) বিষয়বস্তু থাকা একটি, যা কিছু reasoning মডেল একটি টুল কল দিয়ে কাজ শেষ করার পরে দেয়। এতে কোনো আউটপুট টুল বা গোছানো schema জড়িত নেই। এটি সেই একই ধারা, যেভাবে সাধারণ `str`-কে একটি গোছানো টুল কলের বদলে মুক্ত লেখার আউটপুট হিসেবে আলাদাভাবে ধরা হয়।

অন্য আউটপুট মোডেও `None` সমর্থিত, খালি-উত্তরের বিকল্প পথের পাশাপাশি (বা তার বদলে) একটি বাড়তি গোছানো পথসহ:

- **টুল মোড ব্যবহার করা `None`-সহ সাধারণ union** — যেমন `output_type=int | None`, `output_type=[int, float, None]`, বা `output_type=[ToolOutput(Foo), None]`: অন্য আউটপুট টুলের পাশাপাশি একটি বিশেষ `final_result_None` আউটপুট টুল দেখানো হয়, যাতে মডেল একটি টুল কল দিয়ে `None` নিশ্চিত করতে পারে। একটি খালি, ফাঁকা-লেখার, বা শুধু-thinking মডেল উত্তরকেও তবুও `None` ধরা হয়, ঠিক `str | None`-এর মতো।
- **স্পষ্ট আউটপুট মোড চিহ্নিতকারী** — যেমন `output_type=ToolOutput(int | None)`, `output_type=NativeOutput([int, None])`, বা `output_type=PromptedOutput([int, None])`: wrapper যে গোছানো schema তৈরি করে তার একটি শাখা হিসেবে `None` রাখা হয়। মডেল নিশ্চিত করে টুলটিকে `null` দিয়ে ডেকে (`ToolOutput`-এর জন্য) বা discriminated schema-র `None` শাখা বেছে নিয়ে (`NativeOutput`/`PromptedOutput`-এর জন্য)। একটি খালি উত্তর গ্রহণ **করা হয় না** — একবার একটি স্পষ্ট গোছানো আউটপুট মোড বেছে নিলে, মডেলের কাছে আশা করা হয় schema দিয়েই নিশ্চিত করবে।

/// note | মনে রাখুন

শুধু `output_type=None` বৈধ নয় — `None`-এর পাশাপাশি অন্তত আরেকটি আউটপুট টাইপ দিতে হবে।

///

/// note | মনে রাখুন

একটি ঐচ্ছিক আউটপুট টাইপসহ [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] ব্যবহার করলে, একটি খালি মডেল উত্তরে দেওয়ার মতো কোনো মাঝের মান থাকে না, তাই এই ক্ষেত্রে [`stream_output()`][pydantic_ai.result.StreamedRunResult.stream_output] একটি খালি iterator তৈরি করে। বদলে চূড়ান্ত `None` মান পেতে [`get_output()`][pydantic_ai.result.StreamedRunResult.get_output] ব্যবহার করুন।

///

## Stream করা ফল { #streamed-results }

stream করা ফলে দুটি প্রধান চ্যালেঞ্জ আছে:

1. সম্পূর্ণ হওয়ার আগেই গোছানো উত্তর যাচাই করা, এটি সম্ভব হয় "partial validation" দিয়ে, যা সম্প্রতি [pydantic/pydantic#10748](https://github.com/pydantic/pydantic/pull/10748)-এ Pydantic-এ যোগ হয়েছে।
2. একটি উত্তর পাওয়ার সময়, stream শুরু করে বিষয়বস্তুতে উঁকি না দিয়ে আমরা জানি না এটি চূড়ান্ত উত্তর কিনা। Pydantic AI উত্তরের ঠিক ততটুকু stream করে যতটুকুতে বোঝা যায় এটি একটি টুল কল নাকি একটি আউটপুট, তারপর পুরোটা stream করে টুল ডাকে, বা stream-টি একটি [`StreamedRunResult`][pydantic_ai.result.StreamedRunResult] হিসেবে ফেরত দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

Stream হলো রেস্তোরাঁয় একসাথে পুরো থালা না এনে একটি একটি পদ আসা: আপনি প্রথম পদ খেতে শুরু করে দেন, বাকিটার জন্য বসে থাকতে হয় না। চ্যাট অ্যাপে উত্তর শব্দে শব্দে ফুটে ওঠা এটিই। আর গোছানো ডেটায় "partial validation" মানে আধা-রান্না পদও দেখে বলা যায় "এ পর্যন্ত ঠিক আছে"।

///

/// note | মনে রাখুন

যেহেতু `run_stream()` মেথড `output_type`-এর সাথে মেলা প্রথম আউটপুটকেই চূড়ান্ত আউটপুট ধরবে,
এটি এজেন্ট graph চালানো থামিয়ে দেবে আর এই "চূড়ান্ত" আউটপুটের পরে মডেলের করা কোনো টুল কল চালাবে না।

আপনি যদি সবসময় এজেন্ট graph সম্পূর্ণ চালাতে চান আর মডেলের stream করা উত্তর আর এজেন্টের টুল চালানো থেকে সব event stream করতে চান,
তাহলে বদলে [`agent.run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] ([ডক](agent.md#streaming-all-events)) বা [`agent.iter()`][pydantic_ai.agent.AbstractAgent.iter] ([ডক](agent.md#streaming-all-events-and-output)) ব্যবহার করুন।

///

### লেখা stream করা { #streaming-text }

stream করা লেখার আউটপুটের উদাহরণ:

```python title="streamed_hello_world.py"
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash')  # (1)!


async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:  # (2)!
        async for message in result.stream_text():  # (3)!
            print(message)
            #> The first known
            #> The first known use of "hello,
            #> The first known use of "hello, world" was in
            #> The first known use of "hello, world" was in a 1974 textbook
            #> The first known use of "hello, world" was in a 1974 textbook about the C
            #> The first known use of "hello, world" was in a 1974 textbook about the C programming language.
```

1. Stream সাধারণ [`Agent`][pydantic_ai.Agent] ক্লাসেই কাজ করে, আর কোনো বিশেষ সেটআপ লাগে না, শুধু stream সমর্থন করে এমন একটি মডেল (বর্তমানে সব মডেলই stream সমর্থন করে)।
2. একটি stream করা রান শুরু করতে [`Agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] মেথড ব্যবহার হয়, এই মেথড একটি context manager ফেরত দেয় যাতে stream শেষ হলে সংযোগ বন্ধ করা যায়।
3. [`StreamedRunResult.stream_text()`][pydantic_ai.result.StreamedRunResult.stream_text]-এর দেওয়া প্রতিটি আইটেম হলো সম্পূর্ণ লেখার উত্তর, নতুন ডেটা আসার সাথে সাথে বাড়তে থাকে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

[`stream_text()`][pydantic_ai.result.StreamedRunResult.stream_text]-এর ঐচ্ছিক `debounce_by` আর্গুমেন্ট নিয়ন্ত্রণ করে, দেওয়ার আগে Pydantic AI আসা টুকরোগুলো কতক্ষণ ধরে একসাথে জড়ো করবে। ডিফল্ট `0.1` সর্বোচ্চ 0.1 সেকেন্ড পর্যন্ত টুকরো জড়ো করে; প্রতিটি টুকরো আসার সাথে সাথেই দিতে `None` দিন। লম্বা গোছানো উত্তরে debounce বিশেষভাবে সহায়ক, যেখানে এটি প্রতিটি টুকরো আসার সাথে সাথে যাচাইয়ের বাড়তি খরচ কমায়।

প্রতিটি আইটেমে পুরো লেখার বদলে আমরা লেখা delta (শুধু নতুন অংশ) হিসেবেও stream করতে পারি:

```python title="streamed_delta_hello_world.py"
from pydantic_ai import Agent

agent = Agent('google:gemini-3.8-flash')


async def main():
    async with agent.run_stream('Where does "hello world" come from?') as result:
        async for message in result.stream_text(delta=True):  # (1)!
            print(message)
            #> The first known
            #> use of "hello,
            #> world" was in
            #> a 1974 textbook
            #> about the C
            #> programming language.
```

1. উত্তরটি লেখা না হলে [`stream_text`][pydantic_ai.result.StreamedRunResult.stream_text] এরর দেবে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// info | `delta=False` বনাম `delta=True`

ধরুন মডেল লিখছে "আমি ভালো আছি"। `delta=False` (ডিফল্ট) দেয় "আমি", "আমি ভালো", "আমি ভালো আছি" — প্রতিবার এ পর্যন্ত পুরোটা, তাই স্ক্রিনের লেখা প্রতিবার বদলে দিন। `delta=True` দেয় "আমি", " ভালো", " আছি" — শুধু নতুন টুকরো, তাই আগের লেখার সাথে জুড়ে দিন।

///

/// warning | আউটপুট বার্তা `messages`-এ যোগ হয় না

আপনি `.stream_text(delta=True)` ব্যবহার করলে চূড়ান্ত আউটপুট বার্তা ফলের বার্তায় যোগ **হবে না**,
আরও তথ্যের জন্য দেখুন [Messages and chat history](message-history.md)।

///

/// note | `stream_text()` `TextOutput` ফাংশন এড়িয়ে যায়

[`stream_text()`][pydantic_ai.result.StreamedRunResult.stream_text] [`TextOutput`](#text-output) ফাংশন প্রয়োগ **করে না**। `delta=False`-এ এটি জমা হওয়া প্রতিটি লেখার snapshot-এ [আউটপুট validator](#output-validator-functions) প্রয়োগ করে, তাই একটি validator যা দেওয়া হয় তা বদলাতে পারে; `delta=True`-তে এটি কাঁচা লেখার delta দেয় আর validator এড়িয়ে যায়। আপনার `TextOutput` ফাংশনের তৈরি মান stream করতে, বদলে [`stream_output()`][pydantic_ai.result.StreamedRunResult.stream_output] ব্যবহার করুন।

///

### গোছানো আউটপুট stream করা { #streaming-structured-output }

তৈরি হতে হতে একটি ব্যবহারকারীর প্রোফাইল stream করার একটি উদাহরণ:

```python title="streamed_user_profile.py"
from datetime import date
from typing import NotRequired

from typing_extensions import TypedDict

from pydantic_ai import Agent


class UserProfile(TypedDict):
    name: str
    dob: NotRequired[date]
    bio: NotRequired[str]


agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=UserProfile,
    instructions='Extract a user profile from the input',
)


async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for profile in result.stream_output():
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

#### গোছানো উত্তর দ্রুত দেখানো { #making-structured-responses-appear-faster }

একটি গোছানো উত্তর আপনার অ্যাপ্লিকেশনে দেখা দিতে অনেক সময় নিলে, নিশ্চিত করুন পুরো রান শেষ হওয়ার অপেক্ষা না করে আপনি যাচাই হওয়া আংশিক আউটপুট stream করছেন। [`stream_output()`][pydantic_ai.result.StreamedRunResult.stream_output] মডেল তৈরি করার সাথে সাথে জমা হওয়া আউটপুট দেয়, প্রতিটি snapshot-এ partial validation আর চূড়ান্ত আউটপুটে পূর্ণ যাচাই প্রয়োগ করে।

মাঝের মডেল রিকোয়েস্ট আর টুল কলের event-ও দরকার হলে, [`agent.iter()`][pydantic_ai.agent.AbstractAgent.iter] ব্যবহার করুন। মডেল চূড়ান্ত ফল তৈরি শুরু না করা পর্যন্ত প্রতিটি `AgentStream`-এর ওপর iterate করুন, তারপর যাচাই হওয়া আংশিক আউটপুটের জন্য `stream_output()`-এ চলে যান:

```python title="stream_structured_output_and_events.py"
from pydantic import BaseModel

from pydantic_ai import Agent, AgentStreamEvent, FinalResultEvent


class Client(BaseModel):
    id: int
    name: str


agent = Agent(
    'openai:gpt-6.1-sol',
    output_type=list[str | Client],
    instructions='Find the requested clients and explain each match.',
)


def record_event(event: AgentStreamEvent) -> None:
    ...


def render_output(output: list[str | Client]) -> None:
    ...


async def main():
    async with agent.iter('Find clients named Jane') as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as stream:
                    final_result_started = False
                    async for event in stream:
                        record_event(event)
                        if isinstance(event, FinalResultEvent):
                            final_result_started = True
                            break

                    if final_result_started:
                        async for output in stream.stream_output():
                            render_output(output)
            elif Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as stream:
                    async for event in stream:
                        record_event(event)
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

`stream_output()`-এর প্রতিটি মান একটি জমা হওয়া snapshot, delta নয়। partial validation পাস করার মতো যথেষ্ট ডেটা না আসা পর্যন্ত একটি অসম্পূর্ণ ফিল্ড বা তালিকার আইটেম অনুপস্থিত থাকতে পারে, তাই প্রতিটি yield জুড়ে না দিয়ে প্রতিটি snapshot থেকে দেখানো মান হালনাগাদ করুন।

`AgentStream` একটি একক iterator। একবার `stream_output()`-এ চলে গেলে, এটি বাকি চূড়ান্ত-আউটপুট event যাচাই করতে করতে খরচ করে ফেলে, তাই সেই কাঁচা event-গুলো আগের loop-এ আর দেওয়া হয় না। প্রতিটি কাঁচা event রাখতে হলে, [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] ব্যবহার করে নিজে আউটপুট পুনর্গঠন আর যাচাই করুন।

যেহেতু `output_type` সেট করলে ডিফল্টভাবে [Tool Output](#tool-output) মোড ব্যবহার হয়, এটি শুধু তখনই কাজ করবে যখন মডেল টুলের আর্গুমেন্ট stream করা সমর্থন করে। যেসব মডেল করে না, সেগুলোতে বদলে [Native Output](#native-output) বা [Prompted Output](#prompted-output) চেষ্টা করুন। Gemini 3-এ Native Output ব্যবহার করুন; ফাংশন টুলও ব্যবহার করা আগের Gemini মডেলে Prompted Output ব্যবহার করুন।

### মডেলের উত্তর stream করা { #streaming-model-responses }

যাচাইয়ের ওপর সূক্ষ্ম নিয়ন্ত্রণ চাইলে, পুরো আংশিক [`ModelResponse`][pydantic_ai.messages.ModelResponse] পেতে নিচের ধরন ব্যবহার করতে পারেন:

```python title="streamed_user_profile.py"
from datetime import date

from pydantic import ValidationError
from typing_extensions import TypedDict

from pydantic_ai import Agent


class UserProfile(TypedDict, total=False):
    name: str
    dob: date
    bio: str


agent = Agent('openai:gpt-6.1-sol', output_type=UserProfile)


async def main():
    user_input = 'My name is Ben, I was born on January 28th 1990, I like the chain the dog and the pyramid.'
    async with agent.run_stream(user_input) as result:
        async for message in result.stream_response(debounce_by=0.01):  # (1)!
            try:
                profile = await result.validate_response_output(  # (2)!
                    message,
                    allow_partial=message.state == 'incomplete',
                )
            except ValidationError:
                continue
            print(profile)
            #> {'name': 'Ben'}
            #> {'name': 'Ben'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the '}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyr'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
            #> {'name': 'Ben', 'dob': date(1990, 1, 28), 'bio': 'Likes the chain the dog and the pyramid'}
```

1. [`stream_response`][pydantic_ai.result.StreamedRunResult.stream_response] ডেটা [`ModelResponse`][pydantic_ai.messages.ModelResponse] অবজেক্ট হিসেবে stream করে, তাই iteration একটি `ValidationError` দিয়ে ব্যর্থ হতে পারে না।
2. [`validate_response_output`][pydantic_ai.result.StreamedRunResult.validate_response_output] ডেটা যাচাই করে, `allow_partial=True` pydantic-এর [`TypeAdapter`-এর `experimental_allow_partial` ফ্ল্যাগ][pydantic.type_adapter.TypeAdapter.validate_json] চালু করে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

### Stream বাতিল করা { #cancelling-streams }

কখনো কখনো একটি stream করা উত্তর শেষ হওয়ার আগেই থামাতে হয়: একজন ব্যবহারকারী চ্যাট UI-তে "stop generating" চাপেন, সিদ্ধান্ত নেওয়ার মতো যথেষ্ট ডেটা আপনি পেয়ে গেছেন, বা আরও token পাওয়া এড়াতে চান। [`run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] আর [`iter()`][pydantic_ai.agent.Agent.iter] ভেতরের মডেল stream বন্ধ করে স্পষ্ট বাতিল সমর্থন করে। [`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] একটি async context manager, তাই event নেওয়া থামালে পরিষ্কারের কাজ নিশ্চিতভাবে চলে — `async with` ব্লক ছেড়ে গেলে পেছনের রান task বাতিল হয়। stream নয় এমন একটি রান থামাতে, দেখুন [Cancelling a Run](agent.md#cancelling-a-run); একটি একক ধাপ কতক্ষণ নিতে পারে তা বেঁধে দিতে, দেখুন [Timeouts](timeouts.md)।

/// note | মডেলের সমর্থন

Google, xAI আর Hugging Face SDK stream শুধু async iterator হিসেবে দেয়, প্রতি-stream-এর নথিভুক্ত transport handle ছাড়া। Pydantic AI নিরাপদে তার সক্রিয় iterator থেকে টানা থামায়, কিন্তু SDK-গুলো নিশ্চয়তা দেয় না যে স্থানীয় iterator বন্ধ করলে দূরের তৈরি বা বিলিং সাথে সাথে থামে। দেখুন [Google](models/google.md#streaming-cancellation), [xAI](models/xai.md#streaming-cancellation) আর [Hugging Face](models/huggingface.md#streaming-cancellation) provider-এর নোট।

///

#### `run_stream_events` পরিষ্কার করা { #cleaning-up-run_stream_events }

[`run_stream_events()`][pydantic_ai.agent.AbstractAgent.run_stream_events] একটি async context manager, যা event-এর ওপর একটি async iterator দেয়:

```python title="stream_cancel_stream_events.py"
from pydantic_ai import Agent, FinalResultEvent, PartStartEvent

agent = Agent('openai:gpt-6.1-sol')


async def main():
    async with agent.run_stream_events('Write a long essay about Python') as events:
        async for event in events:
            if isinstance(event, PartStartEvent):
                print(f'Started: {event.part!r}')
                #> Started: TextPart(content='Python is a ')
            elif isinstance(event, FinalResultEvent):
                break  # (1)!
```

1. loop থেকে বেরিয়ে গেলে `async with` ব্লক ছেড়ে যাওয়া হয়, যা পেছনের রান task বাতিল করে আর HTTP সংযোগ বন্ধ করে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

দেওয়া [`AgentRunEvents`][pydantic_ai.agent.AgentRunEvents] handle পুরো রান বাতিল করতে `cancel()` দেয় (দেখুন [Cancelling a Run](agent.md#cancelling-a-run)); এরপর iteration চালিয়ে গেলে [`RunCancelled`][pydantic_ai.exceptions.RunCancelled] ওঠে। এটি `all_messages()`, `new_messages()`, `usage` আর সম্পূর্ণ `result`-ও দেয়। একটি টুল বা `event_stream_handler`-এর ভেতর থেকে, বদলে [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel] ব্যবহার করুন। উত্তর-স্তরের একটি বিকল্প হিসেবে, `run_stream()` থেকে পাওয়া [`StreamedRunResult.cancel()`][pydantic_ai.result.StreamedRunResult.cancel] শুধু বর্তমান মডেল উত্তর থামায়।

#### `run_stream` বাতিল করা { #cancelling-run_stream }

stream বাতিল করতে [`StreamedRunResult`][pydantic_ai.result.StreamedRunResult]-এ `cancel()` ডাকুন:

```python title="stream_cancel_stream.py"
from pydantic_ai import Agent

agent = Agent('openai:gpt-6.1-sol')


async def main():
    async with agent.run_stream('Write a long essay about Python') as result:
        text = ''
        async for chunk in result.stream_text(delta=True):
            text += chunk
            if len(text) > 100:  # (1)!
                await result.cancel()  # (2)!
                break
        print(result.cancelled)  # (3)!
        #> True
        print(result.response.state == 'interrupted')  # (4)!
        #> True
```

1. stream চলার সময় একটি শর্ত পরীক্ষা করুন, যেমন যথেষ্ট লেখা এসেছে কিনা।
2. `cancel()` মডেল provider-কে token তৈরি থামাতে বলে আর মডেল integration সমর্থন করলে HTTP সংযোগ বন্ধ করে।
3. `cancelled` property বাতিলের অবস্থা দেখায়।
4. চূড়ান্ত [`ModelResponse`][pydantic_ai.messages.ModelResponse] `state='interrupted'` দিয়ে চিহ্নিত হয়, যাতে পরের কোড অসম্পূর্ণ উত্তর চিনতে পারে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

আপনি `stream_text()` থেকে `break` করে তারপর চারপাশের `async with` ব্লক ছেড়ে গেলে, context বেরোনোর সময় stream পরিষ্কার হয়ে যায়। শুধু স্থানীয়ভাবে নেওয়া থামানোর বদলে সাথে সাথে তৈরি থামাতে চাইলে `cancel()` ব্যবহার করুন।

/// warning | বাধাপ্রাপ্ত টুল কল

একটি মডেল উত্তরের stream বাতিল করলে বা তা থেকে বেরিয়ে গেলে চূড়ান্ত [`ModelResponse`][pydantic_ai.messages.ModelResponse]-এ অসম্পূর্ণ টুল-কলের আর্গুমেন্ট থেকে যেতে পারে। Pydantic AI উত্তরটি `state='interrupted'` দিয়ে রেকর্ড করে, আর ইতিহাসটি আরেকটি রানে আবার ব্যবহার হলে আংশিক টুল কলগুলো [নিজে থেকে মেরামত](message-history.md#making-histories-provider-valid) হয়। আপনি [`agent.iter()`][pydantic_ai.agent.Agent.iter] দিয়ে graph নিয়ন্ত্রণ করলে, পুরো রানও থামাতে [`agent_run.cancel()`][pydantic_ai.run.AgentRun.cancel] ডাকুন, বা রানকে টুল চালানোয় এগোতে দেওয়ার আগে `response.state == 'interrupted'` পরীক্ষা করুন।

///

#### `iter` দিয়ে বাতিল করা { #cancelling-with-iter }

এজেন্ট graph-এর ওপর সূক্ষ্ম নিয়ন্ত্রণের জন্য [`agent.iter()`][pydantic_ai.agent.Agent.iter] ব্যবহার করলে, একটি `ModelRequestNode.stream()` context-এর ভেতরে [`AgentStream`][pydantic_ai.result.AgentStream] বাতিল করতে পারেন:

```python title="stream_cancel_iter.py"
from pydantic_ai import Agent, FinalResultEvent

agent = Agent('openai:gpt-6.1-sol')


async def main():
    async with agent.iter('Write a long essay about Python') as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as stream:
                    async for event in stream:
                        if isinstance(event, FinalResultEvent):
                            await stream.cancel()  # (1)!
                            break
```

1. `AgentStream.cancel()` মডেল রিকোয়েস্টের স্তরে stream বাতিল করে।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

শুধু বর্তমান উত্তর নয়, রানটিই বাতিল করতে -- আর বাতিল কীভাবে বার্তার ইতিহাসে রেকর্ড হয় তা জানতে -- দেখুন [Cancelling a Run](agent.md#cancelling-a-run)।

## উদাহরণ { #examples }

নিচের উদাহরণগুলো দেখায় Pydantic AI-তে stream করা উত্তর কীভাবে ব্যবহার করবেন:

- [Stream markdown](examples/stream-markdown.md)
- [Stream Whales](examples/stream-whales.md)

/// check | সংক্ষেপে মনে রাখুন

* `output_type` উত্তরের গঠন ঠিক করে: `str`, Pydantic মডেল, dataclass, `TypedDict`, union, বা একাধিকের তালিকা।
* আউটপুট ফাংশন = মডেলের দেওয়া আর্গুমেন্টে চলা ফাংশন, যা রান শেষ করে; stream-এ পার্শ্বপ্রতিক্রিয়ার আগে `ctx.partial_output` দেখুন।
* তিন মোড: `ToolOutput` (ডিফল্ট, সবচেয়ে নির্ভরযোগ্য), `NativeOutput` (মডেলের নিজস্ব JSON schema), `PromptedOutput` (নির্দেশনায় schema)।
* চলার সময় জানা বিকল্পে `Choices`; বাইরের JSON schema-তে `StructuredDict` (যাচাই হয় না)।
* async বা IO-নির্ভর যাচাইয়ে `@agent.output_validator` আর `ModelRetry`।
* `None` অনুমোদন করতে `output_type`-এ `None` রাখুন; ছবির জন্য `BinaryImage`।
* stream: লেখায় `stream_text()`, গোছানো ডেটায় `stream_output()`; থামাতে `cancel()`।

///
