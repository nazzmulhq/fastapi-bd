# Dependencies - `Depends()` এবং `Security()` { #dependencies-depends-and-security }

/// note | এই পেজে যা পাবেন

* ডিপেন্ডেন্সি ইনজেকশনের দুটি মূল ফাংশন `Depends()` আর `Security()`।
* প্রতিটি প্যারামিটারের অর্থ: `dependency`, `use_cache`, `scope`, `scopes`, উদাহরণসহ।
* ফাংশন, ক্লাস আর `yield`-ওয়ালা ডিপেন্ডেন্সি, আর সাব-ডিপেন্ডেন্সি।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## `Depends()` { #depends }

ডিপেন্ডেন্সি মূলত বিশেষ ফাংশন `Depends()` দিয়ে সামলানো হয়, যা একটি callable (কল করা যায় এমন কিছু, যেমন একটি ফাংশন) নেয়।

এখানে এটি আর এর প্যারামিটারগুলোর রেফারেন্স দেওয়া হলো।

আপনি এটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Depends
```

/// tip | উদাহরণ দিয়ে বুঝি

ডিপেন্ডেন্সি হলো রাঁধুনির সহকারী। রাঁধুনি (আপনার পাথ অপারেশন) শুধু বলে "আমার লগইন করা ইউজার লাগবে", "ডেটাবেস সংযোগ লাগবে"; সহকারী (ডিপেন্ডেন্সি) সেটা তৈরি করে হাতে দেয়। একই সহকারী অনেক রান্নায় কাজে লাগে, আর সহকারীরও নিজের সহকারী থাকতে পারে (সাব-ডিপেন্ডেন্সি)।

///

### `Depends()`-এর প্যারামিটার { #bn-depends-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `dependency` | যে ফাংশন বা ক্লাস FastAPI কল করবে। নিজে কল করবেন না, শুধু নাম দিন: `Depends(get_db)`, `Depends(get_db())` নয় |
| `use_cache` | ডিফল্ট `True`: একই রিকোয়েস্টে একই ডিপেন্ডেন্সি কয়েক জায়গায় লাগলেও একবারই চলে, ফলাফল আবার ব্যবহার হয়। `False` দিলে প্রতিবার নতুন করে চলে |
| `scope` | মূলত `yield`-ওয়ালা ডিপেন্ডেন্সির জন্য: `"function"` হলে `yield`-এর পরের কোড রেসপন্স পাঠানোর **আগে** চলে, `"request"` হলে রেসপন্স পাঠানোর **পরে** |

### উদাহরণ ১: সাধারণ ফাংশন ডিপেন্ডেন্সি { #bn-depends-function }

```python
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


def common_parameters(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]


@app.get("/items/")
def read_items(commons: CommonsDep):
    return commons


@app.get("/users/")
def read_users(commons: CommonsDep):
    return commons
```

(`skip` আর `limit` কোয়েরি প্যারামিটার দুটি রাউটেই একবার লিখেই পাওয়া গেল। `CommonsDep` একটি type alias, যাতে বারবার পুরো `Annotated[...]` লিখতে না হয়।)

### উদাহরণ ২: `yield` দিয়ে খোলা-বন্ধ (ডেটাবেস সংযোগ) { #bn-depends-yield }

```python
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


class FakeDB:
    def close(self):
        print("সংযোগ বন্ধ")


def get_db():
    db = FakeDB()  # রিকোয়েস্টের শুরুতে সংযোগ খোলা
    try:
        yield db  # পাথ অপারেশন এটি ব্যবহার করে
    finally:
        db.close()  # কাজ শেষে বন্ধ


@app.get("/orders/")
def read_orders(db: Annotated[FakeDB, Depends(get_db, scope="request")]):
    return {"db": "ready"}
