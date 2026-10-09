# বড় অ্যাপ্লিকেশন - একাধিক ফাইল { #bigger-applications-multiple-files }

/// note | এই পেজে যা শিখবেন

* একটি বড় অ্যাপকে কীভাবে একাধিক ফাইল ও ফোল্ডারে সাজাবেন।
* Python প্যাকেজ, মডিউল আর `__init__.py` কী।
* `APIRouter` দিয়ে প্রতিটি অংশের পাথ অপারেশন আলাদা ফাইলে রাখা।
* রিলেটিভ ইমপোর্ট (`.`, `..`) কীভাবে কাজ করে।
* রাউটারে একসাথে `prefix`, `tags`, `dependencies` দেওয়া আর মূল অ্যাপে সব জুড়ে দেওয়া।

///

একটি অ্যাপ্লিকেশন বা ওয়েব API বানানোর সময় সবকিছু একটিমাত্র ফাইলে রাখা খুব কমই সম্ভব হয়।

**FastAPI** সব নমনীয়তা বজায় রেখে আপনার অ্যাপ্লিকেশন সাজানোর একটি সুবিধাজনক টুল দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

একটি বড় দোকানের কথা ভাবুন। সব জিনিস একটি ঘরে স্তূপ করে রাখলে খুঁজে পাওয়া কঠিন। তাই আলাদা আলাদা বিভাগ: পোশাক, ইলেকট্রনিক্স, খাবার। প্রতিটি বিভাগের নিজস্ব কর্মী, কিন্তু সবাই একই দোকানের অংশ। `APIRouter` হলো একেকটি বিভাগ, আর মূল `FastAPI` অ্যাপ হলো পুরো দোকান।

///

/// note | নোট

আপনি যদি Flask থেকে আসেন, তাহলে এটি Flask-এর Blueprints-এর সমতুল্য।

///

## একটি উদাহরণ ফাইল কাঠামো { #an-example-file-structure }

ধরা যাক আপনার ফাইল কাঠামো এমন:

```
.
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   └── routers
│   │   ├── __init__.py
│   │   ├── items.py
│   │   └── users.py
│   └── internal
│       ├── __init__.py
│       └── admin.py
```

/// tip | পরামর্শ

কয়েকটি `__init__.py` ফাইল আছে: প্রতিটি ফোল্ডার বা সাব-ফোল্ডারে একটি করে।

এটাই এক ফাইল থেকে আরেক ফাইলে কোড ইমপোর্ট করতে দেয়। (ফাইলটি খালিও হতে পারে, এর উপস্থিতিই Python-কে বলে "এই ফোল্ডারটি একটি প্যাকেজ"।)

যেমন, `app/main.py`-তে এরকম একটি লাইন থাকতে পারে:

```
from app.routers import items
```

///

* `app` ফোল্ডারে সবকিছু আছে। আর এতে একটি খালি ফাইল `app/__init__.py` আছে, তাই এটি একটি "Python প্যাকেজ" ("Python মডিউলের" একটি সংগ্রহ): `app`।
* এতে একটি `app/main.py` ফাইল আছে। যেহেতু এটি একটি Python প্যাকেজের (একটি `__init__.py` ফাইলসহ ফোল্ডার) ভেতরে, তাই এটি ওই প্যাকেজের একটি "মডিউল": `app.main`।
* একটি `app/dependencies.py` ফাইলও আছে, ঠিক `app/main.py`-এর মতোই এটি একটি "মডিউল": `app.dependencies`।
* আরেকটি `__init__.py` ফাইলসহ একটি সাব-ফোল্ডার `app/routers/` আছে, তাই এটি একটি "Python সাব-প্যাকেজ": `app.routers`।
* `app/routers/items.py` ফাইলটি একটি প্যাকেজের ভেতরে, `app/routers/`, তাই এটি একটি সাব-মডিউল: `app.routers.items`।
* `app/routers/users.py`-ও তাই, এটি আরেকটি সাব-মডিউল: `app.routers.users`।
* আরেকটি `__init__.py` ফাইলসহ একটি সাব-ফোল্ডার `app/internal/`-ও আছে, তাই এটি আরেকটি "Python সাব-প্যাকেজ": `app.internal`।
* আর `app/internal/admin.py` ফাইলটি আরেকটি সাব-মডিউল: `app.internal.admin`।

<img src="/img/tutorial/bigger-applications/package.drawio.svg">

মন্তব্যসহ একই ফাইল কাঠামো:

```bash
.
├── app                  # "app" একটি Python প্যাকেজ
│   ├── __init__.py      # এই ফাইলটি "app"-কে একটি "Python প্যাকেজ" বানায়
│   ├── main.py          # "main" মডিউল, যেমন import app.main
│   ├── dependencies.py  # "dependencies" মডিউল, যেমন import app.dependencies
│   └── routers          # "routers" একটি "Python সাব-প্যাকেজ"
│   │   ├── __init__.py  # "routers"-কে একটি "Python সাব-প্যাকেজ" বানায়
│   │   ├── items.py     # "items" সাব-মডিউল, যেমন import app.routers.items
│   │   └── users.py     # "users" সাব-মডিউল, যেমন import app.routers.users
│   └── internal         # "internal" একটি "Python সাব-প্যাকেজ"
│       ├── __init__.py  # "internal"-কে একটি "Python সাব-প্যাকেজ" বানায়
│       └── admin.py     # "admin" সাব-মডিউল, যেমন import app.internal.admin
```

## `APIRouter` { #apirouter }

ধরা যাক শুধু ইউজার সামলানোর জন্য নির্দিষ্ট ফাইলটি হলো `/app/routers/users.py`-এর সাব-মডিউল।

আপনি চান আপনার ইউজার-সংক্রান্ত *পাথ অপারেশনগুলো* বাকি কোড থেকে আলাদা থাকুক, যাতে সব গোছানো থাকে।

কিন্তু এটি তখনও একই **FastAPI** অ্যাপ্লিকেশন/ওয়েব API-এর অংশ (একই "Python প্যাকেজের" অংশ)।

`APIRouter` ব্যবহার করে ওই মডিউলের জন্য *পাথ অপারেশন* তৈরি করতে পারেন।

### `APIRouter` ইমপোর্ট করুন { #import-apirouter }

এটি ইমপোর্ট করে একটি "ইনস্ট্যান্স" তৈরি করুন, ঠিক `FastAPI` ক্লাসের মতো:

{* ../../docs_src/bigger_applications/app_an_py310/routers/users.py hl[1,3] title["app/routers/users.py"] *}

### `APIRouter` দিয়ে *পাথ অপারেশন* { #path-operations-with-apirouter }

তারপর এটি দিয়ে আপনার *পাথ অপারেশনগুলো* ঘোষণা করুন।

`FastAPI` ক্লাস যেভাবে ব্যবহার করতেন সেভাবেই এটি ব্যবহার করুন:

{* ../../docs_src/bigger_applications/app_an_py310/routers/users.py hl[6,11,16] title["app/routers/users.py"] *}

`APIRouter`-কে একটি "ছোট `FastAPI`" ক্লাস হিসেবে ভাবতে পারেন।

সব একই অপশন সাপোর্টেড।

সব একই `parameters`, `responses`, `dependencies`, `tags` ইত্যাদি।

শুধু পার্থক্য হলো `@app.get(...)`-এর বদলে `@router.get(...)` লেখেন।

/// tip | পরামর্শ

এই উদাহরণে ভেরিয়েবলের নাম `router`, তবে আপনি যেকোনো নাম দিতে পারেন।

///

আমরা এই `APIRouter`-টি মূল `FastAPI` অ্যাপে অন্তর্ভুক্ত করব, তবে তার আগে ডিপেন্ডেন্সি আর আরেকটি `APIRouter` দেখে নেওয়া যাক।

## ডিপেন্ডেন্সি { #dependencies }

আমরা দেখছি যে অ্যাপ্লিকেশনের বেশ কয়েক জায়গায় ব্যবহৃত কিছু ডিপেন্ডেন্সি লাগবে।

তাই সেগুলো তাদের নিজস্ব `dependencies` মডিউলে (`app/dependencies.py`) রাখি।

এবার একটি কাস্টম `X-Token` হেডার পড়তে একটি সহজ ডিপেন্ডেন্সি ব্যবহার করব:

{* ../../docs_src/bigger_applications/app_an_py310/dependencies.py hl[3,6:8] title["app/dependencies.py"] *}

/// tip | পরামর্শ

এই উদাহরণ সহজ রাখতে আমরা একটি বানানো হেডার ব্যবহার করছি।

কিন্তু বাস্তবে একীভূত [সিকিউরিটি টুলগুলো](security/index.md) ব্যবহার করলে ভালো ফল পাবেন।

///

## `APIRouter`-সহ আরেকটি মডিউল { #another-module-with-apirouter }

