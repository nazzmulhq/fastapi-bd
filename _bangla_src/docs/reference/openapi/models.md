# OpenAPI `models` { #openapi-models }

/// note | এই পেজে যা পাবেন

* OpenAPI স্কিমার গঠন সহজ ভাষায়, আর কোন মডেল কোন অংশের জন্য।
* স্কিমা হাতে বদলানোর একটি উদাহরণ।
* সবশেষে প্রতিটি মডেলের (যেমন `Info`, `Contact`, `License`, `Operation`, `Schema`) স্বয়ংক্রিয় পূর্ণ তালিকা।

///

তৈরি হওয়া OpenAPI তৈরি আর যাচাই করতে ব্যবহৃত OpenAPI-এর Pydantic মডেলগুলো।

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

OpenAPI স্কিমা হলো আপনার API-এর পূর্ণ "নকশা" (ব্লুপ্রিন্ট), একটি বড় JSON। এই মডেলগুলো হলো নকশার প্রতিটি অংশের ছাঁচ: কোথায় কী লেখা থাকবে, কোন ঘর বাধ্যতামূলক। FastAPI এগুলো দিয়ে নিশ্চিত করে যে তৈরি নকশা নিয়মমাফিক।

///

স্কিমার গঠন আর সংশ্লিষ্ট মডেল:

```
OpenAPI                      ← পুরো স্কিমা (openapi, info, paths, components ...)
├── Info                     ← title, version, description
│   ├── Contact              ← name, url, email
│   └── License              ← name, identifier/url
├── Server                   ← servers: url, description, variables
├── paths: {"/items": PathItem}
│   └── PathItem             ← get, post, put, delete ...
│       └── Operation        ← summary, tags, parameters, requestBody, responses
│           ├── Parameter    ← name, in (query/path/header/cookie), schema
│           ├── RequestBody  ← content: {"application/json": MediaType}
│           └── Response     ← description, content, headers
├── Components               ← schemas, securitySchemes, ... (বারবার ব্যবহৃত অংশ)
│   ├── Schema               ← একটি ডেটা মডেলের JSON Schema
│   └── SecurityBase ...     ← APIKey, HTTPBase, HTTPBearer, OAuth2, OpenIdConnect
└── Tag                      ← tags: name, description, externalDocs
```

## কখন কাজে লাগে { #bn-when }

সাধারণত সরাসরি দরকার হয় না। তবে যদি [OpenAPI বাড়ানো](../../how-to/extending-openapi.md)-র মতো কাজে স্কিমা হাতে বদলান, তখন কোন অংশে কী ফিল্ড থাকে তা দেখতে এই তালিকা কাজে লাগে।

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()


@app.get("/items/")
def read_items():
    return []


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title="দোকান API", version="2.0.0", routes=app.routes)
    schema["info"]["x-logo"] = {"url": "https://example.com/logo.png"}  # Info অংশে বাড়তি তথ্য
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
```

`info`-তে কী কী ফিল্ড রাখা যায় তা নিচের `Info` মডেলে দেখুন; `x-` দিয়ে শুরু বাড়তি ফিল্ডও (extension) অনুমোদিত।

/// check | সংক্ষেপে মনে রাখুন

* এগুলো OpenAPI স্কিমার প্রতিটি অংশের Pydantic মডেল।
* স্কিমা হাতে বদলানোর সময় কোন ঘরে কী যায় দেখতে এই তালিকা ব্যবহার করুন।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: fastapi.openapi.models
