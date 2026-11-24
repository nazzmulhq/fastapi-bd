# Legacy Query API: session.query() আর তার ২.০ বিকল্প { #api-query }

/// warning | পুরোনো (legacy) API

`session.query(User).filter(...).all()` হলো SQLAlchemy ১.x-এর কুয়েরি লেখার ধরন। ২.০ ও ২.১-এ এটি এখনো **পুরোপুরি চলে** আর শিগগির সরানো হবে না, কিন্তু "legacy": নতুন ফিচার আসে শুধু `select()`-এ। **নতুন কোডে লিখুন** `session.scalars(select(User).where(...)).all()`। এই পেজ আছে পুরোনো কোড পড়তে ও ধাপে ধাপে বদলাতে; প্রতিটি মেথডের সাথে তার ২.০ বিকল্প দেওয়া আছে, আর পেজের শেষে একটি রূপান্তর-টেবিল।

///

/// note | এই পেজে যা আছে

* `Query`-এর **প্রতিটি** মেথড ও প্রপার্টি (৯৭টি), উদাহরণ আর ২.০ বিকল্পসহ।
* সংশ্লিষ্ট: `scoped_session.query_property()`-এর `QueryPropertyDescriptor`, `merge_frozen_result()`, `merge_result()`, `contains_alias()` / `AliasOption`, `create_session()`, আর ORM-এর `FromStatement`।
* `Query`-কে কাজে লাগায় এমন `AppenderQuery` (`lazy="dynamic"`) আছে [Relationship Collection পেজে](collections.md)।

///

`Query`-ও **নতুন অবজেক্ট ফেরত দেয়** (generative): `q = q.filter(...)` লিখতে হয়। পার্থক্য: `Query` নিজের সেশন সাথে রাখে, তাই `.all()`, `.first()`, `.count()` ডাকলেই কুয়েরি চলে।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[Select API পেজের](select.md) মতোই `User` (`id`, `name`, `addresses`) আর `Address` (`id`, `email`, `user_id`, `user`) মডেল, আর তিনজন ইউজার: রহিম (দুটি ঠিকানা), করিম, সুমি। `print(q)` দিলে তৈরি SQL দেখা যায়। `rows(q)`: ফলের রোগুলো tuple হিসেবে। PostgreSQL 16-এ চালিয়ে দেখা; legacy মেথডের সতর্কবার্তা উদাহরণে চুপ করিয়ে রাখা।

///

## `Query` { #query }

```python
from sqlalchemy.orm import Query
```

`session.query(...)` যে অবজেক্ট দেয়। আর্গুমেন্ট `select()`-এর মতো: মডেল, কলাম, এক্সপ্রেশন। একটি মডেল দিলে ফলের প্রতিটি উপাদান সেই অবজেক্ট; একাধিক দিলে `Row`। নিচের মেথডগুলোর দুই ধরন:

* **বানানোর মেথড** (`filter()`, `join()`, `order_by()` …): নতুন `Query` দেয়, এখনো কিছু চলে না। এগুলোর মানে `Select`-এর একই নামের মেথডের মতো।
* **চালানোর মেথড** (`all()`, `first()`, `one()`, `scalar()`, `count()`, `get()`, `update()`, `delete()`, আর `for x in q`): ডাকা মাত্র SQL চলে।

**উদাহরণ:**

```python
q = session.query(User).filter(User.name.like("র%")).order_by(User.id)
print([u.name for u in q.all()])   # ['রহিম']
# ২.০: session.scalars(select(User).where(User.name.like("র%")).order_by(User.id)).all()
print(rows(session.query(User.id, User.name).order_by(User.id).limit(2)))   # [(1, 'রহিম'), (2, 'করিম')]
```

### কনস্ট্রাক্টরের প্যারামিটার { #query-ctor-params }

