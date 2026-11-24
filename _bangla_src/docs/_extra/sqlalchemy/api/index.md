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

## যা যা আছে { #bn-contents }

| পেজ | ক্লাস ও ফাংশন | সদস্য সংখ্যা |
| :--- | :--- | :--- |
| [Session API](session.md) | `Session`, `sessionmaker`, `SessionTransaction`, `scoped_session`, `close_all_sessions()`, `make_transient()`, `make_transient_to_detached()`, `object_session()`, `was_deleted()` | ১১০ |
| [Result ও Row API](result.md) | `Result`, `ScalarResult`, `MappingResult`, `TupleResult`, `Row`, `RowMapping`, `CursorResult`, `FrozenResult`, `IteratorResult`, `ChunkedIteratorResult`, `MergedResult`, `FilterResult` | ২০০ |
| [ORM ম্যাপিং API](mapping.md) | `DeclarativeBase`, `DeclarativeBaseNoMeta`, `MappedAsDataclass`, `Mapped`, `WriteOnlyMapped`, `DynamicMapped`, `declared_attr`, `mapped_column()` ও `relationship()`-এর **সব** প্যারামিটার, `backref()`, `foreign()`, `remote()`, `column_property()`, `deferred()`, `query_expression()`, `composite()`, `synonym()`, `synonym_for()`, `validates()`, `reconstructor()`, `declarative_mixin()`, `declarative_base()`, `as_declarative()` | ২৪টি ক্লাস/ফাংশন, ১৬৭টি প্যারামিটার |
| [Registry ও Mapper API](registry.md) | `registry`, `Mapper` (৮৫টি সদস্যের সবগুলো), `configure_mappers()`, `clear_mappers()`, `class_mapper()`, `object_mapper()`, `mapped_as_dataclass()`, `add_mapped_attribute()`, `polymorphic_union()` | ৯৯, আর ৪৮টি প্যারামিটার |
| [Select API](select.md) | `select()`, `Select` (৯৪টি সদস্যের সবগুলো), `union()`, `union_all()`, `intersect()`, `intersect_all()`, `except_()`, `except_all()`, `CompoundSelect`, `Subquery`, `CTE`, `values()`, `Values` | ২৮৪ |
| [Insert, Update, Delete ও text()](dml.md) | `insert()`, `Insert`, `update()`, `Update`, `delete()`, `Delete`, `text()`, `TextClause`, `TextualSelect` | ২৪৯ |
| [Async API](async.md) | `create_async_engine()`, `async_engine_from_config()`, `AsyncEngine`, `AsyncConnection`, `AsyncTransaction`, `async_sessionmaker`, `AsyncSession`, `AsyncSessionTransaction`, `AsyncAttrs`, `async_scoped_session`, `AsyncResult`, `AsyncScalarResult`, `AsyncMappingResult`, `AsyncTupleResult`, `async_object_session()`, `async_session()` | ২২৬ |

## পরের ধাপে যা আসছে { #bn-roadmap }

অফিসিয়াল রেফারেন্সের বাকি অংশ একই নিয়মে ধাপে ধাপে যোগ হবে:

1. ✅ **কুয়েরি ও স্টেটমেন্ট:** `select()`, `insert()`, `update()`, `delete()`, `text()` (যোগ হয়েছে)। `exists()` / `Exists` আর `ScalarSelect` আসবে ৪ নম্বরের সাথে, কারণ এদের সাথে কলামের সব অপারেটরও আছে।
2. ✅ **ORM ম্যাপিং:** `DeclarativeBase`, `Mapped`, `mapped_column()`, `relationship()`-এর সব প্যারামিটার, `registry`, `Mapper` (যোগ হয়েছে)।
3. **লোডিং অপশন:** `selectinload`, `joinedload`, `load_only`, `defer`, `contains_eager`, `with_loader_criteria`, `Load` …
4. **SQL এক্সপ্রেশন:** কলামের অপারেটর (`==`, `in_`, `like` …), `func`, `and_`/`or_`, `case`, `cast`, CTE, window।
5. **স্কিমা ও টাইপ:** `MetaData`, `Table`, `Column`, কনস্ট্রেইন্ট, ইনডেক্স, সব কলাম টাইপ।
6. **Engine, কানেকশন, পুল ও Event:** `create_engine()`-এর সব প্যারামিটার, `Engine`, `Connection`, পুলের ধরন, সব event hook।
7. **এক্সটেনশন, ডায়ালেক্ট ও এক্সেপশন:** hybrid, association proxy, mutable, automap; PostgreSQL / MySQL / SQLite-এর বিশেষ টাইপ ও ফাংশন; সব এক্সেপশন ক্লাস।
