# কলাম টাইপ API: String, Integer, Numeric, DateTime, Enum, JSON, ARRAY … { #api-types }

/// note | এই পেজে যা আছে

* `TypeEngine`: সব টাইপের মূল ক্লাস ও তার **সব** মেথড (`with_variant()`, `compile()`, `python_type`, `evaluates_none()` …)।
* **সাধারণ (generic) টাইপ:** `String`, `Text`, `Unicode`, `UnicodeText`, `Integer`, `SmallInteger`, `BigInteger`, `Numeric`, `Float`, `Double`, `Boolean`, `Date`, `DateTime`, `Time`, `Interval`, `LargeBinary`, `Enum`, `JSON` (আর `JSON.Comparator`), `ARRAY` (আর `ARRAY.Comparator`), `PickleType`, `Uuid`, `TupleType`, `NullType`, `MatchType`।
* **SQL স্ট্যান্ডার্ড টাইপ** (বড় হাতের নাম): `VARCHAR`, `CHAR`, `TEXT`, `CLOB`, `NVARCHAR`, `NCHAR`, `INTEGER`, `INT`, `SMALLINT`, `BIGINT`, `NUMERIC`, `DECIMAL`, `FLOAT`, `REAL`, `DOUBLE`, `DOUBLE_PRECISION`, `BOOLEAN`, `DATE`, `DATETIME`, `TIMESTAMP`, `TIME`, `BINARY`, `VARBINARY`, `BLOB`, `UUID`।
* মিক্সিন ও ২.১-এর নতুন: `Concatenable`, `Indexable`, `NumericCommon`, `SchemaType`, `OperatorClass`।

///

**কোনটা ব্যবহার করবেন:** সাধারণত CamelCase **generic** টাইপ (`String`, `Integer`, `DateTime`): SQLAlchemy প্রতিটি ডেটাবেসে সবচেয়ে উপযুক্ত আসল টাইপ বসায়। ঠিক কোন SQL টাইপ চান তা নিশ্চিত করতে বড় হাতের **SQL-standard** টাইপ (`VARCHAR`, `TIMESTAMP`)। আর PostgreSQL-এর বিশেষ টাইপ (`JSONB`, `INET`, `TSVECTOR`) আসবে ডায়ালেক্ট পেজে। ORM-এ `Mapped[int]`, `Mapped[str]` লিখলে টাইপ নিজে থেকে বেছে নেওয়া হয় ([Model অধ্যায়](../models.md))।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

* `rt(টাইপ, মান)`: একটি অস্থায়ী টেবিলে মানটি লিখে আবার পড়ে যা ফেরত আসে তা দেয় (round-trip)।
* `pgt(টাইপ)`: PostgreSQL-এর `CREATE TABLE`-এ টাইপটি কী নামে বসবে।

সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## `TypeEngine` { #typeengine }

```python
from sqlalchemy.types import TypeEngine
```

সব SQL টাইপের মূল ক্লাস। একটি টাইপ তিনটি কাজ করে: DDL-এ কী নাম বসবে (`compile()`), Python মান কীভাবে ডেটাবেসে যাবে ও ফিরবে (`bind_processor()` / `result_processor()`), আর সেই টাইপের কলামে কোন অপারেটর চলবে (`comparator_factory`)। নিচের মেথডগুলো সব টাইপে আছে।

**উদাহরণ:**

```python
t = String(50)
print(isinstance(t, TypeEngine), pgt(t), t.python_type)   # True VARCHAR(50) <class 'str'>
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typeengine-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`Comparator`](#typeengine-Comparator) | অ্যাট্রিবিউট | টাইপ-স্তরের অপারেটর-ক্লাস; নিজের অপারেটর যোগ করতে সাবক্লাস করুন। |
| [`adapt()`](#typeengine-adapt) | মেথড | এই টাইপের আর্গুমেন্টগুলো (length ইত্যাদি) রেখে আরেকটি টাইপ-ক্লাসের অবজেক্ট বানায়। |
| [`as_generic()`](#typeengine-as-generic) | মেথড | ডায়ালেক্ট-নির্দিষ্ট টাইপের সবচেয়ে কাছের generic রূপ দেয় (reflection থেকে পাওয়া টাইপকে অন্য ডেটাবেসে কপি করতে)। |
| [`bind_expression()`](#typeengine-bind-expression) | মেথড | (override করার জন্য) প্যারামিটারকে SQL ফাংশনে মোড়ায়; ডিফল্টে `None` (মোড়ায় না)। |
| [`bind_processor()`](#typeengine-bind-processor) | মেথড | একটি ডায়ালেক্টের জন্য Python মান → DB-API মানের রূপান্তর-ফাংশন দেয় (দরকার না হলে `None`)। |
| [`coerce_compared_value()`](#typeengine-coerce-compared-value) | মেথড | `col <অপারেটর> Python-মান`-এ ডান দিকের মানটি কোন টাইপে ধরা হবে। |
| [`column_expression()`](#typeengine-column-expression) | মেথড | (override করার জন্য) SELECT-এ কলামকে SQL ফাংশনে মুড়িয়ে পড়ে; ডিফল্টে `None`। |
| [`comparator_factory`](#typeengine-comparator-factory) | অ্যাট্রিবিউট | এই টাইপের কলামে অপারেটরগুলো যে `Comparator` ক্লাস থেকে আসে। |
| [`compare_values()`](#typeengine-compare-values) | মেথড | দুটি Python মান এই টাইপের দৃষ্টিতে সমান কি না (ORM dirty-checking-এ: মান আসলে বদলেছে কি না)। |
| [`compile()`](#typeengine-compile) | মেথড | টাইপটি একটি ডায়ালেক্টে (না দিলে ডিফল্ট) DDL-এ কী নামে বসবে তার স্ট্রিং। |
| [`copy()`](#typeengine-copy) | মেথড | একই আর্গুমেন্টে টাইপের একটি কপি। |
| [`copy_value()`](#typeengine-copy-value) | মেথড (internal) | ORM-এর জন্য একটি মানের কপি বানায় (mutable মানের "আগের অবস্থা" রাখতে)। |
| [`dialect_impl()`](#typeengine-dialect-impl) | মেথড | একটি ডায়ালেক্টে এই টাইপের জন্য আসলে যে (ডায়ালেক্ট-নির্দিষ্ট) টাইপ অবজেক্ট ব্যবহার হবে। |
| [`evaluates_none()`](#typeengine-evaluates-none) | মেথড | এমন একটি কপি দেয় যেখানে Python `None`-কে "কিছু দেওয়া হয়নি" না ধরে **একটি মান** হিসেবে ধরা হয়, ফলে INSERT-এ ডিফল্ট না বসে সরাসরি NULL যায়। |
| [`get_dbapi_type()`](#typeengine-get-dbapi-type) | মেথড (internal) | DB-API ড্রাইভারের সংশ্লিষ্ট টাইপ-অবজেক্ট (কিছু ড্রাইভারে `setinputsizes()`-এর জন্য)। |
| [`hashable`](#typeengine-hashable) | অ্যাট্রিবিউট | এই টাইপের মান Python-এ hashable কি না। |
| [`literal_processor()`](#typeengine-literal-processor) | মেথড | মান যখন প্যারামিটার না হয়ে SQL-এ সরাসরি বসে (`literal_binds`), তখন মানটিকে SQL লেখায় রূপান্তরের ফাংশন। |
| [`operator_classes`](#typeengine-operator-classes) | অ্যাট্রিবিউট | (২.১-এ নতুন) এই টাইপে কোন ধরনের built-in অপারেটর বৈধ (`OperatorClass` flag-এর মিশ্রণ)। |
| [`python_type`](#typeengine-python-type) | প্রপার্টি | এই টাইপের কলাম থেকে সাধারণত যে Python টাইপ আসে। |
| [`render_bind_cast`](#typeengine-render-bind-cast) | অ্যাট্রিবিউট (internal) | কিছু ড্রাইভারে (asyncpg, psycopg 3) প্যারামিটারের পাশে `::টাইপ` CAST বসাতে হবে কি না। |
| [`render_literal_cast`](#typeengine-render-literal-cast) | অ্যাট্রিবিউট (internal) | literal হিসেবে বসানো মানের পাশে CAST বসাতে হবে কি না। |
| [`repr_struct()`](#typeengine-repr-struct) | মেথড (internal) | টাইপের `repr()` বানানোর জন্য গঠন-তথ্য (Alembic autogenerate-এ টাইপ লিখতে কাজে লাগে)। |
| [`result_processor()`](#typeengine-result-processor) | মেথড | ডেটাবেস থেকে আসা মান → Python মানের রূপান্তর-ফাংশন (দরকার না হলে `None`)। |
| [`should_evaluate_none`](#typeengine-should-evaluate-none) | অ্যাট্রিবিউট | `evaluates_none()` প্রয়োগ হয়েছে কি না। |
| [`sort_key_function`](#typeengine-sort-key-function) | অ্যাট্রিবিউট | ORM primary key হিসেবে এই টাইপের মান সাজানোর ফাংশন (যেমন Python `Enum` মান সরাসরি তুলনা করা যায় না বলে); না দিলে `None`। |
| [`with_variant()`](#typeengine-with-variant) | মেথড | নির্দিষ্ট ডায়ালেক্টে ভিন্ন টাইপ ব্যবহারের কপি: যেমন সাধারণত `JSON`, কিন্তু PostgreSQL-এ `JSONB`। |

### `TypeEngine.Comparator` { #typeengine-Comparator }

**ধরন:** অ্যাট্রিবিউট

টাইপ-স্তরের অপারেটর-ক্লাস; নিজের অপারেটর যোগ করতে সাবক্লাস করুন। বিস্তারিত [কাস্টম টাইপ পেজে](custom-types.md#typeengine-comparator)।

**উদাহরণ:**

```python
print(issubclass(String.Comparator, TypeEngine.Comparator))   # True
```

### `TypeEngine.adapt()` { #typeengine-adapt }

```python
TypeEngine.adapt(**kw)
```

**ধরন:** মেথড

এই টাইপের আর্গুমেন্টগুলো (length ইত্যাদি) রেখে আরেকটি টাইপ-ক্লাসের অবজেক্ট বানায়। ডায়ালেক্ট generic টাইপকে নিজের টাইপে রূপান্তর করতে এটি ব্যবহার করে।

**উদাহরণ:**

```python
print(repr(String(30).adapt(postgresql.VARCHAR)))   # VARCHAR(length=30)
```

### `TypeEngine.as_generic()` { #typeengine-as-generic }

```python
TypeEngine.as_generic(allow_nulltype=False)
```

**ধরন:** মেথড

ডায়ালেক্ট-নির্দিষ্ট টাইপের সবচেয়ে কাছের generic রূপ দেয় (reflection থেকে পাওয়া টাইপকে অন্য ডেটাবেসে কপি করতে)।

**উদাহরণ:**

```python
print(repr(postgresql.VARCHAR(20).as_generic()), repr(postgresql.DOUBLE_PRECISION().as_generic()))   # String(length=20) Double()
```

### `TypeEngine.bind_expression()` { #typeengine-bind-expression }

```python
TypeEngine.bind_expression(bindvalue)
```

**ধরন:** মেথড

(override করার জন্য) প্যারামিটারকে SQL ফাংশনে মোড়ায়; ডিফল্টে `None` (মোড়ায় না)। উদাহরণ [`TypeDecorator.bind_expression`](custom-types.md#typedecorator-bind-expression)-এ।

**উদাহরণ:**

```python
print(Integer().bind_expression(literal(1)))   # None
```

### `TypeEngine.bind_processor()` { #typeengine-bind-processor }

```python
TypeEngine.bind_processor(dialect)
```

**ধরন:** মেথড

একটি ডায়ালেক্টের জন্য Python মান → DB-API মানের রূপান্তর-ফাংশন দেয় (দরকার না হলে `None`)। কাস্টম টাইপে সাধারণত `TypeDecorator.process_bind_param` লিখলেই চলে।

**উদাহরণ:**

```python
p = Numeric().bind_processor(sqlite.dialect())
print(p(Decimal("1.50")))   # 1.5
```

### `TypeEngine.coerce_compared_value()` { #typeengine-coerce-compared-value }

```python
TypeEngine.coerce_compared_value(op, value)
```

**ধরন:** মেথড

`col <অপারেটর> Python-মান`-এ ডান দিকের মানটি কোন টাইপে ধরা হবে। যেমন Integer কলামে দশমিক যোগ করলে `Numeric` ধরা হয়।

**উদাহরণ:**

```python
print(repr(Integer().coerce_compared_value(operators.add, 2.5)))   # Double()  (২.১-এ Python float → Double)
```

### `TypeEngine.column_expression()` { #typeengine-column-expression }

```python
TypeEngine.column_expression(colexpr)
```

**ধরন:** মেথড

(override করার জন্য) SELECT-এ কলামকে SQL ফাংশনে মুড়িয়ে পড়ে; ডিফল্টে `None`। উদাহরণ [`TypeDecorator.column_expression`](custom-types.md#typedecorator-column-expression)-এ।

**উদাহরণ:**

```python
print(String().column_expression(column("x")))   # None
```

### `TypeEngine.comparator_factory` { #typeengine-comparator-factory }

**ধরন:** অ্যাট্রিবিউট

এই টাইপের কলামে অপারেটরগুলো যে `Comparator` ক্লাস থেকে আসে। String-এ `concat`, JSON-এ `[]`, ARRAY-তে index; নিজের টাইপে বদলানো যায়।

**উদাহরণ:**

```python
print(JSON.comparator_factory.__qualname__)   # JSON.Comparator
```

### `TypeEngine.compare_values()` { #typeengine-compare-values }

```python
TypeEngine.compare_values(x, y)
```

**ধরন:** মেথড

দুটি Python মান এই টাইপের দৃষ্টিতে সমান কি না (ORM dirty-checking-এ: মান আসলে বদলেছে কি না)। `PickleType`-এর মতো টাইপ override করে।

**উদাহরণ:**

```python
print(Integer().compare_values(5, 5), Integer().compare_values(5, 6))   # True False
```

### `TypeEngine.compile()` { #typeengine-compile }

```python
TypeEngine.compile(dialect=None)
```

**ধরন:** মেথড

টাইপটি একটি ডায়ালেক্টে (না দিলে ডিফল্ট) DDL-এ কী নামে বসবে তার স্ট্রিং।

**উদাহরণ:**

```python
print(Uuid().compile(dialect=postgresql.dialect()), Uuid().compile(dialect=sqlite.dialect()))   # UUID CHAR(32)
```

### `TypeEngine.copy()` { #typeengine-copy }

```python
TypeEngine.copy(**kw)
```

**ধরন:** মেথড

একই আর্গুমেন্টে টাইপের একটি কপি।

**উদাহরণ:**

```python
print(String(30).copy().length)   # 30
```

### `TypeEngine.copy_value()` { #typeengine-copy-value }

```python
TypeEngine.copy_value(value)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ORM-এর জন্য একটি মানের কপি বানায় (mutable মানের "আগের অবস্থা" রাখতে)।

