# Transaction ও Session-এর ভেতরের কাজ { #sqlalchemy-transactions }

/// note | এই পেজে যা শিখবেন

* ট্রানজ্যাকশন কী, আর SQLAlchemy 2.0-তে commit-এর দুটি ধরন।
* isolation level আর savepoint (ট্রানজ্যাকশনের ভেতরে ছোট ট্রানজ্যাকশন)।
* সেশনের ভেতরে একটি অবজেক্টের চারটি অবস্থা, identity map, আর `flush()` বনাম `commit()`।
* দীর্ঘ সময় চলা worker-এ মেমরি লিক এড়ানো।
* execution option, statement cache, read replica ও multi-tenancy।

///

/// tip | উদাহরণ দিয়ে বুঝি

আপনি মোবাইল ব্যাংকিংয়ে বন্ধুকে ৫০০ টাকা পাঠালেন। দুটি কাজ হবে: আপনার অ্যাকাউন্ট থেকে ৫০০ কমবে, বন্ধুর অ্যাকাউন্টে ৫০০ বাড়বে। কল্পনা করুন প্রথমটা হলো, তারপর সার্ভার বন্ধ! আপনার টাকা কাটা গেল, বন্ধু পেল না।

**ট্রানজ্যাকশন** এই বিপদ থেকে বাঁচায়: হয় দুটি কাজই হবে (**COMMIT**), নয়তো একটিও না (**ROLLBACK**)। মাঝামাঝি কোনো অবস্থা ডেটাবেসে কখনো দেখা যায় না।

///

## 21. Transaction: Commit-as-you-go, `begin()`, Isolation Level ও Savepoint { #s21 }

SQLAlchemy 2.0-এ লাইব্রেরি-লেভেলের autocommit নেই। প্রথম স্টেটমেন্টে transaction নিজে থেকে শুরু হয় এবং আপনি `commit()` / `rollback()` না করা পর্যন্ত, বা একটি `begin()` ব্লক শেষ না হওয়া পর্যন্ত চলতে থাকে।

### 21.1 দুটি ধরন (Core connection দেখানো হলো; session-ও একইভাবে আচরণ করে) { #s21-1 }
```python
from sqlalchemy import text

# ধরন A — context-managed transaction: সফল হলে COMMIT, এক্সেপশনে ROLLBACK
with sync_engine.begin() as conn:
    conn.execute(text("UPDATE accounts SET balance = balance - 100 WHERE id = :id"), {"id": 1})
    conn.execute(text("UPDATE accounts SET balance = balance + 100 WHERE id = :id"), {"id": 2})

# ধরন B — commit as you go
with sync_engine.connect() as conn:
    balance = conn.execute(
        text("SELECT balance FROM accounts WHERE id = :id"), {"id": 1}
    ).scalar_one()
    if balance >= 100:
        conn.execute(text("UPDATE accounts SET balance = balance - 100 WHERE id = :id"), {"id": 1})
        conn.commit()
    else:
        conn.rollback()
```

/// info | কোডটি সহজ ভাষায়

* **ধরন A, `engine.begin()`**: "এই ব্লকের সব কাজ এক ট্রানজ্যাকশন।" ব্লক ঠিকঠাক শেষ হলে নিজেই COMMIT, মাঝে এরর হলে নিজেই ROLLBACK। ভুলে যাওয়ার সুযোগ নেই, তাই বেশিরভাগ ক্ষেত্রে এটাই ভালো।
* **ধরন B, `engine.connect()` + `conn.commit()`**: আপনি নিজে ঠিক করবেন কখন commit, কখন rollback। শর্তের ওপর নির্ভর করলে কাজে লাগে।
* ধরন B-তে commit না করে ব্লক থেকে বের হলে সব পরিবর্তন **বাতিল** হয়ে যায়।

///

`AsyncSession`-এ:
```python
async with AsyncSessionLocal() as session:
    async with session.begin():        # শেষে commit, এক্সেপশনে rollback
        session.add(obj)
    # transaction এখানে শেষ
```

/// note | পরিচিত প্যাটার্ন

FastAPI এন্ডপয়েন্টে সাধারণত `get_db` থেকে সেশন আসে, আর আপনি কাজ শেষে `await session.commit()` লেখেন। এটা **ধরন B** (commit as you go)। কয়েকটি টেবিলে একসাথে লেখার সময় `async with session.begin():` (ধরন A) বেশি নিরাপদ। এর উদাহরণ পাবেন [সম্পর্কিত টেবিলে CRUD](related-crud.md) অধ্যায়ে।

