# Templating - `Jinja2Templates` { #templating-jinja2templates }

/// note | এই পেজে যা পাবেন

`Jinja2Templates` ক্লাসের বিস্তারিত, যা দিয়ে HTML টেমপ্লেটে ডেটা বসিয়ে পূর্ণ ওয়েবপেজ তৈরি করা যায়।

///

Jinja টেমপ্লেট রেন্ডার করতে `Jinja2Templates` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [টেমপ্লেট নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/advanced/templates/)।

আপনি এটি সরাসরি `fastapi.templating` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.templating import Jinja2Templates
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/hello/{name}", response_class=HTMLResponse)
def hello(request: Request, name: str):
    return templates.TemplateResponse(
        request=request, name="hello.html", context={"name": name}
    )
```

`templates/hello.html` ফাইলের ভেতরে `name` ভেরিয়েবলটি বসিয়ে HTML পেজ তৈরি হবে। টেমপ্লেট হলো একটি ফাঁকা ফর্মের মতো, যার খালি ঘরগুলো কোড পূরণ করে দেয়।

///

::: fastapi.templating.Jinja2Templates
