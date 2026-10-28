# `Request` ক্লাস { #request-class }

/// note | এই পেজে যা পাবেন

* কাঁচা রিকোয়েস্ট অবজেক্ট কখন দরকার।
* প্রতিটি গুরুত্বপূর্ণ অ্যাট্রিবিউট (`method`, `url`, `headers`, `query_params`, `path_params`, `cookies`, `client`, `state`, `app`) আর মেথড (`body()`, `json()`, `form()`, `stream()`, `is_disconnected()`, `url_for()`), উদাহরণসহ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

আপনি একটি *পাথ অপারেশন ফাংশন* বা ডিপেন্ডেন্সিতে `Request` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন, তারপর কোনো যাচাই ইত্যাদি ছাড়াই সরাসরি কাঁচা রিকোয়েস্ট অবজেক্ট ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [সরাসরি Request ব্যবহার নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/using-request-directly/)

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Request
```

/// tip | পরামর্শ

যখন এমন ডিপেন্ডেন্সি তৈরি করতে চান যা HTTP আর WebSocket দুটোর সাথেই মানানসই হবে, তখন `Request` বা `WebSocket`-এর বদলে `HTTPConnection` নেয় এমন একটি প্যারামিটার সংজ্ঞায়িত করতে পারেন।

///

/// warning | কখন ব্যবহার করবেন

সম্ভব হলে `Query()`, `Header()`, `Body()` এর মতো সাধারণ প্যারামিটার ব্যবহার করুন; সেগুলোতে যাচাই আর `/docs` ডকুমেন্টেশন নিজে থেকে হয়। `Request` থেকে সরাসরি পড়া ডেটা যাচাই হয় না, ডকসেও দেখায় না। `Request` দরকার হয় মূলত middleware-এ, ক্লায়েন্টের IP জানতে, `request.state` ব্যবহারে, বা টেমপ্লেটে।

///

## অ্যাট্রিবিউট { #bn-attributes }

| অ্যাট্রিবিউট | কী রাখে | উদাহরণ |
| --- | --- | --- |
| `method` | HTTP মেথড | `"GET"` |
| `url` | পূর্ণ URL অবজেক্ট (`.path`, `.query`, `.hostname` ...) | `request.url.path` → `"/items/5"` |
| `base_url` | অ্যাপের মূল ঠিকানা | `"http://localhost:8000/"` |
| `headers` | সব হেডার (বড়-ছোট হাতের পার্থক্য নেই) | `request.headers["user-agent"]` |
| `query_params` | কোয়েরি প্যারামিটার | `request.query_params.get("q")` |
| `path_params` | পাথ প্যারামিটারের ডিকশনারি | `{"item_id": "5"}` |
| `cookies` | কুকির ডিকশনারি | `request.cookies.get("session")` |
| `client` | ক্লায়েন্টের `host` আর `port` | `request.client.host` |
| `state` | এই রিকোয়েস্টের জন্য নিজের ডেটা রাখার জায়গা | `request.state.user = ...` |
| `app` | যে `FastAPI` অ্যাপ রিকোয়েস্টটি সামলাচ্ছে | `request.app.state.db` |
| `scope` | ASGI-র কাঁচা তথ্যের ডিকশনারি | (অ্যাডভান্সড) |

## মেথড (বেশিরভাগ `async`) { #bn-methods }

| মেথড | কী করে |
| --- | --- |
| `await request.body()` | কাঁচা বডি `bytes` হিসেবে |
| `await request.json()` | বডি JSON হিসেবে পার্স করে |
| `await request.form()` | ফর্ম ডেটা (ফাইলসহ) |
| `request.stream()` | বডি অংশে অংশে পড়ার async iterator |
| `await request.is_disconnected()` | ক্লায়েন্ট সংযোগ ছেড়ে চলে গেছে কিনা |
| `request.url_for(name, **path_params)` | রাউটের নাম থেকে পূর্ণ URL তৈরি |

## উদাহরণ { #bn-examples }

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/items/{item_id}", name="get_item")
def get_item(item_id: int, request: Request):
    return {
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "all_query": dict(request.query_params),
        "self_url": str(request.url_for("get_item", item_id=item_id)),
    }


@app.post("/webhook")
async def webhook(request: Request):
    raw = await request.body()  # স্বাক্ষর যাচাইয়ের জন্য কাঁচা bytes
    data = await request.json()
    return {"size": len(raw), "event": data.get("event")}
```

### middleware থেকে `request.state`-এ ডেটা রাখা { #bn-state }

```python
import uuid

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    return await call_next(request)


@app.get("/")
def home(request: Request):
    return {"request_id": request.state.request_id}
```

/// check | সংক্ষেপে মনে রাখুন

* প্যারামিটারে `request: Request` দিলে পুরো রিকোয়েস্ট হাতে পাবেন।
* `request.headers`, `request.query_params`, `request.cookies`, `request.client.host`, `request.url`।
* বডি পড়তে `await request.json()` বা `await request.body()`; নিজের ডেটা রাখতে `request.state`।
* যাচাই আর ডকস চাইলে সাধারণ প্যারামিটারই ভালো।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.Request
