# Dataclasses { #dataclasses }

/// note | এই পেজে যা শিখবেন

* Pydantic dataclass কী, আর সাধারণ Python dataclass-এর সাথে পার্থক্য।
* `BaseModel`-এর সাথে মিল-অমিল, আর কখন কোনটি বেছে নেবেন।
* config দেওয়া, stdlib dataclass-এর সাথে মেশানো, নিজের টাইপ ব্যবহার।
* validator আর `__post_init__()` কোন ক্রমে চলে।

///

/// details | API ডকুমেন্টেশন
    type: info

[`@pydantic.dataclasses.dataclass`][pydantic.dataclasses.dataclass]<br>

///

আপনি যদি Pydantic-এর [`BaseModel`][pydantic.BaseModel] ব্যবহার করতে না চান, তাহলে সাধারণ
[dataclasses][dataclasses]-এর ওপরেই একই ডেটা যাচাই পেতে পারেন।

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

শুধু `from dataclasses import dataclass`-এর বদলে `from pydantic.dataclasses import dataclass` লেখা হয়েছে। ফলে `id='42'` স্ট্রিং থেকে `42` সংখ্যা হয়ে গেল, আর `signup_ts`-এর লেখা তারিখ `datetime` অবজেক্ট হলো। সাধারণ dataclass হলে কোনো রূপান্তর বা যাচাই হতো না, যা দিতেন তা-ই থাকত।

///

/// note | মনে রাখুন

Pydantic dataclass [Pydantic মডেলের](../concepts/models.md) বিকল্প **নয়**।
এগুলো stdlib dataclass-এর মতোই সুবিধা দেয়, সাথে Pydantic-এর যাচাই।

কিছু ক্ষেত্রে Pydantic মডেল ব্যবহার করাই ভালো।

