# আরও ORM API: ২.১-এর unmapped_column, TypeResolve, DictBundle … { #api-orm-extras }

/// note | এই পেজে যা আছে

ORM-এর ছোট ছোট আরও কিছু API, বেশিরভাগই **২.১-এ নতুন**:

* **টেবিলে আছে কিন্তু মডেলে নেই এমন কলাম:** `Unmapped` আর `unmapped_column()` (২.১.৫)।
* **dataclass mixin:** `unmapped_dataclass()` (২.১)।
* **টাইপ:** `as_typed_table()` (২.১), `TypeResolve` (২.১, `RegistryEvents.resolve_type_annotation`-এর আর্গুমেন্ট), `MappedClassProtocol`।
* **কুয়েরি:** `DictBundle` (২.১)।
* **অন্যান্য:** `orm_insert_sentinel()`, `has_inherited_table()`, আর সরিয়ে ফেলা `mapper()`-এর স্থানধারক।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

প্রতিটি উদাহরণ নিজের মডেল বানায় (একটি নতুন `Base`)। চালানো হয় SQLite-এর মেমোরি ডেটাবেসে (`engine`), যাতে উদাহরণগুলো ছোট থাকে; ডেটাবেস-নির্ভর কিছু নেই।

///

## টেবিলে আছে, মডেলে নেই { #unmapped-column-group }

## `unmapped_column()` { #unmapped-column }

```python
from sqlalchemy.orm import Unmapped, unmapped_column
```

```python
unmapped_column(*args, init=False, nullable=<SchemaConst.NULL_UNSPECIFIED: 3>, primary_key=False, autoincrement='auto', use_existing_column=False, name=None, type_=None, index=None, unique=None, info=None, default=_NoArg.NO_ARG, insert_default=_NoArg.NO_ARG, onupdate=None, server_default=None, server_onupdate=None, quote=None, system=False, comment=None, sort_order=_NoArg.NO_ARG, **kw)
```

**ধরন:** ফাংশন

(২.১.৫-এ নতুন) একটি কলাম **টেবিলে** রাখুন (`CREATE TABLE`-এ থাকবে, Alembic autogenerate-ও দেখবে), কিন্তু **Python মডেলে নয়**: `User.legacy_name` অ্যাট্রিবিউট থাকবে না, dataclass-এর `__init__`-এও না। টাইপ ও nullability `Unmapped[...]` annotation থেকে আসে, `Mapped[...]`-এর মতো। ব্যবহার: পুরোনো কলাম যা ডেটাবেসে রাখতে হবে কিন্তু কোডে আর লাগে না, বা শুধু ডেটাবেস-ট্রিগার যে কলাম ব্যবহার করে।

