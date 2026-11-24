# inspect() ও Inspector API: ডেটাবেসের গঠন পড়া { #api-inspection }

/// note | এই পেজে যা আছে

* `inspect()`: যেকোনো SQLAlchemy অবজেক্টের "ভেতরের তথ্য" দেখার একক ফাংশন।
* `Inspector`: ডেটাবেসে **আসলে** কী আছে (টেবিল, কলাম, ইনডেক্স, কনস্ট্রেইন্ট, ভিউ, sequence, comment) পড়ার **সব** মেথড, ২.১-এর `has_multi_table()`-সহ।
* `ObjectKind`, `ObjectScope`: `get_multi_*()` মেথডে কোন ধরনের অবজেক্ট পড়া হবে।

///

কোড বা মডেল যা বলছে আর ডেটাবেসে আসলে যা আছে, দুটো আলাদা হতে পারে (কেউ হাতে কলাম যোগ করেছে, মাইগ্রেশন বাদ পড়েছে)। `Inspector` সরাসরি ডেটাবেস থেকে পড়ে। Alembic-এর autogenerate, `MetaData.reflect()`, অ্যাডমিন টুল আর "স্কিমা ঠিক আছে কি না" হেলথ-চেক এটিই ব্যবহার করে।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

PostgreSQL 16-এ এই স্কিমা তৈরি করা আছে:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL CONSTRAINT uq_users_email UNIQUE,
    age INTEGER CONSTRAINT ck_users_age CHECK (age >= 0)
);
COMMENT ON TABLE users IS 'ইউজার';
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'new'
);
CREATE INDEX ix_orders_status ON orders (status);
CREATE VIEW active_users AS SELECT id, email FROM users WHERE age IS NOT NULL;
CREATE MATERIALIZED VIEW order_counts AS SELECT user_id, count(*) AS n FROM orders GROUP BY user_id;
CREATE SEQUENCE invoice_seq;
CREATE SCHEMA archive;
```

`insp = inspect(engine)`।

///

## `inspect()` { #inspect }

```python
from sqlalchemy import inspect
```

```python
inspect(subject, raiseerr=True)
```

**ধরন:** ফাংশন

যেকোনো সমর্থিত অবজেক্টের inspection-অবজেক্ট দেয়:

* `inspect(engine)` / `inspect(connection)` → `Inspector` (ডেটাবেসের গঠন)।
* `inspect(User)` (ORM ক্লাস) → `Mapper` ([Registry ও Mapper পেজ](registry.md#mapper))।
* `inspect(user_obj)` (ORM অবজেক্ট) → `InstanceState`: অবস্থা (`transient`, `pending`, `persistent`, `detached`), পরিবর্তন-ইতিহাস।
* `inspect(aliased(User))` → `AliasedInsp`।

`raiseerr=False` দিলে অসমর্থিত অবজেক্টে এরর না দিয়ে `None` দেয়।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    age: Mapped[int | None]

print(type(inspect(engine)).__name__, type(inspect(User)).__name__)   # PGInspector Mapper
u = User(email="a@b.com")
print(inspect(u).transient)                                           # True
with Session(engine) as s:
    s.add(u); s.flush()
    print(inspect(u).persistent, inspect(u).identity)                 # True (1,)
print(inspect(42, raiseerr=False))                                    # None
```

### `inspect()`-এর সব প্যারামিটার { #inspect-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `subject` | যার তথ্য চাই: Engine, Connection, ORM ক্লাস, ORM অবজেক্ট, aliased ইত্যাদি। |
| `raiseerr` | `True` (ডিফল্ট): অসমর্থিত অবজেক্টে `NoInspectionAvailable` এরর; `False`: `None` ফেরত। |

## `Inspector` { #inspector }

```python
from sqlalchemy import inspect
```

ডেটাবেসের স্কিমা পড়ার অবজেক্ট (`inspect(engine)` বা `inspect(connection)`)। ফলাফল ক্যাশ করে রাখে, তাই একই Inspector দিয়ে বারবার পড়া দ্রুত; স্কিমা বদলের পর নতুন তথ্য চাইলে `clear_cache()` বা নতুন Inspector। প্রায় সব মেথডে `schema=` দিয়ে অন্য স্কিমা পড়া যায়। ২.০ থেকে `get_multi_*()` মেথডগুলো **একটি কুয়েরিতে** অনেক টেবিলের তথ্য আনে (বড় ডেটাবেসে অনেক দ্রুত)।

