# Routing Numbers { #routing-numbers }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: আমেরিকার ব্যাংকের ABA routing number (৯ অঙ্ক, checksum পরীক্ষাসহ)।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `ABARoutingNumber` | ৯ অঙ্কের মার্কিন ব্যাংক routing number |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.routing_number import ABARoutingNumber


class BankAccount(BaseModel):
    routing: ABARoutingNumber


print(BankAccount(routing='122105155'))
#> routing='122105155'
```

/// tip | পরামর্শ

এটি শুধু মার্কিন ব্যাংকের জন্য; বাংলাদেশের ব্যাংকের routing number-এর জন্য নয়।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.routing_number
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
