# কাস্টম রেসপন্স ক্লাস - File, HTML, Redirect, Streaming, ইত্যাদি { #custom-response-classes-file-html-redirect-streaming-etc }

/// note | এই পেজে যা পাবেন

বিভিন্ন ধরনের রেসপন্স ক্লাসের বিস্তারিত: JSON, HTML, সাধারণ টেক্সট, ফাইল, রিডাইরেক্ট, স্ট্রিমিং। কোনটি কখন ব্যবহার করবেন, তার সহজ সারণিও নিচে আছে।

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

/// info | কোনটি কখন ব্যবহার করবেন

| ক্লাস | কী ফেরত দেয় | কখন |
| --- | --- | --- |
| `JSONResponse` | JSON | ডিফল্ট, সাধারণত নিজে লিখতে হয় না |
| `HTMLResponse` | HTML পেজ | ব্রাউজারে একটি পেজ দেখাতে |
| `PlainTextResponse` | সাধারণ টেক্সট | শুধু লেখা ফেরত দিতে |
| `FileResponse` | একটি ফাইল | ডাউনলোড বা ছবি দেখাতে |
| `RedirectResponse` | অন্য URL-এ পাঠানো | লগইনের পরে অন্য পেজে নিতে |
| `StreamingResponse` | ধাপে ধাপে ডেটা | বড় ফাইল বা লাইভ ডেটা পাঠাতে |
| `Response` | যা খুশি | সব নিয়ন্ত্রণ নিজে রাখতে |

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1>স্বাগতম</h1>"


@app.get("/download")
def download():
    return FileResponse("report.pdf")


@app.get("/old-page")
def old_page():
    return RedirectResponse("/")
```

///

## FastAPI রেসপন্স { #fastapi-responses }

JSON পারফরম্যান্স বাড়ানোর উদ্দেশ্যে কয়েকটি কাস্টম FastAPI রেসপন্স ক্লাস ছিল।

তবে এগুলো এখন পুরনো (deprecated), কারণ এখন [রেসপন্স মডেল - রিটার্ন টাইপ](https://fastapi.tiangolo.com/tutorial/response-model/) ব্যবহার করলেই আপনি আরও ভালো পারফরম্যান্স পাবেন।

এভাবে Pydantic Rust-এর দিকে ডেটাকে JSON bytes-এ সিরিয়ালাইজ করবে, যা এই কাস্টম JSON রেসপন্সগুলোর চেয়ে ভালো পারফরম্যান্স দেবে।

এ সম্পর্কে আরও পড়ুন [কাস্টম রেসপন্স - HTML, Stream, File, অন্যান্য - `orjson` নাকি রেসপন্স মডেল](https://fastapi.tiangolo.com/advanced/custom-response/#orjson-or-response-model)-এ।

⟦CODE1⟧

⟦CODE2⟧

## Starlette রেসপন্স { #starlette-responses }

এগুলোর সবকটি সম্পর্কে আরও পড়তে পারেন [কাস্টম রেসপন্স নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/custom-response/) আর [Responses নিয়ে Starlette ডকসে](https://starlette.dev/responses/)।

⟦CODE3⟧

⟦CODE4⟧

⟦CODE5⟧

⟦CODE6⟧

⟦CODE7⟧

⟦CODE8⟧

⟦CODE9⟧
