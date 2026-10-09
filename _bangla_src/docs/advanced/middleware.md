# উন্নত মিডলওয়্যার { #advanced-middleware }

/// note | এই পেজে যা শিখবেন

* যেকোনো ASGI মিডলওয়্যার কীভাবে যোগ করবেন।
* FastAPI-এর তৈরি তিনটি কাজের মিডলওয়্যার: HTTPS-এ রিডাইরেক্ট, বৈধ হোস্ট যাচাই, আর GZip সংকোচন।

///

মূল টিউটোরিয়ালে পড়েছেন কীভাবে আপনার অ্যাপ্লিকেশনে [কাস্টম মিডলওয়্যার](../tutorial/middleware.md) যোগ করতে হয়।

তারপর এটাও পড়েছেন কীভাবে [`CORSMiddleware` দিয়ে CORS](../tutorial/cors.md) সামলাতে হয়।

এই অংশে আমরা দেখব কীভাবে অন্য মিডলওয়্যার ব্যবহার করতে হয়।

## ASGI মিডলওয়্যার যোগ করা { #adding-asgi-middlewares }

যেহেতু **FastAPI** তৈরি Starlette-এর ওপর আর <abbr title="Asynchronous Server Gateway Interface">ASGI</abbr> স্পেসিফিকেশন ইমপ্লিমেন্ট করে, তাই আপনি যেকোনো ASGI মিডলওয়্যার ব্যবহার করতে পারেন।

কাজ করার জন্য একটি মিডলওয়্যারকে FastAPI বা Starlette-এর জন্য বানানো হতে হবে না, যতক্ষণ এটি ASGI স্পেসিফিকেশন মেনে চলে।

সাধারণভাবে, ASGI মিডলওয়্যার হলো এমন ক্লাস, যা প্রথম আর্গুমেন্ট হিসেবে একটি ASGI অ্যাপ পাওয়ার আশা করে।

তাই থার্ড-পার্টি ASGI মিডলওয়্যারের ডকুমেন্টেশনে সম্ভবত আপনাকে এরকম কিছু করতে বলবে:

```Python
from unicorn import UnicornMiddleware

app = SomeASGIApp()

new_app = UnicornMiddleware(app, some_config="rainbow")
```

কিন্তু FastAPI (আসলে Starlette) এটি করার একটি সহজ উপায় দেয়, যা নিশ্চিত করে যে অভ্যন্তরীণ মিডলওয়্যারগুলো সার্ভারের এরর সামলায় আর কাস্টম এক্সেপশন হ্যান্ডলারগুলো ঠিকভাবে কাজ করে।

এর জন্য `app.add_middleware()` ব্যবহার করুন (CORS-এর উদাহরণের মতো)।

```Python
from fastapi import FastAPI
from unicorn import UnicornMiddleware

app = FastAPI()

app.add_middleware(UnicornMiddleware, some_config="rainbow")
```

`app.add_middleware()` প্রথম আর্গুমেন্ট হিসেবে একটি মিডলওয়্যার ক্লাস নেয়, আর মিডলওয়্যারে পাঠানোর জন্য যেকোনো বাড়তি আর্গুমেন্ট নেয়।

## একীভূত মিডলওয়্যার { #integrated-middlewares }

**FastAPI**-তে প্রচলিত ব্যবহারের জন্য বেশ কয়েকটি মিডলওয়্যার আছে, এরপর দেখব কীভাবে সেগুলো ব্যবহার করতে হয়।

/// note | কারিগরি বিবরণ

পরের উদাহরণগুলোর জন্য `from starlette.middleware.something import SomethingMiddleware`-ও ব্যবহার করতে পারতেন।

**FastAPI** ডেভেলপার হিসেবে আপনার সুবিধার জন্যই `fastapi.middleware`-এ বেশ কয়েকটি মিডলওয়্যার দেয়। কিন্তু উপলব্ধ বেশিরভাগ মিডলওয়্যার সরাসরি Starlette থেকে আসে।

///

## `HTTPSRedirectMiddleware` { #httpsredirectmiddleware }

নিশ্চিত করে যে সব আসা রিকোয়েস্ট অবশ্যই `https` বা `wss` (নিরাপদ WebSocket) হবে।

`http` বা `ws`-এ আসা যেকোনো রিকোয়েস্ট এর বদলে নিরাপদ স্কিমে রিডাইরেক্ট করা হবে।

