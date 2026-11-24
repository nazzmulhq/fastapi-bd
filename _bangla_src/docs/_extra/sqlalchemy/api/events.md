# Core Event API: listen(), Pool, Connection, Dialect ও DDL event { #api-events }

/// note | এই পেজে যা আছে

* event নিবন্ধনের ফাংশন: `event.listen()`, `@event.listens_for`, `event.remove()`, `event.contains()`।
* Core-এর **সব** event hook: `PoolEvents` (১০টি), `ConnectionEvents` (১৮টি), `DialectEvents` (৬টি), `DDLEvents` (৭টি)।
* ORM-এর event (`SessionEvents`, `MapperEvents`, `InstanceEvents`, `AttributeEvents` …) আছে [ORM Event পেজে](orm-events.md)।

///

**event** মানে: "যখন X ঘটবে, তখন আমার এই ফাংশনটি ডাকো।" SQLAlchemy-র কোড না বদলে তার আচরণে হুক বসানো যায়: প্রতিটি নতুন কানেকশনে timezone সেট করা, ধীর কুয়েরি লগ করা, SQL-এ comment যোগ করা, টেবিল তৈরির পর trigger বানানো। প্রতিটি সদস্যের সিগনেচারই আপনার listener ফাংশনের সিগনেচার।

/// warning | সাধারণ ভুল

* listener-এর ভেতরে ভারী কাজ বা নতুন কুয়েরি সাবধানে; প্রতিটি কুয়েরি/কানেকশনে চলে।
* `Engine`-এ listener বসালে সেই engine-এর সব কানেকশনে চলে; `Engine` **ক্লাসে** বসালে সব engine-এ।
* async engine-এ Core event বসাতে `async_engine.sync_engine` ব্যবহার করুন।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

প্রতিটি উদাহরণ নিজের নতুন `engine` (PostgreSQL 16, psycopg2) আর `users` টেবিল (`id`, `name`) পায়; `calls` একটি খালি তালিকা যেখানে listener-গুলো কী ঘটল তা লিখে রাখে।

///

## event নিবন্ধন { #listen-group }

## `listen()` { #listen }

```python
from sqlalchemy import event
```

```python
listen(target, identifier, fn, *args, **kw)
```

**ধরন:** ফাংশন

একটি টার্গেটে (engine, pool, Session, মডেল ক্লাস, অ্যাট্রিবিউট, টেবিল …) একটি event-এর listener বসায়। নাম স্ট্রিং হিসেবে দিন (`"connect"`, `"before_flush"`)। কিছু event-এ বাড়তি অপশন আছে: `retval=True` (listener-এর ফেরত মান ব্যবহার হবে), `propagate=True` (সাবক্লাসেও প্রযোজ্য), `once=True` (শুধু প্রথমবার), `insert=True` (তালিকার শুরুতে)।

**উদাহরণ:**

```python
def set_tz(dbapi_conn, record):
    cur = dbapi_conn.cursor(); cur.execute("SET TIME ZONE 'Asia/Dhaka'"); cur.close()

event.listen(engine, "connect", set_tz)
with engine.connect() as c:
    print(c.exec_driver_sql("SHOW TimeZone").scalar())   # Asia/Dhaka
```

### `listen()`-এর সব প্যারামিটার { #listen-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | যেখানে বসবে: Engine, Pool, Connection, Session/sessionmaker, মডেল ক্লাস, `Mapper`, অ্যাট্রিবিউট (`User.name`), `Table`, `MetaData` … |
| `identifier` | event-এর নাম। |
| `fn` | listener ফাংশন। |
| `args` | বাড়তি পজিশনাল আর্গুমেন্ট (খুব কম ব্যবহৃত)। |
| `kw` | `retval`, `propagate`, `once`, `insert`, `named` (listener-এ আর্গুমেন্টগুলো keyword হিসেবে আসবে), `raw`, `restore_load_context` ইত্যাদি event-নির্দিষ্ট অপশন। |

## `listens_for()` { #listens-for }

```python
from sqlalchemy import event
```

```python
listens_for(target, identifier, *args, **kw)
```

**ধরন:** ফাংশন

`listen()`-এর ডেকোরেটর রূপ (বেশি প্রচলিত)।

**উদাহরণ:**

```python
@event.listens_for(engine, "before_cursor_execute")
def log_sql(conn, cursor, statement, parameters, context, executemany):
    calls.append(statement.split()[0])

with engine.connect() as c:
    c.execute(select(users))
print(calls)   # ['SELECT']
```

### `listens_for()`-এর সব প্যারামিটার { #listens-for-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | টার্গেট। |
| `identifier` | event-এর নাম। |
| `args` | বাড়তি পজিশনাল আর্গুমেন্ট। |
| `kw` | `listen()`-এর মতো অপশন। |

## `remove()` { #remove }

```python
from sqlalchemy import event
```

```python
remove(target, identifier, fn)
```

**ধরন:** ফাংশন

আগে বসানো listener সরিয়ে দেয় (একই টার্গেট, নাম আর ফাংশন দিতে হবে)। টেস্টে সাময়িক listener-এর জন্য।

**উদাহরণ:**

```python
def on_checkout(dbapi_conn, record, proxy):
    calls.append("checkout")

event.listen(engine, "checkout", on_checkout)
with engine.connect():
    pass
event.remove(engine, "checkout", on_checkout)
with engine.connect():
    pass
print(calls)   # ['checkout']
```

