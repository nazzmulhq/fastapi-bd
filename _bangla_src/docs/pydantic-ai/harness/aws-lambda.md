
# AWS Lambda Durability { #aws-lambda-durability }

/// note | এই পেজে যা শিখবেন

* `AWSLambdaDurability` দিয়ে একটি এজেন্টকে AWS Lambda durable function-এ আবার-চালু-যোগ্য করা।
* sync Lambda handler আর async এজেন্ট কীভাবে `durable_agent_handler` দিয়ে যুক্ত হয়।
* কী কী checkpoint হয়, step-এর নাম, আর গুরুত্বপূর্ণ সীমাবদ্ধতা (retry, ক্রম, বাজেট)।
* প্রতি-টুল কনফিগারেশন।

///

`AWSLambdaDurability` একটি এজেন্টকে [AWS Lambda durable
functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)-এ আবার-চালু-যোগ্য করে। প্রতিটি মডেল রিকোয়েস্ট, ফাংশন টুল কল, MCP কল আর dynamic-toolset মীমাংসা একটি durable step হিসেবে checkpoint হয়, তাই যে invocation timeout হয়, ব্যর্থ হয় বা retry হয়, তা ইতিমধ্যে টাকা দেওয়া কাজ পুনরাবৃত্তি না করে শেষ সম্পন্ন step থেকে চলতে থাকে।

Lambda durable operation-এর একটি log রাখে। একটি execution আবার চললে, handler আবার শুরু থেকে চলে আর সম্পন্ন step-গুলো চালানোর বদলে তাদের সংরক্ষিত ফল ফেরত দেয়। checkpoint ছাড়া, একটি আবার-চালু রান প্রতিটি মডেল রিকোয়েস্ট আর টুল কল পুনরাবৃত্তি করত।

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি Lambda function-এর সর্বোচ্চ চলার সময় সীমিত। ধরুন একটি এজেন্ট ১০টি টুল কল করে আর ৭ নম্বরে timeout হলো। সাধারণ Lambda-য় retry মানে আবার ১ থেকে — আগের ৬টি মডেল কলের টাকা আবার। durable Lambda-য় handler আবার শুরু থেকে চলে, কিন্তু ১-৬ নম্বর step-এর ফল log থেকে সাথে সাথে ফেরত আসে (চলে না), আর কাজ ৭ থেকে এগোয়।

///

## ইনস্টলেশন { #installation }

/// tab | pip

```bash
pip install "pydantic-ai-harness[aws-lambda]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[aws-lambda]"
```

///


AWS Durable Execution SDK-এর জন্য Python 3.11 বা নতুনতর লাগে।

নিচের quick start একটি Bedrock provider মডেল ব্যবহার করে, যার জন্য
`pydantic-ai-slim[bedrock]` থেকে Bedrock SDK লাগে:

/// tab | pip

```bash
pip install "pydantic-ai-harness[aws-lambda]" "pydantic-ai-slim[bedrock]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[aws-lambda]" "pydantic-ai-slim[bedrock]"
```

///


## দ্রুত শুরু { #quick-start }

এজেন্ট তৈরির সময় capability যুক্ত করুন, তারপর `durable_agent_handler` দিয়ে একটি async handler body মানিয়ে নিন:

```python title="handler.py"
from typing import Any

from aws_durable_execution_sdk_python import DurableContext, durable_execution
from pydantic_ai import Agent

from pydantic_ai_harness.aws_lambda import AWSLambdaDurability, durable_agent_handler

agent = Agent(
    'bedrock:global.anthropic.claude-sonnet-5-5',
    name='support',
    capabilities=[AWSLambdaDurability()],
)


@agent.tool_plain
def get_weather(city: str) -> str:
    return f'It is sunny in {city}.'


@durable_execution
@durable_agent_handler
async def handler(event: dict[str, Any], context: DurableContext) -> str:
    result = await agent.run(str(event['prompt']))
    return result.output
```

