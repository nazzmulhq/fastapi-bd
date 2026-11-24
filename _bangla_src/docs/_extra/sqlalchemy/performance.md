# পারফরম্যান্স ও প্রোডাকশন { #sqlalchemy-performance }

/// note | এই পেজে যা শিখবেন

* হাজার-লাখ রো লেখার দ্রুততম সঠিক উপায়, আর PostgreSQL `COPY`।
* বিশাল ফলাফল মেমরিতে না এনে স্ট্রিম করা।
* `EXPLAIN ANALYZE` দিয়ে ধীর কুয়েরির কারণ খোঁজা, আর কোন প্যাটার্নে কোন ইনডেক্স।
* প্রোডাকশনে যাওয়ার আগের পূর্ণ চেকলিস্ট, সাধারণ ভুল ও best practice।

///

## 48. Bulk Operation, Streaming ও `EXPLAIN ANALYZE` { #s48 }

### 48.1 বাল্ক রাইট চিট শিট { #s48-1 }

/// tip | উদাহরণ দিয়ে বুঝি

১০,০০০ বস্তা চাল গুদামে নিতে হবে। একটি করে বস্তা সাইকেলে নিয়ে গেলে ১০,০০০ বার যাওয়া-আসা (`session.add()` লুপে)। একটি ট্রাকে সব একবারে নিলে মাত্র কয়েকবার (`insert(Model)` + dict-এর তালিকা)। ডেটাবেসের ক্ষেত্রেও প্রতিটি যাওয়া-আসায় সময় লাগে, তাই বাল্ক অপারেশন দশ থেকে একশো গুণ দ্রুত।

///

