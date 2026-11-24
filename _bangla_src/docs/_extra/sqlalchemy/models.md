# Model, Column ও Schema { #sqlalchemy-models }

/// note | এই পেজে যা শিখবেন

* `DeclarativeBase` দিয়ে সব মডেলের বেস ক্লাস, আর কনস্ট্রেইন্টের নামের নিয়ম (naming convention)।
* `Mapped[]` টাইপ হিন্ট থেকে SQLAlchemy কীভাবে কলামের টাইপ ও NULL-যোগ্যতা বোঝে।
* `mapped_column()`-এর সব প্যারামিটার, Python টাইপ ↔ SQL টাইপের পুরো তালিকা।
* `default`, `server_default`, `onupdate`-এর পার্থক্য; primary key ও composite key।
* `__table_args__`, `__mapper_args__`, mixin, `declared_attr`, dataclass মডেল ও Core `Table`।

///

/// tip | উদাহরণ দিয়ে বুঝি

স্কুলে ভর্তির একটি **ফর্ম** কল্পনা করুন। ফর্মে কী কী ঘর থাকবে (নাম, রোল, জন্মতারিখ), কোন ঘর বাধ্যতামূলক, কোনটা ফাঁকা রাখা যায়, সব আগে থেকে ঠিক করা। **মডেল ক্লাস** হলো সেই ফর্মের নকশা, **টেবিল** হলো পূরণ করা সব ফর্মের ফাইল, আর **প্রতিটি অবজেক্ট** হলো একজন ছাত্রের পূরণ করা একটি ফর্ম।

///

## 3. DeclarativeBase, Base ও MetaData Naming Convention { #s3 }

2.0-তে প্রতিটি মডেল `DeclarativeBase` থেকে তৈরি একটি ক্লাসকে inherit করে শুরু হয়।

### `app/core/database.py` { #s3-a }
```python
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Constraint naming convention — PostgreSQL ও Alembic-এর জন্য অত্যন্ত গুরুত্বপূর্ণ
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
```

/// info | কোডটি সহজ ভাষায়

* `class Base(DeclarativeBase)`: আপনার সব মডেল এই ক্লাস থেকে তৈরি হবে। প্রজেক্টে সাধারণত **একটিই** `Base` থাকে।
* `metadata = MetaData(naming_convention=...)`: ডেটাবেস যত কনস্ট্রেইন্ট বানাবে, সবার নাম কোন নিয়মে হবে তা বলে দেওয়া হলো।
* নিয়মের প্রতিটি লাইনের মানে, `orders` টেবিলের উদাহরণে:

| key | কিসের নাম | উদাহরণ |
| :--- | :--- | :--- |
| `ix` | সাধারণ ইনডেক্স | `ix_orders_customer_id` |
| `uq` | ইউনিক কনস্ট্রেইন্ট | `uq_orders_order_code` |
| `ck` | চেক কনস্ট্রেইন্ট | `ck_orders_positive_total` |
| `fk` | ফরেন কি | `fk_orders_customer_id_customers` |
| `pk` | প্রাইমারি কী | `pk_orders` |

///

### মডেল তৈরি { #s3-b }
```python
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
```

/// info | কোডটি সহজ ভাষায়

এই ছোট মডেল থেকে SQLAlchemy এই SQL বানায় (PostgreSQL):

```sql
CREATE TABLE users (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    CONSTRAINT pk_users PRIMARY KEY (id)
)
```

* `__tablename__ = "users"`: ডেটাবেসে টেবিলের নাম।
* `id: Mapped[int] = mapped_column(primary_key=True)`: ইন্টিজার প্রাইমারি কী, মান ডেটাবেস নিজে বাড়িয়ে বসায়।
* `name: Mapped[str]`: শুধু টাইপ হিন্ট দিলেই কলাম হয়ে যায়। `str` মানে `VARCHAR`, আর `| None` না থাকায় `NOT NULL`।
* `pk_users`: naming convention-এর `pk` নিয়ম অনুযায়ী নামটি এসেছে।

///

### `Base` কী দায়িত্ব পালন করে { #s3-c }
1. **Model Registry** — সব ম্যাপ করা ক্লাস কেন্দ্রীয়ভাবে রেজিস্টার রাখে (এ কারণেই `relationship("Order")`-এর মতো স্ট্রিং রেফারেন্স খুঁজে পাওয়া যায়)।
2. **Metadata Holder (`Base.metadata`)** — সব টেবিল, কলাম, ইনডেক্স, কনস্ট্রেইন্ট ও ফরেন কি সংগ্রহ করে রাখে।
3. **Alembic-এর ভিত্তি** — Alembic `Base.metadata`-কে লাইভ ডেটাবেসের সাথে তুলনা করে স্বয়ংক্রিয় মাইগ্রেশন তৈরি করে।

### Naming convention কেন জরুরি { #s3-d }
Convention না দিলে PostgreSQL নিজে থেকে কনস্ট্রেইন্টের নাম দেয় (যেমন `orders_customer_id_fkey`), আর অন্য ডেটাবেস দেয় অন্য নাম। ফলে Alembic নির্ভরযোগ্যভাবে কনস্ট্রেইন্ট খুঁজে drop/alter করতে পারে না এবং বিভিন্ন environment-এ ভিন্ন মাইগ্রেশন তৈরি হয়। উপরের convention থাকলে প্রতিটি কনস্ট্রেইন্টের নাম নির্দিষ্ট হয়, যেমন `fk_orders_customer_id_customers`।

/// warning | গুরুত্বপূর্ণ

প্রোডাকশনে কখনোই `Base.metadata.create_all()`-কে মাইগ্রেশন টুল হিসেবে ব্যবহার করবেন না। এটি কেবল লোকাল টেস্ট ও প্রোটোটাইপের জন্য। প্রোডাকশনে স্কিমা ভার্সন নিয়ন্ত্রণ করুন **Alembic** দিয়ে।

///

/// tip | পরামর্শ

প্রজেক্টের **প্রথম দিনেই** naming convention দিন। পরে যোগ করলে পুরোনো আর নতুন কনস্ট্রেইন্টের নাম আলাদা নিয়মে থাকবে, আর Alembic মাইগ্রেশনে ঝামেলা হবে।

///

## 4. `Mapped[]` ও স্বয়ংক্রিয় Nullability { #s4 }

