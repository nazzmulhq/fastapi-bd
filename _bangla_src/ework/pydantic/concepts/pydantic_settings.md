
# Settings Management { #settings-management }

/// note | এই পেজে যা শিখবেন

* `pydantic-settings` দিয়ে environment variable, `.env` ফাইল, secret ফাইল, কমান্ড লাইন আর ক্লাউডের secret store থেকে অ্যাপের সেটিংস পড়া ও যাচাই করা।
* environment variable-এর নাম কীভাবে ঠিক হয় (prefix, alias, বড়-ছোট হাতের অক্ষর), আর জটিল মান (তালিকা, ডিকশনারি, নেস্টেড মডেল) কীভাবে পড়া হয়।
* CLI অ্যাপ বানানো, একাধিক উৎসের অগ্রাধিকার, নিজের উৎস যোগ করা, আর সেটিংস cache করা।

///

/// tip | উদাহরণ দিয়ে বুঝি

অ্যাপের সেটিংস (ডেটাবেসের ঠিকানা, API key, debug চালু কিনা) কোডে সরাসরি লিখে রাখা মানে দরজার চাবি দরজাতেই ঝুলিয়ে রাখা। `BaseSettings` হলো একটি নিরাপদ চাবির বাক্স: চাবিগুলো থাকে বাইরে (environment variable, `.env` ফাইল, secret), আর অ্যাপ চালুর সময় বাক্সটি সেগুলো সংগ্রহ করে, মিলিয়ে দেখে (যাচাই করে), তারপর আপনার হাতে দেয়। ভুল চাবি (যেমন পোর্টে `"abc"`) থাকলে অ্যাপ চালুর সময়েই জানিয়ে দেয়।

///

