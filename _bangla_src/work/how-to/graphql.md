# GraphQL { #graphql }

যেহেতু **FastAPI** **ASGI** স্ট্যান্ডার্ডের ওপর ভিত্তি করে তৈরি, তাই ASGI-এর সাথে সামঞ্জস্যপূর্ণ যেকোনো **GraphQL** লাইব্রেরি যুক্ত করা খুবই সহজ।

একই অ্যাপ্লিকেশনে আপনি সাধারণ FastAPI *পাথ অপারেশনের* সাথে GraphQL একত্রিত করতে পারেন।

/// tip | পরামর্শ

**GraphQL** কিছু খুবই নির্দিষ্ট ব্যবহারের ক্ষেত্রের সমাধান করে।

প্রচলিত **ওয়েব API**-এর তুলনায় এর **সুবিধা** ও **অসুবিধা** দুটোই আছে।

নিশ্চিত করুন যে আপনি মূল্যায়ন করছেন আপনার ব্যবহারের ক্ষেত্রে **সুবিধাগুলো** **অসুবিধাগুলো** পুষিয়ে দেয় কিনা। 🤓

///

## GraphQL লাইব্রেরি { #graphql-libraries }

**ASGI** সাপোর্ট আছে এমন কিছু **GraphQL** লাইব্রেরি এখানে দেওয়া হলো। আপনি এগুলো **FastAPI**-এর সাথে ব্যবহার করতে পারেন:

* [Strawberry](https://strawberry.rocks/) 🍓
    * [FastAPI-এর জন্য ডকুমেন্টেশনসহ](https://strawberry.rocks/docs/integrations/fastapi)
* [Ariadne](https://ariadnegraphql.org/)
    * [FastAPI-এর জন্য ডকুমেন্টেশনসহ](https://ariadnegraphql.org/server/Integrations/fastapi-integration)
* [Tartiflette](https://tartiflette.io/)
    * ASGI ইন্টিগ্রেশন দিতে [Tartiflette ASGI](https://tartiflette.github.io/tartiflette-asgi/)-সহ
* [Graphene](https://graphene-python.org/)
    * [starlette-graphene3](https://github.com/ciscorn/starlette-graphene3)-সহ

## Strawberry দিয়ে GraphQL { #graphql-with-strawberry }

আপনার যদি **GraphQL** নিয়ে কাজ করতে হয় বা করতে চান, তাহলে [**Strawberry**](https://strawberry.rocks/) হলো **প্রস্তাবিত** লাইব্রেরি, কারণ এর ডিজাইন **FastAPI**-এর ডিজাইনের সবচেয়ে কাছাকাছি, এটি পুরোটাই **টাইপ অ্যানোটেশনের** ওপর ভিত্তি করে তৈরি।

আপনার ব্যবহারের ক্ষেত্রের ওপর নির্ভর করে আপনি হয়তো একটি ভিন্ন লাইব্রেরি ব্যবহার করতে পছন্দ করবেন, তবে আপনি যদি আমাকে জিজ্ঞেস করেন, আমি সম্ভবত আপনাকে **Strawberry** চেষ্টা করে দেখার পরামর্শ দেব।

FastAPI-এর সাথে Strawberry কীভাবে যুক্ত করতে পারেন তার একটি ছোট প্রিভিউ এখানে দেওয়া হলো:

{* ../../docs_src/graphql_/tutorial001_py310.py hl[3,22,25] *}

Strawberry সম্পর্কে আরও জানতে পারেন [Strawberry ডকুমেন্টেশনে](https://strawberry.rocks/)।

এবং [FastAPI-এর সাথে Strawberry](https://strawberry.rocks/docs/integrations/fastapi) সম্পর্কিত ডকুমেন্টেশনেও।

## Starlette-এর পুরোনো `GraphQLApp` { #older-graphqlapp-from-starlette }

Starlette-এর আগের ভার্সনগুলোতে [Graphene](https://graphene-python.org/)-এর সাথে যুক্ত করার জন্য একটি `GraphQLApp` ক্লাস অন্তর্ভুক্ত ছিল।

এটি Starlette থেকে ডেপ্রিকেট করা হয়েছে, তবে আপনার যদি এটি ব্যবহার করা কোড থাকে, তাহলে সহজেই [starlette-graphene3](https://github.com/ciscorn/starlette-graphene3)-এ **মাইগ্রেট** করতে পারেন, যা একই ব্যবহারের ক্ষেত্র কাভার করে এবং যার ইন্টারফেস **প্রায় অভিন্ন**।

/// tip | পরামর্শ

আপনার যদি GraphQL দরকার হয়, তবুও আমি আপনাকে [Strawberry](https://strawberry.rocks/) দেখে নেওয়ার পরামর্শ দেব, কারণ এটি কাস্টম ক্লাস ও টাইপের বদলে টাইপ অ্যানোটেশনের ওপর ভিত্তি করে তৈরি।

///

## আরও জানুন { #learn-more }

**GraphQL** সম্পর্কে আরও জানতে পারেন [অফিসিয়াল GraphQL ডকুমেন্টেশনে](https://graphql.org/)।

ওপরে বর্ণিত প্রতিটি লাইব্রেরি সম্পর্কে তাদের লিংকে আরও পড়তে পারেন।
