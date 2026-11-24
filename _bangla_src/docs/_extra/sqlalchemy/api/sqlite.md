# SQLite API: upsert, তারিখ-সময়ের স্টোরেজ, JSON ও JSONB { #api-sqlite }

/// note | এই পেজে যা আছে

`sqlalchemy.dialects.sqlite`-এর সব পাবলিক API:

* **Upsert:** `insert()` আর `Insert`-এর `on_conflict_do_update()`, `on_conflict_do_nothing()`, `excluded` (SQLite ৩.২৪+)।
* **তারিখ-সময়:** `DATETIME`, `DATE`, `TIME`: SQLite-এ আলাদা তারিখ টাইপ নেই, তাই কীভাবে **স্ট্রিং হিসেবে** জমা হবে তা এরাই ঠিক করে।
* **JSON** আর ২.১-এর নতুন **JSONB** (SQLite ৩.৪৫+-এর বাইনারি JSON)।
* `dialect` আর সাধারণ টাইপের তালিকা পেজের শেষে।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
engine = create_engine("sqlite://")      # মেমোরিতে, প্রতিটি উদাহরণে নতুন
m = MetaData()
products = Table("products", m,
                 Column("id", Integer, primary_key=True),
                 Column("sku", String, unique=True),
                 Column("name", String),
                 Column("stock", Integer))
```

ডেটা: `P1` "লাল কলম" (stock ১০)। `rows(stmt)`: ফলের রোগুলো tuple হিসেবে। `raw(sql)`: ডেটাবেসে আসলে কী জমা আছে (SQLAlchemy-র রূপান্তর ছাড়া)। Python-এর সাথে আসা SQLite ৩.৫৩-এ চালিয়ে দেখা।

///

## Upsert (INSERT ... ON CONFLICT) { #insert-fn-group }

## `insert()` { #insert-fn }

```python
from sqlalchemy.dialects.sqlite import insert
```

```python
insert(table)
```

**ধরন:** ফাংশন

SQLite-এর `INSERT` বানায়: সাধারণ `insert()`-এর সব কিছু, সাথে `ON CONFLICT` (upsert, SQLite ৩.২৪+)। **সাধারণ `sqlalchemy.insert` নয়, এটা ইমপোর্ট করুন।** ব্যবহার PostgreSQL-এর `insert()`-এর প্রায় হুবহু (শুধু `constraint=` নাম দিয়ে কনফ্লিক্ট বলা যায় না)।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="লাল কলম", stock=3)
run(stmt.on_conflict_do_update(index_elements=[products.c.sku], set_={"stock": products.c.stock + stmt.excluded.stock}))
print(rows(select(products.c.sku, products.c.stock)))   # [('P1', 13)]  (১০ + ৩, নতুন রো নয়)
```

### `insert()`-এর সব প্যারামিটার { #insert-fn-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `table` | টেবিল বা মডেল। |

## `Insert` { #insert }

```python
from sqlalchemy.dialects.sqlite import Insert
```

SQLite `insert()`-এর ফল। সাধারণ `Insert`-এর সব মেথড (`values()`, `returning()` …) আছে (ভাঁজ করা বক্সে [DML পেজের](dml.md) লিংক), সাথে নিচের তিনটি নিজস্ব।

**SQLite-এ `RETURNING`-এর ফল commit-এর আগেই পড়ে ফেলুন।** না পড়ে commit করলে `OperationalError: cannot commit transaction - SQL statements in progress`।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P2", name="খাতা", stock=1).on_conflict_do_nothing().returning(products.c.id)
with engine.begin() as c:
    new_id = c.execute(stmt).scalar()      # transaction-এর ভেতরেই পড়া হলো
