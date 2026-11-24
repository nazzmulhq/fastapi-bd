# Mutable ও OrderingList API: JSON/ARRAY-এর ভেতরের বদল ধরা { #api-mutable }

/// note | এই পেজে যা আছে

* `sqlalchemy.ext.mutable`: `MutableBase`, `Mutable`, `MutableComposite`, `MutableDict`, `MutableList`, `MutableSet`; প্রতিটির **সব** সদস্য।
* `sqlalchemy.ext.orderinglist`: `ordering_list()`, `OrderingList`, `count_from_0()`, `count_from_1()`, `count_from_n_factory()`।

///

**সমস্যা:** JSON/ARRAY কলামে `user.prefs["theme"] = "dark"` লিখলে ORM বদলটা **দেখতে পায় না** (অ্যাট্রিবিউটে নতুন মান বসেনি, শুধু dict-এর ভেতরে বদলেছে), তাই `commit()` করলেও ডেটাবেসে কিছু যায় না। **সমাধান:** কলামের টাইপকে `MutableDict.as_mutable(JSONB)` দিয়ে মুড়ে দিন; তখন dict-এর প্রতিটি বদল ORM-কে জানানো হয়। (বিকল্প: পুরো নতুন dict বসানো, বা `flag_modified(obj, "prefs")`।)

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    plain: Mapped[dict] = mapped_column(JSONB, default=dict)                          # সাধারণ: বদল ধরা পড়ে না
    prefs: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), default=dict)   # mutable
    tags: Mapped[list] = mapped_column(MutableList.as_mutable(ARRAY(String)), default=list)
    roles: Mapped[set] = mapped_column(MutableSet.as_mutable(StrSet), default=set)   # StrSet: ARRAY ↔ set (নিচে দেখুন)
