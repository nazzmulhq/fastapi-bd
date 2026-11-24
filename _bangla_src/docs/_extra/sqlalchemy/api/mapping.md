# ORM ম্যাপিং API: মডেল, কলাম ও রিলেশনশিপ { #api-mapping }

/// note | এই পেজে যা আছে

* মডেলের বেস ক্লাস: `DeclarativeBase`, `DeclarativeBaseNoMeta`, `MappedAsDataclass`, আর টাইপ: `Mapped`, `WriteOnlyMapped`, `DynamicMapped`।
* `mapped_column()`-এর **সব ৩৩টি** আর `relationship()`-এর **সব ৩৯টি** প্যারামিটার, সহজ বাংলায়।
* `column_property()`, `deferred()`, `composite()`, `synonym()`, `query_expression()`, `backref()`, `foreign()`, `remote()`, `validates()`, `reconstructor()`, `declared_attr` আর পুরোনো (legacy) হেল্পারগুলো।

///

মডেল লেখার ধারণাগুলো ধাপে ধাপে শিখতে দেখুন [Model](../models.md) ও [Relationship](../relationships.md) অধ্যায়। এই পেজ হলো অভিধান: প্রতিটি ফাংশন আর প্রতিটি প্যারামিটার ঠিক কী করে।

/// info | উদাহরণগুলো সম্পর্কে

প্রতিটি উদাহরণ নিজের মডেল নিজেই সংজ্ঞায়িত করে (`class Base(DeclarativeBase)` থেকে শুরু), তাই আলাদা করে কপি করে চালানো যায়। ধরে নেওয়া হয়েছে `engine` একটি PostgreSQL engine। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা হয়েছে।

///

## `DeclarativeBase` { #declarativebase }

```python
from sqlalchemy.orm import DeclarativeBase
```

সব মডেলের বেস ক্লাস বানানোর আধুনিক (2.0+) উপায়। এর একটি সাবক্লাস বানান (`class Base(DeclarativeBase): pass`), তারপর প্রতিটি মডেল সেই `Base` থেকে তৈরি করুন। সাবক্লাস করার সময় নিজে থেকেই একটি নতুন `registry` আর `MetaData` তৈরি হয়।

`Base`-এ যা যা সেট বা ব্যবহার করা যায়:

| নাম | কাজ |
| :--- | :--- |
| `metadata` | সব টেবিলের সংগ্রহ (`MetaData`)। নিজে দিলে (যেমন naming convention-সহ) সেটাই ব্যবহার হয়। `Base.metadata.create_all(engine)` এখান থেকেই। |
| `registry` | মডেলগুলোর রেজিস্ট্রি; স্ট্রিং নাম (`relationship("Address")`) এখান থেকেই খোঁজা হয়। দেখুন [Registry API](registry.md)। |
| `type_annotation_map` | Python টাইপ → SQL টাইপের নিজস্ব ম্যাপ, যেমন `{str: String(255), Decimal: Numeric(12, 2)}`। |
| `__tablename__` | (মডেলে) ডেটাবেসে টেবিলের নাম। |
| `__table_args__` | (মডেলে) কনস্ট্রেইন্ট, ইনডেক্স, স্কিমা ইত্যাদি। দেখুন [§8.2](../models.md#s8-2)। |
| `__mapper_args__` | (মডেলে) ORM ম্যাপিংয়ের অপশন, যেমন `version_id_col`, `polymorphic_on`, `eager_defaults`। পূর্ণ তালিকা [§8.3](../models.md#s8-3)। |
| `__abstract__` | `True` দিলে এই ক্লাসের নিজের টেবিল হয় না, শুধু সন্তানদের হয়। |
| `__table__` | (ম্যাপ হওয়ার পর) তৈরি হওয়া Core `Table` অবজেক্ট; নিজে দিলে বিদ্যমান টেবিলে ম্যাপ হয়। |
| `__mapper__` | (ম্যাপ হওয়ার পর) ক্লাসের `Mapper` অবজেক্ট। |
| `__init__` | ডিফল্ট কনস্ট্রাক্টর: শুধু keyword আর্গুমেন্ট নেয়, যেমন `User(name="x")`। |

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    type_annotation_map = {str: String(100)}          # সব Mapped[str] = VARCHAR(100)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

Base.metadata.create_all(engine)
print(User.__table__.c.name.type)          # VARCHAR(100)
print(User.__mapper__.class_ is User)      # True
with Session(engine) as s:
    s.add(User(name="রহিম")); s.commit()
    print(s.scalar(select(User.name)))     # রহিম
```

## `DeclarativeBaseNoMeta` { #declarativebasenometa }

```python
from sqlalchemy.orm import DeclarativeBaseNoMeta
```

`DeclarativeBase`-এর মতোই, কিন্তু metaclass ব্যবহার করে না। আপনার মডেলে অন্য কোনো লাইব্রেরির metaclass থাকলে (যেমন কিছু ABC বা ফ্রেমওয়ার্ক) সংঘর্ষ এড়াতে এটি ব্যবহার করুন। পার্থক্য: ক্লাস বানানোর পরে নতুন অ্যাট্রিবিউট যোগ করলে তা নিজে থেকে ম্যাপ হয় না।

**উদাহরণ:**

```python
class Base(DeclarativeBaseNoMeta):
    pass

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)

print(Item.__table__.name)   # items
```

## `MappedAsDataclass` { #mappedasdataclass }

```python
from sqlalchemy.orm import MappedAsDataclass
```

এই mixin বেসে যোগ করলে প্রতিটি মডেল একটি আসল Python **dataclass** হয়: `__init__`, `__repr__`, `__eq__` নিজে থেকে তৈরি হয়, আর টাইপ চেকার কনস্ট্রাক্টরের আর্গুমেন্টও যাচাই করে। কলামে `init=False`, `default=`, `default_factory=`, `kw_only=`, `repr=False` ইত্যাদি দিয়ে প্রতিটি ফিল্ড নিয়ন্ত্রণ করুন।

ক্লাস বানানোর সময় dataclass-এর অপশনও দেওয়া যায়: `class User(Base, kw_only=True, unsafe_hash=True)`। সমর্থিত: `init`, `repr`, `eq`, `order`, `unsafe_hash`, `match_args`, `kw_only`, `dataclass_callable`।

**উদাহরণ:**

```python
class Base(MappedAsDataclass, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    tags: Mapped[list[str]] = mapped_column(postgresql.ARRAY(String), default_factory=list)

u = User("রহিম")
print(u)                     # User(id=None, name='রহিম', tags=[])
print(dataclasses.is_dataclass(u))   # True
```

## `Mapped` { #mapped }

```python
from sqlalchemy.orm import Mapped
```

মডেলের প্রতিটি ম্যাপ করা অ্যাট্রিবিউটের টাইপ হিন্ট। `Mapped[int]` বলে দেয় "এটা ORM-নিয়ন্ত্রিত, Python-এ মান `int`"। টাইপ থেকেই SQL টাইপ আর NULL-যোগ্যতা অনুমান হয়: `Mapped[str]` = NOT NULL, `Mapped[str | None]` = NULL চলবে। রিলেশনশিপে `Mapped[list["Address"]]` (কালেকশন) বা `Mapped["User"]` (একটি)।

ক্লাস লেভেলে (`User.name`) এটি একটি SQL এক্সপ্রেশন, তাই `User.name == "x"`, `User.name.like(...)`, `User.id.in_([...])` লেখা যায়। এই অপারেটর-মেথডগুলোর (`==`, `in_`, `like`, `between` …) পূর্ণ রেফারেন্স আসছে SQL এক্সপ্রেশন পেজে।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    nickname: Mapped[str | None]

print(User.__table__.c.name.nullable, User.__table__.c.nickname.nullable)   # False True
print(select(User.id).where(User.name.like("র%")))
# SELECT users.id FROM users WHERE users.name LIKE :name_1
```

## `WriteOnlyMapped` { #writeonlymapped }

```python
from sqlalchemy.orm import WriteOnlyMapped
```

"write-only" কালেকশন রিলেশনশিপের টাইপ। কালেকশনটি কখনো পুরোটা লোড হয় না; বদলে `.add()`, `.remove()` আর `.select()` (ফিল্টার করা কুয়েরি) পাওয়া যায়। লক্ষ লক্ষ চাইল্ডের ক্ষেত্রে (লগ, অডিট ইভেন্ট) আদর্শ। **`Mapped[...]` দিয়ে মোড়াবেন না**: লিখুন `WriteOnlyMapped["Event"]`।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    events: WriteOnlyMapped["Event"] = relationship()

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    kind: Mapped[str]

Base.metadata.create_all(engine)
with Session(engine) as s:
    acc = Account(id=1)
    acc.events.add_all([Event(kind="LOGIN"), Event(kind="FAIL"), Event(kind="FAIL")])
    s.add(acc); s.commit()
    fails = s.scalars(acc.events.select().where(Event.kind == "FAIL")).all()
    print(len(fails))   # 2
```

## `DynamicMapped` { #dynamicmapped }

```python
from sqlalchemy.orm import DynamicMapped
```

পুরোনো (legacy) "dynamic" রিলেশনশিপের টাইপ (`lazy="dynamic"`)। কালেকশন অ্যাক্সেস করলে legacy `Query` পাওয়া যায়। async-এ চলে না। নতুন কোডে `WriteOnlyMapped` ব্যবহার করুন।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    events: DynamicMapped["Event"] = relationship()

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))

Base.metadata.create_all(engine)
with Session(engine) as s:
    acc = Account(id=1); acc.events.append(Event()); s.add(acc); s.commit()
    print(acc.events.count())   # 1 — legacy Query
```

## `declared_attr` { #declared-attr }

```python
from sqlalchemy.orm import declared_attr
```

mixin-এ এমন অ্যাট্রিবিউট লেখার ডেকোরেটর, যা **প্রতিটি মডেলের জন্য আলাদা করে** তৈরি হতে হয়: `ForeignKey`-যুক্ত কলাম, `relationship()`, বা ক্লাসের নাম থেকে বানানো `__tablename__`। ফাংশনটি প্রতিটি সাবক্লাসের জন্য একবার চলে, `cls` হিসেবে সেই সাবক্লাস পায়।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)

class TenantMixin:
    @declared_attr
    def tenant_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("tenants.id"))

    @declared_attr
    def tenant(cls) -> Mapped["Tenant"]:
        return relationship()

