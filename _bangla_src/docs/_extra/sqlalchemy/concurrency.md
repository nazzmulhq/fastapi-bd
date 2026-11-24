# Concurrency: Race Condition ঠেকানো { #sqlalchemy-concurrency }

/// note | এই পেজে যা শিখবেন

* race condition আর "lost update" কী, ধাপে ধাপে।
* ঠেকানোর ৫টি প্রোডাকশন-প্রমাণিত উপায়: atomic SQL, `SELECT … FOR UPDATE`, optimistic locking, unique constraint ও idempotency key, `SERIALIZABLE` + retry।
* job queue-তে `SKIP LOCKED`, আর কোন পরিস্থিতিতে কোন উপায়।

///

/// tip | উদাহরণ দিয়ে বুঝি

একটি জয়েন্ট অ্যাকাউন্ট, ব্যালেন্স ১০০ টাকা। স্বামী আর স্ত্রী একই সেকেন্ডে দুটি আলাদা ATM থেকে ৮০ টাকা করে তুলতে গেলেন। দুটি মেশিনই দেখল "১০০ আছে, ৮০ দেওয়া যায়", দুটিই টাকা দিল। ব্যাংক হারাল ৬০ টাকা।

FastAPI অ্যাপে প্রতিদিন এমনই হয়: একাধিক রিকোয়েস্ট একসাথে একই রো পড়ে আর লেখে। এই অধ্যায়ের প্রতিটি উপায় আমরা আসলে দুটি রিকোয়েস্ট একসাথে চালিয়ে (`asyncio.gather`) পরীক্ষা করেছি।

///

এই অধ্যায়ের উদাহরণে এই ছোট মডেলগুলো ব্যবহৃত হয়েছে:

```python
class Wallet(Base):
    __tablename__ = "wallets"
    wallet_id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class QueueJob(Base):
    __tablename__ = "queue_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED")
    priority: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    locked_by: Mapped[str | None] = mapped_column(String(50))
```