///

/// warning | সতর্কতা

Session যদি আগেই নিজে থেকে একটি transaction শুরু করে থাকে (যেমন একই রিকোয়েস্টে আগে কোনো কুয়েরি চালানো হয়েছে), তাহলে `async with session.begin():` *"A transaction is already begun"* এরর দেয়। হয় শুরুতেই `begin()` ব্লক খুলুন, নয়তো স্পষ্ট `commit()` ব্যবহার করুন।

///

### 21.2 Isolation level { #s21-2 }
```python
# প্রতি কানেকশনে
async with engine.connect() as conn:
    conn = await conn.execution_options(isolation_level="SERIALIZABLE")
    async with conn.begin():
        ...

# পুরো engine-এর ডিফল্ট
engine = create_async_engine(url, isolation_level="REPEATABLE READ")

# serializable কাজের জন্য আলাদা engine (ডিফল্টটির সাথে কিছু শেয়ার করে না)
serializable_engine = engine.execution_options(isolation_level="SERIALIZABLE")
```

| লেভেল (PostgreSQL) | কী ঠেকায় | সাধারণ ব্যবহার |
| :--- | :--- | :--- |
| `READ COMMITTED` (ডিফল্ট) | Dirty read | সাধারণ OLTP |
| `REPEATABLE READ` | + non-repeatable read (snapshot) | এক transaction-এ সামঞ্জস্যপূর্ণ রিপোর্ট |
| `SERIALIZABLE` | + write skew / phantom | একাধিক রো জুড়ে আর্থিক নিয়ম; **40001-এ retry** ([§47.6](concurrency.md#s47-6)) |
| `AUTOCOMMIT` | — | `VACUUM`, `CREATE INDEX CONCURRENTLY`, `CREATE DATABASE` |

/// tip | isolation level সহজ ভাষায়

একসাথে অনেক ট্রানজ্যাকশন চললে একে অপরের অসমাপ্ত কাজ কতটা দেখতে পাবে, সেটাই isolation level।

* **READ COMMITTED** (PostgreSQL-এর ডিফল্ট): অন্যের শুধু **commit হওয়া** পরিবর্তন দেখবেন। তবে একই ট্রানজ্যাকশনে একই কুয়েরি দুবার চালালে মাঝে অন্য কেউ commit করলে দুবার দুই রকম ফল পেতে পারেন।
* **REPEATABLE READ**: ট্রানজ্যাকশন শুরুর মুহূর্তের একটি "ছবি" দেখবেন। ভেতরে যতবার পড়ুন, একই ফল। রিপোর্টের জন্য ভালো।
* **SERIALIZABLE**: ডেটাবেস নিশ্চিত করে যেন সব ট্রানজ্যাকশন একটার পর একটা চলেছে। সবচেয়ে কঠোর, কিন্তু মাঝে মাঝে ট্রানজ্যাকশন বাতিল করে আবার চেষ্টা করতে বলে ([§47.6](concurrency.md#s47-6))।

সাধারণ CRUD অ্যাপে ডিফল্টই যথেষ্ট।

///

### 21.3 Savepoint (nested transaction) { #s21-3 }
`SAVEPOINT` transaction-এর একটি অংশকে ব্যর্থ হয়ে rollback হতে দেয়, অথচ বাইরের transaction চলতে থাকে।
```python
# Core
with sync_engine.begin() as conn:
    conn.execute(text("INSERT INTO audit_logs (action) VALUES ('START')"))
    savepoint = conn.begin_nested()
    try:
        conn.execute(text("INSERT INTO payment_records (status) VALUES ('PENDING')"))
        savepoint.commit()        # RELEASE SAVEPOINT
    except Exception:
        savepoint.rollback()      # ROLLBACK TO SAVEPOINT — বাইরের transaction এখনও সচল

# ORM / async: একটি ব্যাচ প্রসেস করা, অবৈধ আইটেম বাদ দিয়ে
async def process_batch_orders(session: AsyncSession, orders_data: list[dict]):
    async with session.begin():                       # বাইরের transaction
        for order_data in orders_data:
            try:
                async with session.begin_nested():    # প্রতি অর্ডারে SAVEPOINT
                    await process_single_order(session, order_data)
            except ValidationError as e:
                # শুধু এই অর্ডারটি rollback হয়; ব্যাচের বাকিগুলো টিকে থাকে
                logger.warning("Skipping invalid order %s: %s", order_data, e)
```

/// tip | উদাহরণ দিয়ে বুঝি

**Savepoint** হলো ভিডিও গেমের **চেকপয়েন্ট**। পুরো লেভেল (বাইরের ট্রানজ্যাকশন) চলছে। মাঝে একটা কঠিন অংশে হেরে গেলে শুরু থেকে নয়, শুধু শেষ চেকপয়েন্ট থেকে আবার শুরু।

ওপরের ব্যাচ উদাহরণে ৩টি অর্ডারের ২য়টি ভুল হলে শুধু সেটি বাদ যায়, ১ম ও ৩য়টি সংরক্ষিত থাকে। আমরা আসলে চালিয়ে দেখেছি: ফলাফলে ১ম ও ৩য় অর্ডারই থেকে যায়।

///

## 22. Unit of Work Internals: Session State, Identity Map, Flush ক্রম ও মেমরি { #s22 }

### 22.1 অবজেক্টের চারটি অবস্থা { #s22-1 }
```
                session.add()
  [ TRANSIENT ] -------------> [ PENDING ]
                                   |
                                   | session.flush()  (INSERT পাঠানো হয়)
                                   v
                                [ PERSISTENT ]  <-- কুয়েরি দিয়ে লোড করা অবজেক্টও
                                   |
                                   | session.close() / expunge() / commit()+expire
                                   v
                                [ DETACHED ]
```

/// tip | উদাহরণ দিয়ে বুঝি

একটি সরকারি অফিসে আবেদন জমা দেওয়ার কথা ভাবুন:

* **Transient**: বাড়িতে বসে ফর্ম পূরণ করেছেন, অফিস এখনো জানে না।
* **Pending**: কাউন্টারের "জমা" ট্রে-তে রেখেছেন (`session.add`), কিন্তু এখনো খাতায় ওঠেনি।
* **Persistent**: কর্মকর্তা খাতায় তুলে নম্বর দিয়েছেন (`flush`)। এখন অফিস এটা চেনে।
* **Detached**: অফিস বন্ধ হয়ে গেছে (`session.close`), আপনার হাতে শুধু রসিদের ফটোকপি। আরও কিছু জানতে চাইলে আবার অফিসে যেতে হবে।

///

1. **Transient** — Python-এ তৈরি (`u = User(name="Alice")`), কোনো সেশনের অজানা, DB-তে রো নেই।
2. **Pending** — `session.add(u)` করা হয়েছে; এখনও কোনো SQL পাঠানো হয়নি।
3. **Persistent** — সেশনের **Identity Map**-এ আছে এবং DB-তে সংশ্লিষ্ট রো আছে (flush-এর পর, অথবা কুয়েরিতে লোড হলে)।
4. **Detached** — পরিচয় ছিল, কিন্তু সেশন বন্ধ হয়ে গেছে বা `expunge()` করা হয়েছে। লোড না হওয়া অ্যাট্রিবিউট অ্যাক্সেস করলে `DetachedInstanceError`।

(এ ছাড়া আছে **deleted**: `DELETE` flush হয়েছে কিন্তু commit হয়নি — commit-এর পর এটি detached হয়।)

যেকোনো অবজেক্টের অবস্থা দেখতে: `from sqlalchemy import inspect; inspect(obj).persistent`।

### 22.2 Identity Map { #s22-2 }
এক সেশনের মধ্যে একটি নির্দিষ্ট `(class, primary key)` **ঠিক একটি Python অবজেক্টের** সাথে ম্যাপ হয়:
```python
user_a = await session.get(User, 1)
user_b = await session.scalar(select(User).where(User.id == 1))
assert user_a is user_b          # মেমরিতে একই অবজেক্ট
```

/// tip | উদাহরণ দিয়ে বুঝি

**Identity map** হলো ক্লাসের হাজিরা খাতা। একই রোল নম্বরের ছাত্র খাতায় একবারই থাকে। আপনি নাম দিয়ে খুঁজুন বা রোল দিয়ে, একই ছাত্রকেই পাবেন। ফলে একই রো-র দুটি আলাদা Python অবজেক্ট কখনো তৈরি হয় না, আর একটিতে করা পরিবর্তন অন্যটিতে হারায় না।

///

ফলাফল:
- অবজেক্ট আগেই লোড হয়ে থাকলে `session.get()` SQL ছাড়াই identity map থেকে রিটার্ন করে।
- পরের কোনো কুয়েরি মেমরিতে আপনার পরিবর্তিত অ্যাট্রিবিউট **ওভাররাইট করে না** (DB থেকে জোর করে রিফ্রেশ করতে `populate_existing()` ব্যবহার করুন)।

### 22.3 `flush()` কীভাবে SQL-এর ক্রম ঠিক করে { #s22-3 }
আপনি যে ক্রমে `add()` / অ্যাট্রিবিউট সেট করেছেন SQLAlchemy সেই ক্রমে SQL পাঠায় **না**। Flush-এর সময় unit of work:
1. নতুন, dirty (পরিবর্তিত) ও deleted অবজেক্ট সংগ্রহ করে।
2. ফরেন কি ও রিলেশনশিপ থেকে একটি **dependency graph** তৈরি করে।
3. Topological sort করে — প্যারেন্ট INSERT, তারপর চাইল্ড INSERT, তারপর UPDATE, তারপর চাইল্ড DELETE, তারপর প্যারেন্ট DELETE।
4. একই ধরনের স্টেটমেন্টগুলো `executemany` / মাল্টি-রো INSERT-এ ব্যাচ করে।

এ কারণেই নতুন প্যারেন্টে চাইল্ড append করে শুধু প্যারেন্টকে `add()` করলেই চলে — FK মান সঠিক সময়ে বসে যায়।

### 22.4 `flush()` বনাম `commit()` বনাম `refresh()` { #s22-4 }
| কল | কী ঘটে |
| :--- | :--- |
| `await session.flush()` | জমা SQL পাঠায়; transaction **খোলা** থাকে; তৈরি হওয়া PK এখন পাওয়া যায়। |
| `await session.commit()` | Flush করে, তারপর COMMIT। `expire_on_commit=True` হলে সব অবজেক্ট expire হয়। |
| `await session.rollback()` | Rollback করে; pending অবজেক্ট বাদ পড়ে, persistent অবজেক্ট expire হয়। |
| `await session.refresh(obj)` | রো আবার SELECT করে (সার্ভার ডিফল্ট/ট্রিগারের মান লোড হয়)। |
| `session.expunge(obj)` / `expunge_all()` | অবজেক্ট detach করে; identity map-এর মেমরি ফাঁকা করে। |

/// tip | উদাহরণ দিয়ে বুঝি

* **`flush()`** = পেনসিলে খসড়া লেখা। ডেটাবেস লেখাটা দেখে, নতুন রো-র id-ও দিয়ে দেয়, কিন্তু চাইলে এখনো মুছে ফেলা যায় (rollback)।
* **`commit()`** = কলমে সই করে জমা দেওয়া। এখন স্থায়ী।
* **`refresh(obj)`** = ডেটাবেস থেকে সর্বশেষ মানগুলো আবার পড়ে আনা।

```python
order = Order(customer_id=1, order_code="A-1")
session.add(order)
print(order.order_id)    # None — এখনো ডেটাবেসে যায়নি
await session.flush()
print(order.order_id)    # 42 — ডেটাবেস id দিয়েছে, কিন্তু commit হয়নি
await session.commit()   # এখন স্থায়ী
```

///

### 22.5 Autoflush { #s22-5 }
`autoflush=True` (sync-এর ডিফল্ট) থাকলে প্রতিটি কুয়েরির আগে সেশন নিজে flush করে, যাতে কুয়েরি জমা পরিবর্তন দেখতে পায়। এতে অবাক হওয়ার মতো ঘটনা ঘটতে পারে: অর্ধেক তৈরি অবজেক্ট আগেই INSERT হয়ে NOT NULL কনস্ট্রেইন্ট ভাঙে। আমরা এটি বন্ধ রাখি (`autoflush=False`) এবং স্পষ্টভাবে flush করি; সাময়িকভাবে বন্ধ করতে `with session.no_autoflush:`।

### 22.6 দীর্ঘমেয়াদি worker-এ মেমরি লিক { #s22-6 }
সেশন বন্ধ না হওয়া পর্যন্ত তার identity map লোড করা প্রতিটি অবজেক্ট ধরে রাখে। যে Celery টাস্ক, Kafka consumer বা cron লুপ চিরকাল একটি সেশন পুনর্ব্যবহার করে, তাতে মেমরি লিক হয়।

```python
async def background_consumer_loop(session_factory):
    async with session_factory() as session:
        while True:
            batch = await get_next_batch()
            await process_batch(session, batch)
            await session.commit()
            # প্রতি ব্যাচের পর লোড হওয়া সব অবজেক্ট ছেড়ে দেওয়া
            session.expunge_all()
```
আরও ভালো: লুপের ভেতরে **প্রতি ব্যাচে নতুন স্বল্পমেয়াদি সেশন** খুলুন (`async with session_factory() as session:`)।

/// info | কোডটি সহজ ভাষায়

প্রথম উদাহরণে একটি সেশন অনন্তকাল খোলা, তাই প্রতি ব্যাচ শেষে `expunge_all()` দিয়ে identity map খালি করতে হয়। দ্বিতীয় (ভালো) উপায়ে এমন লিখুন:

```python
async def background_consumer_loop(session_factory):
    while True:
        batch = await get_next_batch()
        async with session_factory() as session:      # প্রতি ব্যাচে নতুন, ছোট সেশন
            await process_batch(session, batch)
            await session.commit()
        # ব্লক শেষ: সেশন বন্ধ, সব অবজেক্ট মেমরি থেকে মুক্ত
```

///

## 23. Execution Options, Statement Cache, Read Replica ও Multi-Tenancy { #s23 }

### 23.1 Execution options ও compiled-SQL cache { #s23-1 }
SQLAlchemy 2.0 প্রতিটি স্টেটমেন্ট *আকারের* কম্পাইল করা SQL স্ট্রিং একটি LRU ক্যাশে রাখে (প্রতি engine-এ ডিফল্ট ৫০০টি; `create_engine(..., query_cache_size=1200)` দিয়ে বদলানো যায়)। প্যারামিটারের মান আলাদাভাবে বাইন্ড হয়, তাই ভিন্ন মানসহ একই কুয়েরি ক্যাশ করা কম্পাইলেশন পুনর্ব্যবহার করে।

```python
async def execute_with_custom_options(session: AsyncSession, order_id: str):
    stmt = (
        select(OrderHeader)
        .where(OrderHeader.order_id == order_id)
        .execution_options(
            # সতর্কতা: compiled_cache=None দিলে এই স্টেটমেন্টের ক্যাশ বন্ধ হয়ে যায়।
            # ডিফল্ট ক্যাশিং রাখতে অপশনটি বাদ দিন।
            schema_translate_map={"core": "tenant_123"},   # মাল্টি-টেন্যান্সি
            populate_existing=True,                        # identity-map-এর অবস্থা ওভাররাইট
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

/// warning | async-এ `yield_per`

`yield_per` মানে ডেটা টুকরো টুকরো করে আনা (server-side cursor)। `AsyncSession.execute()`-এ এটা দিলে `AsyncMethodRequired` এরর আসে, কারণ `execute()` পুরো ফলাফল একবারে মেমরিতে আনে। টুকরো করে আনতে `await session.stream(stmt)` অথবা `await session.stream_scalars(stmt)` ব্যবহার করুন ([§48.3](performance.md#s48-3))। এই কারণে ওপরের উদাহরণে `yield_per` রাখা হয়নি।

///

কাজের অপশন:
| অপশন | প্রভাব |
| :--- | :--- |
| `yield_per=N` | N রো-র ব্যাচে আনা (server-side cursor)। Async-এ শুধু `session.stream()` / `stream_scalars()`-এর সাথে চলে; `session.execute()`-এ দিলে `AsyncMethodRequired` এরর |
| `populate_existing=True` | আগে লোড হওয়া অবজেক্ট DB-র মান দিয়ে রিফ্রেশ |
| `schema_translate_map={...}` | এক্সিকিউশনের সময় স্কিমা নাম বদলে দেওয়া |
| `synchronize_session=...` | বাল্ক `update()`/`delete()` মেমরির অবজেক্ট কীভাবে সিঙ্ক করবে (`"auto"`, `"fetch"`, `"evaluate"`, `False`) |
| `isolation_level="..."` | প্রতি-কানেকশন isolation |
| `compiled_cache=None` | স্টেটমেন্ট ক্যাশিং বন্ধ (শুধু ডিবাগিংয়ে) |

### 23.2 ক্যাশ সমস্যা নির্ণয় { #s23-2 }
`echo=True` থাকলে প্রতিটি স্টেটমেন্টের লগ লাইনের শেষে `[cached since 12.3s ago]`, `[generated in 0.0003s]` বা `[no key]` লেখা থাকে। একই কুয়েরির জন্য বারবার `[generated]` মানে কিছু একটা (সাধারণত কাস্টম কনস্ট্রাক্ট বা `cache_ok = True` ছাড়া `TypeDecorator`) ক্যাশিং ব্যর্থ করছে।

### 23.3 CQRS: primary-তে লেখা, replica থেকে পড়া { #s23-3 }
```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

primary_engine = create_async_engine(settings.PRIMARY_DATABASE_URL, pool_size=20, pool_pre_ping=True)
replica_engine = create_async_engine(settings.REPLICA_DATABASE_URL, pool_size=40, pool_pre_ping=True)

PrimarySessionFactory = async_sessionmaker(bind=primary_engine, expire_on_commit=False)
ReplicaSessionFactory = async_sessionmaker(bind=replica_engine, expire_on_commit=False)

async def get_write_db() -> AsyncGenerator[AsyncSession, None]:
    """রিকোয়েস্ট-প্রতি unit of work: সফল হলে commit, এররে rollback।"""
    async with PrimarySessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """শুধু-পড়া: commit-এর দরকার নেই।"""
    async with ReplicaSessionFactory() as session:
        yield session
```

/// info | কোডটি সহজ ভাষায়

বড় অ্যাপে সাধারণত একটি **primary** ডেটাবেস (সব লেখা এখানে) আর কয়েকটি **replica** (primary-র কপি, শুধু পড়ার জন্য) থাকে। পড়ার রিকোয়েস্ট অনেক বেশি হয়, তাই সেগুলো replica-তে পাঠালে primary-র চাপ কমে।

```python
@router.get("/orders")                                  # শুধু পড়া → replica
async def list_orders(session: AsyncSession = Depends(get_read_db)): ...

@router.post("/orders")                                 # লেখা → primary, নিজে commit করে
async def create_order(data: OrderCreate, session: AsyncSession = Depends(get_write_db)): ...
```

`get_write_db` নিজেই `yield`-এর পর commit করে, তাই এখানে এন্ডপয়েন্ট বা repository শুধু `flush()` করবে, `commit()` নয়।

///

**Replication lag** মনে রাখুন: যে রিকোয়েস্ট এইমাত্র লিখেছে এবং নিজের লেখা পড়তে হবে, সে primary ব্যবহার করবে।

### 23.4 Schema-per-tenant মাল্টি-টেন্যান্সি { #s23-4 }
মডেলগুলো একটি placeholder স্কিমা ঘোষণা করে (`{"schema": "core"}`), এবং প্রতিটি রিকোয়েস্ট সেটিকে টেন্যান্টের স্কিমায় ম্যাপ করে:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def tenant_session(tenant_schema: str):
    async with primary_engine.connect() as conn:
        conn = await conn.execution_options(schema_translate_map={"core": tenant_schema})
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session
            await session.commit()

# ব্যবহার
async with tenant_session("tenant_123") as session:
    orders = (await session.scalars(select(OrderHeader).limit(10))).all()
```

/// info | কোডটি সহজ ভাষায়

প্রতিটি গ্রাহক কোম্পানির (tenant) জন্য আলাদা PostgreSQL স্কিমা (`tenant_123`, `tenant_456` …), কিন্তু সবগুলোতে একই টেবিল। মডেলে লেখা থাকে `{"schema": "core"}`, আর `schema_translate_map` চলার সময় `core`-কে বদলে সঠিক tenant-এর স্কিমা বসায়:

```sql
-- কোডে: select(OrderHeader)
-- আসলে চলে:
SELECT ... FROM tenant_123.order_header
```

///

অনুবাদটি এক্সিকিউশনের সময় হয় বলে compiled-SQL ক্যাশ টেন্যান্টদের মধ্যে শেয়ার থাকে।

/// check | সংক্ষেপে মনে রাখুন

* ট্রানজ্যাকশন = সব অথবা কিছুই না। 2.0-তে autocommit নেই, প্রথম SQL-এই ট্রানজ্যাকশন শুরু হয়।
* `async with session.begin():` = ব্লক শেষে নিজেই commit বা rollback; অথবা নিজে `await session.commit()`।
* savepoint (`begin_nested()`) = ভেতরের একটা অংশ ব্যর্থ হলেও বাকিটা টিকে থাকে।
* অবজেক্টের অবস্থা: transient → pending → persistent → detached।
* `flush()` = SQL পাঠায়, ট্রানজ্যাকশন খোলা; `commit()` = স্থায়ী।
* দীর্ঘ worker-এ প্রতি ব্যাচে নতুন সেশন।

///

**পরের ধাপ:** ডেটা খোঁজা শিখুন [কুয়েরি: select() ও JOIN](querying.md) অধ্যায়ে।
