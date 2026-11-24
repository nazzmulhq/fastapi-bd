# ইনস্টল ও প্রজেক্ট সেটআপ { #sqlalchemy-setup }

/// note | এই পেজে যা শিখবেন

* SQLAlchemy, FastAPI আর ডেটাবেস ড্রাইভার ইনস্টল করা।
* শেখার জন্য SQLite, আর প্রোডাকশনের জন্য PostgreSQL কেন।
* ডেটাবেস কানেকশন URL-এর প্রতিটি অংশের মানে।
* `.env` ফাইল ও `pydantic-settings` দিয়ে কনফিগারেশন রাখা।
* ডেটাবেসের সাথে সংযোগ ঠিক আছে কি না পরীক্ষা করা, আর প্রজেক্টের ফোল্ডার কাঠামো।

///

## ১. ভার্চুয়াল এনভায়রনমেন্ট { #bn-venv }

প্রতিটি প্রজেক্টের প্যাকেজ আলাদা রাখতে একটি ভার্চুয়াল এনভায়রনমেন্ট বানিয়ে চালু করুন। বিস্তারিত পাবেন [ভার্চুয়াল এনভায়রনমেন্ট](../virtual-environments.md) পেজে।

```bash
mkdir shop && cd shop
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## ২. প্যাকেজ ইনস্টল { #bn-install }

```bash
pip install "fastapi[standard]" "sqlalchemy[asyncio]>=2.0" asyncpg aiosqlite alembic pydantic-settings
```

| প্যাকেজ | কেন লাগে |
| :--- | :--- |
| `fastapi[standard]` | FastAPI, সাথে `uvicorn` সার্ভার আর `fastapi` কমান্ড |
| `sqlalchemy[asyncio]` | SQLAlchemy 2.0, সাথে async-এর জন্য দরকারি `greenlet` |
| `asyncpg` | PostgreSQL-এর দ্রুত async ড্রাইভার |
| `aiosqlite` | SQLite-এর async ড্রাইভার (শেখা ও ছোট টেস্টের জন্য) |
| `alembic` | ডেটাবেস মাইগ্রেশন ([Alembic অধ্যায়](alembic.md)) |
| `pydantic-settings` | `.env` ফাইল আর এনভায়রনমেন্ট ভেরিয়েবল থেকে কনফিগারেশন পড়া |

ভার্সন যাচাই করুন:

```bash
python -c "import sqlalchemy, fastapi; print(sqlalchemy.__version__, fastapi.__version__)"
```

`2.0.x` বা তার পরের কোনো সংখ্যা দেখালে ঠিক আছে।

/// info | ড্রাইভার কী?

SQLAlchemy নিজে ডেটাবেসের সাথে নেটওয়ার্কে কথা বলে না। সেই কাজ করে একটি **ড্রাইভার** (DBAPI)। গাড়ি আর চালকের মতো: SQLAlchemy ঠিক করে কোথায় যেতে হবে, ড্রাইভার আসলে চালিয়ে নিয়ে যায়। async কোডের জন্য async ড্রাইভার লাগে, যেমন `asyncpg` বা `aiosqlite`।

///

## ৩. কোন ডেটাবেস ব্যবহার করবেন? { #bn-choose-db }

| | SQLite | PostgreSQL |
| :--- | :--- | :--- |
| কী | একটি ফাইলই পুরো ডেটাবেস | আলাদা ডেটাবেস সার্ভার |
| ইনস্টল | লাগে না, Python-এর সাথেই আছে | লাগে (Docker দিয়ে সহজ) |
| কখন | শেখা, ছোট টুল, দ্রুত পরীক্ষা | আসল অ্যাপ, প্রোডাকশন, একসাথে অনেক ইউজার |
| এই গাইডে | [প্রথম অ্যাপ](first-app.md) | বাকি সব অধ্যায় |

Docker থাকলে এক কমান্ডেই PostgreSQL চালু করা যায়:

```bash
docker run -d --name shop-db -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=shop \
  postgres:16
```

/// tip | পরামর্শ

প্রোডাকশনে যে ডেটাবেস ব্যবহার করবেন, ডেভেলপমেন্ট আর টেস্টেও সেটাই ব্যবহার করুন। SQLite আর PostgreSQL-এর আচরণে কিছু পার্থক্য আছে (যেমন টাইমজোন, `ILIKE`, `ON CONFLICT`, লকিং)। একই ডেটাবেসে কাজ করলে প্রোডাকশনে গিয়ে চমকে যেতে হয় না।

///

## ৪. ডেটাবেস কানেকশন URL { #bn-database-url }

SQLAlchemy একটি URL দেখে বোঝে কোন ডেটাবেসে, কোন ড্রাইভার দিয়ে, কোন ইউজার নিয়ে যুক্ত হতে হবে:

```
postgresql+asyncpg://postgres:secret@localhost:5432/shop
└───┬────┘ └──┬──┘   └──┬───┘ └─┬──┘ └───┬───┘ └┬─┘ └┬─┘
 ডেটাবেস   ড্রাইভার    ইউজার  পাসওয়ার্ড   হোস্ট   পোর্ট  ডেটাবেসের নাম
