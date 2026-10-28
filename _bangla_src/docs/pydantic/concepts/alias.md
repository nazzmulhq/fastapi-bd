# Alias { #alias }

/// note | এই পেজে যা শিখবেন

* alias (ফিল্ডের বিকল্প নাম) নির্দিষ্ট করার সব উপায়।
* `AliasPath` দিয়ে নেস্টেড ডেটার ভেতর থেকে মান তুলে আনা, আর `AliasChoices` দিয়ে একাধিক নামের যেকোনোটি গ্রহণ করা।
* alias generator দিয়ে সব ফিল্ডের নাম একসাথে বদলানো (যেমন `snake_case` → `camelCase`)।
* config আর প্রতিটি কলের সময় alias ব্যবহার চালু/বন্ধ করা।

///

alias হলো একটি ফিল্ডের বিকল্প নাম, যা ডেটা সিরিয়ালাইজ (লেখা) আর ডিসিরিয়ালাইজ (পড়া) করার সময় ব্যবহার হয়।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন বাসায় সবাই আপনাকে "বাবু" ডাকে, কিন্তু অফিসের কাগজে লেখা "Abdur Rahman"। একই মানুষ, দুই নাম। Pydantic-এ কোডের ভেতরের নাম (`first_name`) আর বাইরের JSON-এর নাম (`firstName` বা `fname`) আলাদা হতে পারে; alias সেই দুটি নামের মধ্যে সেতু।

///

alias নিচের উপায়গুলোতে নির্দিষ্ট করতে পারেন:

* [`Field`][pydantic.fields.Field]-এ `alias`
    * অবশ্যই একটি `str` হতে হবে
* [`Field`][pydantic.fields.Field]-এ `validation_alias`
    * `str`, [`AliasPath`][pydantic.aliases.AliasPath] বা [`AliasChoices`][pydantic.aliases.AliasChoices]-এর একটি ইনস্ট্যান্স হতে পারে
* [`Field`][pydantic.fields.Field]-এ `serialization_alias`
    * অবশ্যই একটি `str` হতে হবে
* [`Config`][pydantic.config.ConfigDict.alias_generator]-এ `alias_generator`
    * একটি callable বা [`AliasGenerator`][pydantic.aliases.AliasGenerator]-এর একটি ইনস্ট্যান্স হতে পারে

