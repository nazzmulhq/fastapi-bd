# Experimental API { #experimental-api }

/// note | এই পেজে যা পাবেন

পরীক্ষামূলক Pipeline API আর `generate_arguments_schema()`-এর মেথডগুলোর সারণি। ধারণা আর উদাহরণ: [পরীক্ষামূলক সুবিধা](../concepts/experimental.md)। এগুলো বদলাতে পারে।

///

## Pipeline API { #pipeline-api }

`validate_as(টাইপ)` দিয়ে শুরু, তারপর ধাপ জোড়া লাগানো হয়:

| মেথড | কী করে |
| --- | --- |
| `validate_as(T)` / `validate_as(...)` | `T` হিসেবে যাচাই (`...` মানে ফিল্ডের নিজের টাইপ) |
| `validate_as_deferred(func)` | পরে সংজ্ঞায়িত টাইপের জন্য অলস যাচাই |
| `transform(func)` | মান বদলানো |
| `constrain(constraint)` | `annotated_types`-এর শর্ত প্রয়োগ |
| `predicate(func)` | `func` `False` দিলে এরর |
| `gt`, `ge`, `lt`, `le`, `len(min, max)`, `multiple_of`, `eq`, `not_eq`, `in_`, `not_in` | সংখ্যা আর দৈর্ঘ্যের শর্ত |
| `str_lower`, `str_upper`, `str_title`, `str_strip`, `str_pattern`, `str_contains`, `str_starts_with`, `str_ends_with` | স্ট্রিংয়ের রূপান্তর আর শর্ত |
| `datetime_tz_aware`, `datetime_tz_naive`, `datetime_tz(tz)`, `datetime_with_tz(tz)` | `datetime`-এর timezone শর্ত বা timezone বসানো |
| `otherwise(other)`, বা পাইপ অপারেটর | এটি ব্যর্থ হলে অন্যটি চেষ্টা (OR) |
| `then(other)`, বা `&` অপারেটর | এটির পরে অন্যটি (AND) |

::: pydantic.experimental.pipeline
    options:
        members:
        - _Pipeline
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

## Arguments schema API { #arguments-schema-api }

| ফাংশন | কী করে |
| --- | --- |
| `generate_arguments_schema(func, schema_type='arguments-v3', parameters_callback=None, config=None)` | একটি ফাংশনের আর্গুমেন্টের core schema তৈরি, যা `SchemaValidator`-এ দিয়ে ফাংশন না ডেকেই আর্গুমেন্ট যাচাই করা যায় |

::: pydantic.experimental.arguments_schema
    options:
        members:
        - generate_arguments_schema
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
