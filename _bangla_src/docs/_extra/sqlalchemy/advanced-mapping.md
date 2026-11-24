# অ্যাডভান্সড ম্যাপিং ও Event { #sqlalchemy-advanced-mapping }

/// note | এই পেজে যা শিখবেন

* polymorphic inheritance: একটি বেস ক্লাস, অনেক ধরন (single, joined, concrete)।
* `@hybrid_property`: একই প্রপার্টি Python-এও চলে, SQL কুয়েরিতেও।
* `composite()` দিয়ে value object, association proxy দিয়ে জাংশনের ধাপ লুকানো, `MutableDict` দিয়ে JSON-এর পরিবর্তন ট্র্যাক।
* event hook: অডিট টাইমস্ট্যাম্প, স্লো-কুয়েরি লগ; আর `TypeDecorator` দিয়ে কলাম এনক্রিপশন।

///

## 44. Polymorphic Inheritance: Single, Joined, Concrete { #s44 }

/// tip | উদাহরণ দিয়ে বুঝি

একটি দোকানে পেমেন্ট নেওয়া হয় কয়েক ভাবে: কার্ড, বিকাশ, ক্যাশ। সব পেমেন্টের কিছু জিনিস এক (টাকার পরিমাণ, তারিখ), কিছু আলাদা (কার্ডের শেষ ৪ অঙ্ক, বিকাশের ট্রানজ্যাকশন id)। Python-এ এটা স্বাভাবিকভাবে লেখা যায়: `class Payment` আর তার সন্তান `CardPayment`, `BkashPayment`। প্রশ্ন হলো ডেটাবেসে কীভাবে রাখবেন। তিনটি উপায় আছে, নিচের ছবি আর টেবিলে।

///

```
1. Single Table Inheritance     2. Joined Table Inheritance      3. Concrete Table Inheritance
+-------------------------+     +-------------------------+     +-------------------------+
|      employees          |     |        employees        |     |     hourly_employees    |
+-------------------------+     +-------------------------+     +-------------------------+
| id                      |     | id (PK)                 |     | id (PK), name, rate     |
| type ("hourly"/"sal")   |     | type                    |     +-------------------------+
| name                    |     | name                    |     +-------------------------+
| hourly_rate (nullable)  |     +-------------------------+     |    salaried_employees   |
| annual_salary (nullable)|                  ^                  +-------------------------+
+-------------------------+                  |                  | id (PK), name, salary   |
                                +-------------------------+     +-------------------------+
                                |     salaried_employees  |
                                +-------------------------+
                                | id (PK, FK -> employees)|
                                | annual_salary           |
                                +-------------------------+
```

| স্ট্র্যাটেজি | টেবিল | সুবিধা | অসুবিধা |
| :--- | :--- | :--- | :--- |
| **Single (STI)** | ১টি | দ্রুততম কুয়েরি, join নেই | সাবক্লাসের কলাম ফাঁকা ও nullable; সাবক্লাস-ভিত্তিক NOT NULL সম্ভব নয় |
| **Joined (JTI)** | ১টি বেস + প্রতি সাবক্লাসে ১টি | নর্মালাইজড, সাবক্লাস-ভিত্তিক কনস্ট্রেইন্ট | Polymorphic কুয়েরিতে JOIN লাগে |
| **Concrete** | প্রতি ক্লাসে ১টি, শেয়ার্ড টেবিল নেই | স্বাধীন টেবিল | Polymorphic কুয়েরিতে UNION লাগে; খুব কমই লাভজনক |

### 44.1 Single Table Inheritance { #s44-1 }
```python
from decimal import Decimal
from typing import Optional

class Payment(Base):
    __tablename__ = "payments"
    payment_id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_type: Mapped[str] = mapped_column(String(30))        # discriminator কলাম

    __mapper_args__ = {
        "polymorphic_on": payment_type,
        "polymorphic_identity": "generic_payment",
    }

class CreditCardPayment(Payment):          # __tablename__ নেই → একই টেবিল
    card_last4: Mapped[Optional[str]] = mapped_column(String(4))
    stripe_charge_id: Mapped[Optional[str]] = mapped_column(String(64))
    __mapper_args__ = {"polymorphic_identity": "credit_card"}

class CryptoPayment(Payment):
    wallet_address: Mapped[Optional[str]] = mapped_column(String(128))
    blockchain_tx_hash: Mapped[Optional[str]] = mapped_column(String(128))
    __mapper_args__ = {"polymorphic_identity": "crypto"}
```

