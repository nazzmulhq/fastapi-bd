# Script Code { #script-code }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: ISO 15924 অনুযায়ী লিপির (script) চার অক্ষরের কোড।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`pycountry` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `ISO_15924` | লিপির কোড, যেমন বাংলা লিপি `Beng`, লাতিন `Latn` |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.script_code import ISO_15924


class Font(BaseModel):
    script: ISO_15924


print(Font(script='Beng'))
#> script='Beng'
```

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