প্রতি রানে না করে তৈরির সময় capability যুক্ত করুন। প্রতি-রানে যুক্ত করাও কাজ করে (capability যেকোনোভাবেই toolset বাঁধে আর মোড়ায়), কিন্তু একবার যুক্ত করলে মোড়ানো আর deploy করা step-এর রূপ invocation জুড়ে স্থিতিশীল থাকে, আর এটি অন্য durability ইন্টিগ্রেশনের সাথে মেলে।

একটি durable কনফিগারেশন দিয়ে deploy করুন আর একটি published version invoke করুন, কারণ চলমান execution তাদের শুরু করা version-এ আটকানো থাকে:

```bash
aws lambda create-function \
  --function-name support-agent \
  --runtime python3.13 \
  --handler handler.handler \
  --role <ROLE_ARN> \
  --zip-file fileb://support-agent.zip \
  --timeout 300 --memory-size 1024 \
  --durable-config '{"ExecutionTimeout":3600,"RetentionPeriodInDays":7}'

aws lambda publish-version --function-name support-agent
```

/// warning | একটি রান শুধু durable handler সেতুর ভেতরেই durable

`AWSLambdaDurability` যুক্ত করা নিজে থেকে একটি রান durable করে না। শুধু
`durable_agent_handler` বা `run_durable` দিয়ে প্রবেশ করা একটি রানই checkpoint হয়। `agent.run_sync(...)` ডাকা, বা নিজের `asyncio.run(...)` থেকে এজেন্ট await করা, একটি পুরোপুরি কাজ করা কিন্তু
**non-durable** রান তৈরি করে, কোনো সতর্কবার্তা ছাড়াই।

///

## প্রয়োজনীয়তা { #requirements }

এজেন্টের একটি `name` (বা `AWSLambdaDurability(name=...)`) লাগে, আর প্রতিটি পাতা-স্তরের toolset-এর একটি অনন্য `id` লাগে। দুটোই প্রতিটি step নামের অংশ, তাই এজেন্ট তৈরির সময়ই দুটো যাচাই হয়: নাম ছাড়া একটি এজেন্ট `Agent(...)` থেকে একটি `UserError` তোলে, একইভাবে `id` নেই বা অন্য toolset-এর সাথে একই `id` ভাগ করা একটি toolset-ও। এজেন্টে সরাসরি নিবন্ধিত টুল এমন একটি toolset-এ থাকে যার id `<agent>` হিসেবে দেখায়, তাই `@agent.tool_plain def get_weather` checkpoint হয়
`{name}__function_toolset__<agent>.call_tool:get_weather` হিসেবে।

## sync handler আর async এজেন্ট কীভাবে যুক্ত হয় { #how-the-sync-handler-and-the-async-agent-connect }

Lambda-র durable API synchronous: `context.step(...)` আটকে থাকে, আর প্রতিটি step Lambda যে thread invoke করেছে তাতেই তৈরি করতে হয়। একটি এজেন্ট রান async। `durable_agent_handler` দুটিকে জুড়তে `run_durable` ব্যবহার করে: এটি async handler body একটি background event loop-এ রাখে আর এর step-গুলো Lambda handler thread-এ পরিবেশন করে, তাই সব step একটি অবিচ্ছিন্ন ক্রমে তৈরি হয়। একটি step body এর কাজ এজেন্ট loop-এ ফেরত দেয় আর শেষ না হওয়া পর্যন্ত আটকে থাকে, যা handler thread অপেক্ষার সময় loop-কে মুক্ত রাখে।

