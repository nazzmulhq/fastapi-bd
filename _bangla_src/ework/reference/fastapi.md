# `FastAPI` ক্লাস { #fastapi-class }

/// note | এই পেজে যা পাবেন

* প্রথমে একটি **সহজ গাইড**: `FastAPI()` তৈরির প্রতিটি প্যারামিটার কাজ অনুযায়ী দলে ভাগ করে, প্রতিটি দলের উদাহরণসহ।
* তারপর `@app.get()`, `@app.post()` ইত্যাদি ডেকোরেটরের প্রতিটি প্যারামিটারের অর্থ।
* `include_router()`, `websocket()`, `middleware()`, `exception_handler()`, `frontend()` এর মতো মেথড আর `state`, `dependency_overrides` এর মতো অ্যাট্রিবিউট।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি **পূর্ণ API তালিকা**, যেখানে প্রতিটি প্যারামিটারের টাইপ, ডিফল্ট মান আর বিস্তারিত বর্ণনা আছে।

///

এখানে `FastAPI` ক্লাসের রেফারেন্স তথ্য দেওয়া হলো, এর সব প্যারামিটার, অ্যাট্রিবিউট ও মেথডসহ।

আপনি `FastAPI` ক্লাসটি সরাসরি `fastapi` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi import FastAPI
```

## এক নজরে { #bn-overview }

আপনার পুরো ওয়েব অ্যাপ্লিকেশনটিই `FastAPI` ক্লাসের একটি অবজেক্ট। সাধারণত এর নাম রাখা হয় `app`, আর সার্ভার (`fastapi dev` বা Uvicorn) এই `app`-কেই চালায়।

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "স্বাগতম"}
```

/// tip | উদাহরণ দিয়ে বুঝি

`FastAPI()` হলো একটি রেস্টুরেন্ট খোলা। তৈরির সময় দেওয়া প্যারামিটারগুলো রেস্টুরেন্টের সাইনবোর্ড আর নিয়ম (নাম, মেনুর ঠিকানা, সব টেবিলে প্রযোজ্য নিয়ম)। আর `@app.get(...)` দিয়ে লেখা প্রতিটি ফাংশন হলো মেনুর একেকটি খাবার।

///

## `FastAPI()` তৈরির প্যারামিটার { #bn-constructor-params }

সব প্যারামিটার ঐচ্ছিক; কিছু না দিলেও অ্যাপ চলে। নিচে কাজ অনুযায়ী দলে ভাগ করা হলো।

### ডকুমেন্টেশনের তথ্য (metadata) { #bn-metadata }

এগুলো শুধু `/docs` আর `/redoc` পেজে কী দেখাবে তা ঠিক করে; অ্যাপের আচরণ বদলায় না।

| প্যারামিটার | কী করে |
| --- | --- |
| `title` | API-র নাম (ডিফল্ট `"FastAPI"`) |
| `summary` | এক লাইনের সারসংক্ষেপ |
| `description` | বিস্তারিত বর্ণনা, Markdown লেখা যায় |
| `version` | আপনার API-র সংস্করণ, যেমন `"1.0.0"` (FastAPI-র সংস্করণ নয়) |
| `terms_of_service` | ব্যবহারের শর্তাবলির URL |
| `contact` | যোগাযোগের তথ্য: `{"name": ..., "url": ..., "email": ...}` |
| `license_info` | লাইসেন্স: `{"name": "MIT", "url": ...}` |
| `openapi_tags` | প্রতিটি tag-এর বর্ণনা আর ক্রম |
| `openapi_external_docs` | বাইরের ডকুমেন্টেশনের লিংক |

```python
from fastapi import FastAPI

app = FastAPI(
    title="বইয়ের দোকান API",
    summary="বই খোঁজা আর অর্ডার করার API",
    description="এখানে **Markdown** লেখা যায়।",
    version="2.1.0",
    contact={"name": "সাপোর্ট টিম", "email": "support@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    openapi_tags=[
        {"name": "books", "description": "বই সংক্রান্ত সব কাজ"},
        {"name": "orders", "description": "অর্ডার দেওয়া আর দেখা"},
    ],
)
```

বিস্তারিত: [মেটাডেটা এবং ডকস URL](../tutorial/metadata.md)।

### ডকস আর OpenAPI-র ঠিকানা { #bn-docs-urls }

