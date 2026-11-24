# CRUD ১: Create ও Read { #sqlalchemy-crud }

/// note | এই পেজে যা শিখবেন

* SQLAlchemy 2.0-তে CRUD-এর দুটি পথ: অবজেক্ট দিয়ে (unit of work) আর স্টেটমেন্ট দিয়ে (Core DML)।
* `Order` / `OrderItem` রেফারেন্স মডেল ও Pydantic v2 স্কিমা।
* **Create**: একটি রো, হাজার রো একসাথে, প্যারেন্ট + চাইল্ড একসাথে, upsert।
* **Read**: primary key দিয়ে, ডায়নামিক ফিল্টার, offset ও keyset pagination, eager loading, স্ট্রিমিং।

///

**CRUD** মানে ডেটার চারটি মৌলিক কাজ। প্রতিটি কাজ HTTP, SQL আর SQLAlchemy-তে কীভাবে মেলে:

| কাজ | HTTP মেথড | SQL | SQLAlchemy (অবজেক্ট) | SQLAlchemy (স্টেটমেন্ট) |
| :--- | :--- | :--- | :--- | :--- |
| **C**reate (তৈরি) | `POST` | `INSERT` | `session.add(obj)` | `insert(Model)` |
| **R**ead (পড়া) | `GET` | `SELECT` | `session.get(Model, id)` | `select(Model)` |
| **U**pdate (বদলানো) | `PUT` / `PATCH` | `UPDATE` | `obj.field = value` | `update(Model)` |
| **D**elete (মোছা) | `DELETE` | `DELETE` | `session.delete(obj)` | `delete(Model)` |

এই পেজে C ও R, আর পরের পেজ [CRUD ২](crud-update-delete.md)-তে U ও D।

## 32. 2.0-এর CRUD দৃষ্টিভঙ্গি ও Golden Rules { #s32 }

1.x-এ CRUD নির্ভর করত `session.query(Model)` এবং লোড করা ইনস্ট্যান্স পরিবর্তনের উপর। 2.0-এ প্রতিটি অপারেশন হয় অবজেক্টের উপর একটি **ORM unit-of-work** কাজ, নয়তো একই সেশনের মাধ্যমে চালানো একটি **Core DML স্টেটমেন্ট**।

```
                    +------------------------------------+
                    |        FastAPI HTTP Request        |
                    +------------------------------------+
                                      |
                     [Pydantic v2 ingestion & validation]
                                      |
                                      v
                    +------------------------------------+
                    |        Async CRUD Repository       |
                    +------------------------------------+
                                      |
       +------------------------------+------------------------------+
       |                              |                              |
       v                              v                              v
[Instance ORM operations]     [Core DML expressions]     [Direct bulk operations]
   session.add(entity)           select(Model).where()      insert(Model).values()
   session.delete(entity)        update(Model).where()      update(Model).where()
   session.flush()               delete(Model).where()      delete(Model).where()
       |                              |                              |
       +------------------------------+------------------------------+
                                      |
                                      v
                    +------------------------------------+
                    |      SQLAlchemy Identity Map       |
                    |    & Unit of Work Flush Engine     |
                    +------------------------------------+
                                      |
                                      v
                    +------------------------------------+
                    |    PostgreSQL / driver (asyncpg)   |
                    +------------------------------------+
```

