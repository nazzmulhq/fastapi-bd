# Errors { #errors }

/// note | এই পেজে যা পাবেন

`pydantic.errors` মডিউলের exception ক্লাসগুলো: কোড ভুলভাবে লিখলে (usage error) এগুলোর কোনোটি ওঠে। ডেটা ভুল হলে যে `ValidationError` ওঠে, সেটি আছে [pydantic_core](pydantic_core.md)-এ।

///

## এক নজরে { #bn-overview }

| ক্লাস | কখন ওঠে |
| --- | --- |
| `PydanticUserError` | Pydantic ভুলভাবে ব্যবহার করলে; অন্যগুলোর অভিভাবক। `.code` অ্যাট্রিবিউটে এররের কোড থাকে |
| `PydanticUndefinedAnnotation` | annotation-এর একটি নাম সংজ্ঞায়িত নয় (forward reference resolve হয়নি) |
| `PydanticSchemaGenerationError` | কোনো টাইপের জন্য schema তৈরি করা যায় না (যেমন অচেনা ক্লাস, `arbitrary_types_allowed` ছাড়া) |
| `PydanticInvalidForJsonSchema` | কোনো টাইপের JSON Schema বানানো যায় না |
| `PydanticImportError` | V1-এর এমন কিছু import করলে যা V2-তে সরানো হয়েছে |
| `PydanticForbiddenQualifier` | নিষিদ্ধ type qualifier (যেমন ভুল জায়গায় `ClassVar`) |
| `PydanticErrorCodes` | সম্ভাব্য সব এরর কোডের তালিকা (Literal) |

```python
from pydantic import BaseModel, PydanticUserError

try:

    class Bad(BaseModel):
        x = 1  # টাইপ annotation নেই

except PydanticUserError as e:
    print(e.code)
    #> model-field-missing-annotation
```

প্রতিটি `code`-এর ব্যাখ্যা আর সমাধান: [Usage Errors](../errors/usage_errors.md)।

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.errors
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
