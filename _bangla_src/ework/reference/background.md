# Background Tasks - `BackgroundTasks` { #background-tasks-backgroundtasks }

/// note | এই পেজে যা পাবেন

`BackgroundTasks` ক্লাস আর এর `add_task()` মেথডের বিস্তারিত, যা দিয়ে রেসপন্স পাঠানোর পরে কোনো কাজ চালানো যায়।

///

আপনি একটি *পাথ অপারেশন ফাংশন* বা ডিপেন্ডেন্সি ফাংশনে `BackgroundTasks` টাইপের একটি প্যারামিটার ঘোষণা করতে পারেন, তারপর রেসপন্স পাঠানোর পরে ব্যাকগ্রাউন্ড টাস্ক চালানোর সময়সূচি করতে এটি ব্যবহার করতে পারেন।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import BackgroundTasks
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def send_email(email: str):
    print(f"ইমেইল পাঠানো হচ্ছে: {email}")


@app.post("/signup/")
def signup(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "নিবন্ধন সম্পন্ন"}
```

ব্যবহারকারী সাথে সাথে "নিবন্ধন সম্পন্ন" উত্তর পায়, আর ইমেইল পাঠানোর ধীর কাজটি তার পরে ব্যাকগ্রাউন্ডে চলে। বিস্তারিত দেখুন [ব্যাকগ্রাউন্ড টাস্ক](../tutorial/background-tasks.md) পেজে।

///

::: fastapi.BackgroundTasks