`Mapped[]` হলো SQLAlchemy 2.0-এর টাইপিং জেনেরিক। এটি টাইপ চেকার (Mypy, Pyright, Pylance) **এবং** SQLAlchemy mapper—উভয়কে জানায় যে অ্যাট্রিবিউটটি সাধারণ ক্লাস ভ্যারিয়েবল নয়, বরং ORM-নিয়ন্ত্রিত কলাম বা রিলেশনশিপ।

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(100))
```

/// info | কোডটি সহজ ভাষায়

* `name: Mapped[str]` → `name VARCHAR(100) NOT NULL`: নাম দিতেই হবে।
* `nickname: Mapped[str | None]` → `nickname VARCHAR(100)` (NULL চলবে): ডাকনাম না থাকলেও চলবে।

অর্থাৎ শুধু টাইপ হিন্ট দেখেই SQLAlchemy বুঝে যায় কলামটি বাধ্যতামূলক কি না। Python-এ `None` মানে ডেটাবেসে `NULL`।

///

### অ্যানোটেশন থেকে কী অনুমান করা হয় { #s4-a }
| অ্যানোটেশন | অর্থ |
| :--- | :--- |
| `Mapped[str]` | কলাম **NOT NULL** (`nullable=False`) |
| `Mapped[str \| None]` / `Mapped[Optional[str]]` | কলামে **NULL অনুমোদিত** (`nullable=True`) |
| `Mapped[list["Order"]]` | কালেকশন রিলেশনশিপ (1:N বা N:M) |
| `Mapped["Profile"]` / `Mapped["Profile \| None"]` | স্কেলার রিলেশনশিপ (N:1 বা 1:1) |
| `mapped_column()` ছাড়া `Mapped[int]` | `Integer` টাইপের NOT NULL কলাম |

`mapped_column()`-এ স্পষ্টভাবে `nullable=` দিলে তা সবসময় অ্যানোটেশনের অনুমানকে override করে।

/// warning | সাধারণ ভুল

`Mapped[str]` লিখে `nullable=True` দিলে ডেটাবেসে NULL ঢুকতে পারবে, কিন্তু টাইপ চেকার ভাববে মান সবসময় `str`। ফলে কোডে `None` আসলে অবাক হবেন। টাইপ হিন্ট আর `nullable` মিলিয়ে লিখুন: ফাঁকা রাখা গেলে `Mapped[str | None]`।

///

## 5. `mapped_column()` — সিনট্যাক্স, টাইপ ম্যাপিং ও সম্পূর্ণ প্যারামিটার রেফারেন্স { #s5 }

Declarative ক্লাসের ভেতরে `mapped_column()` হলো 1.x-এর `Column()`-এর 2.0 বিকল্প। এটি একটি Core `Column` তৈরি করে এবং `Mapped[]` অ্যানোটেশনের সাথে মিলে SQL টাইপ ও nullability অনুমান করে।

### 5.1 সাধারণ সিনট্যাক্স { #s5-1 }
```python
attribute_name: Mapped[PythonType] = mapped_column(
    SQLType,              # অ্যানোটেশন থেকে অনুমান করা গেলে ঐচ্ছিক
    primary_key=False,
    nullable=...,
    default=...,
    server_default=...,
    unique=...,
    index=...,
    ...
)
```

### 5.2 কলাম টাইপ ম্যাপিং (Python ↔ SQLAlchemy ↔ PostgreSQL) { #s5-2 }

| ক্যাটাগরি | Python টাইপ | SQLAlchemy টাইপ | টার্গেট SQL টাইপ | `mapped_column()` উদাহরণ |
| :--- | :--- | :--- | :--- | :--- |
| **Small Integer** | `int` | `SmallInteger` | `SMALLINT` | `mapped_column(SmallInteger)` |
| **Integer** | `int` | `Integer` | `INTEGER` | `mapped_column(Integer)` |
| **Big Integer** | `int` | `BigInteger` | `BIGINT` | `mapped_column(BigInteger)` |
| **Auto-increment PK** | `int` | `Integer` / `BigInteger` | `SERIAL` / `BIGSERIAL` / `IDENTITY` | `mapped_column(primary_key=True)` |
| **Float** | `float` | `Float` | `REAL` / `FLOAT` | `mapped_column(Float)` |
| **Double** | `float` | `Double` | `DOUBLE PRECISION` | `mapped_column(Double)` |
| **Fixed decimal** | `decimal.Decimal` | `Numeric(p, s)` | `NUMERIC(p, s)` | `mapped_column(Numeric(14, 2))` |
| **নির্দিষ্ট দৈর্ঘ্যের string** | `str` | `CHAR(n)` | `CHAR(n)` | `mapped_column(CHAR(10))` |
| **পরিবর্তনশীল string** | `str` | `String(n)` | `VARCHAR(n)` | `mapped_column(String(255))` |
| **সীমাহীন text** | `str` | `Text` | `TEXT` | `mapped_column(Text)` |
| **Boolean** | `bool` | `Boolean` | `BOOLEAN` | `mapped_column(Boolean, default=True)` |
| **Timestamp + TZ** | `datetime.datetime` | `DateTime(timezone=True)` | `TIMESTAMP WITH TIME ZONE` | `mapped_column(DateTime(timezone=True))` |
| **Naive timestamp** | `datetime.datetime` | `DateTime` | `TIMESTAMP WITHOUT TIME ZONE` | `mapped_column(DateTime)` |
| **Date** | `datetime.date` | `Date` | `DATE` | `mapped_column(Date)` |
| **Time** | `datetime.time` | `Time` | `TIME` | `mapped_column(Time)` |
| **Interval** | `datetime.timedelta` | `Interval` | `INTERVAL` | `mapped_column(Interval)` |
| **Binary / BLOB** | `bytes` | `LargeBinary` | `BYTEA` / `BLOB` | `mapped_column(LargeBinary)` |
| **UUID** | `uuid.UUID` | `Uuid` | `UUID` | `mapped_column(Uuid, default=uuid.uuid4)` |
| **JSON** | `dict` / `list` | `JSON` | `JSON` | `mapped_column(JSON)` |
| **JSONB (PG)** | `dict` / `list` | `JSONB` | `JSONB` | `mapped_column(JSONB)` |
| **Enum** | `enum.Enum` | `Enum(PyEnum)` | `ENUM` / `VARCHAR` | `mapped_column(Enum(StatusEnum))` |
| **Array (PG)** | `list[T]` | `ARRAY(T)` | `T[]` (যেমন `INTEGER[]`) | `mapped_column(ARRAY(Integer))` |
| **INET (PG)** | `str` / `ipaddress` | `INET` | `INET` | `mapped_column(INET)` |
| **MAC address (PG)** | `str` | `MACADDR` | `MACADDR` | `mapped_column(MACADDR)` |

/// warning | সতর্কতা

টাকা-পয়সার হিসাবে কখনোই `Float` ব্যবহার করবেন না। বাইনারি ফ্লোটিং পয়েন্ট `0.10`-কে সঠিকভাবে প্রকাশ করতে পারে না। `Decimal`-সহ `Numeric(p, s)` ব্যবহার করুন।

///

/// tip | কোন টাইপ কখন

* **id**: সাধারণ ক্ষেত্রে `int` (অটো-ইনক্রিমেন্ট)। বাইরে দেখানো বা অনুমান-অযোগ্য id চাইলে `uuid.UUID`।
* **নাম, ইমেইল, কোড**: `String(n)`, যেখানে `n` হলো সর্বোচ্চ দৈর্ঘ্য।
* **লম্বা লেখা** (বিবরণ, ব্লগ পোস্ট): `Text`।
* **টাকা, দাম, পরিমাণ**: `Numeric(p, s)` + `Decimal`। যেমন `Numeric(12, 2)` মানে মোট ১২ অঙ্ক, তার মধ্যে দশমিকের পর ২।
* **সময়**: `DateTime(timezone=True)`, আর সবসময় UTC-তে রাখুন।
* **হ্যাঁ/না**: `bool`।
* **নির্দিষ্ট কয়েকটি মানের একটি** (যেমন অর্ডারের অবস্থা): `enum.Enum` অথবা `String` + `CheckConstraint`।

///

### 5.3 সম্পূর্ণ প্যারামিটার রেফারেন্স { #s5-3 }

/// note | সব মুখস্থ করার দরকার নেই

এই টেবিলটি রেফারেন্সের জন্য। দৈনন্দিন কাজে সবচেয়ে বেশি লাগে মাত্র কয়েকটি: `primary_key`, `nullable`, `unique`, `index`, `default`, `server_default`, `onupdate`। বাকিগুলো দরকার হলে এখানে এসে দেখে নেবেন।

///

| Parameter | Type / Signature | Default | Category | কাজ ও ব্যবহারবিধি |
| :--- | :--- | :--- | :--- | :--- |
| `__name` | `str \| None` | `None` (পজিশনাল) | Core / Schema | ডেটাবেসে কলামের নাম, যদি Python অ্যাট্রিবিউটের নাম থেকে ভিন্ন হয়। |
| `__type` | `TypeEngine \| None` | `Mapped[]` থেকে অনুমিত | Core / Schema | SQL টাইপ (`String(100)`, `Integer()` …)। অনুমান করা না গেলে দিতে হয়। |
| `*args` | `ForeignKey`, `Constraint`, `Identity`, … | — (পজিশনাল) | Core / Schema | অতিরিক্ত স্কিমা কনস্ট্রাক্ট, যেমন `ForeignKey("users.id")`, `CheckConstraint(...)`, `Identity()`। |
| `primary_key` | `bool` | `False` | Core / Schema | কলামকে primary key (বা তার অংশ) করে; স্বয়ংক্রিয়ভাবে `NOT NULL`। |
| `nullable` | `bool \| None` | অ্যানোটেশন থেকে অনুমিত | Core / Schema | `NULL` অনুমোদিত কি না। `Mapped[X \| None]` → `True`, নতুবা `False`। |
| `unique` | `bool` | `False` | Core / Schema | `UNIQUE` কনস্ট্রেইন্ট / ইউনিক ইনডেক্স তৈরি করে। |
| `index` | `bool` | `False` | Core / Schema | কলামে (B-tree) ইনডেক্স তৈরি করে। |
| `autoincrement` | `bool \| "auto" \| "ignore_fk"` | `"auto"` | Core / Schema | ইন্টিজার PK-তে SERIAL / IDENTITY / AUTO_INCREMENT নিয়ন্ত্রণ করে। |
| `quote` | `bool \| None` | `None` | Core / Schema | SQL-এ কলাম নাম বাধ্যতামূলক উদ্ধৃত (বা অনুদ্ধৃত) করবে কি না। |
| `system` | `bool` | `False` | Core / Schema | ডেটাবেসের সিস্টেম কলাম (যেমন PostgreSQL `xmin`, `ctid`) — DDL-এ কখনো তৈরি হয় না। |
| `comment` | `str \| None` | `None` | Documentation | ডেটাবেসে `COMMENT ON COLUMN` হিসেবে সংরক্ষিত হয়। |
| `doc` | `str \| None` | `None` | Documentation | ORM অ্যাট্রিবিউটের Python docstring (IDE / Sphinx)। |
| `key` | `str \| None` | `None` | ORM / Core | `Table.c`-তে কলামটি যে বিকল্প key নামে রেফার হবে। |
| `info` | `dict \| None` | `None` | Metadata | অ্যাপ্লিকেশন-লেভেলের মুক্ত মেটাডেটা (UI লেবেল, ভ্যালিডেশন হিন্ট …)। |
| `default` | scalar \| callable \| SQL expr | `None` | Value generation | INSERT-এর সময় SQLAlchemy যে ক্লায়েন্ট-সাইড ডিফল্ট বসায়। |
| `server_default` | `str \| TextClause \| FetchedValue` | `None` | Value generation | DDL-এর `DEFAULT` ক্লজ; ডেটাবেস নিজে মান দেয়। |
| `insert_default` | `Any` | `None` | Value generation | `default`-এর মতোই, তবে dataclass-এর `default` এড়িয়ে যায় (`MappedAsDataclass`-এ কাজের)। |
| `onupdate` | scalar \| callable \| SQL expr | `None` | Value generation | UPDATE-এর সময় SQLAlchemy যে ক্লায়েন্ট-সাইড মান বসায়। |
| `server_onupdate` | `FetchedValue` | `None` | Value generation | জানায় যে UPDATE-এ ডেটাবেস (trigger ইত্যাদি) মান বদলায়। |
| `deferred` | `bool` | `False` | ORM loading | প্রথম SELECT-এ লোড হবে না; প্রথম অ্যাক্সেসে লোড হবে। |
| `deferred_group` | `str \| None` | `None` | ORM loading | একই গ্রুপের deferred কলামগুলো একসাথে এক কুয়েরিতে লোড হয়। |
| `deferred_raiseload` | `bool` | `False` | ORM loading | লোড না হওয়া deferred কলাম অ্যাক্সেস করলে lazy-load না করে এরর দেয় (async-এর জন্য চমৎকার)। |
| `use_existing_column` | `bool` | `False` | ORM inheritance | সুপারক্লাসে একই নামে ঘোষিত কলাম পুনর্ব্যবহার করে (Single Table Inheritance)। |
| `active_history` | `bool` | `False` | ORM tracking | মান বদলালে আগের মান লোড করে যাতে history/event তা দেখতে পায়। |
| `sort_order` | `int` | `0` | ORM DDL | তৈরি হওয়া `CREATE TABLE`-এ কলামের ক্রম নিয়ন্ত্রণ করে। |
| `init` | `bool` | `True` | Dataclass | তৈরি হওয়া `__init__()`-এ ফিল্ডটি থাকবে কি না। |
| `repr` | `bool` | `True` | Dataclass | `__repr__()`-এ ফিল্ডটি থাকবে কি না। |
| `default_factory` | `Callable[[], Any]` | `None` | Dataclass | মিউটেবল ডিফল্টের ফ্যাক্টরি (`list`, `dict`)। |
| `compare` | `bool` | `True` | Dataclass | `__eq__` তুলনায় অন্তর্ভুক্ত হবে কি না। |
| `kw_only` | `bool` | `False` | Dataclass | `__init__()`-এ ফিল্ডটিকে keyword-only করে। |
| `hash` | `bool \| None` | `None` | Dataclass | `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `**kw` | kwargs | — | Core passthrough | ভেতরের Core `Column`-এ পাঠানো হয় (dialect-নির্দিষ্ট অপশন)। |

