# Async API: সম্পূর্ণ রেফারেন্স { #api-async }

/// note | এই পেজে যা আছে

* `create_async_engine()`, `AsyncEngine`, `AsyncConnection`, `AsyncTransaction`-এর **প্রতিটি** সদস্য।
* `async_sessionmaker`, `AsyncSession` (FastAPI-তে সবচেয়ে বেশি ব্যবহৃত), `AsyncSessionTransaction`, `AsyncAttrs`, `async_scoped_session`।
* async ফলাফল: `AsyncResult`, `AsyncScalarResult`, `AsyncMappingResult`, `AsyncTupleResult`।

///

async API আসলে sync API-র একটি পাতলা মোড়ক (wrapper)। ভেতরে সেই একই `Session` / `Connection` চলে, শুধু যেখানে ডেটাবেসে যেতে হয় সেখানে `await` লাগে। তাই এখানে অনেক মেথডের ব্যাখ্যা [Session API](session.md) বা [Result API](result.md) পেজের সংশ্লিষ্ট মেথডের সাথে লিংক করা। প্রতিটি মেথডের সিগনেচারের সামনে `await` দেখলে বুঝবেন সেটি await করতে হবে।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

সব উদাহরণ একটি `async def` ফাংশনের ভেতরে চলছে ধরে লেখা, আর PostgreSQL + `asyncpg`-এ চালিয়ে দেখা হয়েছে। ডেটাবেসে তিনজন ইউজার: রহিম (id ১, একটি ঠিকানাসহ), করিম, সুমি।

```python
from sqlalchemy import ForeignKey, String, func, select, text
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/shop")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
session = SessionLocal()
```

///

## `create_async_engine()` { #create-async-engine }

```python
from sqlalchemy.ext.asyncio import create_async_engine
```

```python
create_async_engine(url, **kw)
```

**ধরন:** ফাংশন