`mapped_column()`-এর ORM/dataclass-বিশেষ প্যারামিটার (`deferred`, `default_factory` …) এখানে নেই, কারণ অ্যাট্রিবিউটটাই নেই।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    legacy_name: Unmapped[str | None] = unmapped_column(String(40))
print([c.name for c in User.__table__.c], hasattr(User, "legacy_name"))   # ['id', 'name', 'legacy_name'] False
print(User.__table__.c.legacy_name.type, User.__table__.c.legacy_name.nullable)   # VARCHAR(40) True
```

### `unmapped_column()`-এর সব প্যারামিটার { #unmapped-column-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `args` | `ForeignKey`, `CheckConstraint` ইত্যাদি অবস্থানগত আর্গুমেন্ট (নাম আর টাইপও প্রথম দুটি অবস্থানে দেওয়া যায়, `mapped_column()`-এর মতো)। |
| `init` | সবসময় `False`: শুধু টাইপ-চেকার (PEP 681) যেন dataclass-এর `__init__`-এ এটি না ধরে। |
| `nullable` | NULL চলবে কি না; না দিলে annotation (<code>str &#124; None</code>) থেকে। |
| `primary_key` | primary key-এর অংশ কি না। মডেলে অ্যাট্রিবিউট নেই বলে mapper-কে কোন কলাম পরিচয় দেবে তা `__mapper_args__ = {"primary_key": [...]}` দিয়ে বলতে হয়। |
| `autoincrement` | `Column.autoincrement`-এর মতো। |
| `use_existing_column` | `mapped_column()`-এর মতো (single-table inheritance-এ)। |
| `name` | ডেটাবেসে কলামের নাম (ডিফল্ট: অ্যাট্রিবিউটের নাম)। |
| `type_` | SQL টাইপ (না দিলে annotation থেকে)। |
| `index` | ইনডেক্স। |
| `unique` | UNIQUE। |
| `info` | `Column.info`। |
| `default` | Core-স্তরের ডিফল্ট (INSERT-এ)। |
| `insert_default` | `default`-এর আরেক নাম। |
| `onupdate` | UPDATE-এ Core ডিফল্ট। |
| `server_default` | ডেটাবেস-স্তরের ডিফল্ট (`DEFAULT ...`)। |
| `server_onupdate` | ডেটাবেস-স্তরের on-update ডিফল্ট। |
| `quote` | নাম quote করবে কি না। |
| `system` | সিস্টেম কলাম (DDL-এ লেখা হবে না)। |
| `comment` | কলামের comment। |
| `sort_order` | টেবিলে কলামের ক্রম। |
| `kw` | `Column`-এর বাকি সব আর্গুমেন্ট (ডায়ালেক্ট-বিশেষসহ)। |

## `Unmapped` { #unmapped }

```python
from sqlalchemy.orm import Unmapped
```

(২.১.৫) `unmapped_column()`-এর সাথে ব্যবহারের annotation: `legacy_name: Unmapped[str | None] = unmapped_column()`। ডান দিকে কিছু না দিয়ে শুধু `Unmapped[str]` লিখলেও একই, তবে dataclass ব্যবহার করলে টাইপ-চেকার ঠিক বোঝার জন্য `= unmapped_column()` লেখাই ভালো।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    old_code: Unmapped[int]                  # ডান দিক ছাড়া
print(Item.__table__.c.old_code.type, Item.__table__.c.old_code.nullable, "old_code" in inspect(Item).attrs)   # INTEGER False False
```

## dataclass mixin { #unmapped-dataclass-group }

## `unmapped_dataclass()` { #unmapped-dataclass }

```python
from sqlalchemy.orm import unmapped_dataclass
```

```python
unmapped_dataclass(*, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, eq=_NoArg.NO_ARG, order=_NoArg.NO_ARG, unsafe_hash=_NoArg.NO_ARG, match_args=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, dataclass_callable=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) `mapped_as_dataclass()`-এর মতো ডেকোরেটর, কিন্তু ক্লাসটিকে **ম্যাপ করে না**: dataclass-সমর্থিত **mixin** বানায় (যেমন সব মডেলে `created`, `updated` ফিল্ড), যা ম্যাপ করা dataclass মডেলে মেশানো যায়। প্যারামিটার `mapped_as_dataclass()`-এর মতো (`init`, `repr`, `eq`, `kw_only` …)। `MappedAsDataclass`-ভিত্তিক `Base` ব্যবহার করলে mixin-এ শুধু `MappedAsDataclass` subclass করলেও একই কাজ হয়।

**উদাহরণ:**

```python
@unmapped_dataclass
class Timestamps:
    created: Mapped[int] = mapped_column(default=0)

