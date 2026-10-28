# Strict Mode { #strict-mode }

/// note | এই পেজে যা শিখবেন

* "lax" (নমনীয়) আর "strict" (কঠোর) মোডের পার্থক্য।
* strict mode চালুর তিনটি উপায়: যাচাইয়ের সময়, নির্দিষ্ট ফিল্ডে, আর পুরো মডেলের কনফিগারেশনে।
* `Strict()`, `StrictInt`, `StrictStr`-এর মতো সহজ টাইপ।
* JSON ইনপুটে strict mode কেন একটু ঢিলে।

///

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.types.Strict`][pydantic.types.Strict]<br>

///

ডিফল্টভাবে, সম্ভব হলে Pydantic মানকে কাঙ্ক্ষিত টাইপে রূপান্তর (coerce) করার চেষ্টা করে।
যেমন, [`int` সংখ্যা টাইপের](../api/standard_library_types.md#integers) ইনপুট হিসেবে `'123'` স্ট্রিং দিলে,
সেটি `123` মানে রূপান্তরিত হবে।
এই রূপান্তর অনেক ক্ষেত্রেই কাজের: ভাবুন UUID, URL প্যারামিটার, HTTP হেডার, environment variable,
তারিখ ইত্যাদির কথা, যেগুলো প্রায় সবসময় লেখা (স্ট্রিং) হিসেবে আসে।

তবে কিছু ক্ষেত্রে এটি কাম্য নয়, আর আপনি চান ডেটা রূপান্তর না করে Pydantic এরর দিক।

এই প্রয়োজন ভালোভাবে মেটাতে Pydantic একটি "strict mode" দেয়। strict mode চালু থাকলে Pydantic ডেটা রূপান্তরে
অনেক কম ছাড় দেয়, আর ডেটা সঠিক টাইপের না হলে এরর দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

lax মোড হলো বন্ধুসুলভ দোকানদার: আপনি "একশ টাকা" লিখে দিলেও তিনি বুঝে নেন ১০০ টাকা। strict মোড হলো ব্যাংকের কাউন্টার: চেকে অঙ্কে ঠিক সংখ্যা না লিখলে ফেরত দেয়। টাকা-পয়সা, অনুমতি, বা অন্য সিস্টেম থেকে আসা ডেটা যেখানে টাইপ ঠিক থাকাটাই জরুরি, সেখানে strict ভালো।

///

বেশিরভাগ সময় strict mode শুধু সেই টাইপের instance-ই গ্রহণ করে, তবে JSON ইনপুটের ক্ষেত্রে নিয়ম কিছুটা ঢিলে হতে পারে
(যেমন, [তারিখ আর সময়ের টাইপ](../api/standard_library_types.md#date-and-time-types) strict mode-এও স্ট্রিং
গ্রহণ করে, কারণ JSON-এ তারিখ লেখার আর কোনো উপায় নেই)।

প্রতিটি টাইপের strict আচরণ পাওয়া যাবে [standard library টাইপ](../api/standard_library_types.md) ডকুমেন্টেশনে,
আর সারসংক্ষেপ আছে [রূপান্তর সারণিতে](./conversion_table.md)।

strict আর ডিফল্ট lax মোডে যাচাইয়ের আচরণের পার্থক্য দেখানো একটি ছোট উদাহরণ:

⟦CODE1⟧

| ইনপুট (`int` ফিল্ডে) | lax | strict |
| --- | --- | --- |
| `123` | `123` | `123` |
| `'123'` | `123` | এরর |
| `123.0` | `123` | এরর |
| `True` | `1` | এরর |

যে অ্যাপ্লিকেশন ইতিমধ্যে চলছে, তার মডেলে strict mode চালুর একটি সতর্কতা: যে ইনপুটগুলো এতদিন চুপচাপ
রূপান্তর হচ্ছিল, সেগুলো এখন ব্যর্থ হতে শুরু করবে। প্রতিটি কলকারী (caller) পরীক্ষা করা সম্ভব না হলে, পরিবর্তনটি চালুর সময়
যাচাই ব্যর্থতার ওপর নজর রাখা কাজে দেয়। [Logfire](../integrations/logfire.md) সফল আর
ব্যর্থ যাচাই metric হিসেবে গোনে, আর গোছানো এররে থাকা প্রত্যাখ্যাত মান রেকর্ড করতে পারে।

strict mode কয়েকভাবে চালু করা যায়:

* [যাচাইয়ের প্যারামিটার হিসেবে](#as-a-validation-parameter), যেমন Pydantic মডেলে [`model_validate()`][pydantic.BaseModel.model_validate]
  ব্যবহারের সময়।
* [ফিল্ড পর্যায়ে](#at-the-field-level)।
* [কনফিগারেশন পর্যায়ে](#as-a-configuration-value) (ফিল্ড পর্যায়ে আবার বদলানোর সুযোগসহ)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#strict-mode-in-method-calls}{% endraw %}

## যাচাইয়ের প্যারামিটার হিসেবে { #as-a-validation-parameter }

[Pydantic মডেল](./models.md) আর [type adapter](./type_adapter.md)-এর [যাচাই মেথড](./models.md#validating-data)
ব্যবহারের সময়, প্রতিটি যাচাইয়ের ডাকে আলাদা করে strict mode চালু করা যায়।

⟦CODE2⟧

1. যেমন বলা হয়েছে, JSON থেকে যাচাইয়ের সময় strict mode বেশি ঢিলে।

/// info | কোডটি সহজ ভাষায়

Python থেকে `'2000-01-01'` স্ট্রিং দিলে strict mode বলে "এটা তো `date` অবজেক্ট নয়", তাই এরর। কিন্তু JSON-এ তারিখ সবসময় স্ট্রিং হিসেবেই আসে, তাই `validate_json` strict mode-এও সেটি গ্রহণ করে।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#strict-mode-with-field}{% endraw %}

## ফিল্ড পর্যায়ে { #at-the-field-level }

নির্দিষ্ট ফিল্ডে strict mode চালু করা যায়, [`Field()`][pydantic.Field] ফাংশনের `strict` প্যারামিটার
`True` করে। [যাচাই মেথড](./models.md#validating-data) lax মোডে ডাকা হলেও
এমন ফিল্ডে strict mode প্রয়োগ হবে।

⟦CODE3⟧

1. strict শর্তটি [annotated pattern](./fields.md#the-annotated-pattern) দিয়েও প্রয়োগ করা যায়:
   `Annotated[int, Field(strict=True)]`

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#strict-mode-with-annotated-strict}{% endraw %}

### `Strict()` metadata ক্লাস ব্যবহার { #using-the-strict-metadata-class }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.types.Strict`][pydantic.types.Strict]<br>