### `TypeEngine.dialect_impl()` { #typeengine-dialect-impl }

```python
TypeEngine.dialect_impl(dialect)
```

**ধরন:** মেথড

একটি ডায়ালেক্টে এই টাইপের জন্য আসলে যে (ডায়ালেক্ট-নির্দিষ্ট) টাইপ অবজেক্ট ব্যবহার হবে।

**উদাহরণ:**

```python
print(type(DateTime().dialect_impl(postgresql.dialect())).__name__)   # _PGTimeStamp
```

### `TypeEngine.evaluates_none()` { #typeengine-evaluates-none }

```python
TypeEngine.evaluates_none()
```

**ধরন:** মেথড

এমন একটি কপি দেয় যেখানে Python `None`-কে "কিছু দেওয়া হয়নি" না ধরে **একটি মান** হিসেবে ধরা হয়, ফলে INSERT-এ ডিফল্ট না বসে সরাসরি NULL যায়। JSON-এ `None` → JSON `null` রাখতেও ব্যবহৃত হয়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("ev", m, Column("id", Integer, primary_key=True),
          Column("a", String, server_default="ডিফল্ট"),
          Column("b", String().evaluates_none(), server_default="ডিফল্ট"))
m.create_all(engine)
from sqlalchemy.orm import Session, registry
class Row: pass
registry().map_imperatively(Row, t)
with Session(engine) as s:
    r = Row(); r.a = None; r.b = None
    s.add(r); s.commit()
    print(s.execute(select(t.c.a, t.c.b)).one())   # ('ডিফল্ট', None)
```

### `TypeEngine.get_dbapi_type()` { #typeengine-get-dbapi-type }

```python
TypeEngine.get_dbapi_type(dbapi)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DB-API ড্রাইভারের সংশ্লিষ্ট টাইপ-অবজেক্ট (কিছু ড্রাইভারে `setinputsizes()`-এর জন্য)।

### `TypeEngine.hashable` { #typeengine-hashable }

**ধরন:** অ্যাট্রিবিউট

এই টাইপের মান Python-এ hashable কি না। `False` হলে (JSON, ARRAY) ORM সেগুলো identity/unique হিসাবে ভিন্নভাবে সামলায়।

**উদাহরণ:**

```python
print(Integer.hashable, JSON.hashable)   # True False
```

### `TypeEngine.literal_processor()` { #typeengine-literal-processor }

```python
TypeEngine.literal_processor(dialect)
```

**ধরন:** মেথড

মান যখন প্যারামিটার না হয়ে SQL-এ সরাসরি বসে (`literal_binds`), তখন মানটিকে SQL লেখায় রূপান্তরের ফাংশন। স্ট্রিংয়ে quote ও escape করে।

**উদাহরণ:**

```python
print(String().literal_processor(postgresql.dialect())("it's"))   # 'it''s'
```

### `TypeEngine.operator_classes` { #typeengine-operator-classes }

**ধরন:** অ্যাট্রিবিউট

(২.১-এ নতুন) এই টাইপে কোন ধরনের built-in অপারেটর বৈধ (`OperatorClass` flag-এর মিশ্রণ)। ভুল টাইপে অপারেটর ব্যবহার ধরতে।

**উদাহরণ:**

```python
print(OperatorClass.MATH in Integer().operator_classes, OperatorClass.MATH in Boolean().operator_classes)   # True False
```

### `TypeEngine.python_type` { #typeengine-python-type }

**ধরন:** প্রপার্টি

এই টাইপের কলাম থেকে সাধারণত যে Python টাইপ আসে।

**উদাহরণ:**

```python
print(DateTime().python_type.__name__, Numeric().python_type.__name__, JSON().python_type.__name__)   # datetime Decimal object
```

### `TypeEngine.render_bind_cast` { #typeengine-render-bind-cast }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কিছু ড্রাইভারে (asyncpg, psycopg 3) প্যারামিটারের পাশে `::টাইপ` CAST বসাতে হবে কি না।

### `TypeEngine.render_literal_cast` { #typeengine-render-literal-cast }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

literal হিসেবে বসানো মানের পাশে CAST বসাতে হবে কি না।

### `TypeEngine.repr_struct()` { #typeengine-repr-struct }

