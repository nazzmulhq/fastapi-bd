# গতিশীল মডেল (Dynamic models) { #dynamic-models }

/// note | এই পেজে যা শিখবেন

* চলার সময় `create_model()` দিয়ে নতুন মডেল তৈরি।
* একটি বিদ্যমান মডেল থেকে "সব ফিল্ড ঐচ্ছিক" এমন নতুন মডেল বানানো (যেমন PATCH রিকোয়েস্টের জন্য)।
* `FieldInfo.asdict()` দিয়ে ফিল্ডের annotation, metadata আর attribute আলাদা করে আবার ব্যবহার।

///

[`create_model()`][pydantic.create_model] factory ফাংশন দিয়ে মডেল [গতিশীলভাবে তৈরি](../concepts/models.md#dynamic-model-creation) করা যায়।

এই উদাহরণে দেখাব কীভাবে একটি বিদ্যমান মডেল থেকে গতিশীলভাবে একটি মডেল তৈরি করা যায়, যেখানে প্রতিটি ফিল্ড ঐচ্ছিক। এটি করতে
আমরা [`model_fields`][pydantic.main.BaseModel.model_fields] মডেল ক্লাস অ্যাট্রিবিউট ব্যবহার করব, আর ফিল্ডের সংজ্ঞা থেকে নতুন annotation তৈরি করে
[`create_model()`][pydantic.create_model] factory-তে পাঠাব। অবশ্যই এই উদাহরণ এমন যেকোনো ক্ষেত্রে প্রযোজ্য
যেখানে একটি মডেল থেকে আরেকটি নতুন মডেল বানাতে হয় (ডিফল্ট মান বাদ দেওয়া, alias যোগ করা ইত্যাদি)।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি ছাপানো ফর্মে সব ঘর বাধ্যতামূলক ("নাম*", "বয়স*")। তথ্য *আপডেট* করার ফর্মে মানুষ শুধু যা বদলাতে চায় তা-ই লিখবে। এখানে আমরা মূল ফর্মটি হাতে আবার না লিখে, কোড দিয়ে একটি কপি বানাচ্ছি যেখানে সব তারকা (*) মুছে দেওয়া, অর্থাৎ সব ঘর ঐচ্ছিক, কিন্তু অন্য সব নিয়ম (যেমন "বয়স ১-এর বেশি") অক্ষুণ্ণ।

///

/// tab | Python 3.10

```python linenums="1"
from typing import Annotated

from pydantic import BaseModel, Field, create_model


def make_fields_optional(model_cls: type[BaseModel]) -> type[BaseModel]:
    new_fields = {}

    for f_name, f_info in model_cls.model_fields.items():
        f_dct = f_info.asdict()
        new_fields[f_name] = (
            Annotated[(f_dct['annotation'] | None, *f_dct['metadata'], Field(**f_dct['attributes']))],
            None,
        )

    return create_model(
        f'{model_cls.__name__}Optional',
        __base__=model_cls,  # (1)!
        **new_fields,
    )
```

1. মূল মডেলকে base হিসেবে ব্যবহার করলে [validator](../concepts/validators.md), [computed field](../concepts/fields.md#the-computed_field-decorator) ইত্যাদি উত্তরাধিকারে পাওয়া যায়।
অভিভাবকের ফিল্ডগুলো আমাদের সংজ্ঞায়িত ফিল্ড দিয়ে বদলে যায়।

///

/// tab | Python 3.11 ও তার ওপরে

```python linenums="1"
from typing import Annotated

from pydantic import BaseModel, Field, create_model


def make_fields_optional(model_cls: type[BaseModel]) -> type[BaseModel]:
    new_fields = {}

    for f_name, f_info in model_cls.model_fields.items():
        f_dct = f_info.asdict()
        new_fields[f_name] = (
            Annotated[f_dct['annotation'] | None, *f_dct['metadata'], Field(**f_dct['attributes'])],
            None,
        )

    return create_model(
        f'{model_cls.__name__}Optional',
        __base__=model_cls,  # (1)!
        **new_fields,
    )
```

1. মূল মডেলকে base হিসেবে ব্যবহার করলে [validator](../concepts/validators.md), [computed field](../concepts/fields.md#the-computed_field-decorator) ইত্যাদি উত্তরাধিকারে পাওয়া যায়।
অভিভাবকের ফিল্ডগুলো আমাদের সংজ্ঞায়িত ফিল্ড দিয়ে বদলে যায়।

///

প্রতিটি ফিল্ডের জন্য, আমরা [`asdict()`][pydantic.fields.FieldInfo.asdict] মেথড দিয়ে [`FieldInfo`][pydantic.fields.FieldInfo] instance-এর
একটি ডিকশনারি রূপ তৈরি করি, যাতে annotation, metadata আর attribute থাকে।

নিচের মডেলটি দিয়ে:

```python
class Model(BaseModel):
    f: Annotated[int, Field(gt=1), WithJsonSchema({'extra': 'data'}), Field(title='F')] = 1
```

`f`-এর [`FieldInfo`][pydantic.fields.FieldInfo] instance-এর ডিকশনারি রূপে তিনটি আইটেম থাকবে:

* `annotation`: `int`।
* `metadata`: টাইপ-নির্দিষ্ট শর্ত আর অন্যান্য metadata-র একটি তালিকা: `[Gt(1), WithJsonSchema({'extra': 'data'})]`।
* `attributes`: ফিল্ড-নির্দিষ্ট বাকি attribute: `{'title': 'F'}`।

এটি মাথায় রেখে, আমরা এমন একটি annotation আবার তৈরি করতে পারি যা মূল মডেলেরটিকে "অনুকরণ" করে:

/// tab | Python 3.10 ও তার ওপরে

```python
new_annotation = Annotated[(
    f_dct['annotation'] | None,  # (1)!
    *f_dct['metadata'],  # (2)!
    Field(**f_dct['attributes']),  # (3)!
)]
```

1. বিদ্যমান annotation থেকে একটি নতুন annotation তৈরি করি, তবে অনুমোদিত মান হিসেবে `None` যোগ করে
   (আগের উদাহরণে, এটি `int | None`-এর সমান)।

2. আবার ব্যবহারের জন্য metadata খুলে দিই (আগের উদাহরণে, এটি [`Annotated`][typing.Annotated]
   metadata হিসেবে `Field(gt=1)` আর `WithJsonSchema({'extra': 'data'})` দেওয়ার সমান)।

3. [`Field()`][pydantic.Field] ফাংশন দিয়ে ফিল্ড-নির্দিষ্ট attribute দিই
   (আগের উদাহরণে, এটি `Field(title='F')`-এর সমান)।

///

/// tab | Python 3.11 ও তার ওপরে

```python
new_annotation = Annotated[
    f_dct['annotation'] | None,  # (1)!
    *f_dct['metadata'],  # (2)!
    Field(**f_dct['attributes']),  # (3)!
]
```

1. বিদ্যমান annotation থেকে একটি নতুন annotation তৈরি করি, তবে অনুমোদিত মান হিসেবে `None` যোগ করে
   (আগের উদাহরণে, এটি `int | None`-এর সমান)।

2. আবার ব্যবহারের জন্য metadata খুলে দিই (আগের উদাহরণে, এটি [`Annotated`][typing.Annotated]
   metadata হিসেবে `Field(gt=1)` আর `WithJsonSchema({'extra': 'data'})` দেওয়ার সমান)।

3. [`Field()`][pydantic.Field] ফাংশন দিয়ে ফিল্ড-নির্দিষ্ট attribute দিই
   (আগের উদাহরণে, এটি `Field(title='F')`-এর সমান)।

///

আর ডিফল্ট মান হিসেবে `None` দিই ([`create_model()`][pydantic.create_model] যে ফিল্ড সংজ্ঞার tuple গ্রহণ করে, তার দ্বিতীয় উপাদান)।

আমাদের factory ফাংশনের একটি প্রদর্শনী:

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    a: Annotated[int, Field(gt=1)]


ModelOptional = make_fields_optional(Model)

m = ModelOptional()
print(m.a)
#> None
```

/// info | কোডটি সহজ ভাষায়

মূল `Model`-এ `a` বাধ্যতামূলক, তাই `Model()` এরর দিত। `ModelOptional()`-এ `a`-র ডিফল্ট `None`, তাই কিছু না দিলেও চলে। কিন্তু `ModelOptional(a=0)` দিলে এখনো এরর হবে, কারণ `gt=1` শর্তটি metadata হিসেবে নতুন মডেলেও কপি হয়েছে।

///

বাস্তবায়ন নিয়ে কয়েকটি কথা:

* আমাদের `make_fields_optional()` ফাংশন যেকোনো একটি Pydantic মডেল ক্লাস ফেরত দেয় বলে সংজ্ঞায়িত (`-> type[BaseModel]`)।
  ইনপুট ক্লাসটি ধরে রাখার একটি বিকল্প সমাধান হতে পারে একটি type variable ব্যবহার:

    /// tab | Python 3.10 ও তার ওপরে

    ```python
    ModelTypeT = TypeVar('ModelTypeT', bound=type[BaseModel])

    def make_fields_optional(model_cls: ModelTypeT) -> ModelTypeT:
        ...
    ```

    ///

    /// tab | Python 3.12 ও তার ওপরে

    ```python
    def make_fields_optional[ModelTypeT: type[BaseModel]](model_cls: ModelTypeT) -> ModelTypeT:
        ...
    ```

    ///

    তবে মনে রাখুন, static type checker বুঝতে *পারবে না* যে এখন সব ফিল্ড ঐচ্ছিক।

* ডিফল্ট মানের জন্য `None`-এর বিকল্প হিসেবে [`MISSING` sentinel](../concepts/types.md#missing-sentinel) ব্যবহার করা যায়।
  নতুন annotation আর ডিফল্ট মানে শুধু `None`-এর জায়গায় `MISSING` লিখুন।

* মূল [`FieldInfo`][pydantic.fields.FieldInfo] instance-গুলোর কপি বানিয়ে, তাতে
  ডিফল্ট যোগ করে আর/অথবা অন্য পরিবর্তন করে, তারপর সেটি [`Annotated`][typing.Annotated] metadata হিসেবে আবার ব্যবহারের লোভ হতে পারে। কিছু ক্ষেত্রে এটি
  কাজ করলেও, এটি সমর্থিত পদ্ধতি **নয়**, আর যেকোনো সময় ভেঙে যেতে বা বাতিল (deprecated) হতে পারে। আমরা জোরালোভাবে
  এই উদাহরণের পদ্ধতিটিই ব্যবহারের পরামর্শ দিই।

/// tip | `None` বনাম `MISSING`

PATCH রিকোয়েস্টে "ব্যবহারকারী `a` পাঠায়নি" আর "ব্যবহারকারী `a=None` পাঠিয়েছে" আলাদা অর্থ বহন করতে পারে (দ্বিতীয়টি মানে মান মুছে দাও)। `None` ডিফল্ট দিলে দুটো একই দেখায়; `MISSING` দিলে পার্থক্য বোঝা যায়, আর dump করার সময় না পাঠানো ফিল্ড বাদ পড়ে। বিকল্প হিসেবে `model_dump(exclude_unset=True)`-ও কাজে লাগে।

///

/// check | সংক্ষেপে মনে রাখুন

* `create_model('Name', __base__=Base, field=(annotation, default))` দিয়ে চলার সময় মডেল।
* `Model.model_fields[name].asdict()` থেকে `annotation`, `metadata`, `attributes` নিয়ে নতুন `Annotated[...]` বানান।
* `__base__=মূল_মডেল` দিলে validator আর computed field উত্তরাধিকারে আসে।
* `FieldInfo` কপি করে বদলানো সমর্থিত নয়।

///