```

(`scope="request"` দেওয়ায় `db.close()` রেসপন্স ক্লায়েন্টের কাছে পাঠানোর পরে চলে, যা স্ট্রিমিং রেসপন্সে ডেটাবেস খোলা রাখতে কাজের। সাধারণ ক্ষেত্রে `scope` না দিলেই চলে।)

### উদাহরণ ৩: সাব-ডিপেন্ডেন্সি আর `use_cache` { #bn-depends-sub }

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()


def get_token(authorization: Annotated[str | None, Header()] = None):
    if not authorization:
        raise HTTPException(status_code=401, detail="লগইন করুন")
    return authorization


def get_current_user(token: Annotated[str, Depends(get_token)]):  # সাব-ডিপেন্ডেন্সি
    return {"name": "rahim", "token": token}


@app.get("/me")
def me(
    user: Annotated[dict, Depends(get_current_user)],
    token: Annotated[str, Depends(get_token)],  # একই রিকোয়েস্টে আবার, কিন্তু cache থেকে
):
    return {"user": user, "token": token}
```

(`get_token` দুই জায়গায় লাগলেও `use_cache=True` (ডিফল্ট) থাকায় একবারই চলে।)

বিস্তারিত: [ডিপেন্ডেন্সি](../tutorial/dependencies/index.md), [সাব-ডিপেন্ডেন্সি](../tutorial/dependencies/sub-dependencies.md), [yield-সহ ডিপেন্ডেন্সি](../tutorial/dependencies/dependencies-with-yield.md), [ক্লাস হিসেবে ডিপেন্ডেন্সি](../tutorial/dependencies/classes-as-dependencies.md)।

::: fastapi.Depends

## `Security()` { #security }

অনেক ক্ষেত্রে আপনি `Depends()` দিয়ে ডিপেন্ডেন্সি ব্যবহার করেই নিরাপত্তা (অনুমোদন, অথেনটিকেশন ইত্যাদি) সামলাতে পারেন।

কিন্তু যখন আপনি OAuth2 scope-ও ঘোষণা করতে চান, তখন `Depends()`-এর বদলে `Security()` ব্যবহার করতে পারেন।

আপনি `Security()` সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import Security
```

### `Security()`-এর প্যারামিটার { #bn-security-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `dependency` | `Depends()`-এর মতোই, যে ফাংশন FastAPI কল করবে |
| `scopes` | এই পাথ অপারেশনে কোন OAuth2 অনুমতি (scope) লাগবে, যেমন `["items:read"]` |
| `use_cache` | `Depends()`-এর মতোই |

ডিপেন্ডেন্সি ফাংশন `SecurityScopes` প্যারামিটার দিয়ে জানতে পারে কোন কোন scope চাওয়া হয়েছে:

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token", scopes={"items:read": "আইটেম পড়া", "items:write": "আইটেম লেখা"}
)


def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    token_scopes = ["items:read"]  # আসল অ্যাপে টোকেন থেকে পড়া হবে
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=403, detail="যথেষ্ট অনুমতি নেই")
    return {"name": "rahim"}


@app.get("/items/")
def read_items(user: Annotated[dict, Security(get_current_user, scopes=["items:read"])]):
    return [{"item": "কলম"}]


@app.post("/items/")
def create_item(user: Annotated[dict, Security(get_current_user, scopes=["items:write"])]):
    return {"ok": True}
```

/// info | `Depends()` বনাম `Security()`

দুটো প্রায় একই কাজ করে। পার্থক্য শুধু এই যে `Security()`-তে বাড়তি `scopes` প্যারামিটার আছে, যা ডকসে (`/docs`-এর Authorize বোতামে) দেখায় কোন অনুমতি লাগবে আর ডিপেন্ডেন্সিকে `SecurityScopes` দিয়ে তা জানায়। বিস্তারিত দেখুন [OAuth2 scopes](../advanced/security/oauth2-scopes.md) পেজে।

///

/// warning | সাধারণ ভুল

`Depends(get_db())` লিখবেন না (ফাংশন কল করে দেওয়া)। লিখুন `Depends(get_db)`; কখন কল করতে হবে তা FastAPI নিজেই ঠিক করে।

///

/// check | সংক্ষেপে মনে রাখুন

* `Depends(func)`: রিকোয়েস্টের আগে `func` চালিয়ে ফলাফল দাও; একই রিকোয়েস্টে ফলাফল cache হয়।
* `yield`-ওয়ালা ডিপেন্ডেন্সি দিয়ে খোলা-বন্ধ (ডেটাবেস, ফাইল); `scope` দিয়ে বন্ধ হওয়ার সময় ঠিক করা যায়।
* OAuth2 অনুমতি লাগলে `Security(func, scopes=[...])`।

///

::: fastapi.Security
