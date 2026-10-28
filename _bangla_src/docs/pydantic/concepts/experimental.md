# পরীক্ষামূলক সুবিধা { #experimental-features }

/// note | এই পেজে যা শিখবেন

* Pydantic-এর নতুন, পরীক্ষামূলক (experimental) সুবিধাগুলো, যা ভবিষ্যতে বদলাতে বা বাদ পড়তে পারে।
* **Pipeline API**: ধাপে ধাপে যাচাই, রূপান্তর আর শর্ত জোড়া লাগানো।
* **আংশিক যাচাই (Partial Validation)**: অসম্পূর্ণ JSON, যেমন LLM-এর stream করা উত্তর, যাচাই করা।
* **callable-এর আর্গুমেন্ট যাচাই**: ফাংশন না ডেকেই তার আর্গুমেন্ট যাচাই।

///

এই অংশে Pydantic-এর নতুন, পরীক্ষামূলক সুবিধাগুলোর ডকুমেন্টেশন পাবেন। এই সুবিধাগুলো বদলাতে বা বাদ পড়তে পারে, আর Pydantic-এর স্থায়ী অংশ করার আগে আমরা মতামত আর পরামর্শ চাইছি।

/// warning | প্রোডাকশনে সাবধান

"পরীক্ষামূলক" মানে পরের সংস্করণে API বদলে যেতে পারে, ফলে Pydantic আপডেট করলে আপনার কোড ভেঙে যেতে পারে। প্রোডাকশন কোডে ব্যবহার করলে Pydantic-এর সংস্করণ নির্দিষ্ট (pin) করে রাখুন।

///

