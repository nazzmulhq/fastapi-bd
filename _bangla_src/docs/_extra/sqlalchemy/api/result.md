# Result ও Row API: সম্পূর্ণ রেফারেন্স { #api-result }

/// note | এই পেজে যা আছে

* `session.execute()` / `connection.execute()` যা ফেরত দেয়, সেই `Result`-এর **প্রতিটি** মেথড।
* `ScalarResult`, `MappingResult`, `TupleResult`, `Row`, `RowMapping`, `CursorResult`, `FrozenResult` আর বাকি ফলাফল-ক্লাস।
* SQLAlchemy **2.1**-এর পরিবর্তন: `Row` এখন সরাসরি tuple-এর মতো, তাই `.t` / `.tuples()` বাতিলের পথে।

///

কুয়েরি চালালে যা ফেরত আসে তা হলো একটি **Result**। এটা অনেকটা দোকানের রসিদের বাক্সের মতো: সব রসিদ একসাথে নিতে পারেন (`.all()`), শুধু প্রথমটা (`.first()`), ঠিক একটা (`.one()`), বা একটা একটা করে (`for row in result`)। একবার যা বের করে নিয়েছেন তা আর বাক্সে থাকে না।

/// info | কোনটা কখন — এক নজরে

| চাই | লিখুন | পাবেন |
| :--- | :--- | :--- |
| সব রো | `result.all()` | `Row`-এর তালিকা |
| সব অবজেক্ট / একটি কলামের সব মান | `result.scalars().all()` | মানের তালিকা |
| ঠিক একটি রো (না থাকলে বা বেশি হলে এরর) | `result.one()` | `Row` |
| শূন্য বা একটি | `result.one_or_none()` / `result.scalar_one_or_none()` | `Row` / মান / `None` |
| প্রথমটি, বাকিগুলো বাদ | `result.first()` / `result.scalar()` | `Row` / মান / `None` |
| dict হিসেবে | `result.mappings().all()` | `RowMapping`-এর তালিকা |
| ডুপ্লিকেট বাদ | `result.unique()` | একই ধরনের Result |

///

এই পেজের উদাহরণগুলো [Session API পেজের](session.md) মতোই `User` / `Address` মডেল আর তিনজন ইউজার (রহিম, করিম, সুমি) ধরে লেখা, আর PostgreSQL-এ চালিয়ে দেখা হয়েছে।

## `Result` { #result }

```python
from sqlalchemy.engine import Result
```

একটি কুয়েরির ফলাফল। প্রতিটি আইটেম একটি `Row` (টাপলের মতো, নাম দিয়েও পড়া যায়)। `Result` একটি **iterator**: প্রতিটি রো একবারই পাওয়া যায়। ORM-এ `session.execute()` সাধারণত ফলাফল আগেই মেমরিতে এনে রাখে (buffered), তাই কানেকশন আটকে থাকে না।

**উদাহরণ:**

```python
result = session.execute(select(User.id, User.name).order_by(User.id))
for row in result:
    print(row.id, row.name)       # নাম দিয়ে
# 1 রহিম / 2 করিম / 3 সুমি
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #result-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#result-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#result-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#result-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#result-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#result-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#result-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#result-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#result-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#result-freeze) | মেথড | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`keys()`](#result-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`mappings()`](#result-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#result-memoized-attribute) | অ্যাট্রিবিউট (internal) | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#result-memoized-instancemethod) | ক্লাস মেথড (internal) | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`merge()`](#result-merge) | মেথড | একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে। |
| [`one()`](#result-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#result-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#result-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`scalar()`](#result-scalar) | মেথড | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#result-scalar-one) | মেথড | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#result-scalar-one-or-none) | মেথড | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#result-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`t`](#result-t) | প্রপার্টি ⚠️ deprecated | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#result-tuples) | মেথড ⚠️ deprecated | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#result-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#result-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `Result.all()` { #result-all }

```python
Result.all()
```

**ধরন:** মেথড

বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। পরে আবার ডাকলে খালি তালিকা।

**উদাহরণ:**

```python
rows = session.execute(select(User.id, User.name).order_by(User.id)).all()
print(rows[0].name, len(rows))   # রহিম 3
```

### `Result.close()` { #result-close }

```python
Result.close()
```

**ধরন:** মেথড

Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। বন্ধ করার পর রো চাইলে এরর হয়। সাধারণত সব রো পড়া শেষ হলে নিজেই বন্ধ হয়, তাই আলাদা করে ডাকতে হয় না।

**উদাহরণ:**

```python
result = session.execute(select(User))
result.close()
print(result.closed)   # True
```

### `Result.closed` { #result-closed }

**ধরন:** প্রপার্টি

`close()` দিয়ে বন্ধ করা হলে `True`।

**উদাহরণ:**

```python
result = session.execute(select(User.id))
print(result.closed)   # False
```

### `Result.columns()` { #result-columns }

```python
Result.columns(*col_expressions)
```

**ধরন:** মেথড

প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। কলাম বাদ দেওয়া বা ক্রম বদলানো যায়।

**উদাহরণ:**

```python
result = session.execute(select(User.id, User.name).order_by(User.id))
print(result.columns("name", "id").first())   # ('রহিম', 1)
```

### `Result.fetchall()` { #result-fetchall }

```python
Result.fetchall()
```

**ধরন:** মেথড

`all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। কাজ একই।

**উদাহরণ:**

```python
print(len(session.execute(select(User.id)).fetchall()))   # 3
```

### `Result.fetchmany()` { #result-fetchmany }

```python
Result.fetchmany(size=None)
```

**ধরন:** মেথড

পরের `size`-টি রো দেয়। শেষ হয়ে গেলে খালি তালিকা। বড় ফলাফল টুকরো টুকরো করে পড়তে কাজে লাগে।

**উদাহরণ:**

```python
result = session.execute(select(User.id).order_by(User.id))
print(result.fetchmany(2))   # [(1,), (2,)]
print(result.fetchmany(2))   # [(3,)]
```

### `Result.fetchone()` { #result-fetchone }

```python
Result.fetchone()
```

**ধরন:** মেথড

পরের একটি রো দেয়, শেষ হলে `None`। Result বন্ধ করে না, তাই বাকিগুলো পরে পড়া যায়।

**উদাহরণ:**

```python
result = session.execute(select(User.id).order_by(User.id))
print(result.fetchone(), result.fetchone())   # (1,) (2,)
```

### `Result.first()` { #result-first }

```python
Result.first()
```

**ধরন:** মেথড

প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। একাধিক রো থাকলেও এরর দেয় না।

**উদাহরণ:**

```python
row = session.execute(select(User.name).order_by(User.id)).first()
print(row.name)   # রহিম
```

### `Result.freeze()` { #result-freeze }

```python
Result.freeze()
```

**ধরন:** মেথড

ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। ক্যাশিংয়ের জন্য কাজে লাগে।

**উদাহরণ:**

```python
frozen = session.execute(select(User.name).order_by(User.id)).freeze()
print(frozen().scalars().all())   # ['রহিম', 'করিম', 'সুমি']
print(frozen().first())           # ('রহিম',) — আবারও পাওয়া গেল
```

### `Result.keys()` { #result-keys }

```python
Result.keys()
```

**ধরন:** মেথড

প্রতিটি রো-র কলামের নামগুলো দেয়।

**উদাহরণ:**

```python
result = session.execute(select(User.id, User.name))
print(list(result.keys()))   # ['id', 'name']
```

### `Result.mappings()` { #result-mappings }

```python
Result.mappings()
```

**ধরন:** মেথড

রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। JSON বানাতে বা রিপোর্টে সুবিধাজনক।

**উদাহরণ:**

```python
rows = session.execute(select(User.id, User.name).order_by(User.id)).mappings().all()
print(rows[0]["name"], dict(rows[0]))   # রহিম {'id': 1, 'name': 'রহিম'}
```

### `Result.memoized_attribute` { #result-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। ক্লাসে নাম হিসেবে দেখা যায়, কিন্তু ফলাফল পড়ার সাথে এর কোনো সম্পর্ক নেই।

