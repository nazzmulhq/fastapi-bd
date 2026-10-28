# Background Tasks - `BackgroundTasks` { #background-tasks-backgroundtasks }

/// note | এই পেজে যা পাবেন

* ব্যাকগ্রাউন্ড টাস্ক কী, আর কখন ব্যবহার করবেন।
* `add_task()` মেথডের আর্গুমেন্ট, উদাহরণসহ।
* ডিপেন্ডেন্সির ভেতর থেকে টাস্ক যোগ করা।
* কখন ব্যাকগ্রাউন্ড টাস্ক যথেষ্ট নয়।

///

আপনি একটি *পাথ অপারেশন ফাংশন* বা ডিপেন্ডেন্সি ফাংশনে `BackgroundTasks` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন, তারপর রেসপন্স পাঠানোর পরে ব্যাকগ্রাউন্ড টাস্ক চালানোর সময়সূচি করতে এটি ব্যবহার করতে পারেন।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import BackgroundTasks
```

/// tip | উদাহরণ দিয়ে বুঝি

রেস্টুরেন্টে খাবার দিয়েই ওয়েটার আপনাকে বসিয়ে রাখে না, খাবার পরিবেশন (রেসপন্স) করে তারপর রান্নাঘর গোছায় (ব্যাকগ্রাউন্ড টাস্ক)। ইমেইল পাঠানো, লগ লেখা, থাম্বনেইল বানানোর মতো ধীর কাজ ব্যবহারকারীকে অপেক্ষা না করিয়ে পরে করা যায়।

///

## `add_task(func, *args, **kwargs)` { #bn-add-task }

| আর্গুমেন্ট | কী |
| --- | --- |
| `func` | যে ফাংশন পরে চলবে; সাধারণ `def` বা `async def` দুটোই চলে |
| `*args`, `**kwargs` | ফাংশনটিকে দেওয়ার আর্গুমেন্ট |

একাধিক `add_task()` দিলে যে ক্রমে যোগ করা হয়েছে সেই ক্রমে একের পর এক চলে।

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def write_log(message: str, level: str = "INFO"):
    with open("log.txt", mode="a", encoding="utf-8") as f:
        f.write(f"[{level}] {message}\n")


async def send_email(email: str):
    print(f"{email} ঠিকানায় স্বাগত ইমেইল পাঠানো হলো")


@app.post("/signup/")
def signup(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    background_tasks.add_task(write_log, f"নতুন ইউজার: {email}", level="INFO")
    return {"message": "নিবন্ধন সম্পন্ন"}
```

ব্যবহারকারী সাথে সাথে "নিবন্ধন সম্পন্ন" উত্তর পায়, আর ইমেইল ও লগ তার পরে চলে।

## ডিপেন্ডেন্সি থেকে টাস্ক যোগ { #bn-in-dependency }

একই রিকোয়েস্টে পাথ অপারেশন আর ডিপেন্ডেন্সি একই `BackgroundTasks` অবজেক্ট পায়, তাই দুই জায়গা থেকে যোগ করা টাস্ক একসাথে চলে।

```python
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI

app = FastAPI()


def log_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        background_tasks.add_task(print, f"খোঁজা হয়েছে: {q}")
    return q


@app.get("/search/")
def search(q: Annotated[str | None, Depends(log_query)]):
    return {"q": q}
```

/// warning | কখন যথেষ্ট নয়

ব্যাকগ্রাউন্ড টাস্ক একই সার্ভার প্রসেসে চলে। সার্ভার রিস্টার্ট হলে চলমান টাস্ক হারিয়ে যায়, আর ভারী কাজ (ঘণ্টাখানেকের হিসাব, ভিডিও রূপান্তর) সার্ভারকে ধীর করে। সেসব ক্ষেত্রে Celery বা অন্য কোনো job queue টুল ব্যবহার করুন।

///

বিস্তারিত: [ব্যাকগ্রাউন্ড টাস্ক](../tutorial/background-tasks.md)।

/// check | সংক্ষেপে মনে রাখুন

* প্যারামিটারে `background_tasks: BackgroundTasks`, তারপর `background_tasks.add_task(func, ...)`।
* রেসপন্স পাঠানোর পরে টাস্কগুলো ক্রমানুসারে চলে।
* ছোট-মাঝারি কাজের জন্য; ভারী বা গুরুত্বপূর্ণ কাজের জন্য আলাদা job queue।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.BackgroundTasks