| প্যারামিটার | কী করে |
| --- | --- |
| `docs_url` | Swagger UI-র ঠিকানা (ডিফল্ট `"/docs"`); `None` দিলে বন্ধ |
| `redoc_url` | ReDoc-এর ঠিকানা (ডিফল্ট `"/redoc"`); `None` দিলে বন্ধ |
| `openapi_url` | OpenAPI JSON-এর ঠিকানা (ডিফল্ট `"/openapi.json"`); `None` দিলে সব ডকস বন্ধ |
| `swagger_ui_parameters` | Swagger UI-র সেটিং, যেমন `{"syntaxHighlight": False}` |
| `swagger_ui_oauth2_redirect_url` | OAuth2 লগইনের পরে ফেরার ঠিকানা |
| `swagger_ui_init_oauth` | Swagger UI-তে OAuth2-এর প্রাথমিক সেটিং |
| `include_in_schema` | `False` দিলে কোনো রাউটই OpenAPI-তে দেখাবে না |

```python
app = FastAPI(
    docs_url="/documentation",  # Swagger UI এখন /documentation-এ
    redoc_url=None,  # ReDoc বন্ধ
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
```

বিস্তারিত: [Swagger UI কনফিগার করা](../how-to/configure-swagger-ui.md), [শর্তসাপেক্ষ OpenAPI](../how-to/conditional-openapi.md)।

### সব পাথ অপারেশনে প্রযোজ্য সেটিং { #bn-global-settings }

এগুলো দিলে অ্যাপের **সব** রাউটে একসাথে প্রয়োগ হয়।

| প্যারামিটার | কী করে |
| --- | --- |
| `dependencies` | প্রতিটি রিকোয়েস্টে চলবে এমন ডিপেন্ডেন্সির তালিকা (যেমন API key যাচাই) |
| `responses` | সব রাউটের ডকসে বাড়তি রেসপন্স যোগ, যেমন `{404: {"description": "পাওয়া যায়নি"}}` |
| `default_response_class` | ডিফল্ট রেসপন্স ক্লাস, যেমন `ORJSONResponse` বা `HTMLResponse` |
| `deprecated` | `True` দিলে সব রাউট ডকসে deprecated দেখাবে |
| `callbacks` | সব রাউটে প্রযোজ্য OpenAPI callback |
| `generate_unique_id_function` | operation ID তৈরির নিজস্ব ফাংশন (SDK তৈরিতে কাজের) |
| `redirect_slashes` | `/items` আর `/items/`-এর মধ্যে স্বয়ংক্রিয় রিডাইরেক্ট (ডিফল্ট `True`) |
| `strict_content_type` | JSON বডির জন্য `Content-Type` হেডার বাধ্যতামূলক কিনা (ডিফল্ট `True`) |
| `separate_input_output_schemas` | ইনপুট আর আউটপুটের জন্য আলাদা JSON Schema (ডিফল্ট `True`) |

```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException


def verify_key(x_api_key: Annotated[str, Header()]):
    if x_api_key != "secret":
        raise HTTPException(status_code=401, detail="ভুল API key")


app = FastAPI(
    dependencies=[Depends(verify_key)],  # প্রতিটি রিকোয়েস্টে key যাচাই
    responses={401: {"description": "API key নেই বা ভুল"}},
)


@app.get("/items/")
def read_items():
    return ["বই", "কলম"]
```

বিস্তারিত: [গ্লোবাল ডিপেন্ডেন্সি](../tutorial/dependencies/global-dependencies.md), [OpenAPI-তে বাড়তি রেসপন্স](../advanced/additional-responses.md), [SDK তৈরি](../advanced/generate-clients.md), [কঠোর Content-Type যাচাই](../advanced/strict-content-type.md)।

### অ্যাপ চালু আর বন্ধের সময়ের কাজ { #bn-lifespan }

| প্যারামিটার | কী করে |
| --- | --- |
| `lifespan` | একটি async context manager: `yield`-এর আগের কোড চালু হওয়ার সময়, পরের কোড বন্ধের সময় চলে |
| `on_startup` | (পুরনো) চালু হওয়ার সময় চলা ফাংশনের তালিকা; এখন `lifespan` ব্যবহার করুন |
| `on_shutdown` | (পুরনো) বন্ধের সময় চলা ফাংশনের তালিকা; এখন `lifespan` ব্যবহার করুন |

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["answer"] = lambda x: x * 42  # চালু হওয়ার সময় মডেল লোড
    yield
    ml_models.clear()  # বন্ধের সময় পরিষ্কার


