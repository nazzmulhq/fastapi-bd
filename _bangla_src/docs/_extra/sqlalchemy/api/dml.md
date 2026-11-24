# Insert, Update, Delete ও text() API { #api-dml }

/// note | এই পেজে যা আছে

* `insert()`, `update()`, `delete()` আর `Insert`, `Update`, `Delete`-এর **প্রতিটি** মেথড।
* raw SQL লেখার জন্য `text()`, `TextClause` আর `TextualSelect`।
* ২.১-এ নতুন: `Delete.using()`।

///

এগুলোকে বলে **DML** (Data Manipulation Language): ডেটা ঢোকানো, বদলানো, মোছা। একটি একটি অবজেক্ট নিয়ে কাজ করলে `session.add()` / অ্যাট্রিবিউট বদল / `session.delete()` সহজ; কিন্তু অনেক রো একসাথে বদলাতে বা `RETURNING` চাইলে এই স্টেটমেন্টগুলো দ্রুত ও শক্তিশালী। ব্যবহারের ধরন শিখতে দেখুন [CRUD ১](../crud.md) ও [CRUD ২](../crud-update-delete.md)।

`select()`-এর মতো এগুলোও অপরিবর্তনীয়: প্রতিটি মেথড নতুন স্টেটমেন্ট দেয়। `compile()`, `params()`, `cte()`, `execution_options()`, `prefix_with()`-এর মতো সাধারণ মেথডগুলোর কাজ [Select API](select.md)-তে যেমন, এখানেও তেমন; সেগুলোর ব্যাখ্যা সেখানে লিংক করা।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[Session API পেজের](session.md) মতোই `User` / `Address` মডেল আর তিনজন ইউজার (রহিম, করিম, সুমি; রহিমের দুটি ঠিকানা)। উদাহরণগুলো PostgreSQL 16-এ চালিয়ে দেখা।

///

## `insert()` { #insert }

```python
from sqlalchemy import insert
```

```python
insert(table)
```

**ধরন:** ফাংশন

একটি `INSERT` স্টেটমেন্ট বানায়। লক্ষ্য হিসেবে মডেল (`User`) বা টেবিল দিন। মান দেওয়ার দুই উপায়: `.values(...)`, অথবা চালানোর সময় dict / dict-এর তালিকা (বাল্ক insert, সবচেয়ে দ্রুত)।

**উদাহরণ:**

```python
session.execute(insert(User).values(name="তানিয়া"))
session.execute(insert(User), [{"name": "অনু"}, {"name": "বিনু"}])      # বাল্ক
session.commit()
print(session.scalar(select(func.count()).select_from(User)))      # 6
```

## `Insert` { #insert }

```python
from sqlalchemy import Insert
```

`insert()` থেকে পাওয়া স্টেটমেন্ট। ORM মডেল দিয়ে বানালে Python-side `default` প্রয়োগ হয়, আর `returning(User)` দিলে পুরো ORM অবজেক্টই ফেরত আসে।

**উদাহরণ:**

