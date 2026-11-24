# func ও SQL ফাংশন API: count, sum, window, FILTER … { #api-functions }

/// note | এই পেজে যা আছে

* `func`: যেকোনো SQL ফাংশন ডাকার অবজেক্ট, আর `register_function()`।
* `FunctionElement` (সব ফাংশনের মূল ক্লাস)-এর **সব** সদস্য: `over()`, `filter()`, `within_group()`, `aggregate_order_by()` (২.১), `table_valued()`, `column_valued()` …; আর `Function`, `GenericFunction`।
* SQLAlchemy-র **সব** তৈরি-করা ফাংশন (`func.count()`, `func.sum()`, `func.coalesce()`, `func.rank()`, `func.percentile_cont()`, `func.aggregate_strings()`, ২.১-এর নতুন `func.pow()`, `func.any_()` …), প্রতিটির উদাহরণসহ।
* window ও aggregate সহায়ক: `over()`, `within_group()`, `funcfilter()`, `aggregate_order_by()` আর তাদের ক্লাস `Over`, `WithinGroup`, `FunctionFilter`, `AggregateOrderBy`।

///

`func.যেকোনো_নাম(...)` লিখলে SQLAlchemy সেই নামের SQL ফাংশন বানায়: `func.lower(User.name)` → `lower(users.name)`। নামটি SQLAlchemy না চিনলেও চলে (ডেটাবেসের নিজস্ব ফাংশন যেমন `func.date_trunc(...)`, `func.jsonb_build_object(...)`)। আর চেনা নাম (`count`, `sum`, `now` …) হলে সাথে সঠিক **ফলের টাইপ** আর ডেটাবেস-ভেদে সঠিক SQL বসে। window function শিখতে দেখুন [অ্যাডভান্সড কুয়েরি](../advanced-queries.md#s28)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

একটি বিক্রির টেবিল `Sale` (`id`, `region`, `product`, `amount`, `qty`, `sold_at`):

| id | region | product | amount | qty | sold_at |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ১ | ঢাকা | কলম | ১০০ | ২ | ২০২৪-০১-০৫ |
| ২ | ঢাকা | খাতা | ২৫০ | ৫ | ২০২৪-০১-২০ |
| ৩ | চট্টগ্রাম | কলম | ১৫০ | ৩ | ২০২৪-০২-১০ |
| ৪ | চট্টগ্রাম | খাতা | ৫০ | `NULL` | ২০২৪-০২-১৫ |
| ৫ | ঢাকা | কলম | ৩০০ | ৬ | ২০২৪-০৩-০১ |

`rows(স্টেটমেন্ট)` চালিয়ে সব রো দেয়; `one(এক্সপ্রেশন)` শুধু একটি মান বের করে (`session.scalar(select(এক্সপ্রেশন))`)। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## `func` { #func }

```python
from sqlalchemy import func
```

**ধরন:** বিশেষ অবজেক্ট (ফাংশন-জেনারেটর)

`func.নাম(আর্গুমেন্ট...)` লিখলে `নাম(আর্গুমেন্ট...)` SQL ফাংশন তৈরি হয়। নিয়মগুলো:

* **অচেনা নাম** → সাধারণ `Function`; ফলের টাইপ অজানা (`NullType`), দরকার হলে `type_=` দিন: `func.date_trunc("month", col, type_=Date)`।
* **চেনা নাম** (নিচের তালিকার `count`, `sum`, `now` …) → সেই `GenericFunction` সাবক্লাস, সঠিক ফলের টাইপসহ।
* **ডট দিয়ে প্যাকেজ/স্কিমা:** `func.myschema.myfunc()` → `myschema.myfunc()`।
* আর্গুমেন্টে Python মান দিলে bound parameter হয় (নিরাপদ)।
* ফাংশনের নাম SQL-এ হুবহু বসে; বড়-ছোট হাতের নাম বা বিশেষ অক্ষর থাকলে quote হয়।

**উদাহরণ:**

```python
print(func.lower(Sale.product))                                    # lower(sales.product)
print(rows(select(Sale.region, func.sum(Sale.amount)).group_by(Sale.region).order_by(Sale.region)))
# [('চট্টগ্রাম', 200), ('ঢাকা', 650)]
print(one(func.date_trunc("month", func.max(Sale.sold_at))))         # 2024-03-01 00:00:00+00:00
print(func.myschema.myfunc(1))                                      # myschema.myfunc(:myfunc_1)
```

## `register_function()` { #register-function }

```python
from sqlalchemy.sql.functions import register_function
```

```python
register_function(identifier, fn, package='_default')
```

**ধরন:** ফাংশন

একটি নাম `func`-এ নিবন্ধন করে, যাতে `func.নাম(...)` আপনার দেওয়া ক্লাস ব্যবহার করে। `GenericFunction` সাবক্লাস বানালে এটি নিজে থেকেই ডাকা হয়; শুধু অন্য কোনো construct (যেমন `Cast`-এর মতো) `func`-এ যুক্ত করতে সরাসরি দরকার।

**উদাহরণ:**

```python
class shout(Function):
    inherit_cache = True
    def __init__(self, *args, **kw):
        super().__init__("upper", *args, **kw)

register_function("shout_demo", shout)
print(one(func.shout_demo("hello")))   # HELLO
```

### `register_function()`-এর সব প্যারামিটার { #register-function-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `identifier` | `func.` এর পরে যে নাম লেখা হবে। |
| `fn` | যে ক্লাস (বা callable) সেই নামে ডাকা হবে। |
| `package` | প্যাকেজের নাম (ডিফল্ট `"_default"`); দিলে `func.প্যাকেজ.নাম()` রূপে পাওয়া যায়। |

## ফাংশনের ক্লাস { #functionelement-group }

## `FunctionElement` { #functionelement }

```python
from sqlalchemy.sql.functions import FunctionElement
```

**সব** SQL ফাংশনের মূল ক্লাস: `func.xxx()` যা-ই ফেরত দিক, সেটি এর সাবক্লাস। কলামের মতো (`ColumnElement`) ব্যবহার হয়, আবার টেবিলের মতো FROM-এও বসতে পারে (table-valued function, যেমন PostgreSQL-এর `generate_series`)। নিচে শুধু ফাংশনের নিজস্ব সদস্য; কলামের সব অপারেটর আর `label()`, `cast()` ইত্যাদি ভাঁজ করা বক্সে লিংকসহ।

**উদাহরণ:**

```python
f = func.count(Sale.id)
print(isinstance(f, FunctionElement), f.type)   # True INTEGER
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #functionelement-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`aggregate_order_by()`](#functionelement-aggregate-order-by) | মেথড | (২.১-এ নতুন) aggregate ফাংশনের **ভেতরে** `ORDER BY` বসায়: `array_agg(x ORDER BY y)`, `string_agg(x, ',' ORDER BY y)`। |
| [`alias()`](#functionelement-alias) | মেথড | ফাংশনকে নামযুক্ত FROM (table-valued alias) বানায়। |
| [`as_comparison()`](#functionelement-as-comparison) | মেথড | দুই-আর্গুমেন্টের একটি ফাংশনকে "তুলনা" হিসেবে ধরে (বাম = আর্গুমেন্ট নং `left_index`, ডান = `right_index`, ১ থেকে গোনা)। |
| [`c`](#functionelement-c) | প্রপার্টি | `columns`-এর ছোট নাম। |
| [`clauses`](#functionelement-clauses) | প্রপার্টি | ফাংশনের আর্গুমেন্টগুলো (একটি `ClauseList`)। |
| [`column_valued()`](#functionelement-column-valued) | মেথড | ফাংশনটিকে FROM-এ বসিয়ে তার একমাত্র কলাম হিসেবে ব্যবহার করে (যেসব ফাংশন একাধিক রো দেয়, যেমন `generate_series`, `unnest`)। |
| [`columns`](#functionelement-columns) | প্রপার্টি | ফাংশনকে FROM হিসেবে ব্যবহার করলে যে কলামগুলো পাওয়া যায় (সাধারণ ফাংশনে একটি বেনামি কলাম)। |
| [`corresponding_column()`](#functionelement-corresponding-column) | মেথড (internal) | FROM হিসেবে ব্যবহৃত হলে, অন্য একটি কলামের সাথে মিলে এমন রপ্তানি করা কলাম খোঁজে (alias/adaptation ব্যবস্থার জন্য)। |
| [`execution_options()`](#functionelement-execution-options) | মেথড | ফাংশন-অবজেক্টকে সরাসরি স্টেটমেন্ট হিসেবে চালালে প্রযোজ্য execution option সেট করে (`Select.execution_options()`-এর মতো)। |
| [`exported_columns`](#functionelement-exported-columns) | প্রপার্টি (internal) | FROM হিসেবে রপ্তানি হওয়া কলাম-সংগ্রহ (`columns`-এর মতো)। |
| [`filter()`](#functionelement-filter) | মেথড | aggregate-এর সাথে `FILTER (WHERE ...)`: শুধু শর্ত মানা রো-গুলোর ওপর হিসাব। |
| [`get_execution_options()`](#functionelement-get-execution-options) | মেথড | সেট করা execution option-গুলো দেয়। |
| [`is_delete`](#functionelement-is-delete) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`is_derived_from()`](#functionelement-is-derived-from) | মেথড (internal) | FROM হিসেবে, এটি দেওয়া FROM থেকে তৈরি কি না (alias ব্যবস্থার জন্য)। |
| [`is_from_statement`](#functionelement-is-from-statement) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`is_insert`](#functionelement-is-insert) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`is_select`](#functionelement-is-select) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`is_text`](#functionelement-is-text) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`is_update`](#functionelement-is-update) | অ্যাট্রিবিউট (internal) | স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)। |
| [`join()`](#functionelement-join) | মেথড | ফাংশনকে FROM হিসেবে ধরে আরেকটি টেবিলের সাথে JOIN বানায়। |
| [`lateral()`](#functionelement-lateral) | মেথড | ফাংশনকে `LATERAL` FROM হিসেবে বসায়, যাতে আর্গুমেন্টে আগের টেবিলের কলাম ব্যবহার করা যায় (প্রতিটি রো-র জন্য আলাদা করে ফাংশন চলে)। |
| [`monotonic`](#functionelement-monotonic) | অ্যাট্রিবিউট | (২.১-এ নতুন) ফাংশনটি প্রতিবার আগের চেয়ে বড় মান দেয় কি না (`Function(..., monotonic=True)`)। |
| [`named_with_column`](#functionelement-named-with-column) | অ্যাট্রিবিউট (internal) | FROM হিসেবে নামযুক্ত কলাম আছে কি না তার ভেতরের ফ্ল্যাগ। |
| [`options()`](#functionelement-options) | মেথড (internal) | স্টেটমেন্ট-অপশন যোগ করে (`Executable.options()`); ফাংশনে সাধারণত দরকার নেই। |
| [`outerjoin()`](#functionelement-outerjoin) | মেথড | `join(..., isouter=True)`-এর ছোট রূপ। |
| [`over()`](#functionelement-over) | মেথড | ফাংশনকে **window function** বানায়: `OVER (PARTITION BY ... ORDER BY ... ROWS/RANGE/GROUPS ...)`। |
| [`packagenames`](#functionelement-packagenames) | অ্যাট্রিবিউট | `func.pkg.fn()` লিখলে প্যাকেজ/স্কিমার নামগুলো (tuple)। |
| [`replace_selectable()`](#functionelement-replace-selectable) | মেথড (internal) | ভেতরের একটি FROM-কে alias দিয়ে বদলে কপি দেয় (পুরোনো adaptation API)। |
| [`scalar_table_valued()`](#functionelement-scalar-table-valued) | মেথড | যে ফাংশন রেকর্ড/রো দেয়, তার একটি নির্দিষ্ট ক্ষেত্রকে কলামের মতো বের করে, FROM ছাড়াই: `(jsonb_each(x)).key`। |
| [`schema`](#functionelement-schema) | অ্যাট্রিবিউট (internal) | FROM হিসেবে স্কিমার নাম (ফাংশনে `None`)। |
| [`select()`](#functionelement-select) | মেথড | `select(ফাংশন)`-এর ছোট রূপ। |
| [`selectable`](#functionelement-selectable) | প্রপার্টি (internal) | FROM হিসেবে ব্যবহারের selectable রূপ। |
| [`table_valued()`](#functionelement-table-valued) | মেথড | যে ফাংশন একাধিক কলামের রো দেয় (table-valued function), সেটিকে নামযুক্ত কলামসহ FROM বানায়। |
| [`tablesample()`](#functionelement-tablesample) | মেথড (internal) | `FromClause` থেকে পাওয়া `TABLESAMPLE`; ফাংশনের ক্ষেত্রে কার্যত ব্যবহার হয় না (টেবিলে `tablesample()` দেখুন)। |
| [`with_cols()`](#functionelement-with-cols) | মেথড | (২.১-এ নতুন) শুধু **টাইপ চেকারের** জন্য: FROM হিসেবে ব্যবহৃত ফাংশনকে একটি `TypedColumns` সাবক্লাসের কলাম-কাঠামো দিয়ে typed করে। |
| [`within_group()`](#functionelement-within-group) | মেথড | "ordered-set aggregate" (`percentile_cont`, `mode`, `rank` ইত্যাদি hypothetical-set)-এর জন্য `WITHIN GROUP (ORDER BY ...)` বসায়। |
| [`within_group_type()`](#functionelement-within-group-type) | মেথড (internal) | `WITHIN GROUP`-এর ORDER BY এক্সপ্রেশন দেখে ফলের টাইপ ঠিক করার হুক (`percentile_cont` ইত্যাদি override করে)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FunctionElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `FunctionElement.aggregate_order_by()` { #functionelement-aggregate-order-by }

```python
FunctionElement.aggregate_order_by(*order_by)
```

**ধরন:** মেথড

(২.১-এ নতুন) aggregate ফাংশনের **ভেতরে** `ORDER BY` বসায়: `array_agg(x ORDER BY y)`, `string_agg(x, ',' ORDER BY y)`। ফলের তালিকা/স্ট্রিংয়ের ক্রম ঠিক করতে। PostgreSQL, MySQL/MariaDB, SQLite-এ ভেতরের ORDER BY; Oracle/SQL Server-এ `WITHIN GROUP` হিসেবে কম্পাইল হয়।

**উদাহরণ:**

```python
agg = func.array_agg(Sale.product).aggregate_order_by(Sale.amount.desc())
print(one(agg.filter(Sale.region == "ঢাকা")))   # ['কলম', 'খাতা', 'কলম']
```

### `FunctionElement.alias()` { #functionelement-alias }

```python
FunctionElement.alias(name=None, joins_implicitly=False)
```

**ধরন:** মেথড

ফাংশনকে নামযুক্ত FROM (table-valued alias) বানায়। বেশিরভাগ ক্ষেত্রে `table_valued()` বা `column_valued()` সহজ।

**উদাহরণ:**

```python
g = func.generate_series(1, 3).alias("g")
print(session.scalars(select(g.column)).all())   # [1, 2, 3]
```

### `FunctionElement.as_comparison()` { #functionelement-as-comparison }

```python
FunctionElement.as_comparison(left_index, right_index)
```

**ধরন:** মেথড

দুই-আর্গুমেন্টের একটি ফাংশনকে "তুলনা" হিসেবে ধরে (বাম = আর্গুমেন্ট নং `left_index`, ডান = `right_index`, ১ থেকে গোনা)। রিলেশনশিপের কাস্টম `primaryjoin`-এ SQL ফাংশন দিয়ে join করতে কাজে লাগে।

**উদাহরণ:**

```python
cond = func.starts_with(Sale.product, "খা").as_comparison(1, 2)
print(cond.left, "|", cond.right.value)                     # sales.product | খা
print(session.scalar(select(func.count()).where(cond)))     # 2
```

### `FunctionElement.c` { #functionelement-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(len(func.now().c))   # 1
```

### `FunctionElement.clauses` { #functionelement-clauses }

**ধরন:** প্রপার্টি

ফাংশনের আর্গুমেন্টগুলো (একটি `ClauseList`)।

**উদাহরণ:**

```python
print(func.coalesce(Sale.qty, 0).clauses)   # sales.qty, :coalesce_1
```

### `FunctionElement.column_valued()` { #functionelement-column-valued }

```python
FunctionElement.column_valued(name=None, joins_implicitly=False)
```

**ধরন:** মেথড

ফাংশনটিকে FROM-এ বসিয়ে তার একমাত্র কলাম হিসেবে ব্যবহার করে (যেসব ফাংশন একাধিক রো দেয়, যেমন `generate_series`, `unnest`)।

**উদাহরণ:**

```python
print(session.scalars(select(func.generate_series(1, 3).column_valued())).all())   # [1, 2, 3]
print(session.scalars(select(func.unnest(cast([5, 6], postgresql.ARRAY(Integer))).column_valued())).all())   # [5, 6]
```

### `FunctionElement.columns` { #functionelement-columns }

**ধরন:** প্রপার্টি

ফাংশনকে FROM হিসেবে ব্যবহার করলে যে কলামগুলো পাওয়া যায় (সাধারণ ফাংশনে একটি বেনামি কলাম)।

**উদাহরণ:**

```python
print(len(func.now().columns))   # 1
```

### `FunctionElement.corresponding_column()` { #functionelement-corresponding-column }

```python
FunctionElement.corresponding_column(column, require_embedded=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে ব্যবহৃত হলে, অন্য একটি কলামের সাথে মিলে এমন রপ্তানি করা কলাম খোঁজে (alias/adaptation ব্যবস্থার জন্য)।

### `FunctionElement.execution_options()` { #functionelement-execution-options }

```python
FunctionElement.execution_options(**kw)
```

**ধরন:** মেথড

ফাংশন-অবজেক্টকে সরাসরি স্টেটমেন্ট হিসেবে চালালে প্রযোজ্য execution option সেট করে (`Select.execution_options()`-এর মতো)।

**উদাহরণ:**

```python
f = func.now().execution_options(my_flag=True)
print(dict(f.get_execution_options()))   # {'my_flag': True}
```

### `FunctionElement.exported_columns` { #functionelement-exported-columns }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে রপ্তানি হওয়া কলাম-সংগ্রহ (`columns`-এর মতো)।

### `FunctionElement.filter()` { #functionelement-filter }

```python
FunctionElement.filter(*criterion)
```

**ধরন:** মেথড

aggregate-এর সাথে `FILTER (WHERE ...)`: শুধু শর্ত মানা রো-গুলোর ওপর হিসাব। একই কুয়েরিতে কয়েকটি শর্তসাপেক্ষ গণনা করতে দারুণ (`CASE`-এর চেয়ে পরিষ্কার)।

**উদাহরণ:**

```python
stmt = select(func.count(Sale.id).filter(Sale.region == "ঢাকা"),
              func.sum(Sale.amount).filter(Sale.product == "কলম"))
print(rows(stmt))   # [(3, 550)]
```

### `FunctionElement.get_execution_options()` { #functionelement-get-execution-options }

```python
FunctionElement.get_execution_options()
```

**ধরন:** মেথড

সেট করা execution option-গুলো দেয়।

**উদাহরণ:**

```python
print(dict(func.now().get_execution_options()))   # {}
```

### `FunctionElement.is_delete` { #functionelement-is-delete }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.is_derived_from()` { #functionelement-is-derived-from }

```python
FunctionElement.is_derived_from(fromclause)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে, এটি দেওয়া FROM থেকে তৈরি কি না (alias ব্যবস্থার জন্য)।

### `FunctionElement.is_from_statement` { #functionelement-is-from-statement }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.is_insert` { #functionelement-is-insert }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.is_select` { #functionelement-is-select }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.is_text` { #functionelement-is-text }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.is_update` { #functionelement-is-update }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-ধরনের ফ্ল্যাগ (`False`)।

### `FunctionElement.join()` { #functionelement-join }

```python
FunctionElement.join(right, onclause=None, isouter=False, full=False)
```

**ধরন:** মেথড

ফাংশনকে FROM হিসেবে ধরে আরেকটি টেবিলের সাথে JOIN বানায়।

**উদাহরণ:**

```python
j = func.generate_series(1, 2).join(Sale.__table__, true())
print(session.scalar(select(func.count()).select_from(j)))   # 10  (২ × ৫)
```

### `FunctionElement.lateral()` { #functionelement-lateral }

```python
FunctionElement.lateral(name=None)
```

**ধরন:** মেথড

ফাংশনকে `LATERAL` FROM হিসেবে বসায়, যাতে আর্গুমেন্টে আগের টেবিলের কলাম ব্যবহার করা যায় (প্রতিটি রো-র জন্য আলাদা করে ফাংশন চলে)।

**উদাহরণ:**

```python
g = func.generate_series(1, Sale.qty).lateral("g")
stmt = select(Sale.id, func.count()).join(g, true()).group_by(Sale.id).order_by(Sale.id)
print(rows(stmt))   # [(1, 2), (2, 5), (3, 3), (5, 6)]
```

### `FunctionElement.monotonic` { #functionelement-monotonic }

**ধরন:** অ্যাট্রিবিউট

(২.১-এ নতুন) ফাংশনটি প্রতিবার আগের চেয়ে বড় মান দেয় কি না (`Function(..., monotonic=True)`)। এমন ফাংশন primary key-র ডিফল্ট হলে, বাল্ক INSERT-এ RETURNING রো-গুলোর ক্রম মেলাতে SQLAlchemy সেটিকে "sentinel" হিসেবে ব্যবহার করতে পারে।

**উদাহরণ:**

```python
print(Function("nextval", literal("order_seq"), monotonic=True).monotonic)   # True
```

### `FunctionElement.named_with_column` { #functionelement-named-with-column }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে নামযুক্ত কলাম আছে কি না তার ভেতরের ফ্ল্যাগ।

### `FunctionElement.options()` { #functionelement-options }

```python
FunctionElement.options(*options)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট-অপশন যোগ করে (`Executable.options()`); ফাংশনে সাধারণত দরকার নেই।

### `FunctionElement.outerjoin()` { #functionelement-outerjoin }

```python
FunctionElement.outerjoin(right, onclause=None, full=False)
```

**ধরন:** মেথড

`join(..., isouter=True)`-এর ছোট রূপ।

**উদাহরণ:**

```python
j = func.generate_series(1, 2).outerjoin(Sale.__table__, Sale.id > 4)
print(session.scalar(select(func.count()).select_from(j)))   # 2
```

### `FunctionElement.over()` { #functionelement-over }

```python
FunctionElement.over(*, partition_by=None, order_by=None, rows=None, range_=None, groups=None, exclude=None)
```

**ধরন:** মেথড

ফাংশনকে **window function** বানায়: `OVER (PARTITION BY ... ORDER BY ... ROWS/RANGE/GROUPS ...)`। রো-গুলো একত্র না করে প্রতিটি রো-র পাশে হিসাব (র‍্যাংক, চলমান যোগফল, আগের রো-র মান)। প্যারামিটারগুলো `over()` ফাংশনের মতো।

**উদাহরণ:**

```python
rk = func.rank().over(partition_by=Sale.region, order_by=Sale.amount.desc())
print(rows(select(Sale.id, rk).order_by(Sale.id)))   # [(1, 3), (2, 2), (3, 1), (4, 2), (5, 1)]
```

### `FunctionElement.packagenames` { #functionelement-packagenames }

**ধরন:** অ্যাট্রিবিউট

`func.pkg.fn()` লিখলে প্যাকেজ/স্কিমার নামগুলো (tuple)।

**উদাহরণ:**

```python
print(func.analytics.score(1).packagenames)   # ('analytics',)
```

### `FunctionElement.replace_selectable()` { #functionelement-replace-selectable }

```python
FunctionElement.replace_selectable(old, alias)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের একটি FROM-কে alias দিয়ে বদলে কপি দেয় (পুরোনো adaptation API)।

### `FunctionElement.scalar_table_valued()` { #functionelement-scalar-table-valued }

```python
FunctionElement.scalar_table_valued(name, type_=None)
```

**ধরন:** মেথড

যে ফাংশন রেকর্ড/রো দেয়, তার একটি নির্দিষ্ট ক্ষেত্রকে কলামের মতো বের করে, FROM ছাড়াই: `(jsonb_each(x)).key`।

**উদাহরণ:**

```python
k = func.jsonb_each(cast({"a": 1, "b": 2}, JSONB)).scalar_table_valued("key")
print(session.scalars(select(k)).all())   # ['a', 'b']
```

### `FunctionElement.schema` { #functionelement-schema }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে স্কিমার নাম (ফাংশনে `None`)।

### `FunctionElement.select()` { #functionelement-select }

```python
FunctionElement.select()
```

**ধরন:** মেথড

`select(ফাংশন)`-এর ছোট রূপ।

**উদাহরণ:**

```python
print(session.scalar(func.count(Sale.id).select()))   # 5
```

### `FunctionElement.selectable` { #functionelement-selectable }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM হিসেবে ব্যবহারের selectable রূপ।

### `FunctionElement.table_valued()` { #functionelement-table-valued }

```python
FunctionElement.table_valued(*expr, **kw)
```

**ধরন:** মেথড

যে ফাংশন একাধিক কলামের রো দেয় (table-valued function), সেটিকে নামযুক্ত কলামসহ FROM বানায়। `.render_derived()` দিয়ে কলামের নাম/টাইপ SQL-এ বসানো যায় (`AS x(a INT, b TEXT)`)।

**উদাহরণ:**

```python
tv = func.generate_series(1, 3).table_valued("n").render_derived()
print(session.scalars(select(tv.c.n * 10)).all())   # [10, 20, 30]
kv = func.jsonb_each_text(cast({"k": "v"}, JSONB)).table_valued("key", "value")
print(rows(select(kv.c.key, kv.c.value)))          # [('k', 'v')]
```

### `FunctionElement.tablesample()` { #functionelement-tablesample }

```python
FunctionElement.tablesample(sampling, name=None, seed=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`FromClause` থেকে পাওয়া `TABLESAMPLE`; ফাংশনের ক্ষেত্রে কার্যত ব্যবহার হয় না (টেবিলে `tablesample()` দেখুন)।

### `FunctionElement.with_cols()` { #functionelement-with-cols }

```python
FunctionElement.with_cols(type_)
```

**ধরন:** মেথড

(২.১-এ নতুন) শুধু **টাইপ চেকারের** জন্য: FROM হিসেবে ব্যবহৃত ফাংশনকে একটি `TypedColumns` সাবক্লাসের কলাম-কাঠামো দিয়ে typed করে। রানটাইমে নিজেকেই ফেরত দেয়, কিছু যাচাই করে না।

**উদাহরণ:**

```python
tv = func.generate_series(1, 2).table_valued("n")
print(tv.with_cols(object) is tv)   # True
```

### `FunctionElement.within_group()` { #functionelement-within-group }

```python
FunctionElement.within_group(*order_by)
```

**ধরন:** মেথড

"ordered-set aggregate" (`percentile_cont`, `mode`, `rank` ইত্যাদি hypothetical-set)-এর জন্য `WITHIN GROUP (ORDER BY ...)` বসায়।

**উদাহরণ:**

```python
med = func.percentile_cont(0.5).within_group(Sale.amount)
print(one(med))   # 150.0
```

### `FunctionElement.within_group_type()` { #functionelement-within-group-type }

```python
FunctionElement.within_group_type(within_group)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`WITHIN GROUP`-এর ORDER BY এক্সপ্রেশন দেখে ফলের টাইপ ঠিক করার হুক (`percentile_cont` ইত্যাদি override করে)।

## `Function` { #function }

```python
from sqlalchemy.sql.functions import Function
```

নামযুক্ত সাধারণ SQL ফাংশন। `func.অচেনা_নাম(...)` এটাই ফেরত দেয়। সরাসরি বানানো যায়: `Function("lower", col)`; তখন `type_` দিয়ে ফলের টাইপও দেওয়া যায়।

**উদাহরণ:**

```python
f = Function("upper", Sale.product, type_=String)
print(f, f.type)                         # upper(sales.product) VARCHAR
print(type(func.date_trunc("day", Sale.sold_at)).__name__)   # Function
```

### কনস্ট্রাক্টরের প্যারামিটার { #function-params }

```python
Function(name, *clauses, type_=None, packagenames=None, monotonic=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | SQL ফাংশনের নাম। |
| `clauses` | আর্গুমেন্টগুলো। |
| `type_` | ফলের SQL টাইপ। |
| `packagenames` | প্যাকেজ/স্কিমার নামের tuple (`func.pkg.fn`-এর মতো)। |
| `monotonic` | (২.১) ফাংশনটি ক্রমবর্ধমান মান দেয় কি না (উপরের `monotonic` দেখুন)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #function-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১১৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Function`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FunctionElement` থেকে:** [`aggregate_order_by()`](#functionelement-aggregate-order-by) · [`alias()`](#functionelement-alias) · [`as_comparison()`](#functionelement-as-comparison) · [`c`](#functionelement-c) · [`clauses`](#functionelement-clauses) · [`column_valued()`](#functionelement-column-valued) · [`columns`](#functionelement-columns) · [`corresponding_column()`](#functionelement-corresponding-column) · [`execution_options()`](#functionelement-execution-options) · [`exported_columns`](#functionelement-exported-columns) · [`filter()`](#functionelement-filter) · [`get_execution_options()`](#functionelement-get-execution-options) · [`is_delete`](#functionelement-is-delete) · [`is_derived_from()`](#functionelement-is-derived-from) · [`is_from_statement`](#functionelement-is-from-statement) · [`is_insert`](#functionelement-is-insert) · [`is_select`](#functionelement-is-select) · [`is_text`](#functionelement-is-text) · [`is_update`](#functionelement-is-update) · [`join()`](#functionelement-join) · [`lateral()`](#functionelement-lateral) · [`monotonic`](#functionelement-monotonic) · [`named_with_column`](#functionelement-named-with-column) · [`options()`](#functionelement-options) · [`outerjoin()`](#functionelement-outerjoin) · [`over()`](#functionelement-over) · [`packagenames`](#functionelement-packagenames) · [`replace_selectable()`](#functionelement-replace-selectable) · [`scalar_table_valued()`](#functionelement-scalar-table-valued) · [`schema`](#functionelement-schema) · [`select()`](#functionelement-select) · [`selectable`](#functionelement-selectable) · [`table_valued()`](#functionelement-table-valued) · [`tablesample()`](#functionelement-tablesample) · [`with_cols()`](#functionelement-with-cols) · [`within_group()`](#functionelement-within-group) · [`within_group_type()`](#functionelement-within-group-type)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## `GenericFunction` { #genericfunction }

```python
from sqlalchemy.sql.functions import GenericFunction
```

"চেনা" ফাংশনের মূল ক্লাস। সাবক্লাস বানালেই সেটি **নিজে থেকে** `func`-এ নিবন্ধিত হয় (ক্লাসের নাম ছোট হাতে, বা `identifier` দিয়ে), আর নির্দিষ্ট ফলের টাইপ পায়। নিজের প্রজেক্টের বারবার ব্যবহৃত ডেটাবেস ফাংশনকে টাইপসহ `func`-এ আনার সেরা উপায়।

**উদাহরণ:**

```python
class money(GenericFunction):
    type = String()
    identifier = "money"        # func.money(...) নামে পাওয়া যাবে
    name = "to_char"            # SQL-এ আসল নাম
    inherit_cache = True

print(func.money(Sale.amount, "FM9999"))                       # to_char(sales.amount, :to_char_1)
print(session.scalar(select(func.money(Sale.amount, "FM9999")).where(Sale.id == 2)))   # 250
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #genericfunction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`coerce_arguments`](#genericfunction-coerce-arguments) | অ্যাট্রিবিউট | `True` (ডিফল্ট) হলে আর্গুমেন্টগুলো SQL এক্সপ্রেশনে রূপান্তর হয় (Python মান → bound parameter)। |
| [`identifier`](#genericfunction-identifier) | অ্যাট্রিবিউট | (ক্লাস অ্যাট্রিবিউট, প্রতিটি সাবক্লাসে) `func.` এর পরে কোন নামে এই ফাংশন পাওয়া যাবে। |
| [`name`](#genericfunction-name) | অ্যাট্রিবিউট | SQL-এ বসা ফাংশনের নাম (না দিলে `identifier`-এর সমান)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১১৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `GenericFunction`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FunctionElement` থেকে:** [`aggregate_order_by()`](#functionelement-aggregate-order-by) · [`alias()`](#functionelement-alias) · [`as_comparison()`](#functionelement-as-comparison) · [`c`](#functionelement-c) · [`clauses`](#functionelement-clauses) · [`column_valued()`](#functionelement-column-valued) · [`columns`](#functionelement-columns) · [`corresponding_column()`](#functionelement-corresponding-column) · [`execution_options()`](#functionelement-execution-options) · [`exported_columns`](#functionelement-exported-columns) · [`filter()`](#functionelement-filter) · [`get_execution_options()`](#functionelement-get-execution-options) · [`is_delete`](#functionelement-is-delete) · [`is_derived_from()`](#functionelement-is-derived-from) · [`is_from_statement`](#functionelement-is-from-statement) · [`is_insert`](#functionelement-is-insert) · [`is_select`](#functionelement-is-select) · [`is_text`](#functionelement-is-text) · [`is_update`](#functionelement-is-update) · [`join()`](#functionelement-join) · [`lateral()`](#functionelement-lateral) · [`monotonic`](#functionelement-monotonic) · [`named_with_column`](#functionelement-named-with-column) · [`options()`](#functionelement-options) · [`outerjoin()`](#functionelement-outerjoin) · [`over()`](#functionelement-over) · [`packagenames`](#functionelement-packagenames) · [`replace_selectable()`](#functionelement-replace-selectable) · [`scalar_table_valued()`](#functionelement-scalar-table-valued) · [`schema`](#functionelement-schema) · [`select()`](#functionelement-select) · [`selectable`](#functionelement-selectable) · [`table_valued()`](#functionelement-table-valued) · [`tablesample()`](#functionelement-tablesample) · [`with_cols()`](#functionelement-with-cols) · [`within_group()`](#functionelement-within-group) · [`within_group_type()`](#functionelement-within-group-type)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `GenericFunction.coerce_arguments` { #genericfunction-coerce-arguments }

**ধরন:** অ্যাট্রিবিউট

`True` (ডিফল্ট) হলে আর্গুমেন্টগুলো SQL এক্সপ্রেশনে রূপান্তর হয় (Python মান → bound parameter)। সাবক্লাসে বদলানো যায়।

**উদাহরণ:**

```python
print(GenericFunction.coerce_arguments)   # True
```

### `GenericFunction.identifier` { #genericfunction-identifier }

**ধরন:** অ্যাট্রিবিউট

(ক্লাস অ্যাট্রিবিউট, প্রতিটি সাবক্লাসে) `func.` এর পরে কোন নামে এই ফাংশন পাওয়া যাবে। না দিলে `name`, সেটাও না থাকলে ক্লাসের নাম। তাই SQL-এর নাম (`name`) আর `func.`-এর নাম আলাদা রাখতে চাইলে দুটোই দিন।

**উদাহরণ:**

```python
from sqlalchemy.sql import functions as F
print(F.count.identifier, F.aggregate_strings.identifier)   # count aggregate_strings
```

### `GenericFunction.name` { #genericfunction-name }

**ধরন:** অ্যাট্রিবিউট

SQL-এ বসা ফাংশনের নাম (না দিলে `identifier`-এর সমান)।

**উদাহরণ:**

```python
print(func.count().name, func.char_length("x").name)   # count char_length
```

## তৈরি-করা ফাংশনের ভিত্তি-ক্লাস { #ansifunction-group }

## `AnsiFunction` { #ansifunction }

```python
from sqlalchemy.sql.functions import AnsiFunction
```

ANSI SQL-এর যেসব ফাংশন **বন্ধনী ছাড়া** লেখা হয় (`CURRENT_DATE`, `CURRENT_TIMESTAMP`, `LOCALTIME` …) তাদের ভিত্তি। নিজের এমন ফাংশন বানাতে সাবক্লাস করুন।

**উদাহরণ:**

```python
print(func.current_date(), isinstance(func.current_date(), AnsiFunction))   # CURRENT_DATE True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `ReturnTypeFromArgs` { #returntypefromargs }

```python
from sqlalchemy.sql.functions import ReturnTypeFromArgs
```

যে ফাংশনের ফলের টাইপ **প্রথম আর্গুমেন্টের** টাইপের সমান (`max`, `min`, `sum`, `coalesce` …)। যেমন `func.max(Sale.sold_at)`-এর টাইপ `Date`, তাই রেজাল্টে `datetime.date` আসে।

**উদাহরণ:**

```python
print(func.max(Sale.sold_at).type, func.sum(Sale.amount).type)   # DATE INTEGER
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `ReturnTypeFromOptionalArgs` { #returntypefromoptionalargs }

```python
from sqlalchemy.sql.functions import ReturnTypeFromOptionalArgs
```

`ReturnTypeFromArgs`-এর মতো, কিন্তু ফল NULL হতে পারে বলে টাইপ চেকারে `Optional` হিসেবে ধরা হয় (`coalesce`-এর ভিত্তি)।

**উদাহরণ:**

```python
print(func.coalesce(Sale.qty, 0).type)   # INTEGER
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `OrderedSetAgg` { #orderedsetagg }

```python
from sqlalchemy.sql.functions import OrderedSetAgg
```

"ordered-set aggregate"-এর ভিত্তি (`percentile_cont`, `percentile_disc`, `mode`): `within_group(...)` দিয়ে ব্যবহার করতে হয়, আর ফলের টাইপ WITHIN GROUP-এর এক্সপ্রেশন থেকে আসে।

**উদাহরণ:**

```python
print(func.mode().within_group(Sale.product).type)   # VARCHAR
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #orderedsetagg-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`array_for_multi_clause`](#orderedsetagg-array-for-multi-clause) | অ্যাট্রিবিউট | `True` হলে একাধিক আর্গুমেন্ট (যেমন `percentile_cont([0.25, 0.5])`) দিলে ফল একটি ARRAY হয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১১৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `OrderedSetAgg`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FunctionElement` থেকে:** [`aggregate_order_by()`](#functionelement-aggregate-order-by) · [`alias()`](#functionelement-alias) · [`as_comparison()`](#functionelement-as-comparison) · [`c`](#functionelement-c) · [`clauses`](#functionelement-clauses) · [`column_valued()`](#functionelement-column-valued) · [`columns`](#functionelement-columns) · [`corresponding_column()`](#functionelement-corresponding-column) · [`execution_options()`](#functionelement-execution-options) · [`exported_columns`](#functionelement-exported-columns) · [`filter()`](#functionelement-filter) · [`get_execution_options()`](#functionelement-get-execution-options) · [`is_delete`](#functionelement-is-delete) · [`is_derived_from()`](#functionelement-is-derived-from) · [`is_from_statement`](#functionelement-is-from-statement) · [`is_insert`](#functionelement-is-insert) · [`is_select`](#functionelement-is-select) · [`is_text`](#functionelement-is-text) · [`is_update`](#functionelement-is-update) · [`join()`](#functionelement-join) · [`lateral()`](#functionelement-lateral) · [`monotonic`](#functionelement-monotonic) · [`named_with_column`](#functionelement-named-with-column) · [`options()`](#functionelement-options) · [`outerjoin()`](#functionelement-outerjoin) · [`over()`](#functionelement-over) · [`packagenames`](#functionelement-packagenames) · [`replace_selectable()`](#functionelement-replace-selectable) · [`scalar_table_valued()`](#functionelement-scalar-table-valued) · [`schema`](#functionelement-schema) · [`select()`](#functionelement-select) · [`selectable`](#functionelement-selectable) · [`table_valued()`](#functionelement-table-valued) · [`tablesample()`](#functionelement-tablesample) · [`with_cols()`](#functionelement-with-cols) · [`within_group()`](#functionelement-within-group) · [`within_group_type()`](#functionelement-within-group-type)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`GenericFunction` থেকে:** [`coerce_arguments`](#genericfunction-coerce-arguments) · [`identifier`](#genericfunction-identifier) · [`name`](#genericfunction-name)

///

### `OrderedSetAgg.array_for_multi_clause` { #orderedsetagg-array-for-multi-clause }

**ধরন:** অ্যাট্রিবিউট

`True` হলে একাধিক আর্গুমেন্ট (যেমন `percentile_cont([0.25, 0.5])`) দিলে ফল একটি ARRAY হয়।

**উদাহরণ:**

```python
q = func.percentile_cont([0.25, 0.75]).within_group(Sale.amount)
print(one(q))   # [100.0, 250.0]
```

## `CollectionAggregateFunction` { #collectionaggregatefunction }

```python
from sqlalchemy.sql.functions import CollectionAggregateFunction
```

(২.১-এ নতুন) `func.any_()`, `func.all_()`, `func.some()`-এর ভিত্তি: `ANY(...)`/`ALL(...)`/`SOME(...)` ফাংশন রূপে।

**উদাহরণ:**

```python
print(isinstance(func.any_(column("a")), CollectionAggregateFunction))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## তৈরি-করা ফাংশন (func.xxx) { #func-count-group }

## `func.count()` { #func-count }

```python
from sqlalchemy import func
```

`COUNT`: রো গোনে। আর্গুমেন্ট না দিলে `count(*)`; কলাম দিলে সেই কলামের NULL নয় এমন মান গোনে। ফল `Integer`।

**উদাহরণ:**

```python
print(session.scalar(select(func.count()).select_from(Sale)), one(func.count(Sale.qty)))   # 5 4  (একটি qty NULL)
print(select(func.count()).select_from(Sale))          # SELECT count(*) AS count_1 FROM sales
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.sum()` { #func-sum }

```python
from sqlalchemy import func
```

`SUM`: যোগফল (NULL বাদ দিয়ে)। কোনো রো না থাকলে NULL, তাই প্রয়োজনে `func.coalesce(func.sum(x), 0)`।

**উদাহরণ:**

```python
print(one(func.sum(Sale.qty)))                                          # 16
print(session.scalar(select(func.coalesce(func.sum(Sale.amount), 0)).where(Sale.id > 99)))   # 0
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromArgs`](#returntypefromargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.max()` { #func-max }

```python
from sqlalchemy import func
```

`MAX`: সর্বোচ্চ মান; ফলের টাইপ আর্গুমেন্টের মতো।

**উদাহরণ:**

```python
print(one(func.max(Sale.amount)), one(func.max(Sale.sold_at)))   # 300 2024-03-01
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromArgs`](#returntypefromargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.min()` { #func-min }

```python
from sqlalchemy import func
```

`MIN`: সর্বনিম্ন মান।

**উদাহরণ:**

```python
print(one(func.min(Sale.amount)))   # 50
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromArgs`](#returntypefromargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.coalesce()` { #func-coalesce }

```python
from sqlalchemy import func
```

`COALESCE(a, b, ...)`: প্রথম যে মানটি NULL নয় সেটি। NULL-এর জায়গায় ডিফল্ট মান দেখাতে।

**উদাহরণ:**

```python
print(session.scalars(select(func.coalesce(Sale.qty, 0)).order_by(Sale.id)).all())   # [2, 5, 3, 0, 6]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromOptionalArgs`](#returntypefromoptionalargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.concat()` { #func-concat }

```python
from sqlalchemy import func
```

`CONCAT(a, b, ...)`: স্ট্রিং জোড়া লাগায়; NULL-কে খালি স্ট্রিং ধরে (PostgreSQL-এ)। `||` অপারেটরে (`a + b`) কোনো একটি NULL হলে পুরো ফল NULL হয়, পার্থক্যটা মনে রাখুন।

**উদাহরণ:**

```python
print(session.scalar(select(func.concat(Sale.region, "-", Sale.product)).where(Sale.id == 3)))   # চট্টগ্রাম-কলম
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.char_length()` { #func-char-length }

```python
from sqlalchemy import func
```

`CHAR_LENGTH`: স্ট্রিংয়ের অক্ষর-সংখ্যা (বাইট নয়)।

**উদাহরণ:**

```python
print(one(func.char_length("hello")))   # 5
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.aggregate_strings()` { #func-aggregate-strings }

```python
from sqlalchemy import func
```

(২.০.২১-এ নতুন) কয়েকটি রো-র স্ট্রিং একটি বিভাজক দিয়ে জোড়া লাগায়; ডেটাবেস-ভেদে সঠিক ফাংশন বসায় (PostgreSQL `string_agg`, MySQL/SQLite `group_concat`, Oracle `LISTAGG`)। ক্রম ঠিক করতে `.aggregate_order_by()` (২.১)।

**উদাহরণ:**

```python
agg = func.aggregate_strings(Sale.product, ", ").aggregate_order_by(Sale.id)
print(session.scalar(select(agg).where(Sale.region == "ঢাকা")))   # কলম, খাতা, কলম
print(func.aggregate_strings(Sale.product, ",").compile(dialect=postgresql.dialect()))
# string_agg(sales.product, __[POSTCOMPILE_aggregate_strings_1])  (বিভাজক চালানোর সময় সরাসরি বসে)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.array_agg()` { #func-array-agg }

```python
from sqlalchemy import func
```

`ARRAY_AGG`: রো-গুলোর মান একটি অ্যারেতে জড়ো করে; ফলের টাইপ `ARRAY`, তাই index/slice করা যায়। PostgreSQL-নির্দিষ্ট অপারেটর চাইলে `sqlalchemy.dialects.postgresql.array_agg`।

**উদাহরণ:**

```python
stmt = select(Sale.region, func.array_agg(Sale.amount).aggregate_order_by(Sale.amount)).group_by(Sale.region).order_by(Sale.region)
print(rows(stmt))   # [('চট্টগ্রাম', [50, 150]), ('ঢাকা', [100, 250, 300])]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromArgs`](#returntypefromargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.random()` { #func-random }

```python
from sqlalchemy import func
```

`RANDOM()`: র‍্যান্ডম সংখ্যা; সাধারণত র‍্যান্ডম ক্রমে সাজাতে `order_by(func.random())` (বড় টেবিলে ধীর)।

**উদাহরণ:**

```python
print(len(session.scalars(select(Sale.id).order_by(func.random()).limit(2)).all()))   # 2
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.pow()` { #func-pow }

```python
from sqlalchemy import func
```

(২.১-এ নতুন) `POW(x, y)`: ঘাত (x^y); ফলের টাইপ আর্গুমেন্টের মতো।

**উদাহরণ:**

```python
print(one(func.pow(2, 10)))   # 1024.0
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ReturnTypeFromArgs`](#returntypefromargs)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.next_value()` { #func-next-value }

```python
from sqlalchemy import func
```

একটি `Sequence`-এর পরের মান; ডেটাবেস-ভেদে সঠিক SQL বসায় (PostgreSQL `nextval('...')`)। sequence সমর্থন না করা ডেটাবেসে এরর।

**উদাহরণ:**

```python
print(one(func.next_value(order_seq)), one(func.next_value(order_seq)))   # 1 2
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.now()` { #func-now }

```python
from sqlalchemy import func
```

বর্তমান তারিখ-সময় (PostgreSQL `now()`; অন্য ডেটাবেসে সমতুল্য)। ফল `DateTime`। টাইমস্ট্যাম্প কলামের `server_default=func.now()` হিসেবে খুব প্রচলিত।

**উদাহরণ:**

```python
print(type(one(func.now())).__name__)   # datetime
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.current_date()` { #func-current-date }

```python
from sqlalchemy import func
```

ANSI `CURRENT_DATE` (বন্ধনী ছাড়া বসে): আজকের তারিখ।

**উদাহরণ:**

```python
print(one(func.current_date()) == datetime.date.today())   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.current_time()` { #func-current-time }

```python
from sqlalchemy import func
```

ANSI `CURRENT_TIME`: বর্তমান সময় (টাইমজোনসহ)।

**উদাহরণ:**

```python
print(func.current_time(), type(one(func.current_time())).__name__)   # CURRENT_TIME time
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.current_timestamp()` { #func-current-timestamp }

```python
from sqlalchemy import func
```

ANSI `CURRENT_TIMESTAMP`: বর্তমান তারিখ-সময় (ট্রানজ্যাকশন শুরুর সময়)।

**উদাহরণ:**

```python
print(func.current_timestamp())   # CURRENT_TIMESTAMP
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.localtime()` { #func-localtime }

```python
from sqlalchemy import func
```

ANSI `LOCALTIME`: বর্তমান সময়, টাইমজোন ছাড়া।

**উদাহরণ:**

```python
print(func.localtime(), type(one(func.localtime())).__name__)   # LOCALTIME time
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.localtimestamp()` { #func-localtimestamp }

```python
from sqlalchemy import func
```

ANSI `LOCALTIMESTAMP`: বর্তমান তারিখ-সময়, টাইমজোন ছাড়া।

**উদাহরণ:**

```python
print(one(func.localtimestamp()).tzinfo)   # None
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.sysdate()` { #func-sysdate }

```python
from sqlalchemy import func
```

`SYSDATE`: Oracle/MySQL-এর বর্তমান তারিখ-সময়। PostgreSQL-এ এই ফাংশন নেই; সেখানে `func.now()`।

**উদাহরণ:**

```python
print(func.sysdate())   # sysdate
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.current_user()` { #func-current-user }

```python
from sqlalchemy import func
```

ANSI `CURRENT_USER`: যে ডেটাবেস ইউজার হিসেবে কুয়েরি চলছে।

**উদাহরণ:**

```python
print(one(func.current_user()))   # postgres
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.session_user()` { #func-session-user }

```python
from sqlalchemy import func
```

ANSI `SESSION_USER`: কানেকশন যে ইউজারে লগইন করেছে (`SET ROLE` করলেও বদলায় না)।

**উদাহরণ:**

```python
print(one(func.session_user()))   # postgres
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.user()` { #func-user }

```python
from sqlalchemy import func
```

ANSI `USER` (`CURRENT_USER`-এর সমার্থক)।

**উদাহরণ:**

```python
print(one(func.user()))   # postgres
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AnsiFunction`](#ansifunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.rollup()` { #func-rollup }

```python
from sqlalchemy import func
```

`GROUP BY ROLLUP(a, b)`: প্রতিটি গ্রুপের যোগফলের সাথে উপ-মোট আর সর্বমোট রো-ও দেয় (রিপোর্টে খুব কাজের)। উপ-মোটের রো-তে গ্রুপ কলাম NULL থাকে।

**উদাহরণ:**

```python
stmt = (select(Sale.region, func.sum(Sale.amount)).group_by(func.rollup(Sale.region))
        .order_by(Sale.region.nulls_last()))
print(rows(stmt))   # [('চট্টগ্রাম', 200), ('ঢাকা', 650), (None, 850)]  (শেষটি সর্বমোট)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.cube()` { #func-cube }

```python
from sqlalchemy import func
```

`GROUP BY CUBE(a, b)`: দেওয়া কলামগুলোর **সব** সম্ভাব্য মিশ্রণে উপ-মোট (a একা, b একা, দুটো একসাথে, সর্বমোট)।

**উদাহরণ:**

```python
stmt = select(Sale.region, Sale.product, func.sum(Sale.amount)).group_by(func.cube(Sale.region, Sale.product))
print(len(rows(stmt)))   # 9  (৪টি region×product + ২ region + ২ product + ১ সর্বমোট)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.grouping_sets()` { #func-grouping-sets }

```python
from sqlalchemy import func
```

`GROUP BY GROUPING SETS(...)`: ঠিক কোন কোন গ্রুপিং চাই তা নিজে বলে দেওয়া। একাধিক কলামের সেট দিতে `tuple_()`।

**উদাহরণ:**

```python
stmt = select(Sale.region, Sale.product, func.sum(Sale.amount)).group_by(
    func.grouping_sets(Sale.region, Sale.product))
print(len(rows(stmt)))   # 4  (২টি region + ২টি product)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.rank()` { #func-rank }

```python
from sqlalchemy import func
```

`RANK()`: সাধারণত window function হিসেবে (`.over(order_by=...)`): সমান মানে একই র‍্যাংক, পরের র‍্যাংকে ফাঁক থাকে (১, ২, ২, ৪)। `within_group()` দিয়ে "hypothetical-set aggregate" হিসেবেও: "এই মানটি থাকলে কততম হতো"।

**উদাহরণ:**

```python
rk = func.rank().over(order_by=Sale.product)
print(session.scalars(select(rk).order_by(Sale.product, Sale.id)).all())   # [1, 1, 1, 4, 4]
print(one(func.rank(200).within_group(Sale.amount.desc())))                 # 3
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.dense_rank()` { #func-dense-rank }

```python
from sqlalchemy import func
```

`DENSE_RANK()`: `rank()`-এর মতো, কিন্তু ফাঁক ছাড়া (১, ১, ২, ৩)।

**উদাহরণ:**

```python
dr = func.dense_rank().over(order_by=Sale.product)
print(session.scalars(select(dr).order_by(Sale.product, Sale.id)).all())   # [1, 1, 1, 2, 2]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.percent_rank()` { #func-percent-rank }

```python
from sqlalchemy import func
```

`PERCENT_RANK()`: আপেক্ষিক র‍্যাংক ০ থেকে ১-এর মধ্যে: `(rank - 1) / (মোট রো - 1)`।

**উদাহরণ:**

```python
pr = func.percent_rank().over(order_by=Sale.amount)
print([float(x) for x in session.scalars(select(pr).order_by(Sale.amount))])   # [0.0, 0.25, 0.5, 0.75, 1.0]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.cume_dist()` { #func-cume-dist }

```python
from sqlalchemy import func
```

`CUME_DIST()`: ক্রমযোজিত বণ্টন: এই রো বা তার আগের রো-গুলো মোটের কত ভাগ (০-এর বেশি থেকে ১)।

**উদাহরণ:**

```python
cd = func.cume_dist().over(order_by=Sale.amount)
print([float(x) for x in session.scalars(select(cd).order_by(Sale.amount))])   # [0.2, 0.4, 0.6, 0.8, 1.0]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.percentile_cont()` { #func-percentile-cont }

```python
from sqlalchemy import func
```

`PERCENTILE_CONT(p) WITHIN GROUP (ORDER BY x)`: অবিচ্ছিন্ন percentile; দরকারে দুই মানের মাঝে interpolate করে। ০.৫ দিলে median (মধ্যমা)। তালিকা দিলে কয়েকটি percentile একসাথে (ARRAY)।

**উদাহরণ:**

```python
print(one(func.percentile_cont(0.5).within_group(Sale.amount)))    # 150.0  (median)
print(one(func.percentile_cont(0.9).within_group(Sale.amount)))    # 280.0  (interpolated)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`OrderedSetAgg`](#orderedsetagg-summary)-এর মতো।

## `func.percentile_disc()` { #func-percentile-disc }

```python
from sqlalchemy import func
```

`PERCENTILE_DISC(p) WITHIN GROUP (ORDER BY x)`: বিচ্ছিন্ন percentile; সবসময় ডেটার একটি আসল মান দেয় (interpolate করে না)।

**উদাহরণ:**

```python
print(one(func.percentile_disc(0.9).within_group(Sale.amount)))   # 300
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`OrderedSetAgg`](#orderedsetagg-summary)-এর মতো।

## `func.mode()` { #func-mode }

```python
from sqlalchemy import func
```

`MODE() WITHIN GROUP (ORDER BY x)`: সবচেয়ে বেশিবার আসা মান।

**উদাহরণ:**

```python
print(one(func.mode().within_group(Sale.product)))   # কলম
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`OrderedSetAgg`](#orderedsetagg-summary)-এর মতো।

## `func.any_()` { #func-any }

```python
from sqlalchemy import func
```

(২.১-এ নতুন) `ANY(...)` ফাংশন রূপে: তুলনার ডান দিকে অ্যারে বা সাবকুয়েরি। স্বতন্ত্র [`any_()`](expressions.md#any-func) এক্সপ্রেশনের ফাংশন-সংস্করণ।

**উদাহরণ:**

```python
amounts = cast([100, 300], postgresql.ARRAY(Integer))
print(session.scalars(select(Sale.id).where(Sale.amount == func.any_(amounts)).order_by(Sale.id)).all())   # [1, 5]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CollectionAggregateFunction`](#collectionaggregatefunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.all_()` { #func-all }

```python
from sqlalchemy import func
```

(২.১-এ নতুন) `ALL(...)` ফাংশন রূপে: অ্যারের **সব** মানের সাথে তুলনা সত্য হতে হবে।

**উদাহরণ:**

```python
limits = cast([120, 200], postgresql.ARRAY(Integer))
print(session.scalars(select(Sale.id).where(Sale.amount > func.all_(limits)).order_by(Sale.id)).all())   # [2, 5]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CollectionAggregateFunction`](#collectionaggregatefunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## `func.some()` { #func-some }

```python
from sqlalchemy import func
```

(২.১-এ নতুন) `SOME(...)`: SQL স্ট্যান্ডার্ডে `ANY`-এর সমার্থক।

**উদাহরণ:**

```python
amounts = cast([50, 150], postgresql.ARRAY(Integer))
print(session.scalars(select(Sale.id).where(Sale.amount == func.some(amounts)).order_by(Sale.id)).all())   # [3, 4]
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CollectionAggregateFunction`](#collectionaggregatefunction)-এর মতো, অর্থাৎ [`GenericFunction`](#genericfunction-summary)-এর মতো।

## window ও aggregate সহায়ক { #over-func-group }

## `over()` { #over-func }

```python
from sqlalchemy import over
```

```python
over(element, partition_by=None, order_by=None, range_=None, rows=None, groups=None, exclude=None)
```

**ধরন:** ফাংশন

একটি ফাংশনকে window function বানায়; `func.xxx().over(...)` মেথডের ফাংশন রূপ। frame (`rows`, `range_`, `groups`) দেওয়া হয় `(শুরু, শেষ)` tuple দিয়ে: `None` = সীমাহীন, `0` = বর্তমান রো, ঋণাত্মক = আগের, ধনাত্মক = পরের।

**উদাহরণ:**

```python
running = over(func.sum(Sale.amount), order_by=Sale.id, rows=(None, 0))
print(session.scalars(select(running).order_by(Sale.id)).all())   # [100, 350, 500, 550, 850]  (চলমান যোগফল)
```

### `over()`-এর সব প্যারামিটার { #over-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে ফাংশনকে window বানানো হবে। |
| `partition_by` | `PARTITION BY`: কোন কলাম অনুযায়ী আলাদা আলাদা দলে হিসাব হবে। |
| `order_by` | `ORDER BY`: দলের ভেতরে ক্রম। |
| `range_` | `RANGE BETWEEN ...` frame (মানের দূরত্ব অনুযায়ী)। |
| `rows` | `ROWS BETWEEN ...` frame (রো-সংখ্যা অনুযায়ী)। |
| `groups` | (২.০.৪০-এ নতুন) `GROUPS BETWEEN ...` frame (সমান মানের দল অনুযায়ী)। |
| `exclude` | (২.১-এ নতুন) frame থেকে বাদ: `"CURRENT ROW"`, `"GROUP"`, `"TIES"` বা `"NO OTHERS"`; `rows`/`range_`/`groups`-এর সাথে দিতে হয়। |

**আগের ১টি আর পরের ১টি রো মিলিয়ে চলমান গড়, আর নিজের রো বাদ দিয়ে (২.১-এর exclude)**

```python
avg3 = func.avg(Sale.amount).over(order_by=Sale.id, rows=(-1, 1))
print([round(x) for x in session.scalars(select(avg3).order_by(Sale.id))])   # [175, 167, 150, 167, 175]
others = func.sum(Sale.amount).over(order_by=Sale.id, rows=(None, None), exclude="CURRENT ROW")
print(session.scalars(select(others).order_by(Sale.id)).all())               # [750, 600, 700, 800, 550]
```

## `within_group()` { #within-group-func }

```python
from sqlalchemy import within_group
```

```python
within_group(element, *order_by)
```

**ধরন:** ফাংশন

`func.xxx().within_group(...)`-এর ফাংশন রূপ: ordered-set aggregate-এ `WITHIN GROUP (ORDER BY ...)`।

**উদাহরণ:**

```python
print(one(within_group(func.percentile_disc(0.5), Sale.amount)))   # 150
```

### `within_group()`-এর সব প্যারামিটার { #within-group-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | ফাংশন। |
| `order_by` | WITHIN GROUP-এর ভেতরের ORDER BY এক্সপ্রেশন(গুলো)। |

## `funcfilter()` { #funcfilter }

```python
from sqlalchemy import funcfilter
```

```python
funcfilter(func, *criterion)
```

**ধরন:** ফাংশন

`func.xxx().filter(...)`-এর ফাংশন রূপ: aggregate-এ `FILTER (WHERE ...)`।

**উদাহরণ:**

```python
print(one(funcfilter(func.count(Sale.id), Sale.qty.is_(None))))   # 1
```

### `funcfilter()`-এর সব প্যারামিটার { #funcfilter-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `func` | aggregate ফাংশন। |
| `criterion` | শর্ত(গুলো)। |

## `aggregate_order_by()` { #aggregate-order-by-func }

```python
from sqlalchemy import aggregate_order_by
```

```python
aggregate_order_by(element, *order_by)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) `func.xxx().aggregate_order_by(...)`-এর ফাংশন রূপ: aggregate-এর ভেতরে `ORDER BY` (আগে শুধু PostgreSQL ডায়ালেক্টে ছিল, এখন সাধারণ)।

**উদাহরণ:**

```python
agg = aggregate_order_by(func.array_agg(Sale.id), Sale.amount.desc())
print(one(agg))   # [5, 2, 3, 1, 4]
```

### `aggregate_order_by()`-এর সব প্যারামিটার { #aggregate-order-by-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | aggregate ফাংশন। |
| `order_by` | ভেতরের ORDER BY এক্সপ্রেশন(গুলো)। |

## `Over` { #over }

```python
from sqlalchemy.sql.expression import Over
```

`.over()` / `over()`-এর ফল: `ফাংশন OVER (...)`।

**উদাহরণ:**

```python
o = func.row_number().over(partition_by=Sale.region, order_by=Sale.id)
print(type(o).__name__, o)   # Over row_number() OVER (PARTITION BY sales.region ORDER BY sales.id)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #over-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`element`](#over-element) | অ্যাট্রিবিউট | যে ফাংশন window করা হয়েছে। |
| [`exclude`](#over-exclude) | অ্যাট্রিবিউট | (২.১) frame-এর EXCLUDE অংশ (না দিলে `None`)। |
| [`groups`](#over-groups) | অ্যাট্রিবিউট | `GROUPS` frame (একটি `FrameClause`, না দিলে `None`)। |
| [`order_by`](#over-order-by) | অ্যাট্রিবিউট | window-এর ORDER BY এক্সপ্রেশন (`ClauseList`, না দিলে `None`)। |
| [`partition_by`](#over-partition-by) | অ্যাট্রিবিউট | window-এর PARTITION BY এক্সপ্রেশন। |
| [`range_`](#over-range-) | অ্যাট্রিবিউট | `RANGE` frame (না দিলে `None`)। |
| [`rows`](#over-rows) | অ্যাট্রিবিউট | `ROWS` frame (না দিলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Over`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `Over.element` { #over-element }

**ধরন:** অ্যাট্রিবিউট

যে ফাংশন window করা হয়েছে।

**উদাহরণ:**

```python
print(func.rank().over(order_by=Sale.id).element)   # rank()
```

### `Over.exclude` { #over-exclude }

**ধরন:** অ্যাট্রিবিউট

(২.১) frame-এর EXCLUDE অংশ (না দিলে `None`)।

**উদাহরণ:**

```python
print(func.sum(Sale.amount).over(rows=(None, None), exclude="TIES").exclude)   # TIES
```

### `Over.groups` { #over-groups }

**ধরন:** অ্যাট্রিবিউট

`GROUPS` frame (একটি `FrameClause`, না দিলে `None`)।

**উদাহরণ:**

```python
print(func.sum(Sale.amount).over(order_by=Sale.qty, groups=(-1, 0)).groups is not None)   # True
```

### `Over.order_by` { #over-order-by }

**ধরন:** অ্যাট্রিবিউট

window-এর ORDER BY এক্সপ্রেশন (`ClauseList`, না দিলে `None`)।

**উদাহরণ:**

```python
print(func.rank().over(order_by=Sale.amount.desc()).order_by)   # sales.amount DESC
```

### `Over.partition_by` { #over-partition-by }

**ধরন:** অ্যাট্রিবিউট

window-এর PARTITION BY এক্সপ্রেশন।

**উদাহরণ:**

```python
print(func.rank().over(partition_by=Sale.region).partition_by)   # sales.region
```

### `Over.range_` { #over-range- }

**ধরন:** অ্যাট্রিবিউট

`RANGE` frame (না দিলে `None`)।

**উদাহরণ:**

```python
print(func.sum(Sale.amount).over(order_by=Sale.amount, range_=(-100, 0)).range_ is not None)   # True
```

### `Over.rows` { #over-rows }

**ধরন:** অ্যাট্রিবিউট

`ROWS` frame (না দিলে `None`)।

**উদাহরণ:**

```python
print(func.sum(Sale.amount).over(rows=(None, 0)).rows is not None)   # True
```

## `WithinGroup` { #withingroup }

```python
from sqlalchemy.sql.expression import WithinGroup
```

`.within_group()`-এর ফল: `ফাংশন WITHIN GROUP (ORDER BY ...)`।

**উদাহরণ:**

```python
w = func.mode().within_group(Sale.product)
print(type(w).__name__, w)   # WithinGroup mode() WITHIN GROUP (ORDER BY sales.product)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #withingroup-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`element`](#withingroup-element) | অ্যাট্রিবিউট | ভেতরের ফাংশন। |
| [`filter()`](#withingroup-filter) | মেথড | এর ওপর `FILTER (WHERE ...)` বসায়। |
| [`order_by`](#withingroup-order-by) | অ্যাট্রিবিউট | WITHIN GROUP-এর ORDER BY এক্সপ্রেশন। |
| [`over()`](#withingroup-over) | মেথড | এর ওপর `OVER (...)` বসায় (যেসব ডেটাবেস ordered-set aggregate-কে window হিসেবে সমর্থন করে; PostgreSQL করে না)। |
| [`wrapped_column_expression`](#withingroup-wrapped-column-expression) | প্রপার্টি (internal) | কলাম-নাম/লেবেল ঠিক করতে যে মূল এক্সপ্রেশন ধরা হয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `WithinGroup`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `WithinGroup.element` { #withingroup-element }

**ধরন:** অ্যাট্রিবিউট

ভেতরের ফাংশন।

**উদাহরণ:**

```python
print(func.mode().within_group(Sale.product).element)   # mode()
```

### `WithinGroup.filter()` { #withingroup-filter }

```python
WithinGroup.filter(*criterion)
```

**ধরন:** মেথড

এর ওপর `FILTER (WHERE ...)` বসায়।

**উদাহরণ:**

```python
w = func.percentile_disc(0.5).within_group(Sale.amount).filter(Sale.region == "ঢাকা")
print(one(w))   # 250
```

### `WithinGroup.order_by` { #withingroup-order-by }

**ধরন:** অ্যাট্রিবিউট

WITHIN GROUP-এর ORDER BY এক্সপ্রেশন।

**উদাহরণ:**

```python
print(func.mode().within_group(Sale.product).order_by)   # sales.product
```

### `WithinGroup.over()` { #withingroup-over }

```python
WithinGroup.over(*, partition_by=None, order_by=None, rows=None, range_=None, groups=None, exclude=None)
```

**ধরন:** মেথড

এর ওপর `OVER (...)` বসায় (যেসব ডেটাবেস ordered-set aggregate-কে window হিসেবে সমর্থন করে; PostgreSQL করে না)।

**উদাহরণ:**

```python
print(func.percentile_cont(0.5).within_group(Sale.amount).over(partition_by=Sale.region))
# percentile_cont(:percentile_cont_1) WITHIN GROUP (ORDER BY sales.amount) OVER (PARTITION BY sales.region)
```

### `WithinGroup.wrapped_column_expression` { #withingroup-wrapped-column-expression }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলাম-নাম/লেবেল ঠিক করতে যে মূল এক্সপ্রেশন ধরা হয়।

## `FunctionFilter` { #functionfilter }

```python
from sqlalchemy.sql.expression import FunctionFilter
```

`.filter()` / `funcfilter()`-এর ফল: `ফাংশন FILTER (WHERE ...)`।

**উদাহরণ:**

```python
f = func.count(Sale.id).filter(Sale.qty > 2)
print(type(f).__name__, one(f))   # FunctionFilter 3
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #functionfilter-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`criterion`](#functionfilter-criterion) | অ্যাট্রিবিউট | FILTER-এর শর্ত। |
| [`filter()`](#functionfilter-filter) | মেথড | আরও শর্ত যোগ করে (AND)। |
| [`func`](#functionfilter-func) | অ্যাট্রিবিউট | ভেতরের aggregate ফাংশন। |
| [`over()`](#functionfilter-over) | মেথড | FILTER-যুক্ত aggregate-কে window function বানায়। |
| [`within_group()`](#functionfilter-within-group) | মেথড | এর ওপর `WITHIN GROUP (ORDER BY ...)` বসায়। |
| [`within_group_type()`](#functionfilter-within-group-type) | মেথড (internal) | WITHIN GROUP থাকলে ফলের টাইপ ঠিক করার হুক। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FunctionFilter`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `FunctionFilter.criterion` { #functionfilter-criterion }

**ধরন:** অ্যাট্রিবিউট

FILTER-এর শর্ত।

**উদাহরণ:**

```python
print(func.count(Sale.id).filter(Sale.qty > 2).criterion)   # sales.qty > :qty_1
```

### `FunctionFilter.filter()` { #functionfilter-filter }

```python
FunctionFilter.filter(*criterion)
```

**ধরন:** মেথড

আরও শর্ত যোগ করে (AND)।

**উদাহরণ:**

```python
f = func.count(Sale.id).filter(Sale.qty > 2).filter(Sale.region == "ঢাকা")
print(one(f))   # 2
```

### `FunctionFilter.func` { #functionfilter-func }

**ধরন:** অ্যাট্রিবিউট

ভেতরের aggregate ফাংশন।

**উদাহরণ:**

```python
print(func.count(Sale.id).filter(Sale.qty > 2).func)   # count(sales.id)
```

### `FunctionFilter.over()` { #functionfilter-over }

```python
FunctionFilter.over(partition_by=None, order_by=None, range_=None, rows=None, groups=None, exclude=None)
```

**ধরন:** মেথড

FILTER-যুক্ত aggregate-কে window function বানায়।

**উদাহরণ:**

```python
f = func.count(Sale.id).filter(Sale.product == "কলম").over(partition_by=Sale.region)
print(session.scalars(select(f).order_by(Sale.id)).all())   # [2, 2, 1, 1, 2]
```

### `FunctionFilter.within_group()` { #functionfilter-within-group }

```python
FunctionFilter.within_group(*order_by)
```

**ধরন:** মেথড

এর ওপর `WITHIN GROUP (ORDER BY ...)` বসায়।

**উদাহরণ:**

```python
f = func.percentile_disc(0.5).filter(Sale.region == "চট্টগ্রাম").within_group(Sale.amount)
print(f)   # percentile_disc(:percentile_disc_1) FILTER (WHERE sales.region = :region_1) WITHIN GROUP (ORDER BY sales.amount)
```

### `FunctionFilter.within_group_type()` { #functionfilter-within-group-type }

```python
FunctionFilter.within_group_type(within_group)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

WITHIN GROUP থাকলে ফলের টাইপ ঠিক করার হুক।

## `AggregateOrderBy` { #aggregateorderby }

```python
from sqlalchemy.sql.expression import AggregateOrderBy
```

(২.১-এ নতুন) `.aggregate_order_by()` / `aggregate_order_by()`-এর ফল: `ফাংশন(x ORDER BY y)`।

**উদাহরণ:**

```python
a = func.array_agg(Sale.id).aggregate_order_by(Sale.id.desc())
print(type(a).__name__, a.compile(dialect=postgresql.dialect()))   # AggregateOrderBy array_agg(sales.id ORDER BY sales.id DESC)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aggregateorderby-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`element`](#aggregateorderby-element) | অ্যাট্রিবিউট | ভেতরের aggregate ফাংশন। |
| [`filter()`](#aggregateorderby-filter) | মেথড | এর ওপর `FILTER (WHERE ...)` বসায়। |
| [`order_by`](#aggregateorderby-order-by) | অ্যাট্রিবিউট | ভেতরের ORDER BY এক্সপ্রেশন। |
| [`over()`](#aggregateorderby-over) | মেথড | এর ওপর `OVER (...)` বসায় (PostgreSQL এই মিশ্রণ সমর্থন করে না)। |
| [`wrapped_column_expression`](#aggregateorderby-wrapped-column-expression) | প্রপার্টি (internal) | কলাম-নাম/লেবেল ঠিক করতে যে মূল এক্সপ্রেশন ধরা হয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AggregateOrderBy`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `AggregateOrderBy.element` { #aggregateorderby-element }

**ধরন:** অ্যাট্রিবিউট

ভেতরের aggregate ফাংশন।

**উদাহরণ:**

```python
print(func.array_agg(Sale.id).aggregate_order_by(Sale.id).element)   # array_agg(sales.id)
```

### `AggregateOrderBy.filter()` { #aggregateorderby-filter }

```python
AggregateOrderBy.filter(*criterion)
```

**ধরন:** মেথড

এর ওপর `FILTER (WHERE ...)` বসায়।

**উদাহরণ:**

```python
a = func.array_agg(Sale.id).aggregate_order_by(Sale.amount).filter(Sale.region == "চট্টগ্রাম")
print(one(a))   # [4, 3]
```

### `AggregateOrderBy.order_by` { #aggregateorderby-order-by }

**ধরন:** অ্যাট্রিবিউট

ভেতরের ORDER BY এক্সপ্রেশন।

**উদাহরণ:**

```python
print(func.array_agg(Sale.id).aggregate_order_by(Sale.amount).order_by)   # sales.amount
```

### `AggregateOrderBy.over()` { #aggregateorderby-over }

```python
AggregateOrderBy.over(*, partition_by=None, order_by=None, rows=None, range_=None, groups=None, exclude=None)
```

**ধরন:** মেথড

এর ওপর `OVER (...)` বসায় (PostgreSQL এই মিশ্রণ সমর্থন করে না)।

**উদাহরণ:**

```python
a = func.array_agg(Sale.id).aggregate_order_by(Sale.id).over(partition_by=Sale.region)
print(a)   # array_agg(sales.id ORDER BY sales.id) OVER (PARTITION BY sales.region)
```

### `AggregateOrderBy.wrapped_column_expression` { #aggregateorderby-wrapped-column-expression }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলাম-নাম/লেবেল ঠিক করতে যে মূল এক্সপ্রেশন ধরা হয়।

/// check | সংক্ষেপে মনে রাখুন

* যেকোনো ডেটাবেস ফাংশন: `func.নাম(...)`; ফলের টাইপ জানা দরকার হলে `type_=`।
* aggregate: `count()`, `sum()`, `max()`, `min()`; NULL এড়াতে `coalesce(sum(x), 0)`।
* শর্তসাপেক্ষ aggregate: `.filter(শর্ত)`; aggregate-এর ভেতরে ক্রম: `.aggregate_order_by(...)` (২.১)।
* window: `.over(partition_by=..., order_by=..., rows=(None, 0))`; র‍্যাংক: `rank()`, `dense_rank()`, `row_number()`।
* median/percentile: `percentile_cont(0.5).within_group(col)`।
* রিপোর্টের উপ-মোট: `group_by(func.rollup(...))`।
* নিজের টাইপড ফাংশন: `class myfn(GenericFunction): type = ...; inherit_cache = True`।

///
