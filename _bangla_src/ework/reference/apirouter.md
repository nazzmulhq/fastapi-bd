# `APIRouter` ক্লাস { #apirouter-class }

/// note | এই পেজে যা পাবেন

* `APIRouter` কী, আর কেন বড় অ্যাপকে একাধিক ফাইলে ভাগ করতে এটি লাগে।
* `APIRouter()` তৈরির প্রতিটি প্যারামিটারের অর্থ, উদাহরণসহ।
* রাউটারকে অ্যাপে (বা অন্য রাউটারে) যুক্ত করার নিয়ম আর প্যারামিটার কীভাবে মিলে যায়।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

এখানে `APIRouter` ক্লাসের রেফারেন্স তথ্য দেওয়া হলো, এর সব প্যারামিটার, অ্যাট্রিবিউট ও মেথডসহ।

আপনি `APIRouter` ক্লাসটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import APIRouter
```

## এক নজরে { #bn-overview }

`APIRouter` হলো একটি "ছোট FastAPI"। এতে `FastAPI` অ্যাপের মতোই `@router.get()`, `@router.post()` ইত্যাদি দিয়ে রাউট লেখা যায়, কিন্তু এটি নিজে চলে না; পরে `app.include_router(router)` দিয়ে মূল অ্যাপে যুক্ত করতে হয়।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বড় শপিং মলের কথা ভাবুন। মল (`FastAPI` অ্যাপ) একটাই, কিন্তু ভেতরে আলাদা আলাদা দোকান (`APIRouter`): পোশাকের দোকান, বইয়ের দোকান। প্রতিটি দোকান নিজের জিনিস নিজে সাজায় (নিজের ফাইলে নিজের রাউট), আর মল শুধু জায়গা দেয় ("দ্বিতীয় তলা = `/books`")।

///

```python
# app/routers/books.py
from fastapi import APIRouter

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/")
def list_books():
    return [{"title": "পথের পাঁচালী"}]


@router.get("/{book_id}")
def get_book(book_id: int):
    return {"id": book_id}
```

```python
# app/main.py
from fastapi import FastAPI

from .routers import books

app = FastAPI()
app.include_router(books.router)
# রাউটগুলো: GET /books/ আর GET /books/{book_id}
```

## `APIRouter()` তৈরির প্যারামিটার { #bn-constructor-params }

### সবচেয়ে বেশি ব্যবহৃত { #bn-common-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `prefix` | এই রাউটারের সব পাথের শুরুতে বসবে, যেমন `"/books"` (শেষে `/` দেবেন না) |
| `tags` | সব রাউটের ডকসের দল, যেমন `["books"]` |
| `dependencies` | এই রাউটারের সব রাউটে চলবে এমন ডিপেন্ডেন্সি (যেমন লগইন যাচাই) |
| `responses` | সব রাউটের ডকসে বাড়তি রেসপন্স, যেমন `{404: {"description": "পাওয়া যায়নি"}}` |
| `deprecated` | `True` দিলে সব রাউট ডকসে deprecated দেখাবে |
| `include_in_schema` | `False` দিলে সব রাউট ডকস থেকে লুকানো থাকবে |

```python
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token হেডার ভুল")


router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(verify_token)],
    responses={404: {"description": "পাওয়া যায়নি"}},
)


@router.get("/")
async def read_items():
    return [{"name": "কলম"}]
```

(এখানে `/items/`-এর প্রতিটি রিকোয়েস্টে আগে `verify_token` চলবে; ভুল হেডার হলে রাউট পর্যন্ত পৌঁছাবেই না।)

### অন্যান্য প্যারামিটার { #bn-other-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `default_response_class` | এই রাউটারের ডিফল্ট রেসপন্স ক্লাস, যেমন `HTMLResponse` |
| `callbacks` | সব রাউটের OpenAPI callback |
| `route_class` | রাউট তৈরিতে ব্যবহৃত ক্লাস; নিজের `APIRoute` সাব-ক্লাস দিয়ে আচরণ বদলানো যায় |
| `generate_unique_id_function` | operation ID তৈরির নিজস্ব ফাংশন |
| `redirect_slashes` | `/x` আর `/x/`-এর মধ্যে স্বয়ংক্রিয় রিডাইরেক্ট |
| `strict_content_type` | JSON বডির জন্য `Content-Type` হেডার বাধ্যতামূলক কিনা |
| `lifespan`, `on_startup`, `on_shutdown` | রাউটার স্তরের চালু/বন্ধের কাজ (সাধারণত অ্যাপেই দেওয়া হয়) |
| `routes`, `default`, `dependency_overrides_provider` | Starlette/ভেতরের কাজের জন্য; সাধারণত নিজে ব্যবহার করবেন না |

```python
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

