# JSON Schema { #json-schema }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema`][pydantic.json_schema]<br>

///

/// note | এই পেজে যা শিখবেন

* JSON Schema কী, আর Pydantic মডেল থেকে কীভাবে তা তৈরি হয়।
* `model_json_schema()` আর `TypeAdapter.json_schema()` ব্যবহার।
* ফিল্ড আর মডেল স্তরে schema নিজের মতো করা: title, description, examples, `json_schema_extra`।
* কাস্টম টাইপের schema, schema তৈরির পুরো প্রক্রিয়া বদলানো, আর `$ref` নিজের মতো করা।

///

/// tip | উদাহরণ দিয়ে বুঝি

JSON Schema হলো ডেটার একটি "নিয়মের বই", যা নিজেও JSON-এ লেখা: "এই অবজেক্টে `name` থাকবে, সেটি স্ট্রিং; `age` থাকবে, সেটি integer আর বাধ্যতামূলক"। যেকোনো ভাষার যেকোনো টুল এই নিয়মের বই পড়ে বুঝতে পারে আপনার ডেটা কেমন। FastAPI-র `/docs` পেজ, SDK জেনারেটর, এমনকি AI মডেলের "structured output", সবই এই JSON Schema পড়ে কাজ করে। Pydantic আপনার Python মডেল থেকে এই নিয়মের বই স্বয়ংক্রিয়ভাবে লিখে দেয়।

///

Pydantic মডেল থেকে স্বয়ংক্রিয়ভাবে JSON schema তৈরি আর নিজের মতো করার সুযোগ দেয়।
তৈরি হওয়া JSON schema নিচের স্পেসিফিকেশনগুলো মেনে চলে:

* [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/release-notes.html)
* [OpenAPI Specification v3.1.0](https://github.com/OAI/OpenAPI-Specification)।

## JSON Schema তৈরি করা { #generating-json-schema }

JSON schema তৈরি করতে নিচের ফাংশনগুলো ব্যবহার করুন:

* [`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] একটি মডেলের schema-র একটি JSON-যোগ্য dict ফেরত দেয়।
* [`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] একটি adapt করা টাইপের schema-র একটি JSON-যোগ্য dict ফেরত দেয়।

/// note | নোট

এই মেথডগুলোকে [`BaseModel.model_dump_json`][pydantic.main.BaseModel.model_dump_json]
আর [`TypeAdapter.dump_json`][pydantic.type_adapter.TypeAdapter.dump_json]-এর সাথে গুলিয়ে ফেলবেন না, যেগুলো যথাক্রমে
মডেল বা adapt করা টাইপের ইনস্ট্যান্স (আসল ডেটা) সিরিয়ালাইজ করে। ওই মেথডগুলো JSON স্ট্রিং ফেরত দেয়। তুলনায়,
[`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] আর
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] যথাক্রমে মডেল বা adapt করা টাইপের JSON schema (ডেটার নিয়ম)
বোঝায় এমন একটি JSON-যোগ্য dict ফেরত দেয়।

///

/// note | JSON schema-র "JSON-যোগ্য" প্রকৃতি নিয়ে

[`model_json_schema`][pydantic.main.BaseModel.model_json_schema]-এর ফলাফলের "JSON-যোগ্য" প্রকৃতি সম্পর্কে বলতে গেলে,
কোনো `BaseModel` `m`-এর ওপর `json.dumps(m.model_json_schema())` কল করলে একটি বৈধ JSON স্ট্রিং পাওয়া যায়। একইভাবে,
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema]-এর ক্ষেত্রে,
`json.dumps(TypeAdapter(<some_type>).json_schema())` কল করলে একটি বৈধ JSON স্ট্রিং পাওয়া যায়।

///

/// tip | পরামর্শ

Pydantic নিচের দুটোই সমর্থন করে:

1. [JSON Schema নিজের মতো করা](#customizing-json-schema)
2. [JSON Schema তৈরির প্রক্রিয়া নিজের মতো করা](#customizing-the-json-schema-generation-process)

প্রথম পদ্ধতির পরিধি সাধারণত সংকীর্ণ, এটি আরও নির্দিষ্ট ক্ষেত্র আর টাইপের জন্য JSON schema নিজের মতো করতে দেয়।
দ্বিতীয় পদ্ধতির পরিধি সাধারণত বড়, এটি সামগ্রিকভাবে JSON schema তৈরির প্রক্রিয়া নিজের মতো করতে দেয়।
দুটো পদ্ধতিতেই একই ফল পাওয়া যায়, কিন্তু আপনার প্রয়োজন অনুযায়ী একটি অন্যটির চেয়ে সহজ সমাধান দিতে পারে।

///

একটি `BaseModel` থেকে JSON schema তৈরির একটি উদাহরণ:

```python
import json
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class FooBar(BaseModel):
    count: int
    size: float | None = None


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'


class MainModel(BaseModel):
    """
    This is the description of the main model
    """

    model_config = ConfigDict(title='Main')

    foo_bar: FooBar
    gender: Annotated[Gender | None, Field(alias='Gender')] = None
    snap: int = Field(
        default=42,
        title='The Snap',
        description='this is the value of snap',
        gt=30,
        lt=50,
    )


main_model_schema = MainModel.model_json_schema()  # (1)!
print(json.dumps(main_model_schema, indent=2))  # (2)!
```

JSON আউটপুট:

```json
{
  "$defs": {
    "FooBar": {
      "properties": {
        "count": {
          "title": "Count",
          "type": "integer"
        },
        "size": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Size"
        }
      },
      "required": [
        "count"
      ],
      "title": "FooBar",
      "type": "object"
    },
    "Gender": {
      "enum": [
        "male",
        "female",
        "other",
        "not_given"
      ],
      "title": "Gender",
      "type": "string"
    }
  },
  "description": "This is the description of the main model",
  "properties": {
    "foo_bar": {
      "$ref": "#/$defs/FooBar"
    },
    "Gender": {
      "anyOf": [
        {
          "$ref": "#/$defs/Gender"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "snap": {
      "default": 42,
      "description": "this is the value of snap",
      "exclusiveMaximum": 50,
      "exclusiveMinimum": 30,
      "title": "The Snap",
      "type": "integer"
    }
  },
  "required": [
    "foo_bar"
  ],
  "title": "Main",
  "type": "object"
}
```


1. এটি `MainModel`-এর schema-র একটি "JSON-যোগ্য" dict তৈরি করে।
2. schema dict-এর ওপর `json.dumps` কল করলে একটি JSON স্ট্রিং পাওয়া যায়।

/// info | আউটপুটটি সহজ ভাষায়

* `properties`: প্রতিটি ফিল্ড আর তার টাইপ। `snap`-এর জন্য `title`, `description`, `default` আর `gt`/`lt` থেকে আসা `exclusiveMinimum`/`exclusiveMaximum` সব দেখা যাচ্ছে।
* `required`: বাধ্যতামূলক ফিল্ড, এখানে শুধু `foo_bar`।
* `$defs`: নেস্টেড মডেল (`FooBar`) আর enum (`Gender`)-এর সংজ্ঞা আলাদা রাখা, আর `$ref` দিয়ে উল্লেখ করা।
* `description`: মডেলের docstring থেকে, আর `title`: `ConfigDict(title='Main')` থেকে।
* `Gender` ফিল্ডটি alias দিয়ে লেখা, কারণ schema ডিফল্টভাবে alias ব্যবহার করে।

///

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ক্লাস দিয়ে যেকোনো টাইপের জন্য যাচাই, সিরিয়ালাইজ
আর JSON schema তৈরির মেথডসহ একটি অবজেক্ট তৈরি করা যায়। এটি Pydantic V1-এর `schema_of`-এর
(যা এখন deprecated) সম্পূর্ণ বিকল্প।

একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] থেকে JSON schema তৈরির একটি উদাহরণ:

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

[`BaseModel`][pydantic.main.BaseModel] আর [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর সমন্বয়ের জন্যও
JSON schema তৈরি করতে পারেন, যেমন এই উদাহরণে দেখানো হয়েছে:

```python
import json

from pydantic import BaseModel, TypeAdapter


class Cat(BaseModel):
    name: str
    color: str


class Dog(BaseModel):
    name: str
    breed: str


ta = TypeAdapter(Cat | Dog)
ta_schema = ta.json_schema()
print(json.dumps(ta_schema, indent=2))
```

JSON আউটপুট:

```json
{
  "$defs": {
    "Cat": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "color": {
          "title": "Color",
          "type": "string"
        }
      },
      "required": [
        "name",
        "color"
      ],
      "title": "Cat",
      "type": "object"
    },
    "Dog": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "breed": {
          "title": "Breed",
          "type": "string"
        }
      },
      "required": [
        "name",
        "breed"
      ],
      "title": "Dog",
      "type": "object"
    }
  },
  "anyOf": [
    {
      "$ref": "#/$defs/Cat"
    },
    {
      "$ref": "#/$defs/Dog"
    }
  ]
}
```

(`Cat | Dog` union-এর জন্য schema-তে `anyOf` এসেছে, অর্থাৎ "এদের যেকোনো একটি"।)

### `JsonSchemaMode` কনফিগার করা { #configuring-the-jsonschemamode }

[`model_json_schema`][pydantic.main.BaseModel.model_json_schema] আর
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] মেথডের `mode` প্যারামিটার দিয়ে JSON schema তৈরির মোড
নির্দিষ্ট করুন। ডিফল্টভাবে মোড `'validation'`, যা মডেলের যাচাইয়ের schema-র সাথে মেলে এমন JSON schema তৈরি করে।

[`JsonSchemaMode`][pydantic.json_schema.JsonSchemaMode] হলো একটি টাইপ alias, যা `mode` প্যারামিটারের উপলব্ধ অপশনগুলো বোঝায়:

* `'validation'` (ইনপুট হিসেবে কী গ্রহণ করা হয়)
* `'serialization'` (আউটপুট হিসেবে কী বের হয়)

`mode` প্যারামিটার কীভাবে নির্দিষ্ট করতে হয়, আর তা তৈরি হওয়া JSON schema-কে কীভাবে প্রভাবিত করে, তার একটি উদাহরণ:

```python
from decimal import Decimal