`alias`, `validation_alias` আর `serialization_alias` কীভাবে ব্যবহার করতে হয় তার উদাহরণের জন্য দেখুন [ফিল্ডের alias](../concepts/fields.md#field-aliases)।

## `AliasPath` আর `AliasChoices` { #aliaspath-and-aliaschoices }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.aliases.AliasPath`][pydantic.aliases.AliasPath]<br>
[`pydantic.aliases.AliasChoices`][pydantic.aliases.AliasChoices]<br>

///

`validation_alias` ব্যবহারের সময় সুবিধার জন্য Pydantic দুটি বিশেষ টাইপ দেয়: `AliasPath` আর `AliasChoices`।

alias ব্যবহার করে একটি ফিল্ডের পথ (path) নির্দিষ্ট করতে `AliasPath` ব্যবহার হয়। যেমন:

```python
from pydantic import BaseModel, Field, AliasPath


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))
    address: str = Field(validation_alias=AliasPath('contact', 'address'))

user = User.model_validate({  # (1)!
    'names': ['John', 'Doe'],
    'contact': {'address': '221B Baker Street'}
})
print(user)
#> first_name='John' last_name='Doe' address='221B Baker Street'
```

1. ফিল্ডের alias ব্যবহার করে একটি ডিকশনারি যাচাই করতে আমরা [`model_validate()`][pydantic.BaseModel.model_validate] ব্যবহার করছি।
   আরও বিস্তারিত জানতে [ডেটা যাচাই](./models.md#validating-data) নিয়ে ডকুমেন্টেশন দেখুন।

`'first_name'` ফিল্ডে, প্রথম নামের পথ নির্দিষ্ট করতে আমরা alias `'names'` আর ইনডেক্স `0` ব্যবহার করছি।
`'last_name'` ফিল্ডে, শেষ নামের পথ নির্দিষ্ট করতে আমরা alias `'names'` আর ইনডেক্স `1` ব্যবহার করছি।

(আর `address` এসেছে `contact` ডিকশনারির ভেতরের `address` key থেকে। অর্থাৎ `AliasPath` দিয়ে নেস্টেড ডেটার ভেতরে "ঠিকানা" ধরে মান তুলে আনা যায়, আলাদা নেস্টেড মডেল না বানিয়েই।)

একাধিক বিকল্প alias-এর একটি তালিকা নির্দিষ্ট করতে `AliasChoices` ব্যবহার হয়। তালিকায় আগে আসা বিকল্পগুলো যাচাইয়ের সময়
বেশি অগ্রাধিকার পায়। যেমন:

```python
from pydantic import BaseModel, Field, AliasChoices


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'fname'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lname'))

user = User.model_validate({'fname': 'John', 'lname': 'Doe'})  # (1)!
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'first_name': 'John', 'lname': 'Doe'})  # (2)!
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'first_name': 'John', 'fname': 'J', 'lname': 'Doe'})  # (3)!
print(user)
#> first_name='John' last_name='Doe'
```

1. আমরা দুটি ফিল্ডের জন্যই দ্বিতীয় alias বিকল্প ব্যবহার করছি।
2. আমরা `'first_name'` ফিল্ডের জন্য প্রথম alias বিকল্প আর `'last_name'` ফিল্ডের জন্য
   দ্বিতীয় alias বিকল্প ব্যবহার করছি।
3. `'first_name'` আর `'fname'` দুটোই দেওয়া হয়েছে, `'first_name'` ব্যবহার হয়েছে কারণ এর অগ্রাধিকার বেশি।

(পুরনো আর নতুন API দুটো থেকেই ডেটা আসলে, বা বিভিন্ন ক্লায়েন্ট বিভিন্ন নামে পাঠালে, `AliasChoices` দিয়ে সব নাম গ্রহণ করা যায়।)

`AliasPath`-এর সাথে `AliasChoices`-ও ব্যবহার করতে পারেন:

```python
from pydantic import BaseModel, Field, AliasPath, AliasChoices


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', AliasPath('names', 0)))
    last_name: str = Field(validation_alias=AliasChoices('last_name', AliasPath('names', 1)))


user = User.model_validate({'first_name': 'John', 'last_name': 'Doe'})
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'names': ['John', 'Doe']})
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'names': ['John'], 'last_name': 'Doe'})
print(user)
#> first_name='John' last_name='Doe'
```

## alias generator ব্যবহার { #using-alias-generators }

একটি মডেলের সব ফিল্ডের alias তৈরি করবে এমন একটি callable (অথবা `AliasGenerator`-এর মাধ্যমে একগুচ্ছ callable) নির্দিষ্ট করতে
[`Config`][pydantic.config.ConfigDict.alias_generator]-এর `alias_generator` প্যারামিটার ব্যবহার করতে পারেন।
এটি কাজের যদি একটি মডেলের সব ফিল্ডের জন্য একটি সামঞ্জস্যপূর্ণ নামকরণের নিয়ম চান, কিন্তু প্রতিটি ফিল্ডের জন্য আলাদা করে
alias লিখতে না চান।

/// note | নোট

Pydantic তিনটি বিল্ট-ইন alias generator দেয়, যা সরাসরি ব্যবহার করতে পারেন:

[`to_pascal`][pydantic.alias_generators.to_pascal]<br>
[`to_camel`][pydantic.alias_generators.to_camel]<br>
[`to_snake`][pydantic.alias_generators.to_snake]<br>

(যেমন `first_name` → `to_pascal` দিলে `FirstName`, `to_camel` দিলে `firstName`।)

///

### একটি callable ব্যবহার { #using-a-callable }

একটি callable ব্যবহারের একটি মৌলিক উদাহরণ:

```python
from pydantic import BaseModel, ConfigDict


class Tree(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: field_name.upper()
    )

    age: int
    height: float
    kind: str


t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'})
print(t.model_dump(by_alias=True))
#> {'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'}
```

(এখানে প্রতিটি ফিল্ডের alias তার নামের বড় হাতের রূপ: `age` → `AGE`। তাই ইনপুটে বড় হাতের key দিতে হয়, আর `by_alias=True` দিয়ে লিখলেও বড় হাতে বের হয়।)

### একটি `AliasGenerator` ব্যবহার { #using-an-aliasgenerator }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.aliases.AliasGenerator`][pydantic.aliases.AliasGenerator]<br>

///

`AliasGenerator` এমন একটি ক্লাস যা দিয়ে একটি মডেলের জন্য একাধিক alias generator নির্দিষ্ট করা যায়।
যাচাই আর সিরিয়ালাইজেশনের জন্য ভিন্ন ভিন্ন alias generator নির্দিষ্ট করতে একটি `AliasGenerator` ব্যবহার করতে পারেন।

এটি বিশেষ করে কাজের যদি ডেটা লোড আর সংরক্ষণের জন্য ভিন্ন নামকরণের নিয়ম লাগে,
কিন্তু প্রতিটি ফিল্ডের জন্য আলাদা করে যাচাই আর সিরিয়ালাইজেশনের alias লিখতে না চান।

যেমন:

```python
from pydantic import AliasGenerator, BaseModel, ConfigDict


class Tree(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: field_name.upper(),
            serialization_alias=lambda field_name: field_name.title(),
        )
    )

    age: int
    height: float
    kind: str


t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'})
print(t.model_dump(by_alias=True))
#> {'Age': 12, 'Height': 1.2, 'Kind': 'oak'}
```

(পড়ার সময় বড় হাতের `AGE`, লেখার সময় শুধু প্রথম অক্ষর বড় `Age`।)

## alias-এর অগ্রাধিকার { #alias-precedence }

যদি [`Field`][pydantic.fields.Field]-এ একটি `alias` নির্দিষ্ট করেন, তাহলে ডিফল্টভাবে এটি তৈরি হওয়া alias-এর চেয়ে অগ্রাধিকার পাবে:

```python
from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class Voice(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    name: str
    language_code: str = Field(alias='lang')


voice = Voice(Name='Filiz', lang='tr-TR')
print(voice.language_code)
#> tr-TR
print(voice.model_dump(by_alias=True))
#> {'Name': 'Filiz', 'lang': 'tr-TR'}
```

(`name`-এর alias generator থেকে এসেছে `Name`, কিন্তু `language_code`-এ নিজে `alias='lang'` দেওয়ায় generator-এর `LanguageCode`-এর বদলে `lang` ব্যবহার হয়েছে।)

### alias-এর প্রাধান্য (priority) { #alias-priority }

এই আচরণ বদলাতে একটি ফিল্ডে `alias_priority` সেট করতে পারেন:

* `alias_priority=2` হলে alias generator alias-টিকে ওভাররাইড *করবে না*।
* `alias_priority=1` হলে alias generator alias-টিকে ওভাররাইড *করবে*।
* `alias_priority` সেট না করা থাকলে:
    * alias সেট থাকলে: alias generator alias-টিকে ওভাররাইড *করবে না*।
    * alias সেট না থাকলে: alias generator alias-টিকে ওভাররাইড *করবে*।

`validation_alias` আর `serialization_alias`-এর ক্ষেত্রেও একই অগ্রাধিকার প্রযোজ্য।
বিভিন্ন ফিল্ড alias নিয়ে আরও দেখুন [ফিল্ডের alias](../concepts/fields.md#field-aliases)-এ।

## alias-এর configuration { #alias-configuration }

alias ব্যবহার হবে কিনা তা নিয়ন্ত্রণ করতে [`ConfigDict`](./config.md) সেটিং অথবা চলমান অবস্থার যাচাই/সিরিয়ালাইজেশন
সেটিং ব্যবহার করতে পারেন।

### `ConfigDict` সেটিং { #configdict-settings }

মডেল স্তরে যাচাই আর সিরিয়ালাইজেশনে alias ব্যবহার হবে কিনা তা নিয়ন্ত্রণ করতে
[configuration সেটিং](./config.md) ব্যবহার করতে পারেন। যদি নেস্টেড মডেলের জন্য/config-মডেলের সীমানা ছাড়িয়ে এই আচরণ
নিয়ন্ত্রণ করতে চান, তাহলে [চলমান অবস্থার সেটিং](#runtime-settings) ব্যবহার করুন।

#### যাচাই { #validation }

ডেটা যাচাইয়ের সময়, অ্যাট্রিবিউটের নাম, alias বা দুটো দিয়েই অ্যাট্রিবিউট পূরণ চালু করতে পারেন।
**ডিফল্টভাবে**, Pydantic যাচাইয়ের জন্য alias ব্যবহার করে। আরও configuration পাওয়া যায় এগুলোর মাধ্যমে:

* [`ConfigDict.validate_by_alias`][pydantic.config.ConfigDict.validate_by_alias]: ডিফল্টভাবে `True`
* [`ConfigDict.validate_by_name`][pydantic.config.ConfigDict.validate_by_name]: ডিফল্টভাবে `False`

/// tab | `validate_by_alias`

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=False)


print(repr(Model(my_alias='foo')))  # (1)!
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য alias `my_alias` ব্যবহার হয়েছে।

///

/// tab | `validate_by_name`

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')

    model_config = ConfigDict(validate_by_alias=False, validate_by_name=True)


print(repr(Model(my_field='foo')))  # (1)!
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য অ্যাট্রিবিউটের নাম `my_field` ব্যবহার হয়েছে।

///

/// tab | `validate_by_alias` আর `validate_by_name`

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)


print(repr(Model(my_alias='foo')))  # (1)!
#> Model(my_field='foo')

print(repr(Model(my_field='foo')))  # (2)!
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য alias `my_alias` ব্যবহার হয়েছে।
2. যাচাইয়ের জন্য অ্যাট্রিবিউটের নাম `my_field` ব্যবহার হয়েছে।

///

/// warning | সতর্কতা

`validate_by_alias` আর `validate_by_name` দুটোই `False` সেট করতে পারবেন না।
এই ক্ষেত্রে একটি [ব্যবহারকারীর এরর](../errors/usage_errors.md#validate-by-alias-and-name-false) হয়।

///

#### সিরিয়ালাইজেশন { #serialization }

ডেটা সিরিয়ালাইজ করার সময়, alias দিয়ে সিরিয়ালাইজেশন চালু করতে পারেন, যা ডিফল্টভাবে বন্ধ থাকে।
আরও বিস্তারিত জানতে [`ConfigDict.serialize_by_alias`][pydantic.config.ConfigDict.serialize_by_alias]-এর API ডকুমেন্টেশন
দেখুন।

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    my_field: str = Field(serialization_alias='my_alias')

    model_config = ConfigDict(serialize_by_alias=True)


m = Model(my_field='foo')
print(m.model_dump())  # (1)!
#> {'my_alias': 'foo'}
```

1. সিরিয়ালাইজেশনের জন্য alias `my_alias` ব্যবহার হয়েছে।

/// note | নোট

alias দিয়ে সিরিয়ালাইজেশন ডিফল্টভাবে বন্ধ থাকা যাচাইয়ের ডিফল্টের (যেখানে ডিফল্টভাবে alias ব্যবহার হয়) সাথে
লক্ষণীয়ভাবে অসংগত। আমরা V3-তে এই ডিফল্ট বদলানোর আশা করছি।

///

/// warning | সাধারণ ভুল

alias দিয়ে পড়লেন, কিন্তু `model_dump()` করলে আসল ফিল্ডের নামে বের হলো, এটা নতুনদের সবচেয়ে প্রচলিত বিভ্রান্তি। লেখার সময়ও alias চাইলে `model_dump(by_alias=True)` দিন, অথবা config-এ `serialize_by_alias=True` সেট করুন। (FastAPI `response_model` ব্যবহার করলে নিজেই `by_alias=True` দিয়ে লেখে।)

///

### চলমান অবস্থার সেটিং { #runtime-settings }

প্রতিটি কলে আলাদাভাবে যাচাই আর সিরিয়ালাইজেশনে alias ব্যবহার নিয়ন্ত্রণ করতে চলমান অবস্থার alias ফ্ল্যাগ ব্যবহার করতে পারেন।
যদি মডেল স্তরে এই আচরণ নিয়ন্ত্রণ করতে চান, তাহলে
[`ConfigDict` সেটিং](#configdict-settings) ব্যবহার করুন।

#### যাচাই { #validation_1 }

ডেটা যাচাইয়ের সময়, অ্যাট্রিবিউটের নাম, alias বা দুটো দিয়েই অ্যাট্রিবিউট পূরণ চালু করতে পারেন।

`by_alias` আর `by_name` ফ্ল্যাগ পাওয়া যায় [`model_validate()`][pydantic.main.BaseModel.model_validate],
[`model_validate_json()`][pydantic.main.BaseModel.model_validate_json] আর [`model_validate_strings()`][pydantic.main.BaseModel.model_validate_strings] মেথডে, সাথে [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর যাচাইয়ের মেথডগুলোতেও।

ডিফল্টভাবে:

* `by_alias` হলো `True`
* `by_name` হলো `False`

/// tab | `by_alias`

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')


m = Model.model_validate(
    {'my_alias': 'foo'},  # (1)!
    by_alias=True,
    by_name=False,
)
print(repr(m))
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য alias `my_alias` ব্যবহার হয়েছে।

///

/// tab | `by_name`

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')


m = Model.model_validate(
    {'my_field': 'foo'}, by_alias=False, by_name=True  # (1)!
)
print(repr(m))
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য অ্যাট্রিবিউটের নাম `my_field` ব্যবহার হয়েছে।

///

/// tab | `validate_by_alias` আর `validate_by_name`

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    my_field: str = Field(validation_alias='my_alias')


m = Model.model_validate(
    {'my_alias': 'foo'}, by_alias=True, by_name=True  # (1)!
)
print(repr(m))
#> Model(my_field='foo')

m = Model.model_validate(
    {'my_field': 'foo'}, by_alias=True, by_name=True  # (2)!
)
print(repr(m))
#> Model(my_field='foo')
```

1. যাচাইয়ের জন্য alias `my_alias` ব্যবহার হয়েছে।
2. যাচাইয়ের জন্য অ্যাট্রিবিউটের নাম `my_field` ব্যবহার হয়েছে।

///

/// warning | সতর্কতা

`by_alias` আর `by_name` দুটোই `False` সেট করতে পারবেন না।
এই ক্ষেত্রে একটি [ব্যবহারকারীর এরর](../errors/usage_errors.md#validate-by-alias-and-name-false) হয়।

///

#### সিরিয়ালাইজেশন { #serialization_1 }

ডেটা সিরিয়ালাইজ করার সময়, `by_alias` ফ্ল্যাগ দিয়ে alias দিয়ে সিরিয়ালাইজেশন চালু করতে পারেন,
যা পাওয়া যায় [`model_dump()`][pydantic.main.BaseModel.model_dump] আর
[`model_dump_json()`][pydantic.main.BaseModel.model_dump_json] মেথডে, সাথে
[`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর মেথডগুলোতেও।

ডিফল্টভাবে `by_alias` হলো `False`।

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    my_field: str = Field(serialization_alias='my_alias')


m = Model(my_field='foo')
print(m.model_dump(by_alias=True))  # (1)!
#> {'my_alias': 'foo'}
```

1. সিরিয়ালাইজেশনের জন্য alias `my_alias` ব্যবহার হয়েছে।

/// note | নোট

alias দিয়ে সিরিয়ালাইজেশন ডিফল্টভাবে বন্ধ থাকা যাচাইয়ের ডিফল্টের (যেখানে ডিফল্টভাবে alias ব্যবহার হয়) সাথে
লক্ষণীয়ভাবে অসংগত। আমরা V3-তে এই ডিফল্ট বদলানোর আশা করছি।

///

/// check | সংক্ষেপে মনে রাখুন

* `alias` = পড়া ও লেখা দুটোতেই; `validation_alias` = শুধু পড়ায়; `serialization_alias` = শুধু লেখায়।
* নেস্টেড ডেটা থেকে মান তুলতে `AliasPath`, একাধিক নাম গ্রহণ করতে `AliasChoices`।
* সব ফিল্ডে একসাথে নামের নিয়ম: `ConfigDict(alias_generator=to_camel)`।
* পড়ার সময় alias ডিফল্টভাবে চালু, লেখার সময় বন্ধ; লিখতে `by_alias=True`।

///