```

| ডেটাবেস ও ড্রাইভার | URL |
| :--- | :--- |
| PostgreSQL, async (`asyncpg`) | `postgresql+asyncpg://user:pass@localhost:5432/shop` |
| PostgreSQL, sync (`psycopg` 3) | `postgresql+psycopg://user:pass@localhost:5432/shop` |
| SQLite ফাইল, async | `sqlite+aiosqlite:///./shop.db` |
| SQLite মেমরিতে, async | `sqlite+aiosqlite:///:memory:` |
| MySQL / MariaDB, async | `mysql+aiomysql://user:pass@localhost:3306/shop` |

/// warning | পাসওয়ার্ডে বিশেষ চিহ্ন থাকলে

পাসওয়ার্ডে `@`, `:`, `/`, `%` বা `#` থাকলে URL ভেঙে যায়। দুটি নিরাপদ উপায় আছে:

```python
from urllib.parse import quote_plus

from sqlalchemy import URL

# উপায় ১: পাসওয়ার্ড এনকোড করা
url = f"postgresql+asyncpg://shop_user:{quote_plus('p@ss:w/rd')}@localhost:5432/shop"

# উপায় ২: URL.create — প্রতিটি অংশ আলাদা করে দেওয়া, এনকোডিংয়ের ঝামেলা নেই
url = URL.create(
    "postgresql+asyncpg",
    username="shop_user",
    password="p@ss:w/rd",
    host="localhost",
    port=5432,
    database="shop",
)
```

///

## ৫. `.env` ফাইল ও Settings { #bn-settings }

পাসওয়ার্ডসহ URL কোডে লিখে রাখা বিপজ্জনক। তাই এটি রাখুন একটি `.env` ফাইলে:

```bash
# .env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/shop
DB_ECHO=false
```

তারপর `pydantic-settings` দিয়ে পড়ুন:

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """সব কনফিগারেশন এক জায়গায়। মান আসে এনভায়রনমেন্ট ভেরিয়েবল বা .env ফাইল থেকে।"""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shop"
    DB_ECHO: bool = False          # True দিলে প্রতিটি SQL টার্মিনালে প্রিন্ট হবে
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

/// info | কোডটি সহজ ভাষায়

* `Settings` একটি Pydantic মডেল। প্রতিটি ফিল্ডের মান প্রথমে খোঁজা হয় এনভায়রনমেন্ট ভেরিয়েবলে, না পেলে `.env` ফাইলে, তাও না পেলে কোডের ডিফল্ট মান নেওয়া হয়।
* `DB_ECHO: bool`: `.env`-এ লেখা `"false"` টেক্সটকে Pydantic নিজেই `False` বানিয়ে দেয়।
* `settings = Settings()`: পুরো অ্যাপে এই একটি অবজেক্টই ইমপোর্ট করে ব্যবহার করা হবে।

আরও জানতে দেখুন [Settings ও এনভায়রনমেন্ট ভেরিয়েবল](../advanced/settings.md)।

///

/// warning | সাধারণ ভুল

`.env` ফাইল কখনো Git-এ কমিট করবেন না। `.gitignore`-এ যোগ করুন:

```
.env
.venv/
__pycache__/
```

টিমের অন্যদের জন্য পাসওয়ার্ড ছাড়া একটি `.env.example` ফাইল রাখতে পারেন।

///

## ৬. সংযোগ পরীক্ষা { #bn-check-connection }

পুরো অ্যাপ বানানোর আগে নিশ্চিত হয়ে নিন যে ডেটাবেসে যুক্ত হওয়া যাচ্ছে:

```python
# check_db.py
import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def main() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        version = await conn.scalar(text("SELECT version()"))
        print("সংযোগ সফল:", version)
    await engine.dispose()


asyncio.run(main())
```

```bash
python check_db.py
```

```
সংযোগ সফল: PostgreSQL 16.x on x86_64-pc-linux-gnu, ...
```

/// info | কোডটি সহজ ভাষায়

* `create_async_engine(...)`: ডেটাবেসের সাথে যোগাযোগের "ইঞ্জিন" বানায়। এখনো কোনো কানেকশন খোলে না।
* `async with engine.connect() as conn`: এখানে আসল কানেকশন খোলে, ব্লক শেষ হলে নিজেই ফেরত দেয়।
* `text("SELECT version()")`: সরাসরি SQL লেখার উপায়। ছোট পরীক্ষার জন্য ঠিক আছে।
* `await engine.dispose()`: স্ক্রিপ্ট শেষে সব কানেকশন বন্ধ করে।

SQLite ব্যবহার করলে `SELECT version()`-এর বদলে `SELECT sqlite_version()` লিখুন।

///