{* ../../docs_src/advanced_middleware/tutorial001_py310.py hl[2,6] *}

## `TrustedHostMiddleware` { #trustedhostmiddleware }

HTTP Host Header আক্রমণ থেকে রক্ষা পেতে নিশ্চিত করে যে সব আসা রিকোয়েস্টে সঠিকভাবে সেট করা `Host` হেডার আছে। (অর্থাৎ শুধু আপনার নির্ধারিত ডোমেইন নামেই আসা রিকোয়েস্ট গ্রহণ করা হবে।)

{* ../../docs_src/advanced_middleware/tutorial002_py310.py hl[2,6:8] *}

এই আর্গুমেন্টগুলো সাপোর্টেড:

* `allowed_hosts` - হোস্টনেম হিসেবে অনুমোদিত হওয়া উচিত এমন ডোমেইন নামের একটি তালিকা। সাবডোমেইন মেলাতে `*.example.com`-এর মতো ওয়াইল্ডকার্ড ডোমেইন সাপোর্টেড। যেকোনো হোস্টনেম অনুমোদন করতে হয় `allowed_hosts=["*"]` ব্যবহার করুন, নয়তো মিডলওয়্যারটি বাদ দিন।
* `www_redirect` - True সেট করা থাকলে অনুমোদিত হোস্টগুলোর www ছাড়া সংস্করণে আসা রিকোয়েস্টগুলো তাদের www সংস্করণে রিডাইরেক্ট হবে। ডিফল্ট `True`।

একটি আসা রিকোয়েস্ট সঠিকভাবে যাচাই না হলে একটি `400` রেসপন্স পাঠানো হবে।

## `GZipMiddleware` { #gzipmiddleware }

যেকোনো রিকোয়েস্টের `Accept-Encoding` হেডারে `"gzip"` থাকলে সেটির জন্য GZip রেসপন্স সামলায়।

GZip হলো ডেটা সংকুচিত (compress) করার একটি পদ্ধতি, যেমন ফাইল zip করা। বড় JSON রেসপন্স সংকুচিত করে পাঠালে নেটওয়ার্কে কম ডেটা যায়, তাই দ্রুত পৌঁছায়। ব্রাউজার নিজেই আবার খুলে নেয়।

মিডলওয়্যারটি স্ট্যান্ডার্ড আর স্ট্রিমিং দুই ধরনের রেসপন্সই সামলাবে।

{* ../../docs_src/advanced_middleware/tutorial003_py310.py hl[2,6] *}

এই আর্গুমেন্টগুলো সাপোর্টেড:

* `minimum_size` - বাইটে এই সর্বনিম্ন আকারের চেয়ে ছোট রেসপন্স GZip করবে না। ডিফল্ট `500`। (খুব ছোট ডেটা সংকোচন করে লাভ নেই।)
* `compresslevel` - GZip সংকোচনের সময় ব্যবহার হয়। এটি ১ থেকে ৯ পর্যন্ত একটি পূর্ণসংখ্যা। ডিফল্ট `9`। কম মানে দ্রুত সংকোচন কিন্তু বড় ফাইল, আর বেশি মানে ধীর সংকোচন কিন্তু ছোট ফাইল।

## অন্যান্য মিডলওয়্যার { #other-middlewares }

আরও অনেক ASGI মিডলওয়্যার আছে।

যেমন:

* [Uvicorn-এর `ProxyHeadersMiddleware`](https://github.com/Kludex/uvicorn/blob/main/uvicorn/middleware/proxy_headers.py)
* [MessagePack](https://github.com/florimondmanca/msgpack-asgi)

অন্যান্য উপলব্ধ মিডলওয়্যার দেখতে [Starlette-এর মিডলওয়্যার ডকুমেন্টেশন](https://starlette.dev/middleware/) আর [ASGI Awesome List](https://github.com/florimondmanca/awesome-asgi) দেখুন।

/// check | সংক্ষেপে মনে রাখুন

* যেকোনো ASGI মিডলওয়্যার: `app.add_middleware(MiddlewareClass, অপশন=...)`।
* সব রিকোয়েস্ট HTTPS-এ পাঠাতে `HTTPSRedirectMiddleware`।
* শুধু নিজের ডোমেইনে আসা রিকোয়েস্ট নিতে `TrustedHostMiddleware(allowed_hosts=[...])`।
* বড় রেসপন্স সংকুচিত করতে `GZipMiddleware(minimum_size=1000)`।

///
