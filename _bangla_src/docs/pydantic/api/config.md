# Configuration { #configuration }

/// note | এই পেজে যা পাবেন

* `ConfigDict`-এর প্রতিটি সেটিং, কাজ অনুযায়ী দলে ভাগ করে, বাংলায় এক লাইনের ব্যাখ্যাসহ।
* `with_config` decorator, আর `to_camel`, `to_pascal`, `to_snake` alias generator।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

ফিল্ডের নিয়ম লেখা হয় প্রতিটি ঘরের পাশে (`Field()`), আর `ConfigDict` হলো পুরো ফর্মের ওপরে লেখা সাধারণ নির্দেশনা: "সব লেখার শুরু-শেষের ফাঁকা বাদ দাও", "অচেনা ঘর থাকলে ফেরত দাও", "পূরণের পরে আর বদলানো যাবে না"।

///

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Product(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, str_to_lower=True, extra='forbid', frozen=True)

    name: str


p = Product(name='  KOLOM ')
print(repr(p.name))
#> 'kolom'

try:
    Product(name='x', price=1)
except ValidationError as e:
    print(e.errors()[0]['type'])
    #> extra_forbidden

try:
    p.name = 'y'
except ValidationError as e:
    print(e.errors()[0]['type'])
    #> frozen_instance
```

## `ConfigDict` সেটিংস { #bn-configdict }

### স্ট্রিং { #bn-strings }

| সেটিং | কী করে |
| --- | --- |
| `str_strip_whitespace` | শুরু-শেষের ফাঁকা জায়গা বাদ |
| `str_to_lower` / `str_to_upper` | সব ছোট / বড় হাতের অক্ষরে |
| `str_min_length` / `str_max_length` | সব স্ট্রিংয়ের ন্যূনতম / সর্বোচ্চ দৈর্ঘ্য |
| `coerce_numbers_to_str` | `str` ফিল্ডে সংখ্যা দিলে স্ট্রিংয়ে বদলে নেবে |
| `regex_engine` | `pattern`-এর জন্য `'rust-regex'` (ডিফল্ট, দ্রুত) বা `'python-re'` (বেশি সুবিধা) |
| `cache_strings` | পুনরাবৃত্ত স্ট্রিং cache করে মেমোরি বাঁচানো |

### যাচাইয়ের আচরণ { #bn-validation }

| সেটিং | কী করে |
| --- | --- |
| `extra` | অচেনা ফিল্ড: `'ignore'` (ডিফল্ট, বাদ), `'allow'` (রাখো), `'forbid'` (এরর) |
| `strict` | পুরো মডেলে টাইপ রূপান্তর বন্ধ |
| `frozen` | তৈরির পরে বদলানো যাবে না (আর hash করা যাবে) |
| `validate_assignment` | `m.x = ...` বসানোর সময়ও যাচাই |
| `validate_default` | ডিফল্ট মানও যাচাই |
| `revalidate_instances` | ফিল্ডে মডেলের instance দিলে আবার যাচাই: `'never'`, `'always'`, `'subclass-instances'` |
| `from_attributes` | অবজেক্টের অ্যাট্রিবিউট থেকে পড়া (ORM) |
| `arbitrary_types_allowed` | অচেনা ক্লাস টাইপ হিসেবে অনুমোদন (শুধু `isinstance` পরীক্ষা) |
| `allow_inf_nan` | float-এ `inf`/`nan` অনুমোদন |
| `use_enum_values` | enum সদস্যের বদলে তার মান রাখা |
| `validate_return` | `validate_call`-এ ফেরত মানও যাচাই |
| `hide_input_in_errors` | এররের বার্তায় ইনপুট মান লুকানো (সংবেদনশীল ডেটার জন্য) |
| `validation_error_cause` | এররের মূল কারণ exception-এর `__cause__`-এ রাখা |
| `val_json_bytes` | JSON-এ `bytes` কীভাবে পড়বে: `'utf8'`, `'base64'`, `'hex'` |
| `val_temporal_unit` | সংখ্যা থেকে তারিখ পড়ার একক: `'seconds'`, `'milliseconds'`, `'infer'` |

### নাম আর alias { #bn-names }

| সেটিং | কী করে |
| --- | --- |
| `alias_generator` | সব ফিল্ডের alias বানানোর ফাংশন, যেমন `to_camel` |
| `validate_by_alias` | ইনপুটে alias দিয়ে খোঁজা (ডিফল্ট `True`) |
| `validate_by_name` | ইনপুটে ফিল্ডের আসল নাম দিয়েও খোঁজা |
| `serialize_by_alias` | dump-এ ডিফল্টভাবে alias ব্যবহার |
| `populate_by_name` | পুরনো; বদলে `validate_by_name` |
| `loc_by_alias` | এররের `loc`-এ alias দেখাবে কিনা |

### সিরিয়ালাইজেশন { #bn-serialization }

| সেটিং | কী করে |
| --- | --- |
| `ser_json_timedelta` | `timedelta` JSON-এ: `'iso8601'` বা `'float'` |
| `ser_json_temporal` | তারিখ/সময় JSON-এ: `'iso8601'`, `'seconds'`, `'milliseconds'` |
| `ser_json_bytes` | `bytes` JSON-এ: `'utf8'`, `'base64'`, `'hex'` |
| `ser_json_inf_nan` | `inf`/`nan` JSON-এ: `'null'`, `'constants'`, `'strings'` |
| `polymorphic_serialization` | subclass-এর বাড়তি ফিল্ডসহ dump |
| `url_preserve_empty_path` | URL-এর খালি path অপরিবর্তিত রাখা |
| `json_encoders` | পুরনো (deprecated); বদলে `@field_serializer` |

### JSON Schema আর ডকুমেন্টেশন { #bn-json-schema }

| সেটিং | কী করে |
| --- | --- |
| `title` | schema-র শিরোনাম |
| `model_title_generator` / `field_title_generator` | শিরোনাম বানানোর ফাংশন |
| `json_schema_extra` | schema-তে বাড়তি key |
| `json_schema_mode_override` | schema সবসময় `'validation'` বা `'serialization'` মোডে |
| `json_schema_serialization_defaults_required` | serialization schema-তে ডিফল্টওয়ালা ফিল্ডকেও `required` দেখানো |
| `use_attribute_docstrings` | ফিল্ডের নিচের docstring বর্ণনা হিসেবে ব্যবহার |

### উন্নত { #bn-advanced }

| সেটিং | কী করে |
| --- | --- |
| `defer_build` | schema তৈরি প্রথম ব্যবহার পর্যন্ত পিছিয়ে রাখা (অ্যাপ দ্রুত চালু হয়) |
| `ignored_types` | যে টাইপের ক্লাস অ্যাট্রিবিউট ফিল্ড হিসেবে ধরা হবে না |
| `protected_namespaces` | যে prefix দিয়ে ফিল্ডের নাম শুরু হলে সতর্কবার্তা (ডিফল্ট `model_validate`, `model_dump`) |
| `plugin_settings` | plugin-এর (যেমন Logfire) সেটিংস |
| `schema_generator` | পুরনো; ব্যবহার না করাই ভালো |

## `with_config` { #bn-with-config }

`BaseModel` নয় এমন ক্লাসে (`TypedDict`, stdlib dataclass) config দিতে decorator:

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, TypeAdapter, with_config


@with_config(ConfigDict(str_to_upper=True))
class Code(TypedDict):
    code: str


print(TypeAdapter(Code).validate_python({'code': 'bd'}))
#> {'code': 'BD'}
```