/// info | কোডটি সহজ ভাষায়

* একটিই টেবিল `payments`। `payment_type` কলামে লেখা থাকে রো-টি কোন ধরনের (`"credit_card"`, `"crypto"`)। একে বলে **discriminator**।
* `select(Payment)` করলে SQLAlchemy `payment_type` দেখে সঠিক ক্লাসের অবজেক্ট বানায়। আমাদের পরীক্ষায় ফলাফল: `[CreditCardPayment, CryptoPayment]`।
* `select(CreditCardPayment)` করলে নিজেই `WHERE payment_type = 'credit_card'` যোগ হয়।

///

সাবক্লাসের কলাম nullable হতে হবে (অন্য সাবক্লাসের রো-তে এগুলো থাকে না)। দুটি সাবক্লাস একই নামের কলাম ঘোষণা করলে `mapped_column(..., use_existing_column=True)` ব্যবহার করুন।

### 44.2 Joined Table Inheritance (প্রোডাকশন প্যাটার্ন) { #s44-2 }
```python
class PaymentMethod(Base):
    """payment_method টেবিলে ম্যাপ করা মূল polymorphic ক্লাস।"""
    __tablename__ = "payment_method"

    payment_method_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    payment_method_type_id: Mapped[str] = mapped_column(String(20), nullable=False)
    party_id: Mapped[str] = mapped_column(String(20))

    __mapper_args__ = {
        "polymorphic_on": "payment_method_type_id",
        "polymorphic_identity": "GENERIC",
    }

class CreditCard(PaymentMethod):
    """credit_card টেবিলে ম্যাপ করা joined সাবক্লাস।"""
    __tablename__ = "credit_card"

    payment_method_id: Mapped[str] = mapped_column(
        ForeignKey("payment_method.payment_method_id", ondelete="CASCADE"), primary_key=True
    )
    card_number: Mapped[str] = mapped_column(String(20))
    expire_date: Mapped[str] = mapped_column(String(10))

    __mapper_args__ = {"polymorphic_identity": "CREDIT_CARD"}

class BankAccount(PaymentMethod):
    """bank_account টেবিলে ম্যাপ করা joined সাবক্লাস।"""
    __tablename__ = "bank_account"

    payment_method_id: Mapped[str] = mapped_column(
        ForeignKey("payment_method.payment_method_id", ondelete="CASCADE"), primary_key=True
    )
    routing_number: Mapped[str] = mapped_column(String(20))
    account_number: Mapped[str] = mapped_column(String(30))

    __mapper_args__ = {"polymorphic_identity": "BANK_ACCOUNT"}
```

/// info | কোডটি সহজ ভাষায়