ধরা যাক আপনার অ্যাপ্লিকেশনের "আইটেম" সামলানোর জন্য নির্দিষ্ট এন্ডপয়েন্টগুলোও আছে `app/routers/items.py` মডিউলে।

আপনার *পাথ অপারেশন* আছে এগুলোর জন্য:

* `/items/`
* `/items/{item_id}`

গঠন `app/routers/users.py`-এর মতোই।

কিন্তু আমরা আরও বুদ্ধিমান হয়ে কোডটা একটু সহজ করতে চাই।

আমরা জানি এই মডিউলের সব *পাথ অপারেশনে* একই:

* পাথের `prefix` (শুরুর অংশ): `/items`।
* `tags`: (শুধু একটি ট্যাগ: `items`)।
* বাড়তি `responses`।
* `dependencies`: সবারই আমাদের তৈরি করা সেই `X-Token` ডিপেন্ডেন্সি লাগবে।

তাই প্রতিটি *পাথ অপারেশনে* এসব যোগ না করে, এগুলো `APIRouter`-এ যোগ করতে পারি।

{* ../../docs_src/bigger_applications/app_an_py310/routers/items.py hl[5:10,16,21] title["app/routers/items.py"] *}

যেহেতু প্রতিটি *পাথ অপারেশনের* পাথ `/` দিয়ে শুরু হতে হবে, এভাবে:

```Python hl_lines="1"
@router.get("/{item_id}")
async def read_item(item_id: str):
    ...
```

...তাই prefix-এর শেষে `/` থাকা চলবে না।

তাই এই ক্ষেত্রে prefix হলো `/items`।

এই রাউটারে অন্তর্ভুক্ত সব *পাথ অপারেশনে* প্রযোজ্য হবে এমন `tags`-এর তালিকা আর বাড়তি `responses`-ও যোগ করতে পারি।

আর `dependencies`-এর একটি তালিকা যোগ করতে পারি, যা রাউটারের সব *পাথ অপারেশনে* যোগ হবে, আর সেগুলোতে করা প্রতিটি রিকোয়েস্টে চলবে/সমাধান হবে।

/// tip | পরামর্শ

খেয়াল করুন, অনেকটা [*পাথ অপারেশন ডেকোরেটরে* ডিপেন্ডেন্সির](dependencies/dependencies-in-path-operation-decorators.md) মতোই, আপনার *পাথ অপারেশন ফাংশনে* কোনো মান পাঠানো হবে না।

///

শেষ ফলাফল হলো, আইটেমের পাথগুলো এখন:

* `/items/`
* `/items/{item_id}`

...যেমনটা আমরা চেয়েছিলাম।

* এগুলো একটিমাত্র স্ট্রিং `"items"`-সহ ট্যাগের তালিকা দিয়ে চিহ্নিত থাকবে।
    * এই "ট্যাগগুলো" বিশেষভাবে স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ ডকুমেন্টেশন সিস্টেমের (OpenAPI ব্যবহার করে) জন্য কাজের।
* এদের সবার মধ্যে আগে থেকে নির্ধারিত `responses` থাকবে।
* এই সব *পাথ অপারেশনের* আগে `dependencies`-এর তালিকাটি মূল্যায়ন/চালানো হবে।
    * আপনি যদি কোনো নির্দিষ্ট *পাথ অপারেশনেও* ডিপেন্ডেন্সি ঘোষণা করেন, **সেগুলোও চলবে**।
    * প্রথমে রাউটারের ডিপেন্ডেন্সি চলে, তারপর [ডেকোরেটরের `dependencies`](dependencies/dependencies-in-path-operation-decorators.md), তারপর সাধারণ প্যারামিটারের ডিপেন্ডেন্সি।
    * আপনি [`scopes`-সহ `Security` ডিপেন্ডেন্সিও](../advanced/security/oauth2-scopes.md) যোগ করতে পারেন।

/// tip | পরামর্শ

`APIRouter`-এ `dependencies` রাখা, যেমন, পুরো একদল *পাথ অপারেশনের* জন্য অথেনটিকেশন বাধ্যতামূলক করতে ব্যবহার করা যায়। ডিপেন্ডেন্সিগুলো প্রতিটিতে আলাদাভাবে যোগ না করলেও।

///

/// tip | পরামর্শ

`prefix`, `tags`, `responses` আর `dependencies` প্যারামিটারগুলো (অন্য অনেক ক্ষেত্রের মতোই) শুধু **FastAPI**-এর একটি সুবিধা, যাতে আপনি কোডের পুনরাবৃত্তি এড়াতে পারেন।