class Base(MappedAsDataclass, DeclarativeBase): pass
class Post(Timestamps, Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(default="")
print(Post(title="প্রথম"), dataclasses.is_dataclass(Timestamps))   # Post(created=0, id=None, title='প্রথম') True
```

### `unmapped_dataclass()`-এর সব প্যারামিটার { #unmapped-dataclass-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `init` | `__init__` বানাবে কি না। |
| `repr` | `__repr__` বানাবে কি না। |
| `eq` | `__eq__` বানাবে কি না। |
| `order` | তুলনা মেথড (`<` ইত্যাদি)। |
| `unsafe_hash` | `__hash__` জোর করে বানাবে কি না। |
| `match_args` | `__match_args__` (pattern matching)। |
| `kw_only` | সব ফিল্ড কীওয়ার্ড-একমাত্র। |
| `dataclass_callable` | `dataclasses.dataclass`-এর বদলে অন্য ফাংশন (যেমন Pydantic dataclass)। |

## টাইপ-হিন্ট সহায়ক { #as-typed-table-group }

## `as_typed_table()` { #as-typed-table }

```python
from sqlalchemy.orm import as_typed_table
```

```python
as_typed_table(typed_columns_cls=None, /)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) শুধু **টাইপ-চেকারের** জন্য: ORM মডেলের `__table__`-কে এমনভাবে ফেরত দেয় যাতে টাইপ-চেকার কলামগুলো চেনে (`table.c.data` → `Column[str]`)। চলার সময় এটি হুবহু `Model.__table__`। সাথে একটি [`TypedColumns`](schema.md#typedcolumns) ক্লাস দিন (অথবা মডেলে `__typed_cols__` annotation রাখলে শুধু মডেল)। কলামে `Mapped[...]`-এর বদলে `MappedColumn[...]` annotation দিলে টাইপ সবচেয়ে নির্ভুল হয়।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class A(Base):
    __tablename__ = "a"
    id: MappedColumn[int] = mapped_column(primary_key=True)
    data: MappedColumn[str]
class a_cols(A, TypedColumns):
    pass
t = as_typed_table(A, a_cols)
print(t is A.__table__, t.c.data.type)   # True VARCHAR
```

### `as_typed_table()`-এর সব প্যারামিটার { #as-typed-table-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cls` | ORM মডেল ক্লাস। |
| `typed_columns_cls` | মডেলের কলামগুলো বর্ণনা করা `TypedColumns` ক্লাস (মডেলে `__typed_cols__` থাকলে ঐচ্ছিক)। |

## `TypeResolve` { #typeresolve }

```python
from sqlalchemy.orm import TypeResolve
```

(২.১-এ নতুন) [`RegistryEvents.resolve_type_annotation`](orm-events.md#registryevents-resolve-type-annotation) ইভেন্টের আর্গুমেন্ট: একটি `Mapped[X]` annotation থেকে SQL টাইপ বের করতে যা যা জানা দরকার। সাধারণত `resolved_type` দেখে একটি SQL টাইপ ফেরত দেন; বাকি টাইপ `resolve()` দিয়ে registry-র নিয়মে ঠিক করা যায়।

**উদাহরণ:**

```python
Email = typing.NewType("Email", str)
class Base(DeclarativeBase): pass
seen = []
@event.listens_for(Base, "resolve_type_annotation")
def resolve(rt):
    seen.append((rt.key, rt.resolved_type.__name__))
    return String(320) if rt.resolved_type is Email else None
class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[Email]
print(seen, Contact.__table__.c.email.type)   # [('id', 'int'), ('email', 'Email')] VARCHAR(320)
```

### কনস্ট্রাক্টরের প্যারামিটার { #typeresolve-params }

```python
TypeResolve(registry, key, raw_type, resolved_type, raw_pep_593_type, pep_593_resolved_argument, raw_pep_695_type, pep_695_resolved_value)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `registry` | যে `registry`-তে ম্যাপ হচ্ছে। |
| `cls` | যে মডেল ক্লাস। |
| `key` | অ্যাট্রিবিউটের নাম। |
| `raw_type` | annotation-এর ভেতরের টাইপ যেমন লেখা। |
| `resolved_type` | `Optional`/`Annotated`/alias খুলে পাওয়া মূল Python টাইপ। |
| `raw_pep_593_type` | `Annotated[...]` হলে পুরো রূপ। |
| `pep_593_resolved_argument` | `Annotated[X, ...]`-এর `X`। |
| `raw_pep_695_type` | PEP 695 `type` alias হলে সেটি। |
| `pep_695_resolved_value` | alias-এর মান। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #typeresolve-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`cls`](#typeresolve-cls) | অ্যাট্রিবিউট | মডেল ক্লাস। |
| [`key`](#typeresolve-key) | অ্যাট্রিবিউট | অ্যাট্রিবিউটের নাম। |
| [`pep_593_resolved_argument`](#typeresolve-pep-593-resolved-argument) | অ্যাট্রিবিউট | `Annotated[X, ...]` হলে `X`, নইলে `None`। |
| [`pep_695_resolved_value`](#typeresolve-pep-695-resolved-value) | অ্যাট্রিবিউট | PEP 695 `type X = ...` alias হলে তার মান, নইলে `None`। |
| [`raw_pep_593_type`](#typeresolve-raw-pep-593-type) | অ্যাট্রিবিউট | `Annotated[...]` হলে পুরো annotated টাইপ, নইলে `None`। |
| [`raw_pep_695_type`](#typeresolve-raw-pep-695-type) | অ্যাট্রিবিউট | PEP 695 alias অবজেক্ট (`TypeAliasType`), নইলে `None`। |
| [`raw_type`](#typeresolve-raw-type) | অ্যাট্রিবিউট | `Mapped[...]`-এর ভেতরে যেমন লেখা (যেমন <code>str &#124; None</code>)। |
| [`registry`](#typeresolve-registry) | অ্যাট্রিবিউট | যে `registry`-তে ম্যাপ হচ্ছে। |
| [`resolve()`](#typeresolve-resolve) | মেথড | যেকোনো Python টাইপকে registry-র সাধারণ নিয়মে (`type_annotation_map`) SQL টাইপে বদলায়; না পারলে `None`। |
| [`resolved_type`](#typeresolve-resolved-type) | অ্যাট্রিবিউট | `Optional`, `Annotated`, alias খুলে পাওয়া মূল টাইপ: <code>str &#124; None</code> হলে `str`। |

### `TypeResolve.cls` { #typeresolve-cls }

**ধরন:** অ্যাট্রিবিউট

মডেল ক্লাস।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.cls.__name__))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
print(seen)   # ['T']
```

### `TypeResolve.key` { #typeresolve-key }

**ধরন:** অ্যাট্রিবিউট

অ্যাট্রিবিউটের নাম।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.key))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
    n: Mapped[str]
