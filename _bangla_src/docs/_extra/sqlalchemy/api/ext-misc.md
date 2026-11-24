# আরও এক্সটেনশন: automap, compiler, DeferredReflection, sharding, serializer, baked { #api-ext-misc }

/// note | এই পেজে যা আছে

* **automap** (`sqlalchemy.ext.automap`): বিদ্যমান ডেটাবেস থেকে নিজে থেকে মডেল-ক্লাস বানানো; `automap_base()`, `AutomapBase`, আর নামকরণ-ফাংশনগুলো।
* **declarative এক্সটেনশন** (`sqlalchemy.ext.declarative`): `DeferredReflection`, `ConcreteBase`, `AbstractConcreteBase`, `has_inherited_table()`, `DeclarativeMeta`।
* **compiler** (`sqlalchemy.ext.compiler`): নিজের SQL কনস্ট্রাক্ট বা ডেটাবেস-ভেদে ভিন্ন SQL: `@compiles`, `deregister()`।
* **horizontal sharding**: `ShardedSession`, `ShardedQuery`, `set_shard_id`।
* **serializer**: কুয়েরি pickle করা: `dumps()`, `loads()`, `Serializer`, `Deserializer`।
* **baked** (পুরোনো): `bakery()`, `BakedQuery`, `Bakery`, `Result`।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

PostgreSQL 16-এ দুটি টেবিল আগে থেকে আছে (কোনো Python মডেল নেই):

```sql
CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(50));
CREATE TABLE addresses (id SERIAL PRIMARY KEY, city VARCHAR(50), user_id INT REFERENCES users(id));
-- ডেটা: রহিম (ঢাকা), করিম
```

///

## automap { #automap-base-group }

## `automap_base()` { #automap-base }

```python
from sqlalchemy.ext.automap import automap_base
```

```python
automap_base(declarative_base=None, **kw)
```

**ধরন:** ফাংশন

একটি বিশেষ declarative Base বানায়; `prepare(autoload_with=engine)` ডাকলে ডেটাবেসের প্রতিটি টেবিলের জন্য একটি মডেল-ক্লাস, আর ফরেন কি থেকে **রিলেশনশিপও** নিজে থেকে তৈরি করে। পুরোনো ডেটাবেসে দ্রুত স্ক্রিপ্ট/অ্যাডমিন টুল লিখতে দারুণ; বড় অ্যাপে স্পষ্ট মডেল লেখাই ভালো। কিছু ক্লাস নিজে লিখে বাকিগুলো automap-কে দিয়ে বানানোও যায়।

**উদাহরণ:**

```python
Base = automap_base()
Base.prepare(autoload_with=engine)
User, Address = Base.classes.users, Base.classes.addresses
with Session(engine) as s:
    u = s.scalars(select(User).where(User.name == "রহিম")).one()
    print([a.city for a in u.addresses_collection])   # ['ঢাকা']   (রিলেশনশিপ নিজে থেকে তৈরি)
    print(s.get(Address, 1).users.name)               # রহিম
```

### `automap_base()`-এর সব প্যারামিটার { #automap-base-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `declarative_base` | নিজের একটি declarative Base (না দিলে নতুন তৈরি হয়)। |
| `kw` | `declarative_base()`-এর অপশন (যেমন `metadata=`)। |

## `AutomapBase` { #automapbase }

```python
from sqlalchemy.ext.automap import AutomapBase
```

`automap_base()`-এর ফলের ক্লাস। `prepare()` ডাকার পর `classes` থেকে তৈরি ক্লাসগুলো পাওয়া যায়।

**উদাহরণ:**

```python
Base = automap_base()
print(issubclass(Base, AutomapBase))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #automapbase-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`by_module`](#automapbase-by-module) | অ্যাট্রিবিউট | (২.০) মডিউল-নাম অনুযায়ী সাজানো ক্লাস (একাধিক স্কিমা থেকে একই নামের টেবিল হলে `modulename_for_table` দিয়ে আলাদা করা)। |
| [`classes`](#automapbase-classes) | অ্যাট্রিবিউট | তৈরি হওয়া সব ক্লাসের সংগ্রহ (টেবিলের নাম অনুযায়ী): `Base.classes.users`। |
| [`prepare()`](#automapbase-prepare) | ক্লাস মেথড | (ক্লাস মেথড) ডেটাবেস (বা `MetaData`) থেকে টেবিল পড়ে ক্লাস ও রিলেশনশিপ বানায়। |

### `AutomapBase.by_module` { #automapbase-by-module }

**ধরন:** অ্যাট্রিবিউট

(২.০) মডিউল-নাম অনুযায়ী সাজানো ক্লাস (একাধিক স্কিমা থেকে একই নামের টেবিল হলে `modulename_for_table` দিয়ে আলাদা করা)।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine)
print(Base.by_module.sqlalchemy.ext.automap.users is Base.classes.users)   # True  (ডিফল্ট মডিউল-নাম sqlalchemy.ext.automap)
```

### `AutomapBase.classes` { #automapbase-classes }

**ধরন:** অ্যাট্রিবিউট

তৈরি হওয়া সব ক্লাসের সংগ্রহ (টেবিলের নাম অনুযায়ী): `Base.classes.users`।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine)
print(sorted(Base.classes.keys()))   # ['addresses', 'users']
```

### `AutomapBase.prepare()` { #automapbase-prepare }

```python
AutomapBase.prepare(autoload_with=None, engine=None, reflect=False, schema=None, classname_for_table=None, modulename_for_table=None, collection_class=None, name_for_scalar_relationship=None, name_for_collection_relationship=None, generate_relationship=None, reflection_options={})
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) ডেটাবেস (বা `MetaData`) থেকে টেবিল পড়ে ক্লাস ও রিলেশনশিপ বানায়। অপশন: `autoload_with` (engine), `reflect` (পুরোনো), `schema`, আর নামকরণ বদলাতে `classname_for_table`, `name_for_scalar_relationship`, `name_for_collection_relationship`, `generate_relationship`, `modulename_for_table`, `collection_class`, `reflection_options`।

