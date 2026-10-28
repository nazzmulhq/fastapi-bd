# Semantic Version { #semantic-version }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: [Semantic Versioning](https://semver.org/) অনুযায়ী সংস্করণ নম্বর (`1.2.3-beta.1+build.5`)।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (`semver` লাগে; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `SemanticVersion` | সংস্করণ পার্স করে; অ্যাট্রিবিউট `major`, `minor`, `patch`, `prerelease`, `build`; তুলনা (`<`, `>`) করা যায় |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.semantic_version import SemanticVersion


class Release(BaseModel):
    version: SemanticVersion


r = Release(version='1.2.3-beta.1+build.5')
print(r.version.major, r.version.prerelease, Release(version='2.0.0').version > r.version)
#> 1 beta.1 True
```

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.semantic_version
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
