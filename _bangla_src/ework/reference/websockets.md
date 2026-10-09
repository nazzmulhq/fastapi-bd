# WebSockets { #websockets }

/// note | এই পেজে যা পাবেন

`WebSocket` অবজেক্টের সব মেথড (সংযোগ গ্রহণ, বার্তা পাঠানো/গ্রহণ, বন্ধ করা), আর `WebSocketDisconnect` ও `WebSocketState` ক্লাস।

///

WebSocket সংজ্ঞায়িত করার সময়, আপনি সাধারণত `WebSocket` টাইপের একটি প্যারামিটার ঘোষণা করেন, আর এটি দিয়ে ক্লায়েন্ট থেকে ডেটা পড়তে আর তাকে ডেটা পাঠাতে পারেন।

এ সম্পর্কে আরও পড়ুন [WebSocket নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/websockets/)

এটি সরাসরি Starlette দেয়, কিন্তু আপনি এটি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import WebSocket
```

/// tip | পরামর্শ

যখন এমন ডিপেন্ডেন্সি তৈরি করতে চান যা HTTP আর WebSocket দুটোর সাথেই মানানসই হবে, তখন `Request` বা `WebSocket`-এর বদলে `HTTPConnection` নেয় এমন একটি প্যারামিটার সংজ্ঞায়িত করতে পারেন।

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            await websocket.send_text(f"আপনি লিখেছেন: {text}")
    except WebSocketDisconnect:
        print("ক্লায়েন্ট চলে গেছে")
```

* `accept()`: সংযোগ গ্রহণ।
* `receive_text()` / `send_text()`: টেক্সট বার্তা গ্রহণ ও পাঠানো (JSON-এর জন্য `receive_json()` / `send_json()`)।
* `WebSocketDisconnect`: ক্লায়েন্ট সংযোগ বিচ্ছিন্ন করলে এই এক্সেপশন আসে।

///

::: fastapi.WebSocket
    options:
        members:
            - scope
            - app
            - url
            - base_url
            - headers
            - query_params
            - path_params
            - cookies
            - client
            - state
            - url_for
            - client_state
            - application_state
            - receive
            - send
            - accept
            - receive_text
            - receive_bytes
            - receive_json
            - iter_text
            - iter_bytes
            - iter_json
            - send_text
            - send_bytes
            - send_json
            - close

## WebSockets - অতিরিক্ত ক্লাস { #websockets-additional-classes }

WebSocket সামলানোর জন্য অতিরিক্ত ক্লাস।

সরাসরি Starlette দেয়, কিন্তু আপনি এগুলো `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.websockets import WebSocketDisconnect, WebSocketState
```

::: fastapi.websockets.WebSocketDisconnect

যখন একজন ক্লায়েন্ট সংযোগ বিচ্ছিন্ন করে, তখন একটি `WebSocketDisconnect` এক্সেপশন raise হয়, আপনি এটি ধরতে (catch করতে) পারেন।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import WebSocketDisconnect
```

এ সম্পর্কে আরও পড়ুন [WebSocket নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients)

::: fastapi.websockets.WebSocketState

`WebSocketState` হলো একটি WebSocket সংযোগের সম্ভাব্য অবস্থাগুলোর একটি enumeration (নির্দিষ্ট মানের তালিকা), যেমন সংযোগ হচ্ছে, সংযুক্ত, বিচ্ছিন্ন।
