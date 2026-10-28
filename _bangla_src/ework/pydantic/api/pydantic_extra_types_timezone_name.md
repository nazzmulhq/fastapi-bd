# Timezone Name { #timezone-name }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: IANA timezone-এর নাম, যেমন `Asia/Dhaka`।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই (Windows-এ `tzdata` লাগতে পারে); সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `TimeZoneName` | বৈধ IANA timezone নাম |
| `TimeZoneNameSettings` | কঠোরতার সেটিং (বড়-ছোট হাতের অক্ষর মানবে কিনা) |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName


class User(BaseModel):
    tz: TimeZoneName


print(User(tz='Asia/Dhaka'))
#> tz='Asia/Dhaka'
```

/// tip | পরামর্শ

ব্যবহারকারীর timezone নাম রাখুন, offset (`+06:00`) নয়; নাম থেকে daylight saving-সহ সঠিক সময় হিসাব করা যায়।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
