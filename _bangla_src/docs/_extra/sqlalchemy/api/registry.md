# Registry ও Mapper API: ম্যাপিংয়ের ভেতরের তথ্য { #api-registry }

/// note | এই পেজে যা আছে

* `registry`: মডেলগুলোর রেজিস্ট্রি, তার সব মেথড ও কনস্ট্রাক্টর প্যারামিটার।
* `Mapper`: একটি মডেল-ক্লাস কীভাবে টেবিলে ম্যাপ হয়েছে তার পূর্ণ বিবরণ; **সব** মেথড, প্রপার্টি আর অ্যাট্রিবিউট (৮৫টি), আর কনস্ট্রাক্টরের প্যারামিটার (যেগুলো আসলে `__mapper_args__`-এর অপশন)।
* `configure_mappers()`, `clear_mappers()`, `class_mapper()`, `object_mapper()`, `mapped_as_dataclass()`, `add_mapped_attribute()`, `polymorphic_union()`।

///

সাধারণ অ্যাপে এগুলো সরাসরি খুব কম লাগে; `DeclarativeBase` সব নিজে করে। কিন্তু **মডেল নিয়ে কোড লেখার কোড** (অ্যাডমিন প্যানেল, জেনেরিক CRUD, সিরিয়ালাইজার, মাইগ্রেশন টুল) বানাতে `Mapper` অপরিহার্য: কোন মডেলে কী কলাম আর রিলেশনশিপ আছে, তা রানটাইমে এখান থেকেই জানা যায়। কোনো মডেলের `Mapper` পাওয়ার সহজ উপায়: `inspect(User)` বা `User.__mapper__`।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
import dataclasses
from sqlalchemy import ForeignKey, func, inspect
from sqlalchemy.orm import (DeclarativeBase, Mapped, column_property, composite,
                            mapped_column, relationship, synonym)

@dataclasses.dataclass
class Point:
    x: int
    y: int

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    version: Mapped[int] = mapped_column(default=1)
    upper_name: Mapped[str] = column_property(func.upper(name))
    alias: Mapped[str] = synonym("name")
    loc: Mapped[Point] = composite(mapped_column("x", default=0), mapped_column("y", default=0))
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    __mapper_args__ = {"version_id_col": version}

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")

class Employee(Base):                                   # joined-table inheritance
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "employee"}

class Engineer(Employee):
    __tablename__ = "engineers"
    id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "engineer"}

class Manager(Employee):
    __tablename__ = "managers"
    id: Mapped[int] = mapped_column(ForeignKey("employees.id"), primary_key=True)
    __mapper_args__ = {"polymorphic_identity": "manager"}

