# Language { #language }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: ISO 639 অনুযায়ী ভাষার কোড আর নাম।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`pycountry` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `LanguageAlpha2` | দুই অক্ষরের কোড (ISO 639-1), যেমন `bn` |
| `ISO639_3` | তিন অক্ষরের কোড, যেমন `ben` |
| `ISO639_5` | ভাষা-পরিবারের কোড |
| `LanguageName` | ইংরেজি নাম, যেমন `Bengali` |
| `LanguageInfo` | ভাষার তথ্যের কাঠামো |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.language_code import ISO639_3, LanguageAlpha2, LanguageName


class Profile(BaseModel):
    lang: LanguageAlpha2
    lang_name: LanguageName
    lang3: ISO639_3


p = Profile(lang='bn', lang_name='Bengali', lang3='ben')
print(p.lang.name, p.lang.alpha3, p.lang_name.alpha2)
#> Bengali ben bn
```

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
