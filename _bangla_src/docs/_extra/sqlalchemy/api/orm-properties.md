# Mapper Property API: ColumnProperty, Relationship, Composite, Synonym … { #api-orm-properties }

/// note | এই পেজে যা আছে

`mapped_column()`, `relationship()`, `column_property()`, `composite()`, `synonym()` আসলে যে অবজেক্ট বানায়, আর ম্যাপিংয়ের পর `inspect(User).attrs` থেকে যা পাওয়া যায়:

* **মূল ক্লাস:** `InspectionAttr`, `InspectionAttrInfo`, `InspectionAttrExtensionType`, `NotExtension`, `MapperProperty`, `PropComparator`।
* **কলাম:** `ColumnProperty` (আর তার `Comparator`), `MappedColumn`, `MappedSQLExpression`, `SQLORMExpression`, `ORMDescriptor`।
* **সম্পর্ক:** `RelationshipProperty` (আর তার `Comparator`), `Relationship`, `RelationshipDirection`, `CascadeOptions`।
* **composite ও synonym:** `CompositeProperty` (আর `Comparator`), `Composite`, `SynonymProperty`, `Synonym`।

///

এগুলো কোথায় কাজে লাগে: মডেল থেকে **নিজে থেকে কিছু বানাতে** (যেমন প্রতিটি relationship দেখে API serializer, admin প্যানেল, বা ডকুমেন্টেশন), নিজের comparator লিখতে, বা ডিবাগে "এই relationship কোন দিকে, কোন কলাম দিয়ে যুক্ত"। প্যারামিটারগুলোর ব্যাখ্যা আছে [ORM ম্যাপিং পেজে](mapping.md) (`mapped_column()`, `relationship()` …); এখানে তৈরি হওয়া অবজেক্টের সদস্য।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
@dataclasses.dataclass
class Point:
    x: int
    y: int

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    bio: Mapped[str | None] = mapped_column(deferred=True)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    name_len: Mapped[int] = column_property(func.length(name))
    display_name = synonym("name")

class Address(Base):   # id, email, user_id, user = relationship(back_populates="addresses")
class Shape(Base):     # id, start: Mapped[Point] = composite(mapped_column("x1"), mapped_column("y1"))
```

ডেটা: রহিম (দুটি ঠিকানা), করিম; Shape ১ (শুরু `Point(1, 2)`)। `m = inspect(User)` (Mapper), `rel = m.attrs.addresses`। PostgreSQL 16-এ চালিয়ে দেখা।

///

## মূল ক্লাস { #inspectionattr-group }

## `InspectionAttr` { #inspectionattr }

```python
from sqlalchemy.orm import InspectionAttr
```

`inspect()` যা কিছু ফেরত দিতে পারে (Mapper, অ্যাট্রিবিউট, property, aliased class, `InstanceState` …) তাদের সবার মূল ক্লাস। এর `is_*` পতাকাগুলো দিয়ে `isinstance()` ছাড়াই বোঝা যায় হাতের জিনিসটি কী।

**উদাহরণ:**

```python
for obj in [m, User.name, m.attrs.name, inspect(aliased(User)), inspect(session.get(User, 1))]:
    print(type(obj).__name__, obj.is_mapper, obj.is_attribute, obj.is_property, obj.is_aliased_class, obj.is_instance)
