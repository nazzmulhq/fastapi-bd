# Pydantic Dataclasses { #pydantic-dataclasses }

/// note | এই পেজে যা পাবেন

* `@pydantic.dataclasses.dataclass` decorator-এর প্রতিটি প্যারামিটার।
* `rebuild_dataclass()` আর `is_pydantic_dataclass()` ফাংশন।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

`from dataclasses import dataclass`-এর জায়গায় `from pydantic.dataclasses import dataclass` লিখলে সাধারণ dataclass-এ Pydantic-এর যাচাই যোগ হয়। ধারণা আর উদাহরণ বিস্তারিত: [Dataclasses](../concepts/dataclasses.md)।

```python
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass, is_pydantic_dataclass


@dataclass
class Point:
    x: int
    y: int = 0


p = Point(x='3')
print(p, is_pydantic_dataclass(Point))
#> Point(x=3, y=0) True
print(TypeAdapter(Point).dump_python(p))  # model_dump() নেই, TypeAdapter দিয়ে
#> {'x': 3, 'y': 0}
```

## `@dataclass(...)` প্যারামিটার { #bn-parameters }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `init` | `False` | স্থির; Pydantic নিজের `__init__` দেয় (এটি বদলানো যায় না) |
| `repr`, `eq`, `order`, `unsafe_hash` | stdlib-এর মতো | সাধারণ dataclass-এর মতোই |
| `frozen` | `None` | `True` হলে তৈরির পরে মান বদলানো যায় না |
| `config` | `None` | `ConfigDict(...)`, যেমন `ConfigDict(validate_assignment=True)` |
| `validate_on_init` | `None` | পুরনো, আর ব্যবহার হয় না |
| `kw_only` | `False` | সব ফিল্ড শুধু keyword দিয়ে দিতে হবে |
| `slots` | `False` | `__slots__` তৈরি করে মেমোরি কমায় |

## অন্য ফাংশন { #bn-functions }

| ফাংশন | কী করে |
| --- | --- |
| `is_pydantic_dataclass(cls)` | ক্লাসটি Pydantic dataclass কিনা (সাধারণ dataclass হলে `False`) |
| `rebuild_dataclass(cls, force=False, raise_errors=True, ...)` | forward reference সংজ্ঞায়িত হওয়ার পরে schema আবার তৈরি (`BaseModel.model_rebuild()`-এর সমতুল্য) |

/// check | সংক্ষেপে মনে রাখুন

* `@dataclass(config=ConfigDict(...), frozen=True, kw_only=True)` এর মতো stdlib আর Pydantic দুই ধরনের প্যারামিটারই চলে।
* dump/schema-র জন্য `TypeAdapter(MyDataclass)`।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
