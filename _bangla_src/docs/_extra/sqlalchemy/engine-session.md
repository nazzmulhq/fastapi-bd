# Engine, Connection Pool ও Async Session { #sqlalchemy-engine-session }

/// note | এই পেজে যা শিখবেন

* `Engine` আর কানেকশন পুল ভেতরে কীভাবে কাজ করে, আর `pool_size`, `max_overflow`-এর মতো সেটিং কীভাবে ঠিক করবেন।
* প্রোডাকশনের উপযোগী async engine ও `async_sessionmaker`।
* async SQLAlchemy ভেতরে কীভাবে চলে (greenlet), আর `MissingGreenlet` এরর কেন আসে ও কীভাবে সারাবেন।
* FastAPI-তে প্রতি রিকোয়েস্টে একটি সেশন দেওয়ার ডিপেন্ডেন্সি।

///

/// tip | উদাহরণ দিয়ে বুঝি

ডেটাবেসের সাথে নতুন কানেকশন খোলা অনেকটা নতুন ট্যাক্সি ডেকে আনার মতো: সময় লাগে। **কানেকশন পুল** হলো একটি **ট্যাক্সি স্ট্যান্ড**। কয়েকটি ট্যাক্সি (কানেকশন) সবসময় দাঁড়িয়ে থাকে। একটি রিকোয়েস্ট এলে স্ট্যান্ড থেকে একটি নেয়, কাজ শেষে ফেরত দেয়, পরের রিকোয়েস্ট সেটাই আবার ব্যবহার করে।

* `pool_size`: স্ট্যান্ডে সবসময় কয়টি ট্যাক্সি থাকবে।
* `max_overflow`: ভিড়ের সময় সাময়িকভাবে আর কয়টি বাড়তি ট্যাক্সি ডাকা যাবে।
* `pool_timeout`: সব ট্যাক্সি ব্যস্ত থাকলে যাত্রী কতক্ষণ অপেক্ষা করবে, তারপর হাল ছেড়ে দেবে।

///

## 19. Engine ও Connection Pool-এর ভেতরের কাজ { #s19 }

`Engine` ফিজিক্যাল DB কানেকশনের একটি **pool** পরিচালনা করে এবং SQL কম্পাইলেশনের দায়িত্ব একটি **dialect**-কে দেয়। Async অ্যাপে (FastAPI + `asyncpg`) পুল কনফিগারেশন সরাসরি থ্রুপুট, লোডের সময়ের লেটেন্সি এবং ডেটাবেসের স্বাস্থ্য নির্ধারণ করে।

```
+-------------------------------------------------------------------------+
|                              FastAPI App                                |
|  [Worker 1]      [Worker 2]      [Worker 3]      [Background Tasks]     |
+-------+--------------+---------------+-------------------+--------------+
        |              |               |                   |
        v              v               v                   v
+-------------------------------------------------------------------------+
|                  SQLAlchemy AsyncAdaptedQueuePool                       |
|  Steady pool [ C1 | C2 | C3 | ... | C_pool_size ]                       |
|  Overflow    [ O1 | O2 | ... | O_max_overflow   ]                       |
+-------------------------------------------------------------------------+
                                    |
                       TCP sockets (asyncpg driver)
                                    v
+-------------------------------------------------------------------------+
|                       PostgreSQL Database Server                        |
|                     (max_connections = 200)                             |
+-------------------------------------------------------------------------+
```