from pydantic import BaseModel


class Model(BaseModel):
    a: Decimal = Decimal('12.34')


print(Model.model_json_schema(mode='validation'))
"""
{
    'properties': {
        'a': {
            'anyOf': [{'type': 'number'}, {'type': 'string'}],
            'default': '12.34',
            'title': 'A',
        }
    },
    'title': 'Model',
    'type': 'object',
}
"""

print(Model.model_json_schema(mode='serialization'))
"""
{
    'properties': {'a': {'default': '12.34', 'title': 'A', 'type': 'string'}},
    'title': 'Model',
    'type': 'object',
}
"""
```

(`Decimal` ইনপুটে সংখ্যা বা স্ট্রিং দুটোই গ্রহণ করে, তাই validation schema-তে `anyOf`; কিন্তু আউটপুটে সবসময় স্ট্রিং হিসেবে বের হয়, তাই serialization schema-তে শুধু `string`।)

## JSON Schema নিজের মতো করা { #customizing-json-schema }

তৈরি হওয়া JSON schema [ফিল্ড স্তরে](#field-level-customization) আর [মডেল স্তরে](#model-level-customization) দুই জায়গাতেই নিজের মতো করা যায়।

ফিল্ড আর মডেল দুই স্তরেই JSON schema-তে বাড়তি তথ্য যোগ করতে [`json_schema_extra` অপশন](#using-json_schema_extra) ব্যবহার করতে পারেন।

কাস্টম টাইপের জন্য, JSON schema তৈরি নিজের মতো করতে Pydantic অন্যান্য টুল দেয়:

1. [`WithJsonSchema` অ্যানোটেশন](#withjsonschema-annotation)
2. [`SkipJsonSchema` অ্যানোটেশন](#skipjsonschema-annotation)
3. [`__get_pydantic_core_schema__` বাস্তবায়ন](#implementing_get_pydantic_core_schema)
4. [`__get_pydantic_json_schema__` বাস্তবায়ন](#implementing_get_pydantic_json_schema)

### ফিল্ড-স্তরের কাস্টমাইজেশন { #field-level-customization }

[ফিল্ডের](./fields.md) JSON Schema নিজের মতো করা যায়। এটি সাধারণত [`Field()`][pydantic.fields.Field]
ফাংশন দিয়ে করা হয়।

কিছু ফিল্ড প্যারামিটার শুধু তৈরি হওয়া JSON Schema নিজের মতো করতে ব্যবহার হয়:

* `title`: ফিল্ডের শিরোনাম।
* `description`: ফিল্ডের বর্ণনা।
* `examples`: ফিল্ডের উদাহরণ।
* `json_schema_extra`: ফিল্ডে যোগ করার বাড়তি JSON Schema প্রপার্টি ([নির্দিষ্ট ডকুমেন্টেশন](#using-json_schema_extra) দেখুন)।
* `field_title_generator`: একটি ফাংশন, যা ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে ফিল্ডের শিরোনাম সেট করে।

একটি উদাহরণ:

```python
import json
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, SecretStr


class User(BaseModel):
    age: int = Field(description='Age of the user')
    email: Annotated[EmailStr, Field(examples=['marcelo@mail.com'])]  # (1)!
    name: str = Field(title='Username')
    password: SecretStr = Field(
        json_schema_extra={
            'title': 'Password',
            'description': 'Password of the user',
            'examples': ['123456'],
        }
    )


