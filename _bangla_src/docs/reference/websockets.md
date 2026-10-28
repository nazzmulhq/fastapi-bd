# WebSockets { #websockets }

/// note | এই পেজে যা পাবেন

* WebSocket কী, আর সাধারণ HTTP থেকে কীভাবে আলাদা।
* `WebSocket` অবজেক্টের প্রতিটি মেথড (সংযোগ গ্রহণ, বার্তা গ্রহণ/পাঠানো, বন্ধ করা) সারণি আর উদাহরণসহ।
* `WebSocketDisconnect` আর `WebSocketState` ক্লাস।
* একাধিক ক্লায়েন্টকে একসাথে বার্তা পাঠানোর (চ্যাট রুম) উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

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

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ HTTP হলো চিঠি: একটি প্রশ্ন পাঠালেন, একটি উত্তর এল, ব্যস। WebSocket হলো ফোন কল: একবার সংযোগ হলে দুই দিক থেকেই যখন খুশি কথা বলা যায়, যতক্ষণ না কেউ ফোন রাখে। চ্যাট, লাইভ খেলার স্কোর, একসাথে ডকুমেন্ট সম্পাদনার মতো কাজে এটি দরকার।

///

একটি WebSocket সংযোগের জীবনচক্র:

1. ক্লায়েন্ট সংযোগের অনুরোধ পাঠায় (অবস্থা `CONNECTING`)।
2. আপনি `await websocket.accept()` দিয়ে গ্রহণ করেন (অবস্থা `CONNECTED`)।
3. দুই দিক থেকে বার্তা আদান-প্রদান চলে।
4. কেউ একজন সংযোগ বন্ধ করে (অবস্থা `DISCONNECTED`); ক্লায়েন্ট বন্ধ করলে আপনার কোডে `WebSocketDisconnect` এক্সেপশন আসে।

## মেথড { #bn-methods }

### সংযোগ গ্রহণ আর বন্ধ { #bn-accept-close }

| মেথড | কী করে |
| --- | --- |
| `await websocket.accept(subprotocol=None, headers=None)` | সংযোগ গ্রহণ করে; বার্তা পাঠানো/গ্রহণের আগে অবশ্যই ডাকতে হয় |
| `await websocket.close(code=1000, reason=None)` | সংযোগ বন্ধ করে; `code` হলো বন্ধের কারণের কোড |

### বার্তা গ্রহণ { #bn-receive }

| মেথড | কী ফেরত দেয় |
| --- | --- |
| `await websocket.receive_text()` | একটি টেক্সট বার্তা (`str`) |
| `await websocket.receive_bytes()` | একটি বাইনারি বার্তা (`bytes`) |
| `await websocket.receive_json(mode="text")` | JSON পার্স করা ডেটা (`dict`, `list` ...) |
| `websocket.iter_text()` / `iter_bytes()` / `iter_json()` | `async for` লুপে একের পর এক বার্তা; সংযোগ বন্ধ হলে লুপ নিজে থেকে শেষ হয় |

### বার্তা পাঠানো { #bn-send }

| মেথড | কী পাঠায় |
| --- | --- |
| `await websocket.send_text(data)` | টেক্সট |
| `await websocket.send_bytes(data)` | bytes |
| `await websocket.send_json(data, mode="text")` | যেকোনো JSON-যোগ্য ডেটা |

### অ্যাট্রিবিউট { #bn-attributes }

`Request`-এর মতোই এখানেও `url`, `headers`, `query_params`, `path_params`, `cookies`, `client`, `state`, `app` আছে। সাথে আছে `client_state` আর `application_state`: দুই দিকের সংযোগের বর্তমান অবস্থা (`WebSocketState`)।

## উদাহরণ { #bn-examples }

### সাধারণ echo সার্ভার { #bn-echo }

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

/// info | কোডটি সহজ ভাষায়

* `accept()`: ফোন তোলা।
* `while True` লুপ: যতক্ষণ সংযোগ আছে, প্রতিটি বার্তা পড়ে উত্তর পাঠানো।
* `WebSocketDisconnect`: ক্লায়েন্ট ফোন রেখে দিলে লুপ থেকে বের হওয়ার সংকেত।

///

### JSON বার্তা আর `iter_json()` { #bn-json }

```python
@app.websocket("/ws/calc")
async def calc(websocket: WebSocket):
    await websocket.accept()
    async for msg in websocket.iter_json():  # যেমন {"a": 2, "b": 3}
        await websocket.send_json({"sum": msg["a"] + msg["b"]})
```

### একাধিক ক্লায়েন্ট: ছোট চ্যাট রুম { #bn-chat-room }

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{username}")
async def room(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    await manager.broadcast(f"{username} যোগ দিয়েছেন")
    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast(f"{username}: {text}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} চলে গেছেন")
```

/// warning | সাধারণ ভুল

* `accept()` না করে `send_text()` বা `receive_text()` ডাকলে এরর হয়।
* ওপরের `ConnectionManager` শুধু একটি প্রসেসের মেমোরিতে তালিকা রাখে। একাধিক সার্ভার বা worker চালালে সবার কাছে বার্তা পৌঁছাতে Redis-এর মতো আলাদা ব্যবস্থা লাগে।

///

/// check | সংক্ষেপে মনে রাখুন

* `@app.websocket("/path")` আর প্যারামিটারে `websocket: WebSocket`।
* আগে `await websocket.accept()`, তারপর `receive_*` / `send_*`।
* ক্লায়েন্ট চলে গেলে `WebSocketDisconnect` ধরুন; নিজে বন্ধ করতে `await websocket.close()`।

///

## পূর্ণ API তালিকা { #bn-full-api }

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

এক্সেপশনটির দুটি অ্যাট্রিবিউট কাজে লাগে: `code` (বন্ধের কোড, যেমন `1000` = স্বাভাবিকভাবে বন্ধ, `1001` = পেজ ছেড়ে চলে গেছে) আর `reason` (কারণের লেখা, থাকলে)।

```python
try:
    await websocket.receive_text()
except WebSocketDisconnect as exc:
    print("বন্ধের কোড:", exc.code, "কারণ:", exc.reason)
```

::: fastapi.websockets.WebSocketState

`WebSocketState` হলো একটি WebSocket সংযোগের সম্ভাব্য অবস্থাগুলোর একটি enumeration (নির্দিষ্ট মানের তালিকা):

| মান | অর্থ |
| --- | --- |
| `CONNECTING` | সংযোগ হচ্ছে, এখনো গ্রহণ করা হয়নি |
| `CONNECTED` | সংযুক্ত, বার্তা আদান-প্রদান চলতে পারে |
| `DISCONNECTED` | বিচ্ছিন্ন |
| `RESPONSE` | সংযোগ গ্রহণ না করে একটি সাধারণ HTTP রেসপন্স পাঠানো হয়েছে |

```python
from fastapi.websockets import WebSocketState

if websocket.client_state == WebSocketState.CONNECTED:
    await websocket.send_text("এখনো সংযুক্ত আছেন")
```