### `Result.memoized_instancemethod()` { #result-memoized-instancemethod }

```python
Result.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। অ্যাপ কোডে দরকার নেই।

### `Result.merge()` { #result-merge }

```python
Result.merge(*others)
```

**ধরন:** মেথড

একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে।

**উদাহরণ:**

```python
r1 = session.execute(select(User.name).where(User.id == 1))
r2 = session.execute(select(User.name).where(User.id == 2))
print(r1.merge(r2).scalars().all())   # ['রহিম', 'করিম']
```

### `Result.one()` { #result-one }

```python
Result.one()
```

**ধরন:** মেথড

ঠিক একটি রো দেয়। কোনো রো না থাকলে `NoResultFound`, একাধিক থাকলে `MultipleResultsFound` এরর।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name).where(User.id == 2)).one()
print(row)   # (2, 'করিম')
```

### `Result.one_or_none()` { #result-one-or-none }

```python
Result.one_or_none()
```

**ধরন:** মেথড

শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`।

**উদাহরণ:**

```python
print(session.execute(select(User.id).where(User.id == 99)).one_or_none())   # None
```

### `Result.partitions()` { #result-partitions }

```python
Result.partitions(size=None)
```

**ধরন:** মেথড

রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। `yield_per`-এর সাথে মিলিয়ে বড় ডেটা ব্যাচে প্রসেস করতে ব্যবহার হয়।

**উদাহরণ:**

```python
result = session.execute(select(User.id).order_by(User.id))
for chunk in result.partitions(2):
    print([r.id for r in chunk])   # [1, 2] তারপর [3]
```

### `Result.scalar()` { #result-scalar }

```python
Result.scalar()
```

**ধরন:** মেথড

প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে।

**উদাহরণ:**

```python
print(session.execute(select(func.count()).select_from(User)).scalar())   # 3
```

### `Result.scalar_one()` { #result-scalar-one }

```python
Result.scalar_one()
```

**ধরন:** মেথড

ঠিক একটি রো-র প্রথম কলাম দেয়। না থাকলে বা একাধিক থাকলে এরর। `count(*)` জাতীয় কুয়েরিতে আদর্শ।

**উদাহরণ:**

```python
print(session.execute(select(User.name).where(User.id == 3)).scalar_one())   # সুমি
```

### `Result.scalar_one_or_none()` { #result-scalar-one-or-none }

```python
Result.scalar_one_or_none()
```

**ধরন:** মেথড

শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। "খুঁজে দেখো, থাকলে দাও" ধরনের কাজে সবচেয়ে বেশি ব্যবহৃত।

**উদাহরণ:**

```python
user = session.execute(select(User).where(User.name == "করিম")).scalar_one_or_none()
print(user.id)   # 2
```

### `Result.scalars()` { #result-scalars }

```python
Result.scalars(index=0)
```

**ধরন:** মেথড

প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। ORM অবজেক্টের তালিকা পেতে সবচেয়ে প্রচলিত।

**উদাহরণ:**

```python
users = session.execute(select(User).order_by(User.id)).scalars().all()
names = session.execute(select(User.id, User.name)).scalars(1).all()   # দ্বিতীয় কলাম
print([u.name for u in users], sorted(names))
```

### `Result.t` { #result-t }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। ২.১-এ বাতিলের পথে, কারণ `Row` এখন নিজেই tuple-এর মতো আচরণ করে আর টাইপসহ unpack করা যায়। সরাসরি `for id_, name in result:` লিখুন।

**উদাহরণ:**

```python
for id_, name in session.execute(select(User.id, User.name).order_by(User.id)):
    print(id_, name)
```

### `Result.tuples()` { #result-tuples }

```python
Result.tuples()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

`t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। সরাসরি রো unpack করুন।

**উদাহরণ:**

```python
(id_, name), *_ = session.execute(select(User.id, User.name).order_by(User.id)).all()
print(id_, name)   # 1 রহিম
```

### `Result.unique()` { #result-unique }

```python
Result.unique(strategy=None)
```

**ধরন:** মেথড

একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। কালেকশনে `joinedload()` বা `contains_eager()` করলে **বাধ্যতামূলক**। `strategy=` দিয়ে নিজের তুলনার নিয়ম দেওয়া যায়।

**উদাহরণ:**

```python
stmt = select(User).options(joinedload(User.addresses)).order_by(User.id)
users = session.execute(stmt).unique().scalars().all()
print(len(users))   # 3 (রহিমের দুই ঠিকানা থাকলেও রহিম একবার)
```

### `Result.yield_per()` { #result-yield-per }

```python
Result.yield_per(num)
```

**ধরন:** মেথড

ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। বিশাল ফলাফলে মেমরি কম লাগে। স্টেটমেন্টে `.execution_options(yield_per=N)` দেওয়াও একই কাজ করে।

**উদাহরণ:**

```python
result = session.execute(select(User.id).order_by(User.id)).yield_per(2)
print([r.id for r in result])   # [1, 2, 3] — কিন্তু ২টি করে আনা হয়েছে
```

## `ScalarResult` { #scalarresult }

```python
from sqlalchemy.engine import ScalarResult
```

`Result`-এর একটি মোড়ক, যেখানে প্রতিটি আইটেম একটি `Row` নয়, একটি **একক মান** (সাধারণত একটি ORM অবজেক্ট)। `session.scalars()` বা `result.scalars()` এটি দেয়।

**উদাহরণ:**

```python
users = session.scalars(select(User).order_by(User.id))
for user in users:
    print(user.name)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #scalarresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#scalarresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#scalarresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#scalarresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`fetchall()`](#scalarresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#scalarresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`first()`](#scalarresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`memoized_attribute`](#scalarresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#scalarresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`one()`](#scalarresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#scalarresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#scalarresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`unique()`](#scalarresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#scalarresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `ScalarResult.all()` { #scalarresult-all }