///

### ডিপেন্ডেন্সিগুলো ইমপোর্ট করুন { #import-the-dependencies }

এই কোডটি আছে `app.routers.items` মডিউলে, `app/routers/items.py` ফাইলে।

আর আমাদের ডিপেন্ডেন্সি ফাংশনটি আনতে হবে `app.dependencies` মডিউল থেকে, `app/dependencies.py` ফাইল থেকে।

তাই ডিপেন্ডেন্সির জন্য `..` দিয়ে একটি রিলেটিভ ইমপোর্ট ব্যবহার করি:

{* ../../docs_src/bigger_applications/app_an_py310/routers/items.py hl[3] title["app/routers/items.py"] *}

#### রিলেটিভ ইমপোর্ট কীভাবে কাজ করে { #how-relative-imports-work }

/// tip | পরামর্শ

ইমপোর্ট কীভাবে কাজ করে তা যদি পুরোপুরি জানেন, তাহলে নিচের পরের অংশে চলে যান।

///

একটি ডট `.`, যেমন:

```Python
from .dependencies import get_token_header
```

এর মানে হবে:

* এই মডিউলটি (`app/routers/items.py` ফাইল) যে প্যাকেজে আছে (`app/routers/` ফোল্ডার), সেখান থেকে শুরু করে...
* `dependencies` মডিউলটি খুঁজুন (`app/routers/dependencies.py`-এ একটি কাল্পনিক ফাইল)...
* আর সেখান থেকে `get_token_header` ফাংশনটি ইমপোর্ট করুন।

কিন্তু ওই ফাইলটি নেই, আমাদের ডিপেন্ডেন্সিগুলো আছে `app/dependencies.py` ফাইলে।

মনে করুন আমাদের অ্যাপ/ফাইল কাঠামো দেখতে কেমন:

<img src="/img/tutorial/bigger-applications/package.drawio.svg">

---

দুটি ডট `..`, যেমন:

```Python
from ..dependencies import get_token_header
```

এর মানে:

* এই মডিউলটি (`app/routers/items.py` ফাইল) যে প্যাকেজে আছে (`app/routers/` ফোল্ডার), সেখান থেকে শুরু করে...
* প্যারেন্ট (মূল) প্যাকেজে যান (`app/` ফোল্ডার)...
* আর সেখানে `dependencies` মডিউলটি খুঁজুন (`app/dependencies.py`-এর ফাইল)...
* আর সেখান থেকে `get_token_header` ফাংশনটি ইমপোর্ট করুন।

এটি ঠিকঠাক কাজ করে! 🎉

---

একইভাবে, যদি তিনটি ডট `...` ব্যবহার করতাম, যেমন:

```Python
from ...dependencies import get_token_header
```

তার মানে হতো:

* এই মডিউলটি (`app/routers/items.py` ফাইল) যে প্যাকেজে আছে (`app/routers/` ফোল্ডার), সেখান থেকে শুরু করে...
* প্যারেন্ট প্যাকেজে যান (`app/` ফোল্ডার)...
* তারপর সেই প্যাকেজের প্যারেন্টে যান (কোনো প্যারেন্ট প্যাকেজ নেই, `app` সবচেয়ে ওপরের স্তর 😱)...
* আর সেখানে `dependencies` মডিউলটি খুঁজুন (`app/dependencies.py`-এর ফাইল)...
* আর সেখান থেকে `get_token_header` ফাংশনটি ইমপোর্ট করুন।

এটি `app/`-এর ওপরের কোনো প্যাকেজকে বোঝাত, যার নিজস্ব `__init__.py` ফাইল ইত্যাদি আছে। কিন্তু আমাদের তা নেই। তাই আমাদের উদাহরণে এটি একটি এরর দিত। 🚨

/// tip | মনে রাখার সহজ উপায়

ফাইল এক্সপ্লোরারে ফোল্ডারে চলাফেরার মতো: `.` মানে "এই ফোল্ডার", `..` মানে "এক ধাপ ওপরের ফোল্ডার", `...` মানে "দুই ধাপ ওপরের ফোল্ডার"।

///

কিন্তু এখন আপনি জানেন এটি কীভাবে কাজ করে, তাই আপনার অ্যাপ যত জটিলই হোক, নিজের অ্যাপে রিলেটিভ ইমপোর্ট ব্যবহার করতে পারবেন। 🤓