print(seen)   # ['id', 'n']
```

### `TypeResolve.pep_593_resolved_argument` { #typeresolve-pep-593-resolved-argument }

**ধরন:** অ্যাট্রিবিউট

`Annotated[X, ...]` হলে `X`, নইলে `None`।

**উদাহরণ:**

```python
Big = typing.Annotated[int, "বড়"]
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.pep_593_resolved_argument))
class T(Base):
    __tablename__ = "t"
    id: Mapped[Big] = mapped_column(primary_key=True)
print(seen)   # [<class 'int'>]
```

### `TypeResolve.pep_695_resolved_value` { #typeresolve-pep-695-resolved-value }

**ধরন:** অ্যাট্রিবিউট

PEP 695 `type X = ...` alias হলে তার মান, নইলে `None`।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.pep_695_resolved_value))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
print(seen)   # [None]
```

### `TypeResolve.raw_pep_593_type` { #typeresolve-raw-pep-593-type }

**ধরন:** অ্যাট্রিবিউট

`Annotated[...]` হলে পুরো annotated টাইপ, নইলে `None`।

**উদাহরণ:**

```python
Big = typing.Annotated[int, "বড়"]
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.raw_pep_593_type is Big))
class T(Base):
    __tablename__ = "t"
    id: Mapped[Big] = mapped_column(primary_key=True)
print(seen)   # [True]
```

### `TypeResolve.raw_pep_695_type` { #typeresolve-raw-pep-695-type }

**ধরন:** অ্যাট্রিবিউট

PEP 695 alias অবজেক্ট (`TypeAliasType`), নইলে `None`।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.raw_pep_695_type))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
print(seen)   # [None]
```

### `TypeResolve.raw_type` { #typeresolve-raw-type }

**ধরন:** অ্যাট্রিবিউট

`Mapped[...]`-এর ভেতরে যেমন লেখা (যেমন `str | None`)।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.raw_type))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
    note: Mapped[str | None]
print(seen)   # [<class 'int'>, str | None]
```

### `TypeResolve.registry` { #typeresolve-registry }

**ধরন:** অ্যাট্রিবিউট