`InventoryItem` আছে [রেফারেন্স মডেলে](querying.md#s25)।

## 47. Concurrency Control: Race Condition ঠেকানোর ৫টি প্রোডাকশন সমাধান { #s47 }

Async অ্যাপে অনেক রিকোয়েস্ট একই সময়ে একই রো পড়ে ও লেখে। স্পষ্ট নিয়ন্ত্রণ না থাকলে **lost update** হয় এবং হিসাব নষ্ট হয়।

### 47.1 Lost update-এর গঠন { #s47-1 }
১০০ টাকার একটি ওয়ালেট থেকে দুটি রিকোয়েস্ট একসাথে ৮০ টাকা করে তুলছে:
```
Time  Request A                          Request B                          DB balance
--------------------------------------------------------------------------------------
T1    SELECT balance  -> 100                                                100
T2                                       SELECT balance  -> 100             100
T3    check 100 >= 80  OK                                                   100
T4                                       check 100 >= 80  OK                100
T5    UPDATE balance = 100 - 80 = 20                                        20
T6                                       UPDATE balance = 100 - 80 = 20     20  (LOST UPDATE)
--------------------------------------------------------------------------------------
ফলাফল: ১৬০ টাকা তোলা হয়েছে, অথচ বাকি দেখাচ্ছে ২০। ডেটাবেস ভুল।
```

/// info | টেবিলটি সহজ ভাষায়

সমস্যার মূল: **পড়া** (T1, T2) আর **লেখা** (T5, T6)-র মাঝে একটা ফাঁক আছে। সেই ফাঁকে অন্য রিকোয়েস্ট ঢুকে পুরোনো মান পড়ে ফেলে। দুজনেই ভাবে "আমি ১০০ থেকে ৮০ কমাচ্ছি", অথচ দ্বিতীয়জনের কমানো উচিত ছিল ২০ থেকে। তাই নিচের প্রতিটি উপায়ের লক্ষ্য একটাই: এই ফাঁক বন্ধ করা।

///

### 47.2 সমাধান ১ — atomic SQL এক্সপ্রেশন (স্পষ্ট লক ছাড়া) { #s47-2 }
হিসাব **এবং** শর্ত একটি UPDATE-এই করুন:
```python
from decimal import Decimal
from sqlalchemy import update
from app.models.wallet import Wallet

async def withdraw_money_atomic(session: AsyncSession, wallet_id: int, amount: Decimal) -> bool:
    result = await session.execute(
        update(Wallet)
        .where(Wallet.wallet_id == wallet_id, Wallet.balance >= amount)   # শর্ত: পর্যাপ্ত ব্যালেন্স
        .values(balance=Wallet.balance - amount)                          # হিসাব করে ডেটাবেস
    )
    await session.commit()
    return result.rowcount > 0       # 0 → অপর্যাপ্ত ব্যালেন্স (অথবা ওয়ালেট নেই)
```

/// tip | উদাহরণ দিয়ে বুঝি

এটা যেন ব্যাংকের একজন ক্যাশিয়ারকে বলা, "যদি অন্তত ৮০ থাকে, তবেই ৮০ কমাও।" যাচাই আর কমানো তিনি এক নিঃশ্বাসে করেন, মাঝে কাউকে ঢুকতে দেন না।

পরীক্ষার ফল: দুটি রিকোয়েস্ট একসাথে → `[True, False]`। একটি সফল, অন্যটি "পর্যাপ্ত ব্যালেন্স নেই"। ব্যালেন্স ২০, ঠিকঠাক।

///

UPDATE নিজেই যে রো লক নেয় তা দুটি রিকোয়েস্টকে পরপর চালায়, এবং দ্বিতীয়টি নতুন মানের উপর `balance >= amount` আবার যাচাই করে।
- **সুবিধা:** দ্রুততম; Python কোড চলাকালীন কোনো লক ধরে রাখা হয় না।
- **অসুবিধা:** শুধু তখনই সম্ভব যখন লজিক SQL-এ লেখা যায়।

### 47.3 সমাধান ২ — pessimistic row locking (`SELECT … FOR UPDATE`) { #s47-3 }
যখন পড়া ও লেখার মাঝে Python লজিক (ভ্যালিডেশন, অন্য টেবিল, বাইরের কল) চালাতে হয়:
```python
from sqlalchemy import select

async def withdraw_with_pessimistic_lock(session: AsyncSession, wallet_id: int, amount: Decimal) -> Wallet:
    async with session.begin():
        # এক্সক্লুসিভ রো লক: commit না হওয়া পর্যন্ত এই রো-তে অন্য FOR UPDATE / UPDATE অপেক্ষা করবে
        wallet = (await session.scalars(
            select(Wallet).where(Wallet.wallet_id == wallet_id).with_for_update()
        )).one_or_none()

        if not wallet:
            raise ValueError("Wallet not found")
        if wallet.balance < amount:              # অবস্থা নিশ্চিতভাবে হালনাগাদ
            raise ValueError("Insufficient balance")

        wallet.balance -= amount
    # COMMIT লক ছেড়ে দেয়
    return wallet
```

/// tip | উদাহরণ দিয়ে বুঝি

`FOR UPDATE` হলো বাথরুমের দরজার ছিটকিনি। একজন ঢুকে ছিটকিনি দিলে (রো লক) পরের জন দরজার বাইরে অপেক্ষা করেন। প্রথমজন বের হলে (COMMIT) দ্বিতীয়জন ঢোকেন, আর তখন তিনি **হালনাগাদ** অবস্থা দেখেন।

পরীক্ষার ফল: `["Insufficient balance", "ok"]`। দ্বিতীয় রিকোয়েস্ট অপেক্ষা করে নতুন ব্যালেন্স ২০ দেখল, তাই প্রত্যাখ্যান করল।

///

ইনভেন্টরি উদাহরণ (OFBiz `InventoryItem`):
```python
async def reserve_inventory_pessimistic(session: AsyncSession, inventory_item_id: str, qty: Decimal) -> bool:
    async with session.begin():
        item = (await session.execute(
            select(InventoryItem)
            .where(InventoryItem.inventory_item_id == inventory_item_id)
            .with_for_update()                    # লক না পাওয়া পর্যন্ত ব্লক থাকবে
        )).scalar_one_or_none()
        if not item or item.available_to_promise_total < qty:
            return False
        item.available_to_promise_total -= qty
        return True
```

`with_for_update()`-এর রূপভেদ:
| কল | SQL | ব্যবহার |
| :--- | :--- | :--- |
| `with_for_update()` | `FOR UPDATE` | লকের জন্য অপেক্ষা |
| `with_for_update(nowait=True)` | `FOR UPDATE NOWAIT` | সাথে সাথে ফেইল (`OperationalError` / `LockNotAvailable`) — "অন্য কেউ এডিট করছে" |
| `with_for_update(skip_locked=True)` | `FOR UPDATE SKIP LOCKED` | জব কিউ: পরের লক-না-করা রো নেওয়া |
| `with_for_update(read=True)` | `FOR SHARE` | লেখকদের আটকায়, অন্য পাঠকদের অনুমতি দেয় |
| `with_for_update(of=Wallet)` | `FOR UPDATE OF wallets` | Join-এ শুধু একটি টেবিল লক |
| `with_for_update(key_share=True)` | `FOR NO KEY UPDATE` / `FOR KEY SHARE` | হালকা লক যা FK চেক আটকায় না |

`SKIP LOCKED` দিয়ে হাই-থ্রুপুট কিউ — অনেক worker, শূন্য প্রতিযোগিতা:
```python
async def claim_next_job(session: AsyncSession, worker_id: str) -> QueueJob | None:
    async with session.begin():
        job = (await session.scalars(
            select(QueueJob)
            .where(QueueJob.status == "QUEUED")
            .order_by(QueueJob.priority.desc(), QueueJob.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)    # অন্য worker-এর লক করা রো বাদ যায়
        )).first()
        if job:
            job.status = "PROCESSING"
            job.locked_by = worker_id
    return job
```

/// info | কোডটি সহজ ভাষায়

অনেক worker একসাথে কাজ নিতে চাইলে সাধারণ `FOR UPDATE`-এ সবাই প্রথম কাজটির জন্য লাইনে দাঁড়ায়। `SKIP LOCKED` বলে, "যে কাজ অন্য কেউ ধরে রেখেছে, সেটা বাদ দিয়ে পরেরটা নাও"। পরীক্ষায় ৪টি worker একসাথে, ৩টি কাজ: প্রত্যেকে আলাদা কাজ পেল (`[1, 2, 3]`), একজন পেল না, আর কেউ কারও জন্য অপেক্ষা করল না।

///

/// danger | বিপদ

লক করা অংশ ছোট রাখুন — রো লক ধরে রেখে কখনো ধীর HTTP কল `await` করবেন না। ডেডলক এড়াতে সবসময় একই ক্রমে (যেমন primary key অনুযায়ী) রো লক করুন।

///

### 47.4 সমাধান ৩ — optimistic locking (`version_id_col`) { #s47-4 }
কোনো লক নেই; ধরে নেওয়া হয় দ্বন্দ্ব বিরল, এবং লেখার সময় তা শনাক্ত করা হয়:
```python
class ProductInventory(Base):
    __tablename__ = "product_inventory"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __mapper_args__ = {"version_id_col": version}     # কলাম সংজ্ঞার পরে
```
SQLAlchemy পাঠায় `UPDATE ... SET stock=?, version=version+1 WHERE product_id=? AND version=?`। অন্য transaction আগেই ভার্সন বাড়িয়ে থাকলে কোনো রো মেলে না এবং `StaleDataError` হয়:
```python
from fastapi import HTTPException
from sqlalchemy.orm.exc import StaleDataError

async def deduct_stock_optimistic(session: AsyncSession, product_id: int, quantity: int) -> ProductInventory:
    item = await session.get(ProductInventory, product_id)
    if not item or item.stock < quantity:
        raise ValueError("Out of stock or invalid product")

    item.stock -= quantity
    try:
        await session.commit()
        await session.refresh(item)
        return item
    except StaleDataError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="কনকারেন্ট এডিট দ্বন্দ্ব! স্টক অন্য রিকোয়েস্টে বদলেছে, আবার চেষ্টা করুন।")
```

/// tip | উদাহরণ দিয়ে বুঝি

Google Docs-এ দুজন একই লাইন একসাথে এডিট করলে একজনকে বলা হয় "এর মধ্যে বদলে গেছে, আবার দেখুন"। optimistic locking-ও তাই: কাউকে আটকায় না, শুধু জমা দেওয়ার সময় ভার্সন মিলিয়ে দেখে।

* **কখন ভালো**: দ্বন্দ্ব কম হয়, আর ইউজার অনেকক্ষণ ধরে ফর্ম এডিট করেন (লক এতক্ষণ ধরে রাখা অসম্ভব)।
* **API-তে**: রেসপন্সে `version` পাঠান, আর আপডেট রিকোয়েস্টে ক্লায়েন্টকে সেটা ফেরত পাঠাতে বলুন (অথবা `ETag` / `If-Match` হেডার)।

///

সার্ভার-সাইড ভার্সনিং (যেমন PostgreSQL `xmin`): `version_id_col=xmin_col, "version_id_generator": False`।

### 47.5 সমাধান ৪ — unique constraint ও idempotency key (ডাবল সাবমিট) { #s47-5 }
ডাবল-ক্লিক, ক্লায়েন্টের retry এবং webhook-এর পুনঃপ্রেরণ ডুপ্লিকেট তৈরি করে। ডেটাবেসকেই প্রত্যাখ্যান করতে দিন:
```python
from sqlalchemy import UniqueConstraint

class CouponClaim(Base):
    __tablename__ = "coupon_claims"

    claim_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    coupon_id: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    __table_args__ = (UniqueConstraint("user_id", "coupon_id", name="uq_user_coupon_claim"),)
```
```python
from sqlalchemy.exc import IntegrityError

async def claim_coupon_safe(session: AsyncSession, user_id: int, coupon_id: int, idempotency_key: str):
    try:
        session.add(CouponClaim(user_id=user_id, coupon_id=coupon_id, idempotency_key=idempotency_key))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="কুপন আগেই নেওয়া হয়েছে অথবা ডুপ্লিকেট রিকোয়েস্ট।")
```

/// info | কোডটি সহজ ভাষায়

* `UniqueConstraint("user_id", "coupon_id")`: একজন ইউজার একটি কুপন একবারই নিতে পারবেন, ডেটাবেস নিজেই নিশ্চিত করে।
* `idempotency_key`: ক্লায়েন্ট প্রতিটি "কাজ"-এর জন্য একটি অনন্য key পাঠায় (সাধারণত `Idempotency-Key` হেডারে)। নেটওয়ার্ক সমস্যায় একই রিকোয়েস্ট আবার এলে key একই থাকে, তাই ডেটাবেস দ্বিতীয়টি প্রত্যাখ্যান করে।
* পরীক্ষায় দ্বিতীয় দাবি `IntegrityError` দিয়ে প্রত্যাখ্যাত হয়েছে।

///

Python-এ "আগে চেক, তারপর ইনসার্ট" নিরাপদ **নয়** — দুটি রিকোয়েস্টই চেক পার হতে পারে। শুধু কনস্ট্রেইন্টই নিরাপদ।

### 47.6 সমাধান ৫ — `SERIALIZABLE` isolation + স্বয়ংক্রিয় retry { #s47-6 }
একাধিক রো/টেবিল জুড়ে নিয়মের ক্ষেত্রে (যেমন "বরাদ্দের যোগফল ≤ বাজেট") `SERIALIZABLE`-এ চালান এবং PostgreSQL transaction বাতিল করলে (`40001` serialization failure, `40P01` deadlock) retry করুন:
```python
import asyncio
import functools
import random
from sqlalchemy.exc import DBAPIError

RETRYABLE_SQLSTATES = {"40001", "40P01"}

def _sqlstate(exc: DBAPIError) -> str | None:
    orig = exc.orig
    # asyncpg এরর র‍্যাপ করা থাকে; কোডটি মূল এক্সেপশনে থাকে
    return getattr(orig, "sqlstate", None) or getattr(getattr(orig, "__cause__", None), "sqlstate", None)

def retry_on_concurrency_conflict(max_retries: int = 3, base_delay: float = 0.1):
    """Exponential backoff + jitter দিয়ে পুরো transaction আবার চালানো।"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except DBAPIError as exc:
                    if _sqlstate(exc) not in RETRYABLE_SQLSTATES or attempt == max_retries:
                        raise
                    await asyncio.sleep(delay + random.uniform(0, delay))
                    delay *= 2
        return wrapper
    return decorator

@retry_on_concurrency_conflict()
async def allocate_budget(amount: Decimal, project_id: int):
    # প্রতিটি চেষ্টায় অবশ্যই নতুন session/transaction
    async with SerializableSession() as session, session.begin():
        ...
```

/// info | কোডটি সহজ ভাষায়

* `SERIALIZABLE`-এ PostgreSQL পাহারা দেয় যেন ফল ঠিক সেরকম হয় যেন ট্রানজ্যাকশনগুলো একটার পর একটা চলেছে। নিয়ম ভাঙার সম্ভাবনা দেখলে একটিকে বাতিল করে `40001` কোড দিয়ে।
* decorator সেই এরর ধরে **পুরো ফাংশন** আবার চালায়: নতুন সেশন, নতুন ট্রানজ্যাকশন, নতুন করে পড়া।
* `delay + random.uniform(0, delay)`: প্রতিবার অপেক্ষা দ্বিগুণ, সাথে একটু এলোমেলো সময় (jitter), যাতে সবাই একই মুহূর্তে আবার চেষ্টা না করে।

পরীক্ষায় দুটি withdraw (১০ ও ২০ টাকা) একসাথে চালানো হয়েছিল। একটি `40001` পেয়ে আবার চেষ্টা করে সফল হয়েছে, শেষ ব্যালেন্স ঠিক ৭০।

///

এখানে `SerializableSession = async_sessionmaker(engine.execution_options(isolation_level="SERIALIZABLE"), expire_on_commit=False)`।

Retry করা ফাংশনকে শুরু থেকে শেষ পর্যন্ত নিজের transaction-এর মালিক হতে হবে — ব্যর্থ transaction-এর শুধু শেষ স্টেটমেন্ট আবার চালানো অর্থহীন।

### 47.7 সিদ্ধান্ত ফ্লোচার্ট { #s47-7 }
```
                      Need race-condition prevention?
                                    |
                    +---------------+---------------+
                    |                               |
       [Simple counter/balance/stock]     [Complex business logic]
                    |                               |
          Fix 1: Atomic SQL               Contention high or low?
        WHERE balance >= amount                     |
        SET balance = balance - amount +------------+------------+
                                       |                         |
                                 [High contention]        [Low contention]
                                       |                         |
                               Fix 2: Pessimistic        Fix 3: Optimistic
                               (SELECT ... FOR UPDATE)   (version_id_col)
                                       |
                   +-------------------+-------------------+
                   |                                       |
       [Job / task queue workers]              [Prevent double submissions]
                   |                                       |
       with_for_update(skip_locked=True)      Fix 4: UniqueConstraint / idempotency key

  Invariant across many rows/tables?  -->  Fix 5: SERIALIZABLE + retry decorator
```

| কৌশল | লক | কখন সেরা | ব্যর্থতার রূপ |
| :--- | :--- | :--- | :--- |
| Atomic SQL | এক স্টেটমেন্টের জন্য রো লক | লজিক এক UPDATE-এ লেখা যায় | `rowcount == 0` |
| `FOR UPDATE` | commit পর্যন্ত রো লক | উচ্চ প্রতিযোগিতা, Python লজিক দরকার | অপেক্ষা / ডেডলক |
| `version_id_col` | নেই | কম প্রতিযোগিতা, দীর্ঘ এডিট ফর্ম | `StaleDataError` → 409 |
| Unique constraint | ইনডেক্স এন্ট্রি | ডুপ্লিকেট প্রতিরোধ | `IntegrityError` → 409 |
| `SERIALIZABLE` | Predicate ট্র্যাকিং | বহু-রো নিয়ম | `40001` → retry |

/// check | সংক্ষেপে মনে রাখুন

* "পড়ো → Python-এ হিসাব → লেখো" প্যাটার্নে race condition লুকিয়ে থাকে।
* সম্ভব হলে এক UPDATE-এ শর্তসহ হিসাব (atomic SQL), সবচেয়ে দ্রুত ও সহজ।
* পড়ে Python-এ সিদ্ধান্ত নিতে হলে `with_for_update()`, লক ধরে রাখা অংশ ছোট।
* লম্বা এডিট বা কম দ্বন্দ্বে `version_id_col` + 409।
* ডুপ্লিকেট ঠেকাতে Python-এ চেক নয়, ডেটাবেসের unique constraint।
* বহু রো-র নিয়মে `SERIALIZABLE` + পুরো ট্রানজ্যাকশন retry।

///

**পরের ধাপ:** দ্রুততা আর প্রোডাকশনের প্রস্তুতি দেখুন [পারফরম্যান্স ও প্রোডাকশন](performance.md) অধ্যায়ে।
