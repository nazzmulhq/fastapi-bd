# রিকোয়েস্টের উদাহরণ ডেটা ঘোষণা { #declare-request-example-data }

/// note | এই পেজে যা শিখবেন

* `/docs`-এ ক্লায়েন্টদের জন্য নমুনা (উদাহরণ) ডেটা কীভাবে দেখাবেন।
* মডেলে (`model_config`), ফিল্ডে (`Field`) আর প্যারামিটারে (`Body` ইত্যাদি) উদাহরণ দেওয়ার উপায়।
* `openapi_examples` দিয়ে ডকুমেন্টেশনে একাধিক নাম দেওয়া উদাহরণ দেখানো।
* `example` আর `examples`-এর ইতিহাস (ঐচ্ছিক)।

///

আপনার অ্যাপ কী ধরনের ডেটা গ্রহণ করতে পারে তার উদাহরণ ঘোষণা করতে পারেন।

কেন দরকার? আপনার API যারা ব্যবহার করবে (যেমন ফ্রন্টএন্ড ডেভেলপার), তারা `/docs`-এ গিয়ে সাথে সাথে দেখতে পাবে কেমন ডেটা পাঠাতে হবে। "Try it out" চাপলে বক্সে আগে থেকেই সেই উদাহরণ বসানো থাকবে, শুধু Execute চাপলেই হবে।

এখানে এটি করার কয়েকটি উপায় দেওয়া হলো।

## Pydantic মডেলে বাড়তি JSON Schema ডেটা { #extra-json-schema-data-in-pydantic-models }

একটি Pydantic মডেলের জন্য `examples` ঘোষণা করতে পারেন, যা তৈরি হওয়া JSON Schema-তে যোগ হবে।

{* ../../docs_src/schema_extra_example/tutorial001_py310.py hl[13:24] *}

ওই বাড়তি তথ্য মডেলটির আউটপুট **JSON Schema**-তে যেমন আছে তেমনই যোগ হবে, এবং API ডকুমেন্টেশনে ব্যবহার হবে।

/// info | কোডটি সহজ ভাষায়

* লাইন ১৩: `model_config` হলো মডেলের সেটিংস রাখার একটি বিশেষ অ্যাট্রিবিউট (একটি ডিকশনারি)।
* লাইন ১৪: `"json_schema_extra"` মানে "JSON Schema-তে এই বাড়তি জিনিসগুলো যোগ করো"।
* লাইন ১৫-২২: `"examples"` হলো উদাহরণের একটি তালিকা, এখানে একটিমাত্র উদাহরণ: `Foo` নামের একটি পণ্য।

এটি শুধু ডকুমেন্টেশনের জন্য। যাচাইয়ের নিয়মে কোনো পরিবর্তন হয় না।

///

[Pydantic-এর ডকুমেন্টেশন: Configuration](https://pydantic.dev/docs/validation/latest/api/pydantic/config/)-এ বর্ণিত `model_config` অ্যাট্রিবিউটটি ব্যবহার করতে পারেন, যা একটি `dict` নেয়।

`"json_schema_extra"`-তে এমন একটি `dict` দিতে পারেন, যাতে তৈরি হওয়া JSON Schema-তে আপনি যা দেখাতে চান এমন যেকোনো বাড়তি ডেটা থাকে, `examples`-সহ।

/// tip | পরামর্শ

একই কৌশলে JSON Schema বাড়িয়ে নিজের কাস্টম বাড়তি তথ্যও যোগ করতে পারেন।

যেমন একটি ফ্রন্টএন্ড ইউজার ইন্টারফেসের জন্য মেটাডেটা যোগ করতে এটি ব্যবহার করতে পারেন।

///

/// note | নোট

OpenAPI 3.1.0 (FastAPI 0.99.0 থেকে ব্যবহৃত) `examples`-এর সাপোর্ট যোগ করেছে, যা **JSON Schema** স্ট্যান্ডার্ডের অংশ।

এর আগে এটি কেবল একটিমাত্র উদাহরণসহ `example` কিওয়ার্ড সাপোর্ট করত। OpenAPI 3.1.0 এখনো সেটি সাপোর্ট করে, তবে এটি deprecated আর JSON Schema স্ট্যান্ডার্ডের অংশ নয়। তাই `example` থেকে `examples`-এ চলে যাওয়ার জন্য উৎসাহিত করা হয়। 🤓

এই পেজের শেষে এ নিয়ে আরও পড়তে পারেন।

///

## `Field`-এর বাড়তি আর্গুমেন্ট { #field-additional-arguments }

Pydantic মডেলে `Field()` ব্যবহার করার সময় বাড়তি `examples`-ও ঘোষণা করতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial002_py310.py hl[2,8:11] *}

