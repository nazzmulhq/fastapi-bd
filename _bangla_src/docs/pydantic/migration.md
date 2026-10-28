# মাইগ্রেশন গাইড { #migration-guide }

/// note | এই পেজে যা জানবেন

* পুরনো Pydantic V1 থেকে নতুন Pydantic V2-তে কোড সরানোর (মাইগ্রেশন) ধাপগুলো।
* `bump-pydantic` টুল দিয়ে স্বয়ংক্রিয়ভাবে বেশিরভাগ কোড বদলানো।
* মেথডের নতুন নাম (`dict()` → `model_dump()` ইত্যাদি), config আর validator-এর পরিবর্তন।
* `Optional` ফিল্ড, union, float→int রূপান্তর, URL ইত্যাদির আচরণে কী বদলেছে।
* কোন জিনিস কোথায় সরে গেছে বা বাদ পড়েছে।

নতুন করে Pydantic শিখছেন আর পুরনো কোড নেই? তাহলে এই পেজ এড়িয়ে [মডেল](concepts/models.md) পেজে চলে যেতে পারেন।

///

Pydantic V2-তে API-তে বেশ কিছু পরিবর্তন এসেছে, যার কিছু breaking change (এমন পরিবর্তন যা পুরনো কোড ভেঙে দিতে পারে)।

এই পেজটি আপনার কোড Pydantic V1 থেকে Pydantic V2-তে সরাতে সাহায্য করার জন্য সবচেয়ে
গুরুত্বপূর্ণ পরিবর্তনগুলো তুলে ধরে একটি গাইড দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

মাইগ্রেশন অনেকটা নতুন বাসায় ওঠার মতো। আসবাব (আপনার কোডের যুক্তি) একই থাকে, কিন্তু কিছু জিনিসের জায়গা বদলেছে (`pydantic.BaseSettings` এখন আলাদা প্যাকেজে), কিছুর নাম বদলেছে (`dict()` এখন `model_dump()`), আর কিছু পুরনো জিনিস ফেলে দেওয়া হয়েছে। এই পেজ হলো সেই নতুন বাসার মানচিত্র।

///

## Pydantic V2 ইনস্টল করুন { #install-pydantic-v2 }

Pydantic V2 এখন Pydantic-এর বর্তমান প্রোডাকশন রিলিজ।
PyPI থেকে Pydantic V2 ইনস্টল করতে পারেন:

```bash
pip install -U pydantic
```

