# ORM Event API: Session, Mapper, Instance ও Attribute event { #api-orm-events }

/// note | এই পেজে যা আছে

ORM-এর **সব** event hook, প্রতিটির listener-সিগনেচার আর চালিয়ে দেখা উদাহরণ:

* `SessionEvents` (২৫টি): flush, commit, rollback, অবজেক্টের অবস্থা-পরিবর্তন, আর সবচেয়ে শক্তিশালী `do_orm_execute`।
* `MapperEvents` (১২টি): INSERT/UPDATE/DELETE-এর আগে-পরে, mapper configure।
* `InstanceEvents` (৮টি): অবজেক্ট তৈরি, লোড, refresh, expire, pickle।
* `AttributeEvents` (৯টি): অ্যাট্রিবিউট সেট, কালেকশনে যোগ/বাদ।
* `InstrumentationEvents` (৩টি) আর পুরোনো `QueryEvents` (৩টি)।

///

event নিবন্ধনের নিয়ম (`event.listen()`, `@event.listens_for`) আর Core event আছে [Core Event পেজে](events.md)।

/// tip | কোন কাজে কোন event

| কাজ | event |
| :--- | :--- |
| সব কুয়েরিতে soft-delete / tenant ফিল্টার | `SessionEvents.do_orm_execute` + `with_loader_criteria` |
| সেভের আগে অবজেক্ট যাচাই বা হিসাব (slug, total) | `SessionEvents.before_flush` |
| অডিট লগ: কোন অবজেক্ট বদলেছে | `before_flush` (`session.dirty`) বা `after_flush` |
| commit সফল হলে ইমেইল/ক্যাশ ক্লিয়ার | `SessionEvents.after_commit` (DB-তে কিছু লিখবেন না) |
| একটি মডেলের প্রতি INSERT-এ কিছু বসানো | `MapperEvents.before_insert` |
| অ্যাট্রিবিউট বদলালে প্রতিক্রিয়া (normalize) | `AttributeEvents.set` (`retval=True`) |

///

/// warning | সাধারণ ভুল

* `before_insert` / `after_update` ইত্যাদি mapper event-এর ভেতরে `session.add()` বা অন্য অবজেক্ট বদলানো কাজ করে না (flush ততক্ষণে পরিকল্পিত)। সেসব কাজ `before_flush`-এ করুন; mapper event-এ শুধু নিজের অবজেক্টের কলাম বা `connection.execute()`।
* async (`AsyncSession`)-এ listener বসান `AsyncSession.sync_session_class`-এ বা `Session` ক্লাসে; listener নিজে sync ফাংশন।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    slug: Mapped[str | None]
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now())
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Address(Base):          # id, city, user_id, user
    ...
```

ডেটাবেসে একজন ইউজার: রহিম (id ১, একটি ঠিকানা: ঢাকা)। `calls` একটি খালি তালিকা যেখানে listener-গুলো কী ঘটল লিখে রাখে। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `SessionEvents` { #sessionevents }

```python
from sqlalchemy.orm import SessionEvents
```

`Session`-এর event। টার্গেট: একটি `Session` অবজেক্ট, একটি `sessionmaker`, বা `Session` ক্লাস (সব session-এ)। উদাহরণে নিচের `on()` হেল্পার শুধু `event.listen()`, যা উদাহরণ শেষে listener সরিয়ে দেয়।

**উদাহরণ:**

```python
for name in ["before_flush", "after_flush", "before_commit", "after_commit"]:
    on(session, name, lambda *a, n=name, **k: calls.append(n))