async body কয়েকটি এজেন্ট রান await করতে পারে আর তাদের মাঝে async কাজ করতে পারে, আর ওই সব অংশ একই সেতু আর step ক্রম ভাগ করে। রানগুলো একটার পর একটা await করুন, `asyncio.gather` বা task দিয়ে একসাথে নয়: একটি আবার-চালু execution checkpoint মেলায় step-গুলো যে ক্রমে পৌঁছানো হয় তা দিয়ে, তাই replay-তে ভিন্ন ক্রমে তাদের step-এ পৌঁছানো একসাথে চলা রানগুলো একে অপরের লেখা ফল পায়। একটি synchronous handler-কে প্রতিটি async অংশের জন্য আলাদাভাবে `run_durable` ডাকতে হয়, আর একসাথে কল প্রত্যাখ্যাত হয়।

তিনটি ফলাফল জানা মূল্যবান:

- `@durable_execution` অবশ্যই সবচেয়ে বাইরের decorator হতে হবে, কারণ এর wrapper-ই Lambda invoke করে।
  ক্রম উল্টালে handler সংজ্ঞায়িত হওয়ার সময় একটি `UserError` ওঠে।
- `run_durable` ডাকা thread আটকে রাখে, তাই একটি চলমান event loop-এর ভেতর থেকে এটি ডাকা যায় না।
  একটি synchronous handler থেকে সরাসরি এটি ডাকুন। সেতুতে একটি handler-এর শীর্ষ ছাড়া অন্য কোথাও প্রবেশ করতে হলে এটি উপলব্ধ থাকে।
- Durable step nest করতে পারে না। আরেকটি durable এজেন্ট রান শুরু করা একটি টুল deadlock না করে একটি ব্যাখ্যামূলক error দিয়ে প্রত্যাখ্যাত হয়।

একটি উষ্ণ execution environment-এর invocation জুড়ে loop পুনর্ব্যবহৃত হয়, তাই একটি provider-এর cache করা HTTP client-এর মতো loop-বাঁধা resource তাদের মাঝে বৈধ থাকে। তাই একটি স্থগিত বা error-এ পরিত্যক্ত রান handler ফেরত দেওয়ার আগে বাতিল হয়, আর `run_durable` এটি গুটিয়ে নেওয়ার জন্য `cancel_timeout` সেকেন্ড (ডিফল্ট 5) অপেক্ষা করে। যে কাজের পরিষ্কার সত্যিই ধীর, তার জন্য এটি বাড়ান। timeout শেষ হলে, পরিত্যক্ত পরিষ্কার-কাজ একটি অবসরপ্রাপ্ত loop-এ সর্বোচ্চ সেই loop-এর grace period পর্যন্ত চলতে থাকে আর পরের উষ্ণ invocation-এর সাথে মিশে যেতে পারে। এজেন্ট রান আর handler-এর মধ্যে পরিবর্তনযোগ্য module-global state ভাগ করবেন না। পরিষ্কার-কাজের একটি বাইরের side effect, যেমন একটি store-এ লেখা, একটি ভাগ করা lock ছাড়া, বা একটি metric পাঠানো, পরের একটি invocation-এর সময়ও ঘটতে পারে।
Loop-বাঁধা resource বিচ্ছিন্ন: পরের invocation একটি নতুন loop পায়, তাই পরিত্যক্ত পরিষ্কার-কাজ ওই invocation-এর provider HTTP client-এর মতো resource ছুঁতে পারে না।

loop পুনর্ব্যবহারের আরও একটি ফলাফল আছে: একটি টুল থেকে `asyncio.create_task()` দিয়ে বা executor কাজ await না করে রেখে background কাজ আলাদা করবেন না। আলাদা করা কাজ checkpoint হয় না আর durable execution-এর নিশ্চয়তায় কভার হয় না, আর এটি একে শুরু করা invocation-এর চেয়ে বেশি দিন টিকতে পারে।

## কী checkpoint হয় { #what-gets-checkpointed }

Step-এর নাম তৈরি হয় এজেন্টের `name` আর প্রতিটি toolset-এর `id` থেকে:

