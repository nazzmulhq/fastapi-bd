# Server-Sent Events - `EventSourceResponse` এবং `ServerSentEvent` { #server-sent-events-eventsourceresponse-and-serversentevent }

/// note | এই পেজে যা পাবেন

* Server-Sent Events (SSE) কী, আর WebSocket থেকে কীভাবে আলাদা।
* `EventSourceResponse` কীভাবে কাজ করে, আর FastAPI নিজে থেকে কী কী করে দেয়।
* `ServerSentEvent`-এর প্রতিটি ফিল্ড (`data`, `raw_data`, `event`, `id`, `retry`, `comment`) উদাহরণসহ।
* সংযোগ ছিন্ন হলে `Last-Event-ID` দিয়ে আবার শুরু করা, আর ব্রাউজারে শোনার JavaScript।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

Server-Sent Events (SSE) স্ট্রিম করতে, আপনার *পাথ অপারেশন ফাংশনে* `yield` ব্যবহার করুন আর `response_class=EventSourceResponse` সেট করুন।

যদি `event`, `id`, `retry` বা `comment` এর মতো SSE ফিল্ড সেট করতে হয়, তাহলে সাধারণ ডেটার বদলে `ServerSentEvent` অবজেক্ট `yield` করতে পারেন।

এ সম্পর্কে আরও পড়ুন [Server-Sent Events (SSE) নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/server-sent-events/)।

আপনি এগুলো সরাসরি `fastapi.sse` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.sse import EventSourceResponse, ServerSentEvent
```

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

SSE হলো রেডিও: সার্ভার সম্প্রচার করে আর ক্লায়েন্ট শুনতে থাকে। WebSocket হলো ফোন কল, দুই দিক থেকেই কথা বলা যায়। লাইভ নোটিফিকেশন, প্রগ্রেস বার, বা AI-এর উত্তর অক্ষরে অক্ষরে দেখানোর মতো কাজে শুধু সার্ভার থেকে ক্লায়েন্টে পাঠালেই চলে, তাই SSE সহজ পছন্দ।

///

| | SSE | WebSocket |
| --- | --- | --- |
| দিক | শুধু সার্ভার → ক্লায়েন্ট | দুই দিকেই |
| প্রোটোকল | সাধারণ HTTP | আলাদা WebSocket প্রোটোকল |
| সংযোগ ছিন্ন হলে | ব্রাউজার নিজে থেকে আবার সংযোগ করে | নিজে কোড লিখতে হয় |
| ব্রাউজারে | `EventSource` | `WebSocket` |

## `EventSourceResponse` { #bn-eventsourceresponse }

`response_class=EventSourceResponse` দিয়ে যে ফাংশনে `yield` আছে, তার প্রতিটি `yield` একটি করে ঘটনা (event) হিসেবে পাঠানো হয়। সাধারণ মান (ডিকশনারি, Pydantic মডেল, তালিকা) `yield` করলে সেটি JSON হয়ে `data` ফিল্ডে যায়।

```python
import asyncio

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse

app = FastAPI()


@app.get("/countdown", response_class=EventSourceResponse)
async def countdown():
    for i in range(5, 0, -1):
        yield {"remaining": i}
        await asyncio.sleep(1)
```

ক্লায়েন্ট প্রতি সেকেন্ডে একটি করে এমন অংশ পায়:

```
data: {"remaining": 5}

data: {"remaining": 4}

```

FastAPI নিজে থেকেই যা করে দেয়:

* কোনো বার্তা না থাকলে প্রতি ১৫ সেকেন্ডে একটি "ping" মন্তব্য পাঠায়, যাতে মাঝের প্রক্সি সংযোগ বন্ধ না করে।
* `Cache-Control: no-cache` হেডার দেয়, যাতে স্ট্রিম ক্যাশ না হয়।
* `X-Accel-Buffering: no` হেডার দেয়, যাতে Nginx-এর মতো প্রক্সি জমিয়ে না রাখে।
* `GET` ছাড়া `POST` সহ যেকোনো HTTP মেথডে কাজ করে।

## `ServerSentEvent` ফিল্ড { #bn-serversentevent }

| ফিল্ড | কী করে |
| --- | --- |
| `data` | মূল ডেটা; সবসময় JSON-এ রূপান্তর হয়ে পাঠানো হয় (স্ট্রিং দিলেও উদ্ধৃতিচিহ্নসহ JSON স্ট্রিং হয়) |
| `raw_data` | হুবহু যেমন আছে তেমন পাঠানো লেখা, JSON রূপান্তর ছাড়া (`data`-এর বদলে, একসাথে নয়) |
| `event` | ঘটনার নাম; ব্রাউজারে `addEventListener("নাম", ...)` দিয়ে আলাদা করে ধরা যায়; এক লাইনের হতে হবে |
| `id` | ঘটনার আইডি; সংযোগ ছিন্ন হলে ব্রাউজার শেষ আইডি `Last-Event-ID` হেডারে ফেরত পাঠায় |
| `retry` | সংযোগ ছিন্ন হলে আবার চেষ্টার আগে কত মিলিসেকেন্ড অপেক্ষা (০ বা বেশি) |
| `comment` | মন্তব্য লাইন (`: ...`); ব্রাউজার উপেক্ষা করে, সংযোগ সজীব রাখতে কাজে লাগে |

```python
from collections.abc import AsyncIterable

