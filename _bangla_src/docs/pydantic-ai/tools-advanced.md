# টুলের উন্নত সুবিধা { #advanced-tool-features }

/// note | এই পেজে যা শিখবেন

* টুল থেকে ফাইল আর multi-modal বিষয়বস্তু ফেরত দেওয়া, আর `ToolReturn` দিয়ে ফল, বাড়তি বিষয়বস্তু ও metadata আলাদা করা।
* নিজের schema (`Tool.from_schema`), strict mode, আর `prepare`/`prepare_tools` দিয়ে গতিশীল টুল।
* টুল বাছাই নিয়ন্ত্রণ, tool search, timeout, retry আর ব্যর্থতা (`ModelRetry` বনাম `ToolFailed`)।
* সমান্তরাল টুল কল, আর একটি টুল থেকে রান বাতিল।

///

এই পেজ Pydantic AI-তে ফাংশন টুলের উন্নত সুবিধা নিয়ে। টুলের মৌলিক ব্যবহারের জন্য দেখুন [Function Tools](tools.md) ডকুমেন্টেশন।

## টুলের আউটপুট { #function-tool-output }

Pydantic JSON-এ serialize করতে পারে এমন যেকোনো কিছু টুল ফেরত দিতে পারে, সাথে মডেল যে ধরনের [multi-modal ইনপুট](input.md) সমর্থন করে তার ওপর নির্ভর করে অডিও, ভিডিও, ছবি বা ডকুমেন্ট বিষয়বস্তু:

```python title="function_tool_output.py"
from datetime import datetime

from pydantic import BaseModel

from pydantic_ai import Agent, DocumentUrl, ImageUrl
from pydantic_ai.models.openai import OpenAIResponsesModel


class User(BaseModel):
    name: str
    age: int


agent = Agent(model=OpenAIResponsesModel('gpt-6.1-sol'))


@agent.tool_plain
def get_current_time() -> datetime:
    return datetime.now()


@agent.tool_plain
def get_user() -> User:
    return User(name='John', age=30)


@agent.tool_plain
def get_company_logo() -> ImageUrl:
    return ImageUrl(url='https://iili.io/3Hs4FMg.png')


@agent.tool_plain
def get_document() -> DocumentUrl:
    return DocumentUrl(url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf')


result = agent.run_sync('What time is it?')
print(result.output)
#> The current time is 10:45 PM on April 17, 2025.

result = agent.run_sync('What is the user name?')
print(result.output)
#> The user's name is John.

result = agent.run_sync('What is the company name in the logo?')
print(result.output)
#> The company name in the logo is "Pydantic."

result = agent.run_sync('What is the main content of the document?')
print(result.output)
#> The document contains just the text "Dummy PDF file."
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

কিছু মডেল (যেমন Gemini) নিজস্বভাবে আধা-গোছানো ফেরত মান সমর্থন করে, আর কিছু লেখা চায় (OpenAI) কিন্তু ডেটা থেকে অর্থ বের করতে সমান দক্ষ বলে মনে হয়। একটি Python অবজেক্ট ফেরত দেওয়া হলে আর মডেল একটি স্ট্রিং চাইলে, মানটি JSON-এ serialize হবে। যে মানের JSON রূপ একটি স্ট্রিং, যেমন একটি `datetime`, `UUID` বা `Decimal`, তা JSON উদ্ধৃতিচিহ্ন ছাড়া সেই স্ট্রিং হিসেবে পাঠানো হয়, যা [বার্তার ইতিহাস সংরক্ষণ আর লোড](message-history.md#storing-and-loading-messages-to-json) করার পরেও তা-ই হিসেবে ফিরে আসে, তাই মডেল যেকোনোভাবেই একই লেখা দেখে।

### একটি ফেরত দেওয়া ফাইল কোথায় পাঠানো হয় { #tool-return-file-provenance }

একটি ফাইল টুলের ফলের ভেতরে যেতে পারে কিনা তা নির্ভর করে মডেল **আর** ফাইলের media type-এর ওপর:

- **টুলের ফলের ভেতরে**, যেখানে API আর media type দুটোই অনুমতি দেয়: ছবি আর ডকুমেন্টের জন্য Anthropic আর OpenAI Responses, এর [`GoogleModelProfile`][pydantic_ai.profiles.google.GoogleModelProfile]-এর `google_supported_mime_types_in_tool_returns`-এ তালিকাভুক্ত টাইপের জন্য Gemini 3, আর একটি মডেল পরিবার যে media kind সমর্থন করে তার জন্য Bedrock।
- **User চ্যানেলে** — যে চ্যানেলে আপনার এজেন্টের সাথে কথা বলা মানুষটি আপলোড করেন — বাকি সবকিছুর জন্য: OpenAI Chat Completions, Groq, Mistral, xAI, Hugging Face আর Gemini 2.5 ও আগেরগুলো একটি টুল ফলে শুধু লেখা নেয়, আর Gemini 3 আর Bedrock যে media type বহন করতে পারে না তার জন্য এখানে ফিরে আসে (Gemini 3-এ অডিও আর ভিডিও, বা একটি Bedrock পরিবারের সেটের বাইরের একটি kind)।
- **এর জায়গায় একটি নোট হিসেবে**, যেখানে মডেল সেই ধরনের ফাইল একেবারেই পড়তে পারে না, যেমন এর [profile](models/overview.md#inspecting-a-models-profile)-এর ফাইল-ইনপুট ফ্ল্যাগ বলে। যেমন: ফাইল ইনপুট নেই এমন Chat Completions provider-এ লেখা ছাড়া অন্য ডকুমেন্ট, যেমন Azure আর vLLM, Anthropic, OpenAI Responses, Mistral আর xAI-তে অডিও আর ভিডিও, OpenAI Chat Completions-এ ভিডিও, Bedrock-এ অডিও, Groq আর Hugging Face-এ ছবি ছাড়া যেকোনো কিছু, আর Cohere-তে যেকোনো ফাইল, সাথে Anthropic-এ PDF আর সাধারণ লেখা ছাড়া অন্য ডকুমেন্ট, আর Mistral-এ PDF আর লেখার ফরম্যাট ছাড়া অন্যগুলো।

মডেল যাতে একটি টুলের আউটপুটকে ব্যবহারকারীর সংযুক্ত কিছু হিসেবে না পড়ে, user চ্যানেলে যাওয়া একটি ফাইল যে কল থেকে এসেছে তা দিয়ে ঘেরা হয়:

```text
<tool_result tool_name="get_photo" tool_call_id="call_9cQx" file_id="d9a13f">
[the image]
</tool_result>
```

টুলের ফল নিজে ফাইলের জায়গায় `See file d9a13f.` বহন করে, আর প্রতিটি ফাইল নিজের ট্যাগ পায়, তাই একই ধাপে কয়েকটি টুল media ফেরত দিলেও মডেল প্রতিটি ফাইলকে যে কল তৈরি করেছে তার সাথে মেলাতে পারে। একটি ব্যর্থ Gemini টুল ফল একমাত্র ব্যতিক্রম: এর ফল হলো Gemini-র নিজস্ব `error` স্ট্রিং, যা কোনো ফাইল রেফারেন্স নেয় না, তাই সেখানে শুধু ট্যাগই কৃতিত্ব বহন করে। Realtime session টুলের তৈরি ফাইল একইভাবে ঘেরে। এটি প্রতিফলিত করে কীভাবে কথোপকথনের মাঝের একটি [`SystemPromptPart`][pydantic_ai.messages.SystemPromptPart] এমন একটি মডেলের জন্য `<system>...</system>` হিসেবে ঘেরা হয় যার API-তে এটি রাখার জায়গা নেই।

ঘের রিকোয়েস্ট তৈরির সময় প্রয়োগ হয় আর কখনো সংরক্ষিত হয় না: ফাইলটি আপনার বার্তার ইতিহাসে [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart]-এ থাকে, তাই নিজস্বভাবে ফাইল নেয় এমন একটি মডেলে একই ইতিহাস আবার চালালে সেগুলো কোনো ঘের ছাড়াই টুলের ফলে রাখা হয়।

যেহেতু এটি সাধারণ prompt লেখা, ঘের মডেলকে বলে বিষয়বস্তু কোথা থেকে এসেছে, প্রমাণ করে না — দেখুন [the trust boundary](message-history.md#trust-boundary-for-client-supplied-history)।

মডেল পড়তে পারে না এমন একটি ফাইল পাঠালে রিকোয়েস্ট ব্যর্থ হতো, যা মডেল একটি টুলের কাছে চাওয়া কিছুর জন্য অসামঞ্জস্যপূর্ণ, তাই এটি টুলের ফলে এর নাম বলা একটি নোট দিয়ে বদলানো হয়, আর রান চলতে থাকে:

```text
File d9a13f (audio/mpeg, 48,213 bytes) was not sent: this model cannot read audio files.
```

তখন মডেল ব্যবহারকারীকে বলতে পারে, বা আরেকটি টুল চেষ্টা করতে পারে। ঘেরের মতো, নোটটি শুধু রিকোয়েস্টে: ফাইলটি আপনার বার্তার ইতিহাসে `ToolReturnPart`-এ থাকে, আর একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] যে প্রতিটি মডেল চেষ্টা করে সেটি নিজে সিদ্ধান্ত নেয়, তাই যেটি ফাইলটি পড়তে পারে তাকে পাঠানো হয়। [File Understanding](capabilities/file-understanding.md) capability-সহ, ফাইলটি বদলে এটি পড়তে পারে এমন একটি মডেল দিয়ে লেখায় বর্ণিত হয়। একটি user prompt-এ, বা [`ToolReturn.content`](#advanced-tool-returns)-এ থাকা একটি ফাইল যেমন আছে তেমন পাঠানো হয়, আর যে মডেল এটি নিতে পারে না সে তবুও রিকোয়েস্ট ব্যর্থ করে: আপনি বা আপনার ব্যবহারকারী এটি পাঠাতে বেছেছেন।

### উন্নত টুল ফেরত { #advanced-tool-returns }

যেসব ক্ষেত্রে টুলের ফেরত মান আর মডেলে পাঠানো বিষয়বস্তু দুটোর ওপর আরও নিয়ন্ত্রণ দরকার, সেখানে [`ToolReturn`][pydantic_ai.messages.ToolReturn] ব্যবহার করতে পারেন। এটি বিশেষভাবে কাজে লাগে যখন আপনি চান:

- মডেলে পাঠানো বাড়তি বিষয়বস্তু থেকে গোছানো ফেরত মান আলাদা করতে
- স্পষ্টভাবে বিষয়বস্তু একটি আলাদা user বার্তা হিসেবে পাঠাতে (টুলের ফলে নয়)
- এমন বাড়তি metadata রাখতে যা LLM-এ পাঠানো উচিত নয়
- পরের মডেল রিকোয়েস্টের জন্য deferred টুল নাম দিয়ে প্রকাশ করতে

এখানে একটি কম্পিউটার স্বয়ংক্রিয়করণ টুলের উদাহরণ যা screenshot নেয় আর দৃশ্যমান feedback দেয়:

```python title="advanced_tool_return.py"
from pydantic_ai import Agent, BinaryContent, ToolReturn
from pydantic_ai.models.test import TestModel

agent = Agent(TestModel())

@agent.tool_plain
def click_and_capture(x: int, y: int) -> ToolReturn:
    """Click at coordinates and show before/after screenshots."""
    before_screenshot = BinaryContent(data=b'\x89PNG', media_type='image/png')
    # perform_click(x, y)
    after_screenshot = BinaryContent(data=b'\x89PNG', media_type='image/png')
    return ToolReturn(
        return_value=f'Successfully clicked at ({x}, {y})',
        content=[
            'Before:',
            before_screenshot,
            'After:',
            after_screenshot,
        ],
        metadata={
            'coordinates': {'x': x, 'y': y},
            'action_type': 'click_and_capture',
        },
    )

# The model receives the rich visual content for analysis
# while your application can access the structured return_value and metadata
result = agent.run_sync('Click on the submit button and tell me what happened')
print(result.output)
#> {"click_and_capture":"Successfully clicked at (0, 0)"}
```

- **`return_value`**: টুলের উত্তরে ব্যবহৃত আসল ফেরত মান। এটিই serialize হয়ে টুলের ফল হিসেবে মডেলে ফেরত যায়। এতে সরাসরি multimodal বিষয়বস্তু থাকতে পারে (দেখুন ওপরের [Tool Output](#function-tool-output))।
- **`tools`**: `defer_loading=True` চিহ্নিত যে টুলগুলো এই কল উপলব্ধ করেছে তাদের নাম। Pydantic AI এগুলো রেকর্ড করে একটি [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart]-এ, এই কলের [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart]-এর ঠিক পরে, একই [`ModelRequest`][pydantic_ai.messages.ModelRequest]-এ। ইতিহাস আবার শুরু হলে নামগুলো প্রকাশিত থাকে, অথচ বর্তমান টুলের সংজ্ঞা তবুও এজেন্ট থেকেই আসে।
- **`content`**: টুলের ফলের পরে একটি **আলাদা user বার্তা** হিসেবে পাঠানো বিষয়বস্তু। এটি ব্যবহার করুন যখন আপনি স্পষ্টভাবে চান বিষয়বস্তু টুলের ফলের বাইরে দেখা দিক, বা যখন গোছানো ফেরত মানকে সমৃদ্ধ বিষয়বস্তুর সাথে মেলান। এটি যেমন লিখেছেন তেমনই পাঠানো হয় — এটি আপনি ইচ্ছা করে user বিষয়বস্তু যোগ করছেন, তাই মডেল API নিতে পারেনি এমন একটি ফাইলের মতো ঘেরা হয় না (দেখুন [Where a returned file is sent](#tool-return-file-provenance))।
- **`metadata`**: ঐচ্ছিক metadata যা আপনার অ্যাপ্লিকেশন পড়তে পারে কিন্তু LLM-এ পাঠানো হয় না। লগিং, debugging বা বাড়তি প্রক্রিয়াকরণে কাজে লাগে। অন্য কিছু AI framework এই সুবিধাকে 'artifacts' বলে।

এই বিভাজন আপনাকে মডেলকে সমৃদ্ধ প্রসঙ্গ দিতে দেয়, আপনার অ্যাপ্লিকেশনের লজিকের জন্য পরিষ্কার, গোছানো ফেরত মান বজায় রেখে। টুলের ফলে নিজস্বভাবে পাঠানো উচিত এমন multimodal বিষয়বস্তুর জন্য (মডেল সমর্থন করলে), টুল ফাংশন থেকে সরাসরি ফেরত দিন বা `return_value`-এ রাখুন (দেখুন ওপরের [Tool Output](#function-tool-output))।

/// tip | উদাহরণ দিয়ে বুঝি

`ToolReturn` হলো একটি পার্সেলের তিনটি ঘর: `return_value` হলো রসিদ (মডেল টুলের উত্তর হিসেবে পায়), `content` হলো সাথে দেওয়া ছবি বা চিঠি (আলাদা বার্তা হিসেবে মডেল দেখে), আর `metadata` হলো আপনার গুদামের খাতায় লেখা নোট (মডেল কখনো দেখে না, শুধু আপনার কোড)।

///

## নিজের টুল schema { #custom-tool-schema }

আপনার এমন একটি ফাংশন থাকলে যার উপযুক্ত নথিভুক্তি নেই (যেমন খারাপ নাম, কোনো টাইপের তথ্য নেই, খারাপ docstring, \*args বা \*\*kwargs ইত্যাদির ব্যবহার), তবুও আপনি [`Tool.from_schema`][pydantic_ai.tools.Tool.from_schema] ফাংশন দিয়ে এটিকে এমন একটি টুলে পরিণত করতে পারেন যা এজেন্ট কার্যকরভাবে ব্যবহার করতে পারে। এতে আপনি সরাসরি ফাংশনের নাম, বর্ণনা, JSON schema, আর ফাংশনটি একটি `RunContext` নেয় কিনা দেন:

```python
from pydantic_ai import Agent, Tool
from pydantic_ai.models.test import TestModel


def foobar(**kwargs) -> str:
    return kwargs['a'] + kwargs['b']

tool = Tool.from_schema(
    function=foobar,
    name='sum',
    description='Sum two numbers.',
    json_schema={
        'additionalProperties': False,
        'properties': {
            'a': {'description': 'the first number', 'type': 'integer'},
            'b': {'description': 'the second number', 'type': 'integer'},
        },
        'required': ['a', 'b'],
        'type': 'object',
    },
    takes_ctx=False,
)

test_model = TestModel()
agent = Agent(test_model, tools=[tool])

result = agent.run_sync('testing...')
print(result.output)
#> {"sum":0}
```

Pydantic AI এখানে টুলের আর্গুমেন্ট যাচাই করে না; এগুলো keyword আর্গুমেন্ট হিসেবে পাঠায়।

## Strict mode { #strict-mode }

কিছু provider টুল কলের জন্য একটি *strict* mode সমর্থন করে, যা মডেলকে সীমিত করে যাতে এর টুল-কলের আর্গুমেন্ট সবসময় টুলের JSON schema মানে। মডেলকে মুক্তভাবে আর্গুমেন্ট তৈরি করতে দিয়ে পরে যাচাই না করে, provider তৈরি সীমিত করে যাতে schema-র বাইরের আর্গুমেন্ট প্রথম থেকেই তৈরি না হয়। এটি নিয়ন্ত্রণ করে `strict` ফ্ল্যাগ, প্রতিটি টুল নথিভুক্তির ব্যবস্থায় ([`@agent.tool`][pydantic_ai.agent.Agent.tool], [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain], [`Tool`][pydantic_ai.tools.Tool], [`FunctionToolset.add_function`][pydantic_ai.toolsets.function.FunctionToolset.add_function] ইত্যাদি) আর [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এ পাওয়া যায়:

```python
from pydantic import BaseModel

