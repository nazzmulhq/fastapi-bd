# Select API: select(), সাবকুয়েরি, CTE ও UNION { #api-select }

/// note | এই পেজে যা আছে

* `select()` আর `Select`-এর **প্রতিটি** মেথড ও প্রপার্টি (৯৪টি), উদাহরণ ও তৈরি হওয়া SQL-সহ।
* `union()`, `union_all()`, `intersect()`, `except_()` … আর `CompoundSelect`।
* `Subquery`, `CTE` আর `values()` / `Values`।
* ২.১-এর পরিবর্তন: `distinct(কলাম)` বাতিলের পথে, এর বদলে `.ext(distinct_on(...))`; নতুন `ext()`, `into()`।

///

`select()` দিয়ে বানানো স্টেটমেন্ট **অপরিবর্তনীয় (immutable)**: প্রতিটি মেথড (`where`, `order_by` …) একটি **নতুন** স্টেটমেন্ট ফেরত দেয়, আগেরটি বদলায় না। তাই সবসময় `stmt = stmt.where(...)` লিখুন। স্টেটমেন্ট শুধু "চিরকুট"; চালাতে হয় `session.execute()` / `session.scalars()` দিয়ে। ধারণাগুলো ধাপে ধাপে শিখতে দেখুন [কুয়েরি অধ্যায়](../querying.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[Session API পেজের](session.md) মতোই `User` (`id`, `name`, `addresses`) আর `Address` (`id`, `email`, `user_id`) মডেল, আর তিনজন ইউজার: রহিম (দুটি ঠিকানা), করিম, সুমি। `print(stmt)` দিলে SQLAlchemy যে SQL বানায় তা দেখা যায়; কমেন্টে সেটাই দেখানো হয়েছে। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## `select()` { #select }

```python
from sqlalchemy import select
```

```python
select(*entities)
```

**ধরন:** ফাংশন

একটি `SELECT` স্টেটমেন্ট বানায়। আর্গুমেন্টে দিন কী চাই: পুরো মডেল (`User`), কলাম (`User.name`), টেবিল, বা যেকোনো SQL এক্সপ্রেশন (`func.count()`)। একাধিক দিলে প্রতিটি রো-তে সেগুলো পাশাপাশি আসে।

**উদাহরণ:**

```python
stmt = select(User).where(User.name == "রহিম")
print(session.scalars(stmt).one().id)                         # 1
rows = session.execute(select(User.id, func.upper(User.name))).all()
print(len(rows))                                               # 3
```

## `Select` { #select }

```python
from sqlalchemy import Select
```

`select()` থেকে পাওয়া স্টেটমেন্ট অবজেক্ট। নিচের প্রায় সব মেথড "generative": নতুন একটি `Select` ফেরত দেয়, তাই চেইন করে লেখা যায়।

**উদাহরণ:**

```python
stmt = (
    select(User.name, func.count(Address.id).label("n"))
    .join(User.addresses, isouter=True)
    .group_by(User.name)
    .order_by(User.name)
)
print(session.execute(stmt).all())   # [('করিম', 0), ('রহিম', 2), ('সুমি', 0)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #select-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_columns()`](#select-add-columns) | মেথড | বিদ্যমান কলামের তালিকার শেষে আরও কলাম বা এন্টিটি যোগ করে। |
| [`add_cte()`](#select-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`alias()`](#select-alias) | মেথড | `subquery()`-এর আরেক নাম: এই SELECT-কে একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`allows_lambda`](#select-allows-lambda) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`apply_syntax_extension_point()`](#select-apply-syntax-extension-point) | মেথড (internal) | (২.১-এ নতুন) কাস্টম SQL syntax extension বানানোর সময় extension নিজে এটি ডাকে, স্টেটমেন্টের নির্দিষ্ট জায়গায় (যেমন WHERE-এর পরে) নিজেকে বসাতে। |
| [`argument_for()`](#select-argument-for) | ক্লাস মেথড (internal) | এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। |
| [`as_scalar()`](#select-as-scalar) | মেথড ⚠️ deprecated | ১.৪ থেকে বাতিলের পথে। |
| [`column()`](#select-column) | মেথড ⚠️ deprecated | ১.৪ থেকে বাতিলের পথে। |
| [`column_descriptions`](#select-column-descriptions) | প্রপার্টি | SELECT-এ কী কী আছে তার বিবরণ (নাম, টাইপ, এক্সপ্রেশন, কোন মডেলের) dict-এর তালিকা হিসেবে। |
| [`columns_clause_froms`](#select-columns-clause-froms) | প্রপার্টি | শুধু কলামের তালিকা থেকে বোঝা যায় এমন FROM-গুলো (টেবিল) দেয়। |
| [`compare()`](#select-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#select-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`correlate()`](#select-correlate) | মেথড | সাবকুয়েরি হিসেবে ব্যবহারের সময় কোন বাইরের টেবিলের সাথে "correlate" (বাইরের রো-র সাথে যুক্ত) হবে তা স্পষ্ট করে। |
| [`correlate_except()`](#select-correlate-except) | মেথড | উল্টোটা: দেওয়া টেবিলগুলো ছাড়া বাকি সব বাইরের টেবিলের সাথে correlate করে; দেওয়া টেবিল সবসময় সাবকুয়েরির নিজের FROM-এ থাকে। |
| [`corresponding_column()`](#select-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#select-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#select-description) | প্রপার্টি (internal) | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`dialect_kwargs`](#select-dialect-kwargs) | প্রপার্টি (internal) | এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। |
| [`dialect_options`](#select-dialect-options) | প্রপার্টি (internal) | `dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ। |
| [`distinct()`](#select-distinct) | মেথড | `SELECT DISTINCT` বানায়: একই রো একবারই আসে। |
| [`entity_namespace`](#select-entity-namespace) | প্রপার্টি (internal) | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`except_()`](#select-except-) | মেথড | এই SELECT থেকে অন্য SELECT-এর রো বাদ দিয়ে বাকিটা দেয় (`EXCEPT`)। |
| [`except_all()`](#select-except-all) | মেথড | `EXCEPT ALL`: ডুপ্লিকেট রো গুনে বাদ দেয়। |
| [`execution_options()`](#select-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exists()`](#select-exists) | মেথড | এই SELECT-কে `EXISTS (...)` এক্সপ্রেশন বানায়, যা `where()`-এ শর্ত হিসেবে বা কলাম হিসেবে ব্যবহার করা যায়। |
| [`exported_columns`](#select-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`ext()`](#select-ext) | মেথড | (২.১-এ নতুন) ডেটাবেস-নির্দিষ্ট একটি SQL syntax extension যুক্ত করে, যেমন PostgreSQL-এর `DISTINCT ON`। |
| [`fetch()`](#select-fetch) | মেথড | SQL স্ট্যান্ডার্ড `FETCH FIRST n ROWS ONLY` দেয় (`limit()`-এর বিকল্প)। |
| [`filter()`](#select-filter) | মেথড | `where()`-এর আরেক নাম। |
| [`filter_by()`](#select-filter-by) | মেথড | `কলাম=মান` keyword দিয়ে সহজ সমান-শর্ত যোগ করে। |
| [`from_statement()`](#select-from-statement) | মেথড | ORM-এ: এই `select(User)`-এর এন্টিটিগুলো অন্য একটি স্টেটমেন্টের (সাধারণত `text()` দিয়ে লেখা raw SQL) রো থেকে বানায়। |
| [`froms`](#select-froms) | প্রপার্টি ⚠️ deprecated | ১.৪.২৩ থেকে বাতিলের পথে। |
| [`get_children()`](#select-get-children) | মেথড (internal) | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_dialect_option()`](#select-get-dialect-option) | মেথড (internal) | একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। |
| [`get_execution_options()`](#select-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`get_final_froms()`](#select-get-final-froms) | মেথড | SELECT শেষ পর্যন্ত কোন FROM-গুলো দেখাবে তা পুরো হিসাব করে দেয় (join সহ)। |
| [`get_label_style()`](#select-get-label-style) | মেথড | বর্তমান label style (কলামের নামকরণের নিয়ম) দেয়। |
| [`group_by()`](#select-group-by) | মেথড | `GROUP BY` যোগ করে। |
| [`having()`](#select-having) | মেথড | `HAVING` যোগ করে: গ্রুপ হওয়ার **পরের** শর্ত (যেমন "যাদের ঠিকানা ১টির বেশি")। |
| [`inherit_cache`](#select-inherit-cache) | অ্যাট্রিবিউট (internal) | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`inner_columns`](#select-inner-columns) | প্রপার্টি (legacy) | SELECT-এর কলাম-এক্সপ্রেশনগুলোর iterator। |
| [`intersect()`](#select-intersect) | মেথড | দুটি SELECT-এ **দুটোতেই** আছে এমন রো দেয় (`INTERSECT`)। |
| [`intersect_all()`](#select-intersect-all) | মেথড | `INTERSECT ALL`: ডুপ্লিকেট গুনে মিল খোঁজে। |
| [`into()`](#select-into) | মেথড | (২.১-এ নতুন) এই SELECT-এর ফল দিয়ে নতুন একটি টেবিল বানানোর `CREATE TABLE ... AS SELECT ...` স্টেটমেন্ট দেয়। |
| [`is_clause_element`](#select-is-clause-element) | অ্যাট্রিবিউট (internal) | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#select-is-delete) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#select-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#select-is-dml) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#select-is-from-statement) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#select-is-insert) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#select-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#select-is-selectable) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#select-is-text) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#select-is-update) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`join()`](#select-join) | মেথড | SELECT-এর FROM-এ একটি JOIN যোগ করে। |
| [`join_from()`](#select-join-from) | মেথড | `join()`-এর মতো, কিন্তু বাম দিকের টেবিলও স্পষ্ট করে দেন। |
| [`kwargs`](#select-kwargs) | প্রপার্টি (internal) | `dialect_kwargs`-এর আরেক নাম। |
| [`label()`](#select-label) | মেথড | এই SELECT-কে একটি নাম দেওয়া scalar সাবকুয়েরি বানায়, যাতে বাইরের SELECT-এ কলাম হিসেবে বসানো যায়। |
| [`lateral()`](#select-lateral) | মেথড | `LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`limit()`](#select-limit) | মেথড | `LIMIT`: সর্বোচ্চ কয়টি রো আসবে। |
| [`memoized_attribute`](#select-memoized-attribute) | অ্যাট্রিবিউট (internal) | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#select-memoized-instancemethod) | ক্লাস মেথড (internal) | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#select-name-cte-columns) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`offset()`](#select-offset) | মেথড | `OFFSET`: শুরু থেকে কয়টি রো বাদ যাবে (pagination-এ `limit()`-এর সাথে)। |
| [`options()`](#select-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`order_by()`](#select-order-by) | মেথড | `ORDER BY` যোগ করে। |
| [`outerjoin()`](#select-outerjoin) | মেথড | LEFT OUTER JOIN যোগ করে (`join(..., isouter=True)`-এর সমান)। |
| [`outerjoin_from()`](#select-outerjoin-from) | মেথড | `outerjoin()`-এর মতো, বাম দিকের টেবিল স্পষ্ট করে। |
| [`params()`](#select-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`prefix_with()`](#select-prefix-with) | মেথড | `SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। |
| [`reduce_columns()`](#select-reduce-columns) | মেথড | একই মান বহনকারী (যেমন FK আর তার লক্ষ্য কলাম) একাধিক কলাম থাকলে একটি রেখে বাকিগুলো বাদ দেয়। |
| [`reflect_only_elements`](#select-reflect-only-elements) | প্রপার্টি (internal) | (২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। |
| [`replace_selectable()`](#select-replace-selectable) | মেথড ⚠️ deprecated | ১.৪ থেকে বাতিলের পথে। |
| [`scalar_subquery()`](#select-scalar-subquery) | মেথড | এক রো, এক কলাম দেয় এমন SELECT-কে একটি মান হিসেবে (scalar) ব্যবহারযোগ্য করে, যাতে অন্য SELECT-এর কলামে বা WHERE-এ বসানো যায়। |
| [`select_from()`](#select-select-from) | মেথড | FROM-এ কোন টেবিল থাকবে তা স্পষ্ট করে। |
| [`selectable`](#select-selectable) | প্রপার্টি (internal) | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`selected_columns`](#select-selected-columns) | প্রপার্টি | এই SELECT যে কলামগুলো ফেরত দেবে তার সংগ্রহ। |
| [`self_group()`](#select-self-group) | মেথড (internal) | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`set_label_style()`](#select-set-label-style) | মেথড | ফলাফলের কলামগুলোর নাম কীভাবে হবে তা ঠিক করে। |
| [`slice()`](#select-slice) | মেথড | Python-এর slice-এর মতো `[start:stop]` দিয়ে LIMIT/OFFSET বসায়। |
| [`stringify_dialect`](#select-stringify-dialect) | অ্যাট্রিবিউট (internal) | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`subquery()`](#select-subquery) | মেথড | এই SELECT-কে FROM-এ বসানোর মতো একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`suffix_with()`](#select-suffix-with) | মেথড | পুরো স্টেটমেন্টের শেষে কিছু যোগ করে (ডেটাবেস-নির্দিষ্ট অপশনের জন্য)। |
| [`supports_execution`](#select-supports-execution) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`union()`](#select-union) | মেথড | দুটি SELECT-এর রো একসাথে দেয়, ডুপ্লিকেট বাদ দিয়ে (`UNION`)। |
| [`union_all()`](#select-union-all) | মেথড | `UNION ALL`: ডুপ্লিকেটসহ সব রো; `union()`-এর চেয়ে দ্রুত। |
| [`unique_params()`](#select-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#select-uses-inspection) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`where()`](#select-where) | মেথড | `WHERE` শর্ত যোগ করে। |
| [`whereclause`](#select-whereclause) | প্রপার্টি | এ পর্যন্ত যোগ করা সব WHERE শর্ত একসাথে (একটি এক্সপ্রেশন) দেয়; না থাকলে `None`। |
| [`with_for_update()`](#select-with-for-update) | মেথড | `SELECT ... FOR UPDATE` বানায়: পড়া রো-গুলো ট্রানজ্যাকশন শেষ না হওয়া পর্যন্ত লক থাকে। |
| [`with_hint()`](#select-with-hint) | মেথড | নির্দিষ্ট একটি টেবিলের জন্য ডেটাবেস-নির্দিষ্ট hint (যেমন Oracle/MySQL-এর index hint) যোগ করে। |
| [`with_only_columns()`](#select-with-only-columns) | মেথড | বিদ্যমান স্টেটমেন্টের কলামের তালিকা পুরো বদলে দেয় (WHERE, JOIN ইত্যাদি থাকে)। |
| [`with_statement_hint()`](#select-with-statement-hint) | মেথড | পুরো স্টেটমেন্টের জন্য hint যোগ করে, সাধারণত শেষে। |

### `Select.add_columns()` { #select-add-columns }

```python
Select.add_columns(*entities)
```

**ধরন:** মেথড

বিদ্যমান কলামের তালিকার শেষে আরও কলাম বা এন্টিটি যোগ করে।

**উদাহরণ:**

```python
stmt = select(User.id).add_columns(User.name)
print(stmt)   # SELECT users.id, users.name FROM users
```

### `Select.add_cte()` { #select-add-cte }

```python
Select.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। সাধারণত DML CTE (যেমন `INSERT ... RETURNING`) চালাতে কাজে লাগে।

**উদাহরণ:**

```python
ins = User.__table__.insert().values(name="CTE থেকে").returning(User.id).cte("new_user")
stmt = select(User.name).where(User.id == 1).add_cte(ins)
print(session.execute(stmt).scalar())   # রহিম (আর নতুন ইউজারও ঢুকে গেছে)
session.commit()
```

### `Select.alias()` { #select-alias }

```python
Select.alias(name=None, flat=False)
```

**ধরন:** মেথড

`subquery()`-এর আরেক নাম: এই SELECT-কে একটি নামযুক্ত সাবকুয়েরি বানায়।

**উদাহরণ:**

```python
sub = select(User.id).where(User.id > 1).alias("big_ids")
print(select(sub.c.id))   # SELECT big_ids.id FROM (SELECT users.id ... ) AS big_ids
```

### `Select.allows_lambda` { #select-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না।

### `Select.apply_syntax_extension_point()` { #select-apply-syntax-extension-point }

```python
Select.apply_syntax_extension_point(apply_fn, position)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(২.১-এ নতুন) কাস্টম SQL syntax extension বানানোর সময় extension নিজে এটি ডাকে, স্টেটমেন্টের নির্দিষ্ট জায়গায় (যেমন WHERE-এর পরে) নিজেকে বসাতে। অ্যাপ কোডে `ext()` ব্যবহার করুন।

### `Select.argument_for()` { #select-argument-for }

```python
Select.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। থার্ড-পার্টি ডায়ালেক্ট বানালে কাজে লাগে।

### `Select.as_scalar()` { #select-as-scalar }

```python
Select.as_scalar()
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪ থেকে বাতিলের পথে। এর বদলে `scalar_subquery()` লিখুন।

**উদাহরণ:**

```python
count_sub = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
print(session.execute(select(User.name, count_sub).order_by(User.id)).first())   # ('রহিম', 2)
```

### `Select.column()` { #select-column }

```python
Select.column(column)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪ থেকে বাতিলের পথে। বিকল্প: `add_columns()`।

**উদাহরণ:**

```python
stmt = select(User.id).add_columns(User.name)
```

### `Select.column_descriptions` { #select-column-descriptions }

**ধরন:** প্রপার্টি

SELECT-এ কী কী আছে তার বিবরণ (নাম, টাইপ, এক্সপ্রেশন, কোন মডেলের) dict-এর তালিকা হিসেবে। API-তে ডায়নামিক কলাম দেখাতে বা ডিবাগিংয়ে কাজে লাগে।

**উদাহরণ:**

```python
for d in select(User.id, User.name).column_descriptions:
    print(d["name"], d["entity"].__name__)   # id User / name User
```

### `Select.columns_clause_froms` { #select-columns-clause-froms }

**ধরন:** প্রপার্টি

শুধু কলামের তালিকা থেকে বোঝা যায় এমন FROM-গুলো (টেবিল) দেয়।

**উদাহরণ:**

```python
print([t.name for t in select(User.name, Address.email).columns_clause_froms])   # ['users', 'addresses']
```

### `Select.compare()` { #select-compare }

```python
Select.compare(other, **kw)
```

**ধরন:** মেথড

দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। ক্যাশিং বা টেস্টে কাজে লাগে।

**উদাহরণ:**

```python
a = select(User).where(User.id == 5)
b = select(User).where(User.id == 5)
print(a.compare(b))   # True
```

### `Select.compile()` { #select-compile }

```python
Select.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। `dialect=` দিয়ে নির্দিষ্ট ডেটাবেসের SQL দেখা যায়; `compile_kwargs={"literal_binds": True}` দিলে প্যারামিটারের মান SQL-এর ভেতরে বসে (শুধু ডিবাগিংয়ের জন্য)।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id == 2)
print(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
# SELECT users.name FROM users WHERE users.id = 2
```

### `Select.correlate()` { #select-correlate }

```python
Select.correlate(*fromclauses)
```

**ধরন:** মেথড

সাবকুয়েরি হিসেবে ব্যবহারের সময় কোন বাইরের টেবিলের সাথে "correlate" (বাইরের রো-র সাথে যুক্ত) হবে তা স্পষ্ট করে। সাধারণত SQLAlchemy নিজেই বোঝে (auto-correlation); স্পষ্ট করতে হলে এটি।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).correlate(User).scalar_subquery()
print(session.execute(select(User.name, n).order_by(User.id)).all())
# [('রহিম', 2), ('করিম', 0), ('সুমি', 0)]
```

### `Select.correlate_except()` { #select-correlate-except }

```python
Select.correlate_except(*fromclauses)
```

**ধরন:** মেথড

উল্টোটা: দেওয়া টেবিলগুলো ছাড়া বাকি সব বাইরের টেবিলের সাথে correlate করে; দেওয়া টেবিল সবসময় সাবকুয়েরির নিজের FROM-এ থাকে।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).correlate_except(Address).scalar_subquery()
print(session.execute(select(User.name, n).where(User.id == 1)).one())   # ('রহিম', 2)
```

### `Select.corresponding_column()` { #select-corresponding-column }

```python
Select.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়।

**উদাহরণ:**

```python
stmt = select(User.id, User.name)
print(stmt.corresponding_column(User.__table__.c.name) is not None)   # True
```

### `Select.cte()` { #select-cte }

```python
Select.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। `recursive=True` দিলে recursive CTE। ফলাফল একটি `CTE` অবজেক্ট, যার কলাম `.c` দিয়ে পাওয়া যায়।

**উদাহরণ:**

```python
rich = select(User.id, User.name).where(User.id < 3).cte("small_ids")
print(session.execute(select(rich.c.name).order_by(rich.c.id)).scalars().all())   # ['রহিম', 'করিম']
```

### `Select.description` { #select-description }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। SELECT-এর ক্ষেত্রে সাধারণত `None`।

### `Select.dialect_kwargs` { #select-dialect-kwargs }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। `Select`-এ সাধারণত খালি; `Table`, `Index`-এ বেশি কাজে লাগে।

**উদাহরণ:**

```python
print(dict(select(User).dialect_kwargs))   # {}
```

### `Select.dialect_options` { #select-dialect-options }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ।

### `Select.distinct()` { #select-distinct }

```python
Select.distinct(*expr)
```

**ধরন:** মেথড

`SELECT DISTINCT` বানায়: একই রো একবারই আসে। ২.১ থেকে এতে কলাম দেওয়া (PostgreSQL-এর `DISTINCT ON`) বাতিলের পথে; তার বদলে `.ext(distinct_on(কলাম))` লিখুন।

**উদাহরণ:**

```python
print(session.scalars(select(Address.user_id).distinct()).all())   # [1]
stmt = select(Address).ext(distinct_on(Address.user_id)).order_by(Address.user_id, Address.id)
print(stmt.compile(dialect=postgresql.dialect()))
# SELECT DISTINCT ON (addresses.user_id) addresses.id, ... ORDER BY addresses.user_id, addresses.id
```

### `Select.entity_namespace` { #select-entity-namespace }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক।

### `Select.except_()` { #select-except- }

```python
Select.except_(*other)
```

**ধরন:** মেথড

এই SELECT থেকে অন্য SELECT-এর রো বাদ দিয়ে বাকিটা দেয় (`EXCEPT`)। ফল একটি `CompoundSelect`।

**উদাহরণ:**

```python
stmt = select(User.id).except_(select(Address.user_id))
print(sorted(session.scalars(stmt).all()))   # [2, 3] — যাদের কোনো ঠিকানা নেই
```

### `Select.except_all()` { #select-except-all }

```python
Select.except_all(*other)
```

**ধরন:** মেথড

`EXCEPT ALL`: ডুপ্লিকেট রো গুনে বাদ দেয়।

**উদাহরণ:**

```python
stmt = select(User.id).except_all(select(Address.user_id))
print(sorted(session.scalars(stmt).all()))   # [2, 3]
```

### `Select.execution_options()` { #select-execution-options }

```python
Select.execution_options(**kw)
```

**ধরন:** মেথড

স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। SQL বদলায় না।

**উদাহরণ:**

```python
stmt = select(User).execution_options(populate_existing=True)
print(stmt.get_execution_options())   # immutabledict({'populate_existing': True})
```

### `Select.exists()` { #select-exists }

```python
Select.exists()
```

**ধরন:** মেথড

এই SELECT-কে `EXISTS (...)` এক্সপ্রেশন বানায়, যা `where()`-এ শর্ত হিসেবে বা কলাম হিসেবে ব্যবহার করা যায়।

**উদাহরণ:**

```python
has_addr = select(Address.id).where(Address.user_id == User.id).exists()
print(session.scalars(select(User.name).where(has_addr)).all())   # ['রহিম']
```

### `Select.exported_columns` { #select-exported-columns }

**ধরন:** প্রপার্টি

এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। `Select`-এ এটি `selected_columns`-এর সমান।

**উদাহরণ:**

```python
print(list(select(User.id, User.name).exported_columns.keys()))   # ['id', 'name']
```

### `Select.ext()` { #select-ext }

```python
Select.ext(extension)
```

**ধরন:** মেথড

(২.১-এ নতুন) ডেটাবেস-নির্দিষ্ট একটি SQL syntax extension যুক্ত করে, যেমন PostgreSQL-এর `DISTINCT ON`।

**উদাহরণ:**

```python
stmt = select(User.name).ext(distinct_on(User.name))
print(stmt.compile(dialect=postgresql.dialect()))   # SELECT DISTINCT ON (users.name) users.name FROM users
```

### `Select.fetch()` { #select-fetch }

```python
Select.fetch(count, with_ties=False, percent=False, **dialect_kw)
```

**ধরন:** মেথড

SQL স্ট্যান্ডার্ড `FETCH FIRST n ROWS ONLY` দেয় (`limit()`-এর বিকল্প)। `with_ties=True` দিলে শেষ মানের সমান সব রো আসে। PostgreSQL, Oracle, SQL Server-এ চলে।

**উদাহরণ:**

```python
stmt = select(User.name).order_by(User.id).fetch(2)
print(session.scalars(stmt).all())   # ['রহিম', 'করিম']
```

### `Select.filter()` { #select-filter }

```python
Select.filter(*criteria)
```

**ধরন:** মেথড

`where()`-এর আরেক নাম। কাজ হুবহু এক।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).filter(User.id == 3)).one())   # সুমি
```

### `Select.filter_by()` { #select-filter-by }

```python
Select.filter_by(**kwargs)
```

**ধরন:** মেথড

`কলাম=মান` keyword দিয়ে সহজ সমান-শর্ত যোগ করে। শেষ যোগ করা এন্টিটির (সাধারণত join-এর পরেরটি) কলামের নাম ধরে খোঁজে।

**উদাহরণ:**

```python
print(session.scalars(select(User).filter_by(name="করিম")).one().id)   # 2
```

### `Select.from_statement()` { #select-from-statement }

```python
Select.from_statement(statement)
```

**ধরন:** মেথড

ORM-এ: এই `select(User)`-এর এন্টিটিগুলো অন্য একটি স্টেটমেন্টের (সাধারণত `text()` দিয়ে লেখা raw SQL) রো থেকে বানায়। raw SQL চালিয়েও ORM অবজেক্ট পেতে কাজে লাগে।

**উদাহরণ:**

```python
raw = text("SELECT id, name FROM users WHERE name = :n")
user = session.scalars(select(User).from_statement(raw), {"n": "সুমি"}).one()
print(user.id, type(user).__name__)   # 3 User
```

### `Select.froms` { #select-froms }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪.২৩ থেকে বাতিলের পথে। বিকল্প: `get_final_froms()`।

**উদাহরণ:**

```python
print([t.name for t in select(User.name).get_final_froms()])   # ['users']
```

### `Select.get_children()` { #select-get-children }

```python
Select.get_children(**kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। SQL ট্রি ঘুরে দেখার (visitor) টুলে ব্যবহৃত।

### `Select.get_dialect_option()` { #select-get-dialect-option }

```python
Select.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। ডায়ালেক্টের কম্পাইলার বানাতে কাজে লাগে।

### `Select.get_execution_options()` { #select-get-execution-options }

```python
Select.get_execution_options()
```

**ধরন:** মেথড

`execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়।

**উদাহরণ:**

```python
print(select(User).execution_options(yield_per=10).get_execution_options())   # immutabledict({'yield_per': 10})
```

### `Select.get_final_froms()` { #select-get-final-froms }

```python
Select.get_final_froms()
```

**ধরন:** মেথড

SELECT শেষ পর্যন্ত কোন FROM-গুলো দেখাবে তা পুরো হিসাব করে দেয় (join সহ)।

**উদাহরণ:**

```python
stmt = select(User.name).join(User.addresses)
print(len(stmt.get_final_froms()))   # 1 — users JOIN addresses একটি FROM
```

### `Select.get_label_style()` { #select-get-label-style }

```python
Select.get_label_style()
```

**ধরন:** মেথড

বর্তমান label style (কলামের নামকরণের নিয়ম) দেয়।

**উদাহরণ:**

```python
print(select(User).get_label_style())   # SelectLabelStyle.LABEL_STYLE_DISAMBIGUATE_ONLY
```

### `Select.group_by()` { #select-group-by }

```python
Select.group_by(*clauses)
```

**ধরন:** মেথড

`GROUP BY` যোগ করে। aggregate (`count`, `sum`) প্রতি দলে হিসাব করতে।

**উদাহরণ:**

```python
stmt = select(Address.user_id, func.count()).group_by(Address.user_id)
print(session.execute(stmt).all())   # [(1, 2)]
```

### `Select.having()` { #select-having }

```python
Select.having(*having)
```

**ধরন:** মেথড

`HAVING` যোগ করে: গ্রুপ হওয়ার **পরের** শর্ত (যেমন "যাদের ঠিকানা ১টির বেশি")।

**উদাহরণ:**

```python
stmt = select(Address.user_id).group_by(Address.user_id).having(func.count() > 1)
print(session.scalars(stmt).all())   # [1]
```

### `Select.inherit_cache` { #select-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ।

### `Select.inner_columns` { #select-inner-columns }

**ধরন:** প্রপার্টি

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

SELECT-এর কলাম-এক্সপ্রেশনগুলোর iterator। ১.৪ থেকে legacy; বিকল্প `exported_columns` / `selected_columns`।

**উদাহরণ:**

```python
print(len(list(select(User.id, User.name).inner_columns)))   # 2
```

### `Select.intersect()` { #select-intersect }

```python
Select.intersect(*other)
```

**ধরন:** মেথড

দুটি SELECT-এ **দুটোতেই** আছে এমন রো দেয় (`INTERSECT`)।

**উদাহরণ:**

```python
stmt = select(User.id).intersect(select(Address.user_id))
print(session.scalars(stmt).all())   # [1]
```

### `Select.intersect_all()` { #select-intersect-all }

```python
Select.intersect_all(*other)
```

**ধরন:** মেথড

`INTERSECT ALL`: ডুপ্লিকেট গুনে মিল খোঁজে।

**উদাহরণ:**

```python
stmt = select(Address.user_id).intersect_all(select(User.id))
print(session.scalars(stmt).all())   # [1]
```

### `Select.into()` { #select-into }

```python
Select.into(target, *, metadata=None, schema=None, temporary=False, if_not_exists=False)
```

**ধরন:** মেথড

(২.১-এ নতুন) এই SELECT-এর ফল দিয়ে নতুন একটি টেবিল বানানোর `CREATE TABLE ... AS SELECT ...` স্টেটমেন্ট দেয়। রিপোর্ট বা ব্যাকআপ টেবিল বানাতে কাজে লাগে।

**উদাহরণ:**

```python
with engine.begin() as conn:
    conn.execute(select(User.id, User.name).where(User.id < 3).into("users_copy"))
    print(conn.exec_driver_sql("SELECT count(*) FROM users_copy").scalar())   # 2
```

### `Select.is_clause_element` { #select-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)।

### `Select.is_delete` { #select-is-delete }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)।

### `Select.is_derived_from()` { #select-is-derived-from }

```python
Select.is_derived_from(fromclause)
```

**ধরন:** মেথড

এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে।

**উদাহরণ:**

```python
print(select(User.name).subquery().is_derived_from(User.__table__))   # True
```

### `Select.is_dml` { #select-is-dml }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)।

### `Select.is_from_statement` { #select-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না।

### `Select.is_insert` { #select-is-insert }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: INSERT কি না।

### `Select.is_select` { #select-is-select }

**ধরন:** অ্যাট্রিবিউট

এটি SELECT স্টেটমেন্ট হলে `True`। event hook-এ (যেমন `do_orm_execute`) স্টেটমেন্টের ধরন বুঝতে কাজে লাগে।

**উদাহরণ:**

```python
print(select(User).is_select)   # True
```

### `Select.is_selectable` { #select-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট।

### `Select.is_text` { #select-is-text }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না।

### `Select.is_update` { #select-is-update }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: UPDATE কি না।

### `Select.join()` { #select-join }

```python
Select.join(target, onclause=None, *, isouter=False, full=False)
```

**ধরন:** মেথড

SELECT-এর FROM-এ একটি JOIN যোগ করে। রিলেশনশিপ দিলে (`User.addresses`) ON নিজে বের হয়; নইলে দ্বিতীয় আর্গুমেন্টে ON দিন। `isouter=True` = LEFT OUTER JOIN, `full=True` = FULL OUTER JOIN।

**উদাহরণ:**

```python
stmt = select(User.name, Address.email).join(User.addresses).order_by(Address.id)
print(session.execute(stmt).all())   # [('রহিম', 'rahim@example.com'), ('রহিম', 'rahim@work.com')]
```

### `Select.join_from()` { #select-join-from }

```python
Select.join_from(from_, target, onclause=None, *, isouter=False, full=False)
```

**ধরন:** মেথড

`join()`-এর মতো, কিন্তু বাম দিকের টেবিলও স্পষ্ট করে দেন। কোন দিক থেকে join হবে তা নিয়ে দ্বিধা থাকলে কাজে লাগে।

**উদাহরণ:**

```python
stmt = select(Address.email).join_from(User, Address, User.id == Address.user_id).where(User.id == 1)
print(len(session.scalars(stmt).all()))   # 2
```

### `Select.kwargs` { #select-kwargs }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`dialect_kwargs`-এর আরেক নাম।

### `Select.label()` { #select-label }

```python
Select.label(name)
```

**ধরন:** মেথড

এই SELECT-কে একটি নাম দেওয়া scalar সাবকুয়েরি বানায়, যাতে বাইরের SELECT-এ কলাম হিসেবে বসানো যায়। এক রো, এক কলাম ফেরত দেয় এমন কুয়েরিতে ব্যবহার করুন।

**উদাহরণ:**

```python
total = select(func.count(User.id)).label("total_users")
print(session.execute(select(total)).one().total_users)   # 3
```

### `Select.lateral()` { #select-lateral }

```python
Select.lateral(name=None)
```

**ধরন:** মেথড

`LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। "প্রতি দলের শীর্ষ N" ধরনের কুয়েরিতে কাজে লাগে।

**উদাহরণ:**

```python
latest = (select(Address.email).where(Address.user_id == User.id)
          .order_by(Address.id.desc()).limit(1).lateral("latest"))
stmt = select(User.name, latest.c.email).join(latest, literal(True)).order_by(User.id)
print(session.execute(stmt).all())   # [('রহিম', 'rahim@work.com')]
```

### `Select.limit()` { #select-limit }

```python
Select.limit(limit)
```

**ধরন:** মেথড

`LIMIT`: সর্বোচ্চ কয়টি রো আসবে।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.id).limit(2)).all())   # ['রহিম', 'করিম']
```

### `Select.memoized_attribute` { #select-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)।

### `Select.memoized_instancemethod()` { #select-memoized-instancemethod }

```python
Select.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)।

### `Select.name_cte_columns` { #select-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)।

### `Select.offset()` { #select-offset }

```python
Select.offset(offset)
```

**ধরন:** মেথড

`OFFSET`: শুরু থেকে কয়টি রো বাদ যাবে (pagination-এ `limit()`-এর সাথে)।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.id).offset(1).limit(1)).all())   # ['করিম']
```

### `Select.options()` { #select-options }

```python
Select.options(*options)
```

**ধরন:** মেথড

ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)।

**উদাহরণ:**

```python
users = session.scalars(select(User).options(selectinload(User.addresses)).order_by(User.id)).all()
print(len(users[0].addresses))   # 2
```

### `Select.order_by()` { #select-order-by }

```python
Select.order_by(*clauses)
```

**ধরন:** মেথড

`ORDER BY` যোগ করে। কলামের `.desc()`, `.asc()`, `.nulls_last()` দিয়ে দিক ঠিক করুন। `order_by(None)` দিলে আগের সব ORDER BY মুছে যায়।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.id.desc())).all())   # ['সুমি', 'করিম', 'রহিম']
```

### `Select.outerjoin()` { #select-outerjoin }

```python
Select.outerjoin(target, onclause=None, *, full=False)
```

**ধরন:** মেথড

LEFT OUTER JOIN যোগ করে (`join(..., isouter=True)`-এর সমান)। বাম দিকের সব রো থাকে, মিল না থাকলে ডান দিক `None`।

**উদাহরণ:**

```python
stmt = select(User.name, Address.email).outerjoin(User.addresses).where(User.id == 2)
print(session.execute(stmt).all())   # [('করিম', None)]
```

### `Select.outerjoin_from()` { #select-outerjoin-from }

```python
Select.outerjoin_from(from_, target, onclause=None, *, full=False)
```

**ধরন:** মেথড

`outerjoin()`-এর মতো, বাম দিকের টেবিল স্পষ্ট করে।

**উদাহরণ:**

```python
stmt = select(User.name).outerjoin_from(User, Address).where(Address.id.is_(None)).order_by(User.id)
print(session.scalars(stmt).all())   # ['করিম', 'সুমি']
```

### `Select.params()` { #select-params }

```python
Select.params(**kwargs)
```

**ধরন:** মেথড

`bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id == bindparam("uid"))
print(session.scalars(stmt.params(uid=2)).one())   # করিম
```

### `Select.prefix_with()` { #select-prefix-with }

```python
Select.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

`SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। `dialect=` দিলে শুধু সেই ডেটাবেসে বসে।

**উদাহরণ:**

```python
print(select(User.id).prefix_with("/*+ fast */"))   # SELECT /*+ fast */ users.id FROM users
```

### `Select.reduce_columns()` { #select-reduce-columns }

```python
Select.reduce_columns(only_synonyms=True)
```

**ধরন:** মেথড

একই মান বহনকারী (যেমন FK আর তার লক্ষ্য কলাম) একাধিক কলাম থাকলে একটি রেখে বাকিগুলো বাদ দেয়। ডিফল্টে (`only_synonyms=True`) শুধু **একই নামের** কলাম বাদ যায়; নাম আলাদা হলেও বাদ দিতে `only_synonyms=False` দিন।

**উদাহরণ:**

```python
stmt = select(User.__table__.c.id, Address.__table__.c.user_id).where(User.id == Address.user_id)
print(len(stmt.reduce_columns().selected_columns))                       # 2 — নাম আলাদা (id, user_id)
print(len(stmt.reduce_columns(only_synonyms=False).selected_columns))    # 1
```

### `Select.reflect_only_elements` { #select-reflect-only-elements }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। মূলত `Table` ও `Index`-এর জন্য; `Select`-এ খালি থাকে।

### `Select.replace_selectable()` { #select-replace-selectable }

```python
Select.replace_selectable(old, alias)
```

**ধরন:** মেথড

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪ থেকে বাতিলের পথে। একটি টেবিলকে alias দিয়ে বদলানো একটি কপি দিত; এখন `sqlalchemy.sql.visitors` ব্যবহার করুন।

### `Select.scalar_subquery()` { #select-scalar-subquery }

```python
Select.scalar_subquery()
```

**ধরন:** মেথড

এক রো, এক কলাম দেয় এমন SELECT-কে একটি মান হিসেবে (scalar) ব্যবহারযোগ্য করে, যাতে অন্য SELECT-এর কলামে বা WHERE-এ বসানো যায়।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
print(session.execute(select(User.name, n.label("n")).order_by(User.id)).first())   # ('রহিম', 2)
```

### `Select.select_from()` { #select-select-from }

```python
Select.select_from(*froms)
```

**ধরন:** মেথড

FROM-এ কোন টেবিল থাকবে তা স্পষ্ট করে। কলাম থেকে টেবিল বোঝা না গেলে (যেমন `func.count()`) বা join-এর বাম দিক ঠিক করতে কাজে লাগে।

**উদাহরণ:**

```python
print(session.scalar(select(func.count()).select_from(User)))   # 3
```

### `Select.selectable` { #select-selectable }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়।

### `Select.selected_columns` { #select-selected-columns }

**ধরন:** প্রপার্টি

এই SELECT যে কলামগুলো ফেরত দেবে তার সংগ্রহ। নাম দিয়ে পাওয়া যায়: `stmt.selected_columns.name`। বিদ্যমান স্টেটমেন্ট থেকে ফিল্টার বানাতে কাজে লাগে।

**উদাহরণ:**

```python
stmt = select(User.id, User.name)
stmt = stmt.where(stmt.selected_columns.name == "সুমি")
print(session.execute(stmt).one())   # (3, 'সুমি')
```

### `Select.self_group()` { #select-self-group }

```python
Select.self_group(against=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। SQLAlchemy নিজেই ডাকে।

### `Select.set_label_style()` { #select-set-label-style }

```python
Select.set_label_style(style)
```

**ধরন:** মেথড

ফলাফলের কলামগুলোর নাম কীভাবে হবে তা ঠিক করে। যেমন `LABEL_STYLE_TABLENAME_PLUS_COL` দিলে `users_id`, `users_name`; দুই টেবিলে একই নামের কলাম থাকলে কাজে লাগে।

**উদাহরণ:**

```python
stmt = select(User.id, Address.id).join(User.addresses).set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)
print(list(session.execute(stmt).keys()))   # ['users_id', 'addresses_id']
```

### `Select.slice()` { #select-slice }

```python
Select.slice(start, stop)
```

**ধরন:** মেথড

Python-এর slice-এর মতো `[start:stop]` দিয়ে LIMIT/OFFSET বসায়। `slice(1, 3)` = দ্বিতীয় ও তৃতীয় রো।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.id).slice(1, 3)).all())   # ['করিম', 'সুমি']
```

### `Select.stringify_dialect` { #select-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")।

### `Select.subquery()` { #select-subquery }

```python
Select.subquery(name=None)
```

**ধরন:** মেথড

এই SELECT-কে FROM-এ বসানোর মতো একটি নামযুক্ত সাবকুয়েরি বানায়। এর কলাম `.c` দিয়ে পাওয়া যায়। ORM-এ এন্টিটি হিসেবে পেতে `aliased(User, sub)`।

**উদাহরণ:**

```python
sub = select(Address.user_id, func.count().label("n")).group_by(Address.user_id).subquery()
stmt = select(User.name, sub.c.n).join(sub, sub.c.user_id == User.id)
print(session.execute(stmt).all())   # [('রহিম', 2)]
```

### `Select.suffix_with()` { #select-suffix-with }

```python
Select.suffix_with(*suffixes, dialect='*')
```

**ধরন:** মেথড

পুরো স্টেটমেন্টের শেষে কিছু যোগ করে (ডেটাবেস-নির্দিষ্ট অপশনের জন্য)।

**উদাহরণ:**

```python
print(select(User.id).suffix_with("-- রিপোর্ট"))   # SELECT users.id FROM users -- রিপোর্ট
```

### `Select.supports_execution` { #select-supports-execution }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)।

### `Select.union()` { #select-union }

```python
Select.union(*other)
```

**ধরন:** মেথড

দুটি SELECT-এর রো একসাথে দেয়, ডুপ্লিকেট বাদ দিয়ে (`UNION`)। দুটিতেই কলাম সংখ্যা ও ধরন এক হতে হবে।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id == 1).union(select(User.name).where(User.id < 3))
print(sorted(session.scalars(stmt).all()))   # ['করিম', 'রহিম']
```

### `Select.union_all()` { #select-union-all }

```python
Select.union_all(*other)
```

**ধরন:** মেথড

`UNION ALL`: ডুপ্লিকেটসহ সব রো; `union()`-এর চেয়ে দ্রুত।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id == 1).union_all(select(User.name).where(User.id < 3))
print(sorted(session.scalars(stmt).all()))   # ['করিম', 'রহিম', 'রহিম']
```

### `Select.unique_params()` { #select-unique-params }

```python
Select.unique_params(**kwargs)
```

**ধরন:** মেথড

`params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়।

**উদাহরণ:**

```python
s = select(User.id).where(User.id == bindparam("x"))
stmt = union(s.unique_params(x=1), s.unique_params(x=2))
print(sorted(session.scalars(stmt).all()))   # [1, 2]
```

### `Select.uses_inspection` { #select-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না।

### `Select.where()` { #select-where }

```python
Select.where(*whereclause)
```

**ধরন:** মেথড

`WHERE` শর্ত যোগ করে। কমা দিয়ে একাধিক শর্ত দিলে বা বারবার ডাকলে সব `AND` হয়। `or_()`, `and_()`, `not_()` দিয়ে জটিল শর্ত।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id > 1, User.name != "সুমি")
print(session.scalars(stmt).all())   # ['করিম']
```

### `Select.whereclause` { #select-whereclause }

**ধরন:** প্রপার্টি

এ পর্যন্ত যোগ করা সব WHERE শর্ত একসাথে (একটি এক্সপ্রেশন) দেয়; না থাকলে `None`।

**উদাহরণ:**

```python
stmt = select(User).where(User.id > 1).where(User.name != "x")
print(stmt.whereclause)   # users.id > :id_1 AND users.name != :name_1
```

### `Select.with_for_update()` { #select-with-for-update }

```python
Select.with_for_update(*, nowait=False, read=False, of=None, skip_locked=False, key_share=False)
```

**ধরন:** মেথড

`SELECT ... FOR UPDATE` বানায়: পড়া রো-গুলো ট্রানজ্যাকশন শেষ না হওয়া পর্যন্ত লক থাকে। `nowait=True`, `skip_locked=True`, `read=True` (FOR SHARE), `of=` দেওয়া যায়। বিস্তারিত [Concurrency](../concurrency.md#s47-3)।

**উদাহরণ:**

```python
with session.begin():
    user = session.scalars(select(User).where(User.id == 1).with_for_update()).one()
    user.name = "লক করে বদলানো"
```

### `Select.with_hint()` { #select-with-hint }

```python
Select.with_hint(selectable, text, dialect_name='*')
```

**ধরন:** মেথড

নির্দিষ্ট একটি টেবিলের জন্য ডেটাবেস-নির্দিষ্ট hint (যেমন Oracle/MySQL-এর index hint) যোগ করে। যেসব ডেটাবেস সাপোর্ট করে না (যেমন PostgreSQL), সেখানে কিছু বসে না।

**উদাহরণ:**

```python
stmt = select(User.id).with_hint(User, "USE INDEX (ix_name)", dialect_name="mysql")
print(stmt.compile(dialect=postgresql.dialect()))   # PostgreSQL-এ hint নেই: SELECT users.id FROM users
```

### `Select.with_only_columns()` { #select-with-only-columns }

```python
Select.with_only_columns(*entities, maintain_column_froms=False)
```

**ধরন:** মেথড

বিদ্যমান স্টেটমেন্টের কলামের তালিকা পুরো বদলে দেয় (WHERE, JOIN ইত্যাদি থাকে)। যেমন একই ফিল্টার রেখে শুধু গণনা।

**উদাহরণ:**

```python
stmt = select(User).where(User.id > 1)
count_stmt = stmt.with_only_columns(func.count())
print(session.scalar(count_stmt))   # 2
```

### `Select.with_statement_hint()` { #select-with-statement-hint }

```python
Select.with_statement_hint(text, dialect_name='*')
```

**ধরন:** মেথড

পুরো স্টেটমেন্টের জন্য hint যোগ করে, সাধারণত শেষে। SQL Server-এর `OPTION (...)` জাতীয় কাজে।

**উদাহরণ:**

```python
stmt = select(User.id).with_statement_hint("OPTION (MAXDOP 1)", dialect_name="mssql")
```

## `union()` { #union }

```python
from sqlalchemy import union
```

```python
union(*selects)
```

**ধরন:** ফাংশন

কয়েকটি SELECT-এর রো একসাথে দেয়, ডুপ্লিকেট বাদ দিয়ে (`UNION`)। `Select.union()`-এর ফাংশন রূপ, দুইয়ের বেশি SELECT একসাথে জুড়তে সুবিধাজনক।

**উদাহরণ:**

```python
stmt = union(select(User.name).where(User.id == 1), select(User.name).where(User.id == 3))
print(sorted(session.scalars(stmt).all()))   # ['রহিম', 'সুমি']
```

## `union_all()` { #union-all }

```python
from sqlalchemy import union_all
```

```python
union_all(*selects)
```

**ধরন:** ফাংশন

`UNION ALL`: ডুপ্লিকেটসহ সব রো। ডুপ্লিকেট বাদ দেওয়ার দরকার না থাকলে এটিই দ্রুত।

**উদাহরণ:**

```python
stmt = union_all(select(literal("ক")), select(literal("ক")))
print(session.scalars(stmt).all())   # ['ক', 'ক']
```

## `intersect()` { #intersect }

```python
from sqlalchemy import intersect
```

```python
intersect(*selects)
```

**ধরন:** ফাংশন

সব SELECT-এ উপস্থিত রো (`INTERSECT`)।

**উদাহরণ:**

```python
print(session.scalars(intersect(select(User.id), select(Address.user_id))).all())   # [1]
```

## `intersect_all()` { #intersect-all }

```python
from sqlalchemy import intersect_all
```

```python
intersect_all(*selects)
```

**ধরন:** ফাংশন

`INTERSECT ALL`: ডুপ্লিকেট গুনে মিল।

**উদাহরণ:**

```python
print(session.scalars(intersect_all(select(Address.user_id), select(Address.user_id))).all())   # [1, 1]
```

## `except_()` { #except- }

```python
from sqlalchemy import except_
```

```python
except_(*selects)
```

**ধরন:** ফাংশন

প্রথম SELECT-এ আছে কিন্তু পরেরটিতে নেই এমন রো (`EXCEPT`)।

**উদাহরণ:**

```python
print(sorted(session.scalars(except_(select(User.id), select(Address.user_id))).all()))   # [2, 3]
```

## `except_all()` { #except-all }

```python
from sqlalchemy import except_all
```

```python
except_all(*selects)
```

**ধরন:** ফাংশন

`EXCEPT ALL`: ডুপ্লিকেট গুনে বাদ দেয়।

**উদাহরণ:**

```python
print(session.scalars(except_all(select(Address.user_id), select(literal(1)))).all())   # [1]
```

## `CompoundSelect` { #compoundselect }

```python
from sqlalchemy.sql.expression import CompoundSelect
```

`union()`, `intersect()`, `except_()` ইত্যাদি থেকে পাওয়া মিলিত SELECT। এর ওপরও `order_by()`, `limit()`, `subquery()` ইত্যাদি চলে (পুরো ফলাফলের ওপর)। বাকি মেথডগুলোর কাজ `Select`-এর মতো।

**উদাহরণ:**

```python
stmt = union(select(User.name), select(Address.email)).order_by("name").limit(2)
print(session.scalars(stmt).all())   # ['rahim@example.com', 'rahim@work.com'] — ক্রম ডেটাবেসের collation অনুযায়ী
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #compoundselect-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`EXCEPT`](#compoundselect-EXCEPT) | অ্যাট্রিবিউট (internal) | কোন ধরনের সেট-অপারেশন তা বোঝানোর ভেতরের ধ্রুবক (`EXCEPT`)। |
| [`EXCEPT_ALL`](#compoundselect-EXCEPT-ALL) | অ্যাট্রিবিউট (internal) | ধ্রুবক: `EXCEPT ALL`। |
| [`INTERSECT`](#compoundselect-INTERSECT) | অ্যাট্রিবিউট (internal) | ধ্রুবক: `INTERSECT`। |
| [`INTERSECT_ALL`](#compoundselect-INTERSECT-ALL) | অ্যাট্রিবিউট (internal) | ধ্রুবক: `INTERSECT ALL`। |
| [`UNION`](#compoundselect-UNION) | অ্যাট্রিবিউট (internal) | ধ্রুবক: `UNION`। |
| [`UNION_ALL`](#compoundselect-UNION-ALL) | অ্যাট্রিবিউট (internal) | ধ্রুবক: `UNION ALL`। |
| [`add_cte()`](#compoundselect-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`alias()`](#compoundselect-alias) | মেথড | `subquery()`-এর আরেক নাম: এই SELECT-কে একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`allows_lambda`](#compoundselect-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`argument_for()`](#compoundselect-argument-for) | ক্লাস মেথড | এই ধরনের কনস্ট্রাক্টে নতুন ডায়ালেক্ট-নির্দিষ্ট keyword argument নিবন্ধন করে (ক্লাস মেথড)। |
| [`as_scalar()`](#compoundselect-as-scalar) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`compare()`](#compoundselect-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#compoundselect-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#compoundselect-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#compoundselect-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`description`](#compoundselect-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`dialect_kwargs`](#compoundselect-dialect-kwargs) | প্রপার্টি | এই কনস্ট্রাক্টে দেওয়া ডায়ালেক্ট-নির্দিষ্ট অপশন (`<ডায়ালেক্ট>_<নাম>` আকারে)। |
| [`dialect_options`](#compoundselect-dialect-options) | প্রপার্টি | `dialect_kwargs`-এর দুই স্তরের রূপ: `[ডায়ালেক্ট][অপশন]`, ডিফল্ট মানসহ। |
| [`entity_namespace`](#compoundselect-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`execution_options()`](#compoundselect-execution-options) | মেথড | স্টেটমেন্টের সাথে চালানোর সময়ের অপশন যুক্ত করে, যেমন `yield_per`, `populate_existing`, `synchronize_session`। |
| [`exists()`](#compoundselect-exists) | মেথড | এই SELECT-কে `EXISTS (...)` এক্সপ্রেশন বানায়, যা `where()`-এ শর্ত হিসেবে বা কলাম হিসেবে ব্যবহার করা যায়। |
| [`exported_columns`](#compoundselect-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`fetch()`](#compoundselect-fetch) | মেথড | SQL স্ট্যান্ডার্ড `FETCH FIRST n ROWS ONLY` দেয় (`limit()`-এর বিকল্প)। |
| [`get_children()`](#compoundselect-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`get_dialect_option()`](#compoundselect-get-dialect-option) | মেথড | একটি ডায়ালেক্ট-নির্দিষ্ট অপশনের মান দেয়, না থাকলে `else_`। |
| [`get_execution_options()`](#compoundselect-get-execution-options) | মেথড | `execution_options()` দিয়ে যোগ করা অপশনগুলো দেয়। |
| [`get_label_style()`](#compoundselect-get-label-style) | মেথড | বর্তমান label style (কলামের নামকরণের নিয়ম) দেয়। |
| [`group_by()`](#compoundselect-group-by) | মেথড | `GROUP BY` যোগ করে। |
| [`inherit_cache`](#compoundselect-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`into()`](#compoundselect-into) | মেথড | (২.১-এ নতুন) এই SELECT-এর ফল দিয়ে নতুন একটি টেবিল বানানোর `CREATE TABLE ... AS SELECT ...` স্টেটমেন্ট দেয়। |
| [`is_clause_element`](#compoundselect-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_delete`](#compoundselect-is-delete) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি DELETE স্টেটমেন্ট কি না (`Select`-এ `False`)। |
| [`is_derived_from()`](#compoundselect-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#compoundselect-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_from_statement`](#compoundselect-is-from-statement) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: ORM-এর `from_statement()` থেকে তৈরি কি না। |
| [`is_insert`](#compoundselect-is-insert) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT কি না। |
| [`is_select`](#compoundselect-is-select) | অ্যাট্রিবিউট | এটি SELECT স্টেটমেন্ট হলে `True`। |
| [`is_selectable`](#compoundselect-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`is_text`](#compoundselect-is-text) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `text()` থেকে তৈরি কি না। |
| [`is_update`](#compoundselect-is-update) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: UPDATE কি না। |
| [`kwargs`](#compoundselect-kwargs) | প্রপার্টি | `dialect_kwargs`-এর আরেক নাম। |
| [`label()`](#compoundselect-label) | মেথড | এই SELECT-কে একটি নাম দেওয়া scalar সাবকুয়েরি বানায়, যাতে বাইরের SELECT-এ কলাম হিসেবে বসানো যায়। |
| [`lateral()`](#compoundselect-lateral) | মেথড | `LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`limit()`](#compoundselect-limit) | মেথড | `LIMIT`: সর্বোচ্চ কয়টি রো আসবে। |
| [`memoized_attribute`](#compoundselect-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#compoundselect-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#compoundselect-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`offset()`](#compoundselect-offset) | মেথড | `OFFSET`: শুরু থেকে কয়টি রো বাদ যাবে (pagination-এ `limit()`-এর সাথে)। |
| [`options()`](#compoundselect-options) | মেথড | ORM অপশন যুক্ত করে, যেমন লোডিং অপশন (`selectinload`, `joinedload`, `load_only`)। |
| [`order_by()`](#compoundselect-order-by) | মেথড | `ORDER BY` যোগ করে। |
| [`params()`](#compoundselect-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`reflect_only_elements`](#compoundselect-reflect-only-elements) | প্রপার্টি | (২.১-এ নতুন) ডেটাবেস reflection থেকে পাওয়া ডায়ালেক্ট-নির্দিষ্ট তথ্য। |
| [`replace_selectable()`](#compoundselect-replace-selectable) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`scalar_subquery()`](#compoundselect-scalar-subquery) | মেথড | এক রো, এক কলাম দেয় এমন SELECT-কে একটি মান হিসেবে (scalar) ব্যবহারযোগ্য করে, যাতে অন্য SELECT-এর কলামে বা WHERE-এ বসানো যায়। |
| [`selectable`](#compoundselect-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`selected_columns`](#compoundselect-selected-columns) | প্রপার্টি | এই SELECT যে কলামগুলো ফেরত দেবে তার সংগ্রহ। |
| [`self_group()`](#compoundselect-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`set_label_style()`](#compoundselect-set-label-style) | মেথড | ফলাফলের কলামগুলোর নাম কীভাবে হবে তা ঠিক করে। |
| [`slice()`](#compoundselect-slice) | মেথড | Python-এর slice-এর মতো `[start:stop]` দিয়ে LIMIT/OFFSET বসায়। |
| [`stringify_dialect`](#compoundselect-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`subquery()`](#compoundselect-subquery) | মেথড | এই SELECT-কে FROM-এ বসানোর মতো একটি নামযুক্ত সাবকুয়েরি বানায়। |
| [`supports_execution`](#compoundselect-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`unique_params()`](#compoundselect-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#compoundselect-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`with_for_update()`](#compoundselect-with-for-update) | মেথড | `SELECT ... FOR UPDATE` বানায়: পড়া রো-গুলো ট্রানজ্যাকশন শেষ না হওয়া পর্যন্ত লক থাকে। |

### `CompoundSelect.EXCEPT` { #compoundselect-EXCEPT }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন ধরনের সেট-অপারেশন তা বোঝানোর ভেতরের ধ্রুবক (`EXCEPT`)। `stmt.keyword` এর সাথে তুলনা করে চেনা যায়।

**উদাহরণ:**

```python
print(except_(select(User.id), select(Address.user_id)).keyword == CompoundSelect.EXCEPT)   # True
```

### `CompoundSelect.EXCEPT_ALL` { #compoundselect-EXCEPT-ALL }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ধ্রুবক: `EXCEPT ALL`।

### `CompoundSelect.INTERSECT` { #compoundselect-INTERSECT }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ধ্রুবক: `INTERSECT`।

### `CompoundSelect.INTERSECT_ALL` { #compoundselect-INTERSECT-ALL }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ধ্রুবক: `INTERSECT ALL`।

### `CompoundSelect.UNION` { #compoundselect-UNION }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ধ্রুবক: `UNION`।

**উদাহরণ:**

```python
print(union(select(User.id), select(Address.user_id)).keyword == CompoundSelect.UNION)   # True
```

### `CompoundSelect.UNION_ALL` { #compoundselect-UNION-ALL }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ধ্রুবক: `UNION ALL`।

### `CompoundSelect.add_cte()` { #compoundselect-add-cte }

```python
CompoundSelect.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](#select-add-cte)-এর মতো।

### `CompoundSelect.alias()` { #compoundselect-alias }

```python
CompoundSelect.alias(name=None, flat=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.alias`](#select-alias)-এর মতো।

### `CompoundSelect.allows_lambda` { #compoundselect-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](#select-allows-lambda)-এর মতো।

### `CompoundSelect.argument_for()` { #compoundselect-argument-for }

```python
CompoundSelect.argument_for(dialect_name, argument_name, default)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.argument_for`](#select-argument-for)-এর মতো।

### `CompoundSelect.as_scalar()` { #compoundselect-as-scalar }

```python
CompoundSelect.as_scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.as_scalar`](#select-as-scalar)-এর মতো।

### `CompoundSelect.compare()` { #compoundselect-compare }

```python
CompoundSelect.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](#select-compare)-এর মতো।

### `CompoundSelect.compile()` { #compoundselect-compile }

```python
CompoundSelect.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](#select-compile)-এর মতো।

### `CompoundSelect.corresponding_column()` { #compoundselect-corresponding-column }

```python
CompoundSelect.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](#select-corresponding-column)-এর মতো।

### `CompoundSelect.cte()` { #compoundselect-cte }

```python
CompoundSelect.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](#select-cte)-এর মতো।

### `CompoundSelect.description` { #compoundselect-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](#select-description)-এর মতো।

### `CompoundSelect.dialect_kwargs` { #compoundselect-dialect-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_kwargs`](#select-dialect-kwargs)-এর মতো।

### `CompoundSelect.dialect_options` { #compoundselect-dialect-options }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.dialect_options`](#select-dialect-options)-এর মতো।

### `CompoundSelect.entity_namespace` { #compoundselect-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](#select-entity-namespace)-এর মতো।

### `CompoundSelect.execution_options()` { #compoundselect-execution-options }

```python
CompoundSelect.execution_options(**kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.execution_options`](#select-execution-options)-এর মতো।

### `CompoundSelect.exists()` { #compoundselect-exists }

```python
CompoundSelect.exists()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.exists`](#select-exists)-এর মতো।

### `CompoundSelect.exported_columns` { #compoundselect-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.exported_columns`](#select-exported-columns)-এর মতো।

### `CompoundSelect.fetch()` { #compoundselect-fetch }

```python
CompoundSelect.fetch(count, with_ties=False, percent=False, **dialect_kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.fetch`](#select-fetch)-এর মতো।

### `CompoundSelect.get_children()` { #compoundselect-get-children }

```python
CompoundSelect.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](#select-get-children)-এর মতো।

### `CompoundSelect.get_dialect_option()` { #compoundselect-get-dialect-option }

```python
CompoundSelect.get_dialect_option(dialect, argument_name, *, else_=None, deprecated_fallback=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_dialect_option`](#select-get-dialect-option)-এর মতো।

### `CompoundSelect.get_execution_options()` { #compoundselect-get-execution-options }

```python
CompoundSelect.get_execution_options()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_execution_options`](#select-get-execution-options)-এর মতো।

### `CompoundSelect.get_label_style()` { #compoundselect-get-label-style }

```python
CompoundSelect.get_label_style()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_label_style`](#select-get-label-style)-এর মতো।

### `CompoundSelect.group_by()` { #compoundselect-group-by }

```python
CompoundSelect.group_by(*clauses)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.group_by`](#select-group-by)-এর মতো।

### `CompoundSelect.inherit_cache` { #compoundselect-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](#select-inherit-cache)-এর মতো।

### `CompoundSelect.into()` { #compoundselect-into }

```python
CompoundSelect.into(target, *, metadata=None, schema=None, temporary=False, if_not_exists=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.into`](#select-into)-এর মতো।

### `CompoundSelect.is_clause_element` { #compoundselect-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](#select-is-clause-element)-এর মতো।

### `CompoundSelect.is_delete` { #compoundselect-is-delete }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_delete`](#select-is-delete)-এর মতো।

### `CompoundSelect.is_derived_from()` { #compoundselect-is-derived-from }

```python
CompoundSelect.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](#select-is-derived-from)-এর মতো।

### `CompoundSelect.is_dml` { #compoundselect-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](#select-is-dml)-এর মতো।

### `CompoundSelect.is_from_statement` { #compoundselect-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_from_statement`](#select-is-from-statement)-এর মতো।

### `CompoundSelect.is_insert` { #compoundselect-is-insert }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_insert`](#select-is-insert)-এর মতো।

### `CompoundSelect.is_select` { #compoundselect-is-select }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_select`](#select-is-select)-এর মতো।

### `CompoundSelect.is_selectable` { #compoundselect-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](#select-is-selectable)-এর মতো।

### `CompoundSelect.is_text` { #compoundselect-is-text }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_text`](#select-is-text)-এর মতো।

### `CompoundSelect.is_update` { #compoundselect-is-update }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_update`](#select-is-update)-এর মতো।

### `CompoundSelect.kwargs` { #compoundselect-kwargs }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.kwargs`](#select-kwargs)-এর মতো।

### `CompoundSelect.label()` { #compoundselect-label }

```python
CompoundSelect.label(name)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.label`](#select-label)-এর মতো।

### `CompoundSelect.lateral()` { #compoundselect-lateral }

```python
CompoundSelect.lateral(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.lateral`](#select-lateral)-এর মতো।

### `CompoundSelect.limit()` { #compoundselect-limit }

```python
CompoundSelect.limit(limit)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.limit`](#select-limit)-এর মতো।

### `CompoundSelect.memoized_attribute` { #compoundselect-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](#select-memoized-attribute)-এর মতো।

### `CompoundSelect.memoized_instancemethod()` { #compoundselect-memoized-instancemethod }

```python
CompoundSelect.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](#select-memoized-instancemethod)-এর মতো।

### `CompoundSelect.name_cte_columns` { #compoundselect-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](#select-name-cte-columns)-এর মতো।

### `CompoundSelect.offset()` { #compoundselect-offset }

```python
CompoundSelect.offset(offset)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.offset`](#select-offset)-এর মতো।

### `CompoundSelect.options()` { #compoundselect-options }

```python
CompoundSelect.options(*options)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.options`](#select-options)-এর মতো।

### `CompoundSelect.order_by()` { #compoundselect-order-by }

```python
CompoundSelect.order_by(*clauses)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.order_by`](#select-order-by)-এর মতো।

### `CompoundSelect.params()` { #compoundselect-params }

```python
CompoundSelect.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](#select-params)-এর মতো।

### `CompoundSelect.reflect_only_elements` { #compoundselect-reflect-only-elements }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.reflect_only_elements`](#select-reflect-only-elements)-এর মতো।

### `CompoundSelect.replace_selectable()` { #compoundselect-replace-selectable }

```python
CompoundSelect.replace_selectable(old, alias)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.replace_selectable`](#select-replace-selectable)-এর মতো।

### `CompoundSelect.scalar_subquery()` { #compoundselect-scalar-subquery }

```python
CompoundSelect.scalar_subquery()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.scalar_subquery`](#select-scalar-subquery)-এর মতো।

### `CompoundSelect.selectable` { #compoundselect-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](#select-selectable)-এর মতো।

### `CompoundSelect.selected_columns` { #compoundselect-selected-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selected_columns`](#select-selected-columns)-এর মতো।

### `CompoundSelect.self_group()` { #compoundselect-self-group }

```python
CompoundSelect.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](#select-self-group)-এর মতো।

### `CompoundSelect.set_label_style()` { #compoundselect-set-label-style }

```python
CompoundSelect.set_label_style(style)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.set_label_style`](#select-set-label-style)-এর মতো।

### `CompoundSelect.slice()` { #compoundselect-slice }

```python
CompoundSelect.slice(start, stop)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.slice`](#select-slice)-এর মতো।

### `CompoundSelect.stringify_dialect` { #compoundselect-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](#select-stringify-dialect)-এর মতো।

### `CompoundSelect.subquery()` { #compoundselect-subquery }

```python
CompoundSelect.subquery(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.subquery`](#select-subquery)-এর মতো।

### `CompoundSelect.supports_execution` { #compoundselect-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](#select-supports-execution)-এর মতো।

### `CompoundSelect.unique_params()` { #compoundselect-unique-params }

```python
CompoundSelect.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](#select-unique-params)-এর মতো।

### `CompoundSelect.uses_inspection` { #compoundselect-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](#select-uses-inspection)-এর মতো।

### `CompoundSelect.with_for_update()` { #compoundselect-with-for-update }

```python
CompoundSelect.with_for_update(*, nowait=False, read=False, of=None, skip_locked=False, key_share=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.with_for_update`](#select-with-for-update)-এর মতো।

## `Subquery` { #subquery }

```python
from sqlalchemy.sql.expression import Subquery
```

`stmt.subquery()` থেকে পাওয়া নামযুক্ত সাবকুয়েরি, যা একটি টেবিলের মতো আচরণ করে: `.c` দিয়ে কলাম, `join()` দিয়ে জোড়া, আর অন্য `select()`-এর FROM-এ বসানো যায়।

**উদাহরণ:**

```python
sub = select(User.id, User.name).where(User.id > 1).subquery("others")
print(session.execute(select(sub.c.name).order_by(sub.c.id)).scalars().all())   # ['করিম', 'সুমি']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #subquery-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`alias()`](#subquery-alias) | মেথড | এই সাবকুয়েরির আরেকটি নামযুক্ত alias দেয়, যাতে একই সাবকুয়েরি একটি কুয়েরিতে দুবার ব্যবহার করা যায়। |
| [`allows_lambda`](#subquery-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`as_scalar()`](#subquery-as-scalar) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`c`](#subquery-c) | প্রপার্টি | সাবকুয়েরির কলামগুলো (`columns`-এর ছোট নাম)। |
| [`columns`](#subquery-columns) | প্রপার্টি | সাবকুয়েরির কলামের নাম-ভিত্তিক সংগ্রহ (`ColumnCollection`)। |
| [`compare()`](#subquery-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#subquery-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#subquery-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`description`](#subquery-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`entity_namespace`](#subquery-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`exported_columns`](#subquery-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`foreign_keys`](#subquery-foreign-keys) | প্রপার্টি | এই সাবকুয়েরির কলামগুলো যেসব ফরেন কি রেফার করে তার সংগ্রহ (মূল টেবিল থেকে আসে)। |
| [`get_children()`](#subquery-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`implicit_returning`](#subquery-implicit-returning) | প্রপার্টি (internal) | `Table`-এর সাথে সামঞ্জস্যের জন্য রাখা ভেতরের ফ্ল্যাগ; সাবকুয়েরিতে অর্থহীন। |
| [`inherit_cache`](#subquery-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`is_clause_element`](#subquery-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_derived_from()`](#subquery-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#subquery-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_selectable`](#subquery-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`join()`](#subquery-join) | মেথড | এই সাবকুয়েরি আর আরেকটি টেবিল/সাবকুয়েরির `Join` অবজেক্ট বানায় (টেবিলের `join()`-এর মতো), যা `select_from()`-এ বসানো যায়। |
| [`lateral()`](#subquery-lateral) | মেথড | `LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`memoized_attribute`](#subquery-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#subquery-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`named_with_column`](#subquery-named-with-column) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: কলাম রেফার করার সময় এই FROM-এর নাম আগে বসবে কি না (`sub.col`)। |
| [`original`](#subquery-original) | প্রপার্টি (legacy) | যে মূল SELECT থেকে সাবকুয়েরিটি বানানো, সেটি। |
| [`outerjoin()`](#subquery-outerjoin) | মেথড | `join()`-এর মতো, কিন্তু LEFT OUTER JOIN দিয়ে `Join` অবজেক্ট বানায়। |
| [`params()`](#subquery-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`primary_key`](#subquery-primary-key) | প্রপার্টি | সাবকুয়েরির যে কলামগুলো মূল টেবিলের primary key থেকে এসেছে। |
| [`replace_selectable()`](#subquery-replace-selectable) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`schema`](#subquery-schema) | অ্যাট্রিবিউট (internal) | `Table`-এর সাথে সামঞ্জস্যের জন্য; সাবকুয়েরিতে সবসময় `None`। |
| [`select()`](#subquery-select) | মেথড | এই সাবকুয়েরি থেকে সব কলামসহ একটি নতুন `SELECT * FROM (সাবকুয়েরি)` বানায়। |
| [`selectable`](#subquery-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#subquery-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#subquery-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`supports_execution`](#subquery-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`table_valued()`](#subquery-table-valued) | মেথড | পুরো রো-কে একটি কলাম হিসেবে উপস্থাপন করে (PostgreSQL-এ রো-টিকে একটি record/composite মান হিসেবে)। |
| [`tablesample()`](#subquery-tablesample) | মেথড | `TABLESAMPLE` দিয়ে টেবিলের এলোমেলো নমুনা (শতাংশ হিসেবে) নেওয়ার alias বানায়। |
| [`unique_params()`](#subquery-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#subquery-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`with_cols()`](#subquery-with-cols) | মেথড | (২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-কে একটি নির্দিষ্ট `TypedColumns` ক্লাসের কলাম আছে বলে ঘোষণা করে। |

### `Subquery.alias()` { #subquery-alias }

```python
Subquery.alias(name=None, flat=False)
```

**ধরন:** মেথড

এই সাবকুয়েরির আরেকটি নামযুক্ত alias দেয়, যাতে একই সাবকুয়েরি একটি কুয়েরিতে দুবার ব্যবহার করা যায়।

**উদাহরণ:**

```python
sub = select(User.id).subquery()
a1, a2 = sub.alias("a1"), sub.alias("a2")
print(session.execute(select(a1.c.id, a2.c.id).where(a1.c.id == a2.c.id).order_by(a1.c.id)).first())   # (1, 1)
```

### `Subquery.allows_lambda` { #subquery-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](#select-allows-lambda)-এর মতো।

### `Subquery.as_scalar()` { #subquery-as-scalar }

```python
Subquery.as_scalar()
```

**ধরন:** মেথড

কাজ হুবহু [`Select.as_scalar`](#select-as-scalar)-এর মতো।

### `Subquery.c` { #subquery-c }

**ধরন:** প্রপার্টি

সাবকুয়েরির কলামগুলো (`columns`-এর ছোট নাম)। `sub.c.name` এভাবে।

**উদাহরণ:**

```python
sub = select(User.id, User.name).subquery()
print(list(sub.c.keys()))   # ['id', 'name']
```

### `Subquery.columns` { #subquery-columns }

**ধরন:** প্রপার্টি

সাবকুয়েরির কলামের নাম-ভিত্তিক সংগ্রহ (`ColumnCollection`)। `.c` একই জিনিস।

**উদাহরণ:**

```python
sub = select(User.id, User.name).subquery()
print(sub.columns.name is sub.c.name)   # True
```

### `Subquery.compare()` { #subquery-compare }

```python
Subquery.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](#select-compare)-এর মতো।

### `Subquery.compile()` { #subquery-compile }

```python
Subquery.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](#select-compile)-এর মতো।

### `Subquery.corresponding_column()` { #subquery-corresponding-column }

```python
Subquery.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](#select-corresponding-column)-এর মতো।

### `Subquery.description` { #subquery-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](#select-description)-এর মতো।

### `Subquery.entity_namespace` { #subquery-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](#select-entity-namespace)-এর মতো।

### `Subquery.exported_columns` { #subquery-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.exported_columns`](#select-exported-columns)-এর মতো।

### `Subquery.foreign_keys` { #subquery-foreign-keys }

**ধরন:** প্রপার্টি

এই সাবকুয়েরির কলামগুলো যেসব ফরেন কি রেফার করে তার সংগ্রহ (মূল টেবিল থেকে আসে)।

**উদাহরণ:**

```python
sub = select(Address.id, Address.user_id).subquery()
print(len(sub.foreign_keys))   # 1
```

### `Subquery.get_children()` { #subquery-get-children }

```python
Subquery.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](#select-get-children)-এর মতো।

### `Subquery.implicit_returning` { #subquery-implicit-returning }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Table`-এর সাথে সামঞ্জস্যের জন্য রাখা ভেতরের ফ্ল্যাগ; সাবকুয়েরিতে অর্থহীন।

### `Subquery.inherit_cache` { #subquery-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](#select-inherit-cache)-এর মতো।

### `Subquery.is_clause_element` { #subquery-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](#select-is-clause-element)-এর মতো।

### `Subquery.is_derived_from()` { #subquery-is-derived-from }

```python
Subquery.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](#select-is-derived-from)-এর মতো।

### `Subquery.is_dml` { #subquery-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](#select-is-dml)-এর মতো।

### `Subquery.is_selectable` { #subquery-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](#select-is-selectable)-এর মতো।

### `Subquery.join()` { #subquery-join }

```python
Subquery.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

এই সাবকুয়েরি আর আরেকটি টেবিল/সাবকুয়েরির `Join` অবজেক্ট বানায় (টেবিলের `join()`-এর মতো), যা `select_from()`-এ বসানো যায়। `Select.join()` থেকে আলাদা: সেটা SELECT-এ join যোগ করে, এটা একটি নতুন FROM বানায়।

**উদাহরণ:**

```python
sub = select(Address.user_id).distinct().subquery()
j = sub.join(User.__table__, sub.c.user_id == User.__table__.c.id)
print(session.execute(select(User.__table__.c.name).select_from(j)).scalars().all())   # ['রহিম']
```

### `Subquery.lateral()` { #subquery-lateral }

```python
Subquery.lateral(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.lateral`](#select-lateral)-এর মতো।

### `Subquery.memoized_attribute` { #subquery-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](#select-memoized-attribute)-এর মতো।

### `Subquery.memoized_instancemethod()` { #subquery-memoized-instancemethod }

```python
Subquery.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](#select-memoized-instancemethod)-এর মতো।

### `Subquery.named_with_column` { #subquery-named-with-column }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: কলাম রেফার করার সময় এই FROM-এর নাম আগে বসবে কি না (`sub.col`)।

### `Subquery.original` { #subquery-original }

**ধরন:** প্রপার্টি

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

যে মূল SELECT থেকে সাবকুয়েরিটি বানানো, সেটি। পুরোনো ডায়ালেক্টের সামঞ্জস্যের জন্য রাখা।

**উদাহরণ:**

```python
stmt = select(User.id)
print(stmt.subquery().original is stmt)   # True
```

### `Subquery.outerjoin()` { #subquery-outerjoin }

```python
Subquery.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

`join()`-এর মতো, কিন্তু LEFT OUTER JOIN দিয়ে `Join` অবজেক্ট বানায়।

**উদাহরণ:**

```python
sub = select(Address.user_id).distinct().subquery()
j = User.__table__.outerjoin(sub, sub.c.user_id == User.__table__.c.id)
print(len(session.execute(select(User.__table__.c.id).select_from(j)).all()))   # 3
```

### `Subquery.params()` { #subquery-params }

```python
Subquery.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](#select-params)-এর মতো।

### `Subquery.primary_key` { #subquery-primary-key }

**ধরন:** প্রপার্টি

সাবকুয়েরির যে কলামগুলো মূল টেবিলের primary key থেকে এসেছে।

**উদাহরণ:**

```python
sub = select(User.id, User.name).subquery()
print([c.name for c in sub.primary_key])   # ['id']
```

### `Subquery.replace_selectable()` { #subquery-replace-selectable }

```python
Subquery.replace_selectable(old, alias)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.replace_selectable`](#select-replace-selectable)-এর মতো।

### `Subquery.schema` { #subquery-schema }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Table`-এর সাথে সামঞ্জস্যের জন্য; সাবকুয়েরিতে সবসময় `None`।

### `Subquery.select()` { #subquery-select }

```python
Subquery.select()
```

**ধরন:** মেথড

এই সাবকুয়েরি থেকে সব কলামসহ একটি নতুন `SELECT * FROM (সাবকুয়েরি)` বানায়।

**উদাহরণ:**

```python
sub = select(User.name).where(User.id == 2).subquery()
print(session.execute(sub.select()).scalar())   # করিম
```

### `Subquery.selectable` { #subquery-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](#select-selectable)-এর মতো।

### `Subquery.self_group()` { #subquery-self-group }

```python
Subquery.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](#select-self-group)-এর মতো।

### `Subquery.stringify_dialect` { #subquery-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](#select-stringify-dialect)-এর মতো।

### `Subquery.supports_execution` { #subquery-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](#select-supports-execution)-এর মতো।

### `Subquery.table_valued()` { #subquery-table-valued }

```python
Subquery.table_valued()
```

**ধরন:** মেথড

পুরো রো-কে একটি কলাম হিসেবে উপস্থাপন করে (PostgreSQL-এ রো-টিকে একটি record/composite মান হিসেবে)। যেমন একটি রো JSON বানাতে।

**উদাহরণ:**

```python
sub = select(User.id, User.name).where(User.id == 1).subquery("u")
print(session.execute(select(func.row_to_json(sub.table_valued()))).scalar())   # {'id': 1, 'name': 'রহিম'}
```

### `Subquery.tablesample()` { #subquery-tablesample }

```python
Subquery.tablesample(sampling, name=None, seed=None)
```

**ধরন:** মেথড

`TABLESAMPLE` দিয়ে টেবিলের এলোমেলো নমুনা (শতাংশ হিসেবে) নেওয়ার alias বানায়। বিশাল টেবিল থেকে দ্রুত নমুনা নিতে।

**উদাহরণ:**

```python
sample = User.__table__.tablesample(func.bernoulli(100), name="s")
print(session.execute(select(func.count()).select_from(sample)).scalar())   # 3 (১০০% নমুনা)
```

### `Subquery.unique_params()` { #subquery-unique-params }

```python
Subquery.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](#select-unique-params)-এর মতো।

### `Subquery.uses_inspection` { #subquery-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](#select-uses-inspection)-এর মতো।

### `Subquery.with_cols()` { #subquery-with-cols }

```python
Subquery.with_cols(type_)
```

**ধরন:** মেথড

(২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-কে একটি নির্দিষ্ট `TypedColumns` ক্লাসের কলাম আছে বলে ঘোষণা করে। রানটাইমে কিছুই বদলায় না, নিজেকেই ফেরত দেয়।

## `CTE` { #cte }

```python
from sqlalchemy.sql.expression import CTE
```

`stmt.cte()` থেকে পাওয়া Common Table Expression (`WITH নাম AS (...)`)। সাবকুয়েরির মতোই `.c` দিয়ে কলাম, আর FROM-এ বসানো যায়। recursive CTE-তে `union_all()` দিয়ে নিজের সাথে জোড়া হয়। পূর্ণ উদাহরণ: [Recursive CTE](../advanced-queries.md#s27-2)।

**উদাহরণ:**

```python
nums = select(literal(1).label("n")).cte("nums", recursive=True)
nums = nums.union_all(select(nums.c.n + 1).where(nums.c.n < 5))
print(session.execute(select(nums.c.n)).scalars().all())   # [1, 2, 3, 4, 5]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cte-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`alias()`](#cte-alias) | মেথড | এই সাবকুয়েরির আরেকটি নামযুক্ত alias দেয়, যাতে একই সাবকুয়েরি একটি কুয়েরিতে দুবার ব্যবহার করা যায়। |
| [`allows_lambda`](#cte-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`c`](#cte-c) | প্রপার্টি | সাবকুয়েরির কলামগুলো (`columns`-এর ছোট নাম)। |
| [`columns`](#cte-columns) | প্রপার্টি | সাবকুয়েরির কলামের নাম-ভিত্তিক সংগ্রহ (`ColumnCollection`)। |
| [`compare()`](#cte-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#cte-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#cte-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`description`](#cte-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`entity_namespace`](#cte-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`exported_columns`](#cte-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`foreign_keys`](#cte-foreign-keys) | প্রপার্টি | এই সাবকুয়েরির কলামগুলো যেসব ফরেন কি রেফার করে তার সংগ্রহ (মূল টেবিল থেকে আসে)। |
| [`get_children()`](#cte-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`implicit_returning`](#cte-implicit-returning) | প্রপার্টি | `Table`-এর সাথে সামঞ্জস্যের জন্য রাখা ভেতরের ফ্ল্যাগ; সাবকুয়েরিতে অর্থহীন। |
| [`inherit_cache`](#cte-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`is_clause_element`](#cte-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_derived_from()`](#cte-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#cte-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_selectable`](#cte-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`join()`](#cte-join) | মেথড | এই সাবকুয়েরি আর আরেকটি টেবিল/সাবকুয়েরির `Join` অবজেক্ট বানায় (টেবিলের `join()`-এর মতো), যা `select_from()`-এ বসানো যায়। |
| [`lateral()`](#cte-lateral) | মেথড | `LATERAL` সাবকুয়েরি বানায়: এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`memoized_attribute`](#cte-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#cte-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`named_with_column`](#cte-named-with-column) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: কলাম রেফার করার সময় এই FROM-এর নাম আগে বসবে কি না (`sub.col`)। |
| [`original`](#cte-original) | প্রপার্টি | যে মূল SELECT থেকে সাবকুয়েরিটি বানানো, সেটি। |
| [`outerjoin()`](#cte-outerjoin) | মেথড | `join()`-এর মতো, কিন্তু LEFT OUTER JOIN দিয়ে `Join` অবজেক্ট বানায়। |
| [`params()`](#cte-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`prefix_with()`](#cte-prefix-with) | মেথড | `SELECT` শব্দের ঠিক পরে কিছু যোগ করে, যেমন MySQL-এর `HIGH_PRIORITY` বা optimizer hint। |
| [`primary_key`](#cte-primary-key) | প্রপার্টি | সাবকুয়েরির যে কলামগুলো মূল টেবিলের primary key থেকে এসেছে। |
| [`replace_selectable()`](#cte-replace-selectable) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`schema`](#cte-schema) | অ্যাট্রিবিউট | `Table`-এর সাথে সামঞ্জস্যের জন্য; সাবকুয়েরিতে সবসময় `None`। |
| [`select()`](#cte-select) | মেথড | এই সাবকুয়েরি থেকে সব কলামসহ একটি নতুন `SELECT * FROM (সাবকুয়েরি)` বানায়। |
| [`selectable`](#cte-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#cte-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#cte-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`suffix_with()`](#cte-suffix-with) | মেথড | পুরো স্টেটমেন্টের শেষে কিছু যোগ করে (ডেটাবেস-নির্দিষ্ট অপশনের জন্য)। |
| [`supports_execution`](#cte-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`table_valued()`](#cte-table-valued) | মেথড | পুরো রো-কে একটি কলাম হিসেবে উপস্থাপন করে (PostgreSQL-এ রো-টিকে একটি record/composite মান হিসেবে)। |
| [`tablesample()`](#cte-tablesample) | মেথড | `TABLESAMPLE` দিয়ে টেবিলের এলোমেলো নমুনা (শতাংশ হিসেবে) নেওয়ার alias বানায়। |
| [`union()`](#cte-union) | মেথড | recursive CTE বানাতে: এই CTE-র anchor অংশের সাথে recursive অংশ `UNION` (ডুপ্লিকেট বাদ) দিয়ে জোড়ে। |
| [`union_all()`](#cte-union-all) | মেথড | recursive CTE-র সবচেয়ে প্রচলিত রূপ: anchor + recursive অংশ `UNION ALL` দিয়ে জোড়ে। |
| [`unique_params()`](#cte-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#cte-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`with_cols()`](#cte-with-cols) | মেথড | (২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-কে একটি নির্দিষ্ট `TypedColumns` ক্লাসের কলাম আছে বলে ঘোষণা করে। |

### `CTE.alias()` { #cte-alias }

```python
CTE.alias(name=None, flat=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.alias`](#subquery-alias)-এর মতো।

### `CTE.allows_lambda` { #cte-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](#select-allows-lambda)-এর মতো।

### `CTE.c` { #cte-c }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.c`](#subquery-c)-এর মতো।

### `CTE.columns` { #cte-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.columns`](#subquery-columns)-এর মতো।

### `CTE.compare()` { #cte-compare }

```python
CTE.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](#select-compare)-এর মতো।

### `CTE.compile()` { #cte-compile }

```python
CTE.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](#select-compile)-এর মতো।

### `CTE.corresponding_column()` { #cte-corresponding-column }

```python
CTE.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](#select-corresponding-column)-এর মতো।

### `CTE.description` { #cte-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](#select-description)-এর মতো।

### `CTE.entity_namespace` { #cte-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](#select-entity-namespace)-এর মতো।

### `CTE.exported_columns` { #cte-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.exported_columns`](#select-exported-columns)-এর মতো।

### `CTE.foreign_keys` { #cte-foreign-keys }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.foreign_keys`](#subquery-foreign-keys)-এর মতো।

### `CTE.get_children()` { #cte-get-children }

```python
CTE.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](#select-get-children)-এর মতো।

### `CTE.implicit_returning` { #cte-implicit-returning }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.implicit_returning`](#subquery-implicit-returning)-এর মতো।

### `CTE.inherit_cache` { #cte-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](#select-inherit-cache)-এর মতো।

### `CTE.is_clause_element` { #cte-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](#select-is-clause-element)-এর মতো।

### `CTE.is_derived_from()` { #cte-is-derived-from }

```python
CTE.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](#select-is-derived-from)-এর মতো।

### `CTE.is_dml` { #cte-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](#select-is-dml)-এর মতো।

### `CTE.is_selectable` { #cte-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](#select-is-selectable)-এর মতো।

### `CTE.join()` { #cte-join }

```python
CTE.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.join`](#subquery-join)-এর মতো।

### `CTE.lateral()` { #cte-lateral }

```python
CTE.lateral(name=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.lateral`](#select-lateral)-এর মতো।

### `CTE.memoized_attribute` { #cte-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](#select-memoized-attribute)-এর মতো।

### `CTE.memoized_instancemethod()` { #cte-memoized-instancemethod }

```python
CTE.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](#select-memoized-instancemethod)-এর মতো।

### `CTE.named_with_column` { #cte-named-with-column }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Subquery.named_with_column`](#subquery-named-with-column)-এর মতো।

### `CTE.original` { #cte-original }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.original`](#subquery-original)-এর মতো।

### `CTE.outerjoin()` { #cte-outerjoin }

```python
CTE.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.outerjoin`](#subquery-outerjoin)-এর মতো।

### `CTE.params()` { #cte-params }

```python
CTE.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](#select-params)-এর মতো।

### `CTE.prefix_with()` { #cte-prefix-with }

```python
CTE.prefix_with(*prefixes, dialect='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.prefix_with`](#select-prefix-with)-এর মতো।

### `CTE.primary_key` { #cte-primary-key }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.primary_key`](#subquery-primary-key)-এর মতো।

### `CTE.replace_selectable()` { #cte-replace-selectable }

```python
CTE.replace_selectable(old, alias)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.replace_selectable`](#select-replace-selectable)-এর মতো।

### `CTE.schema` { #cte-schema }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Subquery.schema`](#subquery-schema)-এর মতো।

### `CTE.select()` { #cte-select }

```python
CTE.select()
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.select`](#subquery-select)-এর মতো।

### `CTE.selectable` { #cte-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](#select-selectable)-এর মতো।

### `CTE.self_group()` { #cte-self-group }

```python
CTE.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](#select-self-group)-এর মতো।

### `CTE.stringify_dialect` { #cte-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](#select-stringify-dialect)-এর মতো।

### `CTE.suffix_with()` { #cte-suffix-with }

```python
CTE.suffix_with(*suffixes, dialect='*')
```

**ধরন:** মেথড

কাজ হুবহু [`Select.suffix_with`](#select-suffix-with)-এর মতো।

### `CTE.supports_execution` { #cte-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](#select-supports-execution)-এর মতো।

### `CTE.table_valued()` { #cte-table-valued }

```python
CTE.table_valued()
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.table_valued`](#subquery-table-valued)-এর মতো।

### `CTE.tablesample()` { #cte-tablesample }

```python
CTE.tablesample(sampling, name=None, seed=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.tablesample`](#subquery-tablesample)-এর মতো।

### `CTE.union()` { #cte-union }

```python
CTE.union(*other)
```

**ধরন:** মেথড

recursive CTE বানাতে: এই CTE-র anchor অংশের সাথে recursive অংশ `UNION` (ডুপ্লিকেট বাদ) দিয়ে জোড়ে।

**উদাহরণ:**

```python
c = select(literal(1).label("n")).cte("c", recursive=True)
c = c.union(select(c.c.n + 1).where(c.c.n < 3))
print(session.execute(select(c.c.n)).scalars().all())   # [1, 2, 3]
```

### `CTE.union_all()` { #cte-union-all }

```python
CTE.union_all(*other)
```

**ধরন:** মেথড

recursive CTE-র সবচেয়ে প্রচলিত রূপ: anchor + recursive অংশ `UNION ALL` দিয়ে জোড়ে।

**উদাহরণ:**

```python
c = select(literal(10).label("n")).cte("c", recursive=True)
c = c.union_all(select(c.c.n - 3).where(c.c.n > 5))
print(session.execute(select(c.c.n)).scalars().all())   # [10, 7, 4] — ৭ > ৫ তাই আরেক ধাপ
```

### `CTE.unique_params()` { #cte-unique-params }

```python
CTE.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](#select-unique-params)-এর মতো।

### `CTE.uses_inspection` { #cte-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](#select-uses-inspection)-এর মতো।

### `CTE.with_cols()` { #cte-with-cols }

```python
CTE.with_cols(type_)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.with_cols`](#subquery-with-cols)-এর মতো।

## `values()` { #values }

```python
from sqlalchemy import values
```

```python
values(*columns, name=None, literal_binds=False)
```

**ধরন:** ফাংশন

Python ডেটা থেকে একটি অস্থায়ী টেবিলের মতো `VALUES (...), (...)` কনস্ট্রাক্ট বানায়, যাকে টেবিলের মতো join বা select করা যায়। অনেক মান দিয়ে একসাথে মেলানো/আপডেট করতে কাজে লাগে।

**উদাহরণ:**

```python
v = values(column("id", Integer), column("nick", String), name="nicks").data([(1, "রহি"), (2, "করি")])
stmt = select(User.name, v.c.nick).join(v, v.c.id == User.id).order_by(User.id)
print(session.execute(stmt).all())   # [('রহিম', 'রহি'), ('করিম', 'করি')]
```

## `Values` { #values }

```python
from sqlalchemy.sql.expression import Values
```

`values()` থেকে পাওয়া কনস্ট্রাক্ট। টেবিল/সাবকুয়েরির মতো আচরণ করে।

**উদাহরণ:**

```python
v = values(column("n", Integer), name="v").data([(1,), (2,)])
print(session.execute(select(v.c.n)).scalars().all())   # [1, 2]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #values-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_cte()`](#values-add-cte) | মেথড | স্টেটমেন্টের সাথে একটি বা একাধিক CTE স্পষ্টভাবে যুক্ত করে, মূল কুয়েরিতে সেটা ব্যবহার না হলেও। |
| [`alias()`](#values-alias) | মেথড | এই সাবকুয়েরির আরেকটি নামযুক্ত alias দেয়, যাতে একই সাবকুয়েরি একটি কুয়েরিতে দুবার ব্যবহার করা যায়। |
| [`allows_lambda`](#values-allows-lambda) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই ধরনের স্টেটমেন্ট `lambda_stmt()`-এর ভেতরে ব্যবহার করা যায় কি না। |
| [`c`](#values-c) | প্রপার্টি | সাবকুয়েরির কলামগুলো (`columns`-এর ছোট নাম)। |
| [`columns`](#values-columns) | প্রপার্টি | সাবকুয়েরির কলামের নাম-ভিত্তিক সংগ্রহ (`ColumnCollection`)। |
| [`compare()`](#values-compare) | মেথড | দুটি স্টেটমেন্টের গঠন হুবহু একই কি না তুলনা করে। |
| [`compile()`](#values-compile) | মেথড | স্টেটমেন্টকে SQL স্ট্রিংয়ে কম্পাইল করে। |
| [`corresponding_column()`](#values-corresponding-column) | মেথড | একটি মূল কলাম (যেমন `User.__table__.c.id`) দিলে এই স্টেটমেন্টের রপ্তানি করা কলামগুলোর মধ্যে সংশ্লিষ্টটি খুঁজে দেয়। |
| [`cte()`](#values-cte) | মেথড | এই SELECT-কে একটি CTE (`WITH নাম AS (...)`) বানায়। |
| [`data()`](#values-data) | মেথড | VALUES-এর রো-গুলো (tuple-এর তালিকা) দেয়, আর নতুন একটি `Values` ফেরত দেয়। |
| [`description`](#values-description) | প্রপার্টি | ভেতরের একটি বর্ণনামূলক নাম (লগ/ডিবাগিংয়ের জন্য)। |
| [`entity_namespace`](#values-entity-namespace) | প্রপার্টি | `filter_by()`-এর মতো নাম দিয়ে খোঁজার সময় কোন এন্টিটির নাম-ভান্ডার ব্যবহার হবে, তার ভেতরের হুক। |
| [`exported_columns`](#values-exported-columns) | প্রপার্টি | এই স্টেটমেন্ট যে কলামগুলো "রপ্তানি" করে (বাইরে থেকে পাওয়া যায়) তার সংগ্রহ। |
| [`foreign_keys`](#values-foreign-keys) | প্রপার্টি | এই সাবকুয়েরির কলামগুলো যেসব ফরেন কি রেফার করে তার সংগ্রহ (মূল টেবিল থেকে আসে)। |
| [`get_children()`](#values-get-children) | মেথড | এই এক্সপ্রেশন-গাছের সরাসরি "সন্তান" উপাদানগুলো দেয়। |
| [`inherit_cache`](#values-inherit-cache) | অ্যাট্রিবিউট | কাস্টম SQL কনস্ট্রাক্ট বানানোর সময় সাবক্লাস বেস ক্লাসের ক্যাশ-key ব্যবস্থা নেবে কি না তার ফ্ল্যাগ। |
| [`is_clause_element`](#values-is-clause-element) | অ্যাট্রিবিউট | ভেতরের টাইপ-ফ্ল্যাগ: এটি একটি SQL এক্সপ্রেশন উপাদান (`True`)। |
| [`is_derived_from()`](#values-is-derived-from) | মেথড | এই স্টেটমেন্ট একটি নির্দিষ্ট টেবিল/FROM থেকে তৈরি কি না দেখে। |
| [`is_dml`](#values-is-dml) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: INSERT/UPDATE/DELETE কি না (`Select`-এ `False`)। |
| [`is_selectable`](#values-is-selectable) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এটি একটি selectable (রো দেয় এমন) কনস্ট্রাক্ট। |
| [`join()`](#values-join) | মেথড | এই সাবকুয়েরি আর আরেকটি টেবিল/সাবকুয়েরির `Join` অবজেক্ট বানায় (টেবিলের `join()`-এর মতো), যা `select_from()`-এ বসানো যায়। |
| [`lateral()`](#values-lateral) | মেথড | VALUES-কে LATERAL হিসেবে চিহ্নিত করে, যাতে এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে। |
| [`memoized_attribute`](#values-memoized-attribute) | অ্যাট্রিবিউট | ভেতরের ডেকোরেটর (একবার হিসাব করে মনে রাখা প্রপার্টি)। |
| [`memoized_instancemethod()`](#values-memoized-instancemethod) | ক্লাস মেথড | ভেতরের ডেকোরেটর (মেথডের ফল মনে রাখা)। |
| [`name_cte_columns`](#values-name-cte-columns) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: CTE বানানোর সময় কলামের নামগুলো `WITH নাম(কলাম১, কলাম২)` আকারে লেখা হবে কি না (`values()`-এর মতো কনস্ট্রাক্টে লাগে)। |
| [`named_with_column`](#values-named-with-column) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: কলাম রেফার করার সময় এই FROM-এর নাম আগে বসবে কি না (`sub.col`)। |
| [`outerjoin()`](#values-outerjoin) | মেথড | `join()`-এর মতো, কিন্তু LEFT OUTER JOIN দিয়ে `Join` অবজেক্ট বানায়। |
| [`params()`](#values-params) | মেথড | `bindparam()` দিয়ে রাখা নামযুক্ত প্যারামিটারের মান বসিয়ে একটি কপি দেয়। |
| [`primary_key`](#values-primary-key) | প্রপার্টি | সাবকুয়েরির যে কলামগুলো মূল টেবিলের primary key থেকে এসেছে। |
| [`replace_selectable()`](#values-replace-selectable) | মেথড | ১.৪ থেকে বাতিলের পথে। |
| [`scalar_values()`](#values-scalar-values) | মেথড | এক কলামের VALUES-কে একটি scalar এক্সপ্রেশন বানায়, যেমন `IN (VALUES (1), (2))`-এ ব্যবহারের জন্য। |
| [`schema`](#values-schema) | অ্যাট্রিবিউট | `Table`-এর সাথে সামঞ্জস্যের জন্য; সাবকুয়েরিতে সবসময় `None`। |
| [`select()`](#values-select) | মেথড | এই সাবকুয়েরি থেকে সব কলামসহ একটি নতুন `SELECT * FROM (সাবকুয়েরি)` বানায়। |
| [`selectable`](#values-selectable) | প্রপার্টি | ভেতরের সামঞ্জস্য-প্রপার্টি; নিজেকেই দেয়। |
| [`self_group()`](#values-self-group) | মেথড | বড় এক্সপ্রেশনে বসানোর সময় প্রয়োজনমতো বন্ধনী (`( ... )`) দেয়। |
| [`stringify_dialect`](#values-stringify-dialect) | অ্যাট্রিবিউট | `str(stmt)` / `print(stmt)` করলে কোন ডায়ালেক্টে SQL দেখানো হবে (ডিফল্ট সাধারণ "default")। |
| [`supports_execution`](#values-supports-execution) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: এই কনস্ট্রাক্ট সরাসরি `execute()` করা যায় (`True`)। |
| [`table_valued()`](#values-table-valued) | মেথড | পুরো রো-কে একটি কলাম হিসেবে উপস্থাপন করে (PostgreSQL-এ রো-টিকে একটি record/composite মান হিসেবে)। |
| [`tablesample()`](#values-tablesample) | মেথড | `TABLESAMPLE` দিয়ে টেবিলের এলোমেলো নমুনা (শতাংশ হিসেবে) নেওয়ার alias বানায়। |
| [`unique_params()`](#values-unique-params) | মেথড | `params()`-এর মতো, কিন্তু প্যারামিটারগুলোর নাম অনন্য (unique) করে দেয়, যাতে একই স্টেটমেন্টের কয়েকটি কপি এক কুয়েরিতে মেলানো যায়। |
| [`uses_inspection`](#values-uses-inspection) | অ্যাট্রিবিউট | ভেতরের ফ্ল্যাগ: `inspect()` এই অবজেক্টে কাজ করে কি না। |
| [`with_cols()`](#values-with-cols) | মেথড | (২.১-এ নতুন) শুধু টাইপ চেকারের জন্য: এই FROM-কে একটি নির্দিষ্ট `TypedColumns` ক্লাসের কলাম আছে বলে ঘোষণা করে। |

### `Values.add_cte()` { #values-add-cte }

```python
Values.add_cte(*ctes, nest_here=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.add_cte`](#select-add-cte)-এর মতো।

### `Values.alias()` { #values-alias }

```python
Values.alias(name=None, flat=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.alias`](#subquery-alias)-এর মতো।

### `Values.allows_lambda` { #values-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.allows_lambda`](#select-allows-lambda)-এর মতো।

### `Values.c` { #values-c }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.c`](#subquery-c)-এর মতো।

### `Values.columns` { #values-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.columns`](#subquery-columns)-এর মতো।

### `Values.compare()` { #values-compare }

```python
Values.compare(other, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compare`](#select-compare)-এর মতো।

### `Values.compile()` { #values-compile }

```python
Values.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.compile`](#select-compile)-এর মতো।

### `Values.corresponding_column()` { #values-corresponding-column }

```python
Values.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.corresponding_column`](#select-corresponding-column)-এর মতো।

### `Values.cte()` { #values-cte }

```python
Values.cte(name=None, recursive=False, nesting=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.cte`](#select-cte)-এর মতো।

### `Values.data()` { #values-data }

```python
Values.data(values)
```

**ধরন:** মেথড

VALUES-এর রো-গুলো (tuple-এর তালিকা) দেয়, আর নতুন একটি `Values` ফেরত দেয়। একাধিকবার ডাকলে রো যোগ হয়।

**উদাহরণ:**

```python
v = values(column("n", Integer), name="v").data([(1,)]).data([(2,)])
print(session.execute(select(v.c.n)).scalars().all())   # [1, 2]
```

### `Values.description` { #values-description }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.description`](#select-description)-এর মতো।

### `Values.entity_namespace` { #values-entity-namespace }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.entity_namespace`](#select-entity-namespace)-এর মতো।

### `Values.exported_columns` { #values-exported-columns }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.exported_columns`](#select-exported-columns)-এর মতো।

### `Values.foreign_keys` { #values-foreign-keys }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.foreign_keys`](#subquery-foreign-keys)-এর মতো।

### `Values.get_children()` { #values-get-children }

```python
Values.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.get_children`](#select-get-children)-এর মতো।

### `Values.inherit_cache` { #values-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.inherit_cache`](#select-inherit-cache)-এর মতো।

### `Values.is_clause_element` { #values-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_clause_element`](#select-is-clause-element)-এর মতো।

### `Values.is_derived_from()` { #values-is-derived-from }

```python
Values.is_derived_from(fromclause)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.is_derived_from`](#select-is-derived-from)-এর মতো।

### `Values.is_dml` { #values-is-dml }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_dml`](#select-is-dml)-এর মতো।

### `Values.is_selectable` { #values-is-selectable }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.is_selectable`](#select-is-selectable)-এর মতো।

### `Values.join()` { #values-join }

```python
Values.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.join`](#subquery-join)-এর মতো।

### `Values.lateral()` { #values-lateral }

```python
Values.lateral(name=None)
```

**ধরন:** মেথড

VALUES-কে LATERAL হিসেবে চিহ্নিত করে, যাতে এটি বাম দিকের টেবিলের কলাম রেফার করতে পারে।

**উদাহরণ:**

```python
v = values(column("x", Integer), name="v").data([(1,)]).lateral()
print(type(v).__name__)   # Values
```

### `Values.memoized_attribute` { #values-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.memoized_attribute`](#select-memoized-attribute)-এর মতো।

### `Values.memoized_instancemethod()` { #values-memoized-instancemethod }

```python
Values.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

কাজ হুবহু [`Select.memoized_instancemethod`](#select-memoized-instancemethod)-এর মতো।

### `Values.name_cte_columns` { #values-name-cte-columns }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.name_cte_columns`](#select-name-cte-columns)-এর মতো।

### `Values.named_with_column` { #values-named-with-column }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Subquery.named_with_column`](#subquery-named-with-column)-এর মতো।

### `Values.outerjoin()` { #values-outerjoin }

```python
Values.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.outerjoin`](#subquery-outerjoin)-এর মতো।

### `Values.params()` { #values-params }

```python
Values.params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.params`](#select-params)-এর মতো।

### `Values.primary_key` { #values-primary-key }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Subquery.primary_key`](#subquery-primary-key)-এর মতো।

### `Values.replace_selectable()` { #values-replace-selectable }

```python
Values.replace_selectable(old, alias)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.replace_selectable`](#select-replace-selectable)-এর মতো।

### `Values.scalar_values()` { #values-scalar-values }

```python
Values.scalar_values()
```

**ধরন:** মেথড

এক কলামের VALUES-কে একটি scalar এক্সপ্রেশন বানায়, যেমন `IN (VALUES (1), (2))`-এ ব্যবহারের জন্য।

**উদাহরণ:**

```python
v = values(column("id", Integer), name="v").data([(1,), (3,)]).scalar_values()
print(sorted(session.scalars(select(User.name).where(User.id.in_(v))).all()))   # ['রহিম', 'সুমি']
```

### `Values.schema` { #values-schema }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Subquery.schema`](#subquery-schema)-এর মতো।

### `Values.select()` { #values-select }

```python
Values.select()
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.select`](#subquery-select)-এর মতো।

### `Values.selectable` { #values-selectable }

**ধরন:** প্রপার্টি

কাজ হুবহু [`Select.selectable`](#select-selectable)-এর মতো।

### `Values.self_group()` { #values-self-group }

```python
Values.self_group(against=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.self_group`](#select-self-group)-এর মতো।

### `Values.stringify_dialect` { #values-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.stringify_dialect`](#select-stringify-dialect)-এর মতো।

### `Values.supports_execution` { #values-supports-execution }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.supports_execution`](#select-supports-execution)-এর মতো।

### `Values.table_valued()` { #values-table-valued }

```python
Values.table_valued()
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.table_valued`](#subquery-table-valued)-এর মতো।

### `Values.tablesample()` { #values-tablesample }

```python
Values.tablesample(sampling, name=None, seed=None)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.tablesample`](#subquery-tablesample)-এর মতো।

### `Values.unique_params()` { #values-unique-params }

```python
Values.unique_params(**kwargs)
```

**ধরন:** মেথড

কাজ হুবহু [`Select.unique_params`](#select-unique-params)-এর মতো।

### `Values.uses_inspection` { #values-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

কাজ হুবহু [`Select.uses_inspection`](#select-uses-inspection)-এর মতো।

### `Values.with_cols()` { #values-with-cols }

```python
Values.with_cols(type_)
```

**ধরন:** মেথড

কাজ হুবহু [`Subquery.with_cols`](#subquery-with-cols)-এর মতো।

/// check | সংক্ষেপে মনে রাখুন

* `select()` অপরিবর্তনীয়: প্রতিটি মেথড নতুন স্টেটমেন্ট দেয়, তাই `stmt = stmt.where(...)`।
* ফিল্টার: `where()` / `filter_by()`; জোড়া: `join()` / `outerjoin()`; দল: `group_by()` + `having()`; ক্রম ও পেজ: `order_by()`, `limit()`, `offset()`, `slice()`।
* সাবকুয়েরি তিন রূপে: FROM-এ `subquery()`, একটি মান হিসেবে `scalar_subquery()`, শর্ত হিসেবে `exists()`; নাম দিয়ে আলাদা অংশ `cte()`।
* সেট-অপারেশন: `union()` / `union_all()` / `intersect()` / `except_()`।
* ২.১: `distinct(কলাম)` নয়, `.ext(distinct_on(কলাম))`; নতুন টেবিল বানাতে `into()`।

///
