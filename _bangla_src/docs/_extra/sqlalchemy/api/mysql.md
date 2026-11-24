# MySQL ও MariaDB API: upsert, UPDATE … LIMIT, MATCH, বিশেষ টাইপ { #api-mysql }

/// note | এই পেজে যা আছে

`sqlalchemy.dialects.mysql`-এর সব পাবলিক API (MariaDB-ও এই একই মডিউল ব্যবহার করে):

* **Upsert:** `insert()` আর `Insert`-এর `on_duplicate_key_update()`, `inserted`।
* **২.১-এর নতুন `limit()`:** `UPDATE ... LIMIT` / `DELETE ... LIMIT`।
* **ফুল-টেক্সট:** `match()` (`MATCH (...) AGAINST (...)`)।
* **টাইপ:** পূর্ণসংখ্যা (`TINYINT` … `BIGINT`, `UNSIGNED`/`ZEROFILL`সহ), দশমিক, স্ট্রিং (`CHARACTER SET`/`COLLATE`সহ, `TINYTEXT` … `LONGTEXT`), `ENUM`, `SET`, `YEAR`, `BIT`, তারিখ-সময় (`fsp`), BLOB, `JSON`, MariaDB-র `INET4`/`INET6`।
* `dialect` আর সাধারণ টাইপের তালিকা পেজের শেষে।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
from sqlalchemy.dialects import mysql

m = MetaData()
products = Table("products", m,
                 Column("id", Integer, primary_key=True),
                 Column("sku", String(20), unique=True),
                 Column("name", String(100)),
                 Column("stock", Integer))
```

* `my(stmt)`: MySQL-এর জন্য তৈরি SQL দেখায় (মানসহ)। `myt(টাইপ)`: `CREATE TABLE`-এ টাইপটি কী নামে বসে।
* এই পেজের উদাহরণ **কম্পাইল করে** দেখানো (পরীক্ষার পরিবেশে MySQL সার্ভার নেই); যে SQL ছাপা হয়েছে, সেটাই সার্ভারে যায়। সংযোগ: `create_engine("mysql+pymysql://user:pass@host/db?charset=utf8mb4")`, MariaDB হলে `"mariadb+pymysql://..."`।

///

## Upsert (INSERT ... ON DUPLICATE KEY UPDATE) { #insert-fn-group }

## `insert()` { #insert-fn }

```python
from sqlalchemy.dialects.mysql import insert
```

```python
insert(table)
```

**ধরন:** ফাংশন

MySQL-এর `INSERT` বানায়: সাধারণ `insert()`-এর সব কিছু, সাথে `ON DUPLICATE KEY UPDATE`। **সাধারণ `sqlalchemy.insert` নয়, এটা ইমপোর্ট করুন।** PostgreSQL/SQLite-এর মতো কোন কলামে কনফ্লিক্ট তা বলা যায় না: **যেকোনো** PRIMARY KEY বা UNIQUE কনফ্লিক্টে আপডেট হয়।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="লাল কলম", stock=3)
my(stmt.on_duplicate_key_update(stock=products.c.stock + stmt.inserted.stock))
# INSERT INTO products (sku, name, stock) VALUES ('P1', 'লাল কলম', 3) ON DUPLICATE KEY UPDATE stock = (products.stock + VALUES(stock))
```

### `insert()`-এর সব প্যারামিটার { #insert-fn-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `table` | টেবিল বা মডেল। |

## `Insert` { #insert }

```python
from sqlalchemy.dialects.mysql import Insert
```

MySQL `insert()`-এর ফল। সাধারণ `Insert`-এর সব মেথড আছে (ভাঁজ করা বক্সে [DML পেজের](dml.md) লিংক), সাথে নিচের তিনটি নিজস্ব।

**MySQL ৮.০.২০+**: `VALUES(col)` ফাংশন সেখানে বাতিলের পথে। সার্ভারের ভার্সন ৮.০.২০ বা তার বেশি হলে SQLAlchemy নিজে থেকেই নতুন রূপ লেখে: `INSERT ... VALUES (...) AS new ON DUPLICATE KEY UPDATE stock = new.stock`। আপনার কোড একই থাকে।

**উদাহরণ:**

