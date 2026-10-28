# `UploadFile` ক্লাস { #uploadfile-class }

/// note | এই পেজে যা পাবেন

* `UploadFile` কী, আর `bytes`-এর চেয়ে কেন বড় ফাইলের জন্য ভালো।
* প্রতিটি অ্যাট্রিবিউট (`filename`, `content_type`, `size`, `headers`, `file`) আর মেথড (`read`, `write`, `seek`, `close`), উদাহরণসহ।
* একাধিক ফাইল আপলোড আর ফাইল ডিস্কে সংরক্ষণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

রিকোয়েস্ট থেকে ফাইল গ্রহণ করতে আপনি *পাথ অপারেশন ফাংশনের* প্যারামিটারের টাইপ `UploadFile` নির্ধারণ করতে পারেন।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import UploadFile
```

(ফাইল আপলোড পেতে আগে `pip install python-multipart` করতে হয়।)

## `bytes` নাকি `UploadFile` { #bn-bytes-vs-uploadfile }

| | `bytes` | `UploadFile` |
| --- | --- | --- |
| ফাইল কোথায় থাকে | পুরোটা মেমোরিতে | ছোট হলে মেমোরিতে, বড় হলে অস্থায়ীভাবে ডিস্কে |
| বড় ফাইল (ভিডিও, ছবি) | মেমোরি ফুরিয়ে যেতে পারে | নিরাপদ |
| ফাইলের নাম, টাইপ জানা | যায় না | যায় (`filename`, `content_type`) |
| কখন ব্যবহার | খুব ছোট ফাইল | প্রায় সবসময় |

/// tip | উদাহরণ দিয়ে বুঝি

`bytes` হলো পুরো পার্সেল খুলে সব জিনিস একসাথে হাতে নেওয়া; জিনিস ভারী হলে হাত ব্যথা (মেমোরি শেষ)। `UploadFile` হলো পার্সেলটি টেবিলে রেখে লেবেল দেখা (নাম, টাইপ) আর দরকারমতো একটু একটু করে বের করা।

///

## অ্যাট্রিবিউট { #bn-attributes }

| অ্যাট্রিবিউট | কী রাখে |
| --- | --- |
| `filename` | ব্যবহারকারীর কম্পিউটারে ফাইলের নাম, যেমন `"photo.jpg"` |
| `content_type` | ফাইলের ধরন (MIME type), যেমন `"image/jpeg"` |
| `size` | ফাইলের আকার bytes-এ |
| `headers` | এই ফাইল অংশের হেডার |
| `file` | ভেতরের আসল Python ফাইল অবজেক্ট (সাধারণ `def` ফাংশনে সরাসরি পড়তে) |

## মেথড (সবগুলো `async`, তাই `await` লাগে) { #bn-methods }

| মেথড | কী করে |
| --- | --- |
| `await file.read(size)` | `size` সংখ্যক bytes পড়ে; `size` না দিলে পুরো ফাইল |
| `await file.write(data)` | ফাইলে bytes লেখে |
| `await file.seek(offset)` | ফাইলের ভেতরে নির্দিষ্ট অবস্থানে যায়, যেমন `seek(0)` = শুরুতে ফেরা |
| `await file.close()` | ফাইল বন্ধ করে |

## উদাহরণ { #bn-examples }

### ফাইলের তথ্য দেখা আর পড়া { #bn-read }

```python
from fastapi import FastAPI, HTTPException, UploadFile

app = FastAPI()


@app.post("/upload/")
async def upload(file: UploadFile):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="শুধু JPEG বা PNG ছবি দিন")
    content = await file.read()
    return {"filename": file.filename, "type": file.content_type, "size": len(content)}
```

### বড় ফাইল অংশে অংশে ডিস্কে সংরক্ষণ { #bn-save }

```python
from pathlib import Path

from fastapi import FastAPI, UploadFile

app = FastAPI()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/save/")
async def save(file: UploadFile):
    dest = UPLOAD_DIR / Path(file.filename).name  # নাম থেকে ফোল্ডারের অংশ বাদ
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):  # ১ MB করে
            out.write(chunk)
    return {"saved_as": str(dest)}
```

/// warning | সাধারণ ভুল

ব্যবহারকারীর দেওয়া `filename` সরাসরি ফাইলের পথ হিসেবে ব্যবহার করবেন না; `"../../etc/passwd"` এর মতো নাম দিয়ে অন্য ফোল্ডারে লেখার চেষ্টা হতে পারে। ওপরের উদাহরণের মতো `Path(...).name` দিয়ে শুধু নামটুকু নিন, বা নিজে একটি নতুন নাম বানান।

///

### একাধিক ফাইল { #bn-multiple }

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/photos/")
async def photos(files: list[UploadFile]):
    return {"names": [f.filename for f in files]}
```

বিস্তারিত: [রিকোয়েস্ট ফাইল](../tutorial/request-files.md)।

/// check | সংক্ষেপে মনে রাখুন

* আপলোডের জন্য `file: UploadFile`; নাম `file.filename`, ধরন `file.content_type`, আকার `file.size`।
* পড়তে `await file.read()`; বড় ফাইল অংশে অংশে পড়ুন।
* একাধিক ফাইল: `list[UploadFile]`। `python-multipart` ইনস্টল করতে ভুলবেন না।

///

## পূর্ণ API তালিকা { #bn-full-api }

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
