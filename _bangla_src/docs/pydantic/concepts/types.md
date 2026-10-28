# টাইপ { #types }

/// note | এই পেজে যা শিখবেন

* Pydantic কীভাবে টাইপ দিয়ে যাচাই আর সিরিয়ালাইজেশন নিয়ন্ত্রণ করে।
* কাজের কিছু বিশেষ টাইপ: `OnErrorOmit`, `FailFast`, `MISSING`।
* `Annotated` দিয়ে নিজের পুনরায় ব্যবহারযোগ্য টাইপ বানানো (যেমন "ধনাত্মক integer")।
* নামযুক্ত type alias আর পুনরাবৃত্ত (recursive) টাইপ।
* অ্যাডভান্সড: `__get_pydantic_core_schema__` দিয়ে সম্পূর্ণ নিজস্ব টাইপ, তৃতীয় পক্ষের টাইপ আর generic ক্লাস সামলানো।

শুরুর দিকে "ইউটিলিটি টাইপ" আর "Annotated প্যাটার্ন" অংশ পড়লেই যথেষ্ট; বাকিটা দরকার হলে পড়ুন।

///

যাচাই আর সিরিয়ালাইজেশন কীভাবে হবে তা নির্ধারণ করতে Pydantic টাইপ ব্যবহার করে।
[বিল্ট-ইন আর স্ট্যান্ডার্ড লাইব্রেরির টাইপ](../api/standard_library_types.md) (যেমন [`int`][],
[`str`][], [`date`][datetime.date]) যেমন আছে তেমনই ব্যবহার করা যায়। এগুলোর ওপর [কঠোরতা](./strict_mode.md)
নিয়ন্ত্রণ করা আর শর্ত প্রয়োগ করা যায়।

