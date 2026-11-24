# PostgreSQL API: upsert, JSONB, ARRAY, HSTORE, ফুল-টেক্সট সার্চ { #api-postgresql }

/// note | এই পেজে যা আছে

`sqlalchemy.dialects.postgresql`-এর কুয়েরি-সংক্রান্ত অংশ:

* **Upsert:** `insert()` আর `Insert`-এর `on_conflict_do_update()`, `on_conflict_do_nothing()`, `excluded`।
* **২.১-এর `distinct_on()`**, `aggregate_order_by`, `array_agg()`, `Any()` / `All()`।
* **JSON / JSONB** (আর তাদের অপারেটর: `has_key()`, `contains()`, `path_exists()` …), `JSONPATH`।
* **ARRAY** আর `array[...]` লিটারাল (অপারেটর: `contains()`, `contained_by()`, `overlap()` …)।
* **HSTORE** আর `hstore()`।
* **ফুল-টেক্সট সার্চ:** `to_tsvector()`, `to_tsquery()`, `plainto_tsquery()`, `phraseto_tsquery()`, `websearch_to_tsquery()`, `ts_headline()`।
* `ExcludeConstraint` আর `dialect`।

PostgreSQL-এর **টাইপগুলো** (range, ENUM, DOMAIN, INET, CITEXT …) আছে [PostgreSQL টাইপ পেজে](postgresql-types.md)।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
from sqlalchemy.dialects.postgresql import insert, JSONB, ARRAY, HSTORE

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    stock: Mapped[int] = mapped_column(default=0)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    attrs: Mapped[dict] = mapped_column(JSONB, default=dict)
    extra: Mapped[dict] = mapped_column(HSTORE, default=dict)
