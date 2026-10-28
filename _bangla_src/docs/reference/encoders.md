# Encoders - `jsonable_encoder` { #encoders-jsonable-encoder }

/// note | এই পেজে যা পাবেন

* `jsonable_encoder` কী করে, আর কখন নিজে ডাকতে হয়।
* কোন টাইপ কী রূপে বদলে যায় (রূপান্তর সারণি)।
* প্রতিটি প্যারামিটার (`include`, `exclude`, `by_alias`, `exclude_unset`, `exclude_defaults`, `exclude_none`, `custom_encoder`, `sqlalchemy_safe`) উদাহরণসহ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

`jsonable_encoder` যেকোনো ডেটাকে (Pydantic মডেল, `datetime`, `UUID`, `Decimal`, `set` ইত্যাদি) এমন সাধারণ Python রূপে আনে যা সরাসরি JSON-এ রাখা যায়: `dict`, `list`, `str`, `int`, `float`, `bool`, `None`।

/// tip | উদাহরণ দিয়ে বুঝি

বিদেশে পার্সেল পাঠানোর আগে সব জিনিস মানক বাক্সে ভরতে হয়। `datetime` বা `UUID` হলো অদ্ভুত আকারের জিনিস যা JSON-এর বাক্সে ঢোকে না; `jsonable_encoder` এগুলোকে লেখা (স্ট্রিং) বা সংখ্যায় বদলে মানক বাক্সে ভরে দেয়।

///

FastAPI রেসপন্স পাঠানোর সময় নিজেই এটি ব্যবহার করে। নিজে ডাকতে হয় মূলত তখন, যখন:

* ডেটাবেসে (যেমন JSON কলাম বা NoSQL) সংরক্ষণের আগে সাধারণ `dict` দরকার।
* সরাসরি `JSONResponse(content=...)` ফেরত দিচ্ছেন।
* অন্য সার্ভিসে পাঠানোর জন্য `json.dumps()` করবেন।

### রূপান্তর সারণি { #bn-conversions }

সাধারণ Python মান (ডিকশনারি, তালিকার ভেতরের মান) এভাবে বদলায়:

| মূল টাইপ | কী হয়ে যায় | উদাহরণ |
| --- | --- | --- |
| Pydantic মডেল | `dict` | `{"name": "বই"}` |
| `datetime`, `date`, `time` | ISO স্ট্রিং | `"2024-01-01T10:30:00"` |
| `timedelta` | মোট সেকেন্ড (`float`) | `90.0` |
| `UUID`, `Path`, URL, ইমেইল | `str` | `"4f1c..."` |
| `Decimal` | দশমিক না থাকলে `int`, থাকলে `float` | `12` বা `12.5` |
| `Enum` | তার মান | `"active"` |
| `set`, `frozenset`, `deque`, জেনারেটর | `list` | `[1, 2]` |
| `bytes` | `str` | `"abc"` |
| `SecretStr` | লুকানো স্ট্রিং | `"**********"` |

/// info | Pydantic মডেলের ভেতরে

মডেল পেলে `jsonable_encoder` আসলে `model.model_dump(mode="json")` ডাকে, তাই মডেলের ফিল্ডগুলো **Pydantic-এর নিজের JSON নিয়মে** বদলায়। পার্থক্য চোখে পড়ে কয়েক জায়গায়: মডেলের ভেতরের `Decimal("12.50")` হয় স্ট্রিং `"12.50"`, আর `timedelta` হয় ISO সময়কাল স্ট্রিং, যেমন `"PT1M30S"`।

///