যে `registry`-তে ম্যাপ হচ্ছে।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.registry is Base.registry))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
print(seen)   # [True]
```

### `TypeResolve.resolve()` { #typeresolve-resolve }

```python
TypeResolve.resolve(python_type)
```

**ধরন:** মেথড

যেকোনো Python টাইপকে registry-র সাধারণ নিয়মে (`type_annotation_map`) SQL টাইপে বদলায়; না পারলে `None`। নিজের নিয়মের ভেতর থেকে "বাকিটা স্বাভাবিকভাবে করো" বলতে।

**উদাহরণ:**

```python
Score = typing.NewType("Score", int)
class Base(DeclarativeBase): pass
@event.listens_for(Base, "resolve_type_annotation")
def resolve(rt):
    if rt.resolved_type is Score:
        return rt.resolve(int)          # Score-কে int-এর মতো ধরো
    return None
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[Score]
print(T.__table__.c.points.type)   # INTEGER
```

### `TypeResolve.resolved_type` { #typeresolve-resolved-type }

**ধরন:** অ্যাট্রিবিউট

`Optional`, `Annotated`, alias খুলে পাওয়া মূল টাইপ: `str | None` হলে `str`।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
seen = []
event.listen(Base, "resolve_type_annotation", lambda rt: seen.append(rt.resolved_type))
class T(Base):
    __tablename__ = "t"
    id: Mapped[int] = mapped_column(primary_key=True)
    note: Mapped[str | None]
print(seen)   # [<class 'int'>, <class 'str'>]
```

## `MappedClassProtocol` { #mappedclassprotocol }

```python
from sqlalchemy.orm import MappedClassProtocol
```

টাইপ-হিন্টের জন্য একটি `Protocol`: "যেকোনো ম্যাপ করা ক্লাস" (যার `__mapper__`, `__table__` আছে)। নিজের জেনেরিক ফাংশনে `def count_rows(model: type[MappedClassProtocol[Any]])`। শুধু টাইপ-চেকারের জন্য, `isinstance()`-এ চলে না।

**উদাহরণ:**

```python
def table_name(model: "MappedClassProtocol[typing.Any]") -> str:
    return model.__table__.name
class Base(DeclarativeBase): pass
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
print(table_name(Item))   # items
```

## কুয়েরি { #dictbundle-group }

## `DictBundle` { #dictbundle }

```python
from sqlalchemy.orm import DictBundle
```