```

ডেটা: `P1` "লাল কলম" (stock ১০, tags `[pen, red]`, attrs `{"color": "red", "size": {"cm": 14}}`), `P2` "নীল খাতা" (stock ৫, tags `[book]`, attrs `{"pages": 100}`)। `pg(stmt)` PostgreSQL SQL দেখায়। PostgreSQL 16-এ চালিয়ে দেখা।

///

## Upsert (INSERT ... ON CONFLICT) { #insert-fn-group }

## `insert()` { #insert-fn }

```python
from sqlalchemy.dialects.postgresql import insert
```

```python
insert(table)
```

**ধরন:** ফাংশন

PostgreSQL-এর `INSERT` বানায়: সাধারণ `insert()`-এর সব কিছু, সাথে `ON CONFLICT` (upsert)। **সাধারণ `sqlalchemy.insert` নয়, এটা ইমপোর্ট করুন**, নইলে `on_conflict_*` মেথড পাবেন না।

**উদাহরণ:**

```python
stmt = insert(Product).values(sku="P1", name="লাল কলম", stock=3)
stmt = stmt.on_conflict_do_update(index_elements=[Product.sku], set_={"stock": Product.stock + stmt.excluded.stock})
session.execute(stmt); session.commit()
print(session.scalar(select(Product.stock).where(Product.sku == "P1")))   # 13  (১০ + ৩, নতুন রো নয়)
```

### `insert()`-এর সব প্যারামিটার { #insert-fn-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `table` | টেবিল বা মডেল। |

## `Insert` { #insert }

```python
from sqlalchemy.dialects.postgresql import Insert
```

PostgreSQL `insert()`-এর ফল। সাধারণ `Insert`-এর সব মেথড (`values()`, `returning()` …) আছে (ভাঁজ করা বক্সে [DML পেজের](dml.md) লিংক), সাথে নিচের তিনটি নিজস্ব।

**উদাহরণ:**

```python
stmt = insert(Product).values(sku="P3", name="পেন্সিল").on_conflict_do_nothing().returning(Product.id)
print(session.scalar(stmt))   # 3
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #insert-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`excluded`](#insert-excluded) | প্রপার্টি | `ON CONFLICT ... DO UPDATE`-এর ভেতরে "যে রো ঢোকাতে চেয়েছিলাম" তার কলাম: `stmt.excluded.stock` (SQL-এ `excluded.stock`)। |
| [`on_conflict_do_nothing()`](#insert-on-conflict-do-nothing) | মেথড | `ON CONFLICT DO NOTHING`: কনফ্লিক্ট হলে চুপচাপ বাদ (ডুপ্লিকেট এড়িয়ে বাল্ক insert)। |
| [`on_conflict_do_update()`](#insert-on-conflict-do-update) | মেথড | `ON CONFLICT (...) DO UPDATE SET ...`: কনফ্লিক্ট হলে বিদ্যমান রো হালনাগাদ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Insert`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`apply_syntax_extension_point()`](select.md#select-apply-syntax-extension-point) · [`argument_for()`](select.md#select-argument-for) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`ext()`](select.md#select-ext) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`prefix_with()`](select.md#select-prefix-with) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_hint()`](select.md#select-with-hint)

**`Insert` থেকে:** [`entity_description`](dml.md#insert-entity-description) · [`exported_columns`](dml.md#insert-exported-columns) · [`from_select()`](dml.md#insert-from-select) · [`include_insert_from_select_defaults`](dml.md#insert-include-insert-from-select-defaults) · [`inline()`](dml.md#insert-inline) · [`named_with_column`](dml.md#insert-named-with-column) · [`return_defaults()`](dml.md#insert-return-defaults) · [`returning()`](dml.md#insert-returning) · [`returning_column_descriptions`](dml.md#insert-returning-column-descriptions) · [`select`](dml.md#insert-select) · [`values()`](dml.md#insert-values) · [`with_dialect_options()`](dml.md#insert-with-dialect-options)

///

### `Insert.excluded` { #insert-excluded }

**ধরন:** প্রপার্টি

`ON CONFLICT ... DO UPDATE`-এর ভেতরে "যে রো ঢোকাতে চেয়েছিলাম" তার কলাম: `stmt.excluded.stock` (SQL-এ `excluded.stock`)। নতুন মান দিয়ে পুরোনো বদলাতে।

**উদাহরণ:**

```python
stmt = insert(Product).values(sku="P2", name="নীল খাতা (নতুন সংস্করণ)")
stmt = stmt.on_conflict_do_update(index_elements=["sku"], set_={"name": stmt.excluded.name})
session.execute(stmt); session.commit()
print(session.scalar(select(Product.name).where(Product.sku == "P2")))   # নীল খাতা (নতুন সংস্করণ)
```

### `Insert.on_conflict_do_nothing()` { #insert-on-conflict-do-nothing }

```python
Insert.on_conflict_do_nothing(constraint=None, index_elements=None, index_where=None)
```

**ধরন:** মেথড

`ON CONFLICT DO NOTHING`: কনফ্লিক্ট হলে চুপচাপ বাদ (ডুপ্লিকেট এড়িয়ে বাল্ক insert)। `index_elements`/`constraint` না দিলে যেকোনো unique কনফ্লিক্টে।

**উদাহরণ:**

```python
r = session.execute(insert(Product).values([{"sku": "P1", "name": "x"}, {"sku": "P9", "name": "নতুন"}])
                    .on_conflict_do_nothing(index_elements=["sku"]))
print(r.rowcount)   # 1  (P1 আগেই ছিল, শুধু P9 ঢুকল)
```

### `Insert.on_conflict_do_update()` { #insert-on-conflict-do-update }

```python
Insert.on_conflict_do_update(constraint=None, index_elements=None, index_where=None, set_=None, where=None)
```

**ধরন:** মেথড

`ON CONFLICT (...) DO UPDATE SET ...`: কনফ্লিক্ট হলে বিদ্যমান রো হালনাগাদ। কনফ্লিক্টের লক্ষ্য দিন `index_elements` (কলাম) বা `constraint` (কনস্ট্রেইন্টের নাম); partial index হলে `index_where`; কী বসবে `set_`; শর্তসাপেক্ষ আপডেটে `where`।

**উদাহরণ:**

```python
stmt = insert(Product).values(sku="P1", name="লাল কলম", stock=1)
stmt = stmt.on_conflict_do_update(
    constraint="products_sku_key",
    set_={"stock": stmt.excluded.stock},
    where=Product.stock < 100,
)
pg(stmt)
# INSERT INTO products (sku, name, stock, tags, attrs, extra) VALUES ('P1', 'লাল কলম', 1, NULL, NULL, NULL)
# ON CONFLICT ON CONSTRAINT products_sku_key DO UPDATE SET stock = excluded.stock WHERE products.stock < 100
# RETURNING products.id
```

## কুয়েরি সহায়ক { #distinct-on-group }

## `distinct_on()` { #distinct-on }

```python
from sqlalchemy.dialects.postgresql import distinct_on
```

```python
distinct_on(*expr)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) PostgreSQL-এর `SELECT DISTINCT ON (...)`: প্রতিটি দলের **প্রথম** রো (ORDER BY অনুযায়ী)। ব্যবহার `select(...).ext(distinct_on(col))`; পুরোনো `select().distinct(col)` ২.১-এ বাতিলের পথে।

**উদাহরণ:**

```python
session.add(Product(id=5, sku="P5", name="লাল খাতা", stock=7, tags=["book", "red"])); session.flush()
stmt = (select(Product.tags[1], Product.name).ext(distinct_on(Product.tags[1]))
        .order_by(Product.tags[1], Product.stock.desc()))
print(rows(stmt))   # [('book', 'লাল খাতা'), ('pen', 'লাল কলম')]  (প্রতিটি প্রথম-ট্যাগে সবচেয়ে বেশি stock)
```

### `distinct_on()`-এর সব প্যারামিটার { #distinct-on-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | যে কলাম(গুলো) অনুযায়ী অনন্য। |

## `aggregate_order_by` { #aggregate-order-by }

```python
from sqlalchemy.dialects.postgresql import aggregate_order_by
```

aggregate-এর ভেতরে `ORDER BY`: `array_agg(name ORDER BY stock)`। **২.১-এ** এটি সাধারণ `sqlalchemy.aggregate_order_by` / `func.xxx().aggregate_order_by()` হয়ে গেছে (সব ডেটাবেসে); PostgreSQL-এর এই রূপ পুরোনো কোডের জন্য।

**উদাহরণ:**

```python
print(session.scalar(select(func.array_agg(aggregate_order_by(Product.name, Product.stock.desc())))))   # ['লাল কলম', 'নীল খাতা']
```

### কনস্ট্রাক্টরের প্যারামিটার { #aggregate-order-by-params }

```python
aggregate_order_by(target, *order_by)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | যে এক্সপ্রেশন জড়ো হবে। |
| `order_by` | ভেতরের ORDER BY। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aggregate-order-by-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `aggregate_order_by`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## `array_agg()` { #array-agg }

```python
from sqlalchemy.dialects.postgresql import array_agg
```

```python
array_agg(*arg, **kw)
```

**ধরন:** ফাংশন

`func.array_agg()`-এর PostgreSQL রূপ: ফলের টাইপ `postgresql.ARRAY`, তাই `contains()`, `overlap()`-এর মতো PostgreSQL অপারেটর ফলের ওপর চলে।

**উদাহরণ:**

```python
agg = array_agg(Product.sku)
print(type(agg.type).__module__.split(".")[-2], session.scalar(select(agg)))   # postgresql ['P1', 'P2']
```

### `array_agg()`-এর সব প্যারামিটার { #array-agg-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `arg` | আর্গুমেন্ট। |
| `kw` | `type_=` ইত্যাদি। |

## `Any()` { #any }

```python
from sqlalchemy.dialects.postgresql import Any
```

```python
Any(other, arrexpr, operator=<built-in function eq>)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(পুরোনো) `মান <op> ANY (array)`। নতুন কোডে `col.any_()` বা `any_(col)`।

**উদাহরণ:**

```python
tags = Product.__table__.c.tags          # ORM অ্যাট্রিবিউট নয়, টেবিলের কলাম দিন
print(session.scalars(select(Product.sku).where(Any("red", tags))).all())   # ['P1']
```

### `Any()`-এর সব প্যারামিটার { #any-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `other` | তুলনার মান। |
| `arrexpr` | অ্যারে এক্সপ্রেশন। |
| `operator` | অপারেটর (ডিফল্ট `==`)। |

## `All()` { #all }

```python
from sqlalchemy.dialects.postgresql import All
```

```python
All(other, arrexpr, operator=<built-in function eq>)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(পুরোনো) `মান <op> ALL (array)`। নতুন কোডে `col.all_()`।

**উদাহরণ:**

```python
import operator
tags = Product.__table__.c.tags
print(session.scalars(select(Product.sku).where(All("a", tags, operator=operator.lt)).order_by(Product.id)).all())   # ['P1', 'P2']
```

### `All()`-এর সব প্যারামিটার { #all-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `other` | তুলনার মান। |
| `arrexpr` | অ্যারে এক্সপ্রেশন। |
| `operator` | অপারেটর। |

## ARRAY { #array-group }

## `ARRAY` { #array }

```python
from sqlalchemy.dialects.postgresql import ARRAY
```

PostgreSQL অ্যারে টাইপ (generic `ARRAY`-এর মতো), সাথে PostgreSQL-এর অ্যারে-অপারেটর: `contains()` (`@>`), `contained_by()` (`<@`), `overlap()` (`&&`)। GIN ইনডেক্স দিয়ে এই কুয়েরি দ্রুত হয়।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.contains(["red"]))).all())   # ['P1']
print(session.scalars(select(Product.sku).where(Product.tags.overlap(["book", "x"]))).all())   # ['P2']
```

### কনস্ট্রাক্টরের প্যারামিটার { #array-params }

```python
ARRAY(item_type, as_tuple=False, dimensions=None, zero_indexes=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `item_type` | উপাদানের টাইপ। |
| `as_tuple` | tuple ফেরত দেবে কি না। |
| `dimensions` | মাত্রা। |
| `zero_indexes` | ০-ভিত্তিক index। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ARRAY`](types.md#array-summary)-এর মতো।

## `postgresql.ARRAY.Comparator` { #pg-array-comparator }

```python
from sqlalchemy.dialects.postgresql import ARRAY
```

PostgreSQL ARRAY কলামের অপারেটর।

**উদাহরণ:**

```python
pg(Product.tags.contained_by(["pen", "red", "blue"]))   # products.tags <@ ARRAY['pen', 'red', 'blue']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #pg-array-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#pg-array-comparator-all) | মেথড (legacy) | `মান <op> ALL (col)`; নতুন কোডে `col.all_()`। |
| [`any()`](#pg-array-comparator-any) | মেথড (legacy) | `মান = ANY (col)`; নতুন কোডে `col.any_()`। |
| [`contained_by()`](#pg-array-comparator-contained-by) | মেথড | `<@`: কলামের সব উপাদান দেওয়া অ্যারের ভেতরে আছে কি না। |
| [`contains()`](#pg-array-comparator-contains) | মেথড | `@>`: কলামে দেওয়া সব উপাদান আছে কি না (স্ট্রিংয়ের `LIKE` নয়)। |
| [`overlap()`](#pg-array-comparator-overlap) | মেথড | `&&`: অন্তত একটি উপাদান মিলে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `postgresql.ARRAY.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `postgresql.ARRAY.Comparator.all()` { #pg-array-comparator-all }

```python
postgresql.ARRAY.Comparator.all(other, operator=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`মান <op> ALL (col)`; নতুন কোডে `col.all_()`।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.all("book"))).all())   # ['P2']
```

### `postgresql.ARRAY.Comparator.any()` { #pg-array-comparator-any }

```python
postgresql.ARRAY.Comparator.any(other, operator=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`মান = ANY (col)`; নতুন কোডে `col.any_()`।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.any("pen"))).all())   # ['P1']
```

### `postgresql.ARRAY.Comparator.contained_by()` { #pg-array-comparator-contained-by }

```python
postgresql.ARRAY.Comparator.contained_by(other)
```

**ধরন:** মেথড

`<@`: কলামের সব উপাদান দেওয়া অ্যারের ভেতরে আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.contained_by(["pen", "red", "book"]))).all())   # ['P1', 'P2']
```

### `postgresql.ARRAY.Comparator.contains()` { #pg-array-comparator-contains }

```python
postgresql.ARRAY.Comparator.contains(other, **kwargs)
```

**ধরন:** মেথড

`@>`: কলামে দেওয়া সব উপাদান আছে কি না (স্ট্রিংয়ের `LIKE` নয়)।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.contains(["pen", "red"]))).all())   # ['P1']
```

### `postgresql.ARRAY.Comparator.overlap()` { #pg-array-comparator-overlap }

```python
postgresql.ARRAY.Comparator.overlap(other)
```

**ধরন:** মেথড

`&&`: অন্তত একটি উপাদান মিলে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.tags.overlap(["red", "book"])).order_by(Product.id)).all())   # ['P1', 'P2']
```

## `array` { #array-literal }

```python
from sqlalchemy.dialects.postgresql import array
```

একটি অ্যারে **লিটারাল** `ARRAY[a, b, c]` (কলাম নয়, মান থেকে)। অ্যারে-কলামের সাথে তুলনা বা ফাংশনে দিতে।

**উদাহরণ:**

```python
pg(array([1, 2, 3]))                                                 # ARRAY[1, 2, 3]
print(session.scalar(select(array(["a", "b"])[2])))                 # b
```

### কনস্ট্রাক্টরের প্যারামিটার { #array-literal-params }

```python
array(clauses, *, type_=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | উপাদানগুলো। |
| `type_` | উপাদানের টাইপ (খালি অ্যারে বা অস্পষ্ট মানের জন্য)। |
| `kw` | বাড়তি অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #array-literal-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `array`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`BinaryExpression` থেকে:** [`group`](elements.md#binaryexpression-group) · [`is_comparison`](elements.md#binaryexpression-is-comparison)

///

## JSON ও JSONB { #jsonb-group }

## `JSONB` { #jsonb }

```python
from sqlalchemy.dialects.postgresql import JSONB
```

বাইনারি JSON (PostgreSQL-এ সাধারণত **JSON-এর চেয়ে ভালো**): ইনডেক্স করা যায় (GIN), key-ক্রম/ফাঁকা জায়গা রাখে না, আর `?`, `@>`, `@?` ইত্যাদি অপারেটর। `col["key"]` → JSON মান, `col["key"].astext` → টেক্সট (`->>`)।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs["color"].astext == "red")).all())   # ['P1']
print(session.scalar(select(Product.attrs[("size", "cm")].as_integer()).where(Product.id == 1)))   # 14
```

### কনস্ট্রাক্টরের প্যারামিটার { #jsonb-params }

```python
JSONB(none_as_null=False, astext_type=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `None` → SQL NULL (ডিফল্টে JSON null)। |
| `astext_type` | `.astext`-এর ফলের টাইপ (ডিফল্ট `Text`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #jsonb-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`astext_type`](#jsonb-astext-type) | অ্যাট্রিবিউট | `.astext`-এর ফলের টাইপ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSONB`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

**`JSON` থেকে:** [`JSONElementType`](types.md#json-JSONElementType) · [`JSONIndexType`](types.md#json-JSONIndexType) · [`JSONIntIndexType`](types.md#json-JSONIntIndexType) · [`JSONPathType`](types.md#json-JSONPathType) · [`JSONStrIndexType`](types.md#json-JSONStrIndexType) · [`NULL`](types.md#json-NULL)

///

### `JSONB.astext_type` { #jsonb-astext-type }

**ধরন:** অ্যাট্রিবিউট

`.astext`-এর ফলের টাইপ।

**উদাহরণ:**

```python
print(JSONB().astext_type)   # TEXT
```

## `JSONB.Comparator` { #jsonb-comparator }

```python
from sqlalchemy.dialects.postgresql import JSONB
```

JSONB কলামের অপারেটর: key আছে কি না, ধারণ, JSONPath, path মোছা; আর generic JSON-এর `as_string()`, `as_integer()` …

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.has_key("pages"))).all())   # ['P2']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #jsonb-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`astext`](#jsonb-comparator-astext) | প্রপার্টি | index করা মানকে টেক্সট হিসেবে (`->>`; path হলে `#>>`)। |
| [`contained_by()`](#jsonb-comparator-contained-by) | মেথড | `<@`: কলামের JSON দেওয়া JSON-এর ভেতরে আছে কি না। |
| [`contains()`](#jsonb-comparator-contains) | মেথড | `@>`: কলামের JSON দেওয়া অংশটি ধারণ করে কি না (GIN ইনডেক্স-বান্ধব)। |
| [`delete_path()`](#jsonb-comparator-delete-path) | মেথড | `#-`: নির্দিষ্ট path-এর মান মুছে নতুন JSON দেয়। |
| [`has_all()`](#jsonb-comparator-has-all) | মেথড | `?&`: সব key আছে কি না। |
| [`has_any()`](#jsonb-comparator-has-any) | মেথড | <code>?&#124;</code>: যেকোনো একটি key আছে কি না। |
| [`has_key()`](#jsonb-comparator-has-key) | মেথড | `?`: একটি key আছে কি না। |
| [`path_exists()`](#jsonb-comparator-path-exists) | মেথড | `@?`: JSONPath দিয়ে কোনো item আছে কি না। |
| [`path_match()`](#jsonb-comparator-path-match) | মেথড | `@@`: JSONPath শর্ত (predicate) মেলে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSONB.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`JSON.Comparator` থেকে:** [`as_boolean()`](types.md#json-comparator-as-boolean) · [`as_float()`](types.md#json-comparator-as-float) · [`as_integer()`](types.md#json-comparator-as-integer) · [`as_json()`](types.md#json-comparator-as-json) · [`as_numeric()`](types.md#json-comparator-as-numeric) · [`as_string()`](types.md#json-comparator-as-string)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `JSONB.Comparator.astext` { #jsonb-comparator-astext }

**ধরন:** প্রপার্টি

index করা মানকে টেক্সট হিসেবে (`->>`; path হলে `#>>`)। তুলনা/সাজানোর আগে লাগে।

**উদাহরণ:**

```python
pg(Product.attrs["color"].astext)   # products.attrs ->> 'color'
```

### `JSONB.Comparator.contained_by()` { #jsonb-comparator-contained-by }

```python
JSONB.Comparator.contained_by(other)
```

**ধরন:** মেথড

`<@`: কলামের JSON দেওয়া JSON-এর ভেতরে আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.contained_by({"pages": 100, "x": 1}))).all())   # ['P2']
```

### `JSONB.Comparator.contains()` { #jsonb-comparator-contains }

```python
JSONB.Comparator.contains(other, **kwargs)
```

**ধরন:** মেথড

`@>`: কলামের JSON দেওয়া অংশটি ধারণ করে কি না (GIN ইনডেক্স-বান্ধব)।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.contains({"color": "red"}))).all())   # ['P1']
```

### `JSONB.Comparator.delete_path()` { #jsonb-comparator-delete-path }

```python
JSONB.Comparator.delete_path(array)
```

**ধরন:** মেথড

`#-`: নির্দিষ্ট path-এর মান মুছে নতুন JSON দেয়।

**উদাহরণ:**

```python
print(session.scalar(select(Product.attrs.delete_path(["size", "cm"])).where(Product.id == 1)))   # {'size': {}, 'color': 'red'}
```

### `JSONB.Comparator.has_all()` { #jsonb-comparator-has-all }

```python
JSONB.Comparator.has_all(other)
```

**ধরন:** মেথড

`?&`: সব key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.has_all(array(["color", "size"])))).all())   # ['P1']
```

### `JSONB.Comparator.has_any()` { #jsonb-comparator-has-any }

```python
JSONB.Comparator.has_any(other)
```

**ধরন:** মেথড

`?|`: যেকোনো একটি key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.has_any(array(["pages", "zz"])))).all())   # ['P2']
```

### `JSONB.Comparator.has_key()` { #jsonb-comparator-has-key }

```python
JSONB.Comparator.has_key(other)
```

**ধরন:** মেথড

`?`: একটি key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.has_key("color"))).all())   # ['P1']
```

### `JSONB.Comparator.path_exists()` { #jsonb-comparator-path-exists }

```python
JSONB.Comparator.path_exists(other)
```

**ধরন:** মেথড

`@?`: JSONPath দিয়ে কোনো item আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.path_exists("$.size.cm"))).all())   # ['P1']
```

