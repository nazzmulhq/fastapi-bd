# BaseModel { #basemodel }

/// note | এই পেজে যা পাবেন

* `BaseModel`-এর প্রতিটি গুরুত্বপূর্ণ অ্যাট্রিবিউট আর মেথড, কাজ অনুযায়ী দলে ভাগ করে: মডেল তৈরি ও যাচাই, ডেটা বের করা (dump), কপি, JSON Schema, hook।
* প্রতিটি মেথডের প্যারামিটারের বাংলা সারণি আর চালানো যায় এমন উদাহরণ (আউটপুটসহ)।
* `create_model()` দিয়ে চলার সময় মডেল তৈরি।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা (ইংরেজিতে)।

///

Pydantic মডেল হলো এমন ক্লাস, যা `BaseModel` থেকে উত্তরাধিকার নেয় আর annotation দেওয়া অ্যাট্রিবিউট হিসেবে ফিল্ড সংজ্ঞায়িত করে।

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

`BaseModel` হলো একটি ছাঁচ (form template)। আপনি ঘরগুলো (ফিল্ড) আর প্রতিটি ঘরে কী ধরনের তথ্য যাবে (টাইপ) তা লেখেন। তারপর যে-ই ফর্ম পূরণ করুক (ডিকশনারি, JSON, অবজেক্ট), Pydantic মিলিয়ে দেখে, ঠিক রূপে বদলে দেয়, আর ভুল থাকলে কোন ঘরে কী ভুল তা জানায়। ফর্ম তৈরি হয়ে গেলে সেটিকে আবার ডিকশনারি বা JSON-এ (`model_dump`) বদলে অন্য কোথাও পাঠানো যায়।

///

| কাজ | সদস্য |
| --- | --- |
| মডেলের তথ্য (ক্লাসে) | `model_config`, `model_fields`, `model_computed_fields`, `__pydantic_core_schema__` |
| instance-এর তথ্য | `model_fields_set`, `model_extra` |
| তৈরি আর যাচাই | `__init__`, `model_validate()`, `model_validate_json()`, `model_validate_strings()`, `model_construct()` |
| ডেটা বের করা | `model_dump()`, `model_dump_json()` |
| কপি | `model_copy()` |
| JSON Schema | `model_json_schema()` |
| hook আর বিশেষ | `model_post_init()`, `model_rebuild()`, `model_parametrized_name()` |

এই পেজের সব উদাহরণে নিচের মডেলটি ব্যবহার হবে:

```python
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, computed_field


class Address(BaseModel):
    city: str
    zip_code: str | None = None


class User(BaseModel):
    model_config = ConfigDict(extra='allow')  # অচেনা ফিল্ডও রাখবে

    id: int
    name: str = Field(min_length=2)
    joined: date
    address: Address
    tags: list[str] = []

    @computed_field
    @property
    def display_name(self) -> str:
        return f'#{self.id} {self.name}'


u = User(id='7', name='রহিম', joined='2024-01-15', address={'city': 'ঢাকা'}, role='admin')
print(repr(u))
#> User(id=7, name='রহিম', joined=datetime.date(2024, 1, 15), address=Address(city='ঢাকা', zip_code=None), tags=[], role='admin', display_name='#7 রহিম')
```

## ক্লাসের অ্যাট্রিবিউট { #bn-class-attributes }

| অ্যাট্রিবিউট | কী রাখে |
| --- | --- |
| `model_config` | মডেলের কনফিগারেশন, একটি [`ConfigDict`](config.md) (যেমন `extra`, `strict`, `frozen`) |
| `model_fields` | ফিল্ডের নাম থেকে [`FieldInfo`](fields.md)-র ডিকশনারি: টাইপ, ডিফল্ট, alias, শর্ত |
| `model_computed_fields` | `@computed_field` দিয়ে বানানো ফিল্ডের তালিকা |
| `__pydantic_core_schema__` | ভেতরের core schema (দেখুন [Architecture](../internals/architecture.md)); সাধারণত দরকার হয় না |

