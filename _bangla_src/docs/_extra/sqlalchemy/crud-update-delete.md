# CRUD ২: Update ও Delete { #sqlalchemy-crud-update-delete }

/// note | এই পেজে যা শিখবেন

* **Update**: PUT (পুরোটা) বনাম PATCH (আংশিক), বাল্ক আপডেট, atomic increment।
* optimistic concurrency (`version_id_col`) দিয়ে একসাথে দুজনের এডিট সামলানো।
* প্যারেন্টের চাইল্ড-তালিকা সিঙ্ক করা: পুরো বদলানো বনাম মিলিয়ে বদলানো (reconcile)।
* **Delete**: একক, বাল্ক, cascade, আর soft delete (মুছে না ফেলে লুকিয়ে রাখা)।

///

এই পেজও [CRUD ১-এর](crud.md#s33) `Order` / `OrderItem` মডেল আর স্কিমা ব্যবহার করে।

## 36. UPDATE: PUT, PATCH, Bulk, Atomic, Versioned, Nested Sync { #s36 }

### 36.1 পূর্ণ আপডেট (PUT) { #s36-1 }
প্রতিটি পরিবর্তনযোগ্য ফিল্ড প্রতিস্থাপিত হয়:
```python
from app.schemas.order import OrderUpdateFull

async def update_order_full(session: AsyncSession, order_id: int, data: OrderUpdateFull) -> Order | None:
    order = await session.get(Order, order_id)
    if not order or order.is_deleted:
        return None

    order.status = data.status
    order.total_amount = data.total_amount

    await session.commit()            # শুধু পরিবর্তিত কলাম UPDATE হয় (dirty tracking)
    await session.refresh(order)
    return order
```

/// info | কোডটি সহজ ভাষায়

কোথাও `UPDATE` লেখা নেই, অথচ ডেটাবেসে আপডেট হয়। কারণ সেশন প্রতিটি লোড করা অবজেক্টের মূল মান মনে রাখে। commit-এর সময় দেখে কোন অ্যাট্রিবিউট বদলেছে (**dirty tracking**), শুধু সেগুলোর জন্য SQL বানায়:

```sql
UPDATE orders SET status=$1, total_amount=$2, version=$3, updated_at=now()
WHERE orders.order_id = $4 AND orders.version = $5
RETURNING orders.updated_at
```

`version` মেলানো আর `RETURNING updated_at` এসেছে মডেলের `version_id_col` ও `eager_defaults`-এর কারণে।

///

### 36.2 আংশিক আপডেট (PATCH) — `exclude_unset=True` { #s36-2 }

/// tip | উদাহরণ দিয়ে বুঝি

* **PUT** = পুরো ফর্ম নতুন করে জমা দেওয়া। কোনো ঘর ফাঁকা রাখলে সেটা ফাঁকাই হয়ে যাবে।
* **PATCH** = শুধু একটা ঘরে কাটাকুটি করে সংশোধন। বাকি সব যেমন ছিল।

FastAPI টিউটোরিয়ালের [বডি - আপডেট](../tutorial/body-updates.md) পেজেও এ নিয়ে আলোচনা আছে।

///

ক্লায়েন্ট আসলে যে ফিল্ডগুলো পাঠিয়েছে শুধু সেগুলোই বদলায়:
```python
from app.schemas.order import OrderUpdatePartial

async def update_order_partial(session: AsyncSession, order_id: int, data: OrderUpdatePartial) -> Order | None:
    order = await session.get(Order, order_id)
    if not order or order.is_deleted:
        return None

    # exclude_unset=True রিকোয়েস্ট বডিতে না থাকা ফিল্ড বাদ দেয়
    # (স্পষ্টভাবে পাঠানো "status": null রাখা হয় এবং NULL সেট করে)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(order, field, value)

    await session.commit()
    await session.refresh(order)
    return order
```

/// info | `exclude_unset` উদাহরণসহ

ক্লায়েন্ট পাঠাল `{"status": "PAID"}`:

```python
data.model_dump()                    # {"status": "PAID", "total_amount": None, "is_deleted": None}  ❌ বাকিগুলো None হয়ে যেত
data.model_dump(exclude_unset=True)  # {"status": "PAID"}                                           ✅ শুধু পাঠানোটা
```

আর ক্লায়েন্ট যদি সত্যিই `{"total_amount": null}` পাঠায়, তাহলে সেটা "set" হিসেবে গণ্য হবে, আর `total_amount` NULL করার চেষ্টা হবে। কলামটি NOT NULL হলে ডেটাবেস প্রত্যাখ্যান করবে, তাই এমন ফিল্ডে স্কিমাতেই `None` নিষেধ করুন।

///

ক্লায়েন্ট কোন ফিল্ড PATCH করতে পারবে তা হোয়াইটলিস্ট করুন (এখানে schema সেটা করছে) — ইউজার ইনপুটের যেকোনো key-তে কখনো `setattr` করবেন না।

### 36.3 স্টেটমেন্ট-ভিত্তিক বাল্ক UPDATE { #s36-3 }
অনেক রো লোড না করেই বদলায়:
```python
from datetime import datetime
from sqlalchemy import update

async def bulk_cancel_stale_orders(session: AsyncSession, cutoff_date: datetime) -> int:
    stmt = (
        update(Order)
        .where(
            Order.status == "PENDING",
            Order.created_at < cutoff_date,
            Order.is_deleted.is_(False),
        )
        .values(status="CANCELLED", updated_at=func.now())
        .execution_options(synchronize_session=False)   # এই অবজেক্টগুলো আমরা ধরে রাখিনি
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount
```

/// info | কোডটি সহজ ভাষায়

একটি মাত্র SQL, যত রো-ই হোক:

```sql
UPDATE orders SET status='CANCELLED', updated_at=now()
WHERE orders.status = 'PENDING' AND orders.created_at < $1 AND orders.is_deleted IS false
```

কোনো অবজেক্ট Python-এ লোড হয় না। `result.rowcount` বলে দেয় কয়টি রো বদলেছে।

///

`synchronize_session` সেশনে আগে থেকে লোড থাকা মেমরির অবজেক্ট নিয়ন্ত্রণ করে:
| মান | আচরণ |
| :--- | :--- |
| `"auto"` (ডিফল্ট) | সম্ভব হলে `"evaluate"`, নইলে `"fetch"` |
| `"evaluate"` | লোড করা অবজেক্টে Python-এ WHERE/SET প্রয়োগ |
| `"fetch"` | `RETURNING`/SELECT দিয়ে প্রভাবিত রো খুঁজে সেগুলো আপডেট |
| `False` | কিছুই করে না — দ্রুততম; লোড করা অবজেক্ট পুরোনো থাকতে পারে |

/// note | নোট

বাল্ক `update()` `version_id_col` বাড়ায় **না** এবং ORM ইভেন্ট চালায় না। ভার্সনিং দরকার হলে নিজে `version=Order.version + 1` সেট করুন।

///

### 36.4 Atomic increment / decrement { #s36-4 }
একসাথে বহু রিকোয়েস্টে কাউন্টার কখনো Python-এ read-modify-write করবেন না (`order.total_amount += delta`) — দুটি রিকোয়েস্ট একই পুরোনো মান পড়তে পারে। হিসাবটা SQL-কে করতে দিন:
```python
async def adjust_order_total_atomic(session: AsyncSession, order_id: int, adjustment: Decimal) -> None:
    await session.execute(
        update(Order)
        .where(Order.order_id == order_id)
        .values(total_amount=Order.total_amount + adjustment, updated_at=func.now())
    )
    await session.commit()
```

/// warning | কেন `order.total_amount += delta` নয়?

দুটি রিকোয়েস্ট প্রায় একসাথে মোট ১০০-তে ৫ যোগ করতে চাইল:

1. রিকোয়েস্ট A পড়ল ১০০, রিকোয়েস্ট B-ও পড়ল ১০০।
2. A লিখল ১০৫, B-ও লিখল ১০৫।
3. ফল ১০৫, হওয়া উচিত ছিল ১১০। একটি যোগ **হারিয়ে গেল**।

`total_amount = Order.total_amount + adjustment` লিখলে হিসাবটা হয় ডেটাবেসের ভেতরে (`SET total_amount = total_amount + 5`), তাই দুটোই ঠিকঠাক যোগ হয়। বিস্তারিত পাবেন [Concurrency](concurrency.md) অধ্যায়ে।

///

আরও concurrency কৌশল [§47](concurrency.md#s47)-এ।

### 36.5 `version_id_col` দিয়ে optimistic concurrency { #s36-5 }
```python
from sqlalchemy.orm.exc import StaleDataError

async def update_order_concurrency_safe(session: AsyncSession, order_id: int, new_status: str) -> Order:
    order = await session.get(Order, order_id)
    if not order:
        raise ValueError("Order not found")

    order.status = new_status
    try:
        await session.commit()       # UPDATE ... WHERE order_id = ? AND version = ?
        await session.refresh(order)
        return order
    except StaleDataError:
        await session.rollback()
        raise RuntimeError("Conflict: order modified by another request — please retry.")
```

/// tip | উদাহরণ দিয়ে বুঝি

দুজন কর্মী একই অর্ডারের ফাইল খুললেন। দুজনের ফাইলেই লেখা "ভার্সন ৫"। প্রথমজন সংশোধন করে জমা দিলেন, ফাইল হলো "ভার্সন ৬"। দ্বিতীয়জন জমা দিতে গেলে অফিস বলল, "আপনার হাতের কপিটা ভার্সন ৫-এর, এখন চলছে ৬। আগে নতুনটা দেখে নিন।"

এটাই **optimistic locking**: কাউকে আটকায় না, শুধু জমার সময় মিলিয়ে দেখে। মিল না হলে `StaleDataError`, যা API-তে `409 Conflict` হিসেবে ফেরত দিন। আমরা দুটি সেশন দিয়ে চালিয়ে দেখেছি: দ্বিতীয় commit-এ সত্যিই `StaleDataError` আসে।

///

HTTP API-তে রেসপন্সে `version` দিন এবং তা ফেরত চান (অথবা `If-Match` ETag), যাতে চেকটি শুধু রিকোয়েস্ট নয়, ইউজারের ভাবনার সময়টুকুও কভার করে।

### 36.6 নেস্টেড কালেকশন সিঙ্ক { #s36-6 }
সব চাইল্ড **প্রতিস্থাপন**:
```python
async def replace_order_items(session: AsyncSession, order_id: int, new_items: list[OrderItemCreate]) -> Order:
    stmt = select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id)
    order = (await session.execute(stmt)).scalar_one()

    order.items.clear()          # delete-orphan → flush-এ পুরোনো রো DELETE হয়
    for i in new_items:
        order.items.append(OrderItem(product_sku=i.product_sku, quantity=i.quantity, unit_price=i.unit_price))

    order.total_amount = sum(it.quantity * it.unit_price for it in order.items)
    await session.commit()
    return order
```

**Reconcile** (diff) — মিলে যাওয়া রো রেখে আপডেট, নতুন ইনসার্ট, অনুপস্থিত ডিলিট। ID সংরক্ষিত থাকে, অপ্রয়োজনীয় পরিবর্তন হয় না:
```python
async def sync_order_items(session: AsyncSession, order_id: int, incoming: list[OrderItemCreate]) -> Order:
    stmt = select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id)
    order = (await session.execute(stmt)).scalar_one()

    existing = {item.product_sku: item for item in order.items}
    incoming_by_sku = {i.product_sku: i for i in incoming}

    # ১. যেগুলো আর নেই সেগুলো ডিলিট
    for sku, item in existing.items():
        if sku not in incoming_by_sku:
            order.items.remove(item)                 # delete-orphan

    # ২. বিদ্যমানগুলো আপডেট / নতুনগুলো ইনসার্ট
    for sku, data in incoming_by_sku.items():
        if sku in existing:
            existing[sku].quantity = data.quantity
            existing[sku].unit_price = data.unit_price
        else:
            order.items.append(OrderItem(product_sku=sku, quantity=data.quantity, unit_price=data.unit_price))

    order.total_amount = sum(it.quantity * it.unit_price for it in order.items)
    await session.commit()
    return order
```

/// info | দুই পদ্ধতির পার্থক্য

| | `replace_order_items` | `sync_order_items` |
| :--- | :--- | :--- |
| পদ্ধতি | সব পুরোনো মুছে সব নতুন ঢোকানো | মিলিয়ে দেখা: থাকলে বদলাও, নতুন হলে যোগ, না থাকলে মোছো |
| আইটেমের `item_id` | বদলে যায় | যেগুলো আছে সেগুলোর একই থাকে |
| SQL সংখ্যা | সবসময় বেশি | শুধু যা বদলেছে |
| কখন | ছোট তালিকা, id-র গুরুত্ব নেই | অন্য টেবিল `item_id` রেফার করে, অথবা অডিট লগ আছে |

///

### 36.7 `RETURNING`-সহ বাল্ক UPDATE { #s36-7 }
```python
async def bulk_discount_orders(session: AsyncSession, customer_id: int, discount_pct: Decimal) -> list[dict]:
    multiplier = Decimal("1.00") - (discount_pct / Decimal("100.00"))
    result = await session.execute(
        update(Order)
        .where(Order.customer_id == customer_id, Order.status == "PENDING")
        .values(total_amount=Order.total_amount * multiplier)
        .returning(Order.order_id, Order.total_amount)
    )
    rows = result.all()
    await session.commit()
    return [{"order_id": r.order_id, "new_total": r.total_amount} for r in rows]
```

### 36.8 Primary key ধরে বাল্ক UPDATE (প্রতি রো-তে আলাদা মান) { #s36-8 }
```python
# ORM "bulk update by primary key": প্রতিটি dict-এ PK থাকতে হবে
# Order-এ version_id_col আছে, তাই বর্তমান version-ও দিতে হবে (না দিলে KeyError: 'version')
await session.execute(
    update(Order),
    [
        {"order_id": 1, "status": "SHIPPED", "version": 1},
        {"order_id": 2, "status": "CANCELLED", "version": 3},
    ],
)
# ফলাফল: WHERE order_id = ? AND version = ? — মিললে version এক বাড়ে, না মিললে StaleDataError
```

/// note | ভার্সনসহ মডেলে বাল্ক আপডেট

`Order`-এ `version_id_col` থাকায় প্রতিটি dict-এ বর্তমান `version`-ও দিতে হয়। না দিলে `KeyError: 'version'` আসে (আমরা আসলে চালিয়ে পেয়েছি)। দিলে SQLAlchemy প্রতিটি রো-তে ভার্সন মিলিয়ে দেখে, আর এক বাড়ায়। ভার্সন ছাড়া মডেলে শুধু primary key আর বদলানোর মানই যথেষ্ট।

///

## 37. DELETE: Hard, Bulk, Cascade ও Soft Delete { #s37 }

### 37.1 একক hard delete { #s37-1 }
```python
async def hard_delete_order(session: AsyncSession, order_id: int) -> bool:
    order = await session.get(Order, order_id)
    if not order:
        return False
    await session.delete(order)      # ORM cascade প্রযোজ্য (+ passive_deletes-এ DB cascade)
    await session.commit()
    return True
```

/// info | কোডটি সহজ ভাষায়

`session.delete(order)` তখনই কাজ করে যখন অবজেক্টটি লোড করা থাকে। মডেলে `cascade="all, delete-orphan"` আর `passive_deletes=True` আছে, তাই:

* আইটেমগুলো সেশনে **লোড করা না থাকলে** SQLAlchemy সেগুলো আনতে যায় না। শুধু `DELETE FROM orders WHERE order_id = ... AND version = ...` পাঠায়, আর আইটেমগুলো ডেটাবেস নিজে মোছে (`ON DELETE CASCADE`)।
* আইটেমগুলো **আগে থেকেই লোড থাকলে** ORM নিজেও প্রতিটির জন্য `DELETE FROM order_items ...` পাঠায়, তারপর অর্ডার মোছে। ফল একই, শুধু SQL বেশি।

///

### 37.2 স্টেটমেন্ট-ভিত্তিক বাল্ক delete { #s37-2 }
```python
from sqlalchemy import delete

async def bulk_delete_cancelled_orders(session: AsyncSession, cutoff_date: datetime) -> int:
    result = await session.execute(
        delete(Order).where(Order.status == "CANCELLED", Order.created_at < cutoff_date)
    )
    await session.commit()
    return result.rowcount
```
বাল্ক `delete()` ORM cascade এড়িয়ে যায় — চাইল্ড মোছে কেবল ডেটাবেসের `ON DELETE CASCADE` (অথবা আপনি আগে চাইল্ড, পরে প্যারেন্ট মুছবেন, যেমন [§38.3](related-crud.md#s38-3)-এ)।

### 37.3 ORM বনাম ডেটাবেস cascade { #s37-3 }
| কনফিগারেশন | মেকানিজম | পারফরম্যান্স |
| :--- | :--- | :--- |
| `cascade="all, delete-orphan"` | ORM সব চাইল্ড SELECT করে, আলাদা আলাদা DELETE পাঠায় | বড় কালেকশনে ধীর |
| + `passive_deletes=True` + `ForeignKey(..., ondelete="CASCADE")` | ORM প্যারেন্ট মোছে; PostgreSQL চাইল্ড মোছে | **দ্রুত (রিকমেন্ডেড)** |
| কোনো ORM cascade নেই, `ondelete` ছাড়া FK | চাইল্ডসহ প্যারেন্ট মুছলে → `IntegrityError` | যখন ডিলিট প্রত্যাখ্যান করাই উদ্দেশ্য |

### 37.4 Soft delete আর্কিটেকচার { #s37-4 }

/// tip | উদাহরণ দিয়ে বুঝি

**Soft delete** হলো কম্পিউটারের **রিসাইকেল বিন**। ফাইল মুছলে আসলে হারায় না, শুধু চোখের আড়ালে যায়। দরকার হলে ফিরিয়ে আনা যায়। হিসাব, অডিট বা আইনি কারণে অনেক ব্যবসায় ডেটা আসলে কখনো মোছা হয় না।

///

রো না মুছে চিহ্নিত করে ইতিহাস রাখা এবং পুনরুদ্ধারের সুযোগ দেওয়া:
```python
async def soft_delete_order(session: AsyncSession, order_id: int) -> bool:
    result = await session.execute(
        update(Order)
        .where(Order.order_id == order_id, Order.is_deleted.is_(False))
        .values(is_deleted=True, updated_at=func.now())
    )
    await session.commit()
    return result.rowcount > 0

async def restore_soft_deleted_order(session: AsyncSession, order_id: int) -> bool:
    result = await session.execute(
        update(Order)
        .where(Order.order_id == order_id, Order.is_deleted.is_(True))
        .values(is_deleted=False, updated_at=func.now())
    )
    await session.commit()
    return result.rowcount > 0
```

সব জায়গায় `is_deleted == False` মনে রাখার বদলে একটি গ্লোবাল criteria hook দিয়ে **প্রতিটি** কুয়েরিতে "ডিলিট হয়নি" শর্তটি ডিফল্ট করুন:
```python
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)

@event.listens_for(Session, "do_orm_execute")
def _filter_soft_deleted(execute_state):
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(SoftDeleteMixin, lambda cls: cls.is_deleted.is_(False), include_aliases=True)
        )

# অ্যাডমিন / restore স্ক্রিনে বাদ দিতে:
stmt = select(Order).execution_options(include_deleted=True)
```

/// info | কোডটি সহজ ভাষায়

* `do_orm_execute` event প্রতিটি ORM কুয়েরির ঠিক আগে চলে।
* `with_loader_criteria(SoftDeleteMixin, ...)`: `SoftDeleteMixin` থেকে তৈরি **সব** মডেলে স্বয়ংক্রিয়ভাবে `WHERE is_deleted IS false` যোগ হয়। relationship লোডেও (`selectinload`) এটা কাজ করে।
* `execution_options(include_deleted=True)`: অ্যাডমিন স্ক্রিনে মুছে ফেলাগুলোও দেখতে চাইলে।

আমরা পরীক্ষা করেছি: সাধারণ কুয়েরিতে শুধু সক্রিয় অর্ডার আসে, `include_deleted=True` দিলে সব আসে, আর `selectinload` করা আইটেম থেকেও মুছে ফেলা আইটেম বাদ যায়।

এটা কাজ করাতে মডেলকে mixin থেকে তৈরি করতে হবে: `class Order(SoftDeleteMixin, Base)`।

///

একটি **partial unique index**-ও বিবেচনা করুন, যাতে soft-deleted রো একই কোড দিয়ে নতুন রো তৈরিতে বাধা না দেয়: `Index("uq_orders_code_live", "order_code", unique=True, postgresql_where=text("NOT is_deleted"))`। লিংকের ক্ষেত্রে OFBiz-এ soft delete-এর সমতুল্য হলো `thru_date` সেট করা ([§39.2](related-crud.md#s39-2))।

/// check | সংক্ষেপে মনে রাখুন

* অবজেক্ট লোড করে অ্যাট্রিবিউট বদলান, commit করলেই শুধু বদলানো কলাম UPDATE হয়।
* PATCH-এ `model_dump(exclude_unset=True)`, আর ইউজার ইনপুটের যেকোনো key-তে `setattr` নয়।
* কাউন্টার বা ব্যালেন্সে `update().values(col=Model.col + n)`, Python-এ পড়ে-যোগ-লেখা নয়।
* দুজনের এডিট সামলাতে `version_id_col` + `StaleDataError` → 409।
* বাল্ক `update()` / `delete()` cascade, event বা version চালায় না।
* ইতিহাস রাখতে soft delete + গ্লোবাল ফিল্টার।

///

**পরের ধাপ:** একাধিক টেবিল একসাথে সামলান [সম্পর্কিত টেবিলে CRUD](related-crud.md) অধ্যায়ে।
