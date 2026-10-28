# JSON { #json }

/// note | এই পেজে যা শিখবেন

* Pydantic-এর নিজস্ব দ্রুত JSON পার্সার, আর JSON থেকে সরাসরি যাচাই করার সুবিধা।
* অসম্পূর্ণ (partial) JSON পার্স করা, যা AI মডেলের stream করা উত্তর পড়তে খুব কাজের।
* স্ট্রিং cache করে গতি বাড়ানো।

///

## JSON পার্স করা { #json-parsing }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.main.BaseModel.model_validate_json`][pydantic.main.BaseModel.model_validate_json]
[`pydantic.type_adapter.TypeAdapter.validate_json`][pydantic.type_adapter.TypeAdapter.validate_json]
[`pydantic_core.from_json`][pydantic_core.from_json]

///

Pydantic-এ বিল্ট-ইন JSON পার্সিং আছে, যা সাহায্য করে:

* তৃতীয় পক্ষের লাইব্রেরি ব্যবহারের খরচ ছাড়াই উল্লেখযোগ্য পারফরম্যান্স উন্নতিতে
* কাস্টম এররের সমর্থনে
* `strict` স্পেসিফিকেশনের সমর্থনে

(পার্স করা মানে JSON টেক্সট পড়ে Python ডেটায় রূপান্তর করা, যেমন `'{"a": 1}'` → `{'a': 1}`।)

[`model_validate_json`][pydantic.main.BaseModel.model_validate_json] মেথডের মাধ্যমে Pydantic-এর বিল্ট-ইন JSON পার্সিংয়ের একটি উদাহরণ, যেখানে মডেলের টাইপ অ্যানোটেশনের সাথে মেলে না এমন JSON ডেটা পার্স করার সময় `strict` স্পেসিফিকেশনের সমর্থন দেখানো হয়েছে:

```python
from datetime import date

from pydantic import BaseModel, ConfigDict, ValidationError


class Event(BaseModel):
    model_config = ConfigDict(strict=True)

    when: date
    where: tuple[int, int]


json_data = '{"when": "1987-01-28", "where": [51, -1]}'
print(Event.model_validate_json(json_data))  # (1)!
#> when=datetime.date(1987, 1, 28) where=(51, -1)

try:
    Event.model_validate({'when': '1987-01-28', 'where': [51, -1]})  # (2)!
except ValidationError as e:
    print(e)
    """
    2 validation errors for Event
    when
      Input should be a valid date [type=date_type, input_value='1987-01-28', input_type=str]
    where
      Input should be a valid tuple [type=tuple_type, input_value=[51, -1], input_type=list]
    """
```

1. JSON-এ কোনো `date` বা tuple টাইপ নেই, কিন্তু Pydantic তা জানে, তাই সরাসরি JSON পার্স করার সময় যথাক্রমে স্ট্রিং আর array ইনপুট হিসেবে গ্রহণ করে।
2. একই মান যদি [`model_validate`][pydantic.main.BaseModel.model_validate] মেথডে দেন, তাহলে Pydantic একটি যাচাই এরর দেবে, কারণ `strict` configuration চালু আছে।

/// tip | উদাহরণ দিয়ে বুঝি

JSON-এ তারিখ লেখার একমাত্র উপায় স্ট্রিং, আর tuple লেখার উপায় array। তাই strict মোডেও JSON থেকে পড়ার সময় Pydantic এগুলো মেনে নেয়: ভাষার সীমাবদ্ধতা বোঝে। কিন্তু Python থেকে সরাসরি দিলে আপনি তো আসল `date` বা `tuple` দিতেই পারতেন, তাই সেখানে strict মোড স্ট্রিং বা list গ্রহণ করে না।

///

