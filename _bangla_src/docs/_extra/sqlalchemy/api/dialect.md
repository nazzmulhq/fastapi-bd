# ডায়ালেক্ট API: Dialect, ExecutionContext, ExceptionContext, DB-API protocol { #api-dialect }

/// note | এই পেজে যা আছে

SQLAlchemy আর ডেটাবেস ড্রাইভারের (DB-API) মাঝের স্তর:

* `Dialect` (ইন্টারফেস) আর `DefaultDialect` (ডিফল্ট বাস্তবায়ন): ডেটাবেস কী কী পারে, কীভাবে সংযোগ, transaction, SQL চালানো, isolation level, reflection।
* `ExecutionContext` / `DefaultExecutionContext`: একটি স্টেটমেন্ট চালানোর সময়ের সব তথ্য।
* `ExceptionContext`: `handle_error` ইভেন্টে এররের সব তথ্য।
* DB-API protocol: `DBAPIConnection`, `DBAPICursor`, `DBAPIModule`, `DBAPIType`; আর `AdaptedConnection`, `BindTyping`, `CacheStats`, `ConnectionEventsTarget`।

///

প্রতিটি ডেটাবেস + ড্রাইভারের জন্য একটি `Dialect` ক্লাস আছে (`postgresql+psycopg`, `sqlite+pysqlite` …); `engine.dialect` সেটি। সাধারণ অ্যাপে দরকার পড়ে **তথ্য জানতে** ("এই ডেটাবেস কি RETURNING পারে?", "সার্ভারের ভার্সন কত?") আর ইভেন্ট হুকে (`before_cursor_execute`-এর `context`, `handle_error`-এর `ExceptionContext`)। নতুন ডায়ালেক্ট লেখকদের জন্য বাকি সব hook।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
pg, sl, my = postgresql.dialect(), sqlite.dialect(), mysql.dialect()   # শুধু তুলনার জন্য, সংযোগ ছাড়া
engine = create_engine("sqlite://")                                       # আসল সংযোগসহ উদাহরণের জন্য
users = Table("users", m, Column("id", Integer, primary_key=True), Column("name", String(50)))
d = engine.dialect                                                        # সংযোগের পর initialize হওয়া ডায়ালেক্ট
```

`users`-এ রহিম আর করিম। SQLite (Python-এর সাথে আসা) দিয়ে চালানো।

///

## Dialect { #dialect-group }

## `Dialect` { #dialect }

```python
from sqlalchemy.engine import Dialect
```

একটি ডেটাবেস + ড্রাইভারের সব বিশেষত্ব এক জায়গায়: কোন SQL কম্পাইলার, কোন টাইপ, কোন quote চিহ্ন, ড্রাইভারের কোন ফাংশনে সংযোগ/commit/execute, কোন ফিচার সমর্থিত। `engine.dialect` দিয়ে পাওয়া যায়; প্রথম সংযোগের পর `initialize()` চলে, তখন সার্ভারের ভার্সন ইত্যাদি জানা যায়।

এখানে `Dialect` একটি **ইন্টারফেস** (কোন কোন সদস্য থাকবে তার বর্ণনা); আসল বাস্তবায়ন [`DefaultDialect`](#defaultdialect) আর তার ডায়ালেক্ট-বিশেষ subclass।

**উদাহরণ:**

```python
print(type(d).__name__, d.name, d.driver, d.server_version_info[:1])   # SQLiteDialect_pysqlite sqlite pysqlite (3,)
print(pg.insert_returning, my.insert_returning, isinstance(pg, Dialect))   # True False True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dialect-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`CACHE_HIT`](#dialect-CACHE-HIT) | অ্যাট্রিবিউট | [`CacheStats`](#cachestats)-এর একটি মান: SQL কম্পাইল-ক্যাশে পাওয়া গেছে। |
| [`CACHE_MISS`](#dialect-CACHE-MISS) | অ্যাট্রিবিউট | ক্যাশে ছিল না, এবার কম্পাইল করে রাখা হলো (লগে `[generated in ...]`)। |
| [`CACHING_DISABLED`](#dialect-CACHING-DISABLED) | অ্যাট্রিবিউট | ক্যাশ বন্ধ (`query_cache_size=0` বা `compiled_cache=None`)। |
| [`NO_CACHE_KEY`](#dialect-NO-CACHE-KEY) | অ্যাট্রিবিউট | স্টেটমেন্টের cache key বানানো যায়নি (যেমন `inherit_cache` ছাড়া কাস্টম কনস্ট্রাক্ট)। |
| [`NO_DIALECT_SUPPORT`](#dialect-NO-DIALECT-SUPPORT) | অ্যাট্রিবিউট | ডায়ালেক্টটি ক্যাশিং সমর্থন করে না (`supports_statement_cache = False`)। |
| [`aggregate_order_by_style`](#dialect-aggregate-order-by-style) | অ্যাট্রিবিউট | (২.১) aggregate-এর ভেতরে ORDER BY কীভাবে লেখা হয়: [`AggregateOrderByStyle`](compiler.md#aggregateorderbystyle)। |
| [`bind_typing`](#dialect-bind-typing) | অ্যাট্রিবিউট | bind প্যারামিটারের টাইপ ড্রাইভারকে কীভাবে জানানো হয়: [`BindTyping`](#bindtyping) (`NONE`, `SETINPUTSIZES`, `RENDER_CASTS`)। |
| [`colspecs`](#dialect-colspecs) | অ্যাট্রিবিউট (internal) | সাধারণ টাইপ → এই ডায়ালেক্টের বিশেষ টাইপ-ক্লাসের ম্যাপ (যেমন SQLite-এ `DateTime` → নিজের `DATETIME`)। |
| [`compiler_linting`](#dialect-compiler-linting) | অ্যাট্রিবিউট (internal) | কম্পাইলের সময় কোন [`Linting`](compiler.md#linting) পতাকা: `create_engine()`-এর ডিফল্টে `COLLECT_CARTESIAN_PRODUCTS` (সতর্কবার্তার অংশ `WARN_LINTING` চালানোর সময় যোগ হয়)। |
| [`connect()`](#dialect-connect) | মেথড | ড্রাইভার দিয়ে একটি নতুন DB-API সংযোগ খোলে (`dbapi.connect(*cargs, **cparams)`)। |
| [`construct_arguments`](#dialect-construct-arguments) | অ্যাট্রিবিউট (internal) | ডায়ালেক্ট-বিশেষ কীওয়ার্ড (যেমন `Table(..., postgresql_partition_by=...)`) কোন কনস্ট্রাক্টে বৈধ তার তালিকা। |
| [`create_connect_args()`](#dialect-create-connect-args) | মেথড | `URL` থেকে ড্রাইভারের `connect()`-এর আর্গুমেন্ট (`(args, kwargs)`) বানায়। |
| [`dbapi`](#dialect-dbapi) | অ্যাট্রিবিউট | লোড করা ড্রাইভার মডিউল (`sqlite3`, `psycopg` …); শুধু কম্পাইলের জন্য বানানো ডায়ালেক্টে `None`। |
| [`dbapi_exception_translation_map`](#dialect-dbapi-exception-translation-map) | অ্যাট্রিবিউট (internal) | ড্রাইভারের এরর-ক্লাসের নাম PEP 249-এর নামের সাথে না মিললে নাম-বদলের ম্যাপ। |
| [`dbapi_version`](#dialect-dbapi-version) | প্রপার্টি | ড্রাইভারের ভার্সন (`VersionInfo`, tuple-এর মতো তুলনা চলে)। |
| [`ddl_compiler`](#dialect-ddl-compiler) | অ্যাট্রিবিউট | DDL কম্পাইলার ক্লাস ([`DDLCompiler`](compiler.md#ddlcompiler)-এর subclass)। |
| [`default_isolation_level`](#dialect-default-isolation-level) | অ্যাট্রিবিউট | সংযোগের সময় সার্ভারের ডিফল্ট isolation level (initialize-এর পরে পাওয়া যায়)। |
| [`default_metavalue_token`](#dialect-default-metavalue-token) | অ্যাট্রিবিউট (internal) | ডিফল্ট মান বোঝাতে INSERT-এ যে শব্দ বসে (`DEFAULT`)। |
| [`default_schema_name`](#dialect-default-schema-name) | অ্যাট্রিবিউট | সংযোগের ডিফল্ট স্কিমা (PostgreSQL-এ সাধারণত `public`, SQLite-এ `main`), initialize-এর পরে। |
| [`default_sequence_base`](#dialect-default-sequence-base) | অ্যাট্রিবিউট (internal) | Sequence-এর ডিফল্ট শুরুর মান। |
| [`denormalize_name()`](#dialect-denormalize-name) | মেথড (internal) | ছোট হাতের নাম ডেটাবেসের নিজের ধরনে (বড় হাতে) বদলায়। |
| [`detect_autocommit_setting()`](#dialect-detect-autocommit-setting) | মেথড | একটি DB-API সংযোগে autocommit চালু কি না দেখে। |
| [`dialect_description`](#dialect-dialect-description) | অ্যাট্রিবিউট | `name+driver` রূপের বর্ণনা। |
| [`dialect_injects_custom_json_deserializer`](#dialect-dialect-injects-custom-json-deserializer) | অ্যাট্রিবিউট (internal) | ডায়ালেক্ট নিজের JSON deserializer ড্রাইভারে বসায় কি না। |
| [`do_begin()`](#dialect-do-begin) | মেথড (internal) | transaction শুরু (বেশিরভাগ ড্রাইভারে কিছুই করতে হয় না: DB-API নিজে থেকে শুরু করে)। |
| [`do_close()`](#dialect-do-close) | মেথড (internal) | DB-API সংযোগ বন্ধ করে (`connection.close()`)। |
| [`do_commit()`](#dialect-do-commit) | মেথড | `connection.commit()` চালায়। |
| [`do_execute()`](#dialect-do-execute) | মেথড | `cursor.execute(statement, parameters)` চালায়। |
| [`do_execute_no_params()`](#dialect-do-execute-no-params) | মেথড (internal) | প্যারামিটার ছাড়া `cursor.execute(statement)`। |
| [`do_executemany()`](#dialect-do-executemany) | মেথড | `cursor.executemany(statement, parameters)` (অনেক রো একসাথে)। |
| [`do_ping()`](#dialect-do-ping) | মেথড | সংযোগ বেঁচে আছে কি না পরীক্ষা (`pool_pre_ping=True` এটি ব্যবহার করে)। |
| [`do_release_savepoint()`](#dialect-do-release-savepoint) | মেথড (internal) | `RELEASE SAVEPOINT <নাম>`। |
| [`do_rollback()`](#dialect-do-rollback) | মেথড | `connection.rollback()`। |
| [`do_rollback_to_savepoint()`](#dialect-do-rollback-to-savepoint) | মেথড (internal) | `ROLLBACK TO SAVEPOINT <নাম>`। |
| [`do_savepoint()`](#dialect-do-savepoint) | মেথড (internal) | `SAVEPOINT <নাম>` (`begin_nested()` এটি ডাকে)। |
| [`do_set_input_sizes()`](#dialect-do-set-input-sizes) | মেথড (internal) | `cursor.setinputsizes()` ডাকে (`bind_typing = SETINPUTSIZES` এমন ড্রাইভারে, যেমন cx_Oracle)। |
| [`do_terminate()`](#dialect-do-terminate) | মেথড (internal) | সংযোগ জোর করে বন্ধ (অপেক্ষা না করে), যেমন async ড্রাইভারে cancel হলে। |
| [`driver`](#dialect-driver) | অ্যাট্রিবিউট | ড্রাইভারের নাম। |
| [`engine_config_types`](#dialect-engine-config-types) | অ্যাট্রিবিউট (internal) | `engine_from_config()`-এ স্ট্রিং মানকে কোন টাইপে বদলাবে (`pool_timeout` → int …)। |
| [`engine_created()`](#dialect-engine-created) | ক্লাস মেথড (internal) | (ক্লাস মেথড) `create_engine()` engine বানানোর ঠিক আগে ডাকে; ডায়ালেক্ট নিজের ইভেন্ট বসাতে পারে। |
| [`exclude_set_input_sizes`](#dialect-exclude-set-input-sizes) | অ্যাট্রিবিউট (internal) | setinputsizes-এ যে DB-API টাইপগুলো বাদ যাবে। |
| [`execute_sequence_format`](#dialect-execute-sequence-format) | অ্যাট্রিবিউট (internal) | positional প্যারামিটার কোন ধরনের sequence-এ পাঠাবে (`tuple` বা `list`)। |
| [`execution_ctx_cls`](#dialect-execution-ctx-cls) | অ্যাট্রিবিউট | execution context-এর ক্লাস ([`DefaultExecutionContext`](#defaultexecutioncontext)-এর subclass)। |
| [`get_async_dialect_cls()`](#dialect-get-async-dialect-cls) | ক্লাস মেথড (internal) | (ক্লাস মেথড) async engine-এর জন্য কোন ডায়ালেক্ট ক্লাস (সাধারণত `get_dialect_cls()`-এর মতো)। |
| [`get_default_isolation_level()`](#dialect-get-default-isolation-level) | মেথড | সংযোগ থেকে ডিফল্ট isolation level পড়ে। |
| [`get_dialect_cls()`](#dialect-get-dialect-cls) | ক্লাস মেথড (internal) | (ক্লাস মেথড) URL থেকে আসলে কোন ডায়ালেক্ট ক্লাস হবে (plugin/তৃতীয় পক্ষ বদলাতে পারে)। |
| [`get_dialect_pool_class()`](#dialect-get-dialect-pool-class) | মেথড | URL অনুযায়ী ডিফল্ট পুল ক্লাস (যেমন SQLite মেমোরিতে `SingletonThreadPool`, ফাইলে `QueuePool`)। |
| [`get_driver_connection()`](#dialect-get-driver-connection) | মেথড | পুলের মোড়ক থেকে ড্রাইভারের আসল সংযোগ অবজেক্ট (async ড্রাইভারে আসল asyncpg সংযোগ)। |
| [`get_isolation_level()`](#dialect-get-isolation-level) | মেথড | সংযোগের বর্তমান isolation level। |
| [`get_isolation_level_values()`](#dialect-get-isolation-level-values) | মেথড | এই ডায়ালেক্টে বৈধ isolation level-এর নাম। |
| [`has_terminate`](#dialect-has-terminate) | অ্যাট্রিবিউট (internal) | `do_terminate()`-এর আলাদা বাস্তবায়ন আছে কি না। |
| [`identifier_preparer`](#dialect-identifier-preparer) | অ্যাট্রিবিউট | নাম quote করার [`IdentifierPreparer`](compiler.md#identifierpreparer) অবজেক্ট। |
| [`import_dbapi()`](#dialect-import-dbapi) | ক্লাস মেথড | (ক্লাস মেথড) ড্রাইভার মডিউল ইমপোর্ট করে ফেরত দেয়। |
| [`include_set_input_sizes`](#dialect-include-set-input-sizes) | অ্যাট্রিবিউট (internal) | setinputsizes-এ শুধু যে DB-API টাইপগুলো যাবে। |
| [`initialize()`](#dialect-initialize) | মেথড | প্রথম সংযোগের সময় একবার চলে: সার্ভারের ভার্সন, ডিফল্ট স্কিমা, isolation level ইত্যাদি পড়ে পতাকা ঠিক করে। |
| [`insertmanyvalues_implicit_sentinel`](#dialect-insertmanyvalues-implicit-sentinel) | অ্যাট্রিবিউট (internal) | কোন primary key ধরনকে sentinel হিসেবে বিশ্বাস করে: [`InsertmanyvaluesSentinelOpts`](compiler.md#insertmanyvaluessentinelopts)। |
| [`insertmanyvalues_max_parameters`](#dialect-insertmanyvalues-max-parameters) | অ্যাট্রিবিউট | insertmanyvalues-এ একটি স্টেটমেন্টে সর্বোচ্চ কত প্যারামিটার (এর বেশি হলে ভাগ করে চালায়)। |
| [`insertmanyvalues_page_size`](#dialect-insertmanyvalues-page-size) | অ্যাট্রিবিউট | insertmanyvalues-এ একটি স্টেটমেন্টে সর্বোচ্চ কত রো (`create_engine(insertmanyvalues_page_size=...)`)। |
| [`is_async`](#dialect-is-async) | অ্যাট্রিবিউট | async ড্রাইভার (asyncpg, aiosqlite …) কি না। |
| [`is_disconnect()`](#dialect-is-disconnect) | মেথড | একটি ড্রাইভার-এরর "সংযোগ কেটে গেছে" ধরনের কি না; `True` হলে SQLAlchemy সংযোগ বাতিল করে (`connection_invalidated`)। |
| [`label_length`](#dialect-label-length) | অ্যাট্রিবিউট (internal) | `create_engine(label_length=...)` দিলে স্বয়ংক্রিয় label-এর দৈর্ঘ্যসীমা, নইলে `None`। |
| [`load_provisioning()`](#dialect-load-provisioning) | ক্লাস মেথড (internal) | (ক্লাস মেথড) SQLAlchemy-র টেস্ট-স্যুটের জন্য ডায়ালেক্টের provision মডিউল লোড করে। |
| [`loaded_dbapi`](#dialect-loaded-dbapi) | প্রপার্টি | `dbapi`-এর মতো, কিন্তু কখনো `None` নয়: ড্রাইভার লোড না থাকলে `NoDBAPILoaded` এরর। |
| [`max_constraint_name_length`](#dialect-max-constraint-name-length) | অ্যাট্রিবিউট | কনস্ট্রেইন্টের নামের সর্বোচ্চ দৈর্ঘ্য (আলাদা না হলে `None`, তখন `max_identifier_length`)। |
| [`max_identifier_length`](#dialect-max-identifier-length) | অ্যাট্রিবিউট | নামের সর্বোচ্চ দৈর্ঘ্য: PostgreSQL ৬৩, MySQL ২৫৫, SQLite কার্যত সীমাহীন। |
| [`max_index_name_length`](#dialect-max-index-name-length) | অ্যাট্রিবিউট | ইনডেক্সের নামের সর্বোচ্চ দৈর্ঘ্য (আলাদা হলে)। |
| [`min_year_for_type()`](#dialect-min-year-for-type) | মেথড (internal) | (২.১) একটি তারিখ টাইপে ডেটাবেস সবচেয়ে পুরোনো কোন বছর নেয় (টেস্টের জন্য)। |
| [`minimum_dbapi_version`](#dialect-minimum-dbapi-version) | অ্যাট্রিবিউট (internal) | ড্রাইভারের সর্বনিম্ন প্রয়োজনীয় ভার্সন (নির্দিষ্ট না হলে `None`)। |
| [`name`](#dialect-name) | অ্যাট্রিবিউট | ডেটাবেসের নাম (`postgresql`, `sqlite`, `mysql`, `mariadb` …)। |
| [`normalize_name()`](#dialect-normalize-name) | মেথড (internal) | ডেটাবেসের বড় হাতের নাম (Oracle) ছোট হাতে বদলায় (reflection-এ); `denormalize_name()`-এর উল্টো। |
| [`on_connect()`](#dialect-on-connect) | মেথড | নতুন DB-API সংযোগ তৈরি হলে চালানোর ফাংশন দেয় (যেমন SQLite-এ PRAGMA, PostgreSQL-এ টাইপ নিবন্ধন), নইলে `None`। |
| [`on_connect_url()`](#dialect-on-connect-url) | মেথড (internal) | `on_connect()`-এর মতো, কিন্তু URL দেখে। |
| [`paramstyle`](#dialect-paramstyle) | অ্যাট্রিবিউট | প্যারামিটার লেখার ধরন: `qmark` (`?`), `format` (`%s`), `pyformat` (`%(name)s`), `named` (`:name`), `numeric_dollar` (`$1`)। |
| [`positional`](#dialect-positional) | অ্যাট্রিবিউট | paramstyle positional (`?`, `%s`) কি না। |
| [`preexecute_autoincrement_sequences`](#dialect-preexecute-autoincrement-sequences) | অ্যাট্রিবিউট (internal) | (সক্ষমতার পতাকা দেখুন) sequence-ভিত্তিক primary key INSERT-এর আগে আলাদা করে আনবে কি না। |
| [`preparer`](#dialect-preparer) | অ্যাট্রিবিউট (internal) | `IdentifierPreparer`-এর **ক্লাস** (অবজেক্টটি `identifier_preparer`)। |
| [`reflection_options`](#dialect-reflection-options) | অ্যাট্রিবিউট (internal) | `Table(..., autoload_with=...)`-এ বৈধ ডায়ালেক্ট-বিশেষ reflection অপশন (যেমন `postgresql_ignore_search_path`)। |
| [`requires_name_normalize`](#dialect-requires-name-normalize) | অ্যাট্রিবিউট (internal) | reflection-এ নাম ছোট হাতে বদলাতে হবে কি না (Oracle-এ `True`)। |
| [`reset_isolation_level()`](#dialect-reset-isolation-level) | মেথড | সংযোগের isolation level ডিফল্টে ফেরায় (পুলে ফেরত দেওয়ার সময়)। |
| [`retrieve_dbapi_version()`](#dialect-retrieve-dbapi-version) | মেথড (internal) | (ক্লাস মেথড) ড্রাইভার মডিউল থেকে তার ভার্সন পড়ে। |
| [`server_side_cursors`](#dialect-server-side-cursors) | অ্যাট্রিবিউট (internal) | (পুরোনো) সব কুয়েরিতে server-side cursor ব্যবহার; এখন `execution_options(stream_results=True)` দিন। |
| [`server_version_info`](#dialect-server-version-info) | অ্যাট্রিবিউট | সার্ভারের ভার্সন tuple (যেমন `(16, 4)`), প্রথম সংযোগের পর। |
| [`set_connection_execution_options()`](#dialect-set-connection-execution-options) | মেথড (internal) | `connection.execution_options(...)` দিলে ডায়ালেক্ট-বিশেষ অপশন (যেমন isolation_level) প্রয়োগ করে। |
| [`set_engine_execution_options()`](#dialect-set-engine-execution-options) | মেথড (internal) | `engine.execution_options(...)`-এর ক্ষেত্রে একই কাজ। |
| [`set_isolation_level()`](#dialect-set-isolation-level) | মেথড | সংযোগের isolation level বসায় (সাধারণত `create_engine(isolation_level=...)` বা `execution_options(isolation_level=...)` দিয়েই করুন)। |
| [`skip_autocommit_rollback`](#dialect-skip-autocommit-rollback) | অ্যাট্রিবিউট | (২.০.৪৩) `True` হলে AUTOCOMMIT মোডে সংযোগ পুলে ফেরত দেওয়ার সময় ROLLBACK পাঠায় না (কিছু ডেটাবেসে দ্রুততর)। |
| [`statement_compiler`](#dialect-statement-compiler) | অ্যাট্রিবিউট | SQL কম্পাইলার ক্লাস ([`SQLCompiler`](compiler.md#sqlcompiler)-এর subclass)। |
| [`supports_statement_cache`](#dialect-supports-statement-cache) | অ্যাট্রিবিউট | ডায়ালেক্ট SQL কম্পাইল-ক্যাশ সমর্থন করে কি না। |
| [`type_compiler`](#dialect-type-compiler) | অ্যাট্রিবিউট (legacy) | `type_compiler_instance`-এর পুরোনো নাম। |
| [`type_compiler_cls`](#dialect-type-compiler-cls) | অ্যাট্রিবিউট | টাইপ কম্পাইলার ক্লাস। |
| [`type_compiler_instance`](#dialect-type-compiler-instance) | অ্যাট্রিবিউট | টাইপ কম্পাইলার অবজেক্ট। |
| [`type_descriptor()`](#dialect-type-descriptor) | মেথড | একটি সাধারণ টাইপকে এই ডায়ালেক্টের বিশেষ টাইপে বদলায় (`colspecs` দেখে)। |
| [`use_insertmanyvalues`](#dialect-use-insertmanyvalues) | অ্যাট্রিবিউট | বাল্ক INSERT-এ "insertmanyvalues" (একটি স্টেটমেন্টে অনেক রো, RETURNING-সহ) ব্যবহার করবে কি না: ২.০-এর বড় গতি-উন্নতি। |
| [`use_insertmanyvalues_wo_returning`](#dialect-use-insertmanyvalues-wo-returning) | অ্যাট্রিবিউট (internal) | RETURNING ছাড়াও insertmanyvalues ব্যবহার করবে কি না। |
| [`validate_identifier()`](#dialect-validate-identifier) | মেথড (internal) | নামটি দৈর্ঘ্যসীমার মধ্যে কি না যাচাই করে, নইলে `IdentifierError`। |

/// details | সক্ষমতার পতাকা: ডেটাবেস/ড্রাইভার কী কী পারে (৩৫টি, দেখতে ক্লিক করুন)
    type: info

প্রতিটি পতাকা একটি `True`/`False` (কয়েকটি মেথড): ডেটাবেস বা ড্রাইভার একটি ফিচার পারে কি না, আর SQLAlchemy সেই অনুযায়ী SQL লেখে বা বিকল্প পথ নেয়। নামগুলোই অর্থ বলে দেয়:

* `supports_*`: যেমন `supports_alter` (ALTER TABLE), `supports_sequences`, `supports_native_boolean` / `_enum` / `_uuid` / `_decimal` (ডেটাবেসের নিজের টাইপ), `supports_identity_columns`, `supports_comments`, `supports_server_side_cursors`, `supports_sane_rowcount` (UPDATE/DELETE-এর পর `rowcount` বিশ্বাসযোগ্য), `supports_multivalues_insert` (`VALUES (...), (...)`), `supports_native_json_serialization` …
* `*_returning`: INSERT/UPDATE/DELETE-এ `RETURNING` চলে কি না (`_multifrom`: একাধিক টেবিলের UPDATE/DELETE-এ; `_executemany_returning`: অনেক রো-র সাথে)।
* বাকি: `cte_follows_insert` (CTE `INSERT`-এর পরে বসে), `div_is_floordiv` (`/` পূর্ণসংখ্যা ভাগ), `tuple_in_values` (`(a, b) IN (VALUES ...)` লিখতে হয়), `inline_comments` (কলামের comment `CREATE TABLE`-এর ভেতরে), `returns_native_bytes`, `sequences_optional`, `preexecute_autoincrement_sequences`, `favor_returning_over_lastrowid`।

নিজের কোডে ডেটাবেসভেদে আলাদা আচরণ লাগলে এগুলো দেখুন: `if engine.dialect.insert_returning: ...`।

**উদাহরণ:**

```python
flags = ["supports_alter", "supports_sequences", "supports_native_boolean", "supports_native_enum",
         "supports_native_uuid", "supports_identity_columns", "supports_comments", "insert_returning",
         "delete_returning_multifrom", "tuple_in_values"]
print(f"{'':28} pg    sqlite mysql")
for f in flags:
    print(f"{f:28} {getattr(pg, f)!s:5} {getattr(sl, f)!s:6} {getattr(my, f)!s}")
#                              pg    sqlite mysql
# supports_alter               True  False  True
# supports_sequences           True  False  False
# supports_native_boolean      True  False  False
# supports_native_enum         True  False  True
# supports_native_uuid         True  False  False
# supports_identity_columns    True  False  False
# supports_comments            True  False  True
# insert_returning             True  True   False
# delete_returning_multifrom   True  False  False
# tuple_in_values              False True   False
```

`cte_follows_insert` · `delete_executemany_returning` · `delete_returning` · `delete_returning_multifrom` · `div_is_floordiv` · `favor_returning_over_lastrowid` · `inline_comments` · `insert_executemany_returning` · `insert_executemany_returning_sort_by_parameter_order` · `insert_returning` · `returns_native_bytes` · `sequences_optional` · `supports_alter` · `supports_comments` · `supports_constraint_comments` · `supports_default_metavalue` · `supports_default_values` · `supports_empty_insert` · `supports_identity_columns` · `supports_multivalues_insert` · `supports_native_boolean` · `supports_native_decimal` · `supports_native_enum` · `supports_native_json_deserialization` · `supports_native_json_serialization` · `supports_native_uuid` · `supports_sane_multi_rowcount` · `supports_sane_rowcount` · `supports_sequences` · `supports_server_side_cursors` · `supports_simple_order_by_label` · `tuple_in_values` · `update_executemany_returning` · `update_returning` · `update_returning_multifrom`

///

/// details | reflection মেথড (Inspector এগুলোই ডাকে) (২৯টি, দেখতে ক্লিক করুন)
    type: info

ডেটাবেস থেকে টেবিল, কলাম, ইনডেক্স, কনস্ট্রেইন্ট ইত্যাদির তথ্য পড়ার নিচু-স্তরের মেথড। [`Inspector`](inspection.md#inspector)-এর একই নামের মেথড (`inspect(engine).get_columns("users")`) ভেতরে এগুলো ডাকে, ক্যাশসহ। পার্থক্য শুধু: প্রথম আর্গুমেন্ট একটি `Connection`। `get_multi_*` একসাথে অনেক টেবিলের তথ্য আনে (Inspector-এর `get_multi_*`-এর মতো), `has_*` "আছে কি না"। **নিজের কোডে `Inspector` ব্যবহার করুন**; এগুলো ডায়ালেক্ট লেখকদের জন্য।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print([c["name"] for c in d.get_columns(conn, "users")], d.has_table(conn, "users"))   # ['id', 'name'] True
```

`get_check_constraints()` · `get_columns()` · `get_foreign_keys()` · `get_indexes()` · `get_materialized_view_names()` · `get_multi_check_constraints()` · `get_multi_columns()` · `get_multi_foreign_keys()` · `get_multi_indexes()` · `get_multi_pk_constraint()` · `get_multi_table_comment()` · `get_multi_table_options()` · `get_multi_unique_constraints()` · `get_pk_constraint()` · `get_schema_names()` · `get_sequence_names()` · `get_table_comment()` · `get_table_names()` · `get_table_options()` · `get_temp_table_names()` · `get_temp_view_names()` · `get_unique_constraints()` · `get_view_definition()` · `get_view_names()` · `has_index()` · `has_multi_table()` · `has_schema()` · `has_sequence()` · `has_table()`

///

/// details | two-phase commit মেথড (৬টি, দেখতে ক্লিক করুন)
    type: info

দুই-ধাপের (distributed, XA) transaction: `do_begin_twophase` শুরু, `do_prepare_twophase` প্রস্তুত, `do_commit_twophase` / `do_rollback_twophase` শেষ, `do_recover_twophase` আটকে থাকা transaction খোঁজা, `create_xid` নতুন transaction id। `connection.begin_twophase()` এগুলো ডাকে। PostgreSQL (`PREPARE TRANSACTION`) আর MySQL (XA) সমর্থন করে; SQLite করে না।

**উদাহরণ:**

```python
print(isinstance(pg.create_xid(), str))   # True
```

`create_xid()` · `do_begin_twophase()` · `do_commit_twophase()` · `do_prepare_twophase()` · `do_recover_twophase()` · `do_rollback_twophase()`

///

### `Dialect.CACHE_HIT` { #dialect-CACHE-HIT }

**ধরন:** অ্যাট্রিবিউট

[`CacheStats`](#cachestats)-এর একটি মান: SQL কম্পাইল-ক্যাশে পাওয়া গেছে। লগে `[cached since 2.1s ago]` দেখায়।

**উদাহরণ:**

```python
print(Dialect.CACHE_HIT is CacheStats.CACHE_HIT)   # True
```

### `Dialect.CACHE_MISS` { #dialect-CACHE-MISS }

**ধরন:** অ্যাট্রিবিউট

ক্যাশে ছিল না, এবার কম্পাইল করে রাখা হলো (লগে `[generated in ...]`)।

**উদাহরণ:**

```python
print(Dialect.CACHE_MISS.name)   # CACHE_MISS
```

### `Dialect.CACHING_DISABLED` { #dialect-CACHING-DISABLED }

**ধরন:** অ্যাট্রিবিউট

ক্যাশ বন্ধ (`query_cache_size=0` বা `compiled_cache=None`)।

**উদাহরণ:**

```python
print(Dialect.CACHING_DISABLED.name)   # CACHING_DISABLED
```

### `Dialect.NO_CACHE_KEY` { #dialect-NO-CACHE-KEY }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের cache key বানানো যায়নি (যেমন `inherit_cache` ছাড়া কাস্টম কনস্ট্রাক্ট)।

**উদাহরণ:**

```python
print(Dialect.NO_CACHE_KEY.name)   # NO_CACHE_KEY
```

### `Dialect.NO_DIALECT_SUPPORT` { #dialect-NO-DIALECT-SUPPORT }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্টটি ক্যাশিং সমর্থন করে না (`supports_statement_cache = False`)।

**উদাহরণ:**

```python
print(Dialect.NO_DIALECT_SUPPORT.name)   # NO_DIALECT_SUPPORT
```

### `Dialect.aggregate_order_by_style` { #dialect-aggregate-order-by-style }

**ধরন:** অ্যাট্রিবিউট

(২.১) aggregate-এর ভেতরে ORDER BY কীভাবে লেখা হয়: [`AggregateOrderByStyle`](compiler.md#aggregateorderbystyle)।

**উদাহরণ:**

```python
print(pg.aggregate_order_by_style.name)   # INLINE
```

### `Dialect.bind_typing` { #dialect-bind-typing }

**ধরন:** অ্যাট্রিবিউট

bind প্যারামিটারের টাইপ ড্রাইভারকে কীভাবে জানানো হয়: [`BindTyping`](#bindtyping) (`NONE`, `SETINPUTSIZES`, `RENDER_CASTS`)।

**উদাহরণ:**

```python
print(pg.bind_typing.name, sl.bind_typing.name)   # RENDER_CASTS NONE
```

### `Dialect.colspecs` { #dialect-colspecs }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সাধারণ টাইপ → এই ডায়ালেক্টের বিশেষ টাইপ-ক্লাসের ম্যাপ (যেমন SQLite-এ `DateTime` → নিজের `DATETIME`)।

**উদাহরণ:**

```python
from sqlalchemy import DateTime
print(sl.colspecs[DateTime].__module__.split(".")[2])   # sqlite
```

### `Dialect.compiler_linting` { #dialect-compiler-linting }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় কোন [`Linting`](compiler.md#linting) পতাকা: `create_engine()`-এর ডিফল্টে `COLLECT_CARTESIAN_PRODUCTS` (সতর্কবার্তার অংশ `WARN_LINTING` চালানোর সময় যোগ হয়)।

**উদাহরণ:**

```python
print(int(d.compiler_linting))   # 1
```

### `Dialect.connect()` { #dialect-connect }

```python
Dialect.connect(*cargs, **cparams)
```

**ধরন:** মেথড

ড্রাইভার দিয়ে একটি নতুন DB-API সংযোগ খোলে (`dbapi.connect(*cargs, **cparams)`)। পুল এটি ডাকে; `do_connect` ইভেন্টে আর্গুমেন্ট বদলানো যায়।

**উদাহরণ:**

```python
raw = d.connect(":memory:")
print(type(raw).__module__)   # sqlite3
raw.close()
```

### `Dialect.construct_arguments` { #dialect-construct-arguments }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডায়ালেক্ট-বিশেষ কীওয়ার্ড (যেমন `Table(..., postgresql_partition_by=...)`) কোন কনস্ট্রাক্টে বৈধ তার তালিকা।

**উদাহরণ:**

```python
from sqlalchemy import Table as T
print(any(cls is T for cls, _ in pg.construct_arguments))   # True
```

### `Dialect.create_connect_args()` { #dialect-create-connect-args }

```python
Dialect.create_connect_args(url)
```

**ধরন:** মেথড

`URL` থেকে ড্রাইভারের `connect()`-এর আর্গুমেন্ট (`(args, kwargs)`) বানায়।

**উদাহরণ:**

```python
print(pg.create_connect_args(make_url("postgresql+psycopg://u:p@db:5433/shop")))
# ([], {'host': 'db', 'dbname': 'shop', 'user': 'u', 'password': 'p', 'port': 5433})
```

### `Dialect.dbapi` { #dialect-dbapi }

**ধরন:** অ্যাট্রিবিউট

লোড করা ড্রাইভার মডিউল (`sqlite3`, `psycopg` …); শুধু কম্পাইলের জন্য বানানো ডায়ালেক্টে `None`।

**উদাহরণ:**

```python
print(d.dbapi.__name__, pg.dbapi)   # sqlite3.dbapi2 None
```

### `Dialect.dbapi_exception_translation_map` { #dialect-dbapi-exception-translation-map }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ড্রাইভারের এরর-ক্লাসের নাম PEP 249-এর নামের সাথে না মিললে নাম-বদলের ম্যাপ।

**উদাহরণ:**

```python
print(d.dbapi_exception_translation_map)   # immutabledict({})
```

### `Dialect.dbapi_version` { #dialect-dbapi-version }

**ধরন:** প্রপার্টি

ড্রাইভারের ভার্সন (`VersionInfo`, tuple-এর মতো তুলনা চলে)।

**উদাহরণ:**

```python
print(type(d.dbapi_version).__name__, d.dbapi_version >= (2, 0))   # VersionInfo True
```

### `Dialect.ddl_compiler` { #dialect-ddl-compiler }

**ধরন:** অ্যাট্রিবিউট

DDL কম্পাইলার ক্লাস ([`DDLCompiler`](compiler.md#ddlcompiler)-এর subclass)।

**উদাহরণ:**

```python
print(pg.ddl_compiler.__name__)   # PGDDLCompiler
```

### `Dialect.default_isolation_level` { #dialect-default-isolation-level }

**ধরন:** অ্যাট্রিবিউট

সংযোগের সময় সার্ভারের ডিফল্ট isolation level (initialize-এর পরে পাওয়া যায়)।

**উদাহরণ:**

```python
with engine.connect():
    pass
print(d.default_isolation_level)   # SERIALIZABLE
```

### `Dialect.default_metavalue_token` { #dialect-default-metavalue-token }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডিফল্ট মান বোঝাতে INSERT-এ যে শব্দ বসে (`DEFAULT`)।

**উদাহরণ:**

```python
print(pg.default_metavalue_token)   # DEFAULT
```

### `Dialect.default_schema_name` { #dialect-default-schema-name }

**ধরন:** অ্যাট্রিবিউট

সংযোগের ডিফল্ট স্কিমা (PostgreSQL-এ সাধারণত `public`, SQLite-এ `main`), initialize-এর পরে।

**উদাহরণ:**

```python
print(d.default_schema_name)   # main
```

### `Dialect.default_sequence_base` { #dialect-default-sequence-base }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

Sequence-এর ডিফল্ট শুরুর মান।

**উদাহরণ:**

```python
print(pg.default_sequence_base)   # 1
```

### `Dialect.denormalize_name()` { #dialect-denormalize-name }

```python
Dialect.denormalize_name(name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ছোট হাতের নাম ডেটাবেসের নিজের ধরনে (বড় হাতে) বদলায়। ডিফল্ট বাস্তবায়ন সবসময় বড় হাতে করে, কিন্তু SQLAlchemy এটি ডাকে শুধু `requires_name_normalize=True` ডায়ালেক্টে (Oracle, Firebird)।

**উদাহরণ:**

```python
print(pg.denormalize_name("users"), pg.requires_name_normalize)   # USERS False
```

### `Dialect.detect_autocommit_setting()` { #dialect-detect-autocommit-setting }

```python
Dialect.detect_autocommit_setting(dbapi_conn)
```

**ধরন:** মেথড

একটি DB-API সংযোগে autocommit চালু কি না দেখে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(d.detect_autocommit_setting(conn.connection.dbapi_connection))   # False
```

### `Dialect.dialect_description` { #dialect-dialect-description }

**ধরন:** অ্যাট্রিবিউট

`name+driver` রূপের বর্ণনা।

**উদাহরণ:**

```python
print(pg.dialect_description, sl.dialect_description)   # postgresql+psycopg sqlite+pysqlite
```

### `Dialect.dialect_injects_custom_json_deserializer` { #dialect-dialect-injects-custom-json-deserializer }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডায়ালেক্ট নিজের JSON deserializer ড্রাইভারে বসায় কি না।

**উদাহরণ:**

```python
print(pg.dialect_injects_custom_json_deserializer)   # True
```

### `Dialect.do_begin()` { #dialect-do-begin }

```python
Dialect.do_begin(dbapi_connection)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

transaction শুরু (বেশিরভাগ ড্রাইভারে কিছুই করতে হয় না: DB-API নিজে থেকে শুরু করে)।

**উদাহরণ:**

```python
print(callable(d.do_begin))   # True
```

### `Dialect.do_close()` { #dialect-do-close }

```python
Dialect.do_close(dbapi_connection)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

DB-API সংযোগ বন্ধ করে (`connection.close()`)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); d.do_close(raw)
print("closed")   # closed
```

### `Dialect.do_commit()` { #dialect-do-commit }

```python
Dialect.do_commit(dbapi_connection)
```

**ধরন:** মেথড

`connection.commit()` চালায়।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); d.do_commit(raw); raw.close()
print("ok")   # ok
```

### `Dialect.do_execute()` { #dialect-do-execute }

```python
Dialect.do_execute(cursor, statement, parameters, context=None)
```

**ধরন:** মেথড

`cursor.execute(statement, parameters)` চালায়। `do_execute` ইভেন্টে এটি বদলানো যায়।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor()
d.do_execute(cur, "SELECT ? + 1", (41,), None)
print(cur.fetchone())   # (42,)
raw.close()
```

### `Dialect.do_execute_no_params()` { #dialect-do-execute-no-params }

```python
Dialect.do_execute_no_params(cursor, statement, context=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

প্যারামিটার ছাড়া `cursor.execute(statement)`।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor()
d.do_execute_no_params(cur, "SELECT 7", None)
print(cur.fetchone())   # (7,)
raw.close()
```

### `Dialect.do_executemany()` { #dialect-do-executemany }

```python
Dialect.do_executemany(cursor, statement, parameters, context=None)
```

**ধরন:** মেথড

`cursor.executemany(statement, parameters)` (অনেক রো একসাথে)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor()
cur.execute("CREATE TABLE t (x)")
d.do_executemany(cur, "INSERT INTO t VALUES (?)", [(1,), (2,)], None)
print(cur.execute("SELECT count(*) FROM t").fetchone())   # (2,)
raw.close()
```

### `Dialect.do_ping()` { #dialect-do-ping }

```python
Dialect.do_ping(dbapi_connection)
```

**ধরন:** মেথড

সংযোগ বেঁচে আছে কি না পরীক্ষা (`pool_pre_ping=True` এটি ব্যবহার করে)।

**উদাহরণ:**

```python
raw = d.connect(":memory:")
print(d.do_ping(raw))   # True
raw.close()
```

### `Dialect.do_release_savepoint()` { #dialect-do-release-savepoint }

```python
Dialect.do_release_savepoint(connection, name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`RELEASE SAVEPOINT <নাম>`।

**উদাহরণ:**

```python
print(callable(d.do_release_savepoint))   # True
```

### `Dialect.do_rollback()` { #dialect-do-rollback }

```python
Dialect.do_rollback(dbapi_connection)
```

**ধরন:** মেথড

`connection.rollback()`।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); d.do_rollback(raw); raw.close()
print("ok")   # ok
```

### `Dialect.do_rollback_to_savepoint()` { #dialect-do-rollback-to-savepoint }

```python
Dialect.do_rollback_to_savepoint(connection, name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`ROLLBACK TO SAVEPOINT <নাম>`।

**উদাহরণ:**

```python
print(callable(d.do_rollback_to_savepoint))   # True
```

### `Dialect.do_savepoint()` { #dialect-do-savepoint }

```python
Dialect.do_savepoint(connection, name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`SAVEPOINT <নাম>` (`begin_nested()` এটি ডাকে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    conn.begin(); d.do_savepoint(conn, "sp1"); d.do_release_savepoint(conn, "sp1")
    print("ok")   # ok
```

### `Dialect.do_set_input_sizes()` { #dialect-do-set-input-sizes }

```python
Dialect.do_set_input_sizes(cursor, list_of_tuples, context)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`cursor.setinputsizes()` ডাকে (`bind_typing = SETINPUTSIZES` এমন ড্রাইভারে, যেমন cx_Oracle)।

**উদাহরণ:**

```python
print(callable(d.do_set_input_sizes))   # True
```

### `Dialect.do_terminate()` { #dialect-do-terminate }

```python
Dialect.do_terminate(dbapi_connection)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সংযোগ জোর করে বন্ধ (অপেক্ষা না করে), যেমন async ড্রাইভারে cancel হলে।

**উদাহরণ:**

```python
print(callable(d.do_terminate))   # True
```

### `Dialect.driver` { #dialect-driver }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারের নাম।

**উদাহরণ:**

```python
print(pg.driver, my.driver, d.driver)   # psycopg mysqldb pysqlite
```

### `Dialect.engine_config_types` { #dialect-engine-config-types }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`engine_from_config()`-এ স্ট্রিং মানকে কোন টাইপে বদলাবে (`pool_timeout` → int …)।

**উদাহরণ:**

```python
print("pool_timeout" in pg.engine_config_types)   # True
```

### `Dialect.engine_created()` { #dialect-engine-created }

```python
Dialect.engine_created(engine)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) `create_engine()` engine বানানোর ঠিক আগে ডাকে; ডায়ালেক্ট নিজের ইভেন্ট বসাতে পারে।

**উদাহরণ:**

```python
print(callable(DefaultDialect.engine_created))   # True
```

### `Dialect.exclude_set_input_sizes` { #dialect-exclude-set-input-sizes }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

setinputsizes-এ যে DB-API টাইপগুলো বাদ যাবে।

**উদাহরণ:**

```python
print(pg.exclude_set_input_sizes)   # None
```

### `Dialect.execute_sequence_format` { #dialect-execute-sequence-format }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

positional প্যারামিটার কোন ধরনের sequence-এ পাঠাবে (`tuple` বা `list`)।

**উদাহরণ:**

```python
print(pg.execute_sequence_format.__name__)   # tuple
```

### `Dialect.execution_ctx_cls` { #dialect-execution-ctx-cls }

**ধরন:** অ্যাট্রিবিউট

execution context-এর ক্লাস ([`DefaultExecutionContext`](#defaultexecutioncontext)-এর subclass)।

**উদাহরণ:**

```python
print(issubclass(sl.execution_ctx_cls, DefaultExecutionContext))   # True
```

### `Dialect.get_async_dialect_cls()` { #dialect-get-async-dialect-cls }

```python
Dialect.get_async_dialect_cls(url)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) async engine-এর জন্য কোন ডায়ালেক্ট ক্লাস (সাধারণত `get_dialect_cls()`-এর মতো)।

**উদাহরণ:**

```python
print(sqlite.dialect.get_async_dialect_cls(make_url("sqlite://")).__name__)   # SQLiteDialect_pysqlite
```

### `Dialect.get_default_isolation_level()` { #dialect-get-default-isolation-level }

```python
Dialect.get_default_isolation_level(dbapi_conn)
```

**ধরন:** মেথড

সংযোগ থেকে ডিফল্ট isolation level পড়ে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(d.get_default_isolation_level(conn.connection.dbapi_connection))   # SERIALIZABLE
```

### `Dialect.get_dialect_cls()` { #dialect-get-dialect-cls }

```python
Dialect.get_dialect_cls(url)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) URL থেকে আসলে কোন ডায়ালেক্ট ক্লাস হবে (plugin/তৃতীয় পক্ষ বদলাতে পারে)।

**উদাহরণ:**

```python
print(sqlite.dialect.get_dialect_cls(make_url("sqlite://")).__name__)   # SQLiteDialect_pysqlite
```

### `Dialect.get_dialect_pool_class()` { #dialect-get-dialect-pool-class }

```python
Dialect.get_dialect_pool_class(url)
```

**ধরন:** মেথড

URL অনুযায়ী ডিফল্ট পুল ক্লাস (যেমন SQLite মেমোরিতে `SingletonThreadPool`, ফাইলে `QueuePool`)।

**উদাহরণ:**

```python
print(d.get_dialect_pool_class(make_url("sqlite://")).__name__, d.get_dialect_pool_class(make_url("sqlite:///a.db")).__name__)
# SingletonThreadPool QueuePool
```

### `Dialect.get_driver_connection()` { #dialect-get-driver-connection }

```python
Dialect.get_driver_connection(connection)
```

**ধরন:** মেথড

পুলের মোড়ক থেকে ড্রাইভারের আসল সংযোগ অবজেক্ট (async ড্রাইভারে আসল asyncpg সংযোগ)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(d.get_driver_connection(conn.connection.dbapi_connection)).__module__)   # sqlite3
```

### `Dialect.get_isolation_level()` { #dialect-get-isolation-level }

```python
Dialect.get_isolation_level(dbapi_connection)
```

**ধরন:** মেথড

সংযোগের বর্তমান isolation level।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(d.get_isolation_level(conn.connection.dbapi_connection))   # SERIALIZABLE
```

### `Dialect.get_isolation_level_values()` { #dialect-get-isolation-level-values }

```python
Dialect.get_isolation_level_values(dbapi_conn)
```

**ধরন:** মেথড

এই ডায়ালেক্টে বৈধ isolation level-এর নাম।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(d.get_isolation_level_values(conn.connection.dbapi_connection))   # ['READ UNCOMMITTED', 'SERIALIZABLE', 'AUTOCOMMIT']
```

### `Dialect.has_terminate` { #dialect-has-terminate }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`do_terminate()`-এর আলাদা বাস্তবায়ন আছে কি না।

**উদাহরণ:**

```python
print(sl.has_terminate)   # False
```

### `Dialect.identifier_preparer` { #dialect-identifier-preparer }

**ধরন:** অ্যাট্রিবিউট

নাম quote করার [`IdentifierPreparer`](compiler.md#identifierpreparer) অবজেক্ট।

**উদাহরণ:**

```python
print(pg.identifier_preparer.quote("order"), my.identifier_preparer.quote("order"))   # "order" `order`
```

### `Dialect.import_dbapi()` { #dialect-import-dbapi }

```python
Dialect.import_dbapi()
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) ড্রাইভার মডিউল ইমপোর্ট করে ফেরত দেয়। ড্রাইভার ইনস্টল না থাকলে এখানেই `ModuleNotFoundError`।

**উদাহরণ:**

```python
print(sqlite.dialect.import_dbapi().__name__)   # sqlite3
```

### `Dialect.include_set_input_sizes` { #dialect-include-set-input-sizes }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

setinputsizes-এ শুধু যে DB-API টাইপগুলো যাবে।

**উদাহরণ:**

```python
print(pg.include_set_input_sizes)   # None
```

### `Dialect.initialize()` { #dialect-initialize }

```python
Dialect.initialize(connection)
```

**ধরন:** মেথড

প্রথম সংযোগের সময় একবার চলে: সার্ভারের ভার্সন, ডিফল্ট স্কিমা, isolation level ইত্যাদি পড়ে পতাকা ঠিক করে।

**উদাহরণ:**

```python
fresh = create_engine("sqlite://")
print(fresh.dialect.server_version_info, end=" ")
with fresh.connect():
    pass
print(fresh.dialect.server_version_info is not None)   # None True
```

### `Dialect.insertmanyvalues_implicit_sentinel` { #dialect-insertmanyvalues-implicit-sentinel }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন primary key ধরনকে sentinel হিসেবে বিশ্বাস করে: [`InsertmanyvaluesSentinelOpts`](compiler.md#insertmanyvaluessentinelopts)।

**উদাহরণ:**

```python
print(int(pg.insertmanyvalues_implicit_sentinel) > 0)   # True
```

### `Dialect.insertmanyvalues_max_parameters` { #dialect-insertmanyvalues-max-parameters }

**ধরন:** অ্যাট্রিবিউট

insertmanyvalues-এ একটি স্টেটমেন্টে সর্বোচ্চ কত প্যারামিটার (এর বেশি হলে ভাগ করে চালায়)।

**উদাহরণ:**

```python
print(pg.insertmanyvalues_max_parameters)   # 32700
```

### `Dialect.insertmanyvalues_page_size` { #dialect-insertmanyvalues-page-size }

**ধরন:** অ্যাট্রিবিউট

insertmanyvalues-এ একটি স্টেটমেন্টে সর্বোচ্চ কত রো (`create_engine(insertmanyvalues_page_size=...)`)।

**উদাহরণ:**

```python
print(pg.insertmanyvalues_page_size)   # 1000
```

### `Dialect.is_async` { #dialect-is-async }

**ধরন:** অ্যাট্রিবিউট

async ড্রাইভার (asyncpg, aiosqlite …) কি না।

**উদাহরণ:**

```python
print(postgresql.asyncpg.dialect().is_async, pg.is_async)   # True False
```

### `Dialect.is_disconnect()` { #dialect-is-disconnect }

```python
Dialect.is_disconnect(e, connection, cursor)
```

**ধরন:** মেথড

একটি ড্রাইভার-এরর "সংযোগ কেটে গেছে" ধরনের কি না; `True` হলে SQLAlchemy সংযোগ বাতিল করে (`connection_invalidated`)।

**উদাহরণ:**

```python
import sqlite3
print(d.is_disconnect(sqlite3.ProgrammingError("Cannot operate on a closed database."), None, None))   # True
```

### `Dialect.label_length` { #dialect-label-length }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`create_engine(label_length=...)` দিলে স্বয়ংক্রিয় label-এর দৈর্ঘ্যসীমা, নইলে `None`।

**উদাহরণ:**

```python
print(pg.label_length)   # None
```

### `Dialect.load_provisioning()` { #dialect-load-provisioning }

```python
Dialect.load_provisioning()
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) SQLAlchemy-র টেস্ট-স্যুটের জন্য ডায়ালেক্টের provision মডিউল লোড করে।

**উদাহরণ:**

```python
print(callable(DefaultDialect.load_provisioning))   # True
```

### `Dialect.loaded_dbapi` { #dialect-loaded-dbapi }

**ধরন:** প্রপার্টি

`dbapi`-এর মতো, কিন্তু কখনো `None` নয়: ড্রাইভার লোড না থাকলে `NoDBAPILoaded` এরর।

**উদাহরণ:**

```python
print(d.loaded_dbapi.__name__)   # sqlite3
try:
    pg.loaded_dbapi
except exc.NoDBAPILoaded:
    print("ড্রাইভার লোড হয়নি")   # ড্রাইভার লোড হয়নি
```

### `Dialect.max_constraint_name_length` { #dialect-max-constraint-name-length }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রেইন্টের নামের সর্বোচ্চ দৈর্ঘ্য (আলাদা না হলে `None`, তখন `max_identifier_length`)।

**উদাহরণ:**

```python
print(my.max_constraint_name_length, pg.max_constraint_name_length)   # 64 None
```

### `Dialect.max_identifier_length` { #dialect-max-identifier-length }

**ধরন:** অ্যাট্রিবিউট

নামের সর্বোচ্চ দৈর্ঘ্য: PostgreSQL ৬৩, MySQL ২৫৫, SQLite কার্যত সীমাহীন। এর বেশি হলে স্বয়ংক্রিয় নাম ছোট হয়, নিজে দেওয়া হলে `IdentifierError`।

**উদাহরণ:**

```python
print(pg.max_identifier_length, my.max_identifier_length, sl.max_identifier_length)   # 63 255 9999
```

### `Dialect.max_index_name_length` { #dialect-max-index-name-length }

**ধরন:** অ্যাট্রিবিউট

ইনডেক্সের নামের সর্বোচ্চ দৈর্ঘ্য (আলাদা হলে)।

**উদাহরণ:**

```python
print(my.max_index_name_length)   # 64
```

### `Dialect.min_year_for_type()` { #dialect-min-year-for-type }

```python
Dialect.min_year_for_type(typeobj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(২.১) একটি তারিখ টাইপে ডেটাবেস সবচেয়ে পুরোনো কোন বছর নেয় (টেস্টের জন্য)।

**উদাহরণ:**

```python
print(pg.min_year_for_type(Date()))   # 1
```

### `Dialect.minimum_dbapi_version` { #dialect-minimum-dbapi-version }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ড্রাইভারের সর্বনিম্ন প্রয়োজনীয় ভার্সন (নির্দিষ্ট না হলে `None`)।

**উদাহরণ:**

```python
print(sl.minimum_dbapi_version)   # None
```

### `Dialect.name` { #dialect-name }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেসের নাম (`postgresql`, `sqlite`, `mysql`, `mariadb` …)। ডেটাবেসভেদে কোড আলাদা করতে: `if engine.dialect.name == "postgresql": ...`।

**উদাহরণ:**

```python
print(pg.name, sl.name, my.name)   # postgresql sqlite mysql
```

### `Dialect.normalize_name()` { #dialect-normalize-name }

```python
Dialect.normalize_name(name)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডেটাবেসের বড় হাতের নাম (Oracle) ছোট হাতে বদলায় (reflection-এ); `denormalize_name()`-এর উল্টো।

**উদাহরণ:**

```python
print(pg.normalize_name("USERS"))   # users
```

### `Dialect.on_connect()` { #dialect-on-connect }

```python
Dialect.on_connect()
```

**ধরন:** মেথড

নতুন DB-API সংযোগ তৈরি হলে চালানোর ফাংশন দেয় (যেমন SQLite-এ PRAGMA, PostgreSQL-এ টাইপ নিবন্ধন), নইলে `None`।

**উদাহরণ:**

```python
print(callable(d.on_connect()))   # True
```

### `Dialect.on_connect_url()` { #dialect-on-connect-url }

```python
Dialect.on_connect_url(url)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`on_connect()`-এর মতো, কিন্তু URL দেখে।

**উদাহরণ:**

```python
print(callable(d.on_connect_url(make_url("sqlite://"))))   # True
```

### `Dialect.paramstyle` { #dialect-paramstyle }

**ধরন:** অ্যাট্রিবিউট

প্যারামিটার লেখার ধরন: `qmark` (`?`), `format` (`%s`), `pyformat` (`%(name)s`), `named` (`:name`), `numeric_dollar` (`$1`)। `create_engine(paramstyle=...)` দিয়ে বদলানো যায়।

**উদাহরণ:**

```python
print(pg.paramstyle, sl.paramstyle, my.paramstyle)   # pyformat qmark format
```

### `Dialect.positional` { #dialect-positional }

**ধরন:** অ্যাট্রিবিউট

paramstyle positional (`?`, `%s`) কি না।

**উদাহরণ:**

```python
print(pg.positional, sl.positional)   # False True
```

### `Dialect.preexecute_autoincrement_sequences` { #dialect-preexecute-autoincrement-sequences }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(সক্ষমতার পতাকা দেখুন) sequence-ভিত্তিক primary key INSERT-এর আগে আলাদা করে আনবে কি না।

**উদাহরণ:**

```python
print(pg.preexecute_autoincrement_sequences)   # True
```

### `Dialect.preparer` { #dialect-preparer }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`IdentifierPreparer`-এর **ক্লাস** (অবজেক্টটি `identifier_preparer`)।

**উদাহরণ:**

```python
print(issubclass(pg.preparer, type(pg.identifier_preparer)) or pg.preparer is type(pg.identifier_preparer))   # True
```

### `Dialect.reflection_options` { #dialect-reflection-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Table(..., autoload_with=...)`-এ বৈধ ডায়ালেক্ট-বিশেষ reflection অপশন (যেমন `postgresql_ignore_search_path`)।

**উদাহরণ:**

```python
print(pg.reflection_options)   # ('postgresql_ignore_search_path',)
```

### `Dialect.requires_name_normalize` { #dialect-requires-name-normalize }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

reflection-এ নাম ছোট হাতে বদলাতে হবে কি না (Oracle-এ `True`)।

**উদাহরণ:**

```python
print(pg.requires_name_normalize)   # False
```

### `Dialect.reset_isolation_level()` { #dialect-reset-isolation-level }

```python
Dialect.reset_isolation_level(dbapi_connection)
```

**ধরন:** মেথড

সংযোগের isolation level ডিফল্টে ফেরায় (পুলে ফেরত দেওয়ার সময়)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    raw = conn.connection.dbapi_connection
    d.set_isolation_level(raw, "READ UNCOMMITTED"); d.reset_isolation_level(raw)
    print(d.get_isolation_level(raw))   # SERIALIZABLE
```

### `Dialect.retrieve_dbapi_version()` { #dialect-retrieve-dbapi-version }

```python
Dialect.retrieve_dbapi_version(dbapi)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) ড্রাইভার মডিউল থেকে তার ভার্সন পড়ে।

**উদাহরণ:**

```python
import sqlite3
print(type(d.retrieve_dbapi_version(sqlite3)).__name__)   # VersionInfo
```

### `Dialect.server_side_cursors` { #dialect-server-side-cursors }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(পুরোনো) সব কুয়েরিতে server-side cursor ব্যবহার; এখন `execution_options(stream_results=True)` দিন।

**উদাহরণ:**

```python
print(pg.server_side_cursors)   # False
```

### `Dialect.server_version_info` { #dialect-server-version-info }

**ধরন:** অ্যাট্রিবিউট

সার্ভারের ভার্সন tuple (যেমন `(16, 4)`), প্রথম সংযোগের পর। ভার্সনভেদে ফিচার বেছে নিতে।

**উদাহরণ:**

```python
print(d.server_version_info >= (3, 24))   # True  (SQLite ৩.২৪+ → upsert চলে)
```

### `Dialect.set_connection_execution_options()` { #dialect-set-connection-execution-options }

```python
Dialect.set_connection_execution_options(connection, opts)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`connection.execution_options(...)` দিলে ডায়ালেক্ট-বিশেষ অপশন (যেমন isolation_level) প্রয়োগ করে।

**উদাহরণ:**

```python
print(callable(d.set_connection_execution_options))   # True
```

### `Dialect.set_engine_execution_options()` { #dialect-set-engine-execution-options }

```python
Dialect.set_engine_execution_options(engine, opts)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`engine.execution_options(...)`-এর ক্ষেত্রে একই কাজ।

**উদাহরণ:**

```python
print(callable(d.set_engine_execution_options))   # True
```

### `Dialect.set_isolation_level()` { #dialect-set-isolation-level }

```python
Dialect.set_isolation_level(dbapi_connection, level)
```

**ধরন:** মেথড

সংযোগের isolation level বসায় (সাধারণত `create_engine(isolation_level=...)` বা `execution_options(isolation_level=...)` দিয়েই করুন)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    raw = conn.connection.dbapi_connection
    d.set_isolation_level(raw, "READ UNCOMMITTED")
    print(d.get_isolation_level(raw))   # READ UNCOMMITTED
    d.reset_isolation_level(raw)
```

### `Dialect.skip_autocommit_rollback` { #dialect-skip-autocommit-rollback }

**ধরন:** অ্যাট্রিবিউট

(২.০.৪৩) `True` হলে AUTOCOMMIT মোডে সংযোগ পুলে ফেরত দেওয়ার সময় ROLLBACK পাঠায় না (কিছু ডেটাবেসে দ্রুততর)। `create_engine(skip_autocommit_rollback=True)`।

**উদাহরণ:**

```python
print(pg.skip_autocommit_rollback)   # False
```

### `Dialect.statement_compiler` { #dialect-statement-compiler }

**ধরন:** অ্যাট্রিবিউট

SQL কম্পাইলার ক্লাস ([`SQLCompiler`](compiler.md#sqlcompiler)-এর subclass)।

**উদাহরণ:**

```python
print(pg.statement_compiler.__name__)   # PGCompiler_psycopg
```

### `Dialect.supports_statement_cache` { #dialect-supports-statement-cache }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্ট SQL কম্পাইল-ক্যাশ সমর্থন করে কি না। তৃতীয় পক্ষের ডায়ালেক্টে এটি `True` না থাকলে ক্যাশ বন্ধ থাকে আর সতর্কবার্তা আসে।

**উদাহরণ:**

```python
print(pg.supports_statement_cache)   # True
```

### `Dialect.type_compiler` { #dialect-type-compiler }

**ধরন:** অ্যাট্রিবিউট

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`type_compiler_instance`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(pg.type_compiler is pg.type_compiler_instance)   # True
```

### `Dialect.type_compiler_cls` { #dialect-type-compiler-cls }

**ধরন:** অ্যাট্রিবিউট

টাইপ কম্পাইলার ক্লাস।

**উদাহরণ:**

```python
print(pg.type_compiler_cls.__name__)   # PGTypeCompiler
```

### `Dialect.type_compiler_instance` { #dialect-type-compiler-instance }

**ধরন:** অ্যাট্রিবিউট

টাইপ কম্পাইলার অবজেক্ট।

**উদাহরণ:**

```python
print(pg.type_compiler_instance.process(String(10)))   # VARCHAR(10)
```

### `Dialect.type_descriptor()` { #dialect-type-descriptor }

```python
Dialect.type_descriptor(typeobj)
```

**ধরন:** মেথড

একটি সাধারণ টাইপকে এই ডায়ালেক্টের বিশেষ টাইপে বদলায় (`colspecs` দেখে)।

**উদাহরণ:**

```python
from sqlalchemy import DateTime
print(type(sl.type_descriptor(DateTime())).__module__.split(".")[2])   # sqlite
```

### `Dialect.use_insertmanyvalues` { #dialect-use-insertmanyvalues }

**ধরন:** অ্যাট্রিবিউট

বাল্ক INSERT-এ "insertmanyvalues" (একটি স্টেটমেন্টে অনেক রো, RETURNING-সহ) ব্যবহার করবে কি না: ২.০-এর বড় গতি-উন্নতি।

**উদাহরণ:**

```python
print(pg.use_insertmanyvalues)   # True
```

### `Dialect.use_insertmanyvalues_wo_returning` { #dialect-use-insertmanyvalues-wo-returning }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

RETURNING ছাড়াও insertmanyvalues ব্যবহার করবে কি না।

**উদাহরণ:**

```python
print(pg.use_insertmanyvalues_wo_returning)   # False
```

### `Dialect.validate_identifier()` { #dialect-validate-identifier }

```python
Dialect.validate_identifier(ident)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নামটি দৈর্ঘ্যসীমার মধ্যে কি না যাচাই করে, নইলে `IdentifierError`।

**উদাহরণ:**

```python
try:
    pg.validate_identifier("x" * 70)
except exc.IdentifierError:
    print("খুব লম্বা")   # খুব লম্বা
```

## `DefaultDialect` { #defaultdialect }

```python
from sqlalchemy.engine.default import DefaultDialect
```

`Dialect` ইন্টারফেসের ডিফল্ট বাস্তবায়ন: সব ডায়ালেক্ট এর subclass। নিজের ডায়ালেক্ট লিখতে (বা শুধু SQL কম্পাইল দেখতে) এটি থেকে শুরু করুন। ডায়ালেক্ট ছাড়া `str(stmt)` আসলে `DefaultDialect`-এর একটি রূপ ব্যবহার করে। কনস্ট্রাক্টরের প্যারামিটার `create_engine()`-এর একই নামের অপশন থেকে আসে।

**উদাহরণ:**

```python
dd = DefaultDialect(paramstyle="named")
print(dd.name, select(users.c.id).where(users.c.id == 1).compile(dialect=dd).string.splitlines()[-1])   # default WHERE users.id = :id_1
print(isinstance(d, DefaultDialect))   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #defaultdialect-params }

```python
DefaultDialect(paramstyle=None, isolation_level=None, dbapi=None, implicit_returning=True, supports_native_boolean=None, max_identifier_length=None, label_length=None, insertmanyvalues_page_size=_NoArg.NO_ARG, use_insertmanyvalues=None, compiler_linting=0, server_side_cursors=False, skip_autocommit_rollback=False, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `paramstyle` | প্যারামিটার লেখার ধরন (ডিফল্ট: ড্রাইভারের `paramstyle`)। |
| `isolation_level` | সব সংযোগের isolation level। |
| `dbapi` | ড্রাইভার মডিউল। |
| `implicit_returning` | সবসময় `True` (২.০ থেকে বদলানো যায় না)। |
| `supports_native_boolean` | native BOOLEAN ব্যবহার করবে কি না (বাধ্য করতে)। |
| `max_identifier_length` | নামের দৈর্ঘ্যসীমা বদলাতে। |
| `label_length` | স্বয়ংক্রিয় label-এর দৈর্ঘ্যসীমা। |
| `insertmanyvalues_page_size` | insertmanyvalues-এর ব্যাচের আকার। |
| `use_insertmanyvalues` | insertmanyvalues চালু/বন্ধ। |
| `compiler_linting` | SQL linting-এর পছন্দ। |
| `server_side_cursors` | (পুরোনো) সব কুয়েরিতে server-side cursor। |
| `skip_autocommit_rollback` | AUTOCOMMIT-এ পুলে ফেরার সময় ROLLBACK বাদ। |
| `kwargs` | বাকি অপশন (ডায়ালেক্ট-বিশেষ)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #defaultdialect-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`connection_characteristics`](#defaultdialect-connection-characteristics) | অ্যাট্রিবিউট (internal) | সংযোগ-স্তরের যে বৈশিষ্ট্যগুলো (`isolation_level`, `logging_token` …) execution option দিয়ে বসানো আর পুলে ফেরার সময় ফেরানো যায়। |
| [`default_paramstyle`](#defaultdialect-default-paramstyle) | অ্যাট্রিবিউট (internal) | ড্রাইভার নির্দিষ্ট না করলে ডিফল্ট paramstyle। |
| [`full_returning`](#defaultdialect-full-returning) | প্রপার্টি ⚠️ deprecated | (২.০ থেকে বাতিলের পথে) INSERT/UPDATE/DELETE সবগুলোতে RETURNING চলে কি না; বদলে `insert_returning`, `update_returning`, `delete_returning` আলাদাভাবে দেখুন। |
| [`get_pool_class()`](#defaultdialect-get-pool-class) | ক্লাস মেথড (internal) | (ক্লাস মেথড) URL-এর জন্য পুল ক্লাস (`get_dialect_pool_class()` ভেতরে এটি ডাকে)। |
| [`insert_null_pk_still_autoincrements`](#defaultdialect-insert-null-pk-still-autoincrements) | অ্যাট্রিবিউট (internal) | primary key-এ `NULL` দিলেও ডেটাবেস নিজে মান বসায় কি না (SQLite-এ `True`)। |
| [`isolation_level`](#defaultdialect-isolation-level) | অ্যাট্রিবিউট | শ্রেণি-স্তরের পুরোনো অ্যাট্রিবিউট, **সবসময় `None`**। |
| [`non_native_boolean_check_constraint`](#defaultdialect-non-native-boolean-check-constraint) | অ্যাট্রিবিউট (internal) | native BOOLEAN নেই এমন ডেটাবেসে `Boolean(create_constraint=True)` দিলে `CHECK (x IN (0, 1))` বসাবে কি না। |
| [`postfetch_lastrowid`](#defaultdialect-postfetch-lastrowid) | অ্যাট্রিবিউট (internal) | INSERT-এর পর `cursor.lastrowid` থেকে primary key আনে কি না (RETURNING না থাকলে)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DefaultDialect`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Dialect` থেকে:** [`CACHE_HIT`](#dialect-CACHE-HIT) · [`CACHE_MISS`](#dialect-CACHE-MISS) · [`CACHING_DISABLED`](#dialect-CACHING-DISABLED) · [`NO_CACHE_KEY`](#dialect-NO-CACHE-KEY) · [`NO_DIALECT_SUPPORT`](#dialect-NO-DIALECT-SUPPORT) · [`aggregate_order_by_style`](#dialect-aggregate-order-by-style) · [`bind_typing`](#dialect-bind-typing) · [`colspecs`](#dialect-colspecs) · [`compiler_linting`](#dialect-compiler-linting) · [`connect()`](#dialect-connect) · [`construct_arguments`](#dialect-construct-arguments) · [`create_connect_args()`](#dialect-create-connect-args) · [`dbapi`](#dialect-dbapi) · [`dbapi_exception_translation_map`](#dialect-dbapi-exception-translation-map) · [`dbapi_version`](#dialect-dbapi-version) · [`ddl_compiler`](#dialect-ddl-compiler) · [`default_metavalue_token`](#dialect-default-metavalue-token) · [`default_schema_name`](#dialect-default-schema-name) · [`default_sequence_base`](#dialect-default-sequence-base) · [`denormalize_name()`](#dialect-denormalize-name) · [`detect_autocommit_setting()`](#dialect-detect-autocommit-setting) · [`dialect_description`](#dialect-dialect-description) · [`dialect_injects_custom_json_deserializer`](#dialect-dialect-injects-custom-json-deserializer) · [`do_begin()`](#dialect-do-begin) · [`do_close()`](#dialect-do-close) · [`do_commit()`](#dialect-do-commit) · [`do_execute()`](#dialect-do-execute) · [`do_execute_no_params()`](#dialect-do-execute-no-params) · [`do_executemany()`](#dialect-do-executemany) · [`do_ping()`](#dialect-do-ping) · [`do_release_savepoint()`](#dialect-do-release-savepoint) · [`do_rollback()`](#dialect-do-rollback) · [`do_rollback_to_savepoint()`](#dialect-do-rollback-to-savepoint) · [`do_savepoint()`](#dialect-do-savepoint) · [`do_set_input_sizes()`](#dialect-do-set-input-sizes) · [`do_terminate()`](#dialect-do-terminate) · [`driver`](#dialect-driver) · [`engine_config_types`](#dialect-engine-config-types) · [`engine_created()`](#dialect-engine-created) · [`exclude_set_input_sizes`](#dialect-exclude-set-input-sizes) · [`execute_sequence_format`](#dialect-execute-sequence-format) · [`execution_ctx_cls`](#dialect-execution-ctx-cls) · [`get_async_dialect_cls()`](#dialect-get-async-dialect-cls) · [`get_default_isolation_level()`](#dialect-get-default-isolation-level) · [`get_dialect_cls()`](#dialect-get-dialect-cls) · [`get_dialect_pool_class()`](#dialect-get-dialect-pool-class) · [`get_driver_connection()`](#dialect-get-driver-connection) · [`get_isolation_level()`](#dialect-get-isolation-level) · [`get_isolation_level_values()`](#dialect-get-isolation-level-values) · [`has_terminate`](#dialect-has-terminate) · [`identifier_preparer`](#dialect-identifier-preparer) · [`import_dbapi()`](#dialect-import-dbapi) · [`include_set_input_sizes`](#dialect-include-set-input-sizes) · [`initialize()`](#dialect-initialize) · [`insertmanyvalues_implicit_sentinel`](#dialect-insertmanyvalues-implicit-sentinel) · [`insertmanyvalues_max_parameters`](#dialect-insertmanyvalues-max-parameters) · [`insertmanyvalues_page_size`](#dialect-insertmanyvalues-page-size) · [`is_async`](#dialect-is-async) · [`is_disconnect()`](#dialect-is-disconnect) · [`load_provisioning()`](#dialect-load-provisioning) · [`loaded_dbapi`](#dialect-loaded-dbapi) · [`max_constraint_name_length`](#dialect-max-constraint-name-length) · [`max_identifier_length`](#dialect-max-identifier-length) · [`max_index_name_length`](#dialect-max-index-name-length) · [`min_year_for_type()`](#dialect-min-year-for-type) · [`minimum_dbapi_version`](#dialect-minimum-dbapi-version) · [`name`](#dialect-name) · [`normalize_name()`](#dialect-normalize-name) · [`on_connect()`](#dialect-on-connect) · [`on_connect_url()`](#dialect-on-connect-url) · [`paramstyle`](#dialect-paramstyle) · [`positional`](#dialect-positional) · [`preexecute_autoincrement_sequences`](#dialect-preexecute-autoincrement-sequences) · [`preparer`](#dialect-preparer) · [`reflection_options`](#dialect-reflection-options) · [`requires_name_normalize`](#dialect-requires-name-normalize) · [`reset_isolation_level()`](#dialect-reset-isolation-level) · [`retrieve_dbapi_version()`](#dialect-retrieve-dbapi-version) · [`server_side_cursors`](#dialect-server-side-cursors) · [`server_version_info`](#dialect-server-version-info) · [`set_connection_execution_options()`](#dialect-set-connection-execution-options) · [`set_engine_execution_options()`](#dialect-set-engine-execution-options) · [`set_isolation_level()`](#dialect-set-isolation-level) · [`statement_compiler`](#dialect-statement-compiler) · [`supports_statement_cache`](#dialect-supports-statement-cache) · [`type_compiler_cls`](#dialect-type-compiler-cls) · [`type_compiler_instance`](#dialect-type-compiler-instance) · [`type_descriptor()`](#dialect-type-descriptor) · [`use_insertmanyvalues`](#dialect-use-insertmanyvalues) · [`use_insertmanyvalues_wo_returning`](#dialect-use-insertmanyvalues-wo-returning) · [`validate_identifier()`](#dialect-validate-identifier)

///

/// details | সক্ষমতার পতাকা: ডেটাবেস/ড্রাইভার কী কী পারে (৪০টি, দেখতে ক্লিক করুন)
    type: info

প্রতিটি পতাকা একটি `True`/`False` (কয়েকটি মেথড): ডেটাবেস বা ড্রাইভার একটি ফিচার পারে কি না, আর SQLAlchemy সেই অনুযায়ী SQL লেখে বা বিকল্প পথ নেয়। নামগুলোই অর্থ বলে দেয়:

* `supports_*`: যেমন `supports_alter` (ALTER TABLE), `supports_sequences`, `supports_native_boolean` / `_enum` / `_uuid` / `_decimal` (ডেটাবেসের নিজের টাইপ), `supports_identity_columns`, `supports_comments`, `supports_server_side_cursors`, `supports_sane_rowcount` (UPDATE/DELETE-এর পর `rowcount` বিশ্বাসযোগ্য), `supports_multivalues_insert` (`VALUES (...), (...)`), `supports_native_json_serialization` …
* `*_returning`: INSERT/UPDATE/DELETE-এ `RETURNING` চলে কি না (`_multifrom`: একাধিক টেবিলের UPDATE/DELETE-এ; `_executemany_returning`: অনেক রো-র সাথে)।
* বাকি: `cte_follows_insert` (CTE `INSERT`-এর পরে বসে), `div_is_floordiv` (`/` পূর্ণসংখ্যা ভাগ), `tuple_in_values` (`(a, b) IN (VALUES ...)` লিখতে হয়), `inline_comments` (কলামের comment `CREATE TABLE`-এর ভেতরে), `returns_native_bytes`, `sequences_optional`, `preexecute_autoincrement_sequences`, `favor_returning_over_lastrowid`।

নিজের কোডে ডেটাবেসভেদে আলাদা আচরণ লাগলে এগুলো দেখুন: `if engine.dialect.insert_returning: ...`।

**উদাহরণ:**

```python
flags = ["supports_alter", "supports_sequences", "supports_native_boolean", "supports_native_enum",
         "supports_native_uuid", "supports_identity_columns", "supports_comments", "insert_returning",
         "delete_returning_multifrom", "tuple_in_values"]
print(f"{'':28} pg    sqlite mysql")
for f in flags:
    print(f"{f:28} {getattr(pg, f)!s:5} {getattr(sl, f)!s:6} {getattr(my, f)!s}")
#                              pg    sqlite mysql
# supports_alter               True  False  True
# supports_sequences           True  False  False
# supports_native_boolean      True  False  False
# supports_native_enum         True  False  True
# supports_native_uuid         True  False  False
# supports_identity_columns    True  False  False
# supports_comments            True  False  True
# insert_returning             True  True   False
# delete_returning_multifrom   True  False  False
# tuple_in_values              False True   False
```

`cte_follows_insert` · `delete_executemany_returning` · `delete_returning` · `delete_returning_multifrom` · `div_is_floordiv` · `favor_returning_over_lastrowid` · `inline_comments` · `insert_executemany_returning` · `insert_executemany_returning_sort_by_parameter_order` · `insert_returning` · `returns_native_bytes` · `sequences_optional` · `supports_alter` · `supports_comments` · `supports_constraint_comments` · `supports_default_metavalue` · `supports_default_values` · `supports_empty_insert` · `supports_for_update_of` · `supports_identity_columns` · `supports_is_distinct_from` · `supports_multivalues_insert` · `supports_native_boolean` · `supports_native_decimal` · `supports_native_enum` · `supports_native_json_deserialization` · `supports_native_json_serialization` · `supports_native_uuid` · `supports_sane_multi_rowcount` · `supports_sane_rowcount` · `supports_sane_rowcount_returning` · `supports_schemas` · `supports_sequences` · `supports_server_side_cursors` · `supports_simple_order_by_label` · `supports_views` · `tuple_in_values` · `update_executemany_returning` · `update_returning` · `update_returning_multifrom`

///

/// details | reflection মেথড (Inspector এগুলোই ডাকে) (২৯টি, দেখতে ক্লিক করুন)
    type: info

ডেটাবেস থেকে টেবিল, কলাম, ইনডেক্স, কনস্ট্রেইন্ট ইত্যাদির তথ্য পড়ার নিচু-স্তরের মেথড। [`Inspector`](inspection.md#inspector)-এর একই নামের মেথড (`inspect(engine).get_columns("users")`) ভেতরে এগুলো ডাকে, ক্যাশসহ। পার্থক্য শুধু: প্রথম আর্গুমেন্ট একটি `Connection`। `get_multi_*` একসাথে অনেক টেবিলের তথ্য আনে (Inspector-এর `get_multi_*`-এর মতো), `has_*` "আছে কি না"। **নিজের কোডে `Inspector` ব্যবহার করুন**; এগুলো ডায়ালেক্ট লেখকদের জন্য।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print([c["name"] for c in d.get_columns(conn, "users")], d.has_table(conn, "users"))   # ['id', 'name'] True
```

`get_check_constraints()` · `get_columns()` · `get_foreign_keys()` · `get_indexes()` · `get_materialized_view_names()` · `get_multi_check_constraints()` · `get_multi_columns()` · `get_multi_foreign_keys()` · `get_multi_indexes()` · `get_multi_pk_constraint()` · `get_multi_table_comment()` · `get_multi_table_options()` · `get_multi_unique_constraints()` · `get_pk_constraint()` · `get_schema_names()` · `get_sequence_names()` · `get_table_comment()` · `get_table_names()` · `get_table_options()` · `get_temp_table_names()` · `get_temp_view_names()` · `get_unique_constraints()` · `get_view_definition()` · `get_view_names()` · `has_index()` · `has_multi_table()` · `has_schema()` · `has_sequence()` · `has_table()`

///

/// details | two-phase commit মেথড (৬টি, দেখতে ক্লিক করুন)
    type: info

দুই-ধাপের (distributed, XA) transaction: `do_begin_twophase` শুরু, `do_prepare_twophase` প্রস্তুত, `do_commit_twophase` / `do_rollback_twophase` শেষ, `do_recover_twophase` আটকে থাকা transaction খোঁজা, `create_xid` নতুন transaction id। `connection.begin_twophase()` এগুলো ডাকে। PostgreSQL (`PREPARE TRANSACTION`) আর MySQL (XA) সমর্থন করে; SQLite করে না।

**উদাহরণ:**

```python
print(isinstance(pg.create_xid(), str))   # True
```

`create_xid()` · `do_begin_twophase()` · `do_commit_twophase()` · `do_prepare_twophase()` · `do_recover_twophase()` · `do_rollback_twophase()`

///

### `DefaultDialect.connection_characteristics` { #defaultdialect-connection-characteristics }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সংযোগ-স্তরের যে বৈশিষ্ট্যগুলো (`isolation_level`, `logging_token` …) execution option দিয়ে বসানো আর পুলে ফেরার সময় ফেরানো যায়।

**উদাহরণ:**

```python
print(sorted(DefaultDialect.connection_characteristics))   # ['isolation_level', 'logging_token']
```

### `DefaultDialect.default_paramstyle` { #defaultdialect-default-paramstyle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ড্রাইভার নির্দিষ্ট না করলে ডিফল্ট paramstyle।

**উদাহরণ:**

```python
print(DefaultDialect.default_paramstyle)   # named
```

### `DefaultDialect.full_returning` { #defaultdialect-full-returning }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.০ থেকে বাতিলের পথে) INSERT/UPDATE/DELETE সবগুলোতে RETURNING চলে কি না; বদলে `insert_returning`, `update_returning`, `delete_returning` আলাদাভাবে দেখুন।

**উদাহরণ:**

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print(pg.full_returning)   # True
```

### `DefaultDialect.get_pool_class()` { #defaultdialect-get-pool-class }

```python
DefaultDialect.get_pool_class(url)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) URL-এর জন্য পুল ক্লাস (`get_dialect_pool_class()` ভেতরে এটি ডাকে)।

**উদাহরণ:**

```python
print(sqlite.dialect.get_pool_class(make_url("sqlite:///x.db")).__name__)   # QueuePool
```

### `DefaultDialect.insert_null_pk_still_autoincrements` { #defaultdialect-insert-null-pk-still-autoincrements }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

primary key-এ `NULL` দিলেও ডেটাবেস নিজে মান বসায় কি না (SQLite-এ `True`)।

**উদাহরণ:**

```python
print(sl.insert_null_pk_still_autoincrements, pg.insert_null_pk_still_autoincrements)   # True False
```

### `DefaultDialect.isolation_level` { #defaultdialect-isolation-level }

**ধরন:** অ্যাট্রিবিউট

শ্রেণি-স্তরের পুরোনো অ্যাট্রিবিউট, **সবসময় `None`**। `create_engine(isolation_level=...)` বা `DefaultDialect(isolation_level=...)`-এর মান এখানে নয়, ভেতরের একটি অ্যাট্রিবিউটে রাখা হয় আর প্রতিটি নতুন সংযোগে প্রয়োগ হয়। কার্যকর মান দেখতে `conn.get_isolation_level()`।

**উদাহরণ:**

```python
e2 = create_engine("sqlite://", isolation_level="READ UNCOMMITTED")
with e2.connect() as conn:
    print(e2.dialect.isolation_level, conn.get_isolation_level())   # None READ UNCOMMITTED
```

### `DefaultDialect.non_native_boolean_check_constraint` { #defaultdialect-non-native-boolean-check-constraint }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

native BOOLEAN নেই এমন ডেটাবেসে `Boolean(create_constraint=True)` দিলে `CHECK (x IN (0, 1))` বসাবে কি না।

**উদাহরণ:**

```python
print(sl.non_native_boolean_check_constraint)   # True
```

### `DefaultDialect.postfetch_lastrowid` { #defaultdialect-postfetch-lastrowid }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT-এর পর `cursor.lastrowid` থেকে primary key আনে কি না (RETURNING না থাকলে)।

**উদাহরণ:**

```python
print(sl.postfetch_lastrowid, my.postfetch_lastrowid, pg.postfetch_lastrowid)   # True True False
```

## `StrCompileDialect` { #strcompiledialect }

```python
from sqlalchemy.engine.default import StrCompileDialect
```

ডায়ালেক্ট ছাড়া `str(stmt)` দিলে যে ডায়ালেক্ট ব্যবহার হয়: [`StrSQLCompiler`](compiler.md#strsqlcompiler) দিয়ে, ডায়ালেক্ট-বিশেষ কনস্ট্রাক্টও এরর না দিয়ে পড়ার মতো করে লেখে। শুধু দেখার জন্য।

**উদাহরণ:**

```python
sd = StrCompileDialect()
print(sd.name, sd.statement_compiler.__name__, select(users.c.id).where(users.c.id == 1).compile(dialect=sd).string.splitlines()[-1])
# default StrSQLCompiler WHERE users.id = :id_1
```

### কনস্ট্রাক্টরের প্যারামিটার { #strcompiledialect-params }

```python
StrCompileDialect(paramstyle=None, isolation_level=None, dbapi=None, implicit_returning=True, supports_native_boolean=None, max_identifier_length=None, label_length=None, insertmanyvalues_page_size=_NoArg.NO_ARG, use_insertmanyvalues=None, compiler_linting=0, server_side_cursors=False, skip_autocommit_rollback=False, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `paramstyle` | `DefaultDialect`-এর মতো। |
| `isolation_level` | `DefaultDialect`-এর মতো। |
| `dbapi` | `DefaultDialect`-এর মতো। |
| `implicit_returning` | `DefaultDialect`-এর মতো। |
| `supports_native_boolean` | `DefaultDialect`-এর মতো। |
| `max_identifier_length` | `DefaultDialect`-এর মতো। |
| `label_length` | `DefaultDialect`-এর মতো। |
| `insertmanyvalues_page_size` | `DefaultDialect`-এর মতো। |
| `use_insertmanyvalues` | `DefaultDialect`-এর মতো। |
| `compiler_linting` | `DefaultDialect`-এর মতো। |
| `server_side_cursors` | `DefaultDialect`-এর মতো। |
| `skip_autocommit_rollback` | `DefaultDialect`-এর মতো। |
| `kwargs` | `DefaultDialect`-এর মতো। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`DefaultDialect`](#defaultdialect-summary)-এর মতো।

## স্টেটমেন্ট চালানোর context { #executioncontext-group }

## `ExecutionContext` { #executioncontext }

```python
from sqlalchemy.engine import ExecutionContext
```

একটি স্টেটমেন্ট একবার চালানোর সব তথ্য: কোন সংযোগ, কোন cursor, কম্পাইল করা SQL, প্যারামিটার, INSERT না UPDATE … প্রতিবার `execute()`-এ একটি নতুন context তৈরি হয়। পাওয়া যায় `result.context`, আর `before_cursor_execute` / `after_cursor_execute` ইভেন্টের `context` আর্গুমেন্টে। (ইন্টারফেস; আসল বাস্তবায়ন `DefaultExecutionContext`।)

**উদাহরণ:**

```python
seen = []
@event.listens_for(engine, "before_cursor_execute")
def log(conn, cursor, statement, parameters, context, executemany):
    seen.append((type(context).__name__, context.isinsert, context.executemany))
with engine.begin() as conn:
    conn.execute(insert(users), [{"name": "ক"}, {"name": "খ"}])
print(seen)   # [('SQLiteExecutionContext', True, True)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #executioncontext-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`compiled`](#executioncontext-compiled) | অ্যাট্রিবিউট | কম্পাইল করা [`Compiled`](compiler.md#compiled) (text/driver SQL হলে `None`)। |
| [`connection`](#executioncontext-connection) | অ্যাট্রিবিউট | যে `Connection`-এ চলছে। |
| [`create_cursor()`](#executioncontext-create-cursor) | মেথড (internal) | এই execution-এর জন্য একটি DB-API cursor বানায় (stream_results হলে server-side cursor)। |
| [`cursor`](#executioncontext-cursor) | অ্যাট্রিবিউট | ব্যবহৃত DB-API cursor। |
| [`dialect`](#executioncontext-dialect) | অ্যাট্রিবিউট | ডায়ালেক্ট। |
| [`engine`](#executioncontext-engine) | অ্যাট্রিবিউট | মূল `Engine`। |
| [`execute_style`](#executioncontext-execute-style) | অ্যাট্রিবিউট (internal) | কীভাবে চালানো হলো: `EXECUTE`, `EXECUTEMANY`, বা `INSERTMANYVALUES`। |
| [`executemany`](#executioncontext-executemany) | অ্যাট্রিবিউট | অনেক প্যারামিটার-সেট নিয়ে চলছে কি না। |
| [`execution_options`](#executioncontext-execution-options) | অ্যাট্রিবিউট | এই execution-এর মোট execution options। |
| [`fetchall_for_returning()`](#executioncontext-fetchall-for-returning) | মেথড (internal) | RETURNING-এর ফল cursor থেকে একবারে আনে (কিছু ড্রাইভারে বিশেষ ব্যবস্থা লাগে)। |
| [`fire_sequence()`](#executioncontext-fire-sequence) | মেথড (internal) | একটি `Sequence`-এর পরের মান আনে (`nextval()`)। |
| [`get_out_parameter_values()`](#executioncontext-get-out-parameter-values) | মেথড (internal) | stored procedure-এর OUT প্যারামিটারের মান (Oracle)। |
| [`get_rowcount()`](#executioncontext-get-rowcount) | মেথড | ইন্টারফেসের মেথড: `cursor.rowcount`। |
| [`handle_dbapi_exception()`](#executioncontext-handle-dbapi-exception) | মেথড (internal) | ড্রাইভার-এরর হলে ডায়ালেক্ট-বিশেষ পরিষ্কারের hook। |
| [`invoked_statement`](#executioncontext-invoked-statement) | অ্যাট্রিবিউট | ব্যবহারকারী যে স্টেটমেন্ট অবজেক্ট দিয়েছিলেন (ক্যাশ থেকে কম্পাইল-ফল আসলেও এটি আসল অবজেক্ট)। |
| [`isinsert`](#executioncontext-isinsert) | অ্যাট্রিবিউট | INSERT কি না। |
| [`isupdate`](#executioncontext-isupdate) | অ্যাট্রিবিউট | UPDATE কি না। |
| [`lastrow_has_defaults()`](#executioncontext-lastrow-has-defaults) | মেথড | শেষ INSERT/UPDATE-এর রো-তে ডেটাবেস-ডিফল্ট বা SQL-এক্সপ্রেশন মান ছিল কি না (তাহলে ORM সেগুলো আবার আনে)। |
| [`no_parameters`](#executioncontext-no-parameters) | অ্যাট্রিবিউট | `execution_options(no_parameters=True)` দেওয়া হয়েছে কি না: তখন প্যারামিটার না থাকলে `cursor.execute(sql)` একটি মাত্র আর্গুমেন্টে ডাকা হয় (কিছু ড্রাইভারে তখন `%` এস্কেপ লাগে না)। |
| [`parameters`](#executioncontext-parameters) | অ্যাট্রিবিউট | ড্রাইভারে পাঠানো প্যারামিটার (সবসময় তালিকা: একটি রো হলেও `[...]`)। |
| [`post_exec()`](#executioncontext-post-exec) | মেথড (internal) | স্টেটমেন্ট চালানোর পরের hook। |
| [`postfetch_cols`](#executioncontext-postfetch-cols) | অ্যাট্রিবিউট (internal) | INSERT/UPDATE-এর পর ডেটাবেস থেকে আবার আনতে হবে এমন কলাম (server default ইত্যাদি)। |
| [`pre_exec()`](#executioncontext-pre-exec) | মেথড (internal) | স্টেটমেন্ট চালানোর আগের hook। |
| [`prefetch_cols`](#executioncontext-prefetch-cols) | অ্যাট্রিবিউট (internal) | INSERT/UPDATE-এর আগে Python-এ হিসাব করা ডিফল্টের কলাম। |
| [`root_connection`](#executioncontext-root-connection) | অ্যাট্রিবিউট (internal) | মূল `Connection` (branching থাকলে সবচেয়ে বাইরেরটি)। |
| [`statement`](#executioncontext-statement) | অ্যাট্রিবিউট | ড্রাইভারে পাঠানো চূড়ান্ত SQL স্ট্রিং। |

### `ExecutionContext.compiled` { #executioncontext-compiled }

**ধরন:** অ্যাট্রিবিউট

কম্পাইল করা [`Compiled`](compiler.md#compiled) (text/driver SQL হলে `None`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    r = conn.execute(select(users.c.name).where(users.c.id == 1))
    print(type(r.context.compiled).__name__)   # SQLiteCompiler
```

### `ExecutionContext.connection` { #executioncontext-connection }

**ধরন:** অ্যাট্রিবিউট

যে `Connection`-এ চলছে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.connection is conn)   # True
```

### `ExecutionContext.create_cursor()` { #executioncontext-create-cursor }

```python
ExecutionContext.create_cursor()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই execution-এর জন্য একটি DB-API cursor বানায় (stream_results হলে server-side cursor)।

**উদাহরণ:**

```python
print(callable(ExecutionContext.create_cursor))   # True
```

### `ExecutionContext.cursor` { #executioncontext-cursor }

**ধরন:** অ্যাট্রিবিউট

ব্যবহৃত DB-API cursor।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(conn.execute(select(users.c.id)).context.cursor).__name__)   # Cursor
```

### `ExecutionContext.dialect` { #executioncontext-dialect }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্ট।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.dialect is d)   # True
```

### `ExecutionContext.engine` { #executioncontext-engine }

**ধরন:** অ্যাট্রিবিউট

মূল `Engine`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.engine is engine)   # True
```

### `ExecutionContext.execute_style` { #executioncontext-execute-style }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কীভাবে চালানো হলো: `EXECUTE`, `EXECUTEMANY`, বা `INSERTMANYVALUES`। insertmanyvalues শুধু তখন যখন RETURNING লাগে (যেমন ORM-এ নতুন primary key আনতে); নইলে সাধারণ `executemany`।

**উদাহরণ:**

```python
with engine.begin() as conn:
    r1 = conn.execute(insert(users), [{"name": "ক"}, {"name": "খ"}])
    r2 = conn.execute(insert(users).returning(users.c.id), [{"name": "গ"}, {"name": "ঘ"}])
    print(r1.context.execute_style.name, r2.context.execute_style.name)   # EXECUTEMANY INSERTMANYVALUES
```

### `ExecutionContext.executemany` { #executioncontext-executemany }

**ধরন:** অ্যাট্রিবিউট

অনেক প্যারামিটার-সেট নিয়ে চলছে কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.executemany)   # False
```

### `ExecutionContext.execution_options` { #executioncontext-execution-options }

**ধরন:** অ্যাট্রিবিউট

এই execution-এর মোট execution options।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(dict(conn.execute(select(users.c.id).execution_options(my=1)).context.execution_options).get("my"))   # 1
```

### `ExecutionContext.fetchall_for_returning()` { #executioncontext-fetchall-for-returning }

```python
ExecutionContext.fetchall_for_returning(cursor)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

RETURNING-এর ফল cursor থেকে একবারে আনে (কিছু ড্রাইভারে বিশেষ ব্যবস্থা লাগে)।

**উদাহরণ:**

```python
print(callable(ExecutionContext.fetchall_for_returning))   # True
```

### `ExecutionContext.fire_sequence()` { #executioncontext-fire-sequence }

```python
ExecutionContext.fire_sequence(seq, type_)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি `Sequence`-এর পরের মান আনে (`nextval()`)।

**উদাহরণ:**

```python
print(callable(ExecutionContext.fire_sequence))   # True
```

### `ExecutionContext.get_out_parameter_values()` { #executioncontext-get-out-parameter-values }

```python
ExecutionContext.get_out_parameter_values(out_param_names)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

stored procedure-এর OUT প্যারামিটারের মান (Oracle)।

**উদাহরণ:**

```python
print(callable(ExecutionContext.get_out_parameter_values))   # True
```

### `ExecutionContext.get_rowcount()` { #executioncontext-get-rowcount }

```python
ExecutionContext.get_rowcount()
```

**ধরন:** মেথড

ইন্টারফেসের মেথড: `cursor.rowcount`। **ডিফল্ট `DefaultExecutionContext` এটি বাস্তবায়ন করে না** (ডাকলে `NotImplementedError`); সেখানে `context.rowcount` অ্যাট্রিবিউট আছে, আর `result.rowcount` সেটাই পড়ে। শুধু কিছু ডায়ালেক্ট এই মেথড বাস্তবায়ন করে।

**উদাহরণ:**

```python
from sqlalchemy import update
with engine.begin() as conn:
    r = conn.execute(update(users).values(name="x"))
    print(r.rowcount, r.context.rowcount)   # 2 2
    try:
        r.context.get_rowcount()
    except NotImplementedError:
        print("বাস্তবায়িত নয়")   # বাস্তবায়িত নয়
```

### `ExecutionContext.handle_dbapi_exception()` { #executioncontext-handle-dbapi-exception }

```python
ExecutionContext.handle_dbapi_exception(e)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ড্রাইভার-এরর হলে ডায়ালেক্ট-বিশেষ পরিষ্কারের hook।

**উদাহরণ:**

```python
print(callable(ExecutionContext.handle_dbapi_exception))   # True
```

### `ExecutionContext.invoked_statement` { #executioncontext-invoked-statement }

**ধরন:** অ্যাট্রিবিউট

ব্যবহারকারী যে স্টেটমেন্ট অবজেক্ট দিয়েছিলেন (ক্যাশ থেকে কম্পাইল-ফল আসলেও এটি আসল অবজেক্ট)।

**উদাহরণ:**

```python
stmt = select(users.c.id)
with engine.connect() as conn:
    print(conn.execute(stmt).context.invoked_statement is stmt)   # True
```

### `ExecutionContext.isinsert` { #executioncontext-isinsert }

**ধরন:** অ্যাট্রিবিউট

INSERT কি না।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.isinsert)   # True
```

### `ExecutionContext.isupdate` { #executioncontext-isupdate }

**ধরন:** অ্যাট্রিবিউট

UPDATE কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.isupdate)   # False
```

### `ExecutionContext.lastrow_has_defaults()` { #executioncontext-lastrow-has-defaults }

```python
ExecutionContext.lastrow_has_defaults()
```

**ধরন:** মেথড

শেষ INSERT/UPDATE-এর রো-তে ডেটাবেস-ডিফল্ট বা SQL-এক্সপ্রেশন মান ছিল কি না (তাহলে ORM সেগুলো আবার আনে)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.lastrow_has_defaults())   # False
```

### `ExecutionContext.no_parameters` { #executioncontext-no-parameters }

**ধরন:** অ্যাট্রিবিউট

`execution_options(no_parameters=True)` দেওয়া হয়েছে কি না: তখন প্যারামিটার না থাকলে `cursor.execute(sql)` একটি মাত্র আর্গুমেন্টে ডাকা হয় (কিছু ড্রাইভারে তখন `%` এস্কেপ লাগে না)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.exec_driver_sql("SELECT 1").context.no_parameters,
          conn.exec_driver_sql("SELECT 1", execution_options={"no_parameters": True}).context.no_parameters)   # False True
```

### `ExecutionContext.parameters` { #executioncontext-parameters }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারে পাঠানো প্যারামিটার (সবসময় তালিকা: একটি রো হলেও `[...]`)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id).where(users.c.id == 1)).context.parameters)   # [(1,)]
```

### `ExecutionContext.post_exec()` { #executioncontext-post-exec }

```python
ExecutionContext.post_exec()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট চালানোর পরের hook।

**উদাহরণ:**

```python
print(callable(ExecutionContext.post_exec))   # True
```

### `ExecutionContext.postfetch_cols` { #executioncontext-postfetch-cols }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT/UPDATE-এর পর ডেটাবেস থেকে আবার আনতে হবে এমন কলাম (server default ইত্যাদি)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.postfetch_cols)   # []
```

### `ExecutionContext.pre_exec()` { #executioncontext-pre-exec }

```python
ExecutionContext.pre_exec()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

স্টেটমেন্ট চালানোর আগের hook।

**উদাহরণ:**

```python
print(callable(ExecutionContext.pre_exec))   # True
```

### `ExecutionContext.prefetch_cols` { #executioncontext-prefetch-cols }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT/UPDATE-এর আগে Python-এ হিসাব করা ডিফল্টের কলাম।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.prefetch_cols)   # []
```

### `ExecutionContext.root_connection` { #executioncontext-root-connection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল `Connection` (branching থাকলে সবচেয়ে বাইরেরটি)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.root_connection is conn)   # True
```

### `ExecutionContext.statement` { #executioncontext-statement }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারে পাঠানো চূড়ান্ত SQL স্ট্রিং।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id).where(users.c.id == 1)).context.statement.splitlines()[-1])   # WHERE users.id = ?
```

## `DefaultExecutionContext` { #defaultexecutioncontext }

```python
from sqlalchemy.engine.default import DefaultExecutionContext
```

`ExecutionContext`-এর ডিফল্ট বাস্তবায়ন। কলামের Python-ডিফল্ট (`default=lambda: ...`) লেখার সময় যে `context` আর্গুমেন্ট পান, সেটিও এটি: `context.get_current_parameters()` দিয়ে একই রো-র অন্য কলামের মান পড়া যায়।

**উদাহরণ:**

```python
def make_slug(context):
    return context.get_current_parameters()["title"].lower().replace(" ", "-")
t = Table("posts", MetaData(), Column("id", Integer, primary_key=True), Column("title", String),
          Column("slug", String, default=make_slug))
t.create(engine)
with engine.begin() as conn:
    conn.execute(insert(t).values(title="Hello World"))
    print(conn.execute(select(t.c.slug)).scalar())   # hello-world
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #defaultexecutioncontext-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache_hit`](#defaultexecutioncontext-cache-hit) | অ্যাট্রিবিউট | এই execution-এ কম্পাইল-ক্যাশ ব্যবহার হয়েছে কি না ([`CacheStats`](#cachestats))। |
| [`compiled_parameters`](#defaultexecutioncontext-compiled-parameters) | অ্যাট্রিবিউট (internal) | প্রতিটি প্যারামিটার-সেটের নাম → মান dict-এর তালিকা (ড্রাইভারের রূপে বদলানোর আগে)। |
| [`create_default_cursor()`](#defaultexecutioncontext-create-default-cursor) | মেথড (internal) | সাধারণ cursor বানায়। |
| [`create_server_side_cursor()`](#defaultexecutioncontext-create-server-side-cursor) | মেথড (internal) | server-side (streaming) cursor বানায় (ডায়ালেক্ট সমর্থন করলে)। |
| [`current_parameters`](#defaultexecutioncontext-current-parameters) | অ্যাট্রিবিউট (internal) | ডিফল্ট-ফাংশন চলার সময় বর্তমান রো-র প্যারামিটার (সরাসরি না পড়ে `get_current_parameters()` দিন)। |
| [`cursor_fetch_strategy`](#defaultexecutioncontext-cursor-fetch-strategy) | অ্যাট্রিবিউট (internal) | ফল আনার কৌশল (সাধারণ, buffered, …)। |
| [`extracted_parameters`](#defaultexecutioncontext-extracted-parameters) | অ্যাট্রিবিউট (internal) | ক্যাশ থেকে আসা কম্পাইলের জন্য স্টেটমেন্ট থেকে বের করা প্যারামিটার। |
| [`get_current_parameters()`](#defaultexecutioncontext-get-current-parameters) | মেথড | কলামের Python-ডিফল্ট ফাংশনের ভেতরে: **এই রো-র** সব কলামের মান (dict)। |
| [`get_insert_default()`](#defaultexecutioncontext-get-insert-default) | মেথড (internal) | একটি কলামের INSERT-ডিফল্ট হিসাব করে। |
| [`get_lastrowid()`](#defaultexecutioncontext-get-lastrowid) | মেথড (internal) | INSERT-এর পর `cursor.lastrowid`। |
| [`get_result_processor()`](#defaultexecutioncontext-get-result-processor) | মেথড (internal) | ফলের একটি কলামের মান Python-এ বদলানোর ফাংশন (টাইপ অনুযায়ী)। |
| [`get_update_default()`](#defaultexecutioncontext-get-update-default) | মেথড (internal) | একটি কলামের UPDATE-ডিফল্ট (`onupdate`) হিসাব করে। |
| [`identifier_preparer`](#defaultexecutioncontext-identifier-preparer) | প্রপার্টি (internal) | ডায়ালেক্টের `IdentifierPreparer`। |
| [`inserted_primary_key_rows`](#defaultexecutioncontext-inserted-primary-key-rows) | প্রপার্টি | INSERT-এ নতুন primary key-গুলো (প্রতিটি রো-র জন্য একটি tuple); `result.inserted_primary_key_rows` এটাই। |
| [`is_crud`](#defaultexecutioncontext-is-crud) | অ্যাট্রিবিউট | INSERT/UPDATE/DELETE কি না। |
| [`is_text`](#defaultexecutioncontext-is-text) | অ্যাট্রিবিউট | `text()` স্টেটমেন্ট কি না। |
| [`isddl`](#defaultexecutioncontext-isddl) | অ্যাট্রিবিউট | DDL কি না। |
| [`isdelete`](#defaultexecutioncontext-isdelete) | অ্যাট্রিবিউট | DELETE কি না। |
| [`result_column_struct`](#defaultexecutioncontext-result-column-struct) | অ্যাট্রিবিউট (internal) | ফল-কলাম মেলানোর ভেতরের গঠন। |
| [`returned_default_rows`](#defaultexecutioncontext-returned-default-rows) | অ্যাট্রিবিউট (internal) | RETURNING থেকে পাওয়া ডিফল্ট মানের রো। |
| [`rowcount`](#defaultexecutioncontext-rowcount) | প্রপার্টি | `cursor.rowcount`-এর মান (ক্যাশ করা)। |
| [`supports_sane_multi_rowcount()`](#defaultexecutioncontext-supports-sane-multi-rowcount) | মেথড (internal) | executemany-তে rowcount বিশ্বাসযোগ্য কি না। |
| [`supports_sane_rowcount()`](#defaultexecutioncontext-supports-sane-rowcount) | মেথড (internal) | rowcount বিশ্বাসযোগ্য কি না। |
| [`unicode_statement`](#defaultexecutioncontext-unicode-statement) | অ্যাট্রিবিউট (internal) | চূড়ান্ত SQL স্ট্রিং (`statement`-এর মতো)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DefaultExecutionContext`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ExecutionContext` থেকে:** [`compiled`](#executioncontext-compiled) · [`connection`](#executioncontext-connection) · [`create_cursor()`](#executioncontext-create-cursor) · [`engine`](#executioncontext-engine) · [`execute_style`](#executioncontext-execute-style) · [`executemany`](#executioncontext-executemany) · [`execution_options`](#executioncontext-execution-options) · [`fetchall_for_returning()`](#executioncontext-fetchall-for-returning) · [`fire_sequence()`](#executioncontext-fire-sequence) · [`get_out_parameter_values()`](#executioncontext-get-out-parameter-values) · [`get_rowcount()`](#executioncontext-get-rowcount) · [`handle_dbapi_exception()`](#executioncontext-handle-dbapi-exception) · [`invoked_statement`](#executioncontext-invoked-statement) · [`isinsert`](#executioncontext-isinsert) · [`isupdate`](#executioncontext-isupdate) · [`lastrow_has_defaults()`](#executioncontext-lastrow-has-defaults) · [`no_parameters`](#executioncontext-no-parameters) · [`post_exec()`](#executioncontext-post-exec) · [`postfetch_cols`](#executioncontext-postfetch-cols) · [`pre_exec()`](#executioncontext-pre-exec) · [`prefetch_cols`](#executioncontext-prefetch-cols)

///

### `DefaultExecutionContext.cache_hit` { #defaultexecutioncontext-cache-hit }

**ধরন:** অ্যাট্রিবিউট

এই execution-এ কম্পাইল-ক্যাশ ব্যবহার হয়েছে কি না ([`CacheStats`](#cachestats))।

**উদাহরণ:**

```python
stmt = select(users.c.id)
with engine.connect() as conn:
    print(conn.execute(stmt).context.cache_hit.name, conn.execute(stmt).context.cache_hit.name)   # CACHE_MISS CACHE_HIT
```

### `DefaultExecutionContext.compiled_parameters` { #defaultexecutioncontext-compiled-parameters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

প্রতিটি প্যারামিটার-সেটের নাম → মান dict-এর তালিকা (ড্রাইভারের রূপে বদলানোর আগে)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id).where(users.c.id == 1)).context.compiled_parameters)   # [{'id_1': 1}]
```

### `DefaultExecutionContext.create_default_cursor()` { #defaultexecutioncontext-create-default-cursor }

```python
DefaultExecutionContext.create_default_cursor()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সাধারণ cursor বানায়।

**উদাহরণ:**

```python
print(callable(DefaultExecutionContext.create_default_cursor))   # True
```

### `DefaultExecutionContext.create_server_side_cursor()` { #defaultexecutioncontext-create-server-side-cursor }

```python
DefaultExecutionContext.create_server_side_cursor()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

server-side (streaming) cursor বানায় (ডায়ালেক্ট সমর্থন করলে)।

**উদাহরণ:**

```python
print(callable(DefaultExecutionContext.create_server_side_cursor))   # True
```

### `DefaultExecutionContext.current_parameters` { #defaultexecutioncontext-current-parameters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডিফল্ট-ফাংশন চলার সময় বর্তমান রো-র প্যারামিটার (সরাসরি না পড়ে `get_current_parameters()` দিন)।

**উদাহরণ:**

```python
print(DefaultExecutionContext.current_parameters)   # None
```

### `DefaultExecutionContext.cursor_fetch_strategy` { #defaultexecutioncontext-cursor-fetch-strategy }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফল আনার কৌশল (সাধারণ, buffered, …)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(conn.execute(select(users.c.id)).context.cursor_fetch_strategy).__name__)   # CursorFetchStrategy
```

### `DefaultExecutionContext.extracted_parameters` { #defaultexecutioncontext-extracted-parameters }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ থেকে আসা কম্পাইলের জন্য স্টেটমেন্ট থেকে বের করা প্যারামিটার।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(type(conn.execute(select(users.c.id).where(users.c.id == 1)).context.extracted_parameters).__name__)   # list
```

### `DefaultExecutionContext.get_current_parameters()` { #defaultexecutioncontext-get-current-parameters }

```python
DefaultExecutionContext.get_current_parameters(isolate_multiinsert_groups=True)
```

**ধরন:** মেথড

কলামের Python-ডিফল্ট ফাংশনের ভেতরে: **এই রো-র** সব কলামের মান (dict)। একই রো-র অন্য কলাম থেকে মান হিসাব করতে।

**উদাহরণ:**

```python
seen = []
def dflt(context):
    seen.append(sorted(context.get_current_parameters()))
    return "x"
t = Table("t2", MetaData(), Column("id", Integer, primary_key=True), Column("a", String), Column("b", String, default=dflt))
t.create(engine)
with engine.begin() as conn:
    conn.execute(insert(t).values(a="1"))
print(seen)   # [['a', 'b']]
```

### `DefaultExecutionContext.get_insert_default()` { #defaultexecutioncontext-get-insert-default }

```python
DefaultExecutionContext.get_insert_default(column)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি কলামের INSERT-ডিফল্ট হিসাব করে।

**উদাহরণ:**

```python
print(callable(DefaultExecutionContext.get_insert_default))   # True
```

### `DefaultExecutionContext.get_lastrowid()` { #defaultexecutioncontext-get-lastrowid }

```python
DefaultExecutionContext.get_lastrowid()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

INSERT-এর পর `cursor.lastrowid`।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.get_lastrowid())   # 3
```

### `DefaultExecutionContext.get_result_processor()` { #defaultexecutioncontext-get-result-processor }

```python
DefaultExecutionContext.get_result_processor(type_, colname, coltype)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফলের একটি কলামের মান Python-এ বদলানোর ফাংশন (টাইপ অনুযায়ী)।

**উদাহরণ:**

```python
print(callable(DefaultExecutionContext.get_result_processor))   # True
```

### `DefaultExecutionContext.get_update_default()` { #defaultexecutioncontext-get-update-default }

```python
DefaultExecutionContext.get_update_default(column)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি কলামের UPDATE-ডিফল্ট (`onupdate`) হিসাব করে।

**উদাহরণ:**

```python
print(callable(DefaultExecutionContext.get_update_default))   # True
```

### `DefaultExecutionContext.identifier_preparer` { #defaultexecutioncontext-identifier-preparer }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডায়ালেক্টের `IdentifierPreparer`।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.identifier_preparer is d.identifier_preparer)   # True
```

### `DefaultExecutionContext.inserted_primary_key_rows` { #defaultexecutioncontext-inserted-primary-key-rows }

**ধরন:** প্রপার্টি

INSERT-এ নতুন primary key-গুলো (প্রতিটি রো-র জন্য একটি tuple); `result.inserted_primary_key_rows` এটাই।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.inserted_primary_key_rows)   # [(3,)]
```

### `DefaultExecutionContext.is_crud` { #defaultexecutioncontext-is-crud }

**ধরন:** অ্যাট্রিবিউট

INSERT/UPDATE/DELETE কি না।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(insert(users).values(name="x")).context.is_crud)   # True
```

### `DefaultExecutionContext.is_text` { #defaultexecutioncontext-is-text }

**ধরন:** অ্যাট্রিবিউট

`text()` স্টেটমেন্ট কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(text("SELECT 1")).context.is_text)   # True
```

### `DefaultExecutionContext.isddl` { #defaultexecutioncontext-isddl }

**ধরন:** অ্যাট্রিবিউট

DDL কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.isddl)   # False
```

### `DefaultExecutionContext.isdelete` { #defaultexecutioncontext-isdelete }

**ধরন:** অ্যাট্রিবিউট

DELETE কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.isdelete)   # False
```

### `DefaultExecutionContext.result_column_struct` { #defaultexecutioncontext-result-column-struct }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফল-কলাম মেলানোর ভেতরের গঠন।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.result_column_struct is not None)   # True
```

### `DefaultExecutionContext.returned_default_rows` { #defaultexecutioncontext-returned-default-rows }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

RETURNING থেকে পাওয়া ডিফল্ট মানের রো।

**উদাহরণ:**

```python
print(DefaultExecutionContext.returned_default_rows)   # None
```

### `DefaultExecutionContext.rowcount` { #defaultexecutioncontext-rowcount }

**ধরন:** প্রপার্টি

`cursor.rowcount`-এর মান (ক্যাশ করা)।

**উদাহরণ:**

```python
from sqlalchemy import delete
with engine.begin() as conn:
    print(conn.execute(delete(users).where(users.c.id == 1)).context.rowcount)   # 1
```

### `DefaultExecutionContext.supports_sane_multi_rowcount()` { #defaultexecutioncontext-supports-sane-multi-rowcount }

```python
DefaultExecutionContext.supports_sane_multi_rowcount()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

executemany-তে rowcount বিশ্বাসযোগ্য কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.supports_sane_multi_rowcount())   # True
```

### `DefaultExecutionContext.supports_sane_rowcount()` { #defaultexecutioncontext-supports-sane-rowcount }

```python
DefaultExecutionContext.supports_sane_rowcount()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

rowcount বিশ্বাসযোগ্য কি না।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.execute(select(users.c.id)).context.supports_sane_rowcount())   # True
```

### `DefaultExecutionContext.unicode_statement` { #defaultexecutioncontext-unicode-statement }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

চূড়ান্ত SQL স্ট্রিং (`statement`-এর মতো)।

**উদাহরণ:**

```python
with engine.connect() as conn:
    print(conn.exec_driver_sql("SELECT 1").context.unicode_statement)   # SELECT 1
```

## `ExecuteStyle` { #executestyle }

```python
from sqlalchemy.engine.interfaces import ExecuteStyle
```

(২.০) একটি স্টেটমেন্ট ড্রাইভারে কীভাবে পাঠানো হলো (`context.execute_style`)।

**উদাহরণ:**

```python
with engine.begin() as conn:
    print(conn.execute(select(users.c.id)).context.execute_style.name)   # EXECUTE
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #executestyle-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`EXECUTE`](#executestyle-EXECUTE) | অ্যাট্রিবিউট | একবার `cursor.execute()`। |
| [`EXECUTEMANY`](#executestyle-EXECUTEMANY) | অ্যাট্রিবিউট | `cursor.executemany()` (অনেক প্যারামিটার-সেট, RETURNING ছাড়া)। |
| [`INSERTMANYVALUES`](#executestyle-INSERTMANYVALUES) | অ্যাট্রিবিউট | SQLAlchemy-র insertmanyvalues: অনেক রো একটি (বা কয়েকটি) `INSERT ... VALUES (...), (...)`-এ, RETURNING-সহ। |

### `ExecuteStyle.EXECUTE` { #executestyle-EXECUTE }

**ধরন:** অ্যাট্রিবিউট

একবার `cursor.execute()`।

**উদাহরণ:**

```python
print(ExecuteStyle.EXECUTE.value)   # 0
```

### `ExecuteStyle.EXECUTEMANY` { #executestyle-EXECUTEMANY }

**ধরন:** অ্যাট্রিবিউট

`cursor.executemany()` (অনেক প্যারামিটার-সেট, RETURNING ছাড়া)।

**উদাহরণ:**

```python
print(ExecuteStyle.EXECUTEMANY.value)   # 1
```

### `ExecuteStyle.INSERTMANYVALUES` { #executestyle-INSERTMANYVALUES }

**ধরন:** অ্যাট্রিবিউট

SQLAlchemy-র insertmanyvalues: অনেক রো একটি (বা কয়েকটি) `INSERT ... VALUES (...), (...)`-এ, RETURNING-সহ।

**উদাহরণ:**

```python
print(ExecuteStyle.INSERTMANYVALUES.value)   # 2
```

## `ExceptionContext` { #exceptioncontext }

```python
from sqlalchemy.engine import ExceptionContext
```

[`handle_error`](events.md#dialectevents-handle-error) ইভেন্টের আর্গুমেন্ট: একটি এরর ঘটার মুহূর্তের সব তথ্য। হুকে এটি দেখে এরর লগ করা, নিজের এক্সেপশনে বদলানো (`return MyError(...)` বা `raise`), বা "এটা সংযোগ-বিচ্ছিন্নতা" বলে চিহ্নিত করা (`ctx.is_disconnect = True`) যায়।

**উদাহরণ:**

```python
seen = []
@event.listens_for(engine, "handle_error")
def on_error(ctx):
    seen.append((type(ctx.original_exception).__name__, type(ctx.sqlalchemy_exception).__name__, ctx.statement))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.OperationalError:
    pass
print(seen)   # [('OperationalError', 'OperationalError', 'SELECT * FROM nope')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #exceptioncontext-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`chained_exception`](#exceptioncontext-chained-exception) | অ্যাট্রিবিউট | একাধিক `handle_error` হুক থাকলে আগের হুক যে নতুন এক্সেপশন ফেরত দিয়েছে। |
| [`connection`](#exceptioncontext-connection) | অ্যাট্রিবিউট | যে `Connection`-এ এরর (সংযোগ খোলার সময় হলে `None`)। |
| [`cursor`](#exceptioncontext-cursor) | অ্যাট্রিবিউট | যে DB-API cursor-এ এরর। |
| [`dialect`](#exceptioncontext-dialect) | অ্যাট্রিবিউট | ডায়ালেক্ট। |
| [`engine`](#exceptioncontext-engine) | অ্যাট্রিবিউট | `Engine` (সংযোগ খোলার সময়ের এররেও পাওয়া যায়)। |
| [`execution_context`](#exceptioncontext-execution-context) | অ্যাট্রিবিউট | চলমান `ExecutionContext` (থাকলে)। |
| [`invalidate_pool_on_disconnect`](#exceptioncontext-invalidate-pool-on-disconnect) | অ্যাট্রিবিউট | `is_disconnect` হলে পুরো পুল বাতিল করবে কি না (ডিফল্ট `True`); হুকে `False` করলে শুধু এই সংযোগ। |
| [`is_disconnect`](#exceptioncontext-is-disconnect) | অ্যাট্রিবিউট | এররটি সংযোগ-বিচ্ছিন্নতা কি না। |
| [`is_pre_ping`](#exceptioncontext-is-pre-ping) | অ্যাট্রিবিউট | এররটি `pool_pre_ping`-এর পরীক্ষার সময় কি না। |
| [`original_exception`](#exceptioncontext-original-exception) | অ্যাট্রিবিউট | ড্রাইভারের আসল এক্সেপশন (`sqlite3.OperationalError` ইত্যাদি)। |
| [`parameters`](#exceptioncontext-parameters) | অ্যাট্রিবিউট | স্টেটমেন্টের প্যারামিটার। |
| [`sqlalchemy_exception`](#exceptioncontext-sqlalchemy-exception) | অ্যাট্রিবিউট | SQLAlchemy যে মোড়ানো এক্সেপশন তুলবে (`OperationalError` ইত্যাদি); হুক অন্য কিছু ফেরত না দিলে এটাই আসে। |
| [`statement`](#exceptioncontext-statement) | অ্যাট্রিবিউট | যে SQL স্ট্রিং চালাতে গিয়ে এরর। |

### `ExceptionContext.chained_exception` { #exceptioncontext-chained-exception }

**ধরন:** অ্যাট্রিবিউট

একাধিক `handle_error` হুক থাকলে আগের হুক যে নতুন এক্সেপশন ফেরত দিয়েছে। **২.১.৯-এ এটি কেবল তখনই বসানো হয়**; আগের কোনো হুক কিছু ফেরত না দিলে পড়লে `AttributeError`, তাই `getattr(ctx, "chained_exception", None)` লিখুন।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(getattr(ctx, "chained_exception", None)))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [None]
```

### `ExceptionContext.connection` { #exceptioncontext-connection }

**ধরন:** অ্যাট্রিবিউট

যে `Connection`-এ এরর (সংযোগ খোলার সময় হলে `None`)।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.connection is not None))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [True]
```

### `ExceptionContext.cursor` { #exceptioncontext-cursor }

**ধরন:** অ্যাট্রিবিউট

যে DB-API cursor-এ এরর। **সতর্কতা:** ইন্টারফেসে ঘোষিত থাকলেও ২.১.৯-এর বাস্তবায়ন (`ExceptionContextImpl`) এটি বসায় না, তাই পড়লে `AttributeError`। cursor দরকার হলে `ctx.execution_context.cursor` ব্যবহার করুন।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append((hasattr(ctx, "cursor"), type(ctx.execution_context.cursor).__name__)))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [(False, 'Cursor')]
```

### `ExceptionContext.dialect` { #exceptioncontext-dialect }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্ট।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.dialect.name))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # ['sqlite']
```

### `ExceptionContext.engine` { #exceptioncontext-engine }

**ধরন:** অ্যাট্রিবিউট

`Engine` (সংযোগ খোলার সময়ের এররেও পাওয়া যায়)।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.engine is engine))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [True]
```

### `ExceptionContext.execution_context` { #exceptioncontext-execution-context }

**ধরন:** অ্যাট্রিবিউট

চলমান `ExecutionContext` (থাকলে)।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.execution_context is not None))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [True]
```

### `ExceptionContext.invalidate_pool_on_disconnect` { #exceptioncontext-invalidate-pool-on-disconnect }

**ধরন:** অ্যাট্রিবিউট

`is_disconnect` হলে পুরো পুল বাতিল করবে কি না (ডিফল্ট `True`); হুকে `False` করলে শুধু এই সংযোগ।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.invalidate_pool_on_disconnect))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [True]
```

### `ExceptionContext.is_disconnect` { #exceptioncontext-is-disconnect }

**ধরন:** অ্যাট্রিবিউট

এররটি সংযোগ-বিচ্ছিন্নতা কি না। হুকে `True` বসালে SQLAlchemy সংযোগটি বাতিল করবে (নিজের "এই এরর মানে সংযোগ নষ্ট" নিয়মের জন্য)।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.is_disconnect))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [False]
```

### `ExceptionContext.is_pre_ping` { #exceptioncontext-is-pre-ping }

**ধরন:** অ্যাট্রিবিউট

এররটি `pool_pre_ping`-এর পরীক্ষার সময় কি না।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.is_pre_ping))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # [False]
```

### `ExceptionContext.original_exception` { #exceptioncontext-original-exception }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারের আসল এক্সেপশন (`sqlite3.OperationalError` ইত্যাদি)।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(type(ctx.original_exception).__module__))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # ['sqlite3']
```

### `ExceptionContext.parameters` { #exceptioncontext-parameters }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের প্যারামিটার।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.parameters))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope WHERE x = ?", (5,))
except exc.DBAPIError:
    pass
print(seen)   # [(5,)]
```

### `ExceptionContext.sqlalchemy_exception` { #exceptioncontext-sqlalchemy-exception }

**ধরন:** অ্যাট্রিবিউট

SQLAlchemy যে মোড়ানো এক্সেপশন তুলবে (`OperationalError` ইত্যাদি); হুক অন্য কিছু ফেরত না দিলে এটাই আসে।

**উদাহরণ:**

```python
class AppError(Exception):
    pass
@event.listens_for(engine, "handle_error")
def convert(ctx):
    if "no such table" in str(ctx.original_exception):
        raise AppError("টেবিল নেই") from ctx.sqlalchemy_exception
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except AppError as e:
    print(e, type(e.__cause__).__name__)   # টেবিল নেই OperationalError
```

### `ExceptionContext.statement` { #exceptioncontext-statement }

**ধরন:** অ্যাট্রিবিউট

যে SQL স্ট্রিং চালাতে গিয়ে এরর।

**উদাহরণ:**

```python
seen = []
event.listen(engine, "handle_error", lambda ctx: seen.append(ctx.statement))
try:
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT * FROM nope")
except exc.DBAPIError:
    pass
print(seen)   # ['SELECT * FROM nope']
```

## DB-API protocol ও সহায়ক { #dbapiconnection-group }

## `DBAPIConnection` { #dbapiconnection }

```python
from sqlalchemy.engine.interfaces import DBAPIConnection
```

টাইপ-হিন্টের জন্য একটি `Protocol`: PEP 249 (DB-API 2.0) অনুযায়ী একটি ড্রাইভার-সংযোগে যা থাকে (`cursor()`, `commit()`, `rollback()`, `close()`)। `conn.connection.dbapi_connection` এমন একটি অবজেক্ট। নিজের ইভেন্ট হুকে টাইপ লিখতে কাজে লাগে।

**উদাহরণ:**

```python
with engine.connect() as conn:
    raw = conn.connection.dbapi_connection
    print(type(raw).__module__, all(hasattr(raw, m) for m in ("cursor", "commit", "rollback", "close")))   # sqlite3 True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dbapiconnection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`close()`](#dbapiconnection-close) | মেথড | সংযোগ বন্ধ। |
| [`commit()`](#dbapiconnection-commit) | মেথড | transaction commit। |
| [`cursor()`](#dbapiconnection-cursor) | মেথড | নতুন cursor। |
| [`rollback()`](#dbapiconnection-rollback) | মেথড | transaction rollback। |

### `DBAPIConnection.close()` { #dbapiconnection-close }

```python
DBAPIConnection.close()
```

**ধরন:** মেথড

সংযোগ বন্ধ।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.close()
print("closed")   # closed
```

### `DBAPIConnection.commit()` { #dbapiconnection-commit }

```python
DBAPIConnection.commit()
```

**ধরন:** মেথড

transaction commit।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.commit(); raw.close()
print("ok")   # ok
```

### `DBAPIConnection.cursor()` { #dbapiconnection-cursor }

```python
DBAPIConnection.cursor(*args, **kwargs)
```

**ধরন:** মেথড

নতুন cursor।

**উদাহরণ:**

```python
raw = d.connect(":memory:")
print(raw.cursor().execute("SELECT 1").fetchone()); raw.close()   # (1,)
```

### `DBAPIConnection.rollback()` { #dbapiconnection-rollback }

```python
DBAPIConnection.rollback()
```

**ধরন:** মেথড

transaction rollback।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.rollback(); raw.close()
print("ok")   # ok
```

## `DBAPICursor` { #dbapicursor }

```python
from sqlalchemy.engine.interfaces import DBAPICursor
```

PEP 249 cursor-এর `Protocol`: `execute()`, `fetchone()`, `description` ইত্যাদি। `before_cursor_execute` ইভেন্টের `cursor` আর্গুমেন্ট এমন একটি অবজেক্ট।

**উদাহরণ:**

```python
raw = d.connect(":memory:")
cur = raw.cursor()
cur.execute("SELECT 1 AS x, 'a' AS y")
print([col[0] for col in cur.description], cur.fetchall())   # ['x', 'y'] [(1, 'a')]
raw.close()
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dbapicursor-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`arraysize`](#dbapicursor-arraysize) | অ্যাট্রিবিউট | `fetchmany()`-এ ডিফল্টে কতটি রো। |
| [`callproc()`](#dbapicursor-callproc) | মেথড | stored procedure চালায় (সব ড্রাইভারে নেই; sqlite3-এ নেই)। |
| [`close()`](#dbapicursor-close) | মেথড | cursor বন্ধ। |
| [`description`](#dbapicursor-description) | প্রপার্টি | ফলের কলামগুলোর বর্ণনা: প্রতিটি কলামের জন্য ৭-টি উপাদানের tuple (প্রথমটি নাম)। |
| [`execute()`](#dbapicursor-execute) | মেথড | একটি SQL চালায়। |
| [`executemany()`](#dbapicursor-executemany) | মেথড | একই SQL অনেক প্যারামিটার-সেট দিয়ে। |
| [`fetchall()`](#dbapicursor-fetchall) | মেথড | বাকি সব রো। |
| [`fetchmany()`](#dbapicursor-fetchmany) | মেথড | পরের `size`টি রো। |
| [`fetchone()`](#dbapicursor-fetchone) | মেথড | পরের একটি রো (না থাকলে `None`)। |
| [`lastrowid`](#dbapicursor-lastrowid) | অ্যাট্রিবিউট | শেষ INSERT-এর রো id (ড্রাইভারভেদে)। |
| [`nextset()`](#dbapicursor-nextset) | মেথড | একাধিক ফল-সেট থাকলে পরেরটিতে যায় (সব ড্রাইভারে নেই)। |
| [`rowcount`](#dbapicursor-rowcount) | প্রপার্টি | শেষ execute-এ কতটি রো বদলেছে (SELECT-এ প্রায়ই `-1`)। |
| [`setinputsizes()`](#dbapicursor-setinputsizes) | মেথড | প্যারামিটারের টাইপ/আকার আগে থেকে জানায় (বেশিরভাগ ড্রাইভারে কিছুই করে না)। |
| [`setoutputsize()`](#dbapicursor-setoutputsize) | মেথড | বড় কলামের বাফার আকার (বেশিরভাগ ড্রাইভারে কিছুই করে না)। |

### `DBAPICursor.arraysize` { #dbapicursor-arraysize }

**ধরন:** অ্যাট্রিবিউট

`fetchmany()`-এ ডিফল্টে কতটি রো।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(raw.cursor().arraysize); raw.close()   # 1
```

### `DBAPICursor.callproc()` { #dbapicursor-callproc }

```python
DBAPICursor.callproc(procname, parameters=Ellipsis)
```

**ধরন:** মেথড

stored procedure চালায় (সব ড্রাইভারে নেই; sqlite3-এ নেই)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(hasattr(raw.cursor(), "callproc")); raw.close()   # False
```

### `DBAPICursor.close()` { #dbapicursor-close }

```python
DBAPICursor.close()
```

**ধরন:** মেথড

cursor বন্ধ।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.cursor().close(); raw.close()
print("ok")   # ok
```

### `DBAPICursor.description` { #dbapicursor-description }

**ধরন:** প্রপার্টি

ফলের কলামগুলোর বর্ণনা: প্রতিটি কলামের জন্য ৭-টি উপাদানের tuple (প্রথমটি নাম)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor(); cur.execute("SELECT 1 AS n")
print(cur.description[0][0]); raw.close()   # n
```

### `DBAPICursor.execute()` { #dbapicursor-execute }

```python
DBAPICursor.execute(operation, parameters=None)
```

**ধরন:** মেথড

একটি SQL চালায়।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(raw.cursor().execute("SELECT ?", (9,)).fetchone()); raw.close()   # (9,)
```

### `DBAPICursor.executemany()` { #dbapicursor-executemany }

```python
DBAPICursor.executemany(operation, parameters)
```

**ধরন:** মেথড

একই SQL অনেক প্যারামিটার-সেট দিয়ে।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor(); cur.execute("CREATE TABLE t (x)")
cur.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (3,)])
print(cur.rowcount); raw.close()   # 3
```

### `DBAPICursor.fetchall()` { #dbapicursor-fetchall }

```python
DBAPICursor.fetchall()
```

**ধরন:** মেথড

বাকি সব রো।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(raw.cursor().execute("SELECT 1 UNION ALL SELECT 2").fetchall()); raw.close()   # [(1,), (2,)]
```

### `DBAPICursor.fetchmany()` { #dbapicursor-fetchmany }

```python
DBAPICursor.fetchmany(size=Ellipsis)
```

**ধরন:** মেথড

পরের `size`টি রো।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(raw.cursor().execute("SELECT 1 UNION ALL SELECT 2").fetchmany(1)); raw.close()   # [(1,)]
```

### `DBAPICursor.fetchone()` { #dbapicursor-fetchone }

```python
DBAPICursor.fetchone()
```

**ধরন:** মেথড

পরের একটি রো (না থাকলে `None`)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(raw.cursor().execute("SELECT 5").fetchone()); raw.close()   # (5,)
```

### `DBAPICursor.lastrowid` { #dbapicursor-lastrowid }

**ধরন:** অ্যাট্রিবিউট

শেষ INSERT-এর রো id (ড্রাইভারভেদে)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor(); cur.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, x)")
cur.execute("INSERT INTO t (x) VALUES (1)"); print(cur.lastrowid); raw.close()   # 1
```

### `DBAPICursor.nextset()` { #dbapicursor-nextset }

```python
DBAPICursor.nextset()
```

**ধরন:** মেথড

একাধিক ফল-সেট থাকলে পরেরটিতে যায় (সব ড্রাইভারে নেই)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); print(hasattr(raw.cursor(), "nextset")); raw.close()   # False
```

### `DBAPICursor.rowcount` { #dbapicursor-rowcount }

**ধরন:** প্রপার্টি

শেষ execute-এ কতটি রো বদলেছে (SELECT-এ প্রায়ই `-1`)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); cur = raw.cursor(); cur.execute("SELECT 1"); print(cur.rowcount); raw.close()   # -1
```

### `DBAPICursor.setinputsizes()` { #dbapicursor-setinputsizes }

```python
DBAPICursor.setinputsizes(sizes)
```

**ধরন:** মেথড

প্যারামিটারের টাইপ/আকার আগে থেকে জানায় (বেশিরভাগ ড্রাইভারে কিছুই করে না)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.cursor().setinputsizes([None]); raw.close()
print("ok")   # ok
```

### `DBAPICursor.setoutputsize()` { #dbapicursor-setoutputsize }

```python
DBAPICursor.setoutputsize(size, column)
```

**ধরন:** মেথড

বড় কলামের বাফার আকার (বেশিরভাগ ড্রাইভারে কিছুই করে না)।

**উদাহরণ:**

```python
raw = d.connect(":memory:"); raw.cursor().setoutputsize(1000, 0); raw.close()
print("ok")   # ok
```

## `DBAPIModule` { #dbapimodule }

```python
from sqlalchemy.engine.interfaces import DBAPIModule
```

ড্রাইভার **মডিউলের** `Protocol` (`sqlite3`, `psycopg` …): `connect()`, `paramstyle` আর PEP 249-এর এরর ক্লাসগুলো। `dialect.dbapi` এমন একটি মডিউল।

**উদাহরণ:**

```python
print(d.dbapi.__name__, d.dbapi.paramstyle, issubclass(d.dbapi.IntegrityError, d.dbapi.Error))   # sqlite3.dbapi2 qmark True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #dbapimodule-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`Error`](#dbapimodule-Error) | অ্যাট্রিবিউট | ড্রাইভারের সব এররের মূল ক্লাস। |
| [`IntegrityError`](#dbapimodule-IntegrityError) | অ্যাট্রিবিউট | নিয়ম-ভাঙার এরর (SQLAlchemy এটিকে `exc.IntegrityError`-এ মোড়ায়)। |
| [`InterfaceError`](#dbapimodule-InterfaceError) | অ্যাট্রিবিউট | ড্রাইভারের নিজের সমস্যা। |
| [`OperationalError`](#dbapimodule-OperationalError) | অ্যাট্রিবিউট | ডেটাবেস চালানোর সমস্যা। |

### `DBAPIModule.Error` { #dbapimodule-Error }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারের সব এররের মূল ক্লাস।

**উদাহরণ:**

```python
print(d.dbapi.Error.__name__)   # Error
```

### `DBAPIModule.IntegrityError` { #dbapimodule-IntegrityError }

**ধরন:** অ্যাট্রিবিউট

নিয়ম-ভাঙার এরর (SQLAlchemy এটিকে `exc.IntegrityError`-এ মোড়ায়)।

**উদাহরণ:**

```python
print(d.dbapi.IntegrityError.__name__)   # IntegrityError
```

### `DBAPIModule.InterfaceError` { #dbapimodule-InterfaceError }

**ধরন:** অ্যাট্রিবিউট

ড্রাইভারের নিজের সমস্যা।

**উদাহরণ:**

```python
print(d.dbapi.InterfaceError.__name__)   # InterfaceError
```

### `DBAPIModule.OperationalError` { #dbapimodule-OperationalError }

**ধরন:** অ্যাট্রিবিউট

ডেটাবেস চালানোর সমস্যা।

**উদাহরণ:**

```python
print(d.dbapi.OperationalError.__name__)   # OperationalError
```

## `DBAPIType` { #dbapitype }

```python
from sqlalchemy.engine.interfaces import DBAPIType
```

ড্রাইভারের টাইপ-অবজেক্টের `Protocol` (PEP 249-এর `STRING`, `NUMBER`, `DATETIME` …): `TypeEngine.get_dbapi_type()` এমন অবজেক্ট দেয়, আর `cursor.description`-এর দ্বিতীয় উপাদান এর সাথে তুলনা করা যায়। শুধু টাইপ-হিন্টের জন্য। সব ড্রাইভারে এগুলো নেই: Python-এর `sqlite3`-এ `STRING` ইত্যাদি নেই, তাই সেখানে `get_dbapi_type()` ডাকলে `AttributeError`।

**উদাহরণ:**

```python
import psycopg
print(String().get_dbapi_type(psycopg), hasattr(d.dbapi, "STRING"))   # STRING False
```

## `AdaptedConnection` { #adaptedconnection }

```python
from sqlalchemy.engine import AdaptedConnection
```

(১.৪.২৪) async ড্রাইভারের (asyncpg, aiosqlite …) সংযোগকে sync DB-API-র মতো দেখানোর মোড়কের মূল ক্লাস। `conn.connection.dbapi_connection` async engine-এ এটি; আসল async সংযোগ `driver_connection`-এ।

**উদাহরণ:**

```python
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_connection
print(issubclass(AsyncAdapt_asyncpg_connection, AdaptedConnection))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #adaptedconnection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`driver_connection`](#adaptedconnection-driver-connection) | প্রপার্টি | ড্রাইভারের আসল সংযোগ অবজেক্ট (যেমন `asyncpg.Connection`)। |
| [`run_async()`](#adaptedconnection-run-async) | মেথড | sync কোডের ভেতর থেকে (যেমন ইভেন্ট হুকে) আসল async সংযোগে একটি coroutine চালায়: `dbapi_conn.run_async(lambda c: c.set_type_codec(...))`। |

### `AdaptedConnection.driver_connection` { #adaptedconnection-driver-connection }

**ধরন:** প্রপার্টি

ড্রাইভারের আসল সংযোগ অবজেক্ট (যেমন `asyncpg.Connection`)।

**উদাহরণ:**

```python
print(isinstance(AdaptedConnection.driver_connection, property))   # True
```

### `AdaptedConnection.run_async()` { #adaptedconnection-run-async }

```python
AdaptedConnection.run_async(fn)
```

**ধরন:** মেথড

sync কোডের ভেতর থেকে (যেমন ইভেন্ট হুকে) আসল async সংযোগে একটি coroutine চালায়: `dbapi_conn.run_async(lambda c: c.set_type_codec(...))`। asyncpg-এ কাস্টম টাইপ নিবন্ধনে কাজে লাগে।

**উদাহরণ:**

```python
print(callable(AdaptedConnection.run_async))   # True
```

## `BindTyping` { #bindtyping }

```python
from sqlalchemy.engine import BindTyping
```

(২.০) bind প্যারামিটারের টাইপ ড্রাইভারকে কীভাবে জানানো হয় (`dialect.bind_typing`)।

**উদাহরণ:**

```python
print(pg.bind_typing.name, sl.bind_typing.name)   # RENDER_CASTS NONE
print(select(users.c.id).where(users.c.id == 1).compile(dialect=pg).string.splitlines()[-1])   # WHERE users.id = %(id_1)s::INTEGER
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bindtyping-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`NONE`](#bindtyping-NONE) | অ্যাট্রিবিউট | কিছুই নয়: ড্রাইভার নিজে বুঝে নেয় (SQLite, MySQL)। |
| [`RENDER_CASTS`](#bindtyping-RENDER-CASTS) | অ্যাট্রিবিউট | SQL-এই cast লিখে দেয় (`%(x)s::INTEGER`): psycopg 3, asyncpg। |
| [`SETINPUTSIZES`](#bindtyping-SETINPUTSIZES) | অ্যাট্রিবিউট | `cursor.setinputsizes()` দিয়ে জানায় (cx_Oracle/oracledb)। |

### `BindTyping.NONE` { #bindtyping-NONE }

**ধরন:** অ্যাট্রিবিউট

কিছুই নয়: ড্রাইভার নিজে বুঝে নেয় (SQLite, MySQL)।

**উদাহরণ:**

```python
print(BindTyping.NONE.value)   # 1
```

### `BindTyping.RENDER_CASTS` { #bindtyping-RENDER-CASTS }

**ধরন:** অ্যাট্রিবিউট

SQL-এই cast লিখে দেয় (`%(x)s::INTEGER`): psycopg 3, asyncpg।

**উদাহরণ:**

```python
print(BindTyping.RENDER_CASTS.value)   # 3
```

### `BindTyping.SETINPUTSIZES` { #bindtyping-SETINPUTSIZES }

**ধরন:** অ্যাট্রিবিউট

`cursor.setinputsizes()` দিয়ে জানায় (cx_Oracle/oracledb)।

**উদাহরণ:**

```python
print(BindTyping.SETINPUTSIZES.value)   # 2
```

## `CacheStats` { #cachestats }

```python
from sqlalchemy.engine.interfaces import CacheStats
```

SQL কম্পাইল-ক্যাশের ফলাফল (`context.cache_hit`), লগে `[cached since ...]`/`[generated in ...]` এর উৎস। `Dialect.CACHE_HIT` ইত্যাদি এরই মান।

**উদাহরণ:**

```python
stmt = select(users.c.name)
with engine.connect() as conn:
    print([conn.execute(stmt).context.cache_hit.name for _ in range(2)])   # ['CACHE_MISS', 'CACHE_HIT']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cachestats-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`CACHE_HIT`](#cachestats-CACHE-HIT) | অ্যাট্রিবিউট | ক্যাশে পাওয়া গেছে। |
| [`CACHE_MISS`](#cachestats-CACHE-MISS) | অ্যাট্রিবিউট | ক্যাশে ছিল না; কম্পাইল হয়ে রাখা হলো। |
| [`CACHING_DISABLED`](#cachestats-CACHING-DISABLED) | অ্যাট্রিবিউট | ক্যাশ বন্ধ। |
| [`NO_CACHE_KEY`](#cachestats-NO-CACHE-KEY) | অ্যাট্রিবিউট | স্টেটমেন্টের cache key নেই। |
| [`NO_DIALECT_SUPPORT`](#cachestats-NO-DIALECT-SUPPORT) | অ্যাট্রিবিউট | ডায়ালেক্ট ক্যাশ সমর্থন করে না। |

### `CacheStats.CACHE_HIT` { #cachestats-CACHE-HIT }

**ধরন:** অ্যাট্রিবিউট

ক্যাশে পাওয়া গেছে।

**উদাহরণ:**

```python
print(CacheStats.CACHE_HIT.value)   # 0
```

### `CacheStats.CACHE_MISS` { #cachestats-CACHE-MISS }

**ধরন:** অ্যাট্রিবিউট

ক্যাশে ছিল না; কম্পাইল হয়ে রাখা হলো।

**উদাহরণ:**

```python
print(CacheStats.CACHE_MISS.value)   # 1
```

### `CacheStats.CACHING_DISABLED` { #cachestats-CACHING-DISABLED }

**ধরন:** অ্যাট্রিবিউট

ক্যাশ বন্ধ।

**উদাহরণ:**

```python
e2 = create_engine("sqlite://", query_cache_size=0)
with e2.connect() as conn:
    print(conn.execute(text("SELECT 1")).context.cache_hit.name)   # CACHING_DISABLED
```

### `CacheStats.NO_CACHE_KEY` { #cachestats-NO-CACHE-KEY }

**ধরন:** অ্যাট্রিবিউট

স্টেটমেন্টের cache key নেই।

**উদাহরণ:**

```python
print(CacheStats.NO_CACHE_KEY.value)   # 3
```

### `CacheStats.NO_DIALECT_SUPPORT` { #cachestats-NO-DIALECT-SUPPORT }

**ধরন:** অ্যাট্রিবিউট

ডায়ালেক্ট ক্যাশ সমর্থন করে না।

**উদাহরণ:**

```python
print(CacheStats.NO_DIALECT_SUPPORT.value)   # 4
```

## `ConnectionEventsTarget` { #connectioneventstarget }

```python
from sqlalchemy.engine.interfaces import ConnectionEventsTarget
```

(২.০) [`ConnectionEvents`](events.md#connectionevents) গ্রহণ করতে পারে এমন অবজেক্টের মূল ক্লাস: `Engine` আর `Connection`। `sqlalchemy.engine.Connectable` এই একই ক্লাস (পুরোনো নাম)। ইভেন্ট টার্গেটের টাইপ-হিন্টে।

**উদাহরণ:**

```python
from sqlalchemy.engine import Connectable
with engine.connect() as conn:
    print(isinstance(engine, ConnectionEventsTarget), isinstance(conn, ConnectionEventsTarget), Connectable is ConnectionEventsTarget)
    # True True True
```