### 19.1 প্রোডাকশন async engine { #s19-1 }
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,            # "postgresql+asyncpg://user:pass@host:5432/db"
    # async engine-এর ডিফল্ট পুল হলো AsyncAdaptedQueuePool

    pool_size=20,                     # স্থায়ীভাবে খোলা রাখা কানেকশন সংখ্যা
    max_overflow=10,                  # ট্রাফিক স্পাইকে অতিরিক্ত সাময়িক কানেকশন
    pool_timeout=30,                  # ফাঁকা কানেকশনের জন্য সর্বোচ্চ অপেক্ষা (সেকেন্ড), তারপর TimeoutError
    pool_recycle=1800,                # ৩০ মিনিটের পুরোনো কানেকশন বদলে দেয় (ফায়ারওয়াল/LB idle drop রোধে)
    pool_pre_ping=True,               # চেকআউটে হালকা লাইভনেস চেক; মৃত সকেট নীরবে বদলে দেয়
    echo=False,                       # প্রোডাকশনে SQL লগিং বন্ধ (stdout I/O ব্যয়বহুল)

    connect_args={                    # সরাসরি asyncpg.connect()-এ যায়
        "server_settings": {
            "application_name": "fastapi_enterprise_app",
            "timezone": "UTC",
            "statement_timeout": "30000",     # প্রতিটি স্টেটমেন্টের সর্বোচ্চ সীমা ৩০ সেকেন্ড (ms)
        },
        "command_timeout": 30,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,          # ভ্যালিডেশন লজিকের মাঝে অপ্রত্যাশিত flush নয়
    expire_on_commit=False,   # async-এ অত্যাবশ্যক: commit-এর পরও অ্যাট্রিবিউট পড়া যায়
)
```

/// info | কোডটি সহজ ভাষায়

* `pool_size=20` + `max_overflow=10`: স্বাভাবিক সময়ে সর্বোচ্চ ২০টি, ভিড়ে সর্বোচ্চ ৩০টি কানেকশন। ৩১তম রিকোয়েস্টটি অপেক্ষা করবে।
* `pool_timeout=30`: ৩০ সেকেন্ডেও কানেকশন না পেলে `TimeoutError`। এরর আসাটাও ভালো, কারণ চিরকাল আটকে থাকার চেয়ে দ্রুত জানা ভালো।
* `pool_recycle=1800`: ৩০ মিনিটের পুরোনো কানেকশন বাদ দিয়ে নতুন খোলে। অনেক ফায়ারওয়াল বা লোড ব্যালান্সার অলস কানেকশন চুপচাপ কেটে দেয়।
* `pool_pre_ping=True`: কানেকশন দেওয়ার আগে ছোট্ট একটা "বেঁচে আছো?" পরীক্ষা। মরা কানেকশন হলে নিজেই নতুন দেয়।
* `server_settings`: প্রতিটি কানেকশনে PostgreSQL-এর সেটিং। যেমন `statement_timeout` ৩০ সেকেন্ডের বেশি চলা কুয়েরি বাতিল করে।
* `autoflush=False`, `expire_on_commit=False`: এই দুটির কারণ [§22.5](transactions.md#s22-5) আর [§20](#s20)-এ আছে।

///

/// note | `engine` একটি, `session` অনেক

পুরো অ্যাপে **একটিই** `engine` বানান (মডিউল লেভেলে)। প্রতিটি রিকোয়েস্টে নতুন engine বানালে প্রতিবার নতুন পুল তৈরি হয়, ফলে পুলের সুবিধাই নষ্ট হয় আর কানেকশন ফুরিয়ে যায়। উল্টো দিকে, `session` প্রতি রিকোয়েস্টে **নতুন**, আর কাজ শেষে বন্ধ।

///

### 19.2 Sync engine-এর সমতুল্য { #s19-2 }
```python
from sqlalchemy import create_engine