session.add(User(name="করিম")); session.commit()
print(calls)   # ['before_commit', 'before_flush', 'after_flush', 'after_commit']  (commit শুরু → নিজে থেকে flush → commit শেষ)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sessionevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`after_attach()`](#sessionevents-after-attach) | মেথড | একটি অবজেক্ট session-এ যুক্ত হওয়ার পরে (`add()`, cascade, `merge()`)। |
| [`after_begin()`](#sessionevents-after-begin) | মেথড | session একটি কানেকশনে ট্রানজ্যাকশন শুরু করার পরে (প্রতি কানেকশনে একবার)। |
| [`after_bulk_delete()`](#sessionevents-after-bulk-delete) | মেথড (legacy) | পুরোনো `Query.delete()`-এর পরে। |
| [`after_bulk_update()`](#sessionevents-after-bulk-update) | মেথড (legacy) | পুরোনো `Query.update()`-এর পরে। |
| [`after_commit()`](#sessionevents-after-commit) | মেথড | commit সফল হওয়ার পরে। |
| [`after_flush()`](#sessionevents-after-flush) | মেথড | flush শেষ হলে, কিন্তু session-এর অবস্থা (`new`, `dirty`, `deleted`) তখনো আগের মতো; কী কী সেভ হলো দেখার জায়গা (অডিট)। |
| [`after_flush_postexec()`](#sessionevents-after-flush-postexec) | মেথড | flush-এর পরে session-এর অবস্থা হালনাগাদ হয়ে যাওয়ার পর (তখন `session.new` খালি)। |
| [`after_rollback()`](#sessionevents-after-rollback) | মেথড | আসল ডেটাবেস rollback হওয়ার পরে। |
| [`after_soft_rollback()`](#sessionevents-after-soft-rollback) | মেথড | যেকোনো rollback-এর পরে (nested বা "soft" rollback-সহ, যেখানে ডেটাবেসে কিছু নাও যেতে পারে)। |
| [`after_transaction_create()`](#sessionevents-after-transaction-create) | মেথড | একটি নতুন `SessionTransaction` (মূল বা nested) তৈরি হলে। |
| [`after_transaction_end()`](#sessionevents-after-transaction-end) | মেথড | একটি `SessionTransaction` শেষ হলে (commit/rollback/close)। |
| [`before_attach()`](#sessionevents-before-attach) | মেথড | অবজেক্ট session-এ যুক্ত হওয়ার আগে। |
| [`before_commit()`](#sessionevents-before-commit) | মেথড | commit-এর আগে (flush তখনো বাকি থাকতে পারে); শেষ মুহূর্তের যাচাই। |
| [`before_flush()`](#sessionevents-before-flush) | মেথড | flush শুরুর আগে: **অবজেক্ট বদলানো, নতুন অবজেক্ট যোগ, যাচাই করার সঠিক জায়গা** (`session.new`, `session.dirty`, `session.deleted` দেখে)। |
| [`deleted_to_detached()`](#sessionevents-deleted-to-detached) | মেথড | মোছা অবজেক্ট commit-এর পরে session থেকে বিচ্ছিন্ন হলে। |
| [`deleted_to_persistent()`](#sessionevents-deleted-to-persistent) | মেথড | মোছা (flush হওয়া) অবজেক্ট rollback-এ আবার persistent হলে। |
| [`detached_to_persistent()`](#sessionevents-detached-to-persistent) | মেথড | detached অবজেক্ট আবার session-এ যুক্ত হলে (`add()`)। |
| [`do_orm_execute()`](#sessionevents-do-orm-execute) | মেথড | session-এর প্রতিটি ORM স্টেটমেন্ট চালানোর আগে (`execute()`, `scalars()`, lazy load, `get()` …)। |
| [`loaded_as_persistent()`](#sessionevents-loaded-as-persistent) | মেথড | ডেটাবেস থেকে লোড হয়ে একটি অবজেক্ট persistent হলে। |
| [`pending_to_persistent()`](#sessionevents-pending-to-persistent) | মেথড | নতুন (pending) অবজেক্ট flush হয়ে persistent হলে (এখন primary key আছে)। |
| [`pending_to_transient()`](#sessionevents-pending-to-transient) | মেথড | pending অবজেক্ট rollback বা `expunge()`-এ আবার transient হলে। |
| [`persistent_to_deleted()`](#sessionevents-persistent-to-deleted) | মেথড | persistent অবজেক্টের DELETE flush হলে। |
| [`persistent_to_detached()`](#sessionevents-persistent-to-detached) | মেথড | persistent অবজেক্ট session থেকে বিচ্ছিন্ন হলে (`expunge()`, `close()`)। |
| [`persistent_to_transient()`](#sessionevents-persistent-to-transient) | মেথড | persistent অবজেক্ট transient হলে (যেমন INSERT-এর পরে rollback, বা `make_transient()`)। |
| [`transient_to_pending()`](#sessionevents-transient-to-pending) | মেথড | নতুন অবজেক্ট `add()` হয়ে pending হলে। |

### `SessionEvents.after_attach()` { #sessionevents-after-attach }

```python
SessionEvents.after_attach(session, instance)
```

**ধরন:** মেথড

একটি অবজেক্ট session-এ যুক্ত হওয়ার পরে (`add()`, cascade, `merge()`)।

**উদাহরণ:**

```python
on(session, "after_attach", lambda s, obj: calls.append(type(obj).__name__))
session.add(User(name="ক", addresses=[Address(city="খুলনা")]))
print(calls)   # ['User', 'Address']  (cascade-এ ঠিকানাও)
```

### `SessionEvents.after_begin()` { #sessionevents-after-begin }

```python
SessionEvents.after_begin(session, transaction, connection)
```

**ধরন:** মেথড

session একটি কানেকশনে ট্রানজ্যাকশন শুরু করার পরে (প্রতি কানেকশনে একবার)। কানেকশন-স্তরে কিছু সেট করতে (যেমন `SET LOCAL`)।

**উদাহরণ:**

```python
@on(session, "after_begin")
def set_local(sess, transaction, connection):
    connection.exec_driver_sql("SET LOCAL statement_timeout = '5s'")
    calls.append("BEGIN")
print(session.scalar(text("SHOW statement_timeout")), calls)   # 5s ['BEGIN']
```

### `SessionEvents.after_bulk_delete()` { #sessionevents-after-bulk-delete }

```python
SessionEvents.after_bulk_delete(delete_context)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো `Query.delete()`-এর পরে। ২.০-স্টাইলে `session.execute(delete(...))`-এর জন্য `do_orm_execute` ব্যবহার করুন।

**উদাহরণ:**

```python
on(session, "after_bulk_delete", lambda ctx: calls.append(ctx.result.rowcount))
session.query(Address).filter(Address.city == "ঢাকা").delete()
print(calls)   # [1]
```

### `SessionEvents.after_bulk_update()` { #sessionevents-after-bulk-update }

```python
SessionEvents.after_bulk_update(update_context)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো `Query.update()`-এর পরে।

**উদাহরণ:**

```python
on(session, "after_bulk_update", lambda ctx: calls.append(ctx.result.rowcount))
session.query(User).filter(User.id == 1).update({"name": "রহিম উদ্দিন"})
print(calls)   # [1]
```

### `SessionEvents.after_commit()` { #sessionevents-after-commit }

```python
SessionEvents.after_commit(session)
```

**ধরন:** মেথড

commit সফল হওয়ার পরে। এখানে ডেটাবেসে কিছু লেখা যাবে না (ট্রানজ্যাকশন শেষ); বাইরের কাজের জন্য (ইমেইল পাঠানো, ক্যাশ মোছা, মেসেজ-কিউ)।

**উদাহরণ:**

```python
on(session, "after_commit", lambda s: calls.append("ইমেইল পাঠাও"))
session.add(User(name="নতুন")); session.commit()
print(calls)   # ['ইমেইল পাঠাও']
```

### `SessionEvents.after_flush()` { #sessionevents-after-flush }

```python
SessionEvents.after_flush(session, flush_context)
```

**ধরন:** মেথড

flush শেষ হলে, কিন্তু session-এর অবস্থা (`new`, `dirty`, `deleted`) তখনো আগের মতো; কী কী সেভ হলো দেখার জায়গা (অডিট)।

**উদাহরণ:**

```python
@on(session, "after_flush")
def audit(sess, ctx):
    calls.extend(f"নতুন {type(o).__name__}" for o in sess.new)
session.add(User(name="ক")); session.flush()
print(calls)   # ['নতুন User']
```

### `SessionEvents.after_flush_postexec()` { #sessionevents-after-flush-postexec }

```python
SessionEvents.after_flush_postexec(session, flush_context)
```

**ধরন:** মেথড

flush-এর পরে session-এর অবস্থা হালনাগাদ হয়ে যাওয়ার পর (তখন `session.new` খালি)।

**উদাহরণ:**

```python
on(session, "after_flush_postexec", lambda s, ctx: calls.append(len(s.new)))
session.add(User(name="ক")); session.flush()
print(calls)   # [0]
```

### `SessionEvents.after_rollback()` { #sessionevents-after-rollback }

```python
SessionEvents.after_rollback(session)
```

**ধরন:** মেথড

আসল ডেটাবেস rollback হওয়ার পরে।

**উদাহরণ:**

```python
on(session, "after_rollback", lambda s: calls.append("rollback"))
session.add(User(name="ক")); session.flush(); session.rollback()
print(calls)   # ['rollback']
```

### `SessionEvents.after_soft_rollback()` { #sessionevents-after-soft-rollback }

```python
SessionEvents.after_soft_rollback(session, previous_transaction)
```

**ধরন:** মেথড

যেকোনো rollback-এর পরে (nested বা "soft" rollback-সহ, যেখানে ডেটাবেসে কিছু নাও যেতে পারে)।

**উদাহরণ:**

```python
on(session, "after_soft_rollback", lambda s, prev: calls.append(prev.nested))
session.begin_nested(); session.rollback()
print(calls)   # [True, False]  (session.rollback() ভেতরের SAVEPOINT থেকে মূল পর্যন্ত সব rollback করে)
```

### `SessionEvents.after_transaction_create()` { #sessionevents-after-transaction-create }

```python
SessionEvents.after_transaction_create(session, transaction)
```

**ধরন:** মেথড

একটি নতুন `SessionTransaction` (মূল বা nested) তৈরি হলে।

**উদাহরণ:**

```python
on(session, "after_transaction_create", lambda s, tx: calls.append("nested" if tx.nested else "root"))
session.scalar(select(User.id).limit(1)); session.begin_nested()
print(calls)   # ['root', 'nested']
```

### `SessionEvents.after_transaction_end()` { #sessionevents-after-transaction-end }

```python
SessionEvents.after_transaction_end(session, transaction)
```

**ধরন:** মেথড

একটি `SessionTransaction` শেষ হলে (commit/rollback/close)।

**উদাহরণ:**

```python
on(session, "after_transaction_end", lambda s, tx: calls.append("শেষ"))
session.scalar(select(User.id).limit(1)); session.commit()
print(calls)   # ['শেষ']
```

### `SessionEvents.before_attach()` { #sessionevents-before-attach }

```python
SessionEvents.before_attach(session, instance)
```

**ধরন:** মেথড

অবজেক্ট session-এ যুক্ত হওয়ার আগে।

**উদাহরণ:**

```python
on(session, "before_attach", lambda s, obj: calls.append(obj.name))
session.add(User(name="সুমি"))
print(calls)   # ['সুমি']
```

### `SessionEvents.before_commit()` { #sessionevents-before-commit }

```python
SessionEvents.before_commit(session)
```

**ধরন:** মেথড

commit-এর আগে (flush তখনো বাকি থাকতে পারে); শেষ মুহূর্তের যাচাই।

**উদাহরণ:**

```python
on(session, "before_commit", lambda s: calls.append(len(s.new)))
session.add(User(name="ক")); session.commit()
print(calls)   # [1]  (এখনো flush হয়নি)
```

### `SessionEvents.before_flush()` { #sessionevents-before-flush }

```python
SessionEvents.before_flush(session, flush_context, instances)
```

**ধরন:** মেথড

flush শুরুর আগে: **অবজেক্ট বদলানো, নতুন অবজেক্ট যোগ, যাচাই করার সঠিক জায়গা** (`session.new`, `session.dirty`, `session.deleted` দেখে)। এখানে যা বদলাবেন তা একই flush-এ সেভ হবে।

**উদাহরণ:**

```python
@on(session, "before_flush")
def make_slug(sess, ctx, instances):
    for obj in sess.new | sess.dirty:
        if isinstance(obj, User):
            obj.slug = obj.name.strip().lower().replace(" ", "-")
u = User(name="Abdul Karim"); session.add(u); session.flush()
print(u.slug)   # abdul-karim
```

### `SessionEvents.deleted_to_detached()` { #sessionevents-deleted-to-detached }

```python
SessionEvents.deleted_to_detached(session, instance)
```

**ধরন:** মেথড

মোছা অবজেক্ট commit-এর পরে session থেকে বিচ্ছিন্ন হলে।

**উদাহরণ:**

```python
on(session, "deleted_to_detached", lambda s, obj: calls.append(type(obj).__name__))
a = session.get(Address, 1)          # রেফারেন্স রাখুন; নইলে অবজেক্ট garbage-collect হয়ে event আসে না
session.delete(a); session.commit()
print(calls)   # ['Address']
```

### `SessionEvents.deleted_to_persistent()` { #sessionevents-deleted-to-persistent }

```python
SessionEvents.deleted_to_persistent(session, instance)
```

**ধরন:** মেথড

মোছা (flush হওয়া) অবজেক্ট rollback-এ আবার persistent হলে।

**উদাহরণ:**

```python
on(session, "deleted_to_persistent", lambda s, obj: calls.append(obj.city))
a = session.get(Address, 1)
session.delete(a); session.flush(); session.rollback()
print(calls)   # ['ঢাকা']
```

### `SessionEvents.detached_to_persistent()` { #sessionevents-detached-to-persistent }

```python
SessionEvents.detached_to_persistent(session, instance)
```

**ধরন:** মেথড

detached অবজেক্ট আবার session-এ যুক্ত হলে (`add()`)।

**উদাহরণ:**

```python
with Session(engine) as s1:
    u = s1.get(User, 1)
on(session, "detached_to_persistent", lambda s, obj: calls.append(obj.id))
session.add(u)
print(calls)   # [1]
```

### `SessionEvents.do_orm_execute()` { #sessionevents-do-orm-execute }

```python
SessionEvents.do_orm_execute(orm_execute_state)
```

**ধরন:** মেথড

session-এর প্রতিটি ORM স্টেটমেন্ট চালানোর আগে (`execute()`, `scalars()`, lazy load, `get()` …)। `ORMExecuteState` দিয়ে স্টেটমেন্ট দেখা/বদলানো যায় (`is_select`, `statement`, `update_execution_options()`)। **সব কুয়েরিতে soft-delete/tenant ফিল্টার বসানোর সেরা জায়গা**; নিজে ফল ফেরত দিয়ে ক্যাশিংও করা যায়।

**উদাহরণ:**

```python
@on(session, "do_orm_execute")
def hide_khulna(state):
    if state.is_select:
        state.statement = state.statement.options(
            with_loader_criteria(Address, Address.city != "খুলনা", include_aliases=True))
session.add(Address(city="খুলনা", user_id=1)); session.flush()
print(session.scalars(select(Address.city)).all())   # ['ঢাকা']
```

### `SessionEvents.loaded_as_persistent()` { #sessionevents-loaded-as-persistent }

```python
SessionEvents.loaded_as_persistent(session, instance)
```

**ধরন:** মেথড

ডেটাবেস থেকে লোড হয়ে একটি অবজেক্ট persistent হলে।

**উদাহরণ:**

```python
on(session, "loaded_as_persistent", lambda s, obj: calls.append(type(obj).__name__))
session.get(User, 1)
print(calls)   # ['User']
```

### `SessionEvents.pending_to_persistent()` { #sessionevents-pending-to-persistent }

```python
SessionEvents.pending_to_persistent(session, instance)
```

**ধরন:** মেথড

নতুন (pending) অবজেক্ট flush হয়ে persistent হলে (এখন primary key আছে)।

**উদাহরণ:**

```python
on(session, "pending_to_persistent", lambda s, obj: calls.append(obj.id is not None))
session.add(User(name="ক")); session.flush()
print(calls)   # [True]
```

### `SessionEvents.pending_to_transient()` { #sessionevents-pending-to-transient }

```python
SessionEvents.pending_to_transient(session, instance)
```

**ধরন:** মেথড

pending অবজেক্ট rollback বা `expunge()`-এ আবার transient হলে।

**উদাহরণ:**

```python
on(session, "pending_to_transient", lambda s, obj: calls.append(obj.name))
u = User(name="ক"); session.add(u); session.expunge(u)
print(calls)   # ['ক']
```

### `SessionEvents.persistent_to_deleted()` { #sessionevents-persistent-to-deleted }

```python
SessionEvents.persistent_to_deleted(session, instance)
```

**ধরন:** মেথড

persistent অবজেক্টের DELETE flush হলে।

**উদাহরণ:**

```python
on(session, "persistent_to_deleted", lambda s, obj: calls.append(obj.city))
session.delete(session.get(Address, 1)); session.flush()
print(calls)   # ['ঢাকা']
```

### `SessionEvents.persistent_to_detached()` { #sessionevents-persistent-to-detached }

```python
SessionEvents.persistent_to_detached(session, instance)
```

**ধরন:** মেথড

persistent অবজেক্ট session থেকে বিচ্ছিন্ন হলে (`expunge()`, `close()`)।

**উদাহরণ:**

```python
on(session, "persistent_to_detached", lambda s, obj: calls.append(type(obj).__name__))
u = session.get(User, 1)              # শক্ত রেফারেন্স ছাড়া (weak identity map) event আসে না
session.close()
print(calls)   # ['User']
```

### `SessionEvents.persistent_to_transient()` { #sessionevents-persistent-to-transient }

```python
SessionEvents.persistent_to_transient(session, instance)
```

**ধরন:** মেথড

persistent অবজেক্ট transient হলে (যেমন INSERT-এর পরে rollback, বা `make_transient()`)।

**উদাহরণ:**

```python
on(session, "persistent_to_transient", lambda s, obj: calls.append(obj.name))
u = User(name="ক"); session.add(u); session.flush(); session.rollback()
print(calls)   # ['ক']
```

### `SessionEvents.transient_to_pending()` { #sessionevents-transient-to-pending }

```python
SessionEvents.transient_to_pending(session, instance)
```

**ধরন:** মেথড

নতুন অবজেক্ট `add()` হয়ে pending হলে।

**উদাহরণ:**

```python
on(session, "transient_to_pending", lambda s, obj: calls.append(obj.name))
session.add(User(name="খ"))
print(calls)   # ['খ']
```

## `MapperEvents` { #mapperevents }

```python
from sqlalchemy.orm import MapperEvents
```

একটি মডেল-ক্লাসের (mapper-এর) event: প্রতিটি অবজেক্টের INSERT/UPDATE/DELETE-এর আগে-পরে, আর mapper configure হওয়ার ধাপগুলো। টার্গেট: মডেল ক্লাস (`User`), `Mapper`, বা বেস ক্লাস (`propagate=True` দিলে সব সাবক্লাসে)।

**উদাহরণ:**

```python
@on(User, "before_insert")
def default_slug(mapper, connection, target):
    target.slug = target.slug or target.name.lower()
u = User(name="Sumi"); session.add(u); session.flush()
print(u.slug)   # sumi
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mapperevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`after_configured()`](#mapperevents-after-configured) | মেথড | `configure_mappers()` শেষে একবার (সব mapper তৈরি)। |
| [`after_delete()`](#mapperevents-after-delete) | মেথড | অবজেক্টের DELETE চলার পরে। |
| [`after_insert()`](#mapperevents-after-insert) | মেথড | INSERT-এর পরে (primary key তখন জানা)। |
| [`after_mapper_constructed()`](#mapperevents-after-mapper-constructed) | মেথড | (২.০.২) একটি mapper তৈরি হওয়ার পরপরই (configure-এর আগে)। |
| [`after_update()`](#mapperevents-after-update) | মেথড | UPDATE-এর পরে (শুধু যেসব অবজেক্টে কলাম আসলেই বদলেছে)। |
| [`before_configured()`](#mapperevents-before-configured) | মেথড | `configure_mappers()` শুরুর আগে একবার (`after_configured`-এর মতোই: `Mapper`-এ আর্গুমেন্ট নেই, Base-এ ২.১-এ `registry`)। |
| [`before_delete()`](#mapperevents-before-delete) | মেথড | DELETE-এর আগে (যেমন মোছা নিষেধ করতে exception raise)। |
| [`before_insert()`](#mapperevents-before-insert) | মেথড | INSERT-এর আগে: নিজের অবজেক্টের কলামে মান বসানো যায়। |
| [`before_mapper_configured()`](#mapperevents-before-mapper-configured) | মেথড | একটি নির্দিষ্ট mapper configure হওয়ার ঠিক আগে (`EXT_SKIP` ফেরত দিলে সেটি বাদ যায়)। |
| [`before_update()`](#mapperevents-before-update) | মেথড | UPDATE-এর আগে: যেমন `updated_by` বসানো, বা যাচাই। |
| [`instrument_class()`](#mapperevents-instrument-class) | মেথড | ক্লাসটির mapper প্রথম তৈরি হওয়ার মুহূর্তে, অ্যাট্রিবিউট instrument হওয়ার আগে। |
| [`mapper_configured()`](#mapperevents-mapper-configured) | মেথড | একটি mapper-এর configure শেষ হলে (রিলেশনশিপ এখন প্রস্তুত); ক্লাস-ভিত্তিক সেটআপের জায়গা। |

### `MapperEvents.after_configured()` { #mapperevents-after-configured }

```python
MapperEvents.after_configured()
```

**ধরন:** মেথড

`configure_mappers()` শেষে একবার (সব mapper তৈরি)। টার্গেট `Mapper` ক্লাস (listener-এ কোনো আর্গুমেন্ট নেই) বা declarative Base / `registry` (**২.১-এ** listener একটি আর্গুমেন্ট পায়: সেই `registry`)।

**উদাহরণ:**

```python
class B2(DeclarativeBase): pass
on(B2, "after_configured", lambda reg: calls.append(type(reg).__name__))
class T(B2):
    __tablename__ = "t_cfg"
    id: Mapped[int] = mapped_column(primary_key=True)
configure_mappers()
print(calls)   # ['registry']
```

### `MapperEvents.after_delete()` { #mapperevents-after-delete }

```python
MapperEvents.after_delete(mapper, connection, target)
```

**ধরন:** মেথড

অবজেক্টের DELETE চলার পরে।

**উদাহরণ:**

```python
on(Address, "after_delete", lambda m, conn, t: calls.append(t.id))
session.delete(session.get(Address, 1)); session.flush()
print(calls)   # [1]
```

### `MapperEvents.after_insert()` { #mapperevents-after-insert }

```python
MapperEvents.after_insert(mapper, connection, target)
```

**ধরন:** মেথড

INSERT-এর পরে (primary key তখন জানা)। একই কানেকশনে অন্য টেবিলে লেখা যায় (`connection.execute(...)`), যেমন অডিট টেবিলে।

**উদাহরণ:**

```python
on(User, "after_insert", lambda m, conn, t: calls.append(t.id))
session.add(User(id=50, name="ক")); session.flush()
print(calls)   # [50]
```

### `MapperEvents.after_mapper_constructed()` { #mapperevents-after-mapper-constructed }

```python
MapperEvents.after_mapper_constructed(mapper, class_)
```

**ধরন:** মেথড

(২.০.২) একটি mapper তৈরি হওয়ার পরপরই (configure-এর আগে)।

**উদাহরণ:**

```python
class B3(DeclarativeBase): pass
on(B3, "after_mapper_constructed", lambda m, cls: calls.append(cls.__name__), propagate=True)
class Item(B3):
    __tablename__ = "items_mc"
    id: Mapped[int] = mapped_column(primary_key=True)
print(calls)   # ['Item']
```

### `MapperEvents.after_update()` { #mapperevents-after-update }

```python
MapperEvents.after_update(mapper, connection, target)
```

**ধরন:** মেথড

UPDATE-এর পরে (শুধু যেসব অবজেক্টে কলাম আসলেই বদলেছে)।

**উদাহরণ:**

```python
on(User, "after_update", lambda m, conn, t: calls.append(t.name))
u = session.get(User, 1); u.name = "রহিম ভাই"; session.flush()
print(calls)   # ['রহিম ভাই']
```

### `MapperEvents.before_configured()` { #mapperevents-before-configured }

```python
MapperEvents.before_configured()
```

**ধরন:** মেথড

`configure_mappers()` শুরুর আগে একবার (`after_configured`-এর মতোই: `Mapper`-এ আর্গুমেন্ট নেই, Base-এ ২.১-এ `registry`)।

**উদাহরণ:**

```python
class B4(DeclarativeBase): pass
on(B4, "before_configured", lambda reg: calls.append("শুরু"))
class T4(B4):
    __tablename__ = "t4"
    id: Mapped[int] = mapped_column(primary_key=True)
configure_mappers()
print(calls)   # ['শুরু']
```

### `MapperEvents.before_delete()` { #mapperevents-before-delete }

```python
MapperEvents.before_delete(mapper, connection, target)
```

**ধরন:** মেথড

DELETE-এর আগে (যেমন মোছা নিষেধ করতে exception raise)।

**উদাহরণ:**

```python
@on(User, "before_delete")
def protect(m, conn, target):
    if target.id == 1:
        raise ValueError("এই ইউজার মোছা যাবে না")
session.delete(session.get(User, 1))
try:
    session.flush()
except ValueError as e:
    print(e)   # এই ইউজার মোছা যাবে না
```

### `MapperEvents.before_insert()` { #mapperevents-before-insert }

```python
MapperEvents.before_insert(mapper, connection, target)
```

**ধরন:** মেথড

INSERT-এর আগে: নিজের অবজেক্টের কলামে মান বসানো যায়।

**উদাহরণ:**

```python
on(User, "before_insert", lambda m, conn, t: setattr(t, "name", t.name.strip()))
u = User(name="  ফাঁকা  "); session.add(u); session.flush()
print(repr(u.name))   # 'ফাঁকা'
```

### `MapperEvents.before_mapper_configured()` { #mapperevents-before-mapper-configured }

```python
MapperEvents.before_mapper_configured(mapper, class_)
```

**ধরন:** মেথড

একটি নির্দিষ্ট mapper configure হওয়ার ঠিক আগে (`EXT_SKIP` ফেরত দিলে সেটি বাদ যায়)।

**উদাহরণ:**

```python
class B5(DeclarativeBase): pass
on(B5, "before_mapper_configured", lambda m, cls: calls.append(cls.__name__), propagate=True)
class T5(B5):
    __tablename__ = "t5"
    id: Mapped[int] = mapped_column(primary_key=True)
configure_mappers()
print(calls)   # ['T5']
```

### `MapperEvents.before_update()` { #mapperevents-before-update }

```python
MapperEvents.before_update(mapper, connection, target)
```

**ধরন:** মেথড

UPDATE-এর আগে: যেমন `updated_by` বসানো, বা যাচাই।

**উদাহরণ:**

```python
on(User, "before_update", lambda m, conn, t: setattr(t, "slug", "updated"))
u = session.get(User, 1); u.name = "নতুন"; session.flush()
print(u.slug)   # updated
```

### `MapperEvents.instrument_class()` { #mapperevents-instrument-class }

```python
MapperEvents.instrument_class(mapper, class_)
```

**ধরন:** মেথড

ক্লাসটির mapper প্রথম তৈরি হওয়ার মুহূর্তে, অ্যাট্রিবিউট instrument হওয়ার আগে।

**উদাহরণ:**

```python
class B6(DeclarativeBase): pass
on(B6, "instrument_class", lambda m, cls: calls.append(cls.__name__), propagate=True)
class T6(B6):
    __tablename__ = "t6"
    id: Mapped[int] = mapped_column(primary_key=True)
print(calls)   # ['T6']
```

### `MapperEvents.mapper_configured()` { #mapperevents-mapper-configured }

```python
MapperEvents.mapper_configured(mapper, class_)
```

**ধরন:** মেথড

একটি mapper-এর configure শেষ হলে (রিলেশনশিপ এখন প্রস্তুত); ক্লাস-ভিত্তিক সেটআপের জায়গা।

**উদাহরণ:**

```python
class B7(DeclarativeBase): pass
on(B7, "mapper_configured", lambda m, cls: calls.append(list(m.relationships.keys())), propagate=True)
class P(B7):
    __tablename__ = "p7"
    id: Mapped[int] = mapped_column(primary_key=True)
    kids: Mapped[list["K"]] = relationship()
class K(B7):
    __tablename__ = "k7"
    id: Mapped[int] = mapped_column(primary_key=True)
    p_id: Mapped[int] = mapped_column(ForeignKey("p7.id"))
configure_mappers()
print(sorted(map(str, calls)))   # ["['kids']", '[]']
```

## `InstanceEvents` { #instanceevents }

```python
from sqlalchemy.orm import InstanceEvents
```

একটি মডেলের **অবজেক্টের** জীবনচক্রের event: তৈরি (`__init__`), ডেটাবেস থেকে লোড, refresh, expire, pickle। টার্গেট: মডেল ক্লাস (বা বেস + `propagate=True`)।

**উদাহরণ:**

```python
on(User, "load", lambda target, ctx: calls.append(f"লোড: {target.name}"))
session.get(User, 1)
print(calls)   # ['লোড: রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #instanceevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`expire()`](#instanceevents-expire) | মেথড | অবজেক্টের (বা কিছু) অ্যাট্রিবিউট expire হলে (`commit()`, `expire()`)। |
| [`init()`](#instanceevents-init) | মেথড | অবজেক্টের কনস্ট্রাক্টর ডাকা হলে (`User(...)`), আসল `__init__`-এর আগে; kwargs দেখা/বদলানো যায় (ডিফল্ট বসানো)। |
| [`init_failure()`](#instanceevents-init-failure) | মেথড | কনস্ট্রাক্টর exception দিলে। |
| [`load()`](#instanceevents-load) | মেথড | ডেটাবেস থেকে অবজেক্ট তৈরি হয়ে প্রাথমিক অ্যাট্রিবিউট ভরার পর (`__init__` ডাকা হয় না, তাই "লোডের পর সেটআপ"-এর জায়গা; `@reconstructor`-এর মতো)। |
| [`pickle()`](#instanceevents-pickle) | মেথড | অবজেক্ট pickle হওয়ার সময়। |
| [`refresh()`](#instanceevents-refresh) | মেথড | কুয়েরির মাধ্যমে অবজেক্টের অ্যাট্রিবিউট আবার লোড (refresh) হলে। |
| [`refresh_flush()`](#instanceevents-refresh-flush) | মেথড | flush-এর সময় ডেটাবেস-তৈরি মান (server default, `onupdate`, RETURNING) অবজেক্টে বসলে। |
| [`unpickle()`](#instanceevents-unpickle) | মেথড | অবজেক্ট unpickle হওয়ার পরে। |

### `InstanceEvents.expire()` { #instanceevents-expire }

```python
InstanceEvents.expire(target, attrs)
```

**ধরন:** মেথড

অবজেক্টের (বা কিছু) অ্যাট্রিবিউট expire হলে (`commit()`, `expire()`)।

**উদাহরণ:**

```python
on(User, "expire", lambda target, attrs: calls.append(attrs))
u = session.get(User, 1); session.expire(u, ["name"])
print(calls)   # [['name']]
```

### `InstanceEvents.init()` { #instanceevents-init }

```python
InstanceEvents.init(target, args, kwargs)
```

**ধরন:** মেথড

অবজেক্টের কনস্ট্রাক্টর ডাকা হলে (`User(...)`), আসল `__init__`-এর আগে; kwargs দেখা/বদলানো যায় (ডিফল্ট বসানো)।

**উদাহরণ:**

```python
@on(User, "init")
def defaults(target, args, kwargs):
    kwargs.setdefault("slug", "auto")
print(User(name="ক").slug)   # auto
```

### `InstanceEvents.init_failure()` { #instanceevents-init-failure }

```python
InstanceEvents.init_failure(target, args, kwargs)
```

**ধরন:** মেথড

কনস্ট্রাক্টর exception দিলে।

**উদাহরণ:**

```python
on(User, "init_failure", lambda target, args, kwargs: calls.append("ব্যর্থ"))
try:
    User(nonexistent="x")
except TypeError:
    pass
print(calls)   # ['ব্যর্থ']
```

### `InstanceEvents.load()` { #instanceevents-load }

```python
InstanceEvents.load(target, context)
```

**ধরন:** মেথড

ডেটাবেস থেকে অবজেক্ট তৈরি হয়ে প্রাথমিক অ্যাট্রিবিউট ভরার পর (`__init__` ডাকা হয় না, তাই "লোডের পর সেটআপ"-এর জায়গা; `@reconstructor`-এর মতো)।

**উদাহরণ:**

```python
on(User, "load", lambda target, ctx: setattr(target, "_cache", {}))
print(hasattr(session.get(User, 1), "_cache"))   # True
```

### `InstanceEvents.pickle()` { #instanceevents-pickle }

```python
InstanceEvents.pickle(target, state_dict)
```

**ধরন:** মেথড

অবজেক্ট pickle হওয়ার সময়।

**উদাহরণ:**

```python
on(User, "pickle", lambda target, state: calls.append("pickle"))
pickle.dumps(session.get(User, 1))
print(calls)   # ['pickle']
```

### `InstanceEvents.refresh()` { #instanceevents-refresh }

```python
InstanceEvents.refresh(target, context, attrs)
```

**ধরন:** মেথড

কুয়েরির মাধ্যমে অবজেক্টের অ্যাট্রিবিউট আবার লোড (refresh) হলে।

**উদাহরণ:**

```python
on(User, "refresh", lambda target, ctx, attrs: calls.append(sorted(attrs) if attrs else "সব"))
u = session.get(User, 1); session.refresh(u, ["name"])
print(calls)   # [['name']]
```

### `InstanceEvents.refresh_flush()` { #instanceevents-refresh-flush }

```python
InstanceEvents.refresh_flush(target, flush_context, attrs)
```

**ধরন:** মেথড

flush-এর সময় ডেটাবেস-তৈরি মান (server default, `onupdate`, RETURNING) অবজেক্টে বসলে।

**উদাহরণ:**

```python
class B12(DeclarativeBase): pass
class Doc(B12):
    __tablename__ = "docs_rf"
    id: Mapped[int] = mapped_column(primary_key=True)
    created: Mapped[datetime] = mapped_column(server_default=func.now())
B12.metadata.create_all(engine)
on(Doc, "refresh_flush", lambda target, ctx, attrs: calls.append(sorted(attrs)))
session.add(Doc()); session.flush()
print(calls)   # [['created']]  (INSERT ... RETURNING দিয়ে server default ফেরত এল)
```

### `InstanceEvents.unpickle()` { #instanceevents-unpickle }

```python
InstanceEvents.unpickle(target, state_dict)
```

**ধরন:** মেথড

অবজেক্ট unpickle হওয়ার পরে।

**উদাহরণ:**

```python
on(User, "unpickle", lambda target, state: calls.append("unpickle"))
pickle.loads(pickle.dumps(session.get(User, 1)))
print(calls)   # ['unpickle']
```

## `AttributeEvents` { #attributeevents }

```python
from sqlalchemy.orm import AttributeEvents
```

একটি নির্দিষ্ট অ্যাট্রিবিউটের event: মান সেট, কালেকশনে যোগ/বাদ। টার্গেট: অ্যাট্রিবিউট (`User.name`, `User.addresses`)। `retval=True` দিয়ে বসালে `set`/`append`-এর ফেরত মানটিই আসলে বসে (normalize করতে)। `active_history=True` দিলে পুরোনো মান লোড করে দেয়।

**উদাহরণ:**

```python
on(User.name, "set", lambda target, value, old, initiator: value.strip().title(), retval=True)
u = User(name="  karim  ")
print(u.name)   # Karim
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #attributeevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append()`](#attributeevents-append) | মেথড | কালেকশনে একটি উপাদান যোগ হলে (`user.addresses.append(a)`)। |
| [`append_wo_mutation()`](#attributeevents-append-wo-mutation) | মেথড | (১.৪.১৫) যোগ করার চেষ্টা হলো কিন্তু উপাদানটি আগে থেকেই ছিল, তাই কালেকশন আসলে বদলায়নি। |
| [`bulk_replace()`](#attributeevents-bulk-replace) | মেথড | পুরো কালেকশন একসাথে বদলালে (`user.addresses = [...]`), আলাদা append/remove event-এর আগে। |
| [`dispose_collection()`](#attributeevents-dispose-collection) | মেথড | একটি কালেকশন অবজেক্ট বাতিল হলে (পুরো কালেকশন বদলে দেওয়ায় পুরোনোটি)। |
| [`init_collection()`](#attributeevents-init-collection) | মেথড | একটি খালি কালেকশন প্রথম তৈরি হলে (নতুন অবজেক্টে প্রথমবার `user.addresses` পড়লে)। |
| [`init_scalar()`](#attributeevents-init-scalar) | মেথড | মান না থাকা (নতুন অবজেক্টের) স্কেলার অ্যাট্রিবিউট প্রথমবার পড়ার সময়: ডিফল্ট মান দেখানোর কৌশল (`dict_`-এ বসালে সেটিই থাকে)। |
| [`modified()`](#attributeevents-modified) | মেথড | `attributes.flag_modified()` দিয়ে অ্যাট্রিবিউট "বদলেছে" চিহ্নিত করা হলে (যেমন JSON-এর ভেতরে বদলের পর)। |
| [`remove()`](#attributeevents-remove) | মেথড | কালেকশন থেকে উপাদান বাদ গেলে। |
| [`set()`](#attributeevents-set) | মেথড | স্কেলার অ্যাট্রিবিউটে মান বসলে (`user.name = ...`), নতুন ও পুরোনো মানসহ। |

### `AttributeEvents.append()` { #attributeevents-append }

```python
AttributeEvents.append(target, value, initiator, *, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

কালেকশনে একটি উপাদান যোগ হলে (`user.addresses.append(a)`)। `retval=True` দিয়ে উপাদান বদলানো যায়।

**উদাহরণ:**

```python
on(User.addresses, "append", lambda target, value, initiator: calls.append(value.city))
u = session.get(User, 1); u.addresses.append(Address(city="রাজশাহী"))
print(calls)   # ['রাজশাহী']
```

### `AttributeEvents.append_wo_mutation()` { #attributeevents-append-wo-mutation }

```python
AttributeEvents.append_wo_mutation(target, value, initiator, *, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

(১.৪.১৫) যোগ করার চেষ্টা হলো কিন্তু উপাদানটি আগে থেকেই ছিল, তাই কালেকশন আসলে বদলায়নি। শুধু ডুপ্লিকেট-বাদ-দেওয়া কালেকশনে (`set`, dict) আসে।

**উদাহরণ:**

```python
class B13(DeclarativeBase): pass
class Post(B13):
    __tablename__ = "posts_awm"
    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[set["Tag"]] = relationship()
class Tag(B13):
    __tablename__ = "tags_awm"
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts_awm.id"))
on(Post.tags, "append_wo_mutation", lambda target, value, initiator: calls.append("আগেই ছিল"))
p, t = Post(), Tag()
p.tags.add(t); p.tags.add(t)
print(calls)   # ['আগেই ছিল']
```

### `AttributeEvents.bulk_replace()` { #attributeevents-bulk-replace }

```python
AttributeEvents.bulk_replace(target, values, initiator, *, keys=None)
```

**ধরন:** মেথড

পুরো কালেকশন একসাথে বদলালে (`user.addresses = [...]`), আলাদা append/remove event-এর আগে।

**উদাহরণ:**

```python
on(User.addresses, "bulk_replace", lambda target, values, initiator, **kw: calls.append(len(values)))
u = session.get(User, 1); u.addresses = [Address(city="ক"), Address(city="খ")]
print(calls)   # [2]
```

### `AttributeEvents.dispose_collection()` { #attributeevents-dispose-collection }

```python
AttributeEvents.dispose_collection(target, collection, collection_adapter)
```

**ধরন:** মেথড

একটি কালেকশন অবজেক্ট বাতিল হলে (পুরো কালেকশন বদলে দেওয়ায় পুরোনোটি)।

**উদাহরণ:**

```python
on(User.addresses, "dispose_collection", lambda target, coll, adapter: calls.append(len(coll)))
u = session.get(User, 1); u.addresses = []
print(calls)   # [1]
```

### `AttributeEvents.init_collection()` { #attributeevents-init-collection }

```python
AttributeEvents.init_collection(target, collection, collection_adapter)
```

**ধরন:** মেথড

একটি খালি কালেকশন প্রথম তৈরি হলে (নতুন অবজেক্টে প্রথমবার `user.addresses` পড়লে)।

**উদাহরণ:**

```python
on(User.addresses, "init_collection", lambda target, coll, adapter: calls.append(type(coll).__name__))
User(name="ক").addresses
print(calls)   # ['InstrumentedList']
```

### `AttributeEvents.init_scalar()` { #attributeevents-init-scalar }

```python
AttributeEvents.init_scalar(target, value, dict_)
```

**ধরন:** মেথড

মান না থাকা (নতুন অবজেক্টের) স্কেলার অ্যাট্রিবিউট প্রথমবার পড়ার সময়: ডিফল্ট মান দেখানোর কৌশল (`dict_`-এ বসালে সেটিই থাকে)।

**উদাহরণ:**

```python
@on(User.slug, "init_scalar", retval=True)
def default_slug(target, value, dict_):
    dict_["slug"] = "নতুন"
    return "নতুন"
print(User(name="ক").slug)   # নতুন
```

### `AttributeEvents.modified()` { #attributeevents-modified }

```python
AttributeEvents.modified(target, initiator)
```

**ধরন:** মেথড

`attributes.flag_modified()` দিয়ে অ্যাট্রিবিউট "বদলেছে" চিহ্নিত করা হলে (যেমন JSON-এর ভেতরে বদলের পর)।

**উদাহরণ:**

```python
on(User.name, "modified", lambda target, initiator: calls.append("modified"))
u = session.get(User, 1); attributes.flag_modified(u, "name")
print(calls)   # ['modified']
```

### `AttributeEvents.remove()` { #attributeevents-remove }

```python
AttributeEvents.remove(target, value, initiator, *, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

কালেকশন থেকে উপাদান বাদ গেলে।

**উদাহরণ:**

```python
on(User.addresses, "remove", lambda target, value, initiator: calls.append(value.city))
u = session.get(User, 1); u.addresses.remove(u.addresses[0])
print(calls)   # ['ঢাকা']
```

### `AttributeEvents.set()` { #attributeevents-set }

```python
AttributeEvents.set(target, value, oldvalue, initiator)
```

**ধরন:** মেথড

স্কেলার অ্যাট্রিবিউটে মান বসলে (`user.name = ...`), নতুন ও পুরোনো মানসহ। `retval=True` দিয়ে মান বদলানো যায়।

**উদাহরণ:**

```python
on(User.name, "set", lambda target, value, old, initiator: calls.append((old, value)), active_history=True)
u = session.get(User, 1); u.name = "নতুন নাম"
print(calls)   # [('রহিম', 'নতুন নাম')]
```

## `InstrumentationEvents` { #instrumentationevents }

```python
from sqlalchemy.orm import InstrumentationEvents
```

ক্লাস "instrument" (ORM-এর অ্যাট্রিবিউট-পর্যবেক্ষণ ব্যবস্থা বসানো) হওয়ার নিচু-স্তরের event। টার্গেট: একটি বেস ক্লাস; তার সাবক্লাসে প্রযোজ্য। extension লেখকদের জন্য; অ্যাপে প্রায় দরকার হয় না।

**উদাহরণ:**

```python
class B8(DeclarativeBase): pass
on(B8, "class_instrument", lambda cls: calls.append(cls.__name__))
class T8(B8):
    __tablename__ = "t8"
    id: Mapped[int] = mapped_column(primary_key=True)
print(calls)   # ['T8']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #instrumentationevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`attribute_instrument()`](#instrumentationevents-attribute-instrument) | মেথড | ক্লাসের একটি অ্যাট্রিবিউট পুরোপুরি instrument হলে (mapper configure হওয়ার সময়)। |
| [`class_instrument()`](#instrumentationevents-class-instrument) | মেথড | একটি ক্লাস instrument হওয়ার পরে। |
| [`class_uninstrument()`](#instrumentationevents-class-uninstrument) | মেথড | ক্লাস থেকে instrumentation সরানোর আগে (`clear_mappers()` / `registry.dispose()`)। |

### `InstrumentationEvents.attribute_instrument()` { #instrumentationevents-attribute-instrument }

```python
InstrumentationEvents.attribute_instrument(key, inst)
```

**ধরন:** মেথড

ক্লাসের একটি অ্যাট্রিবিউট পুরোপুরি instrument হলে (mapper configure হওয়ার সময়)।

**উদাহরণ:**

```python
class B9(DeclarativeBase): pass
on(B9, "attribute_instrument", lambda cls, key, inst: calls.append(key))
class T9(B9):
    __tablename__ = "t9"
    id: Mapped[int] = mapped_column(primary_key=True)
configure_mappers()                      # অ্যাট্রিবিউটগুলো configure হওয়ার সময় event আসে
print(calls)   # ['id']
```

### `InstrumentationEvents.class_instrument()` { #instrumentationevents-class-instrument }

```python
InstrumentationEvents.class_instrument()
```

**ধরন:** মেথড

একটি ক্লাস instrument হওয়ার পরে।

**উদাহরণ:**

```python
class B10(DeclarativeBase): pass
on(B10, "class_instrument", lambda cls: calls.append("instrumented"))
class T10(B10):
    __tablename__ = "t10"
    id: Mapped[int] = mapped_column(primary_key=True)
print(calls)   # ['instrumented']
```

### `InstrumentationEvents.class_uninstrument()` { #instrumentationevents-class-uninstrument }

```python
InstrumentationEvents.class_uninstrument()
```

**ধরন:** মেথড

ক্লাস থেকে instrumentation সরানোর আগে (`clear_mappers()` / `registry.dispose()`)।

**উদাহরণ:**

```python
from sqlalchemy.orm import registry
reg = registry()
class B11: pass
on(B11, "class_uninstrument", lambda cls: calls.append("uninstrument"))
@reg.mapped
class T11(B11):
    __tablename__ = "t11"
    id: Mapped[int] = mapped_column(primary_key=True)
reg.dispose()
print(calls)   # ['uninstrument']
```

## `QueryEvents` { #queryevents }

```python
from sqlalchemy.orm import QueryEvents
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো `Query` API-র event (`session.query(...)`)। ২.০-স্টাইলে (`select()` + `session.execute()`) এগুলো চলে না; তার বদলে `SessionEvents.do_orm_execute` ব্যবহার করুন।

**উদাহরণ:**

```python
from sqlalchemy.orm import Query

@on(Query, "before_compile", retval=True)
def only_rahim(query):
    for desc in query.column_descriptions:
        if desc["type"] is User:
            query = query.filter(User.name == "রহিম")
    return query
session.add(User(name="করিম")); session.flush()
print([u.name for u in session.query(User)])   # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #queryevents-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`before_compile()`](#queryevents-before-compile) | মেথড | `Query` থেকে SELECT বানানোর আগে; `retval=True` দিয়ে বদলানো Query ফেরত দেওয়া যায়। |
| [`before_compile_delete()`](#queryevents-before-compile-delete) | মেথড | `Query.delete()`-এর আগে। |
| [`before_compile_update()`](#queryevents-before-compile-update) | মেথড | `Query.update()`-এর আগে। |

### `QueryEvents.before_compile()` { #queryevents-before-compile }

```python
QueryEvents.before_compile(query)
```

**ধরন:** মেথড

`Query` থেকে SELECT বানানোর আগে; `retval=True` দিয়ে বদলানো Query ফেরত দেওয়া যায়।

**উদাহরণ:**

```python
from sqlalchemy.orm import Query
on(Query, "before_compile", lambda q: calls.append("compile"))
session.query(User).all()
print(calls)   # ['compile']
```

### `QueryEvents.before_compile_delete()` { #queryevents-before-compile-delete }

```python
QueryEvents.before_compile_delete(query, delete_context)
```

**ধরন:** মেথড

`Query.delete()`-এর আগে।

**উদাহরণ:**

```python
from sqlalchemy.orm import Query
on(Query, "before_compile_delete", lambda q, ctx: calls.append("delete"))
session.query(Address).filter(Address.id == 1).delete()
print(calls)   # ['delete']
```

### `QueryEvents.before_compile_update()` { #queryevents-before-compile-update }

```python
QueryEvents.before_compile_update(query, update_context)
```

**ধরন:** মেথড

`Query.update()`-এর আগে।

**উদাহরণ:**

```python
from sqlalchemy.orm import Query
on(Query, "before_compile_update", lambda q, ctx: calls.append("update"))
session.query(User).filter(User.id == 1).update({"slug": "x"})
print(calls)   # ['update']
```

/// check | সংক্ষেপে মনে রাখুন

* সেভের আগে সব যাচাই/হিসাব: `before_flush` (`session.new`, `session.dirty`, `session.deleted`)।
* সব কুয়েরিতে ফিল্টার: `do_orm_execute` + `with_loader_criteria(..., include_aliases=True)`।
* commit-এর পরে বাইরের কাজ: `after_commit` (ডেটাবেসে লেখা নয়)।
* একটি মডেলের INSERT/UPDATE-এ নিজের কলাম বসানো: `before_insert` / `before_update`।
* মান normalize: `@event.listens_for(User.email, "set", retval=True)`।
* লোডের পর সেটআপ (`__init__` চলে না): `InstanceEvents.load` বা `@reconstructor`।

///