### কিছু কাস্টম `tags`, `responses` আর `dependencies` যোগ করুন { #add-some-custom-tags-responses-and-dependencies }

আমরা প্রতিটি *পাথ অপারেশনে* prefix `/items` বা `tags=["items"]` যোগ করছি না, কারণ এগুলো `APIRouter`-এ যোগ করেছি।

কিন্তু তবুও একটি নির্দিষ্ট *পাথ অপারেশনে* প্রযোজ্য _আরও_ `tags` যোগ করতে পারি, আর ওই *পাথ অপারেশনের* জন্য নির্দিষ্ট কিছু বাড়তি `responses`-ও:

{* ../../docs_src/bigger_applications/app_an_py310/routers/items.py hl[30:31] title["app/routers/items.py"] *}

/// tip | পরামর্শ

এই শেষ পাথ অপারেশনটিতে ট্যাগের সমন্বয় থাকবে: `["items", "custom"]`।

আর ডকুমেন্টেশনে দুটো রেসপন্সই থাকবে, একটি `404`-এর জন্য আর একটি `403`-এর জন্য।

///

## মূল `FastAPI` { #the-main-fastapi }

এবার `app/main.py`-এর মডিউলটি দেখা যাক।

এখানেই আপনি `FastAPI` ক্লাস ইমপোর্ট করে ব্যবহার করবেন।

এটি হবে আপনার অ্যাপ্লিকেশনের মূল ফাইল, যা সবকিছু একসাথে জোড়া লাগায়।

আর যেহেতু আপনার বেশিরভাগ লজিক এখন নিজ নিজ নির্দিষ্ট মডিউলে থাকবে, তাই মূল ফাইলটি বেশ সহজ হবে।

### `FastAPI` ইমপোর্ট করুন { #import-fastapi }

স্বাভাবিকভাবেই একটি `FastAPI` ক্লাস ইমপোর্ট করে তৈরি করুন।

আর আমরা এমনকি [গ্লোবাল ডিপেন্ডেন্সিও](dependencies/global-dependencies.md) ঘোষণা করতে পারি, যা প্রতিটি `APIRouter`-এর ডিপেন্ডেন্সির সাথে মিলিত হবে:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[1,3,7] title["app/main.py"] *}

### `APIRouter` ইমপোর্ট করুন { #import-the-apirouter }

এবার `APIRouter`-ওয়ালা অন্য সাব-মডিউলগুলো ইমপোর্ট করি:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[4:5] title["app/main.py"] *}

যেহেতু `app/routers/users.py` আর `app/routers/items.py` ফাইলগুলো একই Python প্যাকেজ `app`-এর অংশ সাব-মডিউল, তাই "রিলেটিভ ইমপোর্ট" দিয়ে এগুলো ইমপোর্ট করতে একটি ডট `.` ব্যবহার করতে পারি।

### ইমপোর্ট কীভাবে কাজ করে { #how-the-importing-works }

এই অংশটি:

```Python
from .routers import items, users
```

মানে:

* এই মডিউলটি (`app/main.py` ফাইল) যে প্যাকেজে আছে (`app/` ফোল্ডার), সেখান থেকে শুরু করে...
* `routers` সাব-প্যাকেজটি খুঁজুন (`app/routers/`-এর ফোল্ডার)...
* আর সেখান থেকে `items` সাব-মডিউল (`app/routers/items.py`-এর ফাইল) আর `users` (`app/routers/users.py`-এর ফাইল) ইমপোর্ট করুন...

`items` মডিউলে একটি ভেরিয়েবল `router` থাকবে (`items.router`)। এটি সেটিই যা আমরা `app/routers/items.py` ফাইলে তৈরি করেছিলাম, এটি একটি `APIRouter` অবজেক্ট।

তারপর `users` মডিউলের জন্যও একই কাজ করি।

এভাবেও ইমপোর্ট করতে পারতাম:

```Python
from app.routers import items, users
```

/// note | নোট

প্রথম সংস্করণটি একটি "রিলেটিভ ইমপোর্ট" (বর্তমান অবস্থানের তুলনায়):

```Python
from .routers import items, users
```

দ্বিতীয় সংস্করণটি একটি "অ্যাবসোলিউট ইমপোর্ট" (প্রজেক্টের মূল থেকে পুরো ঠিকানা):

```Python
from app.routers import items, users
```