```python
ScalarResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.close()` { #scalarresult-close }

```python
ScalarResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.closed` { #scalarresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.fetchall()` { #scalarresult-fetchall }

```python
ScalarResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.fetchmany()` { #scalarresult-fetchmany }

```python
ScalarResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.first()` { #scalarresult-first }

```python
ScalarResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.memoized_attribute` { #scalarresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.memoized_instancemethod()` { #scalarresult-memoized-instancemethod }

```python
ScalarResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.one()` { #scalarresult-one }

```python
ScalarResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.one_or_none()` { #scalarresult-one-or-none }

```python
ScalarResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.partitions()` { #scalarresult-partitions }

```python
ScalarResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.unique()` { #scalarresult-unique }

```python
ScalarResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

### `ScalarResult.yield_per()` { #scalarresult-yield-per }

```python
ScalarResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম `Row` নয়, একটি একক মান (যেমন `User` অবজেক্ট)।

## `MappingResult` { #mappingresult }

```python
from sqlalchemy.engine import MappingResult
```

`Result`-এর মোড়ক, যেখানে প্রতিটি আইটেম একটি dict-এর মতো `RowMapping`। `result.mappings()` এটি দেয়।

**উদাহরণ:**

```python
for m in session.execute(select(User.id, User.name).order_by(User.id)).mappings():
    print(m["id"], m["name"])
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mappingresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#mappingresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#mappingresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#mappingresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#mappingresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#mappingresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#mappingresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#mappingresult-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#mappingresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`keys()`](#mappingresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`memoized_attribute`](#mappingresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#mappingresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`one()`](#mappingresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#mappingresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#mappingresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`unique()`](#mappingresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#mappingresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `MappingResult.all()` { #mappingresult-all }

```python
MappingResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.close()` { #mappingresult-close }

```python
MappingResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.closed` { #mappingresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.columns()` { #mappingresult-columns }

```python
MappingResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](#result-columns)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.fetchall()` { #mappingresult-fetchall }

```python
MappingResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.fetchmany()` { #mappingresult-fetchmany }

```python
MappingResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.fetchone()` { #mappingresult-fetchone }

```python
MappingResult.fetchone()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchone`](#result-fetchone)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.first()` { #mappingresult-first }

```python
MappingResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.keys()` { #mappingresult-keys }

```python
MappingResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](#result-keys)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.memoized_attribute` { #mappingresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.memoized_instancemethod()` { #mappingresult-memoized-instancemethod }

```python
MappingResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.one()` { #mappingresult-one }

```python
MappingResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.one_or_none()` { #mappingresult-one-or-none }

```python
MappingResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.partitions()` { #mappingresult-partitions }

```python
MappingResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.unique()` { #mappingresult-unique }

```python
MappingResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

### `MappingResult.yield_per()` { #mappingresult-yield-per }

```python
MappingResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো। পার্থক্য শুধু এটুকু: এখানে প্রতিটি আইটেম dict-এর মতো `RowMapping`।

## `TupleResult` { #tupleresult }

```python
from sqlalchemy.engine import TupleResult
```

শুধু টাইপ চেকারের জন্য: `Result` যেটা প্রতিটি রো-কে সাধারণ tuple হিসেবে ঘোষণা করে। রানটাইমে আসল অবজেক্টটি `Result`-ই। `Result.tuples()` (২.১-এ বাতিলের পথে) এটি দেয়।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tupleresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#tupleresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#tupleresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`memoized_attribute`](#tupleresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#tupleresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`yield_per()`](#tupleresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `TupleResult.close()` { #tupleresult-close }

```python
TupleResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `TupleResult.closed` { #tupleresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `TupleResult.memoized_attribute` { #tupleresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `TupleResult.memoized_instancemethod()` { #tupleresult-memoized-instancemethod }

```python
TupleResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `TupleResult.yield_per()` { #tupleresult-yield-per }

```python
TupleResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

## `Row` { #row }

```python
from sqlalchemy.engine import Row
```

ফলাফলের একটি রো। এটি একটি **named tuple**-এর মতো: অবস্থান দিয়ে (`row[0]`), নাম দিয়ে (`row.name`), বা unpack করে (`id_, name = row`) পড়া যায়। ২.১ থেকে `Row` আরও বেশি tuple-এর মতো, টাইপসহ unpack সরাসরি কাজ করে।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name).where(User.id == 1)).one()
print(row[0], row.name)     # 1 রহিম
id_, name = row
print(id_, name)            # 1 রহিম
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #row-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`_asdict()`](#row--asdict) | মেথড | রো-কে একটি সাধারণ Python `dict` বানিয়ে দেয় (named tuple-এর `_asdict()`-এর মতো)। |
| [`_fields`](#row--fields) | প্রপার্টি | রো-র কলামগুলোর নাম একটি tuple-এ দেয়। |
| [`_mapping`](#row--mapping) | প্রপার্টি | একই রো-র একটি dict-এর মতো রূপ (`RowMapping`) দেয়। |
| [`_t`](#row--t) | প্রপার্টি ⚠️ deprecated | `_tuple()`-এর প্রপার্টি রূপ। |
| [`_tuple()`](#row--tuple) | মেথড ⚠️ deprecated | রো-কে সাধারণ `tuple` হিসেবে দেয় (টাইপিংয়ের জন্য)। |
| [`count`](#row-count) | প্রপার্টি | সাধারণ tuple-এর `count()`: একটি মান রো-তে কতবার আছে তা গোনে। |
| [`index`](#row-index) | প্রপার্টি | সাধারণ tuple-এর `index()`: একটি মান রো-র কোন অবস্থানে প্রথম আছে তা দেয়। |
| [`t`](#row-t) | প্রপার্টি ⚠️ deprecated | ২.০.১৯ থেকে বাতিলের পথে (আগে `Row.t`)। |
| [`tuple()`](#row-tuple) | মেথড ⚠️ deprecated | ২.০.১৯ থেকে বাতিলের পথে। |

### `Row._asdict()` { #row--asdict }

```python
Row._asdict()
```

**ধরন:** মেথড

রো-কে একটি সাধারণ Python `dict` বানিয়ে দেয় (named tuple-এর `_asdict()`-এর মতো)। নামের আগে `_` থাকলেও এটি পাবলিক API, যাতে কলামের নামের সাথে সংঘর্ষ না হয়।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name).where(User.id == 2)).one()
print(row._asdict())   # {'id': 2, 'name': 'করিম'}
```

### `Row._fields` { #row--fields }

**ধরন:** প্রপার্টি

রো-র কলামগুলোর নাম একটি tuple-এ দেয়।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name)).first()
print(row._fields)   # ('id', 'name')
```

### `Row._mapping` { #row--mapping }

**ধরন:** প্রপার্টি

একই রো-র একটি dict-এর মতো রূপ (`RowMapping`) দেয়। নাম বা কলাম অবজেক্ট দিয়ে মান পড়া যায়।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name).where(User.id == 1)).one()
print(row._mapping["name"], row._mapping[User.id])   # রহিম 1
```

### `Row._t` { #row--t }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

`_tuple()`-এর প্রপার্টি রূপ। ২.১-এ বাতিলের পথে, কারণ `Row` নিজেই এখন টাইপসহ tuple-এর মতো কাজ করে।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name)).first()
id_, name = row          # সরাসরি unpack করুন
```

### `Row._tuple()` { #row--tuple }

```python
Row._tuple()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

রো-কে সাধারণ `tuple` হিসেবে দেয় (টাইপিংয়ের জন্য)। ২.১-এ বাতিলের পথে; দরকার হলে `tuple(row)` লিখুন।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name)).first()
print(tuple(row))   # (1, 'রহিম')
```

### `Row.count` { #row-count }

**ধরন:** প্রপার্টি

সাধারণ tuple-এর `count()`: একটি মান রো-তে কতবার আছে তা গোনে।

**উদাহরণ:**

```python
row = session.execute(select(literal(5), literal(5), literal(7))).one()
print(row.count(5))   # 2
```

### `Row.index` { #row-index }

**ধরন:** প্রপার্টি

সাধারণ tuple-এর `index()`: একটি মান রো-র কোন অবস্থানে প্রথম আছে তা দেয়।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name).where(User.id == 3)).one()
print(row.index("সুমি"))   # 1
```

### `Row.t` { #row-t }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

২.০.১৯ থেকে বাতিলের পথে (আগে `Row.t`)। সরাসরি রো unpack করুন বা `tuple(row)` লিখুন।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name)).first()
id_, name = row
```

### `Row.tuple()` { #row-tuple }

```python
Row.tuple()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

২.০.১৯ থেকে বাতিলের পথে। বিকল্প: `tuple(row)` বা সরাসরি unpack।

**উদাহরণ:**

```python
row = session.execute(select(User.id, User.name)).first()
print(tuple(row))
```

## `RowMapping` { #rowmapping }

```python
from sqlalchemy.engine import RowMapping
```

একটি রো-র dict-এর মতো রূপ। key হিসেবে কলামের নাম (string) বা কলাম অবজেক্ট দুটোই চলে। পরিবর্তন করা যায় না (read-only)। `result.mappings()` বা `row._mapping` এটি দেয়।

**উদাহরণ:**

```python
m = session.execute(select(User.id, User.name).where(User.id == 1)).mappings().one()
print(m["name"], m[User.name], "id" in m)   # রহিম রহিম True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #rowmapping-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get()`](#rowmapping-get) | মেথড | dict-এর `get()`-এর মতো: key থাকলে মান, না থাকলে `default` (ডিফল্ট `None`)। |
| [`items()`](#rowmapping-items) | মেথড | `(কলামের নাম, মান)` জোড়াগুলো দেয়, dict-এর `items()`-এর মতো। |
| [`keys()`](#rowmapping-keys) | মেথড | কলামের নামগুলো দেয়, dict-এর `keys()`-এর মতো। |
| [`values()`](#rowmapping-values) | মেথড | শুধু মানগুলো দেয়, dict-এর `values()`-এর মতো। |

### `RowMapping.get()` { #rowmapping-get }

```python
RowMapping.get(key, default=None)
```

**ধরন:** মেথড

dict-এর `get()`-এর মতো: key থাকলে মান, না থাকলে `default` (ডিফল্ট `None`)।

**উদাহরণ:**

```python
m = session.execute(select(User.id, User.name)).mappings().first()
print(m.get("name"), m.get("email", "নেই"))   # রহিম নেই
```

### `RowMapping.items()` { #rowmapping-items }

```python
RowMapping.items()
```

**ধরন:** মেথড

`(কলামের নাম, মান)` জোড়াগুলো দেয়, dict-এর `items()`-এর মতো।

**উদাহরণ:**

```python
m = session.execute(select(User.id, User.name).where(User.id == 2)).mappings().one()
print(list(m.items()))   # [('id', 2), ('name', 'করিম')]
```

### `RowMapping.keys()` { #rowmapping-keys }

```python
RowMapping.keys()
```

**ধরন:** মেথড

কলামের নামগুলো দেয়, dict-এর `keys()`-এর মতো।

**উদাহরণ:**

```python
m = session.execute(select(User.id, User.name)).mappings().first()
print(list(m.keys()))   # ['id', 'name']
```

### `RowMapping.values()` { #rowmapping-values }

```python
RowMapping.values()
```

**ধরন:** মেথড

শুধু মানগুলো দেয়, dict-এর `values()`-এর মতো।

**উদাহরণ:**

```python
m = session.execute(select(User.id, User.name).where(User.id == 3)).mappings().one()
print(list(m.values()))   # [3, 'সুমি']
```

## `CursorResult` { #cursorresult }

```python
from sqlalchemy.engine import CursorResult
```

Core লেভেলে (`connection.execute()`) আর DML-এ (`insert`/`update`/`delete`) যে `Result` আসে, যার পেছনে একটি DBAPI cursor আছে। সাধারণ `Result`-এর সব মেথড ছাড়াও এতে আছে `rowcount`, `inserted_primary_key`, `returned_defaults` জাতীয় তথ্য।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(update(User.__table__).where(User.__table__.c.id > 1).values(name="নাম বদল"))
    print(type(result).__name__, result.rowcount)   # CursorResult 2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cursorresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#cursorresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#cursorresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#cursorresult-closed) | অ্যাট্রিবিউট | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#cursorresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`connection`](#cursorresult-connection) | অ্যাট্রিবিউট (internal) | এই ফলাফল যে `Connection`-এ তৈরি হয়েছে সেটি। |
| [`context`](#cursorresult-context) | অ্যাট্রিবিউট (internal) | ভেতরের `ExecutionContext`, যেখানে এই এক্সিকিউশনের সব খুঁটিনাটি থাকে (কম্পাইল করা SQL, প্যারামিটার)। |
| [`cursor`](#cursorresult-cursor) | অ্যাট্রিবিউট (internal) | ভেতরের আসল DBAPI cursor অবজেক্ট (যেমন psycopg2-এর cursor)। |
| [`cursor_strategy`](#cursorresult-cursor-strategy) | অ্যাট্রিবিউট (internal) | cursor থেকে রো কীভাবে আনা হবে তার ভেতরের কৌশল-অবজেক্ট (buffered, server-side ইত্যাদি)। |
| [`dialect`](#cursorresult-dialect) | অ্যাট্রিবিউট | যে ডেটাবেস ডায়ালেক্টে কুয়েরি চলেছে (যেমন PostgreSQL)। |
| [`fetchall()`](#cursorresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#cursorresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#cursorresult-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#cursorresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#cursorresult-freeze) | মেথড | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`inserted_primary_key`](#cursorresult-inserted-primary-key) | প্রপার্টি | একটি রো-র `insert()` চালানোর পর নতুন রো-র primary key, একটি `Row` হিসেবে। |
| [`inserted_primary_key_rows`](#cursorresult-inserted-primary-key-rows) | প্রপার্টি | `inserted_primary_key`-এর তালিকা রূপ; একাধিক রো insert করলে প্রতিটির primary key (ড্রাইভার সাপোর্ট করলে)। |
| [`is_insert`](#cursorresult-is-insert) | প্রপার্টি | এই ফলাফল একটি `insert()` থেকে এলে `True`। |
| [`keys()`](#cursorresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`last_inserted_params()`](#cursorresult-last-inserted-params) | মেথড | শেষ `insert()`-এ যে প্যারামিটার (default সহ) পাঠানো হয়েছিল সেগুলো। |
| [`last_updated_params()`](#cursorresult-last-updated-params) | মেথড | শেষ `update()`-এ পাঠানো প্যারামিটারগুলো। |
| [`lastrow_has_defaults()`](#cursorresult-lastrow-has-defaults) | মেথড | শেষ insert/update করা রো-তে ডেটাবেস-তৈরি default মান ছিল কি না। |
| [`lastrowid`](#cursorresult-lastrowid) | প্রপার্টি | DBAPI cursor-এর `lastrowid` (শেষ insert করা রো-র id)। |
| [`mappings()`](#cursorresult-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#cursorresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#cursorresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`merge()`](#cursorresult-merge) | মেথড | একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে। |
| [`one()`](#cursorresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#cursorresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#cursorresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`postfetch_cols()`](#cursorresult-postfetch-cols) | মেথড | যেসব কলামের মান ডেটাবেসে তৈরি হয়েছে আর পরে আলাদা করে আনতে হবে (server default/onupdate), সেগুলোর তালিকা। |
| [`prefetch_cols()`](#cursorresult-prefetch-cols) | মেথড | যেসব কলামের মান SQL চালানোর আগেই Python-এ হিসাব করা হয়েছে (Python-side default), সেগুলোর তালিকা। |
| [`returned_defaults`](#cursorresult-returned-defaults) | প্রপার্টি | `.return_defaults()` দেওয়া insert/update-এর পর ডেটাবেস যে default মানগুলো ফেরত দিয়েছে, একটি `Row` হিসেবে। |
| [`returned_defaults_rows`](#cursorresult-returned-defaults-rows) | প্রপার্টি | `returned_defaults`-এর তালিকা রূপ, একাধিক রো-র জন্য। |
| [`returns_rows`](#cursorresult-returns-rows) | প্রপার্টি | এই ফলাফলে রো আছে কি না (SELECT বা `RETURNING`-যুক্ত DML হলে `True`)। |
| [`rowcount`](#cursorresult-rowcount) | প্রপার্টি | UPDATE বা DELETE কয়টি রো-তে মিলেছে (match) তার সংখ্যা। |
| [`scalar()`](#cursorresult-scalar) | মেথড | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#cursorresult-scalar-one) | মেথড | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#cursorresult-scalar-one-or-none) | মেথড | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#cursorresult-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`splice_horizontally()`](#cursorresult-splice-horizontally) | মেথড | দুটি `CursorResult`-এর রো পাশাপাশি জোড়া দেয় (প্রথমটির কলাম + দ্বিতীয়টির কলাম)। |
| [`splice_vertically()`](#cursorresult-splice-vertically) | মেথড | দুটি `CursorResult`-এর রো ওপর-নিচে জোড়া দেয় (প্রথমটির রো, তারপর দ্বিতীয়টির)। |
| [`supports_sane_multi_rowcount()`](#cursorresult-supports-sane-multi-rowcount) | মেথড | ড্রাইভার executemany-তেও সঠিক `rowcount` দিতে পারে কি না। |
| [`supports_sane_rowcount()`](#cursorresult-supports-sane-rowcount) | মেথড | ড্রাইভার সাধারণ UPDATE/DELETE-এ সঠিক `rowcount` দিতে পারে কি না। |
| [`t`](#cursorresult-t) | প্রপার্টি | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#cursorresult-tuples) | মেথড | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#cursorresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#cursorresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `CursorResult.all()` { #cursorresult-all }

```python
CursorResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো।

### `CursorResult.close()` { #cursorresult-close }

```python
CursorResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `CursorResult.closed` { #cursorresult-closed }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `CursorResult.columns()` { #cursorresult-columns }

```python
CursorResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](#result-columns)-এর মতো।

### `CursorResult.connection` { #cursorresult-connection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই ফলাফল যে `Connection`-এ তৈরি হয়েছে সেটি।

**উদাহরণ:**

```python
with engine.connect() as conn:
    result = conn.execute(select(User.__table__.c.id))
    print(result.connection is conn)   # True
```

### `CursorResult.context` { #cursorresult-context }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের `ExecutionContext`, যেখানে এই এক্সিকিউশনের সব খুঁটিনাটি থাকে (কম্পাইল করা SQL, প্যারামিটার)। ডিবাগিংয়ে কাজে লাগে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    result = conn.execute(select(User.__table__.c.id).where(User.__table__.c.id == 1))
    print(result.context.statement)   # কম্পাইল করা SQL
```

### `CursorResult.cursor` { #cursorresult-cursor }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের আসল DBAPI cursor অবজেক্ট (যেমন psycopg2-এর cursor)। সব রো পড়া শেষ হলে `None` হয়ে যায়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    result = conn.execute(select(User.__table__.c.id))
    print(result.cursor is not None)   # True
```

### `CursorResult.cursor_strategy` { #cursorresult-cursor-strategy }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

cursor থেকে রো কীভাবে আনা হবে তার ভেতরের কৌশল-অবজেক্ট (buffered, server-side ইত্যাদি)।

### `CursorResult.dialect` { #cursorresult-dialect }

**ধরন:** অ্যাট্রিবিউট

যে ডেটাবেস ডায়ালেক্টে কুয়েরি চলেছে (যেমন PostgreSQL)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(literal(1))).dialect.name)   # postgresql
```

### `CursorResult.fetchall()` { #cursorresult-fetchall }

```python
CursorResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো।

### `CursorResult.fetchmany()` { #cursorresult-fetchmany }

```python
CursorResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো।

### `CursorResult.fetchone()` { #cursorresult-fetchone }

```python
CursorResult.fetchone()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchone`](#result-fetchone)-এর মতো।

### `CursorResult.first()` { #cursorresult-first }

```python
CursorResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো।

### `CursorResult.freeze()` { #cursorresult-freeze }

```python
CursorResult.freeze()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.freeze`](#result-freeze)-এর মতো।

### `CursorResult.inserted_primary_key` { #cursorresult-inserted-primary-key }

**ধরন:** প্রপার্টি

একটি রো-র `insert()` চালানোর পর নতুন রো-র primary key, একটি `Row` হিসেবে।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="নতুন"))
    print(result.inserted_primary_key)   # (4,)
```

### `CursorResult.inserted_primary_key_rows` { #cursorresult-inserted-primary-key-rows }

**ধরন:** প্রপার্টি

`inserted_primary_key`-এর তালিকা রূপ; একাধিক রো insert করলে প্রতিটির primary key (ড্রাইভার সাপোর্ট করলে)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="এক"))
    print(result.inserted_primary_key_rows)   # [(4,)]
```

### `CursorResult.is_insert` { #cursorresult-is-insert }

**ধরন:** প্রপার্টি

এই ফলাফল একটি `insert()` থেকে এলে `True`।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(User.__table__).values(name="ক")).is_insert)   # True
```

### `CursorResult.keys()` { #cursorresult-keys }

```python
CursorResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](#result-keys)-এর মতো।

### `CursorResult.last_inserted_params()` { #cursorresult-last-inserted-params }

```python
CursorResult.last_inserted_params()
```

**ধরন:** মেথড

শেষ `insert()`-এ যে প্যারামিটার (default সহ) পাঠানো হয়েছিল সেগুলো।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="প্যারাম"))
    print(result.last_inserted_params())   # {'name': 'প্যারাম'}
```

### `CursorResult.last_updated_params()` { #cursorresult-last-updated-params }

```python
CursorResult.last_updated_params()
```

**ধরন:** মেথড

শেষ `update()`-এ পাঠানো প্যারামিটারগুলো।

**উদাহরণ:**

```python
t = User.__table__
with engine.begin() as conn:
    result = conn.execute(t.update().where(t.c.id == 1).values(name="নতুন রহিম"))
    print(result.last_updated_params())   # {'name': 'নতুন রহিম', 'id_1': 1}
```

### `CursorResult.lastrow_has_defaults()` { #cursorresult-lastrow-has-defaults }

```python
CursorResult.lastrow_has_defaults()
```

**ধরন:** মেথড

শেষ insert/update করা রো-তে ডেটাবেস-তৈরি default মান ছিল কি না।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(User.__table__).values(name="দ")).lastrow_has_defaults())
```

### `CursorResult.lastrowid` { #cursorresult-lastrowid }

**ধরন:** প্রপার্টি

DBAPI cursor-এর `lastrowid` (শেষ insert করা রো-র id)। সব ডেটাবেসে নির্ভরযোগ্য নয় (PostgreSQL-এ সাধারণত অর্থহীন); `inserted_primary_key` বা `RETURNING` ভালো।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(User.__table__).values(name="ল")).lastrowid)
```

### `CursorResult.mappings()` { #cursorresult-mappings }

```python
CursorResult.mappings()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.mappings`](#result-mappings)-এর মতো।

### `CursorResult.memoized_attribute` { #cursorresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `CursorResult.memoized_instancemethod()` { #cursorresult-memoized-instancemethod }

```python
CursorResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `CursorResult.merge()` { #cursorresult-merge }

```python
CursorResult.merge(*others)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.merge`](#result-merge)-এর মতো।

### `CursorResult.one()` { #cursorresult-one }

```python
CursorResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো।

### `CursorResult.one_or_none()` { #cursorresult-one-or-none }

```python
CursorResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো।

### `CursorResult.partitions()` { #cursorresult-partitions }

```python
CursorResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো।

### `CursorResult.postfetch_cols()` { #cursorresult-postfetch-cols }

```python
CursorResult.postfetch_cols()
```

**ধরন:** মেথড

যেসব কলামের মান ডেটাবেসে তৈরি হয়েছে আর পরে আলাদা করে আনতে হবে (server default/onupdate), সেগুলোর তালিকা।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(User.__table__).values(name="প")).postfetch_cols())   # []
```

### `CursorResult.prefetch_cols()` { #cursorresult-prefetch-cols }

```python
CursorResult.prefetch_cols()
```

**ধরন:** মেথড

যেসব কলামের মান SQL চালানোর আগেই Python-এ হিসাব করা হয়েছে (Python-side default), সেগুলোর তালিকা।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(User.__table__).values(name="প্রি")).prefetch_cols())   # []
```

### `CursorResult.returned_defaults` { #cursorresult-returned-defaults }

**ধরন:** প্রপার্টি

`.return_defaults()` দেওয়া insert/update-এর পর ডেটাবেস যে default মানগুলো ফেরত দিয়েছে, একটি `Row` হিসেবে।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="ডিফল্ট").return_defaults())
    print(result.returned_defaults)   # (4,)
```

### `CursorResult.returned_defaults_rows` { #cursorresult-returned-defaults-rows }

**ধরন:** প্রপার্টি

`returned_defaults`-এর তালিকা রূপ, একাধিক রো-র জন্য।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="ড২").return_defaults())
    print(result.returned_defaults_rows)   # [(4,)]
```

### `CursorResult.returns_rows` { #cursorresult-returns-rows }

**ধরন:** প্রপার্টি

এই ফলাফলে রো আছে কি না (SELECT বা `RETURNING`-যুক্ত DML হলে `True`)।

**উদাহরণ:**

```python
t = User.__table__
with engine.begin() as conn:
    print(conn.execute(select(t.c.id)).returns_rows)                   # True
    print(conn.execute(t.update().values(name="x")).returns_rows)       # False
```

### `CursorResult.rowcount` { #cursorresult-rowcount }

**ধরন:** প্রপার্টি

UPDATE বা DELETE কয়টি রো-তে মিলেছে (match) তার সংখ্যা। SELECT-এ নির্ভরযোগ্য নয়। ORM বাল্ক `update()` / `delete()`-এও এটি পাওয়া যায়।

**উদাহরণ:**

```python
result = session.execute(update(User).where(User.id > 1).values(name="বাকি দুজন"))
print(result.rowcount)   # 2
```

### `CursorResult.scalar()` { #cursorresult-scalar }

```python
CursorResult.scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar`](#result-scalar)-এর মতো।

### `CursorResult.scalar_one()` { #cursorresult-scalar-one }

```python
CursorResult.scalar_one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one`](#result-scalar-one)-এর মতো।

### `CursorResult.scalar_one_or_none()` { #cursorresult-scalar-one-or-none }

```python
CursorResult.scalar_one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one_or_none`](#result-scalar-one-or-none)-এর মতো।

### `CursorResult.scalars()` { #cursorresult-scalars }

```python
CursorResult.scalars(index=0)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalars`](#result-scalars)-এর মতো।

### `CursorResult.splice_horizontally()` { #cursorresult-splice-horizontally }

```python
CursorResult.splice_horizontally(other)
```

**ধরন:** মেথড

দুটি `CursorResult`-এর রো পাশাপাশি জোড়া দেয় (প্রথমটির কলাম + দ্বিতীয়টির কলাম)। দুটিতে রো-সংখ্যা সমান হতে হবে। মূলত ORM-এর ভেতরের কাজে ব্যবহৃত।

**উদাহরণ:**

```python
with engine.connect() as conn:
    r1 = conn.execute(select(User.__table__.c.id).order_by(User.__table__.c.id))
    r2 = conn.execute(select(User.__table__.c.name).order_by(User.__table__.c.id))
    print(r1.splice_horizontally(r2).all())   # [(1, 'রহিম'), (2, 'করিম'), (3, 'সুমি')]
```

### `CursorResult.splice_vertically()` { #cursorresult-splice-vertically }

```python
CursorResult.splice_vertically(other)
```

**ধরন:** মেথড

দুটি `CursorResult`-এর রো ওপর-নিচে জোড়া দেয় (প্রথমটির রো, তারপর দ্বিতীয়টির)। কলাম একই হতে হবে।

**উদাহরণ:**

```python
t = User.__table__
with engine.connect() as conn:
    r1 = conn.execute(select(t.c.id).where(t.c.id == 1))
    r2 = conn.execute(select(t.c.id).where(t.c.id == 3))
    print(r1.splice_vertically(r2).all())   # [(1,), (3,)]
```

### `CursorResult.supports_sane_multi_rowcount()` { #cursorresult-supports-sane-multi-rowcount }

```python
CursorResult.supports_sane_multi_rowcount()
```

**ধরন:** মেথড

ড্রাইভার executemany-তেও সঠিক `rowcount` দিতে পারে কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(literal(1))).supports_sane_multi_rowcount())
```

### `CursorResult.supports_sane_rowcount()` { #cursorresult-supports-sane-rowcount }

```python
CursorResult.supports_sane_rowcount()
```

**ধরন:** মেথড

ড্রাইভার সাধারণ UPDATE/DELETE-এ সঠিক `rowcount` দিতে পারে কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(literal(1))).supports_sane_rowcount())   # True
```

### `CursorResult.t` { #cursorresult-t }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.t`](#result-t)-এর মতো।

### `CursorResult.tuples()` { #cursorresult-tuples }

```python
CursorResult.tuples()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.tuples`](#result-tuples)-এর মতো।

### `CursorResult.unique()` { #cursorresult-unique }

```python
CursorResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো।

### `CursorResult.yield_per()` { #cursorresult-yield-per }

```python
CursorResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

## `FrozenResult` { #frozenresult }

```python
from sqlalchemy.engine import FrozenResult
```

`Result.freeze()` থেকে পাওয়া "জমানো" ফলাফল। অবজেক্টটিকে ফাংশনের মতো ডাকলে (`frozen()`) প্রতিবার একই রো-সহ একটি নতুন `Result` দেয়। ফলাফল ক্যাশ করতে (যেমন dogpile cache) ব্যবহৃত হয়।

**উদাহরণ:**

```python
frozen = session.execute(select(User.id, User.name).order_by(User.id)).freeze()
print(frozen().all() == frozen().all())   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #frozenresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`with_new_rows()`](#frozenresult-with-new-rows) | মেথড | একই কলাম-কাঠামো রেখে নতুন রো দিয়ে একটি `FrozenResult` বানায়। |

### `FrozenResult.with_new_rows()` { #frozenresult-with-new-rows }

```python
FrozenResult.with_new_rows(tuple_data)
```

**ধরন:** মেথড

একই কলাম-কাঠামো রেখে নতুন রো দিয়ে একটি `FrozenResult` বানায়।

**উদাহরণ:**

```python
frozen = session.execute(select(User.id, User.name).where(User.id == 1)).freeze()
other = frozen.with_new_rows([(9, "নয়")])
print(other().all())   # [(9, 'নয়')]
```

## `IteratorResult` { #iteratorresult }

```python
from sqlalchemy.engine import IteratorResult
```

Python iterator থেকে রো দেয় এমন `Result`। ORM-এর buffered ফলাফল সাধারণত এই ধরনের। আচরণ পুরোপুরি `Result`-এর মতো।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #iteratorresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#iteratorresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#iteratorresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#iteratorresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#iteratorresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#iteratorresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#iteratorresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#iteratorresult-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#iteratorresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#iteratorresult-freeze) | মেথড | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`keys()`](#iteratorresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`mappings()`](#iteratorresult-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#iteratorresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#iteratorresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`merge()`](#iteratorresult-merge) | মেথড | একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে। |
| [`one()`](#iteratorresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#iteratorresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#iteratorresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`scalar()`](#iteratorresult-scalar) | মেথড | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#iteratorresult-scalar-one) | মেথড | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#iteratorresult-scalar-one-or-none) | মেথড | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#iteratorresult-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`t`](#iteratorresult-t) | প্রপার্টি | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#iteratorresult-tuples) | মেথড | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#iteratorresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#iteratorresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `IteratorResult.all()` { #iteratorresult-all }

```python
IteratorResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো।

### `IteratorResult.close()` { #iteratorresult-close }

```python
IteratorResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `IteratorResult.closed` { #iteratorresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `IteratorResult.columns()` { #iteratorresult-columns }

```python
IteratorResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](#result-columns)-এর মতো।

### `IteratorResult.fetchall()` { #iteratorresult-fetchall }

```python
IteratorResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো।

### `IteratorResult.fetchmany()` { #iteratorresult-fetchmany }

```python
IteratorResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো।

### `IteratorResult.fetchone()` { #iteratorresult-fetchone }

```python
IteratorResult.fetchone()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchone`](#result-fetchone)-এর মতো।

### `IteratorResult.first()` { #iteratorresult-first }

```python
IteratorResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো।

### `IteratorResult.freeze()` { #iteratorresult-freeze }

```python
IteratorResult.freeze()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.freeze`](#result-freeze)-এর মতো।

### `IteratorResult.keys()` { #iteratorresult-keys }

```python
IteratorResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](#result-keys)-এর মতো।

### `IteratorResult.mappings()` { #iteratorresult-mappings }

```python
IteratorResult.mappings()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.mappings`](#result-mappings)-এর মতো।

### `IteratorResult.memoized_attribute` { #iteratorresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `IteratorResult.memoized_instancemethod()` { #iteratorresult-memoized-instancemethod }

```python
IteratorResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `IteratorResult.merge()` { #iteratorresult-merge }

```python
IteratorResult.merge(*others)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.merge`](#result-merge)-এর মতো।

### `IteratorResult.one()` { #iteratorresult-one }

```python
IteratorResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো।

### `IteratorResult.one_or_none()` { #iteratorresult-one-or-none }

```python
IteratorResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো।

### `IteratorResult.partitions()` { #iteratorresult-partitions }

```python
IteratorResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো।

### `IteratorResult.scalar()` { #iteratorresult-scalar }

```python
IteratorResult.scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar`](#result-scalar)-এর মতো।

### `IteratorResult.scalar_one()` { #iteratorresult-scalar-one }

```python
IteratorResult.scalar_one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one`](#result-scalar-one)-এর মতো।

### `IteratorResult.scalar_one_or_none()` { #iteratorresult-scalar-one-or-none }

```python
IteratorResult.scalar_one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one_or_none`](#result-scalar-one-or-none)-এর মতো।

### `IteratorResult.scalars()` { #iteratorresult-scalars }

```python
IteratorResult.scalars(index=0)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalars`](#result-scalars)-এর মতো।

### `IteratorResult.t` { #iteratorresult-t }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.t`](#result-t)-এর মতো।

### `IteratorResult.tuples()` { #iteratorresult-tuples }

```python
IteratorResult.tuples()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.tuples`](#result-tuples)-এর মতো।

### `IteratorResult.unique()` { #iteratorresult-unique }

```python
IteratorResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো।

### `IteratorResult.yield_per()` { #iteratorresult-yield-per }

```python
IteratorResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

## `ChunkedIteratorResult` { #chunkediteratorresult }

```python
from sqlalchemy.engine import ChunkedIteratorResult
```

টুকরো টুকরো (chunk) করে রো আনে এমন `IteratorResult`; `yield_per` দিলে ORM এটি ব্যবহার করে। আচরণ `Result`-এর মতো।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #chunkediteratorresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#chunkediteratorresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#chunkediteratorresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#chunkediteratorresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#chunkediteratorresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#chunkediteratorresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#chunkediteratorresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#chunkediteratorresult-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#chunkediteratorresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#chunkediteratorresult-freeze) | মেথড | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`keys()`](#chunkediteratorresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`mappings()`](#chunkediteratorresult-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#chunkediteratorresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#chunkediteratorresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`merge()`](#chunkediteratorresult-merge) | মেথড | একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে। |
| [`one()`](#chunkediteratorresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#chunkediteratorresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#chunkediteratorresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`scalar()`](#chunkediteratorresult-scalar) | মেথড | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#chunkediteratorresult-scalar-one) | মেথড | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#chunkediteratorresult-scalar-one-or-none) | মেথড | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#chunkediteratorresult-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`t`](#chunkediteratorresult-t) | প্রপার্টি | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#chunkediteratorresult-tuples) | মেথড | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#chunkediteratorresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#chunkediteratorresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `ChunkedIteratorResult.all()` { #chunkediteratorresult-all }

```python
ChunkedIteratorResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো।

### `ChunkedIteratorResult.close()` { #chunkediteratorresult-close }

```python
ChunkedIteratorResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `ChunkedIteratorResult.closed` { #chunkediteratorresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `ChunkedIteratorResult.columns()` { #chunkediteratorresult-columns }

```python
ChunkedIteratorResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](#result-columns)-এর মতো।

### `ChunkedIteratorResult.fetchall()` { #chunkediteratorresult-fetchall }

```python
ChunkedIteratorResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো।

### `ChunkedIteratorResult.fetchmany()` { #chunkediteratorresult-fetchmany }

```python
ChunkedIteratorResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো।

### `ChunkedIteratorResult.fetchone()` { #chunkediteratorresult-fetchone }

```python
ChunkedIteratorResult.fetchone()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchone`](#result-fetchone)-এর মতো।

### `ChunkedIteratorResult.first()` { #chunkediteratorresult-first }

```python
ChunkedIteratorResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো।

### `ChunkedIteratorResult.freeze()` { #chunkediteratorresult-freeze }

```python
ChunkedIteratorResult.freeze()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.freeze`](#result-freeze)-এর মতো।

### `ChunkedIteratorResult.keys()` { #chunkediteratorresult-keys }

```python
ChunkedIteratorResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](#result-keys)-এর মতো।

### `ChunkedIteratorResult.mappings()` { #chunkediteratorresult-mappings }

```python
ChunkedIteratorResult.mappings()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.mappings`](#result-mappings)-এর মতো।

### `ChunkedIteratorResult.memoized_attribute` { #chunkediteratorresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `ChunkedIteratorResult.memoized_instancemethod()` { #chunkediteratorresult-memoized-instancemethod }

```python
ChunkedIteratorResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `ChunkedIteratorResult.merge()` { #chunkediteratorresult-merge }

```python
ChunkedIteratorResult.merge(*others)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.merge`](#result-merge)-এর মতো।

### `ChunkedIteratorResult.one()` { #chunkediteratorresult-one }

```python
ChunkedIteratorResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো।

### `ChunkedIteratorResult.one_or_none()` { #chunkediteratorresult-one-or-none }

```python
ChunkedIteratorResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো।

### `ChunkedIteratorResult.partitions()` { #chunkediteratorresult-partitions }

```python
ChunkedIteratorResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো।

### `ChunkedIteratorResult.scalar()` { #chunkediteratorresult-scalar }

```python
ChunkedIteratorResult.scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar`](#result-scalar)-এর মতো।

### `ChunkedIteratorResult.scalar_one()` { #chunkediteratorresult-scalar-one }

```python
ChunkedIteratorResult.scalar_one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one`](#result-scalar-one)-এর মতো।

### `ChunkedIteratorResult.scalar_one_or_none()` { #chunkediteratorresult-scalar-one-or-none }

```python
ChunkedIteratorResult.scalar_one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one_or_none`](#result-scalar-one-or-none)-এর মতো।

### `ChunkedIteratorResult.scalars()` { #chunkediteratorresult-scalars }

```python
ChunkedIteratorResult.scalars(index=0)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalars`](#result-scalars)-এর মতো।

### `ChunkedIteratorResult.t` { #chunkediteratorresult-t }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.t`](#result-t)-এর মতো।

### `ChunkedIteratorResult.tuples()` { #chunkediteratorresult-tuples }

```python
ChunkedIteratorResult.tuples()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.tuples`](#result-tuples)-এর মতো।

### `ChunkedIteratorResult.unique()` { #chunkediteratorresult-unique }

```python
ChunkedIteratorResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো।

### `ChunkedIteratorResult.yield_per()` { #chunkediteratorresult-yield-per }

```python
ChunkedIteratorResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

## `MergedResult` { #mergedresult }

```python
from sqlalchemy.engine import MergedResult
```

`Result.merge()` থেকে পাওয়া, কয়েকটি Result জুড়ে বানানো ফলাফল। আচরণ `Result`-এর মতো।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mergedresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#mergedresult-all) | মেথড | বাকি থাকা সব রো একটি তালিকায় দেয়, আর Result শেষ করে দেয়। |
| [`close()`](#mergedresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#mergedresult-closed) | অ্যাট্রিবিউট | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`columns()`](#mergedresult-columns) | মেথড | প্রতিটি রো-তে কোন কলাম কোন ক্রমে থাকবে তা নতুন করে ঠিক করে, নাম বা অবস্থান (index) দিয়ে। |
| [`fetchall()`](#mergedresult-fetchall) | মেথড | `all()`-এর পুরোনো নাম (DBAPI ধাঁচ)। |
| [`fetchmany()`](#mergedresult-fetchmany) | মেথড | পরের `size`-টি রো দেয়। |
| [`fetchone()`](#mergedresult-fetchone) | মেথড | পরের একটি রো দেয়, শেষ হলে `None`। |
| [`first()`](#mergedresult-first) | মেথড | প্রথম রো দেয় (না থাকলে `None`), আর বাকি সব বাদ দিয়ে Result বন্ধ করে দেয়। |
| [`freeze()`](#mergedresult-freeze) | মেথড | ফলাফলের একটি "জমানো" কপি (`FrozenResult`) বানায়, যেটা ডেকে যতবার খুশি নতুন Result পাওয়া যায়। |
| [`keys()`](#mergedresult-keys) | মেথড | প্রতিটি রো-র কলামের নামগুলো দেয়। |
| [`mappings()`](#mergedresult-mappings) | মেথড | রো-গুলোকে dict-এর মতো `RowMapping` হিসেবে দেওয়ার জন্য একটি `MappingResult` দেয়। |
| [`memoized_attribute`](#mergedresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#mergedresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`merge()`](#mergedresult-merge) | মেথড | একই কলামের কয়েকটি Result জুড়ে একটি Result বানায়, প্রথমটির রো শেষ হলে পরেরটির রো আসে। |
| [`one()`](#mergedresult-one) | মেথড | ঠিক একটি রো দেয়। |
| [`one_or_none()`](#mergedresult-one-or-none) | মেথড | শূন্য বা একটি রো দেয়: না থাকলে `None`, একাধিক হলে `MultipleResultsFound`। |
| [`partitions()`](#mergedresult-partitions) | মেথড | রো-গুলোকে `size` আকারের টুকরোয় ভাগ করে একটি একটি টুকরো দেয়। |
| [`scalar()`](#mergedresult-scalar) | মেথড | প্রথম রো-র প্রথম কলামের মান দেয় (না থাকলে `None`) আর Result বন্ধ করে। |
| [`scalar_one()`](#mergedresult-scalar-one) | মেথড | ঠিক একটি রো-র প্রথম কলাম দেয়। |
| [`scalar_one_or_none()`](#mergedresult-scalar-one-or-none) | মেথড | শূন্য বা একটি রো-র প্রথম কলাম: না থাকলে `None`, একাধিক হলে এরর। |
| [`scalars()`](#mergedresult-scalars) | মেথড | প্রতিটি রো থেকে শুধু একটি কলাম (ডিফল্টে প্রথমটি) নিয়ে `ScalarResult` দেয়। |
| [`t`](#mergedresult-t) | প্রপার্টি | টাইপ চেকারের জন্য রো-গুলোকে "typed tuple" হিসেবে চিহ্নিত করার পুরোনো উপায়। |
| [`tuples()`](#mergedresult-tuples) | মেথড | `t`-এর মেথড রূপ; একইভাবে ২.১-এ বাতিলের পথে। |
| [`unique()`](#mergedresult-unique) | মেথড | একই রো (বা একই অবজেক্ট) একাধিকবার এলে একবারই রাখে। |
| [`yield_per()`](#mergedresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `MergedResult.all()` { #mergedresult-all }

```python
MergedResult.all()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.all`](#result-all)-এর মতো।

### `MergedResult.close()` { #mergedresult-close }

```python
MergedResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `MergedResult.closed` { #mergedresult-closed }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `MergedResult.columns()` { #mergedresult-columns }

```python
MergedResult.columns(*col_expressions)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.columns`](#result-columns)-এর মতো।

### `MergedResult.fetchall()` { #mergedresult-fetchall }

```python
MergedResult.fetchall()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchall`](#result-fetchall)-এর মতো।

### `MergedResult.fetchmany()` { #mergedresult-fetchmany }

```python
MergedResult.fetchmany(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchmany`](#result-fetchmany)-এর মতো।

### `MergedResult.fetchone()` { #mergedresult-fetchone }

```python
MergedResult.fetchone()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.fetchone`](#result-fetchone)-এর মতো।

### `MergedResult.first()` { #mergedresult-first }

```python
MergedResult.first()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.first`](#result-first)-এর মতো।

### `MergedResult.freeze()` { #mergedresult-freeze }

```python
MergedResult.freeze()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.freeze`](#result-freeze)-এর মতো।

### `MergedResult.keys()` { #mergedresult-keys }

```python
MergedResult.keys()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.keys`](#result-keys)-এর মতো।

### `MergedResult.mappings()` { #mergedresult-mappings }

```python
MergedResult.mappings()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.mappings`](#result-mappings)-এর মতো।

### `MergedResult.memoized_attribute` { #mergedresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `MergedResult.memoized_instancemethod()` { #mergedresult-memoized-instancemethod }

```python
MergedResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `MergedResult.merge()` { #mergedresult-merge }

```python
MergedResult.merge(*others)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.merge`](#result-merge)-এর মতো।

### `MergedResult.one()` { #mergedresult-one }

```python
MergedResult.one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one`](#result-one)-এর মতো।

### `MergedResult.one_or_none()` { #mergedresult-one-or-none }

```python
MergedResult.one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.one_or_none`](#result-one-or-none)-এর মতো।

### `MergedResult.partitions()` { #mergedresult-partitions }

```python
MergedResult.partitions(size=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.partitions`](#result-partitions)-এর মতো।

### `MergedResult.scalar()` { #mergedresult-scalar }

```python
MergedResult.scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar`](#result-scalar)-এর মতো।

### `MergedResult.scalar_one()` { #mergedresult-scalar-one }

```python
MergedResult.scalar_one()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one`](#result-scalar-one)-এর মতো।

### `MergedResult.scalar_one_or_none()` { #mergedresult-scalar-one-or-none }

```python
MergedResult.scalar_one_or_none()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalar_one_or_none`](#result-scalar-one-or-none)-এর মতো।

### `MergedResult.scalars()` { #mergedresult-scalars }

```python
MergedResult.scalars(index=0)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.scalars`](#result-scalars)-এর মতো।

### `MergedResult.t` { #mergedresult-t }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.t`](#result-t)-এর মতো।

### `MergedResult.tuples()` { #mergedresult-tuples }

```python
MergedResult.tuples()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.tuples`](#result-tuples)-এর মতো।

### `MergedResult.unique()` { #mergedresult-unique }

```python
MergedResult.unique(strategy=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.unique`](#result-unique)-এর মতো।

### `MergedResult.yield_per()` { #mergedresult-yield-per }

```python
MergedResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

## `FilterResult` { #filterresult }

```python
from sqlalchemy.engine.result import FilterResult
```

`ScalarResult`, `MappingResult` ইত্যাদির সাধারণ বেস ক্লাস (অভ্যন্তরীণ)। এর সব মেথড `Result`-এর মতোই।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #filterresult-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#filterresult-close) | মেথড | Result পুরোপুরি বন্ধ করে, ভেতরের cursor ছেড়ে দেয়। |
| [`closed`](#filterresult-closed) | প্রপার্টি | `close()` দিয়ে বন্ধ করা হলে `True`। |
| [`memoized_attribute`](#filterresult-memoized-attribute) | অ্যাট্রিবিউট | SQLAlchemy-র ভেতরের একটি ডেকোরেটর (একবার হিসাব করে মান মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#filterresult-memoized-instancemethod) | ক্লাস মেথড | ভেতরের আরেকটি ডেকোরেটর (মেথডের ফল মনে রাখে)। |
| [`yield_per()`](#filterresult-yield-per) | মেথড | ডেটাবেস থেকে একবারে কতগুলো রো আনা হবে তা ঠিক করে (`num`)। |

### `FilterResult.close()` { #filterresult-close }

```python
FilterResult.close()
```

**ধরন:** মেথড

কাজ হুবহু [`Result.close`](#result-close)-এর মতো।

### `FilterResult.closed` { #filterresult-closed }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Result.closed`](#result-closed)-এর মতো।

### `FilterResult.memoized_attribute` { #filterresult-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Result.memoized_attribute`](#result-memoized-attribute)-এর মতো।

### `FilterResult.memoized_instancemethod()` { #filterresult-memoized-instancemethod }

```python
FilterResult.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Result.memoized_instancemethod`](#result-memoized-instancemethod)-এর মতো।

### `FilterResult.yield_per()` { #filterresult-yield-per }

```python
FilterResult.yield_per(num)
```

**ধরন:** মেথড

কাজ হুবহু [`Result.yield_per`](#result-yield-per)-এর মতো।

/// check | সংক্ষেপে মনে রাখুন

* অবজেক্ট বা একটি কলাম → `scalars()`; একাধিক কলাম → `Row` (নাম, index বা unpack দিয়ে পড়ুন); dict → `mappings()`।
* `one()` = ঠিক একটি, `one_or_none()` = শূন্য বা একটি, `first()` = প্রথমটি (বাকি বাদ), `all()` = সব।
* কালেকশনে `joinedload` থাকলে `.unique()` বাধ্যতামূলক।
* DML-এর পর `rowcount`, insert-এর পর `inserted_primary_key`।
* ২.১: `Row` সরাসরি tuple, তাই `.t`, `.tuples()`, `._t`, `._tuple()` এড়িয়ে চলুন।

///