পরীক্ষামূলক সুবিধা নিয়ে আরও তথ্যের জন্য দেখুন আমাদের [সংস্করণ নীতি](../version-policy.md#experimental-features)।

## মতামত { #feedback }

পরীক্ষামূলক সুবিধা নিয়ে মতামত আমরা স্বাগত জানাই! আপনার ভাবনা, অনুরোধ বা পরামর্শ জানাতে অনুগ্রহ করে [Pydantic GitHub repository](https://github.com/pydantic/pydantic/issues/new/choose)-তে একটি issue খুলুন।

বিদ্যমান মতামতগুলো পড়ে সেই issue-গুলোতে আপনার ভাবনা যোগ করতেও আমরা উৎসাহ দিই।

## Pipeline API { #pipeline-api }

Pydantic v2.8.0 একটি পরীক্ষামূলক "pipeline" API চালু করেছে, যা দিয়ে পার্সিং (যাচাই), শর্ত আর রূপান্তর বিদ্যমান API-গুলোর চেয়ে বেশি টাইপ-নিরাপদভাবে জোড়া লাগানো যায়। এই API বদলাতে বা বাদ পড়তে পারে; Pydantic-এর স্থায়ী অংশ করার আগে আমরা মতামত আর পরামর্শ চাইছি।

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.experimental.pipeline`][pydantic.experimental.pipeline]<br>

///

সাধারণভাবে, pipeline API ব্যবহার হয় যাচাইয়ের সময় আসা ডেটার ওপর প্রয়োগের জন্য ধাপের একটি ক্রম সংজ্ঞায়িত করতে। pipeline API বিদ্যমান Pydantic API-র চেয়ে বেশি টাইপ-নিরাপদ আর জোড়া লাগানোর উপযোগী করে তৈরি।

/// tip | উদাহরণ দিয়ে বুঝি

কারখানার কনভেয়ার বেল্টের কথা ভাবুন: কাঁচামাল আসে, প্রথম মেশিন ধোয় (`str_strip()`), দ্বিতীয়টি মাপ দেখে (`gt(0)`), তৃতীয়টি রূপ বদলায় (`transform(...)`)। প্রতিটি `.` দিয়ে একটি করে নতুন মেশিন বেল্টে যোগ হয়, বাম থেকে ডানে ক্রমানুসারে।

///

pipeline-এর প্রতিটি ধাপ হতে পারে:

* একটি যাচাই ধাপ, যা দেওয়া টাইপের ওপর pydantic যাচাই চালায়
* একটি রূপান্তর ধাপ, যা ডেটা বদলায়
* একটি শর্ত ধাপ, যা ডেটা একটি শর্তের বিপরীতে পরীক্ষা করে
* একটি predicate ধাপ, যা ডেটা একটি শর্তের বিপরীতে পরীক্ষা করে আর `False` ফেরত দিলে এরর তোলে

<!-- TODO: add more documentation once we solidify the API during the experimental phase -->

মনে রাখুন, নিচের উদাহরণটি জটিলতার বিনিময়ে সম্পূর্ণ হওয়ার চেষ্টা করেছে: যদি দেখেন টাইপ annotation-এ এত বেশি রূপান্তর লিখছেন, তাহলে হয়তো একটি `UserIn` আর `UserOut` মডেল (নিচের উদাহরণ) বা এমন কিছু বিবেচনা করা উচিত, যেখানে রূপান্তরগুলো সাধারণ, স্বাভাবিক Python কোডে করা হয়।
এই API-গুলো সেই পরিস্থিতির জন্য, যেখানে কোড অনেকটা কমে আর বাড়তি জটিলতা তুলনামূলক কম।

```python
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from pydantic.experimental.pipeline import validate_as


class User(BaseModel):
    name: Annotated[str, validate_as(str).str_lower()]  # (1)!
    age: Annotated[int, validate_as(int).gt(0)]  # (2)!
    username: Annotated[str, validate_as(str).str_pattern(r'[a-z]+')]  # (3)!
    password: Annotated[
        str,
        validate_as(str)
        .transform(str.lower)
        .predicate(lambda x: x != 'password'),  # (4)!
    ]
    favorite_number: Annotated[  # (5)!
        int,
        (validate_as(int) | validate_as(str).str_strip().validate_as(int)).gt(
            0
        ),
    ]
    friends: Annotated[list[User], validate_as(...).len(0, 100)]  # (6)!
    bio: Annotated[
        datetime,
        validate_as(int)
        .transform(lambda x: x / 1_000_000)
        .validate_as(...),  # (7)!
    ]
```

1. একটি স্ট্রিং ছোট হাতের অক্ষরে রূপান্তর।
2. একটি পূর্ণসংখ্যাকে শূন্যের চেয়ে বড় হওয়ার শর্ত দেওয়া।
3. একটি স্ট্রিংকে একটি regex প্যাটার্নের সাথে মেলার শর্ত দেওয়া।
4. নিচু-স্তরের transform, constrain আর predicate মেথডও ব্যবহার করতে পারেন।
5. ধাপ জোড়া লাগাতে `|` বা `&` অপারেটর ব্যবহার করুন (যুক্তির OR বা AND-এর মতো)।
6. প্রথম positional আর্গুমেন্ট হিসেবে `Ellipsis`, `...` দিয়ে `validate_as(...)` ডাকা মানে `validate_as(<ফিল্ডের টাইপ>)`। যেকোনো টাইপ গ্রহণ করতে `validate_as(Any)` ব্যবহার করুন।
7. আগে বা পরে প্রক্রিয়াকরণের জন্য অন্য ধাপের আগে বা পরে `validate_as()` ডাকতে পারেন।

### `BeforeValidator`, `AfterValidator` আর `WrapValidator` থেকে রূপান্তর { #mapping-from-beforevalidator-aftervalidator-and-wrapvalidator }

`validate_as` মেথড `BeforeValidator`, `AfterValidator` আর `WrapValidator` সংজ্ঞায়িত করার আরও টাইপ-নিরাপদ উপায়:

```python
from typing import Annotated

from pydantic.experimental.pipeline import transform, validate_as

# BeforeValidator
Annotated[int, validate_as(str).str_strip().validate_as(...)]  # (1)!
# AfterValidator
Annotated[int, transform(lambda x: x * 2)]  # (2)!
# WrapValidator
Annotated[
    int,
    validate_as(str)
    .str_strip()
    .validate_as(...)
    .transform(lambda x: x * 2),  # (3)!
]
```

1. পূর্ণসংখ্যা হিসেবে পার্স করার আগে স্ট্রিং থেকে ফাঁকা জায়গা বাদ দেওয়া।
2. পার্স করার পরে পূর্ণসংখ্যাকে ২ দিয়ে গুণ।
3. স্ট্রিং থেকে ফাঁকা জায়গা বাদ দিয়ে, পূর্ণসংখ্যা হিসেবে যাচাই করে, তারপর ২ দিয়ে গুণ।

### বিকল্প পদ্ধতি { #alternative-patterns }

পরিস্থিতি অনুযায়ী ব্যবহারের অনেক বিকল্প পদ্ধতি আছে।
উদাহরণ হিসেবে, ওপরে বলা `UserIn` আর `UserOut` পদ্ধতিটি দেখুন:

```python
from __future__ import annotations

from pydantic import BaseModel


class UserIn(BaseModel):
    favorite_number: int | str


class UserOut(BaseModel):
    favorite_number: int


def my_api(user: UserIn) -> UserOut:
    favorite_number = user.favorite_number
    if isinstance(favorite_number, str):
        favorite_number = int(user.favorite_number.strip())

    return UserOut(favorite_number=favorite_number)


assert my_api(UserIn(favorite_number=' 1 ')).favorite_number == 1
```

এই উদাহরণটি সাধারণ, স্বাভাবিক Python কোড ব্যবহার করে, যা ওপরের উদাহরণগুলোর চেয়ে বোঝা, টাইপ-পরীক্ষা ইত্যাদিতে সহজ হতে পারে।
আপনি কোন পদ্ধতি বেছে নেবেন তা আসলে নির্ভর করা উচিত আপনার ব্যবহারের ক্ষেত্রের ওপর।
সঠিক পদ্ধতি বাছতে কোডের দৈর্ঘ্য, পারফরম্যান্স, ব্যবহারকারীকে অর্থপূর্ণ এরর ফেরত দেওয়ার সহজতা ইত্যাদি তুলনা করতে হবে।
শুধু পারা যায় বলেই pipeline API-এর মতো অ্যাডভান্সড পদ্ধতির অপব্যবহার করবেন না।

## আংশিক যাচাই (Partial Validation) { #partial-validation }

/// info | v2.10-এ যোগ হয়েছে
///

আংশিক যাচাই দিয়ে একটি অসম্পূর্ণ JSON স্ট্রিং, বা অসম্পূর্ণ ইনপুট ডেটা প্রকাশ করা একটি Python অবজেক্ট যাচাই করা যায়।

আংশিক যাচাই বিশেষভাবে কাজে লাগে একটি LLM-এর আউটপুট প্রক্রিয়া করার সময়, যেখানে মডেলটি গোছানো উত্তর stream করে (একটু একটু করে পাঠায়), আর আপনি তখনো ডেটা পেতে পেতেই stream যাচাই শুরু করতে চাইতে পারেন (যেমন ব্যবহারকারীকে আংশিক ডেটা দেখাতে)।

/// tip | উদাহরণ দিয়ে বুঝি

চিঠি লেখা চলছে, এখনো শেষ হয়নি: "প্রিয় রহিম, কেমন আছ? আমি ভা"। আংশিক যাচাই পুরো চিঠির জন্য অপেক্ষা না করে যতটুকু সম্পূর্ণ (প্রথম দুটি বাক্য) সেটুকু দেখিয়ে দেয়, আর অর্ধেক লেখা শেষ শব্দটি ("ভা") আপাতত বাদ রাখে।

///

এমন streaming pipeline পরে ডিবাগ করা ঝামেলার হতে পারে। প্রোডাকশনে একটি চালালে,
[Logfire](../integrations/logfire.md) আশেপাশের রিকোয়েস্টের প্রেক্ষাপটে প্রতিটি যাচাই রেকর্ড করতে পারে,
ফলে একটি নির্দিষ্ট stream কীভাবে সামলানো হয়েছিল তা আবার সাজানো সহজ হয়।

/// warning | সতর্কতা

আংশিক যাচাই একটি পরীক্ষামূলক সুবিধা আর Pydantic-এর ভবিষ্যৎ সংস্করণে বদলাতে পারে। বর্তমান ব্যবস্থাকে এখন একটি ধারণার প্রমাণ (proof of concept) হিসেবে ধরা উচিত, আর এর কিছু [সীমাবদ্ধতা](#limitations-of-partial-validation) আছে।

///

`TypeAdapter`-এর তিনটি যাচাই মেথড ব্যবহারের সময় আংশিক যাচাই চালু করা যায়: [`TypeAdapter.validate_json()`][pydantic.TypeAdapter.validate_json], [`TypeAdapter.validate_python()`][pydantic.TypeAdapter.validate_python] আর [`TypeAdapter.validate_strings()`][pydantic.TypeAdapter.validate_strings]। এতে অসম্পূর্ণ JSON পার্স আর যাচাই করা যায়, আবার যেকোনো ফরম্যাটের অসম্পূর্ণ ডেটা পার্স করে তৈরি Python অবজেক্টও যাচাই করা যায়।

আংশিক যাচাই চালু করতে এই মেথডগুলোতে `experimental_allow_partial` ফ্ল্যাগ দেওয়া যায়।
এটি নিচের মানগুলো নিতে পারে (আর ডিফল্টভাবে `False`):

* `False` বা `'off'` - আংশিক যাচাই বন্ধ
* `True` বা `'on'` - আংশিক যাচাই চালু, তবে শেষের অসম্পূর্ণ স্ট্রিং সমর্থন করে না
* `'trailing-strings'` - আংশিক যাচাই চালু আর শেষের অসম্পূর্ণ স্ট্রিংও সমর্থন করে

/// info | `'trailing-strings'` মোড

`'trailing-strings'` মোডে আংশিক JSON-এর শেষে থাকা অসম্পূর্ণ স্ট্রিং আউটপুটে রাখা যায়।
যেমন, নিচের মডেলের বিপরীতে যাচাই করলে:

```python
from typing import TypedDict


class Model(TypedDict):
    a: str
    b: str
```

তাহলে শেষে অসম্পূর্ণ স্ট্রিং থাকা সত্ত্বেও নিচের JSON ইনপুটটি বৈধ ধরা হবে:

```json
'{"a": "hello", "b": "wor'
```

আর যাচাই হবে এভাবে:

```python
{'a': 'hello', 'b': 'wor'}
```

///

`experiment_allow_partial` কাজে:

```python
from typing import Annotated

from annotated_types import MinLen
from typing_extensions import NotRequired, TypedDict

from pydantic import TypeAdapter


class Foobar(TypedDict):  # (1)!
    a: int
    b: NotRequired[float]
    c: NotRequired[Annotated[str, MinLen(5)]]


ta = TypeAdapter(list[Foobar])

v = ta.validate_json('[{"a": 1, "b"', experimental_allow_partial=True)  # (2)!
print(v)
#> [{'a': 1}]

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcd', experimental_allow_partial=True  # (3)!
)
print(v)
#> [{'a': 1, 'b': 1.0}]

v = ta.validate_json(
    '[{"b": 1.0, "c": "abcde"', experimental_allow_partial=True  # (4)!
)
print(v)
#> []

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcde"},{"a": ', experimental_allow_partial=True
)
print(v)
#> [{'a': 1, 'b': 1.0, 'c': 'abcde'}]