app = FastAPI(lifespan=lifespan)
```

বিস্তারিত: [Lifespan ইভেন্ট](../advanced/events.md)।

### Middleware আর এরর হ্যান্ডলার { #bn-middleware-exceptions }

| প্যারামিটার | কী করে |
| --- | --- |
| `middleware` | `Middleware(...)`-এর তালিকা, যা প্রতিটি রিকোয়েস্ট-রেসপন্সের চারপাশে চলে |
| `exception_handlers` | এক্সেপশন বা স্ট্যাটাস কোড থেকে হ্যান্ডলার ফাংশনের ডিকশনারি |

```python
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware import Middleware


async def not_found(request: Request, exc: Exception):
    return JSONResponse(status_code=404, content={"error": "এই পেজ নেই"})


app = FastAPI(
    middleware=[Middleware(GZipMiddleware, minimum_size=1000)],
    exception_handlers={404: not_found},
)
```

সাধারণত একই কাজ পরে `app.add_middleware(...)` আর `@app.exception_handler(...)` দিয়েও করা যায় (নিচে দেখুন)। বিস্তারিত: [Middleware](../tutorial/middleware.md), [এরর সামলানো](../tutorial/handling-errors.md)।

### প্রক্সির পেছনে চালানো { #bn-proxy }

| প্যারামিটার | কী করে |
| --- | --- |
| `root_path` | অ্যাপটি কোন path prefix-এর পেছনে আছে, যেমন `"/api/v1"` |
| `root_path_in_servers` | `root_path` OpenAPI-র `servers` তালিকায় যোগ হবে কিনা (ডিফল্ট `True`) |
| `servers` | ডকসে দেখানো সার্ভারের তালিকা, যেমন staging আর production |
| `openapi_prefix` | (পুরনো) `root_path`-এর পুরনো নাম |

```python
app = FastAPI(
    root_path="/api/v1",
    servers=[
        {"url": "https://stag.example.com", "description": "Staging"},
        {"url": "https://prod.example.com", "description": "Production"},
    ],
)
```

বিস্তারিত: [প্রক্সির পেছনে](../advanced/behind-a-proxy.md)।

### অন্যান্য প্যারামিটার { #bn-other-params }

| প্যারামিটার | কী করে |
| --- | --- |
| `debug` | `True` দিলে সার্ভার এররে বিস্তারিত traceback দেখায় (শুধু ডেভেলপমেন্টে) |
| `routes` | Starlette থেকে আসা, সরাসরি রাউটের তালিকা; সাধারণত ব্যবহার করবেন না |
| `webhooks` | webhook ডকুমেন্ট করার জন্য একটি `APIRouter` (সাধারণত `app.webhooks` ব্যবহার হয়) |
| `telemetry` | OpenTelemetry সেটিং, যেমন `{"tracing": False}` |

বিস্তারিত: [OpenAPI Webhook](../advanced/openapi-webhooks.md), [OpenTelemetry](../advanced/opentelemetry.md)।

## পাথ অপারেশন ডেকোরেটর { #bn-decorators }

`@app.get()`, `@app.post()`, `@app.put()`, `@app.patch()`, `@app.delete()`, `@app.options()`, `@app.head()`, `@app.trace()` সবগুলোর প্যারামিটার একই। শুধু HTTP মেথড আলাদা:

* `get` = ডেটা পড়া, `post` = নতুন কিছু তৈরি, `put` = পুরোটা বদলানো, `patch` = আংশিক বদলানো, `delete` = মুছে ফেলা।

| প্যারামিটার | কী করে |
| --- | --- |
| `path` | URL পাথ, যেমন `"/items/{item_id}"` (একমাত্র বাধ্যতামূলক প্যারামিটার) |
| `response_model` | রেসপন্সের মডেল: আউটপুট যাচাই, ফিল্টার আর ডকুমেন্ট করে |
| `status_code` | সফল রেসপন্সের স্ট্যাটাস কোড, যেমন `201` |
| `tags` | ডকসে কোন দলে দেখাবে, যেমন `["books"]` |
| `summary`, `description` | ডকসে শিরোনাম আর বর্ণনা (না দিলে ফাংশনের নাম আর docstring থেকে) |
| `response_description` | সফল রেসপন্সের বর্ণনা (ডিফল্ট `"Successful Response"`) |
| `responses` | বাড়তি সম্ভাব্য রেসপন্স, যেমন `{404: {"model": Message}}` |
| `deprecated` | `True` দিলে ডকসে কাটা দাগসহ "পুরনো" দেখাবে |
| `dependencies` | এই রাউটের জন্য ডিপেন্ডেন্সি, যার ফেরত মান দরকার নেই |
| `operation_id` | OpenAPI-তে এই অপারেশনের অনন্য নাম |
| `response_model_include` / `response_model_exclude` | রেসপন্সে কোন ফিল্ড রাখবেন/বাদ দেবেন |
| `response_model_by_alias` | রেসপন্সে alias নাম ব্যবহার (ডিফল্ট `True`) |
| `response_model_exclude_unset` | যে ফিল্ড সেট করা হয়নি তা বাদ |
| `response_model_exclude_defaults` | ডিফল্টের সমান মানের ফিল্ড বাদ |
| `response_model_exclude_none` | `None` মানের ফিল্ড বাদ |
| `include_in_schema` | `False` দিলে রাউটটি ডকসে লুকানো থাকবে |
| `response_class` | রেসপন্সের ক্লাস, যেমন `HTMLResponse` |
| `name` | রাউটের ভেতরের নাম (`url_for`-এ ব্যবহার হয়) |
| `callbacks` | এই রাউটের OpenAPI callback |
| `openapi_extra` | OpenAPI schema-তে হাতে বাড়তি তথ্য যোগ |
| `generate_unique_id_function` | শুধু এই রাউটের operation ID তৈরির ফাংশন |

```python
from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()