আরও তথ্য আর আলোচনার জন্য দেখুন
[pydantic/pydantic#710](https://github.com/pydantic/pydantic/issues/710)।

///

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ dataclass হলো একটি খালি ফর্ম: যে যা লেখে, তা-ই থাকে। Pydantic dataclass হলো সেই একই ফর্ম, কিন্তু জমা দেওয়ার সময় একজন কর্মী মিলিয়ে দেখেন সব ঘর ঠিকভাবে পূরণ হয়েছে কিনা, আর দরকারে ঠিক রূপে বদলে দেন। `BaseModel` হলো পুরো একটি অফিস: যাচাই ছাড়াও `model_dump()`, `model_json_schema()`-এর মতো অনেক বাড়তি সেবা।

///

Pydantic dataclass আর মডেলের মধ্যে মিল, দুটোতেই আছে:

* [কনফিগারেশন](#dataclass-config) সমর্থন (তবে মনে রাখুন, Pydantic মডেলের মতো dataclass-এ `model_config` অ্যাট্রিবিউট চলে না)
* [নেস্টেড](./models.md#nested-models) ক্লাস
* dataclass তৈরিতে দেওয়া আর্গুমেন্টগুলো [কপি](./models.md#attribute-copies) হয়।

Pydantic dataclass আর মডেলের কিছু পার্থক্য:

* যাচাই, dump আর JSON Schema তৈরির [বিভিন্ন মেথড](./models.md#model-methods-and-properties) পাওয়া যায় না। বদলে,
  dataclass-টিকে একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] দিয়ে মুড়ে তার মেথডগুলো ব্যবহার করতে পারেন:

    ⟦CODE2⟧

* validator (দেখুন [আলাদা অংশ](#validators-and-initialization-hooks))।
* [`extra`][pydantic.ConfigDict.extra] কনফিগারেশনের আচরণ:
    * বাড়তি ডেটা [সিরিয়ালাইজেশনে](./serialization.md#serializing-data) থাকে না।
    * [`__pydantic_extra__` অ্যাট্রিবিউট দিয়ে](./models.md#extra-data) বাড়তি মানের যাচাই নিজের মতো করার কোনো উপায় নেই।
* generic dataclass সমর্থিত, কিন্তু standard library-র অন্য generic টাইপের মতোই, প্যারামিটারসহ dataclass প্রত্যাশামতো কাজ করবে না:

    /// tab | Python 3.10 ও তার ওপরে

    ⟦CODE3⟧

    1. [generic Pydantic মডেলের](./models.md#generic-models) মতো নয়, `Foo[int]` একটি [generic alias][types-genericalias], আসল টাইপ অবজেক্ট নয়।
       তাই Pydantic এখন `Foo[int]`-কে `Foo[Any]`-এর মতোই ধরে,
       `f`-এর কোনো যাচাই করে না।

    ///

    /// tab | Python 3.12 ও তার ওপরে (নতুন সিনট্যাক্স)

    ⟦CODE4⟧

    1. [generic Pydantic মডেলের](./models.md#generic-models) মতো নয়, `Foo[int]` একটি [generic alias][types-genericalias], আসল টাইপ অবজেক্ট নয়।
       তাই Pydantic এখন কোনো যাচাই করে না।

    ///

    বদলে, প্যারামিটারসহ `Foo[int]` ক্লাসটিকে একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] দিয়ে মুড়ে নিতে পারেন।

| | Pydantic dataclass | `BaseModel` |
| --- | --- | --- |
| যাচাই | আছে | আছে |
| `model_dump()`, `model_validate()`, `model_json_schema()` | নেই (`TypeAdapter` লাগে) | আছে |
| কনফিগারেশন | `config=` বা `__pydantic_config__` | `model_config` |
| `dataclasses.asdict()`, `fields()` এর মতো stdlib টুল | চলে | চলে না |
| কখন বেছে নেবেন | আগে থেকে dataclass ব্যবহার করা কোডে যাচাই যোগ করতে | নতুন কোডে, বিশেষ করে API/JSON নিয়ে কাজে |

Pydantic-এর [`Field()`][pydantic.Field] আর stdlib-এর [`field()`][dataclasses.field] দুটো ফাংশনই ব্যবহার করা যায়:

⟦CODE5⟧

/// info | কোডটি সহজ ভাষায়

* `friends`: stdlib-এর `dataclasses.field(default_factory=...)` দিয়ে প্রতিবার নতুন তালিকা।
* `age`: stdlib-এর `field()`-এর `metadata` দিয়ে শিরোনাম আর বর্ণনা।
* `height`: Pydantic-এর `Field()` দিয়ে `ge=50, le=300` সীমা; `'250'` স্ট্রিং যাচাই হয়ে `250` হলো।

///

Pydantic-এর [`@dataclass`][pydantic.dataclasses.dataclass] decorator সাধারণ decorator-এর সব আর্গুমেন্টই নেয়,
সাথে বাড়তি একটি `config` প্যারামিটার।

## Dataclass কনফিগারেশন { #dataclass-config }

[`BaseModel`][pydantic.BaseModel]-এর মতো কনফিগারেশন বদলাতে চাইলে দুটি উপায় আছে:

* decorator-এর `config` প্যারামিটার ব্যবহার।
* `__pydantic_config__` অ্যাট্রিবিউট দিয়ে কনফিগারেশন সংজ্ঞায়িত করা।

⟦CODE6⟧

1. `validate_assignment` নিয়ে আরও পড়ুন [API রেফারেন্সে][pydantic.config.ConfigDict.validate_assignment]।

## Dataclass schema আবার তৈরি { #rebuilding-dataclass-schema }

dataclass-এর core schema আবার তৈরি করতে [`rebuild_dataclass()`][pydantic.dataclasses.rebuild_dataclass] ফাংশন ব্যবহার করা যায়।
বিস্তারিত জানতে [মডেল schema আবার তৈরি](./models.md#rebuilding-model-schema) অংশ দেখুন।

## Stdlib dataclass আর Pydantic dataclass { #stdlib-dataclasses-and-pydantic-dataclasses }

### stdlib dataclass থেকে উত্তরাধিকার { #inherit-from-stdlib-dataclasses }

stdlib dataclass (নেস্টেড হোক বা না হোক) থেকেও উত্তরাধিকার নেওয়া যায়, আর Pydantic স্বয়ংক্রিয়ভাবে
উত্তরাধিকারে পাওয়া সব ফিল্ড যাচাই করবে।

⟦CODE7⟧

/// info | কোডটি সহজ ভাষায়

`Z` আর `Y` সাধারণ dataclass, শুধু `X` Pydantic dataclass। তবু `X` তৈরির সময় `z`, `y`, `x` তিনটিই যাচাই আর রূপান্তর হলো (`b'1'` → `1`, `'2'` → `2`)। আর `z='pika'` সংখ্যা নয় বলে এরর এল।

///

Pydantic dataclass যেহেতু মডেলের মতোই ইনপুট যাচাই করে, পর্যবেক্ষণের সুবিধাও একই: যদি
[Logfire](../integrations/logfire.md) ব্যবহার করেন, Pydantic dataclass-এর যাচাইও
[মডেলের যাচাইয়ের পাশাপাশি রেকর্ড হয়](../errors/troubleshooting.md), গোছানো এররে প্রত্যাখ্যাত মানসহ।

decorator সরাসরি একটি stdlib dataclass-এর ওপরেও প্রয়োগ করা যায়; সেক্ষেত্রে একটি নতুন subclass তৈরি হবে:

⟦CODE8⟧

### `BaseModel`-এর সাথে stdlib dataclass ব্যবহার { #usage-of-stdlib-dataclasses-with-basemodel }

একটি standard library dataclass যখন Pydantic মডেল, Pydantic dataclass বা [`TypeAdapter`][pydantic.TypeAdapter]-এর ভেতরে ব্যবহার হয়,
তখন যাচাই প্রয়োগ হয় (আর [কনফিগারেশন](#dataclass-config) একই থাকে)। অর্থাৎ ফিল্ডের annotation হিসেবে stdlib বা Pydantic
dataclass ব্যবহার করা কার্যত একই।

⟦CODE9⟧

/// info | কোডটি সহজ ভাষায়

* `User(name=['not', 'a', 'string'])` সরাসরি তৈরিতে কোনো যাচাই হয় না, কারণ এটি সাধারণ dataclass।
* কিন্তু `Foo(user=user)`-এ ঢোকানোমাত্র Pydantic ভেতরের `name` যাচাই করে এরর দেয়। `revalidate_instances='always'` না দিলে ইতিমধ্যে তৈরি instance আবার যাচাই হতো না।
* `frozen=True` থাকায় পরে `name` বদলানো যায় না; এটি stdlib-এর নিজের আচরণ, Pydantic বদলায় না।

///

### নিজের টাইপ ব্যবহার { #using-custom-types }

ওপরে যেমন বলা হলো, standard library dataclass-এও যাচাই প্রয়োগ হয়। নিজের বানানো
টাইপ ব্যবহার করলে, dataclass-টি উল্লেখ করার সময় এরর পাবেন। সমস্যা এড়াতে
dataclass-এ (বা যে মডেলে এটি আছে সেখানে) [`arbitrary_types_allowed`][pydantic.ConfigDict.arbitrary_types_allowed]
কনফিগারেশন সেট করতে পারেন:

⟦CODE10⟧

/// tip | উদাহরণ দিয়ে বুঝি

`ArbitraryType` এমন একটি জিনিস যা Pydantic চেনে না, যেমন কাস্টমসে অচেনা একটি যন্ত্র। `arbitrary_types_allowed=True` মানে "চিনতে না পারলেও চলবে, শুধু দেখো এটি আসলেই ওই ক্লাসের instance কিনা"। তখন Pydantic শুধু `isinstance()` পরীক্ষা করে।

///

### dataclass-টি Pydantic dataclass কিনা পরীক্ষা { #checking-if-a-dataclass-is-a-pydantic-dataclass }

Pydantic dataclass-কেও dataclass হিসেবেই ধরা হয়, তাই [`dataclasses.is_dataclass()`][dataclasses.is_dataclass]
`True` ফেরত দেবে। একটি টাইপ বিশেষভাবে Pydantic dataclass কিনা পরীক্ষা করতে
[`is_pydantic_dataclass()`][pydantic.dataclasses.is_pydantic_dataclass] ফাংশন ব্যবহার করুন।

⟦CODE11⟧

## Validator আর initialization hook { #validators-and-initialization-hooks }

Pydantic dataclass-এও validator কাজ করে:

⟦CODE12⟧

<!-- markdownlint-disable-next-line strong-style -->
dataclass-এর [`__post_init__()`][dataclasses.__post_init__] মেথডও সমর্থিত, আর এটি
*before* আর *after* মডেল validator-এর ডাকের মাঝখানে ডাকা হয়।

/// details | উদাহরণ
    type: tip

⟦CODE13⟧

1. Pydantic মডেলের মতো নয়, এখানে `values` প্যারামিটারের টাইপ [`ArgsKwargs`][pydantic_core.ArgsKwargs]

///

/// info | চলার ক্রম

1. `mode='before'` মডেল validator (কাঁচা আর্গুমেন্ট, `ArgsKwargs` হিসেবে)
2. ফিল্ডের যাচাই
3. `__post_init__()`
4. `mode='after'` মডেল validator

///

/// check | সংক্ষেপে মনে রাখুন

* `from pydantic.dataclasses import dataclass` লিখলেই সাধারণ dataclass-এ যাচাই যোগ হয়।
* `model_dump()`-এর মতো মেথড নেই; দরকারে `TypeAdapter(MyDataclass)`।
* কনফিগারেশন: `@dataclass(config=ConfigDict(...))` বা `__pydantic_config__`।
* stdlib dataclass মডেলের ভেতরে ব্যবহার করলেও যাচাই হয়।
* ক্রম: before validator → ফিল্ড যাচাই → `__post_init__` → after validator।

///
