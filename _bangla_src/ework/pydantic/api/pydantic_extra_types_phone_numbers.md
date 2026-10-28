# Phone Numbers { #phone-numbers }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: আন্তর্জাতিক ফোন নম্বর, Google-এর `phonenumbers` লাইব্রেরি দিয়ে যাচাই।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`phonenumbers` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `PhoneNumber` | যেকোনো দেশের বৈধ নম্বর; দেশের কোডসহ দিতে হয় (`+880...`); ডিফল্ট আউটপুট `tel:` URI রূপ |
| `PhoneNumberValidator(default_region=None, number_format='RFC3966', supported_regions=None)` | `Annotated` metadata: ডিফল্ট দেশ, আউটপুটের ফরম্যাট (`E164`, `INTERNATIONAL`, `NATIONAL`, `RFC3966`) আর অনুমোদিত দেশ ঠিক করা |

## উদাহরণ { #bn-example }

```python
from typing import Annotated

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator

BDPhone = Annotated[str, PhoneNumberValidator(default_region='BD', number_format='E164')]


class Contact(BaseModel):
    any_phone: PhoneNumber
    bd_phone: BDPhone


print(Contact(any_phone='+8801712345678', bd_phone='01712345678'))
#> any_phone='tel:+880-1712-345678' bd_phone='+8801712345678'
```

/// tip | পরামর্শ

`default_region='BD'` দিলে ব্যবহারকারী `+880` ছাড়াই `017...` লিখতে পারে; `number_format='E164'` দিলে ডেটাবেসে সবসময় একই রূপে (`+8801712345678`) জমা থাকে।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
