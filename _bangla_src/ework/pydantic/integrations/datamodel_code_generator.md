# datamodel-code-generator দিয়ে কোড তৈরি { #code-generation-with-datamodel-code-generator }

/// note | এই পেজে যা শিখবেন

* OpenAPI, JSON Schema, JSON/YAML/CSV ডেটা বা GraphQL schema থেকে স্বয়ংক্রিয়ভাবে Pydantic মডেল তৈরি।
* তৈরি হওয়া মডেল আর উৎসের schema সরে গেলে (drift) তা কীভাবে ধরা পড়ে।

///

[datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator/) প্রজেক্টটি একটি লাইব্রেরি আর কমান্ড-লাইন টুল, যা প্রায় যেকোনো ডেটা উৎস থেকে pydantic মডেল তৈরি করে, যেমন:

* OpenAPI 3 (YAML/JSON)
* JSON Schema
* JSON/YAML/CSV ডেটা (যা JSON Schema-তে রূপান্তরিত হবে)
* Python ডিকশনারি (যা JSON Schema-তে রূপান্তরিত হবে)
* GraphQL schema

যখনই এমন কোনো ডেটা হাতে থাকে যা JSON-এ রূপান্তরযোগ্য কিন্তু তার pydantic মডেল নেই, এই টুল দিয়ে দরকারমতো টাইপ-নিরাপদ মডেলের কাঠামো তৈরি করতে পারবেন।

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি বড় পেমেন্ট কোম্পানির API-র OpenAPI ফাইলে ২০০টি ডেটা কাঠামো আছে। হাতে ২০০টি মডেল লেখা ক্লান্তিকর আর ভুলপ্রবণ। এই টুল সেই নকশা (schema) পড়ে সব মডেল একবারে লিখে দেয়, যেমন স্থপতির নকশা দেখে যন্ত্র ইট সাজায়।

///

## ইনস্টলেশন { #installation }

```bash
pip install datamodel-code-generator
```

## উদাহরণ { #example }

এক্ষেত্রে, datamodel-code-generator একটি JSON Schema ফাইল থেকে pydantic মডেল তৈরি করে।

```bash
datamodel-codegen  --input person.json --input-file-type jsonschema --output model.py
```

person.json:

⟦CODE1⟧

model.py:

⟦CODE2⟧

/// info | কোডটি সহজ ভাষায়

* schema-র `required`-এ থাকা `first_name` আর `last_name` বাধ্যতামূলক ফিল্ড হয়েছে; বাকিগুলো `| None = None` সহ ঐচ্ছিক।
* `"minimum": 0` হয়েছে `conint(ge=0)`, আর `description` হয়েছে `Field(description=...)`।
* `definitions`-এর `Pet` আলাদা মডেল হয়েছে, আর `pets` হলো তার তালিকা।

///

আরও তথ্য পাওয়া যাবে
[অফিসিয়াল ডকুমেন্টেশনে](https://datamodel-code-generator.koxudaxi.dev/)।

## উৎসের schema থেকে সরে যাওয়া ধরা { #catching-drift-from-the-source-schema }

একটি OpenAPI বা JSON Schema ডকুমেন্ট থেকে তৈরি মডেল হলো সেই চুক্তির একটি স্থিরচিত্র (snapshot)। উৎসের
ডেটা এর সাথে মেলা বন্ধ করলে (একটি ফিল্ডের টাইপ বদলায়, একটি নতুন বাধ্যতামূলক ফিল্ড আসে), অমিলটি
চলার সময় একটি [`ValidationError`][pydantic_core.ValidationError] হিসেবে দেখা দেয়, যা প্রায়ই প্রথম সংকেত যে
উৎসটি আপনার মডেল তৈরির schema থেকে সরে গেছে।

যদি [Logfire দিয়ে যাচাই রেকর্ড করেন](../errors/troubleshooting.md), সেই ব্যর্থতাগুলো তাদের
গোছানো এরর আর প্রত্যাখ্যাত মানসহ জমা থাকে, ফলে দেখতে পারেন *কী* বদলেছে আর *কবে* শুরু হয়েছে;
এটি কাজে লাগে যখন schema আপনার নয় আর কী সরেছে না জানা পর্যন্ত মডেল আবার তৈরি করতে পারছেন না।

/// check | সংক্ষেপে মনে রাখুন

* `pip install datamodel-code-generator`, তারপর `datamodel-codegen --input ফাইল --input-file-type ধরন --output model.py`।
* উৎসের schema বদলালে মডেল আবার তৈরি করুন; চলার সময় `ValidationError` প্রায়ই সেই বদলের প্রথম সংকেত।

///