| Step-এর নাম | কাজ |
|---|---|
| `{name}__model.request` | একটি মডেল রিকোয়েস্ট অংশ |
| `{name}__model.request_stream` | একটি stream করা মডেল রিকোয়েস্ট অংশ |
| `{name}__model.compact_messages` | একটি মডেল message-compaction কাজ |
| `{name}__model.cancel_suspended_response` | একটি স্থগিত response গুটিয়ে ফেলা |
| `{name}__capability__{capability_id}.{operation}` | অন্য একটি capability-র দেওয়া একটি কাজ |
| `{name}__function_toolset__{id}.validate_args` | একটি ফাংশন টুল কলের আর্গুমেন্ট যাচাই |
| `{name}__function_toolset__{id}.call_tool:{tool}` | একটি ফাংশন টুল কল |
| `{name}__mcp_server__{id}.get_tools` | একটি MCP সার্ভারের টুল তালিকা |
| `{name}__mcp_server__{id}.get_instructions` | একটি MCP সার্ভারের instructions |
| `{name}__mcp_server__{id}.call_tool` | একটি MCP টুল কল |
| `{name}__dynamic_toolset__{id}.get_tools` | একটি dynamic toolset মীমাংসা |
| `{name}__dynamic_toolset__{id}.validate_args` | একটি dynamic toolset কলের আর্গুমেন্ট যাচাই |
| `{name}__dynamic_toolset__{id}.call_tool:{tool}` | একটি dynamic toolset-এর টুল কল |
| `{name}__event_stream_handler` | একটি `event_stream_handler`-এ পাঠানো একটি event |

এজেন্টের ডিফল্ট মডেল ব্যবহার করে না এমন একটি মডেল কাজ step নামে এর model id লেখে
(যেমন `{name}__model.request.{model_id}`), তাই execution history দেখায় প্রতিটি checkpoint কোন মডেল থেকে এসেছে। ডিফল্ট মডেল সাধারণ, প্রত্যয়-ছাড়া নাম রাখে।

## সীমাবদ্ধতা { #constraints }

- **Step অন্তত একবার চলে, আর ডিফল্টভাবে retry হয়।** একটি step চলার পরে checkpoint হয়, তাই একটি টুলের side effect আর এর checkpoint-এর মাঝে একটি বাধা execution আবার চলার সময় টুলটি আবার চালায়। এর ওপরে, SDK-এর ডিফল্ট retry policy হলো exponential backoff-সহ (5s থেকে 60s) ছয়টি চেষ্টা, প্রতিটি মডেল রিকোয়েস্ট আর প্রতিটি টুল কলে প্রযোজ্য। টুলের side effect idempotent রাখুন। শুধু `AT_MOST_ONCE_PER_RETRY` একটি টুলকে একবার চালাতে যথেষ্ট নয়: এটি একটি চেষ্টার *ভেতরে* একটি বাধার পর আবার চালানো আটকায়, কিন্তু retry policy তবুও আরও চেষ্টা শুরু করে যা body চালায়। যে টুল পুনরাবৃত্তি করা চলবে না, তার জন্য দুটোই সেট করুন:

    ```python
    from aws_durable_execution_sdk_python.config import StepSemantics
    from aws_durable_execution_sdk_python.retries import RetryPresets

    metadata={'aws_lambda': {'step_semantics': StepSemantics.AT_MOST_ONCE_PER_RETRY,
                             'retry_strategy': RetryPresets.none()}}
    ```

