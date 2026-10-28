# Functional Validators { #functional-validators }

/// note | এই পেজে যা পাবেন

* `field_validator`, `model_validator` decorator আর `AfterValidator`, `BeforeValidator`, `PlainValidator`, `WrapValidator`-এর প্যারামিটার আর পার্থক্য।
* `InstanceOf`, `SkipValidation`, `ValidateAs` বিশেষ টাইপ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

validator-এর ধারণা, চার মোডের পার্থক্য আর বিস্তারিত উদাহরণ: [Validators](../concepts/validators.md)। এই পেজ হলো দ্রুত খোঁজার সারণি।

| সদস্য | ধরন | কী করে |
| --- | --- | --- |
| `AfterValidator(func)` | `Annotated` metadata | Pydantic-এর যাচাইয়ের পরে `func` চালায় |
| `BeforeValidator(func, json_schema_input_type=...)` | `Annotated` metadata | যাচাইয়ের আগে কাঁচা ইনপুটে `func` চালায় |
| `PlainValidator(func, json_schema_input_type=Any)` | `Annotated` metadata | Pydantic-এর যাচাইয়ের বদলে শুধু `func` |
| `WrapValidator(func, json_schema_input_type=...)` | `Annotated` metadata | `func(value, handler)`; `handler` ডেকে ভেতরের যাচাই |
| `@field_validator(*fields, mode='after', check_fields=None, json_schema_input_type=...)` | decorator (classmethod) | এক বা একাধিক ফিল্ডের validator |
| `@model_validator(mode=...)` | decorator | পুরো মডেলের validator; `mode` বাধ্যতামূলক: `'before'`, `'after'`, `'wrap'` |
| `InstanceOf[T]` | টাইপ | শুধু `isinstance(value, T)` পরীক্ষা |
| `SkipValidation[T]` | টাইপ | এই ফিল্ডের যাচাই বাদ |
| `ValidateAs(from_type, instantiation_hook)` | `Annotated` metadata | অন্য টাইপ হিসেবে যাচাই করে, তারপর ফাংশন দিয়ে নিজের টাইপ বানায় |
| `ModelWrapValidatorHandler` | টাইপ hint | মডেল wrap validator-এর `handler`-এর টাইপ |

### `@field_validator` প্যারামিটার { #bn-field-validator }

| প্যারামিটার | কী করে |
| --- | --- |
| `field, *fields` | যে ফিল্ড(গুলো)র নাম; সব ফিল্ডের জন্য `'*'` |
| `mode` | `'after'` (ডিফল্ট), `'before'`, `'plain'`, `'wrap'` |
| `check_fields` | ফিল্ডের নাম মডেলে আছে কিনা পরীক্ষা করবে কিনা (base class-এ `False`) |
| `json_schema_input_type` | before/plain/wrap মোডে JSON Schema-তে ইনপুটের টাইপ |

## উদাহরণ: বারবার ব্যবহারযোগ্য মোবাইল নম্বর টাইপ { #bn-example }

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel, BeforeValidator


def check_bd_mobile(v: str) -> str:
    if not (v.startswith('01') and len(v) == 11):
        raise ValueError('বাংলাদেশি মোবাইল নম্বর নয়')
    return v


Phone = Annotated[
    str,
    BeforeValidator(lambda v: v.replace('-', '').replace(' ', '')),  # আগে: ড্যাশ আর ফাঁকা বাদ
    AfterValidator(check_bd_mobile),  # পরে: নিয়ম পরীক্ষা
]


class Contact(BaseModel):
    phone: Phone


print(Contact(phone='017-1234 5678'))
#> phone='01712345678'
```

/// info | কোডটি সহজ ভাষায়

`BeforeValidator` কাঁচা লেখা থেকে `-` আর ফাঁকা সরায়; তারপর Pydantic দেখে এটি `str` কিনা; শেষে `AfterValidator` নিয়ম মেলায়। `Phone` টাইপটি এখন যেকোনো মডেলে আবার ব্যবহার করা যায়।

///

/// check | সংক্ষেপে মনে রাখুন

* বারবার ব্যবহার: `Annotated[T, AfterValidator(f)]`; এক মডেলে: `@field_validator('x')` + `@classmethod`।
* একাধিক ফিল্ড মিলিয়ে: `@model_validator(mode='after')`।
* validator-এ মান ফেরত দিতে ভুলবেন না; এরর তুলতে `ValueError`।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