### 5.4 ক্যাটাগরি অনুযায়ী প্যারামিটার, উদাহরণসহ { #s5-4 }

#### ক) Core ও DDL কনস্ট্রেইন্ট { #s5-4-a }
```python
# পজিশনাল নাম + টাইপ: DB কলাম "usr_email_address", Python অ্যাট্রিবিউট "email"
email: Mapped[str] = mapped_column("usr_email_address", String(255), unique=True)

# primary_key, nullable, unique, index
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
bio: Mapped[str | None] = mapped_column(Text, nullable=True)

# quote ও comment
status_code: Mapped[str] = mapped_column(
    String(20),
    quote=True,
    comment="অ্যাকাউন্টের বর্তমান স্ট্যাটাস কোড (ACTIVE, SUSPENDED)",
)
```

/// info | কোডটি সহজ ভাষায়

* প্রথম লাইনে প্রথম আর্গুমেন্ট `"usr_email_address"` হলো ডেটাবেসের কলামের নাম, কিন্তু Python-এ আপনি লিখবেন `user.email`। পুরোনো ডেটাবেসের অদ্ভুত নামের সাথে কাজ করতে এটা কাজে লাগে।
* `unique=True`: একই ইমেইল দুবার ঢোকানো যাবে না।
* `index=True`: এই কলাম দিয়ে খোঁজা দ্রুত হবে, বইয়ের শেষের সূচিপত্রের মতো।
* `comment=...`: ডেটাবেসের ভেতরে কলামের বিবরণ হিসেবে জমা থাকে।