sync_engine = create_engine(
    "postgresql+psycopg://user:password@localhost:5432/production_db",
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)
```

### 19.3 পুলের ধরন { #s19-3 }
| Pool | কখন ব্যবহৃত হয় |
| :--- | :--- |
| **`QueuePool`** | Sync engine-এর ডিফল্ট (SQLite in-memory ছাড়া)। থ্রেড-সেফ FIFO পুল। |
| **`AsyncAdaptedQueuePool`** | Async engine-এর ডিফল্ট। একই আচরণ, asyncio-বান্ধব। |
| **`NullPool`** | কোনো পুলিং নেই: প্রতি চেকআউটে আসল কানেকশন খোলে/বন্ধ করে। সার্ভারলেস (AWS Lambda) এবং **transaction mode-এর PgBouncer**-এর পেছনে ব্যবহার করুন। |
| **`StaticPool`** | সব জায়গায় শেয়ার করা ঠিক একটি কানেকশন — in-memory SQLite টেস্ট। |

### 19.4 পুলের আকার নির্ধারণ { #s19-4 }
- মোট কানেকশন = `(pool_size + max_overflow) × প্রসেস সংখ্যা`। `20 + 10` সহ চারটি Uvicorn worker সর্বোচ্চ **১২০টি** কানেকশন খুলতে পারে — এটিকে PostgreSQL-এর `max_connections` থেকে মাইগ্রেশন, অ্যাডমিন ও অন্যান্য সার্ভিসের জায়গা বাদ দিয়ে কম রাখুন।
- *সক্রিয়* কানেকশনের জন্য DB-দিকের প্রচলিত হিসাব `(CPU core × 2) + effective_spindles`; এর বেশি কানেকশন মূলত শুধু প্রতিযোগিতা বাড়ায়।
- অনেক রেপ্লিকা/প্রসেস চালালে সামনে **PgBouncer** বসান এবং অ্যাপে `NullPool` (অথবা ছোট পুল) ব্যবহার করুন।

/// note | নোট

PgBouncer transaction pooling mode-এ asyncpg-এর prepared-statement cache ভেঙে যায়। `connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0}` যোগ করুন।

///

/// tip | একটি হিসাব করে দেখি

ধরুন PostgreSQL-এ `max_connections = 100`। মাইগ্রেশন আর অ্যাডমিনের জন্য ১০টি রেখে বাকি ৯০টি।

* ৪টি Uvicorn worker চালাবেন → প্রতি worker সর্বোচ্চ ৯০ ÷ ৪ ≈ ২২টি।
* তাই `pool_size=15`, `max_overflow=5` (মোট ২০) নিরাপদ।
* পরে Kubernetes-এ ৩টি pod করলে ১২টি worker × ২০ = ২৪০টি, সীমা ছাড়িয়ে যাবে! তখন পুল ছোট করুন বা PgBouncer বসান।

///

## 20. AsyncIO Extension, `MissingGreenlet` ও FastAPI Session Dependency { #s20 }

### 20.1 Greenlet ব্রিজ { #s20-1 }

/// tip | উদাহরণ দিয়ে বুঝি

SQLAlchemy-র ভেতরের ORM কোড বহু বছরের পুরোনো, পুরোপুরি sync। async ড্রাইভার (`asyncpg`) বোঝে শুধু `await`। **greenlet** দুজনের মাঝের একজন দোভাষী। ORM যখন বলে "এই SQL চালাও", দোভাষী চুপিচুপি ইভেন্ট লুপকে বলে "আমি অপেক্ষা করছি, অন্য কাজ সেরে নাও", তারপর উত্তর এলে ORM-কে ফিরিয়ে দেয়।

সমস্যা হয় যখন এই দোভাষী উপস্থিত নেই এমন জায়গায় (`await` ছাড়া সাধারণ কোডে) ORM ডেটাবেসে যেতে চায়। তখনই আসে `MissingGreenlet`।

///

SQLAlchemy-র ORM কোর (mapper, unit of work, identity map) synchronous কোড। asyncio extension এই কোডকে একটি **greenlet**-এর ভেতরে চালায়, এবং যখনই নেটওয়ার্ক I/O দরকার হয়, greenlet ইভেন্ট লুপে ফিরে গিয়ে async ড্রাইভারকে `await` করে। আপনি লেখেন `await session.execute(...)`; ভেতরে sync ORM অপরিবর্তিত থেকে চলে।

```
+--------------------------------------------------------------------+
|                         AsyncSession                               |
|   await session.execute()  -->  spawns greenlet runner context     |
+--------------------------------------------------------------------+
                                 |
                                 v
