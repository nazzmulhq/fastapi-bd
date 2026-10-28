# Functional Serializers { #functional-serializers }

/// note | এই পেজে যা পাবেন

* ডেটা বের করার (dump) সময় মান নিজের মতো বদলানোর টুল: `PlainSerializer`, `WrapSerializer`, `@field_serializer`, `@model_serializer`, `SerializeAsAny`।
* প্রতিটির প্যারামিটার (`return_type`, `when_used`, `mode`) আর উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

validator হলো দরজা দিয়ে ঢোকার সময়ের পরীক্ষা; serializer হলো বের হওয়ার সময়ের সাজসজ্জা। ভেতরে দাম থাকে সংখ্যা `1250.5`, কিন্তু বাইরে পাঠানোর সময় `'৳1,250.50'` লেখা হিসেবে যায়।

///

| সদস্য | ধরন | কী করে |
| --- | --- | --- |
| `PlainSerializer(func, return_type=..., when_used='always')` | `Annotated` metadata | মানটি `func` দিয়ে পুরোপুরি বদলে dump |
| `WrapSerializer(func, return_type=..., when_used='always')` | `Annotated` metadata | `func(value, handler)`; `handler` ডেকে স্বাভাবিক dump, তারপর বদল |
| `@field_serializer(*fields, mode='plain', return_type=..., when_used='always', check_fields=None)` | decorator | এক বা একাধিক ফিল্ডের serializer মেথড |
| `@model_serializer(mode='plain', when_used='always', return_type=...)` | decorator | পুরো মডেলের আউটপুট নিজে বানানো |
| `SerializeAsAny[T]` | টাইপ | subclass-এর বাড়তি ফিল্ডসহ dump (duck typing) |
| `SerializationInfo`, `SerializerFunctionWrapHandler` | টাইপ hint | serializer ফাংশনের `info` আর `handler`-এর টাইপ |

`when_used`-এর মান:

| মান | কখন serializer চলে |
| --- | --- |
| `'always'` | সবসময় |
| `'unless-none'` | মান `None` না হলে |
| `'json'` | শুধু JSON মোডে (`model_dump_json`, `mode='json'`) |
| `'json-unless-none'` | JSON মোডে আর মান `None` না হলে |

## উদাহরণ { #bn-example }

```python
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, PlainSerializer, field_serializer, model_serializer

Money = Annotated[float, PlainSerializer(lambda v: f'৳{v:,.2f}', return_type=str)]


class Order(BaseModel):
    total: Money
    at: datetime

    @field_serializer('at')
    def ser_at(self, v: datetime) -> str:
        return v.strftime('%d/%m/%Y')


o = Order(total=1250.5, at=datetime(2024, 3, 1, 10, 0))
print(o.model_dump(), o.total)
#> {'total': '৳1,250.50', 'at': '01/03/2024'} 1250.5


class Box(BaseModel):
    w: int
    h: int

    @model_serializer
    def ser(self):
        return {'area': self.w * self.h}


print(Box(w=2, h=3).model_dump())
#> {'area': 6}
```

লক্ষ করুন: `o.total` ভেতরে এখনো সংখ্যা `1250.5`; শুধু dump-এর সময় বদলায়।

বিস্তারিত: [Serialization](../concepts/serialization.md)।

/// check | সংক্ষেপে মনে রাখুন

* বারবার ব্যবহার: `Annotated[T, PlainSerializer(f, return_type=...)]`; এক মডেলে: `@field_serializer('x')`।
* শুধু JSON-এ বদলাতে `when_used='json'`; পুরো আউটপুট নিজে বানাতে `@model_serializer`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.functional_serializers
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
