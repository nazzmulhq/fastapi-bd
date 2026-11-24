# Core-এর মূল ক্লাস: Executable, SelectBase, UpdateBase, quoted_name, custom_op … { #api-core-bases }

/// note | এই পেজে যা আছে

`Select`, `Insert`, `Column`, `Table` ইত্যাদির পেছনের **মূল (base) ক্লাস আর সহায়ক ক্লাস**, যাদের নাম টাইপ-হিন্টে, ডকস্ট্রিংয়ে আর এররের বার্তায় দেখা যায়:

* **স্টেটমেন্ট:** `Executable`, `ExecutableStatement`, `ReturnsRows`, `SelectBase`, `GenerativeSelect`, `HasCTE`, `HasPrefixes`, `HasSuffixes`, `UpdateBase`, `ValuesBase`, `DMLTargetCopy`, `AliasedReturnsRows`, `FromGrouping`, `ScalarValues`।
* **এক্সপ্রেশন:** `ClauseList`, `ExpressionClauseList`, `OrderByList`, `Grouping`, `TypeClause`, `TableValuedColumn`, `TString`, `FrameClause`, `FrameClauseType`, savepoint clause, `SQLColumnExpression`, `Operators`, `custom_op`, `quoted_name`, `SelectLabelStyle`, `WriteableColumnCollection`, `Visitable`, `Named`।
* **স্কিমা:** `SchemaItem`, `SchemaConst`, `ColumnCollectionMixin`, `ForeignKeyTarget`, `SchemaVisitable`, `SchemaVisitor`, `InvokeDDLBase`।
* **অন্যান্য:** `adapt_type()`, `to_instance()`, ইভেন্টের `EventTarget`, `Events`, `dispatcher`, `RefCollection`, `Inspectable`, আর `BaseRow`।

///

এদের বেশিরভাগ সদস্য আসল ক্লাসগুলোর (যেমন `Select`, `Insert`) পেজে আগেই ব্যাখ্যা করা; এখানে প্রতিটি ক্লাস **কী, কোথায় দেখা যায়, কেন জানা দরকার**, আর সদস্যগুলো লিংকসহ ভাঁজ করা বক্সে। সবচেয়ে কাজের: টাইপ-হিন্ট লিখতে (`def run(stmt: Executable)`), `quoted_name` (নামের quote নিয়ন্ত্রণ), `custom_op` (নিজের অপারেটর), আর `SelectLabelStyle`।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

`users` (`id`, `name`) আর `addresses` (`id`, `email`, `user_id`) টেবিল, SQLite মেমোরি `engine`-এ রহিম আর করিম। `pg = postgresql.dialect()` দিয়ে কম্পাইল করে দেখা।

///

## স্টেটমেন্টের মূল ক্লাস { #executable-group }

## `Executable` { #executable }

```python
from sqlalchemy.sql.expression import Executable
```

"চালানো যায়" এমন সব স্টেটমেন্টের মূল ক্লাস: `select()`, `insert()`, `update()`, `delete()`, `text()`, DDL। `connection.execute()` আর `session.execute()` এটাই নেয়। নিজের হেল্পার ফাংশনে টাইপ-হিন্ট: `def run(stmt: Executable) -> ...`। `execution_options()`, `options()` এখান থেকে আসে।

**উদাহরণ:**

```python
for s in [select(users), insert(users), update(users), delete(users), text("SELECT 1")]:
    print(type(s).__name__, isinstance(s, Executable), end=" | ")
print()
# Select True | Insert True | Update True | Delete True | TextClause True |
print(isinstance(users.c.id == 1, Executable))   # False  (একটি শর্ত একা চালানো যায় না)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #executable-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Executable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

///

## `ExecutableStatement` { #executablestatement }

```python
from sqlalchemy.sql.expression import ExecutableStatement
```

(২.১-এ নতুন) `Executable`-এর একটি subclass যা `params()`-এর হালকা (দ্রুততর) রূপ দেয়: পুরো এক্সপ্রেশন-গাছ কপি না করে শুধু bind মান বদলায়। `Select`, `Insert`, `text()` ইত্যাদি সব স্টেটমেন্ট এর থেকে আসে।

**উদাহরণ:**

```python
stmt = select(users.c.name).where(users.c.id == 1)
print(isinstance(stmt, ExecutableStatement), isinstance(text("SELECT 1"), ExecutableStatement), isinstance(users.c.id == 1, ExecutableStatement))   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #executablestatement-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ExecutableStatement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

///

## `ReturnsRows` { #returnsrows }

```python
from sqlalchemy.sql.expression import ReturnsRows
```

"রো ফেরত দেয়" এমন সব কনস্ট্রাক্টের সবচেয়ে মূল ক্লাস: `Table`, `Select`, সাবকুয়েরি, আর `RETURNING`-সহ INSERT/UPDATE/DELETE। `exported_columns` এখান থেকে।

**উদাহরণ:**

