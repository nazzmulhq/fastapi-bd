# চিট শিট ও শেখার রোডম্যাপ { #sqlalchemy-cheat-sheet }

/// note | এই পাতায় যা আছে

পুরো গাইডের সবচেয়ে বেশি লাগা সিনট্যাক্স এক জায়গায়: মডেল, CRUD, join, লক। প্রতিটি লাইনের বিস্তারিত ব্যাখ্যা তার নিজের অধ্যায়ে আছে, টেবিলের "কেন" ঘরে সেই ইঙ্গিত দেওয়া। শেষে অফিসিয়াল ডকুমেন্টেশনের লিংক আর শেখার ধাপ।

///

## 51. Cheat Sheet { #s51 }

### 51.1 মডেল { #s51-1 }
```python
# ১. Base
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

# ২. টেবিল
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

# ৩. 1:N রিলেশনশিপ
class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(primary_key=True)
    children: Mapped[list["Child"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", passive_deletes=True, lazy="raise"
    )

class Child(Base):
    __tablename__ = "children"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), index=True)
    parent: Mapped["Parent"] = relationship(back_populates="children", lazy="raise")

# ৪. Eager কুয়েরি
stmt = select(Parent).options(selectinload(Parent.children))
parents = (await session.scalars(stmt)).all()
```

/// tip | পরামর্শ

নতুন প্রজেক্টে এই চারটি অংশ কপি করে শুরু করতে পারেন। মডেলের বিস্তারিত [Model](models.md) অধ্যায়ে, রিলেশনশিপ ও লোডিং [Relationship](relationships.md) অধ্যায়ে।

///

### 51.2 CRUD { #s51-2 }
| অপারেশন | সিনট্যাক্স | কেন |
| :--- | :--- | :--- |
| **একটি তৈরি** | `session.add(obj); await session.commit()` | Unit of work |
| **অনেক তৈরি** | `await session.execute(insert(M).returning(M.id), rows)` | এক রাউন্ড-ট্রিপ |
| **Upsert** | `pg_insert(M).values(...).on_conflict_do_update(...)` | Atomic, idempotent |
| **PK দিয়ে আনা** | `await session.get(M, pk)` | আগে identity map |
| **ফিল্টার** | `await session.scalars(select(M).where(...))` | টাইপড 2.0 API |
| **পেজ (বড়)** | keyset `where(tuple_(M.created_at, M.id) < cursor)` | স্থির খরচ |
| **PUT** | schema থেকে প্রতিটি ফিল্ড অ্যাসাইন | পূর্ণ প্রতিস্থাপন |
| **PATCH** | `model_dump(exclude_unset=True)` লুপ | শুধু পাঠানো ফিল্ড |
| **বাল্ক আপডেট** | `await session.execute(update(M).where(...).values(...))` | কোনো অবজেক্ট লোড হয় না |
| **Atomic inc/dec** | `update(M).values(col=M.col + delta)` | Lost update নয় |
| **Soft delete** | `update(M).where(...).values(is_deleted=True)` | ইতিহাস থাকে |
| **Hard delete** | `await session.delete(obj)` / `delete(M).where(...)` | স্থায়ী |

### 51.3 Join ও related টেবিল { #s51-3 }
| অপারেশন | প্যাটার্ন | কৌশল |
| :--- | :--- | :--- |
| **Inner join** | `select(A, B).join(B, A.id == B.a_id)` | শুধু মিলে যাওয়া রো |
| **Outer join** | `.join(B, A.id == B.a_id, isouter=True)` | বামের সব রো থাকে |
| **Self join** | `P = aliased(A); .join(P, A.parent_id == P.id)` | এক টেবিলের দুই নাম |
| **ফিল্টার করা চাইল্ড** | `.join(A.bs).where(B.x == 1).options(contains_eager(A.bs))` + `.unique()` | শুধু মিলে যাওয়া চাইল্ড যুক্ত |
| **প্যারেন্ট + চাইল্ড ইনসার্ট** | `session.add(parent); await session.flush(); session.add_all(children)` | FK-এর জন্য প্যারেন্ট রো থাকে |
| **প্যারেন্ট + চাইল্ড ডিলিট** | চাইল্ড ডিলিট → প্যারেন্ট ডিলিট | FK ইন্টিগ্রিটি |
| **জাংশন লিংক** | `session.add(Junction(fk1=..., fk2=..., from_date=now))` | সংযোগ তৈরি |
| **জাংশন soft unlink** | `junction.thru_date = now` | অডিট ট্রেইল |
| **জাংশন hard unlink** | `delete(Junction).where(...)` | এন্টিটি অক্ষত |
| **Subtype তৈরি** | বেস add → `flush()` → একই PK-সহ subtype add | Shared-PK 1:1 |
| **Subtype ডিলিট** | subtype ডিলিট → বেস ডিলিট | FK ইন্টিগ্রিটি |

### 51.4 লক ও concurrency { #s51-4 }
| প্রয়োজন | ব্যবহার |
| :--- | :--- |
| স্টক/ব্যালেন্স নিরাপদে কমানো | `update().where(col >= n).values(col=col - n)` |
| পড়ে Python-এ সিদ্ধান্ত নিয়ে লেখা | `session.begin()`-এর ভেতরে `select(...).with_for_update()` |
| অন্য কেউ এডিট করলে ফেইল | `with_for_update(nowait=True)` |
| Worker কিউ | `with_for_update(skip_locked=True)` |
| দীর্ঘ এডিট ফর্ম | `version_id_col` + `StaleDataError`-এ 409 |
| ডুপ্লিকেট সাবমিশন নয় | `UniqueConstraint` / idempotency key |
| বহু-রো নিয়ম | `SERIALIZABLE` + retry decorator |

