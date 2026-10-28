# পারফরম্যান্সের পরামর্শ { #performance-tips }

/// note | এই পেজে যা শিখবেন

* Pydantic-কে আরও দ্রুত চালানোর প্রমাণিত কৌশলগুলো, প্রতিটি "খারাপ" আর "ভালো" উদাহরণসহ।
* কোন টাইপ বেছে নিলে যাচাই দ্রুত হয় (`list` বনাম `Sequence`, `TypedDict` বনাম নেস্টেড মডেল, tagged union)।
* কখন যাচাই এড়িয়ে যাওয়া যায়, আর `FailFast` দিয়ে আগেভাগে থামা।

///

বেশিরভাগ ক্ষেত্রে Pydantic আপনার অ্যাপের ধীরগতির কারণ (bottleneck) হবে না; নিশ্চিত হলে তবেই এগুলো অনুসরণ করুন।

/// tip | উদাহরণ দিয়ে বুঝি

গাড়ি ধীর চললে আগে দেখুন রাস্তায় জ্যাম (ডেটাবেস, নেটওয়ার্ক) কিনা; ইঞ্জিন টিউন (Pydantic অপ্টিমাইজ) করা শেষ ধাপ। আগে মেপে দেখুন সময় আসলে কোথায় যাচ্ছে।

///

চলমান অ্যাপ্লিকেশনে যাচাইয়ের সময় আসলে কোথায় যাচ্ছে তা খুঁজতে, [Logfire](../integrations/logfire.md)
প্রতিটি Pydantic যাচাইয়ের সময়কাল একটি span হিসেবে রেকর্ড করে।

## সাধারণভাবে, `model_validate(json.loads(...))` নয়, `model_validate_json()` ব্যবহার করুন { #in-general-use-model_validate_json-not-model_validatejsonloads }

`model_validate(json.loads(...))`-এ JSON প্রথমে Python-এ পার্স হয়, তারপর একটি dict-এ রূপান্তরিত হয়, তারপর ভেতরে ভেতরে যাচাই হয়।
অন্যদিকে, `model_validate_json()` ভেতরেই (Rust-এ) পার্সিং আর যাচাই একসাথে করে ফেলে।

```python
import json

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


raw = '{"id": 1, "name": "রহিম"}'

user = User.model_validate_json(raw)          # ✅ এক ধাপে, দ্রুত
user = User.model_validate(json.loads(raw))   # ধীর: আগে Python dict, তারপর যাচাই
```

