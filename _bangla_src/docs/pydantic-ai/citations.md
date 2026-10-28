# Citation (তথ্যসূত্র) { #citations }

/// note | এই পেজে যা শিখবেন

* Citation কী: মডেলের উত্তরের কোন অংশের পেছনে কোন উৎস (ওয়েব পেজ, ডকুমেন্ট, ফাইল) আছে।
* `Citations()` capability দিয়ে citation চাওয়া আর `TextPart.citations` থেকে পড়া।
* গোছানো আউটপুট আর টুলের সাথে citation-এর সীমাবদ্ধতা।
* বার্তার ইতিহাসে citation, আর কোন provider কী সমর্থন করে।

///

একটি citation আপনাকে বলে মডেলের উত্তরের একটি অংশের পেছনে কোন উৎস আছে: সে যে ওয়েব পেজ সার্চ বা fetch করেছে, আপনার পাঠানো একটি ডকুমেন্ট, বা একটি provider-এর ফাইল স্টোরের একটি ফাইল।

Pydantic AI citation রাখে [`TextPart.citations`][pydantic_ai.messages.TextPart.citations]-এ, প্রতিটি provider-এর জন্য একই
আকারে। মডেলের লেখা কখনো বদলানো হয় না।

/// tip | উদাহরণ দিয়ে বুঝি

একটি গবেষণা-প্রবন্ধের পাদটীকা ভাবুন: "পৃথিবীর জনসংখ্যা ৮০০ কোটি¹" — আর নিচে ¹ লেখা "জাতিসংঘ রিপোর্ট, ২০২৩"। Citation হলো এজেন্টের উত্তরের সেই পাদটীকা: কোন বাক্য কোন সূত্র থেকে এসেছে। এতে ব্যবহারকারী উত্তর যাচাই করতে পারেন, আর মডেল বানিয়ে বলছে কিনা ধরা সহজ হয়।

///

## Citation চালু করা { #turning-citations-on }

