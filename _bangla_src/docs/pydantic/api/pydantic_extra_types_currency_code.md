# Currency { #currency }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: ISO 4217 মুদ্রার কোড।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`pycountry` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `ISO4217` | যেকোনো ISO 4217 কোড; ছোট হাতে দিলেও বড় হাতে বদলে নেয় |
| `Currency` | বর্তমানে চালু মুদ্রার কোড (বাতিল আর বিশেষ কোড বাদ) |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.currency_code import ISO4217, Currency


class Price(BaseModel):
    amount: float
    currency: Currency
    settle_in: ISO4217


print(Price(amount=100, currency='BDT', settle_in='usd'))
#> amount=100.0 currency='BDT' settle_in='USD'
```

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.currency_code
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