এরর এলে এই তালিকা মিলিয়ে দেখুন:

| এরর | সম্ভাব্য কারণ |
| :--- | :--- |
| `ConnectionRefusedError` | ডেটাবেস সার্ভার চালু নেই, বা হোস্ট/পোর্ট ভুল |
| `InvalidPasswordError` / `password authentication failed` | ইউজার বা পাসওয়ার্ড ভুল |
| `InvalidCatalogNameError` / `database "shop" does not exist` | ডেটাবেসটি এখনো তৈরি হয়নি |
| `ModuleNotFoundError: No module named 'asyncpg'` | ড্রাইভার ইনস্টল হয়নি |
| `The asyncio extension requires an async driver` | URL-এ `postgresql://` লিখেছেন, async-এর জন্য `postgresql+asyncpg://` লাগবে |

## ৭. প্রজেক্টের ফোল্ডার কাঠামো { #bn-project-layout }

ছোট পরীক্ষার জন্য একটি ফাইলই যথেষ্ট ([প্রথম অ্যাপ](first-app.md) দেখুন)। কিন্তু আসল প্রজেক্টে কাজগুলো আলাদা ফাইলে ভাগ করলে বোঝা ও বড় করা সহজ হয়। এই গাইডে আমরা এই কাঠামো ব্যবহার করব:

```
shop/
├── .env                      # গোপন কনফিগারেশন (Git-এ যাবে না)
├── alembic.ini               # Alembic-এর কনফিগারেশন
├── migrations/               # মাইগ্রেশন ফাইল (Alembic বানায়)
├── app/
│   ├── main.py               # FastAPI অ্যাপ তৈরি, router যোগ
│   ├── core/
│   │   ├── config.py         # Settings
│   │   └── database.py       # Base, engine, session, get_db
│   ├── models/               # SQLAlchemy মডেল (ডেটাবেসের টেবিল)
│   │   ├── __init__.py
│   │   └── order.py
│   ├── schemas/              # Pydantic স্কিমা (API-র ইনপুট/আউটপুট)
│   │   └── order.py
│   ├── crud/                 # ডেটাবেসের কাজ (repository)
│   │   ├── base.py
│   │   └── order.py
│   └── api/
│       └── v1/
│           └── orders.py     # পাথ অপারেশন (router)
└── tests/
    ├── conftest.py
    └── test_orders.py
```

/// tip | উদাহরণ দিয়ে বুঝি

একটি রেস্তোরাঁর কথা ভাবুন:

* `api/` হলো **ওয়েটার**: অতিথির (ক্লায়েন্টের) অর্ডার নেয়, খাবার পৌঁছে দেয়।
* `schemas/` হলো **মেনুকার্ড**: কী অর্ডার করা যায়, কোন রূপে খাবার আসবে।
* `crud/` হলো **রাঁধুনি**: আসল কাজটা করে।
* `models/` হলো **ভাঁড়ার ঘরের তাক**: কোন জিনিস কোথায়, কীভাবে সাজানো।
* `core/database.py` হলো **ভাঁড়ার ঘরের দরজা ও চাবি**: সবাই এখান দিয়েই ঢোকে।

প্রত্যেকে নিজের কাজ করে, তাই একটা বদলালে বাকিগুলো ভাঙে না।

///

/// note | Sync নাকি Async?

SQLAlchemy দুইভাবেই চলে। FastAPI-তে `def` এন্ডপয়েন্ট আর সাধারণ (sync) `Session` দিয়েও কাজ করা যায়, FastAPI সেগুলো আলাদা থ্রেডে চালায়। এই গাইডে আমরা **async** (`async def` + `AsyncSession`) ব্যবহার করব, কারণ:

* একটি প্রসেসেই একসাথে অনেক রিকোয়েস্ট সামলানো যায়।
* FastAPI-র বাকি async ইকোসিস্টেমের (HTTP ক্লায়েন্ট, WebSocket) সাথে মিলে যায়।

async-এর কিছু নিয়ম আছে (যেমন lazy loading চলে না), সেগুলো [Engine ও Async Session](engine-session.md) অধ্যায়ে বিস্তারিত বোঝানো হয়েছে।

///

/// check | সংক্ষেপে মনে রাখুন

* ইনস্টল: `fastapi[standard]`, `sqlalchemy[asyncio]`, একটি async ড্রাইভার (`asyncpg` / `aiosqlite`), `alembic`, `pydantic-settings`।
* URL-এর রূপ: `ডেটাবেস+ড্রাইভার://ইউজার:পাসওয়ার্ড@হোস্ট:পোর্ট/নাম`।
* পাসওয়ার্ড রাখুন `.env`-এ, পড়ুন `Settings` দিয়ে, `.env` কখনো কমিট নয়।
* কাজ ভাগ করুন: `models`, `schemas`, `crud`, `api`, `core`।

///

**পরের ধাপ:** [প্রথম অ্যাপ: ধাপে ধাপে](first-app.md)।
