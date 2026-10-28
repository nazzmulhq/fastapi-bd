# Exceptions - `HTTPException` এবং `WebSocketException` { #exceptions-httpexception-and-websocketexception }

/// note | এই পেজে যা পাবেন

* `HTTPException` আর `WebSocketException`-এর প্রতিটি প্যারামিটারের অর্থ, উদাহরণসহ।
* এরর হলে ক্লায়েন্ট আসলে কী পায় (JSON-এর চেহারা)।
* নিজের এক্সেপশন বানিয়ে সুন্দর এরর ফেরত দেওয়া।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

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

## `HTTPException` { #bn-httpexception }

| প্যারামিটার | কী করে |
| --- | --- |
| `status_code` | HTTP স্ট্যাটাস কোড, যেমন `404` বা `status.HTTP_404_NOT_FOUND` (বাধ্যতামূলক) |
| `detail` | ক্লায়েন্টকে পাঠানো বার্তা; স্ট্রিং, ডিকশনারি বা তালিকা, যা JSON-এ রূপান্তর করা যায় |
| `headers` | রেসপন্সে যোগ করার বাড়তি হেডার, যেমন `{"WWW-Authenticate": "Bearer"}` |

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()
items = {"foo": "The Foo Wrestlers"}


@app.get("/items/{item_id}")
def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "আইটেম পাওয়া যায়নি", "item_id": item_id},
            headers={"X-Error": "not-found"},
        )
    return {"item": items[item_id]}
```

`/items/bar` চাইলে ক্লায়েন্ট পাবে স্ট্যাটাস `404`, হেডার `X-Error: not-found`, আর বডি:

```json
{"detail": {"error": "আইটেম পাওয়া যায়নি", "item_id": "bar"}}
```

/// tip | উদাহরণ দিয়ে বুঝি

`raise HTTPException(...)` হলো রেস্টুরেন্টের ওয়েটারের "দুঃখিত, এটা আজ নেই" বলা। রান্না (ফাংশনের বাকি কোড) আর শুরুই হয় না, ওয়েটার সরাসরি গ্রাহককে কারণ জানিয়ে দেয়। `return` না করে `raise` করা হয়, তাই এটি ডিপেন্ডেন্সি বা সাহায্যকারী ফাংশনের ভেতর থেকেও কাজ করে।

///

### লগইনের এররে হেডার { #bn-auth-header }

```python
raise HTTPException(
    status_code=401,
    detail="লগইন তথ্য সঠিক নয়",
    headers={"WWW-Authenticate": "Bearer"},  # নিয়ম অনুযায়ী 401-এর সাথে দেওয়া উচিত
)
```

## `WebSocketException` { #bn-websocketexception }

WebSocket সংযোগ একটি নির্দিষ্ট কারণসহ বন্ধ করতে ব্যবহার হয়।

| প্যারামিটার | কী করে |
| --- | --- |
| `code` | WebSocket বন্ধের কোড, যেমন `status.WS_1008_POLICY_VIOLATION` |
| `reason` | বন্ধের কারণ লেখা (ঐচ্ছিক) |

```python
from typing import Annotated

from fastapi import FastAPI, Query, WebSocket, WebSocketException, status

app = FastAPI()


@app.websocket("/ws")
async def ws(websocket: WebSocket, token: Annotated[str | None, Query()] = None):
    if token != "secret":
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="ভুল টোকেন")
    await websocket.accept()
    await websocket.send_text("স্বাগতম")
```

## নিজের এক্সেপশন আর হ্যান্ডলার { #bn-custom }

বারবার একই ধরনের এরর হলে নিজের এক্সেপশন ক্লাস বানিয়ে একটি হ্যান্ডলার যোগ করুন:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotEnoughBalance(Exception):
    def __init__(self, needed: float):
        self.needed = needed


app = FastAPI()


@app.exception_handler(NotEnoughBalance)
async def balance_handler(request: Request, exc: NotEnoughBalance):
    return JSONResponse(status_code=402, content={"message": f"আরও {exc.needed} টাকা লাগবে"})


@app.post("/pay")
def pay(amount: float):
    raise NotEnoughBalance(needed=amount)
```

বিস্তারিত: [এরর সামলানো](../tutorial/handling-errors.md)।

/// check | সংক্ষেপে মনে রাখুন

* `raise HTTPException(status_code=..., detail=..., headers=...)`; ক্লায়েন্ট পায় `{"detail": ...}`।
* WebSocket-এ `raise WebSocketException(code=..., reason=...)`।
* নিজের এক্সেপশন + `@app.exception_handler(...)` দিয়ে এররের চেহারা পুরোপুরি নিজের মতো করা যায়।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.HTTPException

::: fastapi.WebSocketException