```python
stmt = insert(products).values([{"sku": "P1", "name": "কলম"}, {"sku": "P2", "name": "খাতা"}])
my(stmt.on_duplicate_key_update(name=stmt.inserted.name))
# INSERT INTO products (sku, name) VALUES ('P1', 'কলম'), ('P2', 'খাতা') ON DUPLICATE KEY UPDATE name = VALUES(name)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #insert-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`inserted`](#insert-inserted) | প্রপার্টি | "যে রো ঢোকাতে চেয়েছিলাম" তার কলামগুলো (`ColumnCollection`): `stmt.inserted.stock` SQL-এ হয় `VALUES(stock)` (৮.০.২০+-এ `new.stock`)। |
| [`inserted_alias`](#insert-inserted-alias) | প্রপার্টি (internal) | `inserted`-এর পেছনের alias (টেবিলের `inserted` নামের alias)। |
| [`on_duplicate_key_update()`](#insert-on-duplicate-key-update) | মেথড | `ON DUPLICATE KEY UPDATE` অংশ যোগ করে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Insert`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`apply_syntax_extension_point()`](select.md#select-apply-syntax-extension-point) · [`argument_for()`](select.md#select-argument-for) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`ext()`](select.md#select-ext) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`prefix_with()`](select.md#select-prefix-with) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_hint()`](select.md#select-with-hint)

**`Insert` থেকে:** [`entity_description`](dml.md#insert-entity-description) · [`exported_columns`](dml.md#insert-exported-columns) · [`from_select()`](dml.md#insert-from-select) · [`include_insert_from_select_defaults`](dml.md#insert-include-insert-from-select-defaults) · [`inline()`](dml.md#insert-inline) · [`named_with_column`](dml.md#insert-named-with-column) · [`return_defaults()`](dml.md#insert-return-defaults) · [`returning()`](dml.md#insert-returning) · [`returning_column_descriptions`](dml.md#insert-returning-column-descriptions) · [`select`](dml.md#insert-select) · [`values()`](dml.md#insert-values) · [`with_dialect_options()`](dml.md#insert-with-dialect-options)

///

### `Insert.inserted` { #insert-inserted }

**ধরন:** প্রপার্টি

"যে রো ঢোকাতে চেয়েছিলাম" তার কলামগুলো (`ColumnCollection`): `stmt.inserted.stock` SQL-এ হয় `VALUES(stock)` (৮.০.২০+-এ `new.stock`)। নাম `values` নয় যাতে `Insert.values()` মেথডের সাথে না মেলে; অদ্ভুত নামের কলাম `stmt.inserted["col name"]`।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="নতুন নাম")
print(stmt.inserted.name.table.name, list(stmt.inserted.keys()))   # inserted ['id', 'sku', 'name', 'stock']
```

### `Insert.inserted_alias` { #insert-inserted-alias }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`inserted`-এর পেছনের alias (টেবিলের `inserted` নামের alias)। কম্পাইলার এটি দেখে চেনে কোন কলাম `VALUES()`/`new.` হিসেবে লিখতে হবে; সাধারণত `inserted` ব্যবহার করুন।

**উদাহরণ:**

```python
stmt = insert(products)
print(stmt.inserted_alias.name, stmt.inserted_alias.c.sku is stmt.inserted.sku)   # inserted True
```

### `Insert.on_duplicate_key_update()` { #insert-on-duplicate-key-update }

```python
Insert.on_duplicate_key_update(*args, **kw)
```

**ধরন:** মেথড

`ON DUPLICATE KEY UPDATE` অংশ যোগ করে। তিনভাবে মান দিন: কীওয়ার্ড (`stock=...`), একটি dict (কলামের নাম ফাঁকা/অদ্ভুত হলে), বা `(কলাম, মান)` জোড়ার **তালিকা** (SET-এর ক্রম ঠিক রাখতে)। একটি স্টেটমেন্টে একবারই দেওয়া যায়।

**সাবধান:** কলামের `onupdate=` (যেমন `updated_at`) এখানে নিজে থেকে চলে না; দরকার হলে নিজে লিখুন।

**উদাহরণ:**

```python
stmt = insert(products).values(sku="P1", name="কলম", stock=1)
my(stmt.on_duplicate_key_update({"stock": products.c.stock + stmt.inserted.stock, "name": stmt.inserted.name}))
# INSERT INTO products (sku, name, stock) VALUES ('P1', 'কলম', 1) ON DUPLICATE KEY UPDATE name = VALUES(name), stock = (products.stock + VALUES(stock))
# (SET-এর ক্রম টেবিলের কলামের ক্রমে)
print(stmt.on_duplicate_key_update([("stock", 0), ("name", "x")]).compile(dialect=mysql.dialect()))
# INSERT INTO products (sku, name, stock) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE stock = %s, name = %s
```

## UPDATE/DELETE-এ LIMIT ও ফুল-টেক্সট MATCH { #limit-group }

## `limit()` { #limit }

```python
from sqlalchemy.dialects.mysql import limit
```

```python
limit(limit)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) MySQL/MariaDB-র `UPDATE ... LIMIT n` আর `DELETE ... LIMIT n`। `.ext(limit(n))` দিয়ে যোগ করুন। আগের `mysql_limit=` কীওয়ার্ডের জায়গায়। বড় টেবিল ছোট ছোট ব্যাচে মুছতে কাজে লাগে।

**উদাহরণ:**

```python
my(update(products).values(stock=0).where(products.c.stock < 0).ext(limit(5)))
# UPDATE products SET stock=0 WHERE products.stock < 0 LIMIT 5
my(delete(products).where(products.c.stock == 0).ext(limit(1000)))
# DELETE FROM products WHERE products.stock = 0 LIMIT 1000
```

### `limit()`-এর সব প্যারামিটার { #limit-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `limit` | সর্বোচ্চ কতটি রো (সংখ্যা বা SQL এক্সপ্রেশন)। |

## `match` { #match }

```python
from sqlalchemy.dialects.mysql import match
```

`MATCH (col1, col2) AGAINST ('শব্দ')`: MySQL-এর ফুল-টেক্সট সার্চ (কলামগুলোতে `FULLTEXT` ইনডেক্স লাগবে)। সাধারণ `col.match("...")`-এর মতো, কিন্তু **একাধিক কলাম** নেয় আর মোড বেছে নেওয়া যায়। ফল একটি সংখ্যা (প্রাসঙ্গিকতা), তাই `ORDER BY`-তেও দেওয়া যায়।

**উদাহরণ:**

```python
m_expr = match(products.c.name, products.c.sku, against="কলম")
my(select(products.c.id).where(m_expr.in_boolean_mode()).order_by(desc(m_expr)))
# SELECT products.id
# FROM products
# WHERE MATCH (products.name, products.sku) AGAINST ('কলম' IN BOOLEAN MODE) ORDER BY MATCH (products.name, products.sku) AGAINST ('কলম') DESC
```

