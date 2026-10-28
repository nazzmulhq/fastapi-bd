# Annotated Handlers { #annotated-handlers }

/// note | এই পেজে যা পাবেন

`GetCoreSchemaHandler` আর `GetJsonSchemaHandler`: নিজের টাইপের `__get_pydantic_core_schema__` আর `__get_pydantic_json_schema__` মেথডে যে `handler` আর্গুমেন্ট আসে, তার টাইপ।

///

## এক নজরে { #bn-overview }

| ক্লাস | কোথায় আসে | দরকারি মেথড |
| --- | --- | --- |
| `GetCoreSchemaHandler` | `__get_pydantic_core_schema__(cls, source, handler)` | `handler(source)`: ভেতরের (স্বাভাবিক) core schema; `handler.generate_schema(type)`: অন্য টাইপের schema; `handler.field_name` |
| `GetJsonSchemaHandler` | `__get_pydantic_json_schema__(cls, core_schema, handler)` | `handler(core_schema)`: স্বাভাবিক JSON schema; `handler.resolve_ref_schema(schema)`: `$ref` খুলে আসল schema; `handler.mode` |

```python
from typing import Any

from pydantic_core import core_schema

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter


class Taka(float):
    @classmethod
    def __get_pydantic_core_schema__(cls, source: Any, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(cls, handler(float))

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler: GetJsonSchemaHandler):
        json_schema = handler(schema)
        json_schema['description'] = 'টাকার অঙ্ক'
        return json_schema


print(TypeAdapter(Taka).validate_python('10.5'), TypeAdapter(Taka).json_schema())
#> 10.5 {'description': 'টাকার অঙ্ক', 'type': 'number'}
```

wrapper পদ্ধতিটি কীভাবে কাজ করে: [Architecture](../internals/architecture.md#customizing-the-core-schema-and-json-schema); নিজের টাইপ বানানো: [Types](../concepts/types.md#custom-types)।

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
