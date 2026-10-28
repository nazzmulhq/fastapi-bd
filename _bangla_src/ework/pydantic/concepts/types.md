# টাইপ { #types }

/// note | এই পেজে যা শিখবেন

* Pydantic কীভাবে টাইপ দিয়ে যাচাই আর সিরিয়ালাইজেশন নিয়ন্ত্রণ করে।
* কাজের কিছু বিশেষ টাইপ: `OnErrorOmit`, `FailFast`, `MISSING`।
* `Annotated` দিয়ে নিজের পুনরায় ব্যবহারযোগ্য টাইপ বানানো (যেমন "ধনাত্মক integer")।
* নামযুক্ত type alias আর পুনরাবৃত্ত (recursive) টাইপ।
* অ্যাডভান্সড: `__get_pydantic_core_schema__` দিয়ে সম্পূর্ণ নিজস্ব টাইপ, তৃতীয় পক্ষের টাইপ আর generic ক্লাস সামলানো।

শুরুর দিকে "ইউটিলিটি টাইপ" আর "Annotated প্যাটার্ন" অংশ পড়লেই যথেষ্ট; বাকিটা দরকার হলে পড়ুন।

///

যাচাই আর সিরিয়ালাইজেশন কীভাবে হবে তা নির্ধারণ করতে Pydantic টাইপ ব্যবহার করে।
[বিল্ট-ইন আর স্ট্যান্ডার্ড লাইব্রেরির টাইপ](../api/standard_library_types.md) (যেমন [`int`][],
[`str`][], [`date`][datetime.date]) যেমন আছে তেমনই ব্যবহার করা যায়। এগুলোর ওপর [কঠোরতা](./strict_mode.md)
নিয়ন্ত্রণ করা আর শর্ত প্রয়োগ করা যায়।

