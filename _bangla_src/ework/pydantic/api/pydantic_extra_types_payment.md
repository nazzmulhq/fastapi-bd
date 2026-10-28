# Payment { #payment }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: পেমেন্ট কার্ডের নম্বর, Luhn check digit আর brand শনাক্তসহ।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `PaymentCardNumber` | কার্ড নম্বর; অ্যাট্রিবিউট: `brand`, `masked`, `last4`, `bin` |
| `PaymentCardBrand` | brand-এর enum: `visa`, `mastercard`, `amex` ইত্যাদি |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.payment import PaymentCardNumber


class Card(BaseModel):
    number: PaymentCardNumber


c = Card(number='4000000000000002').number  # পরীক্ষার নম্বর
print(c.brand, c.masked, c.last4)
#> Visa 400000******0002 0002
```

/// tip | পরামর্শ

আসল কার্ড নম্বর নিজের সার্ভারে রাখা নিরাপত্তা আর আইনের (PCI DSS) দিক থেকে ঝুঁকিপূর্ণ। সাধারণত পেমেন্ট গেটওয়ের টোকেন রাখাই ভালো; লগে শুধু `masked` দেখান।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