class Book(BaseModel):
    title: str
    price: float
    note: str | None = None


class Message(BaseModel):
    message: str


@app.post(
    "/books/",
    response_model=Book,
    status_code=status.HTTP_201_CREATED,
    tags=["books"],
    summary="নতুন বই যোগ করুন",
    response_description="যোগ হওয়া বই",
    responses={409: {"model": Message, "description": "বইটি আগেই আছে"}},
    response_model_exclude_none=True,
)
def create_book(book: Book):
    """
    একটি নতুন বই তৈরি করে।

    - **title**: বইয়ের নাম
    - **price**: দাম
    """
    return book
```

/// info | কোডটি সহজ ভাষায়

* `response_model=Book`: ফেরত দেওয়া ডেটা `Book` হিসেবে যাচাই আর ডকুমেন্ট হবে।
* `status_code=201`: সফল হলে "তৈরি হয়েছে" কোড যাবে।
* `tags`, `summary`, `response_description`: `/docs`-এ দলের নাম, শিরোনাম আর রেসপন্সের বর্ণনা।
* `responses={409: ...}`: ডকসে দেখাবে যে `409` এররও আসতে পারে, আর তখন বডি হবে `Message`।
* `response_model_exclude_none=True`: `note` না থাকলে রেসপন্সে `"note": null` যাবে না।
* docstring-এর Markdown ডকসে বর্ণনা হিসেবে দেখাবে।

///

বিস্তারিত: [পাথ অপারেশন কনফিগারেশন](../tutorial/path-operation-configuration.md), [রেসপন্স মডেল](../tutorial/response-model.md), [রেসপন্স স্ট্যাটাস কোড](../tutorial/response-status-code.md)।

## অন্যান্য মেথড { #bn-methods }

### `include_router()` { #bn-include-router }

অন্য ফাইলে লেখা একটি `APIRouter`-এর সব রাউট অ্যাপে যুক্ত করে। এখানে `prefix`, `tags`, `dependencies`, `responses` দিলে ওই রাউটারের সব রাউটে প্রযোজ্য হয়।

```python
from fastapi import APIRouter, FastAPI

users_router = APIRouter()


@users_router.get("/")
def list_users():
    return [{"username": "rahim"}]


app = FastAPI()
app.include_router(users_router, prefix="/users", tags=["users"])
# এখন রাউটটি পাওয়া যাবে /users/ ঠিকানায়
```

বিস্তারিত: [বড় অ্যাপ্লিকেশন - একাধিক ফাইল](../tutorial/bigger-applications.md)।

### `websocket()` { #bn-websocket }

একটি WebSocket রাউট তৈরির ডেকোরেটর।

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(f"পেয়েছি: {data}")
```

বিস্তারিত: [WebSockets](../advanced/websockets.md)।

### `middleware()` { #bn-middleware-decorator }

ফাংশন দিয়ে HTTP middleware তৈরির ডেকোরেটর; একমাত্র মান `"http"`। প্রতিটি রিকোয়েস্টের আগে-পরে কাজ করে।

```python
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response
```

### `exception_handler()` { #bn-exception-handler }

একটি নির্দিষ্ট এক্সেপশন বা স্ট্যাটাস কোডের জন্য নিজের রেসপন্স ফেরত দেওয়ার হ্যান্ডলার।

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class OutOfStock(Exception):
    def __init__(self, name: str):
        self.name = name


app = FastAPI()


@app.exception_handler(OutOfStock)
async def out_of_stock_handler(request: Request, exc: OutOfStock):
    return JSONResponse(status_code=409, content={"message": f"{exc.name} স্টকে নেই"})