এগুলোর ওপরে, Pydantic বাড়তি টাইপ দেয়, হয় [সরাসরি লাইব্রেরিতে](../api/types.md)
(যেমন [`SecretStr`][pydantic.types.SecretStr]), নয়তো [`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types)
বাইরের লাইব্রেরিতে। এগুলো [কাস্টম টাইপ](#custom-types) অংশে বর্ণিত প্যাটার্ন ব্যবহার করে বাস্তবায়িত।
এগুলোর ওপর কঠোরতা আর শর্ত প্রয়োগ *করা যায় না*।

[বিল্ট-ইন আর স্ট্যান্ডার্ড লাইব্রেরির টাইপ](../api/standard_library_types.md) ডকুমেন্টেশন
সমর্থিত টাইপগুলো নিয়ে আলোচনা করে: অনুমোদিত মান, সম্ভাব্য যাচাইয়ের শর্ত, আর [কঠোরতা](./strict_mode.md)
কনফিগার করা যায় কিনা।

প্রতিটি টাইপের অনুমোদিত মানের সারসংক্ষেপের জন্য [রূপান্তর সারণি](../concepts/conversion_table.md)-ও দেখুন।

## ইউটিলিটি টাইপ { #utility-types }

যাচাই/সিরিয়ালাইজেশনের আচরণ নিজের মতো করতে Pydantic কয়েকটি কাজের টাইপ/অ্যানোটেশন দেয়।

### `OnErrorOmit` { #onerroromit }

/// info | v2.6-এ যোগ হয়েছে
///

ডিফল্টভাবে, একটি collection-এর (যেমন একটি list, একটি ডিকশনারি বা একটি [`TypedDict`][typing.TypedDict]) একটি আইটেম
যাচাইয়ে ব্যর্থ হলে, একটি [`ValidationError`][pydantic_core.ValidationError] হয় আর পুরো collection-টি
বাতিল হয়। [`OnErrorOmit`][pydantic.types.OnErrorOmit] অ্যানোটেশন এই আচরণ বদলায়: যাচাইয়ে ব্যর্থ যেকোনো আইটেম
নিঃশব্দে ফলাফল থেকে বাদ পড়ে, আর বৈধগুলো থেকে যায়।

⟦CODE1⟧

(`'a'` integer নয়, তাই এররের বদলে চুপচাপ বাদ পড়েছে; বাকি `[1, 2, 3]` থেকে গেছে। অগোছালো ডেটা থেকে যতটুকু ভালো তা নিতে চাইলে এটি কাজের।)

এটি কোথায় প্রয়োগ করা যায় তার আরও বিস্তারিত জানতে [API ডকুমেন্টেশন][pydantic.types.OnErrorOmit] দেখুন।

### `FailFast` { #failfast }

/// info | v2.8-এ যোগ হয়েছে
///

ডিফল্টভাবে, একটি collection যাচাই করার সময় Pydantic প্রতিটি আইটেম যাচাই করে আর সব এরর
একসাথে জানায়। [`FailFast`][pydantic.types.FailFast] অ্যানোটেশন একটি collection টাইপে
(যেমন একটি [`list`][], একটি [`tuple`][], একটি [`set`][] বা একটি [`dict`][]) প্রয়োগ করে প্রথম আইটেম ব্যর্থ হওয়া মাত্রই থামানো যায়।
এতে যাচাই দ্রুত হয়, তবে এররগুলো সম্পর্কে কম তথ্য পান।

⟦CODE2⟧

(তালিকায় `'a'` আর `'b'` দুটোই ভুল, কিন্তু `FailFast` থাকায় শুধু প্রথম এররটি জানানো হয়েছে।)

### `MISSING` sentinel { #missing-sentinel }

⟦CODE3⟧

(`MISSING` হলো একটি বিশেষ চিহ্ন, যা বোঝায় "এই ফিল্ডের মান একেবারেই দেওয়া হয়নি"। এটি `None` থেকে আলাদা: `None` মানে "মান দেওয়া হয়েছে, আর তা খালি"। বিস্তারিত ব্যাখ্যা ওপরের বাক্সে স্বয়ংক্রিয়ভাবে দেখানো হয়েছে।)

## কাস্টম টাইপ { #custom-types }

নিজের কাস্টম টাইপ সংজ্ঞায়িত করার কয়েকটি উপায় আছে।

### Annotated প্যাটার্ন ব্যবহার { #using-the-annotated-pattern }

আপনার কোডবেসজুড়ে টাইপ পুনরায় ব্যবহারযোগ্য করতে [Annotated প্যাটার্ন](./fields.md#the-annotated-pattern) ব্যবহার করা যায়।
যেমন, একটি ধনাত্মক integer বোঝায় এমন একটি টাইপ তৈরি করতে:

⟦CODE4⟧

1. লক্ষ্য করুন, এটিকে Pydantic-নিরপেক্ষ করতে [annotated-types](https://github.com/annotated-types/annotated-types)
  লাইব্রেরির শর্তও ব্যবহার করতে পারেন:

    ⟦CODE5⟧

/// tip | উদাহরণ দিয়ে বুঝি

`PositiveInt = Annotated[int, Field(gt=0)]` একবার লিখলে, এরপর যেকোনো মডেলে `age: PositiveInt`, `count: PositiveInt` লিখলেই একই নিয়ম প্রয়োগ হয়। অনেকটা একটি রাবার স্ট্যাম্প বানিয়ে রাখার মতো: একবার বানান, যতবার খুশি ছাপ দিন।

///

#### যাচাই আর সিরিয়ালাইজেশন যোগ করা { #adding-validation-and-serialization }

Pydantic যেসব মার্কার দেয় সেগুলো ব্যবহার করে যেকোনো টাইপে যাচাই, সিরিয়ালাইজেশন আর JSON schema যোগ বা ওভাররাইড করতে পারেন:

⟦CODE6⟧

/// info | কোডটি সহজ ভাষায়

`TruncatedFloat` একটি float, তিনটি স্টিকারসহ:

* `AfterValidator(...)`: যাচাইয়ের পরে মানটিকে এক দশমিক ঘরে গোল করে (`1.02345` → `1.0`)।
* `PlainSerializer(...)`: আউটপুটে মানটিকে বৈজ্ঞানিক রূপের স্ট্রিং বানায় (`"1.0e+00"`)।
* `WithJsonSchema(...)`: সিরিয়ালাইজেশন মোডের JSON schema-তে টাইপ `string` বলে দেয়, কারণ আউটপুট এখন স্ট্রিং।

///

#### Generic { #generics }

[`Annotated`][typing.Annotated] টাইপের ভেতরে [টাইপ ভেরিয়েবল][typing.TypeVar] ব্যবহার করা যায়:

⟦CODE7⟧

(`ShortList[T]` হলো "সর্বোচ্চ ৪টি উপাদানের তালিকা", যেকোনো টাইপের জন্য; `ShortList[int]` দিলে integer-এর ছোট তালিকা। একইভাবে `PositiveList[float]` মানে ধনাত্মক float-এর তালিকা।)

### নামযুক্ত type alias { #named-type-aliases }

/// info | v2.11-এ যোগ হয়েছে
নামযুক্ত type alias এখন পুরোপুরি সমর্থিত।
///

ওপরের উদাহরণগুলো *অন্তর্নিহিত* (implicit) type alias ব্যবহার করে, যা একটি ভেরিয়েবলে বসানো। চলমান অবস্থায়, Pydantic-এর
জানার কোনো উপায় নেই যে এটি কোন ভেরিয়েবলের নামে বসানো হয়েছিল, আর এটি দুই কারণে
সমস্যা হতে পারে:

* alias-এর [JSON Schema](./json_schema.md) একটি
  [definition](https://json-schema.org/understanding-json-schema/structuring#defs)-এ রূপান্তরিত হবে না।
  এটি মূলত তখন কাজের যখন একটি মডেলের সংজ্ঞায় alias-টি একাধিকবার ব্যবহার করেন।
* বেশিরভাগ ক্ষেত্রে, [পুনরাবৃত্ত type alias](#named-recursive-types) কাজ করবে না।

নতুন [`type` স্টেটমেন্ট](https://typing.readthedocs.io/en/latest/spec/aliases.html#type-statement)
([PEP 695](https://peps.python.org/pep-0695/)-এ আনা) কাজে লাগিয়ে, এভাবে alias সংজ্ঞায়িত করতে পারেন:

/// tab | Python 3.10 ও তার পরে

⟦CODE8⟧

1. যদি `PositiveIntList` একটি অন্তর্নিহিত type alias হিসেবে সংজ্ঞায়িত হতো, তাহলে এর সংজ্ঞা
   `'x'` আর `'y'` দুই জায়গাতেই পুনরাবৃত্ত হতো।

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

⟦CODE9⟧

1. যদি `PositiveIntList` একটি অন্তর্নিহিত type alias হিসেবে সংজ্ঞায়িত হতো, তাহলে এর সংজ্ঞা
   `'x'` আর `'y'` দুই জায়গাতেই পুনরাবৃত্ত হতো।

///

<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#metadata-type-alias-warning}{% endraw %}

//// warning | কখন নামযুক্ত type alias ব্যবহার করবেন

যদিও স্ট্যাটিক টাইপ চেকারের কাছে (নামযুক্ত) PEP 695 alias আর অন্তর্নিহিত type alias সমতুল্য হওয়ার কথা,
Pydantic নামযুক্ত alias-এর ভেতরের ফিল্ড-নির্দিষ্ট মেটাডেটা বুঝবে *না*। অর্থাৎ, `alias`, `default`, `deprecated`-এর মতো মেটাডেটা
ব্যবহার *করা যাবে না*:

/// tab | Python 3.10 ও তার পরে

⟦CODE10⟧

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

⟦CODE11⟧

///

শুধু সেই মেটাডেটা অনুমোদিত যা অ্যানোটেট করা টাইপের নিজের ওপর প্রয়োগ করা যায়
(যেমন [যাচাইয়ের শর্ত](./fields.md#field-constraints) আর JSON মেটাডেটা)।
ফিল্ড-নির্দিষ্ট মেটাডেটা সমর্থন করতে হলে type alias-এর [`__value__`][typing.TypeAliasType.__value__] আগেভাগেই পরীক্ষা করতে হতো,
আর তাহলে Pydantic alias-টিকে একটি JSON Schema definition হিসেবে রাখতে পারত না।

////

//// note | নোট

অন্তর্নিহিত type alias-এর মতোই, generic alias-এর ভেতরেও [টাইপ ভেরিয়েবল][typing.TypeVar] ব্যবহার করা যায়:

/// tab | Python 3.10 ও তার পরে

⟦CODE12⟧

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

⟦CODE13⟧

///

////

#### নামযুক্ত পুনরাবৃত্ত টাইপ { #named-recursive-types }

যখনই পুনরাবৃত্ত (নিজেকেই নির্দেশ করে এমন) type alias সংজ্ঞায়িত করতে হবে, তখন নামযুক্ত type alias ব্যবহার করা উচিত (1)।
{ .annotate }

1. কয়েকটি কারণে, Pydantic অন্তর্নিহিত পুনরাবৃত্ত alias সমর্থন করতে পারে না। যেমন,
   এটি মডিউলগুলোর মধ্যে [forward annotation](./forward_annotations.md) সমাধান করতে পারবে না।

যেমন, এখানে একটি JSON টাইপের উদাহরণ সংজ্ঞা দেওয়া হলো:

/// tab | Python 3.10 ও তার পরে

⟦CODE14⟧

1. অ্যানোটেশনটি উদ্ধৃতিচিহ্নে মুড়ে দেওয়া দরকার, কারণ এটি আগেভাগেই মূল্যায়ন হয়
   (আর `Json` তখনো সংজ্ঞায়িত হয়নি)।

///

/// tab | Python 3.12 ও তার পরে (নতুন সিনট্যাক্স)

⟦CODE15⟧

1. একটি নামযুক্ত type alias-এর মান দেরিতে মূল্যায়ন হয়, তাই forward annotation ব্যবহারের দরকার নেই।

///

(JSON মান নিজেই পুনরাবৃত্ত: একটি JSON অবজেক্টের ভেতরে আবার JSON মান, তালিকার ভেতরে আবার JSON মান। তাই `Json` টাইপটি নিজের নাম নিজের সংজ্ঞায় ব্যবহার করে।)

/// tip | পরামর্শ

সুবিধার জন্য Pydantic একটি [`JsonValue`][pydantic.types.JsonValue] টাইপ সংজ্ঞায়িত করে রেখেছে।

///

### `__get_pydantic_core_schema__` দিয়ে যাচাই নিজের মতো করা <a name="customizing_validation_with_get_pydantic_core_schema"></a> { #customizing-validation-with-get_pydantic_core_schema }

Pydantic কাস্টম ক্লাস কীভাবে সামলায় তা আরও ব্যাপকভাবে নিজের মতো করতে, বিশেষ করে যখন আপনার কাছে
ক্লাসটি আছে বা এর সাব-ক্লাস বানাতে পারেন, তখন Pydantic-কে `pydantic-core` schema কীভাবে তৈরি করতে হবে তা জানাতে একটি বিশেষ
`__get_pydantic_core_schema__` বাস্তবায়ন করতে পারেন।

যদিও যাচাই আর সিরিয়ালাইজেশন সামলাতে `pydantic` ভেতরে `pydantic-core` ব্যবহার করে, এটি Pydantic V2-এর জন্য একটি নতুন API,
তাই এটি ভবিষ্যতে বদলানোর সবচেয়ে বেশি সম্ভাবনাময় জায়গাগুলোর একটি, আর আপনার উচিত যতটা সম্ভব বিল্ট-ইন
গঠনগুলোতেই থাকা, যেমন `annotated-types`, `pydantic.Field`, বা `BeforeValidator` ইত্যাদি যা দেয়।

`__get_pydantic_core_schema__` একটি কাস্টম টাইপে আর `Annotated`-এ রাখার জন্য তৈরি মেটাডেটায়, দুই জায়গাতেই বাস্তবায়ন করতে পারেন।
দুই ক্ষেত্রেই API-টি middleware-এর মতো আর "wrap" validator-এর মতো: আপনি একটি `source_type` পান (যা
অবশ্যই ক্লাসের মতো একই নয়, বিশেষ করে generic-এর ক্ষেত্রে) আর একটি `handler`, যা একটি টাইপসহ কল করে হয়
`Annotated`-এর পরবর্তী মেটাডেটা কল করতে পারেন, নয়তো Pydantic-এর ভেতরের schema তৈরিতে যেতে পারেন।

সবচেয়ে সহজ কিছু-না-করা বাস্তবায়ন দেওয়া টাইপসহ handler কল করে, তারপর তা ফলাফল হিসেবে ফেরত দেয়। আপনি চাইলে
handler কল করার আগে টাইপ বদলাতে পারেন, handler-এর ফেরত দেওয়া core schema বদলাতে পারেন, অথবা handler একেবারেই
কল না করতে পারেন।

#### একটি কাস্টম টাইপের মেথড হিসেবে { #as-a-method-on-a-custom-type }

নিচে এমন একটি টাইপের উদাহরণ, যা কীভাবে যাচাই হবে তা নিজের মতো করতে `__get_pydantic_core_schema__` ব্যবহার করে।
এটি Pydantic V1-এ `__get_validators__` বাস্তবায়নের সমতুল্য।

⟦CODE16⟧

(`Username` হলো `str`-এর একটি সাব-ক্লাস। schema বলে: "আগে সাধারণ `str` হিসেবে যাচাই করো (`handler(str)`), তারপর ফলাফলটি দিয়ে `Username` বানাও"। ফলে যাচাইয়ের পরে আপনি একটি আসল `Username` অবজেক্ট পান।)

কাস্টম টাইপের JSON schema কীভাবে নিজের মতো করবেন তার আরও বিস্তারিত জানতে [JSON Schema](../concepts/json_schema.md) দেখুন।

#### একটি অ্যানোটেশন হিসেবে { #as-an-annotation }

প্রায়ই আপনি শুধু generic টাইপ প্যারামিটারের চেয়েও বেশি কিছু দিয়ে আপনার কাস্টম টাইপ প্যারামিটারাইজ করতে চাইবেন (যা টাইপ সিস্টেম দিয়ে করা যায় আর পরে আলোচনা করা হবে)। অথবা হয়তো আপনার সাব-ক্লাসের একটি ইনস্ট্যান্স বানানোর আসলে দরকার নেই (বা চানও না); আপনি আসলে মূল টাইপটিই চান, শুধু কিছু বাড়তি যাচাইসহ।

যেমন, যদি নিজেই `pydantic.AfterValidator` বাস্তবায়ন করতেন ([যাচাই আর সিরিয়ালাইজেশন যোগ করা](#adding-validation-and-serialization) দেখুন), তাহলে নিচের মতো কিছু করতেন:

⟦CODE17⟧

1. `frozen=True` নির্দিষ্ট করায় `MyAfterValidator` hashable হয়। এটি ছাড়া `Username | None`-এর মতো একটি union এরর দেবে।
2. লক্ষ্য করুন, আগের উদাহরণের মতো টাইপ চেকার `'ABC'`-কে `Username`-এ বসানো নিয়ে আপত্তি করবে না, কারণ তারা `Username`-কে `str` থেকে আলাদা কোনো টাইপ মনে করে না।

#### তৃতীয় পক্ষের টাইপ সামলানো { #handling-third-party-types }

আগের অংশের প্যাটার্নের আরেকটি ব্যবহার হলো তৃতীয় পক্ষের (অন্য লাইব্রেরির) টাইপ সামলানো।

⟦CODE18⟧

এই পদ্ধতি দিয়ে, যেমন Pandas বা Numpy টাইপের আচরণ সংজ্ঞায়িত করতে পারেন।

/// info | কোডটি সহজ ভাষায়

`ThirdPartyType` এমন একটি ক্লাস যা Pydantic-এর কথা ভেবে বানানো হয়নি, আর আমরা এর কোড বদলাতে পারি না। তাই আলাদা একটি "অনুবাদক" ক্লাস (`_ThirdPartyTypePydanticAnnotation`) বানিয়ে `Annotated[ThirdPartyType, ...]`-এ লাগানো হয়েছে। অনুবাদক Pydantic-কে বলে দেয়: integer এলে তা দিয়ে একটি `ThirdPartyType` বানাও, ইতিমধ্যে `ThirdPartyType` হলে যেমন আছে রাখো, আর আউটপুটে শুধু `x` integer-টি লেখো।

///

#### বাড়তি কোড কমাতে `GetPydanticSchema` ব্যবহার { #using-getpydanticschema-to-reduce-boilerplate }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.types.GetPydanticSchema`][pydantic.types.GetPydanticSchema]<br>