### `remove()`-এর সব প্যারামিটার { #remove-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | টার্গেট। |
| `identifier` | event-এর নাম। |
| `fn` | যে listener সরাতে হবে। |

## `contains()` { #contains }

```python
from sqlalchemy import event
```

```python
contains(target, identifier, fn)
```

**ধরন:** ফাংশন

একটি listener বসানো আছে কি না।

**উদাহরণ:**

```python
def f(*a): pass
event.listen(engine, "checkin", f)
print(event.contains(engine, "checkin", f), event.contains(engine, "connect", f))   # True False
```

### `contains()`-এর সব প্যারামিটার { #contains-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | টার্গেট। |
| `identifier` | event-এর নাম। |
| `fn` | listener। |

## Event ক্লাস { #poolevents-group }

## `PoolEvents` { #poolevents }

```python
from sqlalchemy.events import PoolEvents
```

কানেকশন পুলের event: কানেকশন তৈরি, ধার দেওয়া, ফেরত, বাতিল। টার্গেট: `Engine` (তার পুল), `Pool` অবজেক্ট, বা `Pool` ক্লাস। প্রথম দুটি আর্গুমেন্ট সাধারণত DBAPI কানেকশন আর `ConnectionPoolEntry`।

**উদাহরণ:**

```python
for name in ["connect", "first_connect", "checkout", "checkin"]:
    event.listen(engine, name, lambda *a, n=name: calls.append(n))
with engine.connect():
    pass
print(calls)   # ['first_connect', 'connect', 'checkout', 'checkin']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #poolevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`checkin()`](#poolevents-checkin) | মেথড | কানেকশন পুলে ফেরত আসার সময়। |
| [`checkout()`](#poolevents-checkout) | মেথড | পুল থেকে কানেকশন ধার দেওয়ার সময়। |
| [`close()`](#poolevents-close) | মেথড | পুলের একটি কানেকশন সত্যিই বন্ধ হওয়ার সময় (dispose, recycle, invalidate)। |
| [`close_detached()`](#poolevents-close-detached) | মেথড | detach করা কানেকশন বন্ধ হওয়ার সময়। |
| [`connect()`](#poolevents-connect) | মেথড | একটি **নতুন** DBAPI কানেকশন তৈরি হওয়ার মুহূর্তে (প্রতিটির জন্য একবার)। |
| [`detach()`](#poolevents-detach) | মেথড | কানেকশন পুল থেকে detach হওয়ার সময়। |
| [`first_connect()`](#poolevents-first-connect) | মেথড | পুলের **প্রথম** কানেকশনে একবারই (ডায়ালেক্ট এখানে সার্ভারের ভার্সন ইত্যাদি জেনে নেয়)। |
| [`invalidate()`](#poolevents-invalidate) | মেথড | কানেকশন invalidate (বাতিল) হওয়ার সময়, সাথে কারণ (exception) থাকলে সেটি। |
| [`reset()`](#poolevents-reset) | মেথড | কানেকশন পুলে ফেরার আগে "reset" (rollback) হওয়ার সময়; `PoolResetState` দিয়ে জানা যায় কী অবস্থা। |
| [`soft_invalidate()`](#poolevents-soft-invalidate) | মেথড | "soft" invalidate: কানেকশন এখন চলতে থাকবে, কিন্তু পরের checkout-এ বদলানো হবে। |

### `PoolEvents.checkin()` { #poolevents-checkin }

```python
PoolEvents.checkin(dbapi_connection, connection_record)
```

**ধরন:** মেথড

কানেকশন পুলে ফেরত আসার সময়। (কানেকশন invalidate হয়ে থাকলে DBAPI কানেকশন `None` হতে পারে।)

**উদাহরণ:**

```python
event.listen(engine, "checkin", lambda dbapi, rec: calls.append("ফেরত"))
with engine.connect():
    pass
print(calls)   # ['ফেরত']
```

### `PoolEvents.checkout()` { #poolevents-checkout }

```python
PoolEvents.checkout(dbapi_connection, connection_record, connection_proxy)
```

**ধরন:** মেথড

পুল থেকে কানেকশন ধার দেওয়ার সময়। এখানে `exc.DisconnectionError` raise করলে পুল কানেকশনটি বাদ দিয়ে আরেকটি নেয় (নিজের pre-ping লেখার উপায়)।

**উদাহরণ:**

```python
@event.listens_for(engine, "checkout")
def ping(dbapi_conn, record, proxy):
    calls.append(record.info.setdefault("n", 0) + 1); record.info["n"] += 1
for _ in range(2):
    with engine.connect():
        pass
print(calls)   # [1, 2]  (একই কানেকশন দুবার ধার দেওয়া হলো)
```

### `PoolEvents.close()` { #poolevents-close }

```python
PoolEvents.close(dbapi_connection, connection_record)
```

**ধরন:** মেথড

পুলের একটি কানেকশন সত্যিই বন্ধ হওয়ার সময় (dispose, recycle, invalidate)।

**উদাহরণ:**

```python
event.listen(engine, "close", lambda dbapi, rec: calls.append("বন্ধ"))
with engine.connect():
    pass
engine.dispose()
print(calls)   # ['বন্ধ']
```

### `PoolEvents.close_detached()` { #poolevents-close-detached }

```python
PoolEvents.close_detached(dbapi_connection)
```

**ধরন:** মেথড

detach করা কানেকশন বন্ধ হওয়ার সময়।

**উদাহরণ:**

```python
event.listen(engine, "close_detached", lambda dbapi: calls.append("detached বন্ধ"))
with engine.connect() as c:
    c.detach()
