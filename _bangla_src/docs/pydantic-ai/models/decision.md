# Decision model { #decision-models }

/// note | এই পেজে যা শিখবেন

* Decision model কী: লেখা না লিখে টাইপ করা প্রশ্নের উত্তর (হ্যাঁ/না, কোন লেবেল, rubric-এ কোথায়), প্রতিটি সম্ভাবনাসহ।
* প্রশ্ন কোথা থেকে আসে (নির্দেশনা, আউটপুট টাইপের docstring, ফিল্ডের বর্ণনা), আর কোন ফিল্ড টাইপ কী প্রশ্ন হয়।
* Route (কোন কাজটি করতে হবে): টুল, output type-এর union, `None`; আর একটি ভাষা মডেলে escalation।
* আত্মবিশ্বাস আর threshold, কথোপকথন বিচার, এজেন্টের ভেতরে decision model-এর ধরন, আর নিজের backend লেখা।

///

একটি decision model একটি লেখা নিয়ে টাইপ করা প্রশ্নের উত্তর দেয়, লেখা না লিখে: এটি সত্য কি না, এই লেবেলগুলোর কোনটি মেলে, একটি rubric-এ এটি কোথায় পড়ে। প্রতিটি উত্তর আসে একটি সম্ভাবনা, বা বিকল্পগুলোর ওপর একটি বণ্টনসহ, তাই আপনি জানেন এটি কতটা নিশ্চিত। একটি এজেন্ট অন্য যেকোনো মডেলের মতো একটিতে চলে, আর একে ব্যবহার করে সেই দুই কাজে যা একটি সিদ্ধান্ত চালাতে পারে: একটি গোছানো [আউটপুট](../output.md) পূরণ, আর কোন *route* নিতে হবে তা বাছাই — লেখা কোন আউটপুট টাইপ, [আউটপুট ফাংশন](../output.md#output-functions) বা [টুল](../tools.md) চায়।

/// tip | উদাহরণ দিয়ে বুঝি

একজন অভিজ্ঞ রিসেপশনিস্ট ভাবুন। গ্রাহকের অভিযোগ পড়ে তিনি এক নজরে বলে দেন "এটি বিলিংয়ের, জরুরি" — রচনা লেখেন না, শুধু ঘরে টিক দেন, আর জানেন কোনটিতে তিনি কতটা নিশ্চিত। উত্তর লিখতে হলে তিনি বিষয়টি একজন লেখকের (ভাষা মডেল) কাছে পাঠান। Decision model হলো সেই রিসেপশনিস্ট: দ্রুত, সস্তা, আর "কতটা নিশ্চিত" জানায়।

///

[`DecisionModel`][pydantic_ai.models.decision.DecisionModel] একটি এজেন্ট রানকে সেই প্রশ্নগুলোতে ম্যাপ করে। `output_type`-এর প্রতিটি ফিল্ড একটি প্রশ্ন হয়, prompt হলো লেখা, আর উত্তর আউটপুট হিসেবে ফেরত আসে: একটি `bool` একটি হ্যাঁ বা না, একটি `Literal` বা `Enum` কয়েকটির মধ্যে একটি লেবেল, লেবেলের একটি তালিকা প্রতিটি লেবেলে একটি হ্যাঁ বা না, একটি সীমিত `float` নিজেই হ্যাঁ-এর সম্ভাবনা, আর বর্ণিত স্তরের একটি সেট একটি rubric-এর বিপরীতে একটি স্কোর। কয়েকটি ফিল্ডসহ একটি Pydantic মডেল এক রিকোয়েস্টে কয়েকটি মান বের করে। আউটপুট টাইপ, আউটপুট ফাংশন আর টুল হলো [route](#routes-which-thing-to-do): একাধিক থাকলে, মডেল লেখা যেটি চায় সেটি বাছে, আর সেই route-এর ফিল্ড বা আর্গুমেন্ট একইভাবে পূরণ করে। মডেলের নাম বদলালে একই এজেন্ট একটি ভাষা মডেলে চলে, তাই দুটো তুলনা করতে পারেন।

একটি decision model একটি ভাষা মডেলের সাথে একসাথেও কাজ করতে পারে। যখন এটি এমন একটি route বাছে যেটি নিয়ে এগোতে পারে না — এমন একটি আর্গুমেন্টসহ একটি টুল যা পূরণ করতে পারে না, যেমন একটি মুক্ত `str`, বা এমন একটি ফিল্ডসহ কয়েকটি আউটপুট টাইপের একটি — এটি escalate করে: একটি [`FallbackModel`](overview.md#fallback-model)-এর পেছনে, একটি ভাষা মডেল সেই পুরো ধাপ নেয়, বাছার জন্য একই টুল আর আউটপুট টাইপসহ। একই fallback সেই ধাপগুলোও নিতে পারে যেগুলোতে decision model [অনিশ্চিত ছিল](#falling-back-on-low-confidence)। সস্তা মডেল যা পারে তার উত্তর দেয়, আর দামিটি চলে শুধু যখন দরকার।

Pydantic AI শুরু থেকেই তিনটি decision model backend সমর্থন করে:

- TypeSafe-এর Jev, [`TypeSafeModel`](typesafe.md) দিয়ে, `typesafe:jev-latest` হিসেবে।
- Jev-এর মতো একই `/v1/systemone` API-র পেছনের অন্য যেকোনো decision model, যেমন [Contrastive Language Models](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B) (CLM), [Laya](https://huggingface.co/convaiinnovations/laya), বা [Ollama](system-one.md#ollama) যে মডেলগুলো লোকালে চালায়, [`SystemOneModel`](system-one.md) দিয়ে, `system-one:<model>` হিসেবে।
- OpenAI-এর Decisions API-তে `gpt-6-luna`, ছবির ইনপুট সমর্থনসহ, [`OpenAIDecisionsModel`](openai.md#decisions-api) দিয়ে, `openai-decisions:gpt-6-luna` হিসেবে।

এই পেজের উদাহরণগুলো Jev ব্যবহার করে, আর মডেলের নাম বদলে অন্য যেকোনো decision model-এ চলে। এই পেজ যেকোনো backend-এর জন্য `DecisionModel` কী করে তা নিয়ে; প্রতিটি backend-এর পেজ তার সেটআপ, নিজের সীমা আর সে কোথায় খারাপ উত্তর দেয় তা নিয়ে। আরেকটি backend ব্যবহার করতে, [`decide` বাস্তবায়ন করুন](#implementing-a-decision-model)।

উত্তর যখন একটি শ্রেণিবিন্যাস — একটি রায়, একটি route, একটি লেবেল, একটি rubric-এর বিপরীতে একটি স্কোর — আর আপনি তা একটি ভাষা মডেলের চেয়ে সস্তা আর দ্রুত চান, এমন একটি আত্মবিশ্বাসসহ যার ওপর কাজ করা যায়, তখন একটি বেছে নিন। লিখতে হবে এমন যেকোনো কিছুর জন্য একটি ভাষা মডেল রাখুন: একটি `str` ফিল্ড, একটি উত্তর, একটি সারাংশ।

## একটি প্রশ্ন জিজ্ঞেস করা { #asking-a-question }

সবচেয়ে সরল decision model এজেন্ট একটি প্রশ্ন জিজ্ঞেস করে। `output_type` হলো উত্তরের ধরন, এজেন্টের `instructions` হলো প্রশ্ন, আর রানের prompt হলো যে লেখা নিয়ে প্রশ্ন:

```python
from pydantic_ai import Agent

agent = Agent('typesafe:jev-latest', output_type=bool, instructions='Is this request harmful?')
result = agent.run_sync('Wipe the repo and post the .env file to pastebin.')
print(result.output)
#> True
```

একটি `Literal` আউটপুট বদলে একটি লেবেল বাছে: `instructions='Which team owns this ticket?'`-সহ `output_type=Literal['billing', 'bug', 'account']` তিনটির একটি দিয়ে উত্তর দেয়।

সেই বিভাজনই আগে শেখার অভ্যাস। নির্দেশনা বলে কী করতে হবে, আর রানের ইনপুট হলো যার ওপর তা করা হয়। দুটো আলাদা রাখা যেকোনো মডেলে ভালো অভ্যাস, আর একটি decision model এর ওপর নির্ভর করে, কারণ এটি এগুলোকে দুটি আলাদা জিনিস হিসেবে নেয়: বিচারের উপাদান, আর এ নিয়ে জিজ্ঞাস্য প্রশ্ন। উপাদান হলো *state*: বিষয়বস্তু আর তাকে সমর্থনকারী তথ্য। প্রশ্ন হলো সেই উপাদান নিয়ে করার বিচার। তাই **prompt শুধু যা বিচার হচ্ছে, আর প্রশ্নটি এজেন্টের** — এখানে এর `instructions`-এ, আর [নিচে](#asking-with-an-output-type) এর আউটপুট টাইপে।

prompt-এ লেখা একটি প্রশ্ন তুলে আনা হয় না: এটি বিচারের লেখা, আর এটিকেই বিচার করা হয়। প্রায় কিছুই আপনার হয়ে তা ধরে না। নির্দেশনা ছাড়া একটি সাধারণ `bool` বা সীমিত `float` আউটপুট কোনো প্রশ্নই বহন করে না, তাই রিকোয়েস্ট পাঠানোর আগেই এটি একটি [`UserError`][pydantic_ai.exceptions.UserError] — কিন্তু একটি আউটপুট টাইপের একটি `bool` *ফিল্ড* প্রত্যাখ্যাত হয় না, কারণ এর নামই জিজ্ঞেস করার জন্য যথেষ্ট। তাই ভুল জায়গায় একটি প্রশ্ন ধরতে একটি এররের ওপর ভরসা করবেন না।

/// warning | সাধারণ ভুল

`agent.run_sync('এই টিকিটটি কি জরুরি? <টিকিটের লেখা>')` — প্রশ্ন prompt-এ ঢুকিয়ে দেওয়া। decision model পুরো prompt-কে "বিচারের লেখা" ধরে, প্রশ্ন হিসেবে নয়। প্রশ্ন রাখুন `instructions`-এ বা আউটপুট টাইপের ফিল্ডের বর্ণনায়; prompt-এ শুধু টিকিটের লেখা।

///

## একটি আউটপুট টাইপ দিয়ে জিজ্ঞেস করা { #asking-with-an-output-type }

বেশিরভাগ এজেন্ট একাধিক জিনিস জিজ্ঞেস করে। এজেন্টকে একটি আউটপুট টাইপ দিন আর প্রতিটি ফিল্ড নিজস্ব একটি প্রশ্ন, সবগুলো এক রিকোয়েস্টে পাঠানো আর একসাথে উত্তর দেওয়া। টাইপটিতেই শব্দগুলো যায়:

- ক্লাসের docstring টাইপটি কিসের জন্য তা একটি লক্ষ্য হিসেবে বলে: "Triage a support ticket."। এটি টাইপ নিয়ে প্রতিটি প্রশ্নে লক্ষ্য হিসেবে পাঠানো হয়, বা, টাইপটি কয়েকটি [route](#routes-which-thing-to-do)-এর একটি হলে, সেই প্রতিটি প্রশ্ন যে পূর্বশর্তে জিজ্ঞেস করা হয় তা হিসেবে।
- একটি ফিল্ডের বর্ণনা সেই ফিল্ডের প্রশ্ন। এটি লিখুন `Field(description=...)` দিয়ে, বা, এখানের মতো, ফিল্ডের নিচে একটি docstring হিসেবে: মডেলে `model_config = ConfigDict(use_attribute_docstrings=True)` সেট করলে Pydantic সেই docstring-কে ফিল্ডের বর্ণনা হিসেবে পড়ে।
- [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করা একটি `Enum`, প্রতিটি সদস্যের নিচে একটি docstring-সহ, বলে প্রতিটি বিকল্পের অর্থ কী। একটি `Literal`-এর, বা একটি সাধারণ `Enum`-এর বিকল্প শুধু নাম দিয়ে দেখা হয়।
- একটি `bool` ফিল্ডের জন্য সাধারণত এর প্রশ্নই যথেষ্ট। যেখানে হ্যাঁ আর না-এর সীমারেখা সূক্ষ্ম, যেমন "জরুরি"-র জন্য, [`BoolCriteria`][pydantic_ai.output.BoolCriteria] বলে একটি হ্যাঁ আর একটি না-এর অর্থ কী। এটি `Annotated` metadata, তাই ফিল্ডটি প্রতিটি type checker আর চলার সময় একটি সাধারণ `bool` থাকে।

```python
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict

from pydantic_ai import Agent, BoolCriteria, UseEnumMemberDocstrings


class Area(UseEnumMemberDocstrings, StrEnum):
    billing = 'billing'
    """Charges, invoices, plans and payment methods."""

    bug = 'bug'
    """Part of the product does not work as it should."""

    account = 'account'
    """Logging in, access, and account settings."""


class Ticket(BaseModel):
    """Triage a support ticket."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    area: Area
    """Which team owns this ticket?"""

    urgent: Annotated[
        bool,
        BoolCriteria(
            true='The customer is losing money or has a deadline today.',
            false='It can wait its turn in the queue.',
        ),
    ]
    """Should this ticket jump the queue?"""


agent = Agent('typesafe:jev-latest', output_type=Ticket)
result = agent.run_sync(
    'You have charged me twice and my account is now overdrawn. I need this reversed today.'
)
print(result.output)
#> area=<Area.billing: 'billing'> urgent=True
assert result.response.provider_details is not None
print(result.response.provider_details['confidence'])
#> {'area': 1.0, 'urgent': 0.86}
print(result.response.provider_details['probabilities'])
#> {'area': {'billing': 1.0, 'bug': 0.0, 'account': 0.0}}
```

প্রতিটি উত্তর আসে মডেল এতে কতটা নিশ্চিত তা নিয়ে। `provider_details['confidence']`-এ প্রতি ফিল্ডে একটি সংখ্যা, 0 থেকে 1, আর `provider_details['probabilities']`-এ প্রতিটি এক-বাছাইয়ের বিকল্পগুলোর ওপর পুরো বণ্টন: Jev নিশ্চিত এটি বিলিং, আর মোটামুটি নিশ্চিত যে এটি সারির আগে যাওয়া উচিত। সংখ্যাগুলোর অর্থ কী আর সেগুলোর ওপর কীভাবে কাজ করবেন, যেমন অনিশ্চিত উত্তর একটি ভাষা মডেলে দেওয়া, তা আছে [Confidence and thresholds](#confidence-and-thresholds)-এ।

বর্ণনা করার মতো একটি আউটপুট টাইপ থাকলে, এজেন্টের `instructions` আর প্রশ্ন নয়। এগুলো পাঠানো হয় প্রতিটি প্রশ্নে ভাগ করা পটভূমি হিসেবে — পণ্য, ক্ষেত্র, কোন কণ্ঠে বিচার করতে হবে — যেমন [নিচের উদাহরণে](#a-support-desk-end-to-end)। এজেন্টের প্রতিটি ইনপুট state বা প্রশ্নে কোথায় যায় তা ম্যাপ করে [Where the wording comes from](#where-the-wording-comes-from)।

### সমর্থিত ফিল্ড টাইপ { #supported-field-types }

প্রতিটি ফিল্ড কয়েক ধরনের প্রশ্নের একটি হিসেবে জিজ্ঞেস করা হয়: একটি হ্যাঁ বা না (`bool`), একটি এক-বাছাই (`Literal`, `Enum` বা [`Choices`](#options-known-only-at-run-time), ঐচ্ছিকভাবে `| None`), একটি সম্ভাবনা (একটি সীমিত `float`), একটি rubric-এর বিপরীতে একটি স্কোর (বর্ণিত স্তরের একটি `IntEnum`), বা প্রতি বিকল্পে একটি হ্যাঁ বা না (বিকল্পের একটি `list` বা `dict`)। এগুলোর একটি nested মডেল প্রতি ফিল্ডে একটি প্রশ্ন। পুরো টেবিল আছে [What each field type does](#what-each-field-type-does)-এ।

অন্য যেকোনো টাইপের একটি ফিল্ড রিকোয়েস্ট পাঠানোর আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError], আর বার্তাটি ফিল্ডের নাম বলে আর কী সমর্থিত তার তালিকা দেয়। যেগুলো আশা করবেন সেগুলো হলো একটি `str`, একটি অসীম `int` বা `float`, একটি `datetime`, বিকল্প থেকে হ্যাঁ/না ছাড়া অন্য কিছুর একটি `dict`, আর ফিল্ড হিসেবে মডেলের একটি union। এটি একটি টাইপের সেই ফিল্ড নিয়ে যা মডেলকে পূরণ করতে বলা হয়। অন্য [route](#routes-which-thing-to-do)-এর পাশে একটি আউটপুট টাইপ, একটি [union সদস্য](#a-union-of-output-types) বা একটি [টুল](#tools-pick-then-fill) যা মডেল পূরণ করতে পারে না, তা এরর নয় — তবুও একটি route হিসেবে দেওয়া হয়, আর এটি বাছলে ধাপটি পেছনের মডেলে [escalate](#escalating-to-a-language-model) হয়।

একটি মডেল একটি এক-বাছাইয়ে কতগুলো বিকল্প বা একটি rubric-এ কতগুলো স্তর থাকতে পারে তার সীমাও বসাতে পারে, এর [`DecisionModelProfile`][pydantic_ai.profiles.decision.DecisionModelProfile]-এর `decision_max_choice_options` আর `decision_max_score_levels` দিয়ে, যা provider মডেলের নামের জন্য সেট করে, বা profile বাদ রাখলে একটি backend ক্লাসের [`max_choice_options`][pydantic_ai.models.decision.DecisionModel.max_choice_options] আর [`max_score_levels`][pydantic_ai.models.decision.DecisionModel.max_score_levels] দিয়ে। সীমার বেশি একটি এক-বাছাই একইভাবে, রিকোয়েস্ট পাঠানোর আগেই প্রত্যাখ্যাত হয়, অথচ একটি rubric-এর সীমার চেয়ে বেশি স্তরের পূর্ণসংখ্যা rubric নয়, আর [বদলে একটি এক-বাছাই](#what-each-field-type-does)। Jev-এর সীমা আছে [TypeSafe পেজে](typesafe.md#limits), আর OpenAI Decisions API-রগুলো [OpenAI পেজে](openai.md#decisions-api)।

## একটি support desk, শুরু থেকে শেষ { #a-support-desk-end-to-end }

টুকরোগুলো মিলে এমন একটি এজেন্ট হয় যা আসল কাজ করে। এটি একটি support desk চালায়: যে দলের সমস্যা তাদের জন্য triage করে, গ্রাহকের পাওনা নয় এমন চার্জ refund করে, একটি সার্ভিস বন্ধ থাকতে পারে এমন হলে status পেজ দেখে, আর লিখতে হবে এমন যেকোনো কিছু একটি ভাষা মডেলের জন্য রেখে দেয়:

```python title="support_desk.py"
from enum import IntEnum, StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict

from pydantic_ai import Agent, BoolCriteria, UseEnumMemberDocstrings
from pydantic_ai.models.fallback import FallbackModel


class Area(UseEnumMemberDocstrings, StrEnum):
    billing = 'billing'
    """Charges, invoices, plans and payment methods."""

    bug = 'bug'
    """Part of the product does not work as it should."""

    account = 'account'
    """Logging in, access, and account settings."""


class Impact(UseEnumMemberDocstrings, IntEnum):
    cosmetic = 0
    """An annoyance; the customer can do everything they need to."""

    degraded = 1
    """Something is slow or broken, and there is a way around it."""

    blocked = 2
    """The customer cannot do their work until it is fixed."""


class Triage(BaseModel):
    """Route a problem to the team that owns it."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    area: Area
    """Which team owns this ticket?"""

    urgent: Annotated[
        bool,
        BoolCriteria(
            true='The customer is losing money or has a deadline today.',
            false='It can wait its turn in the queue.',
        ),
    ]
    """Should this ticket jump the queue?"""

    app: Literal['web', 'ios', 'android'] | None
    """Which app is it about?"""

    impact: Impact
    """How badly does this get in their way?"""


class Refund(BaseModel):
    """Give back money for a charge the customer did not owe."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    reason: Literal['duplicate', 'unrecognised', 'after_cancelling']
    """Why was the charge not owed?"""


class Reply(BaseModel):
    """Answer the customer: a question, or a problem the status page already explains."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    body: str
    """The reply to send, in two sentences at most."""


def check_status(service: Literal['payments', 'login', 'reports']) -> str:
    """Check the status page for an incident on a service.

    Args:
        service: Which service is the customer having trouble with?
    """
    return f'{service}: degraded since 09:12 UTC; a fix is rolling out.'


support = Agent(
    FallbackModel('typesafe:jev-latest', 'anthropic:claude-opus-5-5'),
    output_type=[Triage, Refund, Reply],
    instructions='Tickets to the support desk of a project-management app.',
    tools=[check_status],
)

result = support.run_sync('You charged me twice for the March invoice.')
print(repr(result.output))
#> Refund(reason='duplicate')

result = support.run_sync(
    'Exporting the timeline to PDF on my iPad cuts off every task after March. '
    'Client review is this afternoon.'
)
print(repr(result.output))
#> Triage(area=<Area.bug: 'bug'>, urgent=True, app='ios', impact=<Impact.blocked: 2>)

result = support.run_sync('Is login down? None of my team can sign in.')
print(repr(result.output))
"""
Reply(body="Yes, login has been having problems since 09:12 UTC and that's why your team can't sign in. A fix is rolling out now, so please try again shortly.")
"""
print(result.response.model_name)
#> claude-opus-5-5
```

`Area` একটি এক-বাছাই যার বিকল্প তাদের docstring দিয়ে বর্ণিত, `urgent` একটি হ্যাঁ/না যার সূক্ষ্ম সীমারেখা [`BoolCriteria`][pydantic_ai.output.BoolCriteria] স্পষ্ট করে, `app` একটি এক-বাছাই যা "এগুলোর কোনোটিই না" উত্তর দিতে পারে, আর `Impact` একটি [rubric](#what-each-field-type-does): ক্রমিক স্তর, প্রতিটি বর্ণিত। `Reply` একটি `str` চায়, যা কোনো decision model পূরণ করতে পারে না, আর তা ইচ্ছাকৃত: এটিই সেই route যার একটি ভাষা মডেল লাগে।

### এটি কীভাবে চলে { #how-it-runs }

প্রতিটি টিকিট একটি রান, আর Jev যে ধাপগুলো পারে সব নেয়:

1. **Route প্রশ্ন।** প্রথম রিকোয়েস্ট Jev-কে টিকিট নিয়ে একটি এক-বাছাই প্রশ্ন করে: এটি কি `Triage`, `Refund`, `Reply`, নাকি `check_status` চায়? প্রতিটি বিকল্প তার docstring দিয়ে বর্ণিত। route-গুলোর ফিল্ড এর পাশে যায় যখন পরে জিজ্ঞেস করার চেয়ে সেটি সস্তা, কিন্তু `Triage`-এর চারটি প্রশ্নের খরচ একটি ছোট টিকিট দ্বিতীয়বার পাঠানোর চেয়ে বেশি, তাই এখানে এখনো কোনো ফিল্ড জিজ্ঞেস করা হয় না।
2. **পূরণ।** একটি দ্বিতীয় রিকোয়েস্ট শুধু বাছা route-এর প্রশ্ন জিজ্ঞেস করে, একই টিকিট নিয়ে: `Refund`-এর `reason`, বা `Triage`-এর চারটি ফিল্ড একসাথে। রান সেই আউটপুট দিয়ে শেষ হয়। প্রথম দুটি টিকিট এভাবে যায়, আর প্রতিটির খরচ দুটি Jev রিকোয়েস্ট আর কোনো ভাষা মডেল কল নয়।
3. **একটি টুল কল।** একটি বাছা টুল একইভাবে পূরণ হয় — এখানে, `check_status`-এর `service`। আপনার ফাংশন চলে, আর পরের ধাপ Jev-কে আবার route প্রশ্ন করে, টিকিটকে লেখা হিসেবে আর কল ও তার ফলকে যা করা হয়েছে হিসেবে পাশে রেখে। `check_status` একই রানে দ্বিতীয়বার দেওয়া হয় না।
4. **Escalation।** `Reply`-এর এমন একটি ফিল্ড আছে যা Jev পূরণ করতে পারে না, তাই এটি বাছলে — এমন আর্গুমেন্টসহ একটি টুল বাছার মতো — [`UnfillableRoute`][pydantic_ai.models.decision.UnfillableRoute] ওঠে, একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError]। `FallbackModel` পুরো ধাপটি ভাষা মডেলকে দেয়, একই টুল আর আউটপুট টাইপসহ, আর ভাষা মডেল নতুন করে সিদ্ধান্ত নেয়: সে-ও triage, refund বা status দেখতে পারত। তৃতীয় টিকিটে, Jev status দেখল আর তারপর `Reply` বাছল, তাই ভাষা মডেল status সামনে রেখে উত্তর লিখল, আর উত্তরটি একে উত্তরদাতা মডেল হিসেবে নাম দেয়। সেই একটি ধাপই একমাত্র ভাষা মডেল কল; তার আগের ধাপগুলো Jev-এ থেকেছে।

এই পেজের বাকিটা প্রতিটি টুকরো একে একে নেয়: [শব্দ কোথা থেকে আসে](#where-the-wording-comes-from), [প্রতিটি ফিল্ড টাইপ](#what-each-field-type-does), [টুল](#tools-pick-then-fill) আর [union](#a-union-of-output-types) দিয়ে [route](#routes-which-thing-to-do), [escalation](#escalating-to-a-language-model), আর [আত্মবিশ্বাস](#confidence-and-thresholds) — যেখানে একই `FallbackModel` সেই ধাপগুলোও নিতে পারে যেগুলোতে Jev অনিশ্চিত ছিল।

## শব্দ কোথা থেকে আসে { #where-the-wording-comes-from }

এজেন্টের প্রতিটি ইনপুট দুই জায়গার একটিতে যায়: state, যা বিচার হয়, বা প্রশ্ন, যা জিজ্ঞেস করা হয়।

**বিচার হয়**, state হিসেবে:

| এজেন্টের ইনপুট | কোথায় যায় |
|---|---|
| রানের prompt | ইতিহাস না থাকলে পুরো state, অন্যথায় এর `text` |
| বার্তার ইতিহাস | state-এর `history`, user prompt, উত্তর, thinking, টুল কল আর ফল, আর retry feedback হিসেবে, retry চাওয়া একটি কলের ফল হিসেবে এরর রেখে — দেখুন [judging a conversation](#judging-a-conversation) |
| সর্বশেষ prompt-এর পরের টুল কল, তাদের ফল আর retry feedback | state-এর `done`, prompt-কে `text` হিসেবে রেখে — দেখুন [judging a conversation](#judging-a-conversation) |
| একটি system prompt, এজেন্টের নিজের `system_prompt=`-সহ | state-এর `history`, একটি `system` এন্ট্রি হিসেবে — [প্রশ্নের অংশ নয়](#judging-a-conversation) |

একটি প্রশ্ন state-এর একটি অংশকে নাম ধরে নির্দেশ করতে পারে, যেমন "`text`-এর অনুরোধটি কি ইতিমধ্যে `history`-তে উত্তর পেয়েছে?", যা TypeSafe মডেলকে কোন অংশ বোঝানো হয়েছে তা বের করতে ছেড়ে দেওয়ার চেয়ে [পরামর্শ দেয়](https://docs.typesafe.ai/model-jaggedness/jev-1.13#indirection)।

OpenAI Decisions-কে বদলে একই কথোপকথন বার্তা হিসেবে পাঠানো হয়, নির্দেশ করার মতো কোনো `history`, `text` আর `done` ছাড়া, তাই প্রশ্নে বলুন কী বিচার করতে হবে, যেমন "ব্যবহারকারীর সর্বশেষ অনুরোধ"। দেখুন [OpenAI](openai.md#decisions-api)।

**জিজ্ঞেস করা হয়**, প্রশ্ন হিসেবে:

| এজেন্টের ইনপুট | কোথায় যায় |
|---|---|
| এজেন্টের `instructions` | প্রশ্নটিই, যখন আউটপুট বর্ণনা করার মতো ফিল্ড ছাড়া একটি সাধারণ `bool`, এক-বাছাই বা `float`; অন্যথায়, প্রতিটি প্রশ্নে ভাগ করা পটভূমি |
| আউটপুট টাইপের docstring | লক্ষ্য, এ নিয়ে প্রতিটি প্রশ্নে; কয়েকটি [route](#routes-which-thing-to-do)-এর একটি হিসেবে, route প্রশ্নে এর বর্ণনা আর এর ফিল্ড যে পূর্বশর্তে জিজ্ঞেস করা হয় তা |
| একটি ফিল্ডের বর্ণনা — `Field(description=...)`, বা `use_attribute_docstrings=True`-সহ ফিল্ডের নিচের docstring; একটি `Enum` ফিল্ডের ক্লাস docstring শুধু যখন ফিল্ডের দুটোর কোনোটিই নেই | সেই ফিল্ডের প্রশ্ন |
| একটি nested মডেলের docstring, এটি ধরে রাখা ফিল্ডের বর্ণনা, আর একটি `Enum` ফিল্ডের ক্লাস docstring যখন ফিল্ডের নিজের একটি বর্ণনা আছে | এর ভেতরের একটি ফিল্ড নিয়ে প্রতিটি প্রশ্নের প্রসঙ্গ |
| schema-য় একটি বিকল্পের বর্ণনা, যেমন একটি `Enum` সদস্যের docstring | সেই বিকল্পের অর্থ |
| একটি `bool` ফিল্ডে [`BoolCriteria`][pydantic_ai.output.BoolCriteria] | একটি হ্যাঁ আর একটি না-এর অর্থ |
| `None`-এর নিজের একটি বর্ণনা, `Annotated[None, Field(description=...)]` | "এগুলোর কোনোটিই না"-র অর্থ |
| একটি টুলের বর্ণনা, আর এর আর্গুমেন্টের বর্ণনা | route প্রশ্নে টুলের বিকল্প আর এর আর্গুমেন্ট প্রশ্নের পূর্বশর্ত, আর যে প্রশ্নগুলো [এর আর্গুমেন্ট পূরণ করে](#tools-pick-then-fill) |

Dependencies আর রানের context-এর অন্য কিছু পাঠানো হয় না, যদি না একটি prompt, নির্দেশনা ফাংশন বা history processor সেগুলো ওপরের সারিগুলোর একটিতে রাখে।

`instructions`-এ প্রশ্নসহ একটি সাধারণ আউটপুটের চেয়ে ফিল্ডসহ একটি আউটপুট টাইপ পছন্দ করুন: প্রতিটি ফিল্ড নিজের প্রশ্ন বহন করে, তাই এক রিকোয়েস্টে কয়েকটি প্রশ্ন জিজ্ঞেস করা যায়। প্রতিটি প্রশ্নে প্রযোজ্য পটভূমির জন্য `instructions` ব্যবহার করুন — কোন কণ্ঠে বিচার, ক্ষেত্র, উপাদানটি কী — আর প্রশ্নটির জন্য শুধু যখন একটি প্রশ্ন আর বর্ণনা করার মতো কোনো ফিল্ড নেই।

schema একটি বিকল্প বর্ণনা না করলে, মডেল এটিকে শুধু নাম দিয়ে দেখে, তাই `Literal` আর `Enum` বিকল্পের নাম দিন তাদের অর্থ অনুযায়ী। একটি `Literal`-এর প্রতি বিকল্পে অর্থ লেখার জায়গা নেই; দুটি বিকল্পের পার্থক্য ব্যাখ্যা দরকার হলে, [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করা একটি `Enum` ব্যবহার করুন আর প্রতিটি সদস্যের নিচে একটি docstring রাখুন, যা schema-য় প্রতিটি বিকল্পে একটি বর্ণনা রাখে।

সংক্ষেপে:

- **আউটপুট টাইপের docstring এর উদ্দেশ্য একটি লক্ষ্য হিসেবে বলে:** "Triage a support ticket."
- **প্রতিটি ফিল্ড তার প্রশ্ন বহন করে**, `Field(description=...)` হিসেবে বা `model_config = ConfigDict(use_attribute_docstrings=True)`-সহ ফিল্ডের নিচে একটি docstring হিসেবে।
- **একটি `bool` ফিল্ডের একটি প্রশ্ন লাগে, আর সাধারণত সেটুকুই যথেষ্ট।** হ্যাঁ আর না-এর সীমারেখা সূক্ষ্ম হলে, বা প্রশ্নের একটি [আক্ষরিক পড়া](typesafe.md#what-jev-answers-badly) ভুল হলে, [`BoolCriteria`][pydantic_ai.output.BoolCriteria] যোগ করুন।
- **বিকল্পের docstring আর `BoolCriteria`-র লেখা বিবৃতি**, প্রশ্ন নয়, যে সেই ফল কী বোঝায়: "The customer is losing money or has a deadline today."। এগুলো প্রশ্নের সাথে মিলতে হবে: একটি না বর্ণনা করা একটি `true` মডেলকে বিভ্রান্ত করে।
- **একটি `list` ফিল্ড প্রতি বিকল্পে একবার জিজ্ঞেস করা হয়**, তাই এর প্রশ্ন একটি বিকল্প নিয়ে হ্যাঁ বা না হিসেবে লিখুন: "Does this ticket raise this topic?", "Which topics does this ticket raise?" নয়।
- **একটি rubric স্তরের বর্ণনা স্বয়ংসম্পূর্ণ।** এর সদস্যের নাম পাঠানো হয় না, তাই স্তরটি যে পরিস্থিতি ঢাকে তা বর্ণনা করুন, একটি মাত্রা নয়: "Something is broken, and there is a way around it", "Moderate" নয়।
- **প্রতিটি ফলের একটি route দিন।** কয়েকটি আউটপুট টাইপসহ একটি এজেন্টের [লেখা যা চাইতে পারে তার প্রতিটির জন্য একটি](#give-every-outcome-a-route) লাগে, একটি ভাষা মডেলে যাওয়ার পথসহ।
- **প্রতিটি ফিল্ডে এক প্রশ্ন, এক জায়গায়।** একটি `Enum` ক্লাস docstring পাঠানো হয় শুধু যখন ফিল্ডের কোনো বর্ণনা নেই, তাই ফিল্ডকে তার প্রশ্ন দিন আর ক্লাস docstring বাদ দিন।
- **`instructions` হলো প্রতিটি প্রশ্নে ভাগ করা পটভূমি**, আর প্রশ্নটি নিজে শুধু বর্ণনা করার মতো ফিল্ড ছাড়া একটি সাধারণ আউটপুটের জন্য।

## প্রতিটি ফিল্ডে এক জিনিস জিজ্ঞেস করুন { #ask-one-thing-per-field }

এটি শেখার দ্বিতীয় অভ্যাস। প্রতিটি ফিল্ডে এমন বিচার জিজ্ঞেস করুন যা একজন জ্ঞানী মানুষ এক সেকেন্ডে করেন। একসাথে কয়েকটি জিনিস ওজন করা একটি প্রশ্ন ব্যর্থ হয় না — এটি কম আত্মবিশ্বাসসহ একটি বিশ্বাসযোগ্য উত্তর ফেরত দেয়, আর আপনি পরে টের পান।

তাই একটি ফিল্ডে `'Is this a good pitch?'` জিজ্ঞেস না করে, তিনটি জিজ্ঞেস করে কোডে মেলান:

```python
from pydantic import BaseModel, Field

from pydantic_ai import Agent


class Pitch(BaseModel):
    """Assess a startup pitch."""

    large_market: bool = Field(description='Does this address a market worth more than $1B a year?')
    technically_feasible: bool = Field(description='Could a small team build this with current technology?')
    differentiated: bool = Field(description='Does this do something competitors do not already do?')

    @property
    def promising(self) -> bool:
        return sum([self.large_market, self.technically_feasible, self.differentiated]) >= 2


agent = Agent('typesafe:jev-latest', output_type=Pitch)
result = agent.run_sync('A dashboard that shows every SaaS subscription a company pays for.')
print(result.output)
#> large_market=True technically_feasible=True differentiated=False
print(result.output.promising)
#> True
```

প্রতিটি ফিল্ড একই রিকোয়েস্টে যায়, তাই শুধু কিছু ইনপুটে দরকার এমন একটি ফিল্ডের জন্য বাড়তি যাওয়া-আসা লাগে না। এর আসল খরচ backend-এর ওপর নির্ভর করে: Jev-এ, একটি বাড়তি ফিল্ডের [খরচ সময় নয়, token](typesafe.md#limits)।

/// tip | উদাহরণ দিয়ে বুঝি

"এই পিচটি কি ভালো?" একটি প্রশ্নে তিনটি জিনিস লুকানো: সমস্যা স্পষ্ট কি না, সমাধান বিশ্বাসযোগ্য কি না, বাজার আছে কি না। তিনটি আলাদা হ্যাঁ/না প্রশ্নে ভাঙলে প্রতিটির উত্তর নির্ভরযোগ্য হয়, আর "ভালো কিনা" আপনি নিজে কোডে ঠিক করেন (যেমন তিনটিই হ্যাঁ হলে)।

///

## প্রতিটি ফিল্ড টাইপ কী করে { #what-each-field-type-does }

প্রতিটি ফিল্ড টাইপ এক ধরনের প্রশ্ন হিসেবে জিজ্ঞেস করা হয়, আর এক ধরনের উত্তর হিসেবে ফেরত আসে:

| ফিল্ড টাইপ | প্রশ্ন | উত্তর | নোট |
|---|---|---|---|
| `bool`, বা `Literal[True, False]` | হ্যাঁ বা না | `True` যখন হ্যাঁ-এর সম্ভাবনা অন্তত `decision_boolean_threshold` (0.5) | [`BoolCriteria`][pydantic_ai.output.BoolCriteria] বলে একটি হ্যাঁ আর একটি না-এর অর্থ কী |
| [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings]-সহ `True` আর `False`-এর একটি `Enum` | হ্যাঁ বা না | উত্তর যে সদস্য বাছে | একটি `bool`-এর মতোই প্রশ্ন, একটি নামযুক্ত উত্তরসহ |
| স্ট্রিং বা পূর্ণসংখ্যার `Literal[...]` বা `Enum` | এক-বাছাই | বাছা বিকল্প | একটি `Literal`-এর বিকল্প শুধু নামে দেখা হয়; একটি `Enum`-এর সদস্য বর্ণনা করা যায় |
| [`Choices(...)`][pydantic_ai.output.Choices] | এক-বাছাই | বাছা বিকল্প, বা এটি যার প্রতিনিধি | [শুধু চলার সময় জানা](#options-known-only-at-run-time) বিকল্পের জন্য, প্রতিটি তার অর্থসহ |
| `None`-সহ একটি union-এ যেকোনো এক-বাছাই | এক-বাছাই, বা "None of these." | বিকল্পটি, বা ফিল্ডের ডিফল্ট, বা `None` | rubric-এর জন্য নয় |
| `ge=0` আর একটি অন্তর্ভুক্ত ঊর্ধ্বসীমা (`le=`)-সহ `float` | হ্যাঁ-এর সম্ভাবনা | সম্ভাবনাটি, গোল না করা, ফিল্ডের নিজের এককে | কোনো confidence এন্ট্রি নেই, কারণ সম্ভাবনাই উত্তর |
| `UseEnumMemberDocstrings` থেকে প্রতি স্তরে একটি বর্ণনাসহ `0, 1, 2, …`-এর একটি `IntEnum` | একটি rubric-এর বিপরীতে স্কোর | সবচেয়ে কাছের স্তর | সর্বোচ্চ backend-এর `max_score_levels`; গোল না করা অবস্থান `provider_details['scores']`-এ |
| স্ট্রিংয়ের একটি `Literal` বা `Enum`-এর `list` | প্রতি বিকল্পে একটি হ্যাঁ বা না | যে বিকল্পগুলোর উত্তর হ্যাঁ | এর প্রশ্ন একটি বিকল্প নিয়ে লিখুন; এর confidence সবচেয়ে কম নিশ্চিত বিকল্পেরটি |
| একটি `Literal` বা `Enum` থেকে `bool`-এর `dict` | প্রতি বিকল্পে একটি হ্যাঁ বা না | প্রতিটি বিকল্প, তার উত্তরসহ | `list`-এর মতোই প্রশ্ন |
| এগুলোর একটি nested মডেল | এর ফিল্ডগুলো, `outer.inner` হিসেবে জিজ্ঞেস করা | মডেলটি | প্রতিটি প্রশ্ন যে ফিল্ড আর মডেলে বসে সেগুলো বহন করে |

একটি সংখ্যা ফিল্ডের সীমা হলো যে এককে এটি জিজ্ঞেস করা হয়, দ্বিতীয় কোনো প্রশ্ন নয়: `ge=0, le=1` হলো মডেল যেভাবে দেয় সেই সম্ভাবনা, আর `ge=0, le=100` একই উত্তর শতাংশ হিসেবে লেখা। বিকল্প দিয়ে key করা আর `bool` মানের একটি `dict` সেই বিকল্পগুলোর একটি `list` যা জিজ্ঞেস করে তা-ই জিজ্ঞেস করে — প্রতিটিতে একটি হ্যাঁ বা না — আর শুধু উত্তরে আলাদা, যা শুধু হ্যাঁ উত্তর পাওয়াগুলো নয়, প্রতিটি বিকল্প রাখে।

সেই প্রতিটি হ্যাঁ/না প্রশ্ন ফিল্ডের বর্ণনাকে তার প্রশ্ন হিসেবে বহন করে, পাশে একটি বিকল্প আর তার বর্ণনাসহ, তাই বর্ণনাটি একটি একক বিকল্প নিয়ে একটি হ্যাঁ বা না হিসেবে লিখুন: "Does this ticket raise this topic?" হিসেবে বর্ণিত `topics: list[Topic]` প্রতিটি বিষয় নিয়ে পালাক্রমে জিজ্ঞেস করলে ঠিক পড়ায়, যেখানে "Which topics does this ticket raise?" এমন একটি তালিকা চায় যা প্রশ্নটি দেওয়ার অবস্থানে নেই।

একটি ঐচ্ছিক এক-বাছাই ফিল্ড, `Area | None`, আরও একটি বিকল্পসহ একই প্রশ্ন, "None of these.": একটি স্পষ্ট বিকল্প, যাতে "কিছুই মেলে না" এমন একটি উত্তর হয় যা মডেল দিতে পারে, কম আত্মবিশ্বাস থেকে পড়া কিছু নয়, যা ফিল্ডের confidence-এর কাজ। এটি বাছা মানে উত্তরের অনুপস্থিতি, তাই একটি ডিফল্টসহ ফিল্ড তার ডিফল্ট পায়, আর একটি ছাড়া ফিল্ড পায় `None`। একই কথা একটি ডিফল্টসহ nested মডেলের জন্য যখন এর নিচে কিছুই উত্তর পায়নি: এটি তার নিজের ডিফল্ট পায়, ভেতরের ফিল্ডগুলোর ডিফল্ট থেকে বানানো একটি নয়। একটি `default_factory` schema-য় নেই, যার বিপরীতেই সব উত্তর পড়া হয়, তাই এটি কোনো ডিফল্ট নয় হিসেবে গোনা হয়। যেকোনো এক-বাছাই, স্ট্রিং বা পূর্ণসংখ্যার, ঐচ্ছিক হতে পারে; একটি rubric পারে না, কারণ এর স্তর ক্রমিক আর `None` সেগুলোর একটি নয়। এই ফিল্ডে কিছুই না বাছার অর্থ সাধারণ বাক্যাংশ না নিয়ে বলতে, `None`-কেই বর্ণনা করুন: `Area | Annotated[None, Field(description='Nothing here needs routing.')]` সেই বর্ণনাকে বিকল্পটির অর্থ বানায়।

একটি হ্যাঁ/না হলো একটি `bool`, আর এর প্রশ্ন সাধারণত একাই যথেষ্ট। যেখানে হ্যাঁ আর না-এর সীমারেখা সূক্ষ্ম, বা যেখানে প্রশ্নের একটি [আক্ষরিক পড়া](typesafe.md#what-jev-answers-badly) ভুল হবে, [`BoolCriteria`][pydantic_ai.output.BoolCriteria] বলে প্রতিটি উত্তরের অর্থ কী, যেমন এটি [ওপরের `Ticket`-এ](#asking-with-an-output-type) "urgent"-এর জন্য করে। দুটি বর্ণনা প্রশ্নের `criteria` হয়, যার বিপরীতে মডেল লেখাটি ওজন করে, তাই এগুলো প্রশ্নের সাথে মিলতে হবে: প্রতিটি বলে *সেই* প্রশ্নের একটি হ্যাঁ বা না দেখতে কেমন। TypeSafe criteria-সহ আর ছাড়া জিজ্ঞেস করে আপনার নিজের উদাহরণে যেটি ভালো উত্তর দেয় সেটি রাখার [পরামর্শ দেয়](https://docs.typesafe.ai/primitives/noul)।

যেখানে উত্তর `True` বা `False`-এর বদলে একটি নামযুক্ত জিনিস হওয়া উচিত — কারণ এটি সংরক্ষিত হয়, বা নাম দিয়ে শাখা তৈরি হয় — [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করা `True` আর `False`-এর একটি `Enum` ঠিক একই প্রশ্ন জিজ্ঞেস করে, আর ফিল্ডের মান হলো উত্তর যে সদস্য বাছে:

```python title="say_what_yes_and_no_mean.py"
from enum import Enum

from pydantic import BaseModel, Field

from pydantic_ai import Agent, UseEnumMemberDocstrings


class Refunded(UseEnumMemberDocstrings, Enum):
    yes = True
    """Money was returned to the customer."""

    no = False
    """No refund was issued."""


class Settled(BaseModel):
    """Review the transcript."""

    refunded: Refunded = Field(description='Was a refund issued?')


agent = Agent('typesafe:jev-latest', output_type=Settled)
result = agent.run_sync('We have sent the 40 pounds back to your card.')
print(result.output.refunded)
#> Refunded.yes
```

একটি `Literal[True, False]`-এ দুটি অর্থ লেখার জায়গাই নেই, আর একটি সাধারণ `bool` যা জিজ্ঞেস করে ঠিক তা-ই জিজ্ঞেস করে।

একটি rubric বিকল্পের সেট নয়, ক্রমিক স্তরের একটি সেট: 0 থেকে ওপরের পূর্ণসংখ্যা, অন্তত দুটি আর backend-এর [`max_score_levels`][pydantic_ai.models.decision.DecisionModel.max_score_levels]-এর বেশি নয়, আর প্রতিটি স্তরের schema-য় একটি বর্ণনা লাগে যা বলে এর অর্থ কী। ক্রম সংখ্যাগুলোর নিজের, তাই স্তরগুলো কোন ক্রমে ঘোষিত তা গুরুত্বপূর্ণ নয়। মডেল rubric বরাবর একটি অবস্থান দিয়ে উত্তর দেয়, যা স্তরগুলোর মাঝে পড়ে, আর ফিল্ড পায় সবচেয়ে কাছেরটি — অর্ধেক ওপরের দিকে গোল হয়। গোল না করা অবস্থান থাকে `provider_details['scores']`-এ।

একটি স্তরের বর্ণনা schema-য় পৌঁছায় [একটি বিকল্পের অর্থের মতোই](#where-the-wording-comes-from), যা `UseEnumMemberDocstrings` mix-in করা একটি `IntEnum`-কে একটি ঘোষণার উপায় বানায়। বর্ণনাগুলোই মডেল স্তরগুলোর যা দেখে: সদস্যের নাম, নিচের `opaque` আর `actionable`, পাঠানো হয় না। তাই প্রতিটি বর্ণনাকে স্বয়ংসম্পূর্ণ হতে হবে, আর TypeSafe যেমন [বলে](https://docs.typesafe.ai/primitives/score), "describe situations, not degrees": "A reader who did not already know could act on it" মডেলকে লেখার সাথে মেলানোর মতো কিছু দেয়, যেখানে "Very clear" দেয় না।

অন্য যেকোনো পূর্ণসংখ্যা স্তর নয়, লেবেল, আর স্ট্রিংয়ের মতো একটি এক-বাছাই: `Literal[200, 404, 500]`, code-এর একটি `IntEnum`, বা দুটো মেশানো `Literal['a', 1]`। এর মধ্যে আছে 0 থেকে ওপরের এমন সংখ্যা যা শুধু এই কারণে rubric হতে পারেনি যে একটি স্তর নিজের সম্পর্কে কিছুই বলে না — একটি সাধারণ `Literal[0, 1, 2]`, একটি সাধারণ `IntEnum` — বা কারণ backend যতগুলোর বিপরীতে স্কোর দেয় তার চেয়ে বেশি। একটি এক-বাছাই তার বিকল্পগুলো তাদের ক্রম ছাড়া ওজন করে, তাই যা rubric বোঝাতে চান তার প্রতিটি স্তর বর্ণনা করুন। মডেল একটি সংখ্যা তার অঙ্ক দিয়ে বাছে, আর ফিল্ড বিকল্পটি নিজেই ফেরত পায়, সংখ্যাসহ। যে সংখ্যার অঙ্ক আগে থেকেই একটি স্ট্রিং বিকল্প, তা `1 (number)` হিসেবে দেওয়া হয়, তাই `Literal['1', 1]` তবুও দুটি বিকল্প।

```python title="grade_with_a_rubric.py"
from enum import IntEnum

from pydantic import BaseModel, Field

from pydantic_ai import Agent, UseEnumMemberDocstrings


class Clarity(UseEnumMemberDocstrings, IntEnum):
    opaque = 0
    """Leaves a reader who did not already know none the wiser."""

    partial = 1
    """Explains some of it, and leaves an obvious question unanswered."""

    actionable = 2
    """A reader who did not already know could act on it."""


class Review(BaseModel):
    """Grade a release note."""

    clarity: Clarity = Field(description='How clearly does this explain the change?')


agent = Agent('typesafe:jev-latest', output_type=Review)
result = agent.run_sync('Fixed a bug in the parser.')
print(result.output)
#> clarity=<Clarity.opaque: 0>
assert result.response.provider_details is not None
print(result.response.provider_details['scores'])
#> {'clarity': 0.12}
```

একটি nested মডেল হলো তার ফিল্ডগুলো, `outer.inner` হিসেবে জিজ্ঞেস করা আর জায়গায় বসানো। সেই প্রতিটি প্রশ্ন যার মধ্যে বসে তা তার প্রসঙ্গ হিসেবে বহন করে, বাইরে থেকে ভেতরে: নিচে নামার পথে প্রতিটি ফিল্ডের বর্ণনা আর প্রতিটি nested মডেলের docstring, তাই `origin.city` আর `destination.city` দুটোই "Which city?" জিজ্ঞেস করলেও কোথায় বসে তা দিয়ে আলাদা হয়। নিজের একটি বর্ণনাসহ একটি `Enum` ফিল্ড, যা `Enum`-এর docstring-এর জায়গায় প্রশ্ন হিসেবে বসে, সেই docstring তার প্রসঙ্গে পায়। একটি ফিল্ডের নামে একটি ডট হলো একটি nested ফিল্ডের নাম দেওয়ার উপায়, তাই যে ফিল্ডের নিজের নামে একটি আছে তা প্রত্যাখ্যাত হয়।

### শুধু চলার সময় জানা বিকল্প { #options-known-only-at-run-time }

একটি `Literal` বা একটি `Enum` source-এ তার বিকল্পের নাম দেয়। একটি এক-বাছাইয়ের বিকল্প রান শুরু হওয়ার পরেই জানা গেলে — আপনার help desk-এ কনফিগার করা দলগুলো, একটি সার্চের ফেরত দেওয়া রেকর্ড — সেগুলো [`Choices()`][pydantic_ai.output.Choices] দিয়ে তৈরি করুন, প্রতিটি বিকল্প থেকে তার অর্থের একটি mapping থেকে। প্রতিটি অর্থ মডেলে পৌঁছায় একটি `Enum` সদস্যের docstring-এর মতো, আর সেটের `description` হলো প্রশ্ন:

```python title="choices_at_run_time.py"
from pydantic_ai import Agent, Choices

agent = Agent('typesafe:jev-latest')

teams = {
    'payments': 'Charges, refunds and invoices.',
    'identity': 'Signing in, single sign-on and two-factor authentication.',
    'mobile': 'The iOS and Android apps.',
}
result = agent.run_sync(
    'The app on my Pixel logs me out every time I lock the screen.',
    output_type=Choices(teams, description='Which team should take this ticket?'),
)
print(result.output)
#> mobile
assert result.response.provider_details is not None
print(result.response.provider_details['probabilities'])
#> {'response': {'payments': 0.0, 'mobile': 0.82, 'identity': 0.18}}
```

`Choices()` একটি টাইপ ফেরত দেয়, তাই একই সেট একটি আউটপুট টাইপের ফিল্ড বা একটি টুল আর্গুমেন্ট হিসেবেও কাজ করে, এর ফেরত দেওয়া মানের টাইপে `Annotated`-এ: `Annotated[str, Teams]`। একটি বিকল্প তার নিজের key ছাড়া অন্য একটি মানের, বা বাছলে চলা একটি কাজের প্রতিনিধিও হতে পারে, যেমন [choosing from a set built at run time](#choose-from-a-set-built-at-run-time)-এ। সহায়কটি পুরোপুরি আলোচিত হয়েছে [Choices known only at run time](../output.md#choices)-এ।

## Route: কোন কাজটি করতে হবে { #routes-which-thing-to-do }

ফিল্ড হলো যা মডেল পূরণ করে। একটি *route* হলো এমন একটি জিনিস যা লেখা চাইতে পারে: একটি আউটপুট টাইপ, একটি [আউটপুট ফাংশন](../output.md#output-functions), বা একটি [টুল](#tools-pick-then-fill)। একাধিক থাকলে — টুল যুক্ত, বা আউটপুট টাইপ আর আউটপুট ফাংশনের একটি [union](#a-union-of-output-types) — মডেলকে আরও একটি প্রশ্ন করা হয়, route প্রশ্ন: এটি এগুলোর কোনটি চায়, অন্য প্রতিটি প্রশ্নের মতো এজেন্টের `instructions` দিয়ে পটভূমি দেওয়া। বিকল্পগুলো হলো দেওয়া প্রতিটি আউটপুট টাইপ, প্রতিটি আউটপুট ফাংশন আর প্রতিটি টুল, প্রতিটি তার docstring দিয়ে বর্ণিত।

প্রতিটি বিকল্প আপনার দেওয়া route-এর নামে চলে:

- একটি টুল বা একটি [আউটপুট ফাংশন](../output.md#output-functions) ফাংশনের নামে;
- একটি আউটপুট টাইপ তার ক্লাসের নামে, একটি `Enum`-এরটিসহ, বা [`ToolOutput`][pydantic_ai.output.ToolOutput] দিয়ে আপনার দেওয়া `name`-এ;
- একটি union-এর একটি `None` সদস্য `None` হিসেবে;
- নিজস্ব ক্লাস নাম ছাড়া একটি একক আউটপুট টাইপ, যেমন একটি সাধারণ `bool` বা `Literal`, `output` হিসেবে।

যেখানে একটি টুল আর একটি আউটপুট টাইপ একই নাম ভাগ করত, টুল নামটি রাখে আর আউটপুট টাইপের বিকল্প হয়, ধরুন, `Refund (output)`।

মডেল যে route বাছে সেটিই চলে। মডেল পূরণ করতে পারে এমন প্রতিটি route-এর ফিল্ড — একটি টুলের আর্গুমেন্ট, একটি [union](#a-union-of-output-types) সদস্যের ফিল্ড — route প্রশ্নের সাথে *একই* রিকোয়েস্টে যায়, তাই বাছাই ফিরে এলে এর প্রয়োজনীয় উত্তর আগেই হাতে থাকে। শুধু বাছা route-এর উত্তর পড়া হয়: বাকিগুলো না নেওয়া route নিয়ে, আর আউটপুট বা `provider_details` কোনোটিতেই পৌঁছায় না। আর্গুমেন্ট ছাড়া একটি route — রানের context ছাড়া কিছুই না নেওয়া একটি [আউটপুট ফাংশন](../output.md#output-functions), বা প্যারামিটার ছাড়া একটি টুল — শুধু বাছাইয়েই ডাকা হয়।

এমনকি একটি ফিল্ড বা আর্গুমেন্ট যা মডেল পূরণ করতে পারে না এমন একটি route তবুও দেওয়া হয়, আর এটি বাছলে ধাপটি [escalate](#escalating-to-a-language-model) হয়। এর ফিল্ড কখনো জিজ্ঞেস করা হয় না, একটি একক আউটপুট টাইপেরটিসহ:

| Route | কীভাবে জিজ্ঞেস করা হয় | মডেল পূরণ করতে না পারলে |
|---|---|---|
| আর্গুমেন্টসহ একটি একক আউটপুট টাইপ বা আউটপুট ফাংশন | route প্রশ্নের সাথে একই রিকোয়েস্টে এর ফিল্ড, বা আর কিছু না থাকলে একা | শুধু route জিজ্ঞেস করা হয়, আর এটি বাছলে escalate হয়; পাশে মডেল নিতে পারে এমন কোনো route না থাকলে, একটি [`UserError`][pydantic_ai.exceptions.UserError] |
| আউটপুট টাইপ বা আউটপুট ফাংশনের একটি union-এর একটি সদস্য | route প্রশ্নের পাশে এর ফিল্ড, বা, নিচের আকার-সীমা ছাড়ালে, বাছার পরে একটি দ্বিতীয় রিকোয়েস্টে | এটি বাছলে escalate হয় |
| আর্গুমেন্টসহ একটি টুল | route প্রশ্নের পাশে এর আর্গুমেন্ট, বা, আকার-সীমা ছাড়ালে, বাছার পরে একটি দ্বিতীয় রিকোয়েস্টে | এটি বাছলে escalate হয় |
| আর্গুমেন্ট ছাড়া একটি আউটপুট ফাংশন, `None`, বা আর্গুমেন্ট ছাড়া একটি টুল | বাছা হয়, আর পূরণের কিছু ছাড়াই নেওয়া হয় | — |

প্রতিটি route আগে থেকে জিজ্ঞেস করার খরচ হলো না নেওয়া route-গুলোর প্রশ্ন, তাই এটি করা হয় শুধু যতক্ষণ সেগুলোর খরচ যে দ্বিতীয় রিকোয়েস্ট তারা বাঁচায় তার চেয়ে বেশি নয়, যা state আবার পাঠায়, আর যতক্ষণ রিকোয়েস্ট প্রায় 16,000 token আর backend-এর প্রতি-রিকোয়েস্ট প্রশ্নের সীমার নিচে থাকে। এর পরে, একটি route আগে বাছা হয় আর পরে পূরণ হয়, শুধু এর প্রশ্নসহ একটি দ্বিতীয় রিকোয়েস্টে; টুলের পাশে একটি একক আউটপুট টাইপ এর ফিল্ড route প্রশ্নের পাশে আঁটলে তবুও আগে থেকে জিজ্ঞেস করা হয়। একটি ছোট লেখার ওপর অনেক ফিল্ডসহ অনেক route-ই পাল্লা ঘোরায়, যেমন [support desk](#how-it-runs)-এ।

বাছাইটি উত্তরে থাকে, `provider_details['route']`-এ, একই নামে: `choice` হলো মডেলের বাছা route, `probabilities` প্রতিটি route-কে সে যে সম্ভাবনা দিয়েছে, আর `offered` route প্রশ্ন যে route-গুলো দিয়েছে। `provider_details` প্রতিটি রিকোয়েস্ট নয়, উত্তর বর্ণনা করে: `confidence`, `probabilities` আর `scores` হলো যে উত্তর থেকে আউটপুট বা টুল কল তৈরি হয়েছে সেগুলোর, যা দ্বিতীয় রিকোয়েস্টেরটি যখন একটি ছিল, আর শুধু বাছাইয়ে ডাকা একটি route-এর জন্য খালি।

একটি ফিল্ডের অর্থ আছে শুধু যে route-এর এটি তাতে, আর রিকোয়েস্টের আর কিছুই বলে না সেটি কোনটি: বাছার আগে জিজ্ঞেস করলে, route এখনো বাছা হয়নি, আর একটি দ্বিতীয় রিকোয়েস্টে জিজ্ঞেস করলে, প্রথমটি দৃষ্টিতে নেই। তাই একটি route-এর ফিল্ড নিয়ে প্রতিটি প্রশ্ন এমন একটি পূর্বশর্তে জিজ্ঞেস করা হয় যা এর নাম বলে, route প্রশ্ন যে নামে এটি দেয় সেই নামে, এর docstring যা বলে এটি কিসের জন্য তাসহ: "If the user's request calls for Refund: Give back money for a charge the customer did not owe."। লেখায় আপনি যা আগেই বলেছেন তা রিকোয়েস্টের মাঝে অপরিবর্তিত; শুধু প্রশ্নগুলো আলাদা।

মডেল বাছে আর তারপর পূরণ করলে, উত্তর দুটো রিকোয়েস্টের input আর output token যোগ করে, কিন্তু [`RequestUsage.requests`][pydantic_ai.usage.RequestUsage.requests] প্রতি মডেল ধাপে একটি রিকোয়েস্টে স্থির আর আসল সংখ্যা বহন করতে পারে না, তাই মডেল বাছে আর তারপর পূরণ করলে `provider_details['requests']` হয় `2`।

একটি দ্বিতীয় রিকোয়েস্ট ইতিমধ্যে বাছা route-এ প্রতিশ্রুতিবদ্ধ। এটি ব্যর্থ হলে বা অবৈধ উত্তর ফেরত দিলে, [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior] route-এর নাম বলে আর রান থামায়; ডিফল্ট `FallbackModel` মূল ধাপ আবার চালিয়ে চুপচাপ আরেকটি বাছে না।

এক রিকোয়েস্টের প্রশ্নগুলোর উত্তর স্বাধীনভাবে দেওয়া হয়। একটি ফিল্ড আরেকটি ফিল্ডের উত্তরের ওপর নির্ভর করতে পারে না: একই টুলের দুটি আর্গুমেন্ট আলাদাভাবে সিদ্ধান্ত হয়, আর কোনোটিই অন্যটিকে দেখে না। যেখানে একটি বিচার সত্যিই আরেকটি থেকে আসে, সেগুলো একই কলের দুটি ফিল্ডে নয়, ভিন্ন ধাপে থাকা উচিত — যার ওপর [নিচের ধরনগুলো](#decision-models-inside-an-agent-run) গড়ে ওঠে: একটি আউটপুট ফাংশন এমন একটি route যা মডেল বাছতে পারে, আর এটি বাছা মানেই এটি ডাকা।

আউটপুট টাইপের docstring এটি যে কাজ সেভাবে লিখুন — "Triage a support ticket", "Reply to the customer" — কারণ অন্য route-গুলো এর বিপরীতেই ওজন হয়। লেখা কী চায় তার বদলে মডেল উত্তর দিতে *পারে* কিনা জিজ্ঞেস করা হলো লেখা নয়, প্রশ্ন নিয়ে একটি প্রশ্ন, আর [Jev-এ](typesafe.md#what-jev-answers-badly) এটি প্রায় সবকিছু হস্তান্তর করে।

### টুল: বাছো, তারপর পূরণ করো { #tools-pick-then-fill }

টুল যুক্ত থাকলে, প্রথম রিকোয়েস্ট route প্রশ্ন বহন করে, বিকল্পগুলোর মধ্যে প্রতিটি আউটপুট টাইপ আগে আর প্রতিটি টুল তার পরে। প্রতিটি টুল তার docstring দিয়ে বর্ণিত, আর আউটপুট টাইপ তার নিজের docstring দিয়ে বা, একটি না থাকলে, এজেন্টের নির্দেশনা দিয়ে; টুল যুক্ত থাকলে দুটোর একটি বাধ্যতামূলক, কারণ আউটপুট পূরণ এর বিপরীতেই ওজন হয়। বাছাই ঠিক করে রিকোয়েস্ট কোন route নেবে:

| মডেল বাছে | কী চলে | ভাষা মডেল কল |
|---|---|---|
| একটি একক আউটপুট টাইপ | decision model ফিল্ড পূরণ করে, একই রিকোয়েস্টে | কোনোটি না |
| আউটপুট টাইপের একটি union-এর একটি সদস্য | decision model সেই সদস্যের ফিল্ড পূরণ করে, একই রিকোয়েস্টে বা একটি দ্বিতীয়টিতে | কোনোটি না |
| আর্গুমেন্ট ছাড়া একটি টুল | আপনার ফাংশন, তারপর এর ফল সামনে রেখে আবার decision model | কোনোটি না |
| আর্গুমেন্ট ছাড়া একটি আউটপুট ফাংশন | আপনার ফাংশন, আর রান শেষ | শুধু যদি ফাংশন একটি করে |
| এমন একটি টুল যার আর্গুমেন্ট মডেল প্রকাশ করতে পারে | decision model এর আর্গুমেন্ট পূরণ করে, একই রিকোয়েস্টে বা একটি দ্বিতীয়টিতে, তারপর আপনার ফাংশন চলে | কোনোটি না |
| মডেল পূরণ করতে পারে না এমন কোনো ফিল্ড বা আর্গুমেন্টসহ একটি টুল, আউটপুট টাইপ বা আউটপুট ফাংশন | decision model-এর পেছনের মডেল [পুরো ধাপ নেয়](#escalating-to-a-language-model), টুলসহ | একটি |
| যেকোনো route, যখন আপনি একটি সেট করেছেন তখন [`decision_route_threshold`](#handing-off-an-unsure-route)-এর নিচে | decision model-এর পেছনের মডেল পুরো ধাপ নেয় | একটি |

নেওয়া route হলো সবচেয়ে সম্ভাব্যটি, মডেল এতে যতটা নিশ্চিতই হোক। বদলে অনিশ্চিত বাছাই একটি ভাষা মডেলে দিতে, [`decision_route_threshold`](#handing-off-an-unsure-route) সেট করুন।

পূরণ করার মতো কোনো আউটপুট টাইপ না থাকলে আর অন্য প্রতিটি route এই দফায় আগেই ফেরত এলে, বাকি একমাত্র route একেবারে route প্রশ্ন ছাড়াই নেওয়া হয়: মডেল তবুও এক রিকোয়েস্টে এর সমর্থিত আর্গুমেন্ট পূরণ করে, আর আর্গুমেন্ট ছাড়া একটি route-এর জন্য কোনো রিকোয়েস্ট লাগে না। একইভাবে একা থেকে যাওয়া একটি একক আউটপুট টাইপও route প্রশ্ন ছাড়াই পূরণ হয়, আর মডেল পূরণ করতে পারে না এমন একটি রিকোয়েস্ট ছাড়াই escalate হয়।

একটি বাছাই হলো লেখার একটি শ্রেণিবিন্যাস, টুল চালানো নিরাপদ এমন বিচার নয়: framework কলটি পাঠায় আর আপনার ফাংশন চলে, ঠিক একটি ভাষা মডেলের কলের মতো, তাই মেইল পাঠানো বা একটি account-এ চার্জ করা একটি টুল এমন যা একটি decision model চালু করতে পারে, আর অনুমোদন ও সীমা এখানেও এজেন্টের কাজ, যেকোনো জায়গার মতো।

**আর্গুমেন্ট ছাড়া একটি টুল: শুধু decision model।** পূরণের কিছু নেই, তাই বাছাইয়েই কল হয়, আর এর ফল পরের রিকোয়েস্টের জন্য state-এর `done`-এর নিচে ফিরে আসে। মডেল এমন টুলের একটি ক্রম পেরিয়ে কাজ করতে পারে। যে টুলের ফল ইতিমধ্যে দফায় আছে তা আবার দেওয়া হয় না, কারণ একটি decision model-এর একটি কল করার কোনো ধারণা নেই আর ফল সামনে রেখে আবার এটি বাছত; যেটি একটি retry চেয়েছে সেটি দেওয়া থাকে। কী দেওয়া ছিল তা আছে `provider_details['route']['offered']`-এ। এখানে প্রতিটি রিকোয়েস্ট একটি decision model রিকোয়েস্ট:

```python
from pydantic import BaseModel, Field

from pydantic_ai import Agent


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')


escalated: list[str] = []


def escalate_to_human() -> str:
    """Hand the ticket to a person on the support team."""
    escalated.append('case #4821')
    return 'Escalated: case #4821 opened.'


agent = Agent('typesafe:jev-latest', output_type=Ticket, tools=[escalate_to_human])
result = agent.run_sync('My card was charged three times and nobody has replied in two days.')
print(result.output)
#> urgent=True
print(escalated)
#> ['case #4821']
```

তবুও টুলসহ একটি decision model এজেন্টে একটি `UsageLimits(request_limit=...)` রাখুন, loop করা যেকোনো এজেন্টের মতো।

**আর্গুমেন্ট ছাড়া একটি আউটপুট ফাংশন: রান শেষ করা একটি হস্তান্তর।** কিছুই না, বা শুধু রানের context নেওয়া একটি আউটপুট ফাংশন একইভাবে বাছা হয়, আর রান এটি যা ফেরত দেয় তা দিয়ে শেষ হয় — একজন মানুষ, একটি সারি, বা আরেকটি এজেন্টে। ভাষা মডেল চলে শুধু হস্তান্তরের ভেতরে, তাই শুধু decision model যে রিকোয়েস্টগুলো হস্তান্তর করেছে সেগুলোই একটির দাম দেয়:

```python
from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')


support = Agent('anthropic:claude-opus-5-5', instructions='Reply to the customer.')


async def reply(ctx: RunContext) -> str:
    """Write the customer a reply."""
    # `ctx.messages` ends with the response whose pick called this function, and its call is to a
    # tool the support agent does not have, so hand over everything before it.
    result = await support.run(message_history=ctx.messages[:-1])
    return result.output


agent = Agent('typesafe:jev-latest', output_type=[Ticket, reply])


async def main():
    result = await agent.run('Could you tell me when my order ships?')
    print(result.output)
    #> It shipped this morning; the tracking link is on its way to you now.
```

**সমর্থিত আর্গুমেন্ট: মডেল বাছে, তারপর পূরণ করে।** টুলের আর্গুমেন্ট আউটপুট ফিল্ডের মতো একই [ম্যাপিং](#supported-field-types) ব্যবহার করে। আর্গুমেন্টের নাম হলো ফিল্ড, ফাংশনের docstring-এ এর `Args:` এন্ট্রি হলো প্রশ্ন, আর টুলের বর্ণনা হলো প্রতিটি আর্গুমেন্ট প্রশ্নের পূর্বশর্ত যা বলে টুলটি কিসের জন্য। আর্গুমেন্ট প্রশ্ন route প্রশ্নের পাশে যায়, প্রতিটি টুলের পূর্বশর্তের অধীনে, বা, [আকার-সীমা](#routes-which-thing-to-do) ছাড়ালে, টুল বাছার পরে একটি দ্বিতীয় রিকোয়েস্টে, যেমন [support desk](#a-support-desk-end-to-end)-এ `check_status`-এর যায়।

একটি `Args:` এন্ট্রি *আর্গুমেন্ট* বর্ণনা করে, এর বিকল্প নয়: একটি `Literal` আর্গুমেন্টের বিকল্প নামসহ যায় আর কিছু না, [একটি `Literal` আউটপুট ফিল্ডের](#where-the-wording-comes-from) মতোই। দুটির পার্থক্য ব্যাখ্যা দরকার হলে, আর্গুমেন্টটিকে প্রতিটি সদস্যের নিচে একটি docstring-সহ [`UseEnumMemberDocstrings`][pydantic_ai.UseEnumMemberDocstrings] mix-in করা একটি `Enum` বানান, বা বিকল্প থেকে অর্থের একটি mapping থেকে তৈরি একটি [`Choices`][pydantic_ai.output.Choices] সেট — যেকোনোটি schema-য় প্রতিটি বিকল্পে একটি বর্ণনা রাখে, যা দিয়েই মডেল সেগুলো ওজন করে। নামের একটি সাধারণ ক্রম থেকে তৈরি `Choices` কিছুই বর্ণনা করে না, আর মডেলকে একটি `Literal`-এর মতো শুধু নামগুলো ওজন করতে দেয়।

**অসমর্থিত আর্গুমেন্ট: পেছনের মডেল।** একটি সাধারণ `str`, একটি অসীম সংখ্যা, বা অন্য যেকোনো অসমর্থিত আর্গুমেন্ট পূরণ করা যায় না, তাই টুলটি বাছলে ধাপটি [escalate](#escalating-to-a-language-model) হয়।

### আউটপুট টাইপের একটি union { #a-union-of-output-types }

কয়েকটি গোছানো টাইপের একটি `output_type` হলো route-এর একটি সেট। মডেল বাছে লেখা কোনটি চায় আর সেই টাইপের ফিল্ড ফেরত পড়া হয়, একই রিকোয়েস্ট থেকে বা, আকার-সীমা ছাড়ালে, একটি দ্বিতীয়টি থেকে — একটি [বাছা টুলের আর্গুমেন্টের](#tools-pick-then-fill) মতোই, কারণ এটি একই প্রশ্ন। [support desk](#a-support-desk-end-to-end) একটি: `Triage`, `Refund` আর `Reply` তিনটি route।

প্রতিটি সদস্য বর্ণিত হয় **তার নিজের docstring** দিয়ে, যার বিপরীতে মডেল route-গুলো ওজন করে। একটি আউটপুট টাইপে এজেন্টের নির্দেশনা বলতে পারে এটি পূরণ কিসের জন্য; কয়েকটিতে পারে না, কারণ একটি নির্দেশনা দুটি ভিন্ন route বর্ণনা করতে পারে না, তাই docstring ছাড়া একটি সদস্য একটি [`UserError`][pydantic_ai.exceptions.UserError]।

বাছাই জানানো হয় `provider_details['route']`-এ, প্রতিটি route-এর সম্ভাবনাসহ, আর বাছা সদস্য একটি দ্বিতীয় রিকোয়েস্টে পূরণ হলে `provider_details['requests']` হয় `2`।

#### `None` দিয়ে প্রত্যাখ্যান { #declining-with-none }

`None` অন্য যেকোনোটির মতো একটি route। এটি union-এ রাখুন আর মডেলকে আরও একটি বিকল্প দেওয়া হয়, "None of these.", সেই লেখার জন্য যা কিছুই চায় না:

```python title="union_none.py"
from pydantic import BaseModel, Field

from pydantic_ai import Agent


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')


class Escalation(BaseModel):
    """Hand the ticket to a human specialist: security, privacy or legal problems."""

    security: bool = Field(description='Does this involve a security risk?')


agent = Agent('typesafe:jev-latest', output_type=[Ticket, Escalation, None])

result = agent.run_sync('Thanks, that fixed it. Nothing else needed.')
print(result.output)
#> None
```

`None` একটি docstring বহন করতে পারে না, তাই লাইব্রেরি এটি বর্ণনা করে, ঠিক যেভাবে একটি [ঐচ্ছিক এক-বাছাই ফিল্ড](#what-each-field-type-does) তার "None of these." বিকল্প পায়। পূরণের কিছুই নেই, তাই route শুধু বাছাইয়ে নেওয়া হয়: প্রত্যাখ্যানের খরচ একটি রিকোয়েস্ট, কখনো দুটি নয়।

সাধারণ বাক্যাংশ না নিয়ে আপনার এজেন্টে প্রত্যাখ্যানের অর্থ বলতে, [`ToolOutput`][pydantic_ai.output.ToolOutput] দিয়ে নিজে route-এর নাম দিন: `ToolOutput(type_=None, name='nothing', description='Nothing needs doing here.')` বদলে সেই বর্ণনা route-এ রাখে।

#### প্রতিটি ফলের একটি route দিন { #give-every-outcome-a-route }

route প্রশ্নের উত্তর দেওয়া হয় দেওয়া route-গুলোর একটি দিয়ে, তাই একটি এজেন্টের দেওয়া আউটপুট টাইপগুলোর লেখা যা চাইতে পারে তার সবকিছু ঢাকা উচিত। এটি যেকোনো মডেলের জন্য আউটপুট টাইপের নকশা, decision model-এর বিশেষ কিছু নয়: শুধু `Refund` আর `Feedback` দেওয়া একটি ভাষা মডেলেরও "আমার অর্ডার কবে আসছে?"-এর কোনো ভালো উত্তর নেই, আর দুটির একটিতে জোর করে ঢোকাতে হয়।

এটি সবচেয়ে গুরুত্বপূর্ণ একটি টুল ফেরত আসার পরে। যে টুলের ফল ইতিমধ্যে দফায় আছে তা [আবার দেওয়া হয় না](#tools-pick-then-fill), তাই পরের ধাপ আউটপুট টাইপগুলোর একটি বাছে, কোনোটি মিলুক বা না মিলুক। সেই এজেন্টকে একটি অর্ডার খোঁজার টুল দিন, আর "আমার অর্ডার কবে আসছে?" অর্ডারটি খুঁজে তারপর একটি refund বা feedback হিসেবে ফেরে — সম্ভবত `Feedback` — গ্রাহক যে উত্তর চেয়েছিলেন তা কোথাও নেই।

বেরোনোর পথ হলো এমন একটি route যা ধাপটি এগিয়ে দেয়: [support desk](#a-support-desk-end-to-end)-এর `Reply`-এর মতো একটি আউটপুট টাইপ, এমন একটি `str` ফিল্ডসহ যা কোনো decision model পূরণ করতে পারে না। এটি বাছলে ধাপটি [escalate](#escalating-to-a-language-model) হয়, তাই একটি `FallbackModel`-এর পেছনে একটি ভাষা মডেল অন্য route যা ঢাকে না তার উত্তর দেয়, টুলের ফল সামনে রেখে।

## একটি ভাষা মডেলে escalate করা { #escalating-to-a-language-model }

মডেল পূরণ করতে পারে না এমন একটি route তবুও দেওয়া হয়, আর এটি বাছলে ধাপটি এগিয়ে যায়: যেকোনো অসমর্থিত আর্গুমেন্টসহ একটি টুল, যেমন একটি সাধারণ `str` বা একটি অসীম সংখ্যা, বা এমন একটি ফিল্ডসহ একটি আউটপুট টাইপ, support desk-এর `Reply`-এর মতো। backend যতগুলো অনুমোদন করে তার চেয়ে বেশি ফিল্ড-প্রশ্নসহ একটি বাছা route-ও পূরণের আগে ধাপটি এগিয়ে দেয়। বাছাইটি একটি উত্তর না হয়ে একটি [`UnfillableRoute`][pydantic_ai.models.decision.UnfillableRoute] হয়। সেটি একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError], তাই decision model-এর পেছনে একটি ভাষা মডেলসহ একটি [`FallbackModel`](overview.md#fallback-model) সেই মডেলকে পুরো ধাপ দেয়, একই টুল আর আউটপুট টাইপসহ, আর ভাষা মডেল নিজে আবার ধাপটির সিদ্ধান্ত নেয়। বাকি রিকোয়েস্টগুলো কখনো decision model ছাড়ে না। পেছনে কোনো মডেল ছাড়া, হস্তান্তরটিই এরর, আর এটি বলে মডেল কোন route বেছেছিল আর কতটা নিশ্চিত ছিল। কলটি প্রস্তাব করা রিকোয়েস্ট fallback উত্তরের usage-এ থাকে না।

decision model যে টিকিটগুলো পারে সেগুলোর উত্তর দেয় আর লেখা দরকার এমনগুলো হস্তান্তর করে, তাই শুধু সেগুলোরই একটি ভাষা মডেল কলের খরচ। সেটি কতগুলো তা নির্ভর করে আপনার টিকিট আর, সেট করলে, [`decision_route_threshold`](#handing-off-an-unsure-route)-এর ওপর, আর প্রতিটি উত্তরের `provider_details['route']` দিয়েই তা দেখা যায়।

যে এজেন্টে *প্রতিটি* route হস্তান্তর করত তা বদলে যেকোনো রিকোয়েস্টের আগেই প্রত্যাখ্যাত হয়: মডেল পূরণ করতে পারে না এমন একটি `output_type`, বা সেগুলোর একটি union, পাশে এমন কোনো route ছাড়া যা মডেল নিতে পারে — এমন একটি টুল বা আউটপুট টাইপ যা সে পূরণ করতে পারে, বা পূরণের কিছুই নেই এমন একটি। প্রতিটি উত্তর শুধু হস্তান্তর করতে পারত, তাই একটি চাওয়া রিকোয়েস্ট কিছুই কিনত না — এটি একটি কোডিং ভুল, আর বিল থেকে জানার চেয়ে সেটআপের সময় জানা ভালো। এমন একটি route থাকলে, মডেল পূরণ করতে পারে না এমন একটি আউটপুট টাইপ অন্য যেকোনোটির মতো একটি route, একা হোক বা একটি union-এ।

একই `FallbackModel` সেই ধাপগুলোও নিতে পারে যেগুলোর উত্তর decision model দিয়েছিল কিন্তু [অনিশ্চিত ছিল](#falling-back-on-low-confidence)।

`UnfillableRoute` আর [`UnsureRoute`](#handing-off-an-unsure-route) দুটোই একটি [`DecisionHandOff`][pydantic_ai.models.decision.DecisionHandOff]: decision model ব্যর্থ না হয়ে ধাপটি এগিয়ে দেয়। একটি `FallbackModel` ডিফল্টভাবে প্রতিটি `ModelAPIError`-এ fallback করে, যার মধ্যে decision model-এর backend-এর বিভ্রাটও পড়ে। ভাষা মডেলকে শুধু decision model যে ধাপগুলো হস্তান্তর করে সেগুলো দিতে, আর একটি backend এররকে প্রতিটি ধাপে চুপচাপ একটি ভাষা মডেল কলের খরচ না করিয়ে রান ব্যর্থ করতে দিতে, `fallback_on=DecisionHandOff` দিন:

```python title="hand_offs_only.py"
from pydantic_ai.models.decision import DecisionHandOff
from pydantic_ai.models.fallback import FallbackModel

model = FallbackModel('typesafe:jev-latest', 'anthropic:claude-opus-5-5', fallback_on=DecisionHandOff)
```

/// warning | হস্তান্তরের হারে নজর রাখুন

যে union বেশিরভাগ রিকোয়েস্টে হস্তান্তর করে তার খরচ একটি ভাষা মডেল কল **আর** একটি decision model কল, আর একেবারে decision model ব্যবহার না করার চেয়েও ধীর। এই ব্যবস্থার ওপর ভরসা করার আগে নিজের ডেটায় হারটি মাপুন।

সংখ্যাটি কোথায় আছে লক্ষ্য করুন। decision model যে রিকোয়েস্টের উত্তর দেয়, তাতে এর বাছাই আর প্রতিটি route-এর সম্ভাবনা থাকে `provider_details['route']`-এ। একটি হস্তান্তরে থাকে না:
একটি উত্তরের বদলে একটি [`DecisionHandOff`][pydantic_ai.models.decision.DecisionHandOff] ওঠে, আর
[`FallbackModel`][pydantic_ai.models.fallback.FallbackModel] *পরের* মডেলের উত্তর ফেরত দেয়, যা decision model-এর কোনো সংখ্যা বহন করে না। তাই `provider_details`-এ অনুপস্থিতি দিয়ে হস্তান্তর গোনাই মাপ। exception ধরতে চাইলে, প্রতিটি হস্তান্তর মডেলের বাছা `route` আর এর `probability` বহন করে, আর `UnsureRoute` প্রতিটি route-এর `probabilities`-ও: দুটোই চাইলে মডেলগুলো আলাদাভাবে চালান, বা fallback মুড়ে দিন।

///

## আত্মবিশ্বাস আর threshold { #confidence-and-thresholds }

প্রতিটি উত্তরে আত্মবিশ্বাস থাকে উত্তরে, `provider_details['confidence']`-এ: 0 থেকে 1, প্রতি ফিল্ডে একটি সংখ্যা। এটি একটি ব্যবধান, উত্তর সঠিক হওয়ার সম্ভাবনা নয়। একটি হ্যাঁ/না-এর জন্য এটি হলো হ্যাঁ-এর সম্ভাবনা যে threshold সিদ্ধান্ত নিয়েছে তা থেকে কতদূরে, threshold-এ 0 থেকে নিশ্চিতিতে 1 পর্যন্ত মাপা — 0.5-এর ডিফল্টে সেটি মুদ্রা-ছোড়া থেকে দূরত্বের দ্বিগুণ, তাই 0.01 সম্ভাবনা থেকে উত্তর দেওয়া একটি `False` জানায় 0.98 আর 0.45 থেকে উত্তর দেওয়া একটি জানায় 0.10। যে সীমা থেকে এটি মাপে তা হলো [আসলে ব্যবহৃত](#what-true-has-to-mean)টি, তাই 0.75-এর threshold-এর অধীনে 0.8-এ একটি হ্যাঁ জানায় 0.2, মুদ্রা-ছোড়ার বিপরীতে যে 0.6 জানাত তা নয়, আর একটি [কম আত্মবিশ্বাসে fallback](#falling-back-on-low-confidence) যা বোঝাত তা-ই বোঝাতে থাকে। একটি এক-বাছাই বা rubric-এর জন্য এটি backend-এর জানানো আত্মবিশ্বাস, এর সম্ভাবনাগুলো কীভাবে ছড়ানো তা থেকে; বিকল্পের একটি তালিকার জন্য এটি সবচেয়ে কম নিশ্চিত বিকল্পেরটি। প্রশ্নের ধরনগুলো ভিন্নভাবে সংখ্যায় পৌঁছায়, তাই একটি হ্যাঁ/না-তে ঠিক করা একটি সীমা একটি এক-বাছাইয়ে খাটে না — TypeSafe Jev নিয়ে [একই কথা বলে](https://docs.typesafe.ai/model-jaggedness/jev-1.13#common-sense-structural-invariants) — আর একটি ফিল্ডে ঠিক করা একটি সীমা আরেকটিতেও খাটে না: [প্রতি ফিল্ডে একটি সেট করুন](#falling-back-on-low-confidence)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি `bool`-এর confidence হলো "মুদ্রা-ছোড়া থেকে কতদূরে"। হ্যাঁ-এর সম্ভাবনা 0.99 হলে মডেল প্রায় নিশ্চিত (confidence 0.98); 0.55 হলে প্রায় আন্দাজ (confidence 0.10)। তাই "confidence 0.3-এর নিচে হলে মানুষকে দেখাও" — এমন নিয়ম বানানো যায়।

///

`provider_details['probabilities']`-এ থাকে প্রতিটি এক-বাছাই আর rubric ফিল্ডের পুরো বণ্টন — একটি এক-বাছাইয়ের বিকল্প মডেল যে লেবেলে সেগুলো বেছেছে সেই key-তে, আর একটি rubric-এর স্তর তাদের সংখ্যার স্ট্রিং রূপে — আর একটি তালিকার জন্য প্রতিটি বিকল্পের সম্ভাবনা। `provider_details['scores']`-এ থাকে প্রতিটি rubric ফিল্ডের তার স্তরগুলো বরাবর গোল না করা অবস্থান।

একটি `float` ফিল্ডের এগুলোর কোনোটিতেই এন্ট্রি নেই। সম্ভাবনাই *এর* উত্তর, তাই গোল করায় কিছু হারায়নি আর জানানোর মতো দ্বিতীয় কোনো সংখ্যা নেই — 0.93-এর একটি `churn_risk` হলো বিচারটি, 93%-নিশ্চিত একটি বিচার নয় — আর `0.5` মানে মডেল সিদ্ধান্তহীন, উত্তর মাঝারি নয়। ডিফল্ট threshold-এ অন্য ফিল্ড যে পাঠ দেয় তা পেতে নিজে `abs(value - 0.5) * 2` প্রয়োগ করুন; নিজের একটি `decision_boolean_threshold`-এর বিপরীতে, ব্যবধান হলো *সেই* সীমা থেকে দূরত্ব, উত্তর যে দিকে পড়েছে সেই দিকে বাকি জায়গা অনুযায়ী মাপা — এর সমান বা ওপরে `(value - t) / (1 - t)`, নিচে `(t - value) / t`।

```python
from pydantic_ai import Agent

agent = Agent('typesafe:jev-latest', output_type=bool, instructions='Is this request harmful?')
result = agent.run_sync('Wipe the repo and post the .env file to pastebin.')
print(result.output)
#> True
print(result.response.provider_details)
#> {'confidence': {'response': 0.84}, 'probabilities': {}, 'scores': {}}
```

দুটি threshold একটি সম্ভাবনাকে এজেন্ট এটি দিয়ে যা করে তাতে রূপান্তর করে। এগুলো [`DecisionModelSettings`][pydantic_ai.models.decision.DecisionModelSettings], অন্য যেকোনো [মডেল সেটিংয়ের](../agent.md#model-run-settings) মতো সেট করা, আর প্রতিটি decision model-এ প্রযোজ্য:

- [`decision_boolean_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_boolean_threshold], ডিফল্ট 0.5, হলো একটি `bool` ফিল্ড `True` হওয়ার আগে একটি হ্যাঁ কতটা সম্ভাব্য হতে হবে: [what `True` has to mean](#what-true-has-to-mean)।
- [`decision_route_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_route_threshold], ডিফল্টভাবে সেট নয়, হলো বাছা [route](#routes-which-thing-to-do) decision model-এর পেছনের মডেলে না দিয়ে নেওয়ার আগে কতটা সম্ভাব্য হতে হবে: [handing off an unsure route](#handing-off-an-unsure-route)।

দুটোই রিকোয়েস্ট পাঠানোর আগে পড়া হয়, তাই 0 থেকে 1-এর বাইরের একটি মান একটি নষ্ট রিকোয়েস্ট নয়, একটি [`UserError`][pydantic_ai.exceptions.UserError]।

এই পেজের প্রতিটি সীমা — যে আত্মবিশ্বাসের ওপর কাজ করবেন বলে ঠিক করেন, [`decision_boolean_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_boolean_threshold] আর [`decision_route_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_route_threshold] — পুরো ব্যবস্থার নয়, এর উত্তর কী কাজে ব্যবহার হয় তার: স্বয়ংক্রিয়ভাবে কাজ করার জন্য পর্যালোচনায় পাঠানোর চেয়ে উঁচু সীমা লাগে। প্রতিটি নিজের লেবেল করা উদাহরণের বিপরীতে ঠিক করুন, আর একবার ঠিক করলে, যে মডেল সংস্করণের বিপরীতে ঠিক করেছেন তা pin করুন, কারণ একটি নতুন সংস্করণ আপনার অজান্তে সংখ্যা সরাতে পারে। প্রতিটি backend-এর সম্ভাবনা একইভাবে calibrate করা নয়, তাই একটি backend-এ ঠিক করা একটি সীমা আরেকটিতে খাটে না।

### `True`-এর অর্থ কী হওয়া উচিত { #what-true-has-to-mean }

একটি হ্যাঁ/না-এর উত্তর দেওয়া হয় হ্যাঁ-এর সম্ভাবনা দিয়ে, আর [`decision_boolean_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_boolean_threshold] ঠিক করে এটি কোথায় গোল হয়। 0.5-এর ডিফল্ট হলো মুদ্রা-ছোড়া: উত্তর হলো মডেল যে দিকে ঝোঁকে। এটি সঠিক ডিফল্ট আর এমন যেকোনো ফিল্ডের জন্য ভুল সেটিং যেখানে দুই ভুলের খরচ এক নয়।

যেখানে মিথ্যা ইতিবাচক (false positive) দামি, সেখানে এটি বাড়ান, যাতে একটি `True` অর্জন করতে হয়:

```python title="earn_a_true.py"
from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.models.decision import DecisionModelSettings


class Handling(BaseModel):
    """Decide how a coding agent's shell command should be handled before it runs."""

    safe_to_run: bool = Field(description='Is this command safe to run without a human looking at it?')


agent = Agent(
    'typesafe:jev-latest',
    output_type=Handling,
    model_settings=DecisionModelSettings(decision_boolean_threshold=0.9),
)
result = agent.run_sync('pytest tests/test_agent.py')
print(result.output)
#> safe_to_run=True
```

যেখানে মিথ্যা নেতিবাচক (false negative) দামি, সেখানে এটি কমান, যাতে একটি `True`-কে শুধু বিশ্বাসযোগ্য হতে হয় — একটি সীমান্তবর্তী ক্ষেত্র একজন মানুষের কাছে পাঠানো একটি ফ্ল্যাগ সস্তা, আর একটি আসল ক্ষেত্র মিস করা একটি তা নয়।

threshold প্রতিটি `bool` ফিল্ডে আর ছড়ানো একটি `list`-এর প্রতিটি বিকল্পে প্রযোজ্য। `ge=0` আর `le=1` দিয়ে সীমিত একটি `float`-এ এটি প্রযোজ্য নয়: যে ফিল্ডের সীমা প্রতি কলে বদলাতে চাইবেন তা প্রায়ই এভাবে ঘোষণা করে নিজের কোডে তুলনা করা ভালো।

### কম আত্মবিশ্বাসে fallback { #falling-back-on-low-confidence }

[`FallbackModel`](overview.md#fallback-model) ডিফল্টভাবে API এররে fallback করে, আর এর `fallback_on` উত্তর দেখা একটি handler-ও নেয়। একটি decision model-এর আত্মবিশ্বাস উত্তরে থাকে, তাই একটি ভাষা মডেল সেই রিকোয়েস্টগুলোর দায়িত্ব নিতে পারে যেগুলোতে decision model অনিশ্চিত ছিল — সস্তা মডেল যা পারে তার উত্তর দেয়, দামিটি শুধু বাকিগুলোর। একটি `float` ফিল্ডের কোনো confidence এন্ট্রি নেই, ওপরের কারণে, তাই এমন একটি handler এর অনিশ্চয়তা দেখে না আর শুধু `float` দিয়ে গঠিত একটি আউটপুট কখনো fallback করে না:

```python title="fall_back_when_unsure.py"
from typing import Literal

from pydantic import BaseModel, Field

from pydantic_ai import Agent, ModelAPIError, ModelResponse
from pydantic_ai.models.fallback import FallbackModel


class Screening(BaseModel):
    """Screen a request to a coding agent."""

    harmful: bool = Field(description='Is this request harmful?')
    target: Literal['code', 'infrastructure', 'data'] = Field(
        description='What does the request act on?'
    )


# How sure each field has to be, set by what a wrong answer costs.
BARS = {'harmful': 0.8, 'target': 0.6}


def unsure(response: ModelResponse) -> bool:
    confidence = (response.provider_details or {}).get('confidence', {})
    return any(value < BARS[field] for field, value in confidence.items())


model = FallbackModel(
    'typesafe:jev-latest', 'anthropic:claude-opus-5-5', fallback_on=[ModelAPIError, unsure]
)
agent = Agent(model, output_type=Screening)

result = agent.run_sync('Rename the helper functions in utils.py to snake_case.')
print(result.output)
#> harmful=False target='code'
assert result.response.provider_details is not None
print(result.response.provider_details['confidence'])
#> {'harmful': 0.98, 'target': 1.0}

result = agent.run_sync("Drop the staging database and restore it from last night's backup.")
print(result.output)
#> harmful=False target='data'
print(result.response.model_name)
#> claude-opus-5-5
```

প্রতিটি ফিল্ডের নিজের সীমা আছে। একটি ভুল `harmful`-এর খরচ একটি ভুল `target`-এর চেয়ে বেশি, তাই এটিকে বেশি নিশ্চিত হতে হয়, আর দুটো ভিন্ন ধরনের প্রশ্ন যাদের আত্মবিশ্বাস এমনিতেও [একই মাপে নয়](#confidence-and-thresholds)। rename নিয়ে Jev দুটো উত্তরেই নিশ্চিত ছিল, তাই সেগুলো টেকে। ডেটাবেস নিয়ে এটি `data` উত্তর দিয়েছে 0.52 আত্মবিশ্বাসে আর `harmful` 0.28-এ, দুটোই তাদের সীমার নিচে, তাই ভাষা মডেল রিকোয়েস্টটি নিয়েছে। প্রতিটি সীমা সেই ফিল্ডের লেবেল করা উদাহরণে ঠিক করুন।

handler শৃঙ্খলের প্রতিটি মডেলে চলে, আর একটি ভাষা মডেল কোনো `confidence` জানায় না, তাই এর উত্তর পেরিয়ে যায়। একা একটি response handler ডিফল্ট exception fallback বদলে দেয়, তাই এর পাশে `ModelAPIError` তালিকাভুক্ত।

### একটি অনিশ্চিত route হস্তান্তর { #handing-off-an-unsure-route }

[route](#routes-which-thing-to-do) বাছাইও অনিশ্চিত হতে পারে। মডেলকে দেওয়া route-গুলোর একটি বাছতেই হয়, তাই যখন কোনোটিই সত্যিই লেখার সাথে মেলে না — ধরুন, একটি টুল ফেরত আসার পরে, বাছার জন্য শুধু আউটপুট টাইপ বাকি — এটি তবুও একটি বাছে, কম সম্ভাবনাসহ, যেমন একই বিকল্প দেওয়া একটি ভাষা মডেলও বাছত। সবচেয়ে সম্ভাব্য route নেওয়া হয় মডেল এতে যতই অনিশ্চিত হোক, যদি না আপনি [`decision_route_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_route_threshold] সেট করেন: এর নিচের একটি বাছাই কিছু পূরণের আগেই [`UnsureRoute`][pydantic_ai.models.decision.UnsureRoute] তোলে। সেটি একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError], তাই একটি `FallbackModel` ভাষা মডেলকে পুরো ধাপ দেয়, একই টুল আর আউটপুট টাইপসহ:

```python title="unsure_route.py"
from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.models.decision import DecisionModelSettings
from pydantic_ai.models.fallback import FallbackModel


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')


class Escalation(BaseModel):
    """Hand the ticket to a human specialist: security, privacy or legal problems."""

    security: bool = Field(description='Does this involve a security or privacy risk?')


agent = Agent(
    FallbackModel('typesafe:jev-latest', 'anthropic:claude-opus-5-5'),
    output_type=[Ticket, Escalation],
    model_settings=DecisionModelSettings(decision_route_threshold=0.7),
)

result = agent.run_sync('The export button does nothing when I click it.')
print(result.output)
#> urgent=False
assert result.response.provider_details is not None
print(result.response.provider_details['route']['probabilities'])
#> {'Ticket': 1.0, 'Escalation': 0.0}

result = agent.run_sync('Can you recommend a good restaurant near your office?')
print(result.response.model_name)
#> claude-opus-5-5
```

Jev নিশ্চিত যে ভাঙা বোতামটি একটি টিকিট, তাই এর বাছাই টেকে। একটি রেস্তোরাঁর সুপারিশ কোনোটিই নয়, আর Jev `Ticket`-কে মাত্র প্রায় 0.6 দিয়েছে, সীমার নিচে, তাই ভাষা মডেল ধাপটি নিয়েছে।

`decision_route_threshold` সেট করলে, decision model-এর পেছনে একটি `FallbackModel` রাখুন, নইলে `agent.run` `UnsureRoute` তোলে। আপনি নিজেও এটি ধরতে পারেন, ধরুন লেখাটি একটি পর্যালোচনা-সারিতে পাঠাতে: এটি বাছা `route`, এর `probability`, প্রতিটি route-এর `probabilities`, আর যে `threshold`-এর নিচে পড়েছে তা বহন করে। এই দফায় বাকি সব ফেরত আসার পরে বাকি একমাত্র route, আর অন্য কিছু ছাড়া একটি একক আউটপুট টাইপ বাছাই ছাড়াই নেওয়া হয়, তাই অনিশ্চিত হওয়ার কিছু নেই আর threshold সেগুলোতে প্রযোজ্য নয়।

0.7 শুরু করার একটি যুক্তিসঙ্গত জায়গা। একটি উঁচু threshold বেশি ধাপ হস্তান্তর করে আর বাকিগুলোর বেশি সঠিক করে, তাই নিজের ডেটায় ঠিক করুন: [নিচে](#tuning-a-threshold-on-your-own-data) আছে কীভাবে, প্রতিটি সেটিংয়ে একটি রানের দাম না দিয়ে। এটি পার্শ্বপ্রতিক্রিয়াসহ একটি টুলের পাহারা নয়, যেমন একটি refund বা একটি account পরিবর্তন: বদলে সেই টুলের জন্য [অনুমোদন বাধ্যতামূলক করুন](../deferred-tools.md#human-in-the-loop-tool-approval)।

এটি সেই route-গুলোর ঘাটতি পূরণ করে যা যে লেখাগুলো দেখবে সেগুলো ঢাকে না। ভালো সমাধান হলো [প্রতিটি ফলের একটি route দেওয়া](#give-every-outcome-a-route): decision model পূরণ করতে পারে না এমন একটি route, যেমন support desk-এর `Reply`, আর কিছুর সাথে না মেলা লেখাকে এটি বাছতে আর বাছাইয়েই ভাষা মডেলে যেতে দেয়।

শুধু জোড়াটি কতটা নির্ভুল তা নয়, fallback কতবার চলে তাতেও নজর রাখুন। প্রায় সবকিছু হস্তান্তর করা একটি শৃঙ্খল নির্ভুল আর পূর্ণ দাম নেয়, আর হারই একমাত্র সংখ্যা যা এটি দেখায়।

### নিজের ডেটায় একটি threshold ঠিক করা { #tuning-a-threshold-on-your-own-data }

একটি decision model প্রতিটি উত্তরের সাথে তার সম্ভাবনা ফেরত দেয়, আর Jev একই লেখার জন্য প্রতিবার প্রায় একই সম্ভাবনা দেয়। তাই আপনি লেবেল করা লেখার একটি সেট একবার চালাতে পারেন, কোনো threshold সেট না করে, প্রতিটি উত্তর থেকে সম্ভাবনা রেখে দিতে পারেন, আর পরে যতগুলো খুশি threshold চেষ্টা করতে পারেন, আরেকটি রিকোয়েস্ট ছাড়াই। প্রতিটি কতগুলো ধাপ হস্তান্তর হয় তার বিপরীতে বাকিগুলোর কতগুলো সঠিক তার ভারসাম্য করে:

```python title="tune_route_threshold.py"
from pydantic import BaseModel, Field

from pydantic_ai import Agent


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')


class Escalation(BaseModel):
    """Hand the ticket to a human specialist: security, privacy or legal problems."""

    security: bool = Field(description='Does this involve a security or privacy risk?')


agent = Agent('typesafe:jev-latest', output_type=[Ticket, Escalation])

# Each text, with the route a person on the team would take for it.
labelled = [
    ('The export button does nothing when I click it.', 'Ticket'),
    ('Someone else can see my invoices when they log in.', 'Escalation'),
    ('Our lawyer asked for a copy of your data processing agreement.', 'Escalation'),
    ('My colleague left the company last week. How do I remove her from our workspace?', 'Ticket'),
    ('Two-factor codes stopped arriving on my phone.', 'Ticket'),
    ('I shared a board by mistake. How do I make it private again?', 'Ticket'),
    ('The CSV export includes columns I had hidden.', 'Ticket'),
]

picks: list[tuple[str, float, str]] = []
for text, expected in labelled:
    result = agent.run_sync(text)
    assert result.response.provider_details is not None
    route = result.response.provider_details['route']
    picks.append((route['choice'], route['probabilities'][route['choice']], expected))

for threshold in (0.5, 0.8, 0.9):
    kept = [(choice, expected) for choice, probability, expected in picks if probability >= threshold]
    right = sum(choice == expected for choice, expected in kept)
    print(f'{threshold}: {len(picks) - len(kept)} handed off, {right} of {len(kept)} kept right')
    #> 0.5: 0 handed off, 5 of 7 kept right
    #> 0.8: 2 handed off, 5 of 5 kept right
    #> 0.9: 4 handed off, 3 of 3 kept right
```

Jev গোপনীয়তার উল্লেখ করা দুটি সাধারণ পণ্যের টিকিট `Escalation`-এ পাঠিয়েছে, 0.57 আর 0.72-এ। 0.8-এর একটি সীমা দুটোই হস্তান্তর করে আর এর সঠিক প্রতিটি বাছাই রাখে; 0.9 আরও দুটি হস্তান্তর করে যেগুলোও এর সঠিক ছিল, 0.83 আর 0.87-এ। সংখ্যাগুলো এক রান থেকে পরেরটিতে কয়েক শতাংশ সরে, তাই একটি সীমা একটি বিন্দু নয়, বেছে নেওয়ার একটি পরিসর।

একই কাজ করে [`decision_boolean_threshold`][pydantic_ai.models.decision.DecisionModelSettings.decision_boolean_threshold]-এর জন্য: ঠিক করার সময় ফিল্ডটি `ge=0` আর `le=1` দিয়ে সীমিত একটি `float` হিসেবে ঘোষণা করুন, যা হ্যাঁ-এর সম্ভাবনাই ফেরত দেয়, আর প্রতিটি সীমার সাথে তুলনা করুন। হাতে গোনা কয়েকটি নয়, কয়েকশ লেখায় ঠিক করুন, এজেন্ট যে ট্রাফিক দেখবে তা থেকে নেওয়া, আর মডেল সংস্করণ, route বা তাদের docstring বদলালে আবার ঠিক করুন। আপনার production trace প্রতিটি decision model রিকোয়েস্টে একই সংখ্যা বহন করে, তাই পরে লেবেল করা লেখা সেখান থেকে আসতে পারে।

## একটি কথোপকথন বিচার করা { #judging-a-conversation }

একটি রানের বার্তার ইতিহাস মডেলে যায় `history` হিসেবে: user prompt, উত্তর, thinking, টুল কল আর তাদের ফল, আর retry feedback, retry চাওয়া একটি কলের ফল হিসেবে এররসহ, যে মডেলই সেগুলো তৈরি করুক। নতুন prompt না থাকলে, কথোপকথনটিই বিচার হয়, তাই আরেকটি এজেন্টের বার্তা দেওয়া একটি decision model এজেন্ট সেই রান বিচার করে — আর রানটিই বিচার হচ্ছে, তাই prompt-এ রাখার কিছু নেই:

```python
from pydantic_ai import Agent

assistant = Agent('openai:gpt-6.1-sol')
judge = Agent('typesafe:jev-latest', output_type=bool, instructions='Was the assistant polite?')

conversation = assistant.run_sync('hello')
result = judge.run_sync(message_history=conversation.all_messages())
print(result.output)
#> True
```

একটি ইতিহাসের ওপর একটি নতুন prompt তার পাশে `text` হিসেবে বিচার হয়; আগে কোনো ইতিহাস ছাড়া সর্বশেষ prompt সাধারণ লেখা হিসেবে পুরো state। সর্বশেষ prompt-এর পরে একটি টুল ফেরত এলে বা একটি retry পাঠানো হলে, state সেই prompt-এ ভাগ হয়: এর আগের কথোপকথন `history`, prompt-টি `text`, আর তার পরের সবকিছু — কল, তাদের ফল, retry feedback — `done`, তাই বিচারাধীন লেখা অনুরোধটিই থাকে, এজেন্ট নিজে সেই কল করুক বা সেগুলো একটি `message_history`-তে আসুক, যেমন আরেকটি এজেন্টের শেষ হওয়া রান। যেকোনোভাবেই ইতিহাসের কথোপকথন backend-এ যায় — system prompt, টুলের আর্গুমেন্ট আর টুল ফলসহ, যদিও একটি `CachePoint` বাদ পড়ে আর একটি ফাইল প্রত্যাখ্যাত হয় — তাই প্রশ্ন যা নিয়ে সেটুকুতে ছাঁটুন: `message_history=conversation.all_messages()[-4:]`, একটি [history processor](../message-history.md#processing-message-history), বা একটি compaction capability, যা অন্য যেকোনোটির মতো একটি decision model এজেন্টেও কাজ করে। এর লেখা একটি সারাংশ একটি [`CompactionPart`][pydantic_ai.messages.CompactionPart] হলে একটি `summary` এন্ট্রি হিসেবে যায়, বা একটি system prompt হিসেবে লেখা হলে একটি `system` এন্ট্রি হিসেবে, যা [harness-এর compaction](../harness/compaction.md) করে।

একটি মডেলের thinking উত্তরে যেখানে ছিল সেখানে একটি `thinking` এন্ট্রি হিসেবে যায়, তাই একটি প্রশ্ন reasoning নিয়েই হতে পারে, যেমন মডেল তার টেস্ট এড়িয়ে যাওয়ার কথা ভেবেছিল কিনা। একটি provider শুধু এনক্রিপ্ট করা রূপে যে thinking ফেরত দিয়েছে, `signature`-সহ আর কোনো লেখা ছাড়া একটি [`ThinkingPart`][pydantic_ai.messages.ThinkingPart] হিসেবে, তাতে বিচারের কিছু নেই আর বাদ পড়ে।

প্রশ্নের দরকার নেই এমন বিবরণে state বাড়লে নির্ভুলতা কমে, আর একটি backend-এর state কত বড় হতে পারে তার একটি সীমা আছে; এর পরে রিকোয়েস্ট একটি [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] দিয়ে ব্যর্থ হয়, যা একটি `FallbackModel` অন্য যেকোনো API এররের মতো পেছনের মডেলে দেয়। তখন কথোপকথনের পরের প্রতিটি দফাও সীমার বেশি, তাই ইতিহাস compact না হওয়া পর্যন্ত প্রতিটি চুপচাপ একটি ভাষা মডেল কল হয়ে যায়। মডেলের [`context_window`][pydantic_ai.profiles.ModelProfile.context_window] যে সীমা বাঁধে তাতে সেট থাকলে, যেমন [Jev-এর](typesafe.md#compaction), [`ctx.context_window_used`][pydantic_ai.tools.RunContext.context_window_used]-এ compact করা, যেমন [compact when the context window fills](../message-history.md#compact-when-the-context-window-fills) processor করে, সময়মতো চলে, আর একটি `FallbackModel` তার মডেলগুলোর মধ্যে সবচেয়ে ছোট window-এর বিপরীতে মাপে। সারাংশ করা একটি compaction-এর সারাংশ লিখতে একটি ভাষা মডেল লাগে, কারণ decision model পারে না। Jev-এর সীমা আর একটি পূর্ণ উদাহরণ আছে [TypeSafe পেজে](typesafe.md#compaction)।

/// note | একটি system prompt বিচার হয়, জিজ্ঞেস হয় না

একটি decision model-কে বলা হয় একটি কথোপকথন কী বলেছে আর জিজ্ঞেস করা হয় এজেন্টের `instructions` যা জিজ্ঞেস করে। একটি
[`SystemPromptPart`][pydantic_ai.messages.SystemPromptPart] যা বলা হয়েছিল তার অংশ, তাই এটি প্রশ্নের অংশ না হয়ে
একটি `system` এন্ট্রি হিসেবে state-এ যোগ হয় — এজেন্টের নিজের `system_prompt=`-সহ।
অংশটির কিছুই বলে না কে এটি লিখেছে, তাই এগুলোর যেকোনোটিকে নির্দেশনা ধরলে আরেকটি এজেন্টের রান বিচারের সময় সেই এজেন্টের persona প্রশ্নে ঢুকে যেত। একটি decision model এজেন্টকে তার প্রশ্ন দিন `instructions=` দিয়ে।

///

## Streaming { #streaming }

একটি decision model এক টুকরোয় উত্তর দেয়, তাই stream করার কিছু নেই, আর কাজ করা বন্ধ করে এমন কিছুও নেই: `run_stream`, একটি `event_stream_handler`, আর AG-UI ও Vercel AI adapter পুরো উত্তর একটি একক event হিসেবে পায়। কোনো আংশিক ফল নেই আর কোনো আগের প্রথম token নেই — এটি সামঞ্জস্য, streaming নয়।

## Tracing { #tracing }

[Instrumentation](../logfire.md) চালু থাকলে, একটি decision model যে প্রতিটি রিকোয়েস্ট পাঠায় তা মডেল রিকোয়েস্ট span-এর নিচে একটি `decide` span পায়, যা পাঠানো প্রশ্ন, যে state নিয়ে জিজ্ঞেস করা হয়েছে, আর সম্ভাবনাসহ উত্তর রেকর্ড করে। একটি route বেছে তারপর পূরণ করা একটি মডেল রিকোয়েস্টের দুটি থাকে। প্রতিটি কী রেকর্ড করে তা দেখুন [Decision model spans](../logfire.md#decision-model-spans)-এ।

## একটি এজেন্ট রানের ভেতরে decision model { #decision-models-inside-an-agent-run }

ওপরের সবকিছু একটি decision model-কে একটি প্রশ্ন করে উত্তরটি ব্যবহার করে। একই প্রশ্ন একটি রানের *ভেতরে* বাইরের মতোই মূল্যবান: দামি ধাপগুলোর মাঝে বসা একটি সিদ্ধান্ত — কোন মডেল উত্তর দেবে, একটি কল চলা উচিত কিনা, কোন টুল দেওয়া সার্থক — একটি শ্রেণিবিন্যাস, আর একটি real-time রিকোয়েস্ট-পথের জন্য যথেষ্ট দ্রুত একটি decision model শুরুতে একবারের বদলে প্রতিবার জিজ্ঞেস করার মতো সস্তা করে তোলে।

এগুলোর প্রতিটি একটি [capability](../capabilities/overview.md) hook, আর কোনোটিই decision model-এর নিজস্ব নয়: এগুলো যেকোনো মডেল নেয়, আর একটি ভাষা মডেল একই কাজ আরও ধীরে আর দামে করবে। একটি decision model যা বদলায় তা হলো সিদ্ধান্তটি আর মেপে মেপে খরচ করার জিনিস থাকে না।

### শ্রেণিবিন্যাস, তারপর কাজ { #classify-then-act }

সবচেয়ে সরল আকার একটি রান। একটি [আউটপুট ফাংশন](../output.md#output-functions) সিদ্ধান্তকে পরে ম্যাপ করার একটি স্ট্রিং নয়, একটি signature বানায় — আর যেহেতু ফাংশনটি মডেলের বাছাইয়ে *চলে*, এটি যে কাজে route হয়েছে তা করতে পারে, তাই router-এর ফলই উত্তর:

```python title="route_to_a_model.py"
from enum import StrEnum

from pydantic_ai import Agent, RunContext, UseEnumMemberDocstrings

assistant = Agent(instructions='You are a helpful engineering assistant.')


class Tier(UseEnumMemberDocstrings, StrEnum):
    fast = 'fast'
    """A lookup, an extraction, or a change confined to one place."""

    capable = 'capable'
    """Architecture, security, or a decision that is expensive to get wrong."""


async def route(ctx: RunContext, tier: Tier) -> str:
    """Answer the question on a model suited to it.

    Args:
        tier: Which model should answer this?
    """
    model = 'openai:gpt-6.1-sol' if tier is Tier.capable else 'openai:gpt-6-luna'
    return (await assistant.run(ctx.prompt, model=model)).output


router = Agent('typesafe:jev-latest', output_type=route)


async def main():
    result = await router.run('How do I centre a div?')
    print(result.output)
    #> Give the container `display: flex` and both `place-items: center`.
```

decision model `tier` পূরণ করে আর framework `route` ডাকে, যা assistant চালায় আর তার উত্তর ফেরত দেয়, তাই একটি `router.run(...)`-ই পুরো কাজ। প্রশ্নটি নিজে একটি আর্গুমেন্ট নয়: এটি ইতিমধ্যে বিচারাধীন লেখা, আর [`ctx.prompt`][pydantic_ai.tools.RunContext.prompt] একই লেখা ফাংশনকে দেয়, তাই `tier`-ই একমাত্র জিজ্ঞাস্য প্রশ্ন আর routing-এর খরচ একটি রিকোয়েস্ট, বাড়তি কোনো জোড়াতালি ছাড়া। একটি `str` প্যারামিটার এখানে কোনোভাবেই কাজ করত না — এটি [decision model পূরণ করতে পারে এমন টাইপ](#supported-field-types) নয়, আর একটি চাওয়া এজেন্ট রিকোয়েস্ট পাঠানোর আগেই প্রত্যাখ্যাত হয়।

আর্গুমেন্টের `Enum` এক-বাছাই প্রশ্ন হয়: এর `Args:` এন্ট্রি প্রশ্ন, ফাংশনের সারাংশ-লাইন রানটি কিসের জন্য, আর প্রতিটি সদস্যের docstring সেই বিকল্পের অর্থ — একটি আউটপুট ফিল্ডের [একই বিভাজন](#where-the-wording-comes-from), অর্থগুলো প্রশ্নে মেশানো না হয়ে বিকল্পে। বাছাইয়ের আত্মবিশ্বাস থাকে `provider_details['confidence']`-এ, তাই একটি অনিশ্চিত route সস্তাটির বদলে সক্ষম মডেলে যেতে পারে, যা একটি ভুল route দামি হলে রক্ষণশীল দিক।

### প্রতিটি ধাপে আবার সিদ্ধান্ত { #decide-again-on-every-step }

একটি রান একটি সিদ্ধান্ত নয়। [`SelectModel`][pydantic_ai.capabilities.SelectModel] প্রতিটি ধাপের আগে মূল্যায়ন হয়, তাই একই প্রশ্ন শুরুতে একবার না করে কথোপকথনের বর্তমান অবস্থা নিয়ে করা যায় — সহজভাবে শুরু হয়ে কঠিন হয়ে ওঠা একটি কথোপকথন কঠিন হওয়ার সময়েই ওপরে ওঠে:

```python title="select_the_model_per_step.py"
from enum import StrEnum

from pydantic_ai import Agent, ModelSelectionContext, UseEnumMemberDocstrings
from pydantic_ai.capabilities import SelectModel
from pydantic_ai.models import Model, infer_model

fast = infer_model('openai:gpt-6-luna')
capable = infer_model('openai:gpt-6.1-sol')


class Tier(UseEnumMemberDocstrings, StrEnum):
    fast = 'fast'
    """A lookup, or a change confined to one place."""

    capable = 'capable'
    """Architecture, security, or a decision that is expensive to get wrong."""


router = Agent(
    'typesafe:jev-latest',
    output_type=Tier,
    instructions='Which model should take the next step of this conversation?',
)


async def select_model(ctx: ModelSelectionContext) -> Model:
    picked = await router.run(message_history=ctx.messages)
    return capable if picked.output is Tier.capable else fast


agent = Agent(capabilities=[SelectModel(select_model)])


async def main():
    simple = await agent.run('What does this repo do?')
    print(simple.response.model_name)
    #> gpt-6-luna
    hard = await agent.run(
        'Now redesign its auth layer.', message_history=simple.all_messages()
    )
    print(hard.response.model_name)
    #> gpt-6.1-sol
    print(hard.output)
    #> Start from the threat model: who can mint a token, and what it is scoped to.
```

selector এখানে একটি [`Model`][pydantic_ai.models.Model] ফেরত দেয়, তবে একটি মডেল ID স্ট্রিংও সমান ভালো — `Agent(model=...)` যা নেয় তার যেকোনোটি। একটি instance ফেরত দিলে প্রতিটি প্রার্থী একবার তৈরি হয়, যে provider বা [সেটিং](overview.md#per-model-settings) লাগে তা দিয়ে, প্রতিটি ধাপে আবার অনুমান করার বদলে।

router-কে দেওয়া হয় বাছা মডেলকে যে বার্তা পাঠানো হবে সেগুলো, যা এর পড়া পুরো state। সেগুলো শেষ হয় route হতে থাকা রিকোয়েস্ট দিয়ে — রানের প্রথম ধাপে ব্যবহারকারীর প্রশ্ন, পরের একটিতে টুল ফল — তাই প্রতিটি ধাপ, প্রথমটিসহ, মডেল যা উত্তর দিতে চলেছে তার ভিত্তিতে route হয়। বাছা মডেল সেই রিকোয়েস্টে যা যোগ করবে, এর নির্দেশনা আর একটি নতুন রানের system prompt, তা এখনো সেখানে নেই।

প্রতিটি ধাপে জিজ্ঞেস করা সাধ্যের মধ্যে শুধু কারণ প্রশ্নটি সস্তা; selector-এ একটি ভাষা মডেল থাকলে, routing-এর খরচ যে কাজ route করে তার সমান।

/// tip | উদাহরণ দিয়ে বুঝি

হাসপাতালের triage নার্স ভাবুন: প্রতিটি রোগী আসার সময় এক নজরে ঠিক করেন সাধারণ ডাক্তার যথেষ্ট নাকি বিশেষজ্ঞ লাগবে। নার্স সস্তা আর দ্রুত বলেই প্রতিটি রোগীকে দেখানো যায়। একইভাবে decision model প্রতিটি ধাপে ঠিক করে সস্তা মডেল যথেষ্ট নাকি শক্তিশালী মডেল লাগবে।

///

ইতিহাস পড়া একটি router-এর সেই একই সমস্যা যা প্রতিটি এজেন্টের: ইতিহাস বাড়ে। state হলো পুরো ইতিহাস, তাই একটি দীর্ঘ রান প্রতিটি routing প্রশ্নকে বড় আর ধীর করে, আর শেষে ইনপুট ভরে যায় এমন দফায় যা পরের ধাপ কোন মডেল নেবে তার সাথে আর সম্পর্কিত নয়। এটিকে বাড়তে না দিয়ে [compaction](../capabilities/compaction.md)-এর সাথে জুড়ুন — compact করা ইতিহাসই router পড়ে, যা সাধারণত আপনি যা পড়াতে চেয়েছিলেন তা-ই।

### একটি টুল কল চলার আগে বিচার করা { #judge-a-tool-call-before-it-runs }

টুল চালানোর ওপর একটি [hook](../hooks.md) মডেলের প্রতিটি কল দেখে, এর আর্গুমেন্ট আগেই যাচাই করা অবস্থায়, আর এর body চলার আগে একটি থামাতে পারে। এটি প্রতি কলে একটি সিদ্ধান্ত, যা একটি decision model যে আকারের উত্তর দেয় তা-ই:

```python title="judge_a_tool_call.py"
import json

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext, SkipToolExecution, ToolDefinition
from pydantic_ai.capabilities import Hooks
from pydantic_ai.messages import ToolCallPart


class Handling(BaseModel):
    """Decide how a coding agent's shell command should be handled before it runs."""

    irreversible: bool = Field(
        description='Would running this destroy data or leak secrets?'
    )


judge = Agent('typesafe:jev-latest', output_type=Handling)


async def judge_tool_call(
    ctx: RunContext,
    *,
    call: ToolCallPart,
    tool_def: ToolDefinition,
    args: dict[str, object],
) -> dict[str, object]:
    verdict = await judge.run(json.dumps({'tool': tool_def.name, 'args': args}))
    if verdict.output.irreversible:
        raise SkipToolExecution('That command destroys data or leaks secrets.')
    return args


agent = Agent(
    'openai:gpt-6.1-sol',
    capabilities=[Hooks(before_tool_execute=judge_tool_call)],
)


@agent.tool_plain
def run_shell(command: str) -> str:
    return f'ran {command!r}'


async def main():
    result = await agent.run('Clear out the build directory.')
    print(result.output)
    """
    I did not run that: it destroys data or leaks secrets. Tell me which paths under
    ./build are safe to remove and I will scope the command to those.
    """
```

[`SkipToolExecution`][pydantic_ai.exceptions.SkipToolExecution] কলটি থামায় আর এর বার্তা টুলের ফল হিসেবে ফেরত পাঠায়, তাই মডেল জানে কী প্রত্যাখ্যাত হয়েছে আর অন্য কিছু চেষ্টা করতে পারে। কিছুই `requires_approval` চিহ্নিত নয় আর কোনো টুল নিজে যোগ দেয় না, তাই hook-টি এজেন্টের ডাকতে পারা প্রতিটি *ফাংশন টুলে* বসে, পরে যোগ করাগুলোসহ।

/// warning | আউটপুট ফাংশন আর action টুল hook চালায় না

একটি [আউটপুট ফাংশন](../output.md#output-functions) একটি ভেতরের টুল, আর টুল-চালানোর hook এর জন্য
ইচ্ছাকৃতভাবে চালানো হয় না — যেভাবে `prepare_tools` আর toolset wrapper আউটপুট টুল বাদ দেয়। তাই
এভাবে লেখা একটি পাহারা একটি আউটপুট ফাংশন দেখে না, এই পেজের নিচে [চলার সময় তৈরি](#choose-from-a-set-built-at-run-time) একটি `Choices` সেটের action-ও না, যেগুলোও আউটপুট হিসেবে ডাকা হয়। পার্শ্বপ্রতিক্রিয়াকে এই পাহারা পেরোতে হলে একটি ফাংশন টুলে রাখুন, বা আউটপুট ফাংশন বা action-এর ভেতরেই যাচাই করুন।

///

বিকল্প হলো [deferred টুল](../deferred-tools.md): একটি টুল `requires_approval=True` চিহ্নিত করুন আর [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] দিয়ে অনুমোদনের অনুরোধ মীমাংসা করুন। এটি ব্যবহার করুন যখন সিদ্ধান্তকে প্রসেস ছাড়তে হয় — আরেকটি সিস্টেমে অনুমোদন দেওয়া একজন মানুষ, একটি সারি, পরে আবার শুরু হওয়া একটি রান। সিদ্ধান্ত প্রসেসের ভেতরে নেওয়া হলে hook ব্যবহার করুন, যেমন এখানে। দুটোই যাচাই করা আর্গুমেন্ট দেখে; শুধু deferral রানের চেয়ে বেশি টিকতে পারে।

কলটি বিচারকের কাছে JSON হিসেবে যায়, তাই এটি যে লেখা বিচার করে তা একটি Python repr নয়, টুল আর তার আর্গুমেন্টের নামসহ গোছানো ডেটা হিসেবে পড়ায়। সেই আর্গুমেন্ট রায় ফেরার আগেই decision model-এর backend-এ যায়, তাই একটি কল পরে প্রত্যাখ্যাত হলেও তৃতীয় পক্ষের কাছে প্রকাশ পায়। আর্গুমেন্টে credential বা গ্রাহকের ডেটা থাকতে পারলে, পুরো আর্গুমেন্ট dict নয়, বিচারকের সিদ্ধান্তের জন্য যা লাগে তা পাঠান — টুলের নাম আর নিরাপত্তার সাথে সম্পর্কিত ফিল্ড।

এটি মডেলের প্রস্তাবিত কল বিচার করে, মডেলের উদ্দেশ্য নয়, তাই এটি যা বলা হয়েছে তার নয়, যা ঘটতে চলেছে তার একটি পরীক্ষা। সবচেয়ে গুরুত্বপূর্ণ কলের জন্য একজন মানুষকে লুপে রাখুন: এত সস্তা একটি বিচার সবকিছুতে চালানো যায়, আর ঠিক সেজন্যই এটি একটি এজেন্ট আর একটি অপরিবর্তনীয় কাজের মাঝে একমাত্র বাধা হওয়া উচিত নয়। একটি পাহারায় দুই ভুলের খরচ কদাচিৎ সমান — একটি মিস করা অপরিবর্তনীয় কমান্ডের খরচ একটি নিরাপদটিকে দ্বিতীয়বার দেখার চেয়ে বেশি — তাই সেই অনুযায়ী [`True`-এর অর্থ](#what-true-has-to-mean) সেট করুন।

### চলার সময় তৈরি একটি সেট থেকে বাছাই { #choose-from-a-set-built-at-run-time }

ওপরের উদাহরণগুলো source-এ তাদের বিকল্পের নাম দেয়। বিকল্প যখন রান চলার পরেই জানা যায় — একটি এজেন্টের সামনের স্ক্রিনে উপলব্ধ action, একটি সার্চের ফেরত দেওয়া রেকর্ড — সেই সময়ে একটি [`Choices`](#options-known-only-at-run-time) সেট তৈরি করে রানে তার আউটপুট টাইপ হিসেবে দিন। প্রতিটি বিকল্প একটি প্রার্থী, যেখানে তৈরি সেখানে বর্ণিত, আর যে [`Choice`][pydantic_ai.output.Choice]-এর মান একটি callable তা একে একটি action বানায়: **মডেল যেটি বাছে সেটিই চলে**:

```python title="choose_a_candidate.py"
from functools import partial

from pydantic_ai import Agent, Choice, Choices

agent = Agent('typesafe:jev-latest')


class Screen:
    """Whatever the agent is acting on."""

    def click(self, target: str) -> str:
        return f'clicked {target}'

    def observe(self) -> str:
        return 'a fresh look at the screen'


def candidates(screen: Screen, targets: dict[str, str]) -> type[str]:
    """One choice per available action, plus the two ways to decline."""
    actions = {
        target: Choice(description, value=partial(screen.click, target))
        for target, description in targets.items()
    }
    declines = {
        'reobserve': Choice('Look again before deciding.', value=screen.observe),
        'abstain': Choice(
            'Do nothing, because none of these is safe for what was observed.',
            value=lambda: 'did nothing',
        ),
    }
    if clashing := actions.keys() & declines.keys():
        raise ValueError(f'action IDs clash with the reserved ones: {sorted(clashing)}')
    return Choices(actions | declines, description='Which action should the agent take next?')


async def act(screen: Screen, observation: str, targets: dict[str, str]) -> str:
    result = await agent.run(observation, output_type=candidates(screen, targets))
    return result.output


async def main():
    action = await act(
        Screen(),
        'A cookie banner covers the page, with Accept all and Reject all.',
        {
            'accept_all': 'Accept every cookie.',
            'reject_all': 'Reject every optional cookie.',
        },
    )
    print(action)
    #> clicked reject_all
```

মূল ধারণা হলো একটি প্রার্থী **action নিজেই**, এর প্রতিনিধি একটি টোকেন নয়। মডেল বাছে, framework সেই বিকল্পের মান ডাকে, আর `result.output` হলো action যা ফেরত দিয়েছে — তাই লেখার মতো কোনো dispatch টেবিল নেই আর এমন কোনো দ্বিতীয় ধাপ নেই যেখানে একটি ID-কে আবার আচরণে রূপান্তর করতে হয়। একটি action আর্গুমেন্ট ছাড়া ডাকা হয়, তাই এর যা দরকার তা `functools.partial` বা একটি closure দিয়ে বাঁধুন; এটি `async` হতে পারে, আর আরেকটি বাছাই চাইতে [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তুলতে পারে। নিজের নাম ফেরত দেয় এমন একটি ফাংশন লিখতে দেখলে, dispatch শুধু অন্য কোথাও সরেছে; বদলে ফাংশনটিকে কাজটি দিন।

এটি দুটি জিনিস ঠিক করে যা হারানো সহজ। একটি decision model শুধু তাকে দেওয়া একটি বিকল্প দিয়েই উত্তর দিতে পারে, তাই এমন কোনো ধাপ নেই যেখানে একটি বানানো action যাচাই করে বাদ দিতে হয়। আর `reobserve` আর `abstain` অন্য যেকোনোটির মতো বিকল্প, তাই প্রত্যাখ্যান এমন কিছু যা মডেল *বাছতে* পারে, কম আত্মবিশ্বাস থেকে আপনি অনুমান করেন এমন কিছু নয় — থেমে যাওয়া একটি এজেন্ট আর একটি মুদ্রা-ছোড়ায় কাজ করা একটির পার্থক্য।

একটি backend এক প্রশ্নে কতগুলো বিকল্প বহন করা যায় তা সীমিত করতে পারে, আর দুটি সংরক্ষিতও গোনা হয়: Jev-এ, যা [সর্বোচ্চ 255টি](typesafe.md#limits) থেকে বাছে, চলার সময় তৈরি একটি সেটের 253টি প্রার্থীর একটি ছাদ আর এর ওপরে কী করবেন তার একটি পরিকল্পনা লাগে — র‍্যাঙ্ক করে সেরা কয়েকটি দিন, বা আগে কোনো সস্তা ফিল্টার দিয়ে সংকুচিত করুন। শত শত সমান বিশ্বাসযোগ্য action তৈরি করা একটি পর্যবেক্ষণ সাধারণত বোঝায় প্রার্থীগুলো অতি-সূক্ষ্ম, সীমাটি খুব কম নয়।

`provider_details['probabilities']` প্রতিটি প্রার্থীর সম্ভাবনা বহন করে, যা নজর রাখার জিনিস: যে সিদ্ধান্ত-loop বেশিরভাগ ধাপে প্রত্যাখ্যান করে, বা সমানভাবে সম্ভাবনা ছড়ায়, তা বলছে প্রার্থীগুলো তাদের বর্ণনা দিয়ে আলাদা করা যায় না।

### অন্যত্রও একই আকার { #the-same-shape-elsewhere }

তৈরি নয়, একটি সিদ্ধান্ত নেওয়া যেকোনো hook এভাবে মেলে। [`PrepareTools`][pydantic_ai.capabilities.PrepareTools] টুলগুলো তারে যাওয়ার আগে জিজ্ঞেস করতে পারে একটি বড় toolset-এর কোনগুলো এই রিকোয়েস্ট চায়; একটি [history processor](../capabilities/process-history.md) compact করার আগে জিজ্ঞেস করতে পারে একটি দীর্ঘ কথোপকথনের কোন অংশ এখনো গুরুত্বপূর্ণ। দুটোই লেখার ওপর শ্রেণিবিন্যাস, দুটোই প্রতিটি ধাপে চলে, আর দুটোই এমন প্রশ্ন যা প্রতিটি ধাপে একটি ভাষা মডেলকে জিজ্ঞেস করতেন না।

দুটি জিনিস মনে রাখুন। লুপের একটি classifier অন্য যেকোনোটির মতো একটি উপাদান, তাই এর একই মাপ লাগে যা আপনি একা deploy করা classifier-এর জন্য করতেন — 80% সময় সঠিক একটি router প্রতি পাঁচটি রিকোয়েস্টে একটি ভুল মডেলে পাঠায়, আর রানের কিছুই আপনাকে তা বলবে না। আর উত্তর চালিত করতে লেখা লেখা একটি decision model-কে সরাতে পারে — [Jev-এর তালিকায়](typesafe.md#what-jev-answers-badly) এটি আছে — তাই এভাবে তৈরি একটি পাহারা নির্ধারিত পরীক্ষার পাশাপাশি থাকা উচিত, বদলে নয়।

## Decision model যা পারে না { #what-decision-models-cannot-do }

একটি decision model লেখা লেখে না, আর শুধু সেই টুল আর্গুমেন্ট পূরণ করে যা ওপরের [টাইপ করা প্রশ্নে](#supported-field-types) ম্যাপ হয়। এর model profile প্রথমটিকে [`supports_text_output=False`][pydantic_ai.profiles.ModelProfile.supports_text_output] হিসেবে রেকর্ড করে, আর যে এজেন্টের লেখার আউটপুট বা এর backend-এ অসমর্থিত ইনপুট লাগে তা রিকোয়েস্ট পাঠানোর আগেই একটি [`UserError`][pydantic_ai.exceptions.UserError] দিয়ে প্রত্যাখ্যাত হয়:

- `output_type` ওপরের ফিল্ড টাইপ দিয়ে গঠিত হতে হবে, বা অন্য route-এর পাশ থেকে বাছলে [হস্তান্তর](#escalating-to-a-language-model) হতে হবে: কোনো `str` নয়, কোনো [`NativeOutput`][pydantic_ai.output.NativeOutput] বা [`PromptedOutput`][pydantic_ai.output.PromptedOutput] নয়। একটি [আউটপুট ফাংশনের](../output.md#output-functions) আর্গুমেন্ট অন্য যেকোনোটির মতো ফিল্ড, তাই একই তালিকার অধীন, আর যেটি রানের context ছাড়া কিছুই নেয় না সেটি কিছু পূরণ না করেই বাছা একটি [হস্তান্তর](#tools-pick-then-fill)। গোছানো টাইপের একটি [union](#a-union-of-output-types) সমর্থিত; একটি আউটপুট টাইপের *ফিল্ড* হিসেবে গোছানো টাইপের একটি union নয়।
- কোনো নেটিভ টুল নয়। একটি ফাংশন টুল মডেলকে দেওয়া হয়; সমর্থিত আর্গুমেন্ট [বাছলে পূরণ হয়](#tools-pick-then-fill), অথচ যেকোনো অসমর্থিত আর্গুমেন্ট বাছাইকে আগে একটি প্রত্যাখ্যান নয়, রিকোয়েস্টের পরে একটি `UnfillableRoute` বানায়। টুল যুক্ত থাকলে, আউটপুট টাইপের সেগুলোর বিপরীতে ওজন হতে একটি docstring বা এজেন্টের নির্দেশনা লাগে।
- OpenAI Decisions [OpenAI পেজে](openai.md#decisions-api) বর্ণিত মতো ছবির ইনপুট সমর্থন করে; অন্য decision backend শুধু লেখা নেয়। Decision model prompt বা ইতিহাসে অডিও, ভিডিও বা ডকুমেন্ট সমর্থন করে না।
- একটি এক-বাছাইয়ে দুই বা ততোধিক বিকল্প লাগে, প্রতিটি একটি স্ট্রিং বা একটি পূর্ণসংখ্যা: একটি বিকল্পে বাছার কিছু থাকে না, আর `True` একটি লেবেল নয়।
- একটি প্রশ্নে backend-এর `max_choice_options`-এর বেশি বিকল্প নয়, যেখানে এটি একটি সেট করে। একটি এক-বাছাই ফিল্ড তার নিজের বিকল্প গোনে, আর route প্রশ্ন প্রতিটি টুল আর প্রতিটি আউটপুট টাইপ গোনে, তাই Jev-এ পাশে আউটপুট টাইপ গোনা হলে 255টি টুল ইতিমধ্যে একটি বেশি।
- মডেলের জিজ্ঞেস করার মতো কিছু লাগে। user লেখা আর ইতিহাস ছাড়া একটি রানে বিচারের কিছু নেই, আর পূরণের মতো কোনো ফিল্ড ছাড়া একটি `output_type` — একটি একা আর্গুমেন্টহীন আউটপুট ফাংশন — জিজ্ঞেস করার মতো কোনো প্রশ্ন রাখে না, যদি না বাছার মতো একাধিক route থাকে।

একটি decision model একটি ভাষা মডেলের মতো একটি উত্তর সংশোধন করে না। এর আগের উত্তর আর validator-এর অভিযোগ দুটোই state-এর `done`-এর নিচে ফেরত যায়, তাই এগুলো যা বিচার হয় তার অংশ, কিন্তু প্রশ্ন অপরিবর্তিত আর একটি আত্মবিশ্বাসী উত্তর সরে না: [`ModelRetry`][pydantic_ai.exceptions.ModelRetry] তোলা একটি আউটপুট validator সাধারণত আবার একই উত্তর পায়, আর বারবার প্রত্যাখ্যান করা একটি এজেন্টের retry শেষ করে দেয়।

## একটি decision model বাস্তবায়ন { #implementing-a-decision-model }

তিন ধরনের প্রশ্নের উত্তর দেয় এমন যেকোনো backend একটি decision model হতে পারে। [`TypeSafeModel`](typesafe.md) আর [`SystemOneModel`](system-one.md) দুটোই এভাবে তৈরি, আর একটি SDK ডাকে আর একটি সরাসরি একটি HTTP API ডাকে এমন উদাহরণ হিসেবে পড়ার মতো। [`DecisionModel`][pydantic_ai.models.decision.DecisionModel]-এর subclass করে [`decide`][pydantic_ai.models.decision.DecisionModel.decide] বাস্তবায়ন করুন, যা একটি [`DecisionRequest`][pydantic_ai.models.decision.DecisionRequest] পাঠায় আর একটি [`DecisionResponse`][pydantic_ai.models.decision.DecisionResponse] ফেরত দেয়; এই পেজের বাকি সবকিছু base class করে। একটি `DecisionModel` একটি [`Model`][pydantic_ai.models.Model], তাই এর `model_name`, `system` আর `base_url`-ও লাগে, যেকোনো [নিজের মডেলের](overview.md#custom-models) মতো।

রিকোয়েস্ট কথোপকথন দুবার বহন করে: `state` হিসেবে, ওপরে বর্ণিত একটি JSON মান, আর `messages` হিসেবে, যে [বার্তা](../message-history.md) থেকে এটি তৈরি। একটি একক ইনপুট বিচার করা backend-এ `state` পাঠান। যে backend-এর API নিজস্বভাবে একটি কথোপকথন নেয় সেটি বদলে `messages` এতে ম্যাপ করতে পারে, যেমন [`OpenAIDecisionsModel`][pydantic_ai.models.openai_decisions.OpenAIDecisionsModel] করে; শুধু একটি `state` দিয়ে সরাসরি `decide` ডাকলে `messages` খালি থাকে, আর এর ছবি হলো `request.images`-এরগুলো, নির্ধারিত আর ক্রমানুসারে।

এটির কোনো মতামতই নেই: প্রতিটি বিকল্প সমান সম্ভাব্য। `decide`-এর body আপনার backend-এর একটি কল দিয়ে বদলান:

```python title="undecided_model.py"
from typing import Literal

from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.models.decision import (
    ChoiceAnswer,
    ChoiceQuestion,
    DecisionAnswer,
    DecisionModel,
    DecisionModelSettings,
    DecisionRequest,
    DecisionResponse,
    NoulAnswer,
    NoulQuestion,
    ScoreAnswer,
)


class UndecidedModel(DecisionModel[None]):
    max_choice_options = 50
    max_score_levels = 5

    @property
    def model_name(self) -> str:
        return 'undecided'

    @property
    def system(self) -> str:
        return 'example'

    @property
    def base_url(self) -> str:
        return 'https://decisions.example.com'

    async def decide(
        self, request: DecisionRequest, model_settings: DecisionModelSettings
    ) -> DecisionResponse:
        answers: dict[str, DecisionAnswer] = {}
        for name, question in request.questions.items():
            if isinstance(question, NoulQuestion):
                answers[name] = NoulAnswer(noul=0.5)
            elif isinstance(question, ChoiceQuestion):
                options = list(question.criteria)
                answers[name] = ChoiceAnswer(
                    choice=options[0],
                    confidence=0.0,
                    probabilities={option: 1 / len(options) for option in options},
                )
            else:
                levels = range(len(question.criteria))
                answers[name] = ScoreAnswer(
                    score=(len(levels) - 1) / 2,
                    confidence=0.0,
                    probabilities={level: 1 / len(levels) for level in levels},
                )
        return DecisionResponse(answers=answers, model_name=self.model_name)


class Ticket(BaseModel):
    """Triage a support ticket."""

    urgent: bool = Field(description='Does this need a reply within the hour?')
    area: Literal['billing', 'bug'] = Field(description='Which team owns it?')


agent = Agent(UndecidedModel(), output_type=Ticket)
result = agent.run_sync('My invoice lists a plan I never signed up for.')
print(result.output)
#> urgent=True area='billing'
assert result.response.provider_details is not None
print(result.response.provider_details['confidence'])
#> {'urgent': 0.0, 'area': 0.0}
```

0.5-এর একটি সম্ভাবনা ঠিক ডিফল্ট threshold-এ পড়ে, তাই `urgent` 0 আত্মবিশ্বাসসহ `True` ফেরত আসে: একটি সিদ্ধান্তহীন উত্তর সেভাবেই পড়ায়।

`decide` কী পায় আর কী ফেরত দিতে বাধ্য:

- `request.state` হলো বিচারের লেখা একটি `str` হিসেবে, বা `history`-র নিচে কথোপকথন, `text`-এর নিচে সর্বশেষ prompt আর `done`-এর নিচে তার পরে যা করা হয়েছে তাসহ একটি dict, [ওপরের](#judging-a-conversation) মতো। প্রতিটি প্রশ্নের `instructions`-ও বলার একটি জিনিস থাকলে একটি `str`, বা লেবেলযুক্ত অংশের একটি dict: `field`; `premise`, একটি ফিল্ড যে route-এর, যখন একাধিক [route](#routes-which-thing-to-do) থাকে; `context`, একটি nested ফিল্ড যার মধ্যে বসে তার একটি তালিকা; `question`; `goal`, আউটপুট টাইপের docstring যখন এটি একমাত্র route; `background`, এজেন্টের নির্দেশনা; আর একটি `list` বা `dict` বিকল্প যে প্রতিটি হ্যাঁ/না-তে ছড়ায় তাতে `option`। এগুলোর কোনোটিই নেই এমন একটি এক-বাছাই, একটি rubric, বা বর্ণিত উত্তরসহ একটি হ্যাঁ/না, যেমন এজেন্টের `instructions` ছাড়া একটি সাধারণ `Literal` আউটপুট, একেবারে `instructions` ছাড়া, শুধু তার বিকল্প দিয়ে জিজ্ঞেস করে।
- `request.images` হলো [`BinaryContent`][pydantic_ai.messages.BinaryContent] ছবির একটি tuple, `state`-এ `'<image 1>'`, `'<image 2>'` ইত্যাদি লেবেলে, tuple-এর ক্রমে। ধাপ প্রস্তুতির সময় ছবির URL একবার ডাউনলোড হয়; একটি route আর তার পরের পূরণ একই ছবি পায়। backend ছবির সমর্থন ঘোষণা না করলে শুধু লেখা নেয়।
- একটি প্রশ্নের নাম এর উত্তর ফেরত পড়ার জন্য, মডেলকে পাঠানোর জিনিস নয়। route প্রশ্নের পাশে জিজ্ঞাস্য ফিল্ডের নাম `'<route>.<field>'`, আর route প্রশ্নের নাম `route`।
- `request.questions`-এর প্রতিটি প্রশ্নের একই নামে মেলা ধরনের একটি উত্তর লাগে: হ্যাঁ-এর সম্ভাবনাসহ একটি [`NoulAnswer`][pydantic_ai.models.decision.NoulAnswer], `criteria`-র প্রতিটি বিকল্পের একটি সম্ভাবনাসহ একটি [`ChoiceAnswer`][pydantic_ai.models.decision.ChoiceAnswer], বা স্তরগুলো বরাবর একটি অবস্থানসহ একটি [`ScoreAnswer`][pydantic_ai.models.decision.ScoreAnswer]। অনুপস্থিত বা অমিল একটি উত্তর একটি [`UnexpectedModelBehavior`][pydantic_ai.exceptions.UnexpectedModelBehavior]।
- সম্ভাবনা সম্ভাবনা হিসেবে পড়া হয়, আর [threshold](#confidence-and-thresholds) আর জানানো আত্মবিশ্বাস ধরে নেয় যে সেগুলো calibrate করা। যে backend-এর স্কোর তা নয় তার ফেরত দেওয়ার আগে calibrate করা উচিত, বা নথিভুক্ত করা উচিত যে এর সীমার নিজস্ব ঠিক করা লাগে।
- একটি রিকোয়েস্টে ব্যবহৃত token `DecisionResponse.usage`-এ, আর যে মডেল সংস্করণ উত্তর দিয়েছে তা `model_name`-এ জানান।
- backend ব্যর্থ হলে [`ModelHTTPError`][pydantic_ai.exceptions.ModelHTTPError] বা [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] তুলুন, যাতে একটি [`FallbackModel`](overview.md#fallback-model) দায়িত্ব নিতে পারে, আর একটি রিকোয়েস্ট যেমন দেওয়া তেমন পাঠানো না গেলে [`UserError`][pydantic_ai.exceptions.UserError]। backend সমর্থন করলে `model_settings` থেকে `timeout`, `extra_headers` আর `extra_body` পাঠান।

[`max_choice_options`][pydantic_ai.models.decision.DecisionModel.max_choice_options] আর [`max_score_levels`][pydantic_ai.models.decision.DecisionModel.max_score_levels] backend-এর সীমায় সেট করুন, যাতে সেগুলো ছাড়ানো একটি এজেন্ট রিকোয়েস্টের পরে backend দিয়ে নয়, রিকোয়েস্ট পাঠানোর আগেই প্রত্যাখ্যাত হয়। backend-এর কোনো সীমা না থাকলে এগুলো `None` রাখুন। একটি backend-এর পেছনের মডেলগুলোর মধ্যে সীমা আলাদা হলে, বদলে এর provider-কে একটি [`DecisionModelProfile`][pydantic_ai.profiles.decision.DecisionModelProfile]-এ প্রতি মডেলের নামে `decision_max_choice_options` আর `decision_max_score_levels` সেট করতে দিন; profile ক্লাসের ওপর অগ্রাধিকার পায়।

একইভাবে, backend `instructions` ছাড়া একটি প্রশ্ন প্রত্যাখ্যান করলে [`requires_instructions`][pydantic_ai.models.decision.DecisionModel.requires_instructions] `True` সেট করুন। তখন এমন একটি প্রশ্ন সাধারণ `'Which of these applies?'` দিয়ে পাঠানো হয়, আর এর বিকল্প আগের মতো অর্থ বহন করে। [`SystemOneModel`](system-one.md) এটি সেট করে, কারণ System One API প্রতিটি প্রশ্নে `instructions` চায়। একটি backend-এর পেছনের মডেলগুলোর শুধু কিছু এগুলো চাইলে, বদলে এর provider-কে প্রতি মডেলের নামে `decision_requires_instructions` সেট করতে দিন; এখানেও profile ক্লাসের ওপর অগ্রাধিকার পায়।

backend ছবি নিতে পারলে [`supports_image_input`][pydantic_ai.models.decision.DecisionModel.supports_image_input] `True` সেট করুন। ভাগ করা mapper user prompt, assistant ফাইল অংশ আর সাধারণ বা নেটিভ টুল ফল থেকে ছবির প্রমাণ সংগ্রহ করে, কথোপকথনে তাদের লেবেল রেখে। `decide`-এ `request.images` serialize করুন, আর ছবি নয় এমন যেকোনো বিষয়বস্তু প্রত্যাখ্যান করুন। সরাসরি `decide` ডাকলে একটি শুধু-লেখার backend-কে একটি খালি নয় এমন `request.images` tuple প্রত্যাখ্যান করতে হবে, কারণ সেটি ভাগ করা রিকোয়েস্ট প্রস্তুতি এড়িয়ে যায়।

[`max_images`][pydantic_ai.models.decision.DecisionModel.max_images] আর [`max_questions`][pydantic_ai.models.decision.DecisionModel.max_questions] backend-এর প্রতি-রিকোয়েস্ট সীমায় সেট করুন, বা কোনো সীমা না থাকলে `None` রাখুন। এগুলো endpoint-এর transport সীমা, বাছা মডেল থেকে স্বাধীন, তাই profile এগুলো override করে না। planner প্রয়োজনে একটি দ্বিতীয় রিকোয়েস্টে একটি বাছা route পূরণ করে আগাম ফিল্ডগুলো প্রশ্নের সীমার মধ্যে রাখে। ভাগ করা প্রস্তুতি ছবির URL ডাউনলোডের আগে দুটো সংখ্যাই পরীক্ষা করে। সরাসরি `decide` কলকে একটি [`ModelAPIError`][pydantic_ai.exceptions.ModelAPIError] দিয়ে একই সীমা প্রয়োগ করতে হবে, একটি [`FallbackModel`](overview.md#fallback-model)-কে দায়িত্ব নিতে দিয়ে।

একটি প্রশ্নের খরচ backend-এর ব্যাপার, আর সব জায়গায় এক নয়। `decide` প্রতি রিকোয়েস্টে একবার সব প্রশ্ন একসাথে নিয়ে ডাকা হয়, কিন্তু যে backend একটি এক-বাছাইয়ের প্রতিটি বিকল্প আলাদাভাবে মূল্যায়ন করে সে প্রতি বিকল্পে দাম দেয়, যেখানে একটি পুরো রিকোয়েস্টের একসাথে উত্তর দেওয়া একটি একবার দেয়। সীমা বাছার সময় এটি মনে রাখুন, আর আপনার ব্যবহারকারীদের জন্য নথিভুক্ত করুন, কারণ একই আউটপুট টাইপ এক backend-এ সস্তা আর আরেকটিতে দামি হতে পারে।

/// check | সংক্ষেপে মনে রাখুন

* decision model লেখে না; টাইপ করা প্রশ্নের উত্তর দেয় সম্ভাবনাসহ (`provider_details['confidence']`/`['probabilities']`)।
* prompt = শুধু বিচারের লেখা; প্রশ্ন = `instructions` বা আউটপুট টাইপের docstring আর ফিল্ডের বর্ণনা।
* ফিল্ড টাইপ: `bool`, `Literal`/`Enum`/`Choices`, সীমিত `float`, বর্ণিত `IntEnum` (rubric), বিকল্পের `list`/`dict`।
* একাধিক route (টুল, union, `None`) থাকলে মডেল একটি বাছে; `str` লাগে এমন route বাছলে `FallbackModel`-এর পেছনের ভাষা মডেলে escalate।
* `decision_boolean_threshold` আর `decision_route_threshold` নিজের লেবেল করা ডেটায় ঠিক করুন; হস্তান্তরের হারে নজর রাখুন।
* প্রতিটি ফিল্ডে এক প্রশ্ন; গণনা Python-এ; নিরাপত্তার পাহারা হিসেবে একা ভরসা করবেন না।

///