Python প্যাকেজ আর মডিউল সম্পর্কে আরও জানতে [মডিউল নিয়ে অফিসিয়াল Python ডকুমেন্টেশন](https://docs.python.org/3/tutorial/modules.html) পড়ুন।

///

### নামের সংঘর্ষ এড়ান { #avoid-name-collisions }

আমরা শুধু এর `router` ভেরিয়েবলটি ইমপোর্ট না করে সরাসরি `items` সাব-মডিউলটি ইমপোর্ট করছি।

এর কারণ, `users` সাব-মডিউলেও `router` নামে আরেকটি ভেরিয়েবল আছে।

যদি একটির পর একটি ইমপোর্ট করতাম, এভাবে:

```Python
from .routers.items import router
from .routers.users import router
```

তাহলে `users`-এর `router` `items`-এরটিকে মুছে দিত (ওভাররাইট করত), আর আমরা দুটো একসাথে ব্যবহার করতে পারতাম না।

তাই একই ফাইলে দুটোই ব্যবহার করতে আমরা সরাসরি সাব-মডিউলগুলো ইমপোর্ট করি:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[5] title["app/main.py"] *}

### `users` আর `items`-এর `APIRouter` অন্তর্ভুক্ত করুন { #include-the-apirouters-for-users-and-items }

এবার `users` আর `items` সাব-মডিউলের `router`-গুলো অন্তর্ভুক্ত করি:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[10:11] title["app/main.py"] *}

/// note | নোট

`users.router`-এ আছে `app/routers/users.py` ফাইলের ভেতরের `APIRouter`।

আর `items.router`-এ আছে `app/routers/items.py` ফাইলের ভেতরের `APIRouter`।

///

`app.include_router()` দিয়ে প্রতিটি `APIRouter` মূল `FastAPI` অ্যাপ্লিকেশনে যোগ করতে পারি।

এটি ওই রাউটারের সব রাউট নিজের অংশ হিসেবে অন্তর্ভুক্ত করবে।

/// note | কারিগরি বিবরণ

রাউটারটি মূল অ্যাপ্লিকেশনে অন্তর্ভুক্ত হলে FastAPI মূল `APIRouter` আর এর `APIRoute`-গুলো সক্রিয় রাখে।

এর মানে রাউটার অন্তর্ভুক্ত হওয়ার পরেও কাস্টম `APIRouter` আর `APIRoute` সাব-ক্লাসগুলো অংশ নিতে পারে।

///

/// tip | পরামর্শ

রাউটার অন্তর্ভুক্ত করার সময় পারফরম্যান্স নিয়ে চিন্তা করতে হবে না।

এটি হালকা হওয়ার জন্য আর প্রতিটি রিকোয়েস্টে বাড়তি বোঝা যোগ না করার জন্য ডিজাইন করা।

তাই এটি পারফরম্যান্সে প্রভাব ফেলবে না। ⚡

///

### কাস্টম `prefix`, `tags`, `responses` আর `dependencies`-সহ একটি `APIRouter` অন্তর্ভুক্ত করুন { #include-an-apirouter-with-a-custom-prefix-tags-responses-and-dependencies }

এবার কল্পনা করুন, আপনার প্রতিষ্ঠান আপনাকে `app/internal/admin.py` ফাইলটি দিয়েছে।

এতে কিছু অ্যাডমিন *পাথ অপারেশনসহ* একটি `APIRouter` আছে, যা আপনার প্রতিষ্ঠান কয়েকটি প্রজেক্টের মধ্যে ভাগাভাগি করে।

এই উদাহরণে এটি খুবই সহজ। কিন্তু ধরা যাক, যেহেতু এটি প্রতিষ্ঠানের অন্য প্রজেক্টগুলোর সাথে ভাগাভাগি করা, তাই আমরা এটি পরিবর্তন করে সরাসরি `APIRouter`-এ একটি `prefix`, `dependencies`, `tags` ইত্যাদি যোগ করতে পারব না:

{* ../../docs_src/bigger_applications/app_an_py310/internal/admin.py hl[3] title["app/internal/admin.py"] *}

কিন্তু তবুও `APIRouter` অন্তর্ভুক্ত করার সময় একটি কাস্টম `prefix` সেট করতে চাই, যাতে এর সব *পাথ অপারেশন* `/admin` দিয়ে শুরু হয়, এই প্রজেক্টে আমাদের যে `dependencies` আছে সেগুলো দিয়ে এটি সুরক্ষিত করতে চাই, আর `tags` ও `responses` যোগ করতে চাই।

