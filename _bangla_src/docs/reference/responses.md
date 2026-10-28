# কাস্টম রেসপন্স ক্লাস - File, HTML, Redirect, Streaming, ইত্যাদি { #custom-response-classes-file-html-redirect-streaming-etc }

/// note | এই পেজে যা পাবেন

* কোন রেসপন্স ক্লাস কখন ব্যবহার করবেন, তার সারণি।
* সব রেসপন্স ক্লাসের সাধারণ প্যারামিটার।
* প্রতিটি ক্লাস (`JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `FileResponse`, `StreamingResponse`) আলাদা করে, নিজস্ব প্যারামিটার আর উদাহরণসহ।
* `response_class` দিয়ে ডকসে সঠিক ধরন দেখানো।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

কয়েকটি কাস্টম রেসপন্স ক্লাস আছে, যেগুলোর একটি ইনস্ট্যান্স তৈরি করে সরাসরি আপনার *পাথ অপারেশন* থেকে ফেরত দিতে পারেন।

এ সম্পর্কে আরও পড়ুন [কাস্টম রেসপন্স - HTML, Stream, File, অন্যান্য নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/custom-response/)।

আপনি এগুলো সরাসরি `fastapi.responses` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
    UJSONResponse,
)
```

## এক নজরে { #bn-overview }

| ক্লাস | কী ফেরত দেয় | কখন |
| --- | --- | --- |
| `JSONResponse` | JSON | ডিফল্ট; নিজে লিখতে হয় শুধু স্ট্যাটাস/হেডার বদলাতে |
| `HTMLResponse` | HTML পেজ | ব্রাউজারে একটি পেজ দেখাতে |
| `PlainTextResponse` | সাধারণ টেক্সট | শুধু লেখা ফেরত দিতে |
| `RedirectResponse` | অন্য URL-এ পাঠানো | লগইনের পরে অন্য পেজে নিতে, পুরনো ঠিকানা বদলাতে |
| `FileResponse` | ডিস্কের একটি ফাইল | ডাউনলোড, ছবি, PDF |
| `StreamingResponse` | ধাপে ধাপে ডেটা | বড় ফাইল, লাইভ ডেটা, তৈরি হতে থাকা CSV |
| `Response` | যা খুশি | সব নিয়ন্ত্রণ নিজে রাখতে (দেখুন [`Response` ক্লাস](response.md)) |

/// tip | উদাহরণ দিয়ে বুঝি

রেসপন্স ক্লাস হলো পার্সেলের প্যাকেট। চিঠির জন্য খাম (`PlainTextResponse`), ছবির অ্যালবামের জন্য শক্ত বাক্স (`FileResponse`), পানির জন্য পাইপ (`StreamingResponse`), আর "এই ঠিকানায় যান" লেখা চিরকুট (`RedirectResponse`)। ভেতরের জিনিস অনুযায়ী ঠিক প্যাকেট বেছে নিলে ক্লায়েন্ট (ব্রাউজার) ঠিকভাবে বুঝতে পারে।

///

### সব ক্লাসের সাধারণ প্যারামিটার { #bn-common-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `content` | যা পাঠাবেন (প্রতিটি ক্লাসের নিজের ধরন অনুযায়ী) |
| `status_code` | স্ট্যাটাস কোড, ডিফল্ট `200` |
| `headers` | বাড়তি হেডারের ডিকশনারি |
| `media_type` | `Content-Type`; প্রতিটি ক্লাসের নিজের ডিফল্ট আছে |
| `background` | রেসপন্স পাঠানোর পরে চলবে এমন একটি `BackgroundTask` |

সবগুলোতে `set_cookie()` আর `delete_cookie()` মেথডও আছে।

## `JSONResponse` { #bn-jsonresponse }

`content` হিসেবে JSON-যোগ্য ডেটা নেয় (`dict`, `list`, `str`, সংখ্যা...)। Pydantic মডেল বা `datetime` থাকলে আগে [`jsonable_encoder`](encoders.md) দিয়ে রূপান্তর করুন।

```python
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str


@app.post("/items/")
def create_item(item: Item):
    return JSONResponse(
        status_code=201,
        content=jsonable_encoder(item),
        headers={"Location": f"/items/{item.name}"},
    )
```

/// warning | মনে রাখুন

সরাসরি `JSONResponse` ফেরত দিলে `response_model` প্রয়োগ হয় না আর ডেটা যাচাই হয় না। শুধু স্ট্যাটাস কোড বদলাতে চাইলে ডেকোরেটরে `status_code=201` দেওয়াই সহজ।

///

## `HTMLResponse` { #bn-htmlresponse }

`content` হলো HTML লেখা (স্ট্রিং)। `response_class=HTMLResponse` দিলে স্ট্রিং ফেরত দিলেই চলে, আর ডকসেও দেখায় যে এটি HTML ফেরত দেয়।

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>স্বাগতম</title></head>
        <body><h1>আমার সাইটে স্বাগতম</h1></body>
    </html>
    """
```

## `PlainTextResponse` { #bn-plaintextresponse }

```python
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()


@app.get("/health", response_class=PlainTextResponse)
def health():
    return "OK"
```

## `RedirectResponse` { #bn-redirectresponse }

| প্যারামিটার | কী করে |
| --- | --- |
| `url` | কোথায় পাঠাবে |
| `status_code` | ডিফল্ট `307` (মেথড একই থাকে); স্থায়ীভাবে সরলে `301`/`308`; ফর্ম পাঠানোর পরে অন্য পেজে নিতে `303` |

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/old-page")
def old_page():
    return RedirectResponse("/new-page", status_code=301)


@app.post("/login")
def login():
    # ফর্ম জমার পরে ড্যাশবোর্ডে, ব্রাউজার GET দিয়ে খুলবে
    return RedirectResponse("/dashboard", status_code=303)
```

## `FileResponse` { #bn-fileresponse }

ফাইলটি অল্প অল্প করে (async ভাবে) পড়ে পাঠায়, তাই বড় ফাইলেও মেমোরি ভরে না।

| প্যারামিটার | কী করে |
| --- | --- |
| `path` | ডিস্কে ফাইলের পথ |
| `filename` | ডাউনলোডের সময় ব্যবহারকারী যে নাম দেখবে |
| `media_type` | না দিলে ফাইলের এক্সটেনশন দেখে নিজে থেকে ঠিক করে |
| `content_disposition_type` | `"attachment"` (ডিফল্ট, ডাউনলোড হয়) বা `"inline"` (ব্রাউজারে খোলে); শুধু `filename` দিলে প্রযোজ্য |

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


@app.get("/report")
def report():
    return FileResponse("files/report-2024.pdf", filename="বার্ষিক-রিপোর্ট.pdf")


@app.get("/report/view")
def view_report():
    return FileResponse(
        "files/report-2024.pdf",
        filename="report.pdf",
        content_disposition_type="inline",
    )
```

## `StreamingResponse` { #bn-streamingresponse }

`content` হিসেবে একটি iterator বা async iterator নেয় (যেমন `yield` থাকা জেনারেটর ফাংশন), আর প্রতিটি অংশ তৈরি হওয়ামাত্র পাঠিয়ে দেয়।

```python
import csv
import io

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


def make_csv():
    for i in range(1, 100_001):
        buf = io.StringIO()
        csv.writer(buf).writerow([i, f"user{i}@example.com"])
        yield buf.getvalue()


@app.get("/export.csv")
def export():
    return StreamingResponse(
        make_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )
```

১ লাখ সারির পুরো ফাইল মেমোরিতে না বানিয়ে, প্রতিটি সারি তৈরি হতেই পাঠানো হচ্ছে।

/// tip | পরামর্শ

লাইভ ঘটনা (নোটিফিকেশন, AI-এর উত্তর) পাঠাতে [Server-Sent Events](sse.md) আরও সুবিধাজনক।

///

## ডিফল্ট রেসপন্স ক্লাস বদলানো { #bn-default-response-class }

পুরো অ্যাপের জন্য: `FastAPI(default_response_class=HTMLResponse)`। একটি রাউটের জন্য: ডেকোরেটরে `response_class=...`। এতে ফেরত দেওয়া মান সেই ক্লাসে মোড়ানো হয় আর `/docs`-এ সঠিক `Content-Type` দেখায়।

/// check | সংক্ষেপে মনে রাখুন

* JSON ডিফল্ট; HTML-এর জন্য `HTMLResponse`, লেখার জন্য `PlainTextResponse`।
* অন্য পেজে পাঠাতে `RedirectResponse(url, status_code=...)`।
* ফাইল পাঠাতে `FileResponse(path, filename=...)`; ধাপে ধাপে ডেটার জন্য `StreamingResponse(generator)`।
* নিজে রেসপন্স ফেরত দিলে যাচাই আর `response_model` প্রয়োগ হয় না।

///

## পূর্ণ API তালিকা { #bn-full-api }

নিচে প্রতিটি ক্লাসের সব প্যারামিটার আর মেথডের স্বয়ংক্রিয় তালিকা।

## FastAPI রেসপন্স { #fastapi-responses }

JSON পারফরম্যান্স বাড়ানোর উদ্দেশ্যে কয়েকটি কাস্টম FastAPI রেসপন্স ক্লাস ছিল।

তবে এগুলো এখন পুরনো (deprecated), কারণ এখন [রেসপন্স মডেল - রিটার্ন টাইপ](https://fastapi.tiangolo.com/tutorial/response-model/) ব্যবহার করলেই আপনি আরও ভালো পারফরম্যান্স পাবেন।

এভাবে Pydantic Rust-এর দিকে ডেটাকে JSON bytes-এ সিরিয়ালাইজ করবে, যা এই কাস্টম JSON রেসপন্সগুলোর চেয়ে ভালো পারফরম্যান্স দেবে।

এ সম্পর্কে আরও পড়ুন [কাস্টম রেসপন্স - HTML, Stream, File, অন্যান্য - `orjson` নাকি রেসপন্স মডেল](https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model)-এ।

::: fastapi.responses.UJSONResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.ORJSONResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

## Starlette রেসপন্স { #starlette-responses }

এগুলোর সবকটি সম্পর্কে আরও পড়তে পারেন [কাস্টম রেসপন্স নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/custom-response/) আর [Responses নিয়ে Starlette ডকসে](https://starlette.dev/responses/)।

::: fastapi.responses.FileResponse
    options:
        members:
            - chunk_size
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.HTMLResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.JSONResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.PlainTextResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.RedirectResponse
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.Response
    options:
        members:
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie

::: fastapi.responses.StreamingResponse
    options:
        members:
            - body_iterator
            - charset
            - status_code
            - media_type
            - body
            - background
            - raw_headers
            - render
            - init_headers
            - headers
            - set_cookie
            - delete_cookie