@app.get("/buy/{name}")
def buy(name: str):
    raise OutOfStock(name)
```

### `frontend()` { #bn-frontend }

React, Vue বা Vite-এর মতো টুলের তৈরি করা স্ট্যাটিক ফাইলের ফোল্ডার (যেমন `dist`) অ্যাপ থেকে পরিবেশন করে। আগে আপনার সাধারণ রাউটগুলো খোঁজা হয়, কিছু না মিললে তখন ফ্রন্টএন্ডের ফাইল।

* `path`: কোন URL prefix-এ ফ্রন্টএন্ড থাকবে, যেমন `"/"`।
* `directory`: build ফাইলের ফোল্ডার।
* `fallback`: ফাইল না পাওয়া গেলে কী দেবে (`"auto"`, `"index.html"`, `"404.html"`)। single page app-এর জন্য `"index.html"`।
* `check_dir`: অ্যাপ চালুর সময় ফোল্ডারটি আছে কিনা যাচাই।

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/hello")
def hello():
    return {"message": "হ্যালো"}


app.frontend("/", directory="dist")
```

বিস্তারিত: [ফ্রন্টএন্ড পরিবেশন](../tutorial/frontend.md)।

### `on_event()` { #bn-on-event }

(পুরনো, deprecated) `"startup"` বা `"shutdown"` ইভেন্টে ফাংশন চালানোর ডেকোরেটর। নতুন কোডে এর বদলে [`lifespan`](#bn-lifespan) ব্যবহার করুন।

### `openapi()` { #bn-openapi-method }

অ্যাপের OpenAPI schema একটি ডিকশনারি হিসেবে ফেরত দেয় (প্রথমবার তৈরি করে, পরে cache থেকে)। নিজের মতো schema বানাতে এটি বদলানো যায়।

```python
schema = app.openapi()
print(schema["info"]["title"])
```

বিস্তারিত: [OpenAPI বাড়ানো](../how-to/extending-openapi.md)।

## অ্যাট্রিবিউট { #bn-attributes }

| অ্যাট্রিবিউট | কী রাখে |
| --- | --- |
| `state` | অ্যাপজুড়ে ভাগ করা ডেটা রাখার জায়গা, যেমন `app.state.db = ...` |
| `dependency_overrides` | টেস্টে আসল ডিপেন্ডেন্সির বদলে নকল বসানোর ডিকশনারি |
| `openapi_version` | তৈরি হওয়া OpenAPI-র সংস্করণ (যেমন `"3.1.0"`) |
| `webhooks` | webhook ডকুমেন্ট করার `APIRouter`: `@app.webhooks.post("new-order")` |

```python
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.state.app_name = "আমার দোকান"  # অ্যাপজুড়ে ব্যবহারের জন্য


def get_user():
    return {"name": "আসল ইউজার"}


@app.get("/me")
def me(user=Depends(get_user)):
    return user


# টেস্টে আসল ডিপেন্ডেন্সির বদলে নকল
app.dependency_overrides[get_user] = lambda: {"name": "নকল ইউজার"}
client = TestClient(app)
print(client.get("/me").json())
```

বিস্তারিত: [ওভাররাইড দিয়ে ডিপেন্ডেন্সি টেস্ট](../advanced/testing-dependencies.md), [OpenAPI Webhook](../advanced/openapi-webhooks.md)।

/// check | সংক্ষেপে মনে রাখুন

* `FastAPI(...)`-এর প্যারামিটার পুরো অ্যাপে প্রযোজ্য: ডকসের তথ্য, ডকসের ঠিকানা, গ্লোবাল ডিপেন্ডেন্সি, lifespan, middleware, প্রক্সি সেটিং।
* `@app.get(...)` ইত্যাদির প্যারামিটার শুধু সেই একটি রাউটে প্রযোজ্য: `response_model`, `status_code`, `tags`, `summary` ...
* বড় অ্যাপ ভাগ করতে `include_router()`, এরর সাজাতে `exception_handler()`, টেস্টে `dependency_overrides`।

///

## পূর্ণ API তালিকা { #bn-full-api }

নিচে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ তালিকা: প্রতিটি প্যারামিটারের টাইপ (TYPE), ডিফল্ট মান (DEFAULT) আর বিস্তারিত বর্ণনা।

::: fastapi.FastAPI
    options:
        members:
            - openapi_version
            - webhooks
            - state
            - dependency_overrides
            - openapi
            - websocket
            - include_router
            - frontend
            - get
            - put
            - post
            - delete
            - options
            - head
            - patch
            - trace
            - on_event
            - middleware
            - exception_handler
