# কানেকশন পুল API: QueuePool, NullPool, StaticPool … { #api-pool }

/// note | এই পেজে যা আছে

* পুলের ধরন: `Pool` (মূল), `QueuePool` (ডিফল্ট), `AsyncAdaptedQueuePool` (async ডিফল্ট), `NullPool`, `StaticPool`, `SingletonThreadPool`, `AssertionPool`; প্রতিটির **সব** সদস্য ও প্যারামিটার।
* পুলের কানেকশন-অবজেক্ট: `PoolProxiedConnection`, `ConnectionPoolEntry`, `ManagesConnection`, `PoolResetState`, আর `reset_rollback` / `reset_commit` / `reset_none`।

///

প্রতিটি নতুন ডেটাবেস কানেকশন খোলা ব্যয়বহুল (নেটওয়ার্ক, লগইন, TLS)। **পুল** কয়েকটি কানেকশন খোলা রেখে বারবার ধার দেয়: `engine.connect()` পুল থেকে নেয়, `close()` পুলে ফেরত দেয় (আসলে বন্ধ করে না)। সাধারণত `create_engine(pool_size=..., max_overflow=..., pool_pre_ping=True)` দিয়েই কনফিগার হয়, পুলের ক্লাস সরাসরি লাগে না।

/// tip | কোন পুল কখন

| অবস্থা | পুল |
| :--- | :--- |
| সাধারণ ওয়েব অ্যাপ (ডিফল্ট) | `QueuePool` / async-এ `AsyncAdaptedQueuePool` |
| PgBouncer-এর মতো বাইরের পুলার, serverless, বা প্রতি টেস্টে নতুন কানেকশন | `NullPool` |
| SQLite `:memory:` টেস্ট (সব জায়গায় একই কানেকশন লাগবে) | `StaticPool` |
| পুলে কানেকশন লিক খুঁজতে (ডিবাগ) | `AssertionPool` |

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

