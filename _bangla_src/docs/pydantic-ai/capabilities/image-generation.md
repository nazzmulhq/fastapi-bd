
# ImageGeneration Capability { #imagegeneration-capability }

/// note | এই পেজে যা শিখবেন

* `ImageGeneration` capability দিয়ে এজেন্টকে কখন ছবি বানাবে তা নিজে ঠিক করতে দেওয়া।
* নেটিভ টুল বনাম সরাসরি image model (`local=ImageGenerator` / `fallback_image_model`) বনাম subagent বিকল্প।
* তৈরি ছবি কোথায় পাওয়া যায়, কোন সেটিং কোন পথে কাজ করে, আর agent spec-এ কনফিগারেশন।

///

[`ImageGeneration`][pydantic_ai.capabilities.ImageGeneration] [capability](overview.md) একটি এজেন্টকে কখন একটি ছবি তৈরি করবে তা ঠিক করতে দেয়। এটি কথোপকথনের মডেল provider-এর নেটিভ image-generation টুল পছন্দ করে আর সরাসরি image-generation API দিয়ে একটি নির্দিষ্ট image মডেলে ফিরে যেতে পারে, যার শুরু-থেকে-শেষ বিবরণ হলো [Image Generation](../image-generation.md)।

```python title="image_generation_capability.py"
from pydantic_ai import Agent, ImageGenerator
from pydantic_ai.capabilities import ImageGeneration
from pydantic_ai.images.openai import OpenAIImageGenerationSettings

image_generator = ImageGenerator(
    'openai:gpt-image-2.5-flare',
    settings=OpenAIImageGenerationSettings(
        openai_output_format='png',
        openai_quality='low',
    ),
)

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[
        ImageGeneration(
            native=False,
            local=image_generator,
            dimensions=(1024, 1024),
        )
    ],
)
```

`ImageGeneration()` ডিফল্টভাবে শুধু-নেটিভ। image API দিয়ে তৈরি করা একটি বিকল্প যোগ করুন — আরেকটি এজেন্ট তৈরি না করেই — দুটি ফিল্ডের একটি দিয়ে, আর কোনটি ব্যবহার করবেন তা আপনার কাছে যা আছে তার ওপর নির্ভর করে: একটি [`ImageGenerator`][pydantic_ai.images.ImageGenerator] নিজস্ব সেটিং বহন করে, তাই এটি আপনার দেওয়া অন্য বাস্তবায়নের পাশে `local`-এ যায়; একটি খালি [`ImageGenerationModel`][pydantic_ai.images.ImageGenerationModel] বা একটি `'provider:model'` নাম যায় `fallback_image_model`-এ। যেকোনোভাবে সরাসরি মডেল image API দিয়ে তৈরি করে, যেখানে `fallback_subagent_model` একটি subagent-এ একটি কথোপকথনের মডেল চালায়, আর এতে পৌঁছানো হয় যখন এজেন্টের মডেলের কোনো নেটিভ image generation নেই — বা `native=False`-সহ প্রতিটি কলে। `ImageGeneration`-এর কোনো বান্ডেল করা লোকাল কৌশল নেই, তাই `local` অন্যথায় আপনার নিজের একটি টুল নেয়।

/// info | এক নজরে: তিনটি পথ

| পথ | কীভাবে | কখন |
|----|--------|------|
| নেটিভ (ডিফল্ট) | মডেল নিজেই provider-এর image টুল ডাকে | মডেল নেটিভ image generation সমর্থন করলে |
| সরাসরি image model | `local=ImageGenerator(...)` বা `fallback_image_model='openai:gpt-image-...'` | মাপ/aspect ratio বা image মডেল আপনি ঠিক করতে চাইলে; একটি API কল, বাড়তি এজেন্ট নয় |
| Subagent | `fallback_subagent_model='...'` | নেটিভ টুলের আচরণ চান কিন্তু এজেন্টের মডেল তা পারে না |

///

