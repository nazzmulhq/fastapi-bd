# MetaData, Table ও Column API { #api-schema }

/// note | এই পেজে যা আছে

* `MetaData`: সব টেবিলের সংগ্রহ; `create_all()`, `drop_all()`, `reflect()`, `sorted_tables` …
* `Table`: টেবিলের **সব** সদস্য আর কনস্ট্রাক্টরের প্রতিটি প্যারামিটার।
* `Column`: কলামের **সব** সদস্য আর প্রতিটি প্যারামিটার (`nullable`, `default`, `server_default`, `onupdate`, `index`, `unique`, `autoincrement`, `comment` …)।
* `insert_sentinel()`, `sort_tables()`, `sort_tables_and_constraints()`, আর ২.১-এর নতুন `TypedColumns`, `Named`, `CheckFirst`।

///

ORM মডেলে (`DeclarativeBase`) আপনি সাধারণত সরাসরি `Table`/`Column` লেখেন না; `mapped_column()` ভেতরে একটি `Column` বানায় আর `__tablename__` থেকে একটি `Table` তৈরি হয় (`User.__table__`)। কিন্তু Core-ভিত্তিক কোড, Alembic মাইগ্রেশন, association table, আর রিফ্লেকশনে (বিদ্যমান ডেটাবেস থেকে টেবিল পড়া) এগুলোই মূল। `mapped_column()`-এর প্রায় সব প্যারামিটার আসলে নিচের `Column` প্যারামিটারগুলোতেই যায়।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
md = MetaData()

users = Table(
    "users", md,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False, index=True),
    Column("email", String(100), unique=True),
    Column("created_at", DateTime, server_default=func.now()),
    comment="অ্যাপের ইউজার",
)