///

[`Field()`][pydantic.Field] ফাংশনের বিকল্প হিসেবে Pydantic [`Strict`][pydantic.types.Strict]
metadata ক্লাস দেয়, যা [annotated pattern](./fields.md#the-annotated-pattern)-এর সাথে ব্যবহারের জন্য। সবচেয়ে প্রচলিত টাইপগুলোর জন্য
সুবিধাজনক alias-ও আছে (যেমন [`StrictBool`][pydantic.types.StrictBool],
[`StrictInt`][pydantic.types.StrictInt], [`StrictFloat`][pydantic.types.StrictFloat], [`StrictStr`][pydantic.types.StrictStr]
আর [`StrictBytes`][pydantic.types.StrictBytes])।

⟦CODE4⟧

1. `Annotated[int, Strict()]`-এর সমান।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#strict-mode-with-configdict}{% endraw %}

## কনফিগারেশন মান হিসেবে { #as-a-configuration-value }

[কনফিগারেশন](./config.md) পর্যায়েও strict mode নিয়ন্ত্রণ করা যায়। Pydantic মডেলে
(বা [dataclass](./dataclasses.md)-এর মতো মডেল-সদৃশ ক্লাসে) ব্যবহার করলেও, [ফিল্ড পর্যায়ে](#at-the-field-level)
কঠোরতা আবার বদলানো যায়:

⟦CODE5⟧

/// info | কোডটি সহজ ভাষায়

পুরো মডেল strict (`ConfigDict(strict=True)`), কিন্তু `age` ফিল্ডে `Field(strict=False)` দিয়ে ছাড় দেওয়া হয়েছে। তাই `age='18'` গ্রহণ হয়ে `18` হলো, অথচ `name`-এ সংখ্যা দিলে এরর হতো।

///

/// check | সংক্ষেপে মনে রাখুন

* ডিফল্ট lax: `'123'` → `123`। strict: ঠিক টাইপ না হলে এরর।
* এক ডাকে: `Model.model_validate(data, strict=True)`।
* এক ফিল্ডে: `Field(strict=True)`, `Annotated[UUID, Strict()]`, বা `StrictInt`/`StrictStr`।
* পুরো মডেলে: `model_config = ConfigDict(strict=True)`, দরকারে ফিল্ডে `Field(strict=False)`।
* JSON ইনপুটে তারিখ, UUID-এর মতো টাইপ strict mode-এও স্ট্রিং হিসেবে গ্রহণযোগ্য।

///