দুটি ফিল্ড একটি image মডেলের নাম দেয় আর এরা বদলাবদলি যোগ্য নয়: `image_model` provider-এর নেটিভ টুল কনফিগার করে আর prefix-ছাড়া (`image_model='gpt-image-2.5-flare'`), যখন `fallback_image_model` সরাসরি মডেল বাছে আর এর provider বহন করে:

```python title="image_generation_routing.py"
from pydantic_ai import BinaryImage, ImageGenerator
from pydantic_ai.capabilities import ImageGeneration
from pydantic_ai.images.openai import OpenAIImageGenerationSettings

# Native preferred; use the direct model when native generation is unavailable
ImageGeneration(fallback_image_model='openai:gpt-image-2.5-flare')

# Always use the direct image API
ImageGeneration(native=False, fallback_image_model='google:gemini-3.1-flash-image')

# Supply reusable direct settings through an explicit generator, which goes on `local`
generator = ImageGenerator(
    'openai:gpt-image-2.5-flare',
    settings=OpenAIImageGenerationSettings(
        openai_output_format='jpeg',
        openai_quality='low',
    ),
)
ImageGeneration(native=False, local=generator, dimensions=(1280, 720))


# A custom callable or Tool of your own also goes on `local`
def my_image_tool(prompt: str) -> BinaryImage: ...


ImageGeneration(local=my_image_tool)
```

/// warning | সাধারণ ভুল

`image_model='openai:gpt-image-2.5-flare'` (prefix-সহ) বা `fallback_image_model='gpt-image-2.5-flare'` (prefix ছাড়া) লেখা। মনে রাখুন: `image_model` → **prefix ছাড়া** (নেটিভ টুলের জন্য), `fallback_image_model` → **`provider:` prefix-সহ** (সরাসরি মডেলের জন্য)।

///

