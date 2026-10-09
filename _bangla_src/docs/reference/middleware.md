# Middleware { #middleware }

/// note | এই পেজে যা পাবেন

FastAPI-এর সাথে আসা চারটি তৈরি middleware-এর সব প্যারামিটার: CORS, GZip, HTTPS রিডাইরেক্ট আর Trusted Host।

///

Starlette সরাসরি কয়েকটি middleware দেয়।

এগুলো সম্পর্কে আরও পড়ুন [Middleware নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/middleware/)।

/// info | কোন middleware কী করে

* `CORSMiddleware`: অন্য ডোমেইনের ওয়েবসাইট (যেমন আপনার React ফ্রন্টএন্ড) থেকে আপনার API-তে রিকোয়েস্ট পাঠানোর অনুমতি দেয়।
* `GZipMiddleware`: বড় রেসপন্স সংকুচিত করে পাঠায়, ফলে দ্রুত পৌঁছায়।
* `HTTPSRedirectMiddleware`: `http://` দিয়ে আসা সব রিকোয়েস্ট `https://`-এ পাঠিয়ে দেয়।
* `TrustedHostMiddleware`: শুধু অনুমোদিত ডোমেইন নামের (Host হেডার) রিকোয়েস্ট গ্রহণ করে।

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

এখানে `http://localhost:3000`-এ চলা ফ্রন্টএন্ডকে আপনার API ব্যবহারের অনুমতি দেওয়া হলো।

///

::: fastapi.middleware.cors.CORSMiddleware

এটি `fastapi` থেকে ইম্পোর্ট করা যায়:

```python
from fastapi.middleware.cors import CORSMiddleware
```

::: fastapi.middleware.gzip.GZipMiddleware

এটি `fastapi` থেকে ইম্পোর্ট করা যায়:

```python
from fastapi.middleware.gzip import GZipMiddleware
```

::: fastapi.middleware.httpsredirect.HTTPSRedirectMiddleware

এটি `fastapi` থেকে ইম্পোর্ট করা যায়:

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
```

::: fastapi.middleware.trustedhost.TrustedHostMiddleware

এটি `fastapi` থেকে ইম্পোর্ট করা যায়:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
```
