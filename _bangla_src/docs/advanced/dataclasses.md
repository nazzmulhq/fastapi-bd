# Dataclass ব্যবহার { #using-dataclasses }

/// note | এই পেজে যা শিখবেন

* Pydantic মডেলের বদলে Python-এর সাধারণ `dataclass` দিয়ে রিকোয়েস্ট ও রেসপন্স ঘোষণা করা।
* `response_model`-এ আর নেস্টেড কাঠামোতে dataclass।

///

FastAPI তৈরি **Pydantic**-এর ওপর, আর আমি আপনাকে দেখিয়েছি রিকোয়েস্ট আর রেসপন্স ঘোষণা করতে কীভাবে Pydantic মডেল ব্যবহার করতে হয়।

কিন্তু FastAPI একইভাবে [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) ব্যবহারও সাপোর্ট করে:

{* ../../docs_src/dataclasses_/tutorial001_py310.py hl[1,6:11,18:19] *}

/// tip | dataclass সহজ ভাষায়

`@dataclass` হলো Python-এর নিজস্ব একটি ডেকোরেটর, যা শুধু অ্যাট্রিবিউটের তালিকা লিখেই একটি ডেটা রাখার ক্লাস বানিয়ে দেয়, `__init__` আলাদা করে লিখতে হয় না। দেখতে Pydantic মডেলের মতোই, তবে এটি Python-এর স্ট্যান্ডার্ড লাইব্রেরির অংশ।

///