| কাজ | দ্রুততম সঠিক পদ্ধতি |
| :--- | :--- |
| ১০ হাজার+ রো ইনসার্ট | `await session.execute(insert(Model), list_of_dicts)` ([§34.2](crud.md#s34-2)) |
| ইনসার্ট করে ID ফেরত | dict-এর তালিকাসহ `insert(Model).returning(Model.id)` |
| Insert-or-update | `pg_insert(Model).on_conflict_do_update(...)` ([§34.4](crud.md#s34-4)) |
| অনেক রো-তে একই পরিবর্তন | `update(Model).where(...).values(...)` ([§36.3](crud-update-delete.md#s36-3)) |
| PK ধরে প্রতি রো-তে আলাদা মান | `await session.execute(update(Model), [{"id": 1, ...}, ...])` ([§36.8](crud-update-delete.md#s36-8)) |
| অনেক রো মোছা | `delete(Model).where(...)` ([§37.2](crud-update-delete.md#s37-2)) |
| ফাইল থেকে লক্ষ লক্ষ রো | raw asyncpg কানেকশন দিয়ে PostgreSQL `COPY` (`copy_records_to_table`) |

৫০ হাজার অবজেক্টের জন্য `session.add_all()` কেন নয়? প্রতিটি অবজেক্ট instrumentation, identity-map হিসাবরক্ষণ ও unit-of-work সর্টিংয়ের মধ্য দিয়ে যায় — বাল্ক স্টেটমেন্টের চেয়ে সহজেই ১০–১০০ গুণ ধীর এবং মেমরিতে অনেক ভারী।

```python
from sqlalchemy import insert, update

async def bulk_insert_order_items(session: AsyncSession, raw_items: list[dict]):
    """raw_items = [{"order_id": "O1", "order_item_seq_id": "00001", "product_id": "P1", ...}, ...]"""
    result = await session.execute(
        insert(OrderItem).returning(OrderItem.order_id, OrderItem.order_item_seq_id),
        raw_items,
    )
    await session.commit()
    return result.all()

async def bulk_update_item_statuses(session: AsyncSession, order_ids: list[str], new_status: str):
    await session.execute(
        update(OrderItem)
        .where(OrderItem.order_id.in_(order_ids))
        .values(status_id=new_status)
        .execution_options(synchronize_session="fetch")   # লোড করা অবজেক্ট সিঙ্কে রাখে
    )
    await session.commit()
```
খুব বড় ব্যাচ টুকরো করুন (যেমন প্রতি স্টেটমেন্টে ৫,০০০–১০,০০০ রো), যাতে transaction ও মেমরি সীমিত থাকে।

### 48.2 Raw asyncpg কানেকশন ব্যবহার (`COPY`-এর জন্য) { #s48-2 }
```python
async def copy_rows(session: AsyncSession, rows: list[tuple]):
    conn = await session.connection()
    raw = await conn.get_raw_connection()
    await raw.driver_connection.copy_records_to_table(
        "audit_log", records=rows, columns=["log_id", "action", "created_at"]
    )
```

/// info | কোডটি সহজ ভাষায়

`COPY` হলো PostgreSQL-এ ডেটা ঢোকানোর সবচেয়ে দ্রুত উপায়, সাধারণ INSERT-এর চেয়েও অনেক দ্রুত। SQLAlchemy এটা সরাসরি দেয় না, তাই আসল `asyncpg` কানেকশন বের করে তার `copy_records_to_table()` ডাকা হয়েছে। আমাদের পরীক্ষায় ১০০০টি রো এক ডাকেই ঢুকেছে।

খেয়াল রাখুন: এটা ORM-এর বাইরে চলে, তাই Python `default`, event কিছুই চলে না। প্রতিটি কলামের মান নিজেকে দিতে হবে।

///

### 48.3 বিশাল রেজাল্ট সেট স্ট্রিমিং { #s48-3 }
৫,০০,০০০ রো-তে `.all()` সবগুলোকে একসাথে মেমরিতে আনে। তার বদলে server-side cursor দিয়ে স্ট্রিম করুন:
```python
from typing import AsyncGenerator

async def stream_large_order_export(session: AsyncSession) -> AsyncGenerator[OrderHeader, None]:
    stmt = (
        select(OrderHeader)
        .order_by(OrderHeader.order_date)
        .execution_options(yield_per=1000)      # প্রতিবার ১,০০০ রো আনা
    )
    result = await session.stream_scalars(stmt)
    async for order in result:
        yield order
```

/// info | FastAPI-তে CSV স্ট্রিম করা

```python
import csv
import io

from fastapi.responses import StreamingResponse


@router.get("/orders/export.csv")
async def export_orders(session: SessionDep):
    async def rows():
        yield "order_id,order_code,total_amount\n"
        stmt = (
            select(Order.order_id, Order.order_code, Order.total_amount)   # শুধু কলাম, অবজেক্ট নয়
            .order_by(Order.order_id)
            .execution_options(yield_per=1000)
        )
        result = await session.stream(stmt)
        async for row in result:
            buf = io.StringIO()
            csv.writer(buf).writerow(row)
            yield buf.getvalue()

    return StreamingResponse(rows(), media_type="text/csv")
```

লাখ রো হলেও সার্ভারের মেমরিতে একসাথে থাকে মাত্র ১০০০টি, আর ক্লায়েন্ট প্রথম লাইন সাথে সাথে পেতে শুরু করে।

এটা কাজ করে কারণ FastAPI **0.118.0** থেকে `yield`-সহ ডিপেন্ডেন্সির শেষের অংশ (সেশন বন্ধ) চলে রেসপন্স পুরো পাঠানোর **পরে**। পুরোনো 0.106–0.117 ভার্সনে সেশন স্ট্রিমিং শুরুর আগেই বন্ধ হয়ে যেত। আমরা ২৫০০ রো দিয়ে চালিয়ে দেখেছি, সব লাইন ঠিকঠাক এসেছে।

///

- পুরো iteration জুড়ে খোলা transaction/কানেকশন লাগে — মাঝপথে commit করবেন না।
- অবজেক্টগুলো তবুও identity map-এ জমে; এক্সপোর্টের জন্য **কলাম** সিলেক্ট করুন (`select(OrderHeader.order_id, ...)`) অথবা প্রতি চাঙ্কে `session.expunge_all()` কল করুন (`result.partitions()` দিয়ে iterate করে)।
- FastAPI-তে `StreamingResponse`-এর সাথে মিলিয়ে বাফার ছাড়াই CSV/NDJSON পাঠান।

### 48.4 Python থেকে `EXPLAIN (ANALYZE, BUFFERS)` { #s48-4 }
```python
from sqlalchemy import text

async def explain_analyze_statement(session: AsyncSession, statement) -> str:
    """যেকোনো SQLAlchemy স্টেটমেন্টে EXPLAIN ANALYZE চালানো (শুধু dev/test)।"""
    compiled = statement.compile(
        dialect=session.bind.dialect,
        compile_kwargs={"literal_binds": True},
    )
    result = await session.execute(text(f"EXPLAIN (ANALYZE, BUFFERS) {compiled}"))
    return "\n".join(row[0] for row in result.all())
```

/// info | `EXPLAIN`-এর ফল পড়া, সহজ ভাষায়

২৫০০ অর্ডারের টেবিলে `select(Order).where(Order.customer_id > 0, Order.order_id > 2490)`-এর আসল ফল:

```
Index Scan using pk_orders on orders  (cost=0.28..8.48 rows=10 width=49) (actual time=0.006..0.008 rows=10 loops=1)
  Index Cond: (order_id > 2490)
  Filter: (customer_id > 0)
  Buffers: shared hit=3
Planning Time: 0.241 ms
Execution Time: 0.025 ms
```

* `Index Scan using pk_orders`: primary key-র ইনডেক্স দিয়ে সরাসরি শেষের ১০টি রো-তে চলে গেছে। ভালো খবর।
* `Index Cond` = ইনডেক্স দিয়ে খোঁজা শর্ত; `Filter` = রো পাওয়ার পর বাকি শর্ত মেলানো।
* `rows=10` (অনুমান) আর `actual ... rows=10` (আসল) কাছাকাছি, মানে PostgreSQL-এর পরিসংখ্যান ঠিক আছে।
* `Buffers: shared hit=3`: মাত্র ৩টি পাতা পড়েছে, সবগুলো মেমরি থেকে (`hit`)। `read` থাকলে ডিস্ক থেকে, যা ধীর।

বিপদের লক্ষণ: বড় টেবিলে `Seq Scan` (পুরো টেবিল শুরু থেকে শেষ পর্যন্ত পড়া), আর ফেরত রো-র চেয়ে অনেক বড় `Rows Removed by Filter`। তখন `WHERE`-এর কলামে ইনডেক্স দরকার।

///

/// danger | বিপদ

`EXPLAIN ANALYZE` স্টেটমেন্টটি আসলেই **চালায়** — DML হলে এমন transaction-এ মুড়ুন যা rollback করবেন। `literal_binds` মানগুলো SQL টেক্সটে বসিয়ে দেয়; টেস্টের বাইরে অবিশ্বস্ত ইনপুটের সাথে কখনো ব্যবহার করবেন না।

///

যা খুঁজবেন: বড় টেবিলে `Seq Scan` (ইনডেক্স নেই), ফেরত রো-র চেয়ে অনেক বেশি `Rows Removed by Filter`, বিশাল outer row count-সহ nested loop, এবং `Buffers: shared read` (ডিস্ক) বনাম `hit` (ক্যাশ)।

### 48.5 এই গাইডের প্যাটার্নগুলোর জন্য জরুরি ইনডেক্সিং নির্দেশিকা { #s48-5 }
| কুয়েরি প্যাটার্ন | ইনডেক্স |
| :--- | :--- |
| Join / `selectinload`-এ ব্যবহৃত FK কলাম | প্রতিটি FK কলামে ইনডেক্স দিন (PostgreSQL নিজে থেকে দেয় না) |
| Keyset pagination `ORDER BY created_at DESC, id DESC` | `Index("ix", Order.created_at.desc(), Order.order_id.desc())` |
| Soft delete + ফিল্টার | `WHERE NOT is_deleted` partial index |
| JSONB containment | GIN ইনডেক্স |
| Full-text search | সংরক্ষিত `tsvector`-এ GIN |
| `LATERAL` "সর্বশেষ চাইল্ড" | Composite `(parent_id, seq DESC)` |
| কিউ `SKIP LOCKED` | `(status, priority DESC, created_at)` partial `WHERE status = 'QUEUED'` |

## 49. প্রোডাকশন আর্কিটেকচার চেকলিস্ট { #s49 }

/// tip | পরামর্শ

এই টেবিলটি প্রিন্ট করে বা বুকমার্ক করে রাখুন। প্রোডাকশনে যাওয়ার আগে প্রতিটি লাইন মিলিয়ে নিন। প্রতিটি লাইনের পেছনে কোনো না কোনো প্রজেক্টের সত্যিকারের দুর্ঘটনা আছে।

///

| ক্যাটাগরি | সেটিং / অনুশীলন | কেন |
| :--- | :--- | :--- |
| **Async নিরাপত্তা** | `expire_on_commit=False` | Commit-এর পর পড়তে গিয়ে `MissingGreenlet` নয় |
| **Async নিরাপত্তা** | প্রতিটি `relationship()`-এ `lazy="raise"` | লুকানো N+1 / ইমপ্লিসিট I/O জোরালোভাবে ফেইল করে |
| **Async নিরাপত্তা** | `response_model` যা সিরিয়ালাইজ করে সব eager-load | সিরিয়ালাইজেশন কখনো I/O চালায় না |
| **Session** | `autoflush=False`, স্পষ্ট `flush()` | ভ্যালিডেশনের মাঝে অপ্রত্যাশিত INSERT নয় |
| **Session** | প্রতি রিকোয়েস্ট / টাস্কে একটি সেশন; কনকারেন্ট টাস্কে কখনো শেয়ার নয় | `AsyncSession` কনকারেন্সি-নিরাপদ নয় |
| **Pool sizing** | `(pool_size + max_overflow) × প্রসেস` < DB `max_connections` | কানেকশন ফুরিয়ে যাওয়া রোধ |
| **Socket স্বাস্থ্য** | `pool_pre_ping=True`, `pool_recycle=1800` | Idle drop-এর পর ভাঙা সকেট এরর নয় |
| **Timeout** | `statement_timeout`, `command_timeout`, `pool_timeout` | অনিয়ন্ত্রিত কুয়েরি চিরকাল কানেকশন ধরে রাখতে পারে না |
| **Migration** | `MetaData(naming_convention=...)` + Alembic; প্রোডাকশনে `create_all()` নয় | পূর্বানুমেয়, রিভিউযোগ্য মাইগ্রেশন |
| **টাকা** | `Numeric` + `Decimal`, কখনো `Float` নয় | নির্ভুল হিসাব |
| **সময়** | `DateTime(timezone=True)`, UTC-তে সংরক্ষণ | DST / অফসেট বাগ নয় |
| **Bulk write** | `session.execute(insert(Model), list_of_dicts)` | লুপে `add()`-এর চেয়ে ১০–১০০ গুণ দ্রুত |
| **বড় read** | `yield_per` + `stream_scalars`, অথবা কলাম সিলেক্ট | OOM নয় |
| **Pagination** | বড় টেবিলে keyset + composite index | প্রতি পেজে স্থির খরচ |
| **Concurrency** | Atomic SQL / `FOR UPDATE` / version কলাম / unique constraint ([§47](concurrency.md#s47)) | Lost update বা ডুপ্লিকেট নয় |
| **Retry** | পুরো transaction ঘিরে `40001` / `40P01`-এর retry decorator | Serialization failure ও ডেডলক সামলানো |
| **Worker** | স্বল্পমেয়াদি সেশন বা প্রতি ব্যাচে `expunge_all()` | Identity-map মেমরি লিক নয় |
| **Read scaling** | শুধু-পড়ার এন্ডপয়েন্টে replica engine; read-your-writes-এ primary | Primary-র বোঝা কমানো |
| **Observability** | Slow-query event hook, `application_name`, হট কুয়েরির জন্য CI-তে `EXPLAIN` | রিগ্রেশন আগেভাগে ধরা |
| **Logging** | প্রোডাকশনে `echo=False` | stdout লগিং ধীর এবং ডেটা ফাঁস করে |

## 50. সাধারণ ভুল ও Best Practice { #s50 }

### 50.1 সাধারণ ভুলসমূহ { #s50-1 }
1. **`ForeignKey` ছাড়া `relationship()`** — `relationship()` শুধু নেভিগেশন কনফিগার করে; ইন্টিগ্রিটি আসে FK থেকে।
2. **চাইল্ডের FK-তে `unique=True` ছাড়া 1:1** — ডেটাবেস একাধিক "one-to-one" চাইল্ড ঢুকতে দেয়।
3. **টাকার হিসাবে `Float`** — `Numeric(18, 4)` / `Decimal` ব্যবহার করুন।
4. **প্রোডাকশনে `create_all()`** — Alembic ব্যবহার করুন।
5. **FastAPI থেকে লোড না হওয়া রিলেশনশিপ রিটার্ন** — সিরিয়ালাইজেশনে `MissingGreenlet` বা `lazy="raise"` এরর।
6. **`AsyncSession`-এর সাথে `expire_on_commit=True`** — commit-এর পর প্রতিটি অ্যাট্রিবিউট পড়তে গিয়ে I/O করার চেষ্টা।
7. **Python-এ কাউন্টার read-modify-write** — lost update; `update().values(col=col + n)` ব্যবহার করুন।
8. **`.unique()` ছাড়া কালেকশনে `joinedload()`** — প্যারেন্ট ডুপ্লিকেট / 2.0-তে এরর।
9. **বাল্ক `update()`/`delete()` থেকে ORM cascade, event বা `version_id_col` আশা করা** — এগুলো unit of work এড়িয়ে যায়।
10. **`asyncio.gather()` টাস্কগুলোর মধ্যে একটি `AsyncSession` শেয়ার** — সেশন কনকারেন্ট ব্যবহারের জন্য নিরাপদ নয়।
11. **এক্সেপশনের পর `rollback()` ভুলে যাওয়া** — সেশন ব্যর্থ অবস্থায় থেকে যায় (`PendingRollbackError`)।
12. **`ON DELETE CASCADE` না থাকলেও চাইল্ডের আগে প্যারেন্ট মোছা।**
13. Many-to-many "unlink"-এ **জাংশন রো-র বদলে এন্টিটি মুছে ফেলা।**
14. **`version` কলামের উপরে `__mapper_args__ = {"version_id_col": version}` লেখা** — ইমপোর্টের সময় `NameError`।
15. **কোটি রো-র টেবিলে `OFFSET` pagination** — প্রতি পেজে খরচ বাড়তে থাকে।

### 50.2 Best practice { #s50-2 }
- সর্বত্র আধুনিক `Mapped[]` + `mapped_column()`; প্রতিটি রিলেশনশিপ টাইপ করুন।
- প্রথম দিনেই `MetaData(naming_convention=...)` কনফিগার করুন।
- সবসময় স্পষ্ট `back_populates`।
- কালেকশন → `selectinload`; স্কেলার → `joinedload`; বাকি সব `lazy="raise"`।
- মালিকানাধীন চাইল্ডের জন্য `cascade="all, delete-orphan"` + `passive_deletes=True` + `ondelete="CASCADE"`।
- একাধিক টেবিলে লেখা `async with session.begin():`-এ মুড়ুন।
- প্রতিটি কনস্ট্রেইন্টের নাম দিন যাতে `IntegrityError`-কে API এররে ম্যাপ করা যায়।
- ব্যাচ কাজে স্টেটমেন্ট-ভিত্তিক DML; বিজনেস লজিকে ORM অবজেক্ট।
- লোকালি `echo=True` চালু করে প্রতিটি এন্ডপয়েন্টের কুয়েরি সংখ্যা দেখুন।
- হট এন্ডপয়েন্টের কুয়েরি সংখ্যা assert করে এমন টেস্ট লিখুন।

/// check | সংক্ষেপে মনে রাখুন

* অনেক রো লিখতে `session.execute(insert(Model), list_of_dicts)`; ফাইল থেকে লাখ রো হলে `COPY`।
* বড় ফলাফল `stream()` / `stream_scalars()` + `yield_per`; এক্সপোর্টে অবজেক্ট নয়, কলাম।
* ধীর কুয়েরিতে আন্দাজ নয়, `EXPLAIN (ANALYZE, BUFFERS)`।
* প্রতিটি FK কলামে ইনডেক্স; keyset pagination-এ composite ইনডেক্স।
* প্রোডাকশনের আগে §49-এর চেকলিস্ট।

///

**পরের ধাপ:** সব জরুরি সিনট্যাক্স এক পাতায় দেখুন [চিট শিট](cheat-sheet.md)-এ।
