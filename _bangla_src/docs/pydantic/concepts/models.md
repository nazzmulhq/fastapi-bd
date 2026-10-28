# মডেল { #models }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.main.BaseModel`][pydantic.main.BaseModel]<br>

///

/// note | এই পেজে যা শিখবেন

* মডেল কী, আর `BaseModel` দিয়ে কীভাবে মডেল বানাতে হয়।
* মডেলের গুরুত্বপূর্ণ মেথড: `model_validate()`, `model_dump()`, `model_copy()` ইত্যাদি।
* Pydantic কীভাবে ডেটা রূপান্তর করে, আর বাড়তি (extra) ডেটা কীভাবে সামলায়।
* নেস্টেড মডেল, generic মডেল, ডায়নামিক মডেল, `RootModel`, immutable মডেল এবং আরও অনেক কিছু।

এটি Pydantic-এর সবচেয়ে গুরুত্বপূর্ণ পেজ। ধীরে ধীরে পড়ুন, প্রতিটি অংশের উদাহরণ নিজে চালিয়ে দেখুন।

///

Pydantic-এ স্কিমা (ডেটার কাঠামো) সংজ্ঞায়িত করার প্রধান উপায়গুলোর একটি হলো মডেল। মডেল হলো সাধারণ ক্লাস, যেগুলো
[`BaseModel`][pydantic.main.BaseModel] থেকে উত্তরাধিকার পায় আর অ্যানোটেট করা অ্যাট্রিবিউট হিসেবে ফিল্ড সংজ্ঞায়িত করে।

মডেলকে C-এর মতো ভাষার struct-এর মতো ভাবতে পারেন, অথবা একটি API-র একটি এন্ডপয়েন্টের
প্রয়োজনীয় ডেটার তালিকা হিসেবে।

মডেলের সাথে Python-এর [dataclasses][dataclasses]-এর অনেক মিল আছে, কিন্তু এগুলো কিছু সূক্ষ্ম অথচ গুরুত্বপূর্ণ
পার্থক্যসহ ডিজাইন করা, যা যাচাই, সিরিয়ালাইজেশন আর JSON schema তৈরির সাথে সম্পর্কিত কিছু কাজ সহজ করে।
এ নিয়ে আরও আলোচনা পাবেন ডকসের [Dataclasses](dataclasses.md) অংশে।

অবিশ্বস্ত ডেটা একটি মডেলে দেওয়া যায়, আর পার্স ও যাচাইয়ের পরে Pydantic নিশ্চয়তা দেয় যে
ফলস্বরূপ মডেল ইনস্ট্যান্সের ফিল্ডগুলো মডেলে সংজ্ঞায়িত ফিল্ড টাইপের সাথে মিলবে।

/// tip | উদাহরণ দিয়ে বুঝি

মডেল হলো একটি ছাপানো ফর্মের মতো: "নাম: ____ (লেখা)", "বয়স: ____ (সংখ্যা)", "ইমেইল: ____ (ঐচ্ছিক)"। ফর্মটি নিজে কোনো তথ্য রাখে না, শুধু বলে কী কী তথ্য কোন রূপে লাগবে। যখন কেউ তথ্য দিয়ে ফর্ম পূরণ করে (মডেলের ইনস্ট্যান্স তৈরি), তখন Pydantic পরীক্ষা করে সব ঘর ঠিকমতো পূরণ হয়েছে কিনা।

///

/// note | যাচাই (Validation) — একটি *ইচ্ছাকৃত* ভুল নাম

<h3>সংক্ষেপে</h3>

নির্দিষ্ট টাইপ আর শর্ত মেনে চলে এমন একটি মডেল (বা অন্য টাইপ) তৈরির প্রক্রিয়াকে বোঝাতে আমরা "validation" (যাচাই) শব্দটি ব্যবহার করি।
Pydantic যে কাজের জন্য সুপরিচিত, সেটি সাধারণ কথায় "যাচাই" হিসেবেই সবচেয়ে বেশি পরিচিত,
যদিও অন্য প্রসঙ্গে "যাচাই" শব্দটির অর্থ আরও সীমিত হতে পারে।

---

<h3>দীর্ঘ ব্যাখ্যা</h3>

"যাচাই" শব্দটি নিয়ে সম্ভাব্য বিভ্রান্তির কারণ হলো, কঠোরভাবে বললে, Pydantic-এর
প্রধান লক্ষ্য "যাচাই"-এর অভিধানের সংজ্ঞার সাথে হুবহু মেলে না:

> <h3>validation</h3>
> _noun_
> the action of checking or proving the validity or accuracy of something.

(অর্থাৎ: কোনো কিছুর বৈধতা বা নির্ভুলতা পরীক্ষা বা প্রমাণ করার কাজ।)

Pydantic-এ "যাচাই" শব্দটি বোঝায় নির্দিষ্ট টাইপ আর শর্ত মেনে চলে এমন একটি মডেল (বা অন্য টাইপ) তৈরির প্রক্রিয়া।
Pydantic আউটপুটের টাইপ আর শর্তের নিশ্চয়তা দেয়, ইনপুট ডেটার নয়।
এই পার্থক্য স্পষ্ট হয় যখন দেখি যে ডেটাকে সফলভাবে একটি মডেল ইনস্ট্যান্সে পার্স করা না গেলে
Pydantic-এর `ValidationError` raise হয়।

