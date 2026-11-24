# Session API: সম্পূর্ণ রেফারেন্স { #api-session }

/// note | এই পেজে যা আছে

* `Session`-এর **প্রতিটি** মেথড, প্রপার্টি ও কনস্ট্রাক্টর প্যারামিটার, সহজ বাংলায় আর উদাহরণসহ।
* `sessionmaker`, `SessionTransaction`, `scoped_session` আর সেশন-সম্পর্কিত ফাংশনগুলো।
* তালিকাটি সরাসরি SQLAlchemy **2.1**-এর সোর্স থেকে তৈরি, তাই কোনো সদস্য বাদ পড়েনি।

///

`Session` হলো ORM-এর কেন্দ্র। অবজেক্ট যোগ, খোঁজা, বদলানো, মোছা আর ট্রানজ্যাকশন, সব এর মাধ্যমেই। ধারণাগুলো সহজ ভাষায় বুঝতে আগে [Transaction ও Session-এর ভেতরের কাজ](../transactions.md) অধ্যায়টি পড়ে নিতে পারেন। এই পেজটি হলো "অভিধান": কোন মেথড ঠিক কী করে, তা খুঁজে দেখার জায়গা।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

এই পেজের সব উদাহরণ নিচের মডেল আর ডেটা ধরে লেখা, আর আমরা PostgreSQL 16-এ প্রতিটি উদাহরণ আলাদা করে চালিয়ে দেখেছি। ডেটাবেসে আগে থেকে তিনজন ইউজার আছেন: id ১ "রহিম" (একটি ঠিকানাসহ), id ২ "করিম", id ৩ "সুমি"।

```python
from sqlalchemy import ForeignKey, String, create_engine, func, insert, select
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship, selectinload, sessionmaker)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

engine = create_engine("postgresql+psycopg2://user:pass@localhost/shop")
session = Session(engine)
```

///

এখানে sync `Session` দেখানো হয়েছে। async কোডে প্রায় সব মেথড একই, শুধু সামনে `await` বসে। বিস্তারিত দেখুন [Async API](async.md) পেজে।

## `Session` { #session }

```python
from sqlalchemy.orm import Session
```

ORM-এর মাধ্যমে ডেটাবেসে সব কাজ (persistence) পরিচালনা করে। একটি `Session` একটি "কাজের খাতা" (unit of work): আপনি কোন অবজেক্ট যোগ করলেন, কোনটা বদলালেন, কোনটা মুছলেন, সব মনে রাখে, আর `flush()` বা `commit()`-এর সময় সঠিক ক্রমে SQL পাঠায়। ভেতরে একটি **identity map** রাখে, যাতে একই রো-র জন্য মেমরিতে একটাই অবজেক্ট থাকে।

সাধারণ নিয়ম: একটি কাজ (যেমন একটি HTTP রিকোয়েস্ট) = একটি সেশন। কাজ শেষে বন্ধ করুন। `with Session(engine) as session:` লিখলে ব্লক শেষে নিজেই বন্ধ হয়।

**উদাহরণ:**

```python
with Session(engine) as session:
    session.add(User(name="নতুন ইউজার"))
    session.commit()
    users = session.scalars(select(User).order_by(User.id)).all()
    print([u.name for u in users])
```

### কনস্ট্রাক্টরের প্যারামিটার { #session-params }

