# মাল্টিমোডাল ইনপুট (Multimodal Input) { #multimodal-input }

/// note | এই পেজে যা শিখবেন

* লেখার পাশাপাশি এজেন্টকে ছবি, অডিও, ভিডিও আর ডকুমেন্ট কীভাবে দেবেন: URL দিয়ে (`ImageUrl` ইত্যাদি) বা সরাসরি বাইট দিয়ে (`BinaryContent`)।
* কোন মডেল URL নিজে ডাউনলোড করে, আর কখন Pydantic AI ফাইলটি নামিয়ে বাইট পাঠায় (`force_download`)।
* provider-এ আগে আপলোড করা ফাইল `UploadedFile` দিয়ে কীভাবে ব্যবহার করবেন।
* বাইরের URL নিয়ে নিরাপত্তার সতর্কতা।

///

লেখার পাশাপাশি, এজেন্ট ছবি, অডিও, ভিডিও আর ডকুমেন্ট ইনপুট নিতে পারে, যদি মডেল তা সমর্থন করে।

/// tip | উদাহরণ দিয়ে বুঝি

"Multimodal" মানে একাধিক "মাধ্যম"। শুধু চিঠি লিখে প্রশ্ন না করে, আপনি চিঠির সাথে একটি ছবি, একটি ভয়েস রেকর্ডিং বা একটি PDF জুড়ে দিচ্ছেন: "এই ছবিতে কী আছে?", "এই চুক্তিপত্রের সারাংশ দাও"। এজেন্টের prompt তখন একটি স্ট্রিং না হয়ে একটি তালিকা হয়: `['প্রশ্নের লেখা', ImageUrl(...)]`।

///

## ছবির ইনপুট { #image-input }

/// info | মডেলের সমর্থন দেখে নিন

কিছু মডেল ছবির ইনপুট সমর্থন করে না। মডেলটি ছবির ইনপুট সমর্থন করে কিনা তা নিশ্চিত হতে অনুগ্রহ করে মডেলের ডকুমেন্টেশন দেখুন।

///

ছবির একটি সরাসরি URL থাকলে, [`ImageUrl`][pydantic_ai.ImageUrl] ব্যবহার করতে পারেন:

```python title="image_input.py"
from pydantic_ai import Agent, ImageUrl

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync(
    [
        'What company is this logo from?',
        ImageUrl(url='https://iili.io/3Hs4FMg.png'),
    ]
)
print(result.output)
#> This is the logo for Pydantic, a data validation and settings management library in Python.
```

ছবিটি আপনার কম্পিউটারে থাকলে, [`BinaryContent`][pydantic_ai.BinaryContent]-ও ব্যবহার করতে পারেন:

```python title="local_image_input.py"
import httpx

from pydantic_ai import Agent, BinaryContent

image_response = httpx.get('https://iili.io/3Hs4FMg.png')  # Pydantic logo

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync(
    [
        'What company is this logo from?',
        BinaryContent(data=image_response.content, media_type='image/png'),  # (1)!
    ]
)
print(result.output)
#> This is the logo for Pydantic, a data validation and settings management library in Python.
```

1. উদাহরণটি যাতে চালানো যায়, তাই আমরা ছবিটি ওয়েব থেকে নামাচ্ছি, তবে একটি লোকাল ফাইলের বিষয়বস্তু পড়তে `Path().read_bytes()`-ও ব্যবহার করতে পারেন।

/// info | কোনটি কখন?

* **URL-ভিত্তিক ক্লাস** (`ImageUrl`, `AudioUrl`, `VideoUrl`, `DocumentUrl`): ফাইলটি ইন্টারনেটে আছে। সাধারণত URL-টিই মডেল provider-কে পাঠানো হয়, আর সে নিজে ফাইলটি নামায়।
* **`BinaryContent`**: ফাইলের বাইট আপনার হাতে (ডিস্ক থেকে পড়া, ব্যবহারকারীর আপলোড)। সাথে `media_type` দিন, যেমন `'image/png'` বা `'application/pdf'`, যাতে মডেল জানে এটি কী ধরনের ফাইল।

///

## অডিও ইনপুট { #audio-input }

/// info | মডেলের সমর্থন দেখে নিন