(২.১-এ নতুন) [`Bundle`](loading.md#bundle)-এর মতো কয়েকটি কলাম এক নামে দলবদ্ধ করে, কিন্তু ফল দেয় **`dict`** হিসেবে (tuple-এর মতো `Row` নয়)। JSON API-তে সরাসরি পাঠানোর জন্য সুবিধাজনক। একই নামের দুটি কলাম রাখা যায় না।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
Base.metadata.create_all(engine)
with Session(engine) as s:
    s.add_all([User(id=1, name="রহিম"), User(id=2, name="করিম")]); s.commit()
    info = DictBundle("info", User.id, User.name)
    print(s.scalars(select(info).order_by(User.id)).all())   # [{'id': 1, 'name': 'রহিম'}, {'id': 2, 'name': 'করিম'}]
```

### কনস্ট্রাক্টরের প্যারামিটার { #dictbundle-params }

```python
DictBundle(name, *exprs, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | দলের নাম (ফলের রো-তে `row.info`)। |
| `exprs` | কলাম/এক্সপ্রেশনগুলো। |
| `kw` | `single_entity=` ইত্যাদি (`Bundle`-এর মতো)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Bundle`](loading.md#bundle-summary)-এর মতো।

## অন্যান্য { #orm-insert-sentinel-group }

## `orm_insert_sentinel()` { #orm-insert-sentinel }

```python
from sqlalchemy.orm import orm_insert_sentinel
```

```python
orm_insert_sentinel(name=None, type_=None, *, default=None, omit_from_statements=True)
```

**ধরন:** ফাংশন

(২.০.১০) "sentinel" কলাম যোগ করে: বাল্ক INSERT-এ (`insertmanyvalues`) একসাথে অনেক রো ঢুকিয়ে `RETURNING`-এর ফল **ঠিক কোন রো-র** তা মেলাতে SQLAlchemy এটি ব্যবহার করে। সাধারণত দরকার নেই; লাগে তখনই যখন primary key এমন যে ডেটাবেস নিজে বানায় অথচ ক্রম নিশ্চিত নয় (যেমন UUID server default)। ডেটাবেস টেবিলেও এই কলাম থাকতে হবে। Core-এর [`insert_sentinel()`](schema.md#insert-sentinel)-এর ORM রূপ।

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    _sentinel: Mapped[int] = orm_insert_sentinel()
print([(c.name, c._insert_sentinel) for c in Event.__table__.c])   # [('id', False), ('_sentinel', True)]
```

### `orm_insert_sentinel()`-এর সব প্যারামিটার { #orm-insert-sentinel-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | কলামের নাম (ডিফল্ট: অ্যাট্রিবিউটের নাম)। |
| `type_` | কলামের টাইপ (ডিফল্ট Integer)। |
| `default` | client-side ডিফল্ট (প্রতিটি রো-তে আলাদা মান হতে হবে; না দিলে SQLAlchemy নিজে দেয়)। |
| `omit_from_statements` | `True` (ডিফল্ট): সাধারণ SELECT/INSERT-এ কলামটি দেখাবে না। |

## `has_inherited_table()` { #has-inherited-table }

```python
from sqlalchemy.orm import has_inherited_table
```

```python
has_inherited_table()
```

**ধরন:** ফাংশন

ক্লাসের কোনো পূর্বপুরুষের নিজস্ব ম্যাপ করা টেবিল আছে কি না। mixin-এ কাজে লাগে: মূল ক্লাসে `__tablename__` দেবে, কিন্তু single-table inheritance-এর subclass-এ দেবে না। (`sqlalchemy.ext.declarative.has_inherited_table` একই কাজের পুরোনো জায়গা; [আরও এক্সটেনশন পেজে](ext-misc.md#has-inherited-table)।)

**উদাহরণ:**

```python
class Base(DeclarativeBase): pass
class AutoTable:
    @declared_attr.directive
    def __tablename__(cls):
        return None if has_inherited_table(cls) else cls.__name__.lower()
class Animal(AutoTable, Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str]
    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "animal"}
class Dog(Animal):
    __mapper_args__ = {"polymorphic_identity": "dog"}
print(has_inherited_table(Animal), has_inherited_table(Dog), Dog.__table__.name)   # False True animal
```

### `has_inherited_table()`-এর সব প্যারামিটার { #has-inherited-table-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cls` | যে ক্লাস পরীক্ষা করবেন। |

## `mapper()` { #mapper }

```python
from sqlalchemy.orm import mapper
```

```python
mapper(*arg, **kw)
```

**ধরন:** ফাংশন

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

২.০-তে **সরিয়ে ফেলা** `mapper()` ফাংশনের স্থানধারক। ডাকলে এরর। শুধু পুরোনো কোডের `event.listen(mapper, ...)` (সব mapper-এর ইভেন্ট) না ভাঙার জন্য আছে; সেখানে লিখুন `event.listen(Mapper, ...)`। classical mapping-এর জন্য `registry.map_imperatively()`।

**উদাহরণ:**

```python
class Plain:
    pass
try:
    mapper(Plain)
except Exception as e:
    print(type(e).__name__, str(e).split(".")[0])   # InvalidRequestError The 'sqlalchemy
```

### `mapper()`-এর সব প্যারামিটার { #mapper-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `arg` | (অব্যবহৃত) |
| `kw` | (অব্যবহৃত) |

/// tip | `Unmapped` বনাম অন্যান্য উপায়

| চাই | উপায় |
| :--- | :--- |
| কলাম টেবিলে থাকবে, কিন্তু মডেলে কখনো নয় | `x: Unmapped[int] = unmapped_column()` (২.১.৫) |
| কলাম মডেলে থাকবে, কিন্তু সাধারণত লোড হবে না | `mapped_column(deferred=True)` |
| ডেটাবেসে কলাম নেই, শুধু Python অ্যাট্রিবিউট | সাধারণ `@property`, বা annotation ছাড়া ক্লাস অ্যাট্রিবিউট |
| মডেলে কলাম নয়, SQL এক্সপ্রেশন | `column_property()` বা `hybrid_property` |

///
