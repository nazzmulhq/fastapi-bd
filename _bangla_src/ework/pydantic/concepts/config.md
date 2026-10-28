# Configuration { #configuration }

/// note | এই পেজে যা শিখবেন

* মডেল, dataclass, `TypeAdapter`, TypedDict আর `@validate_call`-এ কীভাবে configuration (সেটিং) দিতে হয়।
* পুরো প্রজেক্টে একই সেটিং চালু করতে একটি প্যারেন্ট মডেল বানানো।
* নেস্টেড মডেলে configuration কখন ছড়ায় আর কখন ছড়ায় না।

///

Pydantic-এর আচরণ বিভিন্ন configuration মান দিয়ে নিয়ন্ত্রণ করা যায়, যেগুলো
[`ConfigDict`][pydantic.ConfigDict] ক্লাসে ডকুমেন্ট করা আছে। এই পেজ বর্ণনা করে Pydantic-এর সমর্থিত টাইপগুলোতে কীভাবে
configuration নির্দিষ্ট করা যায়।

/// tip | উদাহরণ দিয়ে বুঝি

configuration হলো মডেলের "সেটিংস মেনু", যেমন ফোনের সেটিংসে ভাষা, ফন্টের আকার বেছে নেন। `ConfigDict(str_max_length=5)` মানে "এই মডেলের সব স্ট্রিং ৫ অক্ষরের মধ্যে", `ConfigDict(extra='forbid')` মানে "বাড়তি ফিল্ড নিষেধ"। পূর্ণ তালিকা দেখুন [`ConfigDict`][pydantic.ConfigDict]-এর API পেজে।

///

## Pydantic মডেলে configuration { #configuration-on-pydantic-models }

Pydantic মডেলে configuration দুইভাবে নির্দিষ্ট করা যায়:

* [`model_config`][pydantic.BaseModel.model_config] ক্লাস অ্যাট্রিবিউট ব্যবহার করে:

    ⟦CODE1⟧

    1. একটি সাধারণ ডিকশনারি (যেমন `{'str_max_length': 5}`)-ও ব্যবহার করা যায়।

    /// note | নোট

    Pydantic V1-এ `Config` ক্লাস ব্যবহার হতো। এটি এখনো সমর্থিত, কিন্তু **deprecated**।

    ///

* ক্লাস আর্গুমেন্ট ব্যবহার করে:

    ⟦CODE2⟧

  [`model_config`][pydantic.BaseModel.model_config] ক্লাস অ্যাট্রিবিউটের মতো নয়,
  স্ট্যাটিক টাইপ চেকার ক্লাস আর্গুমেন্ট চিনতে পারে। `frozen`-এর ক্ষেত্রে, ইনস্ট্যান্সে যেকোনো
  পরিবর্তন টাইপ চেকিং এরর হিসেবে চিহ্নিত হবে।

## Pydantic dataclass-এ configuration { #configuration-on-pydantic-dataclasses }

