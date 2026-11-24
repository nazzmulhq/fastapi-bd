# এক্সেপশন ও সতর্কবার্তা: sqlalchemy.exc আর sqlalchemy.orm.exc { #api-exceptions }

/// note | এই পেজে যা আছে

SQLAlchemy-র **সব** এক্সেপশন আর সতর্কবার্তা (warning) ক্লাস: `sqlalchemy.exc`-এর ৫১টি, `sqlalchemy.orm.exc`-এর ORM-বিশেষ ১২টি, আর দুটি সহায়ক ক্লাস (`HasDescriptionCode`, `DontWrapMixin`)। প্রতিটির জন্য: কখন আসে, কীভাবে ধরবেন, আর বাস্তবে তুলে (trigger করে) দেখানো উদাহরণ। শেষে পুরো ক্লাস-গাছ (hierarchy) আর **FastAPI-তে কোন এররকে কোন HTTP কোডে** বদলাবেন।

///

/// tip | তিনটি জিনিস মনে রাখলেই বেশিরভাগ কাজ চলে

1. **সব** SQLAlchemy এরর `SQLAlchemyError`-এর সন্তান; ডেটাবেস থেকে আসা সব এরর `DBAPIError`-এর সন্তান।
2. ডেটাবেস ড্রাইভারের আসল এরর থাকে `e.orig`-এ (যেমন psycopg-এর `UniqueViolation`)। ডেটাবেসের এরর কোড `e.orig.sqlstate` (psycopg 3) বা `e.orig.pgcode` (psycopg2)।
3. ORM-এ এরর হলে `session.rollback()` না করা পর্যন্ত সেশন আর চলবে না (`PendingRollbackError`)।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    version: Mapped[int] = mapped_column(default=1)     # optimistic locking (StaleDataError দেখাতে)
    posts: Mapped[list["Post"]] = relationship()
    __mapper_args__ = {"version_id_col": version}

class Post(Base):          # id, title, user_id → users.id
    ...

class Node(Base):          # id, parent_id → nodes.id, parent (নিজের দিকে relationship)
    ...