from fastapi import FastAPI
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()


@app.get("/orders/stream", response_class=EventSourceResponse)
async def order_updates() -> AsyncIterable[ServerSentEvent]:
    yield ServerSentEvent(comment="স্ট্রিম শুরু")
    yield ServerSentEvent(data={"order": 7, "status": "cooking"}, event="status", id="1", retry=5000)
    yield ServerSentEvent(data={"order": 7, "status": "on-the-way"}, event="status", id="2")
    yield ServerSentEvent(raw_data="DONE", event="end", id="3")
```

ক্লায়েন্ট যা পায়:

```
: স্ট্রিম শুরু

event: status
data: {"order": 7, "status": "cooking"}
id: 1
retry: 5000

event: status
data: {"order": 7, "status": "on-the-way"}
id: 2

event: end
data: DONE
id: 3

```

/// info | বাংলা লেখা থাকলে

`data`-তে ডিকশনারি দিলে তা Python-এর `json.dumps` দিয়ে JSON হয়, তাই বাংলা অক্ষর তারের ওপর `\u0986`-এর মতো escape করা অবস্থায় যায়। চিন্তার কিছু নেই: ব্রাউজারে `JSON.parse(e.data)` করলে আবার ঠিক বাংলা লেখাই পাবেন। ওপরের উদাহরণে আউটপুট সহজে পড়ার জন্য ইংরেজি মান রাখা হয়েছে।

///

### ব্রাউজারে শোনা { #bn-browser }

```javascript
const source = new EventSource("/orders/stream");
source.addEventListener("status", (e) => {
  const info = JSON.parse(e.data);
  console.log("অর্ডার", info.order, ":", info.status);
});
source.addEventListener("end", () => source.close());
```

## `Last-Event-ID` দিয়ে আবার শুরু { #bn-resume }

সংযোগ ছিন্ন হলে ব্রাউজার নিজে থেকে আবার সংযোগ করে, আর শেষ পাওয়া `id` `Last-Event-ID` হেডারে পাঠায়। হেডার প্যারামিটার হিসেবে পড়ে সেখান থেকে শুরু করুন:

```python
from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.sse import EventSourceResponse, ServerSentEvent

app = FastAPI()
news = ["খবর ১", "খবর ২", "খবর ৩"]


@app.get("/news/stream", response_class=EventSourceResponse)
async def news_stream(
    last_event_id: Annotated[int | None, Header()] = None,
) -> AsyncIterable[ServerSentEvent]:
    start = last_event_id + 1 if last_event_id is not None else 0
    for i in range(start, len(news)):
        yield ServerSentEvent(data={"headline": news[i]}, id=str(i))
```

/// warning | সাধারণ ভুল

* `data` আর `raw_data` একসাথে দেওয়া যায় না।
* `event` আর `id`-তে নতুন লাইন (`\n`) থাকলে এরর হয়।
* রিটার্ন টাইপ লিখলে (`AsyncIterable[Item]`) প্রতিটি আইটেম যাচাই হয় আর ডকসে স্কিমা দেখায়; না লিখলেও কাজ করে।

///

/// check | সংক্ষেপে মনে রাখুন

* `response_class=EventSourceResponse` + ফাংশনে `yield`।
* সাধারণ ডেটা `yield` করলে সেটি `data` হয়; বাড়তি ফিল্ডের জন্য `ServerSentEvent(data=..., event=..., id=..., retry=...)`।
* `id` দিলে ব্রাউজার `Last-Event-ID` পাঠায়, তা দিয়ে স্ট্রিম যেখানে থেমেছিল সেখান থেকে শুরু করা যায়।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.sse.EventSourceResponse

::: fastapi.sse.ServerSentEvent
