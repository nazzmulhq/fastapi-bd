# ওয়েব আর API রিকোয়েস্ট { #web-and-api-requests }

/// note | এই পেজে যা শিখবেন

* `httpx` দিয়ে অন্য কোনো API থেকে আনা ডেটা Pydantic মডেল দিয়ে যাচাই করা।
* একটি তালিকা ফেরত দেয় এমন API-র উত্তর `TypeAdapter(list[...])` দিয়ে যাচাই।
* যাচাই এরর কেন প্রায়ই "API বদলে গেছে" এর প্রথম সংকেত।

///

রিকোয়েস্ট আর রেসপন্সের ডেটা যাচাই ও সিরিয়ালাইজ করার দারুণ উপায় Pydantic মডেল।
FastAPI, Django, Flask আর HTTPX-এর মতো অনেক web framework আর লাইব্রেরিতে Pydantic গুরুত্বপূর্ণ ভূমিকা রাখে।

/// tip | উদাহরণ দিয়ে বুঝি

অন্যের API থেকে আসা ডেটা হলো দোকান থেকে আসা পার্সেল। খুলে ব্যবহারের আগে মিলিয়ে দেখা ভালো ভেতরে যা থাকার কথা তা আছে কিনা। Pydantic মডেল হলো সেই অর্ডারের তালিকা; কিছু কম বা ভুল থাকলে সাথে সাথে জানিয়ে দেয়, পরে কোডের গভীরে গিয়ে রহস্যময় এরর হওয়ার আগেই।

///

## `httpx` রিকোয়েস্ট { #httpx-requests }

[`httpx`](https://www.python-httpx.org/) হলো synchronous আর asynchronous API সহ Python 3-এর একটি HTTP client।
নিচের উদাহরণে, একজন ব্যবহারকারীর ডেটা পেতে আমরা [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)-তে রিকোয়েস্ট পাঠাই আর একটি Pydantic মডেল দিয়ে তা যাচাই করি।

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

* `raise_for_status()`: স্ট্যাটাস কোড 4xx/5xx হলে আগেই এরর তোলে, ফলে ভুল উত্তর যাচাই পর্যন্ত যায় না।
* `response.json()` ডিকশনারি দেয়, আর `User.model_validate(...)` সেটি যাচাই করে `User` অবজেক্ট বানায়।
* API-র উত্তরে আরও অনেক ফিল্ড থাকলেও (ঠিকানা, ফোন...), মডেলে যা আছে শুধু সেগুলোই রাখা হয়; বাকিগুলো ডিফল্টভাবে উপেক্ষিত।

///

HTTP রিকোয়েস্ট নিয়ে কাজের সময় Pydantic-এর [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] টুল প্রায়ই খুব
কাজে আসে। একই ধরনের একটি উদাহরণ দেখুন, যেখানে আমরা ব্যবহারকারীদের একটি তালিকা যাচাই করছি:

⟦CODE2⟧

1. লক্ষ করুন, ব্যবহারকারীদের তালিকা পেতে এখানে আমরা `/users/` endpoint-এ রিকোয়েস্ট পাঠাচ্ছি।

এভাবে রেসপন্স যাচাই করলে, একটি [`ValidationError`][pydantic_core.ValidationError] প্রায়ই
প্রথম সংকেত যে আপনি যে API-র ওপর নির্ভর করেন সেটি তার রেসপন্সের ফরম্যাট বদলেছে। তখন দরকারি প্রশ্ন হলো
*রেসপন্সে আসলে কী ছিল*, আর *এটি কবে থেকে শুরু হলো*:
[Logfire দিয়ে ব্যর্থ যাচাই রেকর্ড করা](../errors/troubleshooting.md) দুটো প্রশ্নেরই উত্তর দেয়, কারণ প্রতিটি
ব্যর্থতা তার গোছানো এরর আর প্রত্যাখ্যাত মানসহ জমা থাকে।

/// tip | async সংস্করণ

`httpx.AsyncClient` দিয়ে একই কাজ async ভাবে:

```python
import httpx

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


async def get_user(user_id: int) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'https://jsonplaceholder.typicode.com/users/{user_id}')
        response.raise_for_status()
        return User.model_validate_json(response.content)  # bytes থেকে সরাসরি, আরও দ্রুত
```

///

<!-- TODO: httpx, flask, Django rest framework, FastAPI -->

/// check | সংক্ষেপে মনে রাখুন

* `response.raise_for_status()`, তারপর `Model.model_validate(response.json())` বা `Model.model_validate_json(response.content)`।
* তালিকার জন্য `TypeAdapter(list[Model])`, একবার বানিয়ে বারবার ব্যবহার।
* যাচাই এরর মানে প্রায়ই বাইরের API বদলে গেছে; মডেলেই সমস্যা ধরা পড়ে।

///
