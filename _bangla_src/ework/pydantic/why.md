# কেন Pydantic Validation ব্যবহার করবেন? { #why-use-pydantic-validation }

/// note | এই পেজে যা জানবেন

* Pydantic-এর ৭টি বড় সুবিধা: টাইপ হিন্ট, গতি, সিরিয়ালাইজেশন, JSON Schema, strict মোড, বিভিন্ন ধরনের স্কিমা আর কাস্টমাইজেশন।
* প্রতিটি সুবিধার ছোট উদাহরণ, সহজ ব্যাখ্যাসহ।
* কোন কোন বিখ্যাত লাইব্রেরি আর প্রতিষ্ঠান Pydantic ব্যবহার করে।

///

আজ Pydantic মাসে <span id="download-count">অনেকবার</span> ডাউনলোড হয়, আর বিশ্বের সবচেয়ে বড় আর পরিচিত কিছু প্রতিষ্ঠান এটি ব্যবহার করে।

ছয় বছর আগে শুরু হওয়ার পর থেকে কেন এত মানুষ Pydantic গ্রহণ করেছে তা নিশ্চিত করে বলা কঠিন, তবে এখানে কয়েকটি অনুমান দেওয়া হলো।

## টাইপ হিন্ট দিয়ে চালিত স্কিমা যাচাই { #type-hints }

