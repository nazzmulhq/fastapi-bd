# `Response` ক্লাস { #response-class }

/// note | এই পেজে যা পাবেন

`Response` ক্লাসের বিস্তারিত: হেডার আর কুকি সেট করা, স্ট্যাটাস কোড, আর নিজে রেসপন্স তৈরি করা।

///

আপনি একটি *পাথ অপারেশন ফাংশন* বা ডিপেন্ডেন্সিতে `Response` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন, তারপর রেসপন্সের জন্য হেডার বা কুকির মতো ডেটা সেট করতে পারেন।

আপনি সরাসরি এটির একটি ইনস্ট্যান্স তৈরি করে আপনার *পাথ অপারেশন* থেকে ফেরতও দিতে পারেন।

এ সম্পর্কে আরও পড়ুন [একটি কাস্টম Response ফেরত দেওয়া নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/response-directly/#returning-a-custom-response)

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Response
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/set-cookie/")
def set_cookie(response: Response):
    response.set_cookie(key="theme", value="dark")
    response.headers["X-Hello"] = "World"
    return {"message": "কুকি সেট হয়েছে"}


@app.get("/legacy/")
def legacy():
    return Response(content="<h1>হ্যালো</h1>", media_type="text/html")
```

* প্রথম রাউট: প্যারামিটার হিসেবে `Response` নিয়ে কুকি আর হেডার যোগ করা, কিন্তু ডেটা স্বাভাবিকভাবেই `dict` হিসেবে ফেরত।
* দ্বিতীয় রাউট: নিজেই একটি `Response` তৈরি করে ফেরত দেওয়া, এতে FastAPI কোনো রূপান্তর করে না।

///

::: fastapi.Response