print(calls)   # ['detached বন্ধ']
```

### `PoolEvents.connect()` { #poolevents-connect }

```python
PoolEvents.connect(dbapi_connection, connection_record)
```

**ধরন:** মেথড

একটি **নতুন** DBAPI কানেকশন তৈরি হওয়ার মুহূর্তে (প্রতিটির জন্য একবার)। প্রতি কানেকশনে সেটিং বসানোর জায়গা: timezone, `search_path`, SQLite-এর `PRAGMA foreign_keys=ON`।

**উদাহরণ:**

```python
@event.listens_for(engine, "connect")
def on_connect(dbapi_conn, record):
    cur = dbapi_conn.cursor(); cur.execute("SET search_path TO public"); cur.close()
    calls.append("নতুন কানেকশন")
with engine.connect(): pass
with engine.connect(): pass
print(calls)   # ['নতুন কানেকশন']  (দ্বিতীয়বার পুল থেকে পুরোনোটা)
```

### `PoolEvents.detach()` { #poolevents-detach }

```python
PoolEvents.detach(dbapi_connection, connection_record)
```

**ধরন:** মেথড

কানেকশন পুল থেকে detach হওয়ার সময়।

**উদাহরণ:**

```python
event.listen(engine, "detach", lambda dbapi, rec: calls.append("detach"))
with engine.connect() as c:
    c.detach()
print(calls)   # ['detach']
```

### `PoolEvents.first_connect()` { #poolevents-first-connect }

```python
PoolEvents.first_connect(dbapi_connection, connection_record)
```

**ধরন:** মেথড

পুলের **প্রথম** কানেকশনে একবারই (ডায়ালেক্ট এখানে সার্ভারের ভার্সন ইত্যাদি জেনে নেয়)।

**উদাহরণ:**

```python
event.listen(engine, "first_connect", lambda dbapi, rec: calls.append("প্রথম"))
with engine.connect(): pass
with engine.connect(): pass
print(calls)   # ['প্রথম']
```

### `PoolEvents.invalidate()` { #poolevents-invalidate }

```python
PoolEvents.invalidate(dbapi_connection, connection_record, exception)
```

**ধরন:** মেথড

কানেকশন invalidate (বাতিল) হওয়ার সময়, সাথে কারণ (exception) থাকলে সেটি।

**উদাহরণ:**

```python
event.listen(engine, "invalidate", lambda dbapi, rec, e: calls.append(type(e).__name__ if e else None))
with engine.connect() as c:
    c.invalidate(RuntimeError("ডেমো"))
print(calls)   # ['RuntimeError']
```

### `PoolEvents.reset()` { #poolevents-reset }

```python
PoolEvents.reset(dbapi_connection, connection_record, reset_state)
```

**ধরন:** মেথড

কানেকশন পুলে ফেরার আগে "reset" (rollback) হওয়ার সময়; `PoolResetState` দিয়ে জানা যায় কী অবস্থা। নিজে পরিষ্কার করতে (যেমন `DISCARD ALL`) এখানে।

**উদাহরণ:**

```python
event.listen(engine, "reset", lambda dbapi, rec, st: calls.append(st.transaction_was_reset))
with engine.connect() as c:
    c.exec_driver_sql("SELECT 1")
print(calls)   # [True]
```

### `PoolEvents.soft_invalidate()` { #poolevents-soft-invalidate }

```python
PoolEvents.soft_invalidate(dbapi_connection, connection_record, exception)
```

**ধরন:** মেথড

"soft" invalidate: কানেকশন এখন চলতে থাকবে, কিন্তু পরের checkout-এ বদলানো হবে।

**উদাহরণ:**

```python
event.listen(engine, "soft_invalidate", lambda dbapi, rec, e: calls.append("soft"))
with engine.connect() as c:
    c.connection.invalidate(soft=True)
print(calls)   # ['soft']
```

## `ConnectionEvents` { #connectionevents }

```python
from sqlalchemy.events import ConnectionEvents
```

`Connection`/`Engine`-এর event: স্টেটমেন্ট চালানো, ট্রানজ্যাকশন, SAVEPOINT, two-phase। টার্গেট: `Engine`, `Connection`, বা `Engine` ক্লাস। সবচেয়ে বেশি ব্যবহৃত `before_cursor_execute` / `after_cursor_execute` (SQL লগিং, ধীর-কুয়েরি মাপা, SQL comment যোগ)।

**উদাহরণ:**

```python
import time
@event.listens_for(engine, "before_cursor_execute")
def start(conn, cursor, stmt, params, ctx, many):
    conn.info["t0"] = time.perf_counter()
@event.listens_for(engine, "after_cursor_execute")
def end(conn, cursor, stmt, params, ctx, many):
    calls.append(time.perf_counter() - conn.info.pop("t0") < 5)
with engine.connect() as c:
    c.execute(text("SELECT pg_sleep(0.01)"))
