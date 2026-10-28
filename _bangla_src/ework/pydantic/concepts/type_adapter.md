# Type Adapter { #type-adapter }

/// note | এই পেজে যা শিখবেন

* `TypeAdapter` কী, আর `BaseModel` ছাড়া যেকোনো টাইপ (যেমন `list[Item]`, `TypedDict`, `int`) কীভাবে যাচাই করবেন।
* এর প্রধান মেথড: যাচাই, dump আর JSON Schema।
* কেন `dump_json` `bytes` ফেরত দেয়।
* পারফরম্যান্সের জন্য একবার বানিয়ে বারবার ব্যবহার, আর পরে schema তৈরি (`defer_build`, `rebuild()`)।

///

এমন টাইপ থাকতে পারে যা `BaseModel` নয়, কিন্তু সেগুলোর বিপরীতে আপনি ডেটা যাচাই করতে চান।
অথবা একটি `list[SomeModel]` যাচাই করতে চান, বা সেটিকে JSON-এ dump করতে চান।

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.type_adapter.TypeAdapter`][pydantic.type_adapter.TypeAdapter]<br>

///

এমন ক্ষেত্রের জন্য Pydantic দেয় [`TypeAdapter`][pydantic.type_adapter.TypeAdapter],
যা দিয়ে কোনো [`BaseModel`][pydantic.main.BaseModel] তৈরি না করেই টাইপ যাচাই, সিরিয়ালাইজেশন আর JSON schema তৈরি করা যায়।

/// tip | উদাহরণ দিয়ে বুঝি

`TypeAdapter` হলো বিদ্যুতের অ্যাডাপ্টার (প্লাগ কনভার্টার)। আপনার যন্ত্রটি (টাইপ) সরাসরি Pydantic-এর সকেটে ঢোকে না, কারণ এটি `BaseModel` নয়। অ্যাডাপ্টার লাগিয়ে দিলে একই বিদ্যুৎ (যাচাই, dump, schema) পাওয়া যায়, যন্ত্র না বদলেই।

///

যেসব টাইপে [`BaseModel`][pydantic.main.BaseModel]-এর instance মেথডগুলো নেই (যেমন dataclass, সাধারণ টাইপ, আরও অনেক),
তাদের জন্য একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] instance সেই সুবিধাগুলোর কিছু দেয়:

⟦CODE1⟧

| `TypeAdapter` মেথড | `BaseModel`-এ যার সমান | কী করে |
| --- | --- | --- |
| `validate_python(obj)` | `Model.model_validate(obj)` | Python অবজেক্ট যাচাই |
| `validate_json(data)` | `Model.model_validate_json(data)` | JSON স্ট্রিং/bytes সরাসরি যাচাই |
| `validate_strings(obj)` | `Model.model_validate_strings(obj)` | সব মান স্ট্রিং হিসেবে এলে যাচাই |
| `dump_python(obj)` | `m.model_dump()` | সাধারণ Python রূপে আনা |
| `dump_json(obj)` | `m.model_dump_json()` | JSON-এ রূপান্তর (`bytes` ফেরত দেয়) |
| `json_schema()` | `Model.model_json_schema()` | JSON Schema তৈরি |
| `rebuild()` | `Model.model_rebuild()` | schema আবার তৈরি |

/// info | `dump_json` ফেরত দেয় `bytes`

`TypeAdapter`-এর `dump_json` মেথড একটি `bytes` অবজেক্ট ফেরত দেয়, অথচ `BaseModel`-এর সমতুল্য মেথড `model_dump_json` ফেরত দেয় `str`।
এই অমিলের কারণ হলো V1-এ মডেল dump করলে str টাইপ ফেরত আসত, তাই পুরনো কোডের সাথে মিল রাখতে V2-তেও এই আচরণ রাখা হয়েছে।
`BaseModel`-এর ক্ষেত্রে `bytes`-কে `str`-এ রূপান্তর করা হয়, কিন্তু প্রায়ই শেষ পর্যন্ত `bytes`-ই দরকার হয়।
তাই V2-এর নতুন `TypeAdapter` ক্লাসে ফেরত টাইপ সরাসরি `bytes`, যা দরকারে সহজেই `str`-এ রূপান্তর করা যায় (`.decode()`)।

///

/// note | মনে রাখুন

[`RootModel`][pydantic.root_model.RootModel]-এর সাথে ব্যবহারের ক্ষেত্রে কিছুটা মিল থাকলেও,
`BaseModel` ইত্যাদির ফিল্ড নির্ধারণে [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-কে
টাইপ annotation হিসেবে ব্যবহার করা উচিত নয়।

///

## নির্দিষ্ট টাইপে ডেটা পার্স করা { #parsing-data-into-a-specified-type }

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] দিয়ে আরও তাৎক্ষণিকভাবে (ad-hoc) পার্সিংয়ের নিয়ম প্রয়োগ করে Pydantic মডেল
পূরণ করা যায়। এটি [`BaseModel.model_validate`][pydantic.main.BaseModel.model_validate]-এর মতোই আচরণ করে,
কিন্তু Pydantic-সমর্থিত যেকোনো টাইপের সাথে কাজ করে।

এটি বিশেষভাবে কাজে লাগে যখন ফলাফল এমন একটি টাইপে পার্স করতে চান যা সরাসরি
[`BaseModel`][pydantic.main.BaseModel]-এর subclass নয়। যেমন:

⟦CODE2⟧

/// info | কোডটি সহজ ভাষায়

API থেকে আসা ডেটা একটি তালিকা, প্রতিটি উপাদান একটি `Item`। `list[Item]` নিজে কোনো মডেল নয়, তাই `TypeAdapter(list[Item])` দিয়ে পুরো তালিকা একবারে যাচাই করা হলো, আর প্রতিটি ডিকশনারি `Item` অবজেক্ট হয়ে গেল।

///

[`BaseModel`][pydantic.main.BaseModel]-এর ফিল্ড হিসেবে Pydantic যে টাইপগুলো সামলাতে পারে, [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]
তার যেকোনোটিতে ডেটা পার্স করতে পারে।

এভাবে পার্স করা ডেটা প্রায়ই এমন উৎস থেকে আসে যা আপনার নিয়ন্ত্রণে নেই, যেমন ওপরের উদাহরণের API কল,
তাই কোড চালু হওয়ার অনেক পরেও যাচাই ব্যর্থ হতে পারে। `TypeAdapter` মডেলের মতোই গোছানো এরর তোলে,
তাই প্রোডাকশনে যাচাই ব্যর্থতা রেকর্ড করে এমন টুল, যেমন
[Logfire](../integrations/logfire.md), এগুলোও ধরে রাখে।

/// info | পারফরম্যান্স নিয়ে ভাবনা

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর instance তৈরির সময়, দেওয়া টাইপটি বিশ্লেষণ করে pydantic-core
schema-তে রূপান্তর করতে হয়। এতে উল্লেখযোগ্য খরচ আছে, তাই একটি টাইপের জন্য `TypeAdapter`
একবারই তৈরি করে লুপ বা পারফরম্যান্স-গুরুত্বপূর্ণ কোডে বারবার ব্যবহার করার পরামর্শ দেওয়া হয়।

///

```python
from pydantic import TypeAdapter

