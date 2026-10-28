# OpenAPI `docs` { #openapi-docs }

/// note | এই পেজে যা পাবেন

* `/docs` (Swagger UI) আর `/redoc` (ReDoc) পেজ তৈরির ফাংশনগুলোর প্রতিটি প্যারামিটার।
* নিজের সার্ভার থেকে JavaScript/CSS দেওয়া (ইন্টারনেট ছাড়া ডকস), Swagger UI-এর সেটিংস বদলানো, OAuth2 লগইন আগে থেকে পূরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

OpenAPI-এর স্বয়ংক্রিয় UI ডকুমেন্টেশন সামলানোর ইউটিলিটি, যার মধ্যে আছে Swagger UI (ডিফল্টভাবে `/docs`-এ) আর ReDoc (ডিফল্টভাবে `/redoc`-এ)।

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

FastAPI নিজে থেকেই `/docs` আর `/redoc` পেজ বানায়, যেমন রেস্টুরেন্ট নিজেই মেনু ছাপায়। এই ফাংশনগুলো দিয়ে আপনি নিজের মতো করে মেনু ছাপাতে পারেন: ভিন্ন শিরোনাম, নিজের লোগো, বা ইন্টারনেট ছাড়া চলে এমন।

///

ব্যবহারের ধাপ সবসময় একই:

1. `FastAPI(docs_url=None)` (বা `redoc_url=None`) দিয়ে ডিফল্ট পেজ বন্ধ করুন।
2. নিজের একটি রাউট বানিয়ে সেখান থেকে এই ফাংশনের ফল ফেরত দিন। ফাংশনগুলো সরাসরি `HTMLResponse` ফেরত দেয়।

## `get_swagger_ui_html()` { #bn-swagger }

| প্যারামিটার | কী করে |
| --- | --- |
| `openapi_url` | OpenAPI স্কিমার ঠিকানা, সাধারণত `app.openapi_url` (বাধ্যতামূলক) |
| `title` | ব্রাউজার ট্যাবের শিরোনাম (বাধ্যতামূলক) |
| `swagger_js_url` | Swagger UI-এর JavaScript ফাইলের ঠিকানা; ডিফল্ট jsDelivr CDN |
| `swagger_css_url` | Swagger UI-এর CSS ফাইলের ঠিকানা |
| `swagger_favicon_url` | ট্যাবের ছোট আইকন |
| `oauth2_redirect_url` | OAuth2 লগইনের পরে ফেরার পাথ, সাধারণত `app.swagger_ui_oauth2_redirect_url` |
| `init_oauth` | Authorize বক্সে আগে থেকে বসানো মান, যেমন `{"clientId": "my-app"}` |
| `swagger_ui_parameters` | Swagger UI-এর বাড়তি সেটিংস; না দিলে `swagger_ui_default_parameters` ব্যবহার হয় |

```python
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="আমার API - ডকস",
        swagger_js_url="/static/swagger-ui-bundle.js",  # নিজের সার্ভার থেকে
        swagger_css_url="/static/swagger-ui.css",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_ui_parameters={"docExpansion": "none", "syntaxHighlight": {"theme": "obsidian"}},
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()
```

/// info | কোডটি সহজ ভাষায়

* JS/CSS ফাইল `static/` ফোল্ডারে রেখে নিজের সার্ভার থেকে দেওয়া হচ্ছে, তাই CDN-এ পৌঁছাতে না পারলেও (অফিসের বন্ধ নেটওয়ার্ক) ডকস চলবে।
* `docExpansion: "none"`: সব রাউট গুটানো অবস্থায় দেখাবে।
* OAuth2 ব্যবহার করলে redirect পেজটিও নিজে দিতে হয়, তাই দ্বিতীয় রাউট।

///

## `get_redoc_html()` { #bn-redoc }

| প্যারামিটার | কী করে |
| --- | --- |
| `openapi_url`, `title` | ওপরের মতো (বাধ্যতামূলক) |
| `redoc_js_url` | ReDoc-এর JavaScript ফাইলের ঠিকানা |
| `redoc_favicon_url` | ট্যাবের আইকন |
| `with_google_fonts` | Google Fonts লোড করবে কিনা (ডিফল্ট `True`); ইন্টারনেট ছাড়া চালাতে `False` |

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html

app = FastAPI(redoc_url=None)


@app.get("/redoc", include_in_schema=False)
def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="আমার API - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        with_google_fonts=False,
    )
```

## `get_swagger_ui_oauth2_redirect_html()` আর `swagger_ui_default_parameters` { #bn-others }

* `get_swagger_ui_oauth2_redirect_html()`: কোনো প্যারামিটার নেই; OAuth2 লগইনের পরে Swagger UI-তে ফেরার ছোট HTML পেজ দেয় (ওপরের প্রথম উদাহরণ দেখুন)।
* `swagger_ui_default_parameters`: Swagger UI-এর ডিফল্ট সেটিংসের ডিকশনারি: `dom_id`, `layout`, `deepLinking`, `showExtensions`, `showCommonExtensions`। পুরো অ্যাপে সেটিংস বদলাতে সাধারণত `FastAPI(swagger_ui_parameters={...})` দেওয়াই সহজ; দেখুন [Swagger UI কনফিগার](../../how-to/configure-swagger-ui.md)।

বিস্তারিত: [কাস্টম ডকস UI স্ট্যাটিক অ্যাসেট](../../how-to/custom-docs-ui-assets.md)।

/// check | সংক্ষেপে মনে রাখুন

* ডিফল্ট বন্ধ করুন (`docs_url=None`), তারপর নিজের রাউট থেকে `get_swagger_ui_html(...)` ফেরত দিন।
* ইন্টারনেট ছাড়া ডকস: `swagger_js_url`/`swagger_css_url`/`redoc_js_url` নিজের সার্ভারে, আর `with_google_fonts=False`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.openapi.docs.get_swagger_ui_html

::: fastapi.openapi.docs.get_redoc_html

::: fastapi.openapi.docs.get_swagger_ui_oauth2_redirect_html

::: fastapi.openapi.docs.swagger_ui_default_parameters