**উদাহরণ:**

```python
print(insp.get_table_names())                                   # ['users', 'orders']
print([c["name"] for c in insp.get_columns("orders")])         # ['id', 'user_id', 'status']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #inspector-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bind`](#inspector-bind) | অ্যাট্রিবিউট | যে Engine বা Connection থেকে Inspector বানানো। |
| [`clear_cache()`](#inspector-clear-cache) | মেথড | ক্যাশ খালি করে; পরের কলে ডেটাবেস থেকে আবার পড়ে (স্কিমা বদলানোর পর)। |
| [`default_schema_name`](#inspector-default-schema-name) | প্রপার্টি | বর্তমান ইউজারের ডিফল্ট স্কিমা। |
| [`dialect`](#inspector-dialect) | অ্যাট্রিবিউট | ব্যবহৃত ডায়ালেক্ট। |
| [`engine`](#inspector-engine) | অ্যাট্রিবিউট | সংশ্লিষ্ট Engine। |
| [`from_engine()`](#inspector-from-engine) | ক্লাস মেথড (legacy) | (ক্লাস মেথড) Engine থেকে Inspector বানায়; নতুন কোডে `inspect(engine)` লিখুন। |
| [`get_check_constraints()`](#inspector-get-check-constraints) | মেথড | একটি টেবিলের CHECK কনস্ট্রেইন্ট: প্রতিটির `name`, `sqltext`। |
| [`get_columns()`](#inspector-get-columns) | মেথড | একটি টেবিলের কলাম: প্রতিটির `name`, `type`, `nullable`, `default`, `autoincrement`, `comment` (আর থাকলে `computed`, `identity`)। |
| [`get_foreign_keys()`](#inspector-get-foreign-keys) | মেথড | ফরেন কি: `name`, `constrained_columns`, `referred_table`, `referred_columns`, `options` (`ondelete` ইত্যাদি)। |
| [`get_indexes()`](#inspector-get-indexes) | মেথড | ইনডেক্স: `name`, `column_names`, `unique`, আর ডায়ালেক্ট-তথ্য। |
| [`get_materialized_view_names()`](#inspector-get-materialized-view-names) | মেথড | materialized view-এর নাম। |
| [`get_multi_check_constraints()`](#inspector-get-multi-check-constraints) | মেথড | (২.০) অনেক টেবিলের CHECK কনস্ট্রেইন্ট একসাথে: `{(স্কিমা, টেবিল): [...]}`। |
| [`get_multi_columns()`](#inspector-get-multi-columns) | মেথড | (২.০) অনেক টেবিল/ভিউয়ের কলাম এক কুয়েরিতে। |
| [`get_multi_foreign_keys()`](#inspector-get-multi-foreign-keys) | মেথড | (২.০) অনেক টেবিলের ফরেন কি একসাথে। |
| [`get_multi_indexes()`](#inspector-get-multi-indexes) | মেথড | (২.০) অনেক টেবিলের ইনডেক্স একসাথে। |
| [`get_multi_pk_constraint()`](#inspector-get-multi-pk-constraint) | মেথড | (২.০) অনেক টেবিলের primary key একসাথে। |
| [`get_multi_table_comment()`](#inspector-get-multi-table-comment) | মেথড | (২.০) অনেক টেবিলের comment একসাথে। |
| [`get_multi_table_options()`](#inspector-get-multi-table-options) | মেথড | (২.০) অনেক টেবিলের ডায়ালেক্ট-অপশন একসাথে। |
| [`get_multi_unique_constraints()`](#inspector-get-multi-unique-constraints) | মেথড | (২.০) অনেক টেবিলের unique কনস্ট্রেইন্ট একসাথে। |
| [`get_pk_constraint()`](#inspector-get-pk-constraint) | মেথড | একটি টেবিলের primary key: `constrained_columns`, `name`। |
| [`get_schema_names()`](#inspector-get-schema-names) | মেথড | ডেটাবেসের সব স্কিমার নাম। |
| [`get_sequence_names()`](#inspector-get-sequence-names) | মেথড | sequence-গুলোর নাম (`SERIAL`-এর নিজে-তৈরি sequence-সহ)। |
| [`get_sorted_table_and_fkc_names()`](#inspector-get-sorted-table-and-fkc-names) | মেথড | টেবিলের নাম ফরেন কি নির্ভরতা-ক্রমে (আগে প্যারেন্ট), প্রতিটির সাথে তার FK কনস্ট্রেইন্টের নাম; শেষে চক্রাকার FK আলাদা। |
| [`get_table_comment()`](#inspector-get-table-comment) | মেথড | টেবিলের comment। |
| [`get_table_names()`](#inspector-get-table-names) | মেথড | সাধারণ টেবিলের নাম, ফরেন কি নির্ভরতা-ক্রমে (ভিউ ছাড়া)। |
| [`get_table_options()`](#inspector-get-table-options) | মেথড | টেবিল তৈরির সময়ের ডায়ালেক্ট-অপশন (PostgreSQL-এ `postgresql_with`, partition ইত্যাদি)। |
| [`get_temp_table_names()`](#inspector-get-temp-table-names) | মেথড | বর্তমান কানেকশনের অস্থায়ী (TEMPORARY) টেবিলের নাম। |
| [`get_temp_view_names()`](#inspector-get-temp-view-names) | মেথড | বর্তমান কানেকশনের অস্থায়ী ভিউয়ের নাম। |
| [`get_unique_constraints()`](#inspector-get-unique-constraints) | মেথড | unique কনস্ট্রেইন্ট: `name`, `column_names`। |
| [`get_view_definition()`](#inspector-get-view-definition) | মেথড | একটি ভিউ (বা materialized view)-এর SELECT লেখা। |
| [`get_view_names()`](#inspector-get-view-names) | মেথড | সাধারণ ভিউয়ের নাম (materialized নয়)। |
| [`has_index()`](#inspector-has-index) | মেথড | (২.০) নির্দিষ্ট নামের ইনডেক্স আছে কি না। |
| [`has_multi_table()`](#inspector-has-multi-table) | মেথড | (২.১-এ নতুন) অনেকগুলো টেবিল-নামের প্রতিটি আছে কি না, এক কুয়েরিতে: `{(স্কিমা, নাম): bool}`। |
| [`has_schema()`](#inspector-has-schema) | মেথড | (২.০) স্কিমা আছে কি না। |
| [`has_sequence()`](#inspector-has-sequence) | মেথড | sequence আছে কি না। |
| [`has_table()`](#inspector-has-table) | মেথড | টেবিল (বা ভিউ, অস্থায়ী টেবিল) আছে কি না। |
| [`info_cache`](#inspector-info-cache) | অ্যাট্রিবিউট (internal) | ফলাফল ক্যাশের dict (`clear_cache()` খালি করে)। |
| [`reflect_table()`](#inspector-reflect-table) | মেথড | একটি খালি `Table` অবজেক্টে ডেটাবেস থেকে কলাম, কনস্ট্রেইন্ট, ইনডেক্স ভরে দেয় (`Table(..., autoload_with=engine)` ভেতরে এটিই করে)। |
| [`sort_tables_on_foreign_key_dependency()`](#inspector-sort-tables-on-foreign-key-dependency) | মেথড | (২.০) কয়েকটি স্কিমা মিলিয়ে টেবিলগুলো ফরেন কি নির্ভরতা-ক্রমে সাজায়: `((স্কিমা, টেবিল), [(FK-এর টেবিল, FK-নাম)])`। |

### `Inspector.bind` { #inspector-bind }

**ধরন:** অ্যাট্রিবিউট

যে Engine বা Connection থেকে Inspector বানানো।

**উদাহরণ:**

```python
print(insp.bind is engine)   # True
```

### `Inspector.clear_cache()` { #inspector-clear-cache }

```python
Inspector.clear_cache()
```

**ধরন:** মেথড

ক্যাশ খালি করে; পরের কলে ডেটাবেস থেকে আবার পড়ে (স্কিমা বদলানোর পর)।

**উদাহরণ:**

```python
print(len(insp.get_table_names()))   # 2
with engine.begin() as c:
    c.exec_driver_sql("CREATE TABLE extra (id int)")
print(len(insp.get_table_names()))   # 2  (ক্যাশ থেকে)
insp.clear_cache()
print(len(insp.get_table_names()))   # 3
```

### `Inspector.default_schema_name` { #inspector-default-schema-name }

**ধরন:** প্রপার্টি

বর্তমান ইউজারের ডিফল্ট স্কিমা।

**উদাহরণ:**

```python
print(insp.default_schema_name)   # public
```

### `Inspector.dialect` { #inspector-dialect }

**ধরন:** অ্যাট্রিবিউট

ব্যবহৃত ডায়ালেক্ট।

**উদাহরণ:**

```python
print(insp.dialect.name)   # postgresql
```

### `Inspector.engine` { #inspector-engine }

**ধরন:** অ্যাট্রিবিউট

সংশ্লিষ্ট Engine।

**উদাহরণ:**

```python
print(insp.engine is engine)   # True
```

### `Inspector.from_engine()` { #inspector-from-engine }

```python
Inspector.from_engine(bind)
```

**ধরন:** ক্লাস মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(ক্লাস মেথড) Engine থেকে Inspector বানায়; নতুন কোডে `inspect(engine)` লিখুন।

**উদাহরণ:**

```python
print(type(Inspector.from_engine(engine)).__name__)   # PGInspector
```

### `Inspector.get_check_constraints()` { #inspector-get-check-constraints }

```python
Inspector.get_check_constraints(table_name, schema=None, **kw)
```

**ধরন:** মেথড

একটি টেবিলের CHECK কনস্ট্রেইন্ট: প্রতিটির `name`, `sqltext`।

**উদাহরণ:**

```python
print(insp.get_check_constraints("users"))   # [{'name': 'ck_users_age', 'sqltext': 'age >= 0', 'comment': None}]
```

### `Inspector.get_columns()` { #inspector-get-columns }

```python
Inspector.get_columns(table_name, schema=None, **kw)
```

**ধরন:** মেথড

একটি টেবিলের কলাম: প্রতিটির `name`, `type`, `nullable`, `default`, `autoincrement`, `comment` (আর থাকলে `computed`, `identity`)।

**উদাহরণ:**

```python
c = insp.get_columns("orders")[2]
print(c["name"], c["type"], c["nullable"], c["default"])   # status VARCHAR(20) True 'new'::character varying
```

### `Inspector.get_foreign_keys()` { #inspector-get-foreign-keys }

```python
Inspector.get_foreign_keys(table_name, schema=None, **kw)
```

**ধরন:** মেথড

ফরেন কি: `name`, `constrained_columns`, `referred_table`, `referred_columns`, `options` (`ondelete` ইত্যাদি)।

**উদাহরণ:**

```python
fk = insp.get_foreign_keys("orders")[0]
print(fk["constrained_columns"], fk["referred_table"], fk["options"])   # ['user_id'] users {'ondelete': 'CASCADE'}
```

### `Inspector.get_indexes()` { #inspector-get-indexes }

```python
Inspector.get_indexes(table_name, schema=None, **kw)
```

**ধরন:** মেথড

ইনডেক্স: `name`, `column_names`, `unique`, আর ডায়ালেক্ট-তথ্য। PostgreSQL-এ UNIQUE কনস্ট্রেইন্টের পেছনের ইনডেক্সও এখানে আসে, সাথে `duplicates_constraint` key (তাই সেটি আলাদা ইনডেক্স হিসেবে গুনবেন না)।

**উদাহরণ:**

```python
print([(i["name"], i["column_names"], i["unique"]) for i in insp.get_indexes("orders")])   # [('ix_orders_status', ['status'], False)]
```

### `Inspector.get_materialized_view_names()` { #inspector-get-materialized-view-names }

```python
Inspector.get_materialized_view_names(schema=None, **kw)
```

**ধরন:** মেথড

materialized view-এর নাম।

**উদাহরণ:**

```python
print(insp.get_materialized_view_names())   # ['order_counts']
```

### `Inspector.get_multi_check_constraints()` { #inspector-get-multi-check-constraints }

```python
Inspector.get_multi_check_constraints(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের CHECK কনস্ট্রেইন্ট একসাথে: `{(স্কিমা, টেবিল): [...]}`। `filter_names`, `kind`, `scope` দিয়ে ছাঁকা যায়।

**উদাহরণ:**

```python
print(insp.get_multi_check_constraints()[(None, "users")][0]["name"])   # ck_users_age
```

### `Inspector.get_multi_columns()` { #inspector-get-multi-columns }

```python
Inspector.get_multi_columns(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিল/ভিউয়ের কলাম এক কুয়েরিতে। `kind=ObjectKind.ANY` দিলে ভিউও।

**উদাহরণ:**

```python
cols = insp.get_multi_columns(kind=ObjectKind.ANY)
print(sorted(k[1] for k in cols))   # ['active_users', 'order_counts', 'orders', 'users']
```

### `Inspector.get_multi_foreign_keys()` { #inspector-get-multi-foreign-keys }

```python
Inspector.get_multi_foreign_keys(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের ফরেন কি একসাথে।

**উদাহরণ:**

```python
fks = insp.get_multi_foreign_keys()
print(len(fks[(None, "users")]), fks[(None, "orders")][0]["referred_table"])   # 0 users
```

### `Inspector.get_multi_indexes()` { #inspector-get-multi-indexes }

```python
Inspector.get_multi_indexes(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের ইনডেক্স একসাথে।

**উদাহরণ:**

```python
print({k[1]: [i["name"] for i in v] for k, v in insp.get_multi_indexes().items()})   # {'users': ['uq_users_email'], 'orders': ['ix_orders_status']}
```

### `Inspector.get_multi_pk_constraint()` { #inspector-get-multi-pk-constraint }

```python
Inspector.get_multi_pk_constraint(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের primary key একসাথে।

**উদাহরণ:**

```python
print(insp.get_multi_pk_constraint()[(None, "orders")]["constrained_columns"])   # ['id']
```

### `Inspector.get_multi_table_comment()` { #inspector-get-multi-table-comment }

```python
Inspector.get_multi_table_comment(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের comment একসাথে।

**উদাহরণ:**

```python
print(insp.get_multi_table_comment()[(None, "users")])   # {'text': 'ইউজার'}
```

### `Inspector.get_multi_table_options()` { #inspector-get-multi-table-options }

```python
Inspector.get_multi_table_options(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের ডায়ালেক্ট-অপশন একসাথে।

**উদাহরণ:**

```python
print(insp.get_multi_table_options()[(None, "users")])   # {}
```

### `Inspector.get_multi_unique_constraints()` { #inspector-get-multi-unique-constraints }

```python
Inspector.get_multi_unique_constraints(schema=None, filter_names=None, kind=<ObjectKind.TABLE: 1>, scope=<ObjectScope.DEFAULT: 1>, **kw)
```

**ধরন:** মেথড

(২.০) অনেক টেবিলের unique কনস্ট্রেইন্ট একসাথে।

**উদাহরণ:**

```python
print(insp.get_multi_unique_constraints()[(None, "users")][0]["name"])   # uq_users_email
```

### `Inspector.get_pk_constraint()` { #inspector-get-pk-constraint }

```python
Inspector.get_pk_constraint(table_name, schema=None, **kw)
```

**ধরন:** মেথড

একটি টেবিলের primary key: `constrained_columns`, `name`।

**উদাহরণ:**

```python
print(insp.get_pk_constraint("users"))
# {'constrained_columns': ['id'], 'name': 'users_pkey', 'comment': None, 'dialect_options': {'postgresql_include': []}}
```

### `Inspector.get_schema_names()` { #inspector-get-schema-names }

```python
Inspector.get_schema_names(**kw)
```

**ধরন:** মেথড

ডেটাবেসের সব স্কিমার নাম।

**উদাহরণ:**

```python
print("archive" in insp.get_schema_names(), "public" in insp.get_schema_names())   # True True
```

### `Inspector.get_sequence_names()` { #inspector-get-sequence-names }

```python
Inspector.get_sequence_names(schema=None, **kw)
```

**ধরন:** মেথড

sequence-গুলোর নাম (`SERIAL`-এর নিজে-তৈরি sequence-সহ)।

**উদাহরণ:**

```python
print(sorted(insp.get_sequence_names()))   # ['invoice_seq', 'orders_id_seq', 'users_id_seq']
```

### `Inspector.get_sorted_table_and_fkc_names()` { #inspector-get-sorted-table-and-fkc-names }

```python
Inspector.get_sorted_table_and_fkc_names(schema=None, **kw)
```

**ধরন:** মেথড

টেবিলের নাম ফরেন কি নির্ভরতা-ক্রমে (আগে প্যারেন্ট), প্রতিটির সাথে তার FK কনস্ট্রেইন্টের নাম; শেষে চক্রাকার FK আলাদা।

**উদাহরণ:**

```python
print([t for t, fks in insp.get_sorted_table_and_fkc_names()])   # ['users', 'orders', None]
```

### `Inspector.get_table_comment()` { #inspector-get-table-comment }

```python
Inspector.get_table_comment(table_name, schema=None, **kw)
```

**ধরন:** মেথড

টেবিলের comment।

**উদাহরণ:**

```python
print(insp.get_table_comment("users"))   # {'text': 'ইউজার'}
```

### `Inspector.get_table_names()` { #inspector-get-table-names }

```python
Inspector.get_table_names(schema=None, **kw)
```

**ধরন:** মেথড

সাধারণ টেবিলের নাম, ফরেন কি নির্ভরতা-ক্রমে (ভিউ ছাড়া)।

**উদাহরণ:**

```python
print(insp.get_table_names(schema="archive"))   # []
```

### `Inspector.get_table_options()` { #inspector-get-table-options }

```python
Inspector.get_table_options(table_name, schema=None, **kw)
```

**ধরন:** মেথড

টেবিল তৈরির সময়ের ডায়ালেক্ট-অপশন (PostgreSQL-এ `postgresql_with`, partition ইত্যাদি)।

**উদাহরণ:**

```python
print(insp.get_table_options("users"))   # {}
```

### `Inspector.get_temp_table_names()` { #inspector-get-temp-table-names }

```python
Inspector.get_temp_table_names(**kw)
```

**ধরন:** মেথড

বর্তমান কানেকশনের অস্থায়ী (TEMPORARY) টেবিলের নাম।

**উদাহরণ:**

```python
with engine.connect() as c:
    c.exec_driver_sql("CREATE TEMP TABLE scratch (x int)")
    print(inspect(c).get_temp_table_names())   # ['scratch']
```

### `Inspector.get_temp_view_names()` { #inspector-get-temp-view-names }

```python
Inspector.get_temp_view_names(**kw)
```

**ধরন:** মেথড

বর্তমান কানেকশনের অস্থায়ী ভিউয়ের নাম।

**উদাহরণ:**

```python
with engine.connect() as c:
    c.exec_driver_sql("CREATE TEMP VIEW tv AS SELECT 1 AS x")
    print(inspect(c).get_temp_view_names())   # ['tv']
```

### `Inspector.get_unique_constraints()` { #inspector-get-unique-constraints }

```python
Inspector.get_unique_constraints(table_name, schema=None, **kw)
```

**ধরন:** মেথড

unique কনস্ট্রেইন্ট: `name`, `column_names`।

**উদাহরণ:**

```python
print([(u["name"], u["column_names"]) for u in insp.get_unique_constraints("users")])   # [('uq_users_email', ['email'])]
```

### `Inspector.get_view_definition()` { #inspector-get-view-definition }

```python
Inspector.get_view_definition(view_name, schema=None, **kw)
```

**ধরন:** মেথড

একটি ভিউ (বা materialized view)-এর SELECT লেখা।

**উদাহরণ:**

```python
print(" ".join(insp.get_view_definition("active_users").split())[:27])   # SELECT id, email FROM users
```

### `Inspector.get_view_names()` { #inspector-get-view-names }

```python
Inspector.get_view_names(schema=None, **kw)
```

**ধরন:** মেথড

সাধারণ ভিউয়ের নাম (materialized নয়)।

**উদাহরণ:**

```python
print(insp.get_view_names())   # ['active_users']
```

### `Inspector.has_index()` { #inspector-has-index }

```python
Inspector.has_index(table_name, index_name, schema=None, **kw)
```

**ধরন:** মেথড

(২.০) নির্দিষ্ট নামের ইনডেক্স আছে কি না।

**উদাহরণ:**

```python
print(insp.has_index("orders", "ix_orders_status"), insp.has_index("orders", "nope"))   # True False
```

### `Inspector.has_multi_table()` { #inspector-has-multi-table }

```python
Inspector.has_multi_table(table_names, schema=None, **kw)
```

**ধরন:** মেথড

(২.১-এ নতুন) অনেকগুলো টেবিল-নামের প্রতিটি আছে কি না, এক কুয়েরিতে: `{(স্কিমা, নাম): bool}`।

**উদাহরণ:**

```python
print(insp.has_multi_table(["users", "nope", "active_users"]))
# {(None, 'users'): True, (None, 'nope'): False, (None, 'active_users'): True}
```

### `Inspector.has_schema()` { #inspector-has-schema }

```python
Inspector.has_schema(schema_name, **kw)
```

**ধরন:** মেথড

(২.০) স্কিমা আছে কি না।

**উদাহরণ:**

```python
print(insp.has_schema("archive"), insp.has_schema("nope"))   # True False
```

### `Inspector.has_sequence()` { #inspector-has-sequence }

```python
Inspector.has_sequence(sequence_name, schema=None, **kw)
```

**ধরন:** মেথড

sequence আছে কি না।

**উদাহরণ:**

```python
print(insp.has_sequence("invoice_seq"))   # True
```

### `Inspector.has_table()` { #inspector-has-table }

```python
Inspector.has_table(table_name, schema=None, **kw)
```

**ধরন:** মেথড

টেবিল (বা ভিউ, অস্থায়ী টেবিল) আছে কি না। হেলথ-চেক বা "প্রথমবার চালু হলে টেবিল বানাও" যুক্তিতে।

**উদাহরণ:**

```python
print(insp.has_table("orders"), insp.has_table("active_users"), insp.has_table("nope"))   # True True False
```

### `Inspector.info_cache` { #inspector-info-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফলাফল ক্যাশের dict (`clear_cache()` খালি করে)।

### `Inspector.reflect_table()` { #inspector-reflect-table }

```python
Inspector.reflect_table(table, include_columns, exclude_columns=(), resolve_fks=True)
```

**ধরন:** মেথড

একটি খালি `Table` অবজেক্টে ডেটাবেস থেকে কলাম, কনস্ট্রেইন্ট, ইনডেক্স ভরে দেয় (`Table(..., autoload_with=engine)` ভেতরে এটিই করে)।

**উদাহরণ:**

```python
t = Table("orders", MetaData())
insp.reflect_table(t, None)
print([c.name for c in t.c], [fk.target_fullname for fk in t.foreign_keys])   # ['id', 'user_id', 'status'] ['users.id']
```

### `Inspector.sort_tables_on_foreign_key_dependency()` { #inspector-sort-tables-on-foreign-key-dependency }

```python
Inspector.sort_tables_on_foreign_key_dependency(consider_schemas=(None,), **kw)
```

**ধরন:** মেথড

(২.০) কয়েকটি স্কিমা মিলিয়ে টেবিলগুলো ফরেন কি নির্ভরতা-ক্রমে সাজায়: `((স্কিমা, টেবিল), [(FK-এর টেবিল, FK-নাম)])`।

**উদাহরণ:**

```python
print([t for t, fks in insp.sort_tables_on_foreign_key_dependency()])   # [(None, 'users'), (None, 'orders'), None]
```

## `ObjectKind` { #objectkind }

```python
from sqlalchemy.engine import ObjectKind
```

(২.০) `get_multi_*()` মেথডে কোন ধরনের অবজেক্ট পড়া হবে তার flag: `TABLE` (ডিফল্ট), `VIEW`, `MATERIALIZED_VIEW`; মিলিত রূপ `ANY_VIEW` (দুই ধরনের ভিউ) আর `ANY` (সব)।

**উদাহরণ:**

```python
views = insp.get_multi_columns(kind=ObjectKind.ANY_VIEW)
print(sorted(k[1] for k in views))   # ['active_users', 'order_counts']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #objectkind-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`MATERIALIZED_VIEW`](#objectkind-MATERIALIZED-VIEW) | অ্যাট্রিবিউট | শুধু materialized view। |
| [`TABLE`](#objectkind-TABLE) | অ্যাট্রিবিউট | শুধু সাধারণ টেবিল (ডিফল্ট)। |
| [`VIEW`](#objectkind-VIEW) | অ্যাট্রিবিউট | শুধু সাধারণ ভিউ। |

### `ObjectKind.MATERIALIZED_VIEW` { #objectkind-MATERIALIZED-VIEW }

**ধরন:** অ্যাট্রিবিউট

শুধু materialized view।

**উদাহরণ:**

```python
print(list(insp.get_multi_columns(kind=ObjectKind.MATERIALIZED_VIEW)))   # [(None, 'order_counts')]
```

### `ObjectKind.TABLE` { #objectkind-TABLE }

**ধরন:** অ্যাট্রিবিউট

শুধু সাধারণ টেবিল (ডিফল্ট)।

**উদাহরণ:**

```python
print(sorted(k[1] for k in insp.get_multi_columns(kind=ObjectKind.TABLE)))   # ['orders', 'users']
```

### `ObjectKind.VIEW` { #objectkind-VIEW }

**ধরন:** অ্যাট্রিবিউট

শুধু সাধারণ ভিউ।

**উদাহরণ:**

```python
print(list(insp.get_multi_columns(kind=ObjectKind.VIEW)))   # [(None, 'active_users')]
```

## `ObjectScope` { #objectscope }

```python
from sqlalchemy.engine import ObjectScope
```

(২.০) `get_multi_*()`-এ স্থায়ী না অস্থায়ী অবজেক্ট: `DEFAULT` (স্থায়ী, ডিফল্ট), `TEMPORARY`, আর মিলিত `ANY`।

**উদাহরণ:**

```python
with engine.connect() as c:
    c.exec_driver_sql("CREATE TEMP TABLE scratch (x int)")
    tmp = inspect(c).get_multi_columns(scope=ObjectScope.TEMPORARY)
    print([k[1] for k in tmp])   # ['scratch']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #objectscope-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`DEFAULT`](#objectscope-DEFAULT) | অ্যাট্রিবিউট | স্থায়ী অবজেক্ট। |
| [`TEMPORARY`](#objectscope-TEMPORARY) | অ্যাট্রিবিউট | অস্থায়ী (TEMP) অবজেক্ট। |

### `ObjectScope.DEFAULT` { #objectscope-DEFAULT }

**ধরন:** অ্যাট্রিবিউট

স্থায়ী অবজেক্ট।

**উদাহরণ:**

```python
print(ObjectScope.DEFAULT.value)   # 1
```

### `ObjectScope.TEMPORARY` { #objectscope-TEMPORARY }

**ধরন:** অ্যাট্রিবিউট

অস্থায়ী (TEMP) অবজেক্ট।

**উদাহরণ:**

```python
print(ObjectScope.TEMPORARY.value)   # 2
```

/// check | সংক্ষেপে মনে রাখুন

* `inspect(engine)` → ডেটাবেসের গঠন; `inspect(Model)` → Mapper; `inspect(obj)` → অবজেক্টের অবস্থা।
* টেবিল আছে কি না: `insp.has_table("নাম")`; অনেকগুলো একসাথে: `has_multi_table()` (২.১)।
* অনেক টেবিলের তথ্য দ্রুত: `get_multi_columns()`, `get_multi_indexes()` …
* স্কিমা বদলের পর: `insp.clear_cache()` বা নতুন `inspect(engine)`।

///