```python
Query(entities, session=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entities` | কী আনবে: মডেল, কলাম, এক্সপ্রেশন (`session.query(...)`-এর আর্গুমেন্ট)। |
| `session` | যে সেশনে চলবে (সাধারণত `session.query()` নিজে দেয়)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #query-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_column()`](#query-add-column) | মেথড ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) একটি কলাম যোগ করে। |
| [`add_columns()`](#query-add-columns) | মেথড | ফলে আরও কলাম/এক্সপ্রেশন যোগ করে; তখন প্রতিটি ফল `Row` হয়। |
| [`add_entity()`](#query-add-entity) | মেথড | ফলে আরও একটি **মডেল** (বা `aliased()`) যোগ করে। |
| [`all()`](#query-all) | মেথড | কুয়েরি চালিয়ে সব ফল `list` হিসেবে দেয়। |
| [`apply_labels()`](#query-apply-labels) | মেথড ⚠️ deprecated | (২.০ থেকে legacy) কলামের নামে টেবিলের নাম জুড়ে দেয় (`users_id`)। |
| [`as_scalar()`](#query-as-scalar) | মেথড ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) `scalar_subquery()`-এর পুরোনো নাম। |
| [`autoflush()`](#query-autoflush) | মেথড | শুধু এই কুয়েরির জন্য autoflush চালু/বন্ধ। |
| [`column_descriptions`](#query-column-descriptions) | প্রপার্টি | ফলে কী কী কলাম/entity আসবে তার বিবরণ: প্রতিটির `name`, `type`, `aliased`, `expr`, `entity`। |
| [`correlate()`](#query-correlate) | মেথড | সাবকুয়েরি হিসেবে ব্যবহারের সময় কোন বাইরের টেবিলকে নিজের FROM থেকে বাদ দিয়ে বাইরের সাথে যুক্ত (correlate) করবে। |
| [`count()`](#query-count) | মেথড | ফলে কতগুলো রো আসবে তা গোনে। |
| [`cte()`](#query-cte) | মেথড | কুয়েরিকে CTE (`WITH ...`) বানায়। |
| [`delete()`](#query-delete) | মেথড | কুয়েরির শর্তে মেলা সব রো **একবারে** মোছে (বাল্ক DELETE), মোছা রোর সংখ্যা দেয়। |
| [`distinct()`](#query-distinct) | মেথড | `SELECT DISTINCT`। |
| [`enable_assertions()`](#query-enable-assertions) | মেথড | `False` দিলে কিছু নিরাপত্তা-পরীক্ষা বন্ধ (যেমন `limit()`-এর পর `filter()` দেওয়ায় এরর)। |
| [`enable_eagerloads()`](#query-enable-eagerloads) | মেথড | `False` দিলে eager loading (`joinedload` ইত্যাদি) বন্ধ। |
| [`except_()`](#query-except-) | মেথড | `EXCEPT`: এই কুয়েরির ফল থেকে অন্যটির ফল বাদ। |
| [`except_all()`](#query-except-all) | মেথড | `EXCEPT ALL` (ডুপ্লিকেট রেখে)। |
| [`execution_options()`](#query-execution-options) | মেথড | চালানোর অপশন: `yield_per`, `populate_existing`, `autoflush`, `stream_results` ইত্যাদি। |
| [`exists()`](#query-exists) | মেথড | কুয়েরিকে `EXISTS (SELECT 1 ...)` বানায়; সাধারণত `session.query(q.exists()).scalar()`। |
| [`ext()`](#query-ext) | মেথড | (২.১-এ নতুন) SQL সিনট্যাক্স-এক্সটেনশন যোগ করে, যেমন `postgresql.distinct_on()`। |
| [`filter()`](#query-filter) | মেথড | `WHERE` শর্ত যোগ করে (SQL এক্সপ্রেশন দিয়ে); কয়েকটি দিলে বা কয়েকবার ডাকলে `AND`। |
| [`filter_by()`](#query-filter-by) | মেথড | কীওয়ার্ড দিয়ে সমান-শর্ত: `filter_by(name="রহিম")` মানে `WHERE users.name = 'রহিম'`। |
| [`first()`](#query-first) | মেথড | `LIMIT 1` দিয়ে চালিয়ে প্রথম ফল দেয়, না থাকলে `None`। |
| [`from_statement()`](#query-from-statement) | মেথড | নিজের লেখা SQL (`text()`) বা অন্য স্টেটমেন্ট থেকে ORM অবজেক্ট লোড করে। |
| [`get()`](#query-get) | মেথড (legacy) | (২.০ থেকে legacy) primary key দিয়ে একটি অবজেক্ট; না থাকলে `None`। |
| [`get_children()`](#query-get-children) | মেথড (internal) | ভেতরের এক্সপ্রেশন-গাছের সরাসরি উপাদানগুলো দেয় (SQLAlchemy-র traversal ব্যবস্থার অংশ)। |
| [`get_execution_options()`](#query-get-execution-options) | মেথড | `execution_options()`-এ দেওয়া অপশনগুলো (immutable dict)। |
| [`get_label_style`](#query-get-label-style) | প্রপার্টি | বর্তমান label style (`set_label_style()` দেখুন)। |
| [`group_by()`](#query-group-by) | মেথড | `GROUP BY`। |
| [`having()`](#query-having) | মেথড | `HAVING` (group-এর ওপর শর্ত)। |
| [`instances()`](#query-instances) | মেথড ⚠️ deprecated | (২.০ থেকে বাতিলের পথে) একটি কাঁচা `CursorResult` থেকে ORM অবজেক্ট বানায়। |
| [`intersect()`](#query-intersect) | মেথড | `INTERSECT`: দুই কুয়েরির সাধারণ ফল। |
| [`intersect_all()`](#query-intersect-all) | মেথড | `INTERSECT ALL` (ডুপ্লিকেট রেখে)। |
| [`is_single_entity`](#query-is-single-entity) | প্রপার্টি | প্রতিটি ফল একটি অবজেক্ট (`True`) নাকি `Row` (`False`)। |
| [`join()`](#query-join) | মেথড | `INNER JOIN`। |
| [`label()`](#query-label) | মেথড | কুয়েরিকে নাম-দেওয়া scalar subquery বানায়: `(SELECT ...) AS নাম`। |
| [`lazy_loaded_from`](#query-lazy-loaded-from) | প্রপার্টি ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) কুয়েরিটি lazy load-এর জন্য চললে কোন অবজেক্টের (`InstanceState`) জন্য। |
| [`limit()`](#query-limit) | মেথড | `LIMIT n`। |
| [`load_options`](#query-load-options) | অ্যাট্রিবিউট (internal) | ORM-এর ভেতরের লোড-অপশন (populate_existing, autoflush, yield_per … একসাথে রাখা অবজেক্ট)। |
| [`logger`](#query-logger) | অ্যাট্রিবিউট (internal) | এই ক্লাসের `logging.Logger` (`sqlalchemy.orm.query.Query`)। |
| [`logging_name`](#query-logging-name) | অ্যাট্রিবিউট (internal) | লগে দেখানোর বাড়তি নাম (সাধারণত `None`)। |
| [`merge_result()`](#query-merge-result) | মেথড (legacy) | (২.০ থেকে legacy) অন্য জায়গা থেকে আনা (যেমন ক্যাশ করা) ফলকে এই সেশনে মিশিয়ে persistent অবজেক্ট বানায়। |
| [`offset()`](#query-offset) | মেথড | `OFFSET n` (প্রথম n রো বাদ)। |
| [`one()`](#query-one) | মেথড | ঠিক একটি ফল; না থাকলে `NoResultFound`, একাধিক হলে `MultipleResultsFound`। |
| [`one_or_none()`](#query-one-or-none) | মেথড | শূন্য বা একটি ফল (না থাকলে `None`, একাধিক হলে `MultipleResultsFound`)। |
| [`only_return_tuples()`](#query-only-return-tuples) | মেথড | `True` দিলে একটি মডেল চাইলেও প্রতিটি ফল `Row` (tuple) হবে। |
| [`options()`](#query-options) | মেথড | লোডার অপশন দেয়: `selectinload()`, `joinedload()`, `load_only()` … ২.০: `select(...).options(...)`। |
| [`order_by()`](#query-order-by) | মেথড | `ORDER BY`; `None` দিলে আগের order_by মুছে যায়। |
| [`outerjoin()`](#query-outerjoin) | মেথড | `LEFT OUTER JOIN`: বাঁ দিকের সব রো, মিল না থাকলে ডান দিক `NULL`। |
| [`params()`](#query-params) | মেথড | `text()` বা `bindparam()`-এর নামযুক্ত প্যারামিটারের মান দেয়। |
| [`populate_existing()`](#query-populate-existing) | মেথড | সেশনে আগে থেকে থাকা অবজেক্টগুলোও ডেটাবেসের নতুন মান দিয়ে **ওভাররাইট** করে (সাধারণত identity map-এর অবজেক্ট আর লোড হয় না)। |
| [`prefix_with()`](#query-prefix-with) | মেথড | `SELECT`-এর ঠিক পরে কিছু বসায়, যেমন MySQL-এর `SQL_NO_CACHE`। |
| [`reset_joinpoint()`](#query-reset-joinpoint) | মেথড | "join point" আবার মূল entity-তে ফেরায় (পুরোনো `join(..., aliased=True)` ধারার সাথে)। |
| [`scalar()`](#query-scalar) | মেথড | প্রথম রো-র প্রথম কলাম; রো না থাকলে `None`, **একাধিক রো হলে `MultipleResultsFound`**। |
| [`scalar_subquery()`](#query-scalar-subquery) | মেথড | কুয়েরিকে scalar subquery বানায় (একটি মান দেয়, অন্য কুয়েরির কলাম/শর্তে বসানোর জন্য)। |
| [`select_from()`](#query-select-from) | মেথড | FROM স্পষ্ট করে দেয়; বিশেষত যখন SELECT-এর প্রথম জিনিস দিয়ে join শুরু করা যায় না। |
| [`selectable`](#query-selectable) | প্রপার্টি | `statement`-এর আরেক নাম: কুয়েরির ভেতরের `Select` অবজেক্ট। |
| [`set_label_style()`](#query-set-label-style) | মেথড | কলামের নামের ধরন: `LABEL_STYLE_TABLENAME_PLUS_COL` দিলে `users_id`। |
| [`slice()`](#query-slice) | মেথড | Python slice-এর মতো `LIMIT`/`OFFSET`: `slice(1, 3)` মানে ২য় আর ৩য়। |
| [`statement`](#query-statement) | প্রপার্টি | কুয়েরির **২.০-ধাঁচের `Select`** অবজেক্ট। |
| [`subquery()`](#query-subquery) | মেথড | কুয়েরিকে নাম-দেওয়া সাবকুয়েরি (`(SELECT ...) AS নাম`) বানায়, FROM-এ বা join-এ ব্যবহারের জন্য। |
| [`suffix_with()`](#query-suffix-with) | মেথড | পুরো স্টেটমেন্টের শেষে কিছু বসায়। |
| [`tuples()`](#query-tuples) | মেথড ⚠️ deprecated | (২.০-তে আসা, ২.১-এ বাতিলের পথে) টাইপ-চেকারের জন্য ফলকে `Tuple` হিসেবে চিহ্নিত করত। |
| [`union()`](#query-union) | মেথড | `UNION`: দুই কুয়েরির ফল একসাথে (ডুপ্লিকেট বাদ)। |
| [`union_all()`](#query-union-all) | মেথড | `UNION ALL` (ডুপ্লিকেট রেখে)। |
| [`update()`](#query-update) | মেথড | কুয়েরির শর্তে মেলা সব রো **একবারে** হালনাগাদ (বাল্ক UPDATE), বদলানো রোর সংখ্যা দেয়। |
| [`value()`](#query-value) | মেথড ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) একটি কলামের প্রথম মান। |
| [`values()`](#query-values) | মেথড ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) নির্দিষ্ট কলামগুলোর ফলের iterator। |
| [`where()`](#query-where) | মেথড | `filter()`-এর আরেক নাম (১.৪+), ২.০ ধাঁচের সাথে মিল রাখতে। |
| [`whereclause`](#query-whereclause) | প্রপার্টি | বর্তমান WHERE শর্ত (এক্সপ্রেশন), না থাকলে `None`। |
| [`with_entities()`](#query-with-entities) | মেথড | SELECT তালিকা পুরো বদলে দেয় (শর্ত, join একই থাকে)। |
| [`with_for_update()`](#query-with-for-update) | মেথড | `SELECT ... FOR UPDATE` (রো লক)। |
| [`with_hint()`](#query-with-hint) | মেথড | নির্দিষ্ট টেবিলের জন্য ডেটাবেস-বিশেষ "hint" (যেমন MySQL `USE INDEX`, Oracle `/*+ ... */`)। |
| [`with_labels()`](#query-with-labels) | মেথড ⚠️ deprecated | (২.০ থেকে legacy) `apply_labels()`-এর মতো। |
| [`with_parent()`](#query-with-parent) | মেথড (legacy) | (২.০ থেকে legacy) একটি অবজেক্টের সাথে relationship-এ যুক্ত রোগুলো: "রহিমের ঠিকানাগুলো"। |
| [`with_session()`](#query-with-session) | মেথড | কুয়েরিটি অন্য একটি সেশনে চালানোর জন্য নতুন `Query` দেয়। |
| [`with_statement_hint()`](#query-with-statement-hint) | মেথড | পুরো স্টেটমেন্টের জন্য hint (যেমন Oracle-এর optimizer hint)। |
| [`with_transformation()`](#query-with-transformation) | মেথড | একটি ফাংশন (`Query → Query`) প্রয়োগ করে: বারবার লাগে এমন শর্ত বা অপশন এক জায়গায় রাখার কৌশল। |
| [`yield_per()`](#query-yield-per) | মেথড | বড় ফলাফল একবারে মেমোরিতে না এনে `count`-টি করে ব্যাচে আনে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Query`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

///

### `Query.add_column()` { #query-add-column }

```python
Query.add_column(column)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) একটি কলাম যোগ করে। বদলে `add_columns()`।

**উদাহরণ:**

```python
print(rows(session.query(User.name).add_column(User.id).filter(User.id == 2)))   # [('করিম', 2)]
```

### `Query.add_columns()` { #query-add-columns }

```python
Query.add_columns(*column)
```

**ধরন:** মেথড

ফলে আরও কলাম/এক্সপ্রেশন যোগ করে; তখন প্রতিটি ফল `Row` হয়। ২.০: `select(...).add_columns(...)`।

**উদাহরণ:**

```python
q = session.query(User.name).add_columns(func.length(User.name)).order_by(User.id)
print(rows(q))   # [('রহিম', 4), ('করিম', 4), ('সুমি', 4)]
```

### `Query.add_entity()` { #query-add-entity }

```python
Query.add_entity(entity, alias=None)
```

**ধরন:** মেথড

ফলে আরও একটি **মডেল** (বা `aliased()`) যোগ করে। ২.০: `select(User, Address)`।

**উদাহরণ:**

```python
q = session.query(User).add_entity(Address).join(User.addresses).order_by(Address.id)
print([(u.name, a.email) for u, a in q])   # [('রহিম', 'rahim@example.com'), ('রহিম', 'rahim@work.com')]
```

### `Query.all()` { #query-all }

```python
Query.all()
```

**ধরন:** মেথড

কুয়েরি চালিয়ে সব ফল `list` হিসেবে দেয়। একটি মডেল হলে অবজেক্টের তালিকা, নইলে `Row`-এর তালিকা। ২.০: `session.scalars(stmt).all()` বা `session.execute(stmt).all()`।

**উদাহরণ:**

```python
print(len(session.query(User).all()), session.query(User.name).order_by(User.id).all()[0])   # 3 ('রহিম',)
```

### `Query.apply_labels()` { #query-apply-labels }

```python
Query.apply_labels()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) কলামের নামে টেবিলের নাম জুড়ে দেয় (`users_id`)। বদলে `set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)`।

**উদাহরণ:**

```python
print(session.query(User.id).apply_labels().statement)   # SELECT users.id AS users_id
# FROM users
```

### `Query.as_scalar()` { #query-as-scalar }

```python
Query.as_scalar()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) `scalar_subquery()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(type(session.query(func.count(User.id)).as_scalar()).__name__)   # ScalarSelect
```

### `Query.autoflush()` { #query-autoflush }

```python
Query.autoflush(setting)
```

**ধরন:** মেথড

শুধু এই কুয়েরির জন্য autoflush চালু/বন্ধ। ২.০: `select(...).execution_options(autoflush=False)`।

**উদাহরণ:**

```python
session.add(User(name="নতুন"))
print(session.query(User).autoflush(False).count(), session.query(User).count())   # 3 4
```

### `Query.column_descriptions` { #query-column-descriptions }

**ধরন:** প্রপার্টি

ফলে কী কী কলাম/entity আসবে তার বিবরণ: প্রতিটির `name`, `type`, `aliased`, `expr`, `entity`। ২.০: `select(...).column_descriptions`।

**উদাহরণ:**

```python
d = session.query(User, User.id).column_descriptions
print([(x["name"], x["entity"].__name__) for x in d])   # [('User', 'User'), ('id', 'User')]
```

### `Query.correlate()` { #query-correlate }

```python
Query.correlate(*fromclauses)
```

**ধরন:** মেথড

সাবকুয়েরি হিসেবে ব্যবহারের সময় কোন বাইরের টেবিলকে নিজের FROM থেকে বাদ দিয়ে বাইরের সাথে যুক্ত (correlate) করবে।

**উদাহরণ:**

```python
sub = session.query(func.count(Address.id)).filter(Address.user_id == User.id).correlate(User).scalar_subquery()
print(rows(session.query(User.name, sub).order_by(User.id)))   # [('রহিম', 2), ('করিম', 0), ('সুমি', 0)]
```

### `Query.count()` { #query-count }

```python
Query.count()
```

**ধরন:** মেথড

ফলে কতগুলো রো আসবে তা গোনে। ভেতরে `SELECT count(*) FROM (আপনার কুয়েরি)` চালায়। ২.০: `session.scalar(select(func.count()).select_from(User))`।

**উদাহরণ:**

```python
print(session.query(User).count(), session.query(Address).filter(Address.user_id == 1).count())   # 3 2
```

### `Query.cte()` { #query-cte }

```python
Query.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কুয়েরিকে CTE (`WITH ...`) বানায়। ২.০: `select(...).cte()`। `recursive=True` দিলে recursive CTE।

**উদাহরণ:**

```python
c = session.query(User.id, User.name).filter(User.id > 1).cte("others")
print(rows(session.query(c.c.name).order_by(c.c.id)))   # [('করিম',), ('সুমি',)]
```

### `Query.delete()` { #query-delete }

```python
Query.delete(synchronize_session='auto', delete_args=None)
```

**ধরন:** মেথড

কুয়েরির শর্তে মেলা সব রো **একবারে** মোছে (বাল্ক DELETE), মোছা রোর সংখ্যা দেয়। `synchronize_session` ("auto", "evaluate", "fetch", `False`): সেশনে থাকা অবজেক্টের সাথে মেলানোর কৌশল। (২.০.৩৭) `delete_args`: ডায়ালেক্ট-বিশেষ অপশন। ২.০: `session.execute(delete(Address).where(...))`।

**উদাহরণ:**

```python
n = session.query(Address).filter(Address.email.like("%work%")).delete()
print(n, session.query(Address).count())   # 1 1
```

### `Query.distinct()` { #query-distinct }

```python
Query.distinct(*expr)
```

**ধরন:** মেথড

`SELECT DISTINCT`। ORDER BY-এর কলাম নিজে থেকে SELECT-এ যোগ করে (এই আচরণ ২.০-তে বাতিলের পথে)। ২.১-এ `distinct(col)` (PostgreSQL DISTINCT ON) দেওয়াও বাতিলের পথে। ২.০: `select(...).distinct()`।

**উদাহরণ:**

```python
print(rows(session.query(Address.user_id).distinct()))   # [(1,)]
```

### `Query.enable_assertions()` { #query-enable-assertions }

```python
Query.enable_assertions(value)
```

**ধরন:** মেথড

`False` দিলে কিছু নিরাপত্তা-পরীক্ষা বন্ধ (যেমন `limit()`-এর পর `filter()` দেওয়ায় এরর)। শুধু কাস্টম `Query` সাবক্লাসের জন্য।

**উদাহরণ:**

```python
q = session.query(User).limit(2)
try:
    q.filter(User.id > 1)
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError
print(q.enable_assertions(False).filter(User.id > 1).count())   # 2
```

### `Query.enable_eagerloads()` { #query-enable-eagerloads }

```python
Query.enable_eagerloads(value)
```

**ধরন:** মেথড

`False` দিলে eager loading (`joinedload` ইত্যাদি) বন্ধ। কুয়েরিটিকে সাবকুয়েরি হিসেবে ব্যবহারের সময় অপ্রয়োজনীয় JOIN এড়াতে।

**উদাহরণ:**

```python
q = session.query(User).options(joinedload(User.addresses))
print("JOIN" in str(q), "JOIN" in str(q.enable_eagerloads(False)))   # True False
```

### `Query.except_()` { #query-except- }

```python
Query.except_(*q)
```

**ধরন:** মেথড

`EXCEPT`: এই কুয়েরির ফল থেকে অন্যটির ফল বাদ। ২.০: `except_(stmt1, stmt2)`।

**উদাহরণ:**

```python
q = session.query(User.name).except_(session.query(User.name).filter(User.id == 1))
print(sorted(n for (n,) in q))   # ['করিম', 'সুমি']
```

### `Query.except_all()` { #query-except-all }

```python
Query.except_all(*q)
```

**ধরন:** মেথড

`EXCEPT ALL` (ডুপ্লিকেট রেখে)।

**উদাহরণ:**

```python
q = session.query(Address.user_id).except_all(session.query(literal(1)))
print(rows(q))   # [(1,)]
```

### `Query.execution_options()` { #query-execution-options }

```python
Query.execution_options(**kwargs)
```

**ধরন:** মেথড

চালানোর অপশন: `yield_per`, `populate_existing`, `autoflush`, `stream_results` ইত্যাদি। ২.০: `select(...).execution_options(...)` বা `session.execute(stmt, execution_options={...})`।

**উদাহরণ:**

```python
q = session.query(User).execution_options(populate_existing=True)
print(q.get_execution_options()["populate_existing"])   # True
```

### `Query.exists()` { #query-exists }

```python
Query.exists()
```

**ধরন:** মেথড

কুয়েরিকে `EXISTS (SELECT 1 ...)` বানায়; সাধারণত `session.query(q.exists()).scalar()`। ২.০: `session.scalar(select(exists().where(...)))`।

**উদাহরণ:**

```python
q = session.query(User).filter(User.name == "করিম")
print(session.query(q.exists()).scalar())   # True
```

### `Query.ext()` { #query-ext }

```python
Query.ext(extension)
```

**ধরন:** মেথড

(২.১-এ নতুন) SQL সিনট্যাক্স-এক্সটেনশন যোগ করে, যেমন `postgresql.distinct_on()`। `Select.ext()`-এর মতো।

**উদাহরণ:**

```python
from sqlalchemy.dialects.postgresql import distinct_on
q = session.query(Address.user_id, Address.email).ext(distinct_on(Address.user_id)).order_by(Address.user_id, Address.email)
print(rows(q))   # [(1, 'rahim@example.com')]
```

### `Query.filter()` { #query-filter }

```python
Query.filter(*criterion)
```

**ধরন:** মেথড

`WHERE` শর্ত যোগ করে (SQL এক্সপ্রেশন দিয়ে); কয়েকটি দিলে বা কয়েকবার ডাকলে `AND`। ২.০: `select(...).where(...)`।

**উদাহরণ:**

```python
print([u.name for u in session.query(User).filter(User.id > 1, User.name != "সুমি")])   # ['করিম']
```

### `Query.filter_by()` { #query-filter-by }

```python
Query.filter_by(**kwargs)
```

**ধরন:** মেথড

কীওয়ার্ড দিয়ে সমান-শর্ত: `filter_by(name="রহিম")` মানে `WHERE users.name = 'রহিম'`। শেষ যে entity join হয়েছে তার কলাম ধরে। ২.০: `select(...).filter_by(...)`।

**উদাহরণ:**

```python
print(session.query(User).filter_by(name="রহিম").one().id)   # 1
```

### `Query.first()` { #query-first }

```python
Query.first()
```

**ধরন:** মেথড

`LIMIT 1` দিয়ে চালিয়ে প্রথম ফল দেয়, না থাকলে `None`। ২.০: `session.scalars(stmt).first()` (তবে সেটা LIMIT যোগ করে না; দরকার হলে `.limit(1)`)।

**উদাহরণ:**

```python
print(session.query(User).order_by(User.id.desc()).first().name, session.query(User).filter(User.id == 99).first())   # সুমি None
```

### `Query.from_statement()` { #query-from-statement }

```python
Query.from_statement(statement)
```

**ধরন:** মেথড

নিজের লেখা SQL (`text()`) বা অন্য স্টেটমেন্ট থেকে ORM অবজেক্ট লোড করে। ২.০: `select(User).from_statement(text(...))`।

**উদাহরণ:**

```python
q = session.query(User).from_statement(text("SELECT * FROM users WHERE id = :id")).params(id=2)
print(q.one().name)   # করিম
```

### `Query.get()` { #query-get }

```python
Query.get(ident)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) primary key দিয়ে একটি অবজেক্ট; না থাকলে `None`। আগে identity map দেখে, থাকলে SQL চালায় না। বদলে `session.get(User, 1)`।

**উদাহরণ:**

```python
print(session.query(User).get(1).name, session.get(User, 1).name)   # রহিম রহিম
```

### `Query.get_children()` { #query-get-children }

```python
Query.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের এক্সপ্রেশন-গাছের সরাসরি উপাদানগুলো দেয় (SQLAlchemy-র traversal ব্যবস্থার অংশ)।

**উদাহরণ:**

```python
print(type(list(session.query(User).get_children())).__name__)   # list
```

### `Query.get_execution_options()` { #query-get-execution-options }

```python
Query.get_execution_options()
```

**ধরন:** মেথড

`execution_options()`-এ দেওয়া অপশনগুলো (immutable dict)।

**উদাহরণ:**

```python
print(dict(session.query(User).execution_options(yield_per=10).get_execution_options()))   # {'yield_per': 10}
```

### `Query.get_label_style` { #query-get-label-style }

**ধরন:** প্রপার্টি

বর্তমান label style (`set_label_style()` দেখুন)।

**উদাহরণ:**

```python
print(session.query(User).get_label_style)   # SelectLabelStyle.LABEL_STYLE_LEGACY_ORM
```

### `Query.group_by()` { #query-group-by }

```python
Query.group_by(*clauses)
```

**ধরন:** মেথড

`GROUP BY`। `None` দিলে আগের group_by মুছে যায়। ২.০: `select(...).group_by(...)`।

**উদাহরণ:**

```python
q = session.query(Address.user_id, func.count()).group_by(Address.user_id)
print(rows(q))   # [(1, 2)]
```

### `Query.having()` { #query-having }

```python
Query.having(*having)
```

**ধরন:** মেথড

`HAVING` (group-এর ওপর শর্ত)।

**উদাহরণ:**

```python
q = session.query(User.name).join(User.addresses).group_by(User.name).having(func.count(Address.id) > 1)
print(rows(q))   # [('রহিম',)]
```

### `Query.instances()` { #query-instances }

```python
Query.instances(result_proxy, context=None)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে বাতিলের পথে) একটি কাঁচা `CursorResult` থেকে ORM অবজেক্ট বানায়। বদলে `select(User).from_statement(...)` বা `aliased()`।

**উদাহরণ:**

```python
with engine.connect() as c:
    cr = c.execute(select(User.__table__).order_by(User.__table__.c.id))   # কাঁচা text() হলে কলাম মেলে না
    print([u.name for u in session.query(User).instances(cr)])   # ['রহিম', 'করিম', 'সুমি']
```

### `Query.intersect()` { #query-intersect }

```python
Query.intersect(*q)
```

**ধরন:** মেথড

`INTERSECT`: দুই কুয়েরির সাধারণ ফল।

**উদাহরণ:**

```python
q = session.query(User.id).intersect(session.query(Address.user_id))
print(rows(q))   # [(1,)]
```

### `Query.intersect_all()` { #query-intersect-all }

```python
Query.intersect_all(*q)
```

**ধরন:** মেথড

`INTERSECT ALL` (ডুপ্লিকেট রেখে)।

**উদাহরণ:**

```python
q = session.query(Address.user_id).intersect_all(session.query(User.id))
print(rows(q))   # [(1,)]
```

### `Query.is_single_entity` { #query-is-single-entity }

**ধরন:** প্রপার্টি

প্রতিটি ফল একটি অবজেক্ট (`True`) নাকি `Row` (`False`)।

**উদাহরণ:**

```python
print(session.query(User).is_single_entity, session.query(User, Address).is_single_entity)   # True False
```

### `Query.join()` { #query-join }

```python
Query.join(target, onclause=None, *, isouter=False, full=False)
```

**ধরন:** মেথড

`INNER JOIN`। সাধারণত relationship দিয়ে: `join(User.addresses)`; বা টার্গেট আর ON শর্ত: `join(Address, Address.user_id == User.id)`। `isouter=True` → LEFT JOIN, `full=True` → FULL JOIN। ২.০: `select(...).join(...)`। (১.x-এর `join("addresses")` স্ট্রিং আর `aliased=True` ২.০-তে সরানো হয়েছে।)

**উদাহরণ:**

```python
q = session.query(User.name, Address.email).join(User.addresses).order_by(Address.id)
print(rows(q)[0])   # ('রহিম', 'rahim@example.com')
```

### `Query.label()` { #query-label }

```python
Query.label(name)
```

**ধরন:** মেথড

কুয়েরিকে নাম-দেওয়া scalar subquery বানায়: `(SELECT ...) AS নাম`।

**উদাহরণ:**

```python
total = session.query(func.count(Address.id)).filter(Address.user_id == User.id).label("n")
print(rows(session.query(User.name, total).filter(User.id == 1)))   # [('রহিম', 2)]
```

### `Query.lazy_loaded_from` { #query-lazy-loaded-from }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) কুয়েরিটি lazy load-এর জন্য চললে কোন অবজেক্টের (`InstanceState`) জন্য। বদলে `do_orm_execute` ইভেন্টে `ORMExecuteState.lazy_loaded_from`।

**উদাহরণ:**

```python
print(session.query(User).lazy_loaded_from)   # None
```

### `Query.limit()` { #query-limit }

```python
Query.limit(limit)
```

**ধরন:** মেথড

`LIMIT n`। ২.০: `select(...).limit(n)`।

**উদাহরণ:**

```python
print(len(session.query(User).limit(2).all()))   # 2
```

### `Query.load_options` { #query-load-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ORM-এর ভেতরের লোড-অপশন (populate_existing, autoflush, yield_per … একসাথে রাখা অবজেক্ট)।

**উদাহরণ:**

```python
print(session.query(User).populate_existing().load_options._populate_existing)   # True
```

### `Query.logger` { #query-logger }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই ক্লাসের `logging.Logger` (`sqlalchemy.orm.query.Query`)।

**উদাহরণ:**

```python
print(Query.logger.name)   # sqlalchemy.orm.query.Query
```

### `Query.logging_name` { #query-logging-name }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লগে দেখানোর বাড়তি নাম (সাধারণত `None`)।

**উদাহরণ:**

```python
print(Query.logging_name)   # None
```

### `Query.merge_result()` { #query-merge-result }

```python
Query.merge_result(iterator, load=True)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) অন্য জায়গা থেকে আনা (যেমন ক্যাশ করা) ফলকে এই সেশনে মিশিয়ে persistent অবজেক্ট বানায়। বদলে [`merge_frozen_result()`](#merge-frozen-result)।

**উদাহরণ:**

```python
detached = Session(engine).query(User).filter(User.id == 2).all()   # অন্য সেশনের (বা ক্যাশের) অবজেক্ট
s2 = Session(engine)
merged = list(s2.query(User).merge_result(detached))
print([u.name for u in merged], merged[0] in s2)   # ['করিম'] True
```

### `Query.offset()` { #query-offset }

```python
Query.offset(offset)
```

**ধরন:** মেথড

`OFFSET n` (প্রথম n রো বাদ)। ২.০: `select(...).offset(n)`।

**উদাহরণ:**

```python
print([u.name for u in session.query(User).order_by(User.id).offset(1)])   # ['করিম', 'সুমি']
```

### `Query.one()` { #query-one }

```python
Query.one()
```

**ধরন:** মেথড

ঠিক একটি ফল; না থাকলে `NoResultFound`, একাধিক হলে `MultipleResultsFound`। ২.০: `session.scalars(stmt).one()` বা `session.execute(stmt).scalar_one()`।

**উদাহরণ:**

```python
print(session.query(User).filter(User.id == 3).one().name)   # সুমি
```

### `Query.one_or_none()` { #query-one-or-none }

```python
Query.one_or_none()
```

**ধরন:** মেথড

শূন্য বা একটি ফল (না থাকলে `None`, একাধিক হলে `MultipleResultsFound`)। ২.০: `scalar_one_or_none()`।

**উদাহরণ:**

```python
print(session.query(User).filter(User.id == 99).one_or_none())   # None
```

### `Query.only_return_tuples()` { #query-only-return-tuples }

```python
Query.only_return_tuples(value)
```

**ধরন:** মেথড

`True` দিলে একটি মডেল চাইলেও প্রতিটি ফল `Row` (tuple) হবে।

**উদাহরণ:**

```python
print(type(session.query(User).only_return_tuples(True).first()).__name__)   # Row
```

### `Query.options()` { #query-options }

```python
Query.options(*args)
```

**ধরন:** মেথড

লোডার অপশন দেয়: `selectinload()`, `joinedload()`, `load_only()` … ২.০: `select(...).options(...)`।

**উদাহরণ:**

```python
u = session.query(User).options(selectinload(User.addresses)).filter(User.id == 1).one()
print("addresses" in u.__dict__)   # True  (আগেই লোড হয়ে গেছে)
```

### `Query.order_by()` { #query-order-by }

```python
Query.order_by(*clauses)
```

**ধরন:** মেথড

`ORDER BY`; `None` দিলে আগের order_by মুছে যায়। ২.০: `select(...).order_by(...)`।

**উদাহরণ:**

```python
print([u.name for u in session.query(User).order_by(User.name.desc())])   # ['সুমি', 'রহিম', 'করিম']
```

### `Query.outerjoin()` { #query-outerjoin }

```python
Query.outerjoin(target, onclause=None, *, full=False)
```

**ধরন:** মেথড

`LEFT OUTER JOIN`: বাঁ দিকের সব রো, মিল না থাকলে ডান দিক `NULL`। ২.০: `select(...).outerjoin(...)`।

**উদাহরণ:**

```python
q = session.query(User.name, func.count(Address.id)).outerjoin(User.addresses).group_by(User.id, User.name).order_by(User.id)
print(rows(q))   # [('রহিম', 2), ('করিম', 0), ('সুমি', 0)]
```

### `Query.params()` { #query-params }

```python
Query.params(**kw)
```

**ধরন:** মেথড

`text()` বা `bindparam()`-এর নামযুক্ত প্যারামিটারের মান দেয়। ২.০: `session.execute(stmt, {"id": 2})`।

**উদাহরণ:**

```python
q = session.query(User).filter(text("id = :uid")).params(uid=2)
print(q.one().name)   # করিম
```

### `Query.populate_existing()` { #query-populate-existing }

```python
Query.populate_existing()
```

**ধরন:** মেথড

সেশনে আগে থেকে থাকা অবজেক্টগুলোও ডেটাবেসের নতুন মান দিয়ে **ওভাররাইট** করে (সাধারণত identity map-এর অবজেক্ট আর লোড হয় না)। ২.০: `execution_options(populate_existing=True)`।

**উদাহরণ:**

```python
u = session.get(User, 1)
u.name = "অস্থায়ী"                        # সেশনে বদলালাম, flush করিনি
session.query(User).populate_existing().filter(User.id == 1).execution_options(autoflush=False).one()
print(u.name)   # রহিম  (ডেটাবেসের মান দিয়ে ফিরে গেল)
```

### `Query.prefix_with()` { #query-prefix-with }

```python
Query.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

`SELECT`-এর ঠিক পরে কিছু বসায়, যেমন MySQL-এর `SQL_NO_CACHE`। `dialect=` দিলে শুধু সেই ডেটাবেসে।

**উদাহরণ:**

```python
print(str(session.query(User.id).prefix_with("/* টেস্ট */")).splitlines()[0])   # SELECT /* টেস্ট */ users.id AS users_id
```

### `Query.reset_joinpoint()` { #query-reset-joinpoint }

```python
Query.reset_joinpoint()
```

**ধরন:** মেথড

"join point" আবার মূল entity-তে ফেরায় (পুরোনো `join(..., aliased=True)` ধারার সাথে)। ২.০-তে join point ধারণাটাই নেই, তাই এখন প্রায় কিছুই করে না।

**উদাহরণ:**

```python
q = session.query(User).join(User.addresses).reset_joinpoint().filter(User.id == 1)
print(q.count())   # 2
```

### `Query.scalar()` { #query-scalar }

```python
Query.scalar()
```

**ধরন:** মেথড

প্রথম রো-র প্রথম কলাম; রো না থাকলে `None`, **একাধিক রো হলে `MultipleResultsFound`**। ২.০: `session.scalar(stmt)` (সেটা একাধিক রো-তেও প্রথমটি দেয়)।

**উদাহরণ:**

```python
print(session.query(func.count(User.id)).scalar(), session.query(User.id).filter(User.id == 99).scalar())   # 3 None
```

### `Query.scalar_subquery()` { #query-scalar-subquery }

```python
Query.scalar_subquery()
```

**ধরন:** মেথড

কুয়েরিকে scalar subquery বানায় (একটি মান দেয়, অন্য কুয়েরির কলাম/শর্তে বসানোর জন্য)।

**উদাহরণ:**

```python
max_id = session.query(func.max(User.id)).scalar_subquery()
print([u.name for u in session.query(User).filter(User.id == max_id)])   # ['সুমি']
```

### `Query.select_from()` { #query-select-from }

```python
Query.select_from(*from_obj)
```

**ধরন:** মেথড

FROM স্পষ্ট করে দেয়; বিশেষত যখন SELECT-এর প্রথম জিনিস দিয়ে join শুরু করা যায় না।

**উদাহরণ:**

```python
q = session.query(Address.email).select_from(User).join(User.addresses).filter(User.name == "রহিম").order_by(Address.id)
print(rows(q))   # [('rahim@example.com',), ('rahim@work.com',)]
```

### `Query.selectable` { #query-selectable }

**ধরন:** প্রপার্টি

`statement`-এর আরেক নাম: কুয়েরির ভেতরের `Select` অবজেক্ট।

**উদাহরণ:**

```python
print(type(session.query(User).selectable).__name__)   # Select
```

### `Query.set_label_style()` { #query-set-label-style }

```python
Query.set_label_style(style)
```

**ধরন:** মেথড

কলামের নামের ধরন: `LABEL_STYLE_TABLENAME_PLUS_COL` দিলে `users_id`। পুরোনো `apply_labels()`-এর বদলে।

**উদাহরণ:**

```python
print(session.query(User.id).set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL).statement)   # SELECT users.id AS users_id
# FROM users
```

### `Query.slice()` { #query-slice }

```python
Query.slice(start, stop)
```

**ধরন:** মেথড

Python slice-এর মতো `LIMIT`/`OFFSET`: `slice(1, 3)` মানে ২য় আর ৩য়। `q[1:3]` লিখলেও একই।

**উদাহরণ:**

```python
print([u.name for u in session.query(User).order_by(User.id).slice(1, 3)], [u.name for u in session.query(User).order_by(User.id)[0:1]])
# ['করিম', 'সুমি'] ['রহিম']
```

### `Query.statement` { #query-statement }

**ধরন:** প্রপার্টি

কুয়েরির **২.০-ধাঁচের `Select`** অবজেক্ট। পুরোনো কোড ধীরে ধীরে বদলাতে খুব কাজের: `session.execute(q.statement)`।

**উদাহরণ:**

```python
stmt = session.query(User).filter(User.id == 2).statement
print(session.scalars(stmt).one().name)   # করিম
```

### `Query.subquery()` { #query-subquery }

```python
Query.subquery(name=None, with_labels=False, reduce_columns=False)
```

**ধরন:** মেথড

কুয়েরিকে নাম-দেওয়া সাবকুয়েরি (`(SELECT ...) AS নাম`) বানায়, FROM-এ বা join-এ ব্যবহারের জন্য। ২.০: `select(...).subquery()`।

**উদাহরণ:**

```python
sq = session.query(Address.user_id, func.count().label("n")).group_by(Address.user_id).subquery()
print(rows(session.query(User.name, sq.c.n).join(sq, sq.c.user_id == User.id)))   # [('রহিম', 2)]
```

### `Query.suffix_with()` { #query-suffix-with }

```python
Query.suffix_with(*suffixes, dialect='*')
```

**ধরন:** মেথড

পুরো স্টেটমেন্টের শেষে কিছু বসায়।

**উদাহরণ:**

```python
print(str(session.query(User.id).suffix_with("-- শেষ")).splitlines()[-1])   # FROM users -- শেষ
```

### `Query.tuples()` { #query-tuples }

```python
Query.tuples()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.০-তে আসা, ২.১-এ বাতিলের পথে) টাইপ-চেকারের জন্য ফলকে `Tuple` হিসেবে চিহ্নিত করত। ২.১-এ `Row` নিজেই tuple-এর মতো টাইপ বোঝে, তাই দরকার নেই।

**উদাহরণ:**

```python
print(session.query(User.id, User.name).tuples().first())   # (1, 'রহিম')
```

### `Query.union()` { #query-union }

```python
Query.union(*q)
```

**ধরন:** মেথড

`UNION`: দুই কুয়েরির ফল একসাথে (ডুপ্লিকেট বাদ)। ২.০: `union(stmt1, stmt2)`।

**উদাহরণ:**

```python
q = session.query(User.name).filter(User.id == 1).union(session.query(User.name).filter(User.id == 3))
print(sorted(n for (n,) in q))   # ['রহিম', 'সুমি']
```

### `Query.union_all()` { #query-union-all }

```python
Query.union_all(*q)
```

**ধরন:** মেথড

`UNION ALL` (ডুপ্লিকেট রেখে)।

**উদাহরণ:**

```python
q = session.query(literal(1)).union_all(session.query(literal(1)))
print(len(q.all()))   # 2
```

### `Query.update()` { #query-update }

```python
Query.update(values, synchronize_session='auto', update_args=None)
```

**ধরন:** মেথড

কুয়েরির শর্তে মেলা সব রো **একবারে** হালনাগাদ (বাল্ক UPDATE), বদলানো রোর সংখ্যা দেয়। প্রথম আর্গুমেন্ট `{কলাম: মান}` dict। `synchronize_session` আর `update_args` `delete()`-এর মতো। ২.০: `session.execute(update(User).where(...).values(...))`।

**উদাহরণ:**

```python
n = session.query(User).filter(User.id > 1).update({User.name: User.name + "!"})
print(n, [u.name for u in session.query(User).order_by(User.id)])   # 2 ['রহিম', 'করিম!', 'সুমি!']
```

### `Query.value()` { #query-value }

```python
Query.value(column)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) একটি কলামের প্রথম মান। বদলে `with_entities(col).scalar()`।

**উদাহরণ:**

```python
print(session.query(User).filter(User.id == 2).value(User.name))   # করিম
```

### `Query.values()` { #query-values }

```python
Query.values(*columns)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) নির্দিষ্ট কলামগুলোর ফলের iterator। বদলে `with_entities(...)`।

**উদাহরণ:**

```python
print(list(session.query(User).order_by(User.id).values(User.id))[:2])   # [(1,), (2,)]
```

### `Query.where()` { #query-where }

```python
Query.where(*criterion)
```

**ধরন:** মেথড

`filter()`-এর আরেক নাম (১.৪+), ২.০ ধাঁচের সাথে মিল রাখতে।

**উদাহরণ:**

```python
print(session.query(User).where(User.id == 2).one().name)   # করিম
```

### `Query.whereclause` { #query-whereclause }

**ধরন:** প্রপার্টি

বর্তমান WHERE শর্ত (এক্সপ্রেশন), না থাকলে `None`।

**উদাহরণ:**

```python
print(session.query(User).filter(User.id > 1).whereclause)   # users.id > :id_1
```

### `Query.with_entities()` { #query-with-entities }

```python
Query.with_entities(*entities)
```

**ধরন:** মেথড

SELECT তালিকা পুরো বদলে দেয় (শর্ত, join একই থাকে)। ২.০: `select(...).with_only_columns(...)`।

**উদাহরণ:**

```python
q = session.query(User).filter(User.id < 3)
print(rows(q.with_entities(User.name).order_by(User.id)))   # [('রহিম',), ('করিম',)]
```

### `Query.with_for_update()` { #query-with-for-update }

```python
Query.with_for_update(*, nowait=False, read=False, of=None, skip_locked=False, key_share=False)
```

**ধরন:** মেথড

`SELECT ... FOR UPDATE` (রো লক)। `nowait`, `read` (FOR SHARE), `of`, `skip_locked`, `key_share`। ২.০: `select(...).with_for_update(...)`।

**উদাহরণ:**

```python
print(str(session.query(User.id).with_for_update(skip_locked=True)).splitlines()[-1])   # FROM users FOR UPDATE SKIP LOCKED
```

### `Query.with_hint()` { #query-with-hint }

```python
Query.with_hint(selectable, text, dialect_name='*')
```

**ধরন:** মেথড

নির্দিষ্ট টেবিলের জন্য ডেটাবেস-বিশেষ "hint" (যেমন MySQL `USE INDEX`, Oracle `/*+ ... */`)। PostgreSQL এগুলো উপেক্ষা করে।

**উদাহরণ:**

```python
from sqlalchemy.dialects import mysql
q = session.query(User.id).with_hint(User, "USE INDEX (ix_name)", "mysql")
print(str(q.statement.compile(dialect=mysql.dialect())).splitlines()[-1])   # FROM users USE INDEX (ix_name)
```

### `Query.with_labels()` { #query-with-labels }

```python
Query.with_labels()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) `apply_labels()`-এর মতো। বদলে `set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)`।

**উদাহরণ:**

```python
print(session.query(User.id).with_labels().get_label_style.name)   # LABEL_STYLE_TABLENAME_PLUS_COL
```

### `Query.with_parent()` { #query-with-parent }

```python
Query.with_parent(instance, property=None, from_entity=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) একটি অবজেক্টের সাথে relationship-এ যুক্ত রোগুলো: "রহিমের ঠিকানাগুলো"। বদলে স্বতন্ত্র `with_parent()` ফাংশন: `select(Address).where(with_parent(u, User.addresses))`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(session.query(Address).with_parent(u, User.addresses).count())   # 2
```

### `Query.with_session()` { #query-with-session }

```python
Query.with_session(session)
```

**ধরন:** মেথড

কুয়েরিটি অন্য একটি সেশনে চালানোর জন্য নতুন `Query` দেয়।

**উদাহরণ:**

```python
other = Session(engine)
print(session.query(User).with_session(other).session is other)   # True
```

### `Query.with_statement_hint()` { #query-with-statement-hint }

```python
Query.with_statement_hint(text, dialect_name='*')
```

**ধরন:** মেথড

পুরো স্টেটমেন্টের জন্য hint (যেমন Oracle-এর optimizer hint)।

**উদাহরণ:**

```python
print(str(session.query(User.id).with_statement_hint("/*+ টেস্ট */")).splitlines()[-1])   # FROM users /*+ টেস্ট */
```

### `Query.with_transformation()` { #query-with-transformation }

```python
Query.with_transformation(fn)
```

**ধরন:** মেথড

একটি ফাংশন (`Query → Query`) প্রয়োগ করে: বারবার লাগে এমন শর্ত বা অপশন এক জায়গায় রাখার কৌশল।

**উদাহরণ:**

```python
def active_only(q):
    return q.filter(User.id != 3)
print(session.query(User).with_transformation(active_only).count())   # 2
```

### `Query.yield_per()` { #query-yield-per }

```python
Query.yield_per(count)
```

**ধরন:** মেথড

বড় ফলাফল একবারে মেমোরিতে না এনে `count`-টি করে ব্যাচে আনে। ২.০: `execution_options(yield_per=1000)`।

**উদাহরণ:**

```python
print([u.name for u in session.query(User).order_by(User.id).yield_per(2)])   # ['রহিম', 'করিম', 'সুমি']
```

## সংশ্লিষ্ট ফাংশন ও ক্লাস { #querypropertydescriptor-group }

## `QueryPropertyDescriptor` { #querypropertydescriptor }

```python
from sqlalchemy.orm import QueryPropertyDescriptor
```

(২.০.৫) `scoped_session.query_property()` যে class-level অ্যাট্রিবিউট দেয় তার **টাইপ-হিন্ট** (একটি `typing.Protocol`, তাই `isinstance()` চলে না; শুধু টাইপ-চেকারের জন্য)। পুরোনো ধাঁচ: মডেলে `query = Session.query_property()` রাখলে `User.query.filter(...)` লেখা যায় (Flask-SQLAlchemy-র `Model.query`-এর মতো)। নতুন কোডে এড়িয়ে চলুন।

**উদাহরণ:**

```python
Scoped = scoped_session(sessionmaker(engine))
prop = Scoped.query_property()      # টাইপ-হিন্টে: prop: QueryPropertyDescriptor
User.query = prop
print(User.query.filter_by(id=2).one().name)   # করিম
del User.query; Scoped.remove()
```

## `merge_frozen_result()` { #merge-frozen-result }

```python
from sqlalchemy.orm import merge_frozen_result
```

```python
merge_frozen_result(session, statement, frozen_result, load=True)
```

**ধরন:** ফাংশন

`Result.freeze()` দিয়ে জমিয়ে রাখা (যেমন ক্যাশ থেকে আনা) ফলকে একটি সেশনে মিশিয়ে persistent অবজেক্টসহ নতুন `FrozenResult` দেয়; সেটি ডাকলে (`merged()`) সাধারণ `Result` পাবেন। ক্যাশিং রেসিপির (`do_orm_execute` ইভেন্টে) মূল অংশ।

**উদাহরণ:**

```python
stmt = select(User).where(User.id == 2)
frozen = session.execute(stmt).freeze()          # ক্যাশে রাখার মতো জিনিস
s2 = Session(engine)
merged = merge_frozen_result(s2, stmt, frozen, load=False)
print(type(merged).__name__)   # FrozenResult  (ডকস্ট্রিং "Result" বলে, আসলে আবার FrozenResult)
u = merged().scalars().one()       # ডেকে Result বানান
print(u.name, u in s2)   # করিম True
```

### `merge_frozen_result()`-এর সব প্যারামিটার { #merge-frozen-result-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `session` | যে সেশনে মেশাবে। |
| `statement` | যে স্টেটমেন্ট থেকে ফলটি এসেছিল। |
| `frozen_result` | `FrozenResult` অবজেক্ট। |
| `load` | `True`: সেশনে না থাকা অবজেক্ট ডেটাবেস থেকে মিলিয়ে নেয়; `False`: ডেটাবেসে না গিয়ে সরাসরি বসায় (ক্যাশের জন্য দ্রুত)। |

## `merge_result()` { #merge-result }

```python
from sqlalchemy.orm import merge_result
```

```python
merge_result(query, iterator, load=True)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে legacy) `Query.merge_result()`-এর ফাংশন রূপ। বদলে `merge_frozen_result()`।

**উদাহরণ:**

```python
detached = Session(engine).query(User).filter(User.id == 3).all()
print([u.name for u in merge_result(Session(engine).query(User), detached)])   # ['সুমি']
```

### `merge_result()`-এর সব প্যারামিটার { #merge-result-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `query` | যে `Query`-এর সেশনে মেশাবে। |
| `iterator` | ফলের রো বা `FrozenResult`। |
| `load` | `merge_frozen_result()`-এর মতো। |

## `contains_alias()` { #contains-alias }

```python
from sqlalchemy.orm import contains_alias
```

```python
contains_alias(alias)
```

**ধরন:** ফাংশন

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে, এখন কিছুই করে না) পুরোনো দিনে `from_statement()`-এ মূল টেবিলের alias ব্যবহার করলে ORM-কে জানাতে লাগত। এখন ORM নিজেই কলাম মিলিয়ে নেয়, তাই অপশনটি অর্থহীন।

**উদাহরণ:**

```python
opt = contains_alias(User.__table__.alias("u"))
print(type(opt).__name__)   # AliasOption
```

### `contains_alias()`-এর সব প্যারামিটার { #contains-alias-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `alias` | মূল টেবিলের alias বা subquery। |

## `AliasOption` { #aliasoption }

```python
from sqlalchemy.orm.query import AliasOption
```

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

`contains_alias()` যে অপশন অবজেক্ট দেয়। কম্পাইলের সময় কিছুই বদলায় না; শুধু পুরোনো কোড ভাঙা এড়াতে আছে।

**উদাহরণ:**

```python
q = session.query(User).options(AliasOption(User.__table__.alias("u"))).filter(User.id == 1)
print(q.one().name)   # রহিম  (অপশনটি কিছু বদলায়নি)
```

### কনস্ট্রাক্টরের প্যারামিটার { #aliasoption-params }

```python
AliasOption(alias)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `alias` | টেবিলের alias। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aliasoption-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get_children()`](#aliasoption-get-children) | মেথড (internal) | traversal-এর অংশ। |
| [`inherit_cache`](#aliasoption-inherit-cache) | অ্যাট্রিবিউট (internal) | SQL ক্যাশের জন্য: এই অপশন কুয়েরির ক্যাশ-কী-তে প্রভাব ফেলে না। |
| [`process_compile_state()`](#aliasoption-process-compile-state) | মেথড (internal) | কম্পাইলের সময় ORM অপশন প্রয়োগের hook; এখানে কিছুই করে না। |
| [`process_compile_state_replaced_entities()`](#aliasoption-process-compile-state-replaced-entities) | মেথড (internal) | entity বদলে দেওয়া কুয়েরির (যেমন `with_entities()`) জন্য একই hook। |
| [`propagate_to_loaders`](#aliasoption-propagate-to-loaders) | অ্যাট্রিবিউট (internal) | অপশনটি lazy load-এর কুয়েরিতেও যাবে কি না। |

### `AliasOption.get_children()` { #aliasoption-get-children }

```python
AliasOption.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

traversal-এর অংশ।

**উদাহরণ:**

```python
print(list(AliasOption(User.__table__.alias()).get_children()))   # []
```

### `AliasOption.inherit_cache` { #aliasoption-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQL ক্যাশের জন্য: এই অপশন কুয়েরির ক্যাশ-কী-তে প্রভাব ফেলে না।

**উদাহরণ:**

```python
print(AliasOption.inherit_cache)   # False
```

### `AliasOption.process_compile_state()` { #aliasoption-process-compile-state }

```python
AliasOption.process_compile_state(compile_state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় ORM অপশন প্রয়োগের hook; এখানে কিছুই করে না।

**উদাহরণ:**

```python
print(AliasOption.process_compile_state(AliasOption(User.__table__.alias()), None))   # None
```

### `AliasOption.process_compile_state_replaced_entities()` { #aliasoption-process-compile-state-replaced-entities }

```python
AliasOption.process_compile_state_replaced_entities(compile_state, mapper_entities)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

entity বদলে দেওয়া কুয়েরির (যেমন `with_entities()`) জন্য একই hook।

**উদাহরণ:**

```python
print(callable(AliasOption.process_compile_state_replaced_entities))   # True
```

### `AliasOption.propagate_to_loaders` { #aliasoption-propagate-to-loaders }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অপশনটি lazy load-এর কুয়েরিতেও যাবে কি না।

**উদাহরণ:**

```python
print(AliasOption.propagate_to_loaders)   # False
```

## `create_session()` { #create-session }

```python
from sqlalchemy.orm import create_session
```

```python
create_session(bind=None, **kwargs)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

**autoflush আর expire_on_commit দুটোই বন্ধ** করে একটি `Session` বানায় (`sessionmaker`-এর উল্টো ডিফল্ট)। মূলত পুরোনো পরীক্ষার কোডে। সাধারণ কাজে `Session(engine)` বা `sessionmaker()`।

**উদাহরণ:**

```python
s = create_session(bind=engine)
print(type(s).__name__, s.autoflush, s.expire_on_commit)   # Session False False
s.close()
```

### `create_session()`-এর সব প্যারামিটার { #create-session-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bind` | যে Engine/Connection-এ চলবে। |
| `kwargs` | `Session`-এর বাকি প্যারামিটার। |

## `FromStatement` { #fromstatement }

```python
from sqlalchemy.orm.context import FromStatement
```

`select(User).from_statement(text(...))` (বা `Query.from_statement()`) যে অবজেক্ট বানায়: "এই SQL চালাও, আর রোগুলো থেকে `User` অবজেক্ট বানাও"। `text()`, `Select`, `Insert ... RETURNING` ইত্যাদি থেকে ORM অবজেক্ট লোড করা যায়।

**উদাহরণ:**

```python
stmt = select(User).from_statement(text("SELECT * FROM users WHERE name = :n"))
print(type(stmt).__name__, session.scalars(stmt, {"n": "সুমি"}).one().id)   # FromStatement 3
```

### কনস্ট্রাক্টরের প্যারামিটার { #fromstatement-params }

```python
FromStatement(entities, element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entities` | কোন entity/কলাম লোড হবে। |
| `element` | আসল SQL: `text()`, `Select`, `Insert` ইত্যাদি। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #fromstatement-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FromStatement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`column_descriptions`](select.md#select-column-descriptions) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`exported_columns`](select.md#select-exported-columns) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

## পুরোনো থেকে নতুন: রূপান্তর-টেবিল { #migration }

| ১.x ধাঁচ (`Query`) | ২.০ ধাঁচ (`select()`) |
| :--- | :--- |
| `session.query(User).all()` | `session.scalars(select(User)).all()` |
| `session.query(User).filter(User.id > 1).first()` | `session.scalars(select(User).where(User.id > 1).limit(1)).first()` |
| `session.query(User).filter_by(name="x").one()` | `session.execute(select(User).filter_by(name="x")).scalar_one()` |
| `session.query(User).get(5)` | `session.get(User, 5)` |
| `session.query(User.id, User.name).all()` | `session.execute(select(User.id, User.name)).all()` |
| `session.query(User).count()` | `session.scalar(select(func.count()).select_from(User))` |
| `session.query(User).join(User.addresses)` | `select(User).join(User.addresses)` |
| `q.filter(...).update({...})` | `session.execute(update(User).where(...).values(...))` |
| `q.filter(...).delete()` | `session.execute(delete(User).where(...))` |
| `session.query(q.exists()).scalar()` | `session.scalar(select(exists().where(...)))` |
| `q.with_parent(u, User.addresses)` | `select(Address).where(with_parent(u, User.addresses))` |
| `q.yield_per(1000)` | `session.scalars(stmt.execution_options(yield_per=1000))` |
| `q.statement` | (আগে থেকেই `Select`) |

/// tip | ধাপে ধাপে বদলানোর কৌশল

পুরো প্রজেক্ট একবারে বদলাতে হবে না। প্রথমে পরীক্ষায় সতর্কবার্তা এরর বানান: `warnings.filterwarnings("error", category=sqlalchemy.exc.LegacyAPIWarning)` (দেখুন [এক্সেপশন পেজ](exceptions.md#legacyapiwarning))। তারপর একটি একটি ফাইল বদলান; মাঝের অবস্থায় `session.execute(q.statement)` দিয়ে পুরোনো `Query`-কে নতুন ধাঁচে চালানো যায়।

///