## প্যারামিটার { #bn-parameters }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `obj` | (বাধ্যতামূলক) | যে ডেটা রূপান্তর করবেন |
| `include` | `None` | শুধু এই ফিল্ডগুলো রাখবে, যেমন `{"name", "price"}` |
| `exclude` | `None` | এই ফিল্ডগুলো বাদ দেবে |
| `by_alias` | `True` | Pydantic মডেলে alias থাকলে alias নামটি key হবে |
| `exclude_unset` | `False` | যে ফিল্ড ব্যবহারকারী দেয়নি (শুধু ডিফল্ট মান আছে) সেগুলো বাদ |
| `exclude_defaults` | `False` | যে ফিল্ডের মান ডিফল্টের সমান সেগুলো বাদ |
| `exclude_none` | `False` | যে ফিল্ডের মান `None` সেগুলো বাদ |
| `custom_encoder` | `None` | নির্দিষ্ট টাইপ কীভাবে রূপান্তর হবে, তার নিজের নিয়ম: `{টাইপ: ফাংশন}`; সাধারণ ডিকশনারি/তালিকার মানে কাজ করে, Pydantic মডেলের ভেতরের ফিল্ডে নয় |
| `sqlalchemy_safe` | `True` | SQLAlchemy-র ভেতরের `_sa_` দিয়ে শুরু key বাদ দেয় |

## উদাহরণ { #bn-examples }

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: UUID
    name: str
    price: Decimal
    created: datetime
    note: str | None = None
    internal_code: str = Field(default="X1", alias="internalCode")


p = Product(
    id=UUID("12345678-1234-5678-1234-567812345678"),
    name="কলম",
    price=Decimal("12.50"),
    created=datetime(2024, 1, 1, 10, 30),
)

print(jsonable_encoder(p))
# {'id': '12345678-1234-5678-1234-567812345678', 'name': 'কলম', 'price': '12.50',
#  'created': '2024-01-01T10:30:00', 'note': None, 'internalCode': 'X1'}

print(jsonable_encoder(p, exclude_none=True, by_alias=False))
# ... 'note' নেই, আর 'internalCode'-এর বদলে 'internal_code'

print(jsonable_encoder(p, include={"name", "price"}))
# {'name': 'কলম', 'price': '12.50'}
```

### `exclude_unset`: PATCH-এর জন্য খুব কাজের { #bn-exclude-unset }

```python
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class ItemUpdate(BaseModel):
    name: str | None = None
    price: float | None = None


update = ItemUpdate(price=99)
print(jsonable_encoder(update))                      # {'name': None, 'price': 99.0}
print(jsonable_encoder(update, exclude_unset=True))  # {'price': 99.0}
```

দ্বিতীয়টি দিয়ে শুধু ব্যবহারকারীর পাঠানো ফিল্ডগুলো আপডেট করা যায়, বাকিগুলো `None` দিয়ে মুছে যায় না। দেখুন [বডি - আপডেট](../tutorial/body-updates.md)।

### `custom_encoder` { #bn-custom-encoder }

```python
from datetime import datetime

from fastapi.encoders import jsonable_encoder

data = {"at": datetime(2024, 1, 1)}
print(jsonable_encoder(data, custom_encoder={datetime: lambda d: d.strftime("%d/%m/%Y")}))
# {'at': '01/01/2024'}
```

/// warning | সাধারণ ভুল

`jsonable_encoder` JSON **স্ট্রিং** ফেরত দেয় না, ফেরত দেয় JSON-যোগ্য Python অবজেক্ট (`dict` ইত্যাদি)। স্ট্রিং লাগলে তারপর `json.dumps(...)` করুন।

///

বিস্তারিত দেখুন [JSON উপযোগী এনকোডার](../tutorial/encoder.md) পেজে।

/// check | সংক্ষেপে মনে রাখুন

* `jsonable_encoder(obj)` → JSON-যোগ্য `dict`/`list`/`str`...।
* `datetime` → ISO স্ট্রিং, `UUID` → স্ট্রিং, `set` → তালিকা, মডেল → `dict`।
* ফিল্টার করতে `include`, `exclude`, `exclude_unset`, `exclude_none`; নিজের নিয়মে `custom_encoder`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.encoders.jsonable_encoder
