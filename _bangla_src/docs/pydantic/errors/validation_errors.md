# Validation Errors { #validation-errors }

/// note | এই পেজে যা পাবেন

* যাচাইয়ের সময় Pydantic যে প্রতিটি এরর `type` দিতে পারে, তার অর্থ আর একটি করে উদাহরণ (বর্ণানুক্রমে)।
* কোন এরর কোন দলে পড়ে, তার দ্রুত সারণি, আর এরর পেলে কী করবেন।

///

Pydantic দরকারি যাচাই এরর দেওয়ার চেষ্টা করে। নিচে pydantic নিয়ে কাজের সময় ব্যবহারকারীরা যেসব সাধারণ যাচাই এরর
পেতে পারেন তার বিস্তারিত, আর সেগুলো ঠিক করার কিছু পরামর্শ দেওয়া হলো।

নিচের এন্ট্রিগুলো প্রতিটি এরর টাইপের অর্থ ব্যাখ্যা করে। চলমান একটি সার্ভিসে কোনোটি ঘটলে প্রত্যাখ্যাত মান আর আশেপাশের trace দেখতে,
[Logfire](troubleshooting.md) ব্যর্থ যাচাই তাদের গোছানো এররসহ রেকর্ড করতে পারে। সেটআপ আর
সংবেদনশীল ডেটা নিয়ে ভাবনার জন্য দেখুন [যাচাই এররের সমস্যা সমাধান](troubleshooting.md)।

## এরর কীভাবে খুঁজবেন { #bn-how-to-use }

এরর বার্তার শেষে `[type=...]` অংশে এররের নাম থাকে, যেমন `[type=int_parsing, ...]`। নিচে সেই নামের অংশে গিয়ে অর্থ আর উদাহরণ দেখুন। নাম দেখে দলও চেনা যায়:

| নামের ধরন | মানে | উদাহরণ |
| --- | --- | --- |
| `..._type` | ইনপুটের টাইপই ভুল (যেমন সংখ্যার জায়গায় তালিকা) | `int_type`, `list_type`, `string_type` |
| `..._parsing` | টাইপ লেখা (স্ট্রিং) হলেও পড়ে বোঝা গেল না | `int_parsing`, `date_parsing`, `url_parsing` |
| `greater_than`, `less_than`, `multiple_of` ... | সংখ্যার শর্ত ভাঙা | `gt`, `ge`, `lt`, `le` |
| `..._too_long`, `..._too_short` | দৈর্ঘ্যের শর্ত ভাঙা | `max_length`, `min_length` |
| `missing...` | বাধ্যতামূলক কিছু দেওয়া হয়নি | `missing`, `missing_argument` |
| `frozen_...` | বদলানো নিষেধ এমন কিছু বদলানোর চেষ্টা | `frozen_field`, `frozen_instance` |
| `value_error`, `assertion_error` | আপনার নিজের validator এরর তুলেছে | |

/// tip | উদাহরণ দিয়ে বুঝি

এই পেজটি ডাক্তারের রোগ নির্ণয়ের বইয়ের মতো: উপসর্গের নাম (`type`) দেখে ঠিক পাতায় যান, সেখানে কারণ আর উদাহরণ পাবেন। প্রায় সব ক্ষেত্রে সমাধান দুটির একটি: হয় ইনপুট ঠিক করুন, নয়তো মডেলের টাইপ বা শর্ত আপনার আসল ডেটার সাথে মিলিয়ে নিন।

///

## `arguments_type` { #arguments_type }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি ফাংশনে আর্গুমেন্ট হিসেবে পাঠানো হবে এমন একটি অবজেক্ট
`tuple`, `list` বা `dict` নয়:

```python
from pydantic import TypeAdapter, ValidationError


def func(x: int) -> None: ...


ta = TypeAdapter(func)

try:
    ta.validate_python('invalid')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'arguments_type'
```

## `assertion_error` { #assertion_error }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি ব্যর্থ `assert` স্টেটমেন্ট পাওয়া যায়:

```python
from pydantic import BaseModel, ValidationError, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    @classmethod
    def force_x_positive(cls, v):
        assert v > 0
        return v


try:
    Model(x=-1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'assertion_error'
```

## `bool_parsing` { #bool_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা boolean-এ রূপান্তরের জন্য বৈধ নয় (যেমন `'yes'`, `'true'`, `'1'` চলে, কিন্তু `'হ্যাঁ'` বা `'maybe'` চলে না):

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bool


Model(x='true')  # OK

try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bool_parsing'
```

## `bool_type` { #bool_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `bool` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bool


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bool_type'
```

strict ফিল্ডে ইনপুট মান `bool`-এর instance না হলেও এই এরর ওঠে।

## `bytes_invalid_encoding` { #bytes_invalid_encoding }

এই এরর ওঠে যখন একটি `bytes` মান কনফিগার করা encoding অনুযায়ী অবৈধ।
নিচের উদাহরণে, `'a'` অবৈধ hex (অঙ্কের সংখ্যা বিজোড়)।

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bytes
    model_config = {'val_json_bytes': 'hex'}


