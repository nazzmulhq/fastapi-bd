# TypeAdapter { #typeadapter }

/// note | এই পেজে যা পাবেন

* `TypeAdapter`-এর constructor আর প্রতিটি মেথড (যাচাই, dump, JSON Schema, rebuild), প্যারামিটার সারণি আর উদাহরণসহ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

`TypeAdapter` যেকোনো টাইপকে (`list[int]`, `dict[str, Item]`, `TypedDict`, dataclass, `int`) `BaseModel`-এর মতো যাচাই আর dump করার ক্ষমতা দেয়। ধারণা বিস্তারিত: [Type Adapter](../concepts/type_adapter.md)।

```python
from pydantic import TypeAdapter

ta = TypeAdapter(list[int])  # একবার বানান, বারবার ব্যবহার করুন
print(ta.validate_python(['1', 2]))
#> [1, 2]
print(ta.validate_json('[1, "2"]'))
#> [1, 2]
print(ta.dump_json([1, 2]))
#> b'[1,2]'
print(ta.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

## constructor: `TypeAdapter(type, *, config=None, module=None)` { #bn-init }

| প্যারামিটার | কী করে |
| --- | --- |
| `type` | যে টাইপ যাচাই করবেন |
| `config` | `ConfigDict`; তবে `BaseModel`, `TypedDict` বা dataclass-এর নিজের config থাকলে এখানে দেওয়া যায় না |
| `module` | forward reference খোঁজার মডিউল (অ্যাডভান্সড) |

## যাচাইয়ের মেথড { #bn-validate }

| মেথড | ইনপুট |
| --- | --- |
| `validate_python(obj)` | Python অবজেক্ট |
| `validate_json(data)` | JSON স্ট্রিং/bytes |
| `validate_strings(obj)` | সব মান স্ট্রিং এমন অবজেক্ট |

তিনটিরই প্যারামিটার: `strict`, `extra`, `context`, `by_alias`, `by_name` (অর্থ [`BaseModel.model_validate`](base_model.md#bn-validate)-এর মতো), `experimental_allow_partial` ([আংশিক যাচাই](../concepts/experimental.md#partial-validation)); আর `validate_python`-এ বাড়তি `from_attributes`।

## dump-এর মেথড { #bn-dump }

| মেথড | ফেরত দেয় |
| --- | --- |
| `dump_python(instance, mode='python', ...)` | Python অবজেক্ট (`mode='json'` দিলে JSON-যোগ্য) |
| `dump_json(instance, indent=None, ...)` | `bytes` (স্ট্রিং লাগলে `.decode()`) |

প্যারামিটার `BaseModel.model_dump()`-এর মতোই: `include`, `exclude`, `by_alias`, `exclude_unset`, `exclude_defaults`, `exclude_none`, `round_trip`, `warnings`, `fallback`, `context` ইত্যাদি। দেখুন [`model_dump` সারণি](base_model.md#bn-dump)।

## অন্য মেথড { #bn-others }

| মেথড | কী করে |
| --- | --- |
| `json_schema(by_alias=True, mode='validation', ...)` | টাইপটির JSON Schema |
| `rebuild(force=False, raise_errors=True)` | `defer_build` বা forward reference থাকলে schema তৈরি/আবার তৈরি |

/// check | সংক্ষেপে মনে রাখুন

* `TypeAdapter(টাইপ)` একবার, তারপর `validate_python` / `validate_json` / `dump_python` / `dump_json` / `json_schema`।
* `dump_json` দেয় `bytes`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.type_adapter.TypeAdapter
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
