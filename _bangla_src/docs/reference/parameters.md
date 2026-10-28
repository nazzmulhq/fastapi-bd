# রিকোয়েস্ট প্যারামিটার { #request-parameters }

/// note | এই পেজে যা পাবেন

* সাতটি বিশেষ ফাংশন `Query()`, `Path()`, `Body()`, `Cookie()`, `Header()`, `Form()`, `File()`: কোনটি রিকোয়েস্টের কোন অংশ থেকে ডেটা আনে।
* সবার সাধারণ প্যারামিটারগুলো (ডিফল্ট, alias, শর্ত, ডকসের তথ্য) দলে ভাগ করে, উদাহরণসহ।
* প্রতিটি ফাংশনের নিজস্ব বিশেষ প্যারামিটার (`embed`, `convert_underscores`, `media_type`) আর একটি করে উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

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

## এক নজরে: কোনটি কোথা থেকে ডেটা আনে { #bn-overview }

| ফাংশন | ডেটা কোথা থেকে আসে | উদাহরণ | ডিফল্ট আচরণ |
| --- | --- | --- | --- |
| `Path()` | URL-এর পাথের অংশ | `/items/5`-এর `5` | সবসময় বাধ্যতামূলক |
| `Query()` | URL-এর `?` এর পরের অংশ | `/items?q=book`-এর `book` | ডিফল্ট না দিলে বাধ্যতামূলক |
| `Body()` | রিকোয়েস্টের বডি (সাধারণত JSON) | `{"name": "বই"}` | JSON হিসেবে পড়ে |
| `Header()` | HTTP হেডার | `User-Agent`, `X-Token` | নামের `_` নিজে থেকেই `-` হয় |
| `Cookie()` | ব্রাউজারের কুকি | `session_id` | |
| `Form()` | HTML ফর্মের ডেটা | লগইন ফর্মের `username` | `python-multipart` লাগে |
| `File()` | আপলোড করা ফাইল | একটি ছবি | `python-multipart` লাগে |

/// tip | উদাহরণ দিয়ে বুঝি

একটি রিকোয়েস্ট হলো একটি পার্সেলের মতো। খামের ওপরে ঠিকানা (Path), ঠিকানার পাশে ছোট নোট (Query), খামের গায়ে লাগানো স্টিকার (Header, Cookie), আর ভেতরে আসল জিনিস (Body, Form, File)। এই ফাংশনগুলো FastAPI-কে বলে দেয় কোন তথ্য পার্সেলের কোন জায়গা থেকে তুলতে হবে, আর কী নিয়মে যাচাই করতে হবে।

///

ব্যবহারের নিয়ম সবার জন্য একই: `Annotated[টাইপ, ফাংশন(...)]`।

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

## সবার সাধারণ প্যারামিটার { #bn-common-params }

### ডিফল্ট মান { #bn-defaults }

| প্যারামিটার | কী করে |
| --- | --- |
| `default` | ডিফল্ট মান; সাধারণত `Annotated` দিয়ে লিখলে `= মান` হিসেবে দেওয়া হয় |
| `default_factory` | প্রতিবার নতুন ডিফল্ট তৈরির ফাংশন, যেমন `default_factory=list` |

```python
# ঐচ্ছিক, ডিফল্ট 10
limit: Annotated[int, Query()] = 10
```

### নাম বদলানো (alias) { #bn-alias }

| প্যারামিটার | কী করে |
| --- | --- |
| `alias` | রিকোয়েস্টে ভিন্ন নাম, যেমন Python-এ অবৈধ নাম `item-query` |
| `validation_alias` | শুধু পড়ার সময়ের নাম |
| `serialization_alias` | শুধু লেখার সময়ের নাম |
| `alias_priority` | alias generator-এর সাথে কোনটির অগ্রাধিকার |

```python
# URL: /items/?item-query=book
q: Annotated[str | None, Query(alias="item-query")] = None
```

### যাচাইয়ের শর্ত { #bn-constraints }