কোনো সমস্যায় পড়লে, অনুগ্রহ করে `bug V2` লেবেল দিয়ে [GitHub-এ একটি issue তৈরি করুন](https://github.com/pydantic/pydantic/issues)।
এতে আমরা সক্রিয়ভাবে এরর পর্যবেক্ষণ আর ট্র্যাক করতে পারব, আর লাইব্রেরির পারফরম্যান্স উন্নত করে যেতে পারব।

যদি কোনো কারণে সর্বশেষ Pydantic V1 ব্যবহার করতে হয়, তাহলে ইনস্টলেশন আর `pydantic.v1` থেকে ইমপোর্টের বিস্তারিত জানতে নিচের [Pydantic V1-এর ফিচার ব্যবহার চালিয়ে যাওয়া](#continue-using-pydantic-v1-features) অংশ দেখুন।

## কোড রূপান্তরের টুল { #code-transformation-tool }

আপনার কোড মাইগ্রেট করতে সাহায্যের জন্য আমরা একটি টুল তৈরি করেছি। টুলটি এখনো বেটা পর্যায়ে, তবে আশা করি এটি আপনাকে
আরও দ্রুত কোড মাইগ্রেট করতে সাহায্য করবে।

PyPI থেকে টুলটি ইনস্টল করতে পারেন:

```bash
pip install bump-pydantic
```

ব্যবহার খুবই সহজ। যদি আপনার প্রজেক্টের কাঠামো এমন হয়:

    * repo_folder
        * my_package
            * <python source files> ...

তাহলে আপনাকে এটি করতে হবে:

    cd /path/to/repo_folder
    bump-pydantic my_package

এ সম্পর্কে আরও দেখুন [Bump Pydantic](https://github.com/pydantic/bump-pydantic) রিপোজিটরিতে।

/// warning | সাধারণ ভুল

`bump-pydantic` চালানোর আগে কোড git-এ commit করে রাখুন, যাতে কী কী বদলাল তা দেখতে আর দরকার হলে ফিরিয়ে আনতে পারেন। টুলটি সব কিছু বদলাতে পারে না, তাই শেষে টেস্ট চালিয়ে আর এই পেজ মিলিয়ে বাকিটা নিজে ঠিক করুন।

///

## Pydantic V1-এর ফিচার ব্যবহার চালিয়ে যাওয়া { #continue-using-pydantic-v1-features }

দরকার হলে Pydantic V1 এখনো পাওয়া যায়, যদিও এর উন্নতি আর নতুন ফিচারের জন্য আমরা
Pydantic V2-তে মাইগ্রেট করার পরামর্শ দিই।

যদি সর্বশেষ Pydantic V1 ব্যবহার করতে হয়, এভাবে ইনস্টল করতে পারেন:

```bash
pip install "pydantic==1.*"
```

Pydantic V2 প্যাকেজ `pydantic.v1`-এর মাধ্যমে ইমপোর্ট করে Pydantic V1 API ব্যবহারের সুযোগও দিয়ে যাচ্ছে।

যেমন, Pydantic V2-এর `pydantic.BaseModel` ক্লাসের বদলে Pydantic V1-এর
`BaseModel` ক্লাস ব্যবহার করতে পারেন:

```python
from pydantic.v1 import BaseModel
```

Pydantic V2 থেকে সরিয়ে দেওয়া ফাংশনও ইমপোর্ট করতে পারেন, যেমন `lenient_isinstance`:

```python
from pydantic.v1.utils import lenient_isinstance
```

দেখুন [Pydantic V1 ডকুমেন্টেশন](https://pydantic.dev/docs/validation/1.10/overview/)।

### v1/v2 পরিবেশে Pydantic v1-এর ফিচার ব্যবহার { #using-pydantic-v1-features-in-a-v1v2-environment }

`pydantic>=1.10.17` থেকে, `pydantic.v1` নেমস্পেস V1-এর ভেতরেও ব্যবহার করা যায়।
এতে V2-তে মাইগ্রেট করা সহজ হয়, কারণ V2-ও `pydantic.v1`
নেমস্পেস সমর্থন করে। একটি `pydantic<2` ডিপেন্ডেন্সি খুলে দিয়ে (unpin করে) V1-এর
ফিচার ব্যবহার চালিয়ে যেতে, নিচের ধাপগুলো অনুসরণ করুন:

1. `pydantic<2`-এর জায়গায় `pydantic>=1.10.17` লিখুন
2. এর সব জায়গা খুঁজে বদলে দিন:

```python
from pydantic.<module> import <object>
```

এটি দিয়ে:

```python
from pydantic.v1.<module> import <object>
```

আপনার `pydantic` সংস্করণ অনুযায়ী `pydantic`-এর v1 ফিচার এভাবে ইমপোর্ট করতে পারেন:

/// tab | `pydantic>=1.10.17,<3`

`v1.10.17` থেকে V1-এ `.v1` নেমস্পেস পাওয়া যায়, তাই নিচের মতো ইমপোর্ট করা যায়:

```python
from pydantic.v1.fields import ModelField
```

///

/// tab | `pydantic<3`

Pydantic V1 আর V2-এর সব সংস্করণ নিচের ইমপোর্ট পদ্ধতি সমর্থন করে, যদি আপনি না জানেন
কোন Pydantic সংস্করণ ব্যবহার করছেন:

```python
try:
    from pydantic.v1.fields import ModelField
except ImportError:
    from pydantic.fields import ModelField
```

///

/// note | নোট

`.v1` নেমস্পেস দিয়ে `pydantic>=1.10.17,<2`-এ মডিউল ইমপোর্ট করলে,
সেই মডিউলগুলো `.v1` ছাড়া একই ইমপোর্টের **একই** মডিউল *হবে না*, কিন্তু ইমপোর্ট করা জিনিসগুলো (class, function) একই *হবে*।
যেমন `pydantic.v1.fields is not pydantic.fields`,
কিন্তু `pydantic.v1.fields.ModelField is pydantic.fields.ModelField`। সৌভাগ্যক্রমে, বেশিরভাগ ক্ষেত্রে এটি প্রাসঙ্গিক হওয়ার সম্ভাবনা কম।
এটি শুধু মাইগ্রেশনের অভিজ্ঞতা মসৃণ করার একটি অনিবার্য পার্শ্বফল।

///

## মাইগ্রেশন গাইড { #migration-guide_1 }

নিচের অংশগুলোতে Pydantic V2-এর সবচেয়ে গুরুত্বপূর্ণ পরিবর্তনগুলোর বিস্তারিত দেওয়া হলো।

### `pydantic.BaseModel`-এর পরিবর্তন { #changes-to-pydanticbasemodel }

বিভিন্ন মেথডের নাম বদলেছে; deprecated নয় এমন সব `BaseModel` মেথডের নাম এখন হয়
`model_.*` ধাঁচের, নয়তো `__.*pydantic.*__` ধাঁচের। যেখানে সম্ভব, মাইগ্রেশন সহজ করতে আমরা পুরনো নামের deprecated মেথডগুলো রেখে দিয়েছি,
কিন্তু সেগুলো কল করলে `DeprecationWarning` দেখাবে।

| Pydantic V1 | Pydantic V2  |
| ----------- | ------------ |
| `__fields__` | `model_fields` |
| `__private_attributes__` | `__pydantic_private__` |
| `__validators__` | `__pydantic_validator__` |
| `construct()` | `model_construct()` |
| `copy()` | `model_copy()` |
| `dict()` | `model_dump()` |
| `json_schema()` | `model_json_schema()` |
| `json()` | `model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `update_forward_refs()` | `model_rebuild()` |

/// tip | মনে রাখার সহজ উপায়

V2-তে প্রায় সব মেথডের নাম `model_` দিয়ে শুরু। এর কারণ: আপনার মডেলে `dict` বা `json` নামে কোনো ফিল্ড থাকলে আগে মেথডের নামের সাথে সংঘর্ষ হতো। এখন `model_` উপসর্গ থাকায় সেই ঝামেলা নেই। FastAPI কোডে `item.dict()` লিখে থাকলে এখন লিখুন `item.model_dump()`।

///

* ডেটা লোড করার কিছু বিল্ট-ইন সুবিধা সরিয়ে ফেলার পরিকল্পনা আছে। বিশেষ করে,
    `parse_raw` আর `parse_file` এখন deprecated। Pydantic V2-তে `model_validate_json` কাজ করে `parse_raw`-এর মতো। অন্যথায়, আগে ডেটা লোড করে তারপর `model_validate`-এ দিন।
* `from_orm` মেথড deprecated হয়েছে; এখন মডেলের config-এ `from_attributes=True` সেট করা থাকলে, শুধু `model_validate` (যা
  Pydantic V1-এর `parse_obj`-এর সমতুল্য) ব্যবহার করেই একই রকম কাজ করা যায়।
* মডেলের `__eq__` (সমতা তুলনা) মেথড বদলেছে।
    * মডেল শুধু অন্য `BaseModel` ইনস্ট্যান্সের সমান হতে পারে।
    * দুটি মডেল ইনস্ট্যান্স সমান হতে হলে, এগুলোর মিল থাকতে হবে:
        * টাইপে (অথবা generic মডেলের ক্ষেত্রে, প্যারামিটার ছাড়া মূল generic টাইপে)
        * ফিল্ডের মানে
        * বাড়তি (extra) মানে (শুধু যখন `model_config['extra'] == 'allow'`)
        * private অ্যাট্রিবিউটের মানে; private অ্যাট্রিবিউটের মান ভিন্ন হলে মডেলগুলো আর সমান নয়।
        * মডেল আর তাদের ডেটা থাকা dict-এর সমান নয়।
        * ভিন্ন টাইপের non-generic মডেল কখনো সমান নয়।
        * ভিন্ন মূল টাইপের generic মডেল কখনো সমান নয়। আমরা *হুবহু* টাইপের সমতা দাবি করি না, যাতে,
            যেমন, `MyGenericModel[Any]`-এর ইনস্ট্যান্স `MyGenericModel[int]`-এর ইনস্ট্যান্সের সমান হতে পারে।
* একটি "কাস্টম রুট মডেল" নির্দিষ্ট করতে `__root__` ফিল্ড ব্যবহারের বদলে আমরা এনেছি নতুন একটি টাইপ
    [`RootModel`](concepts/models.md#rootmodel-and-custom-root-types), যা Pydantic V1-এ
    `__root__` নামের ফিল্ড ব্যবহারের কার্যকারিতার বদলে এসেছে। লক্ষ্য করুন, `RootModel` টাইপ আর `arbitrary_types_allowed`
    config সেটিং সমর্থন করে না। ব্যাখ্যার জন্য [এই issue মন্তব্য](https://github.com/pydantic/pydantic/issues/6710#issuecomment-1700948167) দেখুন।
* সিরিয়ালাইজেশন নিজের মতো করার সক্ষমতা আমরা অনেক বাড়িয়েছি। বিশেষ করে, আমরা যোগ করেছি
    [`@field_serializer`](api/functional_serializers.md#pydantic.functional_serializers.field_serializer),
    [`@model_serializer`](api/functional_serializers.md#pydantic.functional_serializers.model_serializer), আর
    [`@computed_field`](api/fields.md#pydantic.fields.computed_field) ডেকোরেটর, যেগুলো Pydantic V1-এর বিভিন্ন
    ঘাটতি পূরণ করে।
    * এই নতুন ডেকোরেটরগুলোর ব্যবহারের ডকস দেখুন [কাস্টম serializer](concepts/serialization.md#serializers)-এ।
    * পারফরম্যান্সের বাড়তি খরচ আর বাস্তবায়নের জটিলতার কারণে, model config-এ
        `json_encoders` নির্দিষ্ট করার সমর্থন এখন deprecated। এই সুবিধা মূলত কাস্টম
        সিরিয়ালাইজেশনের যুক্তির জন্য যোগ করা হয়েছিল, আর আমরা মনে করি বেশিরভাগ প্রচলিত ক্ষেত্রে নতুন সিরিয়ালাইজেশন ডেকোরেটরই ভালো পছন্দ।
* প্যারেন্ট মডেলের নেস্টেড ফিল্ড হিসেবে থাকা মডেলের সাব-ক্লাস সিরিয়ালাইজ করার আচরণ আমরা বদলেছি।
  V1-এ, আমরা সবসময় সাব-ক্লাস ইনস্ট্যান্সের সব ফিল্ড অন্তর্ভুক্ত করতাম। V2-তে, মডেল dump করার সময় শুধু
  ফিল্ডের অ্যানোটেট করা টাইপে সংজ্ঞায়িত ফিল্ডগুলোই অন্তর্ভুক্ত করি। এতে কিছু দুর্ঘটনাবশত নিরাপত্তা
  ত্রুটি এড়ানো যায় (যেমন সাব-ক্লাসের `password` ফিল্ড ভুলে বেরিয়ে যাওয়া)। এ নিয়ে আরও পড়তে পারেন (এই আচরণ বন্ধ করার উপায়সহ)
  মডেল এক্সপোর্টের ডকসের [সংশ্লিষ্ট অংশে](concepts/serialization.md#subclasses-of-model-like-types)।
* `GetterDict` সরিয়ে দেওয়া হয়েছে, কারণ এটি ছিল শুধু `orm_mode`-এর একটি ভেতরের বাস্তবায়ন, আর `orm_mode` সরিয়ে দেওয়া হয়েছে।
* অনেক ক্ষেত্রে, যাচাই আর প্রয়োজনে রূপান্তর করতে constructor-এ দেওয়া আর্গুমেন্ট **কপি** করা হবে
  ([ডকুমেন্টেশন](./concepts/models.md#attribute-copies) দেখুন)।
  constructor-এ পরিবর্তনযোগ্য (mutable) অবজেক্ট, যেমন list, আর্গুমেন্ট হিসেবে দেওয়ার ক্ষেত্রে এটি লক্ষণীয়।
* `.json()` মেথড deprecated, আর এই deprecated মেথডে `indent` বা `ensure_ascii`-এর মতো আর্গুমেন্ট
দিয়ে ব্যবহার করলে বিভ্রান্তিকর এরর হতে পারে। সেরা ফলাফলের জন্য V2-এর সমতুল্য `model_dump_json()`-এ চলে যান।
যদি তবুও ওই আর্গুমেন্টগুলো ব্যবহার করতে চান, তাহলে [এই বিকল্প উপায়](https://github.com/pydantic/pydantic/issues/8825#issuecomment-1946206415) ব্যবহার করতে পারেন।
* স্ট্রিং নয় এমন key-এর JSON সিরিয়ালাইজেশন সাধারণত `str(key)` দিয়ে করা হয়, ফলে আচরণে কিছু পরিবর্তন হয়, যেমন:

```python
from pydantic import BaseModel as V2BaseModel
from pydantic.v1 import BaseModel as V1BaseModel


class V1Model(V1BaseModel):
    a: dict[str | None, int]


class V2Model(V2BaseModel):
    a: dict[str | None, int]


v1_model = V1Model(a={None: 123})
v2_model = V2Model(a={None: 123})

# V1
print(v1_model.json())
#> {"a": {"null": 123}}

# V2
print(v2_model.model_dump_json())
#> {"a":{"None":123}}
```

* জায়গা বাঁচাতে `model_dump_json()`-এর ফলাফল সংক্ষিপ্ত (ফাঁকা স্থান ছাড়া) করা হয়, আর সবসময় হুবহু `json.dumps()`-এর আউটপুটের সাথে মেলে না।
তবে `json.dumps()`-এর ফলাফলে ব্যবহৃত বিভাজক (separator) সহজেই বদলে দুটি আউটপুট মিলিয়ে নিতে পারেন:

```python
import json

from pydantic import BaseModel as V2BaseModel
from pydantic.v1 import BaseModel as V1BaseModel


class V1Model(V1BaseModel):
    a: list[str]


class V2Model(V2BaseModel):
    a: list[str]


v1_model = V1Model(a=['fancy', 'sushi'])
v2_model = V2Model(a=['fancy', 'sushi'])

# V1
print(v1_model.json())
#> {"a": ["fancy", "sushi"]}

# V2
print(v2_model.model_dump_json())
#> {"a":["fancy","sushi"]}

# Plain json.dumps
print(json.dumps(v2_model.model_dump()))
#> {"a": ["fancy", "sushi"]}

# Modified json.dumps
print(json.dumps(v2_model.model_dump(), separators=(',', ':')))
#> {"a":["fancy","sushi"]}
```

/// info | কোড দুটি সহজ ভাষায়

* প্রথম উদাহরণ: dict-এর key `None` হলে V1-এ JSON-এ লিখত `"null"`, V2-তে লেখে `"None"` (কারণ `str(None)` = `'None'`)।
* দ্বিতীয় উদাহরণ: V2-এর `model_dump_json()` কমা আর কোলনের পরে স্পেস রাখে না (`{"a":["fancy","sushi"]}`)। `json.dumps(..., separators=(',', ':'))` দিলে সাধারণ `json.dumps`-ও একই রকম আউটপুট দেয়।

///

### `pydantic.generics.GenericModel`-এর পরিবর্তন { #changes-to-pydanticgenericsgenericmodel }

`pydantic.generics.GenericModel` ক্লাসের আর দরকার নেই, আর এটি সরিয়ে দেওয়া হয়েছে। এর বদলে, এখন
সরাসরি একটি `BaseModel` সাব-ক্লাসে প্যারেন্ট ক্লাস হিসেবে `Generic` যোগ করেই generic `BaseModel` সাব-ক্লাস তৈরি করতে পারেন।
দেখতে এমন: `class MyGenericModel(BaseModel, Generic[T]): ...`।

V1 আর V2 মডেল মেশানো সমর্থিত নয়, অর্থাৎ এমন generic `BaseModel` (V2)-এর টাইপ প্যারামিটার
V1 মডেল হতে পারবে না।

এটি এরর না দিলেও, `isinstance` যাচাইয়ে *প্যারামিটারযুক্ত* generic ব্যবহার না করার জোর পরামর্শ দিই।

* যেমন, `isinstance(my_model, MyGenericModel[int])` করা উচিত নয়।
    তবে `isinstance(my_model, MyGenericModel)` করা ঠিক আছে। (লক্ষ্য করুন, স্ট্যান্ডার্ড generic-এর ক্ষেত্রে প্যারামিটারযুক্ত generic দিয়ে
    সাব-ক্লাস যাচাই করলে এরর হতো।)
* যদি প্যারামিটারযুক্ত generic-এর বিপরীতে `isinstance` যাচাই করতেই হয়, তাহলে প্যারামিটারযুক্ত generic ক্লাসের সাব-ক্লাস
    বানিয়ে তা করতে পারেন। দেখতে এমন: `class MyIntModel(MyGenericModel[int]): ...` আর
    `isinstance(my_model, MyIntModel)`।

আরও তথ্য পাবেন [Generic মডেল](concepts/models.md#generic-models) ডকুমেন্টেশনে।

### `pydantic.Field`-এর পরিবর্তন { #changes-to-pydanticfield }

`Field` আর JSON schema-তে যোগ করার জন্য ইচ্ছামতো keyword argument সমর্থন করে না। এর বদলে, JSON schema-তে
যে বাড়তি ডেটা যোগ করতে চান তা `json_schema_extra` keyword argument-এ একটি ডিকশনারি হিসেবে দিতে হবে।

Pydantic V1-এ, কোনো alias সেট করা না থাকলে `alias` প্রপার্টি ফিল্ডের নাম ফেরত দিত।
Pydantic V2-তে এই আচরণ বদলে, কোনো alias সেট করা না থাকলে `None` ফেরত দেয়।

`Field` থেকে নিচের প্রপার্টিগুলো সরানো হয়েছে বা বদলেছে:

* `const`
* `min_items` (এর বদলে `min_length` ব্যবহার করুন)
* `max_items` (এর বদলে `max_length` ব্যবহার করুন)
* `unique_items`
* `allow_mutation` (এর বদলে `frozen` ব্যবহার করুন)
* `regex` (এর বদলে `pattern` ব্যবহার করুন)
* `final` (এর বদলে [typing.Final][] টাইপ হিন্ট ব্যবহার করুন)

ফিল্ডের শর্ত আর স্বয়ংক্রিয়ভাবে generic-এর প্যারামিটারে নিচে নামানো হয় না। যেমন, `my_list: list[str] = Field(pattern=".*")` দিয়ে আর তালিকার প্রতিটি উপাদান একটি regex-এর সাথে মেলে কিনা যাচাই করা যায় না। এর বদলে, `str`-এর নিজের ওপরেই একটি অ্যানোটেশন দিতে [`typing.Annotated`][] ব্যবহার করুন: `my_list: list[Annotated[str, Field(pattern=".*")]]`

### dataclass-এর পরিবর্তন { #changes-to-dataclasses }

`BaseModel`-এর সাব-ক্লাস না বানিয়েই স্ট্যান্ডার্ড dataclass-এ ডেটা যাচাই চালু করতে Pydantic [dataclass](concepts/dataclasses.md) এখনো
কাজের। Pydantic V2 এই dataclass-এর আচরণে নিচের পরিবর্তনগুলো এনেছে:

* ফিল্ড হিসেবে ব্যবহার করলে, dataclass (Pydantic বা সাধারণ) আর যাচাইয়ের ইনপুট হিসেবে tuple গ্রহণ করে না; এর বদলে dict
  ব্যবহার করতে হবে।
* Pydantic dataclass-এর `__post_init__` এখন যাচাইয়ের আগে নয়, যাচাইয়ের *পরে* কল হবে।
    * ফলে `__post_init_post_parse__` মেথড অপ্রয়োজনীয় হয়ে পড়ত, তাই সরিয়ে দেওয়া হয়েছে।
* Pydantic আর Pydantic dataclass-এর জন্য `extra='allow'` সমর্থন করে না, যেখানে initializer-এ দেওয়া বাড়তি ফিল্ড
    dataclass-এ বাড়তি অ্যাট্রিবিউট হিসেবে রাখা হতো। ডেটা পার্স করার সময় অপ্রত্যাশিত ফিল্ড উপেক্ষা করার জন্য
    `extra='ignore'` এখনো সমর্থিত, শুধু সেগুলো ইনস্ট্যান্সে রাখা হবে না।
* Pydantic dataclass-এ আর `__pydantic_model__` অ্যাট্রিবিউট নেই, আর যাচাই বা অন্য সুবিধার জন্য ভেতরে একটি `BaseModel`
    ব্যবহার করে না।
    * যাচাই করতে, একটি JSON schema তৈরি করতে, বা V1-এ `__pydantic_model__` দরকার হতো এমন
        অন্য যেকোনো সুবিধা ব্যবহার করতে, এখন dataclass-টিকে একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] দিয়ে মুড়ে ([নিচে আরও আলোচনা করা হয়েছে](#introduction-of-typeadapter))
        তার মেথডগুলো ব্যবহার করতে হবে।
* Pydantic V1-এ, যদি একটি সাধারণ (non-Pydantic) dataclass ফিল্ড হিসেবে ব্যবহার করতেন, তাহলে প্যারেন্ট টাইপের config
    ওই dataclass-এর নিজের config হিসেবেও ব্যবহার হতো। Pydantic V2-তে আর তা হয় না।
    * Pydantic V2-তে config ওভাররাইড করতে (যেমন `BaseModel`-এ `model_config` দিয়ে করতেন),
        `@dataclass` ডেকোরেটরের `config` প্যারামিটার ব্যবহার করতে পারেন।
        উদাহরণ দেখুন [Dataclass Config](concepts/dataclasses.md#dataclass-config)-এ।

### config-এর পরিবর্তন { #changes-to-config }

* Pydantic V2-তে একটি মডেলে config নির্দিষ্ট করতে, `model_config` নামের একটি ক্লাস অ্যাট্রিবিউট সেট করতে হবে,
  যা হবে আপনার চাওয়া config-এর key/value জোড়াসহ একটি dict। প্যারেন্ট `BaseModel` সাব-ক্লাসের ভেতরে `Config` নামের ক্লাস তৈরির
  Pydantic V1-এর পদ্ধতি এখন deprecated।

* একটি মডেলের সাব-ক্লাস বানালে, `model_config` অ্যাট্রিবিউট উত্তরাধিকারসূত্রে আসে। অনেক মডেলের জন্য একটি নির্দিষ্ট config-সহ
একটি বেস ক্লাস ব্যবহার করতে চাইলে এটি কাজের। লক্ষ্য করুন, যদি একাধিক `BaseModel` সাব-ক্লাস থেকে উত্তরাধিকার নেন,
যেমন `class MyModel(Model1, Model2)`, তাহলে দুই মডেলের `model_config`-এর ডিফল্ট নয় এমন সেটিংসগুলো
মিলিত হবে, আর দুটিতেই সংজ্ঞায়িত সেটিংসের ক্ষেত্রে `Model2`-এরগুলো `Model1`-এরগুলোকে ওভাররাইড করবে।

* নিচের config সেটিংসগুলো সরিয়ে দেওয়া হয়েছে:
    * `allow_mutation` — এটি সরিয়ে দেওয়া হয়েছে। এর সমতুল্য হিসেবে [`frozen`](api/config.md#pydantic.config.ConfigDict.frozen) ব্যবহার করতে পারবেন (বর্তমান ব্যবহারের উল্টো অর্থে)।
    * `error_msg_templates`
    * `fields` — এটি বিভিন্ন বাগের উৎস ছিল, তাই সরিয়ে দেওয়া হয়েছে।
      ফিল্ডগুলো ইচ্ছামতো বদলাতে ফিল্ডে `Annotated` ব্যবহার করতে পারবেন।
    * `getter_dict` — `orm_mode` সরিয়ে দেওয়া হয়েছে, আর এই ভেতরের বাস্তবায়ন আর দরকার নেই।
    * `smart_union` - Pydantic V2-তে ডিফল্ট `union_mode` হলো `'smart'`।
    * `underscore_attrs_are_private` — Pydantic V2-এর আচরণ এখন এমন, যেন Pydantic V1-এ এটি সবসময়
      `True` সেট করা ছিল।
    * `json_loads`
    * `json_dumps`
    * `copy_on_model_validation`
    * `post_init_call`

* নিচের config সেটিংসগুলোর নাম বদলেছে:
    * `allow_population_by_field_name` → `populate_by_name` (অথবা v2.11 থেকে `validate_by_name`)
    * `anystr_lower` → `str_to_lower`
    * `anystr_strip_whitespace` → `str_strip_whitespace`
    * `anystr_upper` → `str_to_upper`
    * `keep_untouched` → `ignored_types`
    * `max_anystr_length` → `str_max_length`
    * `min_anystr_length` → `str_min_length`
    * `orm_mode` → `from_attributes`
    * `schema_extra` → `json_schema_extra`
    * `validate_all` → `validate_default`

আরও বিস্তারিত জানতে দেখুন [`ConfigDict` API রেফারেন্স][pydantic.config.ConfigDict]।

/// tip | উদাহরণ দিয়ে বুঝি

V1-এ লিখতেন:
`class Config: orm_mode = True`

V2-তে লিখুন:
`model_config = ConfigDict(from_attributes=True)`

FastAPI-তে SQLAlchemy-র মতো ORM অবজেক্ট থেকে মডেল বানাতে আগে `orm_mode` দিতেন, এখন `from_attributes`।

///

### validator-এর পরিবর্তন { #changes-to-validators }

#### `@validator` আর `@root_validator` deprecated { #validator-and-root_validator-are-deprecated }

* `@validator` deprecated হয়েছে, আর এর বদলে [`@field_validator`](concepts/validators.md) ব্যবহার করা উচিত, যাতে বিভিন্ন নতুন ফিচার
    আর উন্নতি আছে।
    * নতুন `@field_validator` ডেকোরেটরে `each_item` keyword argument নেই; একটি generic container-এর ভেতরের আইটেমগুলোতে যে validator
        প্রয়োগ করতে চান, সেগুলো টাইপ আর্গুমেন্টে অ্যানোটেশন দিয়ে যোগ করতে হবে। বিস্তারিত দেখুন
        [Annotated metadata-তে validator](concepts/types.md#using-the-annotated-pattern)।
        দেখতে এমন: `list[Annotated[int, Field(ge=0)]]`
    * এমনকি deprecated `@validator` ডেকোরেটর ব্যবহার চালিয়ে গেলেও, validator ফাংশনের signature-এ আর `field` বা
        `config` আর্গুমেন্ট যোগ করতে পারবেন না। এগুলো দরকার হলে, আপনাকে
        `@field_validator`-এ মাইগ্রেট করতে হবে — বিস্তারিত দেখুন [পরের অংশে](#changes-to-validators-allowed-signatures)।
    * যদি একটি validator ফাংশনে `always=True` keyword argument ব্যবহার করেন, তাহলে খেয়াল রাখুন যে অ্যানোটেট করা টাইপের
        স্ট্যান্ডার্ড validator-ও ডিফল্ট মানের ওপর প্রয়োগ হবে, শুধু কাস্টম validator নয়। যেমন,
        নিচের validator কখনো এরর না দিলেও, নিচের কোড একটি `ValidationError` দেয় (কারণ ডিফল্ট `1` একটি `str` নয়):

/// note | নোট

এটি এড়াতে `Field` ফাংশনের `validate_default` আর্গুমেন্ট ব্যবহার করতে পারেন। `True` সেট করলে এটি Pydantic v1-এর `always=True`-এর আচরণ অনুকরণ করে। তবে `validate_default` ব্যবহারের নতুন পদ্ধতিই উৎসাহিত করা হয়, কারণ এতে বেশি নমনীয়তা আর নিয়ন্ত্রণ পাওয়া যায়।

///

```python
from pydantic import BaseModel, validator


class Model(BaseModel):
    x: str = 1

    @validator('x', always=True)
    @classmethod
    def validate_x(cls, v):
        return v


Model()
```

* `@root_validator` deprecated হয়েছে, আর এর বদলে
    [`@model_validator`](api/functional_validators.md#pydantic.functional_validators.model_validator) ব্যবহার করা উচিত, যাতেও নতুন ফিচার আর উন্নতি আছে।
    খেয়াল রাখুন যে অনুমোদিত signature বদলেছে ([সংশ্লিষ্ট ডকুমেন্টেশন](./concepts/validators.md#model-validators) দেখুন)।
    * কিছু পরিস্থিতিতে (যেমন যখন `model_config['validate_assignment'] is True` আর মান বসানো হয়),
        `@model_validator` ডেকোরেটর মানের একটি dict নয়, মডেলের একটি ইনস্ট্যান্স পাবে। এই ক্ষেত্রটি
        সামলাতে সতর্ক থাকতে হতে পারে।
    * এমনকি deprecated `@root_validator` ডেকোরেটর ব্যবহার চালিয়ে গেলেও, যাচাইয়ের যুক্তিতে রিফ্যাক্টরের কারণে,
        আর `skip_on_failure=False` দিয়ে চালাতে পারবেন না (যা এই keyword argument-এর ডিফল্ট মান,
        তাই একে স্পষ্টভাবে `True` সেট করতে হবে)।

#### `@validator`-এর অনুমোদিত signature-এর পরিবর্তন { #changes-to-validators-allowed-signatures }

Pydantic V1-এ, `@validator` দিয়ে মোড়ানো ফাংশনগুলো কী যাচাই হচ্ছে সে সম্পর্কে মেটাডেটাসহ keyword argument
পেতে পারত। Pydantic V2-এর `@field_validator` থেকে এর কিছু আর্গুমেন্ট সরিয়ে দেওয়া হয়েছে:

* `config`: Pydantic V2-এর config এখন একটি ক্লাসের বদলে একটি ডিকশনারি, অর্থাৎ এই আর্গুমেন্ট আর পুরনো কোডের সাথে
    সামঞ্জস্যপূর্ণ নয়। config ব্যবহার করতে হলে আপনাকে `@field_validator`-এ মাইগ্রেট করে
    `info.config` ব্যবহার করতে হবে।
* `field`: এই আর্গুমেন্ট আগে ছিল একটি `ModelField` অবজেক্ট, যা ছিল প্রায়-অভ্যন্তরীণ একটি ক্লাস আর Pydantic V2-তে
    আর নেই। এর বেশিরভাগ তথ্য এখনো `info.field_name` থেকে ফিল্ডের নাম নিয়ে
    `cls.model_fields`-এ খুঁজে পাওয়া যায়।

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int, info: ValidationInfo) -> int:
        assert info.config is not None
        print(info.config.get('title'))
        #> Model
        print(cls.model_fields[info.field_name].is_required())
        #> True
        return v


Model(x=1)
```

/// info | কোডটি সহজ ভাষায়

`info: ValidationInfo` প্যারামিটার দিয়ে validator-এর ভেতরে প্রসঙ্গের তথ্য পাওয়া যায়: `info.config` হলো মডেলের config (এখানে title `Model`), আর `info.field_name` হলো কোন ফিল্ড যাচাই হচ্ছে (`'x'`)। সেই নাম দিয়ে `cls.model_fields['x']` থেকে ফিল্ডের তথ্য (যেমন এটি বাধ্যতামূলক কিনা) পাওয়া যায়।

///

#### validator-এ `TypeError` আর `ValidationError`-এ রূপান্তরিত হয় না { #typeerror-is-no-longer-converted-to-validationerror-in-validators }

আগে, একটি validator ফাংশনের ভেতরে `TypeError` হলে, সেই এররটি একটি `ValidationError`-এ মুড়ে দেওয়া হতো,
আর কিছু ক্ষেত্রে (যেমন FastAPI-তে) এই এররগুলো শেষ ব্যবহারকারীকে দেখানো হতো। এতে নানা
অনাকাঙ্ক্ষিত আচরণ হতো &mdash; যেমন, ভুল signature দিয়ে একটি ফাংশন কল করলে ব্যবহারকারীর সামনে একটি
`ValidationError` দেখা যেতে পারত।

তবে Pydantic V2-তে, একটি validator-এ `TypeError` হলে তা আর
`ValidationError`-এ রূপান্তরিত হয় না:

```python
import pytest

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int) -> int:
        return str.lower(v)  # raises a TypeError


with pytest.raises(TypeError):
    Model(x=1)
```

এটি সব যাচাইয়ের ডেকোরেটরের ক্ষেত্রে প্রযোজ্য।

(অর্থাৎ validator-এ আপনার কোডের বাগ এখন বাগ হিসেবেই দেখা যাবে, ব্যবহারকারীর ভুল ইনপুট হিসেবে লুকিয়ে থাকবে না। ইনপুট ভুল বোঝাতে চাইলে validator-এ `ValueError` raise করুন।)

#### validator-এর আচরণের পরিবর্তন { #validator-behavior-changes }

Pydantic V2-তে টাইপ রূপান্তরে কিছু পরিবর্তন এসেছে। যেমন:

* `int`, `float` আর `Decimal` মানকে স্ট্রিংয়ে রূপান্তর এখন ঐচ্ছিক আর ডিফল্টভাবে বন্ধ, দেখুন
  [সংখ্যাকে স্ট্রিংয়ে রূপান্তর][pydantic.config.ConfigDict.coerce_numbers_to_str]।
* জোড়ার iterable (যেমন `[('a', 1)]`) আর dict-এ রূপান্তরিত হয় না।

Pydantic V2-এর টাইপ রূপান্তরের ডিফল্ট সম্পর্কে বিস্তারিত দেখুন [রূপান্তর সারণি](concepts/conversion_table.md)-তে।

#### `allow_reuse` keyword argument আর দরকার নেই { #the-allow_reuse-keyword-argument-is-no-longer-necessary }

আগে, Pydantic ডেকোরেটরে "পুনরায় ব্যবহৃত" ফাংশন ট্র্যাক করত, কারণ এটি ভুলের একটি প্রচলিত উৎস ছিল।
আমরা এটি করতাম ফাংশনের পূর্ণ নাম (মডিউলের নাম + ফাংশনের নাম) তুলনা করে, যাতে ভুল ইতিবাচক ফল
আসতে পারত। ইচ্ছাকৃত হলে এটি বন্ধ করতে `allow_reuse` keyword argument ব্যবহার করা যেত।

বারবার সংজ্ঞায়িত ফাংশন শনাক্ত করার আমাদের পদ্ধতি নতুন করে সাজানো হয়েছে, এখন শুধু একটি ক্লাসের ভেতরে পুনঃসংজ্ঞার
ক্ষেত্রেই এরর দেয়, ফলে ভুল ইতিবাচক ফল কমে, আর আচরণটি একটি ক্লাসে একই নামে একাধিকবার মেথড সংজ্ঞায়িত করলে
টাইপ চেকার আর linter যে এরর দেয় তার আরও কাছাকাছি হয়।

প্রায় সব ক্ষেত্রেই, যদি `allow_reuse=True` ব্যবহার করে থাকেন, তাহলে শুধু সেই keyword argument মুছে দিলেই
সবকিছু প্রত্যাশামতো কাজ করতে থাকবে।

#### `@validate_arguments`-এর নাম বদলে হয়েছে `@validate_call` { #validate_arguments-has-been-renamed-to-validate_call }

Pydantic V2-তে `@validate_arguments` ডেকোরেটরের নাম বদলে `@validate_call` করা হয়েছে।

Pydantic V1-এ, ডেকোরেট করা ফাংশনে বিভিন্ন অ্যাট্রিবিউট যোগ হতো, যেমন `raw_function`, আর `validate`
(যা দিয়ে ডেকোরেট করা ফাংশন আসলে কল না করেই আর্গুমেন্ট যাচাই করা যেত)। এই অ্যাট্রিবিউটগুলোর সীমিত
ব্যবহার আর বাস্তবায়নে পারফরম্যান্স-কেন্দ্রিক পরিবর্তনের কারণে, `@validate_call`-এ আমরা এই সুবিধা রাখিনি।

### ইনপুটের টাইপ রাখা হয় না { #input-types-are-not-preserved }

Pydantic V1-এ আমরা generic collection-এর ক্ষেত্রে সব ফিল্ডের ইনপুটের টাইপ রেখে দিতে অনেক চেষ্টা করতাম, যখন সেগুলো
ফিল্ডের অ্যানোটেশনের সঠিক সাব-টাইপ হতো। যেমন, অ্যানোটেশন `Mapping[str, int]` হলে যদি একটি
`collection.Counter()` দিতেন, তাহলে মান হিসেবে একটি `collection.Counter()`-ই পেতেন।

V2-তে এই আচরণ সমর্থন করলে সাধারণ ক্ষেত্রে পারফরম্যান্সে নেতিবাচক প্রভাব পড়ত
(প্রতিবার টাইপ যাচাই করতে হতো) আর যাচাইয়ে অনেক জটিলতা যোগ হতো। তা ছাড়া, V1-এও এই আচরণ
অসংগত আর আংশিক ভাঙা ছিল: এটি অনেক টাইপের (`str`, `UUID` ইত্যাদি) ক্ষেত্রে কাজ করত না, আর generic
collection-এর ক্ষেত্রে অনেক বিশেষ ব্যবস্থা ছাড়া মূল ইনপুট সঠিকভাবে আবার তৈরি করা অসম্ভব
(`ChainMap`-এর কথা ভাবুন; ইনপুট আবার তৈরি করা দরকার কারণ যাচাইয়ের পরে মানগুলো বদলাতে হয়, যেমন
স্ট্রিংকে int-এ রূপান্তর করলে)।

Pydantic V2-তে আমরা আর সব ক্ষেত্রে ইনপুটের টাইপ রাখার চেষ্টা করি না; বরং শুধু প্রতিশ্রুতি দিই যে আউটপুটের
টাইপ টাইপ অ্যানোটেশনের সাথে মিলবে।

`Mapping`-এর উদাহরণে ফিরে গেলে, আমরা প্রতিশ্রুতি দিই যে আউটপুট একটি বৈধ `Mapping` হবে, আর বাস্তবে এটি হবে একটি
সাধারণ `dict`:

```python
from collections.abc import Mapping

from pydantic import TypeAdapter


class MyDict(dict):
    pass


ta = TypeAdapter(Mapping[str, int])
v = ta.validate_python(MyDict())
print(type(v))
#> <class 'dict'>
```

যদি আউটপুট একটি নির্দিষ্ট টাইপের হতে হয়, তাহলে সেভাবে অ্যানোটেট করার বা একটি কাস্টম validator বাস্তবায়নের কথা ভাবুন:

```python
from collections.abc import Mapping
from typing import Annotated, Any, TypeVar

from pydantic import (
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)


def restore_input_type(
    value: Any, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> Any:
    return type(value)(handler(value))


T = TypeVar('T')
PreserveType = Annotated[T, WrapValidator(restore_input_type)]


ta = TypeAdapter(PreserveType[Mapping[str, int]])


class MyDict(dict):
    pass


v = ta.validate_python(MyDict())
assert type(v) is MyDict
```

/// info | কোডটি সহজ ভাষায়

`restore_input_type` একটি wrap validator: আগে `handler(value)` দিয়ে Pydantic-এর স্বাভাবিক যাচাই চালায় (যা একটি সাধারণ `dict` দেয়), তারপর `type(value)(...)` দিয়ে ফলাফলটিকে আবার ইনপুটের মূল টাইপে (এখানে `MyDict`) বানিয়ে দেয়। `PreserveType[...]` হলো এই আচরণসহ একটি পুনরায় ব্যবহারযোগ্য টাইপ।

///

যদিও আমরা সব জায়গায় ইনপুটের টাইপ রাখার প্রতিশ্রুতি দিই না, `BaseModel`-এর সাব-ক্লাস আর dataclass-এর ক্ষেত্রে আমরা *ঠিকই*
সেগুলো রাখি:

```python
import pydantic.dataclasses
from pydantic import BaseModel


class InnerModel(BaseModel):
    x: int


class OuterModel(BaseModel):
    inner: InnerModel


class SubInnerModel(InnerModel):
    y: int


m = OuterModel(inner=SubInnerModel(x=1, y=2))
print(m)
#> inner=SubInnerModel(x=1, y=2)


@pydantic.dataclasses.dataclass
class InnerDataclass:
    x: int


@pydantic.dataclasses.dataclass
class SubInnerDataclass(InnerDataclass):
    y: int


@pydantic.dataclasses.dataclass
class OuterDataclass:
    inner: InnerDataclass


d = OuterDataclass(inner=SubInnerDataclass(x=1, y=2))
print(d)
#> OuterDataclass(inner=SubInnerDataclass(x=1, y=2))
```

### স্ট্যান্ডার্ড টাইপ সামলানোর পরিবর্তন { #changes-to-handling-of-standard-types }

#### Dict { #dicts }

`dict` টাইপের ফিল্ডে জোড়ার iterable (খালি iterable-সহ) আর যাচাইয়ে উত্তীর্ণ হয় না।

#### Union { #unions }

Union টাইপ এখনো বাঁ থেকে ডানে প্রতিটি বিকল্প দিয়ে যাচাইয়ের চেষ্টা করলেও, এখন যখনই সম্ভব ইনপুটের টাইপ রেখে দেয়,
এমনকি যদি সঠিক টাইপটি প্রথম বিকল্প না হয় যার জন্য ইনপুটটি যাচাইয়ে উত্তীর্ণ হতো।
উদাহরণ হিসেবে, নিচেরটি দেখুন:

```python
from pydantic import BaseModel


class Model(BaseModel):
    x: int | str


print(Model(x='1'))
#> x='1'
```

Pydantic V1-এ ছাপা ফলাফল হতো `x=1`, কারণ মানটি `int` হিসেবে যাচাইয়ে উত্তীর্ণ হতো।
Pydantic V2-তে আমরা চিনতে পারি যে মানটি বিকল্পগুলোর একটির হুবহু ইনস্ট্যান্স (`'1'` আসলেই একটি `str`), তাই স্ট্যান্ডার্ড union যাচাই সংক্ষেপে শেষ করি।

V1-এর মতো বাঁ-থেকে-ডানে আচরণে ফিরে যেতে, union-কে `Field(union_mode='left_to_right')` দিয়ে অ্যানোটেট করুন।
আরও বিস্তারিত দেখুন [Union মোড](./concepts/unions.md#union-modes)-এ।

#### বাধ্যতামূলক, ঐচ্ছিক আর nullable ফিল্ড { #required-optional-and-nullable-fields }

`Optional` হিসেবে অ্যানোটেট করা একটি ফিল্ড বাধ্যতামূলক (কোনো ডিফল্ট মান নেই) নাকি নয় (ডিফল্ট মান `None` বা সংশ্লিষ্ট টাইপের অন্য কোনো মান আছে),
তা নির্ধারণের কিছু যুক্তি Pydantic V2 বদলেছে, আর এখন এটি `dataclasses`-এর আচরণের
আরও কাছাকাছি। একইভাবে, `Any` হিসেবে অ্যানোটেট করা ফিল্ডের ডিফল্ট মান আর `None` নয়।

নিচের সারণিতে V2-তে ফিল্ড অ্যানোটেশনের আচরণ দেখানো হলো:

| অবস্থা                                                 | ফিল্ডের সংজ্ঞা            |
|-------------------------------------------------------|-----------------------------|
| বাধ্যতামূলক, `None` হতে পারে না                            | `f1: str`                   |
| বাধ্যতামূলক নয়, `None` হতে পারে না, ডিফল্টভাবে `'abc'` | `f2: str = 'abc'`           |
| বাধ্যতামূলক, `None` হতে পারে                               | `f3: Optional[str]`         |
| বাধ্যতামূলক নয়, `None` হতে পারে, ডিফল্টভাবে `None`     | `f4: Optional[str] = None`  |
| বাধ্যতামূলক নয়, `None` হতে পারে, ডিফল্টভাবে `'abc'`    | `f5: Optional[str] = 'abc'` |
| বাধ্যতামূলক, যেকোনো টাইপ হতে পারে (`None`-সহ)          | `f6: Any`                   |
| বাধ্যতামূলক নয়, যেকোনো টাইপ হতে পারে (`None`-সহ)      | `f7: Any = None`            |

/// note | নোট

`typing.Optional[T]` হিসেবে অ্যানোটেট করা একটি ফিল্ড বাধ্যতামূলক হবে, আর `None` মান গ্রহণ করবে।
এর মানে এই নয় যে ফিল্ডটির ডিফল্ট মান `None`। *(এটি V1 থেকে একটি breaking change।)*

///

/// note | নোট

কোনো ডিফল্ট মান দিলেই ফিল্ডটি বাধ্যতামূলক থাকে না।

///

/// warning | সাধারণ ভুল

V1-এ `name: Optional[str]` লিখলে ফিল্ডটি ঐচ্ছিক হতো (ডিফল্ট `None`)। V2-তে একই লেখায় ফিল্ডটি **বাধ্যতামূলক**, শুধু `None` দেওয়ার অনুমতি আছে। পুরনো আচরণ চাইলে স্পষ্ট করে `= None` লিখুন: `name: Optional[str] = None` (বা `name: str | None = None`)। এই একটি পরিবর্তনই মাইগ্রেশনের সময় সবচেয়ে বেশি এরর তৈরি করে।

///

ওপরের বিষয়টি দেখানো একটি কোড উদাহরণ:

```python
from typing import Optional

from pydantic import BaseModel, ValidationError


class Foo(BaseModel):
    f1: str  # required, cannot be None
    f2: Optional[str]  # required, can be None - same as str | None
    f3: Optional[str] = None  # not required, can be None
    f4: str = 'Foobar'  # not required, but cannot be None


try:
    Foo(f1=None, f2=None, f4='b')
except ValidationError as e:
    print(e)
    """
    1 validation error for Foo
    f1
      Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    """
```

#### স্ট্রিংয়ে pattern / regex { #patterns-regex-on-strings }

Pydantic V1 Python-এর regex লাইব্রেরি ব্যবহার করত। Pydantic V2 ব্যবহার করে Rust-এর [regex crate]।
এই crate শুধু "রেগুলার এক্সপ্রেশনের একটি Rust সংস্করণ" নয়, এটি রেগুলার এক্সপ্রেশনের সম্পূর্ণ ভিন্ন একটি পদ্ধতি।
বিশেষ করে, এটি কয়েকটি ফিচার (যেমন look around আর backreference) বাদ দেওয়ার বিনিময়ে স্ট্রিংয়ে রৈখিক সময়ে (linear time) খোঁজার প্রতিশ্রুতি দেয়।
আমরা মনে করি এই বিনিময় যুক্তিসঙ্গত, বিশেষ করে কারণ Pydantic অবিশ্বস্ত ইনপুট যাচাইয়ে ব্যবহার হয়, যেখানে নিশ্চিত করা গুরুত্বপূর্ণ যে অবিশ্বস্ত ইনপুটের ওপর নির্ভর করে কোনো কিছু দুর্ঘটনাবশত সূচকীয় (exponential) সময় নিয়ে চলবে না।
অন্যদিকে, যারা এই ফিচারগুলো ব্যবহার করেন না, তাদের জন্য জটিল regex যাচাই অনেক গুণ দ্রুত হওয়া উচিত, কারণ এটি Rust-এ আর রৈখিক সময়ে হয়।

(এর ফলে "ReDoS" নামের আক্রমণ, যেখানে বিশেষভাবে তৈরি একটি লম্বা স্ট্রিং পাঠিয়ে সার্ভারকে আটকে দেওয়া হয়, তা থেকে আপনার API সুরক্ষিত থাকে।)

যদি তবুও Python-এর regex লাইব্রেরি ব্যবহার করতে চান, তাহলে [`regex_engine`](./api/config.md#pydantic.config.ConfigDict.regex_engine) config সেটিং ব্যবহার করতে পারেন।

[regex crate]: https://github.com/rust-lang/regex

### float থেকে integer-এ টাইপ রূপান্তর { #type-conversion-from-floats-to-integers }

V1-এ, যখনই একটি ফিল্ড `int` হিসেবে অ্যানোটেট করা থাকত, যেকোনো float মান গ্রহণ করা হতো, ফলে float মানের দশমিক অংশ শূন্য না হলে
ডেটা হারানোর সম্ভাবনা ছিল। V2-তে, float থেকে integer-এ রূপান্তর শুধু তখনই অনুমোদিত
যখন দশমিক অংশ শূন্য:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


print(Model(x=10.0))
#> x=10
try:
    Model(x=10.2)
except ValidationError as err:
    print(err)
    """
    1 validation error for Model
    x
      Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=10.2, input_type=float]
    """
```

(অর্থাৎ `10.0` → `10` চলবে, কিন্তু `10.2` দিলে এরর, কারণ `.2` চুপচাপ হারিয়ে যাওয়া উচিত নয়।)

### `TypeAdapter`-এর আগমন { #introduction-of-typeadapter }

Pydantic V1-এ `BaseModel` নয় এমন টাইপ যাচাই বা সিরিয়ালাইজ করার সমর্থন দুর্বল ছিল।

এগুলো নিয়ে কাজ করতে, আপনাকে হয় একটি "root" মডেল তৈরি করতে হতো, নয়তো `pydantic.tools`-এর ইউটিলিটি ফাংশন
(যেমন `parse_obj_as` আর `schema_of`) ব্যবহার করতে হতো।

Pydantic V2-তে এটি *অনেক* সহজ: [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ক্লাস দিয়ে আপনি যেকোনো টাইপের জন্য
যাচাই, সিরিয়ালাইজ আর JSON schema তৈরির মেথডসহ একটি অবজেক্ট তৈরি করতে পারেন।
এটি `parse_obj_as` আর `schema_of`-এর (যা এখন deprecated) সম্পূর্ণ বিকল্প,
আর "root" মডেলের কিছু ব্যবহারের ক্ষেত্রও কভার করে। ([`RootModel`](concepts/models.md#rootmodel-and-custom-root-types),
[যা ওপরে আলোচনা করা হয়েছে](#changes-to-pydanticbasemodel), বাকিগুলো কভার করে।)

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
assert adapter.validate_python(['1', '2', '3']) == [1, 2, 3]
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

প্রচলিত টাইপ চেকারগুলোর generic টাইপ অনুমানের সীমাবদ্ধতার কারণে, কিছু পরিস্থিতিতে সঠিক টাইপিং পেতে
আপনাকে generic প্যারামিটার স্পষ্টভাবে নির্দিষ্ট করতে হতে পারে:

```python
from pydantic import TypeAdapter

adapter = TypeAdapter[str | int](str | int)
...
```

আরও তথ্যের জন্য দেখুন [Type Adapter](concepts/type_adapter.md)।

### কাস্টম টাইপ সংজ্ঞায়িত করা { #defining-custom-types }

Pydantic-এ কাস্টম টাইপ সংজ্ঞায়িত করার পদ্ধতি আমরা সম্পূর্ণ নতুন করে সাজিয়েছি।

`pydantic-core` আর JSON schema দুটোই তৈরির জন্য আমরা hook উন্মুক্ত করেছি, যাতে নিজের কাস্টম টাইপ ব্যবহার করলেও
Pydantic V2-এর পারফরম্যান্সের সব সুবিধা পান।

নিজের টাইপে কাস্টম যাচাই যোগ করতে [`typing.Annotated`][] ব্যবহারের উপায়ও আমরা এনেছি।

প্রধান পরিবর্তনগুলো হলো:

* `__get_validators__`-এর বদলে `__get_pydantic_core_schema__` ব্যবহার করতে হবে।
  আরও তথ্যের জন্য দেখুন [কাস্টম ডেটা টাইপ](concepts/types.md#customizing_validation_with_get_pydantic_core_schema)।
* `__modify_schema__` হয়েছে `__get_pydantic_json_schema__`।
  আরও তথ্যের জন্য দেখুন [JSON Schema কাস্টমাইজেশন](concepts/json_schema.md#customizing-json-schema)।

তা ছাড়া, একটি টাইপের `__get_pydantic_core_schema__` আর `__get_pydantic_json_schema__` ফাংশন বদলাতে বা দিতে,
টাইপটি নিজে না বদলে, সেটিকে [`typing.Annotated`][] দিয়ে অ্যানোটেট করতে পারেন।
এটি তৃতীয় পক্ষের টাইপ Pydantic-এর সাথে যুক্ত করার একটি শক্তিশালী আর নমনীয় ব্যবস্থা দেয়, আর কিছু ক্ষেত্রে
কাস্টম টাইপের সীমাবদ্ধতা এড়াতে Pydantic V1-এ যোগ করা জোড়াতালি সরিয়ে ফেলতে সাহায্য করতে পারে।

আরও তথ্যের জন্য দেখুন [কাস্টম ডেটা টাইপ](concepts/types.md#custom-types)।

### JSON schema তৈরির পরিবর্তন { #changes-to-json-schema-generation }

বছরের পর বছর ধরে pydantic যে JSON schema তৈরি করে, তাতে পরিবর্তনের অনেক অনুরোধ আমরা পেয়েছি।

Pydantic V2-তে, আমরা অনেক প্রচলিত অনুরোধ পূরণের চেষ্টা করেছি:

* `Optional` ফিল্ডের JSON schema এখন দেখায় যে `null` মান অনুমোদিত।
* `Decimal` টাইপ এখন JSON schema-তে একটি স্ট্রিং হিসেবে দেখানো (আর সিরিয়ালাইজ করা) হয়।
* JSON schema আর namedtuple-কে namedtuple হিসেবে রাখে না।
* আমরা ডিফল্টভাবে যে JSON schema তৈরি করি তা এখন draft 2020-12 লক্ষ্য করে (কিছু OpenAPI সম্প্রসারণসহ)।
* যখন দুটি ভিন্ন হয়, এখন নির্দিষ্ট করতে পারেন যে JSON schema যাচাইয়ের ইনপুট বোঝাবে,
    নাকি সিরিয়ালাইজেশনের আউটপুট।

তবে বছরের পর বছর ধরে পরিবর্তনের অনেক যুক্তিসঙ্গত অনুরোধ ছিল যা আমরা বাস্তবায়ন না করার সিদ্ধান্ত নিয়েছি।

Pydantic V1-এ, এমনকি আপনি নিজে পরিবর্তন বাস্তবায়ন করতে রাজি থাকলেও, তা খুব কঠিন ছিল, কারণ JSON schema
তৈরির প্রক্রিয়ায় বিভিন্ন পুনরাবৃত্ত (recursive) ফাংশন কল জড়িত ছিল; একটি ওভাররাইড করতে, পুরো
বাস্তবায়ন কপি করে বদলাতে হতো।

Pydantic V2-তে, আমাদের ডিজাইনের একটি লক্ষ্য ছিল JSON schema তৈরি নিজের মতো করা সহজ করা। এজন্য আমরা
[`GenerateJsonSchema`](api/json_schema.md#pydantic.json_schema.GenerateJsonSchema) ক্লাস এনেছি,
যা একটি টাইপের pydantic-core schema-কে একটি JSON schema-তে
রূপান্তর বাস্তবায়ন করে। নকশা অনুযায়ী, এই ক্লাস JSON schema তৈরির প্রক্রিয়াকে ছোট ছোট মেথডে ভাগ করে, যেগুলো
সাব-ক্লাসে সহজে ওভাররাইড করে JSON schema তৈরির "সার্বিক" পদ্ধতি বদলানো যায়।

JSON schema তৈরির বিভিন্ন মেথড (যেমন `BaseModel.model_json_schema` বা
`TypeAdapter.json_schema`) একটি keyword argument `schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema` গ্রহণ করে,
আর JSON schema তৈরিতে নিজের পদ্ধতি ব্যবহার করতে এই মেথডগুলোতে আপনার কাস্টম সাব-ক্লাস দিতে পারেন।

আশা করি এর মানে, যদি আমাদের কোনো সিদ্ধান্তের সাথে আপনি একমত না হন, বা যদি আপনি Pydantic V1-এর এমন আচরণের ওপর নির্ভরশীল হন
যা Pydantic V2-তে বদলেছে, তাহলে একটি কাস্টম `schema_generator` ব্যবহার করে, আপনার অ্যাপ্লিকেশনের প্রয়োজনমতো
`GenerateJsonSchema` ক্লাস বদলে নিতে পারবেন।

### `BaseSettings` সরে গেছে `pydantic-settings`-এ { #basesettings-has-moved-to-pydantic-settings }

Pydantic-এর [সেটিংস ব্যবস্থাপনার](concepts/pydantic_settings.md) মূল অবজেক্ট [`BaseSettings`](api/pydantic_settings.md#pydantic_settings.BaseSettings)
একটি আলাদা প্যাকেজে সরানো হয়েছে,
[`pydantic-settings`](https://github.com/pydantic/pydantic-settings)।

তা ছাড়া, `parse_env_var` classmethod সরিয়ে দেওয়া হয়েছে। তাই নিজের পার্সিং ফাংশন রাখতে আপনাকে
[সেটিংসের উৎস নিজের মতো করতে](concepts/pydantic_settings.md#customise-settings-sources) হবে।

(FastAPI-র [সেটিংস এবং এনভায়রনমেন্ট ভেরিয়েবল](../advanced/settings.md) পেজে যে `pip install pydantic-settings` করেছিলেন, তার কারণ এটাই।)

### Color আর Payment Card Number সরে গেছে `pydantic-extra-types`-এ { #color-and-payment-card-numbers-moved-to-pydantic-extra-types }

নিচের বিশেষ ব্যবহারের টাইপগুলো
[Pydantic Extra Types](https://github.com/pydantic/pydantic-extra-types) প্যাকেজে সরানো হয়েছে,
যা দরকার হলে আলাদাভাবে ইনস্টল করা যায়।

* [Color টাইপ](api/pydantic_extra_types_color.md)
* [পেমেন্ট কার্ড নম্বর](api/pydantic_extra_types_payment.md)

### `pydantic.networks`-এর Url আর Dsn টাইপ আর `str` থেকে উত্তরাধিকার পায় না { #url-and-dsn-types-in-pydanticnetworks-no-longer-inherit-from-str }

Pydantic V1-এ [`AnyUrl`][pydantic.networks.AnyUrl] টাইপ `str` থেকে উত্তরাধিকার পেত, আর অন্য সব
`Url` আর `Dsn` টাইপ এগুলো থেকে উত্তরাধিকার পেত। Pydantic V2-তে এই টাইপগুলো তৈরি হয়েছে দুটি নতুন `Url` আর `MultiHostUrl`
ক্লাসের ওপর, `Annotated` ব্যবহার করে।

`str` থেকে উত্তরাধিকার পাওয়ার সুবিধা-অসুবিধা দুটোই ছিল, আর V2-এর জন্য আমরা ঠিক করেছি এটি সরিয়ে ফেলাই ভালো। `str` আশা করে
এমন API-তে এই টাইপগুলো ব্যবহার করতে এখন আপনাকে এগুলো রূপান্তর করতে হবে (`str(url)` দিয়ে)।

Pydantic V2 URL যাচাইয়ে Rust-এর [Url](https://crates.io/crates/url) crate ব্যবহার করে।
কিছু URL যাচাই V1-এর আগের আচরণ থেকে সামান্য ভিন্ন।
একটি উল্লেখযোগ্য পার্থক্য হলো, কোনো path না থাকলে নতুন `Url` টাইপগুলো যাচাই করা সংস্করণের শেষে স্ল্যাশ যোগ করে,
এমনকি যদি `Url` টাইপের constructor-এর আর্গুমেন্টে স্ল্যাশ না দেওয়া থাকে। এই আচরণ দেখুন নিচের উদাহরণে:

```python
from pydantic import AnyUrl

assert str(AnyUrl(url='https://google.com')) == 'https://google.com/'
assert str(AnyUrl(url='https://google.com/')) == 'https://google.com/'
assert str(AnyUrl(url='https://google.com/api')) == 'https://google.com/api'
assert str(AnyUrl(url='https://google.com/api/')) == 'https://google.com/api/'
```

যদি তবুও শেষে স্ল্যাশ যোগ না করার পুরনো আচরণ চান, তাহলে এই [সমাধান](https://github.com/pydantic/pydantic/issues/7186#issuecomment-1690235887) দেখুন।

### শর্তযুক্ত (Constrained) টাইপ { #constrained-types }

`Constrained*` ক্লাসগুলো *সরিয়ে দেওয়া* হয়েছে, আর এগুলোর বদলে `Annotated[<type>, Field(...)]` ব্যবহার করা উচিত, যেমন:

```python
from pydantic import BaseModel, ConstrainedInt


class MyInt(ConstrainedInt):
    ge = 0


class Model(BaseModel):
    x: MyInt
```

...হয়ে যায়:

```python
from typing import Annotated

from pydantic import BaseModel, Field

MyInt = Annotated[int, Field(ge=0)]


class Model(BaseModel):
    x: MyInt
```

এ সম্পর্কে আরও পড়ুন [`Annotated` দিয়ে টাইপ গঠন](concepts/types.md#using-the-annotated-pattern)
ডকসে।

`ConstrainedStr`-এর বদলে [`StringConstraints`][pydantic.types.StringConstraints] ব্যবহার করতে পারেন।

### Mypy plugin { #mypy-plugins }

Pydantic V2-তে `pydantic.mypy`-তে একটি [mypy](https://mypy.readthedocs.io/en/stable/extending_mypy.html#configuring-mypy-to-use-plugins) plugin আছে।

[V1 ফিচার](migration.md#continue-using-pydantic-v1-features) ব্যবহার করলে
`pydantic.v1.mypy` plugin-ও চালু করতে হতে পারে।

mypy plugin কনফিগার করতে:

/// tab | `mypy.ini`

```ini
[mypy]
plugins = pydantic.mypy, pydantic.v1.mypy  # include `.v1.mypy` if required.
```

///

/// tab | `pyproject.toml`

```toml
[tool.mypy]
plugins = [
    "pydantic.mypy",
    "pydantic.v1.mypy",  # include `.v1.mypy` if required.
]
```

///

## অন্যান্য পরিবর্তন { #other-changes }

* [`email-validator<2.0.0`](https://github.com/JoshData/python-email-validator)-এর সমর্থন বাদ দেওয়া হয়েছে। `pip install -U email-validator`
  দিয়ে আপডেট করে নিন।

## Pydantic V2-তে সরানো জিনিস { #moved-in-pydantic-v2 }

| Pydantic V1 | Pydantic V2 |
| --- | --- |
| `pydantic.BaseSettings` | [`pydantic_settings.BaseSettings`](#basesettings-has-moved-to-pydantic-settings) |
| `pydantic.color` | [`pydantic_extra_types.color`][pydantic_extra_types.color] |
| `pydantic.types.PaymentCardBrand` | [`pydantic_extra_types.PaymentCardBrand`](#color-and-payment-card-numbers-moved-to-pydantic-extra-types) |
| `pydantic.types.PaymentCardNumber` | [`pydantic_extra_types.PaymentCardNumber`](#color-and-payment-card-numbers-moved-to-pydantic-extra-types) |
| `pydantic.utils.version_info` | [`pydantic.version.version_info`][pydantic.version.version_info] |
| `pydantic.error_wrappers.ValidationError` | [`pydantic.ValidationError`][pydantic_core.ValidationError] |
| `pydantic.utils.to_camel` | [`pydantic.alias_generators.to_pascal`][pydantic.alias_generators.to_pascal] |
| `pydantic.utils.to_lower_camel` | [`pydantic.alias_generators.to_camel`][pydantic.alias_generators.to_camel] |
| `pydantic.PyObject` | [`pydantic.ImportString`][pydantic.types.ImportString] |

## Pydantic V2-তে deprecated আর সরানো জিনিস { #deprecated-and-moved-in-pydantic-v2 }

এগুলো এখনো নতুন জায়গা থেকে ইমপোর্ট করে ব্যবহার করা যায়, কিন্তু deprecated; নতুন কোডে এড়িয়ে চলুন।

| Pydantic V1 | Pydantic V2 |
| --- | --- |
| `pydantic.tools.schema_of` | `pydantic.deprecated.tools.schema_of` |
| `pydantic.tools.parse_obj_as` | `pydantic.deprecated.tools.parse_obj_as` |
| `pydantic.tools.schema_json_of` | `pydantic.deprecated.tools.schema_json_of` |
| `pydantic.json.pydantic_encoder` | `pydantic.deprecated.json.pydantic_encoder` |
| `pydantic.validate_arguments` | `pydantic.deprecated.decorator.validate_arguments` |
| `pydantic.json.custom_pydantic_encoder` | `pydantic.deprecated.json.custom_pydantic_encoder` |
| `pydantic.json.ENCODERS_BY_TYPE` | `pydantic.deprecated.json.ENCODERS_BY_TYPE` |
| `pydantic.json.timedelta_isoformat` | `pydantic.deprecated.json.timedelta_isoformat` |
| `pydantic.decorator.validate_arguments` | `pydantic.deprecated.decorator.validate_arguments` |
| `pydantic.class_validators.validator` | `pydantic.deprecated.class_validators.validator` |
| `pydantic.class_validators.root_validator` | `pydantic.deprecated.class_validators.root_validator` |
| `pydantic.utils.deep_update` | `pydantic.v1.utils.deep_update` |
| `pydantic.utils.GetterDict` | `pydantic.v1.utils.GetterDict` |
| `pydantic.utils.lenient_issubclass` | `pydantic.v1.utils.lenient_issubclass` |
| `pydantic.utils.lenient_isinstance` | `pydantic.v1.utils.lenient_isinstance` |
| `pydantic.utils.is_valid_field` | `pydantic.v1.utils.is_valid_field` |
| `pydantic.utils.update_not_none` | `pydantic.v1.utils.update_not_none` |
| `pydantic.utils.import_string` | `pydantic.v1.utils.import_string` |
| `pydantic.utils.Representation` | `pydantic.v1.utils.Representation` |
| `pydantic.utils.ROOT_KEY` | `pydantic.v1.utils.ROOT_KEY` |
| `pydantic.utils.smart_deepcopy` | `pydantic.v1.utils.smart_deepcopy` |
| `pydantic.utils.sequence_like` | `pydantic.v1.utils.sequence_like` |

## Pydantic V2-তে বাদ পড়া জিনিস { #removed-in-pydantic-v2 }

নিচের জিনিসগুলো Pydantic V2-তে আর নেই। ("This was an alias to ..." মানে "এটি ছিল ...-এর আরেকটি নাম"; এখন সরাসরি সেই টাইপটিই লিখুন, যেমন `NoneStr`-এর বদলে `str | None`।)

* `pydantic.ConstrainedBytes`
* `pydantic.ConstrainedDate`
* `pydantic.ConstrainedDecimal`
* `pydantic.ConstrainedFloat`
* `pydantic.ConstrainedFrozenSet`
* `pydantic.ConstrainedInt`
* `pydantic.ConstrainedList`
* `pydantic.ConstrainedSet`
* `pydantic.ConstrainedStr`
* `pydantic.JsonWrapper`
* `pydantic.NoneBytes`
    * This was an alias to `None | bytes`.
* `pydantic.NoneStr`
    * This was an alias to `None | str`.
* `pydantic.NoneStrBytes`
    * This was an alias to `None | str | bytes`.
* `pydantic.Protocol`
* `pydantic.Required`
* `pydantic.StrBytes`
    * This was an alias to `str | bytes`.
* `pydantic.compiled`
* `pydantic.config.get_config`
* `pydantic.config.inherit_config`
* `pydantic.config.prepare_config`
* `pydantic.create_model_from_namedtuple`
* `pydantic.create_model_from_typeddict`
* `pydantic.dataclasses.create_pydantic_model_from_dataclass`
* `pydantic.dataclasses.make_dataclass_validator`
* `pydantic.dataclasses.set_validation`
* `pydantic.datetime_parse.parse_date`
* `pydantic.datetime_parse.parse_time`
* `pydantic.datetime_parse.parse_datetime`
* `pydantic.datetime_parse.parse_duration`
* `pydantic.error_wrappers.ErrorWrapper`
* `pydantic.errors.AnyStrMaxLengthError`
* `pydantic.errors.AnyStrMinLengthError`
* `pydantic.errors.ArbitraryTypeError`
* `pydantic.errors.BoolError`
* `pydantic.errors.BytesError`
* `pydantic.errors.CallableError`
* `pydantic.errors.ClassError`
* `pydantic.errors.ColorError`
* `pydantic.errors.ConfigError`
* `pydantic.errors.DataclassTypeError`
* `pydantic.errors.DateError`
* `pydantic.errors.DateNotInTheFutureError`
* `pydantic.errors.DateNotInThePastError`
* `pydantic.errors.DateTimeError`
* `pydantic.errors.DecimalError`
* `pydantic.errors.DecimalIsNotFiniteError`
* `pydantic.errors.DecimalMaxDigitsError`
* `pydantic.errors.DecimalMaxPlacesError`
* `pydantic.errors.DecimalWholeDigitsError`
* `pydantic.errors.DictError`
* `pydantic.errors.DurationError`
* `pydantic.errors.EmailError`
* `pydantic.errors.EnumError`
* `pydantic.errors.EnumMemberError`
* `pydantic.errors.ExtraError`
* `pydantic.errors.FloatError`
* `pydantic.errors.FrozenSetError`
* `pydantic.errors.FrozenSetMaxLengthError`
* `pydantic.errors.FrozenSetMinLengthError`
* `pydantic.errors.HashableError`
* `pydantic.errors.IPv4AddressError`
* `pydantic.errors.IPv4InterfaceError`
* `pydantic.errors.IPv4NetworkError`
* `pydantic.errors.IPv6AddressError`
* `pydantic.errors.IPv6InterfaceError`
* `pydantic.errors.IPv6NetworkError`
* `pydantic.errors.IPvAnyAddressError`
* `pydantic.errors.IPvAnyInterfaceError`
* `pydantic.errors.IPvAnyNetworkError`
* `pydantic.errors.IntEnumError`
* `pydantic.errors.IntegerError`
* `pydantic.errors.InvalidByteSize`
* `pydantic.errors.InvalidByteSizeUnit`
* `pydantic.errors.InvalidDiscriminator`
* `pydantic.errors.InvalidLengthForBrand`
* `pydantic.errors.JsonError`
* `pydantic.errors.JsonTypeError`
* `pydantic.errors.ListError`
* `pydantic.errors.ListMaxLengthError`
* `pydantic.errors.ListMinLengthError`
* `pydantic.errors.ListUniqueItemsError`
* `pydantic.errors.LuhnValidationError`
* `pydantic.errors.MissingDiscriminator`
* `pydantic.errors.MissingError`
* `pydantic.errors.NoneIsAllowedError`
* `pydantic.errors.NoneIsNotAllowedError`
* `pydantic.errors.NotDigitError`
* `pydantic.errors.NotNoneError`
* `pydantic.errors.NumberNotGeError`
* `pydantic.errors.NumberNotGtError`
* `pydantic.errors.NumberNotLeError`
* `pydantic.errors.NumberNotLtError`
* `pydantic.errors.NumberNotMultipleError`
* `pydantic.errors.PathError`
* `pydantic.errors.PathNotADirectoryError`
* `pydantic.errors.PathNotAFileError`
* `pydantic.errors.PathNotExistsError`
* `pydantic.errors.PatternError`
* `pydantic.errors.PyObjectError`
* `pydantic.errors.PydanticTypeError`
* `pydantic.errors.PydanticValueError`
* `pydantic.errors.SequenceError`
* `pydantic.errors.SetError`
* `pydantic.errors.SetMaxLengthError`
* `pydantic.errors.SetMinLengthError`
* `pydantic.errors.StrError`
* `pydantic.errors.StrRegexError`
* `pydantic.errors.StrictBoolError`
* `pydantic.errors.SubclassError`
* `pydantic.errors.TimeError`
* `pydantic.errors.TupleError`
* `pydantic.errors.TupleLengthError`
* `pydantic.errors.UUIDError`
* `pydantic.errors.UUIDVersionError`
* `pydantic.errors.UrlError`
* `pydantic.errors.UrlExtraError`
* `pydantic.errors.UrlHostError`
* `pydantic.errors.UrlHostTldError`
* `pydantic.errors.UrlPortError`
* `pydantic.errors.UrlSchemeError`
* `pydantic.errors.UrlSchemePermittedError`
* `pydantic.errors.UrlUserInfoError`
* `pydantic.errors.WrongConstantError`
* `pydantic.main.validate_model`
* `pydantic.networks.stricturl`
* `pydantic.parse_file_as`
* `pydantic.parse_raw_as`
* `pydantic.stricturl`
* `pydantic.tools.parse_file_as`
* `pydantic.tools.parse_raw_as`
* `pydantic.types.JsonWrapper`
* `pydantic.types.NoneBytes`
* `pydantic.types.NoneStr`
* `pydantic.types.NoneStrBytes`
* `pydantic.types.PyObject`
* `pydantic.types.StrBytes`
* `pydantic.typing.evaluate_forwardref`
* `pydantic.typing.AbstractSetIntStr`
* `pydantic.typing.AnyCallable`
* `pydantic.typing.AnyClassMethod`
* `pydantic.typing.CallableGenerator`
* `pydantic.typing.DictAny`
* `pydantic.typing.DictIntStrAny`
* `pydantic.typing.DictStrAny`
* `pydantic.typing.IntStr`
* `pydantic.typing.ListStr`
* `pydantic.typing.MappingIntStrAny`
* `pydantic.typing.NoArgAnyCallable`
* `pydantic.typing.NoneType`
* `pydantic.typing.ReprArgs`
* `pydantic.typing.SetStr`
* `pydantic.typing.StrPath`
* `pydantic.typing.TupleGenerator`
* `pydantic.typing.WithArgsTypes`
* `pydantic.typing.all_literal_values`
* `pydantic.typing.display_as_type`
* `pydantic.typing.get_all_type_hints`
* `pydantic.typing.get_args`
* `pydantic.typing.get_origin`
* `pydantic.typing.get_sub_types`
* `pydantic.typing.is_callable_type`
* `pydantic.typing.is_classvar`
* `pydantic.typing.is_finalvar`
* `pydantic.typing.is_literal_type`
* `pydantic.typing.is_namedtuple`
* `pydantic.typing.is_new_type`
* `pydantic.typing.is_none_type`
* `pydantic.typing.is_typeddict`
* `pydantic.typing.is_typeddict_special`
* `pydantic.typing.is_union`
* `pydantic.typing.new_type_supertype`
* `pydantic.typing.resolve_annotations`
* `pydantic.typing.typing_base`
* `pydantic.typing.update_field_forward_refs`
* `pydantic.typing.update_model_forward_refs`
* `pydantic.utils.ClassAttribute`
* `pydantic.utils.DUNDER_ATTRIBUTES`
* `pydantic.utils.PyObjectStr`
* `pydantic.utils.ValueItems`
* `pydantic.utils.almost_equal_floats`
* `pydantic.utils.get_discriminator_alias_and_values`
* `pydantic.utils.get_model`
* `pydantic.utils.get_unique_discriminator_alias`
* `pydantic.utils.in_ipython`
* `pydantic.utils.is_valid_identifier`
* `pydantic.utils.path_type`
* `pydantic.utils.validate_field_name`
* `pydantic.validate_model`

/// check | সংক্ষেপে মনে রাখুন

* আগে `bump-pydantic` চালান, তারপর টেস্ট চালিয়ে বাকিটা এই পেজ দেখে ঠিক করুন।
* মেথডের নাম: `dict()` → `model_dump()`, `json()` → `model_dump_json()`, `parse_obj()` → `model_validate()`।
* config: `class Config` → `model_config = ConfigDict(...)`, `orm_mode` → `from_attributes`।
* validator: `@validator` → `@field_validator`, `@root_validator` → `@model_validator`।
* `Optional[str]` এখন বাধ্যতামূলক; ঐচ্ছিক করতে `= None` লিখুন।
* `BaseSettings` এখন `pydantic-settings` প্যাকেজে।

///