+--------------------------------------------------------------------+
|                     Synchronous ORM core logic                     |
|   Mapper, Session, Identity Map, dependency graph                  |
+--------------------------------------------------------------------+
                                 |
                                 v
+--------------------------------------------------------------------+
|                 AsyncAdapt connection bridge                       |
|   Intercepts sync DBAPI calls -> converts to asyncio awaitables    |
+--------------------------------------------------------------------+
                                 |
                                 v
+--------------------------------------------------------------------+
|                       asyncpg / psycopg driver                     |
|   Native non-blocking TCP socket operations                        |
+--------------------------------------------------------------------+
```

### 20.2 `MissingGreenlet` — এর অর্থ { #s20-2 }
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here. Was IO attempted in an unexpected place?
```
কোনো কোড `await` করা SQLAlchemy কলের **বাইরে** ডেটাবেস I/O করার চেষ্টা করেছে। সাধারণ কারণ:
1. **লোড না হওয়া রিলেশনশিপ** ছোঁয়া (`order.items`) → ইমপ্লিসিট lazy load।
2. **`commit()`-এ expire হওয়া** অ্যাট্রিবিউট পড়া (যখন `expire_on_commit=True`) → ইমপ্লিসিট refresh।
3. লোড না হওয়া **deferred কলাম** পড়া।
4. FastAPI/Pydantic `response_model`-এ লোড না হওয়া রিলেশনশিপসহ মডেল **সিরিয়ালাইজ** করছে।

/// info | প্রতিটি কারণ ও সমাধান, কোডসহ

```python
# ১. লোড না হওয়া রিলেশনশিপ
order = await session.get(Order, 1)
order.items                                     # ❌ MissingGreenlet (অথবা lazy="raise" এরর)

order = await session.get(Order, 1, options=[selectinload(Order.items)])
order.items                                     # ✅ আগেই লোড করা

# ২. commit-এর পর expire হওয়া অ্যাট্রিবিউট (expire_on_commit=True থাকলে)
await session.commit()
order.status                                    # ❌ আবার লোড করতে চায়
# ✅ সমাধান: async_sessionmaker(..., expire_on_commit=False), অথবা await session.refresh(order)

# ৩. ডেটাবেস নিজে যে মান বানায় (server_default / onupdate=func.now())
order.status = "PAID"
await session.commit()
order.updated_at                                # ❌ মানটি ডেটাবেসে তৈরি, মেমরিতে নেই
await session.refresh(order)                    # ✅ অথবা মডেলে "eager_defaults": True

# ৪. FastAPI রেসপন্স সিরিয়ালাইজ করার সময়
return order                                    # ❌ response_model-এ items আছে, কিন্তু লোড করা হয়নি
# ✅ যা যা রেসপন্সে যাবে, কুয়েরিতেই selectinload() / joinedload() দিয়ে লোড করুন
```

///

### 20.3 Async নিরাপত্তার Golden Rules { #s20-3 }
1. `async_sessionmaker`-এ **`expire_on_commit=False`** — `commit()`-এর পরও অবজেক্ট পড়া যায়।
2. রিলেশনশিপে **`lazy="raise"`** — ভুলবশত lazy load টেস্টেই পরিষ্কারভাবে ফেইল করে।
3. রেসপন্সের যা যা লাগবে সব `selectinload()` / `joinedload()` দিয়ে **স্পষ্টভাবে eager load** করুন।
4. সার্ভারে তৈরি মান লেখার পর `await session.refresh(obj)` (প্রয়োজনে `refresh(obj, ["items"])`)।
5. শুধু-sync API (DDL, `inspect`, পুরোনো হেল্পার) চালাতে `await conn.run_sync(fn)` / `await session.run_sync(fn)`।
6. একটি অ্যাট্রিবিউটের জন্য শেষ উপায়: `await obj.awaitable_attrs.items` (`Base`-এ 2.0-এর `AsyncAttrs` mixin)। এটি শুধু ডিফল্ট `lazy="select"` রিলেশনশিপে কাজ করে; `lazy="raise"` দেওয়া থাকলে এটিও এরর দেবে।