```python
TypeEngine.repr_struct()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপের `repr()` বানানোর জন্য গঠন-তথ্য (Alembic autogenerate-এ টাইপ লিখতে কাজে লাগে)।

### `TypeEngine.result_processor()` { #typeengine-result-processor }

```python
TypeEngine.result_processor(dialect, coltype)
```

**ধরন:** মেথড

ডেটাবেস থেকে আসা মান → Python মানের রূপান্তর-ফাংশন (দরকার না হলে `None`)।

**উদাহরণ:**

```python
p = Numeric(10, 2).result_processor(sqlite.dialect(), None)   # SQLite float দেয়, তাই Decimal-এ রূপান্তর লাগে
print(repr(p(2.5)))   # Decimal('2.50')
```

### `TypeEngine.should_evaluate_none` { #typeengine-should-evaluate-none }

**ধরন:** অ্যাট্রিবিউট

`evaluates_none()` প্রয়োগ হয়েছে কি না।

**উদাহরণ:**

```python
print(JSON().should_evaluate_none, String().evaluates_none().should_evaluate_none)   # True True
```

### `TypeEngine.sort_key_function` { #typeengine-sort-key-function }

**ধরন:** অ্যাট্রিবিউট

ORM primary key হিসেবে এই টাইপের মান সাজানোর ফাংশন (যেমন Python `Enum` মান সরাসরি তুলনা করা যায় না বলে); না দিলে `None`।

**উদাহরণ:**

```python
print(Enum(Status, sort_key_function=lambda e: e.value).sort_key_function(Status.draft))   # draft
```

### `TypeEngine.with_variant()` { #typeengine-with-variant }

```python
TypeEngine.with_variant(type_, *dialect_names)
```

**ধরন:** মেথড

নির্দিষ্ট ডায়ালেক্টে ভিন্ন টাইপ ব্যবহারের কপি: যেমন সাধারণত `JSON`, কিন্তু PostgreSQL-এ `JSONB`। একই মডেল একাধিক ডেটাবেসে (টেস্টে SQLite, প্রোডাকশনে PostgreSQL) চালাতে।

**উদাহরণ:**

```python
t = JSON().with_variant(postgresql.JSONB(), "postgresql")
print(pgt(t), t.compile(dialect=sqlite.dialect()))   # JSONB JSON
```

## স্ট্রিং টাইপ { #string-group }

## `String` { #string }

```python
from sqlalchemy import String
```

স্ট্রিং (`VARCHAR`)। দৈর্ঘ্য দিলে `VARCHAR(n)`; PostgreSQL-এ দৈর্ঘ্য না দিলেও চলে (`VARCHAR`), কিন্তু MySQL-এ দৈর্ঘ্য বাধ্যতামূলক। স্ট্রিং কলামে `+` মানে জোড়া লাগানো, আর `like()`, `ilike()`, `contains()` ইত্যাদি চলে।

**উদাহরণ:**

```python
print(pgt(String(50)), pgt(String()), rt(String(10), "ঢাকা"))   # VARCHAR(50) VARCHAR ঢাকা
```

### কনস্ট্রাক্টরের প্যারামিটার { #string-params }

```python
String(length=None, collation=None, collation_schema=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | সর্বোচ্চ দৈর্ঘ্য (`VARCHAR(n)`)। |
| `collation` | collation, যেমন `"C"` বা `"bn-BD-x-icu"` (সাজানো ও তুলনার নিয়ম)। |
| `collation_schema` | (২.১-এ নতুন) collation যে স্কিমায় আছে (PostgreSQL)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #string-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`collation`](#string-collation) | অ্যাট্রিবিউট | collation-এর নাম (না দিলে `None`)। |
| [`collation_schema`](#string-collation-schema) | অ্যাট্রিবিউট | (২.১) collation-এর স্কিমা। |
| [`length`](#string-length) | অ্যাট্রিবিউট | দৈর্ঘ্য (না দিলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `String`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `String.collation` { #string-collation }

**ধরন:** অ্যাট্রিবিউট

collation-এর নাম (না দিলে `None`)।

**উদাহরণ:**

```python
print(pgt(String(20, collation="C")))   # VARCHAR(20) COLLATE "C"
```

### `String.collation_schema` { #string-collation-schema }

**ধরন:** অ্যাট্রিবিউট

(২.১) collation-এর স্কিমা।

**উদাহরণ:**

```python
print(pgt(String(20, collation="C", collation_schema="pg_catalog")))   # VARCHAR(20) COLLATE pg_catalog."C"
```

### `String.length` { #string-length }

**ধরন:** অ্যাট্রিবিউট

দৈর্ঘ্য (না দিলে `None`)।

**উদাহরণ:**

```python
print(String(50).length)   # 50
```

## `Text` { #text }

```python
from sqlalchemy import Text
```

দৈর্ঘ্য-সীমাহীন বড় লেখা (`TEXT`; MySQL-এ `TEXT`/`LONGTEXT`, Oracle-এ `CLOB`)। PostgreSQL-এ `TEXT` আর `VARCHAR`-এর পারফরম্যান্স একই।

**উদাহরণ:**

```python
print(pgt(Text()), len(rt(Text, "ক" * 10000)))   # TEXT 10000
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `Unicode` { #unicode }

```python
from sqlalchemy import Unicode
```

Unicode স্ট্রিং; যেসব ডেটাবেসে আলাদা Unicode টাইপ আছে (SQL Server-এ `NVARCHAR`) সেখানে সেটি বসায়। PostgreSQL/MySQL-এ সাধারণ `VARCHAR` (তারা UTF-8 এমনিতেই সমর্থন করে)।

**উদাহরণ:**

```python
from sqlalchemy.dialects import mssql
print(pgt(Unicode(30)), Unicode(30).compile(dialect=mssql.dialect()))   # VARCHAR(30) NVARCHAR(30)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `UnicodeText` { #unicodetext }

```python
from sqlalchemy import UnicodeText
```

দৈর্ঘ্য-সীমাহীন Unicode লেখা (SQL Server-এ `NVARCHAR(max)`)।

**উদাহরণ:**

```python
print(pgt(UnicodeText()))   # TEXT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## সংখ্যার টাইপ { #integer-group }

## `Integer` { #integer }

```python
from sqlalchemy import Integer
```

পূর্ণসংখ্যা (`INTEGER`, সাধারণত ৩২-বিট: প্রায় ±২১০ কোটি)। primary key হলে PostgreSQL-এ `SERIAL`/IDENTITY হয়।

**উদাহরণ:**

```python
print(pgt(Integer()), rt(Integer, 42) + 1)   # INTEGER 43
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](#typeengine-summary)-এর মতো।

## `SmallInteger` { #smallinteger }

```python
from sqlalchemy import SmallInteger
```

ছোট পূর্ণসংখ্যা (`SMALLINT`, ±৩২,৭৬৭)।

**উদাহরণ:**

```python
print(pgt(SmallInteger()))   # SMALLINT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `BigInteger` { #biginteger }

```python
from sqlalchemy import BigInteger
```

বড় পূর্ণসংখ্যা (`BIGINT`, ৬৪-বিট)। দ্রুত বাড়তে থাকা টেবিলের id বা বড় কাউন্টারের জন্য।

**উদাহরণ:**

```python
print(pgt(BigInteger()), rt(BigInteger, 9_000_000_000))   # BIGINT 9000000000
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `Numeric` { #numeric }

```python
from sqlalchemy import Numeric
```

নির্দিষ্ট দশমিকের সংখ্যা (`NUMERIC(precision, scale)`); টাকা-পয়সার জন্য **এটাই** ব্যবহার করুন (float নয়)। ডিফল্টে Python `Decimal` ফেরত দেয়।

**উদাহরণ:**

```python
print(pgt(Numeric(10, 2)), rt(Numeric(10, 2), Decimal("1999.99")))   # NUMERIC(10, 2) 1999.99
```

### কনস্ট্রাক্টরের প্যারামিটার { #numeric-params }

```python
Numeric(precision=None, scale=None, decimal_return_scale=None, asdecimal=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্কের সংখ্যা। |
| `scale` | দশমিকের পরে কয়টি অঙ্ক। |
| `decimal_return_scale` | `Decimal`-এ রূপান্তরের সময় দশমিকের পরে কয়টি অঙ্ক রাখা হবে (scale না থাকলে কাজে লাগে)। |
| `asdecimal` | `True` (ডিফল্ট) হলে `Decimal` ফেরত দেয়, `False` হলে `float`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #numeric-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`asdecimal`](#numeric-asdecimal) | অ্যাট্রিবিউট | `Decimal` ফেরত দেবে কি না। |
| [`decimal_return_scale`](#numeric-decimal-return-scale) | অ্যাট্রিবিউট | ফেরত `Decimal`-এর দশমিক-ঘর (না দিলে `None`)। |
| [`precision`](#numeric-precision) | অ্যাট্রিবিউট | precision। |
| [`scale`](#numeric-scale) | অ্যাট্রিবিউট | scale। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Numeric`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `Numeric.asdecimal` { #numeric-asdecimal }

**ধরন:** অ্যাট্রিবিউট

`Decimal` ফেরত দেবে কি না।

**উদাহরণ:**

```python
print(rt(Numeric(10, 2, asdecimal=False), Decimal("2.50")))   # 2.5
```

### `Numeric.decimal_return_scale` { #numeric-decimal-return-scale }

**ধরন:** অ্যাট্রিবিউট

ফেরত `Decimal`-এর দশমিক-ঘর (না দিলে `None`)।

**উদাহরণ:**

```python
print(Numeric(decimal_return_scale=3).decimal_return_scale)   # 3
```

### `Numeric.precision` { #numeric-precision }

**ধরন:** অ্যাট্রিবিউট

precision।

**উদাহরণ:**

```python
print(Numeric(10, 2).precision)   # 10
```

### `Numeric.scale` { #numeric-scale }

**ধরন:** অ্যাট্রিবিউট

scale।

**উদাহরণ:**

```python
print(Numeric(10, 2).scale)   # 2
```

## `Float` { #float }

```python
from sqlalchemy import Float
```

ভাসমান-বিন্দু সংখ্যা (`FLOAT`)। আনুমানিক মান, তাই টাকায় নয়; বৈজ্ঞানিক মাপ, স্কোর ইত্যাদিতে। ডিফল্টে Python `float` ফেরত দেয়।

**উদাহরণ:**

```python
print(pgt(Float()), rt(Float, 0.1 + 0.2))   # FLOAT 0.30000000000000004
```

### কনস্ট্রাক্টরের প্যারামিটার { #float-params }

```python
Float(precision=None, asdecimal=False, decimal_return_scale=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | বাইনারি precision (যেমন `FLOAT(24)`)। |
| `asdecimal` | `True` দিলে `Decimal` ফেরত দেয় (ডিফল্ট `False`)। |
| `decimal_return_scale` | `asdecimal=True` হলে দশমিক-ঘর। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Numeric`](#numeric-summary)-এর মতো।

## `Double` { #double }

```python
from sqlalchemy import Double
```

(২.০) double precision ভাসমান-বিন্দু (`DOUBLE PRECISION` PostgreSQL-এ, `DOUBLE` অন্যত্র)। ORM-এ `Mapped[float]` লিখলে ২.১-এ এটাই বসে।

**উদাহরণ:**

```python
print(pgt(Double()))   # DOUBLE PRECISION
```

### কনস্ট্রাক্টরের প্যারামিটার { #double-params }

```python
Double(precision=None, asdecimal=False, decimal_return_scale=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | precision। |
| `asdecimal` | `Decimal` ফেরত দেবে কি না (ডিফল্ট `False`)। |
| `decimal_return_scale` | দশমিক-ঘর। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Float`](#float)-এর মতো, অর্থাৎ [`Numeric`](#numeric-summary)-এর মতো।

## বুলিয়ান ও Enum { #boolean-group }

## `Boolean` { #boolean }

```python
from sqlalchemy import Boolean
```

সত্য/মিথ্যা। PostgreSQL-এ native `BOOLEAN`; native বুলিয়ান নেই এমন ডেটাবেসে `SMALLINT` (০/১), আর চাইলে সাথে একটি CHECK কনস্ট্রেইন্ট। এটি একটি `SchemaType` (প্রয়োজনে নিজের কনস্ট্রেইন্ট/টাইপ তৈরি করতে পারে)।

**উদাহরণ:**

```python
print(pgt(Boolean()), rt(Boolean, True))   # BOOLEAN True
```

### কনস্ট্রাক্টরের প্যারামিটার { #boolean-params }

```python
Boolean(create_constraint=False, name=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `create_constraint` | native বুলিয়ান না থাকলে `CHECK (x IN (0, 1))` বানাবে কি না (ডিফল্ট `False`)। |
| `name` | সেই CHECK কনস্ট্রেইন্টের নাম। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #boolean-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_to_emulated()`](#boolean-adapt-to-emulated) | মেথড (internal) | native টাইপ নেই এমন ডায়ালেক্টের জন্য "emulated" রূপে রূপান্তর। |
| [`create()`](#boolean-create) | মেথড | এই টাইপের জন্য আলাদা ডেটাবেস অবজেক্ট থাকলে (PostgreSQL ENUM টাইপ) সেটি তৈরি করে। |
| [`create_constraint`](#boolean-create-constraint) | অ্যাট্রিবিউট | CHECK কনস্ট্রেইন্ট বানাবে কি না। |
| [`drop()`](#boolean-drop) | মেথড | `create()`-এর উল্টো: আলাদা টাইপ-অবজেক্ট মুছে দেয় (PostgreSQL `DROP TYPE`)। |
| [`inherit_schema`](#boolean-inherit-schema) | প্রপার্টি | টাইপটি টেবিলের স্কিমা নিজে থেকে নেবে কি না (PostgreSQL ENUM কোন স্কিমায় তৈরি হবে)। |
| [`name`](#boolean-name) | অ্যাট্রিবিউট | কনস্ট্রেইন্ট/টাইপের নাম (না দিলে `None`)। |
| [`native`](#boolean-native) | অ্যাট্রিবিউট | ডায়ালেক্টের native টাইপ ব্যবহার করবে কি না (`True`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Boolean`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `Boolean.adapt_to_emulated()` { #boolean-adapt-to-emulated }

```python
Boolean.adapt_to_emulated(impltype, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

native টাইপ নেই এমন ডায়ালেক্টের জন্য "emulated" রূপে রূপান্তর।

### `Boolean.create()` { #boolean-create }

```python
Boolean.create(bind, checkfirst=False)
```

**ধরন:** মেথড

এই টাইপের জন্য আলাদা ডেটাবেস অবজেক্ট থাকলে (PostgreSQL ENUM টাইপ) সেটি তৈরি করে। Boolean-এ কিছুই করে না; `Enum`-এ `CREATE TYPE` চালায়।

**উদাহরণ:**

```python
e = Enum(Status, name="status_t")
e.create(engine)
from sqlalchemy import inspect
print([x["name"] for x in inspect(engine).get_enums()])   # ['status_t']
```

### `Boolean.create_constraint` { #boolean-create-constraint }

**ধরন:** অ্যাট্রিবিউট

CHECK কনস্ট্রেইন্ট বানাবে কি না।

**উদাহরণ:**

```python
print(Boolean(create_constraint=True).create_constraint)   # True
```

### `Boolean.drop()` { #boolean-drop }

```python
Boolean.drop(bind, checkfirst=False)
```

**ধরন:** মেথড

`create()`-এর উল্টো: আলাদা টাইপ-অবজেক্ট মুছে দেয় (PostgreSQL `DROP TYPE`)।

**উদাহরণ:**

```python
e = Enum(Status, name="status_t"); e.create(engine); e.drop(engine)
from sqlalchemy import inspect
print(inspect(engine).get_enums())   # []
```

### `Boolean.inherit_schema` { #boolean-inherit-schema }

**ধরন:** প্রপার্টি

টাইপটি টেবিলের স্কিমা নিজে থেকে নেবে কি না (PostgreSQL ENUM কোন স্কিমায় তৈরি হবে)।

**উদাহরণ:**

```python
print(Enum(Status, inherit_schema=True).inherit_schema)   # True
```

### `Boolean.name` { #boolean-name }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্ট/টাইপের নাম (না দিলে `None`)।

**উদাহরণ:**

```python
print(Boolean(name="ck_flag").name)   # ck_flag
```

### `Boolean.native` { #boolean-native }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্টের native টাইপ ব্যবহার করবে কি না (`True`)।

**উদাহরণ:**

```python
print(Boolean().native)   # True
```

## `Enum` { #enum }

```python
from sqlalchemy import Enum
```

নির্দিষ্ট কিছু মানের যেকোনো একটি। Python `enum.Enum` ক্লাস বা স্ট্রিংগুলো দিন। PostgreSQL-এ একটি আলাদা `CREATE TYPE ... AS ENUM` তৈরি হয় (`create_all()`-এ নিজে থেকে); অন্য ডেটাবেসে `VARCHAR` + ঐচ্ছিক CHECK। Python enum দিলে ফেরত আসে enum সদস্য; ডেটাবেসে জমা হয় **নাম** (মান নয়; বদলাতে `values_callable`)।

**উদাহরণ:**

```python
print(rt(Enum(Status, name="status_t"), Status.published))   # Status.published
print(rt(Enum("S", "M", "L", name="size_t"), "M"))           # M
```

### কনস্ট্রাক্টরের প্যারামিটার { #enum-params }

```python
Enum(*enums, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `enums` | অনুমোদিত মানগুলো: একটি Python `Enum` ক্লাস, বা কয়েকটি স্ট্রিং। |
| `kw` | • `name`: ডেটাবেসে টাইপের নাম (PostgreSQL-এ বাধ্যতামূলক; Python enum দিলে না দিলে ক্লাসের নাম ছোট হাতে)।<br>• `native_enum` (ডিফল্ট `True`): native ENUM টাইপ; `False` দিলে `VARCHAR`।<br>• `create_constraint` (ডিফল্ট `False`): non-native হলে CHECK কনস্ট্রেইন্ট।<br>• `length`: non-native হলে `VARCHAR`-এর দৈর্ঘ্য।<br>• `values_callable`: enum ক্লাস নিয়ে জমা রাখার স্ট্রিং-তালিকা দেয়, যেমন `lambda e: [m.value for m in e]` (নামের বদলে মান জমা রাখতে)।<br>• `validate_strings`: অনুমোদিত নয় এমন স্ট্রিং দিলে Python-এই এরর।<br>• `schema`, `metadata`, `inherit_schema`, `quote`: টাইপটি কোন স্কিমা/MetaData-তে।<br>• `create_type` (২.১-এ নতুন, ডিফল্ট `True`): টেবিল তৈরির সময় `CREATE TYPE` চালাবে কি না (টাইপ আগেই থাকলে `False`)।<br>• `sort_key_function`: ORM primary key হিসেবে সাজানোর ফাংশন।<br>• `omit_aliases` (২.০, ডিফল্ট `True`): Python enum-এর alias সদস্য বাদ দেবে কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #enum-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`create_type`](#enum-create-type) | অ্যাট্রিবিউট | (২.১-এ নতুন) টেবিলের সাথে `CREATE TYPE` চলবে কি না। |
| [`enum_class`](#enum-enum-class) | অ্যাট্রিবিউট | Python enum ক্লাস দিলে সেটি (স্ট্রিং দিলে `None`)। |
| [`enums`](#enum-enums) | অ্যাট্রিবিউট | ডেটাবেসে জমা হবে এমন স্ট্রিংগুলোর তালিকা। |
| [`length`](#enum-length) | অ্যাট্রিবিউট | non-native রূপে `VARCHAR`-এর দৈর্ঘ্য (না দিলে সবচেয়ে লম্বা মানের দৈর্ঘ্য)। |
| [`metadata`](#enum-metadata) | অ্যাট্রিবিউট | টাইপটি যে `MetaData`-তে নিবন্ধিত (দিলে `create_all()`-এ টেবিল ছাড়াই তৈরি হয়)। |
| [`native_enum`](#enum-native-enum) | অ্যাট্রিবিউট | native ENUM টাইপ ব্যবহার হবে কি না। |
| [`schema`](#enum-schema) | অ্যাট্রিবিউট | ENUM টাইপের স্কিমা। |
| [`validate_strings`](#enum-validate-strings) | অ্যাট্রিবিউট | অনুমোদিত নয় এমন স্ট্রিং Python-এ ধরবে কি না। |
| [`values_callable`](#enum-values-callable) | অ্যাট্রিবিউট | জমা রাখার স্ট্রিং বানানোর ফাংশন (না দিলে `None`, মানে সদস্যের নাম)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Enum`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`Boolean` থেকে:** [`adapt_to_emulated()`](#boolean-adapt-to-emulated) · [`create()`](#boolean-create) · [`create_constraint`](#boolean-create-constraint) · [`drop()`](#boolean-drop) · [`inherit_schema`](#boolean-inherit-schema) · [`name`](#boolean-name) · [`native`](#boolean-native)

**`String` থেকে:** [`collation`](#string-collation) · [`collation_schema`](#string-collation-schema)

///

### `Enum.create_type` { #enum-create-type }

**ধরন:** অ্যাট্রিবিউট

(২.১-এ নতুন) টেবিলের সাথে `CREATE TYPE` চলবে কি না।

**উদাহরণ:**

```python
print(Enum(Status, create_type=False).create_type)   # False
```

### `Enum.enum_class` { #enum-enum-class }

**ধরন:** অ্যাট্রিবিউট

Python enum ক্লাস দিলে সেটি (স্ট্রিং দিলে `None`)।

**উদাহরণ:**

```python
print(Enum(Status).enum_class.__name__)   # Status
```

### `Enum.enums` { #enum-enums }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেসে জমা হবে এমন স্ট্রিংগুলোর তালিকা।

**উদাহরণ:**

```python
print(Enum(Status).enums, Enum(Status, values_callable=lambda e: [m.value.upper() for m in e]).enums)
# ['draft', 'published'] ['DRAFT', 'PUBLISHED']
```

### `Enum.length` { #enum-length }

**ধরন:** অ্যাট্রিবিউট

non-native রূপে `VARCHAR`-এর দৈর্ঘ্য (না দিলে সবচেয়ে লম্বা মানের দৈর্ঘ্য)।

**উদাহরণ:**

```python
print(Enum("S", "XXL", native_enum=False).length)   # 3
```

### `Enum.metadata` { #enum-metadata }

**ধরন:** অ্যাট্রিবিউট

টাইপটি যে `MetaData`-তে নিবন্ধিত (দিলে `create_all()`-এ টেবিল ছাড়াই তৈরি হয়)।

**উদাহরণ:**

```python
m = MetaData()
print(Enum(Status, name="st", metadata=m).metadata is m)   # True
```

### `Enum.native_enum` { #enum-native-enum }

**ধরন:** অ্যাট্রিবিউট

native ENUM টাইপ ব্যবহার হবে কি না।

**উদাহরণ:**

```python
print(pgt(Enum(Status, native_enum=False)))   # VARCHAR(9)
```

### `Enum.schema` { #enum-schema }

**ধরন:** অ্যাট্রিবিউট

ENUM টাইপের স্কিমা।

**উদাহরণ:**

```python
print(Enum(Status, name="st", schema="billing").schema)   # billing
```

### `Enum.validate_strings` { #enum-validate-strings }

**ধরন:** অ্যাট্রিবিউট

অনুমোদিত নয় এমন স্ট্রিং Python-এ ধরবে কি না।

**উদাহরণ:**

```python
try:
    rt(Enum("S", "M", name="sz", validate_strings=True), "XL")
except Exception as e:
    print(type(e.__cause__ or e).__name__)   # LookupError
```

### `Enum.values_callable` { #enum-values-callable }

**ধরন:** অ্যাট্রিবিউট

জমা রাখার স্ট্রিং বানানোর ফাংশন (না দিলে `None`, মানে সদস্যের নাম)।

**উদাহরণ:**

```python
e = Enum(Status, name="st2", values_callable=lambda cls: [m.value for m in cls])
print(rt(e, Status.draft))   # Status.draft  (ডেটাবেসে জমা হয়েছে "draft" মান)
```

## `SchemaType` { #schematype }

```python
from sqlalchemy.types import SchemaType
```

যেসব টাইপের সাথে আলাদা ডেটাবেস-অবজেক্ট (ENUM টাইপ, CHECK কনস্ট্রেইন্ট) জড়িত, তাদের মিক্সিন (`Boolean`, `Enum`)। টেবিল তৈরি/মোছার সাথে সেগুলোও তৈরি/মোছা হয়। নিচের সব সদস্যের ব্যাখ্যা `Boolean`-এ।

**উদাহরণ:**

```python
print(isinstance(Enum(Status), SchemaType), isinstance(Boolean(), SchemaType), isinstance(String(), SchemaType))   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #schematype-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SchemaType`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`adapt()`](#typeengine-adapt) · [`copy()`](#typeengine-copy)

**`Boolean` থেকে:** [`create()`](#boolean-create) · [`drop()`](#boolean-drop) · [`inherit_schema`](#boolean-inherit-schema)

///

## `MatchType` { #matchtype }

```python
from sqlalchemy.types import MatchType
```

`col.match(...)` (ফুল-টেক্সট সার্চ) এক্সপ্রেশনের ফলের টাইপ; একটি `Boolean`।

**উদাহরণ:**

```python
print(type(column("body", Text).match("x").type).__name__)   # MatchType
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Boolean`](#boolean-summary)-এর মতো।

## তারিখ ও সময় { #date-group }

## `Date` { #date }

```python
from sqlalchemy import Date
```

শুধু তারিখ (`DATE`) → Python `datetime.date`।

**উদাহরণ:**

```python
print(pgt(Date()), rt(Date, datetime.date(2024, 12, 16)))   # DATE 2024-12-16
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](#typeengine-summary)-এর মতো।

## `DateTime` { #datetime }

```python
from sqlalchemy import DateTime
```

তারিখ ও সময় → Python `datetime.datetime`। PostgreSQL-এ `TIMESTAMP WITHOUT TIME ZONE`; `timezone=True` দিলে `TIMESTAMP WITH TIME ZONE` (**প্রোডাকশনে এটাই সুপারিশকৃত**: ডেটাবেস UTC-তে রাখে, timezone-aware datetime ফেরত দেয়)।

**উদাহরণ:**

```python
dt = datetime.datetime(2024, 1, 1, 18, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=6)))
print(pgt(DateTime(timezone=True)), rt(DateTime(timezone=True), dt).astimezone(datetime.timezone.utc))
# TIMESTAMP WITH TIME ZONE 2024-01-01 12:00:00+00:00
```

### কনস্ট্রাক্টরের প্যারামিটার { #datetime-params }

```python
DateTime(timezone=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | `True` দিলে timezone-সহ টাইপ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #datetime-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`timezone`](#datetime-timezone) | অ্যাট্রিবিউট | timezone-সহ কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DateTime`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `DateTime.timezone` { #datetime-timezone }

**ধরন:** অ্যাট্রিবিউট

timezone-সহ কি না।

**উদাহরণ:**

```python
print(DateTime(timezone=True).timezone, pgt(DateTime()))   # True TIMESTAMP WITHOUT TIME ZONE
```

## `Time` { #time }

```python
from sqlalchemy import Time
```

শুধু দিনের সময় (`TIME`) → Python `datetime.time`; `timezone=True` দিলে `TIME WITH TIME ZONE`।

**উদাহরণ:**

```python
print(pgt(Time()), rt(Time, datetime.time(9, 30)))   # TIME WITHOUT TIME ZONE 09:30:00
```

### কনস্ট্রাক্টরের প্যারামিটার { #time-params }

```python
Time(timezone=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | `True` দিলে timezone-সহ। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DateTime`](#datetime-summary)-এর মতো।

## `Interval` { #interval }

```python
from sqlalchemy import Interval
```

সময়ের ব্যবধান → Python `datetime.timedelta`। PostgreSQL-এ native `INTERVAL`; অন্যত্র epoch থেকে একটি `DateTime` হিসেবে emulate করা হয়। তারিখের সাথে যোগ-বিয়োগ করা যায়।

**উদাহরণ:**

```python
print(pgt(Interval()), rt(Interval, datetime.timedelta(days=2, hours=3)))   # INTERVAL 2 days, 3:00:00
```

### কনস্ট্রাক্টরের প্যারামিটার { #interval-params }

```python
Interval(native=True, second_precision=None, day_precision=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `native` | native `INTERVAL` ব্যবহার করবে কি না (ডিফল্ট `True`)। |
| `second_precision` | সেকেন্ডের ভগ্নাংশের অঙ্ক (PostgreSQL `INTERVAL(n)`)। |
| `day_precision` | দিনের অঙ্ক (Oracle)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #interval-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`day_precision`](#interval-day-precision) | অ্যাট্রিবিউট | দিনের precision। |
| [`epoch`](#interval-epoch) | অ্যাট্রিবিউট | non-native রূপে ব্যবধান হিসাবের শূন্য-বিন্দু (`1970-01-01`)। |
| [`impl`](#interval-impl) | অ্যাট্রিবিউট | non-native রূপে আসল জমা-টাইপ (`DateTime`)। |
| [`second_precision`](#interval-second-precision) | অ্যাট্রিবিউট | সেকেন্ডের precision। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Interval`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_processor()`](#typeengine-bind-processor) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`TypeDecorator` থেকে:** [`TDComparatorContainer`](custom-types.md#typedecorator-TDComparatorContainer) · [`bind_expression()`](custom-types.md#typedecorator-bind-expression) · [`cache_ok`](custom-types.md#typedecorator-cache-ok) · [`coerce_compared_value()`](custom-types.md#typedecorator-coerce-compared-value) · [`coerce_to_is_types`](custom-types.md#typedecorator-coerce-to-is-types) · [`column_expression()`](custom-types.md#typedecorator-column-expression) · [`comparator_factory`](custom-types.md#typedecorator-comparator-factory) · [`impl_instance`](custom-types.md#typedecorator-impl-instance) · [`load_dialect_impl()`](custom-types.md#typedecorator-load-dialect-impl) · [`process_bind_param()`](custom-types.md#typedecorator-process-bind-param) · [`process_literal_param()`](custom-types.md#typedecorator-process-literal-param) · [`process_result_value()`](custom-types.md#typedecorator-process-result-value) · [`type_engine()`](custom-types.md#typedecorator-type-engine)

**`Boolean` থেকে:** [`adapt_to_emulated()`](#boolean-adapt-to-emulated) · [`native`](#boolean-native)

///

### `Interval.day_precision` { #interval-day-precision }

**ধরন:** অ্যাট্রিবিউট

দিনের precision।

**উদাহরণ:**

```python
print(Interval(day_precision=3).day_precision)   # 3
```

### `Interval.epoch` { #interval-epoch }

**ধরন:** অ্যাট্রিবিউট

non-native রূপে ব্যবধান হিসাবের শূন্য-বিন্দু (`1970-01-01`)।

**উদাহরণ:**

```python
print(Interval.epoch)   # 1970-01-01 00:00:00
```

### `Interval.impl` { #interval-impl }

**ধরন:** অ্যাট্রিবিউট

non-native রূপে আসল জমা-টাইপ (`DateTime`)।

**উদাহরণ:**

```python
print(Interval.impl.__name__)   # DateTime
```

### `Interval.second_precision` { #interval-second-precision }

**ধরন:** অ্যাট্রিবিউট

সেকেন্ডের precision।

**উদাহরণ:**

```python
print(pgt(Interval(second_precision=2)))   # INTERVAL (2)
```

## বাইনারি, JSON, ARRAY ও অন্যান্য { #largebinary-group }

## `LargeBinary` { #largebinary }

```python
from sqlalchemy import LargeBinary
```

বাইনারি ডেটা → Python `bytes` (PostgreSQL `BYTEA`, MySQL `BLOB`)। বড় ফাইল ডেটাবেসে না রেখে স্টোরেজে (S3) রেখে শুধু পাথ রাখাই সাধারণত ভালো।

**উদাহরণ:**

```python
print(pgt(LargeBinary()), rt(LargeBinary, b"\x00\xff"))   # BYTEA b'\x00\xff'
```

### কনস্ট্রাক্টরের প্যারামিটার { #largebinary-params }

```python
LargeBinary(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য (কিছু ডেটাবেসে)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #largebinary-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `LargeBinary`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`String` থেকে:** [`length`](#string-length)

///

## `JSON` { #json }

```python
from sqlalchemy import JSON
```

JSON ডেটা → Python dict/list। PostgreSQL-এ `JSON` (ইনডেক্স ও বেশি অপারেটরের জন্য `postgresql.JSONB` ভালো), MySQL, SQLite-এও কাজ করে। `col["key"]` দিয়ে ভেতরের মান, আর `.as_string()`, `.as_integer()` দিয়ে টাইপসহ বের করা যায়। ORM-এ dict-এর ভেতরে বদলালে নিজে থেকে ধরা পড়ে না; `MutableDict` বা পুরো মান বদলান।

**উদাহরণ:**

```python
v = rt(JSON, {"name": "রহিম", "tags": ["a", "b"]})
print(v["tags"], type(v).__name__)   # ['a', 'b'] dict
```

### কনস্ট্রাক্টরের প্যারামিটার { #json-params }

```python
JSON(none_as_null=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `True` দিলে Python `None` → SQL `NULL`; ডিফল্টে (`False`) → JSON `null`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #json-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`JSONElementType`](#json-JSONElementType) | অ্যাট্রিবিউট (internal) | `col[...]`-এর index/path মানের জন্য ভেতরের টাইপ। |
| [`JSONIndexType`](#json-JSONIndexType) | অ্যাট্রিবিউট (internal) | `col["key"]` / `col[0]`-এর index-মানের টাইপ (ডায়ালেক্ট নিজের রূপ দেয়)। |
| [`JSONIntIndexType`](#json-JSONIntIndexType) | অ্যাট্রিবিউট (internal) | পূর্ণসংখ্যা index-এর টাইপ। |
| [`JSONPathType`](#json-JSONPathType) | অ্যাট্রিবিউট (internal) | `col[("a", "b")]` ধরনের path-এর টাইপ। |
| [`JSONStrIndexType`](#json-JSONStrIndexType) | অ্যাট্রিবিউট (internal) | স্ট্রিং key-এর টাইপ। |
| [`NULL`](#json-NULL) | অ্যাট্রিবিউট | JSON-এর `null` মান স্পষ্টভাবে দিতে (SQL `NULL` নয়)। |
| [`none_as_null`](#json-none-as-null) | অ্যাট্রিবিউট | `None` → SQL NULL কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSON`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `JSON.JSONElementType` { #json-JSONElementType }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`col[...]`-এর index/path মানের জন্য ভেতরের টাইপ।

### `JSON.JSONIndexType` { #json-JSONIndexType }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`col["key"]` / `col[0]`-এর index-মানের টাইপ (ডায়ালেক্ট নিজের রূপ দেয়)।

### `JSON.JSONIntIndexType` { #json-JSONIntIndexType }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

পূর্ণসংখ্যা index-এর টাইপ।

### `JSON.JSONPathType` { #json-JSONPathType }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`col[("a", "b")]` ধরনের path-এর টাইপ।

### `JSON.JSONStrIndexType` { #json-JSONStrIndexType }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্ট্রিং key-এর টাইপ।

### `JSON.NULL` { #json-NULL }

**ধরন:** অ্যাট্রিবিউট

JSON-এর `null` মান স্পষ্টভাবে দিতে (SQL `NULL` নয়)। `none_as_null=True` কলামেও JSON null রাখতে কাজে লাগে।

**উদাহরণ:**

```python
m = MetaData()
t = Table("j", m, Column("id", Integer, primary_key=True), Column("v", JSON(none_as_null=True)))
m.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(t), [{"id": 1, "v": None}, {"id": 2, "v": JSON.NULL}])
    print(conn.exec_driver_sql("SELECT id, v IS NULL FROM j ORDER BY id").all())   # [(1, True), (2, False)]
```

### `JSON.none_as_null` { #json-none-as-null }

**ধরন:** অ্যাট্রিবিউট

`None` → SQL NULL কি না।

**উদাহরণ:**

```python
print(JSON().none_as_null, JSON(none_as_null=True).none_as_null)   # False True
```

## `JSON.Comparator` { #json-comparator }

```python
from sqlalchemy import JSON
```

JSON কলামের অপারেটর: `col["key"]` (index), `col[("a", "b")]` (path), আর ফলকে নির্দিষ্ট টাইপে বের করার নিচের মেথডগুলো। `col["key"]`-এর ফল নিজেও JSON, তাই তুলনা/সাজানোর আগে `.as_string()` ইত্যাদি দিন।

**উদাহরণ:**

```python
m = MetaData()
t = Table("docs", m, Column("id", Integer, primary_key=True), Column("data", JSON))
m.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(t), [{"data": {"name": "রহিম", "age": 30}}, {"data": {"name": "করিম", "age": 25}}])
    print(conn.execute(select(t.c.data["name"].as_string()).where(t.c.data["age"].as_integer() > 26)).scalars().all())
    # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #json-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_boolean()`](#json-comparator-as-boolean) | মেথড | JSON মানকে বুলিয়ান হিসেবে বের করে। |
| [`as_float()`](#json-comparator-as-float) | মেথড | ভাসমান-বিন্দু হিসেবে বের করে। |
| [`as_integer()`](#json-comparator-as-integer) | মেথড | পূর্ণসংখ্যা হিসেবে বের করে (তুলনা/যোগে ব্যবহারযোগ্য)। |
| [`as_json()`](#json-comparator-as-json) | মেথড | মানটিকে JSON হিসেবেই রাখে (ডিফল্ট আচরণ; অন্য টাইপ থেকে আবার JSON করতে)। |
| [`as_numeric()`](#json-comparator-as-numeric) | মেথড | `Numeric(precision, scale)` হিসেবে বের করে (টাকার অঙ্কের জন্য)। |
| [`as_string()`](#json-comparator-as-string) | মেথড | স্ট্রিং হিসেবে বের করে (PostgreSQL-এ `->>`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSON.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `JSON.Comparator.as_boolean()` { #json-comparator-as-boolean }

```python
JSON.Comparator.as_boolean()
```

**ধরন:** মেথড

JSON মানকে বুলিয়ান হিসেবে বের করে।

**উদাহরণ:**

```python
print(column("d", JSON)["ok"].as_boolean().type)   # BOOLEAN
```

### `JSON.Comparator.as_float()` { #json-comparator-as-float }

```python
JSON.Comparator.as_float()
```

**ধরন:** মেথড

ভাসমান-বিন্দু হিসেবে বের করে।

**উদাহরণ:**

```python
print(column("d", JSON)["score"].as_float().type)   # FLOAT
```

### `JSON.Comparator.as_integer()` { #json-comparator-as-integer }

```python
JSON.Comparator.as_integer()
```

**ধরন:** মেথড

পূর্ণসংখ্যা হিসেবে বের করে (তুলনা/যোগে ব্যবহারযোগ্য)।

**উদাহরণ:**

```python
print(column("d", JSON)["age"].as_integer().type)   # INTEGER
```

### `JSON.Comparator.as_json()` { #json-comparator-as-json }

```python
JSON.Comparator.as_json()
```

**ধরন:** মেথড

মানটিকে JSON হিসেবেই রাখে (ডিফল্ট আচরণ; অন্য টাইপ থেকে আবার JSON করতে)।

**উদাহরণ:**

```python
print(type(column("d", JSON)["tags"].as_json().type).__name__)   # JSON
```

### `JSON.Comparator.as_numeric()` { #json-comparator-as-numeric }

```python
JSON.Comparator.as_numeric(precision, scale, asdecimal=True)
```

**ধরন:** মেথড

`Numeric(precision, scale)` হিসেবে বের করে (টাকার অঙ্কের জন্য)।

**উদাহরণ:**

```python
print(column("d", JSON)["price"].as_numeric(10, 2).type)   # NUMERIC(10, 2)
```

### `JSON.Comparator.as_string()` { #json-comparator-as-string }

```python
JSON.Comparator.as_string()
```

**ধরন:** মেথড

স্ট্রিং হিসেবে বের করে (PostgreSQL-এ `->>`)।

**উদাহরণ:**

```python
print(column("d", JSON)["name"].as_string().compile(dialect=postgresql.dialect()))   # CAST(d ->> %(d_1)s::TEXT AS VARCHAR)
```

## `ARRAY` { #array }

```python
from sqlalchemy import ARRAY
```

অ্যারে কলাম (মূলত PostgreSQL) → Python list। `col[1]` দিয়ে উপাদান (PostgreSQL-এ index ১ থেকে), `col[1:3]` slice, আর `any_()`/`all_()`। PostgreSQL-এর বাড়তি অপারেটর (`contains`, `overlap`) চাইলে `postgresql.ARRAY`।

**উদাহরণ:**

```python
print(pgt(ARRAY(Integer)), rt(ARRAY(Integer), [3, 1, 2]))   # INTEGER[] [3, 1, 2]
```

### কনস্ট্রাক্টরের প্যারামিটার { #array-params }

```python
ARRAY(item_type, as_tuple=False, dimensions=None, zero_indexes=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `item_type` | উপাদানের টাইপ। |
| `as_tuple` | `True` দিলে list-এর বদলে tuple ফেরত দেয় (hashable হয়)। |
| `dimensions` | মাত্রা (`2` = অ্যারের অ্যারে)। |
| `zero_indexes` | `True` দিলে Python-এর মতো ০ থেকে index ধরে (SQL-এ পাঠানোর সময় +১ করে)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #array-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_tuple`](#array-as-tuple) | অ্যাট্রিবিউট | tuple ফেরত দেবে কি না। |
| [`dimensions`](#array-dimensions) | অ্যাট্রিবিউট | মাত্রা। |
| [`item_type`](#array-item-type) | অ্যাট্রিবিউট | উপাদানের টাইপ। |
| [`zero_indexes`](#array-zero-indexes) | অ্যাট্রিবিউট | ০-ভিত্তিক index কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ARRAY`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

///

### `ARRAY.as_tuple` { #array-as-tuple }

**ধরন:** অ্যাট্রিবিউট

tuple ফেরত দেবে কি না।

**উদাহরণ:**

```python
print(rt(ARRAY(Integer, as_tuple=True), [1, 2]))   # (1, 2)
```

### `ARRAY.dimensions` { #array-dimensions }

**ধরন:** অ্যাট্রিবিউট

মাত্রা।

**উদাহরণ:**

```python
print(pgt(ARRAY(Integer, dimensions=2)))   # INTEGER[][]
```

### `ARRAY.item_type` { #array-item-type }

**ধরন:** অ্যাট্রিবিউট

উপাদানের টাইপ।

**উদাহরণ:**

```python
print(ARRAY(String(10)).item_type)   # VARCHAR(10)
```

### `ARRAY.zero_indexes` { #array-zero-indexes }

**ধরন:** অ্যাট্রিবিউট

০-ভিত্তিক index কি না।

**উদাহরণ:**

```python
m = MetaData()
t = Table("arr", m, Column("id", Integer, primary_key=True), Column("v", ARRAY(Integer, zero_indexes=True)))
m.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(t).values(v=[10, 20, 30]))
    print(conn.execute(select(t.c.v[0])).scalar())   # 10
```

## `ARRAY.Comparator` { #array-comparator }

```python
from sqlalchemy import ARRAY
```

ARRAY কলামের অপারেটর: index/slice, আর পুরোনো ধাঁচের `any()` / `all()`।

**উদাহরণ:**

```python
print(column("v", ARRAY(Integer))[2:3].compile(dialect=postgresql.dialect()))   # v[%(v_1)s::INTEGER:%(v_2)s::INTEGER]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #array-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#array-comparator-all) | মেথড (legacy) | `মান <op> ALL (col)` বানায়। |
| [`any()`](#array-comparator-any) | মেথড (legacy) | `মান = ANY (col)` বানায়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ARRAY.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `ARRAY.Comparator.all()` { #array-comparator-all }

```python
ARRAY.Comparator.all(other, operator=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`মান <op> ALL (col)` বানায়। নতুন কোডে `col.all_()` (কলাম অপারেটর) ব্যবহার করুন।

**উদাহরণ:**

```python
print(column("v", ARRAY(Integer)).all(5, operator=operators.lt))   # :v_1 < ALL (v)
```

### `ARRAY.Comparator.any()` { #array-comparator-any }

```python
ARRAY.Comparator.any(other, operator=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`মান = ANY (col)` বানায়। নতুন কোডে `col.any_()`।

**উদাহরণ:**

```python
print(column("v", ARRAY(Integer)).any(5))   # :v_1 = ANY (v)
```

## `PickleType` { #pickletype }

```python
from sqlalchemy import PickleType
```

যেকোনো Python অবজেক্ট `pickle` করে বাইনারি হিসেবে রাখে। **সতর্কতা:** ডেটাবেসে কুয়েরি/ইনডেক্স করা যায় না, অন্য ভাষা পড়তে পারে না, আর অবিশ্বস্ত ডেটা unpickle করা নিরাপত্তা-ঝুঁকি; সম্ভব হলে `JSON` ব্যবহার করুন।

**উদাহরণ:**

```python
print(pgt(PickleType()), rt(PickleType, {"a": {1, 2}}))   # BYTEA {'a': {1, 2}}
```

### কনস্ট্রাক্টরের প্যারামিটার { #pickletype-params }

```python
PickleType(protocol=5, pickler=None, comparator=None, impl=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `protocol` | pickle protocol (ডিফল্ট ৫)। |
| `pickler` | `pickle`-এর বদলে অন্য মডিউল (যেমন `cloudpickle`)। |
| `comparator` | দুটি মান সমান কি না তুলনার ফাংশন (dirty-checking-এ)। |
| `impl` | জমা রাখার আসল টাইপ (ডিফল্ট `LargeBinary`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #pickletype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`comparator`](#pickletype-comparator) | অ্যাট্রিবিউট | তুলনার ফাংশন (না দিলে `None`, মানে `==`)। |
| [`pickler`](#pickletype-pickler) | অ্যাট্রিবিউট | ব্যবহৃত pickle মডিউল। |
| [`protocol`](#pickletype-protocol) | অ্যাট্রিবিউট | pickle protocol। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `PickleType`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_processor()`](#typeengine-bind-processor) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`TypeDecorator` থেকে:** [`TDComparatorContainer`](custom-types.md#typedecorator-TDComparatorContainer) · [`bind_expression()`](custom-types.md#typedecorator-bind-expression) · [`cache_ok`](custom-types.md#typedecorator-cache-ok) · [`coerce_compared_value()`](custom-types.md#typedecorator-coerce-compared-value) · [`coerce_to_is_types`](custom-types.md#typedecorator-coerce-to-is-types) · [`column_expression()`](custom-types.md#typedecorator-column-expression) · [`comparator_factory`](custom-types.md#typedecorator-comparator-factory) · [`impl`](custom-types.md#typedecorator-impl) · [`impl_instance`](custom-types.md#typedecorator-impl-instance) · [`load_dialect_impl()`](custom-types.md#typedecorator-load-dialect-impl) · [`process_bind_param()`](custom-types.md#typedecorator-process-bind-param) · [`process_literal_param()`](custom-types.md#typedecorator-process-literal-param) · [`process_result_value()`](custom-types.md#typedecorator-process-result-value) · [`type_engine()`](custom-types.md#typedecorator-type-engine)

///

### `PickleType.comparator` { #pickletype-comparator }

**ধরন:** অ্যাট্রিবিউট

তুলনার ফাংশন (না দিলে `None`, মানে `==`)।

**উদাহরণ:**

```python
print(PickleType().comparator)   # None
```

### `PickleType.pickler` { #pickletype-pickler }

**ধরন:** অ্যাট্রিবিউট

ব্যবহৃত pickle মডিউল।

**উদাহরণ:**

```python
print(PickleType().pickler.__name__)   # pickle
```

### `PickleType.protocol` { #pickletype-protocol }

**ধরন:** অ্যাট্রিবিউট

pickle protocol।

**উদাহরণ:**

```python
print(PickleType().protocol)   # 5
```

## `Uuid` { #uuid }

```python
from sqlalchemy import Uuid
```

(২.০) UUID → Python `uuid.UUID`। PostgreSQL-এ native `UUID`; অন্যত্র `CHAR(32)`। ORM-এ `Mapped[uuid.UUID]` লিখলে এটাই বসে।

**উদাহরণ:**

```python
u = uuid.UUID("12345678-1234-5678-1234-567812345678")
print(pgt(Uuid()), rt(Uuid, u) == u)   # UUID True
```

### কনস্ট্রাক্টরের প্যারামিটার { #uuid-params }

```python
Uuid(as_uuid=True, native_uuid=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `as_uuid` | `True` (ডিফল্ট) হলে `uuid.UUID` ফেরত দেয়, `False` হলে স্ট্রিং। |
| `native_uuid` | native UUID টাইপ ব্যবহার করবে কি না (ডিফল্ট `True`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #uuid-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_uuid`](#uuid-as-uuid) | অ্যাট্রিবিউট | `uuid.UUID` ফেরত দেবে কি না। |
| [`native_uuid`](#uuid-native-uuid) | অ্যাট্রিবিউট | native টাইপ ব্যবহার হবে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Uuid`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`Boolean` থেকে:** [`adapt_to_emulated()`](#boolean-adapt-to-emulated) · [`native`](#boolean-native)

**`String` থেকে:** [`collation`](#string-collation) · [`collation_schema`](#string-collation-schema) · [`length`](#string-length)

///

### `Uuid.as_uuid` { #uuid-as-uuid }

**ধরন:** অ্যাট্রিবিউট

`uuid.UUID` ফেরত দেবে কি না।

**উদাহরণ:**

```python
print(rt(Uuid(as_uuid=False), "12345678-1234-5678-1234-567812345678"))   # 12345678-1234-5678-1234-567812345678
```

### `Uuid.native_uuid` { #uuid-native-uuid }

**ধরন:** অ্যাট্রিবিউট

native টাইপ ব্যবহার হবে কি না।

**উদাহরণ:**

```python
print(Uuid(native_uuid=False).compile(dialect=postgresql.dialect()))   # CHAR(32)
```

## `TupleType` { #tupletype }

```python
from sqlalchemy.types import TupleType
```

`tuple_(a, b)` এক্সপ্রেশনের টাইপ (কলাম টাইপ হিসেবে নয়): প্রতিটি অবস্থানের টাইপ।

**উদাহরণ:**

```python
print(type(tuple_(column("a", Integer), column("b", String)).type).__name__)   # TupleType
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](#typeengine-summary)-এর মতো।

## `NullType` { #nulltype }

```python
from sqlalchemy.types import NullType
```

"অজানা টাইপ": টাইপ না দিলে বা SQLAlchemy অনুমান করতে না পারলে (যেমন `func.অচেনা()`-এর ফল, reflection-এ অচেনা টাইপ)। মান কোনো রূপান্তর ছাড়া যেমন আছে তেমন যায়-আসে।

**উদাহরণ:**

```python
print(type(func.my_custom_fn().type).__name__, type(column("x").type).__name__)   # NullType NullType
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](#typeengine-summary)-এর মতো।

## মিক্সিন ও OperatorClass { #concatenable-group }

## `Concatenable` { #concatenable }

```python
from sqlalchemy.types import Concatenable
```

যেসব টাইপে `+` মানে জোড়া লাগানো (`||`), তাদের মিক্সিন (`String`, `ARRAY`, `LargeBinary` …)।

**উদাহরণ:**

```python
print(isinstance(String(), Concatenable), column("a", String) + "!")   # True a || :a_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #concatenable-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Concatenable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`comparator_factory`](#typeengine-comparator-factory)

///

## `Indexable` { #indexable }

```python
from sqlalchemy.types import Indexable
```

যেসব টাইপে `col[...]` index চলে, তাদের মিক্সিন (`JSON`, `ARRAY`)।

**উদাহরণ:**

```python
print(isinstance(JSON(), Indexable), isinstance(ARRAY(Integer), Indexable), isinstance(String(), Indexable))   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #indexable-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Indexable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`comparator_factory`](#typeengine-comparator-factory)

///

## `NumericCommon` { #numericcommon }

```python
from sqlalchemy.types import NumericCommon
```

(২.১-এ নতুন) `Numeric` আর `Float`-এর সাধারণ ভিত্তি (২.১-এ `Float` আর `Numeric`-এর সাবক্লাস নয়, দুটোই এর সাবক্লাস)। `isinstance(t, NumericCommon)` দিয়ে "যেকোনো দশমিক টাইপ" যাচাই করা যায়।

**উদাহরণ:**

```python
print(isinstance(Float(), NumericCommon), isinstance(Numeric(), NumericCommon), isinstance(Float(), Numeric))   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #numericcommon-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `NumericCommon`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`bind_processor()`](#typeengine-bind-processor) · [`comparator_factory`](#typeengine-comparator-factory) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type)

///

## `OperatorClass` { #operatorclass }

```python
from sqlalchemy.types import OperatorClass
```

(২.১-এ নতুন) built-in অপারেটরের শ্রেণি-flag। প্রতিটি টাইপের `operator_classes` জানায় তাতে কোন অপারেটর বৈধ; নিজের `op()`-এ `operator_class=` দিয়ে জানানো যায় কাস্টম অপারেটরটি কোন শ্রেণির।

**উদাহরণ:**

```python
print(OperatorClass.STRING_MATCH in String().operator_classes, OperatorClass.STRING_MATCH in Integer().operator_classes)   # True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #operatorclass-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`BASE`](#operatorclass-BASE) | অ্যাট্রিবিউট | সব টাইপে বৈধ মৌলিক অপারেটর। |
| [`BITWISE`](#operatorclass-BITWISE) | অ্যাট্রিবিউট | বিট-অপারেটর (`bitwise_and()` …), পূর্ণসংখ্যায়। |
| [`BOOLEAN_ALGEBRA`](#operatorclass-BOOLEAN-ALGEBRA) | অ্যাট্রিবিউট | `AND`/`OR`/`NOT`, বুলিয়ানে। |
| [`CONCATENABLE`](#operatorclass-CONCATENABLE) | অ্যাট্রিবিউট | জোড়া লাগানো (<code>&#124;&#124;</code>)। |
| [`CONTAINS`](#operatorclass-CONTAINS) | অ্যাট্রিবিউট | ধারণ-অপারেটর (`contains()` ইত্যাদি)। |
| [`DATE_ARITHEMETIC`](#operatorclass-DATE-ARITHEMETIC) | অ্যাট্রিবিউট | তারিখের গাণিতিক (তারিখ ± interval)। |
| [`EQUALITY`](#operatorclass-EQUALITY) | অ্যাট্রিবিউট | `=`, `!=`। |
| [`INDEXABLE`](#operatorclass-INDEXABLE) | অ্যাট্রিবিউট | `col[...]` index। |
| [`JSON_GETITEM`](#operatorclass-JSON-GETITEM) | অ্যাট্রিবিউট | JSON-এর `[]` ও path। |
| [`MATH`](#operatorclass-MATH) | অ্যাট্রিবিউট | গাণিতিক (`+`, `-`, `*`, `/` …)। |
| [`ORDERING`](#operatorclass-ORDERING) | অ্যাট্রিবিউট | `<`, `>`, `ORDER BY` ইত্যাদি। |
| [`STRING_MATCH`](#operatorclass-STRING-MATCH) | অ্যাট্রিবিউট | `LIKE`, `ILIKE`, regex ইত্যাদি। |
| [`UNSPECIFIED`](#operatorclass-UNSPECIFIED) | অ্যাট্রিবিউট | অনির্দিষ্ট (কোনো শ্রেণি বলা নেই)। |

### `OperatorClass.BASE` { #operatorclass-BASE }

**ধরন:** অ্যাট্রিবিউট

সব টাইপে বৈধ মৌলিক অপারেটর।

**উদাহরণ:**

```python
print(OperatorClass.BASE.value)   # 2
```

### `OperatorClass.BITWISE` { #operatorclass-BITWISE }

**ধরন:** অ্যাট্রিবিউট

বিট-অপারেটর (`bitwise_and()` …), পূর্ণসংখ্যায়।

**উদাহরণ:**

```python
print(OperatorClass.BITWISE in Integer().operator_classes)   # True
```

### `OperatorClass.BOOLEAN_ALGEBRA` { #operatorclass-BOOLEAN-ALGEBRA }

**ধরন:** অ্যাট্রিবিউট

`AND`/`OR`/`NOT`, বুলিয়ানে।

**উদাহরণ:**

```python
print(OperatorClass.BOOLEAN_ALGEBRA in Boolean().operator_classes)   # True
```

### `OperatorClass.CONCATENABLE` { #operatorclass-CONCATENABLE }

**ধরন:** অ্যাট্রিবিউট

জোড়া লাগানো (`||`)।

**উদাহরণ:**

```python
print(OperatorClass.CONCATENABLE in String().operator_classes)   # True
```

### `OperatorClass.CONTAINS` { #operatorclass-CONTAINS }

**ধরন:** অ্যাট্রিবিউট

ধারণ-অপারেটর (`contains()` ইত্যাদি)।

**উদাহরণ:**

```python
print(OperatorClass.CONTAINS.value)   # 64
```

### `OperatorClass.DATE_ARITHEMETIC` { #operatorclass-DATE-ARITHEMETIC }

**ধরন:** অ্যাট্রিবিউট

তারিখের গাণিতিক (তারিখ ± interval)। (নামের বানান SQLAlchemy-তে এভাবেই।)

**উদাহরণ:**

```python
print(OperatorClass.DATE_ARITHEMETIC in DateTime().operator_classes)   # True
```

### `OperatorClass.EQUALITY` { #operatorclass-EQUALITY }

**ধরন:** অ্যাট্রিবিউট

`=`, `!=`।

**উদাহরণ:**

```python
print(OperatorClass.EQUALITY in JSON().operator_classes)   # True
```

### `OperatorClass.INDEXABLE` { #operatorclass-INDEXABLE }

**ধরন:** অ্যাট্রিবিউট

`col[...]` index।

**উদাহরণ:**

```python
print(OperatorClass.INDEXABLE in ARRAY(Integer).operator_classes)   # True
```

### `OperatorClass.JSON_GETITEM` { #operatorclass-JSON-GETITEM }

**ধরন:** অ্যাট্রিবিউট

JSON-এর `[]` ও path।

**উদাহরণ:**

```python
print(OperatorClass.JSON_GETITEM in JSON().operator_classes)   # True
```

### `OperatorClass.MATH` { #operatorclass-MATH }

**ধরন:** অ্যাট্রিবিউট

গাণিতিক (`+`, `-`, `*`, `/` …)।

**উদাহরণ:**

```python
print(OperatorClass.MATH in Numeric().operator_classes)   # True
```

### `OperatorClass.ORDERING` { #operatorclass-ORDERING }

**ধরন:** অ্যাট্রিবিউট

`<`, `>`, `ORDER BY` ইত্যাদি।

**উদাহরণ:**

```python
print(OperatorClass.ORDERING in Date().operator_classes)   # True
```

### `OperatorClass.STRING_MATCH` { #operatorclass-STRING-MATCH }

**ধরন:** অ্যাট্রিবিউট

`LIKE`, `ILIKE`, regex ইত্যাদি।

**উদাহরণ:**

```python
print(OperatorClass.STRING_MATCH in Text().operator_classes)   # True
```

### `OperatorClass.UNSPECIFIED` { #operatorclass-UNSPECIFIED }

**ধরন:** অ্যাট্রিবিউট

অনির্দিষ্ট (কোনো শ্রেণি বলা নেই)।

**উদাহরণ:**

```python
print(OperatorClass.UNSPECIFIED.value)   # 1
```

## SQL স্ট্যান্ডার্ড (বড় হাতের) টাইপ { #varchar-group }

## `VARCHAR` { #varchar }

```python
from sqlalchemy import VARCHAR
```

ঠিক `VARCHAR(n)`, সব ডেটাবেসে।

**উদাহরণ:**

```python
print(pgt(VARCHAR(20)))   # VARCHAR(20)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `CHAR` { #char }

```python
from sqlalchemy import CHAR
```

নির্দিষ্ট দৈর্ঘ্যের স্ট্রিং `CHAR(n)` (ছোট হলে ডান দিকে ফাঁকা দিয়ে পূর্ণ হয়)।

**উদাহরণ:**

```python
print(pgt(CHAR(3)), repr(rt(CHAR(3), "ab")))   # CHAR(3) 'ab '
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `TEXT` { #text }

```python
from sqlalchemy import TEXT
```

ঠিক `TEXT`।

**উদাহরণ:**

```python
print(pgt(TEXT()))   # TEXT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `CLOB` { #clob }

```python
from sqlalchemy import CLOB
```

`CLOB` (Oracle-এর বড় লেখা)। PostgreSQL-এ এই টাইপ নেই।

**উদাহরণ:**

```python
print(CLOB().compile())   # CLOB
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `NVARCHAR` { #nvarchar }

```python
from sqlalchemy import NVARCHAR
```

`NVARCHAR(n)` (SQL Server/Oracle-এর Unicode স্ট্রিং)।

**উদাহরণ:**

```python
print(NVARCHAR(10).compile())   # NVARCHAR(10)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `NCHAR` { #nchar }

```python
from sqlalchemy import NCHAR
```

`NCHAR(n)`।

**উদাহরণ:**

```python
print(NCHAR(5).compile())   # NCHAR(5)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](#string-summary)-এর মতো।

## `INTEGER` { #integer }

```python
from sqlalchemy import INTEGER
```

ঠিক `INTEGER`।

**উদাহরণ:**

```python
print(pgt(INTEGER()))   # INTEGER
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `INT` { #int }

```python
from sqlalchemy import INT
```

`INTEGER`-এর আরেক নাম।

**উদাহরণ:**

```python
print(INT is INTEGER)   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `SMALLINT` { #smallint }

```python
from sqlalchemy import SMALLINT
```

ঠিক `SMALLINT`।

**উদাহরণ:**

```python
print(pgt(SMALLINT()))   # SMALLINT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `BIGINT` { #bigint }

```python
from sqlalchemy import BIGINT
```

ঠিক `BIGINT`।

**উদাহরণ:**

```python
print(pgt(BIGINT()))   # BIGINT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](#integer)-এর মতো, অর্থাৎ [`TypeEngine`](#typeengine-summary)-এর মতো।

## `NUMERIC` { #numeric }

```python
from sqlalchemy import NUMERIC
```

ঠিক `NUMERIC(p, s)`।

**উদাহরণ:**

```python
print(pgt(NUMERIC(12, 4)))   # NUMERIC(12, 4)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Numeric`](#numeric-summary)-এর মতো।

## `DECIMAL` { #decimal }

```python
from sqlalchemy import DECIMAL
```

ঠিক `DECIMAL(p, s)`।

**উদাহরণ:**

```python
print(pgt(DECIMAL(8, 2)))   # DECIMAL(8, 2)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Numeric`](#numeric-summary)-এর মতো।

## `FLOAT` { #float }

```python
from sqlalchemy import FLOAT
```

ঠিক `FLOAT`।

**উদাহরণ:**

```python
print(pgt(FLOAT()))   # FLOAT
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Float`](#float)-এর মতো, অর্থাৎ [`Numeric`](#numeric-summary)-এর মতো।

## `REAL` { #real }

```python
from sqlalchemy import REAL
```

ঠিক `REAL` (single precision)।

**উদাহরণ:**

```python
print(pgt(REAL()))   # REAL
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Float`](#float)-এর মতো, অর্থাৎ [`Numeric`](#numeric-summary)-এর মতো।

## `DOUBLE` { #double }

```python
from sqlalchemy import DOUBLE
```

(২.০) ঠিক `DOUBLE` (MySQL ইত্যাদি)। PostgreSQL-এ `DOUBLE PRECISION` বসায়।

**উদাহরণ:**

```python
print(DOUBLE().compile(dialect=mysql.dialect()))   # DOUBLE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Float`](#float)-এর মতো, অর্থাৎ [`Numeric`](#numeric-summary)-এর মতো।

## `DOUBLE_PRECISION` { #double-precision }

```python
from sqlalchemy import DOUBLE_PRECISION
```

(২.০) ঠিক `DOUBLE PRECISION`।

**উদাহরণ:**

```python
print(pgt(DOUBLE_PRECISION()))   # DOUBLE PRECISION
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Float`](#float)-এর মতো, অর্থাৎ [`Numeric`](#numeric-summary)-এর মতো।

## `BOOLEAN` { #boolean }

```python
from sqlalchemy import BOOLEAN
```

ঠিক `BOOLEAN`।

**উদাহরণ:**

```python
print(pgt(BOOLEAN()))   # BOOLEAN
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Boolean`](#boolean-summary)-এর মতো।

## `DATE` { #date }

```python
from sqlalchemy import DATE
```

ঠিক `DATE`।

**উদাহরণ:**

```python
print(pgt(DATE()))   # DATE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](#typeengine-summary)-এর মতো।

## `DATETIME` { #datetime }

```python
from sqlalchemy import DATETIME
```

ঠিক `DATETIME` (MySQL/SQL Server)। PostgreSQL-এ এই নাম নেই; সেখানে `TIMESTAMP`।

**উদাহরণ:**

```python
print(DATETIME().compile(dialect=mysql.dialect()))   # DATETIME
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DateTime`](#datetime-summary)-এর মতো।

## `TIMESTAMP` { #timestamp }

```python
from sqlalchemy import TIMESTAMP
```

ঠিক `TIMESTAMP` (`timezone=True` দিলে PostgreSQL-এ `TIMESTAMP WITH TIME ZONE`)।

**উদাহরণ:**

```python
print(pgt(TIMESTAMP(timezone=True)))   # TIMESTAMP WITH TIME ZONE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DateTime`](#datetime-summary)-এর মতো।

## `TIME` { #time }

```python
from sqlalchemy import TIME
```

ঠিক `TIME`।

**উদাহরণ:**

```python
print(pgt(TIME()))   # TIME WITHOUT TIME ZONE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DateTime`](#datetime-summary)-এর মতো।

## `BINARY` { #binary }

```python
from sqlalchemy import BINARY
```

নির্দিষ্ট দৈর্ঘ্যের বাইনারি `BINARY(n)` (MySQL/SQL Server)।

**উদাহরণ:**

```python
print(BINARY(16).compile(dialect=mysql.dialect()))   # BINARY(16)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](#largebinary-summary)-এর মতো।

## `VARBINARY` { #varbinary }

```python
from sqlalchemy import VARBINARY
```

পরিবর্তনশীল দৈর্ঘ্যের বাইনারি `VARBINARY(n)`।

**উদাহরণ:**

```python
print(VARBINARY(64).compile(dialect=mysql.dialect()))   # VARBINARY(64)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](#largebinary-summary)-এর মতো।

## `BLOB` { #blob }

```python
from sqlalchemy import BLOB
```

ঠিক `BLOB`।

**উদাহরণ:**

```python
print(BLOB().compile(dialect=mysql.dialect()))   # BLOB
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](#largebinary-summary)-এর মতো।

## `UUID` { #uuid }

```python
from sqlalchemy import UUID
```

(২.০) ঠিক native `UUID` টাইপ (native সমর্থন না থাকলে এরর); generic `Uuid`-এর মতো fallback নেই।

**উদাহরণ:**

```python
print(pgt(UUID()), type(rt(UUID(), uuid.uuid4())).__name__)   # UUID UUID
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #uuid-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_emulated_to_native()`](#uuid-adapt-emulated-to-native) | ক্লাস মেথড (internal) | emulated রূপ থেকে native UUID-তে রূপান্তর (ডায়ালেক্টের ভেতরের কাজ)। |
| [`adapt_native_to_emulated()`](#uuid-adapt-native-to-emulated) | ক্লাস মেথড (internal) | native UUID থেকে emulated রূপে রূপান্তর। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `UUID`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](#typeengine-Comparator) · [`adapt()`](#typeengine-adapt) · [`as_generic()`](#typeengine-as-generic) · [`bind_expression()`](#typeengine-bind-expression) · [`bind_processor()`](#typeengine-bind-processor) · [`coerce_compared_value()`](#typeengine-coerce-compared-value) · [`column_expression()`](#typeengine-column-expression) · [`comparator_factory`](#typeengine-comparator-factory) · [`compare_values()`](#typeengine-compare-values) · [`compile()`](#typeengine-compile) · [`copy()`](#typeengine-copy) · [`copy_value()`](#typeengine-copy-value) · [`dialect_impl()`](#typeengine-dialect-impl) · [`evaluates_none()`](#typeengine-evaluates-none) · [`get_dbapi_type()`](#typeengine-get-dbapi-type) · [`hashable`](#typeengine-hashable) · [`literal_processor()`](#typeengine-literal-processor) · [`operator_classes`](#typeengine-operator-classes) · [`python_type`](#typeengine-python-type) · [`render_bind_cast`](#typeengine-render-bind-cast) · [`render_literal_cast`](#typeengine-render-literal-cast) · [`repr_struct()`](#typeengine-repr-struct) · [`result_processor()`](#typeengine-result-processor) · [`should_evaluate_none`](#typeengine-should-evaluate-none) · [`sort_key_function`](#typeengine-sort-key-function) · [`with_variant()`](#typeengine-with-variant)

**`Boolean` থেকে:** [`adapt_to_emulated()`](#boolean-adapt-to-emulated) · [`native`](#boolean-native)

**`String` থেকে:** [`collation`](#string-collation) · [`collation_schema`](#string-collation-schema) · [`length`](#string-length)

///

### `UUID.adapt_emulated_to_native()` { #uuid-adapt-emulated-to-native }

```python
UUID.adapt_emulated_to_native(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

emulated রূপ থেকে native UUID-তে রূপান্তর (ডায়ালেক্টের ভেতরের কাজ)।

### `UUID.adapt_native_to_emulated()` { #uuid-adapt-native-to-emulated }

```python
UUID.adapt_native_to_emulated(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

native UUID থেকে emulated রূপে রূপান্তর।

/// check | সংক্ষেপে মনে রাখুন

* টাকা: `Numeric(12, 2)` (কখনো `Float` নয়)। সময়: `DateTime(timezone=True)`। আইডি: `BigInteger` বা `Uuid`।
* PostgreSQL ENUM টাইপকে নাম দিন (`Enum(MyEnum, name="my_enum")`); মান বদলাতে Alembic-এ আলাদা মাইগ্রেশন লাগে।
* JSON-এর ভেতরের মানে তুলনা: `col["key"].as_string()` / `.as_integer()`।
* ডেটাবেস-ভেদে ভিন্ন টাইপ: `JSON().with_variant(JSONB(), "postgresql")`।
* `None` → NULL না ডিফল্ট? `evaluates_none()` / `JSON(none_as_null=True)` দিয়ে নিয়ন্ত্রণ।

///