- **Retry জমা হয়।** Pydantic AI আর provider client-এর নিজস্ব retry লজিক আছে। step retry policy-র পাশাপাশি সেগুলো চালু রাখলে চেষ্টার সংখ্যা গুণিত হয় আর `Retry-After` ভুলভাবে সামলানো হয়; একটি দিক বন্ধ করুন।
- **টুল কল একবারে একটি চলে।** একটি step-এর পরিচয় আসে step-গুলো যে ক্রমে পৌঁছানো হয় তা থেকে, তাই একসাথে নির্ধারিত টুল কল execution আবার চলার সময় একে অপরের checkpoint দাবি করতে পারত। একটি durable handler-এর ভেতরে রান ক্রমিক টুল চালানোয় বদলে যায়। এর বাইরে এজেন্ট তার কনফিগার করা সমান্তরালতা রাখে।
- **রানের রূপ বদলালে চলমান execution ভাঙে।** একটি আবার-চালু execution step নাম দিয়ে নয়, কাজগুলো যে ক্রমে পৌঁছানো হয় তা দিয়ে checkpoint মেলায়, তাই step-এর সংখ্যা বা ক্রম বদলায় এমন যেকোনো কিছু পুরনো কোডে শুরু হওয়া execution ভাঙে: একটি টুল বা MCP সার্ভার যোগ বা বাদ দেওয়া, একটি `metadata={'aws_lambda': False}` opt-out উল্টানো, বা একটি `event_stream_handler` যোগ করা (যা model step-কে `model.request_stream`-এ বদলায় আর handler step যোগ করে)। অমিল ধরা পড়ে না: একটি step আরেকটি step-এর লেখা ফল পায়, যা সাধারণত decode হতে ব্যর্থ হয় কিন্তু নিঃশব্দে ভুল ডেটাও ফেরত দিতে পারে। একটি নতুন published version-এ deploy করুন আর চলমান execution পুরনোটিতে শেষ হতে দিন।
- **Step-এর ফল SDK serializer-এ টিকতে হবে।** ফল Lambda SDK-এর serializer দিয়ে checkpoint হয়। টুলের ফল আগে Pydantic দিয়ে encode হয়, তাই `ToolReturn` আর `BinaryContent`-এর মতো কাঠামোবদ্ধ ফেরত যাওয়া-আসা করে; Pydantic serialize করতে পারে না এমন একটি মান পারে না।
- **একটি চলমান durable execution থেকে event বেরোতে পারে না।** `run_stream` আর `iter` handler-এর ভেতরে কাজ করে আর স্বাভাবিকভাবে checkpoint হয়, কিন্তু একটি durable execution শেষ হলে একটি একক মান ফেরত দেয়, তাই চলার সময় একজন caller-এর কাছে token stream করার কোনো চ্যানেল নেই। একটি `event_stream_handler` কাজ করে: মডেল event model step-এর ভেতরে লাইভ সামলানো হয় আর প্রতিটি এজেন্ট-স্তরের event নিজের step-এ checkpoint হয়।
- **একটি durable step-এর ভেতরে `ctx.enqueue()` পাওয়া যায় না**, একটি checkpoint করা টুল হোক বা একটি `event_stream_handler` (যা মডেল event-এর জন্য model step-এর ভেতরে আর এজেন্ট event-এর জন্য নিজের step-এ চলে), কারণ একটি আবার-চালু execution লেখা step আউটপুট পরিবেশন করে আর enqueue করা বার্তা হারিয়ে যেত। এর বদলে handler-স্তরের কোড থেকে enqueue করুন।
- **Checkpoint রানের ডেটা রাখে।** মডেল response, টুলের ফল, আর ব্যর্থ step-এর error বার্তা (যাতে একটি provider-এর error response body থাকতে পারে) durable কনফিগারেশনের `RetentionPeriodInDays` পর্যন্ত execution-এর durable state-এ সংরক্ষিত থাকে। execution history পড়তে পারা যে কেউ এগুলো পড়তে পারে, তাই সংবেদনশীল কাজের জন্য retention period ছোট রাখুন।
- **বাজেট।** একটি durable execution 3,000টি কাজ আর 100 MB মোট checkpoint করা state অনুমতি দেয়। একটি turn-এর খরচ একটি model step আর প্রতি টুল কলে একটি step, তাই কাজের বাজেট উদার, কিন্তু বড় টুলের ফল state বাজেট খায়: একটি blob-এর বদলে একটি রেফারেন্স (ধরুন একটি S3 key) ফেরত দিন।