`URL_STR = "postgresql+psycopg2://postgres@127.0.0.1/apiref"`; প্রতিটি উদাহরণ নিজের engine/পুল বানায়। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `Pool` { #pool }

```python
from sqlalchemy.pool import Pool
```

সব পুলের মূল ক্লাস। Engine-এর পুল পাওয়া যায় `engine.pool` দিয়ে। নিজে বানাতে একটি `creator` (DBAPI কানেকশন ফেরত দেওয়া ফাংশন) লাগে।

**উদাহরণ:**

```python
eng = create_engine(URL_STR)
print(isinstance(eng.pool, Pool), type(eng.pool).__name__)   # True QueuePool
eng.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #pool-params }

```python
Pool(creator, recycle=-1, echo=None, logging_name=None, reset_on_return=True, events=None, dialect=None, pre_ping=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | নতুন DBAPI কানেকশন বানানোর ফাংশন। |
| `recycle` | এত সেকেন্ডের বেশি পুরোনো কানেকশন ধার দেওয়ার আগে বন্ধ করে নতুন খোলে (`-1` = কখনো নয়)। `create_engine(pool_recycle=...)`। |
| `echo` | `True`/`"debug"` দিলে পুলের কার্যক্রম লগ করে (`echo_pool`)। |
| `logging_name` | লগে পুলের নাম। |
| `reset_on_return` | কানেকশন পুলে ফেরার সময় কী করবে: `"rollback"` (ডিফল্ট, অসমাপ্ত ট্রানজ্যাকশন বাতিল), `"commit"`, বা `None` (কিছু না; শুধু autocommit-এ নিরাপদ)। |
| `events` | `[(fn, event_name), ...]`: পুল বানানোর সময়েই event listener। |
| `dialect` | ডায়ালেক্ট (rollback/ping-এর ডেটাবেস-নির্দিষ্ট রূপের জন্য)। |
| `pre_ping` | `True` দিলে ধার দেওয়ার আগে একটি হালকা কুয়েরি দিয়ে কানেকশন বেঁচে আছে কি না দেখে; মরা হলে নিঃশব্দে নতুন খোলে। প্রোডাকশনে সুপারিশকৃত (`pool_pre_ping=True`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #pool-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`connect()`](#pool-connect) | মেথড | পুল থেকে একটি DBAPI কানেকশন (মোড়ানো `PoolProxiedConnection`) দেয়; `close()` করলে পুলে ফেরে। |
| [`dispose()`](#pool-dispose) | মেথড | পুলে বসে থাকা (checked-in) সব কানেকশন বন্ধ করে। |
| [`logging_name`](#pool-logging-name) | অ্যাট্রিবিউট | লগে পুলের নাম (না দিলে `None`)। |
| [`recreate()`](#pool-recreate) | মেথড | একই সেটিংসে নতুন একটি খালি পুল দেয় (`engine.dispose()` ভেতরে এটি ব্যবহার করে)। |
| [`status()`](#pool-status) | মেথড | পুলের অবস্থার এক লাইনের বর্ণনা (মনিটরিং/ডিবাগে কাজে লাগে)। |

### `Pool.connect()` { #pool-connect }

```python
Pool.connect()
```

**ধরন:** মেথড

পুল থেকে একটি DBAPI কানেকশন (মোড়ানো `PoolProxiedConnection`) দেয়; `close()` করলে পুলে ফেরে।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=2)
c = pool.connect()
print(pool.checkedout()); c.close(); print(pool.checkedout())
# 1
# 0
pool.dispose()
```

### `Pool.dispose()` { #pool-dispose }

```python
Pool.dispose()
```

**ধরন:** মেথড

পুলে বসে থাকা (checked-in) সব কানেকশন বন্ধ করে। ধার দেওয়া কানেকশনগুলো ফেরার সময় বন্ধ হয়।

**উদাহরণ:**

```python
pool = QueuePool(creator)
pool.connect().close()
print(pool.checkedin()); pool.dispose(); print(pool.checkedin())
# 1
# 0
```

### `Pool.logging_name` { #pool-logging-name }

**ধরন:** অ্যাট্রিবিউট

লগে পুলের নাম (না দিলে `None`)।

**উদাহরণ:**

```python
print(QueuePool(creator, logging_name="main").logging_name)   # main
```

### `Pool.recreate()` { #pool-recreate }

```python
Pool.recreate()
```

**ধরন:** মেথড

একই সেটিংসে নতুন একটি খালি পুল দেয় (`engine.dispose()` ভেতরে এটি ব্যবহার করে)।

**উদাহরণ:**

```python
p1 = QueuePool(creator, pool_size=3)
p2 = p1.recreate()
print(p2 is not p1, p2.size())   # True 3
```

### `Pool.status()` { #pool-status }

```python
Pool.status()
```

**ধরন:** মেথড

পুলের অবস্থার এক লাইনের বর্ণনা (মনিটরিং/ডিবাগে কাজে লাগে)।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=2)
c = pool.connect()
print(pool.status())   # Pool size: 2  Connections in pool: 0 Current Overflow: -1 Current Checked out connections: 1
c.close(); pool.dispose()
```

## `QueuePool` { #queuepool }

```python
from sqlalchemy.pool import QueuePool
```

Engine-এর **ডিফল্ট** পুল: সর্বোচ্চ `pool_size` টি কানেকশন খোলা রাখে, চাপের সময় আরও `max_overflow` টি পর্যন্ত বাড়তি খোলে (ফেরত এলে সেগুলো বন্ধ হয়)। সব ব্যস্ত থাকলে `timeout` সেকেন্ড অপেক্ষা করে, তারপর `TimeoutError`। মোট সর্বোচ্চ কানেকশন = `pool_size + max_overflow` (প্রতি প্রসেসে; কয়েকটি worker থাকলে গুণ করুন, আর ডেটাবেসের `max_connections`-এর নিচে রাখুন)।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=1, max_overflow=1, timeout=0.5)
a, b = pool.connect(), pool.connect()               # ১টি স্থায়ী + ১টি overflow
try:
    pool.connect()
except exc.TimeoutError:
    print("পুল ভর্তি, ০.৫ সেকেন্ড পর TimeoutError")   # পুল ভর্তি, ০.৫ সেকেন্ড পর TimeoutError
a.close(); b.close(); pool.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #queuepool-params }

```python
QueuePool(creator, pool_size=5, max_overflow=10, timeout=30.0, use_lifo=False, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | কানেকশন বানানোর ফাংশন। |
| `pool_size` | পুলে স্থায়ীভাবে রাখা কানেকশনের সংখ্যা (ডিফল্ট ৫; ০ = সীমাহীন)। |
| `max_overflow` | `pool_size`-এর ওপরে সাময়িক বাড়তি কানেকশন (ডিফল্ট ১০; `-1` = সীমাহীন)। |
| `timeout` | খালি কানেকশনের জন্য সর্বোচ্চ অপেক্ষা, সেকেন্ডে (ডিফল্ট ৩০)। |
| `use_lifo` | `True` দিলে সবচেয়ে সাম্প্রতিক ফেরত আসা কানেকশন আগে দেয় (কম চাপে অতিরিক্ত কানেকশনগুলো অলস থেকে বন্ধ হতে পারে)। |
| `kw` | `Pool`-এর অপশন (`recycle`, `pre_ping`, `reset_on_return` …)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #queuepool-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`checkedin()`](#queuepool-checkedin) | মেথড | এখন পুলে অলস বসে থাকা কানেকশনের সংখ্যা। |
| [`checkedout()`](#queuepool-checkedout) | মেথড | এখন ধার দেওয়া (ব্যবহৃত) কানেকশনের সংখ্যা। |
| [`overflow()`](#queuepool-overflow) | মেথড | বর্তমান overflow: `pool_size`-এর তুলনায় কতটি বেশি/কম কানেকশন খোলা (ঋণাত্মক = এখনো পুল পূর্ণ হয়নি)। |
| [`size()`](#queuepool-size) | মেথড | কনফিগার করা `pool_size`। |
| [`timeout()`](#queuepool-timeout) | মেথড | কনফিগার করা অপেক্ষার সময়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `QueuePool`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Pool` থেকে:** [`connect()`](#pool-connect) · [`dispose()`](#pool-dispose) · [`logging_name`](#pool-logging-name) · [`recreate()`](#pool-recreate) · [`status()`](#pool-status)

///

### `QueuePool.checkedin()` { #queuepool-checkedin }

```python
QueuePool.checkedin()
```

**ধরন:** মেথড

এখন পুলে অলস বসে থাকা কানেকশনের সংখ্যা।

**উদাহরণ:**

```python
pool = QueuePool(creator); pool.connect().close()
print(pool.checkedin())   # 1
pool.dispose()
```

### `QueuePool.checkedout()` { #queuepool-checkedout }

```python
QueuePool.checkedout()
```

**ধরন:** মেথড

এখন ধার দেওয়া (ব্যবহৃত) কানেকশনের সংখ্যা। সবসময় উঁচু থাকলে কোথাও কানেকশন ফেরত দেওয়া হচ্ছে না (লিক)।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect()
print(pool.checkedout())   # 1
c.close(); pool.dispose()
```

### `QueuePool.overflow()` { #queuepool-overflow }

```python
QueuePool.overflow()
```

**ধরন:** মেথড

বর্তমান overflow: `pool_size`-এর তুলনায় কতটি বেশি/কম কানেকশন খোলা (ঋণাত্মক = এখনো পুল পূর্ণ হয়নি)।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=1, max_overflow=2)
a, b = pool.connect(), pool.connect()
print(pool.overflow())   # 1
a.close(); b.close(); pool.dispose()
```

### `QueuePool.size()` { #queuepool-size }

```python
QueuePool.size()
```

**ধরন:** মেথড

কনফিগার করা `pool_size`।

**উদাহরণ:**

```python
print(QueuePool(creator, pool_size=7).size())   # 7
```

### `QueuePool.timeout()` { #queuepool-timeout }

```python
QueuePool.timeout()
```

**ধরন:** মেথড

কনফিগার করা অপেক্ষার সময়।

**উদাহরণ:**

```python
print(QueuePool(creator, timeout=5).timeout())   # 5
```

## `AsyncAdaptedQueuePool` { #asyncadaptedqueuepool }

```python
from sqlalchemy.pool import AsyncAdaptedQueuePool
```

`QueuePool`-এর asyncio সংস্করণ: `create_async_engine()`-এর ডিফল্ট পুল। অপেক্ষার সারিটি asyncio-বান্ধব; সেটিং একই।

**উদাহরণ:**

```python
from sqlalchemy.ext.asyncio import create_async_engine
aeng = create_async_engine("postgresql+asyncpg://postgres@127.0.0.1/apiref")
print(type(aeng.sync_engine.pool).__name__)   # AsyncAdaptedQueuePool
```

### কনস্ট্রাক্টরের প্যারামিটার { #asyncadaptedqueuepool-params }

```python
AsyncAdaptedQueuePool(creator, pool_size=5, max_overflow=10, timeout=30.0, use_lifo=False, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | কানেকশন বানানোর ফাংশন। |
| `pool_size` | স্থায়ী কানেকশনের সংখ্যা। |
| `max_overflow` | বাড়তি কানেকশন। |
| `timeout` | অপেক্ষার সর্বোচ্চ সময়। |
| `use_lifo` | LIFO ক্রম। |
| `kw` | `Pool`-এর অপশন। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`QueuePool`](#queuepool-summary)-এর মতো।

## `NullPool` { #nullpool }

```python
from sqlalchemy.pool import NullPool
```

**কোনো পুলিং নয়:** প্রতিটি `connect()`-এ নতুন কানেকশন খোলে, `close()`-এ সত্যিই বন্ধ করে। কখন: PgBouncer/RDS Proxy-র মতো বাইরের পুলার আছে, serverless (Lambda), multiprocessing, বা টেস্টে প্রতিবার পরিষ্কার কানেকশন চাই।

**উদাহরণ:**

```python
eng = create_engine(URL_STR, poolclass=NullPool)
with eng.connect() as c:
    pid1 = c.exec_driver_sql("SELECT pg_backend_pid()").scalar()
with eng.connect() as c:
    pid2 = c.exec_driver_sql("SELECT pg_backend_pid()").scalar()
print(pid1 != pid2)   # True  (প্রতিবার নতুন সার্ভার-প্রসেস, মানে নতুন কানেকশন)
```

### কনস্ট্রাক্টরের প্যারামিটার { #nullpool-params }

```python
NullPool(creator, recycle=-1, echo=None, logging_name=None, reset_on_return=True, events=None, dialect=None, pre_ping=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | কানেকশন বানানোর ফাংশন। |
| `recycle` | (অর্থহীন; কানেকশন রাখা হয় না)। |
| `echo` | লগিং। |
| `logging_name` | লগে নাম। |
| `reset_on_return` | ফেরার সময়ের reset নিয়ম। |
| `events` | event listener-এর তালিকা। |
| `dialect` | ডায়ালেক্ট। |
| `pre_ping` | ping (নতুন কানেকশনে কার্যত অপ্রয়োজনীয়)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Pool`](#pool-summary)-এর মতো।

## `StaticPool` { #staticpool }

```python
from sqlalchemy.pool import StaticPool
```

**ঠিক একটি** কানেকশন রাখে আর সবাইকে সেটাই দেয়। প্রধান ব্যবহার: SQLite in-memory ডেটাবেসের টেস্ট (`sqlite://` + `connect_args={"check_same_thread": False}`), যাতে সব কানেকশন একই মেমরি-ডেটাবেস দেখে।

**উদাহরণ:**

```python
eng = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
with eng.begin() as c:
    c.exec_driver_sql("CREATE TABLE t (x INTEGER)"); c.exec_driver_sql("INSERT INTO t VALUES (1)")
with eng.connect() as c:                       # অন্য "কানেকশনেও" একই ডেটাবেস
    print(c.exec_driver_sql("SELECT count(*) FROM t").scalar())   # 1
```

### কনস্ট্রাক্টরের প্যারামিটার { #staticpool-params }

```python
StaticPool(creator, recycle=-1, echo=None, logging_name=None, reset_on_return=True, events=None, dialect=None, pre_ping=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | কানেকশন বানানোর ফাংশন। |
| `recycle` | recycle সময়। |
| `echo` | লগিং। |
| `logging_name` | লগে নাম। |
| `reset_on_return` | reset নিয়ম। |
| `events` | event listener। |
| `dialect` | ডায়ালেক্ট। |
| `pre_ping` | ping। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #staticpool-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`connection`](#staticpool-connection) | প্রপার্টি | পুলের একমাত্র কানেকশন-রেকর্ড। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `StaticPool`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Pool` থেকে:** [`connect()`](#pool-connect) · [`dispose()`](#pool-dispose) · [`logging_name`](#pool-logging-name) · [`recreate()`](#pool-recreate) · [`status()`](#pool-status)

///

### `StaticPool.connection` { #staticpool-connection }

**ধরন:** প্রপার্টি

পুলের একমাত্র কানেকশন-রেকর্ড।

**উদাহরণ:**

```python
eng = create_engine("sqlite://", poolclass=StaticPool)
with eng.connect():
    pass
print(type(eng.pool.connection).__name__)   # _ConnectionRecord
```

## `SingletonThreadPool` { #singletonthreadpool }

```python
from sqlalchemy.pool import SingletonThreadPool
```

প্রতি **thread**-এ একটি কানেকশন রাখে (একই thread বারবার একই কানেকশন পায়)। মূলত পুরোনো SQLite in-memory ব্যবহারের জন্য; সাধারণ অ্যাপে নয়।

**উদাহরণ:**

```python
pool = SingletonThreadPool(creator, pool_size=5)
a = pool.connect(); a_dbapi = a.dbapi_connection; a.close()
b = pool.connect()
print(b.dbapi_connection is a_dbapi)   # True  (একই thread → একই কানেকশন)
b.close(); pool.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #singletonthreadpool-params }

```python
SingletonThreadPool(creator, pool_size=5, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `creator` | কানেকশন বানানোর ফাংশন। |
| `pool_size` | সর্বোচ্চ কয়টি thread-এর কানেকশন রাখবে। |
| `kw` | `Pool`-এর অপশন। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Pool`](#pool-summary)-এর মতো।

## `AssertionPool` { #assertionpool }

```python
from sqlalchemy.pool import AssertionPool
```

ডিবাগ-পুল: একসাথে **একটির বেশি** কানেকশন ধার দিলে সাথে সাথে এরর দেয়। কোড অজান্তে দুটি কানেকশন খুলছে কি না (বা ফেরত দিচ্ছে না) ধরতে।

**উদাহরণ:**

```python
pool = AssertionPool(creator)
a = pool.connect()
try:
    pool.connect()
except AssertionError as e:
    print(type(e).__name__)   # AssertionError
a.close(); pool.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #assertionpool-params }

```python
AssertionPool(*args, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | `Pool`-এর পজিশনাল আর্গুমেন্ট (`creator`)। |
| `kw` | `Pool`-এর অপশন। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Pool`](#pool-summary)-এর মতো।

## পুলের কানেকশন-অবজেক্ট { #managesconnection-group }

## `ManagesConnection` { #managesconnection }

```python
from sqlalchemy.pool import ManagesConnection
```

পুলের কানেকশন-ধারকদের (`PoolProxiedConnection`, `ConnectionPoolEntry`) সাধারণ ইন্টারফেস: আসল DBAPI কানেকশন, তথ্য-dict, আর invalidate।

**উদাহরণ:**

```python
pool = QueuePool(creator)
c = pool.connect()
print(isinstance(c, ManagesConnection), type(c.dbapi_connection).__module__)   # True psycopg2.extensions
c.close(); pool.dispose()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #managesconnection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`dbapi_connection`](#managesconnection-dbapi-connection) | অ্যাট্রিবিউট | আসল DBAPI কানেকশন অবজেক্ট (যেমন psycopg2-এর `connection`)। |
| [`driver_connection`](#managesconnection-driver-connection) | অ্যাট্রিবিউট | ড্রাইভারের "নিজস্ব" কানেকশন: সাধারণ ড্রাইভারে `dbapi_connection`-এর সমান; asyncpg-এর মতো async ড্রাইভারে মোড়কের ভেতরের আসল asyncpg কানেকশন। |
| [`info`](#managesconnection-info) | প্রপার্টি | DBAPI কানেকশনের সাথে যুক্ত dict; কানেকশন যতদিন বাঁচে ততদিন থাকে (invalidate হলে মুছে যায়)। |
| [`invalidate()`](#managesconnection-invalidate) | মেথড | কানেকশনকে বাতিল চিহ্নিত করে: পুল এটি বন্ধ করে পরের বার নতুন খুলবে। |
| [`record_info`](#managesconnection-record-info) | প্রপার্টি | কানেকশন-**রেকর্ডের** (পুলের স্লটের) সাথে যুক্ত dict: invalidate হয়ে নতুন DBAPI কানেকশন এলেও থেকে যায়। |

### `ManagesConnection.dbapi_connection` { #managesconnection-dbapi-connection }

**ধরন:** অ্যাট্রিবিউট

আসল DBAPI কানেকশন অবজেক্ট (যেমন psycopg2-এর `connection`)। invalidate হলে `None`।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect()
print(c.dbapi_connection.closed)   # 0
c.close(); pool.dispose()
```

### `ManagesConnection.driver_connection` { #managesconnection-driver-connection }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারের "নিজস্ব" কানেকশন: সাধারণ ড্রাইভারে `dbapi_connection`-এর সমান; asyncpg-এর মতো async ড্রাইভারে মোড়কের ভেতরের আসল asyncpg কানেকশন।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect()
print(c.driver_connection is c.dbapi_connection)   # True
c.close(); pool.dispose()
```

### `ManagesConnection.info` { #managesconnection-info }

**ধরন:** প্রপার্টি

DBAPI কানেকশনের সাথে যুক্ত dict; কানেকশন যতদিন বাঁচে ততদিন থাকে (invalidate হলে মুছে যায়)। কানেকশন-ভিত্তিক ক্যাশ রাখতে।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=1)
c = pool.connect(); c.info["seen"] = True; c.close()
print(pool.connect().info.get("seen"))   # True
pool.dispose()
```

### `ManagesConnection.invalidate()` { #managesconnection-invalidate }

```python
ManagesConnection.invalidate(e=None, soft=False)
```

**ধরন:** মেথড

কানেকশনকে বাতিল চিহ্নিত করে: পুল এটি বন্ধ করে পরের বার নতুন খুলবে। `soft=True` দিলে এখন বন্ধ করে না, শুধু পরের checkout-এ বদলায়।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=1)
c = pool.connect(); old = c.dbapi_connection; c.invalidate(); c.close()
print(pool.connect().dbapi_connection is old)   # False
pool.dispose()
```

### `ManagesConnection.record_info` { #managesconnection-record-info }

**ধরন:** প্রপার্টি

কানেকশন-**রেকর্ডের** (পুলের স্লটের) সাথে যুক্ত dict: invalidate হয়ে নতুন DBAPI কানেকশন এলেও থেকে যায়।

**উদাহরণ:**

```python
pool = QueuePool(creator, pool_size=1)
c = pool.connect(); c.record_info["n"] = 1; c.invalidate(); c.close()
print(pool.connect().record_info.get("n"))   # 1
pool.dispose()
```

## `PoolProxiedConnection` { #poolproxiedconnection }

```python
from sqlalchemy.pool import PoolProxiedConnection
```

`pool.connect()` / `engine.raw_connection()` থেকে পাওয়া DBAPI কানেকশনের মোড়ক। DBAPI কানেকশনের মতোই ব্যবহার করা যায় (`cursor()`, `commit()`), পার্থক্য: `close()` পুলে ফেরত দেয়।

**উদাহরণ:**

```python
pool = QueuePool(creator)
c = pool.connect()
cur = c.cursor(); cur.execute("SELECT 41 + 1"); print(cur.fetchone()[0])   # 42
c.close(); pool.dispose()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #poolproxiedconnection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#poolproxiedconnection-close) | মেথড | কানেকশন পুলে ফেরত দেয় (detach হলে আসলেই বন্ধ করে)। |
| [`detach()`](#poolproxiedconnection-detach) | মেথড | কানেকশনকে পুল থেকে আলাদা করে: `close()`-এ পুলে না ফিরে বন্ধ হয়, আর পুল তার জায়গায় নতুন খুলতে পারে। |
| [`is_detached`](#poolproxiedconnection-is-detached) | প্রপার্টি | detach হয়েছে কি না। |
| [`is_valid`](#poolproxiedconnection-is-valid) | প্রপার্টি | এখনো একটি সক্রিয় DBAPI কানেকশন ধরে আছে কি না (invalidate হলে `False`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `PoolProxiedConnection`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ManagesConnection` থেকে:** [`info`](#managesconnection-info) · [`invalidate()`](#managesconnection-invalidate) · [`record_info`](#managesconnection-record-info)

///

### `PoolProxiedConnection.close()` { #poolproxiedconnection-close }

```python
PoolProxiedConnection.close()
```

**ধরন:** মেথড

কানেকশন পুলে ফেরত দেয় (detach হলে আসলেই বন্ধ করে)।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect(); c.close()
print(pool.checkedin())   # 1
pool.dispose()
```

### `PoolProxiedConnection.detach()` { #poolproxiedconnection-detach }

```python
PoolProxiedConnection.detach()
```

**ধরন:** মেথড

কানেকশনকে পুল থেকে আলাদা করে: `close()`-এ পুলে না ফিরে বন্ধ হয়, আর পুল তার জায়গায় নতুন খুলতে পারে।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect(); c.detach()
print(c.is_detached, pool.checkedout())   # True 0
c.close(); pool.dispose()
```

### `PoolProxiedConnection.is_detached` { #poolproxiedconnection-is-detached }

**ধরন:** প্রপার্টি

detach হয়েছে কি না।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect()
print(c.is_detached)   # False
c.close(); pool.dispose()
```

### `PoolProxiedConnection.is_valid` { #poolproxiedconnection-is-valid }

**ধরন:** প্রপার্টি

এখনো একটি সক্রিয় DBAPI কানেকশন ধরে আছে কি না (invalidate হলে `False`)।

**উদাহরণ:**

```python
pool = QueuePool(creator); c = pool.connect()
print(c.is_valid); c.invalidate(); print(c.is_valid)
# True
# False
c.close(); pool.dispose()
```

## `ConnectionPoolEntry` { #connectionpoolentry }

```python
from sqlalchemy.pool import ConnectionPoolEntry
```

পুলের ভেতরের একটি "স্লট" (কানেকশন-রেকর্ড)। পুল event-এ (`connect`, `checkout`) দ্বিতীয় আর্গুমেন্ট হিসেবে আসে; এক স্লটের DBAPI কানেকশন invalidate হয়ে বদলালেও রেকর্ড একই থাকে।

**উদাহরণ:**

```python
seen = []
eng = create_engine(URL_STR)
@event.listens_for(eng, "connect")
def on_connect(dbapi_conn, record):
    seen.append(isinstance(record, ConnectionPoolEntry))
with eng.connect():
    pass
print(seen)   # [True]
eng.dispose()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #connectionpoolentry-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#connectionpoolentry-close) | মেথড | এই রেকর্ডের DBAPI কানেকশন বন্ধ করে। |
| [`in_use`](#connectionpoolentry-in-use) | প্রপার্টি | এখন ধার দেওয়া আছে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ConnectionPoolEntry`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ManagesConnection` থেকে:** [`info`](#managesconnection-info) · [`invalidate()`](#managesconnection-invalidate) · [`record_info`](#managesconnection-record-info)

///

### `ConnectionPoolEntry.close()` { #connectionpoolentry-close }

```python
ConnectionPoolEntry.close()
```

**ধরন:** মেথড

এই রেকর্ডের DBAPI কানেকশন বন্ধ করে।

**উদাহরণ:**

```python
eng = create_engine(URL_STR); recs = []
event.listen(eng, "checkout", lambda dbapi, rec, proxy: recs.append(rec))
with eng.connect():
    pass
recs[0].close()
print(recs[0].dbapi_connection)   # None
eng.dispose()
```

### `ConnectionPoolEntry.in_use` { #connectionpoolentry-in-use }

**ধরন:** প্রপার্টি

এখন ধার দেওয়া আছে কি না।

**উদাহরণ:**

```python
eng = create_engine(URL_STR); recs = []
event.listen(eng, "checkout", lambda dbapi, rec, proxy: recs.append(rec))
with eng.connect():
    print(recs[0].in_use)   # True
print(recs[0].in_use)       # False
eng.dispose()
```

## `PoolResetState` { #poolresetstate }

```python
from sqlalchemy.pool import PoolResetState
```

(২.০.০) কানেকশন পুলে ফেরার সময়ের `reset` event-এ পাওয়া তথ্য: ট্রানজ্যাকশন আগেই শেষ হয়েছিল কি না, কানেকশন বন্ধ হচ্ছে কি না, asyncio-নিরাপদ কি না। নিজের reset-যুক্তি (যেমন `DISCARD ALL`) লিখতে।

**উদাহরণ:**

```python
states = []
eng = create_engine(URL_STR)
@event.listens_for(eng, "reset")
def on_reset(dbapi_conn, record, reset_state):
    states.append(reset_state.transaction_was_reset)
with eng.connect() as c:
    c.exec_driver_sql("SELECT 1")
print(states)   # [True]  (Connection নিজেই rollback করে ফেলেছিল, তাই পুলের আর rollback লাগেনি)
eng.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #poolresetstate-params }

```python
PoolResetState(transaction_was_reset, terminate_only, asyncio_safe)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `transaction_was_reset` | Connection নিজেই ট্রানজ্যাকশন শেষ করেছিল কি না। |
| `terminate_only` | কানেকশন পুলে না ফিরে বন্ধ হচ্ছে কি না। |
| `asyncio_safe` | asyncio কানেকশনে await-যোগ্য কাজ নিরাপদ কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #poolresetstate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`asyncio_safe`](#poolresetstate-asyncio-safe) | অ্যাট্রিবিউট | reset-এর সময় asyncio কাজ (await) নিরাপদ কি না। |
| [`terminate_only`](#poolresetstate-terminate-only) | অ্যাট্রিবিউট | কানেকশন বন্ধ হতে যাচ্ছে (reset অর্থহীন) কি না। |
| [`transaction_was_reset`](#poolresetstate-transaction-was-reset) | অ্যাট্রিবিউট | `Connection` আগেই commit/rollback করে ট্রানজ্যাকশন শেষ করেছিল কি না (তাহলে আবার rollback লাগে না)। |

### `PoolResetState.asyncio_safe` { #poolresetstate-asyncio-safe }

**ধরন:** অ্যাট্রিবিউট

reset-এর সময় asyncio কাজ (await) নিরাপদ কি না।

**উদাহরণ:**

```python
print(PoolResetState(True, False, True).asyncio_safe)   # True
```

### `PoolResetState.terminate_only` { #poolresetstate-terminate-only }

**ধরন:** অ্যাট্রিবিউট

কানেকশন বন্ধ হতে যাচ্ছে (reset অর্থহীন) কি না।

**উদাহরণ:**

```python
print(PoolResetState(False, True, True).terminate_only)   # True
```

### `PoolResetState.transaction_was_reset` { #poolresetstate-transaction-was-reset }

**ধরন:** অ্যাট্রিবিউট

`Connection` আগেই commit/rollback করে ট্রানজ্যাকশন শেষ করেছিল কি না (তাহলে আবার rollback লাগে না)।

**উদাহরণ:**

```python
print(PoolResetState(True, False, True).transaction_was_reset)   # True
```

## `reset_rollback()` { #reset-rollback }

```python
from sqlalchemy.pool import reset_rollback
```

**ধরন:** ধ্রুবক (enum সদস্য)

`reset_on_return`-এর ধ্রুবক: ফেরার সময় `rollback()` (ডিফল্ট)। `"rollback"` স্ট্রিং দিলেও একই। এগুলো একটি enum (`ResetStyle`)-এর সদস্য, তাই আলাদা সদস্য-তালিকা নেই।

**উদাহরণ:**

```python
print(reset_rollback.name)   # reset_rollback
```

## `reset_commit()` { #reset-commit }

```python
from sqlalchemy.pool import reset_commit
```

**ধরন:** ধ্রুবক (enum সদস্য)

`reset_on_return`-এর ধ্রুবক: ফেরার সময় `commit()`। খুব বিশেষ ক্ষেত্র ছাড়া ব্যবহার করবেন না (ভুলে যাওয়া কাজ নিঃশব্দে সেভ হয়ে যায়)।

**উদাহরণ:**

```python
eng = create_engine(URL_STR, pool_reset_on_return="commit")
print(reset_commit.name)   # reset_commit
```

## `reset_none()` { #reset-none }

```python
from sqlalchemy.pool import reset_none
```

**ধরন:** ধ্রুবক (enum সদস্য)

`reset_on_return`-এর ধ্রুবক: ফেরার সময় কিছুই না। শুধু তখন নিরাপদ যখন কানেকশনগুলো autocommit মোডে, বা নিজের `reset` event দিয়ে পরিষ্কার করছেন।

**উদাহরণ:**

```python
print(reset_none.name)   # reset_none
```

/// check | সংক্ষেপে মনে রাখুন

* সাধারণ অ্যাপ: ডিফল্ট `QueuePool` + `pool_pre_ping=True`; `pool_size + max_overflow` × worker সংখ্যা < ডেটাবেসের `max_connections`।
* PgBouncer/serverless: `poolclass=NullPool`।
* SQLite in-memory টেস্ট: `StaticPool` + `check_same_thread=False`।
* লিক সন্দেহ হলে: `engine.pool.status()` দেখুন, বা টেস্টে `AssertionPool`।
* কানেকশন খোলার সময় কিছু সেট করতে (timezone, search_path): পুলের `connect` event।

///