# Mapper True False False False False
# InstrumentedAttribute False True False False False
# ColumnProperty False False True False False
# AliasedInsp False False False True False
# InstanceState False False False False True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #inspectionattr-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`extension_type`](#inspectionattr-extension-type) | অ্যাট্রিবিউট | এটি কোনো এক্সটেনশনের অংশ কি না: সাধারণ অ্যাট্রিবিউটে `NotExtension.NOT_EXTENSION`, hybrid হলে `HybridExtensionType.HYBRID_PROPERTY` ইত্যাদি। |
| [`is_aliased_class`](#inspectionattr-is-aliased-class) | অ্যাট্রিবিউট | `aliased()`-এর inspect রূপ (`AliasedInsp`) কি না। |
| [`is_attribute`](#inspectionattr-is-attribute) | অ্যাট্রিবিউট | ক্লাস-লেভেলের অ্যাট্রিবিউট (`User.name`, `QueryableAttribute`) কি না। |
| [`is_bundle`](#inspectionattr-is-bundle) | অ্যাট্রিবিউট | `Bundle` কি না। |
| [`is_clause_element`](#inspectionattr-is-clause-element) | অ্যাট্রিবিউট | Core-এর `ClauseElement` (SQL এক্সপ্রেশন) কি না। |
| [`is_instance`](#inspectionattr-is-instance) | অ্যাট্রিবিউট | একটি অবজেক্টের `InstanceState` কি না। |
| [`is_mapper`](#inspectionattr-is-mapper) | অ্যাট্রিবিউট | `Mapper` কি না। |
| [`is_property`](#inspectionattr-is-property) | অ্যাট্রিবিউট | `MapperProperty` (ColumnProperty, Relationship …) কি না। |
| [`is_selectable`](#inspectionattr-is-selectable) | অ্যাট্রিবিউট | FROM-এ বসানো যায় এমন `Selectable` (Table ইত্যাদি) কি না। |

### `InspectionAttr.extension_type` { #inspectionattr-extension-type }

**ধরন:** অ্যাট্রিবিউট

এটি কোনো এক্সটেনশনের অংশ কি না: সাধারণ অ্যাট্রিবিউটে `NotExtension.NOT_EXTENSION`, hybrid হলে `HybridExtensionType.HYBRID_PROPERTY` ইত্যাদি। `mapper.all_orm_descriptors` থেকে hybrid আলাদা করতে।

**উদাহরণ:**

```python
class U2(Base):
    __tablename__ = "u2"
    id: Mapped[int] = mapped_column(primary_key=True)
    @hybrid_property
    def double(self):
        return self.id * 2
d = inspect(U2).all_orm_descriptors
print(d["id"].extension_type, d["double"].extension_type)   # NotExtension.NOT_EXTENSION HybridExtensionType.HYBRID_PROPERTY
```

### `InspectionAttr.is_aliased_class` { #inspectionattr-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

`aliased()`-এর inspect রূপ (`AliasedInsp`) কি না।

**উদাহরণ:**

```python
print(inspect(aliased(User)).is_aliased_class, m.is_aliased_class)   # True False
```

### `InspectionAttr.is_attribute` { #inspectionattr-is-attribute }

**ধরন:** অ্যাট্রিবিউট

ক্লাস-লেভেলের অ্যাট্রিবিউট (`User.name`, `QueryableAttribute`) কি না।

**উদাহরণ:**

```python
print(User.name.is_attribute, m.attrs.name.is_attribute)   # True False
```

### `InspectionAttr.is_bundle` { #inspectionattr-is-bundle }

**ধরন:** অ্যাট্রিবিউট

`Bundle` কি না।

**উদাহরণ:**

```python
from sqlalchemy.orm import Bundle
print(Bundle("b", User.id).is_bundle)   # True
```

### `InspectionAttr.is_clause_element` { #inspectionattr-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

Core-এর `ClauseElement` (SQL এক্সপ্রেশন) কি না।

**উদাহরণ:**

```python
print(User.__table__.c.name.is_clause_element, User.name.is_clause_element)   # True False
```

### `InspectionAttr.is_instance` { #inspectionattr-is-instance }

**ধরন:** অ্যাট্রিবিউট

একটি অবজেক্টের `InstanceState` কি না।

**উদাহরণ:**

```python
print(inspect(session.get(User, 1)).is_instance)   # True
```

### `InspectionAttr.is_mapper` { #inspectionattr-is-mapper }

**ধরন:** অ্যাট্রিবিউট

`Mapper` কি না।

**উদাহরণ:**

```python
print(inspect(User).is_mapper, inspect(aliased(User)).is_mapper)   # True False
```

### `InspectionAttr.is_property` { #inspectionattr-is-property }

**ধরন:** অ্যাট্রিবিউট

`MapperProperty` (ColumnProperty, Relationship …) কি না।

**উদাহরণ:**

```python
print(rel.is_property)   # True
```

### `InspectionAttr.is_selectable` { #inspectionattr-is-selectable }

**ধরন:** অ্যাট্রিবিউট

FROM-এ বসানো যায় এমন `Selectable` (Table ইত্যাদি) কি না।

**উদাহরণ:**

```python
print(User.__table__.is_selectable, m.is_selectable)   # True False
```

## `InspectionAttrInfo` { #inspectionattrinfo }

```python
from sqlalchemy.orm import InspectionAttrInfo
```

`InspectionAttr`-এর সাথে `.info` dict যোগ করে। `MapperProperty` (তাই সব `ColumnProperty`, `Relationship` …) আর `InstanceState` এর থেকে আসে। `Mapper` আর `User.name` (`QueryableAttribute`) নয়: অ্যাট্রিবিউটের `User.name.info` আসলে তার property-র `info`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(isinstance(rel, InspectionAttrInfo), isinstance(inspect(u), InspectionAttrInfo), isinstance(m, InspectionAttrInfo))   # True True False
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #inspectionattrinfo-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`info`](#inspectionattrinfo-info) | প্রপার্টি | নিজের তথ্য রাখার খালি dict (প্রথমবার পড়লে তৈরি হয়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `InspectionAttrInfo`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

///

### `InspectionAttrInfo.info` { #inspectionattrinfo-info }

**ধরন:** প্রপার্টি

নিজের তথ্য রাখার খালি dict (প্রথমবার পড়লে তৈরি হয়)। `mapped_column(info={...})`, `relationship(info={...})` দিয়ে শুরুতেই দেওয়া যায়; যেমন admin প্যানেলে লেবেল বা "API-তে দেখাবে না" চিহ্ন।

**উদাহরণ:**

```python
class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    secret: Mapped[str] = mapped_column(info={"hidden": True})
print([k for k, p in inspect(Tag).column_attrs.items() if p.columns[0].info.get("hidden")])   # ['secret']
rel.info["label"] = "ঠিকানা"
print(inspect(User).attrs.addresses.info)   # {'label': 'ঠিকানা'}
```

## `InspectionAttrExtensionType` { #inspectionattrextensiontype }

```python
from sqlalchemy.orm import InspectionAttrExtensionType
```

`extension_type`-এর মানগুলোর মূল `Enum` (নিজের কোনো মান নেই)। এর সন্তান: `NotExtension`, `HybridExtensionType` (`HYBRID_PROPERTY`, `HYBRID_METHOD`), `AssociationProxyExtensionType`। নিজের এক্সটেনশন লিখলে এটি subclass করে নিজের মান দিন।

**উদাহরণ:**

```python
print(issubclass(NotExtension, InspectionAttrExtensionType), issubclass(HybridExtensionType, InspectionAttrExtensionType))   # True True
```

## `NotExtension` { #notextension }

```python
from sqlalchemy.orm import NotExtension
```

সাধারণ (এক্সটেনশন নয় এমন) অ্যাট্রিবিউটের `extension_type`।

**উদাহরণ:**

```python
print(User.name.extension_type is NotExtension.NOT_EXTENSION)   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #notextension-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`NOT_EXTENSION`](#notextension-NOT-EXTENSION) | অ্যাট্রিবিউট | একমাত্র মান: "এটা কোনো এক্সটেনশনের নয়"। |

### `NotExtension.NOT_EXTENSION` { #notextension-NOT-EXTENSION }

**ধরন:** অ্যাট্রিবিউট

একমাত্র মান: "এটা কোনো এক্সটেনশনের নয়"।

**উদাহরণ:**

```python
print(NotExtension.NOT_EXTENSION.value)   # not_extension
```

## `MapperProperty` { #mapperproperty }

```python
from sqlalchemy.orm import MapperProperty
```

Mapper-এর প্রতিটি অ্যাট্রিবিউটের মূল ক্লাস: `ColumnProperty`, `Relationship`, `Composite`, `Synonym` সবই এর সন্তান। `inspect(User).attrs` এদের সংগ্রহ। এখানকার বেশিরভাগ মেথড ORM নিজে কনফিগার/লোড/merge-এর সময় ডাকে; ব্যবহারকারীর কাজের অংশ `key`, `parent`, `class_attribute`, `info`, `doc`।

**উদাহরণ:**

```python
for key, prop in m.attrs.items():
    print(key, type(prop).__name__, isinstance(prop, MapperProperty))
# addresses _RelationshipDeclared True
# name_len MappedSQLExpression True
# display_name Synonym True
# id ColumnProperty True
# name ColumnProperty True
# bio ColumnProperty True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mapperproperty-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cascade`](#mapperproperty-cascade) | অ্যাট্রিবিউট | এই property-র cascade নিয়ম ([`CascadeOptions`](#cascadeoptions))। |
| [`cascade_iterator()`](#mapperproperty-cascade-iterator) | মেথড (internal) | একটি cascade নিয়ম (যেমন `"save-update"`) মেনে কোন সম্পর্কিত অবজেক্টগুলোতে কাজটি ছড়াবে তা দেয়। |
| [`class_attribute`](#mapperproperty-class-attribute) | প্রপার্টি | এই property-র ক্লাস-লেভেলের অ্যাট্রিবিউট (`User.name`)। |
| [`create_row_processor()`](#mapperproperty-create-row-processor) | মেথড (internal) | ফলের রো থেকে অবজেক্টে মান বসানোর ফাংশন বানায় (লোডিং strategy ডাকে)। |
| [`do_init()`](#mapperproperty-do-init) | মেথড (internal) | mapper তৈরির পর subclass-বিশেষ প্রস্তুতি (relationship-এ join শর্ত হিসাব ইত্যাদি)। |
| [`doc`](#mapperproperty-doc) | অ্যাট্রিবিউট | `mapped_column(doc="...")`/`relationship(doc="...")`-এ দেওয়া ডকস্ট্রিং, নইলে `None`। |
| [`inherit_cache`](#mapperproperty-inherit-cache) | অ্যাট্রিবিউট (internal) | SQL ক্যাশ-কী সংক্রান্ত পতাকা। |
| [`init()`](#mapperproperty-init) | মেথড (internal) | সব mapper তৈরি হওয়ার পর property-কে প্রস্তুত করে (`configure_mappers()` ডাকে)। |
| [`instrument_class()`](#mapperproperty-instrument-class) | মেথড (internal) | ক্লাসে descriptor (`User.addresses`) বসায়। |
| [`key`](#mapperproperty-key) | অ্যাট্রিবিউট | অ্যাট্রিবিউটের নাম। |
| [`merge()`](#mapperproperty-merge) | মেথড (internal) | `session.merge()`-এর সময় এই অ্যাট্রিবিউটের মান উৎস থেকে গন্তব্যে কপি করে। |
| [`parent`](#mapperproperty-parent) | অ্যাট্রিবিউট | যে Mapper-এর property (মালিক ক্লাসের Mapper)। |
| [`path_string()`](#mapperproperty-path-string) | মেথড (internal) | লোড-পথে দেখানোর নাম (`ClassName.attr`)। |
| [`post_instrument_class()`](#mapperproperty-post-instrument-class) | মেথড (internal) | `init()`-এর পর শেষ instrumentation সমন্বয়। |
| [`set_parent()`](#mapperproperty-set-parent) | মেথড (internal) | property-কে তার mapper-এর সাথে যুক্ত করে। |
| [`setup()`](#mapperproperty-setup) | মেথড (internal) | SELECT বানানোর সময় এই property-র কলাম/join যোগ করে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MapperProperty`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

### `MapperProperty.cascade` { #mapperproperty-cascade }

**ধরন:** অ্যাট্রিবিউট

এই property-র cascade নিয়ম ([`CascadeOptions`](#cascadeoptions))। relationship ছাড়া অন্যগুলোতে খালি।

**উদাহরণ:**

```python
print(sorted(rel.cascade), m.attrs.name.cascade)   # ['delete', 'delete-orphan', 'expunge', 'merge', 'refresh-expire', 'save-update'] None
```

### `MapperProperty.cascade_iterator()` { #mapperproperty-cascade-iterator }

```python
MapperProperty.cascade_iterator(type_, state, dict_, visited_states, halt_on=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি cascade নিয়ম (যেমন `"save-update"`) মেনে কোন সম্পর্কিত অবজেক্টগুলোতে কাজটি ছড়াবে তা দেয়।

**উদাহরণ:**

```python
u = session.get(User, 1)
st = inspect(u)
related = list(rel.cascade_iterator("delete", st, st.dict, set()))
print(len(related))   # 2
```

### `MapperProperty.class_attribute` { #mapperproperty-class-attribute }

**ধরন:** প্রপার্টি

এই property-র ক্লাস-লেভেলের অ্যাট্রিবিউট (`User.name`)।

**উদাহরণ:**

```python
print(m.attrs.name.class_attribute is User.name)   # True
```

### `MapperProperty.create_row_processor()` { #mapperproperty-create-row-processor }

```python
MapperProperty.create_row_processor(context, query_entity, path, mapper, result, adapter, populators)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফলের রো থেকে অবজেক্টে মান বসানোর ফাংশন বানায় (লোডিং strategy ডাকে)।

**উদাহরণ:**

```python
print(callable(MapperProperty.create_row_processor))   # True
```

### `MapperProperty.do_init()` { #mapperproperty-do-init }

```python
MapperProperty.do_init()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

mapper তৈরির পর subclass-বিশেষ প্রস্তুতি (relationship-এ join শর্ত হিসাব ইত্যাদি)।

**উদাহরণ:**

```python
print(callable(rel.do_init))   # True
```

### `MapperProperty.doc` { #mapperproperty-doc }

**ধরন:** অ্যাট্রিবিউট

`mapped_column(doc="...")`/`relationship(doc="...")`-এ দেওয়া ডকস্ট্রিং, নইলে `None`।

**উদাহরণ:**

```python
class Doc(Base):
    __tablename__ = "docs"
    id: Mapped[int] = mapped_column(primary_key=True, doc="প্রাথমিক চাবি")
print(inspect(Doc).attrs.id.doc)   # প্রাথমিক চাবি
```

### `MapperProperty.inherit_cache` { #mapperproperty-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQL ক্যাশ-কী সংক্রান্ত পতাকা।

**উদাহরণ:**

```python
print(MapperProperty.inherit_cache)   # None
```

### `MapperProperty.init()` { #mapperproperty-init }

```python
MapperProperty.init()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সব mapper তৈরি হওয়ার পর property-কে প্রস্তুত করে (`configure_mappers()` ডাকে)।

**উদাহরণ:**

```python
print(callable(rel.init))   # True
```

### `MapperProperty.instrument_class()` { #mapperproperty-instrument-class }

```python
MapperProperty.instrument_class(mapper)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসে descriptor (`User.addresses`) বসায়।

**উদাহরণ:**

```python
print(callable(rel.instrument_class))   # True
```

### `MapperProperty.key` { #mapperproperty-key }

**ধরন:** অ্যাট্রিবিউট

অ্যাট্রিবিউটের নাম।

**উদাহরণ:**

```python
print(rel.key, m.attrs.name.key)   # addresses name
```

### `MapperProperty.merge()` { #mapperproperty-merge }

```python
MapperProperty.merge(session, source_state, source_dict, dest_state, dest_dict, load)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`session.merge()`-এর সময় এই অ্যাট্রিবিউটের মান উৎস থেকে গন্তব্যে কপি করে।

**উদাহরণ:**

```python
print(callable(MapperProperty.merge))   # True
```

### `MapperProperty.parent` { #mapperproperty-parent }

**ধরন:** অ্যাট্রিবিউট

যে Mapper-এর property (মালিক ক্লাসের Mapper)।

**উদাহরণ:**

```python
print(rel.parent, rel.mapper)   # Mapper[User(users)] Mapper[Address(addresses)]
```

### `MapperProperty.path_string()` { #mapperproperty-path-string }

```python
MapperProperty.path_string()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোড-পথে দেখানোর নাম (`ClassName.attr`)।

**উদাহরণ:**

```python
print(rel.path_string())   # User.addresses
```

### `MapperProperty.post_instrument_class()` { #mapperproperty-post-instrument-class }

```python
MapperProperty.post_instrument_class(mapper)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`init()`-এর পর শেষ instrumentation সমন্বয়।

**উদাহরণ:**

```python
print(callable(rel.post_instrument_class))   # True
```

### `MapperProperty.set_parent()` { #mapperproperty-set-parent }

```python
MapperProperty.set_parent(parent, init)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

property-কে তার mapper-এর সাথে যুক্ত করে।

**উদাহরণ:**

```python
print(callable(MapperProperty.set_parent))   # True
```

### `MapperProperty.setup()` { #mapperproperty-setup }

```python
MapperProperty.setup(context, query_entity, path, adapter, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SELECT বানানোর সময় এই property-র কলাম/join যোগ করে।

**উদাহরণ:**

```python
print(callable(MapperProperty.setup))   # True
```

## `PropComparator` { #propcomparator }

```python
from sqlalchemy.orm import PropComparator
```

ক্লাস-লেভেলের অ্যাট্রিবিউটে (`User.name == "x"`, `User.addresses.any(...)`) যে অপারেটরগুলো কাজ করে, সেগুলোর আসল বাস্তবায়ন এই ক্লাসে। `User.name` (`QueryableAttribute`) প্রতিটি অপারেটর এর `comparator`-কে দিয়ে দেয়। প্রতিটি property-র নিজের subclass আছে (`ColumnProperty.Comparator`, `RelationshipProperty.Comparator` …)।

**নিজের comparator:** subclass করে `__eq__` ইত্যাদি বদলান, তারপর `column_property(mapped_column(...), comparator_factory=...)` দিন। (`mapped_column()`-এ `comparator_factory=` প্যারামিটার **নেই**; দিলে সেটি ভুল করে ডায়ালেক্ট-অপশন ধরা হয়, শুধু একটি সতর্কবার্তা আসে।) নিচের উদাহরণে ছোট-বড় হাতের পার্থক্য-মুক্ত তুলনা।

**উদাহরণ:**

```python
class CaseInsensitive(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = column_property(mapped_column(String), comparator_factory=CaseInsensitive)
print(Person.email == "A@B.com")   # lower(people.email) = lower(:lower_1)
print(isinstance(User.name.comparator, PropComparator))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #propcomparator-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `PropComparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`QueryableAttribute` থেকে:** [`adapt_to_entity()`](operators.md#queryableattribute-adapt-to-entity) · [`adapter`](operators.md#queryableattribute-adapter) · [`and_()`](operators.md#queryableattribute-and-) · [`any()`](operators.md#queryableattribute-any) · [`any_op()`](operators.md#queryableattribute-any-op) · [`has()`](operators.md#queryableattribute-has) · [`has_op()`](operators.md#queryableattribute-has-op) · [`info`](operators.md#queryableattribute-info) · [`of_type()`](operators.md#queryableattribute-of-type) · [`of_type_op()`](operators.md#queryableattribute-of-type-op) · [`prop`](operators.md#queryableattribute-prop) · [`property`](operators.md#queryableattribute-property)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

## কলাম property { #columnproperty-heading-group }

## `ColumnProperty` { #columnproperty }

```python
from sqlalchemy.orm import ColumnProperty
```

একটি কলাম (বা SQL এক্সপ্রেশন) ম্যাপ করা অ্যাট্রিবিউট। `mapped_column()` দেওয়া প্রতিটি কলাম ম্যাপিংয়ের পর এটি হয়; `inspect(User).column_attrs` এদের সংগ্রহ।

**উদাহরণ:**

```python
p = m.attrs.name
print(type(p).__name__, p.columns, p.expression)   # ColumnProperty [Column('name', String(length=50), table=<users>, nullable=False)] users.name
print(list(m.column_attrs.keys()))   # ['name_len', 'id', 'name', 'bio']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columnproperty-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`Comparator`](#columnproperty-Comparator) | অ্যাট্রিবিউট | কলাম property-র comparator ক্লাস; নিচে [`ColumnProperty.Comparator`](#columnproperty-comparator)। |
| [`active_history`](#columnproperty-active-history) | অ্যাট্রিবিউট | `True` হলে মান বদলানোর সময় আগের মান লোড না থাকলেও **আগে লোড করে** রাখে (অডিট লগে "আগের মান" লাগলে)। |
| [`columns`](#columnproperty-columns) | অ্যাট্রিবিউট | এই property-র কলাম(গুলো)র তালিকা (সাধারণত একটি; inheritance-এ একাধিক হতে পারে)। |
| [`columns_to_assign`](#columnproperty-columns-to-assign) | প্রপার্টি (internal) | declarative-এ টেবিলে যোগ করার বাকি কলাম (ম্যাপিংয়ের পর সাধারণত খালি)। |
| [`comparator_factory`](#columnproperty-comparator-factory) | অ্যাট্রিবিউট | কোন comparator ক্লাস ব্যবহার হচ্ছে। |
| [`copy()`](#columnproperty-copy) | মেথড (internal) | এই property-র একটি কপি (কোনো mapper-এ যুক্ত নয়), inheritance-এ ব্যবহার হয়। |
| [`declarative_scan()`](#columnproperty-declarative-scan) | মেথড (internal) | declarative ক্লাস স্ক্যানের সময় annotation (`Mapped[...]`) থেকে টাইপ ইত্যাদি ঠিক করে। |
| [`deferred`](#columnproperty-deferred) | অ্যাট্রিবিউট | কলামটি deferred (প্রথম কুয়েরিতে লোড না হয়ে, প্রথমবার পড়ার সময় লোড) কি না। |
| [`expire_on_flush`](#columnproperty-expire-on-flush) | অ্যাট্রিবিউট | flush-এর পর মান expire হবে কি না। |
| [`expression`](#columnproperty-expression) | প্রপার্টি | প্রধান কলাম বা SQL এক্সপ্রেশন। |
| [`found_in_pep593_annotated()`](#columnproperty-found-in-pep593-annotated) | মেথড (internal) | `Annotated[...]`-এর ভেতরে পাওয়া গেলে ব্যবহারের জন্য একটি কপি দেয়। |
| [`group`](#columnproperty-group) | অ্যাট্রিবিউট | deferred গ্রুপের নাম (`deferred_group=`), নইলে `None`; একই গ্রুপের কলাম একসাথে লোড হয়। |
| [`instrument`](#columnproperty-instrument) | অ্যাট্রিবিউট (internal) | ক্লাসে descriptor বসানো হবে কি না। |
| [`logger`](#columnproperty-logger) | অ্যাট্রিবিউট (internal) | এই ক্লাসের `logging.Logger`। |
| [`logging_name`](#columnproperty-logging-name) | অ্যাট্রিবিউট (internal) | লগে বাড়তি নাম (সাধারণত `None`)। |
| [`mapper_property_to_assign`](#columnproperty-mapper-property-to-assign) | প্রপার্টি (internal) | declarative-এ mapper-এ বসানোর property (নিজেই)। |
| [`raiseload`](#columnproperty-raiseload) | অ্যাট্রিবিউট | deferred কলাম পড়লে লোড না করে এরর দেবে কি না (`mapped_column(deferred_raiseload=True)`); না দিলে `None`। |
| [`strategy`](#columnproperty-strategy) | অ্যাট্রিবিউট (internal) | বর্তমান লোডিং strategy অবজেক্ট। |
| [`strategy_for()`](#columnproperty-strategy-for) | ক্লাস মেথড (internal) | (ক্লাস মেথড) একটি strategy ক্লাসকে নির্দিষ্ট অপশনের জন্য নথিভুক্ত করার ডেকোরেটর। |
| [`strategy_key`](#columnproperty-strategy-key) | অ্যাট্রিবিউট (internal) | বর্তমান strategy-র key (অপশনের tuple)। |
| [`strategy_wildcard_key`](#columnproperty-strategy-wildcard-key) | অ্যাট্রিবিউট (internal) | `defer("*")` ধরনের wildcard অপশনের key। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnProperty`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

### `ColumnProperty.Comparator` { #columnproperty-Comparator }

**ধরন:** অ্যাট্রিবিউট

কলাম property-র comparator ক্লাস; নিচে [`ColumnProperty.Comparator`](#columnproperty-comparator)।

**উদাহরণ:**

```python
print(ColumnProperty.Comparator.__qualname__)   # ColumnProperty.Comparator
```

### `ColumnProperty.active_history` { #columnproperty-active-history }

**ধরন:** অ্যাট্রিবিউট

`True` হলে মান বদলানোর সময় আগের মান লোড না থাকলেও **আগে লোড করে** রাখে (অডিট লগে "আগের মান" লাগলে)। `mapped_column(active_history=True)`।

**উদাহরণ:**

```python
print(m.attrs.name.active_history)   # False
```

### `ColumnProperty.columns` { #columnproperty-columns }

**ধরন:** অ্যাট্রিবিউট

এই property-র কলাম(গুলো)র তালিকা (সাধারণত একটি; inheritance-এ একাধিক হতে পারে)।

**উদাহরণ:**

```python
print([c.name for c in m.attrs.id.columns])   # ['id']
```

### `ColumnProperty.columns_to_assign` { #columnproperty-columns-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

declarative-এ টেবিলে যোগ করার বাকি কলাম (ম্যাপিংয়ের পর সাধারণত খালি)।

**উদাহরণ:**

```python
print(m.attrs.name.columns_to_assign)   # []
```

### `ColumnProperty.comparator_factory` { #columnproperty-comparator-factory }

**ধরন:** অ্যাট্রিবিউট

কোন comparator ক্লাস ব্যবহার হচ্ছে।

**উদাহরণ:**

```python
print(m.attrs.name.comparator_factory.__qualname__)   # ColumnProperty.Comparator
```

### `ColumnProperty.copy()` { #columnproperty-copy }

```python
ColumnProperty.copy()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই property-র একটি কপি (কোনো mapper-এ যুক্ত নয়), inheritance-এ ব্যবহার হয়।

**উদাহরণ:**

```python
print(type(m.attrs.name.copy()).__name__)   # ColumnProperty
```

### `ColumnProperty.declarative_scan()` { #columnproperty-declarative-scan }

```python
ColumnProperty.declarative_scan(decl_scan, registry, originating_module, key, mapped_container, annotation, extracted_mapped_annotation, is_dataclass_field)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

declarative ক্লাস স্ক্যানের সময় annotation (`Mapped[...]`) থেকে টাইপ ইত্যাদি ঠিক করে।

**উদাহরণ:**

```python
print(callable(ColumnProperty.declarative_scan))   # True
```

### `ColumnProperty.deferred` { #columnproperty-deferred }

**ধরন:** অ্যাট্রিবিউট

কলামটি deferred (প্রথম কুয়েরিতে লোড না হয়ে, প্রথমবার পড়ার সময় লোড) কি না।

**উদাহরণ:**

```python
print(m.attrs.bio.deferred, m.attrs.name.deferred)   # True False
```

### `ColumnProperty.expire_on_flush` { #columnproperty-expire-on-flush }

**ধরন:** অ্যাট্রিবিউট

flush-এর পর মান expire হবে কি না। SQL এক্সপ্রেশন-ভিত্তিক `column_property`-তে `True` (ডেটাবেস নতুন মান হিসাব করে), সাধারণ কলামে `True` হলেও INSERT/UPDATE-এ লেখা মান থেকে যায়।

**উদাহরণ:**

```python
print(m.attrs.name_len.expire_on_flush)   # True
```

### `ColumnProperty.expression` { #columnproperty-expression }

**ধরন:** প্রপার্টি

প্রধান কলাম বা SQL এক্সপ্রেশন।

**উদাহরণ:**

```python
print(m.attrs.name_len.expression)   # length(users.name)
```

### `ColumnProperty.found_in_pep593_annotated()` { #columnproperty-found-in-pep593-annotated }

```python
ColumnProperty.found_in_pep593_annotated()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Annotated[...]`-এর ভেতরে পাওয়া গেলে ব্যবহারের জন্য একটি কপি দেয়।

**উদাহরণ:**

```python
print(callable(ColumnProperty.found_in_pep593_annotated))   # True
```

### `ColumnProperty.group` { #columnproperty-group }

**ধরন:** অ্যাট্রিবিউট

deferred গ্রুপের নাম (`deferred_group=`), নইলে `None`; একই গ্রুপের কলাম একসাথে লোড হয়।

**উদাহরণ:**

```python
print(m.attrs.bio.group)   # None
```

### `ColumnProperty.instrument` { #columnproperty-instrument }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসে descriptor বসানো হবে কি না।

**উদাহরণ:**

```python
print(m.attrs.name.instrument)   # True
```

### `ColumnProperty.logger` { #columnproperty-logger }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই ক্লাসের `logging.Logger`।

**উদাহরণ:**

```python
print(ColumnProperty.logger.name)   # sqlalchemy.orm.properties.ColumnProperty
```

### `ColumnProperty.logging_name` { #columnproperty-logging-name }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লগে বাড়তি নাম (সাধারণত `None`)।

**উদাহরণ:**

```python
print(ColumnProperty.logging_name)   # None
```

### `ColumnProperty.mapper_property_to_assign` { #columnproperty-mapper-property-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

declarative-এ mapper-এ বসানোর property (নিজেই)।

**উদাহরণ:**

```python
print(m.attrs.name.mapper_property_to_assign is m.attrs.name)   # True
```

### `ColumnProperty.raiseload` { #columnproperty-raiseload }

**ধরন:** অ্যাট্রিবিউট

deferred কলাম পড়লে লোড না করে এরর দেবে কি না (`mapped_column(deferred_raiseload=True)`); না দিলে `None`।

**উদাহরণ:**

```python
print(m.attrs.bio.raiseload)   # None
```

### `ColumnProperty.strategy` { #columnproperty-strategy }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বর্তমান লোডিং strategy অবজেক্ট।

**উদাহরণ:**

```python
print(type(m.attrs.bio.strategy).__name__)   # _DeferredColumnLoader
```

### `ColumnProperty.strategy_for()` { #columnproperty-strategy-for }

```python
ColumnProperty.strategy_for(**kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) একটি strategy ক্লাসকে নির্দিষ্ট অপশনের জন্য নথিভুক্ত করার ডেকোরেটর।

**উদাহরণ:**

```python
print(callable(ColumnProperty.strategy_for))   # True
```

### `ColumnProperty.strategy_key` { #columnproperty-strategy-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বর্তমান strategy-র key (অপশনের tuple)।

**উদাহরণ:**

```python
print(m.attrs.name.strategy_key)   # (('deferred', False), ('instrument', True))
```

### `ColumnProperty.strategy_wildcard_key` { #columnproperty-strategy-wildcard-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`defer("*")` ধরনের wildcard অপশনের key।

**উদাহরণ:**

```python
print(ColumnProperty.strategy_wildcard_key)   # column
```

## `ColumnProperty.Comparator` { #columnproperty-comparator }

```python
from sqlalchemy.orm import ColumnProperty
```

কলাম অ্যাট্রিবিউটের (`User.name`) অপারেটর: `==`, `like()`, `in_()` … সব [কলাম অপারেটর](operators.md) এখান থেকে আসে। নিজের comparator বানাতে এটি subclass করুন (উপরে `PropComparator`-এর উদাহরণ)।

**উদাহরণ:**

```python
print(type(User.name.comparator).__qualname__, User.name.comparator.expressions)   # ColumnProperty.Comparator [Column('name', String(length=50), table=<users>, nullable=False)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columnproperty-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`expressions`](#columnproperty-comparator-expressions) | অ্যাট্রিবিউট | এই অ্যাট্রিবিউটের সব কলাম এক্সপ্রেশনের তালিকা (inheritance-এ একাধিক)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ColumnProperty.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`QueryableAttribute` থেকে:** [`adapt_to_entity()`](operators.md#queryableattribute-adapt-to-entity) · [`adapter`](operators.md#queryableattribute-adapter) · [`and_()`](operators.md#queryableattribute-and-) · [`any()`](operators.md#queryableattribute-any) · [`any_op()`](operators.md#queryableattribute-any-op) · [`has()`](operators.md#queryableattribute-has) · [`has_op()`](operators.md#queryableattribute-has-op) · [`info`](operators.md#queryableattribute-info) · [`of_type()`](operators.md#queryableattribute-of-type) · [`of_type_op()`](operators.md#queryableattribute-of-type-op) · [`prop`](operators.md#queryableattribute-prop) · [`property`](operators.md#queryableattribute-property)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `ColumnProperty.Comparator.expressions` { #columnproperty-comparator-expressions }

**ধরন:** অ্যাট্রিবিউট

এই অ্যাট্রিবিউটের সব কলাম এক্সপ্রেশনের তালিকা (inheritance-এ একাধিক)।

**উদাহরণ:**

```python
print([str(e) for e in User.name_len.comparator.expressions])   # ['length(users.name)']
```

## `MappedSQLExpression` { #mappedsqlexpression }

```python
from sqlalchemy.orm import MappedSQLExpression
```

(২.০) `column_property()` (আর `query_expression()`) declarative-এ যা বানায়: `ColumnProperty`-এর declarative রূপ, যেটি `Mapped[int]` annotation-এর সাথে খাপ খায়। ম্যাপিংয়ের পরও এই ক্লাসই থাকে।

**উদাহরণ:**

```python
p = m.attrs.name_len
print(type(p).__name__, isinstance(p, ColumnProperty), session.get(User, 1).name_len)   # MappedSQLExpression True 4
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mappedsqlexpression-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MappedSQLExpression`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnProperty` থেকে:** [`Comparator`](#columnproperty-Comparator) · [`active_history`](#columnproperty-active-history) · [`columns`](#columnproperty-columns) · [`columns_to_assign`](#columnproperty-columns-to-assign) · [`comparator_factory`](#columnproperty-comparator-factory) · [`copy()`](#columnproperty-copy) · [`declarative_scan()`](#columnproperty-declarative-scan) · [`deferred`](#columnproperty-deferred) · [`expire_on_flush`](#columnproperty-expire-on-flush) · [`expression`](#columnproperty-expression) · [`found_in_pep593_annotated()`](#columnproperty-found-in-pep593-annotated) · [`group`](#columnproperty-group) · [`instrument`](#columnproperty-instrument) · [`logger`](#columnproperty-logger) · [`logging_name`](#columnproperty-logging-name) · [`mapper_property_to_assign`](#columnproperty-mapper-property-to-assign) · [`raiseload`](#columnproperty-raiseload) · [`strategy`](#columnproperty-strategy) · [`strategy_for()`](#columnproperty-strategy-for) · [`strategy_key`](#columnproperty-strategy-key) · [`strategy_wildcard_key`](#columnproperty-strategy-wildcard-key)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

## `MappedColumn` { #mappedcolumn }

```python
from sqlalchemy.orm import MappedColumn
```

`mapped_column()` যে অবজেক্ট ফেরত দেয়: declarative ক্লাস স্ক্যান হওয়ার **আগের** অবস্থা, ভেতরে একটি `Column` আর ORM-এর অপশন। ম্যাপিং শেষে এটি একটি `ColumnProperty` বানিয়ে দেয়; তাই `inspect(User).attrs.name`-এ `ColumnProperty` পাবেন, `MappedColumn` নয়।

**উদাহরণ:**

```python
mc = mapped_column(String(10), deferred=True, deferred_group="details")
print(type(mc).__name__, mc.column.type, mc.deferred, mc.deferred_group)   # MappedColumn VARCHAR(10) True details
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mappedcolumn-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`active_history`](#mappedcolumn-active-history) | অ্যাট্রিবিউট | `active_history=` অপশন। |
| [`column`](#mappedcolumn-column) | অ্যাট্রিবিউট | ভেতরের Core `Column` (নাম/টেবিল এখনো নাও বসতে পারে)। |
| [`columns_to_assign`](#mappedcolumn-columns-to-assign) | প্রপার্টি (internal) | টেবিলে যোগ করার কলাম (আর তার `sort_order`)। |
| [`declarative_scan()`](#mappedcolumn-declarative-scan) | মেথড (internal) | ক্লাস স্ক্যানের সময় নাম, টাইপ (annotation থেকে) ইত্যাদি বসায়। |
| [`declarative_scan_for_composite()`](#mappedcolumn-declarative-scan-for-composite) | মেথড (internal) | `composite()`-এর ভেতরে থাকলে dataclass-এর ফিল্ড-টাইপ থেকে টাইপ বসায়। |
| [`deferred`](#mappedcolumn-deferred) | অ্যাট্রিবিউট | `deferred=` অপশন। |
| [`deferred_group`](#mappedcolumn-deferred-group) | অ্যাট্রিবিউট | `deferred_group=` অপশন। |
| [`deferred_raiseload`](#mappedcolumn-deferred-raiseload) | অ্যাট্রিবিউট | `deferred_raiseload=` অপশন। |
| [`foreign_keys`](#mappedcolumn-foreign-keys) | অ্যাট্রিবিউট | ভেতরের কলামের `ForeignKey`-গুলোর set। |
| [`found_in_pep593_annotated()`](#mappedcolumn-found-in-pep593-annotated) | মেথড (internal) | `Annotated[int, mapped_column(...)]`-এ পাওয়া গেলে প্রতিটি ব্যবহারের জন্য আলাদা কপি দেয়। |
| [`mapper_property_to_assign`](#mappedcolumn-mapper-property-to-assign) | প্রপার্টি (internal) | mapper-এ বসানোর `ColumnProperty` (প্রয়োজনে তৈরি করে)। |
| [`name`](#mappedcolumn-name) | প্রপার্টি | কলামের নাম (স্ক্যানের আগে `None`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MappedColumn`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

///

### `MappedColumn.active_history` { #mappedcolumn-active-history }

**ধরন:** অ্যাট্রিবিউট

`active_history=` অপশন।

**উদাহরণ:**

```python
print(mapped_column(active_history=True).active_history)   # True
```

### `MappedColumn.column` { #mappedcolumn-column }

**ধরন:** অ্যাট্রিবিউট

ভেতরের Core `Column` (নাম/টেবিল এখনো নাও বসতে পারে)।

**উদাহরণ:**

```python
print(repr(mapped_column(String(10), nullable=False).column))   # Column(None, String(length=10), table=None, nullable=False)
```

### `MappedColumn.columns_to_assign` { #mappedcolumn-columns-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

টেবিলে যোগ করার কলাম (আর তার `sort_order`)।

**উদাহরণ:**

```python
print(mapped_column(Integer).columns_to_assign)   # [(Column(None, Integer(), table=None), 0)]
```

### `MappedColumn.declarative_scan()` { #mappedcolumn-declarative-scan }

```python
MappedColumn.declarative_scan(decl_scan, registry, originating_module, key, mapped_container, annotation, extracted_mapped_annotation, is_dataclass_field)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস স্ক্যানের সময় নাম, টাইপ (annotation থেকে) ইত্যাদি বসায়।

**উদাহরণ:**

```python
print(callable(MappedColumn.declarative_scan))   # True
```

### `MappedColumn.declarative_scan_for_composite()` { #mappedcolumn-declarative-scan-for-composite }

```python
MappedColumn.declarative_scan_for_composite(decl_scan, registry, originating_module, key, param_name, param_annotation)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`composite()`-এর ভেতরে থাকলে dataclass-এর ফিল্ড-টাইপ থেকে টাইপ বসায়।

**উদাহরণ:**

```python
print(callable(MappedColumn.declarative_scan_for_composite))   # True
```

### `MappedColumn.deferred` { #mappedcolumn-deferred }

**ধরন:** অ্যাট্রিবিউট

`deferred=` অপশন।

**উদাহরণ:**

```python
print(mapped_column(deferred=True).deferred)   # True
```

### `MappedColumn.deferred_group` { #mappedcolumn-deferred-group }

**ধরন:** অ্যাট্রিবিউট

`deferred_group=` অপশন।

**উদাহরণ:**

```python
print(mapped_column(deferred_group="g").deferred_group)   # g
```

### `MappedColumn.deferred_raiseload` { #mappedcolumn-deferred-raiseload }

**ধরন:** অ্যাট্রিবিউট

`deferred_raiseload=` অপশন।

**উদাহরণ:**

```python
print(mapped_column(deferred_raiseload=True).deferred_raiseload)   # True
```

### `MappedColumn.foreign_keys` { #mappedcolumn-foreign-keys }

**ধরন:** অ্যাট্রিবিউট

ভেতরের কলামের `ForeignKey`-গুলোর set।

**উদাহরণ:**

```python
print(mapped_column(ForeignKey("users.id")).foreign_keys)   # {ForeignKey('users.id')}
```

### `MappedColumn.found_in_pep593_annotated()` { #mappedcolumn-found-in-pep593-annotated }

```python
MappedColumn.found_in_pep593_annotated()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Annotated[int, mapped_column(...)]`-এ পাওয়া গেলে প্রতিটি ব্যবহারের জন্য আলাদা কপি দেয়।

**উদাহরণ:**

```python
mc = mapped_column(String(10))
print(mc.found_in_pep593_annotated() is not mc)   # True
```

### `MappedColumn.mapper_property_to_assign` { #mappedcolumn-mapper-property-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

mapper-এ বসানোর `ColumnProperty` (প্রয়োজনে তৈরি করে)।

**উদাহরণ:**

```python
print(type(mapped_column(deferred=True).mapper_property_to_assign).__name__)   # ColumnProperty
```

### `MappedColumn.name` { #mappedcolumn-name }

**ধরন:** প্রপার্টি

কলামের নাম (স্ক্যানের আগে `None`)।

**উদাহরণ:**

```python
print(mapped_column("user_name").name, mapped_column().name)   # user_name None
```

## `SQLORMExpression` { #sqlormexpression }

```python
from sqlalchemy.orm import SQLORMExpression
```

(২.০) টাইপ-হিন্টের জন্য: "ORM-এর এমন কিছু যা SQL এক্সপ্রেশনের মতো আচরণ করে" (`User.name`, hybrid, `column_property` …)। নিজের ফাংশনে এমন আর্গুমেন্ট নিতে `def f(col: SQLORMExpression[str])`। কলামের সব অপারেটর আছে।

**উদাহরণ:**

```python
def starts_with(col: SQLORMExpression[str], prefix: str):
    return col.startswith(prefix)
print(starts_with(User.name, "র"))   # users.name LIKE :name_1 || '%'
print(isinstance(User.name, SQLORMExpression))   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sqlormexpression-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SQLORMExpression`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

///

## `ORMDescriptor` { #ormdescriptor }

```python
from sqlalchemy.orm import ORMDescriptor
```

(২.০) টাইপ-হিন্টের জন্য: ক্লাস-লেভেলে SQL এক্সপ্রেশন দেয় এমন যেকোনো Python descriptor (`InstrumentedAttribute`, `hybrid_property`, `association_proxy`)। `mapper.all_orm_descriptors`-এর মানগুলোর টাইপ।

**উদাহরণ:**

```python
d = inspect(User).all_orm_descriptors
print(sorted(d.keys()))   # ['addresses', 'bio', 'display_name', 'id', 'name', 'name_len']
```

## সম্পর্ক (relationship) property { #relationshipproperty-group }

## `RelationshipProperty` { #relationshipproperty }

```python
from sqlalchemy.orm import RelationshipProperty
```

একটি `relationship()`-এর ম্যাপিংয়ের পরের রূপ: কোন ক্লাসে যায়, কোন দিকে (one-to-many …), কোন কলাম দিয়ে যুক্ত, cascade কী। `inspect(User).relationships` এদের সংগ্রহ। মডেল থেকে স্বয়ংক্রিয়ভাবে API/serializer বানাতে এই তথ্যগুলোই লাগে।

নিচের অ্যাট্রিবিউটগুলো (`direction`, `uselist`, `local_columns` …) mapper কনফিগার হওয়ার **পরে** ঠিকমতো পাওয়া যায় (`configure_mappers()`, বা প্রথম কুয়েরির পর)।

**উদাহরণ:**

```python
for key, r in m.relationships.items():
    print(key, r.direction.name, r.mapper.class_.__name__, r.uselist)   # addresses ONETOMANY Address True
ar = inspect(Address).relationships["user"]
print(ar.direction.name, ar.uselist, ar.back_populates)   # MANYTOONE False addresses
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #relationshipproperty-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`Comparator`](#relationshipproperty-Comparator) | অ্যাট্রিবিউট | relationship অ্যাট্রিবিউটের comparator; নিচে [`RelationshipProperty.Comparator`](#relationshipproperty-comparator)। |
| [`argument`](#relationshipproperty-argument) | অ্যাট্রিবিউট | `relationship()`-এর প্রথম আর্গুমেন্ট যেমন দেওয়া হয়েছিল (ক্লাস, স্ট্রিং নাম, বা annotation থেকে পাওয়া নাম)। |
| [`back_populates`](#relationshipproperty-back-populates) | প্রপার্টি | `back_populates=`-এ দেওয়া উল্টো দিকের অ্যাট্রিবিউটের নাম, নইলে `None`। |
| [`collection_class`](#relationshipproperty-collection-class) | অ্যাট্রিবিউট | collection-এর ধরন (`list`, `set`, dict factory …); many-to-one-এ `None`। |
| [`declarative_scan()`](#relationshipproperty-declarative-scan) | মেথড (internal) | ক্লাস স্ক্যানের সময় annotation (`Mapped[list["Address"]]`) থেকে টার্গেট আর collection ধরন বের করে। |
| [`direction`](#relationshipproperty-direction) | অ্যাট্রিবিউট | সম্পর্কের দিক: [`RelationshipDirection`](#relationshipdirection)-এর `ONETOMANY`, `MANYTOONE` বা `MANYTOMANY`। |
| [`entity`](#relationshipproperty-entity) | প্রপার্টি | টার্গেট entity (ক্লাসের Mapper, বা `aliased()` হলে তার `AliasedInsp`)। |
| [`found_in_pep593_annotated()`](#relationshipproperty-found-in-pep593-annotated) | মেথড (internal) | `Annotated[...]`-এর ভেতরে পাওয়া গেলে কপি দেয়। |
| [`lazy`](#relationshipproperty-lazy) | অ্যাট্রিবিউট | লোডিং ধরন: `"select"` (ডিফল্ট lazy), `"selectin"`, `"joined"`, `"raise"`, `"write_only"`, `"dynamic"` … |
| [`local_columns`](#relationshipproperty-local-columns) | অ্যাট্রিবিউট | এই (মালিক) দিকের যে কলামগুলো join-এ অংশ নেয়। |
| [`local_remote_pairs`](#relationshipproperty-local-remote-pairs) | অ্যাট্রিবিউট | join-এ (এই দিকের কলাম, অন্য দিকের কলাম) জোড়াগুলো। |
| [`logger`](#relationshipproperty-logger) | অ্যাট্রিবিউট (internal) | এই ক্লাসের `logging.Logger`। |
| [`logging_name`](#relationshipproperty-logging-name) | অ্যাট্রিবিউট (internal) | লগে বাড়তি নাম। |
| [`mapper`](#relationshipproperty-mapper) | প্রপার্টি | টার্গেট ক্লাসের `Mapper`। |
| [`order_by`](#relationshipproperty-order-by) | অ্যাট্রিবিউট | `order_by=`-এ দেওয়া ক্রম, নইলে `False`। |
| [`passive_deletes`](#relationshipproperty-passive-deletes) | অ্যাট্রিবিউট | `passive_deletes=` (ডেটাবেসের `ON DELETE CASCADE`-এর ওপর ভরসা করবে কি না)। |
| [`post_update`](#relationshipproperty-post-update) | অ্যাট্রিবিউট | `post_update=` (চক্রাকার নির্ভরতা ভাঙতে আলাদা UPDATE)। |
| [`primaryjoin`](#relationshipproperty-primaryjoin) | অ্যাট্রিবিউট | join শর্ত (SQL এক্সপ্রেশন), নিজে থেকে FK দেখে বানানো বা `primaryjoin=` দেওয়া। |
| [`remote_side`](#relationshipproperty-remote-side) | অ্যাট্রিবিউট | অন্য দিকের যে কলামগুলো join-এ অংশ নেয় (self-referential-এ `remote_side=` দিয়ে ঠিক করা হয়)। |
| [`secondary`](#relationshipproperty-secondary) | অ্যাট্রিবিউট | many-to-many-এর মাঝের (association) টেবিল, নইলে `None`। |
| [`secondaryjoin`](#relationshipproperty-secondaryjoin) | অ্যাট্রিবিউট | many-to-many-এ মাঝের টেবিল থেকে টার্গেটে join শর্ত, নইলে `None`। |
| [`strategy`](#relationshipproperty-strategy) | অ্যাট্রিবিউট (internal) | বর্তমান লোডিং strategy অবজেক্ট। |
| [`strategy_for()`](#relationshipproperty-strategy-for) | ক্লাস মেথড (internal) | (ক্লাস মেথড) strategy নথিভুক্ত করার ডেকোরেটর। |
| [`strategy_key`](#relationshipproperty-strategy-key) | অ্যাট্রিবিউট (internal) | বর্তমান strategy-র key। |
| [`strategy_wildcard_key`](#relationshipproperty-strategy-wildcard-key) | অ্যাট্রিবিউট (internal) | wildcard লোডার অপশনের key। |
| [`synchronize_pairs`](#relationshipproperty-synchronize-pairs) | অ্যাট্রিবিউট | flush-এ কোন কলামের মান কোন কলামে কপি হবে (যেমন `users.id` → `addresses.user_id`)। |
| [`target`](#relationshipproperty-target) | অ্যাট্রিবিউট | টার্গেট টেবিল (বা selectable)। |
| [`uselist`](#relationshipproperty-uselist) | অ্যাট্রিবিউট | `True` হলে collection (list ইত্যাদি), `False` হলে একটি অবজেক্ট (many-to-one বা one-to-one)। |
| [`viewonly`](#relationshipproperty-viewonly) | অ্যাট্রিবিউট | `viewonly=True` হলে শুধু পড়ার জন্য: flush-এ এই relationship থেকে কিছু লেখা হয় না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `RelationshipProperty`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

### `RelationshipProperty.Comparator` { #relationshipproperty-Comparator }

**ধরন:** অ্যাট্রিবিউট

relationship অ্যাট্রিবিউটের comparator; নিচে [`RelationshipProperty.Comparator`](#relationshipproperty-comparator)।

**উদাহরণ:**

```python
print(type(User.addresses.comparator).__qualname__)   # RelationshipProperty.Comparator
```

### `RelationshipProperty.argument` { #relationshipproperty-argument }

**ধরন:** অ্যাট্রিবিউট

`relationship()`-এর প্রথম আর্গুমেন্ট যেমন দেওয়া হয়েছিল (ক্লাস, স্ট্রিং নাম, বা annotation থেকে পাওয়া নাম)।

**উদাহরণ:**

```python
print(rel.argument)   # Address
```

### `RelationshipProperty.back_populates` { #relationshipproperty-back-populates }

**ধরন:** প্রপার্টি

`back_populates=`-এ দেওয়া উল্টো দিকের অ্যাট্রিবিউটের নাম, নইলে `None`।

**উদাহরণ:**

```python
print(rel.back_populates)   # user
```

### `RelationshipProperty.collection_class` { #relationshipproperty-collection-class }

**ধরন:** অ্যাট্রিবিউট

collection-এর ধরন (`list`, `set`, dict factory …); many-to-one-এ `None`।

**উদাহরণ:**

```python
print(rel.collection_class, inspect(Address).relationships["user"].collection_class)   # <class 'list'> None
```

### `RelationshipProperty.declarative_scan()` { #relationshipproperty-declarative-scan }

```python
RelationshipProperty.declarative_scan(decl_scan, registry, originating_module, key, mapped_container, annotation, extracted_mapped_annotation, is_dataclass_field)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস স্ক্যানের সময় annotation (`Mapped[list["Address"]]`) থেকে টার্গেট আর collection ধরন বের করে।

**উদাহরণ:**

```python
print(callable(RelationshipProperty.declarative_scan))   # True
```

### `RelationshipProperty.direction` { #relationshipproperty-direction }

**ধরন:** অ্যাট্রিবিউট

সম্পর্কের দিক: [`RelationshipDirection`](#relationshipdirection)-এর `ONETOMANY`, `MANYTOONE` বা `MANYTOMANY`।

**উদাহরণ:**

```python
print(rel.direction, inspect(Address).relationships["user"].direction)   # RelationshipDirection.ONETOMANY RelationshipDirection.MANYTOONE
```

### `RelationshipProperty.entity` { #relationshipproperty-entity }

**ধরন:** প্রপার্টি

টার্গেট entity (ক্লাসের Mapper, বা `aliased()` হলে তার `AliasedInsp`)।

**উদাহরণ:**

```python
print(rel.entity)   # Mapper[Address(addresses)]
```

### `RelationshipProperty.found_in_pep593_annotated()` { #relationshipproperty-found-in-pep593-annotated }

```python
RelationshipProperty.found_in_pep593_annotated()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Annotated[...]`-এর ভেতরে পাওয়া গেলে কপি দেয়।

**উদাহরণ:**

```python
print(callable(RelationshipProperty.found_in_pep593_annotated))   # True
```

### `RelationshipProperty.lazy` { #relationshipproperty-lazy }

**ধরন:** অ্যাট্রিবিউট

লোডিং ধরন: `"select"` (ডিফল্ট lazy), `"selectin"`, `"joined"`, `"raise"`, `"write_only"`, `"dynamic"` …

**উদাহরণ:**

```python
print(rel.lazy)   # select
```

### `RelationshipProperty.local_columns` { #relationshipproperty-local-columns }

**ধরন:** অ্যাট্রিবিউট

এই (মালিক) দিকের যে কলামগুলো join-এ অংশ নেয়।

**উদাহরণ:**

```python
print([c.name for c in rel.local_columns])   # ['id']
```

### `RelationshipProperty.local_remote_pairs` { #relationshipproperty-local-remote-pairs }

**ধরন:** অ্যাট্রিবিউট

join-এ (এই দিকের কলাম, অন্য দিকের কলাম) জোড়াগুলো।

**উদাহরণ:**

```python
print([(a.name, b.table.name + "." + b.name) for a, b in rel.local_remote_pairs])   # [('id', 'addresses.user_id')]
```

### `RelationshipProperty.logger` { #relationshipproperty-logger }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই ক্লাসের `logging.Logger`।

**উদাহরণ:**

```python
print(RelationshipProperty.logger.name)   # sqlalchemy.orm.relationships.RelationshipProperty
```

### `RelationshipProperty.logging_name` { #relationshipproperty-logging-name }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লগে বাড়তি নাম।

**উদাহরণ:**

```python
print(RelationshipProperty.logging_name)   # None
```

### `RelationshipProperty.mapper` { #relationshipproperty-mapper }

**ধরন:** প্রপার্টি

টার্গেট ক্লাসের `Mapper`।

**উদাহরণ:**

```python
print(rel.mapper.class_.__name__)   # Address
```

### `RelationshipProperty.order_by` { #relationshipproperty-order-by }

**ধরন:** অ্যাট্রিবিউট

`order_by=`-এ দেওয়া ক্রম, নইলে `False`।

**উদাহরণ:**

```python
print(rel.order_by)   # False
```

### `RelationshipProperty.passive_deletes` { #relationshipproperty-passive-deletes }

**ধরন:** অ্যাট্রিবিউট

`passive_deletes=` (ডেটাবেসের `ON DELETE CASCADE`-এর ওপর ভরসা করবে কি না)।

**উদাহরণ:**

```python
print(rel.passive_deletes)   # False
```

### `RelationshipProperty.post_update` { #relationshipproperty-post-update }

**ধরন:** অ্যাট্রিবিউট

`post_update=` (চক্রাকার নির্ভরতা ভাঙতে আলাদা UPDATE)।

**উদাহরণ:**

```python
print(rel.post_update)   # False
```

### `RelationshipProperty.primaryjoin` { #relationshipproperty-primaryjoin }

**ধরন:** অ্যাট্রিবিউট

join শর্ত (SQL এক্সপ্রেশন), নিজে থেকে FK দেখে বানানো বা `primaryjoin=` দেওয়া।

**উদাহরণ:**

```python
print(rel.primaryjoin)   # users.id = addresses.user_id
```

### `RelationshipProperty.remote_side` { #relationshipproperty-remote-side }

**ধরন:** অ্যাট্রিবিউট

অন্য দিকের যে কলামগুলো join-এ অংশ নেয় (self-referential-এ `remote_side=` দিয়ে ঠিক করা হয়)।

**উদাহরণ:**

```python
print([c.name for c in rel.remote_side])   # ['user_id']
```

### `RelationshipProperty.secondary` { #relationshipproperty-secondary }

**ধরন:** অ্যাট্রিবিউট

many-to-many-এর মাঝের (association) টেবিল, নইলে `None`।

**উদাহরণ:**

```python
print(rel.secondary)   # None
```

### `RelationshipProperty.secondaryjoin` { #relationshipproperty-secondaryjoin }

**ধরন:** অ্যাট্রিবিউট

many-to-many-এ মাঝের টেবিল থেকে টার্গেটে join শর্ত, নইলে `None`।

**উদাহরণ:**

```python
print(rel.secondaryjoin)   # None
```

### `RelationshipProperty.strategy` { #relationshipproperty-strategy }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বর্তমান লোডিং strategy অবজেক্ট।

**উদাহরণ:**

```python
print(type(rel.strategy).__name__)   # _LazyLoader
```

### `RelationshipProperty.strategy_for()` { #relationshipproperty-strategy-for }

```python
RelationshipProperty.strategy_for(**kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) strategy নথিভুক্ত করার ডেকোরেটর।

**উদাহরণ:**

```python
print(callable(RelationshipProperty.strategy_for))   # True
```

### `RelationshipProperty.strategy_key` { #relationshipproperty-strategy-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বর্তমান strategy-র key।

**উদাহরণ:**

```python
print(rel.strategy_key)   # (('lazy', 'select'),)
```

### `RelationshipProperty.strategy_wildcard_key` { #relationshipproperty-strategy-wildcard-key }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

wildcard লোডার অপশনের key।

**উদাহরণ:**

```python
print(RelationshipProperty.strategy_wildcard_key)   # relationship
```

### `RelationshipProperty.synchronize_pairs` { #relationshipproperty-synchronize-pairs }

**ধরন:** অ্যাট্রিবিউট

flush-এ কোন কলামের মান কোন কলামে কপি হবে (যেমন `users.id` → `addresses.user_id`)।

**উদাহরণ:**

```python
print([(a.name, b.name) for a, b in rel.synchronize_pairs])   # [('id', 'user_id')]
```

### `RelationshipProperty.target` { #relationshipproperty-target }

**ধরন:** অ্যাট্রিবিউট

টার্গেট টেবিল (বা selectable)।

**উদাহরণ:**

```python
print(rel.target)   # addresses
```

### `RelationshipProperty.uselist` { #relationshipproperty-uselist }

**ধরন:** অ্যাট্রিবিউট

`True` হলে collection (list ইত্যাদি), `False` হলে একটি অবজেক্ট (many-to-one বা one-to-one)।

**উদাহরণ:**

```python
print(rel.uselist, inspect(Address).relationships["user"].uselist)   # True False
```

### `RelationshipProperty.viewonly` { #relationshipproperty-viewonly }

**ধরন:** অ্যাট্রিবিউট

`viewonly=True` হলে শুধু পড়ার জন্য: flush-এ এই relationship থেকে কিছু লেখা হয় না।

**উদাহরণ:**

```python
print(rel.viewonly)   # False
```

## `RelationshipProperty.Comparator` { #relationshipproperty-comparator }

```python
from sqlalchemy.orm import RelationshipProperty
```

relationship অ্যাট্রিবিউটে (`User.addresses`, `Address.user`) কুয়েরির অপারেটর। কলামের মতো নয়; এগুলো **অবজেক্ট/সম্পর্ক** নিয়ে কাজ করে:

* `Address.user == some_user`: many-to-one-এ FK তুলনা (`addresses.user_id = :id`)। `== None` মানে "কেউ নেই"।
* `User.addresses.contains(addr)`: one-to-many/many-to-many-এ "এই অবজেক্টটি collection-এ আছে"।
* `User.addresses.any(শর্ত)`: collection-এ শর্ত মেলে এমন অন্তত একটি (`EXISTS`)।
* `Address.user.has(শর্ত)`: many-to-one-এর অবজেক্ট শর্ত মেলে (`EXISTS`)।
* `of_type()`, `and_()`: inheritance-এ subclass বেছে নেওয়া, join-এর ON-এ শর্ত যোগ।

বিস্তারিত (উদাহরণসহ) [QueryableAttribute](operators.md#queryableattribute)-এ; এখানে কয়েকটি relationship-বিশেষ উদাহরণ।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).where(User.addresses.any(Address.email.like("%work%")))).all())   # ['রহিম']
print(session.scalars(select(User.name).where(~User.addresses.any())).all())   # ['করিম']
u = session.get(User, 1)
print(session.scalars(select(Address.email).where(Address.user == u).order_by(Address.id)).all())   # ['rahim@example.com', 'rahim@work.com']
a1 = session.get(Address, 1)
print(session.scalars(select(User.name).where(User.addresses.contains(a1))).all())   # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #relationshipproperty-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`entity`](#relationshipproperty-comparator-entity) | অ্যাট্রিবিউট | টার্গেট entity (aliased হলে তার রূপ)। |
| [`mapper`](#relationshipproperty-comparator-mapper) | অ্যাট্রিবিউট | টার্গেট ক্লাসের Mapper। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `RelationshipProperty.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`QueryableAttribute` থেকে:** [`adapt_to_entity()`](operators.md#queryableattribute-adapt-to-entity) · [`adapter`](operators.md#queryableattribute-adapter) · [`and_()`](operators.md#queryableattribute-and-) · [`any()`](operators.md#queryableattribute-any) · [`any_op()`](operators.md#queryableattribute-any-op) · [`has()`](operators.md#queryableattribute-has) · [`has_op()`](operators.md#queryableattribute-has-op) · [`info`](operators.md#queryableattribute-info) · [`of_type()`](operators.md#queryableattribute-of-type) · [`of_type_op()`](operators.md#queryableattribute-of-type-op) · [`prop`](operators.md#queryableattribute-prop) · [`property`](operators.md#queryableattribute-property)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `RelationshipProperty.Comparator.entity` { #relationshipproperty-comparator-entity }

**ধরন:** অ্যাট্রিবিউট

টার্গেট entity (aliased হলে তার রূপ)।

**উদাহরণ:**

```python
print(User.addresses.comparator.entity)   # Mapper[Address(addresses)]
```

### `RelationshipProperty.Comparator.mapper` { #relationshipproperty-comparator-mapper }

**ধরন:** অ্যাট্রিবিউট

টার্গেট ক্লাসের Mapper।

**উদাহরণ:**

```python
print(Address.user.comparator.mapper)   # Mapper[User(users)]
```

## `Relationship` { #relationship }

```python
from sqlalchemy.orm import Relationship
```

(২.০) `RelationshipProperty`-এর declarative-উপযোগী রূপ (`Mapped[...]` annotation-এর সাথে খাপ খায়)। `relationship()` আসলে এর একটি ভেতরের subclass `_RelationshipDeclared` ফেরত দেয়; তাই টাইপ চিনতে নাম নয়, `isinstance(x, Relationship)` ব্যবহার করুন। সব সদস্য `RelationshipProperty`-এর।

**উদাহরণ:**

```python
r = relationship("Address")
print(type(r).__name__, isinstance(r, Relationship), isinstance(rel, RelationshipProperty))   # _RelationshipDeclared True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #relationship-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Relationship`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`RelationshipProperty` থেকে:** [`Comparator`](#relationshipproperty-Comparator) · [`back_populates`](#relationshipproperty-back-populates) · [`declarative_scan()`](#relationshipproperty-declarative-scan) · [`entity`](#relationshipproperty-entity) · [`found_in_pep593_annotated()`](#relationshipproperty-found-in-pep593-annotated) · [`logger`](#relationshipproperty-logger) · [`logging_name`](#relationshipproperty-logging-name) · [`mapper`](#relationshipproperty-mapper) · [`strategy`](#relationshipproperty-strategy) · [`strategy_for()`](#relationshipproperty-strategy-for) · [`strategy_key`](#relationshipproperty-strategy-key) · [`strategy_wildcard_key`](#relationshipproperty-strategy-wildcard-key)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

## `RelationshipDirection` { #relationshipdirection }

```python
from sqlalchemy.orm import RelationshipDirection
```

`RelationshipProperty.direction`-এর মান: সম্পর্কটি কোন দিকের।

**উদাহরণ:**

```python
print([r.direction.name for r in inspect(Address).relationships], [r.direction.name for r in m.relationships])   # ['MANYTOONE'] ['ONETOMANY']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #relationshipdirection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`MANYTOMANY`](#relationshipdirection-MANYTOMANY) | অ্যাট্রিবিউট | মাঝের টেবিল (`secondary`) দিয়ে অনেক-থেকে-অনেক, যেমন ছাত্র ↔ কোর্স। |
| [`MANYTOONE`](#relationshipdirection-MANYTOONE) | অ্যাট্রিবিউট | অনেক-থেকে-এক: FK **এই** টেবিলে, যেমন `Address.user`। |
| [`ONETOMANY`](#relationshipdirection-ONETOMANY) | অ্যাট্রিবিউট | এক-থেকে-অনেক: FK **অন্য** টেবিলে, যেমন `User.addresses`। |

### `RelationshipDirection.MANYTOMANY` { #relationshipdirection-MANYTOMANY }

**ধরন:** অ্যাট্রিবিউট

মাঝের টেবিল (`secondary`) দিয়ে অনেক-থেকে-অনেক, যেমন ছাত্র ↔ কোর্স।

**উদাহরণ:**

```python
print(RelationshipDirection.MANYTOMANY.value)   # 3
```

### `RelationshipDirection.MANYTOONE` { #relationshipdirection-MANYTOONE }

**ধরন:** অ্যাট্রিবিউট

অনেক-থেকে-এক: FK **এই** টেবিলে, যেমন `Address.user`।

**উদাহরণ:**

```python
print(RelationshipDirection.MANYTOONE.value)   # 2
```

### `RelationshipDirection.ONETOMANY` { #relationshipdirection-ONETOMANY }

**ধরন:** অ্যাট্রিবিউট

এক-থেকে-অনেক: FK **অন্য** টেবিলে, যেমন `User.addresses`।

**উদাহরণ:**

```python
print(RelationshipDirection.ONETOMANY.value)   # 1
```

## `CascadeOptions` { #cascadeoptions }

```python
from sqlalchemy.orm.util import CascadeOptions
```

`relationship(cascade="...")` স্ট্রিং থেকে তৈরি নিয়মের সেট (একটি `frozenset`)। `"all"` মানে `save-update, merge, refresh-expire, expunge, delete`; সাথে আলাদা করে `delete-orphan`। প্রতিটি নিয়ম বুলিয়ান অ্যাট্রিবিউট হিসেবেও পড়া যায়।

**উদাহরণ:**

```python
c = CascadeOptions("all, delete-orphan")
print(sorted(c))   # ['delete', 'delete-orphan', 'expunge', 'merge', 'refresh-expire', 'save-update']
print(rel.cascade.delete_orphan, inspect(Address).relationships["user"].cascade.delete)   # True False
```

**Python `frozenset`-এর সব মেথড** (`copy()`, `difference()`, `intersection()`, `isdisjoint()`, `issubset()`, `issuperset()`, `symmetric_difference()`, `union()`) সাধারণ `frozenset`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #cascadeoptions-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`delete`](#cascadeoptions-delete) | অ্যাট্রিবিউট | মালিক মুছলে সন্তানও মুছবে। |
| [`delete_orphan`](#cascadeoptions-delete-orphan) | অ্যাট্রিবিউট | collection থেকে সরানো (অভিভাবকহীন) সন্তান মুছে যাবে। |
| [`expunge`](#cascadeoptions-expunge) | অ্যাট্রিবিউট | মালিক `expunge()` হলে সন্তানও সেশন থেকে সরবে। |
| [`from_string()`](#cascadeoptions-from-string) | ক্লাস মেথড (internal) | (ক্লাস মেথড) স্ট্রিং থেকে বানায় (কনস্ট্রাক্টরের মতো)। |
| [`merge`](#cascadeoptions-merge) | অ্যাট্রিবিউট | মালিক `merge()` হলে সন্তানও merge হবে। |
| [`refresh_expire`](#cascadeoptions-refresh-expire) | অ্যাট্রিবিউট | মালিক `refresh()`/`expire()` হলে সন্তানও। |
| [`save_update`](#cascadeoptions-save-update) | অ্যাট্রিবিউট | মালিক সেশনে `add()` হলে সন্তানও যোগ হবে (ডিফল্ট cascade-এর অংশ)। |

### `CascadeOptions.delete` { #cascadeoptions-delete }

**ধরন:** অ্যাট্রিবিউট

মালিক মুছলে সন্তানও মুছবে।

**উদাহরণ:**

```python
print(CascadeOptions("all").delete, CascadeOptions("save-update").delete)   # True False
```

### `CascadeOptions.delete_orphan` { #cascadeoptions-delete-orphan }

**ধরন:** অ্যাট্রিবিউট

collection থেকে সরানো (অভিভাবকহীন) সন্তান মুছে যাবে।

**উদাহরণ:**

```python
print(CascadeOptions("all, delete-orphan").delete_orphan)   # True
```

### `CascadeOptions.expunge` { #cascadeoptions-expunge }

**ধরন:** অ্যাট্রিবিউট

মালিক `expunge()` হলে সন্তানও সেশন থেকে সরবে।

**উদাহরণ:**

```python
print(CascadeOptions("all").expunge)   # True
```

### `CascadeOptions.from_string()` { #cascadeoptions-from-string }

```python
CascadeOptions.from_string(arg)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) স্ট্রিং থেকে বানায় (কনস্ট্রাক্টরের মতো)।

**উদাহরণ:**

```python
print(CascadeOptions.from_string("merge"))   # CascadeOptions('merge')
```

### `CascadeOptions.merge` { #cascadeoptions-merge }

**ধরন:** অ্যাট্রিবিউট

মালিক `merge()` হলে সন্তানও merge হবে।

**উদাহরণ:**

```python
print(CascadeOptions("save-update, merge").merge)   # True
```

### `CascadeOptions.refresh_expire` { #cascadeoptions-refresh-expire }

**ধরন:** অ্যাট্রিবিউট

মালিক `refresh()`/`expire()` হলে সন্তানও।

**উদাহরণ:**

```python
print(CascadeOptions("all").refresh_expire)   # True
```

### `CascadeOptions.save_update` { #cascadeoptions-save-update }

**ধরন:** অ্যাট্রিবিউট

মালিক সেশনে `add()` হলে সন্তানও যোগ হবে (ডিফল্ট cascade-এর অংশ)।

**উদাহরণ:**

```python
print(CascadeOptions("save-update, merge").save_update)   # True
```

## composite ও synonym { #compositeproperty-group }

## `CompositeProperty` { #compositeproperty }

```python
from sqlalchemy.orm import CompositeProperty
```

কয়েকটি কলাম মিলে একটি Python অবজেক্ট (যেমন `x1`, `y1` → `Point(1, 2)`): `composite()`-এর ম্যাপিংয়ের পরের রূপ।

**উদাহরণ:**

```python
cp = inspect(Shape).attrs.start
print(type(cp).__name__, [c.name for c in cp.columns], session.get(Shape, 1).start)   # Composite ['x1', 'y1'] Point(x=1, y=2)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #compositeproperty-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`Comparator`](#compositeproperty-Comparator) | অ্যাট্রিবিউট | composite অ্যাট্রিবিউটের comparator; নিচে [`CompositeProperty.Comparator`](#compositeproperty-comparator)। |
| [`CompositeBundle`](#compositeproperty-CompositeBundle) | অ্যাট্রিবিউট | `select(Shape.start)` লিখলে কলামগুলো একসাথে এনে একটি `Point` বানানোর `Bundle`। |
| [`columns`](#compositeproperty-columns) | প্রপার্টি | composite-এর কলামগুলো। |
| [`columns_to_assign`](#compositeproperty-columns-to-assign) | প্রপার্টি (internal) | declarative-এ টেবিলে যোগ করার কলাম (ম্যাপিংয়ের পর খালি)। |
| [`declarative_scan()`](#compositeproperty-declarative-scan) | মেথড (internal) | annotation (`Mapped[Point]`) থেকে composite ক্লাস বের করে। |
| [`found_in_pep593_annotated()`](#compositeproperty-found-in-pep593-annotated) | মেথড (internal) | `Annotated[...]`-এ পাওয়া গেলে কপি। |
| [`get_history()`](#compositeproperty-get-history) | মেথড | composite মানের history (আগের আর নতুন `Point`)। |
| [`mapper_property_to_assign`](#compositeproperty-mapper-property-to-assign) | প্রপার্টি (internal) | mapper-এ বসানোর property। |
| [`props`](#compositeproperty-props) | প্রপার্টি | প্রতিটি কলামের `ColumnProperty`। |
| [`uses_objects`](#compositeproperty-uses-objects) | অ্যাট্রিবিউট (internal) | মান অবজেক্ট-ভিত্তিক কি না (composite-এ `False`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CompositeProperty`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

### `CompositeProperty.Comparator` { #compositeproperty-Comparator }

**ধরন:** অ্যাট্রিবিউট

composite অ্যাট্রিবিউটের comparator; নিচে [`CompositeProperty.Comparator`](#compositeproperty-comparator)।

**উদাহরণ:**

```python
print(type(Shape.start.comparator).__qualname__)   # CompositeProperty.Comparator
```

### `CompositeProperty.CompositeBundle` { #compositeproperty-CompositeBundle }

**ধরন:** অ্যাট্রিবিউট

`select(Shape.start)` লিখলে কলামগুলো একসাথে এনে একটি `Point` বানানোর `Bundle`।

**উদাহরণ:**

```python
print(session.execute(select(Shape.start)).scalar())   # Point(x=1, y=2)
```

### `CompositeProperty.columns` { #compositeproperty-columns }

**ধরন:** প্রপার্টি

composite-এর কলামগুলো।

**উদাহরণ:**

```python
print([c.name for c in inspect(Shape).attrs.start.columns])   # ['x1', 'y1']
```

### `CompositeProperty.columns_to_assign` { #compositeproperty-columns-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

declarative-এ টেবিলে যোগ করার কলাম (ম্যাপিংয়ের পর খালি)।

**উদাহরণ:**

```python
print(inspect(Shape).attrs.start.columns_to_assign)   # []
```

### `CompositeProperty.declarative_scan()` { #compositeproperty-declarative-scan }

```python
CompositeProperty.declarative_scan(decl_scan, registry, originating_module, key, mapped_container, annotation, extracted_mapped_annotation, is_dataclass_field)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

annotation (`Mapped[Point]`) থেকে composite ক্লাস বের করে।

**উদাহরণ:**

```python
print(callable(CompositeProperty.declarative_scan))   # True
```

### `CompositeProperty.found_in_pep593_annotated()` { #compositeproperty-found-in-pep593-annotated }

```python
CompositeProperty.found_in_pep593_annotated()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`Annotated[...]`-এ পাওয়া গেলে কপি।

**উদাহরণ:**

```python
print(callable(CompositeProperty.found_in_pep593_annotated))   # True
```

### `CompositeProperty.get_history()` { #compositeproperty-get-history }

```python
CompositeProperty.get_history(state, dict_, passive=symbol('PASSIVE_OFF'))
```

**ধরন:** মেথড

composite মানের history (আগের আর নতুন `Point`)। সাধারণত `inspect(obj).attrs.start.history`।

**উদাহরণ:**

```python
s = session.get(Shape, 1)
s.start = Point(5, 6)
print(inspect(s).attrs.start.history.added)   # [Point(x=5, y=6)]
```

### `CompositeProperty.mapper_property_to_assign` { #compositeproperty-mapper-property-to-assign }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

mapper-এ বসানোর property।

**উদাহরণ:**

```python
cp = inspect(Shape).attrs.start
print(cp.mapper_property_to_assign is cp)   # True
```

### `CompositeProperty.props` { #compositeproperty-props }

**ধরন:** প্রপার্টি

প্রতিটি কলামের `ColumnProperty`।

**উদাহরণ:**

```python
print([p.key for p in inspect(Shape).attrs.start.props])   # ['x1', 'y1']
```

### `CompositeProperty.uses_objects` { #compositeproperty-uses-objects }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মান অবজেক্ট-ভিত্তিক কি না (composite-এ `False`)।

**উদাহরণ:**

```python
print(inspect(Shape).attrs.start.uses_objects)   # False
```

## `CompositeProperty.Comparator` { #compositeproperty-comparator }

```python
from sqlalchemy.orm import CompositeProperty
```

composite অ্যাট্রিবিউটের অপারেটর: `Shape.start == Point(1, 2)` লিখলে প্রতিটি কলাম আলাদাভাবে তুলনা হয় (`x1 = 1 AND y1 = 2`)। `<`, `>` ইত্যাদি চাইলে এটি subclass করে `comparator_factory=` দিন।

**উদাহরণ:**

```python
print(select(Shape.id).where(Shape.start == Point(1, 2)).whereclause)   # shapes.x1 = :x1_1 AND shapes.y1 = :y1_1
print(session.scalars(select(Shape.id).where(Shape.start == Point(1, 2))).all())   # [1]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #compositeproperty-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`clauses`](#compositeproperty-comparator-clauses) | প্রপার্টি | composite-এর কলামগুলো একটি `ClauseList` হিসেবে। |
| [`expression`](#compositeproperty-comparator-expression) | প্রপার্টি | কলামগুলো একসাথে (Bundle) এক্সপ্রেশন হিসেবে; `select(Shape.start)`-এ এটাই বসে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `CompositeProperty.Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`QueryableAttribute` থেকে:** [`adapt_to_entity()`](operators.md#queryableattribute-adapt-to-entity) · [`adapter`](operators.md#queryableattribute-adapter) · [`and_()`](operators.md#queryableattribute-and-) · [`any()`](operators.md#queryableattribute-any) · [`any_op()`](operators.md#queryableattribute-any-op) · [`has()`](operators.md#queryableattribute-has) · [`has_op()`](operators.md#queryableattribute-has-op) · [`info`](operators.md#queryableattribute-info) · [`of_type()`](operators.md#queryableattribute-of-type) · [`of_type_op()`](operators.md#queryableattribute-of-type-op) · [`prop`](operators.md#queryableattribute-prop) · [`property`](operators.md#queryableattribute-property)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `CompositeProperty.Comparator.clauses` { #compositeproperty-comparator-clauses }

**ধরন:** প্রপার্টি

composite-এর কলামগুলো একটি `ClauseList` হিসেবে।

**উদাহরণ:**

```python
print(Shape.start.comparator.clauses)   # shapes.x1, shapes.y1
```

### `CompositeProperty.Comparator.expression` { #compositeproperty-comparator-expression }

**ধরন:** প্রপার্টি

কলামগুলো একসাথে (Bundle) এক্সপ্রেশন হিসেবে; `select(Shape.start)`-এ এটাই বসে।

**উদাহরণ:**

```python
print(type(Shape.start.comparator.expression).__name__)   # CompositeBundle
```

## `Composite` { #composite }

```python
from sqlalchemy.orm import Composite
```

(২.০) `composite()` যা ফেরত দেয়: `CompositeProperty`-এর declarative রূপ। ম্যাপিংয়ের পরও এটাই থাকে।

**উদাহরণ:**

```python
print(isinstance(inspect(Shape).attrs.start, Composite), issubclass(Composite, CompositeProperty))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #composite-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৮৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Composite`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`CompositeProperty` থেকে:** [`Comparator`](#compositeproperty-Comparator) · [`CompositeBundle`](#compositeproperty-CompositeBundle) · [`columns`](#compositeproperty-columns) · [`columns_to_assign`](#compositeproperty-columns-to-assign) · [`declarative_scan()`](#compositeproperty-declarative-scan) · [`found_in_pep593_annotated()`](#compositeproperty-found-in-pep593-annotated) · [`get_history()`](#compositeproperty-get-history) · [`mapper_property_to_assign`](#compositeproperty-mapper-property-to-assign) · [`props`](#compositeproperty-props) · [`uses_objects`](#compositeproperty-uses-objects)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

## `SynonymProperty` { #synonymproperty }

```python
from sqlalchemy.orm import SynonymProperty
```

একটি অ্যাট্রিবিউটের আরেক নাম: `display_name = synonym("name")` দিলে `user.display_name` আর `User.display_name == "x"` দুটোই `name`-এর মতো কাজ করে। কলামের নাম বদলানোর সময় পুরোনো নাম রেখে দিতে কাজে লাগে।

**উদাহরণ:**

```python
sp = m.attrs.display_name
print(type(sp).__name__, sp.name, session.get(User, 1).display_name)   # Synonym name রহিম
print(User.display_name == "করিম")   # users.name = :name_1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #synonymproperty-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get_history()`](#synonymproperty-get-history) | মেথড | মূল অ্যাট্রিবিউটের history (synonym-এর নিজের আলাদা history নেই)। |
| [`name`](#synonymproperty-name) | অ্যাট্রিবিউট | যে অ্যাট্রিবিউটের আরেক নাম। |
| [`uses_objects`](#synonymproperty-uses-objects) | প্রপার্টি (internal) | মূল অ্যাট্রিবিউট অবজেক্ট-ভিত্তিক (relationship) কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `SynonymProperty`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

### `SynonymProperty.get_history()` { #synonymproperty-get-history }

```python
SynonymProperty.get_history(state, dict_, passive=symbol('PASSIVE_OFF'))
```

**ধরন:** মেথড

মূল অ্যাট্রিবিউটের history (synonym-এর নিজের আলাদা history নেই)।

**উদাহরণ:**

```python
u = session.get(User, 1)
u.display_name = "নতুন"
print(inspect(u).attrs.name.history.added)   # ['নতুন']
```

### `SynonymProperty.name` { #synonymproperty-name }

**ধরন:** অ্যাট্রিবিউট

যে অ্যাট্রিবিউটের আরেক নাম।

**উদাহরণ:**

```python
print(m.attrs.display_name.name)   # name
```

### `SynonymProperty.uses_objects` { #synonymproperty-uses-objects }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল অ্যাট্রিবিউট অবজেক্ট-ভিত্তিক (relationship) কি না।

**উদাহরণ:**

```python
print(m.attrs.display_name.uses_objects)   # False
```

## `Synonym` { #synonym }

```python
from sqlalchemy.orm import Synonym
```

(২.০) `synonym()` যা ফেরত দেয়: `SynonymProperty`-এর declarative রূপ।

**উদাহরণ:**

```python
print(isinstance(m.attrs.display_name, Synonym), issubclass(Synonym, SynonymProperty))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #synonym-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৭৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Synonym`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`QueryableAttribute` থেকে:** [`allows_lambda`](operators.md#queryableattribute-allows-lambda) · [`label()`](operators.md#queryableattribute-label) · [`uses_inspection`](operators.md#queryableattribute-uses-inspection)

**`MapperProperty` থেকে:** [`cascade`](#mapperproperty-cascade) · [`cascade_iterator()`](#mapperproperty-cascade-iterator) · [`class_attribute`](#mapperproperty-class-attribute) · [`create_row_processor()`](#mapperproperty-create-row-processor) · [`do_init()`](#mapperproperty-do-init) · [`doc`](#mapperproperty-doc) · [`inherit_cache`](#mapperproperty-inherit-cache) · [`init()`](#mapperproperty-init) · [`instrument_class()`](#mapperproperty-instrument-class) · [`key`](#mapperproperty-key) · [`merge()`](#mapperproperty-merge) · [`parent`](#mapperproperty-parent) · [`path_string()`](#mapperproperty-path-string) · [`post_instrument_class()`](#mapperproperty-post-instrument-class) · [`set_parent()`](#mapperproperty-set-parent) · [`setup()`](#mapperproperty-setup)

**`InspectionAttr` থেকে:** [`extension_type`](#inspectionattr-extension-type) · [`is_aliased_class`](#inspectionattr-is-aliased-class) · [`is_attribute`](#inspectionattr-is-attribute) · [`is_bundle`](#inspectionattr-is-bundle) · [`is_clause_element`](#inspectionattr-is-clause-element) · [`is_instance`](#inspectionattr-is-instance) · [`is_mapper`](#inspectionattr-is-mapper) · [`is_property`](#inspectionattr-is-property) · [`is_selectable`](#inspectionattr-is-selectable)

**`SynonymProperty` থেকে:** [`get_history()`](#synonymproperty-get-history) · [`uses_objects`](#synonymproperty-uses-objects)

**`InspectionAttrInfo` থেকে:** [`info`](#inspectionattrinfo-info)

///

/// tip | মডেল থেকে নিজে থেকে তথ্য বের করা (উদাহরণ: সাধারণ serializer)

```python
def to_dict(obj, depth=1):
    mapper = inspect(obj).mapper
    data = {p.key: getattr(obj, p.key) for p in mapper.column_attrs}
    if depth > 0:
        for r in mapper.relationships:
            value = getattr(obj, r.key)
            if r.uselist:
                data[r.key] = [to_dict(v, depth - 1) for v in value]
            else:
                data[r.key] = to_dict(value, depth - 1) if value is not None else None
    return data
```

`column_attrs` থেকে সাধারণ কলাম, `relationships` থেকে সম্পর্ক, আর `uselist` দেখে list নাকি একক অবজেক্ট। FastAPI-তে সাধারণত Pydantic মডেলই ভালো, কিন্তু admin বা export টুলে এমন জেনেরিক কোড কাজে লাগে।

///
