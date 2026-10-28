# Coordinate { #coordinate }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: ভৌগোলিক অবস্থান: অক্ষাংশ (latitude, −90 থেকে 90) আর দ্রাঘিমাংশ (longitude, −180 থেকে 180)।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `Latitude` | অক্ষাংশ, −90 থেকে 90 |
| `Longitude` | দ্রাঘিমাংশ, −180 থেকে 180 |
| `Coordinate` | দুটো একসাথে; tuple `(23.81, 90.41)` বা লেখা `"23.81,90.41"` গ্রহণ করে; `.latitude`, `.longitude` |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel, ValidationError
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude


class Shop(BaseModel):
    loc: Coordinate


print(Shop(loc=(23.8103, 90.4125)))  # ঢাকা
#> loc=Coordinate(latitude=23.8103, longitude=90.4125)
print(Shop(loc='23.8103,90.4125').loc.latitude)
#> 23.8103


class Point(BaseModel):
    lat: Latitude
    lng: Longitude


try:
    Point(lat=95, lng=0)
except ValidationError as e:
    print(e.errors()[0]['type'])
    #> less_than_equal
```

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.coordinate
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
