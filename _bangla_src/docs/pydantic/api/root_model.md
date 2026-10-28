# RootModel { #rootmodel }

/// note | এই পেজে যা পাবেন

* `RootModel` কী: পুরো ডেটা যখন একটিমাত্র মান (তালিকা, ডিকশনারি, সংখ্যা), নামযুক্ত ফিল্ড নয়।
* `root` অ্যাট্রিবিউট, যাচাই আর dump, আর তালিকা/ডিকশনারির মতো আচরণ যোগ করা।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ মডেল হলো ঘরওয়ালা ফর্ম ("নাম: __, বয়স: __")। কিন্তু কখনো পুরো ডেটাটাই একটি জিনিস, যেমন শুধু একটি তালিকা `["a", "b"]`; ঘরের নাম নেই। `RootModel` সেই "নামহীন" ডেটাকে মডেলের সব সুবিধা দেয়: যাচাই, `model_dump()`, JSON Schema। মানটি থাকে `.root`-এ।

///

| সদস্য | কী করে |
| --- | --- |
| `RootModel[টাইপ]` | যেকোনো টাইপকে মডেলে মোড়ায় |
| `.root` | আসল মান |
| `Model(value)` | positional আর্গুমেন্টে মান দিয়ে তৈরি |
| `model_validate()`, `model_validate_json()` | `BaseModel`-এর মতোই যাচাই |
| `model_dump()`, `model_dump_json()` | ডিকশনারির বদলে সরাসরি মানটি ফেরত দেয় |

```python
from pydantic import RootModel

Tags = RootModel[list[str]]
t = Tags(['a', 'b'])
print(t.root, t.model_dump(), t.model_dump_json())
#> ['a', 'b'] ['a', 'b'] ["a","b"]
```

## তালিকা বা ডিকশনারির মতো আচরণ { #bn-container }

`RootModel` নিজে থেকে `for` লুপ বা `[]` সমর্থন করে না; দরকার হলে subclass বানিয়ে `__iter__` আর `__getitem__` যোগ করুন:

```python
from pydantic import RootModel


class Scores(RootModel[dict[str, int]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, key):
        return self.root[key]


s = Scores.model_validate({'math': '90', 'bangla': 85})
print(s['math'], list(s))
#> 90 ['math', 'bangla']
```

/// warning | সাধারণ ভুল

* `RootModel`-এ `model_config['extra']` দেওয়া যায় না, কারণ এতে বাড়তি ফিল্ডের কোনো ধারণাই নেই।
* শুধু যাচাইয়ের জন্য (মডেল ক্লাস না বানিয়ে) [`TypeAdapter`](type_adapter.md) প্রায়ই সহজ; `RootModel` তখন ভালো, যখন অন্য মডেলের ফিল্ড হিসেবে বা নিজের মেথডসহ ব্যবহার করবেন।

///

বিস্তারিত: [RootModel ও কাস্টম root টাইপ](../concepts/models.md#rootmodel-and-custom-root-types)।

/// check | সংক্ষেপে মনে রাখুন

* `RootModel[list[str]]` বা `class X(RootModel[...])`; মান থাকে `.root`-এ।
* `model_dump()` সরাসরি মানটি দেয়, ডিকশনারি নয়।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.root_model
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
