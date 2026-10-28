# Architecture { #architecture }

/// note | এই পেজে যা শিখবেন

* Pydantic-এর দুই অংশ: Python-এ লেখা `pydantic` আর Rust-এ লেখা `pydantic-core`, আর তারা কীভাবে একসাথে কাজ করে।
* "core schema" কী: দুই অংশের মধ্যে কথা বলার ভাষা।
* মডেল সংজ্ঞায়িত করা থেকে শুরু করে যাচাই, সিরিয়ালাইজেশন আর JSON Schema তৈরি পর্যন্ত পুরো পথ।

///

/// note | মনে রাখুন

এই অংশটি *ভেতরের কাঠামো* (internals) ডকুমেন্টেশনের অংশ, আর আংশিকভাবে অবদানকারীদের (contributors) জন্য লেখা। সাধারণ ব্যবহারের জন্য এটি জানা জরুরি নয়, তবে Pydantic কেন এত দ্রুত আর কিছু এরর কেন আসে তা বুঝতে সাহায্য করে।

///

Pydantic V2 থেকে কোডের একটি অংশ Rust-এ লেখা, `pydantic-core` নামের একটি আলাদা প্যাকেজে।
এটি করা হয়েছে আংশিকভাবে যাচাই আর সিরিয়ালাইজেশনের পারফরম্যান্স বাড়াতে (এর বিনিময়ে ভেতরের যুক্তি
নিজের মতো করা আর বাড়ানোর সুযোগ কিছুটা সীমিত হয়েছে)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি রেস্টুরেন্ট ভাবুন। `pydantic` হলো ওয়েটার: গ্রাহকের (আপনার) সাথে আপনার ভাষায় (Python) কথা বলে, অর্ডার (মডেলের সংজ্ঞা) বুঝে নেয়, আর রান্নাঘরের জন্য একটি নির্দিষ্ট ফরম্যাটে অর্ডার স্লিপ লেখে, সেটিই **core schema**। `pydantic-core` হলো রান্নাঘর: খুব দ্রুত কাজ করে (Rust), কিন্তু শুধু ঠিক ফরম্যাটের স্লিপই বোঝে। প্রতিবার খাবার (যাচাই) রান্নাঘরেই হয়, ওয়েটার শুধু একবার স্লিপ লেখে।

///

এই architecture ডকুমেন্টেশন প্রথমে দেখাবে `pydantic` আর `pydantic-core` এই দুটি প্যাকেজ কীভাবে একসাথে
কাজ করে, তারপর বিভিন্ন পদ্ধতির (মডেল সংজ্ঞা, যাচাই, সিরিয়ালাইজেশন, JSON Schema) architecture-এর খুঁটিনাটি দেখাবে।

Pydantic লাইব্রেরির ব্যবহার দুই ভাগে ভাগ করা যায়:

* মডেল সংজ্ঞা, যা হয় `pydantic` প্যাকেজে।
* মডেলের যাচাই আর সিরিয়ালাইজেশন, যা হয় `pydantic-core` প্যাকেজে।

```
আপনার কোড: class Model(BaseModel): foo: bool
        │
        ▼  (ক্লাস সংজ্ঞায়িত হওয়ার সময়, একবার)
pydantic (Python): annotation, config, validator সংগ্রহ → GenerateSchema → core schema
        │
        ▼
pydantic-core (Rust): SchemaValidator + SchemaSerializer তৈরি
        │
        ▼  (প্রতিবার Model(...), model_dump() ডাকলে)
দ্রুত যাচাই আর সিরিয়ালাইজেশন
```

## মডেল সংজ্ঞা { #model-definition }

যখনই একটি Pydantic [`BaseModel`][pydantic.main.BaseModel] সংজ্ঞায়িত হয়, metaclass
মডেলের ভেতরের অংশ বিশ্লেষণ করে কয়েকটি উপাদান সংগ্রহ করে:

* মডেলের ফিল্ড তৈরির জন্য সংজ্ঞায়িত annotation ([`model_fields`][pydantic.main.BaseModel.model_fields] অ্যাট্রিবিউটে সংগৃহীত)।
* মডেলের কনফিগারেশন, যা [`model_config`][pydantic.main.BaseModel.model_config] দিয়ে সেট করা।
* বাড়তি validator/serializer।
* private অ্যাট্রিবিউট, class variable, generic প্যারামিটার শনাক্ত করা ইত্যাদি।

