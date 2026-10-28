# Mac Address { #mac-address }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: নেটওয়ার্ক যন্ত্রের MAC ঠিকানা।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `MacAddress` | `00:1A:2B:3C:4D:5E`, `00-1A-...`, `001a.2b3c.4d5e` এর মতো রূপ গ্রহণ করে, আর ছোট হাতের `:` দেওয়া মানক রূপে রাখে |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.mac_address import MacAddress


class Device(BaseModel):
    mac: MacAddress


print(Device(mac='00:1A:2B:3C:4D:5E').mac, Device(mac='001a.2b3c.4d5e').mac)
#> 00:1a:2b:3c:4d:5e 00:1a:2b:3c:4d:5e
```

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