class Invoice(TenantMixin, Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(primary_key=True)

class Order(TenantMixin, Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)

print(Invoice.__table__.c.tenant_id is not Order.__table__.c.tenant_id)   # True — আলাদা কলাম
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #declared-attr-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cascading`](#declared-attr-cascading) | প্রপার্টি | inheritance-এর প্রতিটি স্তরে (সাবক্লাসের সাবক্লাসেও) ফাংশনটি আবার চালায়। |
| [`directive`](#declared-attr-directive) | প্রপার্টি | `__tablename__`, `__table_args__`, `__mapper_args__`-এর মতো "নির্দেশনা" (directive) mixin-এ ফাংশন দিয়ে বানানোর জন্য। |

### `declared_attr.cascading` { #declared-attr-cascading }

**ধরন:** প্রপার্টি

inheritance-এর প্রতিটি স্তরে (সাবক্লাসের সাবক্লাসেও) ফাংশনটি আবার চালায়। সাধারণ `declared_attr` শুধু প্রথম ম্যাপ হওয়া ক্লাসে চলে; inheritance চেইনের প্রতিটি টেবিলে আলাদা কলাম চাইলে এটি।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class HasIdMixin:
    @declared_attr.cascading
    def id(cls) -> Mapped[int]:
        if cls.__name__ == "Person":
            return mapped_column(Integer, primary_key=True)
        return mapped_column(ForeignKey("person.id"), primary_key=True)

class Person(HasIdMixin, Base):
    __tablename__ = "person"
    kind: Mapped[str]
    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "person"}

class Engineer(Person):
    __tablename__ = "engineer"
    __mapper_args__ = {"polymorphic_identity": "engineer"}

print([fk.target_fullname for fk in Engineer.__table__.c.id.foreign_keys])   # ['person.id']
```

### `declared_attr.directive` { #declared-attr-directive }

**ধরন:** প্রপার্টি

`__tablename__`, `__table_args__`, `__mapper_args__`-এর মতো "নির্দেশনা" (directive) mixin-এ ফাংশন দিয়ে বানানোর জন্য। টাইপ চেকারকে বলে দেয় এটা ম্যাপ করা কলাম নয়।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class AutoName:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

class Product(AutoName, Base):
    id: Mapped[int] = mapped_column(primary_key=True)

print(Product.__table__.name)   # products
```

## `mapped_column()` { #mapped-column }

```python
from sqlalchemy.orm import mapped_column
```

```python
mapped_column(*args, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, nullable=<SchemaConst.NULL_UNSPECIFIED: 3>, primary_key=False, deferred=_NoArg.NO_ARG, deferred_group=None, deferred_raiseload=None, use_existing_column=False, name=None, type_=None, autoincrement='auto', doc=None, key=None, index=None, unique=None, info=None, onupdate=None, insert_default=_NoArg.NO_ARG, server_default=None, server_onupdate=None, active_history=False, quote=None, system=False, comment=None, sort_order=_NoArg.NO_ARG, dataclass_metadata=_NoArg.NO_ARG, **kw)
```

**ধরন:** ফাংশন

Declarative মডেলে একটি কলাম ঘোষণা করে। `Mapped[...]` টাইপ থেকে SQL টাইপ আর NULL-যোগ্যতা নিজেই বোঝে, তাই প্রায়ই শুধু `mapped_column(primary_key=True)` বা `mapped_column(String(50))` যথেষ্ট। প্রথম দুটি **পজিশনাল** আর্গুমেন্ট হতে পারে ডেটাবেসের কলামের নাম আর SQL টাইপ: `mapped_column("usr_name", String(50))`। এর পরে পজিশনালভাবে `ForeignKey(...)`, `Identity()`, `CheckConstraint(...)` ইত্যাদি দেওয়া যায় (`args`)।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column("product_code", String(20), unique=True, comment="SKU কোড")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

print(CreateTable(Product.__table__).compile(dialect=postgresql.dialect()))
# CREATE TABLE products (
#     id SERIAL NOT NULL,
#     product_code VARCHAR(20) NOT NULL,
#     price NUMERIC(10, 2) DEFAULT '0' NOT NULL,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
#     PRIMARY KEY (id), UNIQUE (product_code)
# )
```

### `mapped_column()`-এর সব প্যারামিটার { #mapped-column-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | পজিশনাল স্কিমা আইটেম: `ForeignKey("users.id")`, `Identity()`, `Sequence(...)`, `CheckConstraint(...)`, `Computed(...)`। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | দুই কাজ: INSERT-এ মান না দিলে Python-side ডিফল্ট (`Column.default`), আর dataclass মডেলে `__init__`-এর ডিফল্ট। স্থির মান, ফাংশন বা SQL এক্সপ্রেশন হতে পারে। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `nullable` | NULL চলবে কি না। না দিলে টাইপ হিন্ট থেকে অনুমান: `Mapped[X \| None]` = `True`, নইলে `False`। দিলে সেটাই চূড়ান্ত। |
| `primary_key` | এই কলাম primary key (বা তার অংশ)। একাধিক কলামে দিলে composite primary key। |
| `deferred` | `True` দিলে সাধারণ SELECT-এ কলামটি আসে না; প্রথমবার পড়লে আলাদা কুয়েরিতে আসে (async-এ আগে `undefer()` দিন)। |
| `deferred_group` | একই নামের group-এর deferred কলামগুলো একসাথে এক কুয়েরিতে লোড হয়। |
| `deferred_raiseload` | deferred কলাম লোড না করে পড়লে লুকিয়ে SELECT না চালিয়ে এরর দেয়। |
| `use_existing_column` | single-table inheritance-এ: সুপারক্লাসের টেবিলে একই নামের কলাম থাকলে নতুন না বানিয়ে সেটাই ব্যবহার করে। |
| `name` | ডেটাবেসে কলামের নাম, যদি Python অ্যাট্রিবিউটের নাম থেকে আলাদা হয় (পজিশনাল প্রথম আর্গুমেন্টের keyword রূপ)। |
| `type_` | SQL টাইপ (পজিশনাল দ্বিতীয় আর্গুমেন্টের keyword রূপ), যেমন `type_=String(50)`। |
| `autoincrement` | ইন্টিজার primary key-তে ডেটাবেস নিজে মান বাড়াবে কি না (`True`, `False`, `"auto"`, `"ignore_fk"`)। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |
| `key` | Core `Table.c`-তে কলামটি কোন নামে পাওয়া যাবে (বিরল ব্যবহার)। |
| `index` | `True` দিলে কলামে একটি ইনডেক্স তৈরি হয়। |
| `unique` | `True` দিলে UNIQUE কনস্ট্রেইন্ট; একই মান দুবার ঢোকানো যাবে না। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `onupdate` | ORM বা `update()` দিয়ে রো আপডেট হলে Python-side যে মান বসবে, যেমন `func.now()`। |
| `insert_default` | শুধু INSERT-এর Python-side ডিফল্ট (`Column.default`)। dataclass মডেলে `default`-এর বদলে এটি দিলে `__init__`-এর ডিফল্টে প্রভাব পড়ে না। |
| `server_default` | টেবিল তৈরির SQL-এ `DEFAULT ...` বসায়; মান বসায় ডেটাবেস নিজে (স্ট্রিং, `text()` বা `func.now()`)। |
| `server_onupdate` | ডেটাবেস (ট্রিগার ইত্যাদি) UPDATE-এ মান বদলায়, তা ORM-কে জানায় (`FetchedValue()`), যাতে পরে আবার পড়ে আনে। |
| `active_history` | মান বদলানোর সময় আগের মানটি লোড না থাকলে তা আগে লোড করে, যাতে history/event-এ পুরোনো মান পাওয়া যায়। |
| `quote` | SQL-এ কলামের নাম জোর করে উদ্ধৃতিচিহ্নে (`"Name"`) লেখা হবে কি না। |
| `system` | ডেটাবেসের নিজস্ব সিস্টেম কলাম (যেমন PostgreSQL-এর `xmin`) বোঝায়; `CREATE TABLE`-এ লেখা হয় না। |
| `comment` | ডেটাবেসে কলামের মন্তব্য (`COMMENT ON COLUMN`)। |
| `sort_order` | ORM যখন টেবিল বানায়, কলামগুলো কোন ক্রমে বসবে (ছোট সংখ্যা আগে)। mixin-এর কলাম শুরুতে বা শেষে রাখতে কাজে লাগে। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |
| `kw` | বাকি যেকোনো keyword সরাসরি ভেতরের Core `Column`-এ যায় (যেমন ডায়ালেক্ট-নির্দিষ্ট অপশন)। |

**উদাহরণ: deferred, default, onupdate ও dataclass প্যারামিটার একসাথে**

```python
class Base(MappedAsDataclass, DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(200), index=True)
    body: Mapped[str] = mapped_column(Text, deferred=True, deferred_group="text", default="")
    status: Mapped[str] = mapped_column(String(10), default="draft")
    secret: Mapped[str] = mapped_column(String(50), default="x", repr=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None, onupdate=func.now())

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Article("প্রথম লেখা", body="অনেক বড় লেখা ...")); s.commit()
with Session(engine) as s:
    a = s.scalars(select(Article)).one()
    print(a.title, a.status)               # প্রথম লেখা draft
    print("body" in inspect(a).unloaded)   # True — deferred, এখনো লোড হয়নি
    a.status = "published"; s.commit()
    print(a.updated_at is not None)        # True — onupdate বসেছে