এগুলোর ওপরে, Pydantic বাড়তি টাইপ দেয়, হয় [সরাসরি লাইব্রেরিতে](../api/types.md)
(যেমন [`SecretStr`][pydantic.types.SecretStr]), নয়তো [`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types)
বাইরের লাইব্রেরিতে। এগুলো [কাস্টম টাইপ](#custom-types) অংশে বর্ণিত প্যাটার্ন ব্যবহার করে বাস্তবায়িত।
এগুলোর ওপর কঠোরতা আর শর্ত প্রয়োগ *করা যায় না*।

[বিল্ট-ইন আর স্ট্যান্ডার্ড লাইব্রেরির টাইপ](../api/standard_library_types.md) ডকুমেন্টেশন
সমর্থিত টাইপগুলো নিয়ে আলোচনা করে: অনুমোদিত মান, সম্ভাব্য যাচাইয়ের শর্ত, আর [কঠোরতা](./strict_mode.md)
কনফিগার করা যায় কিনা।

প্রতিটি টাইপের অনুমোদিত মানের সারসংক্ষেপের জন্য [রূপান্তর সারণি](../concepts/conversion_table.md)-ও দেখুন।

## ইউটিলিটি টাইপ { #utility-types }

যাচাই/সিরিয়ালাইজেশনের আচরণ নিজের মতো করতে Pydantic কয়েকটি কাজের টাইপ/অ্যানোটেশন দেয়।

### `OnErrorOmit` { #onerroromit }

/// info | v2.6-এ যোগ হয়েছে
///

ডিফল্টভাবে, একটি collection-এর (যেমন একটি list, একটি ডিকশনারি বা একটি [`TypedDict`][typing.TypedDict]) একটি আইটেম
যাচাইয়ে ব্যর্থ হলে, একটি [`ValidationError`][pydantic_core.ValidationError] হয় আর পুরো collection-টি
বাতিল হয়। [`OnErrorOmit`][pydantic.types.OnErrorOmit] অ্যানোটেশন এই আচরণ বদলায়: যাচাইয়ে ব্যর্থ যেকোনো আইটেম
নিঃশব্দে ফলাফল থেকে বাদ পড়ে, আর বৈধগুলো থেকে যায়।

```python
from pydantic import OnErrorOmit, TypeAdapter

ta = TypeAdapter(list[OnErrorOmit[int]])

print(ta.validate_python([1, 2, 'a', 3]))
#> [1, 2, 3]
```

(`'a'` integer নয়, তাই এররের বদলে চুপচাপ বাদ পড়েছে; বাকি `[1, 2, 3]` থেকে গেছে। অগোছালো ডেটা থেকে যতটুকু ভালো তা নিতে চাইলে এটি কাজের।)

এটি কোথায় প্রয়োগ করা যায় তার আরও বিস্তারিত জানতে [API ডকুমেন্টেশন][pydantic.types.OnErrorOmit] দেখুন।

### `FailFast` { #failfast }

/// info | v2.8-এ যোগ হয়েছে
///

ডিফল্টভাবে, একটি collection যাচাই করার সময় Pydantic প্রতিটি আইটেম যাচাই করে আর সব এরর
একসাথে জানায়। [`FailFast`][pydantic.types.FailFast] অ্যানোটেশন একটি collection টাইপে
(যেমন একটি [`list`][], একটি [`tuple`][], একটি [`set`][] বা একটি [`dict`][]) প্রয়োগ করে প্রথম আইটেম ব্যর্থ হওয়া মাত্রই থামানো যায়।
এতে যাচাই দ্রুত হয়, তবে এররগুলো সম্পর্কে কম তথ্য পান।

```python
from typing import Annotated

from pydantic import FailFast, TypeAdapter, ValidationError

ta = TypeAdapter(Annotated[list[int], FailFast()])

try:
    ta.validate_python([1, 'a', 2, 'b'])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[int]
    1
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

(তালিকায় `'a'` আর `'b'` দুটোই ভুল, কিন্তু `FailFast` থাকায় শুধু প্রথম এররটি জানানো হয়েছে।)

### `MISSING` sentinel { #missing-sentinel }

::: pydantic_core.MISSING
    options:
        show_root_heading: false
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true

(`MISSING` হলো একটি বিশেষ চিহ্ন, যা বোঝায় "এই ফিল্ডের মান একেবারেই দেওয়া হয়নি"। এটি `None` থেকে আলাদা: `None` মানে "মান দেওয়া হয়েছে, আর তা খালি"। বিস্তারিত ব্যাখ্যা ওপরের বাক্সে স্বয়ংক্রিয়ভাবে দেখানো হয়েছে।)

## কাস্টম টাইপ { #custom-types }

নিজের কাস্টম টাইপ সংজ্ঞায়িত করার কয়েকটি উপায় আছে।

### Annotated প্যাটার্ন ব্যবহার { #using-the-annotated-pattern }

আপনার কোডবেসজুড়ে টাইপ পুনরায় ব্যবহারযোগ্য করতে [Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) ব্যবহার করা যায়।
যেমন, একটি ধনাত্মক integer বোঝায় এমন একটি টাইপ তৈরি করতে:

```python
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError

PositiveInt = Annotated[int, Field(gt=0)]  # (1)!

ta = TypeAdapter(PositiveInt)

print(ta.validate_python(1))
#> 1

try:
    ta.validate_python(-1)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for constrained-int
      Input should be greater than 0 [type=greater_than, input_value=-1, input_type=int]
    """
```

1. লক্ষ্য করুন, এটিকে Pydantic-নিরপেক্ষ করতে [annotated-types](https://github.com/annotated-types/annotated-types)
  লাইব্রেরির শর্তও ব্যবহার করতে পারেন:

    ```python
    from annotated_types import Gt

    PositiveInt = Annotated[int, Gt(0)]
    ```

/// tip | উদাহরণ দিয়ে বুঝি

`PositiveInt = Annotated[int, Field(gt=0)]` একবার লিখলে, এরপর যেকোনো মডেলে `age: PositiveInt`, `count: PositiveInt` লিখলেই একই নিয়ম প্রয়োগ হয়। অনেকটা একটি রাবার স্ট্যাম্প বানিয়ে রাখার মতো: একবার বানান, যতবার খুশি ছাপ দিন।

///

#### যাচাই আর সিরিয়ালাইজেশন যোগ করা { #adding-validation-and-serialization }

Pydantic যেসব মার্কার দেয় সেগুলো ব্যবহার করে যেকোনো টাইপে যাচাই, সিরিয়ালাইজেশন আর JSON schema যোগ বা ওভাররাইড করতে পারেন:

```python
from typing import Annotated

from pydantic import (
    AfterValidator,
    PlainSerializer,
    TypeAdapter,
    WithJsonSchema,
)

TruncatedFloat = Annotated[
    float,
    AfterValidator(lambda x: round(x, 1)),
    PlainSerializer(lambda x: f'{x:.1e}', return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]


ta = TypeAdapter(TruncatedFloat)

input = 1.02345
assert input != 1.0

assert ta.validate_python(input) == 1.0

assert ta.dump_json(input) == b'"1.0e+00"'

assert ta.json_schema(mode='validation') == {'type': 'number'}
assert ta.json_schema(mode='serialization') == {'type': 'string'}
```

/// info | কোডটি সহজ ভাষায়

`TruncatedFloat` একটি float, তিনটি স্টিকারসহ:

* `AfterValidator(...)`: যাচাইয়ের পরে মানটিকে এক দশমিক ঘরে গোল করে (`1.02345` → `1.0`)।
* `PlainSerializer(...)`: আউটপুটে মানটিকে বৈজ্ঞানিক রূপের স্ট্রিং বানায় (`"1.0e+00"`)।
* `WithJsonSchema(...)`: সিরিয়ালাইজেশন মোডের JSON schema-তে টাইপ `string` বলে দেয়, কারণ আউটপুট এখন স্ট্রিং।

///

#### Generic { #generics }

[`Annotated`][typing.Annotated] টাইপের ভেতরে [টাইপ ভেরিয়েবল][typing.TypeVar] ব্যবহার করা যায়:

```python
from typing import Annotated, TypeVar

from annotated_types import Gt, Len

from pydantic import TypeAdapter, ValidationError

T = TypeVar('T')


ShortList = Annotated[list[T], Len(max_length=4)]


ta = TypeAdapter(ShortList[int])

v = ta.validate_python([1, 2, 3, 4])
assert v == [1, 2, 3, 4]

try:
    ta.validate_python([1, 2, 3, 4, 5])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[int]
      List should have at most 4 items after validation, not 5 [type=too_long, input_value=[1, 2, 3, 4, 5], input_type=list]
    """


PositiveList = list[Annotated[T, Gt(0)]]

ta = TypeAdapter(PositiveList[float])

v = ta.validate_python([1.0])
assert type(v[0]) is float


try:
    ta.validate_python([-1.0])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[constrained-float]
    0
      Input should be greater than 0 [type=greater_than, input_value=-1.0, input_type=float]
    """
```

(`ShortList[T]` হলো "সর্বোচ্চ ৪টি উপাদানের তালিকা", যেকোনো টাইপের জন্য; `ShortList[int]` দিলে integer-এর ছোট তালিকা। একইভাবে `PositiveList[float]` মানে ধনাত্মক float-এর তালিকা।)

### নামযুক্ত type alias { #named-type-aliases }

/// info | v2.11-এ যোগ হয়েছে
নামযুক্ত type alias এখন পুরোপুরি সমর্থিত।
///

ওপরের উদাহরণগুলো *অন্তর্নিহিত* (implicit) type alias ব্যবহার করে, যা একটি ভেরিয়েবলে বসানো। চলমান অবস্থায়, Pydantic-এর
জানার কোনো উপায় নেই যে এটি কোন ভেরিয়েবলের নামে বসানো হয়েছিল, আর এটি দুই কারণে
সমস্যা হতে পারে:

* alias-এর [JSON Schema](./json_schema.md) একটি
  [definition](https://json-schema.org/understanding-json-schema/structuring#defs)-এ রূপান্তরিত হবে না।
  এটি মূলত তখন কাজের যখন একটি মডেলের সংজ্ঞায় alias-টি একাধিকবার ব্যবহার করেন।
* বেশিরভাগ ক্ষেত্রে, [পুনরাবৃত্ত type alias](#named-recursive-types) কাজ করবে না।

নতুন [`type` স্টেটমেন্ট](https://typing.readthedocs.io/en/latest/spec/aliases.html#type-statement)
([PEP 695](https://peps.python.org/pep-0695/)-এ আনা) কাজে লাগিয়ে, এভাবে alias সংজ্ঞায়িত করতে পারেন:

/// tab | Python 3.10 ও তার পরে

```python
from typing import Annotated

from annotated_types import Gt
from typing_extensions import TypeAliasType

from pydantic import BaseModel

PositiveIntList = TypeAliasType('PositiveIntList', list[Annotated[int, Gt(0)]])


class Model(BaseModel):
    x: PositiveIntList
    y: PositiveIntList


print(Model.model_json_schema())  # (1)!
"""
{
    '$defs': {
        'PositiveIntList': {
            'items': {'exclusiveMinimum': 0, 'type': 'integer'},
            'type': 'array',
        }
    },
    'properties': {
        'x': {'$ref': '#/$defs/PositiveIntList'},
        'y': {'$ref': '#/$defs/PositiveIntList'},
    },
    'required': ['x', 'y'],
    'title': 'Model',
    'type': 'object',
}
"""
```

1. যদি `PositiveIntList` একটি অন্তর্নিহিত type alias হিসেবে সংজ্ঞায়িত হতো, তাহলে এর সংজ্ঞা
   `'x'` আর `'y'` দুই জায়গাতেই পুনরাবৃত্ত হতো।

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

```python
from typing import Annotated

from annotated_types import Gt

from pydantic import BaseModel

type PositiveIntList = list[Annotated[int, Gt(0)]]


class Model(BaseModel):
    x: PositiveIntList
    y: PositiveIntList


print(Model.model_json_schema())  # (1)!
"""
{
    '$defs': {
        'PositiveIntList': {
            'items': {'exclusiveMinimum': 0, 'type': 'integer'},
            'type': 'array',
        }
    },
    'properties': {
        'x': {'$ref': '#/$defs/PositiveIntList'},
        'y': {'$ref': '#/$defs/PositiveIntList'},
    },
    'required': ['x', 'y'],
    'title': 'Model',
    'type': 'object',
}
"""
```

1. যদি `PositiveIntList` একটি অন্তর্নিহিত type alias হিসেবে সংজ্ঞায়িত হতো, তাহলে এর সংজ্ঞা
   `'x'` আর `'y'` দুই জায়গাতেই পুনরাবৃত্ত হতো।

///

<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#metadata-type-alias-warning}{% endraw %}

//// warning | কখন নামযুক্ত type alias ব্যবহার করবেন

যদিও স্ট্যাটিক টাইপ চেকারের কাছে (নামযুক্ত) PEP 695 alias আর অন্তর্নিহিত type alias সমতুল্য হওয়ার কথা,
Pydantic নামযুক্ত alias-এর ভেতরের ফিল্ড-নির্দিষ্ট মেটাডেটা বুঝবে *না*। অর্থাৎ, `alias`, `default`, `deprecated`-এর মতো মেটাডেটা
ব্যবহার *করা যাবে না*:

/// tab | Python 3.10 ও তার পরে

```python
from typing import Annotated

from typing_extensions import TypeAliasType

from pydantic import BaseModel, Field

MyAlias = TypeAliasType('MyAlias', Annotated[int, Field(default=1)])


class Model(BaseModel):
    x: MyAlias  # This is not allowed
```

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

```python
from typing import Annotated

from pydantic import BaseModel, Field

type MyAlias = Annotated[int, Field(default=1)]


class Model(BaseModel):
    x: MyAlias  # This is not allowed
```

///

শুধু সেই মেটাডেটা অনুমোদিত যা অ্যানোটেট করা টাইপের নিজের ওপর প্রয়োগ করা যায়
(যেমন [যাচাইয়ের শর্ত](./fields.md#field-constraints) আর JSON মেটাডেটা)।
ফিল্ড-নির্দিষ্ট মেটাডেটা সমর্থন করতে হলে type alias-এর [`__value__`][typing.TypeAliasType.__value__] আগেভাগেই পরীক্ষা করতে হতো,
আর তাহলে Pydantic alias-টিকে একটি JSON Schema definition হিসেবে রাখতে পারত না।

////

//// note | নোট

অন্তর্নিহিত type alias-এর মতোই, generic alias-এর ভেতরেও [টাইপ ভেরিয়েবল][typing.TypeVar] ব্যবহার করা যায়:

/// tab | Python 3.10 ও তার পরে

```python
from typing import Annotated, TypeVar

from annotated_types import Len
from typing_extensions import TypeAliasType

T = TypeVar('T')

ShortList = TypeAliasType(
    'ShortList', Annotated[list[T], Len(max_length=4)], type_params=(T,)
)
```

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

```python
from typing import Annotated, TypeVar

from annotated_types import Len

type ShortList[T] = Annotated[list[T], Len(max_length=4)]
```

///

////

#### নামযুক্ত পুনরাবৃত্ত টাইপ { #named-recursive-types }

যখনই পুনরাবৃত্ত (নিজেকেই নির্দেশ করে এমন) type alias সংজ্ঞায়িত করতে হবে, তখন নামযুক্ত type alias ব্যবহার করা উচিত (1)।
{ .annotate }

1. কয়েকটি কারণে, Pydantic অন্তর্নিহিত পুনরাবৃত্ত alias সমর্থন করতে পারে না। যেমন,
   এটি মডিউলগুলোর মধ্যে [forward annotation](./forward_annotations.md) সমাধান করতে পারবে না।

যেমন, এখানে একটি JSON টাইপের উদাহরণ সংজ্ঞা দেওয়া হলো:

/// tab | Python 3.10 ও তার পরে

```python
from typing_extensions import TypeAliasType

from pydantic import TypeAdapter

Json = TypeAliasType(
    'Json',
    'dict[str, Json] | list[Json] | str | int | float | bool | None',  # (1)!
)

ta = TypeAdapter(Json)
print(ta.json_schema())
"""
{
    '$defs': {
        'Json': {
            'anyOf': [
                {
                    'additionalProperties': {'$ref': '#/$defs/Json'},
                    'type': 'object',
                },
                {'items': {'$ref': '#/$defs/Json'}, 'type': 'array'},
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'number'},
                {'type': 'boolean'},
                {'type': 'null'},
            ]
        }
    },
    '$ref': '#/$defs/Json',
}
"""
```

1. অ্যানোটেশনটি উদ্ধৃতিচিহ্নে মুড়ে দেওয়া দরকার, কারণ এটি আগেভাগেই মূল্যায়ন হয়
   (আর `Json` তখনো সংজ্ঞায়িত হয়নি)।

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

```python
from pydantic import TypeAdapter

type Json = dict[str, Json] | list[Json] | str | int | float | bool | None  # (1)!

ta = TypeAdapter(Json)
print(ta.json_schema())
"""
{
    '$defs': {
        'Json': {
            'anyOf': [
                {
                    'additionalProperties': {'$ref': '#/$defs/Json'},
                    'type': 'object',
                },
                {'items': {'$ref': '#/$defs/Json'}, 'type': 'array'},
                {'type': 'string'},
                {'type': 'integer'},
                {'type': 'number'},
                {'type': 'boolean'},
                {'type': 'null'},
            ]
        }
    },
    '$ref': '#/$defs/Json',
}
"""
```

1. একটি নামযুক্ত type alias-এর মান দেরিতে মূল্যায়ন হয়, তাই forward annotation ব্যবহারের দরকার নেই।

///

(JSON মান নিজেই পুনরাবৃত্ত: একটি JSON অবজেক্টের ভেতরে আবার JSON মান, তালিকার ভেতরে আবার JSON মান। তাই `Json` টাইপটি নিজের নাম নিজের সংজ্ঞায় ব্যবহার করে।)

/// tip | পরামর্শ

সুবিধার জন্য Pydantic একটি [`JsonValue`][pydantic.types.JsonValue] টাইপ সংজ্ঞায়িত করে রেখেছে।

///

### `__get_pydantic_core_schema__` দিয়ে যাচাই নিজের মতো করা <a name="customizing_validation_with_get_pydantic_core_schema"></a> { #customizing-validation-with-get_pydantic_core_schema }

Pydantic কাস্টম ক্লাস কীভাবে সামলায় তা আরও ব্যাপকভাবে নিজের মতো করতে, বিশেষ করে যখন আপনার কাছে
ক্লাসটি আছে বা এর সাব-ক্লাস বানাতে পারেন, তখন Pydantic-কে `pydantic-core` schema কীভাবে তৈরি করতে হবে তা জানাতে একটি বিশেষ
`__get_pydantic_core_schema__` বাস্তবায়ন করতে পারেন।

যদিও যাচাই আর সিরিয়ালাইজেশন সামলাতে `pydantic` ভেতরে `pydantic-core` ব্যবহার করে, এটি Pydantic V2-এর জন্য একটি নতুন API,
তাই এটি ভবিষ্যতে বদলানোর সবচেয়ে বেশি সম্ভাবনাময় জায়গাগুলোর একটি, আর আপনার উচিত যতটা সম্ভব বিল্ট-ইন
গঠনগুলোতেই থাকা, যেমন `annotated-types`, `pydantic.Field`, বা `BeforeValidator` ইত্যাদি যা দেয়।

`__get_pydantic_core_schema__` একটি কাস্টম টাইপে আর `Annotated`-এ রাখার জন্য তৈরি মেটাডেটায়, দুই জায়গাতেই বাস্তবায়ন করতে পারেন।
দুই ক্ষেত্রেই API-টি middleware-এর মতো আর "wrap" validator-এর মতো: আপনি একটি `source_type` পান (যা
অবশ্যই ক্লাসের মতো একই নয়, বিশেষ করে generic-এর ক্ষেত্রে) আর একটি `handler`, যা একটি টাইপসহ কল করে হয়
`Annotated`-এর পরবর্তী মেটাডেটা কল করতে পারেন, নয়তো Pydantic-এর ভেতরের schema তৈরিতে যেতে পারেন।

সবচেয়ে সহজ কিছু-না-করা বাস্তবায়ন দেওয়া টাইপসহ handler কল করে, তারপর তা ফলাফল হিসেবে ফেরত দেয়। আপনি চাইলে
handler কল করার আগে টাইপ বদলাতে পারেন, handler-এর ফেরত দেওয়া core schema বদলাতে পারেন, অথবা handler একেবারেই
কল না করতে পারেন।

#### একটি কাস্টম টাইপের মেথড হিসেবে { #as-a-method-on-a-custom-type }

নিচে এমন একটি টাইপের উদাহরণ, যা কীভাবে যাচাই হবে তা নিজের মতো করতে `__get_pydantic_core_schema__` ব্যবহার করে।
এটি Pydantic V1-এ `__get_validators__` বাস্তবায়নের সমতুল্য।

```python
from typing import Any

from pydantic_core import CoreSchema, core_schema

from pydantic import GetCoreSchemaHandler, TypeAdapter


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


ta = TypeAdapter(Username)
res = ta.validate_python('abc')
assert isinstance(res, Username)
assert res == 'abc'
```

(`Username` হলো `str`-এর একটি সাব-ক্লাস। schema বলে: "আগে সাধারণ `str` হিসেবে যাচাই করো (`handler(str)`), তারপর ফলাফলটি দিয়ে `Username` বানাও"। ফলে যাচাইয়ের পরে আপনি একটি আসল `Username` অবজেক্ট পান।)

কাস্টম টাইপের JSON schema কীভাবে নিজের মতো করবেন তার আরও বিস্তারিত জানতে [JSON Schema](../concepts/json_schema.md) দেখুন।

#### একটি অ্যানোটেশন হিসেবে { #as-an-annotation }

প্রায়ই আপনি শুধু generic টাইপ প্যারামিটারের চেয়েও বেশি কিছু দিয়ে আপনার কাস্টম টাইপ প্যারামিটারাইজ করতে চাইবেন (যা টাইপ সিস্টেম দিয়ে করা যায় আর পরে আলোচনা করা হবে)। অথবা হয়তো আপনার সাব-ক্লাসের একটি ইনস্ট্যান্স বানানোর আসলে দরকার নেই (বা চানও না); আপনি আসলে মূল টাইপটিই চান, শুধু কিছু বাড়তি যাচাইসহ।

যেমন, যদি নিজেই `pydantic.AfterValidator` বাস্তবায়ন করতেন ([যাচাই আর সিরিয়ালাইজেশন যোগ করা](#adding-validation-and-serialization) দেখুন), তাহলে নিচের মতো কিছু করতেন:

```python
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic_core import CoreSchema, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


@dataclass(frozen=True)  # (1)!
class MyAfterValidator:
    func: Callable[[Any], Any]

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            self.func, handler(source_type)
        )


Username = Annotated[str, MyAfterValidator(str.lower)]


class Model(BaseModel):
    name: Username


assert Model(name='ABC').name == 'abc'  # (2)!
```

1. `frozen=True` নির্দিষ্ট করায় `MyAfterValidator` hashable হয়। এটি ছাড়া `Username | None`-এর মতো একটি union এরর দেবে।
2. লক্ষ্য করুন, আগের উদাহরণের মতো টাইপ চেকার `'ABC'`-কে `Username`-এ বসানো নিয়ে আপত্তি করবে না, কারণ তারা `Username`-কে `str` থেকে আলাদা কোনো টাইপ মনে করে না।

#### তৃতীয় পক্ষের টাইপ সামলানো { #handling-third-party-types }

আগের অংশের প্যাটার্নের আরেকটি ব্যবহার হলো তৃতীয় পক্ষের (অন্য লাইব্রেরির) টাইপ সামলানো।

```python
from typing import Annotated, Any

from pydantic_core import core_schema

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
)
from pydantic.json_schema import JsonSchemaValue


class ThirdPartyType:
    """
    This is meant to represent a type from a third-party library that wasn't designed with Pydantic
    integration in mind, and so doesn't have a `pydantic_core.CoreSchema` or anything.
    """

    x: int

    def __init__(self):
        self.x = 0


class _ThirdPartyTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * ints will be parsed as `ThirdPartyType` instances with the int as the x attribute
        * `ThirdPartyType` instances will be parsed as `ThirdPartyType` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just an int
        """

        def validate_from_int(value: int) -> ThirdPartyType:
            result = ThirdPartyType()
            result.x = value
            return result

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_int),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_int_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ThirdPartyType),
                    from_int_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.x
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `int`
        return handler(core_schema.int_schema())


# We now create an `Annotated` wrapper that we'll use as the annotation for fields on `BaseModel`s, etc.
PydanticThirdPartyType = Annotated[
    ThirdPartyType, _ThirdPartyTypePydanticAnnotation
]


# Create a model class that uses this annotation as a field
class Model(BaseModel):
    third_party_type: PydanticThirdPartyType


# Demonstrate that this field is handled correctly, that ints are parsed into `ThirdPartyType`, and that
# these instances are also "dumped" directly into ints as expected.
m_int = Model(third_party_type=1)
assert isinstance(m_int.third_party_type, ThirdPartyType)
assert m_int.third_party_type.x == 1
assert m_int.model_dump() == {'third_party_type': 1}

# Do the same thing where an instance of ThirdPartyType is passed in
instance = ThirdPartyType()
assert instance.x == 0
instance.x = 10

m_instance = Model(third_party_type=instance)
assert isinstance(m_instance.third_party_type, ThirdPartyType)
assert m_instance.third_party_type.x == 10
assert m_instance.model_dump() == {'third_party_type': 10}

# Demonstrate that validation errors are raised as expected for invalid inputs
try:
    Model(third_party_type='a')
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    third_party_type.is-instance[ThirdPartyType]
      Input should be an instance of ThirdPartyType [type=is_instance_of, input_value='a', input_type=str]
    third_party_type.chain[int,function-plain[validate_from_int()]]
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """


assert Model.model_json_schema() == {
    'properties': {
        'third_party_type': {'title': 'Third Party Type', 'type': 'integer'}
    },
    'required': ['third_party_type'],
    'title': 'Model',
    'type': 'object',
}
```

এই পদ্ধতি দিয়ে, যেমন Pandas বা Numpy টাইপের আচরণ সংজ্ঞায়িত করতে পারেন।

/// info | কোডটি সহজ ভাষায়

`ThirdPartyType` এমন একটি ক্লাস যা Pydantic-এর কথা ভেবে বানানো হয়নি, আর আমরা এর কোড বদলাতে পারি না। তাই আলাদা একটি "অনুবাদক" ক্লাস (`_ThirdPartyTypePydanticAnnotation`) বানিয়ে `Annotated[ThirdPartyType, ...]`-এ লাগানো হয়েছে। অনুবাদক Pydantic-কে বলে দেয়: integer এলে তা দিয়ে একটি `ThirdPartyType` বানাও, ইতিমধ্যে `ThirdPartyType` হলে যেমন আছে রাখো, আর আউটপুটে শুধু `x` integer-টি লেখো।

///

#### বাড়তি কোড কমাতে `GetPydanticSchema` ব্যবহার { #using-getpydanticschema-to-reduce-boilerplate }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.types.GetPydanticSchema`][pydantic.types.GetPydanticSchema]<br>

///

হয়তো লক্ষ্য করেছেন, ওপরের যে উদাহরণগুলোতে আমরা একটি মার্কার ক্লাস বানাই, সেগুলোতে বেশ কিছু একই ধাঁচের বাড়তি কোড (boilerplate) লাগে।
অনেক সহজ ক্ষেত্রে `pydantic.GetPydanticSchema` ব্যবহার করে এটি অনেক কমিয়ে আনতে পারেন:

```python
from typing import Annotated

from pydantic_core import core_schema

from pydantic import BaseModel, GetPydanticSchema


class Model(BaseModel):
    y: Annotated[
        str,
        GetPydanticSchema(
            lambda tp, handler: core_schema.no_info_after_validator_function(
                lambda x: x * 2, handler(tp)
            )
        ),
    ]


assert Model(y='ab').y == 'abab'
```

(আলাদা ক্লাস না বানিয়ে একটি lambda-তেই বলা হয়েছে: স্ট্রিং যাচাইয়ের পরে তাকে দ্বিগুণ করো, তাই `'ab'` → `'abab'`।)

#### সারসংক্ষেপ { #summary }

সংক্ষেপে বলা যাক:

1. `Annotated`-এর মাধ্যমে টাইপ নিজের মতো করতে Pydantic উচ্চ-স্তরের hook দেয়, যেমন `AfterValidator` আর `Field`। সম্ভব হলে এগুলোই ব্যবহার করুন।
2. ভেতরে ভেতরে এগুলো যাচাই নিজের মতো করতে `pydantic-core` ব্যবহার করে, আর `GetPydanticSchema` বা `__get_pydantic_core_schema__`-সহ একটি মার্কার ক্লাস দিয়ে সরাসরি সেখানে যুক্ত হতে পারেন।
3. যদি সত্যিই একটি কাস্টম টাইপ চান, তাহলে টাইপটির নিজের ওপরেই `__get_pydantic_core_schema__` বাস্তবায়ন করতে পারেন।

### কাস্টম generic ক্লাস সামলানো { #handling-custom-generic-classes }

/// warning | সতর্কতা

এটি একটি অ্যাডভান্সড কৌশল, যা শুরুতে আপনার দরকার নাও হতে পারে। বেশিরভাগ
ক্ষেত্রে সম্ভবত স্ট্যান্ডার্ড Pydantic মডেল দিয়েই কাজ চলে যাবে।

///

ফিল্ডের টাইপ হিসেবে
[Generic ক্লাস](https://docs.python.org/3/library/typing.html#typing.Generic) ব্যবহার করে,
`__get_pydantic_core_schema__` দিয়ে "টাইপ প্যারামিটার" (বা সাব-টাইপ)-এর ভিত্তিতে কাস্টম যাচাই করতে পারেন।

আপনি যে Generic ক্লাস সাব-টাইপ হিসেবে ব্যবহার করছেন, তাতে যদি একটি classmethod
`__get_pydantic_core_schema__` থাকে, তাহলে এটি কাজ করাতে
[`arbitrary_types_allowed`][pydantic.config.ConfigDict.arbitrary_types_allowed] ব্যবহারের দরকার নেই।

যেহেতু `source_type` প্যারামিটার `cls` প্যারামিটারের মতো একই নয়, তাই generic প্যারামিটারগুলো বের করতে `typing.get_args` (বা `typing_extensions.get_args`) ব্যবহার করতে পারেন।
তারপর `handler.generate_schema` কল করে সেগুলোর schema তৈরি করতে `handler` ব্যবহার করতে পারেন।
লক্ষ্য করুন, আমরা `handler(get_args(source_type)[0])`-এর মতো কিছু করি না, কারণ আমরা সেই generic প্যারামিটারের জন্য একটি সম্পর্কহীন
schema তৈরি করতে চাই, `Annotated` মেটাডেটা ইত্যাদির বর্তমান প্রসঙ্গ দিয়ে প্রভাবিত নয় এমন।
কাস্টম টাইপের ক্ষেত্রে এটি কম গুরুত্বপূর্ণ, কিন্তু schema তৈরি বদলায় এমন অ্যানোটেট করা মেটাডেটার জন্য অত্যন্ত জরুরি।

```python
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, get_args, get_origin

from pydantic_core import CoreSchema, core_schema

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    ValidationError,
    ValidatorFunctionWrapHandler,
)

ItemType = TypeVar('ItemType')


# This is not a pydantic model, it's an arbitrary generic class
@dataclass
class Owner(Generic[ItemType]):
    name: str
    item: ItemType

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        origin = get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            origin = source_type
            item_tp = Any
        else:
            item_tp = get_args(source_type)[0]
        # both calling handler(...) and handler.generate_schema(...)
        # would work, but prefer the latter for conceptual and consistency reasons
        item_schema = handler.generate_schema(item_tp)

        def val_item(
            v: Owner[Any], handler: ValidatorFunctionWrapHandler
        ) -> Owner[Any]:
            v.item = handler(v.item)
            return v

        python_schema = core_schema.chain_schema(
            # `chain_schema` means do the following steps in order:
            [
                # Ensure the value is an instance of Owner
                core_schema.is_instance_schema(cls),
                # Use the item_schema to validate `items`
                core_schema.no_info_wrap_validator_function(
                    val_item, item_schema
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            # for JSON accept an object with name and item keys
            json_schema=core_schema.chain_schema(
                [
                    core_schema.typed_dict_schema(
                        {
                            'name': core_schema.typed_dict_field(
                                core_schema.str_schema()
                            ),
                            'item': core_schema.typed_dict_field(item_schema),
                        }
                    ),
                    # after validating the json data convert it to python
                    core_schema.no_info_before_validator_function(
                        lambda data: Owner(
                            name=data['name'], item=data['item']
                        ),
                        # note that we reuse the same schema here as below
                        python_schema,
                    ),
                ]
            ),
            python_schema=python_schema,
        )


class Car(BaseModel):
    color: str


class House(BaseModel):
    rooms: int


class Model(BaseModel):
    car_owner: Owner[Car]
    home_owner: Owner[House]


model = Model(
    car_owner=Owner(name='John', item=Car(color='black')),
    home_owner=Owner(name='James', item=House(rooms=3)),
)
print(model)
"""
car_owner=Owner(name='John', item=Car(color='black')) home_owner=Owner(name='James', item=House(rooms=3))
"""

try:
    # If the values of the sub-types are invalid, we get an error
    Model(
        car_owner=Owner(name='John', item=House(rooms=3)),
        home_owner=Owner(name='James', item=Car(color='black')),
    )
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    wine
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='Kinda good', input_type=str]
    cheese
      Input should be a valid boolean, unable to interpret input [type=bool_parsing, input_value='yeah', input_type=str]
    """

# Similarly with JSON
model = Model.model_validate_json(
    '{"car_owner":{"name":"John","item":{"color":"black"}},"home_owner":{"name":"James","item":{"rooms":3}}}'
)
print(model)
"""
car_owner=Owner(name='John', item=Car(color='black')) home_owner=Owner(name='James', item=House(rooms=3))
"""

try:
    Model.model_validate_json(
        '{"car_owner":{"name":"John","item":{"rooms":3}},"home_owner":{"name":"James","item":{"color":"black"}}}'
    )
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    car_owner.item.color
      Field required [type=missing, input_value={'rooms': 3}, input_type=dict]
    home_owner.item.rooms
      Field required [type=missing, input_value={'color': 'black'}, input_type=dict]
    """
```

(`Owner[ItemType]` একটি সাধারণ dataclass, Pydantic মডেল নয়। এর `__get_pydantic_core_schema__` `get_args` দিয়ে জেনে নেয় `ItemType` আসলে কী (যেমন `Owner[int]` হলে `int`), তারপর `item` ফিল্ডটি সেই টাইপ অনুযায়ী যাচাই করে।)

#### Generic container { #generic-containers }

একই ধারণা প্রয়োগ করে generic container টাইপ তৈরি করা যায়, যেমন একটি কাস্টম `Sequence` টাইপ:

```python
from collections.abc import Sequence
from typing import Any, TypeVar, get_args

from pydantic_core import ValidationError, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler

T = TypeVar('T')


class MySequence(Sequence[T]):
    def __init__(self, v: Sequence[T]):
        self.v = v

    def __getitem__(self, i):
        return self.v[i]

    def __len__(self):
        return len(self.v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source)
        if args:
            # replace the type and rely on Pydantic to generate the right schema
            # for `Sequence`
            sequence_t_schema = handler.generate_schema(Sequence[args[0]])
        else:
            sequence_t_schema = handler.generate_schema(Sequence)

        non_instance_schema = core_schema.no_info_after_validator_function(
            MySequence, sequence_t_schema
        )
        return core_schema.union_schema([instance_schema, non_instance_schema])


class M(BaseModel):
    model_config = dict(validate_default=True)

    s1: MySequence = [3]


m = M()
print(m)
#> s1=<__main__.MySequence object at 0x0123456789ab>
print(m.s1.v)
#> [3]


class M(BaseModel):
    s1: MySequence[int]


M(s1=[1])
try:
    M(s1=['a'])
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for M
    s1.is-instance[MySequence]
      Input should be an instance of MySequence [type=is_instance_of, input_value=['a'], input_type=list]
    s1.function-after[MySequence(), json-or-python[json=list[int],python=chain[is-instance[Sequence],function-wrap[sequence_validator()]]]].0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

### ফিল্ডের নাম পাওয়া { #access-to-field-name }

/// note | নোট

এটি Pydantic V2 থেকে V2.3 পর্যন্ত সম্ভব ছিল না, Pydantic V2.4-এ এটি [আবার যোগ করা হয়েছে](https://github.com/pydantic/pydantic/pull/7542)।

///

Pydantic V2.4 থেকে, `__get_pydantic_core_schema__`-এর ভেতরে `handler.field_name` দিয়ে ফিল্ডের নাম পেতে পারেন,
আর এর মাধ্যমে ফিল্ডের নাম সেট করতে পারেন, যা `info.field_name` থেকে পাওয়া যাবে।

```python
from typing import Any

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler, ValidationInfo


class CustomType:
    """Custom type that stores the field it was used in."""

    def __init__(self, value: int, field_name: str):
        self.value = value
        self.field_name = field_name

    def __repr__(self):
        return f'CustomType<{self.value} {self.field_name!r}>'

    @classmethod
    def validate(cls, value: int, info: ValidationInfo):
        return cls(value, info.field_name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate, handler(int)
        )


class MyModel(BaseModel):
    my_field: CustomType


m = MyModel(my_field=1)
print(m.my_field)
#> CustomType<1 'my_field'>
```

`Annotated`-এর সাথে ব্যবহৃত মার্কার থেকেও `field_name` পেতে পারেন, যেমন [`AfterValidator`][pydantic.functional_validators.AfterValidator]।

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ValidationInfo


def my_validators(value: int, info: ValidationInfo):
    return f'<{value} {info.field_name!r}>'


class MyModel(BaseModel):
    my_field: Annotated[int, AfterValidator(my_validators)]


m = MyModel(my_field=1)
print(m.my_field)
#> <1 'my_field'>
```

/// check | সংক্ষেপে মনে রাখুন

* সাধারণ Python টাইপ (`int`, `str`, `date` ...) সরাসরি চলে; Pydantic বাড়তি টাইপও দেয় (`SecretStr`, `EmailStr` ...)।
* খারাপ আইটেম বাদ দিতে `OnErrorOmit`, প্রথম এররেই থামতে `FailFast`।
* নিজের পুনরায় ব্যবহারযোগ্য টাইপ: `MyType = Annotated[int, Field(gt=0), AfterValidator(...)]`।
* JSON-এর মতো পুনরাবৃত্ত টাইপের জন্য নামযুক্ত type alias (`TypeAliasType` বা `type` স্টেটমেন্ট)।
* সম্পূর্ণ নিজস্ব আচরণ দরকার হলে শেষ ভরসা `__get_pydantic_core_schema__`।

///
