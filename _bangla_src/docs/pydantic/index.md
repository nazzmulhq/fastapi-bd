# Pydantic Validation { #pydantic-validation }

[![CI](https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg)](https://coverage-badge.samuelcolvin.workers.dev/redirect/pydantic/pydantic)<br>
[![pypi](https://img.shields.io/pypi/v/pydantic.svg)](https://pypi.python.org/pypi/pydantic)
[![CondaForge](https://img.shields.io/conda/v/conda-forge/pydantic.svg)](https://anaconda.org/conda-forge/pydantic)
[![downloads](https://static.pepy.tech/badge/pydantic/month)](https://pepy.tech/project/pydantic)<br>
[![license](https://img.shields.io/github/license/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/blob/main/LICENSE)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://pydantic.dev/docs/validation/latest/llms.txt)

এটি ডেভেলপমেন্ট সংস্করণের ডকুমেন্টেশন: [v2.15.0a0+dev](https://github.com/pydantic/pydantic/releases)।

/// note | এই পেজে যা জানবেন

* Pydantic কী, আর "ডেটা ভ্যালিডেশন" (ডেটা যাচাই) বলতে কী বোঝায়।
* কেন এটি Python-এর সবচেয়ে জনপ্রিয় ডেটা যাচাই লাইব্রেরি।
* প্রথম একটি সহজ উদাহরণ, লাইন ধরে ধরে ব্যাখ্যাসহ।
* ভুল ডেটা এলে Pydantic কীভাবে স্পষ্ট এরর দেয়।

///

Pydantic হলো Python-এর সবচেয়ে বেশি ব্যবহৃত **ডেটা ভ্যালিডেশন** (ডেটা যাচাই) লাইব্রেরি।

এটি দ্রুত আর বাড়ানো যায় (extensible), আর আপনার linter, IDE (কোড এডিটর) আর মস্তিষ্ক, সবার সাথেই চমৎকার মানিয়ে চলে। ডেটা দেখতে কেমন হওয়া উচিত তা আপনি খাঁটি, সাধারণ Python 3.10+ দিয়ে লিখে দেন; আর Pydantic সেই অনুযায়ী ডেটা যাচাই করে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বিমানবন্দরের ইমিগ্রেশন কাউন্টারের কথা ভাবুন। প্রতিটি যাত্রীর পাসপোর্টে নাম, জন্মতারিখ, ভিসা ঠিক আছে কিনা অফিসার দেখে নেন। সব ঠিক থাকলে ঢুকতে দেন, কিছু ভুল থাকলে স্পষ্ট করে বলে দেন কোনটি ভুল।

Pydantic আপনার প্রোগ্রামের সেই ইমিগ্রেশন অফিসার। বাইরে থেকে আসা ডেটা (ইউজারের ফর্ম, API রিকোয়েস্ট, ফাইল, ডেটাবেস) আপনার কোডে ঢোকার আগে Pydantic পরীক্ষা করে: বয়স কি সত্যিই সংখ্যা? ইমেইল কি সঠিক ফরম্যাটে? দরকারি ঘর কি খালি? ঠিক থাকলে ডেটা সঠিক টাইপে রূপান্তর করে দেয়, ভুল থাকলে কোথায় কী ভুল তা জানিয়ে দেয়।

///

/// info | FastAPI-এর সাথে সম্পর্ক

আপনি যদি এই সাইটে FastAPI শিখে থাকেন, তাহলে আপনি ইতিমধ্যে Pydantic ব্যবহার করেছেন! FastAPI-তে রিকোয়েস্ট বডির জন্য যে `class Item(BaseModel)` লিখেছিলেন, সেই `BaseModel` আসে Pydantic থেকে। FastAPI-এর সব ডেটা যাচাই, রূপান্তর আর JSON Schema (যা দিয়ে `/docs` তৈরি হয়) আসলে Pydantic-ই করে। এই অংশে আপনি সেই ইঞ্জিনটিকে গভীরভাবে চিনবেন।

///

**আমাদের নিউজলেটার *The Pydantic Stack*-এ সাইন আপ করুন, যেখানে Pydantic, Logfire আর Pydantic AI নিয়ে আপডেট আর টিউটোরিয়াল থাকে:**

<form method="POST" action="https://eu.customerioforms.com/forms/submit_action?site_id=53d2086c3c4214eaecaa&form_id=14b22611745b458&success_url=https://pydantic.dev/docs/validation/latest/get-started/" class="md-typeset" style="display: flex; align-items: center; gap: 0.5rem; max-width: 100%;">
    <input
    type="email"
    id="email_input"
    name="email"
    class="md-input md-input--stretch"
    style="flex: 1; background: var(--md-default-bg-color); color: var(--md-default-fg-color);"
    required
    placeholder="Email"
    data-1p-ignore
    data-lpignore="true"
    data-protonpass-ignore="true"
    data-bwignore="true"
    />
    <input type="hidden" id="source_input" name="source" value="pydantic" />
    <button type="submit" class="md-button md-button--primary">Subscribe</button>
</form>

## কেন Pydantic ব্যবহার করবেন? { #why-use-pydantic }

* **টাইপ হিন্ট দিয়ে চালিত** &mdash; Pydantic-এ স্কিমা যাচাই আর সিরিয়ালাইজেশন (ডেটাকে JSON-এর মতো রূপে বদলানো) নিয়ন্ত্রিত হয় টাইপ অ্যানোটেশন দিয়ে; শেখার বিষয় কম, লেখার কোড কম, আর আপনার IDE ও স্ট্যাটিক অ্যানালাইসিস টুলের সাথে সংযোগ। [আরও জানুন…](why.md#type-hints)
* **গতি** &mdash; Pydantic-এর মূল যাচাইয়ের যুক্তি Rust-এ লেখা। ফলে Pydantic Python-এর দ্রুততম ডেটা যাচাই লাইব্রেরিগুলোর একটি। [আরও জানুন…](why.md#performance)
* **JSON Schema** &mdash; Pydantic মডেল থেকে JSON Schema তৈরি করা যায়, ফলে অন্য টুলের সাথে সহজে যুক্ত করা যায়। [আরও জানুন…](why.md#json-schema)
* **Strict** আর **Lax** মোড &mdash; Pydantic strict (কঠোর) মোডে চলতে পারে, যেখানে ডেটা রূপান্তর হয় না; অথবা lax (নমনীয়) মোডে, যেখানে উপযুক্ত হলে Pydantic ডেটাকে সঠিক টাইপে রূপান্তরের চেষ্টা করে। [আরও জানুন…](why.md#strict-lax)
* **Dataclass**, **TypedDict** এবং আরও অনেক কিছু &mdash; Pydantic `dataclass` আর `TypedDict`-সহ স্ট্যান্ডার্ড লাইব্রেরির অনেক টাইপ যাচাই করতে পারে। [আরও জানুন…](why.md#dataclasses-typeddict-more)
* **কাস্টমাইজেশন** &mdash; কাস্টম validator আর serializer দিয়ে ডেটা কীভাবে প্রসেস হবে তা অনেক শক্তিশালী উপায়ে বদলানো যায়। [আরও জানুন…](why.md#customisation)
* **ইকোসিস্টেম** &mdash; PyPI-তে প্রায় ৮,০০০ প্যাকেজ Pydantic ব্যবহার করে, যার মধ্যে আছে ব্যাপক জনপ্রিয় লাইব্রেরি যেমন
  *FastAPI*, *huggingface*, *Django Ninja*, *SQLModel*, & *LangChain*। [আরও জানুন…](why.md#ecosystem)
* **যুদ্ধে পরীক্ষিত** &mdash; Pydantic মাসে ৫৫ কোটিরও বেশিবার ডাউনলোড হয়, আর সব FAANG কোম্পানি ও NASDAQ-এর বৃহত্তম ২৫টির মধ্যে ২০টি কোম্পানি এটি ব্যবহার করে। Pydantic দিয়ে আপনি যা করতে চাইছেন, সম্ভবত অন্য কেউ ইতিমধ্যে তা করে ফেলেছে। [আরও জানুন…](why.md#using-pydantic)

[Pydantic ইনস্টল করা](install.md) খুবই সহজ: `pip install pydantic`

## Pydantic-এর উদাহরণ { #pydantic-examples }

Pydantic কীভাবে কাজ করে তা দেখতে, একটি সহজ উদাহরণ দিয়ে শুরু করি: `BaseModel` থেকে উত্তরাধিকার পাওয়া (inherit করা) একটি কাস্টম ক্লাস তৈরি করা।

```python title="Validation Successful"
from datetime import datetime

from pydantic import BaseModel, PositiveInt


class User(BaseModel):
    id: int  # (1)!
    name: str = 'John Doe'  # (2)!
    signup_ts: datetime | None  # (3)!
    tastes: dict[str, PositiveInt]  # (4)!


external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',  # (5)!
    'tastes': {
        'wine': 9,
        b'cheese': 7,  # (6)!
        'cabbage': '1',  # (7)!
    },
}

user = User(**external_data)  # (8)!

print(user.id)  # (9)!
#> 123
print(user.model_dump())  # (10)!
"""
{
    'id': 123,
    'name': 'John Doe',
    'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
    'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
}
"""
```

1. `id`-এর টাইপ `int`; শুধু টাইপ লেখা (কোনো ডিফল্ট মান নেই) মানে Pydantic-কে বলা হচ্ছে যে এই ফিল্ডটি বাধ্যতামূলক। স্ট্রিং,
   bytes বা float সম্ভব হলে integer-এ রূপান্তরিত হবে; নইলে একটি এক্সেপশন (এরর) হবে।
2. `name` একটি স্ট্রিং; যেহেতু এর একটি ডিফল্ট মান আছে, তাই এটি বাধ্যতামূলক নয়।
3. `signup_ts` একটি [`datetime`][datetime.datetime] ফিল্ড যা বাধ্যতামূলক, কিন্তু এর মান `None`-ও দেওয়া যায়;
   Pydantic একটি [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) integer (যেমন `1496498400`)
   অথবা তারিখ-সময় বোঝায় এমন একটি স্ট্রিং, দুটোই প্রসেস করতে পারে।
4. `tastes` একটি ডিকশনারি, যার key স্ট্রিং আর value ধনাত্মক integer। `PositiveInt` টাইপটি হলো
   `Annotated[int, annotated_types.Gt(0)]`-এর সংক্ষিপ্ত রূপ (অর্থাৎ ০-এর চেয়ে বড় integer)।
5. এখানে ইনপুটটি [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) ফরম্যাটের একটি তারিখ-সময় স্ট্রিং, কিন্তু Pydantic
   এটিকে একটি [`datetime`][datetime.datetime] অবজেক্টে রূপান্তর করবে।
6. এখানে key-টি `bytes`, কিন্তু Pydantic এটিকে স্ট্রিংয়ে রূপান্তরের দায়িত্ব নেবে।
7. একইভাবে, Pydantic স্ট্রিং `'1'`-কে integer `1`-এ রূপান্তর করবে।
8. আমরা বাইরের ডেটাকে keyword argument হিসেবে `User`-এ দিয়ে `User`-এর একটি ইনস্ট্যান্স তৈরি করি।
9. মডেলের ফিল্ডগুলো অ্যাট্রিবিউট হিসেবে ব্যবহার করা যায়।
10. [`model_dump()`][pydantic.BaseModel.model_dump] দিয়ে মডেলটিকে একটি ডিকশনারিতে রূপান্তর করা যায়।

/// info | কোডটি সহজ ভাষায়

* প্রথমে `class User(BaseModel)` দিয়ে আমরা বলে দিলাম একজন ইউজারের ডেটা দেখতে কেমন হবে: কোন ফিল্ড, কোন টাইপ, কোনটির ডিফল্ট আছে।
* তারপর `external_data` হলো বাইরে থেকে আসা "অগোছালো" ডেটা: তারিখ লেখা আছে স্ট্রিং হিসেবে, একটি key `bytes`, একটি সংখ্যা `'1'` স্ট্রিং হিসেবে।
* `User(**external_data)` লেখার মুহূর্তেই Pydantic সব যাচাই করে আর গুছিয়ে দেয়: স্ট্রিং তারিখ হয়ে যায় আসল `datetime`, `b'cheese'` হয়ে যায় `'cheese'`, `'1'` হয়ে যায় `1`।
* শেষে `user.model_dump()` দেখায় যে ভেতরে সব ডেটা এখন পরিষ্কার আর সঠিক টাইপের। `name` দেওয়া হয়নি, তাই ডিফল্ট `'John Doe'` বসেছে।

কোডের ভেতরের `# (1)!` এর মতো চিহ্নগুলোতে ক্লিক করলেও ছোট ব্যাখ্যা দেখতে পাবেন।

///

যাচাই ব্যর্থ হলে, Pydantic একটি এরর দেবে, যেখানে ঠিক কী কী ভুল তার বিস্তারিত থাকবে:

```python title="Validation Error"
# continuing the above example...

from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]


external_data = {'id': 'not an int', 'tastes': {}}  # (1)!

try:
    User(**external_data)  # (2)!
except ValidationError as e:
    print(e.errors())
    """
    [
        {
            'type': 'int_parsing',
            'loc': ('id',),
            'msg': 'Input should be a valid integer, unable to parse string as an integer',
            'input': 'not an int',
            'url': 'https://errors.pydantic.dev/2/v/int_parsing',
        },
        {
            'type': 'missing',
            'loc': ('signup_ts',),
            'msg': 'Field required',
            'input': {'id': 'not an int', 'tastes': {}},
            'url': 'https://errors.pydantic.dev/2/v/missing',
        },
    ]
    """
```

1. এখানে ইনপুট ডেটা ভুল &mdash; `id` একটি বৈধ integer নয়, আর `signup_ts` নেই।
2. `User` তৈরির চেষ্টা করলে একটি [`ValidationError`][pydantic_core.ValidationError] হবে, যাতে এররগুলোর একটি তালিকা থাকবে।

/// info | এরর বার্তাটি সহজ ভাষায়

`e.errors()` প্রতিটি ভুলের জন্য একটি ডিকশনারি দেয়:

* `type`: ভুলের ধরন, যেমন `int_parsing` (সংখ্যায় রূপান্তর করা যায়নি) বা `missing` (ঘরটি নেই)।
* `loc`: কোন ফিল্ডে ভুল, যেমন `('id',)`।
* `msg`: মানুষের পড়ার মতো বার্তা।
* `input`: আসলে কী পাঠানো হয়েছিল।
* `url`: এই ধরনের এরর নিয়ে বিস্তারিত ব্যাখ্যার লিংক।

FastAPI-তে ভুল রিকোয়েস্ট পাঠালে যে `422` এরর আর `detail` তালিকা দেখেছিলেন, সেটি আসলে এই `errors()`-ই।

///

## কারা Pydantic ব্যবহার করে? { #who-is-using-pydantic }

শত শত প্রতিষ্ঠান আর প্যাকেজ Pydantic ব্যবহার করে। বিশ্বের যেসব বিখ্যাত কোম্পানি আর প্রতিষ্ঠান Pydantic ব্যবহার করে, তাদের কয়েকটি:

<div style="display:flex;flex-wrap:wrap;align-items:center"><a href="why/#org-adobe" title="Adobe"><img src="logos/adobe_logo.png" alt="Adobe" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-amazon" title="Amazon and AWS"><img src="logos/amazon_logo.png" alt="Amazon and AWS" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-anthropic" title="Anthropic"><img src="logos/anthropic_logo.png" alt="Anthropic" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-apple" title="Apple"><img src="logos/apple_logo.png" alt="Apple" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-asml" title="ASML"><img src="logos/asml_logo.png" alt="ASML" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-astrazeneca" title="AstraZeneca"><img src="logos/astrazeneca_logo.png" alt="AstraZeneca" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-cisco" title="Cisco Systems"><img src="logos/cisco_logo.png" alt="Cisco Systems" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-capital_one" title="Capital One"><img src="logos/capital_one_logo.png" alt="Capital One" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-comcast" title="Comcast"><img src="logos/comcast_logo.png" alt="Comcast" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-datadog" title="Datadog"><img src="logos/datadog_logo.png" alt="Datadog" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-facebook" title="Facebook"><img src="logos/facebook_logo.png" alt="Facebook" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-github" title="GitHub"><img src="logos/github_logo.png" alt="GitHub" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-google" title="Google"><img src="logos/google_logo.png" alt="Google" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-hsbc" title="HSBC"><img src="logos/hsbc_logo.png" alt="HSBC" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-ibm" title="IBM"><img src="logos/ibm_logo.png" alt="IBM" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-intel" title="Intel"><img src="logos/intel_logo.png" alt="Intel" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-intuit" title="Intuit"><img src="logos/intuit_logo.png" alt="Intuit" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-ipcc" title="Intergovernmental Panel on Climate Change"><img src="logos/ipcc_logo.png" alt="Intergovernmental Panel on Climate Change" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-jpmorgan" title="JPMorgan"><img src="logos/jpmorgan_logo.png" alt="JPMorgan" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-jupyter" title="Jupyter"><img src="logos/jupyter_logo.png" alt="Jupyter" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-microsoft" title="Microsoft"><img src="logos/microsoft_logo.png" alt="Microsoft" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-molssi" title="Molecular Science Software Institute"><img src="logos/molssi_logo.png" alt="Molecular Science Software Institute" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-nasa" title="NASA"><img src="logos/nasa_logo.png" alt="NASA" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-netflix" title="Netflix"><img src="logos/netflix_logo.png" alt="Netflix" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-nsa" title="NSA"><img src="logos/nsa_logo.png" alt="NSA" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-nvidia" title="NVIDIA"><img src="logos/nvidia_logo.png" alt="NVIDIA" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-openai" title="OpenAI"><img src="logos/openai_logo.png" alt="OpenAI" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-oracle" title="Oracle"><img src="logos/oracle_logo.png" alt="Oracle" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-palantir" title="Palantir"><img src="logos/palantir_logo.png" alt="Palantir" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-qualcomm" title="Qualcomm"><img src="logos/qualcomm_logo.png" alt="Qualcomm" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-redhat" title="Red Hat"><img src="logos/redhat_logo.png" alt="Red Hat" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-revolut" title="Revolut"><img src="logos/revolut_logo.png" alt="Revolut" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-robusta" title="Robusta"><img src="logos/robusta_logo.png" alt="Robusta" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-salesforce" title="Salesforce"><img src="logos/salesforce_logo.png" alt="Salesforce" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-starbucks" title="Starbucks"><img src="logos/starbucks_logo.png" alt="Starbucks" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-ti" title="Texas Instruments"><img src="logos/ti_logo.png" alt="Texas Instruments" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-twilio" title="Twilio"><img src="logos/twilio_logo.png" alt="Twilio" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-twitter" title="Twitter"><img src="logos/twitter_logo.png" alt="Twitter" style="height:48px;width:auto;margin:.4rem .8rem"/></a><a href="why/#org-ukhomeoffice" title="UK Home Office"><img src="logos/ukhomeoffice_logo.png" alt="UK Home Office" style="height:48px;width:auto;margin:.4rem .8rem"/></a></div>

Pydantic ব্যবহার করে এমন ওপেন সোর্স প্রজেক্টের আরও বড় তালিকার জন্য দেখুন
[GitHub-এ dependents-এর তালিকা](https://github.com/pydantic/pydantic/network/dependents), অথবা Pydantic ব্যবহার করা কিছু দারুণ প্রজেক্ট খুঁজে পাবেন [awesome-pydantic](https://github.com/Kludex/awesome-pydantic)-এ।

/// check | সংক্ষেপে মনে রাখুন

* Pydantic = বাইরের ডেটা আপনার কোডে ঢোকার আগে যাচাই আর গোছানোর লাইব্রেরি।
* ডেটা কেমন হবে তা `class X(BaseModel)`-এ সাধারণ Python টাইপ দিয়ে লেখেন, বাকিটা Pydantic করে।
* ভুল ডেটা এলে `ValidationError` হয়, যাতে কোন ফিল্ডে কী ভুল তা স্পষ্ট লেখা থাকে।
* FastAPI-সহ হাজারো লাইব্রেরি এর ওপর দাঁড়িয়ে আছে। নতুন শব্দের মানে জানতে [সহজ শব্দকোষ](../learn/glossary.md) দেখুন।

///
