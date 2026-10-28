# Templating - `Jinja2Templates` { #templating-jinja2templates }

/// note | এই পেজে যা পাবেন

* টেমপ্লেট কী, আর `Jinja2Templates` দিয়ে কীভাবে HTML পেজ বানাতে হয়।
* constructor (`directory`, `context_processors`, `env`) আর `TemplateResponse()`-এর প্রতিটি প্যারামিটার।
* টেমপ্লেটে `url_for()` দিয়ে লিংক আর স্ট্যাটিক ফাইলের ঠিকানা তৈরি।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

Jinja টেমপ্লেট রেন্ডার করতে `Jinja2Templates` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [টেমপ্লেট নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/templates/)।

আপনি এটি সরাসরি `fastapi.templating` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.templating import Jinja2Templates
```

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

টেমপ্লেট হলো একটি ছাপানো ফর্ম যার কিছু ঘর ফাঁকা: "নাম: ____"। আপনার কোড ঘরগুলো পূরণ করে দেয় (context), আর তৈরি হয় সম্পূর্ণ HTML পেজ। একই ফর্ম হাজার জনের জন্য ব্যবহার করা যায়।

///

প্রথমে `pip install jinja2` করুন।

## constructor প্যারামিটার { #bn-constructor }

| প্যারামিটার | কী করে |
| --- | --- |
| `directory` | টেমপ্লেট ফাইলের ফোল্ডার, যেমন `"templates"`; একাধিক ফোল্ডারের তালিকাও দেওয়া যায় |
| `context_processors` | ফাংশনের তালিকা; প্রতিটি `request` নিয়ে একটি ডিকশনারি ফেরত দেয়, যা **সব** টেমপ্লেটে নিজে থেকে যোগ হয় |
| `env` | নিজে বানানো `jinja2.Environment` (`directory`-র বদলে, একসাথে নয়) |

## `TemplateResponse()` প্যারামিটার { #bn-templateresponse }

| প্যারামিটার | কী করে |
| --- | --- |
| `request` | বর্তমান `Request` (বাধ্যতামূলক; টেমপ্লেটে `url_for` এর জন্য লাগে) |
| `name` | টেমপ্লেট ফাইলের নাম, যেমন `"item.html"` |
| `context` | টেমপ্লেটের ফাঁকা ঘর পূরণের ডিকশনারি |
| `status_code` | স্ট্যাটাস কোড, ডিফল্ট `200` |
| `headers`, `media_type`, `background` | অন্য রেসপন্সের মতোই |

## উদাহরণ { #bn-example }

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


def site_info(request: Request) -> dict:
    return {"site_name": "আমার দোকান"}


templates = Jinja2Templates(directory="templates", context_processors=[site_info])


@app.get("/items/{item_id}", response_class=HTMLResponse)
def read_item(request: Request, item_id: int):
    return templates.TemplateResponse(
        request=request,
        name="item.html",
        context={"item_id": item_id, "tags": ["নতুন", "ছাড়"]},
    )
```

`templates/item.html`:

{% raw %}

```jinja
<html>
<head>
    <title>{{ site_name }}</title>
    <link href="{{ url_for('static', path='/style.css') }}" rel="stylesheet">
</head>
<body>
    <h1>আইটেম নম্বর {{ item_id }}</h1>
    <ul>
    {% for tag in tags %}
        <li>{{ tag }}</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('read_item', item_id=item_id + 1) }}">পরের আইটেম</a>
</body>
</html>
```

{% endraw %}

/// info | কোডটি সহজ ভাষায়

* দুই জোড়া বাঁকা বন্ধনীর ভেতরের নাম (যেমন `item_id`) context থেকে মান বসায়।
* `for ... endfor` দিয়ে তালিকার প্রতিটি জিনিসের জন্য একটি করে লাইন তৈরি হয়।
* `site_name` context-এ দেওয়া হয়নি, তবু আছে, কারণ `context_processors` সব টেমপ্লেটে এটি যোগ করে।
* `url_for('static', path=...)` স্ট্যাটিক ফাইলের ঠিকানা, আর `url_for('read_item', item_id=...)` ফাংশনের নাম থেকে রাউটের ঠিকানা তৈরি করে।

///

/// warning | সাধারণ ভুল

পুরনো লেখায় `TemplateResponse("item.html", {"request": request, ...})` দেখতে পারেন। নতুন নিয়মে `request` আলাদা প্রথম আর্গুমেন্ট (বা `request=`), আর `name=` ও `context=` নাম দিয়ে দেওয়াই পরিষ্কার।

///

/// check | সংক্ষেপে মনে রাখুন

* `templates = Jinja2Templates(directory="templates")`।
* `templates.TemplateResponse(request=request, name="x.html", context={...})`।
* সব পেজে একই তথ্য দরকার হলে `context_processors`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.templating.Jinja2Templates
