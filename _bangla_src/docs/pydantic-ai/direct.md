# সরাসরি মডেল রিকোয়েস্ট (Direct Model Requests) { #direct-model-requests }

/// note | এই পেজে যা শিখবেন

* এজেন্ট ছাড়াই `pydantic_ai.direct` দিয়ে সরাসরি একটি LLM-কে একবার প্রশ্ন করা।
* চারটি ফাংশন: async/sync, stream/stream ছাড়া।
* সরাসরি API-তে টুল কলিং, কখন Agent আর কখন direct API, আর Logfire দিয়ে পর্যবেক্ষণ।

///

`direct` মডিউল LLM-এ আদেশমূলক (imperative) রিকোয়েস্ট করার নিম্ন-স্তরের মেথড দেয়, যেখানে একমাত্র বিমূর্ততা হলো ইনপুট আর আউটপুট schema-র অনুবাদ, ফলে আপনি একই API দিয়ে সব মডেল ব্যবহার করতে পারেন।

এই মেথডগুলো [`Model`][pydantic_ai.models.Model] বাস্তবায়নের চারপাশে পাতলা wrapper, যখন একটি [`Agent`][pydantic_ai.Agent]-এর পুরো সুবিধা দরকার নেই তখনকার জন্য একটি সরল interface।

/// tip | উদাহরণ দিয়ে বুঝি

`Agent` হলো একজন পূর্ণ সহকারী: সে টুল চালায়, ভুল হলে আবার চেষ্টা করে, আউটপুট যাচাই করে, একাধিক ধাপে কাজ শেষ করে। `direct` API হলো সরাসরি ফোন তুলে একটি প্রশ্ন করা আর একটি উত্তর পাওয়া — মাঝে কোনো ব্যবস্থাপক নেই। সুবিধা: পুরো নিয়ন্ত্রণ আপনার। অসুবিধা: টুল চালানো, আবার চেষ্টা ইত্যাদি সব নিজে করতে হবে।

///

নিচের ফাংশনগুলো পাওয়া যায়:

- [`model_request`][pydantic_ai.direct.model_request]: একটি মডেলে stream ছাড়া async রিকোয়েস্ট
- [`model_request_sync`][pydantic_ai.direct.model_request_sync]: একটি মডেলে stream ছাড়া synchronous রিকোয়েস্ট
- [`model_request_stream`][pydantic_ai.direct.model_request_stream]: একটি মডেলে stream করা async রিকোয়েস্ট
- [`model_request_stream_sync`][pydantic_ai.direct.model_request_stream_sync]: একটি মডেলে stream করা sync রিকোয়েস্ট

## সাধারণ উদাহরণ { #basic-example }

একটি সাধারণ রিকোয়েস্ট করতে direct API কীভাবে ব্যবহার করবেন তার একটি সহজ উদাহরণ:

```python title="direct_basic.py"
from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')]
)

print(model_response.text)
#> The capital of France is Paris.
print(model_response.usage)
#> RequestUsage(input_tokens=56, output_tokens=7)
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// info | কোডটি সহজ ভাষায়

* `model_request_sync(মডেল, বার্তার তালিকা)` — মডেলের নাম আর পাঠানোর বার্তা দিন।
* `ModelRequest.user_text_prompt('...')` — একটি সাধারণ ব্যবহারকারী-প্রশ্ন দিয়ে একটি `ModelRequest` বানানোর শর্টকাট।
* ফেরত আসে একটি `ModelResponse`: `.text`-এ উত্তরের লেখা, `.usage`-এ কত token খরচ হলো।

///

/// note | মনে রাখুন

বার্তার ইতিহাস-জুড়ে নির্দেশনা জমা হয় না। একাধিক [`ModelRequest`][pydantic_ai.messages.ModelRequest]-এ [`instructions`][pydantic_ai.messages.ModelRequest.instructions] থাকলে, direct API সবচেয়ে সাম্প্রতিকটি ব্যবহার করে।

///

## টুল কলিংসহ উন্নত উদাহরণ { #advanced-example-with-tool-calling }

ফাংশন/টুল কলিং নিয়ে কাজ করতেও direct API ব্যবহার করা যায়।

এখানেও টুলের JSON schema তৈরি করতে আমরা Pydantic ব্যবহার করতে পারি:

```python
from typing import Literal

from pydantic import BaseModel

from pydantic_ai import ModelRequest, ToolDefinition
from pydantic_ai.direct import model_request
from pydantic_ai.models import ModelRequestParameters


class Divide(BaseModel):
    """Divide two numbers."""

    numerator: float
    denominator: float
    on_inf: Literal['error', 'infinity'] = 'infinity'