এখানে প্রতিটি ফিল্ডের জন্য আলাদা আলাদা উদাহরণ দেওয়া হয়েছে, যেমন `name`-এর উদাহরণ `"Foo"`, `price`-এর উদাহরণ `35.4`। ডকুমেন্টেশন এগুলো জুড়ে একটি পূর্ণ উদাহরণ দেখাবে।

## JSON Schema-তে `examples` - OpenAPI { #examples-in-json-schema-openapi }

এগুলোর যেকোনোটি ব্যবহার করার সময়:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

বাড়তি তথ্যসহ একগুচ্ছ `examples`-ও ঘোষণা করতে পারেন, যা **OpenAPI**-এর ভেতরে এদের **JSON Schema**-তে যোগ হবে।

### `examples`-সহ `Body` { #body-with-examples }

এখানে আমরা `Body()`-তে প্রত্যাশিত ডেটার একটি উদাহরণসহ `examples` দিচ্ছি:

{* ../../docs_src/schema_extra_example/tutorial003_an_py310.py hl[22:29] *}

### ডকুমেন্টেশন UI-তে উদাহরণ { #example-in-the-docs-ui }

ওপরের যেকোনো পদ্ধতিতে `/docs`-এ এটি দেখতে এমন হবে:

<img src="/img/tutorial/body-fields/image01.png">

### একাধিক `examples`-সহ `Body` { #body-with-multiple-examples }

অবশ্যই একাধিক `examples`-ও দিতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial004_an_py310.py hl[23:38] *}

এটি করলে উদাহরণগুলো ওই বডি ডেটার অভ্যন্তরীণ **JSON Schema**-র অংশ হবে।

তবে <dfn title="২০২৩-০৮-২৬">এটি লেখার সময়</dfn> Swagger UI, যা ডকুমেন্টেশন UI দেখানোর দায়িত্বে, **JSON Schema**-তে ডেটার একাধিক উদাহরণ দেখানো সাপোর্ট করে না। তবে একটি বিকল্প সমাধানের জন্য নিচে পড়ুন।

### OpenAPI-নির্দিষ্ট `examples` { #openapi-specific-examples }

**JSON Schema** `examples` সাপোর্ট করার আগে থেকেই OpenAPI-তে ভিন্ন একটি ফিল্ডের সাপোর্ট ছিল, যার নামও `examples`।

এই **OpenAPI-নির্দিষ্ট** `examples` OpenAPI স্পেসিফিকেশনের আরেকটি অংশে থাকে। এটি থাকে **প্রতিটি *পাথ অপারেশনের* বিবরণে**, প্রতিটি JSON Schema-র ভেতরে নয়।

আর Swagger UI অনেকদিন ধরেই এই নির্দিষ্ট `examples` ফিল্ডটি সাপোর্ট করে। তাই **ডকুমেন্টেশন UI-তে** বিভিন্ন **উদাহরণ** **দেখাতে** এটি ব্যবহার করতে পারেন।

এই OpenAPI-নির্দিষ্ট `examples` ফিল্ডের আকার হলো **একাধিক উদাহরণসহ** একটি `dict` (`list`-এর বদলে), যার প্রতিটিতে বাড়তি তথ্য থাকে যা **OpenAPI**-তেও যোগ হবে।

এটি OpenAPI-এর ভেতরের প্রতিটি JSON Schema-র ভেতরে যায় না, বাইরে যায়, সরাসরি *পাথ অপারেশনে*।

### `openapi_examples` প্যারামিটার ব্যবহার { #using-the-openapi-examples-parameter }

FastAPI-তে OpenAPI-নির্দিষ্ট `examples` ঘোষণা করতে পারেন `openapi_examples` প্যারামিটার দিয়ে, এগুলোর জন্য:

* `Path()`
* `Query()`
* `Header()`
* `Cookie()`
* `Body()`
* `Form()`
* `File()`

`dict`-এর কী-গুলো প্রতিটি উদাহরণকে চিহ্নিত করে, আর প্রতিটি মান আরেকটি `dict`।

`examples`-এর প্রতিটি নির্দিষ্ট উদাহরণ `dict`-এ থাকতে পারে:

