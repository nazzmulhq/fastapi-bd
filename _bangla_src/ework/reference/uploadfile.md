# `UploadFile` ক্লাস { #uploadfile-class }

/// note | এই পেজে যা পাবেন

আপলোড করা ফাইলের তথ্য (নাম, আকার, ধরন) আর ফাইল পড়া/লেখার মেথডগুলোর বিস্তারিত তালিকা।

///

রিকোয়েস্ট থেকে ফাইল গ্রহণ করতে আপনি *পাথ অপারেশন ফাংশনের* প্যারামিটারের টাইপ `UploadFile` নির্ধারণ করতে পারেন।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import UploadFile
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/upload/")
async def upload(file: UploadFile):
    content = await file.read()
    return {"filename": file.filename, "size": len(content)}
```

* `file.filename`: ব্যবহারকারীর কম্পিউটারে ফাইলের নাম, যেমন `photo.jpg`।
* `file.content_type`: ফাইলের ধরন, যেমন `image/jpeg`।
* `await file.read()`: ফাইলের বিষয়বস্তু bytes হিসেবে পড়া।

বিস্তারিত দেখুন [রিকোয়েস্ট ফাইল](../tutorial/request-files.md) পেজে।

///

::: fastapi.UploadFile
    options:
        members:
            - file
            - filename
            - size
            - headers
            - content_type
            - read
            - write
            - seek
            - close