### `pydantic` আর `pydantic-core`-এর মধ্যে যোগাযোগ: core schema { #communicating-between-pydantic-and-pydantic-core-the-core-schema }

এরপর মডেল সংজ্ঞা থেকে সংগৃহীত তথ্য `pydantic-core`-এ পৌঁছানোর একটি উপায় দরকার,
যাতে সেই অনুযায়ী যাচাই আর সিরিয়ালাইজেশন হয়। এজন্য Pydantic core schema ধারণা
ব্যবহার করে: একটি গোছানো (আর সিরিয়ালাইজযোগ্য) Python ডিকশনারি ([`TypedDict`][typing.TypedDict] সংজ্ঞা দিয়ে
প্রকাশিত), যা একটি নির্দিষ্ট যাচাই আর সিরিয়ালাইজেশনের যুক্তি বর্ণনা করে। `pydantic` আর `pydantic-core`
প্যাকেজের মধ্যে যোগাযোগের মূল ডেটা কাঠামো এটিই। প্রতিটি core schema-তে একটি বাধ্যতামূলক `type` key থাকে, আর এই `type` অনুযায়ী বাড়তি property।

core schema তৈরি একটিমাত্র জায়গায় সামলানো হয়, `GenerateSchema` ক্লাসে
(Pydantic মডেলের জন্য হোক বা অন্য কিছুর জন্য)।

/// note | মনে রাখুন

নিজের core schema টাইপ সংজ্ঞায়িত করা সম্ভব নয়। একটি core schema `pydantic-core` প্যাকেজের
বুঝতে পারা দরকার, তাই আমরা শুধু নির্দিষ্ট সংখ্যক core schema টাইপ সমর্থন করি।
`GenerateSchema` সত্যিকার অর্থে প্রকাশ্য আর ঠিকমতো ডকুমেন্ট করা না হওয়ার এটিও একটি কারণ।

core schema-র সংজ্ঞাগুলো পাওয়া যাবে [`pydantic_core.core_schema`][] মডিউলে।

///

Pydantic মডেলের ক্ষেত্রে, একটি core schema তৈরি হয়ে
[`__pydantic_core_schema__`][pydantic.main.BaseModel.__pydantic_core_schema__] অ্যাট্রিবিউটে বসানো হয়।

core schema দেখতে কেমন তা বোঝাতে, আমরা
[`bool`][pydantic_core.core_schema.bool_schema] core schema-র উদাহরণ নেব:

⟦CODE1⟧

একটি boolean ফিল্ডসহ Pydantic মডেল সংজ্ঞায়িত করলে:

⟦CODE2⟧

`foo` ফিল্ডের core schema দেখতে হবে এমন:

⟦CODE3⟧

[`BoolSchema`][pydantic_core.core_schema.bool_schema] সংজ্ঞায় যেমন দেখা যায়,
সিরিয়ালাইজেশনের যুক্তিও core schema-তেই সংজ্ঞায়িত।
`foo`-এর জন্য একটি নিজের সিরিয়ালাইজেশন ফাংশন (1) সংজ্ঞায়িত করলে, `serialization` key দেখতে হবে এমন:
{ .annotate }

1. যেমন [`field_serializer`][pydantic.functional_serializers.field_serializer] decorator দিয়ে:

    ⟦CODE4⟧

⟦CODE5⟧

মনে রাখুন, এটিও একটি core schema সংজ্ঞা, শুধু এটি সিরিয়ালাইজেশনের সময় `pydantic-core`-এর জন্যই প্রাসঙ্গিক।

core schema-র পরিসর বিস্তৃত, আর Python আর Rust অংশের মধ্যে যোগাযোগের দরকার হলেই এগুলো ব্যবহার হয়।
আগের উদাহরণগুলো যাচাই আর সিরিয়ালাইজেশন নিয়ে হলেও, তাত্ত্বিকভাবে এটি যেকোনো কিছুর জন্য ব্যবহার করা যায়:
এরর ব্যবস্থাপনা, বাড়তি metadata ইত্যাদি।