মূল `APIRouter` পরিবর্তন না করেই, ওই প্যারামিটারগুলো `app.include_router()`-এ দিয়ে এসব ঘোষণা করতে পারি:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[14:17] title["app/main.py"] *}

এভাবে মূল `APIRouter` অপরিবর্তিত থাকবে, তাই প্রতিষ্ঠানের অন্য প্রজেক্টগুলোর সাথে এখনো সেই একই `app/internal/admin.py` ফাইল ভাগাভাগি করতে পারব।

ফলাফল হলো, আমাদের অ্যাপে `admin` মডিউলের প্রতিটি *পাথ অপারেশনে* থাকবে:

* prefix `/admin`।
* ট্যাগ `admin`।
* ডিপেন্ডেন্সি `get_token_header`।
* রেসপন্স `418`। 🍵

কিন্তু এটি শুধু আমাদের অ্যাপের সেই `APIRouter`-কে প্রভাবিত করবে, এটি ব্যবহার করা অন্য কোনো কোডকে নয়।

তাই যেমন, অন্য প্রজেক্টগুলো একই `APIRouter` ভিন্ন অথেনটিকেশন পদ্ধতিতে ব্যবহার করতে পারে।

### একটি *পাথ অপারেশন* অন্তর্ভুক্ত করুন { #include-a-path-operation }

সরাসরি `FastAPI` অ্যাপেও *পাথ অপারেশন* যোগ করতে পারি।

এখানে আমরা সেটা করছি... শুধু দেখানোর জন্য যে পারি 🤷:

{* ../../docs_src/bigger_applications/app_an_py310/main.py hl[21:23] title["app/main.py"] *}

আর এটি `app.include_router()` দিয়ে যোগ করা অন্য সব *পাথ অপারেশনের* সাথে মিলে সঠিকভাবে কাজ করবে।

/// info | পুরো `main.py` সহজ ভাষায়

* লাইন ৭: পুরো অ্যাপে গ্লোবাল ডিপেন্ডেন্সি `get_query_token`, তাই প্রতিটি রিকোয়েস্টে `?token=jessica` লাগবে।
* লাইন ১০-১১: `users` আর `items` রাউটার যোগ।
* লাইন ১২-১৮: `admin` রাউটার যোগ, `/admin` prefix, `admin` ট্যাগ, `X-Token` যাচাই আর ৪১৮ রেসপন্সসহ।
* লাইন ২১-২৩: মূল অ্যাপে সরাসরি একটি `/` পাথ।

তাই `/items/` পেতে লাগবে `?token=jessica` (গ্লোবাল) আর `X-Token` হেডার (items রাউটারের)।

///

/// note | একেবারে গভীর কারিগরি বিবরণ

**নোট**: এটি খুবই কারিগরি একটি বিষয়, যা আপনি সম্ভবত **বাদ দিতে পারেন**।

---

`APIRouter`-গুলো "mount" করা হয় না, এরা অ্যাপ্লিকেশনের বাকি অংশ থেকে বিচ্ছিন্ন নয়।

কারণ আমরা চাই এদের *পাথ অপারেশনগুলো* OpenAPI স্কিমা আর ইউজার ইন্টারফেসে অন্তর্ভুক্ত হোক।

FastAPI মূল রাউটার আর পাথ অপারেশনগুলো সক্রিয় রাখে, আর রিকোয়েস্ট সামলানো ও OpenAPI তৈরির সময় রাউটারের prefix, ডিপেন্ডেন্সি, ট্যাগ, রেসপন্স আর অন্যান্য মেটাডেটা একত্র করে।

///

## `pyproject.toml`-এ `entrypoint` কনফিগার করুন { #configure-the-entrypoint-in-pyproject-toml }

যেহেতু আপনার FastAPI `app` অবজেক্টটি `app/main.py`-তে আছে, তাই আপনার `pyproject.toml` ফাইলে `entrypoint` এভাবে কনফিগার করতে পারেন:

```toml
[tool.fastapi]
entrypoint = "app.main:app"
```

যা এভাবে ইমপোর্ট করার সমতুল্য:

```python
from app.main import app
```

এভাবে `fastapi` কমান্ড জানবে আপনার অ্যাপ কোথায় খুঁজতে হবে।

/// Note | নোট

কমান্ডে পাথও দিতে পারতেন, এভাবে:

```console
$ uv run fastapi dev app/main.py
```

কিন্তু তাহলে প্রতিবার `fastapi` কমান্ড চালানোর সময় সঠিক পাথ দিতে মনে রাখতে হবে।