try:
    Model(x='a')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_invalid_encoding'
```

## `bytes_too_long` { #bytes_too_long }

এই এরর ওঠে যখন একটি `bytes` মানের দৈর্ঘ্য ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: bytes = Field(max_length=3)


try:
    Model(x=b'test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_too_long'
```

## `bytes_too_short` { #bytes_too_short }

এই এরর ওঠে যখন একটি `bytes` মানের দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: bytes = Field(min_length=3)


try:
    Model(x=b't')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_too_short'
```

## `bytes_type` { #bytes_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `bytes` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bytes


try:
    Model(x=123)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_type'
```

strict ফিল্ডে ইনপুট মান `bytes`-এর instance না হলেও এই এরর ওঠে।

## `callable_type` { #callable_type }

এই এরর ওঠে যখন ইনপুট মান callable (ডাকা যায় এমন, যেমন ফাংশন) হিসেবে বৈধ নয়:

```python
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ImportString, ValidationError


class Model(BaseModel):
    x: ImportString[Callable[[Any], Any]]


Model(x='math:cos')  # OK

try:
    Model(x='os.path')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'callable_type'
```

## `complex_str_parsing` { #complex_str_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং, কিন্তু complex number হিসেবে পার্স করা যায় না কারণ
এটি Python-এর [নিয়ম](https://docs.python.org/3/library/functions.html#complex) মানে না:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    num: complex


try:
    # Complex numbers in json are expected to be valid complex strings.
    # This value `abc` is not a valid complex string.
    Model.model_validate_json('{"num": "abc"}')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'complex_str_parsing'
```

## `complex_type` { #complex_type }

এই এরর ওঠে যখন ইনপুট মানকে complex number হিসেবে বোঝা যায় না:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    num: complex


try:
    Model(num='not a complex number')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'complex_type'
```

## `counter_type` { #counter_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`Counter`][collections.Counter] ফিল্ডের জন্য বৈধ নয়:

```python
from collections import Counter

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Counter[str]


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'counter_type'
```

## `dataclass_exact_type` { #dataclass_exact_type }

এই এরর ওঠে যখন `strict=True` দিয়ে একটি dataclass যাচাই করা হয় আর ইনপুট সেই dataclass-এর instance নয়:

```python
import pydantic.dataclasses
from pydantic import TypeAdapter, ValidationError


@pydantic.dataclasses.dataclass
class MyDataclass:
    x: str


adapter = TypeAdapter(MyDataclass)

print(adapter.validate_python(MyDataclass(x='test'), strict=True))
#> MyDataclass(x='test')
print(adapter.validate_python({'x': 'test'}))
#> MyDataclass(x='test')

try:
    adapter.validate_python({'x': 'test'}, strict=True)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dataclass_exact_type'
```

## `dataclass_type` { #dataclass_type }

এই এরর ওঠে যখন ইনপুট মান একটি `dataclass` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import ValidationError, dataclasses


@dataclasses.dataclass
class Inner:
    x: int


@dataclasses.dataclass
class Outer:
    y: Inner


Outer(y=Inner(x=1))  # OK

try:
    Outer(y=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dataclass_type'
```

## `date_from_datetime_inexact` { #date_from_datetime_inexact }

এই এরর ওঠে যখন একটি `date` ফিল্ডের জন্য দেওয়া `datetime` ইনপুটের সময়ের অংশ শূন্য নয়।
একটি timestamp `date` টাইপের ফিল্ডে পার্স হতে হলে, সময়ের সব অংশ শূন্য হতে হবে:

```python
from datetime import date, datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


Model(x='2023-01-01')  # OK
Model(x=datetime(2023, 1, 1))  # OK

try:
    Model(x=datetime(2023, 1, 1, 12))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_from_datetime_inexact'
```

## `date_from_datetime_parsing` { #date_from_datetime_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `date` ফিল্ডের জন্য পার্স করা যায় না:

```python
from datetime import date

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


try:
    Model(x='XX1494012000')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_from_datetime_parsing'
```

## `date_future` { #date_future }

এই এরর ওঠে যখন একটি `FutureDate` ফিল্ডের জন্য দেওয়া ইনপুট মান ভবিষ্যতের নয়:

```python
from datetime import date

from pydantic import BaseModel, FutureDate, ValidationError


class Model(BaseModel):
    x: FutureDate


try:
    Model(x=date(2000, 1, 1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_future'
```

## `date_parsing` { #date_parsing }

এই এরর ওঠে যখন JSON যাচাইয়ের সময় ইনপুট মান এমন একটি স্ট্রিং যা একটি `date` ফিল্ডের জন্য পার্স করা যায় না:

```python
import json
from datetime import date

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: date = Field(strict=True)


try:
    Model.model_validate_json(json.dumps({'x': '1'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_parsing'
```

## `date_past` { #date_past }

এই এরর ওঠে যখন একটি `PastDate` ফিল্ডের জন্য দেওয়া মান অতীতের নয়:

```python
from datetime import date, timedelta

from pydantic import BaseModel, PastDate, ValidationError


class Model(BaseModel):
    x: PastDate


try:
    Model(x=date.today() + timedelta(1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_past'
```

## `date_type` { #date_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `date` ফিল্ডের জন্য বৈধ নয়:

```python
from datetime import date

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_type'
```

strict ফিল্ডে ইনপুট মান `date`-এর instance না হলেও এই এরর ওঠে।

## `datetime_from_date_parsing` { #datetime_from_date_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `datetime` ফিল্ডের জন্য পার্স করা যায় না:

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: datetime


try:
    # there is no 13th month
    Model(x='2023-13-01')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_from_date_parsing'
```

## `datetime_future` { #datetime_future }

এই এরর ওঠে যখন একটি `FutureDatetime` ফিল্ডের জন্য দেওয়া মান ভবিষ্যতের নয়:

```python
from datetime import datetime

from pydantic import BaseModel, FutureDatetime, ValidationError


class Model(BaseModel):
    x: FutureDatetime


try:
    Model(x=datetime(2000, 1, 1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_future'
```

## `datetime_object_invalid` { #datetime_object_invalid }

এই এরর ওঠে যখন `datetime` অবজেক্টের কোনো কিছু বৈধ নয়:

```python
from datetime import datetime, tzinfo

from pydantic import AwareDatetime, BaseModel, ValidationError


class CustomTz(tzinfo):
    # utcoffset is not implemented!

    def tzname(self, _dt):
        return 'CustomTZ'


class Model(BaseModel):
    x: AwareDatetime


try:
    Model(x=datetime(2023, 1, 1, tzinfo=CustomTz()))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_object_invalid'
```

## `datetime_parsing` { #datetime_parsing }

এই এরর ওঠে যখন মানটি এমন একটি স্ট্রিং যা একটি `datetime` ফিল্ডের জন্য পার্স করা যায় না:

```python
import json
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: datetime = Field(strict=True)


try:
    Model.model_validate_json(json.dumps({'x': 'not a datetime'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_parsing'
```

## `datetime_past` { #datetime_past }

এই এরর ওঠে যখন একটি `PastDatetime` ফিল্ডের জন্য দেওয়া মান অতীতের নয়:

```python
from datetime import datetime, timedelta

from pydantic import BaseModel, PastDatetime, ValidationError


class Model(BaseModel):
    x: PastDatetime


try:
    Model(x=datetime.now() + timedelta(100))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_past'
```

## `datetime_type` { #datetime_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `datetime` ফিল্ডের জন্য বৈধ নয়:

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: datetime


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_type'
```

strict ফিল্ডে ইনপুট মান `datetime`-এর instance না হলেও এই এরর ওঠে।

## `decimal_max_digits` { #decimal_max_digits }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে অঙ্ক খুব বেশি:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(max_digits=3)


try:
    Model(x='42.1234')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_max_digits'
```

## `decimal_max_places` { #decimal_max_places }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে দশমিক বিন্দুর পরে অঙ্ক খুব বেশি:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x='42.1234')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_max_places'
```

## `decimal_parsing` { #decimal_parsing }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মান দশমিক সংখ্যা হিসেবে পার্স করা যায়নি:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_parsing'
```

## `decimal_type` { #decimal_type }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মান ভুল টাইপের:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x=[1, 2, 3])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_type'
```

strict ফিল্ডে ইনপুট মান `Decimal`-এর instance না হলেও এই এরর ওঠে।

## `decimal_whole_digits` { #decimal_whole_digits }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে দশমিক বিন্দুর আগে `max_digits` - `decimal_places`-এর চেয়ে বেশি অঙ্ক থাকে (যদি দুটোই দেওয়া থাকে):

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(max_digits=6, decimal_places=3)


try:
    Model(x='12345.6')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_whole_digits'
```

## `default_factory_not_called` { #default_factory_not_called }

এই এরর ওঠে যখন একটি [যাচাই হওয়া ডেটা নেওয়া default factory](../concepts/fields.md#default-factory-validated-data)
ডাকা যায় না, কারণ আগের ফিল্ডগুলোতে যাচাই ব্যর্থ হয়েছে:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    a: int = Field(gt=10)
    b: int = Field(default_factory=lambda data: data['a'])


try:
    Model(a=1)
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for Model
    a
      Input should be greater than 10 [type=greater_than, input_value=1, input_type=int]
    b
      The default factory uses validated data, but at least one validation error occurred [type=default_factory_not_called]
    """
    print(repr(exc.errors()[1]['type']))
    #> 'default_factory_not_called'
```

## `deque_type` { #deque_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`deque`][collections.deque] ফিল্ডের জন্য বৈধ নয়:

```python
from collections import deque

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: deque[int]


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'deque_type'
```

## `dict_type` { #dict_type }

এই এরর ওঠে যখন একটি `dict` ফিল্ডের ইনপুট মানের টাইপ `dict` নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: dict


try:
    Model(x=['1', '2'])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dict_type'
```

## `ellipsis_error` { #ellipsis_error }

এই এরর ওঠে যখন ইনপুটটি [`Ellipsis`][] literal (`...`) নয়:

```python
from types import EllipsisType

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    e: EllipsisType


try:
    Model(e=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'ellipsis_error'
```

## `enum` { #enum }

এই এরর ওঠে যখন ইনপুট মান একটি `enum` ফিল্ডের সদস্যদের মধ্যে নেই:

```python
from enum import Enum

from pydantic import BaseModel, ValidationError


class MyEnum(str, Enum):
    option = 'option'


class Model(BaseModel):
    x: MyEnum


try:
    Model(x='other_option')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'enum'
```

## `extra_forbidden` { #extra_forbidden }

এই এরর ওঠে যখন ইনপুট মানে বাড়তি ফিল্ড থাকে, কিন্তু `model_config['extra'] == 'forbid'`:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: str

    model_config = ConfigDict(extra='forbid')


try:
    Model(x='test', y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'extra_forbidden'
```

`extra` কনফিগারেশন নিয়ে আরও পড়তে পারেন [বাড়তি অ্যাট্রিবিউট][pydantic.config.ConfigDict.extra] অংশে।

## `finite_number` { #finite_number }

এই এরর ওঠে যখন যাচাইয়ের সময় মানটি অসীম, বা 64-bit floating point সংখ্যা হিসেবে প্রকাশ করার জন্য
খুব বড়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=2.2250738585072011e308)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'finite_number'
```

## `float_parsing` { #float_parsing }

এই এরর ওঠে যখন মানটি এমন একটি স্ট্রিং যা `float` হিসেবে পার্স করা যায় না:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: float


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'float_parsing'
```

## `float_type` { #float_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `float` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: float


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'float_type'
```

## `fraction_parsing` { #fraction_parsing }

এই এরর ওঠে যখন দেওয়া মান ভগ্নাংশ (fraction) হিসেবে পার্স করা যায়নি:

```python
from fractions import Fraction

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Fraction


try:
    Model(x='invalid')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'fraction_parsing'
```

## `fraction_type` { #fraction_type }

এই এরর ওঠে যখন একটি [`Fraction`][fractions.Fraction]-এর জন্য দেওয়া মান ভুল টাইপের:

```python
from fractions import Fraction

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Fraction


try:
    Model.model_validate_json('{"x": [1, 2]}')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'fraction_type'
```

## `frozen_dict_type` { #frozen_dict_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `frozendict` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: frozendict


try:
    model = Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_dict_type'
```

## `frozen_field` { #frozen_field }

এই এরর ওঠে যখন `frozen=True` থাকা একটি ফিল্ডে মান বসানোর, বা এমন ফিল্ড মুছে ফেলার চেষ্টা করেন:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field('test', frozen=True)


model = Model()

try:
    model.x = 'test1'
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_field'

try:
    del model.x
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_field'
```

## `frozen_instance` { #frozen_instance }

এই এরর ওঠে যখন [কনফিগারেশনে](../concepts/config.md) `frozen` সেট করা থাকে আর আপনি যেকোনো ফিল্ড মুছে ফেলার
বা তাতে নতুন মান বসানোর চেষ্টা করেন:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(frozen=True)


m = Model(x=1)

try:
    m.x = 2
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_instance'

try:
    del m.x
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_instance'
```

## `frozen_set_type` { #frozen_set_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `frozenset` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: frozenset


try:
    model = Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_set_type'
```

## `get_attribute_error` { #get_attribute_error }

এই এরর ওঠে যখন `model_config['from_attributes'] == True` আর অ্যাট্রিবিউট পড়ার সময় একটি এরর ওঠে:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Foobar:
    def __init__(self):
        self.x = 1

    @property
    def y(self):
        raise RuntimeError('intentional error')


class Model(BaseModel):
    x: int
    y: str

    model_config = ConfigDict(from_attributes=True)


try:
    Model.model_validate(Foobar())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'get_attribute_error'
```

## `greater_than` { #greater_than }

এই এরর ওঠে যখন মানটি ফিল্ডের `gt` শর্তের চেয়ে বড় নয়:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(gt=10)


try:
    Model(x=10)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'greater_than'
```

## `greater_than_equal` { #greater_than_equal }

এই এরর ওঠে যখন মানটি ফিল্ডের `ge` শর্তের চেয়ে বড় বা সমান নয়:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(ge=10)


try:
    Model(x=9)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'greater_than_equal'
```

## `int_from_float` { #int_from_float }

এই এরর ওঠে যখন একটি `int` ফিল্ডে দশমিক অংশসহ একটি `float` মান দেন (যেমন `1.5`; কিন্তু `1.0` চলে):

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=0.5)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_from_float'
```

## `int_parsing` { #int_parsing }

এই এরর ওঠে যখন মানটি `int` হিসেবে পার্স করা যায় না:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing'
```

## `int_parsing_size` { #int_parsing_size }

এই এরর ওঠে যখন একটি স্ট্রিং থেকে এমন python বা JSON মান পার্সের চেষ্টা করা হয় যা Python-এর
`str` থেকে `int` পার্সিংয়ের অনুমোদিত সর্বোচ্চ সীমার বাইরে:

```python
import json

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


# from Python
assert Model(x='1' * 4_300).x == int('1' * 4_300)  # OK

too_long = '1' * 4_301
try:
    Model(x=too_long)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing_size'

# from JSON
try:
    Model.model_validate_json(json.dumps({'x': too_long}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing_size'
```

## `int_type` { #int_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `int` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_type'
```

## `invalid_key` { #invalid_key }

এই এরর ওঠে যখন এমন একটি `dict` যাচাইয়ের চেষ্টা করা হয় যার একটি key `str`-এর instance নয়:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='allow')


try:
    Model.model_validate({'x': 1, b'y': 2})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'invalid_key'
```

## `is_instance_of` { #is_instance_of }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত টাইপের instance নয়:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Nested:
    x: str


class Model(BaseModel):
    y: Nested

    model_config = ConfigDict(arbitrary_types_allowed=True)


try:
    Model(y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'is_instance_of'
```

## `is_subclass_of` { #is_subclass_of }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত টাইপের subclass নয়:

```python
from pydantic import BaseModel, ValidationError


class Nested:
    x: str


class Model(BaseModel):
    y: type[Nested]


try:
    Model(y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'is_subclass_of'
```

## `iterable_type` { #iterable_type }

এই এরর ওঠে যখন ইনপুট মান একটি `Iterable` হিসেবে বৈধ নয়:

```python
from collections.abc import Iterable

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    y: Iterable[str]


try:
    Model(y=123)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'iterable_type'
```

## `iteration_error` { #iteration_error }

এই এরর ওঠে যখন iteration (একে একে আইটেম নেওয়া)-এর সময় একটি এরর ঘটে:

```python
from pydantic import BaseModel, ValidationError


def gen():
    yield 1
    raise RuntimeError('error')


class Model(BaseModel):
    x: list[int]


try:
    Model(x=gen())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'iteration_error'
```

## `json_invalid` { #json_invalid }

এই এরর ওঠে যখন ইনপুট মান একটি বৈধ JSON স্ট্রিং নয়:

```python
from pydantic import BaseModel, Json, ValidationError


class Model(BaseModel):
    x: Json


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'json_invalid'
```

## `json_type` { #json_type }

এই এরর ওঠে যখন ইনপুট মান এমন টাইপের যা JSON হিসেবে পার্স করা যায় না:

```python
from pydantic import BaseModel, Json, ValidationError


class Model(BaseModel):
    x: Json


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'json_type'
```

## `less_than` { #less_than }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `lt` শর্তের চেয়ে ছোট নয়:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(lt=10)


try:
    Model(x=10)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'less_than'
```

## `less_than_equal` { #less_than_equal }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `le` শর্তের চেয়ে ছোট বা সমান নয়:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(le=10)


try:
    Model(x=11)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'less_than_equal'
```

## `list_type` { #list_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `list` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: list[int]


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'list_type'
```

## `literal_error` { #literal_error }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত literal মানগুলোর একটি নয়:

```python
from typing import Literal

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Literal['a', 'b']


Model(x='a')  # OK

try:
    Model(x='c')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'literal_error'
```

## `mapping_type` { #mapping_type }

এই এরর ওঠে যখন যাচাইয়ের সময় `Mapping` protocol-এর মেথড, যেমন `.items()`, ডাকতে গিয়ে ব্যর্থতার কারণে
সমস্যা হয়:

```python
from collections.abc import Mapping

from pydantic import BaseModel, ValidationError


class BadMapping(Mapping):
    def items(self):
        raise ValueError()

    def __iter__(self):
        raise ValueError()

    def __getitem__(self, key):
        raise ValueError()

    def __len__(self):
        return 1


class Model(BaseModel):
    x: dict[str, str]


try:
    Model(x=BadMapping())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'mapping_type'
```

## `missing` { #missing }

এই এরর ওঠে যখন ইনপুট মানে বাধ্যতামূলক ফিল্ড অনুপস্থিত:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing'
```

/// tip | সমাধান

ফিল্ডটি পাঠান, অথবা ফিল্ডটি ঐচ্ছিক হলে মডেলে একটি ডিফল্ট মান দিন (যেমন `name: str | None = None`)। মনে রাখুন, শুধু `str | None` লিখলে ফিল্ড ঐচ্ছিক হয় না; `= None` ডিফল্টও লাগে।

///

## `missing_argument` { #missing_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক positional-or-keyword আর্গুমেন্ট
দেওয়া হয় না:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_argument'
```

## `missing_keyword_only_argument` { #missing_keyword_only_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক keyword-only আর্গুমেন্ট দেওয়া হয় না:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(*, a: int):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_keyword_only_argument'
```

## `missing_positional_only_argument` { #missing_positional_only_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক positional-only আর্গুমেন্ট
দেওয়া হয় না:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int, /):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_positional_only_argument'
```

## `missing_sentinel_error` { #missing_sentinel_error }

এই এরর ওঠে যখন `MISSING` sentinel-ই একমাত্র অনুমোদিত মান, কিন্তু যাচাইয়ের সময় সেটি দেওয়া হয়নি:

```python
from pydantic import MISSING, BaseModel, ValidationError


class Model(BaseModel):
    f: MISSING


try:
    Model(f=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_sentinel_error'
```

## `model_attributes_type` { #model_attributes_type }

এই এরর ওঠে যখন ইনপুট মান একটি বৈধ ডিকশনারি, মডেল instance, বা এমন instance নয় যা থেকে ফিল্ড বের করা যায়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int


# simply validating a dict
print(Model.model_validate({'a': 1, 'b': 2}))
#> a=1 b=2


class CustomObj:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# using from attributes to extract fields from an objects
print(Model.model_validate(CustomObj(3, 4), from_attributes=True))
#> a=3 b=4

try:
    Model.model_validate('not an object', from_attributes=True)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'model_attributes_type'
```

## `model_type` { #model_type }

এই এরর ওঠে যখন একটি মডেলের ইনপুট সেই মডেলের instance বা dict নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int


# simply validating a dict
m = Model.model_validate({'a': 1, 'b': 2})
print(m)
#> a=1 b=2

# validating an existing model instance
print(Model.model_validate(m))
#> a=1 b=2

try:
    Model.model_validate('not an object')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'model_type'
```

## `multiple_argument_values` { #multiple_argument_values }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি আর্গুমেন্টের জন্য একাধিক মান দেন
(যেমন positional হিসেবেও আর keyword হিসেবেও):

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int):
    return a


try:
    foo(1, a=2)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'multiple_argument_values'
```

## `multiple_of` { #multiple_of }

এই এরর ওঠে যখন ইনপুটটি ফিল্ডের `multiple_of` শর্তের গুণিতক নয়:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(multiple_of=5)


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'multiple_of'
```

## `named_tuple_type` { #named_tuple_type }

এই এরর ওঠে যখন ইনপুট মান একটি named tuple ফিল্ডের জন্য বৈধ নয়:

```python
from typing import NamedTuple

from pydantic import BaseModel, ValidationError


class Point(NamedTuple):
    x: int
    y: int


class Model(BaseModel):
    p: Point


try:
    Model(p='invalid')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'named_tuple_type'
```

## `needs_python_object` { #needs_python_object }

এই ধরনের এরর ওঠে যখন এমন একটি ফরম্যাট থেকে যাচাইয়ের চেষ্টা করা হয় যা একটি Python অবজেক্টে রূপান্তর করা যায় না।
যেমন, JSON থেকে আমরা `isinstance` বা `issubclass` পরীক্ষা করতে পারি না:

```python
import json

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    bm: type[BaseModel]


try:
    Model.model_validate_json(json.dumps({'bm': 'not a basemodel class'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'needs_python_object'
```

## `no_such_attribute` { #no_such_attribute }

এই এরর ওঠে যখন কনফিগে `validate_assignment=True` থাকে, আর আপনি এমন একটি অ্যাট্রিবিউটে মান বসানোর চেষ্টা করেন
যা বিদ্যমান কোনো ফিল্ড নয়:

```python
from pydantic import ConfigDict, ValidationError, dataclasses


@dataclasses.dataclass(config=ConfigDict(validate_assignment=True))
class MyDataclass:
    x: int


m = MyDataclass(x=1)
try:
    m.y = 10
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'no_such_attribute'
```

## `none_required` { #none_required }

এই এরর ওঠে যখন `None` দাবি করে এমন একটি ফিল্ডের ইনপুট মান `None` নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: None


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'none_required'
```

/// note | মনে রাখুন

যখন আপনার মডেলে একটি ফিল্ডের নাম আর তার টাইপের নামের মধ্যে সংঘাত থাকে, তখন এই এরর পেতে পারেন। আরও নির্দিষ্টভাবে, সেই ফিল্ডের ডিফল্ট মান `None` হলে এই এরর ওঠার সম্ভাবনা বেশি।

যেমন, নিচের কোডে `none_required` যাচাই এরর আসবে, কারণ `int` ফিল্ডের ডিফল্ট মান `None` আর এর নাম হুবহু তার টাইপের নামের মতো, যা যাচাইয়ে সমস্যা তৈরি করে।

```python
from typing import Optional

from pydantic import BaseModel


class M1(BaseModel):
    int: Optional[int] = None


m = M1(int=123)  # errors
```

///

## `ordered_dict_type` { #ordered_dict_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`OrderedDict`][collections.OrderedDict] ফিল্ডের জন্য বৈধ নয়:

```python
from collections import OrderedDict

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: OrderedDict[str, int]


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'ordered_dict_type'
```

## `recursion_loop` { #recursion_loop }

এই এরর ওঠে যখন একটি চক্রাকার উল্লেখ শনাক্ত হয় (দেখুন [Cyclic references](../examples/cyclic_references.md)):

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: list['Model']


d = {'x': []}
d['x'].append(d)
try:
    Model(**d)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'recursion_loop'
```

## `set_item_not_hashable` { #set_item_not_hashable }

এই এরর ওঠে যখন একটি hash করা যায় না এমন মান (যেমন তালিকা বা ডিকশনারি) একটি [`set`][] বা একটি [`frozenset`][]-এর বিপরীতে যাচাই হয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: set[object]


class Unhashable:
    __hash__ = None


try:
    Model(x=[{'a': 'b'}, Unhashable()])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'set_item_not_hashable'
    print(repr(exc.errors()[1]['type']))
    #> 'set_item_not_hashable'
```

## `set_type` { #set_type }

এই এরর ওঠে যখন মানের টাইপ একটি `set` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: set[int]


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'set_type'
```

## `string_not_ascii` { #string_not_ascii }

এই এরর ওঠে যখন ইনপুট স্ট্রিংয়ে ASCII নয় এমন অক্ষর থাকে (বাংলা অক্ষরও ASCII নয়):

```python
from typing import Annotated

from pydantic import BaseModel, StringConstraints, ValidationError


class Model(BaseModel):
    v: Annotated[str, StringConstraints(ascii_only=True)]


try:
    Model(v='caf\u00e9')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_not_ascii'
```

## `string_pattern_mismatch` { #string_pattern_mismatch }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `pattern` শর্তের সাথে মেলে না:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(pattern='test')


try:
    Model(x='1')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_pattern_mismatch'
```

## `string_too_long` { #string_too_long }

এই এরর ওঠে যখন ইনপুট মান এমন একটি স্ট্রিং যার দৈর্ঘ্য ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(max_length=3)


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_too_long'
```

## `string_too_short` { #string_too_short }

এই এরর ওঠে যখন ইনপুট মান এমন একটি স্ট্রিং যার দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(min_length=3)


try:
    Model(x='t')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_too_short'
```

## `string_type` { #string_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `str` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_type'
```

strict ফিল্ডে ইনপুট মান `str`-এর instance না হলেও এই এরর ওঠে।

## `string_unicode` { #string_unicode }

এই এরর ওঠে যখন মানটি একটি Unicode স্ট্রিং হিসেবে পার্স করা যায় না:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model(x=b'\x81')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_unicode'
```

## `time_delta_parsing` { #time_delta_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `timedelta` ফিল্ডের জন্য পার্স করা যায় না:

```python
from datetime import timedelta

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: timedelta


try:
    Model(x='t')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_delta_parsing'
```

## `time_delta_type` { #time_delta_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `timedelta` ফিল্ডের জন্য বৈধ নয়:

```python
from datetime import timedelta

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: timedelta


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_delta_type'
```

strict ফিল্ডে ইনপুট মান `timedelta`-এর instance না হলেও এই এরর ওঠে।

## `time_parsing` { #time_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `time` ফিল্ডের জন্য পার্স করা যায় না:

```python
from datetime import time

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: time


try:
    Model(x='25:20:30.400')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_parsing'
```

## `time_type` { #time_type }

এই এরর ওঠে যখন মানের টাইপ একটি `time` ফিল্ডের জন্য বৈধ নয়:

```python
from datetime import time

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: time


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_type'
```

strict ফিল্ডে ইনপুট মান `time`-এর instance না হলেও এই এরর ওঠে।

## `timezone_aware` { #timezone_aware }

এই এরর ওঠে যখন একটি timezone-সহ (timezone-aware) `datetime` ফিল্ডের জন্য দেওয়া `datetime` মানে
timezone-এর তথ্য নেই:

```python
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ValidationError


class Model(BaseModel):
    x: AwareDatetime


try:
    Model(x=datetime.now())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'timezone_aware'
```

## `timezone_naive` { #timezone_naive }

এই এরর ওঠে যখন একটি timezone-ছাড়া (timezone-naive) `datetime` ফিল্ডের জন্য দেওয়া `datetime` মানে
timezone-এর তথ্য আছে:

```python
from datetime import datetime, timezone

from pydantic import BaseModel, NaiveDatetime, ValidationError


class Model(BaseModel):
    x: NaiveDatetime


try:
    Model(x=datetime.now(tz=timezone.utc))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'timezone_naive'
```

## `too_long` { #too_long }

এই এরর ওঠে যখন ইনপুট মানের দৈর্ঘ্য (যেমন তালিকার আইটেম সংখ্যা) ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: list[int] = Field(max_length=3)


try:
    Model(x=[1, 2, 3, 4])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'too_long'
```

## `too_short` { #too_short }

এই এরর ওঠে যখন মানের দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: list[int] = Field(min_length=3)


try:
    Model(x=[1, 2])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'too_short'
```

## `tuple_type` { #tuple_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `tuple` ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: tuple[int]


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'tuple_type'
```

strict ফিল্ডে ইনপুট মান `tuple`-এর instance না হলেও এই এরর ওঠে।

## `unexpected_keyword_argument` { #unexpected_keyword_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি positional-only
আর্গুমেন্টের মান keyword দিয়ে দেন:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int, /):
    return a


try:
    foo(a=2)
except ValidationError as exc:
    print(repr(exc.errors()[1]['type']))
    #> 'unexpected_keyword_argument'
```

pydantic.dataclasses আর `extra=forbid` ব্যবহার করলেও এটি ওঠে:

```python
from pydantic import TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass


@dataclass(config={'extra': 'forbid'})
class Foo:
    bar: int


try:
    TypeAdapter(Foo).validate_python({'bar': 1, 'foobar': 2})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'unexpected_keyword_argument'
```

## `unexpected_positional_argument` { #unexpected_positional_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি keyword-only
আর্গুমেন্টের মান positional হিসেবে দেন:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(*, a: int):
    return a


try:
    foo(2)
except ValidationError as exc:
    print(repr(exc.errors()[1]['type']))
    #> 'unexpected_positional_argument'
```

## `union_tag_invalid` { #union_tag_invalid }

এই এরর ওঠে যখন ইনপুটের discriminator প্রত্যাশিত মানগুলোর একটি নয়:

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['blackcat']


class WhiteCat(BaseModel):
    pet_type: Literal['whitecat']


class Model(BaseModel):
    cat: BlackCat | WhiteCat = Field(discriminator='pet_type')


try:
    Model(cat={'pet_type': 'dog'})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'union_tag_invalid'
```

## `union_tag_not_found` { #union_tag_not_found }

এই এরর ওঠে যখন ইনপুট থেকে একটি discriminator মান বের করা সম্ভব নয় (discriminator ফিল্ডটিই নেই):

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['blackcat']


class WhiteCat(BaseModel):
    pet_type: Literal['whitecat']


class Model(BaseModel):
    cat: BlackCat | WhiteCat = Field(discriminator='pet_type')


try:
    Model(cat={'name': 'blackcat'})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'union_tag_not_found'
```

## `url_parsing` { #url_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি URL হিসেবে পার্স করা যায় না:

```python
from pydantic import AnyUrl, BaseModel, ValidationError


class Model(BaseModel):
    x: AnyUrl


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_parsing'
```

## `url_scheme` { #url_scheme }

এই এরর ওঠে যখন URL-এর scheme (যেমন `http`, `ftp`) ফিল্ডের URL টাইপের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x='ftp://example.com')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_scheme'
```

## `url_syntax_violation` { #url_syntax_violation }

এই এরর ওঠে যখন URL-এর গঠন (syntax) বৈধ নয়:

```python
from pydantic import BaseModel, Field, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl = Field(strict=True)


try:
    Model(x='http:////example.com')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_syntax_violation'
```

## `url_too_long` { #url_too_long }

এই এরর ওঠে যখন URL-এর দৈর্ঘ্য 2083-এর বেশি:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x='x' * 2084)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_too_long'
```

## `url_type` { #url_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি URL ফিল্ডের জন্য বৈধ নয়:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_type'
```

## `uuid_parsing` { #uuid_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি UUID ফিল্ডের জন্য বৈধ নয় (পার্স করা যায় না):

```python
from uuid import UUID

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    u: UUID


try:
    Model(u='12345678-124-1234-1234-567812345678')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_parsing'
```

## `uuid_type` { #uuid_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি UUID ফিল্ডের জন্য বৈধ instance নয় (str, bytes বা UUID):

```python
from uuid import UUID

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    u: UUID


try:
    Model(u=1234567812412341234567812345678)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_type'
```

## `uuid_version` { #uuid_version }

এই এরর ওঠে যখন ইনপুট মান UUID-এর সংস্করণের সাথে মেলে না:

```python
from pydantic import UUID5, BaseModel, ValidationError


class Model(BaseModel):
    u: UUID5


try:
    Model(u='a6cc5730-2261-11ee-9c43-2eb5a363657c')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_version'
```

## `value_error` { #value_error }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি `ValueError` তোলা হয় (সাধারণত আপনার নিজের validator থেকে):

```python
from pydantic import BaseModel, ValidationError, field_validator


class Model(BaseModel):
    x: str

    @field_validator('x')
    @classmethod
    def repeat_b(cls, v):
        raise ValueError()


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'value_error'
```
