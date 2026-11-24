# SQLAlchemy 2.0 + FastAPI: সম্পূর্ণ গাইড { #sqlalchemy }

/// note | এই অংশে যা শিখবেন

* SQLAlchemy ও ORM কী, আর FastAPI-র সাথে কেন এটি সবচেয়ে জনপ্রিয় জুটি।
* শূন্য থেকে শুরু করে মডেল, রিলেশনশিপ, কুয়েরি, CRUD, ট্রানজ্যাকশন ও async সেশন।
* একটি পূর্ণাঙ্গ FastAPI প্রজেক্ট, Alembic দিয়ে মাইগ্রেশন আর pytest দিয়ে টেস্ট।
* প্রোডাকশনের বিষয়: কানেকশন পুল, race condition ঠেকানো, পারফরম্যান্স ও চেকলিস্ট।

///

এই অংশটি **SQLAlchemy 2.0 + FastAPI**-এর একটি A থেকে Z গাইড, সহজ বাংলায়। প্রতিটি অধ্যায়ে আগে সহজ ভাষায় ধারণাটি বোঝানো হয়েছে, তারপর চলমান কোড, আর শেষে মনে রাখার মতো সংক্ষেপ।

/// check | সব কোড পরীক্ষা করা

এই গাইডের উদাহরণগুলো **SQLAlchemy 2.0** ও **2.1**, **FastAPI**, **Pydantic v2**, **asyncpg** ও **PostgreSQL 16** দিয়ে আসলেই চালিয়ে দেখা হয়েছে। মূল গাইডে পাওয়া কয়েকটি বাগ (যেমন `WriteOnlyMapped`-এর annotation, `ConcreteBase`-এর ইমপোর্ট) এখানে ঠিক করে দেওয়া হয়েছে। শেখার অধ্যায়গুলোর ছোট উদাহরণ SQLite দিয়েও চলে।

///

## এই গাইডে কী কী আছে { #bn-guide-map }

| ধাপ | অধ্যায় | কী শিখবেন |
| :--- | :--- | :--- |
| ১ | [ইনস্টল ও প্রজেক্ট সেটআপ](setup.md) | প্যাকেজ, ডেটাবেস, কানেকশন URL, `.env`, ফোল্ডার কাঠামো |
| ২ | [প্রথম অ্যাপ: ধাপে ধাপে](first-app.md) | ১৫ মিনিটে একটি পূর্ণ CRUD API, প্রতিটি লাইনের ব্যাখ্যা |
| ৩ | [Model, Column ও Schema](models.md) | `DeclarativeBase`, `Mapped[]`, `mapped_column()`, কলামের টাইপ, কনস্ট্রেইন্ট |
| ৪ | [Relationship](relationships.md) | ফরেন কি, 1:N, 1:1, N:M, cascade, eager loading, N+1 সমস্যা |
| ৫ | [Engine ও Async Session](engine-session.md) | কানেকশন পুল, `AsyncSession`, `MissingGreenlet`, FastAPI ডিপেন্ডেন্সি |
| ৬ | [Transaction ও Session-এর ভেতরের কাজ](transactions.md) | commit, rollback, savepoint, identity map, flush |
| ৭ | [কুয়েরি: select() ও JOIN](querying.md) | `select()`, ফিল্টার, রেজাল্ট মেথড, সব ধরনের JOIN |
| ৮ | [অ্যাডভান্সড কুয়েরি](advanced-queries.md) | CTE, recursive tree, window function, subquery, JSONB, full-text search |
| ৯ | [CRUD ১: Create ও Read](crud.md) | একক ও বাল্ক insert, upsert, ফিল্টার, pagination |
| ১০ | [CRUD ২: Update ও Delete](crud-update-delete.md) | PUT, PATCH, বাল্ক আপডেট, optimistic lock, soft delete |
| ১১ | [সম্পর্কিত টেবিলে CRUD](related-crud.md) | প্যারেন্ট-চাইল্ড, জাংশন টেবিল, সাবটাইপ টেবিল, এরর হ্যান্ডলিং |
| ১২ | [পূর্ণ FastAPI প্রজেক্ট](fastapi-project.md) | লেয়ার করা প্রজেক্ট, জেনেরিক repository, router |
| ১৩ | [Alembic দিয়ে মাইগ্রেশন](alembic.md) | স্কিমার ভার্সন কন্ট্রোল, autogenerate, upgrade/downgrade |
| ১৪ | [টেস্টিং](testing.md) | pytest, প্রতি টেস্টে rollback, ডিপেন্ডেন্সি override, N+1 টেস্ট |
| ১৫ | [অ্যাডভান্সড ম্যাপিং ও Event](advanced-mapping.md) | inheritance, hybrid property, event, কাস্টম টাইপ |
| ১৬ | [Concurrency](concurrency.md) | race condition ঠেকানোর ৫টি উপায় |
| ১৭ | [পারফরম্যান্স ও প্রোডাকশন](performance.md) | বাল্ক অপারেশন, স্ট্রিমিং, `EXPLAIN`, চেকলিস্ট, সাধারণ ভুল |
| ১৮ | [চিট শিট](cheat-sheet.md) | এক পাতায় সব জরুরি সিনট্যাক্স |
| ১৯ | [API রেফারেন্স](api/index.md) | প্রতিটি ক্লাস, মেথড ও প্রপার্টি, উদাহরণসহ (অফিসিয়াল রেফারেন্সের সহজ বাংলা রূপ) |

