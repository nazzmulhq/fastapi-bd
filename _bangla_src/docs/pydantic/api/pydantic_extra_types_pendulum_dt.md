# Pendulum { #pendulum }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: [pendulum](https://pendulum.eustace.io/) লাইব্রেরির তারিখ-সময়ের টাইপ।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`pendulum` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `DateTime` | timezone-সহ pendulum `DateTime` |
| `Date` | pendulum `Date` |
| `Time` | pendulum `Time` |
| `Duration` | pendulum `Duration`; ISO 8601 সময়কাল (`P1DT2H`) গ্রহণ করে |
| `DateTimeSettings` | পার্সিংয়ের সেটিং (যেমন strict) |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime, Duration


class Event(BaseModel):
    start: DateTime
    length: Duration


e = Event(start='2024-03-26T10:00:00+06:00', length='P1DT2H')
print(e.start.timezone_name, e.length)
#> +06:00 1 day 2 hours
```

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.pendulum_dt
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
