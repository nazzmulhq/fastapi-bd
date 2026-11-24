# SQL এক্সপ্রেশন ক্লাস: ColumnElement, Exists, ScalarSelect, Label … { #api-elements }

/// note | এই পেজে যা আছে

[এক্সপ্রেশন ফাংশনগুলো](expressions.md) যে অবজেক্ট ফেরত দেয়, তাদের ক্লাস ও **সব** সদস্য:

* `ColumnElement`: সব কলাম-জাতীয় এক্সপ্রেশনের মূল ক্লাস (`label()`, `cast()`, `compile()`, `params()`, `type` …), আর তার আগের ধাপ `ClauseElement`।
* `Exists` আর `ScalarSelect`: সাবকুয়েরির নিজস্ব মেথড (`where()`, `correlate()`, `select()` …)।
* `BinaryExpression`, `BooleanClauseList`, `UnaryExpression`, `Label`, `BindParameter`, `ColumnClause`, `Tuple`, `Cast`, `TryCast`, `TypeCoerce`, `Case`, `Extract`, `Null`, `True_`, `False_`, `CollectionAggregate`।
* `StatementLambdaElement` ও `LambdaElement` (`lambda_stmt()`-এর ফল)।

///

এই ক্লাসগুলোর বেশিরভাগ সদস্য একই: সবাই `ColumnElement`, তাই কলামের সব অপারেটর (`==`, `in_()`, `like()` …) সবার ওপর চলে। প্রতিটি ক্লাসে শুধু **তার নিজস্ব** সদস্যের পূর্ণ ব্যাখ্যা আছে; বাকিগুলো একটি বক্সে মূল ব্যাখ্যার লিংকসহ তালিকা করা, যাতে কিছু বাদ না পড়ে আবার পেজও অকারণে লম্বা না হয়।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[এক্সপ্রেশন ফাংশন পেজের](expressions.md) মতোই `User` (`id`, `name`, `email`, `age`, `joined`) আর `Address` (`id`, `city`, `user_id`), একই তিনজন ইউজার: রহিম (৩০, দুটি ঠিকানা), করিম (২৫, email `NULL`), সুমি (age `NULL`)। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## `ColumnElement` { #columnelement }

```python
from sqlalchemy.sql.expression import ColumnElement
```

**যেকোনো কলাম-জাতীয় SQL এক্সপ্রেশনের মূল ক্লাস:** টেবিলের কলাম, `User.age + 1`, `func.count()`, `literal(5)`, `case(...)`, সাবকুয়েরি; যা কিছু SELECT-এর কলাম বা WHERE-এর অংশ হতে পারে। কলামের সব অপারেটর (`ColumnOperators`) এর ভেতরেই আছে। নিজের ফাংশনে "যেকোনো SQL এক্সপ্রেশন" নিতে টাইপ হিন্ট হিসেবে `ColumnElement[bool]`, `ColumnElement[int]` লেখা হয়।

**উদাহরণ:**