///

- `primary_key=True` Identity Map-এর পরিচয় নির্ধারণ করে এবং PK কনস্ট্রেইন্ট তৈরি করে।
- `unique=True` ডেটাবেসে `UNIQUE` কনস্ট্রেইন্ট তৈরি করে।
- `index=True` দ্রুত ফিল্টার/সর্টের জন্য B-tree ইনডেক্স তৈরি করে।

#### খ) মান তৈরি (`default`, `server_default`, `onupdate`) { #s5-4-b }
```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Uuid, func, text

class AuditRecord(Base):
    __tablename__ = "audit_records"

    # Python-side default: অ্যাপ্লিকেশন UUID তৈরি করে
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Python-side স্কেলার ডিফল্ট
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Server-side default: DDL-এর অংশ, ডেটাবেস নিজে মান দেয়
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),          # অথবা text("CURRENT_TIMESTAMP")
    )

    # onupdate: ORM যতবার এই রো UPDATE করবে ততবার নতুন সময় বসবে
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )
```

/// info | কোডটি সহজ ভাষায়

* `default=uuid.uuid4`: খেয়াল করুন, `uuid.uuid4()` নয়, শুধু `uuid.uuid4`। ফাংশনটি দেওয়া হয়েছে, তাই **প্রতিটি নতুন রো-র জন্য** নতুন UUID তৈরি হবে। `()` দিলে সব রো একই UUID পেত।
* `default="pending"`: মান না দিলে Python নিজে `"pending"` বসাবে।
* `server_default=func.now()`: টেবিল তৈরির SQL-এ `DEFAULT now()` লেখা হয়, তাই সময়টা বসায় ডেটাবেস।
* `onupdate=lambda: datetime.now(timezone.utc)`: ORM দিয়ে রো আপডেট করলেই নতুন সময় বসবে।

///

#### গ) ORM loading directive (`deferred`, `deferred_group`, `deferred_raiseload`) { #s5-4-c }
বড় টেক্সট বা বাইনারি কলাম প্রতিটি SELECT-এ টানলে মেমরি ও নেটওয়ার্কের অপচয় হয়। এগুলো defer করুন:
```python
class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    # সাধারণ SELECT-এ আসবে না; প্রথম অ্যাক্সেসে দুটো একসাথে লোড হবে
    content: Mapped[str] = mapped_column(Text, deferred=True, deferred_group="full_text")
    rendered_html: Mapped[str] = mapped_column(Text, deferred=True, deferred_group="full_text")

    # Deferred এবং lazy-load নিষিদ্ধ: লুকানো I/O না করে এরর দেবে (async-এ আদর্শ)
    attachment_blob: Mapped[bytes | None] = mapped_column(
        LargeBinary, deferred=True, deferred_raiseload=True
    )
```

/// info | কোডটি সহজ ভাষায়

* সাধারণ `select(Article)` শুধু `id` আর `title` আনবে। বড় `content` আর `rendered_html` তখনই আসবে যখন দরকার।
* একই `deferred_group` থাকায় দুটির একটি ছুঁলেই দুটোই একসাথে এক কুয়েরিতে আসে।
* `deferred_raiseload=True`: লোড না করে ছুঁলে সরাসরি এরর দেবে, লুকিয়ে কুয়েরি চালাবে না।

