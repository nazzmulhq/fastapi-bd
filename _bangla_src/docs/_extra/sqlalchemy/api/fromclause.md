# FROM এলিমেন্ট API: FromClause, Join, Alias, TableClause … { #api-fromclause }

/// note | এই পেজে যা আছে

`FROM`-এ বসতে পারে এমন সব কিছুর ক্লাস ও **সব** সদস্য:

* `FromClause` (সবার মূল): `c`, `join()`, `outerjoin()`, `alias()`, `select()`, `lateral()`, `tablesample()`, `primary_key`, `foreign_keys` …
* `Selectable`, `TableClause` (`table()`-এর ফল), `Join`, `Alias`, `Lateral`, `TableSample`, `TableValuedAlias`।
* `ColumnCollection`: `table.c`-এর ক্লাস (`keys()`, `get()`, `contains_column()` …)।

///

`Table`, সাবকুয়েরি, CTE, JOIN, alias: সবাই `FromClause`। তাই `users.join(...)`, `subq.c.name`, `cte.alias()` একইভাবে কাজ করে। ORM মডেলে এগুলো সাধারণত ভেতরে ঘটে (`select(User).join(...)`); Core কোডে সরাসরি ব্যবহার হয়।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[Table API পেজের](schema.md) মতোই `users` (`id`, `name`, `email`, `created_at`) আর `addresses` (`id`, `user_id`, `city`) টেবিল; ডেটা: রহিম (দুটি ঠিকানা: ঢাকা, চট্টগ্রাম), করিম (কোনো ঠিকানা নেই), সুমি (ঢাকা)। `rows(স্টেটমেন্ট)` চালিয়ে রো দেয়। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `FromClause` { #fromclause }

```python
from sqlalchemy.sql.expression import FromClause
```

`SELECT ... FROM`-এর `FROM`-এ বসতে পারে এমন যেকোনো কিছুর মূল ক্লাস: `Table`, `TableClause`, `Join`, `Alias`, `Subquery`, `CTE`, table-valued ফাংশন। সবার একটি কলাম-সংগ্রহ (`.c`) আছে, আর সবাইকে join, alias বা select করা যায়।

**উদাহরণ:**

```python
subq = select(users.c.id, users.c.name).where(users.c.id > 1).subquery("s")
print(all(isinstance(x, FromClause) for x in [users, subq, users.join(addresses)]))   # True
print(rows(select(subq.c.name).order_by(subq.c.id)))                                 # [('করিম',), ('সুমি',)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #fromclause-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`alias()`](#fromclause-alias) | মেথড | ছদ্মনাম (`AS নাম`) দেয়, যাতে একই FROM কুয়েরিতে দুবার ব্যবহার করা যায়। |
| [`c`](#fromclause-c) | প্রপার্টি | `columns`-এর ছোট নাম। |
| [`columns`](#fromclause-columns) | প্রপার্টি | এই FROM-এর কলামগুলোর নামভিত্তিক সংগ্রহ (`ColumnCollection`)। |
| [`corresponding_column()`](#fromclause-corresponding-column) | মেথড | মূল টেবিলের একটি কলাম দিলে, এই FROM (যেমন alias বা সাবকুয়েরি)-এর ভেতরের অনুরূপ কলামটি দেয়। |
| [`description`](#fromclause-description) | প্রপার্টি | ছোট বর্ণনামূলক নাম (টেবিল/alias-এর নাম; JOIN-এ দুই দিকের নাম)। |
| [`entity_namespace`](#fromclause-entity-namespace) | প্রপার্টি (internal) | `filter_by()`-এ নাম দিয়ে কলাম খোঁজার নাম-ভান্ডার (এখানে `c`)। |
| [`exported_columns`](#fromclause-exported-columns) | প্রপার্টি | বাইরে থেকে দেখা যায় এমন কলামের সংগ্রহ (`FromClause`-এ `c`-এর সমান)। |
| [`foreign_keys`](#fromclause-foreign-keys) | প্রপার্টি | এই FROM যেসব `ForeignKey` দিয়ে অন্য টেবিলকে রেফার করে তার সেট। |
| [`is_derived_from()`](#fromclause-is-derived-from) | মেথড | এটি দেওয়া FROM থেকে তৈরি কি না (যেমন alias বা join যার ভেতরে টেবিলটি আছে)। |
| [`join()`](#fromclause-join) | মেথড | আরেকটি FROM-এর সাথে `JOIN` বানায় (`Join` অবজেক্ট)। |
| [`lateral()`](#fromclause-lateral) | মেথড | `LATERAL` alias বানায় (সাধারণত সাবকুয়েরিতে ব্যবহৃত)। |
| [`named_with_column`](#fromclause-named-with-column) | অ্যাট্রিবিউট (internal) | কলামগুলো `নাম.কলাম` রূপে উল্লেখ হবে কি না (টেবিল/alias-এ `True`, JOIN-এ `False`)। |
| [`outerjoin()`](#fromclause-outerjoin) | মেথড | `LEFT OUTER JOIN` (`full=True` দিলে FULL OUTER)। |
| [`primary_key`](#fromclause-primary-key) | প্রপার্টি | primary key কলামগুলোর সংগ্রহ (JOIN-এ দুই দিকের মিলিত রূপ)। |
| [`replace_selectable()`](#fromclause-replace-selectable) | মেথড (internal) | ভেতরের একটি FROM-কে alias দিয়ে বদলে কপি দেয় (পুরোনো adaptation API)। |
| [`schema`](#fromclause-schema) | অ্যাট্রিবিউট | FROM-এর স্কিমা (টেবিলে টেবিলের স্কিমা; অন্যগুলোতে সাধারণত `None`)। |
| [`select()`](#fromclause-select) | মেথড | এই FROM-এর সব কলাম নিয়ে একটি `SELECT` বানায়। |
| [`selectable`](#fromclause-selectable) | প্রপার্টি (internal) | এর selectable রূপ (FROM-এ নিজেকেই দেয়)। |
| [`tablesample()`](#fromclause-tablesample) | মেথড | `TABLESAMPLE` alias: বড় টেবিলের র‍্যান্ডম অংশ থেকে পড়া। |
| [`with_cols()`](#fromclause-with-cols) | মেথড | (২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-এর `.c`-কে একটি `TypedColumns` ক্লাসের টাইপ দেয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FromClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `FromClause.alias()` { #fromclause-alias }

```python
FromClause.alias(name=None, flat=False)
```

**ধরন:** মেথড

ছদ্মনাম (`AS নাম`) দেয়, যাতে একই FROM কুয়েরিতে দুবার ব্যবহার করা যায়। `flat=True` (join-এ) প্রতিটি টেবিলকে আলাদা alias দেয়।

**উদাহরণ:**

```python
a1, a2 = addresses.alias("a1"), addresses.alias("a2")
stmt = (select(users.c.name).join(a1, a1.c.user_id == users.c.id).join(a2, a2.c.user_id == users.c.id)
        .where(a1.c.city == "ঢাকা", a2.c.city == "চট্টগ্রাম"))
print(rows(stmt))   # [('রহিম',)]
```

### `FromClause.c` { #fromclause-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(users.join(addresses).c.addresses_city)   # addresses.city
```

### `FromClause.columns` { #fromclause-columns }

**ধরন:** প্রপার্টি

এই FROM-এর কলামগুলোর নামভিত্তিক সংগ্রহ (`ColumnCollection`)। JOIN-এ নামগুলো `টেবিল_কলাম` রূপে থাকে।

**উদাহরণ:**

```python
print(list(users.join(addresses).columns.keys())[:3])   # ['users_id', 'users_name', 'users_email']
```

### `FromClause.corresponding_column()` { #fromclause-corresponding-column }

```python
FromClause.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

মূল টেবিলের একটি কলাম দিলে, এই FROM (যেমন alias বা সাবকুয়েরি)-এর ভেতরের অনুরূপ কলামটি দেয়। একটি কুয়েরি alias-এ "অনুবাদ" করার সময় কাজে লাগে।

**উদাহরণ:**

```python
a = users.alias("u2")
print(a.corresponding_column(users.c.name))   # u2.name
```

### `FromClause.description` { #fromclause-description }

**ধরন:** প্রপার্টি

ছোট বর্ণনামূলক নাম (টেবিল/alias-এর নাম; JOIN-এ দুই দিকের নাম)।

**উদাহরণ:**

```python
print(users.description, users.alias("u2").description)   # users u2
```

### `FromClause.entity_namespace` { #fromclause-entity-namespace }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`filter_by()`-এ নাম দিয়ে কলাম খোঁজার নাম-ভান্ডার (এখানে `c`)।

### `FromClause.exported_columns` { #fromclause-exported-columns }

**ধরন:** প্রপার্টি

বাইরে থেকে দেখা যায় এমন কলামের সংগ্রহ (`FromClause`-এ `c`-এর সমান)।

**উদাহরণ:**

```python
print(list(users.exported_columns.keys()) == list(users.c.keys()))   # True
```

### `FromClause.foreign_keys` { #fromclause-foreign-keys }

**ধরন:** প্রপার্টি

এই FROM যেসব `ForeignKey` দিয়ে অন্য টেবিলকে রেফার করে তার সেট।

**উদাহরণ:**

```python
print([fk.target_fullname for fk in addresses.foreign_keys])   # ['users.id']
```

### `FromClause.is_derived_from()` { #fromclause-is-derived-from }

```python
FromClause.is_derived_from(fromclause)
```

**ধরন:** মেথড

এটি দেওয়া FROM থেকে তৈরি কি না (যেমন alias বা join যার ভেতরে টেবিলটি আছে)।

**উদাহরণ:**

```python
print(users.alias().is_derived_from(users), users.is_derived_from(addresses))   # True False
```

### `FromClause.join()` { #fromclause-join }

```python
FromClause.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

আরেকটি FROM-এর সাথে `JOIN` বানায় (`Join` অবজেক্ট)। ON শর্ত না দিলে ফরেন কি থেকে বোঝে; `isouter=True` → LEFT OUTER, `full=True` → FULL OUTER।

**উদাহরণ:**

```python
j = users.join(addresses)
print(rows(select(users.c.name, addresses.c.city).select_from(j).order_by(addresses.c.id)))
# [('রহিম', 'ঢাকা'), ('রহিম', 'চট্টগ্রাম'), ('সুমি', 'ঢাকা')]
```

### `FromClause.lateral()` { #fromclause-lateral }

```python
FromClause.lateral(name=None)
```

**ধরন:** মেথড

`LATERAL` alias বানায় (সাধারণত সাবকুয়েরিতে ব্যবহৃত)।

**উদাহরণ:**

```python
lat = select(addresses.c.city).where(addresses.c.user_id == users.c.id).limit(1).lateral("one")
print(rows(select(users.c.name, lat.c.city).join(lat, true()).order_by(users.c.id)))   # [('রহিম', 'ঢাকা'), ('সুমি', 'ঢাকা')]
```

### `FromClause.named_with_column` { #fromclause-named-with-column }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলামগুলো `নাম.কলাম` রূপে উল্লেখ হবে কি না (টেবিল/alias-এ `True`, JOIN-এ `False`)।

### `FromClause.outerjoin()` { #fromclause-outerjoin }

```python
FromClause.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

`LEFT OUTER JOIN` (`full=True` দিলে FULL OUTER)।

**উদাহরণ:**

```python
j = users.outerjoin(addresses)
print(rows(select(users.c.name).select_from(j).where(addresses.c.id.is_(None))))   # [('করিম',)]
```

### `FromClause.primary_key` { #fromclause-primary-key }

**ধরন:** প্রপার্টি

primary key কলামগুলোর সংগ্রহ (JOIN-এ দুই দিকের মিলিত রূপ)।

**উদাহরণ:**

```python
print([c.name for c in users.alias().primary_key])   # ['id']
```

### `FromClause.replace_selectable()` { #fromclause-replace-selectable }

```python
FromClause.replace_selectable(old, alias)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের একটি FROM-কে alias দিয়ে বদলে কপি দেয় (পুরোনো adaptation API)।

### `FromClause.schema` { #fromclause-schema }

**ধরন:** অ্যাট্রিবিউট

FROM-এর স্কিমা (টেবিলে টেবিলের স্কিমা; অন্যগুলোতে সাধারণত `None`)।

**উদাহরণ:**

```python
print(users.schema)   # None
```

### `FromClause.select()` { #fromclause-select }

```python
FromClause.select()
```

**ধরন:** মেথড

এই FROM-এর সব কলাম নিয়ে একটি `SELECT` বানায়।

**উদাহরণ:**

```python
print(rows(users.join(addresses).select().with_only_columns(users.c.name, addresses.c.city).where(addresses.c.id == 2)))
# [('রহিম', 'চট্টগ্রাম')]
```

### `FromClause.selectable` { #fromclause-selectable }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এর selectable রূপ (FROM-এ নিজেকেই দেয়)।

### `FromClause.tablesample()` { #fromclause-tablesample }

```python
FromClause.tablesample(sampling, name=None, seed=None)
```

**ধরন:** মেথড

`TABLESAMPLE` alias: বড় টেবিলের র‍্যান্ডম অংশ থেকে পড়া।

**উদাহরণ:**

```python
s = users.tablesample(func.bernoulli(100), name="s")
print(rows(select(func.count()).select_from(s)))   # [(3,)]
```

### `FromClause.with_cols()` { #fromclause-with-cols }

```python
FromClause.with_cols(type_)
```

**ধরন:** মেথড

(২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-এর `.c`-কে একটি `TypedColumns` ক্লাসের টাইপ দেয়। রানটাইমে নিজেকেই ফেরত দেয়।

**উদাহরণ:**

```python
print(users.with_cols(object) is users)   # True
```

## `Selectable` { #selectable }

```python
from sqlalchemy.sql.expression import Selectable
```

"কলামের সারি দেয়" এমন সব কিছুর আরও সাধারণ মূল ক্লাস: `FromClause`, আর `Select` / `CompoundSelect`-ও (`SelectBase`-এর মাধ্যমে)। এর নিজস্ব নতুন সদস্য নেই।

**উদাহরণ:**

```python
print(isinstance(select(users), Selectable), isinstance(users, Selectable))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #selectable-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Selectable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`description`](#fromclause-description) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable)

///

## `TableClause` { #tableclause }

```python
from sqlalchemy.sql.expression import TableClause
```

`table("নাম", column(...))`-এর ফল: `MetaData` ছাড়া "হালকা" টেবিল (কনস্ট্রেইন্ট, টাইপ-ডিফল্ট ইত্যাদি নেই)। `Table` এরই সাবক্লাস, তাই নিচের সব সদস্য `Table`-এর মতো কাজ করে; Alembic মাইগ্রেশনে ডেটা বদলাতে খুব প্রচলিত।

**উদাহরণ:**

```python
u = table("users", column("id"), column("name"))
print(type(u).__name__, rows(select(u.c.name).where(u.c.id == 3)))   # TableClause [('সুমি',)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tableclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TableClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`alias()`](schema.md#table-alias) · [`append_column()`](schema.md#table-append-column) · [`c`](schema.md#table-c) · [`columns`](schema.md#table-columns) · [`delete()`](schema.md#table-delete) · [`description`](schema.md#table-description) · [`foreign_keys`](schema.md#table-foreign-keys) · [`fullname`](schema.md#table-fullname) · [`implicit_returning`](schema.md#table-implicit-returning) · [`insert()`](schema.md#table-insert) · [`insert_column()`](schema.md#table-insert-column) · [`join()`](schema.md#table-join) · [`name`](schema.md#table-name) · [`outerjoin()`](schema.md#table-outerjoin) · [`primary_key`](schema.md#table-primary-key) · [`schema`](schema.md#table-schema) · [`select()`](schema.md#table-select) · [`table_valued()`](schema.md#table-table-valued) · [`update()`](schema.md#table-update)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

///

## `Join` { #join }

```python
from sqlalchemy.sql.expression import Join
```

`a.join(b)` / `join(a, b)`-এর ফল: দুটি FROM আর তাদের ON শর্ত। নিজেও একটি FROM, তাই আরও join চেইন করা যায়: `users.join(addresses).join(orders)`।

**উদাহরণ:**

```python
j = users.join(addresses)
print(type(j).__name__, j.onclause)   # Join users.id = addresses.user_id
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #join-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`full`](#join-full) | অ্যাট্রিবিউট | FULL OUTER JOIN কি না। |
| [`isouter`](#join-isouter) | অ্যাট্রিবিউট | OUTER JOIN কি না। |
| [`left`](#join-left) | অ্যাট্রিবিউট | বাম দিকের FROM। |
| [`onclause`](#join-onclause) | অ্যাট্রিবিউট | ON শর্ত। |
| [`right`](#join-right) | অ্যাট্রিবিউট | ডান দিকের FROM। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Join`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FromClause` থেকে:** [`alias()`](#fromclause-alias) · [`c`](#fromclause-c) · [`columns`](#fromclause-columns) · [`corresponding_column()`](#fromclause-corresponding-column) · [`description`](#fromclause-description) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`foreign_keys`](#fromclause-foreign-keys) · [`is_derived_from()`](#fromclause-is-derived-from) · [`join()`](#fromclause-join) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`outerjoin()`](#fromclause-outerjoin) · [`primary_key`](#fromclause-primary-key) · [`replace_selectable()`](#fromclause-replace-selectable) · [`schema`](#fromclause-schema) · [`select()`](#fromclause-select) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `Join.full` { #join-full }

**ধরন:** অ্যাট্রিবিউট

FULL OUTER JOIN কি না।

**উদাহরণ:**

```python
print(users.join(addresses, full=True).full)   # True
```

### `Join.isouter` { #join-isouter }

**ধরন:** অ্যাট্রিবিউট

OUTER JOIN কি না।

**উদাহরণ:**

```python
print(users.outerjoin(addresses).isouter)   # True
```

### `Join.left` { #join-left }

**ধরন:** অ্যাট্রিবিউট

বাম দিকের FROM।

**উদাহরণ:**

```python
print(users.join(addresses).left.name)   # users
```

### `Join.onclause` { #join-onclause }

**ধরন:** অ্যাট্রিবিউট

ON শর্ত।

**উদাহরণ:**

```python
print(users.join(addresses, users.c.id == addresses.c.user_id).onclause)   # users.id = addresses.user_id
```

### `Join.right` { #join-right }

**ধরন:** অ্যাট্রিবিউট

ডান দিকের FROM।

**উদাহরণ:**

```python
print(users.join(addresses).right.name)   # addresses
```

## `Alias` { #alias }

```python
from sqlalchemy.sql.expression import Alias
```

`table.alias("নাম")`-এর ফল: একটি FROM-এর নামযুক্ত রূপ (`users AS u2`)। কলামগুলো `u2.c.name` রূপে পাওয়া যায়।

**উদাহরণ:**

```python
u2 = users.alias("u2")
print(type(u2).__name__, select(u2.c.name).where(u2.c.id == 1))   # Alias SELECT u2.name FROM users AS u2 WHERE u2.id = :id_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #alias-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`element`](#alias-element) | অ্যাট্রিবিউট | যে মূল FROM-এর alias। |
| [`name`](#alias-name) | অ্যাট্রিবিউট | alias-এর নাম। |
| [`original`](#alias-original) | প্রপার্টি (legacy) | পুরোনো ডায়ালেক্টের জন্য রাখা: alias-এর মূল FROM (`element`-এর মতো)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Alias`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`alias()`](schema.md#table-alias) · [`c`](schema.md#table-c) · [`columns`](schema.md#table-columns) · [`description`](schema.md#table-description) · [`foreign_keys`](schema.md#table-foreign-keys) · [`implicit_returning`](schema.md#table-implicit-returning) · [`join()`](schema.md#table-join) · [`outerjoin()`](schema.md#table-outerjoin) · [`primary_key`](schema.md#table-primary-key) · [`schema`](schema.md#table-schema) · [`select()`](schema.md#table-select) · [`table_valued()`](schema.md#table-table-valued)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

///

### `Alias.element` { #alias-element }

**ধরন:** অ্যাট্রিবিউট

যে মূল FROM-এর alias।

**উদাহরণ:**

```python
print(users.alias("u2").element.name)   # users
```

### `Alias.name` { #alias-name }

**ধরন:** অ্যাট্রিবিউট

alias-এর নাম।

**উদাহরণ:**

```python
print(users.alias("u2").name)   # u2
```

### `Alias.original` { #alias-original }

**ধরন:** প্রপার্টি

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো ডায়ালেক্টের জন্য রাখা: alias-এর মূল FROM (`element`-এর মতো)।

**উদাহরণ:**

```python
print(users.alias("u2").original is users)   # True
```

## `Lateral` { #lateral }

```python
from sqlalchemy.sql.expression import Lateral
```

`lateral()` / `.lateral()`-এর ফল: `LATERAL (SELECT ...) AS নাম`। বাইরের কুয়েরির আগের FROM-এর কলাম ভেতরে ব্যবহার করা যায়। নিজস্ব নতুন সদস্য নেই; সব `Alias`-এর মতো।

**উদাহরণ:**

```python
lat = lateral(select(addresses.c.city).where(addresses.c.user_id == users.c.id).order_by(addresses.c.id.desc()).limit(1), name="last")
print(type(lat).__name__, rows(select(users.c.name, lat.c.city).join(lat, true()).order_by(users.c.id)))
# Lateral [('রহিম', 'চট্টগ্রাম'), ('সুমি', 'ঢাকা')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #lateral-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Lateral`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`alias()`](schema.md#table-alias) · [`c`](schema.md#table-c) · [`columns`](schema.md#table-columns) · [`description`](schema.md#table-description) · [`foreign_keys`](schema.md#table-foreign-keys) · [`implicit_returning`](schema.md#table-implicit-returning) · [`join()`](schema.md#table-join) · [`outerjoin()`](schema.md#table-outerjoin) · [`primary_key`](schema.md#table-primary-key) · [`schema`](schema.md#table-schema) · [`select()`](schema.md#table-select) · [`table_valued()`](schema.md#table-table-valued)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

**`Alias` থেকে:** [`element`](#alias-element) · [`name`](#alias-name) · [`original`](#alias-original)

///

## `TableSample` { #tablesample }

```python
from sqlalchemy.sql.expression import TableSample
```

`tablesample()` / `.tablesample()`-এর ফল: `টেবিল AS নাম TABLESAMPLE পদ্ধতি(শতাংশ) REPEATABLE (seed)`।

**উদাহরণ:**

```python
s = tablesample(users, func.system(100), name="s")
print(type(s).__name__, rows(select(func.count()).select_from(s)))   # TableSample [(3,)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tablesample-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`sampling`](#tablesample-sampling) | অ্যাট্রিবিউট | নমুনার শতাংশ বা নমুনা-পদ্ধতির ফাংশন। |
| [`seed`](#tablesample-seed) | অ্যাট্রিবিউট | `REPEATABLE`-এর seed (না দিলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TableSample`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`alias()`](schema.md#table-alias) · [`c`](schema.md#table-c) · [`columns`](schema.md#table-columns) · [`description`](schema.md#table-description) · [`foreign_keys`](schema.md#table-foreign-keys) · [`implicit_returning`](schema.md#table-implicit-returning) · [`join()`](schema.md#table-join) · [`outerjoin()`](schema.md#table-outerjoin) · [`primary_key`](schema.md#table-primary-key) · [`schema`](schema.md#table-schema) · [`select()`](schema.md#table-select) · [`table_valued()`](schema.md#table-table-valued)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

**`Alias` থেকে:** [`element`](#alias-element) · [`name`](#alias-name) · [`original`](#alias-original)

///

### `TableSample.sampling` { #tablesample-sampling }

**ধরন:** অ্যাট্রিবিউট

নমুনার শতাংশ বা নমুনা-পদ্ধতির ফাংশন।

**উদাহরণ:**

```python
print(users.tablesample(10).sampling)   # system(:system_1)
```

### `TableSample.seed` { #tablesample-seed }

**ধরন:** অ্যাট্রিবিউট

`REPEATABLE`-এর seed (না দিলে `None`)।

**উদাহরণ:**

```python
print(users.tablesample(10, seed=42).seed)   # 42
```

## `TableValuedAlias` { #tablevaluedalias }

```python
from sqlalchemy.sql.expression import TableValuedAlias
```

`func.xxx().table_valued(...)`-এর ফল: যে SQL ফাংশন একাধিক রো/কলাম দেয় (`generate_series`, `json_each`, `unnest`), তাকে FROM হিসেবে ব্যবহারের রূপ।

**উদাহরণ:**

```python
gs = func.generate_series(1, 3).table_valued("n").render_derived()
print(type(gs).__name__, rows(select(gs.c.n)))   # TableValuedAlias [(1,), (2,), (3,)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tablevaluedalias-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`column`](#tablevaluedalias-column) | প্রপার্টি | পুরো table-valued মানটিকে একটি কলাম হিসেবে দেয় (প্রতিটি রো একটি মান)। |
| [`joins_implicitly`](#tablevaluedalias-joins-implicitly) | অ্যাট্রিবিউট | `True` হলে এই ফাংশন অন্য টেবিলের সাথে স্পষ্ট JOIN ছাড়াই FROM-এ থাকতে পারে, "cartesian product" সতর্কবার্তা ছাড়া (যেমন `json_each(t.data)`)। |
| [`render_derived()`](#tablevaluedalias-render-derived) | মেথড | alias-এর পরে কলামের নাম (আর `with_types=True` দিলে টাইপও) SQL-এ বসায়: `AS anon_1(n)` বা `AS x(a INTEGER, b TEXT)`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TableValuedAlias`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`alias()`](schema.md#table-alias) · [`c`](schema.md#table-c) · [`columns`](schema.md#table-columns) · [`description`](schema.md#table-description) · [`foreign_keys`](schema.md#table-foreign-keys) · [`implicit_returning`](schema.md#table-implicit-returning) · [`join()`](schema.md#table-join) · [`outerjoin()`](schema.md#table-outerjoin) · [`primary_key`](schema.md#table-primary-key) · [`schema`](schema.md#table-schema) · [`select()`](schema.md#table-select) · [`table_valued()`](schema.md#table-table-valued)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](#fromclause-corresponding-column) · [`entity_namespace`](#fromclause-entity-namespace) · [`exported_columns`](#fromclause-exported-columns) · [`is_derived_from()`](#fromclause-is-derived-from) · [`lateral()`](#fromclause-lateral) · [`named_with_column`](#fromclause-named-with-column) · [`replace_selectable()`](#fromclause-replace-selectable) · [`selectable`](#fromclause-selectable) · [`tablesample()`](#fromclause-tablesample) · [`with_cols()`](#fromclause-with-cols)

**`Alias` থেকে:** [`element`](#alias-element) · [`name`](#alias-name) · [`original`](#alias-original)

///

### `TableValuedAlias.column` { #tablevaluedalias-column }

**ধরন:** প্রপার্টি

পুরো table-valued মানটিকে একটি কলাম হিসেবে দেয় (প্রতিটি রো একটি মান)।

**উদাহরণ:**

```python
gs = func.generate_series(1, 3).table_valued("n")
print([r[0] for r in rows(select(gs.column))])   # [1, 2, 3]
```

### `TableValuedAlias.joins_implicitly` { #tablevaluedalias-joins-implicitly }

**ধরন:** অ্যাট্রিবিউট

`True` হলে এই ফাংশন অন্য টেবিলের সাথে স্পষ্ট JOIN ছাড়াই FROM-এ থাকতে পারে, "cartesian product" সতর্কবার্তা ছাড়া (যেমন `json_each(t.data)`)।

**উদাহরণ:**

```python
print(func.generate_series(1, 2).table_valued("n", joins_implicitly=True).joins_implicitly)   # True
```

### `TableValuedAlias.render_derived()` { #tablevaluedalias-render-derived }

```python
TableValuedAlias.render_derived(name=None, with_types=False)
```

**ধরন:** মেথড

alias-এর পরে কলামের নাম (আর `with_types=True` দিলে টাইপও) SQL-এ বসায়: `AS anon_1(n)` বা `AS x(a INTEGER, b TEXT)`। PostgreSQL-এ রেকর্ড-ফেরত ফাংশনে প্রায়ই দরকার।

**উদাহরণ:**

```python
gs = func.generate_series(1, 2).table_valued("n").render_derived(name="g")
print(select(gs.c.n))   # SELECT g.n FROM generate_series(:generate_series_1, :generate_series_2) AS g(n)
```

## `ColumnCollection` { #columncollection }

```python
from sqlalchemy.sql.expression import ColumnCollection
```

`table.c` / `subquery.c`-এর ক্লাস: কলামগুলোর একটি ক্রমযুক্ত, নামভিত্তিক সংগ্রহ। অ্যাট্রিবিউট (`c.name`), key (`c["name"]`) বা index (`c[0]`) দিয়ে পাওয়া যায়; `in` দিয়ে নাম যাচাই; লুপে কলাম অবজেক্ট আসে।

**উদাহরণ:**

```python
cc = users.c
print(cc.name is cc["name"] is cc[1], "email" in cc, len(cc))   # True True 4
print([c.name for c in cc if c.nullable])                      # ['email', 'created_at']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columncollection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`compare()`](#columncollection-compare) | মেথড | অন্য একটি সংগ্রহের সাথে key আর কলাম অবজেক্ট হুবহু এক কি না তুলনা করে। |
| [`contains_column()`](#columncollection-contains-column) | মেথড | নির্দিষ্ট **কলাম অবজেক্টটি** এই সংগ্রহে আছে কি না (`in` নাম যাচাই করে, এটি অবজেক্ট)। |
| [`corresponding_column()`](#columncollection-corresponding-column) | মেথড | একটি কলাম দিলে এই সংগ্রহের অনুরূপ কলাম দেয় (alias/সাবকুয়েরিতে মূল কলামের প্রতিরূপ খুঁজতে)। |
| [`get()`](#columncollection-get) | মেথড | নাম দিয়ে কলাম; না থাকলে `default` (dict-এর `get()`-এর মতো)। |
| [`items()`](#columncollection-items) | মেথড | `(নাম, কলাম)` জোড়ার তালিকা। |
| [`keys()`](#columncollection-keys) | মেথড | কলামের নামগুলোর তালিকা। |
| [`values()`](#columncollection-values) | মেথড | কলাম অবজেক্টগুলোর তালিকা। |

### `ColumnCollection.compare()` { #columncollection-compare }

```python
ColumnCollection.compare(other)
```

**ধরন:** মেথড

অন্য একটি সংগ্রহের সাথে key আর কলাম অবজেক্ট হুবহু এক কি না তুলনা করে।

**উদাহরণ:**

```python
print(users.c.compare(users.c), users.c.compare(addresses.c))   # True False
```

### `ColumnCollection.contains_column()` { #columncollection-contains-column }

```python
ColumnCollection.contains_column(col)
```

**ধরন:** মেথড

নির্দিষ্ট **কলাম অবজেক্টটি** এই সংগ্রহে আছে কি না (`in` নাম যাচাই করে, এটি অবজেক্ট)।

**উদাহরণ:**

```python
print(users.c.contains_column(users.c.id), users.c.contains_column(addresses.c.id))   # True False
```

### `ColumnCollection.corresponding_column()` { #columncollection-corresponding-column }

```python
ColumnCollection.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

একটি কলাম দিলে এই সংগ্রহের অনুরূপ কলাম দেয় (alias/সাবকুয়েরিতে মূল কলামের প্রতিরূপ খুঁজতে)।

**উদাহরণ:**

```python
s = select(users).subquery("s")
print(s.c.corresponding_column(users.c.email))   # s.email
```

### `ColumnCollection.get()` { #columncollection-get }

```python
ColumnCollection.get(key, default=None)
```

**ধরন:** মেথড

নাম দিয়ে কলাম; না থাকলে `default` (dict-এর `get()`-এর মতো)।

**উদাহরণ:**

```python
print(users.c.get("name"), users.c.get("phone", "নেই"))   # users.name নেই
```

### `ColumnCollection.items()` { #columncollection-items }

```python
ColumnCollection.items()
```

**ধরন:** মেথড

`(নাম, কলাম)` জোড়ার তালিকা।

**উদাহরণ:**

```python
print([k for k, c in addresses.c.items()])   # ['id', 'user_id', 'city']
```

### `ColumnCollection.keys()` { #columncollection-keys }

```python
ColumnCollection.keys()
```

**ধরন:** মেথড

কলামের নামগুলোর তালিকা।

**উদাহরণ:**

```python
print(addresses.c.keys())   # ['id', 'user_id', 'city']
```

### `ColumnCollection.values()` { #columncollection-values }

```python
ColumnCollection.values()
```

**ধরন:** মেথড

কলাম অবজেক্টগুলোর তালিকা।

**উদাহরণ:**

```python
print([str(c.type) for c in addresses.c.values()])   # ['INTEGER', 'INTEGER', 'VARCHAR(50)']
```

/// check | সংক্ষেপে মনে রাখুন

* যেকোনো FROM-এর কলাম: `.c.নাম`; সাবকুয়েরিতেও একই।
* JOIN: `a.join(b)` (ON নিজে থেকে ফরেন কি থেকে), LEFT: `a.outerjoin(b)`।
* একই টেবিল দুবার: `t.alias("x")`।
* alias/সাবকুয়েরিতে মূল কলামের প্রতিরূপ: `.corresponding_column(col)`।
* MetaData ছাড়া দ্রুত টেবিল: `table("নাম", column("a"), ...)`।

///