```

* ডেটা: User ১ "রহিম", User ২ "করিম"। `session` একটি খোলা `Session`।
* `err(fn)`: `fn()` চালায়; এরর হলে **এররের ক্লাসের নাম** ছাপে আর এররটি ফেরত দেয় (যাতে এর অ্যাট্রিবিউট দেখানো যায়)।
* PostgreSQL 16, ড্রাইভার psycopg 3-এ চালিয়ে দেখা; কিছু উদাহরণে SQLite বা asyncpg।

///

## মূল ক্লাস { #sqlalchemyerror-group }

## `SQLAlchemyError` { #sqlalchemyerror }

```python
from sqlalchemy.exc import SQLAlchemyError
```

SQLAlchemy-র **সব** এক্সেপশনের মূল ক্লাস (সতর্কবার্তা বাদে)। "SQLAlchemy-র যেকোনো এরর" ধরতে এটি ধরুন। এররের বার্তার শেষে প্রায়ই একটি লিংক থাকে: `(Background on this error at: https://sqlalche.me/e/21/<code>)`, যেখানে ঐ এররের বিস্তারিত ব্যাখ্যা।

**উদাহরণ:**

```python
try:
    session.execute(select(User).where(User.id == 99)).scalar_one()
except exc.SQLAlchemyError as e:
    print(type(e).__name__, isinstance(e, exc.InvalidRequestError))   # NoResultFound True
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sqlalchemyerror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`code`](#sqlalchemyerror-code) | অ্যাট্রিবিউট | এররের ছোট কোড (যেমন `"gkpj"`), ঐ লিংকে ব্যবহার হয়। |

### `SQLAlchemyError.code` { #sqlalchemyerror-code }

**ধরন:** অ্যাট্রিবিউট

এররের ছোট কোড (যেমন `"gkpj"`), ঐ লিংকে ব্যবহার হয়। সব এররের কোড নেই (`None`)। নিজের এরর ক্লাসে `code = "..."` দিলে বার্তার শেষে লিংক যোগ হয়।

**উদাহরণ:**

```python
e = err(lambda: session.execute(text("SELECT * FROM nope")))   # ProgrammingError
print(e.code, str(e).splitlines()[-1])   # f405 (Background on this error at: https://sqlalche.me/e/21/f405)
```

## `HasDescriptionCode` { #hasdescriptioncode }

```python
from sqlalchemy.exc import HasDescriptionCode
```

(অভ্যন্তরীণ মিক্সিন) `code` অ্যাট্রিবিউট আর বার্তার শেষে "Background on this error" লিংক যোগ করার ব্যবস্থা দেয়। `SQLAlchemyError` আর `SAWarning` দুটোই এটি থেকে আসে।

**উদাহরণ:**

```python
print(issubclass(exc.SQLAlchemyError, exc.HasDescriptionCode), issubclass(exc.SAWarning, exc.HasDescriptionCode))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hasdescriptioncode-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HasDescriptionCode`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

## `DontWrapMixin` { #dontwrapmixin }

```python
from sqlalchemy.exc import DontWrapMixin
```

নিজের এক্সেপশন ক্লাসে এটি মেশালে, স্টেটমেন্ট চালানোর সময় (যেমন `TypeDecorator.process_bind_param()`-এর ভেতরে) আপনার এরর **`StatementError`-এ মোড়ানো হয় না**; সরাসরি আপনার ক্লাস হিসেবেই আসে। ফলে `except MyError` সহজে ধরা যায়।

**উদাহরণ:**

```python
class NegativeError(exc.DontWrapMixin, ValueError):
    pass

class Positive(TypeDecorator):
    impl = Integer
    cache_ok = True
    def process_bind_param(self, value, dialect):
        if value is not None and value < 0:
            raise NegativeError("ঋণাত্মক সংখ্যা চলবে না")
        return value

t = Table("amounts", MetaData(), Column("v", Positive))
t.create(engine)
try:
    with engine.begin() as c:
        c.execute(insert(t).values(v=-1))
except NegativeError as e:
    print(type(e).__name__, e)   # NegativeError ঋণাত্মক সংখ্যা চলবে না  (মিক্সিন ছাড়া হতো StatementError)
```

## ডেটাবেস থেকে আসা এরর (DB-API) { #statementerror-group }

## `StatementError` { #statementerror }

```python
from sqlalchemy.exc import StatementError
```

একটি SQL স্টেটমেন্ট চালানোর সময় এরর। SQL, প্যারামিটার আর আসল এরর (`orig`) সাথে রাখে, তাই বার্তায় `[SQL: ...]` আর `[parameters: ...]` দেখা যায়। ডেটাবেসে পৌঁছানোর **আগে** (যেমন bind প্যারামিটার তৈরিতে) এরর হলে সরাসরি `StatementError`; ডেটাবেস নিজে এরর দিলে তার সন্তান `DBAPIError`।

**উদাহরণ:**

```python
e = err(lambda: session.execute(select(User).where(User.id == bindparam("uid"))))
# StatementError
print(type(e.orig).__name__, "|", e.orig)
# InvalidRequestError | A value is required for bind parameter 'uid' (Background on this error at: https://sqlalche.me/e/21/cd3x)
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #statementerror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_detail()`](#statementerror-add-detail) | মেথড | বার্তার শুরুতে বাড়তি একটি তথ্য-লাইন (বন্ধনীতে) যোগ করে। |
| [`connection_invalidated`](#statementerror-connection-invalidated) | অ্যাট্রিবিউট | `True` হলে এররটি **সংযোগ বিচ্ছিন্ন** (disconnect) হওয়ার কারণে, আর SQLAlchemy সংযোগটি বাতিল করেছে। |
| [`ismulti`](#statementerror-ismulti) | অ্যাট্রিবিউট | `True` হলে স্টেটমেন্টটি একসাথে অনেক প্যারামিটার-সেট নিয়ে চলছিল (executemany, যেমন `execute(insert(t), [{...}, {...}])`)। |
| [`orig`](#statementerror-orig) | অ্যাট্রিবিউট | **আসল** এরর অবজেক্ট: ড্রাইভারের এক্সেপশন (যেমন `psycopg.errors.UniqueViolation`), বা SQLAlchemy-র ভেতরের এরর। |
| [`params`](#statementerror-params) | অ্যাট্রিবিউট | স্টেটমেন্টের প্যারামিটার (dict, বা executemany হলে তালিকা)। |
| [`statement`](#statementerror-statement) | অ্যাট্রিবিউট | যে SQL স্ট্রিং চালানো হচ্ছিল। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `StatementError`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `StatementError.add_detail()` { #statementerror-add-detail }

```python
StatementError.add_detail(msg)
```

**ধরন:** মেথড

বার্তার শুরুতে বাড়তি একটি তথ্য-লাইন (বন্ধনীতে) যোগ করে। SQLAlchemy নিজে এটি ব্যবহার করে (যেমন autoflush-এর সময় এরর হলে "raised as a result of Query-invoked autoflush" যোগ হয়)।

**উদাহরণ:**

```python
e = exc.StatementError("কিছু ভুল হয়েছে", "SELECT 1", {}, None)
e.add_detail("autoflush-এর সময়")
print(str(e).splitlines())   # ['(autoflush-এর সময়)', 'কিছু ভুল হয়েছে', '[SQL: SELECT 1]']
```

### `StatementError.connection_invalidated` { #statementerror-connection-invalidated }

**ধরন:** অ্যাট্রিবিউট

`True` হলে এররটি **সংযোগ বিচ্ছিন্ন** (disconnect) হওয়ার কারণে, আর SQLAlchemy সংযোগটি বাতিল করেছে। এমন এররে পুরো অপারেশন আবার চেষ্টা (retry) করা নিরাপদ হতে পারে।

**উদাহরণ:**

```python
def broken():
    with engine.connect() as c:
        c.connection.driver_connection.close()   # ড্রাইভারের সংযোগ জোর করে বন্ধ
        c.exec_driver_sql("SELECT 1")
e = err(broken)   # OperationalError
print(e.connection_invalidated)   # True
```

### `StatementError.ismulti` { #statementerror-ismulti }

**ধরন:** অ্যাট্রিবিউট

`True` হলে স্টেটমেন্টটি একসাথে অনেক প্যারামিটার-সেট নিয়ে চলছিল (executemany, যেমন `execute(insert(t), [{...}, {...}])`)।

**উদাহরণ:**

```python
def many():
    with engine.begin() as c:
        c.execute(insert(User), [{"name": "ক"}, {"name": "ক"}])
e = err(many)   # IntegrityError
print(e.ismulti)   # True
```

### `StatementError.orig` { #statementerror-orig }

**ধরন:** অ্যাট্রিবিউট

**আসল** এরর অবজেক্ট: ড্রাইভারের এক্সেপশন (যেমন `psycopg.errors.UniqueViolation`), বা SQLAlchemy-র ভেতরের এরর। ডেটাবেস-নির্দিষ্ট তথ্য (এরর কোড, কনস্ট্রেইন্টের নাম) এখানেই।

**উদাহরণ:**

```python
e = err(lambda: session.execute(insert(User).values(name="রহিম")))   # IntegrityError
print(type(e.orig).__name__, e.orig.sqlstate, e.orig.diag.constraint_name)   # UniqueViolation 23505 users_name_key
```

### `StatementError.params` { #statementerror-params }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের প্যারামিটার (dict, বা executemany হলে তালিকা)। `create_engine(..., hide_parameters=True)` দিলে বার্তায় দেখায় না (লগে পাসওয়ার্ড ইত্যাদি লুকাতে)।

**উদাহরণ:**

```python
e = err(lambda: session.execute(insert(User).values(name="রহিম")))   # IntegrityError
print(e.params)   # {'name': 'রহিম', 'version': 1}
```

### `StatementError.statement` { #statementerror-statement }

**ধরন:** অ্যাট্রিবিউট

যে SQL স্ট্রিং চালানো হচ্ছিল।

**উদাহরণ:**

```python
e = err(lambda: session.execute(text("SELECT * FROM nope")))   # ProgrammingError
print(e.statement)   # SELECT * FROM nope
```

## `DBAPIError` { #dbapierror }

```python
from sqlalchemy.exc import DBAPIError
```

ডেটাবেস ড্রাইভার (DB-API) এরর দিলে SQLAlchemy সেটিকে এই পরিবারের একটি ক্লাসে মুড়িয়ে দেয়; ড্রাইভার যে ধরনের এরর দেয় (PEP 249 অনুযায়ী) সেই নামের ক্লাস: `IntegrityError`, `OperationalError` ইত্যাদি। ফলে ড্রাইভার বদলালেও (psycopg2 → psycopg → asyncpg) আপনার `except` একই থাকে।

**উদাহরণ:**

```python
try:
    session.execute(insert(User).values(name="রহিম"))
except exc.DBAPIError as e:
    print(type(e).__name__, type(e.orig).__module__)   # IntegrityError psycopg.errors
    session.rollback()
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dbapierror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`driver_exception`](#dbapierror-driver-exception) | প্রপার্টি | (২.১-এ নতুন) **ড্রাইভারের নিজের** এরর অবজেক্ট। |
| [`instance()`](#dbapierror-instance) | ক্লাস মেথড (internal) | (ক্লাস মেথড) ড্রাইভারের এরর থেকে ঠিক কোন `DBAPIError` সাবক্লাস হবে তা বেছে নিয়ে বানায়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DBAPIError`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`StatementError` থেকে:** [`add_detail()`](#statementerror-add-detail) · [`connection_invalidated`](#statementerror-connection-invalidated) · [`ismulti`](#statementerror-ismulti) · [`orig`](#statementerror-orig) · [`params`](#statementerror-params) · [`statement`](#statementerror-statement)

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `DBAPIError.driver_exception` { #dbapierror-driver-exception }

**ধরন:** প্রপার্টি

(২.১-এ নতুন) **ড্রাইভারের নিজের** এরর অবজেক্ট। সাধারণ ড্রাইভারে এটি `orig`-এর সমান। কিন্তু asyncpg-এর মতো async ড্রাইভারে SQLAlchemy একটি "নকল" DB-API এরর (`EmulatedDBAPIException`) বানায়; তখন `orig` সেই নকল এরর, আর `driver_exception` asyncpg-এর আসল এরর।

**উদাহরণ:**

```python
e = err(lambda: session.execute(insert(User).values(name="রহিম")))   # IntegrityError
print(e.driver_exception is e.orig)   # True  (psycopg-এ দুটো একই)
```

### `DBAPIError.instance()` { #dbapierror-instance }

```python
DBAPIError.instance(statement, params, orig, dbapi_base_err, hide_parameters=False, connection_invalidated=False, dialect=None, ismulti=None)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) ড্রাইভারের এরর থেকে ঠিক কোন `DBAPIError` সাবক্লাস হবে তা বেছে নিয়ে বানায়। SQLAlchemy ভেতরে ব্যবহার করে; নিজের ডায়ালেক্ট বা পরীক্ষার কোড ছাড়া দরকার নেই।

**উদাহরণ:**

```python
e = exc.DBAPIError.instance("SELECT 1", {}, ValueError("boom"), Exception)
print(type(e).__name__, str(e).splitlines()[0])   # DBAPIError (builtins.ValueError) boom
```

## `IntegrityError` { #integrityerror }

```python
from sqlalchemy.exc import IntegrityError
```

**ডেটার নিয়ম ভাঙা:** UNIQUE (একই ইমেইল দুবার), FOREIGN KEY (নেই এমন id-তে রেফারেন্স), NOT NULL, CHECK। ওয়েব অ্যাপে সবচেয়ে বেশি ধরা হয় এমন এরর; FastAPI-তে সাধারণত HTTP 409 (Conflict)। কোন নিয়ম ভেঙেছে তা `e.orig`-এ।

**উদাহরণ:**

```python
try:
    session.add(User(name="রহিম"))
    session.commit()
except exc.IntegrityError as e:
    session.rollback()
    print(e.orig.sqlstate, e.orig.diag.constraint_name)   # 23505 users_name_key
# PostgreSQL কোড: 23505 unique, 23503 foreign key, 23502 not null, 23514 check
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `DataError` { #dataerror }

```python
from sqlalchemy.exc import DataError
```

**ডেটার মান বা ধরন ভুল:** সংখ্যার জায়গায় টেক্সট, দৈর্ঘ্যের বেশি স্ট্রিং, শূন্য দিয়ে ভাগ, সীমার বাইরে সংখ্যা।

**উদাহরণ:**

```python
e = err(lambda: session.execute(text("SELECT 'abc'::int")))   # DataError
print(type(e.orig).__name__)   # InvalidTextRepresentation
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `ProgrammingError` { #programmingerror }

```python
from sqlalchemy.exc import ProgrammingError
```

**SQL-এ ভুল:** টেবিল/কলাম নেই, সিনট্যাক্স ভুল, প্যারামিটারের সংখ্যা ভুল। প্রায়ই মাইগ্রেশন না চালানোর লক্ষণ।

**উদাহরণ:**

```python
e = err(lambda: session.execute(text("SELECT * FROM nope")))   # ProgrammingError
print(type(e.orig).__name__)   # UndefinedTable
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `OperationalError` { #operationalerror }

```python
from sqlalchemy.exc import OperationalError
```

**ডেটাবেস চালানোর সমস্যা, প্রায়ই আপনার কোডের বাইরে:** সংযোগ হয় না, সংযোগ কেটে গেছে, deadlock, statement timeout, ডিস্ক ভর্তি। অনেক ক্ষেত্রে আবার চেষ্টা করলে চলে; FastAPI-তে সাধারণত HTTP 503।

**উদাহরণ:**

```python
e = err(lambda: create_engine("postgresql+psycopg://postgres@127.0.0.1:1/x").connect())   # OperationalError
print("Connection refused" in str(e))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `InterfaceError` { #interfaceerror }

```python
from sqlalchemy.exc import InterfaceError
```

ডেটাবেস নয়, **ড্রাইভারের নিজের** সমস্যা (ড্রাইভারের "ইন্টারফেস" অংশে)। যেমন psycopg2-এ বন্ধ সংযোগ ব্যবহার করা। কোন ঘটনায় কোন ক্লাস তা ড্রাইভারভেদে আলাদা: একই কাজে psycopg 3 দেয় `OperationalError`।

**উদাহরণ:**

```python
e2 = create_engine("postgresql+psycopg2://postgres@127.0.0.1/apiref")
def closed():
    with e2.connect() as c:
        c.connection.driver_connection.close()
        c.exec_driver_sql("SELECT 1")
e = err(closed)   # InterfaceError
print(e.orig, e.connection_invalidated)   # connection already closed True
e2.dispose()
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `InternalError` { #internalerror }

```python
from sqlalchemy.exc import InternalError
```

ডেটাবেসের ভেতরের অবস্থাজনিত এরর। PostgreSQL-এ সবচেয়ে পরিচিত: একটি এররের পর একই transaction-এ আবার কুয়েরি চালালে "current transaction is aborted" (আগে `ROLLBACK` লাগবে)।

**উদাহরণ:**

```python
def after_failure():
    with engine.begin() as c:
        try:
            c.exec_driver_sql("SELECT 1/0")
        except exc.DataError:
            pass                          # এরর গিলে ফেললাম, কিন্তু rollback করিনি
        c.exec_driver_sql("SELECT 1")
e = err(after_failure)   # InternalError
print(type(e.orig).__name__)   # InFailedSqlTransaction
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `NotSupportedError` { #notsupportederror }

```python
from sqlalchemy.exc import NotSupportedError
```

ডেটাবেস বা ড্রাইভার এই ফিচার সমর্থন করে না।

**উদাহরণ:**

```python
e = err(lambda: session.execute(text("SELECT count(*) FROM users FOR UPDATE")))   # NotSupportedError
print(e.orig)   # FOR UPDATE is not allowed with aggregate functions
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `DatabaseError` { #databaseerror }

```python
from sqlalchemy.exc import DatabaseError
```

ডেটাবেস-সংক্রান্ত এররের সাধারণ ক্লাস: `DataError`, `OperationalError`, `IntegrityError`, `InternalError`, `ProgrammingError`, `NotSupportedError` এর সন্তান (`InterfaceError` নয়)। নির্দিষ্ট ক্লাসে পড়ে না এমন ডেটাবেস এররে ড্রাইভার সরাসরি এটা দেয়।

**উদাহরণ:**

```python
print([c.__name__ for c in exc.DatabaseError.__subclasses__()])
# ['DataError', 'OperationalError', 'IntegrityError', 'InternalError', 'ProgrammingError', 'NotSupportedError']
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DBAPIError`](#dbapierror-summary)-এর মতো।

## `EmulatedDBAPIException` { #emulateddbapiexception }

```python
from sqlalchemy.exc import EmulatedDBAPIException
```

(২.১-এ নতুন) যে ড্রাইভারের নিজস্ব DB-API এরর-কাঠামো নেই (যেমন **asyncpg**), তার জন্য SQLAlchemy যে "নকল" DB-API এরর বানায়, তাদের মূল ক্লাস। `e.orig` হয় এটি; asyncpg-এর আসল এরর পেতে `e.orig.driver_exception` বা `e.driver_exception`।

**উদাহরণ:**

```python
from sqlalchemy.ext.asyncio import create_async_engine
async def main():
    ae = create_async_engine("postgresql+asyncpg://postgres@127.0.0.1/apiref")
    try:
        async with ae.begin() as c:
            await c.execute(insert(User).values(name="রহিম"))
    except exc.IntegrityError as e:
        print(isinstance(e.orig, exc.EmulatedDBAPIException), type(e.orig.driver_exception).__module__)
        # True asyncpg.exceptions
        print(e.driver_exception.sqlstate)   # 23505
    await ae.dispose()
asyncio.run(main())
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #emulateddbapiexception-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`driver_exception`](#emulateddbapiexception-driver-exception) | প্রপার্টি | ড্রাইভারের আসল এক্সেপশন (যেমন `asyncpg.exceptions.UniqueViolationError`)। |

### `EmulatedDBAPIException.driver_exception` { #emulateddbapiexception-driver-exception }

**ধরন:** প্রপার্টি

ড্রাইভারের আসল এক্সেপশন (যেমন `asyncpg.exceptions.UniqueViolationError`)।

**উদাহরণ:**

```python
fake = exc.EmulatedDBAPIException("বার্তা", ValueError("আসল"))
print(repr(fake.driver_exception))   # ValueError('আসল')
```

## সংযোগ ও পুল { #disconnectionerror-group }

## `DisconnectionError` { #disconnectionerror }

```python
from sqlalchemy.exc import DisconnectionError
```

পুলের ইভেন্টে (যেমন `checkout`) **আপনি নিজে** এটি raise করলে পুল বোঝে "এই সংযোগটি নষ্ট", সেটি ফেলে দিয়ে নতুন সংযোগ নিয়ে আবার চেষ্টা করে (সর্বোচ্চ তিনবার)। নিজের "সংযোগ বেঁচে আছে কি না" পরীক্ষার জন্য (আজকাল সাধারণত `pool_pre_ping=True`-ই যথেষ্ট)।

**উদাহরণ:**

```python
calls = []
e3 = create_engine("sqlite://")
@event.listens_for(e3, "checkout")
def check(dbapi_con, record, proxy):
    calls.append(1)
    if len(calls) == 1:
        raise exc.DisconnectionError("পুরোনো সংযোগ")
with e3.connect() as c:
    print(c.scalar(text("SELECT 1")), len(calls))   # 1 2  (প্রথমটি ফেলে দিয়ে দ্বিতীয় সংযোগ)
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #disconnectionerror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`invalidate_pool`](#disconnectionerror-invalidate-pool) | অ্যাট্রিবিউট | `True` হলে শুধু এই সংযোগ নয়, **পুরো পুলের** পুরোনো সব সংযোগ বাতিল হবে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DisconnectionError`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `DisconnectionError.invalidate_pool` { #disconnectionerror-invalidate-pool }

**ধরন:** অ্যাট্রিবিউট

`True` হলে শুধু এই সংযোগ নয়, **পুরো পুলের** পুরোনো সব সংযোগ বাতিল হবে। `DisconnectionError`-এ `False`, `InvalidatePoolError`-এ `True`।

**উদাহরণ:**

```python
print(exc.DisconnectionError().invalidate_pool, exc.InvalidatePoolError().invalidate_pool)   # False True
```

## `InvalidatePoolError` { #invalidatepoolerror }

```python
from sqlalchemy.exc import InvalidatePoolError
```

`DisconnectionError`-এর মতো, কিন্তু পুলকে বলে **সব** পুরোনো সংযোগ বাতিল করতে (যেমন ডেটাবেস রিস্টার্ট হয়েছে বুঝলে)।

**উদাহরণ:**

```python
print(issubclass(exc.InvalidatePoolError, exc.DisconnectionError))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DisconnectionError`](#disconnectionerror-summary)-এর মতো।

## `TimeoutError` { #timeouterror }

```python
from sqlalchemy.exc import TimeoutError
```

পুল থেকে নির্দিষ্ট সময়ের (`pool_timeout`, ডিফল্ট ৩০ সেকেন্ড) মধ্যে সংযোগ পাওয়া গেল না: সব সংযোগ ব্যস্ত। প্রায়ই সংযোগ/সেশন বন্ধ না করার (leak) লক্ষণ, বা `pool_size` বাড়ানো দরকার। Python-এর বিল্ট-ইন `TimeoutError` নয়, তাই `exc.TimeoutError` লিখুন।

**উদাহরণ:**

```python
small = create_engine("postgresql+psycopg://postgres@127.0.0.1/apiref", pool_size=1, max_overflow=0, pool_timeout=0.1)
c1 = small.connect()                 # একমাত্র সংযোগ নিয়ে রাখলাম
e = err(lambda: small.connect())   # TimeoutError
print(str(e).split(",")[0])   # QueuePool limit of size 1 overflow 0 reached
c1.close(); small.dispose()
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoDBAPILoaded` { #nodbapiloaded }

```python
from sqlalchemy.exc import NoDBAPILoaded
```

ড্রাইভার (DBAPI মডিউল) লোড না করা ডায়ালেক্ট থেকে ড্রাইভার-নির্ভর কিছু চাওয়া হয়েছে। যেমন শুধু কম্পাইলের জন্য বানানো `mysql.dialect()`।

**উদাহরণ:**

```python
e = err(lambda: mysql.dialect().loaded_dbapi)   # NoDBAPILoaded
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## ভুল অনুরোধ (InvalidRequestError পরিবার) { #invalidrequesterror-group }

## `InvalidRequestError` { #invalidrequesterror }

```python
from sqlalchemy.exc import InvalidRequestError
```

"SQLAlchemy-কে এমন কিছু করতে বলা হয়েছে যা সে পারে না": সাধারণত কোডের ভুল বা ভুল অবস্থায় ডাকা। নিচের অনেক নির্দিষ্ট এরর (`NoResultFound`, `PendingRollbackError` …) এর সন্তান।

**উদাহরণ:**

```python
e = err(lambda: session.refresh(User(name="নতুন")))   # InvalidRequestError
print("is not persistent within this Session" in str(e))   # True  (নতুন অবজেক্ট, ডেটাবেসে নেই)
other = Session(engine)
u = other.get(User, 1)
e = err(lambda: session.add(u))   # InvalidRequestError  (একই অবজেক্ট দুই সেশনে)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `PendingRollbackError` { #pendingrollbackerror }

```python
from sqlalchemy.exc import PendingRollbackError
```

ORM-এ flush/commit-এ এরর হওয়ার পর `rollback()` না করেই সেশন আবার ব্যবহার করা হয়েছে। সমাধান: এরর ধরার জায়গায় `session.rollback()`, বা `with Session() as s, s.begin():` ব্যবহার করুন (এরর হলে নিজে rollback)। FastAPI-তে request-প্রতি নতুন সেশন দিলে এই সমস্যা কম হয়।

**উদাহরণ:**

```python
session.add(User(name="রহিম"))
try:
    session.flush()
except exc.IntegrityError:
    pass                                   # ভুল: rollback করা হয়নি
e = err(lambda: session.execute(select(User)))   # PendingRollbackError
session.rollback()
print(len(session.execute(select(User)).all()))   # 2  (এখন আবার চলছে)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoResultFound` { #noresultfound }

```python
from sqlalchemy.exc import NoResultFound
```

ঠিক একটি রো দরকার ছিল (`scalar_one()`, `one()`), কিন্তু একটিও পাওয়া যায়নি। FastAPI-তে সাধারণত HTTP 404। "না থাকলে `None`" চাইলে `scalar_one_or_none()` বা `session.get()` ব্যবহার করুন। `sqlalchemy.orm.exc.NoResultFound` এই একই ক্লাস।

**উদাহরণ:**

```python
try:
    session.execute(select(User).where(User.id == 99)).scalar_one()
except exc.NoResultFound:
    print("ইউজার নেই")   # ইউজার নেই
print(session.execute(select(User).where(User.id == 99)).scalar_one_or_none())   # None
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `MultipleResultsFound` { #multipleresultsfound }

```python
from sqlalchemy.exc import MultipleResultsFound
```

ঠিক একটি (বা শূন্য-অথবা-একটি) রো দরকার ছিল, কিন্তু একাধিক পাওয়া গেছে। প্রায়ই `WHERE` শর্ত অসম্পূর্ণ থাকার লক্ষণ। `sqlalchemy.orm.exc.MultipleResultsFound` এই একই ক্লাস।

**উদাহরণ:**

```python
e = err(lambda: session.execute(select(User)).scalar_one_or_none())   # MultipleResultsFound
print(e)   # Multiple rows were found when one or none was required
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `ResourceClosedError` { #resourceclosederror }

```python
from sqlalchemy.exc import ResourceClosedError
```

বন্ধ হয়ে যাওয়া Result, Connection বা cursor ব্যবহার করা হয়েছে। যেমন `with engine.connect()` ব্লকের বাইরে রেজাল্ট পড়া, বা রো নেই এমন স্টেটমেন্টের (UPDATE) রেজাল্ট থেকে রো চাওয়া।

**উদাহরণ:**

```python
with engine.connect() as c:
    result = c.execute(select(User.name))
    result.close()
    e = err(lambda: result.fetchone())   # ResourceClosedError
e = err(lambda: session.execute(update(User).values(version=1)).all())   # ResourceClosedError
print(e)   # This result object does not return rows. It has been closed automatically.
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoSuchColumnError` { #nosuchcolumnerror }

```python
from sqlalchemy.exc import NoSuchColumnError
```

`Row` থেকে নেই এমন কলাম চাওয়া হয়েছে (`row._mapping["nope"]`)। এটি Python-এর `KeyError`-ও, তাই `except KeyError` দিয়ে ধরলে সব ক্ষেত্রে চলে।

**লক্ষ্য করুন:** Core-এর `Connection.execute()`-এর রো দেয় `NoSuchColumnError`, কিন্তু ORM `Session.execute()`-এর রো দেয় **সাধারণ `KeyError`** (আর `row.email` দিলে `AttributeError`)।

**উদাহরণ:**

```python
with engine.connect() as c:
    row = c.execute(select(User.id, User.name)).first()
    e = err(lambda: row._mapping["email"])   # NoSuchColumnError
    print(isinstance(e, KeyError))   # True
orm_row = session.execute(select(User.id, User.name)).first()
e = err(lambda: orm_row._mapping["email"])   # KeyError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoSuchTableError` { #nosuchtableerror }

```python
from sqlalchemy.exc import NoSuchTableError
```

reflection-এ (`autoload_with=`, `inspect(engine).get_columns()` …) চাওয়া টেবিল ডেটাবেসে নেই বা দেখা যায় না। বার্তা শুধু টেবিলের নাম।

**উদাহরণ:**

```python
e = err(lambda: Table("nope", MetaData(), autoload_with=engine))   # NoSuchTableError
print(e)   # nope
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnreflectableTableError` { #unreflectabletableerror }

```python
from sqlalchemy.exc import UnreflectableTableError
```

টেবিল আছে, কিন্তু কোনো কারণে reflect করা যাচ্ছে না (ডায়ালেক্ট টেবিলের কোনো অংশ বুঝতে পারছে না)। খুব কম দেখা যায়; `MetaData.reflect()` চলার সময় এমন টেবিল বাদ দিতে `only=` ব্যবহার করুন।

**উদাহরণ:**

```python
print(issubclass(exc.UnreflectableTableError, exc.InvalidRequestError))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnboundExecutionError` { #unboundexecutionerror }

```python
from sqlalchemy.exc import UnboundExecutionError
```

SQL চালানোর মতো কোনো ডেটাবেস সংযোগ (bind) নেই। যেমন `Session()` বানানো হয়েছে কিন্তু `bind=engine` দেওয়া হয়নি।

**উদাহরণ:**

```python
e = err(lambda: Session().execute(select(User)))   # UnboundExecutionError
print(e)   # Could not locate a bind configured on mapper Mapper[User(users)], SQL expression or this Session.
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoInspectionAvailable` { #noinspectionavailable }

```python
from sqlalchemy.exc import NoInspectionAvailable
```

`inspect(x)`-এ এমন কিছু দেওয়া হয়েছে যা পরীক্ষা করা যায় না (ম্যাপ করা ক্লাস/অবজেক্ট, Engine, Table ইত্যাদি নয়)। ম্যাপ না করা ক্লাসে `session.get()` দিলেও আসে।

**উদাহরণ:**

```python
e = err(lambda: inspect(5))   # NoInspectionAvailable
e = err(lambda: session.get(dict, 1))   # NoInspectionAvailable
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `IllegalStateChangeError` { #illegalstatechangeerror }

```python
from sqlalchemy.exc import IllegalStateChangeError
```

(২.০) Session বা Connection এমন অবস্থায় ছিল যে চাওয়া কাজটি এখন করা যায় না; যেমন একটি মেথড চলার মাঝখানে (ইভেন্ট হুকের ভেতর থেকে) `close()`। প্রায়ই **একই সেশন একাধিক থ্রেড/টাস্ক থেকে একসাথে** ব্যবহারের লক্ষণ (সেশন থ্রেড-নিরাপদ নয়)।

**উদাহরণ:**

```python
s = Session(engine)
@event.listens_for(s, "after_begin")
def bad(sess, trans, conn):
    sess.close()                     # transaction শুরু হওয়ার মাঝেই close
e = err(lambda: s.execute(select(1)))   # IllegalStateChangeError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `AmbiguousColumnError` { #ambiguouscolumnerror }

```python
from sqlalchemy.exc import AmbiguousColumnError
```

(২.১-এ নতুন) একটি নাম একাধিক entity-তে আছে, তাই কোনটি বোঝানো হয়েছে বলা যাচ্ছে না। মূলত `filter_by(name=...)` একাধিক টেবিল join করা কুয়েরিতে। সমাধান: `where(User.name == ...)` স্পষ্টভাবে লিখুন।

**উদাহরণ:**

```python
stmt = select(User, Post).join(Post, User.posts)
e = err(lambda: stmt.filter_by(id=1))   # AmbiguousColumnError
print(str(stmt.where(User.id == 1).compile(compile_kwargs={"literal_binds": True})).splitlines()[-1])   # WHERE users.id = 1
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoReferenceError` { #noreferenceerror }

```python
from sqlalchemy.exc import NoReferenceError
```

`ForeignKey`-এর লক্ষ্য খুঁজে পাওয়া যাচ্ছে না: নিচের দুটির মূল ক্লাস।

**উদাহরণ:**

```python
print([c.__name__ for c in exc.NoReferenceError.__subclasses__()])   # ['NoReferencedTableError', 'NoReferencedColumnError']
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoReferencedTableError` { #noreferencedtableerror }

```python
from sqlalchemy.exc import NoReferencedTableError
```

`ForeignKey("x.id")`-এর টেবিল `x` একই `MetaData`-তে নেই। প্রায়ই টেবিলের নামে বানান ভুল, বা মডেলটি ইমপোর্ট না হওয়া (তাই MetaData-তে রেজিস্টার হয়নি)।

**উদাহরণ:**

```python
fk = ForeignKey("nope.id")
Table("t1", MetaData(), Column("x", Integer, fk))
e = err(lambda: fk.column)   # NoReferencedTableError
print(e.table_name)   # nope
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #noreferencedtableerror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`table_name`](#noreferencedtableerror-table-name) | অ্যাট্রিবিউট | যে টেবিল পাওয়া যায়নি তার নাম। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `NoReferencedTableError`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `NoReferencedTableError.table_name` { #noreferencedtableerror-table-name }

**ধরন:** অ্যাট্রিবিউট

যে টেবিল পাওয়া যায়নি তার নাম।

**উদাহরণ:**

```python
print(exc.NoReferencedTableError("বার্তা", "orders").table_name)   # orders
```

## `NoReferencedColumnError` { #noreferencedcolumnerror }

```python
from sqlalchemy.exc import NoReferencedColumnError
```

`ForeignKey("users.x")`-এর টেবিল আছে, কিন্তু কলাম `x` নেই।

**উদাহরণ:**

```python
m = MetaData()
Table("users", m, Column("id", Integer, primary_key=True))
fk = ForeignKey("users.uid")
Table("t1", m, Column("x", Integer, fk))
e = err(lambda: fk.column)   # NoReferencedColumnError
print(e.table_name, e.column_name)   # users uid
```

**Python `Exception`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Exception`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #noreferencedcolumnerror-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`column_name`](#noreferencedcolumnerror-column-name) | অ্যাট্রিবিউট | যে কলাম পাওয়া যায়নি তার নাম। |
| [`table_name`](#noreferencedcolumnerror-table-name) | অ্যাট্রিবিউট | যে টেবিলে কলামটি খোঁজা হয়েছিল। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `NoReferencedColumnError`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `NoReferencedColumnError.column_name` { #noreferencedcolumnerror-column-name }

**ধরন:** অ্যাট্রিবিউট

যে কলাম পাওয়া যায়নি তার নাম।

**উদাহরণ:**

```python
print(exc.NoReferencedColumnError("বার্তা", "users", "uid").column_name)   # uid
```

### `NoReferencedColumnError.table_name` { #noreferencedcolumnerror-table-name }

**ধরন:** অ্যাট্রিবিউট

যে টেবিলে কলামটি খোঁজা হয়েছিল।

**উদাহরণ:**

```python
print(exc.NoReferencedColumnError("বার্তা", "users", "uid").table_name)   # users
```

## async-সংক্রান্ত { #missinggreenlet-group }

## `MissingGreenlet` { #missinggreenlet }

```python
from sqlalchemy.exc import MissingGreenlet
```

async ড্রাইভারের IO এমন জায়গায় হলো যেখানে `await` করা যায় না। async-এ **সবচেয়ে পরিচিত এরর**। সাধারণ কারণ:

* `AsyncSession`-এ **lazy loading**: `user.posts` পড়লে ভেতরে কুয়েরি চলে, কিন্তু সেখানে `await` নেই। সমাধান: `selectinload()` দিয়ে আগেই লোড, `AsyncAttrs` + `await user.awaitable_attrs.posts`, বা `lazy="raise"`।
* commit-এর পর expired অ্যাট্রিবিউট পড়া (`expire_on_commit=False` দিন)।
* async ড্রাইভার দিয়ে সাধারণ `create_engine()` (`create_async_engine()` লাগবে)।

**উদাহরণ:**

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
async def main():
    ae = create_async_engine("postgresql+asyncpg://postgres@127.0.0.1/apiref")
    async with AsyncSession(ae) as s:
        u = await s.get(User, 1)
        try:
            u.posts                       # lazy load, কিন্তু এখানে await করা যায় না
        except exc.MissingGreenlet as e:
            print(type(e).__name__, e.code)   # MissingGreenlet xd2s
        await s.refresh(u, ["posts"])     # সমাধান: await করে লোড (বা আগেই selectinload)
        print(u.posts)   # []
    await ae.dispose()
asyncio.run(main())
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `AwaitRequired` { #awaitrequired }

```python
from sqlalchemy.exc import AwaitRequired
```

async মোডে একটি কাজ async IO আশা করেছিল কিন্তু কোনো `await` হয়নি। সাধারণত async engine-এ **sync ড্রাইভার** দিলে: যেমন `create_async_engine("postgresql+psycopg2://...")` (asyncpg বা psycopg দিন)।

**উদাহরণ:**

```python
from sqlalchemy.util import greenlet_spawn
async def main():
    await greenlet_spawn(lambda: 1, _require_await=True)   # ভেতরে কোনো await নেই
e = err(lambda: asyncio.run(main()))   # AwaitRequired
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## ভুল আর্গুমেন্ট ও স্কিমা { #argumenterror-group }

## `ArgumentError` { #argumenterror }

```python
from sqlalchemy.exc import ArgumentError
```

কোনো ফাংশন/ক্লাসে ভুল বা পরস্পরবিরোধী আর্গুমেন্ট। যেমন ভুল ডেটাবেস URL, `relationship()`-এ ভুল কনফিগারেশন। নিচের অনেক এরর এর সন্তান।

**উদাহরণ:**

```python
e = err(lambda: create_engine("আমার-ডেটাবেস"))   # ArgumentError
print(e)   # Could not parse SQLAlchemy URL from given URL string
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `ObjectNotExecutableError` { #objectnotexecutableerror }

```python
from sqlalchemy.exc import ObjectNotExecutableError
```

`execute()`-এ এমন কিছু দেওয়া হয়েছে যা চালানো যায় না। **২.০-তে আসা সবচেয়ে সাধারণ ভুল:** কাঁচা SQL স্ট্রিং সরাসরি দেওয়া। সমাধান: `text("...")` দিয়ে মুড়ুন, বা `exec_driver_sql()`।

**উদাহরণ:**

```python
with engine.connect() as c:
    e = err(lambda: c.execute("SELECT 1"))   # ObjectNotExecutableError
    print(c.execute(text("SELECT 1")).scalar())   # 1
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoSuchModuleError` { #nosuchmoduleerror }

```python
from sqlalchemy.exc import NoSuchModuleError
```

URL-এ যে ডায়ালেক্ট/ড্রাইভারের নাম দেওয়া হয়েছে তা খুঁজে পাওয়া যায়নি (বানান ভুল, বা তৃতীয় পক্ষের ডায়ালেক্ট ইনস্টল নেই)। ড্রাইভার প্যাকেজ (`psycopg` ইত্যাদি) ইনস্টল না থাকলে আসে সাধারণ `ModuleNotFoundError`।

**উদাহরণ:**

```python
e = err(lambda: create_engine("postgress://u@h/db"))   # NoSuchModuleError
print(e)   # Can't load plugin: sqlalchemy.dialects:postgress
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `NoForeignKeysError` { #noforeignkeyserror }

```python
from sqlalchemy.exc import NoForeignKeysError
```

দুটি টেবিল join করতে বলা হয়েছে, কিন্তু তাদের মধ্যে কোনো foreign key নেই, আর `ON` শর্তও দেওয়া হয়নি। `relationship()`-এ FK না পেলেও আসে। সমাধান: `join(B, A.x == B.y)` বা `relationship(primaryjoin=...)`।

**উদাহরণ:**

```python
e = err(lambda: select(User).join(Node))   # NoForeignKeysError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `AmbiguousForeignKeysError` { #ambiguousforeignkeyserror }

```python
from sqlalchemy.exc import AmbiguousForeignKeysError
```

দুটি টেবিলের মধ্যে **একাধিক** foreign key, তাই কোনটি দিয়ে join হবে বোঝা যাচ্ছে না। সমাধান: join-এ `ON` শর্ত, বা `relationship(foreign_keys=[...])`।

**উদাহরণ:**

```python
m = MetaData()
a = Table("accounts", m, Column("id", Integer, primary_key=True))
tr = Table("transfers", m, Column("id", Integer, primary_key=True),
           Column("from_id", ForeignKey("accounts.id")), Column("to_id", ForeignKey("accounts.id")))
e = err(lambda: a.join(tr))   # AmbiguousForeignKeysError
print(a.join(tr, a.c.id == tr.c.from_id).onclause)   # accounts.id = transfers.from_id
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `ConstraintColumnNotFoundError` { #constraintcolumnnotfounderror }

```python
from sqlalchemy.exc import ConstraintColumnNotFoundError
```

কনস্ট্রেইন্টে (`UniqueConstraint("x")` ইত্যাদি) স্ট্রিং নামে এমন কলাম দেওয়া হয়েছে যা টেবিলে নেই।

**উদাহরণ:**

```python
e = err(lambda: Table("t1", MetaData(), Column("email", String), UniqueConstraint("emial")))   # ConstraintColumnNotFoundError
print(e)   # Can't create UniqueConstraint on table 't1': no column named 'emial' is present.
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `DuplicateColumnError` { #duplicatecolumnerror }

```python
from sqlalchemy.exc import DuplicateColumnError
```

(২.০) টেবিলে একই নামের কলাম আবার যোগ করা হচ্ছে। ইচ্ছাকৃত হলে `append_column(col, replace_existing=True)`।

**উদাহরণ:**

```python
t = Table("t1", MetaData(), Column("a", Integer))
e = err(lambda: t.append_column(Column("a", String)))   # DuplicateColumnError
t.append_column(Column("a", String), replace_existing=True)
print(t.c.a.type)   # VARCHAR
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `IdentifierError` { #identifiererror }

```python
from sqlalchemy.exc import IdentifierError
```

কোনো নাম (ইনডেক্স, কনস্ট্রেইন্ট) ডেটাবেসের সর্বোচ্চ দৈর্ঘ্যের চেয়ে লম্বা (PostgreSQL-এ ৬৩ অক্ষর)। নামকরণ নিয়ম (naming convention) দিয়ে স্বয়ংক্রিয় নামে SQLAlchemy নিজে ছোট করে; **নিজে দেওয়া** লম্বা নামে এই এরর।

**উদাহরণ:**

```python
long_ix = Index("ix_" + "a" * 70, User.name)
e = err(lambda: schema.CreateIndex(long_ix).compile(dialect=postgresql.dialect()))   # IdentifierError
print(str(e).split("' ")[-1])   # exceeds maximum length of 63 characters
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `CircularDependencyError` { #circulardependencyerror }

```python
from sqlalchemy.exc import CircularDependencyError
```

কোন রো আগে লিখতে হবে তা ঠিক করা যাচ্ছে না, কারণ নির্ভরতা চক্রাকার: A-র জন্য আগে B লাগবে, B-র জন্য আগে A। ORM-এ দুটি অবজেক্ট একে অপরকে নির্দেশ করলে। সমাধান: একটি `relationship()`-এ `post_update=True` (একটি FK পরে আলাদা UPDATE দিয়ে বসবে)।

**উদাহরণ:**

```python
a, b = Node(id=1), Node(id=2)
a.parent = b
b.parent = a                    # চক্র!
session.add_all([a, b])
e = err(lambda: session.flush())   # CircularDependencyError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## কম্পাইলের এরর { #compileerror-group }

## `CompileError` { #compileerror }

```python
from sqlalchemy.exc import CompileError
```

এক্সপ্রেশন থেকে SQL স্ট্রিং বানাতে গিয়ে এরর। যেমন `insert().values()`-এ এমন কলামের নাম যা টেবিলে নেই।

**উদাহরণ:**

```python
e = err(lambda: insert(User).values(email="x@y.com").compile())   # CompileError
print(e)   # Unconsumed column names: email
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnsupportedCompilationError` { #unsupportedcompilationerror }

```python
from sqlalchemy.exc import UnsupportedCompilationError
```

এই ডায়ালেক্ট এই কনস্ট্রাক্ট লিখতে পারে না। যেমন PostgreSQL-বিশেষ `array[...]` SQLite-এ, বা কাস্টম কনস্ট্রাক্টের জন্য ঐ ডায়ালেক্টে `@compiles` না লেখা।

**উদাহরণ:**

```python
e = err(lambda: select(postgresql.array([1, 2])).compile(dialect=sqlite.dialect()))   # UnsupportedCompilationError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## ORM এক্সেপশন (sqlalchemy.orm.exc) { #detachedinstanceerror-group }

## `DetachedInstanceError` { #detachedinstanceerror }

```python
from sqlalchemy.orm.exc import DetachedInstanceError
```

সেশন থেকে বিচ্ছিন্ন (detached) অবজেক্টের এমন অ্যাট্রিবিউট পড়া হয়েছে যা লোড করা নেই: সেশন বন্ধ, তাই ডেটাবেস থেকে আনা যাচ্ছে না। **FastAPI-তে খুব পরিচিত:** রুটে সেশন বন্ধের পর রেসপন্স বানাতে গিয়ে `user.posts` বা commit-এ expired অ্যাট্রিবিউট পড়া। সমাধান: `expire_on_commit=False`, আগেই `selectinload()`, বা সেশন খোলা থাকতেই Pydantic মডেলে রূপান্তর।

**উদাহরণ:**

```python
with Session(engine) as s:
    u = s.get(User, 1)
e = err(lambda: u.posts)   # DetachedInstanceError
print(u.name)   # রহিম  (আগেই লোড হওয়া কলাম পড়া যায়)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `ObjectDeletedError` { #objectdeletederror }

```python
from sqlalchemy.orm.exc import ObjectDeletedError
```

অবজেক্টটি refresh করতে গিয়ে দেখা গেল ডেটাবেসে তার রো আর নেই (অন্য কেউ মুছে ফেলেছে)।

**উদাহরণ:**

```python
u = session.get(User, 2)
session.commit()                               # u এখন expired
with engine.begin() as c:
    c.execute(delete(User).where(User.id == 2))   # অন্য সংযোগ থেকে মোছা
e = err(lambda: u.name)   # ObjectDeletedError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `StaleDataError` { #staledataerror }

```python
from sqlalchemy.orm.exc import StaleDataError
```

UPDATE বা DELETE যতগুলো রো বদলাবে বলে আশা ছিল, তত রো মেলেনি: মাঝখানে অন্য কেউ রোটি বদলেছে বা মুছেছে। **optimistic locking** (`version_id_col`) ব্যবহারে এটাই "অন্য কেউ আগে বদলে ফেলেছে" সংকেত; FastAPI-তে সাধারণত HTTP 409। `ConcurrentModificationError` এই একই ক্লাসের পুরোনো নাম।

**উদাহরণ:**

```python
u = session.get(User, 1)                        # version = 1
with engine.begin() as c:
    c.execute(update(User).where(User.id == 1).values(version=2))   # অন্য কেউ বদলাল
u.name = "রহিম উদ্দিন"
e = err(lambda: session.commit())   # StaleDataError
print(e)   # UPDATE statement on table 'users' expected to update 1 row(s); 0 were matched.
print(orm_exc.ConcurrentModificationError is orm_exc.StaleDataError)   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `FlushError` { #flusherror }

```python
from sqlalchemy.orm.exc import FlushError
```

flush-এর সময় ORM নিজে একটি অসম্ভব অবস্থা ধরেছে (ডেটাবেসে যাওয়ার আগেই)। যেমন collection-এ `None` রাখা।

**উদাহরণ:**

```python
u = session.get(User, 1)
u.posts.append(None)
e = err(lambda: session.flush())   # FlushError
print(e)   # Can't flush None value found in collection User.posts
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnmappedError` { #unmappederror }

```python
from sqlalchemy.orm.exc import UnmappedError
```

ম্যাপিং আশা করা হয়েছিল কিন্তু নেই: নিচের তিনটির মূল ক্লাস।

**উদাহরণ:**

```python
print(sorted(c.__name__ for c in orm_exc.UnmappedError.__subclasses__()))   # ['UnmappedClassError', 'UnmappedInstanceError']
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnmappedClassError` { #unmappedclasserror }

```python
from sqlalchemy.orm.exc import UnmappedClassError
```

ম্যাপ না করা ক্লাসকে ম্যাপ করা ক্লাস হিসেবে ব্যবহার (যেমন `class_mapper()`-এ)। প্রায়ই মডেল `Base` থেকে না নেওয়া।

**উদাহরণ:**

```python
class Plain:
    pass
e = err(lambda: class_mapper(Plain))   # UnmappedClassError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnmappedInstanceError` { #unmappedinstanceerror }

```python
from sqlalchemy.orm.exc import UnmappedInstanceError
```

ম্যাপ না করা ক্লাসের **অবজেক্ট** সেশনে দেওয়া হয়েছে, যেমন Pydantic মডেল সরাসরি `session.add()`-এ। সমাধান: আগে ORM মডেল বানান: `User(**data.model_dump())`।

**উদাহরণ:**

```python
e = err(lambda: session.add({"name": "নতুন"}))   # UnmappedInstanceError
print(e)   # Class 'builtins.dict' is not mapped
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `UnmappedColumnError` { #unmappedcolumnerror }

```python
from sqlalchemy.orm.exc import UnmappedColumnError
```

একটি `Column`-এর জন্য mapper-এ কোনো অ্যাট্রিবিউট নেই (কলামটি এই mapper-এর টেবিলের নয়)।

**উদাহরণ:**

```python
e = err(lambda: inspect(User).get_property_by_column(Post.__table__.c.title))   # UnmappedColumnError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `LoaderStrategyException` { #loaderstrategyexception }

```python
from sqlalchemy.orm.exc import LoaderStrategyException
```

লোডার অপশন ভুল ধরনের অ্যাট্রিবিউটে: যেমন `selectinload()` (relationship-এর জন্য) সাধারণ কলামে।

**উদাহরণ:**

```python
e = err(lambda: session.execute(select(User).options(selectinload(User.name))))   # LoaderStrategyException
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `MappedAnnotationError` { #mappedannotationerror }

```python
from sqlalchemy.orm.exc import MappedAnnotationError
```

(২.০) `Mapped[...]`-এর ভেতরের Python টাইপ থেকে কোন SQL টাইপ হবে SQLAlchemy বুঝতে পারছে না। সমাধান: `mapped_column(JSON)`-এর মতো টাইপ স্পষ্ট দিন, বা `registry(type_annotation_map={...})`-এ যোগ করুন।

**উদাহরণ:**

```python
class B2(DeclarativeBase):
    pass
def define():
    class Doc(B2):
        __tablename__ = "docs"
        id: Mapped[int] = mapped_column(primary_key=True)
        data: Mapped[object]              # object → কোন SQL টাইপ?
e = err(define)   # MappedAnnotationError
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## `ObjectDereferencedError` { #objectdereferencederror }

```python
from sqlalchemy.orm.exc import ObjectDereferencedError
```

একটি অপারেশন শেষ করা গেল না কারণ সংশ্লিষ্ট অবজেক্টটি garbage collect হয়ে গেছে (কোথাও আর রেফারেন্স নেই)। খুব কম দেখা যায়; সাধারণত ইভেন্ট হুক বা weakref-নির্ভর কাস্টম কোডে।

**উদাহরণ:**

```python
print(issubclass(orm_exc.ObjectDereferencedError, exc.SQLAlchemyError))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SQLAlchemyError`](#sqlalchemyerror-summary)-এর মতো।

## সতর্কবার্তা (warning) { #sawarning-group }

## `SAWarning` { #sawarning }

```python
from sqlalchemy.exc import SAWarning
```

চলার সময় SQLAlchemy-র সাধারণ সতর্কবার্তা: এরর নয়, কিন্তু সম্ভবত ভুল কিছু হচ্ছে। যেমন **cartesian product** (দুটি টেবিল join শর্ত ছাড়া), relationship-এর মধ্যে সংঘাত। Python-এর `RuntimeWarning`-এর সন্তান। পরীক্ষায় (pytest) এগুলোকে এরর বানিয়ে ফেলা ভালো: `warnings.filterwarnings("error", category=SAWarning)`।

**উদাহরণ:**

```python
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    session.execute(select(User.id, Post.id))          # join শর্ত নেই!
print(type(w[0].message).__name__, str(w[0].message)[:40])   # SAWarning SELECT statement has a cartesian product
```

**Python `Warning`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `Warning`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sawarning-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SAWarning`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

## `SADeprecationWarning` { #sadeprecationwarning }

```python
from sqlalchemy.exc import SADeprecationWarning
```

বাতিলের পথে এমন API ব্যবহার হয়েছে; ভবিষ্যতের ভার্সনে সরে যাবে। Python-এর `DeprecationWarning`-এর সন্তান। আপগ্রেডের আগে পরীক্ষায় এগুলো এরর বানিয়ে খুঁজে বের করুন।

**উদাহরণ:**

```python
from sqlalchemy.dialects.postgresql import ENUM
warnings.filterwarnings("error", category=exc.SADeprecationWarning)
try:
    ENUM("a", name="x").inherit_schema
except exc.SADeprecationWarning as w:
    print(type(w).__name__, "|", w)   # SADeprecationWarning | The ``inherit_schema`` property is deprecated.
finally:
    warnings.resetwarnings()
```

**Python `DeprecationWarning`-এর সব মেথড** (`add_note()`, `args()`, `with_traceback()`) সাধারণ `DeprecationWarning`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sadeprecationwarning-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`deprecated_since`](#sadeprecationwarning-deprecated-since) | অ্যাট্রিবিউট | কোন ভার্সন থেকে বাতিলের পথে (যেমন `"2.0"`), বা অজানা হলে `None`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SADeprecationWarning`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLAlchemyError` থেকে:** [`code`](#sqlalchemyerror-code)

///

### `SADeprecationWarning.deprecated_since` { #sadeprecationwarning-deprecated-since }

**ধরন:** অ্যাট্রিবিউট

কোন ভার্সন থেকে বাতিলের পথে (যেমন `"2.0"`), বা অজানা হলে `None`।

**উদাহরণ:**

```python
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    session.query(User).get(1)            # পুরোনো Query.get()
print(w[0].message.deprecated_since)   # 2.0
```

## `Base20DeprecationWarning` { #base20deprecationwarning }

```python
from sqlalchemy.exc import Base20DeprecationWarning
```

২.০-তে বিশেষভাবে বাতিল বা legacy হওয়া API-র সতর্কবার্তার মূল ক্লাস (`LegacyAPIWarning`, `MovedIn20Warning`)।

**উদাহরণ:**

```python
print(issubclass(exc.LegacyAPIWarning, exc.Base20DeprecationWarning), issubclass(exc.Base20DeprecationWarning, exc.SADeprecationWarning))   # True True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SADeprecationWarning`](#sadeprecationwarning-summary)-এর মতো।

## `LegacyAPIWarning` { #legacyapiwarning }

```python
from sqlalchemy.exc import LegacyAPIWarning
```

**legacy** API ব্যবহার হয়েছে: এখনো চলে আর শিগগির সরবে না, কিন্তু নতুন কোডে বিকল্প ব্যবহার করুন। যেমন `session.query(User).get(1)` → `session.get(User, 1)`।

**উদাহরণ:**

```python
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    session.query(User).get(1)
print(type(w[0].message).__name__)   # LegacyAPIWarning
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SADeprecationWarning`](#sadeprecationwarning-summary)-এর মতো।

## `MovedIn20Warning` { #movedin20warning }

```python
from sqlalchemy.exc import MovedIn20Warning
```

API-টি শুধু **অন্য জায়গায় সরেছে**: কাজ একই, ইমপোর্টের পথ বদলেছে। যেমন `sqlalchemy.ext.declarative.declarative_base` → `sqlalchemy.orm.declarative_base` (আরও ভালো: `DeclarativeBase`)।

**উদাহরণ:**

```python
from sqlalchemy.ext.declarative import declarative_base
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    declarative_base()
print(type(w[0].message).__name__)   # MovedIn20Warning
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SADeprecationWarning`](#sadeprecationwarning-summary)-এর মতো।

## `SAPendingDeprecationWarning` { #sapendingdeprecationwarning }

```python
from sqlalchemy.exc import SAPendingDeprecationWarning
```

"ভবিষ্যতে বাতিল হবে" ধরনের সতর্কবার্তা (Python-এর `PendingDeprecationWarning`-এর সন্তান)। আধুনিক SQLAlchemy এটি আর ব্যবহার করে না; শুধু পুরোনো কোডের সামঞ্জস্যের জন্য আছে।

**উদাহরণ:**

```python
print(issubclass(exc.SAPendingDeprecationWarning, PendingDeprecationWarning))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SADeprecationWarning`](#sadeprecationwarning-summary)-এর মতো।

## `SATestSuiteWarning` { #satestsuitewarning }

```python
from sqlalchemy.exc import SATestSuiteWarning
```

SQLAlchemy-র নিজের টেস্ট-স্যুটে ধরা অ-মারাত্মক অবস্থার সতর্কবার্তা। অ্যাপ কোডে দেখা যায় না।

**উদাহরণ:**

```python
print(issubclass(exc.SATestSuiteWarning, Warning))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SAWarning`](#sawarning-summary)-এর মতো।

## পুরো ক্লাস-গাছ { #hierarchy }

```text
Exception
└── SQLAlchemyError
    ├── ArgumentError
    │   ├── AmbiguousForeignKeysError · NoForeignKeysError
    │   ├── ConstraintColumnNotFoundError · DuplicateColumnError
    │   ├── NoSuchModuleError · ObjectNotExecutableError
    │   └── orm.exc.MappedAnnotationError
    ├── CircularDependencyError
    ├── CompileError
    │   └── UnsupportedCompilationError
    ├── DisconnectionError
    │   └── InvalidatePoolError
    ├── IdentifierError
    ├── InvalidRequestError
    │   ├── AmbiguousColumnError · AwaitRequired · MissingGreenlet
    │   ├── IllegalStateChangeError · NoDBAPILoaded · NoInspectionAvailable
    │   ├── NoReferenceError ── NoReferencedTableError · NoReferencedColumnError
    │   ├── NoResultFound · MultipleResultsFound · NoSuchColumnError (+KeyError)
    │   ├── NoSuchTableError · UnreflectableTableError · UnboundExecutionError
    │   ├── PendingRollbackError · ResourceClosedError
    │   └── orm.exc: ObjectDeletedError · LoaderStrategyException · UnmappedColumnError
    │                UnmappedError ── UnmappedClassError · UnmappedInstanceError
    ├── StatementError
    │   └── DBAPIError
    │       ├── InterfaceError
    │       └── DatabaseError
    │           ├── DataError · OperationalError · IntegrityError
    │           └── InternalError · ProgrammingError · NotSupportedError
    ├── TimeoutError
    └── orm.exc: DetachedInstanceError · FlushError · StaleDataError · ObjectDereferencedError

Warning
├── RuntimeWarning ── SAWarning ── SATestSuiteWarning
├── DeprecationWarning ── SADeprecationWarning ── Base20DeprecationWarning
│                                                 ├── LegacyAPIWarning
│                                                 └── MovedIn20Warning
└── PendingDeprecationWarning ── SAPendingDeprecationWarning
```

## FastAPI-তে এরর থেকে HTTP রেসপন্স { #fastapi }

| এরর | সাধারণ HTTP কোড | কারণ |
| :--- | :--- | :--- |
| `NoResultFound` | 404 Not Found | চাওয়া রো নেই |
| `IntegrityError` | 409 Conflict (বা 422) | ডুপ্লিকেট / FK / NOT NULL |
| `StaleDataError` | 409 Conflict | অন্য কেউ আগে বদলেছে (optimistic locking) |
| `DataError` | 422 Unprocessable | মান ডেটাবেসে খাপ খায় না |
| `OperationalError`, `TimeoutError` | 503 Service Unavailable | ডেটাবেস নাগালের বাইরে / পুল ভর্তি |
| বাকি `SQLAlchemyError` | 500 | কোডের ভুল; লগ করুন, ব্যবহারকারীকে বিস্তারিত দেখাবেন না |

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import exc

app = FastAPI()

@app.exception_handler(exc.NoResultFound)
async def not_found(request: Request, e: exc.NoResultFound):
    return JSONResponse(status_code=404, content={"detail": "পাওয়া যায়নি"})

@app.exception_handler(exc.IntegrityError)
async def conflict(request: Request, e: exc.IntegrityError):
    # e.orig-এ ডেটাবেসের আসল এরর; বার্তা সরাসরি ব্যবহারকারীকে দেখাবেন না (SQL ফাঁস হতে পারে)
    return JSONResponse(status_code=409, content={"detail": "ডেটা আগে থেকেই আছে বা নিয়ম ভেঙেছে"})
```

/// warning | সেশন rollback ভুলবেন না

exception handler-এ পৌঁছানোর আগে, সেশনের dependency (`yield` দিয়ে) যেন এররে `rollback()` আর শেষে `close()` করে। `with Session(engine) as session:` ব্লক এটা নিজে করে। বিস্তারিত: [Session API](session.md)।

///
