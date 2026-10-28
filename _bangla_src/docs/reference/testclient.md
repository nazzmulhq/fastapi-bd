# Test Client - `TestClient` { #test-client-testclient }

/// note | এই পেজে যা পাবেন

* `TestClient` দিয়ে সার্ভার না চালিয়েই অ্যাপ টেস্ট করা।
* constructor-এর প্যারামিটার (`base_url`, `raise_server_exceptions`, `headers`, `cookies`, `follow_redirects` ইত্যাদি)।
* রিকোয়েস্ট মেথড (`get`, `post`, `put`, `patch`, `delete`...) আর তাদের সাধারণ আর্গুমেন্ট (`params`, `json`, `data`, `files`, `headers`, `cookies`)।
* lifespan চালাতে `with` ব্লক, WebSocket টেস্ট, ডিপেন্ডেন্সি বদলে টেস্ট।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

আসল HTTP আর সকেট সংযোগ তৈরি না করে, শুধু সরাসরি FastAPI কোডের সাথে যোগাযোগ করে FastAPI অ্যাপ্লিকেশন টেস্ট করতে `TestClient` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [টেস্টিং নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/testing/)।

আপনি এটি সরাসরি `fastapi.testclient` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.testclient import TestClient
```

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

`TestClient` হলো একজন নকল গ্রাহক যে দোকানের ভেতরেই থাকে। দরজা খুলে রাস্তায় যেতে হয় না (নেটওয়ার্ক নেই), তাই কেনাকাটা (রিকোয়েস্ট) খুব দ্রুত হয়, আর আপনি দেখে নিতে পারেন দোকানদার ঠিক জিনিস দিচ্ছে কিনা।

///

`pip install httpx` করে নিন (`TestClient` এর ওপর ভিত্তি করে তৈরি), আর টেস্ট চালাতে `pytest`।

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
def home():
    return {"msg": "Hello"}


client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello"}
```

## constructor প্যারামিটার { #bn-constructor }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `app` | (বাধ্যতামূলক) | যে অ্যাপ টেস্ট করবেন |
| `base_url` | `"http://testserver"` | রিকোয়েস্টের মূল ঠিকানা |
| `raise_server_exceptions` | `True` | অ্যাপের ভেতরে এক্সেপশন হলে টেস্টেই সেটি raise হয়; `False` দিলে বদলে `500` রেসপন্স পাবেন |
| `root_path` | `""` | প্রক্সির পেছনে চলার মতো root path |
| `backend` | `"asyncio"` | async ব্যাকএন্ড: `"asyncio"` বা `"trio"` |
| `headers` | `None` | প্রতিটি রিকোয়েস্টে যাবে এমন হেডার |
| `cookies` | `None` | প্রতিটি রিকোয়েস্টে যাবে এমন কুকি |
| `follow_redirects` | `True` | রিডাইরেক্ট এলে নিজে থেকে অনুসরণ করবে কিনা |
| `client` | `("testclient", 50000)` | `request.client`-এ দেখানো host আর port |

## রিকোয়েস্ট মেথড আর আর্গুমেন্ট { #bn-requests }

`client.get()`, `client.post()`, `client.put()`, `client.patch()`, `client.delete()`, `client.head()`, `client.options()`, আর সাধারণ `client.request(method, url)`। গুরুত্বপূর্ণ আর্গুমেন্ট:

| আর্গুমেন্ট | কী পাঠায় |
| --- | --- |
| `params` | কোয়েরি প্যারামিটার, যেমন `{"q": "বই"}` |
| `json` | JSON বডি |
| `data` | ফর্ম ডেটা |
| `files` | আপলোড ফাইল, যেমন `{"file": ("a.txt", b"hello", "text/plain")}` |
| `headers`, `cookies` | এই রিকোয়েস্টের হেডার/কুকি |

রেসপন্স অবজেক্টে: `status_code`, `json()`, `text`, `content`, `headers`, `cookies`।

নিচের উদাহরণগুলোতে ধরে নিচ্ছি অ্যাপে `/items/` আর `/upload/` রাউট আছে (যেমন [`UploadFile`](uploadfile.md) পেজের উদাহরণ)।

```python
def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "কলম", "price": 10},
        headers={"X-Token": "secret"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "কলম"


def test_upload():
    response = client.post("/upload/", files={"file": ("hello.txt", b"hello", "text/plain")})
    assert response.json()["filename"] == "hello.txt"
```

## `with` ব্লক: lifespan চালানো { #bn-lifespan }

অ্যাপের `lifespan` (শুরু/বন্ধের কোড, যেমন ডেটাবেস সংযোগ) চালাতে client-কে `with` ব্লকে ব্যবহার করুন:

```python
def test_with_startup():
    with TestClient(app) as client:  # এখানে lifespan-এর শুরুর অংশ চলে
        response = client.get("/")
        assert response.status_code == 200
    # ব্লক শেষে বন্ধের অংশ চলে
```

## WebSocket টেস্ট { #bn-websocket }

ধরে নিচ্ছি অ্যাপে [WebSockets](websockets.md) পেজের echo রাউটটি আছে:

```python
def test_ws():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("হ্যালো")
        assert websocket.receive_text() == "আপনি লিখেছেন: হ্যালো"
```

## ডিপেন্ডেন্সি বদলে টেস্ট { #bn-overrides }

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


def get_current_user():
    raise RuntimeError("আসল লগইন সার্ভার লাগবে")


@app.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"user": user}


def test_me():
    app.dependency_overrides[get_current_user] = lambda: "test-user"
    client = TestClient(app)
    assert client.get("/me").json() == {"user": "test-user"}
    app.dependency_overrides.clear()
```

বিস্তারিত: [ডিপেন্ডেন্সি ওভাররাইড দিয়ে টেস্টিং](../advanced/testing-dependencies.md)।

/// check | সংক্ষেপে মনে রাখুন

* `client = TestClient(app)`, তারপর `client.get(...)`, `client.post(..., json=...)`।
* lifespan চালাতে `with TestClient(app) as client:`।
* WebSocket: `client.websocket_connect("/ws")`; ডিপেন্ডেন্সি বদলাতে `app.dependency_overrides`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.testclient.TestClient
