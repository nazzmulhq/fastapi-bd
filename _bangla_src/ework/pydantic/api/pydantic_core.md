# pydantic_core { #pydantic_core }

/// note | এই পেজে যা পাবেন

* `pydantic_core` প্যাকেজের (Pydantic-এর Rust অংশ) প্রকাশ্য ক্লাস আর ফাংশন: `ValidationError`, নিজের এরর তোলার ক্লাস, দ্রুত JSON ফাংশন, আর নিচু-স্তরের validator/serializer।
* প্রতিটির এক লাইনের ব্যাখ্যা আর উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

`pydantic_core` হলো Pydantic-এর দ্রুত ইঞ্জিন (দেখুন [Architecture](../internals/architecture.md))। সাধারণ ব্যবহারে এখান থেকে সবচেয়ে বেশি লাগে `ValidationError` আর `PydanticCustomError`; বাকিগুলো অ্যাডভান্সড।

### এরর { #bn-errors }

| সদস্য | কী করে |
| --- | --- |
| `ValidationError` | যাচাই ব্যর্থ হলে যে exception ওঠে। মেথড: `errors()`, `error_count()`, `json()`, `title`; দেখুন [এরর সামলানো](../errors/errors.md) |
| `ErrorDetails` | `errors()`-এর প্রতিটি আইটেমের গঠন: `type`, `loc`, `msg`, `input`, `ctx`, `url` |
| `InitErrorDetails` | `ValidationError.from_exception_data()` দিয়ে হাতে এরর বানানোর গঠন |
| `PydanticCustomError(type, message_template, context)` | validator থেকে নিজের ধরনের আর বার্তার এরর তোলা |
| `PydanticKnownError(type, context)` | Pydantic-এর পরিচিত কোনো এরর ধরন (যেমন `'greater_than'`) তোলা |
| `PydanticOmit` | validator থেকে তুললে আইটেমটি বাদ পড়ে (যেমন তালিকা থেকে) |
| `PydanticUseDefault` | validator থেকে তুললে ফিল্ডের ডিফল্ট মান ব্যবহার হয় |
| `PydanticSerializationError` | সিরিয়ালাইজেশন ব্যর্থ হলে |
| `PydanticSerializationUnexpectedValue` | serializer অপ্রত্যাশিত মান পেলে (সতর্কবার্তার জন্য) |
| `SchemaError` | core schema নিজেই অবৈধ হলে |
| `list_all_errors()` / `ErrorTypeInfo` | Pydantic-এর সব এরর ধরন আর তাদের বার্তার ছাঁচের তালিকা |

### JSON ফাংশন { #bn-json }

| ফাংশন | কী করে |
| --- | --- |
| `to_json(value, indent=None, ...)` | যেকোনো Python মানকে দ্রুত JSON `bytes`-এ রূপান্তর (মডেল, `datetime`, `UUID` সহ) |
| `from_json(data, allow_partial=False, ...)` | JSON পার্স করে Python অবজেক্ট; `allow_partial=True` দিলে অসম্পূর্ণ JSON-ও |
| `to_jsonable_python(value, ...)` | JSON-যোগ্য Python অবজেক্টে রূপান্তর (`date` → স্ট্রিং, `set` → তালিকা) |

### নিচু-স্তরের যাচাই আর অন্যান্য { #bn-low-level }

| সদস্য | কী করে |
| --- | --- |
| `SchemaValidator(schema, config=None)` | একটি core schema থেকে validator; `validate_python()`, `validate_json()`, `validate_strings()` |
| `SchemaSerializer(schema, config=None)` | একটি core schema থেকে serializer; `to_python()`, `to_json()` |
| `Url`, `MultiHostUrl`, `MultiHostHost` | URL টাইপের ভেতরের রূপ (`HttpUrl` ইত্যাদির ভিত্তি) |
| `ArgsKwargs` | positional আর keyword আর্গুমেন্ট একসাথে রাখার কাঠামো (dataclass-এর before validator-এ আসে) |
| `Some` | "মান আছে" বোঝানোর মোড়ক (ডিফল্ট মান খোঁজার ফলাফলে) |
| `TzInfo` | স্থির offset-এর timezone (যেমন `+06:00`) |
| `__version__` | pydantic-core-এর সংস্করণ |

## উদাহরণ { #bn-example }

```python
from datetime import date

from pydantic_core import SchemaValidator, ValidationError, core_schema, from_json, to_json, to_jsonable_python

v = SchemaValidator(
    core_schema.typed_dict_schema(
        {
            'name': core_schema.typed_dict_field(core_schema.str_schema(min_length=2)),
            'age': core_schema.typed_dict_field(core_schema.int_schema(ge=0)),
        }
    )
)
print(v.validate_python({'name': 'রহিম', 'age': '30'}))
#> {'name': 'রহিম', 'age': 30}

try:
    v.validate_python({'name': 'x', 'age': -1})
except ValidationError as e:
    print(e.error_count(), [x['type'] for x in e.errors()])
    #> 2 ['string_too_short', 'greater_than_equal']

print(to_json({'a': 1, 'b': [1, 2]}))
#> b'{"a":1,"b":[1,2]}'
print(from_json('[1, 2, 3', allow_partial=True))
#> [1, 2, 3]
print(to_jsonable_python({'d': date(2024, 1, 1), 's': {1}}))
#> {'d': '2024-01-01', 's': [1]}
```

/// tip | কখন সরাসরি ব্যবহার করবেন

সাধারণত `BaseModel` বা `TypeAdapter`-ই যথেষ্ট; ভেতরে ভেতরে এরাই `SchemaValidator` বানায়। `to_json`/`from_json` অবশ্য যেকোনো জায়গায় দ্রুত JSON কাজের জন্য কাজে লাগে, আর validator-এ `PydanticCustomError` দিয়ে পরিষ্কার এরর তোলা খুব প্রচলিত।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