```python
expr = (User.age + 1).label("next_age")
print(isinstance(expr, ColumnElement), expr.type)   # True INTEGER
print(rows(select(expr).where(User.id == 2)))       # [(26,)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columnelement-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`allows_lambda`](#columnelement-allows-lambda) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: এই এক্সপ্রেশন `lambda_stmt()`-এর ভেতরে ব্যবহারযোগ্য কি না। |
| [`anon_key_label`](#columnelement-anon-key-label) | প্রপার্টি ⚠️ deprecated | ১.৪ থেকে বাতিলের পথে (এখন ভেতরের, প্রাইভেট)। |
| [`anon_label`](#columnelement-anon-label) | প্রপার্টি ⚠️ deprecated | ১.৪ থেকে বাতিলের পথে। |
| [`base_columns`](#columnelement-base-columns) | প্রপার্টি | এই এক্সপ্রেশন যে মূল টেবিল-কলামগুলো থেকে এসেছে (alias/সাবকুয়েরির ভেতর দিয়ে গেলে মূলগুলো) তার সেট। |
| [`cast()`](#columnelement-cast) | মেথড | `CAST(এক্সপ্রেশন AS টাইপ)`; `cast()` ফাংশনের মেথড রূপ। |
| [`comparator`](#columnelement-comparator) | প্রপার্টি (internal) | টাইপ-নির্দিষ্ট অপারেটরগুলো যে `Comparator` অবজেক্টে থাকে (যেমন JSON টাইপে `[]`, ARRAY-তে `contains`)। |
| [`compare()`](#columnelement-compare) | মেথড | দুটি এক্সপ্রেশন **গঠনে** একই কি না (একই কলাম, একই অপারেটর, একই মান) যাচাই করে। |
| [`compile()`](#columnelement-compile) | মেথড | এক্সপ্রেশন/স্টেটমেন্টকে একটি নির্দিষ্ট ডেটাবেসের SQL-এ কম্পাইল করে (`Compiled` অবজেক্ট; `str()` করলে SQL)। |
| [`description`](#columnelement-description) | প্রপার্টি | এক্সপ্রেশনের ছোট বর্ণনামূলক নাম (কলামের ক্ষেত্রে কলামের নাম)। |
| [`entity_namespace`](#columnelement-entity-namespace) | প্রপার্টি (internal) | `filter_by()`-এ নাম দিয়ে অ্যাট্রিবিউট খোঁজার নাম-ভান্ডার। |
| [`expression`](#columnelement-expression) | প্রপার্টি | কলাম-এক্সপ্রেশন রূপটি ফেরত দেয় (এখানে নিজেকেই)। |
| [`foreign_keys`](#columnelement-foreign-keys) | অ্যাট্রিবিউট | এই কলামের `ForeignKey`-গুলোর সেট (সাধারণ এক্সপ্রেশনে খালি)। |
| [`get_children()`](#columnelement-get-children) | মেথড (internal) | এক্সপ্রেশন-গাছের সরাসরি সন্তান এলিমেন্টগুলো দেয় (traversal/visitor-এর জন্য)। |
| [`inherit_cache`](#columnelement-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ব্যবস্থার ফ্ল্যাগ। |
| [`is_clause_element`](#columnelement-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ: এটি একটি SQL এলিমেন্ট (`True`)। |
| [`is_dml`](#columnelement-is-dml) | অ্যাট্রিবিউট | এটি INSERT/UPDATE/DELETE স্টেটমেন্ট কি না (এক্সপ্রেশনে `False`)। |
| [`is_selectable`](#columnelement-is-selectable) | অ্যাট্রিবিউট | এটি একটি FROM-যোগ্য selectable (টেবিল, সাবকুয়েরি) কি না; কলাম-এক্সপ্রেশনে `False`। |
| [`key`](#columnelement-key) | অ্যাট্রিবিউট | এক্সপ্রেশনের key: কলামে কলামের নাম, লেবেলে লেবেলের নাম, অন্যগুলোতে সাধারণত `None`। |
| [`label()`](#columnelement-label) | মেথড | এক্সপ্রেশনকে নাম দেয় (`AS নাম`); রো-তে সেই নামে পাওয়া যায়। |
| [`memoized_attribute`](#columnelement-memoized-attribute) | অ্যাট্রিবিউট (internal) | ভেতরের ডেকোরেটর। |
| [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) | ক্লাস মেথড (internal) | ভেতরের ডেকোরেটর। |
| [`params()`](#columnelement-params) | মেথড | এক্সপ্রেশনের ভেতরের `bindparam()`-গুলোর মান বসিয়ে একটি **কপি** দেয়। |
| [`primary_key`](#columnelement-primary-key) | অ্যাট্রিবিউট | এটি primary key কলাম কি না। |
| [`proxy_set`](#columnelement-proxy-set) | প্রপার্টি (internal) | এই কলাম যে কলামগুলোর "প্রক্সি" (alias/সাবকুয়েরির মাধ্যমে) তাদের সেট; কলাম মিলানোয় ব্যবহার হয়। |
| [`self_group()`](#columnelement-self-group) | মেথড | প্রয়োজনে এক্সপ্রেশনকে বন্ধনীতে মোড়ায়, যাতে বড় এক্সপ্রেশনের ভেতরে অগ্রাধিকার ঠিক থাকে। |
| [`shares_lineage()`](#columnelement-shares-lineage) | মেথড | অন্য একটি কলামের সাথে এর মূল (ancestor) একই কি না: যেমন সাবকুয়েরির কলাম আর মূল টেবিলের কলাম। |
| [`stringify_dialect`](#columnelement-stringify-dialect) | অ্যাট্রিবিউট (internal) | `str(এক্সপ্রেশন)` করার সময় কোন ডায়ালেক্ট ব্যবহার হবে (সাধারণত `"default"`)। |
| [`supports_execution`](#columnelement-supports-execution) | অ্যাট্রিবিউট | এটি নিজে সরাসরি `execute()` করা যায় কি না (এক্সপ্রেশনে `False`; `select()`-এ `True`)। |
| [`type`](#columnelement-type) | প্রপার্টি | এক্সপ্রেশনের SQL টাইপ (`Integer`, `String` …)। |
| [`unique_params()`](#columnelement-unique-params) | মেথড | `params()`-এর মতো, কিন্তু bindparam-গুলোর নাম অনন্য করে দেয়, যাতে একই এক্সপ্রেশন একটি স্টেটমেন্টে দুবার ভিন্ন মানে ব্যবহার করা যায়। |
| [`uses_inspection`](#columnelement-uses-inspection) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `ColumnElement.allows_lambda` { #columnelement-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: এই এক্সপ্রেশন `lambda_stmt()`-এর ভেতরে ব্যবহারযোগ্য কি না।

### `ColumnElement.anon_key_label` { #columnelement-anon-key-label }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪ থেকে বাতিলের পথে (এখন ভেতরের, প্রাইভেট)। নাম ছাড়া এক্সপ্রেশনের জন্য SQLAlchemy-র বানানো বেনামি key-লেবেল। নিজের নাম চাইলে `label()` দিন।

### `ColumnElement.anon_label` { #columnelement-anon-label }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

১.৪ থেকে বাতিলের পথে। নাম ছাড়া এক্সপ্রেশনের বেনামি লেবেল (`anon_1` ধরনের)। বিকল্প: `label()`।

### `ColumnElement.base_columns` { #columnelement-base-columns }

**ধরন:** প্রপার্টি

এই এক্সপ্রেশন যে মূল টেবিল-কলামগুলো থেকে এসেছে (alias/সাবকুয়েরির ভেতর দিয়ে গেলে মূলগুলো) তার সেট।

**উদাহরণ:**

```python
sub = select(User.id, User.name).subquery()
print([c.table.name for c in sub.c.name.base_columns])   # ['users']
```

### `ColumnElement.cast()` { #columnelement-cast }

```python
ColumnElement.cast(type_)
```

**ধরন:** মেথড

`CAST(এক্সপ্রেশন AS টাইপ)`; `cast()` ফাংশনের মেথড রূপ।

**উদাহরণ:**

```python
print(User.age.cast(String))   # CAST(users.age AS VARCHAR)
```

### `ColumnElement.comparator` { #columnelement-comparator }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপ-নির্দিষ্ট অপারেটরগুলো যে `Comparator` অবজেক্টে থাকে (যেমন JSON টাইপে `[]`, ARRAY-তে `contains`)। কাস্টম টাইপে `comparator_factory` দিয়ে বদলানো যায়।

### `ColumnElement.compare()` { #columnelement-compare }

```python
ColumnElement.compare(other, **kw)
```

**ধরন:** মেথড

দুটি এক্সপ্রেশন **গঠনে** একই কি না (একই কলাম, একই অপারেটর, একই মান) যাচাই করে। টেস্টে "ঠিক এই শর্তটাই বানানো হয়েছে কি না" দেখতে কাজে লাগে।

**উদাহরণ:**

```python
print((User.age > 5).compare(User.age > 5))   # True
print((User.age > 5).compare(User.age > 6))   # False
```

### `ColumnElement.compile()` { #columnelement-compile }

```python
ColumnElement.compile(bind=None, dialect=None, **kw)
```

**ধরন:** মেথড

এক্সপ্রেশন/স্টেটমেন্টকে একটি নির্দিষ্ট ডেটাবেসের SQL-এ কম্পাইল করে (`Compiled` অবজেক্ট; `str()` করলে SQL)। `dialect=` দিয়ে ডেটাবেস, আর `compile_kwargs={"literal_binds": True}` দিয়ে মানগুলো সরাসরি বসানো যায় (শুধু দেখা/লগের জন্য, চালানোর জন্য নয়)।

**উদাহরণ:**

```python
c = (User.name == "রহিম").compile(dialect=postgresql.dialect())
print(c, c.params)   # users.name = %(name_1)s::VARCHAR {'name_1': 'রহিম'}
print((User.age > 5).compile(compile_kwargs={"literal_binds": True}))   # users.age > 5
```

### `ColumnElement.description` { #columnelement-description }

**ধরন:** প্রপার্টি

এক্সপ্রেশনের ছোট বর্ণনামূলক নাম (কলামের ক্ষেত্রে কলামের নাম)।

**উদাহরণ:**

```python
print(User.__table__.c.email.description)   # email
```

### `ColumnElement.entity_namespace` { #columnelement-entity-namespace }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`filter_by()`-এ নাম দিয়ে অ্যাট্রিবিউট খোঁজার নাম-ভান্ডার।

### `ColumnElement.expression` { #columnelement-expression }

**ধরন:** প্রপার্টি

কলাম-এক্সপ্রেশন রূপটি ফেরত দেয় (এখানে নিজেকেই)। ORM অ্যাট্রিবিউট আর Core কলামে একই কোড লিখতে কাজে লাগে।

**উদাহরণ:**

```python
e = User.age + 1
print(e.expression is e)   # True
```

### `ColumnElement.foreign_keys` { #columnelement-foreign-keys }

**ধরন:** অ্যাট্রিবিউট

এই কলামের `ForeignKey`-গুলোর সেট (সাধারণ এক্সপ্রেশনে খালি)।

**উদাহরণ:**

```python
print([fk.target_fullname for fk in Address.__table__.c.user_id.foreign_keys])   # ['users.id']
```

### `ColumnElement.get_children()` { #columnelement-get-children }

```python
ColumnElement.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এক্সপ্রেশন-গাছের সরাসরি সন্তান এলিমেন্টগুলো দেয় (traversal/visitor-এর জন্য)।