```python
Session(bind=None, *, autoflush=True, future=True, expire_on_commit=True, autobegin=True, twophase=False, binds=None, enable_baked_queries=True, info=None, query_cls=None, autocommit=False, join_transaction_mode='conditional_savepoint', close_resets_only=_NoArg.NO_ARG, execution_options={})
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bind` | যে `Engine` বা `Connection`-এর মাধ্যমে সেশন ডেটাবেসে যাবে। সাধারণত `Session(engine)`। |
| `autoflush` | `True` (ডিফল্ট) হলে প্রতিটি কুয়েরির আগে সেশন নিজে থেকেই জমা পরিবর্তন `flush()` করে, যাতে কুয়েরি সেগুলো দেখতে পায়। |
| `future` | 2.0 থেকে অর্থহীন, শুধু পুরোনো কোডের সাথে মিল রাখার জন্য আছে। সবসময় `True`। |
| `expire_on_commit` | `True` (ডিফল্ট) হলে `commit()`-এর পর সব অবজেক্টের মান মুছে যায় (expire), পরে পড়লে আবার ডেটাবেস থেকে আসে। async-এ সাধারণত `False` দিন। |
| `autobegin` | `True` (ডিফল্ট) হলে প্রথম কাজের সময় ট্রানজ্যাকশন নিজে শুরু হয়। `False` দিলে আগে `session.begin()` না ডাকলে এরর। |
| `twophase` | `True` দিলে commit দুই ধাপে হয় (two-phase commit), একাধিক ডেটাবেসে একসাথে নিশ্চিতভাবে commit করার জন্য। |
| `binds` | মডেল বা টেবিল অনুযায়ী আলাদা Engine-এর একটি dict, যেমন `{User: engine1, Order: engine2}`। |
| `enable_baked_queries` | পুরোনো "baked query" ক্যাশ চালু রাখবে কি না (legacy, শুধু `session.query()`-এ প্রভাব ফেলে)। |
| `info` | নিজের যেকোনো তথ্য রাখার জন্য একটি dict, পরে `session.info` দিয়ে পাওয়া যায়। |
| `query_cls` | legacy `session.query()` কোন `Query` ক্লাস ব্যবহার করবে। |
| `autocommit` | 1.x-এর পুরোনো autocommit মোড। 2.0-তে সরানো হয়েছে; শুধু `False` গ্রহণযোগ্য। |
| `join_transaction_mode` | বাইরে থেকে দেওয়া `Connection`-এ আগেই ট্রানজ্যাকশন চললে সেশন কীভাবে যোগ দেবে: `"conservative_savepoint"` (ডিফল্ট), `"create_savepoint"` (টেস্টে কাজের), `"rollback_only"`, `"control_fully"`। |
| `close_resets_only` | `True` (ডিফল্ট) হলে `close()`-এর পরও সেশনটি আবার ব্যবহার করা যায়। `False` দিলে `close()` মানে চিরতরে বন্ধ। |
| `execution_options` | (২.১-এ নতুন) এই সেশনের প্রতিটি `execute()`-এ প্রযোজ্য ডিফল্ট execution option-এর dict, যেমন `{"populate_existing": True}`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #session-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#session-add) | মেথড | একটি অবজেক্টকে সেশনে যোগ করে। |
| [`add_all()`](#session-add-all) | মেথড | অনেকগুলো অবজেক্ট একসাথে সেশনে যোগ করে, প্রতিটির জন্য `add()` ডাকার সমান। |
| [`begin()`](#session-begin) | মেথড | স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে আর একটি `SessionTransaction` দেয়। |
| [`begin_nested()`](#session-begin-nested) | মেথড | চলমান ট্রানজ্যাকশনের ভেতরে একটি "নেস্টেড" ট্রানজ্যাকশন, মানে ডেটাবেসে `SAVEPOINT`, শুরু করে। |
| [`bind_mapper()`](#session-bind-mapper) | মেথড | একটি নির্দিষ্ট মডেলের সব কাজ কোন `Engine`-এ যাবে তা ঠিক করে দেয়। |
| [`bind_table()`](#session-bind-table) | মেথড | `bind_mapper()`-এর মতো, তবে মডেলের বদলে একটি `Table`-এর জন্য Engine ঠিক করে। |
| [`bulk_insert_mappings()`](#session-bulk-insert-mappings) | মেথড (legacy) | dict-এর তালিকা দিয়ে অনেক রো দ্রুত `INSERT` করে, ORM অবজেক্ট না বানিয়ে। |
| [`bulk_save_objects()`](#session-bulk-save-objects) | মেথড (legacy) | অনেক অবজেক্ট একসাথে INSERT/UPDATE করে, unit of work-এর অনেক হিসাব (event, relationship cascade) বাদ দিয়ে। |
| [`bulk_update_mappings()`](#session-bulk-update-mappings) | মেথড (legacy) | primary key-সহ dict-এর তালিকা দিয়ে অনেক রো আপডেট করে। |
| [`close()`](#session-close) | মেথড | সেশনের ট্রানজ্যাকশন শেষ (rollback) করে, কানেকশন পুলে ফেরত দেয়, আর সব অবজেক্টকে সেশন থেকে বিচ্ছিন্ন (detached) করে। |
| [`commit()`](#session-commit) | মেথড | জমা থাকা সব পরিবর্তন `flush()` করে, তারপর ডেটাবেসে `COMMIT` পাঠায়। |
| [`connection()`](#session-connection) | মেথড | সেশনের চলমান ট্রানজ্যাকশনের সাথে যুক্ত Core `Connection` দেয়। |
| [`connection_callable`](#session-connection-callable) | অ্যাট্রিবিউট (internal) | ভেতরের একটি হুক, যা সাধারণত `None` থাকে। |
| [`delete()`](#session-delete) | মেথড | একটি অবজেক্টকে মোছার জন্য চিহ্নিত করে। |
| [`delete_all()`](#session-delete-all) | মেথড | (২.১-এ নতুন) অনেকগুলো অবজেক্ট একসাথে মোছার জন্য চিহ্নিত করে, প্রতিটিতে `delete()` ডাকার সমান। |
| [`deleted`](#session-deleted) | প্রপার্টি | যে অবজেক্টগুলো `delete()` দিয়ে মোছার জন্য চিহ্নিত কিন্তু এখনো flush হয়নি, সেগুলোর সেট (set-এর মতো একটি কালেকশন)। |
| [`dirty`](#session-dirty) | প্রপার্টি | যে persistent অবজেক্টগুলোর কোনো অ্যাট্রিবিউট বদলানো হয়েছে, সেগুলোর সেট। |
| [`enable_relationship_loading()`](#session-enable-relationship-loading) | মেথড | একটি অবজেক্টকে সেশনে যোগ না করেই তার relationship লোড করার সুবিধা দেয়, ফরেন কি-র বর্তমান মান দিয়ে। |
| [`execute()`](#session-execute) | মেথড | যেকোনো স্টেটমেন্ট (`select`, `insert`, `update`, `delete`, `text`) চালায় আর একটি `Result` দেয়। |
| [`execution_options`](#session-execution-options) | অ্যাট্রিবিউট | (২.১-এ নতুন) কনস্ট্রাক্টরে দেওয়া ডিফল্ট execution option-গুলো, যা এই সেশনের প্রতিটি `execute()`-এ প্রয়োগ হয়। |
| [`expire()`](#session-expire) | মেথড | একটি অবজেক্টের সব (বা নির্দিষ্ট) অ্যাট্রিবিউটের মেমরিতে থাকা মান মুছে দেয়। |
| [`expire_all()`](#session-expire-all) | মেথড | সেশনের সব persistent অবজেক্টকে expire করে। |
| [`expunge()`](#session-expunge) | মেথড | একটি অবজেক্টকে সেশন থেকে সরিয়ে দেয় (detached করে)। |
| [`expunge_all()`](#session-expunge-all) | মেথড | সেশনের সব অবজেক্ট সরিয়ে identity map খালি করে। |
| [`flush()`](#session-flush) | মেথড | জমা থাকা সব পরিবর্তনের SQL (INSERT/UPDATE/DELETE) এখনই ডেটাবেসে পাঠায়, কিন্তু commit করে না। |
| [`get()`](#session-get) | মেথড | primary key দিয়ে একটি অবজেক্ট দেয়, না থাকলে `None`। |
| [`get_bind()`](#session-get-bind) | মেথড | একটি কুয়েরি বা মডেলের জন্য সেশন কোন `Engine`/`Connection` ব্যবহার করবে তা বের করে দেয়। |
| [`get_nested_transaction()`](#session-get-nested-transaction) | মেথড | এখন কোনো নেস্টেড (SAVEPOINT) ট্রানজ্যাকশন চললে সেটার `SessionTransaction` দেয়, নইলে `None`। |
| [`get_one()`](#session-get-one) | মেথড | `get()`-এর মতোই, কিন্তু রো না পেলে `None` না দিয়ে `NoResultFound` এরর দেয়। |
| [`get_transaction()`](#session-get-transaction) | মেথড | এখন যে মূল (root) ট্রানজ্যাকশন চলছে সেটার `SessionTransaction` দেয়, না থাকলে `None`। |
| [`identity_key()`](#session-identity-key) | ক্লাস মেথড | একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। |
| [`in_nested_transaction()`](#session-in-nested-transaction) | মেথড | এখন কোনো SAVEPOINT চললে `True`। |
| [`in_transaction()`](#session-in-transaction) | মেথড | এখন কোনো ট্রানজ্যাকশন চললে `True`। |
| [`info`](#session-info) | প্রপার্টি | নিজের তথ্য রাখার একটি dict, যেমন রিকোয়েস্ট id বা বর্তমান ইউজার। |
| [`invalidate()`](#session-invalidate) | মেথড | সেশন বন্ধ করে, আর ব্যবহৃত DBAPI কানেকশনগুলো "অকেজো" ঘোষণা করে পুলে ফেরত না দিয়ে ফেলে দেয়। |
| [`is_active`](#session-is-active) | প্রপার্টি | সেশন "আংশিক rollback" অবস্থায় না থাকলে `True`। |
| [`is_modified()`](#session-is-modified) | মেথড | অবজেক্টের কোনো অ্যাট্রিবিউটের মান আসলেই বদলেছে কি না দেখে `True`/`False` দেয়। |
| [`merge()`](#session-merge) | মেথড | বাইরের একটি অবজেক্টের অবস্থা সেশনের ভেতরের সংশ্লিষ্ট অবজেক্টে কপি করে, আর সেই ভেতরের অবজেক্টটি ফেরত দেয়। |
| [`merge_all()`](#session-merge-all) | মেথড | (২.১-এ নতুন) অনেক অবজেক্টে একসাথে `merge()` চালায় আর merge করা অবজেক্টগুলোর তালিকা দেয়। |
| [`new`](#session-new) | প্রপার্টি | যে নতুন অবজেক্টগুলো `add()` করা হয়েছে কিন্তু এখনো flush হয়নি (pending), সেগুলোর সেট। |
| [`no_autoflush`](#session-no-autoflush) | প্রপার্টি | একটি context manager, যার ভেতরে সাময়িকভাবে autoflush বন্ধ থাকে। |
| [`object_session()`](#session-object-session) | ক্লাস মেথড | একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। |
| [`prepare()`](#session-prepare) | মেথড | two-phase commit-এর প্রথম ধাপ: চলমান ট্রানজ্যাকশন "প্রস্তুত" করে। |
| [`query()`](#session-query) | মেথড (legacy) | 1.x যুগের `Query` অবজেক্ট দেয়। |
| [`refresh()`](#session-refresh) | মেথড | অবজেক্টের মানগুলো এখনই ডেটাবেস থেকে আবার পড়ে আনে (একটি SELECT)। |
| [`reset()`](#session-reset) | মেথড | সেশনকে একদম শুরুর অবস্থায় ফিরিয়ে নেয়: ট্রানজ্যাকশন বাতিল, সব অবজেক্ট বিচ্ছিন্ন, কানেকশন ফেরত। |
| [`rollback()`](#session-rollback) | মেথড | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`scalar()`](#session-scalar) | মেথড | একটি স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলামের মানটি দেয় (না থাকলে `None`)। |
| [`scalars()`](#session-scalars) | মেথড | একটি স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলাম দিয়ে একটি `ScalarResult` দেয়। |

### `Session.add()` { #session-add }

```python
Session.add(instance)
```

**ধরন:** মেথড

একটি অবজেক্টকে সেশনে যোগ করে। নতুন (transient) অবজেক্ট হলে পরের flush-এ `INSERT` হবে। অন্য সেশন থেকে আসা (detached) অবজেক্ট হলে আবার এই সেশনের সাথে যুক্ত হয়। `add()` নিজে কোনো SQL পাঠায় না।

**উদাহরণ:**

```python
user = User(name="তানিয়া")
session.add(user)
session.commit()          # এখন INSERT হলো
print(user.id)            # 4
```

### `Session.add_all()` { #session-add-all }

```python
Session.add_all(instances)
```

**ধরন:** মেথড

অনেকগুলো অবজেক্ট একসাথে সেশনে যোগ করে, প্রতিটির জন্য `add()` ডাকার সমান।

**উদাহরণ:**

```python
session.add_all([User(name="অনু"), User(name="বিনু")])
session.commit()
```

### `Session.begin()` { #session-begin }

```python
Session.begin(nested=False)
```

**ধরন:** মেথড

স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে আর একটি `SessionTransaction` দেয়। সাধারণত `with session.begin():` আকারে ব্যবহার হয়: ব্লক ঠিকঠাক শেষ হলে নিজেই commit, এরর হলে rollback। আগে থেকেই ট্রানজ্যাকশন চললে এরর দেয়।

**উদাহরণ:**

```python
with session.begin():
    session.add(User(name="নিরাপদ"))
# এখানে নিজেই COMMIT হয়ে গেছে
```

### `Session.begin_nested()` { #session-begin-nested }

```python
Session.begin_nested()
```

**ধরন:** মেথড

চলমান ট্রানজ্যাকশনের ভেতরে একটি "নেস্টেড" ট্রানজ্যাকশন, মানে ডেটাবেসে `SAVEPOINT`, শুরু করে। ভেতরের অংশ ব্যর্থ হলে শুধু সেটুকু বাতিল হয়, বাইরের কাজ থেকে যায়।

**উদাহরণ:**

```python
with session.begin():
    session.add(User(name="টিকে থাকবে"))
    try:
        with session.begin_nested():          # SAVEPOINT
            session.add(User(name="বাতিল হবে"))
            raise ValueError("সমস্যা")
    except ValueError:
        pass
print(session.scalars(select(User.name).where(User.id > 3)).all())   # ['টিকে থাকবে']
```

### `Session.bind_mapper()` { #session-bind-mapper }

```python
Session.bind_mapper(mapper, bind)
```

**ধরন:** মেথড

একটি নির্দিষ্ট মডেলের সব কাজ কোন `Engine`-এ যাবে তা ঠিক করে দেয়। একাধিক ডেটাবেস ব্যবহার করলে কাজে লাগে।

**উদাহরণ:**

```python
session.bind_mapper(User, engine)
print(session.get_bind(User) is engine)   # True
```

### `Session.bind_table()` { #session-bind-table }

```python
Session.bind_table(table, bind)
```

**ধরন:** মেথড

`bind_mapper()`-এর মতো, তবে মডেলের বদলে একটি `Table`-এর জন্য Engine ঠিক করে।

**উদাহরণ:**

```python
session.bind_table(User.__table__, engine)
print(session.get_bind(clause=User.__table__.select()) is engine)   # True
```

### `Session.bulk_insert_mappings()` { #session-bulk-insert-mappings }

```python
Session.bulk_insert_mappings(mapper, mappings, return_defaults=False, render_nulls=False)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

dict-এর তালিকা দিয়ে অনেক রো দ্রুত `INSERT` করে, ORM অবজেক্ট না বানিয়ে। আধুনিক বিকল্প: `session.execute(insert(User), [{...}, {...}])`।

**উদাহরণ:**

```python
session.bulk_insert_mappings(User, [{"name": "ক"}, {"name": "খ"}])
session.commit()
# আধুনিক রূপ:
session.execute(insert(User), [{"name": "গ"}, {"name": "ঘ"}])
session.commit()
```

### `Session.bulk_save_objects()` { #session-bulk-save-objects }

```python
Session.bulk_save_objects(objects, return_defaults=False, update_changed_only=True, preserve_order=True)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

অনেক অবজেক্ট একসাথে INSERT/UPDATE করে, unit of work-এর অনেক হিসাব (event, relationship cascade) বাদ দিয়ে। আধুনিক বিকল্প: `insert(Model)` / `update(Model)` স্টেটমেন্টে dict-এর তালিকা।

**উদাহরণ:**

```python
session.bulk_save_objects([User(name="চ"), User(name="ছ")])
session.commit()
```

### `Session.bulk_update_mappings()` { #session-bulk-update-mappings }

```python
Session.bulk_update_mappings(mapper, mappings)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

primary key-সহ dict-এর তালিকা দিয়ে অনেক রো আপডেট করে। আধুনিক বিকল্প: `session.execute(update(User), [{"id": 1, "name": "..."}])`।

**উদাহরণ:**

```python
session.bulk_update_mappings(User, [{"id": 2, "name": "করিম মিয়া"}])
session.commit()
# আধুনিক রূপ:
session.execute(update(User), [{"id": 3, "name": "সুমি আক্তার"}])
session.commit()
```

### `Session.close()` { #session-close }

```python
Session.close()
```

**ধরন:** মেথড

সেশনের ট্রানজ্যাকশন শেষ (rollback) করে, কানেকশন পুলে ফেরত দেয়, আর সব অবজেক্টকে সেশন থেকে বিচ্ছিন্ন (detached) করে। ডিফল্টে (`close_resets_only=True`) এরপরও সেশনটি আবার ব্যবহার করা যায়।

**উদাহরণ:**

```python
user = session.get(User, 1)
session.close()
print(user in session)   # False — এখন detached
```

### `Session.commit()` { #session-commit }

```python
Session.commit()
```

**ধরন:** মেথড

জমা থাকা সব পরিবর্তন `flush()` করে, তারপর ডেটাবেসে `COMMIT` পাঠায়। ডিফল্টে এরপর সব অবজেক্ট expire হয় (`expire_on_commit`)।

**উদাহরণ:**

```python
user = session.get(User, 2)
user.name = "করিম উদ্দিন"
session.commit()
```

### `Session.connection()` { #session-connection }

```python
Session.connection(bind_arguments=None, execution_options=None)
```

**ধরন:** মেথড

সেশনের চলমান ট্রানজ্যাকশনের সাথে যুক্ত Core `Connection` দেয়। একই ট্রানজ্যাকশনে raw SQL বা Core কাজ করতে কাজে লাগে।

**উদাহরণ:**

```python
conn = session.connection()
print(conn.exec_driver_sql("SELECT count(*) FROM users").scalar())   # 3
```

### `Session.connection_callable` { #session-connection-callable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের একটি হুক, যা সাধারণত `None` থাকে। horizontal sharding-এর মতো এক্সটেনশন এটি ব্যবহার করে ঠিক করে কোন কানেকশন লাগবে।

### `Session.delete()` { #session-delete }

```python
Session.delete(instance)
```

**ধরন:** মেথড

একটি অবজেক্টকে মোছার জন্য চিহ্নিত করে। পরের flush-এ `DELETE` হয়। relationship-এ cascade থাকলে চাইল্ডও মোছে।

**উদাহরণ:**

```python
user = session.get(User, 3)
session.delete(user)
session.commit()
```

### `Session.delete_all()` { #session-delete-all }

```python
Session.delete_all(instances)
```

**ধরন:** মেথড

(২.১-এ নতুন) অনেকগুলো অবজেক্ট একসাথে মোছার জন্য চিহ্নিত করে, প্রতিটিতে `delete()` ডাকার সমান।

**উদাহরণ:**

```python
users = session.scalars(select(User).where(User.id > 1)).all()
session.delete_all(users)
session.commit()
```

### `Session.deleted` { #session-deleted }

**ধরন:** প্রপার্টি

যে অবজেক্টগুলো `delete()` দিয়ে মোছার জন্য চিহ্নিত কিন্তু এখনো flush হয়নি, সেগুলোর সেট (set-এর মতো একটি কালেকশন)।

**উদাহরণ:**

```python
user = session.get(User, 2)
session.delete(user)
print(user in session.deleted)   # True
```

### `Session.dirty` { #session-dirty }

**ধরন:** প্রপার্টি

যে persistent অবজেক্টগুলোর কোনো অ্যাট্রিবিউট বদলানো হয়েছে, সেগুলোর সেট। মান আসলে বদলেছে কি না নিশ্চিত হতে `is_modified()` দেখুন।

**উদাহরণ:**

```python
user = session.get(User, 1)
user.name = "রহিম উদ্দিন"
print(user in session.dirty)   # True
```

### `Session.enable_relationship_loading()` { #session-enable-relationship-loading }

```python
Session.enable_relationship_loading(obj)
```

**ধরন:** মেথড

একটি অবজেক্টকে সেশনে যোগ না করেই তার relationship লোড করার সুবিধা দেয়, ফরেন কি-র বর্তমান মান দিয়ে। বিরল ক্ষেত্রে কাজে লাগে, যেমন ফর্মের ডেটা থেকে বানানো অবজেক্টের সম্পর্কিত অবজেক্ট দেখা।

**উদাহরণ:**

```python
addr = Address(email="new@example.com", user_id=1)
session.enable_relationship_loading(addr)
print(addr.user.name)   # রহিম — অথচ addr সেশনে add করা হয়নি
```

### `Session.execute()` { #session-execute }

```python
Session.execute(statement, params=None, *, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

যেকোনো স্টেটমেন্ট (`select`, `insert`, `update`, `delete`, `text`) চালায় আর একটি `Result` দেয়। ORM ও Core দুই ধরনের কুয়েরিই এখানে চলে। প্যারামিটার হিসেবে dict বা dict-এর তালিকা (বাল্ক) দেওয়া যায়।

**উদাহরণ:**

```python
result = session.execute(select(User.id, User.name).order_by(User.id))
for row in result:
    print(row.id, row.name)
```

### `Session.execution_options` { #session-execution-options }

**ধরন:** অ্যাট্রিবিউট

(২.১-এ নতুন) কনস্ট্রাক্টরে দেওয়া ডিফল্ট execution option-গুলো, যা এই সেশনের প্রতিটি `execute()`-এ প্রয়োগ হয়। শুধু পড়ার জন্য একটি dict।

**উদাহরণ:**

```python
s = Session(engine, execution_options={"populate_existing": True})
print(dict(s.execution_options))   # {'populate_existing': True}
s.close()
```

### `Session.expire()` { #session-expire }

```python
Session.expire(instance, attribute_names=None)
```

**ধরন:** মেথড

একটি অবজেক্টের সব (বা নির্দিষ্ট) অ্যাট্রিবিউটের মেমরিতে থাকা মান মুছে দেয়। পরের বার পড়লে ডেটাবেস থেকে নতুন করে আসে। async-এ expire করা মান পড়তে গেলে `MissingGreenlet` হয়, তাই সেখানে `refresh()` ভালো।

**উদাহরণ:**

```python
user = session.get(User, 1)
session.expire(user, ["name"])
print(user.name)   # আবার SELECT চালিয়ে আনে
```

### `Session.expire_all()` { #session-expire-all }

```python
Session.expire_all()
```

**ধরন:** মেথড

সেশনের সব persistent অবজেক্টকে expire করে। অন্য কেউ ডেটাবেস বদলেছে জানলে সব নতুন করে পড়তে কাজে লাগে।

**উদাহরণ:**

```python
session.get(User, 1)
session.expire_all()
```

### `Session.expunge()` { #session-expunge }

```python
Session.expunge(instance)
```

**ধরন:** মেথড

একটি অবজেক্টকে সেশন থেকে সরিয়ে দেয় (detached করে)। ডেটাবেসে কিছু হয় না, শুধু সেশন আর এটাকে ট্র্যাক করে না।

**উদাহরণ:**

```python
user = session.get(User, 1)
session.expunge(user)
print(user in session)   # False
```

### `Session.expunge_all()` { #session-expunge-all }

```python
Session.expunge_all()
```

**ধরন:** মেথড

সেশনের সব অবজেক্ট সরিয়ে identity map খালি করে। লম্বা লুপে মেমরি খালি রাখতে কাজে লাগে।

**উদাহরণ:**

```python
session.scalars(select(User)).all()
session.expunge_all()
print(len(session.identity_map))   # 0
```

### `Session.flush()` { #session-flush }

```python
Session.flush(objects=None)
```

**ধরন:** মেথড

জমা থাকা সব পরিবর্তনের SQL (INSERT/UPDATE/DELETE) এখনই ডেটাবেসে পাঠায়, কিন্তু commit করে না। ট্রানজ্যাকশন খোলাই থাকে। নতুন রো-র id দরকার হলে কাজে লাগে।

**উদাহরণ:**

```python
user = User(name="ফ্লাশ")
session.add(user)
print(user.id)     # None
session.flush()
print(user.id)     # 4 — কিন্তু এখনো commit হয়নি
```

### `Session.get()` { #session-get }

```python
Session.get(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

primary key দিয়ে একটি অবজেক্ট দেয়, না থাকলে `None`। আগে identity map দেখে, সেখানে থাকলে ডেটাবেসে যায়ই না। composite key হলে tuple দিন। `options=`, `with_for_update=`, `populate_existing=` দেওয়া যায়।

**উদাহরণ:**

```python
user = session.get(User, 1, options=[selectinload(User.addresses)])
print(user.name, [a.email for a in user.addresses])
print(session.get(User, 999))   # None
```

### `Session.get_bind()` { #session-get-bind }

```python
Session.get_bind(mapper=None, *, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

একটি কুয়েরি বা মডেলের জন্য সেশন কোন `Engine`/`Connection` ব্যবহার করবে তা বের করে দেয়। একাধিক ডেটাবেসের রাউটিং কাস্টমাইজ করতে সাবক্লাসে override করা হয়।

**উদাহরণ:**

```python
print(session.get_bind())   # Engine(postgresql+psycopg2://...)
```

### `Session.get_nested_transaction()` { #session-get-nested-transaction }

```python
Session.get_nested_transaction()
```

**ধরন:** মেথড

এখন কোনো নেস্টেড (SAVEPOINT) ট্রানজ্যাকশন চললে সেটার `SessionTransaction` দেয়, নইলে `None`।

**উদাহরণ:**

```python
with session.begin():
    print(session.get_nested_transaction())        # None
    with session.begin_nested():
        print(session.get_nested_transaction() is not None)   # True
```

### `Session.get_one()` { #session-get-one }

```python
Session.get_one(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

`get()`-এর মতোই, কিন্তু রো না পেলে `None` না দিয়ে `NoResultFound` এরর দেয়। "অবশ্যই থাকবে" এমন ক্ষেত্রে কোড পরিষ্কার রাখে।

**উদাহরণ:**

```python
from sqlalchemy.exc import NoResultFound
print(session.get_one(User, 1).name)
try:
    session.get_one(User, 999)
except NoResultFound:
    print("পাওয়া যায়নি")
```

### `Session.get_transaction()` { #session-get-transaction }

```python
Session.get_transaction()
```

**ধরন:** মেথড

এখন যে মূল (root) ট্রানজ্যাকশন চলছে সেটার `SessionTransaction` দেয়, না থাকলে `None`।

**উদাহরণ:**

```python
print(session.get_transaction())       # None — এখনো কিছু করা হয়নি
session.get(User, 1)                   # autobegin
print(session.get_transaction() is not None)   # True
```

### `Session.identity_key()` { #session-identity-key }

```python
Session.identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ক্লাস মেথড

একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। ক্লাস মেথড, তাই সেশন ছাড়াও ডাকা যায়।

**উদাহরণ:**

```python
print(Session.identity_key(User, 1))   # (<class '...User'>, (1,), None)
```

### `Session.in_nested_transaction()` { #session-in-nested-transaction }

```python
Session.in_nested_transaction()
```

**ধরন:** মেথড

এখন কোনো SAVEPOINT চললে `True`।

**উদাহরণ:**

```python
with session.begin():
    with session.begin_nested():
        print(session.in_nested_transaction())   # True
```

### `Session.in_transaction()` { #session-in-transaction }

```python
Session.in_transaction()
```

**ধরন:** মেথড

এখন কোনো ট্রানজ্যাকশন চললে `True`। প্রথম কুয়েরির পর autobegin হলেও `True` হয়।

**উদাহরণ:**

```python
print(session.in_transaction())   # False
session.get(User, 1)
print(session.in_transaction())   # True
```

### `Session.info` { #session-info }

**ধরন:** প্রপার্টি

নিজের তথ্য রাখার একটি dict, যেমন রিকোয়েস্ট id বা বর্তমান ইউজার। event hook-এ এই তথ্য পড়া যায়।

**উদাহরণ:**

```python
session.info["request_id"] = "req-42"
print(session.info["request_id"])
```

### `Session.invalidate()` { #session-invalidate }

```python
Session.invalidate()
```

**ধরন:** মেথড

সেশন বন্ধ করে, আর ব্যবহৃত DBAPI কানেকশনগুলো "অকেজো" ঘোষণা করে পুলে ফেরত না দিয়ে ফেলে দেয়। কানেকশন নষ্ট হয়ে গেছে সন্দেহ হলে (যেমন টাইমআউট বা বাতিল হওয়া কাজের পর) ব্যবহার করুন।

**উদাহরণ:**

```python
session.get(User, 1)
session.invalidate()
```

### `Session.is_active` { #session-is-active }

**ধরন:** প্রপার্টি

সেশন "আংশিক rollback" অবস্থায় না থাকলে `True`। flush-এ এরর হওয়ার পর `rollback()` না ডাকা পর্যন্ত এটি `False` থাকে।

**উদাহরণ:**

```python
print(session.is_active)   # True
```

### `Session.is_modified()` { #session-is-modified }

```python
Session.is_modified(instance, include_collections=True)
```

**ধরন:** মেথড

অবজেক্টের কোনো অ্যাট্রিবিউটের মান আসলেই বদলেছে কি না দেখে `True`/`False` দেয়। একই মান আবার বসালে `dirty`-তে থাকলেও এখানে `False` আসে।

**উদাহরণ:**

```python
user = session.get(User, 1)
user.name = "রহিম"                 # একই মান
print(session.is_modified(user))   # False
user.name = "রহিম খান"
print(session.is_modified(user))   # True
```

### `Session.merge()` { #session-merge }

```python
Session.merge(instance, *, load=True, options=None)
```

**ধরন:** মেথড

বাইরের একটি অবজেক্টের অবস্থা সেশনের ভেতরের সংশ্লিষ্ট অবজেক্টে কপি করে, আর সেই ভেতরের অবজেক্টটি ফেরত দেয়। একই primary key-এর অবজেক্ট না থাকলে ডেটাবেস থেকে লোড করে, তাও না পেলে নতুন বানায়। দেওয়া অবজেক্টটি নিজে সেশনে যুক্ত হয় না।

**উদাহরণ:**

```python
outside = User(id=2, name="করিম (নতুন নাম)")
merged = session.merge(outside)
session.commit()
print(merged is outside, merged.name)   # False করিম (নতুন নাম)
```

### `Session.merge_all()` { #session-merge-all }

```python
Session.merge_all(instances, *, load=True, options=None)
```

**ধরন:** মেথড

(২.১-এ নতুন) অনেক অবজেক্টে একসাথে `merge()` চালায় আর merge করা অবজেক্টগুলোর তালিকা দেয়।

**উদাহরণ:**

```python
merged = session.merge_all([User(id=2, name="ক২"), User(id=3, name="স৩")])
session.commit()
print([u.name for u in merged])
```

### `Session.new` { #session-new }

**ধরন:** প্রপার্টি

যে নতুন অবজেক্টগুলো `add()` করা হয়েছে কিন্তু এখনো flush হয়নি (pending), সেগুলোর সেট।

**উদাহরণ:**

```python
user = User(name="নতুন")
session.add(user)
print(user in session.new)   # True
```

### `Session.no_autoflush` { #session-no-autoflush }

**ধরন:** প্রপার্টি

একটি context manager, যার ভেতরে সাময়িকভাবে autoflush বন্ধ থাকে। অর্ধেক তৈরি অবজেক্ট নিয়ে কুয়েরি চালাতে হলে কাজে লাগে।

**উদাহরণ:**

```python
user = User()                     # name এখনো নেই (NOT NULL)
session.add(user)
with session.no_autoflush:
    count = session.scalar(select(func.count()).select_from(User))   # flush হবে না
user.name = "পরে নাম দিলাম"
session.commit()
print(count)   # 3
```

### `Session.object_session()` { #session-object-session }

```python
Session.object_session(instance)
```

**ধরন:** ক্লাস মেথড

একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। ক্লাস মেথড।

**উদাহরণ:**

```python
user = session.get(User, 1)
print(Session.object_session(user) is session)   # True
```

### `Session.prepare()` { #session-prepare }

```python
Session.prepare()
```

**ধরন:** মেথড

two-phase commit-এর প্রথম ধাপ: চলমান ট্রানজ্যাকশন "প্রস্তুত" করে। শুধু `twophase=True` সেশনে চলে। PostgreSQL-এ এর জন্য সার্ভারে `max_prepared_transactions` শূন্যের বেশি হতে হয় (ডিফল্ট শূন্য, তাই উদাহরণটি আমাদের টেস্ট সার্ভারে চালানো হয়নি)।

**উদাহরণ:**

```python
with Session(engine, twophase=True) as s:
    s.add(User(name="দুই ধাপ"))
    s.prepare()
    s.commit()
```

### `Session.query()` { #session-query }

```python
Session.query(*entities, **kwargs)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

1.x যুগের `Query` অবজেক্ট দেয়। এখনো চলে, কিন্তু নতুন কোডে `select()` + `session.scalars()` / `session.execute()` ব্যবহার করুন। `Query`-এর সব মেথড আর তাদের ২.০ বিকল্প: [Legacy Query API](query.md)।

**উদাহরণ:**

```python
old = session.query(User).filter(User.name == "রহিম").all()
new = session.scalars(select(User).where(User.name == "রহিম")).all()
print(old == new)   # True
```

### `Session.refresh()` { #session-refresh }

```python
Session.refresh(instance, attribute_names=None, with_for_update=None)
```

**ধরন:** মেথড

অবজেক্টের মানগুলো এখনই ডেটাবেস থেকে আবার পড়ে আনে (একটি SELECT)। ডেটাবেসে তৈরি মান (server_default, trigger) পেতে, বা অন্য কারো পরিবর্তন দেখতে ব্যবহার হয়। `attribute_names=` দিয়ে নির্দিষ্ট অ্যাট্রিবিউট বা relationship-ও রিফ্রেশ করা যায়।

**উদাহরণ:**

```python
user = session.get(User, 1)
with engine.begin() as other:      # অন্য কানেকশন থেকে কেউ নাম বদলাল
    other.execute(update(User).where(User.id == 1).values(name="বাইরে বদলানো"))
print(user.name)          # রহিম — মেমরিতে পুরোনো মান
session.refresh(user)
print(user.name)          # বাইরে বদলানো
```

### `Session.reset()` { #session-reset }

```python
Session.reset()
```

**ধরন:** মেথড

সেশনকে একদম শুরুর অবস্থায় ফিরিয়ে নেয়: ট্রানজ্যাকশন বাতিল, সব অবজেক্ট বিচ্ছিন্ন, কানেকশন ফেরত। `close()`-এর মতোই, তবে `close_resets_only=False` থাকলেও সেশনটি আবার ব্যবহারযোগ্য রাখে।

**উদাহরণ:**

```python
session.get(User, 1)
session.reset()
print(len(session.identity_map))   # 0
```

### `Session.rollback()` { #session-rollback }

```python
Session.rollback()
```

**ধরন:** মেথড

চলমান ট্রানজ্যাকশন বাতিল করে। নতুন (pending) অবজেক্ট বাদ পড়ে, আর বাকি অবজেক্ট expire হয়। কোনো এরর ধরার পর সেশন আবার ব্যবহার করতে হলে অবশ্যই `rollback()` লাগে।

**উদাহরণ:**

```python
session.add(User(name="বাতিল"))
session.rollback()
print(session.scalar(select(func.count()).select_from(User)))   # 3
```

### `Session.scalar()` { #session-scalar }

```python
Session.scalar(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড

একটি স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলামের মানটি দেয় (না থাকলে `None`)। গণনা, সর্বোচ্চ মান, বা একটি অবজেক্ট আনতে সুবিধাজনক।

**উদাহরণ:**

```python
total = session.scalar(select(func.count()).select_from(User))
first = session.scalar(select(User).order_by(User.id))
print(total, first.name)   # 3 রহিম
```

### `Session.scalars()` { #session-scalars }

```python
Session.scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড

একটি স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলাম দিয়ে একটি `ScalarResult` দেয়। ORM অবজেক্টের তালিকা আনার সবচেয়ে প্রচলিত উপায়।

**উদাহরণ:**

```python
users = session.scalars(select(User).where(User.id < 3).order_by(User.id)).all()
print([u.name for u in users])   # ['রহিম', 'করিম']
```

## `sessionmaker` { #sessionmaker }

```python
from sqlalchemy.orm import sessionmaker
```

একটি **সেশন কারখানা**। একবার কনফিগার করে রাখুন (engine, `expire_on_commit` ইত্যাদি), তারপর যতবার দরকার `SessionLocal()` ডেকে একই সেটিংয়ের নতুন সেশন বানান। অ্যাপে সাধারণত মডিউল লেভেলে একটি sessionmaker থাকে।

**উদাহরণ:**

```python
SessionLocal = sessionmaker(engine, expire_on_commit=False)
with SessionLocal() as s:
    print(s.get(User, 1).name)
```

### কনস্ট্রাক্টরের প্যারামিটার { #sessionmaker-params }

```python
sessionmaker(bind=None, *, class_=Session, autoflush=True, expire_on_commit=True, info=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bind` | নতুন সেশনগুলো কোন `Engine`-এ যুক্ত হবে। |
| `class_` | কোন সেশন ক্লাস বানাবে, ডিফল্ট `Session`। নিজের সাবক্লাস দিতে পারেন। |
| `autoflush` | নতুন সেশনের `autoflush` সেটিং। |
| `expire_on_commit` | নতুন সেশনের `expire_on_commit` সেটিং। |
| `info` | নতুন প্রতিটি সেশনের `info` dict-এ যা থাকবে। |
| `kw` | বাকি যেকোনো `Session` কনস্ট্রাক্টর প্যারামিটার (যেমন `autobegin`, `join_transaction_mode`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sessionmaker-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`begin()`](#sessionmaker-begin) | মেথড | নতুন সেশন বানিয়ে সাথে সাথে একটি ট্রানজ্যাকশনও শুরু করে। |
| [`configure()`](#sessionmaker-configure) | মেথড | sessionmaker-এর সেটিং পরে বদলায়। |
| [`identity_key()`](#sessionmaker-identity-key) | ক্লাস মেথড | একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। |
| [`object_session()`](#sessionmaker-object-session) | ক্লাস মেথড | একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। |

### `sessionmaker.begin()` { #sessionmaker-begin }

```python
sessionmaker.begin()
```

**ধরন:** মেথড

নতুন সেশন বানিয়ে সাথে সাথে একটি ট্রানজ্যাকশনও শুরু করে। `with` ব্লক শেষে commit হয়, তারপর সেশন বন্ধ হয়। এরর হলে rollback।

**উদাহরণ:**

```python
SessionLocal = sessionmaker(engine)
with SessionLocal.begin() as s:
    s.add(User(name="এক লাইনে"))
# এখানে commit + close দুটোই হয়ে গেছে
```

### `sessionmaker.configure()` { #sessionmaker-configure }

```python
sessionmaker.configure(**new_kw)
```

**ধরন:** মেথড

sessionmaker-এর সেটিং পরে বদলায়। এরপর থেকে বানানো সেশনে নতুন সেটিং প্রযোজ্য। শুরুতে engine জানা না থাকলে কাজে লাগে।

**উদাহরণ:**

```python
SessionLocal = sessionmaker()
SessionLocal.configure(bind=engine)
with SessionLocal() as s:
    print(s.get(User, 1).name)
```

### `sessionmaker.identity_key()` { #sessionmaker-identity-key }

```python
sessionmaker.identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.identity_key`](#session-identity-key)-এর মতো।

### `sessionmaker.object_session()` { #sessionmaker-object-session }

```python
sessionmaker.object_session(instance)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.object_session`](#session-object-session)-এর মতো।

## `SessionTransaction` { #sessiontransaction }

```python
from sqlalchemy.orm import SessionTransaction
```

সেশন লেভেলের একটি ট্রানজ্যাকশন। `session.begin()` বা `session.begin_nested()` এটি ফেরত দেয়। সাধারণত সরাসরি ব্যবহার করতে হয় না; `with session.begin():` লিখলেই যথেষ্ট।

**উদাহরণ:**

```python
trans = session.begin()
session.add(User(name="ট্রানজ্যাকশনে"))
trans.commit()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sessiontransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bound_connection()`](#sessiontransaction-bound-connection) | মেথড | (২.১-এ নতুন) এই ট্রানজ্যাকশন একটি নির্দিষ্ট bind-এর (engine/মডেল) জন্য যে `Connection` আগেই নিয়েছে সেটি দেয়। |
| [`close()`](#sessiontransaction-close) | মেথড | ট্রানজ্যাকশনটি বন্ধ করে। |
| [`commit()`](#sessiontransaction-commit) | মেথড | এই ট্রানজ্যাকশন commit করে। |
| [`connection()`](#sessiontransaction-connection) | মেথড | একটি bind key-র (যেমন মডেলের mapper) জন্য এই ট্রানজ্যাকশনের `Connection` দেয়, দরকার হলে নতুন নেয়। |
| [`connections`](#sessiontransaction-connections) | প্রপার্টি | এই ট্রানজ্যাকশন এ পর্যন্ত যেসব `Connection` নিয়েছে সেগুলোর dict। |
| [`declare_states()`](#sessiontransaction-declare-states) | ক্লাস মেথড (internal) | ভেতরের একটি ডেকোরেটর, যা ঠিক করে কোন অবস্থায় কোন মেথড ডাকা বৈধ (যেমন বন্ধ ট্রানজ্যাকশনে commit নয়)। |
| [`is_active`](#sessiontransaction-is-active) | প্রপার্টি | ট্রানজ্যাকশনটি এখনো চালু থাকলে `True`। |
| [`nested`](#sessiontransaction-nested) | অ্যাট্রিবিউট | এটি SAVEPOINT (নেস্টেড) ট্রানজ্যাকশন হলে `True`। |
| [`parent`](#sessiontransaction-parent) | প্রপার্টি | এই ট্রানজ্যাকশনের প্যারেন্ট `SessionTransaction`। |
| [`prepare()`](#sessiontransaction-prepare) | মেথড | two-phase commit-এর প্রস্তুতি ধাপ; `Session.prepare()`-এর মতো (twophase সেশন ও ডেটাবেসে সাপোর্ট লাগে)। |
| [`rollback()`](#sessiontransaction-rollback) | মেথড | এই ট্রানজ্যাকশন বাতিল করে। |

### `SessionTransaction.bound_connection()` { #sessiontransaction-bound-connection }

```python
SessionTransaction.bound_connection(bindkey=None, **kwargs)
```

**ধরন:** মেথড

(২.১-এ নতুন) এই ট্রানজ্যাকশন একটি নির্দিষ্ট bind-এর (engine/মডেল) জন্য যে `Connection` আগেই নিয়েছে সেটি দেয়।

**উদাহরণ:**

```python
with session.begin() as trans:
    session.get(User, 1)
    print(trans.bound_connection(User))   # <sqlalchemy.engine.base.Connection ...>
```

### `SessionTransaction.close()` { #sessiontransaction-close }

```python
SessionTransaction.close(invalidate=False)
```

**ধরন:** মেথড

ট্রানজ্যাকশনটি বন্ধ করে। commit না হয়ে থাকলে rollback হয়।

**উদাহরণ:**

```python
trans = session.begin()
trans.close()
print(session.in_transaction())   # False
```

### `SessionTransaction.commit()` { #sessiontransaction-commit }

```python
SessionTransaction.commit()
```

**ধরন:** মেথড

এই ট্রানজ্যাকশন commit করে। নেস্টেড হলে SAVEPOINT release হয়।

**উদাহরণ:**

```python
trans = session.begin()
session.add(User(name="কমিট"))
trans.commit()
```

### `SessionTransaction.connection()` { #sessiontransaction-connection }

```python
SessionTransaction.connection(bindkey, execution_options=None, **kwargs)
```

**ধরন:** মেথড

একটি bind key-র (যেমন মডেলের mapper) জন্য এই ট্রানজ্যাকশনের `Connection` দেয়, দরকার হলে নতুন নেয়।

**উদাহরণ:**

```python
with session.begin() as trans:
    conn = trans.connection(None)
    print(conn.exec_driver_sql("SELECT 1").scalar())   # 1
```

### `SessionTransaction.connections` { #sessiontransaction-connections }

**ধরন:** প্রপার্টি

এই ট্রানজ্যাকশন এ পর্যন্ত যেসব `Connection` নিয়েছে সেগুলোর dict।

**উদাহরণ:**

```python
with session.begin() as trans:
    session.get(User, 1)
    print(len(trans.connections))   # 1
```

### `SessionTransaction.declare_states()` { #sessiontransaction-declare-states }

```python
SessionTransaction.declare_states(prerequisite_states, moves_to)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের একটি ডেকোরেটর, যা ঠিক করে কোন অবস্থায় কোন মেথড ডাকা বৈধ (যেমন বন্ধ ট্রানজ্যাকশনে commit নয়)। অ্যাপ কোডে দরকার হয় না।

### `SessionTransaction.is_active` { #sessiontransaction-is-active }

**ধরন:** প্রপার্টি

ট্রানজ্যাকশনটি এখনো চালু থাকলে `True`।

**উদাহরণ:**

```python
trans = session.begin()
print(trans.is_active)   # True
trans.rollback()
print(trans.is_active)   # False
```

### `SessionTransaction.nested` { #sessiontransaction-nested }

**ধরন:** অ্যাট্রিবিউট

এটি SAVEPOINT (নেস্টেড) ট্রানজ্যাকশন হলে `True`।

**উদাহরণ:**

```python
with session.begin() as outer:
    inner = session.begin_nested()
    print(outer.nested, inner.nested)   # False True
    inner.rollback()
```

### `SessionTransaction.parent` { #sessiontransaction-parent }

**ধরন:** প্রপার্টি

এই ট্রানজ্যাকশনের প্যারেন্ট `SessionTransaction`। মূল ট্রানজ্যাকশনের জন্য `None`।

**উদাহরণ:**

```python
with session.begin() as outer:
    inner = session.begin_nested()
    print(inner.parent is outer)   # True
    inner.rollback()
```

### `SessionTransaction.prepare()` { #sessiontransaction-prepare }

```python
SessionTransaction.prepare()
```

**ধরন:** মেথড

two-phase commit-এর প্রস্তুতি ধাপ; `Session.prepare()`-এর মতো (twophase সেশন ও ডেটাবেসে সাপোর্ট লাগে)।

**উদাহরণ:**

```python
trans = Session(engine, twophase=True).begin()
trans.prepare()
trans.commit()
```

### `SessionTransaction.rollback()` { #sessiontransaction-rollback }

```python
SessionTransaction.rollback()
```

**ধরন:** মেথড

এই ট্রানজ্যাকশন বাতিল করে। নেস্টেড হলে শুধু SAVEPOINT পর্যন্ত ফেরে।

**উদাহরণ:**

```python
trans = session.begin()
session.add(User(name="বাতিল"))
trans.rollback()
```

## `scoped_session` { #scoped-session }

```python
from sqlalchemy.orm import scoped_session
```

একটি "রেজিস্ট্রি", যা প্রতি থ্রেডে (বা আপনার ঠিক করা scope-এ) একটি করে সেশন রাখে। `Session()` না বানিয়ে সরাসরি `db_session.add(...)` লিখলে সে নিজেই বর্তমান থ্রেডের সেশন খুঁজে কাজটি করে। Flask-এর মতো থ্রেড-ভিত্তিক অ্যাপে প্রচলিত। FastAPI-তে সাধারণত দরকার নেই, সেখানে `Depends(get_db)` ভালো। এর প্রায় সব মেথড `Session`-এর মেথডের proxy।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
db_session.add(User(name="থ্রেড সেশন"))
db_session.commit()
print(db_session() is db_session())   # True — একই থ্রেডে একই সেশন
db_session.remove()
```

### কনস্ট্রাক্টরের প্যারামিটার { #scoped-session-params }

```python
scoped_session(session_factory, scopefunc=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `session_factory` | নতুন সেশন বানানোর কারখানা, সাধারণত একটি `sessionmaker`। |
| `scopefunc` | একটি ফাংশন, যা বর্তমান "scope"-এর key দেয় (যেমন রিকোয়েস্ট id)। না দিলে প্রতি থ্রেডে একটি সেশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #scoped-session-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#scoped-session-add) | মেথড | একটি অবজেক্টকে সেশনে যোগ করে। |
| [`add_all()`](#scoped-session-add-all) | মেথড | অনেকগুলো অবজেক্ট একসাথে সেশনে যোগ করে, প্রতিটির জন্য `add()` ডাকার সমান। |
| [`autoflush`](#scoped-session-autoflush) | প্রপার্টি | বর্তমান সেশনের `autoflush` সেটিং পড়া বা বদলানোর proxy। |
| [`begin()`](#scoped-session-begin) | মেথড | স্পষ্টভাবে একটি ট্রানজ্যাকশন শুরু করে আর একটি `SessionTransaction` দেয়। |
| [`begin_nested()`](#scoped-session-begin-nested) | মেথড | চলমান ট্রানজ্যাকশনের ভেতরে একটি "নেস্টেড" ট্রানজ্যাকশন, মানে ডেটাবেসে `SAVEPOINT`, শুরু করে। |
| [`bind`](#scoped-session-bind) | প্রপার্টি | বর্তমান সেশন কোন `Engine`-এ যুক্ত তা দেয় (proxy)। |
| [`binds`](#scoped-session-binds) | প্রপার্টি | বর্তমান সেশনের মডেল/টেবিল-ভিত্তিক bind-এর dict (proxy)। |
| [`bulk_insert_mappings()`](#scoped-session-bulk-insert-mappings) | মেথড | dict-এর তালিকা দিয়ে অনেক রো দ্রুত `INSERT` করে, ORM অবজেক্ট না বানিয়ে। |
| [`bulk_save_objects()`](#scoped-session-bulk-save-objects) | মেথড | অনেক অবজেক্ট একসাথে INSERT/UPDATE করে, unit of work-এর অনেক হিসাব (event, relationship cascade) বাদ দিয়ে। |
| [`bulk_update_mappings()`](#scoped-session-bulk-update-mappings) | মেথড | primary key-সহ dict-এর তালিকা দিয়ে অনেক রো আপডেট করে। |
| [`close()`](#scoped-session-close) | মেথড | সেশনের ট্রানজ্যাকশন শেষ (rollback) করে, কানেকশন পুলে ফেরত দেয়, আর সব অবজেক্টকে সেশন থেকে বিচ্ছিন্ন (detached) করে। |
| [`commit()`](#scoped-session-commit) | মেথড | জমা থাকা সব পরিবর্তন `flush()` করে, তারপর ডেটাবেসে `COMMIT` পাঠায়। |
| [`configure()`](#scoped-session-configure) | মেথড | ভেতরের `sessionmaker`-এর সেটিং বদলায়। |
| [`connection()`](#scoped-session-connection) | মেথড | সেশনের চলমান ট্রানজ্যাকশনের সাথে যুক্ত Core `Connection` দেয়। |
| [`delete()`](#scoped-session-delete) | মেথড | একটি অবজেক্টকে মোছার জন্য চিহ্নিত করে। |
| [`delete_all()`](#scoped-session-delete-all) | মেথড | (২.১-এ নতুন) অনেকগুলো অবজেক্ট একসাথে মোছার জন্য চিহ্নিত করে, প্রতিটিতে `delete()` ডাকার সমান। |
| [`deleted`](#scoped-session-deleted) | প্রপার্টি | যে অবজেক্টগুলো `delete()` দিয়ে মোছার জন্য চিহ্নিত কিন্তু এখনো flush হয়নি, সেগুলোর সেট (set-এর মতো একটি কালেকশন)। |
| [`dirty`](#scoped-session-dirty) | প্রপার্টি | যে persistent অবজেক্টগুলোর কোনো অ্যাট্রিবিউট বদলানো হয়েছে, সেগুলোর সেট। |
| [`execute()`](#scoped-session-execute) | মেথড | যেকোনো স্টেটমেন্ট (`select`, `insert`, `update`, `delete`, `text`) চালায় আর একটি `Result` দেয়। |
| [`execution_options`](#scoped-session-execution-options) | প্রপার্টি | (২.১-এ নতুন) কনস্ট্রাক্টরে দেওয়া ডিফল্ট execution option-গুলো, যা এই সেশনের প্রতিটি `execute()`-এ প্রয়োগ হয়। |
| [`expire()`](#scoped-session-expire) | মেথড | একটি অবজেক্টের সব (বা নির্দিষ্ট) অ্যাট্রিবিউটের মেমরিতে থাকা মান মুছে দেয়। |
| [`expire_all()`](#scoped-session-expire-all) | মেথড | সেশনের সব persistent অবজেক্টকে expire করে। |
| [`expunge()`](#scoped-session-expunge) | মেথড | একটি অবজেক্টকে সেশন থেকে সরিয়ে দেয় (detached করে)। |
| [`expunge_all()`](#scoped-session-expunge-all) | মেথড | সেশনের সব অবজেক্ট সরিয়ে identity map খালি করে। |
| [`flush()`](#scoped-session-flush) | মেথড | জমা থাকা সব পরিবর্তনের SQL (INSERT/UPDATE/DELETE) এখনই ডেটাবেসে পাঠায়, কিন্তু commit করে না। |
| [`get()`](#scoped-session-get) | মেথড | primary key দিয়ে একটি অবজেক্ট দেয়, না থাকলে `None`। |
| [`get_bind()`](#scoped-session-get-bind) | মেথড | একটি কুয়েরি বা মডেলের জন্য সেশন কোন `Engine`/`Connection` ব্যবহার করবে তা বের করে দেয়। |
| [`get_one()`](#scoped-session-get-one) | মেথড | `get()`-এর মতোই, কিন্তু রো না পেলে `None` না দিয়ে `NoResultFound` এরর দেয়। |
| [`identity_key()`](#scoped-session-identity-key) | ক্লাস মেথড | একটি অবজেক্টের identity map-এর key, মানে `(ক্লাস, primary key-র tuple, identity_token)` বানিয়ে দেয়। |
| [`identity_map`](#scoped-session-identity-map) | প্রপার্টি | বর্তমান সেশনের identity map (proxy)। |
| [`info`](#scoped-session-info) | প্রপার্টি | নিজের তথ্য রাখার একটি dict, যেমন রিকোয়েস্ট id বা বর্তমান ইউজার। |
| [`is_active`](#scoped-session-is-active) | প্রপার্টি | সেশন "আংশিক rollback" অবস্থায় না থাকলে `True`। |
| [`is_modified()`](#scoped-session-is-modified) | মেথড | অবজেক্টের কোনো অ্যাট্রিবিউটের মান আসলেই বদলেছে কি না দেখে `True`/`False` দেয়। |
| [`merge()`](#scoped-session-merge) | মেথড | বাইরের একটি অবজেক্টের অবস্থা সেশনের ভেতরের সংশ্লিষ্ট অবজেক্টে কপি করে, আর সেই ভেতরের অবজেক্টটি ফেরত দেয়। |
| [`merge_all()`](#scoped-session-merge-all) | মেথড | (২.১-এ নতুন) অনেক অবজেক্টে একসাথে `merge()` চালায় আর merge করা অবজেক্টগুলোর তালিকা দেয়। |
| [`new`](#scoped-session-new) | প্রপার্টি | যে নতুন অবজেক্টগুলো `add()` করা হয়েছে কিন্তু এখনো flush হয়নি (pending), সেগুলোর সেট। |
| [`no_autoflush`](#scoped-session-no-autoflush) | প্রপার্টি | একটি context manager, যার ভেতরে সাময়িকভাবে autoflush বন্ধ থাকে। |
| [`object_session()`](#scoped-session-object-session) | ক্লাস মেথড | একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। |
| [`query()`](#scoped-session-query) | মেথড | 1.x যুগের `Query` অবজেক্ট দেয়। |
| [`query_property()`](#scoped-session-query-property) | মেথড (legacy) | মডেল ক্লাসে একটি `query` প্রপার্টি বানায়, যাতে `User.query.filter(...)` লেখা যায় (Flask-SQLAlchemy ধাঁচ)। |
| [`refresh()`](#scoped-session-refresh) | মেথড | অবজেক্টের মানগুলো এখনই ডেটাবেস থেকে আবার পড়ে আনে (একটি SELECT)। |
| [`remove()`](#scoped-session-remove) | মেথড | বর্তমান scope-এর সেশন বন্ধ করে রেজিস্ট্রি থেকে সরায়। |
| [`reset()`](#scoped-session-reset) | মেথড | সেশনকে একদম শুরুর অবস্থায় ফিরিয়ে নেয়: ট্রানজ্যাকশন বাতিল, সব অবজেক্ট বিচ্ছিন্ন, কানেকশন ফেরত। |
| [`rollback()`](#scoped-session-rollback) | মেথড | চলমান ট্রানজ্যাকশন বাতিল করে। |
| [`scalar()`](#scoped-session-scalar) | মেথড | একটি স্টেটমেন্ট চালিয়ে প্রথম রো-র প্রথম কলামের মানটি দেয় (না থাকলে `None`)। |
| [`scalars()`](#scoped-session-scalars) | মেথড | একটি স্টেটমেন্ট চালিয়ে প্রতিটি রো-র প্রথম কলাম দিয়ে একটি `ScalarResult` দেয়। |

### `scoped_session.add()` { #scoped-session-add }

```python
scoped_session.add(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add`](#session-add)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.add_all()` { #scoped-session-add-all }

```python
scoped_session.add_all(instances)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.add_all`](#session-add-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.autoflush` { #scoped-session-autoflush }

**ধরন:** প্রপার্টি

বর্তমান সেশনের `autoflush` সেটিং পড়া বা বদলানোর proxy।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
print(db_session.autoflush)   # True
db_session.remove()
```

### `scoped_session.begin()` { #scoped-session-begin }

```python
scoped_session.begin(nested=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin`](#session-begin)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.begin_nested()` { #scoped-session-begin-nested }

```python
scoped_session.begin_nested()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.begin_nested`](#session-begin-nested)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.bind` { #scoped-session-bind }

**ধরন:** প্রপার্টি

বর্তমান সেশন কোন `Engine`-এ যুক্ত তা দেয় (proxy)।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
print(db_session.bind is engine)   # True
db_session.remove()
```

### `scoped_session.binds` { #scoped-session-binds }

**ধরন:** প্রপার্টি

বর্তমান সেশনের মডেল/টেবিল-ভিত্তিক bind-এর dict (proxy)।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
print(db_session.binds)   # immutabledict({})
db_session.remove()
```

### `scoped_session.bulk_insert_mappings()` { #scoped-session-bulk-insert-mappings }

```python
scoped_session.bulk_insert_mappings(mapper, mappings, return_defaults=False, render_nulls=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.bulk_insert_mappings`](#session-bulk-insert-mappings)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.bulk_save_objects()` { #scoped-session-bulk-save-objects }

```python
scoped_session.bulk_save_objects(objects, return_defaults=False, update_changed_only=True, preserve_order=True)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.bulk_save_objects`](#session-bulk-save-objects)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.bulk_update_mappings()` { #scoped-session-bulk-update-mappings }

```python
scoped_session.bulk_update_mappings(mapper, mappings)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.bulk_update_mappings`](#session-bulk-update-mappings)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.close()` { #scoped-session-close }

```python
scoped_session.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.close`](#session-close)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.commit()` { #scoped-session-commit }

```python
scoped_session.commit()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.commit`](#session-commit)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.configure()` { #scoped-session-configure }

```python
scoped_session.configure(**kwargs)
```

**ধরন:** মেথড

ভেতরের `sessionmaker`-এর সেটিং বদলায়। বর্তমান scope-এ আগেই সেশন থাকলে সতর্কবার্তা দেয়।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker())
db_session.configure(bind=engine)
print(db_session.get(User, 1).name)
db_session.remove()
```

### `scoped_session.connection()` { #scoped-session-connection }

```python
scoped_session.connection(bind_arguments=None, execution_options=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.connection`](#session-connection)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.delete()` { #scoped-session-delete }

```python
scoped_session.delete(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.delete`](#session-delete)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.delete_all()` { #scoped-session-delete-all }

```python
scoped_session.delete_all(instances)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.delete_all`](#session-delete-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.deleted` { #scoped-session-deleted }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.deleted`](#session-deleted)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.dirty` { #scoped-session-dirty }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.dirty`](#session-dirty)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.execute()` { #scoped-session-execute }

```python
scoped_session.execute(statement, params=None, *, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.execute`](#session-execute)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.execution_options` { #scoped-session-execution-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.execution_options`](#session-execution-options)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.expire()` { #scoped-session-expire }

```python
scoped_session.expire(instance, attribute_names=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire`](#session-expire)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.expire_all()` { #scoped-session-expire-all }

```python
scoped_session.expire_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expire_all`](#session-expire-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.expunge()` { #scoped-session-expunge }

```python
scoped_session.expunge(instance)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge`](#session-expunge)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.expunge_all()` { #scoped-session-expunge-all }

```python
scoped_session.expunge_all()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.expunge_all`](#session-expunge-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.flush()` { #scoped-session-flush }

```python
scoped_session.flush(objects=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.flush`](#session-flush)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.get()` { #scoped-session-get }

```python
scoped_session.get(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get`](#session-get)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.get_bind()` { #scoped-session-get-bind }

```python
scoped_session.get_bind(mapper=None, *, clause=None, bind=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_bind`](#session-get-bind)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.get_one()` { #scoped-session-get-one }

```python
scoped_session.get_one(entity, ident, *, options=None, populate_existing=None, with_for_update=None, identity_token=None, execution_options={}, bind_arguments=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.get_one`](#session-get-one)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.identity_key()` { #scoped-session-identity-key }

```python
scoped_session.identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.identity_key`](#session-identity-key)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.identity_map` { #scoped-session-identity-map }

**ধরন:** প্রপার্টি

বর্তমান সেশনের identity map (proxy)।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
user = db_session.get(User, 1)          # রেফারেন্স রাখুন: identity map অবজেক্ট weak-ভাবে রাখে
print(len(db_session.identity_map))   # 1
db_session.remove()
```

### `scoped_session.info` { #scoped-session-info }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.info`](#session-info)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.is_active` { #scoped-session-is-active }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.is_active`](#session-is-active)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.is_modified()` { #scoped-session-is-modified }

```python
scoped_session.is_modified(instance, include_collections=True)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.is_modified`](#session-is-modified)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.merge()` { #scoped-session-merge }

```python
scoped_session.merge(instance, *, load=True, options=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.merge`](#session-merge)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.merge_all()` { #scoped-session-merge-all }

```python
scoped_session.merge_all(instances, *, load=True, options=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.merge_all`](#session-merge-all)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.new` { #scoped-session-new }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.new`](#session-new)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.no_autoflush` { #scoped-session-no-autoflush }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Session.no_autoflush`](#session-no-autoflush)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.object_session()` { #scoped-session-object-session }

```python
scoped_session.object_session(instance)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Session.object_session`](#session-object-session)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.query()` { #scoped-session-query }

```python
scoped_session.query(*entities, **kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.query`](#session-query)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.query_property()` { #scoped-session-query-property }

```python
scoped_session.query_property(query_cls=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

মডেল ক্লাসে একটি `query` প্রপার্টি বানায়, যাতে `User.query.filter(...)` লেখা যায় (Flask-SQLAlchemy ধাঁচ)। নতুন কোডে `select()` ব্যবহার করুন।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
User.query = db_session.query_property()
print(User.query.filter(User.id == 1).one().name)
db_session.remove()
```

### `scoped_session.refresh()` { #scoped-session-refresh }

```python
scoped_session.refresh(instance, attribute_names=None, with_for_update=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.refresh`](#session-refresh)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.remove()` { #scoped-session-remove }

```python
scoped_session.remove()
```

**ধরন:** মেথড

বর্তমান scope-এর সেশন বন্ধ করে রেজিস্ট্রি থেকে সরায়। প্রতিটি রিকোয়েস্ট বা থ্রেড শেষে অবশ্যই ডাকুন, নইলে কানেকশন আটকে থাকে।

**উদাহরণ:**

```python
db_session = scoped_session(sessionmaker(engine))
db_session.get(User, 1)
db_session.remove()
```

### `scoped_session.reset()` { #scoped-session-reset }

```python
scoped_session.reset()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.reset`](#session-reset)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.rollback()` { #scoped-session-rollback }

```python
scoped_session.rollback()
```

**ধরন:** মেথড

কাজ হুবহু [`Session.rollback`](#session-rollback)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.scalar()` { #scoped-session-scalar }

```python
scoped_session.scalar(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.scalar`](#session-scalar)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

### `scoped_session.scalars()` { #scoped-session-scalars }

```python
scoped_session.scalars(statement, params=None, *, execution_options={}, bind_arguments=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Session.scalars`](#session-scalars)-এর মতো। এখানে কাজটি বর্তমান scope-এর সেশনের ওপর হয়।

## `close_all_sessions()` { #close-all-sessions }

```python
from sqlalchemy.orm import close_all_sessions
```

```python
close_all_sessions()
```

**ধরন:** ফাংশন

মেমরিতে থাকা **সব** `Session` বন্ধ করে। অ্যাপ বন্ধের সময় বা টেস্টের শেষে পরিষ্কার করতে কাজে লাগে।

**উদাহরণ:**

```python
s1, s2 = Session(engine), Session(engine)
s1.get(User, 1); s2.get(User, 2)
close_all_sessions()
```

## `make_transient()` { #make-transient }

```python
from sqlalchemy.orm import make_transient
```

```python
make_transient(instance)
```

**ধরন:** ফাংশন

একটি অবজেক্টকে আবার "transient" (একদম নতুন, কোনো সেশনের অজানা) অবস্থায় নিয়ে যায়। primary key মান থেকে যায়। অবজেক্ট কপি করে নতুন রো বানাতে কাজে লাগে (id `None` করে আবার add)।

**উদাহরণ:**

```python
user = session.get(User, 1)
make_transient(user)
user.id = None
session.add(user)
session.commit()
print(user.id)   # 4 — একই নামে নতুন রো
```

## `make_transient_to_detached()` { #make-transient-to-detached }

```python
from sqlalchemy.orm import make_transient_to_detached
```

```python
make_transient_to_detached(instance)
```

**ধরন:** ফাংশন

একটি transient অবজেক্টকে "detached" বানায়, যেন এটি আগে কোনো সেশনে লোড হয়েছিল। ক্যাশ থেকে বানানো অবজেক্টকে `add()` দিয়ে INSERT ছাড়াই সেশনে ফেরাতে কাজে লাগে। primary key সেট থাকতে হবে।

**উদাহরণ:**

```python
cached = User(id=2, name="করিম")
make_transient_to_detached(cached)
session.add(cached)          # INSERT নয়, persistent হিসেবে যুক্ত
cached.name = "করিম (ক্যাশ থেকে)"
session.commit()             # UPDATE হয়
```

## `object_session()` { #object-session }

```python
from sqlalchemy.orm import object_session
```

```python
object_session(instance)
```

**ধরন:** ফাংশন

একটি অবজেক্ট কোন সেশনের সাথে যুক্ত তা দেয়, না থাকলে `None`। `Session.object_session()`-এর মতোই।

**উদাহরণ:**

```python
user = session.get(User, 1)
print(object_session(user) is session)   # True
```

## `was_deleted()` { #was-deleted }

```python
from sqlalchemy.orm import was_deleted
```

```python
was_deleted(object_)
```

**ধরন:** ফাংশন

অবজেক্টটি কোনো flush-এ ডেটাবেস থেকে মুছে গেছে কি না জানায়।

**উদাহরণ:**

```python
user = session.get(User, 3)
session.delete(user)
session.flush()
print(was_deleted(user))   # True
```

/// check | সংক্ষেপে মনে রাখুন

* লেখা: `add()` / `add_all()` → `flush()` (ঐচ্ছিক) → `commit()`। মোছা: `delete()` / `delete_all()`।
* পড়া: primary key-তে `get()` / `get_one()`, বাকি সব `scalars()` / `execute()` / `scalar()`।
* ট্রানজ্যাকশন: `with session.begin():`, ভেতরে আংশিক বাতিলের জন্য `begin_nested()`।
* মেমরির অবস্থা: `new`, `dirty`, `deleted`, `is_modified()`; নতুন করে পড়া `refresh()` / `expire()`।
* পুরোনো API (`query()`, `bulk_*`) চলে, কিন্তু নতুন কোডে `select()` আর `insert()`/`update()` স্টেটমেন্ট।

///