///

হয়তো লক্ষ্য করেছেন, ওপরের যে উদাহরণগুলোতে আমরা একটি মার্কার ক্লাস বানাই, সেগুলোতে বেশ কিছু একই ধাঁচের বাড়তি কোড (boilerplate) লাগে।
অনেক সহজ ক্ষেত্রে `pydantic.GetPydanticSchema` ব্যবহার করে এটি অনেক কমিয়ে আনতে পারেন:

⟦CODE19⟧

(আলাদা ক্লাস না বানিয়ে একটি lambda-তেই বলা হয়েছে: স্ট্রিং যাচাইয়ের পরে তাকে দ্বিগুণ করো, তাই `'ab'` → `'abab'`।)

#### সারসংক্ষেপ { #summary }

সংক্ষেপে বলা যাক:

1. `Annotated`-এর মাধ্যমে টাইপ নিজের মতো করতে Pydantic উচ্চ-স্তরের hook দেয়, যেমন `AfterValidator` আর `Field`। সম্ভব হলে এগুলোই ব্যবহার করুন।
2. ভেতরে ভেতরে এগুলো যাচাই নিজের মতো করতে `pydantic-core` ব্যবহার করে, আর `GetPydanticSchema` বা `__get_pydantic_core_schema__`-সহ একটি মার্কার ক্লাস দিয়ে সরাসরি সেখানে যুক্ত হতে পারেন।
3. যদি সত্যিই একটি কাস্টম টাইপ চান, তাহলে টাইপটির নিজের ওপরেই `__get_pydantic_core_schema__` বাস্তবায়ন করতে পারেন।