**উদাহরণ:**

```python
def pretty(base, tablename, table):
    return {"users": "User", "addresses": "Address"}.get(tablename, tablename)
Base = automap_base()
Base.prepare(autoload_with=engine, classname_for_table=pretty)
print(sorted(Base.classes.keys()))   # ['Address', 'User']
```

## `classname_for_table()` { #classname-for-table }

```python
from sqlalchemy.ext.automap import classname_for_table
```

```python
classname_for_table(base, tablename, table)
```

**ধরন:** ফাংশন

ডিফল্ট নামকরণ: টেবিলের নামই ক্লাসের নাম। নিজের ফাংশন `prepare(classname_for_table=...)`-এ দিন।

**উদাহরণ:**

```python
t = Table("orders", MetaData())
print(classname_for_table(None, "orders", t))   # orders
```

### `classname_for_table()`-এর সব প্যারামিটার { #classname-for-table-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base` | automap Base। |
| `tablename` | টেবিলের নাম। |
| `table` | `Table` অবজেক্ট। |

## `name_for_scalar_relationship()` { #name-for-scalar-relationship }

```python
from sqlalchemy.ext.automap import name_for_scalar_relationship
```

```python
name_for_scalar_relationship(base, local_cls, referred_cls, constraint)
```

**ধরন:** ফাংশন

ডিফল্ট নামকরণ: many-to-one রিলেশনশিপের নাম = লক্ষ্য ক্লাসের নাম ছোট হাতে (`address.users`)।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine)
A, U = Base.classes.addresses, Base.classes.users
fk = next(iter(A.__table__.foreign_key_constraints))
print(name_for_scalar_relationship(Base, A, U, fk))   # users
```

### `name_for_scalar_relationship()`-এর সব প্যারামিটার { #name-for-scalar-relationship-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base` | automap Base। |
| `local_cls` | যে ক্লাসে রিলেশনশিপ। |
| `referred_cls` | লক্ষ্য ক্লাস। |
| `constraint` | সংশ্লিষ্ট ফরেন কি। |

## `name_for_collection_relationship()` { #name-for-collection-relationship }

```python
from sqlalchemy.ext.automap import name_for_collection_relationship
```

```python
name_for_collection_relationship(base, local_cls, referred_cls, constraint)
```

**ধরন:** ফাংশন

ডিফল্ট নামকরণ: one-to-many কালেকশনের নাম = লক্ষ্য ক্লাস ছোট হাতে + `_collection` (`user.addresses_collection`)। সুন্দর নাম (`user.addresses`) চাইলে নিজের ফাংশন দিন।

**উদাহরণ:**

```python
def plural(base, local_cls, referred_cls, constraint):
    return referred_cls.__name__.lower()          # addresses_collection → addresses
Base = automap_base(); Base.prepare(autoload_with=engine, name_for_collection_relationship=plural)
Base.registry.configure()                        # backref-দিকের অ্যাট্রিবিউট configure-এর সময় তৈরি হয়
print(hasattr(Base.classes.users, "addresses"))   # True
```

### `name_for_collection_relationship()`-এর সব প্যারামিটার { #name-for-collection-relationship-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base` | automap Base। |
| `local_cls` | যে ক্লাসে কালেকশন। |
| `referred_cls` | লক্ষ্য ক্লাস। |
| `constraint` | সংশ্লিষ্ট ফরেন কি। |

## `generate_relationship()` { #generate-relationship }

```python
from sqlalchemy.ext.automap import generate_relationship
```

```python
generate_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw)
```

**ধরন:** ফাংশন

ডিফল্ট ফাংশন যা আসলে `relationship()` / `backref()` বানায়। নিজের ফাংশনে মুড়ে অপশন বদলানো যায় (যেমন সব রিলেশনশিপে `lazy="selectin"` বা `cascade`)।

**উদাহরণ:**

```python
def eager(base, direction, return_fn, attrname, local_cls, referred_cls, **kw):
    kw["lazy"] = "selectin"
    return generate_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw)
Base = automap_base(); Base.prepare(autoload_with=engine, generate_relationship=eager)
Base.registry.configure()
print(Base.classes.users.addresses_collection.property.lazy)   # selectin
```

### `generate_relationship()`-এর সব প্যারামিটার { #generate-relationship-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base` | automap Base। |
| `direction` | রিলেশনশিপের দিক (`ONETOMANY`, `MANYTOONE`, `MANYTOMANY`)। |
| `return_fn` | `relationship` বা `backref` ফাংশন। |
| `attrname` | অ্যাট্রিবিউটের নাম। |
| `local_cls` | যে ক্লাসে। |
| `referred_cls` | লক্ষ্য ক্লাস। |
| `kw` | `relationship()`-এর অপশন। |

## declarative এক্সটেনশন { #deferredreflection-group }

## `DeferredReflection` { #deferredreflection }

```python
from sqlalchemy.ext.declarative import DeferredReflection
```

মডেল-ক্লাস আগে লিখে রাখুন (শুধু টেবিলের নাম আর দরকারি অংশ), কলাম পরে ডেটাবেস থেকে পড়া হবে: `prepare(engine)` ডাকার পর। engine অ্যাপ চালুর সময় তৈরি হলে (কনফিগ থেকে) কাজে লাগে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Reflected(DeferredReflection):
    __abstract__ = True
class User(Reflected, Base):
    __tablename__ = "users"
Reflected.prepare(engine)
print([c.name for c in User.__table__.c])   # ['id', 'name']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #deferredreflection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`prepare()`](#deferredreflection-prepare) | ক্লাস মেথড | (ক্লাস মেথড) সব সাবক্লাসের টেবিল ডেটাবেস থেকে পড়ে ম্যাপিং সম্পূর্ণ করে। |

### `DeferredReflection.prepare()` { #deferredreflection-prepare }