IntList = TypeAdapter(list[int])  # মডিউলের শুরুতে একবার


def handle(rows):
    for row in rows:
        IntList.validate_python(row)  # ✅ লুপে শুধু ব্যবহার
        # TypeAdapter(list[int]).validate_python(row)  ❌ প্রতিবার নতুন বানানো ধীর
```

## একটি `TypeAdapter`-এর schema আবার তৈরি { #rebuilding-a-typeadapters-schema }

/// info | v2.10-এ যোগ হয়েছে
///

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] পরে schema তৈরি (deferred) আর হাতে rebuild সমর্থন করে। এটি কাজে লাগে:

* forward reference থাকা টাইপের ক্ষেত্রে
* যে টাইপের core schema তৈরি ব্যয়বহুল

একটি টাইপ দিয়ে [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] তৈরি করলে, Pydantic টাইপটি বিশ্লেষণ করে এর জন্য একটি core schema বানায়।
এই core schema-তে সেই টাইপের ডেটা যাচাই আর সিরিয়ালাইজ করার দরকারি তথ্য থাকে।
core schema নিয়ে আরও জানতে দেখুন [architecture ডকুমেন্টেশন](../internals/architecture.md)।

`TypeAdapter` তৈরির সময় [`defer_build`][pydantic.config.ConfigDict.defer_build] `True` করলে,
Pydantic core schema তৈরি পিছিয়ে দেবে প্রথমবার দরকার হওয়া পর্যন্ত (যাচাই বা সিরিয়ালাইজেশনের জন্য)।

হাতে core schema তৈরি শুরু করতে, [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] instance-এর
[`rebuild`][pydantic.type_adapter.TypeAdapter.rebuild] মেথড ডাকতে পারেন:

⟦CODE3⟧

/// info | কোডটি সহজ ভাষায়

`'MyInt'` নামটি adapter তৈরির সময় ছিল না, তাই `defer_build=True` দিয়ে schema বানানো পিছিয়ে রাখা হলো। পরে `MyInt = int` সংজ্ঞায়িত হলে `ta.rebuild()` নামটি খুঁজে schema তৈরি করল।

///

/// check | সংক্ষেপে মনে রাখুন

* `BaseModel` নয় এমন যেকোনো টাইপের জন্য: `TypeAdapter(টাইপ)`।
* `validate_python()`, `validate_json()`, `dump_python()`, `dump_json()` (→ `bytes`), `json_schema()`।
* একবার বানিয়ে বারবার ব্যবহার করুন; মডেলের ফিল্ডের টাইপ হিসেবে `TypeAdapter` লিখবেন না।
* forward reference থাকলে `defer_build=True` আর পরে `rebuild()`।

///
