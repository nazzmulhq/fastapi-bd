# কনস্ট্রেইন্ট, ইনডেক্স ও ডিফল্ট API { #api-constraints }

/// note | এই পেজে যা আছে

* **কনস্ট্রেইন্ট:** `Constraint`, `ColumnCollectionConstraint`, `PrimaryKeyConstraint`, `UniqueConstraint`, `CheckConstraint`, `ForeignKeyConstraint`, `ForeignKey`, আর নামের জন্য `conv`।
* **ইনডেক্স:** `Index` (partial, expression, unique, PostgreSQL `USING gin` …)।
* **ডিফল্ট ও generated মান:** `DefaultGenerator`, `ColumnDefault`, `DefaultClause`, `FetchedValue`, `Sequence`, `Identity`, `Computed`।
* প্রতিটির **সব** সদস্য আর কনস্ট্রাক্টরের প্রতিটি প্যারামিটার।

///

কনস্ট্রেইন্ট ডেটাবেসকে ভুল ডেটা ঢুকতে দেয় না: ফাঁকা নাম, ডুপ্লিকেট ইমেইল, অস্তিত্বহীন ইউজারের অর্ডার। কোডের ভ্যালিডেশন ভুলে গেলেও ডেটাবেস রক্ষা করে। ORM মডেলে এগুলো `__table_args__ = (UniqueConstraint(...), Index(...))`-এ বা `mapped_column(unique=True, index=True)` দিয়ে দেওয়া হয়। বিস্তারিত: [Model অধ্যায়](../models.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
md = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

users = Table("users", md,
    Column("id", Integer, primary_key=True),
    Column("email", String(100), nullable=False),
    Column("age", Integer),
    UniqueConstraint("email"),
    CheckConstraint("age >= 0", name="age_positive"),
)

orders = Table("orders", md,
    Column("id", Integer, Identity(start=1000), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("status", String(20), server_default="new"),
    Column("price", Integer), Column("qty", Integer),
    Column("total", Integer, Computed("price * qty", persisted=True)),
    Index(None, "status", postgresql_where=text("status <> 'done'")),
)
```

`ddl(টেবিল)` PostgreSQL-এর `CREATE TABLE` দেখায়। প্রতিটি উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## কনস্ট্রেইন্ট { #constraint-group }

## `Constraint` { #constraint }

```python
from sqlalchemy.schema import Constraint
```

সব টেবিল-কনস্ট্রেইন্টের মূল ক্লাস। নিজে সরাসরি তৈরি করা হয় না; নিচের সাবক্লাসগুলো ব্যবহার করুন। সবারই `name`, `deferrable`, `initially`, `comment`, `info` আছে।

**উদাহরণ:**

```python
print(sorted(type(c).__name__ for c in users.constraints))
# ['CheckConstraint', 'PrimaryKeyConstraint', 'UniqueConstraint']
print(all(isinstance(c, Constraint) for c in users.constraints))   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #constraint-params }

```python
Constraint(name=None, deferrable=None, initially=None, info=None, comment=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | কনস্ট্রেইন্টের নাম। না দিলে ডেটাবেস নিজে নাম দেয়, বা `MetaData(naming_convention=...)` থাকলে সেই নিয়মে তৈরি হয় (Alembic-এ জরুরি)। |
| `deferrable` | `True` দিলে `DEFERRABLE`: যাচাই ট্রানজ্যাকশনের শেষ পর্যন্ত পিছানো যায়। |
| `initially` | `"DEFERRED"` দিলে ডিফল্টে যাচাই commit-এর সময়ে হয়। |
| `info` | নিজের মেটাডেটার dict। |
| `comment` | (২.০) কনস্ট্রেইন্টের SQL comment (যেসব ডেটাবেস সমর্থন করে)। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #constraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`comment`](#constraint-comment) | অ্যাট্রিবিউট | কনস্ট্রেইন্টের comment। |
| [`copy()`](#constraint-copy) | মেথড ⚠️ deprecated | কনস্ট্রেইন্টের কপি (১.৪ থেকে বাতিলের পথে); টেবিলসহ কপিতে `Table.to_metadata()`। |
| [`ddl_if()`](#constraint-ddl-if) | মেথড | শর্তসাপেক্ষ DDL: এই কনস্ট্রেইন্ট/ইনডেক্স শুধু নির্দিষ্ট ডায়ালেক্টে (বা একটি ফাংশন `True` দিলে) তৈরি হবে। |
| [`deferrable`](#constraint-deferrable) | অ্যাট্রিবিউট | `DEFERRABLE` কি না। |
| [`initially`](#constraint-initially) | অ্যাট্রিবিউট | `INITIALLY` সেটিং। |
| [`name`](#constraint-name) | অ্যাট্রিবিউট | কনস্ট্রেইন্টের নাম (naming convention থাকলে সেই নিয়মে তৈরি নাম)। |
| [`parent`](#constraint-parent) | অ্যাট্রিবিউট | কনস্ট্রেইন্টটি যে টেবিলে যুক্ত (`table`-এর মতো)। |
| [`table`](#constraint-table) | প্রপার্টি | কনস্ট্রেইন্টটি যে টেবিলের; এখনো টেবিলে যুক্ত না হলে এরর। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Constraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

///

### `Constraint.comment` { #constraint-comment }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্টের comment।

**উদাহরণ:**

```python
print(CheckConstraint("x > 0", comment="ধনাত্মক").comment)   # ধনাত্মক
```

### `Constraint.copy()` { #constraint-copy }

```python
Constraint.copy(**kw)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

কনস্ট্রেইন্টের কপি (১.৪ থেকে বাতিলের পথে); টেবিলসহ কপিতে `Table.to_metadata()`।

### `Constraint.ddl_if()` { #constraint-ddl-if }

```python
Constraint.ddl_if(dialect=None, callable_=None, state=None)
```

**ধরন:** মেথড

শর্তসাপেক্ষ DDL: এই কনস্ট্রেইন্ট/ইনডেক্স শুধু নির্দিষ্ট ডায়ালেক্টে (বা একটি ফাংশন `True` দিলে) তৈরি হবে। একই মডেল একাধিক ডেটাবেসে চালালে কাজে লাগে।

**উদাহরণ:**

```python
m = MetaData()
t = Table("t", m, Column("id", Integer, primary_key=True), Column("q", Integer))
ix = Index("ix_q", t.c.q).ddl_if(dialect="mysql")
print(CreateTable(t).compile(dialect=postgresql.dialect()).string.count("ix_q"))   # 0
m.create_all(engine)
print([i["name"] for i in inspect(engine).get_indexes("t")])   # []  (PostgreSQL-এ তৈরি হয়নি)
```

### `Constraint.deferrable` { #constraint-deferrable }

**ধরন:** অ্যাট্রিবিউট

`DEFERRABLE` কি না।

**উদাহরণ:**

```python
print(UniqueConstraint("email", deferrable=True).deferrable)   # True
```

### `Constraint.initially` { #constraint-initially }

**ধরন:** অ্যাট্রিবিউট

`INITIALLY` সেটিং।

**উদাহরণ:**

```python
print(UniqueConstraint("email", deferrable=True, initially="DEFERRED").initially)   # DEFERRED
```

### `Constraint.name` { #constraint-name }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্টের নাম (naming convention থাকলে সেই নিয়মে তৈরি নাম)।

**উদাহরণ:**

```python
print(uq(users).name, ck(users).name)   # uq_users_email ck_users_age_positive
```

### `Constraint.parent` { #constraint-parent }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্টটি যে টেবিলে যুক্ত (`table`-এর মতো)।

**উদাহরণ:**

```python
print(uq(users).parent.name)   # users
```

### `Constraint.table` { #constraint-table }

**ধরন:** প্রপার্টি

কনস্ট্রেইন্টটি যে টেবিলের; এখনো টেবিলে যুক্ত না হলে এরর।

**উদাহরণ:**

```python
print(ck(users).table.name)   # users
```

## `ColumnCollectionConstraint` { #columncollectionconstraint }

```python
from sqlalchemy.schema import ColumnCollectionConstraint
```

এক বা একাধিক কলামের ওপর কনস্ট্রেইন্টের মূল ক্লাস (`PrimaryKeyConstraint`, `UniqueConstraint`, `ForeignKeyConstraint`, আর কলামসহ `CheckConstraint`)। কলাম দেওয়া যায় কলাম অবজেক্ট বা নাম (স্ট্রিং) দিয়ে।

**উদাহরণ:**

```python
print(isinstance(uq(users), ColumnCollectionConstraint), [c.name for c in uq(users).columns])   # True ['email']
```

### কনস্ট্রাক্টরের প্যারামিটার { #columncollectionconstraint-params }

```python
ColumnCollectionConstraint(*columns, name=None, deferrable=None, initially=None, info=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | কলামগুলো (অবজেক্ট বা নাম)। |
| `name` | কনস্ট্রেইন্টের নাম। |
| `deferrable` | `DEFERRABLE` কি না। |
| `initially` | `INITIALLY` সেটিং। |
| `info` | নিজের মেটাডেটার dict। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columncollectionconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`c`](#columncollectionconstraint-c) | প্রপার্টি | `columns`-এর ছোট নাম। |
| [`columns`](#columncollectionconstraint-columns) | প্রপার্টি | কনস্ট্রেইন্টের কলামগুলোর সংগ্রহ। |
| [`contains_column()`](#columncollectionconstraint-contains-column) | মেথড | একটি কলাম এই কনস্ট্রেইন্টে আছে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnCollectionConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`Constraint` থেকে:** [`copy()`](#constraint-copy) · [`ddl_if()`](#constraint-ddl-if) · [`table`](#constraint-table)

///

### `ColumnCollectionConstraint.c` { #columncollectionconstraint-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(uq(users).c.email.name)   # email
```

### `ColumnCollectionConstraint.columns` { #columncollectionconstraint-columns }

**ধরন:** প্রপার্টি

কনস্ট্রেইন্টের কলামগুলোর সংগ্রহ।

**উদাহরণ:**

```python
print([c.name for c in pk(users).columns])   # ['id']
```

### `ColumnCollectionConstraint.contains_column()` { #columncollectionconstraint-contains-column }

```python
ColumnCollectionConstraint.contains_column(col)
```

**ধরন:** মেথড

একটি কলাম এই কনস্ট্রেইন্টে আছে কি না।

**উদাহরণ:**

```python
print(uq(users).contains_column(users.c.email), uq(users).contains_column(users.c.age))   # True False
```

## `PrimaryKeyConstraint` { #primarykeyconstraint }

```python
from sqlalchemy import PrimaryKeyConstraint
```

টেবিলের primary key। কলামে `primary_key=True` দিলে নিজেই তৈরি হয়; composite key বা নিজের নাম দিতে স্পষ্টভাবে লিখুন।

**উদাহরণ:**

```python
m = MetaData()
t = Table("order_items", m, Column("order_id", Integer), Column("product_id", Integer), Column("qty", Integer),
          PrimaryKeyConstraint("order_id", "product_id", name="pk_order_items"))
ddl(t)
# CREATE TABLE order_items (
# 	order_id INTEGER NOT NULL,
# 	product_id INTEGER NOT NULL,
# 	qty INTEGER,
# 	CONSTRAINT pk_order_items PRIMARY KEY (order_id, product_id)
# )
```

### কনস্ট্রাক্টরের প্যারামিটার { #primarykeyconstraint-params }

```python
PrimaryKeyConstraint(*columns, name=None, deferrable=None, initially=None, info=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | primary key-এর কলামগুলো। |
| `name` | নাম। |
| `deferrable` | `DEFERRABLE` কি না। |
| `initially` | `INITIALLY` সেটিং। |
| `info` | নিজের মেটাডেটার dict। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন (যেমন SQL Server-এ `mssql_clustered`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #primarykeyconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`columns_autoinc_first`](#primarykeyconstraint-columns-autoinc-first) | প্রপার্টি (internal) | primary key কলামগুলো, auto-increment কলামটি আগে রেখে (কিছু ডায়ালেক্টের DDL-এর জন্য)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `PrimaryKeyConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`ColumnCollectionConstraint` থেকে:** [`c`](#columncollectionconstraint-c) · [`columns`](#columncollectionconstraint-columns) · [`contains_column()`](#columncollectionconstraint-contains-column)

**`Constraint` থেকে:** [`copy()`](#constraint-copy) · [`ddl_if()`](#constraint-ddl-if) · [`table`](#constraint-table)

///

### `PrimaryKeyConstraint.columns_autoinc_first` { #primarykeyconstraint-columns-autoinc-first }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

primary key কলামগুলো, auto-increment কলামটি আগে রেখে (কিছু ডায়ালেক্টের DDL-এর জন্য)।

## `UniqueConstraint` { #uniqueconstraint }

```python
from sqlalchemy import UniqueConstraint
```

এক বা একাধিক কলামের মিলিত মান টেবিলে অনন্য হতে হবে (`UNIQUE`)। একক কলামে `unique=True` লেখাও চলে; কয়েকটি কলাম একসাথে অনন্য রাখতে (যেমন "একই ইউজারের একই নামের দুটি প্রজেক্ট নয়") এটি লাগে। ভঙ্গ হলে `IntegrityError`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    try:
        conn.execute(insert(users).values(id=2, email="rahim@example.com"))
    except exc.IntegrityError as e:
        print(type(e.orig).__name__)   # UniqueViolation
```

### কনস্ট্রাক্টরের প্যারামিটার { #uniqueconstraint-params }

```python
UniqueConstraint(*columns, name=None, deferrable=None, initially=None, info=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | যে কলাম(গুলো) মিলে অনন্য। |
| `name` | নাম। |
| `deferrable` | `DEFERRABLE` কি না (একই ট্রানজ্যাকশনে মান অদলবদলের জন্য)। |
| `initially` | `INITIALLY` সেটিং। |
| `info` | নিজের মেটাডেটার dict। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন, যেমন PostgreSQL ১৫+-এ `postgresql_nulls_not_distinct=True`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ColumnCollectionConstraint`](#columncollectionconstraint-summary)-এর মতো।

## `CheckConstraint` { #checkconstraint }

```python
from sqlalchemy import CheckConstraint
```

একটি শর্ত যা প্রতিটি রো-কে মানতে হবে (`CHECK (age >= 0)`)। শর্ত স্ট্রিং বা SQL এক্সপ্রেশন। ভঙ্গ হলে `IntegrityError`। কলামের ভেতরে দিলে কলাম-স্তরের কনস্ট্রেইন্ট হয়।

**উদাহরণ:**

```python
with engine.connect() as conn:
    try:
        conn.execute(insert(users).values(id=3, email="x@y.com", age=-5))
    except exc.IntegrityError as e:
        print(type(e.orig).__name__, e.orig.diag.constraint_name)   # CheckViolation ck_users_age_positive
```

### কনস্ট্রাক্টরের প্যারামিটার { #checkconstraint-params }

```python
CheckConstraint(sqltext, name=None, deferrable=None, initially=None, table=None, info=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `sqltext` | শর্ত: স্ট্রিং (`"age >= 0"`) বা এক্সপ্রেশন (`users.c.age >= 0`)। |
| `name` | নাম (naming convention-এ `%(constraint_name)s`-এ বসে)। |
| `deferrable` | `DEFERRABLE` কি না। |
| `initially` | `INITIALLY` সেটিং। |
| `table` | যে টেবিলে যুক্ত হবে (সাধারণত `Table()`-এর ভেতরে দিলে নিজেই)। |
| `info` | নিজের মেটাডেটার dict। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #checkconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`is_column_level`](#checkconstraint-is-column-level) | প্রপার্টি | কলামের ভেতরে (কলাম-স্তরে) দেওয়া কনস্ট্রেইন্ট কি না। |
| [`sqltext`](#checkconstraint-sqltext) | অ্যাট্রিবিউট | শর্তের SQL এক্সপ্রেশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CheckConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`ColumnCollectionConstraint` থেকে:** [`c`](#columncollectionconstraint-c) · [`columns`](#columncollectionconstraint-columns) · [`contains_column()`](#columncollectionconstraint-contains-column)

**`Constraint` থেকে:** [`copy()`](#constraint-copy) · [`ddl_if()`](#constraint-ddl-if) · [`table`](#constraint-table)

///

### `CheckConstraint.is_column_level` { #checkconstraint-is-column-level }

**ধরন:** প্রপার্টি

কলামের ভেতরে (কলাম-স্তরে) দেওয়া কনস্ট্রেইন্ট কি না।

**উদাহরণ:**

```python
c = Column("qty", Integer, CheckConstraint("qty > 0"))
Table("t", MetaData(), c)
print(next(iter(c.constraints)).is_column_level)   # True
```

### `CheckConstraint.sqltext` { #checkconstraint-sqltext }

**ধরন:** অ্যাট্রিবিউট

শর্তের SQL এক্সপ্রেশন।

**উদাহরণ:**

```python
print(ck(users).sqltext)   # age >= 0
```

## `ForeignKeyConstraint` { #foreignkeyconstraint }

```python
from sqlalchemy import ForeignKeyConstraint
```

টেবিল-স্তরের ফরেন কি: এক বা একাধিক স্থানীয় কলাম অন্য টেবিলের কলামকে রেফার করে। একক কলামে `Column(..., ForeignKey("users.id"))` লেখাই সহজ (ভেতরে এটিই তৈরি হয়); composite ফরেন কি-তে এটি লাগে।

**উদাহরণ:**

```python
m = MetaData()
Table("products", m, Column("shop_id", Integer, primary_key=True), Column("sku", String(20), primary_key=True))
items = Table("cart_items", m, Column("id", Integer, primary_key=True), Column("shop_id", Integer), Column("sku", String(20)),
              ForeignKeyConstraint(["shop_id", "sku"], ["products.shop_id", "products.sku"], ondelete="RESTRICT"))
print([line.strip() for line in CreateTable(items).compile(dialect=postgresql.dialect()).string.splitlines() if "FOREIGN" in line])
# ['FOREIGN KEY(shop_id, sku) REFERENCES products (shop_id, sku) ON DELETE RESTRICT']
```

### কনস্ট্রাক্টরের প্যারামিটার { #foreignkeyconstraint-params }

```python
ForeignKeyConstraint(columns, refcolumns, name=None, onupdate=None, ondelete=None, deferrable=None, initially=None, use_alter=False, link_to_name=False, match=None, table=None, info=None, comment=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | স্থানীয় কলামগুলো (নাম বা অবজেক্ট)। |
| `refcolumns` | লক্ষ্য কলামগুলো (`"টেবিল.কলাম"` স্ট্রিং বা অবজেক্ট), একই ক্রমে। |
| `name` | নাম। |
| `onupdate` | লক্ষ্য কলামের মান বদলালে কী হবে: `"CASCADE"`, `"SET NULL"`, `"RESTRICT"` … |
| `ondelete` | লক্ষ্য রো মুছলে কী হবে: `"CASCADE"` (সন্তানও মুছবে), `"SET NULL"`, `"RESTRICT"`। বিস্তারিত: [Relationship অধ্যায় §১০](../relationships.md#s10)। |
| `deferrable` | `DEFERRABLE` কি না। |
| `initially` | `INITIALLY` সেটিং। |
| `use_alter` | `True` দিলে CREATE TABLE-এর ভেতরে না বসিয়ে পরে আলাদা `ALTER TABLE ADD CONSTRAINT` দিয়ে যোগ হয় (দুই টেবিল পরস্পরকে রেফার করলে চক্র ভাঙতে)। |
| `link_to_name` | `True` দিলে `refcolumns`-এর স্ট্রিং কলামের key নয়, ডেটাবেসের আসল নাম ধরা হয়। |
| `match` | `MATCH FULL` / `MATCH PARTIAL` (composite FK-তে NULL-এর নিয়ম)। |
| `table` | যে টেবিলে যুক্ত হবে। |
| `info` | নিজের মেটাডেটার dict। |
| `comment` | comment। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন, যেমন PostgreSQL-এ `postgresql_not_valid=True`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #foreignkeyconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`column_keys`](#foreignkeyconstraint-column-keys) | প্রপার্টি | স্থানীয় কলামগুলোর key-এর তালিকা। |
| [`elements`](#foreignkeyconstraint-elements) | অ্যাট্রিবিউট | প্রতিটি কলাম-জোড়ার জন্য একটি করে `ForeignKey` অবজেক্টের তালিকা। |
| [`link_to_name`](#foreignkeyconstraint-link-to-name) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `link_to_name` সেটিং। |
| [`match`](#foreignkeyconstraint-match) | অ্যাট্রিবিউট | `MATCH` সেটিং (না দিলে `None`)। |
| [`ondelete`](#foreignkeyconstraint-ondelete) | অ্যাট্রিবিউট | `ON DELETE` নিয়ম। |
| [`onupdate`](#foreignkeyconstraint-onupdate) | অ্যাট্রিবিউট | `ON UPDATE` নিয়ম (না দিলে `None`)। |
| [`referred_table`](#foreignkeyconstraint-referred-table) | প্রপার্টি | যে টেবিলকে রেফার করা হচ্ছে। |
| [`use_alter`](#foreignkeyconstraint-use-alter) | অ্যাট্রিবিউট | আলাদা `ALTER TABLE` দিয়ে যোগ হবে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ForeignKeyConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`ColumnCollectionConstraint` থেকে:** [`c`](#columncollectionconstraint-c) · [`columns`](#columncollectionconstraint-columns) · [`contains_column()`](#columncollectionconstraint-contains-column)

**`Constraint` থেকে:** [`copy()`](#constraint-copy) · [`ddl_if()`](#constraint-ddl-if) · [`table`](#constraint-table)

///

### `ForeignKeyConstraint.column_keys` { #foreignkeyconstraint-column-keys }

**ধরন:** প্রপার্টি

স্থানীয় কলামগুলোর key-এর তালিকা।

**উদাহরণ:**

```python
print(fkc(orders).column_keys)   # ['user_id']
```

### `ForeignKeyConstraint.elements` { #foreignkeyconstraint-elements }

**ধরন:** অ্যাট্রিবিউট

প্রতিটি কলাম-জোড়ার জন্য একটি করে `ForeignKey` অবজেক্টের তালিকা।

**উদাহরণ:**

```python
print([fk.target_fullname for fk in fkc(orders).elements])   # ['users.id']
```

### `ForeignKeyConstraint.link_to_name` { #foreignkeyconstraint-link-to-name }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `link_to_name` সেটিং।

**উদাহরণ:**

```python
print(fkc(orders).link_to_name)   # False
```

### `ForeignKeyConstraint.match` { #foreignkeyconstraint-match }

**ধরন:** অ্যাট্রিবিউট

`MATCH` সেটিং (না দিলে `None`)।

**উদাহরণ:**

```python
print(fkc(orders).match)   # None
```

### `ForeignKeyConstraint.ondelete` { #foreignkeyconstraint-ondelete }

**ধরন:** অ্যাট্রিবিউট

`ON DELETE` নিয়ম।

**উদাহরণ:**

```python
print(fkc(orders).ondelete)   # CASCADE
```

### `ForeignKeyConstraint.onupdate` { #foreignkeyconstraint-onupdate }

**ধরন:** অ্যাট্রিবিউট

`ON UPDATE` নিয়ম (না দিলে `None`)।

**উদাহরণ:**

```python
print(fkc(orders).onupdate)   # None
```

### `ForeignKeyConstraint.referred_table` { #foreignkeyconstraint-referred-table }

**ধরন:** প্রপার্টি

যে টেবিলকে রেফার করা হচ্ছে।

**উদাহরণ:**

```python
print(fkc(orders).referred_table.name, fkc(orders).name)   # users fk_orders_user_id_users
```

### `ForeignKeyConstraint.use_alter` { #foreignkeyconstraint-use-alter }

**ধরন:** অ্যাট্রিবিউট

আলাদা `ALTER TABLE` দিয়ে যোগ হবে কি না।

**উদাহরণ:**

```python
print(fkc(orders).use_alter)   # False
```

## `ForeignKey` { #foreignkey }

```python
from sqlalchemy import ForeignKey
```

একটি কলাম-স্তরের ফরেন কি রেফারেন্স: `Column("user_id", ForeignKey("users.id"))`। টাইপ না দিলে লক্ষ্য কলামের টাইপ নেয়। ভেতরে একটি `ForeignKeyConstraint` তৈরি হয়। ORM-এ `mapped_column(ForeignKey("users.id"))`। লক্ষ্য রো না থাকলে INSERT-এ `IntegrityError`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    try:
        conn.execute(insert(orders).values(user_id=999))
    except exc.IntegrityError as e:
        print(type(e.orig).__name__)   # ForeignKeyViolation
print(orders.c.user_id.type)          # INTEGER  (users.id থেকে নেওয়া)
```

### কনস্ট্রাক্টরের প্যারামিটার { #foreignkey-params }

```python
ForeignKey(column, use_alter=False, name=None, onupdate=None, ondelete=None, deferrable=None, initially=None, link_to_name=False, match=None, info=None, comment=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | লক্ষ্য: `"টেবিল.কলাম"` (বা `"স্কিমা.টেবিল.কলাম"`) স্ট্রিং, বা কলাম অবজেক্ট। |
| `use_alter` | আলাদা `ALTER TABLE` দিয়ে যোগ (চক্রাকার নির্ভরতায়)। |
| `name` | কনস্ট্রেইন্টের নাম। |
| `onupdate` | `ON UPDATE` নিয়ম। |
| `ondelete` | `ON DELETE` নিয়ম (`"CASCADE"`, `"SET NULL"` …)। |
| `deferrable` | `DEFERRABLE` কি না। |
| `initially` | `INITIALLY` সেটিং। |
| `link_to_name` | স্ট্রিং-লক্ষ্যে কলামের key-এর বদলে ডেটাবেস-নাম ধরা। |
| `match` | `MATCH` নিয়ম। |
| `info` | নিজের মেটাডেটার dict। |
| `comment` | comment। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #foreignkey-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`column`](#foreignkey-column) | প্রপার্টি | লক্ষ্য `Column` অবজেক্ট (স্ট্রিং দেওয়া থাকলে টেবিল খুঁজে বের করে)। |
| [`constraint`](#foreignkey-constraint) | অ্যাট্রিবিউট | এই রেফারেন্স যে `ForeignKeyConstraint`-এর অংশ। |
| [`copy()`](#foreignkey-copy) | মেথড ⚠️ deprecated | কপি (১.৪ থেকে বাতিলের পথে)। |
| [`get_referent()`](#foreignkey-get-referent) | মেথড | একটি টেবিল (বা alias) দিলে তার ভেতরে এই ফরেন কি-র লক্ষ্য কলামটি দেয়; না থাকলে `None`। |
| [`parent`](#foreignkey-parent) | অ্যাট্রিবিউট | যে (স্থানীয়) কলামে এই ফরেন কি দেওয়া। |
| [`references()`](#foreignkey-references) | মেথড | এই ফরেন কি দেওয়া টেবিলকে রেফার করে কি না। |
| [`target_column`](#foreignkey-target-column) | প্রপার্টি (internal) | লক্ষ্য হিসেবে সরাসরি কলাম অবজেক্ট দেওয়া হলে সেটি; স্ট্রিং দেওয়া হলে এরর। |
| [`target_fullname`](#foreignkey-target-fullname) | প্রপার্টি | লক্ষ্যের ডট-যুক্ত পূর্ণ নাম (`"users.id"`)। |
| [`target_table_key`](#foreignkey-target-table-key) | প্রপার্টি | লক্ষ্য টেবিলের `MetaData.tables` key। |
| [`target_tokens`](#foreignkey-target-tokens) | প্রপার্টি | লক্ষ্যকে `(স্কিমা, টেবিল, কলাম)` টুকরোয় ভাগ করে (২.১-এ একটি named tuple `ForeignKeyTarget`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ForeignKey`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`Constraint` থেকে:** [`comment`](#constraint-comment) · [`deferrable`](#constraint-deferrable) · [`initially`](#constraint-initially) · [`name`](#constraint-name)

**`ForeignKeyConstraint` থেকে:** [`link_to_name`](#foreignkeyconstraint-link-to-name) · [`match`](#foreignkeyconstraint-match) · [`ondelete`](#foreignkeyconstraint-ondelete) · [`onupdate`](#foreignkeyconstraint-onupdate) · [`use_alter`](#foreignkeyconstraint-use-alter)

///

### `ForeignKey.column` { #foreignkey-column }

**ধরন:** প্রপার্টি

লক্ষ্য `Column` অবজেক্ট (স্ট্রিং দেওয়া থাকলে টেবিল খুঁজে বের করে)।

**উদাহরণ:**

```python
fk = next(iter(orders.c.user_id.foreign_keys))
print(fk.column is users.c.id)   # True
```

### `ForeignKey.constraint` { #foreignkey-constraint }

**ধরন:** অ্যাট্রিবিউট

এই রেফারেন্স যে `ForeignKeyConstraint`-এর অংশ।

**উদাহরণ:**

```python
fk = next(iter(orders.c.user_id.foreign_keys))
print(fk.constraint.name)   # fk_orders_user_id_users
```

### `ForeignKey.copy()` { #foreignkey-copy }

```python
ForeignKey.copy(*, schema=None, **kw)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

কপি (১.৪ থেকে বাতিলের পথে)।

### `ForeignKey.get_referent()` { #foreignkey-get-referent }

```python
ForeignKey.get_referent(table)
```

**ধরন:** মেথড

একটি টেবিল (বা alias) দিলে তার ভেতরে এই ফরেন কি-র লক্ষ্য কলামটি দেয়; না থাকলে `None`।

**উদাহরণ:**

```python
fk = next(iter(orders.c.user_id.foreign_keys))
print(fk.get_referent(users.alias("u2")))   # u2.id
```

### `ForeignKey.parent` { #foreignkey-parent }

**ধরন:** অ্যাট্রিবিউট

যে (স্থানীয়) কলামে এই ফরেন কি দেওয়া।

**উদাহরণ:**

```python
fk = next(iter(orders.c.user_id.foreign_keys))
print(fk.parent)   # orders.user_id
```

### `ForeignKey.references()` { #foreignkey-references }

```python
ForeignKey.references(table)
```

**ধরন:** মেথড

এই ফরেন কি দেওয়া টেবিলকে রেফার করে কি না।

**উদাহরণ:**

```python
fk = next(iter(orders.c.user_id.foreign_keys))
print(fk.references(users), fk.references(orders))   # True False
```

### `ForeignKey.target_column` { #foreignkey-target-column }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লক্ষ্য হিসেবে সরাসরি কলাম অবজেক্ট দেওয়া হলে সেটি; স্ট্রিং দেওয়া হলে এরর।

### `ForeignKey.target_fullname` { #foreignkey-target-fullname }

**ধরন:** প্রপার্টি

লক্ষ্যের ডট-যুক্ত পূর্ণ নাম (`"users.id"`)।

**উদাহরণ:**

```python
print(next(iter(orders.c.user_id.foreign_keys)).target_fullname)   # users.id
```

### `ForeignKey.target_table_key` { #foreignkey-target-table-key }

**ধরন:** প্রপার্টি

লক্ষ্য টেবিলের `MetaData.tables` key।

**উদাহরণ:**

```python
print(next(iter(orders.c.user_id.foreign_keys)).target_table_key)   # users
```

### `ForeignKey.target_tokens` { #foreignkey-target-tokens }

**ধরন:** প্রপার্টি

লক্ষ্যকে `(স্কিমা, টেবিল, কলাম)` টুকরোয় ভাগ করে (২.১-এ একটি named tuple `ForeignKeyTarget`)।

**উদাহরণ:**

```python
print(next(iter(orders.c.user_id.foreign_keys)).target_tokens)   # ForeignKeyTarget(schema=None, table_name='users', column_name='id')
```

## `conv` { #conv }

```python
from sqlalchemy.schema import conv
```

একটি স্ট্রিং যা বলে "এই নাম **চূড়ান্ত**, naming convention আর প্রয়োগ কোরো না"। Alembic যখন naming convention দিয়ে তৈরি নাম ফেরত দেয়, তখন দ্বিগুণ প্রয়োগ এড়াতে এটি ব্যবহার করে। Python-এর `str`-এর সাবক্লাস, তাই str-এর সব মেথড আছে (আলাদা তালিকা দেওয়া হয়নি)।

**উদাহরণ:**

```python
m = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(constraint_name)s"})
t = Table("t", m, Column("x", Integer), CheckConstraint("x > 0", name=conv("my_exact_name")))
print(next(c.name for c in t.constraints if isinstance(c, CheckConstraint)))   # my_exact_name
```

## ইনডেক্স { #index-group }

## `Index` { #index }

```python
from sqlalchemy import Index
```

একটি ইনডেক্স: খোঁজা/সাজানো দ্রুত করে। কলাম, একাধিক কলাম, বা এক্সপ্রেশন (`func.lower(email)`) দেওয়া যায়; `unique=True` দিলে unique index। `Table()`-এর ভেতরে, বা বাইরে কলাম দিয়ে তৈরি করলে নিজে থেকেই টেবিলে যুক্ত হয়। PostgreSQL অপশন: `postgresql_where` (partial index), `postgresql_using="gin"`, `postgresql_include`, `postgresql_concurrently`, `postgresql_ops`।

**উদাহরণ:**

```python
ix = Index("ix_users_lower_email", func.lower(users.c.email), unique=True)
print(CreateIndex(ix).compile(dialect=postgresql.dialect()))   # CREATE UNIQUE INDEX ix_users_lower_email ON users (lower(email))
print([i["name"] for i in inspect(engine).get_indexes("orders")])   # ['ix_orders_status']
```

### কনস্ট্রাক্টরের প্যারামিটার { #index-params }

```python
Index(name, *expressions, unique=False, quote=None, info=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | ইনডেক্সের নাম (`None` দিলে naming convention থেকে)। |
| `expressions` | কলাম, কলামের নাম, বা SQL এক্সপ্রেশন। |
| `unique` | `True` দিলে `CREATE UNIQUE INDEX`। |
| `quote` | নাম জোর করে quote হবে কি না। |
| `info` | নিজের মেটাডেটার dict। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন: `postgresql_where`, `postgresql_using`, `postgresql_include`, `postgresql_ops`, `postgresql_concurrently`, `mysql_length` … |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #index-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`create()`](#index-create) | মেথড | শুধু এই ইনডেক্সের `CREATE INDEX` চালায় (টেবিল আগে থেকে থাকলে, মাইগ্রেশন ছাড়া দ্রুত যোগ করতে)। |
| [`drop()`](#index-drop) | মেথড | `DROP INDEX` চালায়। |
| [`expressions`](#index-expressions) | অ্যাট্রিবিউট | ইনডেক্সের কলাম/এক্সপ্রেশনগুলো। |
| [`name`](#index-name) | অ্যাট্রিবিউট | ইনডেক্সের নাম। |
| [`table`](#index-table) | অ্যাট্রিবিউট | ইনডেক্সটি যে টেবিলের। |
| [`unique`](#index-unique) | অ্যাট্রিবিউট | unique index কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Index`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`ColumnCollectionConstraint` থেকে:** [`c`](#columncollectionconstraint-c) · [`columns`](#columncollectionconstraint-columns)

**`Constraint` থেকে:** [`ddl_if()`](#constraint-ddl-if)

///

### `Index.create()` { #index-create }

```python
Index.create(bind, checkfirst=<CheckFirst.NONE: 0>)
```

**ধরন:** মেথড

শুধু এই ইনডেক্সের `CREATE INDEX` চালায় (টেবিল আগে থেকে থাকলে, মাইগ্রেশন ছাড়া দ্রুত যোগ করতে)।

**উদাহরণ:**

```python
ix = Index("ix_users_age", users.c.age)
ix.create(engine)
print("ix_users_age" in [i["name"] for i in inspect(engine).get_indexes("users")])   # True
```

### `Index.drop()` { #index-drop }

```python
Index.drop(bind, checkfirst=<CheckFirst.NONE: 0>)
```

**ধরন:** মেথড

`DROP INDEX` চালায়।

**উদাহরণ:**

```python
ix = next(iter(orders.indexes))
ix.drop(engine)
print(inspect(engine).get_indexes("orders"))   # []
```

### `Index.expressions` { #index-expressions }

**ধরন:** অ্যাট্রিবিউট

ইনডেক্সের কলাম/এক্সপ্রেশনগুলো।

**উদাহরণ:**

```python
print([str(e) for e in Index("ix_x", func.lower(users.c.email)).expressions])   # ['lower(users.email)']
```

### `Index.name` { #index-name }

**ধরন:** অ্যাট্রিবিউট

ইনডেক্সের নাম।

**উদাহরণ:**

```python
print(next(iter(orders.indexes)).name)   # ix_orders_status
```

### `Index.table` { #index-table }

**ধরন:** অ্যাট্রিবিউট

ইনডেক্সটি যে টেবিলের।

**উদাহরণ:**

```python
print(next(iter(orders.indexes)).table.name)   # orders
```

### `Index.unique` { #index-unique }

**ধরন:** অ্যাট্রিবিউট

unique index কি না।

**উদাহরণ:**

```python
print(next(iter(orders.indexes)).unique)   # False
```

## ডিফল্ট ও generated মান { #defaultgenerator-group }

## `DefaultGenerator` { #defaultgenerator }

```python
from sqlalchemy.schema import DefaultGenerator
```

কলামের যেসব ডিফল্ট SQLAlchemy নিজে **চালাতে** পারে (Python মান/ফাংশন, SQL এক্সপ্রেশন, `Sequence`) তাদের মূল ক্লাস। নিচের `is_*` flag-গুলো দিয়ে ডিফল্টের ধরন জানা যায়।

**উদাহরণ:**

```python
d = Column("status", String, default="new").default
print(isinstance(d, DefaultGenerator), d.is_scalar, d.is_callable)   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #defaultgenerator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`has_arg`](#defaultgenerator-has-arg) | অ্যাট্রিবিউট | ডিফল্টের একটি মান/ফাংশন (`arg`) আছে কি না। |
| [`is_callable`](#defaultgenerator-is-callable) | অ্যাট্রিবিউট | ডিফল্টটি একটি Python ফাংশন কি না (প্রতি INSERT-এ ডাকা হয়)। |
| [`is_identity`](#defaultgenerator-is-identity) | অ্যাট্রিবিউট | এটি `Identity` কি না। |
| [`is_scalar`](#defaultgenerator-is-scalar) | অ্যাট্রিবিউট | ডিফল্টটি একটি স্থির মান কি না। |
| [`is_sentinel`](#defaultgenerator-is-sentinel) | অ্যাট্রিবিউট (internal) | insert sentinel-এর ডিফল্ট কি না। |
| [`is_sequence`](#defaultgenerator-is-sequence) | অ্যাট্রিবিউট | এটি `Sequence` কি না। |
| [`is_server_default`](#defaultgenerator-is-server-default) | অ্যাট্রিবিউট | ডেটাবেস-দিকের ডিফল্ট কি না (`DefaultGenerator`-এ `False`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DefaultGenerator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

**`Table` থেকে:** [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`info`](schema.md#table-info)

///

### `DefaultGenerator.has_arg` { #defaultgenerator-has-arg }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টের একটি মান/ফাংশন (`arg`) আছে কি না।

**উদাহরণ:**

```python
print(Column("x", Integer, default=0).default.has_arg)   # True
```

### `DefaultGenerator.is_callable` { #defaultgenerator-is-callable }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টটি একটি Python ফাংশন কি না (প্রতি INSERT-এ ডাকা হয়)।

**উদাহরণ:**

```python
print(Column("x", Integer, default=lambda: 1).default.is_callable)   # True
```

### `DefaultGenerator.is_identity` { #defaultgenerator-is-identity }

**ধরন:** অ্যাট্রিবিউট

এটি `Identity` কি না।

**উদাহরণ:**

```python
print(Column("x", Integer, default=0).default.is_identity)   # False
```

### `DefaultGenerator.is_scalar` { #defaultgenerator-is-scalar }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টটি একটি স্থির মান কি না।

**উদাহরণ:**

```python
print(Column("x", Integer, default=0).default.is_scalar)   # True
```

### `DefaultGenerator.is_sentinel` { #defaultgenerator-is-sentinel }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

insert sentinel-এর ডিফল্ট কি না।

### `DefaultGenerator.is_sequence` { #defaultgenerator-is-sequence }

**ধরন:** অ্যাট্রিবিউট

এটি `Sequence` কি না।

**উদাহরণ:**

```python
print(Sequence("s").is_sequence)   # True
```

### `DefaultGenerator.is_server_default` { #defaultgenerator-is-server-default }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস-দিকের ডিফল্ট কি না (`DefaultGenerator`-এ `False`)।

**উদাহরণ:**

```python
print(Column("x", Integer, default=0).default.is_server_default)   # False
```

## `ColumnDefault` { #columndefault }

```python
from sqlalchemy import ColumnDefault
```

`Column(default=...)` / `onupdate=...`-এর পেছনের অবজেক্ট: Python দিকের ডিফল্ট। মান দেওয়ার ধরন অনুযায়ী আসলে একটি নির্দিষ্ট সাবক্লাস তৈরি হয়: স্থির মান, Python ফাংশন (`datetime.now`, `uuid4`; ফাংশনটি একটি `context` আর্গুমেন্টও নিতে পারে), বা SQL এক্সপ্রেশন (`func.now()`; INSERT-এর ভেতরে বসে)। `.arg`-এ আসল মান।

**উদাহরণ:**

```python
m = MetaData()
t = Table("t", m, Column("id", Integer, primary_key=True),
          Column("code", String(10), default=lambda ctx: f"C-{ctx.get_current_parameters()['id']}"),
          Column("made", DateTime, default=func.now()))
m.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(t).values(id=7))
    print(conn.execute(select(t.c.code, t.c.made.is_not(None))).one())   # ('C-7', True)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columndefault-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`arg`](#columndefault-arg) | অ্যাট্রিবিউট | ডিফল্টের আসল মান, ফাংশন, বা SQL এক্সপ্রেশন। |
| [`column`](#columndefault-column) | অ্যাট্রিবিউট | ডিফল্টটি যে কলামের। |
| [`compare()`](#columndefault-compare) | মেথড (internal) | দুটি ডিফল্ট সমান কি না তুলনা (Alembic autogenerate ইত্যাদির জন্য)। |
| [`compare_argument()`](#columndefault-compare-argument) | মেথড (internal) | শুধু `arg` অংশ তুলনা করে। |
| [`for_update`](#columndefault-for-update) | অ্যাট্রিবিউট | `onupdate`-এর ডিফল্ট হলে `True`, INSERT-এর হলে `False`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnDefault`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

**`Table` থেকে:** [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`info`](schema.md#table-info)

**`DefaultGenerator` থেকে:** [`has_arg`](#defaultgenerator-has-arg) · [`is_callable`](#defaultgenerator-is-callable) · [`is_identity`](#defaultgenerator-is-identity) · [`is_scalar`](#defaultgenerator-is-scalar) · [`is_sentinel`](#defaultgenerator-is-sentinel) · [`is_sequence`](#defaultgenerator-is-sequence) · [`is_server_default`](#defaultgenerator-is-server-default)

///

### `ColumnDefault.arg` { #columndefault-arg }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টের আসল মান, ফাংশন, বা SQL এক্সপ্রেশন।

**উদাহরণ:**

```python
print(Column("x", Integer, default=5).default.arg)   # 5
```

### `ColumnDefault.column` { #columndefault-column }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টটি যে কলামের।

**উদাহরণ:**

```python
c = Column("x", Integer, default=5)
print(c.default.column is c)   # True
```

### `ColumnDefault.compare()` { #columndefault-compare }

```python
ColumnDefault.compare(other)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

দুটি ডিফল্ট সমান কি না তুলনা (Alembic autogenerate ইত্যাদির জন্য)।

### `ColumnDefault.compare_argument()` { #columndefault-compare-argument }

```python
ColumnDefault.compare_argument(argument)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

শুধু `arg` অংশ তুলনা করে।

### `ColumnDefault.for_update` { #columndefault-for-update }

**ধরন:** অ্যাট্রিবিউট

`onupdate`-এর ডিফল্ট হলে `True`, INSERT-এর হলে `False`।

**উদাহরণ:**

```python
print(Column("u", DateTime, onupdate=func.now()).onupdate.for_update)   # True
```

## `FetchedValue` { #fetchedvalue }

```python
from sqlalchemy import FetchedValue
```

একটি চিহ্ন: "এই কলামের মান **ডেটাবেস নিজে** বসায় (trigger বা DDL-এর ডিফল্ট দিয়ে), SQLAlchemy কিছু বানাবে না"। ফলে ORM জানে INSERT/UPDATE-এর পর মানটি ডেটাবেস থেকে আবার পড়তে হবে। সাধারণত `server_onupdate=FetchedValue()` হিসেবে।

**উদাহরণ:**

```python
c = Column("updated_at", DateTime, server_default=FetchedValue(), server_onupdate=FetchedValue(for_update=True))
print(c.server_default.is_server_default, c.server_onupdate.for_update)   # True True
```

### কনস্ট্রাক্টরের প্যারামিটার { #fetchedvalue-params }

```python
FetchedValue(for_update=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `for_update` | UPDATE-এর জন্য হলে `True`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #fetchedvalue-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`for_update`](#fetchedvalue-for-update) | অ্যাট্রিবিউট | UPDATE-এর জন্য কি না। |
| [`has_argument`](#fetchedvalue-has-argument) | অ্যাট্রিবিউট | DDL-এ বসানোর মতো কোনো মান আছে কি না (`FetchedValue`-এ `False`; `DefaultClause`-এ `True`)। |
| [`is_clause_element`](#fetchedvalue-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_identity`](#fetchedvalue-is-identity) | অ্যাট্রিবিউট | `Identity` কি না। |
| [`is_server_default`](#fetchedvalue-is-server-default) | অ্যাট্রিবিউট | ডেটাবেস-দিকের ডিফল্ট কি না (`True`)। |
| [`reflected`](#fetchedvalue-reflected) | অ্যাট্রিবিউট | ডেটাবেস থেকে reflection-এ পাওয়া কি না। |

### `FetchedValue.for_update` { #fetchedvalue-for-update }

**ধরন:** অ্যাট্রিবিউট

UPDATE-এর জন্য কি না।

**উদাহরণ:**

```python
print(FetchedValue().for_update)   # False
```

### `FetchedValue.has_argument` { #fetchedvalue-has-argument }

**ধরন:** অ্যাট্রিবিউট

DDL-এ বসানোর মতো কোনো মান আছে কি না (`FetchedValue`-এ `False`; `DefaultClause`-এ `True`)।

**উদাহরণ:**

```python
print(FetchedValue().has_argument, DefaultClause("x").has_argument)   # False True
```

### `FetchedValue.is_clause_element` { #fetchedvalue-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `FetchedValue.is_identity` { #fetchedvalue-is-identity }

**ধরন:** অ্যাট্রিবিউট

`Identity` কি না।

**উদাহরণ:**

```python
print(FetchedValue().is_identity, Identity().is_identity)   # False True
```

### `FetchedValue.is_server_default` { #fetchedvalue-is-server-default }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস-দিকের ডিফল্ট কি না (`True`)।

**উদাহরণ:**

```python
print(FetchedValue().is_server_default)   # True
```

### `FetchedValue.reflected` { #fetchedvalue-reflected }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস থেকে reflection-এ পাওয়া কি না।

**উদাহরণ:**

```python
m = MetaData()
t = Table("orders", m, autoload_with=engine)
print(t.c.status.server_default.reflected)   # True
```

## `DefaultClause` { #defaultclause }

```python
from sqlalchemy import DefaultClause
```

`server_default="..."`-এর পেছনের অবজেক্ট: DDL-এ `DEFAULT ...` বসায়। সাধারণত সরাসরি না লিখে `server_default=` দিন। মান স্ট্রিং (quote করে বসে), `text("...")` (হুবহু), বা `func.now()`।

**উদাহরণ:**

```python
print(orders.c.status.server_default.arg, type(orders.c.status.server_default).__name__)   # new DefaultClause
with engine.begin() as conn:
    conn.execute(text("INSERT INTO orders (user_id) VALUES (1)"))   # কাঁচা SQL-এও ডিফল্ট কাজ করে
    print(conn.execute(select(orders.c.status)).scalar())           # new
```

### কনস্ট্রাক্টরের প্যারামিটার { #defaultclause-params }

```python
DefaultClause(arg, for_update=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `arg` | ডিফল্ট মান: স্ট্রিং, `text()` বা SQL এক্সপ্রেশন। |
| `for_update` | UPDATE-এর জন্য কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #defaultclause-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`arg`](#defaultclause-arg) | অ্যাট্রিবিউট | ডিফল্টের মান/এক্সপ্রেশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DefaultClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FetchedValue` থেকে:** [`for_update`](#fetchedvalue-for-update) · [`has_argument`](#fetchedvalue-has-argument) · [`is_clause_element`](#fetchedvalue-is-clause-element) · [`is_identity`](#fetchedvalue-is-identity) · [`is_server_default`](#fetchedvalue-is-server-default) · [`reflected`](#fetchedvalue-reflected)

///

### `DefaultClause.arg` { #defaultclause-arg }

**ধরন:** অ্যাট্রিবিউট

ডিফল্টের মান/এক্সপ্রেশন।

**উদাহরণ:**

```python
print(DefaultClause(text("now()")).arg)   # now()
```

## `Sequence` { #sequence }

```python
from sqlalchemy import Sequence
```

ডেটাবেসের একটি **sequence** (ক্রমবর্ধমান সংখ্যা-উৎস)। কলামে দিলে INSERT-এ সেখান থেকে নতুন মান নেয়; নিজে নিজে `nextval` হিসেবেও ব্যবহার করা যায় (ইনভয়েস নম্বর ইত্যাদি)। PostgreSQL-এ নতুন টেবিলে সাধারণত `Identity` সহজ।

**উদাহরণ:**

```python
seq = Sequence("invoice_no_seq", start=5001, metadata=MetaData())
seq.create(engine)
with engine.connect() as conn:
    print(conn.scalar(seq.next_value()), conn.scalar(seq.next_value()))   # 5001 5002
```

### কনস্ট্রাক্টরের প্যারামিটার { #sequence-params }

```python
Sequence(name, start=None, increment=None, minvalue=None, maxvalue=None, nominvalue=None, nomaxvalue=None, cycle=None, schema=None, cache=None, order=None, data_type=None, optional=False, quote=None, metadata=None, quote_schema=None, for_update=False, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | sequence-এর নাম। |
| `start` | শুরুর মান। |
| `increment` | প্রতিবার কত বাড়বে। |
| `minvalue` | সর্বনিম্ন মান। |
| `maxvalue` | সর্বোচ্চ মান। |
| `nominvalue` | `NO MINVALUE`। |
| `nomaxvalue` | `NO MAXVALUE`। |
| `cycle` | সর্বোচ্চে পৌঁছালে আবার শুরু থেকে। |
| `schema` | স্কিমা। |
| `cache` | আগেভাগে কয়টি মান মেমরিতে রাখবে (দ্রুততর, কিন্তু ক্র্যাশে ফাঁক হতে পারে)। |
| `order` | (Oracle) ক্রম নিশ্চিত করা। |
| `data_type` | sequence-এর টাইপ (যেমন `BigInteger`)। |
| `optional` | `True` দিলে যেসব ডেটাবেসে অন্য auto-increment ব্যবস্থা আছে সেখানে sequence উপেক্ষা হয়। |
| `quote` | নাম জোর করে quote। |
| `metadata` | যে `MetaData`-তে নিবন্ধিত হবে (`create_all`/`drop_all`-এ সাথে তৈরি/মোছা হয়)। |
| `quote_schema` | স্কিমার নাম quote। |
| `for_update` | UPDATE-এর ডিফল্ট হিসেবে। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sequence-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache`](#sequence-cache) | অ্যাট্রিবিউট | `CACHE` সেটিং। |
| [`column`](#sequence-column) | অ্যাট্রিবিউট | যে কলামে sequence দেওয়া (না থাকলে `None`)। |
| [`create()`](#sequence-create) | মেথড | `CREATE SEQUENCE` চালায়। |
| [`cycle`](#sequence-cycle) | অ্যাট্রিবিউট | `CYCLE` সেটিং। |
| [`data_type`](#sequence-data-type) | অ্যাট্রিবিউট | sequence-এর টাইপ। |
| [`drop()`](#sequence-drop) | মেথড | `DROP SEQUENCE` চালায়। |
| [`for_update`](#sequence-for-update) | অ্যাট্রিবিউট | UPDATE-এর জন্য কি না। |
| [`increment`](#sequence-increment) | অ্যাট্রিবিউট | `INCREMENT BY` মান। |
| [`maxvalue`](#sequence-maxvalue) | অ্যাট্রিবিউট | `MAXVALUE`। |
| [`metadata`](#sequence-metadata) | অ্যাট্রিবিউট | নিবন্ধিত `MetaData`। |
| [`minvalue`](#sequence-minvalue) | অ্যাট্রিবিউট | `MINVALUE`। |
| [`name`](#sequence-name) | অ্যাট্রিবিউট | sequence-এর নাম। |
| [`next_value()`](#sequence-next-value) | মেথড | পরের মান আনার SQL এক্সপ্রেশন (`nextval('...')`); SELECT বা INSERT-এর মানে বসানো যায়। |
| [`nomaxvalue`](#sequence-nomaxvalue) | অ্যাট্রিবিউট | `NO MAXVALUE` কি না। |
| [`nominvalue`](#sequence-nominvalue) | অ্যাট্রিবিউট | `NO MINVALUE` কি না। |
| [`optional`](#sequence-optional) | অ্যাট্রিবিউট | ঐচ্ছিক sequence কি না। |
| [`order`](#sequence-order) | প্রপার্টি | (Oracle) `ORDER` সেটিং; আসলে `oracle_order` ডায়ালেক্ট অপশনের আরেক নাম। |
| [`schema`](#sequence-schema) | অ্যাট্রিবিউট | স্কিমা। |
| [`start`](#sequence-start) | অ্যাট্রিবিউট | `START WITH` মান। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Sequence`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`argument_for()`](select.md#select-argument-for) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`execution_options()`](select.md#select-execution-options) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`options()`](select.md#select-options) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

**`Table` থেকে:** [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`info`](schema.md#table-info)

**`DefaultGenerator` থেকে:** [`has_arg`](#defaultgenerator-has-arg) · [`is_callable`](#defaultgenerator-is-callable) · [`is_identity`](#defaultgenerator-is-identity) · [`is_scalar`](#defaultgenerator-is-scalar) · [`is_sentinel`](#defaultgenerator-is-sentinel) · [`is_sequence`](#defaultgenerator-is-sequence) · [`is_server_default`](#defaultgenerator-is-server-default)

///

### `Sequence.cache` { #sequence-cache }

**ধরন:** অ্যাট্রিবিউট

`CACHE` সেটিং।

**উদাহরণ:**

```python
print(Sequence("s", cache=20).cache)   # 20
```

### `Sequence.column` { #sequence-column }

**ধরন:** অ্যাট্রিবিউট

যে কলামে sequence দেওয়া (না থাকলে `None`)।

**উদাহরণ:**

```python
s = Sequence("s")
c = Column("id", Integer, s, primary_key=True)
print(s.column is c)   # True
```

### `Sequence.create()` { #sequence-create }

```python
Sequence.create(bind, checkfirst=<CheckFirst.SEQUENCES: 16>)
```

**ধরন:** মেথড

`CREATE SEQUENCE` চালায়।

**উদাহরণ:**

```python
Sequence("tmp_seq").create(engine)
print("tmp_seq" in inspect(engine).get_sequence_names())   # True
```

### `Sequence.cycle` { #sequence-cycle }

**ধরন:** অ্যাট্রিবিউট

`CYCLE` সেটিং।

**উদাহরণ:**

```python
print(Sequence("s", cycle=True).cycle)   # True
```

### `Sequence.data_type` { #sequence-data-type }

**ধরন:** অ্যাট্রিবিউট

sequence-এর টাইপ।

**উদাহরণ:**

```python
from sqlalchemy import BigInteger
print(Sequence("s", data_type=BigInteger).data_type)   # BIGINT
```

### `Sequence.drop()` { #sequence-drop }

```python
Sequence.drop(bind, checkfirst=<CheckFirst.SEQUENCES: 16>)
```

**ধরন:** মেথড

`DROP SEQUENCE` চালায়।

**উদাহরণ:**

```python
s = Sequence("tmp_seq"); s.create(engine); s.drop(engine)
print("tmp_seq" in inspect(engine).get_sequence_names())   # False
```

### `Sequence.for_update` { #sequence-for-update }

**ধরন:** অ্যাট্রিবিউট

UPDATE-এর জন্য কি না।

**উদাহরণ:**

```python
print(Sequence("s").for_update)   # False
```

### `Sequence.increment` { #sequence-increment }

**ধরন:** অ্যাট্রিবিউট

`INCREMENT BY` মান।

**উদাহরণ:**

```python
print(Sequence("s", increment=10).increment)   # 10
```

### `Sequence.maxvalue` { #sequence-maxvalue }

**ধরন:** অ্যাট্রিবিউট

`MAXVALUE`।

**উদাহরণ:**

```python
print(Sequence("s", maxvalue=999).maxvalue)   # 999
```

### `Sequence.metadata` { #sequence-metadata }

**ধরন:** অ্যাট্রিবিউট

নিবন্ধিত `MetaData`।

**উদাহরণ:**

```python
m = MetaData()
print(Sequence("s", metadata=m).metadata is m)   # True
```

### `Sequence.minvalue` { #sequence-minvalue }

**ধরন:** অ্যাট্রিবিউট

`MINVALUE`।

**উদাহরণ:**

```python
print(Sequence("s", minvalue=1).minvalue)   # 1
```

### `Sequence.name` { #sequence-name }

**ধরন:** অ্যাট্রিবিউট

sequence-এর নাম।

**উদাহরণ:**

```python
print(Sequence("order_seq").name)   # order_seq
```

### `Sequence.next_value()` { #sequence-next-value }

```python
Sequence.next_value()
```

**ধরন:** মেথড

পরের মান আনার SQL এক্সপ্রেশন (`nextval('...')`); SELECT বা INSERT-এর মানে বসানো যায়।

**উদাহরণ:**

```python
s = Sequence("ticket_seq", start=100); s.create(engine)
print(s.next_value().compile(dialect=postgresql.dialect()))   # nextval('ticket_seq')
```

### `Sequence.nomaxvalue` { #sequence-nomaxvalue }

**ধরন:** অ্যাট্রিবিউট

`NO MAXVALUE` কি না।

**উদাহরণ:**

```python
print(Sequence("s", nomaxvalue=True).nomaxvalue)   # True
```

### `Sequence.nominvalue` { #sequence-nominvalue }

**ধরন:** অ্যাট্রিবিউট

`NO MINVALUE` কি না।

**উদাহরণ:**

```python
print(Sequence("s", nominvalue=True).nominvalue)   # True
```

### `Sequence.optional` { #sequence-optional }

**ধরন:** অ্যাট্রিবিউট

ঐচ্ছিক sequence কি না।

**উদাহরণ:**

```python
print(Sequence("s", optional=True).optional)   # True
```

### `Sequence.order` { #sequence-order }

**ধরন:** প্রপার্টি

(Oracle) `ORDER` সেটিং; আসলে `oracle_order` ডায়ালেক্ট অপশনের আরেক নাম।

**উদাহরণ:**

```python
print(Sequence("s").order)   # None
```

### `Sequence.schema` { #sequence-schema }

**ধরন:** অ্যাট্রিবিউট

স্কিমা।

**উদাহরণ:**

```python
print(Sequence("s", schema="billing").schema)   # billing
```

### `Sequence.start` { #sequence-start }

**ধরন:** অ্যাট্রিবিউট

`START WITH` মান।

**উদাহরণ:**

```python
print(Sequence("s", start=5001).start)   # 5001
```

## `Identity` { #identity }

```python
from sqlalchemy import Identity
```

SQL স্ট্যান্ডার্ড **identity column**: `GENERATED BY DEFAULT AS IDENTITY` (বা `ALWAYS`)। PostgreSQL ১০+-এ `SERIAL`-এর আধুনিক বিকল্প; ডেটাবেস নিজে মান দেয়।

**উদাহরণ:**

```python
print([l.strip() for l in CreateTable(orders).compile(dialect=postgresql.dialect()).string.splitlines() if "IDENTITY" in l])
# ['id INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 1000),']
with engine.begin() as conn:
    print(conn.execute(insert(orders).values(user_id=1).returning(orders.c.id)).scalar())   # 1000
```

### কনস্ট্রাক্টরের প্যারামিটার { #identity-params }

```python
Identity(always=False, on_null=None, start=None, increment=None, minvalue=None, maxvalue=None, nominvalue=None, nomaxvalue=None, cycle=None, cache=None, order=None, **dialect_kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `always` | `True` দিলে `GENERATED ALWAYS` (হাতে মান দেওয়া যাবে না); ডিফল্ট `BY DEFAULT`। |
| `on_null` | (Oracle) `ON NULL`। |
| `start` | শুরুর মান। |
| `increment` | প্রতিবার কত বাড়বে। |
| `minvalue` | সর্বনিম্ন মান। |
| `maxvalue` | সর্বোচ্চ মান। |
| `nominvalue` | `NO MINVALUE`। |
| `nomaxvalue` | `NO MAXVALUE`। |
| `cycle` | শেষে আবার শুরু। |
| `cache` | cache-এর আকার। |
| `order` | (Oracle) `ORDER`। |
| `dialect_kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #identity-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`always`](#identity-always) | অ্যাট্রিবিউট | `GENERATED ALWAYS` কি না। |
| [`copy()`](#identity-copy) | মেথড ⚠️ deprecated | কপি (১.৪ থেকে বাতিলের পথে)। |
| [`on_null`](#identity-on-null) | প্রপার্টি | (Oracle) `ON NULL`; `oracle_on_null` ডায়ালেক্ট অপশনের আরেক নাম। |
| [`order`](#identity-order) | প্রপার্টি | (Oracle) `ORDER`; `oracle_order` অপশনের আরেক নাম। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Identity`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`Sequence` থেকে:** [`cache`](#sequence-cache) · [`column`](#sequence-column) · [`cycle`](#sequence-cycle) · [`increment`](#sequence-increment) · [`maxvalue`](#sequence-maxvalue) · [`minvalue`](#sequence-minvalue) · [`nomaxvalue`](#sequence-nomaxvalue) · [`nominvalue`](#sequence-nominvalue) · [`start`](#sequence-start)

**`FetchedValue` থেকে:** [`has_argument`](#fetchedvalue-has-argument) · [`is_clause_element`](#fetchedvalue-is-clause-element) · [`is_identity`](#fetchedvalue-is-identity) · [`is_server_default`](#fetchedvalue-is-server-default) · [`reflected`](#fetchedvalue-reflected)

///

### `Identity.always` { #identity-always }

**ধরন:** অ্যাট্রিবিউট

`GENERATED ALWAYS` কি না।

**উদাহরণ:**

```python
print(Identity(always=True).always)   # True
```

### `Identity.copy()` { #identity-copy }

```python
Identity.copy(**kw)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

কপি (১.৪ থেকে বাতিলের পথে)।

### `Identity.on_null` { #identity-on-null }

**ধরন:** প্রপার্টি

(Oracle) `ON NULL`; `oracle_on_null` ডায়ালেক্ট অপশনের আরেক নাম।

**উদাহরণ:**

```python
print(Identity().on_null)   # None
```

### `Identity.order` { #identity-order }

**ধরন:** প্রপার্টি

(Oracle) `ORDER`; `oracle_order` অপশনের আরেক নাম।

**উদাহরণ:**

```python
print(Identity().order)   # None
```

## `Computed` { #computed }

```python
from sqlalchemy import Computed
```

**generated column**: মান ডেটাবেস নিজে অন্য কলাম থেকে হিসাব করে (`GENERATED ALWAYS AS (price * qty) STORED`)। হাতে মান দেওয়া যায় না; INSERT/UPDATE-এর পর ORM মানটি আবার পড়ে নেয়।

**উদাহরণ:**

```python
with engine.begin() as conn:
    conn.execute(insert(orders).values(user_id=1, price=50, qty=3))
    print(conn.execute(select(orders.c.total)).scalar())   # 150
```

### কনস্ট্রাক্টরের প্যারামিটার { #computed-params }

```python
Computed(sqltext, persisted=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `sqltext` | হিসাবের SQL এক্সপ্রেশন (স্ট্রিং বা এক্সপ্রেশন)। |
| `persisted` | `True` → `STORED` (ডিস্কে রাখা), `False` → `VIRTUAL` (পড়ার সময় হিসাব)। **সবসময় স্পষ্ট করে দিন:** না দিলে ২.১ PostgreSQL ১৭ বা তার আগের ভার্সনে সতর্কবার্তা দিয়ে `STORED` বানায়, কিন্তু PostgreSQL ১৮+-এ ডিফল্ট `VIRTUAL` হয়ে যায়; ফলে ডেটাবেস আপগ্রেডে আচরণ বদলে যেতে পারে। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #computed-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`copy()`](#computed-copy) | মেথড ⚠️ deprecated | কপি (১.৪ থেকে বাতিলের পথে)। |
| [`persisted`](#computed-persisted) | অ্যাট্রিবিউট | `STORED`/`VIRTUAL` সেটিং (না দিলে `None`)। |
| [`sqltext`](#computed-sqltext) | অ্যাট্রিবিউট | হিসাবের এক্সপ্রেশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Computed`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Sequence` থেকে:** [`column`](#sequence-column)

**`Table` থেকে:** [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`info`](schema.md#table-info)

**`FetchedValue` থেকে:** [`has_argument`](#fetchedvalue-has-argument) · [`is_clause_element`](#fetchedvalue-is-clause-element) · [`is_identity`](#fetchedvalue-is-identity) · [`is_server_default`](#fetchedvalue-is-server-default) · [`reflected`](#fetchedvalue-reflected)

///

### `Computed.copy()` { #computed-copy }

```python
Computed.copy(*, target_table=None, **kw)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

কপি (১.৪ থেকে বাতিলের পথে)।

### `Computed.persisted` { #computed-persisted }

**ধরন:** অ্যাট্রিবিউট

`STORED`/`VIRTUAL` সেটিং (না দিলে `None`)।

**উদাহরণ:**

```python
print(Computed("a + b", persisted=True).persisted)   # True
```

### `Computed.sqltext` { #computed-sqltext }

**ধরন:** অ্যাট্রিবিউট

হিসাবের এক্সপ্রেশন।

**উদাহরণ:**

```python
print(orders.c.total.computed.sqltext)   # price * qty
```

/// check | সংক্ষেপে মনে রাখুন

* `MetaData(naming_convention=...)` দিন, যাতে সব কনস্ট্রেইন্টের নাম অনুমানযোগ্য হয় (Alembic-এ মোছা/বদলানো সহজ)।
* কয়েকটি কলাম মিলে অনন্য: `UniqueConstraint("a", "b")`; ডেটার নিয়ম: `CheckConstraint("qty > 0")`।
* ফরেন কি-তে `ondelete="CASCADE"`/`"SET NULL"` ভেবে দিন; ORM cascade-এর সাথে মিলিয়ে।
* partial/expression index: `Index(..., postgresql_where=...)`, `Index(None, func.lower(col), unique=True)`।
* Python ডিফল্ট `default=`, ডেটাবেস ডিফল্ট `server_default=`; auto-increment নতুন টেবিলে `Identity()`; হিসাব করা কলাম `Computed()`।

///
