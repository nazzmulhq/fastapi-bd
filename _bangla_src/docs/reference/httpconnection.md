# `HTTPConnection` ক্লাস { #httpconnection-class }

/// note | এই পেজে যা পাবেন

`HTTPConnection` ক্লাসের বিস্তারিত। এটি `Request` আর `WebSocket` দুটোরই "অভিভাবক" ক্লাস, তাই দুটোর সাধারণ অংশগুলো (URL, হেডার, কুকি, ক্লায়েন্ট ইত্যাদি) এতে থাকে।

///

যখন এমন ডিপেন্ডেন্সি তৈরি করতে চান যা HTTP আর WebSocket দুটোর সাথেই মানানসই হবে, তখন `Request` বা `WebSocket`-এর বদলে `HTTPConnection` নেয় এমন একটি প্যারামিটার সংজ্ঞায়িত করতে পারেন।

আপনি এটি `fastapi.requests` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.requests import HTTPConnection
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import Depends, FastAPI, WebSocket
from fastapi.requests import HTTPConnection

app = FastAPI()


def get_token(conn: HTTPConnection):
    return conn.headers.get("authorization")


@app.get("/items/")
def read_items(token=Depends(get_token)):
    return {"token": token}


@app.websocket("/ws")
async def ws(websocket: WebSocket, token=Depends(get_token)):
    await websocket.accept()
    await websocket.send_json({"token": token})
```

একই `get_token` ডিপেন্ডেন্সি সাধারণ HTTP রাউট আর WebSocket রাউট দুটোতেই কাজ করছে।

///

::: fastapi.requests.HTTPConnection