async def main():
    # Make a request to the model with tool access
    model_response = await model_request(
        'openai:gpt-6-luna',
        [ModelRequest.user_text_prompt('What is 123 / 456?')],
        model_request_parameters=ModelRequestParameters(
            function_tools=[
                ToolDefinition(
                    name=Divide.__name__.lower(),
                    description=Divide.__doc__,
                    parameters_json_schema=Divide.model_json_schema(),
                )
            ],
            allow_text_output=True,  # Allow model to either use tools or respond directly
        ),
    )
    print(model_response)
    """
    ModelResponse(
        parts=[
            ToolCallPart(
                tool_name='divide',
                args={'numerator': '123', 'denominator': '456'},
                tool_call_id='pyd_ai_2e0e396768a14fe482df90a29a78dc7b',
            )
        ],
        usage=RequestUsage(input_tokens=55, output_tokens=7),
        model_name='gpt-6-luna',
        timestamp=datetime.datetime(...),
    )
    """
```

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

/// info | কোডটি সহজ ভাষায়

`Divide` Pydantic মডেলটি টুলের আর্গুমেন্টের বর্ণনা: `model_json_schema()` থেকে JSON schema আর docstring থেকে বর্ণনা নিয়ে একটি `ToolDefinition` বানানো হলো, তারপর `ModelRequestParameters(function_tools=[...])` দিয়ে মডেলকে জানানো হলো। মডেল উত্তরে একটি `ToolCallPart` ফেরত দিল (`divide`, আর্গুমেন্টসহ) — কিন্তু direct API টুলটি *চালায় না*। ভাগ করা আর ফল আবার মডেলকে পাঠানো আপনার কাজ; `Agent` এই কাজটিই নিজে করে।

///

## কখন direct API আর কখন Agent { #when-to-use-the-direct-api-vs-agent }

direct API আদর্শ যখন:

1. মডেলের সাথে আদান-প্রদানে আরও সরাসরি নিয়ন্ত্রণ দরকার
2. মডেল রিকোয়েস্টের চারপাশে নিজের আচরণ বাস্তবায়ন করতে চান
3. মডেলের আদান-প্রদানের ওপর নিজের বিমূর্ততা তৈরি করছেন

অ্যাপ্লিকেশনের বেশিরভাগ ব্যবহারের ক্ষেত্রে, উচ্চ-স্তরের [`Agent`][pydantic_ai.Agent] API আরও সুবিধাজনক interface দেয়, বাড়তি সুবিধাসহ, যেমন নেটিভ টুল চালানো, আবার চেষ্টা, গোছানো আউটপুট পার্স করা, আরও অনেক কিছু।

| চাই | ব্যবহার করুন |
| --- | --- |
| একটি প্রশ্ন, একটি উত্তর, কোনো টুল নেই | `direct` (বা `Agent`, দুটোই চলে) |
| টুল চালানো, আবার চেষ্টা, যাচাই করা আউটপুট | `Agent` |
| নিজের এজেন্ট-লুপ বা framework বানানো | `direct` |

## OpenTelemetry বা Logfire instrumentation { #opentelemetry-or-logfire-instrumentation }

[এজেন্টের][pydantic_ai.Agent] মতোই, মাত্র কয়েকটি বাড়তি লাইনে OpenTelemetry/Logfire instrumentation চালু করতে পারেন

```python title="direct_instrumented.py" hl_lines="1 6 7"
import logfire

from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

logfire.configure()
logfire.instrument_pydantic_ai()

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')],
)

print(model_response.text)
#> The capital of France is Paris.
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

প্রতিটি কলের ভিত্তিতেও OpenTelemetry চালু করতে পারেন:

```python title="direct_instrumented.py" hl_lines="1 6 12"
import logfire

from pydantic_ai import ModelRequest
from pydantic_ai.direct import model_request_sync

logfire.configure()

# Make a synchronous request to the model
model_response = model_request_sync(
    'anthropic:claude-haiku-5-5',
    [ModelRequest.user_text_prompt('What is the capital of France?')],
    instrument=True
)

print(model_response.text)
#> The capital of France is Paris.
```

আরও বিস্তারিত জানতে দেখুন [Debugging and Monitoring](logfire.md), Logfire ছাড়া সাধারণ OpenTelemetry দিয়ে কীভাবে instrument করবেন তাসহ।

/// check | সংক্ষেপে মনে রাখুন

* `from pydantic_ai.direct import model_request_sync` → `model_request_sync('provider:model', [ModelRequest.user_text_prompt('...')])`।
* চার ফাংশন: `model_request`, `model_request_sync`, `model_request_stream`, `model_request_stream_sync`।
* direct API টুল *চালায় না*, আবার চেষ্টাও করে না; সেগুলো দরকার হলে `Agent`।
* `logfire.instrument_pydantic_ai()` বা প্রতি কলে `instrument=True` দিয়ে পর্যবেক্ষণ।

///
