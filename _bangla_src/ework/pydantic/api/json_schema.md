# JSON Schema { #json-schema }

/// note | এই পেজে যা পাবেন

* `pydantic.json_schema` মডিউলের দরকারি অংশ: `GenerateJsonSchema`, `models_json_schema()`, আর `WithJsonSchema`, `SkipJsonSchema`, `Examples` annotation।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

সাধারণভাবে JSON Schema পেতে `Model.model_json_schema()` বা `TypeAdapter(T).json_schema()` যথেষ্ট। এই মডিউল লাগে schema নিজের মতো করতে। ধারণা বিস্তারিত: [JSON Schema](../concepts/json_schema.md)।

| সদস্য | কী করে |
| --- | --- |
| `GenerateJsonSchema` | schema তৈরির ক্লাস; subclass বানিয়ে নির্দিষ্ট টাইপের schema বদলানো যায়, তারপর `schema_generator=` হিসেবে দিন |
| `models_json_schema([(Model, mode), ...], by_alias=True, title=None, description=None, ...)` | একাধিক মডেলের schema একসাথে, শেয়ার করা `$defs` সহ; প্রতিটি মডেলের সাথে `'validation'` বা `'serialization'` মোড দিন; ফেরত দেয় `(প্রতিটির ref-এর ম্যাপ, সম্মিলিত schema)` |
| `model_json_schema(cls, ...)` | `Model.model_json_schema()`-এর ফাংশন রূপ |
| `WithJsonSchema(json_schema, mode=None)` | `Annotated` metadata: ফিল্ডের schema পুরোপুরি নিজে দেওয়া |
| `SkipJsonSchema[T]` | ফিল্ড (বা union-এর একটি অংশ) schema থেকে বাদ |
| `Examples(examples, mode=None)` | `Annotated` metadata: schema-তে উদাহরণ যোগ |
| `JsonSchemaValue`, `JsonSchemaMode`, `GetJsonSchemaHandler` | টাইপ hint (`mode` হলো `'validation'` বা `'serialization'`) |
| `PydanticJsonSchemaWarning` | schema তৈরিতে সমস্যা হলে সতর্কবার্তা |

## উদাহরণ { #bn-example }

```python
from typing import Annotated

from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema, WithJsonSchema


class S(BaseModel):
    x: Annotated[int, WithJsonSchema({'type': 'integer', 'description': 'custom'})]
    y: SkipJsonSchema[int] = 0  # schema-তে দেখাবে না


print(S.model_json_schema()['properties'])
#> {'x': {'description': 'custom', 'title': 'X', 'type': 'integer'}}
```

/// tip | FastAPI-তে

FastAPI `/docs`-এর জন্য এই schema-ই ব্যবহার করে। কোনো ফিল্ড ডকস থেকে লুকাতে `SkipJsonSchema`, আর উদাহরণ দেখাতে `Field(examples=[...])` সবচেয়ে সহজ।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
