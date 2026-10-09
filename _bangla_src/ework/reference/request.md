# `Request` ক্লাস { #request-class }

/// note | এই পেজে যা পাবেন

কাঁচা রিকোয়েস্ট অবজেক্টের সব অ্যাট্রিবিউট আর মেথড: URL, হেডার, কুকি, ক্লায়েন্টের IP, বডি পড়া ইত্যাদি।

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

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/whoami")
def whoami(request: Request):
    return {
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "path": request.url.path,
    }
```

* `request.client.host`: ক্লায়েন্টের IP ঠিকানা।
* `request.headers`: সব হেডার।
* `request.url.path`: চাওয়া পাথ।

মনে রাখবেন, এখানে FastAPI কোনো যাচাই বা ডকুমেন্টেশন করে না। সম্ভব হলে `Query()`, `Header()` এর মতো সাধারণ প্যারামিটারই ব্যবহার করুন।

///

::: fastapi.Request
