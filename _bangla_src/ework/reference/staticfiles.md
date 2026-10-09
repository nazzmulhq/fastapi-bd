# Static Files - `StaticFiles` { #static-files-staticfiles }

/// note | এই পেজে যা পাবেন

`StaticFiles` ক্লাসের বিস্তারিত, যা একটি ফোল্ডার থেকে JavaScript, CSS, ছবির মতো স্থির (static) ফাইল পরিবেশন করে।

///

JavaScript, CSS, ছবি ইত্যাদির মতো স্ট্যাটিক ফাইল পরিবেশন করতে `StaticFiles` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [স্ট্যাটিক ফাইল নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/static-files/)।

আপনি এটি সরাসরি `fastapi.staticfiles` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.staticfiles import StaticFiles
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
```

এখন `static/logo.png` ফাইলটি পাওয়া যাবে `http://127.0.0.1:8000/static/logo.png` ঠিকানায়।

///

::: fastapi.staticfiles.StaticFiles