### অবজেক্ট অপারেশন নাকি স্টেটমেন্ট — কীভাবে বাছবেন { #s32-a }
| পরিস্থিতি | ব্যবহার করুন |
| :--- | :--- |
| একটি রো, বিজনেস রুল, ইভেন্ট, রিলেশনশিপ | ORM অবজেক্ট: `add()`, অ্যাট্রিবিউট সেট, `delete()` |
| হাজার হাজার রো, একই পরিবর্তন | Core DML: `where()`-সহ `insert()`, `update()`, `delete()` |
| একসাথে বহু রিকোয়েস্টে কাউন্টার/ব্যালেন্স | SQL এক্সপ্রেশনসহ Core `update()` ([§36.4](crud-update-delete.md#s36-4), [§47.2](concurrency.md#s47-2)) |
| লেখা মানগুলো ফেরত দরকার | `.returning(...)` |

/// tip | উদাহরণ দিয়ে বুঝি

* **অবজেক্ট পথ** হলো দর্জির কাছে একটি একটি করে জামা বানানো: প্রতিটির মাপ আলাদা, যত্ন নিয়ে, নিয়ম মেনে (event, cascade, ভ্যালিডেশন সব চলে)।
* **স্টেটমেন্ট পথ** হলো কারখানায় একসাথে হাজার জামা কাটা: দ্রুত, কিন্তু প্রতিটির জন্য আলাদা যত্ন নেই।

একটি অর্ডার নেওয়া → অবজেক্ট। "৩০ দিনের পুরোনো সব PENDING অর্ডার বাতিল করো" → স্টেটমেন্ট।

///

### Async CRUD-এর ৩টি Golden Rule { #s32-b }
1. সেশন ফ্যাক্টরিতে **`expire_on_commit=False`**, যাতে commit-এর পরও অবজেক্ট পড়া যায়।
2. রিলেশনশিপে **`lazy="raise"`**, যাতে ভুলবশত synchronous I/O ডেভেলপমেন্টেই ধরা পড়ে।
3. ব্যাচ পরিবর্তনের জন্য **স্টেটমেন্ট-ভিত্তিক DML** (`update()`, `delete()`), যাতে রো কখনো Python-এ লোড না হয়।

## 33. রেফারেন্স ডোমেইন: `Order` / `OrderItem` মডেল ও Pydantic v2 Schema { #s33 }

CRUD অধ্যায়গুলোতে একটি ছোট integer-key ডোমেইন ব্যবহৃত হয়েছে। [সম্পর্কিত টেবিলে CRUD](related-crud.md) অধ্যায় একই ধারণা OFBiz-এর string-key মডেলে ([§25](querying.md#s25)) প্রয়োগ করে।

### 33.1 SQLAlchemy মডেল { #s33-1 }
```python
# app/models/order.py
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    order_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)   # নাম হবে uq_orders_order_code
    status: Mapped[str] = mapped_column(String(20), default="PENDING", index=True, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)            # optimistic locking
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True, nullable=False)  # soft delete
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

    __mapper_args__ = {
        "version_id_col": version,   # UPDATE-এ স্বয়ংক্রিয় ভার্সন চেক
        "eager_defaults": True,      # INSERT/UPDATE-এর পরপরই সার্ভারে তৈরি মান (created_at, updated_at) RETURNING দিয়ে আনে
    }

class OrderItem(Base):
    __tablename__ = "order_items"

    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    product_sku: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items", lazy="raise")
```

/// info | মডেলটি সহজ ভাষায়

* `order_code`-এ `unique=True` (সাথে `index=True` নয়)। কারণ দুটো একসাথে দিলে SQLAlchemy একটি **ইউনিক ইনডেক্স** বানায়, যার নাম `ix_orders_order_code`। তখন [§41.1](related-crud.md#s41-1)-এর মতো কোড ভুলভাবে `uq_orders_order_code` খুঁজবে। শুধু `unique=True` দিলে PostgreSQL-এ ইউনিক কনস্ট্রেইন্ট `uq_orders_order_code` হয়, আর সেটার জন্য ইনডেক্স এমনিতেই তৈরি হয়ে যায়।
* `version` + `version_id_col`: প্রতিটি UPDATE-এ ভার্সন এক বাড়ে আর মিলিয়ে দেখা হয় ([§36.5](crud-update-delete.md#s36-5))।
* `eager_defaults: True`: `created_at` (`server_default`) আর `updated_at` (`onupdate=func.now()`) ডেটাবেসে তৈরি হয়। এটা থাকলে INSERT/UPDATE-এর সাথেই `RETURNING` দিয়ে মানগুলো ফেরত আসে। না থাকলে UPDATE-এর পর `order.updated_at` পড়তে গেলে async-এ `MissingGreenlet` আসে (আমরা চালিয়ে দেখেছি)।
* `is_deleted`: soft delete-এর জন্য ([§37.4](crud-update-delete.md#s37-4))।
* `items` সম্পর্কে `lazy="raise"`: ভুলবশত lazy load হলে সাথে সাথে এরর।

///

### 33.2 Pydantic v2 schema { #s33-2 }
```python
# app/schemas/order.py
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# --- OrderItem ---
class OrderItemBase(BaseModel):
    product_sku: str = Field(..., max_length=50)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    item_id: int
    order_id: int
    model_config = ConfigDict(from_attributes=True)    # ORM অবজেক্ট থেকে পড়ে

# --- Order ---
class OrderBase(BaseModel):
    customer_id: int
    order_code: str = Field(..., max_length=32)

class OrderCreate(OrderBase):
    items: list[OrderItemCreate] = Field(default_factory=list)

class OrderUpdateFull(BaseModel):
    """HTTP PUT: পরিবর্তনযোগ্য সব ফিল্ড বাধ্যতামূলক।"""
    status: str
    total_amount: Decimal

class OrderUpdatePartial(BaseModel):
    """HTTP PATCH: সব ফিল্ড ঐচ্ছিক।"""
    status: Optional[str] = None
    total_amount: Optional[Decimal] = None
    is_deleted: Optional[bool] = None

class OrderResponse(OrderBase):
    order_id: int
    status: str
    total_amount: Decimal
    version: int
    created_at: datetime
    updated_at: Optional[datetime]
    items: list[OrderItemResponse] = []
    model_config = ConfigDict(from_attributes=True)
```

/// info | এত স্কিমা কেন?

একটি মডেলের জন্য কয়েকটি স্কিমা, কারণ প্রতিটি কাজে ক্লায়েন্ট আলাদা জিনিস পাঠায় বা পায়:

| স্কিমা | কখন | বিশেষত্ব |
| :--- | :--- | :--- |
| `OrderCreate` | `POST` | `order_id` নেই (ডেটাবেস বানাবে), `items` থাকতে পারে |
| `OrderUpdateFull` | `PUT` | সব পরিবর্তনযোগ্য ফিল্ড বাধ্যতামূলক |
| `OrderUpdatePartial` | `PATCH` | সব ঐচ্ছিক |
| `OrderResponse` | রেসপন্স | `order_id`, `version`, `created_at` সহ; `from_attributes=True` |

এতে নিরাপত্তাও বাড়ে: ক্লায়েন্ট `version` বা `created_at` পাঠালেও `OrderCreate`-এ সেই ফিল্ড নেই বলে তা উপেক্ষিত হয়। FastAPI টিউটোরিয়ালের [অতিরিক্ত মডেল](../tutorial/extra-models.md) পেজে এই কৌশল আরও আছে।

///

/// warning | গুরুত্বপূর্ণ

`OrderResponse.items` থাকার কারণে Pydantic `order.items` পড়ে। `lazy="raise"` থাকলে এন্ডপয়েন্টকে **অবশ্যই** items লোড করতে হবে (`selectinload(Order.items)`) অথবা মেমরিতে সদ্য তৈরি করে থাকতে হবে — নইলে সিরিয়ালাইজেশনে এরর হবে।

///

## 34. CREATE: Single, Bulk, Nested ও Upsert { #s34 }

### 34.1 একক এন্টিটি { #s34-1 }
```python
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate

async def create_single_order(session: AsyncSession, data: OrderCreate) -> Order:
    new_order = Order(
        customer_id=data.customer_id,
        order_code=data.order_code,
        status="PENDING",
        total_amount=Decimal("0.00"),
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)      # সার্ভারে তৈরি মান (created_at …) লোড করে
    return new_order
```

/// info | কোডটি সহজ ভাষায়

1. `Order(...)`: মেমরিতে একটি অবজেক্ট (transient)।
2. `session.add(new_order)`: সেশনের তালিকায় যোগ (pending)। এখনো SQL যায়নি।
3. `await session.commit()`: `INSERT INTO orders ... RETURNING order_id, created_at` চলে, তারপর `COMMIT`।
4. `await session.refresh(new_order)`: রো-টি আবার পড়ে আনে। `eager_defaults` থাকলে এটা ঐচ্ছিক, তবে ট্রিগারের মতো অন্য কিছু ডেটাবেসে মান বদলালে কাজে লাগে।

///

Commit-এর আগেই তৈরি হওয়া PK দরকার (যেমন চাইল্ড বা অডিট রো তৈরির জন্য)? `await session.flush()` — `new_order.order_id` পূর্ণ হয় এবং transaction খোলা থাকে।

### 34.2 `RETURNING`-সহ বাল্ক insert { #s34-2 }
`session.add()` লুপে চালালে হাজার হাজার ট্র্যাক করা অবজেক্ট তৈরি হয়। তার বদলে একটি মাল্টি-রো INSERT পাঠান:
```python
from typing import Any
from sqlalchemy import insert

async def bulk_create_orders(session: AsyncSession, orders_data: list[dict[str, Any]]) -> list[int]:
    """এক রাউন্ড-ট্রিপে অনেক রো ইনসার্ট করে তৈরি হওয়া ID ফেরত দেয়।"""
    result = await session.execute(
        insert(Order).returning(Order.order_id),
        orders_data,                        # dict-এর তালিকা → ORM bulk INSERT (insertmanyvalues)
    )
    await session.commit()
    return list(result.scalars().all())
```

/// info | কোডটি সহজ ভাষায়

```python
ids = await bulk_create_orders(session, [
    {"customer_id": 2, "order_code": "B0"},
    {"customer_id": 2, "order_code": "B1"},
    {"customer_id": 2, "order_code": "B2"},
])
print(ids)   # [2, 3, 4]
```

* dict-এর তালিকা দেওয়ায় SQLAlchemy সবগুলো এক বা কয়েকটি বড় `INSERT ... VALUES (...), (...), (...) RETURNING order_id`-এ পাঠায়।
* `status`, `total_amount`, `version`-এর Python `default` নিজেই বসে যায়।
* কোনো ORM অবজেক্ট তৈরি হয় না, তাই মেমরি আর সময় দুটোই অনেক কম লাগে।

///

দুটি লেখার ধরন আছে:
- `session.execute(insert(Model), list_of_dicts)` — **ORM bulk insert**: Python-side `default` প্রয়োগ করে, দক্ষভাবে ব্যাচ করে, `RETURNING` সাপোর্ট করে। **এটিই পছন্দনীয়।**
- `session.execute(insert(Model).values(list_of_dicts))` — একটি literal মাল্টি-VALUES স্টেটমেন্ট; ছোট তালিকায় ঠিক আছে, কিন্তু একটি বিশাল SQL স্ট্রিং তৈরি করে।

কোনোটিই ORM ইভেন্ট চালায় না বা রিলেশনশিপ cascade করে না।

### 34.3 প্যারেন্ট + চাইল্ড একসাথে, atomic-ভাবে { #s34-3 }
Unit of work INSERT-এর ক্রম ঠিক করে এবং FK নিজেই বসিয়ে দেয়:
```python
from app.models.order import OrderItem

async def create_order_with_items(session: AsyncSession, data: OrderCreate) -> Order:
    order = Order(
        customer_id=data.customer_id,
        order_code=data.order_code,
        status="PENDING",
        total_amount=sum(i.quantity * i.unit_price for i in data.items),
        items=[                                   # কনস্ট্রাকশনের সময়ই কালেকশন সেট
            OrderItem(product_sku=i.product_sku, quantity=i.quantity, unit_price=i.unit_price)
            for i in data.items
        ],
    )
    session.add(order)          # 'save-update' cascade প্রতিটি চাইল্ডকেও যুক্ত করে
    await session.commit()      # INSERT orders → INSERT order_items (FK স্বয়ংক্রিয়ভাবে বসে)
    return order
```

/// info | কোডটি সহজ ভাষায়

আপনি কোথাও `order_id` লেখেননি, তবু আইটেমগুলো সঠিক অর্ডারে যুক্ত হয়:

```sql
INSERT INTO orders (...) VALUES (...) RETURNING order_id, created_at   -- order_id = 9
INSERT INTO order_items (order_id, product_sku, ...) VALUES (9, 'X', ...) RETURNING item_id
COMMIT
```

unit of work দেখে যে আইটেমগুলো অর্ডারের ওপর নির্ভরশীল, তাই আগে অর্ডার ঢোকায়, নতুন `order_id` নিয়ে আইটেমে বসায়। সব এক ট্রানজ্যাকশনে, তাই একটি আইটেম ব্যর্থ হলে অর্ডারও থাকবে না।

///

কালেকশনটি মেমরিতে পূর্ণ করা হয়েছে এবং `expire_on_commit=False`, তাই `lazy="raise"` থাকলেও commit-এর পর `order.items` পড়া যায়।

### 34.4 Upsert (`INSERT … ON CONFLICT`) { #s34-4 }
Idempotent "ইনসার্ট করো, ইউনিক key আগে থেকে থাকলে আপডেট করো" — atomic এবং race-মুক্ত:
```python
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert   # sqlite: sqlalchemy.dialects.sqlite.insert

async def upsert_order_status(session: AsyncSession, customer_id: int, order_code: str, status: str) -> None:
    stmt = pg_insert(Order).values(
        customer_id=customer_id,
        order_code=order_code,
        status=status,
        total_amount=Decimal("0.00"),
    )
    # ON CONFLICT (order_code) DO UPDATE SET status = EXCLUDED.status, updated_at = now()
    stmt = stmt.on_conflict_do_update(
        index_elements=[Order.order_code],
        set_={"status": stmt.excluded.status, "updated_at": func.now()},
    )
    await session.execute(stmt)
    await session.commit()
```

/// tip | উদাহরণ দিয়ে বুঝি

**Upsert** = "**up**date অথবা in**sert**"। ফোনের কন্টাক্টে নম্বর সেভ করার মতো: নম্বরটা আগে না থাকলে নতুন কন্টাক্ট, থাকলে পুরোনোটাই হালনাগাদ।

Python-এ "আগে খুঁজি, না পেলে ঢোকাই" লিখলে দুটি রিকোয়েস্ট একসাথে এলে দুজনেই "নেই" দেখে দুবার ঢোকাতে চাইবে। `ON CONFLICT` পুরো কাজটা ডেটাবেসে একটি মাত্র ধাপে করে, তাই কোনো ফাঁক থাকে না।

* `stmt.excluded.status`: যে নতুন মানটি ঢোকানোর চেষ্টা হয়েছিল (`EXCLUDED`)।
* `index_elements=[Order.order_code]`: কোন ইউনিক কলামে সংঘর্ষ হলে update হবে।

///

বিভিন্ন রূপ:
- `on_conflict_do_nothing(index_elements=[...])` — না থাকলে তবেই ইনসার্ট।
- `index_elements`-এর বদলে `constraint="uq_orders_order_code"` — নামযুক্ত কনস্ট্রেইন্ট টার্গেট করা।
- `on_conflict_do_update`-এ `where=...` — শর্ত পূরণ হলে তবেই আপডেট।
- জমা-হওয়া upsert: `set_={"stock_count": Inventory.stock_count + stmt.excluded.stock_count}`।
- Composite conflict target: `index_elements=["user_login_id", "user_pref_type_id"]` (যেমন ইউজার প্রেফারেন্স)।
- প্রভাবিত ID ফেরত পেতে `.returning(Order.order_id)` যোগ করুন।

## 35. READ: Lookup, Dynamic Filter, Pagination, Eager Loading, Streaming { #s35 }

### 35.1 Primary-key দিয়ে খোঁজা { #s35-1 }
```python
async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    # এই সেশনে আগেই লোড হয়ে থাকলে identity-map থেকে সাথে সাথে ফেরত দেয়
    return await session.get(Order, order_id)
```

/// info | `get()` বিশেষ কেন?

`session.get()` আগে identity map দেখে। একই রিকোয়েস্টে অবজেক্টটি আগেই লোড হয়ে থাকলে **ডেটাবেসে যায়ই না**। শুধু primary key দিয়ে খুঁজলে এটাই সবচেয়ে দ্রুত ও সহজ। composite key হলে tuple দিন: `await session.get(OrderItem, ("ORD_1001", "00001"))`।

///

`session.get(Order, order_id, options=[selectinload(Order.items)])` loader অপশন যোগ করে; `with_for_update=True` রো লক করে।

### 35.2 অন্য key দিয়ে একক রেকর্ড { #s35-2 }
```python
from sqlalchemy import select

async def get_order_by_code(session: AsyncSession, code: str) -> Order | None:
    stmt = select(Order).where(Order.order_code == code, Order.is_deleted.is_(False))
    # একাধিক রো মিললে scalar_one_or_none() MultipleResultsFound এরর দেয়
    return (await session.execute(stmt)).scalar_one_or_none()
```

### 35.3 ডায়নামিক মাল্টি-ক্রাইটেরিয়া ফিল্টারিং { #s35-3 }
```python
from decimal import Decimal
from typing import Optional

async def filter_orders(
    session: AsyncSession,
    customer_id: Optional[int] = None,
    statuses: Optional[list[str]] = None,
    min_amount: Optional[Decimal] = None,
    search_code: Optional[str] = None,
) -> list[Order]:
    stmt = select(Order).where(Order.is_deleted.is_(False))

    if customer_id is not None:
        stmt = stmt.where(Order.customer_id == customer_id)
    if statuses:
        stmt = stmt.where(Order.status.in_(statuses))
    if min_amount is not None:
        stmt = stmt.where(Order.total_amount >= min_amount)
    if search_code:
        stmt = stmt.where(Order.order_code.ilike(f"%{search_code}%"))   # মান bind হয়, SQL-এ জোড়া হয় না

    stmt = stmt.order_by(Order.created_at.desc())
    return list((await session.scalars(stmt)).all())
```

/// info | কোডটি সহজ ভাষায়

ক্লায়েন্ট যে ফিল্টারগুলো পাঠায় শুধু সেগুলোই কুয়েরিতে যোগ হয়। `select()` অপরিবর্তনীয় (immutable), তাই প্রতিবার `stmt = stmt.where(...)` লিখে নতুন স্টেটমেন্ট নিতে হয়।

FastAPI এন্ডপয়েন্টে এভাবে ব্যবহার করুন:

```python
@router.get("/orders/search", response_model=list[OrderResponse])
async def search_orders(
    session: SessionDep,
    customer_id: int | None = None,
    statuses: Annotated[list[str] | None, Query()] = None,    # ?statuses=PAID&statuses=SHIPPED
    min_amount: Decimal | None = None,
    q: str | None = None,
):
    orders = await filter_orders(session, customer_id, statuses, min_amount, q)
    ...
```

`f"%{search_code}%"` দেখে ভয় পাবেন না। মানটি SQL-এর ভেতরে জোড়া লাগানো হয় না, আলাদা প্যারামিটার হিসেবে যায়। তাই SQL injection সম্ভব নয়।

///

### 35.4 Pagination: offset বনাম keyset { #s35-4 }

/// tip | উদাহরণ দিয়ে বুঝি

* **Offset pagination** = বইয়ের পৃষ্ঠা নম্বর। "৫০০ নম্বর পৃষ্ঠায় যাও" বললে আগের ৪৯৯ পৃষ্ঠা উল্টে যেতে হয়। যত পেছনের পৃষ্ঠা, তত সময়।
* **Keyset pagination** = বুকমার্ক। "যেখানে থেমেছিলাম, তার পর থেকে" বললে সরাসরি সেখানে চলে যাওয়া যায়। ১ম পৃষ্ঠা আর ১০,০০০তম পৃষ্ঠা, দুটোই সমান দ্রুত।

///

#### A. Offset pagination (ছোট/মাঝারি টেবিল, "N নম্বর পেজে যাও") { #s35-4-a }
```python
async def get_orders_offset_paginated(
    session: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[Order], int]:
    base = select(Order).where(Order.is_deleted.is_(False))

    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()

    data_stmt = base.order_by(Order.order_id.desc()).offset((page - 1) * page_size).limit(page_size)
    records = (await session.scalars(data_stmt)).all()
    return list(records), total
```

#### B. Keyset (cursor) pagination (বড় টেবিল, infinite scroll) { #s35-4-b }
`OFFSET 100000 LIMIT 20` দিলে PostgreSQL ১,০০,০০০ রো পড়ে ফেলে দেয় — পেজ নম্বর যত বাড়ে খরচ তত বাড়ে। Keyset pagination ইনডেক্স ব্যবহার করে সরাসরি শেষ দেখা অবস্থানে চলে যায়, তাই প্রতিটি পেজের খরচ সমান (একটি index seek, O(log N))।
```python
from datetime import datetime
from sqlalchemy import and_, or_

async def get_orders_keyset_paginated(
    session: AsyncSession,
    last_created_at: Optional[datetime],
    last_id: Optional[int],
    limit: int = 20,
) -> list[Order]:
    """(created_at DESC, order_id DESC)-এর উপর ইনডেক্স প্রয়োজন।"""
    stmt = select(Order).where(Order.is_deleted.is_(False))

    if last_created_at is not None and last_id is not None:
        stmt = stmt.where(
            or_(
                Order.created_at < last_created_at,
                and_(Order.created_at == last_created_at, Order.order_id < last_id),
            )
        )
        # PostgreSQL row-value সংক্ষিপ্ত রূপ, একই অর্থ:
        # stmt = stmt.where(tuple_(Order.created_at, Order.order_id) < (last_created_at, last_id))

    stmt = stmt.order_by(Order.created_at.desc(), Order.order_id.desc()).limit(limit)
    return list((await session.scalars(stmt)).all())
```

/// info | কোডটি সহজ ভাষায়

প্রথম পেজে cursor নেই, তাই সর্বশেষ ২০টি আসে। ক্লায়েন্ট শেষ রো-র `(created_at, order_id)` মনে রেখে পরের রিকোয়েস্টে পাঠায়:

```python
page1 = await get_orders_keyset_paginated(session, None, None, limit=3)
last = page1[-1]
page2 = await get_orders_keyset_paginated(session, last.created_at, last.order_id, limit=3)
# পরীক্ষায়: page1 = [9, 8, 6], page2 = [5, 4, 3] — কোনো ফাঁক বা ডুপ্লিকেট নেই
```

API-তে cursor সাধারণত একটি opaque টেক্সট হিসেবে দেওয়া হয় (যেমন দুই মান জুড়ে base64)।

///

ক্লায়েন্ট শেষ রো-র `(created_at, order_id)` cursor হিসেবে ফেরত পাঠায়। সর্ট কলাম ইউনিক না হলে tiebreaker কলাম (`order_id`) বাধ্যতামূলক।

| | Offset | Keyset |
| :--- | :--- | :--- |
| N নম্বর পেজের খরচ | N-এর সাথে বাড়ে | স্থির |
| যেকোনো পেজে লাফ | ✅ | ❌ (শুধু পরের/আগের) |
| একই সময়ে insert হলেও স্থিতিশীল | ❌ রো সরে/ডুপ্লিকেট হয় | ✅ |
| মোট সংখ্যা | অতিরিক্ত `COUNT(*)` | সাধারণত বাদ দেওয়া হয় |

### 35.5 রিলেশনশিপ লোডিং ও N+1 প্রতিরোধ { #s35-5 }
```python
from sqlalchemy.orm import selectinload

async def get_order_with_items(session: AsyncSession, order_id: int) -> Order | None:
    stmt = (
        select(Order)
        .options(selectinload(Order.items))           # 'WHERE order_id IN (...)'
        .where(Order.order_id == order_id, Order.is_deleted.is_(False))
    )
    return (await session.execute(stmt)).scalar_one_or_none()
```

/// warning | রেসপন্সে যা আছে, কুয়েরিতে তা লোড করুন

`OrderResponse`-এ `items` আছে। তাই অর্ডার রিটার্ন করার প্রতিটি এন্ডপয়েন্টে `selectinload(Order.items)` লাগবে। ভুলে গেলে `lazy="raise"`-এর কারণে সাথে সাথে এরর পাবেন, যা লুকানো N+1-এর চেয়ে অনেক ভালো।

///

### 35.6 লক্ষ লক্ষ রো স্ট্রিমিং { #s35-6 }
```python
async def stream_all_orders(session: AsyncSession):
    stmt = select(Order).order_by(Order.order_id).execution_options(yield_per=1000)
    async for order in await session.stream_scalars(stmt):
        yield order
```

/// info | কোডটি সহজ ভাষায়

`stream_all_orders` একটি **async generator**: সব রো একবারে মেমরিতে আনে না, ১০০০টি করে আনে আর একটি একটি করে `yield` করে।

```python
async for order in stream_all_orders(session):
    write_to_csv(order)
```

///

মেমরি-সংক্রান্ত বিষয়ের জন্য [§48.3](performance.md#s48-3) দেখুন।

/// check | সংক্ষেপে মনে রাখুন

* একটি রো ও বিজনেস লজিক → অবজেক্ট (`add()`); হাজার রো → `insert(Model)` + dict-এর তালিকা।
* প্যারেন্টের কালেকশনে চাইল্ড রেখে শুধু প্যারেন্ট `add()` করলেই সব FK ঠিকঠাক বসে।
* "না থাকলে ঢোকাও, থাকলে বদলাও" → `on_conflict_do_update`, Python-এ আগে চেক নয়।
* primary key → `session.get()`; বাকি সব → `select().where()`।
* বড় টেবিলে keyset pagination; রেসপন্সে যা যাবে তা `selectinload` দিয়ে লোড।

///

**পরের ধাপ:** [CRUD ২: Update ও Delete](crud-update-delete.md)।
