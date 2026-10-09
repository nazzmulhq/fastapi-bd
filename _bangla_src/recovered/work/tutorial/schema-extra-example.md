# রিকোয়েস্টের উদাহরণ ডেটা ঘোষণা করুন { #declare-request-example-data }

আপনার অ্যাপ যে ডেটা গ্রহণ করতে পারে তার উদাহরণ আপনি ঘোষণা করতে পারেন।

এটি করার কয়েকটি উপায় এখানে দেওয়া হলো।

## Pydantic মডেলে অতিরিক্ত JSON Schema ডেটা { #extra-json-schema-data-in-pydantic-models }

আপনি একটি Pydantic মডেলের জন্য `examples` ঘোষণা করতে পারেন যা তৈরি হওয়া JSON Schema-তে যোগ হবে।

{* ../../docs_src/schema_extra_example/tutorial001_py310.py hl[13:24] *}

ওই অতিরিক্ত তথ্য ওই মডেলের আউটপুট **JSON Schema**-তে হুবহু যোগ হবে, এবং API ডকুমেন্টেশনে ব্যবহার হবে।

আপনি `model_config` অ্যাট্রিবিউট ব্যবহার করতে পারেন, যা একটি `dict` নেয়, যেমনটা [Pydantic-এর ডকুমেন্টেশন: Configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/)-এ বর্ণনা করা হয়েছে।

তৈরি হওয়া JSON Schema-তে আপনি যে অতিরিক্ত ডেটা দেখাতে চান, `examples`-সহ, তা ধারণকারী একটি `dict` দিয়ে আপনি `"json_schema_extra"` সেট করতে পারেন।

/// tip | পরামর্শ

একই কৌশল ব্যবহার করে আপনি JSON Schema বাড়াতে এবং নিজের কাস্টম অতিরিক্ত তথ্য যোগ করতে পারেন।

যেমন, একটি ফ্রন্টএন্ড ইউজার ইন্টারফেসের জন্য মেটাডেটা যোগ করতে আপনি এটি ব্যবহার করতে পারেন।

///

/// note | নোট

OpenAPI 3.1.0 (FastAPI 0.99.0 থেকে ব্যবহৃত) `examples`-এর সাপোর্ট যোগ করেছে, যা **JSON Schema** স্ট্যান্ডার্ডের অংশ।

তার আগে এটি কেবল একটিমাত্র উদাহরণসহ `example` কিওয়ার্ড সাপোর্ট করত। OpenAPI 3.1.0 এখনো সেটি সাপোর্ট করে, তবে এটি ডেপ্রিকেটেড এবং JSON Schema স্ট্যান্ডার্ডের অংশ নয়। তাই আপনাকে `example` থেকে `examples`-এ মাইগ্রেট করতে উৎসাহিত করা হচ্ছে। 🤓

এই পেজের শেষে আপনি আরও পড়তে পারেন।

///

## `Field`-এর অতিরিক্ত আর্গুমেন্ট { #field-additional-arguments }

Pydantic মডেলের সাথে `Field()` ব্যবহার করার সময় আপনি অতিরিক্ত `examples`-ও ঘোষণা করতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial002_py310.py hl[2,8:11] *}

## JSON Schema-তে `examples` - OpenAPI { #examples-in-json-schema-openapi }

এগুলোর যেকোনোটি ব্যবহার করার সময়:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

আপনি অতিরিক্ত তথ্যসহ একদল `examples`-ও ঘোষণা করতে পারেন, যা **OpenAPI**-এর ভেতরে এগুলোর **JSON Schema**-তে যোগ হবে।

### `examples`-সহ `Body` { #body-with-examples }

এখানে আমরা `Body()`-তে প্রত্যাশিত ডেটার একটি উদাহরণ ধারণকারী `examples` দিচ্ছি:

{* ../../docs_src/schema_extra_example/tutorial003_an_py310.py hl[22:29] *}

### ডকুমেন্টেশন UI-তে উদাহরণ { #example-in-the-docs-ui }

ওপরের যেকোনো পদ্ধতিতে `/docs`-এ এটি দেখতে এরকম হবে:

<img src="/img/tutorial/body-fields/image01.png">

### একাধিক `examples`-সহ `Body` { #body-with-multiple-examples }

অবশ্যই আপনি একাধিক `examples`-ও দিতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial004_an_py310.py hl[23:38] *}

আপনি এটি করলে উদাহরণগুলো ওই বডি ডেটার অভ্যন্তরীণ **JSON Schema**-এর অংশ হবে।

তবুও, <dfn title="২০২৩-০৮-২৬">এটি লেখার সময়</dfn> পর্যন্ত ডকুমেন্টেশন UI দেখানোর দায়িত্বে থাকা টুল Swagger UI **JSON Schema**-তে ডেটার জন্য একাধিক উদাহরণ দেখানো সাপোর্ট করে না। তবে একটি বিকল্প সমাধানের জন্য নিচে পড়ুন।

### OpenAPI-নির্দিষ্ট `examples` { #openapi-specific-examples }