from pydantic_ai import Agent


class Reservation(BaseModel):
    restaurant: str
    party_size: int
    outdoor_seating: bool
    dietary_notes: list[str]


agent = Agent('openai:gpt-6.1-sol')


@agent.tool_plain(strict=True)
def book_table(reservation: Reservation) -> str:
    return f'Booked a table for {reservation.party_size} at {reservation.restaurant}.'
```

এমন গোছানো আর্গুমেন্টে strict mode সার্থক: এটি ছাড়া মডেল `party_size` একটি স্ট্রিং হিসেবে দিতে, `outdoor_seating` বাদ দিতে, বা একটি বাড়তি property বানাতে পারে — strict তৈরি একটি যাচাই-retry-এর ওপর ভরসা না করে সেগুলো আগেই বাদ দেয়।

যেহেতু strict mode নিশ্চয়তা দেয় যে আর্গুমেন্ট হুবহু schema মানে, প্রতিটি schema এর অধীনে প্রকাশ করা যায় না: কিছু provider চায় প্রতিটি property `required`-এ তালিকাভুক্ত হোক আর অবজেক্টে `additionalProperties: false` সেট থাকুক। এভাবে প্রকাশ করা যায় না এমন একটি schema ক্ষতিসহ রূপান্তরিত হতে পারে বা সেই টুলের জন্য ফ্ল্যাগ উপেক্ষিত হতে পারে — সেজন্যই `strict=True`-কে সবচেয়ে ভালো পড়া যায় provider যেখানে মানতে পারে সেখানে strict mode *বাধ্য* করার একটি অনুরোধ হিসেবে।

Pydantic AI `strict` ফ্ল্যাগকে **OpenAI**, **Anthropic**, **Google** আর **Bedrock** মডেলের জন্য একটি নিজস্ব schema-প্রয়োগ সুবিধায় অনুবাদ করে; অন্য provider এটি উপেক্ষা করে। প্রতিটি provider-এর ভেতরের সুবিধা আলাদা:

| Provider | আচরণ |
|---|---|
| OpenAI | Strict টুল সংজ্ঞা। টুলের schema strict-সামঞ্জস্যপূর্ণ হলে নিজে থেকে চালু; `strict=True` বাধ্য করে। |
| Anthropic | Strict টুল সংজ্ঞা। `strict=True` দিয়ে বেছে না নিলে বন্ধ। |
| Bedrock | সমর্থিত মডেলে strict টুল spec। `strict=True` দিয়ে বেছে না নিলে বন্ধ। |
| Google (Gemini) | Gemini-র [`VALIDATED` function-calling mode](https://ai.google.dev/gemini-api/docs/function-calling#function_calling_config), যা নিশ্চিত করে মডেল ঘোষিত schema মানে। **Gemini 2.5 আর নতুনগুলোতে এটি ডিফল্টভাবে চালু** — `VALIDATED`-এর schema-য় কোনো পরিবর্তন লাগে না, তাই এটি একটি বিনামূল্যের উন্নতি — আর আপনি `strict=False` দিয়ে বেরিয়ে আসতে পারেন। Gemini-র mode রিকোয়েস্ট-জুড়ে: `strict=False`-সহ যেকোনো ফাংশন বা আউটপুট টুল পুরো রিকোয়েস্টকে `AUTO`-তে রাখে। `VALIDATED` একটি preview Gemini সুবিধা। |

### Strictness-এর মান { #strictness-values }

`strict` ফ্ল্যাগ একটি `bool | None`:

- `True` — provider টুলের schema-র জন্য যেখানে সমর্থন করে সেখানে strict mode বাধ্য করে।
- `False` — টুলের জন্য কখনো strict mode ব্যবহার করে না। Google-এ, `strict=False`-সহ যেকোনো টুল (ফাংশন বা আউটপুট) পুরো রিকোয়েস্টকে `VALIDATED`-এর বদলে `AUTO`-তে রাখে।
- `None` (**ডিফল্ট**) — provider অনুযায়ী সিদ্ধান্ত: schema strict-সামঞ্জস্যপূর্ণ হলে OpenAI strict চালু করে; Google সমর্থিত মডেলে ডিফল্টভাবে `VALIDATED`; Anthropic আর Bedrock আপনি স্পষ্টভাবে `strict=True` দিয়ে বেছে না নিলে বন্ধ রাখে।

একসাথে অনেক টুলে strict mode চালু করতে, প্রতিটি [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এ `strict=True` সেট করতে [এজেন্ট-জুড়ে গতিশীল টুল](#prepare-tools) ব্যবহার করুন।

## গতিশীল টুল { #tool-prepare }

টুল চাইলে আরেকটি ফাংশন দিয়ে সংজ্ঞায়িত করা যায়: `prepare`, যা একটি রানের প্রতিটি ধাপে ডাকা হয়
মডেলে পাঠানো টুলের সংজ্ঞা নিজের মতো করতে, বা সেই ধাপ থেকে টুলটি পুরোপুরি বাদ দিতে।

একটি `prepare` মেথড যেকোনো টুল নথিভুক্তির ব্যবস্থার `prepare` kwarg দিয়ে নথিভুক্ত করা যায়:

- [`@agent.tool`][pydantic_ai.agent.Agent.tool] decorator
- [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain] decorator
- [`Tool`][pydantic_ai.tools.Tool] dataclass

`prepare` মেথডের টাইপ [`ToolPrepareFunc`][pydantic_ai.tools.ToolPrepareFunc]। এটি [`RunContext`][pydantic_ai.tools.RunContext] আর একটি আগে তৈরি [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] পায়। এটি সেই সংজ্ঞা অপরিবর্তিত ফেরত দিতে, [`dataclasses.replace`][dataclasses.replace] দিয়ে তৈরি একটি বদলানো কপি ফেরত দিতে, বা সেই ধাপে টুলটি বাদ দিতে `None` ফেরত দিতে পারে।

/// warning | দেওয়া সংজ্ঞা বদলান, নতুন একটি তৈরি করবেন না

একটি [`ToolDefinition`][pydantic_ai.tools.ToolDefinition] একটি নাম আর প্যারামিটার schema-র চেয়ে বেশি বহন করে: `description`, `strict`, `sequential`, `kind`, `metadata`, `timeout`, `defer_loading` আর `toolset_id` সবই আগে থেকে ভরা আসে। একটি `prepare` ফাংশনের ভেতরে একটি নতুন তৈরি করলে আপনি যে প্রতিটি ফিল্ড ফেরত দেন না তা নিঃশব্দে ডিফল্টে রিসেট হয়, তাই আপনাকে দেওয়া সংজ্ঞাটিই বদলান বা [`dataclasses.replace`][dataclasses.replace] দিয়ে কপি করুন।

`kind` হলো সেই ফিল্ড যা কামড়ায়: এভাবেই [`requires_approval=True`](deferred-tools.md#human-in-the-loop-tool-approval) এজেন্ট রানে পৌঁছায়। এটি হারানো একটি সংজ্ঞা এমন একটি টুল বর্ণনা করে যা অনুমোদনের জন্য না থেমে সাথে সাথে চলে। প্রতিটি `prepare` ফাংশন এটি রাখবে এর ওপর নির্ভর করতে না চাইলে, [`ApprovalRequiredToolset`](toolsets.md#requiring-tool-approval) টুল ডাকার সময় অনুমোদন প্রয়োগ করে, এর সংজ্ঞা কীভাবে প্রস্তুত হয়েছে তা থেকে স্বাধীনভাবে।

///

এখানে একটি সহজ `prepare` মেথড যা dependency-র মান `42` হলেই শুধু টুলটি রাখে।

আগের উদাহরণের মতো, একটি আসল মডেল না ডেকে আচরণ দেখাতে আমরা [`TestModel`][pydantic_ai.models.test.TestModel] ব্যবহার করি।

```python title="tool_only_if_42.py"

from pydantic_ai import Agent, RunContext, ToolDefinition

agent = Agent('test', deps_type=int)


async def only_if_42(
    ctx: RunContext[int], tool_def: ToolDefinition
) -> ToolDefinition | None:
    if ctx.deps == 42:
        return tool_def


@agent.tool(prepare=only_if_42)
def hitchhiker(ctx: RunContext[int], answer: str) -> str:
    return f'{ctx.deps} {answer}'


result = agent.run_sync('testing...', deps=41)
print(result.output)
#> success (no tool calls)
result = agent.run_sync('testing...', deps=42)
print(result.output)
#> {"hitchhiker":"42 a"}
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

নিচের উদাহরণ `deps`-এর মানের ভিত্তিতে `name` প্যারামিটারের বর্ণনা বদলায়।

বৈচিত্র্যের খাতিরে, আমরা এই টুলটি [`Tool`][pydantic_ai.tools.Tool] dataclass দিয়ে তৈরি করি।

```python title="customize_name.py"
from __future__ import annotations

from typing import Literal

from pydantic_ai import Agent, RunContext, Tool, ToolDefinition
from pydantic_ai.models.test import TestModel


def greet(name: str) -> str:
    return f'hello {name}'


async def prepare_greet(
    ctx: RunContext[Literal['human', 'machine']], tool_def: ToolDefinition
) -> ToolDefinition | None:
    d = f'Name of the {ctx.deps} to greet.'
    tool_def.parameters_json_schema['properties']['name']['description'] = d
    return tool_def


greet_tool = Tool(greet, prepare=prepare_greet)
test_model = TestModel()
agent = Agent(test_model, tools=[greet_tool], deps_type=Literal['human', 'machine'])

result = agent.run_sync('testing...', deps='human')
print(result.output)
#> {"greet":"hello a"}
assert test_model.last_model_request_parameters is not None
print(test_model.last_model_request_parameters.function_tools)
"""
[
    ToolDefinition(
        name='greet',
        parameters_json_schema={
            'additionalProperties': False,
            'properties': {
                'name': {'type': 'string', 'description': 'Name of the human to greet.'}
            },
            'required': ['name'],
            'type': 'object',
        },
        toolset_id='<agent>',
    )
]
"""
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

### এজেন্ট-জুড়ে গতিশীল টুল { #prepare-tools }

প্রতি-টুল `prepare` মেথড ছাড়াও, আপনি একটি এজেন্ট-জুড়ে `prepare_tools` ফাংশনও সংজ্ঞায়িত করতে পারেন। এই ফাংশন একটি রানের প্রতিটি ধাপে ডাকা হয় আর সেই ধাপে এজেন্টের কাছে উপলব্ধ সব টুল সংজ্ঞার তালিকা ছাঁকতে বা বদলাতে দেয়। একসাথে একাধিক টুল চালু বা বন্ধ করতে চাইলে, বা বর্তমান প্রসঙ্গের ভিত্তিতে বৈশ্বিক লজিক প্রয়োগ করতে চাইলে এটি বিশেষভাবে কাজে লাগে।

`prepare_tools` ফাংশনের টাইপ হওয়া উচিত [`ToolsPrepareFunc`][pydantic_ai.tools.ToolsPrepareFunc], যা [`RunContext`][pydantic_ai.tools.RunContext] আর [`ToolDefinition`][pydantic_ai.tools.ToolDefinition]-এর একটি তালিকা নেয়, আর সেই ধাপে দেখানোর টুল সংজ্ঞা ফেরত দেয়। প্রতিটি টুল যেমন আছে তেমন রাখতে `tool_defs` আর্গুমেন্ট ফেরত দিন, বা কোনো টুল না দেখাতে `[]`। প্রতি-টুল `prepare`-এর মতো, আপনাকে দেওয়া সংজ্ঞাগুলো বদলান বা নতুন তৈরি না করে [`dataclasses.replace`][dataclasses.replace] দিয়ে কপি করুন।

/// note | মনে রাখুন

`prepare_tools`-এ দেওয়া টুল সংজ্ঞার তালিকায় সাধারণ ফাংশন টুল আর এজেন্টে নথিভুক্ত যেকোনো [toolset](toolsets.md)-এর টুল দুটোই থাকে, কিন্তু [আউটপুট টুল](output.md#tool-output) নয়।

///
আউটপুট টুল বদলাতে, বদলে একটি `prepare_output_tools` ফাংশন সেট করতে পারেন।

এখানে একটি উদাহরণ যা মডেলটি একটি OpenAI মডেল হলে সব টুল strict করে:

```python title="agent_prepare_tools_customize.py"
from dataclasses import replace

from pydantic_ai import Agent, RunContext, ToolDefinition
from pydantic_ai.capabilities import PrepareTools
from pydantic_ai.models.test import TestModel


async def turn_on_strict_if_openai(
    ctx: RunContext, tool_defs: list[ToolDefinition]
) -> list[ToolDefinition]:
    if ctx.model.system == 'openai':
        return [replace(tool_def, strict=True) for tool_def in tool_defs]
    return tool_defs


test_model = TestModel()
agent = Agent(test_model, capabilities=[PrepareTools(turn_on_strict_if_openai)])


@agent.tool_plain
def echo(message: str) -> str:
    return message


agent.run_sync('testing...')
assert test_model.last_model_request_parameters is not None
assert test_model.last_model_request_parameters.function_tools[0].strict is None

# Set the system attribute of the test_model to 'openai'
test_model._system = 'openai'

agent.run_sync('testing with openai...')
assert test_model.last_model_request_parameters.function_tools[0].strict
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

আরেকটি উদাহরণ যা dependency (`ctx.deps`) `True` হলে শর্তসাপেক্ষে নাম দিয়ে টুল ছেঁকে বাদ দেয়:

