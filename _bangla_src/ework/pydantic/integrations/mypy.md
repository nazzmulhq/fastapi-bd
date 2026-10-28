# Mypy { #mypy }

/// note | এই পেজে যা শিখবেন

* mypy (static type checker) দিয়ে Pydantic কোড পরীক্ষা, আর Pydantic-এর mypy plugin কী বাড়তি সুবিধা দেয়।
* plugin চালু করা আর এর তিনটি সেটিং (`init_typed`, `init_forbid_extra`, `warn_required_dynamic_aliases`)।

///

Pydantic কোনো বাড়তি সেটআপ ছাড়াই [mypy](https://www.mypy-lang.org/)-এর সাথে ভালো কাজ করে।

তবে Pydantic-এর সাথে একটি mypy plugin-ও আসে, যা Pydantic-নির্দিষ্ট কিছু গুরুত্বপূর্ণ সুবিধা যোগ করে
আপনার কোডের টাইপ-পরীক্ষার ক্ষমতা বাড়ায়।

/// tip | উদাহরণ দিয়ে বুঝি

mypy হলো প্রুফরিডার, যে বই ছাপার (কোড চালানোর) আগেই ভুল ধরে। কিন্তু সে Pydantic-এর বিশেষ নিয়ম জানে না, যেমন "`'2'` স্ট্রিং দিলেও Pydantic সেটিকে সংখ্যা বানিয়ে নেবে"। plugin হলো প্রুফরিডারের হাতে দেওয়া Pydantic-এর নিয়মের বই, যাতে সে ভুল ধরে কিন্তু অকারণে আপত্তি না তোলে।

///

যেমন, নিচের script-টি দেখুন:

⟦CODE1⟧

কোনো বিশেষ কনফিগারেশন ছাড়া mypy [মডেলের ফিল্ডে annotation না থাকা](../errors/usage_errors.md#model-field-missing-annotation) ধরতে পারে না,
আর `list_of_ints` আর্গুমেন্ট নিয়ে এরর দেয়, যা Pydantic ঠিকভাবেই পার্স করে:

⟦CODE2⟧

কিন্তু [plugin চালু থাকলে](#enabling-the-plugin) এটি সঠিক এররগুলো দেয়:

⟦CODE3⟧

/// info | পার্থক্যটি সহজ ভাষায়

* plugin ছাড়া: `'2'` আর `b'3'` নিয়ে ভুল আপত্তি (Pydantic তো এগুলো সংখ্যা বানিয়ে নেয়), অথচ ৯ নম্বর লাইনে টাইপ ছাড়া `first_name` ফিল্ডটি ধরা পড়েনি।
* plugin সহ: অকারণ আপত্তি নেই, আর আসল ভুলটি (`Untyped fields disallowed`) ধরা পড়েছে।

///

pydantic mypy plugin থাকলে নির্ভয়ে আপনার মডেল refactor করতে পারেন, কারণ জানেন ফিল্ডের নাম বা টাইপ বদলালে
mypy যেকোনো ভুল ধরবে।

মনে রাখুন, Pydantic plugin ছাড়াই mypy কিছু সুবিধা আগে থেকেই সমর্থন করে, যেমন Pydantic মডেল আর dataclass-এর জন্য
`__init__` মেথড তৈরি করা। বাড়তি সুবিধার তালিকার জন্য দেখুন [mypy plugin-এর ক্ষমতা](#mypy-plugin-capabilities)।

Pydantic mypy plugin সর্বশেষ mypy সংস্করণের বিপরীতে পরীক্ষা করা হয়। পুরনো সংস্করণে কাজ করতে পারে, তবে পরীক্ষা করা হবে না।

## plugin চালু করা { #enabling-the-plugin }

plugin চালু করতে, আপনার [mypy config ফাইলে](https://mypy.readthedocs.io/en/latest/config_file.html)
plugin-এর তালিকায় শুধু `pydantic.mypy` যোগ করুন:

/// tab | `mypy.ini`

⟦CODE4⟧

///

/// tab | `pyproject.toml`

⟦CODE5⟧

///

/// note | মনে রাখুন

`pydantic.v1` মডেল ব্যবহার করলে, আপনার plugin-এর তালিকায় `pydantic.v1.mypy` যোগ করতে হবে।

///

আরও বিস্তারিত জানতে দেখুন [plugin কনফিগারেশন](#configuring-the-plugin)।

## mypy plugin-এর ক্ষমতা { #mypy-plugin-capabilities }

### Pydantic মডেলের জন্য একটি `__init__` signature তৈরি { #generate-a-init-signature-for-pydantic-models }

* গতিশীলভাবে নির্ধারিত alias নেই এমন যেকোনো বাধ্যতামূলক ফিল্ড বাধ্যতামূলক keyword আর্গুমেন্ট হিসেবে
  থাকবে।
* [`validate_by_name`][pydantic.ConfigDict.validate_by_name] মডেল কনফিগারেশন মান `True` হলে,
  তৈরি হওয়া signature alias-এর বদলে ফিল্ডের নাম ব্যবহার করবে।
* [`init_forbid_extra`](#init_forbid_extra) আর [`init_typed`](#init_typed) plugin কনফিগারেশন
  মান দিয়ে তৈরি হওয়া `__init__` মেথড আরও সূক্ষ্মভাবে ঠিক করা যায়।

### `model_construct`-এর জন্য একটি টাইপসহ signature তৈরি { #generate-a-typed-signature-for-model_construct }

* ইনপুট ডেটা বৈধ বলে জানা থাকলে আর পার্স করার দরকার না থাকলে, মডেল যাচাইয়ের বিকল্প হলো [`model_construct`][pydantic.BaseModel.model_construct] মেথড
  (দেখুন [ডকুমেন্টেশন](../concepts/models.md#creating-models-without-validation))।
  এই মেথড চলার সময় কোনো যাচাই করে না বলে, এরর ধরতে static পরীক্ষা গুরুত্বপূর্ণ।

### frozen মডেলের সমর্থন { #support-for-frozen-models }

* [`frozen`][pydantic.ConfigDict.frozen] কনফিগারেশন `True` হলে, একটি মডেল ফিল্ড বদলানোর চেষ্টা করলে
  এরর পাবেন (দেখুন [ছদ্ম অপরিবর্তনীয়তা](../concepts/models.md#faux-immutability))

### `Field`-এর `default` আর `default_factory`-এর টাইপ মানা { #respect-the-type-of-the-fields-default-and-default_factory }

* একটি ফিল্ডে `default` আর `default_factory` দুটোই থাকলে static পরীক্ষার সময় এরর হবে।
* `default` আর `default_factory` মানের টাইপ অবশ্যই ফিল্ডের টাইপের সাথে মানানসই হতে হবে।

### টাইপ ছাড়া ফিল্ড ব্যবহারে সতর্কতা { #warn-about-the-use-of-untyped-fields }

* annotation ছাড়া একটি ফিল্ড সংজ্ঞায়িত করলে [চলার সময় এরর](../errors/usage_errors.md#model-field-missing-annotation) হলেও,
  plugin একটি টাইপ-পরীক্ষার এররও দেবে।

### বাধ্যতামূলক গতিশীল alias ব্যবহার আটকানো { #prevent-the-use-of-required-dynamic-aliases }

দেখুন [`warn_required_dynamic_aliases`](#warn_required_dynamic_aliases) plugin কনফিগারেশন মানের ডকুমেন্টেশন।

## plugin কনফিগার করা { #configuring-the-plugin }

plugin-এর সেটিংসের মান বদলাতে, আপনার mypy config ফাইলে `[pydantic-mypy]` নামে একটি অংশ তৈরি করুন,
আর যে সেটিংস বদলাতে চান সেগুলোর key-value জোড়া যোগ করুন।

plugin-এর সব কঠোরতার ফ্ল্যাগ চালু করা (আর mypy-র আরও কিছু কঠোরতার ফ্ল্যাগসহ) একটি কনফিগারেশন ফাইল দেখতে এমন হতে পারে:

/// tab | `mypy.ini`

⟦CODE6⟧

///

/// tab | `pyproject.toml`

⟦CODE7⟧

///

### `init_typed` { #init_typed }

**ডিফল্ট**: `False`।

Pydantic ডিফল্টভাবে [ডেটা রূপান্তর](../concepts/models.md#data-conversion) করে বলে, নিচেরটি চলার সময় তবুও বৈধ:

⟦CODE8⟧

এই কারণে, `__init__()` মেথড তৈরির সময় plugin ফিল্ডের annotation-এর জন্য [`Any`][typing.Any] ব্যবহার করবে,
যদি না `init_typed` সেট থাকে বা মডেলে [strict mode](../concepts/strict_mode.md) চালু থাকে।

### `init_forbid_extra` { #init_forbid_extra }

**ডিফল্ট**: `False`।

ডিফল্টভাবে, Pydantic যেকোনো বাড়তি দেওয়া আর্গুমেন্ট অনুমোদন করে (আর উপেক্ষা করে):

⟦CODE9⟧

এই কারণে, `__init__()` মেথড তৈরির সময় plugin একটি বাড়তি `**kwargs: Any` প্যারামিটার যোগ করবে, যদি না
`init_forbid_extra` সেট থাকে বা [`extra`][pydantic.ConfigDict.extra] কনফিগারেশন মান `'forbid'` হয়।

### `warn_required_dynamic_aliases` { #warn_required_dynamic_aliases }

**ডিফল্ট**: `False`।

[`validate_by_name`][pydantic.ConfigDict.validate_by_name] `False` এমন একটি মডেলে গতিশীলভাবে নির্ধারিত alias
বা alias generator ব্যবহার করলে এরর দেবে কিনা। এমন alias থাকলে
mypy `__init__()`-এর ডাক ঠিকমতো টাইপ-পরীক্ষা করতে পারে না। সেক্ষেত্রে এটি ডিফল্টভাবে
সব আর্গুমেন্টকে বাধ্যতামূলক নয় ধরে, `__init__()`-কে `(**kwargs: Any) -> None` হিসেবে তৈরি করে।

/// check | সংক্ষেপে মনে রাখুন

* `plugins = pydantic.mypy` যোগ করলেই plugin চালু।
* plugin Pydantic-এর রূপান্তরের নিয়ম বোঝে, টাইপ ছাড়া ফিল্ড ধরে, frozen মডেলে মান বসানো ধরে।
* বেশি কঠোর পরীক্ষা চাইলে `[pydantic-mypy]`-এ `init_typed`, `init_forbid_extra`, `warn_required_dynamic_aliases` চালু করুন।

///