* বেস টেবিল `payment_method`-এ সাধারণ কলাম, আর প্রতিটি ধরনের জন্য আলাদা টেবিল (`credit_card`, `bank_account`), শুধু বিশেষ কলামসহ।
* সাবক্লাসের primary key একই সাথে বেস টেবিলের দিকে ফরেন কি। [সম্পর্কিত টেবিলে CRUD অধ্যায়ের](related-crud.md#s40) `Party` / `Person` প্যাটার্নের মতোই, কিন্তু এখানে SQLAlchemy সব নিজে সামলায়।
* `CreditCard(...)` অবজেক্ট `session.add()` করলে দুটি INSERT হয়: আগে `payment_method`, তারপর `credit_card`।

///

বেস ক্লাস কুয়েরি করলে সঠিক সাবক্লাস অবজেক্ট ফেরত আসে:
```python
from sqlalchemy.orm import selectin_polymorphic, with_polymorphic

# বেস কুয়েরি: সাবক্লাসের কলাম অ্যাক্সেসে লোড হয় (async-এ তার বদলে eager load করুন)
methods = (await session.scalars(select(PaymentMethod))).all()

# একই কুয়েরিতে LEFT OUTER JOIN দিয়ে সাবক্লাসের কলাম লোড
pm = with_polymorphic(PaymentMethod, [CreditCard, BankAccount])
methods = (await session.scalars(select(pm))).all()

# অথবা প্রতি সাবক্লাসে একটি অতিরিক্ত SELECT (অনেক সাবক্লাস থাকলে প্রায়ই দ্রুততর)
methods = (await session.scalars(
    select(PaymentMethod).options(selectin_polymorphic(PaymentMethod, [CreditCard, BankAccount]))
)).all()

# সরাসরি সাবক্লাস কুয়েরি: বেস টেবিলের সাথে স্বয়ংক্রিয় JOIN
cards = (await session.scalars(select(CreditCard).where(CreditCard.party_id == "P100"))).all()
```

/// warning | async-এ মনে রাখুন

শুধু `select(PaymentMethod)` করলে বেস টেবিলের কলামই আসে। পরে `card.card_number` পড়তে গেলে lazy load করতে চায়, আর async-এ `MissingGreenlet`। তাই বেস ক্লাস কুয়েরি করার সময় `with_polymorphic` বা `selectin_polymorphic` দিন। দুটোই আমরা চালিয়ে দেখেছি, ঠিক `[CreditCard, BankAccount]` আসে।

///

Async কোডে সবসময় `with_polymorphic` / `selectin_polymorphic` ব্যবহার করুন (অথবা প্রতিটি সাবক্লাসে `__mapper_args__ = {"polymorphic_load": "selectin"}`), যাতে সাবক্লাসের অ্যাট্রিবিউট কখনো lazy-load না হয়।

### 44.3 Concrete Table Inheritance { #s44-3 }
```python
from sqlalchemy.ext.declarative import ConcreteBase

class Employee(ConcreteBase, Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {"polymorphic_identity": "employee", "concrete": True}

class HourlyEmployee(Employee):
    __tablename__ = "hourly_employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    __mapper_args__ = {"polymorphic_identity": "hourly", "concrete": True}
```

/// note | ইমপোর্টটি খেয়াল করুন

`ConcreteBase` আসে `sqlalchemy.ext.declarative` থেকে। `from sqlalchemy.orm import ConcreteBase` লিখলে `ImportError` আসে।

///

## 45. Hybrid Property, Composite, Association Proxy ও `MutableDict` { #s45 }

### 45.1 `@hybrid_property` — একটি সংজ্ঞা, Python **এবং** SQL দুটোতেই { #s45-1 }
```python
from decimal import Decimal
from sqlalchemy import Numeric, func
from sqlalchemy.ext.hybrid import hybrid_property

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.0"))

    # ১. ইনস্ট্যান্স লেভেল: item.net_total Python-এ হিসাব হয়
    @hybrid_property
    def net_total(self) -> Decimal:
        gross = self.quantity * self.unit_price
        return gross - gross * (self.discount_pct / Decimal("100"))

    # ২. ক্লাস লেভেল: InvoiceItem.net_total SQL-এ কম্পাইল হয়
    @net_total.inplace.expression
    @classmethod
    def _net_total_expression(cls):
        gross = cls.quantity * cls.unit_price
        return gross - gross * (cls.discount_pct / 100)

# WHERE (quantity * unit_price - quantity * unit_price * discount_pct / 100) > 500
items = (await session.scalars(select(InvoiceItem).where(InvoiceItem.net_total > 500))).all()
```

/// tip | উদাহরণ দিয়ে বুঝি

`net_total` একটি "দুই-মুখী" প্রপার্টি:

* অবজেক্টের ওপর (`item.net_total`) এটা সাধারণ Python হিসাব: `10 × 100 − 10%` = `900`।
* ক্লাসের ওপর (`InvoiceItem.net_total > 500`) এটা SQL এক্সপ্রেশন হয়ে যায়, তাই ডেটাবেসেই ফিল্টার হয়। সব রো Python-এ আনতে হয় না।

একই নিয়ম একবার লিখে দুই জায়গায় ব্যবহার, তাই Python আর SQL-এর হিসাবে অমিল হওয়ার সুযোগ নেই।

///

আরেকটি প্রচলিত hybrid — পূর্ণ নাম:
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @full_name.inplace.expression
    @classmethod
    def _full_name_expression(cls):
        return func.concat(cls.first_name, " ", cls.last_name)

# user.full_name -> "John Doe";   select(User).where(User.full_name == "John Doe")
```
`.inplace` রূপটি (2.0) টাইপ চেকারকে সন্তুষ্ট রাখে। পুরোনো ধরন — একই নামের দ্বিতীয় মেথডে `@full_name.expression` — এখনও কাজ করে।

### 45.2 `composite()` — একাধিক কলাম জুড়ে value object (DDD) { #s45-2 }
```python
from dataclasses import dataclass
from sqlalchemy.orm import composite

@dataclass(frozen=True)
class Money:
    """অপরিবর্তনীয় (immutable) value object।"""
    amount: Decimal
    currency: str

class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(100))

    # ফিজিক্যাল কলাম
    _amount: Mapped[Decimal] = mapped_column("amount", Numeric(14, 2))
    _currency: Mapped[str] = mapped_column("currency", String(3))

    # দুটো কলাম মিলে একটি অ্যাট্রিবিউট
    price: Mapped[Money] = composite(Money, _amount, _currency)

