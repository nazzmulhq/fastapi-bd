# Server-Sent Events - `EventSourceResponse` এবং `ServerSentEvent` { #server-sent-events-eventsourceresponse-and-serversentevent }

/// note | এই পেজে যা পাবেন

Server-Sent Events (SSE) পাঠানোর দুটি ক্লাসের বিস্তারিত। SSE দিয়ে সার্ভার একটি খোলা সংযোগে ক্লায়েন্টকে একের পর এক ঘটনা (যেমন লাইভ নোটিফিকেশন, AI-এর উত্তর অক্ষরে অক্ষরে) পাঠাতে পারে।

///

Server-Sent Events (SSE) স্ট্রিম করতে, আপনার *পাথ অপারেশন ফাংশনে* `yield` ব্যবহার করুন আর `response_class=EventSourceResponse` সেট করুন।

যদি `event`, `id`, `retry` বা `comment` এর মতো SSE ফিল্ড সেট করতে হয়, তাহলে সাধারণ ডেটার বদলে `ServerSentEvent` অবজেক্ট `yield` করতে পারেন।

এ সম্পর্কে আরও পড়ুন [Server-Sent Events (SSE) নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/server-sent-events/)।

আপনি এগুলো সরাসরি `fastapi.sse` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.sse import EventSourceResponse, ServerSentEvent
```

/// tip | উদাহরণ দিয়ে বুঝি

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

ব্রাউজার প্রতি সেকেন্ডে একটি করে বার্তা পাবে: ৫, ৪, ৩, ২, ১। ঠিক রেডিওর মতো, সার্ভার সম্প্রচার করে আর ক্লায়েন্ট শুনতে থাকে। (WebSocket-এর মতো দুইমুখী নয়, শুধু সার্ভার থেকে ক্লায়েন্টে।)

///

::: fastapi.sse.EventSourceResponse

::: fastapi.sse.ServerSentEvent
