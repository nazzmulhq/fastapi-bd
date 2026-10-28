# Country { #country }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: ISO 3166 অনুযায়ী দেশের কোড আর নাম।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`pycountry` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `CountryAlpha2` | দুই অক্ষরের কোড, যেমন `BD` |
| `CountryAlpha3` | তিন অক্ষরের কোড, যেমন `BGD` |
| `CountryNumericCode` | সংখ্যার কোড, যেমন `050` |
| `CountryShortName` | ইংরেজি ছোট নাম, যেমন `Bangladesh` |
| `CountryInfo` | দেশের সব তথ্যের কাঠামো |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.country import CountryAlpha2, CountryAlpha3


class Address(BaseModel):
    country: CountryAlpha2
    country3: CountryAlpha3


a = Address(country='BD', country3='BGD')
print(a.country.alpha3, a.country.short_name, a.country.numeric_code)
#> BGD Bangladesh 050
```

/// tip | পরামর্শ

প্রতিটি টাইপ থেকে অন্য রূপগুলো অ্যাট্রিবিউট হিসেবে পাওয়া যায়: `.alpha2`, `.alpha3`, `.numeric_code`, `.short_name`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.country
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