v = ta.validate_python([{'a': 1}], experimental_allow_partial=True)  # (5)!
print(v)
#> [{'a': 1}]

v = ta.validate_python(
    [{'a': 1, 'b': 1.0, 'c': 'abcd'}], experimental_allow_partial=True  # (6)!
)
print(v)
#> [{'a': 1, 'b': 1.0}]

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcdefg',
    experimental_allow_partial='trailing-strings',  # (7)!
)
print(v)
#> [{'a': 1, 'b': 1.0, 'c': 'abcdefg'}]
```

1. TypedDict `Foobar`-এর তিনটি ফিল্ড, কিন্তু শুধু `a` বাধ্যতামূলক, অর্থাৎ `b` আর `c` ফিল্ড না থাকলেও `Foobar`-এর একটি বৈধ instance তৈরি হতে পারে।
2. JSON পার্স করার সময়, স্ট্রিংটি যেখানে কাটা পড়েছে সেই পর্যন্ত ইনপুট বৈধ JSON।
3. এক্ষেত্রে ইনপুট কাটা পড়ায় `c`-এর মান (`abcd`) `c` ফিল্ডের ইনপুট হিসেবে অবৈধ, তাই এটি বাদ দেওয়া হয়েছে।
4. `a` ফিল্ড বাধ্যতামূলক, তাই তালিকার একমাত্র আইটেমের যাচাই ব্যর্থ হয় আর সেটি বাদ পড়ে।
5. আংশিক যাচাই Python অবজেক্টেও কাজ করে; এর অর্থ JSON-এর মতোই হওয়ার কথা, তবে অবশ্যই একটি Python অবজেক্ট সত্যিকার অর্থে "অসম্পূর্ণ" হতে পারে না।
6. ওপরেরটির মতোই, তবে একটি Python অবজেক্ট দিয়ে; `c` বাদ পড়েছে কারণ এটি বাধ্যতামূলক নয় আর যাচাইয়ে ব্যর্থ।
7. `trailing-strings` মোডে আংশিক JSON-এর শেষে থাকা অসম্পূর্ণ স্ট্রিং আউটপুটে রাখা যায়; এক্ষেত্রে স্ট্রিংটি যেখানে কাটা পড়েছে সেই পর্যন্ত ইনপুট বৈধ JSON, তাই শেষ স্ট্রিংটি রাখা হয়েছে।

### আংশিক যাচাই কীভাবে কাজ করে { #how-partial-validation-works }

আংশিক যাচাই Pydantic-এর মূলমন্ত্র মেনে চলে: ইনপুট ডেটা আসলে কী ছিল সে বিষয়ে এটি কোনো নিশ্চয়তা দেয় না, কিন্তু নিশ্চয়তা দেয় যে আপনার চাওয়া টাইপের একটি বৈধ instance ফেরত দেবে, নয়তো একটি যাচাই এরর তুলবে।

এটি করতে `experimental_allow_partial` ফ্ল্যাগ দুটি আচরণ চালু করে:

#### 1. আংশিক JSON পার্সিং { #1-partial-json-parsing }

Pydantic-এর ব্যবহৃত [jiter](https://github.com/pydantic/jiter) JSON parser আগে থেকেই আংশিক JSON পার্স সমর্থন করে;
`experimental_allow_partial` শুধু `allow_partial` আর্গুমেন্ট হিসেবে jiter-এ পাঠানো হয়।

/// note | মনে রাখুন

শুধু আংশিক JSON সমর্থনসহ বিশুদ্ধ JSON পার্সিং চাইলে, সরাসরি [`jiter`](https://pypi.org/project/jiter/) Python লাইব্রেরি ব্যবহার করতে পারেন, অথবা [`pydantic_core.from_json`][pydantic_core.from_json] ডাকার সময় `allow_partial` আর্গুমেন্ট দিতে পারেন।

///

#### 2. ইনপুটের শেষ উপাদানের এরর উপেক্ষা { #2-ignore-errors-in-last }

ইনপুট ডেটার শুধু একটি অংশ হাতে থাকায়, প্রায়ই ইনপুট ডেটার শেষ উপাদানে এরর হয়।

যেমন:

* একটি স্ট্রিংয়ে `MinLen(5)` শর্ত থাকলে, ইনপুটের শুধু একটি অংশ দেখলে স্ট্রিংয়ের কিছু অংশ না থাকায় যাচাই ব্যর্থ হতে পারে (যেমন `{"name": "Samuel"}`-এর বদলে `{"name": "Sam`)
* একটি `int` ফিল্ডে `Ge(10)` শর্ত থাকলে, ইনপুটের শুধু একটি অংশ দেখলে সংখ্যাটি খুব ছোট হওয়ায় যাচাই ব্যর্থ হতে পারে (যেমন `10`-এর বদলে `1`)
* একটি `TypedDict` ফিল্ডে ৩টি বাধ্যতামূলক ফিল্ড থাকলে, কিন্তু আংশিক ইনপুটে শুধু দুটি ফিল্ড থাকলে, কিছু ফিল্ড অনুপস্থিত বলে যাচাই ব্যর্থ হবে
* ইত্যাদি ইত্যাদি — এমন আরও অনেক ক্ষেত্র আছে

মূল কথা হলো, কোনো বৈধ ইনপুট ডেটার শুধু একটি অংশ দেখলে, যাচাই এরর প্রায়ই একটি sequence-এর শেষ উপাদানে বা mapping-এর শেষ মানে হতে পারে।

এই এররগুলো যাতে আংশিক যাচাই ভেঙে না দেয়, Pydantic ইনপুট ডেটার শেষ উপাদানের সব এরর উপেক্ষা করবে।

```python title="Errors in last element ignored"
from typing import Annotated

from annotated_types import MinLen

from pydantic import BaseModel, TypeAdapter


class MyModel(BaseModel):
    a: int
    b: Annotated[str, MinLen(5)]


ta = TypeAdapter(list[MyModel])
v = ta.validate_json(
    '[{"a": 1, "b": "12345"}, {"a": 1,',
    experimental_allow_partial=True,
)
print(v)
#> [MyModel(a=1, b='12345')]
```

### আংশিক যাচাইয়ের সীমাবদ্ধতা { #limitations-of-partial-validation }

#### শুধু TypeAdapter { #typeadapter-only }

`experiment_allow_partial` শুধু [`TypeAdapter`][pydantic.TypeAdapter]-এর মেথডে দেওয়া যায়; [`BaseModel`][pydantic.BaseModel]-এর মতো Pydantic-এর অন্য প্রবেশপথে এখনো এটি সমর্থিত নয়।

#### সমর্থিত টাইপ { #types-supported }

এখন শুধু কিছু collection validator আংশিক যাচাই সামলাতে জানে:

* `list`
* `set`
* `frozenset`
* `dict` (যেমন `dict[X, Y]`)
* `TypedDict` — শুধু বাধ্যতামূলক নয় এমন ফিল্ড অনুপস্থিত থাকতে পারে, যেমন [`NotRequired`][typing.NotRequired] বা [`total=False`][typing.TypedDict.__total__] দিয়ে)