```

## `relationship()` { #relationship }

```python
from sqlalchemy.orm import relationship
```

```python
relationship(argument=None, secondary=None, *, uselist=None, collection_class=None, primaryjoin=None, secondaryjoin=None, back_populates=None, order_by=False, backref=None, overlaps=None, post_update=False, cascade='save-update, merge', viewonly=False, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, lazy='select', passive_deletes=False, passive_updates=True, active_history=False, enable_typechecks=True, foreign_keys=None, remote_side=None, join_depth=None, comparator_factory=None, single_parent=False, innerjoin=False, distinct_target_key=None, load_on_pending=False, query_class=None, info=None, omit_join=None, sync_backref=None, dataclass_metadata=_NoArg.NO_ARG, **kw)
```

**ধরন:** ফাংশন

দুটি মডেলের মধ্যে Python-লেভেলের সম্পর্ক ঘোষণা করে (`user.addresses`, `address.user`)। এটি কোনো কলাম বানায় না; ডেটাবেসের সম্পর্ক আসে `ForeignKey` থেকে। `Mapped[list["X"]]` দিলে কালেকশন, `Mapped["X"]` দিলে একটি অবজেক্ট। প্রথম আর্গুমেন্ট (`argument`) সাধারণত দিতে হয় না, টাইপ হিন্ট থেকেই লক্ষ্য মডেল বোঝা যায়। ধারণাগুলো সহজ ভাষায়: [Relationship অধ্যায়](../relationships.md)।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", order_by="Address.email", lazy="selectin")

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(User(name="রহিম", addresses=[Address(email="z@x.com"), Address(email="a@x.com")]))
    s.commit()
with Session(engine) as s:
    u = s.scalars(select(User)).one()
    print([a.email for a in u.addresses])   # ['a@x.com', 'z@x.com'] — order_by অনুযায়ী
```