`BaseModel`-এ `with_config` ব্যবহার করবেন না; সেখানে `model_config` লিখুন।

## alias generator { #bn-alias-generators }

| ফাংশন | উদাহরণ |
| --- | --- |
| `to_camel` | `'user_id'` → `'userId'` |
| `to_pascal` | `'user_id'` → `'UserId'` |
| `to_snake` | `'UserId'` → `'user_id'` |

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Api(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    user_id: int
    full_name: str


a = Api.model_validate({'userId': 1, 'fullName': 'X'})
print(a.model_dump(by_alias=True), Api(user_id=2, full_name='Y').user_id)
#> {'userId': 1, 'fullName': 'X'} 2
```

বিস্তারিত: [Configuration](../concepts/config.md), [Alias](../concepts/alias.md)।

/// check | সংক্ষেপে মনে রাখুন

* `model_config = ConfigDict(...)` ক্লাসের ভেতরে।
* প্রায়ই লাগে: `extra`, `frozen`, `str_strip_whitespace`, `from_attributes`, `validate_assignment`, `alias_generator`।
* `TypedDict`/dataclass-এ `@with_config(...)`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.config
    options:
        group_by_category: false
        members:
        - ConfigDict
        - with_config
        - ExtraValues
        - BaseConfig
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

::: pydantic.alias_generators
    options:
        show_root_heading: true
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