### কনস্ট্রাক্টরের প্যারামিটার { #match-params }

```python
match(*cols, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cols` | যে কলামগুলোতে খুঁজবে (FULLTEXT ইনডেক্সের কলামগুলো)। |
| `kw` | • `against` (বাধ্যতামূলক): খোঁজার টেক্সট বা এক্সপ্রেশন।<br>• `in_boolean_mode`, `in_natural_language_mode`, `with_query_expansion`: `True` দিলে সেই মোড (নিচের মেথডগুলোর মতো)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #match-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`in_boolean_mode()`](#match-in-boolean-mode) | মেথড | `IN BOOLEAN MODE`: `+শব্দ` (থাকতেই হবে), `-শব্দ` (থাকবে না), `শব্দ*` (শুরু) ইত্যাদি অপারেটর চলে। |
| [`in_natural_language_mode()`](#match-in-natural-language-mode) | মেথড | `IN NATURAL LANGUAGE MODE` (MySQL-এর ডিফল্ট মোড, স্পষ্ট করে লিখতে)। |
| [`with_query_expansion()`](#match-with-query-expansion) | মেথড | `WITH QUERY EXPANSION`: প্রথম ফলের শব্দ দিয়ে আবার খোঁজে (কম শব্দের প্রশ্নে বেশি ফল)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `match`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`BinaryExpression` থেকে:** [`group`](elements.md#binaryexpression-group) · [`is_comparison`](elements.md#binaryexpression-is-comparison)

///

### `match.in_boolean_mode()` { #match-in-boolean-mode }

```python
match.in_boolean_mode()
```

**ধরন:** মেথড

`IN BOOLEAN MODE`: `+শব্দ` (থাকতেই হবে), `-শব্দ` (থাকবে না), `শব্দ*` (শুরু) ইত্যাদি অপারেটর চলে। নতুন `match` অবজেক্ট দেয়।

**উদাহরণ:**

```python
my(select(match(products.c.name, against="+কলম -লাল").in_boolean_mode()))
# SELECT MATCH (products.name) AGAINST ('+কলম -লাল' IN BOOLEAN MODE) AS anon_1
# FROM products
```

### `match.in_natural_language_mode()` { #match-in-natural-language-mode }

```python
match.in_natural_language_mode()
```

**ধরন:** মেথড

`IN NATURAL LANGUAGE MODE` (MySQL-এর ডিফল্ট মোড, স্পষ্ট করে লিখতে)।

**উদাহরণ:**

```python
my(select(match(products.c.name, against="কলম").in_natural_language_mode()))
# SELECT MATCH (products.name) AGAINST ('কলম' IN NATURAL LANGUAGE MODE) AS anon_1
# FROM products
```

### `match.with_query_expansion()` { #match-with-query-expansion }

```python
match.with_query_expansion()
```

**ধরন:** মেথড

`WITH QUERY EXPANSION`: প্রথম ফলের শব্দ দিয়ে আবার খোঁজে (কম শব্দের প্রশ্নে বেশি ফল)।

**উদাহরণ:**

```python
my(select(match(products.c.name, against="কলম").with_query_expansion()))
# SELECT MATCH (products.name) AGAINST ('কলম' WITH QUERY EXPANSION) AS anon_1
# FROM products
```

## পূর্ণসংখ্যার টাইপ { #tinyint-group }

## `TINYINT` { #tinyint }

```python
from sqlalchemy.dialects.mysql import TINYINT
```

১ বাইটের পূর্ণসংখ্যা (−১২৮ থেকে ১২৭, `unsigned=True` হলে ০–২৫৫)। MySQL-এ `BOOL` আসলে `TINYINT(1)`।

**সব MySQL পূর্ণসংখ্যা টাইপের সাধারণ কীওয়ার্ড:** `unsigned=True` → `UNSIGNED` (শুধু ধনাত্মক, সীমা দ্বিগুণ), `zerofill=True` → `ZEROFILL` (`display_width` পর্যন্ত বাঁয়ে শূন্য; MySQL ৮-এ বাতিলের পথে)।

**উদাহরণ:**

```python
print(myt(TINYINT()), "|", myt(TINYINT(unsigned=True)), "|", myt(TINYINT(1)))   # TINYINT | TINYINT UNSIGNED | TINYINT(1)
```

### কনস্ট্রাক্টরের প্যারামিটার { #tinyint-params }

```python
TINYINT(display_width=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ, যেমন `TINYINT(1)` (মান সংরক্ষণে প্রভাব নেই; MySQL ৮.০.১৭+-এ বাতিলের পথে)। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](types.md#integer)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `SMALLINT` { #smallint }

```python
from sqlalchemy.dialects.mysql import SMALLINT
```

২ বাইটের পূর্ণসংখ্যা (−৩২,৭৬৮ থেকে ৩২,৭৬৭)।

**উদাহরণ:**

```python
print(myt(SMALLINT(unsigned=True)))   # SMALLINT UNSIGNED
```

### কনস্ট্রাক্টরের প্যারামিটার { #smallint-params }

```python
SMALLINT(display_width=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`SMALLINT`](types.md#smallint)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `MEDIUMINT` { #mediumint }

```python
from sqlalchemy.dialects.mysql import MEDIUMINT
```

৩ বাইটের পূর্ণসংখ্যা (প্রায় ±৮৪ লাখ), শুধু MySQL/MariaDB-তে আছে।

**উদাহরণ:**

```python
print(myt(MEDIUMINT()))   # MEDIUMINT
```

### কনস্ট্রাক্টরের প্যারামিটার { #mediumint-params }

```python
MEDIUMINT(display_width=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Integer`](types.md#integer)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INTEGER` { #integer }

```python
from sqlalchemy.dialects.mysql import INTEGER
```

৪ বাইটের পূর্ণসংখ্যা। সাধারণ `Integer` MySQL-এ এটাই হয়; `UNSIGNED` বা `ZEROFILL` লাগলে এটা নিন।

**উদাহরণ:**

```python
print(myt(INTEGER(display_width=11, unsigned=True, zerofill=True)))   # INTEGER(11) UNSIGNED ZEROFILL
```

### কনস্ট্রাক্টরের প্যারামিটার { #integer-params }

```python
INTEGER(display_width=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`INTEGER`](types.md#sql-integer)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `BIGINT` { #bigint }

```python
from sqlalchemy.dialects.mysql import BIGINT
```

৮ বাইটের পূর্ণসংখ্যা।

**উদাহরণ:**

```python
print(myt(BIGINT(unsigned=True)))   # BIGINT UNSIGNED
```

### কনস্ট্রাক্টরের প্যারামিটার { #bigint-params }

```python
BIGINT(display_width=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`BIGINT`](types.md#bigint)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `BIT` { #bit }

```python
from sqlalchemy.dialects.mysql import BIT
```

MySQL-এর `BIT(n)` (১–৬৪ বিট)। ডেটাবেস থেকে আসা বাইটগুলো SQLAlchemy **পূর্ণসংখ্যায়** বদলে দেয় (PostgreSQL-এর `BIT`-এর মতো `BitString` নয়)।

**উদাহরণ:**

```python
print(myt(BIT(8)), BIT(8).result_processor(mysql.dialect(), None)(b"\x05"))   # BIT(8) 5
```

### কনস্ট্রাক্টরের প্যারামিটার { #bit-params }

```python
BIT(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | বিটের সংখ্যা (ডিফল্ট ১)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## দশমিক সংখ্যার টাইপ { #decimal-group }

## `DECIMAL` { #decimal }

```python
from sqlalchemy.dialects.mysql import DECIMAL
```

নির্দিষ্ট দশমিকের সংখ্যা (`Decimal`), টাকা-পয়সার জন্য। সাধারণ `Numeric`-এর মতো, সাথে `unsigned`/`zerofill`।

**উদাহরণ:**

```python
print(myt(DECIMAL(10, 2, unsigned=True)))   # DECIMAL(10, 2) UNSIGNED
```

### কনস্ট্রাক্টরের প্যারামিটার { #decimal-params }

```python
DECIMAL(precision=None, scale=None, asdecimal=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্ক। |
| `scale` | দশমিকের পরের অঙ্ক। |
| `asdecimal` | `True` (ডিফল্ট): Python `Decimal` ফেরত। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`NUMERIC`](types.md#sql-numeric)-এর মতো, অর্থাৎ [`Numeric`](types.md#numeric-summary)-এর মতো।

## `NUMERIC` { #numeric }

```python
from sqlalchemy.dialects.mysql import NUMERIC
```

MySQL-এ `DECIMAL`-এর আরেক নাম।

**উদাহরণ:**

```python
print(myt(NUMERIC(10, 2)))   # NUMERIC(10, 2)
```

### কনস্ট্রাক্টরের প্যারামিটার { #numeric-params }

```python
NUMERIC(precision=None, scale=None, asdecimal=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্ক। |
| `scale` | দশমিকের পরের অঙ্ক। |
| `asdecimal` | `True` (ডিফল্ট): `Decimal` ফেরত। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`NUMERIC`](types.md#sql-numeric)-এর মতো, অর্থাৎ [`Numeric`](types.md#numeric-summary)-এর মতো।

## `DOUBLE` { #double }

```python
from sqlalchemy.dialects.mysql import DOUBLE
```

৮ বাইটের floating-point। MySQL-এ `DOUBLE(M, D)` রূপও আছে (বাতিলের পথে)।

**উদাহরণ:**

```python
print(myt(DOUBLE()), "|", myt(DOUBLE(10, 2)))   # DOUBLE | DOUBLE(10, 2)
```

### কনস্ট্রাক্টরের প্যারামিটার { #double-params }

```python
DOUBLE(precision=None, scale=None, asdecimal=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্ক (`scale`-এর সাথে দিতে হয়)। |
| `scale` | দশমিকের পরের অঙ্ক। |
| `asdecimal` | `True` (এখানে ডিফল্ট): `Decimal` ফেরত; `float` চাইলে `False`। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DOUBLE`](types.md#sql-double)-এর মতো, অর্থাৎ [`Numeric`](types.md#numeric-summary)-এর মতো।

## `FLOAT` { #float }

```python
from sqlalchemy.dialects.mysql import FLOAT
```

৪ বাইটের floating-point (`float` ফেরত)।

**উদাহরণ:**

```python
print(myt(FLOAT()), "|", myt(FLOAT(10, 2)))   # FLOAT | FLOAT(10, 2)
```

### কনস্ট্রাক্টরের প্যারামিটার { #float-params }

```python
FLOAT(precision=None, scale=None, asdecimal=False, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্ক। |
| `scale` | দশমিকের পরের অঙ্ক। |
| `asdecimal` | `False` (ডিফল্ট): `float` ফেরত। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`FLOAT`](types.md#sql-float)-এর মতো, অর্থাৎ [`Numeric`](types.md#numeric-summary)-এর মতো।

## `REAL` { #real }

```python
from sqlalchemy.dialects.mysql import REAL
```

MySQL-এ সাধারণত `DOUBLE`-এর আরেক নাম (`REAL_AS_FLOAT` মোড চালু থাকলে `FLOAT`)।

**উদাহরণ:**

```python
print(myt(REAL(10, 2)))   # REAL(10, 2)
```

### কনস্ট্রাক্টরের প্যারামিটার { #real-params }

```python
REAL(precision=None, scale=None, asdecimal=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | মোট অঙ্ক। |
| `scale` | দশমিকের পরের অঙ্ক। |
| `asdecimal` | `True` (এখানে ডিফল্ট): `Decimal` ফেরত। |
| `kw` | `unsigned`, `zerofill`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`REAL`](types.md#real)-এর মতো, অর্থাৎ [`Numeric`](types.md#numeric-summary)-এর মতো।

## স্ট্রিং টাইপ { #varchar-group }

## `VARCHAR` { #varchar }

```python
from sqlalchemy.dialects.mysql import VARCHAR
```

পরিবর্তনশীল দৈর্ঘ্যের স্ট্রিং; **MySQL-এ দৈর্ঘ্য দিতেই হবে** (`String()` দৈর্ঘ্য ছাড়া দিলে `CREATE TABLE`-এ এরর)।

**সব MySQL স্ট্রিং টাইপের সাধারণ কীওয়ার্ড:**

* `charset`: কলামের character set, যেমন `"utf8mb4"` (বাংলা/ইমোজির জন্য এটাই দিন)।
* `collation`: যেমন `"utf8mb4_bin"` (ছোট-বড় হাতের পার্থক্য করে), `"utf8mb4_unicode_ci"`।
* `ascii=True`: `latin1`-এর সংক্ষেপ (`ASCII`); `unicode=True`: `ucs2`-এর সংক্ষেপ (`UNICODE`)।
* `binary=True`: character set-এর binary collation (`BINARY`); ডেটা টাইপ বদলায় না।
* `national=True`: `NATIONAL VARCHAR` (সার্ভারের ডিফল্ট national character set)।

**উদাহরণ:**

```python
print(myt(VARCHAR(50, charset="utf8mb4", collation="utf8mb4_bin")))   # VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
print(myt(VARCHAR(10, binary=True)), "|", myt(String(10)))   # VARCHAR(10) BINARY | VARCHAR(10)
```

### কনস্ট্রাক্টরের প্যারামিটার { #varchar-params }

```python
VARCHAR(length=None, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | সর্বোচ্চ অক্ষর (বাধ্যতামূলক)। |
| `kwargs` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`VARCHAR`](types.md#varchar)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `CHAR` { #char }

```python
from sqlalchemy.dialects.mysql import CHAR
```

নির্দিষ্ট দৈর্ঘ্যের স্ট্রিং (ডান দিকে ফাঁকা দিয়ে পূর্ণ; পড়ার সময় MySQL ফাঁকা কেটে দেয়)।

**উদাহরণ:**

```python
print(myt(CHAR(3, charset="latin1")))   # CHAR(3) CHARACTER SET latin1
```

### কনস্ট্রাক্টরের প্যারামিটার { #char-params }

```python
CHAR(length=None, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য। |
| `kwargs` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CHAR`](types.md#char)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `NCHAR` { #nchar }

```python
from sqlalchemy.dialects.mysql import NCHAR
```

`NATIONAL CHAR(n)`: সার্ভারের national character set-এ নির্দিষ্ট দৈর্ঘ্যের স্ট্রিং।

**উদাহরণ:**

```python
print(myt(NCHAR(5)))   # NATIONAL CHAR(5)
```

### কনস্ট্রাক্টরের প্যারামিটার { #nchar-params }

```python
NCHAR(length=None, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য। |
| `kwargs` | `collation`, `binary` (character set সবসময় national)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`NCHAR`](types.md#nchar)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `NVARCHAR` { #nvarchar }

```python
from sqlalchemy.dialects.mysql import NVARCHAR
```

`NATIONAL VARCHAR(n)`।

**উদাহরণ:**

```python
print(myt(NVARCHAR(10)))   # NATIONAL VARCHAR(10)
```

### কনস্ট্রাক্টরের প্যারামিটার { #nvarchar-params }

```python
NVARCHAR(length=None, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | সর্বোচ্চ দৈর্ঘ্য। |
| `kwargs` | `collation`, `binary`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`NVARCHAR`](types.md#nvarchar)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `TINYTEXT` { #tinytext }

```python
from sqlalchemy.dialects.mysql import TINYTEXT
```

সর্বোচ্চ ২৫৫ বাইটের টেক্সট।

**উদাহরণ:**

```python
print(myt(TINYTEXT()))   # TINYTEXT
```

### কনস্ট্রাক্টরের প্যারামিটার { #tinytext-params }

```python
TINYTEXT(**kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `kwargs` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Text`](types.md#text)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `TEXT` { #text }

```python
from sqlalchemy.dialects.mysql import TEXT
```

সর্বোচ্চ ৬৪ KB-র টেক্সট। `length` দিলে MySQL ঐ দৈর্ঘ্য ধরতে পারে এমন সবচেয়ে ছোট TEXT টাইপ বেছে নেয়।

**উদাহরণ:**

```python
print(myt(TEXT()), "|", myt(TEXT(1000)))   # TEXT | TEXT(1000)
```

### কনস্ট্রাক্টরের প্যারামিটার { #text-params }

```python
TEXT(length=None, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | আনুমানিক সর্বোচ্চ দৈর্ঘ্য (ঐচ্ছিক)। |
| `kw` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TEXT`](types.md#sql-text)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `MEDIUMTEXT` { #mediumtext }

```python
from sqlalchemy.dialects.mysql import MEDIUMTEXT
```

সর্বোচ্চ ১৬ MB-র টেক্সট (লম্বা আর্টিকেল, HTML)।

**উদাহরণ:**

```python
print(myt(MEDIUMTEXT(charset="utf8mb4")))   # MEDIUMTEXT CHARACTER SET utf8mb4
```

### কনস্ট্রাক্টরের প্যারামিটার { #mediumtext-params }

```python
MEDIUMTEXT(**kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `kwargs` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Text`](types.md#text)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `LONGTEXT` { #longtext }

```python
from sqlalchemy.dialects.mysql import LONGTEXT
```

সর্বোচ্চ ৪ GB-র টেক্সট। ORM-এ বড় টেক্সটের জন্য: `mapped_column(Text().with_variant(LONGTEXT, "mysql"))`।

**উদাহরণ:**

```python
print(myt(Text().with_variant(LONGTEXT(), "mysql")))   # LONGTEXT
```

### কনস্ট্রাক্টরের প্যারামিটার { #longtext-params }

```python
LONGTEXT(**kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `kwargs` | `charset`, `collation`, `ascii`, `unicode`, `binary`, `national`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Text`](types.md#text)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## ENUM, SET ও YEAR { #enum-group }

## `ENUM` { #enum }

```python
from sqlalchemy.dialects.mysql import ENUM
```

MySQL-এর কলাম-ভিত্তিক `ENUM('a','b')` (PostgreSQL-এর মতো আলাদা `CREATE TYPE` নেই, তাই `name` লাগে না)। সাধারণ `Enum` MySQL-এ এটাই হয়; সরাসরি নিলে `charset`/`collation` দেওয়া যায়। Python `enum.Enum` ক্লাসও দেওয়া যায়।

**উদাহরণ:**

```python
class Size(enum.Enum):
    S = "small"
    L = "large"
print(myt(ENUM("S", "M", "L")), "|", myt(ENUM(Size)), "|", myt(Enum("a", "b", name="ab")))
# ENUM('S','M','L') | ENUM('S','L') | ENUM('a','b')
```

### কনস্ট্রাক্টরের প্যারামিটার { #enum-params }

```python
ENUM(*enums, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `enums` | অনুমোদিত মানগুলো (স্ট্রিং বা Python enum ক্লাস)। |
| `kw` | `charset`, `collation`, `ascii`, `unicode`, `binary` (স্ট্রিং টাইপের মতো), `strict` (এখন কোনো প্রভাব নেই), আর সাধারণ [`Enum`](types.md#enum-params)-এর প্যারামিটার (`values_callable`, `validate_strings` …)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #enum-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_emulated_to_native()`](#enum-adapt-emulated-to-native) | ক্লাস মেথড (internal) | (ক্লাস মেথড) সাধারণ `Enum` থেকে MySQL `ENUM` বানায়; MySQL ডায়ালেক্ট `Enum` কলাম কম্পাইল করার সময় এটি ব্যবহার হয়। |
| [`adapt_native_to_emulated()`](#enum-adapt-native-to-emulated) | ক্লাস মেথড (internal) | (ক্লাস মেথড) native থেকে emulated টাইপে অভিযোজন; ভেতরের ব্যবহারের জন্য। |
| [`native_enum`](#enum-native-enum) | অ্যাট্রিবিউট | native ENUM কি না: MySQL `ENUM`-এ সবসময় `True`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ENUM`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

**`Boolean` থেকে:** [`adapt_to_emulated()`](types.md#boolean-adapt-to-emulated) · [`create()`](types.md#boolean-create) · [`drop()`](types.md#boolean-drop) · [`inherit_schema`](types.md#boolean-inherit-schema) · [`native`](types.md#boolean-native)

///

### `ENUM.adapt_emulated_to_native()` { #enum-adapt-emulated-to-native }

```python
ENUM.adapt_emulated_to_native(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) সাধারণ `Enum` থেকে MySQL `ENUM` বানায়; MySQL ডায়ালেক্ট `Enum` কলাম কম্পাইল করার সময় এটি ব্যবহার হয়।

**উদাহরণ:**

```python
t = Enum("S", "M", name="size_t").dialect_impl(mysql.dialect())
print(type(t).__module__.split(".")[2], type(t).__name__, t.enums)   # mysql ENUM ['S', 'M']
```

### `ENUM.adapt_native_to_emulated()` { #enum-adapt-native-to-emulated }

```python
ENUM.adapt_native_to_emulated(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) native থেকে emulated টাইপে অভিযোজন; ভেতরের ব্যবহারের জন্য।

**উদাহরণ:**

```python
print(callable(ENUM.adapt_native_to_emulated))   # True
```

### `ENUM.native_enum` { #enum-native-enum }

**ধরন:** অ্যাট্রিবিউট

native ENUM কি না: MySQL `ENUM`-এ সবসময় `True`।

**উদাহরণ:**

```python
print(ENUM("a", "b").native_enum)   # True
```

## `SET` { #set }

```python
from sqlalchemy.dialects.mysql import SET
```

MySQL-এর `SET('a','b','c')`: তালিকা থেকে **শূন্য বা একাধিক** মান একসাথে (যেমন একটি পণ্যের রঙ "লাল,নীল")। Python-এ মান `set` (`{"a", "c"}`); ডেটাবেসে কমা দিয়ে জোড়া স্ট্রিং।

**উদাহরণ:**

```python
tags = SET("a", "b", "c")
print(myt(tags), tags.result_processor(mysql.dialect(), None)("a,c") == {"a", "c"})   # SET('a','b','c') True
```

**retrieve_as_bitwise: সেট → সংখ্যা**

```python
bits = SET("a", "b", "c", retrieve_as_bitwise=True)
print(bits.bind_processor(mysql.dialect())({"a", "c"}))   # 5  (১ + ৪)
```

### কনস্ট্রাক্টরের প্যারামিটার { #set-params }

```python
SET(*values, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `values` | অনুমোদিত মানগুলো। |
| `kw` | • `retrieve_as_bitwise=True`: মান **সংখ্যা** হিসেবে আদান-প্রদান (বিট-মাস্ক: a=১, b=২, c=৪)। ফাঁকা স্ট্রিং মান থাকলে বা নির্ভুলতার জন্য সুপারিশকৃত।<br>• `charset`, `collation`, `ascii`, `unicode`, `binary`। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`String`](types.md#string-summary)-এর মতো।

## `YEAR` { #year }

```python
from sqlalchemy.dialects.mysql import YEAR
```

শুধু বছর (১৯০১–২১৫৫), ১ বাইটে। Python-এ `int`।

**উদাহরণ:**

```python
print(myt(YEAR()), "|", myt(YEAR(4)))   # YEAR | YEAR(4)
```

### কনস্ট্রাক্টরের প্যারামিটার { #year-params }

```python
YEAR(display_width=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `display_width` | প্রদর্শনের প্রস্থ (পুরোনো `YEAR(2)`/`YEAR(4)`; MySQL ৮-এ শুধু ৪)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## তারিখ-সময় ও বাইনারি টাইপ { #datetime-group }

## `DATETIME` { #datetime }

```python
from sqlalchemy.dialects.mysql import DATETIME
```

MySQL `DATETIME`, বাড়তি `fsp` (fractional seconds precision, ০–৬): `DATETIME(6)` দিলে মাইক্রোসেকেন্ড পর্যন্ত থাকে, **না দিলে MySQL সেকেন্ডের ভগ্নাংশ ফেলে দেয়**।

**উদাহরণ:**

```python
print(myt(DATETIME(fsp=6)), "|", myt(DateTime()))   # DATETIME(6) | DATETIME
```

### কনস্ট্রাক্টরের প্যারামিটার { #datetime-params }

```python
DATETIME(timezone=False, fsp=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | MySQL-এ কোনো প্রভাব নেই (DATETIME টাইমজোন রাখে না)। |
| `fsp` | সেকেন্ডের দশমিক অঙ্ক (০–৬)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DATETIME`](types.md#sql-datetime)-এর মতো, অর্থাৎ [`DateTime`](types.md#datetime-summary)-এর মতো।

## `TIMESTAMP` { #timestamp }

```python
from sqlalchemy.dialects.mysql import TIMESTAMP
```

MySQL `TIMESTAMP` (UTC-তে জমা, সংযোগের টাইমজোনে দেখায়; সীমা ২০৩৮ সাল পর্যন্ত), বাড়তি `fsp`।

**উদাহরণ:**

```python
print(myt(TIMESTAMP(fsp=6)))   # TIMESTAMP(6)
```

### কনস্ট্রাক্টরের প্যারামিটার { #timestamp-params }

```python
TIMESTAMP(timezone=False, fsp=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | MySQL-এ কোনো প্রভাব নেই। |
| `fsp` | সেকেন্ডের দশমিক অঙ্ক। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TIMESTAMP`](types.md#timestamp)-এর মতো, অর্থাৎ [`DateTime`](types.md#datetime-summary)-এর মতো।

## `TIME` { #time }

```python
from sqlalchemy.dialects.mysql import TIME
```

MySQL `TIME`, বাড়তি `fsp`। MySQL-এর TIME ২৪ ঘণ্টার বেশিও রাখতে পারে (সময়কাল হিসেবে)।

**উদাহরণ:**

```python
print(myt(TIME(fsp=3)))   # TIME(3)
```

### কনস্ট্রাক্টরের প্যারামিটার { #time-params }

```python
TIME(timezone=False, fsp=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | MySQL-এ কোনো প্রভাব নেই। |
| `fsp` | সেকেন্ডের দশমিক অঙ্ক। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TIME`](types.md#sql-time)-এর মতো, অর্থাৎ [`DateTime`](types.md#datetime-summary)-এর মতো।

## `TINYBLOB` { #tinyblob }

```python
from sqlalchemy.dialects.mysql import TINYBLOB
```

সর্বোচ্চ ২৫৫ বাইটের বাইনারি।

**উদাহরণ:**

```python
print(myt(TINYBLOB()))   # TINYBLOB
```

### কনস্ট্রাক্টরের প্যারামিটার { #tinyblob-params }

```python
TINYBLOB(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য (এখানে উপেক্ষিত)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](types.md#largebinary-summary)-এর মতো।

## `MEDIUMBLOB` { #mediumblob }

```python
from sqlalchemy.dialects.mysql import MEDIUMBLOB
```

সর্বোচ্চ ১৬ MB-র বাইনারি। সাধারণ `LargeBinary` MySQL-এ `BLOB` (৬৪ KB) হয়, তাই বড় ফাইলে এটা বা `LONGBLOB` নিন।

**উদাহরণ:**

```python
print(myt(LargeBinary()), "|", myt(MEDIUMBLOB()))   # BLOB | MEDIUMBLOB
```

### কনস্ট্রাক্টরের প্যারামিটার { #mediumblob-params }

```python
MEDIUMBLOB(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য (এখানে উপেক্ষিত)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](types.md#largebinary-summary)-এর মতো।

## `LONGBLOB` { #longblob }

```python
from sqlalchemy.dialects.mysql import LONGBLOB
```

সর্বোচ্চ ৪ GB-র বাইনারি।

**উদাহরণ:**

```python
print(myt(LONGBLOB()))   # LONGBLOB
```

### কনস্ট্রাক্টরের প্যারামিটার { #longblob-params }

```python
LONGBLOB(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য (এখানে উপেক্ষিত)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](types.md#largebinary-summary)-এর মতো।

## JSON ও MariaDB টাইপ { #json-group }

## `JSON` { #json }

```python
from sqlalchemy.dialects.mysql import JSON
```

MySQL ৫.৭+ / MariaDB ১০.২+-এর `JSON`। সাধারণ `sqlalchemy.JSON` MySQL-এ এটাই হয়, তাই সাধারণত সেটাই ব্যবহার করুন। `col["key"]` SQL-এ হয় `JSON_EXTRACT(col, '$."key"')`।

**উদাহরণ:**

```python
t = Table("docs", MetaData(), Column("id", Integer, primary_key=True), Column("data", JSON))
my(select(t.c.data["name"]))
# SELECT JSON_EXTRACT(docs.data, '$."name"') AS anon_1
# FROM docs
my(select(t.c.data["name"].as_string()))   # JSON null হলে SQL NULL, নইলে উদ্ধৃতি-ছাড়া টেক্সট
# SELECT CASE JSON_EXTRACT(docs.data, '$."name"') WHEN 'null' THEN NULL ELSE JSON_UNQUOTE(JSON_EXTRACT(docs.data, '$."name"')) END AS anon_1
# FROM docs
```

### কনস্ট্রাক্টরের প্যারামিটার { #json-params }

```python
JSON(none_as_null=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `none_as_null` | `True` দিলে Python `None` SQL `NULL` হিসেবে যায় (ডিফল্টে JSON `null`)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`JSON`](types.md#json-summary)-এর মতো।

## `INET4` { #inet4 }

```python
from sqlalchemy.dialects.mysql import INET4
```

(২.০.৩৭) **MariaDB**-র `INET4` টাইপ (১০.১০+): IPv4 ঠিকানা। MySQL-এ নেই।

**উদাহরণ:**

```python
print(INET4().compile(dialect=mysql.dialect(is_mariadb=True)))   # INET4
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INET6` { #inet6 }

```python
from sqlalchemy.dialects.mysql import INET6
```

(২.০.৩৭) **MariaDB**-র `INET6` টাইপ (১০.৫+): IPv6 (আর IPv4) ঠিকানা।

**উদাহরণ:**

```python
print(INET6().compile(dialect=mysql.dialect(is_mariadb=True)))   # INET6
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## ডায়ালেক্ট { #dialect-group }

## `dialect` { #dialect }

```python
from sqlalchemy.dialects.mysql import dialect
```

MySQL-এর ডিফল্ট ডায়ালেক্ট ক্লাস (`mysqlclient` / MySQLdb ড্রাইভার)। SQL কম্পাইল করে দেখতে `stmt.compile(dialect=mysql.dialect())`; MariaDB-র SQL দেখতে `dialect(is_mariadb=True)`। এর সদস্যগুলো সবই SQLAlchemy-র ভেতরের ডায়ালেক্ট-ইন্টারফেস (নতুন ডায়ালেক্ট লেখকদের জন্য), তাই আলাদা তালিকা দেওয়া হয়নি। অন্য ড্রাইভার: `mysql+pymysql://`, `mysql+asyncmy://` (async), `mysql+aiomysql://` (async), `mysql+mysqlconnector://`।

**উদাহরণ:**

```python
d = dialect()
print(d.name, d.driver, dialect(is_mariadb=True).is_mariadb)   # mysql mysqldb True
```

## সাধারণ টাইপ, MySQL মডিউল থেকে { #generic-reexports }

নিচের নামগুলো `from sqlalchemy.dialects.mysql import ...` দিয়েও পাওয়া যায়, কিন্তু এগুলো **হুবহু একই** সাধারণ টাইপ; ব্যাখ্যা [টাইপ পেজে](types.md):

| নাম | কোথায় দেখবেন |
| :--- | :--- |
| `BOOLEAN` | [`BOOLEAN`](types.md#sql-boolean) (MySQL-এ `BOOL`, আসলে `TINYINT(1)`) |
| `DATE` | [`DATE`](types.md#sql-date) |
| `BINARY`, `VARBINARY`, `BLOB` | [`BINARY`](types.md#binary), [`VARBINARY`](types.md#varbinary), [`BLOB`](types.md#blob) |

/// check | সংক্ষেপে মনে রাখুন

* upsert: `from sqlalchemy.dialects.mysql import insert` → `.on_duplicate_key_update(col=stmt.inserted.col)`; যেকোনো unique কনফ্লিক্টে চলে।
* স্ট্রিংয়ে দৈর্ঘ্য দিতেই হবে; বাংলার জন্য `charset="utf8mb4"` (বা সংযোগ URL-এ `?charset=utf8mb4`)।
* মাইক্রোসেকেন্ড রাখতে `DATETIME(fsp=6)`।
* ব্যাচে মুছতে/আপডেটে `.ext(limit(n))` (২.১)।

///