print(json.dumps(User.model_json_schema(), indent=2))
```

JSON আউটপুট:

```json
{
  "properties": {
    "age": {
      "description": "Age of the user",
      "title": "Age",
      "type": "integer"
    },
    "email": {
      "examples": [
        "marcelo@mail.com"
      ],
      "format": "email",
      "title": "Email",
      "type": "string"
    },
    "name": {
      "title": "Username",
      "type": "string"
    },
    "password": {
      "description": "Password of the user",
      "examples": [
        "123456"
      ],
      "format": "password",
      "title": "Password",
      "type": "string",
      "writeOnly": true
    }
  },
  "required": [
    "age",
    "email",
    "name",
    "password"
  ],
  "title": "User",
  "type": "object"
}
```


1. [Annotated প্যাটার্নও](./fields.md#the-annotated-pattern) ব্যবহার করা যায়।

(লক্ষ্য করুন, `SecretStr` পাসওয়ার্ড ফিল্ড schema-তে `"writeOnly": true` আর `"format": "password"` পেয়েছে, অর্থাৎ এটি শুধু পাঠানো যায়, ফেরত দেখানো হয় না।)

### প্রোগ্রাম দিয়ে ফিল্ডের শিরোনাম তৈরি { #programmatic-field-title-generation }

ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে শিরোনাম তৈরি করতে `field_title_generator` প্যারামিটার ব্যবহার করা যায়।

নিচের উদাহরণ দেখুন:

```python
import json

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo


def make_title(field_name: str, field_info: FieldInfo) -> str:
    return field_name.upper()


