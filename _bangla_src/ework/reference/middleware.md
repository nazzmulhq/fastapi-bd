# Middleware { #middleware }

/// note | এই পেজে যা পাবেন

* middleware কী, আর কীভাবে যোগ করতে হয়।
* FastAPI-এর সাথে আসা চারটি তৈরি middleware (CORS, GZip, HTTPS রিডাইরেক্ট, Trusted Host): প্রতিটির সব প্যারামিটার সারণি আর উদাহরণসহ।
* নিজের ছোট middleware লেখা।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

Starlette সরাসরি কয়েকটি middleware দেয়।

এগুলো সম্পর্কে আরও পড়ুন [Middleware নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/middleware/)।

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

middleware হলো অফিসের রিসেপশন। প্রত্যেক অতিথি (রিকোয়েস্ট) ভেতরে যাওয়ার আগে রিসেপশন পার হয়, আর ফেরার পথেও (রেসপন্স)। রিসেপশন পরিচয় দেখতে পারে, অতিথি ফেরাতে পারে, বা ফেরার সময় হাতে একটি ব্যাগ (হেডার) দিতে পারে। প্রতিটি রাউটে আলাদা করে কিছু লিখতে হয় না।

///

| middleware | কী করে |
| --- | --- |
| `CORSMiddleware` | অন্য ডোমেইনের ওয়েবসাইট (যেমন আপনার React ফ্রন্টএন্ড) থেকে আপনার API-তে রিকোয়েস্ট পাঠানোর অনুমতি দেয় |
| `GZipMiddleware` | বড় রেসপন্স সংকুচিত করে পাঠায়, ফলে দ্রুত পৌঁছায় |
| `HTTPSRedirectMiddleware` | `http://` দিয়ে আসা সব রিকোয়েস্ট `https://`-এ পাঠিয়ে দেয় |
| `TrustedHostMiddleware` | শুধু অনুমোদিত ডোমেইন নামের (Host হেডার) রিকোয়েস্ট গ্রহণ করে |

সবগুলো একইভাবে যোগ হয়: `app.add_middleware(MiddlewareClass, প্যারামিটার=...)`।

/// info | ক্রম কেন গুরুত্বপূর্ণ

শেষে যোগ করা middleware সবচেয়ে বাইরে থাকে, অর্থাৎ রিকোয়েস্ট সবার আগে সেটিতেই পৌঁছায়। যেমন `CORSMiddleware` সাধারণত সবশেষে যোগ করা হয়, যাতে অন্য middleware এরর দিলেও রেসপন্সে CORS হেডার থাকে।

///

## `CORSMiddleware` { #bn-cors }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `allow_origins` | `()` | যে ঠিকানাগুলো থেকে রিকোয়েস্ট অনুমোদিত, যেমন `["https://myapp.com"]`; সব অনুমোদনে `["*"]` |
| `allow_origin_regex` | `None` | ঠিকানা মেলানোর regex, যেমন `r"https://.*\.myapp\.com"` |
| `allow_methods` | `("GET",)` | অনুমোদিত HTTP মেথড; সব অনুমোদনে `["*"]` |
| `allow_headers` | `()` | ক্লায়েন্ট যে হেডারগুলো পাঠাতে পারবে; সব অনুমোদনে `["*"]` |
| `allow_credentials` | `False` | কুকি আর `Authorization` হেডার পাঠানো যাবে কিনা |
| `expose_headers` | `()` | ব্রাউজারের JavaScript যে রেসপন্স হেডার পড়তে পারবে |
| `max_age` | `600` | ব্রাউজার CORS অনুমতির ফল কত সেকেন্ড মনে রাখবে |
| `allow_private_network` | `False` | পাবলিক সাইট থেকে লোকাল নেটওয়ার্কের সার্ভারে রিকোয়েস্টের অনুমতি |

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)
```

/// warning | সাধারণ ভুল

`allow_credentials=True` এর সাথে `allow_origins=["*"]` দিলে ব্রাউজার কুকি পাঠাবে না; নিয়ম অনুযায়ী তখন নির্দিষ্ট ঠিকানাগুলো লিখতে হয়।

///

## `GZipMiddleware` { #bn-gzip }

শুধু তখনই সংকোচন করে যখন ক্লায়েন্ট `Accept-Encoding: gzip` হেডার পাঠায়।

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `minimum_size` | `500` | এর চেয়ে ছোট (bytes) রেসপন্স সংকুচিত হবে না |
| `compresslevel` | `9` | সংকোচনের মাত্রা 1 থেকে 9; বেশি মানে ছোট ফাইল কিন্তু বেশি CPU |
| `thread_minimum_size` | `131072` (128 KiB) | এর চেয়ে বড় অংশ আলাদা থ্রেডে সংকুচিত হয়, যাতে সার্ভার আটকে না যায় |
| `exclude_content_types` | gRPC, gzip ইত্যাদি | যে ধরনের রেসপন্স সংকুচিত হবে না (আগে থেকেই সংকুচিত ফাইল) |

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
```

## `HTTPSRedirectMiddleware` { #bn-https-redirect }

কোনো প্যারামিটার নেই। `http`/`ws` রিকোয়েস্ট এলে একই ঠিকানার `https`/`wss` সংস্করণে রিডাইরেক্ট করে।

```python
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

## `TrustedHostMiddleware` { #bn-trusted-host }

`Host` হেডার জাল করে করা আক্রমণ ঠেকায়। অনুমোদিত নয় এমন Host এলে `400` রেসপন্স দেয়।

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `allowed_hosts` | `["*"]` | অনুমোদিত ডোমেইন; `"*.example.com"` দিলে সব সাবডোমেইন |
| `www_redirect` | `True` | `www.example.com` অনুমোদিত থাকলে `example.com`-এর রিকোয়েস্ট `www`-তে রিডাইরেক্ট |

```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"])
```

## নিজের middleware { #bn-custom }

ছোট কাজের জন্য `@app.middleware("http")` ডেকোরেটরই যথেষ্ট:

```python
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)  # রিকোয়েস্ট ভেতরে পাঠানো
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
    return response
```

/// check | সংক্ষেপে মনে রাখুন

* `app.add_middleware(Class, ...)` দিয়ে যোগ করুন; শেষে যোগ করা middleware সবার আগে রিকোয়েস্ট পায়।
* ফ্রন্টএন্ড আলাদা ডোমেইনে থাকলে `CORSMiddleware` লাগবেই।
* বড় JSON/HTML দ্রুত পাঠাতে `GZipMiddleware`; নিরাপত্তায় `HTTPSRedirectMiddleware` আর `TrustedHostMiddleware`।

///

## পূর্ণ API তালিকা { #bn-full-api }

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