Pydantic যে স্কিমা (ডেটার কাঠামোর নিয়ম) অনুযায়ী যাচাই করে, তা সাধারণত Python-এর [টাইপ হিন্ট](https://docs.python.org/3/glossary.html#term-type-hint) দিয়ে সংজ্ঞায়িত হয়।

এর জন্য টাইপ হিন্ট দারুণ, কারণ আপনি যদি আধুনিক Python লেখেন, তাহলে এগুলো কীভাবে ব্যবহার করতে হয় তা আগে থেকেই জানেন।
টাইপ হিন্ট ব্যবহারের মানে আরও হলো, Pydantic স্ট্যাটিক টাইপিং টুলের
([mypy](https://www.mypy-lang.org/) আর [Pyright](https://github.com/microsoft/pyright/)-এর মতো)
আর IDE-এর ([PyCharm](https://www.jetbrains.com/pycharm/) আর [VSCode](https://code.visualstudio.com/)-এর মতো) সাথে ভালোভাবে মানিয়ে চলে।

(টাইপ হিন্ট মানে `name: str`, `age: int` এর মতো লেখা, যা বলে দেয় কোন ভেরিয়েবলে কোন ধরনের মান থাকবে। বিস্তারিত দেখুন [Python টাইপের পরিচিতি](../python-types.md) পেজে।)

/// details | উদাহরণ - শুধু টাইপ হিন্ট
    type: tip
    open: True

⟦CODE1⟧

1. `name` ফিল্ডে শুধু `str` লেখা &mdash; যেকোনো স্ট্রিং চলবে।
2. [`Literal`][typing.Literal] টাইপ দিয়ে বাধ্য করা হয়েছে যে `color` হবে হয় `'red'`, নয়তো `'green'`।
3. এমনকি যখন এমন শর্ত দিতে চাই যা Python টাইপে প্রকাশ করা যায় না, তখনও [`Annotated`][typing.Annotated]
   আর [`annotated-types`](https://github.com/annotated-types/annotated-types) দিয়ে টাইপিং সাপোর্ট বজায় রেখেই শর্ত চাপানো যায় (এখানে: ওজন ০-এর চেয়ে বেশি)।
4. আমি দাবি করছি না যে "bazam" সত্যিই ফলের কোনো বৈশিষ্ট্য; এটি শুধু দেখাতে যে যত জটিল টাইপই হোক, সহজে যাচাই করা যায়।

///

/// tip | আরও জানুন

দেখুন [সমর্থিত টাইপ নিয়ে ডকুমেন্টেশন](concepts/types.md)।

///

## গতি (Performance) { #performance }

Pydantic-এর মূল যাচাইয়ের যুক্তি একটি আলাদা প্যাকেজে ([`pydantic-core`](https://pypi.org/project/pydantic-core)) বাস্তবায়িত,
যেখানে বেশিরভাগ টাইপের যাচাই লেখা হয়েছে Rust-এ।

ফলে Pydantic Python-এর দ্রুততম ডেটা যাচাই লাইব্রেরিগুলোর একটি।

/// tip | উদাহরণ দিয়ে বুঝি

Rust হলো একটি দ্রুতগতির প্রোগ্রামিং ভাষা, যা সরাসরি মেশিন কোডে চলে। Pydantic-এর ভারী কাজটা (হাজার হাজার ডেটা পরীক্ষা) Rust-এ লেখা "ইঞ্জিন" করে, আর আপনি শুধু সহজ Python লেখেন। অনেকটা গাড়ির মতো: আপনি স্টিয়ারিং ঘোরান (Python), আর ভেতরের শক্তিশালী ইঞ্জিন (Rust) গাড়ি চালায়।

///

/// details | গতির উদাহরণ - Pydantic বনাম বিশেষভাবে লেখা কোড
    type: tip

সাধারণত, কোনো নির্দিষ্ট কাজের জন্য বিশেষভাবে লেখা কোড একটি সাধারণ-উদ্দেশ্যের validator-এর চেয়ে অনেক দ্রুত হওয়ার কথা, কিন্তু এই উদাহরণে
JSON পার্স করা আর URL যাচাইয়ের সময় Pydantic বিশেষভাবে লেখা কোডের চেয়ে ৩০০%-এর বেশি দ্রুত।

⟦CODE2⟧

///

/// info | উদাহরণটি সহজ ভাষায়

GitHub-এর ইমোজি তালিকা (নাম আর ছবির URL) ডাউনলোড করে দুইভাবে যাচাই করা হয়েছে: একবার হাতে লেখা Python লুপ দিয়ে (`emojis_pure_python`), আরেকবার `TypeAdapter(dict[str, HttpUrl]).validate_json(...)` দিয়ে। `timeit` দিয়ে সময় মেপে দেখা গেল Pydantic প্রায় ৩.৪৫ গুণ দ্রুত, কারণ JSON পার্স আর URL যাচাই দুটোই Rust-এ একসাথে হয়।

///

অন্যান্য কম্পাইল করা ভাষায় লেখা গতি-কেন্দ্রিক লাইব্রেরির মতো নয়, Pydantic-এ [functional validator](#customisation) দিয়ে যাচাই নিজের মতো করার চমৎকার সুবিধাও আছে।

/// tip | আরও জানুন

Samuel Colvin-এর [PyCon 2023-এর বক্তৃতা](https://youtu.be/pWZw7hYoRVU) ব্যাখ্যা করে [`pydantic-core`](https://pypi.org/project/pydantic-core)
কীভাবে কাজ করে আর এটি Pydantic-এর সাথে কীভাবে যুক্ত।

///

## সিরিয়ালাইজেশন { #serialization }

Pydantic মডেলকে তিনভাবে সিরিয়ালাইজ (অন্য রূপে রূপান্তর) করার সুবিধা দেয়:

1. সংশ্লিষ্ট Python অবজেক্ট দিয়ে তৈরি একটি Python `dict`-এ।
2. শুধু "JSON-যোগ্য" টাইপ দিয়ে তৈরি একটি Python `dict`-এ।
3. একটি JSON স্ট্রিংয়ে।

তিনটি মোডেই আউটপুট নিজের মতো করা যায়: নির্দিষ্ট ফিল্ড বাদ দিয়ে, যে ফিল্ড সেট করা হয়নি তা বাদ দিয়ে, ডিফল্ট মান বাদ দিয়ে, আর `None` মান বাদ দিয়ে।

/// details | উদাহরণ - তিনভাবে সিরিয়ালাইজেশন
    type: tip

⟦CODE3⟧

///

/// info | উদাহরণটি সহজ ভাষায়

* `model_dump(exclude_unset=True)`: শুধু যে ফিল্ডগুলো আসলে দেওয়া হয়েছিল সেগুলো, Python অবজেক্ট হিসেবে (তারিখ থাকে `datetime`, `where` থাকে `bytes`)। `why` দেওয়া হয়নি, তাই বাদ।
* `model_dump(exclude={'where'}, mode='json')`: `where` বাদ দিয়ে, আর সব মান JSON-যোগ্য রূপে (তারিখ হয়ে যায় স্ট্রিং)।
* `model_dump_json(exclude_defaults=True)`: সরাসরি JSON স্ট্রিং, যে ফিল্ডের মান ডিফল্টের সমান (`why`) তা বাদ দিয়ে।

///

/// tip | আরও জানুন

দেখুন [সিরিয়ালাইজেশন নিয়ে ডকুমেন্টেশন](concepts/serialization.md)।

///

## JSON Schema { #json-schema }

যেকোনো Pydantic স্কিমা থেকে একটি [JSON Schema](https://json-schema.org/) তৈরি করা যায় &mdash; ফলে নিজেই নিজের ডকুমেন্টেশন দেয় এমন API তৈরি করা যায়, আর JSON Schema ফরম্যাট সমর্থন করে এমন অনেক টুলের সাথে যুক্ত হওয়া যায়।

/// details | উদাহরণ - JSON Schema
    type: tip

⟦CODE4⟧

///

/// info | উদাহরণটি সহজ ভাষায়

`Meeting.model_json_schema()` মডেলটির একটি "মানচিত্র" দেয়: কোন ফিল্ড কোন টাইপের (`when` তারিখ-সময় স্ট্রিং, `why` স্ট্রিং যার ডিফল্ট আছে), কোনগুলো বাধ্যতামূলক (`required`), আর নেস্টেড মডেল `Address` আলাদা করে `$defs`-এ রাখা হয়েছে আর `$ref` দিয়ে উল্লেখ করা হয়েছে। FastAPI ঠিক এই JSON Schema দিয়েই `/docs` পেজ তৈরি করে।

///

Pydantic JSON Schema স্পেসিফিকেশনের সর্বশেষ সংস্করণ
([2020-12](https://json-schema.org/draft/2020-12/release-notes.html)) মেনে চলে, যা
[OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html)-এর সাথে সামঞ্জস্যপূর্ণ।

/// tip | আরও জানুন

দেখুন [JSON Schema নিয়ে ডকুমেন্টেশন](concepts/json_schema.md)।

///

## Strict মোড আর ডেটা রূপান্তর { #strict-lax }

ডিফল্টভাবে, Pydantic প্রচলিত ভুল টাইপের প্রতি সহনশীল আর ডেটাকে সঠিক টাইপে রূপান্তর করে &mdash;
যেমন একটি `int` ফিল্ডে সংখ্যাসূচক স্ট্রিং দিলে সেটি `int` হিসেবে পার্স হবে।

Pydantic-এ একটি [strict মোড](concepts/strict_mode.md)-ও আছে, যেখানে টাইপ রূপান্তর করা হয় না, আর
ইনপুট ডেটা প্রত্যাশিত স্কিমার সাথে হুবহু না মিললে একটি যাচাই এরর হয়।

কিন্তু JSON ডেটা যাচাইয়ের সময় strict মোড প্রায় অকেজো হতো, কারণ JSON-এ অনেক প্রচলিত Python টাইপের সমতুল্য টাইপ নেই, যেমন
[`datetime`][datetime.datetime], [`UUID`][uuid.UUID] বা [`bytes`][]।

এর সমাধানে, Pydantic এক ধাপেই JSON পার্স আর যাচাই করতে পারে। এতে যুক্তিসঙ্গত ডেটা রূপান্তর সম্ভব হয়
(যেমন স্ট্রিংকে [`datetime`][datetime.datetime] অবজেক্টে পার্স করা)। যেহেতু JSON পার্সিং
Rust-এ বাস্তবায়িত, তাই এটি খুবই দ্রুতও।

/// details | উদাহরণ - এমন strict মোড যা সত্যিই কাজের
    type: tip

⟦CODE5⟧

///

/// info | উদাহরণটি সহজ ভাষায়

* সাধারণ `model_validate` (lax): স্ট্রিং তারিখ আর স্ট্রিং `'home'` দুটোই রূপান্তর হয়ে গেল।
* `strict=True` দিলে: Python ডিকশনারিতে তারিখ স্ট্রিং হিসেবে এলে গ্রহণ করে না, দুটি এরর দেয়।
* কিন্তু `model_validate_json` দিয়ে JSON থেকে পড়লে: JSON-এ তো তারিখ লেখার একমাত্র উপায় স্ট্রিং, তাই সেখানে স্ট্রিং থেকে তারিখ গ্রহণযোগ্য। এভাবে strict মোড JSON-এর সাথেও বাস্তবসম্মতভাবে কাজ করে।

///

/// tip | আরও জানুন

দেখুন [strict মোড নিয়ে ডকুমেন্টেশন](concepts/strict_mode.md)।

///

## Dataclass, TypedDict, এবং আরও { #dataclasses-typeddict-more }

স্কিমা তৈরি করে যাচাই আর সিরিয়ালাইজেশনের জন্য Pydantic চারটি উপায় দেয়:

1. [`BaseModel`](concepts/models.md) &mdash; Pydantic-এর নিজস্ব প্যারেন্ট ক্লাস, যাতে ইনস্ট্যান্স মেথডের মাধ্যমে অনেক প্রচলিত সুবিধা পাওয়া যায়।
2. [Pydantic dataclass](concepts/dataclasses.md) &mdash; স্ট্যান্ডার্ড dataclass-এর ওপর একটি মোড়ক, যাতে বাড়তি যাচাই হয়।
3. [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] &mdash; যেকোনো টাইপকে যাচাই আর সিরিয়ালাইজেশনের উপযোগী করার একটি সাধারণ উপায়।
   এতে [`TypedDict`](api/standard_library_types.md#typeddict) আর [`NamedTuple`](api/standard_library_types.md#named-tuples)-এর মতো টাইপ
   যাচাই করা যায়, সাথে সাধারণ টাইপও (যেমন [`int`][] বা [`timedelta`][datetime.timedelta]) &mdash; সমর্থিত [সব টাইপ](concepts/types.md)
   [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর সাথে ব্যবহার করা যায়।
4. [`validate_call`](concepts/validation_decorator.md) &mdash; একটি ডেকোরেটর, যা একটি ফাংশন কল করার সময় যাচাই করে।

/// details | উদাহরণ - একটি [`TypedDict`][typing.TypedDict]-এর ওপর ভিত্তি করে স্কিমা
    type: tip

⟦CODE6⟧

1. একটি [`TypedDict`][typing.TypedDict]-এর জন্য [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] যাচাই করছে,
   এটি [`validate_json`][pydantic.type_adapter.TypeAdapter.validate_json] দিয়ে সরাসরি JSON ডেটাও যাচাই করতে পারে।
2. [`dump_python`][pydantic.type_adapter.TypeAdapter.dump_python] দিয়ে একটি [`TypedDict`][typing.TypedDict]-কে
   Python অবজেক্টে সিরিয়ালাইজ করা, এটি [`dump_json`][pydantic.type_adapter.TypeAdapter.dump_json] দিয়ে JSON-এও সিরিয়ালাইজ করতে পারে।
3. [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] একটি JSON Schema-ও তৈরি করতে পারে।

///

/// tip | উদাহরণ দিয়ে বুঝি

চারটি উপায়কে চার রকম পাত্রের মতো ভাবুন, ভেতরের "পরীক্ষক" কিন্তু একই। `BaseModel` হলো সব সুবিধাসহ পূর্ণ বাক্স, dataclass হলো পরিচিত Python বাক্সে পরীক্ষা যোগ করা, `TypeAdapter` হলো যেকোনো জিনিসে (এমনকি শুধু `int` বা একটি `TypedDict`) পরীক্ষক লাগানোর অ্যাডাপ্টার, আর `validate_call` হলো ফাংশনের দরজায় পরীক্ষক বসানো।

///

## কাস্টমাইজেশন { #customisation }

Functional validator আর serializer, সাথে কাস্টম টাইপের জন্য একটি শক্তিশালী প্রোটোকল থাকায়, Pydantic কীভাবে কাজ করবে তা প্রতিটি ফিল্ড বা প্রতিটি টাইপ ধরে নিজের মতো করা যায়।

/// details | কাস্টমাইজেশনের উদাহরণ - wrap validator
    type: tip

"wrap validator" Pydantic V2-তে নতুন, আর যাচাই নিজের মতো করার সবচেয়ে শক্তিশালী উপায়গুলোর একটি।

⟦CODE7⟧

///

/// info | উদাহরণটি সহজ ভাষায়

`mode='wrap'` validator Pydantic-এর নিজের যাচাইকে "মুড়ে" রাখে: আগে-পরে নিজের কাজ করা যায়।

* ইনপুট যদি `'now'` হয়, Pydantic-এর যাচাই না চালিয়েই বর্তমান সময় ফেরত দেয়।
* নইলে `handler(input_value)` দিয়ে Pydantic-এর স্বাভাবিক যাচাই চালায়।
* তারপর ফলাফলে টাইমজোন না থাকলে UTC বসিয়ে দেয়।

///

/// tip | আরও জানুন

দেখুন [validator](concepts/validators.md), [কাস্টম serializer](concepts/serialization.md#serializers)
আর [কাস্টম টাইপ](concepts/types.md#custom-types) নিয়ে ডকুমেন্টেশন।

///

## ইকোসিস্টেম { #ecosystem }

এই লেখার সময় GitHub-এ ৪,৬৬,৪০০টি রিপোজিটরি আর PyPI-তে ৮,১১৯টি প্যাকেজ Pydantic-এর ওপর নির্ভর করে।

Pydantic-এর ওপর নির্ভর করে এমন কয়েকটি উল্লেখযোগ্য লাইব্রেরি (পাশে GitHub স্টারের সংখ্যা):

⟦CODE8⟧

Pydantic ব্যবহার করা আরও লাইব্রেরি পাবেন [`Kludex/awesome-pydantic`](https://github.com/Kludex/awesome-pydantic)-এ।

Pydantic-এর পেছনের দল [Pydantic Logfire](integrations/logfire.md)-ও তৈরি করে, যা একটি observability
(চলমান অ্যাপ পর্যবেক্ষণের) প্ল্যাটফর্ম, প্রোডাকশনে যাচাইয়ের ট্রেসিং আর ডিবাগিংয়ের জন্য Pydantic-এর সাথে সরাসরি সংযোগসহ।

## যেসব প্রতিষ্ঠান Pydantic ব্যবহার করে { #using-pydantic }

Pydantic ব্যবহার করে এমন কয়েকটি উল্লেখযোগ্য কোম্পানি আর প্রতিষ্ঠান, সাথে কেন/কীভাবে আমরা জানি যে তারা Pydantic ব্যবহার করে।

নিচের প্রতিষ্ঠানগুলো যুক্ত করা হয়েছে কারণ তারা নিচের এক বা একাধিক শর্ত পূরণ করে:

* একটি পাবলিক রিপোজিটরিতে Pydantic-কে ডিপেন্ডেন্সি হিসেবে ব্যবহার করা।
* প্রতিষ্ঠানের অভ্যন্তরীণ ডোমেইন থেকে Pydantic ডকুমেন্টেশন সাইটে ট্রাফিক আসা &mdash; নির্দিষ্ট উৎসগুলো দেওয়া হয়নি, কারণ সেগুলো সাধারণত প্রকাশ্য তথ্য নয়।
* প্রতিষ্ঠানের ভেতরে Pydantic ব্যবহার নিয়ে Pydantic দল আর সেই প্রতিষ্ঠানে কর্মরত ইঞ্জিনিয়ারদের মধ্যে সরাসরি যোগাযোগ।

যেখানে উপযুক্ত আর ইতিমধ্যে প্রকাশ্য, সেখানে কিছু বাড়তি বিবরণ দেওয়া হয়েছে।

### Adobe { #org-adobe }

[`adobe/dy-sql`](https://github.com/adobe/dy-sql) Pydantic ব্যবহার করে।

### Amazon and AWS { #org-amazon }

* [powertools-lambda-python](https://github.com/aws-powertools/powertools-lambda-python)
* [awslabs/gluonts](https://github.com/awslabs/gluonts)
* ২০২২ সালে Pydantic-এ কাজ করার জন্য AWS [Samuel Colvin-কে $5,000 স্পনসর করেছিল](https://twitter.com/samuel_colvin/status/1549383169006239745)

### Anthropic { #org-anthropic }

[`anthropics/anthropic-sdk-python`](https://github.com/anthropics/anthropic-sdk-python) Pydantic ব্যবহার করে।

### Apple { #org-apple }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### ASML { #org-asml }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### AstraZeneca { #org-astrazeneca }

`AstraZeneca` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3AAstraZeneca+pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

### Cisco Systems { #org-cisco }

* তাদের [RADKit-এ ব্যবহৃত ওপেন সোর্স](https://www.cisco.com/c/dam/en_us/about/doing_business/open_source/docs/RADKit-149-1687424532.pdf)-এর রিপোর্টে Pydantic তালিকাভুক্ত।
* [`cisco/webex-assistant-sdk`](https://github.com/cisco/webex-assistant-sdk)

### Capital One { #org-capital_one }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Comcast { #org-comcast }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Datadog { #org-datadog }

* [`DataDog/integrations-core`](https://github.com/DataDog/integrations-core) আর অন্যান্য রিপোজিটরিতে Pydantic-এর ব্যাপক ব্যবহার
* Datadog-এর ইঞ্জিনিয়ারদের সাথে তারা Pydantic কীভাবে ব্যবহার করেন তা নিয়ে যোগাযোগ।

### Facebook { #org-facebook }

`facebookresearch` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3Afacebookresearch+pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

### GitHub { #org-github }

২০২২ সালে GitHub Pydantic-কে $750 স্পনসর করেছিল।

### Google { #org-google }

[`google/turbinia`](https://github.com/google/turbinia) আর অন্যান্য রিপোজিটরিতে Pydantic-এর ব্যাপক ব্যবহার।

### HSBC { #org-hsbc }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### IBM { #org-ibm }

`IBM` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3AIBM+pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

### Intel { #org-intel }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Intuit { #org-intuit }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Intergovernmental Panel on Climate Change { #org-ipcc }

IPCC (জাতিসংঘের জলবায়ু পরিবর্তন বিষয়ক আন্তঃসরকার প্যানেল) কীভাবে Pydantic ব্যবহার করে তা নিয়ে [টুইট](https://twitter.com/daniel_huppmann/status/1563461797973110785)।

### JPMorgan { #org-jpmorgan }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Jupyter { #org-jupyter }

* Jupyter notebook-এর ডেভেলপাররা [সাব-প্রজেক্টে](https://github.com/pydantic/pydantic/issues/773) Pydantic ব্যবহার করছেন
* FastAPI-ভিত্তিক Jupyter সার্ভার [Jupyverse](https://github.com/jupyter-server/jupyverse)-এর মাধ্যমে
* [FPS](https://github.com/jupyter-server/fps)-এর কনফিগারেশন ব্যবস্থাপনায়।

### Microsoft { #org-microsoft }

* [DeepSpeed](https://github.com/microsoft/DeepSpeed) ডিপ লার্নিং অপ্টিমাইজেশন লাইব্রেরি Pydantic ব্যাপকভাবে ব্যবহার করে
* `microsoft` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3Amicrosoft%20pydantic&type=code) Pydantic-এর ওপর নির্ভর করে
* `Azure` GitHub org-এও Pydantic [ব্যবহৃত হয়](https://github.com/search?q=org%3AAzure%20pydantic&type=code)
* GitHub-এর [মন্তব্য](https://github.com/tiangolo/fastapi/pull/26) দেখায় যে Microsoft-এর ইঞ্জিনিয়াররা Windows আর Office-এর অংশ হিসেবে Pydantic ব্যবহার করছেন

### Molecular Science Software Institute { #org-molssi }

`MolSSI` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3AMolSSI%20pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

### NASA { #org-nasa }

`NASA` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3Anasa%20pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

James Webb মহাকাশ টেলিস্কোপের ছবি প্রসেস করতে NASA তাদের JWST প্রজেক্টে FastAPI-এর মাধ্যমে Pydantic ব্যবহার করছে,
দেখুন [এই টুইট](https://twitter.com/benjamin_falk/status/1546947039363305472)।

### Netflix { #org-netflix }

`Netflix` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3Anetflix%20pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

### NSA { #org-nsa }

[`nsacyber/WALKOFF`](https://github.com/nsacyber/WALKOFF) রিপোজিটরি Pydantic-এর ওপর নির্ভর করে।

### NVIDIA { #org-nvidia }

`NVIDIA` GitHub org-এর [একাধিক রিপোজিটরি](https://github.com/search?q=org%3ANVIDIA%20pydantic&type=code) Pydantic-এর ওপর নির্ভর করে।

[তাদের ডকুমেন্টেশন](https://web.archive.org/web/20220628161919/https://docs.omniverse.nvidia.com/prod_services/prod_services/core/index.html) অনুযায়ী
তাদের "Omniverse Services" Pydantic-এর ওপর নির্ভর করে।

### OpenAI { #org-openai }

GitHub-এর [এই](https://github.com/pydantic/pydantic/discussions/6372) আলোচনা অনুযায়ী, OpenAI তাদের ChatCompletions API-তে Pydantic ব্যবহার করে।

শোনা যায়, OpenAI তাদের অভ্যন্তরীণ সার্ভিসগুলোতে Pydantic ব্যাপকভাবে ব্যবহার করে।

### Oracle { #org-oracle }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Palantir { #org-palantir }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Qualcomm { #org-qualcomm }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Red Hat { #org-redhat }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Revolut { #org-revolut }

শোনা যায়, Revolut-এর সব অভ্যন্তরীণ সার্ভিস FastAPI দিয়ে তৈরি, আর তাই Pydantic দিয়েও।

### Robusta { #org-robusta }

[`robusta-dev/robusta`](https://github.com/robusta-dev/robusta) রিপোজিটরি Pydantic-এর ওপর নির্ভর করে।

### Salesforce { #org-salesforce }

২০২২ সালে Pydantic-এ কাজ করার জন্য Salesforce [Samuel Colvin-কে $10,000 স্পনসর করেছিল](https://twitter.com/samuel_colvin/status/1501288247670063104)।

### Starbucks { #org-starbucks }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Texas Instruments { #org-ti }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Twilio { #org-twilio }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

### Twitter { #org-twitter }

Twitter-এর [`the-algorithm`](https://github.com/twitter/the-algorithm) রিপোজিটরি, যেখানে তারা তাদের রেকমেন্ডেশন ইঞ্জিন
[ওপেন সোর্স করেছে](https://blog.twitter.com/engineering/en_us/topics/open-source/2023/twitter-recommendation-algorithm),
Pydantic ব্যবহার করে।

### UK Home Office { #org-ukhomeoffice }

_(ওপরে বর্ণিত শর্তের ভিত্তিতে)_

/// check | সংক্ষেপে মনে রাখুন

* টাইপ হিন্ট দিয়ে স্কিমা লেখা, Rust-এর গতি, তিনভাবে সিরিয়ালাইজেশন, JSON Schema, বাস্তবসম্মত strict মোড, চার রকম স্কিমা আর শক্তিশালী কাস্টমাইজেশন: এগুলোই Pydantic-এর জনপ্রিয়তার কারণ।
* FastAPI, Hugging Face, LangChain, Airflow-সহ হাজারো লাইব্রেরি আর বিশ্বের বড় বড় প্রতিষ্ঠান Pydantic-এর ওপর ভরসা করে।

///