class Person(BaseModel):
    name: str = Field(field_title_generator=make_title)
    age: int = Field(field_title_generator=make_title)


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "NAME",
      "type": "string"
    },
    "age": {
      "title": "AGE",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
"""
```

### মডেল-স্তরের কাস্টমাইজেশন { #model-level-customization }

একটি মডেলে JSON schema তৈরি নিজের মতো করতে [model config][pydantic.config.ConfigDict]-ও ব্যবহার করতে পারেন।
বিশেষ করে, নিচের config অপশনগুলো প্রাসঙ্গিক:

* [`title`][pydantic.config.ConfigDict.title]
* [`json_schema_extra`][pydantic.config.ConfigDict.json_schema_extra]
* [`json_schema_mode_override`][pydantic.config.ConfigDict.json_schema_mode_override]
* [`field_title_generator`][pydantic.config.ConfigDict.field_title_generator]
* [`model_title_generator`][pydantic.config.ConfigDict.model_title_generator]

### `json_schema_extra` ব্যবহার করা { #using-json_schema_extra }

JSON schema-তে বাড়তি তথ্য যোগ করতে `json_schema_extra` অপশন ব্যবহার করা যায়, হয়
[ফিল্ড স্তরে](#field-level-customization), নয়তো [মডেল স্তরে](#model-level-customization)।
`json_schema_extra`-তে একটি `dict` বা একটি `Callable` দিতে পারেন।

#### `dict` দিয়ে `json_schema_extra` ব্যবহার { #using-json_schema_extra-with-a-dict }

JSON schema-তে বাড়তি তথ্য যোগ করতে `json_schema_extra`-তে একটি `dict` দিতে পারেন:

```python
import json

from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    a: str

    model_config = ConfigDict(json_schema_extra={'examples': [{'a': 'Foo'}]})


print(json.dumps(Model.model_json_schema(), indent=2))
```

JSON আউটপুট:

```json
{
  "examples": [
    {
      "a": "Foo"
    }
  ],
  "properties": {
    "a": {
      "title": "A",
      "type": "string"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
```

(FastAPI-তে রিকোয়েস্ট বডির উদাহরণ `/docs`-এ দেখাতে ঠিক এভাবেই `examples` যোগ করা হয়।)

#### `Callable` দিয়ে `json_schema_extra` ব্যবহার { #using-json_schema_extra-with-a-callable }

একটি ফাংশন দিয়ে JSON schema বদলাতে `json_schema_extra`-তে একটি `Callable` দিতে পারেন:

```python
import json

from pydantic import BaseModel, Field


def pop_default(s):
    s.pop('default')


class Model(BaseModel):
    a: int = Field(default=1, json_schema_extra=pop_default)


print(json.dumps(Model.model_json_schema(), indent=2))
```

JSON আউটপুট:

```json
{
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    }
  },
  "title": "Model",
  "type": "object"
}
```

(ফাংশনটি schema থেকে `default` মুছে দিয়েছে, তাই আউটপুটে `a`-এর ডিফল্ট দেখা যাচ্ছে না।)

#### `json_schema_extra` মিলিয়ে দেওয়া { #merging-json_schema_extra }

v2.9 থেকে, Pydantic অ্যানোটেট করা টাইপগুলোর `json_schema_extra` ডিকশনারিগুলো মিলিয়ে (merge করে) দেয়।
এই পদ্ধতি আগের ওভাররাইড আচরণের বদলে মেলানোর আরও যোগমূলক একটি পদ্ধতি দেয়।
একাধিক টাইপে json schema-র বাড়তি তথ্য পুনরায় ব্যবহারের ক্ষেত্রে এটি বেশ কাজের হতে পারে।

আমরা এই পরিবর্তনকে মূলত একটি বাগ ফিক্স হিসেবে দেখেছি, কারণ এটি `BaseModel` আর `TypeAdapter` ইনস্ট্যান্সের মধ্যে `json_schema_extra` মেলানোর আচরণে
অনিচ্ছাকৃত পার্থক্য দূর করে - আরও বিস্তারিত জানতে [এই issue](https://github.com/pydantic/pydantic/issues/9210)
দেখুন।

```python
import json
from typing import Annotated, TypeAlias

from pydantic import Field, TypeAdapter

ExternalType: TypeAlias = Annotated[
    int, Field(json_schema_extra={'key1': 'value1'})
]

ta = TypeAdapter(
    Annotated[ExternalType, Field(json_schema_extra={'key2': 'value2'})]
)
print(json.dumps(ta.json_schema(), indent=2))
"""
{
  "key1": "value1",
  "key2": "value2",
  "type": "integer"
}
"""
```

/// note | নোট

আমরা আর `dict` আর `callable` টাইপের `json_schema_extra` স্পেসিফিকেশনের মিশ্রণ সমর্থন করি না (আর কখনো পুরোপুরি করিনি)।
যদি আপনার ক্ষেত্রে এটি একটি প্রয়োজন হয়, তাহলে অনুগ্রহ করে [একটি pydantic issue খুলুন](https://github.com/pydantic/pydantic/issues/new/choose) আর আপনার পরিস্থিতি ব্যাখ্যা করুন - জোরালো যুক্তি পেলে আমরা এই সিদ্ধান্ত আবার বিবেচনা করতে খুশি হব।

///

### `WithJsonSchema` অ্যানোটেশন { #withjsonschema-annotation }

/// tip | পরামর্শ

কাস্টম টাইপের জন্য [`__get_pydantic_json_schema__()` বাস্তবায়নের](#implementing_get_pydantic_json_schema) চেয়ে
[`WithJsonSchema`][pydantic.json_schema.WithJsonSchema] ব্যবহার করাই ভালো,
কারণ এটি আরও সহজ আর ভুলের সম্ভাবনা কম।

///

একটি টাইপের JSON Schema ওভাররাইড করার জন্য ব্যবহৃত একটি অ্যানোটেশন।

এটি কাজের যখন এমন একটি টাইপের জন্য JSON Schema সেট করতে চান যা ডিফল্টভাবে কোনো JSON Schema তৈরি করে না
(যেমন [`Callable`][collections.abc.Callable])। লক্ষ্য করুন, এটি টাইপটির পুরো তৈরি হওয়া JSON Schema ওভাররাইড করে
(নিচের উদাহরণে `'type'`-ও দিতে হয়েছে)।

```python
import json
from typing import Annotated

from pydantic import BaseModel, WithJsonSchema

MyInt = Annotated[
    int,
    WithJsonSchema({'type': 'integer', 'examples': [1, 0, -1]}),
]


class Model(BaseModel):
    a: MyInt


print(json.dumps(Model.model_json_schema(), indent=2))
```

JSON আউটপুট:

```json
{
  "properties": {
    "a": {
      "examples": [
        1,
        0,
        -1
      ],
      "title": "A",
      "type": "integer"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
```


আরও বিস্তারিত জানতে [API ডকুমেন্টেশন][pydantic.json_schema.WithJsonSchema] দেখুন।

/// note | নোট

[validator](./validators.md) যুক্ত ফিল্ডের JSON Schema সূক্ষ্মভাবে ঠিক করতে আপনি [`WithJsonSchema`][pydantic.json_schema.WithJsonSchema]
অ্যানোটেশন ব্যবহারে প্রলুব্ধ হতে পারেন। এর বদলে
[`json_schema_input_type` আর্গুমেন্ট](./validators.md#json-schema-and-field-validators) ব্যবহারের পরামর্শ দেওয়া হয়।

///

### `SkipJsonSchema` অ্যানোটেশন { #skipjsonschema-annotation }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema.SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema]<br>

///

তৈরি হওয়া JSON schema থেকে একটি অন্তর্ভুক্ত ফিল্ড (বা একটি ফিল্ডের স্পেসিফিকেশনের অংশ) বাদ দিতে [`SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema] অ্যানোটেশন
ব্যবহার করা যায়। আরও বিস্তারিত জানতে API ডকস দেখুন।

### `__get_pydantic_core_schema__` বাস্তবায়ন <a name="implementing_get_pydantic_core_schema"></a> { #implementing-get_pydantic_core_schema }

কাস্টম টাইপ (`field_name: TheType` বা `field_name: Annotated[TheType, ...]` হিসেবে ব্যবহৃত) আর `Annotated` মেটাডেটা
(`field_name: Annotated[int, SomeMetadata]` হিসেবে ব্যবহৃত)
`__get_pydantic_core_schema__` বাস্তবায়ন করে তৈরি হওয়া schema বদলাতে বা ওভাররাইড করতে পারে।
এই মেথড দুটি positional আর্গুমেন্ট পায়:

1. এই টাইপের সাথে সংশ্লিষ্ট টাইপ অ্যানোটেশন (তাই `TheType[T][int]`-এর ক্ষেত্রে এটি হবে `TheType[int]`)।
2. `__get_pydantic_core_schema__`-এর পরবর্তী বাস্তবায়নকারীকে কল করার জন্য একটি handler/callback।

handler ব্যবস্থাটি ঠিক [*wrap* ফিল্ড validator](validators.md#field-wrap-validator)-এর মতো কাজ করে।
এই ক্ষেত্রে ইনপুট হলো টাইপ আর আউটপুট একটি `core_schema`।

(core schema হলো Pydantic-এর ভেতরের "নির্দেশনার তালিকা", যা Rust ইঞ্জিন `pydantic-core` পড়ে যাচাই আর সিরিয়ালাইজ করে। JSON schema এই core schema থেকেই তৈরি হয়।)

একটি কাস্টম টাইপের উদাহরণ যা তৈরি হওয়া `core_schema` *ওভাররাইড* করে:

```python
from dataclasses import dataclass
from typing import Any

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


@dataclass
class CompressedString:
    dictionary: dict[int, str]
    text: list[int]

    def build(self) -> str:
        return ' '.join([self.dictionary[key] for key in self.text])

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        assert source is CompressedString
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @staticmethod
    def _validate(value: str) -> 'CompressedString':
        inverse_dictionary: dict[str, int] = {}
        text: list[int] = []
        for word in value.split(' '):
            if word not in inverse_dictionary:
                inverse_dictionary[word] = len(inverse_dictionary)
            text.append(inverse_dictionary[word])
        return CompressedString(
            {v: k for k, v in inverse_dictionary.items()}, text
        )

    @staticmethod
    def _serialize(value: 'CompressedString') -> str:
        return value.build()


class MyModel(BaseModel):
    value: CompressedString


print(MyModel.model_json_schema())
"""
{
    'properties': {'value': {'title': 'Value', 'type': 'string'}},
    'required': ['value'],
    'title': 'MyModel',
    'type': 'object',
}
"""
print(MyModel(value='fox fox fox dog fox'))
"""
value = CompressedString(dictionary={0: 'fox', 1: 'dog'}, text=[0, 0, 0, 1, 0])
"""

print(MyModel(value='fox fox fox dog fox').model_dump(mode='json'))
#> {'value': 'fox fox fox dog fox'}
```

/// info | কোডটি সহজ ভাষায়

`CompressedString` একটি নিজস্ব ক্লাস, যা একটি বাক্যকে শব্দের অভিধান আর সংখ্যার তালিকা হিসেবে সংকুচিত করে রাখে। `__get_pydantic_core_schema__` Pydantic-কে বলে দেয়: "ইনপুট হবে একটি স্ট্রিং (`str_schema()`), যাচাইয়ের পরে `_validate` দিয়ে সংকুচিত রূপে বানাও, আর সিরিয়ালাইজ করার সময় `_serialize` দিয়ে আবার স্ট্রিং বানাও"। ফলে JSON schema-তে ফিল্ডটি সাধারণ `string` হিসেবেই দেখায়।

///

যেহেতু Pydantic `CompressedString`-এর জন্য schema তৈরি করতে জানে না, তাই এর `__get_pydantic_core_schema__` মেথডে
`handler(source)` কল করলে একটি `pydantic.errors.PydanticSchemaGenerationError` এরর পেতেন।
বেশিরভাগ কাস্টম টাইপের ক্ষেত্রে এমনই হবে, তাই কাস্টম টাইপের জন্য প্রায় কখনোই `handler` কল করতে চাইবেন না।

`Annotated` মেটাডেটার প্রক্রিয়া প্রায় একই, শুধু সাধারণত `handler` কল করে
Pydantic-কে schema তৈরি সামলাতে দিতে পারেন।

```python
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler, ValidationError


@dataclass
class RestrictCharacters:
    alphabet: Sequence[str]

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not self.alphabet:
            raise ValueError('Alphabet may not be empty')
        schema = handler(
            source
        )  # get the CoreSchema from the type / inner constraints
        if schema['type'] != 'str':
            raise TypeError('RestrictCharacters can only be applied to strings')
        return core_schema.no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: str) -> str:
        if any(c not in self.alphabet for c in value):
            raise ValueError(
                f'{value!r} is not restricted to {self.alphabet!r}'
            )
        return value


class MyModel(BaseModel):
    value: Annotated[str, RestrictCharacters('ABC')]


print(MyModel.model_json_schema())
"""
{
    'properties': {'value': {'title': 'Value', 'type': 'string'}},
    'required': ['value'],
    'title': 'MyModel',
    'type': 'object',
}
"""
print(MyModel(value='CBA'))
#> value='CBA'

try:
    MyModel(value='XYZ')
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    value
      Value error, 'XYZ' is not restricted to 'ABC' [type=value_error, input_value='XYZ', input_type=str]
    """
```

(`RestrictCharacters('ABC')` আগে `handler(source)` দিয়ে স্বাভাবিক `str` schema নেয়, তারপর তার পরে নিজের যাচাই জুড়ে দেয়: স্ট্রিংয়ে শুধু A, B, C অক্ষর থাকতে পারবে।)

এ পর্যন্ত আমরা schema মুড়ে দিচ্ছিলাম, কিন্তু যদি শুধু এটিকে *বদলাতে* বা *উপেক্ষা* করতে চান, তাও করতে পারেন।

schema বদলাতে, প্রথমে handler কল করুন, তারপর ফলাফলটি পরিবর্তন করুন:

```python
from typing import Annotated, Any

from pydantic_core import ValidationError, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


class SmallString:
    def __get_pydantic_core_schema__(
        self,
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        schema = handler(source)
        assert schema['type'] == 'str'
        schema['max_length'] = 10  # modify in place
        return schema


class MyModel(BaseModel):
    value: Annotated[str, SmallString()]


try:
    MyModel(value='too long!!!!!')
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    value
      String should have at most 10 characters [type=string_too_long, input_value='too long!!!!!', input_type=str]
    """
```

/// tip | পরামর্শ

লক্ষ্য করুন, একটি schema আপনাকে *অবশ্যই* ফেরত দিতে হবে, এমনকি যদি শুধু সেটিকে জায়গায় বদলান।

///

schema পুরোপুরি ওভাররাইড করতে, handler কল না করে নিজের
`CoreSchema` ফেরত দিন:

```python
from typing import Annotated, Any

from pydantic_core import ValidationError, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


class AllowAnySubclass:
    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # we can't call handler since it will fail for arbitrary types
        def validate(value: Any) -> Any:
            if not isinstance(value, source):
                raise ValueError(
                    f'Expected an instance of {source}, got an instance of {type(value)}'
                )
            return value

        return core_schema.no_info_plain_validator_function(validate)


class Foo:
    pass


class Model(BaseModel):
    f: Annotated[Foo, AllowAnySubclass()]


print(Model(f=Foo()))
#> f=<__main__.Foo object at 0x0123456789ab>


class NotFoo:
    pass


try:
    Model(f=NotFoo())
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    f
      Value error, Expected an instance of <class '__main__.Foo'>, got an instance of <class '__main__.NotFoo'> [type=value_error, input_value=<__main__.NotFoo object at 0x0123456789ab>, input_type=NotFoo]
    """
```

### `__get_pydantic_json_schema__` বাস্তবায়ন <a name="implementing_get_pydantic_json_schema"></a> { #implementing-get_pydantic_json_schema }

তৈরি হওয়া json schema বদলাতে বা ওভাররাইড করতে `__get_pydantic_json_schema__`-ও বাস্তবায়ন করতে পারেন।
এই মেথড বদলালে শুধু JSON schema প্রভাবিত হয় - core schema নয়, যা যাচাই আর সিরিয়ালাইজেশনে ব্যবহার হয়।

তৈরি হওয়া JSON schema বদলানোর একটি উদাহরণ:

```python
import json
from typing import Any

from pydantic_core import core_schema as cs

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.json_schema import JsonSchemaValue


class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> cs.CoreSchema:
        return cs.typed_dict_schema(
            {
                'name': cs.typed_dict_field(cs.str_schema()),
                'age': cs.typed_dict_field(cs.int_schema()),
            },
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = [
            {
                'name': 'John Doe',
                'age': 25,
            }
        ]
        json_schema['title'] = 'Person'
        return json_schema


print(json.dumps(TypeAdapter(Person).json_schema(), indent=2))
```

JSON আউটপুট:

```json
{
  "examples": [
    {
      "age": 25,
      "name": "John Doe"
    }
  ],
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
```

(`Person` ক্লাসের core schema একটি typed dict হিসেবে সংজ্ঞায়িত, আর `__get_pydantic_json_schema__` তৈরি হওয়া JSON schema-তে শুধু একটি উদাহরণ আর শিরোনাম যোগ করে, যাচাইয়ের আচরণে কোনো প্রভাব না ফেলে।)

### `field_title_generator` ব্যবহার { #using-field_title_generator }

ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে শিরোনাম তৈরি করতে `field_title_generator` প্যারামিটার ব্যবহার করা যায়।
এটি ফিল্ড-স্তরের `field_title_generator`-এর মতো, কিন্তু `ConfigDict` অপশনটি ক্লাসের সব ফিল্ডে প্রয়োগ হবে।

নিচের উদাহরণ দেখুন:

```python
import json

from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    model_config = ConfigDict(
        field_title_generator=lambda field_name, field_info: field_name.upper()
    )
    name: str
    age: int


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "NAME",
      "type": "string"
    },
    "age": {
      "title": "AGE",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
"""
```

### `model_title_generator` ব্যবহার { #using-model_title_generator }

`model_title_generator` config অপশন `field_title_generator` অপশনের মতো, কিন্তু এটি মডেলের নিজের শিরোনামে প্রযোজ্য,
আর ইনপুট হিসেবে মডেল ক্লাস নেয়।

নিচের উদাহরণ দেখুন:

```python
import json

from pydantic import BaseModel, ConfigDict


def make_title(model: type) -> str:
    return f'Title-{model.__name__}'


class Person(BaseModel):
    model_config = ConfigDict(model_title_generator=make_title)
    name: str
    age: int


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Title-Person",
  "type": "object"
}
"""
```

## JSON schema-র টাইপ { #json-schema-types }

টাইপ, কাস্টম ফিল্ড টাইপ আর শর্ত (যেমন `max_length`) সংশ্লিষ্ট স্পেসিফিকেশনের ফরম্যাটে ম্যাপ করা হয়
নিচের অগ্রাধিকারের ক্রমে (যখন সমতুল্য কিছু পাওয়া যায়):

1. [JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core)
2. [JSON Schema Validation](https://json-schema.org/draft/2020-12/json-schema-validation)
3. [OpenAPI Data Types](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#data-types)
4. আরও জটিল `string` সাব-টাইপের জন্য Pydantic-এর সম্প্রসারণ সংজ্ঞায়িত করতে স্ট্যান্ডার্ড `format` JSON ফিল্ড ব্যবহার হয়।

Python বা Pydantic থেকে JSON schema-তে ফিল্ডের schema ম্যাপিং নিচের মতো করা হয়:

/// info | সারণির কলামগুলোর অর্থ

* **Python type**: আপনার মডেলে লেখা টাইপ।
* **JSON Schema Type**: JSON schema-তে কোন মৌলিক টাইপ হিসেবে দেখাবে (`string`, `integer`, `array` ইত্যাদি)।
* **Additional JSON Schema**: সাথে কোন বাড়তি তথ্য যোগ হবে (যেমন `"format": "email"`)।
* **Defined in**: নিয়মটি কোন স্ট্যান্ডার্ড থেকে এসেছে।
* **Notes**: বাড়তি মন্তব্য।

যেমন `EmailStr` হয়ে যায় `{"type": "string", "format": "email"}`, আর `PositiveInt` হয়ে যায় `{"type": "integer", "exclusiveMinimum": 0}`।

///

| Python type | JSON Schema Type | Additional JSON Schema | Defined in | Notes |
| - | - | - | - | - |
| `None` | `null` |  | JSON Schema Core | Same for `type(None)` or `Literal[None]` |
| `bool` | `boolean` |  | JSON Schema Core |  |
| `str` | `string` |  | JSON Schema Core |  |
| `float` | `number` |  | JSON Schema Core |  |
| `int` | `integer` |  | JSON Schema Validation |  |
| `dict` | `object` |  | JSON Schema Core |  |
| `list` | `array` | `{"items": {}}` | JSON Schema Core |  |
| `tuple-positional` | `array` | `{"items": {}}` | JSON Schema Core |  |
| `tuple-variable` | `array` | `{"items": {}}` | JSON Schema Core |  |
| `set` | `array` | `{"uniqueItems": true, "items": {}}` | JSON Schema Validation |  |
| `frozenset` | `array` | `{"uniqueItems": true, "items": {}}` | JSON Schema Validation |  |
| `List[str]` | `array` | `{"items": {"type": "string"}}` | JSON Schema Validation | And equivalently for any other sub type, e.g. `List[int]`. |
| `Tuple[str, ...]` | `array` | `{"items": {"type": "string"}}` | JSON Schema Validation | And equivalently for any other sub type, e.g. `Tuple[int, ...]`. |
| `Tuple[str, int]` | `array` | `{"minItems": 2, "maxItems": 2, "items": [{"type": "string"}, {"type": "integer"}]}` | JSON Schema Validation | And equivalently for any other set of subtypes. Note: If using schemas for OpenAPI, you shouldn't use this declaration, as it would not be valid in OpenAPI (although it is valid in JSON Schema). |
| `Dict[str, int]` | `object` | `{"additionalProperties": {"type": "integer"}}` | JSON Schema Validation | And equivalently for any other subfields for dicts. Have in mind that although you can use other types as keys for dicts with Pydantic, only strings are valid keys for JSON, and so, only str is valid as JSON Schema key types. |
| `Union[str, int]` | `anyOf` | `{"anyOf": [{"type": "string"}, {"type": "integer"}]}` | JSON Schema Validation | And equivalently for any other subfields for unions. |
| `Enum` | `enum` | `{"enum": [...]}` | JSON Schema Validation | All the literal values in the enum are included in the definition. |
| `SecretStr` | `string` | `{"writeOnly": true}` | JSON Schema Validation |  |
| `SecretBytes` | `string` | `{"writeOnly": true}` | JSON Schema Validation |  |
| `EmailStr` | `string` | `{"format": "email"}` | JSON Schema Validation |  |
| `NameEmail` | `string` | `{"format": "name-email"}` | Pydantic standard "format" extension |  |
| `AnyUrl` | `string` | `{"format": "uri"}` | JSON Schema Validation |  |
| `Pattern` | `string` | `{"format": "regex"}` | JSON Schema Validation |  |
| `bytes` | `string` | `{"format": "binary"}` | OpenAPI |  |
| `Decimal` | `number` |  | JSON Schema Core |  |
| `UUID1` | `string` | `{"format": "uuid1"}` | Pydantic standard "format" extension |  |
| `UUID3` | `string` | `{"format": "uuid3"}` | Pydantic standard "format" extension |  |
| `UUID4` | `string` | `{"format": "uuid4"}` | Pydantic standard "format" extension |  |
| `UUID5` | `string` | `{"format": "uuid5"}` | Pydantic standard "format" extension |  |
| `UUID` | `string` | `{"format": "uuid"}` | Pydantic standard "format" extension | Suggested in OpenAPI. |
| `FilePath` | `string` | `{"format": "file-path"}` | Pydantic standard "format" extension |  |
| `DirectoryPath` | `string` | `{"format": "directory-path"}` | Pydantic standard "format" extension |  |
| `Path` | `string` | `{"format": "path"}` | Pydantic standard "format" extension |  |
| `datetime` | `string` | `{"format": "date-time"}` | JSON Schema Validation |  |
| `date` | `string` | `{"format": "date"}` | JSON Schema Validation |  |
| `time` | `string` | `{"format": "time"}` | JSON Schema Validation |  |
| `timedelta` | `number` | `{"format": "time-delta"}` | Difference in seconds (a `float`), with Pydantic standard "format" extension | Suggested in JSON Schema repository's issues by maintainer. |
| `Json` | `string` | `{"format": "json-string"}` | Pydantic standard "format" extension |  |
| `IPv4Address` | `string` | `{"format": "ipv4"}` | JSON Schema Validation |  |
| `IPv6Address` | `string` | `{"format": "ipv6"}` | JSON Schema Validation |  |
| `IPvAnyAddress` | `string` | `{"format": "ipvanyaddress"}` | Pydantic standard "format" extension | IPv4 or IPv6 address as used in `ipaddress` module |
| `IPv4Interface` | `string` | `{"format": "ipv4interface"}` | Pydantic standard "format" extension | IPv4 interface as used in `ipaddress` module |
| `IPv6Interface` | `string` | `{"format": "ipv6interface"}` | Pydantic standard "format" extension | IPv6 interface as used in `ipaddress` module |
| `IPvAnyInterface` | `string` | `{"format": "ipvanyinterface"}` | Pydantic standard "format" extension | IPv4 or IPv6 interface as used in `ipaddress` module |
| `IPv4Network` | `string` | `{"format": "ipv4network"}` | Pydantic standard "format" extension | IPv4 network as used in `ipaddress` module |
| `IPv6Network` | `string` | `{"format": "ipv6network"}` | Pydantic standard "format" extension | IPv6 network as used in `ipaddress` module |
| `IPvAnyNetwork` | `string` | `{"format": "ipvanynetwork"}` | Pydantic standard "format" extension | IPv4 or IPv6 network as used in `ipaddress` module |
| `StrictBool` | `boolean` |  | JSON Schema Core |  |
| `StrictStr` | `string` |  | JSON Schema Core |  |
| `ConstrainedStr` | `string` |  | JSON Schema Core | If the type has values declared for the constraints, they are included as validations. See the mapping for `constr` below. |
| `constr(pattern='^text$', min_length=2, max_length=10)` | `string` | `{"pattern": "^text$", "minLength": 2, "maxLength": 10}` | JSON Schema Validation | Any argument not passed to the function (not defined) will not be included in the schema. |
| `ConstrainedInt` | `integer` |  | JSON Schema Core | If the type has values declared for the constraints, they are included as validations. See the mapping for `conint` below. |
| `conint(gt=1, ge=2, lt=6, le=5, multiple_of=2)` | `integer` | `{"maximum": 5, "exclusiveMaximum": 6, "minimum": 2, "exclusiveMinimum": 1, "multipleOf": 2}` |  | Any argument not passed to the function (not defined) will not be included in the schema. |
| `PositiveInt` | `integer` | `{"exclusiveMinimum": 0}` | JSON Schema Validation |  |
| `NegativeInt` | `integer` | `{"exclusiveMaximum": 0}` | JSON Schema Validation |  |
| `NonNegativeInt` | `integer` | `{"minimum": 0}` | JSON Schema Validation |  |
| `NonPositiveInt` | `integer` | `{"maximum": 0}` | JSON Schema Validation |  |
| `ConstrainedFloat` | `number` |  | JSON Schema Core | If the type has values declared for the constraints, they are included as validations. See the mapping for `confloat` below. |
| `confloat(gt=1, ge=2, lt=6, le=5, multiple_of=2)` | `number` | `{"maximum": 5, "exclusiveMaximum": 6, "minimum": 2, "exclusiveMinimum": 1, "multipleOf": 2}` | JSON Schema Validation | Any argument not passed to the function (not defined) will not be included in the schema. |
| `PositiveFloat` | `number` | `{"exclusiveMinimum": 0}` | JSON Schema Validation |  |
| `NegativeFloat` | `number` | `{"exclusiveMaximum": 0}` | JSON Schema Validation |  |
| `NonNegativeFloat` | `number` | `{"minimum": 0}` | JSON Schema Validation |  |
| `NonPositiveFloat` | `number` | `{"maximum": 0}` | JSON Schema Validation |  |
| `ConstrainedDecimal` | `number` |  | JSON Schema Core | If the type has values declared for the constraints, they are included as validations. See the mapping for `condecimal` below. |
| `condecimal(gt=1, ge=2, lt=6, le=5, multiple_of=2)` | `number` | `{"maximum": 5, "exclusiveMaximum": 6, "minimum": 2, "exclusiveMinimum": 1, "multipleOf": 2}` | JSON Schema Validation | Any argument not passed to the function (not defined) will not be included in the schema. |
| `BaseModel` | `object` |  | JSON Schema Core | All the properties defined will be defined with standard JSON Schema, including submodels. |
| `Color` | `string` | `{"format": "color"}` | Pydantic standard "format" extension |  |


## শীর্ষ-স্তরের schema তৈরি { #top-level-schema-generation }

এমন একটি শীর্ষ-স্তরের JSON schema-ও তৈরি করতে পারেন, যার `$defs`-এ শুধু মডেলের একটি তালিকা আর সংশ্লিষ্ট
সাব-মডেলগুলো থাকে:

```python
import json

from pydantic import BaseModel
from pydantic.json_schema import models_json_schema


class Foo(BaseModel):
    a: str = None


class Model(BaseModel):
    b: Foo


class Bar(BaseModel):
    c: int


_, top_level_schema = models_json_schema(
    [(Model, 'validation'), (Bar, 'validation')], title='My Schema'
)
print(json.dumps(top_level_schema, indent=2))
```

JSON আউটপুট:

```json
{
  "$defs": {
    "Bar": {
      "properties": {
        "c": {
          "title": "C",
          "type": "integer"
        }
      },
      "required": [
        "c"
      ],
      "title": "Bar",
      "type": "object"
    },
    "Foo": {
      "properties": {
        "a": {
          "default": null,
          "title": "A",
          "type": "string"
        }
      },
      "title": "Foo",
      "type": "object"
    },
    "Model": {
      "properties": {
        "b": {
          "$ref": "#/$defs/Foo"
        }
      },
      "required": [
        "b"
      ],
      "title": "Model",
      "type": "object"
    }
  },
  "title": "My Schema"
}
```


## JSON Schema তৈরির প্রক্রিয়া নিজের মতো করা { #customizing-the-json-schema-generation-process }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema`][pydantic.json_schema.GenerateJsonSchema]<br>

///

যদি কাস্টম schema তৈরির দরকার হয়, তাহলে আপনার অ্যাপ্লিকেশনের প্রয়োজনমতো
[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] ক্লাস বদলে একটি `schema_generator` ব্যবহার করতে পারেন।

JSON schema তৈরির বিভিন্ন মেথড একটি keyword argument `schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema` গ্রহণ করে, আর JSON schema তৈরিতে নিজের পদ্ধতি ব্যবহার করতে এই মেথডগুলোতে আপনার কাস্টম সাব-ক্লাস দিতে পারেন।

`GenerateJsonSchema` একটি টাইপের `pydantic-core` schema-কে একটি JSON schema-তে রূপান্তর বাস্তবায়ন করে।
নকশা অনুযায়ী, এই ক্লাস JSON schema তৈরির প্রক্রিয়াকে ছোট ছোট মেথডে ভাগ করে, যেগুলো সাব-ক্লাসে সহজে ওভাররাইড করে
JSON schema তৈরির "সার্বিক" পদ্ধতি বদলানো যায়।

```python
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema


class MyGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema['title'] = 'Customize title'
        json_schema['$schema'] = self.schema_dialect
        return json_schema


class MyModel(BaseModel):
    x: int


print(MyModel.model_json_schema(schema_generator=MyGenerateJsonSchema))
"""
{
    'properties': {'x': {'title': 'X', 'type': 'integer'}},
    'required': ['x'],
    'title': 'Customize title',
    'type': 'object',
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
}
"""
```

(এখানে `generate` মেথড ওভাররাইড করে প্রতিটি schema-র শিরোনাম বদলানো আর `$schema` কী যোগ করা হয়েছে।)

যেসব ফিল্ডের বৈধ json schema নেই সেগুলো schema থেকে বাদ দিতে নিচের পদ্ধতি ব্যবহার করতে পারেন:

```python
from collections.abc import Callable

from pydantic_core import PydanticOmit, core_schema

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class MyGenerateJsonSchema(GenerateJsonSchema):
    def handle_invalid_for_json_schema(
        self, schema: core_schema.CoreSchema, error_info: str
    ) -> JsonSchemaValue:
        raise PydanticOmit


def example_callable():
    return 1


class Example(BaseModel):
    name: str = 'example'
    function: Callable = example_callable


instance_example = Example()

validation_schema = instance_example.model_json_schema(
    schema_generator=MyGenerateJsonSchema, mode='validation'
)
print(validation_schema)
"""
{
    'properties': {
        'name': {'default': 'example', 'title': 'Name', 'type': 'string'}
    },
    'title': 'Example',
    'type': 'object',
}
"""
```

(`Callable` টাইপের ফিল্ডের কোনো JSON schema হয় না; `handle_invalid_for_json_schema`-এ `PydanticOmit` raise করলে এরর না দিয়ে ফিল্ডটি চুপচাপ বাদ পড়ে।)

### JSON schema সাজানো (sorting) { #json-schema-sorting }

ডিফল্টভাবে, Pydantic key-গুলো বর্ণানুক্রমে সাজিয়ে JSON schema পুনরাবৃত্তভাবে সাজায়। উল্লেখযোগ্যভাবে, মডেলে ফিল্ডগুলো যে ক্রমে সংজ্ঞায়িত
তা বজায় রাখতে Pydantic `properties` key-এর মানগুলো সাজানো এড়িয়ে যায়।

এই আচরণ নিজের মতো করতে চাইলে, আপনার কাস্টম `GenerateJsonSchema` সাব-ক্লাসে `sort` মেথড ওভাররাইড করতে পারেন। নিচের উদাহরণে
সাজানো পুরোপুরি বন্ধ করতে একটি কিছু-না-করা `sort` মেথড ব্যবহার করা হয়েছে, যা মডেলের ফিল্ড আর `json_schema_extra` key-এর বজায় থাকা ক্রমে দেখা যায়:

```python
import json

from pydantic import BaseModel, Field
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class MyGenerateJsonSchema(GenerateJsonSchema):
    def sort(
        self, value: JsonSchemaValue, parent_key: str | None = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value


class Bar(BaseModel):
    c: str
    b: str
    a: str = Field(json_schema_extra={'c': 'hi', 'b': 'hello', 'a': 'world'})


json_schema = Bar.model_json_schema(schema_generator=MyGenerateJsonSchema)
print(json.dumps(json_schema, indent=2))
"""
{
  "type": "object",
  "properties": {
    "c": {
      "type": "string",
      "title": "C"
    },
    "b": {
      "type": "string",
      "title": "B"
    },
    "a": {
      "type": "string",
      "c": "hi",
      "b": "hello",
      "a": "world",
      "title": "A"
    }
  },
  "required": [
    "c",
    "b",
    "a"
  ],
  "title": "Bar"
}
"""
```

## JSON Schema-তে `$ref` নিজের মতো করা { #customizing-the-refs-in-json-schema }

[`model_json_schema()`][pydantic.main.BaseModel.model_json_schema]
বা [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]-কে `ref_template` keyword argument দিয়ে কল করে `$ref`-এর ফরম্যাট বদলানো যায়।
সংজ্ঞাগুলো সবসময় `$defs` key-এর নিচে রাখা হয়, কিন্তু রেফারেন্সের জন্য একটি নির্দিষ্ট উপসর্গ ব্যবহার করা যায়।

JSON schema-র ডিফল্ট সংজ্ঞার অবস্থান বাড়ানো বা বদলানোর প্রয়োজন হলে এটি কাজের। যেমন, OpenAPI-র ক্ষেত্রে:

```python
import json

from pydantic import BaseModel
from pydantic.type_adapter import TypeAdapter


class Foo(BaseModel):
    a: int


class Model(BaseModel):
    a: Foo


adapter = TypeAdapter(Model)

print(
    json.dumps(
        adapter.json_schema(ref_template='#/components/schemas/{model}'),
        indent=2,
    )
)
```

JSON আউটপুট:

```json
{
  "$defs": {
    "Foo": {
      "properties": {
        "a": {
          "title": "A",
          "type": "integer"
        }
      },
      "required": [
        "a"
      ],
      "title": "Foo",
      "type": "object"
    }
  },
  "properties": {
    "a": {
      "$ref": "#/components/schemas/Foo"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
```

(OpenAPI-তে মডেলগুলো থাকে `#/components/schemas/...`-এ, তাই `ref_template` দিয়ে `$ref`-গুলো সেই ঠিকানায় নির্দেশ করানো হয়েছে।)

## JSON Schema তৈরি নিয়ে বিবিধ নোট { #miscellaneous-notes-on-json-schema-generation }

* `Optional` ফিল্ডের JSON schema দেখায় যে `null` মান অনুমোদিত।
* `Decimal` টাইপ JSON schema-তে স্ট্রিং হিসেবে দেখানো (আর সিরিয়ালাইজ করা) হয়।
* যেহেতু JSON-এ `namedtuple` টাইপ নেই, তাই একটি মডেলের JSON schema `namedtuple`-কে `namedtuple` হিসেবে রাখে না।
* ব্যবহৃত সাব-মডেলগুলো স্পেসিফিকেশন অনুযায়ী `$defs` JSON অ্যাট্রিবিউটে যোগ হয় আর রেফারেন্স করা হয়।
* পরিবর্তনসহ (`Field` ক্লাস দিয়ে, যেমন কাস্টম শিরোনাম, বর্ণনা বা ডিফল্ট মান) সাব-মডেলগুলো রেফারেন্সের বদলে
    পুনরাবৃত্তভাবে অন্তর্ভুক্ত হয়।
* মডেলের `description` নেওয়া হয় ক্লাসের docstring থেকে, অথবা `Field` ক্লাসের `description`
    আর্গুমেন্ট থেকে।
* schema ডিফল্টভাবে key হিসেবে alias ব্যবহার করে তৈরি হয়, কিন্তু [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema] বা
    [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]-কে `by_alias=False` keyword argument দিয়ে কল করে
    মডেলের প্রপার্টির নাম ব্যবহার করেও তৈরি করা যায়।

/// check | সংক্ষেপে মনে রাখুন

* `Model.model_json_schema()` বা `TypeAdapter(T).json_schema()` দিয়ে JSON schema পাওয়া যায়।
* `mode='validation'` (ইনপুটের নিয়ম) আর `mode='serialization'` (আউটপুটের নিয়ম) ভিন্ন হতে পারে।
* `Field(title=..., description=..., examples=...)` আর `json_schema_extra` দিয়ে schema-তে তথ্য যোগ করুন।
* কাস্টম টাইপের জন্য সবচেয়ে সহজ `WithJsonSchema`; বড় পরিবর্তনের জন্য `GenerateJsonSchema` সাব-ক্লাস।

///