expense = Expense(description="AWS Cloud", price=Money(Decimal("142.50"), "USD"))
session.add(expense)
stmt = select(Expense).where(Expense.price == Money(Decimal("142.50"), "USD"))
```

/// info | কোডটি সহজ ভাষায়

ডেটাবেসে দুটি সাধারণ কলাম (`amount`, `currency`), কিন্তু Python-এ একটি অর্থপূর্ণ জিনিস: `expense.price` → `Money(amount=Decimal('142.50'), currency='USD')`। টাকার পরিমাণ মুদ্রা ছাড়া অর্থহীন, তাই দুটিকে একসাথে রাখা নিরাপদ।

///

`Money` frozen হওয়ায় মান বদলাতে নতুন অবজেক্ট অ্যাসাইন করুন (`expense.price = Money(...)`)।

### 45.3 Association proxy — জাংশনের ধাপ লুকানো { #s45-3 }
```python
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy

class User(Base):
    __tablename__ = "app_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))

    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # user_roles -> role -> name-এর উপর list[str] ভিউ
    role_names: AssociationProxy[list[str]] = association_proxy(
        "user_roles", "role_name",
        creator=lambda name: UserRole(role=Role(name=name)),   # .append("X") কীভাবে লিংক বানাবে
    )

class UserRole(Base):
    __tablename__ = "app_user_roles"
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("app_roles.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship()

    role_name: AssociationProxy[str] = association_proxy("role", "name")

class Role(Base):
    __tablename__ = "app_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

# user.role_names -> ["ADMIN", "MANAGER"]
# user.role_names.append("AUDITOR")  -> `creator`-এর মাধ্যমে UserRole (+ Role) তৈরি হয়
```

/// info | কোডটি সহজ ভাষায়

আসল পথ তিন ধাপের: `user.user_roles[0].role.name`। association proxy এটাকে করে দেয় শুধু `user.role_names` → `["ADMIN", "MANAGER"]`। আর `user.role_names.append("AUDITOR")` লিখলে `creator` ফাংশন পেছনে নিজেই `UserRole` আর `Role` বানিয়ে দেয়।

///

প্রোডাকশনে `creator`-এ নতুন `Role` তৈরি না করে বিদ্যমান `Role` খুঁজে নেবেন। কুয়েরিতে ফিল্টার করতে আসল রিলেশনশিপ দিয়ে যান: `select(User).join(User.user_roles).join(UserRole.role).where(Role.name == "ADMIN")`।

### 45.4 `MutableDict` — JSON-এর in-place পরিবর্তন ট্র্যাক করা { #s45-4 }
ডিফল্টভাবে `prefs.config["theme"] = "dark"` ডিকশনারিকে জায়গায় বদলায়; SQLAlchemy কোনো অ্যাট্রিবিউট অ্যাসাইনমেন্ট দেখে না, তাই **সেভ করে না**। টাইপটি মুড়ে দিন:
```python
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)

    # এখন key/value পরিবর্তন হলেই অ্যাট্রিবিউট dirty হিসেবে চিহ্নিত হয়
    config: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), default=dict)