তাছাড়া অন্য টুলগুলো হয়তো এটি খুঁজে পাবে না, যেমন [VS Code এক্সটেনশন](../editor-support.md) বা [FastAPI Cloud](https://fastapicloud.com), তাই `pyproject.toml`-এ `entrypoint` ব্যবহার করার সুপারিশ করা হয়।

///

## স্বয়ংক্রিয় API ডকুমেন্টেশন দেখুন { #check-the-automatic-api-docs }

এবার আপনার অ্যাপ চালান:

<div class="termy">

```console
$ uv run fastapi dev

<span style="color: green;">INFO</span>:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</div>

আর [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ ডকুমেন্টেশন খুলুন।

আপনি স্বয়ংক্রিয় API ডকুমেন্টেশন দেখবেন, যাতে সব সাব-মডিউলের পাথ আছে, সঠিক পাথ (আর prefix) আর সঠিক ট্যাগসহ:

<img src="/img/tutorial/bigger-applications/image01.png">

## একই রাউটার ভিন্ন `prefix` দিয়ে একাধিকবার অন্তর্ভুক্ত করুন { #include-the-same-router-multiple-times-with-different-prefix }

ভিন্ন ভিন্ন prefix ব্যবহার করে *একই* রাউটারের সাথে `.include_router()` একাধিকবার ব্যবহার করতে পারেন।

এটি কাজে লাগতে পারে, যেমন একই API ভিন্ন prefix-এর অধীনে দেখাতে, যেমন `/api/v1` আর `/api/latest`।

এটি একটি উন্নত ব্যবহার, যা হয়তো আসলে আপনার দরকার হবে না, তবে দরকার হলে আছে।

## একটি `APIRouter` আরেকটিতে অন্তর্ভুক্ত করুন { #include-an-apirouter-in-another }

যেভাবে একটি `FastAPI` অ্যাপ্লিকেশনে একটি `APIRouter` অন্তর্ভুক্ত করা যায়, সেভাবেই একটি `APIRouter` আরেকটি `APIRouter`-এ অন্তর্ভুক্ত করতে পারেন, এভাবে:

```Python
router.include_router(other_router)
```

`router`-কে `FastAPI` অ্যাপে অন্তর্ভুক্ত করার আগে বা পরে এটি করতে পারেন। FastAPI তবুও রাউটিং আর OpenAPI-তে `other_router`-এর *পাথ অপারেশনগুলো* অন্তর্ভুক্ত করবে।

রাউটারগুলোতে পরে যোগ করা *পাথ অপারেশনের* ক্ষেত্রেও একই কথা। আগের অন্তর্ভুক্তির মাধ্যমেও সেগুলো দেখা যাবে।

/// warning | কারিগরি বিবরণ

একটি রাউটার অন্তর্ভুক্ত করার পরে সরাসরি `router.routes` পরিবর্তন করা এড়িয়ে চলুন। FastAPI রাউটার অন্তর্ভুক্তিকে "সজীব" হিসেবে ধরে, তাই মূল রাউটার আর এর রাউটগুলো রাউটিং আর OpenAPI তৈরির অংশ থাকে।

রাউট আর রাউটার যোগ করতে পাথ অপারেশন ডেকোরেটর আর `.include_router()`-এর মতো ডকুমেন্টেড API ব্যবহার করুন।

`router.routes`-কে একটি নিম্ন-স্তরের রাউট-গাছ হিসেবে ধরুন, যাতে রাউটের সংজ্ঞা আর অন্তর্ভুক্ত রাউটার থাকতে পারে, আর একে চূড়ান্ত পাথ অপারেশনের একটি সমতল তালিকা হিসেবে ভরসা করবেন না।

///

/// check | সংক্ষেপে মনে রাখুন

* প্রতিটি অংশের জন্য আলাদা ফাইলে `router = APIRouter()` বানিয়ে `@router.get(...)` দিয়ে পাথ অপারেশন লিখুন।
* রাউটারে একবারে `prefix`, `tags`, `dependencies`, `responses` দিন।
* `main.py`-তে `app.include_router(items.router)` দিয়ে জুড়ুন। বাইরের রাউটার না বদলে `include_router(...)`-এই prefix ইত্যাদি দেওয়া যায়।
* ফোল্ডারে `__init__.py` রাখুন, ইমপোর্টে `.` (এই প্যাকেজ) আর `..` (ওপরের প্যাকেজ)।
* `pyproject.toml`-এ `entrypoint = "app.main:app"`।

///