[Pydantic Settings](https://github.com/pydantic/pydantic-settings) environment variable বা secret ফাইল থেকে একটি settings বা config ক্লাস লোড করার জন্য ঐচ্ছিক Pydantic সুবিধা দেয়।

সেটিংস environment variable আর secret ফাইল থেকে যাচাই হয়, তাই এখানে একটি
[`ValidationError`][pydantic_core.ValidationError] মানে কোনো environment মান তার ফিল্ডের সাথে
মেলেনি। [Logfire](../errors/troubleshooting.md) ব্যর্থ যাচাই আর তাদের গোছানো
এরর রেকর্ড করতে পারে, ফলে কোন সেটিং কেন ব্যর্থ হলো তা দেখতে পারবেন।

## ইনস্টলেশন { #installation }

ইনস্টল করা খুবই সহজ:

```bash
pip install pydantic-settings
```

## ব্যবহার { #usage }

`BaseSettings` থেকে উত্তরাধিকার নেওয়া একটি মডেল তৈরি করলে, keyword আর্গুমেন্ট হিসেবে দেওয়া হয়নি এমন যেকোনো ফিল্ডের মান
মডেলের initialiser environment থেকে পড়ে বের করার চেষ্টা করবে। (মিলে যাওয়া environment variable সেট না থাকলে
ডিফল্ট মানই ব্যবহার হবে।)

এতে সহজ হয়:

* পরিষ্কারভাবে সংজ্ঞায়িত, টাইপ-hint সহ অ্যাপ্লিকেশন কনফিগারেশন ক্লাস তৈরি
* environment variable থেকে কনফিগারেশনের পরিবর্তন স্বয়ংক্রিয়ভাবে পড়া
* দরকারে initialiser-এ হাতে নির্দিষ্ট সেটিং বদলানো (যেমন unit test-এ)

যেমন:

⟦CODE1⟧

1. `validation_alias` দিয়ে environment variable-এর নাম বদলানো হয়েছে। এক্ষেত্রে `auth_key`-এর বদলে
   `my_auth_key` environment variable পড়া হবে।

    আরও তথ্যের জন্য দেখুন [`Field` ডকুমেন্টেশন](fields.md)।

2. `alias` দিয়ে environment variable-এর নাম বদলানো হয়েছে। এক্ষেত্রে `api_key`-এর বদলে
   যাচাই আর সিরিয়ালাইজেশন দুটোর জন্যই `my_api_key` environment variable ব্যবহার হবে।

    আরও তথ্যের জন্য দেখুন [`Field` ডকুমেন্টেশন](fields.md#field-aliases)।

3. [`AliasChoices`][pydantic.AliasChoices] ক্লাস দিয়ে একটি ফিল্ডের জন্য একাধিক environment variable নাম রাখা যায়।
   প্রথম যে environment variable পাওয়া যায়, সেটিই ব্যবহার হয়।

    আরও তথ্যের জন্য দেখুন [alias choices ডকুমেন্টেশন](alias.md#aliaspath-and-aliaschoices)।

4. [`ImportString`][pydantic.types.ImportString] ক্লাস দিয়ে একটি স্ট্রিং থেকে অবজেক্ট ইম্পোর্ট করা যায়।
   এক্ষেত্রে `special_function` environment variable পড়া হবে আর [`math.cos`][] ফাংশনটি ইম্পোর্ট হবে।

5. `env_prefix` কনফিগ সেটিং দিয়ে সব environment variable-এর জন্য একটি prefix (শুরুর অংশ) ঠিক করা যায়।

    আরও তথ্যের জন্য দেখুন [Environment variable নাম ডকুমেন্টেশন](#environment-variable-names)।

/// info | সবচেয়ে সহজ রূপ

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "আমার অ্যাপ"
    port: int = 8000
    debug: bool = False


settings = Settings()
print(settings.port)
```

টার্মিনালে `PORT=9000 DEBUG=true python app.py` চালালে `settings.port` হবে `9000` (সংখ্যা, স্ট্রিং নয়) আর `debug` হবে `True`। কিছু না দিলে ডিফল্ট মান।

///

## ডিফল্ট মানের যাচাই { #validation-of-default-values }

pydantic `BaseModel`-এর মতো নয়, `BaseSettings` ফিল্ডের ডিফল্ট মান ডিফল্টভাবেই যাচাই হয়।
`model_config`-এ, অথবা ফিল্ড পর্যায়ে `Field(validate_default=False)` দিয়ে `validate_default=False` সেট করে
এই আচরণ বন্ধ করতে পারেন:

⟦CODE2⟧

আরও তথ্যের জন্য দেখুন [ডিফল্ট মানের যাচাই](fields.md#validate-default-values)।

## চলার সময়ের যাচাই আর্গুমেন্ট { #runtime-validation-arguments }

সেটিংসের উৎস থেকে মান লোড করতে `BaseSettings` একটি নিজস্ব `__init__` সংজ্ঞায়িত করে, তাই `model_validate()`,
`model_validate_json()` আর `model_validate_strings()` সেই `__init__` ডেকেই instance তৈরি করে।
ফলে:

* সেটিংসের উৎসগুলো তখনো প্রয়োগ হয়, তাই environment variable, dotenv ফাইল ইত্যাদি থেকে মান
  ঠিক `Settings()` ডাকার মতোই লোড হয়।
* `extra`, `strict` আর `context`-এর মতো চলার সময়ের যাচাই আর্গুমেন্ট প্রয়োগ **হয় না**। যাচাই
  বদলে `model_config`-এর আচরণ ব্যবহার করে (যেমন ডিফল্ট `extra='forbid'`)।

ভিন্ন আচরণ দরকার হলে, সেটি `model_config`-এ দিন অথবা যাচাইয়ের আগে ইনপুট ডেটা প্রস্তুত করে নিন।
যেমন, একটি subclass-এর instance থেকে অভিভাবক settings ক্লাস তৈরি করতে, শুধু অভিভাবকের ফিল্ডগুলো রাখুন:

⟦CODE3⟧

## Environment variable-এর নাম { #environment-variable-names }

ডিফল্টভাবে environment variable-এর নাম ফিল্ডের নামের মতোই।

`env_prefix` কনফিগ সেটিং দিয়ে, অথবা instance তৈরির সময় `_env_prefix` keyword আর্গুমেন্ট দিয়ে,
সব environment variable-এর prefix বদলাতে পারেন:

⟦CODE4⟧

/// note | মনে রাখুন

ডিফল্ট `env_prefix` হলো `''` (খালি স্ট্রিং)। `env_prefix` শুধু env সেটিংসের জন্য নয়,
dotenv ফাইল, secret আর অন্য উৎসের জন্যও প্রযোজ্য।

///

/// tip | উদাহরণ দিয়ে বুঝি

একই সার্ভারে একাধিক অ্যাপ চললে সবার `PORT` নামের variable নিয়ে গোলমাল হয়। `env_prefix='SHOP_'` দিলে আপনার অ্যাপ শুধু `SHOP_PORT`, `SHOP_DEBUG` পড়বে; যেন প্রতিটি ফ্ল্যাটের চিঠির বাক্সে ফ্ল্যাট নম্বর লেখা।

///

একটি নির্দিষ্ট ফিল্ডের environment variable নাম বদলাতে চাইলে alias ব্যবহার করতে পারেন।

এটি করার দুটি উপায়:

* `Field(alias=...)` ব্যবহার (ওপরের `api_key` দেখুন)
* `Field(validation_alias=...)` ব্যবহার (ওপরের `auth_key` দেখুন)

alias নিয়ে আরও জানতে দেখুন [`Field` alias ডকুমেন্টেশন](fields.md#field-aliases)।

/// note | নেস্টেড ফিল্ডে alias

ডিফল্টভাবে, একটি নেস্টেড মডেল ফিল্ডে alias দিলে কোন environment variable সেখানে পৌঁছাতে পারবে তা *সংকুচিত* হয়: এর
উপ-ফিল্ডগুলো তখন প্রতিটি উৎসে শুধু সেই alias-কে prefix হিসেবে ধরে খোঁজা হয়। ফিল্ডের নিজের নাম
lookup prefix হিসেবে গ্রহণ হয় না, যদি না `populate_by_name=True` (বা `validate_by_name=True`) চালু থাকে;
dotenv ফাইল আর env নয় এমন অন্য উৎসের ক্ষেত্রেও তাই।

উৎসগুলো নামকরণে একমত না হলে এটি সবচেয়ে গুরুত্বপূর্ণ। যদি বেশি অগ্রাধিকারের উৎস alias ব্যবহার করে আর
কম অগ্রাধিকারের উৎস ফিল্ডের নাম, তাহলে শুধু alias-ভিত্তিক মানগুলোই পাওয়া যায়; অন্যগুলো কখনো
ফিল্ডের সাথে যুক্তই হয়নি, তাই মেশানোর কিছু থাকে না আর কম অগ্রাধিকারের মানগুলো উপেক্ষিত মনে হয়।
তাদের কী হবে তা নির্ভর করে `extra`-র ওপর: ডিফল্ট `extra='forbid'`-এ না মেলা dotenv
এন্ট্রি বাড়তি ইনপুট হিসেবে থেকে যায় আর `ValidationError` তোলে, অথচ সাধারণ environment variable
শুধু ধরা পড়ে না; `extra='ignore'` হলে দুটোই চুপচাপ বাদ পড়ে।

দুই বানানই গ্রহণ করতে, গ্রহণযোগ্য নামের সংখ্যা বাড়ান: হয় সব জায়গায় `populate_by_name=True`
(বা `validate_by_name=True`) দিয়ে, নয়তো প্রতিটি ফিল্ডে [`AliasChoices`][pydantic.AliasChoices] দিয়ে। দুটোতেই
ভিন্ন নামকরণের উৎসগুলো মিশতে পারে:

⟦CODE5⟧

যখন শুধু কিছু ফিল্ডের দুই বানানই দরকার, তখন প্রায়ই `AliasChoices` ভালো মানায়; যেমন এমন একটি
কনফিগারেশন ফাইল যা section-এর নাম পুরোটা লেখে, আর পাশাপাশি environment variable-এ সংক্ষিপ্ত নাম।
এটি সব জায়গায় সব ফিল্ডের নাম গ্রহণ না করে প্রতিটি ফিল্ডে ঠিক কোন নামগুলো গ্রহণযোগ্য তা বলে দেয়,
আর নেস্টিংয়ের প্রতিটি স্তরে আলাদাভাবে দুই বানান চালু করতে দেয়:

⟦CODE6⟧

///

### অচেনা environment variable { #unknown-environment-variables }

যে environment variable কোনো settings ফিল্ড বা তার alias-এর সাথে মেলে না, সেগুলো উপেক্ষা করা হয়, এমনকি
সেগুলো `env_prefix` দিয়ে শুরু হলেও আর `extra='forbid'` সেট থাকলেও। `extra` সেটিং মডেলে পাঠানো ইনপুট যাচাই করে;
এটি `os.environ`-এর প্রতিটি নাম পরীক্ষা করে না। তাই ফিল্ডের নামের বানান ভুল হলে কোনো এরর ছাড়াই
ডিফল্ট মান ব্যবহার হতে থাকতে পারে:

⟦CODE7⟧

1. বানান ভুল, তাই কোনো ফিল্ডের সাথে মেলে না আর যাচাই শুরুর আগেই বাদ পড়ে।

/// warning | সাধারণ ভুল

`DATABSE_URL` (বানান ভুল) সেট করলে Pydantic কিছু বলবে না, চুপচাপ ডিফল্ট ডেটাবেস ব্যবহার করবে। গুরুত্বপূর্ণ সেটিংসে ডিফল্ট মান না দিলে (বাধ্যতামূলক রাখলে) এমন ভুল চালুর সময়েই এরর হয়ে ধরা পড়ে।

///

নেস্টেড মডেলেও একই কথা: ভুল `env_nested_delimiter` হলে variable কোনো ফিল্ডের সাথে মেলে না।
তবে একবার কোনো variable একটি পরিচিত ফিল্ডের নেস্টেড prefix-এর সাথে *মিলে* গেলে, এর বিষয়বস্তু
যাচাইয়ের জন্য সেই ফিল্ডে পাঠানো হয়, তাই সেই নেস্টেড মডেলে `extra='forbid'` থাকলে ভেতরের অচেনা key
একটি `ValidationError` তুলতে পারে:

⟦CODE8⟧

`.env` ফাইল থেকে লোড হওয়া বাড়তি variable আর `dotenv_filtering`-এর প্রভাব জানতে দেখুন
[Dotenv (.env) সমর্থন](#dotenv-env-support)।

### Environment variable prefix কোথায় প্রযোজ্য { #environment-variable-prefix-targets }

`env_prefix` শুধু variable-এর নামে নয়, alias-এও প্রয়োগ করতে `env_prefix_target='all'` দিন।
`env_prefix` শুধু alias-এ প্রয়োগ করতে, variable-এর নামে নয়, `env_prefix_target='alias'` দিন।
`env_prefix` শুধু variable-এর নামে প্রয়োগ করতে (ডিফল্ট আচরণ), `env_prefix_target='variable'` দিন।

| `env_prefix_target` | ফিল্ডের নামে prefix | alias-এ prefix |
| --- | --- | --- |
| `'variable'` (ডিফল্ট) | হ্যাঁ | না |
| `'alias'` | না | হ্যাঁ |
| `'all'` | হ্যাঁ | হ্যাঁ |

⟦CODE9⟧

1. `env_prefix` উপেক্ষা হবে আর মানটি `FooAlias` environment variable থেকে পড়া হবে।

নেস্টেড মডেল ফিল্ডের alias-এও একই কথা প্রযোজ্য:

⟦CODE10⟧

1. `env_prefix` উপেক্ষা হবে আর alias খোঁজা হবে `SUB_VAR1` নামে, `APP_SUB_VAR1` নামে নয়।

### বড়-ছোট হাতের অক্ষর (Case-sensitivity) { #case-sensitivity }

ডিফল্টভাবে environment variable-এর নামে বড়-ছোট হাতের অক্ষরের পার্থক্য ধরা হয় না।

environment variable-এর নামে বড়-ছোট হাতের পার্থক্য চালু করতে `case_sensitive` কনফিগ সেটিং দিতে পারেন:

⟦CODE11⟧

`case_sensitive` `True` হলে, environment variable-এর নাম ফিল্ডের নামের সাথে হুবহু মিলতে হবে (prefix সহ বা ছাড়া),
তাই এই উদাহরণে `redis_host` শুধু `export redis_host` দিয়েই বদলানো যাবে। environment variable-এর নাম
সব বড় হাতের অক্ষরে রাখতে চাইলে অ্যাট্রিবিউটের নামও সব বড় হাতে রাখুন। তবু `Field(validation_alias=...)` দিয়ে
environment variable-এর যেকোনো নাম দিতে পারেন।

instance তৈরির সময় `_case_sensitive` keyword আর্গুমেন্ট দিয়েও case-sensitivity সেট করা যায়।

নেস্টেড মডেলের ক্ষেত্রে `case_sensitive` সেটিং সব নেস্টেড মডেলে প্রয়োগ হবে।

⟦CODE12⟧

1. লক্ষ করুন, `host` ফিল্ড পাওয়া যায়নি, কারণ environment variable-এর নাম `HOST` (সব বড় হাতের অক্ষরে)।

/// note | Windows-এ

Windows-এ Python-এর `os` মডিউল দিয়ে পাওয়া environment variable-এর নামে বড়-ছোট হাতের পার্থক্য থাকে না,
আর সেগুলো বড় হাতে স্বাভাবিক (normalize) করা হয় (যেমন `redis` সেট করলে হয় `REDIS`)। মূল অক্ষর
ফিরে পাওয়া যায় না বলে, Windows-এ **environment variable-এর জন্য `case_sensitive` সেটিংয়ের কোনো প্রভাব নেই**,
সেগুলো সবসময় বড়-ছোট হাত উপেক্ষা করে মেলানো হয়।

এটি শুধু environment variable-এর ক্ষেত্রে। dotenv (`.env`) ফাইল থেকে লোড হওয়া মানে অক্ষর
যেমন আছে তেমন থাকে, তাই সেগুলোর জন্য `case_sensitive=True` মানা হয়, Windows-এও।

///

## Environment variable-এর মান পার্স করা { #parsing-environment-variable-values }

ডিফল্টভাবে environment variable হুবহু পার্স হয়, মান খালি হলেও। `env_ignore_empty` কনফিগ সেটিং `True` করে
খালি environment variable উপেক্ষা করতে পারেন। environment-এর খালি মানের চেয়ে ফিল্ডের ডিফল্ট মান
ব্যবহার করতে চাইলে এটি কাজে লাগে।

বেশিরভাগ সাধারণ ফিল্ড টাইপের ক্ষেত্রে (যেমন `int`, `float`, `str` ইত্যাদি), environment variable-এর মান
ঠিক সেভাবেই পার্স হয় যেভাবে সরাসরি initialiser-এ (স্ট্রিং হিসেবে) দিলে হতো।

`list`, `set`, `dict` আর sub-model-এর মতো জটিল টাইপ environment থেকে পূরণ হয়
environment variable-এর মানকে JSON-এ লেখা স্ট্রিং হিসেবে ধরে।

/// warning | সতর্কতা

এই মানগুলো JSON হিসেবে decode হয় বলে, মান বৈধ JSON না হলে environment variable একটি
[`SettingsError`](../api/pydantic_settings.md#pydantic_settings.SettingsError) তোলে। যেমন, `numbers: list[int]`
ফিল্ডের জন্য `NUMBERS=1,2,3` ব্যর্থ হয়, কারণ `1,2,3` বৈধ JSON নয় (`NUMBERS='[1,2,3]'` হতে হবে)। এমন মান নিজের নিয়মে পার্স করতে চাইলে দেখুন
[JSON পার্সিং বন্ধ করা](#disabling-json-parsing)।

///

জটিল নেস্টেড variable পূরণের আরেকটি উপায় হলো মডেলে `env_nested_delimiter`
কনফিগ সেটিং দেওয়া, তারপর এমন নামের environment variable ব্যবহার করা যা নেস্টেড ফিল্ডগুলোর দিকে নির্দেশ করে।
এটি শুধু আপনার variable-কে ভেঙে নেস্টেড মডেল বা ডিকশনারিতে ছড়িয়ে দেয়।
তাই `FOO__BAR__BAZ=123` variable দিলে এটি হয়ে যাবে `FOO={'BAR': {'BAZ': 123}}`।
একই গঠনের একাধিক variable থাকলে সেগুলো মিশে যাবে।

/// note | মনে রাখুন

sub-model-কে `pydantic.BaseModel` থেকে উত্তরাধিকার নিতে হবে, নইলে `pydantic-settings` sub-model-কে আলাদাভাবে initialize করবে,
sub-model-এর ফিল্ডের মান আলাদা করে সংগ্রহ করবে, আর অপ্রত্যাশিত ফল পেতে পারেন।

///

/// note | মনে রাখুন

`env_nested_delimiter` অপশন সেই variable-গুলোতে প্রযোজ্য যা ঘোষিত কোনো শীর্ষ-স্তরের ফিল্ডের
নাম বা alias-এর সাথে মেলে। সেই ফিল্ডের নেস্টেড মানের ভেতরের অচেনা key তবু নেস্টেড
মডেলের যাচাইয়ের আওতায় থাকে। দেখুন [অচেনা environment variable](#unknown-environment-variables)।

///

উদাহরণস্বরূপ, এই environment variable-গুলো দেওয়া থাকলে:
⟦CODE13⟧

এগুলো নিচের settings মডেলে লোড করতে পারেন:

⟦CODE14⟧

1. sub-model-কে `pydantic.BaseModel` থেকে উত্তরাধিকার নিতে হবে।

2. sub-model-কে `pydantic.BaseModel` থেকে উত্তরাধিকার নিতে হবে।

`env_nested_delimiter` ওপরে দেখানো মতো `model_config` দিয়ে, অথবা instance তৈরির সময়
`_env_nested_delimiter` keyword আর্গুমেন্ট দিয়ে কনফিগার করা যায়।

ডিফল্টভাবে environment variable `env_nested_delimiter` দিয়ে যত গভীর খুশি নেস্টেড ফিল্ডে ভাগ হয়। নেস্টেড ফিল্ডের
গভীরতা সীমিত করা যায় `env_nested_max_split` কনফিগ সেটিং দিয়ে। এটি বিশেষভাবে কাজে লাগে দুই স্তরের সেটিংসে,
যেখানে `env_nested_delimiter` (সাধারণত একটি `_`) মডেলের ফিল্ডের নামের অংশও হতে পারে।
যেমন:

⟦CODE15⟧

এগুলো নিচের settings মডেলে লোড করতে পারেন:

⟦CODE16⟧

`env_nested_max_split=1` না দিলে `GENERATION_LLM_API_KEY` পার্স হতো `llm.api.key` হিসেবে, `llm.api_key` নয়,
আর একটি `ValidationError` উঠত।

নেস্টেড environment variable শীর্ষ-স্তরের environment variable-এর JSON-এর চেয়ে অগ্রাধিকার পায়
(যেমন ওপরের উদাহরণে `SUB_MODEL__V2` জেতে `SUB_MODEL`-এর ওপর)।

নিজের source ক্লাস দিয়েও জটিল টাইপ পূরণ করতে পারেন।

⟦CODE17⟧

### JSON পার্সিং বন্ধ করা { #disabling-json-parsing }

pydantic-settings ডিফল্টভাবে environment variable থেকে জটিল টাইপগুলো JSON স্ট্রিং হিসেবে পার্স করে। অর্থাৎ একটি মান
বৈধ JSON না হলে একটি [`SettingsError`](../api/pydantic_settings.md#pydantic_settings.SettingsError) ওঠে:

⟦CODE18⟧

কোনো ফিল্ডের জন্য এই আচরণ বন্ধ করে নিজের validator-এ মান পার্স করতে চাইলে, ফিল্ডটিতে
[`NoDecode`](../api/pydantic_settings.md#pydantic_settings.NoDecode) annotation দিন:

⟦CODE19⟧

1. `NoDecode` annotation `numbers` ফিল্ডের JSON পার্সিং বন্ধ করে। মান পার্স করতে
   `decode_numbers` ফিল্ড validator ডাকা হবে।

একই পার্সিং একাধিক ফিল্ডে বারবার ব্যবহার করতে, `NoDecode` আর একটি
[`BeforeValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators) একটি
annotated টাইপে মিলিয়ে নিন। কমা দিয়ে আলাদা মান গ্রহণের এটি একটি প্রচলিত উপায়, যেমন CORS origin বা অনুমোদিত
host-এর জন্য:

⟦CODE20⟧

`enable_decoding` কনফিগ সেটিং `False` করে সব ফিল্ডের JSON পার্সিং বন্ধ করতে পারেন:

⟦CODE21⟧

[`ForceDecode`](../api/pydantic_settings.md#pydantic_settings.ForceDecode) annotation দিয়ে কোনো ফিল্ডে জোর করে JSON পার্সিং চালু রাখা যায়।
এটি `enable_decoding` কনফিগ সেটিং এড়িয়ে যায়:

⟦CODE22⟧

1. `numbers1` ফিল্ডে `ForceDecode` annotation নেই, তাই এটি JSON হিসেবে পার্স হবে না,
   আর মান পার্স করতে আমাদের নিজের একটি validator দিতে হবে।

## নেস্টেড মডেলের ডিফল্টে আংশিক আপডেট { #nested-model-default-partial-updates }

ডিফল্টভাবে Pydantic settings নেস্টেড মডেলের ডিফল্ট অবজেক্টে আংশিক আপডেট অনুমোদন করে না। এই আচরণ
বদলানো যায় `nested_model_default_partial_update` ফ্ল্যাগ `True` করে, যা নেস্টেড মডেলের
ডিফল্ট অবজেক্টের ফিল্ডে আংশিক আপডেট অনুমোদন করবে।

⟦CODE23⟧

## Dotenv (.env) সমর্থন { #dotenv-env-support }

Dotenv ফাইল (সাধারণত নাম `.env`) একটি প্রচলিত পদ্ধতি, যা প্ল্যাটফর্ম-নিরপেক্ষভাবে environment variable
ব্যবহার সহজ করে।

dotenv ফাইল সব environment variable-এর একই সাধারণ নিয়ম মেনে চলে, আর দেখতে এমন:

⟦CODE24⟧

`.env` ফাইলে variable লেখা হয়ে গেলে, *pydantic* দুইভাবে এটি লোড করতে পারে:

1. `BaseSettings` ক্লাসের `model_config`-এ `env_file` সেট করে (আর অপারেটিং সিস্টেমের ডিফল্ট encoding না চাইলে `env_file_encoding`-ও):
   ⟦CODE25⟧
2. `BaseSettings` থেকে তৈরি ক্লাসের instance বানানোর সময় `_env_file` keyword আর্গুমেন্ট দিয়ে
(আর দরকার হলে `_env_file_encoding` দিয়ে):
   ⟦CODE26⟧
দুই ক্ষেত্রেই, দেওয়া আর্গুমেন্টের মান যেকোনো বৈধ পথ বা ফাইলের নাম হতে পারে, পূর্ণ পথ (absolute) অথবা
বর্তমান কাজের ফোল্ডারের (working directory) সাপেক্ষে। তারপর *pydantic* বাকি সব নিজেই সামলায়: variable লোড করে
সেগুলো যাচাই করে।

/// note | মনে রাখুন

`env_file`-এ শুধু একটি ফাইলের নাম দিলে, Pydantic শুধু বর্তমান কাজের ফোল্ডারেই খোঁজে,
`.env` ফাইলের জন্য কোনো অভিভাবক ফোল্ডারে খোঁজে না। বর্তমান কাজের ফোল্ডার থেকে কত স্তর **ওপরে** পর্যন্ত
খুঁজবে, তা `env_file_depth`-এ দিন:

⟦CODE27⟧

এটি শুধু তখনই ব্যবহার হয় যখন বর্তমান কাজের ফোল্ডারে ফাইলটি পাওয়া যায় না, আর শুধু আপেক্ষিক (relative)
পথের ক্ষেত্রে প্রযোজ্য। instance তৈরির সময় `_env_file_depth` keyword আর্গুমেন্ট দিয়েও সেট করা যায়।

///

/// tip | পরামর্শ

dotenv ফাইল হিসেবে named pipe (FIFO)-ও সমর্থিত। এটি কাজে লাগে
[1Password Environments](https://developer.1password.com/docs/environments)-এর মতো টুলে, যারা `.env` ফাইলকে
named pipe হিসেবে মাউন্ট করে ডিস্কে না লিখেই দরকারমতো secret দেয়।

///

dotenv ফাইল ব্যবহার করলেও *pydantic* dotenv ফাইলের পাশাপাশি environment variable-ও পড়ে,
আর **dotenv ফাইল থেকে লোড হওয়া মানের চেয়ে environment variable সবসময় অগ্রাধিকার পায়**।

instance তৈরির সময় `_env_file` keyword আর্গুমেন্ট দিয়ে ফাইলের পথ দিলে (পদ্ধতি ২), সেটি
`model_config` ক্লাসে দেওয়া মানকে (যদি থাকে) বাতিল করে। ওপরের দুটো কোড একসাথে ব্যবহার করলে `prod.env` লোড হবে
আর `.env` উপেক্ষিত হবে।

একাধিক dotenv ফাইল লোড করতে চাইলে, ফাইলের পথগুলো একটি tuple বা list হিসেবে দিতে পারেন। ফাইলগুলো
ক্রমানুসারে লোড হবে, আর প্রতিটি ফাইল আগেরটির মান বদলে দেবে।

⟦CODE28⟧

/// tip | উদাহরণ দিয়ে বুঝি

`('.env', '.env.prod')` হলো স্বচ্ছ কাগজের স্তূপ: নিচে সাধারণ সেটিংস (`.env`), ওপরে প্রোডাকশনের বিশেষ সেটিংস (`.env.prod`)। ওপরের কাগজে যা লেখা, সেটাই দেখা যায়; যা লেখা নেই, তা নিচের কাগজ থেকে দেখা যায়।

///

instance তৈরির keyword আর্গুমেন্টে `None` দিয়ে Pydantic-কে কোনো ফাইলই লোড না করতে বলতে পারেন (এমনকি
`model_config` ক্লাসে একটি দেওয়া থাকলেও), যেমন `settings = Settings(_env_file=None)`।

ফাইল পার্স করতে python-dotenv ব্যবহার হয় বলে, `export`-এর মতো bash-সদৃশ নিয়ম ব্যবহার করা যায়, ফলে
(আপনার অপারেটিং সিস্টেম আর পরিবেশ অনুযায়ী) dotenv ফাইলটি `source` দিয়েও ব্যবহার করা যেতে পারে;
বিস্তারিত জানতে দেখুন [python-dotenv ডকুমেন্টেশন](https://saurabh-kumar.com/python-dotenv/#usages)।

dotenv ফাইলের ক্ষেত্রে Pydantic settings `extra` কনফিগ বিবেচনা করে। অর্থাৎ `model_config`-এ `extra=forbid` (*ডিফল্ট*)
থাকলে আর আপনার dotenv ফাইলে এমন কোনো ফিল্ডের এন্ট্রি থাকলে যা settings মডেলে সংজ্ঞায়িত নয়,
settings তৈরির সময় `ValidationError` উঠবে।

এই আচরণ বদলানো যায় `dotenv_filtering` সেটিং দিয়ে, যা আরও দুটি বিকল্প মোড সমর্থন করে:
- `'match_prefix'`: শুধু prefix-এর সাথে মেলা variable-গুলো মডেলে পাঠানো হবে। `env_prefix`-এর সাথে ব্যবহার করলে একটি dotenv ফাইলকে একটি নির্দিষ্ট মডেলের "আওতায়" রাখতে কাজে লাগে।
- `'only_existing'`: শুধু যে variable-গুলোর সমতুল্য ফিল্ড আছে সেগুলো মডেলে পাঠানো হবে। এই অপশনে dotenv settings source ঠিক env settings source-এর মতো আচরণ করে।

pydantic 1.x BaseSettings-এর সাথে সামঞ্জস্যের জন্য `extra=ignore` ব্যবহার করুন:
⟦CODE29⟧


/// note | মনে রাখুন

`dotenv_filtering` ব্যবহার না করলে, Pydantic settings মডেলের `env_prefix` যা-ই হোক, dotenv ফাইলের সব মান লোড করে মডেলে পাঠায়।
তাই dotenv ফাইলে বাড়তি মান দিলে, সেগুলো `env_prefix` দিয়ে শুরু হোক বা না হোক,
একটি `ValidationError` উঠবে।

এর একটি ব্যতিক্রম আছে। `env_prefix` সেট থাকলে, prefix *ছাড়া* একটি dotenv এন্ট্রি যার নাম কোনো
ফিল্ডের নামের সাথে মেলে, সেটি বাড়তি মান হিসেবে না ধরে চুপচাপ বাদ দেওয়া হয়। যেমন, `env_prefix='app_'`
আর একটি `debug` ফিল্ড থাকলে, dotenv ফাইলের একটি `debug=...` লাইন `debug` পূরণও করে না (শুধু `app_debug` তা
করে), আবার `ValidationError`-ও তোলে না; এটি শুধু উপেক্ষিত হয়। এই অসামঞ্জস্য অবাক করতে পারে, কারণ
ডিফল্ট `extra='forbid'`-এ prefix ছাড়া একটি *না-মেলা* এন্ট্রি, যেমন `foo=...`, **ঠিকই** `ValidationError` তুলবে।

///

/// warning | সাধারণ ভুল

`.env` ফাইলে পাসওয়ার্ড, API key থাকে। এটি `.gitignore`-এ যোগ করুন, যাতে ভুল করে git-এ চলে না যায়। সবাইকে কোন variable লাগবে তা জানাতে আলাদা একটি `.env.example` ফাইল রাখুন, আসল মান ছাড়া।

///

## কমান্ড লাইন সমর্থন { #command-line-support }

Pydantic settings সমন্বিত CLI সমর্থন দেয়, ফলে Pydantic মডেল দিয়ে দ্রুত CLI অ্যাপ্লিকেশন সংজ্ঞায়িত করা
সহজ হয়। Pydantic settings CLI-এর দুটি প্রধান ব্যবহার:

1. Pydantic মডেলের ফিল্ড CLI দিয়ে বদলাতে।
2. Pydantic মডেল দিয়ে CLI সংজ্ঞায়িত করতে।

ডিফল্টভাবে আচরণটি ব্যবহার #১-এর উপযোগী, আর এটি [environment variable পার্স করা](#parsing-environment-variable-values)-র
ভিত্তির ওপর তৈরি। আপনার ব্যবহার মূলত #২ হলে, সম্ভবত [CLI অ্যাপ্লিকেশন তৈরি](#creating-cli-applications)-র শেষে বলা
বেশিরভাগ ডিফল্ট চালু করতে চাইবেন।

/// tip | উদাহরণ দিয়ে বুঝি

একই সেটিং তিনভাবে দেওয়া যায়: ফাইলে লিখে রাখা (`.env`), পরিবেশে রাখা (environment variable), আর চালানোর মুহূর্তে মুখে বলা (`python app.py --port 9000`)। মুখে বলা কথাই সবচেয়ে টাটকা, তাই CLI ডিফল্টভাবে সবচেয়ে বেশি অগ্রাধিকার পায়।

///

### মূল কথা { #the-basics }

শুরু করতে, [environment variable পার্স করা](#parsing-environment-variable-values)-য় দেখানো উদাহরণটি
আবার দেখি, তবে এবার Pydantic settings CLI দিয়ে:

⟦CODE30⟧

CLI পার্সিং চালু করতে শুধু `cli_parse_args` ফ্ল্যাগে একটি বৈধ মান দিই, যার অর্থ
`argparse`-এ যেমন সংজ্ঞায়িত তেমনই।

মনে রাখুন, CLI settings source ডিফল্টভাবে [**সবচেয়ে ওপরের উৎস**](#field-value-priority), যদি না এর [অগ্রাধিকার
বদলানো হয়](#customise-settings-sources):

⟦CODE31⟧

#### তালিকা (Lists) { #lists }

তালিকার CLI আর্গুমেন্ট পার্সিং নিচের তিন ধরনের যেকোনোটি মিশিয়ে ব্যবহার সমর্থন করে:

  * JSON ধরন `--field='[1,2]'`
  * Argparse ধরন `--field 1 --field 2`
  * অলস (Lazy) ধরন `--field=1,2`

খালি তালিকা দিতে JSON ধরন `--field='[]'` ব্যবহার করুন। অন্য তালিকা আর্গুমেন্টের সাথে মেশালে খালি array কোনো আইটেম যোগ করে না।

⟦CODE32⟧

#### ডিকশনারি { #dictionaries }

ডিকশনারির CLI আর্গুমেন্ট পার্সিং নিচের দুই ধরনের যেকোনোটি মিশিয়ে ব্যবহার সমর্থন করে:

  * JSON ধরন `--field='{"k1": 1, "k2": 2}'`
  * Environment variable ধরন `--field k1=1 --field k2=2`

এগুলো তালিকার রূপের সাথেও একসাথে ব্যবহার করা যায়, যেমন:

  * `--field k1=1,k2=2 --field k3=3 --field '{"k4": 4}'` ইত্যাদি।

⟦CODE33⟧

#### Literal আর Enum { #literals-and-enums }

literal আর enum-এর CLI আর্গুমেন্ট পার্সিং CLI-এর choices (নির্দিষ্ট বিকল্প)-এ রূপান্তরিত হয়।

⟦CODE34⟧

#### Alias { #aliases }

Pydantic ফিল্ডের alias CLI আর্গুমেন্টের alias হিসেবে যোগ হয়। এক অক্ষরের alias ছোট অপশনে (যেমন `-p`) রূপান্তরিত হয়।

⟦CODE35⟧

### পরিবর্তনশীল সংখ্যার নামযুক্ত অপশন { #variadic-named-options }

collection ফিল্ড ডিফল্টভাবে বারবার দেওয়া অপশন (`--param a --param b`)। এটি যেকোনো
`Sequence`, `Set` বা `Mapping` টাইপে প্রযোজ্য, তাদের subclass যেমন `tuple`, `frozenset`,
`deque` আর `OrderedDict`-সহ। `str`, `bytes` আর `bytearray`-ও sequence, কিন্তু এরা
একটিমাত্র মান নেয়। একটি অপশনের পরে বাকি সব মান গ্রহণ করতে (`--param a b c`), collection ফিল্ডটিকে `CliVariadicArg`-এ মুড়ে দিন।

অপশনটি আবার দিলে আগের মানগুলো **বদলে যায়** (`--param a b --param c` হয়
`['c']`), যা `action=append`-এর উল্টো। `nargs='*'` লোভী: এটি পরের অপশন ফ্ল্যাগ পর্যন্ত সব মান
নিয়ে নেয়, তাই পরে থাকা একটি subcommand-এর নামও গিলে ফেলতে পারে।

`AliasPath` ফিল্ডে `CliVariadicArg` উপেক্ষা করা হয়; সেগুলো তখনো `action=append` ব্যবহার করে।

### Subcommand আর Positional আর্গুমেন্ট { #subcommands-and-positional-arguments }

subcommand আর positional আর্গুমেন্ট প্রকাশ করা হয় `CliSubCommand` আর `CliPositionalArg` annotation দিয়ে।
subcommand annotation শুধু বাধ্যতামূলক ফিল্ডে (অর্থাৎ যে ফিল্ডের ডিফল্ট মান নেই) প্রয়োগ করা যায়।
তাছাড়া subcommand-কে অবশ্যই pydantic `BaseModel` বা pydantic.dataclasses `dataclass` থেকে তৈরি একটি বৈধ টাইপ
হতে হবে।

পার্স করা subcommand মডেল instance থেকে `get_subcommand` ইউটিলিটি ফাংশন দিয়ে পাওয়া যায়। কোনো subcommand
বাধ্যতামূলক না হলে, subcommand না পাওয়া গেলে এরর তোলা বন্ধ করতে `is_required` ফ্ল্যাগ `False` করুন।

/// note | মনে রাখুন

CLI settings-এর subcommand প্রতিটি মডেলে একটিমাত্র subparser-এ সীমাবদ্ধ। অর্থাৎ একটি মডেলের সব subcommand
একটি subparser-এর নিচে থাকে; একাধিক subparser, যাদের প্রতিটির নিজস্ব subcommand-এর সেট, তা সম্ভব নয়।
subparser নিয়ে আরও জানতে দেখুন [argparse
subcommands](https://docs.python.org/3/library/argparse.html#sub-commands)।

///

/// note | মনে রাখুন

`CliSubCommand` আর `CliPositionalArg`-এ বড়-ছোট হাতের অক্ষরের পার্থক্য সবসময় ধরা হয়।

///

⟦CODE36⟧

/// tip | উদাহরণ দিয়ে বুঝি

`git clone URL` কমান্ডে `clone` হলো subcommand (কী কাজ করবে), আর `URL` হলো positional আর্গুমেন্ট (নাম ছাড়া, শুধু অবস্থান দেখে বোঝা যায়)। `--depth 1` হলো নামযুক্ত অপশন।

///

`CliSubCommand` আর `CliPositionalArg` annotation union আর alias-ও সমর্থন করে। Pydantic মডেলের union-এর ক্ষেত্রে,
যাচাইয়ের সময় যে [সূক্ষ্ম বিষয়গুলো](https://docs.pydantic.dev/latest/concepts/unions/) দেখা দিতে পারে তা মনে রাখা জরুরি।
বিশেষ করে, বিষয়বস্তুতে হুবহু একই subcommand-এর union হলে, জটিলতা এড়াতে সেগুলো আলাদা `CliSubCommand`
ফিল্ডে ভাগ করার পরামর্শ দেওয়া হয়। সবশেষে, union থেকে পাওয়া subcommand-এর নাম হবে Pydantic মডেল ক্লাসগুলোর নিজের নাম।

`CliSubCommand` বা `CliPositionalArg` ফিল্ডে alias দিলে শুধু একটিই alias দেওয়া যায়।
union নয় এমন subcommand-এর ক্ষেত্রে alias দিলে দেখানো help লেখা আর subcommand-এর নাম বদলে যায়। উল্টোদিকে, union
subcommand-এর ক্ষেত্রে, CLI settings source-এর দৃষ্টিতে alias-এর কোনো দৃশ্যমান প্রভাব নেই। সবশেষে,
positional আর্গুমেন্টের ক্ষেত্রে alias দিলে ফিল্ডের জন্য দেখানো CLI help লেখা বদলে যায়।

⟦CODE37⟧

### CLI অ্যাপ্লিকেশন তৈরি { #creating-cli-applications }

`CliApp` ক্লাস দুটি ইউটিলিটি মেথড দেয়, `CliApp.run` আর `CliApp.run_subcommand`, যা দিয়ে একটি
Pydantic `BaseSettings`, `BaseModel` বা `pydantic.dataclasses.dataclass`-কে CLI অ্যাপ্লিকেশন হিসেবে চালানো যায়। মূলত মেথডগুলো
মডেলের সাথে যুক্ত `cli_cmd` মেথড চালানোর একটি কাঠামো দেয়।

`CliApp.run` দিয়ে সরাসরি পার্স করার `cli_args` দেওয়া যায়, আর instance তৈরির পরে মডেলের `cli_cmd` মেথড
(যদি সংজ্ঞায়িত থাকে) চালায়:

⟦CODE38⟧

একইভাবে, `CliApp.run_subcommand` পুনরাবৃত্তভাবে (recursively) একটি subcommand-এর `cli_cmd` মেথড চালাতে ব্যবহার করা যায়:

⟦CODE39⟧

/// note | মনে রাখুন

`CliApp.run`-এর মতো নয়, `CliApp.run_subcommand`-এর জন্য subcommand মডেলে একটি `cli_cmd` মেথড সংজ্ঞায়িত থাকতে হবে।

///

`BaseModel` আর `pydantic.dataclasses.dataclass` টাইপের জন্য, `CliApp.run` ভেতরে ভেতরে নিচের
`BaseSettings` কনফিগারেশন ডিফল্টগুলো ব্যবহার করে:

* `nested_model_default_partial_update=True`
* `case_sensitive=True`
* `cli_hide_none_type=True`
* `cli_avoid_json=True`
* `cli_enforce_required=True`
* `cli_implicit_flags=True`
* `cli_kebab_case=True`

#### Asynchronous কমান্ড { #asynchronous-commands }

Pydantic settings `CliApp.run` আর `CliApp.run_subcommand` দিয়ে asynchronous CLI কমান্ড চালানো সমর্থন করে। এই সুবিধায় আপনার Pydantic মডেলের ভেতরে (subcommand-সহ) async def মেথড সংজ্ঞায়িত করে সেগুলো synchronous মেথডের মতোই চালাতে পারেন। বিশেষ করে:

1. asynchronous মেথড সমর্থিত: আপনার cli_cmd বা এমন CLI প্রবেশ-মেথডকে async def হিসেবে চিহ্নিত করলে CliApp সেগুলো চালাবে।
2. subcommand-ও asynchronous হতে পারে: নেস্টেড CLI subcommand থাকলে, শেষ (সবচেয়ে নিচের স্তরের) subcommand মেথডগুলোও asynchronous হতে পারে।
3. asynchronous মেথড শুধু শেষ subcommand-এ রাখুন: অভিভাবক কমান্ডকে asynchronous করা সুপারিশ করা হয় না, কারণ এতে বাড়তি thread আর event loop তৈরি হতে পারে। সেরা পারফরম্যান্স আর অপ্রয়োজনীয় সম্পদ ব্যবহার এড়াতে, শুধু সবচেয়ে গভীরের (child) subcommand-গুলো async def হিসেবে লিখুন।

নিচে একটি asynchronous শীর্ষ-স্তরের কমান্ডের সহজ উদাহরণ:

⟦CODE40⟧

#### Asynchronous Subcommand { #asynchronous-subcommands }

ওপরে যেমন বলা হলো, subcommand-কেও async হিসেবে সংজ্ঞায়িত করা যায়। তবে অভিভাবক কমান্ডে অপ্রয়োজনীয়ভাবে নতুন thread আর event loop তৈরি এড়াতে, এটি শুধু leaf (সবচেয়ে নিচের স্তরের) subcommand-এর জন্য করুন:

⟦CODE41⟧

asynchronous cli_cmd সহ একটি subcommand চালানোর সময়, Pydantic settings স্বয়ংক্রিয়ভাবে দেখে নেয় বর্তমান thread-এ ইতিমধ্যে একটি সক্রিয় event loop আছে কিনা। থাকলে, সংঘাত এড়াতে async কমান্ডটি একটি নতুন thread-এ চালানো হয়। নইলে বর্তমান thread-এ asyncio.run() ব্যবহার করে। এই ব্যবস্থার ফলে আপনার asynchronous subcommand বাড়তি কোনো সেটআপ ছাড়াই "এমনিতেই কাজ করে"।

#### Help দেখানো { #printing-help }

help দেখাতে বা সাজিয়ে লেখা পেতে `print_help` আর `format_help` মেথড পাওয়া যায়।

⟦CODE42⟧

#### আর্গুমেন্ট সিরিয়ালাইজ করা { #serializing-arguments }

`CliApp.serialize` মেথড দিয়ে একটি তৈরি Pydantic মডেলকে তার CLI আর্গুমেন্টে সিরিয়ালাইজ করা যায়। সিরিয়ালাইজেশনের ধরন নিয়ন্ত্রণ করা যায় `list_style`, `dict_style` আর `positionals_first` ফ্ল্যাগ দিয়ে।

⟦CODE43⟧

### পরস্পর-বর্জনশীল দল (Mutually Exclusive Groups) { #mutually-exclusive-groups }

`CliMutuallyExclusiveGroup` ক্লাস থেকে উত্তরাধিকার নিয়ে CLI-এর পরস্পর-বর্জনশীল দল তৈরি করা যায়, যেখানে দলের একটিমাত্র অপশনই একসাথে দেওয়া যায়।

/// note | মনে রাখুন

একটি `CliMutuallyExclusiveGroup` union-এ ব্যবহার করা যায় না, বা এর ভেতরে নেস্টেড মডেল রাখা যায় না।

///

⟦CODE44⟧

### CLI অভিজ্ঞতা নিজের মতো করা { #customizing-the-cli-experience }

নিচের ফ্ল্যাগগুলো দিয়ে CLI-এর অভিজ্ঞতা নিজের প্রয়োজনমতো সাজাতে পারেন।

#### দেখানো প্রোগ্রামের নাম বদলানো { #change-the-displayed-program-name }

help লেখার usage অংশে দেখানো ডিফল্ট প্রোগ্রামের নাম বদলাতে `cli_prog_name` সেট করুন। ডিফল্টভাবে, argparse-এর মতোই,
এটি বর্তমানে চলা প্রোগ্রামের নাম `sys.argv[0]` থেকে নেয়।

⟦CODE45⟧

#### CLI boolean ফ্ল্যাগ { #cli-boolean-flags }

`cli_implicit_flags` সেটিং দিয়ে ঠিক করুন boolean ফিল্ড ডিফল্টভাবে explicit হবে নাকি implicit।
ডিফল্টভাবে boolean ফিল্ড "explicit", অর্থাৎ CLI-এ boolean মানটি স্পষ্টভাবে দিতে হয়, যেমন
`--flag=True`। উল্টোদিকে, "implicit" boolean ফিল্ড মানটি ফ্ল্যাগ থেকেই বুঝে নেয়, যেমন
`--flag,--no-flag`, ফলে আলাদা মান দেওয়ার দরকার হয় না।

এছাড়া, আরও সূক্ষ্ম নিয়ন্ত্রণের জন্য দরকারে দেওয়া `CliImplicitFlag` আর `CliExplicitFlag` annotation
ব্যবহার করা যায়।

⟦CODE46⟧

implicit ফ্ল্যাগের আচরণ আরও সূক্ষ্ম করা যায় "toggle" বা "dual" মোড সেটিং দিয়ে। একইভাবে, আরও সূক্ষ্ম নিয়ন্ত্রণের জন্য
দেওয়া `CliToggleFlag` আর `CliDualFlag` annotation ব্যবহার করা যায়।

"toggle" ফ্ল্যাগের ক্ষেত্রে, default=`False` হলে `--flag` রাখবে `True`। নইলে, default=`True` হলে `--no-flag` রাখবে
`False`।

⟦CODE47⟧

#### অচেনা আর্গুমেন্ট উপেক্ষা আর সংগ্রহ { #ignore-and-retrieve-unknown-arguments }

`cli_ignore_unknown_args` দিয়ে ঠিক করুন অচেনা CLI আর্গুমেন্ট উপেক্ষা করে শুধু চেনাগুলো পার্স করবে কিনা। ডিফল্টভাবে CLI
কোনো আর্গুমেন্ট উপেক্ষা করে না। উপেক্ষিত আর্গুমেন্টগুলো পরে `CliUnknownArgs` annotation দিয়ে পাওয়া যায়।

⟦CODE48⟧

subcommand থাকলে, অচেনা আর্গুমেন্ট ধরে রাখে সবচেয়ে ভেতরের সেই parser যেটি একটি `CliUnknownArgs` ফিল্ড ঘোষণা করে।
subcommand-এর আগে থাকা আর্গুমেন্ট অভিভাবক parser-এর কাছেই থাকে। কোনো child parser-এ ধরার ফিল্ড না থাকলে,
তার বাকি থাকা আর্গুমেন্ট অভিভাবকের কাছে ফেরত যায়। একটি `CliSettingsSource` নতুন আর্গুমেন্ট পার্স করলে ধরা তালিকাগুলো নতুন করে শুরু হয়।

সাধারণ নেস্টেড মডেল অভিভাবকের parser-ই ব্যবহার করে। সেই একই parser-এ একাধিক `CliUnknownArgs` ফিল্ড ঘোষণা করলে
তার বাকি আর্গুমেন্টগুলো তখনো দ্বিগুণ হয়; এই ক্ষেত্রটি ওপরের subcommand-এর আচরণে পড়ে না। যে নিজস্ব parser-এর
`parse_known_args` মেথড বদলানো যায় না, সেগুলোও subcommand-এর বাকি আর্গুমেন্ট আলাদাভাবে ধরতে পারে না।

#### আর্গুমেন্টে CLI kebab case { #cli-kebab-case-for-arguments }

`cli_kebab_case` চালু করে ঠিক করুন CLI আর্গুমেন্ট kebab case (যেমন `--my-option`, `--my_option`-এর বদলে) ব্যবহার করবে কিনা। ডিফল্টভাবে `cli_kebab_case=True`
enum ফিল্ড উপেক্ষা করে, আর এটি `cli_kebab_case='no_enums'`-এর সমান। enum-সহ সবকিছুতে kebab case প্রয়োগ করতে
`cli_kebab_case='all'` ব্যবহার করুন।

⟦CODE49⟧

#### এররে CLI বেরিয়ে যাবে কিনা { #change-whether-cli-should-exit-on-error }

`cli_exit_on_error` দিয়ে ঠিক করুন এরর হলে CLI-এর ভেতরের parser প্রোগ্রাম থেকে বেরিয়ে যাবে, নাকি একটি `SettingsError` এক্সেপশন
তুলবে। ডিফল্টভাবে এরর হলে CLI-এর ভেতরের parser বেরিয়ে যায়।

⟦CODE50⟧

#### CLI-এ বাধ্যতামূলক আর্গুমেন্ট জোর করা { #enforce-required-arguments-at-cli }

Pydantic settings তৈরিই করা হয়েছে মডেল তৈরির সময় বিভিন্ন উৎস থেকে মান টেনে আনার জন্য। অর্থাৎ একটি বাধ্যতামূলক
ফিল্ড কোনো একটি নির্দিষ্ট উৎস থেকে (যেমন CLI) কঠোরভাবে বাধ্যতামূলক নয়। বরং যেকোনো একটি উৎস বাধ্যতামূলক মানটি দিলেই
চলে।

তবে আপনার ব্যবহার যদি [#২-এর সাথে বেশি মেলে](#command-line-support), অর্থাৎ Pydantic মডেল দিয়ে CLI সংজ্ঞায়িত করা,
তাহলে সম্ভবত বাধ্যতামূলক ফিল্ডগুলো _CLI-তেই কঠোরভাবে বাধ্যতামূলক_ রাখতে চাইবেন। এই আচরণ চালু করা যায়
`cli_enforce_required` দিয়ে।

/// note | মনে রাখুন

বাধ্যতামূলক `CliPositionalArg` ফিল্ড CLI-তে সবসময় কঠোরভাবে বাধ্যতামূলক (জোর করা হয়)।

///

⟦CODE51⟧

#### None টাইপ পার্সের স্ট্রিং বদলানো { #change-the-none-type-parse-string }

CLI-এর কোন স্ট্রিং মান (যেমন "null", "void", "None" ইত্যাদি) `None`-এ পার্স হবে তা বদলাতে
`cli_parse_none_str` সেট করুন। ডিফল্টভাবে এটি `env_parse_none_str`-এর মান ব্যবহার করে, যদি সেট থাকে। নইলে,
`cli_avoid_json` `False` হলে ডিফল্ট "null", আর `cli_avoid_json` `True` হলে "None"।

⟦CODE52⟧

#### None টাইপের মান লুকানো { #hide-none-type-values }

`cli_hide_none_type` চালু করে CLI help লেখা থেকে `None` মান লুকান।

⟦CODE53⟧

#### JSON CLI অপশন যোগ করা এড়ানো { #avoid-adding-json-cli-options }

`cli_avoid_json` চালু করে CLI-তে JSON স্ট্রিং দাবি করে এমন জটিল ফিল্ড যোগ করা এড়ান।

⟦CODE54⟧

#### দলের help লেখায় ক্লাসের docstring ব্যবহার { #use-class-docstring-for-group-help-text }

ডিফল্টভাবে, নেস্টেড মডেলের দলের help লেখা পূরণের সময় এটি ফিল্ডের বর্ণনা থেকে নেয়।
বিকল্প হিসেবে, CLI settings-কে ক্লাসের docstring থেকে নিতেও কনফিগার করা যায়।

/// note | মনে রাখুন

ফিল্ডটি নেস্টেড মডেলের union হলে দলের help লেখা সবসময় ফিল্ডের বর্ণনা থেকেই নেওয়া হবে;
`cli_use_class_docs_for_groups` `True` করা থাকলেও।

///

⟦CODE55⟧

#### CLI help-এ environment variable দেখানো { #show-environment-variables-in-cli-help }

help লেখায় প্রতিটি CLI অপশনের জন্য খুঁজে পাওয়া environment variable-এর নাম যোগ করতে `cli_show_env_vars` চালু করুন। এটি
কাজে লাগে ops runbook, কনফিগারেশন খুঁজে পাওয়া, আর 12-factor অ্যাপে, যেখানে একই সেটিং হয়
CLI ফ্ল্যাগ দিয়ে নয়তো environment variable দিয়ে দেওয়া যায়।

⟦CODE56⟧

কোনো ফিল্ড `AliasChoices` ব্যবহার করলে, খুঁজে পাওয়া সব environment variable-এর নাম ক্রমানুসারে দেখানো হয়, যেমন
`[env: API_KEY | LEGACY_API_KEY]`। `cli_show_env_vars=True` দিয়ে সরাসরি একটি `CliSettingsSource` তৈরি করলে,
একই নামগুলো CLI destination-কে key ধরে একটি সাধারণ `env_var_names` mapping হিসেবেও পাওয়া যায়।

`_env_settings_source` না দিয়ে সরাসরি `CliSettingsSource` তৈরি করলে, help লেখা বের করতে একটি বিকল্প
`EnvSettingsSource(settings_cls)` ব্যবহার হয়। এতে মডেলের কনফিগের মান প্রতিফলিত হয়, কিন্তু source-পর্যায়ের
constructor-এ দেওয়া পরিবর্তন (যেমন নিজের `env_prefix` বা `env_nested_delimiter`) থাকে না, যদি না
সেই পরিবর্তিত source-টি স্পষ্টভাবে দেন।

#### CLI ফ্ল্যাগের prefix অক্ষর বদলানো { #change-the-cli-flag-prefix-character }

CLI-এর ঐচ্ছিক আর্গুমেন্টে ব্যবহৃত ফ্ল্যাগের prefix অক্ষর (ডিফল্ট `-`) বদলাতে `cli_flag_prefix_char` সেট করুন।

⟦CODE57⟧

#### CLI help লেখা থেকে ফিল্ড লুকানো { #suppressing-fields-from-cli-help-text }

CLI help লেখা থেকে একটি ফিল্ড লুকাতে, ফিল্ডের টাইপে `CliSuppress` annotation ব্যবহার করা যায়, অথবা ফিল্ডের বর্ণনায়
`CLI_SUPPRESS` স্ট্রিং constant ব্যবহার করা যায়।

⟦CODE58⟧

#### আর্গুমেন্টের CLI shortcut { #cli-shortcuts-for-arguments }

`SettingsConfigDict`-এর `cli_shortcuts` অপশন দিয়ে ফিল্ডের জন্য বিকল্প CLI আর্গুমেন্ট নাম (shortcut) যোগ করুন। এতে CLI আর্গুমেন্টের বাড়তি নাম সংজ্ঞায়িত করা যায়, যা বিশেষভাবে কাজে লাগে গভীরে নেস্টেড বা লম্বা ফিল্ড নামের জন্য আরও ব্যবহারবান্ধব বা ছোট alias দিতে।

`cli_shortcuts` অপশন একটি ডিকশনারি নেয়, যা লক্ষ্য ফিল্ডের নাম (নেস্টেড ফিল্ডের জন্য ডট দিয়ে লেখা) থেকে এক বা একাধিক shortcut নামে নির্দেশ করে। একাধিক ফিল্ড একই shortcut ভাগ করলে, প্রথম মেলা ফিল্ড অগ্রাধিকার পায়।

**সমতল উদাহরণ:**

⟦CODE59⟧

**নেস্টেড উদাহরণ:**

⟦CODE60⟧

কোনো shortcut সংঘাত করলে (একাধিক ফিল্ডে নির্দেশ করলে), এটি মডেলের প্রথম মেলা ফিল্ডে প্রয়োগ হবে।

### বিদ্যমান parser-এর সাথে যুক্ত করা { #integrating-with-existing-parsers }

ডিফল্ট CLI settings source-এর বদলে ব্যবহারকারীর সংজ্ঞায়িত একটি source দিয়ে, যা `root_parser` অবজেক্ট উল্লেখ করে,
একটি CLI settings source-কে বিদ্যমান parser-এর সাথে যুক্ত করা যায়।

⟦CODE61⟧

একটি `CliSettingsSource` parser মেথড ব্যবহার করে `settings_cls`-এর ফিল্ডগুলো কমান্ড লাইন আর্গুমেন্ট হিসেবে যোগ করে
`root_parser` অবজেক্টের সাথে যুক্ত হয়। `CliSettingsSource`-এর ভেতরের parser-এর রূপ `argparse` লাইব্রেরির ওপর ভিত্তি করে, তাই
এর দরকার এমন parser মেথড যা তাদের `argparse` সমতুল্যের মতো একই অ্যাট্রিবিউট সমর্থন করে। নিজের মতো করা যায় এমন
parser মেথডগুলো, তাদের argparse সমতুল্যসহ (ডিফল্ট), নিচে দেওয়া হলো:

* `parse_args_method` - (`argparse.ArgumentParser.parse_args`)
* `add_argument_method` - (`argparse.ArgumentParser.add_argument`)
* `add_argument_group_method` - (`argparse.ArgumentParser.add_argument_group`)
* `add_parser_method` - (`argparse._SubParsersAction.add_parser`)
* `add_subparsers_method` - (`argparse.ArgumentParser.add_subparsers`)
* `format_help_method` - (`argparse.ArgumentParser.format_help`)
* `formatter_class` - (`argparse.RawDescriptionHelpFormatter`)

argparse নয় এমন parser-এর ক্ষেত্রে, সমর্থিত না হলে parser মেথডগুলো `None` সেট করা যায়। root parser-এর সাথে যুক্ত হওয়ার সময়
শুধু তখনই CLI settings এরর তুলবে যখন কোনো parser মেথড দরকারি কিন্তু `None` সেট করা।

/// note | মনে রাখুন

`formatter_class` শুধু subcommand-এ প্রয়োগ হয়। ভাঙন এড়াতে `CliSettingsSource` বাইরের parser-এর কোনো সেটিংস
কখনো ছোঁয় বা বদলায় না। subcommand-গুলো তাদের নিজস্ব ভেতরের parser গাছে থাকে বলে,
বাইরের parser-এর যুক্তি না ভেঙেই নিরাপদে `formatter_class` সেটিংস প্রয়োগ করা যায়।

///

## Secrets { #secrets }

সংবেদনশীল কনফিগারেশন অ্যাপ্লিকেশনে দেওয়ার একটি প্রচলিত পদ্ধতি হলো secret মানগুলো ফাইলে রাখা।

secret ফাইল dotenv ফাইলের মতোই নিয়ম মানে, তবে এতে থাকে শুধু একটিমাত্র মান, আর ফাইলের নামটিই key হিসেবে
ব্যবহার হয়। একটি secret ফাইল দেখতে এমন:

```title
super_secret_database_password
```

secret ফাইলগুলো তৈরি হয়ে গেলে, *pydantic* দুইভাবে সেগুলো লোড করতে পারে:

1. একটি `BaseSettings` ক্লাসের `model_config`-এ `secrets_dir` হিসেবে সেই ফোল্ডার দিয়ে, যেখানে secret ফাইলগুলো রাখা।
   ⟦CODE62⟧
2. `BaseSettings` থেকে তৈরি ক্লাসের instance বানানোর সময় `_secrets_dir` keyword আর্গুমেন্ট দিয়ে:
   ````
   settings = Settings(_secrets_dir='/var/run')
   ````

দুই ক্ষেত্রেই, দেওয়া আর্গুমেন্টের মান যেকোনো বৈধ ফোল্ডার হতে পারে, পূর্ণ পথ অথবা বর্তমান কাজের
ফোল্ডারের সাপেক্ষে। **মনে রাখুন, ফোল্ডারটি না থাকলে শুধু একটি সতর্কবার্তা দেখাবে**।
তারপর *pydantic* বাকি সব নিজেই সামলায়: variable লোড করে সেগুলো যাচাই করে।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন `/run/secrets/` ফোল্ডারে `db_password` নামে একটি ফাইল আছে, যার ভেতরে শুধু পাসওয়ার্ডটি লেখা। `secrets_dir='/run/secrets'` দিলে `db_password: SecretStr` ফিল্ডটি সেই ফাইলের লেখা দিয়ে পূরণ হবে। প্রতিটি ফাইল যেন একটি করে তালাবদ্ধ খাম, খামের ওপর নাম আর ভেতরে মান।

///

secrets ফোল্ডার ব্যবহার করলেও *pydantic* তখনো dotenv ফাইল বা environment থেকে environment variable পড়ে,
আর **secrets ফোল্ডার থেকে লোড হওয়া মানের চেয়ে dotenv ফাইল আর environment variable সবসময় অগ্রাধিকার পায়**।

instance তৈরির সময় `_secrets_dir` keyword আর্গুমেন্ট দিয়ে পথ দিলে (পদ্ধতি ২), সেটি
`model_config` ক্লাসে দেওয়া মানকে (যদি থাকে) বাতিল করে।

একাধিক secrets ফোল্ডার থেকে সেটিংস লোড করতে চাইলে, একাধিক পথ একটি tuple বা list হিসেবে দিতে পারেন। ঠিক `env_file`-এর মতোই, পরের পথের মান আগেরটির মান বদলে দেয়।

⟦CODE63⟧

কোনো `secrets_dir` না থাকলে সেটি উপেক্ষা করা হয় আর সতর্কবার্তা দেখায়। কোনো `secrets_dir` ফোল্ডার না হয়ে ফাইল হলে এরর ওঠে।


### ব্যবহারের ক্ষেত্র: Docker Secrets { #use-case-docker-secrets }

Docker container-এ চলা একটি অ্যাপ্লিকেশনে সংবেদনশীল কনফিগারেশন দিতে Docker Secrets ব্যবহার করা যায়।
একটি *pydantic* অ্যাপ্লিকেশনে এই secret ব্যবহারের প্রক্রিয়া সহজ। Docker-এ secret তৈরি, ব্যবস্থাপনা
আর ব্যবহার নিয়ে আরও তথ্যের জন্য দেখুন অফিসিয়াল
[Docker ডকুমেন্টেশন](https://docs.docker.com/engine/reference/commandline/secret/)।

প্রথমে, secrets ফোল্ডার উল্লেখ করা একটি `SettingsConfigDict` দিয়ে আপনার `Settings` ক্লাস সংজ্ঞায়িত করুন।

⟦CODE64⟧

/// note | মনে রাখুন

ডিফল্টভাবে [Docker লক্ষ্য mount point হিসেবে `/run/secrets` ব্যবহার করে](https://docs.docker.com/engine/swarm/secrets/#how-docker-manages-secrets)।
অন্য জায়গা ব্যবহার করতে চাইলে সেই অনুযায়ী `Config.secrets_dir` বদলান।

///

তারপর Docker CLI দিয়ে আপনার secret তৈরি করুন
```bash
printf "This is a secret" | docker secret create my_secret_data -
```

সবশেষে, একটি Docker container-এর ভেতরে আপনার অ্যাপ্লিকেশন চালান আর নতুন তৈরি secret-টি দিন
```bash
docker service create --name pydantic-with-secrets --secret my_secret_data pydantic-app:latest
```

## নেস্টেড Secrets { #nested-secrets }

ডিফল্ট secrets ব্যবস্থা, `SecretsSettingsSource`, এর আচরণ সবসময় কাঙ্ক্ষিত বা যথেষ্ট নয়।
যেমন, ডিফল্ট ব্যবস্থা নেস্টেড submodel-এ secret ফিল্ড সমর্থন করে না।

ডিফল্ট আচরণ বদলাতে `SecretsSettingsSource`-এর সরাসরি বিকল্প হিসেবে `NestedSecretsSettingsSource` ব্যবহার করা যায়।
এটি নিজে থেকে চালু হয় না: `settings_customise_sources` hook দিয়ে এটি স্পষ্টভাবে কনফিগার করতে হয় (নিচের উদাহরণ দেখুন),
নইলে `BaseSettings` ডিফল্ট `SecretsSettingsSource`-ই ব্যবহার করতে থাকে।
সব পার্থক্য নিচের সারণিতে সংক্ষেপে দেওয়া হলো।

| `SecretsSettingsSource`                                                                                                                                         | `NestedSecretsSettingsSource`                                                                                                    |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| secret ফিল্ডকে শীর্ষ-স্তরের মডেলেই থাকতে হবে।                                                                                                                 | secret নেস্টেড মডেলের ফিল্ডও হতে পারে।                                                                                           |
| secret ফাইল শুধু `secrets_dir`-এ রাখা যায়।                                                                                                              | নেস্টেড মডেলের জন্য secret ফাইল উপ-ফোল্ডারে রাখা যায়।                                                                   |
| secret ফাইল খোঁজা হয় `EnvSettingsSource`-এর একই কনফিগারেশন অপশন দিয়ে: `case_sensitive`, `env_nested_delimiter`, `env_prefix`। | ডিফল্ট অপশন মানা হয়, তবে `secrets_case_sensitive`, `secrets_nested_delimiter`, `secrets_prefix` দিয়ে বদলানো যায়। |
| ফাইল সিস্টেমে `secrets_dir` না থাকলে একটি সতর্কবার্তা তৈরি হয়।                                                                                       | সতর্কবার্তা, এরর, নাকি চুপচাপ উপেক্ষা, তা বেছে নিতে `secrets_dir_missing` অপশন ব্যবহার করুন।                            |

### ব্যবহারের ক্ষেত্র: সমতল ফোল্ডার বিন্যাস { #use-case-plain-directory-layout }

⟦CODE65⟧

নিচের উদাহরণে, secrets-এর nested delimiter `'_'`, যা env-এর nested delimiter `'__'` থেকে আলাদা।
`Settings.db.user`-এর মান env variable `MY_DB__USER`-এ দেওয়া যায়।

⟦CODE66⟧

### ব্যবহারের ক্ষেত্র: নেস্টেড ফোল্ডার বিন্যাস { #use-case-nested-directory-layout }

⟦CODE67⟧
⟦CODE68⟧

### ব্যবহারের ক্ষেত্র: একাধিক নেস্টেড ফোল্ডার { #use-case-multiple-nested-directories }

⟦CODE69⟧
⟦CODE70⟧

### কনফিগারেশন অপশন { #configuration-options }

/// note | মনে রাখুন

`secrets_dir` ছাড়া, যা `SecretsSettingsSource`-এর সাথে ভাগ করা, নিচের সব অপশন শুধু
`NestedSecretsSettingsSource` পড়ে। ওপরের উদাহরণের মতো `settings_customise_sources` hook দিয়ে সেই source আপনার settings
source-এ যোগ না করলে এগুলোর কোনো প্রভাব নেই; ডিফল্ট
`SecretsSettingsSource` এগুলো উপেক্ষা করে। source কনফিগার না করে এর কোনোটি সেট করলে একটি
`UserWarning` ওঠে, যা জানায় যে এটি উপেক্ষিত হবে।

///

#### secrets_dir { #secrets_dir }

secrets ফোল্ডারের পথ, `SecretsSettingsSource.secrets_dir`-এর মতোই। `list` হলে শেষ মিলটিই জেতে।
source constructor আর মডেল কনফিগ দুই জায়গাতেই `secrets_dir` দিলে মানগুলো মেশে না (constructor জেতে)।
একটি `SecretsSettingsSource` মুড়ে নেওয়ার সময়, স্পষ্টভাবে দেওয়া `secrets_dir` মুড়ে নেওয়া source-এর
ফোল্ডারের চেয়েও অগ্রাধিকার পায়, `Settings(_secrets_dir=...)` সহ; সেগুলো উত্তরাধিকারে পেতে চাইলে এটি বাদ দিন।
secrets ফোল্ডার থেকে লোড করা বন্ধ করতে একটি খালি তালিকা দিন।

#### secrets_dir_missing { #secrets_dir_missing }

`secrets_dir` না থাকলে মূল `SecretsSettingsSource` একটি সতর্কবার্তা দেয়।
তবে এটি অনাকাঙ্ক্ষিত হতে পারে, যেমন ডেভেলপমেন্ট পরিবেশে Docker Secrets মাউন্ট না করলে।
বেছে নিতে `secrets_dir_missing` ব্যবহার করুন:

* `'ok'`: `secrets_dir` না থাকলে কিছুই করবে না
* `'warn'` (ডিফল্ট): সতর্কবার্তা দেখাবে, `SecretsSettingsSource`-এর মতোই
* `'error'`: `SettingsError` তুলবে

একাধিক `secrets_dir` দিলে, প্রতিটির ক্ষেত্রে একই `secrets_dir_missing` আচরণ প্রযোজ্য।

#### secrets_dir_max_size { #secrets_dir_max_size }

নিরাপত্তার কারণে `secrets_dir`-এর আকার সীমিত রাখে, ডিফল্ট `SECRETS_DIR_MAX_SIZE`, যা 16 MiB-এর সমান।

`NestedSecretsSettingsSource` হলো `EnvSettingsSource`-এর ওপর একটি পাতলা মোড়ক,
যা শুরুতেই সম্ভাব্য সব secret লোড করে। `secrets_dir`-এর নিচে একটি বড় ফাইল মাউন্ট করলে
এতে `MemoryError` হতে পারে।

একাধিক `secrets_dir` দিলে, সীমাটি প্রতিটি ফোল্ডারে আলাদাভাবে প্রযোজ্য।

#### secrets_case_sensitive { #secrets_case_sensitive }

`case_sensitive`-এর মতোই, তবে শুধু secret-এর জন্য কাজ করে। না দিলে ডিফল্ট হিসেবে `case_sensitive`-এর মান নেয়।

environment variable-এর `case_sensitive`-এর মতো নয়, এই অপশনটি সব প্ল্যাটফর্মে মানা হয়।
Windows-এ `os.environ` বড়-ছোট হাতের পার্থক্য ধরে না, তাই সেখানে `EnvSettingsSource`
পার্থক্য-না-ধরা মেলানোয় ফিরে যায়; secret হলো ফাইল আর তাদের অক্ষর যেমন আছে তেমন থাকে, তাই এমন কোনো
বিকল্পে ফেরার দরকার হয় না।

#### secrets_nested_delimiter { #secrets_nested_delimiter }

`env_nested_delimiter`-এর মতোই, তবে শুধু secret-এর জন্য কাজ করে। না দিলে ডিফল্ট হিসেবে `env_nested_delimiter`-এর মান নেয়।
এই অপশন দিয়ে _নেস্টেড secrets ফোল্ডার_ বিন্যাস তৈরি করা হয়, আর এটি দিয়ে এমনকি
`/run/secrets/model/delim/nested1/delim/nested2`-এর মতো জটিল কাজও করা যায়।

#### secrets_nested_subdir { #secrets_nested_subdir }

_নেস্টেড secrets ফোল্ডার_ মোড চালু করার boolean ফ্ল্যাগ, ডিফল্টভাবে `False`। `True` হলে `secrets_nested_delimiter`
হিসেবে `os.sep` (ফোল্ডার বিভাজক, যেমন `/`) সেট করে। `secrets_nested_delimiter` আগে থেকেই দেওয়া থাকলে `SettingsError` তোলে।

#### secrets_prefix { #secrets_prefix }

secret পথের prefix, `env_prefix`-এর মতো, তবে শুধু secret-এর জন্য কাজ করে। না দিলে ডিফল্ট হিসেবে `env_prefix`-এর মান নেয়।
সমতল আর নেস্টেড দুই ফোল্ডার মোডেই কাজ করে, যেমন
`'/run/secrets/prefix_model__nested'` আর `'/run/secrets/prefix_model/nested'`।


## AWS Secrets Manager { #aws-secrets-manager }

একটি প্যারামিটার অবশ্যই দিতে হবে:

- `secret_id`: AWS secret-এর id

secret-এর key-এর নাম আর ফিল্ডের নামের নিয়ম একই হতে হবে। যেমন, secret-এর key-এর নাম `SqlServerPassword` হলে, ফিল্ডের নামও একই হতে হবে। alias-ও ব্যবহার করতে পারেন।

AWS Secrets Manager-এ নেস্টেড মডেল সমর্থিত, key-এর নামে `--` বিভাজক দিয়ে। যেমন `SqlServer--Password`।

array (যেমন `MySecret--0`, `MySecret--1`) সমর্থিত নয়।

⟦CODE71⟧

## AWS Systems Manager Parameter Store { #aws-systems-manager-parameter-store }

নিচের প্যারামিটারগুলো দিতে পারেন:

- `ssm_path`: যে পথের ক্রমের (hierarchy) নিচে প্যারামিটারগুলো থাকে, যেমন `/prod/my-app`। অবশ্যই `/` দিয়ে শুরু হতে হবে, আর ডিফল্ট `/`।

`ssm_path`-এর নিচের সব প্যারামিটার পুনরাবৃত্তভাবে পড়া হয় [`get_parameters_by_path`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm/client/get_parameters_by_path.html)
API দিয়ে (`WithDecryption=True` সহ, ফলে `SecureString` প্যারামিটার decrypt হয়)। প্রতিটি প্যারামিটারের নাম থেকে
`ssm_path` prefix বাদ দেওয়া হয়, আর বাকি পথটি ফিল্ডের নাম হিসেবে ব্যবহার হয়।

Parameter Store আগে থেকেই `/` দিয়ে ভাগ করা ক্রম ব্যবহার করে বলে, নেস্টেড মডেল `/` বিভাজক দিয়ে সমর্থিত।
যেমন, `/prod/my-app/sub/a` নামের একটি প্যারামিটার `sub` মডেলের `a` ফিল্ড পূরণ করে। ফিল্ডের নাম আর প্যারামিটারের নামের
নিয়ম একই হতে হবে, অথবা alias ব্যবহার করুন।

⟦CODE72⟧

## Azure Key Vault { #azure-key-vault }

দুটি প্যারামিটার অবশ্যই দিতে হবে:

- `url`: যেমন `https://my-resource.vault.azure.net/`।
- `credential`: `DefaultAzureCredential` ব্যবহার করলে, নিজের কম্পিউটারে `az login` চালিয়ে পরিচয়ের credential পেতে পারেন। secret-এ প্রবেশের জন্য পরিচয়টির একটি role assignment থাকতে হবে (প্রস্তাবিতটি হলো `Key Vault Secrets User`)।

ফিল্ডের নাম আর Key Vault-এর secret-এর নামের নিয়ম একই হতে হবে। যেমন, secret-এর নাম `SqlServerPassword` হলে, ফিল্ডের নামও একই হতে হবে। alias-ও ব্যবহার করতে পারেন।

Key Vault-এ নেস্টেড মডেল `--` বিভাজক দিয়ে সমর্থিত। যেমন `SqlServer--Password`।

Key Vault-এর array (যেমন `MySecret--0`, `MySecret--1`) সমর্থিত নয়।

⟦CODE73⟧

### Snake case রূপান্তর { #snake-case-conversion }

Azure Key Vault source একটি `snake_case_conversion` অপশন নেয়, ডিফল্টভাবে বন্ধ, যা alias ছাড়াই Key Vault-এর secret নামগুলোকে Python-এর snake_case ফিল্ড নামে মিলিয়ে রূপান্তর করে।

⟦CODE74⟧

এই ব্যবস্থায় Azure Key Vault-এর secret (যেমন `MySetting`, `mySetting`, `my-secret` বা `MY-SECRET`) লোড হবে, আর সেগুলো snake case রূপে (এক্ষেত্রে `my_setting`) মিলবে।

### ড্যাশ থেকে আন্ডারস্কোর { #dash-to-underscore-mapping }

Azure Key Vault source একটি `dash_to_underscore` অপশন নেয়, ডিফল্টভাবে বন্ধ, যা Key Vault-এর kebab-case secret নামকে Python-এর snake_case ফিল্ড নামে মিলিয়ে সমর্থন করে। চালু থাকলে, যাচাইয়ের সময় secret নামের ড্যাশ (`-`) ফিল্ডের নামে আন্ডারস্কোর (`_`)-এ মেলে।

এই মেলানো শুধু *ফিল্ডের নামে* প্রযোজ্য, alias-এ নয়। নেস্টেড মডেলের ফিল্ড আলাদা করতে `--` ব্যবহার করুন; তাদের নামের ড্যাশও একইভাবে মেলে, তবে ডিকশনারির key যেমন আছে তেমন থাকে।

⟦CODE75⟧

এই ব্যবস্থায় `field-with-underscore`, `Alias-With-Dashes` আর `database--sql-password` নামের Azure Key Vault secret লোড হবে, আর সেগুলো যথাক্রমে `field_with_underscore`, `field_with_alias` আর `database.sql_password` ফিল্ডে মিলবে।

/// tip | পরামর্শ

বিকল্প হিসেবে, PascalCase secret মেলাতে একটি [alias_generator](alias.md#using-alias-generators) কনফিগার করতে পারেন।

///

## Google Cloud Secret Manager { #google-cloud-secret-manager }

Google Cloud Secret Manager দিয়ে Google Cloud Platform-এ সংবেদনশীল তথ্য secret হিসেবে রাখা, ব্যবস্থাপনা আর ব্যবহার করা যায়। এই integration দিয়ে আপনার Pydantic settings-এ ব্যবহারের জন্য সরাসরি GCP Secret Manager থেকে secret আনা যায়।

### ইনস্টলেশন { #installation_1 }

Google Cloud Secret Manager integration-এর জন্য বাড়তি dependency লাগে:

```bash
pip install "pydantic-settings[gcp-secret-manager]"
```

### সাধারণ ব্যবহার { #basic-usage }

Google Cloud Secret Manager ব্যবহার করতে আপনাকে:

1. একটি `GoogleSecretManagerSettingsSource` তৈরি করতে হবে। (অথেনটিকেশনের উপায় জানতে দেখুন [GCP অথেনটিকেশন](#gcp-authentication)।)
2. এই source-টি আপনার settings কাস্টমাইজেশন pipeline-এ যোগ করতে হবে

   ⟦CODE76⟧

### GCP অথেনটিকেশন { #gcp-authentication }

`GoogleSecretManagerSettingsSource` কয়েকটি অথেনটিকেশন পদ্ধতি সমর্থন করে:

1. **ডিফল্ট credential** - credential বা project ID না দিলে, সেগুলো পেতে এটি [`google.auth.default()`](https://google-auth.readthedocs.io/en/master/reference/google.auth.html#google.auth.default) ব্যবহার করবে। এটি কাজ করে:

   - `GOOGLE_APPLICATION_CREDENTIALS` environment variable থেকে service account credential দিয়ে
   - `gcloud auth application-default login` থেকে ব্যবহারকারীর credential দিয়ে
   - Compute Engine, GKE, Cloud Run বা Cloud Functions-এর ডিফল্ট service account দিয়ে

2. **স্পষ্ট credential** - সরাসরি `credentials`-ও দিতে পারেন। যেমন `sa_credentials = google.oauth2.service_account.Credentials.from_service_account_file('path/to/service-account.json')` আর তারপর `GoogleSecretManagerSettingsSource(credentials=sa_credentials)`

### Project ID নির্ধারণ { #project-id-resolution }

source পড়ার সময় `project_id` অলসভাবে (lazily) নির্ধারণ হয়, নিচের অগ্রাধিকারের ক্রমে:

1. স্পষ্ট `project_id` আর্গুমেন্ট, যদি দেওয়া হয়ে থাকে
2. আগের (বেশি অগ্রাধিকারের) settings source-এ নির্ধারিত মান - ডিফল্টভাবে `project_id` ফিল্ড, `project_id_field` আর্গুমেন্ট দিয়ে বদলানো যায়
3. [`google.auth.default()`](https://google-auth.readthedocs.io/en/master/reference/google.auth.html#google.auth.default)

এতে project কোডে সরাসরি লিখে না রেখে অন্য settings source (যেমন একটি environment variable বা init আর্গুমেন্ট) থেকে দেওয়া যায়। যেমন, `GoogleSecretManagerSettingsSource(settings_cls, project_id_field='gcp_project')` দিলে source-টি আগের কোনো source-এ নির্ধারিত `gcp_project` মানকে তার project হিসেবে ব্যবহার করে।

`project_id_field`-কে আগের source `current_state`-এ যে key ব্যবহার করে তার সাথে মিলতে হবে; এটি সাধারণত ফিল্ডের পছন্দের alias। যেমন, আপনার settings মডেলে `gcp_project: str = Field(alias='GCP_PROJECT')` থাকলে, `project_id_field='GCP_PROJECT'` (alias) দিন, `'gcp_project'` (Python অ্যাট্রিবিউটের নাম) নয়।

### নেস্টেড মডেল { #nested-models }

নেস্টেড মডেলের জন্য, Secret Manager `env_nested_delimiter` সেটিং সমর্থন করে, যতক্ষণ সেটি [নামকরণের নিয়ম](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#create-a-secret) মানে। ওপরের উদাহরণে, আপনি Secret Manager-এ `database__password` আর `database__user` নামের secret তৈরি করবেন।

### Secret-এর সংস্করণ { #secret-versions }

ডিফল্টভাবে `GoogleSecretManagerSettingsSource` secret-এর "latest" (সর্বশেষ) সংস্করণ ব্যবহার করে।
`SecretVersion` annotation দিয়ে অন্য সংস্করণ উল্লেখ করতে পারেন।

⟦CODE77⟧

/// note | মনে রাখুন

একই secret-এর (alias) দিকে নির্দেশ করা কিন্তু ভিন্ন সংস্করণের একাধিক ফিল্ড থাকলে, `SettingsConfigDict`-এ অবশ্যই `populate_by_name=True` (বা `validate_by_name=True`) চালু করতে হবে।

///


### গুরুত্বপূর্ণ কথা { #important-notes }

1. **বড়-ছোট হাতের অক্ষর**: ডিফল্টভাবে secret-এর নামে বড়-ছোট হাতের পার্থক্য ধরা হয়।
    *   `case_sensitive=False` দিলে, `pydantic-settings` পার্থক্য না ধরে secret খোঁজার চেষ্টা করবে। এটি পার্থক্য-না-ধরা মিলের চেয়ে হুবহু মিলকে অগ্রাধিকার দেয়। কিছু উদাহরণ দেখতে, ধরুন `case_sensitive=False` আর মডেলের অ্যাট্রিবিউটের নাম `my_secret`:
        * Google Secret Manager-এ `MY_SECRET` আর `my_secret` দুটোই থাকলে - `my_secret`-এর মান ফেরত আসবে।
        * Google Secret Manager-এ `MY_SECRET`, `My_Secret` আর `my_Secret` থাকলে - একটি সতর্কবার্তা উঠবে আর `my_Secret`-এর মান ফেরত আসবে - কারণ secret-এর নামগুলো প্রথমে ASCII ক্রমে সাজানো হয় (যেখানে ছোট হাতের অক্ষর বড় হাতের চেয়ে বড়) আর শেষটি বেছে নেওয়া হয় (এক্ষেত্রে যা `my_Secret`)।
2. **Secret-এর নামকরণ**: Google Secret Manager-এ আপনার ফিল্ডের নামের সাথে মেলে (prefix থাকলে তা-সহ) এমন নামে secret তৈরি করুন। [Secret Manager ডকুমেন্টেশন](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#create-a-secret) অনুযায়ী, secret-এর নামে বড় আর ছোট হাতের অক্ষর, সংখ্যা, হাইফেন আর আন্ডারস্কোর থাকতে পারে। নামের সর্বোচ্চ দৈর্ঘ্য 255 অক্ষর।

Google Cloud Secret Manager-এ secret তৈরি আর ব্যবস্থাপনা নিয়ে আরও বিস্তারিত জানতে দেখুন [অফিসিয়াল Google Cloud ডকুমেন্টেশন](https://cloud.google.com/secret-manager/docs)।

## অন্যান্য settings source { #other-settings-source }

প্রচলিত কনফিগারেশন ফাইলের জন্য আরও settings source পাওয়া যায়:

- `JsonConfigSettingsSource`, `json_file` আর `json_file_encoding` আর্গুমেন্ট দিয়ে
- `PyprojectTomlConfigSettingsSource`, *(ঐচ্ছিক)* `pyproject_toml_depth` আর *(ঐচ্ছিক)* `pyproject_toml_table_header` আর্গুমেন্ট দিয়ে
- `TomlConfigSettingsSource`, `toml_file` আর্গুমেন্ট আর *(ঐচ্ছিক)* `toml_table_header` আর্গুমেন্ট দিয়ে
- `YamlConfigSettingsSource`, `yaml_file` আর yaml_file_encoding আর্গুমেন্ট দিয়ে

এগুলো ব্যবহার করতে [এখানে](#customise-settings-sources) বর্ণিত একই পদ্ধতি ব্যবহার করতে পারেন।

⟦CODE78⟧

এটি আপনার কাজের ফোল্ডারে থাকা নিচের "config.toml" ফাইলটি পড়তে পারবে:

⟦CODE79⟧

পথের একটি তালিকা দিয়ে একাধিক ফাইলও দিতে পারেন।

⟦CODE80⟧

নিচের দুটি কনফিগারেশন ফাইল

⟦CODE81⟧

⟦CODE82⟧

এর সমান

⟦CODE83⟧

ফাইলগুলো অগ্রাধিকারের ঊর্ধ্বক্রমে অগভীরভাবে (shallowly) মেশে। গভীরভাবে মেশানো (deep merge) চালু করতে, সরাসরি source-এ `deep_merge=True` দিন।

/// warning | সতর্কতা

`deep_merge` অপশন `SettingsConfigDict` দিয়ে **পাওয়া যায় না**।

///

/// note | মনে রাখুন

`str` আর `pathlib.Path` ছাড়াও, `json_file`, `toml_file` আর `yaml_file` অপশন একটি
[`Traversable`][importlib.resources.abc.Traversable]-ও গ্রহণ করে, যেমন `importlib.resources.files(...).joinpath(...)`-এর ফল।
এতে আপনার প্যাকেজের ভেতরে থাকা একটি কনফিগারেশন ফাইল লোড করা যায়, এমনকি যেখানে
রিসোর্সটি ফাইল সিস্টেমে নেই (যেমন zip/wheel-এর ভেতরে)।

///

⟦CODE84⟧

deep merge চালু থাকলে, নিচের দুটি কনফিগারেশন ফাইল

⟦CODE85⟧

⟦CODE86⟧

এর সমান

⟦CODE87⟧

/// tip | উদাহরণ দিয়ে বুঝি

অগভীর মেশানো মানে পুরো একটি ড্রয়ার বদলে দেওয়া: দ্বিতীয় ফাইলে `[database]` থাকলে প্রথম ফাইলের পুরো `[database]` অংশ বাদ। গভীর মেশানো মানে ড্রয়ারের ভেতরের জিনিস একটি একটি করে বদলানো: শুধু যে key দুই ফাইলেই আছে সেটি বদলায়, বাকিগুলো থেকে যায়।

///

ফাইলের একটি নির্দিষ্ট table থেকে লোড করতে চাইলে, header-এর অংশগুলোর একটি tuple হিসেবে `toml_table_header` দিতে পারেন। যেমন, `toml_table_header=('my-table',)` `[my-table]` table থেকে variable লোড করবে।

সরাসরি `TomlConfigSettingsSource`-এ `toml_table_header` দিলে মডেলের কনফিগারেশন বাতিল হয়। মডেলে table header কনফিগার করা থাকলেও ফাইলের মূল (root) থেকে লোড করতে `toml_table_header=()` ব্যবহার করুন। আর্গুমেন্টটি বাদ দিলে বা `None` দিলে মডেলের কনফিগারেশন ব্যবহার হয়।

⟦CODE88⟧

এতে নিচের TOML ফাইলটি পড়া যাবে:
⟦CODE89⟧

### pyproject.toml { #pyprojecttoml }

"pyproject.toml" হলো Python প্রজেক্টে কনফিগারেশনের মান দেওয়ার একটি মানক ফাইল।
[PEP 518](https://peps.python.org/pep-0518/#tool-table) একটি `[tool]` table সংজ্ঞায়িত করে, যা দিয়ে যেকোনো টুলের কনফিগারেশন দেওয়া যায়।
`[tool]` table ব্যবহারে উৎসাহ দেওয়া হলেও, "pyproject.toml" ফাইলের যেকোনো জায়গা থেকে variable লোড করতে `PyprojectTomlConfigSettingsSource` ব্যবহার করা যায়।

এটি নিয়ন্ত্রণ করা হয় `SettingsConfigDict(pyproject_toml_table_header=tuple[str, ...])` দিয়ে, যেখানে মানটি header-এর অংশগুলোর একটি tuple।
ডিফল্টভাবে `pyproject_toml_table_header=('tool', 'pydantic-settings')`, যা `[tool.pydantic-settings]` table থেকে variable লোড করবে।

⟦CODE90⟧

এটি আপনার কাজের ফোল্ডারে থাকা নিচের "pyproject.toml" ফাইলটি পড়তে পারবে, ফলে পাওয়া যাবে `Settings(field='default-table')`, `SomeTableSettings(field='some-table')` আর `RootSettings(field='root')`:

⟦CODE91⟧

ডিফল্টভাবে `PyprojectTomlConfigSettingsSource` শুধু আপনার বর্তমান কাজের ফোল্ডারে একটি "pyproject.toml" খোঁজে।
তবে এই আচরণ বদলানোর দুটি উপায় আছে।

* বর্তমান কাজের ফোল্ডারে না পাওয়া গেলে ফোল্ডার-গাছে **ওপরের দিকে** `<int>` সংখ্যক ফোল্ডারে "pyproject.toml" খুঁজতে `SettingsConfigDict(pyproject_toml_depth=<int>)` দেওয়া যায়।
  ডিফল্টভাবে কোনো অভিভাবক ফোল্ডারে খোঁজা হয় না।
* source তৈরির সময় একটি স্পষ্ট ফাইলের পথ দেওয়া যায় (যেমন `PyprojectTomlConfigSettingsSource(settings_cls, Path('~/.config').resolve() / 'pyproject.toml')`)।
  এভাবে ফাইলের পথ দিলে সেটিকে পূর্ণ পথ হিসেবে ধরা হয় (অন্য কোনো জায়গায় খোঁজা হয় না)।

⟦CODE92⟧

## ফিল্ডের মানের অগ্রাধিকার { #field-value-priority }

একই `Settings` ফিল্ডের মান একাধিকভাবে দেওয়া থাকলে,
বেছে নেওয়া মানটি এভাবে ঠিক হয় (অগ্রাধিকারের অধঃক্রমে, অর্থাৎ ওপরেরটি সবচেয়ে শক্তিশালী):

1. `cli_parse_args` চালু থাকলে, CLI-তে দেওয়া আর্গুমেন্ট।
2. `Settings` ক্লাসের initialiser-এ দেওয়া আর্গুমেন্ট।
3. environment variable, যেমন ওপরে বর্ণিত `my_prefix_special_function`।
4. dotenv (`.env`) ফাইল থেকে লোড হওয়া variable।
5. secrets ফোল্ডার থেকে লোড হওয়া variable।
6. `Settings` মডেলের ফিল্ডের ডিফল্ট মান।

/// tip | উদাহরণ দিয়ে বুঝি

`port` তিন জায়গায় আছে: `.env`-এ `8000`, environment-এ `PORT=9000`, আর কোডে `Settings(port=7000)`। ফল হবে `7000`, কারণ initialiser-এর আর্গুমেন্ট (২ নম্বর) environment (৩ নম্বর) আর `.env`-এর (৪ নম্বর) চেয়ে ওপরে।

///

## settings source ডিবাগ করা { #debugging-settings-sources }

একাধিক source চালু থাকলে, একটি মান কোন source থেকে এল, আর কেন, তা বলা কঠিন হতে পারে।
`PYDANTIC_SETTINGS_DEBUG` environment variable একটি সত্য-বাচক মানে (`1`, `true`, `yes`
বা `on`) সেট করলে pydantic-settings `DEBUG` স্তরে log করে প্রতিটি source-এর সংগ্রহ করা ডিকশনারি,
অগ্রাধিকারের ক্রমে (সবচেয়ে বেশিটি আগে):

```bash
PYDANTIC_SETTINGS_DEBUG=1 python your_app.py
```

আউটপুট আসে `pydantic_settings` logger-এ, তাই নিশ্চিত করুন `DEBUG`-স্তরের logging চালু আছে
(যেমন `logging.basicConfig(level=logging.DEBUG)` দিয়ে)। একটি সাধারণ রিপোর্ট দেখতে এমন:

⟦CODE93⟧

source-গুলো সবচেয়ে বেশি থেকে সবচেয়ে কম অগ্রাধিকারের ক্রমে তালিকাভুক্ত, আর deep update দিয়ে মেশানো হয়: বেশি অগ্রাধিকারের source কম অগ্রাধিকারেরটির মান বদলে দেয়।
নেস্টেড গঠনের ক্ষেত্রে, শীর্ষ-স্তরের key বেশি অগ্রাধিকারের source-এ থাকলেও কম অগ্রাধিকারের source তখনো অনুপস্থিত উপ-key যোগ করতে পারে।

একই ফ্ল্যাগ ফাইল খুঁজে পাওয়ার প্রক্রিয়াও দেখায়, ফলে কোন dotenv আর secret ফাইল আসলে
পাওয়া গেল আর লোড হলো তা দেখতে পারেন; এটি কাজে লাগে যখন একই কোড অন্য কাজের ফোল্ডার থেকে চালালে চুপচাপ
ডিফল্ট মান আসে, কারণ আপেক্ষিক `.env` পথটি খুঁজে পাওয়া যায়নি:

⟦CODE94⟧

/// warning | সতর্কতা

ডিবাগ আউটপুটে প্রতিটি source থেকে লোড হওয়া মান থাকে, যাতে environment variable, dotenv ফাইল বা secrets ফোল্ডার
থেকে লোড হওয়া secret থাকতে পারে। শুধু বিশ্বস্ত ডিবাগিং পরিবেশে এটি চালু করুন, আর প্রোডাকশনে চালু রেখে দেবেন না।

///

## settings source নিজের মতো করা { #customise-settings-sources }

অগ্রাধিকারের ডিফল্ট ক্রম আপনার প্রয়োজনের সাথে না মিললে, আপনার `Settings`-এর `settings_customise_sources` মেথড
override করে সেটি বদলানো যায়।

`settings_customise_sources` আর্গুমেন্ট হিসেবে চারটি callable নেয় আর যত খুশি callable একটি tuple হিসেবে ফেরত দেয়।
তারপর এই callable-গুলো ডেকে settings ক্লাসের ফিল্ডের ইনপুট তৈরি করা হয়।

প্রতিটি callable-কে settings ক্লাসের একটি instance একমাত্র আর্গুমেন্ট হিসেবে নিয়ে একটি `dict` ফেরত দিতে হবে।

### অগ্রাধিকার বদলানো { #changing-priority }

ফেরত দেওয়া callable-গুলোর ক্রমই ইনপুটের অগ্রাধিকার ঠিক করে; প্রথমটি সবচেয়ে বেশি অগ্রাধিকারের।

⟦CODE95⟧

`env_settings` আর `init_settings`-এর জায়গা অদলবদল করায়, এখন `__init__` kwargs-এর চেয়ে environment variable অগ্রাধিকার পায়।

### source যোগ করা { #adding-sources }

আগে যেমন বলা হয়েছে, *pydantic*-এর সাথে একাধিক তৈরি settings source আসে। তবে মাঝে মাঝে
আপনার নিজের source যোগ করার দরকার হতে পারে; `settings_customise_sources` এটি খুব সহজ করে:

⟦CODE96⟧

#### আগের source-এর ফল ব্যবহার { #accessing-the-result-of-previous-sources }

প্রতিটি settings source আগেরগুলোর আউটপুট দেখতে পারে।

⟦CODE97⟧

### source বাদ দেওয়া { #removing-sources }

কোনো source বন্ধও করতে চাইতে পারেন:

⟦CODE98⟧


## জায়গায় থেকেই আবার লোড { #in-place-reloading }

একটি বিদ্যমান সেটিং জায়গায় থেকেই (in-place) আবার লোড করতে চাইলে, এর `__init__` মেথড দিয়ে তা করতে পারেন:

⟦CODE99⟧


## সেটিংস cache করা { #caching-settings }

একটি settings মডেল তৈরি করলে প্রতিবার এর কনফিগার করা settings source পড়ে আর যাচাই করে। source যখন
ডিস্ক থেকে পড়ে, যেমন dotenv, secrets, JSON, TOML বা YAML ফাইল, অথবা ক্লাউডের secret
manager আর parameter store থেকে secret আনে, তখন এটি ব্যয়বহুল হতে পারে। যখন একটি অ্যাপ্লিকেশনের প্রতিটি settings
ক্লাস আর প্রসেসের জন্য একটিমাত্র ডিফল্ট settings instance দরকার, তখন `settings_cached()` ব্যবহার করুন:

⟦CODE100⟧

settings ক্লাসটি সরাসরি ডাকলে আগের মতোই নতুন instance তৈরি হয়। `settings_clear_cache()` ডাকলে সেই ক্লাসের
cache করা instance সরে যায়, ফলে পরের `settings_cached()` ডাক আবার settings source লোড করে।

প্রতিটি ক্লাস নিজের key-এর নিচে cache হয়, তাই একটি subclass কখনো অভিভাবকের সাথে instance ভাগ করে না। মোছার সময়ও
একই কথা: `settings_clear_cache()` শুধু যে ক্লাসে ডাকা হয়েছে ঠিক সেটিরই এন্ট্রি সরায়। একটি base class দিয়ে
সেটিংস আবার লোড করলে, cache করা প্রতিটি subclass-ও মুছুন, নইলে সেই subclass-গুলো তাদের
পুরনো instance-ই দিতে থাকবে।

cache প্রতিটি প্রসেসের নিজস্ব। cache করা অবজেক্টটি ভাগ করা, তাই এতে যেকোনো পরিবর্তন সব কলকারী দেখতে পায়।
মডেলকে frozen কনফিগার করলে শুধু এর অ্যাট্রিবিউটে নতুন মান বসানো আটকায়; মানগুলো নিজেরা জমে যায় না, তাই
তালিকা বা ডিকশনারির মতো পরিবর্তনযোগ্য ফিল্ড তখনো জায়গায় থেকে বদলানো যায় আর সেই পরিবর্তন পুরো প্রসেসে ভাগ হয়। একটি cache করা
instance প্রসেসের পুরো জীবনকাল তার নিজের ক্লাসকে জীবিত রাখে, আর এটিই একে singleton বানায়। settings ক্লাস
গতিশীলভাবে (dynamically) তৈরি করলে আর সেগুলো মুছে ফেলা (garbage collect) দরকার হলে, একটির কাজ শেষে `settings_clear_cache()` ডাকুন,
এতে তার cache এন্ট্রি সরে যায়।

`settings_cached` আর `settings_clear_cache` `protected_namespaces`-এ যোগ করা বলে, এর কোনোটি দিয়ে শুরু হওয়া নামের
ফিল্ড সংজ্ঞায়িত করলে একটি `UserWarning` ওঠে। এমন ফিল্ড আগে থেকেই থাকলে, সেটির নাম বদলান অথবা আপনার মডেল কনফিগে
`protected_namespaces` override করুন।

/// tip | FastAPI-তে

FastAPI-তে সেটিংস ডিপেন্ডেন্সি হিসেবে দিতে প্রায়ই `@lru_cache` দিয়ে মোড়ানো `get_settings()` ফাংশন ব্যবহার হয়; `settings_cached()` একই কাজ সরাসরি করে। দেখুন [FastAPI-তে Settings আর Environment Variables](../../advanced/settings.md)।

///


## Async পরিবেশ { #async-environments }

সেটিংস synchronous ভাবে লোড হয়। ডিস্ক থেকে পড়ে এমন source ব্যবহার করলে, যেমন dotenv, secrets, JSON, TOML বা
YAML ফাইল, একটি async অ্যাপ্লিকেশনে settings অবজেক্ট তৈরির সময় ফাইলগুলো পড়া চলাকালীন event loop আটকে যেতে পারে।
async context থেকে সেটিংস লোড বা আবার লোড করতে, তৈরির কাজটি একটি worker thread-এ চালান:

⟦CODE101⟧

cache করা একটি settings অবজেক্ট আবার লোড করতে, ভাগ করা instance জায়গায় থেকে বদলানোর চেয়ে বরং একটি worker thread-এ
নতুন instance তৈরি করে cache করা reference-টি বদলে দিন:

⟦CODE102⟧

reference নতুন করে বসানো atomic (একবারে সম্পূর্ণ হয়), তাই একসাথে পড়া চলা কোড সবসময় সম্পূর্ণ তৈরি অবজেক্টই দেখে। উল্টোদিকে,
[জায়গায় থেকে আবার লোড](#in-place-reloading) (`settings.__init__()`) চলার সময় অবজেক্টটি বদলাতে থাকে, তাই আবার লোডের সময়
সেটিংস পড়া একটি coroutine আংশিক-আপডেট হওয়া অবস্থা দেখতে পারে; এর ওপর নির্ভর করলে, আবার লোড আর প্রতিটি
পড়া দুটোই অ্যাপ্লিকেশন-পর্যায়ের lock দিয়ে সুরক্ষিত রাখুন।

/// check | সংক্ষেপে মনে রাখুন

* `class Settings(BaseSettings)` লিখলেই environment variable থেকে মান পড়া আর যাচাই হয়; নাম বড়-ছোট হাত মানে না (Windows-এ কখনোই না)।
* prefix: `env_prefix='APP_'`; নেস্টেড: `env_nested_delimiter='__'`; জটিল মান JSON হিসেবে (`'[1,2]'`), নইলে `NoDecode` + validator।
* `.env`: `model_config = SettingsConfigDict(env_file='.env')`; secret ফাইল: `secrets_dir`।
* অগ্রাধিকার: CLI > init আর্গুমেন্ট > environment > `.env` > secrets > ডিফল্ট; বদলাতে `settings_customise_sources`।
* বারবার লোড এড়াতে `settings_cached()`; কোন মান কোথা থেকে এল দেখতে `PYDANTIC_SETTINGS_DEBUG=1`।

///
