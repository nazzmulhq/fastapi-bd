# লোডিং অপশন ও ORM কুয়েরি হেল্পার API { #api-loading }

/// note | এই পেজে যা আছে

* **রিলেশনশিপ লোডিং অপশন:** `selectinload()`, `joinedload()`, `subqueryload()`, `lazyload()`, `immediateload()`, `noload()`, `raiseload()`, `defaultload()`, `contains_eager()`।
* **কলাম লোডিং অপশন:** `load_only()`, `defer()`, `undefer()`, `undefer_group()`, `with_expression()`।
* **অন্যান্য অপশন:** `selectin_polymorphic()`, `with_loader_criteria()`, আর `Load` ক্লাসের **সব** সদস্য।
* **ORM কুয়েরি হেল্পার:** `aliased()`, `with_polymorphic()`, `with_parent()`, `join()`, `outerjoin()`, আর `Bundle`-এর সব সদস্য।

///

**লোডার অপশন** কুয়েরিকে বলে দেয় সম্পর্কিত ডেটা (রিলেশনশিপ) বা ভারী কলাম **কখন ও কীভাবে** লোড হবে। মডেলে `relationship(lazy=...)` দিয়ে একটা ডিফল্ট ঠিক করা থাকে; প্রতিটি কুয়েরিতে `.options(...)` দিয়ে সেটা বদলানো যায়। N+1 সমস্যা কী আর কোন অপশন কখন বেছে নেবেন, তা ধাপে ধাপে দেখুন [Relationship অধ্যায়ের ১৬ ও ১৭ নম্বর অংশে](../relationships.md#s16)।

/// tip | কোনটা কখন: এক লাইনে

| অবস্থা | অপশন |
| :--- | :--- |
| one-to-many / many-to-many কালেকশন (সবচেয়ে ভালো ডিফল্ট) | `selectinload()` |
| many-to-one বা one-to-one (একটি অবজেক্ট) | `joinedload()` |
| কুয়েরিতে আগেই JOIN করেছেন, সেই JOIN থেকেই ভরাতে চান | `contains_eager()` |
| async-এ ভুল করে lazy load আটকাতে | `raiseload("*")` |
| বড় কলাম (যেমন `bio`) বাদ দিয়ে হালকা কুয়েরি | `load_only()` / `defer()` |

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    bio: Mapped[str] = mapped_column(deferred=True, deferred_group="profile")      # ভারী কলাম
    avatar: Mapped[str] = mapped_column(deferred=True, deferred_group="profile")
    score: Mapped[int] = query_expression()                                       # কুয়েরিতে হিসাব হবে
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Address(Base):          # id, email, user_id, user (← User.addresses)
    ...

class Post(Base):             # id, title, published (bool), user_id, author (← User.posts)
    ...

class Node(Base):             # self-referential ট্রি: id, name, parent_id, children
    ...

class Employee(Base):         # joined inheritance: Engineer (lang), Manager (team)
    ...
```

ডেটা: রহিম (id ১, দুটি ঠিকানা, দুটি পোস্ট: একটি প্রকাশিত, একটি খসড়া), করিম (id ২, কোনো ঠিকানা নেই, একটি প্রকাশিত পোস্ট), সুমি (id ৩, একটি ঠিকানা)। ট্রি: মূল → শাখা → পাতা। কর্মী: আলিফ (Engineer), বৃষ্টি (Manager), চয়ন (Employee)।

কয়টি SQL কুয়েরি চলল তা গুনতে উদাহরণে `count_sql()` নামের একটি ছোট হেল্পার আছে (ভেতরে `before_cursor_execute` event শোনে)। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## রিলেশনশিপ লোডিং অপশন { #selectinload-group }

## `selectinload()` { #selectinload }

```python
from sqlalchemy.orm import selectinload
```

```python
selectinload(*keys, recursion_depth=None, chunksize=None)
```

**ধরন:** ফাংশন

**সবচেয়ে বেশি ব্যবহৃত eager loader।** মূল কুয়েরির পরে **একটি** আলাদা `SELECT ... WHERE user_id IN (১, ২, ৩)` চালিয়ে সব অবজেক্টের রিলেশনশিপ একসাথে ভরে দেয়। ১০০ জন ইউজার হলে ১০১টি কুয়েরির (N+1) বদলে মাত্র ২টি কুয়েরি। কালেকশনের (one-to-many, many-to-many) জন্য প্রথম পছন্দ, async-এ নিরাপদ।

**উদাহরণ:**

```python
with count_sql() as q:
    users = session.scalars(select(User).options(selectinload(User.addresses)).order_by(User.id)).all()
    print([len(u.addresses) for u in users])   # [2, 0, 1]
print(len(q))                                  # 2  (ইউজার + এক কুয়েরিতে সব ঠিকানা)
```

### `selectinload()`-এর সব প্যারামিটার { #selectinload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ লোড হবে: `User.addresses`। একাধিক দিলে চেইন হয়: `selectinload(User.posts, Post.author)` মানে পোস্ট, তারপর প্রতিটি পোস্টের লেখক। |
| `recursion_depth` | self-referential রিলেশনশিপে (ট্রি) কত স্তর গভীর পর্যন্ত একই অপশন বারবার প্রয়োগ হবে। `-1` মানে যতক্ষণ ডেটা আছে। |
| `chunksize` | (২.১-এ নতুন) `IN (...)`-এর ভেতরে এক কুয়েরিতে সর্বোচ্চ কয়টি primary key যাবে (ডিফল্ট ৫০০)। বেশি হলে একাধিক কুয়েরিতে ভাগ হয়। |

**চেইন: পোস্ট, তারপর প্রতিটি পোস্টের লেখক**

```python
stmt = select(User).options(selectinload(User.posts).selectinload(Post.author))
u = session.scalars(stmt.where(User.id == 1)).one()
print([p.author.name for p in u.posts])   # ['রহিম', 'রহিম']
```

**recursion_depth: পুরো ট্রি এক ধাক্কায়**

```python
with count_sql() as q:
    root = session.scalars(select(Node).where(Node.id == 1)
                           .options(selectinload(Node.children, recursion_depth=-1))).one()
    print(root.children[0].children[0].name)   # পাতা
print(len(q))   # 4  (মূল + প্রতিটি স্তরের জন্য একটি করে; শেষটি খালি স্তর যাচাই করে)
```

## `joinedload()` { #joinedload }

```python
from sqlalchemy.orm import joinedload
```

```python
joinedload(*keys, **kw)
```

**ধরন:** ফাংশন

মূল কুয়েরিতেই `LEFT OUTER JOIN` জুড়ে দিয়ে রিলেশনশিপ একই কুয়েরিতে আনে। **many-to-one / one-to-one** (যেমন `Address.user`) এর জন্য সবচেয়ে ভালো। কালেকশনে ব্যবহার করলে রো সংখ্যা বেড়ে যায় (একজন ইউজার × তার সব ঠিকানা), তাই তখন `.unique()` লাগে।

**উদাহরণ:**

```python
with count_sql() as q:
    addrs = session.scalars(select(Address).options(joinedload(Address.user)).order_by(Address.id)).all()
    print([a.user.name for a in addrs])   # ['রহিম', 'রহিম', 'সুমি']
print(len(q), "JOIN" in q[0])             # 1 True
```

### `joinedload()`-এর সব প্যারামিটার { #joinedload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ (চেইনও করা যায়)। |
| `kw` | `innerjoin=True` দিলে `LEFT OUTER JOIN`-এর বদলে `INNER JOIN` (রিলেশনশিপ কখনো খালি না হলে দ্রুততর)। `innerjoin="unnested"` নেস্টেড চেইনে প্রয়োগের নিয়ম বদলায়। |

**কালেকশনে joinedload: unique() বাধ্যতামূলক**

```python
result = session.scalars(select(User).options(joinedload(User.addresses)).order_by(User.id))
users = result.unique().all()        # unique() না দিলে InvalidRequestError
print([u.name for u in users])       # ['রহিম', 'করিম', 'সুমি']
```

## `subqueryload()` { #subqueryload }

```python
from sqlalchemy.orm import subqueryload
```

```python
subqueryload(*keys)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(পুরোনো ধাঁচ) মূল কুয়েরিটিকেই সাবকুয়েরি বানিয়ে তার সাথে JOIN করে দ্বিতীয় একটি কুয়েরিতে রিলেশনশিপ আনে। এখন প্রায় সব ক্ষেত্রে `selectinload()` ভালো ও সরল; `subqueryload` শুধু খুব বড় composite primary key-র মতো বিশেষ ক্ষেত্রে দরকার হতে পারে।

**উদাহরণ:**

```python
with count_sql() as q:
    users = session.scalars(select(User).options(subqueryload(User.addresses)).order_by(User.id)).all()
    print([len(u.addresses) for u in users])   # [2, 0, 1]
print(len(q))                                  # 2
```

### `subqueryload()`-এর সব প্যারামিটার { #subqueryload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ। |

## `lazyload()` { #lazyload }

```python
from sqlalchemy.orm import lazyload
```

```python
lazyload(*keys)
```

**ধরন:** ফাংশন

রিলেশনশিপকে "lazy" (ডিফল্ট) করে: অ্যাট্রিবিউট প্রথমবার পড়ার সময় তখনই আলাদা SELECT চলে। মডেলে `lazy="selectin"` বা `"joined"` দেওয়া থাকলে কোনো একটি কুয়েরিতে সেটা বন্ধ করতে কাজে লাগে। **async-এ lazy load চলে না** (এরর `MissingGreenlet`)।

**উদাহরণ:**

```python
with count_sql() as q:
    u = session.scalars(select(User).options(lazyload(User.addresses)).where(User.id == 1)).one()
    print(len(q))               # 1  (এখনো ঠিকানা লোড হয়নি)
    print(len(u.addresses))     # 2
    print(len(q))               # 2  (পড়ার সময় আরেকটি SELECT চলল)
```

### `lazyload()`-এর সব প্যারামিটার { #lazyload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ। |

## `immediateload()` { #immediateload }

```python
from sqlalchemy.orm import immediateload
```

```python
immediateload(*keys, recursion_depth=None)
```

**ধরন:** ফাংশন

মূল কুয়েরির পরপরই **প্রতিটি অবজেক্টের জন্য আলাদা** SELECT চালিয়ে রিলেশনশিপ ভরে দেয় (মানে N+1, কিন্তু আগেভাগে)। সাধারণত `selectinload()` ভালো; এটি মূলত self-referential ট্রি বা বিশেষ ক্ষেত্রে।

**উদাহরণ:**

```python
with count_sql() as q:
    users = session.scalars(select(User).options(immediateload(User.addresses)).order_by(User.id)).all()
print(len(q))                                 # 4  (ইউজার ১টি + প্রতি ইউজারে ১টি)
print([len(u.addresses) for u in users])      # [2, 0, 1]  (আর নতুন কুয়েরি লাগে না)
```

### `immediateload()`-এর সব প্যারামিটার { #immediateload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ। |
| `recursion_depth` | self-referential রিলেশনশিপে কত স্তর পর্যন্ত (`-1` মানে সীমাহীন)। |

## `noload()` { #noload }

```python
from sqlalchemy.orm import noload
```

```python
noload(*keys)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

(পুরোনো, ব্যবহার নিরুৎসাহিত) রিলেশনশিপ **কখনো লোড হবে না**: কালেকশন খালি তালিকা, একক রিলেশনশিপ `None` দেখাবে, ডেটাবেসে থাকলেও। ভুল ডেটা দেখানোর ঝুঁকি আছে বলে এর বদলে `raiseload()` ব্যবহার করুন।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(noload(User.addresses)).where(User.id == 1)).one()
print(u.addresses)   # []  (ডেটাবেসে দুটি ঠিকানা থাকা সত্ত্বেও!)
```

### `noload()`-এর সব প্যারামিটার { #noload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ। |

## `raiseload()` { #raiseload }

```python
from sqlalchemy.orm import raiseload
```

```python
raiseload(*keys, **kw)
```

**ধরন:** ফাংশন

রিলেশনশিপ আগেভাগে লোড করা না থাকলে পড়তে গেলেই **এরর** দেয়, চুপচাপ lazy load হতে দেয় না। async কোডে আর পারফরম্যান্স-সচেতন API-তে N+1 ধরার সেরা উপায়। `raiseload("*")` দিলে বাকি সব রিলেশনশিপে প্রযোজ্য।

**উদাহরণ:**

```python
stmt = select(User).options(selectinload(User.addresses), raiseload("*")).where(User.id == 1)
u = session.scalars(stmt).one()
print(len(u.addresses))   # 2  (আগে লোড করা, তাই চলবে)
try:
    u.posts
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError  ('User.posts' is not available due to lazy='raise')
```

### `raiseload()`-এর সব প্যারামিটার { #raiseload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ, বা সব বোঝাতে `"*"`। |
| `kw` | `sql_only=True` দিলে শুধু তখনই এরর যখন সত্যিই SQL চালাতে হতো; identity map থেকে পাওয়া গেলে (যেমন many-to-one যার অবজেক্ট আগেই সেশনে আছে) এরর দেয় না। |

## `defaultload()` { #defaultload }

```python
from sqlalchemy.orm import defaultload
```

```python
defaultload(*keys)
```

**ধরন:** ফাংশন

এই রিলেশনশিপের নিজের লোডিং **যেমন আছে তেমনই থাকবে**; শুধু চেইনের পথ হিসেবে ব্যবহার হয়, যাতে আরও ভেতরের কোনো অ্যাট্রিবিউটে অপশন দেওয়া যায়।

**উদাহরণ:**

```python
# User.posts নিজের ডিফল্টে (lazy) থাকবে, কিন্তু পোস্ট লোড হলে প্রতিটির author joined হবে
stmt = select(User).options(defaultload(User.posts).joinedload(Post.author)).where(User.id == 2)
u = session.scalars(stmt).one()
print(u.posts[0].author.name)   # করিম
```

### `defaultload()`-এর সব প্যারামিটার { #defaultload-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | পথের রিলেশনশিপ। |

## `contains_eager()` { #contains-eager }

```python
from sqlalchemy.orm import contains_eager
```

```python
contains_eager(*keys, **kw)
```

**ধরন:** ফাংশন

কুয়েরিতে আপনি **নিজেই** JOIN করেছেন (সাধারণত ফিল্টার করতে); সেই JOIN-এর কলাম দিয়েই রিলেশনশিপ ভরে দিতে বলে, আলাদা কুয়েরি ছাড়া। সতর্কতা: ফিল্টার করা JOIN হলে রিলেশনশিপে শুধু ফিল্টারে টেকা রো থাকবে।

**উদাহরণ:**

```python
stmt = (select(User).join(User.addresses).where(Address.email.like("%work%"))
        .options(contains_eager(User.addresses)))
u = session.scalars(stmt).unique().one()
print(u.name, [a.email for a in u.addresses])   # রহিম ['rahim@work.com']  (শুধু ফিল্টার হওয়া ঠিকানা)
```

### `contains_eager()`-এর সব প্যারামিটার { #contains-eager-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keys` | কোন রিলেশনশিপ (চেইন করা যায়)। |
| `kw` | `alias=` : JOIN-এ `aliased()` টার্গেট ব্যবহার করলে সেই alias দিন, যাতে SQLAlchemy সঠিক কলাম থেকে পড়ে। |

**aliased টার্গেটের সাথে**

```python
a = aliased(Address)
stmt = select(User).join(User.addresses.of_type(a)).options(contains_eager(User.addresses.of_type(a)))
users = session.scalars(stmt.order_by(User.id)).unique().all()
print([(u.name, len(u.addresses)) for u in users])   # [('রহিম', 2), ('সুমি', 1)]
```

## কলাম লোডিং অপশন { #load-only-group }

## `load_only()` { #load-only }

```python
from sqlalchemy.orm import load_only
```

```python
load_only(*attrs, raiseload=False)
```

**ধরন:** ফাংশন

শুধু দেওয়া কলামগুলো (আর primary key) লোড করে; বাকি সব কলাম deferred হয়, পরে পড়লে আলাদা SELECT চলে। বড় টেবিলের তালিকা-পেজে হালকা কুয়েরির জন্য।

**উদাহরণ:**

```python
with count_sql() as q:
    u = session.scalars(select(User).options(load_only(User.name)).where(User.id == 1)).one()
    print("bio" in q[0])   # False  (bio আনা হয়নি)
    print(u.bio)           # রহিমের লম্বা জীবনী  (এখন আলাদা SELECT চলল)
print(len(q))              # 2
```

### `load_only()`-এর সব প্যারামিটার { #load-only-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attrs` | যে কলামগুলো লোড হবে। |
| `raiseload` | `True` দিলে বাদ পড়া কলাম পড়তে গেলে lazy load না করে এরর দেবে (async-এ দরকারি)। |

## `defer()` { #defer }

```python
from sqlalchemy.orm import defer
```

```python
defer(key, *, raiseload=False)
```

**ধরন:** ফাংশন

`load_only()`-এর উল্টো: শুধু দেওয়া কলামটি বাদ দেয়, বাকি সব লোড হয়।

**উদাহরণ:**

```python
u = session.scalars(select(Post).options(defer(Post.title, raiseload=True)).where(Post.id == 1)).one()
print(u.published)   # True
try:
    u.title
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError
```

### `defer()`-এর সব প্যারামিটার { #defer-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | যে কলামটি লোড হবে না। |
| `raiseload` | `True` দিলে সেটি পড়তে গেলে এরর (lazy load নয়)। |

## `undefer()` { #undefer }

```python
from sqlalchemy.orm import undefer
```

```python
undefer(key)
```

**ধরন:** ফাংশন

মডেলে `deferred=True` দেওয়া কলামকে এই কুয়েরিতে সাথেই লোড করে।

**উদাহরণ:**

```python
with count_sql() as q:
    u = session.scalars(select(User).options(undefer(User.bio)).where(User.id == 1)).one()
    print(u.bio)   # রহিমের লম্বা জীবনী
print(len(q))      # 1
```

### `undefer()`-এর সব প্যারামিটার { #undefer-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | যে deferred কলামটি লোড হবে। |

## `undefer_group()` { #undefer-group }

```python
from sqlalchemy.orm import undefer_group
```

```python
undefer_group(name)
```

**ধরন:** ফাংশন

একই `deferred_group`-এর সব deferred কলাম একসাথে লোড করে।

**উদাহরণ:**

```python
with count_sql() as q:
    u = session.scalars(select(User).options(undefer_group("profile")).where(User.id == 1)).one()
    print(u.bio, u.avatar)   # রহিমের লম্বা জীবনী r.png
print(len(q))                # 1
```

### `undefer_group()`-এর সব প্যারামিটার { #undefer-group-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | গ্রুপের নাম (মডেলে `deferred_group=`)। |

## `with_expression()` { #with-expression }

```python
from sqlalchemy.orm import with_expression
```

```python
with_expression(key, expression)
```

**ধরন:** ফাংশন

মডেলের `query_expression()` অ্যাট্রিবিউটে এই কুয়েরির জন্য একটি SQL এক্সপ্রেশনের মান বসায়। একই মডেলে কুয়েরি-ভেদে ভিন্ন হিসাব (যেমন সার্চ-স্কোর) দেখাতে।

**উদাহরণ:**

```python
n_posts = select(func.count(Post.id)).where(Post.user_id == User.id).scalar_subquery()
users = session.scalars(select(User).options(with_expression(User.score, n_posts)).order_by(User.id)).all()
print([(u.name, u.score) for u in users])   # [('রহিম', 2), ('করিম', 1), ('সুমি', 0)]
```

### `with_expression()`-এর সব প্যারামিটার { #with-expression-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | `query_expression()` দিয়ে বানানো অ্যাট্রিবিউট। |
| `expression` | যে SQL এক্সপ্রেশনের মান বসবে। |

## অন্যান্য অপশন ও Load { #selectin-polymorphic-group }

## `selectin_polymorphic()` { #selectin-polymorphic }

```python
from sqlalchemy.orm import selectin_polymorphic
```

```python
selectin_polymorphic(base_cls, classes)
```

**ধরন:** ফাংশন

inheritance-এ বেস ক্লাস কুয়েরি করলে সাবক্লাসের নিজস্ব কলামগুলো (যেমন `Engineer.lang`) প্রতিটি সাবক্লাসের জন্য একটি করে `SELECT ... WHERE id IN (...)` দিয়ে আগেভাগে লোড করে। না দিলে প্রতিটি অবজেক্টের সাবক্লাস-কলাম পড়ার সময় আলাদা কুয়েরি চলে।

**উদাহরণ:**

```python
with count_sql() as q:
    emps = session.scalars(select(Employee).options(selectin_polymorphic(Employee, [Engineer, Manager]))
                           .order_by(Employee.id)).all()
    print([getattr(e, "lang", None) or getattr(e, "team", None) for e in emps])   # ['Python', 'ব্যাকএন্ড', None]
print(len(q))   # 3  (বেস + Engineer-এর জন্য ১ + Manager-এর জন্য ১)
```

### `selectin_polymorphic()`-এর সব প্যারামিটার { #selectin-polymorphic-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base_cls` | বেস ক্লাস। |
| `classes` | যেসব সাবক্লাসের কলাম আগেভাগে লোড হবে। |

## `with_loader_criteria()` { #with-loader-criteria }

```python
from sqlalchemy.orm import with_loader_criteria
```

```python
with_loader_criteria(entity_or_base, where_criteria, loader_only=False, include_aliases=False, propagate_to_loaders=True, track_closure_variables=True)
```

**ধরন:** ফাংশন

একটি মডেলের **প্রতিটি** লোডে (মূল কুয়েরি, JOIN, আর রিলেশনশিপ লোড, সবখানে) একটি অতিরিক্ত WHERE শর্ত জুড়ে দেয়। soft delete (`deleted_at IS NULL`) বা multi-tenant (`tenant_id == x`) ফিল্টার সব জায়গায় নিশ্চিত করার সেরা উপায়; সাধারণত `do_orm_execute` event-এ বসানো হয়।

**উদাহরণ:**

```python
stmt = (select(User).where(User.id == 1)
        .options(selectinload(User.posts), with_loader_criteria(Post, Post.published == True)))
u = session.scalars(stmt).one()
print([p.title for p in u.posts])   # ['প্রথম পোস্ট']  (খসড়া বাদ)
```

### `with_loader_criteria()`-এর সব প্যারামিটার { #with-loader-criteria-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entity_or_base` | কোন মডেলে শর্ত বসবে। একটি বেস/মিক্সিন ক্লাস দিলে তার সব সাবক্লাসে। |
| `where_criteria` | শর্ত। একটি lambda-ও দেওয়া যায়: `lambda cls: cls.deleted_at.is_(None)`, তখন বেস/মিক্সিন দিয়ে সব মডেলে কাজ করে। |
| `loader_only` | `True` দিলে শুধু রিলেশনশিপ লোডে প্রযোজ্য, মূল কুয়েরিতে নয়। |
| `include_aliases` | `True` দিলে `aliased()` রূপেও শর্ত বসবে। |
| `propagate_to_loaders` | `True` (ডিফল্ট) হলে পরে চলা lazy load-এও শর্ত বহাল থাকে। |
| `track_closure_variables` | lambda শর্তে বাইরের ভেরিয়েবল ক্যাশ-key-তে ধরা হবে কি না (ডিফল্ট `True`)। |

**event দিয়ে সব কুয়েরিতে soft-delete/tenant ফিল্টার**

```python
@event.listens_for(Session, "do_orm_execute")
def _only_published(state):
    if state.is_select:
        state.statement = state.statement.options(
            with_loader_criteria(Post, lambda cls: cls.published == True, include_aliases=True))

print(len(session.scalars(select(Post)).all()))   # 2  (খসড়া আপনাআপনি বাদ)
event.remove(Session, "do_orm_execute", _only_published)
```

## `Load` { #load }

```python
from sqlalchemy.orm import Load
```

লোডার অপশনের "চেইন" অবজেক্ট। `selectinload(...)` ইত্যাদি ফাংশন আসলে ভেতরে একটি `Load` বানায়। সরাসরি `Load(User)` লিখলে নির্দিষ্ট এন্টিটি থেকে শুরু করে অপশন দেওয়া যায়, যা একাধিক এন্টিটির কুয়েরিতে (যেমন `select(User, Address)`) কাজে লাগে। নিচের প্রতিটি মেথড একই নামের ফাংশনের মতো কাজ করে এবং নতুন `Load` ফেরত দেয়, তাই চেইন করা যায়।

**উদাহরণ:**

```python
stmt = select(User, Address).join(User.addresses).options(Load(User).load_only(User.name))
print("bio" in str(stmt))   # False
```

### কনস্ট্রাক্টরের প্যারামিটার { #load-params }

```python
Load(entity)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entity` | যে মডেল (বা aliased) থেকে অপশনের পথ শুরু। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #load-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`additional_source_entities`](#load-additional-source-entities) | অ্যাট্রিবিউট (internal) | ভেতরের: পথ মেলাতে আর কোন কোন এন্টিটি বিবেচনা হবে। |
| [`contains_eager()`](#load-contains-eager) | মেথড | চেইনে `contains_eager()` প্রয়োগ করে। |
| [`context`](#load-context) | অ্যাট্রিবিউট (internal) | ভেতরের: এই চেইনের প্রতিটি ধাপের অপশন-তথ্যের tuple। |
| [`defaultload()`](#load-defaultload) | মেথড | চেইনে `defaultload()` প্রয়োগ করে (শুধু পথ, লোডিং বদলায় না)। |
| [`defer()`](#load-defer) | মেথড | চেইনে `defer()` প্রয়োগ করে। |
| [`get_children()`](#load-get-children) | মেথড (internal) | ক্যাশ/traversal ব্যবস্থার জন্য ভেতরের child এলিমেন্ট দেয়। |
| [`immediateload()`](#load-immediateload) | মেথড | চেইনে `immediateload()` প্রয়োগ করে। |
| [`inherit_cache`](#load-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ। |
| [`joinedload()`](#load-joinedload) | মেথড | চেইনে `joinedload()` প্রয়োগ করে। |
| [`lazyload()`](#load-lazyload) | মেথড | চেইনে `lazyload()` প্রয়োগ করে। |
| [`load_only()`](#load-load-only) | মেথড | চেইনে `load_only()` প্রয়োগ করে। |
| [`noload()`](#load-noload) | মেথড (legacy) | চেইনে `noload()` প্রয়োগ করে। |
| [`options()`](#load-options) | মেথড | এই পথের নিচে একসাথে একাধিক উপ-অপশন বসায়: একই রিলেশনশিপের ভেতরে কয়েকটি জিনিস একবারে বলতে। |
| [`path`](#load-path) | অ্যাট্রিবিউট (internal) | ভেতরের: অপশনটি কোন এন্টিটি-পথে প্রযোজ্য। |
| [`process_compile_state()`](#load-process-compile-state) | মেথড (internal) | কুয়েরি কম্পাইলের সময় SQLAlchemy নিজে ডাকে, অপশনটি প্রয়োগ করতে। |
| [`process_compile_state_replaced_entities()`](#load-process-compile-state-replaced-entities) | মেথড (internal) | `with_only_columns()` ইত্যাদিতে এন্টিটি বদলালে কম্পাইলের সময় SQLAlchemy নিজে ডাকে। |
| [`propagate_to_loaders`](#load-propagate-to-loaders) | অ্যাট্রিবিউট (internal) | অপশনটি পরের lazy load-এও বহাল থাকবে কি না (লোডার অপশনে `True`)। |
| [`raiseload()`](#load-raiseload) | মেথড | চেইনে `raiseload()` প্রয়োগ করে। |
| [`selectin_polymorphic()`](#load-selectin-polymorphic) | মেথড | চেইনে `selectin_polymorphic()` প্রয়োগ করে (বেস ক্লাস থেকে শুরু করা `Load`-এ)। |
| [`selectinload()`](#load-selectinload) | মেথড | চেইনে `selectinload()` প্রয়োগ করে। |
| [`subqueryload()`](#load-subqueryload) | মেথড (legacy) | চেইনে `subqueryload()` প্রয়োগ করে। |
| [`undefer()`](#load-undefer) | মেথড | চেইনে `undefer()` প্রয়োগ করে। |
| [`undefer_group()`](#load-undefer-group) | মেথড | চেইনে `undefer_group()` প্রয়োগ করে। |
| [`with_expression()`](#load-with-expression) | মেথড | চেইনে `with_expression()` প্রয়োগ করে। |

### `Load.additional_source_entities` { #load-additional-source-entities }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের: পথ মেলাতে আর কোন কোন এন্টিটি বিবেচনা হবে।

### `Load.contains_eager()` { #load-contains-eager }

```python
Load.contains_eager(attr, alias=None)
```

**ধরন:** মেথড

চেইনে `contains_eager()` প্রয়োগ করে।

**উদাহরণ:**

```python
stmt = select(User).join(User.addresses).options(Load(User).contains_eager(User.addresses))
print(len(session.scalars(stmt).unique().all()))   # 2
```

### `Load.context` { #load-context }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের: এই চেইনের প্রতিটি ধাপের অপশন-তথ্যের tuple।

### `Load.defaultload()` { #load-defaultload }

```python
Load.defaultload(attr)
```

**ধরন:** মেথড

চেইনে `defaultload()` প্রয়োগ করে (শুধু পথ, লোডিং বদলায় না)।

**উদাহরণ:**

```python
opt = Load(User).defaultload(User.posts).joinedload(Post.author)
print(session.scalars(select(User).options(opt).where(User.id == 2)).one().posts[0].author.name)   # করিম
```

### `Load.defer()` { #load-defer }

```python
Load.defer(key, raiseload=False)
```

**ধরন:** মেথড

চেইনে `defer()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).defer(User.name)).where(User.id == 3)).one()
print("name" in u.__dict__)   # False
```

### `Load.get_children()` { #load-get-children }

```python
Load.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ/traversal ব্যবস্থার জন্য ভেতরের child এলিমেন্ট দেয়।

### `Load.immediateload()` { #load-immediateload }

```python
Load.immediateload(attr, recursion_depth=None)
```

**ধরন:** মেথড

চেইনে `immediateload()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).immediateload(User.posts)).where(User.id == 1)).one()
print("posts" in u.__dict__)   # True
```

### `Load.inherit_cache` { #load-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ।

### `Load.joinedload()` { #load-joinedload }

```python
Load.joinedload(attr, innerjoin=None)
```

**ধরন:** মেথড

চেইনে `joinedload()` প্রয়োগ করে।

**উদাহরণ:**

```python
a = session.scalars(select(Address).options(Load(Address).joinedload(Address.user, innerjoin=True))
                    .where(Address.id == 3)).one()
print(a.user.name)   # সুমি
```

### `Load.lazyload()` { #load-lazyload }

```python
Load.lazyload(attr)
```

**ধরন:** মেথড

চেইনে `lazyload()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).lazyload(User.posts)).where(User.id == 1)).one()
print("posts" in u.__dict__)   # False
```

### `Load.load_only()` { #load-load-only }

```python
Load.load_only(*attrs, raiseload=False)
```

**ধরন:** মেথড

চেইনে `load_only()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).load_only(User.name)).where(User.id == 1)).one()
print(sorted(k for k in u.__dict__ if not k.startswith("_")))   # ['id', 'name']
```

### `Load.noload()` { #load-noload }

```python
Load.noload(attr)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

চেইনে `noload()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).noload(User.posts)).where(User.id == 1)).one()
print(u.posts)   # []
```

### `Load.options()` { #load-options }

```python
Load.options(*opts)
```

**ধরন:** মেথড

এই পথের নিচে একসাথে একাধিক উপ-অপশন বসায়: একই রিলেশনশিপের ভেতরে কয়েকটি জিনিস একবারে বলতে।

**উদাহরণ:**

```python
opt = selectinload(User.posts).options(load_only(Post.title), joinedload(Post.author))
u = session.scalars(select(User).options(opt).where(User.id == 1)).one()
print([p.title for p in u.posts], u.posts[0].author.name)   # ['প্রথম পোস্ট', 'খসড়া'] রহিম
```

### `Load.path` { #load-path }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের: অপশনটি কোন এন্টিটি-পথে প্রযোজ্য।

### `Load.process_compile_state()` { #load-process-compile-state }

```python
Load.process_compile_state(compile_state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কুয়েরি কম্পাইলের সময় SQLAlchemy নিজে ডাকে, অপশনটি প্রয়োগ করতে।

### `Load.process_compile_state_replaced_entities()` { #load-process-compile-state-replaced-entities }

```python
Load.process_compile_state_replaced_entities(compile_state, mapper_entities)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`with_only_columns()` ইত্যাদিতে এন্টিটি বদলালে কম্পাইলের সময় SQLAlchemy নিজে ডাকে।

### `Load.propagate_to_loaders` { #load-propagate-to-loaders }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অপশনটি পরের lazy load-এও বহাল থাকবে কি না (লোডার অপশনে `True`)।

### `Load.raiseload()` { #load-raiseload }

```python
Load.raiseload(attr, sql_only=False)
```

**ধরন:** মেথড

চেইনে `raiseload()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).raiseload("*")).where(User.id == 1)).one()
try:
    u.addresses
except Exception as e:
    print(type(e).__name__)   # InvalidRequestError
```

### `Load.selectin_polymorphic()` { #load-selectin-polymorphic }

```python
Load.selectin_polymorphic(classes)
```

**ধরন:** মেথড

চেইনে `selectin_polymorphic()` প্রয়োগ করে (বেস ক্লাস থেকে শুরু করা `Load`-এ)।

**উদাহরণ:**

```python
emps = session.scalars(select(Employee).options(Load(Employee).selectin_polymorphic([Engineer]))).all()
print(sorted(type(e).__name__ for e in emps))   # ['Employee', 'Engineer', 'Manager']
```

### `Load.selectinload()` { #load-selectinload }

```python
Load.selectinload(attr, recursion_depth=None, chunksize=None)
```

**ধরন:** মেথড

চেইনে `selectinload()` প্রয়োগ করে।

**উদাহরণ:**

```python
users = session.scalars(select(User).options(Load(User).selectinload(User.addresses, chunksize=2))).all()
print(sum(len(u.addresses) for u in users))   # 3
```

### `Load.subqueryload()` { #load-subqueryload }

```python
Load.subqueryload(attr)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

চেইনে `subqueryload()` প্রয়োগ করে।

**উদাহরণ:**

```python
users = session.scalars(select(User).options(Load(User).subqueryload(User.addresses))).all()
print(sum(len(u.addresses) for u in users))   # 3
```

### `Load.undefer()` { #load-undefer }

```python
Load.undefer(key)
```

**ধরন:** মেথড

চেইনে `undefer()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).undefer(User.avatar)).where(User.id == 2)).one()
print(u.__dict__["avatar"])   # k.png
```

### `Load.undefer_group()` { #load-undefer-group }

```python
Load.undefer_group(name)
```

**ধরন:** মেথড

চেইনে `undefer_group()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).undefer_group("profile")).where(User.id == 3)).one()
print(u.__dict__["bio"])   # সুমির জীবনী
```

### `Load.with_expression()` { #load-with-expression }

```python
Load.with_expression(key, expression)
```

**ধরন:** মেথড

চেইনে `with_expression()` প্রয়োগ করে।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(Load(User).with_expression(User.score, literal(42)))
                    .where(User.id == 1)).one()
print(u.score)   # 42
```

## ORM কুয়েরি হেল্পার { #aliased-group }

## `aliased()` { #aliased }

```python
from sqlalchemy.orm import aliased
```

```python
aliased(element, alias=None, name=None, flat=False, adapt_on_names=False)
```

**ধরন:** ফাংশন

একটি মডেলের "ছদ্মনাম" (SQL-এ `AS u2`) বানায়, যাতে একই টেবিল কুয়েরিতে দুবার ব্যবহার করা যায় (self-join, দুটি ভিন্ন শর্তে একই টেবিলে JOIN), বা একটি সাবকুয়েরিকে মডেলের মতো ব্যবহার করা যায়।

**উদাহরণ:**

```python
a1, a2 = aliased(Address), aliased(Address)
stmt = (select(User.name).join(a1, User.addresses).join(a2, User.addresses)
        .where(a1.email.like("%example%"), a2.email.like("%work%")))
print(session.scalars(stmt).all())   # ['রহিম']
```

### `aliased()`-এর সব প্যারামিটার { #aliased-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে মডেল, টেবিল বা সাবকুয়েরির alias চাই। |
| `alias` | একটি সাবকুয়েরি/selectable; দিলে মডেলটি সেই সাবকুয়েরির ওপর ম্যাপ হয় (মডেলের মতো ব্যবহার করা যায়)। |
| `name` | SQL-এ alias-এর নাম। |
| `flat` | joined inheritance-এর মডেলে প্রতিটি টেবিলকে আলাদা alias দেয়, সাবকুয়েরিতে মোড়ায় না (JOIN-এ দ্রুততর)। |
| `adapt_on_names` | সাবকুয়েরির কলাম নাম মিলিয়ে মডেলের অ্যাট্রিবিউটে বসায় (কলাম সরাসরি টেবিল থেকে না এলে, যেমন হিসাব করা কলাম)। |

**সাবকুয়েরিকে মডেল হিসেবে**

```python
sub = select(User).where(User.id > 1).subquery()
Later = aliased(User, sub)
print(session.scalars(select(Later.name).order_by(Later.id)).all())   # ['করিম', 'সুমি']
```

## `with_polymorphic()` { #with-polymorphic }

```python
from sqlalchemy.orm import with_polymorphic
```

```python
with_polymorphic(base, classes, selectable=False, flat=False, polymorphic_on=None, aliased=False, innerjoin=False, adapt_on_names=False, name=None)
```

**ধরন:** ফাংশন

inheritance-এ একটি বিশেষ alias বানায় যাতে বেস আর দেওয়া সাবক্লাসগুলোর টেবিল একসাথে (LEFT OUTER JOIN) কুয়েরি হয়। ফলে সাবক্লাসের কলাম দিয়ে ফিল্টার করা যায় (`emp.Engineer.lang == ...`) আর সব কলাম এক কুয়েরিতে আসে।

**উদাহরণ:**

```python
emp = with_polymorphic(Employee, [Engineer, Manager])
stmt = select(emp).where((emp.Engineer.lang == "Python") | (emp.Manager.team == "ব্যাকএন্ড")).order_by(emp.id)
print([e.name for e in session.scalars(stmt)])   # ['আলিফ', 'বৃষ্টি']
```

### `with_polymorphic()`-এর সব প্যারামিটার { #with-polymorphic-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `base` | বেস ক্লাস। |
| `classes` | যেসব সাবক্লাস JOIN হবে; সব চাইলে `"*"`। |
| `selectable` | নিজের বানানো selectable (যেমন `polymorphic_union`) ব্যবহার করতে। |
| `flat` | সাবকুয়েরিতে না মুড়িয়ে প্রতিটি টেবিলকে আলাদা alias দেয়; অন্য JOIN-এর অংশ হলে দরকার। |
| `polymorphic_on` | discriminator কলাম বদলে দিতে (বিশেষ ক্ষেত্রে)। |
| `aliased` | `True` দিলে alias করা রূপ, যাতে একই কুয়েরিতে বেস টেবিল আবার ব্যবহার করা যায়। |
| `innerjoin` | `True` দিলে LEFT OUTER-এর বদলে INNER JOIN। |
| `adapt_on_names` | `aliased()`-এর মতো, কলাম নাম মিলিয়ে বসানো। |
| `name` | alias-এর নাম। |

## `with_parent()` { #with-parent }

```python
from sqlalchemy.orm import with_parent
```

```python
with_parent(instance, prop, from_entity=None)
```

**ধরন:** ফাংশন

একটি অবজেক্ট আর তার রিলেশনশিপ থেকে WHERE শর্ত বানায়: "এই ইউজারের ঠিকানাগুলো"। রিলেশনশিপ লোড না করেই, অতিরিক্ত ফিল্টার/পেজিনেশনসহ সম্পর্কিত রো আনতে কাজে লাগে।

**উদাহরণ:**

```python
rahim = session.get(User, 1)
stmt = select(Address.email).where(with_parent(rahim, User.addresses)).order_by(Address.email)
print(session.scalars(stmt).all())   # ['rahim@example.com', 'rahim@work.com']
```

### `with_parent()`-এর সব প্যারামিটার { #with-parent-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | প্যারেন্ট অবজেক্ট। |
| `prop` | রিলেশনশিপ অ্যাট্রিবিউট (যেমন `User.addresses`)। |
| `from_entity` | টার্গেট মডেলের একটি `aliased()` রূপ ব্যবহার করলে সেটি। |

## `join()` { #orm-join }

```python
from sqlalchemy.orm import join
```

```python
join(left, right, onclause=None, isouter=False, full=False)
```

**ধরন:** ফাংশন

দুটি মডেল/টেবিলের মধ্যে একটি `Join` অবজেক্ট বানায় (`select_from()`-এ দিতে)। Core-এর `join()`-এর মতো, কিন্তু ON শর্তে রিলেশনশিপ অ্যাট্রিবিউট (`User.addresses`) দেওয়া যায়। সাধারণত `select(...).join(...)` লেখাই সহজ।

**উদাহরণ:**

```python
j = join(User, Address, User.addresses)
stmt = select(User.name, Address.email).select_from(j).order_by(Address.id)
print(session.execute(stmt).first())   # ('রহিম', 'rahim@example.com')
```

### `join()`-এর সব প্যারামিটার { #orm-join-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `left` | বাম দিক (মডেল, টেবিল বা আগের join)। |
| `right` | ডান দিক। |
| `onclause` | ON শর্ত: রিলেশনশিপ অ্যাট্রিবিউট বা SQL এক্সপ্রেশন; না দিলে ফরেন কি থেকে বোঝে। |
| `isouter` | `True` দিলে LEFT OUTER JOIN। |
| `full` | `True` দিলে FULL OUTER JOIN। |

## `outerjoin()` { #orm-outerjoin }

```python
from sqlalchemy.orm import outerjoin
```

```python
outerjoin(left, right, onclause=None, full=False)
```

**ধরন:** ফাংশন

`join(..., isouter=True)`-এর ছোট রূপ: LEFT OUTER JOIN।

**উদাহরণ:**

```python
j = outerjoin(User, Address, User.addresses)
stmt = select(User.name, func.count(Address.id)).select_from(j).group_by(User.name).order_by(User.name)
print(session.execute(stmt).all())   # [('করিম', 0), ('রহিম', 2), ('সুমি', 1)]
```

### `outerjoin()`-এর সব প্যারামিটার { #orm-outerjoin-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `left` | বাম দিক। |
| `right` | ডান দিক। |
| `onclause` | ON শর্ত। |
| `full` | `True` দিলে FULL OUTER JOIN। |

## `Bundle` { #bundle }

```python
from sqlalchemy.orm import Bundle
```

কয়েকটি কলামকে একটি নামের নিচে "বান্ডিল" করে; রেজাল্টের প্রতিটি রো-তে সেগুলো একটি নেস্টেড tuple-এর মতো আসে (`row.user.name`)। সাবক্লাস করে `create_row_processor()` বদলালে বান্ডিল থেকে dict বা নিজের অবজেক্ট বানানো যায়।

**উদাহরণ:**

```python
b = Bundle("user", User.id, User.name)
row = session.execute(select(b, Address.email).join(User.addresses).order_by(Address.id)).first()
print(row.user.name, row.email)   # রহিম rahim@example.com
```

### কনস্ট্রাক্টরের প্যারামিটার { #bundle-params }

```python
Bundle(name, *exprs, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | বান্ডিলের নাম (রো-তে এই নামে পাওয়া যাবে)। |
| `exprs` | বান্ডিলে যে কলাম/এক্সপ্রেশনগুলো থাকবে। |
| `kw` | `single_entity=True` দিলে শুধু এই বান্ডিল select করলে রো-র বদলে সরাসরি বান্ডিলের মান আসে (`scalars()`-এর মতো)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bundle-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`allows_lambda`](#bundle-allows-lambda) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না। |
| [`c`](#bundle-c) | অ্যাট্রিবিউট | `columns`-এর ছোট নাম। |
| [`clauses`](#bundle-clauses) | প্রপার্টি | বান্ডিলের এক্সপ্রেশনগুলোর তালিকা (SELECT-এ যে কলামগুলো বসবে)। |
| [`columns`](#bundle-columns) | অ্যাট্রিবিউট | বান্ডিলের কলামগুলো নাম অনুযায়ী, যাতে `WHERE`/`ORDER BY`-তে ব্যবহার করা যায়। |
| [`create_row_processor()`](#bundle-create-row-processor) | মেথড | রো থেকে বান্ডিলের মান কীভাবে বানানো হবে তা ঠিক করে। |
| [`entity`](#bundle-entity) | প্রপার্টি (internal) | inspection API: বান্ডিলের কলামগুলো যে মডেলের, তার mapper/এন্টিটি (থাকলে)। |
| [`entity_namespace`](#bundle-entity-namespace) | প্রপার্টি (internal) | `filter_by()`-এ নাম দিয়ে কলাম খোঁজার নাম-ভান্ডার (এখানে `c`)। |
| [`exprs`](#bundle-exprs) | অ্যাট্রিবিউট | বান্ডিলে দেওয়া এক্সপ্রেশনগুলোর তালিকা, যে ক্রমে দেওয়া হয়েছিল। |
| [`extension_type`](#bundle-extension-type) | অ্যাট্রিবিউট (internal) | inspection API-র ভেতরের টাইপ-চিহ্ন। |
| [`get_children()`](#bundle-get-children) | মেথড (internal) | traversal ব্যবস্থার জন্য ভেতরের child এলিমেন্ট দেয়। |
| [`inherit_cache`](#bundle-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ। |
| [`is_aliased_class`](#bundle-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_attribute`](#bundle-is-attribute) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_bundle`](#bundle-is-bundle) | অ্যাট্রিবিউট | inspection-এ এটি একটি বান্ডিল কি না বোঝায়: এখানে `True`। |
| [`is_clause_element`](#bundle-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_instance`](#bundle-is-instance) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_mapper`](#bundle-is-mapper) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_property`](#bundle-is-property) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_selectable`](#bundle-is-selectable) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`label()`](#bundle-label) | মেথড | একই কলামের কিন্তু নতুন নামের একটি বান্ডিলের কপি দেয়। |
| [`mapper`](#bundle-mapper) | প্রপার্টি | বান্ডিলের কলামগুলো যে মডেলের, তার `Mapper` (কোনো মডেলের কলাম না থাকলে `None`)। |
| [`memoized_attribute`](#bundle-memoized-attribute) | অ্যাট্রিবিউট (internal) | ভেতরের ডেকোরেটর। |
| [`memoized_instancemethod()`](#bundle-memoized-instancemethod) | ক্লাস মেথড (internal) | ভেতরের ডেকোরেটর। |
| [`name`](#bundle-name) | অ্যাট্রিবিউট | বান্ডিলের নাম। |
| [`proxy_set`](#bundle-proxy-set) | অ্যাট্রিবিউট (internal) | ভেতরের: কলাম-মিলানোর (lineage) সেট। |
| [`single_entity`](#bundle-single-entity) | অ্যাট্রিবিউট | `single_entity=True` দিয়ে বানানো হলে `True`: তখন শুধু এই বান্ডিল select করলে রো ছাড়াই মান আসে। |
| [`uses_inspection`](#bundle-uses-inspection) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ। |

### `Bundle.allows_lambda` { #bundle-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না।

### `Bundle.c` { #bundle-c }

**ধরন:** অ্যাট্রিবিউট

`columns`-এর ছোট নাম।

**উদাহরণ:**

```python
print(Bundle("u", User.id, User.name).c.name)   # users.name
```

### `Bundle.clauses` { #bundle-clauses }

**ধরন:** প্রপার্টি

বান্ডিলের এক্সপ্রেশনগুলোর তালিকা (SELECT-এ যে কলামগুলো বসবে)।

**উদাহরণ:**

```python
print([c.name for c in Bundle("u", User.id, User.name).clauses])   # ['id', 'name']
```

### `Bundle.columns` { #bundle-columns }

**ধরন:** অ্যাট্রিবিউট

বান্ডিলের কলামগুলো নাম অনুযায়ী, যাতে `WHERE`/`ORDER BY`-তে ব্যবহার করা যায়।

**উদাহরণ:**

```python
b = Bundle("u", User.id, User.name)
print(session.execute(select(b).order_by(b.columns.name.desc())).first().u.name)   # সুমি
```

### `Bundle.create_row_processor()` { #bundle-create-row-processor }

```python
Bundle.create_row_processor(query, procs, labels)
```

**ধরন:** মেথড

রো থেকে বান্ডিলের মান কীভাবে বানানো হবে তা ঠিক করে। সাবক্লাসে বদলে dict বা নিজের অবজেক্ট ফেরত দেওয়া যায়।

**উদাহরণ:**

```python
class DictBundle(Bundle):
    def create_row_processor(self, query, procs, labels):
        def proc(row):
            return dict(zip(labels, (p(row) for p in procs)))
        return proc

b = DictBundle("user", User.id, User.name)
print(session.execute(select(b).where(User.id == 2)).scalar_one())   # {'id': 2, 'name': 'করিম'}
```

### `Bundle.entity` { #bundle-entity }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection API: বান্ডিলের কলামগুলো যে মডেলের, তার mapper/এন্টিটি (থাকলে)।

### `Bundle.entity_namespace` { #bundle-entity-namespace }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`filter_by()`-এ নাম দিয়ে কলাম খোঁজার নাম-ভান্ডার (এখানে `c`)।

### `Bundle.exprs` { #bundle-exprs }

**ধরন:** অ্যাট্রিবিউট

বান্ডিলে দেওয়া এক্সপ্রেশনগুলোর তালিকা, যে ক্রমে দেওয়া হয়েছিল।

**উদাহরণ:**

```python
print(len(Bundle("u", User.id, User.name).exprs))   # 2
```

### `Bundle.extension_type` { #bundle-extension-type }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection API-র ভেতরের টাইপ-চিহ্ন।

### `Bundle.get_children()` { #bundle-get-children }

```python
Bundle.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

traversal ব্যবস্থার জন্য ভেতরের child এলিমেন্ট দেয়।

### `Bundle.inherit_cache` { #bundle-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ।

### `Bundle.is_aliased_class` { #bundle-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_attribute` { #bundle-is-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_bundle` { #bundle-is-bundle }

**ধরন:** অ্যাট্রিবিউট

inspection-এ এটি একটি বান্ডিল কি না বোঝায়: এখানে `True`।

**উদাহরণ:**

```python
print(Bundle("u", User.id).is_bundle)   # True
```

### `Bundle.is_clause_element` { #bundle-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_instance` { #bundle-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_mapper` { #bundle-is-mapper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_property` { #bundle-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.is_selectable` { #bundle-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `Bundle.label()` { #bundle-label }

```python
Bundle.label(name)
```

**ধরন:** মেথড

একই কলামের কিন্তু নতুন নামের একটি বান্ডিলের কপি দেয়।

**উদাহরণ:**

```python
b = Bundle("u", User.id, User.name).label("person")
print(session.execute(select(b).where(User.id == 1)).first().person.name)   # রহিম
```

### `Bundle.mapper` { #bundle-mapper }

**ধরন:** প্রপার্টি

বান্ডিলের কলামগুলো যে মডেলের, তার `Mapper` (কোনো মডেলের কলাম না থাকলে `None`)।

**উদাহরণ:**

```python
print(Bundle("u", User.id, User.name).mapper.class_.__name__)   # User
```

### `Bundle.memoized_attribute` { #bundle-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `Bundle.memoized_instancemethod()` { #bundle-memoized-instancemethod }

```python
Bundle.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ডেকোরেটর।

### `Bundle.name` { #bundle-name }

**ধরন:** অ্যাট্রিবিউট

বান্ডিলের নাম।

**উদাহরণ:**

```python
print(Bundle("u", User.id).name)   # u
```

### `Bundle.proxy_set` { #bundle-proxy-set }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের: কলাম-মিলানোর (lineage) সেট।

### `Bundle.single_entity` { #bundle-single-entity }

**ধরন:** অ্যাট্রিবিউট

`single_entity=True` দিয়ে বানানো হলে `True`: তখন শুধু এই বান্ডিল select করলে রো ছাড়াই মান আসে।

**উদাহরণ:**

```python
b = Bundle("u", User.id, User.name, single_entity=True)
print(session.execute(select(b).where(User.id == 3)).first()[0].name)   # সুমি
```

### `Bundle.uses_inspection` { #bundle-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ।

/// check | সংক্ষেপে মনে রাখুন

* কালেকশন → `selectinload()`; একক অবজেক্ট → `joinedload()`; নিজের JOIN থেকে ভরাতে → `contains_eager()`।
* async বা API-তে `raiseload("*")` দিয়ে ভুলে যাওয়া lazy load সাথে সাথে ধরুন।
* চেইন: `selectinload(User.posts).joinedload(Post.author)`; একই পথে কয়েকটি: `.options(...)`।
* হালকা কুয়েরি: `load_only()`, `defer()`; deferred কলাম আনতে `undefer()` / `undefer_group()`।
* সব কুয়েরিতে বাধ্যতামূলক ফিল্টার (soft delete, tenant): `with_loader_criteria()` + `do_orm_execute` event।
* একই টেবিল দুবার: `aliased()`; inheritance-এ সাবক্লাস কলাম দিয়ে ফিল্টার: `with_polymorphic()`।

///