এই পার্থক্য প্রথমে সূক্ষ্ম মনে হলেও, এর বাস্তব গুরুত্ব আছে।
কিছু ক্ষেত্রে, "যাচাই" শুধু মডেল তৈরির চেয়ে বেশি কিছু, আর এতে ডেটা কপি করা আর রূপান্তরও থাকতে পারে।
এতে মূল ইনপুট ডেটা না বদলে নতুন টাইপে রূপান্তর করতে constructor-এ দেওয়া আর্গুমেন্ট কপি করা জড়িত থাকতে পারে।
আপনার ব্যবহারের ওপর এর প্রভাব আরও গভীরভাবে বুঝতে,
নিচের [ডেটা রূপান্তর](#data-conversion) আর [অ্যাট্রিবিউটের কপি](#attribute-copies) অংশ দেখুন।

মূলত, Pydantic-এর প্রধান লক্ষ্য হলো নিশ্চিত করা যে প্রসেসিংয়ের পরের ফলস্বরূপ কাঠামো ("যাচাই" নামে পরিচিত)
প্রয়োগ করা টাইপ হিন্টের সাথে হুবহু মেলে। এই প্রক্রিয়ার জন্য "যাচাই" শব্দটি ব্যাপকভাবে প্রচলিত হওয়ায়,
আমরা আমাদের ডকুমেন্টেশনে ধারাবাহিকভাবে এটিই ব্যবহার করব।

যদিও আগে "parse" আর "validation" শব্দ দুটি একে অপরের বদলে ব্যবহার হতো, এখন থেকে আমরা শুধু "validate" ব্যবহারের লক্ষ্য রাখি,
আর "parse" শব্দটি শুধু [JSON পার্সিং](../concepts/json.md) সম্পর্কিত আলোচনার জন্য রাখা হয়েছে।

///

## মডেলের মৌলিক ব্যবহার { #basic-model-usage }

/// note | নোট

মডেল সংজ্ঞায়িত করতে Pydantic Python-এর বিদ্যমান টাইপিং গঠনের ওপর অনেকটা নির্ভর করে। এগুলোর সাথে পরিচিত না থাকলে, নিচের উৎসগুলো
কাজে লাগতে পারে:

* [Type System Guides](https://typing.readthedocs.io/en/latest/guides/index.html)
* [mypy ডকুমেন্টেশন](https://mypy.readthedocs.io/en/latest/)

এই সাইটের [Python টাইপের পরিচিতি](../../python-types.md) পেজটিও সহজ বাংলায় শুরু করার জন্য ভালো।

///

```python
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str = 'Jane Doe'

    model_config = ConfigDict(str_max_length=10)  # (1)!
```

1. Pydantic মডেল বিভিন্ন [configuration মান](./config.md) সমর্থন করে
   (উপলব্ধ configuration মানগুলো দেখুন [এখানে][pydantic.ConfigDict])। এখানে `str_max_length=10` মানে মডেলের কোনো স্ট্রিং ১০ অক্ষরের বেশি হতে পারবে না।

এই উদাহরণে, `User` হলো দুটি ফিল্ডসহ একটি মডেল:

* `id`, যা একটি integer ([`int`][] টাইপ দিয়ে সংজ্ঞায়িত) আর বাধ্যতামূলক
* `name`, যা একটি স্ট্রিং ([`str`][] টাইপ দিয়ে সংজ্ঞায়িত) আর বাধ্যতামূলক নয় (এর একটি ডিফল্ট মান আছে)।

সমর্থিত টাইপ সম্পর্কে বিস্তারিত আছে [টাইপ](./types.md) ডকুমেন্টেশনে।

[`Field()`][pydantic.Field] ফাংশন দিয়ে ফিল্ডগুলো বিভিন্নভাবে নিজের মতো করা যায়।
আরও তথ্যের জন্য দেখুন [ফিল্ড নিয়ে ডকুমেন্টেশন](./fields.md)।

এরপর মডেলটির ইনস্ট্যান্স তৈরি করা যায়:

```python
user = User(id='123')
```

`user` হলো `User`-এর একটি ইনস্ট্যান্স। অবজেক্টটি তৈরির সময়েই সব পার্স আর যাচাই হয়।
যদি কোনো [`ValidationError`][pydantic_core.ValidationError] এক্সেপশন না হয়,
তাহলে নিশ্চিত থাকতে পারেন যে ফলস্বরূপ মডেল ইনস্ট্যান্সটি বৈধ।

মডেলের ফিল্ডগুলো `user` অবজেক্টের সাধারণ অ্যাট্রিবিউটের মতো ব্যবহার করা যায়:

```python
assert user.name == 'Jane Doe'  # (1)!
assert user.id == 123  # (2)!
assert isinstance(user.id, int)
```

1. `user` তৈরির সময় `name` সেট করা হয়নি, তাই ডিফল্ট মান ব্যবহার হয়েছে।
   তৈরির সময় স্পষ্টভাবে কোন ফিল্ডগুলো সেট করা হয়েছিল তা দেখতে
   [`model_fields_set`][pydantic.BaseModel.model_fields_set] অ্যাট্রিবিউট পরীক্ষা করা যায়।
2. লক্ষ্য করুন, স্ট্রিং `'123'` একটি integer-এ রূপান্তরিত হয়েছে আর এর মান `123`।
   Pydantic-এর রূপান্তরের যুক্তি সম্পর্কে আরও বিস্তারিত পাবেন [ডেটা রূপান্তর](#data-conversion) অংশে।

মডেল ইনস্ট্যান্সটি [`model_dump()`][pydantic.BaseModel.model_dump] মেথড দিয়ে সিরিয়ালাইজ করা যায়:

```python
assert user.model_dump() == {'id': 123, 'name': 'Jane Doe'}
```

ইনস্ট্যান্সের ওপর [dict][] কল করলেও একটি ডিকশনারি পাওয়া যায়, কিন্তু নেস্টেড ফিল্ডগুলো
ধাপে ধাপে ডিকশনারিতে রূপান্তরিত হবে না। [`model_dump()`][pydantic.BaseModel.model_dump] সিরিয়ালাইজেশনের ফলাফল নিজের মতো করতে
অনেক আর্গুমেন্টও দেয়।

ডিফল্টভাবে, মডেল পরিবর্তনযোগ্য (mutable), আর অ্যাট্রিবিউটে মান বসিয়ে ফিল্ডের মান বদলানো যায়:

```python
user.id = 321
assert user.id == 321
```

/// warning | সতর্কতা

মডেল সংজ্ঞায়িত করার সময়, ফিল্ডের নাম আর তার টাইপ অ্যানোটেশনের মধ্যে নামের সংঘর্ষের দিকে খেয়াল রাখুন।

যেমন, নিচেরটি প্রত্যাশামতো আচরণ করবে না আর একটি যাচাই এরর দেবে:

```python
from typing import Optional

from pydantic import BaseModel


class Boo(BaseModel):
    int: Optional[int] = None


m = Boo(int=123)  # Will fail to validate.
```

Python যেভাবে [অ্যানোটেট করা অ্যাসাইনমেন্ট স্টেটমেন্ট][annassign] মূল্যায়ন করে তার কারণে, স্টেটমেন্টটি `int: None = None`-এর সমতুল্য, ফলে
একটি যাচাই এরর হয়।

(সহজ কথায়: ফিল্ডের নাম `int` রাখায়, ক্লাসের ভেতরে `int` নামটি নিজেই ফিল্ডের মান `None` হয়ে যায়, ফলে টাইপ হিসেবে আর আসল `int` থাকে না। ফিল্ডের নাম কখনো `int`, `str`, `list` এর মতো টাইপের নামে রাখবেন না।)

///

### মডেলের মেথড আর প্রপার্টি { #model-methods-and-properties }

ওপরের উদাহরণটি মডেল কী কী করতে পারে তার শুধু হিমশৈলের চূড়া দেখায়।
মডেল ক্লাসের নিচের মেথড আর অ্যাট্রিবিউটগুলো আছে:

* [`model_validate()`][pydantic.main.BaseModel.model_validate]: দেওয়া অবজেক্টটিকে Pydantic মডেল অনুযায়ী যাচাই করে। দেখুন [ডেটা যাচাই](#validating-data)।
* [`model_validate_json()`][pydantic.main.BaseModel.model_validate_json]: দেওয়া JSON ডেটা Pydantic মডেল অনুযায়ী যাচাই করে। দেখুন
    [ডেটা যাচাই](#validating-data)।
* [`model_construct()`][pydantic.main.BaseModel.model_construct]: যাচাই না চালিয়েই মডেল তৈরি করে। দেখুন
    [যাচাই ছাড়া মডেল তৈরি](#creating-models-without-validation)।
* [`model_dump()`][pydantic.main.BaseModel.model_dump]: মডেলের ফিল্ড আর মানের একটি ডিকশনারি ফেরত দেয়। দেখুন
    [সিরিয়ালাইজেশন](serialization.md#python-mode)।
* [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]: [`model_dump()`][pydantic.main.BaseModel.model_dump]-এর একটি JSON স্ট্রিং রূপ ফেরত দেয়। দেখুন [সিরিয়ালাইজেশন](serialization.md#json-mode)।
* [`model_copy()`][pydantic.main.BaseModel.model_copy]: মডেলের একটি কপি (ডিফল্টভাবে shallow copy) ফেরত দেয়। দেখুন
    [মডেল কপি](#model-copy)।
* [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema]: মডেলের JSON Schema বোঝায় এমন একটি JSON-যোগ্য ডিকশনারি ফেরত দেয়। দেখুন [JSON Schema](json_schema.md)।
* [`model_fields`][pydantic.main.BaseModel.model_fields]: ফিল্ডের নাম আর তাদের সংজ্ঞার ([`FieldInfo`][pydantic.fields.FieldInfo] ইনস্ট্যান্স) মধ্যে একটি ম্যাপিং।
* [`model_computed_fields`][pydantic.main.BaseModel.model_computed_fields]: computed ফিল্ডের নাম আর তাদের সংজ্ঞার ([`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] ইনস্ট্যান্স) মধ্যে একটি ম্যাপিং।
* [`model_parametrized_name()`][pydantic.main.BaseModel.model_parametrized_name]: generic ক্লাসের প্যারামিটারাইজেশনের জন্য ক্লাসের নাম হিসাব করে।
* [`model_post_init()`][pydantic.main.BaseModel.model_post_init]: মডেল তৈরি হওয়ার আর সব ফিল্ড validator প্রয়োগের পরে বাড়তি কাজ করে।
* [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild]: মডেলের schema আবার তৈরি করে, যা পুনরাবৃত্ত (recursive) generic মডেল তৈরিও সমর্থন করে।
    দেখুন [মডেল schema আবার তৈরি](#rebuilding-model-schema)।

মডেল ইনস্ট্যান্সের নিচের অ্যাট্রিবিউটগুলো আছে:

* [`model_extra`][pydantic.main.BaseModel.model_extra]: যাচাইয়ের সময় সেট হওয়া বাড়তি (extra) ফিল্ডগুলো।
* [`model_fields_set`][pydantic.main.BaseModel.model_fields_set]: মডেল তৈরির সময় স্পষ্টভাবে দেওয়া ফিল্ডগুলোর সেট।

/// note | নোট

সব মেথড আর অ্যাট্রিবিউটের পূর্ণ তালিকাসহ ক্লাসের সংজ্ঞার জন্য [`BaseModel`][pydantic.main.BaseModel]-এর API ডকুমেন্টেশন দেখুন।

///

/// tip | পরামর্শ

Pydantic V1 থেকে পরিবর্তনের বিস্তারিত জানতে [মাইগ্রেশন গাইডের](../migration.md)
[`pydantic.BaseModel`-এর পরিবর্তন](../migration.md#changes-to-pydanticbasemodel) দেখুন।

///

## ডেটা রূপান্তর { #data-conversion }

মডেলের ফিল্ড টাইপের সাথে মেলাতে Pydantic ইনপুট ডেটার টাইপ বদলাতে (cast করতে) পারে,
আর কিছু ক্ষেত্রে এতে তথ্য হারিয়ে যেতে পারে।
যেমন:

```python
from pydantic import BaseModel


class Model(BaseModel):
    a: int
    b: float
    c: str


print(Model(a=3.000, b='2.72', c=b'binary data').model_dump())
#> {'a': 3, 'b': 2.72, 'c': 'binary data'}
```

/// info | কোডটি সহজ ভাষায়

* `a=3.000` (float) → `3` (int), কারণ দশমিক অংশ শূন্য।
* `b='2.72'` (স্ট্রিং) → `2.72` (float)।
* `c=b'binary data'` (bytes) → `'binary data'` (স্ট্রিং)।

Pydantic ইনপুটকে "বুঝে" সঠিক টাইপে বদলে দেয়, একে বলে lax (নমনীয়) মোড।

///

এটি Pydantic-এর একটি ইচ্ছাকৃত সিদ্ধান্ত, আর প্রায়ই এটিই সবচেয়ে উপকারী পদ্ধতি। এ বিষয়ে দীর্ঘ আলোচনার জন্য
[এই issue](https://github.com/pydantic/pydantic/issues/578) দেখুন।

তবুও, Pydantic একটি [strict মোড](strict_mode.md) দেয়, যেখানে কোনো ডেটা রূপান্তর হয় না।
মানগুলো অবশ্যই ঘোষিত ফিল্ড টাইপের একই টাইপের হতে হবে।

collection-এর ক্ষেত্রেও একই কথা। বেশিরভাগ ক্ষেত্রে, abstract container ক্লাস ব্যবহার না করে
একটি নির্দিষ্ট (concrete) টাইপ ব্যবহার করা উচিত, যেমন [`list`][]:

```python
from pydantic import BaseModel


class Model(BaseModel):
    items: list[int]  # (1)!


print(Model(items=(1, 2, 3)))
#> items=[1, 2, 3]
```

1. এই ক্ষেত্রে, list আর tuple দুটোই গ্রহণ করতে abstract [`Sequence`][collections.abc.Sequence] টাইপ ব্যবহারের
   প্রলোভন হতে পারে। কিন্তু Pydantic tuple ইনপুটকে list-এ রূপান্তরের দায়িত্ব নেয়, তাই
   বেশিরভাগ ক্ষেত্রে এটি দরকার নেই।

তা ছাড়া, এই abstract টাইপগুলো ব্যবহারে [যাচাইয়ের পারফরম্যান্স খারাপ](./performance.md#sequence-vs-list-or-tuple-with-mapping-vs-dict) হতে পারে, আর সাধারণভাবে নির্দিষ্ট container টাইপ ব্যবহার করলে
অপ্রয়োজনীয় যাচাই এড়ানো যায়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#extra-fields}{% endraw %}

## বাড়তি ডেটা (Extra data) { #extra-data }

ডিফল্টভাবে, Pydantic মডেলে **বাড়তি ডেটা দিলে এরর হয় না**, আর এই মানগুলো শুধু উপেক্ষা করা হয়:

```python
from pydantic import BaseModel


class Model(BaseModel):
    x: int


m = Model(x=1, y='a')
assert m.model_dump() == {'x': 1}
```

এই আচরণ নিয়ন্ত্রণ করতে [`extra`][pydantic.ConfigDict.extra] configuration মান ব্যবহার করা যায়:

```python
from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='allow')


m = Model(x=1, y='a')  # (1)!
assert m.model_dump() == {'x': 1, 'y': 'a'}
assert m.__pydantic_extra__ == {'y': 'a'}
```

1. যদি [`extra`][pydantic.ConfigDict.extra]-কে `'forbid'` সেট করা হতো, তাহলে এটি ব্যর্থ হতো।

configuration-টি তিনটি মান নিতে পারে:

* `'ignore'`: বাড়তি ডেটা দিলে উপেক্ষা করা হয় (ডিফল্ট)।
* `'forbid'`: বাড়তি ডেটা দেওয়া অনুমোদিত নয় (এরর হয়)।
* `'allow'`: বাড়তি ডেটা দেওয়া অনুমোদিত আর `__pydantic_extra__` ডিকশনারি অ্যাট্রিবিউটে রাখা হয়।
  বাড়তি ফিল্ডগুলোর যাচাইয়ের জন্য `__pydantic_extra__`-কে স্পষ্টভাবে অ্যানোটেট করা যায়।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি ফর্মে শুধু নাম আর বয়স চাওয়া হয়েছে, কিন্তু কেউ বাড়তি একটি কাগজে ফোন নম্বরও দিয়ে দিল।

* `'ignore'`: বাড়তি কাগজটি ফেলে দেওয়া হয়।
* `'forbid'`: ফর্ম ফেরত দেওয়া হয়, "শুধু যা চাওয়া হয়েছে তা দিন"।
* `'allow'`: বাড়তি কাগজটিও ফাইলে রেখে দেওয়া হয়।

ব্যবহারকারীর টাইপো (যেমন `emial`) ধরতে API-তে `'forbid'` খুব কাজের।

///

যাচাইয়ের মেথডগুলোতে (যেমন [`model_validate()`][pydantic.main.BaseModel.model_validate]) একটি ঐচ্ছিক `extra` আর্গুমেন্ট আছে,
যা সেই যাচাই কলের জন্য মডেলের `extra` configuration মান ওভাররাইড করে।

আরও বিস্তারিত জানতে [`extra`][pydantic.ConfigDict.extra]-এর API ডকুমেন্টেশন দেখুন।

Pydantic dataclass-ও বাড়তি ডেটা সমর্থন করে (দেখুন [dataclass configuration](./dataclasses.md#dataclass-config) অংশ)।

## নেস্টেড মডেল { #nested-models }

অ্যানোটেশনে মডেলকেই টাইপ হিসেবে ব্যবহার করে আরও জটিল স্তরবিন্যস্ত ডেটা কাঠামো সংজ্ঞায়িত করা যায়।

```python
from pydantic import BaseModel


class Foo(BaseModel):
    count: int
    size: float | None = None


class Bar(BaseModel):
    apple: str = 'x'
    banana: str = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: list[Bar]


m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}])
print(m)
"""
foo=Foo(count=4, size=None) bars=[Bar(apple='x1', banana='y'), Bar(apple='x2', banana='y')]
"""
print(m.model_dump())
"""
{
    'foo': {'count': 4, 'size': None},
    'bars': [{'apple': 'x1', 'banana': 'y'}, {'apple': 'x2', 'banana': 'y'}],
}
"""
```

/// info | কোডটি সহজ ভাষায়

`Spam` মডেলের ভেতরে আছে একটি `Foo` আর `Bar`-এর একটি তালিকা। ইনপুটে আমরা সাধারণ ডিকশনারি দিয়েছি (`{'count': 4}`), Pydantic নিজেই সেগুলো থেকে `Foo` আর `Bar` অবজেক্ট বানিয়ে নিয়েছে, ডিফল্ট মানও বসিয়েছে (`size=None`, `banana='y'`)। `model_dump()` আবার পুরোটাকে নেস্টেড ডিকশনারিতে ফিরিয়ে দেয়। FastAPI-তে JSON বডির ভেতরে JSON অবজেক্ট এভাবেই সামলানো হয়।

///

### চক্রাকার রেফারেন্স (Cyclic references) { #cyclic-references }

নিজেকেই নির্দেশ করে এমন পুনরাবৃত্ত মডেল নিয়ে কাজ করার সময়, যাচাইয়ের ইনপুটে চক্রাকার রেফারেন্স
পেতে পারেন। যেমন, অ্যাট্রিবিউট থেকে back-reference থাকা ORM ইনস্ট্যান্স যাচাই করার সময় এটি ঘটতে পারে।

চক্রাকার রেফারেন্সসহ ডেটা যাচাইয়ের চেষ্টায় একটি [`RecursionError`][] দেওয়ার বদলে, Pydantic
চক্রাকার রেফারেন্স শনাক্ত করে একটি উপযুক্ত [`ValidationError`][pydantic_core.ValidationError] দিতে পারে:

/// tab | Python 3.10 ও তার পরে

```python
from pydantic import BaseModel, ValidationError


class ModelA(BaseModel):
    b: 'ModelB | None' = None  # (1)!


class ModelB(BaseModel):
    a: ModelA | None = None


cyclic_data = {}
cyclic_data['a'] = {'b': cyclic_data}
print(cyclic_data)
#> {'a': {'b': {...}}}

try:
    ModelB.model_validate(cyclic_data)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for ModelB
    a.b
      Recursion error - cyclic reference detected [type=recursion_loop, input_value={'a': {'b': {...}}}, input_type=dict]
    """
```

1. যেহেতু `ModelB` এখনো সংজ্ঞায়িত হয়নি, তাই একটি [forward annotation](forward_annotations.md) (উদ্ধৃতিচিহ্নে লেখা টাইপ) ব্যবহার করতে হবে।

///

/// tab | Python 3.14 ও তার পরে

```python
from pydantic import BaseModel, ValidationError


class ModelA(BaseModel):
    b: ModelB | None = None


class ModelB(BaseModel):
    a: ModelA | None = None


cyclic_data = {}
cyclic_data['a'] = {'b': cyclic_data}
print(cyclic_data)
#> {'a': {'b': {...}}}

try:
    ModelB.model_validate(cyclic_data)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for ModelB
    a.b
      Recursion error - cyclic reference detected [type=recursion_loop, input_value={'a': {'b': {...}}}, input_type=dict]
    """
```

///

(Python 3.14-এ অ্যানোটেশন দেরিতে মূল্যায়ন হয়, তাই উদ্ধৃতিচিহ্ন ছাড়াই পরে সংজ্ঞায়িত ক্লাসের নাম লেখা যায়।)

আরও দেখুন: [চক্রাকার রেফারেন্সের উদাহরণ](../examples/cyclic_references.md), যা যাচাই আর সিরিয়ালাইজেশনের সময় এমন
চক্রাকার রেফারেন্স কীভাবে সামলাতে হয় তা দেখায়, আর [চক্রাকার ইমপোর্ট](forward_annotations.md#cyclic-imports)
অংশ, আলাদা মডিউল থেকে একে অপরকে নির্দেশ করা মডেলের জন্য।

## মডেল schema আবার তৈরি করা { #rebuilding-model-schema }

কোডে যখন একটি মডেল ক্লাস সংজ্ঞায়িত করেন, Pydantic যাচাই আর সিরিয়ালাইজেশনের জন্য দরকারি নানা তথ্য সংগ্রহ করতে
ক্লাসের ভেতরের অংশ বিশ্লেষণ করে, আর তা একটি core schema-তে জড়ো করে। বিশেষ করে, প্রতিটি ফিল্ডের বৈধ টাইপ বুঝতে মডেলের টাইপ অ্যানোটেশনগুলো
মূল্যায়ন করা হয় (আরও তথ্য পাবেন [আর্কিটেকচার](../internals/architecture.md) ডকুমেন্টেশনে)।
তবে এমন হতে পারে যে অ্যানোটেশনগুলো এমন নাম নির্দেশ করে যা মডেল ক্লাস তৈরির সময় সংজ্ঞায়িত নয়।
এই সমস্যা এড়াতে [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] মেথড ব্যবহার করা যায়:

```python
from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    x: 'Bar'  # (1)!


try:
    Foo.model_json_schema()
except PydanticUserError as e:
    print(e)
    """
    `Foo` is not fully defined; you should define `Bar`, then call `Foo.model_rebuild()`.

    For further information visit https://errors.pydantic.dev/2/u/class-not-fully-defined
    """


class Bar(BaseModel):
    pass


Foo.model_rebuild()
print(Foo.model_json_schema())
"""
{
    '$defs': {'Bar': {'properties': {}, 'title': 'Bar', 'type': 'object'}},
    'properties': {'x': {'$ref': '#/$defs/Bar'}},
    'required': ['x'],
    'title': 'Foo',
    'type': 'object',
}
"""
```

1. `Foo` ক্লাস তৈরির সময় `Bar` এখনো সংজ্ঞায়িত হয়নি। এই কারণে
    একটি [forward annotation](forward_annotations.md) ব্যবহার করা হচ্ছে।

/// info | কোডটি সহজ ভাষায়

`Foo` তৈরির সময় `'Bar'` শুধু একটি নাম, আসল ক্লাস নেই। তাই `Foo.model_json_schema()` এরর দেয়: "`Bar` সংজ্ঞায়িত করে তারপর `Foo.model_rebuild()` কল করুন"। `Bar` সংজ্ঞায়িত করে `Foo.model_rebuild()` কল করলে Pydantic আবার সব মিলিয়ে নেয়, আর এবার schema ঠিকমতো তৈরি হয়।

///

কখন এটি দরকার তা Pydantic স্বয়ংক্রিয়ভাবে নির্ধারণের চেষ্টা করে আর না করা হলে এরর দেয়, তবে পুনরাবৃত্ত মডেল বা generic নিয়ে কাজ করার সময়
আপনি আগেভাগেই [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] কল করতে চাইতে পারেন।

V2-তে, [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] V1-এর `update_forward_refs()`-এর জায়গা নিয়েছে। নতুন আচরণে কিছু সামান্য পার্থক্য আছে।
সবচেয়ে বড় পরিবর্তন হলো, সবচেয়ে বাইরের মডেলে [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] কল করলে, এটি পুরো মডেলের (নেস্টেড মডেলসহ সব) যাচাইয়ে ব্যবহৃত
একটি core schema তৈরি করে, তাই [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] কল করার আগে সব স্তরের সব টাইপ প্রস্তুত থাকতে হবে।

## ডেটা যাচাই { #validating-data }

Pydantic তিনটি ভিন্ন মোডে ডেটা যাচাই করতে পারে: *Python*, *JSON* আর *strings*।

*Python* মোড ব্যবহার হয় যখন ব্যবহার করেন:

* মডেলের `__init__()` constructor। ফিল্ডের মান keyword argument দিয়ে দিতে হবে।
* [`model_validate()`][pydantic.main.BaseModel.model_validate]: ডেটা দেওয়া যায় হয় একটি ডিকশনারি হিসেবে,
  নয়তো একটি মডেল ইনস্ট্যান্স হিসেবে (ডিফল্টভাবে ইনস্ট্যান্সগুলো বৈধ বলে ধরে নেওয়া হয়; দেখুন [`revalidate_instances`][pydantic.ConfigDict.revalidate_instances]
  সেটিং)। স্পষ্টভাবে চালু করলে [যেকোনো অবজেক্ট](#arbitrary-class-instances)-ও দেওয়া যায়।

*JSON* আর *strings* মোড নির্দিষ্ট মেথড দিয়ে ব্যবহার করা যায়:

* [`model_validate_json()`][pydantic.main.BaseModel.model_validate_json]: ডেটা একটি JSON স্ট্রিং বা `bytes` অবজেক্ট হিসেবে যাচাই হয়।
  আপনার আগত ডেটা একটি JSON payload হলে, এটি সাধারণত বেশি দ্রুত বলে বিবেচিত (নিজে হাতে ডেটাকে ডিকশনারি হিসেবে পার্স করার চেয়ে)।
  JSON পার্সিং নিয়ে আরও জানুন [JSON](../concepts/json.md) ডকুমেন্টেশনে।
* [`model_validate_strings()`][pydantic.main.BaseModel.model_validate_strings]: ডেটা স্ট্রিং key আর মানসহ একটি ডিকশনারি (নেস্টেড হতে পারে) হিসেবে যাচাই হয়,
  আর JSON মোডে যাচাই করে যাতে ওই স্ট্রিংগুলো সঠিক টাইপে রূপান্তরিত হতে পারে।

মডেলের constructor ব্যবহারের তুলনায়, `model_validate_*()` মেথড ব্যবহার করলে কয়েকটি যাচাইয়ের প্যারামিটার নিয়ন্ত্রণ করা যায়
([কঠোরতা](./strict_mode.md), [বাড়তি ডেটা](#extra-data), [যাচাইয়ের প্রসঙ্গ](./validators.md#validation-context) ইত্যাদি)।

/// note | নোট

জড়িত টাইপ আর মডেলের configuration-এর ওপর নির্ভর করে, *Python* আর *JSON* মোডের যাচাইয়ের আচরণ ভিন্ন হতে পারে (যেমন [কঠোরতা](./strict_mode.md)-র ক্ষেত্রে)।
যদি আপনার ডেটা JSON নয় এমন উৎস থেকে আসে, কিন্তু *JSON* মোডের মতো একই যাচাইয়ের আচরণ আর এরর চান, তাহলে আপাতত আমাদের পরামর্শ হলো
হয় আপনার ডেটা JSON-এ dump করুন (যেমন [`json.dumps()`][json.dumps] দিয়ে), নয়তো ডেটা যদি স্ট্রিং key আর মানসহ একটি (সম্ভবত নেস্টেড) ডিকশনারির রূপে থাকে
তাহলে [`model_validate_strings()`][pydantic.main.BaseModel.model_validate_strings] ব্যবহার করুন। এই ফিচারের অগ্রগতি
[এই issue](https://github.com/pydantic/pydantic/issues/11154)-তে দেখা যাবে।

///

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None = None


m = User.model_validate({'id': 123, 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

try:
    m = User.model_validate_json('{"id": 123, "name": 123}')
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      Input should be a valid string [type=string_type, input_value=123, input_type=int]
    """

m = User.model_validate_strings({'id': '123', 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

m = User.model_validate_strings(
    {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01T12:00:00'}
)
print(m)
#> id=123 name='James' signup_ts=datetime.datetime(2024, 4, 1, 12, 0)

try:
    m = User.model_validate_strings(
        {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01'}, strict=True
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    signup_ts
      Input should be a valid datetime, invalid datetime separator, expected `T`, `t`, `_` or space [type=datetime_parsing, input_value='2024-04-01', input_type=str]
    """
```

/// info | কোডটি সহজ ভাষায়

* `model_validate({...})`: Python ডিকশনারি থেকে মডেল।
* `model_validate_json('{"id": 123, "name": 123}')`: JSON স্ট্রিং থেকে মডেল; এখানে `name` একটি সংখ্যা, তাই এরর (JSON মোডে সংখ্যা স্ট্রিং হয় না)।
* `model_validate_strings({...})`: সব মান স্ট্রিং হলেও (যেমন `'123'`, `'2024-04-01T12:00:00'`) সঠিক টাইপে রূপান্তর। এটি এনভায়রনমেন্ট ভেরিয়েবল বা URL কোয়েরির মতো "সবকিছু স্ট্রিং" উৎসের জন্য দারুণ।
* `strict=True` দিলে শুধু তারিখ (`'2024-04-01'`) একটি datetime হিসেবে গ্রহণযোগ্য নয়, পূর্ণ তারিখ-সময় লাগবে।

///

### যাচাই ছাড়া মডেল তৈরি { #creating-models-without-validation }

Pydantic [`model_construct()`][pydantic.main.BaseModel.model_construct] মেথডও দেয়, যা দিয়ে **যাচাই ছাড়াই** মডেল তৈরি করা যায়।
এটি অন্তত কয়েকটি ক্ষেত্রে কাজে লাগতে পারে:

* এমন জটিল ডেটা নিয়ে কাজ করার সময় যা ইতিমধ্যে বৈধ বলে জানা (পারফরম্যান্সের কারণে)
* যখন এক বা একাধিক validator ফাংশন non-idempotent (বারবার চালালে ভিন্ন ফল দেয়)
* যখন এক বা একাধিক validator ফাংশনের এমন পার্শ্বপ্রতিক্রিয়া (side effect) আছে যা আপনি চালু করতে চান না।

/// warning | সতর্কতা

[`model_construct()`][pydantic.main.BaseModel.model_construct] কোনো যাচাই করে না, অর্থাৎ এটি
অবৈধ মডেলও তৈরি করতে পারে। **[`model_construct()`][pydantic.main.BaseModel.model_construct]
মেথড শুধু এমন ডেটার সাথেই ব্যবহার করুন যা ইতিমধ্যে যাচাই করা হয়েছে, বা যা আপনি নিশ্চিতভাবে বিশ্বাস করেন।**

///

/// note | নোট

Pydantic V2-তে, যাচাই (সরাসরি ইনস্ট্যান্স তৈরি বা `model_validate*` মেথড দিয়ে)
আর [`model_construct()`][pydantic.main.BaseModel.model_construct]-এর মধ্যে পারফরম্যান্সের ব্যবধান অনেকটাই
কমে এসেছে। সাধারণ মডেলের ক্ষেত্রে, যাচাই করাই এমনকি দ্রুত হতে পারে। যদি পারফরম্যান্সের কারণে [`model_construct()`][pydantic.main.BaseModel.model_construct]
ব্যবহার করেন, তাহলে আসলেই দ্রুত কিনা ধরে নেওয়ার আগে আপনার ক্ষেত্রটি মেপে (profile করে) দেখতে চাইতে পারেন।

///

লক্ষ্য করুন, [root মডেলের](#rootmodel-and-custom-root-types) ক্ষেত্রে, root মান keyword argument ব্যবহারের বদলে
[`model_construct()`][pydantic.main.BaseModel.model_construct]-এ অবস্থান অনুযায়ী (positionally) দেওয়া যায়।

[`model_construct()`][pydantic.main.BaseModel.model_construct]-এর আচরণ নিয়ে আরও কিছু নোট:

* যখন বলি "কোনো যাচাই হয় না" — এর মধ্যে ডিকশনারিকে মডেল ইনস্ট্যান্সে রূপান্তরও পড়ে। তাই যদি আপনার কোনো ফিল্ড
  একটি মডেল টাইপ নির্দেশ করে, তাহলে ভেতরের ডিকশনারিকে নিজেকেই একটি মডেলে রূপান্তর করতে হবে।
* ডিফল্ট মানওয়ালা ফিল্ডের জন্য keyword argument না দিলে, তবুও ডিফল্ট মানগুলো ব্যবহার হবে।
* private অ্যাট্রিবিউটসহ মডেলের ক্ষেত্রে, `__pydantic_private__` ডিকশনারি ঠিক সেভাবেই পূরণ হবে যেভাবে
  যাচাইসহ মডেল তৈরির সময় হতো।
* মডেল বা এর কোনো প্যারেন্ট ক্লাসের কোনো `__init__` মেথড কল হবে না, এমনকি একটি কাস্টম `__init__` মেথড সংজ্ঞায়িত থাকলেও।

/// note | [`model_construct()`][pydantic.main.BaseModel.model_construct]-এর সাথে [বাড়তি ডেটার](#extra-data) আচরণ

* [`extra`][pydantic.ConfigDict.extra] `'allow'` সেট করা মডেলের ক্ষেত্রে, ফিল্ডের সাথে মেলে না এমন ডেটা সঠিকভাবে
`__pydantic_extra__` ডিকশনারিতে রাখা হবে আর মডেলের `__dict__` অ্যাট্রিবিউটে সংরক্ষিত হবে।
* [`extra`][pydantic.ConfigDict.extra] `'ignore'` সেট করা মডেলের ক্ষেত্রে, ফিল্ডের সাথে মেলে না এমন ডেটা উপেক্ষা করা হবে — অর্থাৎ
ইনস্ট্যান্সের `__pydantic_extra__` বা `__dict__`-এ রাখা হবে না।
* যাচাইসহ মডেল তৈরির সময়ের মতো নয়, [`extra`][pydantic.ConfigDict.extra] `'forbid'` সেট করা অবস্থায় [`model_construct()`][pydantic.main.BaseModel.model_construct] কল করলে ফিল্ডের সাথে মেলে না এমন ডেটা থাকলে এরর হয় না। বরং ওই ইনপুট ডেটা শুধু উপেক্ষা করা হয়।

///

### একটি কাস্টম `__init__()` সংজ্ঞায়িত করা { #defining-a-custom-init }

Pydantic মডেলের জন্য Pydantic একটি ডিফল্ট `__init__()` বাস্তবায়ন দেয়, যা কল হয় *শুধু* মডেলের constructor ব্যবহারের সময়
(`model_validate_*()` মেথডের সাথে নয়)। এই বাস্তবায়ন যাচাইয়ের কাজ `pydantic-core`-কে দেয়।

তবে আপনার মডেলে একটি কাস্টম `__init__()` সংজ্ঞায়িত করা সম্ভব। এই ক্ষেত্রে, এটি সব
[যাচাইয়ের মেথড](#validating-data) থেকে শর্তহীনভাবে কল হবে, যাচাই না চালিয়ে (তাই আপনার বাস্তবায়নে `super().__init__(**kwargs)` কল করা উচিত)।

একটি কাস্টম `__init__()` সংজ্ঞায়িত করার পরামর্শ দেওয়া হয় না, কারণ সব যাচাইয়ের প্যারামিটার ([কঠোরতা](./strict_mode.md),
[বাড়তি ডেটার আচরণ](#extra-data), [যাচাইয়ের প্রসঙ্গ](./validators.md#validation-context)) হারিয়ে যাবে। মডেল তৈরির পরে যদি
কোনো কাজ করতে হয়, তাহলে *after* [ফিল্ড](./validators.md#field-after-validator) বা
[মডেল](./validators.md#model-after-validator) validator ব্যবহার করতে পারেন, অথবা একটি [`model_post_init()`][pydantic.main.BaseModel.model_post_init] বাস্তবায়ন সংজ্ঞায়িত করতে পারেন:

```python
import logging
from typing import Any

from pydantic import BaseModel


class MyModel(BaseModel):
    id: int

    def model_post_init(self, context: Any) -> None:
        logging.info("Model initialized with id %d", self.id)
```

(এখানে মডেল তৈরি আর যাচাই শেষ হওয়ার পরে `model_post_init` চলে আর একটি লগ বার্তা লেখে। মডেল তৈরির পরের যেকোনো বাড়তি কাজের জন্য এটাই নিরাপদ জায়গা।)

## এরর সামলানো { #error-handling }

যাচাই করা ডেটায় কোনো এরর পেলেই Pydantic একটি [`ValidationError`][pydantic_core.ValidationError] এক্সেপশন দেবে।

কতগুলো এরর পাওয়া গেল তা নির্বিশেষে একটিই এক্সেপশন হবে, আর সেই যাচাই এররে
সব এরর আর সেগুলো কীভাবে ঘটল তার তথ্য থাকবে।

স্ট্যান্ডার্ড আর কাস্টম এররের বিস্তারিত জানতে দেখুন [এরর সামলানো](../errors/errors.md)।

উদাহরণ হিসেবে:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    list_of_ints: list[int]
    a_float: float


data = {
    'list_of_ints': ['1', 2, 'bad'],
    'a_float': 'not a float',
}

try:
    Model(**data)
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    list_of_ints.2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]
    a_float
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a float', input_type=str]
    """
```

/// info | এরর বার্তাটি সহজ ভাষায়

`2 validation errors for Model` মানে মোট দুটি ভুল। প্রথম ভুলের অবস্থান `list_of_ints.2`, অর্থাৎ `list_of_ints` তালিকার ২ নম্বর ইনডেক্সের (তৃতীয়) উপাদান `'bad'` সংখ্যা নয়। দ্বিতীয়টি `a_float`-এ `'not a float'` সংখ্যা নয়। বন্ধনীর ভেতরে এররের ধরন (`type`), আসল ইনপুট আর তার টাইপ দেখানো হয়েছে। লক্ষ্য করুন, `'1'` ঠিকই রূপান্তর হয়েছে, তাই সেটি এরর নয়।

///

এমন একটি উদাহরণে, সমস্যাযুক্ত `data` কোডেই আছে। একটি
[`ValidationError`][pydantic_core.ValidationError] প্রতিটি ব্যর্থ অবস্থানে প্রত্যাখ্যাত মান রাখে, কিন্তু একটি চলমান
অ্যাপ্লিকেশনে আপনার হয়তো সেই বিবরণগুলো তাদের রিকোয়েস্ট বা কাজের প্রসঙ্গসহও দরকার হতে পারে। [Logfire ব্যর্থ যাচাইগুলো](../errors/troubleshooting.md)
দুটোসহ রেকর্ড করে।

## যেকোনো ক্লাসের ইনস্ট্যান্স (Arbitrary class instances) { #arbitrary-class-instances }

(আগে "ORM Mode"/`from_orm()` নামে পরিচিত ছিল।)

[`model_validate()`][pydantic.main.BaseModel.model_validate] মেথড ব্যবহারের সময়, Pydantic যেকোনো অবজেক্টও যাচাই করতে পারে,
অবজেক্ট থেকে ফিল্ডের নামের সাথে মেলে এমন অ্যাট্রিবিউটগুলো নিয়ে। এই সুবিধার একটি প্রচলিত ব্যবহার হলো
ORM (object-relational mapping, অর্থাৎ ডেটাবেসের টেবিলকে Python ক্লাস হিসেবে ব্যবহারের টুল)-এর সাথে সংযোগ।

এই ফিচারটি নিজে হাতে চালু করতে হয়, হয় [`from_attributes`][pydantic.config.ConfigDict.from_attributes]
configuration মান সেট করে, নয়তো [`model_validate()`][pydantic.main.BaseModel.model_validate]-এ `from_attributes` প্যারামিটার ব্যবহার করে।

এখানের উদাহরণে [SQLAlchemy](https://www.sqlalchemy.org/) ব্যবহার করা হয়েছে, কিন্তু একই পদ্ধতি যেকোনো ORM-এর জন্য কাজ করা উচিত।

```python
from typing import Annotated

from sqlalchemy import ARRAY, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pydantic import BaseModel, ConfigDict, StringConstraints


class Base(DeclarativeBase):
    pass


class CompanyOrm(Base):
    __tablename__ = 'companies'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    public_key: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, unique=True
    )
    domains: Mapped[list[str]] = mapped_column(ARRAY(String(255)))


class CompanyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_key: Annotated[str, StringConstraints(max_length=20)]
    domains: list[Annotated[str, StringConstraints(max_length=255)]]


co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    domains=['example.com', 'foobar.com'],
)
print(co_orm)
#> <__main__.CompanyOrm object at 0x0123456789ab>
co_model = CompanyModel.model_validate(co_orm)
print(co_model)
#> id=123 public_key='foobar' domains=['example.com', 'foobar.com']
```

/// info | কোডটি সহজ ভাষায়

* `CompanyOrm` হলো ডেটাবেসের টেবিলের SQLAlchemy ক্লাস।
* `CompanyModel`-এ `from_attributes=True` থাকায়, `model_validate(co_orm)` একটি ডিকশনারির বদলে সরাসরি ORM অবজেক্টটি নেয়, আর `co_orm.id`, `co_orm.public_key`, `co_orm.domains` অ্যাট্রিবিউট পড়ে মডেল তৈরি করে।
* FastAPI-তে ডেটাবেস থেকে আসা অবজেক্ট `response_model` দিয়ে ফেরত দেওয়ার সময় ঠিক এই কৌশলটিই কাজ করে।

///

### নেস্টেড অ্যাট্রিবিউট { #nested-attributes }

অ্যাট্রিবিউট ব্যবহার করে মডেল যাচাই করার সময়, প্রয়োজনমতো শীর্ষ-স্তরের অ্যাট্রিবিউট আর
গভীরে নেস্টেড অ্যাট্রিবিউট দুটো থেকেই মডেল ইনস্ট্যান্স তৈরি হবে।

নীতিটি দেখানো একটি উদাহরণ:

```python
from pydantic import BaseModel, ConfigDict


class PetCls:
    def __init__(self, *, name: str) -> None:
        self.name = name


class PersonCls:
    def __init__(self, *, name: str, pets: list[PetCls]) -> None:
        self.name = name
        self.pets = pets


class Pet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    pets: list[Pet]


bones = PetCls(name='Bones')
orion = PetCls(name='Orion')
anna = PersonCls(name='Anna', pets=[bones, orion])
anna_model = Person.model_validate(anna)
print(anna_model)
#> name='Anna' pets=[Pet(name='Bones'), Pet(name='Orion')]
```

(`anna.pets` তালিকার প্রতিটি `PetCls` অবজেক্টও অ্যাট্রিবিউট পড়ে `Pet` মডেলে রূপান্তরিত হয়েছে।)

## মডেল কপি { #model-copy }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.main.BaseModel.model_copy`][pydantic.main.BaseModel.model_copy]<br>

///

[`model_copy()`][pydantic.BaseModel.model_copy] মেথড দিয়ে মডেলের প্রতিলিপি তৈরি করা যায় (ঐচ্ছিক আপডেটসহ, যা যাচাই *করা হয় না*),
যা বিশেষ করে frozen (অপরিবর্তনীয়) মডেল নিয়ে কাজ করার সময় কাজের।

```python
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

print(m.model_copy(update={'banana': 0}))
#> banana=0 foo='hello' bar=BarModel(whatever=123)

# normal copy gives the same object reference for bar:
print(id(m.bar) == id(m.model_copy().bar))
#> True
# deep copy gives a new object reference for `bar`:
print(id(m.bar) == id(m.model_copy(deep=True).bar))
#> False
```

/// info | কোডটি সহজ ভাষায়

* `model_copy(update={'banana': 0})`: একটি কপি, যেখানে শুধু `banana` বদলানো। মনে রাখবেন, `update`-এর মান যাচাই হয় না, তাই সঠিক টাইপ নিজেই দিন।
* সাধারণ কপি (shallow) হলে ভেতরের `bar` অবজেক্টটি একই থাকে (দুই মডেল একই `bar` ভাগ করে)।
* `deep=True` দিলে ভেতরের অবজেক্টেরও নতুন কপি তৈরি হয়।

///

## Generic মডেল { #generic-models }

একটি সাধারণ মডেলের কাঠামো সহজে পুনরায় ব্যবহারের জন্য Pydantic generic মডেল তৈরি সমর্থন করে। নতুন
[টাইপ প্যারামিটার সিনট্যাক্স][type-params] (Python 3.12-এ [PEP 695](https://peps.python.org/pep-0695/) দিয়ে আনা)
আর পুরনো সিনট্যাক্স দুটোই সমর্থিত (আরও বিস্তারিত জানতে
[Python ডকুমেন্টেশন](https://docs.python.org/3/library/typing.html#building-generic-types-and-type-aliases)
দেখুন)।

/// tip | উদাহরণ দিয়ে বুঝি

Generic মডেল হলো একটি "ফাঁকা ঘরসহ" ছাঁচ। ধরুন প্রতিটি API উত্তরের মোড়ক একই: `{"data": ...}`, শুধু `data`-র ভেতরে কখনো সংখ্যা, কখনো একজন ইউজার, কখনো পণ্যের তালিকা। প্রতিটির জন্য আলাদা মডেল না লিখে একটি `Response[DataT]` লিখে, ব্যবহারের সময় বলে দেন `Response[User]` বা `Response[int]`।

///

একটি সহজে পুনরায় ব্যবহারযোগ্য HTTP রেসপন্স payload মোড়ক তৈরিতে একটি generic Pydantic মডেল ব্যবহারের উদাহরণ:

<!-- TODO: tabs should be auto-generated if using Ruff (https://github.com/pydantic/pydantic/issues/10083) -->

/// tab | Python 3.10 ও তার পরে

```python
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

DataT = TypeVar('DataT')  # (1)!


class DataModel(BaseModel):
    number: int


class Response(BaseModel, Generic[DataT]):  # (2)!
    data: DataT  # (3)!


print(Response[int](data=1))
#> data=1
print(Response[str](data='value'))
#> data='value'
print(Response[str](data='value').model_dump())
#> {'data': 'value'}

data = DataModel(number=1)
print(Response[DataModel](data=data).model_dump())
#> {'data': {'number': 1}}
try:
    Response[int](data='value')
except ValidationError as e:
    print(e)
    """
    1 validation error for Response[int]
    data
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]
    """
```

1. আপনার মডেলকে প্যারামিটারাইজ করতে এক বা একাধিক [টাইপ ভেরিয়েবল][typing.TypeVar] ঘোষণা করুন।
2. একটি Pydantic মডেল ঘোষণা করুন যা [`BaseModel`][pydantic.BaseModel] আর [`typing.Generic`][] থেকে উত্তরাধিকার পায়
   (ঠিক এই ক্রমে), আর আগে ঘোষণা করা টাইপ ভেরিয়েবলগুলোর তালিকা [`Generic`][typing.Generic] প্যারেন্টে
   প্যারামিটার হিসেবে যোগ করুন।
3. যেখানে পরে অন্য টাইপ বসাতে চান, সেখানে টাইপ ভেরিয়েবলগুলো অ্যানোটেশন হিসেবে ব্যবহার করুন।

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

```python
from pydantic import BaseModel, ValidationError


class DataModel(BaseModel):
    number: int


class Response[DataT](BaseModel):  # (1)!
    data: DataT  # (2)!


print(Response[int](data=1))
#> data=1
print(Response[str](data='value'))
#> data='value'
print(Response[str](data='value').model_dump())
#> {'data': 'value'}

data = DataModel(number=1)
print(Response[DataModel](data=data).model_dump())
#> {'data': {'number': 1}}
try:
    Response[int](data='value')
except ValidationError as e:
    print(e)
    """
    1 validation error for Response[int]
    data
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]
    """
```

1. একটি Pydantic মডেল ঘোষণা করে টাইপ ভেরিয়েবলগুলোর তালিকা টাইপ প্যারামিটার হিসেবে যোগ করুন।
2. যেখানে পরে অন্য টাইপ বসাতে চান, সেখানে টাইপ ভেরিয়েবলগুলো অ্যানোটেশন হিসেবে ব্যবহার করুন।

///

/// info | v2.11-এ যোগ হয়েছে
[টাইপ প্যারামিটার সিনট্যাক্স][type-params] আর [টাইপ ভেরিয়েবলের ডিফল্ট](https://typing.python.org/en/latest/spec/generics.html#type-parameter-defaults)-এর পূর্ণ সমর্থন।
///

/// warning | সতর্কতা

একটি নির্দিষ্ট টাইপ দিয়ে মডেল প্যারামিটারাইজ করার সময়, যদি টাইপ ভেরিয়েবলের একটি upper bound থাকে, তাহলে দেওয়া টাইপটি
[টাইপ ভেরিয়েবলে বসানোর যোগ্য কিনা][spec-typevars-bound] Pydantic তা যাচাই **করে না**।

[spec-typevars-bound]: https://typing.readthedocs.io/en/latest/spec/generics.html#type-variables-with-an-upper-bound

///

generic মডেলে সেট করা যেকোনো [configuration](./config.md), [যাচাই](./validators.md) বা [সিরিয়ালাইজেশন](./serialization.md)-এর যুক্তি
প্যারামিটারাইজ করা ক্লাসগুলোতেও প্রয়োগ হবে, ঠিক যেভাবে একটি মডেল ক্লাস থেকে উত্তরাধিকার নেওয়ার সময় হয়। যেকোনো কাস্টম মেথড বা অ্যাট্রিবিউটও
উত্তরাধিকারসূত্রে আসবে।

generic মডেল টাইপ চেকারের সাথেও সঠিকভাবে মিশে যায়, তাই প্রতিটি প্যারামিটারাইজেশনের জন্য আলাদা টাইপ ঘোষণা করলে
যে টাইপ চেকিং আশা করতেন তার সবই পাবেন।

/// note | নোট

ভেতরে ভেতরে, generic মডেল ক্লাস প্যারামিটারাইজ করা হলে Pydantic চলমান অবস্থায় generic মডেলের সাব-ক্লাস তৈরি করে।
এই ক্লাসগুলো cache করা থাকে, তাই generic মডেল ব্যবহারে বাড়তি খরচ খুবই কম হওয়া উচিত।

///

একটি generic মডেল থেকে উত্তরাধিকার নিয়ে এটি যে generic তা বজায় রাখতে, সাব-ক্লাসটিকেও
[`Generic`][typing.Generic] থেকে উত্তরাধিকার নিতে হবে:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TypeX = TypeVar('TypeX')


class BaseClass(BaseModel, Generic[TypeX]):
    X: TypeX


class ChildClass(BaseClass[TypeX], Generic[TypeX]):
    pass


# Parametrize `TypeX` with `int`:
print(ChildClass[int](X=1))
#> X=1
```

একটি মডেলের এমন generic সাব-ক্লাসও তৈরি করতে পারেন যা প্যারেন্ট ক্লাসের টাইপ ভেরিয়েবলগুলো আংশিক বা পুরোপুরি
বদলে দেয়:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TypeX = TypeVar('TypeX')
TypeY = TypeVar('TypeY')
TypeZ = TypeVar('TypeZ')


class BaseClass(BaseModel, Generic[TypeX, TypeY]):
    x: TypeX
    y: TypeY


class ChildClass(BaseClass[int, TypeY], Generic[TypeY, TypeZ]):
    z: TypeZ


# Parametrize `TypeY` with `str`:
print(ChildClass[str, int](x='1', y='y', z='3'))
#> x=1 y='y' z=3
```

(এখানে `TypeX`-কে স্থায়ীভাবে `int` করে দেওয়া হয়েছে, `TypeY` এখনো খোলা, আর নতুন একটি `TypeZ` যোগ হয়েছে। তাই `ChildClass[str, int]` মানে `y` হবে `str` আর `z` হবে `int`।)

যদি নির্দিষ্ট সাব-ক্লাসগুলোর নাম গুরুত্বপূর্ণ হয়, তাহলে [`model_parametrized_name()`][pydantic.main.BaseModel.model_parametrized_name] মেথড ওভাররাইড করে
ডিফল্ট নাম তৈরির নিয়মও বদলাতে পারেন:

```python
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar('DataT')


class Response(BaseModel, Generic[DataT]):
    data: DataT

    @classmethod
    def model_parametrized_name(cls, params: tuple[type[Any], ...]) -> str:
        return f'{params[0].__name__.title()}Response'


print(repr(Response[int](data=1)))
#> IntResponse(data=1)
print(repr(Response[str](data='a')))
#> StrResponse(data='a')
```

প্যারামিটারাইজ করা generic মডেল অন্য মডেলে টাইপ হিসেবে ব্যবহার করতে পারেন:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    content: T


class Product(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    id: int
    product: ResponseModel[Product]


product = Product(name='Apple', price=0.5)
response = ResponseModel[Product](content=product)
order = Order(id=1, product=response)
print(repr(order))
"""
Order(id=1, product=ResponseModel[Product](content=Product(name='Apple', price=0.5)))
"""
```

নেস্টেড মডেলে একই টাইপ ভেরিয়েবল ব্যবহার করে আপনার মডেলের বিভিন্ন জায়গায় টাইপের সম্পর্ক বাধ্যতামূলক করতে পারেন:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar('T')


class InnerT(BaseModel, Generic[T]):
    inner: T


class OuterT(BaseModel, Generic[T]):
    outer: T
    nested: InnerT[T]


nested = InnerT[int](inner=1)
print(OuterT[int](outer=1, nested=nested))
#> outer=1 nested=InnerT[int](inner=1)
try:
    print(OuterT[int](outer='a', nested=InnerT(inner='a')))  # (1)!
except ValidationError as e:
    print(e)
    """
    2 validation errors for OuterT[int]
    outer
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    nested.inner
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

1. `OuterT` মডেলটি `int` দিয়ে প্যারামিটারাইজ করা, কিন্তু যাচাইয়ের সময় `T` অ্যানোটেশনের সাথে যুক্ত ডেটা `str` টাইপের, ফলে যাচাই এরর হয়।

/// warning | সতর্কতা

এটি এরর না দিলেও, [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) যাচাইয়ে প্যারামিটারাইজ করা generic ব্যবহার না করার জোর পরামর্শ দিই।

যেমন, `isinstance(my_model, MyGenericModel[int])` করা উচিত নয়। তবে `isinstance(my_model, MyGenericModel)` করা ঠিক আছে (লক্ষ্য করুন, স্ট্যান্ডার্ড generic-এর ক্ষেত্রে প্যারামিটারাইজ করা generic ক্লাস দিয়ে সাব-ক্লাস যাচাই করলে এরর হতো)।

যদি প্যারামিটারাইজ করা generic-এর বিপরীতে [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) যাচাই করতেই হয়, তাহলে প্যারামিটারাইজ করা generic ক্লাসের সাব-ক্লাস বানিয়ে তা করতে পারেন:

```python
class MyIntModel(MyGenericModel[int]): ...

isinstance(my_model, MyIntModel)
```

///

/// details | বাস্তবায়নের বিবরণ
    type: note

নেস্টেড generic মডেল ব্যবহারের সময়, সবচেয়ে স্বাভাবিক যাচাইয়ের ফলাফল দেওয়ার চেষ্টায় Pydantic কখনো কখনো আবার যাচাই (revalidation) করে।
বিশেষ করে, যদি আপনার `GenericModel[SomeType]` টাইপের একটি ফিল্ড থাকে আর এই ফিল্ডের বিপরীতে `GenericModel[SomeCompatibleType]`-এর মতো ডেটা যাচাই করেন,
তাহলে আমরা ডেটাটি পরীক্ষা করব, বুঝব যে ইনপুট ডেটা `GenericModel`-এর এক ধরনের "ঢিলেঢালা" সাব-ক্লাস, আর ভেতরের `SomeCompatibleType` ডেটা আবার যাচাই করব।

এতে কিছু বাড়তি যাচাইয়ের খরচ হয়, কিন্তু নিচের মতো ক্ষেত্রে বিষয়গুলো আরও স্বাভাবিক হয়।

```python
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class GenericModel(BaseModel, Generic[T]):
    a: T


class Model(BaseModel):
    inner: GenericModel[Any]


print(repr(Model.model_validate(Model(inner=GenericModel[int](a=1)))))
#> Model(inner=GenericModel[Any](a=1))
```

লক্ষ্য করুন, যেমন যদি `GenericModel[int]`-এর বিপরীতে যাচাই করেন আর একটি ইনস্ট্যান্স `GenericModel[str](a='not an int')` দেন, তাহলে যাচাই তবুও ব্যর্থ হবে।

এটাও উল্লেখযোগ্য যে এই পদ্ধতি যেকোনো কাস্টম যাচাইও আবার চালু করবে, যেমন বাড়তি মডেল validator ইত্যাদি।
প্রথম ধাপে validator একবার কল হবে, সরাসরি `GenericModel[Any]`-এর বিপরীতে যাচাই করে। সেই যাচাই ব্যর্থ হয়, কারণ `GenericModel[int]` `GenericModel[Any]`-এর সাব-ক্লাস নয়। এটি `isinstance()` আর `issubclass()` যাচাইয়ে প্যারামিটারাইজ করা generic ব্যবহারের জটিলতা নিয়ে ওপরের সতর্কবার্তার সাথে সম্পর্কিত।
তারপর দ্বিতীয় ধাপে, আরও ঢিলেঢালা জোরপূর্বক পুনঃযাচাইয়ের পর্যায়ে, validator আবার কল হবে, যা সফল হয়।
এই পরিণতি আরও ভালোভাবে বুঝতে, নিচে দেখুন:

```python
from typing import Any, Generic, Self, TypeVar

from pydantic import BaseModel, model_validator

T = TypeVar('T')


class GenericModel(BaseModel, Generic[T]):
    a: T

    @model_validator(mode='after')
    def validate_after(self: Self) -> Self:
        print('after validator running custom validation...')
        return self


class Model(BaseModel):
    inner: GenericModel[Any]


m = Model.model_validate(Model(inner=GenericModel[int](a=1)))
#> after validator running custom validation...
#> after validator running custom validation...
print(repr(m))
#> Model(inner=GenericModel[Any](a=1))
```

(আউটপুটে "after validator running custom validation..." দুবার ছাপা হয়েছে, এটাই সেই দুই ধাপের প্রমাণ।)

///

### প্যারামিটারহীন টাইপ ভেরিয়েবলের যাচাই { #validation-of-unparametrized-type-variables }

টাইপ ভেরিয়েবল প্যারামিটারহীন রাখলে, Pydantic generic মডেলকে প্রায় সেভাবেই সামলায় যেভাবে [`list`][] আর [`dict`][]-এর মতো বিল্ট-ইন generic
টাইপ সামলায়:

* টাইপ ভেরিয়েবলটি যদি একটি নির্দিষ্ট টাইপে [bound](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds)
  বা [constrained](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints) থাকে,
  তাহলে সেটি ব্যবহার হবে।
* টাইপ ভেরিয়েবলের একটি ডিফল্ট টাইপ থাকলে ([PEP 696](https://peps.python.org/pep-0696/) অনুযায়ী নির্দিষ্ট), সেটি ব্যবহার হবে।
* unbound বা unconstrained টাইপ ভেরিয়েবলের ক্ষেত্রে, Pydantic [`Any`][typing.Any]-এ ফিরে যাবে।

```python
from typing import Generic

from typing_extensions import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar('T')
U = TypeVar('U', bound=int)
V = TypeVar('V', default=str)


class Model(BaseModel, Generic[T, U, V]):
    t: T
    u: U
    v: V


print(Model(t='t', u=1, v='v'))
#> t='t' u=1 v='v'

try:
    Model(t='t', u='u', v=1)
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for Model
    u
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='u', input_type=str]
    v
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
    """
```

(এখানে `T` সীমাহীন তাই `Any`, `U` `int`-এ bound তাই `'u'` এরর দেয়, আর `V`-এর ডিফল্ট `str` তাই `1` এরর দেয়।)

/// warning | সতর্কতা

কিছু ক্ষেত্রে, প্যারামিটারহীন generic মডেলের বিপরীতে যাচাই করলে ডেটা হারিয়ে যেতে পারে। বিশেষ করে, যদি টাইপ ভেরিয়েবলের upper bound, constraint বা ডিফল্টের একটি সাব-টাইপ ব্যবহার হয় আর মডেলটি স্পষ্টভাবে প্যারামিটারাইজ করা না থাকে, তাহলে ফলস্বরূপ টাইপ দেওয়া টাইপটি **হবে না**:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

ItemT = TypeVar('ItemT', bound='ItemBase')


class ItemBase(BaseModel): ...


class IntItem(ItemBase):
    value: int


class ItemHolder(BaseModel, Generic[ItemT]):
    item: ItemT


loaded_data = {'item': {'value': 1}}


print(ItemHolder(**loaded_data))  # (1)!
#> item=ItemBase()

print(ItemHolder[IntItem](**loaded_data))  # (2)!
#> item=IntItem(value=1)
```

1. generic প্যারামিটারাইজ করা না থাকলে, ইনপুট ডেটা `ItemT`-এর upper bound-এর বিপরীতে যাচাই হয়।
   যেহেতু `ItemBase`-এর কোনো ফিল্ড নেই, তাই `item` ফিল্ডের তথ্য হারিয়ে যায়।
2. এই ক্ষেত্রে, টাইপ ভেরিয়েবলটি স্পষ্টভাবে প্যারামিটারাইজ করা, তাই ইনপুট ডেটা `IntItem` ক্লাসের বিপরীতে যাচাই হয়।

///

### প্যারামিটারহীন টাইপ ভেরিয়েবলের সিরিয়ালাইজেশন { #serialization-of-unparametrized-type-variables }

[upper bound](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds), [constraint](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints) বা একটি ডিফল্ট মানসহ টাইপ ভেরিয়েবল ব্যবহার করলে সিরিয়ালাইজেশনের আচরণ ভিন্ন হয়:

যদি একটি টাইপ ভেরিয়েবলের upper bound-এ একটি Pydantic মডেল ব্যবহার হয় আর টাইপ ভেরিয়েবলটি কখনো প্যারামিটারাইজ না করা হয়, তাহলে Pydantic যাচাইয়ের জন্য upper bound ব্যবহার করবে, কিন্তু সিরিয়ালাইজেশনের ক্ষেত্রে মানটিকে [`Any`][typing.Any] হিসেবে ধরবে:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel


class ErrorDetails(BaseModel):
    foo: str


ErrorDataT = TypeVar('ErrorDataT', bound=ErrorDetails)


class Error(BaseModel, Generic[ErrorDataT]):
    message: str
    details: ErrorDataT


class MyErrorDetails(ErrorDetails):
    bar: str


# serialized as Any
error = Error(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='var2'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
        'bar': 'var2',
    },
}

# serialized using the concrete parametrization
# note that `'bar': 'var2'` is missing
error = Error[ErrorDetails](
    message='We just had an error',
    details=ErrorDetails(foo='var'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
    },
}
```

ওপরের আচরণের আরেকটি উদাহরণ, bound নির্দিষ্ট করা আর generic টাইপ প্যারামিটারাইজ করার সব সম্ভাব্য সমন্বয় দেখিয়ে:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TBound = TypeVar('TBound', bound=BaseModel)
TNoBound = TypeVar('TNoBound')


class IntValue(BaseModel):
    value: int


class ItemBound(BaseModel, Generic[TBound]):
    item: TBound


class ItemNoBound(BaseModel, Generic[TNoBound]):
    item: TNoBound


item_bound_inferred = ItemBound(item=IntValue(value=3))
item_bound_explicit = ItemBound[IntValue](item=IntValue(value=3))
item_no_bound_inferred = ItemNoBound(item=IntValue(value=3))
item_no_bound_explicit = ItemNoBound[IntValue](item=IntValue(value=3))

# calling `print(x.model_dump())` on any of the above instances results in the following:
#> {'item': {'value': 3}}
```

তবে যদি [constraint](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints)
বা একটি ডিফল্ট মান ([PEP 696](https://peps.python.org/pep-0696/) অনুযায়ী) ব্যবহার হয়, তাহলে টাইপ ভেরিয়েবল প্যারামিটারাইজ না করা থাকলে
যাচাই আর সিরিয়ালাইজেশন দুটোর জন্যই ডিফল্ট টাইপ বা constraint ব্যবহার হবে। এই আচরণ
[`SerializeAsAny`](./serialization.md#serializeasany-annotation) দিয়ে ওভাররাইড করতে পারেন:

```python
from typing import Generic

from typing_extensions import TypeVar

from pydantic import BaseModel, SerializeAsAny


class ErrorDetails(BaseModel):
    foo: str


ErrorDataT = TypeVar('ErrorDataT', default=ErrorDetails)


class Error(BaseModel, Generic[ErrorDataT]):
    message: str
    details: ErrorDataT


class MyErrorDetails(ErrorDetails):
    bar: str


# serialized using the default's serializer
error = Error(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='var2'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
    },
}
# If `ErrorDataT` was using an upper bound, `bar` would be present in `details`.


class SerializeAsAnyError(BaseModel, Generic[ErrorDataT]):
    message: str
    details: SerializeAsAny[ErrorDataT]


# serialized as Any
error = SerializeAsAnyError(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='baz'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
        'bar': 'baz',
    },
}
```

## ডায়নামিক মডেল তৈরি { #dynamic-model-creation }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.main.create_model`][pydantic.main.create_model]<br>

///

কিছু ক্ষেত্রে, প্রোগ্রাম চলার সময় পাওয়া তথ্য দিয়ে ফিল্ড নির্দিষ্ট করে একটি মডেল তৈরি করা দরকার হয় (যেমন একটি কনফিগ ফাইল বা ডেটাবেসের কলাম দেখে)।
মডেল ডায়নামিকভাবে তৈরি করতে Pydantic [`create_model()`][pydantic.create_model] ফাংশন দেয়:

```python
from pydantic import BaseModel, create_model

DynamicFoobarModel = create_model('DynamicFoobarModel', foo=str, bar=(int, 123))

# Equivalent to:


class StaticFoobarModel(BaseModel):
    foo: str
    bar: int = 123
```

ফিল্ডের সংজ্ঞাগুলো keyword argument হিসেবে দেওয়া হয়, আর এগুলো হবে হয়:

* একটি একক উপাদান, যা ফিল্ডের টাইপ অ্যানোটেশন বোঝায়।
* একটি দুই-উপাদানের tuple, যার প্রথম উপাদান টাইপ আর দ্বিতীয়টি বসানো মান
  (হয় একটি ডিফল্ট, নয়তো [`Field()`][pydantic.Field] ফাংশন)।

/// info | v2.11-এ পরিবর্তিত হয়েছে
ফিল্ডের সংজ্ঞায় একটি একক উপাদান দিলে, যেকোনো টাইপ ব্যবহার করা যায়
(আগে শুধু একটি [`Annotated`][typing.Annotated] রূপ দেওয়া যেত)।
///

একটি আরও অ্যাডভান্সড উদাহরণ:

```python
from typing import Annotated

from pydantic import BaseModel, Field, PrivateAttr, create_model

DynamicModel = create_model(
    'DynamicModel',
    foo=(str, Field(alias='FOO')),
    bar=Annotated[str, Field(description='Bar field')],
    _private=(int, PrivateAttr(default=1)),
)


class StaticModel(BaseModel):
    foo: str = Field(alias='FOO')
    bar: Annotated[str, Field(description='Bar field')]
    _private: int = PrivateAttr(default=1)
```

নতুন মডেল নিজের মতো করতে বিশেষ keyword argument `__config__` আর `__base__` ব্যবহার করা যায়।
এর মধ্যে একটি বেস মডেলকে বাড়তি ফিল্ড দিয়ে বাড়ানোও আছে।

```python
from pydantic import BaseModel, create_model


class FooModel(BaseModel):
    foo: str
    bar: int = 123


BarModel = create_model(
    'BarModel',
    apple=(str, 'russet'),
    banana=(str, 'yellow'),
    __base__=FooModel,
)
print(BarModel)
#> <class '__main__.BarModel'>
print(BarModel.model_fields.keys())
#> dict_keys(['foo', 'bar', 'apple', 'banana'])
```

(`__base__=FooModel` দেওয়ায় নতুন `BarModel`-এ `FooModel`-এর `foo` আর `bar` ফিল্ডও আছে, সাথে নতুন `apple` আর `banana`।)

[validator](./validators.md), মেথড বা [computed ফিল্ড](./fields.md#the-computed_field-decorator)-এর মতো অ্যাট্রিবিউট
`__namespace__` আর্গুমেন্ট দিয়ে ক্লাসের namespace-এ যোগ করা যায়:

```python
from pydantic import (
    ValidationError,
    computed_field,
    create_model,
    field_validator,
)


def alphanum(cls, v: str) -> str:
    assert v.isalnum(), 'must be alphanumeric'
    return v


def full_name(self) -> str:
    return f'{self.first_name} {self.last_name}'


UserModel = create_model(
    'UserModel',
    first_name=str,
    last_name=str,
    __namespace__={  # (1)!
        'check_alphanum': field_validator('first_name', 'last_name')(alphanum),
        'full_name': computed_field(property(full_name)),
    },
)

user = UserModel(first_name='John', last_name='Doe')
print(user.model_dump())
#> {'first_name': 'John', 'last_name': 'Doe', 'full_name': 'John Doe'}

try:
    UserModel(first_name='J%hn', last_name='Doe')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    first_name
      Assertion failed, must be alphanumeric [type=assertion_error, input_value='J%hn', input_type=str]
    """
```

1. namespace-এর key কোনো ফিল্ডের নামের সাথে মিলতে পারবে না, কারণ
   ভেতরে ভেতরে Pydantic সব সদস্যকে একটি namespace-এ জড়ো করে আর [`types` মডিউলের ইউটিলিটি](https://docs.python.org/3/library/types.html#dynamic-type-creation)
   দিয়ে একটি ক্লাসের স্বাভাবিক তৈরি অনুকরণ করে।

/// info | v2.14-এ যোগ হয়েছে
`__namespace__` আর্গুমেন্ট। `__validators__`-এর মতো নয়, এটি শুধু validator-এ সীমাবদ্ধ নয়, আর ক্লাসের namespace-এ
যেকোনো অ্যাট্রিবিউট (যেমন computed ফিল্ড, property বা মেথড) দিতে ব্যবহার করা যায়।
এখন `__validators__`-এর বদলে `__namespace__` ব্যবহারের পরামর্শ দেওয়া হয়, যা v3-তে deprecated হবে।
///

/// note | নোট

ডায়নামিকভাবে তৈরি একটি মডেল pickle (ফাইলে সংরক্ষণযোগ্য রূপে রূপান্তর) করতে:

* মডেলটি global-ভাবে সংজ্ঞায়িত হতে হবে
* `__module__` আর্গুমেন্ট দিতে হবে

///

/// warning | সতর্কতা

যদি স্ট্রিং রেফারেন্স মূল্যায়ন করতে হয়, তাহলে এই ফাংশন ফিল্ডের অ্যানোটেশনে থাকা যেকোনো কোড চালাতে পারে।

আরও তথ্যের জন্য দেখুন [Security implications of introspecting annotations](https://docs.python.org/3/library/annotationlib.html#annotationlib-security)।

(সহজ কথায়: অবিশ্বস্ত উৎস থেকে আসা টেক্সট দিয়ে কখনো `create_model`-এর টাইপ বানাবেন না।)

///

আরও দেখুন: [ডায়নামিক মডেলের উদাহরণ](../examples/dynamic_models.md), যা অন্য একটি মডেল থেকে একটি ঐচ্ছিক মডেল তৈরির নির্দেশনা দেয়।

## `RootModel` আর কাস্টম root টাইপ { #rootmodel-and-custom-root-types }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.root_model.RootModel`][pydantic.root_model.RootModel]<br>

///

[`pydantic.RootModel`][pydantic.RootModel]-এর সাব-ক্লাস বানিয়ে Pydantic মডেলকে একটি "কাস্টম root টাইপ" দিয়ে সংজ্ঞায়িত করা যায়।

root টাইপ Pydantic সমর্থিত যেকোনো টাইপ হতে পারে, আর এটি `RootModel`-এর generic প্যারামিটার দিয়ে নির্দিষ্ট করা হয়।
root মান মডেলের `__init__` বা [`model_validate`][pydantic.main.BaseModel.model_validate]-এ
প্রথম ও একমাত্র আর্গুমেন্ট হিসেবে দেওয়া যায়।

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ মডেল সবসময় একটি "অবজেক্ট" (`{"name": ..., "age": ...}`)। কিন্তু কখনো পুরো ডেটাটাই একটি তালিকা (`["dog", "cat"]`) বা একটি সাধারণ ডিকশনারি। `RootModel` হলো এমন ডেটার জন্য মডেল: ভেতরের পুরো মানটি থাকে `root` নামে, আর JSON-এ বাড়তি মোড়ক ছাড়াই বের হয়।

///

এটি কীভাবে কাজ করে তার একটি উদাহরণ:

```python
from pydantic import RootModel

Pets = RootModel[list[str]]
PetsByName = RootModel[dict[str, str]]


print(Pets(['dog', 'cat']))
#> root=['dog', 'cat']
print(Pets(['dog', 'cat']).model_dump_json())
#> ["dog","cat"]
print(Pets.model_validate(['dog', 'cat']))
#> root=['dog', 'cat']
print(Pets.model_json_schema())
"""
{'items': {'type': 'string'}, 'title': 'RootModel[list[str]]', 'type': 'array'}
"""

print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}
print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}).model_dump_json())
#> {"Otis":"dog","Milo":"cat"}
print(PetsByName.model_validate({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}
```

প্যারামিটারাইজ করা root মডেলের সাব-ক্লাসও সরাসরি তৈরি করতে পারেন:

```python
from pydantic import RootModel


class Pets(RootModel[list[str]]):
    def describe(self) -> str:
        return f'Pets: {", ".join(self.root)}'


my_pets = Pets.model_validate(['dog', 'cat'])

print(my_pets.describe())
#> Pets: dog, cat
```

## কৃত্রিম অপরিবর্তনীয়তা (Faux immutability) { #faux-immutability }

`model_config['frozen'] = True` দিয়ে মডেলকে অপরিবর্তনীয় (immutable) হিসেবে কনফিগার করা যায়। এটি সেট করলে, ইনস্ট্যান্সের অ্যাট্রিবিউটের মান
বদলানোর চেষ্টা করলে এরর হবে। আরও বিস্তারিত জানতে [API রেফারেন্স][pydantic.config.ConfigDict.frozen] দেখুন।

/// note | নোট

Pydantic V1-এ এই আচরণ পাওয়া যেত config সেটিং `allow_mutation = False` দিয়ে।
এই config ফ্ল্যাগ Pydantic V2-তে deprecated, আর এর জায়গা নিয়েছে `frozen`।

///

/// warning | সতর্কতা

Python-এ অপরিবর্তনীয়তা বাধ্যতামূলক করা হয় না। ডেভেলপাররা চাইলে প্রচলিতভাবে "অপরিবর্তনীয়" বলে বিবেচিত অবজেক্টও
বদলাতে পারেন।

///

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class FooBarModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    a: str
    b: dict


foobar = FooBarModel(a='hello', b={'apple': 'pear'})

try:
    foobar.a = 'different'
except ValidationError as e:
    print(e)
    """
    1 validation error for FooBarModel
    a
      Instance is frozen [type=frozen_instance, input_value='different', input_type=str]
    """

print(foobar.a)
#> hello
print(foobar.b)
#> {'apple': 'pear'}
foobar.b['apple'] = 'grape'
print(foobar.b)
#> {'apple': 'grape'}
```

`a` বদলানোর চেষ্টায় এরর হয়েছে, আর `a` অপরিবর্তিত আছে। তবে dict `b` পরিবর্তনযোগ্য, আর
`foobar`-এর অপরিবর্তনীয়তা `b`-কে বদলানো থেকে আটকায় না।

(এজন্যই একে "কৃত্রিম" বলা হয়: শুধু মডেলের ফিল্ডে নতুন মান বসানো আটকানো হয়, ভেতরের তালিকা বা ডিকশনারির ভেতরে বদল নয়। frozen মডেলের একটি বোনাস হলো এগুলো hashable হয়, তাই set-এ রাখা বা dict-এর key বানানো যায়।)

## Abstract base class { #abstract-base-classes }

Pydantic মডেল Python-এর
[Abstract Base Class](https://docs.python.org/3/library/abc.html) (ABC)-এর সাথে একসাথে ব্যবহার করা যায়।

```python
import abc

from pydantic import BaseModel


class FooBarModel(BaseModel, abc.ABC):
    a: str
    b: int

    @abc.abstractmethod
    def my_abstract_method(self):
        pass
```

(`@abc.abstractmethod` থাকায় `FooBarModel` সরাসরি তৈরি করা যাবে না; এর সাব-ক্লাসকে `my_abstract_method` বাস্তবায়ন করতে হবে।)

## ফিল্ডের ক্রম { #field-ordering }

ফিল্ডের ক্রম মডেলকে নিচের উপায়ে প্রভাবিত করে:

* মডেলের [JSON Schema](json_schema.md)-য় ফিল্ডের ক্রম বজায় থাকে
* [যাচাইয়ের এররে](#error-handling) ফিল্ডের ক্রম বজায় থাকে
* [ডেটা সিরিয়ালাইজ](serialization.md#serializing-data) করার সময় ফিল্ডের ক্রম বজায় থাকে

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int = 2
    c: int = 1
    d: int = 0
    e: float


print(Model.model_fields.keys())
#> dict_keys(['a', 'b', 'c', 'd', 'e'])
m = Model(e=2, a=1)
print(m.model_dump())
#> {'a': 1, 'b': 2, 'c': 1, 'd': 0, 'e': 2.0}
try:
    Model(a='x', b='x', c='x', d='x', e='x')
except ValidationError as err:
    error_locations = [e['loc'] for e in err.errors()]

print(error_locations)
#> [('a',), ('b',), ('c',), ('d',), ('e',)]
```

## স্বয়ংক্রিয়ভাবে বাদ পড়া অ্যাট্রিবিউট { #automatically-excluded-attributes }

### ক্লাস ভেরিয়েবল { #class-variables }

[`ClassVar`][typing.ClassVar] দিয়ে অ্যানোটেট করা অ্যাট্রিবিউটগুলোকে Pydantic সঠিকভাবে ক্লাস ভেরিয়েবল হিসেবে গণ্য করে, আর এগুলো
মডেল ইনস্ট্যান্সের ফিল্ড হবে না:

```python
from typing import ClassVar

from pydantic import BaseModel


class Model(BaseModel):
    x: ClassVar[int] = 1

    y: int = 2


m = Model()
print(m)
#> y=2
print(Model.x)
#> 1
```

(`x` পুরো ক্লাসের জন্য একটি মান, যেমন একটি ধ্রুবক; তাই `print(m)`-এ শুধু `y` দেখা যায়।)

### মডেলের private অ্যাট্রিবিউট { #private-model-attributes }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.fields.PrivateAttr`][pydantic.fields.PrivateAttr]<br>

///

যেসব অ্যাট্রিবিউটের নাম underscore (`_`) দিয়ে শুরু, Pydantic সেগুলোকে ফিল্ড হিসেবে গণ্য করে না, আর মডেলের schema-তে
অন্তর্ভুক্ত করে না। বরং এগুলো একটি "private অ্যাট্রিবিউট"-এ রূপান্তরিত হয়, যা `__init__`, `model_validate` ইত্যাদি কলের সময়
যাচাই করা হয় না, এমনকি সেটও করা হয় না।

ব্যবহারের একটি উদাহরণ:

```python
from datetime import datetime
from random import randint
from typing import Any

from pydantic import BaseModel, PrivateAttr


class TimeAwareModel(BaseModel):
    _processed_at: datetime = PrivateAttr(default_factory=datetime.now)
    _secret_value: str

    def model_post_init(self, context: Any) -> None:
        # this could also be done with `default_factory`:
        self._secret_value = randint(1, 5)


m = TimeAwareModel()
print(m._processed_at)
#> 2032-01-02 03:04:05.000006
print(m._secret_value)
#> 3
```

/// info | কোডটি সহজ ভাষায়

`_processed_at` আর `_secret_value` ব্যবহারকারী ইনপুট দিয়ে সেট করতে পারে না, JSON-এ বা `model_dump()`-এ বের হয় না। এগুলো মডেলের ভেতরের হিসাবনিকাশের জন্য, যেমন কখন প্রসেস হলো তার সময়। `PrivateAttr(default_factory=datetime.now)` প্রতিটি নতুন ইনস্ট্যান্সে বর্তমান সময় বসায়।

///

ফিল্ডের সাথে সংঘাত এড়াতে private অ্যাট্রিবিউটের নাম অবশ্যই underscore দিয়ে শুরু হতে হবে। তবে dunder নাম
(যেমন `__attr__`) সমর্থিত নয়, আর মডেলের সংজ্ঞা থেকে পুরোপুরি উপেক্ষা করা হবে।

/// info | v2.13-এ যোগ হয়েছে
default factory যাচাই করা মডেলের ডেটা আর্গুমেন্ট হিসেবে নিতে পারে।
///

## মডেলের signature { #model-signature }

সব Pydantic মডেলের signature তাদের ফিল্ডের ভিত্তিতে তৈরি হয়:

```python
import inspect

from pydantic import BaseModel, Field


class FooModel(BaseModel):
    id: int
    name: str = None
    description: str = 'Foo'
    apple: int = Field(alias='pear')


print(inspect.signature(FooModel))
#> (*, id: int, name: str = None, description: str = 'Foo', pear: int) -> None
```

একটি সঠিক signature introspection (প্রোগ্রাম দিয়ে কোডের গঠন পরীক্ষা) আর `FastAPI` বা `hypothesis`-এর মতো লাইব্রেরির জন্য কাজের।

তৈরি হওয়া signature কাস্টম `__init__` ফাংশনকেও মেনে চলবে:

```python
import inspect

from pydantic import BaseModel


class MyModel(BaseModel):
    id: int
    info: str = 'Foo'

    def __init__(self, id: int = 1, *, bar: str, **data) -> None:
        """My custom init!"""
        super().__init__(id=id, bar=bar, **data)


print(inspect.signature(MyModel))
#> (id: int = 1, *, bar: str, info: str = 'Foo') -> None
```

signature-এ অন্তর্ভুক্ত হতে, একটি ফিল্ডের alias বা নাম একটি বৈধ Python identifier হতে হবে।
signature তৈরির সময় Pydantic ফিল্ডের নামের চেয়ে alias-কে অগ্রাধিকার দেবে, কিন্তু alias একটি বৈধ Python identifier না হলে
ফিল্ডের নাম ব্যবহার করতে পারে।

যদি একটি ফিল্ডের alias আর নাম *দুটোই* বৈধ identifier না হয় (যা `create_model`-এর অদ্ভুত ব্যবহারে সম্ভব হতে পারে),
তাহলে একটি `**data` আর্গুমেন্ট যোগ হবে। তা ছাড়া, `model_config['extra'] == 'allow'` হলে signature-এ সবসময়
`**data` আর্গুমেন্ট থাকবে।

## Structural pattern matching { #structural-pattern-matching }

Python 3.10-এ [PEP 636](https://peps.python.org/pep-0636/) দিয়ে আনা structural pattern matching (`match`/`case`) Pydantic মডেলের জন্য সমর্থিত।

```python
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    species: str


a = Pet(name='Bones', species='dog')

match a:
    # match `species` to 'dog', declare and initialize `dog_name`
    case Pet(species='dog', name=dog_name):
        print(f'{dog_name} is a dog')
#> Bones is a dog
    # default case
    case _:
        print('No dog matched')
```

/// note | নোট

একটি match-case স্টেটমেন্ট দেখে মনে হতে পারে এটি একটি নতুন মডেল তৈরি করছে, কিন্তু বিভ্রান্ত হবেন না;
এটি শুধু একটি অ্যাট্রিবিউট নিয়ে তুলনা করা, অথবা ঘোষণা করে মান বসানোর একটি সংক্ষিপ্ত লেখার রূপ (syntactic sugar)।

///

## অ্যাট্রিবিউটের কপি { #attribute-copies }

অনেক ক্ষেত্রে, যাচাই আর প্রয়োজনে রূপান্তর করতে constructor-এ দেওয়া আর্গুমেন্টগুলো কপি করা হবে।

এই উদাহরণে লক্ষ্য করুন, ক্লাস তৈরির পরে তালিকার ID বদলে যায়, কারণ যাচাইয়ের সময়
এটি কপি করা হয়েছে:

```python
from pydantic import BaseModel


class C1:
    arr = []

    def __init__(self, in_arr):
        self.arr = in_arr


class C2(BaseModel):
    arr: list[int]


arr_orig = [1, 9, 10, 3]


c1 = C1(arr_orig)
c2 = C2(arr=arr_orig)
print(f'{id(c1.arr) == id(c2.arr)=}')
#> id(c1.arr) == id(c2.arr)=False
```

(সাধারণ ক্লাস `C1` মূল তালিকাটিই রাখে, কিন্তু Pydantic মডেল `C2` একটি নতুন কপি রাখে। তাই পরে মূল `arr_orig` বদলালে `c2.arr` বদলাবে না।)

/// note | নোট

কিছু পরিস্থিতিতে Pydantic অ্যাট্রিবিউট কপি করে না, যেমন মডেল দেওয়ার সময় &mdash; আমরা মডেলটি
যেমন আছে তেমনই ব্যবহার করি। এই আচরণ ওভাররাইড করতে পারেন
[`model_config['revalidate_instances'] = 'always'`](../api/config.md#pydantic.config.ConfigDict.revalidate_instances) সেট করে।

///

/// check | সংক্ষেপে মনে রাখুন

* `class X(BaseModel)` + টাইপসহ ফিল্ড = মডেল; ইনস্ট্যান্স তৈরির সময়েই যাচাই হয়।
* ইনপুট: `X(...)`, `model_validate()`, `model_validate_json()`, `model_validate_strings()`; আউটপুট: `model_dump()`, `model_dump_json()`।
* বাড়তি ডেটা: `extra='ignore' | 'forbid' | 'allow'`; ORM অবজেক্ট পড়তে `from_attributes=True`।
* পুনরায় ব্যবহারযোগ্য ছাঁচের জন্য generic মডেল, তালিকা/সাধারণ মানের জন্য `RootModel`, অপরিবর্তনীয় মডেলের জন্য `frozen=True`।
* `_` দিয়ে শুরু হওয়া নাম private অ্যাট্রিবিউট, `ClassVar` ক্লাস ভেরিয়েবল; কোনোটিই ফিল্ড নয়।

///