```python
print(isinstance(users, ReturnsRows), isinstance(select(users), ReturnsRows), isinstance(insert(users), ReturnsRows))   # True True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #returnsrows-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ReturnsRows`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`exported_columns`](select.md#select-exported-columns) · [`get_children()`](select.md#select-get-children) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_selectable`](select.md#select-is-selectable) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`params()`](select.md#select-params) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

## `SelectBase` { #selectbase }

```python
from sqlalchemy.sql.expression import SelectBase
```

সব SELECT-এর মূল ক্লাস: `Select`, `CompoundSelect` (UNION …), `TextualSelect` (`text().columns()`)। `subquery()`, `scalar_subquery()`, `exists()`, `cte()`, `selected_columns` এখানে। "যেকোনো SELECT" নেওয়ার ফাংশনে টাইপ-হিন্ট।

**উদাহরণ:**

```python
for s in [select(users), union(select(users), select(users)), text("SELECT id FROM users").columns(users.c.id)]:
    print(type(s).__name__, isinstance(s, SelectBase))
# Select True
# CompoundSelect True
# TextualSelect True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #selectbase-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SelectBase`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`alias()`](select.md#select-alias) · [`allows_lambda`](select.md#select-allows-lambda) · [`as_scalar()`](select.md#select-as-scalar) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`exists()`](select.md#select-exists) · [`exported_columns`](select.md#select-exported-columns) · [`get_children()`](select.md#select-get-children) · [`get_label_style()`](select.md#select-get-label-style) · [`inherit_cache`](select.md#select-inherit-cache) · [`into()`](select.md#select-into) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`label()`](select.md#select-label) · [`lateral()`](select.md#select-lateral) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`params()`](select.md#select-params) · [`replace_selectable()`](select.md#select-replace-selectable) · [`scalar_subquery()`](select.md#select-scalar-subquery) · [`selectable`](select.md#select-selectable) · [`selected_columns`](select.md#select-selected-columns) · [`self_group()`](select.md#select-self-group) · [`set_label_style()`](select.md#select-set-label-style) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`subquery()`](select.md#select-subquery) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

## `GenerativeSelect` { #generativeselect }

```python
from sqlalchemy.sql.expression import GenerativeSelect
```

যে SELECT-এ ORDER BY, LIMIT, OFFSET, FOR UPDATE, label style যোগ করা যায় তাদের মূল ক্লাস: `Select` আর `CompoundSelect` (কিন্তু `TextualSelect` নয়)।

**উদাহরণ:**

```python
u = union(select(users.c.name), select(addresses.c.email)).order_by("name").limit(5)
print(isinstance(u, GenerativeSelect), sql(u).splitlines()[-1].strip())   # True LIMIT 5
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #generativeselect-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `GenerativeSelect`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`alias()`](select.md#select-alias) · [`allows_lambda`](select.md#select-allows-lambda) · [`argument_for()`](select.md#select-argument-for) · [`as_scalar()`](select.md#select-as-scalar) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`exists()`](select.md#select-exists) · [`exported_columns`](select.md#select-exported-columns) · [`fetch()`](select.md#select-fetch) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_label_style()`](select.md#select-get-label-style) · [`group_by()`](select.md#select-group-by) · [`inherit_cache`](select.md#select-inherit-cache) · [`into()`](select.md#select-into) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`kwargs`](select.md#select-kwargs) · [`label()`](select.md#select-label) · [`lateral()`](select.md#select-lateral) · [`limit()`](select.md#select-limit) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`offset()`](select.md#select-offset) · [`order_by()`](select.md#select-order-by) · [`params()`](select.md#select-params) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`replace_selectable()`](select.md#select-replace-selectable) · [`scalar_subquery()`](select.md#select-scalar-subquery) · [`selectable`](select.md#select-selectable) · [`selected_columns`](select.md#select-selected-columns) · [`self_group()`](select.md#select-self-group) · [`set_label_style()`](select.md#select-set-label-style) · [`slice()`](select.md#select-slice) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`subquery()`](select.md#select-subquery) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_for_update()`](select.md#select-with-for-update)

///

## `HasCTE` { #hascte }

```python
from sqlalchemy.sql.expression import HasCTE
```

CTE (`WITH`) সমর্থনের মিক্সিন: `cte()` আর `add_cte()`। `Select`, `CompoundSelect`, `Insert`, `Update`, `Delete`-এ আছে।

**উদাহরণ:**

```python
print(all(isinstance(s, HasCTE) for s in [select(users), insert(users), update(users), delete(users)]))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hascte-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HasCTE`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`exported_columns`](select.md#select-exported-columns) · [`get_children()`](select.md#select-get-children) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_selectable`](select.md#select-is-selectable) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`params()`](select.md#select-params) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

## `HasPrefixes` { #hasprefixes }

```python
from sqlalchemy.sql.expression import HasPrefixes
```

`prefix_with()` মেথডের মিক্সিন: স্টেটমেন্টের শুরুর কীওয়ার্ডের পরে কিছু বসাতে (`INSERT OR IGNORE`, `SELECT SQL_NO_CACHE`)।

**উদাহরণ:**

```python
print(sql(insert(users).values(name="x").prefix_with("OR IGNORE")).split(" INTO")[0])   # INSERT OR IGNORE
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hasprefixes-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HasPrefixes`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`prefix_with()`](select.md#select-prefix-with)

///

## `HasSuffixes` { #hassuffixes }

```python
from sqlalchemy.sql.expression import HasSuffixes
```

`suffix_with()` মেথডের মিক্সিন: পুরো স্টেটমেন্টের শেষে কিছু বসাতে।

**উদাহরণ:**

```python
print(sql(select(users.c.id).suffix_with("FOR UPDATE SKIP LOCKED")).splitlines()[-1])   # FROM users FOR UPDATE SKIP LOCKED
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hassuffixes-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HasSuffixes`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`suffix_with()`](select.md#select-suffix-with)

///

## `UpdateBase` { #updatebase }

```python
from sqlalchemy.sql.expression import UpdateBase
```

INSERT, UPDATE, DELETE-এর মূল ক্লাস: `returning()`, `with_dialect_options()`, `return_defaults()`, `entity_description` এখানে। "যেকোনো DML" নেওয়ার ফাংশনে টাইপ-হিন্ট।

**উদাহরণ:**

```python
print([isinstance(s, UpdateBase) for s in (insert(users), update(users), delete(users), select(users))])   # [True, True, True, False]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #updatebase-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `UpdateBase`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`argument_for()`](select.md#select-argument-for) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`prefix_with()`](select.md#select-prefix-with) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_hint()`](select.md#select-with-hint)

**`Insert` থেকে:** [`entity_description`](dml.md#insert-entity-description) · [`exported_columns`](dml.md#insert-exported-columns) · [`named_with_column`](dml.md#insert-named-with-column) · [`return_defaults()`](dml.md#insert-return-defaults) · [`returning()`](dml.md#insert-returning) · [`returning_column_descriptions`](dml.md#insert-returning-column-descriptions) · [`with_dialect_options()`](dml.md#insert-with-dialect-options)

///

## `ValuesBase` { #valuesbase }

```python
from sqlalchemy.sql.expression import ValuesBase
```

`values()` মেথডসহ INSERT আর UPDATE-এর মূল ক্লাস (DELETE-এ `values()` নেই)।

**উদাহরণ:**

```python
print(isinstance(insert(users), ValuesBase), isinstance(update(users), ValuesBase), isinstance(delete(users), ValuesBase))   # True True False
```

### কনস্ট্রাক্টরের প্যারামিটার { #valuesbase-params }

```python
ValuesBase(table)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `table` | টেবিল। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #valuesbase-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ValuesBase`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`add_cte()`](select.md#select-add-cte) · [`allows_lambda`](select.md#select-allows-lambda) · [`argument_for()`](select.md#select-argument-for) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`corresponding_column()`](select.md#select-corresponding-column) · [`cte()`](select.md#select-cte) · [`description`](select.md#select-description) · [`dialect_kwargs`](select.md#select-dialect-kwargs) · [`dialect_options`](select.md#select-dialect-options) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_dialect_option()`](select.md#select-get-dialect-option) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_derived_from()`](select.md#select-is-derived-from) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`kwargs`](select.md#select-kwargs) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`name_cte_columns`](select.md#select-name-cte-columns) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`prefix_with()`](select.md#select-prefix-with) · [`reflect_only_elements`](select.md#select-reflect-only-elements) · [`selectable`](select.md#select-selectable) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection) · [`with_hint()`](select.md#select-with-hint)

**`Insert` থেকে:** [`entity_description`](dml.md#insert-entity-description) · [`exported_columns`](dml.md#insert-exported-columns) · [`named_with_column`](dml.md#insert-named-with-column) · [`return_defaults()`](dml.md#insert-return-defaults) · [`returning()`](dml.md#insert-returning) · [`returning_column_descriptions`](dml.md#insert-returning-column-descriptions) · [`select`](dml.md#insert-select) · [`values()`](dml.md#insert-values) · [`with_dialect_options()`](dml.md#insert-with-dialect-options)

///

## `DMLTargetCopy` { #dmltargetcopy }

```python
from sqlalchemy.sql.expression import DMLTargetCopy
```

(২.১-এ নতুন) [`from_dml_column()`](expressions.md#from-dml-column) যে এক্সপ্রেশন বানায়: INSERT/UPDATE-এ **আরেক কলামের জন্য দেওয়া মান**কে নির্দেশ করে (যেমন `slug`-এর মান `name`-এর মান থেকে)। SQL-এ সেই কলামের প্যারামিটারটিই আবার বসে।

**উদাহরণ:**

```python
t = Table("posts", MetaData(), Column("id", Integer, primary_key=True), Column("title", String), Column("slug", String))
stmt = insert(t).values(title="Hello", slug=func.lower(from_dml_column(t.c.title)))
print(type(from_dml_column(t.c.title)).__name__, sql(stmt))
# DMLTargetCopy INSERT INTO posts (title, slug) VALUES ('Hello', lower('Hello'))
```

### কনস্ট্রাক্টরের প্যারামিটার { #dmltargetcopy-params }

```python
DMLTargetCopy(column)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | যে কলামের মান নির্দেশ করবে। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dmltargetcopy-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DMLTargetCopy`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## `AliasedReturnsRows` { #aliasedreturnsrows }

```python
from sqlalchemy.sql.expression import AliasedReturnsRows
```

নাম-দেওয়া FROM-এর মূল ক্লাস: `Alias` (`table.alias()`), `Subquery`, `CTE`, `Lateral`, `TableSample`। সবগুলোর `.c` থেকে কলাম আর `element` থেকে মূল জিনিস।

**উদাহরণ:**

```python
for x in [users.alias("u"), select(users).subquery("s"), select(users).cte("c")]:
    print(type(x).__name__, isinstance(x, AliasedReturnsRows), x.name)
# Alias True u
# Subquery True s
# CTE True c
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aliasedreturnsrows-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AliasedReturnsRows`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Subquery` থেকে:** [`alias()`](select.md#subquery-alias) · [`c`](select.md#subquery-c) · [`columns`](select.md#subquery-columns) · [`foreign_keys`](select.md#subquery-foreign-keys) · [`implicit_returning`](select.md#subquery-implicit-returning) · [`join()`](select.md#subquery-join) · [`named_with_column`](select.md#subquery-named-with-column) · [`outerjoin()`](select.md#subquery-outerjoin) · [`primary_key`](select.md#subquery-primary-key) · [`schema`](select.md#subquery-schema) · [`select()`](select.md#subquery-select) · [`table_valued()`](select.md#subquery-table-valued) · [`tablesample()`](select.md#subquery-tablesample) · [`with_cols()`](select.md#subquery-with-cols)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`FromClause` থেকে:** [`corresponding_column()`](fromclause.md#fromclause-corresponding-column) · [`description`](fromclause.md#fromclause-description) · [`entity_namespace`](fromclause.md#fromclause-entity-namespace) · [`exported_columns`](fromclause.md#fromclause-exported-columns) · [`is_derived_from()`](fromclause.md#fromclause-is-derived-from) · [`lateral()`](fromclause.md#fromclause-lateral) · [`replace_selectable()`](fromclause.md#fromclause-replace-selectable) · [`selectable`](fromclause.md#fromclause-selectable)

**`Alias` থেকে:** [`original`](fromclause.md#alias-original)

///

## `FromGrouping` { #fromgrouping }

```python
from sqlalchemy.sql.expression import FromGrouping
```

FROM-এর ভেতরে বন্ধনী: নেস্টেড JOIN-কে `(a JOIN b) JOIN c` রূপে লিখতে কম্পাইলার এটি বসায়।

**উদাহরণ:**

```python
j = users.join(addresses).self_group()
print(type(j).__name__)   # FromGrouping
```

### কনস্ট্রাক্টরের প্যারামিটার { #fromgrouping-params }

```python
FromGrouping(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | বন্ধনীর ভেতরের FROM। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #fromgrouping-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FromGrouping`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`FromClause` থেকে:** [`alias()`](fromclause.md#fromclause-alias) · [`c`](fromclause.md#fromclause-c) · [`columns`](fromclause.md#fromclause-columns) · [`corresponding_column()`](fromclause.md#fromclause-corresponding-column) · [`description`](fromclause.md#fromclause-description) · [`entity_namespace`](fromclause.md#fromclause-entity-namespace) · [`exported_columns`](fromclause.md#fromclause-exported-columns) · [`foreign_keys`](fromclause.md#fromclause-foreign-keys) · [`is_derived_from()`](fromclause.md#fromclause-is-derived-from) · [`join()`](fromclause.md#fromclause-join) · [`lateral()`](fromclause.md#fromclause-lateral) · [`named_with_column`](fromclause.md#fromclause-named-with-column) · [`outerjoin()`](fromclause.md#fromclause-outerjoin) · [`primary_key`](fromclause.md#fromclause-primary-key) · [`replace_selectable()`](fromclause.md#fromclause-replace-selectable) · [`schema`](fromclause.md#fromclause-schema) · [`select()`](fromclause.md#fromclause-select) · [`selectable`](fromclause.md#fromclause-selectable) · [`tablesample()`](fromclause.md#fromclause-tablesample) · [`with_cols()`](fromclause.md#fromclause-with-cols)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## `ScalarValues` { #scalarvalues }

```python
from sqlalchemy.sql.expression import ScalarValues
```

কলামের জায়গায় বসানো `VALUES` (এক কলামের মান-তালিকা): `values(...).data(...).scalar_values()`। মূলত `IN (VALUES ...)` বা অ্যারের মতো ব্যবহারে।

**উদাহরণ:**

```python
v = values(column("n", Integer)).data([(1,), (2,)]).scalar_values()
print(type(v).__name__, sql(select(users.c.name).where(users.c.id.in_(v))).splitlines()[-1])
# ScalarValues WHERE users.id IN (VALUES (1), (2))
```

### কনস্ট্রাক্টরের প্যারামিটার { #scalarvalues-params }

```python
ScalarValues(columns, data, literal_binds)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | কলামগুলো। |
| `data` | মানগুলো। |
| `literal_binds` | মান সরাসরি SQL-এ বসাবে কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #scalarvalues-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ScalarValues`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## এক্সপ্রেশনের সহায়ক ক্লাস { #clauselist-group }

## `ClauseList` { #clauselist }

```python
from sqlalchemy.sql.expression import ClauseList
```

কয়েকটি এক্সপ্রেশনের তালিকা, একটি অপারেটর দিয়ে জোড়া (ডিফল্ট কমা): কলামের তালিকা, `GROUP BY` অংশ ইত্যাদি। `and_()`/`or_()`-এর জন্য এর subclass `BooleanClauseList`।

**উদাহরণ:**

```python
cl = ClauseList(users.c.id, users.c.name)
print(cl, len(cl))   # users.id, users.name 2
```

### কনস্ট্রাক্টরের প্যারামিটার { #clauselist-params }

```python
ClauseList(*clauses, operator=comma_op, group=True, group_contents=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | এক্সপ্রেশনগুলো। |
| `operator` | মাঝের অপারেটর (ডিফল্ট কমা)। |
| `group` | দরকারে বন্ধনী দেবে কি না। |
| `group_contents` | প্রতিটি উপাদানকে আলাদা বন্ধনী দেবে কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #clauselist-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append()`](#clauselist-append) | মেথড | তালিকায় আরেকটি এক্সপ্রেশন যোগ করে (এই অবজেক্টটিই বদলায়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ClauseList`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `ClauseList.append()` { #clauselist-append }

```python
ClauseList.append(clause)
```

**ধরন:** মেথড

তালিকায় আরেকটি এক্সপ্রেশন যোগ করে (এই অবজেক্টটিই বদলায়)।

**উদাহরণ:**

```python
cl = ClauseList(users.c.id)
cl.append(users.c.name)
print(cl)   # users.id, users.name
```

## `ExpressionClauseList` { #expressionclauselist }

```python
from sqlalchemy.sql.expression import ExpressionClauseList
```

(২.০) কলাম-এক্সপ্রেশন হিসেবে একটি তালিকা (একটি টাইপসহ), যেমন `tuple_()` বা কিছু অপারেটরের ফল। `ClauseList`-এর মতো যেকোনো কিছু নয়, শুধু মান-এক্সপ্রেশন।

**উদাহরণ:**

```python
from sqlalchemy.sql import operators
e = ExpressionClauseList(operators.comma_op, users.c.id, users.c.name)
print(type(e).__name__, e)   # ExpressionClauseList users.id, users.name
```

### কনস্ট্রাক্টরের প্যারামিটার { #expressionclauselist-params }

```python
ExpressionClauseList(operator, *clauses, type_=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `operator` | মাঝের অপারেটর। |
| `clauses` | এক্সপ্রেশনগুলো। |
| `type_` | ফলের টাইপ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #expressionclauselist-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ExpressionClauseList`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`BooleanClauseList` থেকে:** [`group`](elements.md#booleanclauselist-group) · [`is_comparison`](elements.md#booleanclauselist-is-comparison)

///

## `OrderByList` { #orderbylist }

```python
from sqlalchemy.sql.expression import OrderByList
```

(২.১-এ নতুন) ORDER BY-এর ভেতরে কমা দিয়ে জোড়া এক্সপ্রেশনের তালিকা, যেমন window function বা `aggregate_order_by()`-এর ORDER BY অংশ।

**উদাহরণ:**

```python
ob = OrderByList([users.c.name, users.c.id.desc()])
print(type(ob).__name__, ob)   # OrderByList users.name, users.id DESC
```

### কনস্ট্রাক্টরের প্যারামিটার { #orderbylist-params }

```python
OrderByList(clauses)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | ক্রমের এক্সপ্রেশনগুলো। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #orderbylist-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `OrderByList`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`ColumnOperators` থেকে:** [`asc()`](operators.md#columnoperators-asc) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`desc()`](operators.md#columnoperators-desc) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate)

///

## `Grouping` { #grouping }

```python
from sqlalchemy.sql.expression import Grouping
```

একটি কলাম-এক্সপ্রেশনের চারপাশে বন্ধনী: `(a + b) * c`। অপারেটরের অগ্রাধিকার (precedence) অনুযায়ী কম্পাইলার নিজে থেকে বসায় (`self_group()`)।

**উদাহরণ:**

```python
g = (users.c.id + 1).self_group()
print(type(g).__name__, g * 2)   # Grouping (users.id + :id_1) * :param_1
```

### কনস্ট্রাক্টরের প্যারামিটার { #grouping-params }

```python
Grouping(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | বন্ধনীর ভেতরের এক্সপ্রেশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #grouping-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Grouping`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

## `TypeClause` { #typeclause }

```python
from sqlalchemy.sql.expression import TypeClause
```

SQL-এ একটি টাইপের নাম বসানোর এক্সপ্রেশন, যেমন `CAST(x AS INTEGER)`-এর `INTEGER` অংশ।

**উদাহরণ:**

```python
tc = TypeClause(Integer())
print(type(tc).__name__, tc.compile(dialect=pg))   # TypeClause INTEGER
```

### কনস্ট্রাক্টরের প্যারামিটার { #typeclause-params }

```python
TypeClause(type_)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `type_` | টাইপ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typeclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TypeClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params)

///

## `TableValuedColumn` { #tablevaluedcolumn }

```python
from sqlalchemy.sql.expression import TableValuedColumn
```

table-valued ফাংশনের (`json_each()`, `generate_series()`) **পুরো রো**কে একটি কলাম হিসেবে: `func.json_each(...).table_valued().column`। PostgreSQL-এ রো-টাইপ মান হিসেবে পাওয়া যায়।

**উদাহরণ:**

```python
tv = func.generate_series(1, 3).table_valued("value").alias("s")
print(type(tv.column).__name__, sql(select(tv.column)))
# TableValuedColumn SELECT s
# FROM generate_series(1, 3) AS s
```

### কনস্ট্রাক্টরের প্যারামিটার { #tablevaluedcolumn-params }

```python
TableValuedColumn(scalar_alias, type_)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `scalar_alias` | table-valued alias। |
| `type_` | টাইপ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tablevaluedcolumn-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TableValuedColumn`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`anon_key_label`](elements.md#columnelement-anon-key-label) · [`anon_label`](elements.md#columnelement-anon-label) · [`base_columns`](elements.md#columnelement-base-columns) · [`cast()`](elements.md#columnelement-cast) · [`comparator`](elements.md#columnelement-comparator) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`expression`](elements.md#columnelement-expression) · [`foreign_keys`](elements.md#columnelement-foreign-keys) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`key`](elements.md#columnelement-key) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`primary_key`](elements.md#columnelement-primary-key) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`shares_lineage()`](elements.md#columnelement-shares-lineage) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`ColumnClause` থেকে:** [`is_literal`](elements.md#columnclause-is-literal) · [`table`](elements.md#columnclause-table)

///

## `TString` { #tstring }

```python
from sqlalchemy.sql.expression import TString
```

(২.১-এ নতুন) Python ৩.১৪-এর **t-string** থেকে তৈরি SQL: `tstring(t"SELECT * FROM users WHERE id = {uid}")`। `{...}`-এর মানগুলো নিরাপদ bind প্যারামিটার হয়ে যায় (SQL injection নয়), আর SQL এক্সপ্রেশন (`{users.c.name}`) হলে সেগুলোর SQL বসে। `text()`-এর মতো চালানো যায়। (এই পরীক্ষার পরিবেশ Python ৩.১৩, তাই এখানে t-string লেখা যায় না; উদাহরণ শুধু ক্লাসের পরিচয়।)

**উদাহরণ:**

```python
import sys
print(TString.__mro__[1].__name__, sys.version_info >= (3, 14))   # TextClause False
```

### কনস্ট্রাক্টরের প্যারামিটার { #tstring-params }

```python
TString(template)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `template` | Python ৩.১৪-এর `string.templatelib.Template` (t-string)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #tstring-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `TString`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`label()`](elements.md#columnelement-label) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`TextClause` থেকে:** [`bindparams()`](dml.md#textclause-bindparams) · [`columns()`](dml.md#textclause-columns) · [`comparator`](dml.md#textclause-comparator) · [`key`](dml.md#textclause-key) · [`type`](dml.md#textclause-type)

**`Select` থেকে:** [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options) · [`subquery()`](select.md#select-subquery)

///

## `FrameClause` { #frameclause }

```python
from sqlalchemy.sql.expression import FrameClause
```

(২.১-এ নতুন) window function-এর frame: `ROWS BETWEEN ... AND ...`, `RANGE ...`, `GROUPS ...`। `over(rows=(-2, 0))` ইত্যাদি দিলে তৈরি হয়; সীমার ধরন [`FrameClauseType`](#frameclausetype)।

**উদাহরণ:**

```python
w = func.sum(users.c.id).over(order_by=users.c.id, rows=(-2, 0))
print(type(w.rows).__name__, sql(select(w)).splitlines()[0])
# FrameClause SELECT sum(users.id) OVER (ORDER BY users.id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS anon_1
```

### কনস্ট্রাক্টরের প্যারামিটার { #frameclause-params }

```python
FrameClause(start, end, start_frame_type, end_frame_type)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `start` | শুরুর সীমা (সংখ্যা বা `None`)। |
| `end` | শেষের সীমা। |
| `start_frame_type` | শুরুর সীমার ধরন। |
| `end_frame_type` | শেষের সীমার ধরন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #frameclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `FrameClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params)

///

## `FrameClauseType` { #frameclausetype }

```python
from sqlalchemy.sql.expression import FrameClauseType
```

(২.১) window frame-এর একটি সীমার ধরন।

**উদাহরণ:**

```python
w = func.sum(users.c.id).over(order_by=users.c.id, rows=(None, 0))
print(w.rows.lower_type.name, w.rows.upper_type.name)   # UNBOUNDED CURRENT
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #frameclausetype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`CURRENT`](#frameclausetype-CURRENT) | অ্যাট্রিবিউট | `CURRENT ROW` (মান `0`)। |
| [`FOLLOWING`](#frameclausetype-FOLLOWING) | অ্যাট্রিবিউট | `n FOLLOWING` (ধনাত্মক মান)। |
| [`PRECEDING`](#frameclausetype-PRECEDING) | অ্যাট্রিবিউট | `n PRECEDING` (ঋণাত্মক মান)। |
| [`UNBOUNDED`](#frameclausetype-UNBOUNDED) | অ্যাট্রিবিউট | `UNBOUNDED PRECEDING/FOLLOWING` (মান `None`)। |

### `FrameClauseType.CURRENT` { #frameclausetype-CURRENT }

**ধরন:** অ্যাট্রিবিউট

`CURRENT ROW` (মান `0`)।

**উদাহরণ:**

```python
print(FrameClauseType.CURRENT.name)   # CURRENT
```

### `FrameClauseType.FOLLOWING` { #frameclausetype-FOLLOWING }

**ধরন:** অ্যাট্রিবিউট

`n FOLLOWING` (ধনাত্মক মান)।

**উদাহরণ:**

```python
print(FrameClauseType.FOLLOWING.name)   # FOLLOWING
```

### `FrameClauseType.PRECEDING` { #frameclausetype-PRECEDING }

**ধরন:** অ্যাট্রিবিউট

`n PRECEDING` (ঋণাত্মক মান)।

**উদাহরণ:**

```python
print(FrameClauseType.PRECEDING.name)   # PRECEDING
```

### `FrameClauseType.UNBOUNDED` { #frameclausetype-UNBOUNDED }

**ধরন:** অ্যাট্রিবিউট

`UNBOUNDED PRECEDING/FOLLOWING` (মান `None`)।

**উদাহরণ:**

```python
print(FrameClauseType.UNBOUNDED.name)   # UNBOUNDED
```

## `SavepointClause` { #savepointclause }

```python
from sqlalchemy.sql.expression import SavepointClause
```

`SAVEPOINT <নাম>` স্টেটমেন্ট। `connection.begin_nested()` ভেতরে এটি চালায়।

**উদাহরণ:**

```python
print(SavepointClause("sp1").compile(dialect=pg))   # SAVEPOINT sp1
```

### কনস্ট্রাক্টরের প্যারামিটার { #savepointclause-params }

```python
SavepointClause(ident)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `ident` | savepoint-এর নাম। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #savepointclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SavepointClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`Select` থেকে:** [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options)

///

## `ReleaseSavepointClause` { #releasesavepointclause }

```python
from sqlalchemy.sql.expression import ReleaseSavepointClause
```

`RELEASE SAVEPOINT <নাম>`: nested transaction commit।

**উদাহরণ:**

```python
print(ReleaseSavepointClause("sp1").compile(dialect=pg))   # RELEASE SAVEPOINT sp1
```

### কনস্ট্রাক্টরের প্যারামিটার { #releasesavepointclause-params }

```python
ReleaseSavepointClause(ident)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `ident` | savepoint-এর নাম। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #releasesavepointclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ReleaseSavepointClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`Select` থেকে:** [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options)

///

## `RollbackToSavepointClause` { #rollbacktosavepointclause }

```python
from sqlalchemy.sql.expression import RollbackToSavepointClause
```

`ROLLBACK TO SAVEPOINT <নাম>`: nested transaction rollback।

**উদাহরণ:**

```python
print(RollbackToSavepointClause("sp1").compile(dialect=pg))   # ROLLBACK TO SAVEPOINT sp1
```

### কনস্ট্রাক্টরের প্যারামিটার { #rollbacktosavepointclause-params }

```python
RollbackToSavepointClause(ident)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `ident` | savepoint-এর নাম। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #rollbacktosavepointclause-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `RollbackToSavepointClause`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

**`Select` থেকে:** [`execution_options()`](select.md#select-execution-options) · [`get_execution_options()`](select.md#select-get-execution-options) · [`is_delete`](select.md#select-is-delete) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`options()`](select.md#select-options)

///

## `SQLColumnExpression` { #sqlcolumnexpression }

```python
from sqlalchemy.sql.expression import SQLColumnExpression
```

(২.০) টাইপ-হিন্টের জন্য: "যেকোনো SQL কলাম-এক্সপ্রেশন" (Core `Column`/এক্সপ্রেশন **আর** ORM অ্যাট্রিবিউট `User.name` দুটোই)। হেল্পার ফাংশন যা Core ও ORM দুই জায়গাতেই চলবে: `def search(col: SQLColumnExpression[str], q: str)`।

**উদাহরণ:**

```python
def contains_ci(col: "SQLColumnExpression[str]", q: str):
    return col.icontains(q)
print(contains_ci(users.c.name, "র"), isinstance(users.c.name, SQLColumnExpression))
# lower(users.name) LIKE '%' || lower(:name_1) || '%' True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sqlcolumnexpression-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SQLColumnExpression`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

///

## `Operators` { #operators }

```python
from sqlalchemy.sql.operators import Operators
```

সব অপারেটরের সবচেয়ে মূল ক্লাস: `&` (AND), `|` (OR), `~` (NOT), আর `op()`, `bool_op()`, `operate()`। এর subclass `ColumnOperators` তুলনা ইত্যাদি যোগ করে ([কলাম অপারেটর পেজ](operators.md))।

**উদাহরণ:**

```python
print(isinstance(users.c.id, Operators), (users.c.id > 1) & (users.c.name == "x"))   # True users.id > :id_1 AND users.name = :name_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #operators-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Operators`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`bool_op()`](operators.md#columnoperators-bool-op) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate)

///

## `custom_op` { #custom-op }

```python
from sqlalchemy.sql.operators import custom_op
```

নিজের SQL অপারেটর: `col.op("@>")(other)` লিখলে ভেতরে এটি তৈরি হয়। সরাসরি বানিয়ে আবার ব্যবহারযোগ্য অপারেটর রাখা যায়, বা নিজের comparator-এ `self.operate(custom_op("..."), other)`।

**উদাহরণ:**

```python
contains_op = custom_op("@>", is_comparison=True)
tags = column("tags", postgresql.ARRAY(String))
print(sql(select(literal(1)).where(contains_op(tags, ["a"]))).splitlines()[-1])   # WHERE tags @> ARRAY['a']
```

### কনস্ট্রাক্টরের প্যারামিটার { #custom-op-params }

```python
custom_op(opstring, *, precedence=0, is_comparison=False, return_type=None, natural_self_precedent=False, eager_grouping=False, python_impl=None, operator_class=<OperatorClass.BASE: 2>, visit_name=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `opstring` | SQL-এ অপারেটরের টেক্সট। |
| `precedence` | অগ্রাধিকার (বন্ধনী কোথায় লাগবে)। |
| `is_comparison` | `True` হলে তুলনা অপারেটর: ফল BOOLEAN, আর ORM join শর্তে ব্যবহারযোগ্য। |
| `return_type` | ফলের টাইপ। |
| `natural_self_precedent` | নিজের সাথে পাশাপাশি বসলে বন্ধনী বাদ দেবে কি না (যেমন <code>a &#124;&#124; b &#124;&#124; c</code>)। |
| `eager_grouping` | সবসময় বন্ধনী দেবে কি না। |
| `python_impl` | ORM-এর in-Python মূল্যায়নের (যেমন `synchronize_session="evaluate"`) জন্য Python ফাংশন। |
| `operator_class` | (২.১) কোন টাইপ-শ্রেণিতে বৈধ ([`OperatorClass`](types.md#operatorclass))। |
| `visit_name` | কম্পাইলারে বিশেষ visit-এর নাম (নিজের কম্পাইল-নিয়মের জন্য)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #custom-op-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`eager_grouping`](#custom-op-eager-grouping) | অ্যাট্রিবিউট | সবসময় বন্ধনী দেবে কি না। |
| [`is_comparison`](#custom-op-is-comparison) | অ্যাট্রিবিউট | তুলনা অপারেটর কি না (ফলের টাইপ BOOLEAN)। |
| [`natural_self_precedent`](#custom-op-natural-self-precedent) | অ্যাট্রিবিউট | `a OP b OP c`-এ বন্ধনী বাদ দেবে কি না। |
| [`operator_class`](#custom-op-operator-class) | অ্যাট্রিবিউট | (২.১) অপারেটরটি কোন টাইপ-শ্রেণির জন্য। |
| [`opstring`](#custom-op-opstring) | অ্যাট্রিবিউট | অপারেটরের SQL টেক্সট। |
| [`precedence`](#custom-op-precedence) | অ্যাট্রিবিউট | অগ্রাধিকার (বড় মান = আগে)। |
| [`python_impl`](#custom-op-python-impl) | অ্যাট্রিবিউট | in-Python মূল্যায়নের ফাংশন, বা `None`। |
| [`return_type`](#custom-op-return-type) | অ্যাট্রিবিউট | ফলের টাইপ: ক্লাস দিলেও (`String`) টাইপ-অবজেক্টে বদলে রাখে; না দিলে `None`। |
| [`visit_name`](#custom-op-visit-name) | অ্যাট্রিবিউট | বিশেষ কম্পাইল-নিয়মের নাম, না দিলে `None`। |

### `custom_op.eager_grouping` { #custom-op-eager-grouping }

**ধরন:** অ্যাট্রিবিউট

সবসময় বন্ধনী দেবে কি না।

**উদাহরণ:**

```python
print(custom_op("~~").eager_grouping)   # False
```

### `custom_op.is_comparison` { #custom-op-is-comparison }

**ধরন:** অ্যাট্রিবিউট

তুলনা অপারেটর কি না (ফলের টাইপ BOOLEAN)।

**উদাহরণ:**

```python
print(custom_op("@>", is_comparison=True).is_comparison)   # True
```

### `custom_op.natural_self_precedent` { #custom-op-natural-self-precedent }

**ধরন:** অ্যাট্রিবিউট

`a OP b OP c`-এ বন্ধনী বাদ দেবে কি না।

**উদাহরণ:**

```python
print(custom_op("||").natural_self_precedent)   # False
```

### `custom_op.operator_class` { #custom-op-operator-class }

**ধরন:** অ্যাট্রিবিউট

(২.১) অপারেটরটি কোন টাইপ-শ্রেণির জন্য।

**উদাহরণ:**

```python
print(custom_op("@>").operator_class is not None)   # True
```

### `custom_op.opstring` { #custom-op-opstring }

**ধরন:** অ্যাট্রিবিউট

অপারেটরের SQL টেক্সট।

**উদাহরণ:**

```python
print(custom_op("<->").opstring)   # <->
```

### `custom_op.precedence` { #custom-op-precedence }

**ধরন:** অ্যাট্রিবিউট

অগ্রাধিকার (বড় মান = আগে)।

**উদাহরণ:**

```python
print(custom_op("@>", precedence=5).precedence)   # 5
```

### `custom_op.python_impl` { #custom-op-python-impl }

**ধরন:** অ্যাট্রিবিউট

in-Python মূল্যায়নের ফাংশন, বা `None`।

**উদাহরণ:**

```python
print(custom_op("%", python_impl=lambda a, b: a % b).python_impl(7, 3))   # 1
```

### `custom_op.return_type` { #custom-op-return-type }

**ধরন:** অ্যাট্রিবিউট

ফলের টাইপ: ক্লাস দিলেও (`String`) টাইপ-অবজেক্টে বদলে রাখে; না দিলে `None`।

**উদাহরণ:**

```python
print(repr(custom_op("->", return_type=String).return_type))   # String()
```

### `custom_op.visit_name` { #custom-op-visit-name }

**ধরন:** অ্যাট্রিবিউট

বিশেষ কম্পাইল-নিয়মের নাম, না দিলে `None`।

**উদাহরণ:**

```python
print(custom_op("~").visit_name)   # None
```

## `quoted_name` { #quoted-name }

```python
from sqlalchemy.sql.expression import quoted_name
```

একটি নাম (`str`) সাথে **quote করার সিদ্ধান্ত**: `quoted_name("MyTable", quote=True)` সবসময় quote, `quote=False` কখনো নয়, `None` হলে স্বাভাবিক নিয়ম। কাজে লাগে যখন ডেটাবেসে সত্যিই বড় হাতের বা অদ্ভুত নাম আছে, বা Oracle-এর মতো ডেটাবেসে নাম যেমন আছে ঠিক তেমন রাখতে হবে। reflection-এ পাওয়া নামগুলোও প্রায়ই এই ক্লাসের।

**উদাহরণ:**

```python
t = Table(quoted_name("orders", quote=True), MetaData(), Column("id", Integer))
print(sql(select(t.c.id)).splitlines()[-1], "|", pg.identifier_preparer.quote(quoted_name("Users", quote=False)))
# FROM "orders" | Users
```

**Python `str`-এর সব মেথড** (`capitalize()`, `casefold()`, `center()`, `count()`, `encode()`, `endswith()`, `expandtabs()`, `find()`, `format()`, `format_map()`, `index()`, `isalnum()`, `isalpha()`, `isascii()`, `isdecimal()`, `isdigit()`, `isidentifier()`, `islower()`, `isnumeric()`, `isprintable()`, `isspace()`, `istitle()`, `isupper()`, `join()`, `ljust()`, `lower()`, `lstrip()`, `maketrans()`, `partition()`, `removeprefix()`, `removesuffix()`, `replace()`, `rfind()`, `rindex()`, `rjust()`, `rpartition()`, `rsplit()`, `rstrip()`, `split()`, `splitlines()`, `startswith()`, `strip()`, `swapcase()`, `title()`, `translate()`, `upper()`, `zfill()`) সাধারণ `str`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #quoted-name-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`construct()`](#quoted-name-construct) | ক্লাস মেথড (internal) | (ক্লাস মেথড) নাম আর quote থেকে বানায়; quote `None` হলে সাধারণ `str` ফেরত দিতে পারে। |
| [`quote`](#quoted-name-quote) | অ্যাট্রিবিউট | quote-এর সিদ্ধান্ত: `True`, `False`, বা `None` (স্বাভাবিক নিয়ম)। |

### `quoted_name.construct()` { #quoted-name-construct }

```python
quoted_name.construct(value, quote)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) নাম আর quote থেকে বানায়; quote `None` হলে সাধারণ `str` ফেরত দিতে পারে।

**উদাহরণ:**

```python
print(type(quoted_name.construct("x", True)).__name__)   # quoted_name
```

### `quoted_name.quote` { #quoted-name-quote }

**ধরন:** অ্যাট্রিবিউট

quote-এর সিদ্ধান্ত: `True`, `False`, বা `None` (স্বাভাবিক নিয়ম)।

**উদাহরণ:**

```python
print(quoted_name("x", quote=True).quote, quoted_name("x", None).quote)   # True None
```

## `SelectLabelStyle` { #selectlabelstyle }

```python
from sqlalchemy.sql import LABEL_STYLE_TABLENAME_PLUS_COL
```

SELECT-এর কলামের নাম (label) কীভাবে হবে: `select(...).set_label_style(...)`-এ দিন। একাধিক টেবিলে একই নামের কলাম (`users.id`, `addresses.id`) থাকলে ফলে নাম মেলাতে কাজে লাগে।

**উদাহরণ:**

```python
stmt = select(users.c.id, addresses.c.id)
for style in (SelectLabelStyle.LABEL_STYLE_DISAMBIGUATE_ONLY, SelectLabelStyle.LABEL_STYLE_TABLENAME_PLUS_COL):
    print(style.name, list(stmt.set_label_style(style).selected_columns.keys()))
# LABEL_STYLE_DISAMBIGUATE_ONLY ['id', 'id_1']
# LABEL_STYLE_TABLENAME_PLUS_COL ['users_id', 'addresses_id']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #selectlabelstyle-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`LABEL_STYLE_DISAMBIGUATE_ONLY`](#selectlabelstyle-LABEL-STYLE-DISAMBIGUATE-ONLY) | অ্যাট্রিবিউট | (Core-এর ডিফল্ট) নাম একই হলে শুধু দ্বিতীয়টিকে আলাদা করে (`id`, `id_1`)। |
| [`LABEL_STYLE_LEGACY_ORM`](#selectlabelstyle-LABEL-STYLE-LEGACY-ORM) | অ্যাট্রিবিউট | পুরোনো `Query`-এর ধরন (`users_id`-এর মতো, কিছু পার্থক্যসহ)। |
| [`LABEL_STYLE_NONE`](#selectlabelstyle-LABEL-STYLE-NONE) | অ্যাট্রিবিউট | কোনো label নয়: কলামের নাম যেমন আছে (ডুপ্লিকেট নামও)। |
| [`LABEL_STYLE_TABLENAME_PLUS_COL`](#selectlabelstyle-LABEL-STYLE-TABLENAME-PLUS-COL) | অ্যাট্রিবিউট | প্রতিটি কলাম `টেবিল_কলাম` (`users_id`)। |

### `SelectLabelStyle.LABEL_STYLE_DISAMBIGUATE_ONLY` { #selectlabelstyle-LABEL-STYLE-DISAMBIGUATE-ONLY }

**ধরন:** অ্যাট্রিবিউট

(Core-এর ডিফল্ট) নাম একই হলে শুধু দ্বিতীয়টিকে আলাদা করে (`id`, `id_1`)।

**উদাহরণ:**

```python
print(select(users.c.id).get_label_style().name)   # LABEL_STYLE_DISAMBIGUATE_ONLY
```

### `SelectLabelStyle.LABEL_STYLE_LEGACY_ORM` { #selectlabelstyle-LABEL-STYLE-LEGACY-ORM }

**ধরন:** অ্যাট্রিবিউট

পুরোনো `Query`-এর ধরন (`users_id`-এর মতো, কিছু পার্থক্যসহ)।

**উদাহরণ:**

```python
print(SelectLabelStyle.LABEL_STYLE_LEGACY_ORM.value)   # 3
```

### `SelectLabelStyle.LABEL_STYLE_NONE` { #selectlabelstyle-LABEL-STYLE-NONE }

**ধরন:** অ্যাট্রিবিউট

কোনো label নয়: কলামের নাম যেমন আছে (ডুপ্লিকেট নামও)।

**উদাহরণ:**

```python
stmt = select(users.c.id, addresses.c.id).set_label_style(SelectLabelStyle.LABEL_STYLE_NONE)
print(sql(stmt).splitlines()[0])   # SELECT users.id, addresses.id
```

### `SelectLabelStyle.LABEL_STYLE_TABLENAME_PLUS_COL` { #selectlabelstyle-LABEL-STYLE-TABLENAME-PLUS-COL }

**ধরন:** অ্যাট্রিবিউট

প্রতিটি কলাম `টেবিল_কলাম` (`users_id`)।

**উদাহরণ:**

```python
stmt = select(users.c.id).set_label_style(SelectLabelStyle.LABEL_STYLE_TABLENAME_PLUS_COL)
print(sql(stmt).splitlines()[0])   # SELECT users.id AS users_id
```

## `WriteableColumnCollection` { #writeablecolumncollection }

```python
from sqlalchemy.sql.expression import WriteableColumnCollection
```

(২.১) বদলানো যায় এমন [`ColumnCollection`](fromclause.md#columncollection): `add()`, `remove()` ইত্যাদিসহ। `Table.c` ভেতরে এটি, আর বাইরে read-only রূপ দেখায়।

**উদাহরণ:**

```python
wc = WriteableColumnCollection()
wc.add(column("a")); wc.add(column("b"))
print(list(wc.keys()), type(wc.as_readonly()).__name__)   # ['a', 'b'] ReadOnlyColumnCollection
```

### কনস্ট্রাক্টরের প্যারামিটার { #writeablecolumncollection-params }

```python
WriteableColumnCollection(columns=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | শুরুর `(key, কলাম)` জোড়াগুলো। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #writeablecolumncollection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#writeablecolumncollection-add) | মেথড | একটি কলাম যোগ করে (key না দিলে কলামের নাম)। |
| [`as_readonly()`](#writeablecolumncollection-as-readonly) | মেথড | একই কলামের একটি read-only রূপ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `WriteableColumnCollection`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnCollection` থেকে:** [`compare()`](fromclause.md#columncollection-compare) · [`contains_column()`](fromclause.md#columncollection-contains-column) · [`corresponding_column()`](fromclause.md#columncollection-corresponding-column) · [`get()`](fromclause.md#columncollection-get) · [`items()`](fromclause.md#columncollection-items) · [`keys()`](fromclause.md#columncollection-keys) · [`values()`](fromclause.md#columncollection-values)

///

### `WriteableColumnCollection.add()` { #writeablecolumncollection-add }

```python
WriteableColumnCollection.add(column, key=None)
```

**ধরন:** মেথড

একটি কলাম যোগ করে (key না দিলে কলামের নাম)।

**উদাহরণ:**

```python
wc = WriteableColumnCollection()
wc.add(column("x"), key="y")
print(list(wc.keys()))   # ['y']
```

### `WriteableColumnCollection.as_readonly()` { #writeablecolumncollection-as-readonly }

```python
WriteableColumnCollection.as_readonly()
```

**ধরন:** মেথড

একই কলামের একটি read-only রূপ।

**উদাহরণ:**

```python
wc = WriteableColumnCollection([("a", column("a"))])
ro = wc.as_readonly()
print(hasattr(ro, "add"))   # False
```

## `Visitable` { #visitable }

```python
from sqlalchemy.sql.expression import Visitable
```

কম্পাইলারের `visit_*` dispatch-যোগ্য সব অবজেক্টের মূল ক্লাস: প্রতিটির `__visit_name__` দেখে কম্পাইলার [`visit_<নাম>()`](compiler.md#sqlcompiler) ডাকে।

**উদাহরণ:**

```python
print(isinstance(select(users), Visitable), select(users).__visit_name__, (users.c.id == 1).__visit_name__)   # True select binary
```

## `Named` { #named }

```python
from sqlalchemy import Named
```

(২.১-এ নতুন) [`TypedColumns`](schema.md#typedcolumns)-এ কলাম ঘোষণার descriptor-টাইপ: টাইপ-চেকার যেন জানে `t.c.name` একটি `Column[str]`। চলার সময় এর নিজের কোনো আচরণ নেই, শুধু টাইপ-হিন্টের জন্য।

**উদাহরণ:**

```python
import typing
print(typing.get_origin(Named[int]) is Named)   # True
```

## স্কিমার মূল ক্লাস { #schemaitem-group }

## `SchemaItem` { #schemaitem }

```python
from sqlalchemy.schema import SchemaItem
```

স্কিমা গঠনের সব অংশের মূল ক্লাস: `Table`, `Column`, `Index`, `Constraint`, `Sequence`, `ForeignKey` …। `info` dict আর ডায়ালেক্ট-বিশেষ অপশন (`dialect_options`) এখান থেকে।

**উদাহরণ:**

```python
print([isinstance(x, SchemaItem) for x in (users, users.c.id, Index("ix", users.c.name), list(addresses.c.user_id.foreign_keys)[0])])   # [True, True, True, True]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #schemaitem-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SchemaItem`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Table` থেকে:** [`create_drop_stringify_dialect`](schema.md#table-create-drop-stringify-dialect) · [`info`](schema.md#table-info)

///

## `SchemaConst` { #schemaconst }

```python
from sqlalchemy.schema import SchemaConst
```

স্কিমা-সংক্রান্ত বিশেষ ধ্রুবক (`sqlalchemy.schema.BLANK_SCHEMA` ইত্যাদি নামেও পাওয়া যায়)।

**উদাহরণ:**

```python
from sqlalchemy.schema import BLANK_SCHEMA
print(BLANK_SCHEMA is SchemaConst.BLANK_SCHEMA)   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #schemaconst-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`BLANK_SCHEMA`](#schemaconst-BLANK-SCHEMA) | অ্যাট্রিবিউট | `MetaData(schema="x")` থাকলেও একটি টেবিল/Sequence-কে **স্কিমা ছাড়া** রাখতে: `Table(..., schema=BLANK_SCHEMA)`। |
| [`NULL_UNSPECIFIED`](#schemaconst-NULL-UNSPECIFIED) | অ্যাট্রিবিউট | কলামের `nullable` নির্দিষ্ট করা হয়নি বোঝাতে (ভেতরের ডিফল্ট মান)। |
| [`RETAIN_SCHEMA`](#schemaconst-RETAIN-SCHEMA) | অ্যাট্রিবিউট | `table.to_metadata(..., schema=RETAIN_SCHEMA)`: কপিতে টেবিলের নিজের স্কিমা রাখো (ডিফল্ট)। |

### `SchemaConst.BLANK_SCHEMA` { #schemaconst-BLANK-SCHEMA }

**ধরন:** অ্যাট্রিবিউট

`MetaData(schema="x")` থাকলেও একটি টেবিল/Sequence-কে **স্কিমা ছাড়া** রাখতে: `Table(..., schema=BLANK_SCHEMA)`।

**উদাহরণ:**

```python
from sqlalchemy.schema import BLANK_SCHEMA
md = MetaData(schema="app")
t = Table("t", md, Column("id", Integer), schema=BLANK_SCHEMA)
print(t.schema, Table("t2", md, Column("id", Integer)).schema)   # None app
```

### `SchemaConst.NULL_UNSPECIFIED` { #schemaconst-NULL-UNSPECIFIED }

**ধরন:** অ্যাট্রিবিউট

কলামের `nullable` নির্দিষ্ট করা হয়নি বোঝাতে (ভেতরের ডিফল্ট মান)।

**উদাহরণ:**

```python
print(SchemaConst.NULL_UNSPECIFIED.name)   # NULL_UNSPECIFIED
```

### `SchemaConst.RETAIN_SCHEMA` { #schemaconst-RETAIN-SCHEMA }

**ধরন:** অ্যাট্রিবিউট

`table.to_metadata(..., schema=RETAIN_SCHEMA)`: কপিতে টেবিলের নিজের স্কিমা রাখো (ডিফল্ট)।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("id", Integer), schema="s")
print(t.to_metadata(MetaData(), schema=SchemaConst.RETAIN_SCHEMA).schema)   # s
```

## `ColumnCollectionMixin` { #columncollectionmixin }

```python
from sqlalchemy.schema import ColumnCollectionMixin
```

কলাম-ভিত্তিক কনস্ট্রেইন্ট আর ইনডেক্সের (`PrimaryKeyConstraint`, `UniqueConstraint`, `Index` …) মিক্সিন: কোন কলামগুলো নিয়ে, তা `.columns` / `.c`-তে।

**উদাহরণ:**

```python
uc = UniqueConstraint(users.c.name)
print(isinstance(uc, ColumnCollectionMixin), [c.name for c in uc.columns])   # True ['name']
```

### কনস্ট্রাক্টরের প্যারামিটার { #columncollectionmixin-params }

```python
ColumnCollectionMixin(*columns)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `columns` | কলামগুলো (Column বা নাম)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columncollectionmixin-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`c`](#columncollectionmixin-c) | প্রপার্টি | `columns`-এর ছোট নাম। |
| [`columns`](#columncollectionmixin-columns) | প্রপার্টি | কলামগুলোর `ColumnCollection`। |

### `ColumnCollectionMixin.c` { #columncollectionmixin-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(list(users.primary_key.c.keys()))   # ['id']
```

### `ColumnCollectionMixin.columns` { #columncollectionmixin-columns }

**ধরন:** প্রপার্টি

কলামগুলোর `ColumnCollection`।

**উদাহরণ:**

```python
print([c.name for c in Index("ix_n", users.c.name).columns])   # ['name']
```

## `ForeignKeyTarget` { #foreignkeytarget }

```python
from sqlalchemy.schema import ForeignKeyTarget
```

(২.১) `ForeignKey`-এর লক্ষ্য তিন অংশে (named tuple): `schema`, `table_name`, `column_name`। `ForeignKey.target_tokens` এটি দেয়; সরাসরি `ForeignKey(ForeignKeyTarget(...))`-এও দেওয়া যায় (বিন্দু-ওয়ালা নামের ঝামেলা এড়াতে)।

**উদাহরণ:**

```python
fk = list(addresses.c.user_id.foreign_keys)[0]
print(fk.target_tokens)   # ForeignKeyTarget(schema=None, table_name='users', column_name='id')
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #foreignkeytarget-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`column_name`](#foreignkeytarget-column-name) | অ্যাট্রিবিউট | লক্ষ্য কলামের নাম। |
| [`schema`](#foreignkeytarget-schema) | অ্যাট্রিবিউট | লক্ষ্য টেবিলের স্কিমা (বা `None`)। |
| [`table_name`](#foreignkeytarget-table-name) | অ্যাট্রিবিউট | লক্ষ্য টেবিলের নাম। |

### `ForeignKeyTarget.column_name` { #foreignkeytarget-column-name }

**ধরন:** অ্যাট্রিবিউট

লক্ষ্য কলামের নাম।

**উদাহরণ:**

```python
print(ForeignKeyTarget(None, "users", "id").column_name)   # id
```

### `ForeignKeyTarget.schema` { #foreignkeytarget-schema }

**ধরন:** অ্যাট্রিবিউট

লক্ষ্য টেবিলের স্কিমা (বা `None`)।

**উদাহরণ:**

```python
print(ForeignKeyTarget("app", "users", "id").schema)   # app
```

### `ForeignKeyTarget.table_name` { #foreignkeytarget-table-name }

**ধরন:** অ্যাট্রিবিউট

লক্ষ্য টেবিলের নাম।

**উদাহরণ:**

```python
print(ForeignKeyTarget(None, "users", "id").table_name)   # users
```

## `SchemaVisitable` { #schemavisitable }

```python
from sqlalchemy.schema import SchemaVisitable
```

(২.০.৪১) `SchemaVisitor` যাদের ঘুরতে পারে তাদের মূল ক্লাস: `SchemaItem` আর নামযুক্ত টাইপ (PostgreSQL `ENUM`, `DOMAIN`)।

**উদাহরণ:**

```python
print(isinstance(users, SchemaVisitable), isinstance(postgresql.ENUM("a", name="x"), SchemaVisitable))   # True True
```

## `SchemaVisitor` { #schemavisitor }

```python
from sqlalchemy.schema import SchemaVisitor
```

স্কিমা-অবজেক্ট (MetaData, Table, Column …) ঘোরার visitor-এর মূল ক্লাস। `create_all()`/`drop_all()` এর subclass (`SchemaGenerator`, `SchemaDropper`) দিয়ে চলে।

**উদাহরণ:**

```python
class Count(SchemaVisitor):
    def __init__(self):
        self.tables = 0
    def visit_table(self, t):
        self.tables += 1
v = Count()
for t in m.sorted_tables:
    v.traverse_single(t)
print(v.tables)   # 2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #schemavisitor-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`chain()`](#schemavisitor-chain) | মেথড (internal) | আরেকটি visitor পেছনে জুড়ে দেয় (দুটি একসাথে চলে)। |
| [`iterate()`](#schemavisitor-iterate) | মেথড (internal) | একটি অবজেক্টের সব উপাদান ঘুরে iterator দেয়। |
| [`traverse()`](#schemavisitor-traverse) | মেথড (internal) | গাছের সব উপাদানে visit চালায়। |
| [`traverse_single()`](#schemavisitor-traverse-single) | মেথড | একটি অবজেক্টের জন্য তার `visit_<নাম>()` ডাকে। |
| [`visitor_iterator`](#schemavisitor-visitor-iterator) | প্রপার্টি (internal) | `chain()` দিয়ে জোড়া সব visitor। |

### `SchemaVisitor.chain()` { #schemavisitor-chain }

```python
SchemaVisitor.chain(visitor)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

আরেকটি visitor পেছনে জুড়ে দেয় (দুটি একসাথে চলে)।

**উদাহরণ:**

```python
print(callable(SchemaVisitor.chain))   # True
```

### `SchemaVisitor.iterate()` { #schemavisitor-iterate }

```python
SchemaVisitor.iterate(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টের সব উপাদান ঘুরে iterator দেয়।

**উদাহরণ:**

```python
print(callable(SchemaVisitor.iterate))   # True
```

### `SchemaVisitor.traverse()` { #schemavisitor-traverse }

```python
SchemaVisitor.traverse(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

গাছের সব উপাদানে visit চালায়।

**উদাহরণ:**

```python
print(callable(SchemaVisitor.traverse))   # True
```

### `SchemaVisitor.traverse_single()` { #schemavisitor-traverse-single }

```python
SchemaVisitor.traverse_single(obj, **kw)
```

**ধরন:** মেথড

একটি অবজেক্টের জন্য তার `visit_<নাম>()` ডাকে।

**উদাহরণ:**

```python
class V(SchemaVisitor):
    def visit_table(self, t):
        return t.name
print(V().traverse_single(users))   # users
```

### `SchemaVisitor.visitor_iterator` { #schemavisitor-visitor-iterator }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`chain()` দিয়ে জোড়া সব visitor।

**উদাহরণ:**

```python
v = SchemaVisitor()
print(len(list(v.visitor_iterator)))   # 1
```

## `InvokeDDLBase` { #invokeddlbase }

```python
from sqlalchemy.schema import InvokeDDLBase
```

(অভ্যন্তরীণ) DDL চালানো visitor-এর মূল ক্লাস (`create_all()`-এর `SchemaGenerator`, `drop_all()`-এর `SchemaDropper`): সংযোগে আসল CREATE/DROP চালায় আর `before_create`/`after_create` ইভেন্ট ছোড়ে।

**উদাহরণ:**

```python
from sqlalchemy.sql.ddl import SchemaGenerator
print(issubclass(SchemaGenerator, InvokeDDLBase))   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #invokeddlbase-params }

```python
InvokeDDLBase(connection, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `connection` | যে সংযোগে DDL চলবে। |
| `kw` | বাকি অপশন (`checkfirst` ইত্যাদি)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #invokeddlbase-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`chain()`](#invokeddlbase-chain) | মেথড (internal) | `SchemaVisitor.chain`-এর মতো। |
| [`iterate()`](#invokeddlbase-iterate) | মেথড (internal) | `SchemaVisitor.iterate`-এর মতো। |
| [`traverse()`](#invokeddlbase-traverse) | মেথড (internal) | `SchemaVisitor.traverse`-এর মতো। |
| [`traverse_single()`](#invokeddlbase-traverse-single) | মেথড (internal) | একটি অবজেক্টের DDL চালায়। |
| [`visitor_iterator`](#invokeddlbase-visitor-iterator) | প্রপার্টি (internal) | জোড়া visitor-গুলো। |
| [`with_ddl_events()`](#invokeddlbase-with-ddl-events) | মেথড (internal) | একটি অবজেক্টের DDL-এর আগে-পরে `before_create`/`after_create` (বা drop) ইভেন্ট ছোড়ার context manager। |

### `InvokeDDLBase.chain()` { #invokeddlbase-chain }

```python
InvokeDDLBase.chain(visitor)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`SchemaVisitor.chain`-এর মতো।

**উদাহরণ:**

```python
print(callable(InvokeDDLBase.chain))   # True
```

### `InvokeDDLBase.iterate()` { #invokeddlbase-iterate }

```python
InvokeDDLBase.iterate(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`SchemaVisitor.iterate`-এর মতো।

**উদাহরণ:**

```python
print(callable(InvokeDDLBase.iterate))   # True
```

### `InvokeDDLBase.traverse()` { #invokeddlbase-traverse }

```python
InvokeDDLBase.traverse(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`SchemaVisitor.traverse`-এর মতো।

**উদাহরণ:**

```python
print(callable(InvokeDDLBase.traverse))   # True
```

### `InvokeDDLBase.traverse_single()` { #invokeddlbase-traverse-single }

```python
InvokeDDLBase.traverse_single(obj, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টের DDL চালায়।

**উদাহরণ:**

```python
print(callable(InvokeDDLBase.traverse_single))   # True
```

### `InvokeDDLBase.visitor_iterator` { #invokeddlbase-visitor-iterator }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

জোড়া visitor-গুলো।

**উদাহরণ:**

```python
print(isinstance(InvokeDDLBase.visitor_iterator, property))   # True
```

### `InvokeDDLBase.with_ddl_events()` { #invokeddlbase-with-ddl-events }

```python
InvokeDDLBase.with_ddl_events(target, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টের DDL-এর আগে-পরে `before_create`/`after_create` (বা drop) ইভেন্ট ছোড়ার context manager।

**উদাহরণ:**

```python
print(callable(InvokeDDLBase.with_ddl_events))   # True
```

## টাইপ, ইভেন্ট ও inspection-এর সহায়ক { #adapt-type-group }

## `adapt_type()` { #adapt-type }

```python
from sqlalchemy.types import adapt_type
```

```python
adapt_type(typeobj, colspecs)
```

**ধরন:** ফাংশন

একটি সাধারণ টাইপকে একটি ডায়ালেক্টের `colspecs` অনুযায়ী বিশেষ টাইপে বদলায় (`dialect.type_descriptor()` ভেতরে এটি ডাকে)। ডায়ালেক্ট লেখকদের জন্য।

**উদাহরণ:**

```python
from sqlalchemy import DateTime
from sqlalchemy.dialects import sqlite
print(type(adapt_type(DateTime(), sqlite.dialect().colspecs)).__module__.split(".")[2])   # sqlite
```

### `adapt_type()`-এর সব প্যারামিটার { #adapt-type-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `typeobj` | টাইপ (ক্লাস বা অবজেক্ট)। |
| `colspecs` | সাধারণ টাইপ → বিশেষ টাইপের ম্যাপ। |

## `to_instance()` { #to-instance }

```python
from sqlalchemy.types import to_instance
```

```python
to_instance(typeobj, *arg, **kw)
```

**ধরন:** ফাংশন

টাইপের **ক্লাস** দিলে অবজেক্ট বানায় (`Integer` → `Integer()`), অবজেক্ট দিলে সেটাই, `None` দিলে `NullType()`। নিজের ফাংশনে "টাইপ" আর্গুমেন্ট নিতে যেখানে ক্লাস বা অবজেক্ট দুটোই চলবে।

**উদাহরণ:**

```python
print(repr(to_instance(Integer)), repr(to_instance(String(5))), repr(to_instance(None)))   # Integer() String(length=5) NullType()
```

### `to_instance()`-এর সব প্যারামিটার { #to-instance-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `typeobj` | টাইপের ক্লাস, অবজেক্ট বা `None`। |
| `arg` | ক্লাস হলে কনস্ট্রাক্টরের আর্গুমেন্ট। |
| `kw` | ক্লাস হলে কনস্ট্রাক্টরের কীওয়ার্ড। |

## `SchemaEventTarget` { #schemaeventtarget }

```python
from sqlalchemy.events import SchemaEventTarget
```

[`DDLEvents`](events.md#ddlevents) গ্রহণ করে এমন অবজেক্টের মূল ক্লাস: `Table`, `Column`, `MetaData`, কনস্ট্রেইন্ট, `SchemaType` টাইপ। যেমন `before_create`, `after_parent_attach`, `column_reflect`।

**উদাহরণ:**

```python
from sqlalchemy.events import SchemaEventTarget
print(isinstance(users, SchemaEventTarget), isinstance(users.c.id, SchemaEventTarget), isinstance(m, SchemaEventTarget))   # True True True
```

## `EventTarget` { #eventtarget }

```python
from sqlalchemy.event import EventTarget
```

`event.listen()` যাদের ওপর কাজ করে তাদের মূল ক্লাস: `Engine`, `Connection`, `Pool`, `Table`, `Session`, `Mapper`, `InstrumentedAttribute` …। প্রতিটির `dispatch` অ্যাট্রিবিউটে ইভেন্টের তালিকা।

**উদাহরণ:**

```python
print([isinstance(x, EventTarget) for x in (engine, users, engine.pool)])   # [True, True, True]
```

## `Events` { #events }

```python
from sqlalchemy.event import Events
```

একটি টার্গেট-টাইপের ইভেন্টগুলো সংজ্ঞায়িত করার মূল ক্লাস: `ConnectionEvents`, `PoolEvents`, `SessionEvents` … সবই এর subclass। নিজের ইভেন্ট-ব্যবস্থা বানাতে (লাইব্রেরি লেখকদের জন্য)।

**উদাহরণ:**

```python
from sqlalchemy.events import ConnectionEvents, PoolEvents
print(issubclass(ConnectionEvents, Events), issubclass(PoolEvents, Events))   # True True
```

## `dispatcher` { #dispatcher }

```python
from sqlalchemy.event import dispatcher
```

(অভ্যন্তরীণ) টার্গেট ক্লাসের `dispatch` অ্যাট্রিবিউটের descriptor: ক্লাস-লেভেলে ইভেন্টের তালিকা, অবজেক্ট-লেভেলে সেই অবজেক্টের listener-সমেত নতুন dispatch দেয়।

**উদাহরণ:**

```python
owner = next(k for k in Table.__mro__ if "dispatch" in k.__dict__)   # descriptor-টি কোন মূল ক্লাসে বসানো
print(owner.__name__, isinstance(owner.__dict__["dispatch"], dispatcher))   # SchemaEventTarget True
```

### কনস্ট্রাক্টরের প্যারামিটার { #dispatcher-params }

```python
dispatcher(events)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `events` | কোন `Events` ক্লাসের ইভেন্ট। |

## `RefCollection` { #refcollection }

```python
from sqlalchemy.event import RefCollection
```

(অভ্যন্তরীণ) ইভেন্ট-listener-এর সংগ্রহের মূল ক্লাস; নিজের weak reference (`ref`) রাখে যাতে টার্গেট মুছে গেলে listener-ও মুছে যায়।

**উদাহরণ:**

```python
print(sorted(c.__name__ for c in RefCollection.__subclasses__()))   # ['_ClsLevelDispatch', '_InstanceLevelDispatch']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #refcollection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`ref`](#refcollection-ref) | অ্যাট্রিবিউট (internal) | এই সংগ্রহের weak reference। |

### `RefCollection.ref` { #refcollection-ref }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই সংগ্রহের weak reference।

**উদাহরণ:**

```python
print(hasattr(RefCollection, "ref"))   # True
```

## `Inspectable` { #inspectable }

```python
from sqlalchemy.inspection import Inspectable
```

টাইপ-হিন্টের জন্য: `inspect(x)` কোন ধরনের অবজেক্ট দেবে তা টাইপ-চেকারকে জানানোর জেনেরিক ক্লাস (যেমন `Engine` হলো `Inspectable[Inspector]`)।

**উদাহরণ:**

```python
print(isinstance(engine, Inspectable), type(inspect(engine)).__name__)   # True Inspector
```

## `BaseRow` { #baserow }

```python
from sqlalchemy import BaseRow
```

(অভ্যন্তরীণ) [`Row`](result.md#row)-এর দ্রুত (Cython-এ লেখা) মূল ক্লাস: রো-র মান রাখা আর key দিয়ে খোঁজা এখানে। নিজের কোডে সবসময় `Row`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    row = conn.execute(select(users.c.id, users.c.name)).first()
    print(isinstance(row, BaseRow), type(row).__name__, tuple(row))   # True Row (1, 'রহিম')
```