/// warning | সাধারণ ভুল

একটি `charge_card` টুলে শুধু `step_semantics=AT_MOST_ONCE_PER_RETRY` দিয়ে ভাবা যে কার্ডে একবারই চার্জ হবে। ডিফল্ট retry policy ছয়বার পর্যন্ত চেষ্টা করে — প্রতিটি নতুন চেষ্টায় টুল আবার চলে। একবারই চালাতে হলে ওপরের উদাহরণের মতো `retry_strategy`-তেও `RetryPresets.none()` দিন, আর সাথে payment API-তে idempotency key ব্যবহার করুন।

///

## প্রতি-টুল কনফিগারেশন { #per-tool-configuration }

`aws_lambda` key-র নিচে টুলের metadata সেই টুলের step কনফিগার করে। এটি `StepConfig`-এর
`retry_strategy`, `step_semantics` আর `serdes` ফিল্ড নেয়:

```python
from aws_durable_execution_sdk_python.config import StepSemantics
from pydantic_ai.toolsets import FunctionToolset

toolset = FunctionToolset(id='billing')


@toolset.tool_plain(metadata={'aws_lambda': {'step_semantics': StepSemantics.AT_MOST_ONCE_PER_RETRY}})
def charge_card(amount: int) -> str:
    return f'charged {amount}'
```

`metadata={'aws_lambda': False}` একটি টুলকে checkpoint থেকে পুরোপুরি বের করে, তাই এটি প্রতিটি চেষ্টায় inline চলে। এটি ব্যবহার করুন সস্তা, side-effect-মুক্ত টুলের জন্য, যার ফল একটি checkpoint-এর যোগ্য নয়। MCP টুল বেরোতে পারে না, কারণ এগুলো এমন I/O করে যা execution আবার চলার সময় আবার চলা উচিত নয়।

`AWSLambdaDurability(step_config=...)` প্রতিটি step-এর মূল কনফিগারেশন সেট করে। প্রতি-টুল metadata এটি key ধরে ধরে override করে, তাই শুধু `step_semantics` সেট করা একটি টুল মূল `retry_strategy` রাখে।

## অন্য capability-র সাথে মিলন { #composition-with-other-capabilities }

`AWSLambdaDurability` নিজেকে সবচেয়ে ভেতরে রাখে, তাই একটি মডেল রিকোয়েস্টে অন্য যেকোনো capability-র অবদান durable step-এর ভেতরে আগেই প্রয়োগ হয়ে যায়। অন্য capability-র পাশে স্বাভাবিকভাবে এটি যুক্ত করুন।

## আরও পড়ুন { #further-reading }

- [AWS Lambda durable functions](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
- [AWS Durable Execution SDK for Python](https://github.com/aws/aws-durable-execution-sdk-python)
- [Pydantic AI durable execution](../durable_execution/overview.md)
- [AWS Lambda Durability source code](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/aws_lambda/)

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.aws_lambda.AWSLambdaDurability
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.aws_lambda.durable_agent_handler
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.aws_lambda.run_durable
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic_ai_harness.aws_lambda.AgentLoopGone
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `Agent(name=..., capabilities=[AWSLambdaDurability()])` আর handler `@durable_execution` + `durable_agent_handler` দিয়ে।
* শুধু `durable_agent_handler`/`run_durable` দিয়ে প্রবেশ করা রানই durable; `run_sync()` নিঃশব্দে non-durable।
* `@durable_execution` সবচেয়ে বাইরের decorator; একাধিক রান একটার পর একটা await করুন।
* step অন্তত-একবার আর ডিফল্টভাবে 6 বার পর্যন্ত retry — টুল idempotent রাখুন।
* টুল বা MCP যোগ/বাদ দিলে চলমান execution ভাঙে — নতুন published version-এ deploy করুন।
* বাজেট: 3,000 কাজ, 100 MB state; বড় ফলের বদলে S3 key ফেরত দিন।

///
