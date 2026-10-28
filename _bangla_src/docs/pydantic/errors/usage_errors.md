# Usage Errors { #usage-errors }

/// note | এই পেজে যা পাবেন

* Pydantic ভুলভাবে *ব্যবহার* করলে (ডেটা নয়, কোড ভুল হলে) যে এররগুলো আসে, তাদের অর্থ আর সমাধান।
* এগুলো সাধারণত `PydanticUserError` হিসেবে আসে, আর এররের বার্তায় এই পেজের একটি লিংক (`code`) থাকে।

///

Pydantic দরকারি এরর দেওয়ার চেষ্টা করে। নিচের অংশগুলোতে Pydantic নিয়ে কাজের সময় ডেভেলপাররা যেসব সাধারণ এরর
পেতে পারেন তার বিস্তারিত, আর এরর পরিস্থিতি সমাধানের পরামর্শ দেওয়া হলো।

/// tip | উদাহরণ দিয়ে বুঝি

Validation error মানে ডেটা ভুল (ব্যবহারকারী ভুল তথ্য দিয়েছে)। Usage error মানে কোড ভুল (আপনি Pydantic-কে ভুলভাবে বলেছেন কী করতে হবে), যেমন রান্নার রেসিপিতেই ভুল উপকরণ লেখা। তাই usage error সাধারণত মডেল সংজ্ঞায়িত হওয়ার সময়েই, অ্যাপ চালুর মুহূর্তে আসে, আর ঠিক করতে হয় কোডে।

///

## ক্লাস পুরোপুরি সংজ্ঞায়িত নয় { #class-not-fully-defined }

এই এরর ওঠে যখন pydantic-যাচাই করা একটি টাইপের (যেমন `BaseModel`-এর subclass, বা একটি pydantic `dataclass`)
annotation-এ উল্লেখ করা একটি টাইপ সংজ্ঞায়িত নয়:

```python
from typing import ForwardRef

from pydantic import BaseModel, PydanticUserError

UndefinedType = ForwardRef('UndefinedType')


class Foobar(BaseModel):
    a: UndefinedType


try:
    Foobar(a=1)
except PydanticUserError as exc_info:
    assert exc_info.code == 'class-not-fully-defined'
```

অথবা যখন টাইপটি ব্যবহারের পরে সংজ্ঞায়িত হয়েছে:

```python
from typing import Optional

from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    a: Optional['Bar'] = None


try:
    # this doesn't work, see raised error
    foo = Foo(a={'b': {'a': None}})
except PydanticUserError as exc_info:
    assert exc_info.code == 'class-not-fully-defined'


class Bar(BaseModel):
    b: 'Foo'


# this works, though
foo = Foo(a={'b': {'a': None}})
```

BaseModel subclass-এর ক্ষেত্রে, টাইপটি সংজ্ঞায়িত করে তারপর `.model_rebuild()` ডেকে এটি ঠিক করা যায়:

```python
from typing import Optional

from pydantic import BaseModel


class Foo(BaseModel):
    a: Optional['Bar'] = None


class Bar(BaseModel):
    b: 'Foo'


Foo.model_rebuild()

foo = Foo(a={'b': {'a': None}})
```

অন্য ক্ষেত্রে, উপযুক্ত টাইপ সংজ্ঞায়িত করে কীভাবে ক্লাসটি আবার তৈরি করতে হবে, এররের বার্তাতেই তা বলা থাকার কথা। বিস্তারিত: [Forward Annotations](../concepts/forward_annotations.md)।

## নিজের JSON Schema { #custom-json-schema }

V2-তে `__modify_schema__` মেথড আর সমর্থিত নয়। বদলে আপনার `__get_pydantic_json_schema__` মেথড ব্যবহার করা উচিত।

`__modify_schema__` আগে JSON schema প্রকাশ করা একটিমাত্র আর্গুমেন্ট নিত। নিচের উদাহরণ দেখুন:

```python title="Old way"
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        @classmethod
        def __modify_schema__(cls, field_schema):
            field_schema.update(examples=['example'])

except PydanticUserError as exc_info:
    assert exc_info.code == 'custom-json-schema'
```

নতুন মেথড `__get_pydantic_json_schema__` দুটি আর্গুমেন্ট নেয়: প্রথমটি `CoreSchema` নামে চিহ্নিত একটি ডিকশনারি,
আর দ্বিতীয়টি একটি callable `handler` যা প্যারামিটার হিসেবে একটি `CoreSchema` নিয়ে একটি JSON schema ফেরত দেয়। নিচের উদাহরণ
দেখুন:

```python title="New way"
from typing import Any

from pydantic_core import CoreSchema

from pydantic import BaseModel, GetJsonSchemaHandler


class Model(BaseModel):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(examples=['example'])
        return json_schema


print(Model.model_json_schema())
"""
{'examples': ['example'], 'properties': {}, 'title': 'Model', 'type': 'object'}
"""
```