um = inspect(User)          # User-এর Mapper
```

ডেটাবেসে একজন ইউজার আছেন (id ১, নাম "রহিম", একটি ঠিকানা)। উদাহরণগুলো PostgreSQL 16-এ চালিয়ে দেখা।

///

## `registry` { #registry }

```python
from sqlalchemy.orm import registry
```

মডেল-ক্লাসগুলোর **রেজিস্টার**: কোন ক্লাস কোন টেবিলে ম্যাপ হয়েছে, স্ট্রিং নাম (`relationship("Address")`) কোন ক্লাস বোঝায়, আর সব টেবিলের `MetaData`। `DeclarativeBase` সাবক্লাস করলে একটি `registry` নিজে থেকেই তৈরি হয় (`Base.registry`)। সরাসরি `registry()` বানিয়ে ডেকোরেটর (`@reg.mapped`) বা imperative ম্যাপিংও করা যায়।

**উদাহরণ:**

```python
print(Base.registry.metadata is Base.metadata)        # True
print(sorted(m.class_.__name__ for m in Base.registry.mappers))
# ['Address', 'Employee', 'Engineer', 'Manager', 'User']
```

### কনস্ট্রাক্টরের প্যারামিটার { #registry-params }

```python
registry(*, metadata=None, class_registry=None, type_annotation_map=None, constructor=<function _declarative_constructor at 0x7fdd1d6ebc40>)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `metadata` | এই রেজিস্ট্রির টেবিলগুলো কোন `MetaData`-তে থাকবে (না দিলে নতুন তৈরি হয়)। |
| `class_registry` | ক্লাসের নাম → ক্লাসের dict, স্ট্রিং রেফারেন্স খুঁজতে। একাধিক রেজিস্ট্রি একই নাম-ভান্ডার শেয়ার করতে চাইলে দিন। |
| `type_annotation_map` | Python টাইপ → SQL টাইপের ম্যাপ, যেমন `{str: String(100)}`। |
| `constructor` | ম্যাপ করা ক্লাসগুলোর ডিফল্ট `__init__` (না দিলে keyword-ভিত্তিক কনস্ট্রাক্টর)। `None` দিলে কোনো কনস্ট্রাক্টর বসানো হয় না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #registry-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_declarative_base()`](#registry-as-declarative-base) | মেথড (legacy) | একটি সাধারণ ক্লাসকে এই রেজিস্ট্রির declarative বেস বানানোর ডেকোরেটর। |
| [`configure()`](#registry-configure) | মেথড | এই রেজিস্ট্রির এখনো "configure" না হওয়া সব mapper configure করে: রিলেশনশিপের স্ট্রিং নাম আসল ক্লাসে বদলানো, backref বানানো, join-শর্ত হিসাব। |
| [`dispose()`](#registry-dispose) | মেথড | এই রেজিস্ট্রির সব mapper মুছে ফেলে; ক্লাসগুলো আর ম্যাপ করা থাকে না। |
| [`generate_base()`](#registry-generate-base) | মেথড (legacy) | এই রেজিস্ট্রির সাথে যুক্ত একটি declarative বেস ক্লাস বানিয়ে দেয় (`declarative_base()`-এর রেজিস্ট্রি রূপ)। |
| [`map_declaratively()`](#registry-map-declaratively) | মেথড | একটি ক্লাসকে declarative নিয়মে (ক্লাসের ভেতরের `__tablename__`, কলাম পড়ে) ম্যাপ করে, ডেকোরেটর বা বেস ক্লাস ছাড়াই। |
| [`map_imperatively()`](#registry-map-imperatively) | মেথড | "imperative" (classical) ম্যাপিং: ক্লাসে কোনো ম্যাপিং-তথ্য থাকে না; আলাদা করে বানানো `Table` আর ক্লাসকে এখানে জোড়া হয়। |
| [`mapped()`](#registry-mapped) | মেথড | ক্লাস ডেকোরেটর: বেস ক্লাস ছাড়াই একটি ক্লাসকে declarative নিয়মে ম্যাপ করে। |
| [`mapped_as_dataclass()`](#registry-mapped-as-dataclass) | মেথড | ক্লাস ডেকোরেটর: ক্লাসটিকে ম্যাপ করে **এবং** dataclass বানায় (`MappedAsDataclass`-এর ডেকোরেটর রূপ)। |
| [`mappers`](#registry-mappers) | প্রপার্টি | এই রেজিস্ট্রির সব `Mapper`-এর একটি অপরিবর্তনীয় সংগ্রহ। |
| [`update_type_annotation_map()`](#registry-update-type-annotation-map) | মেথড | রেজিস্ট্রির `type_annotation_map`-এ নতুন Python টাইপ → SQL টাইপ যোগ করে; এরপর থেকে ম্যাপ হওয়া ক্লাসে প্রযোজ্য। |

### `registry.as_declarative_base()` { #registry-as-declarative-base }

```python
registry.as_declarative_base(**kw)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

একটি সাধারণ ক্লাসকে এই রেজিস্ট্রির declarative বেস বানানোর ডেকোরেটর। নতুন কোডে `DeclarativeBase` ভালো।

**উদাহরণ:**

```python
reg = registry()

@reg.as_declarative_base()
class MyBase:
    pass

class Item(MyBase):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)

print(Item.__table__.metadata is reg.metadata)   # True
```

### `registry.configure()` { #registry-configure }

```python
registry.configure(cascade=False)
```

**ধরন:** মেথড

এই রেজিস্ট্রির এখনো "configure" না হওয়া সব mapper configure করে: রিলেশনশিপের স্ট্রিং নাম আসল ক্লাসে বদলানো, backref বানানো, join-শর্ত হিসাব। প্রথম কুয়েরি বা অবজেক্ট বানানোর সময় এটা নিজেই হয়; আগেভাগে ভুল ধরতে অ্যাপ চালুর সময় ডাকতে পারেন। `cascade=True` দিলে নির্ভরশীল অন্য রেজিস্ট্রিও configure হয়।

**উদাহরণ:**

```python
Base.registry.configure()
print(um.configured)   # True
```

### `registry.dispose()` { #registry-dispose }

```python
registry.dispose(cascade=False)
```

**ধরন:** মেথড

এই রেজিস্ট্রির সব mapper মুছে ফেলে; ক্লাসগুলো আর ম্যাপ করা থাকে না। টেস্টে বারবার মডেল বানানোর সময় কাজে লাগে।

**উদাহরণ:**

```python
reg = registry()

@reg.mapped
class Temp:
    __tablename__ = "temp"
    id = Column(Integer, primary_key=True)

reg.dispose()
print(len(reg.mappers))   # 0
```

### `registry.generate_base()` { #registry-generate-base }

```python
registry.generate_base(mapper=None, name='Base', metaclass=<class 'sqlalchemy.orm.decl_api.DeclarativeMeta'>)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

এই রেজিস্ট্রির সাথে যুক্ত একটি declarative বেস ক্লাস বানিয়ে দেয় (`declarative_base()`-এর রেজিস্ট্রি রূপ)।

**উদাহরণ:**

```python
reg = registry()
MyBase = reg.generate_base()

class Item(MyBase):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)

print(Item.__mapper__.registry is reg)   # True
```

### `registry.map_declaratively()` { #registry-map-declaratively }

```python
registry.map_declaratively()
```

**ধরন:** মেথড

একটি ক্লাসকে declarative নিয়মে (ক্লাসের ভেতরের `__tablename__`, কলাম পড়ে) ম্যাপ করে, ডেকোরেটর বা বেস ক্লাস ছাড়াই। `Mapper` ফেরত দেয়।

**উদাহরণ:**

```python
reg = registry()

class Item:
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)

m = reg.map_declaratively(Item)
print(m.class_ is Item, Item.__table__.name)   # True items
```

### `registry.map_imperatively()` { #registry-map-imperatively }

```python
registry.map_imperatively(class_, local_table=None, **kw)
```

**ধরন:** মেথড

"imperative" (classical) ম্যাপিং: ক্লাসে কোনো ম্যাপিং-তথ্য থাকে না; আলাদা করে বানানো `Table` আর ক্লাসকে এখানে জোড়া হয়। পুরোনো কোড বা ডোমেইন ক্লাসকে ডেটাবেস থেকে পুরো আলাদা রাখতে চাইলে কাজে লাগে।

**উদাহরণ:**

```python
reg = registry()
items = Table("items", reg.metadata, Column("id", Integer, primary_key=True), Column("title", String(50)))

class Item:
    pass

reg.map_imperatively(Item, items)
print(select(Item.title).where(Item.id == 1))   # SELECT items.title FROM items WHERE items.id = :id_1
```

### `registry.mapped()` { #registry-mapped }

```python
registry.mapped()
```

**ধরন:** মেথড

ক্লাস ডেকোরেটর: বেস ক্লাস ছাড়াই একটি ক্লাসকে declarative নিয়মে ম্যাপ করে।

**উদাহরণ:**

```python
reg = registry()

@reg.mapped
class Item:
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)

print(Item.__mapper__.registry is reg)   # True
```

### `registry.mapped_as_dataclass()` { #registry-mapped-as-dataclass }

```python
registry.mapped_as_dataclass(*, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, eq=_NoArg.NO_ARG, order=_NoArg.NO_ARG, unsafe_hash=_NoArg.NO_ARG, match_args=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, dataclass_callable=_NoArg.NO_ARG)
```

**ধরন:** মেথড

ক্লাস ডেকোরেটর: ক্লাসটিকে ম্যাপ করে **এবং** dataclass বানায় (`MappedAsDataclass`-এর ডেকোরেটর রূপ)। `init`, `repr`, `eq`, `kw_only` ইত্যাদি অপশন দেওয়া যায়।

**উদাহরণ:**

```python
reg = registry()

@reg.mapped_as_dataclass
class Item:
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str]

print(Item("কলম"))   # Item(id=None, title='কলম')
```

### `registry.mappers` { #registry-mappers }

**ধরন:** প্রপার্টি

এই রেজিস্ট্রির সব `Mapper`-এর একটি অপরিবর্তনীয় সংগ্রহ। সব মডেলের তালিকা পেতে কাজে লাগে।

**উদাহরণ:**

```python
print(len(Base.registry.mappers))   # 5
```

### `registry.update_type_annotation_map()` { #registry-update-type-annotation-map }

```python
registry.update_type_annotation_map(type_annotation_map)
```

**ধরন:** মেথড

রেজিস্ট্রির `type_annotation_map`-এ নতুন Python টাইপ → SQL টাইপ যোগ করে; এরপর থেকে ম্যাপ হওয়া ক্লাসে প্রযোজ্য।

**উদাহরণ:**

```python
reg = registry()
reg.update_type_annotation_map({str: String(30)})

@reg.mapped
class Item:
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

print(Item.__table__.c.title.type)   # VARCHAR(30)
```

## `Mapper` { #mapper }

```python
from sqlalchemy.orm import Mapper
```

একটি ক্লাস আর একটি টেবিলের (বা অন্য selectable-এর) মধ্যে ম্যাপিংয়ের পূর্ণ বিবরণ। declarative নিজেই বানায়; সরাসরি `Mapper(...)` ডাকা হয় না। পেতে লিখুন `inspect(User)` বা `User.__mapper__`। কনস্ট্রাক্টরের প্যারামিটারগুলো আসলে মডেলের `__mapper_args__`-এ দেওয়া অপশন।

**উদাহরণ:**

```python
m = inspect(User)
print(m.class_.__name__, m.local_table.name)       # User users
print(sorted(m.columns.keys()))                     # ['id', 'name', 'upper_name', 'version', 'x', 'y']
print(list(m.relationships.keys()))                 # ['addresses']
```

### কনস্ট্রাক্টরের প্যারামিটার { #mapper-params }

```python
Mapper(class_, local_table=None, properties=None, primary_key=None, inherits=None, inherit_condition=None, inherit_foreign_keys=None, always_refresh=False, version_id_col=None, version_id_generator=None, polymorphic_on=None, polymorphic_identity=None, concrete=False, with_polymorphic=None, polymorphic_abstract=False, polymorphic_load=None, allow_partial_pks=True, batch=True, column_prefix=None, include_properties=None, exclude_properties=None, passive_updates=True, passive_deletes=False, confirm_deleted_rows=True, eager_defaults='auto', legacy_is_orphan=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `class_` | যে ক্লাস ম্যাপ হচ্ছে। |
| `local_table` | ক্লাসটি যে টেবিলে ম্যাপ হচ্ছে (single-table inheritance-এর সাবক্লাসে `None`)। |
| `properties` | অতিরিক্ত অ্যাট্রিবিউটের dict (imperative ম্যাপিংয়ে `relationship()` ইত্যাদি এখানে দেওয়া হয়)। |
| `primary_key` | টেবিলের নিজস্ব primary key-র বদলে কোন কলাম(গুলো) পরিচয় হিসেবে ধরা হবে (view বা PK-হীন টেবিলের জন্য)। |
| `inherits` | inheritance-এ প্যারেন্ট ক্লাস বা mapper (declarative নিজেই বসায়)। |
| `inherit_condition` | joined inheritance-এ প্যারেন্ট আর সন্তান টেবিলের join-শর্ত, ফরেন কি থেকে বোঝা না গেলে। |
| `inherit_foreign_keys` | `inherit_condition`-এ কোন কলামগুলো ফরেন হিসেবে ধরা হবে। |
| `always_refresh` | (legacy) প্রতিটি কুয়েরিতে মেমরির অবজেক্টের মান ডেটাবেস থেকে ওভাররাইট করে; বিকল্প `populate_existing`। |
| `version_id_col` | optimistic locking-এর ভার্সন কলাম; প্রতিটি UPDATE-এ মিলিয়ে দেখে বাড়ায় ([Concurrency](../concurrency.md#s47-4))। |
| `version_id_generator` | নতুন ভার্সন মান বানানোর ফাংশন (ডিফল্ট `+1`); ডেটাবেস নিজে মান দিলে `False`। |
| `polymorphic_on` | inheritance-এ কোন কলাম দেখে রো-টি কোন সাবক্লাসের তা বোঝা হবে (discriminator)। |
| `polymorphic_identity` | এই ক্লাসের রো-তে `polymorphic_on` কলামে যে মান থাকবে। |
| `concrete` | concrete table inheritance (প্রতিটি ক্লাসের সম্পূর্ণ আলাদা টেবিল) চালু করে। |
| `with_polymorphic` | বেস ক্লাস কুয়েরি করলে কোন সাবক্লাসের টেবিলগুলো ডিফল্টে join করে আনা হবে, যেমন `"*"`। |
| `polymorphic_abstract` | এই ক্লাসের নিজের রো কখনো থাকবে না (শুধু সাবক্লাসের), মধ্যবর্তী বেস ক্লাসে কাজে লাগে। |
| `polymorphic_load` | সাবক্লাসের কলাম কীভাবে লোড হবে: `"selectin"` (আলাদা একটি কুয়েরি) বা `"inline"` (বেস কুয়েরিতেই join)। |
| `allow_partial_pks` | composite primary key-র কিছু অংশ NULL হলেও রো-কে বৈধ অবজেক্ট হিসেবে ধরবে কি না (ডিফল্ট `True`)। |
| `batch` | একাধিক অবজেক্টের INSERT/UPDATE ব্যাচ করে পাঠাবে কি না (ডিফল্ট `True`); প্রতিটি অবজেক্টের event আলাদা চালাতে চাইলে `False`। |
| `column_prefix` | টেবিলের কলাম থেকে নিজে তৈরি হওয়া অ্যাট্রিবিউট নামের আগে উপসর্গ (যেমন `"_"`)। |
| `include_properties` | টেবিলের শুধু এই কলামগুলো ম্যাপ হবে। |
| `exclude_properties` | টেবিলের এই কলামগুলো ম্যাপ হবে না। |
| `passive_updates` | joined inheritance-এ primary key বদলালে সন্তান টেবিলের আপডেট ডেটাবেসের `ON UPDATE CASCADE`-এর ওপর ছেড়ে দেয় (ডিফল্ট `True`)। |
| `passive_deletes` | joined inheritance-এ সন্তান টেবিলের রো মোছা ডেটাবেসের `ON DELETE CASCADE`-এর ওপর ছেড়ে দেয়। |
| `confirm_deleted_rows` | DELETE-এর পর মোছা রো-সংখ্যা প্রত্যাশার সাথে না মিললে সতর্কবার্তা দেয় (ডিফল্ট `True`)। |
| `eager_defaults` | INSERT/UPDATE-এর পর ডেটাবেসে তৈরি মানগুলো সাথে সাথে আনবে কি না: `"auto"` (ডিফল্ট, INSERT-এ RETURNING থাকলে), `True`, `False`। |
| `legacy_is_orphan` | (legacy) একাধিক প্যারেন্ট থাকলে `delete-orphan` কখন প্রযোজ্য তার পুরোনো নিয়ম চালু করে। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mapper-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add_properties()`](#mapper-add-properties) | মেথড | একটি dict থেকে কয়েকটি অ্যাট্রিবিউট (কলাম/রিলেশনশিপ) একসাথে mapper-এ যোগ করে। |
| [`add_property()`](#mapper-add-property) | মেথড | mapper-এ একটি নতুন অ্যাট্রিবিউট যোগ করে (ম্যাপ হয়ে যাওয়ার পরেও)। |
| [`all_orm_descriptors`](#mapper-all-orm-descriptors) | প্রপার্টি | ক্লাসের সব ORM-সম্পর্কিত descriptor (কলাম, রিলেশনশিপ, synonym, hybrid property, association proxy) নাম অনুযায়ী। |
| [`allow_partial_pks`](#mapper-allow-partial-pks) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `allow_partial_pks` সেটিং। |
| [`allows_lambda`](#mapper-allows-lambda) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না। |
| [`always_refresh`](#mapper-always-refresh) | অ্যাট্রিবিউট (legacy) | কনস্ট্রাক্টরের `always_refresh` সেটিং। |
| [`attrs`](#mapper-attrs) | প্রপার্টি | mapper-এর সব `MapperProperty` (কলাম, রিলেশনশিপ, composite, synonym) নাম অনুযায়ী। |
| [`base_mapper`](#mapper-base-mapper) | অ্যাট্রিবিউট | inheritance চেইনের সবচেয়ে ওপরের (মূল) mapper। |
| [`batch`](#mapper-batch) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `batch` সেটিং। |
| [`c`](#mapper-c) | প্রপার্টি | `columns`-এর ছোট নাম। |
| [`cascade_iterator()`](#mapper-cascade-iterator) | মেথড | একটি অবজেক্ট থেকে শুরু করে নির্দিষ্ট cascade নিয়ম (যেমন `"delete"`, `"save-update"`) মেনে সম্পর্কিত সব অবজেক্ট ঘুরে দেয়। |
| [`class_`](#mapper-class-) | অ্যাট্রিবিউট | যে Python ক্লাস ম্যাপ হয়েছে। |
| [`class_manager`](#mapper-class-manager) | অ্যাট্রিবিউট (internal) | ক্লাসের ভেতরের instrumentation ম্যানেজার (অ্যাট্রিবিউট পর্যবেক্ষণের ব্যবস্থা)। |
| [`column_attrs`](#mapper-column-attrs) | প্রপার্টি | শুধু কলাম-ভিত্তিক অ্যাট্রিবিউট (`ColumnProperty`): সাধারণ কলাম আর `column_property()`। |
| [`column_prefix`](#mapper-column-prefix) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `column_prefix` সেটিং। |
| [`columns`](#mapper-columns) | প্রপার্টি | ম্যাপ করা সব `Column` বা SQL এক্সপ্রেশন, অ্যাট্রিবিউটের নাম অনুযায়ী। |
| [`common_parent()`](#mapper-common-parent) | মেথড | দুটি mapper-এর একই inheritance-পূর্বপুরুষ থাকলে `True`। |
| [`composites`](#mapper-composites) | প্রপার্টি | শুধু `composite()` অ্যাট্রিবিউটগুলো। |
| [`concrete`](#mapper-concrete) | অ্যাট্রিবিউট | concrete inheritance হলে `True`। |
| [`configured`](#mapper-configured) | অ্যাট্রিবিউট | mapper configure হয়ে গেছে কি না (রিলেশনশিপ ইত্যাদি চূড়ান্ত)। |
| [`confirm_deleted_rows`](#mapper-confirm-deleted-rows) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `confirm_deleted_rows` সেটিং। |
| [`eager_defaults`](#mapper-eager-defaults) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `eager_defaults` সেটিং। |
| [`entity`](#mapper-entity) | প্রপার্টি | inspection API-র অংশ: ম্যাপ করা ক্লাসটিই দেয় (`class_`-এর সমান)। |
| [`entity_namespace`](#mapper-entity-namespace) | প্রপার্টি (internal) | `filter_by()`-এ নাম দিয়ে অ্যাট্রিবিউট খোঁজার ভেতরের নাম-ভান্ডার। |
| [`exclude_properties`](#mapper-exclude-properties) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `exclude_properties` সেটিং। |
| [`extension_type`](#mapper-extension-type) | অ্যাট্রিবিউট (internal) | inspection API-র ভেতরের টাইপ-চিহ্ন (এটি কোনো এক্সটেনশনের অ্যাট্রিবিউট নয়)। |
| [`get_property()`](#mapper-get-property) | মেথড | নাম দিয়ে একটি `MapperProperty` দেয়; না থাকলে এরর। |
| [`get_property_by_column()`](#mapper-get-property-by-column) | মেথড | একটি টেবিল-কলাম দিলে কোন অ্যাট্রিবিউট সেটি ম্যাপ করে তা দেয়। |
| [`has_property()`](#mapper-has-property) | মেথড | ওই নামের অ্যাট্রিবিউট আছে কি না। |
| [`identity_key_from_instance()`](#mapper-identity-key-from-instance) | মেথড | একটি অবজেক্টের identity map key দেয়: `(ক্লাস, primary key-র tuple, identity_token)`। |
| [`identity_key_from_primary_key()`](#mapper-identity-key-from-primary-key) | মেথড | primary key-র মান দিয়ে identity key বানায় (অবজেক্ট ছাড়াই)। |
| [`identity_key_from_row()`](#mapper-identity-key-from-row) | মেথড | কুয়েরির একটি রো থেকে identity key বানায়। |
| [`include_properties`](#mapper-include-properties) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `include_properties` সেটিং (না দিলে `None`, মানে সব কলাম ম্যাপ হয়)। |
| [`inherit_cache`](#mapper-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ। |
| [`inherit_condition`](#mapper-inherit-condition) | অ্যাট্রিবিউট | joined inheritance-এ প্যারেন্ট আর এই টেবিলের join-শর্ত। |
| [`inherit_foreign_keys`](#mapper-inherit-foreign-keys) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `inherit_foreign_keys` সেটিং। |
| [`inherits`](#mapper-inherits) | অ্যাট্রিবিউট | প্যারেন্ট mapper (inheritance না থাকলে `None`)। |
| [`is_aliased_class`](#mapper-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি `aliased()` ক্লাস নয় (`False`)। |
| [`is_attribute`](#mapper-is-attribute) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি একটি অ্যাট্রিবিউট নয় (`False`)। |
| [`is_bundle`](#mapper-is-bundle) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি `Bundle` নয়। |
| [`is_clause_element`](#mapper-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি SQL এক্সপ্রেশন নয়। |
| [`is_instance`](#mapper-is-instance) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি একটি অবজেক্টের অবস্থা (`InstanceState`) নয়। |
| [`is_mapper`](#mapper-is-mapper) | অ্যাট্রিবিউট | `inspect()`-এর ফল একটি mapper কি না বুঝতে: এখানে `True`। |
| [`is_property`](#mapper-is-property) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ: এটি `MapperProperty` নয়। |
| [`is_selectable`](#mapper-is-selectable) | অ্যাট্রিবিউট (internal) | inspection-এর টাইপ-ফ্ল্যাগ। |
| [`is_sibling()`](#mapper-is-sibling) | মেথড | দুটি mapper একই প্যারেন্টের ভিন্ন শাখা (ভাইবোন) হলে `True`। |
| [`isa()`](#mapper-isa) | মেথড | এই mapper দেওয়া mapper থেকে (বা সেটাই) তৈরি হলে `True`, Python-এর `issubclass`-এর মতো। |
| [`iterate_properties`](#mapper-iterate-properties) | প্রপার্টি | সব `MapperProperty`-এর একটি iterator। |
| [`iterate_to_root()`](#mapper-iterate-to-root) | মেথড | এই mapper থেকে শুরু করে প্যারেন্ট, তার প্যারেন্ট … মূল পর্যন্ত ঘুরে দেয়। |
| [`legacy_is_orphan`](#mapper-legacy-is-orphan) | অ্যাট্রিবিউট (legacy) | কনস্ট্রাক্টরের `legacy_is_orphan` সেটিং। |
| [`local_table`](#mapper-local-table) | অ্যাট্রিবিউট | ক্লাসের নিজের টেবিল (joined inheritance-এ সন্তানের নিজের টেবিল; single inheritance-এ প্যারেন্টের টেবিল)। |
| [`logger`](#mapper-logger) | অ্যাট্রিবিউট (internal) | এই mapper-এর লগার (`sqlalchemy.orm.mapper.Mapper`)। |
| [`logging_name`](#mapper-logging-name) | অ্যাট্রিবিউট (internal) | লগে ব্যবহৃত নাম। |
| [`mapper`](#mapper-mapper) | প্রপার্টি | inspection API-র অংশ: নিজেকেই দেয়। |
| [`memoized_attribute`](#mapper-memoized-attribute) | অ্যাট্রিবিউট (internal) | ভেতরের ডেকোরেটর। |
| [`memoized_instancemethod()`](#mapper-memoized-instancemethod) | ক্লাস মেথড (internal) | ভেতরের ডেকোরেটর। |
| [`passive_deletes`](#mapper-passive-deletes) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `passive_deletes` সেটিং। |
| [`passive_updates`](#mapper-passive-updates) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `passive_updates` সেটিং। |
| [`path_string()`](#mapper-path-string) | মেথড (internal) | loader path-এর স্ট্রিং রূপে এই mapper-এর নাম। |
| [`persist_selectable`](#mapper-persist-selectable) | অ্যাট্রিবিউট | যে টেবিল/join-এ এই ক্লাসের রো লেখা হয় (joined inheritance-এ প্যারেন্ট-সন্তানের join)। |
| [`polymorphic_abstract`](#mapper-polymorphic-abstract) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `polymorphic_abstract` সেটিং। |
| [`polymorphic_identity`](#mapper-polymorphic-identity) | অ্যাট্রিবিউট | এই ক্লাসের discriminator মান। |
| [`polymorphic_iterator()`](#mapper-polymorphic-iterator) | মেথড | এই mapper আর তার সব উত্তরসূরি mapper ঘুরে দেয়। |
| [`polymorphic_load`](#mapper-polymorphic-load) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `polymorphic_load` সেটিং। |
| [`polymorphic_map`](#mapper-polymorphic-map) | অ্যাট্রিবিউট | discriminator মান → mapper-এর dict। |
| [`polymorphic_on`](#mapper-polymorphic-on) | অ্যাট্রিবিউট | discriminator কলাম (না থাকলে `None`)। |
| [`primary_base_mapper`](#mapper-primary-base-mapper) | প্রপার্টি (internal) | inheritance-এর মূল "primary" mapper (প্রায় সবসময় `base_mapper`-এর সমান)। |
| [`primary_key`](#mapper-primary-key) | অ্যাট্রিবিউট | mapper-এর দৃষ্টিতে primary key কলামগুলোর tuple। |
| [`primary_key_from_instance()`](#mapper-primary-key-from-instance) | মেথড | একটি অবজেক্টের primary key মানগুলো tuple হিসেবে দেয়। |
| [`primary_mapper()`](#mapper-primary-mapper) | মেথড (legacy) | এই ক্লাসের "primary" mapper দেয় (non-primary mapper সরানোর পর কার্যত নিজেই)। |
| [`registry`](#mapper-registry) | অ্যাট্রিবিউট | এই mapper যে `registry`-তে আছে। |
| [`relationships`](#mapper-relationships) | প্রপার্টি | শুধু রিলেশনশিপগুলো, নাম অনুযায়ী। |
| [`represents_outer_join`](#mapper-represents-outer-join) | অ্যাট্রিবিউট (internal) | inspection-এর ভেতরের ফ্ল্যাগ। |
| [`select_identity_token`](#mapper-select-identity-token) | প্রপার্টি (internal) | horizontal sharding-এ identity token বাছাইয়ের ভেতরের এক্সপ্রেশন। |
| [`selectable`](#mapper-selectable) | প্রপার্টি | এই ক্লাস কুয়েরি করলে ডিফল্টে কোন টেবিল/join থেকে SELECT হয়। |
| [`self_and_descendants`](#mapper-self-and-descendants) | প্রপার্টি | এই mapper আর তার সব উত্তরসূরির সংগ্রহ। |
| [`single`](#mapper-single) | অ্যাট্রিবিউট | single-table inheritance-এর সাবক্লাস হলে `True`। |
| [`synonyms`](#mapper-synonyms) | প্রপার্টি | শুধু `synonym()` অ্যাট্রিবিউটগুলো। |
| [`tables`](#mapper-tables) | অ্যাট্রিবিউট | এই mapper যেসব টেবিল ব্যবহার করে (joined inheritance-এ একাধিক)। |
| [`uses_inspection`](#mapper-uses-inspection) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ। |
| [`validators`](#mapper-validators) | অ্যাট্রিবিউট | `@validates` দিয়ে যুক্ত ভ্যালিডেটরগুলোর dict (অ্যাট্রিবিউটের নাম → মেথড)। |
| [`version_id_col`](#mapper-version-id-col) | অ্যাট্রিবিউট | optimistic locking-এর ভার্সন কলাম। |
| [`version_id_generator`](#mapper-version-id-generator) | অ্যাট্রিবিউট | নতুন ভার্সন মান বানানোর ফাংশন। |
| [`with_polymorphic`](#mapper-with-polymorphic) | অ্যাট্রিবিউট | কনস্ট্রাক্টরের `with_polymorphic` সেটিং (ভেতরে স্বাভাবিক রূপে)। |
| [`with_polymorphic_mappers`](#mapper-with-polymorphic-mappers) | প্রপার্টি | ডিফল্ট polymorphic লোডিংয়ে যেসব সাবক্লাস mapper join হবে তাদের তালিকা। |

### `Mapper.add_properties()` { #mapper-add-properties }

```python
Mapper.add_properties(dict_of_properties)
```

**ধরন:** মেথড

একটি dict থেকে কয়েকটি অ্যাট্রিবিউট (কলাম/রিলেশনশিপ) একসাথে mapper-এ যোগ করে।

**উদাহরণ:**

```python
reg = registry()
t = Table("items", reg.metadata, Column("id", Integer, primary_key=True), Column("title", String(20)))
class Item: pass
m = reg.map_imperatively(Item, t, exclude_properties=["title"])
m.add_properties({"heading": t.c.title})
print(select(Item.heading))   # SELECT items.title FROM items
```

### `Mapper.add_property()` { #mapper-add-property }

```python
Mapper.add_property(key, prop)
```

**ধরন:** মেথড

mapper-এ একটি নতুন অ্যাট্রিবিউট যোগ করে (ম্যাপ হয়ে যাওয়ার পরেও)। declarative-এ সাধারণত দরকার নেই; `add_mapped_attribute()` দেখুন।

**উদাহরণ:**

```python
um.add_property("name_len", column_property(func.length(User.__table__.c.name)))
print(session.get(User, 1).name_len)   # 4
```

### `Mapper.all_orm_descriptors` { #mapper-all-orm-descriptors }

**ধরন:** প্রপার্টি

ক্লাসের সব ORM-সম্পর্কিত descriptor (কলাম, রিলেশনশিপ, synonym, hybrid property, association proxy) নাম অনুযায়ী। `attrs`-এর চেয়ে বড় পরিসর, কারণ hybrid-ও আছে।

**উদাহরণ:**

```python
print(sorted(k for k in um.all_orm_descriptors.keys() if not k.startswith("_")))
# ['addresses', 'alias', 'id', 'loc', 'name', 'upper_name', 'version', 'x', 'y']
```

### `Mapper.allow_partial_pks` { #mapper-allow-partial-pks }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `allow_partial_pks` সেটিং।

**উদাহরণ:**

```python
print(um.allow_partial_pks)   # True
```

### `Mapper.allows_lambda` { #mapper-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না।

### `Mapper.always_refresh` { #mapper-always-refresh }

**ধরন:** অ্যাট্রিবিউট

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

কনস্ট্রাক্টরের `always_refresh` সেটিং।

**উদাহরণ:**

```python
print(um.always_refresh)   # False
```

### `Mapper.attrs` { #mapper-attrs }

**ধরন:** প্রপার্টি

mapper-এর সব `MapperProperty` (কলাম, রিলেশনশিপ, composite, synonym) নাম অনুযায়ী। মডেলের সব ফিল্ড ঘুরে দেখার প্রধান উপায়।

**উদাহরণ:**

```python
print(sorted(um.attrs.keys()))
# ['addresses', 'alias', 'id', 'loc', 'name', 'upper_name', 'version', 'x', 'y']
```

### `Mapper.base_mapper` { #mapper-base-mapper }

**ধরন:** অ্যাট্রিবিউট

inheritance চেইনের সবচেয়ে ওপরের (মূল) mapper। inheritance না থাকলে নিজেই।

**উদাহরণ:**

```python
print(inspect(Engineer).base_mapper.class_.__name__)   # Employee
```

### `Mapper.batch` { #mapper-batch }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `batch` সেটিং।

**উদাহরণ:**

```python
print(um.batch)   # True
```

### `Mapper.c` { #mapper-c }

**ধরন:** প্রপার্টি

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(um.c.name.name)   # name
```

### `Mapper.cascade_iterator()` { #mapper-cascade-iterator }

```python
Mapper.cascade_iterator(type_, state, halt_on=None)
```

**ধরন:** মেথড

একটি অবজেক্ট থেকে শুরু করে নির্দিষ্ট cascade নিয়ম (যেমন `"delete"`, `"save-update"`) মেনে সম্পর্কিত সব অবজেক্ট ঘুরে দেয়। "এটা মুছলে আর কী কী মুছবে" জানতে কাজে লাগে।

**উদাহরণ:**

```python
user = session.get(User, 1)
related = [obj for obj, *_ in um.cascade_iterator("delete", inspect(user))]
print([type(o).__name__ for o in related])   # ['Address']
```

### `Mapper.class_` { #mapper-class- }

**ধরন:** অ্যাট্রিবিউট

যে Python ক্লাস ম্যাপ হয়েছে।

**উদাহরণ:**

```python
print(um.class_ is User)   # True
```

### `Mapper.class_manager` { #mapper-class-manager }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসের ভেতরের instrumentation ম্যানেজার (অ্যাট্রিবিউট পর্যবেক্ষণের ব্যবস্থা)।

### `Mapper.column_attrs` { #mapper-column-attrs }

**ধরন:** প্রপার্টি

শুধু কলাম-ভিত্তিক অ্যাট্রিবিউট (`ColumnProperty`): সাধারণ কলাম আর `column_property()`।

**উদাহরণ:**

```python
print(sorted(um.column_attrs.keys()))   # ['id', 'name', 'upper_name', 'version', 'x', 'y']
```

### `Mapper.column_prefix` { #mapper-column-prefix }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `column_prefix` সেটিং।

**উদাহরণ:**

```python
print(um.column_prefix)   # None
```

### `Mapper.columns` { #mapper-columns }

**ধরন:** প্রপার্টি

ম্যাপ করা সব `Column` বা SQL এক্সপ্রেশন, অ্যাট্রিবিউটের নাম অনুযায়ী। `column_property()`-এর এক্সপ্রেশনও আছে।

**উদাহরণ:**

```python
print(um.columns.upper_name)   # upper(users.name)
```

### `Mapper.common_parent()` { #mapper-common-parent }

```python
Mapper.common_parent(other)
```

**ধরন:** মেথড

দুটি mapper-এর একই inheritance-পূর্বপুরুষ থাকলে `True`।

**উদাহরণ:**

```python
print(inspect(Engineer).common_parent(inspect(Manager)))   # True
```

### `Mapper.composites` { #mapper-composites }

**ধরন:** প্রপার্টি

শুধু `composite()` অ্যাট্রিবিউটগুলো।

**উদাহরণ:**

```python
print(list(um.composites.keys()))   # ['loc']
```

### `Mapper.concrete` { #mapper-concrete }

**ধরন:** অ্যাট্রিবিউট

concrete inheritance হলে `True`।

**উদাহরণ:**

```python
print(um.concrete)   # False
```

### `Mapper.configured` { #mapper-configured }

**ধরন:** অ্যাট্রিবিউট

mapper configure হয়ে গেছে কি না (রিলেশনশিপ ইত্যাদি চূড়ান্ত)।

**উদাহরণ:**

```python
configure_mappers()
print(um.configured)   # True
```

### `Mapper.confirm_deleted_rows` { #mapper-confirm-deleted-rows }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `confirm_deleted_rows` সেটিং।

**উদাহরণ:**

```python
print(um.confirm_deleted_rows)   # True
```

### `Mapper.eager_defaults` { #mapper-eager-defaults }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `eager_defaults` সেটিং।

**উদাহরণ:**

```python
print(um.eager_defaults)   # auto
```

### `Mapper.entity` { #mapper-entity }

**ধরন:** প্রপার্টি

inspection API-র অংশ: ম্যাপ করা ক্লাসটিই দেয় (`class_`-এর সমান)।

**উদাহরণ:**

```python
print(um.entity is User)   # True
```

### `Mapper.entity_namespace` { #mapper-entity-namespace }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`filter_by()`-এ নাম দিয়ে অ্যাট্রিবিউট খোঁজার ভেতরের নাম-ভান্ডার।

### `Mapper.exclude_properties` { #mapper-exclude-properties }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `exclude_properties` সেটিং।

**উদাহরণ:**

```python
print(um.exclude_properties)   # None
```

### `Mapper.extension_type` { #mapper-extension-type }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection API-র ভেতরের টাইপ-চিহ্ন (এটি কোনো এক্সটেনশনের অ্যাট্রিবিউট নয়)।

### `Mapper.get_property()` { #mapper-get-property }

```python
Mapper.get_property(key)
```

**ধরন:** মেথড

নাম দিয়ে একটি `MapperProperty` দেয়; না থাকলে এরর।

**উদাহরণ:**

```python
from sqlalchemy.orm import RelationshipProperty
prop = um.get_property("addresses")
print(isinstance(prop, RelationshipProperty), prop.mapper.class_.__name__)   # True Address
```

### `Mapper.get_property_by_column()` { #mapper-get-property-by-column }

```python
Mapper.get_property_by_column(column)
```

**ধরন:** মেথড

একটি টেবিল-কলাম দিলে কোন অ্যাট্রিবিউট সেটি ম্যাপ করে তা দেয়।

**উদাহরণ:**

```python
print(um.get_property_by_column(User.__table__.c.x).key)   # x
```

### `Mapper.has_property()` { #mapper-has-property }

```python
Mapper.has_property(key)
```

**ধরন:** মেথড

ওই নামের অ্যাট্রিবিউট আছে কি না।

**উদাহরণ:**

```python
print(um.has_property("name"), um.has_property("email"))   # True False
```

### `Mapper.identity_key_from_instance()` { #mapper-identity-key-from-instance }

```python
Mapper.identity_key_from_instance(instance)
```

**ধরন:** মেথড

একটি অবজেক্টের identity map key দেয়: `(ক্লাস, primary key-র tuple, identity_token)`।

**উদাহরণ:**

```python
print(um.identity_key_from_instance(session.get(User, 1))[1])   # (1,)
```

### `Mapper.identity_key_from_primary_key()` { #mapper-identity-key-from-primary-key }

```python
Mapper.identity_key_from_primary_key(primary_key, identity_token=None)
```

**ধরন:** মেথড

primary key-র মান দিয়ে identity key বানায় (অবজেক্ট ছাড়াই)।

**উদাহরণ:**

```python
print(um.identity_key_from_primary_key((1,))[1])   # (1,)
```

### `Mapper.identity_key_from_row()` { #mapper-identity-key-from-row }

```python
Mapper.identity_key_from_row(row, identity_token=None, adapter=None)
```

**ধরন:** মেথড

কুয়েরির একটি রো থেকে identity key বানায়।

**উদাহরণ:**

```python
row = session.execute(select(User.__table__)).first()
print(um.identity_key_from_row(row)[1])   # (1,)
```

### `Mapper.include_properties` { #mapper-include-properties }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `include_properties` সেটিং (না দিলে `None`, মানে সব কলাম ম্যাপ হয়)।

**উদাহরণ:**

```python
print(um.include_properties)   # None
```

### `Mapper.inherit_cache` { #mapper-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ।

### `Mapper.inherit_condition` { #mapper-inherit-condition }

**ধরন:** অ্যাট্রিবিউট

joined inheritance-এ প্যারেন্ট আর এই টেবিলের join-শর্ত।

**উদাহরণ:**

```python
print(inspect(Engineer).inherit_condition)   # employees.id = engineers.id
```

### `Mapper.inherit_foreign_keys` { #mapper-inherit-foreign-keys }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `inherit_foreign_keys` সেটিং।

**উদাহরণ:**

```python
print(inspect(Engineer).inherit_foreign_keys)   # None
```

### `Mapper.inherits` { #mapper-inherits }

**ধরন:** অ্যাট্রিবিউট

প্যারেন্ট mapper (inheritance না থাকলে `None`)।

**উদাহরণ:**

```python
print(inspect(Engineer).inherits.class_.__name__, um.inherits)   # Employee None
```

### `Mapper.is_aliased_class` { #mapper-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি `aliased()` ক্লাস নয় (`False`)।

### `Mapper.is_attribute` { #mapper-is-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি একটি অ্যাট্রিবিউট নয় (`False`)।

### `Mapper.is_bundle` { #mapper-is-bundle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি `Bundle` নয়।

### `Mapper.is_clause_element` { #mapper-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি SQL এক্সপ্রেশন নয়।

### `Mapper.is_instance` { #mapper-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি একটি অবজেক্টের অবস্থা (`InstanceState`) নয়।

### `Mapper.is_mapper` { #mapper-is-mapper }

**ধরন:** অ্যাট্রিবিউট

`inspect()`-এর ফল একটি mapper কি না বুঝতে: এখানে `True`।

**উদাহরণ:**

```python
print(inspect(User).is_mapper)   # True
```

### `Mapper.is_property` { #mapper-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ: এটি `MapperProperty` নয়।

### `Mapper.is_selectable` { #mapper-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর টাইপ-ফ্ল্যাগ।

### `Mapper.is_sibling()` { #mapper-is-sibling }

```python
Mapper.is_sibling(other)
```

**ধরন:** মেথড

দুটি mapper একই প্যারেন্টের ভিন্ন শাখা (ভাইবোন) হলে `True`।

**উদাহরণ:**

```python
print(inspect(Engineer).is_sibling(inspect(Manager)))   # True
```

### `Mapper.isa()` { #mapper-isa }

```python
Mapper.isa(other)
```

**ধরন:** মেথড

এই mapper দেওয়া mapper থেকে (বা সেটাই) তৈরি হলে `True`, Python-এর `issubclass`-এর মতো।

**উদাহরণ:**

```python
print(inspect(Engineer).isa(inspect(Employee)))   # True
```

### `Mapper.iterate_properties` { #mapper-iterate-properties }

**ধরন:** প্রপার্টি

সব `MapperProperty`-এর একটি iterator।

**উদাহরণ:**

```python
print(len(list(um.iterate_properties)))   # 9
```

### `Mapper.iterate_to_root()` { #mapper-iterate-to-root }

```python
Mapper.iterate_to_root()
```

**ধরন:** মেথড

এই mapper থেকে শুরু করে প্যারেন্ট, তার প্যারেন্ট … মূল পর্যন্ত ঘুরে দেয়।

**উদাহরণ:**

```python
print([m.class_.__name__ for m in inspect(Engineer).iterate_to_root()])   # ['Engineer', 'Employee']
```

### `Mapper.legacy_is_orphan` { #mapper-legacy-is-orphan }

**ধরন:** অ্যাট্রিবিউট

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

কনস্ট্রাক্টরের `legacy_is_orphan` সেটিং।

**উদাহরণ:**

```python
print(um.legacy_is_orphan)   # False
```

### `Mapper.local_table` { #mapper-local-table }

**ধরন:** অ্যাট্রিবিউট

ক্লাসের নিজের টেবিল (joined inheritance-এ সন্তানের নিজের টেবিল; single inheritance-এ প্যারেন্টের টেবিল)।

**উদাহরণ:**

```python
print(inspect(Engineer).local_table.name)   # engineers
```

### `Mapper.logger` { #mapper-logger }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই mapper-এর লগার (`sqlalchemy.orm.mapper.Mapper`)।

### `Mapper.logging_name` { #mapper-logging-name }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লগে ব্যবহৃত নাম।

### `Mapper.mapper` { #mapper-mapper }

**ধরন:** প্রপার্টি

inspection API-র অংশ: নিজেকেই দেয়।

**উদাহরণ:**

```python
print(um.mapper is um)   # True
```

### `Mapper.memoized_attribute` { #mapper-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `Mapper.memoized_instancemethod()` { #mapper-memoized-instancemethod }

```python
Mapper.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `Mapper.passive_deletes` { #mapper-passive-deletes }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `passive_deletes` সেটিং।

**উদাহরণ:**

```python
print(um.passive_deletes)   # False
```

### `Mapper.passive_updates` { #mapper-passive-updates }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `passive_updates` সেটিং।

**উদাহরণ:**

```python
print(um.passive_updates)   # True
```

### `Mapper.path_string()` { #mapper-path-string }

```python
Mapper.path_string()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

loader path-এর স্ট্রিং রূপে এই mapper-এর নাম।

### `Mapper.persist_selectable` { #mapper-persist-selectable }

**ধরন:** অ্যাট্রিবিউট

যে টেবিল/join-এ এই ক্লাসের রো লেখা হয় (joined inheritance-এ প্যারেন্ট-সন্তানের join)।

**উদাহরণ:**

```python
print(inspect(Engineer).persist_selectable)   # employees JOIN engineers ON employees.id = engineers.id
```

### `Mapper.polymorphic_abstract` { #mapper-polymorphic-abstract }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `polymorphic_abstract` সেটিং।

**উদাহরণ:**

```python
print(um.polymorphic_abstract)   # False
```

### `Mapper.polymorphic_identity` { #mapper-polymorphic-identity }

**ধরন:** অ্যাট্রিবিউট

এই ক্লাসের discriminator মান।

**উদাহরণ:**

```python
print(inspect(Manager).polymorphic_identity)   # manager
```

### `Mapper.polymorphic_iterator()` { #mapper-polymorphic-iterator }

```python
Mapper.polymorphic_iterator()
```

**ধরন:** মেথড

এই mapper আর তার সব উত্তরসূরি mapper ঘুরে দেয়।

**উদাহরণ:**

```python
print(sorted(m.class_.__name__ for m in inspect(Employee).polymorphic_iterator()))
# ['Employee', 'Engineer', 'Manager']
```

### `Mapper.polymorphic_load` { #mapper-polymorphic-load }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `polymorphic_load` সেটিং।

**উদাহরণ:**

```python
print(inspect(Engineer).polymorphic_load)   # None
```

### `Mapper.polymorphic_map` { #mapper-polymorphic-map }

**ধরন:** অ্যাট্রিবিউট

discriminator মান → mapper-এর dict। কোন মান কোন সাবক্লাস বোঝায় তা দেখায়।

**উদাহরণ:**

```python
print(sorted(inspect(Employee).polymorphic_map))   # ['employee', 'engineer', 'manager']
```

### `Mapper.polymorphic_on` { #mapper-polymorphic-on }

**ধরন:** অ্যাট্রিবিউট

discriminator কলাম (না থাকলে `None`)।

**উদাহরণ:**

```python
print(inspect(Employee).polymorphic_on)   # employees.type
```

### `Mapper.primary_base_mapper` { #mapper-primary-base-mapper }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inheritance-এর মূল "primary" mapper (প্রায় সবসময় `base_mapper`-এর সমান)।

### `Mapper.primary_key` { #mapper-primary-key }

**ধরন:** অ্যাট্রিবিউট

mapper-এর দৃষ্টিতে primary key কলামগুলোর tuple।

**উদাহরণ:**

```python
print([c.name for c in um.primary_key])   # ['id']
```

### `Mapper.primary_key_from_instance()` { #mapper-primary-key-from-instance }

```python
Mapper.primary_key_from_instance(instance)
```

**ধরন:** মেথড

একটি অবজেক্টের primary key মানগুলো tuple হিসেবে দেয়।

**উদাহরণ:**

```python
print(um.primary_key_from_instance(session.get(User, 1)))   # (1,)
```

### `Mapper.primary_mapper()` { #mapper-primary-mapper }

```python
Mapper.primary_mapper()
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

এই ক্লাসের "primary" mapper দেয় (non-primary mapper সরানোর পর কার্যত নিজেই)।

**উদাহরণ:**

```python
print(um.primary_mapper() is um)   # True
```

### `Mapper.registry` { #mapper-registry }

**ধরন:** অ্যাট্রিবিউট

এই mapper যে `registry`-তে আছে।

**উদাহরণ:**

```python
print(um.registry is Base.registry)   # True
```

### `Mapper.relationships` { #mapper-relationships }

**ধরন:** প্রপার্টি

শুধু রিলেশনশিপগুলো, নাম অনুযায়ী। প্রতিটি থেকে লক্ষ্য mapper, direction ইত্যাদি জানা যায়।

**উদাহরণ:**

```python
rel = um.relationships["addresses"]
print(rel.mapper.class_.__name__, rel.direction.name, rel.uselist)   # Address ONETOMANY True
```

### `Mapper.represents_outer_join` { #mapper-represents-outer-join }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection-এর ভেতরের ফ্ল্যাগ।

### `Mapper.select_identity_token` { #mapper-select-identity-token }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

horizontal sharding-এ identity token বাছাইয়ের ভেতরের এক্সপ্রেশন।

### `Mapper.selectable` { #mapper-selectable }

**ধরন:** প্রপার্টি

এই ক্লাস কুয়েরি করলে ডিফল্টে কোন টেবিল/join থেকে SELECT হয়।

**উদাহরণ:**

```python
print(um.selectable.name)   # users
```

### `Mapper.self_and_descendants` { #mapper-self-and-descendants }

**ধরন:** প্রপার্টি

এই mapper আর তার সব উত্তরসূরির সংগ্রহ।

**উদাহরণ:**

```python
print(len(inspect(Employee).self_and_descendants))   # 3
```

### `Mapper.single` { #mapper-single }

**ধরন:** অ্যাট্রিবিউট

single-table inheritance-এর সাবক্লাস হলে `True`।

**উদাহরণ:**

```python
print(inspect(Engineer).single)   # False
```

### `Mapper.synonyms` { #mapper-synonyms }

**ধরন:** প্রপার্টি

শুধু `synonym()` অ্যাট্রিবিউটগুলো।

**উদাহরণ:**

```python
print(list(um.synonyms.keys()))   # ['alias']
```

### `Mapper.tables` { #mapper-tables }

**ধরন:** অ্যাট্রিবিউট

এই mapper যেসব টেবিল ব্যবহার করে (joined inheritance-এ একাধিক)।

**উদাহরণ:**

```python
print([t.name for t in inspect(Engineer).tables])   # ['employees', 'engineers']
```

### `Mapper.uses_inspection` { #mapper-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ।

### `Mapper.validators` { #mapper-validators }

**ধরন:** অ্যাট্রিবিউট

`@validates` দিয়ে যুক্ত ভ্যালিডেটরগুলোর dict (অ্যাট্রিবিউটের নাম → মেথড)।

**উদাহরণ:**

```python
print(dict(um.validators))   # {}
```

### `Mapper.version_id_col` { #mapper-version-id-col }

**ধরন:** অ্যাট্রিবিউট

optimistic locking-এর ভার্সন কলাম।

**উদাহরণ:**

```python
print(um.version_id_col.name)   # version
```

### `Mapper.version_id_generator` { #mapper-version-id-generator }

**ধরন:** অ্যাট্রিবিউট

নতুন ভার্সন মান বানানোর ফাংশন।

**উদাহরণ:**

```python
print(um.version_id_generator(1))   # 2
```

### `Mapper.with_polymorphic` { #mapper-with-polymorphic }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরের `with_polymorphic` সেটিং (ভেতরে স্বাভাবিক রূপে)।

**উদাহরণ:**

```python
print(inspect(Employee).with_polymorphic)   # None
```

### `Mapper.with_polymorphic_mappers` { #mapper-with-polymorphic-mappers }

**ধরন:** প্রপার্টি

ডিফল্ট polymorphic লোডিংয়ে যেসব সাবক্লাস mapper join হবে তাদের তালিকা।

**উদাহরণ:**

```python
print(inspect(Employee).with_polymorphic_mappers)   # []
```

## `configure_mappers()` { #configure-mappers }

```python
from sqlalchemy.orm import configure_mappers
```

```python
configure_mappers()
```

**ধরন:** ফাংশন

সব রেজিস্ট্রির এখনো configure না হওয়া mapper একসাথে configure করে। অ্যাপ চালুর সময় একবার ডাকলে মডেলের ভুল (যেমন ভুল রিলেশনশিপ নাম) প্রথম রিকোয়েস্টের আগেই ধরা পড়ে।

**উদাহরণ:**

```python
configure_mappers()
print(all(m.configured for m in Base.registry.mappers))   # True
```

## `clear_mappers()` { #clear-mappers }

```python
from sqlalchemy.orm import clear_mappers
```

```python
clear_mappers()
```

**ধরন:** ফাংশন

সব রেজিস্ট্রির সব mapper মুছে দেয়; ক্লাসগুলো আর ম্যাপ করা থাকে না। শুধু টেস্টে প্রয়োজন হলে ব্যবহার করুন, সাধারণ অ্যাপে কখনো নয়।

**উদাহরণ:**

```python
clear_mappers()
print(len(Base.registry.mappers))   # 0
```

## `class_mapper()` { #class-mapper }

```python
from sqlalchemy.orm import class_mapper
```

```python
class_mapper(class_, configure=True)
```

**ধরন:** ফাংশন

একটি ক্লাসের `Mapper` দেয়; ক্লাসটি ম্যাপ করা না হলে এরর। `inspect(User)`-এর মতোই।

**উদাহরণ:**

```python
print(class_mapper(User) is inspect(User))   # True
```

### `class_mapper()`-এর সব প্যারামিটার { #class-mapper-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `class_` | যে ক্লাসের mapper চাই। |
| `configure` | `True` (ডিফল্ট) হলে ফেরত দেওয়ার আগে mapper configure করে নেয়। |

## `object_mapper()` { #object-mapper }

```python
from sqlalchemy.orm import object_mapper
```

```python
object_mapper(instance)
```

**ধরন:** ফাংশন

একটি অবজেক্টের (ইনস্ট্যান্স) `Mapper` দেয়।

**উদাহরণ:**

```python
print(object_mapper(User(name="x")) is um)   # True
```

## `mapped_as_dataclass()` { #mapped-as-dataclass }

```python
from sqlalchemy.orm import mapped_as_dataclass
```

```python
mapped_as_dataclass(registry, /, *, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, eq=_NoArg.NO_ARG, order=_NoArg.NO_ARG, unsafe_hash=_NoArg.NO_ARG, match_args=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, dataclass_callable=_NoArg.NO_ARG)
```

**ধরন:** ডেকোরেটর

(২.০.৪৪-এ নতুন) `registry.mapped_as_dataclass`-এর আলাদা ফাংশন রূপ: প্রথম আর্গুমেন্টে রেজিস্ট্রি দিয়ে ক্লাসকে ম্যাপ ও dataclass দুটোই করে। কিছু টাইপ চেকারে (mypy) মেথড রূপের চেয়ে ভালো কাজ করে।

**উদাহরণ:**

```python
reg = registry()

@mapped_as_dataclass(reg, kw_only=True)
class Item:
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str]

print(Item(title="খাতা"))   # Item(id=None, title='খাতা')
```

### `mapped_as_dataclass()`-এর সব প্যারামিটার { #mapped-as-dataclass-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `registry` | যে `registry`-তে ক্লাসটি ম্যাপ হবে। |
| `init` | dataclass-এর `__init__` তৈরি হবে কি না। |
| `repr` | `__repr__` তৈরি হবে কি না। |
| `eq` | `__eq__` তৈরি হবে কি না। |
| `order` | `<`, `>` ইত্যাদি তুলনা-মেথড তৈরি হবে কি না। |
| `unsafe_hash` | `__hash__` জোর করে তৈরি হবে কি না। |
| `match_args` | `match` স্টেটমেন্টের জন্য `__match_args__` তৈরি হবে কি না। |
| `kw_only` | সব ফিল্ড শুধু keyword দিয়ে দেওয়া যাবে। |
| `dataclass_callable` | `dataclasses.dataclass`-এর বদলে অন্য কোনো dataclass-ফাংশন (যেমন Pydantic-এর) ব্যবহার করতে। |

## `add_mapped_attribute()` { #add-mapped-attribute }

```python
from sqlalchemy.orm import add_mapped_attribute
```

```python
add_mapped_attribute(target, key, attr)
```

**ধরন:** ফাংশন

ইতিমধ্যে ম্যাপ হওয়া ক্লাসে পরে একটি নতুন ম্যাপ করা অ্যাট্রিবিউট (কলাম, রিলেশনশিপ, column_property) যোগ করে। মডেল-ফাইলগুলোর পারস্পরিক ইমপোর্ট-চক্র ভাঙতে বা প্লাগিন থেকে অ্যাট্রিবিউট যোগ করতে কাজে লাগে।

**উদাহরণ:**

```python
add_mapped_attribute(User, "address_count", column_property(
    select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()))
print(session.get(User, 1).address_count)   # 1
```

### `add_mapped_attribute()`-এর সব প্যারামিটার { #add-mapped-attribute-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target` | যে ম্যাপ করা ক্লাসে অ্যাট্রিবিউট যোগ হবে। |
| `key` | নতুন অ্যাট্রিবিউটের নাম। |
| `attr` | অ্যাট্রিবিউটটি: `mapped_column()`, `relationship()`, `column_property()` ইত্যাদি। |

## `polymorphic_union()` { #polymorphic-union }

```python
from sqlalchemy.orm import polymorphic_union
```

```python
polymorphic_union(table_map, typecolname, aliasname='p_union', cast_nulls=True)
```

**ধরন:** ফাংশন

concrete table inheritance-এ সব ক্লাসের আলাদা টেবিলকে একটি `UNION ALL` সাবকুয়েরিতে জুড়ে দেয়, যাতে বেস ক্লাস কুয়েরি করলে সব টেবিলের রো আসে। যেসব কলাম কোনো টেবিলে নেই সেখানে NULL বসায়, আর একটি discriminator কলাম যোগ করে।

**উদাহরণ:**

```python
md = MetaData()
cars = Table("cars", md, Column("id", Integer, primary_key=True), Column("name", String))
bikes = Table("bikes", md, Column("id", Integer, primary_key=True), Column("name", String))
pu = polymorphic_union({"car": cars, "bike": bikes}, "kind", "vehicles")
print(sorted(pu.c.keys()))   # ['id', 'kind', 'name']
```

### `polymorphic_union()`-এর সব প্যারামিটার { #polymorphic-union-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `table_map` | discriminator মান → টেবিলের dict। |
| `typecolname` | যোগ হওয়া discriminator কলামের নাম (`None` দিলে যোগ হয় না)। |
| `aliasname` | তৈরি হওয়া সাবকুয়েরির নাম (ডিফল্ট `"p_union"`)। |
| `cast_nulls` | অনুপস্থিত কলামের NULL-কে সঠিক টাইপে `CAST` করবে কি না (ডিফল্ট `True`; কিছু ডেটাবেসে UNION-এর জন্য দরকার)। |

/// check | সংক্ষেপে মনে রাখুন

* যেকোনো মডেলের বিবরণ: `inspect(User)` → `Mapper`; কলাম `.columns` / `.column_attrs`, রিলেশনশিপ `.relationships`, সব `.attrs`।
* inheritance: `.inherits`, `.base_mapper`, `.polymorphic_map`, `.isa()`।
* অবজেক্টের পরিচয়: `.primary_key_from_instance()`, `.identity_key_from_instance()`।
* অ্যাপ চালুর সময় `configure_mappers()` ডাকলে মডেলের ভুল আগেভাগে ধরা পড়ে।
* `registry` থেকে বেস ছাড়াই ম্যাপিং: `@reg.mapped`, `@reg.mapped_as_dataclass`, `reg.map_imperatively()`।

///