### কাস্টম generic ক্লাস সামলানো { #handling-custom-generic-classes }

/// warning | সতর্কতা

এটি একটি অ্যাডভান্সড কৌশল, যা শুরুতে আপনার দরকার নাও হতে পারে। বেশিরভাগ
ক্ষেত্রে সম্ভবত স্ট্যান্ডার্ড Pydantic মডেল দিয়েই কাজ চলে যাবে।

///

ফিল্ডের টাইপ হিসেবে
[Generic ক্লাস](https://docs.python.org/3/library/typing.html#typing.Generic) ব্যবহার করে,
`__get_pydantic_core_schema__` দিয়ে "টাইপ প্যারামিটার" (বা সাব-টাইপ)-এর ভিত্তিতে কাস্টম যাচাই করতে পারেন।

আপনি যে Generic ক্লাস সাব-টাইপ হিসেবে ব্যবহার করছেন, তাতে যদি একটি classmethod
`__get_pydantic_core_schema__` থাকে, তাহলে এটি কাজ করাতে
[`arbitrary_types_allowed`][pydantic.config.ConfigDict.arbitrary_types_allowed] ব্যবহারের দরকার নেই।

যেহেতু `source_type` প্যারামিটার `cls` প্যারামিটারের মতো একই নয়, তাই generic প্যারামিটারগুলো বের করতে `typing.get_args` (বা `typing_extensions.get_args`) ব্যবহার করতে পারেন।
তারপর `handler.generate_schema` কল করে সেগুলোর schema তৈরি করতে `handler` ব্যবহার করতে পারেন।
লক্ষ্য করুন, আমরা `handler(get_args(source_type)[0])`-এর মতো কিছু করি না, কারণ আমরা সেই generic প্যারামিটারের জন্য একটি সম্পর্কহীন
schema তৈরি করতে চাই, `Annotated` মেটাডেটা ইত্যাদির বর্তমান প্রসঙ্গ দিয়ে প্রভাবিত নয় এমন।
কাস্টম টাইপের ক্ষেত্রে এটি কম গুরুত্বপূর্ণ, কিন্তু schema তৈরি বদলায় এমন অ্যানোটেট করা মেটাডেটার জন্য অত্যন্ত জরুরি।

⟦CODE20⟧

(`Owner[ItemType]` একটি সাধারণ dataclass, Pydantic মডেল নয়। এর `__get_pydantic_core_schema__` `get_args` দিয়ে জেনে নেয় `ItemType` আসলে কী (যেমন `Owner[int]` হলে `int`), তারপর `item` ফিল্ডটি সেই টাইপ অনুযায়ী যাচাই করে।)

#### Generic container { #generic-containers }

একই ধারণা প্রয়োগ করে generic container টাইপ তৈরি করা যায়, যেমন একটি কাস্টম `Sequence` টাইপ:

⟦CODE21⟧

### ফিল্ডের নাম পাওয়া { #access-to-field-name }

/// note | নোট

এটি Pydantic V2 থেকে V2.3 পর্যন্ত সম্ভব ছিল না, Pydantic V2.4-এ এটি [আবার যোগ করা হয়েছে](https://github.com/pydantic/pydantic/pull/7542)।

///

Pydantic V2.4 থেকে, `__get_pydantic_core_schema__`-এর ভেতরে `handler.field_name` দিয়ে ফিল্ডের নাম পেতে পারেন,
আর এর মাধ্যমে ফিল্ডের নাম সেট করতে পারেন, যা `info.field_name` থেকে পাওয়া যাবে।

⟦CODE22⟧

`Annotated`-এর সাথে ব্যবহৃত মার্কার থেকেও `field_name` পেতে পারেন, যেমন [`AfterValidator`][pydantic.functional_validators.AfterValidator]।

⟦CODE23⟧

/// check | সংক্ষেপে মনে রাখুন

* সাধারণ Python টাইপ (`int`, `str`, `date` ...) সরাসরি চলে; Pydantic বাড়তি টাইপও দেয় (`SecretStr`, `EmailStr` ...)।
* খারাপ আইটেম বাদ দিতে `OnErrorOmit`, প্রথম এররেই থামতে `FailFast`।
* নিজের পুনরায় ব্যবহারযোগ্য টাইপ: `MyType = Annotated[int, Field(gt=0), AfterValidator(...)]`।
* JSON-এর মতো পুনরাবৃত্ত টাইপের জন্য নামযুক্ত type alias (`TypeAliasType` বা `type` স্টেটমেন্ট)।
* সম্পূর্ণ নিজস্ব আচরণ দরকার হলে শেষ ভরসা `__get_pydantic_core_schema__`।

///