```

/// info | কেন দরকার, উদাহরণসহ

```python
pref.config["theme"] = "dark"     # ডিকশনারির ভেতরে বদল
await session.commit()
```

`MutableDict` ছাড়া SQLAlchemy এই বদল দেখতে পায় না, কারণ `pref.config` নিজে নতুন কিছুতে assign হয়নি। ফলে কোনো UPDATE যায় না। `MutableDict.as_mutable(JSONB)` দিলে বদল ধরা পড়ে, আর আমাদের পরীক্ষায় নতুন সেশনে পড়েও `{"theme": "dark"}` পাওয়া গেছে।

///

`MutableDict` শুধু টপ-লেভেল key ট্র্যাক করে; নেস্টেড কাঠামোর জন্য হয় পুরো মান আবার অ্যাসাইন করুন, নয়তো `sqlalchemy.orm.attributes` থেকে `flag_modified(obj, "config")` কল করুন। অ্যারের জন্য `MutableList` আছে।

## 46. Event, Interceptor ও কাস্টম `TypeDecorator` { #s46 }

/// tip | উদাহরণ দিয়ে বুঝি

**Event** হলো "কিছু ঘটলে আমাকে ডেকো" ধরনের ব্যবস্থা। দরজায় সেন্সর লাগানো বাতির মতো: দরজা খুললেই বাতি জ্বলে, প্রতিবার আপনাকে সুইচ টিপতে হয় না। তেমনি "প্রতিটি সেভের আগে সময় বসাও" বা "প্রতিটি ধীর কুয়েরি লগ করো" একবার লিখে দিলে সব জায়গায় নিজে থেকেই চলে।

///

`@event.listens_for(target, "event_name")` দিয়ে Engine, Connection, Pool, Session ও Mapper লেভেলে event যুক্ত করা যায়। `AsyncEngine`/`AsyncSession`-এর ক্ষেত্রে `engine.sync_engine` / `Session` ক্লাসে (অথবা `async_session.sync_session_class`-এ) যুক্ত করুন।

### 46.1 ORM lifecycle: স্বয়ংক্রিয় অডিট টাইমস্ট্যাম্প { #s46-1 }
```python
from datetime import datetime, timezone
from sqlalchemy import event
from sqlalchemy.orm import Session

@event.listens_for(Session, "before_flush")
def auto_audit_timestamp(session, flush_context, instances):
    """UPDATE পাঠানোর ঠিক আগে প্রতিটি পরিবর্তিত অবজেক্টে সময় বসানো।"""
    now = datetime.now(timezone.utc)
    for obj in session.dirty:                  # পরিবর্তিত persistent অবজেক্ট
        if hasattr(obj, "last_updated_stamp"):
            obj.last_updated_stamp = now
    for obj in session.new:                    # pending অবজেক্ট
        if hasattr(obj, "created_stamp") and obj.created_stamp is None:
            obj.created_stamp = now
```

/// info | কোডটি সহজ ভাষায়

* `before_flush` চলে প্রতিটি flush-এর ঠিক আগে (commit-এর ভেতরেও)।
* `session.new`: এই সেশনে নতুন যোগ হওয়া অবজেক্ট; `session.dirty`: বদলানো অবজেক্ট।
* `hasattr(obj, "created_stamp")`: যে মডেলে এই কলাম আছে শুধু তাতেই কাজ করবে, বাকিগুলো বাদ।
* `Session` ক্লাসে listen করায় এটা সব সেশনে চলে, `AsyncSession`-সহ, কারণ `AsyncSession` ভেতরে একটি সাধারণ `Session`-ই চালায়।

///

অন্যান্য কাজের hook: `after_flush`, `after_commit` (যেমন ডোমেইন ইভেন্ট / outbox প্রকাশ), mapper-লেভেলের `before_insert` / `before_update` (প্রতি অবজেক্টে), `do_orm_execute` (কুয়েরি রিরাইট — [§37.4](crud-update-delete.md#s37-4)-এর soft-delete ফিল্টার দেখুন)।

/// warning | সতর্কতা

Core-ধাঁচের বাল্ক `insert()` / `update()` / `delete()` স্টেটমেন্টে ORM event (`before_flush`, `before_update` …) **চলে না**।

///

### 46.2 Engine hook: টাইমিং ও স্লো-কুয়েরি লগিং { #s46-2 }
```python
import logging
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("sqlalchemy.performance")

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.perf_counter())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    elapsed_ms = (time.perf_counter() - conn.info["query_start_time"].pop()) * 1000
    if elapsed_ms > 200:                                   # ২০০ ms-এর বেশি হলে সতর্কবার্তা
        logger.warning("SLOW QUERY [%.2f ms]:\n%s\nParams: %s", elapsed_ms, statement, parameters)
