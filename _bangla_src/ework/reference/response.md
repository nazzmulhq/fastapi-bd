# `Response` ক্লাস { #response-class }

/// note | এই পেজে যা পাবেন

* `Response` ব্যবহারের দুটি উপায়: প্যারামিটার হিসেবে নিয়ে হেডার/কুকি বসানো, আর নিজেই রেসপন্স বানিয়ে ফেরত দেওয়া।
* constructor-এর প্যারামিটার (`content`, `status_code`, `headers`, `media_type`, `background`)।
* `set_cookie()` আর `delete_cookie()`-এর প্যারামিটার, উদাহরণসহ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

আপনি একটি *পাথ অপারেশন ফাংশন* বা ডিপেন্ডেন্সিতে `Response` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন, তারপর রেসপন্সের জন্য হেডার বা কুকির মতো ডেটা সেট করতে পারেন।

আপনি সরাসরি এটির একটি ইনস্ট্যান্স তৈরি করে আপনার *পাথ অপারেশন* থেকে ফেরতও দিতে পারেন।

এ সম্পর্কে আরও পড়ুন [একটি কাস্টম Response ফেরত দেওয়া নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/response-directly/#returning-a-custom-response)

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Response
```

## উপায় ১: প্যারামিটার হিসেবে নেওয়া { #bn-as-parameter }

ফাংশনে `response: Response` দিলে FastAPI একটি অস্থায়ী রেসপন্স অবজেক্ট দেয়। তাতে হেডার, কুকি বা স্ট্যাটাস কোড বসান; আর ডেটা স্বাভাবিকভাবেই `return` করুন। FastAPI দুটো মিলিয়ে চূড়ান্ত রেসপন্স বানায়।

```python
from fastapi import FastAPI, Response, status

app = FastAPI()


@app.post("/login")
def login(response: Response):
    response.set_cookie(key="session", value="abc123", httponly=True, max_age=3600)
    response.headers["X-Welcome"] = "true"
    return {"message": "লগইন সফল"}


@app.put("/items/{item_id}")
def upsert(item_id: int, response: Response):
    created = item_id > 100  # ধরে নিচ্ছি নতুন তৈরি হলো
    if created:
        response.status_code = status.HTTP_201_CREATED
    return {"item_id": item_id, "created": created}
```

## উপায় ২: নিজেই রেসপন্স বানিয়ে ফেরত দেওয়া { #bn-return-directly }

`Response(...)` ফেরত দিলে FastAPI কোনো রূপান্তর বা যাচাই করে না, যা দিলেন হুবহু তা-ই যায়।

| প্যারামিটার | কী করে |
| --- | --- |
| `content` | বডি: স্ট্রিং বা bytes |
| `status_code` | স্ট্যাটাস কোড (ডিফল্ট `200`) |
| `headers` | হেডারের ডিকশনারি |
| `media_type` | কনটেন্ট টাইপ, যেমন `"application/xml"` |
| `background` | রেসপন্সের পরে চলবে এমন একটি ব্যাকগ্রাউন্ড টাস্ক |

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/legacy/")
def legacy():
    xml = "<?xml version='1.0'?><shampoo><Header>Apply</Header></shampoo>"
    return Response(content=xml, media_type="application/xml", headers={"X-Format": "xml"})
```

## কুকি বসানো আর মোছা { #bn-cookies }

`set_cookie()`-এর গুরুত্বপূর্ণ প্যারামিটার:

| প্যারামিটার | কী করে |
| --- | --- |
| `key`, `value` | কুকির নাম আর মান |
| `max_age` | কত সেকেন্ড টিকবে |
| `expires` | কখন মেয়াদ শেষ |
| `path`, `domain` | কোন পাথ/ডোমেইনে প্রযোজ্য |
| `secure` | শুধু HTTPS-এ পাঠাবে |
| `httponly` | JavaScript থেকে পড়া যাবে না (নিরাপত্তার জন্য) |
| `samesite` | অন্য সাইট থেকে পাঠানো নিয়ন্ত্রণ: `"lax"`, `"strict"`, `"none"` |

```python
@app.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session")
    return {"message": "লগআউট সম্পন্ন"}
```

/// warning | সাধারণ ভুল

নিজে `Response` ফেরত দিলে `response_model` প্রয়োগ হয় না, ডেটা যাচাই বা ফিল্টার হয় না। JSON ডেটা পাঠাতে সাধারণত শুধু ডিকশনারি বা মডেল `return` করাই ভালো।

///

বিস্তারিত: [রেসপন্স কুকি](../advanced/response-cookies.md), [রেসপন্স হেডার](../advanced/response-headers.md), [স্ট্যাটাস কোড বদলানো](../advanced/response-change-status-code.md)।

/// check | সংক্ষেপে মনে রাখুন

* হেডার/কুকি/স্ট্যাটাস বদলাতে: প্যারামিটারে `response: Response`, ডেটা স্বাভাবিকভাবে `return`।
* পুরো নিয়ন্ত্রণ নিজে চাইলে: `return Response(content=..., media_type=...)`।
* কুকি: `set_cookie(key, value, httponly=True, secure=True, ...)`, মুছতে `delete_cookie(key)`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.Response