```python
users = session.scalars(insert(User).returning(User), [{"name": "ক"}, {"name": "খ"}]).all()
print([(u.id, u.name) for u in users])   # [(4, 'ক'), (5, 'খ')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #insert-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_cte()`](#insert-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`allows_lambda`](#insert-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`apply_syntax_extension_point()`](#insert-apply-syntax-extension-point) | মেথড | (২.১-এ নতুন) কাস্টম SQL syntax extension বানানোর সময় extension নিজে এটি ডাকে, স্টেটমেন্টের নির্দিষ্ট জায়গায় (যেমন WHERE-এর পরে) নিজেকে বসাতে। |
| [`argument_for()`](#insert-argument-for) | ক্লাস মেথড | এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। |
| [`compare()`](#insert-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#insert-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#insert-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#insert-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#insert-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`dialect_kwargs`](#insert-dialect-kwargs) | প্রপার্টি | এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। |
| [`dialect_options`](#insert-dialect-options) | প্রপার্টি | `dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ। |
| [`entity_description`](#insert-entity-description) | প্রপার্টি | স্টেটমেন্টটি কোন মডেল/টেবিলের ওপর কাজ করছে তার বিবরণ (dict: `name`, `type`, `entity`, `table` …)। |
| [`entity_namespace`](#insert-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#insert-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exported_columns`](#insert-exported-columns) | প্রপার্টি | DML-এ এটি `RETURNING` কলামগুলোর সংগ্রহ (`returning()` না দিলে খালি)। |
| [`ext()`](#insert-ext) | মেথড | (২.১-এ নতুন) ডেটাবেস-নির্দিষ্ট একটি SQL syntax extension যুক্ত করে, যেমন PostgreSQL-এর `DISTINCT ON`। |
| [`from_select()`](#insert-from-select) | মেথড | `INSERT INTO টেবিল (কলাম...) SELECT ...` বানায়: একটি SELECT-এর ফলাফল সরাসরি টেবিলে ঢোকায়, Python-এ না এনে। |
| [`get_children()`](#insert-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_dialect_option()`](#insert-get-dialect-option) | মেথড | একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। |
| [`get_execution_options()`](#insert-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`include_insert_from_select_defaults`](#insert-include-insert-from-select-defaults) | অ্যাট্রিবিউট (internal) | `from_select(include_defaults=...)`-এ দেওয়া মান রাখার ভেতরের ফ্ল্যাগ। |
| [`inherit_cache`](#insert-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`inline()`](#insert-inline) | মেথড | INSERT-কে "inline" করে: SQL-এ তৈরি default মান আগে থেকে আনার (pre-execute বা RETURNING) চেষ্টা করে না, সব একটি স্টেটমেন্টে যায়। |
| [`is_clause_element`](#insert-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#insert-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#insert-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#insert-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#insert-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#insert-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#insert-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#insert-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#insert-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#insert-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`kwargs`](#insert-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`memoized_attribute`](#insert-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#insert-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#insert-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`named_with_column`](#insert-named-with-column) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্টের নাম কলামের আগে বসে কি না (DML-এ `False`)। |
| [`options()`](#insert-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`params()`](#insert-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`prefix_with()`](#insert-prefix-with) | মেথড | `SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। |
| [`reflect_only_elements`](#insert-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। |
| [`return_defaults()`](#insert-return-defaults) | মেথড | ডেটাবেস যে মানগুলো নিজে বানায় (server default, auto-increment id) সেগুলো `RETURNING` দিয়ে আনে, পরে `result.returned_defaults` দিয়ে পাওয়া যায়। |
| [`returning()`](#insert-returning) | মেথড | `RETURNING` যোগ করে: insert/update/delete হওয়া রো-গুলোর কলাম (বা ORM অবজেক্ট) সাথে সাথে ফেরত আসে, আলাদা SELECT ছাড়াই। |
| [`returning_column_descriptions`](#insert-returning-column-descriptions) | প্রপার্টি | `returning()`-এ দেওয়া কলামগুলোর বিবরণ (নাম, টাইপ, কোন মডেলের)। |
| [`select`](#insert-select) | অ্যাট্রিবিউট (internal) | `from_select()` দিলে সেই SELECT এখানে রাখা হয়; নইলে `None`। |
| [`selectable`](#insert-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#insert-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#insert-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`supports_execution`](#insert-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`unique_params()`](#insert-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#insert-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`values()`](#insert-values) | মেথড | INSERT-এর মান ঠিক করে: keyword (`name="x"`), dict, বা একাধিক রো-র জন্য dict-এর তালিকা (এক স্টেটমেন্টে বহু-রো `VALUES (...), (...)`)। |
| [`with_dialect_options()`](#insert-with-dialect-options) | মেথড | INSERT/UPDATE/DELETE-এ ডেটাবেস-নির্দিষ্ট অপশন যোগ করে, যেমন MySQL-এ `mysql_limit=10` (UPDATE/DELETE-এ `LIMIT`)। |
| [`with_hint()`](#insert-with-hint) | মেথড | নির্দিষ্ট একটি টেবিলের জন্য ডেটাবেস-নির্দিষ্ট hint (যেমন Oracle/MySQL-এর index hint) যোগ করে। |

### `Insert.add_cte()` { #insert-add-cte }

```python
Insert.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](select.md#select-add-cte)-এর মতো।

### `Insert.allows_lambda` { #insert-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](select.md#select-allows-lambda)-এর মতো।

### `Insert.apply_syntax_extension_point()` { #insert-apply-syntax-extension-point }

```python
Insert.apply_syntax_extension_point(apply_fn, position)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.apply_syntax_extension_point`](select.md#select-apply-syntax-extension-point)-এর মতো।

### `Insert.argument_for()` { #insert-argument-for }

```python
Insert.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.argument_for`](select.md#select-argument-for)-এর মতো।

### `Insert.compare()` { #insert-compare }

```python
Insert.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](select.md#select-compare)-এর মতো।

### `Insert.compile()` { #insert-compile }

```python
Insert.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](select.md#select-compile)-এর মতো।

### `Insert.corresponding_column()` { #insert-corresponding-column }

```python
Insert.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](select.md#select-corresponding-column)-এর মতো।

### `Insert.cte()` { #insert-cte }

```python
Insert.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](select.md#select-cte)-এর মতো।

### `Insert.description` { #insert-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](select.md#select-description)-এর মতো।

### `Insert.dialect_kwargs` { #insert-dialect-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_kwargs`](select.md#select-dialect-kwargs)-এর মতো।

### `Insert.dialect_options` { #insert-dialect-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_options`](select.md#select-dialect-options)-এর মতো।

### `Insert.entity_description` { #insert-entity-description }

**ধরন:** প্রপার্টি

স্টেটমেন্টটি কোন মডেল/টেবিলের ওপর কাজ করছে তার বিবরণ (dict: `name`, `type`, `entity`, `table` …)। event hook-এ বা ডিবাগিংয়ে কাজে লাগে। INSERT/UPDATE/DELETE সবগুলোতে আছে।

**উদাহরণ:**

```python
d = insert(User).entity_description
print(d["name"], d["table"].name)   # User users
```

### `Insert.entity_namespace` { #insert-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](select.md#select-entity-namespace)-এর মতো।

### `Insert.execution_options()` { #insert-execution-options }

```python
Insert.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](select.md#select-execution-options)-এর মতো।

### `Insert.exported_columns` { #insert-exported-columns }

**ধরন:** প্রপার্টি

DML-এ এটি `RETURNING` কলামগুলোর সংগ্রহ (`returning()` না দিলে খালি)। এই স্টেটমেন্ট CTE বা সাবকুয়েরি হিসেবে ব্যবহার করলে কোন কলাম পাওয়া যাবে, তা এখান থেকেই আসে।

**উদাহরণ:**

```python
stmt = insert(User).returning(User.id, User.name)
print(list(stmt.exported_columns.keys()))   # ['id', 'name']
```

### `Insert.ext()` { #insert-ext }

```python
Insert.ext(extension)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.ext`](select.md#select-ext)-এর মতো।

### `Insert.from_select()` { #insert-from-select }

```python
Insert.from_select(names, select, include_defaults=True)
```

**ধরন:** মেথড

`INSERT INTO টেবিল (কলাম...) SELECT ...` বানায়: একটি SELECT-এর ফলাফল সরাসরি টেবিলে ঢোকায়, Python-এ না এনে। `include_defaults=False` দিলে Python-side default কলামগুলো যোগ হয় না।

**উদাহরণ:**

```python
copy = select(func.concat(User.name, "-কপি")).where(User.id == 1)
session.execute(insert(User).from_select(["name"], copy))
session.commit()
print(session.scalars(select(User.name).where(User.id == 4)).one())   # রহিম-কপি
```

### `Insert.get_children()` { #insert-get-children }

```python
Insert.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](select.md#select-get-children)-এর মতো।

### `Insert.get_dialect_option()` { #insert-get-dialect-option }

```python
Insert.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_dialect_option`](select.md#select-get-dialect-option)-এর মতো।

### `Insert.get_execution_options()` { #insert-get-execution-options }

```python
Insert.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](select.md#select-get-execution-options)-এর মতো।

### `Insert.include_insert_from_select_defaults` { #insert-include-insert-from-select-defaults }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`from_select(include_defaults=...)`-এ দেওয়া মান রাখার ভেতরের ফ্ল্যাগ।

### `Insert.inherit_cache` { #insert-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](select.md#select-inherit-cache)-এর মতো।

### `Insert.inline()` { #insert-inline }

```python
Insert.inline()
```

**ধরন:** মেথড

INSERT-কে "inline" করে: SQL-এ তৈরি default মান আগে থেকে আনার (pre-execute বা RETURNING) চেষ্টা করে না, সব একটি স্টেটমেন্টে যায়। অনেক রো-র executemany-তে কাজে লাগে।

**উদাহরণ:**

```python
session.execute(insert(User).inline(), [{"name": "ইনলাইন"}])
session.commit()
```

### `Insert.is_clause_element` { #insert-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](select.md#select-is-clause-element)-এর মতো।

### `Insert.is_delete` { #insert-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](select.md#select-is-delete)-এর মতো।

### `Insert.is_derived_from()` { #insert-is-derived-from }

```python
Insert.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](select.md#select-is-derived-from)-এর মতো।

### `Insert.is_dml` { #insert-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](select.md#select-is-dml)-এর মতো।

### `Insert.is_from_statement` { #insert-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](select.md#select-is-from-statement)-এর মতো।

### `Insert.is_insert` { #insert-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](select.md#select-is-insert)-এর মতো।

### `Insert.is_select` { #insert-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](select.md#select-is-select)-এর মতো।

### `Insert.is_selectable` { #insert-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](select.md#select-is-selectable)-এর মতো।

### `Insert.is_text` { #insert-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](select.md#select-is-text)-এর মতো।

### `Insert.is_update` { #insert-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](select.md#select-is-update)-এর মতো।

### `Insert.kwargs` { #insert-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.kwargs`](select.md#select-kwargs)-এর মতো।

### `Insert.memoized_attribute` { #insert-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](select.md#select-memoized-attribute)-এর মতো।

### `Insert.memoized_instancemethod()` { #insert-memoized-instancemethod }

```python
Insert.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](select.md#select-memoized-instancemethod)-এর মতো।

### `Insert.name_cte_columns` { #insert-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](select.md#select-name-cte-columns)-এর মতো।

### `Insert.named_with_column` { #insert-named-with-column }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্টের নাম কলামের আগে বসে কি না (DML-এ `False`)।

### `Insert.options()` { #insert-options }

```python
Insert.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](select.md#select-options)-এর মতো।

### `Insert.params()` { #insert-params }

```python
Insert.params(*arg, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](select.md#select-params)-এর মতো।

### `Insert.prefix_with()` { #insert-prefix-with }

```python
Insert.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.prefix_with`](select.md#select-prefix-with)-এর মতো।

### `Insert.reflect_only_elements` { #insert-reflect-only-elements }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.reflect_only_elements`](select.md#select-reflect-only-elements)-এর মতো।

### `Insert.return_defaults()` { #insert-return-defaults }

```python
Insert.return_defaults(*cols, supplemental_cols=None, sort_by_parameter_order=False)
```

**ধরন:** মেথড

ডেটাবেস যে মানগুলো নিজে বানায় (server default, auto-increment id) সেগুলো `RETURNING` দিয়ে আনে, পরে `result.returned_defaults` দিয়ে পাওয়া যায়। ORM নিজে ভেতরে এটি ব্যবহার করে; অ্যাপ কোডে সাধারণত `returning()` সহজ।

**উদাহরণ:**

```python
with engine.begin() as conn:
    result = conn.execute(insert(User.__table__).values(name="ডিফল্ট").return_defaults())
    print(result.returned_defaults)   # (4,)
```

### `Insert.returning()` { #insert-returning }

```python
Insert.returning(*cols, sort_by_parameter_order=False)
```

**ধরন:** মেথড

`RETURNING` যোগ করে: insert/update/delete হওয়া রো-গুলোর কলাম (বা ORM অবজেক্ট) সাথে সাথে ফেরত আসে, আলাদা SELECT ছাড়াই। PostgreSQL, SQLite, MariaDB, Oracle, SQL Server-এ চলে। বাল্ক insert-এ `sort_by_parameter_order=True` দিলে ফেরত রো দেওয়া প্যারামিটারের ক্রমে আসে।

**উদাহরণ:**

```python
rows = session.execute(insert(User).returning(User.id, User.name), [{"name": "ক"}, {"name": "খ"}]).all()
print(rows)   # [(4, 'ক'), (5, 'খ')]
```

### `Insert.returning_column_descriptions` { #insert-returning-column-descriptions }

**ধরন:** প্রপার্টি

`returning()`-এ দেওয়া কলামগুলোর বিবরণ (নাম, টাইপ, কোন মডেলের)।

**উদাহরণ:**

```python
stmt = insert(User).returning(User.id)
print(stmt.returning_column_descriptions[0]["name"])   # id
```

### `Insert.select` { #insert-select }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`from_select()` দিলে সেই SELECT এখানে রাখা হয়; নইলে `None`।

### `Insert.selectable` { #insert-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](select.md#select-selectable)-এর মতো।

### `Insert.self_group()` { #insert-self-group }

```python
Insert.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](select.md#select-self-group)-এর মতো।

### `Insert.stringify_dialect` { #insert-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](select.md#select-stringify-dialect)-এর মতো।

### `Insert.supports_execution` { #insert-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](select.md#select-supports-execution)-এর মতো।

### `Insert.unique_params()` { #insert-unique-params }

```python
Insert.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](select.md#select-unique-params)-এর মতো।

### `Insert.uses_inspection` { #insert-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](select.md#select-uses-inspection)-এর মতো।

### `Insert.values()` { #insert-values }

```python
Insert.values(*args, **kwargs)
```

**ধরন:** মেথড

INSERT-এর মান ঠিক করে: keyword (`name="x"`), dict, বা একাধিক রো-র জন্য dict-এর তালিকা (এক স্টেটমেন্টে বহু-রো `VALUES (...), (...)`)। অনেক রো হলে তালিকা `.values()`-এ না দিয়ে `session.execute(insert(User), list)` দেওয়াই ভালো।

**উদাহরণ:**

```python
session.execute(insert(User).values([{"name": "চ"}, {"name": "ছ"}]))
session.commit()
print(session.scalar(select(func.count()).select_from(User)))   # 5
```

### `Insert.with_dialect_options()` { #insert-with-dialect-options }

```python
Insert.with_dialect_options(**opt)
```

**ধরন:** মেথড

INSERT/UPDATE/DELETE-এ ডেটাবেস-নির্দিষ্ট অপশন যোগ করে, যেমন MySQL-এ `mysql_limit=10` (UPDATE/DELETE-এ `LIMIT`)। যে ডেটাবেসের অপশন নয়, সেখানে উপেক্ষিত হয়।

**উদাহরণ:**

```python
stmt = update(User).values(name="x").with_dialect_options(mysql_limit=10)
print(stmt.compile(dialect=mysql.dialect()))   # UPDATE users SET name=%s LIMIT 10
```

### `Insert.with_hint()` { #insert-with-hint }

```python
Insert.with_hint(text, selectable=None, dialect_name='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.with_hint`](select.md#select-with-hint)-এর মতো।

## `update()` { #update }

```python
from sqlalchemy import update
```

```python
update(table)
```

**ধরন:** ফাংশন

একটি `UPDATE` স্টেটমেন্ট বানায়। `.where()` দিয়ে কোন রো, `.values()` দিয়ে নতুন মান। ORM-এ primary key-সহ dict-এর তালিকা দিয়ে চালালে প্রতিটি রো আলাদা মানে বদলায় ("bulk update by primary key")।

**উদাহরণ:**

```python
session.execute(update(User).where(User.id > 1).values(name=User.name + " (সদস্য)"))
session.execute(update(User), [{"id": 1, "name": "রহিম খান"}])       # PK ধরে বাল্ক
session.commit()
print(session.scalars(select(User.name).order_by(User.id)).all())
# ['রহিম খান', 'করিম (সদস্য)', 'সুমি (সদস্য)']
```

## `Update` { #update }

```python
from sqlalchemy import Update
```

`update()` থেকে পাওয়া স্টেটমেন্ট। `where()`, `filter()`, `filter_by()` এখানে `Select`-এর মতোই WHERE বানায়।

**উদাহরণ:**

```python
result = session.execute(update(User).where(User.name == "করিম").values(name="করিম উদ্দিন"))
print(result.rowcount)   # 1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #update-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_cte()`](#update-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`allows_lambda`](#update-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`apply_syntax_extension_point()`](#update-apply-syntax-extension-point) | মেথড | (২.১-এ নতুন) কাস্টম SQL syntax extension বানানোর সময় extension নিজে এটি ডাকে, স্টেটমেন্টের নির্দিষ্ট জায়গায় (যেমন WHERE-এর পরে) নিজেকে বসাতে। |
| [`argument_for()`](#update-argument-for) | ক্লাস মেথড | এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। |
| [`compare()`](#update-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#update-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#update-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#update-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#update-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`dialect_kwargs`](#update-dialect-kwargs) | প্রপার্টি | এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। |
| [`dialect_options`](#update-dialect-options) | প্রপার্টি | `dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ। |
| [`entity_description`](#update-entity-description) | প্রপার্টি | স্টেটমেন্টটি কোন মডেল/টেবিলের ওপর কাজ করছে তার বিবরণ (dict: `name`, `type`, `entity`, `table` …)। |
| [`entity_namespace`](#update-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#update-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exported_columns`](#update-exported-columns) | প্রপার্টি | DML-এ এটি `RETURNING` কলামগুলোর সংগ্রহ (`returning()` না দিলে খালি)। |
| [`ext()`](#update-ext) | মেথড | (২.১-এ নতুন) ডেটাবেস-নির্দিষ্ট একটি SQL syntax extension যুক্ত করে, যেমন PostgreSQL-এর `DISTINCT ON`। |
| [`filter()`](#update-filter) | মেথড | `where()`-এর আরেক নাম। |
| [`filter_by()`](#update-filter-by) | মেথড | `কলাম=মান` keyword দিয়ে সহজ সমান-শর্ত যোগ করে। |
| [`get_children()`](#update-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_dialect_option()`](#update-get-dialect-option) | মেথড | একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। |
| [`get_execution_options()`](#update-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`inherit_cache`](#update-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`inline()`](#update-inline) | মেথড | Column-এর Python `default` / `onupdate` মানগুলো আলাদা করে আগে না চালিয়ে সরাসরি SQL-এর ভেতরে বসায়। |
| [`is_clause_element`](#update-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#update-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#update-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#update-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#update-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#update-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#update-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#update-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#update-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#update-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`kwargs`](#update-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`memoized_attribute`](#update-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#update-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#update-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`named_with_column`](#update-named-with-column) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্টের নাম কলামের আগে বসে কি না (DML-এ `False`)। |
| [`options()`](#update-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`ordered_values()`](#update-ordered-values) | মেথড | `SET` অংশে কলামগুলো ঠিক আপনার দেওয়া ক্রমে বসায় (tuple-এর তালিকা দিয়ে)। |
| [`params()`](#update-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`prefix_with()`](#update-prefix-with) | মেথড | `SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। |
| [`reflect_only_elements`](#update-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। |
| [`return_defaults()`](#update-return-defaults) | মেথড | ডেটাবেস যে মানগুলো নিজে বানায় (server default, auto-increment id) সেগুলো `RETURNING` দিয়ে আনে, পরে `result.returned_defaults` দিয়ে পাওয়া যায়। |
| [`returning()`](#update-returning) | মেথড | `RETURNING` যোগ করে: insert/update/delete হওয়া রো-গুলোর কলাম (বা ORM অবজেক্ট) সাথে সাথে ফেরত আসে, আলাদা SELECT ছাড়াই। |
| [`returning_column_descriptions`](#update-returning-column-descriptions) | প্রপার্টি | `returning()`-এ দেওয়া কলামগুলোর বিবরণ (নাম, টাইপ, কোন মডেলের)। |
| [`select`](#update-select) | অ্যাট্রিবিউট | `from_select()` দিলে সেই SELECT এখানে রাখা হয়; নইলে `None`। |
| [`selectable`](#update-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#update-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#update-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`supports_execution`](#update-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`unique_params()`](#update-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#update-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`values()`](#update-values) | মেথড | UPDATE-এর `SET` অংশ: কোন কলামে কী মান। |
| [`where()`](#update-where) | মেথড | `WHERE` শর্ত যোগ করে। |
| [`whereclause`](#update-whereclause) | প্রপার্টি | এ পর্যন্ত যোগ করা সব WHERE শর্ত একসাথে (একটি এক্সপ্রেশন) দেয়; না থাকলে `None`। |
| [`with_dialect_options()`](#update-with-dialect-options) | মেথড | INSERT/UPDATE/DELETE-এ ডেটাবেস-নির্দিষ্ট অপশন যোগ করে, যেমন MySQL-এ `mysql_limit=10` (UPDATE/DELETE-এ `LIMIT`)। |
| [`with_hint()`](#update-with-hint) | মেথড | নির্দিষ্ট একটি টেবিলের জন্য ডেটাবেস-নির্দিষ্ট hint (যেমন Oracle/MySQL-এর index hint) যোগ করে। |

### `Update.add_cte()` { #update-add-cte }

```python
Update.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](select.md#select-add-cte)-এর মতো।

### `Update.allows_lambda` { #update-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](select.md#select-allows-lambda)-এর মতো।

### `Update.apply_syntax_extension_point()` { #update-apply-syntax-extension-point }

```python
Update.apply_syntax_extension_point(apply_fn, position)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.apply_syntax_extension_point`](select.md#select-apply-syntax-extension-point)-এর মতো।

### `Update.argument_for()` { #update-argument-for }

```python
Update.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.argument_for`](select.md#select-argument-for)-এর মতো।

### `Update.compare()` { #update-compare }

```python
Update.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](select.md#select-compare)-এর মতো।

### `Update.compile()` { #update-compile }

```python
Update.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](select.md#select-compile)-এর মতো।

### `Update.corresponding_column()` { #update-corresponding-column }

```python
Update.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](select.md#select-corresponding-column)-এর মতো।

### `Update.cte()` { #update-cte }

```python
Update.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](select.md#select-cte)-এর মতো।

### `Update.description` { #update-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](select.md#select-description)-এর মতো।

### `Update.dialect_kwargs` { #update-dialect-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_kwargs`](select.md#select-dialect-kwargs)-এর মতো।

### `Update.dialect_options` { #update-dialect-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_options`](select.md#select-dialect-options)-এর মতো।

### `Update.entity_description` { #update-entity-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.entity_description`](#insert-entity-description)-এর মতো।

### `Update.entity_namespace` { #update-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](select.md#select-entity-namespace)-এর মতো।

### `Update.execution_options()` { #update-execution-options }

```python
Update.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](select.md#select-execution-options)-এর মতো।

### `Update.exported_columns` { #update-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.exported_columns`](#insert-exported-columns)-এর মতো।

### `Update.ext()` { #update-ext }

```python
Update.ext(extension)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.ext`](select.md#select-ext)-এর মতো।

### `Update.filter()` { #update-filter }

```python
Update.filter(*criteria)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.filter`](select.md#select-filter)-এর মতো।

### `Update.filter_by()` { #update-filter-by }

```python
Update.filter_by(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.filter_by`](select.md#select-filter-by)-এর মতো।

### `Update.get_children()` { #update-get-children }

```python
Update.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](select.md#select-get-children)-এর মতো।

### `Update.get_dialect_option()` { #update-get-dialect-option }

```python
Update.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_dialect_option`](select.md#select-get-dialect-option)-এর মতো।

### `Update.get_execution_options()` { #update-get-execution-options }

```python
Update.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](select.md#select-get-execution-options)-এর মতো।

### `Update.inherit_cache` { #update-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](select.md#select-inherit-cache)-এর মতো।

### `Update.inline()` { #update-inline }

```python
Update.inline()
```

**ধরন:** মেথড

Column-এর Python `default` / `onupdate` মানগুলো আলাদা করে আগে না চালিয়ে সরাসরি SQL-এর ভেতরে বসায়।

**উদাহরণ:**

```python
session.execute(update(User).where(User.id == 1).values(name="ইনলাইন").inline())
session.commit()
```

### `Update.is_clause_element` { #update-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](select.md#select-is-clause-element)-এর মতো।

### `Update.is_delete` { #update-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](select.md#select-is-delete)-এর মতো।

### `Update.is_derived_from()` { #update-is-derived-from }

```python
Update.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](select.md#select-is-derived-from)-এর মতো।

### `Update.is_dml` { #update-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](select.md#select-is-dml)-এর মতো।

### `Update.is_from_statement` { #update-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](select.md#select-is-from-statement)-এর মতো।

### `Update.is_insert` { #update-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](select.md#select-is-insert)-এর মতো।

### `Update.is_select` { #update-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](select.md#select-is-select)-এর মতো।

### `Update.is_selectable` { #update-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](select.md#select-is-selectable)-এর মতো।

### `Update.is_text` { #update-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](select.md#select-is-text)-এর মতো।

### `Update.is_update` { #update-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](select.md#select-is-update)-এর মতো।

### `Update.kwargs` { #update-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.kwargs`](select.md#select-kwargs)-এর মতো।

### `Update.memoized_attribute` { #update-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](select.md#select-memoized-attribute)-এর মতো।

### `Update.memoized_instancemethod()` { #update-memoized-instancemethod }

```python
Update.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](select.md#select-memoized-instancemethod)-এর মতো।

### `Update.name_cte_columns` { #update-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](select.md#select-name-cte-columns)-এর মতো।

### `Update.named_with_column` { #update-named-with-column }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Insert.named_with_column`](#insert-named-with-column)-এর মতো।

### `Update.options()` { #update-options }

```python
Update.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](select.md#select-options)-এর মতো।

### `Update.ordered_values()` { #update-ordered-values }

```python
Update.ordered_values(*args)
```

**ধরন:** মেথড

`SET` অংশে কলামগুলো ঠিক আপনার দেওয়া ক্রমে বসায় (tuple-এর তালিকা দিয়ে)। MySQL-এ ক্রম গুরুত্বপূর্ণ (একই স্টেটমেন্টে আগের কলামের নতুন মান পরের কলামে ব্যবহার হয়), সেখানে কাজে লাগে।

**উদাহরণ:**

```python
stmt = update(User).ordered_values((User.name, "ক"), (User.id, 10))
print(stmt)   # UPDATE users SET name=:name, id=:id
```

### `Update.params()` { #update-params }

```python
Update.params(*arg, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](select.md#select-params)-এর মতো।

### `Update.prefix_with()` { #update-prefix-with }

```python
Update.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.prefix_with`](select.md#select-prefix-with)-এর মতো।

### `Update.reflect_only_elements` { #update-reflect-only-elements }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.reflect_only_elements`](select.md#select-reflect-only-elements)-এর মতো।

### `Update.return_defaults()` { #update-return-defaults }

```python
Update.return_defaults(*cols, supplemental_cols=None, sort_by_parameter_order=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.return_defaults`](#insert-return-defaults)-এর মতো।

### `Update.returning()` { #update-returning }

```python
Update.returning(*cols, sort_by_parameter_order=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.returning`](#insert-returning)-এর মতো।

### `Update.returning_column_descriptions` { #update-returning-column-descriptions }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.returning_column_descriptions`](#insert-returning-column-descriptions)-এর মতো।

### `Update.select` { #update-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Insert.select`](#insert-select)-এর মতো।

### `Update.selectable` { #update-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](select.md#select-selectable)-এর মতো।

### `Update.self_group()` { #update-self-group }

```python
Update.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](select.md#select-self-group)-এর মতো।

### `Update.stringify_dialect` { #update-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](select.md#select-stringify-dialect)-এর মতো।

### `Update.supports_execution` { #update-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](select.md#select-supports-execution)-এর মতো।

### `Update.unique_params()` { #update-unique-params }

```python
Update.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](select.md#select-unique-params)-এর মতো।

### `Update.uses_inspection` { #update-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](select.md#select-uses-inspection)-এর মতো।

### `Update.values()` { #update-values }

```python
Update.values(*args, **kwargs)
```

**ধরন:** মেথড

UPDATE-এর `SET` অংশ: কোন কলামে কী মান। মান হিসেবে SQL এক্সপ্রেশনও দেওয়া যায় (যেমন `User.name + "!"`, `Counter.n + 1`), যা race-condition ছাড়া atomic আপডেট করে।

**উদাহরণ:**

```python
session.execute(update(User).where(User.id == 3).values(name=User.name + "!"))
print(session.scalars(select(User.name).where(User.id == 3)).one())   # সুমি!
```

### `Update.where()` { #update-where }

```python
Update.where(*whereclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.where`](select.md#select-where)-এর মতো।

### `Update.whereclause` { #update-whereclause }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.whereclause`](select.md#select-whereclause)-এর মতো।

### `Update.with_dialect_options()` { #update-with-dialect-options }

```python
Update.with_dialect_options(**opt)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.with_dialect_options`](#insert-with-dialect-options)-এর মতো।

### `Update.with_hint()` { #update-with-hint }

```python
Update.with_hint(text, selectable=None, dialect_name='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.with_hint`](select.md#select-with-hint)-এর মতো।

## `delete()` { #delete }

```python
from sqlalchemy import delete
```

```python
delete(table)
```

**ধরন:** ফাংশন

একটি `DELETE` স্টেটমেন্ট বানায়। `.where()` না দিলে **টেবিলের সব রো মুছে যায়**, সাবধান!

**উদাহরণ:**

```python
result = session.execute(delete(Address).where(Address.email.like("%@work.com")))
session.commit()
print(result.rowcount)   # 1
```

## `Delete` { #delete }

```python
from sqlalchemy import Delete
```

`delete()` থেকে পাওয়া স্টেটমেন্ট। ORM cascade বা event চালায় না; চাইল্ড মুছতে ডেটাবেসের `ON DELETE CASCADE` বা আগে আলাদা delete লাগবে।

**উদাহরণ:**

```python
deleted = session.scalars(delete(Address).where(Address.user_id == 1).returning(Address.email)).all()
print(sorted(deleted))   # ['rahim@example.com', 'rahim@work.com']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #delete-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_cte()`](#delete-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`allows_lambda`](#delete-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`apply_syntax_extension_point()`](#delete-apply-syntax-extension-point) | মেথড | (২.১-এ নতুন) কাস্টম SQL syntax extension বানানোর সময় extension নিজে এটি ডাকে, স্টেটমেন্টের নির্দিষ্ট জায়গায় (যেমন WHERE-এর পরে) নিজেকে বসাতে। |
| [`argument_for()`](#delete-argument-for) | ক্লাস মেথড | এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। |
| [`compare()`](#delete-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#delete-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#delete-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#delete-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#delete-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`dialect_kwargs`](#delete-dialect-kwargs) | প্রপার্টি | এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। |
| [`dialect_options`](#delete-dialect-options) | প্রপার্টি | `dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ। |
| [`entity_description`](#delete-entity-description) | প্রপার্টি | স্টেটমেন্টটি কোন মডেল/টেবিলের ওপর কাজ করছে তার বিবরণ (dict: `name`, `type`, `entity`, `table` …)। |
| [`entity_namespace`](#delete-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#delete-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exported_columns`](#delete-exported-columns) | প্রপার্টি | DML-এ এটি `RETURNING` কলামগুলোর সংগ্রহ (`returning()` না দিলে খালি)। |
| [`ext()`](#delete-ext) | মেথড | (২.১-এ নতুন) ডেটাবেস-নির্দিষ্ট একটি SQL syntax extension যুক্ত করে, যেমন PostgreSQL-এর `DISTINCT ON`। |
| [`filter()`](#delete-filter) | মেথড | `where()`-এর আরেক নাম। |
| [`filter_by()`](#delete-filter-by) | মেথড | `কলাম=মান` keyword দিয়ে সহজ সমান-শর্ত যোগ করে। |
| [`get_children()`](#delete-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_dialect_option()`](#delete-get-dialect-option) | মেথড | একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। |
| [`get_execution_options()`](#delete-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`inherit_cache`](#delete-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`is_clause_element`](#delete-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#delete-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#delete-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#delete-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#delete-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#delete-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#delete-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#delete-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#delete-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#delete-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`kwargs`](#delete-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`memoized_attribute`](#delete-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#delete-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#delete-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`named_with_column`](#delete-named-with-column) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্টের নাম কলামের আগে বসে কি না (DML-এ `False`)। |
| [`options()`](#delete-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`params()`](#delete-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`prefix_with()`](#delete-prefix-with) | মেথড | `SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। |
| [`reflect_only_elements`](#delete-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। |
| [`return_defaults()`](#delete-return-defaults) | মেথড | ডেটাবেস যে মানগুলো নিজে বানায় (server default, auto-increment id) সেগুলো `RETURNING` দিয়ে আনে, পরে `result.returned_defaults` দিয়ে পাওয়া যায়। |
| [`returning()`](#delete-returning) | মেথড | `RETURNING` যোগ করে: insert/update/delete হওয়া রো-গুলোর কলাম (বা ORM অবজেক্ট) সাথে সাথে ফেরত আসে, আলাদা SELECT ছাড়াই। |
| [`returning_column_descriptions`](#delete-returning-column-descriptions) | প্রপার্টি | `returning()`-এ দেওয়া কলামগুলোর বিবরণ (নাম, টাইপ, কোন মডেলের)। |
| [`selectable`](#delete-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#delete-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#delete-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`supports_execution`](#delete-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`unique_params()`](#delete-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#delete-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`using()`](#delete-using) | মেথড | (২.১-এ নতুন) একাধিক টেবিলের DELETE-এ দ্বিতীয় টেবিলটি `USING` হিসেবে স্পষ্ট করে (PostgreSQL ধাঁচ)। |
| [`where()`](#delete-where) | মেথড | `WHERE` শর্ত যোগ করে। |
| [`whereclause`](#delete-whereclause) | প্রপার্টি | এ পর্যন্ত যোগ করা সব WHERE শর্ত একসাথে (একটি এক্সপ্রেশন) দেয়; না থাকলে `None`। |
| [`with_dialect_options()`](#delete-with-dialect-options) | মেথড | INSERT/UPDATE/DELETE-এ ডেটাবেস-নির্দিষ্ট অপশন যোগ করে, যেমন MySQL-এ `mysql_limit=10` (UPDATE/DELETE-এ `LIMIT`)। |
| [`with_hint()`](#delete-with-hint) | মেথড | নির্দিষ্ট একটি টেবিলের জন্য ডেটাবেস-নির্দিষ্ট hint (যেমন Oracle/MySQL-এর index hint) যোগ করে। |

### `Delete.add_cte()` { #delete-add-cte }

```python
Delete.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](select.md#select-add-cte)-এর মতো।

### `Delete.allows_lambda` { #delete-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](select.md#select-allows-lambda)-এর মতো।

### `Delete.apply_syntax_extension_point()` { #delete-apply-syntax-extension-point }

```python
Delete.apply_syntax_extension_point(apply_fn, position)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.apply_syntax_extension_point`](select.md#select-apply-syntax-extension-point)-এর মতো।

### `Delete.argument_for()` { #delete-argument-for }

```python
Delete.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.argument_for`](select.md#select-argument-for)-এর মতো।

### `Delete.compare()` { #delete-compare }

```python
Delete.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](select.md#select-compare)-এর মতো।

### `Delete.compile()` { #delete-compile }

```python
Delete.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](select.md#select-compile)-এর মতো।

### `Delete.corresponding_column()` { #delete-corresponding-column }

```python
Delete.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](select.md#select-corresponding-column)-এর মতো।

### `Delete.cte()` { #delete-cte }

```python
Delete.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](select.md#select-cte)-এর মতো।

### `Delete.description` { #delete-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](select.md#select-description)-এর মতো।

### `Delete.dialect_kwargs` { #delete-dialect-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_kwargs`](select.md#select-dialect-kwargs)-এর মতো।

### `Delete.dialect_options` { #delete-dialect-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_options`](select.md#select-dialect-options)-এর মতো।

### `Delete.entity_description` { #delete-entity-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.entity_description`](#insert-entity-description)-এর মতো।

### `Delete.entity_namespace` { #delete-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](select.md#select-entity-namespace)-এর মতো।

### `Delete.execution_options()` { #delete-execution-options }

```python
Delete.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](select.md#select-execution-options)-এর মতো।

### `Delete.exported_columns` { #delete-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.exported_columns`](#insert-exported-columns)-এর মতো।

### `Delete.ext()` { #delete-ext }

```python
Delete.ext(extension)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.ext`](select.md#select-ext)-এর মতো।

### `Delete.filter()` { #delete-filter }

```python
Delete.filter(*criteria)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.filter`](select.md#select-filter)-এর মতো।

### `Delete.filter_by()` { #delete-filter-by }

```python
Delete.filter_by(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.filter_by`](select.md#select-filter-by)-এর মতো।

### `Delete.get_children()` { #delete-get-children }

```python
Delete.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](select.md#select-get-children)-এর মতো।

### `Delete.get_dialect_option()` { #delete-get-dialect-option }

```python
Delete.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_dialect_option`](select.md#select-get-dialect-option)-এর মতো।

### `Delete.get_execution_options()` { #delete-get-execution-options }

```python
Delete.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](select.md#select-get-execution-options)-এর মতো।

### `Delete.inherit_cache` { #delete-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](select.md#select-inherit-cache)-এর মতো।

### `Delete.is_clause_element` { #delete-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](select.md#select-is-clause-element)-এর মতো।

### `Delete.is_delete` { #delete-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](select.md#select-is-delete)-এর মতো।

### `Delete.is_derived_from()` { #delete-is-derived-from }

```python
Delete.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](select.md#select-is-derived-from)-এর মতো।

### `Delete.is_dml` { #delete-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](select.md#select-is-dml)-এর মতো।

### `Delete.is_from_statement` { #delete-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](select.md#select-is-from-statement)-এর মতো।

### `Delete.is_insert` { #delete-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](select.md#select-is-insert)-এর মতো।

### `Delete.is_select` { #delete-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](select.md#select-is-select)-এর মতো।

### `Delete.is_selectable` { #delete-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](select.md#select-is-selectable)-এর মতো।

### `Delete.is_text` { #delete-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](select.md#select-is-text)-এর মতো।

### `Delete.is_update` { #delete-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](select.md#select-is-update)-এর মতো।

### `Delete.kwargs` { #delete-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.kwargs`](select.md#select-kwargs)-এর মতো।

### `Delete.memoized_attribute` { #delete-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](select.md#select-memoized-attribute)-এর মতো।

### `Delete.memoized_instancemethod()` { #delete-memoized-instancemethod }

```python
Delete.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](select.md#select-memoized-instancemethod)-এর মতো।

### `Delete.name_cte_columns` { #delete-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](select.md#select-name-cte-columns)-এর মতো।

### `Delete.named_with_column` { #delete-named-with-column }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Insert.named_with_column`](#insert-named-with-column)-এর মতো।

### `Delete.options()` { #delete-options }

```python
Delete.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](select.md#select-options)-এর মতো।

### `Delete.params()` { #delete-params }

```python
Delete.params(*arg, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](select.md#select-params)-এর মতো।

### `Delete.prefix_with()` { #delete-prefix-with }

```python
Delete.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.prefix_with`](select.md#select-prefix-with)-এর মতো।

### `Delete.reflect_only_elements` { #delete-reflect-only-elements }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.reflect_only_elements`](select.md#select-reflect-only-elements)-এর মতো।

### `Delete.return_defaults()` { #delete-return-defaults }

```python
Delete.return_defaults(*cols, supplemental_cols=None, sort_by_parameter_order=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.return_defaults`](#insert-return-defaults)-এর মতো।

### `Delete.returning()` { #delete-returning }

```python
Delete.returning(*cols, sort_by_parameter_order=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.returning`](#insert-returning)-এর মতো।

### `Delete.returning_column_descriptions` { #delete-returning-column-descriptions }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Insert.returning_column_descriptions`](#insert-returning-column-descriptions)-এর মতো।

### `Delete.selectable` { #delete-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](select.md#select-selectable)-এর মতো।

### `Delete.self_group()` { #delete-self-group }

```python
Delete.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](select.md#select-self-group)-এর মতো।

### `Delete.stringify_dialect` { #delete-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](select.md#select-stringify-dialect)-এর মতো।

### `Delete.supports_execution` { #delete-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](select.md#select-supports-execution)-এর মতো।

### `Delete.unique_params()` { #delete-unique-params }

```python
Delete.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](select.md#select-unique-params)-এর মতো।

### `Delete.uses_inspection` { #delete-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](select.md#select-uses-inspection)-এর মতো।

### `Delete.using()` { #delete-using }

```python
Delete.using(*froms)
```

**ধরন:** মেথড

(২.১-এ নতুন) একাধিক টেবিলের DELETE-এ দ্বিতীয় টেবিলটি `USING` হিসেবে স্পষ্ট করে (PostgreSQL ধাঁচ)। WHERE-এ অন্য টেবিলের কলাম থাকলে SQLAlchemy সাধারণত নিজেই `USING` বসায়; স্পষ্ট করতে বা জটিল ক্ষেত্রে এটি।

**উদাহরণ:**

```python
stmt = delete(Address).where(Address.user_id == User.id, User.name == "রহিম").using(User)
print(stmt.compile(dialect=postgresql.dialect()))
# DELETE FROM addresses USING users WHERE addresses.user_id = users.id AND users.name = %(name_1)s::VARCHAR
print(session.execute(stmt).rowcount)   # 2
```

### `Delete.where()` { #delete-where }

```python
Delete.where(*whereclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.where`](select.md#select-where)-এর মতো।

### `Delete.whereclause` { #delete-whereclause }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.whereclause`](select.md#select-whereclause)-এর মতো।

### `Delete.with_dialect_options()` { #delete-with-dialect-options }

```python
Delete.with_dialect_options(**opt)
```

**ধরন:** মেথড

কাজ হুবহু [`Insert.with_dialect_options`](#insert-with-dialect-options)-এর মতো।

### `Delete.with_hint()` { #delete-with-hint }

```python
Delete.with_hint(text, selectable=None, dialect_name='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.with_hint`](select.md#select-with-hint)-এর মতো।

## `text()` { #text }

```python
from sqlalchemy import text
```

```python
text(text)
```

**ধরন:** ফাংশন

নিজে লেখা SQL স্ট্রিং থেকে একটি স্টেটমেন্ট বানায়। প্যারামিটার লিখুন `:নাম` আকারে আর মান আলাদা দিন, তাহলে SQL injection হয় না। **কখনো** ইউজারের ইনপুট f-string দিয়ে SQL-এর ভেতরে বসাবেন না।

**উদাহরণ:**

```python
rows = session.execute(text("SELECT id, name FROM users WHERE id < :n ORDER BY id"), {"n": 3}).all()
print(rows)   # [(1, 'রহিম'), (2, 'করিম')]
```

## `TextClause` { #textclause }

```python
from sqlalchemy import TextClause
```

`text()` থেকে পাওয়া কনস্ট্রাক্ট। পুরো স্টেটমেন্ট হিসেবে চালানো যায়, আবার `where(text("..."))`-এর মতো অংশ হিসেবেও বসানো যায়।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).where(text("users.id = 2"))).one())   # করিম
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #textclause-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`allows_lambda`](#textclause-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`bindparams()`](#textclause-bindparams) | মেথড | `:নাম` প্যারামিটারগুলোর মান বা টাইপ আগেই ঠিক করে দেয়, যাতে চালানোর সময় দিতে না হয়। |
| [`columns()`](#textclause-columns) | মেথড | raw SQL কোন কলাম কোন টাইপে ফেরত দেবে তা জানিয়ে একটি `TextualSelect` বানায়। |
| [`comparator`](#textclause-comparator) | প্রপার্টি (internal) | `text()`-কে এক্সপ্রেশনের মতো ব্যবহারের সময় তুলনা-অপারেটরের ভেতরের বস্তু। |
| [`compare()`](#textclause-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#textclause-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`description`](#textclause-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`entity_namespace`](#textclause-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#textclause-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`get_children()`](#textclause-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_execution_options()`](#textclause-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`inherit_cache`](#textclause-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`is_clause_element`](#textclause-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#textclause-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_dml`](#textclause-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#textclause-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#textclause-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#textclause-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#textclause-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#textclause-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#textclause-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`key`](#textclause-key) | অ্যাট্রিবিউট (internal) | ভেতরের key; `text()`-এ সবসময় `None`। |
| [`label()`](#textclause-label) | মেথড | এই SELECT-কে একটি নাম দেওয়া scalar সাবকুয়েরি বানায়, যাতে বাইরের SELECT-এ কলাম হিসেবে বসানো যায়। |
| [`memoized_attribute`](#textclause-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#textclause-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`options()`](#textclause-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`params()`](#textclause-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`self_group()`](#textclause-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#textclause-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`subquery()`](#textclause-subquery) | মেথড | এই SELECT-কে FROM-এ বসানোর মতো একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`supports_execution`](#textclause-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`type`](#textclause-type) | প্রপার্টি | এই টেক্সট এক্সপ্রেশনের SQL টাইপ; অজানা বলে `NullType`। |
| [`unique_params()`](#textclause-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#textclause-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |

### `TextClause.allows_lambda` { #textclause-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](select.md#select-allows-lambda)-এর মতো।

### `TextClause.bindparams()` { #textclause-bindparams }

```python
TextClause.bindparams(*binds, **names_to_values)
```

**ধরন:** মেথড

`:নাম` প্যারামিটারগুলোর মান বা টাইপ আগেই ঠিক করে দেয়, যাতে চালানোর সময় দিতে না হয়।

**উদাহরণ:**

```python
stmt = text("SELECT name FROM users WHERE id = :uid").bindparams(uid=3)
print(session.scalar(stmt))   # সুমি
```

### `TextClause.columns()` { #textclause-columns }

```python
TextClause.columns(*cols, **types)
```

**ধরন:** মেথড

raw SQL কোন কলাম কোন টাইপে ফেরত দেবে তা জানিয়ে একটি `TextualSelect` বানায়। এতে ফলাফলের টাইপ ঠিক থাকে, আর এটিকে সাবকুয়েরি বা `select(User).from_statement()`-এ ব্যবহার করা যায়।

**উদাহরণ:**

```python
stmt = text("SELECT id, name FROM users").columns(User.id, User.name)
sub = stmt.subquery()
print(session.execute(select(sub.c.name).where(sub.c.id == 1)).scalar())   # রহিম
```

### `TextClause.comparator` { #textclause-comparator }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`text()`-কে এক্সপ্রেশনের মতো ব্যবহারের সময় তুলনা-অপারেটরের ভেতরের বস্তু।

### `TextClause.compare()` { #textclause-compare }

```python
TextClause.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](select.md#select-compare)-এর মতো।

### `TextClause.compile()` { #textclause-compile }

```python
TextClause.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](select.md#select-compile)-এর মতো।

### `TextClause.description` { #textclause-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](select.md#select-description)-এর মতো।

### `TextClause.entity_namespace` { #textclause-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](select.md#select-entity-namespace)-এর মতো।

### `TextClause.execution_options()` { #textclause-execution-options }

```python
TextClause.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](select.md#select-execution-options)-এর মতো।

### `TextClause.get_children()` { #textclause-get-children }

```python
TextClause.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](select.md#select-get-children)-এর মতো।

### `TextClause.get_execution_options()` { #textclause-get-execution-options }

```python
TextClause.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](select.md#select-get-execution-options)-এর মতো।

### `TextClause.inherit_cache` { #textclause-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](select.md#select-inherit-cache)-এর মতো।

### `TextClause.is_clause_element` { #textclause-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](select.md#select-is-clause-element)-এর মতো।

### `TextClause.is_delete` { #textclause-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](select.md#select-is-delete)-এর মতো।

### `TextClause.is_dml` { #textclause-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](select.md#select-is-dml)-এর মতো।

### `TextClause.is_from_statement` { #textclause-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](select.md#select-is-from-statement)-এর মতো।

### `TextClause.is_insert` { #textclause-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](select.md#select-is-insert)-এর মতো।

### `TextClause.is_select` { #textclause-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](select.md#select-is-select)-এর মতো।

### `TextClause.is_selectable` { #textclause-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](select.md#select-is-selectable)-এর মতো।

### `TextClause.is_text` { #textclause-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](select.md#select-is-text)-এর মতো।

### `TextClause.is_update` { #textclause-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](select.md#select-is-update)-এর মতো।

### `TextClause.key` { #textclause-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের key; `text()`-এ সবসময় `None`।

### `TextClause.label()` { #textclause-label }

```python
TextClause.label(name)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.label`](select.md#select-label)-এর মতো।

### `TextClause.memoized_attribute` { #textclause-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](select.md#select-memoized-attribute)-এর মতো।

### `TextClause.memoized_instancemethod()` { #textclause-memoized-instancemethod }

```python
TextClause.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](select.md#select-memoized-instancemethod)-এর মতো।

### `TextClause.options()` { #textclause-options }

```python
TextClause.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](select.md#select-options)-এর মতো।

### `TextClause.params()` { #textclause-params }

```python
TextClause.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](select.md#select-params)-এর মতো।

### `TextClause.self_group()` { #textclause-self-group }

```python
TextClause.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](select.md#select-self-group)-এর মতো।

### `TextClause.stringify_dialect` { #textclause-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](select.md#select-stringify-dialect)-এর মতো।

### `TextClause.subquery()` { #textclause-subquery }

```python
TextClause.subquery()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.subquery`](select.md#select-subquery)-এর মতো।

### `TextClause.supports_execution` { #textclause-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](select.md#select-supports-execution)-এর মতো।

### `TextClause.type` { #textclause-type }

**ধরন:** প্রপার্টি

এই টেক্সট এক্সপ্রেশনের SQL টাইপ; অজানা বলে `NullType`। টাইপ দরকার হলে `columns()` বা `literal_column()` ব্যবহার করুন।

**উদাহরণ:**

```python
print(repr(text("1 + 1").type))   # NullType()
```

### `TextClause.unique_params()` { #textclause-unique-params }

```python
TextClause.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](select.md#select-unique-params)-এর মতো।

### `TextClause.uses_inspection` { #textclause-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](select.md#select-uses-inspection)-এর মতো।

## `TextualSelect` { #textualselect }

```python
from sqlalchemy.sql.expression import TextualSelect
```

`text(...).columns(...)` থেকে পাওয়া, কলাম জানা একটি raw SELECT। এটি `select()`-এর মতো আচরণ করে: `subquery()`, `cte()`, `alias()` ইত্যাদি চলে।

**উদাহরণ:**

```python
ts = text("SELECT id, name FROM users WHERE id > 1").columns(column("id", Integer), column("name", String))
print(session.execute(ts).all())   # [(2, 'করিম'), (3, 'সুমি')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #textualselect-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_cte()`](#textualselect-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`alias()`](#textualselect-alias) | মেথড | `subquery()`-এর আরেক নাম: এই SELECT-কে একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`allows_lambda`](#textualselect-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`as_scalar()`](#textualselect-as-scalar) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`bindparams()`](#textualselect-bindparams) | মেথড | `:নাম` প্যারামিটারগুলোর মান বা টাইপ আগেই ঠিক করে দেয়, যাতে চালানোর সময় দিতে না হয়। |
| [`compare()`](#textualselect-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#textualselect-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#textualselect-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#textualselect-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#textualselect-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`entity_namespace`](#textualselect-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#textualselect-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exists()`](#textualselect-exists) | মেথড | এই SELECT-কে `EXISTS (...)` এক্সপ্রেশন বানায়, যা `where()`-এ শর্ত হিসেবে বা কলাম হিসেবে ব্যবহার করা যায়। |
| [`exported_columns`](#textualselect-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`get_children()`](#textualselect-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_execution_options()`](#textualselect-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`get_label_style()`](#textualselect-get-label-style) | মেথড | বর্তমান label style (কলামের নামকরণের নিয়ম) দেয়। |
| [`inherit_cache`](#textualselect-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`into()`](#textualselect-into) | মেথড | (২.১-এ নতুন) এই SELECT-এর ফল দিয়ে নতুন একটি টেবিল বানানোর `CREATE TABLE ... AS SELECT ...` স্টেটমেন্ট দেয়। |
| [`is_clause_element`](#textualselect-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#textualselect-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#textualselect-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#textualselect-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#textualselect-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#textualselect-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#textualselect-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#textualselect-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#textualselect-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#textualselect-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`label()`](#textualselect-label) | মেথড | এই SELECT-কে একটি নাম দেওয়া scalar সাবকুয়েরি বানায়, যাতে বাইরের SELECT-এ কলাম হিসেবে বসানো যায়। |
| [`lateral()`](#textualselect-lateral) | মেথড | `LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`memoized_attribute`](#textualselect-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#textualselect-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#textualselect-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`options()`](#textualselect-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`params()`](#textualselect-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`replace_selectable()`](#textualselect-replace-selectable) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`scalar_subquery()`](#textualselect-scalar-subquery) | মেথড | এক রো, এক কলাম দেয় এমন SELECT-কে একটি মান হিসেবে (scalar) ব্যবহারযোগ্য করে, যাতে অন্য SELECT-এর কলামে বা WHERE-এ বসানো যায়। |
| [`selectable`](#textualselect-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`selected_columns`](#textualselect-selected-columns) | প্রপার্টি | এই SELECT যে কলামগুলো ফেরত দেবে তার সংগ্রহ। |
| [`self_group()`](#textualselect-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`set_label_style()`](#textualselect-set-label-style) | মেথড | ফলাফলের কলামগুলোর নাম কীভাবে হবে তা ঠিক করে। |
| [`stringify_dialect`](#textualselect-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`subquery()`](#textualselect-subquery) | মেথড | এই SELECT-কে FROM-এ বসানোর মতো একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`supports_execution`](#textualselect-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`unique_params()`](#textualselect-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#textualselect-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |

### `TextualSelect.add_cte()` { #textualselect-add-cte }

```python
TextualSelect.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](select.md#select-add-cte)-এর মতো।

### `TextualSelect.alias()` { #textualselect-alias }

```python
TextualSelect.alias(name=None, flat=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.alias`](select.md#select-alias)-এর মতো।

### `TextualSelect.allows_lambda` { #textualselect-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](select.md#select-allows-lambda)-এর মতো।

### `TextualSelect.as_scalar()` { #textualselect-as-scalar }

```python
TextualSelect.as_scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.as_scalar`](select.md#select-as-scalar)-এর মতো।

### `TextualSelect.bindparams()` { #textualselect-bindparams }

```python
TextualSelect.bindparams(*binds, **bind_as_values)
```

**ধরন:** মেথড

কাজ হুবহু [`TextClause.bindparams`](#textclause-bindparams)-এর মতো।

### `TextualSelect.compare()` { #textualselect-compare }

```python
TextualSelect.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](select.md#select-compare)-এর মতো।

### `TextualSelect.compile()` { #textualselect-compile }

```python
TextualSelect.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](select.md#select-compile)-এর মতো।

### `TextualSelect.corresponding_column()` { #textualselect-corresponding-column }

```python
TextualSelect.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](select.md#select-corresponding-column)-এর মতো।

### `TextualSelect.cte()` { #textualselect-cte }

```python
TextualSelect.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](select.md#select-cte)-এর মতো।

### `TextualSelect.description` { #textualselect-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](select.md#select-description)-এর মতো।

### `TextualSelect.entity_namespace` { #textualselect-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](select.md#select-entity-namespace)-এর মতো।

### `TextualSelect.execution_options()` { #textualselect-execution-options }

```python
TextualSelect.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](select.md#select-execution-options)-এর মতো।

### `TextualSelect.exists()` { #textualselect-exists }

```python
TextualSelect.exists()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.exists`](select.md#select-exists)-এর মতো।

### `TextualSelect.exported_columns` { #textualselect-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.exported_columns`](select.md#select-exported-columns)-এর মতো।

### `TextualSelect.get_children()` { #textualselect-get-children }

```python
TextualSelect.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](select.md#select-get-children)-এর মতো।

### `TextualSelect.get_execution_options()` { #textualselect-get-execution-options }

```python
TextualSelect.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](select.md#select-get-execution-options)-এর মতো।

### `TextualSelect.get_label_style()` { #textualselect-get-label-style }

```python
TextualSelect.get_label_style()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_label_style`](select.md#select-get-label-style)-এর মতো।

### `TextualSelect.inherit_cache` { #textualselect-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](select.md#select-inherit-cache)-এর মতো।

### `TextualSelect.into()` { #textualselect-into }

```python
TextualSelect.into(target, *, metadata=None, schema=None, temporary=False, if_not_exists=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.into`](select.md#select-into)-এর মতো।

### `TextualSelect.is_clause_element` { #textualselect-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](select.md#select-is-clause-element)-এর মতো।

### `TextualSelect.is_delete` { #textualselect-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](select.md#select-is-delete)-এর মতো।

### `TextualSelect.is_derived_from()` { #textualselect-is-derived-from }

```python
TextualSelect.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](select.md#select-is-derived-from)-এর মতো।

### `TextualSelect.is_dml` { #textualselect-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](select.md#select-is-dml)-এর মতো।

### `TextualSelect.is_from_statement` { #textualselect-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](select.md#select-is-from-statement)-এর মতো।

### `TextualSelect.is_insert` { #textualselect-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](select.md#select-is-insert)-এর মতো।

### `TextualSelect.is_select` { #textualselect-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](select.md#select-is-select)-এর মতো।

### `TextualSelect.is_selectable` { #textualselect-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](select.md#select-is-selectable)-এর মতো।

### `TextualSelect.is_text` { #textualselect-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](select.md#select-is-text)-এর মতো।

### `TextualSelect.is_update` { #textualselect-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](select.md#select-is-update)-এর মতো।

### `TextualSelect.label()` { #textualselect-label }

```python
TextualSelect.label(name)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.label`](select.md#select-label)-এর মতো।

### `TextualSelect.lateral()` { #textualselect-lateral }

```python
TextualSelect.lateral(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.lateral`](select.md#select-lateral)-এর মতো।

### `TextualSelect.memoized_attribute` { #textualselect-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](select.md#select-memoized-attribute)-এর মতো।

### `TextualSelect.memoized_instancemethod()` { #textualselect-memoized-instancemethod }

```python
TextualSelect.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](select.md#select-memoized-instancemethod)-এর মতো।

### `TextualSelect.name_cte_columns` { #textualselect-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](select.md#select-name-cte-columns)-এর মতো।

### `TextualSelect.options()` { #textualselect-options }

```python
TextualSelect.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](select.md#select-options)-এর মতো।

### `TextualSelect.params()` { #textualselect-params }

```python
TextualSelect.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](select.md#select-params)-এর মতো।

### `TextualSelect.replace_selectable()` { #textualselect-replace-selectable }

```python
TextualSelect.replace_selectable(old, alias)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.replace_selectable`](select.md#select-replace-selectable)-এর মতো।

### `TextualSelect.scalar_subquery()` { #textualselect-scalar-subquery }

```python
TextualSelect.scalar_subquery()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.scalar_subquery`](select.md#select-scalar-subquery)-এর মতো।

### `TextualSelect.selectable` { #textualselect-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](select.md#select-selectable)-এর মতো।

### `TextualSelect.selected_columns` { #textualselect-selected-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selected_columns`](select.md#select-selected-columns)-এর মতো।

### `TextualSelect.self_group()` { #textualselect-self-group }

```python
TextualSelect.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](select.md#select-self-group)-এর মতো।

### `TextualSelect.set_label_style()` { #textualselect-set-label-style }

```python
TextualSelect.set_label_style(style)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.set_label_style`](select.md#select-set-label-style)-এর মতো।

### `TextualSelect.stringify_dialect` { #textualselect-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](select.md#select-stringify-dialect)-এর মতো।

### `TextualSelect.subquery()` { #textualselect-subquery }

```python
TextualSelect.subquery(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.subquery`](select.md#select-subquery)-এর মতো।

### `TextualSelect.supports_execution` { #textualselect-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](select.md#select-supports-execution)-এর মতো।

### `TextualSelect.unique_params()` { #textualselect-unique-params }

```python
TextualSelect.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](select.md#select-unique-params)-এর মতো।

### `TextualSelect.uses_inspection` { #textualselect-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](select.md#select-uses-inspection)-এর মতো।

/// check | সংক্ষেপে মনে রাখুন

* ঢোকানো: `insert(Model).values(...)` অথবা `session.execute(insert(Model), [dict, ...])` (বাল্ক, দ্রুততম)।
* বদলানো: `update(Model).where(...).values(col=Model.col + 1)` (atomic)। PK ধরে আলাদা মান: `session.execute(update(Model), [{"id": .., ...}])`।
* মোছা: `delete(Model).where(...)`; `where` ভুলবেন না।
* ফল ফেরত চাইলে `returning(...)`; কতটি রো বদলাল জানতে `result.rowcount`।
* raw SQL: `text("... :param ...")` + আলাদা প্যারামিটার; কখনো f-string নয়।

///
