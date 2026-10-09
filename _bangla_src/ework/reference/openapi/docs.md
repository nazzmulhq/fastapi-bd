# OpenAPI `docs` { #openapi-docs }

/// note | এই পেজে যা পাবেন

`/docs` (Swagger UI) আর `/redoc` (ReDoc) পেজের HTML তৈরি করার ফাংশনগুলোর বিস্তারিত। নিজের মতো ডকস পেজ বানাতে এগুলো কাজে লাগে।

///

OpenAPI-এর স্বয়ংক্রিয় UI ডকুমেন্টেশন সামলানোর ইউটিলিটি, যার মধ্যে আছে Swagger UI (ডিফল্টভাবে `/docs`-এ) আর ReDoc (ডিফল্টভাবে `/redoc`-এ)।

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(docs_url=None)


@app.get("/docs", include_in_schema=False)
def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="আমার API - ডকস",
    )
```

ডিফল্ট `/docs` বন্ধ করে নিজের শিরোনামসহ একই ধরনের পেজ তৈরি করা হলো। বিস্তারিত দেখুন [কাস্টম ডকস UI স্ট্যাটিক অ্যাসেট](../../how-to/custom-docs-ui-assets.md) পেজে।

///

::: fastapi.openapi.docs.get_swagger_ui_html

::: fastapi.openapi.docs.get_redoc_html

::: fastapi.openapi.docs.get_swagger_ui_oauth2_redirect_html

::: fastapi.openapi.docs.swagger_ui_default_parameters