* `summary`: উদাহরণটির ছোট বিবরণ।
* `description`: একটি লম্বা বিবরণ, যাতে Markdown টেক্সট থাকতে পারে।
* `value`: এটিই আসল দেখানো উদাহরণ, যেমন একটি `dict`।
* `externalValue`: `value`-এর বিকল্প, উদাহরণের দিকে নির্দেশ করা একটি URL। তবে এটি হয়তো `value`-এর মতো এত টুলে সাপোর্টেড নয়।

এভাবে ব্যবহার করতে পারেন:

{* ../../docs_src/schema_extra_example/tutorial005_an_py310.py hl[23:49] *}

/// info | কোডটি সহজ ভাষায়

তিনটি নাম দেওয়া উদাহরণ:

* `"normal"`: একটি সাধারণ, সঠিক পণ্য। সব ঠিকঠাক চলে।
* `"converted"`: দাম পাঠানো হয়েছে টেক্সট `"35.4"` হিসেবে। FastAPI নিজেই এটিকে সংখ্যায় রূপান্তর করে, তাই এটিও সফল হয়।
* `"invalid"`: দাম `"thirty five point four"`, যা সংখ্যায় রূপান্তর করা যায় না, তাই এরর।

এভাবে ডকুমেন্টেশনেই ক্লায়েন্টদের দেখিয়ে দেওয়া যায় কোনটা চলবে আর কোনটা চলবে না।

///

### ডকুমেন্টেশন UI-তে OpenAPI উদাহরণ { #openapi-examples-in-the-docs-ui }

`Body()`-তে `openapi_examples` যোগ করলে `/docs` দেখতে এমন হবে:

<img src="/img/tutorial/body-fields/image02.png">

এখানে একটি ড্রপডাউন থেকে উদাহরণ বেছে নেওয়া যায়।

## কারিগরি বিবরণ { #technical-details }

/// tip | পরামর্শ

আপনি যদি ইতিমধ্যে **FastAPI** সংস্করণ **0.99.0 বা তার ওপরে** ব্যবহার করেন, তাহলে সম্ভবত এই বিবরণ **বাদ দিতে** পারেন।

এগুলো পুরোনো সংস্করণের জন্য বেশি প্রাসঙ্গিক, OpenAPI 3.1.0 আসার আগের।

এটিকে OpenAPI আর JSON Schema-র একটি ছোট্ট **ইতিহাসের পাঠ** ভাবতে পারেন। 🤓

///

/// warning | সতর্কতা

এগুলো **JSON Schema** ও **OpenAPI** স্ট্যান্ডার্ড নিয়ে খুবই কারিগরি বিবরণ।

ওপরের ধারণাগুলো যদি আপনার কাজে লেগে যায়, তাহলে সেটুকুই যথেষ্ট হতে পারে, আর সম্ভবত এই বিবরণের দরকার নেই, নির্দ্বিধায় বাদ দিন।

///

OpenAPI 3.1.0-এর আগে OpenAPI **JSON Schema**-র একটি পুরোনো ও পরিবর্তিত সংস্করণ ব্যবহার করত।

JSON Schema-তে `examples` ছিল না, তাই OpenAPI তার নিজের পরিবর্তিত সংস্করণে নিজস্ব `example` ফিল্ড যোগ করেছিল।

OpenAPI স্পেসিফিকেশনের অন্য অংশেও `example` আর `examples` ফিল্ড যোগ করেছিল:

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

