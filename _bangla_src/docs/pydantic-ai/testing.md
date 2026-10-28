
# Unit testing { #unit-testing }

/// note | এই পেজে যা শিখবেন

* আসল LLM না ডেকে Pydantic AI কোডের unit test কীভাবে লিখবেন।
* `TestModel` (নিজে থেকে সব টুল ডাকে) আর `FunctionModel` (আপনি ঠিক করেন মডেল কী বলবে) — কখন কোনটি।
* `Agent.override` দিয়ে কোড না বদলে মডেল বদলানো, আর `ALLOW_MODEL_REQUESTS=False` দিয়ে ভুল করে আসল রিকোয়েস্ট আটকানো।
* `capture_run_messages` দিয়ে এজেন্ট আর মডেলের আদান-প্রদান যাচাই।

///

একটি এজেন্ট deploy করার আগে, আর এরপর প্রতিটি পরিবর্তনে, unit test মডেলকে ঘিরে থাকা আপনার নিজের কোড যাচাই করে: টুল, dependency, আউটপুট যাচাই আর ব্যর্থতা সামলানো, কোনো মডেল রিকোয়েস্ট ছাড়া আর প্রতিবার একই ফল দিয়ে। এগুলো বলে না মডেলের উত্তর ভালো কিনা; তার জন্য আছে [evals](evals.md)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি গাড়ির কারখানায় ইঞ্জিন পরীক্ষার জন্য আসল রাস্তায় চালানো লাগে না — একটা টেস্ট-বেঞ্চে বসিয়ে দেখা হয় গিয়ার, ব্রেক, তার ঠিকমতো কাজ করছে কিনা। `TestModel` হলো সেই টেস্ট-বেঞ্চ: আসল LLM-এর জায়গায় বসে, তাই টেস্ট দ্রুত, বিনামূল্যে আর প্রতিবার একই ফল দেয়। আর গাড়িটা আসলে কতটা "ভালো চালায়" — সেটা মাপে evals।

///

Pydantic AI কোডের জন্য unit test লেখা অন্য যেকোনো Python কোডের unit test-এর মতোই।

যেহেতু বেশিরভাগ ক্ষেত্রে এগুলো নতুন কিছু নয়, এ ধরনের টেস্ট লেখা আর চালানোর জন্য আমাদের বেশ প্রতিষ্ঠিত টুল আর ধরন আছে।

আপনি নিশ্চিতভাবে ভালো কিছু না জানলে, সম্ভবত মোটামুটি এই কৌশল অনুসরণ করতে চাইবেন:

- আপনার test harness হিসেবে [`pytest`](https://docs.pytest.org/en/stable/) ব্যবহার করুন
- লম্বা assertion টাইপ করতে থাকলে, [inline-snapshot](https://15r10nk.github.io/inline-snapshot/latest/) ব্যবহার করুন
- একইভাবে, বড় ডেটা কাঠামো তুলনা করতে [dirty-equals](https://dirty-equals.helpmanual.io/latest/) কাজের হতে পারে
- আসল LLM কলের usage, দেরি আর অনিশ্চয়তা এড়াতে আপনার আসল মডেলের জায়গায় [`TestModel`][pydantic_ai.models.test.TestModel] বা [`FunctionModel`][pydantic_ai.models.function.FunctionModel] ব্যবহার করুন
- ছবি তৈরি করা কোডের জন্য, একইভাবে [`TestImageGenerationModel`][pydantic_ai.images.TestImageGenerationModel] ব্যবহার করুন — দেখুন [Image Generation: Testing](image-generation.md#testing)
- আপনার অ্যাপ্লিকেশনের লজিকের ভেতরে একটি এজেন্টের মডেল, dependency বা toolset বদলাতে [`Agent.override`][pydantic_ai.agent.Agent.override] ব্যবহার করুন
- non-test মডেলে ভুল করে কোনো রিকোয়েস্ট যাওয়া আটকাতে বৈশ্বিকভাবে [`ALLOW_MODEL_REQUESTS=False`][pydantic_ai.models.ALLOW_MODEL_REQUESTS] সেট করুন

### `TestModel` দিয়ে unit testing { #unit-testing-with-testmodel }

আপনার অ্যাপ্লিকেশন কোডের বেশিরভাগ চালিয়ে দেখার সবচেয়ে সহজ আর দ্রুত উপায় হলো [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করা; এটি (ডিফল্টভাবে) এজেন্টের সব টুল ডাকবে, তারপর এজেন্টের return type অনুযায়ী হয় সাধারণ লেখা নয়তো একটি কাঠামোবদ্ধ response ফেরত দেবে।

/// note | `TestModel` কোনো জাদু নয়

`TestModel`-এর "চতুর" (কিন্তু খুব বেশি চতুর নয়) অংশ হলো, এটি নিবন্ধিত টুলের schema-র ভিত্তিতে [ফাংশন টুল](tools.md) আর [output type](output.md#structured-output)-এর জন্য বৈধ কাঠামোবদ্ধ ডেটা তৈরির চেষ্টা করবে।

`TestModel`-এ কোনো ML বা AI নেই, এটি শুধু সাধারণ পুরনো procedural Python কোড, যা একটি টুলের JSON schema মেনে চলে এমন ডেটা তৈরির চেষ্টা করে।

ফলের ডেটা দেখতে সুন্দর বা প্রাসঙ্গিক হবে না, তবে বেশিরভাগ ক্ষেত্রে Pydantic-এর যাচাই পার হওয়ার কথা।
আরও উন্নত কিছু চাইলে, [`FunctionModel`][pydantic_ai.models.function.FunctionModel] ব্যবহার করে নিজের ডেটা তৈরির লজিক লিখুন।

///

/// note | নেটিভ টুলসহ এজেন্ট টেস্ট করা

[`TestModel`][pydantic_ai.models.test.TestModel] provider-এ চলা [নেটিভ টুল](native-tools.md) অনুকরণ করতে পারে না।
আপনার প্রোডাকশন এজেন্ট `capabilities` দিয়ে নেটিভ টুলসহ কনফিগার করা থাকলে, টেস্টে এগুলো override করুন
`agent.override(model=TestModel(), native_tools=[])` দিয়ে, যদি না টেস্টটি নির্দিষ্টভাবে যাচাই করে যে নেটিভ টুল মডেলে পাঠানো হচ্ছে।

///

চলুন নিচের অ্যাপ্লিকেশন কোডের জন্য unit test লিখি:

```python title="weather_app.py"
import asyncio
from datetime import date

from pydantic_ai import Agent, RunContext

from fake_database import DatabaseConn  # (1)!
from weather_service import WeatherService  # (2)!

weather_agent = Agent(
    'openai:gpt-6.1-sol',
    deps_type=WeatherService,
    instructions='Providing a weather forecast at the locations the user provides.',
)


@weather_agent.tool
def weather_forecast(
    ctx: RunContext[WeatherService], location: str, forecast_date: date
) -> str:
    if forecast_date < date.today():  # (3)!
        return ctx.deps.get_historic_weather(location, forecast_date)
    else:
        return ctx.deps.get_forecast(location, forecast_date)


async def run_weather_forecast(  # (4)!
    user_prompts: list[tuple[str, int]], conn: DatabaseConn
):
    """Run weather forecast for a list of user prompts and save."""
    async with WeatherService() as weather_service:

        async def run_forecast(prompt: str, user_id: int):
            result = await weather_agent.run(prompt, deps=weather_service)
            await conn.store_forecast(user_id, result.output)

        # run all prompts in parallel
        await asyncio.gather(
            *(run_forecast(prompt, user_id) for (prompt, user_id) in user_prompts)
        )
```

1. `DatabaseConn` একটি ক্লাস যা একটি ডেটাবেস সংযোগ রাখে
2. `WeatherService`-এ আবহাওয়ার পূর্বাভাস আর আবহাওয়ার ঐতিহাসিক ডেটা পাওয়ার মেথড আছে
3. তারিখটি অতীতে না ভবিষ্যতে তার ওপর নির্ভর করে আমাদের ভিন্ন endpoint ডাকতে হয়; এই সূক্ষ্মতা কেন জরুরি তা নিচে দেখবেন
4. এই ফাংশনটি হলো সেই কোড যা আমরা টেস্ট করতে চাই, এটি যে এজেন্ট ব্যবহার করে তার সাথে

এখানে আমাদের একটি ফাংশন আছে যা `#!python (user_prompt, user_id)` tuple-এর একটি লিস্ট নেয়, প্রতিটি prompt-এর জন্য একটি আবহাওয়ার পূর্বাভাস নেয়, আর ফল ডেটাবেসে রাখে।

**আমরা এই কোড টেস্ট করতে চাই কিছু অবজেক্ট mock না করে বা test অবজেক্ট পাঠানোর জন্য আমাদের কোড না বদলে।**

[`TestModel`][pydantic_ai.models.test.TestModel] দিয়ে আমরা কীভাবে টেস্ট লিখব:

```python title="test_weather_app.py"
from datetime import UTC
import pytest

from dirty_equals import IsNow, IsStr

from pydantic_ai import models, capture_run_messages, RequestUsage
from pydantic_ai.models.test import TestModel
from pydantic_ai import (
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
    ModelRequest,
)

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio  # (1)!
models.ALLOW_MODEL_REQUESTS = False  # (2)!


async def test_forecast():
    conn = DatabaseConn()
    user_id = 1
    with capture_run_messages() as messages:
        with weather_agent.override(model=TestModel()):  # (3)!
            prompt = 'What will the weather be like in London on 2024-11-28?'
            await run_weather_forecast([(prompt, user_id)], conn)  # (4)!

    forecast = await conn.get_forecast(user_id)
    assert forecast == '{"weather_forecast":"Sunny with a chance of rain"}'  # (5)!

    assert messages == [  # (6)!
        ModelRequest(
            parts=[
                UserPromptPart(
                    content='What will the weather be like in London on 2024-11-28?',
                    timestamp=IsNow(tz=UTC),  # (7)!
                ),
            ],
            instructions='Providing a weather forecast at the locations the user provides.',
            timestamp=IsNow(tz=UTC),
            run_id=IsStr(),
            conversation_id=IsStr(),
        ),
        ModelResponse(
            parts=[
                ToolCallPart(
                    tool_name='weather_forecast',
                    args={
                        'location': 'a',
                        'forecast_date': '2024-01-01',  # (8)!
                    },
                    tool_call_id=IsStr(),
                )
            ],
            usage=RequestUsage(
                input_tokens=60,
                output_tokens=7,
            ),
            model_name='test',
            timestamp=IsNow(tz=UTC),
            provider_name='test',
            run_id=IsStr(),
            conversation_id=IsStr(),
        ),
        ModelRequest(
            parts=[
                ToolReturnPart(
                    tool_name='weather_forecast',
                    content='Sunny with a chance of rain',
                    tool_call_id=IsStr(),
                    timestamp=IsNow(tz=UTC),
                ),
            ],
            instructions='Providing a weather forecast at the locations the user provides.',
            timestamp=IsNow(tz=UTC),
            run_id=IsStr(),
            conversation_id=IsStr(),
        ),
        ModelResponse(
            parts=[
                TextPart(
                    content='{"weather_forecast":"Sunny with a chance of rain"}',
                )
            ],
            usage=RequestUsage(
                input_tokens=66,
                output_tokens=16,
            ),
            model_name='test',
            timestamp=IsNow(tz=UTC),
            provider_name='test',
            run_id=IsStr(),
            conversation_id=IsStr(),
        ),
    ]
```

1. async টেস্ট চালাতে আমরা [anyio](https://anyio.readthedocs.io/en/stable/) ব্যবহার করছি।
2. এটি একটি নিরাপত্তা ব্যবস্থা, যাতে টেস্টের সময় আমরা ভুল করে LLM-এ আসল রিকোয়েস্ট না পাঠাই; আরও বিস্তারিতের জন্য দেখুন [`ALLOW_MODEL_REQUESTS`][pydantic_ai.models.ALLOW_MODEL_REQUESTS]।
3. এজেন্টের মডেল [`TestModel`][pydantic_ai.models.test.TestModel] দিয়ে বদলাতে আমরা [`Agent.override`][pydantic_ai.agent.Agent.override] ব্যবহার করছি; `override`-এর সুবিধা হলো আমরা এজেন্টের `run*` মেথড যেখানে ডাকা হয় সেখানে প্রবেশ ছাড়াই এজেন্টের ভেতরের মডেল বদলাতে পারি।
4. এখন আমরা যে ফাংশন টেস্ট করতে চাই তা `override` context manager-এর ভেতরে ডাকি।
5. ডিফল্টভাবে, `TestModel` একটি JSON string ফেরত দেবে যা করা টুল কল আর কী ফেরত এসেছে তার সারাংশ দেয়। আপনি যদি response-কে বিষয়ের সাথে আরও মানানসই কিছুতে বদলাতে চান, `TestModel` সংজ্ঞায়িত করার সময় [`custom_output_text='Sunny'`][pydantic_ai.models.test.TestModel.custom_output_text] যোগ করতে পারেন।
6. এখন পর্যন্ত আমরা আসলে জানি না কোন টুল কোন মান দিয়ে ডাকা হয়েছে; আমরা সাম্প্রতিকতম রানের বার্তা পরীক্ষা করতে আর এজেন্ট ও মডেলের আদান-প্রদান প্রত্যাশামতো হয়েছে তা assert করতে [`capture_run_messages`][pydantic_ai.capture_run_messages] ব্যবহার করতে পারি।
7. [`IsNow`][dirty_equals.IsNow] helper আমাদের এমন ডেটা দিয়েও ঘোষণামূলক assert ব্যবহার করতে দেয়, যাতে সময়ের সাথে বদলানো timestamp থাকবে।
8. `TestModel` prompt থেকে মান বের করতে চতুর কিছু করে না, তাই এই মানগুলো hardcode করা।

/// info | কোডটি সহজ ভাষায়

* `models.ALLOW_MODEL_REQUESTS = False` — নিরাপত্তা-জাল: কোনো টেস্ট ভুল করে আসল OpenAI-কে ডাকলে সাথে সাথে ব্যর্থ হবে (টাকা খরচ হবে না)।
* `with weather_agent.override(model=TestModel()):` — এই ব্লকের ভেতরে এজেন্ট যেখানেই চলুক, আসল মডেলের বদলে `TestModel` চলবে। আপনার অ্যাপ্লিকেশন কোডে একটা লাইনও বদলাতে হয়নি।
* `with capture_run_messages() as messages:` — রানের সব বার্তা (prompt, টুল কল, টুলের ফল, উত্তর) ধরে রাখে, যাতে আপনি assert করতে পারেন "হ্যাঁ, `weather_forecast` টুল ঠিক এই আর্গুমেন্ট দিয়ে ডাকা হয়েছে"।

///

### `FunctionModel` দিয়ে unit testing { #unit-testing-with-functionmodel }

ওপরের টেস্টগুলো একটি দারুণ শুরু, কিন্তু মনোযোগী পাঠক লক্ষ্য করবেন যে `WeatherService.get_forecast` কখনো ডাকা হয় না, কারণ `TestModel` `weather_forecast`-কে অতীতের একটি তারিখ দিয়ে ডাকে।

`weather_forecast` পুরোপুরি চালিয়ে দেখতে, টুল কীভাবে ডাকা হবে তা কাস্টমাইজ করতে আমাদের [`FunctionModel`][pydantic_ai.models.function.FunctionModel] ব্যবহার করতে হবে।

নিজের input দিয়ে `weather_forecast` টুল টেস্ট করতে `FunctionModel` ব্যবহারের একটি উদাহরণ

```python title="test_weather_app2.py"
import re

import pytest

from pydantic_ai import models
from pydantic_ai import (
    ModelMessage,
    ModelResponse,
    TextPart,
    ToolCallPart,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

from fake_database import DatabaseConn
from weather_app import run_weather_forecast, weather_agent

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


def call_weather_forecast(  # (1)!
    messages: list[ModelMessage], info: AgentInfo
) -> ModelResponse:
    if len(messages) == 1:
        # first call, call the weather forecast tool
        user_prompt = messages[0].parts[-1]
        assert isinstance(user_prompt, UserPromptPart)
        assert isinstance(user_prompt.content, str)
        m = re.search(r'\d{4}-\d{2}-\d{2}', user_prompt.content)
        assert m is not None
        args = {'location': 'London', 'forecast_date': m.group()}  # (2)!
        return ModelResponse(parts=[ToolCallPart('weather_forecast', args)])
    else:
        # second call, return the forecast
        msg = messages[-1].parts[0]
        assert msg.part_kind == 'tool-return'
        return ModelResponse(parts=[TextPart(f'The forecast is: {msg.content}')])


async def test_forecast_future():
    conn = DatabaseConn()
    user_id = 1
    with weather_agent.override(model=FunctionModel(call_weather_forecast)):  # (3)!
        prompt = 'What will the weather be like in London on 2032-01-01?'
        await run_weather_forecast([(prompt, user_id)], conn)

    forecast = await conn.get_forecast(user_id)
    assert forecast == 'The forecast is: Rainy with a chance of sun'
```

1. আমরা একটি ফাংশন `call_weather_forecast` সংজ্ঞায়িত করি, যা LLM-এর জায়গায় `FunctionModel` ডাকবে; এই ফাংশন রানটি গঠন করা [`ModelMessage`][pydantic_ai.messages.ModelMessage]-এর লিস্ট আর [`AgentInfo`][pydantic_ai.models.function.AgentInfo] পায়, যাতে এজেন্ট আর ফাংশন টুল ও return টুল সম্পর্কে তথ্য থাকে।
2. আমাদের ফাংশন একটু বুদ্ধিমান, কারণ এটি prompt থেকে একটি তারিখ বের করার চেষ্টা করে, কিন্তু অবস্থান শুধু hardcode করে।
3. এজেন্টের মডেল আমাদের নিজের ফাংশন দিয়ে বদলাতে আমরা [`FunctionModel`][pydantic_ai.models.function.FunctionModel] ব্যবহার করি।

আপনার বদলি মডেলের যদি রিকোয়েস্টের মাঝে state বহন করতে হয়, `FunctionModel` একটি ফাংশনের জায়গায় একটি `async def __call__`-সহ callable instance-ও নেয়; উদাহরণের জন্য দেখুন [`FunctionModel` API ডক](api/models/function.md)।

/// info | এক নজরে: `TestModel` বনাম `FunctionModel`

| | `TestModel` | `FunctionModel` |
|--|-------------|-----------------|
| কী করে | নিজে থেকে সব টুল ডাকে, schema মেনে নকল ডেটা বানায় | আপনার লেখা ফাংশন ঠিক করে মডেল কী "বলবে" |
| পরিশ্রম | প্রায় শূন্য | একটি ফাংশন লিখতে হয় |
| কখন | দ্রুত smoke test: সব টুল আর আউটপুট টাইপ চলে কিনা | নির্দিষ্ট পথ টেস্ট: নির্দিষ্ট আর্গুমেন্ট, নির্দিষ্ট ক্রম, ভুল আর্গুমেন্টে retry |

///

### pytest fixture দিয়ে মডেল override করা { #overriding-model-via-pytest-fixtures }

আপনি যদি অনেক টেস্ট লেখেন যেগুলোর সবগুলোতে মডেল override করা লাগে, তবে [`TestModel`][pydantic_ai.models.test.TestModel] বা [`FunctionModel`][pydantic_ai.models.function.FunctionModel] দিয়ে মডেলটি পুনর্ব্যবহারযোগ্যভাবে override করতে [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) ব্যবহার করতে পারেন।

`TestModel` দিয়ে মডেল override করা একটি fixture-এর উদাহরণ:

```python title="test_agent.py"
import pytest

from pydantic_ai.models.test import TestModel

from weather_app import weather_agent


@pytest.fixture
def override_weather_agent():
    with weather_agent.override(model=TestModel()):
        yield


async def test_forecast(override_weather_agent: None):
    ...
    # test code here
```

/// warning | সাধারণ ভুল

* `Agent.override` ছাড়া টেস্টে এজেন্টকে নতুন করে তৈরি করা (`Agent(TestModel(), ...)`) — তখন আপনি আপনার আসল এজেন্ট (এর টুল, instructions) টেস্টই করছেন না।
* `ALLOW_MODEL_REQUESTS = False` ভুলে যাওয়া — একটি override বাদ পড়লে টেস্ট নিঃশব্দে আসল API ডাকে, ধীর হয়, টাকা খরচ করে, আর CI-তে API key না থাকলে রহস্যময়ভাবে ব্যর্থ হয়।

///

/// check | সংক্ষেপে মনে রাখুন

* unit test আপনার কোড (টুল, dependency, যাচাই) পরীক্ষা করে; মডেলের মান মাপে evals।
* `TestModel` সব টুল ডাকে আর নকল বৈধ ডেটা বানায়; `FunctionModel`-এ আপনি মডেলের উত্তর নিজে লেখেন।
* `agent.override(model=...)` দিয়ে অ্যাপ্লিকেশন কোড না বদলে মডেল বদলান; নেটিভ টুল থাকলে `native_tools=[]`।
* `ALLOW_MODEL_REQUESTS = False` দিয়ে আসল রিকোয়েস্ট আটকান; `capture_run_messages` দিয়ে আদান-প্রদান assert করুন।
* অনেক টেস্টে একই override লাগলে pytest fixture বানান।

///