///

/// warning | async-এ সাবধান

async কোডে deferred কলাম লোড না করে পড়লে (`article.content`) `MissingGreenlet` এরর আসে। দরকার হলে কুয়েরিতেই বলে দিন: `select(Article).options(undefer_group("full_text"))`।

///

Async কোডে deferred কলাম স্পষ্টভাবে লোড করুন: `select(Article).options(undefer(Article.content))` অথবা `undefer_group("full_text")`।

#### ঘ) Dataclass ইন্টিগ্রেশন (`MappedAsDataclass`) { #s5-4-d }
```python
from sqlalchemy import JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

class DataclassBase(MappedAsDataclass, DeclarativeBase):
    pass

class Customer(DataclassBase):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)          # __init__-এ দিতে হবে না
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), kw_only=True)          # keyword-only আর্গুমেন্ট
    password_hash: Mapped[str] = mapped_column(String(255), repr=False)    # repr-এ গোপন থাকবে
    tags: Mapped[list[str]] = mapped_column(JSON, default_factory=list)    # মিউটেবল ডিফল্ট
```

/// info | কোডটি সহজ ভাষায়

`MappedAsDataclass` থাকলে মডেলটি একটি আসল Python dataclass হয়ে যায়। ফলে `__init__`, `__repr__`, `__eq__` নিজে থেকে তৈরি হয়:

```python
customer = Customer("রহিম", email="rahim@example.com", password_hash="...")
print(customer)
# Customer(id=None, name='রহিম', email='rahim@example.com', tags=[])
```

* `init=False`: `id` কনস্ট্রাক্টরে দিতে হয় না, ডেটাবেস বসাবে।
* `kw_only=True`: `email` নাম দিয়েই দিতে হবে (`email=...`)।
* `repr=False`: পাসওয়ার্ড হ্যাশ প্রিন্ট বা লগে দেখা যাবে না।
* `default_factory=list`: প্রতিটি অবজেক্ট নিজের আলাদা খালি তালিকা পাবে।

///

## 6. `default` বনাম `server_default` বনাম `onupdate` বনাম `server_onupdate` { #s6 }

/// tip | উদাহরণ দিয়ে বুঝি

একটি রেজিস্টার খাতার কথা ভাবুন। **`default`** মানে দোকানদার নিজে হাতে ঘরটি পূরণ করে দেন, কিন্তু শুধু তিনি লিখলেই। অন্য কেউ খাতায় লিখলে ঘরটা ফাঁকা থেকে যায়। **`server_default`** মানে খাতার ঘরে আগে থেকেই ছাপা আছে। যে-ই লিখুক, ঘরটা কখনো ফাঁকা থাকে না।

///

| ফিচার | কোথায় চলে | কখন ব্যবহার করবেন | উদাহরণ |
| :--- | :--- | :--- | :--- |
| **`default`** | Python, SQLAlchemy-র ভেতরে | মান অ্যাপ্লিকেশনের লজিক থেকে আসে | `default=uuid.uuid4`, `default="active"` |
| **`server_default`** | ডেটাবেস সার্ভার (DDL-এ) | অন্য ক্লায়েন্ট রো ঢোকালেও মান থাকা চাই | `server_default=text("now()")` |
| **`onupdate`** | Python, SQLAlchemy-র ভেতরে | ORM রো আপডেট করলেই মান স্বয়ংক্রিয়ভাবে রিফ্রেশ | `onupdate=func.now()` |
| **`server_onupdate`** | ডেটাবেস trigger / মেকানিজম | ডেটাবেস মান বদলায়; ORM-কে জানাতে হয় যে আবার আনতে হবে | `server_onupdate=FetchedValue()` |

গুরুত্বপূর্ণ ফলাফল:
- Raw SQL বা অন্য অ্যাপ্লিকেশন যে রো লেখে, সেখানে `default` / `onupdate` কাজ **করে না**; `server_default` করে।
- `onupdate` কেবল তখনই চলে যখন ORM সেই রো-র জন্য UPDATE পাঠায় (অথবা বাল্ক `update()` যদি ওই কলাম স্পষ্টভাবে সেট না করে)।
- INSERT-এর পর সার্ভারে তৈরি মান রিফ্রেশ না করা পর্যন্ত Python অবজেক্টে থাকে না। `await session.refresh(obj)`, `__mapper_args__ = {"eager_defaults": True}`, অথবা `RETURNING` ব্যবহার করুন।

## 7. Primary Key ও Composite Primary Key { #s7 }

### একক primary key { #s7-a }
```python
id: Mapped[int] = mapped_column(primary_key=True)
```

### Composite primary key { #s7-b }
যখন দুই বা ততোধিক কলাম মিলে একটি রো-র পরিচয় গড়ে (junction টেবিল এবং OFBiz-ধাঁচের চাইল্ড টেবিলে সাধারণ, যেমন `(order_id, order_item_seq_id)`):

```python
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        PrimaryKeyConstraint("student_id", "course_id", name="pk_enrollments"),
        {"schema": "core"},
    )

    student_id: Mapped[int] = mapped_column(ForeignKey("core.students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("core.courses.id"), primary_key=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

/// tip | উদাহরণ দিয়ে বুঝি

একটি স্কুলে শুধু রোল নম্বর দিয়ে ছাত্র চেনা যায় না, কারণ প্রতিটি ক্লাসেই রোল ১ আছে। কিন্তু **(ক্লাস, রোল)** জোড়া একসাথে নিলে প্রত্যেকে অনন্য। এটাই **composite primary key**। এখানে একজন ছাত্র একটি কোর্সে একবারই ভর্তি হতে পারে, তাই `(student_id, course_id)` জোড়াই পরিচয়।

///

Composite-key রো খুঁজতে কলামের ক্রম অনুযায়ী tuple দিন: `await session.get(Enrollment, (student_id, course_id))`।

## 8. Model Class Directives: `__tablename__`, `__table_args__`, `__mapper_args__`, Mixin, `declared_attr`, Dataclass { #s8 }

Declarative মডেলে কয়েকটি ক্লাস-লেভেল directive আছে যা ডেটাবেস স্কিমা এবং ORM ম্যাপিং আচরণ—দুটোই নিয়ন্ত্রণ করে।

### 8.1 `__tablename__` { #s8-1 }
```python
class Product(Base):
    __tablename__ = "products"   # স্ট্যাটিক নাম