v2.5.0 আর তার পরের সংস্করণে, JSON ডেটা পার্স করতে Pydantic [`jiter`](https://docs.rs/jiter/latest/jiter/) ব্যবহার করে, যা একটি দ্রুত আর ধাপে ধাপে পড়তে পারে (iterable) এমন JSON পার্সার।
`serde`-এর তুলনায় `jiter` ব্যবহারে পারফরম্যান্সে পরিমিত উন্নতি হয়, যা ভবিষ্যতে আরও ভালো হবে।

`jiter` JSON পার্সার `serde` JSON পার্সারের সাথে প্রায় পুরোপুরি সামঞ্জস্যপূর্ণ,
একটি লক্ষণীয় উন্নতি হলো `jiter` `inf` আর `NaN` মান deserialize করা সমর্থন করে।
ভবিষ্যতে, `jiter`-এর উদ্দেশ্য হলো যাচাইয়ের এররে মূল JSON ইনপুটের সেই অবস্থান
অন্তর্ভুক্ত করা, যেখানে অবৈধ মানটি ছিল।

### আংশিক (Partial) JSON পার্স করা { #partial-json-parsing }

/// info | v2.7-এ যোগ হয়েছে
///

Pydantic-এর [JSON পার্সার](https://docs.rs/jiter/latest/jiter/) আংশিক JSON পার্স করা সমর্থন করে, যা [`pydantic_core.from_json()`][pydantic_core.from_json]-এর মাধ্যমে পাওয়া যায়।
এই ফিচার কাজ করার একটি উদাহরণ:

```python
from pydantic_core import from_json

partial_json_data = '["aa", "bb", "c'  # (1)!

try:
    result = from_json(partial_json_data, allow_partial=False)
except ValueError as e:
    print(e)  # (2)!
    #> EOF while parsing a string at line 1 column 15

result = from_json(partial_json_data, allow_partial=True)
print(result)  # (3)!
#> ['aa', 'bb']
```

1. JSON তালিকাটি অসম্পূর্ণ - এর শেষের `"]` নেই
2. `allow_partial` যখন `False` (ডিফল্ট), তখন একটি পার্সিং এরর হয়।
3. `allow_partial` যখন `True`, তখন ইনপুটের একটি অংশ সফলভাবে deserialize হয় (অসম্পূর্ণ `"c` বাদ পড়ে)।

এটি আংশিক ডিকশনারি deserialize করার ক্ষেত্রেও কাজ করে। যেমন:

```python
from pydantic_core import from_json

partial_dog_json = '{"breed": "lab", "name": "fluffy", "friends": ["buddy", "spot", "rufus"], "age'
dog_dict = from_json(partial_dog_json, allow_partial=True)
print(dog_dict)
#> {'breed': 'lab', 'name': 'fluffy', 'friends': ['buddy', 'spot', 'rufus']}
```

(শেষের অসম্পূর্ণ `"age` key বাদ পড়েছে, বাকি সম্পূর্ণ অংশ পাওয়া গেছে।)

/// tip | LLM-এর আউটপুট যাচাই

এই ফিচার বিশেষ করে LLM (ChatGPT-এর মতো বড় ভাষা মডেল)-এর আউটপুট যাচাইয়ে উপকারী। AI মডেল উত্তর অক্ষরে অক্ষরে stream করে পাঠায়, তাই মাঝপথে JSON অসম্পূর্ণ থাকে; আংশিক পার্সিং দিয়ে যতটুকু এসেছে ততটুকুই দেখানো যায়। তবে, এমনকি যত্ন করে প্রম্পট দেওয়া
মডেলও কখনো কখনো যাচাইয়ে ব্যর্থ হওয়া আউটপুট দেয়। যদি প্রোডাকশনে LLM আউটপুট যাচাই করেন,
[Logfire](../integrations/logfire.md) শুধু ব্যর্থতাগুলো রেকর্ড করতে পারে, যাতে দেখতে পান কোন তৈরি হওয়া উত্তর
আপনার schema-র সাথে মেলেনি, আর কেন।

///

Pydantic-এর ভবিষ্যৎ সংস্করণে, আমরা এই ফিচারের সমর্থন Pydantic-এর অন্যান্য JSON যাচাইয়ের ফাংশন
([`pydantic.main.BaseModel.model_validate_json`][pydantic.main.BaseModel.model_validate_json] আর
[`pydantic.type_adapter.TypeAdapter.validate_json`][pydantic.type_adapter.TypeAdapter.validate_json]) বা মডেল configuration-এর মাধ্যমে বাড়ানোর আশা করছি। সাথে থাকুন 🚀!

আপাতত, একই ফল পেতে [`pydantic_core.from_json`][pydantic_core.from_json]-কে [`pydantic.main.BaseModel.model_validate`][pydantic.main.BaseModel.model_validate]-এর সাথে মিলিয়ে ব্যবহার করতে পারেন। একটি উদাহরণ:

```python
from pydantic_core import from_json

from pydantic import BaseModel


class Dog(BaseModel):
    breed: str
    name: str
    friends: list


partial_dog_json = '{"breed": "lab", "name": "fluffy", "friends": ["buddy", "spot", "rufus"], "age'
dog = Dog.model_validate(from_json(partial_dog_json, allow_partial=True))
print(repr(dog))
#> Dog(breed='lab', name='fluffy', friends=['buddy', 'spot', 'rufus'])
```

/// tip | পরামর্শ

আংশিক JSON পার্সিং নির্ভরযোগ্যভাবে কাজ করাতে, মডেলের সব ফিল্ডের ডিফল্ট মান থাকা উচিত।

///

আংশিক JSON পার্সিংয়ের সাথে ডিফল্ট মান কীভাবে ব্যবহার করবেন তা আরও গভীরভাবে দেখতে নিচের উদাহরণটি দেখুন:

/// tip | আংশিক JSON পার্সিংয়ের সাথে ডিফল্ট মান ব্যবহার

```python
from typing import Annotated, Any

import pydantic_core

from pydantic import BaseModel, ValidationError, WrapValidator


def default_on_error(v, handler) -> Any:
    """
    Raise a PydanticUseDefault exception if the value is missing.

    This is useful for avoiding errors from partial
    JSON preventing successful validation.
    """
    try:
        return handler(v)
    except ValidationError as exc:
        # there might be other types of errors resulting from partial JSON parsing
        # that you allow here, feel free to customize as needed
        if all(e['type'] == 'missing' for e in exc.errors()):
            raise pydantic_core.PydanticUseDefault()
        else:
            raise


class NestedModel(BaseModel):
    x: int
    y: str


class MyModel(BaseModel):
    foo: str | None = None
    bar: Annotated[tuple[str, int] | None, WrapValidator(default_on_error)] = (
        None
    )
    nested: Annotated[NestedModel | None, WrapValidator(default_on_error)] = (
        None
    )


m = MyModel.model_validate(
    pydantic_core.from_json('{"foo": "x", "bar": ["world",', allow_partial=True)
)
print(repr(m))
#> MyModel(foo='x', bar=None, nested=None)


m = MyModel.model_validate(
    pydantic_core.from_json(
        '{"foo": "x", "bar": ["world", 1], "nested": {"x":', allow_partial=True
    )
)
print(repr(m))
#> MyModel(foo='x', bar=('world', 1), nested=None)
```

///

/// info | কোডটি সহজ ভাষায়

`default_on_error` একটি wrap validator: আগে স্বাভাবিক যাচাই চেষ্টা করে; যদি সব এরর শুধু "missing" (কিছু অংশ এখনো আসেনি) ধরনের হয়, তাহলে `PydanticUseDefault` raise করে Pydantic-কে বলে "এই ফিল্ডে ডিফল্ট মান বসাও"। ফলে অসম্পূর্ণ `bar` বা `nested` এরর না দিয়ে `None` হয়ে যায়, আর ডেটা আসতে থাকলে পরের বার পূর্ণ মান পাওয়া যায়।

///

### স্ট্রিং cache করা { #caching-strings }

**v2.7.0 থেকে**, Pydantic-এর [JSON পার্সার](https://docs.rs/jiter/latest/jiter/) JSON পার্সিং আর যাচাইয়ের সময় Python স্ট্রিং কীভাবে cache (মনে রাখা) হবে তা কনফিগার করার সমর্থন দেয় (যখন Python যাচাইয়ের সময় Rust স্ট্রিং থেকে Python স্ট্রিং তৈরি হয়, যেমন `strip_whitespace=True`-এর পরে)।
`cache_strings` সেটিং [model config][pydantic.config.ConfigDict] আর [`pydantic_core.from_json`][pydantic_core.from_json] দুটোর মাধ্যমেই পাওয়া যায়।

`cache_strings` সেটিং নিচের যেকোনো মান নিতে পারে:

* `True` বা `'all'` (ডিফল্ট): সব স্ট্রিং cache করা
* `'keys'`: শুধু ডিকশনারির key cache করা, এটি **শুধু** তখন প্রযোজ্য যখন [`pydantic_core.from_json`][pydantic_core.from_json]-এর সাথে ব্যবহার হয় বা [`Json`][pydantic.types.Json] দিয়ে JSON পার্স করা হয়
* `False` বা `'none'`: কোনো cache নয়

স্ট্রিং cache করার ফিচার ব্যবহারে পারফরম্যান্স বাড়ে, কিন্তু মেমোরির ব্যবহার সামান্য বাড়ে।

(JSON ডেটায় একই key, যেমন `"name"`, হাজারবার আসে। প্রতিবার নতুন স্ট্রিং না বানিয়ে আগেরটি আবার ব্যবহার করলে সময় বাঁচে।)

/// note | স্ট্রিং cache করার বিবরণ

1. স্ট্রিংগুলো একটি fully associative cache-এ রাখা হয়, যার আকার
[16,384](https://github.com/pydantic/jiter/blob/5bbdcfd22882b7b286416b22f74abd549c7b2fd7/src/py_string_cache.rs#L113)।
2. শুধু `len(string) < 64` এমন স্ট্রিং cache হয়।
3. cache-এ খোঁজার কিছু বাড়তি খরচ আছে, যা স্ট্রিং তৈরি এড়াতে সাধারণত পুষিয়ে যায়।
তবে যদি জানেন যে আপনার ডেটায় খুব কম পুনরাবৃত্ত স্ট্রিং থাকবে, তাহলে `cache_strings=False` দিয়ে এই সেটিং বন্ধ করে হয়তো পারফরম্যান্স বাড়াতে পারবেন।

///

## JSON সিরিয়ালাইজেশন { #json-serialization }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.main.BaseModel.model_dump_json`][pydantic.main.BaseModel.model_dump_json]<br>
[`pydantic.type_adapter.TypeAdapter.dump_json`][pydantic.type_adapter.TypeAdapter.dump_json]<br>
[`pydantic_core.to_json`][pydantic_core.to_json]<br>

///

JSON সিরিয়ালাইজেশন (মডেল থেকে JSON লেখা) নিয়ে আরও তথ্যের জন্য [সিরিয়ালাইজেশনের ধারণা](./serialization.md) পেজ দেখুন।

/// check | সংক্ষেপে মনে রাখুন

* JSON থেকে মডেল বানাতে `model_validate_json()`; এটি `json.loads()` + `model_validate()`-এর চেয়ে দ্রুত আর JSON-এর সীমাবদ্ধতা বোঝে।
* অসম্পূর্ণ JSON পড়তে `pydantic_core.from_json(..., allow_partial=True)`, আর ফিল্ডে ডিফল্ট মান রাখুন।
* `cache_strings` দিয়ে পুনরাবৃত্ত স্ট্রিংয়ের গতি বাড়ানো যায়।

///