```python title="agent_prepare_tools_filter_out.py"

from pydantic_ai import Agent, RunContext, Tool, ToolDefinition
from pydantic_ai.capabilities import PrepareTools


def launch_potato(target: str) -> str:
    return f'Potato launched at {target}!'


async def filter_out_tools_by_name(
    ctx: RunContext[bool], tool_defs: list[ToolDefinition]
) -> list[ToolDefinition]:
    if ctx.deps:
        return [tool_def for tool_def in tool_defs if tool_def.name != 'launch_potato']
    return tool_defs


agent = Agent(
    'test',
    tools=[Tool(launch_potato)],
    capabilities=[PrepareTools(filter_out_tools_by_name)],
    deps_type=bool,
)

result = agent.run_sync('testing...', deps=False)
print(result.output)
#> {"launch_potato":"Potato launched at a!"}
result = agent.run_sync('testing...', deps=True)
print(result.output)
#> success (no tool calls)
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

`prepare_tools` ব্যবহার করে আপনি পারেন:

- বর্তমান মডেল, dependencies বা অন্য প্রসঙ্গের ভিত্তিতে গতিশীলভাবে টুল চালু বা বন্ধ করতে
- বৈশ্বিকভাবে টুলের সংজ্ঞা বদলাতে (যেমন সব টুল strict mode-এ সেট করা, বর্ণনা বদলানো ইত্যাদি)

প্রতি-টুল `prepare` আর এজেন্ট-জুড়ে `prepare_tools` দুটোই ব্যবহার হলে, প্রতি-টুল `prepare` প্রতিটি টুলে আগে প্রয়োগ হয়, আর তারপর ফলস্বরূপ টুল সংজ্ঞার তালিকা দিয়ে `prepare_tools` ডাকা হয়।

/// tip | উদাহরণ দিয়ে বুঝি

`prepare` হলো দারোয়ান যে প্রতিটি ধাপে ঠিক করে আজ কোন ঘর (টুল) খোলা থাকবে: "অতিথি admin না হলে `delete_user` টুল দেখিও না"। মডেল যে টুল দেখে না তা ডাকতেও পারে না — এটি নির্দেশনায় "এটি ডেকো না" লেখার চেয়ে অনেক নির্ভরযোগ্য।

///

## টুল বাছাই (Tool choice) { #tool-choice }

[`ModelSettings`][pydantic_ai.settings.ModelSettings]-এর `tool_choice` সেটিং নিয়ন্ত্রণ করে একটি রিকোয়েস্টের সময় মডেল কোন টুল ব্যবহার করতে পারবে। টুল বন্ধ করতে, টুল ব্যবহার বাধ্য করতে, বা কোন টুল উপলব্ধ তা সীমিত করতে এটি কাজে লাগে।

Pydantic AI **[ফাংশন টুল](tools.md)** (যে টুল আপনি `@agent.tool`, [toolset](toolsets.md) বা [MCP](mcp/client.md) দিয়ে নথিভুক্ত করেন), আর **আউটপুট টুল** ([গোছানো আউটপুটের](output.md#tool-output) জন্য ব্যবহৃত ভেতরের টুল)-এর মধ্যে পার্থক্য করে।

### বিকল্প { #options }

| মান | বর্ণনা |
|-------|-------------|
| `'auto'` (ডিফল্ট) | মডেল ঠিক করে টুল ব্যবহার করবে কিনা। সব টুল উপলব্ধ। |
| `'none'` | ফাংশন টুল বন্ধ করে। মডেল লেখা দিয়ে উত্তর দিতে বা আউটপুট টুল ব্যবহার করতে পারে। |
| `'required'` | মডেলকে একটি ফাংশন টুল ব্যবহার করতে বাধ্য করে। আউটপুট টুল বাদ দেয়, তাই একটি [capability](#dynamic-tool-choice-via-capabilities) দিয়ে গতিশীলভাবে সেট করুন বা [সরাসরি মডেল রিকোয়েস্ট](direct.md) ব্যবহার করুন; `agent.run()`-এ স্থিরভাবে সেট করলে এরর তোলে। |
| `['tool_a', ...]` | নাম দেওয়া ফাংশন আর/বা আউটপুট টুলের একটির কল বাধ্য করে। একটি স্থির তালিকায় একটি আউটপুট টুলের নাম থাকতে হবে যাতে একটি এজেন্ট রান শেষ হতে পারে। |
| [`ToolOrOutput`][pydantic_ai.settings.ToolOrOutput]`(function_tools=['...'])` | সব আউটপুট টুল নিজে থেকে রেখে ফাংশন টুল সীমিত করে। |

একটি তালিকা কয়েকটির মধ্যে একটি নির্দিষ্ট আউটপুট টুল বাধ্য করতে পারে। প্রতিটি আউটপুট টুলকে
[`ToolOutput(..., name=...)`](output.md#tool-output) দিয়ে একটি স্থির নাম দিন আর তালিকায় এর নাম দিন:
`output_type=[ToolOutput(Fruit, name='return_fruit'), ToolOutput(Vehicle, name='return_vehicle')]`-সহ,
`tool_choice=['return_fruit']` মডেলকে একটি `Fruit` ফেরত দিতে বাধ্য করে। বিপরীতে, `'required'` আউটপুট টুল বাদ দেয়, অথচ `ToolOrOutput`
বাছা ফাংশন টুল আর সব আউটপুট টুল উপলব্ধ রাখে আর লেখা বা ছবির আউটপুটও অনুমোদন করে।

[deferred loading](#tool-search) দিয়ে লুকানো টুল `tool_choice`-এর সাথে কাজ করে: এখনো লুকানো একটি টুল
নাম দিয়ে বাধ্য করার সময় উপেক্ষিত হয়, আর একটি স্পষ্ট বাছাই এরর তোলে শুধু যখন প্রতিটি চাওয়া
টুল লুকানো। `'required'` এরর তোলে যখন প্রতিটি ফাংশন
টুল লুকানো।

একটি deferred টুল নাম দিয়ে বাধ্য করা যায় কিনা তা নির্ভর করে এর সংজ্ঞা মডেলে কীভাবে পৌঁছায় তার ওপর:

- schema deferred করে *ঘোষিত* একটি টুল, যেমন নিজস্ব tool search-সহ একটি মডেলে একটি [tool search](#tool-search) corpus সদস্য,
  উপেক্ষিত হয় না: Pydantic AI এর নাম দেওয়া একটি `tool_choice` যেমন আছে তেমন পাঠায়।
  Anthropic যেখানে বাধ্য করা সমর্থন করে সেখানে এটি গ্রহণ করে (দেখুন [Provider Support](#provider-support))।
  OpenAI Responses-এ, কিছুই টুলটি প্রকাশ না করা অবস্থায় API এটি একটি 400 দিয়ে প্রত্যাখ্যান করে, আর
  মডেলের নিজের সার্ভারে চালানো tool search এটি প্রকাশ করার পরেও। একটি [`ToolReturn.tools`][pydantic_ai.messages.ToolReturn] প্রকাশের পরে, GPT-5.6
  আর পরেরগুলো বাধ্য করা গ্রহণ করে আর আগের মডেলগুলো একই 400 ফেরত দেয়।
- OpenAI Responses-এ, প্রকাশ না হওয়া পর্যন্ত আটকে রাখা একটি টুল, যেমন একটি চাহিদামতো capability-র টুল বা
  নিজস্ব tool search ছাড়া একটি মডেলে একটি tool search corpus সদস্য, `load_capability` বা আরেকটি টুলের `ToolReturn.tools` প্রকাশ করলে
  শুধু `additional_tools` আইটেমে যায়, যেমন যায় [রানের মাঝে দেখা দেওয়া](#mid-run-tool-additions) একটি টুল। এমন একটি টুল
  প্রতিটি মডেলে `tool_choice`-এ নাম দেওয়া যায়, যদি না `openai_previous_response_id` বা `openai_conversation_id`
  সেট থাকে। GPT-5.6 আর পরেরগুলো নামটি যেমন আছে তেমন গ্রহণ করে। আগের মডেলে, Pydantic AI যে রিকোয়েস্টের `tool_choice` এর নাম দেয় সেই রিকোয়েস্টে টুলটি
  `tools`-এ ঘোষণা করে, তাই সেই একটি রিকোয়েস্ট prompt cache মিস করে। যেকোনো সেটিংয়ে, Pydantic AI টুলটি শুধু আইটেমে রাখে:
  আগের মডেলগুলো নামটি একটি 400 দিয়ে প্রত্যাখ্যান করে (`Tool choice '<name>' not found in 'tools' parameter.`),
  আর একটি সংরক্ষিত উত্তর আইটেমটি ধরলে GPT-5.6-ও তা-ই করে।

### উদাহরণ { #example }

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.settings import ToolOrOutput

agent = Agent(TestModel())


@agent.tool_plain
def get_weather(city: str) -> str:
    return f'Sunny in {city}'


@agent.tool_plain
def get_time(city: str) -> str:
    return f'12:00 in {city}'


# Pass tool_choice via model_settings
result = agent.run_sync('Hello', model_settings={'tool_choice': 'none'})

# Use ToolOrOutput to restrict to specific function tools while allowing output
result = agent.run_sync(
    'Hello', model_settings={'tool_choice': ToolOrOutput(function_tools=['get_weather'])}
)
```

### Capability দিয়ে গতিশীল tool choice { #dynamic-tool-choice-via-capabilities }

`tool_choice='required'` আউটপুট টুল বাদ দেয়, তাই এটি *স্থিরভাবে* সেট করলে প্রতিটি ধাপে একটি ফাংশন টুল কল বাধ্য হতো আর এজেন্ট একটি চূড়ান্ত উত্তর তৈরি করতে পারত না। কোনো আউটপুট টুলের নাম না দেওয়া একটি স্থির তালিকার একই সমস্যা, এমনকি সাধারণ লেখার আউটপুট অনুমোদিত থাকলেও, কারণ তালিকাটি প্রতিটি ধাপে একটি নাম দেওয়া টুল কল চায়। স্থির ভিত্তিতে এই মানের জন্য `agent.run()` একটি `UserError` তোলে ([`Agent.run`][pydantic_ai.agent.AbstractAgent.run]-এর `model_settings` আর্গুমেন্ট, এজেন্টের নিজের `model_settings`, বা ভেতরের মডেলের ডিফল্ট)। অন্তত একটি আউটপুট টুলের নাম দেওয়া একটি স্থির তালিকা গৃহীত হয়।

`tool_choice` *প্রতি ধাপে* বদলাতে — যেমন, প্রথম ধাপে একটি নির্দিষ্ট টুল বাধ্য করে তারপর মডেলকে ঠিক করতে দিতে — একটি capability-র [`get_model_settings`][pydantic_ai.capabilities.AbstractCapability.get_model_settings] থেকে একটি callable ফেরত দিন। callable-টি `ctx.messages` আর `ctx.run_step`-এ পূর্ণ প্রবেশসহ একটি [`RunContext`][pydantic_ai.tools.RunContext] পায়, তাই এটি রানে আগে কী ঘটেছে তা দেখে মানিয়ে নিতে পারে।

```python title="force_first_call.py"
from pydantic_ai import Agent, ModelSettings, RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ModelRequest, ToolReturnPart


class RequireFirstCall(AbstractCapability):
    """Force `tool_name` to be called successfully before anything else."""

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name

    def get_model_settings(self):
        def settings(ctx: RunContext) -> ModelSettings:
            called = any(
                isinstance(part, ToolReturnPart) and part.tool_name == self.tool_name
                for message in ctx.messages
                if isinstance(message, ModelRequest)
                for part in message.parts
            )
            if called:
                return ModelSettings()
            return ModelSettings(tool_choice=[self.tool_name])

        return settings


agent = Agent('openai:gpt-6.1-sol', capabilities=[RequireFirstCall('get_weather')])


@agent.tool_plain
def get_weather(city: str) -> str:
    return f'Sunny in {city}'
```

যেহেতু capability-র দেওয়া সেটিং প্রতি ধাপে নির্ধারিত হয়, callable-এর ফেরত দেওয়া `tool_choice` ধাপে ধাপে বদলাবে বলে বিশ্বাস করা হয় আর ভিত্তির validator তা প্রত্যাখ্যান করে না। একটি এজেন্ট loop ছাড়া একটি একক মডেল রিকোয়েস্টের জন্য, বদলে [`pydantic_ai.direct.model_request`][pydantic_ai.direct.model_request] ব্যবহার করুন।

### Provider সমর্থন { #provider-support }

সব provider `'auto'` আর `'none'` সমর্থন করে। অন্য বিকল্পের মূল পার্থক্য:

| Provider | `'required'` | নির্দিষ্ট টুল | নোট |
|----------|:------------:|:--------------:|-------|
| OpenAI | ✓ | ✓ | পূর্ণ সমর্থন |
| Anthropic | ⚠️ | ⚠️ | extended thinking-এ, বা Claude Opus 5.5, Sonnet 5.5, Fable 5.1 আর Mythos 5.1-এ সমর্থিত নয়; adaptive thinking বাধ্য করা গ্রহণ করে কিন্তু thinking ছাড়া উত্তর দেয় |
| Google | ✓ | ✓ | |
| Bedrock | ✓ | শুধু একটি | একাধিক টুল 'any' mode-এ ফিরে যায়। Converse-এর কোনো `'none'` mode নেই, তাই `'none'` টুলগুলো বাদ দেয়। ইতিহাসে একটি টুল কল থাকলে, Converse সেগুলো চায়, তাই সেগুলো থাকে: Claude তার নিজস্ব `'none'` পায়, অথচ অন্য মডেলকে সেগুলো ডাকা থেকে আটকানো হয় না ([#10435](https://github.com/pydantic/pydantic-ai/issues/10435))। thinking-এর সামঞ্জস্যের জন্য দেখুন [thinking and structured output](models/bedrock.md#thinking-and-structured-output) |
| Groq/HuggingFace | ✓ | শুধু একটি | একাধিক টুল 'required' mode-এ ফিরে যায় |
| Mistral | ✓ | ✓ | `'required'`-কে `'any'` mode-এ ম্যাপ করে |
| Cohere | ✓ | ✓ | `'required'`-কে `'REQUIRED'`-এ ম্যাপ করে; একটি নাম দেওয়া উপসেট টুলের array ছেঁটে প্রয়োগ হয় |
| xAI | ✓ | ✓ | |

adaptive thinking-এ, Claude একটি বাধ্য টুল বাছাইয়ের উত্তর দেয় শুধু টুল কল দিয়ে আর কোনো thinking ছাড়া, তাই Pydantic AI
শুধু আপনি স্পষ্টভাবে চাওয়া একটি পাঠায়: নিজে অনুমান করা বাধ্য করা রিকোয়েস্ট thinking করার সময় `'auto'`-তে ফিরে যায়।

`OpenAIChatModel`-এর ওপর তৈরি মডেল ক্লাস — Cerebras, Crusoe, GitHub Copilot, Ollama, OpenRouter, Snowflake, Z.AI আর Bedrock Mantle Chat — model profile বাধ্য করা সীমিত না করলে OpenAI সারি অনুসরণ করে। Ollama `tool_choice` উপেক্ষা করে, আর OpenRouter-এর [Anthropic মডেলের জন্য আলাদা নিয়ম](models/openrouter.md#forced-tool-choice) আছে।

একটি মডেলকে একটি টুল ডাকতে বাধ্য করা যায় কিনা তা মডেলের একটি বৈশিষ্ট্য, এর [profile](models/overview.md)-এ [`supports_forced_tool_choice`][pydantic_ai.profiles.ModelProfile.supports_forced_tool_choice] আর [`supports_forced_tool_choice_with_thinking`][pydantic_ai.profiles.ModelProfile.supports_forced_tool_choice_with_thinking] দিয়ে সেট, তাই এটি মডেলটি দেওয়া প্রতিটি provider-এ প্রযোজ্য: Claude Opus 5.5 OpenRouter-এ বাধ্য করা প্রত্যাখ্যান করে ঠিক যেমন Anthropic API-তে করে। যেখানে বাধ্য করা উপলব্ধ নয়, একটি স্পষ্ট `'required'` বা টুলের তালিকা একটি [`UserError`][pydantic_ai.exceptions.UserError] তোলে, অথচ Pydantic AI নিজে অনুমান করা বাধ্য করা, যেমন একটি [আউটপুট টুল](output.md#tool-output) থেকে, `'auto'`-তে ফিরে যায়। OpenRouter-এ, একটি Anthropic মডেলে স্পষ্টভাবে চাওয়া thinking বাধ্য করা অনুপলব্ধ করে, কারণ অন্যথায় OpenRouter নিঃশব্দে reasoning বাদ দিত। শুধু ডিফল্টভাবে চালু thinking সেই নিষেধাজ্ঞা যোগ করে না; মডেলের নিজের বাধ্য-করার সীমা তবুও প্রযোজ্য।

### Prompt caching-এর ওপর প্রভাব { #tool-choice-caching }

`tool_choice` দিয়ে উপলব্ধ টুলের সেট সীমিত করলে provider-এর prompt cache অবৈধ হতে পারে, কারণ বেশিরভাগ provider API পুরো টুল array-এর ওপর cache করে। Pydantic AI দুইভাবে টুলের সেট সীমিত করে:

- **API-স্তরের ছাঁকা** (cache রক্ষা করে): পুরো টুল array পাঠানো হয় আর provider-কে শুধু একটি উপসেট অনুমোদন করতে বলা হয়। ব্যবহার করে OpenAI Responses (`allowed_tools`), Google (`allowed_function_names`), আর একটি একক টুল বাধ্য করার সময় Bedrock আর Mistral।
- **Client-পক্ষের ছাঁকা** (cache ভাঙে): রিকোয়েস্টের আগে টুল array ছাঁটা হয়। ব্যবহার হয় যখন provider API-র দেওয়া ক্ষেত্রের জন্য কোনো নিজস্ব ফিল্টার নেই।

নিচের টেবিল সেই ক্ষেত্রগুলো ঢাকে যেখানে Pydantic AI-কে client-পক্ষে টুল array বদলাতে হয় আর তাই cache ভাঙে:

| Provider | cache-ভাঙা ক্ষেত্র |
|----------|---------------------|
| Anthropic | `tool_choice` একাধিক টুলের একটি তালিকা, বা extended thinking-সহ বা বাধ্য করা সমর্থন করে না এমন একটি মডেলে একটি একক টুল |
| OpenAI Chat | `tool_choice` একাধিক টুলের একটি তালিকা, বা বাধ্য করা সমর্থন করে না এমন একটি মডেলে একটি একক টুল |
| Bedrock | `tool_choice` একাধিক টুলের একটি তালিকা, বা extended thinking-সহ বা বাধ্য করা সমর্থন করে না এমন একটি মডেলে একটি একক টুল, বা ইতিহাসে কোনো টুল কল না থাকা অবস্থায় `'none'` |
| Groq / HuggingFace | `tool_choice` একাধিক টুলের একটি তালিকা |
| Mistral | `tool_choice` একাধিক টুলের একটি তালিকা — API শুধু একটি একক নাম দেওয়া টুল বাধ্য করতে পারে |
| Cohere | `tool_choice` একটি তালিকা (যেকোনো আকার) — API নির্দিষ্ট টুলের নাম নেয় না |
| xAI | `tool_choice` একাধিক টুলের একটি তালিকা, বা বাধ্য করা সমর্থন করে না এমন একটি মডেলে একটি একক টুল |
| OpenAI Responses | GPT-5.6-এর আগের মডেলে, শুধু `additional_tools` আইটেম ঘোষণা করে এমন একটি টুলের নাম দেওয়া একটি `tool_choice` (তালিকা বা `ToolOrOutput`), যেমন `load_capability`-এর প্রকাশ করা একটি বা [রানের মাঝে দেখা দেওয়া](#mid-run-tool-additions) একটি: সেই রিকোয়েস্ট এটি `tools`-এ ঘোষণা করে, যদি না `openai_previous_response_id` বা `openai_conversation_id` সেট থাকে, সেক্ষেত্রে API রিকোয়েস্ট প্রত্যাখ্যান করে (দেখুন [Tool Choice](#tool-choice))। `allowed_tools` বাকি প্রতিটি ক্ষেত্র নিজস্বভাবে সামলায় |
| Google | কখনো না — `allowed_function_names` সব ক্ষেত্র নিজস্বভাবে সামলায় |

cache hit রক্ষা করা গুরুত্বপূর্ণ হলে, "কখনো না" চিহ্নিত provider/ক্ষেত্র পছন্দ করুন, বা একটি সীমিত তালিকার বদলে `ToolOrOutput` ব্যবহার করুন (যা পুরো সেট রাখে)।

## টুল চালানো, retry আর ব্যর্থতা { #tool-retries }

একটি টুল চালানোর সময়, এর আর্গুমেন্ট (LLM-এর দেওয়া) প্রথমে Pydantic দিয়ে ফাংশনের signature-এর বিপরীতে যাচাই হয় (ঐচ্ছিক [validation context](output.md#validation-context)-সহ)। যাচাই ব্যর্থ হলে (যেমন ভুল টাইপ বা অনুপস্থিত বাধ্যতামূলক আর্গুমেন্টের কারণে), একটি `ValidationError` ওঠে, আর framework নিজে থেকে কলটির উত্তর দেয় যাচাইয়ের বিবরণ আর `outcome='retried'`-সহ একটি [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] দিয়ে। সেই ফল provider-এর এরর চ্যানেলে LLM-এ ফেরত পাঠানো হয়, এররটি জানিয়ে আর প্যারামিটার শুধরে টুল কল আবার চেষ্টা করতে দিয়ে।

একটি টুলের নিজের লজিক একটি স্বাভাবিক ফল তৈরি করতে না পারলে, মডেল পরে কী করুক চান তার ভিত্তিতে exception বাছুন:

- মডেলের শুধরানো আর্গুমেন্ট বা ভিন্ন পদ্ধতিতে টুল কল আবার চেষ্টা করা উচিত হলে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলুন।
- টুলের retry বাজেট খরচ না করে টুল কলটি মডেলকে একটি ব্যর্থ ফল হিসেবে জানানো উচিত হলে [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] তুলুন।

অন্য যেকোনো exception এজেন্ট রান থেকে বেরিয়ে যায় আর মডেলে ফেরত পাঠানো হয় না।

/// info | এক নজরে

| পরিস্থিতি | তুলুন | মডেল কী করে |
| --- | --- | --- |
| ভুল আর্গুমেন্ট, ঠিক করে আবার চেষ্টা করলে কাজ হবে | `ModelRetry('কারণ')` | শুধরে আবার ডাকে (retry বাজেট খরচ) |
| কাজটি নিশ্চিতভাবে ব্যর্থ, আবার চেষ্টা বৃথা | `ToolFailed('কারণ')` | ব্যর্থতা দেখে অন্যভাবে এগোয় (বাজেট খরচ নয়) |
| আপনার কোডের বাগ বা অপ্রত্যাশিত সমস্যা | অন্য যেকোনো exception | রান থেমে যায় |

///

### একটি টুল retry চাওয়া { #requesting-a-tool-retry }

`ModelRetry` তুললে কলটির উত্তর হয় exception-এর বার্তা আর `outcome='retried'`-সহ একটি [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] দিয়ে। সেই ফল LLM-এ ফেরত পাঠানো হয় যাতে এটি টুল কল শুধরাতে, আরেকটি টুল বাছতে, বা ভিন্ন পদ্ধতি চেষ্টা করতে পারে।

```python
from pydantic_ai import ModelRetry


def my_flaky_tool(query: str) -> str:
    if query == 'bad':
        # Tell the LLM the query was bad and it should try again
        raise ModelRetry("The query 'bad' is not allowed. Please provide a different query.")
    # ... process query ...
    return 'Success!'
```

`ValidationError` আর `ModelRetry` দুটোই কনফিগার করা retry সীমা মানে — প্রতি-টুল [`Tool(max_retries=N)`][pydantic_ai.tools.Tool] (বা `@agent.tool(retries=N)`) দিয়ে, প্রতি-toolset [`FunctionToolset(max_retries=N)`][pydantic_ai.toolsets.FunctionToolset] দিয়ে, বা এজেন্ট-জুড়ে [`Agent(retries={'tools': N})`][pydantic_ai.agent.Agent.__init__] দিয়ে সেট, সেই অগ্রাধিকারের ক্রমে প্রয়োগ। এজেন্ট-জুড়ে ডিফল্ট প্রতি রানে [`agent.run(retries={'tools': N})`][pydantic_ai.agent.Agent.run] দিয়েও override করা যায় (আর `run_sync`/`run_stream`/`iter`, বা একগুচ্ছ রানের জন্য [`agent.override()`][pydantic_ai.agent.Agent.override] দিয়ে); একটি প্রতি-রান মান অগ্রাধিকার-শৃঙ্খলের তলায় এজেন্ট-জুড়ে ডিফল্টের জায়গা নেয়, তাই স্পষ্ট প্রতি-টুল আর প্রতি-toolset সীমা তবুও জেতে। এই চলার-সময়ের কল-জায়গায় একটি সাধারণ `int` দুটো বাজেটই override করে (তৈরির সাথে মিলিয়ে) — শুধু একটি বদলাতে `retries={'tools': N}` বা `retries={'output': N}`-এর মতো একটি dict দিন।

টুল retry **প্রতি টুলে** ট্র্যাক হয়: প্রতিটি ফাংশন টুলের নিজের গণক, রানজুড়ে ভাগ করা কোনো বৈশ্বিক 'টুল কল' বাজেট নেই। একটি টুল `ModelRetry` তুললে বা এর আর্গুমেন্ট যাচাই ব্যর্থ হলে, শুধু সেই টুলের গণক এগোয়। একটি টুল ফাংশনের ভেতরে, [`ctx.max_retries`][pydantic_ai.tools.RunContext.max_retries] সেই টুলের প্রয়োগ-সীমা দেখায় আর [`ctx.retry`][pydantic_ai.tools.RunContext.retry] সেই টুলের নিজের গণক। টুলের [`prepare`](#tool-prepare) ফাংশন একই গণক পড়ে, এর toolset [prefixed](toolsets.md#prefixing-tool-names) বা [renamed](toolsets.md#renaming-tools) হলেও, যদি না `prepare` নিজে টুলের নাম বদলায় (তখন এটি টুলের অন্যথায় যে নাম হতো তার গণক পড়ে) বা শৃঙ্খলের আরেকটি wrapper-ও টুলের নাম বদলায়। একটি টুল তার গণক শেষ করলে, রান [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] তোলে এই বার্তাসহ: `'Tool {name!r} exceeded max retries count of {N}. Consider raising the retry limit, or see the docs on tool retries: https://pydantic.dev/docs/ai/tools-toolsets/tools-advanced/#tool-retries'`। কোনো প্রতি-toolset মান সেট না থাকলে ব্যবহারকারীর দেওয়া toolset এজেন্ট-জুড়ে টুল-retry ডিফল্ট — বা তার প্রতি-রান override — তাদের ডিফল্ট হিসেবে উত্তরাধিকারসূত্রে পায়।

### কোন retry সীমা জেতে { #which-retry-limit-wins }

দুটি স্বাধীন বাজেট — **টুল** বাজেট (প্রতি ফাংশন/আউটপুট টুল) আর **আউটপুট** বাজেট (আউটপুট যাচাই) — প্রতিটি একই স্তরভিত্তিক অগ্রাধিকার দিয়ে নির্ধারিত হয়। যে প্রথম স্তর একটি মান সেট করে সেটি জেতে; সেট না করা স্তর পরেরটিতে চলে যায়:

| অগ্রাধিকার (সর্বোচ্চ আগে) | কীভাবে সেট করবেন | যে বাজেট সেট করে |
|----------------------------|---------------|----------------|
| 1. প্রতি-টুল সীমা | `@agent.tool(retries=N)` / [`Tool(max_retries=N)`][pydantic_ai.tools.Tool]; একটি আউটপুট টুলের জন্য [`ToolOutput(max_retries=N)`][pydantic_ai.output.ToolOutput.max_retries] | সেই একটি টুল |
| 2. প্রতি-toolset সীমা | [`FunctionToolset(max_retries=N)`][pydantic_ai.toolsets.FunctionToolset] বা [`MCPToolset(max_retries=N)`][pydantic_ai.mcp.MCPToolset] | সেই toolset-এর টুল |
| 3. Override ব্লক | [`agent.override(retries=...)`][pydantic_ai.agent.Agent.override] | টুল আর/বা আউটপুট |
| 4. প্রতি-রান আর্গুমেন্ট | [`agent.run(retries=...)`][pydantic_ai.agent.Agent.run] (আর `run_sync`/`run_stream`/`iter`) | টুল আর/বা আউটপুট |
| 5. প্রতি-রান spec | `agent.run(spec={'retries': ...})` | টুল আর/বা আউটপুট |
| 6. এজেন্ট-জুড়ে ডিফল্ট | [`Agent(retries=...)`][pydantic_ai.agent.Agent.__init__] | টুল আর/বা আউটপুট |
| 7. Built-in ডিফল্ট | — | `1` |

স্তর 3–6-এ, একটি সাধারণ `int` **দুটো** বাজেটই সেই মানে সেট করে, অথচ একটি [`AgentRetries`][pydantic_ai.agent.AgentRetries] dict শুধু তার নাম দেওয়া key সেট করে (`{'tools': N}`, `{'output': N}`, বা দুটোই)। স্তর 3–5 এজেন্ট-জুড়ে ডিফল্ট (স্তর 6) override করে কিন্তু কখনো একটি আরও নির্দিষ্ট প্রতি-টুল (স্তর 1) বা প্রতি-toolset (স্তর 2) সীমা নয়।

### একটি ব্যর্থ টুল ফল জানানো { #tool-failed }

প্রতিটি টুল ব্যর্থতা একটি সংশোধনের অনুরোধ নয়। কল সম্পূর্ণ কিন্তু অসফল হলে — রিসোর্সটি নেই, কাজটি সমর্থিত নয়, upstream সার্ভিস একটি নিশ্চিত এরর ফেরত দিয়েছে — আপনি সাধারণত চান মডেল ব্যর্থ ফলটি *দেখুক* আর পরে কী করবে তা ঠিক করুক। এর জন্য `ToolFailed` তুলুন:

```python
from pathlib import Path

from pydantic_ai import ToolFailed


def read_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.is_file():
        raise ToolFailed(f'File not found: {path}')
    return file_path.read_text(encoding='utf-8')
```

exception-এর বার্তা বার্তার ইতিহাসে `outcome='failed'`-সহ একটি [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart] হিসেবে রেকর্ড হয়। যেখানে মডেল API-র টুল ফলের জন্য একটি নিজস্ব এরর বা failed-status ফিল্ড আছে, Pydantic AI সেটি ব্যবহার করে। নিজস্ব এরর চ্যানেল নেই এমন API-র জন্য, মডেলের কাছে দৃশ্যমান বিষয়বস্তু JSON-এ `{"error": ...}` হিসেবে ঘেরা হয়, তাই ব্যর্থতা তবুও স্পষ্ট থাকে। ব্যর্থ ফল Pydantic AI বার্তার ইতিহাসে রক্ষিত থাকে; সেই ইতিহাস আসা-যাওয়া করলে প্রোটোকল adapter-এর নিজস্ব বাহক লাগতে পারে, যেমন বর্ণিত আছে [AG-UI](ui/ag-ui.md#preserving-failed-tool-outcomes)-এর জন্য। কলটি telemetry-তে একটি এরর হিসেবে trace হয়।

`ModelRetry`-এর মতো নয়, `ToolFailed` প্রতি-টুল retry বাজেট খরচ **করে না**; বারবার ব্যর্থতা সীমিত করা রান স্তরে [`UsageLimits`][pydantic_ai.usage.UsageLimits]-এর কাজ — বিশেষ করে [`request_limit`][pydantic_ai.usage.UsageLimits.request_limit], কারণ [`tool_calls_limit`][pydantic_ai.usage.UsageLimits.tool_calls_limit] শুধু সফল টুল কল গোনে।

সাধারণ নিয়ম: মডেল সংশোধনসহ আবার চেষ্টা করুক চাইলে `ModelRetry` তুলুন; কল শেষ আর ফলটি একটি ব্যর্থতা হলে `ToolFailed` তুলুন। MCP সার্ভারের টুল এররের জন্য, একই বাছাই পাওয়া যায় [`tool_error_behavior`](mcp/client.md#tool-errors) কনফিগারেশন হিসেবে।

আপনি টুল যাচাই আর চালানোর hook থেকেও `ModelRetry` বা `ToolFailed` তুলতে পারেন। প্রতিটি টুলে `try`/`except` পুনরাবৃত্তি না করে third-party exception রূপান্তরে এটি কাজে লাগে; দেখুন [Error hooks](hooks.md#error-hooks) আর [Tool execution hooks](hooks.md#tool-execution-hooks)।

`ToolFailed` সামলানো হয় ফাংশন টুল, তাদের `args_validator`, আর টুল যাচাই বা চালানোর hook-এ। [আউটপুট ফাংশন](output.md#output-functions) আর [আউটপুট validator](output.md#output-validator-functions) মডেলের আবার চেষ্টা করা উচিত হলে `ModelRetry` ব্যবহার করে; সেখানে, `ToolFailed` একটি সাধারণ exception যা রান বাতিল করে, যদি না একটি output-process error hook এটি থেকে উদ্ধার করে।

### টুল timeout { #tool-timeout }

টুল যাতে অনির্দিষ্টকাল না চলে তা ঠেকাতে টুল চালানোর জন্য একটি timeout সেট করতে পারেন। একটি টুল তার timeout ছাড়ালে, তা একটি retry-যোগ্য ব্যর্থতা হিসেবে ধরা হয় আর কলটির উত্তর হয় একটি retried টুল ফল দিয়ে (retry সীমায় গোনা হয়)।

```python
import asyncio

from pydantic_ai import Agent

# Set a default timeout for the agent's own tools
agent = Agent('test', tool_timeout=30)


@agent.tool_plain
async def slow_tool() -> str:
    """This tool will use the agent's default timeout (30 seconds)."""
    await asyncio.sleep(10)
    return 'Done'


@agent.tool_plain(timeout=5)
async def fast_tool() -> str:
    """This tool has its own timeout (5 seconds) that overrides the agent default."""
    await asyncio.sleep(1)
    return 'Done'
```

- **এজেন্ট-স্তরের timeout**: [`Agent`][pydantic_ai.agent.Agent]-এ নথিভুক্ত টুলে একটি ডিফল্ট timeout প্রয়োগ করতে এতে `tool_timeout` সেট করুন।
- **প্রতি-টুল timeout**: [`@agent.tool`][pydantic_ai.agent.Agent.tool], [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain] বা [`Tool`][pydantic_ai.tools.Tool] dataclass দিয়ে নির্দিষ্ট টুলে `timeout` সেট করুন। এটি এজেন্ট-স্তরের ডিফল্ট override করে।

একটি timeout ঘটলে, টুলটি একটি retry-যোগ্য ব্যর্থতা হিসেবে ধরা হয় আর মডেল `"Timed out after {timeout} seconds."` বার্তাসহ একটি retried টুল ফল পায়। এটি যাচাইয়ের এরর বা স্পষ্ট [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] exception-এর মতোই টুলের retry সীমায় গোনা হয়।

দুটো সেটিংই প্রয়োগ করে [`FunctionToolset`][pydantic_ai.toolsets.FunctionToolset], যা এজেন্টের নিজের টুলের পেছনে থাকে। একটি [MCP সার্ভার](mcp/client.md), একটি [বাইরের toolset](deferred-tools.md), বা একটি নিজের [`AbstractToolset`][pydantic_ai.toolsets.AbstractToolset]-এর দেওয়া টুল এগুলো পড়ে না — বদলে সেই সময়সীমা সার্ভার বা transport স্তরে বাঁধুন। টুল timeout একটি রানের অন্য সময়সীমার সাথে কীভাবে সম্পর্কিত তা দেখুন [Timeouts](timeouts.md#bounding-how-long-a-step-takes)-এ।

### একটি টুল থেকে রান বাতিল { #cancelling-the-run-from-a-tool }

একটি টুল [`RunContext.cancel()`][pydantic_ai.tools.RunContext.cancel] ডেকে পুরো রান বাতিল করতে পারে -- যেমন যখন এটি আবিষ্কার করে যে আর কাজ অর্থহীন, বা একটি টুল `RunContext` ধরে থাকার সময় আপনার অ্যাপ্লিকেশনে একটি থামার সংকেত পৌঁছায়। রানের বাইরে থেকে, যেকোনো রান মেথডে একটি [`CancellationToken`][pydantic_ai.CancellationToken] দিন। রান চলমান যা-ই থাকুক তার বাতিল চায় আর caller-এর কাছে [`RunCancelled`][pydantic_ai.exceptions.RunCancelled] তোলে। [সমান্তরালে](#parallel-tool-calls-concurrency) চলা async টুল task বাতিল আর খালি হয়, কিন্তু Python জোর করে একটি sync টুলের worker thread থামাতে পারে না; বাতিল worker-এর জন্য অপেক্ষা করতে পারে বা পেছনে শেষ করতে দিতে পারে। যেকোনোভাবেই, এর শেষ ফল বাদ পড়ে অথচ যেকোনো পার্শ্বপ্রতিক্রিয়া থেকে যায়। ইতিমধ্যে শেষ হওয়া টুল কল তাদের ফল বার্তার ইতিহাসে রাখে, আর কখনো ফল তৈরি না করা একটি টুল কল সেই ইতিহাস আবার ব্যবহারের সময় নিজে থেকে মেরামত হয়। দুই বাতিল-পথই রানের একই প্রসেসে থাকা চায়, তাই এগুলো একটি Temporal activity-র মতো একটি [durable execution](durable_execution/overview.md) serialization সীমানা পেরোয় না।

রানের বাইরে থেকে বাতিল আর বাতিল রানের অবস্থায় পৌঁছানোসহ পুরো চিত্রের জন্য দেখুন [Cancelling a Run](agent.md#cancelling-a-run)।

### নিজের args validator { #args-validator }

`args_validator` প্যারামিটার দিয়ে আপনি নিজের যাচাই সংজ্ঞায়িত করতে পারেন যা Pydantic schema যাচাইয়ের পরে কিন্তু টুল চলার আগে চলে। ব্যবসায়িক লজিকের যাচাই, ফিল্ড-জুড়ে যাচাই, বা deferred টুলের জন্য [মানুষের অনুমোদন](deferred-tools.md) চাওয়ার আগে আর্গুমেন্ট যাচাইয়ে এটি কাজে লাগে।

validator তার প্রথম আর্গুমেন্ট হিসেবে [`RunContext`][pydantic_ai.tools.RunContext] পায়, তারপর টুল ফাংশনের মতো একই প্যারামিটার। সফল হলে `None` ফেরত দিন, মডেলকে আর্গুমেন্ট শুধরে আবার চেষ্টা করতে বলতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলুন, আবার চেষ্টার বদলে মডেলের মানিয়ে নেওয়া উচিত এমন একটি চূড়ান্ত ব্যর্থতা জানাতে [`ToolFailed`][pydantic_ai.exceptions.ToolFailed] তুলুন, বা [কলটি defer করতে](deferred-tools.md) [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] / [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] তুলুন (নিচে দেখুন)।

```python title="args_validator_approval.py"
from pydantic_ai import Agent, DeferredToolRequests, ModelRetry, RunContext

agent = Agent('test', deps_type=int, output_type=[str, DeferredToolRequests])


def validate_sum_limit(ctx: RunContext[int], x: int, y: int) -> None:
    """Validate that the sum doesn't exceed the limit from deps."""
    if x + y > ctx.deps:
        raise ModelRetry(f'Sum of x and y must not exceed {ctx.deps}')


# Validation runs *before* approval is requested, so the model can
# fix bad args without bothering the user.
@agent.tool(requires_approval=True, args_validator=validate_sum_limit)
def add_numbers(ctx: RunContext[int], x: int, y: int) -> int:
    """Add two numbers (sum must not exceed the configured limit)."""
    return x + y


result = agent.run_sync('add 5 and 3', deps=100)
assert isinstance(result.output, DeferredToolRequests)
# The validated args are ready for the user to approve
print(result.output.approvals[0].args)
#> {'x': 0, 'y': 0}
```

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

schema যাচাই ব্যর্থ হলে, বা একটি `args_validator` `ModelRetry` তুললে, এরর বার্তা একটি retried টুল ফল হিসেবে LLM-এ ফেরত পাঠানো হয় আর টুলের `retries` সেটিং মানে। একটি `args_validator` `ToolFailed` তুললে, মডেল বদলে একটি ব্যর্থ টুল ফল পায় যাতে আবার চেষ্টা না করে মানিয়ে নেওয়া উচিত, আর retry বাজেট অছোঁয়া থাকে। [deferred টুলের](deferred-tools.md) জন্য, যাচাই deferral-এর সময় চলে — শুধু বৈধ আর্গুমেন্টসহ টুল কল defer হয়।

একটি validator নিজেই কলটি defer করতে পারে, ঠিক যেমন টুল ফাংশন পারে — আর সেই সিদ্ধান্ত নেওয়ার জন্য এটিই ভালো জায়গা, কারণ একজন মানুষকে অনুমোদন করতে বলার আগেই খারাপ আর্গুমেন্ট প্রত্যাখ্যাত হয়। `ApprovalRequired` বা `CallDeferred` তোলা একটি validator retry বাজেটও খরচ করে না: আর্গুমেন্ট বৈধ ছিল, তাই deferral একটি ব্যর্থতা নয়, একটি ইচ্ছাকৃত সিদ্ধান্ত। টুল ফাংশন চলে না, আর কলটি রানের অন্য [deferred টুল কলের](deferred-tools.md) সাথে যোগ দেয়: আপনার একটি থাকলে [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] handler এটি সেখানেই মীমাংসা করে, বা রানের `DeferredToolRequests` আউটপুটে দেখা দেয়। কলটি [অনুমোদিত](deferred-tools.md#human-in-the-loop-tool-approval) হলে, validator আবার চলে — এবার [`RunContext.tool_call_approved`][pydantic_ai.tools.RunContext.tool_call_approved] `True` সেট করা অবস্থায় — আর টুল চলে।

এখানে, একটি অসম্ভব পরিমাণ সরাসরি প্রত্যাখ্যাত হয় অথচ একটি বড় পরিমাণ একজন মানুষের সামনে রাখা হয়:

```python title="args_validator_conditional_approval.py"
from pydantic_ai import (
    Agent,
    ApprovalRequired,
    DeferredToolRequests,
    ModelMessage,
    ModelResponse,
    ModelRetry,
    RunContext,
    TextPart,
    ToolCallPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

agent = Agent(deps_type=int, output_type=[str, DeferredToolRequests])


def validate_transfer(ctx: RunContext[int], amount: int) -> None:
    if amount > ctx.deps:
        raise ModelRetry(f'Amount must not exceed {ctx.deps}')  # (1)!
    if amount > 100 and not ctx.tool_call_approved:
        raise ApprovalRequired()  # (2)!


@agent.tool(args_validator=validate_transfer)
def transfer_funds(ctx: RunContext[int], amount: int) -> str:
    return f'Transferred {amount}'


def call_transfer(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    if len(messages) == 1:
        return ModelResponse(parts=[ToolCallPart('transfer_funds', {'amount': 500})])
    return ModelResponse(parts=[TextPart('done')])


result = agent.run_sync('transfer 500', deps=1000, model=FunctionModel(call_transfer))
assert isinstance(result.output, DeferredToolRequests)
print(result.output.approvals[0].args)
#> {'amount': 500}
```

1. মডেল নিজেই একটি অসম্ভব পরিমাণ ঠিক করতে পারে, কোনো মানুষ কলটি না দেখেই।
2. শুধু যাচাই পেরোনো কলই একজন মানুষের সামনে রাখা হয়।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// tip | উদাহরণ দিয়ে বুঝি

ব্যাংকের টাকা পাঠানো ভাবুন: `-50` টাকা পাঠাতে বলা অর্থহীন — validator সরাসরি `ModelRetry` দিয়ে মডেলকে ঠিক করতে বলে, ম্যানেজারকে বিরক্ত না করে। কিন্তু ১০ লাখ টাকা বৈধ হলেও বড় — validator `ApprovalRequired` তুলে ম্যানেজারের অনুমোদন চায়। ম্যানেজার শুধু অর্থবহ অনুরোধগুলোই দেখেন।

///

`args_validator` প্যারামিটার পাওয়া যায় [`@agent.tool`][pydantic_ai.agent.Agent.tool], [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain], [`Tool`][pydantic_ai.tools.Tool], [`Tool.from_schema`][pydantic_ai.tools.Tool.from_schema] আর [`FunctionToolset`][pydantic_ai.toolsets.function.FunctionToolset]-এ। validator sync বা async ফাংশন হতে পারে।

[Durable execution](durable_execution/overview.md)-এর অধীনে, engine যেখানেই সেই toolset মোড়ায় সেখানে একটি `args_validator`-সহ একটি টুল একটি নিজস্ব যাচাই activity, step বা task পায়। validator I/O করতে পারে আর কলটি retry, fail বা defer করতে পারে। `args_validator` ছাড়া টুল কোনো বাড়তি durable একক নির্ধারণ করে না।

যাচাইয়ের ফল দেখানো হয় [`FunctionToolCallEvent`][pydantic_ai.messages.FunctionToolCallEvent]-এর `args_valid` ফিল্ড দিয়ে। এটি সব যাচাই প্রতিফলিত করে — schema যাচাই আর নিজের `args_validator` যাচাই দুটোই (কনফিগার থাকলে): `True` মানে সব যাচাই পেরিয়েছে, `False` মানে যাচাই ব্যর্থ, আর `None` মানে যাচাই করা হয়নি (যেমন `'early'` end strategy-র কারণে বাদ পড়া টুল কল, বা চালানো ছাড়া মীমাংসা হওয়া deferred টুল কল)।

### সমান্তরাল টুল কল আর সমান্তরালতা { #parallel-tool-calls-concurrency }

একটি মডেল এক উত্তরে একাধিক টুল কল ফেরত দিলে, Pydantic AI `asyncio.create_task` দিয়ে সেগুলো একসাথে নির্ধারণ করে, মডেল যে ক্রমে দিয়েছে সেই ক্রমে চালিয়ে।

একটি নির্দিষ্ট টুলকে অন্যগুলোর সাথে একসাথে চলা থেকে থামাতে, এটিকে `sequential=True` চিহ্নিত করুন — তখন এটি একটি বাধা হিসেবে কাজ করে: মডেল এর আগে যে টুলগুলো দিয়েছে সেগুলো আগে শেষ হয়, এটি একা চলে, আর এর পরে দেওয়া টুলগুলো এটি শেষ হলেই শুরু হয়।

```python title="sequential_tool.py"
from pydantic_ai import Agent, ModelMessage, ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel

agent = Agent()

calls: list[str] = []


@agent.tool_plain
def fetch_record(record_id: int) -> str:
    calls.append(f'fetch_record({record_id})')
    return f'record-{record_id}'


@agent.tool_plain(sequential=True)
def write_to_database(record: str) -> str:
    calls.append(f'write_to_database({record!r})')
    return 'written'


def call_tools(messages: list[ModelMessage], info: AgentInfo) -> ModelResponse:
    if len(messages) == 1:  # first request: ask for both tools at once
        return ModelResponse(
            parts=[
                ToolCallPart('fetch_record', {'record_id': 1}),
                ToolCallPart('write_to_database', {'record': 'data'}),
            ]
        )
    return ModelResponse(parts=[TextPart('done')])


result = agent.run_sync('store the record', model=FunctionModel(call_tools))
print(result.output)
#> done
# `write_to_database` waited for `fetch_record` to finish before running.
print(calls)
#> ['fetch_record(1)', "write_to_database('data')"]
```

যেকোনো ফাংশন টুল নথিভুক্তির সময় [`sequential`][pydantic_ai.tools.ToolDefinition.sequential] ফ্ল্যাগ দিতে পারেন, আর [আউটপুট টুলের](output.md#tool-output) জন্য একই বাধা পাওয়া যায় [`ToolOutput(sequential=True)`][pydantic_ai.output.ToolOutput] দিয়ে (দেখুন [Controlling output tool parallelism](output.md#controlling-output-tool-parallelism))। কোন টুল ডাকা হয়েছে তা নির্বিশেষে একটি পুরো রানের টুল একটির পর একটি চালাতে, রানটি [`with agent.parallel_tool_call_execution_mode('sequential')`][pydantic_ai.agent.AbstractAgent.parallel_tool_call_execution_mode] context manager-এ মুড়ুন, বা [মডেল সেটিংয়ে][pydantic_ai.settings.ModelSettings] `parallel_tool_calls=False` সেট করুন।

Async ফাংশন event loop-এ চলে, অথচ sync ফাংশন thread-এ পাঠানো হয়। সেরা কর্মক্ষমতার জন্য, _সবসময়_ একটি async ফাংশন ব্যবহার করুন, _যদি না_ আপনি blocking I/O করছেন (আর বদলে একটি non-blocking লাইব্রেরি ব্যবহারের উপায় নেই) বা CPU-নির্ভর কাজ করছেন (যেমন `numpy` বা `scikit-learn`-এর কাজ), যাতে সাধারণ ফাংশন অকারণে thread-এ না যায়।

/// note | Sync টুল একটি আলাদা thread-এ চলে

যেহেতু একটি sync ফাংশন একটি worker thread-এ চলে, এটি একটি [`contextvars.ContextVar`][contextvars.ContextVar]-এ যে মান সেট করে তা ফাংশনের বাইরে দেখা যায় না, আর `asyncio.get_running_loop()`-এর মতো asyncio API এরর তোলে, কারণ worker thread-এ কোনো event loop নেই। context variable পড়া তবুও কাজ করে, কিন্তু লেখার সীমাবদ্ধতা সেই লাইব্রেরিতেও প্রযোজ্য যারা ভেতরে এগুলো ব্যবহার করে, যেমন tracing আর logging integration। আপনার টুলের এগুলোর কোনোটি লাগলে, এটিকে async করুন। একই কথা এজেন্ট আপনার হয়ে চালানো যেকোনো sync ফাংশনে প্রযোজ্য, [hooks](hooks.md), system prompt ফাংশন, আউটপুট ফাংশন আর history processor-সহ।

///

#### দীর্ঘ-চলা সার্ভারের জন্য thread executor { #thread-executor-for-long-running-servers }

ডিফল্টভাবে, sync ফাংশন [`anyio.to_thread.run_sync`][anyio.to_thread.run_sync] দিয়ে thread-এ পাঠানো হয়, যা চাহিদামতো ক্ষণস্থায়ী thread তৈরি করে। দীর্ঘ-চলা সার্ভারে (যেমন FastAPI), টানা ট্রাফিকের মধ্যে এই thread-গুলো জমে মেমরি বাড়াতে পারে।

thread-এর জীবনচক্র নিয়ন্ত্রণ করতে, [`UseThreadExecutor`][pydantic_ai.capabilities.UseThreadExecutor] capability (প্রতি-এজেন্ট) বা [`Agent.using_thread_executor()`][pydantic_ai.agent.AbstractAgent.using_thread_executor] context manager (বৈশ্বিক) দিয়ে একটি সীমিত [`ThreadPoolExecutor`][concurrent.futures.ThreadPoolExecutor] দিন:

```python
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from pydantic_ai import Agent
from pydantic_ai.capabilities import UseThreadExecutor

# Per-agent: pass as a capability
executor = ThreadPoolExecutor(max_workers=16, thread_name_prefix='agent-worker')
agent = Agent('openai:gpt-6.1-sol', capabilities=[UseThreadExecutor(executor)])

# Global: wrap your server lifespan
@asynccontextmanager
async def lifespan(app):
    executor = ThreadPoolExecutor(max_workers=16)
    with Agent.using_thread_executor(executor):
        yield
    executor.shutdown(wait=True)
```

/// note | টুল চালানো সীমিত করা

[`UsageLimits(tool_calls_limit=...)`](agent.md#usage-limits) দিয়ে একটি রানের মধ্যে টুল চালানো সীমিত করতে পারেন। গণক বাড়ে শুধু একটি সফল টুল কলের পরে। আউটপুট টুল ([গোছানো আউটপুটের](output.md) জন্য ব্যবহৃত) `tool_calls` মেট্রিকে গোনা হয় না।

///

#### আউটপুট টুল কল { #output-tool-calls }

একটি মডেল যখন অন্য টুলের সাথে সমান্তরালে একটি চূড়ান্ত ফল তৈরি করে — একটি [আউটপুট টুল](output.md#tool-output) কল, বা গোছানো [native](output.md#native-output)/[prompted](output.md#prompted-output) বা [ছবি](output.md#image-output) আউটপুট — এজেন্টের [`end_strategy`][pydantic_ai.agent.Agent.end_strategy] প্যারামিটার নিয়ন্ত্রণ করে এই টুল কলগুলো কীভাবে চলবে।
ডিফল্ট `'graceful'` কৌশল নিশ্চিত করে একটি চূড়ান্ত ফল পাওয়ার পরেও সব ফাংশন টুল চলে, বাকি আউটপুট টুল বাদ দিয়ে। `'exhaustive'` কৌশল আরও এগিয়ে সব আউটপুট টুলও চালায়। দুটোই কাজে লাগে যখন টুলের পার্শ্বপ্রতিক্রিয়া আছে (যেমন লগিং, নোটিফিকেশন পাঠানো বা মেট্রিক হালনাগাদ) যা সবসময় চলা উচিত।

ফাংশন টুল, আউটপুট টুল আর টুল-নয় আউটপুটের সাথে `end_strategy` কীভাবে কাজ করে তার আরও তথ্যের জন্য দেখুন [Tool calls alongside a final result](output.md#parallel-output-tool-calls)।

## Tool search { #tool-search }

অনেক টুলসহ এজেন্ট (যেমন কয়েক ডজন endpoint দেখানো [MCP সার্ভার](mcp/client.md)) কোনো কাজ হওয়ার আগেই টুলের সংজ্ঞায় অনেক input token খরচ করতে পারে, আর প্রায় 30–50টি উপলব্ধ টুলের পরে টুল বাছাইয়ের নির্ভুলতা লক্ষণীয়ভাবে কমে। deferred loading-এর জন্য টুল চিহ্নিত করলে সেগুলো মডেলের প্রাথমিক প্রসঙ্গ থেকে লুকানো থাকে; দরকার হলে মডেল keyword দিয়ে লুকানো টুল খুঁজে পায়।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বিশাল যন্ত্রপাতির দোকানে সব যন্ত্র কাউন্টারে সাজিয়ে রাখলে খদ্দের দিশেহারা হয়ে ভুল যন্ত্র নেয়। বদলে কাউন্টারে শুধু সবচেয়ে বেশি চলা কয়েকটি রাখুন, আর বাকিগুলোর জন্য একটি ক্যাটালগ ("search")। খদ্দের দরকার হলে ক্যাটালগে খুঁজে নেয়। Tool search ঠিক এটাই — token বাঁচে আর বাছাই নির্ভুল হয়।

///

workflow *বান্ডেলের* জন্য — নির্দেশনা, টুল, মডেল সেটিং আর hook যা একসাথে চলে — দেখুন [on-demand capabilities](capabilities/on-demand.md), যা একই ব্যবস্থার ওপর তৈরি কিন্তু একক-টুল স্তরে নয়, বান্ডেল স্তরে প্রকাশ করে।

এটি ব্যবহার করুন যখন:

* এজেন্ট প্রায় 10+ টুল বা প্রায় 10k token-এর বেশি টুল সংজ্ঞা দেখায়
* টুল আলাদা ক্ষেত্র ঢাকে (যেমন একাধিক MCP সার্ভার) আর প্রতি রিকোয়েস্টে শুধু একটি উপসেট প্রাসঙ্গিক
* toolset বাড়ছে আর আপনি বাড়তি জায়গা চান

বাদ দিন যখন আপনার একটি ছোট, সক্রিয় toolset আছে যার প্রতিটি টুল বেশিরভাগ দফায় ব্যবহার হয় — সবকিছু defer করলে কোনো লাভ ছাড়াই শুধু একটি খোঁজার যাওয়া-আসা যোগ হতো। সাধারণ নিয়ম হিসেবে, আপনার হাতে গোনা সবচেয়ে বেশি ব্যবহৃত টুলগুলো আগে থেকে লোড রাখুন; বাকি দীর্ঘ লেজ defer করুন।

যোগ দিতে, নির্দিষ্ট [`Tool`][pydantic_ai.tools.Tool] / [`@agent.tool`][pydantic_ai.agent.Agent.tool] / [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain] নথিভুক্তিতে `defer_loading=True` সেট করুন, বা একটি পুরো toolset-এ (যার মধ্যে [`MCPToolset`][pydantic_ai.mcp.MCPToolset]) [`.defer_loading()`][pydantic_ai.toolsets.AbstractToolset.defer_loading] ব্যবহার করুন — নির্দিষ্টগুলো লুকাতে টুলের নামের একটি তালিকা দিন, বা সব লুকাতে `None`।

deferred টুল থাকলে, সার্চ সামলায় নিজে থেকে যোগ হওয়া [`ToolSearch`][pydantic_ai.capabilities.ToolSearch] capability:

* সমর্থনকারী মডেলে **নিজস্ব provider সার্চ** (Anthropic Sonnet 4.5+, Opus 4.5+, Haiku 4.5+ [BM25/regex](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) দিয়ে; GPT-5.4 nano ছাড়া GPT-5.4+-এ OpenAI Responses)। deferred টুল তারে `defer_loading`-সহ provider-এ পাঠানো হয় আর provider তাদের দৃশ্যমানতা সামলায়।
* [`ToolSearch(strategy=...)`][pydantic_ai.capabilities.ToolSearch] দিয়ে **নিজের callable** — ব্যবহারকারীর দেওয়া একটি সার্চ ফাংশন। আমাদের দিকে চলে, কিন্তু সমর্থিত হলে provider-এর client-চালিত নিজস্ব পথে পাঠানো হয় (Anthropic `tool_reference` ব্লক, OpenAI `execution='client'`), যাতে মডেল একটি সাধারণ ফাংশন টুলের বদলে একটি tool-search কল দেখে।
* বাকি প্রতিটি মডেলে **লোকাল বিকল্প**: একটি `search_tools` ফাংশন টুল টুলের নাম আর বর্ণনার সাথে keyword মেলায়।

Pydantic AI যখনই উপলব্ধ তখনই নিজস্ব সার্চ পছন্দ করে, কারণ খোঁজার আদান-প্রদান শুধু জুড়ে জুড়ে ঘটে (একটি `tool_search_call` + `tool_search_output` জোড়া) অথচ প্রতিটি টুলের লেখা `defer_loading` মান স্থির থাকে, তাই দফা-জুড়ে prompt caching রক্ষিত থাকে। লোকাল বিকল্পে, প্রকাশিত টুল তাদের স্থির সংজ্ঞা থেকে আলাদাভাবে ট্র্যাক হয় আর আবিষ্কারের পরেই শুধু পাঠানো হয়।

প্রতিটি সার্চযোগ্য deferred টুল পুরো রানজুড়ে সার্চ corpus-এ থাকে, মডেল আগেই আবিষ্কার করেছে এমন টুলসহ। একটি সার্চ পুনরাবৃত্তি নিরাপদ আর মডেলকে একটি টুলের আগের আবিষ্কার আর দৃশ্যমান না থাকার পরে তা ফিরে পেতে দেয়, যেমন [compaction](capabilities/compaction.md)-এর পরে। ডিফল্ট keyword কৌশলে, অনাবিষ্কৃত মিল সবসময় আগে থেকে উপলব্ধগুলোর আগে র‍্যাঙ্ক পায়, তাই `max_results` তালিকা ছাঁটলে, একটি আগে থেকে উপলব্ধ টুল কখনো একটি অনাবিষ্কৃত মিলকে সরায় না — শুধু খালি জায়গা ভরে।

deferred সংজ্ঞা জড়ো করা বা মোড়ানো toolset `get_tools`-এর ভেতরে [`ctx.is_tool_available(tool_def)`][pydantic_ai.tools.RunContext.is_tool_available] দিয়ে দৃশ্যমানতা পরীক্ষা করতে পারে। একটি সংজ্ঞা উপলব্ধ যখন এটি deferred নয় বা এর নাম ইতিহাসে প্রকাশিত হয়েছে। toolset যে সংজ্ঞাটি ধরে আছে তা দিন; নামের রূপটি বর্তমান নির্ধারিত [`ctx.tools`][pydantic_ai.tools.RunContext.tools] snapshot-এ একই পরীক্ষা প্রয়োগ করে আর মডেল-রিকোয়েস্ট hook আর টুল চালানোর জন্য উদ্দিষ্ট।

একটি বান্ডেল হিসেবে আটকানো টুল ঢাকে [on-demand capabilities](capabilities/on-demand.md); এগুলো সার্চযোগ্য corpus-এর অংশ নয়।

প্রতিটি রেকর্ড করা প্রকাশ এজেন্টের event stream-এ একটি [`ToolAvailabilityDeltaEvent`][pydantic_ai.messages.ToolAvailabilityDeltaEvent] হিসেবে আর সংশ্লিষ্ট স্থায়ী Vercel AI data chunk বা AG-UI activity snapshot হিসেবেও দেখা দেয়।

Provider adapter প্রতিটি দৃশ্যমানতা-পরিবর্তন তাদের সমর্থিত ইতিহাস-ভিত্তিক প্রকাশ-ব্যবস্থায় প্রক্ষেপ করে। Anthropic প্রতিটি প্রকাশিত সংজ্ঞা `defer_loading=True`-সহ `tools`-এ ঘোষণা করে — শুধু-capability রানে শুরুতেই (কোনো সার্চ পথ সেগুলো দেখাতে পারে না), মিশ্র রানে প্রকাশের সময় জুড়ে, যা ততক্ষণ capability-র সংজ্ঞা আটকে রাখে — আর একই রিকোয়েস্টে একটি নিজস্ব `tool_addition` ব্লক থেকে এর রেফারেন্স দেয়। OpenAI Responses একটি প্রকাশিত সংজ্ঞা একটি জোড়া `additional_tools` ইনপুট আইটেমে বহন করে: কখনো ঘোষিত হয়নি এমন একটি টুল শুধু আইটেমে যায় (GPT-5.6-এর আগের মডেলে, যে রিকোয়েস্টের `tool_choice` এর নাম দেয় সেটি বদলে এটি `tools`-এ ঘোষণা করে আর cache মিস করে, অথচ `openai_previous_response_id` বা `openai_conversation_id` সেট থাকলে এটি একটি 400 পায়; দেখুন [Tool Choice](#tool-choice)), অথচ একটি deferred `tools` এন্ট্রি হিসেবে আগেই ঘোষিত একটি টুল সেই এন্ট্রি রাখে আর আইটেমটি এটি প্রকাশ করে। অন্য মডেল নতুন উপলব্ধ টুলের ঘোষণা দেয় যখন তাদের schema আগেই দৃশ্যমান, বা একটি তৈরি tool-search আদান-প্রদান পায় যখন এর ফলকে একটি আটকানো schema প্রকাশ করতে হয়।

মডেল যাতে টুল ভালোভাবে খুঁজে পায়, সেগুলোকে সামঞ্জস্যপূর্ণ উপসর্গসহ (`github_*`, `slack_*`, `mortgage_*`) বর্ণনামূলক নাম দিন আর একজন ব্যবহারকারী যে keyword দিয়ে খুঁজতে পারেন তা টুলের বর্ণনায় রাখুন। একটি সার্চ একসাথে হাতে গোনা কয়েকটি মিল ফেরত দেয়, তাই মডেল পুনরাবৃত্তি করতে পারে (সার্চ → আবিষ্কার → কল → আবার সার্চ) — নির্দেশনা একে ঠেলে দিতে পারে: "Search by topic when you don't see a tool you need."

```python title="tool_search.py"
from pydantic_ai import Agent

agent = Agent('anthropic:claude-sonnet-5-5')


@agent.tool_plain(defer_loading=True)
def mortgage_calculator(principal: float, rate: float, years: int) -> str:
    """Calculate monthly mortgage payment for a home loan."""
    monthly_rate = rate / 100 / 12
    n_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    return f'${payment:.2f}/month'
```

MCP সার্ভারের জন্য, সব টুল সার্চের পেছনে লুকাতে [`.defer_loading()`][pydantic_ai.toolsets.AbstractToolset.defer_loading] ব্যবহার করুন:

```python title="tool_search_mcp.py"
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset

mcp = MCPToolset('http://localhost:8000/mcp')
agent = Agent('anthropic:claude-sonnet-5-5', toolsets=[mcp.defer_loading()])
```

### `ToolSearch` কনফিগার করা { #configuring-toolsearch }

কৌশল নিয়ন্ত্রণ করতে বা একটি নিজের সার্চ ফাংশন দিতে একটি স্পষ্ট [`ToolSearch`][pydantic_ai.capabilities.ToolSearch] capability দিন:

```python title="tool_search_custom.py"
from collections.abc import Sequence

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import ToolSearch
from pydantic_ai.tools import ToolDefinition


def fuzzy_search(
    ctx: RunContext, queries: Sequence[str], tools: Sequence[ToolDefinition]
) -> list[str]:
    """Match tools whose name or description contains any query word."""
    needles = [n for q in queries for n in q.lower().split()]
    return [
        t.name
        for t in tools
        if any(n in t.name.lower() or n in (t.description or '').lower() for n in needles)
    ]


agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[ToolSearch(strategy=fuzzy_search)])


@agent.tool_plain(defer_loading=True)
def mortgage_calculator(principal: float, rate: float, years: int) -> str:
    """Calculate monthly mortgage payment for a home loan."""
    monthly_rate = rate / 100 / 12
    n_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    return f'${payment:.2f}/month'
```

উপলব্ধ কৌশলের মান:

| `strategy` | অ্যালগরিদম | আচরণ |
|---|---|---|
| `None` (ডিফল্ট) | উপলব্ধ থাকলে provider-এর নিজস্ব অ্যালগরিদম, অন্যথায় লোকাল keyword মেলানো | Sonnet 4.5+/Opus 4.5+/Haiku 4.5+-এ Anthropic-এর নিজস্ব BM25 ([পুরনো Bedrock client](models/anthropic.md#aws-bedrock)-এ নিজস্ব regex), GPT-5.4 nano ছাড়া GPT-5.4+-এ OpenAI-এর সার্ভারে চালানো `tool_search`, অন্যত্র লোকাল keyword মেলানো। |
| `'keywords'` | লোকাল keyword-overlap | keyword অ্যালগরিদম আমাদের দিকে চলে, কিন্তু তারের আকার মানিয়ে নেয়: সমর্থিত হলে client-চালিত নিজস্ব (Anthropic, OpenAI) যাতে prompt cache গরম থাকে, অন্যত্র সাধারণ `search_tools` ফাংশন টুল। |
| `'bm25'` / `'regex'` | Anthropic নিজস্ব | Anthropic সার্ভারে চালায়। অন্য provider-এ (OpenAI, Google ইত্যাদি) নিঃশব্দে একটি ভিন্ন অ্যালগরিদম বসানোর বদলে রিকোয়েস্ট ব্যর্থ হয়। |
| Callable `(ctx, queries, tools) -> names` | ব্যবহারকারী-সংজ্ঞায়িত | `'keywords'`-এর মতো একই চালানোর-mode সামলানো: সমর্থনকারী provider-এ client-চালিত নিজস্ব, অন্যত্র লোকাল `search_tools` ফাংশন টুল। |

চালানোর mode (সার্ভারে চালানো, client-চালিত নিজস্ব, বা লোকাল বিকল্প) বাছা অ্যালগরিদম আর বর্তমান provider থেকে নিজে থেকে বের করা হয় — ব্যবহারকারী সরাসরি এটি বাছেন না। যখনই উপলব্ধ তখনই নিজস্ব চালানো পছন্দ করা হয়, কারণ এটি খোঁজার দফা-জুড়ে মডেলের দেখা টুলের তালিকা স্থির রাখে, যা Anthropic আর OpenAI prompt caching রক্ষা করে।

নিজস্বভাবে tool search সমর্থন করা একটি provider-এ লোকাল `keywords` অ্যালগরিদম বাধ্য করতে, `ToolSearchTool` বাদ দিতে [`ModelProfile.supported_native_tools`][pydantic_ai.profiles.ModelProfile.supported_native_tools] override করুন — তখন capability লোকাল `search_tools` ফাংশন টুলে নেমে যায়।

/// note | Provider-জুড়ে ইতিহাস আবার চালানো

একটি দফা এক provider-এ আর পরেরটি আরেকটিতে চলতে পারে (যেমন [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] দিয়ে বা রানের মাঝে `model=` বদলে)। বদলের সময় আবিষ্কৃত-টুলের অবস্থা রক্ষিত থাকে:

* একটি নিজস্ব-সমর্থনকারী provider-এ (Anthropic, OpenAI) render হওয়া লোকাল-আকারের `search_tools` ইতিহাস provider-এর নিজস্ব tool-search তারে উন্নীত হয়, যাতে মডেলকে আবার সার্চ করতে বাধ্য না করে আবিষ্কৃত টুলের schema `defer_loading=True` থেকে মুক্ত হয়।
* আরেকটি provider-এ render হওয়া নিজস্ব-আকারের `tool_search` ইতিহাস — লক্ষ্যের নিজের নিজস্ব tool search থাকুক বা না থাকুক — আগে provider-নিরপেক্ষ `search_tools` আদান-প্রদানে অনুবাদিত হয়, তারপর লক্ষ্যের সমর্থিত আকারে render হয়। একটি provider-এর নিজের নিজস্ব ইতিহাস তার হুবহু আবার-চালানোর আকার রাখে। ব্যতিক্রম পুরনো [`AsyncAnthropicBedrock` client](models/anthropic.md#aws-bedrock), যেখানে রেকর্ড করা `bm25` কল `regex` হিসেবে আবার চলে, যদি না রান `ToolSearch(strategy='bm25')` ব্যবহার করে।

///

#### টুল-উপলব্ধতার ইতিহাসের বহনযোগ্যতা { #tool-availability-history-portability }

সংরক্ষিত ইতিহাস একটি টুল ডাকার যোগ্য হওয়াকে বর্ণনা করতে পারে হয় একটি মডেল-চালিত সার্চ, নয়তো একটি
অ্যাপ্লিকেশন-চালিত উপলব্ধতা-পরিবর্তন হিসেবে। একটি ভিন্ন মডেলে ইতিহাস আবার চালালে Pydantic AI সেই পার্থক্য রক্ষা করে:

| সংরক্ষিত রূপ | `tool_addition_mode='by_reference'`-সহ Anthropic | `tool_addition_mode=None`-সহ Anthropic | নিজস্ব সার্চ আর `tool_addition_mode='with_definitions'`-সহ OpenAI Responses | নিজস্ব সার্চ ছাড়া প্রথম-পক্ষের OpenAI Responses, `tool_addition_mode='with_definitions'` | `tool_addition_mode=None`-সহ OpenAI-সামঞ্জস্যপূর্ণ Responses | Gemini (`tool_addition_mode=None`) | OpenAI Chat Completions (`tool_addition_mode=None`) |
|---|---|---|---|---|---|---|---|
| লোকাল `search_tools` কল আর ফল | নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | লোকাল সার্চ + `additional_tools` | লোকাল সার্চ | লোকাল সার্চ | লোকাল সার্চ |
| Anthropic নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | লোকাল সার্চ + `additional_tools` | লোকাল সার্চ | লোকাল সার্চ | লোকাল সার্চ |
| OpenAI নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | লোকাল সার্চ + `additional_tools` | লোকাল সার্চ | লোকাল সার্চ | লোকাল সার্চ |
| [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart] | `tool_addition` | নিজস্ব সার্চ | `additional_tools` | `additional_tools` | ঘোষণা বা লোকাল সার্চ | ঘোষণা | ঘোষণা |
| `metadata['discovered_tools']`-সহ `search_tools` ফল | নিজস্ব সার্চ | নিজস্ব সার্চ | নিজস্ব সার্চ | লোকাল সার্চ | লোকাল সার্চ | লোকাল সার্চ | লোকাল সার্চ |

এখানে, **নিজস্ব সার্চ** মানে একটি জোড়া provider-নিজস্ব সার্চ কল আর ফল আর সাথে নিজস্ব সার্চ
টুল। সার্চযোগ্য deferred টুল deferred corpus-এ থাকে। **লোকাল
সার্চ** মানে একটি জোড়া `search_tools` ফাংশন কল আর ফল আর সাথে লোকাল সার্চ টুল; প্রকাশিত
টুল একটি আগে-লোড ফাংশন টুল হিসেবে থাকে — একটি `with_definitions` লক্ষ্য ছাড়া, যেখানে একটি
গোছানো সার্চ ফল বাড়তি হিসেবে একটি `additional_tools` আইটেমে চড়ে আর প্রকাশিত সংজ্ঞা একটি `tools` এন্ট্রি না নিয়ে
সেখানে যায় (একটি সাধারণ-লেখার পুরনো ফল, শেষ সারি, বহন করার মতো কোনো গোছানো আবিষ্কার রাখে না, তাই
এটি সাধারণ লোকাল সার্চ থাকে)। একটি শুধু-capability corpus-এর জন্য, একটি provider-নিজস্ব
উপলব্ধতা-পরিবর্তনে একটি সার্চ আদান-প্রদান বা একটি সার্চ টুল কোনোটিই থাকে না। একটি মিশ্র corpus-এ,
যে টুলগুলো সার্চযোগ্য থাকে তাদের জন্য সার্চ টুল তারে থাকে; একটি Anthropic capability টুল তার `tool_addition` পাঠানোর সময়
একটি deferred সংজ্ঞা হিসেবে জোড়া হয়।

একটি আসল সার্চ মডেল কী করেছে তার প্রমাণ: এটি একটি query বেছে মিল পেয়েছে। সেই আদান-প্রদানকে
`tool_addition` বা `additional_tools` হিসেবে নতুন করে লিখলে ভুলভাবে মডেল-চালিত আবিষ্কারকে
অ্যাপ্লিকেশন-চালিত নিয়ন্ত্রণে পরিণত করা হতো। তাই provider-নিজস্ব উপলব্ধতা-পরিবর্তন ব্যবহার হয় শুধু
[`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart]-এর জন্য। সেই নিয়ন্ত্রণের মৌলিক উপাদান নেই এমন লক্ষ্যে,
schema আগেই দৃশ্যমান থাকলে কথোপকথনের মাঝের একটি system নির্দেশনা ঘোষণা করে
`The following tool(s) are now available: {names}`। একটি সম্পূর্ণ
লোকাল সার্চ আদান-প্রদান তৈরি করা হয় শুধু যখন এর ফলকে এমন একটি schema প্রকাশ করতে হয় যা আসলে
আটকানো, যাতে টুলটি `defer_loading`-এর পেছনে আটকে না থাকে।

/// note | টুল আবিষ্কার আর বার্তার ইতিহাস

আবিষ্কৃত টুল টাইপ করা বার্তা-অংশে ট্র্যাক হয় — সার্চ কল/ফল জোড়া আর [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart]। একটি [history processor](message-history.md#processing-message-history) সেই প্রমাণ সরালে, পরের রিকোয়েস্টে টুলগুলো আবার লুকিয়ে যায়; রক্ষার চুক্তির জন্য দেখুন [Processing Message History](message-history.md#processing-message-history)।

///

আরও বিস্তারিত জানতে দেখুন [`ToolDefinition.defer_loading`][pydantic_ai.tools.ToolDefinition.defer_loading] আর [Deferred Loading](toolsets.md#deferred-loading)।

### Tool search আর prompt caching { #tool-search-caching }

Prompt caching একটি **স্থির prefix**-এর ওপর key করে: provider রিকোয়েস্টের শুরু থেকে token-এর দীর্ঘতম অপরিবর্তিত অংশ cache করে, মোটামুটি টুলের সংজ্ঞা → system/নির্দেশনা → বার্তার ইতিহাসের ক্রমে। যেকোনো স্তরে একটি পরিবর্তন সেই স্তর আর তার পরের সবকিছুর cache অবৈধ করে — তাই বেশিরভাগ provider-এ **একটি টুলের সংজ্ঞা বদলানো, যোগ, সরানো বা ক্রম বদলানো cache অবৈধ করে**, কারণ টুলের সংজ্ঞা একেবারে সামনে বসে। [রানের মাঝে দেখা দেওয়া](#mid-run-tool-additions) একটি টুল OpenAI Responses আর Anthropic-এ ব্যতিক্রম, যারা এটি `tools[]`-এর বাইরে পায়।

Tool search **প্রতিটি মডেলে** কাজ করে, কিন্তু cache *রক্ষা* করে শুধু যেখানে আবিষ্কার টুলের সংজ্ঞা অছোঁয়া রাখে: নিজস্ব tool search-সহ মডেলে — Anthropic Sonnet 4.5+, Opus 4.5+ আর Haiku 4.5+, আর GPT-5.4 nano ছাড়া GPT-5.4+-এ OpenAI Responses — আর এটি ছাড়া প্রথম-পক্ষের OpenAI Responses মডেলে, যাদের লোকাল বিকল্প প্রতিটি আবিষ্কৃত টুল একটি `additional_tools` ইনপুট আইটেমে প্রকাশ করে। সেখানে আবিষ্কার [শুধু জোড়া](#tool-search) আর deferred টুল কখনো prompt prefix-এ ঢোকে না, তাই আবিষ্কারের দফা-জুড়ে একটি অভিন্ন prefix cache থেকে আবার পড়া হয়। বাকি প্রতিটি মডেলে — Google, পুরনো Anthropic মডেল, OpenAI Chat Completions আর OpenAI-সামঞ্জস্যপূর্ণ Responses endpoint-সহ — লোকাল `search_tools` বিকল্প একটি আবিষ্কৃত টুল টুলের array-তে যোগ করে প্রকাশ করে, যা **প্রতিটি আবিষ্কারের দফায় টুলের সংজ্ঞা থেকে পরের cache করা prefix অবৈধ করে** (Google-এ, একটি স্থির `system_instruction` টুল ব্লকের আগে বসে আর তবুও আবার ব্যবহার হতে পারে — দেখুন নিচের [Related caching controls](#related-caching-controls))।

/// note | Gemini-তে tool search কেন কখনো prefix গরম রাখে না

নিজস্ব tool search cache রক্ষা করে আবিষ্কার একটি provider-পক্ষের মৌলিক উপাদানের হাতে দিয়ে, যা আবিষ্কৃত টুল রিকোয়েস্টের prefix-এর বাইরে রাখে। Gemini-র API এমন কোনো উপাদান দেয় না — Anthropic-এর `bm25`/`regex` tool search বা OpenAI Responses-এর `tool_search`-এর মতো নয় — তাই Gemini-তে tool search সবসময় লোকাল `search_tools` ফাংশন টুলে ফিরে যায়, যা প্রতিটি মিল টুলের array-তে যোগ করে প্রকাশ করে। যেহেতু Gemini রিকোয়েস্ট prefix-এর ওপর cache করে আর টুলের সংজ্ঞা এর সামনে বসে, একটি নতুন টুল প্রকাশ করা প্রতিটি আবিষ্কারের দফা টুল ব্লক থেকে পরের cache অবৈধ করে। এটি একটি অনুপস্থিত-উপাদানের সীমাবদ্ধতা, সংস্করণের বাধা নয়: Anthropic আর OpenAI-এ একটি নতুন মডেল নিজস্ব tool search *সমর্থন করে*, কিন্তু কোনো Gemini মডেল করে না।

///

/// note | Defer করা প্রসঙ্গ বাঁচায় — এটি গতিশীল নথিভুক্তি নয়

যেকোনো কৌশলে, মডেল কখনো পৌঁছাতে পারে এমন প্রতিটি টুল **আগে থেকে এজেন্ট বা toolset-এ ঘোষিত** থাকতে হবে। Defer করা অব্যবহৃত সংজ্ঞা মডেলের প্রসঙ্গের বাইরে রাখে (আর, নিজস্বভাবে, cache করা prefix-এর বাইরে); এটি আপনাকে এমন একটি একেবারে নতুন টুল নথিভুক্ত করতে দেয় না যা দিয়ে এজেন্ট কখনো কনফিগার হয়নি। যেখানে একটি provider কথোপকথনের মাঝে একটি টুলের ঘোষণা জুড়তে পারে — OpenAI Responses-এর `additional_tools` আইটেম — রিকোয়েস্টের `tools` ব্লকে কখনো ছিল না এমন একটি টুলও prefix না ছুঁয়ে ডাকার যোগ্য হতে পারে, কারণ ঘোষণাটি একটি জোড়া ইনপুট আইটেম হিসেবে যায়।

///

[on-demand capabilities](capabilities/on-demand.md#on-demand-capabilities)-এর জন্য, কোনো নতুন টুল সংজ্ঞা প্রকাশ করে না এমন একটি capability লোড করা — শুধু নির্দেশনা বা মডেল সেটিং — প্রতিটি provider-এ cache রক্ষা করে, নিজস্ব tool search ছাড়াও। Anthropic তার cache key থেকে deferred এন্ট্রি বাদ দেয়: শুধু-capability রান প্রথম দফা থেকেই সেগুলোর আগাম বিজ্ঞাপন দেয়, এককালীন deferred ভূমিকাকে প্রাথমিক prefix-এর অংশ বানিয়ে, অথচ মিশ্র রান সার্চযোগ্য corpus দিয়ে সেই ভূমিকার দাম দেয় আর প্রকাশিত deferred এন্ট্রি cache করা prefix-এর বাইরে জোড়ে। কোনো Anthropic capability লোড রানের মাঝপথে deferred ভূমিকা আনে না, যদিও একটি লোড ছাড়া [রানের মাঝে দেখা দেওয়া](#mid-run-tool-additions) একটি টুল, যেমন একটি capability-র গতিশীল toolset থেকে, কিছু মডেলে আনতে পারে যখন এটি রানের প্রথম deferred ঘোষণা। প্রথম-পক্ষের OpenAI Responses `tools[]` না বদলে প্রকাশটি একটি `additional_tools` ইনপুট আইটেম হিসেবে জোড়ে। অন্যত্র প্রকাশিত টুল টুল-সংজ্ঞার prefix-এ ঢোকে, যেমন ঢোকে একটি নেটিভ টুল, আর যেমন ঢোকে লোডের সময় টুলের সংজ্ঞা নতুন করে লেখা একটি deferred `prepare_tools`/`prepare_output_tools` hook। পুরো বিভাজনের জন্য দেখুন [Cache implications](capabilities/on-demand.md#cache-implications)।

#### রানের মাঝে দেখা দেওয়া টুল { #mid-run-tool-additions }

একটি টুল খোঁজা বা লোড না হয়েও একটি রানে যোগ দিতে পারে। এটি আরেকটি টুলের ভেতর থেকে একটি [`FunctionToolset`](toolsets.md#function-toolset)-এ যোগ হতে পারে, একটি [গতিশীলভাবে তৈরি toolset](toolsets.md#dynamically-building-a-toolset) ফেরত দিতে পারে, একটি MCP সার্ভার `notifications/tools/list_changed` পাঠানোর পরে তালিকায় রাখতে পারে, বা একটি [`prepare_tools`](#prepare-tools) ফাংশন ঢুকতে দিতে পারে। Pydantic AI প্রতিটি ধাপে সাথে সাথে উপলব্ধ ফাংশন টুলগুলো রান যেগুলো দিয়ে শুরু হয়েছিল তার সাথে তুলনা করে, আর প্রতিটি নতুনটি বার্তার ইতিহাসে একটি [`ToolAvailabilityDeltaPart`][pydantic_ai.messages.ToolAvailabilityDeltaPart] হিসেবে রেকর্ড করে। `defer_loading=True`-সহ একটি নতুন টুল রেকর্ড হয় না: এটি [tool search](#tool-search) corpus-এ যোগ দেয় আর একটি সার্চ খুঁজে পেলে প্রকাশিত হয়। একটি রেকর্ড করা টুল তারপর মডেলে পৌঁছায় একটি প্রকাশিত deferred টুলের মতোই:

| Provider | নতুন টুল কীভাবে আসে | Cache prefix |
|---|---|---|
| প্রথম-পক্ষের OpenAI Responses (`OpenAIProvider`) | এর সংজ্ঞা বহন করা একটি `additional_tools` ইনপুট আইটেম | **স্থির**: `tools[]` অপরিবর্তিত, শুধু GPT-5.6-এর আগের মডেলে যে রিকোয়েস্টের `tool_choice` নতুন টুলের নাম দেয় তাতে ছাড়া (দেখুন [Tool Choice](#tool-choice)) |
| tool search-সহ Anthropic মডেল (Sonnet 4.5+, Opus 4.5+, Haiku 4.5+) | একটি `defer_loading` ঘোষণা আর একটি `tool_addition` ব্লক (বা কথোপকথনের মাঝে টুল-পরিবর্তন নেই এমন মডেলে একটি `tool_reference` ফল) | **স্থির** যখন রিকোয়েস্ট আগেই একটি deferred টুল ঘোষণা করে। অন্যথায়, কিছু মডেলে (যেমন Claude Opus 4.8) প্রথম deferred ঘোষণা একটি এককালীন ভূমিকা যোগ করে, যা শুধু সেই রিকোয়েস্টে prefix সরায় |
| বাকি সবকিছু, পুরনো Anthropic মডেল, OpenAI-সামঞ্জস্যপূর্ণ Responses endpoint (Azure, OpenRouter ইত্যাদি) আর OpenAI Chat Completions-সহ | `tools[]`-এ যোগ হয়, সাথে কথোপকথনে একটি নোট যে এটি এখন উপলব্ধ | যে রিকোয়েস্টে দেখা দেয় তাতে টুলের সংজ্ঞা থেকে পরে **ভাঙে** |

একটি ব্যতিক্রম আছে: মডেলকে আগে দেওয়া কিছুই স্থির রাখার মতো বাকি না থাকলে, কারণ রান কোনো সরাসরি দৃশ্যমান টুল ছাড়াই শুরু হয়েছে (ধরুন লেখার আউটপুট আর শুধু deferred টুল, বা একটি খালি তালিকাসহ একটি MCP সার্ভার) বা এটি যে প্রতিটি টুল দিয়ে শুরু হয়েছিল তা পরে চলে গেছে, উপস্থিত টুলগুলো সরাসরি `tools[]`-এ যায় আর কিছুই রেকর্ড হয় না। এটি একটি রিকোয়েস্টকে শুধু deferred টুল বহন করা থেকেও রক্ষা করে, যা Anthropic প্রত্যাখ্যান করে।

রেকর্ডটি বার্তার ইতিহাসে থাকে, তাই একই ইতিহাসের ওপর একটি আবার-চেষ্টা করা রিকোয়েস্ট বা পরের একটি রান টুলটি আবার ঘোষণা করে না। রানের সময় [compaction](capabilities/compaction.md) রেকর্ডটির সারাংশ করে সরিয়ে দিলে, `tools[]` না বদলে টুলটি আরও একবার ঘোষিত হয়। compaction-এর পরে শুরু হওয়া পরের একটি রান আর রেকর্ডটি দেখে না, তাই এটি শুরু থেকে থাকা যেকোনো টুলের মতো প্রথম রিকোয়েস্ট থেকেই টুলটি `tools[]`-এ ঘোষণা করে।

শুধু একটি একক রানের মধ্যে দেখা দেওয়া টুলই ধরা পড়ে। একই ইতিহাসের ওপর পরের একটি রানে নতুন একটি টুল, যেমন একটি [tool approval](deferred-tools.md#human-in-the-loop-tool-approval)-এর পরে খোলা একটি, সেই রানের প্রথম রিকোয়েস্ট থেকে `tools[]`-এ পাঠানো হয়। অদৃশ্য হওয়া টুল, আর একই নামে সংজ্ঞা বদলানো টুলও যেমন আছে তেমন পাঠানো হয়।

[Durable execution](durable_execution/overview.md)-এর অধীনে, রানের মাঝের পরিবর্তন workflow-এর অংশ হিসেবে চলা কোড থেকে চালান, যেমন একটি `prepare_tools` ফাংশন বা রানের অবস্থা পড়া একটি গতিশীলভাবে তৈরি toolset। Temporal-এ, টুল activity-তে চলে, যা workflow আবার চালানোর সময় আবার চলে না, তাই `add_function()` ডাকা একটি টুল এমন পরিবর্তন করে যা replay পুনরুৎপাদন করবে না।

সত্যিই অসীম টুলের জগতের জন্য, সবকিছু একটি একক, স্থির টুল দিয়ে পাঠান। harness-এর [`CodeMode`](harness/code-mode.md) capability অনেক টুলকে একটি `run_code` টুলে গুটিয়ে আনে যার সংজ্ঞা বাইট-স্থির থাকে; নতুন আবিষ্কৃত টুল নতুন টুল schema হিসেবে নয়, sandbox-এর ভেতরে callable হিসেবে দেখা দেয়, আবিষ্কার-জুড়ে টুল-সংজ্ঞার prefix — আর এর cache — অক্ষত রেখে।

#### একটি trace-এ দেখা { #seeing-it-in-a-trace }

নিজস্ব tool search-এ deferred ক্যাটালগ কখনো cache করা prefix-এ ঢোকে না, তাই পরের দফায় একটি অভিন্ন রিকোয়েস্ট prefix cache থেকে আবার পড়া হয় — মডেল নতুন টুল আবিষ্কার করলেও `cache_read_tokens` গরম থাকে:

/// info | Logfire trace

[Anthropic: cached tool + system prefix re-read from cache, with deferred tools declared](https://logfire-us.pydantic.dev/public-trace/243f9aa5-dd9d-4de4-a36a-5818611892f1?spanId=28a1621e429ce027)

///

একটি একক টুলের সংজ্ঞা বদলান, আর বদলে পুরো prefix নতুন করে তৈরি হয় — [একটি টুলের বর্ণনা সম্পাদিত একই রিকোয়েস্ট](https://logfire-us.pydantic.dev/public-trace/c3205dc9-6251-40fa-9d0a-ed647be9ba30?spanId=38ef4635ecaf3e0b) কোনো cache পড়া রেকর্ড করে না।

#### সংশ্লিষ্ট caching নিয়ন্ত্রণ { #related-caching-controls }

- [`tool_choice`](#tool-choice) দিয়ে *সক্রিয়* টুল সীমিত করলেও cache অবৈধ হতে পারে যখন Pydantic AI-কে client-পক্ষে array ছাঁটতে হয় — প্রতি-provider বিভাজন আর cache-রক্ষাকারী বিকল্পের (`allowed_tools`, `allowed_function_names`, `ToolOrOutput`) জন্য দেখুন [Prompt caching implications](#tool-choice-caching)।
- বার্তায় স্পষ্ট cache breakpoint বসাতে, [`CachePoint`][pydantic_ai.messages.CachePoint] ব্যবহার করুন (Anthropic, Bedrock আর OpenRouter মানে)। Anthropic-এর টুল, system আর নির্দেশনা caching সেটিং নথিভুক্ত আছে [Anthropic prompt caching](models/anthropic.md#prompt-caching)-এ।
- যে provider prefix-এর সামনে টুলের সংজ্ঞা cache করে — Anthropic, OpenAI আর xAI — সেগুলোতে একটি একক টুলের বর্ণনা সম্পাদনা করলে cache করা prefix অবৈধ হয়। Google-এর *implicit* cache একটি ভিন্ন বিন্যাসে prefix-ভিত্তিক (এর `system_instruction` টুল ব্লকের আগে একটি আলাদা ফিল্ড), তাই একটি বড় স্থির system নির্দেশনা টুলের তালিকা বদলালেও cache hit রাখতে পারে; একটি স্পষ্ট [`CachedContent`](models/google.md) বদলে গঠনগতভাবে টুলগুলোকে cache-এর একটি অপরিবর্তনীয় অংশ হিসেবে আটকে রাখে।

## টাইপ করা টুল অংশ { #typed-tool-parts }

একটি টুলের নাম যিনি লিখেছেন বা কনফিগার করেছেন তিনি বাছেন, আর এর নাম বদলানো বা উপসর্গ যোগ হতে পারে (যেমন [`PrefixTools`][pydantic_ai.capabilities.PrefixTools] দিয়ে), তাই একটি নির্দিষ্ট টুল চিনতে হবে এমন কোডের নাম তুলনা করা উচিত নয়। বদলে, একটি টুল একটি [`ToolKind`][pydantic_ai.messages.ToolKind] দিয়ে ঘোষণা করতে পারে এটি কী। এর কল আর ফেরতের অংশ kind-এর [`id`][pydantic_ai.messages.ToolKind.id] তাদের [`tool_kind`][pydantic_ai.messages.BaseToolCallPart.tool_kind] হিসেবে বহন করে আর [`ToolCallPart`][pydantic_ai.messages.ToolCallPart] ও [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart]-এর টাইপ করা subclass-এ উন্নীত হয়। তখন একটি hook বা history processor `isinstance` দিয়ে টুলটি মেলাতে পারে, এর নাম যা-ই হোক। Core-এর tool search আর deferred-capability টুল এভাবে কাজ করে: [`ToolSearchCallPart`][pydantic_ai.messages.ToolSearchCallPart] আর [`LoadCapabilityReturnPart`][pydantic_ai.messages.LoadCapabilityReturnPart] উদাহরণ।

/// tip | উদাহরণ দিয়ে বুঝি

টুলের নাম হলো দোকানের সাইনবোর্ড — মালিক বদলাতে পারেন ("লুকআপ" থেকে "lookup_v2")। `ToolKind` হলো সরকারি ট্রেড লাইসেন্স নম্বর — যা বদলায় না। নাম না দেখে লাইসেন্স নম্বর (`isinstance`) দিয়ে চিনলে, নাম বদলালেও আপনার কোড ঠিক দোকান চেনে।

///

একটি kind-এর একটি namespace আর একটি নাম থাকে, আর ঐচ্ছিকভাবে টুলের আর্গুমেন্ট (`args`) আর ফলের (`content`) আকার, সাধারণত `TypedDict`। এর id `'{namespace}.{name}'`: namespace ভিন্ন প্যাকেজের kind আলাদা রাখে, যা গুরুত্বপূর্ণ কারণ id প্রতিটি বার্তার ইতিহাসে সংরক্ষিত হয়। একটি kind-এর জন্য টাইপ করা অংশ নথিভুক্ত হয় `kind` ক্লাস আর্গুমেন্ট দিয়ে, যেভাবে [capability events](capabilities/overview.md#capability-events) সংজ্ঞায়িত হয়, আর কোনো `@dataclass` decorator লাগে না। এদের base class kind-এর আকার দিয়ে parameterize করা, যা এদের `typed_args` আর `typed_content` টাইপ করে। একটি টুল তারপর `tool_kind` দিয়ে তার kind ঘোষণা করে, এখানে [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain]-এ:

```python title="typed_tool_part.py"
from typing_extensions import TypedDict

from pydantic_ai import Agent, ToolKind
from pydantic_ai.messages import ToolCallPart, ToolReturnPart


class LookupArgs(TypedDict):
    sku: str


class LookupResult(TypedDict):
    in_stock: bool


lookup = ToolKind('inventory', 'lookup', args=LookupArgs, content=LookupResult)


class LookupCallPart(ToolCallPart[LookupArgs], kind=lookup):
    pass


class LookupReturnPart(ToolReturnPart[LookupResult], kind=lookup):
    pass


agent = Agent('test')


@agent.tool_plain(tool_kind=lookup)
def check_stock(args: LookupArgs) -> LookupResult:
    return {'in_stock': args['sku'].startswith('A')}


result = agent.run_sync('Is A-1 in stock?')
call = result.all_messages()[1].parts[0]
tool_return = result.all_messages()[2].parts[0]
assert isinstance(call, LookupCallPart) and isinstance(tool_return, LookupReturnPart)
print(call.tool_kind)
#> inventory.lookup
print(call.typed_args)
#> {'sku': 'a'}
print(tool_return.typed_content)
#> {'in_stock': False}
```

একটি টুল ফাংশন kind-এর আর্গুমেন্ট তার একটি প্যারামিটার হিসেবে নিতে পারে, যেমন `check_stock` নেয়: মডেল তবুও আকারের ফিল্ড (এখানে `sku`) টুলের প্যারামিটার হিসেবে দেখে, আর ফাংশন সেগুলো একটি `LookupArgs` হিসেবে যাচাই করা অবস্থায় পায়। এটি আলাদা প্যারামিটার হিসেবেও নিতে পারে, যেমন `def check_stock(sku: str) -> LookupResult`-এ। একটি `ToolKind` দেওয়া হলে, টুল decorator type checker-কে ফাংশনের ফেরত টাইপ kind-এর `content`-এর সাথে পরীক্ষা করায়। Type checker ভুল আকারের একটি একক প্যারামিটার আর আলাদা প্যারামিটারসহ একটি ফাংশনের মধ্যে পার্থক্য করতে পারে না, তাই এজেন্ট তার টুল সংগ্রহের সময় প্যারামিটার পরীক্ষা হয় (নিচে দেখুন)।

`typed_args` kind-এর `args`-এর বিপরীতে যাচাই করা আর্গুমেন্ট ফেরত দেয়, বা সেগুলো তখনো stream হতে থাকলে বা যাচাই না হলে `None`। `args` নিজে base টাইপ রাখে, কারণ এটি তখনো কাঁচা JSON স্ট্রিং ধরে থাকতে পারে। একইভাবে, `typed_content` kind-এর `content`-এর বিপরীতে যাচাই করা বিষয়বস্তু ফেরত দেয়, বা না মিললে `None`। `content` নিজে যেমন পাঠানো হয়েছিল তেমন থাকে, এমনকি একটি JSON স্ট্রিং হলেও, তাই একটি সংরক্ষিত ইতিহাস আর মডেলে ফেরত পাঠানো জিনিস বদলায় না। একটি অংশ উন্নীত হয় শুধু যখন এর আর্গুমেন্ট, একবার একটি dictionary হলে, আকারে মেলে; একটি ফেরতের অংশ শুধু যখন এর [`outcome`][pydantic_ai.messages.BaseToolReturnPart.outcome] `'success'` আর এর বিষয়বস্তু মেলে, কারণ অন্য যেকোনো ফেরতের বিষয়বস্তু টাইপ করা ফল নয়, একটি এরর। একটি kind-এর একটি আকার ঘোষণা করতে হয় না: একটি ছাড়া, যেকোনো আর্গুমেন্ট বা বিষয়বস্তু উন্নীত হয়, আর টাইপ করা অংশের base class unparameterized থাকে। kind-এরটি থেকে ভিন্ন আকার দিয়ে parameterize করা একটি base class একটি এরর, type checker আর ক্লাস সংজ্ঞায়িত হওয়ার সময় দুটোতেই।

যে অংশের kind-এর একটি টাইপ করা অংশ আছে তা এর [`ModelResponse`][pydantic_ai.messages.ModelResponse] বা [`ModelRequest`][pydantic_ai.messages.ModelRequest] তৈরি হওয়ামাত্র উন্নীত হয়, একটি মডেল দিয়ে, একটি সংরক্ষিত ইতিহাস লোড করে, বা হাতে, তাই `ModelResponse(parts=[ToolCallPart('lookup_v2', {'sku': 'A-1'}, tool_kind='inventory.lookup')]).parts[0]`-ও একটি `LookupCallPart`। এটি core-এর নিজের kind-এও (`'tool-search'`, `'capability-load'`) প্রযোজ্য। [Temporal](durable_execution/temporal.md)-এর অধীনে, যার workflow sandbox আপনার মডিউল আবার import করে, workflow কোডে উন্নীত একটি অংশ workflow কোড যে ক্লাস import করেছে তার একটি instance, তাই একই `isinstance` পরীক্ষা সেখানেও কাজ করে।

একটি টুল তার kind ঘোষণা করে [`Tool`][pydantic_ai.tools.Tool] আর টুল decorator-এর `tool_kind` আর্গুমেন্ট দিয়ে, বা [`ToolDefinition.tool_kind`][pydantic_ai.tools.ToolDefinition.tool_kind] সেট করে, যেমন একটি toolset-এর `get_tools` বা একটি [`prepare`](#tool-prepare) ফাংশনে। যেকোনোটি `ToolKind` বা এর id নেয়। একটি রান তার টুল সংগ্রহের সময়, সংজ্ঞায়িত নয় এমন একটি kind-এর জন্য [`UserError`][pydantic_ai.exceptions.UserError] তোলে, তাই এটি সংজ্ঞায়িত করা মডিউল import করা থাকতে হবে; এমন kind-সহ একটি সংরক্ষিত `ToolDefinition` (যেমন durable execution-এর ইতিহাসে) তবুও লোড হয়। এটি `UserError`-ও তোলে যখন টুলের প্যারামিটার kind-এর `args`-এ মেলে না, বা এর ফেরত টাইপ kind-এর `content`-এ মেলে না: আকারের প্রয়োজনীয় প্রতিটি ফিল্ড টুলের একটি বাধ্যতামূলক ফিল্ড হতে হবে, আর যেখানে দুটোই একটি ফিল্ডকে একটি JSON টাইপ দেয়, সেই টাইপগুলো মিলতে হবে। ফিল্ড ধরে তুলনা করা যায় না এমন একটি ফেরত টাইপ, যেমন একটি union, গৃহীত হয়। এটি একটি যুক্তিসঙ্গততার পরীক্ষা, পূর্ণ JSON Schema তুলনা নয়।

একটি টাইপ করা subclass শুধু property যোগ করতে পারে; নিজের একটি ফিল্ড যোগ করলে ক্লাস সংজ্ঞায়িত হওয়ার সময় `UserError` ওঠে। সেই নিষেধাজ্ঞা একটি অংশকে কিছু না হারিয়ে তার base class-এ ফিরে যেতে দেয়। বর্তমান প্রসেস সংজ্ঞায়িত করে না এমন একটি kind দিয়ে রেকর্ড করা একটি ইতিহাস (কারণ সংজ্ঞায়িত করা মডিউল import করা নেই, বা সরানো হয়েছে) তবুও লোড হয়: অংশটি তার `tool_kind` রাখা একটি সাধারণ `ToolCallPart` / `ToolReturnPart` থাকে, আর যেখানে kind সংজ্ঞায়িত সেখানে আবার টাইপ করা অংশ হয়।

### Kind দিয়ে একটি টুলকে সরিয়ে দেওয়া { #unless-tool-kind }

একটি capability কখনো কখনো এমন কিছুর জন্য নিজের টুল দেয় যা এজেন্টের একটি আরও সাধারণ টুলও করতে পারে, যেমন workspace-এ রাখা নোট পড়া একটি টুল যখন এজেন্ট এমনিতেই ফাইল পড়তে পারে। [`ToolDefinition.unless_tool_kind`][pydantic_ai.tools.ToolDefinition.unless_tool_kind] একটি kind-এ সেট করলে রান ধাপের আরেকটি টুলের সেই kind থাকলেই টুলটি সরে দাঁড়ায়, সেই টুলের নাম যা-ই হোক। এটি [`unless_native`][pydantic_ai.tools.ToolDefinition.unless_native]-এর প্রতিরূপ, যা মডেলের সমর্থিত একটি নেটিভ টুলের জন্য একই কাজ করে।

এমন একটি টুলের উল্লেখ করা নির্দেশনা আর টুল ফলেও এর নাম লিখে রাখা উচিত নয়। [`RunContext.tool_name_for_kind`][pydantic_ai.tools.RunContext.tool_name_for_kind] বর্তমান ধাপে একটি kind-সহ টুলের নাম ফেরত দেয়, যেকোনো উপসর্গসহ, বা কোনোটি না থাকলে `None`:

```python title="unless_tool_kind.py"
from dataclasses import replace

from pydantic_ai import Agent, AgentRunResult, ModelRequest, RunContext, Tool, ToolKind
from pydantic_ai.tools import ToolDefinition
from pydantic_ai.toolsets import FunctionToolset

file_read = ToolKind('workspace', 'file_read')


def read_file(path: str) -> str:
    """Read a file in the workspace."""
    return f'contents of {path}'


def read_notes() -> str:
    """Read the notes kept in `notes.md`."""
    return 'notes'


def unless_file_reader(ctx: RunContext, tool_def: ToolDefinition) -> ToolDefinition:
    return replace(tool_def, unless_tool_kind=file_read)


agent = Agent('test', tools=[Tool(read_notes, prepare=unless_file_reader)])


@agent.instructions
def notes_instructions(ctx: RunContext) -> str:
    if reader := ctx.tool_name_for_kind(file_read):
        return f'Your notes are in `notes.md`. Read them with `{reader}`.'
    return 'Read your notes with `read_notes`.'


def sent_instructions(result: AgentRunResult[str]) -> str | None:
    request = result.all_messages()[0]
    assert isinstance(request, ModelRequest)
    return request.instructions


result = agent.run_sync('What do my notes say?')
print(sent_instructions(result))
#> Read your notes with `read_notes`.
print(result.output)
#> {"read_notes":"notes"}

file_tools = FunctionToolset([Tool(read_file, tool_kind=file_read)])
result = agent.run_sync('What do my notes say?', toolsets=[file_tools])
print(sent_instructions(result))
#> Your notes are in `notes.md`. Read them with `read_file`.
print(result.output)
#> {"read_file":"contents of a"}
```

সিদ্ধান্ত নেওয়া হয় রান ধাপের টুল সংগ্রহের সময়, যেকোনো [`prepare_tools`](#prepare-tools) ফাংশনের পরে, তাই বাদ পড়া একটি টুল মডেলে পাঠানো হয় না, ডাকার যোগ্যও নয়, আর `tool_name_for_kind` এটি ফেরত দেয় না। [deferred loading](#tool-search) দিয়ে লুকানো একটি টুল উপস্থিত হিসেবে গোনা হয়: উত্তর, আর এ থেকে তৈরি নির্দেশনা, সেই টুল প্রকাশিত হলেও একই থাকে, যা prompt-কে cache-যোগ্য রাখে। একটি টুল বাদ পড়ে শুধু এমন একটি টুলের পক্ষে যা থাকে, তাই একটি তৃতীয় টুল সাধারণটিকে সরিয়ে দিলে, capability-র টুল ফিরে আসে। টুলগুলো প্রত্যেকে অন্যটির পক্ষে বাদ পড়ত এমন হলে, ধাপের টুলে এদের মধ্যে প্রথম তালিকাভুক্তটি থাকে আর যে প্রতিটি টুলের kind এটি নাম দেয় সেগুলো সরে দাঁড়ায়। কিছু চক্র একসাথে প্রতিটি নিয়ম মানতে পারে না (A unless B, B unless C, C unless A)। একটি টুল তবুও কখনো বাদ পড়ে না যদি না এর নাম দেওয়া একটি টুল থাকে, তাই এমন একটি চক্রে একটি টুল এমন একটির পাশে থাকতে পারে যার kind এটি নাম দেয়; একই ক্রমে একই টুলের জন্য ফল একই। `tool_kind`-এর মতো নয়, `unless_tool_kind`-এর kind সংজ্ঞায়িত থাকার দরকার নেই: শুধু id তুলনা করা হয়, তাই একটি capability সেই প্যাকেজ import না করেই আরেকটি প্যাকেজের টুলের জন্য তার kind id দিয়ে সরে দাঁড়াতে পারে, আর কোনো টুলের নেই এমন একটি kind মানে সরে দাঁড়ানোর কিছু নেই।

কয়েকটি টুলের kind থাকলে, `tool_name_for_kind` [`RunContext.tools`][pydantic_ai.tools.RunContext.tools]-এর ক্রমে প্রথমটি ফেরত দেয়, যা ধাপের toolset-গুলো সেগুলো যে ক্রমে তালিকা করে সেই ক্রম, আর যার ওপর iterate করে সবগুলো দেখতে পারেন। নির্দেশনা ফাংশন, মডেল রিকোয়েস্ট hook আর টুল বর্তমান ধাপের টুল দেখে, একটি Temporal activity-তে চলা একটি টুলসহ, যা activity পাঠানোর সময় নেওয়া ধাপের টুলের একটি snapshot থেকে উত্তর দেয়। একটি toolset-এর `get_tools` আর `prepare_tools` ফাংশন সেগুলো তখনো সংগ্রহ হতে থাকার সময় চলে, তাই সেখানে এটি আগের ধাপ থেকে উত্তর দেয়।

## আরও দেখুন { #see-also }

- [Function Tools](tools.md) - টুলের মৌলিক ধারণা আর নথিভুক্তি
- [Toolsets](toolsets.md) - টুলের সংগ্রহ সামলানো
- [Deferred Tools](deferred-tools.md) - অনুমোদন বা বাইরে চালানো লাগে এমন টুল
- [Third-Party Tools](third-party-tools.md) - বাইরের টুল লাইব্রেরির সাথে সংযোগ

/// check | সংক্ষেপে মনে রাখুন

* ফল আর বাড়তি বিষয়বস্তু/metadata আলাদা করতে `ToolReturn(return_value=..., content=..., metadata=...)`।
* `prepare`/`prepare_tools` দিয়ে প্রতি ধাপে টুল লুকানো বা বদলানো; সংজ্ঞা নতুন না বানিয়ে `dataclasses.replace`।
* `ModelRetry` = শুধরে আবার চেষ্টা (বাজেট খরচ), `ToolFailed` = ব্যর্থতা জানানো (বাজেট খরচ নয়); `args_validator` দিয়ে ব্যবসায়িক যাচাই।
* `timeout=`/`tool_timeout`, `sequential=True`, আর `tool_choice` দিয়ে টুল বাছাই নিয়ন্ত্রণ।
* অনেক টুলে `defer_loading=True` দিয়ে tool search; cache রক্ষা নির্ভর করে provider-এর ওপর।

///
