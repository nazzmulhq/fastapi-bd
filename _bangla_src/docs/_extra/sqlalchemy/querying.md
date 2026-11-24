# কুয়েরি: select() ও JOIN { #sqlalchemy-querying }

/// note | এই পেজে যা শিখবেন

* `select()` দিয়ে কুয়েরি বানানো: ফিল্টার, সর্ট, limit, aggregate, `GROUP BY`।
* `scalars()`, `execute()`, `scalar()`, `get()`-এর পার্থক্য, আর `.all()`, `.first()`, `.one()` কখন।
* এন্টারপ্রাইজ-ধাঁচের একটি রেফারেন্স স্কিমা (পুরো মডেল কোডসহ)।
* সব ধরনের JOIN: inner, left outer, চেইন, self-join, aggregate-সহ join।
* কখন JOIN আর কখন eager loading।

///

/// tip | উদাহরণ দিয়ে বুঝি

লাইব্রেরিতে গিয়ে লাইব্রেরিয়ানকে একটি চিরকুট দিলেন: "রবীন্দ্রনাথের লেখা বই, নাম অনুযায়ী সাজিয়ে, প্রথম ১০টি।" **`select()`** হলো সেই চিরকুট লেখা। চিরকুট লিখলেই বই আসে না, লাইব্রেরিয়ানের হাতে দিতে হয়। সেটাই **`await session.scalars(stmt)`**।

///

## 24. `select()`-এর মূল বিষয় ও Result মেথড { #s24 }

### 24.1 স্টেটমেন্ট তৈরি { #s24-1 }

প্রথমে একদম সহজ কয়েকটি উদাহরণ। ধরুন এই মডেলটি আছে:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
    age: Mapped[int | None]
    is_active: Mapped[bool] = mapped_column(default=True)
```

```python
from sqlalchemy import func, or_, select

# ১. সব ইউজার
users = (await session.scalars(select(User))).all()

# ২. শর্তসহ: সক্রিয় এবং ১৮ বা তার বেশি বয়স
stmt = select(User).where(User.is_active.is_(True), User.age >= 18)

# ৩. "অথবা"
stmt = select(User).where(or_(User.name == "রহিম", User.name == "করিম"))

# ৪. সাজানো + পেজ: নাম অনুযায়ী, ২১ থেকে ৩০ নম্বর
stmt = select(User).order_by(User.name).limit(10).offset(20)

# ৫. পুরো অবজেক্ট নয়, শুধু কিছু কলাম
rows = (await session.execute(select(User.id, User.email).where(User.email.ilike("%@gmail.com")))).all()

# ৬. গণনা
total = await session.scalar(select(func.count()).select_from(User))
```

প্রতিটি কোন SQL বানায় দেখতে শুধু `print(stmt)` লিখুন:

```sql
-- ২ নম্বর
SELECT users.id, users.name, users.email, users.age, users.is_active
FROM users
WHERE users.is_active IS true AND users.age >= :age_1

-- ৪ নম্বর
SELECT users.id, users.name, ... FROM users ORDER BY users.name LIMIT :param_1 OFFSET :param_2
```

/// info | কোডটি সহজ ভাষায়

* `select(User)` একটি কুয়েরি **বানায়**, চালায় না। তাই ধাপে ধাপে `.where()`, `.order_by()` যোগ করা যায়।
* `.where(a, b)`-এ কমা দিয়ে একাধিক শর্ত মানে `AND`।
* `:age_1` হলো প্যারামিটারের জায়গা। আসল মান আলাদা পাঠানো হয়, তাই SQL injection হয় না।
* `User.is_active.is_(True)`: `== True` লিখলে Python লিন্টার আপত্তি করে, তাই `.is_()` ব্যবহার করা হয়।

///

এবার একটি বড়, বাস্তব রিপোর্ট কুয়েরি:

স্টেটমেন্ট অপরিবর্তনীয় (immutable) বিল্ডার — প্রতিটি মেথড একটি নতুন স্টেটমেন্ট রিটার্ন করে, তাই শর্তসাপেক্ষে ধাপে ধাপে তৈরি করা যায়।

```python
from sqlalchemy import and_, desc, func, not_, nulls_last, or_, select