**JSON Schema** `examples` সাপোর্ট করার আগে থেকেই OpenAPI-তে একটি ভিন্ন ফিল্ডের সাপোর্ট ছিল, যার নামও `examples`।

এই **OpenAPI-নির্দিষ্ট** `examples` OpenAPI স্পেসিফিকেশনের আরেকটি অংশে থাকে। এটি থাকে **প্রতিটি *পাথ অপারেশনের* বিবরণে**, প্রতিটি JSON Schema-র ভেতরে নয়।

আর Swagger UI কিছুদিন ধরে এই নির্দিষ্ট `examples` ফিল্ডটি সাপোর্ট করছে। তাই আপনি এটি ব্যবহার করে **ডকুমেন্টেশন UI-তে** বিভিন্ন **উদাহরণ** **দেখাতে** পারেন।

এই OpenAPI-নির্দিষ্ট `examples` ফিল্ডের আকৃতি হলো **একাধিক উদাহরণসহ** একটি `dict` (একটি `list`-এর বদলে), যার প্রতিটিতে অতিরিক্ত তথ্য থাকে যা **OpenAPI**-তেও যোগ হবে।

এটি OpenAPI-তে থাকা প্রতিটি JSON Schema-র ভেতরে যায় না, এটি বাইরে, সরাসরি *পাথ অপারেশনে* যায়।

### `openapi_examples` প্যারামিটার ব্যবহার { #using-the-openapi-examples-parameter }

FastAPI-তে আপনি এগুলোর জন্য `openapi_examples` প্যারামিটার দিয়ে OpenAPI-নির্দিষ্ট `examples` ঘোষণা করতে পারেন:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

`dict`-এর কী-গুলো প্রতিটি উদাহরণকে শনাক্ত করে, আর প্রতিটি ভ্যালু আরেকটি `dict`।

`examples`-এর প্রতিটি নির্দিষ্ট উদাহরণ `dict`-এ থাকতে পারে:

* `summary`: উদাহরণটির সংক্ষিপ্ত বিবরণ।
* `description`: একটি দীর্ঘ বিবরণ, যাতে Markdown টেক্সট থাকতে পারে।
* `value`: এটি হলো দেখানো আসল উদাহরণ, যেমন একটি `dict`।
* `externalValue`: `value`-এর বিকল্প, উদাহরণটির দিকে নির্দেশ করা একটি URL। যদিও `value`-এর মতো এত টুল হয়তো এটি সাপোর্ট করে না।

আপনি এটি এভাবে ব্যবহার করতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial005_an_py310.py hl[23:49] *}

### ডকুমেন্টেশন UI-তে OpenAPI উদাহরণ { #openapi-examples-in-the-docs-ui }

`Body()`-তে `openapi_examples` যোগ করলে `/docs` দেখতে এরকম হবে:

<img src="/img/tutorial/body-fields/image02.png">

## কারিগরি বিবরণ { #technical-details }

/// tip | পরামর্শ

আপনি যদি ইতিমধ্যে **FastAPI** ভার্সন **0.99.0 বা তার ওপরে** ব্যবহার করেন, তাহলে সম্ভবত এই বিবরণগুলো **এড়িয়ে যেতে** পারেন।

এগুলো পুরোনো ভার্সনগুলোর জন্য বেশি প্রাসঙ্গিক, OpenAPI 3.1.0 আসার আগের।

একে আপনি OpenAPI ও JSON Schema-র একটি সংক্ষিপ্ত **ইতিহাসের পাঠ** হিসেবে ধরতে পারেন। 🤓

///

/// warning | সতর্কতা

এগুলো **JSON Schema** ও **OpenAPI** স্ট্যান্ডার্ড সম্পর্কে খুবই কারিগরি বিবরণ।

ওপরের ধারণাগুলো যদি আপনার জন্য ইতিমধ্যে কাজ করে, তাহলে সেটাই যথেষ্ট হতে পারে, এবং সম্ভবত এই বিবরণগুলো আপনার দরকার নেই, নির্দ্বিধায় এড়িয়ে যান।

///

OpenAPI 3.1.0-এর আগে OpenAPI **JSON Schema**-র একটি পুরোনো ও পরিবর্তিত ভার্সন ব্যবহার করত।

JSON Schema-তে `examples` ছিল না, তাই OpenAPI তার নিজের পরিবর্তিত ভার্সনে নিজস্ব `example` ফিল্ড যোগ করেছিল।

OpenAPI স্পেসিফিকেশনের অন্যান্য অংশেও `example` ও `examples` ফিল্ড যোগ করেছিল:

* [`Parameter Object` (স্পেসিফিকেশনে)](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#parameter-object), যা FastAPI-এর এগুলো ব্যবহার করত:
    * `Path()`
    * `Query()`
    * `Header()`
    * `Cookie()`
* [`Request Body Object`, `content` ফিল্ডে, `Media Type Object`-এ (স্পেসিফিকেশনে)](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#media-type-object), যা FastAPI-এর এগুলো ব্যবহার করত:
    * `Body()`
    * `File()`
    * `Form()`

/// note | নোট

এই পুরোনো OpenAPI-নির্দিষ্ট `examples` প্যারামিটারটি FastAPI `0.103.0` থেকে এখন `openapi_examples`।

///

### JSON Schema-র `examples` ফিল্ড { #json-schemas-examples-field }

কিন্তু তারপর JSON Schema স্পেসিফিকেশনের একটি নতুন ভার্সনে একটি [`examples`](https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.9.5) ফিল্ড যোগ করে।

তারপর নতুন OpenAPI 3.1.0 সর্বশেষ ভার্সনের (JSON Schema 2020-12) ওপর ভিত্তি করে তৈরি হয়, যাতে এই নতুন `examples` ফিল্ডটি ছিল।

আর এখন এই নতুন `examples` ফিল্ড পুরোনো একক (এবং কাস্টম) `example` ফিল্ডের চেয়ে অগ্রাধিকার পায়, যা এখন ডেপ্রিকেটেড।

JSON Schema-র এই নতুন `examples` ফিল্ড **শুধু উদাহরণের একটি `list`**, OpenAPI-এর অন্যান্য জায়গার (ওপরে বর্ণিত) মতো অতিরিক্ত মেটাডেটাসহ একটি dict নয়।

/// note | নোট

JSON Schema-র সাথে এই নতুন, সহজতর ইন্টিগ্রেশনসহ OpenAPI 3.1.0 প্রকাশিত হওয়ার পরেও কিছুদিন স্বয়ংক্রিয় ডকুমেন্টেশন দেওয়া টুল Swagger UI OpenAPI 3.1.0 সাপোর্ট করত না (ভার্সন 5.0.0 থেকে করে 🎉)।

এ কারণে 0.99.0-এর আগের FastAPI ভার্সনগুলো তখনও 3.1.0-এর চেয়ে নিচের OpenAPI ভার্সন ব্যবহার করত।

///

### Pydantic ও FastAPI-এর `examples` { #pydantic-and-fastapi-examples }

আপনি যখন `schema_extra` বা `Field(examples=["something"])` ব্যবহার করে একটি Pydantic মডেলের ভেতরে `examples` যোগ করেন, তখন সেই উদাহরণ ওই Pydantic মডেলের **JSON Schema**-তে যোগ হয়।

আর Pydantic মডেলের সেই **JSON Schema** আপনার API-এর **OpenAPI**-তে অন্তর্ভুক্ত হয়, তারপর ডকুমেন্টেশন UI-তে ব্যবহার হয়।

FastAPI-এর 0.99.0-এর আগের ভার্সনগুলোতে (0.99.0 ও তার ওপরের ভার্সনগুলো নতুন OpenAPI 3.1.0 ব্যবহার করে) আপনি যখন অন্য কোনো ইউটিলিটি (`Query()`, `Body()` ইত্যাদি) দিয়ে `example` বা `examples` ব্যবহার করতেন, তখন সেই উদাহরণগুলো ওই ডেটা বর্ণনাকারী JSON Schema-তে যোগ হতো না (এমনকি OpenAPI-এর নিজস্ব JSON Schema ভার্সনেও না), সেগুলো সরাসরি OpenAPI-এর *পাথ অপারেশন* ঘোষণায় যোগ হতো (OpenAPI-এর যে অংশগুলো JSON Schema ব্যবহার করে তার বাইরে)।

কিন্তু এখন যেহেতু FastAPI 0.99.0 ও তার ওপরের ভার্সনগুলো OpenAPI 3.1.0 ব্যবহার করে, যা JSON Schema 2020-12 ব্যবহার করে, এবং Swagger UI 5.0.0 ও তার ওপরের ভার্সন ব্যবহার করে, তাই সবকিছু আরও সামঞ্জস্যপূর্ণ এবং উদাহরণগুলো JSON Schema-তে অন্তর্ভুক্ত থাকে।

### Swagger UI ও OpenAPI-নির্দিষ্ট `examples` { #swagger-ui-and-openapi-specific-examples }

যেহেতু Swagger UI একাধিক JSON Schema উদাহরণ সাপোর্ট করত না (২০২৩-০৮-২৬ পর্যন্ত), তাই ইউজারদের ডকুমেন্টেশনে একাধিক উদাহরণ দেখানোর কোনো উপায় ছিল না।

এর সমাধান করতে FastAPI `0.103.0` নতুন `openapi_examples` প্যারামিটার দিয়ে সেই পুরোনো **OpenAPI-নির্দিষ্ট** `examples` ফিল্ড ঘোষণা করার **সাপোর্ট যোগ করেছে**। 🤓

### সারসংক্ষেপ { #summary }

আমি বলতাম যে ইতিহাস আমার খুব একটা পছন্দ নয়... আর এখন দেখুন, "প্রযুক্তির ইতিহাস"-এর পাঠ দিচ্ছি। 😅

সংক্ষেপে, **FastAPI 0.99.0 বা তার ওপরের ভার্সনে আপগ্রেড করুন**, তাতে সবকিছু অনেক **সহজ, সামঞ্জস্যপূর্ণ ও সহজবোধ্য** হবে, আর এই সব ঐতিহাসিক বিবরণ আপনাকে জানতে হবে না। 😎
