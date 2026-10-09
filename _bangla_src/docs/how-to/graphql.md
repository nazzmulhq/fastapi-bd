# GraphQL { #graphql }

/// note | এই পেজে যা শিখবেন

* GraphQL কী, আর সাধারণ REST API থেকে এর পার্থক্য।
* FastAPI-এর সাথে কোন GraphQL লাইব্রেরিগুলো ব্যবহার করা যায়।
* Strawberry দিয়ে FastAPI-তে একটি GraphQL এন্ডপয়েন্ট যোগ করা।

///

যেহেতু **FastAPI** **ASGI** স্ট্যান্ডার্ডের ওপর ভিত্তি করে তৈরি, তাই ASGI-র সাথে মানানসই যেকোনো **GraphQL** লাইব্রেরি যুক্ত করা খুবই সহজ।

একই অ্যাপ্লিকেশনে সাধারণ FastAPI *পাথ অপারেশনের* সাথে GraphQL একসাথে ব্যবহার করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ REST API হলো রেস্টুরেন্টের সেট মেনু: `/users/1` চাইলে যা যা আছে সব পাবেন, দরকার থাকুক বা না থাকুক। **GraphQL** হলো "নিজের মতো থালা সাজান": ক্লায়েন্ট একটি প্রশ্নে (query) ঠিক যে ফিল্ডগুলো চায় তা লিখে দেয়, যেমন শুধু `name` আর `age`, আর সার্ভার ঠিক ততটুকুই ফেরত দেয়। সব কিছু একটি মাত্র এন্ডপয়েন্টে (সাধারণত `/graphql`) যায়।

///

/// tip | পরামর্শ

**GraphQL** কিছু খুবই নির্দিষ্ট সমস্যার সমাধান করে।

সাধারণ **ওয়েব API**-এর তুলনায় এর **সুবিধা** আর **অসুবিধা** দুটোই আছে।

নিশ্চিত করুন যে আপনার ক্ষেত্রে **সুবিধাগুলো** **অসুবিধাগুলোকে** পুষিয়ে দেয় কিনা তা আপনি মূল্যায়ন করেছেন। 🤓

///

## GraphQL লাইব্রেরি { #graphql-libraries }

**ASGI** সাপোর্ট আছে এমন কিছু **GraphQL** লাইব্রেরি এখানে দেওয়া হলো। আপনি এগুলো **FastAPI**-এর সাথে ব্যবহার করতে পারেন:

* [Strawberry](https://strawberry.rocks/) 🍓
    * [FastAPI-এর জন্য ডকস](https://strawberry.rocks/docs/integrations/fastapi)-সহ
* [Ariadne](https://ariadnegraphql.org/)
    * [FastAPI-এর জন্য ডকস](https://ariadnegraphql.org/server/Integrations/fastapi-integration)-সহ
* [Tartiflette](https://tartiflette.io/)
    * ASGI সংযোগ দিতে [Tartiflette ASGI](https://tartiflette.github.io/tartiflette-asgi/)-সহ
* [Graphene](https://graphene-python.org/)
    * [starlette-graphene3](https://github.com/ciscorn/starlette-graphene3)-সহ

## Strawberry দিয়ে GraphQL { #graphql-with-strawberry }

যদি **GraphQL** নিয়ে কাজ করা দরকার হয় বা করতে চান, তাহলে [**Strawberry**](https://strawberry.rocks/) হলো **সুপারিশকৃত** লাইব্রেরি, কারণ এর ডিজাইন **FastAPI**-এর ডিজাইনের সবচেয়ে কাছাকাছি, এটি পুরোটাই **টাইপ অ্যানোটেশনের** ওপর ভিত্তি করে তৈরি।

আপনার প্রয়োজন অনুযায়ী আপনি হয়তো অন্য কোনো লাইব্রেরি পছন্দ করতে পারেন, কিন্তু আমাকে জিজ্ঞেস করলে, আমি সম্ভবত আপনাকে **Strawberry** চেষ্টা করে দেখার পরামর্শ দেব।

FastAPI-এর সাথে Strawberry কীভাবে যুক্ত করতে পারেন তার একটি ছোট ঝলক এখানে:

{* ../../docs_src/graphql_/tutorial001_py310.py hl[3,22,25] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৬–৯: `@strawberry.type` দিয়ে একটি GraphQL টাইপ `User`, যার `name` আর `age` আছে, ঠিক Python টাইপ দিয়ে।
* লাইন ১২–১৬: `Query` টাইপ, যেখানে `user` ফিল্ডটি একটি `User` ফেরত দেয়।
* লাইন ১৯: এই query দিয়ে একটি GraphQL স্কিমা তৈরি।
* লাইন ২২: `GraphQLRouter(schema)` স্কিমাটিকে একটি FastAPI রাউটারে রূপান্তর করে।
* লাইন ২৫: রাউটারটি `/graphql` প্রিফিক্সে যুক্ত করা হলো। এখন ব্রাউজারে `/graphql`-এ গেলে GraphQL প্লেগ্রাউন্ড পাবেন, যেখানে `{ user { name } }` এর মতো query লিখে দেখতে পারেন।

///

Strawberry সম্পর্কে আরও জানতে পারেন [Strawberry ডকুমেন্টেশনে](https://strawberry.rocks/)।

আর [FastAPI-এর সাথে Strawberry](https://strawberry.rocks/docs/integrations/fastapi) নিয়ে ডকসেও।

## Starlette-এর পুরনো `GraphQLApp` { #older-graphqlapp-from-starlette }

Starlette-এর আগের সংস্করণগুলোতে [Graphene](https://graphene-python.org/)-এর সাথে যুক্ত করার জন্য একটি `GraphQLApp` ক্লাস ছিল।

Starlette থেকে এটি পুরনো (deprecated) ঘোষণা করা হয়েছে, কিন্তু যদি আপনার এমন কোড থাকে যা এটি ব্যবহার করত, তাহলে সহজেই [starlette-graphene3](https://github.com/ciscorn/starlette-graphene3)-এ **স্থানান্তর** করতে পারেন, যা একই কাজ করে আর যার **প্রায় হুবহু একই ইন্টারফেস** আছে।

/// tip | পরামর্শ

যদি GraphQL দরকার হয়, আমি তবুও [Strawberry](https://strawberry.rocks/) দেখার পরামর্শ দেব, কারণ এটি কাস্টম ক্লাস আর টাইপের বদলে টাইপ অ্যানোটেশনের ওপর ভিত্তি করে তৈরি।

///

## আরও জানুন { #learn-more }

**GraphQL** সম্পর্কে আরও জানতে পারেন [অফিসিয়াল GraphQL ডকুমেন্টেশনে](https://graphql.org/)।

ওপরে বর্ণিত প্রতিটি লাইব্রেরি সম্পর্কেও তাদের লিংকে আরও পড়তে পারেন।

/// check | সংক্ষেপে মনে রাখুন

* GraphQL-এ ক্লায়েন্ট নিজেই বলে দেয় কোন ফিল্ড চায়, সব একটি এন্ডপয়েন্টে।
* FastAPI-এর সাথে সবচেয়ে মানানসই লাইব্রেরি Strawberry (টাইপ অ্যানোটেশন-ভিত্তিক)।
* `app.include_router(GraphQLRouter(schema), prefix="/graphql")` দিয়ে যুক্ত করুন, বাকি সাধারণ পাথ অপারেশন পাশাপাশি চলতে থাকবে।

///