pages = APIRouter(default_response_class=HTMLResponse, include_in_schema=False)


@pages.get("/about")
def about():
    return "<h1>আমাদের সম্পর্কে</h1>"
```

বিস্তারিত: [কাস্টম Request আর APIRoute ক্লাস](../how-to/custom-request-and-route.md)।

## রাউটার যুক্ত করা: `include_router()` { #bn-include-router }

`app.include_router()` বা `router.include_router()`-এ দেওয়া `prefix`, `tags`, `dependencies`, `responses` রাউটারের নিজের সেটিংয়ের সাথে **যোগ হয়**:

* `prefix` জোড়া লাগে: অ্যাপে `/api` + রাউটারে `/books` = `/api/books`।
* `tags`, `dependencies`, `responses` তালিকায় মিলে যায় (দুই জায়গার সবগুলোই প্রযোজ্য)।

```python
from fastapi import APIRouter, FastAPI

v1 = APIRouter(prefix="/v1")
books = APIRouter(prefix="/books", tags=["books"])


@books.get("/")
def list_books():
    return []


v1.include_router(books)  # রাউটারের ভেতরে রাউটার
app = FastAPI()
app.include_router(v1, prefix="/api", tags=["v1"])
# চূড়ান্ত পাথ: GET /api/v1/books/   tags: ["v1", "books"]
```

/// warning | সাধারণ ভুল

`include_router()` কল করার **পরে** রাউটারে নতুন রাউট যোগ করলে সেটি অ্যাপে দেখা যাবে না, কারণ যুক্ত করার মুহূর্তে রাউটগুলো কপি হয়। আগে সব রাউট লিখুন, তারপর `include_router()`।

///

## রাউটারের মেথড { #bn-methods }

`APIRouter`-এর মেথডগুলো `FastAPI`-এর মতোই:

* `get()`, `post()`, `put()`, `patch()`, `delete()`, `options()`, `head()`, `trace()`: পাথ অপারেশন তৈরি। প্রতিটি প্যারামিটারের অর্থ দেখুন [`FastAPI` ক্লাসের পাথ অপারেশন ডেকোরেটর](fastapi.md#bn-decorators) অংশে।
* `websocket()`: WebSocket রাউট।
* `include_router()`: আরেকটি রাউটার এর ভেতরে যুক্ত করা।
* `frontend()`: স্ট্যাটিক ফ্রন্টএন্ড ফাইল পরিবেশন (দেখুন [`FastAPI.frontend()`](fastapi.md#bn-frontend))।
* `on_event()`: (পুরনো) startup/shutdown ইভেন্ট।

/// check | সংক্ষেপে মনে রাখুন

* প্রতিটি বিষয়ের (users, items, orders) জন্য একটি `APIRouter`, আলাদা ফাইলে।
* `APIRouter(prefix=..., tags=..., dependencies=...)` দিয়ে সেই দলের সব রাউটে একসাথে সেটিং।
* শেষে `app.include_router(router)`; দুই জায়গার prefix জোড়া লাগে, tags আর dependencies মিলে যায়।

///

বিস্তারিত: [বড় অ্যাপ্লিকেশন - একাধিক ফাইল](../tutorial/bigger-applications.md)।

## পূর্ণ API তালিকা { #bn-full-api }

নিচে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ তালিকা: প্রতিটি প্যারামিটারের টাইপ, ডিফল্ট মান আর বিস্তারিত বর্ণনা।

::: fastapi.APIRouter
    options:
        members:
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