### `ColumnElement.inherit_cache` { #columnelement-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ব্যবস্থার ফ্ল্যাগ। নিজের `ColumnElement` সাবক্লাস বানালে `inherit_cache = True` দিন, যাতে স্টেটমেন্ট ক্যাশ হয়।

### `ColumnElement.is_clause_element` { #columnelement-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ: এটি একটি SQL এলিমেন্ট (`True`)।

### `ColumnElement.is_dml` { #columnelement-is-dml }

**ধরন:** অ্যাট্রিবিউট

এটি INSERT/UPDATE/DELETE স্টেটমেন্ট কি না (এক্সপ্রেশনে `False`)।

**উদাহরণ:**

```python
print((User.age > 1).is_dml)   # False
```

### `ColumnElement.is_selectable` { #columnelement-is-selectable }

**ধরন:** অ্যাট্রিবিউট

এটি একটি FROM-যোগ্য selectable (টেবিল, সাবকুয়েরি) কি না; কলাম-এক্সপ্রেশনে `False`।

**উদাহরণ:**

```python
print(User.__table__.c.id.is_selectable, User.__table__.is_selectable)   # False True
```

### `ColumnElement.key` { #columnelement-key }

**ধরন:** অ্যাট্রিবিউট

এক্সপ্রেশনের key: কলামে কলামের নাম, লেবেলে লেবেলের নাম, অন্যগুলোতে সাধারণত `None`। রেজাল্টের রো-তে কোন নামে পাওয়া যাবে তা এখান থেকে আসে।

**উদাহরণ:**

```python
print(User.__table__.c.name.key, (User.age + 1).label("x").key)   # name x
```

### `ColumnElement.label()` { #columnelement-label }

```python
ColumnElement.label(name)
```

**ধরন:** মেথড

এক্সপ্রেশনকে নাম দেয় (`AS নাম`); রো-তে সেই নামে পাওয়া যায়।

**উদাহরণ:**

```python
row = session.execute(select(func.upper(User.name).label("big")).where(User.id == 3)).one()
print(row.big)   # সুমি
```

### `ColumnElement.memoized_attribute` { #columnelement-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `ColumnElement.memoized_instancemethod()` { #columnelement-memoized-instancemethod }

```python
ColumnElement.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `ColumnElement.params()` { #columnelement-params }

```python
ColumnElement.params(**kwargs)
```

**ধরন:** মেথড

এক্সপ্রেশনের ভেতরের `bindparam()`-গুলোর মান বসিয়ে একটি **কপি** দেয়।

**উদাহরণ:**

```python
cond = User.age > bindparam("a")
print(names(cond.params(a=26)))   # ['রহিম']
```

### `ColumnElement.primary_key` { #columnelement-primary-key }

**ধরন:** অ্যাট্রিবিউট

এটি primary key কলাম কি না।

**উদাহরণ:**

```python
print(User.__table__.c.id.primary_key, User.__table__.c.name.primary_key)   # True False
```

### `ColumnElement.proxy_set` { #columnelement-proxy-set }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই কলাম যে কলামগুলোর "প্রক্সি" (alias/সাবকুয়েরির মাধ্যমে) তাদের সেট; কলাম মিলানোয় ব্যবহার হয়।

### `ColumnElement.self_group()` { #columnelement-self-group }

```python
ColumnElement.self_group(against=None)
```

**ধরন:** মেথড

প্রয়োজনে এক্সপ্রেশনকে বন্ধনীতে মোড়ায়, যাতে বড় এক্সপ্রেশনের ভেতরে অগ্রাধিকার ঠিক থাকে। SQLAlchemy নিজে ডাকে; কাস্টম এক্সপ্রেশন বানালে কাজে লাগে।

**উদাহরণ:**

```python
print(or_(User.id == 1, User.id == 2).self_group())   # (users.id = :id_1 OR users.id = :id_2)
```

### `ColumnElement.shares_lineage()` { #columnelement-shares-lineage }

```python
ColumnElement.shares_lineage(othercolumn)
```

**ধরন:** মেথড

অন্য একটি কলামের সাথে এর মূল (ancestor) একই কি না: যেমন সাবকুয়েরির কলাম আর মূল টেবিলের কলাম।

**উদাহরণ:**

```python
sub = select(User.name).subquery()
print(sub.c.name.shares_lineage(User.__table__.c.name))   # True
```

### `ColumnElement.stringify_dialect` { #columnelement-stringify-dialect }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`str(এক্সপ্রেশন)` করার সময় কোন ডায়ালেক্ট ব্যবহার হবে (সাধারণত `"default"`)।

### `ColumnElement.supports_execution` { #columnelement-supports-execution }

**ধরন:** অ্যাট্রিবিউট

এটি নিজে সরাসরি `execute()` করা যায় কি না (এক্সপ্রেশনে `False`; `select()`-এ `True`)।

**উদাহরণ:**

```python
print((User.age > 1).supports_execution, select(User).supports_execution)   # False True
```

### `ColumnElement.type` { #columnelement-type }

**ধরন:** প্রপার্টি

এক্সপ্রেশনের SQL টাইপ (`Integer`, `String` …)। অপারেটরের ফল আর রেজাল্ট রূপান্তর এর ওপর নির্ভর করে।

**উদাহরণ:**

```python
print(User.age.type, (User.age > 1).type, func.count().type)   # INTEGER BOOLEAN INTEGER
```

### `ColumnElement.unique_params()` { #columnelement-unique-params }

```python
ColumnElement.unique_params(**kwargs)
```

**ধরন:** মেথড

`params()`-এর মতো, কিন্তু bindparam-গুলোর নাম অনন্য করে দেয়, যাতে একই এক্সপ্রেশন একটি স্টেটমেন্টে দুবার ভিন্ন মানে ব্যবহার করা যায়।

**উদাহরণ:**

```python
cond = User.age == bindparam("a")
print(names(or_(cond.unique_params(a=25), cond.unique_params(a=30))))   # ['রহিম', 'করিম']
```

### `ColumnElement.uses_inspection` { #columnelement-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ।

## `ClauseElement` { #clauseelement }

```python
from sqlalchemy.sql.expression import ClauseElement
```

**সব** SQL এলিমেন্টের মূল ক্লাস: কলাম-এক্সপ্রেশন, স্টেটমেন্ট (`Select`, `Insert`), টেবিল, JOIN সবই। এর সদস্যগুলো (`compile()`, `params()`, `compare()` …) সব SQL অবজেক্টে আছে; ব্যাখ্যা `ColumnElement`-এর অংশে।

**উদাহরণ:**

```python
print(all(isinstance(x, ClauseElement) for x in [User.__table__, select(User), User.age > 1]))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #clauseelement-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ClauseElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`self_group()`](#columnelement-self-group) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`unique_params()`](#columnelement-unique-params)