addresses = Table(
    "addresses", md,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("city", String(50)),
)
```

`engine` একটি PostgreSQL 16 ইঞ্জিন। প্রতিটি উদাহরণ খালি ডেটাবেসে আলাদাভাবে চালিয়ে দেখা; যেখানে টেবিল লাগে সেখানে আগে `md.create_all(engine)` ডাকা হয়েছে।

///

## `MetaData` { #metadata }

```python
from sqlalchemy import MetaData
```

টেবিল (আর sequence, enum টাইপ ইত্যাদি) সংজ্ঞাগুলোর **সংগ্রহ**। একটি অ্যাপে সাধারণত একটিই থাকে; ORM-এ `Base.metadata`। এখান থেকে সব টেবিল একসাথে তৈরি/মোছা যায়, ফরেন কি অনুযায়ী সাজানো যায়, আর Alembic `target_metadata` হিসেবে এটাই নেয়।

**উদাহরণ:**

```python
print(list(md.tables))                       # ['users', 'addresses']
md.create_all(engine)
print(sorted(inspect(engine).get_table_names()))   # ['addresses', 'users']
```

### কনস্ট্রাক্টরের প্যারামিটার { #metadata-params }

```python
MetaData(schema=None, quote_schema=None, naming_convention=None, info=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `schema` | এই MetaData-র সব টেবিলের ডিফল্ট স্কিমা (PostgreSQL-এ যেমন `"app"`)। টেবিলে নিজস্ব `schema=` দিলে সেটাই চলে। |
| `quote_schema` | স্কিমার নাম জোর করে quote হবে কি না। |
| `naming_convention` | কনস্ট্রেইন্ট ও ইনডেক্সের নাম বানানোর নিয়ম (dict), যেমন `{"ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s", "fk": ..., "pk": ...}`। Alembic-এ নামহীন কনস্ট্রেইন্ট মোছা/বদলানোর ঝামেলা এড়াতে **অবশ্যই** দিন। |
| `info` | নিজের মেটাডেটা রাখার dict। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #metadata-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`clear()`](#metadata-clear) | মেথড | এই MetaData থেকে সব টেবিল সরিয়ে দেয় (শুধু Python দিক থেকে; ডেটাবেসে কিছু হয় না)। |
| [`create_all()`](#metadata-create-all) | মেথড | সব টেবিল (আর তাদের ইনডেক্স, sequence, enum টাইপ) ফরেন কি-র সঠিক ক্রমে তৈরি করে। |
| [`create_drop_stringify_dialect`](#metadata-create-drop-stringify-dialect) | অ্যাট্রিবিউট (internal) | DDL অবজেক্টকে `str()` করার সময় কোন ডায়ালেক্ট ব্যবহার হবে (`"default"`)। |
| [`drop_all()`](#metadata-drop-all) | মেথড | সব টেবিল উল্টো নির্ভরতা-ক্রমে মুছে ফেলে (আগে সন্তান টেবিল, পরে প্যারেন্ট)। |
| [`get_schema_object_by_name()`](#metadata-get-schema-object-by-name) | মেথড | নাম আর ধরন দিয়ে MetaData-তে নিবন্ধিত একটি স্কিমা-অবজেক্ট খোঁজে, যেমন নাম দিয়ে একটি `Sequence` বা named `Enum` টাইপ। |
| [`get_schema_objects()`](#metadata-get-schema-objects) | মেথড | নির্দিষ্ট ধরনের (`Sequence`, `Enum` …) সব নিবন্ধিত স্কিমা-অবজেক্টের তালিকা দেয়; `schema=` দিয়ে স্কিমা অনুযায়ী ছাঁকা যায়। |
| [`info`](#metadata-info) | প্রপার্টি | নিজের মেটাডেটা রাখার dict (SQLAlchemy নিজে ব্যবহার করে না)। |
| [`naming_convention`](#metadata-naming-convention) | অ্যাট্রিবিউট | কনস্ট্রেইন্ট/ইনডেক্সের নাম বানানোর নিয়মের dict (কনস্ট্রাক্টরে দেওয়া)। |
| [`reflect()`](#metadata-reflect) | মেথড | ডেটাবেসে **বিদ্যমান** টেবিলগুলো পড়ে এই MetaData-তে `Table` অবজেক্ট হিসেবে বসায় (কলাম, টাইপ, কনস্ট্রেইন্ট, ইনডেক্সসহ)। |
| [`remove()`](#metadata-remove) | মেথড | একটি টেবিল এই MetaData থেকে সরায় (শুধু Python দিক থেকে)। |
| [`schema`](#metadata-schema) | অ্যাট্রিবিউট | কনস্ট্রাক্টরে দেওয়া ডিফল্ট স্কিমা। |
| [`schemas`](#metadata-schemas) | প্রপার্টি | এই MetaData-র টেবিলগুলোতে যত স্কিমার নাম আছে তার তালিকা। |
| [`sorted_tables`](#metadata-sorted-tables) | প্রপার্টি | টেবিলগুলো ফরেন কি নির্ভরতা অনুযায়ী সাজানো: আগে প্যারেন্ট, পরে সন্তান। |
| [`tables`](#metadata-tables) | অ্যাট্রিবিউট | টেবিলের নাম (স্কিমা থাকলে `schema.name`) → `Table`-এর dict। |

### `MetaData.clear()` { #metadata-clear }

```python
MetaData.clear()
```

**ধরন:** মেথড

এই MetaData থেকে সব টেবিল সরিয়ে দেয় (শুধু Python দিক থেকে; ডেটাবেসে কিছু হয় না)।

**উদাহরণ:**

```python
m = MetaData()
Table("t1", m, Column("id", Integer, primary_key=True))
m.clear()
print(len(m.tables))   # 0
```

### `MetaData.create_all()` { #metadata-create-all }

```python
MetaData.create_all(bind, tables=None, checkfirst=<CheckFirst.ALL: 62>)
```

**ধরন:** মেথড

সব টেবিল (আর তাদের ইনডেক্স, sequence, enum টাইপ) ফরেন কি-র সঠিক ক্রমে তৈরি করে। ডিফল্টে আগে দেখে নেয় কোনটা আছে, যেগুলো আছে সেগুলো বাদ দেয়। **এটি মাইগ্রেশন নয়**: বিদ্যমান টেবিলে নতুন কলাম যোগ করে না; প্রোডাকশনে Alembic ব্যবহার করুন। `tables=[...]` দিয়ে শুধু কিছু টেবিল, আর `checkfirst=` দিয়ে কী কী আগে যাচাই হবে (২.১-এ `CheckFirst` flag-ও নেয়)।

**উদাহরণ:**

```python
md.create_all(engine)
md.create_all(engine)   # দ্বিতীয়বার: কিছুই হয় না, কারণ টেবিল আগে থেকেই আছে
print(sorted(inspect(engine).get_table_names()))   # ['addresses', 'users']
```

### `MetaData.create_drop_stringify_dialect` { #metadata-create-drop-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DDL অবজেক্টকে `str()` করার সময় কোন ডায়ালেক্ট ব্যবহার হবে (`"default"`)।

### `MetaData.drop_all()` { #metadata-drop-all }

```python
MetaData.drop_all(bind, tables=None, checkfirst=<CheckFirst.ALL: 62>)
```

**ধরন:** মেথড

সব টেবিল উল্টো নির্ভরতা-ক্রমে মুছে ফেলে (আগে সন্তান টেবিল, পরে প্যারেন্ট)। টেস্ট শেষে পরিষ্কার করতে কাজে লাগে।

**উদাহরণ:**

```python
md.create_all(engine)
md.drop_all(engine)
print(inspect(engine).get_table_names())   # []
```

### `MetaData.get_schema_object_by_name()` { #metadata-get-schema-object-by-name }

```python
MetaData.get_schema_object_by_name(kind, name, *, schema=_NoArg.NO_ARG)
```

**ধরন:** মেথড

নাম আর ধরন দিয়ে MetaData-তে নিবন্ধিত একটি স্কিমা-অবজেক্ট খোঁজে, যেমন নাম দিয়ে একটি `Sequence` বা named `Enum` টাইপ। না পেলে `None`।

**উদাহরণ:**

```python
m = MetaData()
Sequence("invoice_seq", metadata=m)
print(m.get_schema_object_by_name(Sequence, "invoice_seq").name)   # invoice_seq
```

### `MetaData.get_schema_objects()` { #metadata-get-schema-objects }

```python
MetaData.get_schema_objects(kind, *, schema=_NoArg.NO_ARG)
```

**ধরন:** মেথড

নির্দিষ্ট ধরনের (`Sequence`, `Enum` …) সব নিবন্ধিত স্কিমা-অবজেক্টের তালিকা দেয়; `schema=` দিয়ে স্কিমা অনুযায়ী ছাঁকা যায়।

**উদাহরণ:**

```python
m = MetaData()
Sequence("a_seq", metadata=m); Sequence("b_seq", metadata=m)
print(sorted(s.name for s in m.get_schema_objects(Sequence)))   # ['a_seq', 'b_seq']
```

### `MetaData.info` { #metadata-info }

**ধরন:** প্রপার্টি

নিজের মেটাডেটা রাখার dict (SQLAlchemy নিজে ব্যবহার করে না)।

**উদাহরণ:**

```python
print(MetaData(info={"app": "shop"}).info)   # {'app': 'shop'}
```

### `MetaData.naming_convention` { #metadata-naming-convention }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্ট/ইনডেক্সের নাম বানানোর নিয়মের dict (কনস্ট্রাক্টরে দেওয়া)।

**উদাহরণ:**

```python
m = MetaData(naming_convention={"uq": "uq_%(table_name)s_%(column_0_name)s"})
t = Table("tags", m, Column("id", Integer, primary_key=True), Column("slug", String(20), unique=True))
print([c.name for c in t.constraints if isinstance(c, UniqueConstraint)])   # ['uq_tags_slug']
```

### `MetaData.reflect()` { #metadata-reflect }

```python
MetaData.reflect(bind, schema=None, views=False, only=None, extend_existing=False, autoload_replace=True, resolve_fks=True, **dialect_kwargs)
```

**ধরন:** মেথড

ডেটাবেসে **বিদ্যমান** টেবিলগুলো পড়ে এই MetaData-তে `Table` অবজেক্ট হিসেবে বসায় (কলাম, টাইপ, কনস্ট্রেইন্ট, ইনডেক্সসহ)। পুরোনো ডেটাবেসে কোড লেখা বা স্ক্রিপ্টে কাজে লাগে। `only=[...]` দিয়ে কিছু টেবিল, `views=True` দিয়ে ভিউও।

**উদাহরণ:**

```python
md.create_all(engine)
m2 = MetaData()
m2.reflect(engine, only=["users"])
print([c.name for c in m2.tables["users"].c])   # ['id', 'name', 'email', 'created_at']
```

### `MetaData.remove()` { #metadata-remove }

```python
MetaData.remove(table)
```

**ধরন:** মেথড

একটি টেবিল এই MetaData থেকে সরায় (শুধু Python দিক থেকে)।

**উদাহরণ:**

```python
m = MetaData()
t = Table("tmp", m, Column("id", Integer, primary_key=True))
m.remove(t)
print("tmp" in m.tables)   # False
```

### `MetaData.schema` { #metadata-schema }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরে দেওয়া ডিফল্ট স্কিমা।

**উদাহরণ:**

```python
print(MetaData(schema="archive").schema)   # archive
```

### `MetaData.schemas` { #metadata-schemas }

**ধরন:** প্রপার্টি

এই MetaData-র টেবিলগুলোতে যত স্কিমার নাম আছে তার তালিকা।

**উদাহরণ:**

```python
m = MetaData()
Table("a", m, Column("id", Integer, primary_key=True), schema="archive")
print(m.schemas)   # ('archive',)
```

### `MetaData.sorted_tables` { #metadata-sorted-tables }

**ধরন:** প্রপার্টি

টেবিলগুলো ফরেন কি নির্ভরতা অনুযায়ী সাজানো: আগে প্যারেন্ট, পরে সন্তান। ডেটা কপি/লোডের সময় সঠিক ক্রমে INSERT করতে।

**উদাহরণ:**

```python
print([t.name for t in md.sorted_tables])   # ['users', 'addresses']
```

### `MetaData.tables` { #metadata-tables }

**ধরন:** অ্যাট্রিবিউট

টেবিলের নাম (স্কিমা থাকলে `schema.name`) → `Table`-এর dict।

**উদাহরণ:**

```python
print(md.tables["users"] is users)   # True
```

## `Table` { #table }

```python
from sqlalchemy import Table
```

ডেটাবেসের একটি টেবিলের সংজ্ঞা: নাম, কলাম, কনস্ট্রেইন্ট, ইনডেক্স। প্রথম দুটি আর্গুমেন্ট নাম আর `MetaData`, তারপর যেকোনো ক্রমে `Column`, `Constraint`, `Index`। একই MetaData-তে একই নামে দ্বিতীয়বার `Table()` ডাকলে আগেরটিই ফেরত আসে (নতুন কলাম দিলে এরর, যদি না `extend_existing=True`)। ORM মডেলের টেবিল: `User.__table__`।

**উদাহরণ:**

```python
print(users.name, [c.name for c in users.c])   # users ['id', 'name', 'email', 'created_at']
md.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(users), [{"name": "রহিম"}, {"name": "করিম"}])
    print(conn.execute(select(users.c.name).order_by(users.c.id)).scalars().all())   # ['রহিম', 'করিম']
```

### কনস্ট্রাক্টরের প্যারামিটার { #table-params }

```python
Table(name, metadata, /, *args, schema=None, quote=None, quote_schema=None, autoload_with=None, autoload_replace=True, keep_existing=False, extend_existing=False, resolve_fks=True, include_columns=None, implicit_returning=True, comment=None, info=None, listeners=None, prefixes=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | টেবিলের নাম (ডেটাবেসে যেমন থাকবে)। |
| `metadata` | যে `MetaData`-তে টেবিলটি থাকবে। |
| `args` | `Column`, `Constraint` (`PrimaryKeyConstraint`, `UniqueConstraint`, `CheckConstraint`, `ForeignKeyConstraint`), `Index`; যেকোনো ক্রমে। |
| `schema` | টেবিলের স্কিমা (না দিলে `MetaData.schema`, সেটাও না থাকলে ডেটাবেসের ডিফল্ট)। MetaData-র স্কিমা উপেক্ষা করতে `BLANK_SCHEMA`। |
| `quote` | টেবিলের নাম জোর করে quote হবে (`True`) বা হবে না (`False`)। ডিফল্টে বড় হাতের অক্ষর বা reserved word থাকলে নিজে থেকে quote হয়। |
| `quote_schema` | স্কিমার নামের জন্য একই। |
| `autoload_with` | একটি `Engine`/`Connection` দিলে কলামগুলো ডেটাবেস থেকে পড়ে নেয় (reflection)। |
| `autoload_replace` | reflection-এর সময় আগে থেকে থাকা কলামকে ডেটাবেসের কলাম দিয়ে বদলাবে কি না (ডিফল্ট `True`)। |
| `keep_existing` | টেবিলটি MetaData-তে আগেই থাকলে নতুন আর্গুমেন্টগুলো উপেক্ষা করে আগেরটি ফেরত দেয়। |
| `extend_existing` | টেবিলটি আগেই থাকলে নতুন কলাম/অপশনগুলো তার সাথে যোগ করে (বা বদলায়)। |
| `resolve_fks` | reflection-এর সময় ফরেন কি দিয়ে যুক্ত অন্য টেবিলগুলোও পড়বে কি না (ডিফল্ট `True`)। |
| `include_columns` | reflection-এ শুধু এই নামের কলামগুলো আনবে। |
| `implicit_returning` | INSERT-এর পর নতুন primary key আনতে `RETURNING` ব্যবহার করবে কি না (ডিফল্ট `True`); trigger-এর কারণে RETURNING সমস্যা করলে `False`। |
| `comment` | টেবিলের SQL comment (`COMMENT ON TABLE`), DDL-এ বসে। |
| `info` | নিজের মেটাডেটার dict। |
| `listeners` | `[(event_name, fn), ...]`: টেবিল বানানোর সময়েই event listener যুক্ত করে (যেমন reflection-এর `column_reflect`)। |
| `prefixes` | `CREATE` আর `TABLE`-এর মাঝে বসা শব্দ, যেমন `["TEMPORARY"]` বা `["UNLOGGED"]`। |
| `kw` | `must_exist=True` (টেবিল আগে না থাকলে এরর), আর ডায়ালেক্ট-নির্দিষ্ট অপশন `ডায়ালেক্ট_অপশন` রূপে, যেমন `postgresql_partition_by="RANGE (created_at)"`, `mysql_engine="InnoDB"`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #table-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_is_dependent_on()`](#table-add-is-dependent-on) | মেথড | ফরেন কি না থাকলেও এই টেবিলকে অন্য একটি টেবিলের ওপর "নির্ভরশীল" ঘোষণা করে, যাতে `create_all()`/`sorted_tables`-এ সেটির পরে আসে। |
| [`alias()`](#table-alias) | মেথড | টেবিলের ছদ্মনাম (`users AS u2`), একই টেবিল কুয়েরিতে দুবার ব্যবহারের জন্য। |
| [`append_column()`](#table-append-column) | মেথড | টেবিলে একটি নতুন কলাম যোগ করে (শুধু Python সংজ্ঞায়; ডেটাবেসে `ALTER TABLE` চলে না)। |
| [`append_constraint()`](#table-append-constraint) | মেথড | টেবিলে একটি কনস্ট্রেইন্ট বা ইনডেক্স যোগ করে (Python সংজ্ঞায়)। |
| [`argument_for()`](#table-argument-for) | ক্লাস মেথড (internal) | (ক্লাস মেথড) এই ধরনের অবজেক্টে নতুন একটি ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে; থার্ড-পার্টি ডায়ালেক্ট বানালে লাগে। |
| [`autoincrement_column`](#table-autoincrement-column) | প্রপার্টি | যে কলামটি "auto increment" হিসেবে ধরা হচ্ছে (সাধারণত পূর্ণসংখ্যার একক primary key), না থাকলে `None`। |
| [`c`](#table-c) | প্রপার্টি | `columns`-এর ছোট নাম: নাম দিয়ে কলাম পাওয়া, `users.c.name` বা `users.c["name"]`। |
| [`columns`](#table-columns) | প্রপার্টি | টেবিলের সব কলামের সংগ্রহ (`ColumnCollection`), যোগ করার ক্রমে। |
| [`comment`](#table-comment) | অ্যাট্রিবিউট | টেবিলের SQL comment। |
| [`constraints`](#table-constraints) | অ্যাট্রিবিউট | টেবিলের সব কনস্ট্রেইন্টের সেট (primary key, unique, check, foreign key)। |
| [`create()`](#table-create) | মেথড | শুধু এই টেবিলের `CREATE TABLE` (আর তার ইনডেক্স) চালায়। |
| [`create_drop_stringify_dialect`](#table-create-drop-stringify-dialect) | অ্যাট্রিবিউট (internal) | DDL `str()` করার সময়ের ডায়ালেক্ট নাম। |
| [`delete()`](#table-delete) | মেথড | এই টেবিলে একটি `DELETE` স্টেটমেন্ট বানায় (`delete(users)`-এর মতো)। |
| [`description`](#table-description) | প্রপার্টি | টেবিলের নাম (বর্ণনামূলক নাম হিসেবে)। |
| [`dialect_kwargs`](#table-dialect-kwargs) | প্রপার্টি | `postgresql_...`, `mysql_...` রূপে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশনগুলোর dict। |
| [`dialect_options`](#table-dialect-options) | প্রপার্টি | ডায়ালেক্ট-নির্দিষ্ট অপশন, ডায়ালেক্ট অনুযায়ী ভাগ করা: `t.dialect_options["postgresql"]["with"]`। |
| [`drop()`](#table-drop) | মেথড | শুধু এই টেবিলের `DROP TABLE` চালায়। |
| [`foreign_key_constraints`](#table-foreign-key-constraints) | প্রপার্টি | এই টেবিলের সব `ForeignKeyConstraint`-এর সেট। |
| [`foreign_keys`](#table-foreign-keys) | প্রপার্টি | এই টেবিলের সব `ForeignKey` অবজেক্টের সেট (প্রতিটি কলাম-স্তরের রেফারেন্স)। |
| [`fullname`](#table-fullname) | অ্যাট্রিবিউট | স্কিমাসহ পূর্ণ নাম (`archive.users`); স্কিমা না থাকলে শুধু নাম। |
| [`get_dialect_option()`](#table-get-dialect-option) | মেথড | একটি ডায়ালেক্টের নির্দিষ্ট অপশনের মান দেয়; ডায়ালেক্ট অপশনটি না চিনলে `else_`। |
| [`implicit_returning`](#table-implicit-returning) | অ্যাট্রিবিউট | INSERT-এ নতুন primary key আনতে `RETURNING` ব্যবহার করা হবে কি না। |
| [`indexes`](#table-indexes) | অ্যাট্রিবিউট | টেবিলের সব `Index`-এর সেট (`index=True` কলাম থেকে তৈরি গুলোসহ)। |
| [`info`](#table-info) | প্রপার্টি | নিজের মেটাডেটার dict। |
| [`insert()`](#table-insert) | মেথড | এই টেবিলে একটি `INSERT` স্টেটমেন্ট বানায়। |
| [`insert_column()`](#table-insert-column) | মেথড | (২.১-এ নতুন) একটি কলাম নির্দিষ্ট অবস্থানে (index) ঢোকায়, শুধু শেষে নয়। |
| [`is_view`](#table-is-view) | প্রপার্টি | (২.১-এ নতুন) এই `Table` তৈরি করলে `CREATE TABLE`-এর বদলে `CREATE VIEW` হবে কি না (`CreateView` দিয়ে বানানো হলে `True`)। |
| [`join()`](#table-join) | মেথড | আরেকটি টেবিলের সাথে `JOIN`; ON শর্ত না দিলে ফরেন কি থেকে বোঝে। |
| [`key`](#table-key) | প্রপার্টি | MetaData-র `tables` dict-এ টেবিলটির key: স্কিমা থাকলে `schema.name`, না হলে নাম। |
| [`kwargs`](#table-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`metadata`](#table-metadata) | অ্যাট্রিবিউট | টেবিলটি যে `MetaData`-তে আছে। |
| [`name`](#table-name) | অ্যাট্রিবিউট | টেবিলের নাম (স্কিমা ছাড়া)। |
| [`outerjoin()`](#table-outerjoin) | মেথড | `LEFT OUTER JOIN`। |
| [`primary_key`](#table-primary-key) | প্রপার্টি | টেবিলের `PrimaryKeyConstraint`; `.columns` দিয়ে primary key কলামগুলো। |
| [`reflect_only_elements`](#table-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) reflection-এ ডেটাবেস থেকে পাওয়া এমন ডায়ালেক্ট-নির্দিষ্ট তথ্য, যা DDL-এ ব্যবহার হয় না (শুধু পড়ার জন্য), ডায়ালেক্ট অনুযায়ী ভাগ করা। |
| [`schema`](#table-schema) | অ্যাট্রিবিউট | টেবিলের স্কিমা (না থাকলে `None`)। |
| [`select()`](#table-select) | মেথড | `select(টেবিল)`-এর ছোট রূপ: সব কলাম SELECT। |
| [`set_creator_ddl()`](#table-set-creator-ddl) | মেথড | (২.১-এ নতুন) `create()`/`create_all()`-এ এই টেবিলের জন্য কোন CREATE স্টেটমেন্ট চলবে তা বদলে দেয়, যেমন `CreateTable(t, if_not_exists=True)`। |
| [`set_dropper_ddl()`](#table-set-dropper-ddl) | মেথড | (২.১-এ নতুন) `drop()`/`drop_all()`-এ কোন DROP স্টেটমেন্ট চলবে তা বদলায়, যেমন `DropTable(t, if_exists=True)`। |
| [`table_valued()`](#table-table-valued) | মেথড | পুরো রো-কে একটি কলাম হিসেবে ব্যবহার করার এক্সপ্রেশন (PostgreSQL-এ `SELECT users FROM users` → রো-টাইপ মান)। |
| [`to_metadata()`](#table-to-metadata) | মেথড | টেবিলের একটি কপি আরেকটি `MetaData`-তে বানায় (কলাম, কনস্ট্রেইন্ট, ইনডেক্সসহ); `schema=` দিয়ে ভিন্ন স্কিমায়, `name=` দিয়ে ভিন্ন নামে। |
| [`tometadata()`](#table-tometadata) | মেথড ⚠️ deprecated | `to_metadata()`-এর পুরোনো নাম (১.৪ থেকে বাতিলের পথে)। |
| [`update()`](#table-update) | মেথড | এই টেবিলে একটি `UPDATE` স্টেটমেন্ট বানায়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Table`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](fromclause.md#fromclause-corresponding-column) · [`entity_namespace`](fromclause.md#fromclause-entity-namespace) · [`exported_columns`](fromclause.md#fromclause-exported-columns) · [`is_derived_from()`](fromclause.md#fromclause-is-derived-from) · [`lateral()`](fromclause.md#fromclause-lateral) · [`named_with_column`](fromclause.md#fromclause-named-with-column) · [`replace_selectable()`](fromclause.md#fromclause-replace-selectable) · [`selectable`](fromclause.md#fromclause-selectable) · [`tablesample()`](fromclause.md#fromclause-tablesample) · [`with_cols()`](fromclause.md#fromclause-with-cols)

///

### `Table.add_is_dependent_on()` { #table-add-is-dependent-on }

```python
Table.add_is_dependent_on(table)
```

**ধরন:** মেথড

ফরেন কি না থাকলেও এই টেবিলকে অন্য একটি টেবিলের ওপর "নির্ভরশীল" ঘোষণা করে, যাতে `create_all()`/`sorted_tables`-এ সেটির পরে আসে।

**উদাহরণ:**

```python
m = MetaData()
a = Table("a", m, Column("id", Integer, primary_key=True))
b = Table("b", m, Column("id", Integer, primary_key=True))
a.add_is_dependent_on(b)
print([t.name for t in m.sorted_tables])   # ['b', 'a']
```

### `Table.alias()` { #table-alias }

```python
Table.alias(name=None, flat=False)
```

**ধরন:** মেথড

টেবিলের ছদ্মনাম (`users AS u2`), একই টেবিল কুয়েরিতে দুবার ব্যবহারের জন্য।

**উদাহরণ:**

```python
u2 = users.alias("u2")
print(select(u2.c.name))   # SELECT u2.name FROM users AS u2
```

### `Table.append_column()` { #table-append-column }

```python
Table.append_column(column, *, replace_existing=False)
```

**ধরন:** মেথড

টেবিলে একটি নতুন কলাম যোগ করে (শুধু Python সংজ্ঞায়; ডেটাবেসে `ALTER TABLE` চলে না)। `replace_existing=True` দিলে একই নামের কলাম বদলায়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("t", m, Column("id", Integer, primary_key=True))
t.append_column(Column("note", String(20)))
print(list(t.c.keys()))   # ['id', 'note']
```

### `Table.append_constraint()` { #table-append-constraint }

```python
Table.append_constraint(constraint)
```

**ধরন:** মেথড

টেবিলে একটি কনস্ট্রেইন্ট বা ইনডেক্স যোগ করে (Python সংজ্ঞায়)।

**উদাহরণ:**

```python
m = MetaData()
t = Table("t", m, Column("id", Integer, primary_key=True), Column("qty", Integer))
t.append_constraint(CheckConstraint("qty >= 0", name="ck_qty"))
ddl(t)
# CREATE TABLE t (
# 	id SERIAL NOT NULL,
# 	qty INTEGER,
# 	PRIMARY KEY (id),
# 	CONSTRAINT ck_qty CHECK (qty >= 0)
# )
```

### `Table.argument_for()` { #table-argument-for }

```python
Table.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) এই ধরনের অবজেক্টে নতুন একটি ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে; থার্ড-পার্টি ডায়ালেক্ট বানালে লাগে।

### `Table.autoincrement_column` { #table-autoincrement-column }

**ধরন:** প্রপার্টি

যে কলামটি "auto increment" হিসেবে ধরা হচ্ছে (সাধারণত পূর্ণসংখ্যার একক primary key), না থাকলে `None`।

**উদাহরণ:**

```python
print(users.autoincrement_column.name)   # id
```

### `Table.c` { #table-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম: নাম দিয়ে কলাম পাওয়া, `users.c.name` বা `users.c["name"]`।

**উদাহরণ:**

```python
print(users.c.email.type, "name" in users.c)   # VARCHAR(100) True
```

### `Table.columns` { #table-columns }

**ধরন:** প্রপার্টি

টেবিলের সব কলামের সংগ্রহ (`ColumnCollection`), যোগ করার ক্রমে।

**উদাহরণ:**

```python
print(len(users.columns), users.columns[0].name)   # 4 id
```

### `Table.comment` { #table-comment }

**ধরন:** অ্যাট্রিবিউট

টেবিলের SQL comment।

**উদাহরণ:**

```python
print(users.comment)   # অ্যাপের ইউজার
```

### `Table.constraints` { #table-constraints }

**ধরন:** অ্যাট্রিবিউট

টেবিলের সব কনস্ট্রেইন্টের সেট (primary key, unique, check, foreign key)।

**উদাহরণ:**

```python
print(sorted(type(c).__name__ for c in users.constraints))   # ['PrimaryKeyConstraint', 'UniqueConstraint']
```

### `Table.create()` { #table-create }

```python
Table.create(bind, checkfirst=<CheckFirst.TYPES: 32>)
```

**ধরন:** মেথড

শুধু এই টেবিলের `CREATE TABLE` (আর তার ইনডেক্স) চালায়। `checkfirst=True` দিলে আগে দেখে নেয় আছে কি না।

**উদাহরণ:**

```python
users.create(engine)
users.create(engine, checkfirst=True)   # আছে, তাই কিছু হয় না
print(inspect(engine).has_table("users"))   # True
```

### `Table.create_drop_stringify_dialect` { #table-create-drop-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DDL `str()` করার সময়ের ডায়ালেক্ট নাম।

### `Table.delete()` { #table-delete }

```python
Table.delete()
```

**ধরন:** মেথড

এই টেবিলে একটি `DELETE` স্টেটমেন্ট বানায় (`delete(users)`-এর মতো)।

**উদাহরণ:**

```python
print(users.delete().where(users.c.id == 5))   # DELETE FROM users WHERE users.id = :id_1
```

### `Table.description` { #table-description }

**ধরন:** প্রপার্টি

টেবিলের নাম (বর্ণনামূলক নাম হিসেবে)।

**উদাহরণ:**

```python
print(users.description)   # users
```

### `Table.dialect_kwargs` { #table-dialect-kwargs }

**ধরন:** প্রপার্টি

`postgresql_...`, `mysql_...` রূপে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশনগুলোর dict।

**উদাহরণ:**

```python
t = Table("logs", MetaData(), Column("id", Integer, primary_key=True), prefixes=["UNLOGGED"],
          postgresql_with={"fillfactor": 70})
print(dict(t.dialect_kwargs))   # {'postgresql_with': {'fillfactor': 70}}
```

### `Table.dialect_options` { #table-dialect-options }

**ধরন:** প্রপার্টি

ডায়ালেক্ট-নির্দিষ্ট অপশন, ডায়ালেক্ট অনুযায়ী ভাগ করা: `t.dialect_options["postgresql"]["with"]`।

**উদাহরণ:**

```python
t = Table("logs", MetaData(), Column("id", Integer, primary_key=True), postgresql_with={"fillfactor": 70})
print(t.dialect_options["postgresql"]["with"])   # {'fillfactor': 70}
```

### `Table.drop()` { #table-drop }

```python
Table.drop(bind, checkfirst=<CheckFirst.NONE: 0>)
```

**ধরন:** মেথড

শুধু এই টেবিলের `DROP TABLE` চালায়। `checkfirst=True` দিলে না থাকলে এরর দেয় না।

**উদাহরণ:**

```python
users.create(engine)
users.drop(engine)
users.drop(engine, checkfirst=True)
print(inspect(engine).has_table("users"))   # False
```

### `Table.foreign_key_constraints` { #table-foreign-key-constraints }

**ধরন:** প্রপার্টি

এই টেবিলের সব `ForeignKeyConstraint`-এর সেট।

**উদাহরণ:**

```python
fk = next(iter(addresses.foreign_key_constraints))
print(fk.referred_table.name, fk.ondelete)   # users CASCADE
```

### `Table.foreign_keys` { #table-foreign-keys }

**ধরন:** প্রপার্টি

এই টেবিলের সব `ForeignKey` অবজেক্টের সেট (প্রতিটি কলাম-স্তরের রেফারেন্স)।

**উদাহরণ:**

```python
print([fk.target_fullname for fk in addresses.foreign_keys])   # ['users.id']
```

### `Table.fullname` { #table-fullname }

**ধরন:** অ্যাট্রিবিউট

স্কিমাসহ পূর্ণ নাম (`archive.users`); স্কিমা না থাকলে শুধু নাম।

**উদাহরণ:**

```python
t = Table("old_users", MetaData(), Column("id", Integer, primary_key=True), schema="archive")
print(t.fullname)   # archive.old_users
```

### `Table.get_dialect_option()` { #table-get-dialect-option }

```python
Table.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

একটি ডায়ালেক্টের নির্দিষ্ট অপশনের মান দেয়; ডায়ালেক্ট অপশনটি না চিনলে `else_`।

**উদাহরণ:**

```python
t = Table("logs", MetaData(), Column("id", Integer, primary_key=True), postgresql_with={"fillfactor": 70})
print(t.get_dialect_option(postgresql.dialect(), "with"))   # {'fillfactor': 70}
```

### `Table.implicit_returning` { #table-implicit-returning }

**ধরন:** অ্যাট্রিবিউট

INSERT-এ নতুন primary key আনতে `RETURNING` ব্যবহার করা হবে কি না।

**উদাহরণ:**

```python
print(users.implicit_returning)   # True
```

### `Table.indexes` { #table-indexes }

**ধরন:** অ্যাট্রিবিউট

টেবিলের সব `Index`-এর সেট (`index=True` কলাম থেকে তৈরি গুলোসহ)।

**উদাহরণ:**

```python
print([ix.name for ix in users.indexes])   # ['ix_users_name']
```

### `Table.info` { #table-info }

**ধরন:** প্রপার্টি

নিজের মেটাডেটার dict।

**উদাহরণ:**

```python
print(Table("x", MetaData(), Column("id", Integer, primary_key=True), info={"owner": "billing"}).info)   # {'owner': 'billing'}
```

### `Table.insert()` { #table-insert }

```python
Table.insert()
```

**ধরন:** মেথড

এই টেবিলে একটি `INSERT` স্টেটমেন্ট বানায়।

**উদাহরণ:**

```python
md.create_all(engine)
with engine.begin() as conn:
    new_id = conn.execute(users.insert().values(name="সুমি").returning(users.c.id)).scalar()
print(new_id)   # 1
```

### `Table.insert_column()` { #table-insert-column }

```python
Table.insert_column(column, index, *, replace_existing=False)
```

**ধরন:** মেথড

(২.১-এ নতুন) একটি কলাম নির্দিষ্ট অবস্থানে (index) ঢোকায়, শুধু শেষে নয়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("t", m, Column("id", Integer, primary_key=True), Column("b", Integer))
t.insert_column(Column("a", Integer), 1)
print(list(t.c.keys()))   # ['id', 'a', 'b']
```

### `Table.is_view` { #table-is-view }

**ধরন:** প্রপার্টি

(২.১-এ নতুন) এই `Table` তৈরি করলে `CREATE TABLE`-এর বদলে `CREATE VIEW` হবে কি না (`CreateView` দিয়ে বানানো হলে `True`)।

**উদাহরণ:**

```python
print(users.is_view)   # False
```

### `Table.join()` { #table-join }

```python
Table.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

আরেকটি টেবিলের সাথে `JOIN`; ON শর্ত না দিলে ফরেন কি থেকে বোঝে।

**উদাহরণ:**

```python
print(users.join(addresses))   # users JOIN addresses ON users.id = addresses.user_id
```

### `Table.key` { #table-key }

**ধরন:** প্রপার্টি

MetaData-র `tables` dict-এ টেবিলটির key: স্কিমা থাকলে `schema.name`, না হলে নাম।

**উদাহরণ:**

```python
print(users.key)   # users
```

### `Table.kwargs` { #table-kwargs }

**ধরন:** প্রপার্টি

`dialect_kwargs`-এর আরেক নাম।

**উদাহরণ:**

```python
print(dict(users.kwargs))   # {}
```

### `Table.metadata` { #table-metadata }

**ধরন:** অ্যাট্রিবিউট

টেবিলটি যে `MetaData`-তে আছে।

**উদাহরণ:**

```python
print(users.metadata is md)   # True
```

### `Table.name` { #table-name }

**ধরন:** অ্যাট্রিবিউট

টেবিলের নাম (স্কিমা ছাড়া)।

**উদাহরণ:**

```python
print(addresses.name)   # addresses
```

### `Table.outerjoin()` { #table-outerjoin }

```python
Table.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

`LEFT OUTER JOIN`।

**উদাহরণ:**

```python
print(users.outerjoin(addresses))   # users LEFT OUTER JOIN addresses ON users.id = addresses.user_id
```

### `Table.primary_key` { #table-primary-key }

**ধরন:** প্রপার্টি

টেবিলের `PrimaryKeyConstraint`; `.columns` দিয়ে primary key কলামগুলো।

**উদাহরণ:**

```python
print([c.name for c in users.primary_key.columns])   # ['id']
```

### `Table.reflect_only_elements` { #table-reflect-only-elements }

**ধরন:** প্রপার্টি

(২.১-এ নতুন) reflection-এ ডেটাবেস থেকে পাওয়া এমন ডায়ালেক্ট-নির্দিষ্ট তথ্য, যা DDL-এ ব্যবহার হয় না (শুধু পড়ার জন্য), ডায়ালেক্ট অনুযায়ী ভাগ করা।

**উদাহরণ:**

```python
print(dict(users.reflect_only_elements["postgresql"]))   # {}
```

### `Table.schema` { #table-schema }

**ধরন:** অ্যাট্রিবিউট

টেবিলের স্কিমা (না থাকলে `None`)।

**উদাহরণ:**

```python
print(users.schema)   # None
```

### `Table.select()` { #table-select }

```python
Table.select()
```

**ধরন:** মেথড

`select(টেবিল)`-এর ছোট রূপ: সব কলাম SELECT।

**উদাহরণ:**

```python
print(users.select().where(users.c.id == 1))
# SELECT users.id, users.name, users.email, users.created_at FROM users WHERE users.id = :id_1
```

### `Table.set_creator_ddl()` { #table-set-creator-ddl }

```python
Table.set_creator_ddl(ddl)
```

**ধরন:** মেথড

(২.১-এ নতুন) `create()`/`create_all()`-এ এই টেবিলের জন্য কোন CREATE স্টেটমেন্ট চলবে তা বদলে দেয়, যেমন `CreateTable(t, if_not_exists=True)`।

**উদাহরণ:**

```python
m = MetaData()
t = Table("audit", m, Column("id", Integer, primary_key=True))
t.set_creator_ddl(CreateTable(t, if_not_exists=True))
with engine.begin() as conn:
    m.create_all(conn, checkfirst=False)
    m.create_all(conn, checkfirst=False)   # IF NOT EXISTS-এর কারণে দ্বিতীয়বারেও এরর নেই
print(inspect(engine).has_table("audit"))   # True
```

### `Table.set_dropper_ddl()` { #table-set-dropper-ddl }

```python
Table.set_dropper_ddl(ddl)
```

**ধরন:** মেথড

(২.১-এ নতুন) `drop()`/`drop_all()`-এ কোন DROP স্টেটমেন্ট চলবে তা বদলায়, যেমন `DropTable(t, if_exists=True)`।

**উদাহরণ:**

```python
from sqlalchemy.schema import DropTable
m = MetaData()
t = Table("audit", m, Column("id", Integer, primary_key=True))
t.set_dropper_ddl(DropTable(t, if_exists=True))
m.drop_all(engine, checkfirst=False)   # টেবিল নেই, তবু IF EXISTS-এর কারণে এরর নেই
print("ok")   # ok
```

### `Table.table_valued()` { #table-table-valued }

```python
Table.table_valued()
```

**ধরন:** মেথড

পুরো রো-কে একটি কলাম হিসেবে ব্যবহার করার এক্সপ্রেশন (PostgreSQL-এ `SELECT users FROM users` → রো-টাইপ মান)। JSON-এ রো রূপান্তরের মতো কাজে।

**উদাহরণ:**

```python
md.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(users).values(name="রহিম"))
    row_json = conn.execute(select(func.row_to_json(users.table_valued()))).scalar()
print(row_json["name"], sorted(row_json))   # রহিম ['created_at', 'email', 'id', 'name']
```

### `Table.to_metadata()` { #table-to-metadata }

```python
Table.to_metadata(metadata, schema=<SchemaConst.RETAIN_SCHEMA: 1>, referred_schema_fn=None, name=None)
```

**ধরন:** মেথড

টেবিলের একটি কপি আরেকটি `MetaData`-তে বানায় (কলাম, কনস্ট্রেইন্ট, ইনডেক্সসহ); `schema=` দিয়ে ভিন্ন স্কিমায়, `name=` দিয়ে ভিন্ন নামে। আর্কাইভ টেবিল বা মাল্টি-টেন্যান্ট স্কিমার জন্য।

**উদাহরণ:**

```python
archive = MetaData()
old = users.to_metadata(archive, schema="archive", name="users_2023")
print(old.fullname, [c.name for c in old.c][:2])   # archive.users_2023 ['id', 'name']
```

### `Table.tometadata()` { #table-tometadata }

```python
Table.tometadata(metadata, schema=<SchemaConst.RETAIN_SCHEMA: 1>, referred_schema_fn=None, name=None)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

`to_metadata()`-এর পুরোনো নাম (১.৪ থেকে বাতিলের পথে)।

**উদাহরণ:**

```python
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print(users.tometadata(MetaData()).name)   # users
```

### `Table.update()` { #table-update }

```python
Table.update()
```

**ধরন:** মেথড

এই টেবিলে একটি `UPDATE` স্টেটমেন্ট বানায়।

**উদাহরণ:**

```python
print(users.update().values(name="নতুন").where(users.c.id == 1))
# UPDATE users SET name=:name WHERE users.id = :id_1
```

## `Column` { #column }

```python
from sqlalchemy import Column
```

টেবিলের একটি কলাম: নাম, টাইপ আর সব অপশন। কলাম নিজেও একটি SQL এক্সপ্রেশন, তাই কলামের সব অপারেটর (`==`, `in_()`, `like()` …) এতে চলে। ORM-এ `mapped_column(...)` ঠিক এই প্যারামিটারগুলোই নিয়ে ভেতরে একটি `Column` বানায়। প্রথম পজিশনাল আর্গুমেন্ট নাম, দ্বিতীয় টাইপ, তারপর `ForeignKey`, `Sequence`, `Identity`, `Computed` ইত্যাদি।

**উদাহরণ:**

```python
c = users.c.name
print(c.name, c.type, c.nullable, c.index)   # name VARCHAR(50) False True
print(c == "রহিম")                           # users.name = :name_1
```

### কনস্ট্রাক্টরের প্যারামিটার { #column-params }

```python
Column(*args, name=None, type_=None, autoincrement='auto', default=_NoArg.NO_ARG, insert_default=_NoArg.NO_ARG, doc=None, key=None, index=None, unique=None, info=None, nullable=<SchemaConst.NULL_UNSPECIFIED: 3>, onupdate=None, primary_key=False, server_default=None, server_onupdate=None, quote=None, system=False, comment=None, insert_sentinel=False, **dialect_kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | পজিশনাল: নাম (স্ট্রিং), টাইপ (`String(50)`), আর `ForeignKey`, `Sequence`, `Identity`, `Computed`, `DefaultClause`, কনস্ট্রেইন্ট অবজেক্ট। |
| `name` | কলামের নাম (keyword রূপে)। |
| `type_` | SQL টাইপ (keyword রূপে)। `ForeignKey` থাকলে টাইপ না দিলেও চলে; টার্গেট কলাম থেকে নেয়। |
| `autoincrement` | `"auto"` (ডিফল্ট): পূর্ণসংখ্যার একক primary key নিজে থেকে auto-increment (PostgreSQL-এ `SERIAL`/IDENTITY)। `True` জোর করে, `False` বন্ধ করে, `"ignore_fk"` ফরেন কি থাকলেও চালু রাখে। |
| `default` | INSERT-এ মান না দিলে **Python দিক থেকে** বসানো মান বা ফাংশন (`datetime.utcnow`, `uuid.uuid4`)। ডেটাবেসে কিছু লেখা হয় না। |
| `insert_default` | (২.০.৩১) `default`-এর আরেক নাম (`mapped_column()`-এর সাথে মিল রাখতে)। |
| `doc` | Python দিকের ডকুমেন্টেশন স্ট্রিং (SQL comment নয়)। |
| `key` | Python দিকের ভিন্ন নাম: `table.c.<key>` আর ORM অ্যাট্রিবিউটে এটি, SQL-এ `name`। |
| `index` | `True` দিলে এই কলামে একটি ইনডেক্স (`ix_<table>_<col>`) তৈরি হয়। |
| `unique` | `True` দিলে UNIQUE কনস্ট্রেইন্ট (`index=True`-এর সাথে দিলে unique index)। |
| `info` | নিজের মেটাডেটার dict। |
| `nullable` | NULL চলবে কি না। ডিফল্টে `True`, তবে primary key হলে `False`। |
| `onupdate` | UPDATE-এ মান না দিলে Python দিক থেকে বসানো মান/ফাংশন (যেমন `updated_at`)। |
| `primary_key` | `True` দিলে primary key-র অংশ। |
| `server_default` | **ডেটাবেসের** `DEFAULT` (DDL-এ বসে): স্ট্রিং, `text("...")`, বা `func.now()`। ডেটাবেসে সরাসরি INSERT করলেও কাজ করে। |
| `server_onupdate` | ডেটাবেস নিজে (trigger/`ON UPDATE`) UPDATE-এ মান বদলায় তা জানানোর চিহ্ন (`FetchedValue()`); SQLAlchemy নিজে DDL বানায় না। |
| `quote` | কলামের নাম জোর করে quote হবে কি না। |
| `system` | `True` দিলে ডেটাবেসের নিজস্ব 'system' কলাম (যেমন PostgreSQL-এর `xmin`); CREATE TABLE-এ বসে না। |
| `comment` | কলামের SQL comment। |
| `insert_sentinel` | (২.০.১০) বাল্ক INSERT-এ RETURNING রো-র ক্রম মেলাতে এই কলামকে 'sentinel' হিসেবে চিহ্নিত করে (`insert_sentinel()` দেখুন)। |
| `dialect_kwargs` | ডায়ালেক্ট-নির্দিষ্ট অপশন, যেমন `mysql_charset=...`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #column-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append_foreign_key()`](#column-append-foreign-key) | মেথড (internal) | কলামে একটি `ForeignKey` যোগ করার ভেতরের মেথড (সাধারণত কনস্ট্রাক্টরে `ForeignKey` দিন)। |
| [`argument_for()`](#column-argument-for) | ক্লাস মেথড (internal) | (ক্লাস মেথড) নতুন ডায়ালেক্ট-নির্দিষ্ট argument নিবন্ধন। |
| [`autoincrement`](#column-autoincrement) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `autoincrement` সেটিং। |
| [`comment`](#column-comment) | অ্যাট্রিবিউট | কলামের SQL comment। |
| [`computed`](#column-computed) | অ্যাট্রিবিউট | `Computed(...)` দেওয়া থাকলে সেটি (generated column), না হলে `None`। |
| [`constraints`](#column-constraints) | অ্যাট্রিবিউট | কলাম-স্তরে দেওয়া কনস্ট্রেইন্টের সেট। |
| [`copy()`](#column-copy) | মেথড ⚠️ deprecated | কলামের কপি (১.৪ থেকে বাতিলের পথে)। |
| [`create_drop_stringify_dialect`](#column-create-drop-stringify-dialect) | অ্যাট্রিবিউট (internal) | DDL `str()` করার সময়ের ডায়ালেক্ট নাম। |
| [`default`](#column-default) | অ্যাট্রিবিউট | Python-দিকের INSERT ডিফল্ট (একটি `ColumnDefault` অবজেক্ট; `.arg`-এ আসল মান/ফাংশন), না থাকলে `None`। |
| [`dialect_kwargs`](#column-dialect-kwargs) | প্রপার্টি | কলামে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন। |
| [`dialect_options`](#column-dialect-options) | প্রপার্টি | ডায়ালেক্ট অনুযায়ী ভাগ করা অপশন। |
| [`doc`](#column-doc) | অ্যাট্রিবিউট | Python দিকের ডকুমেন্টেশন স্ট্রিং। |
| [`get_dialect_option()`](#column-get-dialect-option) | মেথড | ডায়ালেক্টের একটি নির্দিষ্ট অপশনের মান। |
| [`identity`](#column-identity) | অ্যাট্রিবিউট | `Identity(...)` দেওয়া থাকলে সেটি (`GENERATED ... AS IDENTITY`), না হলে `None`। |
| [`index`](#column-index) | অ্যাট্রিবিউট | `index=True` দেওয়া হয়েছে কি না (না দিলে `None`)। |
| [`info`](#column-info) | প্রপার্টি | নিজের মেটাডেটার dict। |
| [`is_literal`](#column-is-literal) | অ্যাট্রিবিউট (internal) | কলামের নাম quote ছাড়া হুবহু বসবে কি না (টেবিল-কলামে `False`)। |
| [`kwargs`](#column-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`name`](#column-name) | অ্যাট্রিবিউট | SQL-এ কলামের নাম। |
| [`nullable`](#column-nullable) | অ্যাট্রিবিউট | NULL চলবে কি না। |
| [`onupdate`](#column-onupdate) | অ্যাট্রিবিউট | Python-দিকের UPDATE ডিফল্ট (`ColumnDefault`), না থাকলে `None`। |
| [`references()`](#column-references) | মেথড | এই কলাম ফরেন কি দিয়ে দেওয়া কলামটিকে রেফার করে কি না। |
| [`reflect_only_elements`](#column-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) reflection-এ পাওয়া, DDL-এ ব্যবহার না হওয়া ডায়ালেক্ট-তথ্য (শুধু পড়ার জন্য)। |
| [`server_default`](#column-server-default) | অ্যাট্রিবিউট | ডেটাবেস-দিকের ডিফল্ট (`DefaultClause`), না থাকলে `None`। |
| [`server_onupdate`](#column-server-onupdate) | অ্যাট্রিবিউট | ডেটাবেস-দিকের UPDATE ডিফল্টের চিহ্ন (`FetchedValue`), না থাকলে `None`। |
| [`system`](#column-system) | অ্যাট্রিবিউট | 'system' কলাম কি না। |
| [`table`](#column-table) | অ্যাট্রিবিউট | কলামটি যে টেবিলে আছে (কোনো টেবিলে যোগ না হলে এরর/অনুপস্থিত)। |
| [`unique`](#column-unique) | অ্যাট্রিবিউট | `unique=True` দেওয়া হয়েছে কি না (না দিলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Column`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `Column.append_foreign_key()` { #column-append-foreign-key }

```python
Column.append_foreign_key(fk)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলামে একটি `ForeignKey` যোগ করার ভেতরের মেথড (সাধারণত কনস্ট্রাক্টরে `ForeignKey` দিন)।

### `Column.argument_for()` { #column-argument-for }

```python
Column.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) নতুন ডায়ালেক্ট-নির্দিষ্ট argument নিবন্ধন।

### `Column.autoincrement` { #column-autoincrement }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `autoincrement` সেটিং।

**উদাহরণ:**

```python
print(users.c.id.autoincrement)   # auto
```

### `Column.comment` { #column-comment }

**ধরন:** অ্যাট্রিবিউট

কলামের SQL comment।

**উদাহরণ:**

```python
print(Column("x", Integer, comment="পরিমাণ").comment)   # পরিমাণ
```

### `Column.computed` { #column-computed }

**ধরন:** অ্যাট্রিবিউট

`Computed(...)` দেওয়া থাকলে সেটি (generated column), না হলে `None`।

**উদাহরণ:**

```python
c = Column("total", Integer, Computed("price * qty"))
print(c.computed.sqltext)   # price * qty
```

### `Column.constraints` { #column-constraints }

**ধরন:** অ্যাট্রিবিউট

কলাম-স্তরে দেওয়া কনস্ট্রেইন্টের সেট।

**উদাহরণ:**

```python
print(users.c.id.constraints)   # set()
```

### `Column.copy()` { #column-copy }

```python
Column.copy(**kw)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

কলামের কপি (১.৪ থেকে বাতিলের পথে)। টেবিলসহ কপি করতে `Table.to_metadata()`।

### `Column.create_drop_stringify_dialect` { #column-create-drop-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DDL `str()` করার সময়ের ডায়ালেক্ট নাম।

### `Column.default` { #column-default }

**ধরন:** অ্যাট্রিবিউট

Python-দিকের INSERT ডিফল্ট (একটি `ColumnDefault` অবজেক্ট; `.arg`-এ আসল মান/ফাংশন), না থাকলে `None`।

**উদাহরণ:**

```python
c = Column("status", String(10), default="active")
print(c.default.arg)   # active
```

### `Column.dialect_kwargs` { #column-dialect-kwargs }

**ধরন:** প্রপার্টি

কলামে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন।

**উদাহরণ:**

```python
print(dict(users.c.id.dialect_kwargs))   # {}
```

### `Column.dialect_options` { #column-dialect-options }

**ধরন:** প্রপার্টি

ডায়ালেক্ট অনুযায়ী ভাগ করা অপশন।

**উদাহরণ:**

```python
print(dict(users.c.id.dialect_options["postgresql"]))   # {}
```

### `Column.doc` { #column-doc }

**ধরন:** অ্যাট্রিবিউট

Python দিকের ডকুমেন্টেশন স্ট্রিং।

**উদাহরণ:**

```python
print(Column("x", Integer, doc="গ্রাহকের বয়স").doc)   # গ্রাহকের বয়স
```

### `Column.get_dialect_option()` { #column-get-dialect-option }

```python
Column.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

ডায়ালেক্টের একটি নির্দিষ্ট অপশনের মান।

**উদাহরণ:**

```python
print(users.c.id.get_dialect_option(postgresql.dialect(), "nonexistent", else_="নেই"))   # নেই
```

### `Column.identity` { #column-identity }

**ধরন:** অ্যাট্রিবিউট

`Identity(...)` দেওয়া থাকলে সেটি (`GENERATED ... AS IDENTITY`), না হলে `None`।

**উদাহরণ:**

```python
c = Column("id", BigInteger, Identity(start=1000), primary_key=True)
print(c.identity.start)   # 1000
```

### `Column.index` { #column-index }

**ধরন:** অ্যাট্রিবিউট

`index=True` দেওয়া হয়েছে কি না (না দিলে `None`)।

**উদাহরণ:**

```python
print(users.c.name.index, users.c.email.index)   # True None
```

### `Column.info` { #column-info }

**ধরন:** প্রপার্টি

নিজের মেটাডেটার dict।

**উদাহরণ:**

```python
print(Column("x", Integer, info={"label": "পরিমাণ"}).info)   # {'label': 'পরিমাণ'}
```

### `Column.is_literal` { #column-is-literal }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলামের নাম quote ছাড়া হুবহু বসবে কি না (টেবিল-কলামে `False`)।

### `Column.kwargs` { #column-kwargs }

**ধরন:** প্রপার্টি

`dialect_kwargs`-এর আরেক নাম।

**উদাহরণ:**

```python
print(dict(users.c.name.kwargs))   # {}
```

### `Column.name` { #column-name }

**ধরন:** অ্যাট্রিবিউট

SQL-এ কলামের নাম।

**উদাহরণ:**

```python
print(Column("user_name", String, key="username").name)   # user_name
```

### `Column.nullable` { #column-nullable }

**ধরন:** অ্যাট্রিবিউট

NULL চলবে কি না।

**উদাহরণ:**

```python
print(users.c.email.nullable, users.c.id.nullable)   # True False
```

### `Column.onupdate` { #column-onupdate }

**ধরন:** অ্যাট্রিবিউট

Python-দিকের UPDATE ডিফল্ট (`ColumnDefault`), না থাকলে `None`।

**উদাহরণ:**

```python
c = Column("updated_at", DateTime, onupdate=datetime.datetime.now)
print(c.onupdate.is_callable)   # True
```

### `Column.references()` { #column-references }

```python
Column.references(column)
```

**ধরন:** মেথড

এই কলাম ফরেন কি দিয়ে দেওয়া কলামটিকে রেফার করে কি না।

**উদাহরণ:**

```python
print(addresses.c.user_id.references(users.c.id))   # True
```

### `Column.reflect_only_elements` { #column-reflect-only-elements }

**ধরন:** প্রপার্টি

(২.১-এ নতুন) reflection-এ পাওয়া, DDL-এ ব্যবহার না হওয়া ডায়ালেক্ট-তথ্য (শুধু পড়ার জন্য)।

**উদাহরণ:**

```python
print(dict(users.c.id.reflect_only_elements["postgresql"]))   # {}
```

### `Column.server_default` { #column-server-default }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস-দিকের ডিফল্ট (`DefaultClause`), না থাকলে `None`।

**উদাহরণ:**

```python
print(users.c.created_at.server_default.arg)   # now()
```

### `Column.server_onupdate` { #column-server-onupdate }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস-দিকের UPDATE ডিফল্টের চিহ্ন (`FetchedValue`), না থাকলে `None`।

**উদাহরণ:**

```python
from sqlalchemy import FetchedValue
print(type(Column("x", DateTime, server_onupdate=FetchedValue()).server_onupdate).__name__)   # FetchedValue
```

### `Column.system` { #column-system }

**ধরন:** অ্যাট্রিবিউট

'system' কলাম কি না।

**উদাহরণ:**

```python
print(Column("xmin", Integer, system=True).system)   # True
```

### `Column.table` { #column-table }

**ধরন:** অ্যাট্রিবিউট

কলামটি যে টেবিলে আছে (কোনো টেবিলে যোগ না হলে এরর/অনুপস্থিত)।

**উদাহরণ:**

```python
print(addresses.c.city.table.name)   # addresses
```

### `Column.unique` { #column-unique }

**ধরন:** অ্যাট্রিবিউট

`unique=True` দেওয়া হয়েছে কি না (না দিলে `None`)।

**উদাহরণ:**

```python
print(users.c.email.unique)   # True
```

## সহায়ক ফাংশন ও ২.১-এর টাইপ-হেল্পার { #insert-sentinel-group }

## `insert_sentinel()` { #insert-sentinel }

```python
from sqlalchemy import insert_sentinel
```

```python
insert_sentinel(name=None, type_=None, *, default=None, omit_from_statements=True)
```

**ধরন:** ফাংশন

(২.০.১০-এ নতুন) একটি বিশেষ "sentinel" কলাম বানায়। যেসব টেবিলের primary key ক্রমবর্ধমান নয় (যেমন client-side UUID), সেখানে বাল্ক INSERT ... RETURNING-এর রো-গুলো কোন ইনপুটের তা মেলাতে SQLAlchemy এই কলাম ব্যবহার করে, ফলে বাল্ক insert দ্রুত হয়। সাধারণ SELECT-এ কলামটি বাদ থাকে।

**উদাহরণ:**

```python
m = MetaData()
t = Table("events", m, Column("id", String(36), primary_key=True), insert_sentinel("_sentinel"))
print(t.c._sentinel._insert_sentinel, select(t))   # True SELECT events.id FROM events
```

### `insert_sentinel()`-এর সব প্যারামিটার { #insert-sentinel-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | কলামের নাম (ডিফল্ট `_sentinel`)। |
| `type_` | টাইপ (ডিফল্ট `Integer`)। |
| `default` | ডিফল্ট মান তৈরির নিয়ম। |
| `omit_from_statements` | `True` (ডিফল্ট) হলে সাধারণ SELECT/INSERT-এ কলামটি দেখা যায় না। |

## `sort_tables()` { #sort-tables }

```python
from sqlalchemy.schema import sort_tables
```

```python
sort_tables(tables, skip_fn=None, extra_dependencies=None)
```

**ধরন:** ফাংশন

কয়েকটি টেবিলকে ফরেন কি নির্ভরতা অনুযায়ী সাজায় (আগে প্যারেন্ট)। `MetaData.sorted_tables`-এর স্বাধীন রূপ, যেকোনো টেবিল-তালিকায়।

**উদাহরণ:**

```python
print([t.name for t in sort_tables([addresses, users])])   # ['users', 'addresses']
```

### `sort_tables()`-এর সব প্যারামিটার { #sort-tables-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `tables` | টেবিলের তালিকা। |
| `skip_fn` | একটি `ForeignKey` নিয়ে `True` ফেরত দিলে সেই নির্ভরতা উপেক্ষা হয়। |
| `extra_dependencies` | বাড়তি `(parent, child)` টেবিল-জোড়ার তালিকা। |

## `sort_tables_and_constraints()` { #sort-tables-and-constraints }

```python
from sqlalchemy.schema import sort_tables_and_constraints
```

```python
sort_tables_and_constraints(tables, filter_fn=None, extra_dependencies=None)
```

**ধরন:** ফাংশন

`sort_tables()`-এর মতো, কিন্তু প্রতিটি উপাদান `(টেবিল, [কনস্ট্রেইন্ট])` জোড়া; চক্রাকার ফরেন কি থাকলে সেগুলো আলাদা করে শেষে `(None, [কনস্ট্রেইন্ট])` হিসেবে দেয়, যাতে আগে টেবিল আর পরে `ALTER TABLE ADD CONSTRAINT` করা যায়। `create_all()` ভেতরে এটিই ব্যবহার করে।

**উদাহরণ:**

```python
print([(t.name if t is not None else None) for t, fks in sort_tables_and_constraints([addresses, users])])
# ['users', 'addresses', None]
```

### `sort_tables_and_constraints()`-এর সব প্যারামিটার { #sort-tables-and-constraints-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `tables` | টেবিলের তালিকা। |
| `filter_fn` | একটি কনস্ট্রেইন্ট নিয়ে `True` দিলে সেটি আলাদা (শেষে) রাখা হয়, `False` দিলে উপেক্ষা, `None` দিলে স্বাভাবিক। |
| `extra_dependencies` | বাড়তি `(parent, child)` জোড়া। |

## `TypedColumns` { #typedcolumns }

```python
from sqlalchemy import TypedColumns, Named
```

(২.১-এ নতুন) শুধু **টাইপ চেকারের** জন্য: Core `Table`-এর কলামগুলো একটি ক্লাসে টাইপসহ ঘোষণা করা যায়, ফলে `table.c.name`-এর টাইপ mypy/pyright জানে। রানটাইমে এই ক্লাসের অবজেক্ট তৈরি হয় না; `Table("নাম", md, কলাম-ক্লাস)` দিলে কলামগুলো সেখান থেকে বানানো হয়। `Named[str]` অ্যানোটেশন থেকে টাইপ আর nullable অনুমান হয় (ORM-এর `Mapped[]`-এর মতো)।

**উদাহরণ:**

```python
class item_cols(TypedColumns):
    id = Column(Integer, primary_key=True)
    title: Named[str]
    price: Named[float | None]

items = Table("items", MetaData(), item_cols)
print([(c.name, str(c.type), c.nullable) for c in items.c])
# [('id', 'INTEGER', False), ('title', 'VARCHAR', False), ('price', 'DOUBLE', True)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typedcolumns-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`compare()`](#typedcolumns-compare) | মেথড (internal) | টাইপ-চেকারের জন্য ঘোষিত `ColumnCollection` ইন্টারফেসের অংশ (রানটাইমে আসল কলাম-সংগ্রহের মেথড চলে)। |
| [`contains_column()`](#typedcolumns-contains-column) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.contains_column()` দেখুন। |
| [`corresponding_column()`](#typedcolumns-corresponding-column) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.corresponding_column()` দেখুন। |
| [`get()`](#typedcolumns-get) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.get()` দেখুন। |
| [`items()`](#typedcolumns-items) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.items()` দেখুন। |
| [`keys()`](#typedcolumns-keys) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.keys()` দেখুন। |
| [`values()`](#typedcolumns-values) | মেথড (internal) | টাইপ-চেকার ইন্টারফেস: `ColumnCollection.values()` দেখুন। |

### `TypedColumns.compare()` { #typedcolumns-compare }

```python
TypedColumns.compare(other)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকারের জন্য ঘোষিত `ColumnCollection` ইন্টারফেসের অংশ (রানটাইমে আসল কলাম-সংগ্রহের মেথড চলে)।

### `TypedColumns.contains_column()` { #typedcolumns-contains-column }

```python
TypedColumns.contains_column(col)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.contains_column()` দেখুন।

### `TypedColumns.corresponding_column()` { #typedcolumns-corresponding-column }

```python
TypedColumns.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.corresponding_column()` দেখুন।

### `TypedColumns.get()` { #typedcolumns-get }

```python
TypedColumns.get(key, default=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.get()` দেখুন।

### `TypedColumns.items()` { #typedcolumns-items }

```python
TypedColumns.items()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.items()` দেখুন।

### `TypedColumns.keys()` { #typedcolumns-keys }

```python
TypedColumns.keys()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.keys()` দেখুন।

### `TypedColumns.values()` { #typedcolumns-values }

```python
TypedColumns.values()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-চেকার ইন্টারফেস: `ColumnCollection.values()` দেখুন।

## `CheckFirst` { #checkfirst }

```python
from sqlalchemy.schema import CheckFirst
```

(২.১-এ নতুন) `create_all()`, `drop_all()`, `Table.create()` ইত্যাদির `checkfirst=`-এ কোন কোন ধরনের অবজেক্ট আগে "আছে কি না" যাচাই হবে তা বলার flag enum। `|` দিয়ে মেলানো যায়; `CheckFirst(True)` / `CheckFirst(False)` দিয়ে পুরোনো বুলিয়ান থেকে রূপান্তর। প্রতিটি যাচাই একটি বাড়তি কুয়েরি, তাই যেগুলো দরকার নেই বাদ দিলে দ্রুত হয়।

**উদাহরণ:**

```python
flags = CheckFirst.TABLES | CheckFirst.INDEXES
md.create_all(engine, checkfirst=flags)
print(CheckFirst.TABLES in flags, CheckFirst.TYPES in flags)   # True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #checkfirst-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`INDEXES`](#checkfirst-INDEXES) | অ্যাট্রিবিউট | ইনডেক্স তৈরি/মোছার আগে যাচাই। |
| [`SEQUENCES`](#checkfirst-SEQUENCES) | অ্যাট্রিবিউট | sequence তৈরি/মোছার আগে যাচাই। |
| [`TABLES`](#checkfirst-TABLES) | অ্যাট্রিবিউট | টেবিল তৈরি/মোছার আগে যাচাই। |
| [`TYPES`](#checkfirst-TYPES) | অ্যাট্রিবিউট | কাস্টম টাইপ (যেমন PostgreSQL ENUM) তৈরি/মোছার আগে যাচাই। |
| [`VIEWS`](#checkfirst-VIEWS) | অ্যাট্রিবিউট | ভিউ (২.১-এর `CreateView`) তৈরি/মোছার আগে যাচাই। |

### `CheckFirst.INDEXES` { #checkfirst-INDEXES }

**ধরন:** অ্যাট্রিবিউট

ইনডেক্স তৈরি/মোছার আগে যাচাই।

**উদাহরণ:**

```python
print(CheckFirst.INDEXES.value)   # 8
```

### `CheckFirst.SEQUENCES` { #checkfirst-SEQUENCES }

**ধরন:** অ্যাট্রিবিউট

sequence তৈরি/মোছার আগে যাচাই।

**উদাহরণ:**

```python
print(CheckFirst.SEQUENCES.value)   # 16
```

### `CheckFirst.TABLES` { #checkfirst-TABLES }

**ধরন:** অ্যাট্রিবিউট

টেবিল তৈরি/মোছার আগে যাচাই।

**উদাহরণ:**

```python
print(CheckFirst.TABLES.value)   # 2
```

### `CheckFirst.TYPES` { #checkfirst-TYPES }

**ধরন:** অ্যাট্রিবিউট

কাস্টম টাইপ (যেমন PostgreSQL ENUM) তৈরি/মোছার আগে যাচাই।

**উদাহরণ:**

```python
print(CheckFirst.TYPES.value)   # 32
```

### `CheckFirst.VIEWS` { #checkfirst-VIEWS }

**ধরন:** অ্যাট্রিবিউট

ভিউ (২.১-এর `CreateView`) তৈরি/মোছার আগে যাচাই।

**উদাহরণ:**

```python
print(CheckFirst.VIEWS.value)   # 4
```

/// check | সংক্ষেপে মনে রাখুন

* পুরো অ্যাপে একটি `MetaData`, তাতে `naming_convention` দিন (Alembic-এর জন্য জরুরি)।
* `create_all()` শুধু নেই এমন টেবিল বানায়; কলাম বদলের জন্য Alembic।
* `default` / `onupdate` = Python দিক; `server_default` = ডেটাবেস দিক (DDL-এ বসে)।
* `index=True` → ইনডেক্স; `unique=True` → UNIQUE কনস্ট্রেইন্ট।
* বিদ্যমান ডেটাবেস পড়তে: `MetaData().reflect(engine)` বা `Table("নাম", md, autoload_with=engine)`।
* টেবিল কপি অন্য স্কিমায়: `table.to_metadata(md2, schema="archive")`।

///
