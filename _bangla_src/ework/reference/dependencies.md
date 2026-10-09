# Dependencies - `Depends()` এবং `Security()` { #dependencies-depends-and-security }

/// note | এই পেজে যা পাবেন

ডিপেন্ডেন্সি ইনজেকশনের দুটি মূল ফাংশন `Depends()` আর `Security()`-এর সব প্যারামিটারের বিস্তারিত।

///

## `Depends()` { #depends }

ডিপেন্ডেন্সি মূলত বিশেষ ফাংশন `Depends()` দিয়ে সামলানো হয়, যা একটি callable (কল করা যায় এমন কিছু, যেমন একটি ফাংশন) নেয়।

এখানে এটি আর এর প্যারামিটারগুলোর রেফারেন্স দেওয়া হলো।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Depends
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


def common_parameters(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


@app.get("/items/")
def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

`Depends(common_parameters)` মানে "এই ফাংশন চালানোর আগে `common_parameters` চালাও, আর তার ফলাফল `commons`-এ দাও।" একই ডিপেন্ডেন্সি অনেক পাথ অপারেশনে বারবার ব্যবহার করা যায়। বিস্তারিত দেখুন [ডিপেন্ডেন্সি](../tutorial/dependencies/index.md) অধ্যায়ে।

///

::: fastapi.Depends

## `Security()` { #security }

অনেক ক্ষেত্রে আপনি `Depends()` দিয়ে ডিপেন্ডেন্সি ব্যবহার করেই নিরাপত্তা (অনুমোদন, অথেনটিকেশন ইত্যাদি) সামলাতে পারেন।

কিন্তু যখন আপনি OAuth2 scope-ও ঘোষণা করতে চান, তখন `Depends()`-এর বদলে `Security()` ব্যবহার করতে পারেন।

আপনি `Security()` সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Security
```

/// info | `Depends()` বনাম `Security()`

দুটো প্রায় একই কাজ করে। পার্থক্য শুধু এই যে `Security()`-তে একটি বাড়তি `scopes` প্যারামিটার আছে, যেমন `Security(get_current_user, scopes=["items:read"])`, যা দিয়ে বলা যায় এই পাথ অপারেশনে কোন অনুমতি লাগবে। বিস্তারিত দেখুন [OAuth2 scopes](../advanced/security/oauth2-scopes.md) পেজে।

///

::: fastapi.Security
