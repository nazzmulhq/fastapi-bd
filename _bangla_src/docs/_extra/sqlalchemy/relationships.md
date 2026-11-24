# Relationship: টেবিলের মধ্যে সম্পর্ক { #sqlalchemy-relationships }

/// note | এই পেজে যা শিখবেন

* ফরেন কি দিয়ে ডেটাবেসে দুটি টেবিল জোড়া, আর `relationship()` দিয়ে Python-এ এক অবজেক্ট থেকে আরেকটিতে যাওয়া।
* চার ধরনের সম্পর্ক: one-to-many, many-to-one, one-to-one, many-to-many।
* association table বনাম association object, self-referential ট্রি, একই টেবিলে দুটি FK।
* cascade: প্যারেন্টের সাথে চাইল্ডের কী হবে।
* লোডিং স্ট্র্যাটেজি (`selectinload`, `joinedload`, `lazy="raise"`) আর বিখ্যাত **N+1** সমস্যা।

///

/// tip | উদাহরণ দিয়ে বুঝি

একটি অফিসে প্রতিটি কর্মচারীর ফর্মে লেখা থাকে তিনি কোন বিভাগে কাজ করেন: "বিভাগ নং ৩"। এই নম্বরটিই **ফরেন কি**। এটা ডেটাবেসে রাখা আসল তথ্য।

এখন আপনি চাইলেন "৩ নম্বর বিভাগের সব কর্মচারী দেখাও" অথবা "রহিম কোন বিভাগে?"। প্রতিবার হাতে নম্বর মিলিয়ে খোঁজার বদলে `department.employees` বা `employee.department` লিখলেই উত্তর পেয়ে যান। এই সুবিধাটিই হলো **`relationship()`**। এটা Python-এর একটি শর্টকাট, ডেটাবেসে নতুন কিছু তৈরি করে না।

///

## 10. Foreign Key ও `ondelete` { #s10 }

Foreign key **ডেটাবেস লেভেলে** রেফারেন্শিয়াল ইন্টিগ্রিটি নিশ্চিত করে। `relationship()` (পরের সেকশন) কেবল Python-এ নেভিগেশন কনফিগার করে — দুটোই দরকার।

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    department_id: Mapped[int] = mapped_column(
        ForeignKey("core.departments.id", ondelete="CASCADE"),
        nullable=False,
    )
```

/// info | কোডটি সহজ ভাষায়

* `ForeignKey("core.departments.id")`: এই কলামের মান অবশ্যই `core` স্কিমার `departments` টেবিলের কোনো একটি `id` হতে হবে। ভুল নম্বর দিলে ডেটাবেস প্রত্যাখ্যান করবে।
* `ondelete="CASCADE"`: কোনো বিভাগ মুছে ফেললে তার সব কর্মচারীর রো-ও ডেটাবেস নিজে মুছে দেবে।
* `nullable=False`: প্রত্যেক কর্মচারীকে কোনো না কোনো বিভাগে থাকতেই হবে।

তৈরি হওয়া SQL:

```sql
department_id INTEGER NOT NULL,
CONSTRAINT fk_employees_department_id_departments
    FOREIGN KEY(department_id) REFERENCES core.departments (id) ON DELETE CASCADE
```

///

**Composite** ফরেন কি-র জন্য (যেমন OFBiz-এর কোনো চাইল্ড যা `(order_id, order_item_seq_id)`-কে নির্দেশ করে) টেবিল-লেভেল কনস্ট্রেইন্ট দিন:
```python
from sqlalchemy import ForeignKeyConstraint

__table_args__ = (
    ForeignKeyConstraint(
        ["order_id", "order_item_seq_id"],
        ["order_item.order_id", "order_item.order_item_seq_id"],
        name="fk_shipment_item_order_item",
        ondelete="CASCADE",
    ),
)
```

### `ondelete` অপশনসমূহ { #s10-a }
| অপশন | প্যারেন্ট রো ডিলিট হলে কী হয় |
| :--- | :--- |
| **`CASCADE`** | রেফারেন্স করা চাইল্ড রো ডেটাবেস স্বয়ংক্রিয়ভাবে ডিলিট করে। |
| **`SET NULL`** | চাইল্ডের FK মান `NULL` হয়ে যায় (কলাম nullable হতে হবে)। |
| **`SET DEFAULT`** | চাইল্ডের FK তার server default-এ ফিরে যায়। |
| **`RESTRICT`** | চাইল্ড থাকলে সাথে সাথে ডিলিট প্রত্যাখ্যান করে। |
| **`NO ACTION`** | (ডিফল্ট) RESTRICT-এর মতো, তবে স্টেটমেন্টের শেষে যাচাই হয় — কনস্ট্রেইন্ট `DEFERRABLE INITIALLY DEFERRED` হলে transaction-এর শেষে। |

Primary key বদলালে কী হবে তার জন্য `ForeignKey`-তে `onupdate=` একইভাবে কাজ করে।

## 11. `relationship()` আসলে কী { #s11 }

`relationship()` **কোনো কলাম তৈরি করে না**। এটি ORM-কে বলে দেয় অবজেক্টগুলোর মধ্যে কীভাবে নেভিগেট করতে হবে (`user.addresses`, `address.user`) এবং Python-এ অবজেক্ট যুক্ত করলে ফরেন কি কীভাবে সিঙ্ক করতে হবে।

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
```