একটি `AsyncEngine` বানায়। প্যারামিটার হুবহু sync `create_engine()`-এর মতো (`pool_size`, `max_overflow`, `pool_pre_ping`, `echo`, `connect_args` …), শুধু URL-এ একটি **async ড্রাইভার** লাগবে, যেমন `postgresql+asyncpg://` বা `sqlite+aiosqlite://`। পুরো অ্যাপে একটিই engine বানান। পুলের সেটিংয়ের বিস্তারিত দেখুন [Engine অধ্যায়ে](../engine-session.md#s19-1)।

**উদাহরণ:**

```python
engine = create_async_engine(
    "postgresql+asyncpg://postgres@127.0.0.1/apiref",
    pool_size=10, max_overflow=5, pool_pre_ping=True, echo=False,
)
async with engine.connect() as conn:
    print(await conn.scalar(text("SELECT 1")))   # 1
await engine.dispose()
```

## `async_engine_from_config()` { #async-engine-from-config }

```python
from sqlalchemy.ext.asyncio import async_engine_from_config
```

```python
async_engine_from_config(configuration, prefix='sqlalchemy.', **kwargs)
```

**ধরন:** ফাংশন

একটি dict (যেমন কনফিগ ফাইল থেকে পড়া) থেকে `AsyncEngine` বানায়। যেসব key `prefix` (ডিফল্ট `"sqlalchemy."`) দিয়ে শুরু, সেগুলো নেয়। Alembic-এর async `env.py` এটাই ব্যবহার করে।

**উদাহরণ:**

```python
cfg = {"sqlalchemy.url": URL, "sqlalchemy.echo": "false", "sqlalchemy.pool_pre_ping": "true"}
eng = async_engine_from_config(cfg)
print(eng.url.drivername)   # postgresql+asyncpg
await eng.dispose()
```

## `async_object_session()` { #async-object-session }

```python
from sqlalchemy.ext.asyncio import async_object_session
```

```python
async_object_session(instance)
```

**ধরন:** ফাংশন

একটি ORM অবজেক্ট কোন `AsyncSession`-এর সাথে যুক্ত তা দেয়, না থাকলে `None`।

**উদাহরণ:**

```python
user = await session.get(User, 1)
print(async_object_session(user) is session)   # True
```

## `async_session()` { #async-session }

```python
from sqlalchemy.ext.asyncio import async_session
```

```python
async_session(session)
```

**ধরন:** ফাংশন

ভেতরের একটি sync `Session` কোন `AsyncSession` মুড়ে রেখেছে তা দেয়। event hook-এর ভেতরে (যেখানে sync সেশন পাওয়া যায়) async সেশন খুঁজতে কাজে লাগে।

**উদাহরণ:**

```python
print(async_session(session.sync_session) is session)   # True
```

## `AsyncEngine` { #asyncengine }

```python
from sqlalchemy.ext.asyncio import AsyncEngine
```

sync `Engine`-এর async মোড়ক। কানেকশন পুল রাখে আর `AsyncConnection` দেয়। `create_async_engine()` দিয়ে বানানো হয়, সরাসরি নয়।

**উদাহরণ:**

```python
async with engine.begin() as conn:                     # ট্রানজ্যাকশনসহ কানেকশন
    await conn.execute(text("UPDATE users SET name = 'রহিম' WHERE id = 1"))
async with engine.connect() as conn:                   # শুধু কানেকশন
    print((await conn.execute(text("SELECT count(*) FROM users"))).scalar())   # 3
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncengine-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`begin()`](#asyncengine-begin) | মেথড | একটি context manager: ঢোকার সময় `AsyncConnection` নেয় আর ট্রানজ্যাকশন শুরু করে; ঠিকঠাক বের হলে commit, এরর হলে rollback, তারপর কানেকশন ফেরত। |
| [`clear_compiled_cache()`](#asyncengine-clear-compiled-cache) | মেথড | কম্পাইল করা SQL-এর ক্যাশ খালি করে। |
| [`connect()`](#asyncengine-connect) | মেথড | একটি `AsyncConnection` দেয়। |
| [`dialect`](#asyncengine-dialect) | প্রপার্টি | ব্যবহৃত ডেটাবেস ডায়ালেক্ট অবজেক্ট (PostgreSQL, MySQL …)। |
| [`dispose()`](#asyncengine-dispose) | মেথড (async) | পুলের সব কানেকশন বন্ধ করে নতুন খালি পুল বানায়। |
| [`driver`](#asyncengine-driver) | প্রপার্টি | DBAPI ড্রাইভারের নাম। |
| [`echo`](#asyncengine-echo) | প্রপার্টি | `True` হলে প্রতিটি SQL লগে লেখা হয়। |
| [`engine`](#asyncengine-engine) | প্রপার্টি | ভেতরের sync `Engine` দেয় (sync `Engine.engine` প্রপার্টির proxy, যা Engine আর Connection দুটোতে একইভাবে "engine" পাওয়ার সুবিধা দেয়)। |
| [`execution_options()`](#asyncengine-execution-options) | মেথড | নতুন একটি `AsyncEngine` দেয়, যা একই পুল শেয়ার করে কিন্তু প্রতিটি কানেকশনে দেওয়া execution option প্রয়োগ করে। |
| [`get_execution_options()`](#asyncengine-get-execution-options) | মেথড | এই engine-এর বর্তমান execution option-গুলো দেয়। |
| [`name`](#asyncengine-name) | প্রপার্টি | ডায়ালেক্টের নাম। |
| [`pool`](#asyncengine-pool) | প্রপার্টি | ভেতরের কানেকশন পুল অবজেক্ট। |
| [`raw_connection()`](#asyncengine-raw-connection) | মেথড (async) | পুল থেকে একটি "কাঁচা" DBAPI কানেকশন (মোড়কসহ) দেয়, SQLAlchemy-র ট্রানজ্যাকশন ব্যবস্থার বাইরে। |
| [`sync_engine`](#asyncengine-sync-engine) | অ্যাট্রিবিউট | ভেতরের আসল sync `Engine`। |
| [`update_execution_options()`](#asyncengine-update-execution-options) | মেথড | এই engine-এর ডিফল্ট execution option জায়গায় বদলায় (নতুন engine বানায় না)। |
| [`url`](#asyncengine-url) | প্রপার্টি | engine-এর ডেটাবেস URL (`URL` অবজেক্ট)। |

### `AsyncEngine.begin()` { #asyncengine-begin }

```python
AsyncEngine.begin()
```

**ধরন:** মেথড

একটি context manager: ঢোকার সময় `AsyncConnection` নেয় আর ট্রানজ্যাকশন শুরু করে; ঠিকঠাক বের হলে commit, এরর হলে rollback, তারপর কানেকশন ফেরত।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)    # টেবিল না থাকলে বানায়
```

### `AsyncEngine.clear_compiled_cache()` { #asyncengine-clear-compiled-cache }

```python
AsyncEngine.clear_compiled_cache()
```

**ধরন:** মেথড

কম্পাইল করা SQL-এর ক্যাশ খালি করে। সাধারণত দরকার হয় না; মেটাডেটা রানটাইমে বদলালে কাজে লাগতে পারে।

**উদাহরণ:**

```python
engine.clear_compiled_cache()
```

### `AsyncEngine.connect()` { #asyncengine-connect }

```python
AsyncEngine.connect()
```

**ধরন:** মেথড

একটি `AsyncConnection` দেয়। `async with engine.connect() as conn:` আকারে ব্যবহার করুন; ব্লক শেষে কানেকশন পুলে ফেরত যায়। এখানে commit নিজে থেকে হয় না।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    await conn.execute(text("UPDATE users SET name = 'R' WHERE id = 1"))
    await conn.commit()          # নিজে commit করতে হবে
```

### `AsyncEngine.dialect` { #asyncengine-dialect }

**ধরন:** প্রপার্টি

ব্যবহৃত ডেটাবেস ডায়ালেক্ট অবজেক্ট (PostgreSQL, MySQL …)।

**উদাহরণ:**

```python
print(engine.dialect.name)   # postgresql
```

### `AsyncEngine.dispose()` { #asyncengine-dispose }

```python
await AsyncEngine.dispose(close=True)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

পুলের সব কানেকশন বন্ধ করে নতুন খালি পুল বানায়। অ্যাপ বন্ধের সময় (FastAPI-র lifespan-এর শেষে) অবশ্যই `await engine.dispose()` ডাকুন। `close=False` দিলে চেকআউট করা কানেকশনগুলো বন্ধ না করে শুধু ছেড়ে দেয় (fork-এর পর কাজে লাগে)।

**উদাহরণ:**

```python
await engine.dispose()
```

### `AsyncEngine.driver` { #asyncengine-driver }

**ধরন:** প্রপার্টি

DBAPI ড্রাইভারের নাম।

**উদাহরণ:**

```python
print(engine.driver)   # asyncpg
```

### `AsyncEngine.echo` { #asyncengine-echo }

**ধরন:** প্রপার্টি

`True` হলে প্রতিটি SQL লগে লেখা হয়। চলমান অ্যাপেও বদলানো যায়।

**উদাহরণ:**

```python
engine.echo = False
print(engine.echo)   # False
```

### `AsyncEngine.engine` { #asyncengine-engine }

**ধরন:** প্রপার্টি

ভেতরের sync `Engine` দেয় (sync `Engine.engine` প্রপার্টির proxy, যা Engine আর Connection দুটোতে একইভাবে "engine" পাওয়ার সুবিধা দেয়)। কার্যত `sync_engine`-এর সমান।

**উদাহরণ:**

```python
print(engine.engine is engine.sync_engine)   # True
```

### `AsyncEngine.execution_options()` { #asyncengine-execution-options }

```python
AsyncEngine.execution_options(**opt)
```

**ধরন:** মেথড

নতুন একটি `AsyncEngine` দেয়, যা একই পুল শেয়ার করে কিন্তু প্রতিটি কানেকশনে দেওয়া execution option প্রয়োগ করে। যেমন isolation level আলাদা একটি engine।

**উদাহরণ:**

```python
serializable = engine.execution_options(isolation_level="SERIALIZABLE")
async with serializable.connect() as conn:
    print(await conn.get_isolation_level())   # SERIALIZABLE
```

### `AsyncEngine.get_execution_options()` { #asyncengine-get-execution-options }

```python
AsyncEngine.get_execution_options()
```

**ধরন:** মেথড

এই engine-এর বর্তমান execution option-গুলো দেয়।

**উদাহরণ:**

```python
print(engine.execution_options(isolation_level="AUTOCOMMIT").get_execution_options())
# immutabledict({'isolation_level': 'AUTOCOMMIT'})
```

### `AsyncEngine.name` { #asyncengine-name }

**ধরন:** প্রপার্টি

ডায়ালেক্টের নাম।

**উদাহরণ:**

```python
print(engine.name)   # postgresql
```

### `AsyncEngine.pool` { #asyncengine-pool }

**ধরন:** প্রপার্টি

ভেতরের কানেকশন পুল অবজেক্ট। `engine.pool.status()` দিয়ে পুলের অবস্থা দেখা যায়।

**উদাহরণ:**

```python
print(type(engine.pool).__name__)   # AsyncAdaptedQueuePool
print(engine.pool.status())
```

### `AsyncEngine.raw_connection()` { #asyncengine-raw-connection }

```python
await AsyncEngine.raw_connection()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

পুল থেকে একটি "কাঁচা" DBAPI কানেকশন (মোড়কসহ) দেয়, SQLAlchemy-র ট্রানজ্যাকশন ব্যবস্থার বাইরে। কাজ শেষে `close()` করে পুলে ফেরত দিন।

**উদাহরণ:**

```python
raw = await engine.raw_connection()
print(type(raw.driver_connection).__name__)   # Connection (asyncpg)
raw.close()
```

### `AsyncEngine.sync_engine` { #asyncengine-sync-engine }

**ধরন:** অ্যাট্রিবিউট

ভেতরের আসল sync `Engine`। event listener যুক্ত করতে এটি লাগে: `event.listen(engine.sync_engine, "before_cursor_execute", fn)`।

**উদাহরণ:**

```python
print(type(engine.sync_engine).__name__)   # Engine
```

### `AsyncEngine.update_execution_options()` { #asyncengine-update-execution-options }

```python
AsyncEngine.update_execution_options(**opt)
```

**ধরন:** মেথড

এই engine-এর ডিফল্ট execution option জায়গায় বদলায় (নতুন engine বানায় না)।

**উদাহরণ:**

```python
engine.update_execution_options(compiled_cache=None)
```

### `AsyncEngine.url` { #asyncengine-url }

**ধরন:** প্রপার্টি

engine-এর ডেটাবেস URL (`URL` অবজেক্ট)। পাসওয়ার্ড লুকিয়ে দেখায়।

**উদাহরণ:**

```python
print(engine.url.database, engine.url.drivername)   # apiref postgresql+asyncpg
```

## `AsyncConnection` { #asyncconnection }

```python
from sqlalchemy.ext.asyncio import AsyncConnection
```

sync `Connection`-এর async মোড়ক: ডেটাবেসের সাথে একটি কানেকশন। Core স্টেটমেন্ট আর raw SQL চালাতে, বা `run_sync()` দিয়ে `create_all`-এর মতো sync কাজ চালাতে ব্যবহার হয়। ORM-এর জন্য সাধারণত `AsyncSession` ভালো।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    result = await conn.execute(select(User.__table__.c.name).order_by(User.__table__.c.id))
    print(result.scalars().all())   # ['রহিম', 'করিম', 'সুমি']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncconnection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`aclose()`](#asyncconnection-aclose) | মেথড (async) | `close()`-এর আরেক নাম, যাতে `contextlib.aclosing()` দিয়ে ব্যবহার করা যায়। |
| [`begin()`](#asyncconnection-begin) | মেথড | স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে `AsyncTransaction` দেয়। |
| [`begin_nested()`](#asyncconnection-begin-nested) | মেথড | একটি SAVEPOINT শুরু করে। |
| [`close()`](#asyncconnection-close) | মেথড (async) | কানেকশন বন্ধ করে পুলে ফেরত দেয়; চলমান ট্রানজ্যাকশন rollback হয়। |
| [`closed`](#asyncconnection-closed) | প্রপার্টি | কানেকশন বন্ধ হলে `True`। |
| [`commit()`](#asyncconnection-commit) | মেথড (async) | চলমান ট্রানজ্যাকশন commit করে ("commit as you go")। |
| [`connection`](#asyncconnection-connection) | প্রপার্টি | async-এ এটি ব্যবহার করা যায় না, ডাকলে এরর দেয়। |
| [`default_isolation_level`](#asyncconnection-default-isolation-level) | প্রপার্টি | কানেকশন খোলার সময় ডেটাবেসের ডিফল্ট isolation level। |
| [`dialect`](#asyncconnection-dialect) | প্রপার্টি | এই কানেকশনের ডায়ালেক্ট। |
| [`engine`](#asyncconnection-engine) | অ্যাট্রিবিউট | যে `AsyncEngine` থেকে কানেকশনটি এসেছে। |
| [`exec_driver_sql()`](#asyncconnection-exec-driver-sql) | মেথড (async) | ড্রাইভারের নিজস্ব ভাষায় (প্যারামিটার চিহ্নসহ, যেমন asyncpg-এ `$1`) লেখা SQL সরাসরি চালায়। |
| [`execute()`](#asyncconnection-execute) | মেথড (async) | Core স্টেটমেন্ট বা `text()` চালিয়ে একটি buffered `Result` দেয় (সব রো আগেই মেমরিতে)। |
| [`execution_options()`](#asyncconnection-execution-options) | মেথড (async) | এই কানেকশনের execution option বদলায় (যেমন isolation level), আর একই কানেকশন ফেরত দেয়। |
| [`get_isolation_level()`](#asyncconnection-get-isolation-level) | মেথড (async) | কানেকশনের বর্তমান isolation level ডেটাবেস থেকে পড়ে দেয়। |
| [`get_nested_transaction()`](#asyncconnection-get-nested-transaction) | মেথড | চলমান SAVEPOINT-এর `AsyncTransaction`, না থাকলে `None`। |
| [`get_raw_connection()`](#asyncconnection-get-raw-connection) | মেথড (async) | এই কানেকশনের পেছনের পুল-মোড়কসহ DBAPI কানেকশন দেয়। |
| [`get_transaction()`](#asyncconnection-get-transaction) | মেথড | চলমান মূল ট্রানজ্যাকশনের `AsyncTransaction`, না থাকলে `None`। |
| [`in_nested_transaction()`](#asyncconnection-in-nested-transaction) | মেথড | SAVEPOINT চললে `True`। |
| [`in_transaction()`](#asyncconnection-in-transaction) | মেথড | কোনো ট্রানজ্যাকশন চললে `True`। |
| [`info`](#asyncconnection-info) | প্রপার্টি | কানেকশনের সাথে নিজের তথ্য রাখার dict। |
| [`invalidate()`](#asyncconnection-invalidate) | মেথড (async) | ভেতরের DBAPI কানেকশন "অকেজো" ঘোষণা করে ফেলে দেয়; পরের ব্যবহারে নতুন কানেকশন আসে। |
| [`invalidated`](#asyncconnection-invalidated) | প্রপার্টি | কানেকশন invalidate করা হলে `True`। |
| [`rollback()`](#asyncconnection-rollback) | মেথড (async) | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`run_sync()`](#asyncconnection-run-sync) | মেথড (async) | একটি sync ফাংশন চালায়, প্রথম আর্গুমেন্ট হিসেবে sync `Connection` দিয়ে। |
| [`scalar()`](#asyncconnection-scalar) | মেথড (async) | স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম মান দেয়। |
| [`scalars()`](#asyncconnection-scalars) | মেথড (async) | স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলামের `ScalarResult` দেয়। |
| [`start()`](#asyncconnection-start) | মেথড (async) | `async with` ছাড়া কানেকশন চালু করতে: `conn = await engine.connect().start()`। |
| [`stream()`](#asyncconnection-stream) | মেথড | server-side cursor দিয়ে ফলাফল স্ট্রিম করে একটি `AsyncResult` দেয়; রো একটু একটু করে আসে। |
| [`stream_scalars()`](#asyncconnection-stream-scalars) | মেথড | `stream()`-এর মতো, কিন্তু প্রতিটি রো-র প্রথম কলাম দিয়ে `AsyncScalarResult` দেয়। |
| [`sync_connection`](#asyncconnection-sync-connection) | অ্যাট্রিবিউট | ভেতরের আসল sync `Connection` (চালু থাকলে)। |
| [`sync_engine`](#asyncconnection-sync-engine) | অ্যাট্রিবিউট | ভেতরের sync `Engine`। |

### `AsyncConnection.aclose()` { #asyncconnection-aclose }

```python
await AsyncConnection.aclose()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`close()`-এর আরেক নাম, যাতে `contextlib.aclosing()` দিয়ে ব্যবহার করা যায়।

**উদাহরণ:**

```python
conn = await engine.connect().start()
await conn.aclose()
```

### `AsyncConnection.begin()` { #asyncconnection-begin }

```python
AsyncConnection.begin()
```

**ধরন:** মেথড

স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে `AsyncTransaction` দেয়। `async with conn.begin():` লিখলে শেষে নিজেই commit/rollback।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    async with conn.begin():
        await conn.execute(text("UPDATE users SET name = 'রহিম' WHERE id = 1"))
```

### `AsyncConnection.begin_nested()` { #asyncconnection-begin-nested }

```python
AsyncConnection.begin_nested()
```

**ধরন:** মেথড

একটি SAVEPOINT শুরু করে। ভেতরের অংশ বাতিল হলেও বাইরের ট্রানজ্যাকশন চলে।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    sp = await conn.begin_nested()
    await conn.execute(text("DELETE FROM addresses"))
    await sp.rollback()                 # শুধু SAVEPOINT পর্যন্ত ফেরে
    print(await conn.scalar(text("SELECT count(*) FROM addresses")))   # 1
```

### `AsyncConnection.close()` { #asyncconnection-close }

```python
await AsyncConnection.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কানেকশন বন্ধ করে পুলে ফেরত দেয়; চলমান ট্রানজ্যাকশন rollback হয়।

**উদাহরণ:**

```python
conn = await engine.connect().start()
await conn.close()
print(conn.closed)   # True
```

### `AsyncConnection.closed` { #asyncconnection-closed }

**ধরন:** প্রপার্টি

কানেকশন বন্ধ হলে `True`।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.closed)   # False
```

### `AsyncConnection.commit()` { #asyncconnection-commit }

```python
await AsyncConnection.commit()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

চলমান ট্রানজ্যাকশন commit করে ("commit as you go")।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    await conn.execute(text("UPDATE users SET name = 'করিম' WHERE id = 2"))
    await conn.commit()
```

### `AsyncConnection.connection` { #asyncconnection-connection }

**ধরন:** প্রপার্টি

async-এ এটি ব্যবহার করা যায় না, ডাকলে এরর দেয়। কাঁচা DBAPI কানেকশন চাইলে `await conn.get_raw_connection()` ব্যবহার করুন।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    raw = await conn.get_raw_connection()
```

### `AsyncConnection.default_isolation_level` { #asyncconnection-default-isolation-level }

**ধরন:** প্রপার্টি

কানেকশন খোলার সময় ডেটাবেসের ডিফল্ট isolation level।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.default_isolation_level)   # READ COMMITTED
```

### `AsyncConnection.dialect` { #asyncconnection-dialect }

**ধরন:** প্রপার্টি

এই কানেকশনের ডায়ালেক্ট।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.dialect.name)   # postgresql
```

### `AsyncConnection.engine` { #asyncconnection-engine }

**ধরন:** অ্যাট্রিবিউট

যে `AsyncEngine` থেকে কানেকশনটি এসেছে।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.engine is engine)   # True
```

### `AsyncConnection.exec_driver_sql()` { #asyncconnection-exec-driver-sql }

```python
await AsyncConnection.exec_driver_sql(statement, parameters=None, execution_options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ড্রাইভারের নিজস্ব ভাষায় (প্যারামিটার চিহ্নসহ, যেমন asyncpg-এ `$1`) লেখা SQL সরাসরি চালায়। `text()`-এর মতো রূপান্তর হয় না।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    result = await conn.exec_driver_sql("SELECT name FROM users WHERE id = $1", (2,))
    print(result.scalar())   # করিম
```

### `AsyncConnection.execute()` { #asyncconnection-execute }

```python
await AsyncConnection.execute(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

Core স্টেটমেন্ট বা `text()` চালিয়ে একটি buffered `Result` দেয় (সব রো আগেই মেমরিতে)। প্যারামিটার dict বা dict-এর তালিকা।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    result = await conn.execute(text("SELECT id, name FROM users WHERE id < :n ORDER BY id"), {"n": 3})
    print(result.all())   # [(1, 'রহিম'), (2, 'করিম')]
```

### `AsyncConnection.execution_options()` { #asyncconnection-execution-options }

