# নিরাপত্তা টুল { #security-tools }

/// note | এই পেজে যা পাবেন

* API সুরক্ষিত করার সব তৈরি টুল: API key, HTTP Basic/Bearer/Digest, OAuth2 আর OpenID Connect।
* প্রতিটির প্যারামিটার সারণি, কী ফেরত দেয়, আর একটি করে চলমান উদাহরণ।
* লগইন ফর্ম (`OAuth2PasswordRequestForm`) আর scope যাচাই (`SecurityScopes`)।
* প্রতিটি অংশের শেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

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

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

এই টুলগুলো হলো দারোয়ান। প্রত্যেক দারোয়ান জানে পরিচয়পত্র কোথায় খুঁজতে হবে (হেডারে, কুকিতে, কোয়েরিতে) আর সেটি বের করে আপনার হাতে দেয়। পরিচয়পত্রটি **আসল কিনা**, অর্থাৎ টোকেন বা পাসওয়ার্ড সঠিক কিনা, সেটা যাচাই করা আপনার নিজের কোডের কাজ।

///

| টুল | পরিচয় কোথা থেকে আসে | আপনি কী পান | কখন |
| --- | --- | --- | --- |
| `APIKeyHeader` / `APIKeyQuery` / `APIKeyCookie` | হেডার / কোয়েরি / কুকি | চাবির স্ট্রিং | সার্ভার-থেকে-সার্ভার, সহজ API |
| `HTTPBasic` | `Authorization: Basic ...` | `HTTPBasicCredentials` (username, password) | ছোট অভ্যন্তরীণ টুল |
| `HTTPBearer` | `Authorization: Bearer <টোকেন>` | `HTTPAuthorizationCredentials` | যেকোনো টোকেন (JWT ইত্যাদি) |
| `HTTPDigest` | `Authorization: Digest ...` | `HTTPAuthorizationCredentials` | পুরনো সিস্টেম |
| `OAuth2PasswordBearer` | `Authorization: Bearer <টোকেন>` | টোকেন স্ট্রিং | নিজের লগইন পেজ + টোকেন (সবচেয়ে প্রচলিত) |
| `OAuth2AuthorizationCodeBearer` | `Authorization: Bearer <টোকেন>` | টোকেন স্ট্রিং | বাইরের লগইন সার্ভার (Google, GitHub...) |
| `OpenIdConnect` | `Authorization` হেডার | হেডারের পুরো মান | OpenID Connect প্রদানকারী |

সব টুলের একটি সাধারণ প্যারামিটার আছে:

| প্যারামিটার | কী করে |
| --- | --- |
| `auto_error` | `True` (ডিফল্ট): পরিচয় না পেলে নিজে থেকেই `401` এরর দেয়। `False`: এরর না দিয়ে `None` ফেরত দেয়, যাতে "লগইন ঐচ্ছিক" রাউট বানানো যায় |
| `scheme_name` | `/docs`-এ এই নিরাপত্তা স্কিমের নাম |
| `description` | `/docs`-এ স্কিমের বর্ণনা |

## API Key নিরাপত্তা স্কিম { #api-key-security-schemes }

| প্যারামিটার | কী করে |
| --- | --- |
| `name` | হেডার, কোয়েরি প্যারামিটার বা কুকির নাম, যেমন `"X-API-Key"` |
| `scheme_name`, `description`, `auto_error` | ওপরের সারণির মতো |

ফেরত দেয়: চাবির স্ট্রিং (বা `auto_error=False` হলে না পেলে `None`)।

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

app = FastAPI()
api_key_header = APIKeyHeader(name="X-API-Key", description="আপনার গোপন API চাবি")
VALID_KEYS = {"key-123", "key-456"}


def get_api_key(key: Annotated[str, Depends(api_key_header)]) -> str:
    if key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="ভুল API চাবি")
    return key


@app.get("/reports")
def reports(key: Annotated[str, Depends(get_api_key)]):
    return {"used_key": key}
```

`APIKeyQuery(name="api_key")` দিলে `/reports?api_key=key-123` থেকে, আর `APIKeyCookie(name="session")` দিলে কুকি থেকে পড়বে; বাকি কোড একই।

::: fastapi.security.APIKeyCookie

::: fastapi.security.APIKeyHeader

::: fastapi.security.APIKeyQuery

## HTTP অথেনটিকেশন স্কিম { #http-authentication-schemes }

| ক্লাস | বিশেষ প্যারামিটার |
| --- | --- |
| `HTTPBasic` | `realm`: ব্রাউজারের লগইন বক্সে দেখানো এলাকার নাম |
| `HTTPBearer` | `bearerFormat`: টোকেনের ধরন, যেমন `"JWT"` (শুধু ডকসের জন্য) |
| `HTTPDigest` | (শুধু সাধারণ প্যারামিটার) |

### `HTTPBasic` উদাহরণ { #bn-http-basic }

```python
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic(realm="Admin area")