print(calls)   # [True]  (সময় মাপা হলো)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #connectionevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`after_cursor_execute()`](#connectionevents-after-cursor-execute) | মেথড | ড্রাইভারে SQL চালানোর ঠিক **পরে** (কাঁচা SQL স্ট্রিং ও প্যারামিটারসহ)। |
| [`after_execute()`](#connectionevents-after-execute) | মেথড | উচ্চ-স্তরের `execute()` শেষ হলে (SQLAlchemy স্টেটমেন্ট অবজেক্ট আর রেজাল্টসহ)। |
| [`before_cursor_execute()`](#connectionevents-before-cursor-execute) | মেথড | ড্রাইভারে SQL পাঠানোর ঠিক **আগে**। |
| [`before_execute()`](#connectionevents-before-execute) | মেথড | উচ্চ-স্তরের `execute()` শুরু হওয়ার আগে (স্টেটমেন্ট অবজেক্ট আকারে; `retval=True` দিয়ে বদলানো যায়)। |
| [`begin()`](#connectionevents-begin) | মেথড | ট্রানজ্যাকশন শুরু হওয়ার সময়। |
| [`begin_twophase()`](#connectionevents-begin-twophase) | মেথড | two-phase ট্রানজ্যাকশন শুরু হওয়ার সময়। |
| [`commit()`](#connectionevents-commit) | মেথড | ট্রানজ্যাকশন commit-এর সময়। |
| [`commit_twophase()`](#connectionevents-commit-twophase) | মেথড | two-phase commit-এর সময় (`is_prepared` সহ)। |
| [`engine_connect()`](#connectionevents-engine-connect) | মেথড | একটি নতুন `Connection` অবজেক্ট তৈরি হওয়ার সময় (প্রতি `engine.connect()`-এ; নতুন DBAPI কানেকশন না হলেও)। |
| [`engine_disposed()`](#connectionevents-engine-disposed) | মেথড | `engine.dispose()` ডাকা হলে। |
| [`prepare_twophase()`](#connectionevents-prepare-twophase) | মেথড | two-phase ট্রানজ্যাকশনের `prepare()`-এর সময়। |
| [`release_savepoint()`](#connectionevents-release-savepoint) | মেথড | SAVEPOINT release (সফল nested commit)-এর সময়। |
| [`rollback()`](#connectionevents-rollback) | মেথড | ট্রানজ্যাকশন rollback-এর সময়। |
| [`rollback_savepoint()`](#connectionevents-rollback-savepoint) | মেথড | SAVEPOINT-এ rollback-এর সময়। |
| [`rollback_twophase()`](#connectionevents-rollback-twophase) | মেথড | two-phase rollback-এর সময়। |
| [`savepoint()`](#connectionevents-savepoint) | মেথড | SAVEPOINT তৈরির সময় (নামসহ)। |
| [`set_connection_execution_options()`](#connectionevents-set-connection-execution-options) | মেথড | `connection.execution_options(...)` ডাকা হলে (অপশন যাচাই/প্রয়োগ করতে)। |
| [`set_engine_execution_options()`](#connectionevents-set-engine-execution-options) | মেথড | `engine.execution_options(...)` ডাকা হলে। |

### `ConnectionEvents.after_cursor_execute()` { #connectionevents-after-cursor-execute }

```python
ConnectionEvents.after_cursor_execute(conn, cursor, statement, parameters, context, executemany)
```

**ধরন:** মেথড

ড্রাইভারে SQL চালানোর ঠিক **পরে** (কাঁচা SQL স্ট্রিং ও প্যারামিটারসহ)। সময় মাপা, লগিং।

**উদাহরণ:**

```python
event.listen(engine, "after_cursor_execute", lambda conn, cur, s, p, ctx, many: calls.append(cur.rowcount))
with engine.begin() as c:
    c.execute(insert(users), [{"name": "ক"}, {"name": "খ"}])
print(calls)   # [2]
```

### `ConnectionEvents.after_execute()` { #connectionevents-after-execute }

```python
ConnectionEvents.after_execute(conn, clauseelement, multiparams, params, execution_options, result)
```

**ধরন:** মেথড

উচ্চ-স্তরের `execute()` শেষ হলে (SQLAlchemy স্টেটমেন্ট অবজেক্ট আর রেজাল্টসহ)।

**উদাহরণ:**

```python
event.listen(engine, "after_execute", lambda conn, clause, mp, p, opts, result: calls.append(type(clause).__name__))
with engine.connect() as c:
    c.execute(select(users))
print(calls)   # ['Select']
```

### `ConnectionEvents.before_cursor_execute()` { #connectionevents-before-cursor-execute }

```python
ConnectionEvents.before_cursor_execute(conn, cursor, statement, parameters, context, executemany)
```

**ধরন:** মেথড

ড্রাইভারে SQL পাঠানোর ঠিক **আগে**। `retval=True` দিয়ে বসালে `(statement, parameters)` ফেরত দিয়ে SQL বদলানো যায় (যেমন শুরুতে ট্রেসিং comment)।

**উদাহরণ:**

```python
@event.listens_for(engine, "before_cursor_execute", retval=True)
def add_comment(conn, cursor, statement, parameters, context, executemany):
    return "/* app=shop */ " + statement, parameters
with engine.connect() as c:
    print(c.exec_driver_sql("SELECT current_query()").scalar())   # /* app=shop */ SELECT current_query()
```

### `ConnectionEvents.before_execute()` { #connectionevents-before-execute }

```python
ConnectionEvents.before_execute(conn, clauseelement, multiparams, params, execution_options)
```

**ধরন:** মেথড

উচ্চ-স্তরের `execute()` শুরু হওয়ার আগে (স্টেটমেন্ট অবজেক্ট আকারে; `retval=True` দিয়ে বদলানো যায়)।

**উদাহরণ:**

```python
event.listen(engine, "before_execute", lambda conn, clause, mp, p, opts: calls.append(str(clause).split()[0]))
with engine.connect() as c:
    c.execute(select(users.c.id))
print(calls)   # ['SELECT']
```

### `ConnectionEvents.begin()` { #connectionevents-begin }

```python
ConnectionEvents.begin(conn)
```

**ধরন:** মেথড

ট্রানজ্যাকশন শুরু হওয়ার সময়।

**উদাহরণ:**

```python
event.listen(engine, "begin", lambda conn: calls.append("BEGIN"))
with engine.begin():
    pass
print(calls)   # ['BEGIN']
```

### `ConnectionEvents.begin_twophase()` { #connectionevents-begin-twophase }

```python
ConnectionEvents.begin_twophase(conn, xid)
```

**ধরন:** মেথড

two-phase ট্রানজ্যাকশন শুরু হওয়ার সময়।

**উদাহরণ:**

```python
def on_begin_2pc(conn, xid):
    calls.append(xid)
event.listen(engine, "begin_twophase", on_begin_2pc)
print(event.contains(engine, "begin_twophase", on_begin_2pc))   # True  (PostgreSQL-এ max_prepared_transactions চালু থাকলে চলবে)
```

### `ConnectionEvents.commit()` { #connectionevents-commit }

```python
ConnectionEvents.commit(conn)
```

**ধরন:** মেথড

ট্রানজ্যাকশন commit-এর সময়।

**উদাহরণ:**

```python
event.listen(engine, "commit", lambda conn: calls.append("COMMIT"))
with engine.begin() as c:
    c.execute(insert(users).values(name="ক"))
print(calls)   # ['COMMIT']
```

### `ConnectionEvents.commit_twophase()` { #connectionevents-commit-twophase }

```python
ConnectionEvents.commit_twophase(conn, xid, is_prepared)
```

**ধরন:** মেথড

two-phase commit-এর সময় (`is_prepared` সহ)।

**উদাহরণ:**

```python
def on_commit_2pc(conn, xid, is_prepared):
    calls.append(is_prepared)
event.listen(engine, "commit_twophase", on_commit_2pc)
print(event.contains(engine, "commit_twophase", on_commit_2pc))   # True
```

### `ConnectionEvents.engine_connect()` { #connectionevents-engine-connect }

```python
ConnectionEvents.engine_connect(conn)
```

**ধরন:** মেথড

একটি নতুন `Connection` অবজেক্ট তৈরি হওয়ার সময় (প্রতি `engine.connect()`-এ; নতুন DBAPI কানেকশন না হলেও)।

**উদাহরণ:**

```python
event.listen(engine, "engine_connect", lambda conn: calls.append("connect()"))
with engine.connect(): pass
with engine.connect(): pass
print(calls)   # ['connect()', 'connect()']
```

### `ConnectionEvents.engine_disposed()` { #connectionevents-engine-disposed }

```python
ConnectionEvents.engine_disposed(engine)
```

**ধরন:** মেথড

`engine.dispose()` ডাকা হলে।

**উদাহরণ:**

```python
event.listen(engine, "engine_disposed", lambda eng: calls.append("disposed"))
engine.dispose()
print(calls)   # ['disposed']
```

### `ConnectionEvents.prepare_twophase()` { #connectionevents-prepare-twophase }

```python
ConnectionEvents.prepare_twophase(conn, xid)
```

**ধরন:** মেথড

two-phase ট্রানজ্যাকশনের `prepare()`-এর সময়।

**উদাহরণ:**

```python
def on_prepare_2pc(conn, xid):
    calls.append(xid)
event.listen(engine, "prepare_twophase", on_prepare_2pc)
print(event.contains(engine, "prepare_twophase", on_prepare_2pc))   # True
```

### `ConnectionEvents.release_savepoint()` { #connectionevents-release-savepoint }

```python
ConnectionEvents.release_savepoint(conn, name, context)
```

**ধরন:** মেথড

SAVEPOINT release (সফল nested commit)-এর সময়।

**উদাহরণ:**

```python
event.listen(engine, "release_savepoint", lambda conn, name, ctx: calls.append("RELEASE"))
with engine.begin() as c:
    with c.begin_nested():
        pass
print(calls)   # ['RELEASE']
```

### `ConnectionEvents.rollback()` { #connectionevents-rollback }

```python
ConnectionEvents.rollback(conn)
```

**ধরন:** মেথড

ট্রানজ্যাকশন rollback-এর সময়।

**উদাহরণ:**

```python
event.listen(engine, "rollback", lambda conn: calls.append("ROLLBACK"))
with engine.connect() as c:
    c.exec_driver_sql("SELECT 1")
print(calls)   # ['ROLLBACK']  (commit ছাড়া বন্ধ হলে rollback)
```

### `ConnectionEvents.rollback_savepoint()` { #connectionevents-rollback-savepoint }

```python
ConnectionEvents.rollback_savepoint(conn, name, context)
```

**ধরন:** মেথড

SAVEPOINT-এ rollback-এর সময়।

**উদাহরণ:**

```python
event.listen(engine, "rollback_savepoint", lambda conn, name, ctx: calls.append("ROLLBACK TO"))
with engine.begin() as c:
    c.begin_nested().rollback()
print(calls)   # ['ROLLBACK TO']
```

### `ConnectionEvents.rollback_twophase()` { #connectionevents-rollback-twophase }

```python
ConnectionEvents.rollback_twophase(conn, xid, is_prepared)
```

**ধরন:** মেথড

two-phase rollback-এর সময়।

**উদাহরণ:**

```python
def on_rollback_2pc(conn, xid, is_prepared):
    calls.append(xid)
event.listen(engine, "rollback_twophase", on_rollback_2pc)
print(event.contains(engine, "rollback_twophase", on_rollback_2pc))   # True
```

### `ConnectionEvents.savepoint()` { #connectionevents-savepoint }

```python
ConnectionEvents.savepoint(conn, name)
```

**ধরন:** মেথড

SAVEPOINT তৈরির সময় (নামসহ)।

**উদাহরণ:**

```python
event.listen(engine, "savepoint", lambda conn, name: calls.append("SAVEPOINT"))
with engine.begin() as c:
    c.begin_nested()
print(calls)   # ['SAVEPOINT']
```

### `ConnectionEvents.set_connection_execution_options()` { #connectionevents-set-connection-execution-options }

```python
ConnectionEvents.set_connection_execution_options(conn, opts)
```

**ধরন:** মেথড

`connection.execution_options(...)` ডাকা হলে (অপশন যাচাই/প্রয়োগ করতে)।

**উদাহরণ:**

```python
event.listen(engine, "set_connection_execution_options", lambda conn, opts: calls.append(dict(opts)))
with engine.connect() as c:
    c.execution_options(logging_token="req-1")
print(calls)   # [{'logging_token': 'req-1'}]
```

### `ConnectionEvents.set_engine_execution_options()` { #connectionevents-set-engine-execution-options }

```python
ConnectionEvents.set_engine_execution_options(engine, opts)
```

**ধরন:** মেথড

`engine.execution_options(...)` ডাকা হলে।

**উদাহরণ:**

```python
event.listen(engine, "set_engine_execution_options", lambda eng, opts: calls.append(dict(opts)))
engine.execution_options(stream_results=True)
print(calls)   # [{'stream_results': True}]
```

## `DialectEvents` { #dialectevents }

```python
from sqlalchemy.events import DialectEvents
```

ডায়ালেক্ট-স্তরের নিচু event: কানেকশন তৈরি, ড্রাইভারে execute, আর সব এরর সামলানো। টার্গেট: `Engine` বা `Dialect` ক্লাস। বেশিরভাগ ক্ষেত্রে `ConnectionEvents` যথেষ্ট; এগুলো লাগে ড্রাইভারের আচরণ বদলাতে।

**উদাহরণ:**

```python
@event.listens_for(engine, "do_connect")
def provide_password(dialect, conn_rec, cargs, cparams):
    cparams["application_name"] = "shop-api"        # যেমন: প্রতিবার নতুন token/পাসওয়ার্ড বসানো
with engine.connect() as c:
    print(c.exec_driver_sql("SHOW application_name").scalar())   # shop-api
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dialectevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`do_connect()`](#dialectevents-do-connect) | মেথড | DBAPI `connect()` ডাকার আগে: `cparams` dict বদলে কানেকশন-আর্গুমেন্ট বদলানো যায় (যেমন AWS IAM / Azure-এর মেয়াদি token প্রতিবার নতুন করে বসানো)। |
| [`do_execute()`](#dialectevents-do-execute) | মেথড | প্যারামিটারসহ `cursor.execute()` ডাকার আগে; `True` ফেরত দিলে SQLAlchemy নিজে আর execute করে না (আপনি করেছেন ধরে নেয়)। |
| [`do_execute_no_params()`](#dialectevents-do-execute-no-params) | মেথড | প্যারামিটার ছাড়া `cursor.execute()`-এর আগে। |
| [`do_executemany()`](#dialectevents-do-executemany) | মেথড | `cursor.executemany()`-এর আগে (বাল্ক INSERT/UPDATE; insertmanyvalues ব্যবহার হলে নাও আসতে পারে)। |
| [`do_setinputsizes()`](#dialectevents-do-setinputsizes) | মেথড | যেসব ড্রাইভার `setinputsizes()` ব্যবহার করে (cx_Oracle, pyodbc), তাদের টাইপ-তথ্য বদলানোর সুযোগ। |
| [`handle_error()`](#dialectevents-handle-error) | মেথড | SQLAlchemy যেকোনো ড্রাইভার-এরর সামলানোর সময়: `ExceptionContext` দিয়ে মূল এরর, স্টেটমেন্ট, "কানেকশন বিচ্ছিন্ন কি না" জানা যায়; নতুন exception ফেরত দিয়ে এরর বদলানো, বা `is_disconnect` সেট করা যায়। |

### `DialectEvents.do_connect()` { #dialectevents-do-connect }

```python
DialectEvents.do_connect(dialect, conn_rec, cargs, cparams)
```

**ধরন:** মেথড

DBAPI `connect()` ডাকার আগে: `cparams` dict বদলে কানেকশন-আর্গুমেন্ট বদলানো যায় (যেমন AWS IAM / Azure-এর মেয়াদি token প্রতিবার নতুন করে বসানো)। একটি কানেকশন ফেরত দিলে SQLAlchemy সেটিই ব্যবহার করে।

**উদাহরণ:**

```python
event.listen(engine, "do_connect", lambda d, rec, cargs, cparams: calls.append(sorted(cparams)))
with engine.connect(): pass
print(calls)   # [['dbname', 'host', 'user']]
```

### `DialectEvents.do_execute()` { #dialectevents-do-execute }

```python
DialectEvents.do_execute(cursor, statement, parameters, context)
```

**ধরন:** মেথড

প্যারামিটারসহ `cursor.execute()` ডাকার আগে; `True` ফেরত দিলে SQLAlchemy নিজে আর execute করে না (আপনি করেছেন ধরে নেয়)।

**উদাহরণ:**

```python
event.listen(engine, "do_execute", lambda cur, stmt, params, ctx: calls.append(params))
with engine.connect() as c:
    c.execute(select(users).where(users.c.id == 5))
print(calls)   # [{'id_1': 5}]
```

### `DialectEvents.do_execute_no_params()` { #dialectevents-do-execute-no-params }

```python
DialectEvents.do_execute_no_params(cursor, statement, context)
```

**ধরন:** মেথড

প্যারামিটার ছাড়া `cursor.execute()`-এর আগে।

**উদাহরণ:**

```python
event.listen(engine, "do_execute_no_params", lambda cur, stmt, ctx: calls.append(stmt))
with engine.connect() as c:
    c.execution_options(no_parameters=True).exec_driver_sql("SELECT 1")
print(calls)   # ['SELECT 1']
```

### `DialectEvents.do_executemany()` { #dialectevents-do-executemany }

```python
DialectEvents.do_executemany(cursor, statement, parameters, context)
```

**ধরন:** মেথড

`cursor.executemany()`-এর আগে (বাল্ক INSERT/UPDATE; insertmanyvalues ব্যবহার হলে নাও আসতে পারে)।

**উদাহরণ:**

```python
event.listen(engine, "do_executemany", lambda cur, stmt, params, ctx: calls.append(len(params)))
with engine.begin() as c:
    c.execute(users.update().where(users.c.id == 0).values(name="x"), [{}, {}])
print(calls)   # [2]
```

### `DialectEvents.do_setinputsizes()` { #dialectevents-do-setinputsizes }

```python
DialectEvents.do_setinputsizes(inputsizes, cursor, statement, parameters, context)
```

**ধরন:** মেথড

যেসব ড্রাইভার `setinputsizes()` ব্যবহার করে (cx_Oracle, pyodbc), তাদের টাইপ-তথ্য বদলানোর সুযোগ। psycopg2-তে ডাকা হয় না।

**উদাহরণ:**

```python
event.listen(engine, "do_setinputsizes", lambda sizes, cur, s, p, ctx: calls.append(1))
with engine.connect() as c:
    c.execute(select(users))
print(calls)   # []  (psycopg2 এটি ব্যবহার করে না)
```

### `DialectEvents.handle_error()` { #dialectevents-handle-error }

```python
DialectEvents.handle_error(exception_context)
```

**ধরন:** মেথড

SQLAlchemy যেকোনো ড্রাইভার-এরর সামলানোর সময়: `ExceptionContext` দিয়ে মূল এরর, স্টেটমেন্ট, "কানেকশন বিচ্ছিন্ন কি না" জানা যায়; নতুন exception ফেরত দিয়ে এরর বদলানো, বা `is_disconnect` সেট করা যায়।

**উদাহরণ:**

```python
@event.listens_for(engine, "handle_error")
def on_error(ctx):
    calls.append((type(ctx.original_exception).__name__, ctx.is_disconnect))
with engine.connect() as c:
    try:
        c.exec_driver_sql("SELECT * FROM no_such_table")
    except exc.ProgrammingError:
        pass
print(calls)   # [('UndefinedTable', False)]
```

## `DDLEvents` { #ddlevents }

```python
from sqlalchemy.events import DDLEvents
```

স্কিমা-অবজেক্টের event: টেবিল/MetaData তৈরি-মোছার আগে-পরে, একটি অবজেক্ট আরেকটির সাথে যুক্ত হলে, আর reflection-এ কলাম পড়ার সময়। টার্গেট: `Table`, `MetaData`, `Column`, `Index`, `Constraint` ইত্যাদি।

**উদাহরণ:**

```python
m = MetaData()
t = Table("logs", m, Column("id", Integer, primary_key=True), Column("msg", String))
event.listen(t, "after_create", DDL("CREATE INDEX ix_logs_msg_lower ON logs (lower(msg))"))
m.create_all(engine)
print([i["name"] for i in inspect(engine).get_indexes("logs")])   # ['ix_logs_msg_lower']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #ddlevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`after_create()`](#ddlevents-after-create) | মেথড | টেবিল (বা MetaData-র সব টেবিল) তৈরির পরে। |
| [`after_drop()`](#ddlevents-after-drop) | মেথড | মোছার পরে। |
| [`after_parent_attach()`](#ddlevents-after-parent-attach) | মেথড | একটি অবজেক্ট (কলাম, কনস্ট্রেইন্ট) তার প্যারেন্টের (টেবিল) সাথে যুক্ত হওয়ার পরে। |
| [`before_create()`](#ddlevents-before-create) | মেথড | তৈরির আগে (যেমন প্রয়োজনীয় extension বা schema আগে বানাতে)। |
| [`before_drop()`](#ddlevents-before-drop) | মেথড | মোছার আগে। |
| [`before_parent_attach()`](#ddlevents-before-parent-attach) | মেথড | প্যারেন্টের সাথে যুক্ত হওয়ার ঠিক আগে। |
| [`column_reflect()`](#ddlevents-column-reflect) | মেথড | reflection-এ প্রতিটি কলামের তথ্য পড়ার সময়: dict বদলে কলামের key, টাইপ ইত্যাদি বদলানো যায় (যেমন ডেটাবেসের `UserName` → Python-এ `user_name`)। |

### `DDLEvents.after_create()` { #ddlevents-after-create }

```python
DDLEvents.after_create(target, connection, **kw)
```

**ধরন:** মেথড

টেবিল (বা MetaData-র সব টেবিল) তৈরির পরে। বাড়তি DDL (trigger, function, বিশেষ ইনডেক্স) বসানোর জায়গা; `DDL(...)` সরাসরি listener হিসেবে দেওয়া যায়।

**উদাহরণ:**

```python
m = MetaData(); t = Table("t1", m, Column("id", Integer, primary_key=True))
event.listen(t, "after_create", lambda target, conn, **kw: calls.append(target.name))
m.create_all(engine)
print(calls)   # ['t1']
```

### `DDLEvents.after_drop()` { #ddlevents-after-drop }

```python
DDLEvents.after_drop(target, connection, **kw)
```

**ধরন:** মেথড

মোছার পরে।

**উদাহরণ:**

```python
m = MetaData(); t = Table("t1", m, Column("id", Integer, primary_key=True))
m.create_all(engine)
event.listen(m, "after_drop", lambda target, conn, **kw: calls.append("সব মোছা শেষ"))
m.drop_all(engine)
print(calls)   # ['সব মোছা শেষ']
```

### `DDLEvents.after_parent_attach()` { #ddlevents-after-parent-attach }

```python
DDLEvents.after_parent_attach(target, parent)
```

**ধরন:** মেথড

একটি অবজেক্ট (কলাম, কনস্ট্রেইন্ট) তার প্যারেন্টের (টেবিল) সাথে যুক্ত হওয়ার পরে। নিজে থেকে কনস্ট্রেইন্ট/comment বসানোর কৌশলে।

**উদাহরণ:**

```python
c = Column("email", String)
event.listen(c, "after_parent_attach", lambda col, table: calls.append(f"{table.name}.{col.name}"))
Table("people", MetaData(), c)
print(calls)   # ['people.email']
```

### `DDLEvents.before_create()` { #ddlevents-before-create }

```python
DDLEvents.before_create(target, connection, **kw)
```

**ধরন:** মেথড

তৈরির আগে (যেমন প্রয়োজনীয় extension বা schema আগে বানাতে)।

**উদাহরণ:**

```python
m = MetaData(); Table("t1", m, Column("id", Integer, primary_key=True))
event.listen(m, "before_create", DDL("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
m.create_all(engine)
with engine.connect() as c:
    print(c.exec_driver_sql("SELECT count(*) FROM pg_extension WHERE extname='pg_trgm'").scalar())   # 1
```

### `DDLEvents.before_drop()` { #ddlevents-before-drop }

```python
DDLEvents.before_drop(target, connection, **kw)
```

**ধরন:** মেথড

মোছার আগে।

**উদাহরণ:**

```python
m = MetaData(); t = Table("t1", m, Column("id", Integer, primary_key=True))
m.create_all(engine)
event.listen(t, "before_drop", lambda target, conn, **kw: calls.append(conn.scalar(text("SELECT 1"))))
m.drop_all(engine)
print(calls)   # [1]
```

### `DDLEvents.before_parent_attach()` { #ddlevents-before-parent-attach }

```python
DDLEvents.before_parent_attach(target, parent)
```

**ধরন:** মেথড

প্যারেন্টের সাথে যুক্ত হওয়ার ঠিক আগে।

**উদাহরণ:**

```python
c = Column("x", Integer)
event.listen(c, "before_parent_attach", lambda col, table: calls.append(table.name))
Table("tt", MetaData(), c)
print(calls)   # ['tt']
```

### `DDLEvents.column_reflect()` { #ddlevents-column-reflect }

```python
DDLEvents.column_reflect(inspector, table, column_info)
```

**ধরন:** মেথড

reflection-এ প্রতিটি কলামের তথ্য পড়ার সময়: dict বদলে কলামের key, টাইপ ইত্যাদি বদলানো যায় (যেমন ডেটাবেসের `UserName` → Python-এ `user_name`)। সাধারণত `MetaData`-তে বা `Table` ক্লাসে বসানো হয়।

**উদাহরণ:**

```python
m = MetaData()
@event.listens_for(m, "column_reflect")
def lower_key(inspector, table, column_info):
    column_info["key"] = "col_" + column_info["name"]
t = Table("users", m, autoload_with=engine)
print(list(t.c.keys()))   # ['col_id', 'col_name']
```

/// check | সংক্ষেপে মনে রাখুন

* প্রতি নতুন কানেকশনে সেটিং: `@event.listens_for(engine, "connect")`।
* SQL লগ/সময় মাপা: `before_cursor_execute` + `after_cursor_execute` (`conn.info` দিয়ে মান পাস করুন)।
* SQL বদলানো (comment যোগ): `before_cursor_execute` + `retval=True`।
* মেয়াদি token দিয়ে কানেকশন: `do_connect`-এ `cparams` বদলান।
* টেবিল তৈরির পর বাড়তি SQL: `event.listen(table, "after_create", DDL(...))`।
* async engine: `event.listen(async_engine.sync_engine, ...)`।

///