বহনযোগ্য `dimensions` আর `aspect_ratio` capability সেটিং একটি স্পষ্ট generator-এর ডিফল্ট override করে। শুধু সরাসরি generator `dimensions` প্রয়োগ করতে পারে, আর শুধু এটিই সেই aspect ratio প্রয়োগ করতে পারে যা নেটিভ টুলের নেই, তাই যেকোনোটি নিশ্চিত করতে হলে `native=False` দিন: ডিফল্ট `native=True`-সহ নেটিভভাবে ছবি তৈরি করা একটি মডেল নেটিভ পথ নেয়, যেখানে এদের কোনো সমতুল্য নেই, আর রিকোয়েস্ট সতর্ক করে যে সেটিং প্রয়োগ হয়নি। একটি [`FallbackModel`][pydantic_ai.models.fallback.FallbackModel]-এর অধীনে, এর প্রতিটি মডেল এর নিজের profile যে পথ বাছে তা নেয়, আর যার পথ একটি সেটিং বাদ দেয়, যেমন সরাসরি generator-এ `quality` বা নেটিভ টুলে `dimensions`, সেটির নাম দিয়ে একটি সতর্কবার্তা পায়, [`TemporalDurability`][pydantic_ai.durable_exec.temporal.TemporalDurability]-সহ একটি workflow রানেও। একটি provider-এর নেটিভ টুল এমন একটি সেটিং কোনো সতর্কবার্তা ছাড়াই উপেক্ষা করে যার জন্য এর কোনো ফিল্ড নেই; দেখুন [Image Generation Tool](../native-tools.md#image-generation-tool)-এর নিচে provider সমর্থন টেবিল। একটি [`TemporalAgent`][pydantic_ai.durable_exec.temporal.TemporalAgent]-এর অধীনে যার বর্তমান মডেল একটি `FallbackModel`, বা আপনার নিজের এমন একটি মডেলের অধীনে যা নিজস্ব profile ছাড়া রিকোয়েস্ট পাঠায়, কোনো সতর্কবার্তা দেওয়া হয় না, কারণ কোনো পাবলিক কিছুই বলে না একটি রিকোয়েস্ট কোন মডেলে পৌঁছায়।
`quality` আর `output_format`-এর মতো শুধু-নেটিভ-টুল সেটিং একটি সরাসরি বিকল্পে প্রযোজ্য নয়; generator-এ এদের provider-prefix করা সমতুল্য কনফিগার করুন। `action='edit'` আর `image_model`-ও প্রযোজ্য নয়: সরাসরি বিকল্প `action='edit'`-এর জন্য [`UserError`][pydantic_ai.exceptions.UserError] তোলে, কারণ `generate_image` টুল কোনো রেফারেন্স ছবি পায় না, আর একটি সতর্কবার্তাসহ `image_model` উপেক্ষা করে, কারণ generator আগে থেকেই যে image মডেল দিয়ে তৈরি করে তার নাম দেয়।
`native=False` সরাসরি generator-কে একমাত্র পথ বানায়, তাই এ দুটোই তৈরির সময় পড়ে — বাদ পড়া সেটিং একটি সতর্কবার্তা হিসেবে আর `action='edit'` error হিসেবে; নেটিভ চালু থাকলে নেটিভ টুল তবুও এগুলো বহন করে, তাই এর বদলে সরাসরি generator-এ যাওয়া একটি রিকোয়েস্টই সতর্ক করে যে এগুলো প্রয়োগ হয়নি, আর `action='edit'`-এর জন্য exception তোলে। সরাসরি generator-কে ঠিক একটি তৈরি [`BinaryImage`][pydantic_ai.messages.BinaryImage] ফেরত দিতে হবে; একাধিক ছবি বা রেফারেন্স-ছবি সম্পাদনার জন্য সরাসরি [`ImageGenerator`][pydantic_ai.images.ImageGenerator] ব্যবহার করুন।

[`ImageGenerationTool`][pydantic_ai.native_tools.ImageGenerationTool] হলো নেটিভ বাস্তবায়ন (provider সমর্থন আর কনফিগারেশনের জন্য দেখুন [Image Generation Tool](../native-tools.md#image-generation-tool))। এর পূর্ণ provider-নেটিভ কনফিগারেশন দরকার হলে `native=ImageGenerationTool(...)` দিয়ে একটি স্পষ্ট instance দিন, বা [dynamic configuration](../native-tools.md#dynamic-configuration)-এর জন্য [`RunContext`][pydantic_ai.tools.RunContext] নিয়ে একটি `ImageGenerationTool` বা `None` ফেরত দেওয়া একটি callable। একটি callable প্রতিটি মডেল রিকোয়েস্টে মীমাংসা হয় আর `fallback_subagent_model` subagent চলার সময় আবার। দুটি মীমাংসাই একই `deps` পায়, কিন্তু subagent-এর নিজস্ব `RunContext` আছে; দুটোতে মিলতে হবে এমন কনফিগারেশনের জন্য `ctx.deps` ব্যবহার করুন। capability-স্তরের ফিল্ড subagent-এ factory-র ফল override করে।

একটি স্থির নেটিভ instance-এর `aspect_ratio` আপনার কনফিগার করা যে বিকল্পেই পৌঁছায় — `fallback_subagent_model` subagent বা সরাসরি generator — যখন একটি capability-স্তরের `aspect_ratio` এর ওপর অগ্রাধিকার পায়, যেমন পায় একটি capability-স্তরের `dimensions`, যা একই জ্যামিতি ভিন্নভাবে লেখা আর এর সাথে জোড়া যায় না। শুধু উত্তরাধিকার এভাবে ছাড় দেয়: capability-তেই `dimensions` আর `aspect_ratio` দুটো সেট করলে তৈরির সময় [`UserError`][pydantic_ai.exceptions.UserError] ওঠে, একবার একটি সরাসরি generator এগুলো প্রয়োগ করতে কনফিগার হলে।

Instrumentation প্রতি generator-এ, প্রতি এজেন্টে নয়: এজেন্ট-স্তরের [`Instrumentation`][pydantic_ai.capabilities.Instrumentation] capability সরাসরি generator-এ পৌঁছায় না, তাই generator নিজের না বহন করলে একটি রান কোনো `image_generation` span লেখে না। তৈরির সময় `instrument=` দিন, বা [`ImageGenerator.instrument_all()`][pydantic_ai.images.ImageGenerator.instrument_all] দিয়ে বৈশ্বিকভাবে চালু করুন:

```python title="instrumented_image_generation_capability.py"
from pydantic_ai import ImageGenerator
from pydantic_ai.capabilities import ImageGeneration

ImageGeneration(native=False, local=ImageGenerator('openai:gpt-image-2.5-flare', instrument=True))
```

ওই span কী বহন করে তা দেখুন [Instrumentation](../image-generation.md#instrumentation)-এ।

/// warning | Temporal-সহ durable execution

তৈরি ছবিকে Temporal-এর activity সীমা পার হতে হয়, যেখানে payload আকার-সীমা কাঁচা image bytes-এর জন্য মোটামুটি 1.5MB রাখে। বড় একটি ছবি একটি `UserError` দিয়ে ব্যর্থ হয় — একটি লোকাল বাস্তবায়ন থেকে এলে (একটি `local=` [`ImageGenerator`][pydantic_ai.images.ImageGenerator], একটি `fallback_image_model`, subagent বিকল্প, বা আপনার নিজের `local=` callable বা toolset) টুলের নাম দিয়ে, বা নেটিভ টুল এটি response-এ রাখলে মডেলের নাম দিয়ে। বিকল্পগুলোর জন্য দেখুন [Large Payloads](../durable_execution/temporal.md#large-payloads)।

///

## তৈরি ছবি পাওয়া { #getting-the-generated-image }

ছবিটি রানের message history-তে থাকে, অগত্যা এর চূড়ান্ত response-এ নয়। একটি এজেন্ট সাধারণত একটি ছবি তৈরির পর লেখায় উত্তর দেয়, তাই শেষ response এটি বহন না করলে [`result.response.images`][pydantic_ai.messages.ModelResponse.images] খালি। ছবি কোথায় পড়ে তা নির্ভর করে কোন পথ এটি তৈরি করেছে তার ওপর:

- নেটিভ টুল এটি রাখে যে মডেল response এটি তৈরি করেছে তাতে, [`ModelResponse.images`][pydantic_ai.messages.ModelResponse.images]-এ।
- একটি সরাসরি generator বা `fallback_subagent_model` subagent এটি `generate_image` টুল কল থেকে ফেরত দেয়, তাই এটি সেই কলের [`ToolReturnPart`][pydantic_ai.messages.ToolReturnPart]-এ, এর [`files`][pydantic_ai.messages.BaseToolReturnPart.files]-এর মধ্যে। আপনার নিজের একটি `local` টুল এর নিজের টুল নামে পাওয়া যায়; একটি [`BinaryImage`][pydantic_ai.messages.BinaryImage] ফেরত দিন যাতে ছবি এর `files`-এ পড়ে, কারণ কাঁচা `bytes` base64 লেখা হিসেবে মডেলে পৌঁছায়।

দুটোই সংগ্রহ করলে প্রতিটি রিকোয়েস্ট যে পথই নিক তা কভার হয়:

```python title="image_generation_retrieval.py"
from pydantic_ai import Agent, BinaryImage
from pydantic_ai.capabilities import ImageGeneration
from pydantic_ai.messages import ModelResponse, ToolReturnPart

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[ImageGeneration(fallback_image_model='openai:gpt-image-2.5-flare')],
)
result = agent.run_sync('Generate an illustration of a cafe, then write alt text for it.')

images: list[BinaryImage] = []
for message in result.all_messages():
    if isinstance(message, ModelResponse):
        images.extend(message.images)
    else:
        for part in message.parts:
            if isinstance(part, ToolReturnPart) and part.tool_name == 'generate_image':
                images.extend(file for file in part.files if isinstance(file, BinaryImage))

print(result.output)
#> A cozy corner cafe with warm light spilling onto the sidewalk.
print(len(images))
#> 1
```

/// warning | সাধারণ ভুল

`result.response.images[0]` দিয়ে ছবি নিতে গিয়ে `IndexError` পাওয়া। এজেন্ট ছবি বানানোর পর সাধারণত লেখা দিয়ে উত্তর দেয় ("এই নিন আপনার ছবি!"), তাই শেষ response-এ ছবি থাকে না। ওপরের উদাহরণের মতো পুরো message history থেকে ছবি সংগ্রহ করুন।

///

এর বদলে ছবিকে রানের আউটপুট বানাতে, `output_type=BinaryImage` সেট করুন (দেখুন [Image Output](../output.md#image-output))।
সেই সেটিং বিকল্পের বিপরীতে নয়, এজেন্টের মডেলের বিপরীতে যাচাই হয়: নিজে ছবি তৈরি করে না এমন একটি মডেল একটি বিকল্প এগুলো তৈরি করতে কনফিগার থাকলেও [`UserError`][pydantic_ai.exceptions.UserError] তোলে, তাই ওই মডেলে ইতিহাস থেকে ছবি সংগ্রহ করুন। যে মডেল পারে তাতে, এটি `native=False`-এর পাশেও সেই মডেলের নিজস্ব নেটিভ image generation চালু করে, তাই আউটপুট ছবি আপনার কনফিগার করা generator থেকে নয়, মডেল থেকে আসে।

## বিকল্পের অপশন { #fallback-options }

দুটি বিল্ট-ইন পদ্ধতি এমন একটি মডেল কভার করে যা নেটিভভাবে ছবি তৈরি করে না:

- **সরাসরি মডেল**: একটি [`ImageGenerator`][pydantic_ai.images.ImageGenerator]-সহ `local=`, বা একটি image মডেল নাম বা [`ImageGenerationModel`][pydantic_ai.images.ImageGenerationModel]-সহ `fallback_image_model=`। টুল কল একটি একক image API কল, কোনো বাড়তি এজেন্ট রান ছাড়া, আর এটি বহনযোগ্য `dimensions` আর `aspect_ratio` সেটিং প্রয়োগ করে। এটি ধরুন যখন জ্যামিতি বা image মডেলের পছন্দ আপনার।
- **Subagent**: নেটিভভাবে ছবি তৈরি করা একটি কথোপকথনের মডেলসহ `fallback_subagent_model=`। টুল কল একটি বাড়তি এজেন্ট চালায়, যার নেটিভ [`ImageGenerationTool`][pydantic_ai.native_tools.ImageGenerationTool] ছবি তৈরি করে। এটি ধরুন যখন আপনি সেই মডেলের নেটিভ টুলের আচরণ আর নেটিভ টুলের বহন করা সেটিং চান।

আপনার নিজের একটি `local=` callable, `Tool` বা toolset দুটোকেই আপনার লেখা একটি বাস্তবায়ন দিয়ে বদলায়। capability এতে এর কোনো image সেটিং দেয় না, তাই `native=False`-সহ, যেখানে এটিই একমাত্র বাস্তবায়ন, এর যেকোনোটি সেট করলে তৈরির সময় সতর্ক করে। তিনটি ফিল্ড বিকল্প: একাধিক দিলে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

/// note | `fallback_model` অবচিত

`fallback_model` হলো `fallback_subagent_model`-এর আগের নাম। এটি কাজ করতে থাকে, Python-এ আর একটি [agent spec](../agent-spec.md)-এ, আর সতর্ক করে; দুটি নাম একসাথে দেওয়া প্রত্যাখ্যাত: capability তৈরির সময় [`UserError`][pydantic_ai.exceptions.UserError], আর একটি spec লোড করার সময় spec loader এটিকে যে `ValueError`-এ মোড়ায়।

///

/// note | `None` ফেরত দেওয়া একটি factory

`fallback_subagent_model` ছাড়া, `None` সেই রিকোয়েস্টের জন্য নেটিভ টুল বাদ দেয়। `fallback_subagent_model`-সহ, subagent টুল উপলব্ধ থাকে, আর একে ডাকলে নিঃশব্দে ডিফল্ট image সেটিং ব্যবহার না করে [`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

///

/// note | Temporal-এর অধীনে গতিশীল কনফিগারেশন

subagent টুল কল একটি Temporal activity-র ভেতরে চলে, তাই এর `native=` factory সীমিত [`TemporalRunContext`][pydantic_ai.durable_exec.temporal.TemporalRunContext] পায়। `ctx.deps` সেই সীমা পার হয়; `ctx.messages`-এর মতো ফিল্ড হয় না। দেখুন [Agent Run Context and Dependencies](../durable_execution/temporal.md#agent-run-context-and-dependencies)।

///

subagent নেটিভ টুলের জ্যামিতির শব্দভাণ্ডারে কথা বলে। শুধু-সরাসরি মান, যেমন `dimensions`, যেকোনো GPT Image 2 আকার আর বাড়তি aspect ratio, একটি সতর্কবার্তাসহ উপেক্ষিত হয়। [direct geometry settings](../image-generation.md#output-geometry) প্রয়োগ করতে একটি সরাসরি generator-সহ `native=False` ব্যবহার করুন — `local=ImageGenerator(...)` বা `fallback_image_model='provider:image-model'`।

একটি provider কনটেন্ট-ব্লক যেকোনো লোকাল পথে একটি retry prompt হয়ে যায়, তাই যে মডেল prompt লিখেছে সে রান ব্যর্থ না করে এটি নতুন করে লেখার সুযোগ পায়। অন্য ব্যর্থতা দুটির মধ্যে ভিন্ন: subagent এর রান থেকে একটি [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior]-ও একটি retry prompt-এ বদলায়, যখন সরাসরি মডেল এটি তোলে। একা [`ImageGenerator`][pydantic_ai.images.ImageGenerator] ব্যবহার করা প্রভাবিত হয় না — এটি [`ContentFilterError`][pydantic_ai.exceptions.ContentFilterError] তোলে। সরাসরি API-র exception-এর জন্য দেখুন [error handling](../image-generation.md#error-handling)।

## Agent spec { #agent-specs }

`fallback_image_model='openai:gpt-image-2.5-flare'`-এর মতো সরাসরি মডেলের নাম JSON বা YAML agent spec-এ প্রকাশ করা যায়। Python constructor যে runtime অবজেক্ট নেয় — `fallback_image_model`-এ `ImageGenerationModel`, আর `local` যে `ImageGenerator`, `Tool`, toolset আর callable নেয় — serialize-যোগ্য নয় আর Python-এ কনফিগার করতে হবে। [`from_spec()`][pydantic_ai.capabilities.ImageGeneration.from_spec] একই সেটিং নাম প্রকাশ করে সেই serialize-যোগ্য উপসেট স্পষ্ট রাখে। `dimensions` JSON আর YAML-এ ব্যবহৃত দুই-আইটেমের array হিসেবে লিখুন; Pydantic AI এটি Python API-তে ব্যবহৃত `(width, height)` tuple-এ রূপান্তর করে:

```yaml
model: anthropic:claude-sonnet-5-5
capabilities:
  - ImageGeneration:
      native: false
      fallback_image_model: openai:gpt-image-2.5-flare
      dimensions: [1280, 720]
```

/// check | সংক্ষেপে মনে রাখুন

* `ImageGeneration()` ডিফল্টভাবে শুধু-নেটিভ; বিকল্প: `local=ImageGenerator(...)`, `fallback_image_model='provider:model'`, বা `fallback_subagent_model=`।
* `image_model` prefix ছাড়া (নেটিভ), `fallback_image_model` prefix-সহ (সরাসরি)।
* `dimensions`/বিশেষ aspect ratio নিশ্চিত করতে `native=False` + সরাসরি generator।
* তৈরি ছবি message history-তে খুঁজুন — `ModelResponse.images` বা `generate_image` টুলের `files`।
* সরাসরি generator-এর tracing-এর জন্য `instrument=` বা `ImageGenerator.instrument_all()`।

///
