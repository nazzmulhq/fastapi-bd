# Aliases { #aliases }

/// note | এই পেজে যা পাবেন

* `AliasPath`, `AliasChoices` আর `AliasGenerator`: ইনপুট বা আউটপুটে ফিল্ডের ভিন্ন নাম ব্যবহারের তিনটি টুল, উদাহরণসহ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

alias হলো ডাকনাম। কোডে ফিল্ডের নাম `full_name`, কিন্তু বাইরের API পাঠায় `fullName`। alias বলে দেয় "বাইরে থেকে এই নামে এলে আমার এই ফিল্ডে বসাও"।

///

| টুল | কী করে | উদাহরণ |
| --- | --- | --- |
| `AliasPath('address', 'city')` | নেস্টেড ডেটার ভেতর থেকে মান তুলে আনে (key বা index ধরে) | `{'address': {'city': 'ঢাকা'}}` থেকে `'ঢাকা'` |
| `AliasChoices('phone', 'mobile')` | একাধিক সম্ভাব্য নামের যেকোনোটি গ্রহণ করে; প্রথম যেটি পাওয়া যায় | `phone` বা `mobile` |
| `AliasGenerator(...)` | সব ফিল্ডের alias ফাংশন দিয়ে তৈরি; যাচাই আর dump-এর জন্য আলাদা ফাংশন দেওয়া যায় | `validation_alias=to_camel` |

`AliasPath` আর `AliasChoices` দেওয়া হয় `Field(validation_alias=...)`-এ; `AliasGenerator` দেওয়া হয় `ConfigDict(alias_generator=...)`-এ।

```python
from pydantic import AliasChoices, AliasGenerator, AliasPath, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_pascal


class Resp(BaseModel):
    city: str = Field(validation_alias=AliasPath('address', 'city'))
    phone: str = Field(validation_alias=AliasChoices('phone', 'mobile', 'tel'))


print(Resp.model_validate({'address': {'city': 'ঢাকা'}, 'mobile': '017'}))
#> city='ঢাকা' phone='017'


class G(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel, serialization_alias=to_pascal)
    )

    first_name: str


print(G.model_validate({'firstName': 'A'}).model_dump(by_alias=True))
#> {'FirstName': 'A'}
```

`AliasPath`-এ সংখ্যাও দেওয়া যায় তালিকার index বোঝাতে: `AliasPath('names', 0)` মানে `names` তালিকার প্রথম আইটেম। `AliasChoices`-এর ভেতরে `AliasPath`-ও রাখা যায়।

বিস্তারিত: [Alias](../concepts/alias.md)।

/// check | সংক্ষেপে মনে রাখুন

* নেস্টেড থেকে তোলা: `AliasPath`; একাধিক নাম গ্রহণ: `AliasChoices`; সব ফিল্ডে নিয়ম: `AliasGenerator`।
* এগুলো শুধু ইনপুটে (validation) কাজ করে, `AliasGenerator`-এ `serialization_alias` দিলে আউটপুটেও।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.aliases
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
