# Exceptions - `HTTPException` এবং `WebSocketException` { #exceptions-httpexception-and-websocketexception }

/// note | এই পেজে যা পাবেন

ক্লায়েন্টকে এরর দেখানোর জন্য যে এক্সেপশনগুলো raise করা যায়, তাদের সব প্যারামিটারের বিস্তারিত।

///

এগুলো হলো সেই এক্সেপশন যা ক্লায়েন্টকে এরর দেখাতে আপনি raise করতে পারেন।

যখন আপনি একটি এক্সেপশন raise করেন, সাধারণ Python-এর মতোই, বাকি কাজ বাতিল হয়ে যায়। এভাবে কোডের যেকোনো জায়গা থেকে এই এক্সেপশনগুলো raise করে একটি রিকোয়েস্ট বাতিল করে ক্লায়েন্টকে এরর দেখাতে পারেন।

আপনি ব্যবহার করতে পারেন:

* `HTTPException`
* `WebSocketException`

এই এক্সেপশনগুলো সরাসরি `fastapi` থেকে ইম্পোর্ট করা যায়:

```python
from fastapi import HTTPException, WebSocketException
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()
items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")
def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="আইটেম পাওয়া যায়নি")
    return {"item": items[item_id]}
```

`/items/bar` চাইলে ক্লায়েন্ট পাবে `404` স্ট্যাটাস আর `{"detail": "আইটেম পাওয়া যায়নি"}`। `raise` হওয়ার সাথে সাথে ফাংশনের বাকি অংশ আর চলে না। বিস্তারিত দেখুন [এরর সামলানো](../tutorial/handling-errors.md) পেজে।

///

::: fastapi.HTTPException

::: fastapi.WebSocketException
