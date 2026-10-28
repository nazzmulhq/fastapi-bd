# সিরিয়ালাইজেশন { #serialization }

/// note | এই পেজে যা শিখবেন

* মডেলকে ডিকশনারি (`model_dump()`) আর JSON স্ট্রিং (`model_dump_json()`)-এ রূপান্তর করা।
* Python মোড আর JSON মোডের পার্থক্য।
* field serializer আর model serializer দিয়ে আউটপুট নিজের মতো সাজানো (plain আর wrap)।
* সাব-ক্লাস সিরিয়ালাইজ করার নিয়ম, polymorphic আর "as Any" সিরিয়ালাইজেশন।
* `exclude`, `include`, `exclude_none`, `exclude_unset` ইত্যাদি দিয়ে কোন ফিল্ড বাদ যাবে তা ঠিক করা।

///

ফিল্ডের নাম দিয়ে সরাসরি মডেলের অ্যাট্রিবিউট ব্যবহার করা (যেমন `model.foobar`) ছাড়াও, মডেলকে বিভিন্ন উপায়ে রূপান্তর, dump,
সিরিয়ালাইজ আর এক্সপোর্ট করা যায়। সিরিয়ালাইজেশন পুরো মডেলের জন্য, অথবা প্রতিটি ফিল্ড বা প্রতিটি টাইপ ধরে
নিজের মতো করা যায়।

/// tip | উদাহরণ দিয়ে বুঝি

যাচাই (validation) হলো বাইরের ডেটা ভেতরে ঢোকানো: JSON বা ডিকশনারি থেকে মডেল। সিরিয়ালাইজেশন হলো তার উল্টো: মডেল থেকে আবার ডিকশনারি বা JSON বানিয়ে বাইরে পাঠানো। অনেকটা পার্সেল খোলা (যাচাই) আর আবার প্যাক করে পাঠানোর (সিরিয়ালাইজেশন) মতো। FastAPI যখন আপনার `return` করা মডেল JSON রেসপন্স হিসেবে পাঠায়, তখন ভেতরে এই সিরিয়ালাইজেশনই হয়।

///

/// details | Serialize বনাম dump
    type: info

Pydantic "serialize" আর "dump" শব্দ দুটি একে অপরের বদলে ব্যবহার করে। দুটোই বোঝায় একটি মডেলকে
একটি ডিকশনারি বা JSON-এনকোড করা স্ট্রিংয়ে রূপান্তরের প্রক্রিয়া।

Pydantic-এর বাইরে, "serialize" শব্দটি সাধারণত মেমোরির ডেটাকে একটি স্ট্রিং বা bytes-এ রূপান্তর বোঝায়।
তবে Pydantic-এর প্রসঙ্গে, একটি অবজেক্টকে আরও সুগঠিত রূপ &mdash; যেমন একটি Pydantic মডেল, একটি dataclass ইত্যাদি &mdash; থেকে
dict-এর মতো Python-এর বিল্ট-ইন দিয়ে তৈরি কম সুগঠিত রূপে রূপান্তরের সাথে এর খুব ঘনিষ্ঠ সম্পর্ক আছে।

যদিও আমরা মৌলিক টাইপে রূপান্তরের সময় "dump" আর স্ট্রিংয়ে রূপান্তরের সময় "serialize" ব্যবহার করে
এই পরিস্থিতিগুলোর পার্থক্য করতে পারতাম (আর কখনো কখনো করিও), ব্যবহারিক কারণে আমরা প্রায়ই দুই পরিস্থিতি বোঝাতেই "serialize" শব্দটি
ব্যবহার করি, যদিও এটি সবসময় স্ট্রিং বা bytes-এ রূপান্তর বোঝায় না।

///

/// tip | পরামর্শ

সংশ্লিষ্ট serializer অংশে দ্রুত যেতে চান?

<div class="grid cards" markdown>