```python
DeferredReflection.prepare(bind, **reflect_kw)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) সব সাবক্লাসের টেবিল ডেটাবেস থেকে পড়ে ম্যাপিং সম্পূর্ণ করে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class R(DeferredReflection):
    __abstract__ = True
class Address(R, Base):
    __tablename__ = "addresses"
R.prepare(engine)
with Session(engine) as s:
    print(s.scalar(select(Address.city)))   # ঢাকা
```

## `ConcreteBase` { #concretebase }

```python
from sqlalchemy.ext.declarative import ConcreteBase
```

**concrete table inheritance**-এর মিক্সিন: প্রতিটি ক্লাসের সম্পূর্ণ আলাদা টেবিল (কোনো যৌথ টেবিল নেই), আর বেস ক্লাস কুয়েরি করলে সব টেবিল `UNION ALL` হয়ে আসে। বেস ক্লাসের নিজের টেবিলও থাকে। নিজস্ব কোনো সদস্য নেই।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Employee(ConcreteBase, Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    __mapper_args__ = {"polymorphic_identity": "employee", "concrete": True}
class Engineer(Employee):
    __tablename__ = "engineer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lang: Mapped[str]
    __mapper_args__ = {"polymorphic_identity": "engineer", "concrete": True}
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add_all([Employee(id=1, name="ক"), Engineer(id=2, name="খ", lang="Go")]); s.commit()
    print(sorted(type(e).__name__ for e in s.scalars(select(Employee))))   # ['Employee', 'Engineer']
```

## `AbstractConcreteBase` { #abstractconcretebase }

```python
from sqlalchemy.ext.declarative import AbstractConcreteBase
```

`ConcreteBase`-এর মতো, কিন্তু বেস ক্লাসের **নিজের কোনো টেবিল নেই** (শুধু সাবক্লাসগুলোর)। বেস দিয়ে কুয়েরি করলে সব সাবক্লাস-টেবিলের UNION। নিজস্ব কোনো সদস্য নেই।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Payment(AbstractConcreteBase, Base):
    pass
class Card(Payment):
    __tablename__ = "card_pay"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int]
    __mapper_args__ = {"polymorphic_identity": "card", "concrete": True}
class Bkash(Payment):
    __tablename__ = "bkash_pay"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[int]
    __mapper_args__ = {"polymorphic_identity": "bkash", "concrete": True}
Base.registry.configure()
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add_all([Card(id=1, amount=500), Bkash(id=2, amount=300)]); s.commit()
    print(s.scalar(select(func.sum(Payment.amount))))   # 800
```

## `has_inherited_table()` { #has-inherited-table }

```python
from sqlalchemy.ext.declarative import has_inherited_table
```

```python
has_inherited_table(*arg, **kw)
```

**ধরন:** ফাংশন

একটি ক্লাসের কোনো প্যারেন্ট ইতিমধ্যে টেবিলে ম্যাপ হয়েছে কি না। `declared_attr`-এর ভেতরে "single-table inheritance হলে `__tablename__` দিও না" ধরনের যুক্তিতে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Animal(Base):
    __tablename__ = "animals"
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str]
    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "animal"}
class Dog(Animal):
    __mapper_args__ = {"polymorphic_identity": "dog"}
print(has_inherited_table(Animal), has_inherited_table(Dog))   # False True
```

### `has_inherited_table()`-এর সব প্যারামিটার { #has-inherited-table-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `arg` | ক্লাস। |
| `kw` | (অব্যবহৃত)। |

## `DeclarativeMeta` { #declarativemeta }

```python
from sqlalchemy.ext.declarative import DeclarativeMeta
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো `declarative_base()`-এর metaclass। ২.০-এর `DeclarativeBase` metaclass ব্যবহার করে না; নতুন কোডে দরকার নেই।

**উদাহরণ:**

```python
from sqlalchemy.orm import declarative_base
print(type(declarative_base()).__name__)   # DeclarativeMeta
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #declarativemeta-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`mro()`](#declarativemeta-mro) | মেথড (internal) | Python `type.mro()` (metaclass হিসেবে উত্তরাধিকার-ক্রম)। |

### `DeclarativeMeta.mro()` { #declarativemeta-mro }

```python
DeclarativeMeta.mro()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

Python `type.mro()` (metaclass হিসেবে উত্তরাধিকার-ক্রম)।

## compiler এক্সটেনশন { #compiles-group }

## `compiles()` { #compiles }

```python
from sqlalchemy.ext.compiler import compiles
```

```python
compiles(class_, *specs)
```

**ধরন:** ফাংশন

ডেকোরেটর: একটি SQL কনস্ট্রাক্ট (নিজের বানানো বা বিদ্যমান) কীভাবে SQL-এ কম্পাইল হবে তা ঠিক করে, ঐচ্ছিকভাবে নির্দিষ্ট ডায়ালেক্টের জন্য। নিজের SQL ফাংশন, ডেটাবেস-ভেদে ভিন্ন SQL, বা বিদ্যমান কনস্ট্রাক্টের আউটপুট বদলাতে।

**উদাহরণ:**

```python
from sqlalchemy import DateTime

class utcnow(FunctionElement):
    inherit_cache = True
    type = DateTime()

@compiles(utcnow, "postgresql")
def _pg(element, compiler, **kw):
    return "(now() AT TIME ZONE 'utc')"

@compiles(utcnow, "sqlite")
def _sqlite(element, compiler, **kw):
    return "datetime('now')"

print(select(utcnow()).compile(dialect=postgresql.dialect()))   # SELECT (now() AT TIME ZONE 'utc') AS anon_1
print(select(utcnow()).compile(dialect=sqlite.dialect()))       # SELECT datetime('now') AS anon_1
```

### `compiles()`-এর সব প্যারামিটার { #compiles-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `class_` | যে কনস্ট্রাক্ট-ক্লাসের কম্পাইল-নিয়ম। |
| `specs` | ডায়ালেক্টের নাম(গুলো); না দিলে সব ডায়ালেক্টের ডিফল্ট। |

## `deregister()` { #deregister }