### `relationship()`-এর সব প্যারামিটার { #relationship-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `argument` | লক্ষ্য মডেল: ক্লাস, তার নাম (স্ট্রিং `"Address"`), বা ক্লাস ফেরত দেয় এমন lambda। টাইপ হিন্ট থাকলে সাধারণত দরকার নেই। |
| `secondary` | many-to-many-এর মধ্যবর্তী (association) টেবিল: `Table` অবজেক্ট বা তার নাম। |
| `uselist` | `False` দিলে কালেকশনের বদলে একটি অবজেক্ট (one-to-one)। `Mapped["X"]` টাইপ দিলে নিজেই বোঝা যায়। |
| `collection_class` | কালেকশনের ধরন: ডিফল্ট `list`; `set` দেওয়া যায়, বা `attribute_keyed_dict("key")` দিয়ে dict। |
| `primaryjoin` | join-এর শর্ত নিজে লিখে দেওয়া (ফরেন কি থেকে অনুমান করা না গেলে বা অতিরিক্ত ফিল্টার লাগলে), যেমন `"and_(User.id == Address.user_id, Address.active == True)"`। |
| `secondaryjoin` | many-to-many-এ মধ্যবর্তী টেবিল থেকে লক্ষ্য টেবিলের join-শর্ত (self-referential N:M-এ দরকার)। |
| `back_populates` | অপর দিকের রিলেশনশিপের নাম; দুদিক মেমরিতে একসাথে সিঙ্ক থাকে। দুই মডেলেই লিখতে হয়। |
| `order_by` | কালেকশন লোড হলে কোন ক্রমে সাজানো থাকবে (কলাম, স্ট্রিং বা তালিকা)। |
| `backref` | (পুরোনো ধাঁচ) শুধু এক দিকে লিখে অপর দিকের রিলেশনশিপ নিজে থেকে বানানো। টাইপ চেকার সেটা দেখতে পায় না; নতুন কোডে `back_populates`। |
| `overlaps` | দুটি রিলেশনশিপ একই ফরেন কি কলামে লিখতে পারে জেনেও ইচ্ছাকৃত হলে, সতর্কবার্তা বন্ধ করতে সেই অন্য রিলেশনশিপের নাম(গুলো)। |
| `post_update` | চক্রাকার নির্ভরতা (A → B আর B → A) থাকলে ফরেন কি মান INSERT-এর পরে আলাদা UPDATE দিয়ে বসায়। |
| `cascade` | প্যারেন্টের ওপর সেশন-কাজ চাইল্ডে কীভাবে ছড়াবে: ডিফল্ট `"save-update, merge"`; মালিকানাধীন চাইল্ডে `"all, delete-orphan"`। বিস্তারিত [§15.2](../relationships.md#s15-2)। |
| `viewonly` | `True` দিলে শুধু পড়ার জন্য; এই রিলেশনশিপ দিয়ে কখনো ডেটাবেসে কিছু লেখা হয় না (জটিল `primaryjoin`-এ প্রচলিত)। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান (স্কেলার রিলেশনশিপে সাধারণত `None`)। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `lazy` | ডিফল্ট লোডিং কৌশল: `"select"` (ডিফল্ট, প্রথম অ্যাক্সেসে), `"joined"`, `"selectin"`, `"subquery"`, `"immediate"`, `"raise"`, `"raise_on_sql"`, `"noload"`, `"write_only"`, `"dynamic"`। async-এ `"raise"` বা `"selectin"`। তুলনা [§16.1](../relationships.md#s16-1)। |
| `passive_deletes` | `True` দিলে প্যারেন্ট মোছার সময় লোড না হওয়া চাইল্ড লোড করে না, ডেটাবেসের `ON DELETE CASCADE`-এর ওপর ছেড়ে দেয় (দ্রুত)। `"all"` দিলে লোড করা চাইল্ডেও FK `NULL` করে না। |
| `passive_updates` | primary key বদলালে চাইল্ডের FK আপডেট ডেটাবেসের `ON UPDATE CASCADE` করবে বলে ধরে নেয় (ডিফল্ট `True`)। যে ডেটাবেসে FK cascade নেই সেখানে `False`। |
| `active_history` | স্কেলার রিলেশনশিপ বদলানোর সময় আগের অবজেক্ট লোড না থাকলে লোড করে, যাতে history/event-এ পুরোনো মান পাওয়া যায়। |
| `enable_typechecks` | কালেকশনে ভুল ক্লাসের অবজেক্ট যোগ করলে এরর দেয় (ডিফল্ট `True`)। বন্ধ করা প্রায় কখনো উচিত নয়। |
| `foreign_keys` | একই টেবিলে একাধিক FK থাকলে এই রিলেশনশিপ কোনটা ব্যবহার করবে তা বলে দেয়, যেমন `foreign_keys=[origin_id]`। |
| `remote_side` | self-referential রিলেশনশিপে কোন কলাম "অপর" (প্যারেন্ট) দিকের, তা বলে দেয়, যেমন `remote_side=[id]`। |
| `join_depth` | self-referential রিলেশনশিপে eager loading (joined/selectin) কত স্তর গভীরে যাবে। |
| `comparator_factory` | `User.addresses.any(...)`-এর মতো তুলনা-অপারেটরের SQL নিজের মতো বানাতে কাস্টম `Comparator` ক্লাস। |
| `single_parent` | একটি চাইল্ড একসাথে একাধিক প্যারেন্টের হতে পারবে না, এমন যাচাই যোগ করে। many-to-one-এ `delete-orphan` দিলে দরকার। |
| `innerjoin` | joined eager loading-এ `LEFT OUTER JOIN`-এর বদলে `INNER JOIN` (রিলেশন সবসময় থাকলে দ্রুততর)। |
| `distinct_target_key` | subquery eager loading-এ ভেতরের কুয়েরিতে `DISTINCT` বসবে কি না (ডিফল্ট `None` = নিজে ঠিক করে)। |
| `load_on_pending` | নতুন (pending) অবজেক্টের FK সেট থাকলে flush-এর আগেই রিলেশনশিপ লোড করার চেষ্টা করে (বিরল)। |
| `query_class` | (legacy) `lazy="dynamic"` রিলেশনশিপ কোন `Query` সাবক্লাস ফেরত দেবে। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `omit_join` | selectin loading-এর একটি অপ্টিমাইজেশন (প্যারেন্ট টেবিল join বাদ দেওয়া) নিয়ন্ত্রণ; সাধারণত `None` রাখুন। |
| `sync_backref` | backref/back_populates-এর দুদিক মেমরিতে সিঙ্ক করার event চালু থাকবে কি না (`viewonly`-তে ডিফল্ট বন্ধ)। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |
| `kw` | অন্য কোনো keyword (ভবিষ্যতের/কাস্টম অপশন)। |

**উদাহরণ: self-referential ট্রি (remote_side, join_depth) আর একই টেবিলে দুটি FK (foreign_keys)**

```python
class Base(DeclarativeBase):
    pass

class Node(Base):
    __tablename__ = "nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("nodes.id"))
    parent: Mapped[Optional["Node"]] = relationship(back_populates="children", remote_side=[id])
    children: Mapped[list["Node"]] = relationship(back_populates="parent", lazy="selectin", join_depth=2)

class Transfer(Base):
    __tablename__ = "transfers"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    to_id: Mapped[int] = mapped_column(ForeignKey("nodes.id"))
    source: Mapped["Node"] = relationship(foreign_keys=[from_id])
    target: Mapped["Node"] = relationship(foreign_keys=[to_id])

Base.metadata.create_all(engine)
with Session(engine) as s:
    root = Node(name="মূল", children=[Node(name="শাখা ১"), Node(name="শাখা ২")])
    s.add(root); s.flush()
    s.add(Transfer(source=root.children[0], target=root.children[1])); s.commit()
with Session(engine) as s:
    t = s.scalars(select(Transfer)).one()
    print(t.source.name, "→", t.target.name, "| প্যারেন্ট:", t.source.parent.name)
    # শাখা ১ → শাখা ২ | প্যারেন্ট: মূল
```

**উদাহরণ: many-to-many (secondary), viewonly + primaryjoin, collection_class=set**

```python
class Base(DeclarativeBase):
    pass

post_tags = Table("post_tags", Base.metadata,
             Column("post_id", ForeignKey("posts.id"), primary_key=True),
             Column("tag_id", ForeignKey("tags.id"), primary_key=True))

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[set["Tag"]] = relationship(secondary=post_tags, collection_class=set)
    hot_tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags, viewonly=True,
        secondaryjoin="and_(Tag.id == post_tags.c.tag_id, Tag.hot == True)")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    hot: Mapped[bool] = mapped_column(default=False)

Base.metadata.create_all(engine)
with Session(engine) as s:
    p = Post(id=1, tags={Tag(name="python", hot=True), Tag(name="sql")})
    s.add(p); s.commit()
    print(sorted(t.name for t in p.tags), [t.name for t in p.hot_tags])   # ['python', 'sql'] ['python']
```

## `backref()` { #backref }

```python
from sqlalchemy.orm import backref
```

```python
backref(name, **kwargs)
```

**ধরন:** ফাংশন

(পুরোনো ধাঁচ) `relationship(..., backref=backref("name", ...))` আকারে অপর দিকের রিলেশনশিপের অপশন দেওয়ার জন্য। নতুন টাইপ-সহ কোডে দুই দিকে আলাদা `relationship()` আর `back_populates` লিখুন।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", backref=backref("addresses", order_by="Address.id"))

u = User(); a = Address(user=u)
print(u.addresses == [a])   # True — অপর দিক নিজে থেকে তৈরি
```

### `backref()`-এর সব প্যারামিটার { #backref-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | অপর দিকে যে অ্যাট্রিবিউট তৈরি হবে তার নাম। |
| `kwargs` | অপর দিকের `relationship()`-এর যেকোনো প্যারামিটার (`order_by`, `lazy`, `cascade` …)। |

## `foreign()` { #foreign }

```python
from sqlalchemy.orm import foreign
```

```python
foreign(expr)
```

**ধরন:** ফাংশন

`primaryjoin` লেখার সময় কোন কলামটি "ফরেন" (রেফার করে) দিক, তা চিহ্নিত করে। ডেটাবেসে আসল FK না থাকলেও রিলেশনশিপ বানাতে কাজে লাগে।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    logs: Mapped[list["Log"]] = relationship(
        primaryjoin=lambda: User.email == foreign(Log.user_email), viewonly=True)

class Log(Base):
    __tablename__ = "logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str]        # কোনো ForeignKey নেই

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add_all([User(id=1, email="a@x.com"), Log(user_email="a@x.com"), Log(user_email="a@x.com")]); s.commit()
    print(len(s.get(User, 1).logs))   # 2
```

### `foreign()`-এর সব প্যারামিটার { #foreign-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | যে কলাম এক্সপ্রেশনটিকে "ফরেন" হিসেবে চিহ্নিত করতে হবে। |

## `remote()` { #remote }

```python
from sqlalchemy.orm import remote
```

```python
remote(expr)
```

**ধরন:** ফাংশন

`primaryjoin`-এ কোন কলামটি রিলেশনশিপের "অপর" (remote) দিকের, তা চিহ্নিত করে। self-referential বা অস্বাভাবিক join-এ `remote_side=`-এর বিকল্প।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Folder(Base):
    __tablename__ = "folders"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str]
    descendants: Mapped[list["Folder"]] = relationship(
        primaryjoin=lambda: remote(foreign(Folder.path)).like(Folder.path.concat("/%")), viewonly=True)

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add_all([Folder(id=1, path="/a"), Folder(id=2, path="/a/b"), Folder(id=3, path="/a/b/c")]); s.commit()
    print(sorted(f.path for f in s.get(Folder, 1).descendants))   # ['/a/b', '/a/b/c']
```

### `remote()`-এর সব প্যারামিটার { #remote-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | যে কলাম এক্সপ্রেশনটিকে "remote" হিসেবে চিহ্নিত করতে হবে। |

## `dynamic_loader()` { #dynamic-loader }

```python
from sqlalchemy.orm import dynamic_loader
```

```python
dynamic_loader(argument=None, **kw)
```

**ধরন:** ফাংশন (legacy)

(legacy) `relationship(..., lazy="dynamic")`-এর সংক্ষিপ্ত রূপ। নতুন কোডে `WriteOnlyMapped` ব্যবহার করুন।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    events = dynamic_loader("Event")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))

print(Account.events.property.lazy)   # dynamic
```

### `dynamic_loader()`-এর সব প্যারামিটার { #dynamic-loader-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `argument` | লক্ষ্য মডেল (ক্লাস বা নাম)। |
| `kw` | বাকি সব `relationship()` প্যারামিটার। |

## `column_property()` { #column-property }

```python
from sqlalchemy.orm import column_property
```

```python
column_property(column, *additional_columns, group=None, deferred=False, raiseload=False, comparator_factory=None, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, active_history=False, expire_on_flush=True, info=None, doc=None, dataclass_metadata=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

একটি SQL এক্সপ্রেশনকে মডেলের অ্যাট্রিবিউট বানায়, যা প্রতিটি SELECT-এ হিসাব হয়ে আসে। যেমন পূর্ণ নাম (`first || ' ' || last`) বা সংশ্লিষ্ট রো-র সংখ্যা (correlated subquery)। শুধু পড়ার মান; সাধারণত বদলানো যায় না।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str] = mapped_column()          # ক্লাসের ভেতরে নাম পেতে mapped_column() লাগবে
    last: Mapped[str] = mapped_column()
    full_name: Mapped[str] = column_property(first + " " + last)
    address_count: Mapped[int] = column_property(
        select(func.count(Address.id)).where(Address.user_id == id).correlate_except(Address).scalar_subquery())

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(User(id=1, first="রহিম", last="খান")); s.flush()        # relationship নেই, তাই আগে ইউজার
    s.add_all([Address(user_id=1), Address(user_id=1)]); s.commit()
with Session(engine) as s:
    u = s.get(User, 1)
    print(u.full_name, u.address_count)   # রহিম খান 2
```

### `column_property()`-এর সব প্যারামিটার { #column-property-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | মূল কলাম বা SQL এক্সপ্রেশন। |
| `additional_columns` | একই অ্যাট্রিবিউটে আরও কলাম (inheritance-এ একাধিক টেবিলের একই নামের কলাম জুড়তে)। |
| `group` | deferred group-এর নাম; একই group-এর অ্যাট্রিবিউট একসাথে লোড হয়। |
| `deferred` | `True` দিলে এক্সপ্রেশনটি প্রথম অ্যাক্সেসে আলাদা কুয়েরিতে আসে (দামি হিসাবের জন্য)। |
| `raiseload` | deferred অবস্থায় লোড না করে পড়লে লুকিয়ে কুয়েরি না চালিয়ে এরর দেয়। |
| `comparator_factory` | এই অ্যাট্রিবিউটের তুলনা-অপারেটর (`==`, `<` …) কোন SQL বানাবে, তা কাস্টমাইজ করার ক্লাস। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `active_history` | মান বদলানোর সময় আগের মানটি লোড না থাকলে তা আগে লোড করে, যাতে history/event-এ পুরোনো মান পাওয়া যায়। |
| `expire_on_flush` | `True` (ডিফল্ট) হলে flush-এর পর মানটি expire হয়ে আবার হিসাব হয়; `False` দিলে মেমরির মান থাকে। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |

## `deferred()` { #deferred }

```python
from sqlalchemy.orm import deferred
```

```python
deferred(column, *additional_columns, group=None, raiseload=False, comparator_factory=None, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, active_history=False, expire_on_flush=True, info=None, doc=None, dataclass_metadata=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

`column_property(..., deferred=True)`-এর সংক্ষিপ্ত রূপ: কলাম বা এক্সপ্রেশনটি সাধারণ SELECT-এ আসে না, প্রথম অ্যাক্সেসে আলাদা কুয়েরিতে আসে। `mapped_column(deferred=True)` আধুনিক বিকল্প।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Doc(Base):
    __tablename__ = "docs"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = deferred(mapped_column(Text))

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Doc(id=1, body="বড় লেখা")); s.commit()
with Session(engine) as s:
    d = s.scalars(select(Doc)).one()
    print("body" in inspect(d).unloaded)   # True
    d2 = s.scalars(select(Doc).options(undefer(Doc.body)).execution_options(populate_existing=True)).one()
    print(d2.body)                         # বড় লেখা
```

### `deferred()`-এর সব প্যারামিটার { #deferred-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | যে কলাম বা এক্সপ্রেশন deferred হবে। |
| `additional_columns` | আরও কলাম, একই অ্যাট্রিবিউটে। |
| `group` | deferred group-এর নাম; একই group-এর অ্যাট্রিবিউট একসাথে লোড হয়। |
| `raiseload` | deferred অবস্থায় লোড না করে পড়লে লুকিয়ে কুয়েরি না চালিয়ে এরর দেয়। |
| `comparator_factory` | এই অ্যাট্রিবিউটের তুলনা-অপারেটর (`==`, `<` …) কোন SQL বানাবে, তা কাস্টমাইজ করার ক্লাস। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `active_history` | মান বদলানোর সময় আগের মানটি লোড না থাকলে তা আগে লোড করে, যাতে history/event-এ পুরোনো মান পাওয়া যায়। |
| `expire_on_flush` | `True` (ডিফল্ট) হলে flush-এর পর মানটি expire হয়ে আবার হিসাব হয়; `False` দিলে মেমরির মান থাকে। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |

## `query_expression()` { #query-expression }

```python
from sqlalchemy.orm import query_expression
```

```python
query_expression(default_expr=<sqlalchemy.sql.elements.Null object at 0x7fdd1e1b7b60>, *, repr=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, expire_on_flush=True, info=None, doc=None)
```

**ধরন:** ফাংশন

এমন অ্যাট্রিবিউট ঘোষণা করে, যার মান প্রতিটি কুয়েরিতে আলাদা SQL এক্সপ্রেশন দিয়ে ভরা যায় (`with_expression()` অপশন দিয়ে)। যেমন সার্চ র‍্যাঙ্ক বা দূরত্ব, যা কুয়েরি ভেদে বদলায়।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[int]
    price_with_vat: Mapped[Optional[int]] = query_expression()

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Product(id=1, price=100)); s.commit()
    p = s.scalars(select(Product).options(with_expression(Product.price_with_vat, Product.price * 115 // 100))).one()
    print(p.price_with_vat)   # 115
```

### `query_expression()`-এর সব প্যারামিটার { #query-expression-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `default_expr` | `with_expression()` না দিলে যে ডিফল্ট SQL এক্সপ্রেশন ব্যবহার হবে (না দিলে মান `None`)। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `expire_on_flush` | `True` (ডিফল্ট) হলে flush-এর পর মানটি expire হয়ে আবার হিসাব হয়; `False` দিলে মেমরির মান থাকে। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |

## `composite()` { #composite }

```python
from sqlalchemy.orm import composite
```

```python
composite(*attrs, group=None, deferred=False, raiseload=False, return_none_on=_NoArg.NO_ARG, comparator_factory=None, active_history=False, column_template=None, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, info=None, doc=None, dataclass_metadata=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

কয়েকটি কলামকে একটি Python অবজেক্টে (সাধারণত একটি dataclass, যেমন `Money(amount, currency)` বা `Point(x, y)`) জুড়ে একটি অ্যাট্রিবিউট বানায়। কুয়েরিতেও পুরো অবজেক্ট দিয়ে তুলনা করা যায়।

**উদাহরণ:**

```python
@dataclasses.dataclass(frozen=True)
class Point:
    x: int
    y: int

class Base(DeclarativeBase):
    pass

class Shop(Base):
    __tablename__ = "shops"
    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[Point] = composite(mapped_column("x"), mapped_column("y"))

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(Shop(id=1, location=Point(3, 4))); s.commit()
    print(s.scalars(select(Shop).where(Shop.location == Point(3, 4))).one().location)   # Point(x=3, y=4)
```

### `composite()`-এর সব প্যারামিটার { #composite-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attrs` | যে কলামগুলো জুড়ে অবজেক্ট বানানো হবে (`mapped_column()` বা বিদ্যমান কলাম অ্যাট্রিবিউট), ক্রম অনুযায়ী। প্রথম পজিশনাল আর্গুমেন্ট হিসেবে ক্লাসটিও দেওয়া যায়, নইলে টাইপ হিন্ট থেকে নেয়। |
| `group` | deferred group-এর নাম; একই group-এর অ্যাট্রিবিউট একসাথে লোড হয়। |
| `deferred` | `True` দিলে কলামগুলো প্রথম অ্যাক্সেসে লোড হয়। |
| `raiseload` | deferred অবস্থায় লোড না করে পড়লে লুকিয়ে কুয়েরি না চালিয়ে এরর দেয়। |
| `return_none_on` | (২.১-এ নতুন) একটি ফাংশন, যা কলামের মানগুলো দেখে `True` ফেরত দিলে অবজেক্ট না বানিয়ে `None` দেওয়া হয় (যেমন সব কলাম NULL হলে)। |
| `comparator_factory` | এই অ্যাট্রিবিউটের তুলনা-অপারেটর (`==`, `<` …) কোন SQL বানাবে, তা কাস্টমাইজ করার ক্লাস। |
| `active_history` | মান বদলানোর সময় আগের মানটি লোড না থাকলে তা আগে লোড করে, যাতে history/event-এ পুরোনো মান পাওয়া যায়। |
| `column_template` | (২.১-এ নতুন) `"person_%s"`-এর মতো একটি নামের টেমপ্লেট (ঠিক একটি `%s`-সহ)। composite ক্লাসটি dataclass হলে, যেসব ফিল্ডের কলাম আলাদা করে দেওয়া হয়নি সেগুলোর কলামের নাম এই টেমপ্লেট থেকে বানানো হয়। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |

## `synonym()` { #synonym }

```python
from sqlalchemy.orm import synonym
```

```python
synonym(name, *, map_column=None, descriptor=None, comparator_factory=None, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, info=None, doc=None, dataclass_metadata=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

একটি বিদ্যমান অ্যাট্রিবিউটের আরেকটি নাম বানায়। পড়া, লেখা আর কুয়েরি তিনটিতেই কাজ করে। পুরোনো নাম রেখে API বদলাতে, বা property-র সাথে ম্যাপ করা কলাম জুড়তে কাজে লাগে।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    email: Mapped[str] = synonym("email_address")

u = User(email="a@x.com")
print(u.email_address)                         # a@x.com
print(select(User.id).where(User.email == "a@x.com"))
# SELECT users.id FROM users WHERE users.email_address = :email_address_1
```

### `synonym()`-এর সব প্যারামিটার { #synonym-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | মূল অ্যাট্রিবিউটের নাম। |
| `map_column` | `True` দিলে এই নামেই (synonym-এর নামে) মূল কলামটি ম্যাপ করে, আর মূল নামটি synonym হয় (legacy ধাঁচ)। |
| `descriptor` | একটি Python descriptor (যেমন `@property`), যা অ্যাট্রিবিউট পড়া/লেখার সময় ব্যবহার হবে। |
| `comparator_factory` | এই অ্যাট্রিবিউটের তুলনা-অপারেটর (`==`, `<` …) কোন SQL বানাবে, তা কাস্টমাইজ করার ক্লাস। |
| `init` | (শুধু dataclass মডেলে) তৈরি হওয়া `__init__()`-এ এই ফিল্ড থাকবে কি না। ডেটাবেস যে মান দেবে (যেমন id) তার জন্য `init=False`। |
| `repr` | (শুধু dataclass মডেলে) `__repr__()`-এ দেখাবে কি না। পাসওয়ার্ডের মতো গোপন তথ্যে `repr=False`। |
| `default` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান। |
| `default_factory` | (শুধু dataclass মডেলে) `__init__`-এ ডিফল্ট মান বানানোর ফাংশন, যেমন `list` বা `dict` (পরিবর্তনশীল ডিফল্টের জন্য)। |
| `compare` | (শুধু dataclass মডেলে) তৈরি হওয়া `__eq__()`-এ এই ফিল্ড তুলনা হবে কি না। |
| `kw_only` | (শুধু dataclass মডেলে) `__init__`-এ এই ফিল্ড শুধু নাম দিয়ে (`name=...`) দেওয়া যাবে। |
| `hash` | (শুধু dataclass মডেলে) তৈরি হওয়া `__hash__()`-এ অন্তর্ভুক্ত হবে কি না। |
| `info` | নিজের যেকোনো মেটাডেটা রাখার dict (যেমন UI লেবেল); SQL-এ প্রভাব নেই। |
| `doc` | Python অ্যাট্রিবিউটের docstring (IDE/ডকুমেন্টেশনে দেখা যায়)। |
| `dataclass_metadata` | (শুধু dataclass মডেলে) তৈরি হওয়া dataclass field-এর `metadata`-তে যা বসবে (২.০.৪২-এ নতুন)। |

## `synonym_for()` { #synonym-for }

```python
from sqlalchemy.orm import synonym_for
```

```python
synonym_for(name, map_column=False)
```

**ধরন:** ডেকোরেটর

একটি `@property`-কে একই সাথে একটি কলামের synonym বানানোর ডেকোরেটর। পড়ার সময় property-র যুক্তি চলে, আর কুয়েরিতে মূল কলামটি ব্যবহার হয়।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    _status: Mapped[str] = mapped_column("status")

    @synonym_for("_status")
    @property
    def status(self):
        return self._status.upper()

u = User(_status="active")
print(u.status)                                          # ACTIVE
print(select(User.id).where(User.status == "active"))    # ... WHERE users.status = :status_1
```

### `synonym_for()`-এর সব প্যারামিটার { #synonym-for-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | মূল অ্যাট্রিবিউটের নাম। |
| `map_column` | `synonym()`-এর `map_column`-এর মতো। |

## `validates()` { #validates }

```python
from sqlalchemy.orm import validates
```

```python
validates(*names, include_removes=False, include_backrefs=True)
```

**ধরন:** ডেকোরেটর

মডেলের একটি মেথডকে নির্দিষ্ট অ্যাট্রিবিউটের ভ্যালিডেটর বানায়: মান সেট করার মুহূর্তে মেথডটি চলে, যা ফেরত দেয় সেটাই বসে, আর এরর তুললে মান বসে না। কালেকশনে প্রতিটি `append()`-এ চলে।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]

    @validates("email")
    def check_email(self, key, value):
        if "@" not in value:
            raise ValueError("ভুল ইমেইল")
        return value.lower()

u = User(email="Rahim@Example.COM")
print(u.email)          # rahim@example.com
try:
    u.email = "ভুল"
except ValueError as e:
    print(e)            # ভুল ইমেইল
```

### `validates()`-এর সব প্যারামিটার { #validates-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `names` | যে অ্যাট্রিবিউট(গুলো)র নাম যাচাই হবে। |
| `include_removes` | `True` দিলে কালেকশন থেকে সরানোর সময়ও মেথডটি চলে (তৃতীয় আর্গুমেন্ট `is_remove` পায়)। |
| `include_backrefs` | `False` দিলে অপর দিকের backref থেকে আসা পরিবর্তনে মেথডটি চলে না। |

## `reconstructor()` { #reconstructor }

```python
from sqlalchemy.orm import reconstructor
```

```python
reconstructor(fn)
```

**ধরন:** ডেকোরেটর

ORM যখন ডেটাবেস থেকে অবজেক্ট লোড করে, তখন `__init__()` ডাকে না। লোডের পর কিছু করতে (যেমন ক্যাশ ভ্যারিয়েবল তৈরি) একটি মেথডে এই ডেকোরেটর দিন; প্রতিটি লোডের পর সেটা চলে।

**উদাহরণ:**

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

    @reconstructor
    def init_on_load(self):
        self.cache = {}

Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add(User(id=1)); s.commit()
with Session(engine) as s:
    print(s.get(User, 1).cache)   # {}
```

### `reconstructor()`-এর সব প্যারামিটার { #reconstructor-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `fn` | লোডের পর যে মেথড চলবে। |

## `declarative_mixin()` { #declarative-mixin }

```python
from sqlalchemy.orm import declarative_mixin
```

```python
declarative_mixin()
```

**ধরন:** ডেকোরেটর (deprecated)

/// danger | বাতিলের পথে (deprecated)

২.১-এ বাতিলের পথে। এটি শুধু পুরোনো mypy প্লাগিনের জন্য ছিল, যা এখন সরানো হয়েছে। mixin ক্লাসে কোনো ডেকোরেটর লাগে না।

///

একটি ক্লাসকে "declarative mixin" হিসেবে চিহ্নিত করত। এখন সরাসরি সাধারণ ক্লাস লিখুন।

**উদাহরণ:**

```python
class TimestampMixin:               # কোনো ডেকোরেটর লাগে না
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

### `declarative_mixin()`-এর সব প্যারামিটার { #declarative-mixin-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cls` | mixin ক্লাস। |

## `declarative_base()` { #declarative-base }

```python
from sqlalchemy.orm import declarative_base
```

```python
declarative_base(*, metadata=None, mapper=None, name='Base', class_registry=None, type_annotation_map=None, constructor=<function _declarative_constructor at 0x7fdd1d6ebc40>, metaclass=<class 'sqlalchemy.orm.decl_api.DeclarativeMeta'>)
```

**ধরন:** ফাংশন (legacy)

(legacy) ১.x ধাঁচে বেস ক্লাস বানানোর ফাংশন: `Base = declarative_base()`। এখনো চলে, কিন্তু টাইপ চেকার এটি ভালো বোঝে না। নতুন কোডে `class Base(DeclarativeBase): pass` লিখুন।

**উদাহরণ:**

```python
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)

print(Item.__table__.name)   # items
```

### `declarative_base()`-এর সব প্যারামিটার { #declarative-base-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `metadata` | ব্যবহার করার `MetaData` (না দিলে নতুন তৈরি হয়)। |
| `mapper` | (internal) ক্লাস ম্যাপ করতে কোন mapper ফাংশন ব্যবহার হবে। |
| `cls` | বেস ক্লাস হিসেবে কোন ক্লাস নেওয়া হবে (ডিফল্ট `object`)। |
| `name` | তৈরি হওয়া বেস ক্লাসের নাম (ডিফল্ট `Base`)। |
| `class_registry` | ক্লাসের নাম → ক্লাসের নিজস্ব dict (স্ট্রিং রেফারেন্স খোঁজার জন্য)। |
| `type_annotation_map` | Python টাইপ → SQL টাইপের নিজস্ব ম্যাপ। |
| `constructor` | মডেলগুলোর ডিফল্ট `__init__` (না দিলে keyword-ভিত্তিক)। |
| `metaclass` | বেস ক্লাসের metaclass। |

## `as_declarative()` { #as-declarative }

```python
from sqlalchemy.orm import as_declarative
```

```python
as_declarative(**kw)
```

**ধরন:** ডেকোরেটর (legacy)

(legacy) একটি সাধারণ ক্লাসকে declarative বেস বানানোর ডেকোরেটর (`declarative_base()`-এর ডেকোরেটর রূপ)। নতুন কোডে `DeclarativeBase` সাবক্লাস করুন।

**উদাহরণ:**

```python
@as_declarative()
class Base:
    id: Mapped[int] = mapped_column(primary_key=True)

class Item(Base):
    __tablename__ = "items"

print([c.name for c in Item.__table__.c])   # ['id']
```

### `as_declarative()`-এর সব প্যারামিটার { #as-declarative-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `kw` | `declarative_base()`-এর মতো প্যারামিটার (`metadata`, `class_registry` …)। |

/// check | সংক্ষেপে মনে রাখুন

* বেস: `class Base(DeclarativeBase)`; dataclass চাইলে `MappedAsDataclass` যোগ করুন।
* কলাম: `Mapped[টাইপ] = mapped_column(...)`; NULL-যোগ্যতা টাইপ হিন্ট থেকে।
* রিলেশনশিপ: `ForeignKey` + `relationship(back_populates=...)`; বড় কালেকশনে `WriteOnlyMapped`।
* হিসাব করা মান: `column_property()`; কুয়েরি-ভেদে মান: `query_expression()` + `with_expression()`; একাধিক কলাম এক অবজেক্টে: `composite()`।
* ভ্যালিডেশন: `@validates`; লোডের পর কাজ: `@reconstructor`।
* legacy: `declarative_base()`, `as_declarative()`, `backref()`, `dynamic_loader()`; ২.১-এ deprecated: `declarative_mixin`।

///