```
Mixin-এ `@declared_attr.directive` দিয়ে ডায়নামিকভাবে তৈরি করা যায়:
```python
from sqlalchemy.orm import declared_attr

class TablenameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"   # যেমন Product -> "products"
```

### 8.2 `__table_args__` — কনস্ট্রেইন্ট, ইনডেক্স, স্কিমা ও dialect অপশন { #s8-2 }
`__table_args__` হয় একটি **tuple** (পজিশনাল কনস্ট্রেইন্ট/ইনডেক্স, এবং ঐচ্ছিকভাবে **সবার শেষে** একটি dict), অথবা শুধু একটি **dict**।

```python
from decimal import Decimal
from sqlalchemy import CheckConstraint, Index, Numeric, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

class TenantAccount(Base):
    __tablename__ = "tenant_accounts"
    __table_args__ = (
        # মাল্টি-টেন্যান্ট ইউনিকনেস: প্রতিটি টেন্যান্টের মধ্যে username ইউনিক
        UniqueConstraint("tenant_id", "username", name="uq_tenant_username"),
        # ব্যালেন্স ঋণাত্মক হতে পারবে না
        CheckConstraint("balance >= 0", name="positive_balance"),   # convention-এ নাম হবে ck_tenant_accounts_positive_balance
        # সবচেয়ে বেশি ব্যবহৃত ফিল্টারের জন্য কম্পোজিট ইনডেক্স
        Index("ix_tenant_status", "tenant_id", "status"),
        # Partial index (PostgreSQL): শুধু সক্রিয় অ্যাকাউন্ট ইনডেক্স হবে
        Index("ix_tenant_active", "tenant_id", postgresql_where=text("status = 'ACTIVE'")),
        # অপশন dict — সবসময় tuple-এর সবার শেষে
        {
            "schema": "core",
            "comment": "প্রতি টেন্যান্টের লগইন অ্যাকাউন্ট",
        },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int]
    username: Mapped[str] = mapped_column(String(50))
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[str] = mapped_column(String(20))
```

/// info | কোডটি সহজ ভাষায়

* `UniqueConstraint("tenant_id", "username")`: একই টেন্যান্টে একই username দুবার নয়, কিন্তু আলাদা টেন্যান্টে একই username চলবে।
* `CheckConstraint("balance >= 0")`: ডেটাবেস নিজেই ঋণাত্মক ব্যালেন্স প্রত্যাখ্যান করবে, অ্যাপে বাগ থাকলেও।
* `Index("ix_tenant_status", "tenant_id", "status")`: দুই কলাম একসাথে দিয়ে খোঁজা দ্রুত হবে।
* `postgresql_where=...`: শুধু সক্রিয় রো ইনডেক্সে থাকবে, তাই ইনডেক্স ছোট ও দ্রুত।
* শেষের dict: `{"schema": "core", ...}` সবসময় tuple-এর **একদম শেষে**।

///

/// warning | কনস্ট্রেইন্টের নাম আর naming convention

§3-এর convention-এ `ck` নিয়মটি `ck_%(table_name)s_%(constraint_name)s`। তাই `CheckConstraint`-এ নাম দিন **উপসর্গ ছাড়া**, যেমন `name="positive_balance"`। তাহলে আসল নাম হবে `ck_tenant_accounts_positive_balance`। `name="ck_positive_balance"` লিখলে নাম হয়ে যায় `ck_tenant_accounts_ck_positive_balance`, মানে উপসর্গ দুবার।

///

অপশন dict-এর বহুল ব্যবহৃত key:

| Key | উদ্দেশ্য |
| :--- | :--- |
| `"schema"` | টেবিলটি কোন ডেটাবেস স্কিমায় থাকবে (`"core"`, `"sales"`) |
| `"comment"` | টেবিল-লেভেলের `COMMENT ON TABLE` |
| `"postgresql_partition_by"` | যেমন `"RANGE (created_at)"` — declarative partitioning |
| `"postgresql_tablespace"` | টেবিলস্পেসের নাম |
| `"mysql_engine"` / `"mysql_charset"` | `"InnoDB"`, `"utf8mb4"` |
| `"sqlite_autoincrement"` | SQLite `AUTOINCREMENT` ব্যবহার |
| `"extend_existing"` | `MetaData`-তে আগে থেকে থাকা টেবিল পুনঃসংজ্ঞায়নের অনুমতি (reflection-এ) |

OFBiz-ধাঁচের মডেলগুলোও ([§25](querying.md#s25)) এভাবেই ফরেন কি ঘোষণা করে — `__table_args__`-এর ভেতরে `ForeignKeyConstraint([...], [...], name=...)`। **Composite** ফরেন কি-র জন্য এটি বাধ্যতামূলক।

### 8.3 `__mapper_args__` — ORM mapper কনফিগারেশন { #s8-3 }

| Mapper directive | কাজ | উদাহরণ |
| :--- | :--- | :--- |
| `polymorphic_on` | Inheritance-এর discriminator কলাম | `{"polymorphic_on": "type"}` |
| `polymorphic_identity` | এই ক্লাসকে চিহ্নিত করার মান | `{"polymorphic_identity": "manager"}` |
| `polymorphic_abstract` | মধ্যবর্তী ক্লাস যা কখনো instantiate হবে না (2.0) | `{"polymorphic_abstract": True}` |
| `concrete` | Concrete table inheritance | `{"concrete": True}` |
| `with_polymorphic` | বেস-ক্লাস কুয়েরিতে সাবক্লাসের কলাম স্বয়ংক্রিয় লোড | `{"with_polymorphic": "*"}` |
| `polymorphic_load` | সাবক্লাস লোডিং ধরন (`"inline"` / `"selectin"`) | `{"polymorphic_load": "selectin"}` |
| `version_id_col` | **Optimistic locking**-এর ভার্সন কলাম | `{"version_id_col": version}` |
| `version_id_generator` | কাস্টম ভার্সন জেনারেটর (সার্ভার-সাইডের জন্য `False`) | `{"version_id_generator": lambda v: (v or 0) + 1}` |
| `eager_defaults` | INSERT/UPDATE-এর পরপরই সার্ভারে তৈরি ডিফল্ট আনা | `{"eager_defaults": True}` |
| `primary_key` | PK ছাড়া view/টেবিল ম্যাপ করতে PK ঘোষণা | `{"primary_key": [col1, col2]}` |
| `confirm_deleted_rows` | DELETE রো-কাউন্ট না মিললে সতর্কতা (`False` দিলে এড়িয়ে যায়) | `{"confirm_deleted_rows": False}` |
| `column_prefix` | স্বয়ংক্রিয় ম্যাপ হওয়া অ্যাট্রিবিউট নামের আগে প্রিফিক্স | `{"column_prefix": "_"}` |

/// note | নোট

1.x-এর mapper অপশন `order_by` 2.0-তে **সরিয়ে ফেলা হয়েছে**। অর্ডারিং প্রতিটি `select()`-এ (অথবা `relationship(order_by=...)`-এ) দিন।

///

#### উদাহরণ: inheritance + optimistic locking { #s8-3-a }
`version_id_col`-এ কলাম অবজেক্টটি দিতে হয়, তাই কলামটি `__mapper_args__`-এর **আগে** ঘোষণা করুন (শুধু `polymorphic_on` স্ট্রিং নাম গ্রহণ করে):

```python
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50))
    version_id: Mapped[int] = mapped_column(default=1)

    __mapper_args__ = {
        "polymorphic_on": "role",
        "polymorphic_identity": "employee",
        "version_id_col": version_id,      # উপরে ঘোষিত কলাম অবজেক্ট
        "eager_defaults": True,
    }