### 20.4 FastAPI session dependency { #s20-4 }
```python
# app/core/database.py
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """প্রতি রিকোয়েস্টে একটি সেশন। কখন commit হবে তা কলার ঠিক করে।"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

/// info | কোডটি সহজ ভাষায়

* `async with AsyncSessionLocal() as session`: নতুন সেশন। ব্লক শেষ হলে (রেসপন্স পাঠানোর পর) নিজেই বন্ধ হয়, কানেকশন পুলে ফেরত যায়।
* `yield session`: FastAPI এই সেশনটি পাথ অপারেশন ফাংশনে দেয়।
* `except Exception: await session.rollback(); raise`: এন্ডপয়েন্টে এরর হলে অর্ধেক কাজ বাতিল, আর এররটি আবার ছুড়ে দেওয়া, যাতে FastAPI ঠিক রেসপন্স দিতে পারে।

ব্যবহার, `Annotated` দিয়ে একটি ছোট নাম বানিয়ে:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/orders/{order_id}")
async def read_order(order_id: int, session: SessionDep):
    return await session.get(Order, order_id)
```

একই রিকোয়েস্টে একাধিক ডিপেন্ডেন্সি `get_db` চাইলেও FastAPI একবারই চালায়, তাই সবাই **একই সেশন** পায়।

///

দুটি প্রচলিত ধরন:
- **স্পষ্ট commit** (এই গাইডের বেশিরভাগ উদাহরণে): এন্ডপয়েন্ট/রিপোজিটরি `await session.commit()` কল করে।
- **রিকোয়েস্ট-প্রতি unit of work**: এক্সেপশন না ঘটলে dependency `yield`-এর পর commit করে ([§23.3](transactions.md#s23-3)-এর `get_write_db` দেখুন)। তখন রিপোজিটরি শুধু `flush()` করে।

প্রতিটি প্রজেক্টে একটি ধরন বেছে নিয়ে সেটাতেই থাকুন — মিশিয়ে ফেললে দুবার commit বা commit ভুলে যাওয়ার সমস্যা হয়।

/// warning | একটি সেশন, একটি কাজ

`AsyncSession` একসাথে একাধিক কাজের জন্য নিরাপদ নয়। একই সেশন দিয়ে `asyncio.gather(...)` চালাবেন না:

```python
# ❌ ভুল: একই সেশনে একসাথে দুটি কুয়েরি
await asyncio.gather(session.scalars(q1), session.scalars(q2))

# ✅ পরপর চালান
r1 = await session.scalars(q1)
r2 = await session.scalars(q2)

# ✅ সত্যিই একসাথে চালাতে চাইলে প্রতিটির জন্য আলাদা সেশন
async def run(q):
    async with AsyncSessionLocal() as s:
        return (await s.scalars(q)).all()

r1, r2 = await asyncio.gather(run(q1), run(q2))
```

///

/// check | সংক্ষেপে মনে রাখুন

* একটি অ্যাপ = একটি `engine` = একটি কানেকশন পুল। মোট কানেকশন = `(pool_size + max_overflow) × প্রসেস সংখ্যা`।
* প্রোডাকশনে `pool_pre_ping=True`, `pool_recycle`, আর টাইমআউট দিন।
* `async_sessionmaker(..., expire_on_commit=False)` async-এ প্রায় বাধ্যতামূলক।
* `MissingGreenlet` মানে `await` ছাড়া কোথাও ডেটাবেসে যাওয়ার চেষ্টা। সমাধান: আগেভাগে লোড, `refresh()`, `lazy="raise"`।
* প্রতি রিকোয়েস্টে একটি নতুন সেশন (`Depends(get_db)`), কখনো শেয়ার নয়।

///

**পরের ধাপ:** commit, rollback আর সেশনের ভেতরের কাজ শিখুন [Transaction ও Session-এর ভেতরের কাজ](transactions.md) অধ্যায়ে।
