# Static Files - `StaticFiles` { #static-files-staticfiles }

/// note | এই পেজে যা পাবেন

* `StaticFiles` দিয়ে একটি ফোল্ডারের ফাইল (CSS, JavaScript, ছবি) পরিবেশন।
* প্রতিটি প্যারামিটার (`directory`, `packages`, `html`, `check_dir`, `follow_symlink`) উদাহরণসহ।
* `mount()` আর `url_for()` কীভাবে একসাথে কাজ করে।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

JavaScript, CSS, ছবি ইত্যাদির মতো স্ট্যাটিক ফাইল পরিবেশন করতে `StaticFiles` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [স্ট্যাটিক ফাইল নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/static-files/)।

আপনি এটি সরাসরি `fastapi.staticfiles` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.staticfiles import StaticFiles
```

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

"স্ট্যাটিক" মানে যা বদলায় না: লোগো, স্টাইলশিট, স্ক্রিপ্ট। এগুলোর জন্য প্রতিবার Python কোড চালানোর দরকার নেই। `StaticFiles` হলো একটি তাক: ফোল্ডারে যা আছে, কেউ চাইলে হুবহু তুলে দেয়।

///

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
```

এখন `static/logo.png` ফাইলটি পাওয়া যাবে `http://127.0.0.1:8000/static/logo.png` ঠিকানায়।

* `"/static"`: কোন পাথের নিচে ফাইলগুলো দেখা যাবে।
* `StaticFiles(directory="static")`: ডিস্কের কোন ফোল্ডার থেকে।
* `name="static"`: নাম, যাতে টেমপ্লেটে `url_for("static", path="/logo.png")` দিয়ে ঠিকানা তৈরি করা যায়।

## প্যারামিটার { #bn-parameters }

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `directory` | `None` | ডিস্কের ফোল্ডার, যেমন `"static"` |
| `packages` | `None` | কোনো Python প্যাকেজের ভেতরের `statics` ফোল্ডার থেকে ফাইল; যেমন `["bootstrap4"]` বা `[("mypkg", "assets")]` |
| `html` | `False` | `True` হলে HTML মোড: ফোল্ডারের পাথ চাইলে `index.html` দেয়, না পেলে `404.html` দেখায় |
| `check_dir` | `True` | শুরুতেই ফোল্ডারটি আছে কিনা যাচাই; না থাকলে এরর |
| `follow_symlink` | `False` | symlink (শর্টকাট) অনুসরণ করে ফোল্ডারের বাইরের ফাইল দেওয়া যাবে কিনা |

### `html=True`: একটি পুরো স্ট্যাটিক সাইট { #bn-html-mode }

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/api/hello")
def hello():
    return {"msg": "হ্যালো"}


# সব API রাউটের পরে, সবশেষে মাউন্ট করুন
app.mount("/", StaticFiles(directory="site", html=True), name="site")
```

`/` চাইলে `site/index.html`, `/about/` চাইলে `site/about/index.html`, আর না থাকলে `site/404.html`।

/// warning | সাধারণ ভুল

* `/`-তে মাউন্ট করলে সেটি সব পাথ ধরে ফেলে, তাই API রাউটগুলো আগে সংজ্ঞায়িত করুন।
* ফোল্ডারটি চালানোর জায়গা থেকে খোঁজা হয়; অন্য ফোল্ডার থেকে সার্ভার চালালে ফাইল না-ও পেতে পারে। নিশ্চিত হতে `Path(__file__).parent / "static"` এর মতো পূর্ণ পথ দিন।
* React/Vue-র মতো single-page অ্যাপের জন্য [`app.frontend()`](fastapi.md) আরও সুবিধাজনক।

///

/// check | সংক্ষেপে মনে রাখুন

* `app.mount("/static", StaticFiles(directory="static"), name="static")`।
* `html=True` দিলে `index.html` আর `404.html` নিজে থেকে।
* `/`-তে মাউন্ট করলে সবশেষে করুন।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.staticfiles.StaticFiles