/// tip | নিজে দেখে নিন

যেকোনো মডেলের core schema দেখতে পারেন: `print(Model.__pydantic_core_schema__)`। শেখার জন্য দারুণ, তবে এই কাঠামোর ওপর নির্ভর করে কোড লিখবেন না; ভেতরের জিনিস বলে এটি সংস্করণ ভেদে বদলাতে পারে।

///

### JSON Schema তৈরি { #json-schema-generation }

হয়তো লক্ষ করেছেন, আগের সিরিয়ালাইজেশন core schema-তে একটি `return_schema` key আছে।
কারণ সংশ্লিষ্ট JSON Schema তৈরিতেও core schema ব্যবহার হয়।

core schema যেভাবে তৈরি হয় তার মতোই, JSON Schema তৈরি সামলায়
[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] ক্লাস।
[`generate`][pydantic.json_schema.GenerateJsonSchema.generate] মেথড
হলো প্রধান প্রবেশপথ, আর একে সেই মডেলের core schema দেওয়া হয়।

আমাদের `bool` ফিল্ডের উদাহরণে ফিরে গেলে, [`bool_schema`][pydantic.json_schema.GenerateJsonSchema.bool_schema]
মেথডকে আগে তৈরি করা [boolean core schema][pydantic_core.core_schema.bool_schema] দেওয়া হবে
আর এটি নিচের JSON Schema ফেরত দেবে:

⟦CODE6⟧

### core schema আর JSON schema নিজের মতো করা { #customizing-the-core-schema-and-json-schema }

/// info | ব্যবহারের ডকুমেন্টেশন

