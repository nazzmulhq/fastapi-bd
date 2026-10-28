# স্ট্যাটাস কোড { #status-codes }

/// note | এই পেজে যা পাবেন

* HTTP স্ট্যাটাস কোড কী, আর এর পাঁচটি দল।
* সবচেয়ে বেশি ব্যবহৃত কোডগুলোর নামযুক্ত রূপ আর কখন কোনটি ব্যবহার করবেন।
* `status_code=`, `HTTPException` আর WebSocket-এ কীভাবে ব্যবহার করবেন, উদাহরণসহ।
* সবশেষে সব কোডের পূর্ণ তালিকা।

///

আপনি `fastapi` থেকে `status` মডিউল ইম্পোর্ট করতে পারেন:

```python
from fastapi import status
```

`status` সরাসরি Starlette দেয়।

এতে পূর্ণসংখ্যার স্ট্যাটাস কোডসহ একদল নামযুক্ত কনস্ট্যান্ট (ভেরিয়েবল) আছে।

যেমন:

* 200: `status.HTTP_200_OK`
* 403: `status.HTTP_403_FORBIDDEN`
* ইত্যাদি।

পূর্ণসংখ্যার স্ট্যাটাস কোড মুখস্থ না করে নামের অটোকমপ্লিশন ব্যবহার করে আপনার অ্যাপে দ্রুত HTTP (ও WebSocket) স্ট্যাটাস কোড অ্যাক্সেস করতে এটি সুবিধাজনক হতে পারে।

এ সম্পর্কে আরও পড়ুন [রেসপন্স স্ট্যাটাস কোড নিয়ে FastAPI ডকুমেন্টেশনে](https://fastapi.tiangolo.com/tutorial/response-status-code/)।

## স্ট্যাটাস কোড কী { #bn-what-is }

প্রতিটি HTTP রেসপন্সের সাথে একটি তিন অঙ্কের সংখ্যা যায়, যা ক্লায়েন্টকে এক কথায় বলে দেয় কী হলো। প্রথম অঙ্ক দেখে দল বোঝা যায়:

| দল | অর্থ |
| --- | --- |
| `1xx` | তথ্য: রিকোয়েস্ট পেয়েছি, কাজ চলছে (খুব কম ব্যবহার হয়) |
| `2xx` | সফল |
| `3xx` | অন্য জায়গায় যান (redirect) |
| `4xx` | ক্লায়েন্টের ভুল (ভুল ডেটা, লগইন নেই, পাওয়া যায়নি) |
| `5xx` | সার্ভারের ভুল (কোডে বাগ, সার্ভার বন্ধ) |

/// tip | উদাহরণ দিয়ে বুঝি

দোকানে কিছু চাইলে দোকানদারের উত্তরের মতো: "এই নিন" (`200`), "নতুন বানিয়ে দিলাম" (`201`), "পাশের দোকানে যান" (`307`), "আপনার কুপনটা ভুল" (`400`), "আগে সদস্য হোন" (`401`), "এটা আপনার জন্য নয়" (`403`), "এমন জিনিস নেই" (`404`), "আমাদের মেশিন নষ্ট" (`500`)।

///

## বেশি ব্যবহৃত কোড { #bn-common-codes }

| কোড | নামযুক্ত রূপ | কখন ব্যবহার করবেন |
| --- | --- | --- |
| 200 | `status.HTTP_200_OK` | সাধারণ সফল রেসপন্স (GET-এর ডিফল্ট) |
| 201 | `status.HTTP_201_CREATED` | নতুন কিছু তৈরি হয়েছে (POST) |
| 202 | `status.HTTP_202_ACCEPTED` | গ্রহণ করেছি, পরে প্রসেস হবে |
| 204 | `status.HTTP_204_NO_CONTENT` | সফল, কিন্তু ফেরত দেওয়ার কিছু নেই (DELETE) |
| 301 / 307 | `status.HTTP_301_MOVED_PERMANENTLY` / `status.HTTP_307_TEMPORARY_REDIRECT` | স্থায়ী / অস্থায়ী রিডাইরেক্ট |
| 400 | `status.HTTP_400_BAD_REQUEST` | রিকোয়েস্ট ভুল বা অসম্পূর্ণ |
| 401 | `status.HTTP_401_UNAUTHORIZED` | লগইন নেই বা টোকেন ভুল |
| 403 | `status.HTTP_403_FORBIDDEN` | লগইন আছে, কিন্তু অনুমতি নেই |
| 404 | `status.HTTP_404_NOT_FOUND` | যা চাওয়া হয়েছে তা নেই |
| 409 | `status.HTTP_409_CONFLICT` | সংঘাত, যেমন ইমেইলটি আগেই নিবন্ধিত |
| 422 | `status.HTTP_422_UNPROCESSABLE_CONTENT` | ডেটা যাচাইয়ে ব্যর্থ (FastAPI নিজে থেকে দেয়) |
| 429 | `status.HTTP_429_TOO_MANY_REQUESTS` | খুব বেশি রিকোয়েস্ট, একটু পরে চেষ্টা করুন |
| 500 | `status.HTTP_500_INTERNAL_SERVER_ERROR` | সার্ভারের ভেতরের এরর |
| 503 | `status.HTTP_503_SERVICE_UNAVAILABLE` | সার্ভার এই মুহূর্তে ব্যস্ত বা রক্ষণাবেক্ষণে |

## উদাহরণ { #example }

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.get("/items/", status_code=status.HTTP_418_IM_A_TEAPOT)
def read_items():
    return [{"name": "Plumbus"}, {"name": "Portal Gun"}]
```

(`418 I'm a teapot` একটি মজার কোড, যা একটি পুরনো রসিকতা থেকে এসেছে। আসল অ্যাপে সাধারণত `200`, `201` এর মতো কোড ব্যবহার করবেন।)

### সফল রেসপন্সে, এরর রেসপন্সে আর WebSocket-এ { #bn-usage }

```python
from fastapi import FastAPI, HTTPException, WebSocket, status

app = FastAPI()
books = {1: "পথের পাঁচালী"}


@app.post("/books/", status_code=status.HTTP_201_CREATED)
def create_book(title: str):
    new_id = max(books) + 1
    books[new_id] = title
    return {"id": new_id, "title": title}


@app.get("/books/{book_id}")
def get_book(book_id: int):
    if book_id not in books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="বইটি নেই")
    return {"title": books[book_id]}


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    books.pop(book_id, None)


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
```

/// info | কোডটি সহজ ভাষায়

* `status_code=` দিয়ে সফল রেসপন্সের কোড ঠিক করা হয় (`201`, `204`)।
* এররের কোড দেওয়া হয় `HTTPException(status_code=...)` দিয়ে।
* WebSocket-এর জন্য আলাদা কোড আছে, যেগুলো `WS_` দিয়ে শুরু, যেমন `WS_1008_POLICY_VIOLATION`।

///

/// check | সংক্ষেপে মনে রাখুন

* `2xx` সফল, `4xx` ক্লায়েন্টের ভুল, `5xx` সার্ভারের ভুল।
* সংখ্যার বদলে `status.HTTP_404_NOT_FOUND` এর মতো নাম লিখুন; এডিটর অটোকমপ্লিট করে, ভুলের সম্ভাবনা কমে।
* তৈরি = `201`, মুছে ফেলা = `204`, পাওয়া যায়নি = `404`, অনুমতি নেই = `403`, লগইন নেই = `401`।

///

## পূর্ণ API তালিকা { #bn-full-api }

নিচে `status` মডিউলের সব কনস্ট্যান্টের পূর্ণ তালিকা।

::: fastapi.status
