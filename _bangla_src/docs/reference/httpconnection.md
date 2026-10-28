# `HTTPConnection` ক্লাস { #httpconnection-class }

/// note | এই পেজে যা পাবেন

`HTTPConnection` ক্লাসের বিস্তারিত। এটি `Request` আর `WebSocket` দুটোরই "অভিভাবক" ক্লাস, তাই দুটোর সাধারণ অংশগুলো (URL, হেডার, কুকি, ক্লায়েন্ট ইত্যাদি) এতে থাকে।

///

যখন এমন ডিপেন্ডেন্সি তৈরি করতে চান যা HTTP আর WebSocket দুটোর সাথেই মানানসই হবে, তখন `Request` বা `WebSocket`-এর বদলে `HTTPConnection` নেয় এমন একটি প্যারামিটার সংজ্ঞায়িত করতে পারেন।

আপনি এটি `fastapi.requests` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.requests import HTTPConnection
```

## কী কী পাওয়া যায় { #bn-attributes }

`HTTPConnection`-এ সেই অংশগুলোই আছে যা HTTP রিকোয়েস্ট আর WebSocket দুটোতেই থাকে:

| অ্যাট্রিবিউট/মেথড | কী রাখে |
| --- | --- |
| `url`, `base_url` | URL তথ্য |
| `headers` | হেডার |
| `query_params` | কোয়েরি প্যারামিটার |
| `path_params` | পাথ প্যারামিটার |
| `cookies` | কুকি |
| `client` | ক্লায়েন্টের `host` আর `port` |
| `state` | নিজের ডেটা রাখার জায়গা |
| `app` | অ্যাপ অবজেক্ট |
| `url_for()` | রাউটের নাম থেকে URL |

যা **নেই**: `body()`, `json()`, `form()` (শুধু `Request`-এ), আর `accept()`, `send_text()` (শুধু `WebSocket`-এ)।

/// tip | উদাহরণ দিয়ে বুঝি

`HTTPConnection` হলো "যেকোনো আগন্তুক"। দরজায় যে-ই আসুক, চিঠি নিয়ে (HTTP) বা ফোনে (WebSocket), তার পরিচয়পত্র (হেডার, টোকেন, IP) দেখা যায়। পরিচয় যাচাইয়ের একটি ডিপেন্ডেন্সি তাই দুই ধরনের আগন্তুকের জন্যই কাজ করে।

///

## উদাহরণ { #bn-example }

```python
from fastapi import Depends, FastAPI, HTTPException, WebSocket
from fastapi.requests import HTTPConnection

app = FastAPI()


def get_token(conn: HTTPConnection):
    token = conn.headers.get("authorization") or conn.query_params.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="টোকেন দিন")
    return token


@app.get("/items/")
def read_items(token=Depends(get_token)):
    return {"token": token}


@app.websocket("/ws")
async def ws(websocket: WebSocket, token=Depends(get_token)):
    await websocket.accept()
    await websocket.send_json({"token": token})
```

একই `get_token` ডিপেন্ডেন্সি সাধারণ HTTP রাউট আর WebSocket রাউট দুটোতেই কাজ করছে।

/// check | সংক্ষেপে মনে রাখুন

* HTTP আর WebSocket দুটোতেই চলবে এমন ডিপেন্ডেন্সিতে `conn: HTTPConnection` ব্যবহার করুন।
* হেডার, কোয়েরি, কুকি, ক্লায়েন্ট পড়া যায়; বডি পড়া বা বার্তা পাঠানো যায় না।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.requests.HTTPConnection