[নিজের টাইপ](../concepts/types.md#custom-types)

[`__get_pydantic_core_schema__` বাস্তবায়ন](../concepts/json_schema.md#implementing-__get_pydantic_core_schema__)

[`__get_pydantic_json_schema__` বাস্তবায়ন](../concepts/json_schema.md#implementing-__get_pydantic_json_schema__)

///

`GenerateSchema` আর [`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] ক্লাস
সংশ্লিষ্ট schema তৈরি সামলালেও, কিছু ক্ষেত্রে Pydantic একটি wrapper (মোড়ক) পদ্ধতি মেনে সেগুলো নিজের মতো করার উপায় দেয়।
এই কাস্টমাইজেশন হয় `__get_pydantic_core_schema__` আর `__get_pydantic_json_schema__` মেথড দিয়ে।

এই wrapper পদ্ধতি বুঝতে, আমরা [`Annotated`][typing.Annotated]-এর সাথে ব্যবহৃত metadata ক্লাসের উদাহরণ নেব,
যেখানে `__get_pydantic_core_schema__` মেথড ব্যবহার করা যায়:

⟦CODE7⟧

1. `MyStrict` প্রথম প্রয়োগ হওয়া annotation। এই সময়ে `schema = {'type': 'int'}`।
2. `MyGt` শেষে প্রয়োগ হওয়া annotation। এই সময়ে `schema = {'type': 'int', 'strict': True}`।

`GenerateSchema` ক্লাস যখন `Annotated[int, MyStrict(), MyGt()]`-এর core schema তৈরি করে, তখন এটি
`MyGt.__get_pydantic_core_schema__` মেথডে পাঠানোর জন্য একটি `GetCoreSchemaHandler`-এর instance তৈরি করবে। (1)
{ .annotate }

1. আমাদের [`Annotated`][typing.Annotated] পদ্ধতির ক্ষেত্রে, `GetCoreSchemaHandler` নেস্টেডভাবে সংজ্ঞায়িত।
    এটি ডাকলে পুনরাবৃত্তভাবে অন্য `__get_pydantic_core_schema__` মেথডগুলো ডাকা হয়, যতক্ষণ না `int` annotation-এ পৌঁছায়,
    যেখানে একটি সাধারণ `{'type': 'int'}` schema ফেরত আসে।

/// tip | উদাহরণ দিয়ে বুঝি

রাশিয়ান পুতুলের (matryoshka) মতো: সবচেয়ে বাইরের পুতুল `MyGt`। এটি `handler(source)` ডেকে ভেতরের পুতুল খোলে (`MyStrict`), সেটিও `handler` ডেকে আরও ভেতরে যায়, শেষে সবচেয়ে ছোট পুতুল `int` পাওয়া যায় (`{'type': 'int'}`)। তারপর ফেরার পথে প্রতিটি স্তর নিজের অংশ যোগ করে: `strict`, তারপর `gt`।

///

`source` আর্গুমেন্ট নির্ভর করে core schema তৈরির পদ্ধতির ওপর। [`Annotated`][typing.Annotated]-এর ক্ষেত্রে,
`source` হবে যে টাইপে annotation দেওয়া হচ্ছে সেটি। [নিজের টাইপ সংজ্ঞায়িত করার](../concepts/types.md#as-a-method-on-a-custom-type) সময়,
`source` হবে সেই আসল ক্লাস যেখানে `__get_pydantic_core_schema__` সংজ্ঞায়িত।

## মডেলের যাচাই আর সিরিয়ালাইজেশন { #model-validation-and-serialization }

মডেল সংজ্ঞার পরিসর ছিল *ক্লাস* পর্যায়ে (অর্থাৎ মডেল সংজ্ঞায়িত করার সময়), কিন্তু মডেলের যাচাই
আর সিরিয়ালাইজেশন হয় *instance* পর্যায়ে। এই দুটোই সামলানো হয় `pydantic-core`-এ
(Pydantic V1-এর তুলনায় ৫ থেকে ২০ গুণ পারফরম্যান্স বৃদ্ধি দিয়ে), আগে তৈরি core schema ব্যবহার করে।

এই কাজগুলো করতে `pydantic-core` একটি [`SchemaValidator`][pydantic_core.SchemaValidator] আর
[`SchemaSerializer`][pydantic_core.SchemaSerializer] ক্লাস প্রকাশ করে:

⟦CODE8⟧

1. দেওয়া ডেটা `pydantic-core`-এ পাঠানো হয়
   [`SchemaValidator.validate_python`][pydantic_core.SchemaValidator.validate_python] মেথড দিয়ে।
   `pydantic-core` (মডেলের core schema মেনে) ডেটা যাচাই করবে আর
   মডেলের `__dict__` অ্যাট্রিবিউট পূরণ করবে।
2. `model` instance-টি `pydantic-core`-এ পাঠানো হয়
   [`SchemaSerializer.to_python`][pydantic_core.SchemaSerializer.to_python] মেথড দিয়ে।
   `pydantic-core` instance-এর `__dict__` অ্যাট্রিবিউট পড়বে আর উপযুক্ত ফল তৈরি করবে
   (আবারও, মডেলের core schema মেনে)।

### যাচাইকে ঘিরে plugin hook { #the-plugin-hook-around-validation }

Pydantic `SchemaValidator`-কে একটি plugin স্তরে মুড়ে রাখে: plugin ইনস্টল থাকলে,
`validate_python`, `validate_json` আর `validate_strings`-এর প্রতিটি ডাক মাঝপথে ধরা যায়, ফলে একটি plugin
প্রতিটি যাচাইয়ের ইনপুট, ফল আর যেকোনো এরর দেখতে পারে। [Logfire](../integrations/logfire.md)-এর মতো
পর্যবেক্ষণ টুলের পেছনে এই ব্যবস্থাই কাজ করে, যা প্রতিটি ডাকে আলাদা কোড না লিখেই যাচাই রেকর্ড করে।
plugin প্রতিটি মডেলের জন্য কনফিগার করা হয়
[`plugin_settings`][pydantic.ConfigDict.plugin_settings] কনফিগারেশন মান দিয়ে।

/// check | সংক্ষেপে মনে রাখুন

* `pydantic` (Python) মডেল বোঝে আর একবার core schema বানায়; `pydantic-core` (Rust) সেই schema দিয়ে প্রতিবার দ্রুত যাচাই আর সিরিয়ালাইজ করে।
* core schema হলো `type` key-সহ একটি ডিকশনারি; নতুন ধরনের core schema বানানো যায় না।
* JSON Schema-ও core schema থেকে তৈরি (`GenerateJsonSchema`)।
* নিজের মতো করতে `__get_pydantic_core_schema__` / `__get_pydantic_json_schema__`, যারা `handler` ডেকে ভেতরের schema নেয় আর তাতে যোগ করে।

///