class Manager(Employee):
    department_managed: Mapped[str | None] = mapped_column(String(100))

    __mapper_args__ = {"polymorphic_identity": "manager"}
```

/// note | ক্রম জরুরি

`"version_id_col": version_id` লাইনে `version_id` একটি Python ভেরিয়েবল, যা ঠিক ওপরে কলাম হিসেবে ঘোষণা করা হয়েছে। তাই `__mapper_args__` সবসময় কলামগুলোর **নিচে** লিখুন। ওপরে লিখলে `NameError` আসবে। optimistic locking কী, তা বিস্তারিত পাবেন [Concurrency](concurrency.md#s47-4) অধ্যায়ে।

///

### 8.4 Mixin ও `__abstract__ = True` { #s8-4 }
- একটি **সাধারণ mixin** (যে ক্লাস `Base` inherit করে *না*) কেবল কলাম যোগ করে; এর জন্য বিশেষ কিছু লাগে না।
- `__abstract__ = True` সেই ক্লাসের জন্য যা `Base` inherit **করে** কিন্তু নিজের কোনো টেবিল চায় না — যেমন শেয়ার্ড কলামসহ একটি মধ্যবর্তী বেস।

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:
    """যেকোনো মডেলের জন্য স্বয়ংক্রিয় টাইমস্ট্যাম্প কলাম।"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class AuditedBase(Base):
    __abstract__ = True                       # AuditedBase-এর নিজের কোনো টেবিল নেই
    created_by: Mapped[str | None] = mapped_column(String(64))

class User(TimestampMixin, AuditedBase):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
```

/// tip | উদাহরণ দিয়ে বুঝি

**Mixin** হলো রেডিমেড স্টিকারের মতো। প্রায় প্রতিটি টেবিলে `created_at` আর `updated_at` লাগে। প্রতিবার লেখার বদলে একবার `TimestampMixin` বানিয়ে যেকোনো মডেলে "লাগিয়ে" দিন: `class User(TimestampMixin, Base)`।

`AuditedBase`-এ `__abstract__ = True` থাকায় এর নিজের কোনো টেবিল হয় না, শুধু এর সন্তানদের (`User`) টেবিল হয়, যেখানে `created_by` কলামটিও থাকে।

///

### 8.5 `__table__` — imperative টেবিল ম্যাপিং { #s8-5 }
বিদ্যমান Core `Table`-এর (যেমন লিগ্যাসি টেবিল বা view) উপর ক্লাস ম্যাপ করতে:
```python
from sqlalchemy import Column, Integer, String, Table

class LegacyUser(Base):
    __table__ = Table(
        "legacy_users",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("username", String(50)),
    )
```

### 8.6 `@declared_attr` — mixin-এ প্রতি-সাবক্লাস অ্যাট্রিবিউট { #s8-6 }
`ForeignKey`-যুক্ত কলাম এবং রিলেশনশিপ প্রতিটি সাবক্লাসের জন্য **আলাদাভাবে** তৈরি হতে হয়; `@declared_attr` mixin অ্যাট্রিবিউটকে একটি ফ্যাক্টরিতে পরিণত করে:
- `@declared_attr` — ডায়নামিক কলাম, ফরেন কি, রিলেশনশিপ।
- `@declared_attr.directive` — মেথড থেকে `__tablename__`, `__table_args__`, `__mapper_args__` রিটার্ন করতে।
- `@declared_attr.cascading` — inheritance চেইনের প্রতিটি ক্লাসে আবার মূল্যায়ন করতে।

```python
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

class TenantMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("core.tenants.id", ondelete="CASCADE"), index=True)

    @declared_attr.directive
    def __table_args__(cls):
        return (
            Index(f"ix_{cls.__tablename__}_tenant", "tenant_id"),
            {"schema": "core"},
        )
```

/// info | কোডটি সহজ ভাষায়

সাধারণ mixin-এ `ForeignKey`-যুক্ত কলাম সরাসরি লেখা যায় না, কারণ প্রতিটি মডেলের জন্য আলাদা কলাম অবজেক্ট লাগে। `@declared_attr` এই সমস্যা মেটায়: প্রতিটি সাবক্লাসের জন্য ফাংশনটি আবার চালিয়ে নতুন কলাম বানায়।

```python
class Invoice(TenantMixin, Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)
# ফলাফল: core.invoices টেবিলে tenant_id (FK → core.tenants.id) + ix_invoices_tenant ইনডেক্স
```

///

### 8.7 `MappedAsDataclass`-এর ক্লাস-লেভেল অপশন { #s8-7 }
বেস যখন dataclass বেস (`class DataclassBase(MappedAsDataclass, DeclarativeBase)`), তখন প্রতিটি মডেল ক্লাস-কীওয়ার্ড হিসেবে স্ট্যান্ডার্ড dataclass অপশন দিতে পারে:
```python
class User(DataclassBase, unsafe_hash=True, kw_only=True):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    email: Mapped[str]
```
উপলব্ধ অপশন: `init`, `repr`, `eq`, `order`, `unsafe_hash`, `match_args`, `kw_only`, `slots` (সতর্কতা: অনেক সেটআপে `slots=True` SQLAlchemy instrumentation-এর সাথে দ্বন্দ্ব করে — টেস্ট না করে ব্যবহার করবেন না), এবং `dataclass_callable`।