```python
from sqlalchemy.ext.compiler import deregister
```

```python
deregister(class_)
```

**ধরন:** ফাংশন

`@compiles` দিয়ে বসানো নিজের নিয়ম সরিয়ে আগের আচরণে ফেরায় (টেস্টে কাজে লাগে)।

**উদাহরণ:**

```python
class shout(ColumnClause):
    inherit_cache = True
@compiles(shout)
def _shout(element, compiler, **kw):
    return element.name.upper()
print(select(shout("hello")))   # SELECT HELLO
deregister(shout)
print(select(shout("hello")))   # SELECT hello
```

### `deregister()`-এর সব প্যারামিটার { #deregister-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `class_` | যে ক্লাসের নিয়ম সরাতে হবে। |

## Horizontal sharding { #shardedsession-group }

## `ShardedSession` { #shardedsession }

```python
from sqlalchemy.ext.horizontal_shard import ShardedSession
```

একই মডেলের ডেটা কয়েকটি ডেটাবেসে (shard) ভাগ করা থাকলে: নতুন অবজেক্ট কোন shard-এ যাবে (`shard_chooser`), primary key দিয়ে খুঁজতে কোন shard-গুলোতে দেখবে (`identity_chooser`), আর কুয়েরি কোন shard-গুলোতে চলবে (`execute_chooser`) তা আপনার ফাংশন ঠিক করে। ফল একসাথে মিলিয়ে দেয়। `Session`-এর সব মেথড আছে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str]
shards = {r: create_engine("sqlite://", poolclass=StaticPool) for r in ["bd", "in"]}
for e in shards.values():
    Base.metadata.create_all(e)
