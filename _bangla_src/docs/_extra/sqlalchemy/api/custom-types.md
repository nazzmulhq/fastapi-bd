# কাস্টম টাইপ API: TypeDecorator, UserDefinedType, Comparator { #api-custom-types }

/// note | এই পেজে যা আছে

* `TypeDecorator`: বিদ্যমান টাইপের ওপর নিজের রূপান্তর-নিয়ম (এনক্রিপ্ট করা স্ট্রিং, টাকার অঙ্ক পয়সায়, timezone-aware সময়, কমা-বিভক্ত তালিকা …); **সব** সদস্য।
* `UserDefinedType`: সম্পূর্ণ নতুন ডেটাবেস টাইপ (যেমন PostGIS `GEOMETRY`), আর `ExternalType`।
* `TypeEngine.Comparator`: টাইপে নিজের অপারেটর যোগ করা।
* `Variant` (পুরোনো); এর বদলে `with_variant()`।

///

কখন কোনটা: ডেটাবেসে আগে থেকে থাকা টাইপেই মান রাখবেন, শুধু Python দিকে রূপান্তর চাই → **`TypeDecorator`** (৯৫% ক্ষেত্রে এটাই)। ডেটাবেসের এমন টাইপ যা SQLAlchemy চেনে না → **`UserDefinedType`**। টাইপের কলামে নতুন অপারেটর (`col.distance_to(...)`) → **`Comparator`**। সব built-in টাইপ আর `TypeEngine`-এর মেথডগুলো আছে [কলাম টাইপ পেজে](types.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

`rt(টাইপ, মান)` একটি অস্থায়ী টেবিলে মানটি লিখে আবার পড়ে ফেরত দেয় (round-trip); `raw(টাইপ, মান)` দেখায় ডেটাবেসে আসলে কী জমা হয়েছে। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `TypeDecorator` { #typedecorator }

```python
from sqlalchemy.types import TypeDecorator
```

একটি বিদ্যমান টাইপকে (`impl`) মুড়িয়ে নিজের রূপান্তর যোগ করার ক্লাস। ন্যূনতম তিনটি জিনিস লাগে: `impl` (ডেটাবেসে আসল টাইপ), `cache_ok = True` (ক্যাশে নিরাপদ), আর `process_bind_param()` (Python → ডেটাবেস) ও/বা `process_result_value()` (ডেটাবেস → Python)। মডেলে সাধারণ টাইপের মতোই ব্যবহার: `mapped_column(Cents)`।

**উদাহরণ:**

```python
# উপরের সেটআপের Cents: ১২.৫০ টাকা → ডেটাবেসে 1250
print(raw(Cents, Decimal("12.50")), rt(Cents, Decimal("12.50")))   # 1250 12.5
```

**আরেকটি প্রচলিত উদাহরণ: সবসময় UTC-তে timezone-aware সময়**

```python
class UTCDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True
    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            raise ValueError("naive datetime দেওয়া যাবে না")
        return value
    def process_result_value(self, value, dialect):
        return value.astimezone(datetime.timezone.utc) if value else value

v = rt(UTCDateTime, datetime.datetime(2024, 1, 1, 18, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=6))))
print(v)   # 2024-01-01 12:00:00+00:00
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typedecorator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`TDComparatorContainer`](#typedecorator-TDComparatorContainer) | অ্যাট্রিবিউট (internal) | ভেতরের সহায়ক ক্লাস: `impl`-এর comparator থেকে on-the-fly comparator ক্লাস বানিয়ে ক্যাশ রাখে (pickle-যোগ্যতা বজায় রেখে)। |
| [`bind_expression()`](#typedecorator-bind-expression) | মেথড | (override করার জন্য) INSERT/WHERE-এ প্যারামিটারকে একটি **SQL ফাংশনে** মোড়াতে চাইলে: যেমন ডেটাবেসেই এনক্রিপ্ট `pgp_sym_encrypt(:param, key)`। |
| [`cache_ok`](#typedecorator-cache-ok) | অ্যাট্রিবিউট | **অবশ্যই `True` দিন** যদি টাইপের অবস্থা (কনস্ট্রাক্টরের আর্গুমেন্ট) hashable হয়; তাহলে এই টাইপের স্টেটমেন্ট ক্যাশ হয়। |
| [`coerce_compared_value()`](#typedecorator-coerce-compared-value) | মেথড | `col == মান` লিখলে ডান দিকের Python মানটি কোন টাইপে ধরা হবে। |
| [`coerce_to_is_types`](#typedecorator-coerce-to-is-types) | অ্যাট্রিবিউট | যেসব Python মানের সাথে `==` তুলনায় SQL-এ `=`-এর বদলে `IS` বসবে (ডিফল্ট `(type(None),)`, মানে `col == None` → `IS NULL`)। |
| [`column_expression()`](#typedecorator-column-expression) | মেথড | (override করার জন্য) SELECT-এ কলামটিকে একটি SQL ফাংশনে মুড়িয়ে পড়ে, যেমন `pgp_sym_decrypt(col, key)` বা `ST_AsText(geom)`। |
| [`comparator_factory`](#typedecorator-comparator-factory) | প্রপার্টি | এই টাইপের কলামের অপারেটরগুলো যে `Comparator` ক্লাস থেকে আসে। |
| [`impl`](#typedecorator-impl) | অ্যাট্রিবিউট | (ক্লাস অ্যাট্রিবিউট) মোড়ানো আসল টাইপ: ক্লাস (`Integer`) বা অবজেক্ট (`String(50)`)। |
| [`impl_instance`](#typedecorator-impl-instance) | প্রপার্টি | `impl`-এর একটি অবজেক্ট (ক্লাস দেওয়া থাকলেও)। |
| [`load_dialect_impl()`](#typedecorator-load-dialect-impl) | মেথড | (override করার জন্য) ডেটাবেস-ভেদে ভিন্ন আসল টাইপ বেছে নিতে: যেমন PostgreSQL-এ native `UUID`, অন্য জায়গায় `CHAR(32)`। |
| [`process_bind_param()`](#typedecorator-process-bind-param) | মেথড | (override করার জন্য) Python মান → ডেটাবেসে পাঠানোর মান। |
| [`process_literal_param()`](#typedecorator-process-literal-param) | মেথড | (override করার জন্য) মান যখন প্যারামিটার না হয়ে SQL-এ সরাসরি বসে (`literal_binds`, কিছু DDL ডিফল্ট), তখনকার রূপান্তর। |
| [`process_result_value()`](#typedecorator-process-result-value) | মেথড | (override করার জন্য) ডেটাবেস থেকে আসা মান → Python মান। |
| [`type_engine()`](#typedecorator-type-engine) | মেথড | একটি ডায়ালেক্টের জন্য আসলে যে টাইপ অবজেক্ট ব্যবহার হবে (`load_dialect_impl()`-এর ফল)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TypeDecorator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `TypeDecorator.TDComparatorContainer` { #typedecorator-TDComparatorContainer }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের সহায়ক ক্লাস: `impl`-এর comparator থেকে on-the-fly comparator ক্লাস বানিয়ে ক্যাশ রাখে (pickle-যোগ্যতা বজায় রেখে)।

### `TypeDecorator.bind_expression()` { #typedecorator-bind-expression }

```python
TypeDecorator.bind_expression(bindparam)
```

**ধরন:** মেথড

(override করার জন্য) INSERT/WHERE-এ প্যারামিটারকে একটি **SQL ফাংশনে** মোড়াতে চাইলে: যেমন ডেটাবেসেই এনক্রিপ্ট `pgp_sym_encrypt(:param, key)`। Python-এ রূপান্তর হলে `process_bind_param()` যথেষ্ট।

**উদাহরণ:**

```python
class LowerStr(TypeDecorator):
    impl = String
    cache_ok = True
    def bind_expression(self, bindvalue):
        return func.lower(bindvalue)

print(rt(LowerStr, "HeLLo"))   # hello  (ডেটাবেসের lower() চালিয়ে জমা হয়েছে)
```

### `TypeDecorator.cache_ok` { #typedecorator-cache-ok }

**ধরন:** অ্যাট্রিবিউট

**অবশ্যই `True` দিন** যদি টাইপের অবস্থা (কনস্ট্রাক্টরের আর্গুমেন্ট) hashable হয়; তাহলে এই টাইপের স্টেটমেন্ট ক্যাশ হয়। না দিলে (`None`) SQLAlchemy সতর্কবার্তা দেয় আর ক্যাশিং বন্ধ রাখে (ধীর)। অবস্থা mutable (যেমন dict) হলে `False`।

**উদাহরণ:**

```python
print(Cents.cache_ok)   # True
```

### `TypeDecorator.coerce_compared_value()` { #typedecorator-coerce-compared-value }

```python
TypeDecorator.coerce_compared_value(op, value)
```

**ধরন:** মেথড

`col == মান` লিখলে ডান দিকের Python মানটি কোন টাইপে ধরা হবে। TypeDecorator-এ ডিফল্টে নিজের টাইপ (তাই তুলনার মানও `process_bind_param` দিয়ে যায়)। `col + 5`-এর মতো ক্ষেত্রে ভিন্ন টাইপ চাইলে override করুন।

**উদাহরণ:**

```python
expr = Column("price", Cents) > Decimal("10.00")
print(type(expr.right.type).__name__)   # Cents  (তাই 10.00 → 1000 হিসেবে তুলনা হবে)
```

### `TypeDecorator.coerce_to_is_types` { #typedecorator-coerce-to-is-types }

**ধরন:** অ্যাট্রিবিউট

যেসব Python মানের সাথে `==` তুলনায় SQL-এ `=`-এর বদলে `IS` বসবে (ডিফল্ট `(type(None),)`, মানে `col == None` → `IS NULL`)। `None`-কেও `process_bind_param`-এ পাঠাতে চাইলে খালি tuple দিন।

**উদাহরণ:**

```python
print(Cents.coerce_to_is_types)   # (<class 'NoneType'>,)
```

### `TypeDecorator.column_expression()` { #typedecorator-column-expression }

```python
TypeDecorator.column_expression(column)
```

**ধরন:** মেথড

(override করার জন্য) SELECT-এ কলামটিকে একটি SQL ফাংশনে মুড়িয়ে পড়ে, যেমন `pgp_sym_decrypt(col, key)` বা `ST_AsText(geom)`।

**উদাহরণ:**

```python
class UpperRead(TypeDecorator):
    impl = String
    cache_ok = True
    def column_expression(self, col):
        return func.upper(col)

print(rt(UpperRead, "dhaka"))   # DHAKA  (জমা আছে ছোট হাতে, পড়ার সময় upper())
```

### `TypeDecorator.comparator_factory` { #typedecorator-comparator-factory }

**ধরন:** প্রপার্টি

এই টাইপের কলামের অপারেটরগুলো যে `Comparator` ক্লাস থেকে আসে। TypeDecorator-এ ডিফল্টে `impl`-এর comparator (তাই `String`-ভিত্তিক টাইপে `like()` ইত্যাদি চলে)। নিজের অপারেটর যোগ করতে override করুন (নিচে `TypeEngine.Comparator` দেখুন)।

**উদাহরণ:**

```python
print(Column("x", Cents).comparator.__class__.__mro__[1].__name__)   # Comparator
```

### `TypeDecorator.impl` { #typedecorator-impl }

**ধরন:** অ্যাট্রিবিউট

(ক্লাস অ্যাট্রিবিউট) মোড়ানো আসল টাইপ: ক্লাস (`Integer`) বা অবজেক্ট (`String(50)`)। TypeDecorator-এর কনস্ট্রাক্টরের আর্গুমেন্ট এই `impl`-এর কনস্ট্রাক্টরে যায়: `MyType(50)` → `String(50)`।

**উদাহরণ:**

```python
class Email(TypeDecorator):
    impl = String
    cache_ok = True

print(Email(120).impl)   # VARCHAR(120)
```

### `TypeDecorator.impl_instance` { #typedecorator-impl-instance }

**ধরন:** প্রপার্টি

`impl`-এর একটি অবজেক্ট (ক্লাস দেওয়া থাকলেও)।

**উদাহরণ:**

```python
print(type(Cents().impl_instance).__name__)   # Integer
```

### `TypeDecorator.load_dialect_impl()` { #typedecorator-load-dialect-impl }

```python
TypeDecorator.load_dialect_impl(dialect)
```

**ধরন:** মেথড

(override করার জন্য) ডেটাবেস-ভেদে ভিন্ন আসল টাইপ বেছে নিতে: যেমন PostgreSQL-এ native `UUID`, অন্য জায়গায় `CHAR(32)`।

**উদাহরণ:**

```python
class GUID(TypeDecorator):
    impl = String(36)
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        return dialect.type_descriptor(String(36))

print(type(GUID().load_dialect_impl(postgresql.dialect())).__name__,
      type(GUID().load_dialect_impl(sqlite.dialect())).__name__)   # PGUuid String  (PostgreSQL ডায়ালেক্টের UUID রূপ)
```

### `TypeDecorator.process_bind_param()` { #typedecorator-process-bind-param }

```python
TypeDecorator.process_bind_param(value, dialect)
```

**ধরন:** মেথড

(override করার জন্য) Python মান → ডেটাবেসে পাঠানোর মান। INSERT, UPDATE আর WHERE-এর তুলনা, সব জায়গায় চলে। `None` আসতে পারে, সেটা সামলান।

**উদাহরণ:**

```python
class CSVList(TypeDecorator):
    impl = Text
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return None if value is None else ",".join(value)
    def process_result_value(self, value, dialect):
        return None if value is None else value.split(",")

print(raw(CSVList, ["a", "b"]), rt(CSVList, ["a", "b"]))   # a,b ['a', 'b']
```

### `TypeDecorator.process_literal_param()` { #typedecorator-process-literal-param }

```python
TypeDecorator.process_literal_param(value, dialect)
```

**ধরন:** মেথড

(override করার জন্য) মান যখন প্যারামিটার না হয়ে SQL-এ সরাসরি বসে (`literal_binds`, কিছু DDL ডিফল্ট), তখনকার রূপান্তর।

**উদাহরণ:**

```python
class Cents2(Cents):
    cache_ok = True
    def process_literal_param(self, value, dialect):
        return str(int(Decimal(value) * 100))

stmt = select(literal(Decimal("3.50"), Cents2()))
print(stmt.compile(compile_kwargs={"literal_binds": True}))   # SELECT 350 AS anon_1
```

### `TypeDecorator.process_result_value()` { #typedecorator-process-result-value }

```python
TypeDecorator.process_result_value(value, dialect)
```

**ধরন:** মেথড

(override করার জন্য) ডেটাবেস থেকে আসা মান → Python মান।

**উদাহরণ:**

```python
print(type(rt(Cents, Decimal("1.99"))).__name__)   # Decimal
```

### `TypeDecorator.type_engine()` { #typedecorator-type-engine }

```python
TypeDecorator.type_engine(dialect)
```

**ধরন:** মেথড

একটি ডায়ালেক্টের জন্য আসলে যে টাইপ অবজেক্ট ব্যবহার হবে (`load_dialect_impl()`-এর ফল)।

**উদাহরণ:**

```python
print(Cents().type_engine(postgresql.dialect()))   # INTEGER
```

## `UserDefinedType` { #userdefinedtype }

```python
from sqlalchemy.types import UserDefinedType
```

SQLAlchemy যে টাইপ চেনে না এমন ডেটাবেস টাইপ বানাতে (যেমন PostGIS `GEOMETRY`, PostgreSQL `CITEXT`, `LTREE`)। ন্যূনতম `get_col_spec()` (DDL-এ টাইপের নাম) আর `cache_ok = True`; দরকারে `bind_processor()` / `result_processor()` / `bind_expression()`।

**উদাহরণ:**

```python
class CIText(UserDefinedType):
    cache_ok = True
    def get_col_spec(self, **kw):
        return "CITEXT"

with engine.begin() as conn:
    conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS citext")
m = MetaData()
t = Table("tags", m, Column("id", Integer, primary_key=True), Column("name", CIText()))
m.create_all(engine)
with engine.begin() as conn:
    conn.execute(insert(t).values(name="Python"))
    print(conn.execute(select(t.c.id).where(t.c.name == "PYTHON")).scalar())   # 1  (case-insensitive মিল)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #userdefinedtype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache_ok`](#userdefinedtype-cache-ok) | অ্যাট্রিবিউট | `TypeDecorator.cache_ok`-এর মতো: অবস্থা hashable হলে `True` দিন। |
| [`ensure_kwarg`](#userdefinedtype-ensure-kwarg) | অ্যাট্রিবিউট (internal) | কোন মেথডগুলো (`get_col_spec`) `**kw` নিতে বাধ্য, তার regex-নাম; পুরোনো সিগনেচারের মেথড থাকলে SQLAlchemy নিজে মোড়ায়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `UserDefinedType`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `UserDefinedType.cache_ok` { #userdefinedtype-cache-ok }

**ধরন:** অ্যাট্রিবিউট

`TypeDecorator.cache_ok`-এর মতো: অবস্থা hashable হলে `True` দিন।

**উদাহরণ:**

```python
print(UserDefinedType.cache_ok)   # None
```

### `UserDefinedType.ensure_kwarg` { #userdefinedtype-ensure-kwarg }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন মেথডগুলো (`get_col_spec`) `**kw` নিতে বাধ্য, তার regex-নাম; পুরোনো সিগনেচারের মেথড থাকলে SQLAlchemy নিজে মোড়ায়।

## `ExternalType` { #externaltype }

```python
from sqlalchemy.types import ExternalType
```

থার্ড-পার্টি/নিজের টাইপের (`TypeDecorator`, `UserDefinedType`) মিক্সিন, যার কাজ `cache_ok` ফ্ল্যাগ যোগ করা।

**উদাহরণ:**

```python
print(issubclass(TypeDecorator, ExternalType), issubclass(UserDefinedType, ExternalType))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #externaltype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache_ok`](#externaltype-cache-ok) | অ্যাট্রিবিউট | এই টাইপ ক্যাশে নিরাপদ কি না (`True`/`False`/`None`); বিস্তারিত `TypeDecorator.cache_ok`-এ। |

### `ExternalType.cache_ok` { #externaltype-cache-ok }

**ধরন:** অ্যাট্রিবিউট

এই টাইপ ক্যাশে নিরাপদ কি না (`True`/`False`/`None`); বিস্তারিত `TypeDecorator.cache_ok`-এ।

**উদাহরণ:**

```python
print(ExternalType.cache_ok)   # None
```

## `TypeEngine.Comparator` { #typeengine-comparator }

```python
from sqlalchemy.types import TypeEngine
```

একটি টাইপের কলামে কোন অপারেটর কীভাবে কাজ করবে তার ক্লাস। সাবক্লাস করে **নতুন মেথড-অপারেটর** যোগ করা যায়, তারপর টাইপের `comparator_factory`-তে বসান। কলামের সব সাধারণ অপারেটর (`==`, `like()` …) এখানে আছে, তাই সেগুলো ভাঁজ করা বক্সে [কলাম অপারেটর পেজের](operators.md) লিংকসহ।

**উদাহরণ:**

```python
class Dist(TypeDecorator):
    impl = Integer
    cache_ok = True
    class comparator_factory(Integer.Comparator):
        def near(self, other, within=5):
            return func.abs(self.expr - other) <= within

c = Column("km", Dist)
print(c.near(100))   # abs(km - :km_1) <= :abs_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typeengine-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`expr`](#typeengine-comparator-expr) | অ্যাট্রিবিউট | যে কলাম/এক্সপ্রেশনের ওপর অপারেটর ডাকা হয়েছে (নিজের মেথডে বাম দিক হিসেবে ব্যবহার করুন)। |
| [`type`](#typeengine-comparator-type) | অ্যাট্রিবিউট | সেই এক্সপ্রেশনের টাইপ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TypeEngine.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `TypeEngine.Comparator.expr` { #typeengine-comparator-expr }

**ধরন:** অ্যাট্রিবিউট

যে কলাম/এক্সপ্রেশনের ওপর অপারেটর ডাকা হয়েছে (নিজের মেথডে বাম দিক হিসেবে ব্যবহার করুন)।

**উদাহরণ:**

```python
print(Column("km", Integer).comparator.expr)   # km
```

### `TypeEngine.Comparator.type` { #typeengine-comparator-type }

**ধরন:** অ্যাট্রিবিউট

সেই এক্সপ্রেশনের টাইপ।

**উদাহরণ:**

```python
print(Column("km", Integer).comparator.type)   # INTEGER
```

## `Variant` { #variant }

```python
from sqlalchemy.types import Variant
```

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

পুরোনো (১.৪) API; এখন শুধু পুরোনো কোড চালু রাখতে আছে। ডেটাবেস-ভেদে ভিন্ন টাইপ চাইলে `String().with_variant(postgresql.CITEXT(), "postgresql")` লিখুন (ব্যাখ্যা [`TypeEngine.with_variant()`](types.md#typeengine-with-variant)-এ)।

**উদাহরণ:**

```python
t = String(50).with_variant(Text(), "postgresql")
print(t.compile(dialect=postgresql.dialect()), t.compile(dialect=sqlite.dialect()))   # TEXT VARCHAR(50)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeDecorator`](#typedecorator-summary)-এর মতো।

/// check | সংক্ষেপে মনে রাখুন

* নিজের রূপান্তর: `TypeDecorator` + `impl` + `cache_ok = True` + `process_bind_param` / `process_result_value`।
* ডেটাবেসের ভেতরেই রূপান্তর (SQL ফাংশন): `bind_expression` / `column_expression`।
* ডেটাবেস-ভেদে আসল টাইপ: `load_dialect_impl()` বা `with_variant()`।
* অচেনা ডেটাবেস টাইপ: `UserDefinedType` + `get_col_spec()`।
* নতুন অপারেটর: `comparator_factory` = নিজের `Comparator` সাবক্লাস।

///
