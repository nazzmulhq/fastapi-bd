# SQLAlchemy API রেফারেন্স (সহজ বাংলায়) { #api-reference }

/// note | এই অংশটি কী

অফিসিয়াল [SQLAlchemy ডকুমেন্টেশনের](https://docs.sqlalchemy.org/en/21/) API রেফারেন্স অংশটি, সহজ বাংলায়। প্রতিটি ক্লাসের **প্রতিটি** মেথড, প্রপার্টি ও কনস্ট্রাক্টর প্যারামিটার আছে, প্রতিটির সাথে ব্যাখ্যা আর চালিয়ে দেখা উদাহরণ।

///

গাইডের অধ্যায়গুলো ([Model](../models.md), [CRUD](../crud.md) ইত্যাদি) ধাপে ধাপে **শেখায়**। এই অংশটি হলো **অভিধান**: কোনো মেথড ঠিক কী করে, কোন প্যারামিটার নেয়, কী ফেরত দেয়, তা খুঁজে দেখার জায়গা।

## কীভাবে তৈরি, কেন নির্ভরযোগ্য { #bn-how-built }

* **কিছুই বাদ পড়েনি:** সদস্যের তালিকা হাতে লেখা নয়। SQLAlchemy **2.1**-এর সোর্স কোড থেকে সরাসরি বের করা। কোনো সদস্যের ব্যাখ্যা না থাকলে পেজই তৈরি হয় না।
* **প্রতিটি উদাহরণ চালানো:** উদাহরণগুলো PostgreSQL 16-এ (async উদাহরণ `asyncpg` দিয়ে) আলাদা আলাদা করে চালিয়ে দেখা, আর কমেন্টে লেখা আউটপুট আসল আউটপুটের সাথে মিলিয়ে দেখা।
* **২.১-এর পরিবর্তন চিহ্নিত:** নতুন সদস্যের পাশে "২.১-এ নতুন" লেখা। বাতিলের পথে থাকা (deprecated), পুরোনো (legacy) আর অভ্যন্তরীণ (internal) সদস্য আলাদা করে চিহ্নিত।

## প্রতিটি সদস্য কীভাবে পড়বেন { #bn-how-to-read }

প্রতিটি ক্লাসের শুরুতে একটি **"এক নজরে"** টেবিল থাকে, তারপর প্রতিটি সদস্যের নিজস্ব অংশ:

* **সিগনেচার:** মেথডটি কোন প্যারামিটার নেয়, আর ডিফল্ট মান কী। সামনে `await` থাকলে সেটি coroutine।
* **ধরন:** মেথড, ক্লাস মেথড, প্রপার্টি বা অ্যাট্রিবিউট।
* **ব্যাখ্যা** আর **উদাহরণ**।
* যে সদস্যের কাজ অন্য ক্লাসের সদস্যের হুবহু মতো (যেমন `AsyncSession.get` আর `Session.get`), সেখানে মূল ব্যাখ্যার লিংক দেওয়া আছে।
* অনেক ক্লাস একই প্যারেন্ট থেকে ডজনখানেক সদস্য পায় (যেমন সব এক্সপ্রেশন ক্লাস কলামের ৪৭টি অপারেটর)। সেগুলো প্রতিটি ক্লাসে একটি **ভাঁজ করা বক্সে** লিংকসহ তালিকা করা, যাতে কিছু বাদ না পড়ে আবার পেজও অকারণে লম্বা না হয়।

## যা যা আছে { #bn-contents }

| পেজ | ক্লাস ও ফাংশন | সদস্য সংখ্যা |
| :--- | :--- | :--- |
| [Session API](session.md) | `Session`, `sessionmaker`, `SessionTransaction`, `scoped_session`, `close_all_sessions()`, `make_transient()`, `make_transient_to_detached()`, `object_session()`, `was_deleted()` | ১১০ |
| [MetaData, Table ও Column](schema.md) | `MetaData` (`create_all()`, `reflect()`, `sorted_tables` …), `Table` ও `Column`-এর সব সদস্য আর প্রতিটি প্যারামিটার, `insert_sentinel()`, `sort_tables()`, ২.১-এর `TypedColumns`, `Named`, `CheckFirst` | ১৪ + ৬৯ + ১০৬ |
| [কনস্ট্রেইন্ট, ইনডেক্স ও ডিফল্ট](constraints.md) | `PrimaryKeyConstraint`, `UniqueConstraint`, `CheckConstraint`, `ForeignKeyConstraint`, `ForeignKey`, `Index`, `conv`, `Sequence`, `Identity`, `Computed`, `ColumnDefault`, `DefaultClause`, `FetchedValue` … | ১৫টি ক্লাস |
| [FROM এলিমেন্ট](fromclause.md) | `FromClause`, `Selectable`, `TableClause`, `Join`, `Alias`, `Lateral`, `TableSample`, `TableValuedAlias`, `ColumnCollection` | ৯টি ক্লাস |
| [DDL](ddl.md) | `DDL`, `CreateTable`, `DropTable`, ২.১-এর `CreateTableAs`, `CreateView`, `DropView`, `CreateIndex`, `AddConstraint`, `CreateSchema`, `CreateSequence`, comment DDL … | ২৫টি ক্লাস |
| [কলাম টাইপ](types.md) | `TypeEngine`-এর সব মেথড, সব generic টাইপ (`String`, `Integer`, `Numeric`, `DateTime`, `Enum`, `JSON`, `ARRAY`, `Uuid` …), সব SQL-standard টাইপ (`VARCHAR`, `TIMESTAMP` …), ২.১-এর `OperatorClass` | ৫৩টি ক্লাস |
| [কাস্টম টাইপ](custom-types.md) | `TypeDecorator`, `UserDefinedType`, `ExternalType`, `TypeEngine.Comparator`, `Variant` | ৫টি ক্লাস |
| [Engine, Connection ও URL](engine.md) | `create_engine()`-এর প্রতিটি অপশন, `engine_from_config()`, `create_mock_engine()`, `create_pool_from_url()`, `make_url()`, `Engine`, `Connection`, `Transaction`, `RootTransaction`, `NestedTransaction`, `TwoPhaseTransaction`, `URL`, `CreateEnginePlugin` | ১৭ + ৩১ + ২১ … |
| [কানেকশন পুল](pool.md) | `Pool`, `QueuePool`, `AsyncAdaptedQueuePool`, `NullPool`, `StaticPool`, `SingletonThreadPool`, `AssertionPool`, `PoolProxiedConnection`, `ConnectionPoolEntry`, `ManagesConnection`, `PoolResetState` | ১৪টি ক্লাস/ধ্রুবক |
| [inspect() ও Inspector](inspection.md) | `inspect()`, `Inspector`-এর সব মেথড (২.১-এর `has_multi_table()`-সহ), `ObjectKind`, `ObjectScope` | ৩৯ |
| [Core Event](events.md) | `event.listen()`, `listens_for()`, `remove()`, `contains()`, `PoolEvents`, `ConnectionEvents`, `DialectEvents`, `DDLEvents` | ৪১টি event |
| [ORM Event](orm-events.md) | `SessionEvents`, `MapperEvents`, `InstanceEvents`, `AttributeEvents`, `InstrumentationEvents`, `QueryEvents` | ৬০টি event |
| [Hybrid Attribute](hybrid.md) | `hybrid_property` (`expression`, `setter`, `update_expression`, `inplace` …), `hybrid_method`, `Comparator`, `ExprComparator`, `HybridExtensionType`, `index_property` | ৬টি ক্লাস |
| [Association Proxy](association-proxy.md) | `association_proxy()`, `AssociationProxy`, `AssociationProxyInstance`, `ColumnAssociationProxyInstance`, `ObjectAssociationProxyInstance`, `AmbiguousAssociationProxyInstance`, `AliasedAssociationProxyInstance`, `AssociationProxyExtensionType` | ৮টি ক্লাস/ফাংশন |
| [Mutable ও OrderingList](mutable.md) | `MutableBase`, `Mutable`, `MutableComposite`, `MutableDict`, `MutableList`, `MutableSet`, `ordering_list()`, `OrderingList`, `count_from_0()`, `count_from_1()`, `count_from_n_factory()` | ১১টি ক্লাস/ফাংশন |
| [আরও এক্সটেনশন](ext-misc.md) | automap (`automap_base()`, `AutomapBase`, নামকরণ ফাংশন), `DeferredReflection`, `ConcreteBase`, `AbstractConcreteBase`, `@compiles`, horizontal sharding, serializer, baked query | ২৪টি ক্লাস/ফাংশন |
| [PostgreSQL API](postgresql.md) | upsert (`insert()`, `on_conflict_do_update()`), ২.১-এর `distinct_on()`, `aggregate_order_by`, `array_agg()`, `JSONB`/`JSON` ও অপারেটর, `ARRAY`, `HSTORE`, ফুল-টেক্সট সার্চ ফাংশন, `ExcludeConstraint` | ২৬টি ক্লাস/ফাংশন |
| [PostgreSQL টাইপ](postgresql-types.md) | `Range`, `MultiRange`, range অপারেটর, ১২টি range/multirange টাইপ, `ENUM`, `DOMAIN`, `NamedType`, `CreateEnumType` …, `PGInspector`, `INET`, `CIDR`, `CITEXT`, `MONEY`, `BIT` ও ২.১-এর `BitString`, `INTERVAL` … | ৪৩টি ক্লাস |
| [MySQL ও MariaDB](mysql.md) | upsert (`on_duplicate_key_update()`), ২.১-এর `limit()`, `match()`, `TINYINT` … `BIGINT`, `UNSIGNED`/`charset`, `TINYTEXT` … `LONGTEXT`, `ENUM`, `SET`, `YEAR`, `fsp`, BLOB, `JSON`, `INET4`/`INET6` | ৩৬টি ক্লাস/ফাংশন |
| [SQLite](sqlite.md) | upsert (`on_conflict_do_update()`), তারিখ-সময়ের স্টোরেজ (`DATETIME`, `DATE`, `TIME`), `JSON`, ২.১-এর `JSONB` | ৮টি ক্লাস/ফাংশন |
| [এক্সেপশন ও সতর্কবার্তা](exceptions.md) | `sqlalchemy.exc`-এর সব ৫১টি ক্লাস (`IntegrityError`, `NoResultFound`, `PendingRollbackError`, `MissingGreenlet` …), `sqlalchemy.orm.exc`-এর ১২টি (`DetachedInstanceError`, `StaleDataError` …), ক্লাস-গাছ, FastAPI-তে HTTP কোড | ৬৪টি ক্লাস |
| [Legacy Query API](query.md) | `Query`-এর সব ৯৭টি মেথড ও প্রপার্টি (প্রতিটির ২.০ বিকল্পসহ), `QueryPropertyDescriptor`, `merge_frozen_result()`, `merge_result()`, `contains_alias()`, `AliasOption`, `create_session()`, `FromStatement`, রূপান্তর-টেবিল | ৯৭ + ৭টি ক্লাস/ফাংশন |
| [Relationship Collection](collections.md) | `WriteOnlyCollection`, `AppenderQuery`, `attribute_keyed_dict()`, `column_keyed_dict()`, `keyfunc_mapping()`, `KeyFuncDict`, `collection` ডেকোরেটর, `collection_adapter()`, `CollectionAdapter`, `bulk_replace()`, `InstrumentedList` / `Set` / `Dict` | ১৪টি ক্লাস/ফাংশন |
| [Result ও Row API](result.md) | `Result`, `ScalarResult`, `MappingResult`, `TupleResult`, `Row`, `RowMapping`, `CursorResult`, `FrozenResult`, `IteratorResult`, `ChunkedIteratorResult`, `MergedResult`, `FilterResult` | ২০০ |
| [ORM ম্যাপিং API](mapping.md) | `DeclarativeBase`, `DeclarativeBaseNoMeta`, `MappedAsDataclass`, `Mapped`, `WriteOnlyMapped`, `DynamicMapped`, `declared_attr`, `mapped_column()` ও `relationship()`-এর **সব** প্যারামিটার, `backref()`, `foreign()`, `remote()`, `column_property()`, `deferred()`, `query_expression()`, `composite()`, `synonym()`, `synonym_for()`, `validates()`, `reconstructor()`, `declarative_mixin()`, `declarative_base()`, `as_declarative()` | ২৪টি ক্লাস/ফাংশন, ১৬৭টি প্যারামিটার |
| [Registry ও Mapper API](registry.md) | `registry`, `Mapper` (৮৫টি সদস্যের সবগুলো), `configure_mappers()`, `clear_mappers()`, `class_mapper()`, `object_mapper()`, `mapped_as_dataclass()`, `add_mapped_attribute()`, `polymorphic_union()` | ৯৯, আর ৪৮টি প্যারামিটার |
| [Select API](select.md) | `select()`, `Select` (৯৪টি সদস্যের সবগুলো), `union()`, `union_all()`, `intersect()`, `intersect_all()`, `except_()`, `except_all()`, `CompoundSelect`, `Subquery`, `CTE`, `values()`, `Values` | ২৮৪ |
| [কলাম অপারেটর](operators.md) | Python অপারেটর (`==`, `<`, `+`, `&`, <code>&#124;</code>, `~` …), `ColumnOperators`-এর সব মেথড (`in_()`, `like()`, `ilike()`, `between()`, `is_()`, `contains()`, `regexp_match()`, `op()` …), `QueryableAttribute` (`any()`, `has()`, `of_type()`, `and_()` …) | ৪৭ + ৮২ |
| [SQL এক্সপ্রেশন ফাংশন](expressions.md) | `and_()`, `or_()`, `not_()`, `case()`, `cast()`, `try_cast()`, `type_coerce()`, `literal()`, `literal_column()`, `column()`, `bindparam()`, `null()`, `true()`, `false()`, `tuple_()`, `extract()`, `exists()`, `lateral()`, `lambda_stmt()`, `from_dml_column()`, `tstring()` … | ৪৩টি ফাংশন |
| [func ও SQL ফাংশন](functions.md) | `func`, `FunctionElement` (সব সদস্য), `Function`, `GenericFunction`, তৈরি-করা ৩৫টি ফাংশন (`count`, `sum`, `coalesce`, `rank`, `percentile_cont`, `rollup`, `aggregate_strings` …), `over()`, `within_group()`, `funcfilter()`, `aggregate_order_by()`, `Over`, `WithinGroup`, `FunctionFilter`, `AggregateOrderBy` | ৫৩টি ক্লাস/ফাংশন |
| [SQL এক্সপ্রেশন ক্লাস](elements.md) | `ColumnElement`, `ClauseElement`, `Exists`, `ScalarSelect`, `BinaryExpression`, `BooleanClauseList`, `Label`, `BindParameter`, `ColumnClause`, `Cast`, `Case`, `StatementLambdaElement` … | ২২টি ক্লাস |
| [লোডিং অপশন ও কুয়েরি হেল্পার](loading.md) | `selectinload()`, `joinedload()`, `subqueryload()`, `lazyload()`, `immediateload()`, `noload()`, `raiseload()`, `defaultload()`, `contains_eager()`, `load_only()`, `defer()`, `undefer()`, `undefer_group()`, `with_expression()`, `selectin_polymorphic()`, `with_loader_criteria()`, `Load`, `aliased()`, `with_polymorphic()`, `with_parent()`, `join()`, `outerjoin()`, `Bundle` | ২১টি ফাংশন, ৫১টি সদস্য |
| [Insert, Update, Delete ও text()](dml.md) | `insert()`, `Insert`, `update()`, `Update`, `delete()`, `Delete`, `text()`, `TextClause`, `TextualSelect` | ২৪৯ |
| [Async API](async.md) | `create_async_engine()`, `async_engine_from_config()`, `AsyncEngine`, `AsyncConnection`, `AsyncTransaction`, `async_sessionmaker`, `AsyncSession`, `AsyncSessionTransaction`, `AsyncAttrs`, `async_scoped_session`, `AsyncResult`, `AsyncScalarResult`, `AsyncMappingResult`, `AsyncTupleResult`, `async_object_session()`, `async_session()` | ২২৬ |

## যেভাবে ধাপে ধাপে যোগ হচ্ছে { #bn-roadmap }

অফিসিয়াল রেফারেন্স ধাপে ধাপে যোগ হচ্ছে। প্রথম সাতটি ধাপে সাধারণ কাজের সব API এসেছে; পরের ধাপগুলোতে পুরোনো (legacy) আর ভেতরের (internal) API:

1. ✅ **কুয়েরি ও স্টেটমেন্ট:** `select()`, `insert()`, `update()`, `delete()`, `text()` (যোগ হয়েছে)। `exists()` / `Exists` আর `ScalarSelect` এসেছে ৪ নম্বরের সাথে।
2. ✅ **ORM ম্যাপিং:** `DeclarativeBase`, `Mapped`, `mapped_column()`, `relationship()`-এর সব প্যারামিটার, `registry`, `Mapper` (যোগ হয়েছে)।
3. ✅ **লোডিং অপশন:** `selectinload`, `joinedload`, `load_only`, `defer`, `contains_eager`, `with_loader_criteria`, `Load` … (যোগ হয়েছে)
4. ✅ **SQL এক্সপ্রেশন:** কলামের অপারেটর (`==`, `in_`, `like` …), `func`, `and_`/`or_`, `case`, `cast`, window (যোগ হয়েছে)।
5. ✅ **স্কিমা ও টাইপ:** `MetaData`, `Table`, `Column`, কনস্ট্রেইন্ট, ইনডেক্স, DDL, সব কলাম টাইপ (যোগ হয়েছে)।
6. ✅ **Engine, কানেকশন, পুল ও Event:** `create_engine()`-এর সব প্যারামিটার, `Engine`, `Connection`, পুলের ধরন, `Inspector`, সব event hook (যোগ হয়েছে)।
7. ✅ **এক্সটেনশন, ডায়ালেক্ট ও এক্সেপশন:** hybrid, association proxy, mutable, automap; PostgreSQL / MySQL / SQLite-এর বিশেষ টাইপ ও ফাংশন; সব এক্সেপশন ক্লাস (যোগ হয়েছে)।
8. ✅ **Legacy Query ও Relationship Collection:** `session.query()`-এর সব মেথড ও ২.০ বিকল্প, write-only / dynamic / dict / নিজের collection (যোগ হয়েছে)।
9. **ORM-এর ভেতরের API:** `InstanceState`, `AttributeState`, `ORMExecuteState`, `Relationship`, `ColumnProperty`, `PropComparator` …
10. **Core-এর ভেতরের API:** `Compiled`, `Dialect`, `ExecutionContext`, `ExceptionContext`, `quoted_name`, `custom_op` আর `Select`/`Insert`-এর মূল ক্লাসগুলো।
