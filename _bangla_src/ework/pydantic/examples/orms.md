# ডেটাবেস { #databases }

/// note | এই পেজে যা শিখবেন

* ORM (যেমন SQLAlchemy) অবজেক্ট থেকে Pydantic মডেল তৈরি (`from_attributes=True`)।
* SQLAlchemy-র সংরক্ষিত নামের (`metadata`) সাথে সংঘাত alias দিয়ে এড়ানো।
* কোড দ্বিগুণ লেখা এড়াতে SQLModel।

///

ORM (object relational mapping) লাইব্রেরির জন্য মডেল সংজ্ঞায়িত করার দারুণ টুল Pydantic।
ORM ব্যবহার হয় Python অবজেক্টকে ডেটাবেসের টেবিলে, আর টেবিলকে অবজেক্টে রূপান্তর করতে।

/// tip | উদাহরণ দিয়ে বুঝি

ORM হলো অনুবাদক: ডেটাবেসের সারি (row) কে Python অবজেক্টে আর উল্টোটায় অনুবাদ করে। Pydantic মডেল সেই অবজেক্ট থেকে প্রয়োজনীয় অংশ নিয়ে, যাচাই করে, API-তে পাঠানোর উপযোগী রূপ দেয়।

///

## SQLAlchemy { #sqlalchemy }

Pydantic SQLAlchemy-র সাথে জোড় বাঁধতে পারে, কারণ ডেটাবেস মডেলের schema সংজ্ঞায়িত করতে এটি ব্যবহার করা যায়।

/// warning | কোডের পুনরাবৃত্তি

SQLAlchemy-র সাথে Pydantic ব্যবহার করলে, একই কোড দুবার লেখার ঝামেলায় বিরক্ত হতে পারেন।
এই সমস্যায় পড়লে [`SQLModel`](https://sqlmodel.tiangolo.com/) বিবেচনা করতে পারেন, যা Pydantic আর SQLAlchemy-কে এমনভাবে একসাথে করে যে কোডের পুনরাবৃত্তি অনেকটাই দূর হয়।

///

SQLAlchemy-র সাথে বিশুদ্ধ Pydantic ব্যবহার করতে চাইলে, নিচের উদাহরণের মতো SQLAlchemy মডেলের পাশাপাশি
Pydantic মডেল ব্যবহারের পরামর্শ দিই। এক্ষেত্রে, SQLAlchemy-র একটি সংরক্ষিত (reserved) ফিল্ডের নামে একটি `Column` রাখতে আমরা Pydantic-এর alias সুবিধা কাজে লাগাই, ফলে সংঘাত এড়ানো যায়।

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

* `from_attributes=True`: ডিকশনারি নয়, যেকোনো অবজেক্টের অ্যাট্রিবিউট (`obj.metadata_`) থেকে মান পড়তে দেয়; ORM অবজেক্টের জন্য এটি জরুরি।
* SQLAlchemy মডেলে `metadata` নামটি আগে থেকেই দখল করা, তাই Python-এ অ্যাট্রিবিউটের নাম `metadata_`, যদিও ডেটাবেসের কলামের নাম `metadata`।
* Pydantic মডেলে ফিল্ডের নাম `metadata`, কিন্তু `alias='metadata_'` বলে দেয় "অবজেক্ট থেকে `metadata_` অ্যাট্রিবিউট পড়ো"।
* `model_dump()` ফিল্ডের নাম দেয়, `model_dump(by_alias=True)` দেয় alias।

///

/// note | মনে রাখুন

ওপরের উদাহরণটি কাজ করে কারণ ফিল্ড পূরণের ক্ষেত্রে ফিল্ডের নামের চেয়ে alias অগ্রাধিকার পায়।
`SQLModel`-এর `metadata` অ্যাট্রিবিউট পড়লে একটি `ValidationError` হতো।

///

ORM অবজেক্ট যাচাই করলে এক ধরনের কম চোখে পড়া ব্যর্থতা ধরা পড়তে পারে: শর্ত যোগ করার আগে
লেখা সারি, বা এমন কলাম যা `NULL` অনুমোদন করে অথচ আপনার মডেল করে না। এগুলো শুধু তখনই ব্যর্থ হয় যখন সমস্যার
সারিটি আসলে পড়া হয়, যা deploy-এর অনেক পরে হতে পারে, আর
[ব্যর্থ যাচাই রেকর্ড করা](../errors/troubleshooting.md) তাদের গোছানো এরর আর
প্রত্যাখ্যাত মান ধরে রাখে, যা সমস্যার ডেটা শনাক্ত করতে সাহায্য করতে পারে।

/// tip | FastAPI-তে

FastAPI-তে `response_model` হিসেবে `from_attributes=True` সহ একটি Pydantic মডেল দিলে, পাথ অপারেশন থেকে সরাসরি ORM অবজেক্ট ফেরত দেওয়া যায়; FastAPI নিজেই রূপান্তর করে নেয়। দেখুন [SQL (Relational) ডেটাবেস](../../tutorial/sql-databases.md)।

///

<!-- TODO: add examples for Django with Pydantic models -->

/// check | সংক্ষেপে মনে রাখুন

* ORM অবজেক্ট থেকে মডেল: `model_config = ConfigDict(from_attributes=True)` আর `Model.model_validate(orm_obj)`।
* নামের সংঘাত এড়াতে alias।
* একই কাঠামো দুবার লেখা এড়াতে SQLModel।

///