///

## সাবকুয়েরি এক্সপ্রেশন { #exists-group }

## `Exists` { #exists }

```python
from sqlalchemy.sql.expression import Exists
```

`exists()` বা `select(...).exists()`-এর ফল: `EXISTS (SELECT ...)`। বুলিয়ান এক্সপ্রেশন, তাই `where()`-এ বা `~` দিয়ে উল্টে ব্যবহার হয়। ভেতরের SELECT বদলানোর নিজস্ব মেথড আছে।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id)
print(type(e).__name__, names(e))   # Exists ['রহিম', 'সুমি']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #exists-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`correlate()`](#exists-correlate) | মেথড | ভেতরের SELECT কোন বাইরের টেবিলের সাথে correlate হবে তা স্পষ্ট করে দেয় (সাধারণত নিজে থেকেই ঠিক হয়)। |
| [`correlate_except()`](#exists-correlate-except) | মেথড | দেওয়া টেবিল ছাড়া বাকি সব বাইরের টেবিলের সাথে correlate করে; দেওয়া টেবিলটি ভেতরের FROM-এ থাকে। |
| [`select()`](#exists-select) | মেথড | এই EXISTS-কে একটি পূর্ণ `SELECT EXISTS (...)` স্টেটমেন্ট বানায়, যা চালালে `True`/`False` আসে। |
| [`select_from()`](#exists-select-from) | মেথড | ভেতরের SELECT-এর FROM স্পষ্ট করে দেয়। |
| [`where()`](#exists-where) | মেথড | ভেতরের SELECT-এ WHERE শর্ত যোগ করে (আগের শর্তের সাথে AND)। |
| [`with_hint()`](#exists-with-hint) | মেথড | ভেতরের SELECT-এ ডেটাবেস-নির্দিষ্ট টেবিল hint যোগ করে (যেমন MySQL `USE INDEX`; PostgreSQL hint সমর্থন করে না, সেখানে উপেক্ষিত)। |
| [`with_statement_hint()`](#exists-with-statement-hint) | মেথড | ভেতরের SELECT-এ স্টেটমেন্ট-স্তরের hint যোগ করে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Exists`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `Exists.correlate()` { #exists-correlate }

```python
Exists.correlate(*fromclauses)
```

**ধরন:** মেথড

ভেতরের SELECT কোন বাইরের টেবিলের সাথে correlate হবে তা স্পষ্ট করে দেয় (সাধারণত নিজে থেকেই ঠিক হয়)।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id).correlate(User)
print(names(e))   # ['রহিম', 'সুমি']
```

### `Exists.correlate_except()` { #exists-correlate-except }

```python
Exists.correlate_except(*fromclauses)
```

**ধরন:** মেথড

দেওয়া টেবিল ছাড়া বাকি সব বাইরের টেবিলের সাথে correlate করে; দেওয়া টেবিলটি ভেতরের FROM-এ থাকে।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id).correlate_except(Address)
print(names(e))   # ['রহিম', 'সুমি']
```

### `Exists.select()` { #exists-select }

```python
Exists.select()
```

**ধরন:** মেথড

এই EXISTS-কে একটি পূর্ণ `SELECT EXISTS (...)` স্টেটমেন্ট বানায়, যা চালালে `True`/`False` আসে।

**উদাহরণ:**

```python
print(session.scalar(exists().where(User.age > 28).select()))   # True
```

### `Exists.select_from()` { #exists-select-from }

```python
Exists.select_from(*froms)
```

**ধরন:** মেথড

ভেতরের SELECT-এর FROM স্পষ্ট করে দেয়।

**উদাহরণ:**

```python
e = exists().select_from(Address).where(Address.city == "সিলেট")
print(session.scalar(e.select()))   # False
```

### `Exists.where()` { #exists-where }

```python
Exists.where(*clause)
```

**ধরন:** মেথড

ভেতরের SELECT-এ WHERE শর্ত যোগ করে (আগের শর্তের সাথে AND)।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id).where(Address.city == "চট্টগ্রাম")
print(names(e))   # ['রহিম']
```

### `Exists.with_hint()` { #exists-with-hint }

```python
Exists.with_hint(selectable, text, dialect_name='*')
```

**ধরন:** মেথড

ভেতরের SELECT-এ ডেটাবেস-নির্দিষ্ট টেবিল hint যোগ করে (যেমন MySQL `USE INDEX`; PostgreSQL hint সমর্থন করে না, সেখানে উপেক্ষিত)।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id).with_hint(Address, "USE INDEX (ix_user)", "mysql")
print(names(e))   # ['রহিম', 'সুমি']
```

### `Exists.with_statement_hint()` { #exists-with-statement-hint }

```python
Exists.with_statement_hint(text, dialect_name='*')
```

**ধরন:** মেথড

ভেতরের SELECT-এ স্টেটমেন্ট-স্তরের hint যোগ করে।

**উদাহরণ:**

```python
e = exists().where(Address.user_id == User.id).with_statement_hint("/*+ NO_INDEX */", "oracle")
print(names(e))   # ['রহিম', 'সুমি']
```

## `ScalarSelect` { #scalarselect }

```python
from sqlalchemy.sql.expression import ScalarSelect
```

`select(...).scalar_subquery()`-এর ফল: এমন সাবকুয়েরি যা **একটি মান** দেয়, তাই কলামের মতো SELECT-এ বা তুলনায় বসানো যায়। বাইরের টেবিলের সাথে নিজে থেকে correlate হয় ("প্রতিটি ইউজারের ঠিকানা-সংখ্যা")।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
print(type(n).__name__, rows(select(User.name, n).order_by(User.id)))   # ScalarSelect [('রহিম', 2), ('করিম', 0), ('সুমি', 1)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #scalarselect-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`c`](#scalarselect-c) | প্রপার্টি | ScalarSelect-এর কোনো কলাম-সংগ্রহ নেই: পড়তে গেলেই `InvalidRequestError` দেয়, যাতে ভুল ব্যবহার সাথে সাথে ধরা পড়ে। |
| [`columns`](#scalarselect-columns) | প্রপার্টি | `c`-এর মতো: পড়তে গেলেই `InvalidRequestError`। |
| [`correlate()`](#scalarselect-correlate) | মেথড | কোন বাইরের টেবিলের সাথে correlate হবে তা স্পষ্ট করে। |
| [`correlate_except()`](#scalarselect-correlate-except) | মেথড | দেওয়া টেবিল ছাড়া বাকিগুলোর সাথে correlate করে। |
| [`where()`](#scalarselect-where) | মেথড | ভেতরের SELECT-এ শর্ত যোগ করে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ScalarSelect`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `ScalarSelect.c` { #scalarselect-c }

**ধরন:** প্রপার্টি

ScalarSelect-এর কোনো কলাম-সংগ্রহ নেই: পড়তে গেলেই `InvalidRequestError` দেয়, যাতে ভুল ব্যবহার সাথে সাথে ধরা পড়ে। কলামসহ সাবকুয়েরি চাইলে `scalar_subquery()`-এর বদলে `.subquery()` ব্যবহার করুন।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).scalar_subquery()
try:
    n.c
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError
```

### `ScalarSelect.columns` { #scalarselect-columns }

**ধরন:** প্রপার্টি

`c`-এর মতো: পড়তে গেলেই `InvalidRequestError`।

**উদাহরণ:**

```python
try:
    select(User.id).scalar_subquery().columns
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError
```

### `ScalarSelect.correlate()` { #scalarselect-correlate }

```python
ScalarSelect.correlate(*fromclauses)
```

**ধরন:** মেথড

কোন বাইরের টেবিলের সাথে correlate হবে তা স্পষ্ট করে।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery().correlate(User)
print(session.scalars(select(n).select_from(User).order_by(User.id)).all())   # [2, 0, 1]
```

### `ScalarSelect.correlate_except()` { #scalarselect-correlate-except }

```python
ScalarSelect.correlate_except(*fromclauses)
```

**ধরন:** মেথড

দেওয়া টেবিল ছাড়া বাকিগুলোর সাথে correlate করে।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery().correlate_except(Address)
print(session.scalars(select(n).select_from(User).order_by(User.id)).all())   # [2, 0, 1]
```

### `ScalarSelect.where()` { #scalarselect-where }

```python
ScalarSelect.where(crit)
```

**ধরন:** মেথড

ভেতরের SELECT-এ শর্ত যোগ করে।

**উদাহরণ:**

```python
n = select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
print(session.scalars(select(n.where(Address.city == "ঢাকা")).select_from(User).order_by(User.id)).all())   # [1, 0, 1]
```

## এক্সপ্রেশনের ধরন { #binaryexpression-group }

## `BinaryExpression` { #binaryexpression }

```python
from sqlalchemy.sql.expression import BinaryExpression
```

দুই পাশের এক্সপ্রেশন আর মাঝে অপারেটর: `User.age > 5`, `a + b`, `name LIKE x`। বাম দিক `.left`, ডান দিক `.right`, অপারেটর `.operator`।

**উদাহরণ:**

```python
e = User.age > 5
print(type(e).__name__, e.left, e.operator.__name__, e.right.value)   # BinaryExpression users.age gt 5
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #binaryexpression-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`group`](#binaryexpression-group) | অ্যাট্রিবিউট (internal) | বড় এক্সপ্রেশনের ভেতরে বসলে বন্ধনী লাগবে কি না তার ফ্ল্যাগ। |
| [`is_comparison`](#binaryexpression-is-comparison) | প্রপার্টি | অপারেটরটি তুলনা (`=`, `>`, `LIKE` …) কি না, অর্থাৎ ফল বুলিয়ান কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `BinaryExpression`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `BinaryExpression.group` { #binaryexpression-group }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বড় এক্সপ্রেশনের ভেতরে বসলে বন্ধনী লাগবে কি না তার ফ্ল্যাগ।

### `BinaryExpression.is_comparison` { #binaryexpression-is-comparison }

**ধরন:** প্রপার্টি

অপারেটরটি তুলনা (`=`, `>`, `LIKE` …) কি না, অর্থাৎ ফল বুলিয়ান কি না।

**উদাহরণ:**

```python
print((User.age > 5).is_comparison, (User.age + 5).is_comparison)   # True False
```

## `BooleanClauseList` { #booleanclauselist }

```python
from sqlalchemy.sql.expression import BooleanClauseList
```

`and_()` / `or_()`-এর ফল: কয়েকটি শর্ত AND বা OR দিয়ে জোড়া। `.clauses`-এ শর্তগুলো থাকে।

**উদাহরণ:**

```python
e = and_(User.age > 20, User.name != "করিম")
print(type(e).__name__, len(e.clauses))   # BooleanClauseList 2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #booleanclauselist-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`and_()`](#booleanclauselist-and-) | ক্লাস মেথড | (ক্লাস মেথড) `and_()` ফাংশনের মূল রূপ। |
| [`group`](#booleanclauselist-group) | অ্যাট্রিবিউট (internal) | বন্ধনী লাগবে কি না তার ফ্ল্যাগ। |
| [`is_comparison`](#booleanclauselist-is-comparison) | প্রপার্টি | এটি বুলিয়ান তুলনা হিসেবে গণ্য কি না। |
| [`or_()`](#booleanclauselist-or-) | ক্লাস মেথড | (ক্লাস মেথড) `or_()` ফাংশনের মূল রূপ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `BooleanClauseList`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `BooleanClauseList.and_()` { #booleanclauselist-and- }

```python
BooleanClauseList.and_(initial_clause=_NoArg.NO_ARG, *clauses)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) `and_()` ফাংশনের মূল রূপ।

**উদাহরণ:**

```python
print(names(BooleanClauseList.and_(User.age > 20, User.age < 28)))   # ['করিম']
```

### `BooleanClauseList.group` { #booleanclauselist-group }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বন্ধনী লাগবে কি না তার ফ্ল্যাগ।

### `BooleanClauseList.is_comparison` { #booleanclauselist-is-comparison }

**ধরন:** প্রপার্টি

এটি বুলিয়ান তুলনা হিসেবে গণ্য কি না।

**উদাহরণ:**

```python
print(and_(User.age > 1, User.id > 1).is_comparison)   # False
```

### `BooleanClauseList.or_()` { #booleanclauselist-or- }

```python
BooleanClauseList.or_(initial_clause=_NoArg.NO_ARG, *clauses)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) `or_()` ফাংশনের মূল রূপ।

**উদাহরণ:**

```python
print(names(BooleanClauseList.or_(User.id == 1, User.id == 3)))   # ['রহিম', 'সুমি']
```

## `UnaryExpression` { #unaryexpression }

```python
from sqlalchemy.sql.expression import UnaryExpression
```

এক পাশের এক্সপ্রেশন আর একটি অপারেটর/সংশোধক: `desc(x)`, `x.asc()`, `x.nulls_last()`, `distinct(x)`, `bitwise_not(x)`। নিজস্ব কোনো নতুন সদস্য নেই।

**উদাহরণ:**

```python
print(type(User.age.desc()).__name__, User.age.desc())   # UnaryExpression users.age DESC
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #unaryexpression-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `UnaryExpression`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `Label` { #label }

```python
from sqlalchemy.sql.expression import Label
```

`expr.label("নাম")`-এর ফল: `expr AS নাম`।

**উদাহরণ:**

```python
lb = func.count(Address.id).label("n")
print(type(lb).__name__, lb.name)   # Label n
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #label-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_reference()`](#label-as-reference) | মেথড | GROUP BY / ORDER BY-তে পুরো এক্সপ্রেশন আবার না লিখে শুধু লেবেলের নাম বসায়। |
| [`element`](#label-element) | প্রপার্টি | লেবেলের ভেতরের মূল এক্সপ্রেশন। |
| [`is_literal`](#label-is-literal) | অ্যাট্রিবিউট (internal) | লেবেলটি কাঁচা লেখা হিসেবে বসবে কি না (ভেতরের ফ্ল্যাগ)। |
| [`table`](#label-table) | অ্যাট্রিবিউট (internal) | লেবেলের ক্ষেত্রে সাধারণত `None` (কোনো টেবিলের নিজস্ব কলাম নয়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Label`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `Label.as_reference()` { #label-as-reference }

```python
Label.as_reference()
```

**ধরন:** মেথড

GROUP BY / ORDER BY-তে পুরো এক্সপ্রেশন আবার না লিখে শুধু লেবেলের নাম বসায়।

**উদাহরণ:**

```python
n = func.count(Address.id).label("n")
stmt = select(Address.city, n).group_by(Address.city).order_by(n.as_reference().desc())
print(stmt.compile().string.splitlines()[-1])   # FROM addresses GROUP BY addresses.city ORDER BY n DESC
print(rows(stmt))                               # [('ঢাকা', 2), ('চট্টগ্রাম', 1)]
```

### `Label.element` { #label-element }

**ধরন:** প্রপার্টি

লেবেলের ভেতরের মূল এক্সপ্রেশন।

**উদাহরণ:**

```python
print((User.age + 1).label("x").element)   # users.age + :age_1
```

### `Label.is_literal` { #label-is-literal }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লেবেলটি কাঁচা লেখা হিসেবে বসবে কি না (ভেতরের ফ্ল্যাগ)।

### `Label.table` { #label-table }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লেবেলের ক্ষেত্রে সাধারণত `None` (কোনো টেবিলের নিজস্ব কলাম নয়)।

## `BindParameter` { #bindparameter }

```python
from sqlalchemy.sql.expression import BindParameter
```

একটি bound parameter (`:name_1`): `bindparam()` থেকে, বা আপনি যখন `User.name == "রহিম"`-এ Python মান দেন তখন নিজে থেকেই তৈরি হয় (তখন নামটি "বেনামি", কম্পাইলের সময় `name_1`-এর মতো নাম পায়)। মান থাকে `.value`-তে, নাম `.key`-তে।

**উদাহরণ:**

```python
p = bindparam("uname", "রহিম")
print(type(p).__name__, p.key, p.value)   # BindParameter uname রহিম
auto = (User.name == "রহিম").right
print(type(auto).__name__, auto.value)    # BindParameter রহিম
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bindparameter-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`effective_value`](#bindparameter-effective-value) | প্রপার্টি | প্যারামিটারের প্রকৃত মান: `callable_` দেওয়া থাকলে সেটি ডেকে পাওয়া মান, না হলে `value`। |
| [`render_literal_execute()`](#bindparameter-render-literal-execute) | মেথড | এই প্যারামিটারের এমন কপি দেয় যার মান চালানোর মুহূর্তে SQL-এ সরাসরি বসবে (প্যারামিটার হিসেবে নয়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `BindParameter`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `BindParameter.effective_value` { #bindparameter-effective-value }

**ধরন:** প্রপার্টি

প্যারামিটারের প্রকৃত মান: `callable_` দেওয়া থাকলে সেটি ডেকে পাওয়া মান, না হলে `value`।

**উদাহরণ:**

```python
p = bindparam("x", callable_=lambda: 42)
print(p.effective_value)   # 42
```

### `BindParameter.render_literal_execute()` { #bindparameter-render-literal-execute }

```python
BindParameter.render_literal_execute()
```

**ধরন:** মেথড

এই প্যারামিটারের এমন কপি দেয় যার মান চালানোর মুহূর্তে SQL-এ সরাসরি বসবে (প্যারামিটার হিসেবে নয়)। যেসব জায়গায় ডেটাবেস প্যারামিটার নেয় না (যেমন কিছু ডেটাবেসে `LIMIT`) সেখানে লাগে।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.id == bindparam("i", 2).render_literal_execute())
print(session.scalar(stmt))   # করিম
```

## `ColumnClause` { #columnclause }

```python
from sqlalchemy.sql.expression import ColumnClause
```

নামযুক্ত কলামের মূল ক্লাস: `column("x")`-এর ফল, আর টেবিলের `Column`-এরও প্যারেন্ট।

**উদাহরণ:**

```python
c = column("name")
print(type(c).__name__, c.name, c.table)   # ColumnClause name None
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columnclause-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`default`](#columnclause-default) | অ্যাট্রিবিউট (internal) | Python-দিকের ডিফল্ট মান (শুধু `Column`-এ অর্থবহ; `ColumnClause`-এ `None`)। |
| [`is_literal`](#columnclause-is-literal) | অ্যাট্রিবিউট | `column(..., is_literal=True)` দিলে `True`: নামটি quote ছাড়া হুবহু বসে। |
| [`onupdate`](#columnclause-onupdate) | অ্যাট্রিবিউট (internal) | UPDATE-এর সময়ের Python ডিফল্ট (শুধু `Column`-এ অর্থবহ)। |
| [`server_default`](#columnclause-server-default) | অ্যাট্রিবিউট (internal) | ডেটাবেস-দিকের ডিফল্ট (শুধু `Column`-এ অর্থবহ)। |
| [`server_onupdate`](#columnclause-server-onupdate) | অ্যাট্রিবিউট (internal) | ডেটাবেস-দিকের UPDATE ডিফল্ট (শুধু `Column`-এ অর্থবহ)। |
| [`table`](#columnclause-table) | অ্যাট্রিবিউট | কলামটি যে টেবিলের (একা `column()`-এ `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `ColumnClause.default` { #columnclause-default }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

Python-দিকের ডিফল্ট মান (শুধু `Column`-এ অর্থবহ; `ColumnClause`-এ `None`)।

### `ColumnClause.is_literal` { #columnclause-is-literal }

**ধরন:** অ্যাট্রিবিউট

`column(..., is_literal=True)` দিলে `True`: নামটি quote ছাড়া হুবহু বসে।

**উদাহরণ:**

```python
print(column("x", is_literal=True).is_literal)   # True
```

### `ColumnClause.onupdate` { #columnclause-onupdate }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

UPDATE-এর সময়ের Python ডিফল্ট (শুধু `Column`-এ অর্থবহ)।

### `ColumnClause.server_default` { #columnclause-server-default }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডেটাবেস-দিকের ডিফল্ট (শুধু `Column`-এ অর্থবহ)।

### `ColumnClause.server_onupdate` { #columnclause-server-onupdate }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডেটাবেস-দিকের UPDATE ডিফল্ট (শুধু `Column`-এ অর্থবহ)।

### `ColumnClause.table` { #columnclause-table }

**ধরন:** অ্যাট্রিবিউট

কলামটি যে টেবিলের (একা `column()`-এ `None`)।

**উদাহরণ:**

```python
users = table("users", column("id"))
print(users.c.id.table.name)   # users
```

## `Tuple` { #tuple }

```python
from sqlalchemy.sql.expression import Tuple
```

`tuple_()`-এর ফল: `(a, b, ...)`।

**উদাহরণ:**

```python
t = tuple_(User.id, User.name)
print(type(t).__name__, t)   # Tuple (users.id, users.name)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tuple-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append()`](#tuple-append) | মেথড (internal) | tuple-এ আরেকটি এক্সপ্রেশন যোগ করার ভেতরের মেথড (এক্সপ্রেশন সাধারণত অপরিবর্তনীয় রাখা হয়; নতুন `tuple_()` বানানোই ভালো)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Tuple`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `Tuple.append()` { #tuple-append }

```python
Tuple.append(clause)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

tuple-এ আরেকটি এক্সপ্রেশন যোগ করার ভেতরের মেথড (এক্সপ্রেশন সাধারণত অপরিবর্তনীয় রাখা হয়; নতুন `tuple_()` বানানোই ভালো)।

## `Cast` { #cast }

```python
from sqlalchemy.sql.expression import Cast
```

`cast()` / `.cast()`-এর ফল: `CAST(x AS টাইপ)`।

**উদাহরণ:**

```python
c = cast(User.age, String)
print(type(c).__name__, c.type)   # Cast VARCHAR
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cast-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`wrapped_column_expression`](#cast-wrapped-column-expression) | প্রপার্টি | CAST-এর ভেতরের মূল এক্সপ্রেশন (কলাম-নাম বা লেবেল ঠিক করতে ব্যবহার হয়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Cast`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `Cast.wrapped_column_expression` { #cast-wrapped-column-expression }

**ধরন:** প্রপার্টি

CAST-এর ভেতরের মূল এক্সপ্রেশন (কলাম-নাম বা লেবেল ঠিক করতে ব্যবহার হয়)।

**উদাহরণ:**

```python
print(cast(User.age, String).wrapped_column_expression)   # users.age
```

## `TryCast` { #trycast }

```python
from sqlalchemy.sql.expression import TryCast
```

`try_cast()`-এর ফল (শুধু SQL Server)।

**উদাহরণ:**

```python
print(type(try_cast(column("v"), Integer)).__name__)   # TryCast
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #trycast-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TryCast`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

**`Cast` থেকে:** [`wrapped_column_expression`](#cast-wrapped-column-expression)

///

## `TypeCoerce` { #typecoerce }

```python
from sqlalchemy.sql.expression import TypeCoerce
```

`type_coerce()`-এর ফল: SQL-এ কিছু না বসিয়ে শুধু Python-দিকের টাইপ বদলানো এক্সপ্রেশন।

**উদাহরণ:**

```python
tc = type_coerce(User.age, String)
print(type(tc).__name__, tc.type, tc)   # TypeCoerce VARCHAR users.age
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typecoerce-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`typed_expression`](#typecoerce-typed-expression) | প্রপার্টি (internal) | নতুন টাইপসহ ভেতরের এক্সপ্রেশন (কম্পাইলের সময় ব্যবহার হয়)। |
| [`wrapped_column_expression`](#typecoerce-wrapped-column-expression) | প্রপার্টি | মোড়ানো মূল এক্সপ্রেশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TypeCoerce`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

### `TypeCoerce.typed_expression` { #typecoerce-typed-expression }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নতুন টাইপসহ ভেতরের এক্সপ্রেশন (কম্পাইলের সময় ব্যবহার হয়)।

### `TypeCoerce.wrapped_column_expression` { #typecoerce-wrapped-column-expression }

**ধরন:** প্রপার্টি

মোড়ানো মূল এক্সপ্রেশন।

**উদাহরণ:**

```python
print(type_coerce(User.age, String).wrapped_column_expression)   # users.age
```

## `Case` { #case }

```python
from sqlalchemy.sql.expression import Case
```

`case()`-এর ফল। `.whens`-এ `(শর্ত, মান)` জোড়া, `.else_`-এ ELSE মান। নিজস্ব নতুন সদস্য নেই।

**উদাহরণ:**

```python
c = case((User.age > 26, "বড়"), else_="ছোট")
print(type(c).__name__, len(c.whens))   # Case 1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #case-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Case`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `Extract` { #extract }

```python
from sqlalchemy.sql.expression import Extract
```

`extract()`-এর ফল: `EXTRACT(field FROM expr)`। `.field` আর `.expr`-এ অংশগুলো। নিজস্ব নতুন সদস্য নেই।

**উদাহরণ:**

```python
e = extract("year", User.joined)
print(type(e).__name__, e.field)   # Extract year
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #extract-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Extract`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `Null` { #null }

```python
from sqlalchemy.sql.expression import Null
```

`null()`-এর ফল: SQL `NULL`।

**উদাহরণ:**

```python
print(type(null()).__name__, null())   # Null NULL
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #null-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Null`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `True_` { #true- }

```python
from sqlalchemy.sql.expression import True_
```

`true()`-এর ফল: SQL `true`।

**উদাহরণ:**

```python
print(type(true()).__name__, true())   # True_ true
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #true--summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `True_`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `False_` { #false- }

```python
from sqlalchemy.sql.expression import False_
```

`false()`-এর ফল: SQL `false`।

**উদাহরণ:**

```python
print(type(false()).__name__, false())   # False_ false
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #false--summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `False_`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## `CollectionAggregate` { #collectionaggregate }

```python
from sqlalchemy.sql.expression import CollectionAggregate
```

`any_()` / `all_()` (আর `.any_()` / `.all_()` মেথড)-এর ফল: `ANY (...)` / `ALL (...)`।

**উদাহরণ:**

```python
e = any_(select(Address.user_id).scalar_subquery())
print(type(e).__name__)   # CollectionAggregate
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #collectionaggregate-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CollectionAggregate`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`anon_key_label`](#columnelement-anon-key-label) · [`anon_label`](#columnelement-anon-label) · [`base_columns`](#columnelement-base-columns) · [`cast()`](#columnelement-cast) · [`comparator`](#columnelement-comparator) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`expression`](#columnelement-expression) · [`foreign_keys`](#columnelement-foreign-keys) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`key`](#columnelement-key) · [`label()`](#columnelement-label) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`primary_key`](#columnelement-primary-key) · [`proxy_set`](#columnelement-proxy-set) · [`self_group()`](#columnelement-self-group) · [`shares_lineage()`](#columnelement-shares-lineage) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`type`](#columnelement-type) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

///

## lambda স্টেটমেন্ট { #statementlambdaelement-group }

## `StatementLambdaElement` { #statementlambdaelement }

```python
from sqlalchemy.sql.expression import StatementLambdaElement
```

`lambda_stmt()`-এর ফল: ক্যাশযোগ্য lambda-ভিত্তিক স্টেটমেন্ট। `+` (বা `add_criteria()`) দিয়ে আরও lambda যোগ করা যায়; `session.execute()`-এ সরাসরি চলে।

**উদাহরণ:**

```python
stmt = lambda_stmt(lambda: select(User.name)) + (lambda s: s.where(User.age > 26))
print(isinstance(stmt, StatementLambdaElement), session.scalars(stmt).all())   # True ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #statementlambdaelement-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_criteria()`](#statementlambdaelement-add-criteria) | মেথড | আরেকটি lambda যোগ করে (`+`-এর মতো), সাথে ট্র্যাকিং অপশন (`enable_tracking`, `track_on`, `track_closure_variables`, `track_bound_values`) আলাদা করে দেওয়া যায়। |
| [`parent_lambda`](#statementlambdaelement-parent-lambda) | অ্যাট্রিবিউট (internal) | চেইনে আগের lambda-অংশ (প্রথম অংশে `None`)। |
| [`spoil()`](#statementlambdaelement-spoil) | মেথড | ক্যাশিং বন্ধ করা একটি রূপ দেয়: প্রতিবার সব lambda নতুন করে চলে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `StatementLambdaElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](#columnelement-allows-lambda) · [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`self_group()`](#columnelement-self-group) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`unique_params()`](#columnelement-unique-params) · [`uses_inspection`](#columnelement-uses-inspection)

**`Select` থেকে:** [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options)

///

### `StatementLambdaElement.add_criteria()` { #statementlambdaelement-add-criteria }

```python
StatementLambdaElement.add_criteria(other, enable_tracking=True, track_on=None, track_closure_variables=True, track_bound_values=True)
```

**ধরন:** মেথড

আরেকটি lambda যোগ করে (`+`-এর মতো), সাথে ট্র্যাকিং অপশন (`enable_tracking`, `track_on`, `track_closure_variables`, `track_bound_values`) আলাদা করে দেওয়া যায়।

**উদাহরণ:**

```python
limit = 2
stmt = lambda_stmt(lambda: select(User.name).order_by(User.id))
stmt = stmt.add_criteria(lambda s: s.limit(limit))
print(session.scalars(stmt).all())   # ['রহিম', 'করিম']
```

### `StatementLambdaElement.parent_lambda` { #statementlambdaelement-parent-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

চেইনে আগের lambda-অংশ (প্রথম অংশে `None`)।

### `StatementLambdaElement.spoil()` { #statementlambdaelement-spoil }

```python
StatementLambdaElement.spoil()
```

**ধরন:** মেথড

ক্যাশিং বন্ধ করা একটি রূপ দেয়: প্রতিবার সব lambda নতুন করে চলে। কোনো lambda ক্যাশে সমস্যা করলে ডিবাগ করতে।

**উদাহরণ:**

```python
stmt = lambda_stmt(lambda: select(User.name).where(User.id == 3)).spoil()
print(session.scalar(stmt))   # সুমি
```

## `LambdaElement` { #lambdaelement }

```python
from sqlalchemy.sql.expression import LambdaElement
```

lambda-ভিত্তিক SQL অংশের মূল ক্লাস (`StatementLambdaElement`-এর প্যারেন্ট)। ORM-এর `with_loader_criteria(lambda ...)`-এর মতো জায়গায় ভেতরে ব্যবহার হয়।

**উদাহরণ:**

```python
print(issubclass(StatementLambdaElement, LambdaElement))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #lambdaelement-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `LambdaElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](#columnelement-compare) · [`compile()`](#columnelement-compile) · [`description`](#columnelement-description) · [`entity_namespace`](#columnelement-entity-namespace) · [`get_children()`](#columnelement-get-children) · [`inherit_cache`](#columnelement-inherit-cache) · [`is_clause_element`](#columnelement-is-clause-element) · [`is_dml`](#columnelement-is-dml) · [`is_selectable`](#columnelement-is-selectable) · [`memoized_attribute`](#columnelement-memoized-attribute) · [`memoized_instancemethod()`](#columnelement-memoized-instancemethod) · [`params()`](#columnelement-params) · [`self_group()`](#columnelement-self-group) · [`stringify_dialect`](#columnelement-stringify-dialect) · [`supports_execution`](#columnelement-supports-execution) · [`unique_params()`](#columnelement-unique-params)

**`StatementLambdaElement` থেকে:** [`parent_lambda`](#statementlambdaelement-parent-lambda)

///

/// check | সংক্ষেপে মনে রাখুন

* নিজের হেল্পার ফাংশনে "যেকোনো SQL শর্ত" নিতে টাইপ হিন্ট: `ColumnElement[bool]`।
* SQL দেখতে: `print(expr)`; নির্দিষ্ট ডেটাবেসে: `expr.compile(dialect=postgresql.dialect())`; মানসহ: `compile_kwargs={"literal_binds": True}`।
* টেস্টে শর্ত তুলনা: `expr.compare(other)`।
* সাবকুয়েরি: একটি মান চাইলে `scalar_subquery()` → `ScalarSelect`; অস্তিত্ব চাইলে `exists()` → `Exists`; টেবিলের মতো চাইলে `subquery()`।
* GROUP BY/ORDER BY-তে লেবেলের নাম: `label.as_reference()`।

///