কিছু মডেল অডিও ইনপুট সমর্থন করে না। মডেলটি অডিও ইনপুট সমর্থন করে কিনা তা নিশ্চিত হতে অনুগ্রহ করে মডেলের ডকুমেন্টেশন দেখুন।

///

অডিওর জন্য [`AudioUrl`][pydantic_ai.AudioUrl] বা [`BinaryContent`][pydantic_ai.BinaryContent] ব্যবহার করুন।

## ভিডিও ইনপুট { #video-input }

/// info | মডেলের সমর্থন দেখে নিন

কিছু মডেল ভিডিও ইনপুট সমর্থন করে না। মডেলটি ভিডিও ইনপুট সমর্থন করে কিনা তা নিশ্চিত হতে অনুগ্রহ করে মডেলের ডকুমেন্টেশন দেখুন।

///

ভিডিওর জন্য [`VideoUrl`][pydantic_ai.VideoUrl] বা [`BinaryContent`][pydantic_ai.BinaryContent] ব্যবহার করুন।

## ডকুমেন্ট ইনপুট { #document-input }

/// info | মডেলের সমর্থন দেখে নিন

কিছু মডেল ডকুমেন্ট ইনপুট সমর্থন করে না। মডেলটি ডকুমেন্ট ইনপুট সমর্থন করে কিনা তা নিশ্চিত হতে অনুগ্রহ করে মডেলের ডকুমেন্টেশন দেখুন।

///

ডকুমেন্টের জন্য [`DocumentUrl`][pydantic_ai.DocumentUrl] বা [`BinaryContent`][pydantic_ai.BinaryContent] ব্যবহার করুন।

ডকুমেন্টের একটি সরাসরি URL থাকলে, [`DocumentUrl`][pydantic_ai.DocumentUrl] ব্যবহার করতে পারেন:

```python title="document_input.py"
from pydantic_ai import Agent, DocumentUrl

agent = Agent(model='anthropic:claude-sonnet-5-5')
result = agent.run_sync(
    [
        'What is the main content of this document?',
        DocumentUrl(url='https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf'),
    ]
)
print(result.output)
#> This document is the technical report introducing Gemini 1.5, Google's latest large language model...
```

কোন কোন ডকুমেন্ট ফরম্যাট সমর্থিত, তা মডেলভেদে আলাদা।

ডকুমেন্টের ডেটা সরাসরি দিতে [`BinaryContent`][pydantic_ai.BinaryContent]-ও ব্যবহার করতে পারেন:

```python title="binary_content_input.py"
from pathlib import Path
from pydantic_ai import Agent, BinaryContent

pdf_path = Path('document.pdf')
agent = Agent(model='anthropic:claude-sonnet-5-5')
result = agent.run_sync(
    [
        'What is the main content of this document?',
        BinaryContent(data=pdf_path.read_bytes(), media_type='application/pdf'),
    ]
)
print(result.output)
#> The document discusses...
```

/// tip | পরামর্শ

`DocumentUrl` বা `BinaryContent` কোনোটিই আপনার কাজে না মিললে (যেমন মডেলটি
`DocumentUrl` সমর্থন করে না, বা আপনি একটি অ-বাইনারি ফরম্যাটে ডকুমেন্ট দিতে চান), তবুও আপনি
নিজে লেখাটি বের করে একটি স্ট্রিং বা [`TextContent`][pydantic_ai.TextContent] হিসেবে দিয়ে ডকুমেন্টের বিষয়বস্তু লেখার ইনপুট হিসেবে দিতে পারেন।

///


## লেখার ইনপুট { #text-input }

বাড়তি metadata-সহ লেখার ইনপুট দিতে [`TextContent`][pydantic_ai.TextContent] ব্যবহার করতে পারেন:

```python title="text_content_input.py"
from pydantic_ai import Agent, TextContent

agent = Agent(model='openai:gpt-6.1-sol')
result = agent.run_sync([
    'Summarize the key points from this text.',
    TextContent(
        content=(
            'Pydantic AI is a Python agent framework. '
            'It supports text, image, audio, video, and document input.'
        ),
        metadata={'source': 'pydantic_ai_inputs.txt'},
    ),
])
```

এটি লেখাটি একটি `str` হিসেবে দেওয়ার সমতুল্য, তবে এতে বাড়তি `metadata` রাখা যায়, যা আপনার এজেন্টের
লজিকে প্রোগ্রাম দিয়ে পড়া যায়।