এটি এখনো সাপোর্টেড **Pydantic**-এর কল্যাণে, কারণ এতে [`dataclasses`-এর অভ্যন্তরীণ সাপোর্ট](https://pydantic.dev/docs/validation/latest/concepts/dataclasses/#usage-of-stdlib-dataclasses-with-basemodel) আছে।

তাই, ওপরের কোড স্পষ্টভাবে Pydantic ব্যবহার না করলেও, FastAPI ওই স্ট্যান্ডার্ড dataclass-গুলোকে Pydantic-এর নিজস্ব ধরনের dataclass-এ রূপান্তর করতে Pydantic ব্যবহার করছে।

আর অবশ্যই, এটি একই জিনিসগুলো সাপোর্ট করে:

* ডেটা যাচাই
* ডেটা সিরিয়ালাইজেশন
* ডেটা ডকুমেন্টেশন ইত্যাদি

এটি Pydantic মডেলের মতোই কাজ করে। আর ভেতরে আসলে একইভাবে, Pydantic ব্যবহার করেই এটি অর্জন করা হয়।

/// note | নোট

মনে রাখবেন, Pydantic মডেল যা যা করতে পারে, dataclass সবকিছু করতে পারে না।

তাই আপনার হয়তো তবুও Pydantic মডেল ব্যবহার করতে হতে পারে।

কিন্তু আপনার যদি আগে থেকে একগাদা dataclass পড়ে থাকে, তাহলে FastAPI দিয়ে একটি ওয়েব API চালাতে সেগুলো ব্যবহারের এটি একটি সুন্দর কৌশল। 🤓

///

## `response_model`-এ dataclass { #dataclasses-in-response-model }

`response_model` প্যারামিটারেও `dataclasses` ব্যবহার করতে পারেন:

{* ../../docs_src/dataclasses_/tutorial002_py310.py hl[1,6:12,18] *}

dataclass-টি স্বয়ংক্রিয়ভাবে একটি Pydantic dataclass-এ রূপান্তরিত হবে।

এভাবে এর স্কিমা API ডকুমেন্টেশন ইউজার ইন্টারফেসে দেখাবে:

<img src="/img/tutorial/dataclasses/image01.png">

`tags: list[str] = field(default_factory=list)` মানে প্রতিটি নতুন অবজেক্টের জন্য একটি নতুন খালি তালিকা। (dataclass-এ সরাসরি `= []` লেখা যায় না, কারণ তাতে সব অবজেক্ট একই তালিকা ভাগাভাগি করত।)

## নেস্টেড ডেটা কাঠামোতে dataclass { #dataclasses-in-nested-data-structures }

নেস্টেড ডেটা কাঠামো বানাতে `dataclasses`-কে অন্য টাইপ অ্যানোটেশনের সাথেও মেলাতে পারেন।

কিছু ক্ষেত্রে আপনাকে হয়তো তবুও Pydantic-এর `dataclasses` সংস্করণ ব্যবহার করতে হতে পারে। যেমন, স্বয়ংক্রিয়ভাবে তৈরি API ডকুমেন্টেশনে এরর পেলে।

সেক্ষেত্রে শুধু স্ট্যান্ডার্ড `dataclasses`-কে `pydantic.dataclasses` দিয়ে বদলে দিতে পারেন, যা হুবহু বসিয়ে দেওয়া যায় এমন একটি বিকল্প:

{* ../../docs_src/dataclasses_/tutorial003_py310.py hl[1,4,7:10,13:16,22:24,27] *}

1. আমরা এখনো স্ট্যান্ডার্ড `dataclasses` থেকে `field` ইমপোর্ট করি।

2. `pydantic.dataclasses` হলো `dataclasses`-এর হুবহু বসিয়ে দেওয়া যায় এমন বিকল্প।

3. `Author` dataclass-এ `Item` dataclass-এর একটি তালিকা আছে।

4. `Author` dataclass-টি `response_model` প্যারামিটার হিসেবে ব্যবহার হয়েছে।

5. রিকোয়েস্ট বডি হিসেবে dataclass-এর সাথে অন্য স্ট্যান্ডার্ড টাইপ অ্যানোটেশন ব্যবহার করতে পারেন।

    এই ক্ষেত্রে এটি `Item` dataclass-এর একটি তালিকা।

6. এখানে আমরা এমন একটি ডিকশনারি ফেরত দিচ্ছি, যাতে `items` আছে, যা dataclass-এর একটি তালিকা।

    FastAPI তবুও ডেটাকে JSON-এ <dfn title="ডেটাকে পাঠানো যায় এমন একটি ফরম্যাটে রূপান্তর করা">সিরিয়ালাইজ</dfn> করতে সক্ষম।

7. এখানে `response_model` `Author` dataclass-এর একটি তালিকার টাইপ অ্যানোটেশন ব্যবহার করছে।

    আবারও, `dataclasses`-কে স্ট্যান্ডার্ড টাইপ অ্যানোটেশনের সাথে মেলাতে পারেন।

8. খেয়াল করুন, এই *পাথ অপারেশন ফাংশন* `async def`-এর বদলে সাধারণ `def` ব্যবহার করে।

    বরাবরের মতো, FastAPI-তে দরকার অনুযায়ী `def` আর `async def` মেলাতে পারেন।

    কখন কোনটা ব্যবহার করবেন তা ঝালিয়ে নিতে চাইলে [`async` আর `await`](../async.md#in-a-hurry) নিয়ে ডকুমেন্টেশনের _"তাড়া আছে?"_ অংশটি দেখুন।

9. এই *পাথ অপারেশন ফাংশন* dataclass ফেরত দিচ্ছে না (যদিও দিতে পারত), বরং ভেতরের ডেটাসহ ডিকশনারির একটি তালিকা ফেরত দিচ্ছে।

    রেসপন্স রূপান্তর করতে FastAPI `response_model` প্যারামিটার (যাতে dataclass আছে) ব্যবহার করবে।

জটিল ডেটা কাঠামো তৈরি করতে `dataclasses`-কে অন্য টাইপ অ্যানোটেশনের সাথে অনেক ভিন্ন ভিন্ন সংমিশ্রণে মেলাতে পারেন।

আরও নির্দিষ্ট খুঁটিনাটি দেখতে ওপরের কোডের ভেতরের অ্যানোটেশনের পরামর্শগুলো দেখুন।

## আরও জানুন { #learn-more }

`dataclasses`-কে অন্য Pydantic মডেলের সাথেও মেলাতে পারেন, সেগুলো থেকে ইনহেরিট করতে পারেন, আপনার নিজের মডেলে অন্তর্ভুক্ত করতে পারেন, ইত্যাদি।

আরও জানতে [dataclass নিয়ে Pydantic ডকুমেন্টেশন](https://pydantic.dev/docs/validation/latest/concepts/dataclasses/) দেখুন।

## সংস্করণ { #version }

এটি FastAPI সংস্করণ `0.67.0` থেকে উপলব্ধ। 🔖

/// check | সংক্ষেপে মনে রাখুন

* `@dataclass` দিয়ে বানানো ক্লাস Pydantic মডেলের মতোই বডি, রেসপন্স মডেল ইত্যাদিতে ব্যবহার করা যায়।
* সমস্যা হলে `from pydantic.dataclasses import dataclass` ব্যবহার করুন।
* নতুন কোডে সাধারণত Pydantic মডেলই ভালো, dataclass পুরোনো কোড পুনরায় ব্যবহারের জন্য সুবিধাজনক।

///