/// info | কোডটি সহজ ভাষায়

* আসল কলাম মাত্র একটি: `addresses.user_id`। এটাই ডেটাবেসে সম্পর্ক রাখে।
* `User.addresses` আর `Address.user` দুটোই `relationship()`, কোনো কলাম নয়।
* `back_populates="user"` আর `back_populates="addresses"`: দুই দিক একে অপরকে চেনে। একদিকে বদলালে অন্যদিকেও মেমরিতে সাথে সাথে বদলে যায়:

```python
user = User()
addr = Address()
user.addresses.append(addr)
print(addr.user is user)   # True — commit-এর আগেই, মেমরিতে
```

///

এতে যা পাওয়া যায়:
- `user.addresses.append(addr)` করলে flush-এর সময় `addr.user_id` স্বয়ংক্রিয়ভাবে সেট হয়।
- `Mapped[...]` অ্যানোটেশন ঠিক করে দেয় এটি কালেকশন (`list[...]`) নাকি স্কেলার।
- Join condition `ForeignKey` থেকেই অনুমান করা হয় — লিখতে হয় না (দ্ব্যর্থ হলে আলাদা কথা, [§14](#s14) দেখুন)।

বহুল ব্যবহৃত `relationship()` আর্গুমেন্ট:

| আর্গুমেন্ট | কাজ |
| :--- | :--- |
| `back_populates` | অপর ক্লাসের বিপরীত অ্যাট্রিবিউটের নাম |
| `secondary` | many-to-many-এর association টেবিল |
| `cascade` | কোন session অপারেশন সম্পর্কিত অবজেক্টে ছড়াবে ([§15](#s15)) |
| `passive_deletes` | চাইল্ড মুছতে ডেটাবেসের `ON DELETE CASCADE`-কে দায়িত্ব দেয় ([§15](#s15)) |
| `lazy` | ডিফল্ট লোডিং স্ট্র্যাটেজি ([§16](#s16)) |
| `uselist` | জোর করে স্কেলার (`False`) — সাধারণত `Mapped["X"]` থেকেই বোঝা যায় |
| `foreign_keys` | একই টেবিলে একাধিক FK থাকলে দ্ব্যর্থতা দূর করে ([§14](#s14)) |
| `remote_side` | Self-referential রিলেশনশিপে "প্যারেন্ট" দিক চিহ্নিত করে ([§14](#s14)) |
| `primaryjoin` / `secondaryjoin` | কাস্টম join condition |
| `order_by` | কালেকশনের ডিফল্ট ক্রম |
| `viewonly` | শুধু-পড়ার রিলেশনশিপ (কখনো FK লেখে না) |

## 12. ৪টি Cardinality Pattern (1:N, N:1, 1:1, N:M) { #s12 }

```
1. One-to-Many  : এক Department   -> অনেক Employee
2. Many-to-One  : অনেক Employee   -> এক Department
3. One-to-One   : এক User         <-> এক Profile
4. Many-to-Many : অনেক Student    <-> অনেক Course
```

/// tip | বাস্তব জীবনের উদাহরণ

| সম্পর্ক | উদাহরণ | ফরেন কি কোথায় |
| :--- | :--- | :--- |
| One-to-Many (1:N) | এক মা, অনেক সন্তান; এক বিভাগ, অনেক কর্মচারী | "অনেক" দিকে (`employees.department_id`) |
| Many-to-One (N:1) | একই সম্পর্কের উল্টো দিক থেকে দেখা | "অনেক" দিকে |
| One-to-One (1:1) | একজন নাগরিক, একটি NID | যেকোনো একদিকে, সাথে `unique=True` |
| Many-to-Many (N:M) | অনেক ছাত্র, অনেক কোর্স | আলাদা মধ্যবর্তী টেবিলে |

মনে রাখার সহজ নিয়ম: **ফরেন কি সবসময় "অনেক"-এর দিকে থাকে।** একটি বিভাগের রো-তে হাজার কর্মচারীর id রাখা যায় না, কিন্তু প্রতিটি কর্মচারীর রো-তে একটি বিভাগের id রাখা যায়।

///

### 12.1 One-to-Many (1:N) { #s12-1 }
প্যারেন্টে চাইল্ডের একটি তালিকা থাকে; চাইল্ডে থাকে FK।
```python
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
    )

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(back_populates="employees")
```

/// info | কোডটি সহজ ভাষায়

* `Mapped[list["Employee"]]`: `list` মানে এক বিভাগের **অনেক** কর্মচারী।
* `Mapped["Department"]`: তালিকা নয়, মানে প্রতিটি কর্মচারীর **একটি** বিভাগ।
* `"Employee"` উদ্ধৃতিচিহ্নে লেখা, কারণ `Employee` ক্লাসটি নিচে ঘোষিত। SQLAlchemy পরে নাম দিয়ে খুঁজে নেয়।
* `cascade="all, delete-orphan"`: বিভাগ মুছলে কর্মচারীরাও মুছবে, আর তালিকা থেকে কাউকে সরালে তার রো-ও মুছবে। বিস্তারিত [§15](#s15)-এ।

///

### 12.2 Many-to-One (N:1) { #s12-2 }
বিপরীত দিক: চাইল্ডে FK এবং প্যারেন্টের একটি স্কেলার রেফারেন্স থাকে।
```python
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    # অনেক Order -> এক Customer
    customer: Mapped["Customer"] = relationship(back_populates="orders")
```

### 12.3 One-to-One (1:1) { #s12-3 }
প্রতি প্যারেন্টের সর্বোচ্চ একটি চাইল্ড।
> **মূল শর্ত:** চাইল্ডের FK কলামে অবশ্যই **`unique=True`** দিতে হবে — নইলে ডেটাবেস খুশিমনে একাধিক "one-to-one" চাইল্ড ঢুকতে দেবে।

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    # স্কেলার অ্যানোটেশন মানেই uselist=False
    profile: Mapped["Profile | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,        # ডেটাবেসে 1:1 নিশ্চিত করার চাবিকাঠি
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="profile")
```
টাইপড অ্যানোটেশন না থাকলে একই স্কেলার আচরণ পেতে `relationship(..., uselist=False)` লিখতে হয়।

1:1-এর আরেকটি ধরন — **shared primary key / subtype টেবিল** — OFBiz-এ ব্যবহৃত হয় (`Party` ↔ `Person`): চাইল্ডের PK-ই প্যারেন্টের দিকে FK। [§40](related-crud.md#s40) দেখুন।

/// warning | সাধারণ ভুল

`unique=True` ছাড়া 1:1 লিখলে Python-এ `user.profile` একটি অবজেক্ট দেখাবে ঠিকই, কিন্তু ডেটাবেস একই `user_id`-এর জন্য দুটি `Profile` ঢুকতে দেবে। তখন কোনটা আসবে তার ঠিক নেই। ডেটাবেসকে দিয়েই নিয়মটি নিশ্চিত করুন।

///

### 12.4 Many-to-Many (N:M) { #s12-4 }
দুই দিকই একটি **secondary association টেবিলের** মাধ্যমে অপর দিকের অনেক রো-র সাথে যুক্ত।
```python
from sqlalchemy import Column, ForeignKey, Table

student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    courses: Mapped[list["Course"]] = relationship(
        secondary=student_course, back_populates="students"
    )

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    students: Mapped[list["Student"]] = relationship(
        secondary=student_course, back_populates="courses"
    )
```

/// tip | উদাহরণ দিয়ে বুঝি

`student_course` টেবিলটি একটি **ভর্তির খাতা**। প্রতিটি লাইনে লেখা "অমুক ছাত্র অমুক কোর্সে"। এক ছাত্রের অনেক লাইন থাকতে পারে, এক কোর্সেরও অনেক লাইন।

```python
student.courses.append(course)   # খাতায় একটি লাইন যোগ: INSERT INTO student_course ...
student.courses.remove(course)   # লাইনটি কাটা: DELETE FROM student_course ...
```

ছাত্র বা কোর্স কেউই মোছে না, শুধু সংযোগের লাইনটি যোগ হয় বা মোছে।

///

`student.courses.append(course)` করলে `student_course`-এ একটি রো ঢোকে; `student.courses.remove(course)` করলে তা মুছে যায়।

## 13. Association Table বনাম Association Object { #s13 }

| বৈশিষ্ট্য | Association Table | Association Object |
| :--- | :--- | :--- |
| **মধ্যবর্তী কাঠামো** | সাধারণ `Table(...)` | পূর্ণাঙ্গ ম্যাপড ক্লাস |
| **অতিরিক্ত কলাম** | সম্ভব নয় (শুধু FK) | সম্ভব (`quantity`, `price`, `granted_by`, `from_date` …) |
| **কখন ব্যবহার করবেন** | ট্যাগ, সাধারণ রোল | অর্ডার লাইন, এনরোলমেন্ট, মেয়াদসহ পারমিশন গ্রান্ট |
| **অ্যাক্সেস প্যাটার্ন** | সরাসরি `student.courses` | `order.items[0].product` (অবজেক্টের মধ্য দিয়ে এক ধাপ) |

/// tip | কোনটি বেছে নেবেন?

নিজেকে জিজ্ঞেস করুন: **"সংযোগটির নিজের কোনো তথ্য আছে কি?"**

* না, শুধু "কে কার সাথে যুক্ত" (ট্যাগ, সাধারণ রোল) → **association table** (`Table(...)`)।
* হ্যাঁ, যেমন কত পিস, কোন দামে, কবে থেকে, কে অনুমতি দিল → **association object** (পূর্ণ মডেল ক্লাস)।

শুরুতে সাধারণ মনে হলেও পরে তথ্য যোগ হওয়ার সম্ভাবনা থাকলে শুরু থেকেই association object নিন।

///

### Association object উদাহরণ (অর্ডার লাইন) { #s13-a }
```python
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)

    # সংযোগের উপরেই অতিরিক্ত ডেটা (payload)
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")
```

### Association object উদাহরণ (অডিট ডেটাসহ রোল গ্রান্ট) { #s13-b }
```python
class UserRoleAssociation(Base):
    __tablename__ = "user_role_association"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.role_id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    granted_by: Mapped[str] = mapped_column(String(64))

    user: Mapped["User"] = relationship(back_populates="role_associations")
    role: Mapped["Role"] = relationship(back_populates="user_associations")
```
অতিরিক্ত ধাপটি (`user.role_associations[i].role.name`) লুকাতে **association proxy** ব্যবহার করুন ([§45.3](advanced-mapping.md#s45-3))।

## 14. Self-Referential ও একাধিক-FK Relationship { #s14 }

### 14.1 Self-referential (adjacency list: ট্রি ও হায়ারার্কি) { #s14-1 }
একটি রো **একই টেবিলের** অন্য রো-কে নির্দেশ করে (ক্যাটাগরি → সাব-ক্যাটাগরি, ম্যানেজার → এমপ্লয়ি, কমেন্ট → রিপ্লাই, ফোল্ডার → সাবফোল্ডার)। কোন দিকটি প্যারেন্ট তা SQLAlchemy-কে জানাতে `remote_side` ব্যবহার করুন:

```python
from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"))

    # Many-to-one: প্যারেন্ট। remote_side=[id] বলে দেয় "id" হলো remote (প্যারেন্ট) কলাম
    parent: Mapped[Optional["Category"]] = relationship(
        back_populates="children",
        remote_side=[id],
    )

    # One-to-many: চাইল্ডরা
    children: Mapped[list["Category"]] = relationship(
        back_populates="parent",
        cascade="all, delete-orphan",
    )
```

/// info | কোডটি সহজ ভাষায়

একই `categories` টেবিলের একটি রো আরেকটি রো-কে নির্দেশ করে: "ইলেকট্রনিক্স" → "মোবাইল" → "স্মার্টফোন"।

* `parent_id`: প্যারেন্ট ক্যাটাগরির `id`। সবচেয়ে ওপরের (root) ক্যাটাগরির জন্য `None`।
* দুটি `relationship()` একই টেবিলের দিকে, তাই SQLAlchemy নিজে বুঝতে পারে না কোনটা "ওপরে" আর কোনটা "নিচে"। `remote_side=[id]` বলে দেয়: `parent` সম্পর্কে **অপর দিকের `id`** হলো প্যারেন্ট।

```python
root = Category(name="ইলেকট্রনিক্স", children=[Category(name="মোবাইল")])
session.add(root)   # দুটি রো ঢুকবে, মোবাইলের parent_id = ইলেকট্রনিক্সের id
```

///

পুরো শাখা এক রাউন্ড-ট্রিপে আনতে **recursive CTE** ব্যবহার করুন ([§27](advanced-queries.md#s27))। কুয়েরিতে টেবিলকে নিজের সাথে join করতে `aliased()` ব্যবহার করুন ([§26.4](querying.md#s26-4))।

### 14.2 একই টেবিলে একাধিক foreign key { #s14-2 }
যখন দুটি কলাম একই টার্গেটকে নির্দেশ করে, কোন রিলেশনশিপ কোন FK ব্যবহার করবে SQLAlchemy অনুমান করতে পারে না — `foreign_keys` দিন:

```python
class Shipment(Base):
    __tablename__ = "shipments"
    shipment_id: Mapped[int] = mapped_column(primary_key=True)

    origin_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"))
    destination_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.address_id"))

    origin_address: Mapped["Address"] = relationship(
        foreign_keys=[origin_address_id], back_populates="outgoing_shipments"
    )
    destination_address: Mapped["Address"] = relationship(
        foreign_keys=[destination_address_id], back_populates="incoming_shipments"
    )

class Address(Base):
    __tablename__ = "addresses"
    address_id: Mapped[int] = mapped_column(primary_key=True)

    outgoing_shipments: Mapped[list["Shipment"]] = relationship(
        foreign_keys="Shipment.origin_address_id", back_populates="origin_address"
    )
    incoming_shipments: Mapped[list["Shipment"]] = relationship(
        foreign_keys="Shipment.destination_address_id", back_populates="destination_address"
    )
```
আরও জটিল কিছুর জন্য (join-এ অতিরিক্ত ফিল্টার, বা কোনো FK-ই নেই) `primaryjoin="and_(A.x == B.y, B.active == True)"` ব্যবহার করুন, সাধারণত `viewonly=True`-সহ।

## 15. `back_populates` বনাম `backref`, এবং Cascade { #s15 }

### 15.1 `back_populates` বনাম `backref` { #s15-1 }
- **`back_populates` (আধুনিক, স্পষ্ট, টাইপ-সেফ):** দুই ক্লাসেই অ্যাট্রিবিউট ঘোষিত থাকে এবং একে অপরের নাম উল্লেখ করে। Mypy/Pyright ও IDE অটো-কমপ্লিশনের সাথে কাজ করে।
- **`backref` (পুরোনো, ইমপ্লিসিট):** এক দিকে ঘোষণা করলে অন্য দিকের অ্যাট্রিবিউট রানটাইমে তৈরি হয়। টাইপ চেকারের কাছে অদৃশ্য — টাইপড 2.0 কোডে এড়িয়ে চলুন।

### 15.2 ORM cascade { #s15-2 }

/// tip | উদাহরণ দিয়ে বুঝি

**Cascade** মানে "প্যারেন্টের সাথে যা হবে, চাইল্ডের সাথেও তা হবে"।

* `save-update`: অর্ডারটি সেশনে যোগ করলে তার সব আইটেমও যোগ হয়। আলাদা করে প্রতিটি আইটেম `add()` করতে হয় না।
* `delete`: অর্ডার মুছলে আইটেমগুলোও মোছে।
* `delete-orphan`: অর্ডারের তালিকা থেকে একটি আইটেম সরালে (`order.items.remove(item)`) সেটা "এতিম" হয়ে যায়, তাই মুছে ফেলা হয়। বাজারের ব্যাগ থেকে একটি জিনিস বের করে ফেলে দেওয়ার মতো।

///

প্যারেন্টের উপর session অপারেশন কীভাবে সম্পর্কিত অবজেক্টে ছড়াবে তা `cascade` নির্ধারণ করে:
```python
items: Mapped[list["OrderItem"]] = relationship(
    back_populates="order",
    cascade="all, delete-orphan",
    passive_deletes=True,
)
```

| Cascade ফ্ল্যাগ | আচরণ | মন্তব্য |
| :--- | :--- | :--- |
| `save-update` | `session.add(parent)` করলে চাইল্ডরাও যুক্ত হয় | ডিফল্ট (`all`-এর অংশ) |
| `merge` | `session.merge(parent)` চাইল্ডদেরও merge করে | ডিফল্ট (`all`-এর অংশ) |
| `refresh-expire` | `refresh`/`expire` ছড়িয়ে পড়ে | `all`-এর অংশ |
| `expunge` | প্যারেন্টকে session থেকে সরালে চাইল্ডরাও সরে | `all`-এর অংশ |
| `delete` | প্যারেন্ট ডিলিট করলে চাইল্ডও ডিলিট | মালিকানাধীন চাইল্ডের জন্য |
| `delete-orphan` | কালেকশন থেকে চাইল্ড সরালে (`parent.children.remove(c)`) তা ডিলিট হয় | Aggregate root-এর জন্য জরুরি |
| `all` | `save-update, merge, refresh-expire, expunge, delete` | |
| `all, delete-orphan` | একচেটিয়া মালিকানাধীন কালেকশনের আদর্শ কনফিগারেশন | |

### 15.3 ORM cascade বনাম ডেটাবেস cascade { #s15-3 }
| কনফিগারেশন | মেকানিজম | পারফরম্যান্স |
| :--- | :--- | :--- |
| শুধু `cascade="all, delete-orphan"` | ORM প্রতিটি চাইল্ড **লোড** করে, প্রতিটির জন্য আলাদা `DELETE` পাঠায় | বড় কালেকশনে ধীর |
| `cascade="all, delete-orphan"` + `passive_deletes=True` + `ForeignKey(..., ondelete="CASCADE")` | ORM শুধু প্যারেন্ট ডিলিট করে; PostgreSQL FK-এর মাধ্যমে চাইল্ড ডিলিট করে | **দ্রুত — রিকমেন্ডেড** |

`passive_deletes=True` ORM-কে বলে: "শুধু ডিলিট করার জন্য লোড না হওয়া চাইল্ডদের লোড কোরো না — ডেটাবেসই সেটা করবে।"

/// warning | কখন cascade দেবেন না

`cascade="all, delete-orphan"` শুধু সেই চাইল্ডের জন্য, যা পুরোপুরি প্যারেন্টের **মালিকানাধীন** (অর্ডার → অর্ডার আইটেম)। স্বাধীন জিনিসে দেবেন না। যেমন `Customer.orders`-এ দিলে একজন গ্রাহক মুছলে তার সব অর্ডারের হিসাবও মুছে যাবে, যা প্রায়ই আইন বা হিসাবের দিক থেকে ভুল।

///

## 16. Relationship Loading Strategy ও Write-Only Collection { #s16 }

### 16.1 লোডিং ম্যাট্রিক্স { #s16-1 }

/// tip | উদাহরণ দিয়ে বুঝি

রেস্তোরাঁয় ১০ জন অতিথি, প্রত্যেকে ভাত আর তরকারি চাইলেন:

* **`select` (lazy)**: ওয়েটার আগে ১০ প্লেট ভাত আনেন, তারপর একেকজন তরকারি চাইলে একেকবার রান্নাঘরে যান। মোট ১১ বার যাওয়া-আসা।
* **`selectin`**: আগে সবার ভাত, তারপর এক ট্রে-তে সবার তরকারি একসাথে। মাত্র ২ বার।
* **`joined`**: ভাত আর তরকারি এক বড় থালায় সাজিয়ে একবারেই আনা। ১ বার, কিন্তু থালা ভারী (একই প্যারেন্ট অনেকবার আসে)।
* **`raise`**: ওয়েটার আগেই জানিয়ে রাখেন, "আগে না বললে তরকারি আনব না।" ভুলবশত চাইলে সাথে সাথে এরর।

///

| স্ট্র্যাটেজি | কুয়েরি সংখ্যা | SQL আকার | কোথায় সেরা | Async-এ নিরাপদ? |
| :--- | :--- | :--- | :--- | :--- |
| **`select`** (lazy, ডিফল্ট) | N + 1 | প্রথম অ্যাক্সেসে আলাদা `SELECT ... WHERE parent_id = ?` | ছোট sync স্ক্রিপ্ট | ❌ ইমপ্লিসিট অ্যাক্সেসে `MissingGreenlet` |
| **`joined`** | 1 | মূল কুয়েরিতে `LEFT OUTER JOIN` | Many-to-one, one-to-one স্কেলার | ✅ |
| **`selectin`** | 2 | মূল কুয়েরি + `SELECT ... WHERE id IN (...)` | One-to-many / many-to-many কালেকশন | ✅ **Async-এর জন্য সেরা ডিফল্ট** |
| **`subquery`** | 2 | মূল কুয়েরিকে সাবকুয়েরি হিসেবে আবার চালায় | পুরোনো 1.x কোড | ⚠️ DB-তে ভারী; `selectin` ভালো |
| **`raise`** | 0 | লোড না হওয়া অবস্থায় অ্যাক্সেসে `InvalidRequestError` | Async API-এর সব রিলেশনশিপ | ✅ স্পষ্ট লোডিং বাধ্য করে |
| **`noload`** | 0 | অ্যাট্রিবিউট খালি থাকে | বিরল বিশেষ ক্ষেত্র | ✅ |
| **`write_only`** | 0 | কালেকশন কখনো লোড হয় না | লক্ষ লক্ষ রো-র কালেকশন | ✅ |

মূল নিয়ম:
- **কালেকশন → `selectinload()`**। কালেকশনে `joinedload()` প্যারেন্ট রো গুণিতক হারে বাড়ায় (Cartesian bloat) এবং `.unique()` লাগে।
- **স্কেলার (N:1, 1:1) → `joinedload()`** (অথবা `selectinload()` — দুটোই চলে)।
- Async কোডে **প্রতিটি রিলেশনশিপে ডিফল্ট `lazy="raise"`** দিন, তারপর প্রতিটি কুয়েরিতে প্রয়োজনমতো লোড করুন।

### 16.2 কুয়েরি-টাইম loader অপশন { #s16-2 }
```python
from sqlalchemy import select
from sqlalchemy.orm import contains_eager, joinedload, raiseload, selectinload

# কালেকশন SELECT IN দিয়ে (nested), স্কেলার JOIN দিয়ে
stmt = (
    select(Customer)
    .options(
        selectinload(Customer.orders).selectinload(Order.items),
        joinedload(Customer.profile),
        raiseload("*"),                 # তালিকায় নেই এমন কিছু ছুঁলেই এরর
    )
    .where(Customer.customer_id == 100)
)

# contains_eager: কুয়েরিতে ইতিমধ্যেই সম্পর্কিত টেবিল join করা আছে — দ্বিতীয় join বা
# আলাদা কুয়েরি না করে সেই join-ই পুনর্ব্যবহার করা
stmt_eager = (
    select(Order)
    .join(Order.customer)
    .where(Customer.email.ilike("%@acme.corp"))
    .options(contains_eager(Order.customer))
)
```

/// info | কোডটি সহজ ভাষায়

* `selectinload(Customer.orders).selectinload(Order.items)`: চেইন করে দুই স্তর নিচ পর্যন্ত আগেভাগে লোড। মোট কুয়েরি: গ্রাহক + সব অর্ডার + সব আইটেম = ৩টি।
* `joinedload(Customer.profile)`: একটি মাত্র প্রোফাইল, তাই একই কুয়েরিতে `LEFT OUTER JOIN`।
* `raiseload("*")`: তালিকার বাইরে কিছু ছুঁলেই এরর, যাতে লুকানো কুয়েরি না চলে।
* `contains_eager(Order.customer)`: আপনি তো নিজেই `.join(Order.customer)` করেছেন, তাই সেই JOIN-এর ডেটা দিয়েই `order.customer` পূরণ করো, নতুন কুয়েরি নয়।

///

একটি কালেকশনে **শুধু ফিল্টার হওয়া চাইল্ড** বসাতেও `contains_eager()` ব্যবহৃত হয় ([§26](querying.md#s26) ও [§35.5](crud.md#s35-5) দেখুন): join করুন, চাইল্ডের উপর ফিল্টার দিন, তারপর `contains_eager(Parent.children)` এবং রেজাল্টে `.unique()`।

### 16.3 Write-only collection (`lazy="dynamic"`-এর 2.0 বিকল্প) { #s16-3 }
যেসব কালেকশন কখনোই পুরো লোড করা সম্ভব নয় (অডিট ইভেন্ট, লগ লাইন):
```python
from sqlalchemy.orm import WriteOnlyMapped

class Organization(Base):
    __tablename__ = "organizations"
    org_id: Mapped[int] = mapped_column(primary_key=True)

    # কখনো স্বয়ংক্রিয় লোড হয় না; .add(), .remove(), .select() দেয়
    audit_events: WriteOnlyMapped["AuditEvent"] = relationship(          # Mapped[] দিয়ে মোড়াবেন না
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# ১. বিদ্যমান রো লোড না করেই নতুন আইটেম যোগ
org.audit_events.add(AuditEvent(action="LOGIN"))

# ২. ফিল্টার করা অংশ সরাসরি DB থেকে কুয়েরি
stmt = org.audit_events.select().where(AuditEvent.action == "FAILED_ATTEMPT").limit(10)
recent_failures = (await session.scalars(stmt)).all()
```

/// warning | annotation-টি খেয়াল করুন

লিখতে হবে শুধু `WriteOnlyMapped["AuditEvent"]`, **`Mapped[...]` দিয়ে মোড়ানো নয়**। `Mapped[WriteOnlyMapped[...]]` লিখলে SQLAlchemy একে সাধারণ তালিকা ভাবে, ফলে প্রথম অ্যাক্সেসেই পুরো কালেকশন lazy-load করতে যায়, আর async-এ `MissingGreenlet` এরর আসে। (এই ভুলটি আমরা আসল PostgreSQL-এ চালিয়ে ধরেছি।)

///

## 17. N+1 Query সমস্যা { #s17 }

/// tip | উদাহরণ দিয়ে বুঝি

আপনি দোকানদার, ১০০ জন গ্রাহকের তালিকা হাতে। প্রত্যেকের অর্ডার দেখতে প্রতিবার গুদামে গিয়ে একজনের ফাইল আনছেন। ১ বার তালিকা + ১০০ বার গুদাম = **১০১ বার** যাওয়া-আসা। এটাই **N+1 সমস্যা**। বুদ্ধিমানের কাজ হলো একবারে গুদাম থেকে ১০০ জনের ফাইলই নিয়ে আসা। এটাই eager loading।

ডেটাবেস দ্রুত হলেও প্রতিটি যাওয়া-আসায় নেটওয়ার্কের সময় লাগে। ১০০ বার × ২ মিলিসেকেন্ড = শুধু অপেক্ষাতেই ২০০ মিলিসেকেন্ড।

///

### সমস্যা { #s17-a }
```python
# ১টি কুয়েরি: ১০০ জন ইউজার আনা
users = (await session.scalars(select(User))).all()

# লুপের ভেতরে আরও ১০০টি কুয়েরি: মোট ১ + ১০০ = ১০১ রাউন্ড-ট্রিপ!
for user in users:
    print(user.orders)      # async-এ এটা চলেই না: MissingGreenlet
```
Sync কোডে এটি চুপচাপ ১০১টি কুয়েরি চালায়; async কোডে ইমপ্লিসিট lazy load `MissingGreenlet` এরর দেয়।

### সমাধান: eager load { #s17-b }
```python
from sqlalchemy.orm import selectinload

# ঠিক ২টি কুয়েরি: ইউজার + এক ব্যাচে সবার অর্ডার
stmt = select(User).options(selectinload(User.orders))
users = (await session.scalars(stmt)).all()

for user in users:
    print(user.orders)      # আগেই লোড হয়ে আছে, অতিরিক্ত I/O নেই
```

/// info | তৈরি হওয়া SQL

```sql
-- ১ম কুয়েরি
SELECT users.id, users.name FROM users

-- ২য় কুয়েরি: সব ইউজারের অর্ডার একসাথে
SELECT orders.id, orders.user_id, ... FROM orders
WHERE orders.user_id IN ($1, $2, $3, ... $100)
```

ইউজার ১০০ জন হোক বা ১০,০০০ জন, কুয়েরি সবসময় ২টি। (খুব বড় তালিকা হলে SQLAlchemy নিজেই `IN`-কে ৫০০-র ব্যাচে ভাগ করে।)

///

N+1 আগেভাগে ধরার উপায়:
1. রিলেশনশিপে `lazy="raise"` — ভুলবশত অ্যাক্সেস টেস্টেই জোরালোভাবে ফেইল করবে।
2. ডেভেলপমেন্টে `echo=True` (অথবা [§46.2](advanced-mapping.md#s46-2)-এর slow-query event hook) দিয়ে স্টেটমেন্ট গুনুন।
3. Engine-এর `before_cursor_execute` listener দিয়ে টেস্টে কুয়েরি সংখ্যা assert করুন।

## 18. পূর্ণ উদাহরণ: Company → Department → Employee { #s18 }

```
Company (1)
   └── Departments (অনেক)
            └── Employees (অনেক)
```

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))

    departments: Mapped[list["Department"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"))

    company: Mapped["Company"] = relationship(back_populates="departments", lazy="raise")
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="department",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )

class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"))

    department: Mapped["Department"] = relationship(back_populates="employees", lazy="raise")
```

/// tip | `response_model` দিয়ে আরও ভালো

ORM অবজেক্ট সরাসরি রিটার্ন করলেও FastAPI JSON বানাতে পারে, কিন্তু তখন সব কলাম চলে যায় আর API ডকুমেন্টেশনে কোনো স্কিমা দেখা যায় না। Pydantic স্কিমা দিয়ে ঠিক করে দিন কী যাবে:

```python
from pydantic import BaseModel, ConfigDict


class EmployeeRead(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class DepartmentRead(BaseModel):
    id: int
    name: str
    employees: list[EmployeeRead]
    model_config = ConfigDict(from_attributes=True)


class CompanyRead(BaseModel):
    id: int
    name: str
    departments: list[DepartmentRead]
    model_config = ConfigDict(from_attributes=True)


@router.get("/companies/{company_id}", response_model=CompanyRead)
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    ...  # ওপরের মতোই, selectinload-সহ
```

রেসপন্স:

```json
{"id": 1, "name": "Acme", "departments": [{"id": 1, "name": "IT", "employees": [{"id": 1, "name": "রহিম"}, {"id": 2, "name": "করিম"}]}]}
```

`selectinload` বাদ দিয়ে শুধু `await db.get(Company, company_id)` রিটার্ন করলে `departments` লোড হয়নি বলে (`lazy="raise"`) FastAPI `ResponseValidationError` দেবে। এরর আসবে ডেভেলপমেন্টেই, প্রোডাকশনে লুকিয়ে ধীর হয়ে নয়।

///

FastAPI এন্ডপয়েন্টে পুরো ট্রি লোড করা (মোট ৩টি কুয়েরি, N+1 নেই, async-নিরাপদ):
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db

router = APIRouter()

@router.get("/companies/{company_id}")
async def get_company(company_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Company)
        .where(Company.id == company_id)
        .options(selectinload(Company.departments).selectinload(Department.employees))
    )
    company = (await db.scalars(stmt)).one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
```

/// check | সংক্ষেপে মনে রাখুন

* ফরেন কি (`ForeignKey`) = ডেটাবেসের নিয়ম; `relationship()` = Python-এর শর্টকাট। দুটোই লাগে।
* FK সবসময় "অনেক"-এর দিকে; 1:1-এ FK-তে `unique=True`; N:M-এ মধ্যবর্তী টেবিল।
* সংযোগের নিজের তথ্য থাকলে association object।
* মালিকানাধীন চাইল্ডে `cascade="all, delete-orphan"` + `passive_deletes=True` + `ondelete="CASCADE"`।
* async-এ সব রিলেশনশিপে `lazy="raise"`; কালেকশন `selectinload`, একক অবজেক্ট `joinedload`।
* লুপের ভেতরে রিলেশনশিপ ছোঁয়ার আগে ভাবুন: N+1 হচ্ছে না তো?

///

**পরের ধাপ:** ডেটাবেসের সাথে আসল যোগাযোগ কীভাবে হয়, দেখুন [Engine, Connection Pool ও Async Session](engine-session.md) অধ্যায়ে।