কিন্তু তারপর JSON Schema তার স্পেসিফিকেশনের একটি নতুন সংস্করণে একটি [`examples`](https://json-schema.org/draft/2019-09/json-schema-validation.html#rfc.section.9.5) ফিল্ড যোগ করে।

আর তারপর নতুন OpenAPI 3.1.0 সর্বশেষ সংস্করণের (JSON Schema 2020-12) ওপর ভিত্তি করে তৈরি হয়, যাতে এই নতুন `examples` ফিল্ডটি ছিল।

আর এখন এই নতুন `examples` ফিল্ড পুরোনো একক (এবং কাস্টম) `example` ফিল্ডের চেয়ে অগ্রাধিকার পায়, যা এখন deprecated।

JSON Schema-র এই নতুন `examples` ফিল্ড **শুধু উদাহরণের একটি `list`**, OpenAPI-এর অন্য জায়গাগুলোর (ওপরে বর্ণিত) মতো বাড়তি মেটাডেটাসহ dict নয়।

/// note | নোট

JSON Schema-র সাথে এই নতুন সহজ একীকরণসহ OpenAPI 3.1.0 প্রকাশিত হওয়ার পরেও কিছুদিন Swagger UI, যা স্বয়ংক্রিয় ডকুমেন্টেশন দেয়, OpenAPI 3.1.0 সাপোর্ট করত না (সংস্করণ 5.0.0 থেকে করে 🎉)।

এ কারণে 0.99.0-এর আগের FastAPI সংস্করণগুলো তখনও 3.1.0-এর চেয়ে নিচের OpenAPI সংস্করণ ব্যবহার করত।

///

### Pydantic ও FastAPI-এর `examples` { #pydantic-and-fastapi-examples }

`schema_extra` বা `Field(examples=["something"])` ব্যবহার করে একটি Pydantic মডেলের ভেতরে `examples` যোগ করলে, সেই উদাহরণ ওই Pydantic মডেলের **JSON Schema**-তে যোগ হয়।

আর Pydantic মডেলের সেই **JSON Schema** আপনার API-এর **OpenAPI**-তে অন্তর্ভুক্ত হয়, তারপর ডকুমেন্টেশন UI-তে ব্যবহার হয়।

0.99.0-এর আগের FastAPI সংস্করণগুলোতে (0.99.0 ও তার ওপরেরগুলো নতুন OpenAPI 3.1.0 ব্যবহার করে), অন্য কোনো টুলের (`Query()`, `Body()` ইত্যাদি) সাথে `example` বা `examples` ব্যবহার করলে সেই উদাহরণগুলো ওই ডেটা বর্ণনাকারী JSON Schema-তে যোগ হতো না (এমনকি OpenAPI-এর নিজস্ব JSON Schema সংস্করণেও না)। সেগুলো সরাসরি OpenAPI-এর *পাথ অপারেশন* ঘোষণায় যোগ হতো (OpenAPI-এর যেসব অংশ JSON Schema ব্যবহার করে তার বাইরে)।

কিন্তু এখন FastAPI 0.99.0 ও তার ওপরে OpenAPI 3.1.0 ব্যবহার করে, যা JSON Schema 2020-12 ব্যবহার করে, আর Swagger UI 5.0.0 ও তার ওপরে, তাই সবকিছু আরও সামঞ্জস্যপূর্ণ, আর উদাহরণগুলো JSON Schema-তে অন্তর্ভুক্ত হয়।

### Swagger UI ও OpenAPI-নির্দিষ্ট `examples` { #swagger-ui-and-openapi-specific-examples }

এখন, যেহেতু Swagger UI একাধিক JSON Schema উদাহরণ সাপোর্ট করত না (২০২৩-০৮-২৬ অনুযায়ী), তাই ব্যবহারকারীদের ডকুমেন্টেশনে একাধিক উদাহরণ দেখানোর কোনো উপায় ছিল না।

এটি সমাধান করতে FastAPI `0.103.0` নতুন প্যারামিটার `openapi_examples` দিয়ে সেই পুরোনো **OpenAPI-নির্দিষ্ট** `examples` ফিল্ড ঘোষণার **সাপোর্ট যোগ করেছে**। 🤓

### সারাংশ { #summary }

আমি বলতাম ইতিহাস আমার তেমন পছন্দ নয়... আর এখন দেখুন, "প্রযুক্তির ইতিহাস" পড়াচ্ছি। 😅

সংক্ষেপে, **FastAPI 0.99.0 বা তার ওপরে আপগ্রেড করুন**, তাহলে সবকিছু অনেক **সহজ, সামঞ্জস্যপূর্ণ আর সহজবোধ্য**, আর এই সব ঐতিহাসিক খুঁটিনাটি জানতে হবে না। 😎

/// check | সংক্ষেপে মনে রাখুন

* উদাহরণ শুধু ডকুমেন্টেশনের জন্য, যাচাইয়ের নিয়ম বদলায় না।
* পুরো মডেলের উদাহরণ: `model_config = {"json_schema_extra": {"examples": [...]}}`।
* প্রতিটি ফিল্ডের উদাহরণ: `Field(examples=[...])`।
* প্যারামিটারে উদাহরণ: `Body(examples=[...])`, `Query(examples=[...])` ইত্যাদি।
* `/docs`-এ ড্রপডাউনে একাধিক নাম দেওয়া উদাহরণ দেখাতে: `openapi_examples={...}`।

///