s = ShardedSession(
    shards=shards,
    shard_chooser=lambda mapper, instance, clause=None: instance.region if instance is not None else "bd",
    identity_chooser=lambda mapper, pk, *, lazy_loaded_from, execution_options, bind_arguments, **kw: ["bd", "in"],
    execute_chooser=lambda ctx: ["bd", "in"],
)
s.add_all([Order(id=1, region="bd"), Order(id=2, region="in")]); s.commit()
print(sorted(o.region for o in s.scalars(select(Order))))                     # ['bd', 'in']
print(shards["in"].connect().exec_driver_sql("SELECT count(*) FROM orders").scalar())   # 1
```

### কনস্ট্রাক্টরের প্যারামিটার { #shardedsession-params }

```python
ShardedSession(shard_chooser, identity_chooser=None, execute_chooser=None, shards=None, query_cls=ShardedQuery, *, id_chooser=None, query_chooser=None, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `shard_chooser` | `(mapper, instance, clause=None) -> shard_id`: নতুন অবজেক্ট বা স্টেটমেন্ট কোন shard-এ। |
| `identity_chooser` | primary key দিয়ে `get()`-এর সময় কোন shard-গুলোতে খুঁজবে (তালিকা)। |
| `execute_chooser` | `(ORMExecuteState) -> [shard_id, ...]`: একটি কুয়েরি কোন shard-গুলোতে চলবে। |
| `shards` | `{shard_id: engine}` dict। |
| `query_cls` | (পুরোনো Query API-র জন্য) Query ক্লাস (ডিফল্ট `ShardedQuery`)। |
| `id_chooser` | (পুরোনো) `identity_chooser`-এর আগের রূপ। |
| `query_chooser` | (পুরোনো) `execute_chooser`-এর আগের রূপ। |
| `kwargs` | `Session`-এর বাকি অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #shardedsession-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bind_shard()`](#shardedsession-bind-shard) | মেথড | একটি shard id-তে একটি engine/connection যুক্ত করে (পরে shard যোগ করতে)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ShardedSession`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Session` থেকে:** [`add()`](session.md#session-add) · [`add_all()`](session.md#session-add-all) · [`begin()`](session.md#session-begin) · [`begin_nested()`](session.md#session-begin-nested) · [`bind_mapper()`](session.md#session-bind-mapper) · [`bind_table()`](session.md#session-bind-table) · [`bulk_insert_mappings()`](session.md#session-bulk-insert-mappings) · [`bulk_save_objects()`](session.md#session-bulk-save-objects) · [`bulk_update_mappings()`](session.md#session-bulk-update-mappings) · [`close()`](session.md#session-close) · [`commit()`](session.md#session-commit) · [`connection()`](session.md#session-connection) · [`connection_callable()`](session.md#session-connection-callable) · [`delete()`](session.md#session-delete) · [`delete_all()`](session.md#session-delete-all) · [`deleted`](session.md#session-deleted) · [`dirty`](session.md#session-dirty) · [`enable_relationship_loading()`](session.md#session-enable-relationship-loading) · [`execute()`](session.md#session-execute) · [`execution_options`](session.md#session-execution-options) · [`expire()`](session.md#session-expire) · [`expire_all()`](session.md#session-expire-all) · [`expunge()`](session.md#session-expunge) · [`expunge_all()`](session.md#session-expunge-all) · [`flush()`](session.md#session-flush) · [`get()`](session.md#session-get) · [`get_bind()`](session.md#session-get-bind) · [`get_nested_transaction()`](session.md#session-get-nested-transaction) · [`get_one()`](session.md#session-get-one) · [`get_transaction()`](session.md#session-get-transaction) · [`identity_key()`](session.md#session-identity-key) · [`in_nested_transaction()`](session.md#session-in-nested-transaction) · [`in_transaction()`](session.md#session-in-transaction) · [`info`](session.md#session-info) · [`invalidate()`](session.md#session-invalidate) · [`is_active`](session.md#session-is-active) · [`is_modified()`](session.md#session-is-modified) · [`merge()`](session.md#session-merge) · [`merge_all()`](session.md#session-merge-all) · [`new`](session.md#session-new) · [`no_autoflush`](session.md#session-no-autoflush) · [`object_session()`](session.md#session-object-session) · [`prepare()`](session.md#session-prepare) · [`query()`](session.md#session-query) · [`refresh()`](session.md#session-refresh) · [`reset()`](session.md#session-reset) · [`rollback()`](session.md#session-rollback) · [`scalar()`](session.md#session-scalar) · [`scalars()`](session.md#session-scalars)

///

### `ShardedSession.bind_shard()` { #shardedsession-bind-shard }

```python
ShardedSession.bind_shard(shard_id, bind)
```

**ধরন:** মেথড

একটি shard id-তে একটি engine/connection যুক্ত করে (পরে shard যোগ করতে)।

**উদাহরণ:**

```python
s = ShardedSession(shard_chooser=lambda m, i, c=None: "x", identity_chooser=lambda *a, **k: ["x"],
                   execute_chooser=lambda ctx: ["x"])
s.bind_shard("x", create_engine("sqlite://"))
print(s.get_bind(shard_id="x").url)   # sqlite://
```

## `ShardedQuery` { #shardedquery }

```python
from sqlalchemy.ext.horizontal_shard import ShardedQuery
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

পুরোনো `session.query(...)` API-তে sharding-এর Query ক্লাস। ২.০-স্টাইলে (`select()` + `execute_chooser`) দরকার নেই; একমাত্র নিজস্ব মেথড `set_shard()` (একটি নির্দিষ্ট shard-এ কুয়েরি সীমিত করা); বাকি সব পুরোনো `Query`-এর সদস্য, যেগুলো এই রেফারেন্সে আধুনিক সমতুল্য দিয়ে ব্যাখ্যা করা (`select()`, `Session.execute()`)।

**উদাহরণ:**

```python
print(hasattr(ShardedQuery, "set_shard"))   # True
```

## `set_shard_id` { #set-shard-id }

```python
from sqlalchemy.ext.horizontal_shard import set_shard_id
```

(২.০) একটি কুয়েরিকে নির্দিষ্ট shard-এ সীমিত করার loader option: `select(Order).options(set_shard_id("bd"))`। `execute_chooser`-কে উপেক্ষা করে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    region: Mapped[str]
shards = {r: create_engine("sqlite://", poolclass=StaticPool) for r in ["bd", "in"]}
for e in shards.values():
    Base.metadata.create_all(e)
s = ShardedSession(shards=shards, shard_chooser=lambda m, i, c=None: i.region if i is not None else "bd",
                   identity_chooser=lambda *a, **k: ["bd", "in"], execute_chooser=lambda ctx: ["bd", "in"])
s.add_all([Order(id=1, region="bd"), Order(id=2, region="in")]); s.commit()
print([o.id for o in s.scalars(select(Order).options(set_shard_id("in")))])   # [2]
```

### কনস্ট্রাক্টরের প্যারামিটার { #set-shard-id-params }

```python
set_shard_id(shard_id, propagate_to_loaders=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `shard_id` | যে shard-এ কুয়েরি চলবে। |
| `propagate_to_loaders` | lazy load ইত্যাদিতেও একই shard বহাল থাকবে কি না (ডিফল্ট `True`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #set-shard-id-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get_children()`](#set-shard-id-get-children) | মেথড (internal) | ক্যাশ/traversal-এর জন্য ভেতরের child এলিমেন্ট। |
| [`propagate_to_loaders`](#set-shard-id-propagate-to-loaders) | অ্যাট্রিবিউট | পরের loader-এও প্রযোজ্য কি না। |
| [`shard_id`](#set-shard-id-shard-id) | অ্যাট্রিবিউট | নির্দিষ্ট shard id। |

### `set_shard_id.get_children()` { #set-shard-id-get-children }

```python
set_shard_id.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ/traversal-এর জন্য ভেতরের child এলিমেন্ট।

### `set_shard_id.propagate_to_loaders` { #set-shard-id-propagate-to-loaders }

**ধরন:** অ্যাট্রিবিউট

পরের loader-এও প্রযোজ্য কি না।

**উদাহরণ:**

```python
print(set_shard_id("bd").propagate_to_loaders)   # True
```

### `set_shard_id.shard_id` { #set-shard-id-shard-id }

**ধরন:** অ্যাট্রিবিউট

নির্দিষ্ট shard id।

**উদাহরণ:**

```python
print(set_shard_id("bd").shard_id)   # bd
```

## serializer { #dumps-group }

## `dumps()` { #dumps }

```python
from sqlalchemy.ext.serializer import dumps, loads
```

```python
dumps(obj, protocol=5)
```

**ধরন:** ফাংশন

একটি SQLAlchemy কুয়েরি/এক্সপ্রেশন **pickle** করে (টেবিল, কলাম, mapper-এর রেফারেন্স নাম হিসেবে রেখে), যাতে পরে অন্য প্রসেসে আবার বানানো যায় (যেমন কুয়েরি ক্যাশে রাখা)। শুধু নিজের বিশ্বস্ত ডেটায় ব্যবহার করুন (pickle-এর নিরাপত্তা-ঝুঁকি)।

**উদাহরণ:**

```python
md = MetaData(); users = Table("users", md, autoload_with=engine)
data = dumps(select(users.c.name).where(users.c.id == 2))
stmt = loads(data, md)
with engine.connect() as c:
    print(c.scalar(stmt))   # করিম
```

### `dumps()`-এর সব প্যারামিটার { #dumps-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `obj` | যে কুয়েরি/এক্সপ্রেশন। |
| `protocol` | pickle protocol (ডিফল্ট ৫)। |

## `loads()` { #loads }

```python
from sqlalchemy.ext.serializer import loads
```

```python
loads(data, metadata=None, scoped_session=None, engine=None)
```

**ধরন:** ফাংশন

`dumps()`-এর ফল থেকে কুয়েরি আবার বানায়; টেবিল/কলাম খুঁজতে একটি `MetaData` (আর দরকারে session/engine) দিন।

**উদাহরণ:**

```python
md = MetaData(); users = Table("users", md, autoload_with=engine)
print(loads(dumps(users.c.name == "রহিম"), md))   # users.name = :name_1
```

### `loads()`-এর সব প্যারামিটার { #loads-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `data` | `dumps()`-এর bytes। |
| `metadata` | টেবিল খোঁজার `MetaData`। |
| `scoped_session` | ORM কুয়েরির জন্য session। |
| `engine` | engine (bind দরকার হলে)। |

## `Serializer` { #serializer }

```python
from sqlalchemy.ext.serializer import Serializer
```

`dumps()`-এর পেছনের `pickle.Pickler` সাবক্লাস: SQLAlchemy অবজেক্টকে নাম-রেফারেন্সে বদলায় (`persistent_id`)। নিজের pickle-প্রবাহে ব্যবহার করতে।

**উদাহরণ:**

```python
import io
md = MetaData(); users = Table("users", md, autoload_with=engine)
buf = io.BytesIO(); Serializer(buf).dump(select(users.c.id))
print(len(buf.getvalue()) > 0)   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #serializer-params }

```python
Serializer(*args, **kwargs)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | `pickle.Pickler`-এর আর্গুমেন্ট (ফাইল ইত্যাদি)। |
| `kwargs` | `pickle.Pickler`-এর অপশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #serializer-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bin`](#serializer-bin) | অ্যাট্রিবিউট (internal) | pickle-এর ভেতরের ফ্ল্যাগ (বাইনারি protocol)। |
| [`clear_memo()`](#serializer-clear-memo) | মেথড (internal) | pickle-এর memo খালি করা (`pickle.Pickler`-এর মতো)। |
| [`dispatch_table`](#serializer-dispatch-table) | অ্যাট্রিবিউট (internal) | pickle-এর reduce-table। |
| [`dump()`](#serializer-dump) | মেথড | অবজেক্ট লিখে দেয় (`pickle.Pickler.dump`)। |
| [`fast`](#serializer-fast) | অ্যাট্রিবিউট (internal) | pickle-এর ভেতরের ফ্ল্যাগ। |
| [`memo`](#serializer-memo) | অ্যাট্রিবিউট (internal) | pickle-এর memo dict। |
| [`persistent_id()`](#serializer-persistent-id) | মেথড (internal) | SQLAlchemy অবজেক্টকে (Table, Column, Mapper, Session) নাম-রেফারেন্সে বদলানোর হুক। |

### `Serializer.bin` { #serializer-bin }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর ভেতরের ফ্ল্যাগ (বাইনারি protocol)।

### `Serializer.clear_memo()` { #serializer-clear-memo }

```python
Serializer.clear_memo()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর memo খালি করা (`pickle.Pickler`-এর মতো)।

### `Serializer.dispatch_table` { #serializer-dispatch-table }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর reduce-table।

### `Serializer.dump()` { #serializer-dump }

```python
Serializer.dump(obj, /)
```

**ধরন:** মেথড

অবজেক্ট লিখে দেয় (`pickle.Pickler.dump`)।

**উদাহরণ:**

```python
import io
buf = io.BytesIO(); Serializer(buf).dump(text("SELECT 1"))
print(buf.tell() > 0)   # True
```

### `Serializer.fast` { #serializer-fast }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর ভেতরের ফ্ল্যাগ।

### `Serializer.memo` { #serializer-memo }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর memo dict।

### `Serializer.persistent_id()` { #serializer-persistent-id }

```python
Serializer.persistent_id(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQLAlchemy অবজেক্টকে (Table, Column, Mapper, Session) নাম-রেফারেন্সে বদলানোর হুক।

## `Deserializer` { #deserializer }

```python
from sqlalchemy.ext.serializer import Deserializer
```

`loads()`-এর পেছনের `pickle.Unpickler` সাবক্লাস: নাম-রেফারেন্স থেকে আসল টেবিল/কলাম/mapper খুঁজে বসায়।

**উদাহরণ:**

```python
import io
md = MetaData(); users = Table("users", md, autoload_with=engine)
stmt = Deserializer(io.BytesIO(dumps(select(users.c.name))), md).load()
print(stmt)   # SELECT users.name FROM users
```

### কনস্ট্রাক্টরের প্যারামিটার { #deserializer-params }

```python
Deserializer(file, metadata=None, scoped_session=None, engine=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `file` | পড়ার ফাইল/stream। |
| `metadata` | `MetaData`। |
| `scoped_session` | session। |
| `engine` | engine। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #deserializer-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`find_class()`](#deserializer-find-class) | মেথড (internal) | pickle-এর ক্লাস খোঁজার হুক। |
| [`get_engine()`](#deserializer-get-engine) | মেথড (internal) | দেওয়া engine/session থেকে engine বের করে। |
| [`load()`](#deserializer-load) | মেথড | অবজেক্ট পড়ে দেয়। |
| [`memo`](#deserializer-memo) | অ্যাট্রিবিউট (internal) | pickle-এর memo। |
| [`persistent_load()`](#deserializer-persistent-load) | মেথড (internal) | নাম-রেফারেন্স থেকে আসল অবজেক্ট বের করার হুক। |

### `Deserializer.find_class()` { #deserializer-find-class }

```python
Deserializer.find_class(module_name, global_name, /)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর ক্লাস খোঁজার হুক।

### `Deserializer.get_engine()` { #deserializer-get-engine }

```python
Deserializer.get_engine()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

দেওয়া engine/session থেকে engine বের করে।

### `Deserializer.load()` { #deserializer-load }

```python
Deserializer.load()
```

**ধরন:** মেথড

অবজেক্ট পড়ে দেয়।

**উদাহরণ:**

```python
import io
print(Deserializer(io.BytesIO(dumps(text("SELECT 1")))).load())   # SELECT 1
```

### `Deserializer.memo` { #deserializer-memo }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pickle-এর memo।

### `Deserializer.persistent_load()` { #deserializer-persistent-load }

```python
Deserializer.persistent_load(id_)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নাম-রেফারেন্স থেকে আসল অবজেক্ট বের করার হুক।

## baked (পুরোনো) { #bakery-fn-group }

## `bakery()` { #bakery-fn }

```python
from sqlalchemy.ext import baked
```

```python
bakery(size=200)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(পুরোনো, ১.x যুগের) Query-ভিত্তিক কুয়েরি "বেক" করে ক্যাশ রাখার ব্যবস্থা। ১.৪ থেকে সব স্টেটমেন্ট নিজে থেকেই ক্যাশ হয়, তাই নতুন কোডে **দরকার নেই**; শুধু পুরোনো কোড বুঝতে। আধুনিক বিকল্প: সাধারণ `select()` (নিজেই ক্যাশ হয়) বা `lambda_stmt()`।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); User = Base.classes.users
bakery = baked.bakery()
bq = bakery(lambda s: s.query(User))
bq += lambda q: q.filter(User.name == bindparam("n"))
with Session(engine) as s:
    print(bq(s).params(n="করিম").one().id)   # 2
```

### `bakery()`-এর সব প্যারামিটার { #bakery-fn-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `size` | ক্যাশে সর্বোচ্চ কয়টি কুয়েরি। |

## `BakedQuery` { #bakedquery }

```python
from sqlalchemy.ext.baked import BakedQuery
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`bakery(...)`-এর ফল: ধাপে ধাপে (`+=`) কুয়েরি বানানোর lambda-গুচ্ছ।

**উদাহরণ:**

```python
print(isinstance(baked.bakery()(lambda s: s.query(text("1"))), BakedQuery))   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #bakedquery-params }

```python
BakedQuery(bakery, initial_fn, args=())
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bakery` | ক্যাশ (Bakery)। |
| `initial_fn` | প্রথম lambda। |
| `args` | ক্যাশ-key-এর বাড়তি অংশ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bakedquery-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_criteria()`](#bakedquery-add-criteria) | মেথড | আরেকটি lambda ধাপ যোগ (`+=`-এর মতো)। |
| [`bakery()`](#bakedquery-bakery) | ক্লাস মেথড | (ক্লাস মেথড) নতুন একটি ক্যাশ বানায়। |
| [`for_session()`](#bakedquery-for-session) | মেথড | একটি session-এর জন্য চালানোর-যোগ্য `Result` দেয় (`bq(session)`-এর মতো)। |
| [`spoil()`](#bakedquery-spoil) | মেথড | ক্যাশিং বন্ধ করা (প্রতিবার নতুন করে বানানো)। |
| [`steps`](#bakedquery-steps) | অ্যাট্রিবিউট | lambda ধাপগুলোর তালিকা। |
| [`to_query()`](#bakedquery-to-query) | মেথড | ধাপগুলো থেকে একটি সাধারণ `Query` বানায় (সাবকুয়েরি হিসেবে ব্যবহারে)। |
| [`with_criteria()`](#bakedquery-with-criteria) | মেথড | নতুন ধাপসহ একটি **কপি** দেয় (মূলটি অপরিবর্তিত)। |

### `BakedQuery.add_criteria()` { #bakedquery-add-criteria }

```python
BakedQuery.add_criteria(fn, *args)
```

**ধরন:** মেথড

আরেকটি lambda ধাপ যোগ (`+=`-এর মতো)।

**উদাহরণ:**

```python
bq = baked.bakery()(lambda s: s.query(text("1"))); bq.add_criteria(lambda q: q)
print(len(bq.steps))   # 2
```

### `BakedQuery.bakery()` { #bakedquery-bakery }

```python
BakedQuery.bakery(size=200)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) নতুন একটি ক্যাশ বানায়।

**উদাহরণ:**

```python
print(type(BakedQuery.bakery()).__name__)   # Bakery
```

### `BakedQuery.for_session()` { #bakedquery-for-session }

```python
BakedQuery.for_session(session)
```

**ধরন:** মেথড

একটি session-এর জন্য চালানোর-যোগ্য `Result` দেয় (`bq(session)`-এর মতো)।

**উদাহরণ:**

```python
bq = baked.bakery()(lambda s: s.query(text("1")))
with Session(engine) as s:
    print(type(bq.for_session(s)).__name__)   # Result
```

### `BakedQuery.spoil()` { #bakedquery-spoil }

```python
BakedQuery.spoil(full=False)
```

**ধরন:** মেথড

ক্যাশিং বন্ধ করা (প্রতিবার নতুন করে বানানো)।

**উদাহরণ:**

```python
bq = baked.bakery()(lambda s: s.query(text("1")))
print(bq.spoil() is bq)   # True
```

### `BakedQuery.steps` { #bakedquery-steps }

**ধরন:** অ্যাট্রিবিউট

lambda ধাপগুলোর তালিকা।

**উদাহরণ:**

```python
print(len(baked.bakery()(lambda s: s.query(text("1"))).steps))   # 1
```

### `BakedQuery.to_query()` { #bakedquery-to-query }

```python
BakedQuery.to_query(query_or_session)
```

**ধরন:** মেথড

ধাপগুলো থেকে একটি সাধারণ `Query` বানায় (সাবকুয়েরি হিসেবে ব্যবহারে)।

**উদাহরণ:**

```python
bq = baked.bakery()(lambda s: s.query(text("1")))
with Session(engine) as s:
    print(type(bq.to_query(s)).__name__)   # Query
```

### `BakedQuery.with_criteria()` { #bakedquery-with-criteria }

```python
BakedQuery.with_criteria(fn, *args)
```

**ধরন:** মেথড

নতুন ধাপসহ একটি **কপি** দেয় (মূলটি অপরিবর্তিত)।

**উদাহরণ:**

```python
bq = baked.bakery()(lambda s: s.query(text("1")))
print(len(bq.with_criteria(lambda q: q).steps), len(bq.steps))   # 2 1
```

## `Bakery` { #bakery }

```python
from sqlalchemy.ext.baked import Bakery
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

baked কুয়েরির ক্যাশ; ডাকলে (`bakery(fn)`) একটি `BakedQuery` দেয়।

**উদাহরণ:**

```python
print(type(baked.bakery()).__name__)   # Bakery
```

### কনস্ট্রাক্টরের প্যারামিটার { #bakery-params }

```python
Bakery(cls_, cache)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cls_` | BakedQuery ক্লাস। |
| `cache` | ক্যাশ dict। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bakery-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cache`](#bakery-cache) | অ্যাট্রিবিউট | ক্যাশ (LRU)। |
| [`cls`](#bakery-cls) | অ্যাট্রিবিউট (internal) | যে BakedQuery ক্লাস বানানো হবে। |

### `Bakery.cache` { #bakery-cache }

**ধরন:** অ্যাট্রিবিউট

ক্যাশ (LRU)।

**উদাহরণ:**

```python
print(type(baked.bakery().cache).__name__)   # LRUCache
```

### `Bakery.cls` { #bakery-cls }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে BakedQuery ক্লাস বানানো হবে।

## `Result` { #result }

```python
from sqlalchemy.ext.baked import Result
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

একটি session-এ চালানোর জন্য প্রস্তুত baked কুয়েরি: `.all()`, `.one()`, `.first()` ইত্যাদি (পুরোনো Query-র মতো)।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); User = Base.classes.users
bq = baked.bakery()(lambda s: s.query(User.name).order_by(User.id))
with Session(engine) as s:
    print([r.name for r in bq(s).all()])   # ['রহিম', 'করিম']
```

### কনস্ট্রাক্টরের প্যারামিটার { #result-ctor-params }

```python
Result(bq, session)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `bq` | BakedQuery। |
| `session` | Session। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #result-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all()`](#result-all) | মেথড | সব রো। |
| [`bq`](#result-bq) | অ্যাট্রিবিউট (internal) | মূল BakedQuery। |
| [`count()`](#result-count) | মেথড | রো-সংখ্যা। |
| [`first()`](#result-first) | মেথড | প্রথম রো বা `None`। |
| [`get()`](#result-get) | মেথড | primary key দিয়ে একটি অবজেক্ট। |
| [`one()`](#result-one) | মেথড | ঠিক একটি রো (না হলে এরর)। |
| [`one_or_none()`](#result-one-or-none) | মেথড | একটি রো বা `None`। |
| [`params()`](#result-params) | মেথড | `bindparam`-এর মান দেয়। |
| [`scalar()`](#result-scalar) | মেথড | প্রথম রো-র প্রথম কলাম। |
| [`session`](#result-session) | অ্যাট্রিবিউট (internal) | যে session-এ চলবে। |
| [`with_post_criteria()`](#result-with-post-criteria) | মেথড | ক্যাশের বাইরে, চালানোর ঠিক আগে প্রয়োগ হওয়া অপশন যোগ করে (যেমন execution options)। |

### `Result.all()` { #result-all }

```python
Result.all()
```

**ধরন:** মেথড

সব রো।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(len(baked.bakery()(lambda s: s.query(U))(s).all()))   # 2
```

### `Result.bq` { #result-bq }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল BakedQuery।

### `Result.count()` { #result-count }

```python
Result.count()
```

**ধরন:** মেথড

রো-সংখ্যা।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(U))(s).count())   # 2
```

### `Result.first()` { #result-first }

```python
Result.first()
```

**ধরন:** মেথড

প্রথম রো বা `None`।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(U.name).order_by(U.id))(s).first().name)   # রহিম
```

### `Result.get()` { #result-get }

```python
Result.get(ident)
```

**ধরন:** মেথড

primary key দিয়ে একটি অবজেক্ট।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(U))(s).get(2).name)   # করিম
```

### `Result.one()` { #result-one }

```python
Result.one()
```

**ধরন:** মেথড

ঠিক একটি রো (না হলে এরর)।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(U).filter(U.id == 1))(s).one().name)   # রহিম
```

### `Result.one_or_none()` { #result-one-or-none }

```python
Result.one_or_none()
```

**ধরন:** মেথড

একটি রো বা `None`।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(U).filter(U.id == 99))(s).one_or_none())   # None
```

### `Result.params()` { #result-params }

```python
Result.params(*args, **kw)
```

**ধরন:** মেথড

`bindparam`-এর মান দেয়।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
bq = baked.bakery()(lambda s: s.query(U).filter(U.id == bindparam("i")))
with Session(engine) as s:
    print(bq(s).params(i=1).one().name)   # রহিম
```

### `Result.scalar()` { #result-scalar }

```python
Result.scalar()
```

**ধরন:** মেথড

প্রথম রো-র প্রথম কলাম।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    print(baked.bakery()(lambda s: s.query(func.count(U.id)))(s).scalar())   # 2
```

### `Result.session` { #result-session }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে session-এ চলবে।

### `Result.with_post_criteria()` { #result-with-post-criteria }

```python
Result.with_post_criteria(fn)
```

**ধরন:** মেথড

ক্যাশের বাইরে, চালানোর ঠিক আগে প্রয়োগ হওয়া অপশন যোগ করে (যেমন execution options)।

**উদাহরণ:**

```python
Base = automap_base(); Base.prepare(autoload_with=engine); U = Base.classes.users
with Session(engine) as s:
    r = baked.bakery()(lambda s: s.query(U))(s).with_post_criteria(lambda q: q.execution_options(x=1))
    print(len(r.all()))   # 2
```

/// check | সংক্ষেপে মনে রাখুন

* বিদ্যমান ডেটাবেস থেকে নিজে থেকে মডেল: `automap_base().prepare(autoload_with=engine)`।
* মডেল আগে, কলাম পরে ডেটাবেস থেকে: `DeferredReflection`।
* নিজের SQL বা ডেটাবেস-ভেদে ভিন্ন SQL: `@compiles(MyConstruct, "postgresql")`।
* ডেটা কয়েকটি ডেটাবেসে ভাগ: `ShardedSession` (+ `set_shard_id`)।
* `baked` পুরোনো; নতুন কোডে সাধারণ `select()` নিজেই ক্যাশ হয়।

///