```python
await AsyncConnection.execution_options(**opt)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

এই কানেকশনের execution option বদলায় (যেমন isolation level), আর একই কানেকশন ফেরত দেয়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    await conn.execution_options(isolation_level="REPEATABLE READ")
    print(await conn.get_isolation_level())   # REPEATABLE READ
```

### `AsyncConnection.get_isolation_level()` { #asyncconnection-get-isolation-level }

```python
await AsyncConnection.get_isolation_level()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কানেকশনের বর্তমান isolation level ডেটাবেস থেকে পড়ে দেয়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(await conn.get_isolation_level())   # READ COMMITTED
```

### `AsyncConnection.get_nested_transaction()` { #asyncconnection-get-nested-transaction }

```python
AsyncConnection.get_nested_transaction()
```

**ধরন:** মেথড

চলমান SAVEPOINT-এর `AsyncTransaction`, না থাকলে `None`।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    sp = await conn.begin_nested()
    print(conn.get_nested_transaction() is not None)   # True
    await sp.rollback()
```

### `AsyncConnection.get_raw_connection()` { #asyncconnection-get-raw-connection }

```python
await AsyncConnection.get_raw_connection()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

এই কানেকশনের পেছনের পুল-মোড়কসহ DBAPI কানেকশন দেয়। `driver_connection` দিয়ে আসল asyncpg কানেকশন পাওয়া যায় (যেমন `COPY`-এর জন্য)।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    raw = await conn.get_raw_connection()
    print(await raw.driver_connection.fetchval("SELECT 40 + 2"))   # 42
```

### `AsyncConnection.get_transaction()` { #asyncconnection-get-transaction }

```python
AsyncConnection.get_transaction()
```

**ধরন:** মেথড

চলমান মূল ট্রানজ্যাকশনের `AsyncTransaction`, না থাকলে `None`।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    print(conn.get_transaction() is not None)   # True
```

### `AsyncConnection.in_nested_transaction()` { #asyncconnection-in-nested-transaction }

```python
AsyncConnection.in_nested_transaction()
```

**ধরন:** মেথড

SAVEPOINT চললে `True`।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    print(conn.in_nested_transaction())   # False
```

### `AsyncConnection.in_transaction()` { #asyncconnection-in-transaction }

```python
AsyncConnection.in_transaction()
```

**ধরন:** মেথড

কোনো ট্রানজ্যাকশন চললে `True`।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.in_transaction())          # False
    await conn.execute(text("SELECT 1"))  # autobegin
    print(conn.in_transaction())          # True
```

### `AsyncConnection.info` { #asyncconnection-info }

**ধরন:** প্রপার্টি

কানেকশনের সাথে নিজের তথ্য রাখার dict। এই dict পুলের আসল DBAPI কানেকশনের সাথে থাকে, তাই কানেকশন পুলে ফেরত গেলেও থেকে যায়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    conn.info["tenant"] = "t1"
    print(conn.info["tenant"])
