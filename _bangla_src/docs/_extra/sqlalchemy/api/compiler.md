# কম্পাইলার API: Compiled, SQLCompiler, DDLCompiler, IdentifierPreparer … { #api-compiler }

/// note | এই পেজে যা আছে

SQLAlchemy যেভাবে Python এক্সপ্রেশন থেকে SQL **স্ট্রিং** বানায় তার ভেতরের ক্লাসগুলো:

* `Compiled` আর তার মূল বাস্তবায়ন `SQLCompiler` (আর `StrSQLCompiler`), DDL-এর জন্য `DDLCompiler`।
* টাইপের নাম বানানোর `TypeCompiler`, `GenericTypeCompiler`, `StrSQLTypeCompiler`।
* নাম quote করার `IdentifierPreparer`।
* সহায়ক: `ExpandedState`, `ResultColumnsEntry`, `CacheKey`, `Linting`, `FromLinter`, `CompilerState`, `InsertmanyvaluesSentinelOpts`, `AggregateOrderByStyle`, `aggregate_orderby_inline`, `ilike_case_insensitive`, `prefix_anon_map`।

///

`stmt.compile()` বা `str(stmt)` দিলে যে অবজেক্ট পান সেটি এই `Compiled`। কম্পাইলার এক্সপ্রেশন-গাছ ঘুরে প্রতিটি অংশের জন্য একটি `visit_<নাম>()` মেথড ডাকে (`Select` → `visit_select`, `BinaryExpression` → `visit_binary`)। প্রতিটি ডায়ালেক্ট এগুলোর কয়েকটি বদলে নিজের SQL লেখে। সাধারণ অ্যাপে এদের দরকার হয় SQL দেখে ডিবাগ করতে (`compiled.string`, `compiled.params`), আর নিজের SQL কনস্ট্রাক্ট বানাতে ([`@compiles`](ext-misc.md#compiles))। শত শত `visit_*` মেথড প্রতিটি ক্লাসে নাম ধরে একটি ভাঁজ করা বক্সে তালিকা করা।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
m = MetaData()
users = Table("users", m, Column("id", Integer, primary_key=True), Column("name", String(50)))
pg = postgresql.dialect()
c = select(users).where(users.c.id == bindparam("uid")).compile(dialect=pg)   # একটি SQLCompiler
```

ডেটাবেস লাগে না; সব উদাহরণ শুধু কম্পাইল করে দেখায়।

///

## Compiled ও SQLCompiler { #compiled-group }

## `Compiled` { #compiled }

```python
from sqlalchemy.sql.compiler import Compiled
```

একটি কম্পাইল করা SQL বা DDL স্টেটমেন্ট: SQL স্ট্রিং (`string`), প্যারামিটারের নাম ও মান (`params`), আর কোন ডায়ালেক্টের জন্য। `stmt.compile(dialect=...)` এটি দেয়; `str(stmt)` আসলে `str(stmt.compile())`। SQL স্টেটমেন্টের জন্য আসল ক্লাস `SQLCompiler`, DDL-এর জন্য `DDLCompiler`।

**ডিবাগ টিপ:** প্যারামিটারের মান বসিয়ে দেখতে `stmt.compile(dialect=..., compile_kwargs={"literal_binds": True})`। (শুধু দেখার জন্য; চালানোর জন্য নয়, কারণ SQL injection-এর ঝুঁকি।)

**উদাহরণ:**

```python
print(type(c).__name__, isinstance(c, Compiled))   # PGCompiler_psycopg True
print(c.string)
# SELECT users.id, users.name
# FROM users
# WHERE users.id = %(uid)s::INTEGER
print(select(users.c.name).where(users.c.id == 5).compile(dialect=pg, compile_kwargs={"literal_binds": True}))
# SELECT users.name
# FROM users
# WHERE users.id = 5
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #compiled-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache_key`](#compiled-cache-key) | অ্যাট্রিবিউট (internal) | যে [`CacheKey`](#cachekey) দিয়ে এই কম্পাইল-ফল ক্যাশে রাখা হয়েছে; সরাসরি `compile()` করলে `None`। |
| [`can_execute`](#compiled-can-execute) | অ্যাট্রিবিউট | এটি চালানো যায় এমন স্টেটমেন্ট কি না (SELECT/INSERT/DDL হলে `True`; একটি কলাম-এক্সপ্রেশন কম্পাইল করলে `False`)। |
| [`compile_state`](#compiled-compile-state) | অ্যাট্রিবিউট (internal) | কম্পাইলের সময় তৈরি স্টেটমেন্ট-বিশেষ অবস্থা (FROM-এর তালিকা ইত্যাদি)। |
| [`construct_params()`](#compiled-construct-params) | মেথড | প্যারামিটারের **নাম → মান** dict বানায়; চাইলে নতুন মান দিয়ে (`construct_params({"uid": 7})`)। |
| [`dialect`](#compiled-dialect) | অ্যাট্রিবিউট | যে ডায়ালেক্টের জন্য কম্পাইল হয়েছে। |
| [`dml_compile_state`](#compiled-dml-compile-state) | অ্যাট্রিবিউট (internal) | INSERT/UPDATE/DELETE-এর বাইরের স্টেটমেন্টের compile state (নইলে `None`)। |
| [`execution_options`](#compiled-execution-options) | অ্যাট্রিবিউট | স্টেটমেন্টের execution options (কম্পাইলের সময় যা ছিল)। |
| [`is_ddl`](#compiled-is-ddl) | অ্যাট্রিবিউট | DDL (CREATE/DROP …) কম্পাইল কি না। |
| [`is_sql`](#compiled-is-sql) | অ্যাট্রিবিউট | সাধারণ SQL স্টেটমেন্ট কম্পাইল কি না। |
| [`params`](#compiled-params) | প্রপার্টি | প্যারামিটারের নাম → মান dict (স্টেটমেন্টে দেওয়া মান; না দেওয়া থাকলে `None`)। |
| [`process()`](#compiled-process) | মেথড | এই কম্পাইলার দিয়ে একটি এক্সপ্রেশনের SQL অংশ বানায় (ভেতরে সংশ্লিষ্ট `visit_*` ডাকে)। |
| [`schema_translate_map`](#compiled-schema-translate-map) | অ্যাট্রিবিউট | `execution_options(schema_translate_map={...})` থাকলে স্কিমার নাম বদলের ম্যাপ, নইলে `None`। |
| [`sql_compiler`](#compiled-sql-compiler) | প্রপার্টি | SQL এক্সপ্রেশন কম্পাইল করতে পারে এমন কম্পাইলার: `SQLCompiler`-এ নিজেই, `DDLCompiler`-এ ভেতরের একটি `SQLCompiler` (DDL-এর ভেতরের CHECK শর্ত ইত্যাদির জন্য)। |
| [`state`](#compiled-state) | অ্যাট্রিবিউট (internal) | কম্পাইলারের অবস্থা ([`CompilerState`](#compilerstate)): কাজ শেষে `STRING_APPLIED`। |
| [`statement`](#compiled-statement) | অ্যাট্রিবিউট | যে মূল স্টেটমেন্ট (এক্সপ্রেশন অবজেক্ট) কম্পাইল করা হয়েছে। |
| [`string`](#compiled-string) | অ্যাট্রিবিউট | তৈরি SQL স্ট্রিং (`str(compiled)`-এর মতো)। |
| [`visit_unsupported_compilation()`](#compiled-visit-unsupported-compilation) | মেথড (internal) | কোনো কনস্ট্রাক্টের জন্য `visit_*` না পেলে এটি ডাকা হয় আর `UnsupportedCompilationError` দেয়। |

### `Compiled.cache_key` { #compiled-cache-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে [`CacheKey`](#cachekey) দিয়ে এই কম্পাইল-ফল ক্যাশে রাখা হয়েছে; সরাসরি `compile()` করলে `None`।

**উদাহরণ:**

```python
print(c.cache_key)   # None
```

### `Compiled.can_execute` { #compiled-can-execute }

**ধরন:** অ্যাট্রিবিউট

এটি চালানো যায় এমন স্টেটমেন্ট কি না (SELECT/INSERT/DDL হলে `True`; একটি কলাম-এক্সপ্রেশন কম্পাইল করলে `False`)।

**উদাহরণ:**

```python
print(c.can_execute, (users.c.id == 1).compile().can_execute)   # True False
```

### `Compiled.compile_state` { #compiled-compile-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় তৈরি স্টেটমেন্ট-বিশেষ অবস্থা (FROM-এর তালিকা ইত্যাদি)।

**উদাহরণ:**

```python
print(type(c.compile_state).__name__)   # SelectState
```

### `Compiled.construct_params()` { #compiled-construct-params }

```python
Compiled.construct_params(params=None, extracted_parameters=None, escape_names=True)
```

**ধরন:** মেথড

প্যারামিটারের **নাম → মান** dict বানায়; চাইলে নতুন মান দিয়ে (`construct_params({"uid": 7})`)। `params` প্রপার্টি এটাই ডাকে।

**উদাহরণ:**

```python
print(c.construct_params({"uid": 7}))   # {'uid': 7}
```

### `Compiled.dialect` { #compiled-dialect }

**ধরন:** অ্যাট্রিবিউট

যে ডায়ালেক্টের জন্য কম্পাইল হয়েছে।

**উদাহরণ:**

```python
print(c.dialect.name, c.dialect.driver)   # postgresql psycopg
```

### `Compiled.dml_compile_state` { #compiled-dml-compile-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT/UPDATE/DELETE-এর বাইরের স্টেটমেন্টের compile state (নইলে `None`)।

**উদাহরণ:**

```python
print(type(insert(users).values(name="x").compile(dialect=pg).dml_compile_state).__name__)   # InsertDMLState
```

### `Compiled.execution_options` { #compiled-execution-options }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের execution options (কম্পাইলের সময় যা ছিল)।

**উদাহরণ:**

```python
print(dict(select(users).execution_options(stream_results=True).compile().execution_options))   # {'stream_results': True}
```

### `Compiled.is_ddl` { #compiled-is-ddl }

**ধরন:** অ্যাট্রিবিউট

DDL (CREATE/DROP …) কম্পাইল কি না।

**উদাহরণ:**

```python
print(c.is_ddl, schema.CreateTable(users).compile(dialect=pg).is_ddl)   # False True
```

### `Compiled.is_sql` { #compiled-is-sql }

**ধরন:** অ্যাট্রিবিউট

সাধারণ SQL স্টেটমেন্ট কম্পাইল কি না।

**উদাহরণ:**

```python
print(c.is_sql, schema.CreateTable(users).compile(dialect=pg).is_sql)   # True False
```

### `Compiled.params` { #compiled-params }

**ধরন:** প্রপার্টি

প্যারামিটারের নাম → মান dict (স্টেটমেন্টে দেওয়া মান; না দেওয়া থাকলে `None`)।

**উদাহরণ:**

```python
print(select(users).where(users.c.name == "রহিম").compile(dialect=pg).params)   # {'name_1': 'রহিম'}
```

### `Compiled.process()` { #compiled-process }

```python
Compiled.process(obj, **kwargs)
```

**ধরন:** মেথড

এই কম্পাইলার দিয়ে একটি এক্সপ্রেশনের SQL অংশ বানায় (ভেতরে সংশ্লিষ্ট `visit_*` ডাকে)। নিজের `@compiles` ফাংশনের ভেতরে অংশগুলো কম্পাইল করতে এটাই ব্যবহার হয়: `compiler.process(element.clause, **kw)`।

**উদাহরণ:**

```python
print(c.process(users.c.id + 1))   # users.id + %(id_1)s::INTEGER
```

### `Compiled.schema_translate_map` { #compiled-schema-translate-map }

**ধরন:** অ্যাট্রিবিউট

`execution_options(schema_translate_map={...})` থাকলে স্কিমার নাম বদলের ম্যাপ, নইলে `None`।

**উদাহরণ:**

```python
print(c.schema_translate_map)   # None
```

### `Compiled.sql_compiler` { #compiled-sql-compiler }

**ধরন:** প্রপার্টি

SQL এক্সপ্রেশন কম্পাইল করতে পারে এমন কম্পাইলার: `SQLCompiler`-এ নিজেই, `DDLCompiler`-এ ভেতরের একটি `SQLCompiler` (DDL-এর ভেতরের CHECK শর্ত ইত্যাদির জন্য)।

**উদাহরণ:**

```python
d = schema.CreateTable(users).compile(dialect=pg)
print(c.sql_compiler is c, type(d.sql_compiler).__name__)   # True PGCompiler_psycopg
```

### `Compiled.state` { #compiled-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলারের অবস্থা ([`CompilerState`](#compilerstate)): কাজ শেষে `STRING_APPLIED`।

**উদাহরণ:**

```python
print(c.state.name)   # STRING_APPLIED
```

### `Compiled.statement` { #compiled-statement }

**ধরন:** অ্যাট্রিবিউট

যে মূল স্টেটমেন্ট (এক্সপ্রেশন অবজেক্ট) কম্পাইল করা হয়েছে।

**উদাহরণ:**

```python
print(type(c.statement).__name__)   # Select
```

### `Compiled.string` { #compiled-string }

**ধরন:** অ্যাট্রিবিউট

তৈরি SQL স্ট্রিং (`str(compiled)`-এর মতো)।

**উদাহরণ:**

```python
print(update(users).values(name="x").compile(dialect=pg).string)   # UPDATE users SET name=%(name)s::VARCHAR
```

### `Compiled.visit_unsupported_compilation()` { #compiled-visit-unsupported-compilation }

```python
Compiled.visit_unsupported_compilation(element, err, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোনো কনস্ট্রাক্টের জন্য `visit_*` না পেলে এটি ডাকা হয় আর `UnsupportedCompilationError` দেয়।

**উদাহরণ:**

```python
try:
    select(postgresql.array([1])).compile(dialect=sqlite.dialect())
except exc.UnsupportedCompilationError as e:
    print(type(e).__name__)   # UnsupportedCompilationError
```

## `SQLCompiler` { #sqlcompiler }

```python
from sqlalchemy.sql.compiler import SQLCompiler
```

SELECT/INSERT/UPDATE/DELETE কম্পাইলের ডিফল্ট বাস্তবায়ন। প্রতিটি ডায়ালেক্টের নিজের subclass আছে (`PGCompiler`, `SQLiteCompiler`, `MySQLCompiler` …), যা কিছু `visit_*` আর `*_clause` মেথড বদলায়: যেমন MySQL-এ `LIMIT` লেখার ধরন, PostgreSQL-এ `::INTEGER` cast।

বেশিরভাগ সদস্য ডায়ালেক্ট লেখকদের জন্য hook (`limit_clause()`, `for_update_clause()` …)। ব্যবহারকারীর কাজের অংশ: `string`, `params`, `positiontup`, `binds`, `effective_returning`, আর `@compiles`-এর ভেতরে `process()`।

**উদাহরণ:**

```python
print(type(c).__mro__[1].__name__, issubclass(type(c), SQLCompiler))   # PGCompiler True
print(select(users.c.id).limit(5).compile(dialect=mysql.dialect()).string.splitlines()[-1].strip())   # LIMIT %s
print(select(users.c.id).limit(5).compile(dialect=pg).string.splitlines()[-1].strip())   # LIMIT %(param_1)s::INTEGER
```

### কনস্ট্রাক্টরের প্যারামিটার { #sqlcompiler-params }

```python
SQLCompiler(dialect, statement, cache_key=None, column_keys=None, for_executemany=False, linting=<Linting.NO_LINTING: 0>, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `dialect` | যে ডায়ালেক্টের জন্য। |
| `statement` | কম্পাইল করার স্টেটমেন্ট। |
| `cache_key` | ক্যাশের key (ভেতরের ব্যবহার)। |
| `column_keys` | INSERT/UPDATE-এ কোন কলামের মান দেওয়া হবে (execute-এর প্যারামিটার থেকে)। |
| `for_executemany` | executemany-এর জন্য কম্পাইল কি না। |
| `linting` | [`Linting`](#linting) পতাকা। |
| `kwargs` | `compile_kwargs` (যেমন `literal_binds=True`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sqlcompiler-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`anon_map`](#sqlcompiler-anon-map) | অ্যাট্রিবিউট (internal) | নামহীন (anonymous) label/alias-এর জন্য তৈরি নামের হিসাব। |
| [`ansi_bind_rules`](#sqlcompiler-ansi-bind-rules) | অ্যাট্রিবিউট (internal) | `True` হলে কিছু জায়গায় (যেমন দুই bind প্যারামিটারের তুলনা) bind না বসিয়ে literal বসায়; কিছু ডেটাবেসের নিয়মের জন্য। |
| [`bind_names`](#sqlcompiler-bind-names) | অ্যাট্রিবিউট | `BindParameter` অবজেক্ট → SQL-এ তার নাম। |
| [`bindname_escape_characters`](#sqlcompiler-bindname-escape-characters) | অ্যাট্রিবিউট (internal) | প্যারামিটারের নামে যে অক্ষরগুলো বদলে নিরাপদ করতে হয় (যেমন `%`, `(`, `.`)। |
| [`bindparam_string()`](#sqlcompiler-bindparam-string) | মেথড (internal) | একটি প্যারামিটারের placeholder বানায় (ডায়ালেক্টের paramstyle অনুযায়ী: `%(name)s`, `?`, `:name`)। |
| [`binds`](#sqlcompiler-binds) | অ্যাট্রিবিউট | SQL-এ প্যারামিটারের নাম → `BindParameter` অবজেক্ট। |
| [`bindtemplate`](#sqlcompiler-bindtemplate) | অ্যাট্রিবিউট (internal) | placeholder-এর টেমপ্লেট (paramstyle অনুযায়ী)। |
| [`column_keys`](#sqlcompiler-column-keys) | অ্যাট্রিবিউট | INSERT/UPDATE কম্পাইলে কোন কলামের মান আসবে (execute-এর প্যারামিটারের key), নইলে `None`। |
| [`compilation_bindtemplate`](#sqlcompiler-compilation-bindtemplate) | অ্যাট্রিবিউট (internal) | কম্পাইলের সময় ব্যবহৃত placeholder টেমপ্লেট (positional হলে পরে আসল রূপে বদলায়)। |
| [`compound_keywords`](#sqlcompiler-compound-keywords) | অ্যাট্রিবিউট (internal) | UNION/INTERSECT/EXCEPT ধরন → SQL কীওয়ার্ড। |
| [`construct_expanded_state()`](#sqlcompiler-construct-expanded-state) | মেথড | "expanding" প্যারামিটার (যেমন `in_([1, 2, 3])`) খুলে চূড়ান্ত SQL আর প্যারামিটারসহ একটি [`ExpandedState`](#expandedstate) বানায়: ডেটাবেসে যা আসলে যায় ঠিক সেটি দেখতে। |
| [`ctes`](#sqlcompiler-ctes) | অ্যাট্রিবিউট (internal) | কম্পাইলের সময় পাওয়া CTE-গুলো (না থাকলে `None`)। |
| [`current_executable`](#sqlcompiler-current-executable) | প্রপার্টি (internal) | এখন কম্পাইল হচ্ছে এমন সবচেয়ে ভেতরের স্টেটমেন্ট (সাবকুয়েরির ভেতরে থাকলে সেটি)। |
| [`default_from()`](#sqlcompiler-default-from) | মেথড (internal) | FROM ছাড়া SELECT-এ (যেমন `SELECT 1`) কী বসবে; Oracle-এ ` FROM DUAL`, বেশিরভাগে খালি। |
| [`delete_extra_from_clause()`](#sqlcompiler-delete-extra-from-clause) | মেথড (internal) | `DELETE ... USING/FROM` (একাধিক টেবিলের DELETE) লেখার hook; ডায়ালেক্টভেদে আলাদা। |
| [`delete_post_criteria_clause()`](#sqlcompiler-delete-post-criteria-clause) | মেথড (internal) | DELETE-এর WHERE-এর পরে কিছু যোগের hook (যেমন MySQL `LIMIT`)। |
| [`delete_table_clause()`](#sqlcompiler-delete-table-clause) | মেথড (internal) | `DELETE FROM <টেবিল>` অংশের টেবিল-নাম লেখার hook। |
| [`effective_returning`](#sqlcompiler-effective-returning) | প্রপার্টি | INSERT/UPDATE/DELETE-এ আসলে যে কলামগুলো `RETURNING`-এ যাবে (স্পষ্ট `returning()` + দরকারি primary key ইত্যাদি)। |
| [`escape_literal_column()`](#sqlcompiler-escape-literal-column) | মেথড (internal) | `literal_column()`-এর টেক্সটে `%` ইত্যাদি এস্কেপ করে (paramstyle-এর জন্য)। |
| [`escaped_bind_names`](#sqlcompiler-escaped-bind-names) | অ্যাট্রিবিউট (internal) | যে প্যারামিটারের নাম এস্কেপ হয়েছে: আসল নাম → এস্কেপড নাম। |
| [`extract_map`](#sqlcompiler-extract-map) | অ্যাট্রিবিউট (internal) | `extract("field", ...)`-এর ফিল্ডের নাম → SQL-এ লেখার নাম। |
| [`fetch_clause()`](#sqlcompiler-fetch-clause) | মেথড (internal) | `FETCH FIRST n ROWS ONLY` লেখার hook (`select().fetch(n)`)। |
| [`for_executemany`](#sqlcompiler-for-executemany) | অ্যাট্রিবিউট (internal) | executemany-এর জন্য কম্পাইল কি না। |
| [`for_update_clause()`](#sqlcompiler-for-update-clause) | মেথড (internal) | `FOR UPDATE ...` লেখার hook। |
| [`format_from_hint_text()`](#sqlcompiler-format-from-hint-text) | মেথড (internal) | FROM-এর টেবিলের সাথে hint যোগের hook (`with_hint()`)। |
| [`function_argspec()`](#sqlcompiler-function-argspec) | মেথড (internal) | SQL ফাংশনের আর্গুমেন্ট অংশ (`count(x)`-এর `x`) লেখে। |
| [`get_crud_hint_text()`](#sqlcompiler-get-crud-hint-text) | মেথড (internal) | INSERT/UPDATE/DELETE-এর টেবিল-hint-এর hook। |
| [`get_cte_preamble()`](#sqlcompiler-get-cte-preamble) | মেথড (internal) | `WITH` বা `WITH RECURSIVE` শব্দ দেয়। |
| [`get_from_hint_text()`](#sqlcompiler-get-from-hint-text) | মেথড (internal) | FROM-hint টেক্সট (ডায়ালেক্টভেদে)। |
| [`get_render_as_alias_suffix()`](#sqlcompiler-get-render-as-alias-suffix) | মেথড (internal) | alias লেখার ধরন: ` AS নাম` (Oracle-এ `AS` ছাড়া)। |
| [`get_select_hint_text()`](#sqlcompiler-get-select-hint-text) | মেথড (internal) | SELECT-এর hint অংশ। |
| [`get_select_precolumns()`](#sqlcompiler-get-select-precolumns) | মেথড (internal) | `SELECT`-এর পরে কলামের আগে যা বসে: `DISTINCT `, `DISTINCT ON (...) ` ইত্যাদি। |
| [`get_statement_hint_text()`](#sqlcompiler-get-statement-hint-text) | মেথড (internal) | পুরো স্টেটমেন্টের hint (`with_statement_hint()`)। |
| [`group_by_clause()`](#sqlcompiler-group-by-clause) | মেথড (internal) | `GROUP BY` অংশ লেখার hook। |
| [`has_out_parameters`](#sqlcompiler-has-out-parameters) | অ্যাট্রিবিউট (internal) | স্টেটমেন্টে OUT প্যারামিটার (stored procedure) আছে কি না। |
| [`implicit_returning`](#sqlcompiler-implicit-returning) | অ্যাট্রিবিউট (internal) | INSERT-এ নতুন primary key পেতে নিজে থেকে যোগ হওয়া RETURNING কলাম (না থাকলে `None`)। |
| [`inline`](#sqlcompiler-inline) | অ্যাট্রিবিউট (internal) | INSERT/UPDATE-এ ডিফল্ট মান আলাদা করে আগে না এনে SQL-এর ভেতরেই বসাবে কি না। |
| [`insert_prefetch`](#sqlcompiler-insert-prefetch) | অ্যাট্রিবিউট (internal) | INSERT-এর আগে Python-এ হিসাব করতে হবে এমন ডিফল্টের কলামগুলো। |
| [`insert_single_values_expr`](#sqlcompiler-insert-single-values-expr) | প্রপার্টি (legacy) | পুরোনো "insert batching"-এর জন্য একটি রো-র `VALUES (...)` অংশের স্ট্রিং। |
| [`is_subquery()`](#sqlcompiler-is-subquery) | মেথড (internal) | এখন সাবকুয়েরি কম্পাইল হচ্ছে কি না। |
| [`isdelete`](#sqlcompiler-isdelete) | অ্যাট্রিবিউট | DELETE কম্পাইল কি না। |
| [`isinsert`](#sqlcompiler-isinsert) | অ্যাট্রিবিউট | INSERT কম্পাইল কি না। |
| [`isplaintext`](#sqlcompiler-isplaintext) | অ্যাট্রিবিউট | `text()` কম্পাইল কি না। |
| [`isupdate`](#sqlcompiler-isupdate) | অ্যাট্রিবিউট | UPDATE কম্পাইল কি না। |
| [`label_length`](#sqlcompiler-label-length) | অ্যাট্রিবিউট (internal) | স্বয়ংক্রিয় label-এর সর্বোচ্চ দৈর্ঘ্য (ডায়ালেক্টের `max_identifier_length`)। |
| [`limit_clause()`](#sqlcompiler-limit-clause) | মেথড (internal) | `LIMIT ... OFFSET ...` লেখার hook (ডায়ালেক্টভেদে সবচেয়ে বেশি বদলায়)। |
| [`linting`](#sqlcompiler-linting) | অ্যাট্রিবিউট (internal) | এই কম্পাইলে কোন [`Linting`](#linting) চালু (চালানোর সময় cartesian-product সতর্কতা)। |
| [`literal_execute_params`](#sqlcompiler-literal-execute-params) | অ্যাট্রিবিউট (internal) | যে প্যারামিটার চালানোর সময় literal হিসেবে বসবে (`literal_execute=True`)। |
| [`order_by_clause()`](#sqlcompiler-order-by-clause) | মেথড (internal) | `ORDER BY` লেখার hook। |
| [`positional`](#sqlcompiler-positional) | অ্যাট্রিবিউট | ডায়ালেক্টের paramstyle positional (`?`, `%s`, `$1`) কি না। |
| [`positiontup`](#sqlcompiler-positiontup) | অ্যাট্রিবিউট | positional paramstyle-এ প্যারামিটারগুলোর **ক্রম** (নামের তালিকা); named হলে `None`। |
| [`post_compile_params`](#sqlcompiler-post-compile-params) | অ্যাট্রিবিউট (internal) | যে প্যারামিটার চালানোর সময় খোলা হবে (যেমন `in_()`-এর expanding)। |
| [`post_process_text()`](#sqlcompiler-post-process-text) | মেথড (internal) | `text()`-এর টেক্সট paramstyle অনুযায়ী ঠিক করে (যেমন `%` এস্কেপ)। |
| [`postfetch_lastrowid`](#sqlcompiler-postfetch-lastrowid) | অ্যাট্রিবিউট (internal) | INSERT-এর পর `cursor.lastrowid` থেকে primary key আনবে কি না (RETURNING ব্যবহার না হলে, যেমন SQLite/MySQL-এ)। |
| [`prefetch`](#sqlcompiler-prefetch) | প্রপার্টি (internal) | `insert_prefetch` + `update_prefetch` একসাথে। |
| [`preparer`](#sqlcompiler-preparer) | অ্যাট্রিবিউট | নাম quote করার [`IdentifierPreparer`](#identifierpreparer)। |
| [`render_bind_cast()`](#sqlcompiler-render-bind-cast) | মেথড (internal) | placeholder-এর সাথে cast লেখে (PostgreSQL psycopg-এ `%(x)s::INTEGER`)। |
| [`render_literal_bindparam()`](#sqlcompiler-render-literal-bindparam) | মেথড (internal) | একটি bind প্যারামিটার literal হিসেবে লেখে (`literal_binds=True` হলে)। |
| [`render_literal_value()`](#sqlcompiler-render-literal-value) | মেথড | একটি Python মানকে টাইপ অনুযায়ী SQL literal বানায় (স্ট্রিং হলে quote ও এস্কেপসহ)। |
| [`render_table_with_column_in_update_from`](#sqlcompiler-render-table-with-column-in-update-from) | অ্যাট্রিবিউট (internal) | `UPDATE ... FROM`-এ কলামের আগে টেবিলের নাম লিখবে কি না (MySQL-এর জন্য)। |
| [`returning`](#sqlcompiler-returning) | প্রপার্টি (legacy) | `effective_returning`-এর পুরোনো নাম। |
| [`returning_clause()`](#sqlcompiler-returning-clause) | মেথড (internal) | `RETURNING ...` অংশ লেখার hook। |
| [`returning_precedes_values`](#sqlcompiler-returning-precedes-values) | অ্যাট্রিবিউট (internal) | `RETURNING`/`OUTPUT` VALUES-এর আগে বসবে কি না (SQL Server-এর `OUTPUT`)। |
| [`stack`](#sqlcompiler-stack) | অ্যাট্রিবিউট (internal) | কম্পাইলের সময় ভেতরের স্টেটমেন্টের স্তূপ (সাবকুয়েরি ইত্যাদি)। |
| [`translate_select_structure`](#sqlcompiler-translate-select-structure) | অ্যাট্রিবিউট (internal) | SELECT-এর গঠন বদলানোর hook (পুরোনো Oracle/SQL Server-এ LIMIT অনুকরণে)। |
| [`truncated_names`](#sqlcompiler-truncated-names) | অ্যাট্রিবিউট (internal) | `max_identifier_length`-এর চেয়ে লম্বা স্বয়ংক্রিয় নাম ছোট করার হিসাব। |
| [`update_from_clause()`](#sqlcompiler-update-from-clause) | মেথড (internal) | `UPDATE ... FROM` (একাধিক টেবিলের UPDATE) লেখার hook। |
| [`update_post_criteria_clause()`](#sqlcompiler-update-post-criteria-clause) | মেথড (internal) | UPDATE-এর WHERE-এর পরে কিছু যোগের hook (যেমন MySQL `LIMIT`)। |
| [`update_prefetch`](#sqlcompiler-update-prefetch) | অ্যাট্রিবিউট (internal) | UPDATE-এর আগে Python-এ হিসাব করতে হবে এমন `onupdate` ডিফল্টের কলাম। |
| [`update_tables_clause()`](#sqlcompiler-update-tables-clause) | মেথড (internal) | `UPDATE <টেবিল>` অংশের hook। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SQLCompiler`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Compiled` থেকে:** [`cache_key`](#compiled-cache-key) · [`compile_state`](#compiled-compile-state) · [`construct_params()`](#compiled-construct-params) · [`dml_compile_state`](#compiled-dml-compile-state) · [`execution_options`](#compiled-execution-options) · [`is_ddl`](#compiled-is-ddl) · [`is_sql`](#compiled-is-sql) · [`params`](#compiled-params) · [`process()`](#compiled-process) · [`schema_translate_map`](#compiled-schema-translate-map) · [`sql_compiler`](#compiled-sql-compiler) · [`statement`](#compiled-statement) · [`string`](#compiled-string) · [`visit_unsupported_compilation()`](#compiled-visit-unsupported-compilation)

///

/// details | visit_* মেথড: প্রতিটি SQL কনস্ট্রাক্টের জন্য একটি (৯৭টি, দেখতে ক্লিক করুন)
    type: info

প্রতিটি এক্সপ্রেশন-ক্লাসের একটি `__visit_name__` আছে (`Select` → `"select"`, `BinaryExpression` → `"binary"`, `Label` → `"label"` …)। কম্পাইলার সেই নাম ধরে `visit_<নাম>(element, **kw)` ডাকে, আর মেথডটি ঐ অংশের SQL স্ট্রিং ফেরত দেয়। ডায়ালেক্ট এগুলো override করে নিজের SQL লেখে। নিজের কোডে এগুলো সরাসরি ডাকবেন না; `compiler.process(element)` ডাকুন, সেটাই ঠিক `visit_*` বেছে নেয়। নিজের কনস্ট্রাক্টের জন্য নতুন visit লিখতে [`@compiles`](ext-misc.md#compiles) ব্যবহার করুন।

`visit_<অপারেটর>_binary` (যেমন `visit_like_op_binary`) আর `visit_<অপারেটর>_unary_operator` ধরনের মেথডগুলো নির্দিষ্ট অপারেটরের জন্য: `like()`, `ilike()`, `regexp_match()`, `is_distinct_from()` ইত্যাদি।

**উদাহরণ:**

```python
print(users.c.name.__visit_name__, select(users).__visit_name__)   # column select
print(c.visit_column(users.c.name))   # users.name
print(c.process(users.c.name.ilike("র%")))   # users.name ILIKE %(name_1)s::VARCHAR
```

`visit_aggregate_orderby_inline()` · `visit_aggregate_strings_func()` · `visit_aggregateorderby()` · `visit_alias()` · `visit_between_op_binary()` · `visit_binary()` · `visit_bindparam()` · `visit_case()` · `visit_cast()` · `visit_clauselist()` · `visit_collation()` · `visit_column()` · `visit_compound_select()` · `visit_contains_op_binary()` · `visit_cte()` · `visit_custom_op_binary()` · `visit_custom_op_unary_modifier()` · `visit_custom_op_unary_operator()` · `visit_delete()` · `visit_dmltargetcopy()` · `visit_element_list()` · `visit_empty_set_expr()` · `visit_empty_set_op_expr()` · `visit_endswith_op_binary()` · `visit_expression_clauselist()` · `visit_extract()` · `visit_false()` · `visit_floordiv_binary()` · `visit_frame_clause()` · `visit_fromclause()` · `visit_funcfilter()` · `visit_function()` · `visit_function_as_comparison_op_binary()` · `visit_grouping()` · `visit_icontains_op_binary()` · `visit_iendswith_op_binary()` · `visit_ilike_case_insensitive_operand()` · `visit_ilike_op_binary()` · `visit_index()` · `visit_insert()` · `visit_is_false_unary_operator()` · `visit_is_true_unary_operator()` · `visit_istartswith_op_binary()` · `visit_join()` · `visit_label()` · `visit_label_reference()` · `visit_lambda_element()` · `visit_lateral()` · `visit_like_op_binary()` · `visit_mod_binary()` · `visit_next_value_func()` · `visit_not_between_op_binary()` · `visit_not_contains_op_binary()` · `visit_not_endswith_op_binary()` · `visit_not_icontains_op_binary()` · `visit_not_iendswith_op_binary()` · `visit_not_ilike_op_binary()` · `visit_not_in_op_binary()` · `visit_not_istartswith_op_binary()` · `visit_not_like_op_binary()` · `visit_not_match_op_binary()` · `visit_not_regexp_match_op_binary()` · `visit_not_startswith_op_binary()` · `visit_null()` · `visit_order_by_list()` · `visit_over()` · `visit_override_binds()` · `visit_regexp_match_op_binary()` · `visit_regexp_replace_op_binary()` · `visit_release_savepoint()` · `visit_rollback_to_savepoint()` · `visit_savepoint()` · `visit_scalar_function_column()` · `visit_scalar_values()` · `visit_select()` · `visit_select_statement_grouping()` · `visit_sequence()` · `visit_startswith_op_binary()` · `visit_subquery()` · `visit_table()` · `visit_table_valued_alias()` · `visit_table_valued_column()` · `visit_tablesample()` · `visit_textclause()` · `visit_textual_label_reference()` · `visit_textual_select()` · `visit_true()` · `visit_truediv_binary()` · `visit_tstring()` · `visit_tstring_text()` · `visit_tuple()` · `visit_type_coerce()` · `visit_typeclause()` · `visit_unary()` · `visit_update()` · `visit_values()` · `visit_withingroup()`

///

### `SQLCompiler.anon_map` { #sqlcompiler-anon-map }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নামহীন (anonymous) label/alias-এর জন্য তৈরি নামের হিসাব।

**উদাহরণ:**

```python
print(type(c.anon_map).__name__)   # prefix_anon_map
```

### `SQLCompiler.ansi_bind_rules` { #sqlcompiler-ansi-bind-rules }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`True` হলে কিছু জায়গায় (যেমন দুই bind প্যারামিটারের তুলনা) bind না বসিয়ে literal বসায়; কিছু ডেটাবেসের নিয়মের জন্য।

**উদাহরণ:**

```python
print(c.ansi_bind_rules)   # False
```

### `SQLCompiler.bind_names` { #sqlcompiler-bind-names }

**ধরন:** অ্যাট্রিবিউট

`BindParameter` অবজেক্ট → SQL-এ তার নাম।

**উদাহরণ:**

```python
print(list(c.bind_names.values()))   # ['uid']
```

### `SQLCompiler.bindname_escape_characters` { #sqlcompiler-bindname-escape-characters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

প্যারামিটারের নামে যে অক্ষরগুলো বদলে নিরাপদ করতে হয় (যেমন `%`, `(`, `.`)।

**উদাহরণ:**

```python
print("%" in SQLCompiler.bindname_escape_characters)   # True
```

### `SQLCompiler.bindparam_string()` { #sqlcompiler-bindparam-string }

```python
SQLCompiler.bindparam_string(name, post_compile=False, expanding=False, escaped_from=None, bindparam_type=None, accumulate_bind_names=None, visited_bindparam=None, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি প্যারামিটারের placeholder বানায় (ডায়ালেক্টের paramstyle অনুযায়ী: `%(name)s`, `?`, `:name`)।

**উদাহরণ:**

```python
print(c.bindparam_string("x"), sqlite.dialect().statement_compiler(sqlite.dialect(), None).bindparam_string("x"))   # %(x)s ?
```

### `SQLCompiler.binds` { #sqlcompiler-binds }

**ধরন:** অ্যাট্রিবিউট

SQL-এ প্যারামিটারের নাম → `BindParameter` অবজেক্ট।

**উদাহরণ:**

```python
print(list(c.binds))   # ['uid']
```

### `SQLCompiler.bindtemplate` { #sqlcompiler-bindtemplate }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

placeholder-এর টেমপ্লেট (paramstyle অনুযায়ী)।

**উদাহরণ:**

```python
print(c.bindtemplate)   # %%(%(name)s)s
```

### `SQLCompiler.column_keys` { #sqlcompiler-column-keys }

**ধরন:** অ্যাট্রিবিউট

INSERT/UPDATE কম্পাইলে কোন কলামের মান আসবে (execute-এর প্যারামিটারের key), নইলে `None`।

**উদাহরণ:**

```python
print(insert(users).compile(column_keys=["name"]).string)   # INSERT INTO users (name) VALUES (:name)
```

### `SQLCompiler.compilation_bindtemplate` { #sqlcompiler-compilation-bindtemplate }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় ব্যবহৃত placeholder টেমপ্লেট (positional হলে পরে আসল রূপে বদলায়)।

**উদাহরণ:**

```python
print(c.compilation_bindtemplate)   # %%(%(name)s)s
```

### `SQLCompiler.compound_keywords` { #sqlcompiler-compound-keywords }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

UNION/INTERSECT/EXCEPT ধরন → SQL কীওয়ার্ড।

**উদাহরণ:**

```python
print(sorted(v for v in SQLCompiler.compound_keywords.values()))   # ['EXCEPT', 'EXCEPT ALL', 'INTERSECT', 'INTERSECT ALL', 'UNION', 'UNION ALL']
```

### `SQLCompiler.construct_expanded_state()` { #sqlcompiler-construct-expanded-state }

```python
SQLCompiler.construct_expanded_state(params=None, escape_names=True)
```

**ধরন:** মেথড

"expanding" প্যারামিটার (যেমন `in_([1, 2, 3])`) খুলে চূড়ান্ত SQL আর প্যারামিটারসহ একটি [`ExpandedState`](#expandedstate) বানায়: ডেটাবেসে যা আসলে যায় ঠিক সেটি দেখতে।

**উদাহরণ:**

```python
ci = select(users.c.id).where(users.c.id.in_([1, 2, 3])).compile(dialect=pg)
st = ci.construct_expanded_state()
print(st.statement.splitlines()[-1], st.parameters)
# WHERE users.id IN (%(id_1_1)s::INTEGER, %(id_1_2)s::INTEGER, %(id_1_3)s::INTEGER) {'id_1_1': 1, 'id_1_2': 2, 'id_1_3': 3}
```

### `SQLCompiler.ctes` { #sqlcompiler-ctes }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় পাওয়া CTE-গুলো (না থাকলে `None`)।

**উদাহরণ:**

```python
print(c.ctes)   # None
```

### `SQLCompiler.current_executable` { #sqlcompiler-current-executable }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এখন কম্পাইল হচ্ছে এমন সবচেয়ে ভেতরের স্টেটমেন্ট (সাবকুয়েরির ভেতরে থাকলে সেটি)।

**উদাহরণ:**

```python
print(callable(getattr(SQLCompiler, "current_executable").fget))   # True
```

### `SQLCompiler.default_from()` { #sqlcompiler-default-from }

```python
SQLCompiler.default_from()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM ছাড়া SELECT-এ (যেমন `SELECT 1`) কী বসবে; Oracle-এ ` FROM DUAL`, বেশিরভাগে খালি।

**উদাহরণ:**

```python
print(repr(c.default_from()))   # ''
```

### `SQLCompiler.delete_extra_from_clause()` { #sqlcompiler-delete-extra-from-clause }

```python
SQLCompiler.delete_extra_from_clause(delete_stmt, from_table, extra_froms, from_hints, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`DELETE ... USING/FROM` (একাধিক টেবিলের DELETE) লেখার hook; ডায়ালেক্টভেদে আলাদা।

**উদাহরণ:**

```python
print(delete(users).where(users.c.id == addresses.c.user_id).compile(dialect=pg).string)
# DELETE FROM users USING addresses WHERE users.id = addresses.user_id
```

### `SQLCompiler.delete_post_criteria_clause()` { #sqlcompiler-delete-post-criteria-clause }

```python
SQLCompiler.delete_post_criteria_clause(delete_stmt, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DELETE-এর WHERE-এর পরে কিছু যোগের hook (যেমন MySQL `LIMIT`)।

**উদাহরণ:**

```python
print(c.delete_post_criteria_clause(delete(users)))   # None
```

### `SQLCompiler.delete_table_clause()` { #sqlcompiler-delete-table-clause }

```python
SQLCompiler.delete_table_clause(delete_stmt, from_table, extra_froms, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`DELETE FROM <টেবিল>` অংশের টেবিল-নাম লেখার hook।

**উদাহরণ:**

```python
print(callable(c.delete_table_clause))   # True
```

### `SQLCompiler.effective_returning` { #sqlcompiler-effective-returning }

**ধরন:** প্রপার্টি

INSERT/UPDATE/DELETE-এ আসলে যে কলামগুলো `RETURNING`-এ যাবে (স্পষ্ট `returning()` + দরকারি primary key ইত্যাদি)।

**উদাহরণ:**

```python
ci = insert(users).values(name="x").returning(users.c.id).compile(dialect=pg)
print([col.name for col in ci.effective_returning])   # ['id']
```

### `SQLCompiler.escape_literal_column()` { #sqlcompiler-escape-literal-column }

```python
SQLCompiler.escape_literal_column(text)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`literal_column()`-এর টেক্সটে `%` ইত্যাদি এস্কেপ করে (paramstyle-এর জন্য)।

**উদাহরণ:**

```python
print(c.escape_literal_column("100%"))   # 100%%
```

### `SQLCompiler.escaped_bind_names` { #sqlcompiler-escaped-bind-names }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে প্যারামিটারের নাম এস্কেপ হয়েছে: আসল নাম → এস্কেপড নাম।

**উদাহরণ:**

```python
print(dict(select(users).where(users.c.id == bindparam("a.b")).compile(dialect=pg).escaped_bind_names))   # {'a.b': 'a_b'}
```

### `SQLCompiler.extract_map` { #sqlcompiler-extract-map }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`extract("field", ...)`-এর ফিল্ডের নাম → SQL-এ লেখার নাম।

**উদাহরণ:**

```python
print(SQLCompiler.extract_map["year"])   # year
```

### `SQLCompiler.fetch_clause()` { #sqlcompiler-fetch-clause }

```python
SQLCompiler.fetch_clause(select, fetch_clause=None, require_offset=False, use_literal_execute_for_simple_int=False, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`FETCH FIRST n ROWS ONLY` লেখার hook (`select().fetch(n)`)।

**উদাহরণ:**

```python
print(select(users.c.id).fetch(3).compile(dialect=pg).string.splitlines()[-1].strip())   # FETCH FIRST (%(param_1)s::INTEGER) ROWS ONLY
```

### `SQLCompiler.for_executemany` { #sqlcompiler-for-executemany }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

executemany-এর জন্য কম্পাইল কি না।

**উদাহরণ:**

```python
print(c.for_executemany)   # False
```

### `SQLCompiler.for_update_clause()` { #sqlcompiler-for-update-clause }

```python
SQLCompiler.for_update_clause(select, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`FOR UPDATE ...` লেখার hook।

**উদাহরণ:**

```python
print(select(users.c.id).with_for_update(nowait=True).compile(dialect=pg).string.splitlines()[-1])   # FROM users FOR UPDATE NOWAIT
```

### `SQLCompiler.format_from_hint_text()` { #sqlcompiler-format-from-hint-text }

```python
SQLCompiler.format_from_hint_text(sqltext, table, hint, iscrud)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM-এর টেবিলের সাথে hint যোগের hook (`with_hint()`)।

**উদাহরণ:**

```python
print(callable(c.format_from_hint_text))   # True
```

### `SQLCompiler.function_argspec()` { #sqlcompiler-function-argspec }

```python
SQLCompiler.function_argspec(func, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQL ফাংশনের আর্গুমেন্ট অংশ (`count(x)`-এর `x`) লেখে।

**উদাহরণ:**

```python
print(c.function_argspec(func.coalesce(users.c.name, "?")))   # users.name, %(coalesce_1)s::VARCHAR
```

### `SQLCompiler.get_crud_hint_text()` { #sqlcompiler-get-crud-hint-text }

```python
SQLCompiler.get_crud_hint_text(table, text)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT/UPDATE/DELETE-এর টেবিল-hint-এর hook।

**উদাহরণ:**

```python
print(c.get_crud_hint_text(users, "x"))   # None
```

### `SQLCompiler.get_cte_preamble()` { #sqlcompiler-get-cte-preamble }

```python
SQLCompiler.get_cte_preamble(recursive)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`WITH` বা `WITH RECURSIVE` শব্দ দেয়।

**উদাহরণ:**

```python
print(c.get_cte_preamble(True))   # WITH RECURSIVE
```

### `SQLCompiler.get_from_hint_text()` { #sqlcompiler-get-from-hint-text }

```python
SQLCompiler.get_from_hint_text(table, text)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FROM-hint টেক্সট (ডায়ালেক্টভেদে)।

**উদাহরণ:**

```python
print(c.get_from_hint_text(users, "x"))   # None
```

### `SQLCompiler.get_render_as_alias_suffix()` { #sqlcompiler-get-render-as-alias-suffix }

```python
SQLCompiler.get_render_as_alias_suffix(alias_name_text)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

alias লেখার ধরন: ` AS নাম` (Oracle-এ `AS` ছাড়া)।

**উদাহরণ:**

```python
print(repr(c.get_render_as_alias_suffix("u")))   # ' AS u'
```

### `SQLCompiler.get_select_hint_text()` { #sqlcompiler-get-select-hint-text }

```python
SQLCompiler.get_select_hint_text(byfroms)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SELECT-এর hint অংশ।

**উদাহরণ:**

```python
print(c.get_select_hint_text({}))   # None
```

### `SQLCompiler.get_select_precolumns()` { #sqlcompiler-get-select-precolumns }

```python
SQLCompiler.get_select_precolumns(select, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`SELECT`-এর পরে কলামের আগে যা বসে: `DISTINCT `, `DISTINCT ON (...) ` ইত্যাদি।

**উদাহরণ:**

```python
print(repr(c.get_select_precolumns(select(users.c.id).distinct())))   # 'DISTINCT '
```

### `SQLCompiler.get_statement_hint_text()` { #sqlcompiler-get-statement-hint-text }

```python
SQLCompiler.get_statement_hint_text(hint_texts)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

পুরো স্টেটমেন্টের hint (`with_statement_hint()`)।

**উদাহরণ:**

```python
print(c.get_statement_hint_text(["/*+ x */"]))   # /*+ x */
```

### `SQLCompiler.group_by_clause()` { #sqlcompiler-group-by-clause }

```python
SQLCompiler.group_by_clause(select, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`GROUP BY` অংশ লেখার hook।

**উদাহরণ:**

```python
print(select(users.c.name).group_by(users.c.name).compile(dialect=pg).string.splitlines()[-1])   # FROM users GROUP BY users.name
```

### `SQLCompiler.has_out_parameters` { #sqlcompiler-has-out-parameters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্টে OUT প্যারামিটার (stored procedure) আছে কি না।

**উদাহরণ:**

```python
print(c.has_out_parameters)   # False
```

### `SQLCompiler.implicit_returning` { #sqlcompiler-implicit-returning }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT-এ নতুন primary key পেতে নিজে থেকে যোগ হওয়া RETURNING কলাম (না থাকলে `None`)।

**উদাহরণ:**

```python
print(c.implicit_returning)   # None
```

### `SQLCompiler.inline` { #sqlcompiler-inline }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT/UPDATE-এ ডিফল্ট মান আলাদা করে আগে না এনে SQL-এর ভেতরেই বসাবে কি না।

**উদাহরণ:**

```python
print(c.inline)   # False
```

### `SQLCompiler.insert_prefetch` { #sqlcompiler-insert-prefetch }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT-এর আগে Python-এ হিসাব করতে হবে এমন ডিফল্টের কলামগুলো।

**উদাহরণ:**

```python
print(c.insert_prefetch)   # ()
```

### `SQLCompiler.insert_single_values_expr` { #sqlcompiler-insert-single-values-expr }

**ধরন:** প্রপার্টি

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো "insert batching"-এর জন্য একটি রো-র `VALUES (...)` অংশের স্ট্রিং। ২.০ থেকে SQLAlchemy-র নিজের ডায়ালেক্ট এটি আর ব্যবহার করে না (ভেতরের `_insertmanyvalues` ব্যবস্থা নিয়েছে), তাই সাধারণ কম্পাইলে `None`।

**উদাহরণ:**

```python
print(insert(users).values(name="x").compile(dialect=pg).insert_single_values_expr)   # None
```

### `SQLCompiler.is_subquery()` { #sqlcompiler-is-subquery }

```python
SQLCompiler.is_subquery()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এখন সাবকুয়েরি কম্পাইল হচ্ছে কি না।

**উদাহরণ:**

```python
print(c.is_subquery())   # False
```

### `SQLCompiler.isdelete` { #sqlcompiler-isdelete }

**ধরন:** অ্যাট্রিবিউট

DELETE কম্পাইল কি না।

**উদাহরণ:**

```python
print(c.isdelete, delete(users).compile().isdelete)   # False True
```

### `SQLCompiler.isinsert` { #sqlcompiler-isinsert }

**ধরন:** অ্যাট্রিবিউট

INSERT কম্পাইল কি না।

**উদাহরণ:**

```python
print(insert(users).compile().isinsert)   # True
```

### `SQLCompiler.isplaintext` { #sqlcompiler-isplaintext }

**ধরন:** অ্যাট্রিবিউট

`text()` কম্পাইল কি না।

**উদাহরণ:**

```python
print(text("SELECT 1").compile().isplaintext)   # True
```

### `SQLCompiler.isupdate` { #sqlcompiler-isupdate }

**ধরন:** অ্যাট্রিবিউট

UPDATE কম্পাইল কি না।

**উদাহরণ:**

```python
print(update(users).compile().isupdate)   # True
```

### `SQLCompiler.label_length` { #sqlcompiler-label-length }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্বয়ংক্রিয় label-এর সর্বোচ্চ দৈর্ঘ্য (ডায়ালেক্টের `max_identifier_length`)।

**উদাহরণ:**

```python
print(c.label_length)   # 63
```

### `SQLCompiler.limit_clause()` { #sqlcompiler-limit-clause }

```python
SQLCompiler.limit_clause(select, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`LIMIT ... OFFSET ...` লেখার hook (ডায়ালেক্টভেদে সবচেয়ে বেশি বদলায়)।

**উদাহরণ:**

```python
print(repr(c.limit_clause(select(users).limit(2).offset(1))))   # '\n LIMIT %(param_1)s::INTEGER OFFSET %(param_2)s::INTEGER'
```

### `SQLCompiler.linting` { #sqlcompiler-linting }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই কম্পাইলে কোন [`Linting`](#linting) চালু (চালানোর সময় cartesian-product সতর্কতা)।

**উদাহরণ:**

```python
print(c.linting.name)   # NO_LINTING
```

### `SQLCompiler.literal_execute_params` { #sqlcompiler-literal-execute-params }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে প্যারামিটার চালানোর সময় literal হিসেবে বসবে (`literal_execute=True`)।

**উদাহরণ:**

```python
print(c.literal_execute_params)   # frozenset()
```

### `SQLCompiler.order_by_clause()` { #sqlcompiler-order-by-clause }

```python
SQLCompiler.order_by_clause(select, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`ORDER BY` লেখার hook।

**উদাহরণ:**

```python
print(select(users.c.id).order_by(users.c.id.desc()).compile(dialect=pg).string.splitlines()[-1])   # FROM users ORDER BY users.id DESC
```

### `SQLCompiler.positional` { #sqlcompiler-positional }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্টের paramstyle positional (`?`, `%s`, `$1`) কি না।

**উদাহরণ:**

```python
print(c.positional, select(users).where(users.c.id == 1).compile(dialect=sqlite.dialect()).positional)   # False True
```

### `SQLCompiler.positiontup` { #sqlcompiler-positiontup }

**ধরন:** অ্যাট্রিবিউট

positional paramstyle-এ প্যারামিটারগুলোর **ক্রম** (নামের তালিকা); named হলে `None`।

**উদাহরণ:**

```python
print(select(users).where(users.c.id == 1, users.c.name == "x").compile(dialect=sqlite.dialect()).positiontup)   # ['id_1', 'name_1']
```

### `SQLCompiler.post_compile_params` { #sqlcompiler-post-compile-params }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে প্যারামিটার চালানোর সময় খোলা হবে (যেমন `in_()`-এর expanding)।

**উদাহরণ:**

```python
ci = select(users).where(users.c.id.in_([1, 2])).compile(dialect=pg)
print([b.value for b in ci.post_compile_params])   # [[1, 2]]
```

### `SQLCompiler.post_process_text()` { #sqlcompiler-post-process-text }

```python
SQLCompiler.post_process_text(text)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`text()`-এর টেক্সট paramstyle অনুযায়ী ঠিক করে (যেমন `%` এস্কেপ)।

**উদাহরণ:**

```python
print(c.post_process_text("a % b"))   # a %% b
```

### `SQLCompiler.postfetch_lastrowid` { #sqlcompiler-postfetch-lastrowid }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT-এর পর `cursor.lastrowid` থেকে primary key আনবে কি না (RETURNING ব্যবহার না হলে, যেমন SQLite/MySQL-এ)।

**উদাহরণ:**

```python
print(insert(users).values(name="x").compile(dialect=sqlite.dialect()).postfetch_lastrowid)   # True
```

### `SQLCompiler.prefetch` { #sqlcompiler-prefetch }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`insert_prefetch` + `update_prefetch` একসাথে।

**উদাহরণ:**

```python
print(c.prefetch)   # []
```

### `SQLCompiler.preparer` { #sqlcompiler-preparer }

**ধরন:** অ্যাট্রিবিউট

নাম quote করার [`IdentifierPreparer`](#identifierpreparer)।

**উদাহরণ:**

```python
print(c.preparer.quote("order"))   # "order"
```

### `SQLCompiler.render_bind_cast()` { #sqlcompiler-render-bind-cast }

```python
SQLCompiler.render_bind_cast(type_, dbapi_type, sqltext)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

placeholder-এর সাথে cast লেখে (PostgreSQL psycopg-এ `%(x)s::INTEGER`)।

**উদাহরণ:**

```python
print(c.render_bind_cast(Integer(), Integer(), "%(x)s"))   # %(x)s::INTEGER
```

### `SQLCompiler.render_literal_bindparam()` { #sqlcompiler-render-literal-bindparam }

```python
SQLCompiler.render_literal_bindparam(bindparam, render_literal_value=_NoArg.NO_ARG, bind_expression_template=None, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি bind প্যারামিটার literal হিসেবে লেখে (`literal_binds=True` হলে)।

**উদাহরণ:**

```python
print(c.render_literal_bindparam(literal(5)))   # 5
```

### `SQLCompiler.render_literal_value()` { #sqlcompiler-render-literal-value }

```python
SQLCompiler.render_literal_value(value, type_)
```

**ধরন:** মেথড

একটি Python মানকে টাইপ অনুযায়ী SQL literal বানায় (স্ট্রিং হলে quote ও এস্কেপসহ)।

**উদাহরণ:**

```python
print(c.render_literal_value("O'Brien", String()), c.render_literal_value(42, Integer()))   # 'O''Brien' 42
```

### `SQLCompiler.render_table_with_column_in_update_from` { #sqlcompiler-render-table-with-column-in-update-from }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`UPDATE ... FROM`-এ কলামের আগে টেবিলের নাম লিখবে কি না (MySQL-এর জন্য)।

**উদাহরণ:**

```python
print(c.render_table_with_column_in_update_from)   # False
```

### `SQLCompiler.returning` { #sqlcompiler-returning }

**ধরন:** প্রপার্টি

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`effective_returning`-এর পুরোনো নাম।

**উদাহরণ:**

```python
ci = insert(users).returning(users.c.id).compile(dialect=pg)
print([col.name for col in ci.returning])   # ['id']
```

### `SQLCompiler.returning_clause()` { #sqlcompiler-returning-clause }

```python
SQLCompiler.returning_clause(stmt, returning_cols, *, populate_result_map, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`RETURNING ...` অংশ লেখার hook।

**উদাহরণ:**

```python
print(insert(users).returning(users.c.id).compile(dialect=pg).string.split(") ")[-1])   # RETURNING users.id
```

### `SQLCompiler.returning_precedes_values` { #sqlcompiler-returning-precedes-values }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`RETURNING`/`OUTPUT` VALUES-এর আগে বসবে কি না (SQL Server-এর `OUTPUT`)।

**উদাহরণ:**

```python
print(c.returning_precedes_values)   # False
```

### `SQLCompiler.stack` { #sqlcompiler-stack }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় ভেতরের স্টেটমেন্টের স্তূপ (সাবকুয়েরি ইত্যাদি)। শেষে খালি।

**উদাহরণ:**

```python
print(c.stack)   # []
```

### `SQLCompiler.translate_select_structure` { #sqlcompiler-translate-select-structure }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SELECT-এর গঠন বদলানোর hook (পুরোনো Oracle/SQL Server-এ LIMIT অনুকরণে)। সাধারণত `None`।

**উদাহরণ:**

```python
print(SQLCompiler.translate_select_structure)   # None
```

### `SQLCompiler.truncated_names` { #sqlcompiler-truncated-names }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`max_identifier_length`-এর চেয়ে লম্বা স্বয়ংক্রিয় নাম ছোট করার হিসাব।

**উদাহরণ:**

```python
print(c.truncated_names)   # {}
```

### `SQLCompiler.update_from_clause()` { #sqlcompiler-update-from-clause }

```python
SQLCompiler.update_from_clause(update_stmt, from_table, extra_froms, from_hints, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`UPDATE ... FROM` (একাধিক টেবিলের UPDATE) লেখার hook।

**উদাহরণ:**

```python
print(update(users).values(name=addresses.c.email).where(users.c.id == addresses.c.user_id).compile(dialect=pg).string)
# UPDATE users SET name=addresses.email FROM addresses WHERE users.id = addresses.user_id
```

### `SQLCompiler.update_post_criteria_clause()` { #sqlcompiler-update-post-criteria-clause }

```python
SQLCompiler.update_post_criteria_clause(update_stmt, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

UPDATE-এর WHERE-এর পরে কিছু যোগের hook (যেমন MySQL `LIMIT`)।

**উদাহরণ:**

```python
print(c.update_post_criteria_clause(update(users)))   # None
```

### `SQLCompiler.update_prefetch` { #sqlcompiler-update-prefetch }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

UPDATE-এর আগে Python-এ হিসাব করতে হবে এমন `onupdate` ডিফল্টের কলাম।

**উদাহরণ:**

```python
print(c.update_prefetch)   # ()
```

### `SQLCompiler.update_tables_clause()` { #sqlcompiler-update-tables-clause }

```python
SQLCompiler.update_tables_clause(update_stmt, from_table, extra_froms, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`UPDATE <টেবিল>` অংশের hook।

**উদাহরণ:**

```python
print(callable(c.update_tables_clause))   # True
```

## `StrSQLCompiler` { #strsqlcompiler }

```python
from sqlalchemy.sql.compiler import StrSQLCompiler
```

ডায়ালেক্ট ছাড়া `str(stmt)` দিলে যে কম্পাইলার চলে: "যতটা পারা যায়" SQL লেখে, এমনকি ডায়ালেক্ট-বিশেষ কনস্ট্রাক্টও (যেমন PostgreSQL JSON অপারেটর) মোটামুটি পড়ার মতো করে, এরর না দিয়ে। শুধু দেখার জন্য; চালানোর SQL সবসময় আসল ডায়ালেক্ট দিয়ে কম্পাইল হয়।

**উদাহরণ:**

```python
from sqlalchemy import JSON
t = table("docs", column("data", JSON))
compiled = select(t.c.data["name"]).compile()
print(type(compiled).__name__, str(compiled).splitlines()[0])   # StrSQLCompiler SELECT docs.data[:data_1] AS anon_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #strsqlcompiler-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `StrSQLCompiler`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`SQLCompiler` থেকে:** [`ansi_bind_rules`](#sqlcompiler-ansi-bind-rules) · [`bindname_escape_characters`](#sqlcompiler-bindname-escape-characters) · [`bindparam_string()`](#sqlcompiler-bindparam-string) · [`compound_keywords`](#sqlcompiler-compound-keywords) · [`construct_expanded_state()`](#sqlcompiler-construct-expanded-state) · [`current_executable`](#sqlcompiler-current-executable) · [`default_from()`](#sqlcompiler-default-from) · [`delete_extra_from_clause()`](#sqlcompiler-delete-extra-from-clause) · [`delete_post_criteria_clause()`](#sqlcompiler-delete-post-criteria-clause) · [`delete_table_clause()`](#sqlcompiler-delete-table-clause) · [`effective_returning`](#sqlcompiler-effective-returning) · [`escape_literal_column()`](#sqlcompiler-escape-literal-column) · [`escaped_bind_names`](#sqlcompiler-escaped-bind-names) · [`extract_map`](#sqlcompiler-extract-map) · [`fetch_clause()`](#sqlcompiler-fetch-clause) · [`for_update_clause()`](#sqlcompiler-for-update-clause) · [`format_from_hint_text()`](#sqlcompiler-format-from-hint-text) · [`function_argspec()`](#sqlcompiler-function-argspec) · [`get_crud_hint_text()`](#sqlcompiler-get-crud-hint-text) · [`get_cte_preamble()`](#sqlcompiler-get-cte-preamble) · [`get_from_hint_text()`](#sqlcompiler-get-from-hint-text) · [`get_render_as_alias_suffix()`](#sqlcompiler-get-render-as-alias-suffix) · [`get_select_hint_text()`](#sqlcompiler-get-select-hint-text) · [`get_select_precolumns()`](#sqlcompiler-get-select-precolumns) · [`get_statement_hint_text()`](#sqlcompiler-get-statement-hint-text) · [`group_by_clause()`](#sqlcompiler-group-by-clause) · [`has_out_parameters`](#sqlcompiler-has-out-parameters) · [`implicit_returning`](#sqlcompiler-implicit-returning) · [`inline`](#sqlcompiler-inline) · [`insert_prefetch`](#sqlcompiler-insert-prefetch) · [`insert_single_values_expr`](#sqlcompiler-insert-single-values-expr) · [`is_subquery()`](#sqlcompiler-is-subquery) · [`isdelete`](#sqlcompiler-isdelete) · [`isinsert`](#sqlcompiler-isinsert) · [`isplaintext`](#sqlcompiler-isplaintext) · [`isupdate`](#sqlcompiler-isupdate) · [`limit_clause()`](#sqlcompiler-limit-clause) · [`literal_execute_params`](#sqlcompiler-literal-execute-params) · [`order_by_clause()`](#sqlcompiler-order-by-clause) · [`positiontup`](#sqlcompiler-positiontup) · [`post_compile_params`](#sqlcompiler-post-compile-params) · [`post_process_text()`](#sqlcompiler-post-process-text) · [`postfetch_lastrowid`](#sqlcompiler-postfetch-lastrowid) · [`prefetch`](#sqlcompiler-prefetch) · [`render_bind_cast()`](#sqlcompiler-render-bind-cast) · [`render_literal_bindparam()`](#sqlcompiler-render-literal-bindparam) · [`render_literal_value()`](#sqlcompiler-render-literal-value) · [`render_table_with_column_in_update_from`](#sqlcompiler-render-table-with-column-in-update-from) · [`returning`](#sqlcompiler-returning) · [`returning_clause()`](#sqlcompiler-returning-clause) · [`returning_precedes_values`](#sqlcompiler-returning-precedes-values) · [`translate_select_structure`](#sqlcompiler-translate-select-structure) · [`update_from_clause()`](#sqlcompiler-update-from-clause) · [`update_post_criteria_clause()`](#sqlcompiler-update-post-criteria-clause) · [`update_prefetch`](#sqlcompiler-update-prefetch) · [`update_tables_clause()`](#sqlcompiler-update-tables-clause)

**`Compiled` থেকে:** [`cache_key`](#compiled-cache-key) · [`compile_state`](#compiled-compile-state) · [`construct_params()`](#compiled-construct-params) · [`dml_compile_state`](#compiled-dml-compile-state) · [`execution_options`](#compiled-execution-options) · [`is_ddl`](#compiled-is-ddl) · [`is_sql`](#compiled-is-sql) · [`params`](#compiled-params) · [`process()`](#compiled-process) · [`schema_translate_map`](#compiled-schema-translate-map) · [`sql_compiler`](#compiled-sql-compiler) · [`statement`](#compiled-statement) · [`string`](#compiled-string) · [`visit_unsupported_compilation()`](#compiled-visit-unsupported-compilation)

///

/// details | visit_* মেথড (StrSQLCompiler নিজে কয়েকটি বদলায়: JSON getitem, try_cast …) (১০১টি, দেখতে ক্লিক করুন)
    type: info

`SQLCompiler`-এর সব `visit_*` মেথড, সাথে কয়েকটি নিজস্ব, যেগুলো ডায়ালেক্ট-বিশেষ কনস্ট্রাক্টও একটি সাধারণ রূপে লেখে। ব্যাখ্যা উপরে [`SQLCompiler`](#sqlcompiler)-এর visit বক্সে।

`visit_aggregate_orderby_inline()` · `visit_aggregate_strings_func()` · `visit_aggregateorderby()` · `visit_alias()` · `visit_between_op_binary()` · `visit_binary()` · `visit_bindparam()` · `visit_case()` · `visit_cast()` · `visit_clauselist()` · `visit_collation()` · `visit_column()` · `visit_compound_select()` · `visit_contains_op_binary()` · `visit_cte()` · `visit_custom_op_binary()` · `visit_custom_op_unary_modifier()` · `visit_custom_op_unary_operator()` · `visit_delete()` · `visit_dmltargetcopy()` · `visit_element_list()` · `visit_empty_set_expr()` · `visit_empty_set_op_expr()` · `visit_endswith_op_binary()` · `visit_expression_clauselist()` · `visit_extract()` · `visit_false()` · `visit_floordiv_binary()` · `visit_frame_clause()` · `visit_fromclause()` · `visit_funcfilter()` · `visit_function()` · `visit_function_as_comparison_op_binary()` · `visit_getitem_binary()` · `visit_grouping()` · `visit_icontains_op_binary()` · `visit_iendswith_op_binary()` · `visit_ilike_case_insensitive_operand()` · `visit_ilike_op_binary()` · `visit_index()` · `visit_insert()` · `visit_is_false_unary_operator()` · `visit_is_true_unary_operator()` · `visit_istartswith_op_binary()` · `visit_join()` · `visit_json_getitem_op_binary()` · `visit_json_path_getitem_op_binary()` · `visit_label()` · `visit_label_reference()` · `visit_lambda_element()` · `visit_lateral()` · `visit_like_op_binary()` · `visit_mod_binary()` · `visit_next_value_func()` · `visit_not_between_op_binary()` · `visit_not_contains_op_binary()` · `visit_not_endswith_op_binary()` · `visit_not_icontains_op_binary()` · `visit_not_iendswith_op_binary()` · `visit_not_ilike_op_binary()` · `visit_not_in_op_binary()` · `visit_not_istartswith_op_binary()` · `visit_not_like_op_binary()` · `visit_not_match_op_binary()` · `visit_not_regexp_match_op_binary()` · `visit_not_startswith_op_binary()` · `visit_null()` · `visit_order_by_list()` · `visit_over()` · `visit_override_binds()` · `visit_regexp_match_op_binary()` · `visit_regexp_replace_op_binary()` · `visit_release_savepoint()` · `visit_rollback_to_savepoint()` · `visit_savepoint()` · `visit_scalar_function_column()` · `visit_scalar_values()` · `visit_select()` · `visit_select_statement_grouping()` · `visit_sequence()` · `visit_startswith_op_binary()` · `visit_subquery()` · `visit_table()` · `visit_table_valued_alias()` · `visit_table_valued_column()` · `visit_tablesample()` · `visit_textclause()` · `visit_textual_label_reference()` · `visit_textual_select()` · `visit_true()` · `visit_truediv_binary()` · `visit_try_cast()` · `visit_tstring()` · `visit_tstring_text()` · `visit_tuple()` · `visit_type_coerce()` · `visit_typeclause()` · `visit_unary()` · `visit_update()` · `visit_values()` · `visit_withingroup()`

///

## `DDLCompiler` { #ddlcompiler }

```python
from sqlalchemy.sql.compiler import DDLCompiler
```

`CREATE TABLE`, `CREATE INDEX`, `ALTER TABLE ADD CONSTRAINT` ইত্যাদি DDL কম্পাইল করে। ডায়ালেক্টের subclass (`PGDDLCompiler` …) কলামের ধরন (`SERIAL`), IDENTITY, টেবিলের শেষে অপশন (MySQL `ENGINE=`) ইত্যাদি বদলায়।

**উদাহরণ:**

```python
d = schema.CreateTable(users).compile(dialect=pg)
print(type(d).__name__, d.string.strip().splitlines()[1].strip())   # PGDDLCompiler id SERIAL NOT NULL,
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #ddlcompiler-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`create_table_constraints()`](#ddlcompiler-create-table-constraints) | মেথড (internal) | `CREATE TABLE`-এর ভেতরের কনস্ট্রেইন্টগুলো (PRIMARY KEY, FOREIGN KEY …) লেখে। |
| [`create_table_select_suffixes()`](#ddlcompiler-create-table-select-suffixes) | মেথড (internal) | (২.১) `CREATE TABLE ... AS SELECT` / `CREATE VIEW`-এর শেষের অংশ। |
| [`create_table_suffix()`](#ddlcompiler-create-table-suffix) | মেথড (internal) | `CREATE TABLE <নাম>`-এর ঠিক পরে কিছু বসানোর hook। |
| [`define_check_body()`](#ddlcompiler-define-check-body) | মেথড (internal) | `CHECK (...)`-এর ভেতরের শর্ত। |
| [`define_constraint_cascades()`](#ddlcompiler-define-constraint-cascades) | মেথড (internal) | FK-এর `ON DELETE ... ON UPDATE ...` অংশ। |
| [`define_constraint_deferrability()`](#ddlcompiler-define-constraint-deferrability) | মেথড (internal) | `DEFERRABLE INITIALLY DEFERRED` অংশ। |
| [`define_constraint_match()`](#ddlcompiler-define-constraint-match) | মেথড (internal) | FK-এর `MATCH FULL` ইত্যাদি অংশ। |
| [`define_constraint_ondelete_cascade()`](#ddlcompiler-define-constraint-ondelete-cascade) | মেথড (internal) | শুধু `ON DELETE ...` অংশ। |
| [`define_constraint_onupdate_cascade()`](#ddlcompiler-define-constraint-onupdate-cascade) | মেথড (internal) | শুধু `ON UPDATE ...` অংশ। |
| [`define_constraint_preamble()`](#ddlcompiler-define-constraint-preamble) | মেথড (internal) | `CONSTRAINT <নাম> ` অংশ (নাম থাকলে)। |
| [`define_constraint_remote_table()`](#ddlcompiler-define-constraint-remote-table) | মেথড (internal) | FK-এর `REFERENCES <টেবিল>`-এর টেবিল-নাম। |
| [`define_foreign_key_body()`](#ddlcompiler-define-foreign-key-body) | মেথড (internal) | `FOREIGN KEY(...) REFERENCES ...(...)` অংশ। |
| [`define_primary_key_body()`](#ddlcompiler-define-primary-key-body) | মেথড (internal) | `PRIMARY KEY (...)` অংশ। |
| [`define_unique_body()`](#ddlcompiler-define-unique-body) | মেথড (internal) | `UNIQUE (...)` অংশ। |
| [`define_unique_constraint_distinct()`](#ddlcompiler-define-unique-constraint-distinct) | মেথড (internal) | PostgreSQL ১৫-এর `UNIQUE NULLS NOT DISTINCT` ধরনের অংশ। |
| [`get_column_default_string()`](#ddlcompiler-get-column-default-string) | মেথড (internal) | কলামের `server_default` থেকে `DEFAULT ...` অংশের মান। |
| [`get_column_specification()`](#ddlcompiler-get-column-specification) | মেথড | `CREATE TABLE`-এ একটি কলামের পুরো লাইন: নাম, টাইপ, DEFAULT, NOT NULL। |
| [`get_identity_options()`](#ddlcompiler-get-identity-options) | মেথড (internal) | `Identity()`/`Sequence`-এর অপশন (`START WITH`, `INCREMENT BY` …) লেখে। |
| [`post_create_table()`](#ddlcompiler-post-create-table) | মেথড (internal) | `CREATE TABLE (...)`-এর পরে টেবিল-অপশন (MySQL `ENGINE=InnoDB`, PostgreSQL `PARTITION BY` …)। |
| [`render_default_string()`](#ddlcompiler-render-default-string) | মেথড (internal) | স্ট্রিং server_default-কে quote করে লেখে। |
| [`type_compiler`](#ddlcompiler-type-compiler) | প্রপার্টি (internal) | টাইপের নাম লেখার [`TypeCompiler`](#typecompiler) (ডায়ালেক্টেরটি)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DDLCompiler`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Compiled` থেকে:** [`cache_key`](#compiled-cache-key) · [`compile_state`](#compiled-compile-state) · [`construct_params()`](#compiled-construct-params) · [`dml_compile_state`](#compiled-dml-compile-state) · [`execution_options`](#compiled-execution-options) · [`is_ddl`](#compiled-is-ddl) · [`is_sql`](#compiled-is-sql) · [`params`](#compiled-params) · [`process()`](#compiled-process) · [`schema_translate_map`](#compiled-schema-translate-map) · [`sql_compiler`](#compiled-sql-compiler) · [`statement`](#compiled-statement) · [`string`](#compiled-string) · [`visit_unsupported_compilation()`](#compiled-visit-unsupported-compilation)

///

/// details | visit_* মেথড: প্রতিটি DDL কনস্ট্রাক্টের জন্য একটি (২৯টি, দেখতে ক্লিক করুন)
    type: info

`CreateTable` → `visit_create_table`, `CreateIndex` → `visit_create_index`, `CheckConstraint` → `visit_check_constraint` … প্রতিটি DDL কনস্ট্রাক্ট বা কনস্ট্রেইন্টের SQL লেখে। ডায়ালেক্ট এগুলো override করে; নিজের DDL কনস্ট্রাক্টে `@compiles` ব্যবহার করুন।

**উদাহরণ:**

```python
d = schema.CreateTable(users).compile(dialect=pg)
print(d.process(schema.CreateIndex(Index("ix_name", users.c.name))))   # CREATE INDEX ix_name ON users (name)
```

`visit_add_constraint()` · `visit_check_constraint()` · `visit_column_check_constraint()` · `visit_computed_column()` · `visit_create_column()` · `visit_create_index()` · `visit_create_schema()` · `visit_create_sequence()` · `visit_create_table()` · `visit_create_table_as()` · `visit_create_view()` · `visit_ddl()` · `visit_drop_column_comment()` · `visit_drop_constraint()` · `visit_drop_constraint_comment()` · `visit_drop_index()` · `visit_drop_schema()` · `visit_drop_sequence()` · `visit_drop_table()` · `visit_drop_table_comment()` · `visit_drop_view()` · `visit_foreign_key_constraint()` · `visit_identity_column()` · `visit_primary_key_constraint()` · `visit_set_column_comment()` · `visit_set_constraint_comment()` · `visit_set_table_comment()` · `visit_table_or_column_check_constraint()` · `visit_unique_constraint()`

///

### `DDLCompiler.create_table_constraints()` { #ddlcompiler-create-table-constraints }

```python
DDLCompiler.create_table_constraints(table, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CREATE TABLE`-এর ভেতরের কনস্ট্রেইন্টগুলো (PRIMARY KEY, FOREIGN KEY …) লেখে।

**উদাহরণ:**

```python
d = schema.CreateTable(addresses).compile(dialect=pg)
print(d.create_table_constraints(addresses).split("\n")[0].strip())   # PRIMARY KEY (id),
```

### `DDLCompiler.create_table_select_suffixes()` { #ddlcompiler-create-table-select-suffixes }

```python
DDLCompiler.create_table_select_suffixes(element, type_, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(২.১) `CREATE TABLE ... AS SELECT` / `CREATE VIEW`-এর শেষের অংশ।

**উদাহরণ:**

```python
print(callable(DDLCompiler.create_table_select_suffixes))   # True
```

### `DDLCompiler.create_table_suffix()` { #ddlcompiler-create-table-suffix }

```python
DDLCompiler.create_table_suffix(table)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CREATE TABLE <নাম>`-এর ঠিক পরে কিছু বসানোর hook।

**উদাহরণ:**

```python
d = schema.CreateTable(users).compile(dialect=pg)
print(repr(d.create_table_suffix(users)))   # ''
```

### `DDLCompiler.define_check_body()` { #ddlcompiler-define-check-body }

```python
DDLCompiler.define_check_body(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CHECK (...)`-এর ভেতরের শর্ত।

**উদাহরণ:**

```python
d = schema.CreateTable(users).compile(dialect=pg)
print(d.define_check_body(CheckConstraint("id > 0")))   # id > 0
```

### `DDLCompiler.define_constraint_cascades()` { #ddlcompiler-define-constraint-cascades }

```python
DDLCompiler.define_constraint_cascades(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FK-এর `ON DELETE ... ON UPDATE ...` অংশ।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("u", ForeignKey("users.id", ondelete="CASCADE")))
fk = list(t.foreign_key_constraints)[0]
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_cascades(fk))   #  ON DELETE CASCADE
```

### `DDLCompiler.define_constraint_deferrability()` { #ddlcompiler-define-constraint-deferrability }

```python
DDLCompiler.define_constraint_deferrability(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`DEFERRABLE INITIALLY DEFERRED` অংশ।

**উদাহরণ:**

```python
cc = CheckConstraint("x > 0", deferrable=True, initially="DEFERRED")
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_deferrability(cc))   #  DEFERRABLE INITIALLY DEFERRED
```

### `DDLCompiler.define_constraint_match()` { #ddlcompiler-define-constraint-match }

```python
DDLCompiler.define_constraint_match(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FK-এর `MATCH FULL` ইত্যাদি অংশ।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("u", ForeignKey("users.id", match="FULL")))
fk = list(t.foreign_key_constraints)[0]
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_match(fk))   #  MATCH FULL
```

### `DDLCompiler.define_constraint_ondelete_cascade()` { #ddlcompiler-define-constraint-ondelete-cascade }

```python
DDLCompiler.define_constraint_ondelete_cascade(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

শুধু `ON DELETE ...` অংশ।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("u", ForeignKey("users.id", ondelete="SET NULL")))
fk = list(t.foreign_key_constraints)[0]
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_ondelete_cascade(fk))   #  ON DELETE SET NULL
```

### `DDLCompiler.define_constraint_onupdate_cascade()` { #ddlcompiler-define-constraint-onupdate-cascade }

```python
DDLCompiler.define_constraint_onupdate_cascade(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

শুধু `ON UPDATE ...` অংশ।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("u", ForeignKey("users.id", onupdate="CASCADE")))
fk = list(t.foreign_key_constraints)[0]
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_onupdate_cascade(fk))   #  ON UPDATE CASCADE
```

### `DDLCompiler.define_constraint_preamble()` { #ddlcompiler-define-constraint-preamble }

```python
DDLCompiler.define_constraint_preamble(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CONSTRAINT <নাম> ` অংশ (নাম থাকলে)।

**উদাহরণ:**

```python
print(schema.CreateTable(users).compile(dialect=pg).define_constraint_preamble(CheckConstraint("x > 0", name="ck_x")))   # CONSTRAINT ck_x
```

### `DDLCompiler.define_constraint_remote_table()` { #ddlcompiler-define-constraint-remote-table }

```python
DDLCompiler.define_constraint_remote_table(constraint, table, preparer)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

FK-এর `REFERENCES <টেবিল>`-এর টেবিল-নাম।

**উদাহরণ:**

```python
print(callable(DDLCompiler.define_constraint_remote_table))   # True
```

### `DDLCompiler.define_foreign_key_body()` { #ddlcompiler-define-foreign-key-body }

```python
DDLCompiler.define_foreign_key_body(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`FOREIGN KEY(...) REFERENCES ...(...)` অংশ।

**উদাহরণ:**

```python
fk = list(addresses.foreign_key_constraints)[0]
print(schema.CreateTable(users).compile(dialect=pg).define_foreign_key_body(fk))   # FOREIGN KEY(user_id) REFERENCES users (id)
```

### `DDLCompiler.define_primary_key_body()` { #ddlcompiler-define-primary-key-body }

```python
DDLCompiler.define_primary_key_body(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`PRIMARY KEY (...)` অংশ।

**উদাহরণ:**

```python
print(schema.CreateTable(users).compile(dialect=pg).define_primary_key_body(users.primary_key))   # PRIMARY KEY (id)
```

### `DDLCompiler.define_unique_body()` { #ddlcompiler-define-unique-body }

```python
DDLCompiler.define_unique_body(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`UNIQUE (...)` অংশ।

**উদাহরণ:**

```python
uc = UniqueConstraint(users.c.name)
print(schema.CreateTable(users).compile(dialect=pg).define_unique_body(uc))   # UNIQUE (name)
```

### `DDLCompiler.define_unique_constraint_distinct()` { #ddlcompiler-define-unique-constraint-distinct }

```python
DDLCompiler.define_unique_constraint_distinct(constraint, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

PostgreSQL ১৫-এর `UNIQUE NULLS NOT DISTINCT` ধরনের অংশ।

**উদাহরণ:**

```python
uc = UniqueConstraint(users.c.name)
print(repr(schema.CreateTable(users).compile(dialect=pg).define_unique_constraint_distinct(uc)))   # ''
```

### `DDLCompiler.get_column_default_string()` { #ddlcompiler-get-column-default-string }

```python
DDLCompiler.get_column_default_string(column)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কলামের `server_default` থেকে `DEFAULT ...` অংশের মান।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("n", Integer, server_default="0"))
print(schema.CreateTable(t).compile(dialect=pg).get_column_default_string(t.c.n))   # '0'
```

### `DDLCompiler.get_column_specification()` { #ddlcompiler-get-column-specification }

```python
DDLCompiler.get_column_specification(column, **kwargs)
```

**ধরন:** মেথড

`CREATE TABLE`-এ একটি কলামের পুরো লাইন: নাম, টাইপ, DEFAULT, NOT NULL।

**উদাহরণ:**

```python
print(schema.CreateTable(users).compile(dialect=pg).get_column_specification(users.c.name))   # name VARCHAR(50)
```

### `DDLCompiler.get_identity_options()` { #ddlcompiler-get-identity-options }

```python
DDLCompiler.get_identity_options(identity_options)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Identity()`/`Sequence`-এর অপশন (`START WITH`, `INCREMENT BY` …) লেখে।

**উদাহরণ:**

```python
print(schema.CreateTable(users).compile(dialect=pg).get_identity_options(Identity(start=10, increment=5)))   # INCREMENT BY 5 START WITH 10
```

### `DDLCompiler.post_create_table()` { #ddlcompiler-post-create-table }

```python
DDLCompiler.post_create_table(table)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CREATE TABLE (...)`-এর পরে টেবিল-অপশন (MySQL `ENGINE=InnoDB`, PostgreSQL `PARTITION BY` …)।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("id", Integer), postgresql_partition_by="RANGE (id)")
print(schema.CreateTable(t).compile(dialect=pg).post_create_table(t))   #  PARTITION BY RANGE (id)
```

### `DDLCompiler.render_default_string()` { #ddlcompiler-render-default-string }

```python
DDLCompiler.render_default_string(default)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্ট্রিং server_default-কে quote করে লেখে।

**উদাহরণ:**

```python
print(schema.CreateTable(users).compile(dialect=pg).render_default_string("হ্যাঁ"))   # 'হ্যাঁ'
```

### `DDLCompiler.type_compiler` { #ddlcompiler-type-compiler }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টাইপের নাম লেখার [`TypeCompiler`](#typecompiler) (ডায়ালেক্টেরটি)।

**উদাহরণ:**

```python
print(type(schema.CreateTable(users).compile(dialect=pg).type_compiler).__name__)   # PGTypeCompiler
```

## টাইপ কম্পাইলার { #typecompiler-group }

## `TypeCompiler` { #typecompiler }

```python
from sqlalchemy.sql.compiler import TypeCompiler
```

SQL টাইপের নাম (`VARCHAR(50)`, `INTEGER`, `TIMESTAMP WITHOUT TIME ZONE`) লেখার মূল ক্লাস। `type_.compile(dialect=...)` এটি ব্যবহার করে। প্রতিটি ডায়ালেক্টের একটি subclass।

**উদাহরণ:**

```python
print(String(50).compile(dialect=pg), "|", pg.type_compiler_instance.process(Integer()))   # VARCHAR(50) | INTEGER
```

### কনস্ট্রাক্টরের প্যারামিটার { #typecompiler-params }

```python
TypeCompiler(dialect)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `dialect` | যে ডায়ালেক্টের জন্য। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typecompiler-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`ensure_kwarg`](#typecompiler-ensure-kwarg) | অ্যাট্রিবিউট (internal) | কোন মেথডগুলো (`visit_*`) `**kw` নিশ্চিতভাবে নেবে তার regex (পুরোনো ডায়ালেক্টের সামঞ্জস্যের জন্য)। |
| [`process()`](#typecompiler-process) | মেথড | একটি টাইপের SQL নাম দেয় (ভেতরে টাইপের `visit_*` ডাকে)। |

/// details | visit_* মেথড (১টি, দেখতে ক্লিক করুন)
    type: info

প্রতিটি টাইপের জন্য একটি (`visit_VARCHAR`, `visit_integer` …); ডায়ালেক্ট এগুলো বদলে নিজের টাইপ-নাম লেখে।

`visit_unsupported_compilation()`

///

### `TypeCompiler.ensure_kwarg` { #typecompiler-ensure-kwarg }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন মেথডগুলো (`visit_*`) `**kw` নিশ্চিতভাবে নেবে তার regex (পুরোনো ডায়ালেক্টের সামঞ্জস্যের জন্য)।

**উদাহরণ:**

```python
print(TypeCompiler.ensure_kwarg)   # visit_\w+
```

### `TypeCompiler.process()` { #typecompiler-process }

```python
TypeCompiler.process(type_, **kw)
```

**ধরন:** মেথড

একটি টাইপের SQL নাম দেয় (ভেতরে টাইপের `visit_*` ডাকে)।

**উদাহরণ:**

```python
print(sqlite.dialect().type_compiler_instance.process(String(10)))   # VARCHAR(10)
```

## `GenericTypeCompiler` { #generictypecompiler }

```python
from sqlalchemy.sql.compiler import GenericTypeCompiler
```

সব সাধারণ টাইপের ডিফল্ট নাম: CamelCase সাধারণ টাইপ (`String`, `DateTime`) কোন SQL-standard নামে যাবে (`visit_string` → `visit_VARCHAR`), আর প্রতিটি SQL-standard টাইপ কীভাবে লেখা হয়। ডায়ালেক্টের টাইপ কম্পাইলার এর subclass।

**উদাহরণ:**

```python
from sqlalchemy import DateTime, Boolean
g = GenericTypeCompiler(pg)
print(g.process(DateTime()), g.process(Boolean()), g.process(String(5)))   # DATETIME BOOLEAN VARCHAR(5)
print(DateTime().compile(dialect=pg))   # TIMESTAMP WITHOUT TIME ZONE  (PostgreSQL নিজের নাম দেয়)
```

### কনস্ট্রাক্টরের প্যারামিটার { #generictypecompiler-params }

```python
GenericTypeCompiler(dialect)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `dialect` | যে ডায়ালেক্টের জন্য। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #generictypecompiler-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `GenericTypeCompiler`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeCompiler` থেকে:** [`ensure_kwarg`](#typecompiler-ensure-kwarg) · [`process()`](#typecompiler-process)

///

/// details | visit_* মেথড: প্রতিটি টাইপের জন্য একটি (৪৭টি, দেখতে ক্লিক করুন)
    type: info

ছোট হাতের নাম (`visit_string`, `visit_datetime`, `visit_boolean` …) সাধারণ CamelCase টাইপের জন্য: এরা সাধারণত একটি বড় হাতের SQL-standard visit-এ পাঠায় (`visit_string` → `visit_VARCHAR`)। বড় হাতের নাম (`visit_VARCHAR`, `visit_TIMESTAMP` …) আসল SQL লেখে। নিজের `UserDefinedType`-এ এর বদলে `get_col_spec()` লিখুন।

**উদাহরণ:**

```python
g = GenericTypeCompiler(pg)
print(g.visit_string(String(10)), g.visit_VARCHAR(String(10)))   # VARCHAR(10) VARCHAR(10)
```

`visit_BIGINT()` · `visit_BINARY()` · `visit_BLOB()` · `visit_BOOLEAN()` · `visit_CHAR()` · `visit_CLOB()` · `visit_DATE()` · `visit_DATETIME()` · `visit_DECIMAL()` · `visit_DOUBLE()` · `visit_DOUBLE_PRECISION()` · `visit_FLOAT()` · `visit_INTEGER()` · `visit_NCHAR()` · `visit_NCLOB()` · `visit_NUMERIC()` · `visit_NVARCHAR()` · `visit_REAL()` · `visit_SMALLINT()` · `visit_TEXT()` · `visit_TIME()` · `visit_TIMESTAMP()` · `visit_UUID()` · `visit_VARBINARY()` · `visit_VARCHAR()` · `visit_big_integer()` · `visit_boolean()` · `visit_date()` · `visit_datetime()` · `visit_double()` · `visit_enum()` · `visit_float()` · `visit_integer()` · `visit_large_binary()` · `visit_null()` · `visit_numeric()` · `visit_real()` · `visit_small_integer()` · `visit_string()` · `visit_text()` · `visit_time()` · `visit_type_decorator()` · `visit_unicode()` · `visit_unicode_text()` · `visit_unsupported_compilation()` · `visit_user_defined()` · `visit_uuid()`

///

## `StrSQLTypeCompiler` { #strsqltypecompiler }

```python
from sqlalchemy.sql.compiler import StrSQLTypeCompiler
```

ডায়ালেক্ট ছাড়া টাইপ `str()` করলে যেটি চলে: অচেনা বা ডায়ালেক্ট-বিশেষ টাইপের জন্যও এরর না দিয়ে টাইপের নাম লেখে।

**উদাহরণ:**

```python
print(str(postgresql.JSONB()), str(postgresql.INET()))   # JSONB INET
```

### কনস্ট্রাক্টরের প্যারামিটার { #strsqltypecompiler-params }

```python
StrSQLTypeCompiler(dialect)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `dialect` | যে ডায়ালেক্টের জন্য। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #strsqltypecompiler-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `StrSQLTypeCompiler`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeCompiler` থেকে:** [`ensure_kwarg`](#typecompiler-ensure-kwarg) · [`process()`](#typecompiler-process)

///

/// details | visit_* মেথড (৪৭টি, দেখতে ক্লিক করুন)
    type: info

`GenericTypeCompiler`-এর সব visit, আর অচেনা টাইপের জন্য একটি সাধারণ fallback (টাইপের ক্লাসের নাম বড় হাতে)।

`visit_BIGINT()` · `visit_BINARY()` · `visit_BLOB()` · `visit_BOOLEAN()` · `visit_CHAR()` · `visit_CLOB()` · `visit_DATE()` · `visit_DATETIME()` · `visit_DECIMAL()` · `visit_DOUBLE()` · `visit_DOUBLE_PRECISION()` · `visit_FLOAT()` · `visit_INTEGER()` · `visit_NCHAR()` · `visit_NCLOB()` · `visit_NUMERIC()` · `visit_NVARCHAR()` · `visit_REAL()` · `visit_SMALLINT()` · `visit_TEXT()` · `visit_TIME()` · `visit_TIMESTAMP()` · `visit_UUID()` · `visit_VARBINARY()` · `visit_VARCHAR()` · `visit_big_integer()` · `visit_boolean()` · `visit_date()` · `visit_datetime()` · `visit_double()` · `visit_enum()` · `visit_float()` · `visit_integer()` · `visit_large_binary()` · `visit_null()` · `visit_numeric()` · `visit_real()` · `visit_small_integer()` · `visit_string()` · `visit_text()` · `visit_time()` · `visit_type_decorator()` · `visit_unicode()` · `visit_unicode_text()` · `visit_unsupported_compilation()` · `visit_user_defined()` · `visit_uuid()`

///

## নাম quote করা { #identifierpreparer-group }

## `IdentifierPreparer` { #identifierpreparer }

```python
from sqlalchemy.sql.compiler import IdentifierPreparer
```

টেবিল, কলাম, স্কিমা, কনস্ট্রেইন্টের নাম **কখন আর কীভাবে quote** করবে তা ঠিক করে। নিয়ম: নামটি reserved word (`order`, `user`), বড় হাতের অক্ষর আছে, বা অদ্ভুত অক্ষর আছে হলে quote (`"Order"`); নইলে quote ছাড়া। quote চিহ্ন ডায়ালেক্টভেদে আলাদা (PostgreSQL `"`, MySQL `` ` ``)। পেতে `dialect.identifier_preparer` বা `compiled.preparer`।

**উদাহরণ:**

```python
p = pg.identifier_preparer
print(p.quote("users"), p.quote("order"), p.quote("UserName"), mysql.dialect().identifier_preparer.quote("order"))
# users "order" "UserName" `order`
```

### কনস্ট্রাক্টরের প্যারামিটার { #identifierpreparer-params }

```python
IdentifierPreparer(dialect, initial_quote='"', final_quote=None, escape_quote='"', quote_case_sensitive_collations=True, omit_schema=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `dialect` | যে ডায়ালেক্টের জন্য। |
| `initial_quote` | শুরুর quote চিহ্ন (ডিফল্ট `"`)। |
| `final_quote` | শেষের quote চিহ্ন (ডিফল্ট `initial_quote`-এর মতো)। |
| `escape_quote` | নামের ভেতরে quote চিহ্ন থাকলে এস্কেপ করার চিহ্ন। |
| `quote_case_sensitive_collations` | collation-এর নাম quote করবে কি না। |
| `omit_schema` | স্কিমার নাম একেবারে বাদ দেবে কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #identifierpreparer-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`format_alias()`](#identifierpreparer-format-alias) | মেথড (internal) | alias-এর নাম (দরকার হলে quote করে)। |
| [`format_collation()`](#identifierpreparer-format-collation) | মেথড (internal) | collation-এর নাম। |
| [`format_column()`](#identifierpreparer-format-column) | মেথড | কলামের নাম quote করে (`use_table=True` দিলে টেবিলের নামসহ)। |
| [`format_constraint()`](#identifierpreparer-format-constraint) | মেথড (internal) | কনস্ট্রেইন্ট/ইনডেক্সের নাম (নামকরণ নিয়ম ও দৈর্ঘ্য ছোট করাসহ)। |
| [`format_index()`](#identifierpreparer-format-index) | মেথড (internal) | ইনডেক্সের নাম। |
| [`format_label()`](#identifierpreparer-format-label) | মেথড (internal) | label-এর নাম। |
| [`format_label_name()`](#identifierpreparer-format-label-name) | মেথড (internal) | শুধু নাম থেকে label (স্বয়ংক্রিয় নামসহ)। |
| [`format_savepoint()`](#identifierpreparer-format-savepoint) | মেথড (internal) | SAVEPOINT-এর নাম। |
| [`format_schema()`](#identifierpreparer-format-schema) | মেথড | স্কিমার নাম quote করে। |
| [`format_sequence()`](#identifierpreparer-format-sequence) | মেথড (internal) | Sequence-এর নাম (স্কিমাসহ)। |
| [`format_table()`](#identifierpreparer-format-table) | মেথড | টেবিলের নাম quote করে (স্কিমাসহ)। |
| [`format_table_seq()`](#identifierpreparer-format-table-seq) | মেথড (internal) | (স্কিমা, টেবিল) নাম tuple হিসেবে। |
| [`illegal_initial_characters`](#identifierpreparer-illegal-initial-characters) | অ্যাট্রিবিউট (internal) | যে অক্ষর দিয়ে শুরু হলে নাম quote করতে হয় (সংখ্যা, `$`)। |
| [`legal_characters`](#identifierpreparer-legal-characters) | অ্যাট্রিবিউট (internal) | quote ছাড়া চলে এমন অক্ষরের regex। |
| [`quote()`](#identifierpreparer-quote) | মেথড | **দরকার হলেই** quote করে (সবচেয়ে বেশি ব্যবহৃত)। |
| [`quote_identifier()`](#identifierpreparer-quote-identifier) | মেথড | **সবসময়** quote করে (ভেতরের quote এস্কেপসহ)। |
| [`quote_schema()`](#identifierpreparer-quote-schema) | মেথড | স্কিমার নাম দরকার হলে quote করে। |
| [`reserved_words`](#identifierpreparer-reserved-words) | অ্যাট্রিবিউট | এই ডায়ালেক্টের reserved word-এর set; এদের নাম হিসেবে ব্যবহার করলে quote হয়। |
| [`schema_for_object()`](#identifierpreparer-schema-for-object) | মেথড (internal) | একটি অবজেক্টের (Table ইত্যাদি) কার্যকর স্কিমা দেয় (`schema_translate_map` হিসাবসহ)। |
| [`truncate_and_render_constraint_name()`](#identifierpreparer-truncate-and-render-constraint-name) | মেথড (internal) | কনস্ট্রেইন্টের নাম `max_identifier_length` অনুযায়ী ছোট করে লেখে। |
| [`truncate_and_render_index_name()`](#identifierpreparer-truncate-and-render-index-name) | মেথড (internal) | ইনডেক্সের নাম ছোট করে লেখে। |
| [`unformat_identifiers()`](#identifierpreparer-unformat-identifiers) | মেথড | `schema.table.column` ধরনের স্ট্রিং ভেঙে অংশগুলো দেয় (quote খুলে)। |
| [`validate_sql_phrase()`](#identifierpreparer-validate-sql-phrase) | মেথড (internal) | কোনো টেক্সট নিরাপদ SQL কীওয়ার্ড-বাক্য কি না যাচাই করে (যেমন `ON DELETE`-এর মান), নইলে এরর। |

### `IdentifierPreparer.format_alias()` { #identifierpreparer-format-alias }

```python
IdentifierPreparer.format_alias(alias, name=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

alias-এর নাম (দরকার হলে quote করে)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_alias(users.alias("u")))   # u
```

### `IdentifierPreparer.format_collation()` { #identifierpreparer-format-collation }

```python
IdentifierPreparer.format_collation(collation_name, collation_schema=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

collation-এর নাম।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_collation("C"))   # "C"
```

### `IdentifierPreparer.format_column()` { #identifierpreparer-format-column }

```python
IdentifierPreparer.format_column(column, use_table=False, name=None, table_name=None, use_schema=False, anon_map=None)
```

**ধরন:** মেথড

কলামের নাম quote করে (`use_table=True` দিলে টেবিলের নামসহ)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_column(users.c.name, use_table=True))   # users.name
```

### `IdentifierPreparer.format_constraint()` { #identifierpreparer-format-constraint }

```python
IdentifierPreparer.format_constraint(constraint)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কনস্ট্রেইন্ট/ইনডেক্সের নাম (নামকরণ নিয়ম ও দৈর্ঘ্য ছোট করাসহ)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_constraint(CheckConstraint("x > 0", name="ck_x")))   # ck_x
```

### `IdentifierPreparer.format_index()` { #identifierpreparer-format-index }

```python
IdentifierPreparer.format_index(index)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ইনডেক্সের নাম।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_index(Index("ix_Name", users.c.name)))   # "ix_Name"
```

### `IdentifierPreparer.format_label()` { #identifierpreparer-format-label }

```python
IdentifierPreparer.format_label(label, name=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

label-এর নাম।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_label(users.c.name.label("full name")))   # "full name"
```

### `IdentifierPreparer.format_label_name()` { #identifierpreparer-format-label-name }

```python
IdentifierPreparer.format_label_name(name, anon_map=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

শুধু নাম থেকে label (স্বয়ংক্রিয় নামসহ)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_label_name("total"))   # total
```

### `IdentifierPreparer.format_savepoint()` { #identifierpreparer-format-savepoint }

```python
IdentifierPreparer.format_savepoint(savepoint, name=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SAVEPOINT-এর নাম।

**উদাহরণ:**

```python
from sqlalchemy.sql.elements import SavepointClause
print(pg.identifier_preparer.format_savepoint(SavepointClause("sa_1")))   # sa_1
```

### `IdentifierPreparer.format_schema()` { #identifierpreparer-format-schema }

```python
IdentifierPreparer.format_schema(name)
```

**ধরন:** মেথড

স্কিমার নাম quote করে।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_schema("Sales"))   # "Sales"
```

### `IdentifierPreparer.format_sequence()` { #identifierpreparer-format-sequence }

```python
IdentifierPreparer.format_sequence(sequence, use_schema=True)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

Sequence-এর নাম (স্কিমাসহ)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.format_sequence(Sequence("user_seq", schema="app")))   # app.user_seq
```

### `IdentifierPreparer.format_table()` { #identifierpreparer-format-table }

```python
IdentifierPreparer.format_table(table, use_schema=True, name=None)
```

**ধরন:** মেথড

টেবিলের নাম quote করে (স্কিমাসহ)।

**উদাহরণ:**

```python
t = Table("Orders", MetaData(), Column("id", Integer), schema="shop")
print(pg.identifier_preparer.format_table(t))   # shop."Orders"
```

### `IdentifierPreparer.format_table_seq()` { #identifierpreparer-format-table-seq }

```python
IdentifierPreparer.format_table_seq(table, use_schema=True)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(স্কিমা, টেবিল) নাম tuple হিসেবে।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("id", Integer), schema="s")
print(pg.identifier_preparer.format_table_seq(t))   # ('s', 't')
```

### `IdentifierPreparer.illegal_initial_characters` { #identifierpreparer-illegal-initial-characters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে অক্ষর দিয়ে শুরু হলে নাম quote করতে হয় (সংখ্যা, `$`)।

**উদাহরণ:**

```python
print("1" in pg.identifier_preparer.illegal_initial_characters)   # True
```

### `IdentifierPreparer.legal_characters` { #identifierpreparer-legal-characters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

quote ছাড়া চলে এমন অক্ষরের regex।

**উদাহরণ:**

```python
print(bool(pg.identifier_preparer.legal_characters.match("user_name")))   # True
```

### `IdentifierPreparer.quote()` { #identifierpreparer-quote }

```python
IdentifierPreparer.quote(ident)
```

**ধরন:** মেথড

**দরকার হলেই** quote করে (সবচেয়ে বেশি ব্যবহৃত)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.quote("name"), pg.identifier_preparer.quote("select"))   # name "select"
```

### `IdentifierPreparer.quote_identifier()` { #identifierpreparer-quote-identifier }

```python
IdentifierPreparer.quote_identifier(value)
```

**ধরন:** মেথড

**সবসময়** quote করে (ভেতরের quote এস্কেপসহ)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.quote_identifier('my"col'))   # "my""col"
```

### `IdentifierPreparer.quote_schema()` { #identifierpreparer-quote-schema }

```python
IdentifierPreparer.quote_schema(schema)
```

**ধরন:** মেথড

স্কিমার নাম দরকার হলে quote করে।

**উদাহরণ:**

```python
print(pg.identifier_preparer.quote_schema("public"))   # public
```

### `IdentifierPreparer.reserved_words` { #identifierpreparer-reserved-words }

**ধরন:** অ্যাট্রিবিউট

এই ডায়ালেক্টের reserved word-এর set; এদের নাম হিসেবে ব্যবহার করলে quote হয়।

**উদাহরণ:**

```python
print("order" in pg.identifier_preparer.reserved_words, len(pg.identifier_preparer.reserved_words) > 50)   # True True
```

### `IdentifierPreparer.schema_for_object()` { #identifierpreparer-schema-for-object }

```python
IdentifierPreparer.schema_for_object(obj, /)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টের (Table ইত্যাদি) কার্যকর স্কিমা দেয় (`schema_translate_map` হিসাবসহ)।

**উদাহরণ:**

```python
t = Table("t", MetaData(), Column("id", Integer), schema="s")
print(pg.identifier_preparer.schema_for_object(t))   # s
```

### `IdentifierPreparer.truncate_and_render_constraint_name()` { #identifierpreparer-truncate-and-render-constraint-name }

```python
IdentifierPreparer.truncate_and_render_constraint_name(name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কনস্ট্রেইন্টের নাম `max_identifier_length` অনুযায়ী ছোট করে লেখে।

**উদাহরণ:**

```python
print(pg.identifier_preparer.truncate_and_render_constraint_name("ck_short"))   # ck_short
```

### `IdentifierPreparer.truncate_and_render_index_name()` { #identifierpreparer-truncate-and-render-index-name }

```python
IdentifierPreparer.truncate_and_render_index_name(name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ইনডেক্সের নাম ছোট করে লেখে।

**উদাহরণ:**

```python
print(pg.identifier_preparer.truncate_and_render_index_name("ix_short"))   # ix_short
```

### `IdentifierPreparer.unformat_identifiers()` { #identifierpreparer-unformat-identifiers }

```python
IdentifierPreparer.unformat_identifiers(identifiers)
```

**ধরন:** মেথড

`schema.table.column` ধরনের স্ট্রিং ভেঙে অংশগুলো দেয় (quote খুলে)।

**উদাহরণ:**

```python
print(pg.identifier_preparer.unformat_identifiers('shop."Orders"'))   # ['shop', 'Orders']
```

### `IdentifierPreparer.validate_sql_phrase()` { #identifierpreparer-validate-sql-phrase }

```python
IdentifierPreparer.validate_sql_phrase(element, reg=re.compile('^\\w+(?:\\s+\\w+)*$'))
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোনো টেক্সট নিরাপদ SQL কীওয়ার্ড-বাক্য কি না যাচাই করে (যেমন `ON DELETE`-এর মান), নইলে এরর।

**উদাহরণ:**

```python
import re
allowed = re.compile(r"^(?:RESTRICT|CASCADE|SET NULL|NO ACTION|SET DEFAULT)$", re.I)
print(pg.identifier_preparer.validate_sql_phrase("SET NULL", allowed))   # SET NULL
try:
    pg.identifier_preparer.validate_sql_phrase("CASCADE; DROP TABLE x", allowed)
except Exception as e:
    print(type(e).__name__)   # CompileError
```

## সহায়ক অবজেক্ট { #expandedstate-group }

## `ExpandedState` { #expandedstate }

```python
from sqlalchemy.sql.compiler import ExpandedState
```

`SQLCompiler.construct_expanded_state()`-এর ফল (একটি named tuple): "expanding" প্যারামিটার (`in_()` তালিকা) খোলার পর **আসলে যে SQL আর প্যারামিটার ডেটাবেসে যায়**। লগে ঠিক SQL দেখতে কাজে লাগে।

**উদাহরণ:**

```python
ci = select(users.c.id).where(users.c.id.in_([7, 8])).compile(dialect=sqlite.dialect())
st = ci.construct_expanded_state()
print(st.statement.splitlines()[-1], st.positional_parameters)   # WHERE users.id IN (?, ?) (7, 8)
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #expandedstate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`additional_parameters`](#expandedstate-additional-parameters) | প্রপার্টি | `parameters`-এর আরেক নাম। |
| [`parameter_expansion`](#expandedstate-parameter-expansion) | অ্যাট্রিবিউট (internal) | কোন প্যারামিটার কোন নতুন নামগুলোতে খুলেছে। |
| [`parameters`](#expandedstate-parameters) | অ্যাট্রিবিউট | চূড়ান্ত প্যারামিটার dict (নাম → মান)। |
| [`positional_parameters`](#expandedstate-positional-parameters) | প্রপার্টি | positional paramstyle-এ প্যারামিটারের tuple (named paramstyle-এ এরর)। |
| [`positiontup`](#expandedstate-positiontup) | অ্যাট্রিবিউট | positional হলে প্যারামিটারের নামের ক্রম। |
| [`processors`](#expandedstate-processors) | অ্যাট্রিবিউট (internal) | প্যারামিটার পাঠানোর আগে মান বদলানোর ফাংশন (bind processor)। |
| [`statement`](#expandedstate-statement) | অ্যাট্রিবিউট | চূড়ান্ত SQL স্ট্রিং। |

### `ExpandedState.additional_parameters` { #expandedstate-additional-parameters }

**ধরন:** প্রপার্টি

`parameters`-এর আরেক নাম।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1])).compile(dialect=pg).construct_expanded_state()
print(st.additional_parameters == st.parameters)   # True
```

### `ExpandedState.parameter_expansion` { #expandedstate-parameter-expansion }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন প্যারামিটার কোন নতুন নামগুলোতে খুলেছে।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1, 2])).compile(dialect=pg).construct_expanded_state()
print(st.parameter_expansion)   # {'id_1': ['id_1_1', 'id_1_2']}
```

### `ExpandedState.parameters` { #expandedstate-parameters }

**ধরন:** অ্যাট্রিবিউট

চূড়ান্ত প্যারামিটার dict (নাম → মান)।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1, 2])).compile(dialect=pg).construct_expanded_state()
print(st.parameters)   # {'id_1_1': 1, 'id_1_2': 2}
```

### `ExpandedState.positional_parameters` { #expandedstate-positional-parameters }

**ধরন:** প্রপার্টি

positional paramstyle-এ প্যারামিটারের tuple (named paramstyle-এ এরর)।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1, 2])).compile(dialect=sqlite.dialect()).construct_expanded_state()
print(st.positional_parameters)   # (1, 2)
```

### `ExpandedState.positiontup` { #expandedstate-positiontup }

**ধরন:** অ্যাট্রিবিউট

positional হলে প্যারামিটারের নামের ক্রম।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1, 2])).compile(dialect=sqlite.dialect()).construct_expanded_state()
print(st.positiontup)   # ['id_1_1', 'id_1_2']
```

### `ExpandedState.processors` { #expandedstate-processors }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

প্যারামিটার পাঠানোর আগে মান বদলানোর ফাংশন (bind processor)।

**উদাহরণ:**

```python
st = select(users).where(users.c.id.in_([1])).compile(dialect=pg).construct_expanded_state()
print(type(st.processors).__name__)   # dict
```

### `ExpandedState.statement` { #expandedstate-statement }

**ধরন:** অ্যাট্রিবিউট

চূড়ান্ত SQL স্ট্রিং।

**উদাহরণ:**

```python
st = select(users.c.id).where(users.c.id.in_([1])).compile(dialect=pg).construct_expanded_state()
print(st.statement.splitlines()[-1])   # WHERE users.id IN (%(id_1_1)s::INTEGER)
```

## `ResultColumnsEntry` { #resultcolumnsentry }

```python
from sqlalchemy.sql.compiler import ResultColumnsEntry
```

(অভ্যন্তরীণ) কম্পাইলার প্রতিটি ফল-কলামের জন্য একটি রাখে: ফলের রো-তে কোন নামে আসবে আর কোন এক্সপ্রেশনের সাথে মেলে। `row._mapping[users.c.name]`-এর মতো লেখা এর মাধ্যমেই কাজ করে।

**উদাহরণ:**

```python
e = c._result_columns[1]
print(type(e).__name__, e.keyname, e.name)   # ResultColumnsEntry name name
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #resultcolumnsentry-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`keyname`](#resultcolumnsentry-keyname) | অ্যাট্রিবিউট | ফলের key। |
| [`name`](#resultcolumnsentry-name) | অ্যাট্রিবিউট | SQL-এ কলাম/label-এর নাম। |
| [`objects`](#resultcolumnsentry-objects) | অ্যাট্রিবিউট | এই কলামের সাথে মেলে এমন এক্সপ্রেশনগুলো (Column অবজেক্ট ইত্যাদি)। |
| [`type`](#resultcolumnsentry-type) | অ্যাট্রিবিউট | কলামের SQL টাইপ। |

### `ResultColumnsEntry.keyname` { #resultcolumnsentry-keyname }

**ধরন:** অ্যাট্রিবিউট

ফলের key।

**উদাহরণ:**

```python
print(c._result_columns[0].keyname)   # id
```

### `ResultColumnsEntry.name` { #resultcolumnsentry-name }

**ধরন:** অ্যাট্রিবিউট

SQL-এ কলাম/label-এর নাম।

**উদাহরণ:**

```python
print(c._result_columns[0].name)   # id
```

### `ResultColumnsEntry.objects` { #resultcolumnsentry-objects }

**ধরন:** অ্যাট্রিবিউট

এই কলামের সাথে মেলে এমন এক্সপ্রেশনগুলো (Column অবজেক্ট ইত্যাদি)।

**উদাহরণ:**

```python
print(users.c.id in c._result_columns[0].objects)   # True
```

### `ResultColumnsEntry.type` { #resultcolumnsentry-type }

**ধরন:** অ্যাট্রিবিউট

কলামের SQL টাইপ।

**উদাহরণ:**

```python
print(c._result_columns[1].type)   # VARCHAR(50)
```

## `CacheKey` { #cachekey }

```python
from sqlalchemy.sql.cache_key import CacheKey
```

SQL কম্পাইল-ক্যাশের key: স্টেটমেন্টের **গঠন** (মান নয়) থেকে তৈরি। একই গঠনের দুটি স্টেটমেন্ট (শুধু প্যারামিটারের মান আলাদা) একই key পায়, তাই দ্বিতীয়বার আর কম্পাইল করতে হয় না। এজন্যই SQLAlchemy ২.x বারবার একই কুয়েরিতে দ্রুত। নিজের কনস্ট্রাক্টে `inherit_cache = True` না দিলে ক্যাশ হয় না (সতর্কবার্তা আসে)।

**উদাহরণ:**

```python
k1 = select(users).where(users.c.id == 1)._generate_cache_key()
k2 = select(users).where(users.c.id == 2)._generate_cache_key()
print(type(k1).__name__, k1 == k2, [b.value for b in k2.bindparams])   # CacheKey True [2]
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cachekey-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bindparams`](#cachekey-bindparams) | অ্যাট্রিবিউট | স্টেটমেন্টের bind প্যারামিটারগুলো (এদের **মান** key-এর অংশ নয়)। |
| [`key`](#cachekey-key) | অ্যাট্রিবিউট (internal) | গঠনের আসল key (নেস্টেড tuple)। |
| [`params`](#cachekey-params) | অ্যাট্রিবিউট (internal) | (২.১) ক্যাশ-কী-তে অংশ নেওয়া অতিরিক্ত প্যারামিটার; সাধারণ স্টেটমেন্টে `None`। |
| [`to_offline_string()`](#cachekey-to-offline-string) | মেথড | key-টিকে একটি স্থায়ী **স্ট্রিং** বানায়: আসলে `(SQL, প্যারামিটারের মান)` tuple-এর `repr()`। |

### `CacheKey.bindparams` { #cachekey-bindparams }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের bind প্যারামিটারগুলো (এদের **মান** key-এর অংশ নয়)।

**উদাহরণ:**

```python
k = select(users).where(users.c.name == "x")._generate_cache_key()
print([b.value for b in k.bindparams])   # ['x']
```

### `CacheKey.key` { #cachekey-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

গঠনের আসল key (নেস্টেড tuple)।

**উদাহরণ:**

```python
print(type(select(users)._generate_cache_key().key).__name__)   # tuple
```

### `CacheKey.params` { #cachekey-params }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(২.১) ক্যাশ-কী-তে অংশ নেওয়া অতিরিক্ত প্যারামিটার; সাধারণ স্টেটমেন্টে `None`।

**উদাহরণ:**

```python
print(select(users)._generate_cache_key().params)   # None
```

### `CacheKey.to_offline_string()` { #cachekey-to-offline-string }

```python
CacheKey.to_offline_string(statement_cache, statement, parameters)
```

**ধরন:** মেথড

key-টিকে একটি স্থায়ী **স্ট্রিং** বানায়: আসলে `(SQL, প্যারামিটারের মান)` tuple-এর `repr()`। ফলাফল বাইরের ক্যাশে (Redis ইত্যাদি) রাখার "dogpile caching" রেসিপিতে key হিসেবে।

**উদাহরণ:**

```python
stmt = select(users.c.name).where(users.c.id == 5)
s = stmt._generate_cache_key().to_offline_string({}, stmt, {})
print(s)   # ('SELECT users.name \nFROM users \nWHERE users.id = :id_1', (5,))
```

## `Linting` { #linting }

```python
from sqlalchemy.sql.compiler import Linting
```

SQL "linting"-এর পছন্দ: স্টেটমেন্ট চালানোর সময় কম্পাইলার **cartesian product** (দুটি টেবিল join শর্ত ছাড়া) খুঁজে `SAWarning` দেবে কি না। `create_engine(..., enable_from_linting=False)` দিয়ে বন্ধ করা যায় (ডিফল্ট চালু)।

**উদাহরণ:**

```python
print(bool(Linting.FROM_LINTING & Linting.WARN_LINTING), Linting.FROM_LINTING.name)   # True FROM_LINTING
```

**Python `int`-এর সব মেথড** (`as_integer_ratio()`, `bit_count()`, `bit_length()`, `conjugate()`, `denominator()`, `from_bytes()`, `imag()`, `is_integer()`, `numerator()`, `real()`, `to_bytes()`) সাধারণ `int`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #linting-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`COLLECT_CARTESIAN_PRODUCTS`](#linting-COLLECT-CARTESIAN-PRODUCTS) | অ্যাট্রিবিউট | FROM-এর সম্পর্ক সংগ্রহ করবে (cartesian খোঁজার প্রথম ধাপ)। |
| [`FROM_LINTING`](#linting-FROM-LINTING) | অ্যাট্রিবিউট | <code>COLLECT_CARTESIAN_PRODUCTS &#124; WARN_LINTING</code>: পুরো ফিচার চালু (engine-এর ডিফল্ট)। |
| [`NO_LINTING`](#linting-NO-LINTING) | অ্যাট্রিবিউট | linting বন্ধ (শুধু `compile()` করলে এটাই)। |
| [`WARN_LINTING`](#linting-WARN-LINTING) | অ্যাট্রিবিউট | cartesian পেলে সতর্কবার্তা দেবে। |

### `Linting.COLLECT_CARTESIAN_PRODUCTS` { #linting-COLLECT-CARTESIAN-PRODUCTS }

**ধরন:** অ্যাট্রিবিউট

FROM-এর সম্পর্ক সংগ্রহ করবে (cartesian খোঁজার প্রথম ধাপ)।

**উদাহরণ:**

```python
print(int(Linting.COLLECT_CARTESIAN_PRODUCTS))   # 1
```

### `Linting.FROM_LINTING` { #linting-FROM-LINTING }

**ধরন:** অ্যাট্রিবিউট

`COLLECT_CARTESIAN_PRODUCTS | WARN_LINTING`: পুরো ফিচার চালু (engine-এর ডিফল্ট)।

**উদাহরণ:**

```python
print(Linting.FROM_LINTING == Linting.COLLECT_CARTESIAN_PRODUCTS | Linting.WARN_LINTING)   # True
```

### `Linting.NO_LINTING` { #linting-NO-LINTING }

**ধরন:** অ্যাট্রিবিউট

linting বন্ধ (শুধু `compile()` করলে এটাই)।

**উদাহরণ:**

```python
print(c.linting is Linting.NO_LINTING)   # True
```

### `Linting.WARN_LINTING` { #linting-WARN-LINTING }

**ধরন:** অ্যাট্রিবিউট

cartesian পেলে সতর্কবার্তা দেবে।

**উদাহরণ:**

```python
print(int(Linting.WARN_LINTING))   # 2
```

## `FromLinter` { #fromlinter }

```python
from sqlalchemy.sql.compiler import FromLinter
```

(অভ্যন্তরীণ) cartesian-product খোঁজার অবস্থা: FROM-এর টেবিলগুলো (`froms`) আর তাদের মধ্যে join-এর সংযোগ (`edges`)। সংযোগহীন টেবিল থাকলে `warn()` সতর্কবার্তা দেয়।

**উদাহরণ:**

```python
ci = select(users.c.id, addresses.c.id).compile(dialect=pg, linting=Linting.FROM_LINTING)
print(type(ci.from_linter).__name__, len(ci.from_linter.froms))   # FromLinter 2
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #fromlinter-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`edges`](#fromlinter-edges) | অ্যাট্রিবিউট | join শর্তে যুক্ত টেবিল-জোড়া। |
| [`froms`](#fromlinter-froms) | অ্যাট্রিবিউট | FROM-এর টেবিলগুলো। |
| [`lint()`](#fromlinter-lint) | মেথড | সংযোগহীন টেবিল খোঁজে: `(বিচ্ছিন্ন টেবিলগুলো, শুরুর টেবিল)` দেয়, সব যুক্ত হলে `(None, None)`। |
| [`warn()`](#fromlinter-warn) | মেথড | cartesian থাকলে `SAWarning` দেয়। |

### `FromLinter.edges` { #fromlinter-edges }

**ধরন:** অ্যাট্রিবিউট

join শর্তে যুক্ত টেবিল-জোড়া।

**উদাহরণ:**

```python
ci = select(users.c.id).join_from(users, addresses).compile(dialect=pg, linting=Linting.FROM_LINTING)
print(len(ci.from_linter.edges))   # 1
```

### `FromLinter.froms` { #fromlinter-froms }

**ধরন:** অ্যাট্রিবিউট

FROM-এর টেবিলগুলো।

**উদাহরণ:**

```python
ci = select(users.c.id).compile(dialect=pg, linting=Linting.FROM_LINTING)
print(len(ci.from_linter.froms))   # 1
```

### `FromLinter.lint()` { #fromlinter-lint }

```python
FromLinter.lint(start=None)
```

**ধরন:** মেথড

সংযোগহীন টেবিল খোঁজে: `(বিচ্ছিন্ন টেবিলগুলো, শুরুর টেবিল)` দেয়, সব যুক্ত হলে `(None, None)`।

**উদাহরণ:**

```python
ci = select(users.c.id, addresses.c.id).compile(dialect=pg, linting=Linting.FROM_LINTING)
lonely, start = ci.from_linter.lint()
print(len(lonely))   # 1
```

### `FromLinter.warn()` { #fromlinter-warn }

```python
FromLinter.warn(stmt_type='SELECT')
```

**ধরন:** মেথড

cartesian থাকলে `SAWarning` দেয়।

**উদাহরণ:**

```python
import warnings
ci = select(users.c.id, addresses.c.id).compile(dialect=pg, linting=Linting.FROM_LINTING)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    ci.from_linter.warn()
print(str(w[0].message)[:40])   # SELECT statement has a cartesian product
```

## `CompilerState` { #compilerstate }

```python
from sqlalchemy.sql.compiler import CompilerState
```

কম্পাইলারের অবস্থা (`compiled.state`)। এটি `IntEnum`, তাই Python ৩.১১+-এ `print()` করলে সংখ্যা দেখায়; নাম দেখতে `.name`।

**উদাহরণ:**

```python
print(c.state.name)   # STRING_APPLIED
```

**Python `int`-এর সব মেথড** (`as_integer_ratio()`, `bit_count()`, `bit_length()`, `conjugate()`, `denominator()`, `from_bytes()`, `imag()`, `is_integer()`, `numerator()`, `real()`, `to_bytes()`) সাধারণ `int`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #compilerstate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`COMPILING`](#compilerstate-COMPILING) | অ্যাট্রিবিউট | কম্পাইল চলছে। |
| [`NO_STATEMENT`](#compilerstate-NO-STATEMENT) | অ্যাট্রিবিউট | কোনো স্টেটমেন্ট ছাড়া বানানো কম্পাইলার (টুকরো কম্পাইলের জন্য)। |
| [`STRING_APPLIED`](#compilerstate-STRING-APPLIED) | অ্যাট্রিবিউট | কম্পাইল শেষ, `string` তৈরি। |

### `CompilerState.COMPILING` { #compilerstate-COMPILING }

**ধরন:** অ্যাট্রিবিউট

কম্পাইল চলছে।

**উদাহরণ:**

```python
print(int(CompilerState.COMPILING))   # 0
```

### `CompilerState.NO_STATEMENT` { #compilerstate-NO-STATEMENT }

**ধরন:** অ্যাট্রিবিউট

কোনো স্টেটমেন্ট ছাড়া বানানো কম্পাইলার (টুকরো কম্পাইলের জন্য)।

**উদাহরণ:**

```python
print(int(CompilerState.NO_STATEMENT))   # 2
```

### `CompilerState.STRING_APPLIED` { #compilerstate-STRING-APPLIED }

**ধরন:** অ্যাট্রিবিউট

কম্পাইল শেষ, `string` তৈরি।

**উদাহরণ:**

```python
print(int(CompilerState.STRING_APPLIED))   # 1
```

## `InsertmanyvaluesSentinelOpts` { #insertmanyvaluessentinelopts }

```python
from sqlalchemy.sql.compiler import InsertmanyvaluesSentinelOpts
```

(অভ্যন্তরীণ) ডায়ালেক্টের পতাকা: বাল্ক INSERT-এ (`insertmanyvalues`) কোন ধরনের primary key ডিফল্টকে "sentinel" হিসেবে (RETURNING-এর রো মেলাতে) বিশ্বাস করা যায়। `dialect.insertmanyvalues_implicit_sentinel`-এ থাকে।

**উদাহরণ:**

```python
print(pg.insertmanyvalues_implicit_sentinel & InsertmanyvaluesSentinelOpts.ANY_AUTOINCREMENT != 0)   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #insertmanyvaluessentinelopts-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`ANY_AUTOINCREMENT`](#insertmanyvaluessentinelopts-ANY-AUTOINCREMENT) | অ্যাট্রিবিউট | যেকোনো autoincrement ধরন (<code>AUTOINCREMENT &#124; IDENTITY &#124; SEQUENCE</code>)। |
| [`AUTOINCREMENT`](#insertmanyvaluessentinelopts-AUTOINCREMENT) | অ্যাট্রিবিউট | সাধারণ autoincrement (SERIAL, AUTO_INCREMENT)। |
| [`IDENTITY`](#insertmanyvaluessentinelopts-IDENTITY) | অ্যাট্রিবিউট | `GENERATED ... AS IDENTITY`। |
| [`MONOTONIC_FUNCTION`](#insertmanyvaluessentinelopts-MONOTONIC-FUNCTION) | অ্যাট্রিবিউট | ক্রমবর্ধমান মান দেয় এমন server ফাংশন। |
| [`NOT_SUPPORTED`](#insertmanyvaluessentinelopts-NOT-SUPPORTED) | অ্যাট্রিবিউট | কোনোটিই নয়। |
| [`RENDER_SELECT_COL_CASTS`](#insertmanyvaluessentinelopts-RENDER-SELECT-COL-CASTS) | অ্যাট্রিবিউট | `INSERT ... SELECT` রূপে কলামে cast লিখতে হবে। |
| [`SEQUENCE`](#insertmanyvaluessentinelopts-SEQUENCE) | অ্যাট্রিবিউট | `Sequence`-চালিত primary key। |
| [`USE_INSERT_FROM_SELECT`](#insertmanyvaluessentinelopts-USE-INSERT-FROM-SELECT) | অ্যাট্রিবিউট | বাল্ক INSERT `INSERT ... SELECT ... FROM (VALUES ...)` রূপে লিখবে। |

### `InsertmanyvaluesSentinelOpts.ANY_AUTOINCREMENT` { #insertmanyvaluessentinelopts-ANY-AUTOINCREMENT }

**ধরন:** অ্যাট্রিবিউট

যেকোনো autoincrement ধরন (`AUTOINCREMENT | IDENTITY | SEQUENCE`)।

**উদাহরণ:**

```python
print(bool(InsertmanyvaluesSentinelOpts.ANY_AUTOINCREMENT & InsertmanyvaluesSentinelOpts.IDENTITY))   # True
```

### `InsertmanyvaluesSentinelOpts.AUTOINCREMENT` { #insertmanyvaluessentinelopts-AUTOINCREMENT }

**ধরন:** অ্যাট্রিবিউট

সাধারণ autoincrement (SERIAL, AUTO_INCREMENT)।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.AUTOINCREMENT))   # 2
```

### `InsertmanyvaluesSentinelOpts.IDENTITY` { #insertmanyvaluessentinelopts-IDENTITY }

**ধরন:** অ্যাট্রিবিউট

`GENERATED ... AS IDENTITY`।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.IDENTITY))   # 4
```

### `InsertmanyvaluesSentinelOpts.MONOTONIC_FUNCTION` { #insertmanyvaluessentinelopts-MONOTONIC-FUNCTION }

**ধরন:** অ্যাট্রিবিউট

ক্রমবর্ধমান মান দেয় এমন server ফাংশন।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.MONOTONIC_FUNCTION))   # 16
```

### `InsertmanyvaluesSentinelOpts.NOT_SUPPORTED` { #insertmanyvaluessentinelopts-NOT-SUPPORTED }

**ধরন:** অ্যাট্রিবিউট

কোনোটিই নয়।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.NOT_SUPPORTED))   # 1
```

### `InsertmanyvaluesSentinelOpts.RENDER_SELECT_COL_CASTS` { #insertmanyvaluessentinelopts-RENDER-SELECT-COL-CASTS }

**ধরন:** অ্যাট্রিবিউট

`INSERT ... SELECT` রূপে কলামে cast লিখতে হবে।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.RENDER_SELECT_COL_CASTS))   # 64
```

### `InsertmanyvaluesSentinelOpts.SEQUENCE` { #insertmanyvaluessentinelopts-SEQUENCE }

**ধরন:** অ্যাট্রিবিউট

`Sequence`-চালিত primary key।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.SEQUENCE))   # 8
```

### `InsertmanyvaluesSentinelOpts.USE_INSERT_FROM_SELECT` { #insertmanyvaluessentinelopts-USE-INSERT-FROM-SELECT }

**ধরন:** অ্যাট্রিবিউট

বাল্ক INSERT `INSERT ... SELECT ... FROM (VALUES ...)` রূপে লিখবে।

**উদাহরণ:**

```python
print(int(InsertmanyvaluesSentinelOpts.USE_INSERT_FROM_SELECT))   # 32
```

## `AggregateOrderByStyle` { #aggregateorderbystyle }

```python
from sqlalchemy.sql.compiler import AggregateOrderByStyle
```

(২.১) ডেটাবেস aggregate ফাংশনের ভেতরে ORDER BY কীভাবে সমর্থন করে (`dialect.aggregate_order_by_style`): `array_agg(x ORDER BY y)` (INLINE), `... WITHIN GROUP (ORDER BY y)`, বা একেবারেই না। `aggregate_order_by()` এ অনুযায়ী SQL লেখে।

**উদাহরণ:**

```python
print(pg.aggregate_order_by_style.name, sqlite.dialect().aggregate_order_by_style.name)   # INLINE INLINE
```

**Python `int`-এর সব মেথড** (`as_integer_ratio()`, `bit_count()`, `bit_length()`, `conjugate()`, `denominator()`, `from_bytes()`, `imag()`, `is_integer()`, `numerator()`, `real()`, `to_bytes()`) সাধারণ `int`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aggregateorderbystyle-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`INLINE`](#aggregateorderbystyle-INLINE) | অ্যাট্রিবিউট | ফাংশনের আর্গুমেন্টের ভেতরে: `string_agg(x, ',' ORDER BY y)`। |
| [`NONE`](#aggregateorderbystyle-NONE) | অ্যাট্রিবিউট | সমর্থন নেই। |
| [`WITHIN_GROUP`](#aggregateorderbystyle-WITHIN-GROUP) | অ্যাট্রিবিউট | `... WITHIN GROUP (ORDER BY y)` রূপে (SQL Server, Oracle)। |

### `AggregateOrderByStyle.INLINE` { #aggregateorderbystyle-INLINE }

**ধরন:** অ্যাট্রিবিউট

ফাংশনের আর্গুমেন্টের ভেতরে: `string_agg(x, ',' ORDER BY y)`।

**উদাহরণ:**

```python
print(int(AggregateOrderByStyle.INLINE))   # 1
```

### `AggregateOrderByStyle.NONE` { #aggregateorderbystyle-NONE }

**ধরন:** অ্যাট্রিবিউট

সমর্থন নেই।

**উদাহরণ:**

```python
print(int(AggregateOrderByStyle.NONE))   # 0
```

### `AggregateOrderByStyle.WITHIN_GROUP` { #aggregateorderbystyle-WITHIN-GROUP }

**ধরন:** অ্যাট্রিবিউট

`... WITHIN GROUP (ORDER BY y)` রূপে (SQL Server, Oracle)।

**উদাহরণ:**

```python
print(int(AggregateOrderByStyle.WITHIN_GROUP))   # 2
```

## `aggregate_orderby_inline` { #aggregate-orderby-inline }

```python
from sqlalchemy.sql.compiler import aggregate_orderby_inline
```

(অভ্যন্তরীণ, ২.১) INLINE ধরনের ডেটাবেসে `aggregate_order_by()` লেখার জন্য কম্পাইলার যে মোড়ক-এক্সপ্রেশন বানায়: ফাংশনের আর্গুমেন্টের ভেতরে `ORDER BY` বসায়।

**উদাহরণ:**

```python
print(select(func.string_agg(users.c.name, ",").aggregate_order_by(users.c.id)).compile(dialect=pg).string.splitlines()[0])
# SELECT string_agg(users.name, %(string_agg_2)s::VARCHAR ORDER BY users.id) AS string_agg_1
```

### কনস্ট্রাক্টরের প্যারামিটার { #aggregate-orderby-inline-params }

```python
aggregate_orderby_inline(element, orderby)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | ফাংশনের আর্গুমেন্ট। |
| `orderby` | ভেতরের ORDER BY। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aggregate-orderby-inline-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`aggregate_order_by`](#aggregate-orderby-inline-aggregate-order-by) | অ্যাট্রিবিউট (internal) | ভেতরের ORDER BY এক্সপ্রেশন। |
| [`element`](#aggregate-orderby-inline-element) | অ্যাট্রিবিউট (internal) | মূল আর্গুমেন্ট। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `aggregate_orderby_inline`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compile()`](elements.md#columnelement-compile) · [`label()`](elements.md#columnelement-label) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `aggregate_orderby_inline.aggregate_order_by` { #aggregate-orderby-inline-aggregate-order-by }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ORDER BY এক্সপ্রেশন।

**উদাহরণ:**

```python
a = aggregate_orderby_inline(users.c.name, users.c.id)
print(a.aggregate_order_by)   # users.id
```

### `aggregate_orderby_inline.element` { #aggregate-orderby-inline-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল আর্গুমেন্ট।

**উদাহরণ:**

```python
a = aggregate_orderby_inline(users.c.name, users.c.id)
print(a.element)   # users.name
```

## `ilike_case_insensitive` { #ilike-case-insensitive }

```python
from sqlalchemy.sql.compiler import ilike_case_insensitive
```

(অভ্যন্তরীণ) যে ডেটাবেসে `ILIKE` নেই, সেখানে `ilike()` লিখতে কম্পাইলার উভয় পাশে `lower(...)` বসায়; এটি সেই মোড়ক।

**উদাহরণ:**

```python
print(select(users.c.id).where(users.c.name.ilike("র%")).compile(dialect=sqlite.dialect()).string.splitlines()[-1])
# WHERE lower(users.name) LIKE lower(?)
```

### কনস্ট্রাক্টরের প্যারামিটার { #ilike-case-insensitive-params }

```python
ilike_case_insensitive(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে এক্সপ্রেশন ছোট হাতে নেওয়া হবে। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #ilike-case-insensitive-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`comparator`](#ilike-case-insensitive-comparator) | অ্যাট্রিবিউট (internal) | মূল এক্সপ্রেশনের comparator। |
| [`element`](#ilike-case-insensitive-element) | অ্যাট্রিবিউট (internal) | মূল এক্সপ্রেশন। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ilike_case_insensitive`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnElement` থেকে:** [`allows_lambda`](elements.md#columnelement-allows-lambda) · [`compile()`](elements.md#columnelement-compile) · [`label()`](elements.md#columnelement-label) · [`proxy_set`](elements.md#columnelement-proxy-set) · [`self_group()`](elements.md#columnelement-self-group) · [`stringify_dialect`](elements.md#columnelement-stringify-dialect) · [`supports_execution`](elements.md#columnelement-supports-execution) · [`type`](elements.md#columnelement-type) · [`uses_inspection`](elements.md#columnelement-uses-inspection)

///

### `ilike_case_insensitive.comparator` { #ilike-case-insensitive-comparator }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল এক্সপ্রেশনের comparator।

**উদাহরণ:**

```python
print(type(ilike_case_insensitive(users.c.name).comparator).__name__)   # Comparator
```

### `ilike_case_insensitive.element` { #ilike-case-insensitive-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল এক্সপ্রেশন।

**উদাহরণ:**

```python
print(ilike_case_insensitive(users.c.name).element)   # users.name
```

## `prefix_anon_map` { #prefix-anon-map }

```python
from sqlalchemy.sql.compiler import prefix_anon_map
```

(অভ্যন্তরীণ) নামহীন এক্সপ্রেশনের জন্য স্বয়ংক্রিয় নাম (`anon_1`, `param_1`) বানানোর dict: প্রতিটি উপসর্গের জন্য গণনা রাখে।

**উদাহরণ:**

```python
print(type(c.anon_map).__name__, isinstance(c.anon_map, dict))   # prefix_anon_map True
```

**Python `dict`-এর সব মেথড** (`clear()`, `copy()`, `fromkeys()`, `get()`, `items()`, `keys()`, `pop()`, `popitem()`, `setdefault()`, `update()`, `values()`) সাধারণ `dict`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।