[Pydantic dataclass](./dataclasses.md)-ও configuration সমর্থন করে (আরও পড়ুন
[নির্দিষ্ট অংশে](./dataclasses.md#dataclass-config))।

⟦CODE3⟧

(`validate_assignment=True` থাকায় তৈরির পরে মান বসানোর সময়ও যাচাই হয়, তাই ২০ অক্ষরের নাম বসাতে গেলে এরর।)

## `TypeAdapter`-এ configuration { #configuration-on-typeadapter }

[Type adapter](./type_adapter.md) ([`TypeAdapter`][pydantic.TypeAdapter] ক্লাস ব্যবহার করে) `config` আর্গুমেন্ট দিয়ে
configuration সমর্থন করে।

⟦CODE4⟧

যদি type adapter সরাসরি এমন একটি টাইপ মোড়ায় যা নিজেই configuration সমর্থন করে, তাহলে configuration দেওয়া যায় না, আর এই ক্ষেত্রে একটি
[ব্যবহারের এরর](../errors/usage_errors.md) হয়।
[configuration ছড়ানোর](#configuration-propagation) নিয়মগুলোও প্রযোজ্য।

## অন্যান্য সমর্থিত টাইপে configuration { #configuration-on-other-supported-types }

যদি [স্ট্যান্ডার্ড লাইব্রেরির dataclass][dataclasses] বা [`TypedDict`][typing.TypedDict] ক্লাস ব্যবহার করেন,
তাহলে configuration দুইভাবে সেট করা যায়:

* `__pydantic_config__` ক্লাস অ্যাট্রিবিউট ব্যবহার করে:

    ⟦CODE5⟧

* [`@with_config`][pydantic.config.with_config] ডেকোরেটর ব্যবহার করে (এতে [`TypedDict`][typing.TypedDict]-এর সাথে
  স্ট্যাটিক টাইপ চেকিং এরর এড়ানো যায়):

    ⟦CODE6⟧

## `@validate_call` ডেকোরেটরে configuration { #configuration-on-the-validate_call-decorator }

[`@validate_call`](./validation_decorator.md)-ও কাস্টম configuration সেট করা সমর্থন করে। আরও বিস্তারিত জানতে
[নির্দিষ্ট অংশ](./validation_decorator.md#custom-configuration) দেখুন।

## পুরো প্রজেক্টে আচরণ বদলানো { #change-behaviour-globally }

যদি Pydantic-এর আচরণ সব জায়গায় একসাথে বদলাতে চান, তাহলে একটি কাস্টম configuration-সহ নিজের প্যারেন্ট ক্লাস
তৈরি করতে পারেন, কারণ configuration উত্তরাধিকারসূত্রে আসে:

⟦CODE7⟧

যদি সাব-ক্লাসে configuration দেন, তাহলে তা প্যারেন্টের configuration-এর সাথে *মিলিয়ে দেওয়া* হবে:

⟦CODE8⟧

(প্যারেন্টের `extra='allow'` থেকে গেছে, আর সাব-ক্লাসের `str_to_lower=True` প্যারেন্টের `False`-কে বদলে দিয়েছে। তাই `'FOO'` → `'foo'`।)

/// tip | উদাহরণ দিয়ে বুঝি

একটি প্রজেক্টে সাধারণত একটি `class AppModel(BaseModel)` বানিয়ে তাতে `model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)` এর মতো সেটিং দেওয়া হয়, আর বাকি সব মডেল `AppModel` থেকে উত্তরাধিকার নেয়। এতে এক জায়গায় বদলালেই সব মডেলে প্রয়োগ হয়।

///

/// warning | সতর্কতা

যদি আপনার মডেল একাধিক বেস থেকে উত্তরাধিকার নেয়, তাহলে Pydantic বর্তমানে
[MRO] (method resolution order, অর্থাৎ Python কোন ক্রমে প্যারেন্ট ক্লাস খোঁজে) মেনে চলে *না*। আরও বিস্তারিত জানতে [এই issue](https://github.com/pydantic/pydantic/issues/9992) দেখুন।

[MRO]: https://docs.python.org/3/glossary.html#term-method-resolution-order

///

## Plugin সেটিং { #plugin-settings }

[`plugin_settings`][pydantic.ConfigDict.plugin_settings] configuration মান
Pydantic plugin-এ (এমন কোড যা যাচাইয়ে যুক্ত হয়, সাধারণত যাচাই পর্যবেক্ষণকারী টুলের জন্য, যাচাইয়ের আচরণ
বদলানোর জন্য নয়) অপশন পাঠায়। এর মান হলো plugin-এর নাম অনুযায়ী key-সহ একটি ডিকশনারি, তাই প্রতিটি plugin
শুধু নিজের অংশটি পড়ে।

আজ ব্যবহৃত প্রধান plugin হলো [Logfire](../integrations/logfire.md)-এর, যা observability-র জন্য যাচাই রেকর্ড করে।
প্রতিটি মডেলের জন্য এটি কী রেকর্ড করবে তা ঠিক করতে পারেন, যেমন একটি নির্দিষ্ট মডেলের জন্য শুধু ব্যর্থতা
রেকর্ড করা:

⟦CODE9⟧

## configuration ছড়ানো (propagation) { #configuration-propagation }

configuration সমর্থন করে এমন টাইপ ফিল্ডের অ্যানোটেশন হিসেবে ব্যবহার করলে, configuration নাও ছড়াতে পারে:

* Pydantic মডেল আর dataclass-এর ক্ষেত্রে, configuration ছড়াবে *না*, প্রতিটি মডেলের নিজস্ব
  "configuration সীমানা" আছে:

    ⟦CODE10⟧

* stdlib টাইপের (dataclass আর typed dictionary) ক্ষেত্রে, configuration ছড়াবে, যদি না
  টাইপটির নিজস্ব configuration সেট করা থাকে:

    ⟦CODE11⟧

/// info | কোড দুটি সহজ ভাষায়

* প্রথম উদাহরণে `Parent`-এর `str_to_lower=True` ভেতরের `User` মডেলে পৌঁছায়নি, তাই `'JOHN'` বড় হাতেই থেকে গেছে। প্রতিটি `BaseModel` নিজের সেটিং নিজেই রাখে।
* দ্বিতীয় উদাহরণে সাধারণ dataclass `UserWithoutConfig`-এর নিজের কোনো সেটিং নেই, তাই প্যারেন্টের সেটিং পেয়েছে (`'john'`); কিন্তু `UserWithConfig`-এর নিজের সেটিং আছে, তাই সেটিই প্রযোজ্য (`'JOHN'`)।

///

/// check | সংক্ষেপে মনে রাখুন

* মডেলে: `model_config = ConfigDict(...)` অথবা `class M(BaseModel, frozen=True)`।
* dataclass-এ `@dataclass(config=...)`, `TypeAdapter`-এ `config=...`, TypedDict-এ `@with_config(...)`।
* প্রজেক্টজুড়ে একই সেটিং: একটি প্যারেন্ট মডেল বানান; সাব-ক্লাসের সেটিং প্যারেন্টের সাথে মিলে যায়।
* নেস্টেড `BaseModel`-এ প্যারেন্টের সেটিং পৌঁছায় না।

///