/// note | মনে রাখুন

`content` ফিল্ডটি মডেলের ইনপুট হিসেবে ধরা হয়, কিন্তু `metadata` **মডেলকে পাঠানো হয় না**।
প্রোগ্রাম দিয়ে পড়ার জন্য এটি বার্তায় সংরক্ষিত থাকে।

///

/// tip | উদাহরণ দিয়ে বুঝি

`metadata` হলো খামের পেছনে লেখা নিজের নোট: "এই চিঠি ফাইল নং ৪২ থেকে এসেছে"। প্রাপক (মডেল) শুধু চিঠি (`content`) পড়ে, খামের নোট দেখে না; কিন্তু পরে ইতিহাস ঘাঁটার সময় আপনার কোড নোটটি পড়তে পারে।

///


## ব্যবহারকারীর দিকে ডাউনলোড বনাম সরাসরি ফাইল URL { #user-side-download-vs-direct-file-url }

`ImageUrl`, `AudioUrl`, `VideoUrl` বা `DocumentUrl`-এর একটি ব্যবহার করলে, Pydantic AI ডিফল্টভাবে URL-টি মডেল provider-কে পাঠায়, তাই ফাইলটি তাদের দিকে ডাউনলোড হয়।

ফাইল URL-এর সমর্থন ধরন আর provider অনুযায়ী আলাদা:

| মডেল | URL সরাসরি পাঠায় | নামিয়ে বাইট পাঠায় | সমর্থিত নয় |
|-------|-------------------|-------------------------|-------------|
| [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] | `ImageUrl` | `AudioUrl`, `DocumentUrl` | `VideoUrl`। `DocumentUrl` [`AzureProvider`-এ সমর্থিত নয়](models/azure.md#using-azure-with-the-responses-api), [`AlibabaProvider`-এও নয়](models/compatible-apis.md#alibaba-cloud-model-studio-dashscope) |
| [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] | `ImageUrl`, `AudioUrl`, `DocumentUrl` | — | `VideoUrl` |
| [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel] | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl` |
| [`GoogleModel`][pydantic_ai.models.google.GoogleModel] (Google Cloud) | সব ধরনের URL | — | — |
| [`GoogleModel`][pydantic_ai.models.google.GoogleModel] (Gemini API) | [YouTube](models/google.md#document-image-audio-and-video-input), [Files API](models/google.md#document-image-audio-and-video-input) | বাকি সব URL | — |
| [`XaiModel`][pydantic_ai.models.xai.XaiModel] | `ImageUrl` | `DocumentUrl` | `AudioUrl`, `VideoUrl` |
| [`MistralModel`][pydantic_ai.models.mistral.MistralModel] | `ImageUrl`, `DocumentUrl` (PDF) | `DocumentUrl` (`text/plain`) | `AudioUrl`, `VideoUrl`, `DocumentUrl` (PDF বা লেখা নয় এমন) |
| [`BedrockConverseModel`][pydantic_ai.models.bedrock.BedrockConverseModel] | S3 URL (`s3://`) | `ImageUrl`, `DocumentUrl`, `VideoUrl` | `AudioUrl` |
| [`OpenRouterModel`][pydantic_ai.models.openrouter.OpenRouterModel] | `ImageUrl`, `DocumentUrl`, `VideoUrl` | `AudioUrl` | — |

যে মডেল কোনো এক ধরনের ফাইল একেবারেই নেয় না, তাকেও [File Understanding](capabilities/file-understanding.md) capability দিয়ে সেই ফাইল দেওয়া যায়, যা আগে আরেকটি মডেলকে দিয়ে ফাইলটির লেখায় বর্ণনা করায়। এটি ছাড়া, মডেল নিতে পারে না এমন একটি ফাইল ব্যবহারকারীর prompt-এ থাকলে রিকোয়েস্ট ব্যর্থ হয়, অথচ একটি টুলের ফেরত দেওয়া এমন ফাইল [তার নাম লেখা একটি নোট দিয়ে বদলে যায়](tools-advanced.md#tool-return-file-provenance), তাই রান চলতে থাকে।

একটি মডেল API ফাইল URL সমর্থন করলেও ফাইলটি ডাউনলোড করতে না-ও পারে (যেমন crawling বা প্রবেশাধিকারের সীমাবদ্ধতার কারণে)। যেমন, Google Cloud-এ [`GoogleModel`][pydantic_ai.models.google.GoogleModel] YouTube ভিডিও URL প্রতি রিকোয়েস্টে একটিতে সীমিত রাখে।

এমন ক্ষেত্রে, URL অবজেক্টে `force_download` সেট করে Pydantic AI-কে বলতে পারেন ফাইলের বিষয়বস্তু নিজে ডাউনলোড করে URL-এর বদলে সেটি পাঠাতে:

```python title="force_download.py"
from pydantic_ai import ImageUrl, AudioUrl, VideoUrl, DocumentUrl

ImageUrl(url='https://example.com/image.png', force_download=True)
AudioUrl(url='https://example.com/audio.mp3', force_download=True)
VideoUrl(url='https://example.com/video.mp4', force_download=True)
DocumentUrl(url='https://example.com/doc.pdf', force_download=True)
```

/// warning | ফাইল URL-এর বিশ্বাসের মডেল (নিরাপত্তা)

URL যখন provider-এর কাছে পাঠানো হয়, provider সেগুলো নিজের credential দিয়ে আনে। `s3://` (Bedrock) আর `gs://` (Google Cloud)-এর মতো cloud-storage scheme-এ, সেই credential হলো আপনার সার্ভারের IAM role বা service account, তাই যে URL নিয়ন্ত্রণ করে, সে কার্যত নিয়ন্ত্রণ করে provider আপনার হয়ে কী পড়তে পারবে।

অবিশ্বস্ত ব্যবহারকারীর ইনপুট থেকে scheme আর পরিসর যাচাই না করে [`ImageUrl`][pydantic_ai.messages.ImageUrl], [`AudioUrl`][pydantic_ai.messages.AudioUrl], [`VideoUrl`][pydantic_ai.messages.VideoUrl] বা [`DocumentUrl`][pydantic_ai.messages.DocumentUrl] তৈরি করবেন না। frontend থেকে শুরু হওয়া cloud storage-এ আপলোডের জন্য, ফাইল URL অংশ তৈরির আগে সার্ভারে `s3://bucket/key`-এর মতো রেফারেন্সকে pre-signed `https://` URL-এ রূপান্তর করুন। `force_download=True` শুধু `http(s)://` URL-এ কাজ করে (এটি লাইব্রেরির HTTP client দিয়ে যায় আর SSRF সুরক্ষা প্রয়োগ করে); `s3://` আর `gs://`-এর মতো cloud-storage scheme লোকাল ডাউনলোডের পথে সমর্থিত নয়, আর যেমন আছে তেমন provider-এর কাছে পাঠানো হয়। `force_download='allow-local'` শুধু সার্ভারের নিজের লেখা URL-এ ব্যবহার করুন, কারণ এটি লোকাল নেটওয়ার্কে প্রবেশ অনুমোদন করে।

[UI adapter-গুলো](ui/overview.md) ক্লায়েন্টের পাঠানো বার্তায় [`UIAdapter.allowed_file_url_schemes`][pydantic_ai.ui.UIAdapter.allowed_file_url_schemes] আর [`UIAdapter.allowed_file_url_force_download`][pydantic_ai.ui.UIAdapter.allowed_file_url_force_download] দিয়ে নিজে থেকে এই পরিশোধন প্রয়োগ করে। আপনি একটি নিজের ক্লায়েন্ট API দিয়ে serialize করা `message_history` নিলে, সেই ইতিহাস এজেন্টকে দেওয়ার আগে [`sanitize_messages`][pydantic_ai.messages.sanitize_messages] ব্যবহার করুন।

///

/// tip | উদাহরণ দিয়ে বুঝি

`s3://` URL পাঠানো মানে provider-এর হাতে আপনার গুদামের চাবি দিয়ে বলা "এই তাকের বাক্সটি নিয়ে নাও"। ব্যবহারকারী যদি নিজেই "তাক নম্বর" লিখে দিতে পারে, সে অন্য তাকের (অন্য গ্রাহকের) বাক্সও চেয়ে বসতে পারে। তাই অচেনা ইনপুট থেকে সরাসরি URL বানাবেন না; সার্ভারে যাচাই করে সীমিত মেয়াদের pre-signed লিংক দিন।

///

## আপলোড করা ফাইল { #uploaded-files }

কিছু মডেল provider-এর নিজস্ব ফাইল স্টোরেজ API আছে, যেখানে ফাইল আপলোড করে ID বা URL দিয়ে সেগুলোর রেফারেন্স দেওয়া যায়।

একটি provider-এর ফাইল স্টোরেজ API-তে আপলোড করা ফাইলের রেফারেন্স দিতে [`UploadedFile`][pydantic_ai.messages.UploadedFile] ব্যবহার করুন।

/// tip | পরামর্শ

যেসব provider একটি ফাইল URL ফেরত দেয় (যেমন Google Files API বা Bedrock-এর জন্য S3 URL), সেগুলোতে আপনি সরাসরি [`DocumentUrl`][pydantic_ai.messages.DocumentUrl], [`ImageUrl`][pydantic_ai.messages.ImageUrl] বা [`VideoUrl`][pydantic_ai.messages.VideoUrl]-ও ব্যবহার করতে পারেন। তবে provider-জুড়ে একটি একীভূত API আর সামঞ্জস্যপূর্ণ provider নাম যাচাইয়ের জন্য আমরা `UploadedFile` ব্যবহারের পরামর্শ দিই।

///

/// info | কেন আগে আপলোড?

একটি বড় PDF প্রতিটি প্রশ্নের সাথে বারবার পাঠালে সময় আর ব্যান্ডউইথ দুটোই নষ্ট। একবার provider-এ আপলোড করে একটি `file_id` পেলে, পরের প্রতিটি রিকোয়েস্টে শুধু সেই ছোট ID পাঠালেই চলে।

///

### সমর্থিত মডেল { #supported-models }

| মডেল | সমর্থন |
|-------|---------|
| [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel] | ✅ [Anthropic Files API](https://docs.anthropic.com/en/docs/build-with-claude/files) দিয়ে |
| [`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] | ✅ [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) দিয়ে |
| [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] | ✅ [OpenAI Files API](https://platform.openai.com/docs/api-reference/files) দিয়ে |
| [`GoogleModel`][pydantic_ai.models.google.GoogleModel] | ✅ [Google Files API](https://ai.google.dev/gemini-api/docs/files) দিয়ে |
| [`BedrockConverseModel`][pydantic_ai.models.bedrock.BedrockConverseModel] | ✅ S3 URL (`s3://bucket/key`) দিয়ে |
| [`XaiModel`][pydantic_ai.models.xai.XaiModel] | ✅ [xAI Files API](https://docs.x.ai/docs/guides/files) দিয়ে |
| অন্য মডেল | ❌ সমর্থিত নয় |

### Provider নাম বাধ্যতামূলক { #provider-name-requirement }

[`UploadedFile`][pydantic_ai.messages.UploadedFile] ব্যবহার করলে `provider_name` সেট করতেই হবে। আপলোড করা ফাইল যে সিস্টেমে আপলোড হয়েছে শুধু সেখানকারই, আর এক provider থেকে আরেকটিতে স্থানান্তরযোগ্য নয়। একটি `UploadedFile` থাকা বার্তা ভিন্ন provider-এর সাথে ব্যবহারের চেষ্টা করলে একটি এরর হবে।

/// tip | provider নাম পাওয়া

সঠিক provider নাম গতিশীলভাবে পেতে [`model.system`][pydantic_ai.models.Model.system] ব্যবহার করুন। এতে provider নাম বদলালেও আপনার কোড ঠিকঠাক কাজ করে। নিচের সব উদাহরণ এই ধরন দেখায়।

///

আপনি যদি এজেন্টের লজিকে বহনযোগ্যতা আনতে চান, যাতে একই prompt ইতিহাস ভিন্ন ভিন্ন provider backend-এ কাজ করে, তাহলে একটি [history processor](message-history.md#processing-message-history) দিয়ে সমর্থন না করা provider-এ পাঠানোর আগে বার্তা থেকে `UploadedFile` অংশ সরাতে বা নতুন করে লিখতে পারেন। মনে রাখবেন, `UploadedFile` সরিয়ে দিলে মডেল বিভ্রান্ত হতে পারে, বিশেষ করে লেখায় যদি সেই ফাইলগুলোর উল্লেখ থেকে যায়।

### Media type অনুমান { #media-type-inference }

[`UploadedFile`][pydantic_ai.messages.UploadedFile]-এর জন্য `media_type` প্যারামিটার ঐচ্ছিক। দেওয়া না থাকলে, Pydantic AI এটি `file_id` থেকে অনুমানের চেষ্টা করবে:

1. `file_id` যদি চেনা যায় এমন ফাইল extension-সহ (যেমন `.pdf`, `.png`) একটি URL বা path হয়, media type নিজে থেকে অনুমান হয়
2. অস্বচ্ছ ফাইল ID-র জন্য (যেমন `'file-abc123'`), media type ডিফল্ট হয় `'application/octet-stream'`

/// tip | পরামর্শ

`media_type` ঐচ্ছিক হলেও, জানা থাকলে আমরা এটি স্পষ্টভাবে দেওয়ার পরামর্শ দিই, যাতে মডেল provider ঠিকভাবে সামলায়।

///

### Anthropic { #anthropic }

ফাইল আপলোড করতে [Anthropic Files API ডক](https://docs.anthropic.com/en/docs/build-with-claude/files) অনুসরণ করুন। ভেতরের Anthropic client `provider.client` দিয়ে পাবেন।

/// note | Beta সুবিধা

Anthropic Files API বর্তমানে beta-তে। একটি রিকোয়েস্টে Anthropic-এর [`UploadedFile`][pydantic_ai.messages.UploadedFile] থাকলে `AnthropicModel` প্রয়োজনীয় `anthropic-beta: files-api-2025-04-14` header নিজে থেকে যোগ করে, তাই আপনাকে নিজে তা সেট করতে হয় না।

///

```python title="uploaded_file_anthropic.py"
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider


async def main():
    provider = AnthropicProvider()
    model = AnthropicModel('claude-sonnet-5-5', provider=provider)

    # Upload a file using the provider's client (Anthropic client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.beta.files.upload(file=f)

    # Reference the uploaded file; the beta header is added automatically
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...


asyncio.run(main())
```

### OpenAI { #openai }

ফাইল আপলোড করতে [OpenAI Files API ডক](https://platform.openai.com/docs/api-reference/files/create) অনুসরণ করুন। ভেতরের OpenAI client `provider.client` দিয়ে পাবেন।

```python title="uploaded_file_openai.py"
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


async def main():
    provider = OpenAIProvider()
    model = OpenAIChatModel('gpt-6.1-sol', provider=provider)

    # Upload a file using the provider's client (OpenAI client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.files.create(file=f, purpose='user_data')

    # Reference the uploaded file
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...


asyncio.run(main())
```

/// note | আপলোড করা ছবির রেফারেন্স

[`OpenAIChatModel`][pydantic_ai.models.openai.OpenAIChatModel] শুধু আপলোড করা *ডকুমেন্টের* রেফারেন্স `file_id` দিয়ে দিতে পারে। একটি আপলোড করা ছবির (`image/*` media type) রেফারেন্স দিলে একটি [`UserError`][pydantic_ai.exceptions.UserError] ওঠে, কারণ Chat Completions API ছবির অংশে `file_id` নেয় না। ছবির জন্য [`ImageUrl`][pydantic_ai.messages.ImageUrl] বা [`BinaryContent`][pydantic_ai.messages.BinaryContent] ব্যবহার করুন, অথবা [`OpenAIResponsesModel`][pydantic_ai.models.openai.OpenAIResponsesModel] ব্যবহার করুন, যা আপলোড করা ছবি সমর্থন করে।

`OpenAIResponsesModel`-এ, `UploadedFile`-এ `vendor_metadata={'detail': 'high'}` (বা `'low'`) দিয়ে ছবির [detail level](https://platform.openai.com/docs/guides/images-vision) নিয়ন্ত্রণ করুন; ডিফল্ট `'auto'`।
`OpenAIChatModel`, `GroqModel`, `MistralModel` আর `XaiModel`-এ, [`ImageUrl`][pydantic_ai.messages.ImageUrl] বা [`BinaryContent`][pydantic_ai.messages.BinaryContent]-এ `vendor_metadata={'detail': 'high'}` (বা `'low'`) দিয়ে ছবির detail level নিয়ন্ত্রণ করুন; ডিফল্ট `'auto'`।

///

### Google { #google }

ফাইল আপলোড করতে [Google Files API ডক](https://ai.google.dev/gemini-api/docs/files) অনুসরণ করুন। ভেতরের Google GenAI client `provider.client` দিয়ে পাবেন।

```python title="uploaded_file_google.py"
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider


async def main():
    provider = GoogleProvider()
    model = GoogleModel('gemini-3.8-flash', provider=provider)

    # Upload a file using the provider's client (Google GenAI client)
    with open('document.pdf', 'rb') as f:
        file = await provider.client.aio.files.upload(file=f)
        assert file.uri is not None

    # Reference the uploaded file by URI (media_type is optional for Google)
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=file.uri, media_type=file.mime_type, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...


asyncio.run(main())
```

### Bedrock (S3) { #bedrock-s3 }

Bedrock-এর জন্য ফাইল আলাদাভাবে S3-এ আপলোড করতে হয় (যেমন [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html) দিয়ে)। ধরে নেওয়া role-এর bucket-এ `s3:GetObject` অনুমতি থাকতে হবে।

/// note | `media_type` লাগতে পারে

ফাইলের extension অস্পষ্ট বা অনুপস্থিত হলে Bedrock-এ `media_type` লাগে। `.pdf`, `.png` ইত্যাদির মতো স্পষ্ট extension-সহ S3 URL-এ এটি নিজে থেকে অনুমান করা যায়।

///

```python title="uploaded_file_bedrock.py"
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.bedrock import BedrockConverseModel


async def main():
    model = BedrockConverseModel('global.anthropic.claude-sonnet-5-5')

    agent = Agent(model)
    result = await agent.run([
        'Summarize this document',
        UploadedFile(
            file_id='s3://my-bucket/document.pdf',
            provider_name=model.system,  # 'bedrock'
            media_type='application/pdf',  # Optional for .pdf, but recommended
        ),
    ])
    print(result.output)
    #> The document discusses the main topics and key findings...


asyncio.run(main())
```

/// note | মনে রাখুন

bucket-টি রিকোয়েস্ট করা account-এর মালিকানায় না থাকলে, চাইলে একটি `bucketOwner` query প্যারামিটার দিতে পারেন: `s3://my-bucket/document.pdf?bucketOwner=123456789012`

///

### xAI { #xai }

ফাইল আপলোড করতে [xAI Files API ডক](https://docs.x.ai/docs/guides/files) অনুসরণ করুন। ভেতরের xAI client `provider.client` দিয়ে পাবেন।

```python title="uploaded_file_xai.py"
import asyncio

from pydantic_ai import Agent, UploadedFile
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.xai import XaiProvider


async def main():
    provider = XaiProvider()
    model = XaiModel('grok-4.7', provider=provider)

    # Upload a file using the provider's client (xAI client)
    with open('document.pdf', 'rb') as f:
        uploaded_file = await provider.client.files.upload(f, filename='document.pdf')

    # Reference the uploaded file
    agent = Agent(model)
    result = await agent.run(
        [
            'Summarize this document',
            UploadedFile(file_id=uploaded_file.id, provider_name=model.system),
        ]
    )
    print(result.output)
    #> The document discusses the main topics and key findings...


asyncio.run(main())
```

/// check | সংক্ষেপে মনে রাখুন

* prompt একটি তালিকা হতে পারে: লেখা + `ImageUrl`/`AudioUrl`/`VideoUrl`/`DocumentUrl` বা `BinaryContent(data=..., media_type=...)`।
* সব মডেল সব ধরনের ফাইল নেয় না; ওপরের টেবিল দেখুন, দরকারে [File Understanding](capabilities/file-understanding.md)।
* provider URL নামাতে না পারলে `force_download=True`; অবিশ্বস্ত ইনপুট থেকে URL বানাবেন না।
* `TextContent`-এর `metadata` মডেলে যায় না, শুধু আপনার কোডের জন্য।
* আগে আপলোড করা ফাইলে `UploadedFile(file_id=..., provider_name=model.system)`; ফাইল এক provider-এরই।

///
