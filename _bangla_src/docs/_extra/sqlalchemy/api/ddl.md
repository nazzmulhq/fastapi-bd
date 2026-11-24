# DDL API: CreateTable, CreateView, DDL, AddConstraint … { #api-ddl }

/// note | এই পেজে যা আছে

ডেটাবেসের **গঠন** বদলানোর স্টেটমেন্ট (DDL) বানানোর সব ক্লাস ও তাদের সদস্য:

* `DDL` (কাঁচা DDL), `ExecutableDDLElement` (সবার মূল), `BaseDDLElement`, আর পুরোনো নাম `DDLElement`।
* টেবিল: `CreateTable`, `DropTable`, আর ২.১-এর নতুন `CreateTableAs`, `CreateView`, `DropView`।
* `CreateIndex`, `DropIndex`, `AddConstraint`, `DropConstraint`, `CreateSchema`, `DropSchema`, `CreateSequence`, `DropSequence`, `CreateColumn`।
* comment: `SetTableComment`, `DropTableComment`, `SetColumnComment`, `DropColumnComment`, `SetConstraintComment`, `DropConstraintComment`।
* `HasConditionalDDL`।

///

সাধারণত `metadata.create_all()` বা Alembic মাইগ্রেশন এগুলো ভেতরে ব্যবহার করে। নিজে ব্যবহার করবেন তখন, যখন: তৈরি হওয়া SQL দেখতে চান (`print(CreateTable(t))`), একটি নির্দিষ্ট অবজেক্ট আলাদা করে তৈরি/মুছতে চান, `IF NOT EXISTS` লাগবে, বা টেবিল তৈরির পর বাড়তি SQL (trigger, extension) চালাতে চান (`DDL` + event)। প্রতিটি অবজেক্ট `conn.execute(...)` দিয়ে চালানো যায়।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
md = MetaData()
users = Table("users", md,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), comment="পুরো নাম"),
    Column("active", Boolean, server_default=true()),
    CheckConstraint("length(name) > 0", name="ck_name_nonempty"),
)
ix_name = Index("ix_users_name", users.c.name)
```

`pg(ddl)` PostgreSQL-এর জন্য তৈরি SQL দেখায়; `run(ddl)` সেটি চালায়। প্রতিটি উদাহরণ খালি PostgreSQL 16 ডেটাবেসে চালিয়ে দেখা।

///

## মূল ক্লাস ও কাঁচা DDL { #executableddlelement-group }

## `ExecutableDDLElement` { #executableddlelement }

```python
from sqlalchemy.schema import ExecutableDDLElement
```

চালানো যায় এমন সব DDL অবজেক্টের মূল ক্লাস (`CreateTable`, `DDL` …)। `conn.execute(ddl)` দিয়ে চলে, আর `against()` / `execute_if()` দিয়ে event-এ শর্তসাপেক্ষে বসানো যায়।

**উদাহরণ:**

```python
print(isinstance(CreateTable(users), ExecutableDDLElement), isinstance(DDL("SELECT 1"), ExecutableDDLElement))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #executableddlelement-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`against()`](#executableddlelement-against) | মেথড | একটি টার্গেট (টেবিল/কনস্ট্রেইন্ট) বসানো কপি দেয়; ফলে `DDL`-এর ভেতরে `%(table)s` ইত্যাদি টোকেন সেই টেবিলের নামে বদলায়। |
| [`execute_if()`](#executableddlelement-execute-if) | মেথড | শর্তসাপেক্ষে চালানোর মোড়ক দেয়: শুধু নির্দিষ্ট ডায়ালেক্টে (`dialect="postgresql"`), বা একটি ফাংশন `True` দিলে। |
| [`target`](#executableddlelement-target) | অ্যাট্রিবিউট | `against()` বা event-এর মাধ্যমে বসানো টার্গেট অবজেক্ট (না থাকলে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ExecutableDDLElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

### `ExecutableDDLElement.against()` { #executableddlelement-against }

```python
ExecutableDDLElement.against(target)
```

**ধরন:** মেথড

একটি টার্গেট (টেবিল/কনস্ট্রেইন্ট) বসানো কপি দেয়; ফলে `DDL`-এর ভেতরে `%(table)s` ইত্যাদি টোকেন সেই টেবিলের নামে বদলায়।

**উদাহরণ:**

```python
d = DDL("COMMENT ON TABLE %(table)s IS 'ইউজার টেবিল'").against(users)
pg(d)   # COMMENT ON TABLE users IS 'ইউজার টেবিল'
```

### `ExecutableDDLElement.execute_if()` { #executableddlelement-execute-if }

```python
ExecutableDDLElement.execute_if(dialect=None, callable_=None, state=None)
```

**ধরন:** মেথড

শর্তসাপেক্ষে চালানোর মোড়ক দেয়: শুধু নির্দিষ্ট ডায়ালেক্টে (`dialect="postgresql"`), বা একটি ফাংশন `True` দিলে। সাধারণত `after_create`/`before_drop` event listener হিসেবে বসানো হয়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("docs", m, Column("id", Integer, primary_key=True), Column("body", String))
event.listen(t, "after_create",
             DDL("CREATE INDEX ix_docs_fts ON docs USING gin (to_tsvector('simple', body))").execute_if(dialect="postgresql"))
m.create_all(engine)
print([i["name"] for i in inspect(engine).get_indexes("docs")])   # ['ix_docs_fts']
```

### `ExecutableDDLElement.target` { #executableddlelement-target }

**ধরন:** অ্যাট্রিবিউট

`against()` বা event-এর মাধ্যমে বসানো টার্গেট অবজেক্ট (না থাকলে `None`)।

**উদাহরণ:**

```python
print(DDL("x").against(users).target.name)   # users
```

## `DDL` { #ddl }

```python
from sqlalchemy import DDL
```

কাঁচা DDL স্ট্রিং চালানোর অবজেক্ট: trigger, extension, function, বা SQLAlchemy যা নিজে বানায় না এমন যেকোনো কিছু। `%(table)s`, `%(schema)s`, `%(fullname)s` টোকেন টার্গেটের নামে বদলায় (তাই আসল `%` লিখতে `%%`)। সাধারণত টেবিলের `after_create` event-এ যুক্ত করা হয়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("posts", m, Column("id", Integer, primary_key=True), Column("updated", Integer))
event.listen(t, "after_create", DDL("COMMENT ON TABLE %(table)s IS 'ব্লগ পোস্ট'"))
m.create_all(engine)
print(inspect(engine).get_table_comment("posts")["text"])   # ব্লগ পোস্ট
```

### কনস্ট্রাক্টরের প্যারামিটার { #ddl-params }

```python
DDL(statement, context=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `statement` | DDL স্ট্রিং; `%(table)s` ইত্যাদি টোকেন থাকতে পারে। |
| `context` | টোকেন বদলানোর জন্য বাড়তি মানের dict। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #ddl-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`context`](#ddl-context) | অ্যাট্রিবিউট | টোকেনের বাড়তি মানগুলো। |
| [`statement`](#ddl-statement) | অ্যাট্রিবিউট | মূল DDL স্ট্রিং। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DDL`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

### `DDL.context` { #ddl-context }

**ধরন:** অ্যাট্রিবিউট

টোকেনের বাড়তি মানগুলো।

**উদাহরণ:**

```python
d = DDL("CREATE SCHEMA %(name)s", context={"name": "reports"})
pg(d)   # CREATE SCHEMA reports
```

### `DDL.statement` { #ddl-statement }

**ধরন:** অ্যাট্রিবিউট

মূল DDL স্ট্রিং।

**উদাহরণ:**

```python
print(DDL("VACUUM ANALYZE").statement)   # VACUUM ANALYZE
```

## `BaseDDLElement` { #baseddlelement }

```python
from sqlalchemy.schema import BaseDDLElement
```

সব DDL কনস্ট্রাক্টের (চালানো যায় না এমন `CreateColumn` সহ) সবচেয়ে নিচের মূল ক্লাস। নিজস্ব নতুন সদস্য নেই।

**উদাহরণ:**

```python
print(issubclass(CreateColumn, BaseDDLElement), issubclass(CreateTable, BaseDDLElement))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #baseddlelement-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `BaseDDLElement`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params)

///

## `DDLElement` { #ddlelement }

```python
from sqlalchemy.schema import DDLElement
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`ExecutableDDLElement`-এর পুরোনো নাম (২.০-তে নাম বদলেছে); একই ক্লাস।

**উদাহরণ:**

```python
print(DDLElement is ExecutableDDLElement)   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`ExecutableDDLElement`](#executableddlelement-summary)-এর মতো।

## `HasConditionalDDL` { #hasconditionalddl }

```python
from sqlalchemy.schema import HasConditionalDDL
```

যেসব স্কিমা অবজেক্টে শর্তসাপেক্ষ DDL দেওয়া যায় (`Index`, `Constraint`) তাদের মিক্সিন। একমাত্র সদস্য `ddl_if()`; ব্যাখ্যা [কনস্ট্রেইন্ট পেজে](constraints.md#constraint-ddl-if)।

**উদাহরণ:**

```python
print(isinstance(ix_name, HasConditionalDDL), isinstance(ck(), HasConditionalDDL))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hasconditionalddl-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `HasConditionalDDL`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Constraint` থেকে:** [`ddl_if()`](constraints.md#constraint-ddl-if)

///

## টেবিল ও ভিউ { #createtable-group }

## `CreateTable` { #createtable }

```python
from sqlalchemy.schema import CreateTable
```

একটি টেবিলের `CREATE TABLE` (কলাম, primary key, কনস্ট্রেইন্টসহ; ইনডেক্স আলাদা)। `print()` করে SQL দেখার সবচেয়ে সহজ উপায়, মাইগ্রেশন লেখার আগে যাচাইয়ে কাজে লাগে।

**উদাহরণ:**

```python
pg(CreateTable(users, if_not_exists=True))
# CREATE TABLE IF NOT EXISTS users (
# 	id SERIAL NOT NULL,
# 	name VARCHAR(50),
# 	active BOOLEAN DEFAULT true,
# 	PRIMARY KEY (id),
# 	CONSTRAINT ck_name_nonempty CHECK (length(name) > 0)
# )
```

### কনস্ট্রাক্টরের প্যারামিটার { #createtable-params }

```python
CreateTable(element, include_foreign_key_constraints=None, if_not_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Table`। |
| `include_foreign_key_constraints` | কোন ফরেন কি কনস্ট্রেইন্টগুলো CREATE-এর ভেতরে বসবে (তালিকা); `None` মানে সব। বাকিগুলো পরে `AddConstraint` দিয়ে যোগ করতে। |
| `if_not_exists` | `True` দিলে `CREATE TABLE IF NOT EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createtable-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`columns`](#createtable-columns) | অ্যাট্রিবিউট | প্রতিটি কলামের জন্য একটি `CreateColumn`-এর তালিকা। |
| [`element`](#createtable-element) | অ্যাট্রিবিউট | যে স্কিমা-অবজেক্টের DDL (এখানে টেবিল)। |
| [`if_not_exists`](#createtable-if-not-exists) | অ্যাট্রিবিউট | `IF NOT EXISTS` বসবে কি না। |
| [`include_foreign_key_constraints`](#createtable-include-foreign-key-constraints) | অ্যাট্রিবিউট | কনস্ট্রাক্টরে দেওয়া FK-তালিকা (না দিলে `None`)। |
| [`to_metadata()`](#createtable-to-metadata) | মেথড (internal) | `Table.to_metadata()` দিয়ে টেবিল কপির সময় `set_creator_ddl()`-এ দেওয়া DDL-টিও নতুন টেবিলের জন্য কপি করতে ব্যবহৃত হয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateTable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

///

### `CreateTable.columns` { #createtable-columns }

**ধরন:** অ্যাট্রিবিউট

প্রতিটি কলামের জন্য একটি `CreateColumn`-এর তালিকা।

**উদাহরণ:**

```python
print([type(c).__name__ for c in CreateTable(users).columns][:2])   # ['CreateColumn', 'CreateColumn']
```

### `CreateTable.element` { #createtable-element }

**ধরন:** অ্যাট্রিবিউট

যে স্কিমা-অবজেক্টের DDL (এখানে টেবিল)।

**উদাহরণ:**

```python
print(CreateTable(users).element.name)   # users
```

### `CreateTable.if_not_exists` { #createtable-if-not-exists }

**ধরন:** অ্যাট্রিবিউট

`IF NOT EXISTS` বসবে কি না।

**উদাহরণ:**

```python
print(CreateTable(users, if_not_exists=True).if_not_exists)   # True
```

### `CreateTable.include_foreign_key_constraints` { #createtable-include-foreign-key-constraints }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরে দেওয়া FK-তালিকা (না দিলে `None`)।

**উদাহরণ:**

```python
print(CreateTable(users).include_foreign_key_constraints)   # None
```

### `CreateTable.to_metadata()` { #createtable-to-metadata }

```python
CreateTable.to_metadata(metadata, table)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Table.to_metadata()` দিয়ে টেবিল কপির সময় `set_creator_ddl()`-এ দেওয়া DDL-টিও নতুন টেবিলের জন্য কপি করতে ব্যবহৃত হয়।

## `DropTable` { #droptable }

```python
from sqlalchemy.schema import DropTable
```

একটি টেবিলের `DROP TABLE`।

**উদাহরণ:**

```python
users.create(engine)
run(DropTable(users), DropTable(users, if_exists=True))   # দ্বিতীয়টি IF EXISTS, তাই এরর নেই
print(inspect(engine).has_table("users"))   # False
```

### কনস্ট্রাক্টরের প্যারামিটার { #droptable-params }

```python
DropTable(element, if_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Table`। |
| `if_exists` | `True` দিলে `DROP TABLE IF EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #droptable-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`if_exists`](#droptable-if-exists) | অ্যাট্রিবিউট | `IF EXISTS` বসবে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropTable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`to_metadata()`](#createtable-to-metadata)

///

### `DropTable.if_exists` { #droptable-if-exists }

**ধরন:** অ্যাট্রিবিউট

`IF EXISTS` বসবে কি না।

**উদাহরণ:**

```python
print(DropTable(users, if_exists=True).if_exists)   # True
```

## `CreateTableAs` { #createtableas }

```python
from sqlalchemy.schema import CreateTableAs
```

(২.১-এ নতুন) `CREATE TABLE নাম AS SELECT ...`: একটি SELECT-এর ফল থেকে নতুন টেবিল (গঠন + ডেটা) বানায়। ভিউ নয়: পরে মূল টেবিল বদলালে এটি বদলায় না (রিপোর্টের snapshot, ব্যাকআপ)। `.table`-এ নতুন টেবিলের `Table` অবজেক্ট সাথে সাথেই পাওয়া যায়।

**উদাহরণ:**

```python
users.create(engine)
run(insert(users).values(name="রহিম"), insert(users).values(name="করিম", active=False))
cta = CreateTableAs(select(users.c.id, users.c.name).where(users.c.active), "active_users")
run(cta)
with engine.connect() as conn:
    print(conn.execute(select(cta.table.c.name)).scalars().all())   # ['রহিম']
```

### কনস্ট্রাক্টরের প্যারামিটার { #createtableas-params }

```python
CreateTableAs(selectable, table_name, *, metadata=None, schema=None, temporary=False, if_not_exists=False, **dialect_kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | যে `select()` থেকে টেবিল বানানো হবে। |
| `table_name` | নতুন টেবিলের নাম। |
| `metadata` | দিলে নতুন `Table`-টি এই MetaData-তে নিবন্ধিত হয় (তখন `create_all()`-এও তৈরি হয়)। |
| `schema` | নতুন টেবিলের স্কিমা। |
| `temporary` | `True` দিলে `CREATE TEMPORARY TABLE ... AS`। |
| `if_not_exists` | `True` দিলে `IF NOT EXISTS`। |
| `dialect_kwargs` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createtableas-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`element`](#createtableas-element) | প্রপার্টি | ভেতরে বানানো নতুন `Table` (অর্থাৎ `table`)। |
| [`metadata`](#createtableas-metadata) | অ্যাট্রিবিউট | নিবন্ধিত `MetaData` (না দিলে একটি আলাদা নতুন MetaData)। |
| [`schema`](#createtableas-schema) | অ্যাট্রিবিউট | নতুন টেবিলের স্কিমা। |
| [`selectable`](#createtableas-selectable) | অ্যাট্রিবিউট | উৎস `select()`। |
| [`table`](#createtableas-table) | অ্যাট্রিবিউট | নতুন টেবিলের `Table` অবজেক্ট, SELECT-এর কলাম থেকে বানানো; এখনই কুয়েরিতে ব্যবহারযোগ্য। |
| [`table_name`](#createtableas-table-name) | অ্যাট্রিবিউট | নতুন টেবিলের নাম। |
| [`temporary`](#createtableas-temporary) | অ্যাট্রিবিউট | `TEMPORARY` কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateTableAs`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`description`](schema.md#table-description) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`CreateTable` থেকে:** [`if_not_exists`](#createtable-if-not-exists) · [`to_metadata()`](#createtable-to-metadata)

///

### `CreateTableAs.element` { #createtableas-element }

**ধরন:** প্রপার্টি

ভেতরে বানানো নতুন `Table` (অর্থাৎ `table`)।

**উদাহরণ:**

```python
cta = CreateTableAs(select(users.c.id), "snap")
print(cta.element is cta.table)   # True
```

### `CreateTableAs.metadata` { #createtableas-metadata }

**ধরন:** অ্যাট্রিবিউট

নিবন্ধিত `MetaData` (না দিলে একটি আলাদা নতুন MetaData)।

**উদাহরণ:**

```python
m = MetaData()
print(CreateTableAs(select(users.c.id), "snap", metadata=m).metadata is m)   # True
```

### `CreateTableAs.schema` { #createtableas-schema }

**ধরন:** অ্যাট্রিবিউট

নতুন টেবিলের স্কিমা।

**উদাহরণ:**

```python
print(CreateTableAs(select(users.c.id), "snap", schema="reports").schema)   # reports
```

### `CreateTableAs.selectable` { #createtableas-selectable }

**ধরন:** অ্যাট্রিবিউট

উৎস `select()`।

**উদাহরণ:**

```python
print(CreateTableAs(select(users.c.id), "snap").selectable)   # SELECT users.id FROM users
```

### `CreateTableAs.table` { #createtableas-table }

**ধরন:** অ্যাট্রিবিউট

নতুন টেবিলের `Table` অবজেক্ট, SELECT-এর কলাম থেকে বানানো; এখনই কুয়েরিতে ব্যবহারযোগ্য।

**উদাহরণ:**

```python
cta = CreateTableAs(select(users.c.id, users.c.name), "snap")
print([c.name for c in cta.table.c])   # ['id', 'name']
```

### `CreateTableAs.table_name` { #createtableas-table-name }

**ধরন:** অ্যাট্রিবিউট

নতুন টেবিলের নাম।

**উদাহরণ:**

```python
print(CreateTableAs(select(users.c.id), "snap").table_name)   # snap
```

### `CreateTableAs.temporary` { #createtableas-temporary }

**ধরন:** অ্যাট্রিবিউট

`TEMPORARY` কি না।

**উদাহরণ:**

```python
print(CreateTableAs(select(users.c.id), "snap", temporary=True).temporary)   # True
```

## `CreateView` { #createview }

```python
from sqlalchemy.schema import CreateView
```

(২.১-এ নতুন) `CREATE VIEW নাম AS SELECT ...`: একটি সংরক্ষিত কুয়েরি যা টেবিলের মতো পড়া যায়; প্রতিবার পড়ার সময় SELECT নতুন করে চলে। `materialized=True` দিলে `MATERIALIZED VIEW` (ফল সংরক্ষিত; PostgreSQL-এ `REFRESH MATERIALIZED VIEW` দিয়ে হালনাগাদ)। `.table`-এ ভিউয়ের `Table` অবজেক্ট (তার `is_view` = `True`)।

**উদাহরণ:**

```python
users.create(engine)
run(insert(users).values(name="রহিম"), insert(users).values(name="করিম", active=False))
cv = CreateView(select(users.c.id, users.c.name).where(users.c.active), "active_users_v", or_replace=True)
run(cv)
run(insert(users).values(name="সুমি"))          # ভিউ নিজে থেকেই হালনাগাদ থাকে
with engine.connect() as conn:
    print(conn.execute(select(cv.table.c.name).order_by(cv.table.c.id)).scalars().all())   # ['রহিম', 'সুমি']
print(cv.table.is_view, inspect(engine).get_view_names())   # True ['active_users_v']
```

### কনস্ট্রাক্টরের প্যারামিটার { #createview-params }

```python
CreateView(selectable, view_name, *, metadata=None, schema=None, temporary=False, or_replace=False, materialized=False, **dialect_kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | ভিউয়ের `select()`। |
| `view_name` | ভিউয়ের নাম। |
| `metadata` | দিলে ভিউয়ের `Table` এই MetaData-তে নিবন্ধিত হয় (`create_all()`-এ ভিউও তৈরি হয়)। |
| `schema` | স্কিমা। |
| `temporary` | `True` দিলে `TEMPORARY VIEW`। |
| `or_replace` | `True` দিলে `CREATE OR REPLACE VIEW` (থাকলে বদলায়)। |
| `materialized` | `True` দিলে `MATERIALIZED VIEW`। |
| `dialect_kwargs` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createview-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`materialized`](#createview-materialized) | অ্যাট্রিবিউট | materialized view কি না। |
| [`or_replace`](#createview-or-replace) | অ্যাট্রিবিউট | `OR REPLACE` বসবে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateView`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`Table` থেকে:** [`argument_for()`](schema.md#table-argument-for) · [`description`](schema.md#table-description) · [`dialect_kwargs`](schema.md#table-dialect-kwargs) · [`dialect_options`](schema.md#table-dialect-options) · [`get_dialect_option()`](schema.md#table-get-dialect-option) · [`kwargs`](schema.md#table-kwargs) · [`reflect_only_elements`](schema.md#table-reflect-only-elements)

**`CreateTableAs` থেকে:** [`element`](#createtableas-element) · [`metadata`](#createtableas-metadata) · [`schema`](#createtableas-schema) · [`selectable`](#createtableas-selectable) · [`table`](#createtableas-table) · [`table_name`](#createtableas-table-name) · [`temporary`](#createtableas-temporary)

**`CreateTable` থেকে:** [`if_not_exists`](#createtable-if-not-exists) · [`to_metadata()`](#createtable-to-metadata)

///

### `CreateView.materialized` { #createview-materialized }

**ধরন:** অ্যাট্রিবিউট

materialized view কি না।

**উদাহরণ:**

```python
cv = CreateView(select(users.c.id), "mv", materialized=True)
pg(cv)   # CREATE MATERIALIZED VIEW mv AS SELECT users.id FROM users
```

### `CreateView.or_replace` { #createview-or-replace }

**ধরন:** অ্যাট্রিবিউট

`OR REPLACE` বসবে কি না।

**উদাহরণ:**

```python
print(CreateView(select(users.c.id), "v", or_replace=True).or_replace)   # True
```

## `DropView` { #dropview }

```python
from sqlalchemy.schema import DropView
```

(২.১-এ পাবলিক হয়েছে) `DROP VIEW` (`materialized=True` দিলে `DROP MATERIALIZED VIEW`)। ভিউয়ের `Table` অবজেক্ট দিন।

**উদাহরণ:**

```python
users.create(engine)
cv = CreateView(select(users.c.id), "v_ids")
run(cv, DropView(cv.table, if_exists=True))
print(inspect(engine).get_view_names())   # []
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropview-params }

```python
DropView(element, *, if_exists=False, materialized=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | ভিউয়ের `Table`। |
| `if_exists` | `IF EXISTS`। |
| `materialized` | materialized view মুছতে `True`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropview-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropView`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`to_metadata()`](#createtable-to-metadata)

**`DropTable` থেকে:** [`if_exists`](#droptable-if-exists)

**`CreateView` থেকে:** [`materialized`](#createview-materialized)

///

## ইনডেক্স, কনস্ট্রেইন্ট, স্কিমা ও sequence { #createindex-group }

## `CreateIndex` { #createindex }

```python
from sqlalchemy.schema import CreateIndex
```

একটি ইনডেক্সের `CREATE INDEX`।

**উদাহরণ:**

```python
pg(CreateIndex(ix_name, if_not_exists=True))   # CREATE INDEX IF NOT EXISTS ix_users_name ON users (name)
```

### কনস্ট্রাক্টরের প্যারামিটার { #createindex-params }

```python
CreateIndex(element, if_not_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Index`। |
| `if_not_exists` | `IF NOT EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createindex-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateIndex`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`if_not_exists`](#createtable-if-not-exists)

///

## `DropIndex` { #dropindex }

```python
from sqlalchemy.schema import DropIndex
```

একটি ইনডেক্সের `DROP INDEX`।

**উদাহরণ:**

```python
pg(DropIndex(ix_name, if_exists=True))   # DROP INDEX IF EXISTS ix_users_name
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropindex-params }

```python
DropIndex(element, if_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Index`। |
| `if_exists` | `IF EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropindex-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropIndex`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

**`DropTable` থেকে:** [`if_exists`](#droptable-if-exists)

///

## `AddConstraint` { #addconstraint }

```python
from sqlalchemy.schema import AddConstraint
```

`ALTER TABLE ... ADD CONSTRAINT`: বিদ্যমান টেবিলে কনস্ট্রেইন্ট যোগ। ডিফল্টে (`isolate_from_table=True`) কনস্ট্রেইন্টটিকে টেবিলের CREATE TABLE থেকে আলাদা করে দেয়, যাতে পরে দুবার তৈরি না হয়।

**উদাহরণ:**

```python
m = MetaData()
t = Table("items", m, Column("id", Integer, primary_key=True), Column("sku", String(20)))
t.create(engine)
uq = UniqueConstraint(t.c.sku, name="uq_items_sku")
pg(AddConstraint(uq))   # ALTER TABLE items ADD CONSTRAINT uq_items_sku UNIQUE (sku)
run(AddConstraint(uq))
print([u["name"] for u in inspect(engine).get_unique_constraints("items")])   # ['uq_items_sku']
```

### কনস্ট্রাক্টরের প্যারামিটার { #addconstraint-params }

```python
AddConstraint(element, *, isolate_from_table=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে কনস্ট্রেইন্ট। |
| `isolate_from_table` | `True` (ডিফল্ট) হলে কনস্ট্রেইন্টটি টেবিলের CREATE TABLE-এ আর বসবে না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #addconstraint-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AddConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`if_not_exists`](#createtable-if-not-exists)

///

## `DropConstraint` { #dropconstraint }

```python
from sqlalchemy.schema import DropConstraint
```

`ALTER TABLE ... DROP CONSTRAINT`। নাম থাকা কনস্ট্রেইন্টেই কাজ করে (তাই naming convention জরুরি)।

**উদাহরণ:**

```python
users.create(engine)
pg(DropConstraint(ck(), if_exists=True, cascade=True))   # ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_name_nonempty CASCADE
run(DropConstraint(ck()))
print(inspect(engine).get_check_constraints("users"))   # []
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropconstraint-params }

```python
DropConstraint(element, *, cascade=False, if_exists=False, isolate_from_table=_NoArg.NO_ARG, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে কনস্ট্রেইন্ট। |
| `cascade` | `True` দিলে `CASCADE` (নির্ভরশীল অবজেক্টও মুছবে)। |
| `if_exists` | `IF EXISTS`। |
| `isolate_from_table` | `True` দিলে কনস্ট্রেইন্টটি টেবিলের পরের CREATE TABLE-এ আর বসবে না। |
| `kw` | ডায়ালেক্ট-নির্দিষ্ট অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropconstraint-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cascade`](#dropconstraint-cascade) | অ্যাট্রিবিউট | `CASCADE` বসবে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropConstraint`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

**`DropTable` থেকে:** [`if_exists`](#droptable-if-exists)

///

### `DropConstraint.cascade` { #dropconstraint-cascade }

**ধরন:** অ্যাট্রিবিউট

`CASCADE` বসবে কি না।

**উদাহরণ:**

```python
print(DropConstraint(ck(), cascade=True).cascade)   # True
```

## `CreateSchema` { #createschema }

```python
from sqlalchemy.schema import CreateSchema
```

`CREATE SCHEMA নাম`।

**উদাহরণ:**

```python
run(CreateSchema("reports", if_not_exists=True), CreateSchema("reports", if_not_exists=True))
print("reports" in inspect(engine).get_schema_names())   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #createschema-params }

```python
CreateSchema(name, if_not_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | স্কিমার নাম। |
| `if_not_exists` | `IF NOT EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createschema-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateSchema`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`if_not_exists`](#createtable-if-not-exists)

///

## `DropSchema` { #dropschema }

```python
from sqlalchemy.schema import DropSchema
```

`DROP SCHEMA নাম` (`cascade=True` দিলে ভেতরের সব টেবিলসহ)।

**উদাহরণ:**

```python
run(CreateSchema("reports"), DropSchema("reports", cascade=True, if_exists=True))
print("reports" in inspect(engine).get_schema_names())   # False
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropschema-params }

```python
DropSchema(name, cascade=False, if_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | স্কিমার নাম। |
| `cascade` | `CASCADE`। |
| `if_exists` | `IF EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropschema-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৩টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropSchema`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`DropConstraint` থেকে:** [`cascade`](#dropconstraint-cascade)

**`CreateTable` থেকে:** [`element`](#createtable-element)

**`DropTable` থেকে:** [`if_exists`](#droptable-if-exists)

///

## `CreateSequence` { #createsequence }

```python
from sqlalchemy.schema import CreateSequence
```

`CREATE SEQUENCE`।

**উদাহরণ:**

```python
pg(CreateSequence(Sequence("order_seq", start=1000, increment=5)))   # CREATE SEQUENCE order_seq INCREMENT BY 5 START WITH 1000
```

### কনস্ট্রাক্টরের প্যারামিটার { #createsequence-params }

```python
CreateSequence(element, if_not_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Sequence`। |
| `if_not_exists` | `IF NOT EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createsequence-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateSequence`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element) · [`if_not_exists`](#createtable-if-not-exists)

///

## `DropSequence` { #dropsequence }

```python
from sqlalchemy.schema import DropSequence
```

`DROP SEQUENCE`।

**উদাহরণ:**

```python
pg(DropSequence(Sequence("order_seq"), if_exists=True))   # DROP SEQUENCE IF EXISTS order_seq
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropsequence-params }

```python
DropSequence(element, if_exists=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Sequence`। |
| `if_exists` | `IF EXISTS`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropsequence-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropSequence`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

**`DropTable` থেকে:** [`if_exists`](#droptable-if-exists)

///

## `CreateColumn` { #createcolumn }

```python
from sqlalchemy.schema import CreateColumn
```

CREATE TABLE-এর ভেতরে একটি কলামের অংশ। নিজে চালানো যায় না; `sqlalchemy.ext.compiler`-এর `@compiles(CreateColumn)` দিয়ে কলামের DDL বদলাতে (যেমন কিছু কলাম বাদ দিতে বা বাড়তি শব্দ বসাতে) ব্যবহার হয়।

**উদাহরণ:**

```python
from sqlalchemy.ext.compiler import compiles

@compiles(CreateColumn, "postgresql")
def _maybe_skip(element, compiler, **kw):
    if element.element.info.get("skip_ddl"):
        return None                      # এই কলাম CREATE TABLE-এ বসবে না
    return compiler.visit_create_column(element, **kw)

t = Table("t", MetaData(), Column("id", Integer, primary_key=True), Column("tmp", Integer, info={"skip_ddl": True}))
print("tmp" in str(CreateTable(t).compile(dialect=postgresql.dialect())))   # False
```

### কনস্ট্রাক্টরের প্যারামিটার { #createcolumn-params }

```python
CreateColumn(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Column`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #createcolumn-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CreateColumn`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`compare()`](elements.md#columnelement-compare) · [`compile()`](elements.md#columnelement-compile) · [`description`](elements.md#columnelement-description) · [`entity_namespace`](elements.md#columnelement-entity-namespace) · [`get_children()`](elements.md#columnelement-get-children) · [`inherit_cache`](elements.md#columnelement-inherit-cache) · [`is_clause_element`](elements.md#columnelement-is-clause-element) · [`is_dml`](elements.md#columnelement-is-dml) · [`is_selectable`](elements.md#columnelement-is-selectable) · [`memoized_attribute`](elements.md#columnelement-memoized-attribute) · [`memoized_instancemethod()`](elements.md#columnelement-memoized-instancemethod) · [`params()`](elements.md#columnelement-params) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`unique_params()`](elements.md#columnelement-unique-params)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## comment DDL { #settablecomment-group }

## `SetTableComment` { #settablecomment }

```python
from sqlalchemy.schema import SetTableComment
```

`COMMENT ON TABLE ... IS '...'`: টেবিলের `comment` ডেটাবেসে বসায় (টেবিল আগে থেকে থাকলে)।

**উদাহরণ:**

```python
m = MetaData()
t = Table("orders", m, Column("id", Integer, primary_key=True), comment="সব অর্ডার")
t.create(engine)
pg(SetTableComment(t))   # COMMENT ON TABLE orders IS 'সব অর্ডার'
print(inspect(engine).get_table_comment("orders")["text"])   # সব অর্ডার
```

### কনস্ট্রাক্টরের প্যারামিটার { #settablecomment-params }

```python
SetTableComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Table`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #settablecomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SetTableComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## `DropTableComment` { #droptablecomment }

```python
from sqlalchemy.schema import DropTableComment
```

টেবিলের comment মুছে দেয় (`COMMENT ON TABLE ... IS NULL`)।

**উদাহরণ:**

```python
pg(DropTableComment(users))   # COMMENT ON TABLE users IS NULL
```

### কনস্ট্রাক্টরের প্যারামিটার { #droptablecomment-params }

```python
DropTableComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Table`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #droptablecomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropTableComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## `SetColumnComment` { #setcolumncomment }

```python
from sqlalchemy.schema import SetColumnComment
```

`COMMENT ON COLUMN ... IS '...'`: কলামের `comment` বসায়।

**উদাহরণ:**

```python
pg(SetColumnComment(users.c.name))   # COMMENT ON COLUMN users.name IS 'পুরো নাম'
```

### কনস্ট্রাক্টরের প্যারামিটার { #setcolumncomment-params }

```python
SetColumnComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Column`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #setcolumncomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SetColumnComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## `DropColumnComment` { #dropcolumncomment }

```python
from sqlalchemy.schema import DropColumnComment
```

কলামের comment মুছে দেয়।

**উদাহরণ:**

```python
pg(DropColumnComment(users.c.name))   # COMMENT ON COLUMN users.name IS NULL
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropcolumncomment-params }

```python
DropColumnComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `Column`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropcolumncomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropColumnComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## `SetConstraintComment` { #setconstraintcomment }

```python
from sqlalchemy.schema import SetConstraintComment
```

(২.০) কনস্ট্রেইন্টের comment বসায় (`COMMENT ON CONSTRAINT`; PostgreSQL সমর্থন করে)।

**উদাহরণ:**

```python
c = CheckConstraint("id > 0", name="ck_pos", comment="ধনাত্মক id")
Table("t", MetaData(), Column("id", Integer, primary_key=True), c)
pg(SetConstraintComment(c))   # COMMENT ON CONSTRAINT ck_pos ON t IS 'ধনাত্মক id'
```

### কনস্ট্রাক্টরের প্যারামিটার { #setconstraintcomment-params }

```python
SetConstraintComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে কনস্ট্রেইন্ট। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #setconstraintcomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SetConstraintComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

## `DropConstraintComment` { #dropconstraintcomment }

```python
from sqlalchemy.schema import DropConstraintComment
```

কনস্ট্রেইন্টের comment মুছে দেয়।

**উদাহরণ:**

```python
pg(DropConstraintComment(ck()))   # COMMENT ON CONSTRAINT ck_name_nonempty ON users IS NULL
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropconstraintcomment-params }

```python
DropConstraintComment(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে কনস্ট্রেইন্ট। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dropconstraintcomment-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DropConstraintComment`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutableDDLElement` থেকে:** [`against()`](#executableddlelement-against) · [`execute_if()`](#executableddlelement-execute-if) · [`target`](#executableddlelement-target)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`compare()`](select.md#select-compare) · [`compile()`](select.md#select-compile) · [`description`](select.md#select-description) · [`entity_namespace`](select.md#select-entity-namespace) · [`execution_options()`](select.md#select-execution-options) · [`get_children()`](select.md#select-get-children) · [`get_execution_options()`](select.md#select-get-execution-options) · [`inherit_cache`](select.md#select-inherit-cache) · [`is_clause_element`](select.md#select-is-clause-element) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_selectable`](select.md#select-is-selectable) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`options()`](select.md#select-options) · [`params()`](select.md#select-params) · [`self_group()`](select.md#select-self-group) · [`stringify_dialect`](select.md#select-stringify-dialect) · [`supports_execution`](select.md#select-supports-execution) · [`unique_params()`](select.md#select-unique-params) · [`uses_inspection`](select.md#select-uses-inspection)

**`CreateTable` থেকে:** [`element`](#createtable-element)

///

/// check | সংক্ষেপে মনে রাখুন

* SQL দেখতে: `print(CreateTable(t).compile(dialect=postgresql.dialect()))`।
* `IF NOT EXISTS` / `IF EXISTS`: `CreateTable(t, if_not_exists=True)`, `DropTable(t, if_exists=True)` …
* টেবিল তৈরির পর বাড়তি SQL: `event.listen(t, "after_create", DDL("...").execute_if(dialect="postgresql"))`।
* ২.১: SELECT থেকে টেবিল `CreateTableAs`, ভিউ `CreateView` (materialized সহ), `DropView`।
* প্রোডাকশনে স্কিমা বদলের জন্য এগুলো হাতে না চালিয়ে Alembic মাইগ্রেশন ব্যবহার করুন।

///