| প্যারামিটার | কী করে | প্রযোজ্য |
| --- | --- | --- |
| `gt`, `ge`, `lt`, `le` | এর চেয়ে বড় / বড় বা সমান / ছোট / ছোট বা সমান | সংখ্যা |
| `multiple_of` | এর গুণিতক হতে হবে, যেমন `multiple_of=5` | সংখ্যা |
| `allow_inf_nan` | `inf` আর `nan` গ্রহণ করবে কিনা | float |
| `max_digits`, `decimal_places` | মোট অঙ্ক আর দশমিকের পরের ঘর | `Decimal` |
| `min_length`, `max_length` | সর্বনিম্ন / সর্বোচ্চ দৈর্ঘ্য | স্ট্রিং, তালিকা |
| `pattern` | regex নিয়ম, যেমন `"^[a-z]+$"` (`regex` এর পুরনো নাম) | স্ট্রিং |
| `strict` | `True` দিলে টাইপ রূপান্তর হবে না | সব |
| `discriminator` | union-এ কোন ফিল্ড দেখে মডেল বাছাই হবে | union |

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/products/{code}")
def get_product(
    code: Annotated[str, Path(min_length=3, max_length=8, pattern="^[A-Z0-9]+$")],
    price_max: Annotated[float, Query(gt=0, le=100000)] = 5000,
    page: Annotated[int, Query(ge=1)] = 1,
):
    return {"code": code, "price_max": price_max, "page": page}
```

(ভুল মান, যেমন `page=0` বা ছোট হাতের `code`, দিলে FastAPI নিজেই `422` এরর ফেরত দেয়, আপনার ফাংশন চলেই না।)

বিস্তারিত: [কোয়েরি প্যারামিটার আর স্ট্রিং যাচাই](../tutorial/query-params-str-validations.md), [পাথ প্যারামিটার আর সংখ্যার যাচাই](../tutorial/path-params-numeric-validations.md)।

### ডকসের তথ্য { #bn-docs-info }

| প্যারামিটার | কী করে |
| --- | --- |
| `title`, `description` | `/docs`-এ প্যারামিটারের শিরোনাম আর বর্ণনা |
| `examples` | উদাহরণ মানের তালিকা, যেমন `examples=["বই"]` (`example` এর পুরনো রূপ) |
| `openapi_examples` | নাম আর বর্ণনাসহ একাধিক উদাহরণ, যা Swagger UI-তে ড্রপডাউন হিসেবে দেখায় |
| `deprecated` | `True` দিলে ডকসে "পুরনো" চিহ্নিত হবে |
| `include_in_schema` | `False` দিলে প্যারামিটারটি ডকসে লুকানো থাকবে |
| `json_schema_extra` | JSON Schema-তে বাড়তি তথ্য |

```python
q: Annotated[
    str | None,
    Query(
        title="খোঁজার শব্দ",
        description="বইয়ের নামের যেকোনো অংশ",
        examples=["পথের পাঁচালী"],
        deprecated=False,
    ),
] = None
```

## প্রতিটি ফাংশনের নিজস্ব দিক { #bn-each-function }

### `Path()` { #bn-path }

পাথ প্যারামিটার সবসময় বাধ্যতামূলক (URL-এর অংশ, তাই বাদ দেওয়ার সুযোগ নেই)। পাথে `{item_id}` লিখলে একই নামের প্যারামিটার পাথ থেকে আসে।

```python
@app.get("/users/{user_id}/orders/{order_id}")
def get_order(
    user_id: Annotated[int, Path(title="ইউজার আইডি", ge=1)],
    order_id: Annotated[int, Path(ge=1)],
):
    return {"user_id": user_id, "order_id": order_id}
```

### `Query()` { #bn-query }

সাধারণ টাইপের (`int`, `str` ...) যে প্যারামিটার পাথে নেই, তা ডিফল্টভাবেই কোয়েরি। `Query()` লাগে শর্ত বা ডকসের তথ্য যোগ করতে, আর তালিকা নিতে।

```python
# URL: /items/?tag=new&tag=sale  →  tag = ["new", "sale"]
@app.get("/items/")
def read_items(tag: Annotated[list[str], Query()] = []):
    return {"tags": tag}
```

### `Body()` { #bn-body }

Pydantic মডেল প্যারামিটার ডিফল্টভাবেই বডি থেকে আসে। `Body()` লাগে একটি সাধারণ মান (যেমন `int`) বডিতে রাখতে, অথবা আকার বদলাতে।

* `embed=True`: একটি মাত্র মডেল হলেও বডিতে তার নাম দিয়ে মোড়ানো আশা করে: `{"item": {...}}`।
* `media_type`: ডকসে দেখানো কনটেন্ট টাইপ (ডিফল্ট `"application/json"`)।

```python
from typing import Annotated

