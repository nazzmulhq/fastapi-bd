# `FastAPI` ক্লাস { #fastapi-class }

/// note | এই পেজে যা পাবেন

`FastAPI` ক্লাসের সব প্যারামিটার, অ্যাট্রিবিউট আর মেথডের বিস্তারিত তালিকা। আপনার পুরো অ্যাপ্লিকেশনটিই এই ক্লাসের একটি অবজেক্ট: `app = FastAPI()`।

///

এখানে `FastAPI` ক্লাসের রেফারেন্স তথ্য দেওয়া হলো, এর সব প্যারামিটার, অ্যাট্রিবিউট ও মেথডসহ।

আপনি `FastAPI` ক্লাসটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import FastAPI
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI

app = FastAPI(
    title="আমার দোকানের API",
    version="1.0.0",
    docs_url="/docs",
)


@app.get("/")
def home():
    return {"message": "স্বাগতম"}
```

* `title`, `version`: `/docs`-এ যে নাম আর সংস্করণ দেখাবে।
* `docs_url`: ইন্টারঅ্যাকটিভ ডকস কোন URL-এ থাকবে (`None` দিলে বন্ধ)।
* `@app.get("/")`: নিচের তালিকার `get` মেথড, একটি GET পাথ অপারেশন তৈরি করে।

///

/// info | সবচেয়ে বেশি ব্যবহৃত অংশগুলো

* **প্যারামিটার (তৈরির সময়):** `title`, `description`, `version`, `docs_url`, `redoc_url`, `openapi_url`, `lifespan`, `dependencies`, `middleware`, `root_path`।
* **ডেকোরেটর মেথড:** `get`, `post`, `put`, `delete`, `patch`: পাথ অপারেশন তৈরি করে। `websocket`: WebSocket রাউট।
* **অন্যান্য মেথড:** `include_router` (একটি `APIRouter` যুক্ত করা), `exception_handler` (এরর সামলানোর ফাংশন), `middleware` (middleware যুক্ত করা)।
* **অ্যাট্রিবিউট:** `dependency_overrides` (টেস্টে ডিপেন্ডেন্সি বদলানো), `state` (অ্যাপজুড়ে ডেটা রাখা), `openapi()` (OpenAPI স্কিমা পাওয়া)।

নিচের তালিকায় প্রতিটির পূর্ণ বিবরণ আছে।

///

::: fastapi.FastAPI
    options:
        members:
            - openapi_version
            - webhooks
            - state
            - dependency_overrides
            - openapi
            - websocket
            - include_router
            - frontend
            - get
            - put
            - post
            - delete
            - options
            - head
            - patch
            - trace
            - on_event
            - middleware
            - exception_handler
