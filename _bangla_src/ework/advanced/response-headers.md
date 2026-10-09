# রেসপন্সে হেডার { #response-headers }

/// note | এই পেজে যা শিখবেন

* রেসপন্সে নিজের হেডার যোগ করা, দুই উপায়ে।
* ব্রাউজারের JavaScript যেন কাস্টম হেডার দেখতে পায়, সেজন্য কী করতে হয়।

///

## একটি `Response` প্যারামিটার ব্যবহার করুন { #use-a-response-parameter }

আপনার *পাথ অপারেশন ফাংশনে* `Response` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন (কুকির ক্ষেত্রে যেমন করা যায়)।

তারপর ওই *অস্থায়ী* রেসপন্স অবজেক্টে হেডার সেট করতে পারেন।

{* ../../docs_src/response_headers/tutorial002_py310.py hl[1, 7:8] *}

`response.headers["X-Cat-Dog"] = "alone in the world"` লাইনটি রেসপন্সে `X-Cat-Dog` নামে একটি হেডার যোগ করে, ডিকশনারিতে মান রাখার মতোই।

তারপর সাধারণত যেমন করেন, তেমনই প্রয়োজনীয় যেকোনো অবজেক্ট ফেরত দিতে পারেন (একটি `dict`, একটি ডেটাবেস মডেল ইত্যাদি)।

আর আপনি যদি একটি `response_model` ঘোষণা করে থাকেন, তাহলে ফেরত দেওয়া অবজেক্টটি ফিল্টার আর রূপান্তর করতে এটি তখনও ব্যবহার হবে।

**FastAPI** ওই *অস্থায়ী* রেসপন্স থেকে হেডারগুলো (কুকি আর স্ট্যাটাস কোডও) বের করে, আর আপনার ফেরত দেওয়া মানসহ চূড়ান্ত রেসপন্সে সেগুলো রাখবে, যেকোনো `response_model` দিয়ে ফিল্টার করে।

ডিপেন্ডেন্সিতেও `Response` প্যারামিটার ঘোষণা করে সেখানে হেডার (আর কুকি) সেট করতে পারেন।

## সরাসরি একটি `Response` ফেরত দিন { #return-a-response-directly }

সরাসরি একটি `Response` ফেরত দেওয়ার সময়ও হেডার যোগ করতে পারেন।

[সরাসরি একটি Response ফেরত দিন](response-directly.md)-এ বর্ণিত উপায়ে একটি রেসপন্স তৈরি করুন আর হেডারগুলো একটি বাড়তি প্যারামিটার হিসেবে দিন:

{* ../../docs_src/response_headers/tutorial001_py310.py hl[10:12] *}

/// note | কারিগরি বিবরণ

`from starlette.responses import Response` বা `from starlette.responses import JSONResponse`-ও ব্যবহার করতে পারতেন।

**FastAPI** ডেভেলপার হিসেবে আপনার সুবিধার জন্যই একই `starlette.responses`-কে `fastapi.responses` হিসেবে দেয়। কিন্তু উপলব্ধ বেশিরভাগ রেসপন্স সরাসরি Starlette থেকে আসে।

আর যেহেতু হেডার আর কুকি সেট করতে `Response` প্রায়ই ব্যবহার হতে পারে, তাই **FastAPI** এটিকে `fastapi.Response`-এও দেয়।

///

## কাস্টম হেডার { #custom-headers }

মনে রাখবেন, নিজস্ব কাস্টম হেডার [`X-` প্রিফিক্স ব্যবহার করে](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers) যোগ করা যায়।

কিন্তু আপনার যদি এমন কাস্টম হেডার থাকে যা ব্রাউজারের একটি ক্লায়েন্টকে দেখাতে চান, তাহলে [Starlette-এর CORS ডকুমেন্টেশনে](https://starlette.dev/middleware/#corsmiddleware) বর্ণিত `expose_headers` প্যারামিটার ব্যবহার করে সেগুলো আপনার CORS কনফিগারেশনে যোগ করতে হবে (আরও পড়ুন [CORS (Cross-Origin Resource Sharing)](../tutorial/cors.md)-এ)।

/// check | সংক্ষেপে মনে রাখুন

* `response: Response` প্যারামিটার নিয়ে `response.headers["X-Name"] = "value"`।
* বা `JSONResponse(content=..., headers={...})` সরাসরি ফেরত দিন।
* অন্য origin-এর ব্রাউজার JavaScript-কে কাস্টম হেডার দেখাতে CORS-এ `expose_headers` দিন।

///