def check_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> str:
    ok_user = secrets.compare_digest(credentials.username.encode(), b"admin")
    ok_pass = secrets.compare_digest(credentials.password.encode(), b"s3cret")
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=401,
            detail="ভুল ইউজারনেম বা পাসওয়ার্ড",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/admin")
def admin(username: Annotated[str, Depends(check_admin)]):
    return {"hello": username}
```

/// info | কোডটি সহজ ভাষায়

`secrets.compare_digest` সময় না ফাঁস করে তুলনা করে। সাধারণ `==` প্রথম অমিল অক্ষরে থেমে যায়, ফলে কত সময় লাগল দেখে আক্রমণকারী অক্ষর অক্ষর করে পাসওয়ার্ড অনুমান করতে পারে।

///

### `HTTPBearer` উদাহরণ { #bn-http-bearer }

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer = HTTPBearer(bearerFormat="JWT")


@app.get("/profile")
def profile(creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)]):
    # creds.scheme == "Bearer", creds.credentials == আসল টোকেন
    return {"token": creds.credentials}
```

::: fastapi.security.HTTPBasic

::: fastapi.security.HTTPBearer

::: fastapi.security.HTTPDigest

## HTTP লগইন তথ্য (Credentials) { #http-credentials }

ওপরের HTTP স্কিমগুলো ডিপেন্ডেন্সি হিসেবে এই অবজেক্টগুলো ফেরত দেয়:

| ক্লাস | ফিল্ড | কে ফেরত দেয় |
| --- | --- | --- |
| `HTTPBasicCredentials` | `username`, `password` | `HTTPBasic` |
| `HTTPAuthorizationCredentials` | `scheme` (যেমন `"Bearer"`), `credentials` (টোকেন) | `HTTPBearer`, `HTTPDigest` |

::: fastapi.security.HTTPAuthorizationCredentials

::: fastapi.security.HTTPBasicCredentials

## OAuth2 অথেনটিকেশন { #oauth2-authentication }

### `OAuth2PasswordBearer` { #bn-oauth2-password-bearer }

| প্যারামিটার | কী করে |
| --- | --- |
| `tokenUrl` | যে পাথে ইউজারনেম-পাসওয়ার্ড পাঠিয়ে টোকেন পাওয়া যায়, যেমন `"token"`; `/docs`-এর Authorize বোতাম এটি ব্যবহার করে (বাধ্যতামূলক) |
| `scopes` | সম্ভাব্য scope আর তাদের বর্ণনার ডিকশনারি, যেমন `{"items:read": "আইটেম পড়া"}` |
| `refreshUrl` | টোকেন নবায়নের পাথ (ঐচ্ছিক) |
| `scheme_name`, `description`, `auto_error` | সাধারণ প্যারামিটার |

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
fake_tokens = {"token-of-rahim": "rahim"}


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    if form.username != "rahim" or form.password != "secret":
        raise HTTPException(status_code=400, detail="ভুল ইউজারনেম বা পাসওয়ার্ড")
    return {"access_token": "token-of-rahim", "token_type": "bearer"}


@app.get("/me")
def read_me(token: Annotated[str, Depends(oauth2_scheme)]):
    username = fake_tokens.get(token)
    if username is None:
        raise HTTPException(status_code=401, detail="টোকেন সঠিক নয়", headers={"WWW-Authenticate": "Bearer"})
    return {"username": username}
