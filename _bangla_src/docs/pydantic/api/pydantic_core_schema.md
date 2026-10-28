# pydantic_core.core_schema { #pydantic_corecore_schema }

/// note | এই পেজে যা পাবেন

`pydantic_core.core_schema` মডিউল কী, কখন এটি দরকার হয়, আর এর ফাংশনগুলো কীভাবে চিনবেন। নিচের পূর্ণ তালিকাটি খুব বড় (শতাধিক ফাংশন আর TypedDict), তাই নামের নিয়ম জানলে খোঁজা সহজ।

///

## এক নজরে { #bn-overview }

core schema হলো Pydantic-এর ভেতরের ভাষা, যা দিয়ে Python অংশ Rust অংশকে বলে কী যাচাই করতে হবে (দেখুন [Architecture](../internals/architecture.md))। নিজের টাইপে `__get_pydantic_core_schema__` লিখলে (দেখুন [Types](../concepts/types.md#custom-types)) এই মডিউলের ফাংশন দিয়ে schema বানাতে হয়।

| নামের ধরন | কী বানায় | উদাহরণ |
| --- | --- | --- |
| `<টাইপ>_schema()` | একটি টাইপের schema | `int_schema(ge=0)`, `str_schema(max_length=10)`, `list_schema(int_schema())`, `dict_schema(...)` |
| `<টাইপ>Schema` (TypedDict) | সেই schema-র ডিকশনারির গঠন | `IntSchema`, `StrSchema`, `ModelSchema` |
| `no_info_*_validator_function(func, schema)` | validator ফাংশন যোগ, `info` ছাড়া | `no_info_after_validator_function(f, int_schema())` |
| `with_info_*_validator_function(func, schema)` | validator ফাংশন যোগ, `ValidationInfo` সহ | `with_info_before_validator_function(...)` |
| `plain_serializer_function_ser_schema(func)`, `wrap_serializer_function_ser_schema(func)` | serializer যোগ | `serialization=` আর্গুমেন্টে দিন |
| `union_schema([...])`, `tagged_union_schema(...)`, `nullable_schema(...)` | union আর ঐচ্ছিক | |
| `typed_dict_schema`, `model_schema`, `dataclass_schema` | গঠনযুক্ত ডেটা | |

```python
from typing import Any

from pydantic_core import core_schema

from pydantic import GetCoreSchemaHandler, TypeAdapter


class EvenInt(int):
    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler):
        def check(v: int) -> int:
            if v % 2:
                raise ValueError('জোড় সংখ্যা দিন')
            return v

        return core_schema.no_info_after_validator_function(check, core_schema.int_schema())


print(TypeAdapter(EvenInt).validate_python('4'))
#> 4
```

/// warning | সাবধানতা

core schema একটি নিচু-স্তরের API। এর গঠন pydantic-core-এর সংস্করণের সাথে বদলাতে পারে, আর ভুল schema দিলে এরর বার্তা বোঝা কঠিন হয়। সম্ভব হলে আগে `Annotated` আর `AfterValidator`-এর মতো উঁচু-স্তরের টুল ব্যবহার করুন।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_core.core_schema
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