### 8.8 মডেল docstring { #s8-8 }
ক্লাসের docstring IDE, Sphinx ও inspection টুলের জন্য মডেলের ডকুমেন্টেশন হিসেবে কাজ করে:
```python
class Customer(Base):
    """
    গ্রাহক তথ্য সংরক্ষণের মাস্টার মডেল।
    বিলিং ও শিপিং তথ্য এই টেবিলের সাথে সম্পর্কিত।
    """
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
```

### 8.9 এক নজরে সামারি টেবিল { #s8-9 }

| Directive / Option | Type | উদ্দেশ্য | সাধারণ ব্যবহার |
| :--- | :--- | :--- | :--- |
| `__tablename__` | `str` / directive | টেবিলের নাম | `__tablename__ = "orders"` |
| `__table_args__` | `tuple \| dict` | কনস্ট্রেইন্ট, ইনডেক্স, স্কিমা, dialect অপশন | `(UniqueConstraint(...), {"schema": "core"})` |
| `__mapper_args__` | `dict` | Polymorphism, optimistic locking, eager defaults | `{"polymorphic_on": "role", "version_id_col": version_id}` |
| `__abstract__` | `bool` | নিজের টেবিল ছাড়া `Base` সাবক্লাস | `__abstract__ = True` |
| `__table__` | `Table` | বিদ্যমান Core টেবিলে ম্যাপ | `__table__ = legacy_table` |
| `@declared_attr` | decorator | Mixin-এ প্রতি-সাবক্লাস কলাম/রিলেশনশিপ | `@declared_attr def tenant_id(cls): ...` |
| `MappedAsDataclass` | base mixin | মডেলকে আসল dataclass বানায় | `class Base(MappedAsDataclass, DeclarativeBase)` |
| docstring | `str` | মডেলের ডকুমেন্টেশন | `"""বিবরণ"""` |

## 9. Core `Table` সংজ্ঞা, Reflection ও Inspection { #s9 }

ORM-এর নিচে Core আছে। ক্লাস ছাড়াই টেবিল সংজ্ঞায়িত করা যায় — association টেবিল, রিপোর্টিং টেবিল বা হাই-থ্রুপুট Core-only কোডে কাজে লাগে।

### 9.1 অ্যাডভান্সড কনস্ট্রেইন্টসহ বিশুদ্ধ Core টেবিল { #s9-1 }
```python
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, ForeignKey, Index, Integer,
    MetaData, Numeric, String, Table, UniqueConstraint, func, text,
)

metadata = MetaData(naming_convention=NAMING_CONVENTION)

orders_table = Table(
    "orders",
    metadata,
    Column("order_id", Integer, primary_key=True, autoincrement=True),
    Column("customer_id", Integer, ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False),
    Column("order_code", String(32), nullable=False),
    Column("total_amount", Numeric(12, 2), nullable=False),
    Column("status", String(20), nullable=False, server_default="PENDING"),
    Column("is_active", Boolean, nullable=False, server_default=text("true")),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),

    # টেবিল-লেভেল কনস্ট্রেইন্ট
    CheckConstraint("total_amount >= 0", name="positive_total_amount"),
    UniqueConstraint("order_code", name="uq_orders_order_code"),

    # Partial index: শুধু সক্রিয় অর্ডার ইনডেক্স হবে
    Index("ix_orders_active_created", "created_at", postgresql_where=text("is_active")),
)
```

### 9.2 Reflection ও রানটাইম inspection { #s9-2 }
```python
from sqlalchemy import Table, inspect

inspector = inspect(sync_engine)

table_names = inspector.get_table_names(schema="public")
columns = inspector.get_columns("orders")
foreign_keys = inspector.get_foreign_keys("orders")
indexes = inspector.get_indexes("orders")

# বিদ্যমান টেবিলকে Core Table অবজেক্টে reflect করা
reflected_users = Table("users", metadata, autoload_with=sync_engine)
```

`AsyncEngine`-এ inspection কানেকশনের sync দিকে চালাতে হয়:
```python
async with async_engine.connect() as conn:
    tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
```

/// tip | Reflection কখন কাজে লাগে

* পুরোনো (legacy) ডেটাবেস, যার মডেল আপনার কাছে নেই।
* অ্যাডমিন বা রিপোর্টিং টুল, যা যেকোনো টেবিল দেখাতে পারে।
* মাইগ্রেশনের পর যাচাই করা যে টেবিলে ঠিক কলামগুলো আছে।

নতুন প্রজেক্টে সাধারণত reflection লাগে না। সেখানে মডেলই হলো স্কিমার আসল উৎস।

///

## সাধারণ ভুল { #bn-models-mistakes }

/// warning | সাধারণ ভুল

* **টাকার কলামে `Float`**: `0.1 + 0.2` হয়ে যায় `0.30000000000000004`। সবসময় `Numeric` + `Decimal`।
* **`default=datetime.now()`**: `()` দিলে অ্যাপ চালুর মুহূর্তের সময় সব রো-তে বসে যায়। লিখুন `default=datetime.now` অথবা `server_default=func.now()`।
* **`default=[]` বা `default={}`**: সব অবজেক্ট একই তালিকা শেয়ার করে। লিখুন `default=list` বা `default_factory=list`।
* **টাইমজোন ছাড়া `DateTime`**: সার্ভার বদলালে বা বিভিন্ন দেশের ইউজার এলে সময় গোলমাল হয়। `DateTime(timezone=True)` + UTC।
* **naming convention পরে যোগ করা**: প্রথম দিনেই দিন।

///

/// check | সংক্ষেপে মনে রাখুন

* সব মডেল একটি `Base(DeclarativeBase)` থেকে; `Base.metadata`-তে naming convention।
* `Mapped[X]` = NOT NULL, `Mapped[X | None]` = NULL চলবে।
* `mapped_column()`-এ টাইপ, `primary_key`, `unique`, `index`, `default`, `server_default`।
* `default` চলে Python-এ, `server_default` চলে ডেটাবেসে।
* কনস্ট্রেইন্ট ও ইনডেক্স `__table_args__`-এ, ORM আচরণ `__mapper_args__`-এ।
* বারবার লাগা কলাম mixin-এ রাখুন।

///

**পরের ধাপ:** টেবিলগুলোর মধ্যে সম্পর্ক তৈরি করুন [Relationship](relationships.md) অধ্যায়ে।
