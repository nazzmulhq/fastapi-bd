# `APIRouter` ক্লাস { #apirouter-class }

/// note | এই পেজে যা পাবেন

`APIRouter` ক্লাসের সব প্যারামিটার, অ্যাট্রিবিউট আর মেথডের বিস্তারিত। `APIRouter` হলো একটি "ছোট FastAPI", যা দিয়ে বড় অ্যাপকে একাধিক ফাইলে ভাগ করা হয়।

///

এখানে `APIRouter` ক্লাসের রেফারেন্স তথ্য দেওয়া হলো, এর সব প্যারামিটার, অ্যাট্রিবিউট ও মেথডসহ।

আপনি `APIRouter` ক্লাসটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import APIRouter
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users():
    return [{"username": "Rick"}]


app = FastAPI()
app.include_router(router)
```

* `prefix="/users"`: এই রাউটারের সব পাথের আগে `/users` বসবে, তাই `@router.get("/")` আসলে `/users/`।
* `tags=["users"]`: `/docs`-এ এগুলো "users" দলে দেখাবে।
* `app.include_router(router)`: রাউটারটিকে মূল অ্যাপে যুক্ত করা।

বিস্তারিত দেখুন [বড় অ্যাপ্লিকেশন - একাধিক ফাইল](../tutorial/bigger-applications.md) পেজে।

///

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