## কীভাবে পড়বেন { #bn-how-to-read }

| আপনি যদি… | এই ক্রমে পড়ুন |
| :--- | :--- |
| SQLAlchemy-তে একদম নতুন হন | [সেটআপ](setup.md) → [প্রথম অ্যাপ](first-app.md) → [Model](models.md) → [Relationship](relationships.md) → [CRUD ১](crud.md) |
| FastAPI-তে এন্ডপয়েন্ট বানাতে চান | [Async Session](engine-session.md) → [CRUD ১](crud.md) ও [CRUD ২](crud-update-delete.md) → [পূর্ণ প্রজেক্ট](fastapi-project.md) |
| `MissingGreenlet` বা N+1 এরর ডিবাগ করছেন | [লোডিং স্ট্র্যাটেজি](relationships.md#s16), [N+1](relationships.md#s17), [MissingGreenlet](engine-session.md#s20) |
| বড় এন্টারপ্রাইজ (ERP-ধাঁচের) স্কিমা নিয়ে কাজ করেন | [রেফারেন্স মডেল](querying.md#s25) → [কুয়েরি](querying.md) → [সম্পর্কিত টেবিলে CRUD](related-crud.md) |
| প্রোডাকশনের জন্য টিউন করছেন | [Engine](engine-session.md) → [Concurrency](concurrency.md) → [পারফরম্যান্স](performance.md) |

## শুরুর আগে যা জানা দরকার { #bn-prerequisites }

* **Python-এর মৌলিক বিষয়**: ফাংশন, ক্লাস, `async`/`await`। `async` নিয়ে সন্দেহ থাকলে আগে [Concurrency এবং async / await](../async.md) পেজটি দেখে নিন।
* **টাইপ হিন্ট**: `int`, `str | None`, `list[str]`। দেখুন [Python টাইপ পরিচিতি](../python-types.md)।
* **FastAPI-র শুরুর টিউটোরিয়াল**: পাথ অপারেশন, রিকোয়েস্ট বডি, ডিপেন্ডেন্সি। দেখুন [টিউটোরিয়াল - ইউজার গাইড](../tutorial/index.md)।
* **SQL**: জানা থাকলে ভালো, তবে বাধ্যতামূলক নয়। প্রতিটি জায়গায় SQLAlchemy কোন SQL বানায় তা দেখানো হয়েছে।

/// tip | পরামর্শ

FastAPI-র নিজের টিউটোরিয়ালে [SQL (রিলেশনাল) ডেটাবেস](../tutorial/sql-databases.md) পেজে **SQLModel** দিয়ে একটি ছোট উদাহরণ আছে। SQLModel আসলে SQLAlchemy-র ওপরেই তৈরি। এই গাইডে আমরা সরাসরি SQLAlchemy 2.0 শিখব, যাতে বড় ও জটিল প্রজেক্টেও পুরো নিয়ন্ত্রণ আপনার হাতে থাকে।

///

## কোড লেখার নিয়ম { #bn-code-conventions }

পুরো গাইডে এই নিয়মগুলো মেনে কোড লেখা হয়েছে:

* `session` মানে সবসময় একটি `AsyncSession`, আর প্রতিটি ডেটাবেস কল `await` করা হয়।
* মডেলগুলো [Model অধ্যায়ের §3](models.md#s3)-এ বানানো `Base` ক্লাস থেকে তৈরি।
* কোডের ভেতরের নাম (ক্লাস, ফাংশন, কলাম) ইংরেজিতে, শুধু কমেন্ট বাংলায়।
* ধরে নেওয়া স্ট্যাক: SQLAlchemy **2.0** (typed, declarative), **AsyncSession** + `asyncpg`, **PostgreSQL**, **FastAPI**, **Pydantic v2**।
* লেখার মধ্যে **§২০** ধরনের চিহ্ন মানে "২০ নম্বর সেকশন"। এগুলোতে ক্লিক করলে সেই সেকশনে চলে যাবেন।
* অফিসিয়াল রেফারেন্স: [https://docs.sqlalchemy.org/en/20/](https://docs.sqlalchemy.org/en/20/)

## 1. SQLAlchemy ও ORM কী? { #s1 }

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন আপনি বাংলায় কথা বলেন, আর ডেটাবেস বোঝে শুধু SQL ভাষা। **ORM** হলো একজন দোভাষী। আপনি Python-এ বলেন "১ নম্বর ইউজারকে এনে দাও", দোভাষী সেটাকে `SELECT * FROM users WHERE id = 1` বানিয়ে ডেটাবেসকে বলে। উত্তর এলে আবার Python অবজেক্ট বানিয়ে আপনার হাতে দেয়।

///

**SQLAlchemy** হলো Python ইকোসিস্টেমের সবচেয়ে জনপ্রিয় SQL Toolkit এবং **Object Relational Mapper (ORM)**।

ORM রিলেশনাল ডেটাবেসের টেবিল ও রো-কে Python-এর ক্লাস ও অবজেক্টে রূপান্তর করে। ফলে SQL স্ট্রিং জোড়া না লাগিয়ে টাইপড Python অবজেক্ট দিয়ে কাজ করা যায়; SQLAlchemy নিজেই SQL তৈরি, প্যারামিটারাইজ ও এক্সিকিউট করে।

```sql
-- Raw SQL
SELECT * FROM users WHERE id = 1;
```
```python
# আধুনিক SQLAlchemy 2.0 Async ORM
user = await session.get(User, 1)
```

| Python ধারণা | ডেটাবেস ধারণা | উদাহরণ |
| :--- | :--- | :--- |
| **Class** | **Table** | `User` ক্লাস ↔ `users` টেবিল |
| **Object / Instance** | **Row** | `user1 = User(...)` ↔ একটি রেকর্ড |
| **Attribute** | **Column** | `user.email` ↔ `email` কলাম |
| **Object Relationship** | **Foreign Key Join** | `user.orders` ↔ `orders.user_id = users.id` |
| **ORM Session** | **Unit of Work / Transaction** | `session.add()`, `session.commit()` |

/// info | ডেটাবেসের কয়েকটি মূল শব্দ

* **টেবিল (table)**: Excel শিটের মতো। যেমন `users` টেবিলে সব ইউজারের তথ্য।
* **রো (row)**: টেবিলের একটি লাইন, মানে একজন ইউজারের পুরো তথ্য।
* **কলাম (column)**: টেবিলের একটি ঘর বা ফিল্ড, যেমন `email`।
* **প্রাইমারি কী (primary key)**: প্রতিটি রো-র অনন্য পরিচয়, সাধারণত `id`। দুটি রো-র কখনো একই হয় না।
* **ফরেন কি (foreign key)**: অন্য টেবিলের কোনো রো-র দিকে নির্দেশ। যেমন `orders.user_id` বলে দেয় অর্ডারটি কোন ইউজারের।
* **SQL**: ডেটাবেসের সাথে কথা বলার ভাষা।

আরও শব্দের সহজ মানে পাবেন [সহজ শব্দকোষ](../learn/glossary.md) পেজে।

///

## 2. আর্কিটেকচার: Core বনাম ORM, এবং 2.0-তে কী বদলেছে { #s2 }

### 2.1 স্তরভিত্তিক কম্পোনেন্ট আর্কিটেকচার { #s2-1 }

SQLAlchemy-র দুটি স্তর — **Core** ও **ORM**। 2.0-তে এ দুটি একীভূত: ORM সরাসরি Core SQL Expression Language-এর (একই `select()`, `insert()`, `update()`, `delete()`) উপর চলে, তাই আলাদা কোনো "ORM query language" আর নেই।

```
+-----------------------------------------------------------------------------------+
|                                SQLAlchemy 2.0 ORM                                 |
|   DeclarativeBase   |   Mapped / mapped_column()   |   Session / Unit of Work     |
|   Identity Map      |   Relationship Loaders       |   Mapper Events / Hybrids    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                                SQLAlchemy 2.0 Core                                |
|   SQL Expression Language (select, insert, update, delete, func, cte, window)     |
|   Schema / Metadata Engine (MetaData, Table, Column, Constraints, Indexes)         |
|   Compiled Statement LRU Cache                                                    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           Engine & Execution Layer                                |
|   Engine / AsyncEngine      |   Connection / AsyncConnection                      |
|   Connection Pool (QueuePool / AsyncAdaptedQueuePool / NullPool / StaticPool)     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                              Dialect & DBAPI Layer                                |
|   Dialect Compiler (PostgreSQL, MySQL, SQLite, Oracle, MSSQL)                     |
|   DBAPI Driver (asyncpg, psycopg, psycopg2, asyncmy, aiosqlite, ...)              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                               Database Server (RDBMS)                             |
+-----------------------------------------------------------------------------------+
```

/// info | ছবিটি সহজ ভাষায়

ওপর থেকে নিচে পড়ুন:

1. **ORM**: আপনি এখানে কাজ করেন। Python ক্লাস (মডেল), অবজেক্ট আর `Session`।
2. **Core**: ORM আপনার কাজকে `select()`, `insert()` ইত্যাদি SQL এক্সপ্রেশনে বদলায়।
3. **Engine ও Pool**: ডেটাবেসের সাথে কানেকশন খোলে, আর বারবার ব্যবহারের জন্য একটি "পুল"-এ জমা রাখে।
4. **Dialect ও DBAPI ড্রাইভার**: PostgreSQL, MySQL বা SQLite, যার যে SQL ভাষা, সেই রূপে লিখে ড্রাইভার (যেমন `asyncpg`) দিয়ে পাঠায়।
5. **ডেটাবেস সার্ভার**: আসল কাজ করে উত্তর ফেরত পাঠায়।

ফলে একই Python কোড PostgreSQL, MySQL বা SQLite-এ সামান্য বদলেই চলে।

///

### 2.2 পুরোনো 1.x বনাম আধুনিক 2.0 { #s2-2 }

| বৈশিষ্ট্য | পুরোনো SQLAlchemy 1.x | আধুনিক SQLAlchemy 2.0 |
| :--- | :--- | :--- |
| **Query সিনট্যাক্স** | `session.query(User).filter(...)` | `session.scalars(select(User).where(...))` |
| **Model অ্যাট্রিবিউট** | `id = Column(Integer, primary_key=True)` | `id: Mapped[int] = mapped_column(primary_key=True)` |
| **Type checking** | ডায়নামিক অ্যাট্রিবিউট (Mypy ব্যর্থ) | Pyright / Mypy-সহ পূর্ণ PEP 484 টাইপিং |
| **Async সাপোর্ট** | থার্ড-পার্টি হ্যাক বা sync র‍্যাপিং | ফার্স্ট-ক্লাস `AsyncEngine`, `AsyncSession` |
| **Autocommit** | লাইব্রেরি-লেভেলের ঐচ্ছিক autocommit | **Commit as you go**: স্পষ্ট transaction বাধ্যতামূলক |
| **Bulk operation** | `bulk_save_objects()`, `bulk_insert_mappings()` | `session.execute(insert(Model), [dicts])` |
| **বড় collection** | `lazy="dynamic"` | `WriteOnlyMapped` / `lazy="write_only"` |
| **Statement caching** | প্রতি কলে নতুন করে কম্পাইল | স্বয়ংক্রিয় LRU compiled-SQL cache |

/// note | পুরোনো টিউটোরিয়াল দেখলে

ইন্টারনেটে অনেক টিউটোরিয়ালে `session.query(User).filter(...)` বা `Column(Integer, primary_key=True)` দেখবেন। এগুলো **1.x** যুগের লেখা। এখনো কিছুটা চলে, কিন্তু নতুন কোডে এই গাইডের **2.0** ধরন (`select()`, `Mapped[]`, `mapped_column()`) ব্যবহার করুন। এতে টাইপ চেকিং, অটোকমপ্লিশন আর async সব ঠিকমতো কাজ করে।

///

/// check | সংক্ষেপে মনে রাখুন

* SQLAlchemy একটি SQL টুলকিট ও ORM। ক্লাস = টেবিল, অবজেক্ট = রো, অ্যাট্রিবিউট = কলাম।
* 2.0-তে ORM আর Core একই `select()` / `insert()` / `update()` / `delete()` ব্যবহার করে।
* নতুন কোডে সবসময় 2.0 ধরন: `Mapped[]`, `mapped_column()`, `select()`, `AsyncSession`।

///

**পরের ধাপ:** [ইনস্টল ও প্রজেক্ট সেটআপ](setup.md) দিয়ে শুরু করুন।