অন্য collection validator আছে এমন টাইপের বিপরীতে যাচাইয়ের সময় `experimental_allow_partial` ব্যবহার করা গেলেও, সেই টাইপগুলো "সব বা কিছুই না" পদ্ধতিতে যাচাই হবে, আর আরও নেস্টেড টাইপে আংশিক যাচাই কাজ করবে না।

যেমন [ওপরের](#2-ignore-errors-in-last) উদাহরণে আংশিক যাচাই কাজ করে, যদিও তালিকার দ্বিতীয় আইটেমটি পুরোপুরি বাদ পড়ে, কারণ `BaseModel` (এখনো) আংশিক যাচাই সমর্থন করে না।

কিন্তু নিচের উদাহরণে আংশিক যাচাই একেবারেই কাজ করবে না, কারণ `BaseModel` আংশিক যাচাই সমর্থন করে না বলে এটি `b`-এর list validator-এ `allow_partial` নির্দেশটি পাঠায় না:

```python
from typing import Annotated

from annotated_types import MinLen

from pydantic import BaseModel, TypeAdapter, ValidationError


class MyModel(BaseModel):
    a: int = 1
    b: list[Annotated[str, MinLen(5)]] = []  # (1)!


ta = TypeAdapter(MyModel)
try:
    v = ta.validate_json(
        '{"a": 1, "b": ["12345", "12"', experimental_allow_partial=True
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    b.1
      String should have at least 5 characters [type=string_too_short, input_value='12', input_type=str]
    """
```

1. মডেলের validator `b`-এর list validator-এ `allow_partial` নির্দেশ পাঠায় না, তাই এটি জানে না যে ইনপুটের শেষ উপাদানের এরর উপেক্ষা করতে হবে।

#### কিছু অবৈধ কিন্তু সম্পূর্ণ JSON গ্রহণ হবে { #some-invalid-but-complete-json-will-be-accepted }

[jiter](https://github.com/pydantic/jiter) (Pydantic-এর ব্যবহৃত JSON parser) যেভাবে কাজ করে, তাতে এখন `{"a": 1, "b": "12"}`-এর মতো সম্পূর্ণ JSON আর `{"a": 1, "b": "12`-এর মতো অসম্পূর্ণ JSON-এর মধ্যে পার্থক্য করা সম্ভব নয়।

অর্থাৎ `experimental_allow_partial` ব্যবহারের সময় কিছু অবৈধ JSON Pydantic গ্রহণ করবে, যেমন:

```python
from typing import Annotated

from annotated_types import MinLen
from typing_extensions import TypedDict

from pydantic import TypeAdapter


class Foobar(TypedDict, total=False):
    a: int
    b: Annotated[str, MinLen(5)]


ta = TypeAdapter(Foobar)

v = ta.validate_json(
    '{"a": 1, "b": "12', experimental_allow_partial=True  # (1)!
)
print(v)
#> {'a': 1}

v = ta.validate_json(
    '{"a": 1, "b": "12"}', experimental_allow_partial=True  # (2)!
)
print(v)
#> {'a': 1}
```

1. প্রত্যাশামতোই এটি যাচাই পার হবে, যদিও শেষ ফিল্ডটি বাদ পড়বে কারণ এটি যাচাইয়ে ব্যর্থ।
2. এটিও যাচাই পার হবে, কারণ pydantic-core-এ পাঠানো JSON ডেটার বাইনারি রূপ আগের ক্ষেত্রের থেকে আলাদা করা যায় না।

#### ইনপুটের শেষ ফিল্ডের যেকোনো এরর উপেক্ষা হবে { #any-error-in-the-last-field-of-the-input-will-be-ignored }

[ওপরে](#2-ignore-errors-in-last) যেমন বলা হয়েছে, ইনপুট কাটা পড়ার ফলে অনেক এরর হতে পারে। কাটা পড়ার ফলে হতে পারে এমন এরর আলাদা করে উপেক্ষার চেষ্টা না করে, আংশিক যাচাই মোডে Pydantic ইনপুটের শেষ উপাদানের সব এরর উপেক্ষা করে।

অর্থাৎ এরর যদি ইনপুটের শেষ ফিল্ডে থাকে, তাহলে স্পষ্টভাবে অবৈধ ডেটাও যাচাই পার হবে:

```python
from typing import Annotated

from annotated_types import Ge

from pydantic import TypeAdapter

ta = TypeAdapter(list[Annotated[int, Ge(10)]])
v = ta.validate_python([20, 30, 4], experimental_allow_partial=True)  # (1)!
print(v)
#> [20, 30]

ta = TypeAdapter(list[int])

v = ta.validate_python([1, 2, 'wrong'], experimental_allow_partial=True)  # (2)!
print(v)
#> [1, 2]
```

1. প্রত্যাশামতোই এটি যাচাই পার হবে, কারণ Pydantic (কাটা পড়া) শেষ আইটেমের এরর ঠিকভাবেই উপেক্ষা করে।
2. এটিও যাচাই পার হবে, কারণ শেষ আইটেমের এরর উপেক্ষা করা হয়।

/// warning | সাধারণ ভুল

stream শেষ হয়ে গেলে, অর্থাৎ পুরো ডেটা চলে এলে, `experimental_allow_partial` ছাড়া আরেকবার যাচাই করুন। নইলে শেষ আইটেমের আসল ভুলও চুপচাপ বাদ পড়ে যেতে পারে।

///

## একটি callable-এর আর্গুমেন্টের যাচাই { #validation-of-a-callables-arguments }

একটি callable-এর দেওয়া আর্গুমেন্ট (আর বাড়তি হিসেবে ফেরত টাইপ) যাচাই করতে Pydantic [`@validate_call`][pydantic.validate_call] decorator
দেয়। তবে এটি শুধু decorate করা callable আসলে ডাকার মাধ্যমেই আর্গুমেন্ট দিতে দেয়। কিছু পরিস্থিতিতে, শুধু আর্গুমেন্টগুলো *যাচাই* করতে চাইতে পারেন,
যেমন JSON ডেটার মতো অন্য ডেটা উৎস থেকে লোড করার সময়।

এই কারণে, পরীক্ষামূলক [`generate_arguments_schema()`][pydantic.experimental.arguments_schema.generate_arguments_schema]
ফাংশন দিয়ে একটি core schema তৈরি করা যায়, যা পরে একটি [`SchemaValidator`][pydantic_core.SchemaValidator]-এর সাথে ব্যবহার করা যায়।

```python
from pydantic_core import SchemaValidator

from pydantic.experimental.arguments_schema import generate_arguments_schema


def func(p: bool, *args: str, **kwargs: int) -> None: ...


arguments_schema = generate_arguments_schema(func=func)

val = SchemaValidator(arguments_schema, config={'coerce_numbers_to_str': True})

args, kwargs = val.validate_json(
    '{"p": true, "args": ["arg1", 1], "kwargs": {"extra": 1}}'
)
print(args, kwargs)  # (1)!
#> (True, 'arg1', '1') {'extra': 1}
```

1. যাচাই করা আর্গুমেন্টগুলো ডিকশনারি হিসেবে চাইলে, [`Signature.bind()`][inspect.Signature.bind]
   মেথড ব্যবহার করতে পারেন:

     ```python
     from inspect import signature

     signature(func).bind(*args, **kwargs).arguments
     #> {'p': True, 'args': ('arg1', '1'), 'kwargs': {'extra': 1}}
     ```

/// note | মনে রাখুন

[`@validate_call`][pydantic.validate_call]-এর মতো নয়, এই core schema শুধু দেওয়া আর্গুমেন্টগুলো যাচাই করবে;
মূল callable-টি ডাকা *হবে না*।

///

এছাড়া, একটি callback দিয়ে নির্দিষ্ট প্যারামিটার উপেক্ষা করতে পারেন, যা প্রতিটি প্যারামিটারের জন্য ডাকা হয়:

```python
from typing import Any

from pydantic_core import SchemaValidator

from pydantic.experimental.arguments_schema import generate_arguments_schema


def func(p: bool, *args: str, **kwargs: int) -> None: ...


def skip_first_parameter(index: int, name: str, annotation: Any) -> Any:
    if index == 0:
        return 'skip'


arguments_schema = generate_arguments_schema(
    func=func,
    parameters_callback=skip_first_parameter,
)

val = SchemaValidator(arguments_schema)

args, kwargs = val.validate_json('{"args": ["arg1"], "kwargs": {"extra": 1}}')
print(args, kwargs)
#> ('arg1',) {'extra': 1}
```

/// check | সংক্ষেপে মনে রাখুন

* পরীক্ষামূলক সুবিধা বদলে যেতে পারে; প্রোডাকশনে সংস্করণ pin করুন।
* Pipeline: `validate_as(str).str_strip().validate_as(int).gt(0)` এর মতো ধাপ জোড়া; তবে সাধারণ Python কোড প্রায়ই বেশি পরিষ্কার।
* আংশিক যাচাই: `TypeAdapter(...).validate_json(data, experimental_allow_partial=True)`; শেষ উপাদানের এরর উপেক্ষা হয়।
* ফাংশন না ডেকে আর্গুমেন্ট যাচাই: `generate_arguments_schema()` + `SchemaValidator`।

///