কিছু ক্ষেত্রে `model_validate(json.loads(...))` দ্রুততর হতে পারে। বিশেষ করে, মডেলে একটি `'before'` বা `'wrap'` validator
ব্যবহার করলে, দুই ধাপের পদ্ধতিতে যাচাই দ্রুত হতে পারে। এই বিশেষ ক্ষেত্রগুলো নিয়ে আরও পড়তে পারেন
[এই আলোচনায়](https://github.com/pydantic/pydantic/discussions/6388#discussioncomment-8193105)।

`pydantic-core`-এর জন্য এখন অনেক পারফরম্যান্স উন্নতির কাজ চলছে, দেখুন
[এই আলোচনা](https://github.com/pydantic/pydantic/discussions/6388#discussioncomment-8194048)।
এই পরিবর্তনগুলো যোগ হলে, আমাদের এমন অবস্থায় পৌঁছানোর কথা যেখানে `model_validate_json()` সবসময় `model_validate(json.loads(...))`-এর চেয়ে দ্রুত।

## `TypeAdapter` একবারই তৈরি করুন { #typeadapter-instantiated-once }

এখানে মূল ভাবনা হলো প্রয়োজনের বেশি validator আর serializer তৈরি এড়ানো। প্রতিবার একটি `TypeAdapter` তৈরি হলে,
এটি একটি নতুন validator আর serializer বানায়। একটি ফাংশনের ভেতরে `TypeAdapter` ব্যবহার করলে, প্রতিবার ফাংশন ডাকার সময়
এটি নতুন করে তৈরি হবে। বদলে একবার তৈরি করে বারবার ব্যবহার করুন।

/// tab | ❌ খারাপ

⟦CODE1⟧

///

/// tab | ✅ ভালো

⟦CODE2⟧

///

## `Sequence` বনাম `list` বা `tuple`, আর `Mapping` বনাম `dict` { #sequence-vs-list-or-tuple-with-mapping-vs-dict }

`Sequence` ব্যবহার করলে, মানটি sequence কিনা পরীক্ষা করতে Pydantic `isinstance(value, Sequence)` ডাকে।
তাছাড়া Pydantic বিভিন্ন ধরনের sequence, যেমন `list` আর `tuple`-এর বিপরীতে যাচাইয়ের চেষ্টা করবে।
মানটি `list` বা `tuple` বলে জানা থাকলে, `Sequence`-এর বদলে `list` বা `tuple` ব্যবহার করুন।

`Mapping` আর `dict`-এর ক্ষেত্রেও একই কথা।
মানটি `dict` বলে জানা থাকলে, `Mapping`-এর বদলে `dict` ব্যবহার করুন।

/// tip | উদাহরণ দিয়ে বুঝি

"যেকোনো ধরনের পাত্র" (`Sequence`) চাইলে পরিদর্শককে বালতি, মগ, গ্লাস সব পরীক্ষা করে দেখতে হয়। "শুধু বালতি" (`list`) বললে এক নজরেই কাজ শেষ।

///

## দরকার না হলে যাচাই করবেন না, মান অপরিবর্তিত রাখতে `Any` ব্যবহার করুন { #dont-do-validation-when-you-dont-have-to-use-any-to-keep-the-value-unchanged }

কোনো মান যাচাইয়ের দরকার না থাকলে, মানটি অপরিবর্তিত রাখতে `Any` ব্যবহার করুন।

⟦CODE3⟧

## primitive-এর subclass দিয়ে বাড়তি তথ্য রাখা এড়িয়ে চলুন { #avoid-extra-information-via-subclasses-of-primitives }

/// tab | এটি করবেন না

⟦CODE4⟧

///

/// tab | এটি করুন

⟦CODE5⟧

///

`str`-এর মতো মৌলিক (primitive) টাইপের subclass বানিয়ে তাতে বাড়তি অ্যাট্রিবিউট রাখলে Pydantic তার দ্রুত পথ ব্যবহার করতে পারে না। বাড়তি তথ্য একটি ছোট মডেলের আলাদা ফিল্ডে রাখুন।

## সাধারণ union নয়, tagged union ব্যবহার করুন { #use-tagged-union-not-union }

tagged union (বা discriminated union) হলো এমন একটি union যাতে একটি ফিল্ড থাকে যা বলে দেয় এটি কোন টাইপ।

⟦CODE6⟧

আরও বিস্তারিত জানতে দেখুন [Discriminated Unions]।

/// info | কেন দ্রুত

সাধারণ union-এ Pydantic একে একে প্রতিটি মডেল দিয়ে চেষ্টা করে দেখে কোনটি মেলে। tagged union-এ সে প্রথমে শুধু `el_type` দেখে (যেমন `'span'`) আর সরাসরি `SpanModel` দিয়ে যাচাই করে; বাকিগুলো চেষ্টাই করে না। এররের বার্তাও পরিষ্কার হয়।

///

## নেস্টেড মডেলের বদলে `TypedDict` ব্যবহার করুন { #use-typeddict-over-nested-models }

নেস্টেড মডেল ব্যবহারের বদলে, ডেটার গঠন সংজ্ঞায়িত করতে `TypedDict` ব্যবহার করুন।

/// details | পারফরম্যান্সের তুলনা
    type: info

একটি সহজ benchmark-এ, `TypedDict` নেস্টেড মডেলের চেয়ে প্রায় ~2.5 গুণ দ্রুত:

⟦CODE7⟧

///

তবে মনে রাখুন, `TypedDict` থেকে পাওয়া ফল সাধারণ ডিকশনারি, মডেল নয়; তাই `.model_dump()`, মেথড বা `obj.a` এর মতো অ্যাট্রিবিউট সুবিধা থাকে না। যেখানে লাখ লাখ রেকর্ড যাচাই হয়, সেখানে এই কৌশল সবচেয়ে কাজের।

## পারফরম্যান্স সত্যিই গুরুত্বপূর্ণ হলে wrap validator এড়িয়ে চলুন { #avoid-wrap-validators-if-you-really-care-about-performance }

wrap validator সাধারণত অন্য validator-এর চেয়ে ধীর। কারণ যাচাইয়ের সময় এগুলোর জন্য
ডেটাকে Python অবজেক্টে রূপ দিতে হয়। জটিল যাচাইয়ের যুক্তির জন্য wrap validator অত্যন্ত কাজের,
কিন্তু সেরা পারফরম্যান্স চাইলে এগুলো এড়িয়ে চলা উচিত।

## `FailFast` দিয়ে আগেভাগে ব্যর্থ হওয়া { #failing-early-with-failfast }

v2.8+ থেকে, sequence টাইপে `FailFast` annotation প্রয়োগ করা যায়, যাতে sequence-এর কোনো আইটেম যাচাইয়ে ব্যর্থ হলেই সাথে সাথে থেমে যায়।
এই annotation ব্যবহার করলে, একটি ব্যর্থ হলে sequence-এর বাকি আইটেমগুলোর যাচাই এরর পাবেন না, অর্থাৎ কার্যত
পারফরম্যান্সের বিনিময়ে সব এরর দেখার সুযোগ ছেড়ে দিচ্ছেন।

⟦CODE8⟧

/// info | কোডটি সহজ ভাষায়

তালিকায় দুটি ভুল মান আছে (`'invalid'` আর `'also invalid'`), কিন্তু এরর এসেছে শুধু প্রথমটির (`1` নম্বর অবস্থান)। প্রথম ভুল পেয়েই যাচাই থেমে গেছে, বাকিগুলো দেখা হয়নি।

///

`FailFast` নিয়ে আরও পড়ুন [এখানে][pydantic.types.FailFast]।

[Discriminated Unions]: ../concepts/unions.md#discriminated-unions

/// check | সংক্ষেপে মনে রাখুন

* আগে মেপে দেখুন; বেশিরভাগ সময় Pydantic ধীরগতির কারণ নয়।
* JSON থেকে: `model_validate_json()`; `TypeAdapter` একবার বানিয়ে বারবার ব্যবহার।
* নির্দিষ্ট টাইপ (`list`, `dict`) সাধারণ টাইপের (`Sequence`, `Mapping`) চেয়ে দ্রুত।
* union-এ discriminator, বড় ডেটায় `TypedDict`, দরকার না হলে `Any`।
* wrap validator এড়ান; শুধু ব্যর্থতা জানতে চাইলে `FailFast`।

///
