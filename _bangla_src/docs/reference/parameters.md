# রিকোয়েস্ট প্যারামিটার { #request-parameters }

/// note | এই পেজে যা পাবেন

রিকোয়েস্টের বিভিন্ন জায়গা (URL পাথ, কোয়েরি, বডি, হেডার, কুকি, ফর্ম, ফাইল) থেকে ডেটা নেওয়ার বিশেষ ফাংশনগুলোর বিস্তারিত তালিকা।

///

এখানে রিকোয়েস্ট প্যারামিটারগুলোর রেফারেন্স তথ্য দেওয়া হলো।

এগুলো হলো সেই বিশেষ ফাংশন যেগুলো রিকোয়েস্ট থেকে ডেটা পেতে আপনি `Annotated`-সহ *পাথ অপারেশন ফাংশনের* প্যারামিটার বা ডিপেন্ডেন্সি ফাংশনে রাখতে পারেন।

এতে আছে:

* `Query()`
* `Path()`
* `Body()`
* `Cookie()`
* `Header()`
* `Form()`
* `File()`

আপনি এগুলোর সবই সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Body, Cookie, File, Form, Header, Path, Query
```

/// info | কোনটি কোথা থেকে ডেটা আনে

| ফাংশন | ডেটা কোথা থেকে আসে | উদাহরণ |
| --- | --- | --- |
| `Path()` | URL-এর পাথের অংশ | `/items/5`-এর `5` |
| `Query()` | URL-এর `?` এর পরের অংশ | `/items?q=book`-এর `book` |
| `Body()` | রিকোয়েস্টের বডি (সাধারণত JSON) | `{"name": "বই"}` |
| `Header()` | HTTP হেডার | `User-Agent` |
| `Cookie()` | ব্রাউজারের কুকি | `session_id` |
| `Form()` | HTML ফর্মের ডেটা | লগইন ফর্মের `username` |
| `File()` | আপলোড করা ফাইল | একটি ছবি |

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/items/{item_id}")
def read_item(
    item_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(max_length=50)] = None,
):
    return {"item_id": item_id, "q": q}
```

* `Path(ge=1)`: `item_id` অবশ্যই ১ বা তার বেশি হতে হবে।
* `Query(max_length=50)`: `q` সর্বোচ্চ ৫০ অক্ষরের হতে পারে।

নিচের তালিকায় প্রতিটি ফাংশনের সব প্যারামিটার (`ge`, `le`, `min_length`, `alias`, `description` ইত্যাদি) পাবেন।

///

::: fastapi.Query

::: fastapi.Path

::: fastapi.Body

::: fastapi.Cookie

::: fastapi.Header

::: fastapi.Form

::: fastapi.File