```

`/docs`-এ গিয়ে "Authorize" চাপুন, `rahim` / `secret` দিন; এরপর `/me` টোকেনসহ চলবে। আসল অ্যাপে টোকেন হিসেবে JWT ব্যবহার করুন, দেখুন [পাসওয়ার্ড হ্যাশিং ও JWT সহ OAuth2](../../tutorial/security/oauth2-jwt.md)।

### `OAuth2AuthorizationCodeBearer` { #bn-oauth2-authorization-code }

বাইরের লগইন সার্ভার থাকলে (ব্যবহারকারী সেখানে গিয়ে লগইন করে কোড নিয়ে ফেরে):

| প্যারামিটার | কী করে |
| --- | --- |
| `authorizationUrl` | লগইন পেজের ঠিকানা |
| `tokenUrl` | কোডের বদলে টোকেন নেওয়ার ঠিকানা |
| `refreshUrl`, `scopes` | ওপরের মতো |

```python
from fastapi.security import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://auth.example.com/authorize",
    tokenUrl="https://auth.example.com/token",
    scopes={"openid": "পরিচয়", "email": "ইমেইল দেখা"},
)
```

`OAuth2` হলো এদের অভিভাবক ক্লাস; নিজের কাস্টম flow বানাতে চাইলে এটি ব্যবহার করবেন, সাধারণত দরকার হয় না।

::: fastapi.security.OAuth2

::: fastapi.security.OAuth2AuthorizationCodeBearer

::: fastapi.security.OAuth2PasswordBearer

## OAuth2 পাসওয়ার্ড ফর্ম { #oauth2-password-form }

`Depends()` দিয়ে ব্যবহার করলে লগইন ফর্মের ফিল্ডগুলো পড়ে দেয় (ফর্ম ডেটা হিসেবে, JSON নয়; `python-multipart` লাগে)।

| ফিল্ড | কী রাখে |
| --- | --- |
| `username`, `password` | লগইন তথ্য (বাধ্যতামূলক) |
| `scope` → `scopes` | স্পেস দিয়ে আলাদা করা scope লেখা; `form.scopes` এ তালিকা হিসেবে পাবেন |
| `grant_type` | OAuth2-এর নিয়মে `"password"`; সাধারণ ফর্মে ঐচ্ছিক |
| `client_id`, `client_secret` | ক্লায়েন্ট অ্যাপের পরিচয় (ঐচ্ছিক) |

`OAuth2PasswordRequestFormStrict` একই জিনিস, তবে `grant_type="password"` বাধ্যতামূলক, যেমনটা OAuth2-এর মূল নিয়মে বলা আছে।

::: fastapi.security.OAuth2PasswordRequestForm

::: fastapi.security.OAuth2PasswordRequestFormStrict

## ডিপেন্ডেন্সিতে OAuth2 নিরাপত্তা Scope { #oauth2-security-scopes-in-dependencies }

`SecurityScopes` প্যারামিটার হিসেবে নিলে এই ডিপেন্ডেন্সি আর তার ওপরের সব `Security(..., scopes=[...])` মিলিয়ে কোন কোন scope দরকার তা জানা যায়:

| অ্যাট্রিবিউট | কী রাখে |
| --- | --- |
| `scopes` | দরকারি scope-এর তালিকা, যেমন `["items:read", "me"]` |
| `scope_str` | একই তালিকা স্পেস দিয়ে জোড়া স্ট্রিং; `WWW-Authenticate` হেডারে দিতে কাজে লাগে |

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes={"items:read": "আইটেম পড়া"})
token_scopes = {"token-a": ["items:read"], "token-b": []}


def get_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]):
    granted = token_scopes.get(token, [])
    for scope in security_scopes.scopes:
        if scope not in granted:
            raise HTTPException(
                status_code=403,
                detail="অনুমতি নেই",
                headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
            )
    return {"token": token}


@app.get("/items/")
def items(user: Annotated[dict, Security(get_user, scopes=["items:read"])]):
    return {"items": ["বই", "কলম"], "user": user}
```

`token-a` দিয়ে চলবে, `token-b` দিয়ে `403`। বিস্তারিত: [OAuth2 scope](../../advanced/security/oauth2-scopes.md)।

::: fastapi.security.SecurityScopes

## OpenID Connect { #openid-connect }

| প্যারামিটার | কী করে |
| --- | --- |
| `openIdConnectUrl` | প্রদানকারীর কনফিগারেশন ঠিকানা, সাধারণত `.../.well-known/openid-configuration` (বাধ্যতামূলক) |
| `scheme_name`, `description`, `auto_error` | সাধারণ প্যারামিটার |

ফেরত দেয়: `Authorization` হেডারের পুরো মান (যেমন `"Bearer eyJ..."`); টোকেন যাচাই আপনাকেই করতে হবে।

```python
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.security import OpenIdConnect

app = FastAPI()
oidc = OpenIdConnect(openIdConnectUrl="https://accounts.google.com/.well-known/openid-configuration")


@app.get("/whoami")
def whoami(authorization: Annotated[str, Depends(oidc)]):
    return {"authorization_header": authorization}
```

/// check | সংক্ষেপে মনে রাখুন

* এই টুলগুলো শুধু পরিচয়পত্র বের করে দেয়; যাচাই আপনার ডিপেন্ডেন্সির কাজ।
* না পেলে ডিফল্টভাবে `401`; ঐচ্ছিক লগইনে `auto_error=False`।
* সবচেয়ে প্রচলিত: `OAuth2PasswordBearer(tokenUrl="token")` + `OAuth2PasswordRequestForm` + JWT।
* scope যাচাইয়ে `Security(..., scopes=[...])` আর `SecurityScopes`।

///

::: fastapi.security.OpenIdConnect