## 52. অফিশিয়াল ডকুমেন্টেশন ও শেখার রোডম্যাপ { #s52 }

### অফিশিয়াল ডকুমেন্টেশন { #s52-a }
- **ORM overview:** https://docs.sqlalchemy.org/en/20/orm/
- **Declarative tables:** https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
- **Mapping API (`mapped_column`, `relationship`):** https://docs.sqlalchemy.org/en/20/orm/mapping_api.html
- **Basic relationships:** https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- **Relationship loading techniques:** https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- **ORM querying guide:** https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
- **ORM-enabled INSERT / UPDATE / DELETE:** https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html
- **Inheritance mapping:** https://docs.sqlalchemy.org/en/20/orm/inheritance.html
- **AsyncIO extension:** https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Session basics ও transactions:** https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- **Connection pooling:** https://docs.sqlalchemy.org/en/20/core/pooling.html
- **PostgreSQL dialect:** https://docs.sqlalchemy.org/en/20/dialects/postgresql.html
- **2.0 migration guide:** https://docs.sqlalchemy.org/en/20/changelog/migration_20.html

### শেখার ধারাবাহিক ধাপ { #s52-b }
1. `DeclarativeBase`, `Base.metadata` ও naming convention ([§3](models.md#s3))
2. `Mapped` ও `mapped_column()` ([§4](models.md#s4)–[§6](models.md#s6))
3. ডেটা টাইপ, key ও কনস্ট্রেইন্ট ([§5](models.md#s5), [§7](models.md#s7), [§8](models.md#s8))
4. Foreign key, one-to-many ও many-to-one ([§10](relationships.md#s10)–[§12](relationships.md#s12))
5. One-to-one ও many-to-many, association object ([§12](relationships.md#s12)–[§13](relationships.md#s13))
6. Self-referential ট্রি ([§14](relationships.md#s14))
7. Cascade-এর নিয়ম ([§15](relationships.md#s15))
8. Eager loading ও N+1 প্রতিরোধ ([§16](relationships.md#s16)–[§17](relationships.md#s17))
9. Async SQLAlchemy ও FastAPI ইন্টিগ্রেশন ([§19](engine-session.md#s19)–[§20](engine-session.md#s20))
10. Transaction, savepoint ও session internals ([§21](transactions.md#s21)–[§22](transactions.md#s22))
11. Querying: join, CTE, window function ([কুয়েরি](querying.md), [অ্যাডভান্সড কুয়েরি](advanced-queries.md))
12. CRUD, related-table প্যাটার্ন ও repository ([CRUD ১](crud.md), [CRUD ২](crud-update-delete.md), [সম্পর্কিত টেবিল](related-crud.md), [পূর্ণ প্রজেক্ট](fastapi-project.md))
13. Concurrency control ([§47](concurrency.md#s47))
14. Alembic migration ([Alembic](alembic.md)), টেস্টিং ([টেস্টিং](testing.md)) ও প্রোডাকশন চেকলিস্ট ([§49](performance.md#s49))

## পুরো গাইডের পাতাগুলো { #bn-all-pages }

| | অধ্যায় |
| :--- | :--- |
| শুরু | [পরিচিতি](index.md) · [সেটআপ](setup.md) · [প্রথম অ্যাপ](first-app.md) |
| ভিত্তি | [Model](models.md) · [Relationship](relationships.md) · [Engine ও Async Session](engine-session.md) · [Transaction](transactions.md) |
| কুয়েরি | [select() ও JOIN](querying.md) · [অ্যাডভান্সড কুয়েরি](advanced-queries.md) |
| CRUD | [Create ও Read](crud.md) · [Update ও Delete](crud-update-delete.md) · [সম্পর্কিত টেবিল](related-crud.md) |
| প্রজেক্ট | [পূর্ণ FastAPI প্রজেক্ট](fastapi-project.md) · [Alembic](alembic.md) · [টেস্টিং](testing.md) |
| অ্যাডভান্সড | [ম্যাপিং ও Event](advanced-mapping.md) · [Concurrency](concurrency.md) · [পারফরম্যান্স](performance.md) |
| রেফারেন্স | [API রেফারেন্স](api/index.md) · [Session](api/session.md) · [ORM ম্যাপিং](api/mapping.md) · [Registry ও Mapper](api/registry.md) · [Select](api/select.md) · [অপারেটর](api/operators.md) · [এক্সপ্রেশন](api/expressions.md) · [func](api/functions.md) · [এক্সপ্রেশন ক্লাস](api/elements.md) · [লোডিং অপশন](api/loading.md) · [Insert/Update/Delete](api/dml.md) · [Table ও Column](api/schema.md) · [কনস্ট্রেইন্ট](api/constraints.md) · [টাইপ](api/types.md) · [কাস্টম টাইপ](api/custom-types.md) · [DDL](api/ddl.md) · [Result ও Row](api/result.md) · [Async](api/async.md) |

/// check | শেষ কথা

* প্রথমে [প্রথম অ্যাপ](first-app.md)টি নিজের হাতে লিখে চালান, তারপর [পূর্ণ প্রজেক্ট](fastapi-project.md)।
* কোনো কিছু বুঝতে সমস্যা হলে `echo=True` দিয়ে দেখুন SQLAlchemy আসলে কোন SQL চালাচ্ছে। অর্ধেক রহস্য সেখানেই মিটে যায়।
* async-এর তিন নিয়ম কখনো ভুলবেন না: `expire_on_commit=False`, `lazy="raise"`, আর যা লাগবে তা আগেভাগে লোড।

শুভকামনা! 🚀

///
