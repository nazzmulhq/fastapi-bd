# JSON Schema { #json-schema }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema`][pydantic.json_schema]<br>

///

/// note | এই পেজে যা শিখবেন

* JSON Schema কী, আর Pydantic মডেল থেকে কীভাবে তা তৈরি হয়।
* `model_json_schema()` আর `TypeAdapter.json_schema()` ব্যবহার।
* ফিল্ড আর মডেল স্তরে schema নিজের মতো করা: title, description, examples, `json_schema_extra`।
* কাস্টম টাইপের schema, schema তৈরির পুরো প্রক্রিয়া বদলানো, আর `$ref` নিজের মতো করা।

///

/// tip | উদাহরণ দিয়ে বুঝি

JSON Schema হলো ডেটার একটি "নিয়মের বই", যা নিজেও JSON-এ লেখা: "এই অবজেক্টে `name` থাকবে, সেটি স্ট্রিং; `age` থাকবে, সেটি integer আর বাধ্যতামূলক"। যেকোনো ভাষার যেকোনো টুল এই নিয়মের বই পড়ে বুঝতে পারে আপনার ডেটা কেমন। FastAPI-র `/docs` পেজ, SDK জেনারেটর, এমনকি AI মডেলের "structured output", সবই এই JSON Schema পড়ে কাজ করে। Pydantic আপনার Python মডেল থেকে এই নিয়মের বই স্বয়ংক্রিয়ভাবে লিখে দেয়।

///

Pydantic মডেল থেকে স্বয়ংক্রিয়ভাবে JSON schema তৈরি আর নিজের মতো করার সুযোগ দেয়।
তৈরি হওয়া JSON schema নিচের স্পেসিফিকেশনগুলো মেনে চলে:

* [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/release-notes.html)
* [OpenAPI Specification v3.1.0](https://github.com/OAI/OpenAPI-Specification)।

## JSON Schema তৈরি করা { #generating-json-schema }

JSON schema তৈরি করতে নিচের ফাংশনগুলো ব্যবহার করুন:

* [`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] একটি মডেলের schema-র একটি JSON-যোগ্য dict ফেরত দেয়।
* [`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] একটি adapt করা টাইপের schema-র একটি JSON-যোগ্য dict ফেরত দেয়।

/// note | নোট

এই মেথডগুলোকে [`BaseModel.model_dump_json`][pydantic.main.BaseModel.model_dump_json]
আর [`TypeAdapter.dump_json`][pydantic.type_adapter.TypeAdapter.dump_json]-এর সাথে গুলিয়ে ফেলবেন না, যেগুলো যথাক্রমে
মডেল বা adapt করা টাইপের ইনস্ট্যান্স (আসল ডেটা) সিরিয়ালাইজ করে। ওই মেথডগুলো JSON স্ট্রিং ফেরত দেয়। তুলনায়,
[`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] আর
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] যথাক্রমে মডেল বা adapt করা টাইপের JSON schema (ডেটার নিয়ম)
বোঝায় এমন একটি JSON-যোগ্য dict ফেরত দেয়।

///

/// note | JSON schema-র "JSON-যোগ্য" প্রকৃতি নিয়ে

[`model_json_schema`][pydantic.main.BaseModel.model_json_schema]-এর ফলাফলের "JSON-যোগ্য" প্রকৃতি সম্পর্কে বলতে গেলে,
কোনো `BaseModel` `m`-এর ওপর `json.dumps(m.model_json_schema())` কল করলে একটি বৈধ JSON স্ট্রিং পাওয়া যায়। একইভাবে,
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema]-এর ক্ষেত্রে,
`json.dumps(TypeAdapter(<some_type>).json_schema())` কল করলে একটি বৈধ JSON স্ট্রিং পাওয়া যায়।

///

/// tip | পরামর্শ

Pydantic নিচের দুটোই সমর্থন করে:

1. [JSON Schema নিজের মতো করা](#customizing-json-schema)
2. [JSON Schema তৈরির প্রক্রিয়া নিজের মতো করা](#customizing-the-json-schema-generation-process)

প্রথম পদ্ধতির পরিধি সাধারণত সংকীর্ণ, এটি আরও নির্দিষ্ট ক্ষেত্র আর টাইপের জন্য JSON schema নিজের মতো করতে দেয়।
দ্বিতীয় পদ্ধতির পরিধি সাধারণত বড়, এটি সামগ্রিকভাবে JSON schema তৈরির প্রক্রিয়া নিজের মতো করতে দেয়।
দুটো পদ্ধতিতেই একই ফল পাওয়া যায়, কিন্তু আপনার প্রয়োজন অনুযায়ী একটি অন্যটির চেয়ে সহজ সমাধান দিতে পারে।

///

একটি `BaseModel` থেকে JSON schema তৈরির একটি উদাহরণ:

⟦CODE1⟧

JSON আউটপুট:

⟦CODE2⟧


1. এটি `MainModel`-এর schema-র একটি "JSON-যোগ্য" dict তৈরি করে।
2. schema dict-এর ওপর `json.dumps` কল করলে একটি JSON স্ট্রিং পাওয়া যায়।

/// info | আউটপুটটি সহজ ভাষায়

* `properties`: প্রতিটি ফিল্ড আর তার টাইপ। `snap`-এর জন্য `title`, `description`, `default` আর `gt`/`lt` থেকে আসা `exclusiveMinimum`/`exclusiveMaximum` সব দেখা যাচ্ছে।
* `required`: বাধ্যতামূলক ফিল্ড, এখানে শুধু `foo_bar`।
* `$defs`: নেস্টেড মডেল (`FooBar`) আর enum (`Gender`)-এর সংজ্ঞা আলাদা রাখা, আর `$ref` দিয়ে উল্লেখ করা।
* `description`: মডেলের docstring থেকে, আর `title`: `ConfigDict(title='Main')` থেকে।
* `Gender` ফিল্ডটি alias দিয়ে লেখা, কারণ schema ডিফল্টভাবে alias ব্যবহার করে।

///

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ক্লাস দিয়ে যেকোনো টাইপের জন্য যাচাই, সিরিয়ালাইজ
আর JSON schema তৈরির মেথডসহ একটি অবজেক্ট তৈরি করা যায়। এটি Pydantic V1-এর `schema_of`-এর
(যা এখন deprecated) সম্পূর্ণ বিকল্প।

একটি [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] থেকে JSON schema তৈরির একটি উদাহরণ:

⟦CODE3⟧

[`BaseModel`][pydantic.main.BaseModel] আর [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]-এর সমন্বয়ের জন্যও
JSON schema তৈরি করতে পারেন, যেমন এই উদাহরণে দেখানো হয়েছে:

⟦CODE4⟧

JSON আউটপুট:

⟦CODE5⟧

(`Cat | Dog` union-এর জন্য schema-তে `anyOf` এসেছে, অর্থাৎ "এদের যেকোনো একটি"।)

### `JsonSchemaMode` কনফিগার করা { #configuring-the-jsonschemamode }

[`model_json_schema`][pydantic.main.BaseModel.model_json_schema] আর
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] মেথডের `mode` প্যারামিটার দিয়ে JSON schema তৈরির মোড
নির্দিষ্ট করুন। ডিফল্টভাবে মোড `'validation'`, যা মডেলের যাচাইয়ের schema-র সাথে মেলে এমন JSON schema তৈরি করে।

[`JsonSchemaMode`][pydantic.json_schema.JsonSchemaMode] হলো একটি টাইপ alias, যা `mode` প্যারামিটারের উপলব্ধ অপশনগুলো বোঝায়:

* `'validation'` (ইনপুট হিসেবে কী গ্রহণ করা হয়)
* `'serialization'` (আউটপুট হিসেবে কী বের হয়)

`mode` প্যারামিটার কীভাবে নির্দিষ্ট করতে হয়, আর তা তৈরি হওয়া JSON schema-কে কীভাবে প্রভাবিত করে, তার একটি উদাহরণ:

⟦CODE6⟧

(`Decimal` ইনপুটে সংখ্যা বা স্ট্রিং দুটোই গ্রহণ করে, তাই validation schema-তে `anyOf`; কিন্তু আউটপুটে সবসময় স্ট্রিং হিসেবে বের হয়, তাই serialization schema-তে শুধু `string`।)

## JSON Schema নিজের মতো করা { #customizing-json-schema }

তৈরি হওয়া JSON schema [ফিল্ড স্তরে](#field-level-customization) আর [মডেল স্তরে](#model-level-customization) দুই জায়গাতেই নিজের মতো করা যায়।

ফিল্ড আর মডেল দুই স্তরেই JSON schema-তে বাড়তি তথ্য যোগ করতে [`json_schema_extra` অপশন](#using-json_schema_extra) ব্যবহার করতে পারেন।

কাস্টম টাইপের জন্য, JSON schema তৈরি নিজের মতো করতে Pydantic অন্যান্য টুল দেয়:

1. [`WithJsonSchema` অ্যানোটেশন](#withjsonschema-annotation)
2. [`SkipJsonSchema` অ্যানোটেশন](#skipjsonschema-annotation)
3. [`__get_pydantic_core_schema__` বাস্তবায়ন](#implementing_get_pydantic_core_schema)
4. [`__get_pydantic_json_schema__` বাস্তবায়ন](#implementing_get_pydantic_json_schema)

### ফিল্ড-স্তরের কাস্টমাইজেশন { #field-level-customization }

[ফিল্ডের](./fields.md) JSON Schema নিজের মতো করা যায়। এটি সাধারণত [`Field()`][pydantic.fields.Field]
ফাংশন দিয়ে করা হয়।

কিছু ফিল্ড প্যারামিটার শুধু তৈরি হওয়া JSON Schema নিজের মতো করতে ব্যবহার হয়:

* `title`: ফিল্ডের শিরোনাম।
* `description`: ফিল্ডের বর্ণনা।
* `examples`: ফিল্ডের উদাহরণ।
* `json_schema_extra`: ফিল্ডে যোগ করার বাড়তি JSON Schema প্রপার্টি ([নির্দিষ্ট ডকুমেন্টেশন](#using-json_schema_extra) দেখুন)।
* `field_title_generator`: একটি ফাংশন, যা ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে ফিল্ডের শিরোনাম সেট করে।

একটি উদাহরণ:

⟦CODE7⟧

JSON আউটপুট:

⟦CODE8⟧


1. [Annotated প্যাটার্নও](./fields.md#the-annotated-pattern) ব্যবহার করা যায়।

(লক্ষ্য করুন, `SecretStr` পাসওয়ার্ড ফিল্ড schema-তে `"writeOnly": true` আর `"format": "password"` পেয়েছে, অর্থাৎ এটি শুধু পাঠানো যায়, ফেরত দেখানো হয় না।)

### প্রোগ্রাম দিয়ে ফিল্ডের শিরোনাম তৈরি { #programmatic-field-title-generation }

ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে শিরোনাম তৈরি করতে `field_title_generator` প্যারামিটার ব্যবহার করা যায়।

নিচের উদাহরণ দেখুন:

⟦CODE9⟧

### মডেল-স্তরের কাস্টমাইজেশন { #model-level-customization }

একটি মডেলে JSON schema তৈরি নিজের মতো করতে [model config][pydantic.config.ConfigDict]-ও ব্যবহার করতে পারেন।
বিশেষ করে, নিচের config অপশনগুলো প্রাসঙ্গিক:

* [`title`][pydantic.config.ConfigDict.title]
* [`json_schema_extra`][pydantic.config.ConfigDict.json_schema_extra]
* [`json_schema_mode_override`][pydantic.config.ConfigDict.json_schema_mode_override]
* [`field_title_generator`][pydantic.config.ConfigDict.field_title_generator]
* [`model_title_generator`][pydantic.config.ConfigDict.model_title_generator]

### `json_schema_extra` ব্যবহার করা { #using-json_schema_extra }

JSON schema-তে বাড়তি তথ্য যোগ করতে `json_schema_extra` অপশন ব্যবহার করা যায়, হয়
[ফিল্ড স্তরে](#field-level-customization), নয়তো [মডেল স্তরে](#model-level-customization)।
`json_schema_extra`-তে একটি `dict` বা একটি `Callable` দিতে পারেন।

#### `dict` দিয়ে `json_schema_extra` ব্যবহার { #using-json_schema_extra-with-a-dict }

JSON schema-তে বাড়তি তথ্য যোগ করতে `json_schema_extra`-তে একটি `dict` দিতে পারেন:

⟦CODE10⟧

JSON আউটপুট:

⟦CODE11⟧

(FastAPI-তে রিকোয়েস্ট বডির উদাহরণ `/docs`-এ দেখাতে ঠিক এভাবেই `examples` যোগ করা হয়।)

#### `Callable` দিয়ে `json_schema_extra` ব্যবহার { #using-json_schema_extra-with-a-callable }

একটি ফাংশন দিয়ে JSON schema বদলাতে `json_schema_extra`-তে একটি `Callable` দিতে পারেন:

⟦CODE12⟧

JSON আউটপুট:

⟦CODE13⟧

(ফাংশনটি schema থেকে `default` মুছে দিয়েছে, তাই আউটপুটে `a`-এর ডিফল্ট দেখা যাচ্ছে না।)

#### `json_schema_extra` মিলিয়ে দেওয়া { #merging-json_schema_extra }

v2.9 থেকে, Pydantic অ্যানোটেট করা টাইপগুলোর `json_schema_extra` ডিকশনারিগুলো মিলিয়ে (merge করে) দেয়।
এই পদ্ধতি আগের ওভাররাইড আচরণের বদলে মেলানোর আরও যোগমূলক একটি পদ্ধতি দেয়।
একাধিক টাইপে json schema-র বাড়তি তথ্য পুনরায় ব্যবহারের ক্ষেত্রে এটি বেশ কাজের হতে পারে।

আমরা এই পরিবর্তনকে মূলত একটি বাগ ফিক্স হিসেবে দেখেছি, কারণ এটি `BaseModel` আর `TypeAdapter` ইনস্ট্যান্সের মধ্যে `json_schema_extra` মেলানোর আচরণে
অনিচ্ছাকৃত পার্থক্য দূর করে - আরও বিস্তারিত জানতে [এই issue](https://github.com/pydantic/pydantic/issues/9210)
দেখুন।

⟦CODE14⟧

/// note | নোট

আমরা আর `dict` আর `callable` টাইপের `json_schema_extra` স্পেসিফিকেশনের মিশ্রণ সমর্থন করি না (আর কখনো পুরোপুরি করিনি)।
যদি আপনার ক্ষেত্রে এটি একটি প্রয়োজন হয়, তাহলে অনুগ্রহ করে [একটি pydantic issue খুলুন](https://github.com/pydantic/pydantic/issues/new/choose) আর আপনার পরিস্থিতি ব্যাখ্যা করুন - জোরালো যুক্তি পেলে আমরা এই সিদ্ধান্ত আবার বিবেচনা করতে খুশি হব।

///

### `WithJsonSchema` অ্যানোটেশন { #withjsonschema-annotation }

/// tip | পরামর্শ

কাস্টম টাইপের জন্য [`__get_pydantic_json_schema__()` বাস্তবায়নের](#implementing_get_pydantic_json_schema) চেয়ে
[`WithJsonSchema`][pydantic.json_schema.WithJsonSchema] ব্যবহার করাই ভালো,
কারণ এটি আরও সহজ আর ভুলের সম্ভাবনা কম।

///

একটি টাইপের JSON Schema ওভাররাইড করার জন্য ব্যবহৃত একটি অ্যানোটেশন।

এটি কাজের যখন এমন একটি টাইপের জন্য JSON Schema সেট করতে চান যা ডিফল্টভাবে কোনো JSON Schema তৈরি করে না
(যেমন [`Callable`][collections.abc.Callable])। লক্ষ্য করুন, এটি টাইপটির পুরো তৈরি হওয়া JSON Schema ওভাররাইড করে
(নিচের উদাহরণে `'type'`-ও দিতে হয়েছে)।

⟦CODE15⟧

JSON আউটপুট:

⟦CODE16⟧


আরও বিস্তারিত জানতে [API ডকুমেন্টেশন][pydantic.json_schema.WithJsonSchema] দেখুন।

/// note | নোট

[validator](./validators.md) যুক্ত ফিল্ডের JSON Schema সূক্ষ্মভাবে ঠিক করতে আপনি [`WithJsonSchema`][pydantic.json_schema.WithJsonSchema]
অ্যানোটেশন ব্যবহারে প্রলুব্ধ হতে পারেন। এর বদলে
[`json_schema_input_type` আর্গুমেন্ট](./validators.md#json-schema-and-field-validators) ব্যবহারের পরামর্শ দেওয়া হয়।

///

### `SkipJsonSchema` অ্যানোটেশন { #skipjsonschema-annotation }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema.SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema]<br>

///

তৈরি হওয়া JSON schema থেকে একটি অন্তর্ভুক্ত ফিল্ড (বা একটি ফিল্ডের স্পেসিফিকেশনের অংশ) বাদ দিতে [`SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema] অ্যানোটেশন
ব্যবহার করা যায়। আরও বিস্তারিত জানতে API ডকস দেখুন।

### `__get_pydantic_core_schema__` বাস্তবায়ন <a name="implementing_get_pydantic_core_schema"></a> { #implementing-get_pydantic_core_schema }

কাস্টম টাইপ (`field_name: TheType` বা `field_name: Annotated[TheType, ...]` হিসেবে ব্যবহৃত) আর `Annotated` মেটাডেটা
(`field_name: Annotated[int, SomeMetadata]` হিসেবে ব্যবহৃত)
`__get_pydantic_core_schema__` বাস্তবায়ন করে তৈরি হওয়া schema বদলাতে বা ওভাররাইড করতে পারে।
এই মেথড দুটি positional আর্গুমেন্ট পায়:

1. এই টাইপের সাথে সংশ্লিষ্ট টাইপ অ্যানোটেশন (তাই `TheType[T][int]`-এর ক্ষেত্রে এটি হবে `TheType[int]`)।
2. `__get_pydantic_core_schema__`-এর পরবর্তী বাস্তবায়নকারীকে কল করার জন্য একটি handler/callback।

handler ব্যবস্থাটি ঠিক [*wrap* ফিল্ড validator](validators.md#field-wrap-validator)-এর মতো কাজ করে।
এই ক্ষেত্রে ইনপুট হলো টাইপ আর আউটপুট একটি `core_schema`।

(core schema হলো Pydantic-এর ভেতরের "নির্দেশনার তালিকা", যা Rust ইঞ্জিন `pydantic-core` পড়ে যাচাই আর সিরিয়ালাইজ করে। JSON schema এই core schema থেকেই তৈরি হয়।)

একটি কাস্টম টাইপের উদাহরণ যা তৈরি হওয়া `core_schema` *ওভাররাইড* করে:

⟦CODE17⟧

/// info | কোডটি সহজ ভাষায়

`CompressedString` একটি নিজস্ব ক্লাস, যা একটি বাক্যকে শব্দের অভিধান আর সংখ্যার তালিকা হিসেবে সংকুচিত করে রাখে। `__get_pydantic_core_schema__` Pydantic-কে বলে দেয়: "ইনপুট হবে একটি স্ট্রিং (`str_schema()`), যাচাইয়ের পরে `_validate` দিয়ে সংকুচিত রূপে বানাও, আর সিরিয়ালাইজ করার সময় `_serialize` দিয়ে আবার স্ট্রিং বানাও"। ফলে JSON schema-তে ফিল্ডটি সাধারণ `string` হিসেবেই দেখায়।

///

যেহেতু Pydantic `CompressedString`-এর জন্য schema তৈরি করতে জানে না, তাই এর `__get_pydantic_core_schema__` মেথডে
`handler(source)` কল করলে একটি `pydantic.errors.PydanticSchemaGenerationError` এরর পেতেন।
বেশিরভাগ কাস্টম টাইপের ক্ষেত্রে এমনই হবে, তাই কাস্টম টাইপের জন্য প্রায় কখনোই `handler` কল করতে চাইবেন না।

`Annotated` মেটাডেটার প্রক্রিয়া প্রায় একই, শুধু সাধারণত `handler` কল করে
Pydantic-কে schema তৈরি সামলাতে দিতে পারেন।

⟦CODE18⟧

(`RestrictCharacters('ABC')` আগে `handler(source)` দিয়ে স্বাভাবিক `str` schema নেয়, তারপর তার পরে নিজের যাচাই জুড়ে দেয়: স্ট্রিংয়ে শুধু A, B, C অক্ষর থাকতে পারবে।)

এ পর্যন্ত আমরা schema মুড়ে দিচ্ছিলাম, কিন্তু যদি শুধু এটিকে *বদলাতে* বা *উপেক্ষা* করতে চান, তাও করতে পারেন।

schema বদলাতে, প্রথমে handler কল করুন, তারপর ফলাফলটি পরিবর্তন করুন:

⟦CODE19⟧

/// tip | পরামর্শ

লক্ষ্য করুন, একটি schema আপনাকে *অবশ্যই* ফেরত দিতে হবে, এমনকি যদি শুধু সেটিকে জায়গায় বদলান।

///

schema পুরোপুরি ওভাররাইড করতে, handler কল না করে নিজের
`CoreSchema` ফেরত দিন:

⟦CODE20⟧

### `__get_pydantic_json_schema__` বাস্তবায়ন <a name="implementing_get_pydantic_json_schema"></a> { #implementing-get_pydantic_json_schema }

তৈরি হওয়া json schema বদলাতে বা ওভাররাইড করতে `__get_pydantic_json_schema__`-ও বাস্তবায়ন করতে পারেন।
এই মেথড বদলালে শুধু JSON schema প্রভাবিত হয় - core schema নয়, যা যাচাই আর সিরিয়ালাইজেশনে ব্যবহার হয়।

তৈরি হওয়া JSON schema বদলানোর একটি উদাহরণ:

⟦CODE21⟧

JSON আউটপুট:

⟦CODE22⟧

(`Person` ক্লাসের core schema একটি typed dict হিসেবে সংজ্ঞায়িত, আর `__get_pydantic_json_schema__` তৈরি হওয়া JSON schema-তে শুধু একটি উদাহরণ আর শিরোনাম যোগ করে, যাচাইয়ের আচরণে কোনো প্রভাব না ফেলে।)

### `field_title_generator` ব্যবহার { #using-field_title_generator }

ফিল্ডের নাম আর তথ্যের ভিত্তিতে প্রোগ্রাম দিয়ে শিরোনাম তৈরি করতে `field_title_generator` প্যারামিটার ব্যবহার করা যায়।
এটি ফিল্ড-স্তরের `field_title_generator`-এর মতো, কিন্তু `ConfigDict` অপশনটি ক্লাসের সব ফিল্ডে প্রয়োগ হবে।

নিচের উদাহরণ দেখুন:

⟦CODE23⟧

### `model_title_generator` ব্যবহার { #using-model_title_generator }

`model_title_generator` config অপশন `field_title_generator` অপশনের মতো, কিন্তু এটি মডেলের নিজের শিরোনামে প্রযোজ্য,
আর ইনপুট হিসেবে মডেল ক্লাস নেয়।

নিচের উদাহরণ দেখুন:

⟦CODE24⟧

## JSON schema-র টাইপ { #json-schema-types }

টাইপ, কাস্টম ফিল্ড টাইপ আর শর্ত (যেমন `max_length`) সংশ্লিষ্ট স্পেসিফিকেশনের ফরম্যাটে ম্যাপ করা হয়
নিচের অগ্রাধিকারের ক্রমে (যখন সমতুল্য কিছু পাওয়া যায়):

1. [JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core)
2. [JSON Schema Validation](https://json-schema.org/draft/2020-12/json-schema-validation)
3. [OpenAPI Data Types](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#data-types)
4. আরও জটিল `string` সাব-টাইপের জন্য Pydantic-এর সম্প্রসারণ সংজ্ঞায়িত করতে স্ট্যান্ডার্ড `format` JSON ফিল্ড ব্যবহার হয়।

Python বা Pydantic থেকে JSON schema-তে ফিল্ডের schema ম্যাপিং নিচের মতো করা হয়:

/// info | সারণির কলামগুলোর অর্থ

* **Python type**: আপনার মডেলে লেখা টাইপ।
* **JSON Schema Type**: JSON schema-তে কোন মৌলিক টাইপ হিসেবে দেখাবে (`string`, `integer`, `array` ইত্যাদি)।
* **Additional JSON Schema**: সাথে কোন বাড়তি তথ্য যোগ হবে (যেমন `"format": "email"`)।
* **Defined in**: নিয়মটি কোন স্ট্যান্ডার্ড থেকে এসেছে।
* **Notes**: বাড়তি মন্তব্য।

যেমন `EmailStr` হয়ে যায় `{"type": "string", "format": "email"}`, আর `PositiveInt` হয়ে যায় `{"type": "integer", "exclusiveMinimum": 0}`।

///

⟦CODE25⟧


## শীর্ষ-স্তরের schema তৈরি { #top-level-schema-generation }

এমন একটি শীর্ষ-স্তরের JSON schema-ও তৈরি করতে পারেন, যার `$defs`-এ শুধু মডেলের একটি তালিকা আর সংশ্লিষ্ট
সাব-মডেলগুলো থাকে:

⟦CODE26⟧

JSON আউটপুট:

⟦CODE27⟧


## JSON Schema তৈরির প্রক্রিয়া নিজের মতো করা { #customizing-the-json-schema-generation-process }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.json_schema`][pydantic.json_schema.GenerateJsonSchema]<br>

///

যদি কাস্টম schema তৈরির দরকার হয়, তাহলে আপনার অ্যাপ্লিকেশনের প্রয়োজনমতো
[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] ক্লাস বদলে একটি `schema_generator` ব্যবহার করতে পারেন।

JSON schema তৈরির বিভিন্ন মেথড একটি keyword argument `schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema` গ্রহণ করে, আর JSON schema তৈরিতে নিজের পদ্ধতি ব্যবহার করতে এই মেথডগুলোতে আপনার কাস্টম সাব-ক্লাস দিতে পারেন।

`GenerateJsonSchema` একটি টাইপের `pydantic-core` schema-কে একটি JSON schema-তে রূপান্তর বাস্তবায়ন করে।
নকশা অনুযায়ী, এই ক্লাস JSON schema তৈরির প্রক্রিয়াকে ছোট ছোট মেথডে ভাগ করে, যেগুলো সাব-ক্লাসে সহজে ওভাররাইড করে
JSON schema তৈরির "সার্বিক" পদ্ধতি বদলানো যায়।

⟦CODE28⟧

(এখানে `generate` মেথড ওভাররাইড করে প্রতিটি schema-র শিরোনাম বদলানো আর `$schema` কী যোগ করা হয়েছে।)

যেসব ফিল্ডের বৈধ json schema নেই সেগুলো schema থেকে বাদ দিতে নিচের পদ্ধতি ব্যবহার করতে পারেন:

⟦CODE29⟧

(`Callable` টাইপের ফিল্ডের কোনো JSON schema হয় না; `handle_invalid_for_json_schema`-এ `PydanticOmit` raise করলে এরর না দিয়ে ফিল্ডটি চুপচাপ বাদ পড়ে।)

### JSON schema সাজানো (sorting) { #json-schema-sorting }

ডিফল্টভাবে, Pydantic key-গুলো বর্ণানুক্রমে সাজিয়ে JSON schema পুনরাবৃত্তভাবে সাজায়। উল্লেখযোগ্যভাবে, মডেলে ফিল্ডগুলো যে ক্রমে সংজ্ঞায়িত
তা বজায় রাখতে Pydantic `properties` key-এর মানগুলো সাজানো এড়িয়ে যায়।

এই আচরণ নিজের মতো করতে চাইলে, আপনার কাস্টম `GenerateJsonSchema` সাব-ক্লাসে `sort` মেথড ওভাররাইড করতে পারেন। নিচের উদাহরণে
সাজানো পুরোপুরি বন্ধ করতে একটি কিছু-না-করা `sort` মেথড ব্যবহার করা হয়েছে, যা মডেলের ফিল্ড আর `json_schema_extra` key-এর বজায় থাকা ক্রমে দেখা যায়:

⟦CODE30⟧

## JSON Schema-তে `$ref` নিজের মতো করা { #customizing-the-refs-in-json-schema }

[`model_json_schema()`][pydantic.main.BaseModel.model_json_schema]
বা [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]-কে `ref_template` keyword argument দিয়ে কল করে `$ref`-এর ফরম্যাট বদলানো যায়।
সংজ্ঞাগুলো সবসময় `$defs` key-এর নিচে রাখা হয়, কিন্তু রেফারেন্সের জন্য একটি নির্দিষ্ট উপসর্গ ব্যবহার করা যায়।

JSON schema-র ডিফল্ট সংজ্ঞার অবস্থান বাড়ানো বা বদলানোর প্রয়োজন হলে এটি কাজের। যেমন, OpenAPI-র ক্ষেত্রে:

⟦CODE31⟧

JSON আউটপুট:

⟦CODE32⟧

(OpenAPI-তে মডেলগুলো থাকে `#/components/schemas/...`-এ, তাই `ref_template` দিয়ে `$ref`-গুলো সেই ঠিকানায় নির্দেশ করানো হয়েছে।)

## JSON Schema তৈরি নিয়ে বিবিধ নোট { #miscellaneous-notes-on-json-schema-generation }

* `Optional` ফিল্ডের JSON schema দেখায় যে `null` মান অনুমোদিত।
* `Decimal` টাইপ JSON schema-তে স্ট্রিং হিসেবে দেখানো (আর সিরিয়ালাইজ করা) হয়।
* যেহেতু JSON-এ `namedtuple` টাইপ নেই, তাই একটি মডেলের JSON schema `namedtuple`-কে `namedtuple` হিসেবে রাখে না।
* ব্যবহৃত সাব-মডেলগুলো স্পেসিফিকেশন অনুযায়ী `$defs` JSON অ্যাট্রিবিউটে যোগ হয় আর রেফারেন্স করা হয়।
* পরিবর্তনসহ (`Field` ক্লাস দিয়ে, যেমন কাস্টম শিরোনাম, বর্ণনা বা ডিফল্ট মান) সাব-মডেলগুলো রেফারেন্সের বদলে
    পুনরাবৃত্তভাবে অন্তর্ভুক্ত হয়।
* মডেলের `description` নেওয়া হয় ক্লাসের docstring থেকে, অথবা `Field` ক্লাসের `description`
    আর্গুমেন্ট থেকে।
* schema ডিফল্টভাবে key হিসেবে alias ব্যবহার করে তৈরি হয়, কিন্তু [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema] বা
    [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]-কে `by_alias=False` keyword argument দিয়ে কল করে
    মডেলের প্রপার্টির নাম ব্যবহার করেও তৈরি করা যায়।

/// check | সংক্ষেপে মনে রাখুন

* `Model.model_json_schema()` বা `TypeAdapter(T).json_schema()` দিয়ে JSON schema পাওয়া যায়।
* `mode='validation'` (ইনপুটের নিয়ম) আর `mode='serialization'` (আউটপুটের নিয়ম) ভিন্ন হতে পারে।
* `Field(title=..., description=..., examples=...)` আর `json_schema_extra` দিয়ে schema-তে তথ্য যোগ করুন।
* কাস্টম টাইপের জন্য সবচেয়ে সহজ `WithJsonSchema`; বড় পরিবর্তনের জন্য `GenerateJsonSchema` সাব-ক্লাস।

///
