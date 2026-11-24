# Engine, Connection ও URL API: create_engine() থেকে Transaction { #api-engine }

/// note | এই পেজে যা আছে

* `create_engine()`-এর **প্রতিটি** অপশন (পুল, লগিং, isolation level, ক্যাশ, JSON …), আর `engine_from_config()`, `create_mock_engine()`, `create_pool_from_url()`, `make_url()`।
* `Engine`, `Connection`-এর **সব** সদস্য।
* `Transaction`, `RootTransaction`, `NestedTransaction` (SAVEPOINT), `TwoPhaseTransaction`।
* `URL` (ডেটাবেস ঠিকানা) আর `CreateEnginePlugin`।

///

**Engine** হলো ডেটাবেসের সাথে যোগাযোগের কেন্দ্র: একটি কানেকশন পুল আর একটি ডায়ালেক্ট (কোন ডেটাবেস, কোন ড্রাইভার)। অ্যাপে **একবারই** বানান (মডিউল-স্তরে), প্রতি রিকোয়েস্টে নয়। **Connection** হলো পুল থেকে ধার নেওয়া একটি কানেকশন; কাজ শেষে `with` ব্লক থেকে বেরোলেই পুলে ফেরত যায়। ORM-এর `Session` ভেতরে এগুলোই ব্যবহার করে। async সংস্করণ (`create_async_engine`, `AsyncEngine`) আছে [Async API পেজে](async.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
URL_STR = "postgresql+psycopg2://postgres@127.0.0.1/apiref"
engine = create_engine(URL_STR)

md = MetaData()
users = Table("users", md, Column("id", Integer, primary_key=True), Column("name", String(50)))
md.create_all(engine)    # তিনজন ইউজার: রহিম, করিম, সুমি
```

`count()` টেবিলে কয়টি রো আছে দেখায় (নতুন কানেকশনে, অর্থাৎ শুধু commit হওয়া ডেটা)। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## Engine তৈরির ফাংশন { #create-engine-group }

## `create_engine()` { #create-engine }

```python
from sqlalchemy import create_engine
```

```python
create_engine(url, **kwargs)
```

**ধরন:** ফাংশন

একটি ডেটাবেস URL থেকে `Engine` বানায়। URL-এর রূপ: `ডায়ালেক্ট+ড্রাইভার://ইউজার:পাসওয়ার্ড@হোস্ট:পোর্ট/ডেটাবেস?অপশন`। **২.১-এ পরিবর্তন:** ড্রাইভার না লিখলে (`postgresql://...`) এখন psycopg 3 (`psycopg`) ব্যবহার হয়, আগে ছিল psycopg2; তাই ড্রাইভার সবসময় স্পষ্ট লিখুন (`postgresql+psycopg2://`, `postgresql+psycopg://`, `postgresql+asyncpg://`)। এখানে কোনো কানেকশন খোলে না; প্রথম `connect()`-এ খোলে। পাসওয়ার্ডে `@`, `/` ইত্যাদি থাকলে URL-এ সরাসরি না লিখে `URL.create()` ব্যবহার করুন।

**উদাহরণ:**

```python
eng = create_engine(URL_STR, pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=1800)
with eng.connect() as conn:
    print(conn.scalar(text("SELECT 1 + 1")))   # 2
print(eng.dialect.name, eng.driver, type(eng.pool).__name__)   # postgresql psycopg2 QueuePool
eng.dispose()
```

### `create_engine()`-এর সব প্যারামিটার { #create-engine-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `url` | ডেটাবেস URL: স্ট্রিং বা `URL` অবজেক্ট। |
| `kwargs` | • **পুল:** `pool_size` (ডিফল্ট ৫: পুলে স্থায়ী কানেকশন), `max_overflow` (ডিফল্ট ১০: চাপের সময় বাড়তি কানেকশন), `pool_timeout` (ডিফল্ট ৩০ সেকেন্ড: খালি কানেকশনের জন্য কতক্ষণ অপেক্ষা), `pool_recycle` (এত সেকেন্ডের পুরোনো কানেকশন নতুন করে খোলে; ফায়ারওয়াল/MySQL-এর idle-timeout এড়াতে), `pool_pre_ping` (প্রতিবার ধার দেওয়ার আগে কানেকশন বেঁচে আছে কি না যাচাই; প্রোডাকশনে `True` দিন), `pool_use_lifo` (সবচেয়ে সাম্প্রতিক কানেকশন আগে দেয়), `pool_reset_on_return` (`"rollback"` ডিফল্ট), `poolclass` (যেমন `NullPool`), `pool` (তৈরি করা পুল অবজেক্ট), `pool_logging_name`, `echo_pool`।<br>• **লগিং:** `echo=True` (সব SQL লগ করে; `"debug"` দিলে রো-ও), `hide_parameters=True` (লগে প্যারামিটারের মান লুকায়, পাসওয়ার্ড ইত্যাদির জন্য), `logging_name`।<br>• **কানেকশন:** `connect_args` (ড্রাইভারের `connect()`-এ বাড়তি অপশন, যেমন `{"connect_timeout": 5}` বা `{"options": "-c statement_timeout=5000"}`), `creator` (নিজের কানেকশন-বানানো ফাংশন), `isolation_level` (`"READ COMMITTED"`, `"REPEATABLE READ"`, `"SERIALIZABLE"`, `"AUTOCOMMIT"`), `module` (ভিন্ন DBAPI মডিউল), `paramstyle`।<br>• **এক্সিকিউশন:** `execution_options` (সব কানেকশনের ডিফল্ট অপশন, যেমন `{"schema_translate_map": ...}`), `query_cache_size` (ডিফল্ট ৫০০; ০ = ক্যাশ বন্ধ), `use_insertmanyvalues` ও `insertmanyvalues_page_size` (বাল্ক INSERT...RETURNING-এর পেজ-আকার, ডিফল্ট ১০০০), `enable_from_linting` (cartesian product হলে সতর্কবার্তা; ডিফল্ট `True`), `skip_autocommit_rollback` (২.০.৪৩: autocommit কানেকশনে অপ্রয়োজনীয় rollback বাদ)।<br>• **অন্যান্য:** `json_serializer` / `json_deserializer` (যেমন `orjson`), `label_length`, `max_identifier_length`, `plugins`, `future` (২.০-তে অর্থহীন, শুধু পুরোনো কোডের জন্য), `empty_in_strategy` (আর ব্যবহার হয় না)। |

**পাসওয়ার্ডে বিশেষ অক্ষর থাকলে URL.create(), আর প্রতি কানেকশনে statement timeout**

```python
url = URL.create("postgresql+psycopg2", username="postgres", password="p@ss/w:rd", host="127.0.0.1", database="apiref")
print(url)   # postgresql+psycopg2://postgres:***@127.0.0.1/apiref
eng = create_engine(URL_STR, connect_args={"options": "-c statement_timeout=2000"})
with eng.connect() as conn:
    print(conn.exec_driver_sql("SHOW statement_timeout").scalar())   # 2s
eng.dispose()
```

## `engine_from_config()` { #engine-from-config }

```python
from sqlalchemy import engine_from_config
```

```python
engine_from_config(configuration, prefix='sqlalchemy.', **kwargs)
```

**ধরন:** ফাংশন

একটি কনফিগ dict (যেমন `.ini` ফাইল থেকে পড়া) থেকে Engine বানায়: `sqlalchemy.url`, `sqlalchemy.echo` ইত্যাদি prefix-যুক্ত key পড়ে, আর স্ট্রিং মান (`"true"`, `"10"`) সঠিক টাইপে রূপান্তর করে।

**উদাহরণ:**

```python
cfg = {"sqlalchemy.url": URL_STR, "sqlalchemy.pool_size": "3", "sqlalchemy.echo": "false", "other.key": "x"}
eng = engine_from_config(cfg)
print(eng.pool.size(), eng.echo)   # 3 False
eng.dispose()
```

### `engine_from_config()`-এর সব প্যারামিটার { #engine-from-config-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `configuration` | কনফিগ dict। |
| `prefix` | যে prefix-যুক্ত key-গুলো পড়া হবে (ডিফল্ট `"sqlalchemy."`)। |
| `kwargs` | বাড়তি `create_engine()` অপশন (কনফিগের ওপরে বসে)। |

## `create_mock_engine()` { #create-mock-engine }

```python
from sqlalchemy import create_mock_engine
```

```python
create_mock_engine(url, executor, **kw)
```

**ধরন:** ফাংশন

একটি "নকল" engine যা SQL চালায় না, প্রতিটি স্টেটমেন্ট আপনার ফাংশনে পাঠায়। ডেটাবেস ছাড়াই পুরো স্কিমার DDL স্ক্রিপ্ট বানাতে (`metadata.create_all()`-এর আউটপুট ফাইলে লেখা) কাজে লাগে।

**উদাহরণ:**

```python
out = []
mock = create_mock_engine("postgresql+psycopg2://", lambda sql, *a, **kw: out.append(str(sql.compile(dialect=mock.dialect)).strip()))
md.create_all(mock, checkfirst=False)
print(out[0].splitlines()[0])   # CREATE TABLE users (
```

### `create_mock_engine()`-এর সব প্যারামিটার { #create-mock-engine-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `url` | ডায়ালেক্ট বোঝাতে URL (শুধু ডায়ালেক্ট অংশ লাগে)। |
| `executor` | প্রতিটি স্টেটমেন্ট নিয়ে ডাকা ফাংশন `(sql, *multiparams, **params)`। |
| `kw` | বাড়তি অপশন। |

## `create_pool_from_url()` { #create-pool-from-url }

```python
from sqlalchemy import create_pool_from_url
```

```python
create_pool_from_url(url, **kwargs)
```

**ধরন:** ফাংশন

(২.০.১০) Engine ছাড়া শুধু একটি কানেকশন পুল বানায় (URL আর `pool_size` ইত্যাদি অপশন থেকে)। কাঁচা DBAPI কানেকশন পুল দরকার এমন বিশেষ ক্ষেত্রে।

**উদাহরণ:**

```python
pool = create_pool_from_url(URL_STR, pool_size=2)
conn = pool.connect()
print(type(pool).__name__, conn.cursor().connection is not None)   # QueuePool True
conn.close(); pool.dispose()
```

### `create_pool_from_url()`-এর সব প্যারামিটার { #create-pool-from-url-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `url` | ডেটাবেস URL। |
| `kwargs` | পুলের অপশন (`pool_size`, `poolclass`, `pre_ping` …; `pool_` prefix ছাড়াও দেওয়া যায়)। |

## `make_url()` { #make-url }

```python
from sqlalchemy import make_url
```

```python
make_url(name_or_url, *, keep_blank_values=False)
```

**ধরন:** ফাংশন

স্ট্রিং থেকে একটি `URL` অবজেক্ট বানায় (অংশগুলো আলাদা করে পড়তে/বদলাতে)।

**উদাহরণ:**

```python
u = make_url("postgresql+asyncpg://app:secret@db.example.com:6432/shop?ssl=require")
print(u.drivername, u.host, u.port, u.database, dict(u.query))   # postgresql+asyncpg db.example.com 6432 shop {'ssl': 'require'}
```

### `make_url()`-এর সব প্যারামিটার { #make-url-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name_or_url` | URL স্ট্রিং বা `URL`। |
| `keep_blank_values` | (২.১.৬) `True` দিলে `?key=` ধরনের খালি মানের query অপশনও রাখে। |

## `result_tuple()` { #result-tuple }

```python
from sqlalchemy.engine import result_tuple
```

```python
result_tuple(fields, extra=None)
```

**ধরন:** ফাংশন

নির্দিষ্ট কলাম-নামের `Row` বানানোর একটি ফ্যাক্টরি দেয়; ORM ও extension ভেতরে ব্যবহার করে। অ্যাপ কোডে সাধারণত দরকার হয় না।

**উদাহরণ:**

```python
from sqlalchemy.engine import result_tuple
make_row = result_tuple(["id", "name"])
r = make_row((1, "রহিম"))
print(r.name, r._mapping["id"])   # রহিম 1
```

### `result_tuple()`-এর সব প্যারামিটার { #result-tuple-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `fields` | কলামের নামগুলো। |
| `extra` | ভেতরের বাড়তি তথ্য। |

## `connection_memoize()` { #connection-memoize }

```python
from sqlalchemy.engine import connection_memoize
```

```python
connection_memoize(key)
```

**ধরন:** ফাংশন

ডেকোরেটর: একটি কানেকশনের ওপর চলা ফাংশনের ফল `connection.info`-তে রেখে দেয়, পরের বার আবার না চালিয়ে সেটাই দেয় (ডায়ালেক্ট ভেতরে ব্যবহার করে)।

**উদাহরণ:**

```python
from sqlalchemy.engine import connection_memoize

class Probe:
    @connection_memoize("_server_version")
    def version(self, connection):
        return connection.exec_driver_sql("SHOW server_version_num").scalar()

p = Probe()
print(p.version(engine) == p.version(engine))   # True  (দ্বিতীয়বার কুয়েরি চলেনি, connection.info থেকে এসেছে)
```

### `connection_memoize()`-এর সব প্যারামিটার { #connection-memoize-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | `connection.info`-এ যে key-তে ফল রাখা হবে। |

## Engine ও Connection { #engine-group }

## `Engine` { #engine }

```python
from sqlalchemy import Engine
```

`create_engine()`-এর ফল। thread-safe, তাই পুরো অ্যাপে একটি শেয়ার করুন। কাজ করতে `connect()` (নিজে commit) বা `begin()` (ব্লক শেষে নিজে থেকে commit) দিয়ে একটি `Connection` নিন।

**উদাহরণ:**

```python
with engine.begin() as conn:                       # ব্লক সফলভাবে শেষ হলে COMMIT, এরর হলে ROLLBACK
    conn.execute(insert(users).values(name="নতুন"))
print(count())   # 4
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #engine-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`begin()`](#engine-begin) | মেথড | একটি কানেকশন খুলে ট্রানজ্যাকশন শুরু করে (context manager)। |
| [`clear_compiled_cache()`](#engine-clear-compiled-cache) | মেথড | কম্পাইল করা SQL-এর ক্যাশ খালি করে (মেমরি পরীক্ষা বা টেস্টে)। |
| [`connect()`](#engine-connect) | মেথড | পুল থেকে একটি `Connection` দেয়। |
| [`dialect`](#engine-dialect) | অ্যাট্রিবিউট | ব্যবহৃত `Dialect` অবজেক্ট (ডেটাবেস-নির্দিষ্ট আচরণ: SQL কম্পাইল, টাইপ, ড্রাইভার)। |
| [`dispose()`](#engine-dispose) | মেথড | পুলের সব কানেকশন বন্ধ করে নতুন একটি খালি পুল বসায়। |
| [`driver`](#engine-driver) | প্রপার্টি | DBAPI ড্রাইভারের নাম। |
| [`echo`](#engine-echo) | প্রপার্টি | SQL লগিং চালু/বন্ধ; রানটাইমে বদলানো যায় (`engine.echo = True`)। |
| [`engine`](#engine-engine) | প্রপার্টি | নিজেকেই দেয় (`Connection.engine`-এর সাথে একই ইন্টারফেসের জন্য)। |
| [`execution_options()`](#engine-execution-options) | মেথড | নির্দিষ্ট execution option-সহ একটি **নতুন** Engine-রূপ দেয় (একই পুল শেয়ার করে)। |
| [`get_execution_options()`](#engine-get-execution-options) | মেথড | সেট করা execution option-গুলো। |
| [`hide_parameters`](#engine-hide-parameters) | অ্যাট্রিবিউট | লগ/এরর মেসেজে প্যারামিটারের মান লুকানো হবে কি না। |
| [`logging_name`](#engine-logging-name) | অ্যাট্রিবিউট | লগ রেকর্ডে এই engine-এর নাম (না দিলে `None`)। |
| [`name`](#engine-name) | প্রপার্টি | ডায়ালেক্টের নাম। |
| [`pool`](#engine-pool) | অ্যাট্রিবিউট | কানেকশন পুল অবজেক্ট (`QueuePool` ইত্যাদি; বিস্তারিত [পুল পেজে](pool.md))। |
| [`raw_connection()`](#engine-raw-connection) | মেথড | SQLAlchemy-র `Connection` ছাড়া সরাসরি DBAPI কানেকশন (পুল-মোড়ানো) দেয়; ড্রাইভারের বিশেষ ফিচার (যেমন psycopg2-এর `copy_expert`) লাগলে। |
| [`update_execution_options()`](#engine-update-execution-options) | মেথড | এই engine-এর ডিফল্ট execution option **জায়গাতেই** বদলায় (নতুন রূপ নয়)। |
| [`url`](#engine-url) | অ্যাট্রিবিউট | engine-এর `URL` (পাসওয়ার্ড লুকিয়ে দেখায়)। |

### `Engine.begin()` { #engine-begin }

```python
Engine.begin()
```

**ধরন:** মেথড

একটি কানেকশন খুলে ট্রানজ্যাকশন শুরু করে (context manager)। ব্লক সফল হলে **commit**, exception হলে **rollback**, শেষে কানেকশন পুলে ফেরত। "কাজ করো আর সেভ করো"-এর সবচেয়ে নিরাপদ রূপ।

**উদাহরণ:**

```python
try:
    with engine.begin() as conn:
        conn.execute(insert(users).values(name="এক"))
        raise RuntimeError("মাঝপথে সমস্যা")
except RuntimeError:
    pass
print(count())   # 3  (rollback হয়েছে)
```

### `Engine.clear_compiled_cache()` { #engine-clear-compiled-cache }

```python
Engine.clear_compiled_cache()
```

**ধরন:** মেথড

কম্পাইল করা SQL-এর ক্যাশ খালি করে (মেমরি পরীক্ষা বা টেস্টে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.execute(select(users.c.name))
engine.clear_compiled_cache()   # পরের কুয়েরি আবার কম্পাইল হবে
print("ok")   # ok
```

### `Engine.connect()` { #engine-connect }

```python
Engine.connect()
```

**ধরন:** মেথড

পুল থেকে একটি `Connection` দেয়। ট্রানজ্যাকশন প্রথম স্টেটমেন্টে নিজে থেকে শুরু হয় (autobegin); **`conn.commit()` না ডাকলে** কানেকশন বন্ধের সময় rollback হয়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.execute(insert(users).values(name="সেভ হবে না"))
print(count())   # 3
with engine.connect() as conn:
    conn.execute(insert(users).values(name="সেভ হবে"))
    conn.commit()
print(count())   # 4
```

### `Engine.dialect` { #engine-dialect }

**ধরন:** অ্যাট্রিবিউট

ব্যবহৃত `Dialect` অবজেক্ট (ডেটাবেস-নির্দিষ্ট আচরণ: SQL কম্পাইল, টাইপ, ড্রাইভার)।

**উদাহরণ:**

```python
print(engine.dialect.name, engine.dialect.server_version_info is None)   # postgresql False
```

### `Engine.dispose()` { #engine-dispose }

```python
Engine.dispose(close=True)
```

**ধরন:** মেথড

পুলের সব কানেকশন বন্ধ করে নতুন একটি খালি পুল বসায়। অ্যাপ বন্ধের সময় (FastAPI lifespan-এর শেষে), টেস্টের শেষে, বা **fork-এর পর চাইল্ড প্রসেসে** (`dispose(close=False)`, যাতে প্যারেন্টের কানেকশনে হাত না পড়ে) ডাকুন।

**উদাহরণ:**

```python
with engine.connect():
    pass
print(engine.pool.checkedin())   # 1
engine.dispose()
print(engine.pool.checkedin())   # 0
```

### `Engine.driver` { #engine-driver }

**ধরন:** প্রপার্টি

DBAPI ড্রাইভারের নাম।

**উদাহরণ:**

```python
print(engine.driver)   # psycopg2
```

### `Engine.echo` { #engine-echo }

**ধরন:** প্রপার্টি

SQL লগিং চালু/বন্ধ; রানটাইমে বদলানো যায় (`engine.echo = True`)।

**উদাহরণ:**

```python
print(engine.echo)   # None  (echo দেওয়া হয়নি)
```

### `Engine.engine` { #engine-engine }

**ধরন:** প্রপার্টি

নিজেকেই দেয় (`Connection.engine`-এর সাথে একই ইন্টারফেসের জন্য)।

**উদাহরণ:**

```python
print(engine.engine is engine)   # True
```

### `Engine.execution_options()` { #engine-execution-options }

```python
Engine.execution_options(**opt)
```

**ধরন:** মেথড

নির্দিষ্ট execution option-সহ একটি **নতুন** Engine-রূপ দেয় (একই পুল শেয়ার করে)। যেমন একটি "AUTOCOMMIT" রূপ, বা ভিন্ন স্কিমা ম্যাপ।

**উদাহরণ:**

```python
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
with autocommit_engine.connect() as conn:
    conn.execute(insert(users).values(name="অটো"))   # commit ছাড়াই সাথে সাথে সেভ
print(count(), autocommit_engine.pool is engine.pool)   # 4 True
```

### `Engine.get_execution_options()` { #engine-get-execution-options }

```python
Engine.get_execution_options()
```

**ধরন:** মেথড

সেট করা execution option-গুলো।

**উদাহরণ:**

```python
print(dict(engine.execution_options(stream_results=True).get_execution_options()))   # {'stream_results': True}
```

### `Engine.hide_parameters` { #engine-hide-parameters }

**ধরন:** অ্যাট্রিবিউট

লগ/এরর মেসেজে প্যারামিটারের মান লুকানো হবে কি না।

**উদাহরণ:**

```python
print(create_engine(URL_STR, hide_parameters=True).hide_parameters)   # True
```

### `Engine.logging_name` { #engine-logging-name }

**ধরন:** অ্যাট্রিবিউট

লগ রেকর্ডে এই engine-এর নাম (না দিলে `None`)।

**উদাহরণ:**

```python
print(create_engine(URL_STR, logging_name="main").logging_name)   # main
```

### `Engine.name` { #engine-name }

**ধরন:** প্রপার্টি

ডায়ালেক্টের নাম।

**উদাহরণ:**

```python
print(engine.name)   # postgresql
```

### `Engine.pool` { #engine-pool }

**ধরন:** অ্যাট্রিবিউট

কানেকশন পুল অবজেক্ট (`QueuePool` ইত্যাদি; বিস্তারিত [পুল পেজে](pool.md))।

**উদাহরণ:**

```python
print(type(engine.pool).__name__, engine.pool.size(), engine.pool.checkedout())   # QueuePool 5 0
```

### `Engine.raw_connection()` { #engine-raw-connection }

```python
Engine.raw_connection()
```

**ধরন:** মেথড

SQLAlchemy-র `Connection` ছাড়া সরাসরি DBAPI কানেকশন (পুল-মোড়ানো) দেয়; ড্রাইভারের বিশেষ ফিচার (যেমন psycopg2-এর `copy_expert`) লাগলে। `close()` করলে পুলে ফেরত যায়।

**উদাহরণ:**

```python
raw = engine.raw_connection()
try:
    cur = raw.cursor(); cur.execute("SELECT count(*) FROM users"); print(cur.fetchone()[0])   # 3
finally:
    raw.close()
```

### `Engine.update_execution_options()` { #engine-update-execution-options }

```python
Engine.update_execution_options(**opt)
```

**ধরন:** মেথড

এই engine-এর ডিফল্ট execution option **জায়গাতেই** বদলায় (নতুন রূপ নয়)।

**উদাহরণ:**

```python
engine.update_execution_options(compiled_cache=None)
print("compiled_cache" in engine.get_execution_options())   # True
```

### `Engine.url` { #engine-url }

**ধরন:** অ্যাট্রিবিউট

engine-এর `URL` (পাসওয়ার্ড লুকিয়ে দেখায়)।

**উদাহরণ:**

```python
print(create_engine("postgresql+psycopg2://u:secret@h/db").url)   # postgresql+psycopg2://u:***@h/db
```

## `Connection` { #connection }

```python
from sqlalchemy import Connection
```

পুল থেকে নেওয়া একটি ডেটাবেস কানেকশন: SQL চালানো (`execute()`, `scalar()`, `scalars()`, `exec_driver_sql()`), ট্রানজ্যাকশন (`commit()`, `rollback()`, `begin_nested()`), আর কানেকশন-স্তরের অপশন। **thread-safe নয়**: প্রতি thread/task-এ আলাদা কানেকশন নিন, আর সবসময় `with` দিয়ে ব্যবহার করুন।

**উদাহরণ:**

```python
with engine.connect() as conn:
    rows = conn.execute(select(users.c.id, users.c.name).where(users.c.id < 3).order_by(users.c.id)).all()
    print([tuple(r) for r in rows])   # [(1, 'রহিম'), (2, 'করিম')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #connection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`begin()`](#connection-begin) | মেথড | স্পষ্টভাবে ট্রানজ্যাকশন শুরু করে (`RootTransaction`); context manager হিসেবে ব্লক শেষে commit/rollback। |
| [`begin_nested()`](#connection-begin-nested) | মেথড | ট্রানজ্যাকশনের ভেতরে একটি **SAVEPOINT**: শুধু এই অংশ rollback করা যায়, বাইরের কাজ থাকে। |
| [`begin_twophase()`](#connection-begin-twophase) | মেথড | two-phase (XA) ট্রানজ্যাকশন শুরু করে: একাধিক ডেটাবেসে একসাথে commit নিশ্চিত করতে (`prepare()` তারপর `commit()`)। |
| [`close()`](#connection-close) | মেথড | কানেকশন বন্ধ করে পুলে ফেরত দেয় (চলমান ট্রানজ্যাকশন rollback হয়)। |
| [`closed`](#connection-closed) | প্রপার্টি | কানেকশন বন্ধ কি না। |
| [`commit()`](#connection-commit) | মেথড | চলমান ট্রানজ্যাকশন commit করে। |
| [`commit_prepared()`](#connection-commit-prepared) | মেথড | আগে `prepare()` করা একটি two-phase ট্রানজ্যাকশন (xid দিয়ে) commit করে; ক্র্যাশের পর পুনরুদ্ধারে। |
| [`connection`](#connection-connection) | প্রপার্টি | নিচের DBAPI কানেকশন (পুল-মোড়ানো `PoolProxiedConnection`)। |
| [`default_isolation_level`](#connection-default-isolation-level) | প্রপার্টি | কানেকশন খোলার সময় ডেটাবেসের ডিফল্ট isolation level। |
| [`detach()`](#connection-detach) | মেথড | কানেকশনটিকে পুল থেকে আলাদা করে: `close()` করলে পুলে না ফিরে আসলেই বন্ধ হয়। |
| [`dialect`](#connection-dialect) | অ্যাট্রিবিউট | ব্যবহৃত ডায়ালেক্ট। |
| [`engine`](#connection-engine) | অ্যাট্রিবিউট | যে Engine থেকে কানেকশনটি এসেছে। |
| [`exec_driver_sql()`](#connection-exec-driver-sql) | মেথড | একটি কাঁচা SQL স্ট্রিং সরাসরি ড্রাইভারে চালায় (SQLAlchemy-র কম্পাইল ছাড়া)। |
| [`execute()`](#connection-execute) | মেথড | একটি স্টেটমেন্ট (`select()`, `insert()`, `text()` …) চালিয়ে `CursorResult` দেয়। |
| [`execution_options()`](#connection-execution-options) | মেথড | এই কানেকশনের execution option সেট করে (জায়গাতেই): `isolation_level`, `stream_results`, `yield_per`, `schema_translate_map`, `logging_token`, `compiled_cache` ইত্যাদি। |
| [`get_execution_options()`](#connection-get-execution-options) | মেথড | সেট করা execution option-গুলো। |
| [`get_isolation_level()`](#connection-get-isolation-level) | মেথড | ডেটাবেসে এই কানেকশনের **বর্তমান** isolation level (একটি কুয়েরি চালিয়ে জানে)। |
| [`get_nested_transaction()`](#connection-get-nested-transaction) | মেথড | চলমান SAVEPOINT (`NestedTransaction`), না থাকলে `None`। |
| [`get_transaction()`](#connection-get-transaction) | মেথড | চলমান মূল ট্রানজ্যাকশন, না থাকলে `None`। |
| [`in_nested_transaction()`](#connection-in-nested-transaction) | মেথড | SAVEPOINT চলছে কি না। |
| [`in_transaction()`](#connection-in-transaction) | মেথড | ট্রানজ্যাকশন চলছে কি না। |
| [`info`](#connection-info) | প্রপার্টি | নিচের DBAPI কানেকশনের সাথে যুক্ত dict: কানেকশন পুলে ফিরলেও থেকে যায়। |
| [`invalidate()`](#connection-invalidate) | মেথড | কানেকশনটিকে "নষ্ট" ঘোষণা করে: পুল এটিকে আর ব্যবহার করবে না, পরের কাজে নতুন কানেকশন খুলবে। |
| [`invalidated`](#connection-invalidated) | প্রপার্টি | কানেকশন invalidate হয়েছে কি না। |
| [`recover_twophase()`](#connection-recover-twophase) | মেথড | ডেটাবেসে "prepared" অবস্থায় আটকে থাকা two-phase ট্রানজ্যাকশনগুলোর xid তালিকা দেয়। |
| [`rollback()`](#connection-rollback) | মেথড | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`rollback_prepared()`](#connection-rollback-prepared) | মেথড | `prepare()` করা two-phase ট্রানজ্যাকশন rollback করে। |
| [`scalar()`](#connection-scalar) | মেথড | স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলাম দেয় (রো না থাকলে `None`)। |
| [`scalars()`](#connection-scalars) | মেথড | স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলামের `ScalarResult` দেয়। |
| [`schema_for_object()`](#connection-schema-for-object) | মেথড | একটি স্কিমা-অবজেক্টের আসল স্কিমা নাম দেয়, `schema_translate_map` হিসাবে নিয়ে (মাল্টি-টেন্যান্টে কাজে লাগে)। |
| [`should_close_with_result`](#connection-should-close-with-result) | অ্যাট্রিবিউট (internal) | (পুরোনো API-র অবশেষ) রেজাল্ট শেষ হলে কানেকশন বন্ধ হবে কি না; ২.০-তে সবসময় `False`। |

### `Connection.begin()` { #connection-begin }

```python
Connection.begin()
```

**ধরন:** মেথড

স্পষ্টভাবে ট্রানজ্যাকশন শুরু করে (`RootTransaction`); context manager হিসেবে ব্লক শেষে commit/rollback। সাধারণত autobegin যথেষ্ট, তবে "এই ব্লকটুকু একটি ট্রানজ্যাকশন" বোঝাতে ভালো।

**উদাহরণ:**

```python
with engine.connect() as conn:
    with conn.begin():
        conn.execute(insert(users).values(name="ব্লকে"))
print(count())   # 4
```

### `Connection.begin_nested()` { #connection-begin-nested }

```python
Connection.begin_nested()
```

**ধরন:** মেথড

ট্রানজ্যাকশনের ভেতরে একটি **SAVEPOINT**: শুধু এই অংশ rollback করা যায়, বাইরের কাজ থাকে। "চেষ্টা করো, না হলে বাদ দাও"-এর জন্য (যেমন ডুপ্লিকেট এড়িয়ে বাল্ক insert)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    conn.execute(insert(users).values(name="থাকবে"))
    sp = conn.begin_nested()
    conn.execute(insert(users).values(name="বাদ যাবে"))
    sp.rollback()                                   # শুধু SAVEPOINT পর্যন্ত ফেরত
print(count())   # 4
```

### `Connection.begin_twophase()` { #connection-begin-twophase }

```python
Connection.begin_twophase(xid=None)
```

**ধরন:** মেথড

two-phase (XA) ট্রানজ্যাকশন শুরু করে: একাধিক ডেটাবেসে একসাথে commit নিশ্চিত করতে (`prepare()` তারপর `commit()`)। PostgreSQL-এ `max_prepared_transactions` > ০ লাগে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.exec_driver_sql("SHOW max_prepared_transactions").scalar())   # 0  (ডিফল্টে বন্ধ, তাই এখানে চালানো হলো না)
```

### `Connection.close()` { #connection-close }

```python
Connection.close()
```

**ধরন:** মেথড

কানেকশন বন্ধ করে পুলে ফেরত দেয় (চলমান ট্রানজ্যাকশন rollback হয়)। `with` ব্লক নিজেই এটা করে।

**উদাহরণ:**

```python
conn = engine.connect(); conn.close()
print(conn.closed)   # True
```

### `Connection.closed` { #connection-closed }

**ধরন:** প্রপার্টি

কানেকশন বন্ধ কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.closed)   # False
```

### `Connection.commit()` { #connection-commit }

```python
Connection.commit()
```

**ধরন:** মেথড

চলমান ট্রানজ্যাকশন commit করে। পরের স্টেটমেন্টে নতুন ট্রানজ্যাকশন নিজে শুরু হয় ("commit as you go")।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.execute(insert(users).values(name="ক")); conn.commit()
    conn.execute(insert(users).values(name="খ"))          # commit হয়নি
print(count())   # 4
```

### `Connection.commit_prepared()` { #connection-commit-prepared }

```python
Connection.commit_prepared(xid, recover=False)
```

**ধরন:** মেথড

আগে `prepare()` করা একটি two-phase ট্রানজ্যাকশন (xid দিয়ে) commit করে; ক্র্যাশের পর পুনরুদ্ধারে।

**উদাহরণ:**

```python
print(callable(Connection.commit_prepared))   # True
```

### `Connection.connection` { #connection-connection }

**ধরন:** প্রপার্টি

নিচের DBAPI কানেকশন (পুল-মোড়ানো `PoolProxiedConnection`)। ড্রাইভারের নিজস্ব মেথড লাগলে; `.dbapi_connection` দিয়ে একদম কাঁচা অবজেক্ট।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(conn.connection.dbapi_connection).__module__)   # psycopg2.extensions
```

### `Connection.default_isolation_level` { #connection-default-isolation-level }

**ধরন:** প্রপার্টি

কানেকশন খোলার সময় ডেটাবেসের ডিফল্ট isolation level।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.default_isolation_level)   # READ COMMITTED
```

### `Connection.detach()` { #connection-detach }

```python
Connection.detach()
```

**ধরন:** মেথড

কানেকশনটিকে পুল থেকে আলাদা করে: `close()` করলে পুলে না ফিরে আসলেই বন্ধ হয়। কানেকশনে এমন অবস্থা বদলালে (session ভ্যারিয়েবল) যা অন্যদের কাছে যাওয়া উচিত নয়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(engine.pool.checkedout())   # 1
    conn.detach()
    conn.exec_driver_sql("SET search_path TO pg_catalog")   # এই কানেকশন আর পুলে ফিরবে না
    print(engine.pool.checkedout())   # 0  (পুল আর এটিকে নিজের ধরে না)
```

### `Connection.dialect` { #connection-dialect }

**ধরন:** অ্যাট্রিবিউট

ব্যবহৃত ডায়ালেক্ট।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.dialect is engine.dialect)   # True
```

### `Connection.engine` { #connection-engine }

**ধরন:** অ্যাট্রিবিউট

যে Engine থেকে কানেকশনটি এসেছে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.engine is engine)   # True
```

### `Connection.exec_driver_sql()` { #connection-exec-driver-sql }

```python
Connection.exec_driver_sql(statement, parameters=None, execution_options=None)
```

**ধরন:** মেথড

একটি কাঁচা SQL স্ট্রিং সরাসরি ড্রাইভারে চালায় (SQLAlchemy-র কম্পাইল ছাড়া)। প্যারামিটার ড্রাইভারের নিজস্ব রূপে (psycopg2-তে `%(name)s`)। সাধারণত `text()` ভালো।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.exec_driver_sql("SELECT name FROM users WHERE id = %(i)s", {"i": 3}).scalar())   # সুমি
```

### `Connection.execute()` { #connection-execute }

```python
Connection.execute(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড

একটি স্টেটমেন্ট (`select()`, `insert()`, `text()` …) চালিয়ে `CursorResult` দেয়। প্যারামিটার dict দিলে একবার, dict-এর তালিকা দিলে **executemany** (বাল্ক)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    r = conn.execute(insert(users), [{"name": "ক"}, {"name": "খ"}])
    print(r.rowcount)   # 2
    print(conn.execute(text("SELECT name FROM users WHERE id = :i"), {"i": 1}).scalar())   # রহিম
```

### `Connection.execution_options()` { #connection-execution-options }

```python
Connection.execution_options(**opt)
```

**ধরন:** মেথড

এই কানেকশনের execution option সেট করে (জায়গাতেই): `isolation_level`, `stream_results`, `yield_per`, `schema_translate_map`, `logging_token`, `compiled_cache` ইত্যাদি।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.execution_options(isolation_level="SERIALIZABLE")
    print(conn.get_isolation_level())   # SERIALIZABLE
```

### `Connection.get_execution_options()` { #connection-get-execution-options }

```python
Connection.get_execution_options()
```

**ধরন:** মেথড

সেট করা execution option-গুলো।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(dict(conn.execution_options(stream_results=True).get_execution_options()))   # {'stream_results': True}
```

### `Connection.get_isolation_level()` { #connection-get-isolation-level }

```python
Connection.get_isolation_level()
```

**ধরন:** মেথড

ডেটাবেসে এই কানেকশনের **বর্তমান** isolation level (একটি কুয়েরি চালিয়ে জানে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.get_isolation_level())   # READ COMMITTED
```

### `Connection.get_nested_transaction()` { #connection-get-nested-transaction }

```python
Connection.get_nested_transaction()
```

**ধরন:** মেথড

চলমান SAVEPOINT (`NestedTransaction`), না থাকলে `None`।

**উদাহরণ:**

```python
with engine.begin() as conn:
    sp = conn.begin_nested()
    print(conn.get_nested_transaction() is sp)   # True
```

### `Connection.get_transaction()` { #connection-get-transaction }

```python
Connection.get_transaction()
```

**ধরন:** মেথড

চলমান মূল ট্রানজ্যাকশন, না থাকলে `None`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.get_transaction())   # None
    conn.execute(text("SELECT 1"))
    print(type(conn.get_transaction()).__name__)   # RootTransaction
```

### `Connection.in_nested_transaction()` { #connection-in-nested-transaction }

```python
Connection.in_nested_transaction()
```

**ধরন:** মেথড

SAVEPOINT চলছে কি না।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.in_nested_transaction()); conn.begin_nested(); print(conn.in_nested_transaction())
# False
# True
```

### `Connection.in_transaction()` { #connection-in-transaction }

```python
Connection.in_transaction()
```

**ধরন:** মেথড

ট্রানজ্যাকশন চলছে কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.in_transaction()); conn.execute(text("SELECT 1")); print(conn.in_transaction())
# False
# True
```

### `Connection.info` { #connection-info }

**ধরন:** প্রপার্টি

নিচের DBAPI কানেকশনের সাথে যুক্ত dict: কানেকশন পুলে ফিরলেও থেকে যায়। কানেকশন-ভিত্তিক ক্যাশ রাখতে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.info["tenant"] = "shop1"
with engine.connect() as conn:            # পুল থেকে একই কানেকশন আবার এল
    print(conn.info.get("tenant"))   # shop1
```

### `Connection.invalidate()` { #connection-invalidate }

```python
Connection.invalidate(exception=None)
```

**ধরন:** মেথড

কানেকশনটিকে "নষ্ট" ঘোষণা করে: পুল এটিকে আর ব্যবহার করবে না, পরের কাজে নতুন কানেকশন খুলবে। নেটওয়ার্ক-ত্রুটির পর SQLAlchemy নিজেও এটা করে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.invalidate()
    print(conn.invalidated)   # True
```

### `Connection.invalidated` { #connection-invalidated }

**ধরন:** প্রপার্টি

কানেকশন invalidate হয়েছে কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.invalidated)   # False
```

### `Connection.recover_twophase()` { #connection-recover-twophase }

```python
Connection.recover_twophase()
```

**ধরন:** মেথড

ডেটাবেসে "prepared" অবস্থায় আটকে থাকা two-phase ট্রানজ্যাকশনগুলোর xid তালিকা দেয়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.recover_twophase())   # []
```

### `Connection.rollback()` { #connection-rollback }

```python
Connection.rollback()
```

**ধরন:** মেথড

চলমান ট্রানজ্যাকশন বাতিল করে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.execute(insert(users).values(name="বাতিল")); conn.rollback()
    print(conn.scalar(select(func.count()).select_from(users)))   # 3
```

### `Connection.rollback_prepared()` { #connection-rollback-prepared }

```python
Connection.rollback_prepared(xid, recover=False)
```

**ধরন:** মেথড

`prepare()` করা two-phase ট্রানজ্যাকশন rollback করে।

**উদাহরণ:**

```python
print(callable(Connection.rollback_prepared))   # True
```

### `Connection.scalar()` { #connection-scalar }

```python
Connection.scalar(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড

স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলাম দেয় (রো না থাকলে `None`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.scalar(select(func.max(users.c.id))))   # 3
```

### `Connection.scalars()` { #connection-scalars }

```python
Connection.scalars(statement, parameters=None, *, execution_options=None)
```

**ধরন:** মেথড

স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলামের `ScalarResult` দেয়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.scalars(select(users.c.name).order_by(users.c.id)).all())   # ['রহিম', 'করিম', 'সুমি']
```

### `Connection.schema_for_object()` { #connection-schema-for-object }

```python
Connection.schema_for_object(obj)
```

**ধরন:** মেথড

একটি স্কিমা-অবজেক্টের আসল স্কিমা নাম দেয়, `schema_translate_map` হিসাবে নিয়ে (মাল্টি-টেন্যান্টে কাজে লাগে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn = conn.execution_options(schema_translate_map={None: "tenant_7"})
    print(conn.schema_for_object(users))   # tenant_7
```

### `Connection.should_close_with_result` { #connection-should-close-with-result }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(পুরোনো API-র অবশেষ) রেজাল্ট শেষ হলে কানেকশন বন্ধ হবে কি না; ২.০-তে সবসময় `False`।

## Transaction { #transaction-group }

## `Transaction` { #transaction }

```python
from sqlalchemy.engine import Transaction
```

`conn.begin()` / `begin_nested()` / `begin_twophase()`-এর ফলের মূল ক্লাস। context manager হিসেবে ব্যবহার করুন; ব্লক শেষে নিজে থেকে commit (এরর হলে rollback)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    tx = conn.begin()
    conn.execute(insert(users).values(name="ক"))
    tx.commit()
print(count())   # 4
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #transaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#transaction-close) | মেথড | ট্রানজ্যাকশন বন্ধ করে: শেষ না হয়ে থাকলে rollback (মূল ট্রানজ্যাকশনে)। |
| [`commit()`](#transaction-commit) | মেথড | ট্রানজ্যাকশন commit করে (SAVEPOINT হলে `RELEASE SAVEPOINT`)। |
| [`is_valid`](#transaction-is-valid) | প্রপার্টি | ট্রানজ্যাকশন এখনো ব্যবহারযোগ্য কি না (কানেকশন invalidate হলে `False`)। |
| [`rollback()`](#transaction-rollback) | মেথড | ট্রানজ্যাকশন বাতিল করে। |

### `Transaction.close()` { #transaction-close }

```python
Transaction.close()
```

**ধরন:** মেথড

ট্রানজ্যাকশন বন্ধ করে: শেষ না হয়ে থাকলে rollback (মূল ট্রানজ্যাকশনে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    tx = conn.begin(); conn.execute(insert(users).values(name="ক")); tx.close()
print(count())   # 3
```

### `Transaction.commit()` { #transaction-commit }

```python
Transaction.commit()
```

**ধরন:** মেথড

ট্রানজ্যাকশন commit করে (SAVEPOINT হলে `RELEASE SAVEPOINT`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    tx = conn.begin(); conn.execute(insert(users).values(name="ক")); tx.commit()
    print(tx.is_active)   # False
```

### `Transaction.is_valid` { #transaction-is-valid }

**ধরন:** প্রপার্টি

ট্রানজ্যাকশন এখনো ব্যবহারযোগ্য কি না (কানেকশন invalidate হলে `False`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.begin().is_valid)   # True
```

### `Transaction.rollback()` { #transaction-rollback }

```python
Transaction.rollback()
```

**ধরন:** মেথড

ট্রানজ্যাকশন বাতিল করে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    tx = conn.begin(); conn.execute(insert(users).values(name="ক")); tx.rollback()
print(count())   # 3
```

## `RootTransaction` { #roottransaction }

```python
from sqlalchemy.engine import RootTransaction
```

কানেকশনের মূল (সবচেয়ে বাইরের) ট্রানজ্যাকশন: `BEGIN` ... `COMMIT`/`ROLLBACK`। autobegin বা `conn.begin()` থেকে আসে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(conn.begin()).__name__)   # RootTransaction
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #roottransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`connection`](#roottransaction-connection) | অ্যাট্রিবিউট | যে `Connection`-এর ট্রানজ্যাকশন। |
| [`is_active`](#roottransaction-is-active) | অ্যাট্রিবিউট | ট্রানজ্যাকশন এখনো চলছে কি না (commit/rollback-এর পর `False`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `RootTransaction`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Transaction` থেকে:** [`close()`](#transaction-close) · [`commit()`](#transaction-commit) · [`is_valid`](#transaction-is-valid) · [`rollback()`](#transaction-rollback)

///

### `RootTransaction.connection` { #roottransaction-connection }

**ধরন:** অ্যাট্রিবিউট

যে `Connection`-এর ট্রানজ্যাকশন।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.begin().connection is conn)   # True
```

### `RootTransaction.is_active` { #roottransaction-is-active }

**ধরন:** অ্যাট্রিবিউট

ট্রানজ্যাকশন এখনো চলছে কি না (commit/rollback-এর পর `False`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    tx = conn.begin(); print(tx.is_active); tx.rollback(); print(tx.is_active)
# True
# False
```

## `NestedTransaction` { #nestedtransaction }

```python
from sqlalchemy.engine import NestedTransaction
```

`conn.begin_nested()`-এর ফল: একটি SAVEPOINT। `commit()` = `RELEASE SAVEPOINT` (বাইরের ট্রানজ্যাকশন commit হলে তবেই সেভ), `rollback()` = `ROLLBACK TO SAVEPOINT`।

**উদাহরণ:**

```python
with engine.begin() as conn:
    with conn.begin_nested():                      # সফল হলে release
        conn.execute(insert(users).values(name="ক"))
    try:
        with conn.begin_nested():                  # এরর হলে শুধু এই অংশ rollback
            conn.execute(insert(users).values(id=1, name="ডুপ্লিকেট id"))
    except exc.IntegrityError:
        pass
print(count())   # 4
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`RootTransaction`](#roottransaction-summary)-এর মতো।

## `TwoPhaseTransaction` { #twophasetransaction }

```python
from sqlalchemy.engine import TwoPhaseTransaction
```

`conn.begin_twophase()`-এর ফল: `prepare()` (ডেটাবেসে "প্রস্তুত" অবস্থা, ক্র্যাশেও টিকে থাকে) তারপর `commit()`। একাধিক ডেটাবেস/সিস্টেমে একসাথে commit-এর জন্য; PostgreSQL-এ `max_prepared_transactions` চালু থাকতে হবে।

**উদাহরণ:**

```python
print(issubclass(TwoPhaseTransaction, RootTransaction))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #twophasetransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`prepare()`](#twophasetransaction-prepare) | মেথড | ট্রানজ্যাকশনকে "PREPARE TRANSACTION" অবস্থায় নেয় (প্রথম ধাপ)। |
| [`xid`](#twophasetransaction-xid) | অ্যাট্রিবিউট | ট্রানজ্যাকশনের global id (না দিলে SQLAlchemy একটি বানায়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TwoPhaseTransaction`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Transaction` থেকে:** [`close()`](#transaction-close) · [`commit()`](#transaction-commit) · [`is_valid`](#transaction-is-valid) · [`rollback()`](#transaction-rollback)

**`RootTransaction` থেকে:** [`connection`](#roottransaction-connection) · [`is_active`](#roottransaction-is-active)

///

### `TwoPhaseTransaction.prepare()` { #twophasetransaction-prepare }

```python
TwoPhaseTransaction.prepare()
```

**ধরন:** মেথড

ট্রানজ্যাকশনকে "PREPARE TRANSACTION" অবস্থায় নেয় (প্রথম ধাপ)।

**উদাহরণ:**

```python
print(callable(TwoPhaseTransaction.prepare))   # True
```

### `TwoPhaseTransaction.xid` { #twophasetransaction-xid }

**ধরন:** অ্যাট্রিবিউট

ট্রানজ্যাকশনের global id (না দিলে SQLAlchemy একটি বানায়)।

**উদাহরণ:**

```python
print("xid" in TwoPhaseTransaction.__dict__ or hasattr(TwoPhaseTransaction, "xid"))   # True
```

## URL ও প্লাগিন { #url-group }

## `URL` { #url }

```python
from sqlalchemy import URL
```

ডেটাবেস ঠিকানার অপরিবর্তনীয় (immutable) অবজেক্ট, একটি named tuple: `drivername`, `username`, `password`, `host`, `port`, `database`, `query`। বদলাতে `set()` / `update_query_*()` নতুন URL দেয়। `URL.create()` দিয়ে বানালে পাসওয়ার্ডের বিশেষ অক্ষর নিয়ে চিন্তা নেই।

**উদাহরণ:**

```python
u = URL.create("postgresql+psycopg2", username="app", password="s@cret", host="db", port=5432, database="shop")
print(u.render_as_string(hide_password=False))   # postgresql+psycopg2://app:s%40cret@db:5432/shop
print(repr(u))                                   # postgresql+psycopg2://app:***@db:5432/shop
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #url-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`count()`](#url-count) | মেথড (internal) | tuple-এর মেথড (একটি মান কতবার আছে); URL-এ অর্থবহ নয়। |
| [`create()`](#url-create) | ক্লাস মেথড | (ক্লাস মেথড) অংশগুলো থেকে URL বানায়; পাসওয়ার্ড ইত্যাদিতে escape লাগে না। |
| [`database`](#url-database) | অ্যাট্রিবিউট | ডেটাবেসের নাম (SQLite-এ ফাইলের পাথ)। |
| [`difference_update_query()`](#url-difference-update-query) | মেথড | query অংশ থেকে কিছু key বাদ দিয়ে নতুন URL দেয়। |
| [`drivername`](#url-drivername) | অ্যাট্রিবিউট | `ডায়ালেক্ট+ড্রাইভার` অংশ। |
| [`get_backend_name()`](#url-get-backend-name) | মেথড | শুধু ডায়ালেক্ট (ডেটাবেস) অংশ। |
| [`get_dialect()`](#url-get-dialect) | মেথড | URL অনুযায়ী `Dialect` ক্লাস দেয় (ড্রাইভার ইমপোর্ট ছাড়াই)। |
| [`get_driver_name()`](#url-get-driver-name) | মেথড | ড্রাইভারের নাম (না লিখলে ডায়ালেক্টের ডিফল্ট ড্রাইভার; **২.১-এ `postgresql://`-এর ডিফল্ট psycopg 3**, ২.০-তে ছিল psycopg2)। |
| [`host`](#url-host) | অ্যাট্রিবিউট | হোস্ট। |
| [`index()`](#url-index) | মেথড (internal) | tuple-এর মেথড; URL-এ অর্থবহ নয়। |
| [`normalized_query`](#url-normalized-query) | প্রপার্টি | query অপশনগুলো, প্রতিটি মান tuple হিসেবে (একই key একাধিকবার থাকলে সব মান)। |
| [`password`](#url-password) | অ্যাট্রিবিউট | পাসওয়ার্ড। |
| [`port`](#url-port) | অ্যাট্রিবিউট | পোর্ট (না দিলে `None`)। |
| [`query`](#url-query) | অ্যাট্রিবিউট | `?`-এর পরের অপশনগুলোর dict। |
| [`render_as_string()`](#url-render-as-string) | মেথড | URL স্ট্রিং বানায়; ডিফল্টে পাসওয়ার্ড `***`। |
| [`set()`](#url-set) | মেথড | কিছু অংশ বদলে নতুন URL দেয় (যেমন টেস্টের জন্য ভিন্ন ডেটাবেস)। |
| [`translate_connect_args()`](#url-translate-connect-args) | মেথড | URL-এর অংশগুলোকে ড্রাইভারের `connect()` আর্গুমেন্টের dict-এ রূপান্তর করে (ডায়ালেক্ট বানাতে ব্যবহৃত)। |
| [`update_query_dict()`](#url-update-query-dict) | মেথড | dict থেকে query অপশন যোগ/বদল করে নতুন URL দেয়। |
| [`update_query_pairs()`](#url-update-query-pairs) | মেথড | `(key, value)` জোড়া থেকে query অপশন যোগ/বদল করে। |
| [`update_query_string()`](#url-update-query-string) | মেথড | `"a=1&b=2"` ধরনের স্ট্রিং থেকে query অপশন যোগ/বদল করে (২.১.৬-এ `keep_blank_values`)। |
| [`username`](#url-username) | অ্যাট্রিবিউট | ইউজারনেম। |

### `URL.count()` { #url-count }

```python
URL.count(value, /)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

tuple-এর মেথড (একটি মান কতবার আছে); URL-এ অর্থবহ নয়।

### `URL.create()` { #url-create }

```python
URL.create(drivername, username=None, password=None, host=None, port=None, database=None, query={})
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) অংশগুলো থেকে URL বানায়; পাসওয়ার্ড ইত্যাদিতে escape লাগে না।

**উদাহরণ:**

```python
print(URL.create("sqlite", database="app.db"))   # sqlite:///app.db
```

### `URL.database` { #url-database }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেসের নাম (SQLite-এ ফাইলের পাথ)।

**উদাহরণ:**

```python
print(make_url(URL_STR).database)   # apiref
```

### `URL.difference_update_query()` { #url-difference-update-query }

```python
URL.difference_update_query(names)
```

**ধরন:** মেথড

query অংশ থেকে কিছু key বাদ দিয়ে নতুন URL দেয়।

**উদাহরণ:**

```python
print(make_url("postgresql://h/db?a=1&b=2").difference_update_query(["a"]))   # postgresql://h/db?b=2
```

### `URL.drivername` { #url-drivername }

**ধরন:** অ্যাট্রিবিউট

`ডায়ালেক্ট+ড্রাইভার` অংশ।

**উদাহরণ:**

```python
print(make_url(URL_STR).drivername)   # postgresql+psycopg2
```

### `URL.get_backend_name()` { #url-get-backend-name }

```python
URL.get_backend_name()
```

**ধরন:** মেথড

শুধু ডায়ালেক্ট (ডেটাবেস) অংশ।

**উদাহরণ:**

```python
print(make_url(URL_STR).get_backend_name())   # postgresql
```

### `URL.get_dialect()` { #url-get-dialect }

```python
URL.get_dialect()
```

**ধরন:** মেথড

URL অনুযায়ী `Dialect` ক্লাস দেয় (ড্রাইভার ইমপোর্ট ছাড়াই)।

**উদাহরণ:**

```python
print(make_url(URL_STR).get_dialect().__name__)   # PGDialect_psycopg2
```

### `URL.get_driver_name()` { #url-get-driver-name }

```python
URL.get_driver_name()
```

**ধরন:** মেথড

ড্রাইভারের নাম (না লিখলে ডায়ালেক্টের ডিফল্ট ড্রাইভার; **২.১-এ `postgresql://`-এর ডিফল্ট psycopg 3**, ২.০-তে ছিল psycopg2)।

**উদাহরণ:**

```python
print(make_url("postgresql://h/db").get_driver_name())   # psycopg  (২.১-এ PostgreSQL-এর ডিফল্ট ড্রাইভার psycopg 3)
```

### `URL.host` { #url-host }

**ধরন:** অ্যাট্রিবিউট

হোস্ট।

**উদাহরণ:**

```python
print(make_url(URL_STR).host)   # 127.0.0.1
```

### `URL.index()` { #url-index }

```python
URL.index(value, start=0, stop=9223372036854775807, /)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

tuple-এর মেথড; URL-এ অর্থবহ নয়।

### `URL.normalized_query` { #url-normalized-query }

**ধরন:** প্রপার্টি

query অপশনগুলো, প্রতিটি মান tuple হিসেবে (একই key একাধিকবার থাকলে সব মান)।

**উদাহরণ:**

```python
print(dict(make_url("postgresql://h/db?host=a&host=b").normalized_query))   # {'host': ('a', 'b')}
```

### `URL.password` { #url-password }

**ধরন:** অ্যাট্রিবিউট

পাসওয়ার্ড।

**উদাহরণ:**

```python
print(make_url("postgresql://u:pw@h/db").password)   # pw
```

### `URL.port` { #url-port }

**ধরন:** অ্যাট্রিবিউট

পোর্ট (না দিলে `None`)।

**উদাহরণ:**

```python
print(make_url("postgresql://h:6432/db").port)   # 6432
```

### `URL.query` { #url-query }

**ধরন:** অ্যাট্রিবিউট

`?`-এর পরের অপশনগুলোর dict।

**উদাহরণ:**

```python
print(dict(make_url("postgresql://h/db?sslmode=require").query))   # {'sslmode': 'require'}
```

### `URL.render_as_string()` { #url-render-as-string }

```python
URL.render_as_string(hide_password=True)
```

**ধরন:** মেথড

URL স্ট্রিং বানায়; ডিফল্টে পাসওয়ার্ড `***`। আরেকটি engine বানাতে পূর্ণ স্ট্রিং লাগলে `hide_password=False` (লগে কখনো নয়)।

**উদাহরণ:**

```python
print(make_url("postgresql://u:pw@h/db").render_as_string())   # postgresql://u:***@h/db
```

### `URL.set()` { #url-set }

```python
URL.set(drivername=None, username=None, password=None, host=None, port=None, database=None, query=None)
```

**ধরন:** মেথড

কিছু অংশ বদলে নতুন URL দেয় (যেমন টেস্টের জন্য ভিন্ন ডেটাবেস)।

**উদাহরণ:**

```python
print(make_url(URL_STR).set(database="test_apiref"))   # postgresql+psycopg2://postgres@127.0.0.1/test_apiref
```

### `URL.translate_connect_args()` { #url-translate-connect-args }

```python
URL.translate_connect_args(names=None, **kw)
```

**ধরন:** মেথড

URL-এর অংশগুলোকে ড্রাইভারের `connect()` আর্গুমেন্টের dict-এ রূপান্তর করে (ডায়ালেক্ট বানাতে ব্যবহৃত)।

**উদাহরণ:**

```python
print(make_url("postgresql://u:pw@h:5433/db").translate_connect_args(username="user"))
# {'host': 'h', 'database': 'db', 'user': 'u', 'password': 'pw', 'port': 5433}
```

### `URL.update_query_dict()` { #url-update-query-dict }

```python
URL.update_query_dict(query_parameters, append=False)
```

**ধরন:** মেথড

dict থেকে query অপশন যোগ/বদল করে নতুন URL দেয়।

**উদাহরণ:**

```python
print(make_url("postgresql://h/db").update_query_dict({"sslmode": "require"}))   # postgresql://h/db?sslmode=require
```

### `URL.update_query_pairs()` { #url-update-query-pairs }

```python
URL.update_query_pairs(key_value_pairs, append=False)
```

**ধরন:** মেথড

`(key, value)` জোড়া থেকে query অপশন যোগ/বদল করে।

**উদাহরণ:**

```python
print(make_url("postgresql://h/db").update_query_pairs([("a", "1"), ("b", "2")]))   # postgresql://h/db?a=1&b=2
```

### `URL.update_query_string()` { #url-update-query-string }

```python
URL.update_query_string(query_string, append=False, *, keep_blank_values=False)
```

**ধরন:** মেথড

`"a=1&b=2"` ধরনের স্ট্রিং থেকে query অপশন যোগ/বদল করে (২.১.৬-এ `keep_blank_values`)।

**উদাহরণ:**

```python
print(make_url("postgresql://h/db").update_query_string("connect_timeout=5"))   # postgresql://h/db?connect_timeout=5
```

### `URL.username` { #url-username }

**ধরন:** অ্যাট্রিবিউট

ইউজারনেম।

**উদাহরণ:**

```python
print(make_url(URL_STR).username)   # postgres
```

## `CreateEnginePlugin` { #createengineplugin }

```python
from sqlalchemy.engine import CreateEnginePlugin
```

`create_engine()`-এর আচরণ বদলানোর প্লাগিন (ট্রেসিং, মেট্রিক্স, কানেকশন অপশন যোগ)। URL-এ `?plugin=নাম` বা `create_engine(..., plugins=["নাম"])` দিয়ে চালু হয়; entry point হিসেবে নিবন্ধন করতে হয়।

**উদাহরণ:**

```python
import sys, types
from sqlalchemy.dialects import plugins

class TagPlugin(CreateEnginePlugin):
    def update_url(self, url):
        return url.difference_update_query(["tag"])
    def engine_created(self, engine):
        engine.info_tag = self.url.query.get("tag")

mod = types.ModuleType("my_tag_plugin"); mod.TagPlugin = TagPlugin; sys.modules["my_tag_plugin"] = mod
plugins.register("tagplugin", "my_tag_plugin", "TagPlugin")    # সাধারণত setup.py/pyproject-এর entry point দিয়ে
eng = create_engine(URL_STR + "?plugin=tagplugin&tag=api")
print(eng.info_tag, eng.url)   # api postgresql+psycopg2://postgres@127.0.0.1/apiref
eng.dispose()
```

### কনস্ট্রাক্টরের প্যারামিটার { #createengineplugin-params }

```python
CreateEnginePlugin(url, kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `url` | engine-এর `URL` (প্লাগিন query অপশন পড়তে পারে)। |
| `kwargs` | `create_engine()`-এ দেওয়া keyword argument-গুলো (প্লাগিন নিজের অপশন বের করে নিতে পারে)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createengineplugin-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`engine_created()`](#createengineplugin-engine-created) | মেথড | engine পুরোপুরি তৈরি হলে ডাকা হয়: event listener যুক্ত করার জায়গা। |
| [`handle_dialect_kwargs()`](#createengineplugin-handle-dialect-kwargs) | মেথড | ডায়ালেক্টে যাওয়ার আগে তার kwargs দেখা/বদলানো। |
| [`handle_pool_kwargs()`](#createengineplugin-handle-pool-kwargs) | মেথড | পুল বানানোর আগে তার kwargs দেখা/বদলানো। |
| [`update_url()`](#createengineplugin-update-url) | মেথড | (১.৪) প্লাগিনের নিজের query অপশন URL থেকে বাদ দিয়ে নতুন URL ফেরত দেয়, যাতে সেগুলো ড্রাইভারে না যায়। |

### `CreateEnginePlugin.engine_created()` { #createengineplugin-engine-created }

```python
CreateEnginePlugin.engine_created(engine)
```

**ধরন:** মেথড

engine পুরোপুরি তৈরি হলে ডাকা হয়: event listener যুক্ত করার জায়গা।

**উদাহরণ:**

```python
print(callable(CreateEnginePlugin.engine_created))   # True
```

### `CreateEnginePlugin.handle_dialect_kwargs()` { #createengineplugin-handle-dialect-kwargs }

```python
CreateEnginePlugin.handle_dialect_kwargs(dialect_cls, dialect_args)
```

**ধরন:** মেথড

ডায়ালেক্টে যাওয়ার আগে তার kwargs দেখা/বদলানো।

**উদাহরণ:**

```python
print(callable(CreateEnginePlugin.handle_dialect_kwargs))   # True
```

### `CreateEnginePlugin.handle_pool_kwargs()` { #createengineplugin-handle-pool-kwargs }

```python
CreateEnginePlugin.handle_pool_kwargs(pool_cls, pool_args)
```

**ধরন:** মেথড

পুল বানানোর আগে তার kwargs দেখা/বদলানো।

**উদাহরণ:**

```python
print(callable(CreateEnginePlugin.handle_pool_kwargs))   # True
```

### `CreateEnginePlugin.update_url()` { #createengineplugin-update-url }

```python
CreateEnginePlugin.update_url(url)
```

**ধরন:** মেথড

(১.৪) প্লাগিনের নিজের query অপশন URL থেকে বাদ দিয়ে নতুন URL ফেরত দেয়, যাতে সেগুলো ড্রাইভারে না যায়।

**উদাহরণ:**

```python
print(callable(CreateEnginePlugin.update_url))   # True
```

/// check | সংক্ষেপে মনে রাখুন

* Engine অ্যাপে একটি; প্রোডাকশনে `pool_pre_ping=True`, প্রয়োজনে `pool_recycle`।
* লেখার কাজ: `with engine.begin() as conn:` (নিজে commit/rollback); পড়া: `with engine.connect() as conn:`।
* `connect()`-এ `conn.commit()` না ডাকলে কিছুই সেভ হয় না।
* আংশিক rollback: `conn.begin_nested()` (SAVEPOINT)।
* পাসওয়ার্ডে বিশেষ অক্ষর: `URL.create(...)`; লগে URL দেখাতে `render_as_string()` (পাসওয়ার্ড লুকানো)।
* অ্যাপ বন্ধে / fork-এর পর: `engine.dispose()`।

///
