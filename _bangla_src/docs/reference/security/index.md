# নিরাপত্তা টুল { #security-tools }

/// note | এই পেজে যা পাবেন

API সুরক্ষিত করার সব তৈরি টুলের বিস্তারিত: API key, HTTP Basic/Bearer/Digest, OAuth2 আর OpenID Connect। প্রতিটি টুল একটি ডিপেন্ডেন্সি হিসেবে কাজ করে আর `/docs`-এ "Authorize" বোতামে যুক্ত হয়।

///

যখন OAuth2 scope-সহ ডিপেন্ডেন্সি ঘোষণা করতে হয়, তখন আপনি `Security()` ব্যবহার করেন।

কিন্তু তবুও আপনাকে নির্ধারণ করতে হবে dependable কী, অর্থাৎ যে callable আপনি `Depends()` বা `Security()`-এ প্যারামিটার হিসেবে দেন।

সেই dependable তৈরি করতে আপনি একাধিক টুল ব্যবহার করতে পারেন, আর এগুলো OpenAPI-তে যুক্ত হয়, তাই স্বয়ংক্রিয় ডকস UI-তে দেখানো হয়, স্বয়ংক্রিয়ভাবে তৈরি ক্লায়েন্ট আর SDK এগুলো ব্যবহার করতে পারে, ইত্যাদি।

আপনি এগুলো `fastapi.security` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.security import (
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
    HTTPDigest,
    OAuth2,
    OAuth2AuthorizationCodeBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    OAuth2PasswordRequestFormStrict,
    OpenIdConnect,
    SecurityScopes,
)
```

এগুলো সম্পর্কে আরও পড়ুন [নিরাপত্তা নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/security/)।

/// info | কোনটি কখন

* **API key** (`APIKeyHeader`, `APIKeyQuery`, `APIKeyCookie`): একটি গোপন চাবি হেডার, কোয়েরি বা কুকিতে পাঠানো। সার্ভার-থেকে-সার্ভার যোগাযোগে জনপ্রিয়।
* **HTTP Basic** (`HTTPBasic`): ইউজারনেম আর পাসওয়ার্ড প্রতিটি রিকোয়েস্টে। সহজ, তবে HTTPS ছাড়া অনিরাপদ।
* **HTTP Bearer** (`HTTPBearer`): `Authorization: Bearer <টোকেন>` হেডারে একটি টোকেন।
* **OAuth2** (`OAuth2PasswordBearer` ইত্যাদি): লগইন করে টোকেন নেওয়া, তারপর সেই টোকেন দিয়ে রিকোয়েস্ট। আধুনিক অ্যাপে সবচেয়ে প্রচলিত।
* **OpenID Connect** (`OpenIdConnect`): Google-এর মতো বাইরের পরিচয় প্রদানকারী দিয়ে লগইন।

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/me")
def read_me(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
```

`oauth2_scheme` রিকোয়েস্টের `Authorization` হেডার থেকে টোকেন বের করে দেয়, না থাকলে 401 এরর ফেরত দেয়। বিস্তারিত দেখুন [নিরাপত্তা](../../tutorial/security/index.md) অধ্যায়ে।

///

## API Key নিরাপত্তা স্কিম { #api-key-security-schemes }

::: fastapi.security.APIKeyCookie

::: fastapi.security.APIKeyHeader

::: fastapi.security.APIKeyQuery

## HTTP অথেনটিকেশন স্কিম { #http-authentication-schemes }

::: fastapi.security.HTTPBasic

::: fastapi.security.HTTPBearer

::: fastapi.security.HTTPDigest

## HTTP লগইন তথ্য (Credentials) { #http-credentials }

::: fastapi.security.HTTPAuthorizationCredentials

::: fastapi.security.HTTPBasicCredentials

## OAuth2 অথেনটিকেশন { #oauth2-authentication }

::: fastapi.security.OAuth2

::: fastapi.security.OAuth2AuthorizationCodeBearer

::: fastapi.security.OAuth2PasswordBearer

## OAuth2 পাসওয়ার্ড ফর্ম { #oauth2-password-form }

::: fastapi.security.OAuth2PasswordRequestForm

::: fastapi.security.OAuth2PasswordRequestFormStrict

## ডিপেন্ডেন্সিতে OAuth2 নিরাপত্তা Scope { #oauth2-security-scopes-in-dependencies }

::: fastapi.security.SecurityScopes

## OpenID Connect { #openid-connect }

::: fastapi.security.OpenIdConnect