```

ডেটাবেসে একজন ইউজার (id ১), সব কলাম খালি। `saved()` নতুন session-এ ডেটাবেস থেকে আবার পড়ে দেখায় আসলে কী সেভ হয়েছে। PostgreSQL 16-এ চালিয়ে দেখা।

///

## মূল ক্লাস { #mutablebase-group }

## `MutableBase` { #mutablebase }

```python
from sqlalchemy.ext.mutable import MutableBase
```

`Mutable` আর `MutableComposite`-এর সাধারণ ভিত্তি: কোন অবজেক্টগুলো এই মানের "মালিক" তা মনে রাখে (`_parents`), আর সাধারণ মানকে mutable রূপে রূপান্তরের নিয়ম (`coerce`)।

**উদাহরণ:**

```python
print(issubclass(MutableDict, MutableBase), issubclass(MutableComposite, MutableBase))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutablebase-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`coerce()`](#mutablebase-coerce) | ক্লাস মেথড | (ক্লাস মেথড) অ্যাট্রিবিউটে বসানো সাধারণ মানকে এই mutable ক্লাসে রূপান্তর করে (যেমন সাধারণ `dict` → `MutableDict`); রূপান্তর সম্ভব না হলে এরর। |

### `MutableBase.coerce()` { #mutablebase-coerce }

```python
MutableBase.coerce(key, value)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) অ্যাট্রিবিউটে বসানো সাধারণ মানকে এই mutable ক্লাসে রূপান্তর করে (যেমন সাধারণ `dict` → `MutableDict`); রূপান্তর সম্ভব না হলে এরর। নিজের mutable ক্লাসে override করুন।

**উদাহরণ:**

```python
d = MutableDict.coerce("prefs", {"a": 1})
print(type(d).__name__, d)   # MutableDict {'a': 1}
```

## `Mutable` { #mutable }

```python
from sqlalchemy.ext.mutable import Mutable
```

নিজের mutable ধরন বানানোর মিক্সিন: সাবক্লাস করে প্রতিটি বদলকারী মেথডে `self.changed()` ডাকুন, আর `coerce()` লিখুন। তারপর `MyType.as_mutable(SQLType)` দিয়ে কলামে বসান। তৈরি-করা `MutableDict`, `MutableList`, `MutableSet` এরই সাবক্লাস।

**উদাহরণ:**

```python
class Counter(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        return value if isinstance(value, Counter) else Counter(value)
    def bump(self, k):
        self[k] = self.get(k, 0) + 1
        self.changed()                       # ORM-কে জানাও

class Page(Base):
    __tablename__ = "pages"
    id: Mapped[int] = mapped_column(primary_key=True)
    hits: Mapped[dict] = mapped_column(Counter.as_mutable(JSONB), default=dict)

Base.metadata.create_all(engine)
p = Page(id=1); session.add(p); session.commit()
p.hits.bump("home"); p.hits.bump("home"); session.commit()
with Session(engine) as s:
    print(s.get(Page, 1).hits)   # {'home': 2}
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutable-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`as_mutable()`](#mutable-as-mutable) | ক্লাস মেথড | (ক্লাস মেথড) একটি SQL টাইপ নিয়ে এমন টাইপ ফেরত দেয় যার কলামে এই mutable ক্লাস বসবে, আর বদল ধরা পড়বে: `MutableDict.as_mutable(JSONB)`। |
| [`associate_with()`](#mutable-associate-with) | ক্লাস মেথড | (ক্লাস মেথড) এই SQL টাইপের **সব ভবিষ্যৎ** কলামে নিজে থেকে mutable বসায় (যেমন অ্যাপের সব `JSON` কলামে)। |
| [`associate_with_attribute()`](#mutable-associate-with-attribute) | ক্লাস মেথড (internal) | (ক্লাস মেথড) একটি নির্দিষ্ট ম্যাপ করা অ্যাট্রিবিউটে mutation-listener বসায় (`as_mutable` / `associate_with` ভেতরে এটি ডাকে)। |
| [`changed()`](#mutable-changed) | মেথড | মানের ভেতরে বদল হলে ডাকুন: সব "মালিক" অবজেক্টকে ORM-এ "বদলেছে" চিহ্নিত করে (`flag_modified`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Mutable`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`MutableBase` থেকে:** [`coerce()`](#mutablebase-coerce)

///

### `Mutable.as_mutable()` { #mutable-as-mutable }

```python
Mutable.as_mutable(sqltype)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) একটি SQL টাইপ নিয়ে এমন টাইপ ফেরত দেয় যার কলামে এই mutable ক্লাস বসবে, আর বদল ধরা পড়বে: `MutableDict.as_mutable(JSONB)`। **শুধু এই কলামগুলোতে** প্রযোজ্য।

**উদাহরণ:**

```python
u.plain["x"] = 1; u.prefs["x"] = 1; session.commit()
print(saved("plain"), saved("prefs"))   # {} {'x': 1}   (সাধারণ JSONB-এর ভেতরের বদল হারিয়ে গেল)
```

### `Mutable.associate_with()` { #mutable-associate-with }

```python
Mutable.associate_with(sqltype)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) এই SQL টাইপের **সব ভবিষ্যৎ** কলামে নিজে থেকে mutable বসায় (যেমন অ্যাপের সব `JSON` কলামে)। মডেল তৈরির আগে ডাকতে হয়।

**উদাহরণ:**

```python
from sqlalchemy import JSON
class MyJSON(JSON): pass
MutableDict.associate_with(MyJSON)
class Doc(Base):
    __tablename__ = "docs_aw"
    id: Mapped[int] = mapped_column(primary_key=True)
    meta: Mapped[dict] = mapped_column(MyJSON)
print(type(Doc(meta={"a": 1}).meta).__name__)   # MutableDict
```

### `Mutable.associate_with_attribute()` { #mutable-associate-with-attribute }

```python
Mutable.associate_with_attribute(attribute)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) একটি নির্দিষ্ট ম্যাপ করা অ্যাট্রিবিউটে mutation-listener বসায় (`as_mutable` / `associate_with` ভেতরে এটি ডাকে)।

### `Mutable.changed()` { #mutable-changed }

```python
Mutable.changed()
```

**ধরন:** মেথড

মানের ভেতরে বদল হলে ডাকুন: সব "মালিক" অবজেক্টকে ORM-এ "বদলেছে" চিহ্নিত করে (`flag_modified`)।

**উদাহরণ:**

```python
u.prefs.update({"lang": "bn"})          # MutableDict.update ভেতরে changed() ডাকে
print(u in session.dirty)   # True
```

## `MutableComposite` { #mutablecomposite }

```python
from sqlalchemy.ext.mutable import MutableComposite
```

`composite()` অ্যাট্রিবিউটের (একাধিক কলাম মিলে একটি Python অবজেক্ট) ভেতরের ফিল্ড বদল ধরার মিক্সিন: ফিল্ড বদলালে `self.changed()` ডাকুন (সাধারণত `__setattr__`-এ)।

**উদাহরণ:**

```python
@dataclasses.dataclass
class Point(MutableComposite):
    x: int
    y: int
    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        self.changed()

class Shop(Base):
    __tablename__ = "shops"
    id: Mapped[int] = mapped_column(primary_key=True)
    loc: Mapped[Point] = composite(mapped_column("x", Integer), mapped_column("y", Integer))

Base.metadata.create_all(engine)
sh = Shop(id=1, loc=Point(1, 2)); session.add(sh); session.commit()
sh.loc.x = 99; session.commit()                # শুধু একটি ফিল্ড বদলানো
with Session(engine) as s:
    print(s.get(Shop, 1).loc)   # Point(x=99, y=2)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutablecomposite-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MutableComposite`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Mutable` থেকে:** [`changed()`](#mutable-changed)

**`MutableBase` থেকে:** [`coerce()`](#mutablebase-coerce)

///

## তৈরি-করা mutable কালেকশন { #mutabledict-group }

## `MutableDict` { #mutabledict }

```python
from sqlalchemy.ext.mutable import MutableDict
```

`dict`-এর mutable রূপ: key বসানো, মোছা, `update()` ইত্যাদি সব বদল ORM ধরে। JSON/JSONB/HSTORE কলামে `MutableDict.as_mutable(JSONB)`। **সতর্কতা:** শুধু উপরের স্তরের বদল ধরে; নেস্টেড dict-এর ভেতরে (`prefs["a"]["b"] = 1`) বদল ধরে না।

**উদাহরণ:**

```python
u.prefs["theme"] = "dark"; session.commit()
print(saved("prefs"))   # {'theme': 'dark'}
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutabledict-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`clear()`](#mutabledict-clear) | মেথড | সব key মুছে দেয় (বদল ধরা পড়ে)। |
| [`coerce()`](#mutabledict-coerce) | ক্লাস মেথড | (ক্লাস মেথড) সাধারণ dict → `MutableDict`; অ্যাট্রিবিউটে সাধারণ dict বসালেও নিজে থেকে রূপান্তর হয়। |
| [`copy()`](#mutabledict-copy) | মেথড | একটি সাধারণ কপি (বদলালে মূলটিতে প্রভাব নেই)। |
| [`fromkeys()`](#mutabledict-fromkeys) | মেথড | (dict-এর ক্লাস মেথড) key-তালিকা থেকে নতুন dict। |
| [`get()`](#mutabledict-get) | মেথড | `dict.get()`-এর মতো (কিছু বদলায় না)। |
| [`items()`](#mutabledict-items) | মেথড | `dict.items()`-এর মতো। |
| [`keys()`](#mutabledict-keys) | মেথড | `dict.keys()`-এর মতো। |
| [`pop()`](#mutabledict-pop) | মেথড | key সরিয়ে মান দেয় (বদল ধরা পড়ে)। |
| [`popitem()`](#mutabledict-popitem) | মেথড | শেষ key-মান জোড়া সরিয়ে দেয় (বদল ধরা পড়ে)। |
| [`setdefault()`](#mutabledict-setdefault) | মেথড | key না থাকলে বসায় (বদল ধরা পড়ে) আর মান দেয়। |
| [`update()`](#mutabledict-update) | মেথড | কয়েকটি key একসাথে বসায় (বদল ধরা পড়ে)। |
| [`values()`](#mutabledict-values) | মেথড | `dict.values()`-এর মতো। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MutableDict`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Mutable` থেকে:** [`as_mutable()`](#mutable-as-mutable) · [`associate_with()`](#mutable-associate-with) · [`associate_with_attribute()`](#mutable-associate-with-attribute) · [`changed()`](#mutable-changed)

///

### `MutableDict.clear()` { #mutabledict-clear }

```python
MutableDict.clear()
```

**ধরন:** মেথড

সব key মুছে দেয় (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.prefs["a"] = 1; session.commit(); u.prefs.clear(); session.commit()
print(saved("prefs"))   # {}
```

### `MutableDict.coerce()` { #mutabledict-coerce }

```python
MutableDict.coerce(key, value)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) সাধারণ dict → `MutableDict`; অ্যাট্রিবিউটে সাধারণ dict বসালেও নিজে থেকে রূপান্তর হয়।

**উদাহরণ:**

```python
u.prefs = {"x": 1}
print(type(u.prefs).__name__)   # MutableDict
```

### `MutableDict.copy()` { #mutabledict-copy }

```python
MutableDict.copy()
```

**ধরন:** মেথড

একটি সাধারণ কপি (বদলালে মূলটিতে প্রভাব নেই)।

**উদাহরণ:**

```python
c = u.prefs.copy(); c["z"] = 1
print(u.prefs)   # {}
```

### `MutableDict.fromkeys()` { #mutabledict-fromkeys }

```python
MutableDict.fromkeys(iterable, value=None, /)
```

**ধরন:** মেথড

(dict-এর ক্লাস মেথড) key-তালিকা থেকে নতুন dict।

**উদাহরণ:**

```python
print(MutableDict.fromkeys(["a", "b"], 0))   # {'a': 0, 'b': 0}
```

### `MutableDict.get()` { #mutabledict-get }

```python
MutableDict.get(key, default=None, /)
```

**ধরন:** মেথড

`dict.get()`-এর মতো (কিছু বদলায় না)।

**উদাহরণ:**

```python
print(u.prefs.get("theme", "light"))   # light
```

### `MutableDict.items()` { #mutabledict-items }

```python
MutableDict.items()
```

**ধরন:** মেথড

`dict.items()`-এর মতো।

**উদাহরণ:**

```python
u.prefs["a"] = 1
print(list(u.prefs.items()))   # [('a', 1)]
```

### `MutableDict.keys()` { #mutabledict-keys }

```python
MutableDict.keys()
```

**ধরন:** মেথড

`dict.keys()`-এর মতো।

**উদাহরণ:**

```python
u.prefs["a"] = 1
print(list(u.prefs.keys()))   # ['a']
```

### `MutableDict.pop()` { #mutabledict-pop }

```python
MutableDict.pop(*arg)
```

**ধরন:** মেথড

key সরিয়ে মান দেয় (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.prefs["a"] = 1; session.commit()
print(u.prefs.pop("a")); session.commit(); print(saved("prefs"))
# 1
# {}
```

### `MutableDict.popitem()` { #mutabledict-popitem }

```python
MutableDict.popitem()
```

**ধরন:** মেথড

শেষ key-মান জোড়া সরিয়ে দেয় (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.prefs["a"] = 1
print(u.prefs.popitem())   # ('a', 1)
```

### `MutableDict.setdefault()` { #mutabledict-setdefault }

```python
MutableDict.setdefault(*arg)
```

**ধরন:** মেথড

key না থাকলে বসায় (বদল ধরা পড়ে) আর মান দেয়।

**উদাহরণ:**

```python
u.prefs.setdefault("lang", "bn"); session.commit()
print(saved("prefs"))   # {'lang': 'bn'}
```

### `MutableDict.update()` { #mutabledict-update }

```python
MutableDict.update(*a, **kw)
```

**ধরন:** মেথড

কয়েকটি key একসাথে বসায় (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.prefs.update(theme="dark", lang="bn"); session.commit()
print(saved("prefs"))   # {'lang': 'bn', 'theme': 'dark'}
```

### `MutableDict.values()` { #mutabledict-values }

```python
MutableDict.values()
```

**ধরন:** মেথড

`dict.values()`-এর মতো।

**উদাহরণ:**

```python
u.prefs["a"] = 1
print(list(u.prefs.values()))   # [1]
```

## `MutableList` { #mutablelist }

```python
from sqlalchemy.ext.mutable import MutableList
```

`list`-এর mutable রূপ: `append()`, `extend()`, index-এ বসানো, `pop()` ইত্যাদি সব বদল ORM ধরে। ARRAY বা JSON কলামে।

**উদাহরণ:**

```python
u.tags.append("python"); session.commit()
print(saved("tags"))   # ['python']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutablelist-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append()`](#mutablelist-append) | মেথড | শেষে যোগ (বদল ধরা পড়ে)। |
| [`clear()`](#mutablelist-clear) | মেথড | সব মুছে দেয়। |
| [`coerce()`](#mutablelist-coerce) | ক্লাস মেথড | (ক্লাস মেথড) সাধারণ list → `MutableList`। |
| [`copy()`](#mutablelist-copy) | মেথড | সাধারণ কপি। |
| [`count()`](#mutablelist-count) | মেথড | একটি মান কতবার আছে (বদলায় না)। |
| [`extend()`](#mutablelist-extend) | মেথড | কয়েকটি একসাথে যোগ। |
| [`index()`](#mutablelist-index) | মেথড | মানের অবস্থান। |
| [`insert()`](#mutablelist-insert) | মেথড | নির্দিষ্ট অবস্থানে বসায়। |
| [`pop()`](#mutablelist-pop) | মেথড | একটি উপাদান সরিয়ে দেয়। |
| [`remove()`](#mutablelist-remove) | মেথড | একটি মান মুছে দেয়। |
| [`reverse()`](#mutablelist-reverse) | মেথড | উল্টো ক্রম। |
| [`sort()`](#mutablelist-sort) | মেথড | সাজায়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MutableList`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Mutable` থেকে:** [`as_mutable()`](#mutable-as-mutable) · [`associate_with()`](#mutable-associate-with) · [`associate_with_attribute()`](#mutable-associate-with-attribute) · [`changed()`](#mutable-changed)

///

### `MutableList.append()` { #mutablelist-append }

```python
MutableList.append(x)
```

**ধরন:** মেথড

শেষে যোগ (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.tags.append("sql"); session.commit()
print(saved("tags"))   # ['sql']
```

### `MutableList.clear()` { #mutablelist-clear }

```python
MutableList.clear()
```

**ধরন:** মেথড

সব মুছে দেয়।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"]); session.commit(); u.tags.clear(); session.commit()
print(saved("tags"))   # []
```

### `MutableList.coerce()` { #mutablelist-coerce }

```python
MutableList.coerce(key, value)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) সাধারণ list → `MutableList`।

**উদাহরণ:**

```python
u.tags = ["x"]
print(type(u.tags).__name__)   # MutableList
```

### `MutableList.copy()` { #mutablelist-copy }

```python
MutableList.copy()
```

**ধরন:** মেথড

সাধারণ কপি।

**উদাহরণ:**

```python
u.tags.append("a")
print(u.tags.copy())   # ['a']
```

### `MutableList.count()` { #mutablelist-count }

```python
MutableList.count(value, /)
```

**ধরন:** মেথড

একটি মান কতবার আছে (বদলায় না)।

**উদাহরণ:**

```python
u.tags.extend(["a", "a"])
print(u.tags.count("a"))   # 2
```

### `MutableList.extend()` { #mutablelist-extend }

```python
MutableList.extend(x)
```

**ধরন:** মেথড

কয়েকটি একসাথে যোগ।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"]); session.commit()
print(saved("tags"))   # ['a', 'b']
```

### `MutableList.index()` { #mutablelist-index }

```python
MutableList.index(value, start=0, stop=9223372036854775807, /)
```

**ধরন:** মেথড

মানের অবস্থান।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"])
print(u.tags.index("b"))   # 1
```

### `MutableList.insert()` { #mutablelist-insert }

```python
MutableList.insert(i, x)
```

**ধরন:** মেথড

নির্দিষ্ট অবস্থানে বসায়।

**উদাহরণ:**

```python
u.tags.extend(["a", "c"]); u.tags.insert(1, "b"); session.commit()
print(saved("tags"))   # ['a', 'b', 'c']
```

### `MutableList.pop()` { #mutablelist-pop }

```python
MutableList.pop(*arg)
```

**ধরন:** মেথড

একটি উপাদান সরিয়ে দেয়।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"]); session.commit(); u.tags.pop(); session.commit()
print(saved("tags"))   # ['a']
```

### `MutableList.remove()` { #mutablelist-remove }

```python
MutableList.remove(i)
```

**ধরন:** মেথড

একটি মান মুছে দেয়।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"]); session.commit(); u.tags.remove("a"); session.commit()
print(saved("tags"))   # ['b']
```

### `MutableList.reverse()` { #mutablelist-reverse }

```python
MutableList.reverse()
```

**ধরন:** মেথড

উল্টো ক্রম।

**উদাহরণ:**

```python
u.tags.extend(["a", "b"]); session.commit(); u.tags.reverse(); session.commit()
print(saved("tags"))   # ['b', 'a']
```

### `MutableList.sort()` { #mutablelist-sort }

```python
MutableList.sort(**kw)
```

**ধরন:** মেথড

সাজায়।

**উদাহরণ:**

```python
u.tags.extend(["c", "a"]); session.commit(); u.tags.sort(); session.commit()
print(saved("tags"))   # ['a', 'c']
```

## `MutableSet` { #mutableset }

```python
from sqlalchemy.ext.mutable import MutableSet
```

`set`-এর mutable রূপ: `add()`, `discard()`, `update()` ইত্যাদি সব বদল ORM ধরে (ডুপ্লিকেট নেই)।

/// warning | সাধারণ ভুল

`MutableSet.as_mutable(ARRAY(String))` সরাসরি লিখলে লোডের সময় `ValueError: Attribute 'roles' does not accept objects of type <class 'list'>` আসে: ডেটাবেস (ARRAY বা JSON) সবসময় **list** ফেরত দেয়, আর `MutableSet.coerce()` শুধু set নেয়। তাই একটি ছোট `TypeDecorator` দিয়ে list ↔ set রূপান্তর করুন:

```python
class StrSet(TypeDecorator):
    impl = ARRAY(String)
    cache_ok = True
    def process_bind_param(self, value, dialect):
        return None if value is None else sorted(value)
    def process_result_value(self, value, dialect):
        return None if value is None else set(value)

roles: Mapped[set] = mapped_column(MutableSet.as_mutable(StrSet), default=set)
```

///

**উদাহরণ:**

```python
u.roles.add("admin"); u.roles.add("admin"); session.commit()
print(saved("roles"))   # ['admin']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #mutableset-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#mutableset-add) | মেথড | একটি উপাদান যোগ (বদল ধরা পড়ে)। |
| [`clear()`](#mutableset-clear) | মেথড | সব মুছে দেয়। |
| [`coerce()`](#mutableset-coerce) | ক্লাস মেথড | (ক্লাস মেথড) সাধারণ set/list → `MutableSet`। |
| [`copy()`](#mutableset-copy) | মেথড | সাধারণ কপি। |
| [`difference()`](#mutableset-difference) | মেথড | পার্থক্য (নতুন set; মূলটি বদলায় না)। |
| [`difference_update()`](#mutableset-difference-update) | মেথড | জায়গাতেই পার্থক্য (বদল ধরা পড়ে)। |
| [`discard()`](#mutableset-discard) | মেথড | থাকলে মুছে দেয় (না থাকলে এরর নেই)। |
| [`intersection()`](#mutableset-intersection) | মেথড | ছেদ (নতুন set)। |
| [`intersection_update()`](#mutableset-intersection-update) | মেথড | জায়গাতেই ছেদ। |
| [`isdisjoint()`](#mutableset-isdisjoint) | মেথড | কোনো মিল নেই কি না। |
| [`issubset()`](#mutableset-issubset) | মেথড | উপসেট কি না। |
| [`issuperset()`](#mutableset-issuperset) | মেথড | অধিসেট কি না। |
| [`pop()`](#mutableset-pop) | মেথড | যেকোনো একটি উপাদান সরিয়ে দেয়। |
| [`remove()`](#mutableset-remove) | মেথড | মুছে দেয় (না থাকলে `KeyError`)। |
| [`symmetric_difference()`](#mutableset-symmetric-difference) | মেথড | সমমিত পার্থক্য (নতুন set)। |
| [`symmetric_difference_update()`](#mutableset-symmetric-difference-update) | মেথড | জায়গাতেই সমমিত পার্থক্য। |
| [`union()`](#mutableset-union) | মেথড | মিলন (নতুন set)। |
| [`update()`](#mutableset-update) | মেথড | কয়েকটি একসাথে যোগ (বদল ধরা পড়ে)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `MutableSet`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Mutable` থেকে:** [`as_mutable()`](#mutable-as-mutable) · [`associate_with()`](#mutable-associate-with) · [`associate_with_attribute()`](#mutable-associate-with-attribute) · [`changed()`](#mutable-changed)

///

### `MutableSet.add()` { #mutableset-add }

```python
MutableSet.add(elem)
```

**ধরন:** মেথড

একটি উপাদান যোগ (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.roles.add("editor"); session.commit()
print(saved("roles"))   # ['editor']
```

### `MutableSet.clear()` { #mutableset-clear }

```python
MutableSet.clear()
```

**ধরন:** মেথড

সব মুছে দেয়।

**উদাহরণ:**

```python
u.roles.add("a"); session.commit(); u.roles.clear(); session.commit()
print(saved("roles"))   # []
```

### `MutableSet.coerce()` { #mutableset-coerce }

```python
MutableSet.coerce(index, value)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) সাধারণ set/list → `MutableSet`।

**উদাহরণ:**

```python
u.roles = {"x"}
print(type(u.roles).__name__)   # MutableSet
```

### `MutableSet.copy()` { #mutableset-copy }

```python
MutableSet.copy()
```

**ধরন:** মেথড

সাধারণ কপি।

**উদাহরণ:**

```python
u.roles.add("a")
print(u.roles.copy())   # {'a'}
```

### `MutableSet.difference()` { #mutableset-difference }

```python
MutableSet.difference(*others)
```

**ধরন:** মেথড

পার্থক্য (নতুন set; মূলটি বদলায় না)।

**উদাহরণ:**

```python
u.roles.update({"a", "b"})
print(sorted(u.roles.difference({"a"})))   # ['b']
```

### `MutableSet.difference_update()` { #mutableset-difference-update }

```python
MutableSet.difference_update(*arg)
```

**ধরন:** মেথড

জায়গাতেই পার্থক্য (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.roles.update({"a", "b"}); session.commit(); u.roles.difference_update({"a"}); session.commit()
print(saved("roles"))   # ['b']
```

### `MutableSet.discard()` { #mutableset-discard }

```python
MutableSet.discard(elem)
```

**ধরন:** মেথড

থাকলে মুছে দেয় (না থাকলে এরর নেই)।

**উদাহরণ:**

```python
u.roles.add("a"); session.commit(); u.roles.discard("a"); u.roles.discard("zz"); session.commit()
print(saved("roles"))   # []
```

### `MutableSet.intersection()` { #mutableset-intersection }

```python
MutableSet.intersection(*others)
```

**ধরন:** মেথড

ছেদ (নতুন set)।

**উদাহরণ:**

```python
u.roles.update({"a", "b"})
print(u.roles.intersection({"b", "c"}))   # {'b'}
```

### `MutableSet.intersection_update()` { #mutableset-intersection-update }

```python
MutableSet.intersection_update(*arg)
```

**ধরন:** মেথড

জায়গাতেই ছেদ।

**উদাহরণ:**

```python
u.roles.update({"a", "b"}); session.commit(); u.roles.intersection_update({"b"}); session.commit()
print(saved("roles"))   # ['b']
```

### `MutableSet.isdisjoint()` { #mutableset-isdisjoint }

```python
MutableSet.isdisjoint(other, /)
```

**ধরন:** মেথড

কোনো মিল নেই কি না।

**উদাহরণ:**

```python
u.roles.add("a")
print(u.roles.isdisjoint({"b"}))   # True
```

### `MutableSet.issubset()` { #mutableset-issubset }

```python
MutableSet.issubset(other, /)
```

**ধরন:** মেথড

উপসেট কি না।

**উদাহরণ:**

```python
u.roles.add("a")
print(u.roles.issubset({"a", "b"}))   # True
```

### `MutableSet.issuperset()` { #mutableset-issuperset }

```python
MutableSet.issuperset(other, /)
```

**ধরন:** মেথড

অধিসেট কি না।

**উদাহরণ:**

```python
u.roles.update({"a", "b"})
print(u.roles.issuperset({"a"}))   # True
```

### `MutableSet.pop()` { #mutableset-pop }

```python
MutableSet.pop(*arg)
```

**ধরন:** মেথড

যেকোনো একটি উপাদান সরিয়ে দেয়।

**উদাহরণ:**

```python
u.roles.add("a")
print(u.roles.pop(), len(u.roles))   # a 0
```

### `MutableSet.remove()` { #mutableset-remove }

```python
MutableSet.remove(elem)
```

**ধরন:** মেথড

মুছে দেয় (না থাকলে `KeyError`)।

**উদাহরণ:**

```python
u.roles.add("a"); session.commit(); u.roles.remove("a"); session.commit()
print(saved("roles"))   # []
```

### `MutableSet.symmetric_difference()` { #mutableset-symmetric-difference }

```python
MutableSet.symmetric_difference(other, /)
```

**ধরন:** মেথড

সমমিত পার্থক্য (নতুন set)।

**উদাহরণ:**

```python
u.roles.update({"a", "b"})
print(sorted(u.roles.symmetric_difference({"b", "c"})))   # ['a', 'c']
```

### `MutableSet.symmetric_difference_update()` { #mutableset-symmetric-difference-update }

```python
MutableSet.symmetric_difference_update(*arg)
```

**ধরন:** মেথড

জায়গাতেই সমমিত পার্থক্য।

**উদাহরণ:**

```python
u.roles.update({"a", "b"}); session.commit(); u.roles.symmetric_difference_update({"b", "c"}); session.commit()
print(saved("roles"))   # ['a', 'c']
```

### `MutableSet.union()` { #mutableset-union }

```python
MutableSet.union(*others)
```

**ধরন:** মেথড

মিলন (নতুন set)।

**উদাহরণ:**

```python
u.roles.add("a")
print(sorted(u.roles.union({"b"})))   # ['a', 'b']
```

### `MutableSet.update()` { #mutableset-update }

```python
MutableSet.update(*arg)
```

**ধরন:** মেথড

কয়েকটি একসাথে যোগ (বদল ধরা পড়ে)।

**উদাহরণ:**

```python
u.roles.update({"a", "b"}); session.commit()
print(saved("roles"))   # ['a', 'b']
```

## OrderingList: ক্রম-কলাম নিজে থেকে হালনাগাদ { #ordering-list-group }

## `ordering_list()` { #ordering-list }

```python
from sqlalchemy.ext.orderinglist import ordering_list
```

```python
ordering_list(attr, count_from=None, ordering_func=None, reorder_on_append=False)
```

**ধরন:** ফাংশন

one-to-many কালেকশনের `collection_class` হিসেবে: তালিকায় কোন উপাদান কোন অবস্থানে তা একটি কলামে (`position`) নিজে থেকে লিখে রাখে। `insert()`, `pop()`, অদলবদল করলে বাকিদের `position`-ও ঠিক হয়ে যায়। প্লেলিস্টের গান, কোর্সের লেসন, ফর্মের প্রশ্নের ক্রম রাখতে। রিলেশনশিপে `order_by=Child.position` দিন, যাতে লোডের সময় একই ক্রম আসে।

**উদাহরণ:**

```python
class Playlist(Base):
    __tablename__ = "playlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    songs: Mapped[list["Song"]] = relationship(order_by="Song.position", collection_class=ordering_list("position"))

class Song(Base):
    __tablename__ = "songs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    position: Mapped[int]
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"))

pl = Playlist(songs=[Song(title="ক"), Song(title="খ")])
pl.songs.insert(0, Song(title="শুরু"))
print([(s.title, s.position) for s in pl.songs])   # [('শুরু', 0), ('ক', 1), ('খ', 2)]
```

### `ordering_list()`-এর সব প্যারামিটার { #ordering-list-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attr` | যে কলামে অবস্থান লেখা হবে। |
| `count_from` | কোন সংখ্যা থেকে গোনা শুরু (ডিফল্ট ০; `1` দিলে ১ থেকে)। |
| `ordering_func` | অবস্থান হিসাবের নিজের ফাংশন `(index, collection) -> মান`। |
| `reorder_on_append` | `True` দিলে append করলেও পুরো তালিকার অবস্থান নতুন করে হিসাব (আগে থেকে ভুল অবস্থান থাকলে)। |

## `OrderingList` { #orderinglist }

```python
from sqlalchemy.ext.orderinglist import OrderingList
```

`ordering_list()` যে list-ক্লাস বানায়: সাধারণ `list`-এর সব মেথড, প্রতিটি বদলে অবস্থান-কলাম হালনাগাদ।

**উদাহরণ:**

```python
ol = ordering_list("pos")()
print(isinstance(ol, OrderingList), isinstance(ol, list))   # True True
```

### কনস্ট্রাক্টরের প্যারামিটার { #orderinglist-params }

```python
OrderingList(ordering_attr, ordering_func=None, reorder_on_append=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `ordering_attr` | অবস্থান-কলামের নাম। |
| `ordering_func` | অবস্থান হিসাবের ফাংশন। |
| `reorder_on_append` | append-এ পুরো তালিকা নতুন করে সাজানো। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #orderinglist-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append()`](#orderinglist-append) | মেথড | শেষে যোগ করে, অবস্থান বসায়। |
| [`clear()`](#orderinglist-clear) | মেথড | সব সরিয়ে দেয়। |
| [`copy()`](#orderinglist-copy) | মেথড | সাধারণ list কপি। |
| [`count()`](#orderinglist-count) | মেথড | `list.count()`-এর মতো। |
| [`extend()`](#orderinglist-extend) | মেথড | কয়েকটি যোগ, প্রতিটির অবস্থান বসায়। |
| [`index()`](#orderinglist-index) | মেথড | `list.index()`-এর মতো। |
| [`insert()`](#orderinglist-insert) | মেথড | নির্দিষ্ট অবস্থানে বসায়, পরের সবার অবস্থান এক করে বাড়ায়। |
| [`pop()`](#orderinglist-pop) | মেথড | সরিয়ে দেয়, পরের সবার অবস্থান কমায়। |
| [`remove()`](#orderinglist-remove) | মেথড | একটি উপাদান সরায়। |
| [`reorder()`](#orderinglist-reorder) | মেথড | পুরো তালিকার অবস্থান-কলাম বর্তমান ক্রম অনুযায়ী নতুন করে বসায় (সাধারণ list-অপারেশনে ক্রম বদলালে, যেমন `sort()`-এর পর)। |
| [`reverse()`](#orderinglist-reverse) | মেথড | `list.reverse()` (অবস্থান হালনাগাদে পরে `reorder()` ডাকুন)। |
| [`sort()`](#orderinglist-sort) | মেথড | `list.sort()` (অবস্থান হালনাগাদে পরে `reorder()` ডাকুন)। |

### `OrderingList.append()` { #orderinglist-append }

```python
OrderingList.append(entity)
```

**ধরন:** মেথড

শেষে যোগ করে, অবস্থান বসায়।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); a, b = It(), It()
ol.append(a); ol.append(b)
print(a.pos, b.pos)   # 0 1
```

### `OrderingList.clear()` { #orderinglist-clear }

```python
OrderingList.clear()
```

**ধরন:** মেথড

সব সরিয়ে দেয়।

**উদাহরণ:**

```python
ol = ordering_list("pos")(); ol.clear()
print(len(ol))   # 0
```

### `OrderingList.copy()` { #orderinglist-copy }

```python
OrderingList.copy()
```

**ধরন:** মেথড

সাধারণ list কপি।

**উদাহরণ:**

```python
print(type(ordering_list("pos")().copy()).__name__)   # list
```

### `OrderingList.count()` { #orderinglist-count }

```python
OrderingList.count(value, /)
```

**ধরন:** মেথড

`list.count()`-এর মতো।

**উদাহরণ:**

```python
print(ordering_list("pos")().count(1))   # 0
```

### `OrderingList.extend()` { #orderinglist-extend }

```python
OrderingList.extend(iterable, /)
```

**ধরন:** মেথড

কয়েকটি যোগ, প্রতিটির অবস্থান বসায়।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); items = [It(), It()]
ol.extend(items)
print([i.pos for i in items])   # [0, 1]
```

### `OrderingList.index()` { #orderinglist-index }

```python
OrderingList.index(value, start=0, stop=9223372036854775807, /)
```

**ধরন:** মেথড

`list.index()`-এর মতো।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); a = It(); ol.append(a)
print(ol.index(a))   # 0
```

### `OrderingList.insert()` { #orderinglist-insert }

```python
OrderingList.insert(index, entity)
```

**ধরন:** মেথড

নির্দিষ্ট অবস্থানে বসায়, পরের সবার অবস্থান এক করে বাড়ায়।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); a, b = It(), It()
ol.append(a); ol.insert(0, b)
print(b.pos, a.pos)   # 0 1
```

### `OrderingList.pop()` { #orderinglist-pop }

```python
OrderingList.pop(index=-1)
```

**ধরন:** মেথড

সরিয়ে দেয়, পরের সবার অবস্থান কমায়।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); a, b = It(), It()
ol.extend([a, b]); ol.pop(0)
print(b.pos)   # 0
```

### `OrderingList.remove()` { #orderinglist-remove }

```python
OrderingList.remove(entity)
```

**ধরন:** মেথড

একটি উপাদান সরায়। বাকিদের অবস্থান নতুন করে বসে **শুধু তালিকাটি কোনো রিলেশনশিপের অংশ হলে** (স্বতন্ত্র তালিকায় নয়; তখন `reorder()` ডাকুন)।

**উদাহরণ:**

```python
class It:
    pos = None
ol = ordering_list("pos")(); a, b = It(), It()
ol.extend([a, b]); ol.remove(a)
print(b.pos)   # 1  (স্বতন্ত্র তালিকা, তাই অবস্থান বদলায়নি)
ol.reorder(); print(b.pos)   # 0
```

### `OrderingList.reorder()` { #orderinglist-reorder }

```python
OrderingList.reorder()
```

**ধরন:** মেথড

পুরো তালিকার অবস্থান-কলাম বর্তমান ক্রম অনুযায়ী নতুন করে বসায় (সাধারণ list-অপারেশনে ক্রম বদলালে, যেমন `sort()`-এর পর)।

**উদাহরণ:**

```python
class It:
    def __init__(self, n): self.n, self.pos = n, None
ol = ordering_list("pos")(); ol.extend([It("খ"), It("ক")])
ol.sort(key=lambda i: i.n); ol.reorder()
print([(i.n, i.pos) for i in ol])   # [('ক', 0), ('খ', 1)]
```

### `OrderingList.reverse()` { #orderinglist-reverse }

```python
OrderingList.reverse()
```

**ধরন:** মেথড

`list.reverse()` (অবস্থান হালনাগাদে পরে `reorder()` ডাকুন)।

**উদাহরণ:**

```python
ol = ordering_list("pos")(); ol.reverse()
print(list(ol))   # []
```

### `OrderingList.sort()` { #orderinglist-sort }

```python
OrderingList.sort(*, key=None, reverse=False)
```

**ধরন:** মেথড

`list.sort()` (অবস্থান হালনাগাদে পরে `reorder()` ডাকুন)।

**উদাহরণ:**

```python
ol = ordering_list("pos")(); ol.sort()
print(list(ol))   # []
```

## `count_from_0()` { #count-from-0 }

```python
from sqlalchemy.ext.orderinglist import count_from_0
```

```python
count_from_0(index, collection)
```

**ধরন:** ফাংশন

অবস্থান-ফাংশন: ০ থেকে গোনা (ডিফল্ট)।

**উদাহরণ:**

```python
print(count_from_0(0, []), count_from_0(3, []))   # 0 3
```

### `count_from_0()`-এর সব প্যারামিটার { #count-from-0-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `index` | তালিকায় অবস্থান। |
| `collection` | কালেকশন। |

## `count_from_1()` { #count-from-1 }

```python
from sqlalchemy.ext.orderinglist import count_from_1
```

```python
count_from_1(index, collection)
```

**ধরন:** ফাংশন

অবস্থান-ফাংশন: ১ থেকে গোনা (`ordering_list("pos", count_from=1)`-এর সমান)।

**উদাহরণ:**

```python
print(count_from_1(0, []), count_from_1(3, []))   # 1 4
```

### `count_from_1()`-এর সব প্যারামিটার { #count-from-1-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `index` | তালিকায় অবস্থান। |
| `collection` | কালেকশন। |

## `count_from_n_factory()` { #count-from-n-factory }

```python
from sqlalchemy.ext.orderinglist import count_from_n_factory
```

```python
count_from_n_factory(start)
```

**ধরন:** ফাংশন

যেকোনো সংখ্যা থেকে গোনার অবস্থান-ফাংশন বানায়।

**উদাহরণ:**

```python
from_10 = count_from_n_factory(10)
print(from_10(0, []), from_10(2, []))   # 10 12
```

### `count_from_n_factory()`-এর সব প্যারামিটার { #count-from-n-factory-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `start` | শুরুর সংখ্যা। |

/// check | সংক্ষেপে মনে রাখুন

* JSON/ARRAY-এর ভেতরের বদল সেভ করতে: `MutableDict.as_mutable(JSONB)`, `MutableList.as_mutable(...)`, `MutableSet.as_mutable(...)`।
* নেস্টেড বদল ধরা পড়ে না: পুরো মান নতুন করে বসান বা `flag_modified(obj, "col")`।
* নিজের ধরন: `Mutable` সাবক্লাস + `coerce()` + বদলে `self.changed()`।
* কালেকশনের ক্রম কলামে: `collection_class=ordering_list("position")` + `order_by`।

///
