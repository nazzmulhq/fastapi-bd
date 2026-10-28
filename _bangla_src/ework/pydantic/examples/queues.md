# Queue { #queues }

/// note | এই পেজে যা শিখবেন

* Redis, RabbitMQ আর ARQ-এর মতো queue (সারি) সিস্টেমে বার্তা পাঠানোর আগে সিরিয়ালাইজ আর নেওয়ার পরে যাচাই করা।
* মূল কৌশল: পাঠাতে `model_dump_json()`, নিতে `model_validate_json()`।
* ব্যর্থ বার্তা পরে খুঁজে পেতে যাচাইয়ের এরর রেকর্ড করা।

///

queue-তে ঢোকা আর queue থেকে বের হওয়া ডেটা যাচাইয়ে Pydantic খুবই কাজের। নিচে
আমরা দেখব বিভিন্ন queue সিস্টেমে কীভাবে ডেটা যাচাই / সিরিয়ালাইজ করতে হয়।

/// tip | উদাহরণ দিয়ে বুঝি

queue হলো ডাকঘরের চিঠির বাক্স: একজন চিঠি ফেলে (producer), আরেকজন পরে তুলে নেয় (consumer)। বাক্সে শুধু লেখা (bytes/স্ট্রিং) রাখা যায়, Python অবজেক্ট নয়। তাই পাঠানোর আগে মডেলকে JSON লেখায় বদলাতে হয় (`model_dump_json()`), আর তোলার পরে লেখা থেকে আবার মডেল বানিয়ে যাচাই করতে হয় (`model_validate_json()`), যাতে পথে কোনো ভুল চিঠি ঢুকলে ধরা পড়ে।

///

## Redis queue { #redis-queue }

Redis একটি জনপ্রিয় in-memory (মেমোরিতে থাকা) ডেটা কাঠামোর ভাণ্ডার।

এই উদাহরণটি নিজের কম্পিউটারে চালাতে, আগে আপনাকে [Redis ইনস্টল](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
করে সার্ভারটি চালু করতে হবে।

Pydantic দিয়ে কীভাবে করা যায় তার একটি সহজ উদাহরণ:

1. queue-তে পাঠানোর জন্য ডেটা সিরিয়ালাইজ করা
2. queue থেকে বের করার সময় ডেটা deserialize আর যাচাই করা

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

* `rpush`: queue-এর শেষে JSON লেখা যোগ করে; `lpop`: শুরু থেকে একটি তুলে নেয়। তাই যে আগে ঢোকে সে আগে বের হয় (FIFO)।
* `r.lpop()` bytes ফেরত দেয়; `User.model_validate_json()` bytes সরাসরি নিতে পারে।
* queue খালি হলে `lpop` `None` দেয়, তাই `if data:` পরীক্ষা।

///

## RabbitMQ { #rabbitmq }

RabbitMQ হলো AMQP প্রোটোকল বাস্তবায়ন করা একটি জনপ্রিয় message broker (বার্তা আদান-প্রদানের মধ্যস্থ)।

এই উদাহরণটি নিজের কম্পিউটারে চালাতে, আগে আপনাকে [RabbitMQ ইনস্টল](https://www.rabbitmq.com/download.html) করে সার্ভার চালু করতে হবে।

Pydantic দিয়ে কীভাবে করা যায় তার একটি সহজ উদাহরণ:

1. queue-তে পাঠানোর জন্য ডেটা সিরিয়ালাইজ করা
2. queue থেকে বের করার সময় ডেটা deserialize আর যাচাই করা

প্রথমে একটি sender (প্রেরক) script তৈরি করি।

⟦CODE2⟧

আর এখানে receiver (গ্রাহক) script।

⟦CODE3⟧

এই উদাহরণ পরীক্ষা করতে:

1. consumer চালু করতে একটি টার্মিনালে receiver script চালান।
2. বার্তা পাঠাতে আরেকটি টার্মিনালে sender script চালান।

এমন consumer-এর ক্ষেত্রে একটি বিষয় মনে রাখতে হবে: `model_validate_json` একটি
[`ValidationError`][pydantic_core.ValidationError] তুললে, যে বার্তার কারণে এটি হলো সেটি আপনি তদন্ত শুরুর সময় হয়তো আর
queue-তে নেই, ফলে ব্যর্থতাটি আবার ঘটিয়ে দেখা কঠিন। তাই ব্যর্থ যাচাই ঘটার সাথে সাথে রেকর্ড করা ভালো,
যেমন [Logfire](../errors/troubleshooting.md) দিয়ে, যা গোছানো এররে তাদের ফিল্ডের অবস্থান আর প্রত্যাখ্যাত মান
ধরে রাখে:

⟦CODE4⟧

/// warning | সাধারণ ভুল

consumer-এ যাচাই এরর না ধরলে পুরো consumer প্রসেস থেমে যেতে পারে, আর বাকি সব বার্তা আটকে থাকে। `try/except ValidationError` দিয়ে ভুল বার্তা লগ করুন (বা আলাদা একটি "dead letter" queue-তে পাঠান), তারপর পরেরটিতে চলে যান।

///

## ARQ { #arq }

ARQ হলো Python-এর জন্য Redis-ভিত্তিক একটি দ্রুত job queue।
এটি Redis-এর ওপর তৈরি আর ব্যাকগ্রাউন্ড কাজ সামলানোর একটি সহজ উপায় দেয়।

এই উদাহরণটি নিজের কম্পিউটারে চালাতে, আপনাকে [Redis ইনস্টল](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) করে সার্ভার চালু করতে হবে।

ARQ-এর সাথে Pydantic দিয়ে কীভাবে করা যায় তার একটি সহজ উদাহরণ:

1. আপনার job ডেটার জন্য একটি মডেল সংজ্ঞায়িত করা
2. job queue-তে দেওয়ার সময় ডেটা সিরিয়ালাইজ করা
3. job প্রক্রিয়ার সময় ডেটা যাচাই আর deserialize করা

⟦CODE5⟧

এই script সম্পূর্ণ।
job queue-তে দেওয়া আর প্রক্রিয়া করা দুটোর জন্যই এটি "যেমন আছে তেমন" চলার কথা।
<!-- TODO: kafka, celery, etc - better for SEO, great for new contributors! -->

/// check | সংক্ষেপে মনে রাখুন

* পাঠানোর আগে: `model.model_dump_json()` → queue।
* নেওয়ার পরে: queue → `Model.model_validate_json(data)`।
* consumer-এ `ValidationError` ধরুন আর লগ করুন, যাতে একটি ভুল বার্তায় পুরো সারি থেমে না যায়।

///