## decorator-এ অবৈধ ফিল্ড { #decorator-invalid-fields }

এই এরর ওঠে যখন [`@field_validator`][pydantic.field_validator]
বা [`@field_serializer`][pydantic.field_serializer] decorator-এ দেওয়া ফিল্ডের নাম স্ট্রিং নয়।

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str
        b: str

        @field_validator(['a', 'b'])
        @classmethod
        def check_fields(cls, v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'decorator-invalid-fields'
```

ফিল্ডগুলো আলাদা আলাদা স্ট্রিং আর্গুমেন্ট হিসেবে দিতে হবে:

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    a: str
    b: str

    @field_validator('a', 'b')
    @classmethod
    def check_fields(cls, v):
        return v
```

## ফিল্ড ছাড়া decorator { #decorator-missing-arguments }

এই এরর ওঠে যখন [`@field_validator`][pydantic.field_validator] বা [`@field_serializer`][pydantic.field_serializer]
decorator কোনো আর্গুমেন্ট ছাড়া খালি ব্যবহার করা হয়।

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator
        @classmethod
        def checker(cls, v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'decorator-missing-arguments'
```

অন্তত একটি ফিল্ডের নাম (আর চাইলে আরও ফিল্ডের নাম ও keyword আর্গুমেন্ট) দিতে হবে।

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    a: str

    @field_validator('a')
    @classmethod
    def checker(cls, v):
        return v
```

## অনুপস্থিত ফিল্ডে decorator { #decorator-missing-field }

এই এরর ওঠে যখন এমন একটি ফিল্ড দিয়ে decorator সংজ্ঞায়িত করেন যা বৈধ নয় (মডেলে নেই, বা বানান ভুল)।

```python
from typing import Any

from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator('b')
        def check_b(cls, v: Any):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'decorator-missing-field'
```

মডেল থেকে উত্তরাধিকার নিচ্ছেন আর ইচ্ছা করেই এটি করেছেন হলে `check_fields=False` ব্যবহার করতে পারেন।

```python
from typing import Any

from pydantic import BaseModel, create_model, field_validator


class Model(BaseModel):
    @field_validator('a', check_fields=False)
    def check_a(cls, v: Any):
        return v


model = create_model('FooModel', a=(str, 'cake'), __base__=Model)
```

## Discriminator ফিল্ড নেই { #discriminator-no-field }

এই এরর ওঠে যখন discriminated union-এর একটি মডেল discriminator ফিল্ড সংজ্ঞায়িত করে না।

```python
from typing import Literal

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Cat | Dog = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-no-field'
```

## Discriminator alias-এর টাইপ { #discriminator-alias-type }

এই এরর ওঠে যখন একটি discriminator ফিল্ডে স্ট্রিং নয় এমন alias সংজ্ঞায়িত করেন।

```python
from typing import Literal

from pydantic import AliasChoices, BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: Literal['cat'] = Field(
        validation_alias=AliasChoices('Pet', 'PET')
    )
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Cat | Dog = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-alias-type'
```

## Discriminator-এর literal লাগে { #discriminator-needs-literal }

এই এরর ওঠে যখন একটি discriminator ফিল্ডে `Literal` নয় এমন টাইপ সংজ্ঞায়িত করেন।

```python
from typing import Literal

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: int
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Cat | Dog = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-needs-literal'
```

## Discriminator alias { #discriminator-alias }

এই এরর ওঠে যখন discriminator ফিল্ডগুলোতে ভিন্ন ভিন্ন alias সংজ্ঞায়িত করেন।

```python
from typing import Literal

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: Literal['cat'] = Field(validation_alias='PET')
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog'] = Field(validation_alias='Pet')
    d: str


try:

    class Model(BaseModel):
        pet: Cat | Dog = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-alias'
```

## অবৈধ discriminator validator { #discriminator-validator }

এই এরর ওঠে যখন একটি discriminator ফিল্ডে before, wrap বা plain validator ব্যবহার করেন।

এটি অনুমোদিত নয়, কারণ যাচাইয়ের জন্য কোন মডেল ব্যবহার হবে তা ঠিক করতে discriminator ফিল্ড ব্যবহার হয়,
তাই এমন validator ব্যবহার করা যাবে না যা এর মান বদলে দিতে পারে।

```python
from typing import Literal

from pydantic import BaseModel, Field, PydanticUserError, field_validator


class Cat(BaseModel):
    pet_type: Literal['cat']

    @field_validator('pet_type', mode='before')
    @classmethod
    def validate_pet_type(cls, v):
        if v == 'kitten':
            return 'cat'
        return v


class Dog(BaseModel):
    pet_type: Literal['dog']


try:

    class Model(BaseModel):
        pet: Cat | Dog = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-validator'
```

discriminator বাদ দিয়ে সাধারণ union ব্যবহার করে এটি এড়ানো যায়:

```python
from typing import Literal

from pydantic import BaseModel, field_validator


class Cat(BaseModel):
    pet_type: Literal['cat']

    @field_validator('pet_type', mode='before')
    @classmethod
    def validate_pet_type(cls, v):
        if v == 'kitten':
            return 'cat'
        return v


class Dog(BaseModel):
    pet_type: Literal['dog']


class Model(BaseModel):
    pet: Cat | Dog


assert Model(pet={'pet_type': 'kitten'}).pet.pet_type == 'cat'
```

## callable discriminator-এর কোনো ক্ষেত্রে tag নেই { #callable-discriminator-no-tag }

এই এরর ওঠে যখন একটি callable `Discriminator` ব্যবহার করা union-এর সব ক্ষেত্রে `Tag` annotation থাকে না।

```python
from typing import Annotated

from pydantic import BaseModel, Discriminator, PydanticUserError, Tag


def model_x_discriminator(v):
    if isinstance(v, str):
        return 'str'
    if isinstance(v, (dict, BaseModel)):
        return 'model'


# tag missing for both union choices
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            'str | DiscriminatedModel',
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'

# tag missing for `'DiscriminatedModel'` union choice
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            "Annotated[str, Tag('str')] | DiscriminatedModel",
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'

# tag missing for `str` union choice
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            "str | Annotated[DiscriminatedModel, Tag('model')]",
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'
```

## `TypedDict`-এর সংস্করণ { #typed-dict-version }

এই এরর ওঠে যখন Python < 3.12-এ `typing_extensions.TypedDict`-এর বদলে
[typing.TypedDict][] ব্যবহার করেন।

## অভিভাবক মডেলের ফিল্ড বদলে ফেলা { #model-field-overridden }

এই এরর ওঠে যখন একটি base class-এ সংজ্ঞায়িত একটি ফিল্ড annotation ছাড়া একটি অ্যাট্রিবিউট দিয়ে বদলে (override) ফেলা হয়।

```python
from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    a: float


try:

    class Bar(Foo):
        x: float = 12.3
        a = 123.0

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-field-overridden'
```

## মডেলের ফিল্ডে annotation নেই { #model-field-missing-annotation }

এই এরর ওঠে যখন একটি ফিল্ডের annotation (টাইপ) নেই।

```python
from pydantic import BaseModel, Field, PydanticUserError

try:

    class Model(BaseModel):
        a = Field('foobar')
        b = None

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-field-missing-annotation'
```

ফিল্ডটি যদি ফিল্ড হিসেবে উদ্দেশ্য না হয়, তাহলে
এটিকে `ClassVar` হিসেবে annotate করে এরর সমাধান করতে পারেন:

```python
from typing import ClassVar

from pydantic import BaseModel


class Model(BaseModel):
    a: ClassVar[str]
```

অথবা `model_config['ignored_types']` হালনাগাদ করে:

```python
from pydantic import BaseModel, ConfigDict


class IgnoredType:
    pass


class MyModel(BaseModel):
    model_config = ConfigDict(ignored_types=(IgnoredType,))

    _a = IgnoredType()
    _b: int = IgnoredType()
    _c: IgnoredType
    _d: IgnoredType = IgnoredType()
```

## `Config` আর `model_config` দুটোই সংজ্ঞায়িত { #config-both }

এই এরর ওঠে যখন `class Config` আর `model_config` একসাথে ব্যবহার করা হয়। V2-তে শুধু `model_config` ব্যবহার করুন।

```python
from pydantic import BaseModel, ConfigDict, PydanticUserError

try:

    class Model(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        a: str

        class Config:
            from_attributes = True

except PydanticUserError as exc_info:
    assert exc_info.code == 'config-both'
```

## keyword আর্গুমেন্ট সরানো হয়েছে { #removed-kwargs }

এই এরর ওঠে যখন keyword আর্গুমেন্টগুলো Pydantic V2-তে আর পাওয়া যায় না।

যেমন, Pydantic V2 থেকে `regex` সরানো হয়েছে (বদলে `pattern` ব্যবহার করুন):

```python
from pydantic import BaseModel, Field, PydanticUserError

try:

    class Model(BaseModel):
        x: str = Field(regex='test')

except PydanticUserError as exc_info:
    assert exc_info.code == 'removed-kwargs'
```

## চক্রাকার উল্লেখের schema { #circular-reference-schema }

এই এরর ওঠে যখন এমন একটি চক্রাকার উল্লেখ পাওয়া যায় যা নইলে অসীম recursion-এ গড়াত।

যেমন, এটি একটি বৈধ type alias:

```python
type A = list[A] | None
```

কিন্তু এগুলো নয়:

```python
type A = A

type B = C
type C = B
```

## JSON schema-র জন্য অবৈধ টাইপ { #invalid-for-json-schema }

এই এরর ওঠে যখন Pydantic কোনো `CoreSchema`-র জন্য JSON schema তৈরি করতে ব্যর্থ হয়।

```python
from collections.abc import Callable

from pydantic import BaseModel, PydanticUserError


class Model(BaseModel):
    a: Callable[..., object]


try:
    Model.model_json_schema()
except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-for-json-schema'
```

## JSON schema আগেই ব্যবহার হয়েছে { #json-schema-already-used }

এই এরর ওঠে যখন JSON schema generator ইতিমধ্যে একটি JSON schema তৈরিতে ব্যবহার হয়ে গেছে।
নতুন JSON schema তৈরি করতে আপনাকে একটি নতুন instance বানাতে হবে।

## BaseModel-এর instance তৈরি { #base-model-instantiated }

এই এরর ওঠে যখন সরাসরি `BaseModel`-এর instance তৈরি করেন। Pydantic মডেলকে `BaseModel` থেকে উত্তরাধিকার নিতে হবে।

```python
from pydantic import BaseModel, PydanticUserError

try:
    BaseModel()
except PydanticUserError as exc_info:
    assert exc_info.code == 'base-model-instantiated'
```

## অসংজ্ঞায়িত annotation { #undefined-annotation }

এই এরর ওঠে যখন `CoreSchema` তৈরির সময় অসংজ্ঞায়িত annotation সামলানো হয়।

```python
from pydantic import BaseModel, PydanticUndefinedAnnotation


class Model(BaseModel):
    a: 'B'  # noqa F821


try:
    Model.model_rebuild()
except PydanticUndefinedAnnotation as exc_info:
    assert exc_info.code == 'undefined-annotation'
```

## অচেনা টাইপের schema { #schema-for-unknown-type }

এই এরর ওঠে যখন Pydantic কোনো টাইপের জন্য `CoreSchema` তৈরি করতে ব্যর্থ হয়। সমাধান: `arbitrary_types_allowed=True`, অথবা টাইপে `__get_pydantic_core_schema__` বাস্তবায়ন।

```python
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        x: 43 = 123

except PydanticUserError as exc_info:
    assert exc_info.code == 'schema-for-unknown-type'
```

## Import এরর { #import-error }

এই এরর ওঠে যখন এমন একটি অবজেক্ট import করার চেষ্টা করেন যা Pydantic V1-এ ছিল, কিন্তু
Pydantic V2-তে সরানো হয়েছে।

আরও তথ্যের জন্য দেখুন [Migration Guide](../migration.md)।

## `create_model`-এর ফিল্ড সংজ্ঞা { #create-model-field-definitions }

এই এরর ওঠে যখন [`create_model()`][pydantic.create_model]-এ অবৈধ ফিল্ড সংজ্ঞা দেন।

```python
from pydantic import PydanticUserError, create_model

try:
    create_model('FooModel', foo=(str, 'default value', 'more'))
except PydanticUserError as exc_info:
    assert exc_info.code == 'create-model-field-definitions'
```

ফিল্ড সংজ্ঞার নিয়ম পাওয়া যাবে [গতিশীল মডেল তৈরি](../concepts/models.md#dynamic-model-creation) ডকুমেন্টেশনে।

## `create_model`-এর namespace { #create-model-namespace }

এই এরর ওঠে যখন [`create_model()`][pydantic.create_model]-এর `__namespace__` আর্গুমেন্টের একটি key
একটি ফিল্ডের নামের সাথে সংঘাত করে:

```python
from pydantic import PydanticUserError, create_model

try:
    create_model('FooModel', foo=int, __namespace__={'foo': 1})
except PydanticUserError as exc_info:
    assert exc_info.code == 'create-model-namespace'
```

এটি তখনও ওঠে যখন `__namespace__` আর্গুমেন্টের একটি key এমন একটি অ্যাট্রিবিউট যার জন্য আলাদা আর্গুমেন্ট আছে
(`__annotations__`, `__module__`, `__qualname__`, `__doc__` আর `model_config`):

```python
from pydantic import ConfigDict, PydanticUserError, create_model

try:
    create_model(
        'FooModel', __namespace__={'model_config': ConfigDict(strict=True)}
    )
except PydanticUserError as exc_info:
    assert exc_info.code == 'create-model-namespace'
```

বদলে `__config__` আর্গুমেন্ট ব্যবহার করুন।

## instance মেথডে validator { #validator-instance-method }

এই এরর ওঠে যখন একটি instance মেথডে validator প্রয়োগ করেন (`@field_validator`-এর নিচে `@classmethod` দিতে ভুলে গেলে)।

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: int = 1

        @field_validator('a')
        def check_a(self, value):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-instance-method'
```

## ভুল মোডে `json_schema_input_type` ব্যবহার { #validator-input-type }

এই এরর ওঠে যখন `json_schema_input_type` আর্গুমেন্টে স্পষ্টভাবে একটি মান দেন
আর `mode` `'before'`, `'plain'` বা `'wrap'` কোনোটিই নয়।

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: int = 1

        @field_validator('a', mode='after', json_schema_input_type=int)
        @classmethod
        def check_a(self, value):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-input-type'
```

JSON Schema-র ইনপুট টাইপ ডকুমেন্ট করা শুধু সেই validator-এর জন্য সম্ভব যেখানে দেওয়া
মান যেকোনো কিছু হতে পারে। তাই এটি `after` validator-এ পাওয়া যায় না, যেখানে
মান প্রথমে টাইপ annotation-এর বিপরীতে যাচাই হয়।

## Root validator, `pre`, `skip_on_failure` { #root-validator-pre-skip }

`pre=False` (ডিফল্ট) দিয়ে `@root_validator` ব্যবহার করলে আপনাকে অবশ্যই `skip_on_failure=True` দিতে হবে।
`skip_on_failure=False` অপশন আর পাওয়া যায় না।

`skip_on_failure=False` সেট করার চেষ্টা না করে থাকলে, নিশ্চিন্তে `skip_on_failure=True` দিতে পারেন।
এটি দিলে, কোনো ফিল্ডের যাচাই ব্যর্থ হলে এই root validator আর ডাকা হবে না।

আরও বিস্তারিত জানতে দেখুন [Migration Guide](../migration.md)। (নতুন কোডে `@root_validator`-এর বদলে `@model_validator` ব্যবহার করুন।)

## `model_serializer` instance মেথড { #model-serializer-instance-method }

`@model_serializer` অবশ্যই instance মেথডে প্রয়োগ করতে হবে।

এই এরর ওঠে যখন `self` ছাড়া একটি instance মেথডে `model_serializer` প্রয়োগ করেন:

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        def _serialize(slf, x, y, z):
            return slf

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-instance-method'
```

অথবা একটি class মেথডে:

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        @classmethod
        def _serialize(self, x, y, z):
            return self

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-instance-method'
```

## `validator`, `field`, `config` আর `info` { #validator-field-config-info }

Pydantic V2-তে `field` আর `config` প্যারামিটার পাওয়া যায় না।
বদলে `info` প্যারামিটার ব্যবহার করুন।

কনফিগারেশন `info.config` দিয়ে পাওয়া যায়,
তবে এটি Pydantic V1-এর মতো অবজেক্ট নয়, একটি ডিকশনারি।

`field` আর্গুমেন্ট আর পাওয়া যায় না।

## Pydantic V1 validator signature { #validator-v1-signature }

এই এরর ওঠে যখন Pydantic V1-ধরনের validator-এর জন্য অসমর্থিত signature ব্যবহার করেন।

```python
import warnings

from pydantic import BaseModel, PydanticUserError, validator

warnings.filterwarnings('ignore', category=DeprecationWarning)

try:

    class Model(BaseModel):
        a: int

        @validator('a')
        def check_a(cls, value, foo):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-v1-signature'
```

## অচেনা `field_validator` signature { #validator-signature }

এই এরর ওঠে যখন একটি `field_validator` বা `model_validator` ফাংশনের signature (প্যারামিটারের তালিকা) ভুল।

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator('a')
        @classmethod
        def check_a(cls):
            return 'a'

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-signature'
```

## অচেনা `field_serializer` signature { #field-serializer-signature }

এই এরর ওঠে যখন `field_serializer` ফাংশনের signature ভুল।

```python
from pydantic import BaseModel, PydanticUserError, field_serializer

try:

    class Model(BaseModel):
        x: int

        @field_serializer('x')
        def no_args():
            return 'x'

except PydanticUserError as exc_info:
    assert exc_info.code == 'field-serializer-signature'
```

বৈধ field serializer signature হলো:

```python
from pydantic import FieldSerializationInfo, SerializerFunctionWrapHandler, field_serializer

# an instance method with the default mode or `mode='plain'`
@field_serializer('x')  # or @field_serializer('x', mode='plain')
def ser_x(self, value: Any, info: FieldSerializationInfo): ...

# a static method or function with the default mode or `mode='plain'`
@field_serializer('x')  # or @field_serializer('x', mode='plain')
@staticmethod
def ser_x(value: Any, info: FieldSerializationInfo): ...

# equivalent to
def ser_x(value: Any, info: FieldSerializationInfo): ...
serializer('x')(ser_x)

# an instance method with `mode='wrap'`
@field_serializer('x', mode='wrap')
def ser_x(self, value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...

# a static method or function with `mode='wrap'`
@field_serializer('x', mode='wrap')
@staticmethod
def ser_x(value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...

# equivalent to
def ser_x(value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...
serializer('x')(ser_x)

# For all of these, you can also choose to omit the `info` argument, for example:
@field_serializer('x')
def ser_x(self, value: Any): ...

@field_serializer('x', mode='wrap')
def ser_x(self, value: Any, handler: SerializerFunctionWrapHandler): ...
```

## অচেনা `model_serializer` signature { #model-serializer-signature }

এই এরর ওঠে যখন `model_serializer` ফাংশনের signature ভুল।

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        def _serialize(self, x, y, z):
            return self

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-signature'
```

বৈধ model serializer signature হলো:

```python
from pydantic import SerializerFunctionWrapHandler, SerializationInfo, model_serializer

# an instance method with the default mode or `mode='plain'`
@model_serializer  # or model_serializer(mode='plain')
def mod_ser(self, info: SerializationInfo): ...

# an instance method with `mode='wrap'`
@model_serializer(mode='wrap')
def mod_ser(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo): ...

# For all of these, you can also choose to omit the `info` argument, for example:
@model_serializer(mode='plain')
def mod_ser(self): ...

@model_serializer(mode='wrap')
def mod_ser(self, handler: SerializerFunctionWrapHandler): ...
```

## একাধিক field serializer { #multiple-field-serializers }

এই এরর ওঠে যখন একটি ফিল্ডের জন্য একাধিক serializer ফাংশন সংজ্ঞায়িত হয়।

```python
from pydantic import BaseModel, PydanticUserError, field_serializer

try:

    class MyModel(BaseModel):
        x: int
        y: int

        @field_serializer('x', 'y')
        def serializer1(v):
            return f'{v:,}'

        @field_serializer('x')
        def serializer2(v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'multiple-field-serializers'
```

## অবৈধ annotated টাইপ { #invalid-annotated-type }

এই এরর ওঠে যখন একটি annotation একটি টাইপে প্রয়োগ করা যায় না (যেমন সংখ্যায় স্ট্রিংয়ের শর্ত)।

```python
from typing import Annotated

from pydantic import BaseModel, FutureDate, PydanticUserError

try:

    class Model(BaseModel):
        foo: Annotated[str, FutureDate()]

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-annotated-type'
```

## `TypeAdapter`-এ `config` অব্যবহৃত { #type-adapter-config-unused }

`TypeAdapter`-এ `config` দেওয়ার চেষ্টা করলে এই এরর পাবেন, যখন টাইপটির নিজের এমন config আছে যা
বদলানো যায় না (এখন এটি শুধু `BaseModel`, `TypedDict` আর `dataclass`):

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, PydanticUserError, TypeAdapter


class MyTypedDict(TypedDict):
    x: int


try:
    TypeAdapter(MyTypedDict, config=ConfigDict(strict=True))
except PydanticUserError as exc_info:
    assert exc_info.code == 'type-adapter-config-unused'
```

বদলে আপনাকে টাইপটির subclass বানিয়ে তাতে config বদলাতে বা সেট করতে হবে:

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, TypeAdapter


class MyTypedDict(TypedDict):
    x: int

    # or `model_config = ...` for BaseModel
    __pydantic_config__ = ConfigDict(strict=True)


TypeAdapter(MyTypedDict)  # ok
```

## `RootModel`-এ `model_config['extra']` দেওয়া যায় না { #root-model-extra }

`RootModel` initialization-এর সময় বাড়তি ফিল্ড রাখতে বা এমনকি গ্রহণ করতেও পারে না বলে, `RootModel`-এর একটি subclass
তৈরির সময় `'extra'` কনফিগ সেটিংয়ে মান দেওয়ার চেষ্টা করলে আমরা এরর তুলি:

```python
from pydantic import PydanticUserError, RootModel

try:

    class MyRootModel(RootModel):
        model_config = {'extra': 'allow'}
        root: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'root-model-extra'
```

## টাইপ annotation মূল্যায়ন করা যায় না { #unevaluable-type-annotation }

টাইপ annotation মান বসানোর *পরে* মূল্যায়ন হয় বলে, আপনার কোনো ফিল্ডের সাথে নামের সংঘাত হয় এমন টাইপ annotation-এর নাম
ব্যবহার করলে অপ্রত্যাশিত ফল পেতে পারেন। নিচের ক্ষেত্রে আমরা এরর তুলি:

```python
from datetime import date

from pydantic import BaseModel, Field


class Model(BaseModel):
    date: date = Field(description='A date')
```

বিকল্প হিসেবে, একটি alias ব্যবহার করতে পারেন বা আপনার import বদলাতে পারেন:

```python
import datetime
# Or `from datetime import date as _date`

from pydantic import BaseModel, Field


class Model(BaseModel):
    date: datetime.date = Field(description='A date')
```

## dataclass-এর `init` আর `extra` সেটিং মেলে না { #dataclass-init-false-extra-allow }

কোনো ফিল্ডে `init=False` থাকলে Pydantic একটি dataclass-এ `extra='allow'` সেটিং দেওয়া
অনুমোদন করে না।

তাই নিচের মতো কিছু করতে পারবেন না:

```python
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra='allow'))
class A:
    a: int = Field(init=False, default=1)
```

ওপরের কোড `A` dataclass-এর schema তৈরির সময় নিচের এরর দেয়:

```output
pydantic.errors.PydanticUserError: Field a has `init=False` and dataclass has config setting `extra="allow"`.
This combination is not allowed.
```

## dataclass ফিল্ডে `init` আর `init_var` সেটিং মেলে না { #clashing-init-and-init-var }

`init=False` আর `init_var=True` সেটিং পরস্পর-বর্জনশীল। দুটো একসাথে দিলে নিচের উদাহরণে দেখানো `PydanticUserError` হয়।

```python
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Foo:
    bar: str = Field(init=False, init_var=True)


"""
pydantic.errors.PydanticUserError: Dataclass field bar has init=False and init_var=True, but these are mutually exclusive.
"""
```

## `model_config` একটি মডেল ফিল্ড হিসেবে ব্যবহার { #model-config-invalid-field-name }

এই এরর ওঠে যখন `model_config` একটি ফিল্ডের নাম হিসেবে ব্যবহার হয়।

```python
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        model_config: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-config-invalid-field-name'
```

## একটি `BaseModel` subclass-এ [`with_config`][pydantic.config.with_config] ব্যবহার { #with-config-on-model }

এই এরর ওঠে যখন [`with_config`][pydantic.config.with_config] decorator এমন একটি ক্লাসে ব্যবহার হয় যা ইতিমধ্যে একটি Pydantic মডেল (বদলে `model_config` অ্যাট্রিবিউট ব্যবহার করুন)।

```python
from pydantic import BaseModel, PydanticUserError, with_config

try:

    @with_config({'allow_inf_nan': True})
    class Model(BaseModel):
        bar: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'with-config-on-model'
```

## একটি `BaseModel` subclass-এ `dataclass` ব্যবহার { #dataclass-on-model }

এই এরর ওঠে যখন Pydantic `dataclass` decorator এমন একটি ক্লাসে ব্যবহার হয় যা ইতিমধ্যে
একটি Pydantic মডেল।

```python
from pydantic import BaseModel, PydanticUserError
from pydantic.dataclasses import dataclass

try:

    @dataclass
    class Model(BaseModel):
        bar: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'dataclass-on-model'
```

## `validate_call`-এর জন্য অসমর্থিত টাইপ { #validate-call-type }

`validate_call` কোন callable যাচাই করতে পারে তাতে কিছু সীমাবদ্ধতা আছে। অসমর্থিত একটি callable-এর সাথে এটি ব্যবহারের চেষ্টা করলে এই এরর ওঠে।
এখন সমর্থিত callable হলো ফাংশন (lambda-সহ, তবে built-in নয়), মেথড আর [`partial`][functools.partial]-এর instance।
[`partial`][functools.partial]-এর ক্ষেত্রে, আংশিকভাবে প্রয়োগ করা ফাংশনটিকে অবশ্যই সমর্থিত callable-গুলোর একটি হতে হবে।

### `@classmethod`, `@staticmethod` আর `@property` { #classmethod-staticmethod-and-property }

এই decorator-গুলো অবশ্যই `validate_call`-এর আগে (ওপরে) বসাতে হবে।

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    class A:
        @validate_call
        @classmethod
        def f1(cls): ...

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
@classmethod
@validate_call
def f2(cls): ...
```

### ক্লাস { #classes }

ক্লাস নিজেও callable হলেও, এগুলোতে `validate_call` প্রয়োগ করা যায় না, কারণ টাইপ annotation আনতে কোন মেথড (`__init__` নাকি `__new__`) ব্যবহার হবে তা এর জানা দরকার। একটি ক্লাসের constructor যাচাই করতে চাইলে, বদলে উপযুক্ত মেথডের ওপরে `validate_call` বসান।

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    @validate_call
    class A1: ...

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
class A2:
    @validate_call
    def __init__(self): ...

    @validate_call
    def __new__(cls): ...
```

### callable instance { #callable-instances }

`__call__` মেথড বাস্তবায়ন করে instance-কে callable করা গেলেও, এখন এমন টাইপের instance `validate_call` দিয়ে যাচাই করা যায় না।
ভবিষ্যতে এটি বদলাতে পারে, তবে আপাতত বদলে সরাসরি `__call__`-এর ওপর `validate_call` ব্যবহার করুন।

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    class A1:
        def __call__(self): ...

    validate_call(A1())

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
class A2:
    @validate_call
    def __call__(self): ...
```

### অবৈধ signature { #invalid-signature }

এটি সাধারণত কম দেখা যায়, তবে একটি সম্ভাব্য কারণ হলো আপনি এমন একটি মেথড যাচাইয়ের চেষ্টা করছেন যার অন্তত একটি আর্গুমেন্ট (সাধারণত `self`) নেই।

```python
from pydantic import PydanticUserError, validate_call

try:

    class A:
        def f(): ...

    validate_call(A().f)
except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'
```

## [`TypedDict`][typing.TypedDict] ছাড়া [`Unpack`][typing.Unpack] ব্যবহার { #unpack-typed-dict }

এই এরর ওঠে যখন পরিবর্তনশীল keyword প্যারামিটারের type hint দিতে [`Unpack`][typing.Unpack] একটি
[`TypedDict`][typing.TypedDict] ক্লাস অবজেক্ট ছাড়া অন্য কিছুর সাথে ব্যবহার হয়।

তথ্যসূত্র হিসেবে দেখুন [সংশ্লিষ্ট specification অংশ][related specification section] আর [PEP 692]।

```python
from typing_extensions import Unpack

from pydantic import PydanticUserError, validate_call

try:

    @validate_call
    def func(**kwargs: Unpack[int]):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'unpack-typed-dict'
```

## খুলে দেওয়া [`TypedDict`][typing.TypedDict]-এর ফিল্ড আর আর্গুমেন্টের নাম মিলে যাওয়া { #overlapping-unpack-typed-dict }

এই এরর ওঠে যখন পরিবর্তনশীল keyword প্যারামিটারের type hint-এ ব্যবহৃত typed dictionary-র ফিল্ডের নাম
অন্য প্যারামিটারের সাথে মিলে যায় (যদি না সেগুলো [positional only][positional-only_parameter] হয়)।

তথ্যসূত্র হিসেবে দেখুন [সংশ্লিষ্ট specification অংশ][related specification section] আর [PEP 692]।

```python
from typing_extensions import TypedDict, Unpack

from pydantic import PydanticUserError, validate_call


class TD(TypedDict):
    a: int


try:

    @validate_call
    def func(a: int, **kwargs: Unpack[TD]):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'overlapping-unpack-typed-dict'
```

[related specification section]: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-for-keyword-arguments
[PEP 692]: https://peps.python.org/pep-0692/

## অবৈধ `Self` টাইপ { #invalid-self-type }

এখন [`Self`][typing.Self] শুধু একটি ক্লাসের ফিল্ড annotate করতে ব্যবহার করা যায় (বিশেষ করে [`BaseModel`][pydantic.BaseModel], [`NamedTuple`][typing.NamedTuple], [`TypedDict`][typing.TypedDict] বা dataclass-এর subclass)। অন্য কোনোভাবে [`Self`][typing.Self] ব্যবহারের চেষ্টা করলে এই এরর উঠবে।

```python
from typing_extensions import Self

from pydantic import PydanticUserError, validate_call

try:

    @validate_call
    def func(self: Self):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-self-type'
```

[`validate_call()`][pydantic.validate_call]-এর নিচের উদাহরণটিও এই এরর তুলবে, যদিও type-checking-এর দৃষ্টিতে এটি সঠিক। ভবিষ্যতে এটি সমর্থিত হতে পারে।

```python
from typing_extensions import Self

from pydantic import BaseModel, PydanticUserError, validate_call

try:

    class A(BaseModel):
        @validate_call
        def func(self, arg: Self):
            pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-self-type'
```

## `validate_by_alias` আর `validate_by_name` দুটোই `False` { #validate-by-alias-and-name-false }

এই এরর ওঠে যখন কনফিগারেশনে `validate_by_alias` আর `validate_by_name` দুটোই `False` করেন।

এটি অনুমোদিত নয়, কারণ তাতে অ্যাট্রিবিউট পূরণ করা অসম্ভব হয়ে যেত।

```python
from pydantic import BaseModel, ConfigDict, Field, PydanticUserError

try:

    class Model(BaseModel):
        a: int = Field(alias='A')

        model_config = ConfigDict(
            validate_by_alias=False, validate_by_name=False
        )

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-by-alias-and-name-false'
```
