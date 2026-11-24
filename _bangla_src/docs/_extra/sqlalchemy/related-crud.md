# সম্পর্কিত টেবিলে CRUD { #sqlalchemy-related-crud }

/// note | এই পেজে যা শিখবেন

* একটি ট্রানজ্যাকশনে প্যারেন্ট ও চাইল্ড তৈরি, আপডেট ও মোছা (composite key-সহ)।
* payload-সহ জাংশন টেবিলে লিংক তৈরি, মেয়াদ শেষ করা (soft expire) ও মোছা।
* বেস + সাবটাইপ টেবিল (shared primary key) একসাথে সামলানো।
* `IntegrityError`-কে সুন্দর API এররে বদলানো, আর ঐচ্ছিক ধাপের জন্য savepoint।

///

এই প্যাটার্নগুলো [কুয়েরি অধ্যায়ের রেফারেন্স মডেল](querying.md#s25) ব্যবহার করে: স্ট্রিং key, composite key, আর `__table_args__`-এর ভেতরে `ForeignKeyConstraint`। সেখানে "পুরো রেফারেন্স মডেল কোড" খুলে দেখে নিন।

/// tip | একটাই মূলমন্ত্র

একাধিক টেবিলে লেখা সব কাজ **একটি ট্রানজ্যাকশনে** করুন: `async with session.begin():`। অর্ডার হলো কিন্তু আইটেম হলো না, বা Party হলো কিন্তু Person হলো না, এমন অর্ধেক অবস্থা যেন কখনো ডেটাবেসে না থাকে।

///

## 38. প্যাটার্ন ১: Parent-Child (1:N) — `OrderHeader` ও `OrderItem` { #s38 }

`OrderItem`-এর composite primary key `(order_id, order_item_seq_id)`, যেখানে `order_id` একই সাথে `OrderHeader`-এর দিকে FK।

### 38.1 এক transaction-এ প্যারেন্ট + চাইল্ড তৈরি { #s38-1 }

#### পদ্ধতি ক — সরাসরি FK অ্যাসাইন করে (কোনো `relationship()` ছাড়াই কাজ করে) { #s38-1-a }
```python
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderHeader, OrderItem

async def create_order_with_items_explicit(session: AsyncSession) -> OrderHeader:
    async with session.begin():                      # atomic: হয় সব, নয় কিছুই না
        now = datetime.now(timezone.utc)

        # ধাপ ১: প্যারেন্ট
        order = OrderHeader(
            order_id="ORD_1001",
            order_type_id="SALES_ORDER",
            order_name="Web Sales Order #1001",
            status_id="ORDER_CREATED",
            order_date=now,
            entry_date=now,
            grand_total=Decimal("1500.00"),
            currency_uom="BDT",
        )
        session.add(order)
        # flush = এখনই INSERT পাঠানো (commit ছাড়া), যাতে FK-এর টার্গেট রো থাকে
        # এবং DB-তে তৈরি কোনো key থাকলে তা পাওয়া যায়
        await session.flush()

        # ধাপ ২: চাইল্ড
        session.add_all([
            OrderItem(
                order_id=order.order_id,
                order_item_seq_id="00001",
                order_item_type_id="PRODUCT_ORDER_ITEM",
                product_id="PROD_LAPTOP_01",
                quantity=Decimal("1"),
                unit_price=Decimal("1200.00"),
                status_id="ITEM_CREATED",
            ),
            OrderItem(
                order_id=order.order_id,
                order_item_seq_id="00002",
                order_item_type_id="PRODUCT_ORDER_ITEM",
                product_id="PROD_MOUSE_01",
                quantity=Decimal("2"),
                unit_price=Decimal("150.00"),
                status_id="ITEM_CREATED",
            ),
        ])
    # begin() ব্লক শেষ হওয়ার সময় COMMIT হয়েছে
    return order
```

/// info | কোডটি সহজ ভাষায়

1. `async with session.begin()`: ব্লকের সব কাজ এক ট্রানজ্যাকশন। শেষে নিজেই COMMIT, এরর হলে ROLLBACK।
2. প্যারেন্ট `OrderHeader` যোগ করে `flush()`: `INSERT INTO order_header` এখনই চলে গেল (commit ছাড়া)।
3. দুটি `OrderItem`, প্রতিটিতে `order_id=order.order_id` আর নিজের সিকোয়েন্স নম্বর `"00001"`, `"00002"`।
4. ব্লক শেষ: দুটি আইটেম INSERT, তারপর COMMIT।

///

অ্যাপ্লিকেশন নিজে string PK দিলে flush কঠোরভাবে জরুরি নয় (unit of work এমনিতেই প্যারেন্টকে চাইল্ডের আগে রাখে), কিন্তু প্যারেন্টের PK ডেটাবেস তৈরি করলে এটি অবশ্যই লাগবে।

#### পদ্ধতি খ — ORM কালেকশনের মাধ্যমে { #s38-1-b }
```python
# প্রয়োজন: OrderHeader.items = relationship(back_populates="order_header", cascade="all, delete-orphan")

async def create_order_with_items_orm(session: AsyncSession) -> OrderHeader:
    order = OrderHeader(
        order_id="ORD_1002",
        order_type_id="SALES_ORDER",
        order_name="Mobile Sales Order",
        items=[
            OrderItem(order_item_seq_id="00001", product_id="PROD_PHONE_01",
                      quantity=Decimal("1"), unit_price=Decimal("25000.00")),
            OrderItem(order_item_seq_id="00002", product_id="PROD_CASE_01",
                      quantity=Decimal("1"), unit_price=Decimal("500.00")),
        ],
    )
    session.add(order)          # save-update cascade-এ চাইল্ড যুক্ত হয়; order_id বসে যায়
    await session.commit()
    return order
```

/// info | কোডটি সহজ ভাষায়

এখানে আইটেমে `order_id` লেখাই হয়নি। `items=[...]` কালেকশনে রাখায় SQLAlchemy নিজেই `order_id = "ORD_1002"` বসিয়ে দেয়। রিলেশনশিপ থাকলে এই পদ্ধতিটাই সহজ আর ভুলের সুযোগ কম।

///

### 38.2 বিদ্যমান চাইল্ড আপডেট ও নতুন চাইল্ড যোগ { #s38-2 }
```python
from sqlalchemy import func, select

async def update_order_items(session: AsyncSession, order_id: str):
    async with session.begin():
        # ১. Composite PK দিয়ে একটি চাইল্ড আনা
        item = await session.get(OrderItem, (order_id, "00001"))
        if item:
            item.quantity = Decimal("3")
            item.unit_price = Decimal("1150.00")
            item.status_id = "ITEM_APPROVED"

        # ২. পরবর্তী সিকোয়েন্স নম্বর বের করে নতুন চাইল্ড যোগ
        max_seq = await session.scalar(
            select(func.max(OrderItem.order_item_seq_id)).where(OrderItem.order_id == order_id)
        )
        next_seq = f"{int(max_seq or 0) + 1:05d}"       # "00003"

        session.add(OrderItem(
            order_id=order_id,
            order_item_seq_id=next_seq,
            order_item_type_id="PRODUCT_ORDER_ITEM",
            product_id="PROD_KEYBOARD_01",
            quantity=Decimal("1"),
            unit_price=Decimal("800.00"),
            status_id="ITEM_CREATED",
        ))
```

/// info | কোডটি সহজ ভাষায়

* `session.get(OrderItem, (order_id, "00001"))`: composite key-তে tuple, কলামের ক্রম মেনে।
* `func.max(order_item_seq_id)`: সবচেয়ে বড় সিকোয়েন্স নম্বর, যেমন `"00002"`। তারপর `int("00002") + 1 = 3`, আর `f"{3:05d}"` = `"00003"` (পাঁচ অঙ্ক পর্যন্ত সামনে শূন্য)।

///

একই সময়ে দুটি রিকোয়েস্ট একই `next_seq` হিসাব করতে পারে; composite PK একটিকে `IntegrityError` দিয়ে ফেইল করাবে — ধরে retry করুন, অথবা আগে প্যারেন্টকে লক করুন (`with_for_update`, [§47.3](concurrency.md#s47-3))।

### 38.3 একটি চাইল্ড মোছা বনাম পুরো অর্ডার মোছা { #s38-3 }
```python
from sqlalchemy import delete

async def delete_single_order_item(session: AsyncSession, order_id: str, seq_id: str) -> bool:
    """একটি লাইন মোছে; প্যারেন্ট অর্ডার অক্ষত থাকে।"""
    result = await session.execute(
        delete(OrderItem).where(OrderItem.order_id == order_id, OrderItem.order_item_seq_id == seq_id)
    )
    await session.commit()
    return result.rowcount > 0

async def delete_order_and_items(session: AsyncSession, order_id: str):
    """
    FK-তে ON DELETE CASCADE না থাকলে ম্যানুয়াল cascade:
    আগে চাইল্ড, তারপর প্যারেন্ট — নইলে FK ডিলিট প্রত্যাখ্যান করে।
    """
    async with session.begin():
        await session.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
        await session.execute(delete(OrderHeader).where(OrderHeader.order_id == order_id))
```

/// info | কোডটি সহজ ভাষায়

ফরেন কি-তে `ON DELETE CASCADE` না থাকলে ডেটাবেস প্যারেন্ট মুছতে দেয় না, কারণ চাইল্ডরা তখন "এতিম" হয়ে যেত। তাই ক্রম জরুরি: **আগে চাইল্ড, তারপর প্যারেন্ট**। দুটিই একই `begin()` ব্লকে, তাই মাঝপথে ব্যর্থ হলে কিছুই মুছবে না।

///

## 39. প্যাটার্ন ২: Payload-সহ Junction Table (N:M) — Security ও Product { #s39 }

/// tip | উদাহরণ দিয়ে বুঝি

একটি ক্লাবের সদস্যপদ কার্ড ভাবুন। কার্ডে লেখা থাকে কে সদস্য, কোন ক্লাবের, কবে থেকে, আর কবে পর্যন্ত। মানুষ আর ক্লাব দুটোই আলাদা, কার্ডটি তাদের সংযোগ, আর সংযোগের নিজের তথ্যও আছে (তারিখ)। সদস্যপদ বাতিল মানে কার্ডে মেয়াদের শেষ তারিখ লেখা। মানুষ বা ক্লাব কেউ মুছে যায় না।

///

এন্টারপ্রাইজ many-to-many লিংক হলো মেটাডেটা (`from_date`, `thru_date`, `sequence_num`) বহনকারী স্পষ্ট association অবজেক্ট:
- `UserLogin` ↔ `SecurityGroup` — `UserLoginSecurityGroup`-এর মাধ্যমে
- `Product` ↔ `ProductCategory` — `ProductCategoryMember`-এর মাধ্যমে

### 39.1 লিংক তৈরি { #s39-1 }
```python
from datetime import datetime, timezone
from app.models.security import UserLoginSecurityGroup

async def grant_security_group(session: AsyncSession, user_login_id: str, group_id: str) -> UserLoginSecurityGroup:
    """এখন থেকে কার্যকর একটি জাংশন রো ইনসার্ট।"""
    assignment = UserLoginSecurityGroup(
        user_login_id=user_login_id,
        group_id=group_id,
        from_date=datetime.now(timezone.utc),
        thru_date=None,                       # খোলা মেয়াদ = বর্তমানে সক্রিয়
    )
    session.add(assignment)
    await session.commit()
    return assignment
```

/// info | কোডটি সহজ ভাষায়

`thru_date=None` মানে গ্রান্টটি এখনো চলছে, কোনো শেষ তারিখ নেই। `from_date` primary key-র অংশ, তাই একই ইউজারকে একই গ্রুপে আবার নতুন তারিখ দিয়ে যুক্ত করা যায়, ইতিহাস হারায় না।

///

একটি প্রোডাক্টকে একসাথে একাধিক ক্যাটাগরিতে যুক্ত করা:
```python
from app.models.product import ProductCategoryMember

async def categorize_product(session: AsyncSession, product_id: str, category_ids: list[str]):
    now = datetime.now(timezone.utc)
    session.add_all([
        ProductCategoryMember(
            product_id=product_id,
            product_category_id=cat_id,
            from_date=now,
            sequence_num=idx + 1,
        )
        for idx, cat_id in enumerate(category_ids)
    ])
    await session.commit()
```
"Grant"-কে idempotent করতে (আগে থেকে দেওয়া থাকলেও এরর নয়) `pg_insert(...).on_conflict_do_nothing(index_elements=[...])` ব্যবহার করুন ([§34.4](crud.md#s34-4))।

### 39.2 লিংকের মেটাডেটা আপডেট — `thru_date` দিয়ে soft expire { #s39-2 }
পারমিশন মুছে না ফেলে মেয়াদ শেষ করুন — অডিট ট্রেইল থেকে যায়:
```python
from sqlalchemy import select

async def expire_security_group_assignment(session: AsyncSession, user_login_id: str, group_id: str) -> bool:
    stmt = select(UserLoginSecurityGroup).where(
        UserLoginSecurityGroup.user_login_id == user_login_id,
        UserLoginSecurityGroup.group_id == group_id,
        UserLoginSecurityGroup.thru_date.is_(None),       # শুধু সক্রিয় গ্রান্ট
    )
    assignment = (await session.execute(stmt)).scalar_one_or_none()
    if assignment:
        assignment.thru_date = datetime.now(timezone.utc)
        await session.commit()
        return True
    return False
```
তারিখ-কার্যকর রো-র জন্য "বর্তমানে সক্রিয়" কুয়েরি:
```python
now = datetime.now(timezone.utc)
active = select(UserLoginSecurityGroup).where(
    UserLoginSecurityGroup.user_login_id == user_login_id,
    UserLoginSecurityGroup.from_date <= now,
    or_(UserLoginSecurityGroup.thru_date.is_(None), UserLoginSecurityGroup.thru_date > now),
)
```

/// info | "এখন সক্রিয়" মানে কী

একটি গ্রান্ট এখন সক্রিয় যদি:

* শুরু হয়ে গেছে: `from_date <= এখন`, **এবং**
* শেষ হয়নি: `thru_date` ফাঁকা, **অথবা** `thru_date > এখন`।

ভবিষ্যতের তারিখ দিয়ে গ্রান্ট আগেই তৈরি করে রাখা যায়। নির্দিষ্ট দিনে সেটা নিজে থেকেই সক্রিয় হয়ে যাবে।

///

### 39.3 লিংক মোছা — শুধু জাংশন রো, কখনো এন্টিটি নয় { #s39-3 }
```python
async def unlink_user_from_group(session: AsyncSession, user_login_id: str, group_id: str) -> bool:
    """UserLogin ও SecurityGroup দুটোই থাকে; শুধু সংযোগটি মুছে যায়।"""
    result = await session.execute(
        delete(UserLoginSecurityGroup).where(
            UserLoginSecurityGroup.user_login_id == user_login_id,
            UserLoginSecurityGroup.group_id == group_id,
        )
    )
    await session.commit()
    return result.rowcount > 0
```

## 40. প্যাটার্ন ৩: Subtype / Extension Table (1:1) — `Party`, `Person`, `PartyGroup` { #s40 }

/// tip | উদাহরণ দিয়ে বুঝি

প্রত্যেক নাগরিকের একটি সাধারণ পরিচয় আছে (NID নম্বর, ঠিকানা)। এর ওপর কেউ ছাত্র (স্কুল, ক্লাস), কেউ কোম্পানি (ট্রেড লাইসেন্স)। সাধারণ তথ্য থাকে `Party`-তে, বিশেষ তথ্য থাকে `Person` বা `PartyGroup`-এ। দুটি টেবিলে একই id (`party_id`), ঠিক যেমন একই NID নম্বর দিয়ে স্কুলের রেকর্ডও খোঁজা যায়।

///

OFBiz-এ `Party` হলো বেস পরিচয়, আর `Person` (ব্যক্তি) / `PartyGroup` (প্রতিষ্ঠান) হলো সাবটাইপ টেবিল। এরা primary key শেয়ার করে: `Person.party_id` একই সাথে তার PK এবং `Party.party_id`-এর দিকে FK। (SQLAlchemy এটিকে স্বয়ংক্রিয়ভাবে **joined-table inheritance** হিসেবে মডেল করতে পারে, [§44.2](advanced-mapping.md#s44-2); এখানে আমরা টেবিলগুলো আলাদাভাবে হ্যান্ডল করছি।)

### 40.1 বেস + সাবটাইপ তৈরি { #s40-1 }
```python
from app.models.party import Party, Person

async def create_person(session: AsyncSession, party_id: str, first_name: str, last_name: str) -> tuple[Party, Person]:
    async with session.begin():
        now = datetime.now(timezone.utc)

        party = Party(
            party_id=party_id,
            party_type_id="PERSON",
            status_id="PARTY_ENABLED",
            created_date=now,
            last_modified_date=now,
        )
        session.add(party)
        await session.flush()                 # সাবটাইপের FK চেকের আগে বেস রো তৈরি হয়ে থাকে

        person = Person(
            party_id=party.party_id,          # বেস রো-র একই key
            first_name=first_name,
            last_name=last_name,
            salutation="Mr.",
        )
        session.add(person)
    return party, person
```

/// info | কোডটি সহজ ভাষায়

`Person.party_id` একই সাথে primary key আর `Party`-র দিকে ফরেন কি। তাই আগে `Party` রো থাকতে হবে। `flush()` সেটাকে সাথে সাথে ডেটাবেসে পাঠায়, তারপর একই id দিয়ে `Person` যোগ হয়। SQLAlchemy-র [joined table inheritance](advanced-mapping.md#s44-2) এই পুরো কাজটা নিজে থেকেই করে দিতে পারে।

///

### 40.2 বেস + সাবটাইপ একসাথে আপডেট { #s40-2 }
```python
async def update_person_profile(session: AsyncSession, party_id: str, new_first_name: str, new_status: str) -> bool:
    async with session.begin():
        party = await session.get(Party, party_id)
        person = await session.get(Person, party_id)
        if not (party and person):
            return False

        party.status_id = new_status                          # বেস টেবিল
        party.last_modified_date = datetime.now(timezone.utc)
        person.first_name = new_first_name                    # সাবটাইপ টেবিল
    return True
```
অথবা এক রাউন্ড-ট্রিপে দুটোই আনুন: `select(Party, Person).join(Person, Person.party_id == Party.party_id).where(Party.party_id == party_id)`।

### 40.3 আগে সাবটাইপ, তারপর বেস মোছা { #s40-3 }
```python
async def delete_party_cascade(session: AsyncSession, party_id: str):
    """সাবটাইপ রো আগে মুছতে হবে, নইলে FK বেস রো মোছা প্রত্যাখ্যান করবে।"""
    async with session.begin():
        await session.execute(delete(Person).where(Person.party_id == party_id))
        await session.execute(delete(Party).where(Party.party_id == party_id))
```
বাস্তব OFBiz স্কিমায় অনেক টেবিল `Party`-কে রেফার করে (রোল, কন্টাক্ট মেকানিজম, অর্ডার)। মোছার চেয়ে নিষ্ক্রিয় করা (`status_id = "PARTY_DISABLED"`) ভালো।

## 41. CRUD-এ Error Handling ও Transaction Boundary { #s41 }

### 41.1 `IntegrityError` অনুবাদ করা { #s41-1 }
```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

async def safe_create_order(session: AsyncSession, payload: OrderCreate) -> Order:
    try:
        new_order = Order(customer_id=payload.customer_id, order_code=payload.order_code)
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order
    except IntegrityError as exc:
        await session.rollback()             # বাধ্যতামূলক: rollback না করা পর্যন্ত সেশন অকেজো
        # নামযুক্ত কনস্ট্রেইন্ট (§3) থাকায় এই চেক নির্ভরযোগ্য
        if "uq_orders_order_code" in str(exc.orig):
            raise HTTPException(status_code=409, detail=f"Order code '{payload.order_code}' already exists.")
        raise HTTPException(status_code=400, detail="Database integrity constraint violated.")
```

/// info | কোডটি সহজ ভাষায়

* **`await session.rollback()` বাধ্যতামূলক**: এরর হলে সেশন "ব্যর্থ" অবস্থায় চলে যায়। rollback না করে আর কিছু করতে গেলে `PendingRollbackError` আসে।
* `"uq_orders_order_code" in str(exc.orig)`: নামটি নির্দিষ্ট, কারণ [naming convention](models.md#s3) আছে আর মডেলে শুধু `unique=True` দেওয়া ([§33](crud.md#s33-1) দেখুন)।
* `409 Conflict`: "আপনার রিকোয়েস্টটি বর্তমান অবস্থার সাথে সাংঘর্ষিক", ডুপ্লিকেটের জন্য সঠিক কোড।

asyncpg-এ টেক্সট না মিলিয়ে আরও নির্ভরযোগ্যভাবে দেখা যায়। আমাদের পরীক্ষায় পাওয়া মানগুলো:

```python
exc.orig.__cause__.constraint_name   # 'uq_orders_order_code'
exc.orig.sqlstate                    # '23505'  (unique violation)
```

///

asyncpg-এ স্ট্রিং মেলানোর বদলে `exc.orig.__cause__.constraint_name` / `sqlstate` দেখা যায় (`23505` unique, `23503` FK, `23502` not-null, `23514` check)।

### 41.2 ঐচ্ছিক উপ-ধাপের জন্য savepoint { #s41-2 }
```python
async def process_checkout(session: AsyncSession, order: Order):
    async with session.begin():
        session.add(order)
        await session.flush()                            # transaction-এর ভেতরে অর্ডার সংরক্ষিত

        try:
            async with session.begin_nested():           # SAVEPOINT
                await reserve_inventory(session, order.order_id)
        except InventoryShortageError:
            # শুধু রিজার্ভেশন rollback হয়েছে; অর্ডার রয়ে গেছে
            order.status = "BACKORDERED"
```

/// tip | উদাহরণ দিয়ে বুঝি

অনলাইনে অর্ডার দিলেন, কিন্তু একটা জিনিস স্টকে নেই। পুরো অর্ডার বাতিল না করে অর্ডারটা রাখা হলো, শুধু অবস্থা "BACKORDERED" (মাল এলে পাঠানো হবে)। savepoint ঠিক এটাই করে: ইনভেন্টরি রিজার্ভের অংশটুকু বাতিল, অর্ডার টিকে থাকে।

///

খেয়াল করুন, `try` ব্লকটি `begin_nested()` ব্লককে ঘিরে আছে — এক্সেপশন ব্লক ছেড়ে বের হওয়ার সময় savepoint rollback হয়।

### 41.3 Related-table কাজের নিয়ম { #s41-3 }

/// warning | গুরুত্বপূর্ণ

**`async with session.begin():` দিয়ে atomicity নিশ্চিত করুন।** একাধিক টেবিলের কাজ (অর্ডার + আইটেম, party + person) কখনো আলাদা transaction-এ করবেন না। ৫টির মধ্যে ৩ নম্বর আইটেম ব্যর্থ হলে সবকিছু rollback হতে হবে।

///

/// tip | পরামর্শ

**`flush()` বনাম `commit()` জানুন।** `await session.flush()` SQL পাঠায় এবং তৈরি হওয়া key পাওয়া যায়, কিন্তু transaction খোলা রাখে; `commit()` তা স্থায়ী করে।

///

/// danger | বিপদ

**লিংক মুছুন, টার্গেট নয়।** Many-to-many-তে অ্যাক্সেস সরানোর অর্থ শুধু জাংশন রো (`UserLoginSecurityGroup`) মোছা (বা মেয়াদ শেষ করা) — কখনোই `UserLogin` বা `SecurityGroup`-এ `delete()` নয়।

///

/// note | নোট

FK-তে `ON DELETE CASCADE` না থাকলে **প্যারেন্টের আগে চাইল্ড মুছুন**; ইনসার্টে প্যারেন্ট আগে, চাইল্ড পরে (ORM অবজেক্টের ক্ষেত্রে unit of work এটা করে দেয়, কিন্তু আলাদা আলাদা `execute()` স্টেটমেন্টে নয়)।

///

/// check | সংক্ষেপে মনে রাখুন

* একাধিক টেবিলে লেখা = একটি `async with session.begin():`।
* ঢোকানো: আগে প্যারেন্ট (`flush()`), তারপর চাইল্ড। মোছা: আগে চাইল্ড, তারপর প্যারেন্ট। রিলেশনশিপ কালেকশন দিলে SQLAlchemy নিজেই ক্রম ঠিক করে।
* N:M-এ সংযোগ সরানো মানে জাংশন রো মোছা বা `thru_date` দেওয়া, এন্টিটি মোছা নয়।
* সাবটাইপ টেবিল: বেস → `flush()` → একই key দিয়ে সাবটাইপ।
* `IntegrityError` ধরলে আগে `rollback()`, তারপর 409/400।

///

**পরের ধাপ:** সবকিছু জুড়ে দিন [পূর্ণ FastAPI প্রজেক্ট](fastapi-project.md) অধ্যায়ে।
