# Union { #unions }

/// note | এই পেজে যা শিখবেন

* Union (যেমন `int | str`) কী, আর কেন এর যাচাই একটু জটিল।
* তিনটি পদ্ধতি: left to right মোড, smart মোড (ডিফল্ট) আর discriminated union।
* `discriminator` আর `Discriminator` দিয়ে দ্রুত আর স্পষ্ট যাচাই।
* union-এর লম্বা এরর বার্তা ছোট আর বোধগম্য করা।

///

Pydantic যত টাইপ যাচাই করে, union সেগুলো থেকে মৌলিকভাবে আলাদা - সব ফিল্ড/আইটেম/মান বৈধ হওয়ার বদলে, union-এ শুধু একটি সদস্য বৈধ হলেই চলে।

(Union মানে "এটা অথবা ওটা", যেমন `id: int | str` মানে `id` একটি সংখ্যা অথবা একটি স্ট্রিং হতে পারে।)

এতে union যাচাই নিয়ে কিছু সূক্ষ্মতা দেখা দেয়:

* union-এর কোন সদস্য(দের) বিপরীতে ডেটা যাচাই করবেন, আর কোন ক্রমে?
* যাচাই ব্যর্থ হলে কোন এরর দেখাবেন?

union যাচাই করা যেন যাচাইয়ের প্রক্রিয়ায় আরেকটি স্বাধীন মাত্রা যোগ করার মতো।

এই সমস্যাগুলো সমাধানে, Pydantic union যাচাইয়ের তিনটি মৌলিক পদ্ধতি সমর্থন করে:

1. [left to right মোড](#left-to-right-mode) - সবচেয়ে সহজ পদ্ধতি, union-এর প্রতিটি সদস্য ক্রমানুসারে চেষ্টা করা হয় আর প্রথম মিলটি ফেরত দেওয়া হয়
2. [smart মোড](#smart-mode) - "left to right মোড"-এর মতোই সদস্যগুলো ক্রমানুসারে চেষ্টা করা হয়; তবে প্রথম মিল পাওয়ার পরও আরও ভালো মিল খুঁজতে যাচাই চলতে থাকে, বেশিরভাগ union যাচাইয়ের জন্য এটিই ডিফল্ট মোড
3. [discriminated union](#discriminated-unions) - একটি discriminator-এর ভিত্তিতে union-এর শুধু একটি সদস্য চেষ্টা করা হয়

/// tip | পরামর্শ

সাধারণভাবে, আমরা [discriminated union](#discriminated-unions) ব্যবহারের পরামর্শ দিই। এগুলো untagged (লেবেলহীন) union-এর চেয়ে দ্রুত আর বেশি অনুমানযোগ্য, কারণ union-এর কোন সদস্যের বিপরীতে যাচাই হবে তা আপনি নিয়ন্ত্রণ করতে পারেন।

জটিল ক্ষেত্রে, যদি untagged union ব্যবহার করেন আর union-এর সদস্যদের বিপরীতে যাচাইয়ের চেষ্টার ক্রম নিয়ে নিশ্চয়তা দরকার হয়, তাহলে `union_mode='left_to_right'` ব্যবহারের পরামর্শ দেওয়া হয়।

যদি খুবই বিশেষ ধরনের আচরণ চান, তাহলে একটি [কাস্টম validator](../concepts/validators.md#field-validators) ব্যবহার করতে পারেন।

///

## Union মোড { #union-modes }

### Left to Right মোড { #left-to-right-mode }

/// note | নোট

যেহেতু এই মোড প্রায়ই অপ্রত্যাশিত যাচাইয়ের ফলাফল দেয়, তাই Pydantic >=2-এ এটি ডিফল্ট নয়, বরং `union_mode='smart'` ডিফল্ট।

///

এই পদ্ধতিতে, union-এর প্রতিটি সদস্য যে ক্রমে সংজ্ঞায়িত সেই ক্রমে তার বিপরীতে যাচাইয়ের চেষ্টা করা হয়, আর প্রথম সফল যাচাইটি ইনপুট হিসেবে গৃহীত হয়।

সব সদস্যে যাচাই ব্যর্থ হলে, যাচাইয়ের এররে union-এর সব সদস্যের এরর থাকে।

যে union ফিল্ডে এটি ব্যবহার করতে চান, সেখানে `union_mode='left_to_right'` একটি [`Field`](../concepts/fields.md) প্যারামিটার হিসেবে সেট করতে হবে।

```python title="Union with left to right mode"
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    id: str | int = Field(union_mode='left_to_right')


print(User(id=123))
#> id=123
print(User(id='hello'))
#> id='hello'

try:
    User(id=[])
except ValidationError as e:
    print(e)
    """
    2 validation errors for User
    id.str
      Input should be a valid string [type=string_type, input_value=[], input_type=list]
    id.int
      Input should be a valid integer [type=int_type, input_value=[], input_type=list]
    """
```

এই ক্ষেত্রে সদস্যদের ক্রম খুবই গুরুত্বপূর্ণ, যা ওপরের উদাহরণটি একটু বদলে দেখানো হলো:

```python title="Union with left to right - unexpected results"
from pydantic import BaseModel, Field


class User(BaseModel):
    id: int | str = Field(union_mode='left_to_right')


print(User(id=123))  # (1)
#> id=123
print(User(id='456'))  # (2)
#> id=456
```

1. প্রত্যাশামতোই ইনপুটটি `int` সদস্যের বিপরীতে যাচাই হয় আর ফলাফল প্রত্যাশিত।
2. আমরা lax মোডে আছি, আর সংখ্যাসূচক স্ট্রিং `'123'` union-এর প্রথম সদস্য `int`-এর জন্য বৈধ ইনপুট।
   যেহেতু সেটি প্রথমে চেষ্টা করা হয়, তাই আমরা অবাক করা ফলাফল পাই: `id` একটি `str`-এর বদলে একটি `int`।

/// tip | উদাহরণ দিয়ে বুঝি

left to right মোড হলো সারিতে দাঁড়ানো কর্মীদের মধ্যে প্রথম যে কাজটা "মোটামুটি পারে" তাকেই দিয়ে দেওয়া। `'456'` স্ট্রিংটি `int` কর্মী রূপান্তর করে নিতে পারে, তাই সে-ই কাজটা পেয়ে যায়, যদিও `str` কর্মী হুবহু মেলে। smart মোড আগে সবাইকে জিজ্ঞেস করে দেখে কে সবচেয়ে ভালো মেলে।

///

### Smart মোড { #smart-mode }

`union_mode='left_to_right'`-এর সম্ভাব্য অবাক করা ফলাফলের কারণে, Pydantic >=2-এ union যাচাইয়ের ডিফল্ট মোড হলো `union_mode='smart'`।

এই মোডে, pydantic union-এর সদস্যদের মধ্যে ইনপুটের জন্য সবচেয়ে ভালো মিলটি বেছে নেওয়ার চেষ্টা করে। পারফরম্যান্স আর নির্ভুলতা দুটোতেই উন্নতির জন্য সঠিক অ্যালগরিদম Pydantic-এর minor রিলিজের মধ্যে বদলাতে পারে।

/// note | নোট

ভবিষ্যৎ Pydantic সংস্করণে অভ্যন্তরীণ `smart` মিলানোর অ্যালগরিদম বদলানোর অধিকার আমরা রাখি। যদি খুবই নির্দিষ্ট
মিলানোর আচরণের ওপর নির্ভর করেন, তাহলে `union_mode='left_to_right'` বা [discriminated union](#discriminated-unions) ব্যবহারের পরামর্শ দেওয়া হয়।

///

//// details | Smart মোডের অ্যালগরিদম
    type: info

ইনপুটের জন্য সবচেয়ে ভালো মিল নির্ধারণে smart মোডের অ্যালগরিদম দুটি মাপকাঠি ব্যবহার করে:

1. সেট হওয়া বৈধ ফিল্ডের সংখ্যা (মডেল, dataclass আর typed dict-এর জন্য প্রাসঙ্গিক)
2. মিলের হুবহুতা (exactness) (সব টাইপের জন্য প্রাসঙ্গিক)

#### সেট হওয়া বৈধ ফিল্ডের সংখ্যা { #number-of-valid-fields-set }

/// note | নোট

এই মাপকাঠি Pydantic v2.8.0-এ আনা হয়েছে। এই সংস্করণের আগে, সবচেয়ে ভালো মিল নির্ধারণে শুধু হুবহুতা ব্যবহার হতো।

///

এই মাপকাঠি বর্তমানে শুধু মডেল, dataclass আর typed dict-এর জন্য প্রাসঙ্গিক।

যত বেশি বৈধ ফিল্ড সেট হয়, মিল তত ভালো। নেস্টেড মডেলে সেট হওয়া ফিল্ডের সংখ্যাও হিসাবে নেওয়া হয়।
এই সংখ্যাগুলো শীর্ষ-স্তরের union পর্যন্ত উঠে আসে, যেখানে সবচেয়ে বেশি সংখ্যাওয়ালা union সদস্যকে সবচেয়ে ভালো মিল হিসেবে ধরা হয়।

যেসব ডেটা টাইপের জন্য এই মাপকাঠি প্রাসঙ্গিক, সেখানে আমরা হুবহুতার চেয়ে এই সংখ্যাকে অগ্রাধিকার দিই। অন্য সব টাইপের জন্য, শুধু হুবহুতা ব্যবহার করি।

#### হুবহুতা (Exactness) { #exactness }

`exactness`-এর জন্য, Pydantic একটি union সদস্যের মিলকে নিচের তিনটি দলের একটিতে নম্বর দেয় (সবচেয়ে বেশি নম্বর থেকে সবচেয়ে কম):

* হুবহু টাইপের মিল, যেমন একটি `float | int` union যাচাইয়ে একটি `int` ইনপুট `int` সদস্যের সাথে হুবহু টাইপের মিল
* [`strict` মোডে](../concepts/strict_mode.md) যাচাই সফল হতো
* lax মোডে যাচাই সফল হতো

যে union মিল সবচেয়ে বেশি হুবহুতার নম্বর পেয়েছে, সেটিকে সবচেয়ে ভালো মিল হিসেবে ধরা হবে।

smart মোডে, ইনপুটের জন্য সবচেয়ে ভালো মিল বেছে নিতে নিচের ধাপগুলো নেওয়া হয়:

/// tab | `BaseModel`, `dataclass`, আর `TypedDict`

1. union-এর সদস্যদের বাঁ থেকে ডানে চেষ্টা করা হয়, যেকোনো সফল মিলকে ওপরে বর্ণিত তিনটি হুবহুতার শ্রেণির একটিতে নম্বর দেওয়া হয়,
সাথে সেট হওয়া বৈধ ফিল্ডের সংখ্যাও গোনা হয়।
2. সব সদস্য মূল্যায়নের পরে, সবচেয়ে বেশি "সেট হওয়া বৈধ ফিল্ড" সংখ্যাওয়ালা সদস্য ফেরত দেওয়া হয়।
3. যদি সবচেয়ে বেশি "সেট হওয়া বৈধ ফিল্ড" সংখ্যায় সমতা হয়, তাহলে সমতা ভাঙতে হুবহুতার নম্বর ব্যবহার হয়, আর সবচেয়ে বেশি হুবহুতার নম্বরওয়ালা সদস্য ফেরত দেওয়া হয়।
4. সব সদস্যে যাচাই ব্যর্থ হলে, সব এরর ফেরত দেওয়া হয়।

///

/// tab | অন্য সব ডেটা টাইপ

1. union-এর সদস্যদের বাঁ থেকে ডানে চেষ্টা করা হয়, যেকোনো সফল মিলকে ওপরে বর্ণিত তিনটি হুবহুতার শ্রেণির একটিতে নম্বর দেওয়া হয়।
    * যদি হুবহু টাইপের মিলে যাচাই সফল হয়, তাহলে সেই সদস্য সঙ্গে সঙ্গে ফেরত দেওয়া হয় আর পরের সদস্যগুলো আর চেষ্টা করা হয় না।
2. যদি অন্তত একটি সদস্যে "strict" মিল হিসেবে যাচাই সফল হয়, তাহলে সেই "strict" মিলগুলোর মধ্যে সবচেয়ে বাঁয়েরটি ফেরত দেওয়া হয়।
3. যদি অন্তত একটি সদস্যে "lax" মোডে যাচাই সফল হয়, তাহলে সবচেয়ে বাঁয়ের মিলটি ফেরত দেওয়া হয়।
4. সব সদস্যে যাচাই ব্যর্থ হলে, সব এরর ফেরত দেওয়া হয়।

///

////

```python
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: int | str | UUID
    name: str


user_01 = User(id=123, name='John Doe')
print(user_01)
#> id=123 name='John Doe'
print(user_01.id)
#> 123
user_02 = User(id='1234', name='John Doe')
print(user_02)
#> id='1234' name='John Doe'
print(user_02.id)
#> 1234
user_03_uuid = UUID('cf57432e-809e-4353-adbd-9d5c0d733868')
user_03 = User(id=user_03_uuid, name='John Doe')
print(user_03)
#> id=UUID('cf57432e-809e-4353-adbd-9d5c0d733868') name='John Doe'
print(user_03.id)
#> cf57432e-809e-4353-adbd-9d5c0d733868
print(user_03_uuid.int)
#> 275603287559914445491632874575877060712
```

(smart মোডে `123` হুবহু `int`, তাই `int` থাকে; `'1234'` হুবহু `str`, তাই স্ট্রিং থাকে, সংখ্যায় রূপান্তর হয় না; আর `UUID` অবজেক্ট হুবহু `UUID`, তাই সেটিই থাকে। প্রতিটি ইনপুট তার নিজের টাইপেই রয়ে গেছে।)

## Discriminated union { #discriminated-unions }

**Discriminated union-কে কখনো কখনো "Tagged union" (লেবেলযুক্ত union) বলা হয়।**

একটি discriminator ব্যবহার করে, union-এর কোন সদস্যের বিপরীতে যাচাই হবে তা নির্দিষ্টভাবে বেছে নিয়ে union আরও দক্ষভাবে যাচাই করা যায়।
এতে যাচাই আরও দক্ষ হয়, আর যাচাই ব্যর্থ হলে এররের বন্যাও এড়ানো যায়।

union-এ discriminator যোগ করার মানে আরও হলো, তৈরি হওয়া JSON schema
[OpenAPI স্পেসিফিকেশনের](https://swagger.io/specification/#discriminator-object) `discriminator` অ্যাট্রিবিউট বাস্তবায়ন করে।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#discriminated-unions-with-str-discriminators}{% endraw %}

### স্ট্রিং discriminator-সহ discriminated union { #discriminated-unions-with-string-discriminators }

প্রায়ই, একাধিক মডেলসহ একটি union-এর ক্ষেত্রে, union-এর সব সদস্যের একটি সাধারণ ফিল্ড থাকে,
যা দিয়ে আলাদা করা যায় ডেটা কোন union ক্ষেত্রের বিপরীতে যাচাই হবে।

সেই তথ্যের ভিত্তিতে মডেল যাচাই করতে, union-এর প্রতিটি মডেলে একটি সাধারণ ফিল্ড সেট করতে পারেন (নিচের উদাহরণে `pet_type`),
যার টাইপ এক বা একাধিক literal মান গ্রহণ করে। discriminated union টাইপ সংজ্ঞায়িত করার সময়,
[`Field()` ফাংশনের](./fields.md) `discriminator` প্যারামিটার নির্দিষ্ট করতে হবে ([`Discriminator`][pydantic.Discriminator] টাইপও ব্যবহার করা যায়)।

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError


class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int


class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float


class Lizard(BaseModel):
    pet_type: Literal['reptile', 'lizard']
    scales: bool


class Model(BaseModel):
    pet: Cat | Dog | Lizard = Field(discriminator='pet_type')
    n: int


print(Model(pet={'pet_type': 'dog', 'barks': 3.14}, n=1))
#> pet=Dog(pet_type='dog', barks=3.14) n=1
try:
    Model(pet={'pet_type': 'dog'}, n=1)
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.dog.barks
      Field required [type=missing, input_value={'pet_type': 'dog'}, input_type=dict]
    """
```

/// info | কোডটি সহজ ভাষায়

`pet_type`-এর মান দেখে Pydantic সরাসরি সঠিক মডেল বেছে নেয়: `'dog'` → `Dog`। দ্বিতীয় উদাহরণে `barks` নেই, তাই এরর এসেছে শুধু `Dog`-এর জন্য (`pet.dog.barks`), `Cat` বা `Lizard`-এর কোনো অপ্রাসঙ্গিক এরর নেই। একটি মডেল একাধিক লেবেলও নিতে পারে, যেমন `Lizard`-এর `'reptile'` বা `'lizard'`।

///

/// info | v2.13-এ যোগ হয়েছে
একটি [`Literal`][typing.Literal] root টাইপসহ [root মডেল](./models.md#rootmodel-and-custom-root-types) [`Literal`][typing.Literal] টাইপের জায়গায় ব্যবহার করা যায়।
///

### callable `Discriminator`-সহ discriminated union { #discriminated-unions-with-callable-discriminator }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.types.Discriminator`][pydantic.types.Discriminator]<br>

///

একাধিক মডেলসহ একটি union-এর ক্ষেত্রে, কখনো কখনো সব মডেলে এমন একটি অভিন্ন ফিল্ড থাকে না
যা discriminator হিসেবে ব্যবহার করা যায়।
এটি একটি callable (ফাংশন) `Discriminator`-এর জন্য আদর্শ ক্ষেত্র।

/// tip | পরামর্শ

callable discriminator ডিজাইন করার সময় মনে রাখবেন, আপনাকে হয়তো `dict` আর মডেল টাইপ দুই ধরনের ইনপুটই
বিবেচনা করতে হবে। এই প্যাটার্ন `mode='before'` validator-এর মতো,
যেখানে বিভিন্ন রূপের ইনপুট আশা করতে হয়।

কিন্তু দাঁড়ান! আপনি জিজ্ঞেস করবেন, আমি তো শুধু `dict` টাইপ দেওয়ার আশা করি, মডেলের কথা কেন ভাবতে হবে?
Pydantic সিরিয়ালাইজেশনের জন্যও callable discriminator ব্যবহার করে, আর তখন আপনার callable-এর ইনপুট
খুব সম্ভবত একটি মডেল ইনস্ট্যান্স হবে।

নিচের উদাহরণগুলোতে দেখবেন, callable discriminator-গুলো `dict` আর মডেল দুই ইনপুটই সামলানোর জন্য ডিজাইন করা।
এই অভ্যাস না মানলে, সবচেয়ে ভালো ক্ষেত্রে সিরিয়ালাইজেশনের সময় সতর্কবার্তা পাবেন,
আর সবচেয়ে খারাপ ক্ষেত্রে যাচাইয়ের সময় চলমান অবস্থায় এরর পাবেন।

///

```python
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Discriminator, Tag


class Pie(BaseModel):
    time_to_cook: int
    num_ingredients: int


class ApplePie(Pie):
    fruit: Literal['apple'] = 'apple'


class PumpkinPie(Pie):
    filling: Literal['pumpkin'] = 'pumpkin'


def get_discriminator_value(v: Any) -> str | None:
    if isinstance(v, dict):
        return v.get('fruit', v.get('filling'))
    return getattr(v, 'fruit', getattr(v, 'filling', None))


class ThanksgivingDinner(BaseModel):
    dessert: Annotated[
        Annotated[ApplePie, Tag('apple')] | Annotated[PumpkinPie, Tag('pumpkin')],
        Discriminator(get_discriminator_value),
    ]


apple_variation = ThanksgivingDinner.model_validate(
    {'dessert': {'fruit': 'apple', 'time_to_cook': 60, 'num_ingredients': 8}}
)
print(repr(apple_variation))
"""
ThanksgivingDinner(dessert=ApplePie(time_to_cook=60, num_ingredients=8, fruit='apple'))
"""

pumpkin_variation = ThanksgivingDinner.model_validate(
    {
        'dessert': {
            'filling': 'pumpkin',
            'time_to_cook': 40,
            'num_ingredients': 6,
        }
    }
)
print(repr(pumpkin_variation))
"""
ThanksgivingDinner(dessert=PumpkinPie(time_to_cook=40, num_ingredients=6, filling='pumpkin'))
"""
```

(আপেল পাইয়ের লেবেল ঘর `fruit`, মিষ্টিকুমড়ার পাইয়ের `filling`; তাই `get_discriminator_value` দুটোর যেকোনোটি পড়ে `'apple'` বা `'pumpkin'` ফেরত দেয়, আর `Tag` বলে দেয় কোন লেবেলে কোন মডেল।)

মডেল আর মৌলিক (primitive) টাইপের সমন্বয়সহ union টাইপ যাচাইয়েও `Discriminator` ব্যবহার করা যায়।

যেমন:

```python
from typing import Annotated, Any

from pydantic import BaseModel, Discriminator, Tag, ValidationError


def model_x_discriminator(v: Any) -> str | None:
    if isinstance(v, int):
        return 'int'
    if isinstance(v, (dict, BaseModel)):
        return 'model'
    else:
        # return None if the discriminator value isn't found
        return None


class SpecialValue(BaseModel):
    value: int


class DiscriminatedModel(BaseModel):
    value: Annotated[
        Annotated[int, Tag('int')] | Annotated['SpecialValue', Tag('model')],
        Discriminator(model_x_discriminator),
    ]


model_data = {'value': {'value': 1}}
m = DiscriminatedModel.model_validate(model_data)
print(m)
#> value=SpecialValue(value=1)

int_data = {'value': 123}
m = DiscriminatedModel.model_validate(int_data)
print(m)
#> value=123

try:
    DiscriminatedModel.model_validate({'value': 'not an int or a model'})
except ValidationError as e:
    print(e)  # (1)!
    """
    1 validation error for DiscriminatedModel
    value
      Unable to extract tag using discriminator model_x_discriminator() [type=union_tag_not_found, input_value='not an int or a model', input_type=str]
    """
```

1. লক্ষ্য করুন, discriminator মান না পাওয়া গেলে callable discriminator ফাংশন `None` ফেরত দেয়।
   যখন `None` ফেরত আসে, তখন এই `union_tag_not_found` এরর হয়।

/// note | নোট

union আর `discriminator`-এর তথ্য একসাথে রাখতে [Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) ব্যবহার
সুবিধাজনক হতে পারে। আরও বিস্তারিত জানতে পরের উদাহরণ দেখুন।

একটি ফিল্ডে discriminator সেট করার কয়েকটি উপায় আছে, যেগুলোর সিনট্যাক্সে সামান্য পার্থক্য।

`str` discriminator-এর জন্য:

```python
some_field: ... | ... = Field(discriminator='my_discriminator')
some_field: Annotated[... | ..., Field(discriminator='my_discriminator')]
```

callable `Discriminator`-এর জন্য:

```python
some_field: ... | ... = Field(discriminator=Discriminator(...))
some_field: Annotated[... | ..., Discriminator(...)]
some_field: Annotated[... | ..., Field(discriminator=Discriminator(...))]
```

///

### নেস্টেড discriminated union { #nested-discriminated-unions }

একটি ফিল্ডে শুধু একটি discriminator সেট করা যায়, কিন্তু কখনো একাধিক discriminator মেলাতে চান।
নেস্টেড `Annotated` টাইপ তৈরি করে এটি করতে পারেন, যেমন:

```python
from typing import Annotated, Literal

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['black']
    black_name: str


class WhiteCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['white']
    white_name: str


Cat = Annotated[BlackCat | WhiteCat, Field(discriminator='color')]


class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str


Pet = Annotated[Cat | Dog, Field(discriminator='pet_type')]


class Model(BaseModel):
    pet: Pet
    n: int


m = Model(pet={'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}, n=1)
print(m)
#> pet=BlackCat(pet_type='cat', color='black', black_name='felix') n=1
try:
    Model(pet={'pet_type': 'cat', 'color': 'red'}, n='1')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.cat
      Input tag 'red' found using 'color' does not match any of the expected tags: 'black', 'white' [type=union_tag_invalid, input_value={'pet_type': 'cat', 'color': 'red'}, input_type=dict]
    """
try:
    Model(pet={'pet_type': 'cat', 'color': 'black'}, n='1')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.cat.black.black_name
      Field required [type=missing, input_value={'pet_type': 'cat', 'color': 'black'}, input_type=dict]
    """
```

(প্রথমে `pet_type` দেখে বিড়াল নাকি কুকুর ঠিক হয়; বিড়াল হলে তারপর `color` দেখে কালো নাকি সাদা বিড়াল। দুই ধাপের লেবেল।)

/// tip | পরামর্শ

যদি একটি union-এর বিপরীতে, আর শুধু একটি union-এর বিপরীতে, ডেটা যাচাই করতে চান, তাহলে স্ট্যান্ডার্ড `BaseModel` থেকে উত্তরাধিকার নেওয়ার বদলে pydantic-এর [`TypeAdapter`](../concepts/type_adapter.md) গঠন ব্যবহার করতে পারেন।

আগের উদাহরণের প্রসঙ্গে, আমাদের আছে:

```python
type_adapter = TypeAdapter(Pet)

pet = type_adapter.validate_python(
    {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}
)
print(repr(pet))
#> BlackCat(pet_type='cat', color='black', black_name='felix')
```

///

## Union যাচাইয়ের এরর { #union-validation-errors }

union যাচাই ব্যর্থ হলে, এরর বার্তা বেশ লম্বা হতে পারে, কারণ union-এর প্রতিটি ক্ষেত্রের জন্য
যাচাইয়ের এরর তৈরি হবে।
পুনরাবৃত্ত মডেলের ক্ষেত্রে এটি বিশেষভাবে লক্ষণীয়, যেখানে পুনরাবৃত্তির প্রতিটি স্তরে কারণ তৈরি হতে পারে।
এই ক্ষেত্রে discriminated union এরর বার্তা সহজ করতে সাহায্য করে, কারণ যাচাইয়ের এরর শুধু
মিলে যাওয়া discriminator মানের ক্ষেত্রটির জন্যই তৈরি হয়।

একটি union ব্যর্থতা বোঝা মানে কোন সদস্যের *মেলার কথা ছিল* তা বের করা। একটি
[`ValidationError`][pydantic_core.ValidationError]-এ প্রতিটি সদস্যের এরর আর প্রত্যাখ্যাত মান থাকে;
যখন ব্যর্থতা একটি ডিপ্লয় করা সার্ভিসে ঘটে, তখন [Logfire সেই বিবরণগুলো চারপাশের
trace-সহ রেখে দেয়](../errors/troubleshooting.md), যাতে পরে সেই তুলনা করতে পারেন।

নিচের উদাহরণের মতো, `Discriminator` constructor-এ প্যারামিটার হিসেবে দিয়ে একটি `Discriminator`-এর এররের টাইপ, বার্তা আর প্রসঙ্গও
নিজের মতো করতে পারেন।

```python
from typing import Annotated

from pydantic import BaseModel, Discriminator, Tag, ValidationError


# Errors are quite verbose with a normal union:
class Model(BaseModel):
    x: 'str | Model'


try:
    Model.model_validate({'x': {'x': {'x': 1}}})
except ValidationError as e:
    print(e)
    """
    4 validation errors for Model
    x.str
      Input should be a valid string [type=string_type, input_value={'x': {'x': 1}}, input_type=dict]
    x.Model.x.str
      Input should be a valid string [type=string_type, input_value={'x': 1}, input_type=dict]
    x.Model.x.Model.x.str
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
    x.Model.x.Model.x.Model
      Input should be a valid dictionary or instance of Model [type=model_type, input_value=1, input_type=int]
    """

try:
    Model.model_validate({'x': {'x': {'x': {}}}})
except ValidationError as e:
    print(e)
    """
    4 validation errors for Model
    x.str
      Input should be a valid string [type=string_type, input_value={'x': {'x': {}}}, input_type=dict]
    x.Model.x.str
      Input should be a valid string [type=string_type, input_value={'x': {}}, input_type=dict]
    x.Model.x.Model.x.str
      Input should be a valid string [type=string_type, input_value={}, input_type=dict]
    x.Model.x.Model.x.Model.x
      Field required [type=missing, input_value={}, input_type=dict]
    """


# Errors are much simpler with a discriminated union:
def model_x_discriminator(v):
    if isinstance(v, str):
        return 'str'
    if isinstance(v, (dict, BaseModel)):
        return 'model'


class DiscriminatedModel(BaseModel):
    x: Annotated[
        Annotated[str, Tag('str')] | Annotated['DiscriminatedModel', Tag('model')],
        Discriminator(
            model_x_discriminator,
            custom_error_type='invalid_union_member',  # (1)!
            custom_error_message='Invalid union member',  # (2)!
            custom_error_context={'discriminator': 'str_or_model'},  # (3)!
        ),
    ]


try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': 1}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x
      Invalid union member [type=invalid_union_member, input_value=1, input_type=int]
    """

try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': {}}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x.model.x
      Field required [type=missing, input_value={}, input_type=dict]
    """

# The data is still handled properly when valid:
data = {'x': {'x': {'x': 'a'}}}
m = DiscriminatedModel.model_validate(data)
print(m.model_dump())
#> {'x': {'x': {'x': 'a'}}}
```

1. `custom_error_type` হলো যাচাই ব্যর্থ হলে হওয়া `ValidationError`-এর `type` অ্যাট্রিবিউট।
2. `custom_error_message` হলো যাচাই ব্যর্থ হলে হওয়া `ValidationError`-এর `msg` অ্যাট্রিবিউট।
3. `custom_error_context` হলো যাচাই ব্যর্থ হলে হওয়া `ValidationError`-এর `ctx` অ্যাট্রিবিউট।

প্রতিটি ক্ষেত্রকে একটি [`Tag`][pydantic.types.Tag] দিয়ে লেবেল করেও এরর বার্তা সহজ করতে পারেন।
এটি বিশেষভাবে কাজের যখন এই উদাহরণের মতো জটিল টাইপ থাকে:

```python
from typing import Annotated

from pydantic import AfterValidator, Tag, TypeAdapter, ValidationError

DoubledList = Annotated[list[int], AfterValidator(lambda x: x * 2)]
StringsMap = dict[str, str]


# Not using any `Tag`s for each union case, the errors are not so nice to look at
adapter = TypeAdapter(DoubledList | StringsMap)

try:
    adapter.validate_python(['a'])
except ValidationError as exc_info:
    print(exc_info)
    """
    2 validation errors for union[function-after[<lambda>(), list[int]],dict[str,str]]
    function-after[<lambda>(), list[int]].0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    dict[str,str]
      Input should be a valid dictionary [type=dict_type, input_value=['a'], input_type=list]
    """

tag_adapter = TypeAdapter(
    Annotated[DoubledList, Tag('DoubledList')] | Annotated[StringsMap, Tag('StringsMap')]
)

try:
    tag_adapter.validate_python(['a'])
except ValidationError as exc_info:
    print(exc_info)
    """
    2 validation errors for union[DoubledList,StringsMap]
    DoubledList.0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    StringsMap
      Input should be a valid dictionary [type=dict_type, input_value=['a'], input_type=list]
    """
```

/// check | সংক্ষেপে মনে রাখুন

* ডিফল্ট smart মোড প্রতিটি ইনপুটের জন্য সবচেয়ে "হুবহু" মেলা সদস্য বেছে নেয়।
* ক্রমের নিশ্চয়তা চাইলে `Field(union_mode='left_to_right')`।
* সবচেয়ে ভালো: discriminated union, `Field(discriminator='pet_type')` বা `Discriminator(func)` + `Tag`; দ্রুত, অনুমানযোগ্য আর পরিষ্কার এরর।

///