```python
print(list(User.model_fields))
#> ['id', 'name', 'joined', 'address', 'tags']
print(list(User.model_computed_fields))
#> ['display_name']
print(User.model_fields['name'].metadata)
#> [MinLen(min_length=2)]
```

/// warning | সাধারণ ভুল

`model_fields` ক্লাস থেকে পড়ুন (`User.model_fields`), instance থেকে নয় (`u.model_fields`); instance থেকে পড়া নতুন সংস্করণে deprecated।

///

## instance-এর অ্যাট্রিবিউট { #bn-instance-attributes }

| অ্যাট্রিবিউট | কী রাখে |
| --- | --- |
| `model_fields_set` | যে ফিল্ডগুলো তৈরির সময় স্পষ্টভাবে দেওয়া হয়েছিল (ডিফল্ট থেকে আসা নয়) |
| `model_extra` | `extra='allow'` হলে অচেনা ফিল্ডগুলোর ডিকশনারি, নইলে `None` |

```python
print(u.model_fields_set)
#> {'id', 'name', 'joined', 'address', 'role'}  (ক্রম ভিন্ন হতে পারে; tags নেই, কারণ সেটি ডিফল্ট)
print(u.model_extra)
#> {'role': 'admin'}
```

## মডেল তৈরি আর যাচাই { #bn-validate }

| উপায় | ইনপুট | কখন |
| --- | --- | --- |
| `User(**data)` | keyword আর্গুমেন্ট | কোডে সরাসরি মান দিলে |
| `User.model_validate(obj)` | ডিকশনারি বা অবজেক্ট | API/ডেটাবেস থেকে পাওয়া ডিকশনারি; ORM অবজেক্ট (`from_attributes=True`) |
| `User.model_validate_json(text)` | JSON স্ট্রিং/bytes | JSON সরাসরি; `json.loads()`-এর চেয়ে দ্রুত |
| `User.model_validate_strings(obj)` | সব মান স্ট্রিং | ফর্ম, query string, CSV থেকে আসা ডেটা |
| `User.model_construct(**values)` | যেকোনো | **যাচাই ছাড়াই** তৈরি; শুধু বিশ্বস্ত, ইতিমধ্যে যাচাই হওয়া ডেটার জন্য |

`model_validate*` মেথডগুলোর প্যারামিটার:

| প্যারামিটার | কী করে |
| --- | --- |
| `strict` | `True` হলে টাইপ রূপান্তর বন্ধ ([Strict Mode](../concepts/strict_mode.md)) |
| `extra` | এই ডাকের জন্য বাড়তি ফিল্ডের নিয়ম: `'ignore'`, `'allow'`, `'forbid'` |
| `from_attributes` | ডিকশনারির বদলে অবজেক্টের অ্যাট্রিবিউট থেকে পড়া (শুধু `model_validate`) |
| `context` | validator-এ `info.context` হিসেবে পাঠানো বাড়তি তথ্য |
| `by_alias` / `by_name` | ইনপুটে alias দিয়ে নাকি ফিল্ডের নাম দিয়ে মান খোঁজা হবে |

```python
data = '{"id": 1, "name": "Ali", "joined": "2024-02-01", "address": {"city": "Khulna"}}'
print(User.model_validate_json(data).address.city)
#> Khulna

c = User.model_construct(id=1, name='x')  # name-এর min_length যাচাই হয়নি!
print(c.id, c.name)
#> 1 x
```

/// warning | `model_construct()` সাবধানে

`model_construct()` কোনো যাচাই বা রূপান্তর করে না, অনুপস্থিত বাধ্যতামূলক ফিল্ডও চুপচাপ বাদ রাখে। শুধু তখনই ব্যবহার করুন যখন ডেটা আগেই যাচাই হয়েছে (যেমন নিজের ডেটাবেস থেকে পড়া) আর গতি জরুরি।

///

## ডেটা বের করা: `model_dump()` আর `model_dump_json()` { #bn-dump }