from fastapi import Body, FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    item: Annotated[Item, Body(embed=True)],
    importance: Annotated[int, Body(gt=0)],
):
    return {"item_id": item_id, "item": item, "importance": importance}
```

এই রাউটের বডি দেখতে হবে: `{"item": {"name": "কলম", "price": 10}, "importance": 5}`।

বিস্তারিত: [বডি - একাধিক প্যারামিটার](../tutorial/body-multiple-params.md)।

### `Header()` { #bn-header }

* `convert_underscores` (ডিফল্ট `True`): Python নামের `_`-কে হেডারের `-` বানায়। তাই `user_agent` পড়ে `User-Agent` হেডার। হেডারের নাম বড়-ছোট হাতের পার্থক্য করে না।

```python
@app.get("/me")
def me(
    user_agent: Annotated[str | None, Header()] = None,
    x_token: Annotated[list[str] | None, Header()] = None,  # একই হেডার একাধিকবার
):
    return {"User-Agent": user_agent, "X-Token": x_token}
```

### `Cookie()` { #bn-cookie }

```python
@app.get("/dashboard")
def dashboard(session_id: Annotated[str | None, Cookie()] = None):
    return {"session_id": session_id}
```

### `Form()` { #bn-form }

HTML ফর্ম (`application/x-www-form-urlencoded`) থেকে মান নেয়। আগে `pip install python-multipart` করতে হয়।

```python
from typing import Annotated

from fastapi import FastAPI, Form

app = FastAPI()


@app.post("/login/")
def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}
```

### `File()` { #bn-file }

আপলোড করা ফাইল নেয় (`multipart/form-data`)। টাইপ `bytes` দিলে পুরো ফাইল মেমোরিতে আসে; বড় ফাইলের জন্য `UploadFile` ভালো। `Form()` আর `File()` একসাথে ব্যবহার করা যায়।

```python
from typing import Annotated

from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()


@app.post("/upload/")
async def upload(
    file: Annotated[UploadFile, File(description="প্রোফাইল ছবি")],
    caption: Annotated[str, Form()] = "",
):
    return {"filename": file.filename, "caption": caption}
```

বিস্তারিত: [রিকোয়েস্ট ফর্ম](../tutorial/request-forms.md), [রিকোয়েস্ট ফাইল](../tutorial/request-files.md), [হেডার প্যারামিটার](../tutorial/header-params.md), [কুকি প্যারামিটার](../tutorial/cookie-params.md)।

/// warning | সাধারণ ভুল

* `Form()` বা `File()` থাকলে একই রাউটে JSON `Body()` রাখা যায় না, কারণ বডি হয় ফর্ম, নয়তো JSON; দুটো একসাথে নয়।
* `Path()`-এ ডিফল্ট মান দিলেও লাভ নেই; পাথ প্যারামিটার সবসময় বাধ্যতামূলক।
* `list[str]` কোয়েরি নিতে `Query()` লিখতেই হবে, নইলে FastAPI এটিকে বডি ভাববে।

///

/// check | সংক্ষেপে মনে রাখুন

* `Annotated[টাইপ, Query()/Path()/Body()/...(...)]`: কোথা থেকে ডেটা আসবে + কী নিয়মে যাচাই হবে।
* সবার সাধারণ প্যারামিটার: ডিফল্ট, alias, শর্ত (`gt`, `max_length`, `pattern` ...), ডকসের তথ্য (`title`, `description`, `examples`)।
* বিশেষ: `Body(embed=True)`, `Header(convert_underscores=...)`, `Form()`/`File()`-এর জন্য `python-multipart`।

///

## পূর্ণ API তালিকা { #bn-full-api }

নিচে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ তালিকা: প্রতিটি ফাংশনের প্রতিটি প্যারামিটারের টাইপ, ডিফল্ট মান আর বিস্তারিত বর্ণনা।

::: fastapi.Query

::: fastapi.Path

::: fastapi.Body

::: fastapi.Cookie

::: fastapi.Header

::: fastapi.Form

::: fastapi.File
