# Color { #color }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: রং: CSS-এর নাম (`"green"`), hex (`"#006a4e"`), RGB/RGBA tuple, `rgb()`/`hsl()` লেখা।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `Color` | যেকোনো বৈধ রঙের রূপ গ্রহণ করে; মেথড: `as_hex()`, `as_rgb()`, `as_rgb_tuple()`, `as_hsl()`, `as_named()` |
| `RGBA` | ভেতরের লাল-সবুজ-নীল-স্বচ্ছতা মানের কাঠামো |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.color import Color


class Theme(BaseModel):
    primary: Color


t = Theme(primary='green')
print(t.primary.as_hex(), t.primary.as_rgb())
#> #008000 rgb(0, 128, 0)
print(Theme(primary=(0, 106, 78)).primary.as_hex())  # বাংলাদেশের পতাকার সবুজ
#> #006a4e
print(Theme(primary='#ff0000').primary.as_named())
#> red
```

/// tip | পরামর্শ

JSON-এ dump করলে রং hex লেখা হিসেবে যায়, যেমন `"#006a4e"`।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