বেশিরভাগ মডেল সার্চ টুলের ফল না চাইতেই উল্লেখ করে, যেমন [web search](native-tools.md#web-search-tool),
[web fetch](native-tools.md#web-fetch-tool) আর [file search](native-tools.md#file-search-tool)। কিছু provider শুধু চাইলে আপনার পাঠানো ডকুমেন্ট উল্লেখ করে, বা xAI-তে যেকোনো উৎস। তাদের কাছে চাইতে [`Citations`][pydantic_ai.capabilities.Citations]
capability যোগ করুন:

```python title="document_citations.py"
from pydantic_ai import Agent, BinaryContent, TextPart
from pydantic_ai.capabilities import Citations

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[Citations()])
result = agent.run_sync(
    [
        'How long do customers have to return an item?',
        BinaryContent(data=b'Items may be returned within 30 days.', media_type='text/plain'),
    ]
)
for part in result.response.parts:
    if isinstance(part, TextPart):
        for citation in part.citations or []:
            print(citation.sources[0].excerpts)
            #> ['Items may be returned within 30 days.']
```

মডেল তবুও citation ছাড়া উত্তর দিতে পারে।

## Citation পড়া { #reading-citations }

একটি [`Citation`][pydantic_ai.messages.Citation]-এ আছে:

- `sources`: তথ্য কোথা থেকে এসেছে। একটি [`WebCitationSource`][pydantic_ai.messages.WebCitationSource]-এ থাকে
  পেজের `url`। একটি [`DocumentCitationSource`][pydantic_ai.messages.DocumentCitationSource] হলো অন্য যেকোনো উৎস। এর
  `document_id` হলো provider-এর ID, ফাইলের path নয়, আর prompt-এ আপনার পাঠানো একটি ডকুমেন্টের কোনো ID বা শিরোনাম না-ও থাকতে পারে।
  প্রতিটি উৎসের `excerpts` হলো provider প্রমাণ হিসেবে যে অংশগুলো উদ্ধৃত করেছে। একটি citation-এ একাধিক উৎস মানে
  provider সেগুলো একসাথে জড়ো করেছে; সেগুলো একে অপরকে নকল করতে পারে, তাই এদের সংখ্যা লেখাটি কতটা ভালোভাবে
  সমর্থিত তা নিয়ে কিছুই বলে না।
- `anchor`: লেখার যে অংশ নিয়ে citation, অক্ষরের অবস্থান হিসেবে: `part.content[anchor.start:anchor.end]`।
    - একটি [`ContentCitationAnchor`][pydantic_ai.messages.ContentCitationAnchor] উৎস যে লেখা সমর্থন করে তা ঢাকে।
      কিছু provider, যেমন Anthropic, পুরো লেখার অংশ উল্লেখ করে, তাই anchor পুরো অংশ ঢাকে।
    - একটি [`MarkerCitationAnchor`][pydantic_ai.messages.MarkerCitationAnchor] মডেলের লেখা একটি চিহ্ন ঢাকে, যেমন
      `[1]` বা একটি লিংক।
    - `None` মানে provider বলেনি citation কোন লেখা নিয়ে। যেমন, OpenAI-এর ফাইল citation শুধু
      একটি অবস্থান দেয়, যা অংশের `provider_details['citations']`-এ রাখা হয়।

```python title="render_citations.py"
from pydantic_ai import (
    Agent,
    ContentCitationAnchor,
    MarkerCitationAnchor,
    TextPart,
    WebCitationSource,
)
from pydantic_ai.capabilities import NativeTool
from pydantic_ai.native_tools import WebSearchTool

agent = Agent('openai:gpt-6.1-sol', capabilities=[NativeTool(WebSearchTool())])
result = agent.run_sync('What is the tallest mountain in Alberta?')

for part in result.response.parts:
    if isinstance(part, TextPart):
        for citation in part.citations or []:
            anchor = citation.anchor
            if isinstance(anchor, ContentCitationAnchor):
                location = f'supports {part.content[anchor.start : anchor.end]!r}'
            elif isinstance(anchor, MarkerCitationAnchor):
                location = f'marker {part.content[anchor.start : anchor.end]!r}'
            else:
                location = 'somewhere in the text'

            for source in citation.sources:
                if isinstance(source, WebCitationSource):
                    label = source.title or source.url
                else:
                    label = source.title or source.document_id or 'document'
                print(location, label)
                #> marker '([example.com](https://example.com))' Mount Columbia
```

/// info | কোডটি সহজ ভাষায়

উত্তরের প্রতিটি `TextPart`-এর ওপর ঘুরে, তার প্রতিটি citation-এর জন্য `anchor` দিয়ে লেখার সংশ্লিষ্ট টুকরো (`part.content[anchor.start:anchor.end]`) বের করা হয়, আর পাশে উৎসের URL বা ডকুমেন্টের নাম দেখানো হয়। এভাবেই UI-তে "এই বাক্য → এই লিংক" দেখাতে পারবেন।

///

একই উত্তর বিভিন্ন provider থেকে এমন দেখায়:

```python
from pydantic_ai import (
    Citation,
    ContentCitationAnchor,
    MarkerCitationAnchor,
    TextPart,
    WebCitationSource,
)

# Google selects the supported text, and here lists both sources for it. Anthropic's anchor covers the whole part.
TextPart(
    'Pydantic validates data.',
    citations=[
        Citation(
            sources=[WebCitationSource('https://a.example'), WebCitationSource('https://b.example')],
            anchor=ContentCitationAnchor(start=0, end=24),
        )
    ],
)

# OpenAI selects the link the model wrote.
TextPart(
    'Pydantic validates data. ([example.com](https://example.com))',
    citations=[
        Citation(
            sources=[WebCitationSource('https://example.com')],
            anchor=MarkerCitationAnchor(start=25, end=61),
        )
    ],
)

# Some providers give no position in the text.
TextPart(
    'Pydantic validates data.',
    citations=[Citation(sources=[WebCitationSource('https://example.com')])],
)
```

## Citation, টুল আর গোছানো আউটপুট { #citations-tools-and-structured-output }

Citation লেখার সাথে যুক্ত থাকে, তাই এগুলো শুধু তখনই ফেরত আসে যখন আপনার এজেন্টের আউটপুট লেখা। [গোছানো আউটপুটে](output.md),
`str`-কে একটি গোছানো টাইপের সাথে মেলানো একটি আউটপুট টাইপসহ, যেমন
`[str, Answer]`, উত্তরটি টুল কলের আর্গুমেন্ট হিসেবে ফেরত আসে, যা citation বহন করতে পারে না।

Anthropic-এ, আর Anthropic মডেলসহ Bedrock-এ, মডেল তার citation markup লেখা নয় এমন যেকোনো কিছুতে লিখে ফেলে,
যেমন `summary='(cite index="1-1">Items may be returned within 30 days.</cite>'`। তাই
`Citations()`-সহ:

- **গোছানো আউটপুট:** মডেলের কাছে citation চাওয়া হয় না, তাই আপনার ফিল্ড পরিষ্কার থাকে আর কোনো ডকুমেন্ট
  citation পান না। (Anthropic `NativeOutput`-এর সাথে citation প্রত্যাখ্যান করে।)
- **একটি ডকুমেন্ট বা Web Fetch-সহ রিকোয়েস্টে [`tool_choice`](tools-advanced.md#dynamic-tool-choice-via-capabilities) দিয়ে বাধ্য করা একটি টুল কল:**
  সেই রিকোয়েস্ট পাঠানোর আগেই একটি `UserError` তোলে, কারণ markup প্রতিবার
  টুলের আর্গুমেন্টে পৌঁছায়। যে রান পরের কোনো ধাপে একটি টুল বাধ্য করে, সে সেই ধাপে ব্যর্থ হয়।
- **মডেল নিজে যে টুল ডাকতে বেছে নেয়:** citation চালু থাকে, কিন্তু ছোট মডেল প্রায়ই markup টুলের
  আর্গুমেন্টে লিখে ফেলে, আমাদের টেস্টে প্রায় অর্ধেক সময়, যখন আর্গুমেন্ট একটি ডকুমেন্টের সারাংশ করে। যে আর্গুমেন্ট
  মানুষের সামনে যায় তা পরীক্ষা করুন, যেমন একটি ইমেইলের বিষয়বস্তু, বা সেই এজেন্টগুলোতে `Citations()` বন্ধ রাখুন।

xAI-তে, citation চালু থাকলে মডেল আউটপুট টুল না ডেকে লেখায় উত্তর দেয়, তাই গোছানো আউটপুটে
`Citations()` সেগুলো চায়ও না। টুল স্বাভাবিকভাবে কাজ করে।

Citation দরকার হলে, লেখার আউটপুট ব্যবহার করুন।

Anthropic সবসময় [web search](native-tools.md#web-search-tool) ফল উল্লেখ করে, তাই web search-এ markup
`Citations()` ছাড়াও গোছানো আউটপুটে দেখা দিতে পারে। [web fetch](native-tools.md#web-fetch-tool)-এও একই কথা,
যখন টুলে `enable_citations=True` সেট করেন।

অন্য provider-এ, `Citations()` গোছানো আউটপুটে কোনো প্রভাব ফেলে না। `NativeOutput` বা `PromptedOutput`-এ
আউটপুট JSON লেখা, তাই web search citation এতে ফেরত আসতে পারে, অবস্থান আপনার ফিল্ডে নয়,
JSON লেখায়।

/// warning | সাধারণ ভুল

`output_type=Answer` (একটি Pydantic মডেল) দিয়ে citation আশা করা। গোছানো আউটপুট টুলের আর্গুমেন্ট হয়ে আসে, আর সেখানে citation থাকে না। citation লাগলে `output_type=str` রাখুন (ডিফল্ট)।

///

## জেনে রাখা ভালো { #good-to-know }

- stream করার সময়, citation তাদের লেখার পরে আসতে পারে: Anthropic, Bedrock আর
  OpenAI Responses-এ প্রতিটি লেখার অংশের শেষে, আর Google আর OpenAI Chat-এ উত্তরের শেষে। চূড়ান্ত উত্তর থেকে citation পড়ুন।
  xAI-তে এগুলো উত্তরের শেষে শেষ লেখার অংশে যায়, তাই একটি stream করা উত্তরের পরে একটি টুল কল এলে
  কোনোটিই পায় না।
- [AG-UI adapter](ui/ag-ui.md) frontend-এ citation পাঠায় না।
- Citation-এর URL, শিরোনাম আর উদ্ধৃতি উৎস থেকেই আসে, আর উদ্ধৃতিতে আপনার নিজের
  ডকুমেন্টের লেখা থাকতে পারে। লগ করার বা ব্যবহারকারীকে দেখানোর আগে সেগুলো পরীক্ষা করুন।
- একটি citation নিয়ে provider আর যা ফেরত দিয়েছে, যেমন Google-এর confidence score, provider যেভাবে
  পাঠিয়েছে সেভাবে অংশের `provider_details['citations']`-এ রাখা হয়। এর আকার provider-এর, আর বদলাতে পারে।

## বার্তার ইতিহাসে citation { #citations-in-message-history }

[সংরক্ষিত বার্তার ইতিহাস](message-history.md#storing-and-loading-messages-to-json) প্রতিটি citation রাখে। একই provider-কে
এটি ফেরত পাঠালে, এই citation-গুলো লেখার সাথে যায়, তাই মডেল জানে তার আগের বক্তব্যগুলো কোথা থেকে
এসেছিল:

| Provider | যে citation ফেরত পাঠানো হয় |
| --- | --- |
| Anthropic | Web search citation, web search নেই এমন ক্লায়েন্ট ছাড়া, যেমন Bedrock |
| OpenAI Responses | Web আর ফাইল citation, যখন বার্তার ID পাঠানো হয়, যা reasoning মডেলের ডিফল্ট। দেখুন [`openai_send_reasoning_ids`][pydantic_ai.models.openai.OpenAIResponsesModelSettings.openai_send_reasoning_ids] |

বাকি প্রতিটি citation সংরক্ষিত বার্তায় থাকে, কিন্তু তার লেখা সাধারণ লেখা হিসেবে ফেরত যায়: ডকুমেন্ট আর fetch করা পেজের
citation, OpenAI Chat-এর citation, আর ভিন্ন provider-কে পাঠানো ইতিহাস। একইভাবে যায় এমন একটি citation, যার লেখা
বদলানো হয়েছে বা অন্য লেখার সাথে জোড়া হয়েছে।

একটি সংরক্ষিত উত্তরের লেখা সম্পাদনা করলে, সেই অংশের `citations` আর তার `provider_details['citations']`-ও মুছে দিন।
যে citation-এর লেখা স্পষ্টভাবে বদলেছে Pydantic AI সেগুলো বাদ দেয়, কিন্তু একই দৈর্ঘ্য রাখা একটি সম্পাদনা নজর এড়িয়ে যেতে পারে।

অপরিবর্তিত ফেরত পাঠানো ইতিহাস প্রতিটি দফায় একইভাবে যায়, তাই prompt caching কাজ করতে থাকে।

[Vercel AI adapter](ui/vercel-ai.md#citations) frontend বার্তার ইতিহাস ধরে রাখলে citation রাখে।

/// warning | মডেল হয়তো উৎসটি দেখতে পায় না

একজন ব্যবহারকারী পরে "উৎস [1]" নিয়ে জিজ্ঞেস করলে, মডেল `[1]` দেখতে পারে কিন্তু সেটি কী নির্দেশ করত তা না-ও দেখতে পারে। উৎসটি
নতুন prompt-এ দিন, বা মডেলকে আবার খুঁজে দেখতে দিন।

///

## Provider সমর্থন { #provider-support }

| Provider | Citation | কীভাবে চালু করবেন | নোট |
| --- | --- | --- | --- |
| [Anthropic](https://platform.claude.com/docs/en/build-with-claude/citations) | Web search, web fetch আর ডকুমেন্ট | Web search: সবসময়। Web fetch আর ডকুমেন্ট, টুলের ফেরত দেওয়া ডকুমেন্টসহ: `Citations()`। [`WebFetchTool(enable_citations=True)`][pydantic_ai.native_tools.WebFetchTool.enable_citations] শুধু web fetch-এর জন্য চালু করে | Anchor পুরো লেখার অংশ ঢাকে। একটি fetch করা PDF একটি ডকুমেন্ট উৎস। আপনার নিজের দেওয়া সার্চ ফলের citation থাকে না |
| [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_CitationsContentBlock.html) | ডকুমেন্ট, Anthropic মডেলে | `Citations()`, লেখা আর PDF ডকুমেন্টের জন্য, টুলের ফেরত দেওয়া ডকুমেন্টসহ | Bedrock-এর অন্য মডেল citation সমর্থন করে না, তাই সেটিং উপেক্ষা করে। Anchor পুরো লেখার অংশ ঢাকে। একটি ডকুমেন্টের শিরোনাম হলো Pydantic AI-এর দেওয়া নাম, যেমন `Document 1`। S3 থেকে পড়া ডকুমেন্ট উল্লেখ হয় না, কারণ Bedrock তা অনুমোদন করে না। citation চালু থাকলে, একটি লেখার ডকুমেন্ট UTF-8 হতে হবে, নইলে Pydantic AI একটি `UserError` তোলে |
| [Google Gemini API](https://ai.google.dev/gemini-api/docs/google-search) | Google Search, file search আর web fetch | টুলটি চালু করুন | Google Search-এর URL হলো Google-এর redirect লিংক, আর শিরোনাম প্রায়ই শুধু সাইটের domain |
| [Google Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview) | Google Search | টুলটি চালু করুন | Gemini API-র মতোই |
| [OpenAI Chat আর Responses](https://platform.openai.com/docs/guides/tools-web-search) | ওয়েব পেজ, আর Responses-এ ফাইল | web search চালু করুন, বা ফাইলের জন্য file search | অন্য annotation টাইপ, যেমন `container_file_citation`, শুধু [`openai_include_raw_annotations`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_include_raw_annotations]-এ পাওয়া যায় |
| [OpenRouter](https://openrouter.ai/docs/guides/features/server-tools/web-search) | ওয়েব পেজ | web search চালু করুন। Perplexity Sonar মডেল সবসময় সার্চ করে, আর OpenRouter web search টুলসহ সেগুলো প্রত্যাখ্যান করে | OpenRouter বলে না লেখার কোথায় একটি citation বসে, তাই citation-এর কোনো anchor নেই |
| [xAI](https://docs.x.ai/developers/tools/citations) | Web, X আর collection citation | web search বা X search-এর মতো একটি সার্চ টুলসহ `Citations()` | Citation চালু করলে উত্তর বদলায়: মডেল এতে `[[1]](https://x.com/...)`-এর মতো Markdown চিহ্ন লেখে, আর anchor চিহ্নটি ঢাকে। Collection citation হলো ডকুমেন্ট উৎস |

/// check | সংক্ষেপে মনে রাখুন

* Citation থাকে `TextPart.citations`-এ, সব provider-এ একই আকারে; ডকুমেন্টের citation চাইতে `Citations()` capability।
* প্রতিটি citation-এ `sources` (URL বা ডকুমেন্ট) আর `anchor` (লেখার কোন অংশ)।
* citation শুধু লেখার আউটপুটে আসে; গোছানো আউটপুটে নয়।
* stream-এ citation শেষে আসতে পারে; চূড়ান্ত উত্তর থেকে পড়ুন।
* উৎসের লেখা অবিশ্বস্ত হতে পারে; দেখানোর আগে যাচাই করুন।

///
