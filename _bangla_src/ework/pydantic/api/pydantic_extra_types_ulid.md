# ULID { #ulid }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: [ULID](https://github.com/ulid/spec): সময় অনুযায়ী সাজানো যায় এমন ২৬ অক্ষরের অনন্য পরিচয় নম্বর।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`python-ulid` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `ULID` | ULID লেখা, bytes বা সংখ্যা গ্রহণ করে `ulid.ULID` অবজেক্ট বানায় |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.ulid import ULID


class Order(BaseModel):
    id: ULID


print(Order(id='01ARZ3NDEKTSV4RRFFQ69G5FAV'))
#> id=ULID(01ARZ3NDEKTSV4RRFFQ69G5FAV)
```

/// tip | পরামর্শ

UUID4-এর মতোই অনন্য, কিন্তু শুরুর অংশে সময় থাকে বলে তৈরির ক্রমে সাজানো যায়; ডেটাবেসের index-এর জন্য সুবিধাজনক।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