stmt = (
    select(
        Order.customer_id,
        func.count(Order.order_id).label("total_orders"),
        func.sum(Order.total_amount).label("lifetime_spend"),
        func.coalesce(func.avg(Order.total_amount), 0).label("average_order_value"),
    )
    .where(
        and_(
            Order.status.in_(["COMPLETED", "SHIPPED"]),
            Order.total_amount > 50,
            not_(Order.is_deleted),
        )
    )
    .group_by(Order.customer_id)
    .having(func.count(Order.order_id) >= 3)
    .order_by(nulls_last(desc("lifetime_spend")))
    .limit(100)
    .offset(0)
)
rows = (await session.execute(stmt)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

"প্রতি গ্রাহকের মোট অর্ডার সংখ্যা, মোট খরচ আর গড় অর্ডার মূল্য বের করো। শুধু COMPLETED বা SHIPPED অর্ডার, যাদের মূল্য ৫০-এর বেশি আর যা মুছে ফেলা হয়নি। শুধু সেই গ্রাহক যাদের অন্তত ৩টি অর্ডার আছে। সবচেয়ে বেশি খরচকারী আগে, প্রথম ১০০ জন।"

* `func.count(...)`, `func.sum(...)`, `func.avg(...)`: SQL-এর `COUNT`, `SUM`, `AVG`। `func.` দিয়ে যেকোনো SQL ফাংশন ডাকা যায়।
* `.label("total_orders")`: ফলাফলের কলামের নাম।
* `func.coalesce(x, 0)`: `x` NULL হলে ০।
* `.group_by(Order.customer_id)`: প্রতি গ্রাহকের জন্য একটি রো।
* `.having(...)`: গ্রুপ হওয়ার **পরের** শর্ত। `where` চলে গ্রুপের আগে, `having` পরে।
* `.mappings().all()`: প্রতিটি রো dict-এর মতো, যেমন `row["lifetime_spend"]`।

///

প্রচলিত কলাম অপারেটর:

| এক্সপ্রেশন | SQL |
| :--- | :--- |
| `col == v`, `col != v`, `col > v` | `=`, `!=`, `>` |
| `col.in_([...])`, `col.not_in([...])` | `IN`, `NOT IN` |
| `col.is_(None)`, `col.is_not(None)` | `IS NULL`, `IS NOT NULL` |
| `col.like("a%")`, `col.ilike("%x%")` | `LIKE`, `ILIKE` |
| `col.between(a, b)` | `BETWEEN` |
| `col.startswith("a")`, `col.contains("x")` | `LIKE 'a%'`, `LIKE '%x%'` |
| `and_(...)`, `or_(...)`, `not_(...)` | `AND`, `OR`, `NOT` |
| `.where(a, b)`-এ একাধিক আর্গুমেন্ট | `AND` দিয়ে যুক্ত |

### 24.2 এক্সিকিউট ও রেজাল্ট ব্যবহার { #s24-2 }

| কল | রিটার্ন করে | কখন ব্যবহার করবেন |
| :--- | :--- | :--- |
| `await session.get(Model, pk)` | অবজেক্ট অথবা `None` | Primary key দিয়ে খোঁজা (আগে identity map) |
| `await session.scalars(stmt)` | `ScalarResult` | প্রতি রো-তে একটি এন্টিটি/কলাম |
| `await session.scalar(stmt)` | প্রথম মান অথবা `None` | একক স্কেলার (`count`, `max`, একটি অবজেক্ট) |
| `await session.execute(stmt)` | `Row`-এর `Result` | প্রতি রো-তে একাধিক এন্টিটি/কলাম |
| `.all()` | list | সবকিছু |
| `.first()` | প্রথম রো অথবা `None` | বাকি রো নিয়ে মাথাব্যথা নেই |
| `.one()` | ঠিক একটি রো, নইলে এরর | অবশ্যই থাকবে এবং ইউনিক |
| `.one_or_none()` / `.scalar_one_or_none()` | রো/`None`, > ১ হলে এরর | ঐচ্ছিক ইউনিক রো |
| `.scalar_one()` | মানটি, ০ বা > ১ হলে এরর | `count(*)` ইত্যাদি |
| `.mappings()` | dict-সদৃশ `RowMapping` | রিপোর্টের জন্য JSON-বান্ধব রো |
| `.unique()` | ডুপ্লিকেট-মুক্ত রেজাল্ট | কালেকশনে `joinedload()` / `contains_eager`-এ **বাধ্যতামূলক** |
| `.partitions(n)` | চাঙ্ক | ব্যাচ প্রসেসিং |
| `await session.stream(stmt)` / `stream_scalars` | async iterator | বিশাল রেজাল্ট সেট ([§48.3](performance.md#s48-3)) |

/// tip | `scalars()` নাকি `execute()`?

```python
# scalars(): প্রতিটি রো-র প্রথম জিনিসটি — এখানে User অবজেক্ট
users = (await session.scalars(select(User))).all()
users[0].name                   # "রহিম"

# execute(): প্রতিটি রো একটি Row (টাপলের মতো) — একাধিক জিনিস থাকলে
rows = (await session.execute(select(User.name, User.email))).all()
rows[0].name, rows[0].email     # ("রহিম", "rahim@example.com")

# execute() দিয়ে এন্টিটি আনলে প্রতিটি রো (User,) — একটা বাড়তি মোড়ক
rows = (await session.execute(select(User))).all()
rows[0][0].name                 # তাই এন্টিটির জন্য scalars() সহজ
```

মনে রাখার নিয়ম: **একটা জিনিস চাইলে `scalars()`, একাধিক কলাম বা এন্টিটি চাইলে `execute()`।**

///

### 24.3 Async-এর বিশেষ দিক { #s24-3 }
- `session.execute()`, `session.scalars()`, `session.scalar()`, `session.get()` — সবগুলো `await` করতে হবে।
- ফেরত আসা `Result` আগেই মেমরিতে বাফার করা থাকে, তাই এর উপর `.all()` / `.scalars()` সাধারণ (await-ছাড়া) কল।
- `session.stream()` একটি `AsyncResult` দেয়, যার মেথডগুলো **await / async-iterate করতে হয়**।

## 25. রেফারেন্স মডেল: OFBiz-ধাঁচের এন্টারপ্রাইজ স্কিমা { #s25 }

/// note | OFBiz কী?

[Apache OFBiz](https://ofbiz.apache.org/) একটি ওপেন-সোর্স ERP (ব্যবসার হিসাব-নিকাশ, অর্ডার, ইনভেন্টরি, পার্টি ব্যবস্থাপনার সফটওয়্যার)। এর ডেটাবেস নকশা বড় কোম্পানির সিস্টেমে খুব প্রচলিত: `"ORD_1001"`-এর মতো স্ট্রিং id, চাইল্ড টেবিলে দুই কলামের (composite) primary key, আর অনেক জাংশন টেবিল। বাস্তব এন্টারপ্রাইজ প্রজেক্টে এমন স্কিমার মুখোমুখি হবেন, তাই এই অধ্যায় আর [সম্পর্কিত টেবিলে CRUD](related-crud.md) অধ্যায়ে এটি ব্যবহার করা হয়েছে।

///

কুয়েরি অধ্যায় ও [সম্পর্কিত টেবিলে CRUD](related-crud.md) অধ্যায়ের উদাহরণগুলো একটি এন্টারপ্রাইজ-ধাঁচের স্কিমা ব্যবহার করে (মডেলগুলো `order.py`, `party.py`, `product.py`, `security.py` ফাইলে রাখা হয়েছে ধরে নিচ্ছি), যা Apache OFBiz-এর এন্টারপ্রাইজ প্যাটার্ন অনুসরণ করে: স্ট্রিং primary key, চাইল্ড টেবিলে composite key, এবং `__table_args__`-এর ভেতরে `ForeignKeyConstraint` দিয়ে ঘোষিত ফরেন কি।

| রিলেশনশিপ প্যাটার্ন | প্রধান মডেল | মূল কলাম ও ম্যাপিং |
| :--- | :--- | :--- |
| **Parent-child (1:N)** | `OrderHeader` → `OrderItem` | `OrderHeader.order_id` (PK) ↔ `OrderItem.order_id` (composite PK-এর অংশ + FK) |
| **Many-to-many (N:M)** | `UserLogin` ↔ `SecurityGroup` | জাংশন `UserLoginSecurityGroup` (`user_login_id`, `group_id`, `from_date`) |
| **Many-to-many (N:M)** | `Product` ↔ `ProductCategory` | জাংশন `ProductCategoryMember` (`product_id`, `product_category_id`, `from_date`) |
| **Self-reference** | `ProductCategory` → `ProductCategory` | `primary_parent_category_id` → `product_category_id` |
| **Subtype (1:1)** | `Party` ↔ `Person` / `PartyGroup` | `Party.party_id` (PK) ↔ `Person.party_id` (PK + FK) |

এই টেবিলগুলোর সাথে কাজের দুটি পরিপূরক উপায়:
1. **Explicit SQL JOIN** — `select().join(Target, onclause)`; কোনো `relationship()` লাগে না।
2. **Declarative `relationship()`** এবং eager loader (`selectinload`, `joinedload`, `contains_eager`)।

যেসব উদাহরণে `OrderHeader.items` বা `OrderItem.order_header` ব্যবহৃত হয়েছে, সেখানে ধরে নেওয়া হয়েছে মডেলে এমন রিলেশনশিপ যোগ করা আছে:
```python
# OrderHeader-এ
items: Mapped[list["OrderItem"]] = relationship(
    back_populates="order_header", cascade="all, delete-orphan", lazy="raise"
)
# OrderItem-এ
order_header: Mapped["OrderHeader"] = relationship(back_populates="items", lazy="raise")
```

নিচে এই অধ্যায়ের সব উদাহরণে ব্যবহৃত মডেলগুলোর পুরো কোড দেওয়া হলো। নিজের কম্পিউটারে চালিয়ে দেখতে চাইলে এটি কপি করে নিন।

/// details | পুরো রেফারেন্স মডেল কোড দেখুন

```python
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, ForeignKeyConstraint, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base   # §3-এর naming convention-সহ Base


# ---------- অর্ডার: Parent-child (1:N), composite PK ----------
class OrderHeader(Base):
    __tablename__ = "order_header"

    order_id: Mapped[str] = mapped_column(String(20), primary_key=True)        # স্ট্রিং PK
    order_type_id: Mapped[str] = mapped_column(String(20))
    order_name: Mapped[Optional[str]] = mapped_column(String(100))
    status_id: Mapped[Optional[str]] = mapped_column(String(20))
    order_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    entry_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    grand_total: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    currency_uom: Mapped[Optional[str]] = mapped_column(String(3))

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order_header", cascade="all, delete-orphan", lazy="raise"
    )


class OrderItem(Base):
    __tablename__ = "order_item"
    __table_args__ = (
        # OFBiz ধাঁচ: ফরেন কি __table_args__-এর ভেতরে
        ForeignKeyConstraint(["order_id"], ["order_header.order_id"], name="fk_order_item_order_header"),
        ForeignKeyConstraint(["product_id"], ["product.product_id"], name="fk_order_item_product"),
    )

    order_id: Mapped[str] = mapped_column(String(20), primary_key=True)            # composite PK-এর অংশ + FK
    order_item_seq_id: Mapped[str] = mapped_column(String(20), primary_key=True)   # "00001", "00002" …
    order_item_type_id: Mapped[Optional[str]] = mapped_column(String(20))
    product_id: Mapped[Optional[str]] = mapped_column(String(20))
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6))
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    status_id: Mapped[Optional[str]] = mapped_column(String(20))

    order_header: Mapped["OrderHeader"] = relationship(back_populates="items", lazy="raise")


# ---------- প্রোডাক্ট ও ক্যাটাগরি: N:M জাংশন + self-reference ----------
class Product(Base):
    __tablename__ = "product"

    product_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    product_type_id: Mapped[Optional[str]] = mapped_column(String(20))
    internal_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)


class ProductCategory(Base):
    __tablename__ = "product_category"

    product_category_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100))
    primary_parent_category_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("product_category.product_category_id")                       # নিজের টেবিলের দিকে FK
    )


class ProductCategoryMember(Base):
    """Product ↔ ProductCategory জাংশন, সাথে মেয়াদ ও ক্রম (payload)।"""
    __tablename__ = "product_category_member"

    product_id: Mapped[str] = mapped_column(ForeignKey("product.product_id"), primary_key=True)
    product_category_id: Mapped[str] = mapped_column(
        ForeignKey("product_category.product_category_id"), primary_key=True
    )
    from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    thru_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sequence_num: Mapped[Optional[int]]


# ---------- সিকিউরিটি: UserLogin ↔ SecurityGroup (N:M) ----------
class UserLogin(Base):
    __tablename__ = "user_login"

    user_login_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    enabled: Mapped[str] = mapped_column(String(1), default="Y")                  # "Y" / "N"


class SecurityGroup(Base):
    __tablename__ = "security_group"

    group_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))


class UserLoginSecurityGroup(Base):
    __tablename__ = "user_login_security_group"

    user_login_id: Mapped[str] = mapped_column(ForeignKey("user_login.user_login_id"), primary_key=True)
    group_id: Mapped[str] = mapped_column(ForeignKey("security_group.group_id"), primary_key=True)
    from_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    thru_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))   # NULL = এখনো সক্রিয়


# ---------- Party: বেস + সাবটাইপ (shared PK, 1:1) ----------
class Party(Base):
    __tablename__ = "party"

    party_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    party_type_id: Mapped[str] = mapped_column(String(20))                        # "PERSON" / "PARTY_GROUP"
    status_id: Mapped[Optional[str]] = mapped_column(String(20))
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_modified_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Person(Base):
    __tablename__ = "person"

    party_id: Mapped[str] = mapped_column(ForeignKey("party.party_id"), primary_key=True)  # PK + FK একসাথে
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    salutation: Mapped[Optional[str]] = mapped_column(String(20))


class PartyGroup(Base):
    __tablename__ = "party_group"

    party_id: Mapped[str] = mapped_column(ForeignKey("party.party_id"), primary_key=True)
    group_name: Mapped[Optional[str]] = mapped_column(String(100))


# ---------- ইনভেন্টরি (Concurrency অধ্যায়ে ব্যবহৃত) ----------
class InventoryItem(Base):
    __tablename__ = "inventory_item"

    inventory_item_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("product.product_id"))
    available_to_promise_total: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=Decimal("0"))
```

///

## 26. Explicit JOIN: Inner, Outer, Chain, Self-Join ও Aggregate { #s26 }

/// tip | উদাহরণ দিয়ে বুঝি

দুটি তালিকা কল্পনা করুন। একটিতে ছাত্রদের নাম, আরেকটিতে পরীক্ষার নম্বর (রোল দিয়ে মেলানো)।

| ছাত্র | | নম্বর |
| :--- | :--- | :--- |
| ১ রহিম | | ১ → ৮০ |
| ২ করিম | | ৩ → ৯০ |
| ৩ সুমি | | |

* **Inner join**: যাদের নাম আর নম্বর দুটোই আছে → রহিম ৮০, সুমি ৯০। করিম বাদ।
* **Left outer join**: বাঁ দিকের (ছাত্র) সবাই, নম্বর না থাকলে ফাঁকা → রহিম ৮০, করিম —, সুমি ৯০।

///

### 26.1 Inner join { #s26-1 }
শুধু সেই রো যেখানে দুই দিকেই মিল আছে:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderHeader, OrderItem

async def get_order_with_items(session: AsyncSession, order_id: str):
    stmt = (
        select(OrderHeader, OrderItem)
        .join(OrderItem, OrderHeader.order_id == OrderItem.order_id)
        .where(OrderHeader.order_id == order_id)
    )
    result = await session.execute(stmt)

    rows = result.all()                       # (OrderHeader, OrderItem) টাপলের তালিকা
    for header, item in rows:
        print(f"Order: {header.order_id}, Seq: {item.order_item_seq_id}, Product: {item.product_id}")
    return rows
```

/// info | তৈরি হওয়া SQL

```sql
SELECT order_header.*, order_item.*
FROM order_header
JOIN order_item ON order_header.order_id = order_item.order_id
WHERE order_header.order_id = $1
```

ফলাফলের প্রতিটি রো একটি `(OrderHeader, OrderItem)` জোড়া। একটি অর্ডারে ৩টি আইটেম থাকলে ৩টি রো, প্রতিটিতে একই `header` অবজেক্ট (identity map-এর কারণে মেমরিতে একটাই)।

///

রিলেশনশিপ থাকলে `.join(OrderHeader.items)` লেখা যায়; SQLAlchemy নিজেই `ON` ক্লজ বের করে।

### 26.2 Left outer join (`isouter=True`) { #s26-2 }
বাম দিকের প্রতিটি রো রাখা, মিল না থাকলেও — যেমন কোনো সিকিউরিটি গ্রুপ নেই এমন ইউজারও:
```python
from app.models.security import UserLogin, UserLoginSecurityGroup

async def get_users_with_optional_groups(session: AsyncSession):
    stmt = (
        select(UserLogin.user_login_id, UserLoginSecurityGroup.group_id)
        .join(
            UserLoginSecurityGroup,
            UserLogin.user_login_id == UserLoginSecurityGroup.user_login_id,
            isouter=True,                     # LEFT OUTER JOIN
        )
        .where(UserLogin.enabled == "Y")
    )
    return (await session.execute(stmt)).all()
```

/// info | কোডটি সহজ ভাষায়

`guest` ইউজারের কোনো সিকিউরিটি গ্রুপ না থাকলেও তিনি ফলাফলে আসবেন, `group_id` হবে `None`:

```python
[("admin", "FULLADMIN"), ("guest", None)]
```

"যাদের কোনো গ্রুপ **নেই**" শুধু তাদের চাইলে: `.where(UserLoginSecurityGroup.group_id.is_(None))` যোগ করুন।

///

`select(...).outerjoin(Target, onclause)` সমতুল্য লেখা। `full=True` দিলে `FULL OUTER JOIN` হয়।

### 26.3 মাল্টি-টেবিল চেইন join (৪টি টেবিল) { #s26-3 }
**OrderHeader → OrderItem → Product → ProductCategoryMember**:
```python
from app.models.product import Product, ProductCategoryMember

async def get_order_line_catalog_details(session: AsyncSession, order_id: str):
    stmt = (
        select(
            OrderHeader.order_id,
            OrderHeader.order_date,
            OrderItem.order_item_seq_id,
            OrderItem.quantity,
            OrderItem.unit_price,
            Product.product_id,
            Product.product_type_id,
            ProductCategoryMember.product_category_id,
        )
        .join(OrderItem, OrderHeader.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .join(
            ProductCategoryMember,
            Product.product_id == ProductCategoryMember.product_id,
            isouter=True,                     # ক্যাটাগরি নেই এমন প্রোডাক্টও আসবে
        )
        .where(OrderHeader.order_id == order_id)
    )
    return (await session.execute(stmt)).mappings().all()   # ডিকশনারি-সদৃশ রো
```

/// info | কোডটি সহজ ভাষায়

চারটি টেবিল পরপর জোড়া: **অর্ডার → আইটেম → প্রোডাক্ট → ক্যাটাগরি**। প্রথম তিনটি inner join, কারণ আইটেমের প্রোডাক্ট থাকবেই। শেষেরটি outer join, কারণ সব প্রোডাক্ট কোনো ক্যাটাগরিতে নাও থাকতে পারে। যেটি থাকে না সেখানে `product_category_id` হবে `None`।

///

প্রতিটি `.join()` সবচেয়ে বামের সেই এন্টিটি থেকে join করে যা টার্গেটে পৌঁছাতে পারে; "from" দিক দ্ব্যর্থ হলে `select_from(...)` ব্যবহার করুন অথবা উপরের মতো স্পষ্ট `ON` ক্লজ দিন।

### 26.4 `aliased()` দিয়ে self-referential join { #s26-4 }
নিজের সাথে join করা টেবিলের দুটি নাম লাগে — `aliased()` দ্বিতীয়টি তৈরি করে:
```python
from sqlalchemy.orm import aliased
from app.models.product import ProductCategory

async def get_category_hierarchy(session: AsyncSession):
    ParentCategory = aliased(ProductCategory, name="parent_category")

    stmt = (
        select(
            ProductCategory.product_category_id.label("sub_category_id"),
            ProductCategory.category_name.label("sub_category_name"),
            ParentCategory.product_category_id.label("parent_category_id"),
            ParentCategory.category_name.label("parent_category_name"),
        )
        .join(
            ParentCategory,
            ProductCategory.primary_parent_category_id == ParentCategory.product_category_id,
            isouter=True,                     # রুট ক্যাটাগরির কোনো প্যারেন্ট নেই
        )
    )
    return (await session.execute(stmt)).mappings().all()
```

/// tip | উদাহরণ দিয়ে বুঝি

একই টেবিলকে দুই ভূমিকায় দেখতে হচ্ছে: একবার "সন্তান ক্যাটাগরি", একবার "প্যারেন্ট ক্যাটাগরি"। একই মানুষকে দুটি নামের ব্যাজ পরানোর মতো। `aliased()` দ্বিতীয় ব্যাজটি দেয়, যাতে SQL-এ দুই ভূমিকা আলাদা করা যায়:

```sql
SELECT product_category.product_category_id AS sub_category_id, ...,
       parent_category.product_category_id AS parent_category_id, ...
FROM product_category
LEFT OUTER JOIN product_category AS parent_category
     ON product_category.primary_parent_category_id = parent_category.product_category_id
```

///

এটি এক স্তর দেয়। পুরো পূর্বপুরুষ/উত্তরসূরি চেইনের জন্য recursive CTE ব্যবহার করুন ([§27](advanced-queries.md#s27))।

### 26.5 Aggregation ও `GROUP BY`-সহ join { #s26-5 }
প্রতি অর্ডারে আইটেম সংখ্যা ও আয়:
```python
from sqlalchemy import func

async def get_order_revenue_breakdown(session: AsyncSession):
    line_total = OrderItem.quantity * OrderItem.unit_price
    stmt = (
        select(
            OrderHeader.order_id,
            OrderHeader.order_name,
            func.count(OrderItem.order_item_seq_id).label("total_items"),
            func.sum(line_total).label("calculated_total"),
        )
        .join(OrderItem, OrderHeader.order_id == OrderItem.order_id)
        .group_by(OrderHeader.order_id, OrderHeader.order_name)
        .having(func.count(OrderItem.order_item_seq_id) > 0)
        .order_by(func.sum(line_total).desc())
    )
    return (await session.execute(stmt)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

* `line_total = OrderItem.quantity * OrderItem.unit_price`: Python-এ লেখা গুণ, SQL-এ হয়ে যায় `order_item.quantity * order_item.unit_price`। একবার বানিয়ে কয়েক জায়গায় ব্যবহার করা যায়।
* ফলাফল: প্রতি অর্ডারে একটি রো, যেমন `("ORD_1001", 3, Decimal("4550.00"))`, সবচেয়ে বেশি আয়ের অর্ডার আগে।

///

নিয়ম: সিলেক্ট করা প্রতিটি non-aggregate কলাম `group_by()`-এ থাকতে হবে (গ্রুপ করা primary key-র উপর functionally dependent কলাম PostgreSQL বাদ দিতে দেয়)।

### 26.6 Join বনাম eager loading — কোনটি কখন? { #s26-6 }
| লক্ষ্য | ব্যবহার করুন |
| :--- | :--- |
| একাধিক টেবিল থেকে ফ্ল্যাট রো / রিপোর্ট কলাম | স্পষ্ট `join()` + সিলেক্ট করা কলাম + `.mappings()` |
| চাইল্ডের শর্তে প্যারেন্ট ফিল্টার করে প্যারেন্ট রিটার্ন | `join()` + `where()` (+ `.distinct()` বা `.unique()`) |
| চাইল্ডসহ প্যারেন্ট অবজেক্ট রিটার্ন | `selectinload()` / `joinedload()` |
| শুধু **মিলে যাওয়া** চাইল্ডসহ প্যারেন্ট রিটার্ন | `join()` + `where()` + `contains_eager()` + `.unique()` |

```python
from sqlalchemy.orm import contains_eager

async def get_orders_filtered_by_item_status(session: AsyncSession):
    stmt = (
        select(OrderHeader)
        .join(OrderHeader.items)
        .where(OrderItem.status_id == "ITEM_APPROVED")
        .options(contains_eager(OrderHeader.items))     # items = শুধু অনুমোদিতগুলো
    )
    result = await session.execute(stmt)
    return result.unique().scalars().all()
```

/// warning | `.unique()` কেন?

JOIN-এর কারণে একটি অর্ডারে দুটি অনুমোদিত আইটেম থাকলে অর্ডারটি দুটি রো-তে আসে। `.unique()` একই অর্ডারকে একবার রাখে। কালেকশনে `contains_eager()` বা `joinedload()` ব্যবহার করলে `.unique()` না দিলে SQLAlchemy 2.0 নিজেই এরর দেয়।

///

```python
from sqlalchemy.orm import joinedload, selectinload

# কালেকশন: selectinload (২টি কুয়েরি, রো গুণিত হয় না)
stmt = select(OrderHeader).where(OrderHeader.order_id == order_id).options(selectinload(OrderHeader.items))

# স্কেলার প্যারেন্ট: joinedload (১টি কুয়েরি, LEFT OUTER JOIN)
stmt = (
    select(OrderItem)
    .where(OrderItem.order_id == order_id, OrderItem.order_item_seq_id == seq_id)
    .options(joinedload(OrderItem.order_header))
)
```

/// check | সংক্ষেপে মনে রাখুন

* `select()` কুয়েরি বানায়; `await session.scalars()` / `execute()` চালায়।
* একটা জিনিস চাইলে `scalars()`, একাধিক কলাম চাইলে `execute()`; dict চাইলে `.mappings()`।
* `.one()` = ঠিক একটি, `.one_or_none()` = শূন্য বা একটি, `.first()` = প্রথমটি, `.all()` = সব।
* `.join(Target, onclause)` = inner, `isouter=True` = left outer; একই টেবিল দুবার লাগলে `aliased()`।
* রিপোর্টে JOIN + কলাম; অবজেক্টসহ চাইল্ড চাইলে `selectinload()`।

///

**পরের ধাপ:** CTE, recursive tree আর window function দেখুন [অ্যাডভান্সড কুয়েরি](advanced-queries.md) অধ্যায়ে।