```

### `AsyncConnection.invalidate()` { #asyncconnection-invalidate }

```python
await AsyncConnection.invalidate(exception=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ভেতরের DBAPI কানেকশন "অকেজো" ঘোষণা করে ফেলে দেয়; পরের ব্যবহারে নতুন কানেকশন আসে।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    await conn.invalidate()
    print(conn.invalidated)   # True
```

### `AsyncConnection.invalidated` { #asyncconnection-invalidated }

**ধরন:** প্রপার্টি

কানেকশন invalidate করা হলে `True`।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.invalidated)   # False
```

### `AsyncConnection.rollback()` { #asyncconnection-rollback }

```python
await AsyncConnection.rollback()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

চলমান ট্রানজ্যাকশন বাতিল করে।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    await conn.execute(text("DELETE FROM addresses"))
    await conn.rollback()
```

### `AsyncConnection.run_sync()` { #asyncconnection-run-sync }

```python
await AsyncConnection.run_sync(fn, *arg, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

একটি sync ফাংশন চালায়, প্রথম আর্গুমেন্ট হিসেবে sync `Connection` দিয়ে। `Base.metadata.create_all`, `inspect()` বা পুরোনো sync হেল্পার async কোড থেকে চালাতে এটাই উপায়।

**উদাহরণ:**

```python
from sqlalchemy import inspect
async with engine.connect() as conn:
    tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    print(sorted(tables))   # ['addresses', 'users']
```

### `AsyncConnection.scalar()` { #asyncconnection-scalar }

```python
await AsyncConnection.scalar(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম মান দেয়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(await conn.scalar(text("SELECT count(*) FROM users")))   # 3
```

### `AsyncConnection.scalars()` { #asyncconnection-scalars }

```python
await AsyncConnection.scalars(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলামের `ScalarResult` দেয়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print((await conn.scalars(text("SELECT id FROM users ORDER BY id"))).all())   # [1, 2, 3]
```

### `AsyncConnection.start()` { #asyncconnection-start }

```python
await AsyncConnection.start(is_ctxmanager=False)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`async with` ছাড়া কানেকশন চালু করতে: `conn = await engine.connect().start()`। পরে নিজে `await conn.close()` করতে হবে।

**উদাহরণ:**

```python
conn = await engine.connect().start()
print(await conn.scalar(text("SELECT 1")))   # 1
await conn.close()
```

### `AsyncConnection.stream()` { #asyncconnection-stream }

```python
AsyncConnection.stream(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড

server-side cursor দিয়ে ফলাফল স্ট্রিম করে একটি `AsyncResult` দেয়; রো একটু একটু করে আসে। লাখ রো-র এক্সপোর্টে কাজে লাগে। ট্রানজ্যাকশনের ভেতরে ব্যবহার করুন।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    result = await conn.stream(text("SELECT id FROM users ORDER BY id"))
    async for row in result:
        print(row.id)
```

### `AsyncConnection.stream_scalars()` { #asyncconnection-stream-scalars }

```python
AsyncConnection.stream_scalars(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড

`stream()`-এর মতো, কিন্তু প্রতিটি রো-র প্রথম কলাম দিয়ে `AsyncScalarResult` দেয়।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    result = await conn.stream_scalars(text("SELECT name FROM users ORDER BY id"))
    print([n async for n in result])   # ['রহিম', 'করিম', 'সুমি']
```

### `AsyncConnection.sync_connection` { #asyncconnection-sync-connection }

**ধরন:** অ্যাট্রিবিউট

ভেতরের আসল sync `Connection` (চালু থাকলে)।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(type(conn.sync_connection).__name__)   # Connection
```

### `AsyncConnection.sync_engine` { #asyncconnection-sync-engine }

**ধরন:** অ্যাট্রিবিউট

ভেতরের sync `Engine`।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    print(conn.sync_engine is engine.sync_engine)   # True
```

## `AsyncTransaction` { #asynctransaction }

```python
from sqlalchemy.ext.asyncio import AsyncTransaction
```

`AsyncConnection.begin()` / `begin_nested()` থেকে পাওয়া Core ট্রানজ্যাকশন।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    await conn.execute(text("UPDATE users SET name = 'সুমি' WHERE id = 3"))
    await trans.commit()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asynctransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#asynctransaction-close) | মেথড (async) | ট্রানজ্যাকশন বন্ধ করে; commit না হলে rollback হয়। |
| [`commit()`](#asynctransaction-commit) | মেথড (async) | ট্রানজ্যাকশন commit করে (নেস্টেড হলে SAVEPOINT release)। |
| [`connection`](#asynctransaction-connection) | অ্যাট্রিবিউট | যে `AsyncConnection`-এ ট্রানজ্যাকশনটি চলছে। |
| [`is_active`](#asynctransaction-is-active) | প্রপার্টি | ট্রানজ্যাকশন এখনো চালু থাকলে `True`। |
| [`is_valid`](#asynctransaction-is-valid) | প্রপার্টি | ট্রানজ্যাকশন আর তার কানেকশন দুটোই ঠিক থাকলে `True` (কানেকশন invalidate হলে `False`)। |
| [`nested`](#asynctransaction-nested) | অ্যাট্রিবিউট | SAVEPOINT হলে `True`। |
| [`rollback()`](#asynctransaction-rollback) | মেথড (async) | ট্রানজ্যাকশন বাতিল করে। |
| [`start()`](#asynctransaction-start) | মেথড (async) | `async with` ছাড়া ট্রানজ্যাকশন শুরু করতে: `trans = await conn.begin().start()`। |
| [`sync_transaction`](#asynctransaction-sync-transaction) | অ্যাট্রিবিউট | ভেতরের sync `Transaction` অবজেক্ট। |

### `AsyncTransaction.close()` { #asynctransaction-close }

```python
await AsyncTransaction.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ট্রানজ্যাকশন বন্ধ করে; commit না হলে rollback হয়।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    await trans.close()
    print(trans.is_active)   # False
```

### `AsyncTransaction.commit()` { #asynctransaction-commit }

```python
await AsyncTransaction.commit()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ট্রানজ্যাকশন commit করে (নেস্টেড হলে SAVEPOINT release)।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    await trans.commit()
```

### `AsyncTransaction.connection` { #asynctransaction-connection }

**ধরন:** অ্যাট্রিবিউট

যে `AsyncConnection`-এ ট্রানজ্যাকশনটি চলছে।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    print(trans.connection is conn)   # True
    await trans.rollback()
```

### `AsyncTransaction.is_active` { #asynctransaction-is-active }

**ধরন:** প্রপার্টি

ট্রানজ্যাকশন এখনো চালু থাকলে `True`।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    print(trans.is_active)   # True
    await trans.rollback()
```

### `AsyncTransaction.is_valid` { #asynctransaction-is-valid }

**ধরন:** প্রপার্টি

ট্রানজ্যাকশন আর তার কানেকশন দুটোই ঠিক থাকলে `True` (কানেকশন invalidate হলে `False`)।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    print(trans.is_valid)   # True
    await trans.rollback()
```

### `AsyncTransaction.nested` { #asynctransaction-nested }

**ধরন:** অ্যাট্রিবিউট

SAVEPOINT হলে `True`।

**উদাহরণ:**

```python
async with engine.begin() as conn:
    sp = await conn.begin_nested()
    print(sp.nested)   # True
    await sp.rollback()
```

### `AsyncTransaction.rollback()` { #asynctransaction-rollback }

```python
await AsyncTransaction.rollback()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ট্রানজ্যাকশন বাতিল করে।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    await conn.execute(text("DELETE FROM addresses"))
    await trans.rollback()
```

### `AsyncTransaction.start()` { #asynctransaction-start }

```python
await AsyncTransaction.start(is_ctxmanager=False)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`async with` ছাড়া ট্রানজ্যাকশন শুরু করতে: `trans = await conn.begin().start()`। সাধারণত `await conn.begin()` লিখলেই যথেষ্ট।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin().start()
    await trans.rollback()
```

### `AsyncTransaction.sync_transaction` { #asynctransaction-sync-transaction }

**ধরন:** অ্যাট্রিবিউট

ভেতরের sync `Transaction` অবজেক্ট।

**উদাহরণ:**

```python
async with engine.connect() as conn:
    trans = await conn.begin()
    print(type(trans.sync_transaction).__name__)   # RootTransaction
    await trans.rollback()
```

## `async_sessionmaker` { #async-sessionmaker }

```python
from sqlalchemy.ext.asyncio import async_sessionmaker
```

`AsyncSession`-এর কারখানা, `sessionmaker`-এর async রূপ। FastAPI অ্যাপে সাধারণত `core/database.py`-তে একবার বানানো হয়, আর `get_db` ডিপেন্ডেন্সি প্রতি রিকোয়েস্টে এখান থেকে নতুন সেশন নেয়।

**উদাহরণ:**

```python
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
async with SessionLocal() as s:
    print((await s.get(User, 1)).name)   # রহিম
```

### কনস্ট্রাক্টরের প্যারামিটার { #async-sessionmaker-params }

```python
async_sessionmaker(bind=None, *, class_=<class 'sqlalchemy.ext.asyncio.session.AsyncSession'>, autoflush=True, expire_on_commit=True, info=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bind` | নতুন সেশনগুলো কোন `AsyncEngine`-এ যুক্ত হবে। |
| `class_` | কোন ক্লাস বানাবে, ডিফল্ট `AsyncSession`। |
| `autoflush` | নতুন সেশনের `autoflush`। |
| `expire_on_commit` | নতুন সেশনের `expire_on_commit`। async-এ প্রায় সবসময় `False` দিন। |
| `info` | নতুন প্রতিটি সেশনের `info` dict। |
| `kw` | বাকি যেকোনো সেশন প্যারামিটার (যেমন `sync_session_class`, `join_transaction_mode`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #async-sessionmaker-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`begin()`](#async-sessionmaker-begin) | মেথড | নতুন সেশন আর সাথে ট্রানজ্যাকশন দেয়; `async with` শেষে commit (এরর হলে rollback), তারপর সেশন বন্ধ। |
| [`configure()`](#async-sessionmaker-configure) | মেথড | কারখানার সেটিং পরে বদলায়। |

### `async_sessionmaker.begin()` { #async-sessionmaker-begin }

```python
async_sessionmaker.begin()
```

**ধরন:** মেথড

নতুন সেশন আর সাথে ট্রানজ্যাকশন দেয়; `async with` শেষে commit (এরর হলে rollback), তারপর সেশন বন্ধ।

**উদাহরণ:**

```python
async with SessionLocal.begin() as s:
    s.add(User(name="এক ধাপে"))
# commit + close হয়ে গেছে
```

### `async_sessionmaker.configure()` { #async-sessionmaker-configure }

```python
async_sessionmaker.configure(**new_kw)
```

**ধরন:** মেথড

কারখানার সেটিং পরে বদলায়।

**উদাহরণ:**

```python
maker = async_sessionmaker()
maker.configure(bind=engine)
async with maker() as s:
    print((await s.get(User, 2)).name)   # করিম
```

## `AsyncSession` { #asyncsession }

```python
from sqlalchemy.ext.asyncio import AsyncSession
```

`Session`-এর async রূপ, আর FastAPI-তে সবচেয়ে বেশি ব্যবহৃত ক্লাস। ভেতরে একটি সাধারণ `Session` (`sync_session`) চলে; ডেটাবেসে যেতে হয় এমন প্রতিটি মেথড এখানে coroutine, তাই `await` লাগে। `add()`, `add_all()`, `expunge()`, `new`, `dirty` জাতীয় কাজ, যেগুলো ডেটাবেসে যায় না, সেগুলো `await` ছাড়াই।

async-এর তিন নিয়ম: `expire_on_commit=False`, রিলেশনশিপ আগেভাগে লোড (`selectinload`), আর একটি সেশন একসাথে একাধিক কাজে (`asyncio.gather`) নয়। বিস্তারিত: [MissingGreenlet](../engine-session.md#s20)।

**উদাহরণ:**

```python
async with SessionLocal() as s:
    s.add(User(name="আসিফ"))
    await s.commit()
    users = (await s.scalars(select(User).options(selectinload(User.addresses)).order_by(User.id))).all()
    print([(u.name, len(u.addresses)) for u in users])
```

### কনস্ট্রাক্টরের প্যারামিটার { #asyncsession-params }

```python
AsyncSession(bind=None, *, binds=None, sync_session_class=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bind` | যে `AsyncEngine` বা `AsyncConnection`-এ সেশন যুক্ত। |
| `binds` | মডেল/টেবিল অনুযায়ী আলাদা async engine-এর dict। |
| `sync_session_class` | ভেতরে কোন sync `Session` ক্লাস চলবে। নিজের `Session` সাবক্লাস (যেমন কাস্টম `get_bind()` দিয়ে read replica রাউটিং) দিতে এটি ব্যবহার করুন। |
| `kw` | বাকি সব `Session` প্যারামিটার (`expire_on_commit`, `autoflush`, `info` …), যা ভেতরের sync সেশনে যায়। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncsession-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`aclose()`](#asyncsession-aclose) | মেথড (async) | `close()`-এর আরেক নাম (`contextlib.aclosing()`-এর জন্য)। |
| [`add()`](#asyncsession-add) | মেথড | একটি অবজেক্টকে সেশনে যোগ করে। |
| [`add_all()`](#asyncsession-add-all) | মেথড | অনেকগুলো অবজেক্ট একসাথে সেশনে যোগ করে, প্রতিটির জন্য `add()` ডাকার সমান। |
| [`autoflush`](#asyncsession-autoflush) | প্রপার্টি | ভেতরের সেশনের `autoflush` সেটিং (পড়া ও বদলানো যায়)। |
| [`begin()`](#asyncsession-begin) | মেথড | স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে আর একটি `SessionTransaction` দেয়। |
| [`begin_nested()`](#asyncsession-begin-nested) | মেথড | চলমান ট্রানজ্যাকশনের ভেতরে একটি "নেস্টেড" ট্রানজ্যাকশন, মানে ডেটাবেসে `SAVEPOINT`, শুরু করে। |
| [`bind`](#asyncsession-bind) | প্রপার্টি | সেশনটি কোন `AsyncEngine`/`AsyncConnection`-এ যুক্ত। |
| [`bind_mapper()`](#asyncsession-bind-mapper) | মেথড | একটি নির্দিষ্ট মডেলের সব কাজ কোন `Engine`-এ যাবে তা ঠিক করে দেয়। |
| [`bind_table()`](#asyncsession-bind-table) | মেথড | `bind_mapper()`-এর মতো, তবে মডেলের বদলে একটি `Table`-এর জন্য Engine ঠিক করে। |
| [`binds`](#asyncsession-binds) | প্রপার্টি | মডেল/টেবিল-ভিত্তিক bind-এর অপরিবর্তনীয় dict। |
| [`close()`](#asyncsession-close) | মেথড (async) | সেশনের ট্রানজ্যাকশন শেষ (rollback) করে, কানেকশন পুলে ফেরত দেয়, আর সব অবজেক্টকে সেশন থেকে বিচ্ছিন্ন (detached) করে। |
| [`close_all()`](#asyncsession-close-all) | ক্লাস মেথড (async) | মেমরিতে থাকা সব `AsyncSession` বন্ধ করে (ক্লাস মেথড)। |
| [`commit()`](#asyncsession-commit) | মেথড (async) | জমা থাকা সব পরিবর্তন `flush()` করে, তারপর ডেটাবেসে `COMMIT` পাঠায়। |
| [`connection()`](#asyncsession-connection) | মেথড (async) | সেশনের চলমান ট্রানজ্যাকশনের সাথে যুক্ত Core `Connection` দেয়। |
| [`delete()`](#asyncsession-delete) | মেথড (async) | একটি অবজেক্টকে মোছার জন্য চিহ্নিত করে। |
| [`delete_all()`](#asyncsession-delete-all) | মেথড (async) | (২.১-এ নতুন) অনেকগুলো অবজেক্ট একসাথে মোছার জন্য চিহ্নিত করে, প্রতিটিতে `delete()` ডাকার সমান। |
| [`deleted`](#asyncsession-deleted) | প্রপার্টি | যে অবজেক্টগুলো `delete()` দিয়ে মোছার জন্য চিহ্নিত কিন্তু এখনো flush হয়নি, সেগুলোর সেট (set-এর মতো একটি কালেকশন)। |
| [`dirty`](#asyncsession-dirty) | প্রপার্টি | যে persistent অবজেক্টগুলোর কোনো অ্যাট্রিবিউট বদলানো হয়েছে, সেগুলোর সেট। |
| [`execute()`](#asyncsession-execute) | মেথড (async) | যেকোনো স্টেটমেন্ট (`select`, `insert`, `update`, `delete`, `text`) চালায় আর একটি `Result` দেয়। |
| [`execution_options`](#asyncsession-execution-options) | প্রপার্টি | (২.১-এ নতুন) কনস্ট্রাক্টরে দেওয়া ডিফল্ট execution option-গুলো, যা এই সেশনের প্রতিটি `execute()`-এ প্রয়োগ হয়। |
| [`expire()`](#asyncsession-expire) | মেথড | একটি অবজেক্টের সব (বা নির্দিষ্ট) অ্যাট্রিবিউটের মেমরিতে থাকা মান মুছে দেয়। |
| [`expire_all()`](#asyncsession-expire-all) | মেথড | সেশনের সব persistent অবজেক্টকে expire করে। |
| [`expunge()`](#asyncsession-expunge) | মেথড | একটি অবজেক্টকে সেশন থেকে সরিয়ে দেয় (detached করে)। |
| [`expunge_all()`](#asyncsession-expunge-all) | মেথড | সেশনের সব অবজেক্ট সরিয়ে identity map খালি করে। |
| [`flush()`](#asyncsession-flush) | মেথড (async) | জমা থাকা সব পরিবর্তনের SQL (INSERT/UPDATE/DELETE) এখনই ডেটাবেসে পাঠায়, কিন্তু commit করে না। |
| [`get()`](#asyncsession-get) | মেথড (async) | primary key দিয়ে একটি অবজেক্ট দেয়, না থাকলে `None`। |
| [`get_async_bind()`](#asyncsession-get-async-bind) | মেথড | একটি মডেল বা কুয়েরির জন্য সেশন কোন `AsyncEngine`/`AsyncConnection` ব্যবহার করবে তা দেয়। |
| [`get_bind()`](#asyncsession-get-bind) | মেথড | একটি কুয়েরি বা মডেলের জন্য সেশন কোন `Engine`/`Connection` ব্যবহার করবে তা বের করে দেয়। |
| [`get_nested_transaction()`](#asyncsession-get-nested-transaction) | মেথড | এখন কোনো নেস্টেড (SAVEPOINT) ট্রানজ্যাকশন চললে সেটার `SessionTransaction` দেয়, নইলে `None`। |
| [`get_one()`](#asyncsession-get-one) | মেথড (async) | `get()`-এর মতোই, কিন্তু রো না পেলে `None` না দিয়ে `NoResultFound` এরর দেয়। |
| [`get_transaction()`](#asyncsession-get-transaction) | মেথড | এখন যে মূল (root) ট্রানজ্যাকশন চলছে সেটার `SessionTransaction` দেয়, না থাকলে `None`। |
| [`identity_key()`](#asyncsession-identity-key) | ক্লাস মেথড | একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। |
| [`identity_map`](#asyncsession-identity-map) | প্রপার্টি | ভেতরের সেশনের identity map (লোড করা অবজেক্টের রেজিস্টার)। |
| [`in_nested_transaction()`](#asyncsession-in-nested-transaction) | মেথড | এখন কোনো SAVEPOINT চললে `True`। |
| [`in_transaction()`](#asyncsession-in-transaction) | মেথড | এখন কোনো ট্রানজ্যাকশন চললে `True`। |
| [`info`](#asyncsession-info) | প্রপার্টি | নিজের তথ্য রাখার একটি dict, যেমন রিকোয়েস্ট id বা বর্তমান ইউজার। |
| [`invalidate()`](#asyncsession-invalidate) | মেথড (async) | সেশন বন্ধ করে, আর ব্যবহৃত DBAPI কানেকশনগুলো "অকেজো" ঘোষণা করে পুলে ফেরত না দিয়ে ফেলে দেয়। |
| [`is_active`](#asyncsession-is-active) | প্রপার্টি | সেশন "আংশিক rollback" অবস্থায় না থাকলে `True`। |
| [`is_modified()`](#asyncsession-is-modified) | মেথড | অবজেক্টের কোনো অ্যাট্রিবিউটের মান আসলেই বদলেছে কি না দেখে `True`/`False` দেয়। |
| [`merge()`](#asyncsession-merge) | মেথড (async) | বাইরের একটি অবজেক্টের অবস্থা সেশনের ভেতরের সংশ্লিষ্ট অবজেক্টে কপি করে, আর সেই ভেতরের অবজেক্টটি ফেরত দেয়। |
| [`merge_all()`](#asyncsession-merge-all) | মেথড (async) | (২.১-এ নতুন) অনেক অবজেক্টে একসাথে `merge()` চালায় আর merge করা অবজেক্টগুলোর তালিকা দেয়। |
| [`new`](#asyncsession-new) | প্রপার্টি | যে নতুন অবজেক্টগুলো `add()` করা হয়েছে কিন্তু এখনো flush হয়নি (pending), সেগুলোর সেট। |
| [`no_autoflush`](#asyncsession-no-autoflush) | প্রপার্টি | একটি context manager, যার ভেতরে সাময়িকভাবে autoflush বন্ধ থাকে। |
| [`object_session()`](#asyncsession-object-session) | ক্লাস মেথড | একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। |
| [`refresh()`](#asyncsession-refresh) | মেথড (async) | অবজেক্টের মানগুলো এখনই ডেটাবেস থেকে আবার পড়ে আনে (একটি SELECT)। |
| [`reset()`](#asyncsession-reset) | মেথড (async) | সেশনকে একদম শুরুর অবস্থায় ফিরিয়ে নেয়: ট্রানজ্যাকশন বাতিল, সব অবজেক্ট বিচ্ছিন্ন, কানেকশন ফেরত। |
| [`rollback()`](#asyncsession-rollback) | মেথড (async) | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`run_sync()`](#asyncsession-run-sync) | মেথড (async) | একটি sync ফাংশন চালায়, প্রথম আর্গুমেন্ট হিসেবে ভেতরের sync `Session` দিয়ে, greenlet-এর ভেতরে। |
| [`scalar()`](#asyncsession-scalar) | মেথড (async) | একটি স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলামের মানটি দেয় (না থাকলে `None`)। |
| [`scalars()`](#asyncsession-scalars) | মেথড (async) | একটি স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলাম দিয়ে একটি `ScalarResult` দেয়। |
| [`stream()`](#asyncsession-stream) | মেথড (async) | ORM কুয়েরি স্ট্রিম করে `AsyncResult` দেয়; রো টুকরো করে আসে, সব একসাথে মেমরিতে নয়। |
| [`stream_scalars()`](#asyncsession-stream-scalars) | মেথড (async) | `stream()`-এর মতো, কিন্তু প্রতিটি রো-র প্রথম কলাম, মানে সাধারণত ORM অবজেক্ট, দেয়। |
| [`sync_session_class`](#asyncsession-sync-session-class) | অ্যাট্রিবিউট | ভেতরে কোন sync `Session` ক্লাস চলছে (ডিফল্ট `Session`)। |

### `AsyncSession.aclose()` { #asyncsession-aclose }

```python
await AsyncSession.aclose()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`close()`-এর আরেক নাম (`contextlib.aclosing()`-এর জন্য)।

**উদাহরণ:**

```python
s = SessionLocal()
await s.get(User, 1)
await s.aclose()
```

### `AsyncSession.add()` { #asyncsession-add }

```python
AsyncSession.add(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add`](session.md#session-add)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.add_all()` { #asyncsession-add-all }

```python
AsyncSession.add_all(instances)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add_all`](session.md#session-add-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.autoflush` { #asyncsession-autoflush }

**ধরন:** প্রপার্টি

ভেতরের সেশনের `autoflush` সেটিং (পড়া ও বদলানো যায়)।

**উদাহরণ:**

```python
print(session.autoflush)   # True
```

### `AsyncSession.begin()` { #asyncsession-begin }

```python
AsyncSession.begin()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin`](session.md#session-begin)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.begin_nested()` { #asyncsession-begin-nested }

```python
AsyncSession.begin_nested()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin_nested`](session.md#session-begin-nested)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.bind` { #asyncsession-bind }

**ধরন:** প্রপার্টি

সেশনটি কোন `AsyncEngine`/`AsyncConnection`-এ যুক্ত।

**উদাহরণ:**

```python
print(session.bind is engine)   # True
```

### `AsyncSession.bind_mapper()` { #asyncsession-bind-mapper }

```python
AsyncSession.bind_mapper(mapper, bind)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.bind_mapper`](session.md#session-bind-mapper)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.bind_table()` { #asyncsession-bind-table }

```python
AsyncSession.bind_table(table, bind)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.bind_table`](session.md#session-bind-table)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.binds` { #asyncsession-binds }

**ধরন:** প্রপার্টি

মডেল/টেবিল-ভিত্তিক bind-এর অপরিবর্তনীয় dict।

**উদাহরণ:**

```python
print(dict(session.binds))   # {}
```

### `AsyncSession.close()` { #asyncsession-close }

```python
await AsyncSession.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.close`](session.md#session-close)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.close_all()` { #asyncsession-close-all }

```python
await AsyncSession.close_all()
```

**ধরন:** ক্লাস মেথড (async) · কল করার সময় `await` লাগবে

মেমরিতে থাকা সব `AsyncSession` বন্ধ করে (ক্লাস মেথড)।

**উদাহরণ:**

```python
await AsyncSession.close_all()
```

### `AsyncSession.commit()` { #asyncsession-commit }

```python
await AsyncSession.commit()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.commit`](session.md#session-commit)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.connection()` { #asyncsession-connection }

```python
await AsyncSession.connection(bind_arguments=None, execution_options=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.connection`](session.md#session-connection)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.delete()` { #asyncsession-delete }

```python
await AsyncSession.delete(instance)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.delete`](session.md#session-delete)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.delete_all()` { #asyncsession-delete-all }

```python
await AsyncSession.delete_all(instances)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.delete_all`](session.md#session-delete-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.deleted` { #asyncsession-deleted }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.deleted`](session.md#session-deleted)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.dirty` { #asyncsession-dirty }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.dirty`](session.md#session-dirty)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.execute()` { #asyncsession-execute }

```python
await AsyncSession.execute(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.execute`](session.md#session-execute)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.execution_options` { #asyncsession-execution-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.execution_options`](session.md#session-execution-options)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.expire()` { #asyncsession-expire }

```python
AsyncSession.expire(instance, attribute_names=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire`](session.md#session-expire)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.expire_all()` { #asyncsession-expire-all }

```python
AsyncSession.expire_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire_all`](session.md#session-expire-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.expunge()` { #asyncsession-expunge }

```python
AsyncSession.expunge(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge`](session.md#session-expunge)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.expunge_all()` { #asyncsession-expunge-all }

```python
AsyncSession.expunge_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge_all`](session.md#session-expunge-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.flush()` { #asyncsession-flush }

```python
await AsyncSession.flush(objects=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.flush`](session.md#session-flush)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.get()` { #asyncsession-get }

```python
await AsyncSession.get(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={})
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.get`](session.md#session-get)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.get_async_bind()` { #asyncsession-get-async-bind }

```python
AsyncSession.get_async_bind(mapper=None, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

একটি মডেল বা কুয়েরির জন্য সেশন কোন `AsyncEngine`/`AsyncConnection` ব্যবহার করবে তা দেয়।

**উদাহরণ:**

```python
print(session.get_async_bind(User) is engine)   # True
```

### `AsyncSession.get_bind()` { #asyncsession-get-bind }

```python
AsyncSession.get_bind(mapper=None, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_bind`](session.md#session-get-bind)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.get_nested_transaction()` { #asyncsession-get-nested-transaction }

```python
AsyncSession.get_nested_transaction()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_nested_transaction`](session.md#session-get-nested-transaction)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.get_one()` { #asyncsession-get-one }

```python
await AsyncSession.get_one(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={})
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.get_one`](session.md#session-get-one)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.get_transaction()` { #asyncsession-get-transaction }

```python
AsyncSession.get_transaction()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_transaction`](session.md#session-get-transaction)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.identity_key()` { #asyncsession-identity-key }

```python
AsyncSession.identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.identity_key`](session.md#session-identity-key)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.identity_map` { #asyncsession-identity-map }

**ধরন:** প্রপার্টি

ভেতরের সেশনের identity map (লোড করা অবজেক্টের রেজিস্টার)।

**উদাহরণ:**

```python
user = await session.get(User, 1)
print(len(session.identity_map))   # 1
```

### `AsyncSession.in_nested_transaction()` { #asyncsession-in-nested-transaction }

```python
AsyncSession.in_nested_transaction()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.in_nested_transaction`](session.md#session-in-nested-transaction)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.in_transaction()` { #asyncsession-in-transaction }

```python
AsyncSession.in_transaction()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.in_transaction`](session.md#session-in-transaction)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.info` { #asyncsession-info }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.info`](session.md#session-info)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.invalidate()` { #asyncsession-invalidate }

```python
await AsyncSession.invalidate()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.invalidate`](session.md#session-invalidate)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.is_active` { #asyncsession-is-active }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.is_active`](session.md#session-is-active)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.is_modified()` { #asyncsession-is-modified }

```python
AsyncSession.is_modified(instance, include_collections=True)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.is_modified`](session.md#session-is-modified)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.merge()` { #asyncsession-merge }

```python
await AsyncSession.merge(instance, *, load=True, options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.merge`](session.md#session-merge)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.merge_all()` { #asyncsession-merge-all }

```python
await AsyncSession.merge_all(instances, *, load=True, options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.merge_all`](session.md#session-merge-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.new` { #asyncsession-new }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.new`](session.md#session-new)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.no_autoflush` { #asyncsession-no-autoflush }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.no_autoflush`](session.md#session-no-autoflush)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.object_session()` { #asyncsession-object-session }

```python
AsyncSession.object_session(instance)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.object_session`](session.md#session-object-session)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.refresh()` { #asyncsession-refresh }

```python
await AsyncSession.refresh(instance, attribute_names=None, with_for_update=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.refresh`](session.md#session-refresh)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.reset()` { #asyncsession-reset }

```python
await AsyncSession.reset()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.reset`](session.md#session-reset)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.rollback()` { #asyncsession-rollback }

```python
await AsyncSession.rollback()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.rollback`](session.md#session-rollback)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.run_sync()` { #asyncsession-run-sync }

```python
await AsyncSession.run_sync(fn, *arg, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

একটি sync ফাংশন চালায়, প্রথম আর্গুমেন্ট হিসেবে ভেতরের sync `Session` দিয়ে, greenlet-এর ভেতরে। তাই সেখানে lazy load-ও চলে। পুরোনো sync কোড পুনর্ব্যবহারে কাজের।

**উদাহরণ:**

```python
def count_addresses(sync_session, user_id):
    user = sync_session.get(User, user_id)
    return len(user.addresses)        # sync-এ lazy load চলে
print(await session.run_sync(count_addresses, 1))   # 1
```

### `AsyncSession.scalar()` { #asyncsession-scalar }

```python
await AsyncSession.scalar(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.scalar`](session.md#session-scalar)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.scalars()` { #asyncsession-scalars }

```python
await AsyncSession.scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.scalars`](session.md#session-scalars)-এর মতো। async সংস্করণে মেথডটি coroutine হলে (ওপরের সিগনেচারে `await` থাকলে) অবশ্যই `await` দিন।

### `AsyncSession.stream()` { #asyncsession-stream }

```python
await AsyncSession.stream(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ORM কুয়েরি স্ট্রিম করে `AsyncResult` দেয়; রো টুকরো করে আসে, সব একসাথে মেমরিতে নয়।

**উদাহরণ:**

```python
result = await session.stream(select(User.id, User.name).order_by(User.id))
async for row in result:
    print(row.id, row.name)
```

### `AsyncSession.stream_scalars()` { #asyncsession-stream-scalars }

```python
await AsyncSession.stream_scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`stream()`-এর মতো, কিন্তু প্রতিটি রো-র প্রথম কলাম, মানে সাধারণত ORM অবজেক্ট, দেয়।

**উদাহরণ:**

```python
result = await session.stream_scalars(select(User).order_by(User.id).execution_options(yield_per=100))
async for user in result:
    print(user.name)
```

### `AsyncSession.sync_session_class` { #asyncsession-sync-session-class }

**ধরন:** অ্যাট্রিবিউট

ভেতরে কোন sync `Session` ক্লাস চলছে (ডিফল্ট `Session`)।

**উদাহরণ:**

```python
print(AsyncSession.sync_session_class.__name__)   # Session
```

## `AsyncSessionTransaction` { #asyncsessiontransaction }

```python
from sqlalchemy.ext.asyncio import AsyncSessionTransaction
```

`AsyncSession.begin()` / `begin_nested()` থেকে পাওয়া সেশন-লেভেলের ট্রানজ্যাকশন। সাধারণত `async with session.begin():` আকারেই ব্যবহৃত হয়।

**উদাহরণ:**

```python
async with session.begin():
    session.add(User(name="ট্রানজ্যাকশনে"))
# নিজেই commit
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncsessiontransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bound_connection()`](#asyncsessiontransaction-bound-connection) | মেথড | (২.১-এ নতুন) এই ট্রানজ্যাকশন একটি bind-এর জন্য যে `AsyncConnection` আগেই নিয়েছে সেটি দেয়। |
| [`commit()`](#asyncsessiontransaction-commit) | মেথড (async) | ট্রানজ্যাকশন commit করে। |
| [`connections`](#asyncsessiontransaction-connections) | প্রপার্টি | এই ট্রানজ্যাকশন এ পর্যন্ত যেসব `AsyncConnection` নিয়েছে। |
| [`is_active`](#asyncsessiontransaction-is-active) | প্রপার্টি | ট্রানজ্যাকশন চালু থাকলে `True`। |
| [`nested`](#asyncsessiontransaction-nested) | অ্যাট্রিবিউট | SAVEPOINT হলে `True`। |
| [`rollback()`](#asyncsessiontransaction-rollback) | মেথড (async) | ট্রানজ্যাকশন বাতিল করে। |
| [`session`](#asyncsessiontransaction-session) | অ্যাট্রিবিউট | যে `AsyncSession`-এর ট্রানজ্যাকশন। |
| [`start()`](#asyncsessiontransaction-start) | মেথড (async) | `async with` ছাড়া শুরু করার জন্য; `await session.begin()` ভেতরে এটাই ডাকে। |
| [`sync_transaction`](#asyncsessiontransaction-sync-transaction) | অ্যাট্রিবিউট | ভেতরের sync `SessionTransaction`। |

### `AsyncSessionTransaction.bound_connection()` { #asyncsessiontransaction-bound-connection }

```python
AsyncSessionTransaction.bound_connection(bindkey=None, *, bind=None, **kw)
```

**ধরন:** মেথড

(২.১-এ নতুন) এই ট্রানজ্যাকশন একটি bind-এর জন্য যে `AsyncConnection` আগেই নিয়েছে সেটি দেয়।

**উদাহরণ:**

```python
async with session.begin() as trans:
    await session.get(User, 1)
    print(type(trans.bound_connection(User)).__name__)   # AsyncConnection
```

### `AsyncSessionTransaction.commit()` { #asyncsessiontransaction-commit }

```python
await AsyncSessionTransaction.commit()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ট্রানজ্যাকশন commit করে।

**উদাহরণ:**

```python
trans = await session.begin()
session.add(User(name="ক"))
await trans.commit()
```

### `AsyncSessionTransaction.connections` { #asyncsessiontransaction-connections }

**ধরন:** প্রপার্টি

এই ট্রানজ্যাকশন এ পর্যন্ত যেসব `AsyncConnection` নিয়েছে।

**উদাহরণ:**

```python
async with session.begin() as trans:
    await session.get(User, 1)
    print(len(trans.connections))   # 1
```

### `AsyncSessionTransaction.is_active` { #asyncsessiontransaction-is-active }

**ধরন:** প্রপার্টি

ট্রানজ্যাকশন চালু থাকলে `True`।

**উদাহরণ:**

```python
trans = await session.begin()
print(trans.is_active)   # True
await trans.rollback()
```

### `AsyncSessionTransaction.nested` { #asyncsessiontransaction-nested }

**ধরন:** অ্যাট্রিবিউট

SAVEPOINT হলে `True`।

**উদাহরণ:**

```python
async with session.begin():
    sp = await session.begin_nested()
    print(sp.nested)   # True
    await sp.rollback()
```

### `AsyncSessionTransaction.rollback()` { #asyncsessiontransaction-rollback }

```python
await AsyncSessionTransaction.rollback()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

ট্রানজ্যাকশন বাতিল করে।

**উদাহরণ:**

```python
trans = await session.begin()
session.add(User(name="বাতিল"))
await trans.rollback()
```

### `AsyncSessionTransaction.session` { #asyncsessiontransaction-session }

**ধরন:** অ্যাট্রিবিউট

যে `AsyncSession`-এর ট্রানজ্যাকশন।

**উদাহরণ:**

```python
trans = await session.begin()
print(trans.session is session)   # True
await trans.rollback()
```

### `AsyncSessionTransaction.start()` { #asyncsessiontransaction-start }

```python
await AsyncSessionTransaction.start(is_ctxmanager=False)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

`async with` ছাড়া শুরু করার জন্য; `await session.begin()` ভেতরে এটাই ডাকে।

**উদাহরণ:**

```python
trans = await session.begin().start()
await trans.rollback()
```

### `AsyncSessionTransaction.sync_transaction` { #asyncsessiontransaction-sync-transaction }

**ধরন:** অ্যাট্রিবিউট

ভেতরের sync `SessionTransaction`।

**উদাহরণ:**

```python
trans = await session.begin()
print(type(trans.sync_transaction).__name__)   # SessionTransaction
await trans.rollback()
```

## `AsyncAttrs` { #asyncattrs }

```python
from sqlalchemy.ext.asyncio import AsyncAttrs
```

`Base`-এ mixin হিসেবে যোগ করলে প্রতিটি মডেলে `awaitable_attrs` আসে, যা দিয়ে লোড না হওয়া অ্যাট্রিবিউট `await` করে পড়া যায়। শেষ উপায় হিসেবে ভালো; সাধারণত কুয়েরিতে `selectinload()` দেওয়াই উত্তম।

**উদাহরণ:**

```python
class Base(AsyncAttrs, DeclarativeBase):
    pass
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncattrs-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`awaitable_attrs`](#asyncattrs-awaitable-attrs) | প্রপার্টি | প্রতিটি অ্যাট্রিবিউটের একটি awaitable রূপ দেয়: `await obj.awaitable_attrs.addresses`। |

### `AsyncAttrs.awaitable_attrs` { #asyncattrs-awaitable-attrs }

**ধরন:** প্রপার্টি

প্রতিটি অ্যাট্রিবিউটের একটি awaitable রূপ দেয়: `await obj.awaitable_attrs.addresses`। শুধু ডিফল্ট `lazy="select"` রিলেশনশিপে কাজ করে; `lazy="raise"`-এ এরর দেয়।

**উদাহরণ:**

```python
user = await session.get(User, 1)
addresses = await user.awaitable_attrs.addresses
print([a.email for a in addresses])   # ['rahim@example.com']
```

## `async_scoped_session` { #async-scoped-session }

```python
from sqlalchemy.ext.asyncio import async_scoped_session
```

`scoped_session`-এর async রূপ: আপনার দেওয়া `scopefunc` অনুযায়ী প্রতি scope-এ একটি `AsyncSession` রাখে। async-এ থ্রেড-ভিত্তিক scope অর্থহীন, তাই `scopefunc` দিতেই হয় (যেমন `asyncio.current_task`)। FastAPI-তে সাধারণত `Depends(get_db)` সহজ ও নিরাপদ।

**উদাহরণ:**

```python
scoped = async_scoped_session(async_sessionmaker(engine), scopefunc=asyncio.current_task)
print((await scoped.get(User, 1)).name)   # রহিম
await scoped.remove()
```

### কনস্ট্রাক্টরের প্যারামিটার { #async-scoped-session-params }

```python
async_scoped_session(session_factory, scopefunc)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `session_factory` | `AsyncSession` বানানোর কারখানা, সাধারণত `async_sessionmaker`। |
| `scopefunc` | বর্তমান scope-এর key দেয় এমন ফাংশন, যেমন `asyncio.current_task`। বাধ্যতামূলক। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #async-scoped-session-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`aclose()`](#async-scoped-session-aclose) | মেথড (async) | `close()`-এর আরেক নাম (`contextlib.aclosing()`-এর জন্য)। |
| [`add()`](#async-scoped-session-add) | মেথড | একটি অবজেক্টকে সেশনে যোগ করে। |
| [`add_all()`](#async-scoped-session-add-all) | মেথড | অনেকগুলো অবজেক্ট একসাথে সেশনে যোগ করে, প্রতিটির জন্য `add()` ডাকার সমান। |
| [`autoflush`](#async-scoped-session-autoflush) | প্রপার্টি | ভেতরের সেশনের `autoflush` সেটিং (পড়া ও বদলানো যায়)। |
| [`begin()`](#async-scoped-session-begin) | মেথড | স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে আর একটি `SessionTransaction` দেয়। |
| [`begin_nested()`](#async-scoped-session-begin-nested) | মেথড | চলমান ট্রানজ্যাকশনের ভেতরে একটি "নেস্টেড" ট্রানজ্যাকশন, মানে ডেটাবেসে `SAVEPOINT`, শুরু করে। |
| [`bind`](#async-scoped-session-bind) | প্রপার্টি | সেশনটি কোন `AsyncEngine`/`AsyncConnection`-এ যুক্ত। |
| [`binds`](#async-scoped-session-binds) | প্রপার্টি | মডেল/টেবিল-ভিত্তিক bind-এর অপরিবর্তনীয় dict। |
| [`close()`](#async-scoped-session-close) | মেথড (async) | সেশনের ট্রানজ্যাকশন শেষ (rollback) করে, কানেকশন পুলে ফেরত দেয়, আর সব অবজেক্টকে সেশন থেকে বিচ্ছিন্ন (detached) করে। |
| [`close_all()`](#async-scoped-session-close-all) | ক্লাস মেথড (async) | মেমরিতে থাকা সব `AsyncSession` বন্ধ করে (ক্লাস মেথড)। |
| [`commit()`](#async-scoped-session-commit) | মেথড (async) | জমা থাকা সব পরিবর্তন `flush()` করে, তারপর ডেটাবেসে `COMMIT` পাঠায়। |
| [`configure()`](#async-scoped-session-configure) | মেথড | ভেতরের `async_sessionmaker`-এর সেটিং বদলায়। |
| [`connection()`](#async-scoped-session-connection) | মেথড (async) | সেশনের চলমান ট্রানজ্যাকশনের সাথে যুক্ত Core `Connection` দেয়। |
| [`delete()`](#async-scoped-session-delete) | মেথড (async) | একটি অবজেক্টকে মোছার জন্য চিহ্নিত করে। |
| [`delete_all()`](#async-scoped-session-delete-all) | মেথড (async) | (২.১-এ নতুন) অনেকগুলো অবজেক্ট একসাথে মোছার জন্য চিহ্নিত করে, প্রতিটিতে `delete()` ডাকার সমান। |
| [`deleted`](#async-scoped-session-deleted) | প্রপার্টি | যে অবজেক্টগুলো `delete()` দিয়ে মোছার জন্য চিহ্নিত কিন্তু এখনো flush হয়নি, সেগুলোর সেট (set-এর মতো একটি কালেকশন)। |
| [`dirty`](#async-scoped-session-dirty) | প্রপার্টি | যে persistent অবজেক্টগুলোর কোনো অ্যাট্রিবিউট বদলানো হয়েছে, সেগুলোর সেট। |
| [`execute()`](#async-scoped-session-execute) | মেথড (async) | যেকোনো স্টেটমেন্ট (`select`, `insert`, `update`, `delete`, `text`) চালায় আর একটি `Result` দেয়। |
| [`execution_options`](#async-scoped-session-execution-options) | প্রপার্টি | (২.১-এ নতুন) কনস্ট্রাক্টরে দেওয়া ডিফল্ট execution option-গুলো, যা এই সেশনের প্রতিটি `execute()`-এ প্রয়োগ হয়। |
| [`expire()`](#async-scoped-session-expire) | মেথড | একটি অবজেক্টের সব (বা নির্দিষ্ট) অ্যাট্রিবিউটের মেমরিতে থাকা মান মুছে দেয়। |
| [`expire_all()`](#async-scoped-session-expire-all) | মেথড | সেশনের সব persistent অবজেক্টকে expire করে। |
| [`expunge()`](#async-scoped-session-expunge) | মেথড | একটি অবজেক্টকে সেশন থেকে সরিয়ে দেয় (detached করে)। |
| [`expunge_all()`](#async-scoped-session-expunge-all) | মেথড | সেশনের সব অবজেক্ট সরিয়ে identity map খালি করে। |
| [`flush()`](#async-scoped-session-flush) | মেথড (async) | জমা থাকা সব পরিবর্তনের SQL (INSERT/UPDATE/DELETE) এখনই ডেটাবেসে পাঠায়, কিন্তু commit করে না। |
| [`get()`](#async-scoped-session-get) | মেথড (async) | primary key দিয়ে একটি অবজেক্ট দেয়, না থাকলে `None`। |
| [`get_async_bind()`](#async-scoped-session-get-async-bind) | মেথড | একটি মডেল বা কুয়েরির জন্য সেশন কোন `AsyncEngine`/`AsyncConnection` ব্যবহার করবে তা দেয়। |
| [`get_bind()`](#async-scoped-session-get-bind) | মেথড | একটি কুয়েরি বা মডেলের জন্য সেশন কোন `Engine`/`Connection` ব্যবহার করবে তা বের করে দেয়। |
| [`get_one()`](#async-scoped-session-get-one) | মেথড (async) | `get()`-এর মতোই, কিন্তু রো না পেলে `None` না দিয়ে `NoResultFound` এরর দেয়। |
| [`identity_key()`](#async-scoped-session-identity-key) | ক্লাস মেথড | একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। |
| [`identity_map`](#async-scoped-session-identity-map) | প্রপার্টি | ভেতরের সেশনের identity map (লোড করা অবজেক্টের রেজিস্টার)। |
| [`info`](#async-scoped-session-info) | প্রপার্টি | নিজের তথ্য রাখার একটি dict, যেমন রিকোয়েস্ট id বা বর্তমান ইউজার। |
| [`invalidate()`](#async-scoped-session-invalidate) | মেথড (async) | সেশন বন্ধ করে, আর ব্যবহৃত DBAPI কানেকশনগুলো "অকেজো" ঘোষণা করে পুলে ফেরত না দিয়ে ফেলে দেয়। |
| [`is_active`](#async-scoped-session-is-active) | প্রপার্টি | সেশন "আংশিক rollback" অবস্থায় না থাকলে `True`। |
| [`is_modified()`](#async-scoped-session-is-modified) | মেথড | অবজেক্টের কোনো অ্যাট্রিবিউটের মান আসলেই বদলেছে কি না দেখে `True`/`False` দেয়। |
| [`merge()`](#async-scoped-session-merge) | মেথড (async) | বাইরের একটি অবজেক্টের অবস্থা সেশনের ভেতরের সংশ্লিষ্ট অবজেক্টে কপি করে, আর সেই ভেতরের অবজেক্টটি ফেরত দেয়। |
| [`merge_all()`](#async-scoped-session-merge-all) | মেথড (async) | (২.১-এ নতুন) অনেক অবজেক্টে একসাথে `merge()` চালায় আর merge করা অবজেক্টগুলোর তালিকা দেয়। |
| [`new`](#async-scoped-session-new) | প্রপার্টি | যে নতুন অবজেক্টগুলো `add()` করা হয়েছে কিন্তু এখনো flush হয়নি (pending), সেগুলোর সেট। |
| [`no_autoflush`](#async-scoped-session-no-autoflush) | প্রপার্টি | একটি context manager, যার ভেতরে সাময়িকভাবে autoflush বন্ধ থাকে। |
| [`object_session()`](#async-scoped-session-object-session) | ক্লাস মেথড | একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। |
| [`refresh()`](#async-scoped-session-refresh) | মেথড (async) | অবজেক্টের মানগুলো এখনই ডেটাবেস থেকে আবার পড়ে আনে (একটি SELECT)। |
| [`remove()`](#async-scoped-session-remove) | মেথড (async) | বর্তমান scope-এর সেশন বন্ধ করে রেজিস্ট্রি থেকে সরায়। |
| [`reset()`](#async-scoped-session-reset) | মেথড (async) | সেশনকে একদম শুরুর অবস্থায় ফিরিয়ে নেয়: ট্রানজ্যাকশন বাতিল, সব অবজেক্ট বিচ্ছিন্ন, কানেকশন ফেরত। |
| [`rollback()`](#async-scoped-session-rollback) | মেথড (async) | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`scalar()`](#async-scoped-session-scalar) | মেথড (async) | একটি স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলামের মানটি দেয় (না থাকলে `None`)। |
| [`scalars()`](#async-scoped-session-scalars) | মেথড (async) | একটি স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলাম দিয়ে একটি `ScalarResult` দেয়। |
| [`stream()`](#async-scoped-session-stream) | মেথড (async) | ORM কুয়েরি স্ট্রিম করে `AsyncResult` দেয়; রো টুকরো করে আসে, সব একসাথে মেমরিতে নয়। |
| [`stream_scalars()`](#async-scoped-session-stream-scalars) | মেথড (async) | `stream()`-এর মতো, কিন্তু প্রতিটি রো-র প্রথম কলাম, মানে সাধারণত ORM অবজেক্ট, দেয়। |

### `async_scoped_session.aclose()` { #async-scoped-session-aclose }

```python
await async_scoped_session.aclose()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`AsyncSession.aclose`](#asyncsession-aclose)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.add()` { #async-scoped-session-add }

```python
async_scoped_session.add(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add`](session.md#session-add)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.add_all()` { #async-scoped-session-add-all }

```python
async_scoped_session.add_all(instances)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add_all`](session.md#session-add-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.autoflush` { #async-scoped-session-autoflush }

**ধরন:** প্রপার্টি

কাজ হুবহু [`AsyncSession.autoflush`](#asyncsession-autoflush)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.begin()` { #async-scoped-session-begin }

```python
async_scoped_session.begin()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin`](session.md#session-begin)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.begin_nested()` { #async-scoped-session-begin-nested }

```python
async_scoped_session.begin_nested()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin_nested`](session.md#session-begin-nested)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.bind` { #async-scoped-session-bind }

**ধরন:** প্রপার্টি

কাজ হুবহু [`AsyncSession.bind`](#asyncsession-bind)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.binds` { #async-scoped-session-binds }

**ধরন:** প্রপার্টি

কাজ হুবহু [`AsyncSession.binds`](#asyncsession-binds)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.close()` { #async-scoped-session-close }

```python
await async_scoped_session.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.close`](session.md#session-close)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.close_all()` { #async-scoped-session-close-all }

```python
await async_scoped_session.close_all()
```

**ধরন:** ক্লাস মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`AsyncSession.close_all`](#asyncsession-close-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.commit()` { #async-scoped-session-commit }

```python
await async_scoped_session.commit()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.commit`](session.md#session-commit)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.configure()` { #async-scoped-session-configure }

```python
async_scoped_session.configure(**kwargs)
```

**ধরন:** মেথড

ভেতরের `async_sessionmaker`-এর সেটিং বদলায়।

**উদাহরণ:**

```python
scoped = async_scoped_session(async_sessionmaker(), scopefunc=asyncio.current_task)
scoped.configure(bind=engine)
print((await scoped.get(User, 2)).name)   # করিম
await scoped.remove()
```

### `async_scoped_session.connection()` { #async-scoped-session-connection }

```python
await async_scoped_session.connection(bind_arguments=None, execution_options=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.connection`](session.md#session-connection)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.delete()` { #async-scoped-session-delete }

```python
await async_scoped_session.delete(instance)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.delete`](session.md#session-delete)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.delete_all()` { #async-scoped-session-delete-all }

```python
await async_scoped_session.delete_all(instances)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.delete_all`](session.md#session-delete-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.deleted` { #async-scoped-session-deleted }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.deleted`](session.md#session-deleted)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.dirty` { #async-scoped-session-dirty }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.dirty`](session.md#session-dirty)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.execute()` { #async-scoped-session-execute }

```python
await async_scoped_session.execute(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.execute`](session.md#session-execute)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.execution_options` { #async-scoped-session-execution-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.execution_options`](session.md#session-execution-options)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.expire()` { #async-scoped-session-expire }

```python
async_scoped_session.expire(instance, attribute_names=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire`](session.md#session-expire)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.expire_all()` { #async-scoped-session-expire-all }

```python
async_scoped_session.expire_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire_all`](session.md#session-expire-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.expunge()` { #async-scoped-session-expunge }

```python
async_scoped_session.expunge(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge`](session.md#session-expunge)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.expunge_all()` { #async-scoped-session-expunge-all }

```python
async_scoped_session.expunge_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge_all`](session.md#session-expunge-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.flush()` { #async-scoped-session-flush }

```python
await async_scoped_session.flush(objects=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.flush`](session.md#session-flush)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.get()` { #async-scoped-session-get }

```python
await async_scoped_session.get(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={})
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.get`](session.md#session-get)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.get_async_bind()` { #async-scoped-session-get-async-bind }

```python
async_scoped_session.get_async_bind(mapper=None, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`AsyncSession.get_async_bind`](#asyncsession-get-async-bind)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.get_bind()` { #async-scoped-session-get-bind }

```python
async_scoped_session.get_bind(mapper=None, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_bind`](session.md#session-get-bind)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.get_one()` { #async-scoped-session-get-one }

```python
await async_scoped_session.get_one(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={})
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.get_one`](session.md#session-get-one)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.identity_key()` { #async-scoped-session-identity-key }

```python
async_scoped_session.identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.identity_key`](session.md#session-identity-key)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.identity_map` { #async-scoped-session-identity-map }

**ধরন:** প্রপার্টি

কাজ হুবহু [`AsyncSession.identity_map`](#asyncsession-identity-map)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.info` { #async-scoped-session-info }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.info`](session.md#session-info)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.invalidate()` { #async-scoped-session-invalidate }

```python
await async_scoped_session.invalidate()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.invalidate`](session.md#session-invalidate)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.is_active` { #async-scoped-session-is-active }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.is_active`](session.md#session-is-active)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.is_modified()` { #async-scoped-session-is-modified }

```python
async_scoped_session.is_modified(instance, include_collections=True)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.is_modified`](session.md#session-is-modified)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.merge()` { #async-scoped-session-merge }

```python
await async_scoped_session.merge(instance, *, load=True, options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.merge`](session.md#session-merge)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.merge_all()` { #async-scoped-session-merge-all }

```python
await async_scoped_session.merge_all(instances, *, load=True, options=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.merge_all`](session.md#session-merge-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.new` { #async-scoped-session-new }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.new`](session.md#session-new)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.no_autoflush` { #async-scoped-session-no-autoflush }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.no_autoflush`](session.md#session-no-autoflush)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.object_session()` { #async-scoped-session-object-session }

```python
async_scoped_session.object_session(instance)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.object_session`](session.md#session-object-session)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.refresh()` { #async-scoped-session-refresh }

```python
await async_scoped_session.refresh(instance, attribute_names=None, with_for_update=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.refresh`](session.md#session-refresh)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.remove()` { #async-scoped-session-remove }

```python
await async_scoped_session.remove()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

বর্তমান scope-এর সেশন বন্ধ করে রেজিস্ট্রি থেকে সরায়। প্রতিটি task/রিকোয়েস্ট শেষে ডাকুন।

**উদাহরণ:**

```python
scoped = async_scoped_session(async_sessionmaker(engine), scopefunc=asyncio.current_task)
await scoped.get(User, 1)
await scoped.remove()
```

### `async_scoped_session.reset()` { #async-scoped-session-reset }

```python
await async_scoped_session.reset()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.reset`](session.md#session-reset)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.rollback()` { #async-scoped-session-rollback }

```python
await async_scoped_session.rollback()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.rollback`](session.md#session-rollback)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.scalar()` { #async-scoped-session-scalar }

```python
await async_scoped_session.scalar(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.scalar`](session.md#session-scalar)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.scalars()` { #async-scoped-session-scalars }

```python
await async_scoped_session.scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Session.scalars`](session.md#session-scalars)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.stream()` { #async-scoped-session-stream }

```python
await async_scoped_session.stream(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`AsyncSession.stream`](#asyncsession-stream)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

### `async_scoped_session.stream_scalars()` { #async-scoped-session-stream-scalars }

```python
await async_scoped_session.stream_scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`AsyncSession.stream_scalars`](#asyncsession-stream-scalars)-এর মতো। এখানে কাজটি বর্তমান scope-এর `AsyncSession`-এর ওপর হয়।

## `AsyncResult` { #asyncresult }

```python
from sqlalchemy.ext.asyncio import AsyncResult
```

`stream()` থেকে পাওয়া async ফলাফল। রো ধীরে ধীরে আসে, তাই `.all()`, `.first()`, `.one()` ইত্যাদি সবই `await` করতে হয়, আর লুপ চালাতে `async for`। ট্রানজ্যাকশন খোলা থাকা অবস্থায় পুরোটা পড়ে শেষ করুন।

**উদাহরণ:**

```python
result = await session.stream(select(User.id, User.name).order_by(User.id))
first_two = await result.fetchmany(2)
rest = await result.all()
print(first_two, rest)   # [(1, 'রহিম'), (2, 'করিম')] [(3, 'সুমি')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#asyncresult-all) | মেথড (async) | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#asyncresult-close) | মেথড (async) | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#asyncresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#asyncresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#asyncresult-fetchall) | মেথড (async) | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#asyncresult-fetchmany) | মেথড (async) | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#asyncresult-fetchone) | মেথড (async) | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#asyncresult-first) | মেথড (async) | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#asyncresult-freeze) | মেথড (async) | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`keys()`](#asyncresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`mappings()`](#asyncresult-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#asyncresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#asyncresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`one()`](#asyncresult-one) | মেথড (async) | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#asyncresult-one-or-none) | মেথড (async) | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#asyncresult-partitions) | মেথড (async iterator) | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`scalar()`](#asyncresult-scalar) | মেথড (async) | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#asyncresult-scalar-one) | মেথড (async) | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#asyncresult-scalar-one-or-none) | মেথড (async) | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#asyncresult-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`t`](#asyncresult-t) | প্রপার্টি | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#asyncresult-tuples) | মেথড | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#asyncresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#asyncresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `AsyncResult.all()` { #asyncresult-all }

```python
await AsyncResult.all()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.all`](result.md#result-all)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.close()` { #asyncresult-close }

```python
await AsyncResult.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.close`](result.md#result-close)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.closed` { #asyncresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](result.md#result-closed)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.columns()` { #asyncresult-columns }

```python
AsyncResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](result.md#result-columns)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.fetchall()` { #asyncresult-fetchall }

```python
await AsyncResult.fetchall()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchall`](result.md#result-fetchall)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.fetchmany()` { #asyncresult-fetchmany }

```python
await AsyncResult.fetchmany(size=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchmany`](result.md#result-fetchmany)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.fetchone()` { #asyncresult-fetchone }

```python
await AsyncResult.fetchone()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchone`](result.md#result-fetchone)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.first()` { #asyncresult-first }

```python
await AsyncResult.first()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.first`](result.md#result-first)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.freeze()` { #asyncresult-freeze }

```python
await AsyncResult.freeze()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.freeze`](result.md#result-freeze)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.keys()` { #asyncresult-keys }

```python
AsyncResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](result.md#result-keys)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.mappings()` { #asyncresult-mappings }

```python
AsyncResult.mappings()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.mappings`](result.md#result-mappings)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.memoized_attribute` { #asyncresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](result.md#result-memoized-attribute)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.memoized_instancemethod()` { #asyncresult-memoized-instancemethod }

```python
AsyncResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](result.md#result-memoized-instancemethod)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.one()` { #asyncresult-one }

```python
await AsyncResult.one()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one`](result.md#result-one)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.one_or_none()` { #asyncresult-one-or-none }

```python
await AsyncResult.one_or_none()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one_or_none`](result.md#result-one-or-none)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.partitions()` { #asyncresult-partitions }

```python
AsyncResult.partitions(size=None)
```

**ধরন:** মেথড (async iterator) · `async for` দিয়ে ব্যবহার করুন

কাজ হুবহু [`Result.partitions`](result.md#result-partitions)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.scalar()` { #asyncresult-scalar }

```python
await AsyncResult.scalar()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.scalar`](result.md#result-scalar)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.scalar_one()` { #asyncresult-scalar-one }

```python
await AsyncResult.scalar_one()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.scalar_one`](result.md#result-scalar-one)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.scalar_one_or_none()` { #asyncresult-scalar-one-or-none }

```python
await AsyncResult.scalar_one_or_none()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.scalar_one_or_none`](result.md#result-scalar-one-or-none)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.scalars()` { #asyncresult-scalars }

```python
AsyncResult.scalars(index=0)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalars`](result.md#result-scalars)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.t` { #asyncresult-t }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.t`](result.md#result-t)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.tuples()` { #asyncresult-tuples }

```python
AsyncResult.tuples()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.tuples`](result.md#result-tuples)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.unique()` { #asyncresult-unique }

```python
AsyncResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](result.md#result-unique)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

### `AsyncResult.yield_per()` { #asyncresult-yield-per }

```python
AsyncResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](result.md#result-yield-per)-এর মতো। async সংস্করণে মেথডটি coroutine হলে `await` দিন; `partitions()` ব্যবহার করুন `async for` দিয়ে।

## `AsyncScalarResult` { #asyncscalarresult }

```python
from sqlalchemy.ext.asyncio import AsyncScalarResult
```

`AsyncResult`-এর মোড়ক, যেখানে প্রতিটি আইটেম একটি একক মান (সাধারণত ORM অবজেক্ট)। `stream_scalars()` বা `async_result.scalars()` এটি দেয়।

**উদাহরণ:**

```python
result = await session.stream_scalars(select(User).order_by(User.id))
print([u.name async for u in result])   # ['রহিম', 'করিম', 'সুমি']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncscalarresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#asyncscalarresult-all) | মেথড (async) | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#asyncscalarresult-close) | মেথড (async) | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#asyncscalarresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`fetchall()`](#asyncscalarresult-fetchall) | মেথড (async) | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#asyncscalarresult-fetchmany) | মেথড (async) | পরের `size`-টি রো দেয়। |
| [`first()`](#asyncscalarresult-first) | মেথড (async) | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`memoized_attribute`](#asyncscalarresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#asyncscalarresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`one()`](#asyncscalarresult-one) | মেথড (async) | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#asyncscalarresult-one-or-none) | মেথড (async) | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#asyncscalarresult-partitions) | মেথড (async iterator) | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`unique()`](#asyncscalarresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#asyncscalarresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `AsyncScalarResult.all()` { #asyncscalarresult-all }

```python
await AsyncScalarResult.all()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.all`](result.md#result-all)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.close()` { #asyncscalarresult-close }

```python
await AsyncScalarResult.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.close`](result.md#result-close)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.closed` { #asyncscalarresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](result.md#result-closed)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.fetchall()` { #asyncscalarresult-fetchall }

```python
await AsyncScalarResult.fetchall()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchall`](result.md#result-fetchall)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.fetchmany()` { #asyncscalarresult-fetchmany }

```python
await AsyncScalarResult.fetchmany(size=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchmany`](result.md#result-fetchmany)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.first()` { #asyncscalarresult-first }

```python
await AsyncScalarResult.first()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.first`](result.md#result-first)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.memoized_attribute` { #asyncscalarresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](result.md#result-memoized-attribute)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.memoized_instancemethod()` { #asyncscalarresult-memoized-instancemethod }

```python
AsyncScalarResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](result.md#result-memoized-instancemethod)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.one()` { #asyncscalarresult-one }

```python
await AsyncScalarResult.one()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one`](result.md#result-one)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.one_or_none()` { #asyncscalarresult-one-or-none }

```python
await AsyncScalarResult.one_or_none()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one_or_none`](result.md#result-one-or-none)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.partitions()` { #asyncscalarresult-partitions }

```python
AsyncScalarResult.partitions(size=None)
```

**ধরন:** মেথড (async iterator) · `async for` দিয়ে ব্যবহার করুন

কাজ হুবহু [`Result.partitions`](result.md#result-partitions)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.unique()` { #asyncscalarresult-unique }

```python
AsyncScalarResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](result.md#result-unique)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

### `AsyncScalarResult.yield_per()` { #asyncscalarresult-yield-per }

```python
AsyncScalarResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](result.md#result-yield-per)-এর মতো। পার্থক্য: প্রতিটি আইটেম একটি একক মান, আর coroutine মেথডে `await` লাগে।

## `AsyncMappingResult` { #asyncmappingresult }

```python
from sqlalchemy.ext.asyncio import AsyncMappingResult
```

`AsyncResult`-এর মোড়ক, যেখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`। `async_result.mappings()` এটি দেয়।

**উদাহরণ:**

```python
result = await session.stream(select(User.id, User.name).order_by(User.id))
rows = await result.mappings().all()
print(rows[0]["name"])   # রহিম
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asyncmappingresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#asyncmappingresult-all) | মেথড (async) | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#asyncmappingresult-close) | মেথড (async) | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#asyncmappingresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#asyncmappingresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#asyncmappingresult-fetchall) | মেথড (async) | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#asyncmappingresult-fetchmany) | মেথড (async) | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#asyncmappingresult-fetchone) | মেথড (async) | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#asyncmappingresult-first) | মেথড (async) | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`keys()`](#asyncmappingresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`memoized_attribute`](#asyncmappingresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#asyncmappingresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`one()`](#asyncmappingresult-one) | মেথড (async) | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#asyncmappingresult-one-or-none) | মেথড (async) | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#asyncmappingresult-partitions) | মেথড (async iterator) | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`unique()`](#asyncmappingresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#asyncmappingresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `AsyncMappingResult.all()` { #asyncmappingresult-all }

```python
await AsyncMappingResult.all()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.all`](result.md#result-all)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.close()` { #asyncmappingresult-close }

```python
await AsyncMappingResult.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.close`](result.md#result-close)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.closed` { #asyncmappingresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](result.md#result-closed)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.columns()` { #asyncmappingresult-columns }

```python
AsyncMappingResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](result.md#result-columns)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.fetchall()` { #asyncmappingresult-fetchall }

```python
await AsyncMappingResult.fetchall()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchall`](result.md#result-fetchall)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.fetchmany()` { #asyncmappingresult-fetchmany }

```python
await AsyncMappingResult.fetchmany(size=None)
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchmany`](result.md#result-fetchmany)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.fetchone()` { #asyncmappingresult-fetchone }

```python
await AsyncMappingResult.fetchone()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.fetchone`](result.md#result-fetchone)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.first()` { #asyncmappingresult-first }

```python
await AsyncMappingResult.first()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.first`](result.md#result-first)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.keys()` { #asyncmappingresult-keys }

```python
AsyncMappingResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](result.md#result-keys)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.memoized_attribute` { #asyncmappingresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](result.md#result-memoized-attribute)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.memoized_instancemethod()` { #asyncmappingresult-memoized-instancemethod }

```python
AsyncMappingResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](result.md#result-memoized-instancemethod)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.one()` { #asyncmappingresult-one }

```python
await AsyncMappingResult.one()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one`](result.md#result-one)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.one_or_none()` { #asyncmappingresult-one-or-none }

```python
await AsyncMappingResult.one_or_none()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.one_or_none`](result.md#result-one-or-none)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.partitions()` { #asyncmappingresult-partitions }

```python
AsyncMappingResult.partitions(size=None)
```

**ধরন:** মেথড (async iterator) · `async for` দিয়ে ব্যবহার করুন

কাজ হুবহু [`Result.partitions`](result.md#result-partitions)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.unique()` { #asyncmappingresult-unique }

```python
AsyncMappingResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](result.md#result-unique)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

### `AsyncMappingResult.yield_per()` { #asyncmappingresult-yield-per }

```python
AsyncMappingResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](result.md#result-yield-per)-এর মতো। পার্থক্য: প্রতিটি আইটেম `RowMapping`, আর coroutine মেথডে `await` লাগে।

## `AsyncTupleResult` { #asynctupleresult }

```python
from sqlalchemy.ext.asyncio import AsyncTupleResult
```

শুধু টাইপ চেকারের জন্য: `AsyncResult` যার রো-কে সাধারণ tuple হিসেবে ঘোষণা করা হয়। রানটাইমে আসল অবজেক্টটি `AsyncResult`।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #asynctupleresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#asynctupleresult-close) | মেথড (async) | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#asynctupleresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`memoized_attribute`](#asynctupleresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#asynctupleresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`yield_per()`](#asynctupleresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `AsyncTupleResult.close()` { #asynctupleresult-close }

```python
await AsyncTupleResult.close()
```

**ধরন:** মেথড (async) · কল করার সময় `await` লাগবে

কাজ হুবহু [`Result.close`](result.md#result-close)-এর মতো।

### `AsyncTupleResult.closed` { #asynctupleresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](result.md#result-closed)-এর মতো।

### `AsyncTupleResult.memoized_attribute` { #asynctupleresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](result.md#result-memoized-attribute)-এর মতো।

### `AsyncTupleResult.memoized_instancemethod()` { #asynctupleresult-memoized-instancemethod }

```python
AsyncTupleResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](result.md#result-memoized-instancemethod)-এর মতো।

### `AsyncTupleResult.yield_per()` { #asynctupleresult-yield-per }

```python
AsyncTupleResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](result.md#result-yield-per)-এর মতো।

/// check | সংক্ষেপে মনে রাখুন

* `create_async_engine()` একবার, `async_sessionmaker(engine, expire_on_commit=False)` একবার, প্রতি রিকোয়েস্টে `async with SessionLocal() as session`।
* ডেটাবেসে যায় এমন সব মেথডে `await`: `execute`, `scalars`, `scalar`, `get`, `flush`, `commit`, `refresh`, `delete`, `merge`, `close`।
* `add()`, `add_all()`, `expunge()`, `new`, `dirty`-তে `await` নেই।
* sync-only কাজ (`create_all`, `inspect`, পুরোনো হেল্পার) `run_sync()` দিয়ে।
* বিশাল ফলাফল `stream()` / `stream_scalars()` + `async for`।

///