### `JSONB.Comparator.path_match()` { #jsonb-comparator-path-match }

```python
JSONB.Comparator.path_match(other)
```

**ধরন:** মেথড

`@@`: JSONPath শর্ত (predicate) মেলে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.attrs.path_match("$.pages > 50"))).all())   # ['P2']
```

## `JSON` { #json }

```python
from sqlalchemy.dialects.postgresql import JSON
```

PostgreSQL-এর টেক্সট-ভিত্তিক `JSON` (ইনপুট হুবহু রাখে)। সাধারণত `JSONB` ভালো; JSON-এ `has_key()` ইত্যাদি নেই, তবে `.astext` আছে।

**উদাহরণ:**

```python
print(JSON().compile(dialect=postgresql.dialect()), JSON().astext_type)   # JSON TEXT
```

### কনস্ট্রাক্টরের প্যারামিটার { #json-params }

```python
JSON(none_as_null=False, astext_type=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `None` → SQL NULL। |
| `astext_type` | `.astext`-এর টাইপ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #json-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSON`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

**`JSON` থেকে:** [`JSONElementType`](types.md#json-JSONElementType) · [`JSONIndexType`](types.md#json-JSONIndexType) · [`JSONIntIndexType`](types.md#json-JSONIntIndexType) · [`JSONPathType`](types.md#json-JSONPathType) · [`JSONStrIndexType`](types.md#json-JSONStrIndexType) · [`NULL`](types.md#json-NULL)

**`JSONB` থেকে:** [`astext_type`](#jsonb-astext-type)

///

## `postgresql.JSON.Comparator` { #pg-json-comparator }

```python
from sqlalchemy.dialects.postgresql import JSON
```

PostgreSQL JSON কলামের অপারেটর: generic JSON-এর সব, সাথে `astext`।

**উদাহরণ:**

```python
print(JSON.comparator_factory.__qualname__)   # JSON.Comparator
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #pg-json-comparator-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `postgresql.JSON.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`JSON.Comparator` থেকে:** [`as_boolean()`](types.md#json-comparator-as-boolean) · [`as_float()`](types.md#json-comparator-as-float) · [`as_integer()`](types.md#json-comparator-as-integer) · [`as_json()`](types.md#json-comparator-as-json) · [`as_numeric()`](types.md#json-comparator-as-numeric) · [`as_string()`](types.md#json-comparator-as-string)

**`JSONB.Comparator` থেকে:** [`astext`](#jsonb-comparator-astext) · [`contains()`](#jsonb-comparator-contains)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

## `JSONPATH` { #jsonpath }

```python
from sqlalchemy.dialects.postgresql import JSONPATH
```

JSONPath মানের টাইপ (`jsonpath`); `path_exists()`/`path_match()`-এর আর্গুমেন্টে নিজে থেকে ব্যবহৃত হয়। ফাংশনে স্পষ্টভাবে দিতে `cast("$.a", JSONPATH)`।

**উদাহরণ:**

```python
print(session.scalar(select(func.jsonb_path_query_first(Product.attrs, cast("$.size.cm", JSONPATH))).where(Product.id == 1)))   # 14
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #jsonpath-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`string_bind_processor()`](#jsonpath-string-bind-processor) | মেথড (internal) | path-স্ট্রিং প্যারামিটার রূপান্তরের ভেতরের ফাংশন। |
| [`string_literal_processor()`](#jsonpath-string-literal-processor) | মেথড (internal) | path-স্ট্রিং literal রূপান্তরের ভেতরের ফাংশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `JSONPATH`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `JSONPATH.string_bind_processor()` { #jsonpath-string-bind-processor }

```python
JSONPATH.string_bind_processor(dialect)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

path-স্ট্রিং প্যারামিটার রূপান্তরের ভেতরের ফাংশন।

### `JSONPATH.string_literal_processor()` { #jsonpath-string-literal-processor }

```python
JSONPATH.string_literal_processor(dialect)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

path-স্ট্রিং literal রূপান্তরের ভেতরের ফাংশন।

## HSTORE { #hstore-group }

## `HSTORE` { #hstore }

```python
from sqlalchemy.dialects.postgresql import HSTORE
```

PostgreSQL-এর key → value (দুটোই স্ট্রিং) টাইপ (`hstore` extension লাগে)। Python-এ dict। এখন সাধারণত JSONB বেশি ব্যবহৃত হয়।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra["brand"]).where(Product.id == 1)))   # Matador
```

### কনস্ট্রাক্টরের প্যারামিটার { #hstore-params }

```python
HSTORE(text_type=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `text_type` | `col[key]`-এর ফলের টাইপ (ডিফল্ট `Text`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hstore-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`text_type`](#hstore-text-type) | অ্যাট্রিবিউট | মানগুলোর টাইপ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HSTORE`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `HSTORE.text_type` { #hstore-text-type }

**ধরন:** অ্যাট্রিবিউট

মানগুলোর টাইপ।

**উদাহরণ:**

```python
print(HSTORE().text_type)   # TEXT
```

## `HSTORE.Comparator` { #hstore-comparator }

```python
from sqlalchemy.dialects.postgresql import HSTORE
```

HSTORE কলামের অপারেটর।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.has_key("brand"))).all())   # ['P1']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hstore-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`array()`](#hstore-comparator-array) | মেথড | `%%`: key আর value পালাক্রমে একটি অ্যারেতে। |
| [`contained_by()`](#hstore-comparator-contained-by) | মেথড | `<@`: দেওয়া hstore-এর ভেতরে আছে কি না। |
| [`contains()`](#hstore-comparator-contains) | মেথড | `@>`: দেওয়া জোড়াগুলো আছে কি না। |
| [`defined()`](#hstore-comparator-defined) | মেথড | key-টির মান NULL নয় কি না। |
| [`delete()`](#hstore-comparator-delete) | মেথড | key মুছে নতুন hstore দেয়। |
| [`has_all()`](#hstore-comparator-has-all) | মেথড | `?&`: সব key আছে কি না। |
| [`has_any()`](#hstore-comparator-has-any) | মেথড | <code>?&#124;</code>: যেকোনো key আছে কি না। |
| [`has_key()`](#hstore-comparator-has-key) | মেথড | `?`: key আছে কি না। |
| [`keys()`](#hstore-comparator-keys) | মেথড | সব key-এর অ্যারে। |
| [`matrix()`](#hstore-comparator-matrix) | মেথড | `[[key, value], ...]` অ্যারে। |
| [`slice()`](#hstore-comparator-slice) | মেথড | নির্দিষ্ট key-গুলোর উপ-hstore। |
| [`vals()`](#hstore-comparator-vals) | মেথড | সব value-এর অ্যারে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HSTORE.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `HSTORE.Comparator.array()` { #hstore-comparator-array }

```python
HSTORE.Comparator.array()
```

**ধরন:** মেথড

`%%`: key আর value পালাক্রমে একটি অ্যারেতে।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra.array()).where(Product.id == 1)))   # ['brand', 'Matador']
```

### `HSTORE.Comparator.contained_by()` { #hstore-comparator-contained-by }

```python
HSTORE.Comparator.contained_by(other)
```

**ধরন:** মেথড

`<@`: দেওয়া hstore-এর ভেতরে আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.contained_by({"brand": "Matador", "x": "1"}))).all())   # ['P1', 'P2']
```

### `HSTORE.Comparator.contains()` { #hstore-comparator-contains }

```python
HSTORE.Comparator.contains(other, **kwargs)
```

**ধরন:** মেথড

`@>`: দেওয়া জোড়াগুলো আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.contains({"brand": "Matador"}))).all())   # ['P1']
```

### `HSTORE.Comparator.defined()` { #hstore-comparator-defined }

```python
HSTORE.Comparator.defined(key)
```

**ধরন:** মেথড

key-টির মান NULL নয় কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.defined("brand"))).all())   # ['P1']
```

### `HSTORE.Comparator.delete()` { #hstore-comparator-delete }

```python
HSTORE.Comparator.delete(key)
```

**ধরন:** মেথড

key মুছে নতুন hstore দেয়।

**উদাহরণ:**

```python
print(repr(session.scalar(select(Product.extra.delete("brand")).where(Product.id == 1))))   # ''  (খালি hstore, টেক্সট রূপে)
```

### `HSTORE.Comparator.has_all()` { #hstore-comparator-has-all }

```python
HSTORE.Comparator.has_all(other)
```

**ধরন:** মেথড

`?&`: সব key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.has_all(array(["brand"])))).all())   # ['P1']
```

### `HSTORE.Comparator.has_any()` { #hstore-comparator-has-any }

```python
HSTORE.Comparator.has_any(other)
```

**ধরন:** মেথড

`?|`: যেকোনো key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.has_any(array(["brand", "x"])))).all())   # ['P1']
```

### `HSTORE.Comparator.has_key()` { #hstore-comparator-has-key }

```python
HSTORE.Comparator.has_key(other)
```

**ধরন:** মেথড

`?`: key আছে কি না।

**উদাহরণ:**

```python
print(session.scalars(select(Product.sku).where(Product.extra.has_key("x"))).all())   # []
```

### `HSTORE.Comparator.keys()` { #hstore-comparator-keys }

```python
HSTORE.Comparator.keys()
```

**ধরন:** মেথড

সব key-এর অ্যারে।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra.keys()).where(Product.id == 1)))   # ['brand']
```

### `HSTORE.Comparator.matrix()` { #hstore-comparator-matrix }

```python
HSTORE.Comparator.matrix()
```

**ধরন:** মেথড

`[[key, value], ...]` অ্যারে।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra.matrix()).where(Product.id == 1)))   # [['brand', 'Matador']]
```

### `HSTORE.Comparator.slice()` { #hstore-comparator-slice }

```python
HSTORE.Comparator.slice(array)
```

**ধরন:** মেথড

নির্দিষ্ট key-গুলোর উপ-hstore।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra.slice(array(["brand"]))).where(Product.id == 1)))   # "brand"=>"Matador"  (hstore টেক্সট রূপে)
```

### `HSTORE.Comparator.vals()` { #hstore-comparator-vals }

```python
HSTORE.Comparator.vals()
```

**ধরন:** মেথড

সব value-এর অ্যারে।

**উদাহরণ:**

```python
print(session.scalar(select(Product.extra.vals()).where(Product.id == 1)))   # ['Matador']
```

## `hstore()` { #hstore-func }

```python
from sqlalchemy.dialects.postgresql import hstore
```

SQL ফাংশন `hstore(...)`: key আর value (বা দুটি অ্যারে) থেকে hstore মান বানায়।

**উদাহরণ:**

```python
print(session.scalar(select(hstore("a", "1"))))   # "a"=>"1"  (ফাংশনের ফল hstore-টেক্সট রূপে আসে; কলামে রাখলে dict)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## ফুল-টেক্সট সার্চ { #to-tsvector-group }