```
`Engine` **ক্লাসে** listen করলে এটি প্রতিটি engine-এ প্রযোজ্য হয়, প্রতিটি `AsyncEngine`-এর ভেতরের sync engine-সহ। শুরুর সময়গুলো `conn.info`-তে স্ট্যাক হিসেবে রাখায় নেস্টেড স্টেটমেন্টেও hook নিরাপদ। প্যারামিটারে ব্যক্তিগত তথ্য থাকতে পারলে প্রোডাকশনে সেগুলো লগ করবেন না।

### 46.3 কাস্টম `TypeDecorator`: স্বচ্ছ কলাম এনক্রিপশন { #s46-3 }
```python
from cryptography.fernet import Fernet
from sqlalchemy import String, TypeDecorator

class EncryptedString(TypeDecorator):
    """যাওয়ার পথে এনক্রিপ্ট, আসার পথে ডিক্রিপ্ট।"""
    impl = String(512)
    cache_ok = True          # এই টাইপ ব্যবহার করা স্টেটমেন্ট ক্যাশ করা নিরাপদ

    def __init__(self, key: bytes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fernet = Fernet(key)

    def process_bind_param(self, value, dialect):
        """Python -> ডেটাবেস (এনক্রিপশন)"""
        if value is None:
            return None
        return self.fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def process_result_value(self, value, dialect):
        """ডেটাবেস -> Python (ডিক্রিপশন)"""
        if value is None:
            return None
        return self.fernet.decrypt(value.encode("utf-8")).decode("utf-8")

# মডেলে (key সিক্রেট ম্যানেজার থেকে আনুন, কখনো হার্ড-কোড বা নতুন করে তৈরি করবেন না):
# ssn: Mapped[str] = mapped_column(EncryptedString(settings.FERNET_KEY))
```

/// info | কোডটি সহজ ভাষায়

* `process_bind_param`: Python থেকে ডেটাবেসে যাওয়ার সময় চলে, এখানে এনক্রিপ্ট করে।
* `process_result_value`: ডেটাবেস থেকে আসার সময় চলে, এখানে ডিক্রিপ্ট করে।
* আপনার কোডে সবসময় সাধারণ টেক্সট (`"123-45-6789"`), অথচ ডেটাবেসে শুধু এনক্রিপ্ট করা লেখা। আমরা raw SQL দিয়ে দেখেছি, কলামে আসল মান নেই।
* `cache_ok = True`: SQLAlchemy-কে জানায় এই টাইপ ব্যবহার করা কুয়েরি ক্যাশ করা নিরাপদ। না দিলে সতর্কবার্তা আসে, আর এই টাইপ যেসব কুয়েরিতে আছে সেগুলো ক্যাশ হয় না।

///

Fernet-এর আউটপুট র‍্যান্ডমাইজড, তাই এনক্রিপ্ট করা কলামে ফিল্টার (`WHERE ssn = ...`) বা ইনডেক্স **করা যায় না**; খোঁজার দরকার হলে আলাদা keyed hash সংরক্ষণ করুন।

/// check | সংক্ষেপে মনে রাখুন

* কম কলাম, দ্রুত কুয়েরি → single table; আলাদা কলাম ও কনস্ট্রেইন্ট → joined table (প্রোডাকশনে সবচেয়ে প্রচলিত)।
* async-এ polymorphic কুয়েরিতে `with_polymorphic` / `selectin_polymorphic`।
* hybrid property = একই হিসাব Python ও SQL দুটোতেই।
* JSON কলামের ভেতরের বদল ধরতে `MutableDict`; গভীর বদলে `flag_modified()`।
* event দিয়ে বারবারের কাজ এক জায়গায়, কিন্তু বাল্ক স্টেটমেন্টে ORM event চলে না।

///

**পরের ধাপ:** একসাথে অনেক রিকোয়েস্ট এলে ডেটা কীভাবে নিরাপদ রাখবেন, দেখুন [Concurrency](concurrency.md) অধ্যায়ে।
