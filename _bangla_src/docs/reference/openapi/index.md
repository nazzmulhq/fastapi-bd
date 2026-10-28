# OpenAPI { #openapi }

/// note | এই অংশটি কী

এখানে OpenAPI নিয়ে কাজ করার ভেতরের টুলগুলোর রেফারেন্স আছে: ডকস পেজ (`/docs`, `/redoc`) তৈরির ফাংশন আর OpenAPI স্কিমার Pydantic মডেল।

///

OpenAPI সামলানোর জন্য কয়েকটি ইউটিলিটি আছে।

সাধারণত আপনাকে এগুলো ব্যবহার করতে হবে না, যদি না আপনার এমন কোনো নির্দিষ্ট অ্যাডভান্সড প্রয়োজন থাকে যার জন্য এগুলো দরকার।

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

OpenAPI হলো আপনার API-এর "মেনু কার্ড": কোন পাথে কী পাওয়া যায়, কী দিতে হয়, কী ফেরত আসে। FastAPI আপনার কোড দেখে নিজেই এই মেনু (`/openapi.json`) লেখে, আর `/docs` ও `/redoc` সেটিকে সুন্দর করে দেখায়।

///

| কাজ | কোথায় দেখবেন |
| --- | --- |
| ডকস পেজের শিরোনাম, JS/CSS, সেটিংস নিজের মতো করা | [OpenAPI `docs`](docs.md) (সাথে দেখুন [কাস্টম ডকস UI স্ট্যাটিক অ্যাসেট](../../how-to/custom-docs-ui-assets.md)) |
| OpenAPI স্কিমার গঠন বা কোন অংশে কী ফিল্ড | [OpenAPI `models`](models.md) |
| স্কিমায় বাড়তি তথ্য যোগ (লোগো ইত্যাদি) | [OpenAPI বাড়ানো](../../how-to/extending-openapi.md) |
| শিরোনাম, বিবরণ, ট্যাগ, সংস্করণ | `FastAPI(title=..., description=..., version=..., openapi_tags=...)`, দেখুন [`FastAPI` ক্লাস](../fastapi.md) |

### দ্রুত কিছু কৌশল { #bn-quick }

```python
from fastapi import FastAPI

app = FastAPI(
    title="দোকান API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",  # স্কিমার ঠিকানা বদলানো
    docs_url="/help",                     # Swagger UI নতুন ঠিকানায়
    redoc_url=None,                       # ReDoc বন্ধ
)


@app.get("/internal", include_in_schema=False)  # এই রাউট ডকসে দেখাবে না
def internal():
    return {"ok": True}
```

/// tip | প্রোডাকশনে ডকস বন্ধ

`FastAPI(openapi_url=None)` দিলে স্কিমা আর দুটো ডকস পেজই বন্ধ হয়ে যায়।

///