## `to_tsvector()` { #to-tsvector }

```python
from sqlalchemy.dialects.postgresql import to_tsvector
```

লেখাকে সার্চযোগ্য `tsvector`-এ রূপান্তর (শব্দমূল, stop-word বাদ)। প্রথম আর্গুমেন্টে ভাষা-কনফিগ (`"english"`, `"simple"`) দেওয়া সুপারিশকৃত। `col.match(...)` বা `@@` দিয়ে `tsquery`-র সাথে মেলান। বিস্তারিত: [অ্যাডভান্সড কুয়েরি §৩১.২](../advanced-queries.md#s31-2)।

**উদাহরণ:**

```python
vec = to_tsvector("english", "The quick brown foxes jumped")
print(session.scalar(select(vec)))   # 'brown':3 'fox':4 'jump':5 'quick':2
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## `to_tsquery()` { #to-tsquery }

```python
from sqlalchemy.dialects.postgresql import to_tsquery
```

tsquery বানায় অপারেটরসহ (`&`, `|`, `!`, `:*` prefix)।

**উদাহরণ:**

```python
q = to_tsquery("english", "fox & !cat")
print(session.scalar(select(to_tsvector("english", "red fox").bool_op("@@")(q))))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## `plainto_tsquery()` { #plainto-tsquery }

```python
from sqlalchemy.dialects.postgresql import plainto_tsquery
```

সাধারণ লেখা থেকে tsquery (সব শব্দ AND)। `col.match("...")` ভেতরে এটি ব্যবহার করে।

**উদাহরণ:**

```python
print(session.scalar(select(plainto_tsquery("english", "quick foxes"))))   # 'quick' & 'fox'
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## `phraseto_tsquery()` { #phraseto-tsquery }

```python
from sqlalchemy.dialects.postgresql import phraseto_tsquery
```

শব্দগুলো **ক্রম অনুযায়ী পাশাপাশি** থাকতে হবে এমন tsquery (`<->`)।

**উদাহরণ:**

```python
print(session.scalar(select(phraseto_tsquery("english", "brown fox"))))   # 'brown' <-> 'fox'
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## `websearch_to_tsquery()` { #websearch-to-tsquery }

```python
from sqlalchemy.dialects.postgresql import websearch_to_tsquery
```

সার্চ-বক্সের মতো সিনট্যাক্স থেকে tsquery: `"phrase"`, `or`, `-বাদ`। ইউজারের ইনপুট সরাসরি দেওয়ার জন্য নিরাপদ (সিনট্যাক্স-এরর হয় না)।

**উদাহরণ:**

```python
print(session.scalar(select(websearch_to_tsquery("english", '"brown fox" -cat'))))   # 'brown' <-> 'fox' & !'cat'
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## `ts_headline()` { #ts-headline }

```python
from sqlalchemy.dialects.postgresql import ts_headline
```

সার্চ-ফলে মেলা শব্দগুলো হাইলাইট করা অংশ (`<b>...</b>`) দেয়।

**উদাহরণ:**

```python
print(session.scalar(select(ts_headline("english", "The quick brown fox", to_tsquery("english", "fox")))))   # The quick brown <b>fox</b>
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](functions.md#genericfunction-summary)-এর মতো।

## অন্যান্য { #excludeconstraint-group }

## `ExcludeConstraint` { #excludeconstraint }

```python
from sqlalchemy.dialects.postgresql import ExcludeConstraint
```

PostgreSQL-এর `EXCLUDE` কনস্ট্রেইন্ট: UNIQUE-এর সাধারণীকৃত রূপ, যেকোনো অপারেটর দিয়ে। ক্লাসিক উদাহরণ: একই রুমে **সময় ওভারল্যাপ করা দুটি বুকিং নিষেধ** (range + `&&`; `btree_gist` extension লাগে)।

**উদাহরণ:**

```python
from sqlalchemy.dialects.postgresql import TSRANGE
from sqlalchemy import exc
m = MetaData()
booking = Table("booking", m, Column("room", Integer), Column("during", TSRANGE),
                ExcludeConstraint(("room", "="), ("during", "&&"), using="gist", name="no_overlap"))
m.create_all(engine)
with engine.connect() as c:
    c.execute(booking.insert().values(room=1, during=text("'[2025-01-01 10:00, 2025-01-01 12:00)'")))
    try:
        c.execute(booking.insert().values(room=1, during=text("'[2025-01-01 11:00, 2025-01-01 13:00)'")))
    except exc.IntegrityError as e:
        print(type(e.orig).__name__)   # ExclusionViolation
```

### কনস্ট্রাক্টরের প্যারামিটার { #excludeconstraint-params }

```python
ExcludeConstraint(*elements, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `elements` | `(কলাম বা এক্সপ্রেশন, অপারেটর)` জোড়াগুলো। |
| `kw` | `name`, `using` (`"gist"` ইত্যাদি), `where` (partial), `deferrable`, `initially`, `ops` (operator class), `info`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #excludeconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`inherit_cache`](#excludeconstraint-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ফ্ল্যাগ। |
| [`where`](#excludeconstraint-where) | অ্যাট্রিবিউট | partial কনস্ট্রেইন্টের শর্ত (না দিলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ExcludeConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`info`](schema.md#table-info) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`ColumnCollectionConstraint` থেকে:** [`c`](constraints.md#columncollectionconstraint-c) · [`columns`](constraints.md#columncollectionconstraint-columns) · [`contains_column()`](constraints.md#columncollectionconstraint-contains-column)

**`Constraint` থেকে:** [`copy()`](constraints.md#constraint-copy) · [`ddl_if()`](constraints.md#constraint-ddl-if) · [`table`](constraints.md#constraint-table)

///

### `ExcludeConstraint.inherit_cache` { #excludeconstraint-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ফ্ল্যাগ।

### `ExcludeConstraint.where` { #excludeconstraint-where }

**ধরন:** অ্যাট্রিবিউট

partial কনস্ট্রেইন্টের শর্ত (না দিলে `None`)।

**উদাহরণ:**

```python
c = ExcludeConstraint(("room", "="), where=text("active"))
print(c.where)   # active
```

## `dialect` { #dialect }

```python
from sqlalchemy.dialects.postgresql import dialect
```

PostgreSQL-এর ডিফল্ট ডায়ালেক্ট ক্লাস (**২.১-এ psycopg 3-ভিত্তিক**; ২.০-তে ছিল psycopg2)। SQL কম্পাইল করে দেখতে `stmt.compile(dialect=postgresql.dialect())`। এর ১৭৯টি সদস্য সবই SQLAlchemy-র ভেতরের ডায়ালেক্ট-ইন্টারফেস (নতুন ডায়ালেক্ট লেখকদের জন্য), তাই আলাদা তালিকা দেওয়া হয়নি।

**উদাহরণ:**

```python
d = dialect()
print(d.name, d.driver)   # postgresql psycopg
```

/// check | সংক্ষেপে মনে রাখুন

* upsert: `from sqlalchemy.dialects.postgresql import insert` → `.on_conflict_do_update(index_elements=[...], set_={... stmt.excluded.col})`।
* JSONB-এ key আছে কি না `has_key()`, অংশ ধারণ `contains({...})`, টেক্সট মান `col["k"].astext`।
* ARRAY: `contains([...])`, `overlap([...])`, `col.any_()`।
* ফুল-টেক্সট: `to_tsvector("english", col).bool_op("@@")(websearch_to_tsquery("english", q))` বা `col.match(q)`।
* প্রতিটি দলের প্রথম রো: `select(...).ext(distinct_on(col))` (২.১)।

///