`model_dump()` ডিকশনারি দেয়, `model_dump_json()` JSON স্ট্রিং দেয়। দুটোর প্রায় সব প্যারামিটার এক:

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `mode` (শুধু `model_dump`) | `'python'` | `'python'`: Python অবজেক্ট রাখে (`date`); `'json'`: JSON-যোগ্য রূপে (`'2024-01-15'`) |
| `include` / `exclude` | `None` | কোন ফিল্ড রাখবে/বাদ দেবে, যেমন `{'id', 'name'}`; নেস্টেড: `{'address': {'zip_code'}}` |
| `by_alias` | `None` | alias নামে key লিখবে কিনা |
| `exclude_unset` | `False` | যে ফিল্ড দেওয়া হয়নি (ডিফল্ট থেকে এসেছে) তা বাদ |
| `exclude_defaults` | `False` | যার মান ডিফল্টের সমান তা বাদ |
| `exclude_none` | `False` | `None` মানের ফিল্ড বাদ |
| `exclude_computed_fields` | `False` | `@computed_field` বাদ |
| `round_trip` | `False` | এমনভাবে dump যাতে আবার যাচাই করে একই মডেল পাওয়া যায় |
| `context` | `None` | serializer-এ পাঠানো বাড়তি তথ্য |
| `warnings` | `True` | টাইপ না মিললে সতর্কবার্তা দেবে কিনা (`'none'`, `'warn'`, `'error'`) |
| `fallback` | `None` | অচেনা টাইপ সিরিয়ালাইজ করার ফাংশন |
| `serialize_as_any` | `False` | subclass-এর বাড়তি ফিল্ডসহ dump (duck typing) |
| `indent` (শুধু `model_dump_json`) | `None` | JSON সুন্দর করে সাজাতে ফাঁকা জায়গা, যেমন `2` |
| `ensure_ascii` (শুধু `model_dump_json`) | `False` | `True` হলে বাংলার মতো non-ASCII অক্ষর `\uXXXX`-এ বদলে যায় |

```python
print(u.model_dump(mode='json', include={'id', 'joined'}))
#> {'id': 7, 'joined': '2024-01-15'}

print(u.model_dump(exclude_unset=True, exclude={'address'}))
#> {'id': 7, 'name': 'রহিম', 'joined': datetime.date(2024, 1, 15), 'role': 'admin', 'display_name': '#7 রহিম'}

print(u.model_dump_json(exclude={'address', 'tags', 'role'}))
#> {"id":7,"name":"রহিম","joined":"2024-01-15","display_name":"#7 রহিম"}
```

/// tip | উদাহরণ দিয়ে বুঝি

`exclude_unset=True` হলো "শুধু যা ব্যবহারকারী নিজে লিখেছেন"। PATCH রিকোয়েস্টে এটি খুব কাজের: শুধু পাঠানো ফিল্ডগুলো আপডেট করুন, বাকিগুলো ডিফল্ট দিয়ে মুছে যাবে না। ওপরের ফলে `tags` নেই, কারণ সেটি দেওয়া হয়নি।

///

## কপি: `model_copy()` { #bn-copy }

| প্যারামিটার | কী করে |
| --- | --- |
| `update` | নতুন কপিতে বদলানো মানের ডিকশনারি (**যাচাই হয় না**) |
| `deep` | `True` হলে নেস্টেড অবজেক্টসহ সম্পূর্ণ নতুন কপি; `False` হলে ভেতরের অবজেক্ট ভাগাভাগি |

```python
u2 = u.model_copy(update={'name': 'করিম'})
print(u2.name, u.name)
#> করিম রহিম
```

/// warning | সাধারণ ভুল

`update`-এর মান যাচাই হয় না; `update={'id': 'abc'}` দিলেও এরর হবে না। যাচাই চাইলে `User.model_validate(u.model_dump() | {'id': ...})` ব্যবহার করুন।

///