print(new_id)   # 2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #insert-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`excluded`](#insert-excluded) | প্রপার্টি | `ON CONFLICT ... DO UPDATE`-এর ভেতরে "যে রো ঢোকাতে চেয়েছিলাম" তার কলাম: `stmt.excluded.name` (SQL-এ `excluded.name`)। |
| [`on_conflict_do_nothing()`](#insert-on-conflict-do-nothing) | মেথড | `ON CONFLICT DO NOTHING`: কনফ্লিক্ট হলে চুপচাপ বাদ। |
| [`on_conflict_do_update()`](#insert-on-conflict-do-update) | মেথড | `ON CONFLICT (...) DO UPDATE SET ...`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Insert`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`apply_syntax_extension_point()`](select.md#select-apply-syntax-extension-point) · [`argument_for()`](select.md#select-argument-for) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`ext()`](select.md#select-ext) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`prefix_with()`](select.md#select-prefix-with) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_hint()`](select.md#select-with-hint)

**`Insert` থেকে:** [`entity_description`](dml.md#insert-entity-description) · [`exported_columns`](dml.md#insert-exported-columns) · [`from_select()`](dml.md#insert-from-select) · [`include_insert_from_select_defaults`](dml.md#insert-include-insert-from-select-defaults) · [`inline()`](dml.md#insert-inline) · [`named_with_column`](dml.md#insert-named-with-column) · [`return_defaults()`](dml.md#insert-return-defaults) · [`returning()`](dml.md#insert-returning) · [`returning_column_descriptions`](dml.md#insert-returning-column-descriptions) · [`select`](dml.md#insert-select) · [`values()`](dml.md#insert-values) · [`with_dialect_options()`](dml.md#insert-with-dialect-options)

///

### `Insert.excluded` { #insert-excluded }

**ধরন:** প্রপার্টি

`ON CONFLICT ... DO UPDATE`-এর ভেতরে "যে রো ঢোকাতে চেয়েছিলাম" তার কলাম: `stmt.excluded.name` (SQL-এ `excluded.name`)।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="লাল কলম (নতুন)", stock=0)
run(stmt.on_conflict_do_update(index_elements=["sku"], set_={"name": stmt.excluded.name}))
print(rows(select(products.c.name, products.c.stock)))   # [('লাল কলম (নতুন)', 10)]
```

### `Insert.on_conflict_do_nothing()` { #insert-on-conflict-do-nothing }

```python
Insert.on_conflict_do_nothing(index_elements=None, index_where=None)
```

**ধরন:** মেথড

`ON CONFLICT DO NOTHING`: কনফ্লিক্ট হলে চুপচাপ বাদ। `index_elements` না দিলে যেকোনো unique/PK কনফ্লিক্টে; দিলে শুধু সেই কলামের কনফ্লিক্টে (partial index হলে সাথে `index_where`)।

**উদাহরণ:**

```python
r = run(insert(products).values([{"sku": "P1", "name": "x"}, {"sku": "P9", "name": "নতুন"}])
        .on_conflict_do_nothing(index_elements=["sku"]))
print(r.rowcount, rows(select(products.c.sku)))   # 1 [('P1',), ('P9',)]
```

### `Insert.on_conflict_do_update()` { #insert-on-conflict-do-update }

```python
Insert.on_conflict_do_update(index_elements=None, index_where=None, set_=None, where=None)
```

**ধরন:** মেথড

`ON CONFLICT (...) DO UPDATE SET ...`। কনফ্লিক্টের কলাম `index_elements` (বাধ্যতামূলক), partial index হলে `index_where`, নতুন মান `set_` (dict বা কলাম অবজেক্ট-key), শর্তসাপেক্ষ আপডেটে `where`।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="লাল কলম", stock=1)
stmt = stmt.on_conflict_do_update(index_elements=["sku"], set_={"stock": stmt.excluded.stock},
                                  where=products.c.stock < 5)
print(stmt.compile(dialect=sqlite.dialect()))
# INSERT INTO products (sku, name, stock) VALUES (?, ?, ?) ON CONFLICT (sku) DO UPDATE SET stock = excluded.stock WHERE products.stock < ?
run(stmt)
print(rows(select(products.c.stock)))   # [(10,)]  (stock ১০, শর্ত মেলেনি, তাই বদলায়নি)
```

## তারিখ-সময়ের টাইপ { #datetime-group }

## `DATETIME` { #datetime }

```python
from sqlalchemy.dialects.sqlite import DATETIME
```

SQLite-এ `datetime` জমা হয় **স্ট্রিং** হিসেবে, ডিফল্ট রূপ `2025-03-09 14:30:00.000000`। পড়ার সময় SQLAlchemy আবার `datetime` বানায় (ডিফল্টে `datetime.fromisoformat()` দিয়ে)। সাধারণ `DateTime` SQLite-এ এটাই হয়; সরাসরি নিলে স্টোরেজের রূপ বদলানো যায়।

**সাবধান:** টাইমজোন জমা হয় না। ISO রূপের স্ট্রিং হিসেবে সাজালে সময়ের ক্রমেই সাজে, তাই রূপ বদলালেও বছর-মাস-দিন ক্রম রাখুন।

**উদাহরণ:**

```python
print(rt(DateTime(), datetime.datetime(2025, 3, 9, 14, 30)), raw("SELECT v FROM rt"))
# 2025-03-09 14:30:00 [('2025-03-09 14:30:00.000000',)]
```

**নিজের স্টোরেজ রূপ (storage_format + regexp)**

```python
compact = DATETIME(storage_format="%(year)04d%(month)02d%(day)02d%(hour)02d%(minute)02d",
                   regexp=r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})")
print(rt(compact, datetime.datetime(2025, 3, 9, 14, 30)), raw("SELECT v FROM rt"))
# 2025-03-09 14:30:00 [('202503091430',)]
```

**মাইক্রোসেকেন্ড বাদ (truncate_microseconds)**

```python
print(rt(DATETIME(truncate_microseconds=True), datetime.datetime(2025, 3, 9, 14, 30, 5, 123456)))
# 2025-03-09 14:30:05
```

### কনস্ট্রাক্টরের প্যারামিটার { #datetime-params }

```python
DATETIME(*args, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | সাধারণ `DateTime`-এর অবস্থানগত আর্গুমেন্ট (`timezone`)। |
| `kwargs` | • `storage_format`: ফরম্যাট স্ট্রিং, `year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond` key-সহ dict-এ প্রয়োগ হয়।<br>• `regexp`: পড়ার সময় স্ট্রিং ভাঙার রেগুলার এক্সপ্রেশন। **নামযুক্ত group** (`(?P<year>\d+)`) হলে নাম ধরে, নইলে **ক্রম ধরে** (বছর, মাস, দিন, ঘণ্টা …) `datetime()`-এ যায়।<br>• `truncate_microseconds=True`: মাইক্রোসেকেন্ড ফেলে দেয় (`storage_format`/`regexp`-এর সাথে একসাথে দেওয়া যায় না)।<br>• `timezone`: সাধারণ `DateTime`-এর মতো (SQLite-এ জমা হয় না)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #datetime-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`format_is_text_affinity`](#datetime-format-is-text-affinity) | প্রপার্টি | স্টোরেজ রূপটি SQLite-এর **TEXT affinity** পায় কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DATETIME`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `DATETIME.format_is_text_affinity` { #datetime-format-is-text-affinity }

**ধরন:** প্রপার্টি

স্টোরেজ রূপটি SQLite-এর **TEXT affinity** পায় কি না। ডিফল্টে `True`। শুধু অঙ্ক দিয়ে রূপ বানালে (যেমন `20250309143000`) `False`: তখন `CREATE TABLE`-এ SQLAlchemy কলামের টাইপ `DATETIME_CHAR` লেখে, যাতে SQLite মানটিকে সংখ্যায় না বদলায়।

**উদাহরণ:**

```python
digits = DATETIME(storage_format="%(year)04d%(month)02d%(day)02d%(hour)02d%(minute)02d%(second)02d",
                  regexp=r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})")
print(DATETIME().format_is_text_affinity, digits.format_is_text_affinity)   # True False
print(digits.compile(dialect=sqlite.dialect()))   # DATETIME_CHAR
```

## `DATE` { #date }

```python
from sqlalchemy.dialects.sqlite import DATE
```

`date`-কে স্ট্রিং হিসেবে রাখে, ডিফল্ট রূপ `2025-03-09`। `DATETIME`-এর মতোই `storage_format` আর `regexp` দিয়ে বদলানো যায়।

**উদাহরণ:**

```python
bn_date = DATE(storage_format="%(day)02d/%(month)02d/%(year)04d",
               regexp=r"(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)")
print(rt(bn_date, datetime.date(2025, 3, 9)), raw("SELECT v FROM rt"))   # 2025-03-09 [('09/03/2025',)]
# সাবধান: dd/mm/yyyy রূপে স্ট্রিং-সাজানো আর তারিখ-সাজানো এক নয়
```

### কনস্ট্রাক্টরের প্যারামিটার { #date-params }

```python
DATE(storage_format=None, regexp=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `storage_format` | ফরম্যাট স্ট্রিং (`year`, `month`, `day` key)। |
| `regexp` | পড়ার রেগুলার এক্সপ্রেশন (নামযুক্ত group হলে নাম ধরে, নইলে বছর-মাস-দিন ক্রমে)। |
| `kw` | বাকি সাধারণ `Date`-এর প্যারামিটার। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #date-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`format_is_text_affinity`](#date-format-is-text-affinity) | প্রপার্টি | `DATETIME.format_is_text_affinity`-এর মতো: শুধু-অঙ্কের রূপে `False`, তখন কলামের টাইপ হয় `DATE_CHAR`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DATE`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `DATE.format_is_text_affinity` { #date-format-is-text-affinity }

**ধরন:** প্রপার্টি

`DATETIME.format_is_text_affinity`-এর মতো: শুধু-অঙ্কের রূপে `False`, তখন কলামের টাইপ হয় `DATE_CHAR`।

**উদাহরণ:**

```python
d = DATE(storage_format="%(year)04d%(month)02d%(day)02d", regexp=r"(\d{4})(\d{2})(\d{2})")
print(d.format_is_text_affinity, d.compile(dialect=sqlite.dialect()))   # False DATE_CHAR
```

## `TIME` { #time }

```python
from sqlalchemy.dialects.sqlite import TIME
```

`time`-কে স্ট্রিং হিসেবে রাখে, ডিফল্ট রূপ `14:30:05.000000`। `storage_format`, `regexp`, `truncate_microseconds` সবই `DATETIME`-এর মতো।

**উদাহরণ:**

```python
print(rt(Time(), datetime.time(14, 30, 5)), raw("SELECT v FROM rt"))   # 14:30:05 [('14:30:05.000000',)]
print(rt(TIME(truncate_microseconds=True), datetime.time(10, 1, 2, 345678)))   # 10:01:02
```

### কনস্ট্রাক্টরের প্যারামিটার { #time-params }

```python
TIME(*args, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | সাধারণ `Time`-এর অবস্থানগত আর্গুমেন্ট। |
| `kwargs` | `storage_format` (key: `hour`, `minute`, `second`, `microsecond`), `regexp`, `truncate_microseconds`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #time-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`format_is_text_affinity`](#time-format-is-text-affinity) | প্রপার্টি | শুধু-অঙ্কের রূপে `False`, তখন কলামের টাইপ হয় `TIME_CHAR`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TIME`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `TIME.format_is_text_affinity` { #time-format-is-text-affinity }

**ধরন:** প্রপার্টি

শুধু-অঙ্কের রূপে `False`, তখন কলামের টাইপ হয় `TIME_CHAR`।

**উদাহরণ:**

```python
t = TIME(storage_format="%(hour)02d%(minute)02d%(second)02d", regexp=r"(\d{2})(\d{2})(\d{2})")
print(t.format_is_text_affinity, t.compile(dialect=sqlite.dialect()))   # False TIME_CHAR
```

## JSON ও JSONB { #json-group }

## `JSON` { #json }

```python
from sqlalchemy.dialects.sqlite import JSON
```

SQLite-এর JSON (JSON1 এক্সটেনশন, আধুনিক SQLite-এ বিল্ট-ইন)। মান জমা হয় **টেক্সট** হিসেবে। সাধারণ `sqlalchemy.JSON` SQLite-এ এটাই হয়। `col["key"]` SQL-এ `JSON_QUOTE(JSON_EXTRACT(col, '$."key"'))`।

**উদাহরণ:**

```python
t = Table("docs", MetaData(), Column("id", Integer, primary_key=True), Column("data", JSON))
t.create(engine)
run(sa_insert(t).values(data={"name": "রহিম", "age": 30}))
print(rows(select(t.c.data["name"].as_string(), t.c.data["age"].as_integer())))   # [('রহিম', 30)]
print(raw("SELECT typeof(data) FROM docs"))   # [('text',)]
```

### কনস্ট্রাক্টরের প্যারামিটার { #json-params }

```python
JSON(none_as_null=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `True` দিলে Python `None` SQL `NULL` হিসেবে যায় (ডিফল্টে JSON `null`)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`JSON`](types.md#json-summary)-এর মতো।

## `JSONB` { #jsonb }

```python
from sqlalchemy.dialects.sqlite import JSONB
```

(২.১-এ নতুন) SQLite ৩.৪৫+-এর **বাইনারি JSONB** রূপে জমা রাখে: জায়গা কম, পড়া দ্রুত। লেখার সময় `jsonb()` আর পড়ার সময় `json()` SQL ফাংশন নিজে থেকে বসে, তাই Python দিক থেকে `JSON`-এর মতোই কাজ করে (dict দিন, dict পান)।

**উদাহরণ:**

```python
t = Table("docs", MetaData(), Column("id", Integer, primary_key=True), Column("data", JSONB))
t.create(engine)
run(sa_insert(t).values(data={"tags": ["a", "b"]}))
print(rows(select(t.c.data)), raw("SELECT typeof(data) FROM docs"))   # [({'tags': ['a', 'b']},)] [('blob',)]
```

### কনস্ট্রাক্টরের প্যারামিটার { #jsonb-params }

```python
JSONB(none_as_null=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `JSON`-এর মতো। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`JSON`](types.md#json-summary)-এর মতো।

## ডায়ালেক্ট { #dialect-group }

## `dialect` { #dialect }

```python
from sqlalchemy.dialects.sqlite import dialect
```

SQLite-এর ডিফল্ট ডায়ালেক্ট ক্লাস (Python-এর বিল্ট-ইন `sqlite3`, নাম `pysqlite`)। SQL কম্পাইল করে দেখতে `stmt.compile(dialect=sqlite.dialect())`। সদস্যগুলো SQLAlchemy-র ভেতরের ডায়ালেক্ট-ইন্টারফেস, তাই আলাদা তালিকা দেওয়া হয়নি।

সংযোগ: `sqlite:///app.db` (ফাইল), `sqlite://` (মেমোরি), async হলে `sqlite+aiosqlite:///app.db`। `create_engine(..., native_datetime=True)` দিলে `sqlite3`-এর নিজের `PARSE_DECLTYPES` রূপান্তর ব্যবহার হয় (সাধারণত দরকার নেই)। FastAPI-র মতো একাধিক থ্রেডে ফাইল-ডেটাবেস ব্যবহারে `connect_args={"check_same_thread": False}` লাগে।

**উদাহরণ:**

```python
d = dialect()
print(d.name, d.driver, d.paramstyle)   # sqlite pysqlite qmark
```

## সাধারণ টাইপ, SQLite মডিউল থেকে { #generic-reexports }

নিচের নামগুলো `from sqlalchemy.dialects.sqlite import ...` দিয়েও পাওয়া যায়, কিন্তু এগুলো **হুবহু একই** সাধারণ টাইপ; ব্যাখ্যা [টাইপ পেজে](types.md):

| নাম | কোথায় দেখবেন |
| :--- | :--- |
| `INTEGER`, `SMALLINT` | [`INTEGER`](types.md#sql-integer), [`SMALLINT`](types.md#smallint) |
| `VARCHAR`, `CHAR`, `TEXT` | [`VARCHAR`](types.md#varchar), [`CHAR`](types.md#char), [`TEXT`](types.md#sql-text) |
| `NUMERIC`, `DECIMAL`, `FLOAT`, `REAL` | [`NUMERIC`](types.md#sql-numeric), [`DECIMAL`](types.md#decimal), [`FLOAT`](types.md#sql-float), [`REAL`](types.md#real) |
| `BOOLEAN`, `BLOB`, `TIMESTAMP` | [`BOOLEAN`](types.md#sql-boolean), [`BLOB`](types.md#blob), [`TIMESTAMP`](types.md#timestamp) |

/// check | সংক্ষেপে মনে রাখুন

* upsert: `from sqlalchemy.dialects.sqlite import insert` → `.on_conflict_do_update(index_elements=[...], set_={... stmt.excluded.col})`।
* তারিখ-সময় SQLite-এ স্ট্রিং; রূপ বদলাতে `DATETIME(storage_format=..., regexp=...)`, ক্রম ঠিক রাখতে বছর আগে।
* বড় JSON ডেটায় `JSONB` (২.১, SQLite ৩.৪৫+)।

///