*   Field serializer

    ---

    * [field *plain* serializer](#field-plain-serializer)
    * [field *wrap* serializer](#field-wrap-serializer)

*   Model serializer

    ---

    * [model *plain* serializer](#model-plain-serializer)
    * [model *wrap* serializer](#model-wrap-serializer)

</div>

///

## ডেটা সিরিয়ালাইজ করা { #serializing-data }

Pydantic মডেল (আর [type adapter](./type_adapter.md) ব্যবহারকারী অন্য যেকোনো টাইপ) *দুটি* মোডে সিরিয়ালাইজ করার সুযোগ দেয়:
[Python](#python-mode) আর [JSON](#json-mode)। Python আউটপুটে JSON-এ সিরিয়ালাইজ করা যায় না এমন ডেটা থাকতে পারে (যদিও এটি
অনুকরণ করা যায়)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#modelmodel_dump}{% endraw %}

### Python মোড { #python-mode }

Python মোড ব্যবহার করলে, Pydantic মডেল (আর মডেলের মতো টাইপ, যেমন [dataclasses][]) (1) (পুনরাবৃত্তভাবে) ডিকশনারিতে রূপান্তরিত হয়। এটি [`model_dump()`][pydantic.BaseModel.model_dump] মেথড দিয়ে করা যায়:
{ .annotate }

1. [root মডেল](./models.md#rootmodel-and-custom-root-types) বাদে, যেখানে root মানটি সরাসরি dump হয়।

```python
from pydantic import BaseModel, Field


class BarModel(BaseModel):
    whatever: tuple[int, ...]


class FooBarModel(BaseModel):
    banana: float | None = 1.1
    foo: str = Field(serialization_alias='foo_alias')
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': (1, 2)})

# returns a dictionary:
print(m.model_dump())
#> {'banana': 3.14, 'foo': 'hello', 'bar': {'whatever': (1, 2)}}

print(m.model_dump(by_alias=True))
#> {'banana': 3.14, 'foo_alias': 'hello', 'bar': {'whatever': (1, 2)}}
```

লক্ষ্য করুন, `whatever`-এর মান tuple হিসেবে dump হয়েছে, যা JSON-এর পরিচিত কোনো টাইপ নয়। JSON-সামঞ্জস্যপূর্ণ টাইপ ব্যবহার নিশ্চিত করতে
`mode` আর্গুমেন্ট `'json'` সেট করা যায়:

```python
print(m.model_dump(mode='json'))
#> {'banana': 3.14, 'foo': 'hello', 'bar': {'whatever': [1, 2]}}
```

/// info | আরও দেখুন

[`TypeAdapter.dump_python()`][pydantic.TypeAdapter.dump_python] মেথড, যা Pydantic মডেল নিয়ে কাজ *না* করার সময় কাজের।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#modelmodel_dump_json}{% endraw %}

### JSON মোড { #json-mode }

Pydantic ডেটাকে সরাসরি একটি JSON-এনকোড করা স্ট্রিংয়ে সিরিয়ালাইজ করার সুযোগ দেয়, Python মানগুলোকে বৈধ JSON ডেটায় রূপান্তরের যথাসাধ্য চেষ্টা করে।
এটি [`model_dump_json()`][pydantic.BaseModel.model_dump_json] মেথড দিয়ে করা যায়:

```python
from datetime import datetime

from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: tuple[int, ...]


class FooBarModel(BaseModel):
    foo: datetime
    bar: BarModel


m = FooBarModel(foo=datetime(2032, 6, 1, 12, 13, 14), bar={'whatever': (1, 2)})

print(m.model_dump_json(indent=2))
"""
{
  "foo": "2032-06-01T12:13:14",
  "bar": {
    "whatever": [
      1,
      2
    ]
  }
}
"""
```

(`datetime` হয়ে গেছে ISO ফরম্যাটের স্ট্রিং, আর tuple হয়ে গেছে JSON array। `indent=2` দিয়ে সুন্দর করে সাজানো আউটপুট পাওয়া যায়।)

স্ট্যান্ডার্ড লাইব্রেরির [`json`][] মডিউলের [সমর্থিত টাইপ][json.JSONEncoder] ছাড়াও, Pydantic বিভিন্ন ধরনের অনেক টাইপ
সমর্থন করে ([তারিখ আর সময়ের টাইপ][datetime], [`UUID`][uuid.UUID] অবজেক্ট, [set][set] ইত্যাদি)। যদি একটি অসমর্থিত টাইপ
ব্যবহার হয় আর তা JSON-এ সিরিয়ালাইজ করা না যায়, তাহলে একটি [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] এক্সেপশন
হয়।

এমন একটি সিরিয়ালাইজেশন এরর প্রায়ই শুধু তখনই দেখা দেয় যখন একটি নির্দিষ্ট অবজেক্ট সিরিয়ালাইজ হওয়ার পর্যায়ে পৌঁছায়
(সাধারণত একটি রেসপন্স তৈরির সময়), তাই প্রোডাকশনে না ঘটা পর্যন্ত এটি চোখ এড়িয়ে যেতে পারে। যেকোনো এক্সেপশনের মতো,
আপনার অ্যাপ্লিকেশন instrument করা থাকলে [Logfire](../integrations/logfire.md) এটি ধরে ফেলে, যে রিকোয়েস্ট এটি ঘটিয়েছে তার প্রসঙ্গসহ,
আর অন্য ঘটনাগুলোর সাথে দলবদ্ধ করে, যাতে বুঝতে পারেন এটি একবারের নাকি বারবার ঘটা সমস্যা।

/// info | আরও দেখুন

[`TypeAdapter.dump_json()`][pydantic.TypeAdapter.dump_json] মেথড, যা Pydantic মডেল নিয়ে কাজ *না* করার সময় কাজের।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#dictmodel-and-iteration}{% endraw %}

## মডেলের ওপর iterate করা { #iterating-over-models }

Pydantic মডেলের ওপর iterate করা (লুপ চালানো) যায়, যা `(field_name, field_value)` জোড়া দেয়। লক্ষ্য করুন, ফিল্ডের মানগুলো
যেমন আছে তেমনই থাকে, তাই সাব-মডেলগুলো ডিকশনারিতে রূপান্তরিত *হবে না*:

```python
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

for name, value in m:
    print(f'{name}: {value}')
    #> banana: 3.14
    #> foo: hello
    #> bar: whatever=123
```

এর মানে, একটি মডেলের ওপর [`dict()`][dict] কল করে মডেলের একটি ডিকশনারি তৈরি করা যায়:

```python
print(dict(m))
#> {'banana': 3.14, 'foo': 'hello', 'bar': BarModel(whatever=123)}
```

/// note | নোট

[root মডেল](models.md#rootmodel-and-custom-root-types) `'root'` key-সহ একটি ডিকশনারিতে রূপান্তরিত *হয়*।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#pickledumpsmodel}{% endraw %}

## Pickle সমর্থন { #pickling-support }

Pydantic মডেল দক্ষভাবে pickle আর unpickle (Python অবজেক্টকে bytes-এ সংরক্ষণ আর আবার ফেরত আনা) সমর্থন করে।

<!-- TODO need to get pickling doctest to work -->
```python
import pickle

from pydantic import BaseModel


class FooBarModel(BaseModel):
    a: str
    b: int


m = FooBarModel(a='hello', b=123)
print(m)
#> a='hello' b=123
data = pickle.dumps(m)
print(data[:20])
#> b'\x80\x04\x95\x95\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main_'
m2 = pickle.loads(data)
print(m2)
#> a='hello' b=123
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#custom-serializers}{% endraw %}

## Serializer { #serializers }

[কাস্টম validator](./validators.md)-এর মতোই, সিরিয়ালাইজেশনের আচরণ আরও নিয়ন্ত্রণ করতে ফিল্ড আর মডেল স্তরে কাস্টম serializer
কাজে লাগাতে পারেন।

/// warning | সতর্কতা

প্রতিটি ফিল্ড/মডেলে *একটিই* serializer সংজ্ঞায়িত করা যায়। একাধিক serializer একসাথে মেলানো সম্ভব নয়
(*plain* আর *wrap* serializer-সহ)।

///

### Field serializer { #field-serializers }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.functional_serializers.PlainSerializer`][pydantic.functional_serializers.PlainSerializer]<br>
[`pydantic.functional_serializers.WrapSerializer`][pydantic.functional_serializers.WrapSerializer]<br>
[`pydantic.functional_serializers.field_serializer`][pydantic.functional_serializers.field_serializer]<br>

///

সবচেয়ে সহজ রূপে, একটি field serializer হলো একটি callable যা সিরিয়ালাইজ করার মানটি আর্গুমেন্ট হিসেবে নেয় আর
**সিরিয়ালাইজ করা মান ফেরত দেয়**।

যদি serializer-এ `return_type` আর্গুমেন্ট দেওয়া হয় (অথবা serializer ফাংশনে একটি রিটার্ন টাইপ অ্যানোটেশন থাকে),
তাহলে তা একটি বাড়তি serializer তৈরিতে ব্যবহার হবে, যাতে সিরিয়ালাইজ করা ফিল্ডের মান এই রিটার্ন টাইপের সাথে মেলে।

**দুই** ধরনের serializer ব্যবহার করা যায়। এগুলো সবই
[Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) দিয়ে, অথবা ইনস্ট্যান্স বা [static মেথডে][staticmethod] প্রয়োগ করা
[`@field_serializer`][pydantic.field_serializer] ডেকোরেটর দিয়ে সংজ্ঞায়িত করা যায়।

* ***Plain* serializer**: একটি ফিল্ড সিরিয়ালাইজ করতে শর্তহীনভাবে কল হয়। Pydantic সমর্থিত টাইপের সিরিয়ালাইজেশনের যুক্তি
  কল হবে *না*। যেকোনো টাইপের যুক্তি নির্দিষ্ট করতেও এমন serializer কাজের।
{% raw %}  {#field-plain-serializer}{% endraw %}

    /// tab | Annotated প্যাটার্ন

    ```python
    from typing import Annotated, Any

    from pydantic import BaseModel, PlainSerializer


    def ser_number(value: Any) -> Any:
        if isinstance(value, int):
            return value * 2
        else:
            return value


    class Model(BaseModel):
        number: Annotated[int, PlainSerializer(ser_number)]


    print(Model(number=4).model_dump())
    #> {'number': 8}
    m = Model(number=1)
    m.number = 'invalid'
    print(m.model_dump())  # (1)!
    #> {'number': 'invalid'}
    ```

    1. সিরিয়ালাইজ করা মান `int` টাইপের সাথে মেলে কিনা Pydantic তা যাচাই *করবে না*।

    ///

    /// tab | ডেকোরেটর

    ```python
    from typing import Any

    from pydantic import BaseModel, field_serializer


    class Model(BaseModel):
        number: int

        @field_serializer('number', mode='plain')  # (1)!
        def ser_number(self, value: Any) -> Any:
            if isinstance(value, int):
                return value * 2
            else:
                return value


    print(Model(number=4).model_dump())
    #> {'number': 8}
    m = Model(number=1)
    m.number = 'invalid'
    print(m.model_dump())  # (2)!
    #> {'number': 'invalid'}
    ```

    1. `'plain'` হলো ডেকোরেটরের ডিফল্ট মোড, আর এটি বাদ দেওয়া যায়।
    2. সিরিয়ালাইজ করা মান `int` টাইপের সাথে মেলে কিনা Pydantic তা যাচাই *করবে না*।

    ///

* ***Wrap* serializer**: সিরিয়ালাইজেশনের আচরণ নিজের মতো করতে আরও নমনীয়তা দেয়। Pydantic-এর সিরিয়ালাইজেশন যুক্তির
  আগে বা পরে কোড চালাতে পারেন।
{% raw %}  {#field-wrap-serializer}{% endraw %}

    এমন serializer-কে একটি **বাধ্যতামূলক** বাড়তি *handler* প্যারামিটারসহ সংজ্ঞায়িত করতে হবে: একটি callable, যা সিরিয়ালাইজ করার মানটি
    আর্গুমেন্ট হিসেবে নেয়। ভেতরে, এই handler মানটির সিরিয়ালাইজেশন Pydantic-কে দিয়ে দেবে। চাইলে handler একেবারে
    কল *না* করতেও পারেন।

    /// tab | Annotated প্যাটার্ন

    ```python
    from typing import Annotated, Any

    from pydantic import BaseModel, SerializerFunctionWrapHandler, WrapSerializer


    def ser_number(value: Any, handler: SerializerFunctionWrapHandler) -> int:
        return handler(value) + 1


    class Model(BaseModel):
        number: Annotated[int, WrapSerializer(ser_number)]


    print(Model(number=4).model_dump())
    #> {'number': 5}
    ```

    ///

    /// tab | ডেকোরেটর

    ```python
    from typing import Any

    from pydantic import BaseModel, SerializerFunctionWrapHandler, field_serializer


    class Model(BaseModel):
        number: int

        @field_serializer('number', mode='wrap')
        def ser_number(
            self, value: Any, handler: SerializerFunctionWrapHandler
        ) -> int:
            return handler(value) + 1


    print(Model(number=4).model_dump())
    #> {'number': 5}
    ```

    ///

/// info | plain আর wrap সহজ ভাষায়

* **plain**: Pydantic-এর নিজের কাজ সম্পূর্ণ বাদ দিয়ে আপনার ফাংশনই পুরো সিদ্ধান্ত নেয় (উদাহরণে সংখ্যা দ্বিগুণ করা: `4` → `8`)।
* **wrap**: আগে `handler(value)` দিয়ে Pydantic-এর স্বাভাবিক সিরিয়ালাইজেশন করিয়ে নেন, তারপর ফলাফলে নিজের পরিবর্তন যোগ করেন (উদাহরণে `+ 1`: `4` → `5`)।

///

<!-- Note: keep this section updated with [the validator one](./validators.md#which-validator-pattern-to-use) -->

#### কোন serializer প্যাটার্ন ব্যবহার করবেন { #which-serializer-pattern-to-use }

দুটি পদ্ধতিতেই একই কাজ করা গেলেও, প্রতিটি প্যাটার্নের আলাদা সুবিধা আছে।

##### Annotated প্যাটার্ন ব্যবহার { #using-the-annotated-pattern }

[Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) ব্যবহারের একটি মূল সুবিধা হলো
serializer পুনরায় ব্যবহারযোগ্য করা:

```python
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer

DoubleNumber = Annotated[int, PlainSerializer(lambda v: v * 2)]


class Model1(BaseModel):
    my_number: DoubleNumber


class Model2(BaseModel):
    other_number: Annotated[DoubleNumber, Field(description='My other number')]


class Model3(BaseModel):
    list_of_even_numbers: list[DoubleNumber]  # (1)!
```

1. [Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) ডকুমেন্টেশনে যেমন বলা হয়েছে,
   অ্যানোটেশনের নির্দিষ্ট অংশের জন্যও serializer ব্যবহার করা যায় (এই ক্ষেত্রে,
   সিরিয়ালাইজেশন তালিকার আইটেমগুলোতে প্রয়োগ হয়, পুরো তালিকায় নয়)।

শুধু ফিল্ডের অ্যানোটেশন দেখেই একটি টাইপে কোন serializer প্রয়োগ হয়েছে তা বোঝাও সহজ।

##### ডেকোরেটর প্যাটার্ন ব্যবহার { #using-the-decorator-pattern }

[`@field_serializer`][pydantic.field_serializer] ডেকোরেটর ব্যবহারের একটি মূল সুবিধা হলো
একই ফাংশন একাধিক ফিল্ডে প্রয়োগ করা:

```python
from pydantic import BaseModel, field_serializer


class Model(BaseModel):
    f1: str
    f2: str

    @field_serializer('f1', 'f2', mode='plain')
    def capitalize(self, value: str) -> str:
        return value.capitalize()
```

ডেকোরেটর ব্যবহার নিয়ে আরও কয়েকটি নোট:

* যদি serializer সব ফিল্ডে প্রয়োগ করতে চান (সাব-ক্লাসে সংজ্ঞায়িতগুলোসহ), তাহলে ফিল্ডের নামের আর্গুমেন্ট হিসেবে
  `'*'` দিতে পারেন।
* ডিফল্টভাবে, ডেকোরেটর নিশ্চিত করবে যে দেওয়া ফিল্ডের নাম(গুলো) মডেলে সংজ্ঞায়িত। যদি ক্লাস তৈরির সময় এই যাচাই
  বন্ধ করতে চান, তাহলে `check_fields` আর্গুমেন্টে `False` দিয়ে তা করতে পারেন।
  এটি কাজের যখন field serializer একটি বেস ক্লাসে সংজ্ঞায়িত, আর ফিল্ডটি সাব-ক্লাসে থাকবে বলে আশা করা হয়।

### Model serializer { #model-serializers }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.functional_serializers.model_serializer`][pydantic.functional_serializers.model_serializer]<br>

///

[`@model_serializer`][pydantic.model_serializer] ডেকোরেটর ব্যবহার করে পুরো মডেলের সিরিয়ালাইজেশনও নিজের মতো করা যায়।

যদি [`@model_serializer`][pydantic.model_serializer] ডেকোরেটরে `return_type` আর্গুমেন্ট দেওয়া হয়
(অথবা serializer ফাংশনে একটি রিটার্ন টাইপ অ্যানোটেশন থাকে), তাহলে তা একটি বাড়তি serializer তৈরিতে ব্যবহার হবে,
যাতে সিরিয়ালাইজ করা মডেলের মান এই রিটার্ন টাইপের সাথে মেলে।

[field serializer](#field-serializers)-এর মতোই, **দুই** ধরনের model serializer ব্যবহার করা যায়:

* ***Plain* serializer**: মডেল সিরিয়ালাইজ করতে শর্তহীনভাবে কল হয়।
{% raw %}  {#model-plain-serializer}{% endraw %}

    ```python
    from pydantic import BaseModel, model_serializer


    class UserModel(BaseModel):
        username: str
        password: str

        @model_serializer(mode='plain')  # (1)!
        def serialize_model(self) -> str:  # (2)!
            return f'{self.username} - {self.password}'


    print(UserModel(username='foo', password='bar').model_dump())
    #> foo - bar
    ```

      1. `'plain'` হলো ডেকোরেটরের ডিফল্ট মোড, আর এটি বাদ দেওয়া যায়।
      2. এমন মান ফেরত দিতে পারেন যা ডিকশনারি *নয়*। তবে লক্ষ্য করুন, এতে টাইপ চেকিংয়ের সমস্যা হতে পারে
         (কারণ [`model_dump()`][pydantic.main.BaseModel.model_dump]-এর রিটার্ন টাইপ হলো
         `dict[str, Any]`)।

* ***Wrap* serializer**: সিরিয়ালাইজেশনের আচরণ নিজের মতো করতে আরও নমনীয়তা দেয়। Pydantic-এর সিরিয়ালাইজেশন যুক্তির
  আগে বা পরে কোড চালাতে পারেন।
{% raw %}  {#model-wrap-serializer}{% endraw %}

    এমন serializer-কে একটি **বাধ্যতামূলক** বাড়তি *handler* প্যারামিটারসহ সংজ্ঞায়িত করতে হবে: একটি callable, যা মডেলের ইনস্ট্যান্স
    আর্গুমেন্ট হিসেবে নেয়। ভেতরে, এই handler মডেলের সিরিয়ালাইজেশন Pydantic-কে দিয়ে দেবে। চাইলে handler একেবারে
    কল *না* করতেও পারেন।

      ```python
      from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer


      class UserModel(BaseModel):
          username: str
          password: str

          @model_serializer(mode='wrap')
          def serialize_model(
              self, handler: SerializerFunctionWrapHandler
          ) -> dict[str, object]:
              serialized = handler(self)
              serialized['fields'] = list(serialized)
              return serialized


      print(UserModel(username='foo', password='bar').model_dump())
      #> {'username': 'foo', 'password': 'bar', 'fields': ['username', 'password']}
      ```

(wrap উদাহরণে স্বাভাবিক ডিকশনারি তৈরির পরে একটি বাড়তি `fields` key যোগ করা হয়েছে, যাতে সব ফিল্ডের নামের তালিকা আছে।)

## সিরিয়ালাইজেশনের তথ্য (info) { #serialization-info }

field আর model দুই serializer callable-ই (সব মোডে) ঐচ্ছিকভাবে একটি বাড়তি `info` আর্গুমেন্ট নিতে পারে,
যা কাজের বাড়তি তথ্য দেয়, যেমন:

* [ব্যবহারকারীর দেওয়া প্রসঙ্গ (context)](#serialization-context)
* বর্তমান সিরিয়ালাইজেশন মোড: হয় `'python'`, নয়তো `'json'` ([`mode`][pydantic.SerializationInfo.mode] প্রপার্টি দেখুন)
* [সিরিয়ালাইজেশন মেথড](#serializing-data) দিয়ে সিরিয়ালাইজেশনের সময় সেট করা বিভিন্ন প্যারামিটার
  (যেমন [`exclude_unset`][pydantic.SerializationInfo.exclude_unset], [`serialize_as_any`][pydantic.SerializationInfo.serialize_as_any])
* [field serializer](#field-serializers) ব্যবহার করলে বর্তমান ফিল্ডের নাম
  ([`field_name`][pydantic.FieldSerializationInfo.field_name] প্রপার্টি দেখুন)।

### সিরিয়ালাইজেশনের প্রসঙ্গ (context) { #serialization-context }

[সিরিয়ালাইজেশন মেথডে](#serializing-data) একটি context অবজেক্ট দিতে পারেন, যা serializer ফাংশনের ভেতরে
[`context`][pydantic.SerializationInfo.context] প্রপার্টি দিয়ে পাওয়া যায়:

```python
from pydantic import BaseModel, FieldSerializationInfo, field_serializer


class Model(BaseModel):
    text: str

    @field_serializer('text', mode='plain')
    @classmethod
    def remove_stopwords(cls, v: str, info: FieldSerializationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v


model = Model(text='This is an example document')
print(model.model_dump())  # no context
#> {'text': 'This is an example document'}
print(model.model_dump(context={'stopwords': ['this', 'is', 'an']}))
#> {'text': 'example document'}
```

(serializer-কে বাইরে থেকে বাড়তি তথ্য দিতে context কাজের: এখানে কোন শব্দগুলো বাদ দিতে হবে তা প্রতিটি কলে আলাদা করে বলে দেওয়া হচ্ছে।)

একইভাবে, [যাচাইয়ের জন্য context ব্যবহার](../concepts/validators.md#validation-context) করতে পারেন।

## সাব-ক্লাস সিরিয়ালাইজ করা { #serializing-subclasses }

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#subclasses-of-standard-types}{% endraw %}

### সমর্থিত টাইপের সাব-ক্লাস { #subclasses-of-supported-types }

সমর্থিত টাইপের সাব-ক্লাসগুলো তাদের প্যারেন্ট ক্লাস অনুযায়ী সিরিয়ালাইজ হয়:

```python
from datetime import date

from pydantic import BaseModel


class MyDate(date):
    @property
    def my_date_format(self) -> str:
        return self.strftime('%d/%m/%Y')


class FooModel(BaseModel):
    date: date


m = FooModel(date=MyDate(2023, 1, 1))
print(m.model_dump_json())
#> {"date":"2023-01-01"}
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#subclass-instances-for-fields-of-basemodel-dataclasses-typeddict}{% endraw %}

### মডেলের মতো টাইপের সাব-ক্লাস { #subclasses-of-model-like-types }

যখন মডেলের মতো ক্লাস (Pydantic মডেল, [dataclass](./dataclasses.md) ইত্যাদি) ফিল্ডের অ্যানোটেশন হিসেবে ব্যবহার করেন,
ডিফল্ট আচরণ হলো ফিল্ডের মানকে এমনভাবে সিরিয়ালাইজ করা যেন এটি অ্যানোটেশনে ব্যবহৃত ক্লাসেরই একটি ইনস্ট্যান্স,
এমনকি যদি এটি একটি সাব-ক্লাস হয়। আরও নির্দিষ্টভাবে, শুধু টাইপ অ্যানোটেশনে ঘোষিত ফিল্ডগুলোই
সিরিয়ালাইজেশনের ফলাফলে থাকবে:

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user: User


user = UserLogin(name='pydantic', password='hunter2')

m = OuterModel(user=user)
print(m)
#> user=UserLogin(name='pydantic', password='hunter2')
print(m.model_dump())  # (1)!
#> {'user': {'name': 'pydantic'}}
```

1. লক্ষ্য করুন: password ফিল্ডটি অন্তর্ভুক্ত নয়

/// warning | মাইগ্রেশন সতর্কতা

এই আচরণ Pydantic V1-এ যেভাবে কাজ করত তা থেকে ভিন্ন, যেখানে মডেলকে পুনরাবৃত্তভাবে ডিকশনারিতে সিরিয়ালাইজ করার সময়
আমরা সবসময় সব (সাব-ক্লাসের) ফিল্ড অন্তর্ভুক্ত করতাম। এই আচরণ পরিবর্তনের পেছনের উদ্দেশ্য হলো সিরিয়ালাইজ করার সময়
ঠিক কোন ফিল্ডগুলো অন্তর্ভুক্ত হতে পারে তা আপনি নিশ্চিতভাবে জানেন, এমনকি যদি অবজেক্ট তৈরির সময় সাব-ক্লাস দেওয়া হয়।
বিশেষ করে, সাব-ক্লাসের ফিল্ড হিসেবে গোপন তথ্যের মতো সংবেদনশীল তথ্য যোগ করার সময় এটি অপ্রত্যাশিত ঘটনা এড়াতে সাহায্য করতে পারে।
পুরনো V1 আচরণ চালু করতে, পরের অংশ দেখুন।

///

/// tip | উদাহরণ দিয়ে বুঝি

`OuterModel`-এর ফিল্ডের টাইপ বলা আছে `User` (শুধু `name`)। আপনি ভেতরে একটি `UserLogin` (যাতে `password`-ও আছে) দিলেও, বাইরে পাঠানোর সময় Pydantic শুধু `User`-এর ফিল্ডগুলোই পাঠায়। এটি একটি নিরাপত্তা বেষ্টনী: ভুল করে পাসওয়ার্ড API রেসপন্সে চলে যাওয়া আটকায়।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#serializing-with-duck-typing}{% endraw %}

### Polymorphic সিরিয়ালাইজেশন { #polymorphic-serialization }

/// info | v2.13-এ যোগ হয়েছে
[serialize as any](#serializing-as-any) আচরণের একটি ভালো বিকল্প হিসেবে polymorphic সিরিয়ালাইজেশন যোগ করা হয়েছে, আর এটি
শুধু Pydantic মডেল আর Pydantic dataclass-এ প্রযোজ্য।
///

Polymorphic সিরিয়ালাইজেশন হলো একটি মডেল (বা [Pydantic dataclass](./dataclasses.md)) ইনস্ট্যান্সকে
টাইপ হিসেবে ব্যবহৃত ক্লাসের schema-র বদলে সেই ইনস্ট্যান্সের নিজের সিরিয়ালাইজেশন schema অনুযায়ী সিরিয়ালাইজ করার আচরণ।
এতে সাব-ক্লাসে সংজ্ঞায়িত সব ডেটা সিরিয়ালাইজ করা payload-এ দেখা যাবে।

এই আচরণ নিচের উপায়ে কনফিগার করা যায়:

* configuration স্তরে: মডেল/dataclass [configuration](./config.md)-এ [`polymorphic_serialization`][pydantic.config.ConfigDict.polymorphic_serialization] সেটিং
  ব্যবহার করুন। configuration-টি সেই ক্লাসে সেট করা উচিত যা polymorphic হবে,
  polymorphic ক্লাসকে নির্দেশ করে এমন ক্লাসে নয়।

* চলমান অবস্থার স্তরে: [সিরিয়ালাইজেশন মেথড](#serializing-data) কল করার সময় `polymorphic_serialization` আর্গুমেন্ট ব্যবহার করুন।
  এটি সব (নেস্টেড) টাইপে প্রযোজ্য হবে, যেকোনো configuration ওভাররাইড করে।

/// note | Duck-typed সিরিয়ালাইজেশন

এই আচরণকে (আর নিচে আলোচিত ["any" সিরিয়ালাইজেশন](#serializing-as-any)-কে) আগে duck-typed সিরিয়ালাইজেশন বলা
হতো। এটি একটি ভুল নাম ছিল; এটি প্রচলিত প্রোগ্রামিং ভাষার অর্থে
[duck typing](https://en.wikipedia.org/wiki/Duck_typing)-এর মতো কাজ করত না।

///

/// warning | সতর্কতা

Polymorphic সিরিয়ালাইজেশন শুধু Pydantic মডেল আর [Pydantic dataclass](./dataclasses.md)-এর জন্য সমর্থিত।
[স্ট্যান্ডার্ড লাইব্রেরির dataclass][dataclasses] ব্যবহার করলে, polymorphic সিরিয়ালাইজেশন সমর্থিত *নয়*,
এমনকি dataclass-টি একটি Pydantic dataclass-এর সাব-ক্লাস হলেও। এটি ভবিষ্যতের কোনো Pydantic রিলিজে ঠিক হতে পারে।

///

নিচের উদাহরণে একটি টাইপ `User` আর এর একটি সাব-ক্লাস `UserLogin` সংজ্ঞায়িত করা হয়েছে। দ্বিতীয় এক জোড়া টাইপ, `PolymorphicUser`
আর `PolymorphicUserLogin`, `polymorphic_serialization` চালু করা সমতুল্য টাইপ হিসেবে সংজ্ঞায়িত।

তারপর আমরা এই প্রতিটি টাইপ সিরিয়ালাইজ করার প্রভাব, আর চলমান অবস্থার
`polymorphic_serialization` সেটিংয়ের সাথে এই config-এর পারস্পরিক ক্রিয়া দেখতে পারি:

```python
from pydantic import BaseModel


class User(BaseModel):  # (1)!
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user: User


outer_model = OuterModel(
    user=UserLogin(name='pydantic', password='password'),
)


print(outer_model.model_dump())  # (2)!
#> {'user': {'name': 'pydantic'}}
print(outer_model.model_dump(polymorphic_serialization=True))  # (3)!
#> {'user': {'name': 'pydantic', 'password': 'password'}}
```

1. চলমান অবস্থার নিচের সেটিংয়ের মতো একই আচরণ পেতে এই মডেলে `polymorphic_serialization` configuration সেট করা হতো।
2. polymorphic সিরিয়ালাইজেশন বন্ধ থাকলে, `user` বেস টাইপ হিসেবে সিরিয়ালাইজ হয়।
3. polymorphic সিরিয়ালাইজেশন চালু থাকলে, `user` আসল চলমান সাব-ক্লাস হিসেবে সিরিয়ালাইজ হয়।

উদাহরণে যেমন দেখা গেল, polymorphic সিরিয়ালাইজেশন চালু থাকলে, `User` মানের বদলে `UserLogin` সাব-ক্লাসের মান দেওয়া হলে
`User.model_dump()` মেথড সেটি মেনে নিয়ে পূর্ণ `UserLogin` টাইপ সিরিয়ালাইজ করবে। এই আচরণ
`polymorphic_serialization` চলমান অবস্থার সেটিং দিয়ে সব জায়গায় ওভাররাইড করা যায়; এই ক্ষেত্রে এটি `False` সেট করলে
`UserLogin` মান ঠিক একটি `User` মানের মতো সিরিয়ালাইজ হয়, সাব-ক্লাসের `password` ফিল্ড উপেক্ষা করে।

## "as Any" সিরিয়ালাইজেশন { #serializing-as-any }

[polymorphic সিরিয়ালাইজেশনের](#polymorphic-serialization) আরও চরম একটি রূপ হলো "any" সিরিয়ালাইজেশন। এই
মোডে, মান কীভাবে সিরিয়ালাইজ হবে তা অনুমান করতে Pydantic কোনো টাইপ অ্যানোটেশন (আরও নির্দিষ্টভাবে, টাইপ থেকে পাওয়া সিরিয়ালাইজেশন schema)
ব্যবহার *করে না*, বরং এর জন্য চলমান অবস্থায় মানের আসল টাইপ পরীক্ষা করে (আর এটি শুধু Pydantic মডেল আর dataclass নয়, *সব* টাইপে প্রযোজ্য)।

এর মানে প্রতিটি মান হুবহু তার চলমান টাইপ আর সেই টাইপ সিরিয়ালাইজ করা সম্পর্কে Pydantic-এর জ্ঞানের ভিত্তিতে সিরিয়ালাইজ হবে।
Pydantic নিচের টাইপগুলো কীভাবে সিরিয়ালাইজ করতে হয় তা অনুমান করতে পারে:

* Python স্ট্যান্ডার্ড লাইব্রেরির অনেক টাইপ (সঠিক সেটটি Pydantic সংস্করণ অনুযায়ী বাড়তে পারে)।
* `__pydantic_serializer__` অ্যাট্রিবিউটসহ টাইপ।
* [সিরিয়ালাইজেশন মেথডে](#serializing-data) আর্গুমেন্ট হিসেবে দেওয়া `fallback` ফাংশন দিয়ে সিরিয়ালাইজ করা যায় এমন যেকোনো টাইপ।

বেশিরভাগ ক্ষেত্রে, এর বদলে আপনি [polymorphic সিরিয়ালাইজেশন](#polymorphic-serialization) আচরণ ব্যবহার করতে চাইবেন।

এই আচরণ ফিল্ড স্তরে আর চলমান অবস্থায়, একটি নির্দিষ্ট সিরিয়ালাইজেশন কলের জন্য কনফিগার করা যায়:

* ফিল্ড স্তরে: [`SerializeAsAny`][pydantic.functional_serializers.SerializeAsAny] অ্যানোটেশন ব্যবহার করুন।
* চলমান অবস্থার স্তরে: [সিরিয়ালাইজেশন মেথড](#serializing-data) কল করার সময় `serialize_as_any` আর্গুমেন্ট ব্যবহার করুন।

এই অপশনগুলো নিচে আরও বিস্তারিত আলোচনা করা হয়েছে।

### `SerializeAsAny` অ্যানোটেশন { #serializeasany-annotation }

যদি duck typing সিরিয়ালাইজেশনের আচরণ চান, তাহলে একটি টাইপে
[`SerializeAsAny`][pydantic.functional_serializers.SerializeAsAny] অ্যানোটেশন
ব্যবহার করে তা করা যায়:

```python
from pydantic import BaseModel, SerializeAsAny


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    as_any: SerializeAsAny[User]
    as_user: User


user = UserLogin(name='pydantic', password='password')

print(OuterModel(as_any=user, as_user=user).model_dump())
"""
{
    'as_any': {'name': 'pydantic', 'password': 'password'},
    'as_user': {'name': 'pydantic'},
}
"""
```

একটি টাইপ `SerializeAsAny[<type>]` হিসেবে অ্যানোটেট করা হলে, যাচাইয়ের আচরণ এমন হবে যেন এটি `<type>` হিসেবে অ্যানোটেট করা,
আর স্ট্যাটিক টাইপ চেকার অ্যানোটেশনটিকে শুধু `<type>` হিসেবেই গণ্য করবে।
সিরিয়ালাইজ করার সময়, ফিল্ডটি এমনভাবে সিরিয়ালাইজ হবে যেন ফিল্ডের টাইপ হিন্ট ছিল [`Any`][typing.Any],
এখান থেকেই নামটি এসেছে।

### `serialize_as_any` চলমান অবস্থার সেটিং { #serialize_as_any-runtime-setting }

duck typed সিরিয়ালাইজেশনের আচরণসহ বা ছাড়া মডেলের ডেটা সিরিয়ালাইজ করতে `serialize_as_any` চলমান অবস্থার সেটিং ব্যবহার করা যায়।
`serialize_as_any` বিভিন্ন [সিরিয়ালাইজেশন মেথডে](#serializing-data) (যেমন Pydantic মডেলের
[`model_dump()`][pydantic.BaseModel.model_dump] আর [`model_dump_json()`][pydantic.BaseModel.model_dump_json]) keyword argument হিসেবে দেওয়া যায়।

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user1: User
    user2: User


user = UserLogin(name='pydantic', password='password')

outer_model = OuterModel(user1=user, user2=user)
print(outer_model.model_dump(serialize_as_any=True))  # (1)!
"""
{
    'user1': {'name': 'pydantic', 'password': 'password'},
    'user2': {'name': 'pydantic', 'password': 'password'},
}
"""

print(outer_model.model_dump(serialize_as_any=False))  # (2)!
#> {'user1': {'name': 'pydantic'}, 'user2': {'name': 'pydantic'}}
```

1. `serialize_as_any` `True` সেট করা থাকলে, ফলাফল V1-এর সাথে মেলে।
2. `serialize_as_any` `False` সেট করা থাকলে (V2-এর ডিফল্ট), সাব-ক্লাসে আছে কিন্তু বেস ক্লাসে নেই এমন ফিল্ড
   সিরিয়ালাইজেশনে অন্তর্ভুক্ত হয় না।

তবে লক্ষ্য করুন, *serialize as any* আচরণ *সব* মানে প্রযোজ্য হবে, শুধু সেই মানগুলোতে নয় যেখানে duck typing
প্রাসঙ্গিক। প্রয়োজন হলে এর বদলে `SerializeAsAny` অ্যানোটেশন ব্যবহার করাই পছন্দ করতে পারেন।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#advanced-include-and-exclude}{% endraw %}
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#model-and-field-level-include-and-exclude}{% endraw %}

## ফিল্ড অন্তর্ভুক্তি আর বাদ দেওয়া { #field-inclusion-and-exclusion }

সিরিয়ালাইজেশনের জন্য, ফিল্ড অন্তর্ভুক্তি আর বাদ দেওয়া দুইভাবে কনফিগার করা যায়:

* ফিল্ড স্তরে, [`Field()` ফাংশনের](fields.md) `exclude` আর `exclude_if` প্যারামিটার ব্যবহার করে।
* [সিরিয়ালাইজেশন মেথডের](#serializing-data) বিভিন্ন সিরিয়ালাইজেশন প্যারামিটার ব্যবহার করে।

### ফিল্ড স্তরে { #at-the-field-level }

ফিল্ড স্তরে, `exclude` আর `exclude_if` প্যারামিটার ব্যবহার করা যায়:

```python
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    id: int
    private_id: int = Field(exclude=True)
    value: int = Field(ge=0, exclude_if=lambda v: v == 0)


print(Transaction(id=1, private_id=2, value=0).model_dump())
#> {'id': 1}
```

(`private_id` সবসময় বাদ, আর `value` বাদ শুধু যখন এর মান `0`।)

ফিল্ড স্তরে বাদ দেওয়া নিচে বর্ণিত `include` সিরিয়ালাইজেশন প্যারামিটারের চেয়ে অগ্রাধিকার পায়।

### সিরিয়ালাইজেশন মেথডের প্যারামিটার হিসেবে { #as-parameters-to-the-serialization-methods }

[সিরিয়ালাইজেশন মেথড](#serializing-data) (যেমন [`model_dump()`][pydantic.BaseModel.model_dump]) ব্যবহারের সময়,
ফিল্ড বাদ দিতে বা অন্তর্ভুক্ত করতে কয়েকটি প্যারামিটার ব্যবহার করা যায়।

#### নির্দিষ্ট ফিল্ড বাদ দেওয়া আর অন্তর্ভুক্ত করা { #excluding-and-including-specific-fields }

নিচের মডেলগুলো বিবেচনা করুন:

```python
from pydantic import BaseModel, Field, SecretStr


class User(BaseModel):
    id: int
    username: str
    password: SecretStr


class Transaction(BaseModel):
    id: str
    private_id: str = Field(exclude=True)
    user: User
    value: int


t = Transaction(
    id='1234567890',
    private_id='123',
    user=User(id=42, username='JohnDoe', password='hashedpassword'),
    value=9876543210,
)
```

কোন ফিল্ডগুলো বাদ যাবে (বাকিগুলো থাকবে) তা নির্দিষ্ট করতে `exclude` প্যারামিটার ব্যবহার করা যায়, আর উল্টোটা করতে
`include` প্যারামিটার।

```python
# using a set:
print(t.model_dump(exclude={'user', 'value'}))
#> {'id': '1234567890'}

# using a dictionary:
print(t.model_dump(exclude={'user': {'username', 'password'}, 'value': True}))
#> {'id': '1234567890', 'user': {'id': 42}}

# same configuration using `include`:
print(t.model_dump(include={'id': True, 'user': {'id'}}))
#> {'id': '1234567890', 'user': {'id': 42}}
```

লক্ষ্য করুন, `exclude`-এ একটি ফিল্ড *অন্তর্ভুক্ত* করতে (বা `include`-এ একটি ফিল্ড *বাদ দিতে*) `False` ব্যবহার সমর্থিত নয়।

sequence আর ডিকশনারি থেকে নির্দিষ্ট আইটেম বাদ দেওয়া বা অন্তর্ভুক্ত করাও সম্ভব:

```python
from pydantic import BaseModel


class Hobby(BaseModel):
    name: str
    info: str


class User(BaseModel):
    hobbies: list[Hobby]


user = User(
    hobbies=[
        Hobby(name='Programming', info='Writing code and stuff'),
        Hobby(name='Gaming', info='Hell Yeah!!!'),
    ],
)

print(user.model_dump(exclude={'hobbies': {-1: {'info'}}}))  # (1)!
"""
{
    'hobbies': [
        {'name': 'Programming', 'info': 'Writing code and stuff'},
        {'name': 'Gaming'},
    ]
}
"""
```

1. `include` দিয়ে সমতুল্য কলটি হতো:

     ```python
     user.model_dump(
        include={'hobbies': {0: True, -1: {'name'}}}
     )
     ```

সব সদস্যে একটি বাদ/অন্তর্ভুক্তির প্যাটার্ন প্রয়োগ করতে বিশেষ key `'__all__'` ব্যবহার করা যায়:

```python
print(user.model_dump(exclude={'hobbies': {'__all__': {'info'}}}))
#> {'hobbies': [{'name': 'Programming'}, {'name': 'Gaming'}]}
```

/// info | exclude/include লেখার নিয়ম সহজ ভাষায়

* `exclude={'user'}`: পুরো `user` ফিল্ড বাদ।
* `exclude={'user': {'password'}}`: `user`-এর ভেতরের শুধু `password` বাদ (নেস্টেড ডিকশনারি দিয়ে গভীরে যাওয়া যায়)।
* তালিকার ক্ষেত্রে ইনডেক্স দিয়ে: `{'hobbies': {-1}}` মানে শেষ উপাদান বাদ।
* `'__all__'`: তালিকা বা ডিকশনারির সব সদস্যে একই নিয়ম।

///

#### মানের ভিত্তিতে ফিল্ড বাদ দেওয়া আর অন্তর্ভুক্ত করা { #excluding-and-including-fields-based-on-their-value }

[সিরিয়ালাইজেশন মেথড](#serializing-data) ব্যবহারের সময়, নিচের প্যারামিটারগুলো দিয়ে ফিল্ডের মানের ভিত্তিতে
সেগুলো বাদ দেওয়া সম্ভব:

* `exclude_defaults`: যেসব ফিল্ডের মান ডিফল্ট মানের সমান (সমতা (`==`) তুলনা অপারেটর দিয়ে) সেগুলো সব বাদ।
* `exclude_none`: যেসব ফিল্ডের মান `None` সেগুলো সব বাদ।
* `exclude_unset`: তৈরির সময় কোন ফিল্ডগুলো *স্পষ্টভাবে* সেট করা হয়েছিল Pydantic তা মনে রাখে
  ([`model_fields_set`][pydantic.BaseModel.model_fields_set] প্রপার্টি দিয়ে)। `exclude_unset` ব্যবহার করলে, যে ফিল্ড
  স্পষ্টভাবে দেওয়া হয়নি তা বাদ যাবে:

    ```python
    from pydantic import BaseModel


    class UserModel(BaseModel):
        name: str
        age: int = 18


    user = UserModel(name='John')
    print(user.model_fields_set)
    #> {'name'}

    print(user.model_dump(exclude_unset=True))
    #> {'name': 'John'}
    ```

    লক্ষ্য করুন, ইনস্ট্যান্স তৈরির *পরে* একটি ফিল্ড বদলালে সেটি unset ফিল্ডের তালিকা থেকে সরে যাবে:

    ```python
    user.age = 21

    print(user.model_dump(exclude_unset=True))
    #> {'name': 'John', 'age': 21}
    ```

    /// tip | পরামর্শ

    `exclude_unset`-এর বিকল্প হিসেবে [`MISSING` sentinel](./types.md#missing-sentinel) ব্যবহার করা যায়।
    `MISSING` মানওয়ালা যেকোনো ফিল্ড স্বয়ংক্রিয়ভাবে সিরিয়ালাইজেশনের আউটপুট থেকে বাদ পড়ে।

    ///

/// tip | কোনটি কখন

* `exclude_none`: JSON-এ `null` ভরা ঘরগুলো বাদ দিয়ে ছোট রেসপন্স চাইলে।
* `exclude_unset`: PATCH রিকোয়েস্টে শুধু ক্লায়েন্ট যা পাঠিয়েছে তা-ই আপডেট করতে (FastAPI-র [বডি আপডেট](../../tutorial/body-updates.md) পেজে ঠিক এটিই ব্যবহার হয়)।
* `exclude_defaults`: ডিফল্ট থেকে যা আলাদা শুধু সেটুকু সংরক্ষণ করতে।

///

/// check | সংক্ষেপে মনে রাখুন

* `model_dump()` → Python ডিকশনারি; `model_dump(mode='json')` → JSON-যোগ্য ডিকশনারি; `model_dump_json()` → JSON স্ট্রিং।
* নিজের মতো আউটপুট: `PlainSerializer`/`WrapSerializer` বা `@field_serializer`; পুরো মডেলের জন্য `@model_serializer`।
* ফিল্ডের টাইপ বেস ক্লাস হলে সাব-ক্লাসের বাড়তি ফিল্ড বাদ যায় (নিরাপত্তার জন্য); সব চাইলে `polymorphic_serialization` বা `SerializeAsAny`।
* বাদ দেওয়া: `Field(exclude=True)`, অথবা `model_dump(exclude=..., include=..., exclude_none=True, exclude_unset=True)`।

///