## JSON Schema: `model_json_schema()` { #bn-json-schema }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `by_alias` | `True` | schema-তে alias নাম ব্যবহার |
| `ref_template` | `'#/$defs/{model}'` | নেস্টেড মডেলের `$ref` ঠিকানার ছাঁচ |
| `schema_generator` | `GenerateJsonSchema` | নিজের মতো schema বানাতে subclass দিন |
| `mode` | `'validation'` | `'validation'`: ইনপুটের schema; `'serialization'`: আউটপুটের schema (computed field সহ) |
| `union_format` | `'any_of'` | union কীভাবে লিখবে: `'any_of'` বা `'primitive_type_array'` |

```python
print(User.model_json_schema()['required'])
#> ['id', 'name', 'joined', 'address']
```

বিস্তারিত: [JSON Schema](../concepts/json_schema.md)।

## hook আর বিশেষ মেথড { #bn-hooks }

| মেথড | কখন/কী |
| --- | --- |
| `model_post_init(self, context)` | যাচাই শেষ হওয়ার ঠিক পরে ডাকা হয়; বাড়তি প্রস্তুতি বা private অ্যাট্রিবিউট বসাতে override করুন |
| `model_rebuild()` | forward reference পরে সংজ্ঞায়িত হলে schema আবার তৈরি (দেখুন [Forward Annotations](../concepts/forward_annotations.md)) |
| `model_parametrized_name(params)` | generic মডেলের প্যারামিটারসহ নাম (`Response[int]`) কীভাবে হবে তা বদলাতে override |

```python
from pydantic import BaseModel, PrivateAttr


class Counter(BaseModel):
    start: int
    _value: int = PrivateAttr()

    def model_post_init(self, context) -> None:
        self._value = self.start  # যাচাইয়ের পরে private অবস্থা প্রস্তুত


print(Counter(start=5)._value)
#> 5
```

## `create_model()` { #bn-create-model }

চলার সময় নতুন মডেল ক্লাস তৈরি করে। ফিল্ড দেওয়া হয় keyword আর্গুমেন্টে: `name=(টাইপ, ডিফল্ট)` বা শুধু `name=টাইপ` (বাধ্যতামূলক)।

| প্যারামিটার | কী করে |
| --- | --- |
| `model_name` | নতুন ক্লাসের নাম |
| `__base__` | যে মডেল থেকে উত্তরাধিকার নেবে |
| `__config__` | `ConfigDict` (`__base__`-এর সাথে একসাথে নয়) |
| `__validators__` | validator ফাংশনের ডিকশনারি |
| `__doc__`, `__module__`, `__qualname__` | ক্লাসের docstring আর পরিচয় |
| `**field_definitions` | ফিল্ডগুলো |

```python
from pydantic import create_model

Product = create_model('Product', name=str, price=(float, 0.0))
print(Product(name='কলম', price='12.5'))
#> name='কলম' price=12.5
```

আরও উদাহরণ: [গতিশীল মডেল](../examples/dynamic_models.md)।

/// check | সংক্ষেপে মনে রাখুন

* তৈরি: `Model(**data)`, `Model.model_validate(dict)`, `Model.model_validate_json(text)`; যাচাই ছাড়া: `model_construct()`।
* বের করা: `model_dump(mode='json', exclude_unset=True, ...)`, `model_dump_json(indent=2)`।
* তথ্য: `Model.model_fields`, `m.model_fields_set`, `m.model_extra`।
* কপি: `m.model_copy(update={...})` (যাচাই ছাড়া)।
* schema: `Model.model_json_schema()`; hook: `model_post_init()`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.BaseModel
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        members:
        - __init__
        - model_config
        - model_fields
        - model_computed_fields
        - __pydantic_core_schema__
        - model_extra
        - model_fields_set
        - model_construct
        - model_copy
        - model_dump
        - model_dump_json
        - model_json_schema
        - model_parametrized_name
        - model_post_init
        - model_rebuild
        - model_validate
        - model_validate_json
        - model_validate_strings
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true

::: pydantic.create_model
    options:
        show_root_heading: true
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
