# ফিল্ড { #fields }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.fields.Field`][pydantic.fields.Field]<br>

///

/// note | এই পেজে যা শিখবেন

* `Field()` দিয়ে একটি ফিল্ডকে নিজের মতো সাজানো: ডিফল্ট মান, শর্ত, alias, strict, frozen, exclude ইত্যাদি।
* `Annotated` প্যাটার্ন কী আর কেন এটি প্রায়ই ভালো।
* `default_factory` দিয়ে প্রতিবার নতুন ডিফল্ট মান তৈরি করা।
* deprecated ফিল্ড আর `@computed_field` (অন্য ফিল্ড থেকে হিসাব করা ফিল্ড)।

FastAPI-তে `Query()`, `Path()`, `Body()`-তে যে `gt`, `max_length`, `alias` ইত্যাদি লিখেছিলেন, সেগুলো আসলে এই `Field()`-এরই আত্মীয়।

///

এই অংশে আমরা Pydantic মডেলের ফিল্ড নিজের মতো সাজানোর উপলব্ধ ব্যবস্থাগুলো দেখব:
[ডিফল্ট মান](#default-values), [JSON Schema মেটাডেটা](#customizing-json-schema),
[শর্ত (constraint)](#field-constraints) ইত্যাদি।

এজন্য [`Field()`][pydantic.fields.Field] ফাংশন অনেক ব্যবহার হয়, আর এটি dataclass-এর জন্য স্ট্যান্ডার্ড লাইব্রেরির
[`field()`][dataclasses.field] ফাংশনের মতোই আচরণ করে – অ্যানোটেট করা অ্যাট্রিবিউটে বসিয়ে দিয়ে:

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    name: str = Field(frozen=True)
```

/// note | নোট

`name`-এ একটি মান বসানো থাকলেও, এটি এখনো বাধ্যতামূলক আর এর কোনো ডিফল্ট মান নেই। যদি জোর দিয়ে বোঝাতে চান যে
একটি মান অবশ্যই দিতে হবে, তাহলে [ellipsis][Ellipsis] (`...`) ব্যবহার করতে পারেন:

```python
class Model(BaseModel):
    name: str = Field(..., frozen=True)
```

তবে এর ব্যবহার নিরুৎসাহিত করা হয়, কারণ এটি স্ট্যাটিক টাইপ চেকারের সাথে ভালোভাবে মেলে না।

///

## Annotated প্যাটার্ন { #the-annotated-pattern }

একটি মডেল ফিল্ডে শর্ত প্রয়োগ করতে বা [`Field()`][pydantic.fields.Field] ফাংশন যুক্ত করতে, Pydantic
একটি অ্যানোটেশনে মেটাডেটা যুক্ত করার জন্য [`Annotated`][typing.Annotated] টাইপিং গঠনও সমর্থন করে:

```python
from typing import Annotated

from pydantic import BaseModel, Field, WithJsonSchema


class Model(BaseModel):
    name: Annotated[str, Field(strict=True), WithJsonSchema({'extra': 'data'})]
```

স্ট্যাটিক টাইপ চেকারের দিক থেকে, `name`-এর টাইপ এখনো `str`, কিন্তু Pydantic উপলব্ধ মেটাডেটা
কাজে লাগিয়ে যাচাইয়ের যুক্তি, টাইপের শর্ত ইত্যাদি যোগ করে।

/// tip | উদাহরণ দিয়ে বুঝি

`Annotated[str, ...]` হলো একটি জিনিসে "স্টিকার" লাগানোর মতো। মূল জিনিসটি `str`-ই থাকে (টাইপ চেকার আর এডিটর তাই দেখে), কিন্তু গায়ে লাগানো স্টিকারগুলো (`Field(strict=True)` ইত্যাদি) Pydantic পড়ে বাড়তি নিয়ম প্রয়োগ করে।

///

এই প্যাটার্ন ব্যবহারের কিছু সুবিধা আছে:

* `f: <type> = Field(...)` রূপটি বিভ্রান্তিকর হতে পারে আর ব্যবহারকারীকে ভাবাতে পারে যে `f`-এর
  একটি ডিফল্ট মান আছে, অথচ বাস্তবে এটি এখনো বাধ্যতামূলক।
* একটি ফিল্ডের জন্য ইচ্ছামতো সংখ্যক মেটাডেটা উপাদান দিতে পারেন। ওপরের উদাহরণে যেমন দেখানো হয়েছে,
  [`Field()`][pydantic.fields.Field] ফাংশন শুধু সীমিত কিছু শর্ত/মেটাডেটা সমর্থন করে,
  আর কিছু ক্ষেত্রে আপনাকে [`WithJsonSchema`][pydantic.WithJsonSchema]-এর মতো ভিন্ন Pydantic ইউটিলিটি
  ব্যবহার করতে হতে পারে।
* টাইপগুলো পুনরায় ব্যবহারযোগ্য করা যায় (এই প্যাটার্ন ব্যবহার করে [কাস্টম টাইপ](./types.md#using-the-annotated-pattern)
  নিয়ে ডকুমেন্টেশন দেখুন)।

তবে লক্ষ্য করুন, [`Field()`][pydantic.fields.Field] ফাংশনের কিছু আর্গুমেন্ট (যেমন `default`,
`default_factory` আর `alias`) স্ট্যাটিক টাইপ চেকার একটি সঠিক `__init__()` মেথড তৈরিতে বিবেচনা করে।
Annotated প্যাটার্ন তারা বোঝে *না*, তাই এই ক্ষেত্রে সাধারণ অ্যাসাইনমেন্ট রূপ ব্যবহার করা উচিত।

/// tip | পরামর্শ

Annotated প্যাটার্ন টাইপের নির্দিষ্ট অংশে মেটাডেটা যোগ করতেও ব্যবহার করা যায়। যেমন,
এভাবে [যাচাইয়ের শর্ত](#field-constraints) যোগ করা যায়:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    int_list: list[Annotated[int, Field(gt=0)]]
    # Valid: [1, 3]
    # Invalid: [-1, 2]
```

(এখানে শর্ত `gt=0` তালিকার ভেতরের প্রতিটি `int`-এর ওপর প্রযোজ্য, পুরো তালিকার ওপর নয়।)

*ফিল্ড* আর *টাইপ* মেটাডেটা মিশিয়ে না ফেলার ব্যাপারে সতর্ক থাকুন:

```python
class Model(BaseModel):
    field_bad: Annotated[int, Field(deprecated=True)] | None = None  # (1)!
    field_ok: Annotated[int | None, Field(deprecated=True)] = None  # (2)!
```

  1. [`Field()`][pydantic.fields.Field] ফাংশনটি `int` টাইপে প্রয়োগ হয়েছে, তাই
     `deprecated` ফ্ল্যাগের কোনো প্রভাব থাকবে না। [`Field()`][pydantic.fields.Field] ফাংশনের নাম শুনে মনে হয়
     এটি ফিল্ডে প্রয়োগ হওয়া উচিত, তাই এটি বিভ্রান্তিকর হতে পারে, কিন্তু API-টি ডিজাইন করা হয়েছিল যখন এই ফাংশনই মেটাডেটা দেওয়ার
     একমাত্র উপায় ছিল। বিকল্প হিসেবে [`annotated_types`](https://github.com/annotated-types/annotated-types)
     লাইব্রেরি ব্যবহার করতে পারেন, যা এখন Pydantic সমর্থন করে।

  2. [`Field()`][pydantic.fields.Field] ফাংশনটি "শীর্ষ-স্তরের" union টাইপে প্রয়োগ হয়েছে,
     তাই `deprecated` ফ্ল্যাগ ফিল্ডে প্রয়োগ হবে।

///

## মডেলের ফিল্ড পরীক্ষা করা { #inspecting-model-fields }

[`model_fields`][pydantic.main.BaseModel.model_fields] ক্লাস অ্যাট্রিবিউট দিয়ে একটি মডেলের ফিল্ডগুলো পরীক্ষা করা যায়
(অথবা [Pydantic dataclass](./dataclasses.md)-এর জন্য `__pydantic_fields__` অ্যাট্রিবিউট দিয়ে)। এটি ফিল্ডের নাম থেকে
তাদের সংজ্ঞার ([`FieldInfo`][pydantic.fields.FieldInfo] ইনস্ট্যান্স হিসেবে) একটি ম্যাপিং।

```python
from typing import Annotated

from pydantic import BaseModel, Field, WithJsonSchema


class Model(BaseModel):
    a: Annotated[
        int, Field(gt=1), WithJsonSchema({'extra': 'data'}), Field(alias='b')
    ] = 1


field_info = Model.model_fields['a']
print(field_info.annotation)
#> <class 'int'>
print(field_info.alias)
#> b
print(field_info.metadata)
#> [Gt(gt=1), WithJsonSchema(json_schema={'extra': 'data'}, mode=None)]
```

(`FieldInfo` থেকে ফিল্ডের টাইপ (`annotation`), alias আর শর্তগুলো (`metadata`) পড়া যায়। লক্ষ্য করুন, দুটি আলাদা `Field()` মিলে একটি `FieldInfo` হয়েছে।)

/// warning | v2.11-এ deprecated, v3-তে সরানো হবে
[`model_fields`][pydantic.main.BaseModel.model_fields] শুধু ক্লাস অবজেক্ট থেকে ব্যবহার করা যায়, ইনস্ট্যান্স থেকে নয়।
///

## ডিফল্ট মান { #default-values }

সাধারণ অ্যাসাইনমেন্ট সিনট্যাক্স দিয়ে, অথবা `default` আর্গুমেন্টে একটি মান দিয়ে
ফিল্ডের ডিফল্ট মান দেওয়া যায়:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    # Both fields aren't required:
    name: str = 'John Doe'
    age: int = Field(default=20)
```

/// info | v2-তে পরিবর্তিত হয়েছে
[Pydantic V1-এ](../migration.md#required-optional-and-nullable-fields), [`Any`][typing.Any] হিসেবে অ্যানোটেট করা
বা [`Optional`][typing.Optional] দিয়ে মোড়ানো টাইপকে, স্পষ্টভাবে কোনো ডিফল্ট না দিলেও, অন্তর্নিহিতভাবে `None` ডিফল্ট দেওয়া হতো।
Pydantic V2-তে আর তা হয় না।
///

ডিফল্ট মান তৈরির জন্য কল হবে এমন একটি callable `default_factory` আর্গুমেন্টে দিতেও পারেন:

```python
from uuid import uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
```

(এখানে প্রতিটি নতুন `User`-এর জন্য `uuid4().hex` আবার কল হয়, ফলে প্রত্যেকে আলাদা একটি `id` পায়। সাধারণ `default=` দিলে সবাই একই মান পেত।)

<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#default-factory-validated-data}{% endraw %}

default factory একটি বাধ্যতামূলক আর্গুমেন্টও নিতে পারে, সেই ক্ষেত্রে ইতিমধ্যে যাচাই করা ডেটা একটি ডিকশনারি হিসেবে দেওয়া হবে।

```python
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data['email'])


user = User(email='user@example.com')
print(user.username)
#> user@example.com
```

`data` আর্গুমেন্টে [মডেলের ফিল্ডের ক্রম](./models.md#field-ordering) অনুযায়ী *শুধু* ইতিমধ্যে যাচাই করা ডেটা থাকবে
(`username` যদি `email`-এর আগে সংজ্ঞায়িত হতো, তাহলে ওপরের উদাহরণ ব্যর্থ হতো)।

/// info | v2.10-এ যোগ হয়েছে
default factory ইতিমধ্যে যাচাই করা ডেটা আর্গুমেন্ট হিসেবে নিতে পারে।
///

/// info | v2.13-এ যোগ হয়েছে
[private অ্যাট্রিবিউটের](./models.md#private-model-attributes) default factory যাচাই করা ডেটা আর্গুমেন্ট হিসেবে নিতে পারে।
///

## ডিফল্ট মান যাচাই করা { #validate-default-values }

ডিফল্টভাবে Pydantic ডিফল্ট মান যাচাই *করে না*। এই আচরণ চালু করতে `validate_default` ফিল্ড প্যারামিটার
(অথবা [`validate_default`][pydantic.ConfigDict.validate_default] configuration মান) ব্যবহার করা যায়:

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    age: int = Field(default='twelve', validate_default=True)


try:
    user = User()
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    age
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='twelve', input_type=str]
    """
```

(ডিফল্ট `'twelve'` একটি `int` নয়; `validate_default=True` না থাকলে ভুল ডিফল্টটি চুপচাপ বসে যেত।)

### পরিবর্তনযোগ্য ডিফল্ট মান { #mutable-default-values }

Python-এ বাগের একটি প্রচলিত উৎস হলো ফাংশন বা মেথডের আর্গুমেন্টের ডিফল্ট মান হিসেবে একটি পরিবর্তনযোগ্য অবজেক্ট (যেমন `[]` বা `{}`) ব্যবহার করা,
কারণ প্রতিটি কলে একই ইনস্ট্যান্স আবার ব্যবহার হয়।

[`dataclasses`][dataclasses] মডিউল আসলে এই ক্ষেত্রে একটি এরর দেয়, যা বোঝায় যে এর বদলে একটি
[default factory](https://docs.python.org/3/library/dataclasses.html#default-factory-functions) ব্যবহার করা উচিত।

Pydantic-এও একই কাজ করা যায়, কিন্তু তা বাধ্যতামূলক নয়। ডিফল্ট মান যদি hashable না হয়,
তাহলে মডেলের প্রতিটি ইনস্ট্যান্স তৈরির সময় Pydantic ডিফল্ট মানের একটি deep copy তৈরি করবে:

```python
from pydantic import BaseModel


class Model(BaseModel):
    item_counts: list[dict[str, int]] = [{}]


m1 = Model()
m1.item_counts[0]['a'] = 1
print(m1.item_counts)
#> [{'a': 1}]

m2 = Model()
print(m2.item_counts)
#> [{}]
```

(`m1`-এর তালিকা বদলালেও `m2` তার নিজের নতুন `[{}]` পায়। তাই Pydantic মডেলে `items: list = []` লেখা নিরাপদ।)

## ফিল্ডের alias { #field-aliases }

/// tip | পরামর্শ

alias নিয়ে আরও পড়ুন [নির্দিষ্ট অংশে](./alias.md)।

///

যাচাই আর সিরিয়ালাইজেশনের জন্য, একটি ফিল্ডের alias (বিকল্প নাম) সংজ্ঞায়িত করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

Python-এ নাম লেখা হয় `user_name` এভাবে, কিন্তু অনেক JavaScript API পাঠায় `userName` বা `username`। alias হলো ডাকনাম: কোডের ভেতরে ফিল্ডের আসল নাম `name`, কিন্তু বাইরের দুনিয়ার সাথে কথা বলার সময় (JSON পড়া বা লেখা) ডাকনাম `username` ব্যবহার হয়।

///

alias সংজ্ঞায়িত করার তিনটি উপায় আছে:

* `Field(alias='foo')`
* `Field(validation_alias='foo')`
* `Field(serialization_alias='foo')`

`alias` প্যারামিটার যাচাই *এবং* সিরিয়ালাইজেশন দুটোর জন্যই ব্যবহার হয়। যদি যাচাই আর সিরিয়ালাইজেশনের জন্য
*ভিন্ন* alias ব্যবহার করতে চান, তাহলে `validation_alias`
আর `serialization_alias` প্যারামিটার ব্যবহার করতে পারেন, যেগুলো শুধু তাদের নিজ নিজ ক্ষেত্রে প্রযোজ্য।

`alias` প্যারামিটার ব্যবহারের একটি উদাহরণ:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(alias='username')


user = User(username='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'username': 'johndoe'}
```

1. alias `'username'` ইনস্ট্যান্স তৈরি আর যাচাইয়ে ব্যবহার হয়।
2. মডেলকে সিরিয়ালাইজযোগ্য রূপে রূপান্তর করতে আমরা [`model_dump()`][pydantic.main.BaseModel.model_dump] ব্যবহার করছি।

    লক্ষ্য করুন, `by_alias` keyword argument-এর ডিফল্ট `False`, আর ফিল্ডের (সিরিয়ালাইজেশন) alias ব্যবহার করে মডেল dump করতে
    এটি স্পষ্টভাবে দিতে হবে।

    মডেল স্তরে এই আচরণ কনফিগার করতে [`ConfigDict.serialize_by_alias`][pydantic.config.ConfigDict.serialize_by_alias]-ও
    ব্যবহার করতে পারেন।

    যখন `by_alias=True`, তখন সিরিয়ালাইজেশনে alias `'username'` ব্যবহার হয়।

যদি alias *শুধু* যাচাইয়ের জন্য ব্যবহার করতে চান, তাহলে `validation_alias` প্যারামিটার ব্যবহার করতে পারেন:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(validation_alias='username')


user = User(username='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'name': 'johndoe'}
```

1. যাচাইয়ের সময় validation alias `'username'` ব্যবহার হয়।
2. সিরিয়ালাইজেশনের সময় ফিল্ডের নাম `'name'` ব্যবহার হয়।

যদি শুধু *সিরিয়ালাইজেশনের* জন্য একটি alias সংজ্ঞায়িত করতে চান, তাহলে `serialization_alias` প্যারামিটার ব্যবহার করতে পারেন:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(serialization_alias='username')


user = User(name='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'username': 'johndoe'}
```

1. যাচাইয়ের জন্য ফিল্ডের নাম `'name'` ব্যবহার হয়।
2. সিরিয়ালাইজেশনের জন্য serialization alias `'username'` ব্যবহার হয়।

/// note | alias-এর অগ্রাধিকার

যদি `alias` একই সাথে `validation_alias` বা `serialization_alias`-এর সাথে ব্যবহার করেন,
তাহলে যাচাইয়ের জন্য `validation_alias` `alias`-এর চেয়ে অগ্রাধিকার পাবে, আর সিরিয়ালাইজেশনের জন্য `serialization_alias`
`alias`-এর চেয়ে অগ্রাধিকার পাবে।

যদি [`alias_generator`][pydantic.config.ConfigDict.alias_generator] মডেল সেটিংয়ে একটি মান দেন, তাহলে `alias_priority` ফিল্ড প্যারামিটার দিয়ে ফিল্ডের alias আর তৈরি হওয়া alias-এর অগ্রাধিকারের ক্রম নিয়ন্ত্রণ করতে পারেন। alias-এর অগ্রাধিকার নিয়ে আরও পড়তে পারেন [এখানে](../concepts/alias.md#alias-precedence)।

///

/// details | স্ট্যাটিক টাইপ চেকিং/IDE সাপোর্ট
    type: tip

যদি `alias` ফিল্ড প্যারামিটারে একটি মান দেন, তাহলে স্ট্যাটিক টাইপ চেকার `__init__` মেথড তৈরিতে আসল ফিল্ডের নামের বদলে
এই alias ব্যবহার করবে:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(alias='username')


user = User(username='johndoe')  # (1)!
```

1. টাইপ চেকার গ্রহণ করে।

এর মানে, [`validate_by_name`][pydantic.config.ConfigDict.validate_by_name] মডেল সেটিং ব্যবহার করলে (যা মডেল যাচাইয়ের সময় ফিল্ডের নাম আর alias দুটোই ব্যবহারের অনুমতি দেয়), আসল ফিল্ডের নাম ব্যবহার করলে টাইপ চেকার এরর দেবে:

```python
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    name: str = Field(alias='username')


user = User(name='johndoe')  # (1)!
```

1. টাইপ চেকার গ্রহণ *করে না*।

যদি তবুও চান টাইপ চেকার alias নয়, ফিল্ডের নাম ব্যবহার করুক, তাহলে [Annotated প্যাটার্ন](#the-annotated-pattern)
ব্যবহার করা যায় (যা শুধু Pydantic বোঝে):

```python
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    name: Annotated[str, Field(alias='username')]


user = User(name='johndoe')  # (1)!
user = User(username='johndoe')  # (2)!
```

1. টাইপ চেকার গ্রহণ করে।
2. টাইপ চেকার গ্রহণ *করে না*।

<h3>Validation Alias</h3>

মডেল ইনস্ট্যান্স তৈরির সময় Pydantic `alias` আর `validation_alias`-কে একইভাবে গণ্য করলেও, টাইপ চেকার
শুধু `alias` ফিল্ড প্যারামিটার বোঝে। বিকল্প হিসেবে, এর বদলে একটি `alias` আর একটি
`serialization_alias` (ফিল্ডের নামের সমান) দুটোই দিতে পারেন, কারণ সিরিয়ালাইজেশনের সময় `serialization_alias` `alias`-কে
ওভাররাইড করবে:

```python
from pydantic import BaseModel, Field


class MyModel(BaseModel):
    my_field: int = Field(validation_alias='myValidationAlias')
```

এটি দিয়ে:

```python
from pydantic import BaseModel, Field


class MyModel(BaseModel):
    my_field: int = Field(
        alias='myValidationAlias',
        serialization_alias='my_field',
    )


m = MyModel(myValidationAlias=1)
print(m.model_dump(by_alias=True))
#> {'my_field': 1}
```

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#numeric-constraints}{% endraw %}
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#string-constraints}{% endraw %}
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#decimal-constraints}{% endraw %}

## ফিল্ডের শর্ত (Field constraints) { #field-constraints }

নির্দিষ্ট টাইপে শর্ত যোগ করতেও [`Field()`][pydantic.Field] ফাংশন ব্যবহার করা যায়:

```python
from decimal import Decimal

from pydantic import BaseModel, Field


class Model(BaseModel):
    positive: int = Field(gt=0)
    short_str: str = Field(max_length=3)
    precise_decimal: Decimal = Field(max_digits=5, decimal_places=2)
```

/// info | কোডটি সহজ ভাষায়

* `gt=0`: ০-এর চেয়ে বড় (greater than)। এর আত্মীয়: `ge` (বড় বা সমান), `lt` (ছোট), `le` (ছোট বা সমান)।
* `max_length=3`: স্ট্রিং সর্বোচ্চ ৩ অক্ষরের; এর জোড়া `min_length`।
* `max_digits=5, decimal_places=2`: `Decimal` মোট সর্বোচ্চ ৫ অঙ্কের, দশমিকের পরে সর্বোচ্চ ২ ঘর (যেমন `123.45`)।

///

প্রতিটি টাইপের জন্য উপলব্ধ শর্ত (আর সেগুলো JSON Schema-কে কীভাবে প্রভাবিত করে) বর্ণনা করা আছে
[স্ট্যান্ডার্ড লাইব্রেরি টাইপ](../api/standard_library_types.md) ডকুমেন্টেশনে।

/// note | নোট

একটি union টাইপে শর্ত যোগ করার সময়, union-এর কোনো সদস্য যদি `None` বা [`MISSING` sentinel](./types.md#missing-sentinel) হয়,
তাহলে শর্তগুলো স্বয়ংক্রিয়ভাবে union-এর বাকি টাইপ(গুলো)তে প্রয়োগ হবে:

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    positive: int | None = Field(gt=0)
    # Also works with the annotated pattern:
    negative: Annotated[int | None, Field(lt=0)]
```

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#strict-mode}{% endraw %}

## Strict ফিল্ড { #strict-fields }

[`Field()`][pydantic.Field] ফাংশনের `strict` প্যারামিটার নির্দিষ্ট করে ফিল্ডটি
[strict মোডে](./strict_mode.md) যাচাই হবে কিনা।

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(strict=True)
    age: int = Field(strict=False)  # (1)!


user = User(name='John', age='42')  # (2)!
print(user)
#> name='John' age=42
```

1. এটি ডিফল্ট মান।
2. `age` ফিল্ড lax মোডে যাচাই হয়। তাই এতে একটি স্ট্রিং দেওয়া যায় (`'42'` → `42`)।

[স্ট্যান্ডার্ড লাইব্রেরি টাইপ](../api/standard_library_types.md) ডকুমেন্টেশন প্রতিটি টাইপের strict আচরণ বর্ণনা করে।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#dataclass-constraints}{% endraw %}

## Dataclass ফিল্ড { #dataclass-fields }

[`Field()`][pydantic.Field] ফাংশনের কিছু প্যারামিটার [dataclass](./dataclasses.md)-এ ব্যবহার করা যায়:

* `init`: dataclass-এর তৈরি হওয়া `__init__()` মেথডে ফিল্ডটি অন্তর্ভুক্ত হবে কিনা।
* `init_var`: dataclass-এ ফিল্ডটি [init-only][dataclasses-init-only-variables] (শুধু তৈরির সময় দেওয়া, পরে রাখা হয় না) হবে কিনা।
* `kw_only`: dataclass-এর constructor-এ ফিল্ডটি শুধু keyword argument হিসেবে দেওয়া যাবে কিনা।

একটি উদাহরণ:

```python
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass
class Foo:
    bar: str
    baz: str = Field(init_var=True)
    qux: str = Field(kw_only=True)


class Model(BaseModel):
    foo: Foo


model = Model(foo=Foo('bar', baz='baz', qux='qux'))
print(model.model_dump())  # (1)!
#> {'foo': {'bar': 'bar', 'qux': 'qux'}}
```

1. `baz` ফিল্ড সিরিয়ালাইজ করা আউটপুটে নেই, কারণ এটি একটি init-only ফিল্ড।

## ফিল্ডের উপস্থাপন (Representation) { #field-representation }

মডেলের স্ট্রিং রূপে (যেমন `print(user)`) ফিল্ডটি অন্তর্ভুক্ত হবে কিনা তা নিয়ন্ত্রণ করতে `repr` প্যারামিটার
ব্যবহার করা যায়।

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(repr=True)  # (1)!
    age: int = Field(repr=False)


user = User(name='John', age=42)
print(user)
#> name='John'
```

1. এটি ডিফল্ট মান।

(পাসওয়ার্ড বা টোকেনের মতো সংবেদনশীল ফিল্ড লগে ছাপা এড়াতে `repr=False` কাজের।)

## Discriminator { #discriminator }

একটি union-এ ভিন্ন ভিন্ন মডেলের মধ্যে পার্থক্য করতে কোন ফিল্ড ব্যবহার হবে, তা নিয়ন্ত্রণ করতে `discriminator` প্যারামিটার ব্যবহার করা যায়।
এটি হয় একটি ফিল্ডের নাম, নয়তো একটি `Discriminator` ইনস্ট্যান্স নেয়। যখন union-এর সব মডেলে discriminator ফিল্ড একই নয়,
তখন `Discriminator` পদ্ধতি কাজে লাগতে পারে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি পোষা প্রাণীর ডেটা বিড়াল নাকি কুকুরের, তা `pet_type` ঘরটি দেখেই বলা যায়। discriminator হলো সেই "লেবেল" ঘর: Pydantic আগে লেবেলটি পড়ে, তারপর সরাসরি সঠিক মডেল দিয়ে যাচাই করে। সব মডেল একে একে চেষ্টা করতে হয় না, তাই এটি দ্রুত আর এরর বার্তাও পরিষ্কার হয়।

///

নিচের উদাহরণে একটি ফিল্ডের নাম দিয়ে `discriminator` ব্যবহার দেখানো হয়েছে:

```python
from typing import Literal

from pydantic import BaseModel, Field


class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int


class Dog(BaseModel):
    pet_type: Literal['dog']
    age: int


class Model(BaseModel):
    pet: Cat | Dog = Field(discriminator='pet_type')


print(Model.model_validate({'pet': {'pet_type': 'cat', 'age': 12}}))  # (1)!
#> pet=Cat(pet_type='cat', age=12)
```

1. `model_validate()` নিয়ে আরও দেখুন [ডেটা যাচাই](./models.md#validating-data) ডকুমেন্টেশনে।

নিচের উদাহরণে একটি `Discriminator` ইনস্ট্যান্সসহ `discriminator` keyword argument ব্যবহার দেখানো হয়েছে:

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Discriminator, Field, Tag


class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int


class Dog(BaseModel):
    pet_kind: Literal['dog']
    age: int


def pet_discriminator(v):
    if isinstance(v, dict):
        return v.get('pet_type', v.get('pet_kind'))
    return getattr(v, 'pet_type', getattr(v, 'pet_kind', None))


class Model(BaseModel):
    pet: Annotated[Cat, Tag('cat')] | Annotated[Dog, Tag('dog')] = Field(
        discriminator=Discriminator(pet_discriminator)
    )


print(repr(Model.model_validate({'pet': {'pet_type': 'cat', 'age': 12}})))
#> Model(pet=Cat(pet_type='cat', age=12))

print(repr(Model.model_validate({'pet': {'pet_kind': 'dog', 'age': 12}})))
#> Model(pet=Dog(pet_kind='dog', age=12))
```

(এখানে বিড়ালের লেবেল ঘরের নাম `pet_type`, কুকুরের `pet_kind`; তাই নিজস্ব ফাংশন `pet_discriminator` দুটোর যেকোনোটি পড়ে `'cat'` বা `'dog'` ফেরত দেয়, আর `Tag` দিয়ে বলা থাকে কোন লেবেলে কোন মডেল।)

discriminated union সংজ্ঞায়িত করতে `Annotated`-এর সুবিধাও নিতে পারেন।
আরও বিস্তারিত দেখুন [Discriminated Union](./unions.md#discriminated-unions) ডকুমেন্টেশনে।

## অপরিবর্তনীয়তা (Immutability) { #immutability }

frozen dataclass-এর আচরণ অনুকরণ করতে `frozen` প্যারামিটার ব্যবহার হয়। মডেল তৈরির পরে ফিল্ডে নতুন মান বসানো
আটকাতে (অপরিবর্তনীয়তা) এটি ব্যবহার হয়।

আরও বিস্তারিত জানতে [frozen dataclass-এর ডকুমেন্টেশন][frozen dataclass documentation] দেখুন।

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    name: str = Field(frozen=True)
    age: int


user = User(name='John', age=42)

try:
    user.name = 'Jane'  # (1)!
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      Field is frozen [type=frozen_field, input_value='Jane', input_type=str]
    """
```

1. যেহেতু `name` ফিল্ড frozen, তাই মান বসানো অনুমোদিত নয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#exclude}{% endraw %}

## ফিল্ড বাদ দেওয়া { #excluding-fields }

মডেল এক্সপোর্ট করার সময় কোন ফিল্ডগুলো বাদ যাবে তা নিয়ন্ত্রণ করতে `exclude` আর `exclude_if` প্যারামিটার ব্যবহার করা যায়।

নিচের উদাহরণ দেখুন:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(exclude=True)


user = User(name='John', age=42)
print(user.model_dump())  # (1)!
#> {'name': 'John'}
```

1. `age` ফিল্ড [`model_dump()`][pydantic.BaseModel.model_dump]-এর আউটপুটে নেই, কারণ এটি বাদ দেওয়া হয়েছে।

আরও বিস্তারিত জানতে নির্দিষ্ট [সিরিয়ালাইজেশন অংশ](./serialization.md#field-inclusion-and-exclusion) দেখুন।

/// info | v2.12-এ যোগ হয়েছে
`exclude_if` প্যারামিটার (একটি শর্ত সত্য হলেই শুধু বাদ দেওয়া, যেমন মান খালি হলে)।
///

## Deprecated ফিল্ড { #deprecated-fields }

/// info | v2.7.0-এ যোগ হয়েছে
///

একটি ফিল্ডকে deprecated (পুরনো, শীঘ্রই সরানো হবে) হিসেবে চিহ্নিত করতে `deprecated` প্যারামিটার ব্যবহার করা যায়। এতে:

* ফিল্ডটি ব্যবহার করলে চলমান অবস্থায় একটি deprecation সতর্কবার্তা দেখাবে।
* তৈরি হওয়া JSON schema-তে [deprecated](https://json-schema.org/draft/2020-12/json-schema-validation#section-9.3) keyword
  সেট হবে (ফলে FastAPI-র `/docs`-এ ফিল্ডটি কাটা দাগসহ দেখাবে)।

এই প্যারামিটার বিভিন্ন টাইপ গ্রহণ করে, যা নিচে বর্ণনা করা হলো।

### স্ট্রিং হিসেবে `deprecated` { #deprecated-as-a-string }

মানটি deprecation বার্তা হিসেবে ব্যবহার হবে।

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, Field(deprecated='This is deprecated')]


print(Model.model_json_schema()['properties']['deprecated_field'])
#> {'deprecated': True, 'title': 'Deprecated Field', 'type': 'integer'}
```

### `@warnings.deprecated` ডেকোরেটর দিয়ে `deprecated` { #deprecated-via-the-warningsdeprecated-decorator }

[`@warnings.deprecated`][warnings.deprecated] ডেকোরেটর (অথবা Python 3.12 আর তার আগের সংস্করণে
[`typing_extensions`-এর backport][typing_extensions.deprecated]) একটি ইনস্ট্যান্স হিসেবে
ব্যবহার করা যায়।

<!-- TODO: tabs should be auto-generated if using Ruff (https://github.com/pydantic/pydantic/issues/10083) -->

/// tab | Python 3.10 ও তার পরে

```python
from typing import Annotated

from typing_extensions import deprecated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, deprecated('This is deprecated')]

    # Or explicitly using `Field`:
    alt_form: Annotated[int, Field(deprecated=deprecated('This is deprecated'))]
```

///

/// tab | Python 3.13 ও তার পরে

```python
from typing import Annotated
from warnings import deprecated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, deprecated('This is deprecated')]

    # Or explicitly using `Field`:
    alt_form: Annotated[int, Field(deprecated=deprecated('This is deprecated'))]
```

///

/// note | `category` আর `stacklevel`-এর সমর্থন

এই ফিচারের বর্তমান বাস্তবায়ন `deprecated` ডেকোরেটরের `category` আর `stacklevel`
আর্গুমেন্ট বিবেচনা করে না। এটি Pydantic-এর ভবিষ্যৎ কোনো সংস্করণে আসতে পারে।

///

### বুলিয়ান হিসেবে `deprecated` { #deprecated-as-a-boolean }

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, Field(deprecated=True)]


print(Model.model_json_schema()['properties']['deprecated_field'])
#> {'deprecated': True, 'title': 'Deprecated Field', 'type': 'integer'}
```

/// warning | validator-এর ভেতরে একটি deprecated ফিল্ড ব্যবহার করা

একটি validator-এর ভেতরে একটি deprecated ফিল্ড ব্যবহার করলে deprecation সতর্কবার্তা দেখাবে। এটি স্পষ্টভাবে উপেক্ষা করতে
[`catch_warnings`][warnings.catch_warnings] ব্যবহার করতে পারেন:

```python
import warnings

from typing_extensions import Self

from pydantic import BaseModel, Field, model_validator


class Model(BaseModel):
    deprecated_field: int = Field(deprecated='This is deprecated')

    @model_validator(mode='after')
    def validate_model(self) -> Self:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            self.deprecated_field = self.deprecated_field * 2
```

///

## JSON Schema নিজের মতো করা { #customizing-json-schema }

কিছু ফিল্ড প্যারামিটার শুধু তৈরি হওয়া JSON schema নিজের মতো করতে ব্যবহার হয়। প্যারামিটারগুলো হলো:

* `title` (শিরোনাম)
* `description` (বর্ণনা)
* `examples` (উদাহরণ)
* `json_schema_extra` (বাড়তি তথ্য)

ফিল্ড দিয়ে JSON schema নিজের মতো করা / বদলানো নিয়ে আরও পড়ুন JSON schema ডকসের [ফিল্ড-স্তরের কাস্টমাইজেশন][Customizing JSON Schema] অংশে।

(FastAPI-র `/docs`-এ ফিল্ডের পাশে যে বর্ণনা আর উদাহরণ দেখা যায়, সেগুলো এই প্যারামিটারগুলো থেকেই আসে।)

## `computed_field` ডেকোরেটর { #the-computed_field-decorator }

/// details | API ডকুমেন্টেশন
    type: info

[`@computed_field`][pydantic.fields.computed_field]<br>

///

/// info | v2.13-এ যোগ হয়েছে
ডেকোরেটরের `exclude_if` প্যারামিটার ব্যবহার করে computed ফিল্ডকে শর্তসাপেক্ষে সিরিয়ালাইজেশনের আউটপুট থেকে বাদ দেওয়া যায়।
///

একটি মডেল বা dataclass সিরিয়ালাইজ করার সময় [property][property] (বা
[cached property][functools.cached_property]) অন্তর্ভুক্ত করতে [`@computed_field`][pydantic.fields.computed_field] ডেকোরেটর ব্যবহার করা যায়।
property-টি JSON Schema-তেও (সিরিয়ালাইজেশন মোডে) অন্তর্ভুক্ত হবে।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বাক্সের দৈর্ঘ্য, প্রস্থ আর উচ্চতা জানা থাকলে আয়তন আলাদা করে লেখার দরকার নেই, হিসাব করে নেওয়া যায়। `@computed_field` ঠিক এটাই: ইনপুট হিসেবে নেওয়া হয় না, কিন্তু আউটপুটে (`model_dump()`, JSON) অন্য ফিল্ডগুলোর সাথে দেখা যায়।

///

/// note | নোট

অন্য ফিল্ড থেকে হিসাব করা ফিল্ডের জন্য, অথবা হিসাব করতে ব্যয়বহুল এমন ফিল্ডের জন্য
(যেগুলো [`@cached_property`][functools.cached_property] ব্যবহার করলে cache হয়) property কাজের হতে পারে।

তবে লক্ষ্য করুন, মোড়ানো property-র ওপর Pydantic কোনো বাড়তি যুক্তি প্রয়োগ *করবে না*
(যাচাই, cache বাতিল করা ইত্যাদি)।

///

একটি computed ফিল্ডসহ মডেলের জন্য (সিরিয়ালাইজেশন মোডে) তৈরি হওয়া JSON schema-র একটি উদাহরণ:

```python
from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property  # (1)!
    def volume(self) -> float:
        return self.width * self.height * self.depth


print(Box.model_json_schema(mode='serialization'))
"""
{
    'properties': {
        'width': {'title': 'Width', 'type': 'number'},
        'height': {'title': 'Height', 'type': 'number'},
        'depth': {'title': 'Depth', 'type': 'number'},
        'volume': {'readOnly': True, 'title': 'Volume', 'type': 'number'},
    },
    'required': ['width', 'height', 'depth', 'volume'],
    'title': 'Box',
    'type': 'object',
}
"""
```

1. নির্দিষ্ট না করলে, [`@computed_field`][pydantic.fields.computed_field] অন্তর্নিহিতভাবে মেথডটিকে
   একটি [`@property`][property]-তে রূপান্তর করবে। তবে টাইপ চেকিংয়ের জন্য স্পষ্টভাবে [`@property`][property] ডেকোরেটর
   ব্যবহার করাই ভালো।

একটি computed ফিল্ডসহ [`model_dump()`][pydantic.BaseModel.model_dump] মেথড ব্যবহারের একটি উদাহরণ:

```python
from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth


b = Box(width=1, height=2, depth=3)
print(b.model_dump())
#> {'width': 1.0, 'height': 2.0, 'depth': 3.0, 'volume': 6.0}
```

সাধারণ ফিল্ডের মতোই, computed ফিল্ডকেও deprecated হিসেবে চিহ্নিত করা যায়:

```python
from typing_extensions import deprecated

from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    @deprecated("'volume' is deprecated")
    def volume(self) -> float:
        return self.width * self.height * self.depth
```

[frozen dataclass documentation]: https://docs.python.org/3/library/dataclasses.html#frozen-instances
[Customizing JSON Schema]: json_schema.md#field-level-customization

/// check | সংক্ষেপে মনে রাখুন

* `Field(...)` বা `Annotated[T, Field(...)]` দিয়ে ফিল্ডে ডিফল্ট, শর্ত (`gt`, `max_length` ...), alias, `strict`, `frozen`, `exclude` ইত্যাদি যোগ করুন।
* প্রতিবার নতুন ডিফল্ট লাগলে `default_factory`।
* ভিন্ন নামে JSON পড়তে/লিখতে `alias`, `validation_alias`, `serialization_alias`; লেখার সময় `by_alias=True` মনে রাখবেন।
* হিসাব করা মান আউটপুটে দেখাতে `@computed_field` + `@property`।

///
