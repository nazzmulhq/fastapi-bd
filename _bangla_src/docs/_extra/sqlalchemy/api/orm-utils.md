# ORM সহায়ক ফাংশন: flag_modified, get_history, set_committed_value, aliased-এর ক্লাস { #api-orm-utils }

/// note | এই পেজে যা আছে

`sqlalchemy.orm.attributes` আর `sqlalchemy.orm.util`-এর সহায়ক ফাংশন:

* **বদল জানানো/পড়া:** `flag_modified()` (JSON/ARRAY কলামের ভেতরের বদল ধরাতে, **খুব দরকারি**), `flag_dirty()`, `get_history()` আর `History`।
* **ইভেন্ট ছাড়া/সহ মান বসানো:** `set_committed_value()`, `set_attribute()`, `get_attribute()`, `del_attribute()`, `init_collection()`।
* **অবস্থা:** `instance_state()`, `object_state()`, `is_instrumented()`, `identity_key()`।
* `aliased()` যা বানায়: `AliasedClass` আর তার inspect রূপ `AliasedInsp`।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    prefs: Mapped[dict] = mapped_column(JSON, default=dict)    # সাধারণ JSON (Mutable নয়)
    addresses: Mapped[list["Address"]] = relationship()
```

ডেটা: User ১ "রহিম" (`prefs={"theme": "dark"}`, দুটি ঠিকানা)। `session` খোলা। SQLite মেমোরিতে চালানো।

///

## বদল জানানো ও পড়া { #flag-modified-group }

## `flag_modified()` { #flag-modified }

```python
from sqlalchemy.orm.attributes import flag_modified
```

```python
flag_modified(instance, key)
```

**ধরন:** ফাংশন

একটি অ্যাট্রিবিউটকে জোর করে "বদলেছে" চিহ্নিত করে, যাতে পরের flush-এ UPDATE হয়। **কেন লাগে:** সাধারণ `JSON`/`ARRAY` কলামের **ভেতরের** বদল (`user.prefs["theme"] = "light"`) SQLAlchemy ধরতে পারে না, কারণ অ্যাট্রিবিউটটি নিজে নতুন অবজেক্ট পায়নি। তখন হয় `flag_modified(user, "prefs")` ডাকুন, নয়তো নতুন dict বসান (`user.prefs = {**user.prefs, "theme": "light"}`), নয়তো [`MutableDict`](mutable.md#mutabledict) ব্যবহার করুন।

**উদাহরণ:**

```python
u.prefs["theme"] = "light"            # ভেতরের বদল
session.commit()
print(session.get(User, 1).prefs)   # {'theme': 'dark'}  (হারিয়ে গেল! UPDATE হয়নি)
u = session.get(User, 1)
u.prefs["theme"] = "light"
flag_modified(u, "prefs")             # SQLAlchemy-কে জানালাম
session.commit()
print(session.get(User, 1).prefs)   # {'theme': 'light'}
```

### `flag_modified()`-এর সব প্যারামিটার { #flag-modified-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |

## `flag_dirty()` { #flag-dirty }

```python
from sqlalchemy.orm.attributes import flag_dirty
```

```python
flag_dirty(instance)
```

**ধরন:** ফাংশন

অবজেক্টটিকে "dirty" (বদলানো) চিহ্নিত করে, কোনো নির্দিষ্ট অ্যাট্রিবিউট ছাড়া। ফলে flush-এ `before_update` ইত্যাদি ইভেন্ট চলে, যদিও কোনো কলাম বদলায়নি বলে আসল UPDATE SQL না-ও যেতে পারে। নিজের ইভেন্ট-লজিক চালাতে।

**উদাহরণ:**

```python
flag_dirty(u)
print(u in session.dirty, session.is_modified(u))   # True False
```

### `flag_dirty()`-এর সব প্যারামিটার { #flag-dirty-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |

## `get_history()` { #get-history }

```python
from sqlalchemy.orm.attributes import get_history
```

```python
get_history(obj, key, passive=symbol('PASSIVE_OFF'))
```

**ধরন:** ফাংশন

একটি অ্যাট্রিবিউটের বদলের হিসাব ([`History`](#history)): কী যোগ হলো, কী আগের মতো, কী সরলো। অডিট লগে "কোন ফিল্ড কী থেকে কী হলো" লিখতে, বিশেষত `before_flush` ইভেন্টে। `inspect(obj).attrs.<নাম>.history`-এর ফাংশন রূপ।

**উদাহরণ:**

```python
u.name = "রহিম উদ্দিন"
h = get_history(u, "name")
print(h.deleted, "→", h.added)   # ['রহিম'] → ['রহিম উদ্দিন']
```

### `get_history()`-এর সব প্যারামিটার { #get-history-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `obj` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |
| `passive` | অ্যাট্রিবিউট লোড না থাকলে লোড করবে কি না ([`PassiveFlag`](orm-state.md#passiveflag)); ডিফল্ট `PASSIVE_OFF` (দরকারে লোড করে)। |

## `History` { #history }

```python
from sqlalchemy.orm.attributes import History
```

একটি অ্যাট্রিবিউটের বদলের তিনটি তালিকা (named tuple): `added` (নতুন মান/যোগ হওয়া সদস্য), `unchanged` (আগের মতো), `deleted` (পুরোনো মান/সরানো সদস্য)। সাধারণ কলামে প্রতিটিতে সর্বোচ্চ একটি মান; collection-এ অনেক।

**উদাহরণ:**

```python
h = get_history(u, "addresses")
print(len(h.unchanged), h.added, h.deleted)   # 2 () ()
u.addresses.append(Address(email="c@x.com"))
h = get_history(u, "addresses")
print(len(h.unchanged), [a.email for a in h.added])   # 2 ['c@x.com']
```

**Python `tuple`-এর সব মেথড** (`count()`, `index()`) সাধারণ `tuple`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #history-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`added`](#history-added) | অ্যাট্রিবিউট | নতুন মান বা যোগ হওয়া সদস্যগুলো। |
| [`as_state()`](#history-as-state) | মেথড (internal) | অবজেক্টের বদলে তাদের `InstanceState` দিয়ে একই History। |
| [`deleted`](#history-deleted) | অ্যাট্রিবিউট | পুরোনো মান বা সরানো সদস্যগুলো। |
| [`empty()`](#history-empty) | মেথড | কোনো মানই নেই (বদলও নেই, আগের মানও নেই) কি না। |
| [`from_collection()`](#history-from-collection) | ক্লাস মেথড (internal) | (ক্লাস মেথড) collection অ্যাট্রিবিউটের অবস্থা থেকে History বানায়। |
| [`from_object_attribute()`](#history-from-object-attribute) | ক্লাস মেথড (internal) | (ক্লাস মেথড) many-to-one অ্যাট্রিবিউটের অবস্থা থেকে। |
| [`from_scalar_attribute()`](#history-from-scalar-attribute) | ক্লাস মেথড (internal) | (ক্লাস মেথড) সাধারণ কলামের অবস্থা থেকে। |
| [`has_changes()`](#history-has-changes) | মেথড | কোনো বদল (`added` বা `deleted`) আছে কি না। |
| [`non_added()`](#history-non-added) | মেথড | `unchanged + deleted`: বদলের **আগের** অবস্থা। |
| [`non_deleted()`](#history-non-deleted) | মেথড | `added + unchanged`: বদলের **পরের** অবস্থা। |
| [`sum()`](#history-sum) | মেথড | `added + unchanged + deleted`: সব। |
| [`unchanged`](#history-unchanged) | অ্যাট্রিবিউট | বদলায়নি এমন মান/সদস্য। |

### `History.added` { #history-added }

**ধরন:** অ্যাট্রিবিউট

নতুন মান বা যোগ হওয়া সদস্যগুলো।

**উদাহরণ:**

```python
u.name = "নতুন"
print(get_history(u, "name").added)   # ['নতুন']
```

### `History.as_state()` { #history-as-state }

```python
History.as_state()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টের বদলে তাদের `InstanceState` দিয়ে একই History।

**উদাহরণ:**

```python
print(type(get_history(u, "addresses").as_state().unchanged[0]).__name__)   # InstanceState
```

### `History.deleted` { #history-deleted }

**ধরন:** অ্যাট্রিবিউট

পুরোনো মান বা সরানো সদস্যগুলো।

**উদাহরণ:**

```python
u.name = "নতুন"
print(get_history(u, "name").deleted)   # ['রহিম']
```

### `History.empty()` { #history-empty }

```python
History.empty()
```

**ধরন:** মেথড

কোনো মানই নেই (বদলও নেই, আগের মানও নেই) কি না।

**উদাহরণ:**

```python
print(get_history(u, "name").empty(), get_history(User(), "name").empty())   # False True
```

### `History.from_collection()` { #history-from-collection }

```python
History.from_collection(attribute, state, current)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) collection অ্যাট্রিবিউটের অবস্থা থেকে History বানায়।

**উদাহরণ:**

```python
print(callable(History.from_collection))   # True
```

### `History.from_object_attribute()` { #history-from-object-attribute }

```python
History.from_object_attribute(attribute, state, current, original=symbol('NO_HISTORY'))
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) many-to-one অ্যাট্রিবিউটের অবস্থা থেকে।

**উদাহরণ:**

```python
print(callable(History.from_object_attribute))   # True
```

### `History.from_scalar_attribute()` { #history-from-scalar-attribute }

```python
History.from_scalar_attribute(attribute, state, current)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) সাধারণ কলামের অবস্থা থেকে।

**উদাহরণ:**

```python
print(callable(History.from_scalar_attribute))   # True
```

### `History.has_changes()` { #history-has-changes }

```python
History.has_changes()
```

**ধরন:** মেথড

কোনো বদল (`added` বা `deleted`) আছে কি না।

**উদাহরণ:**

```python
print(get_history(u, "name").has_changes(), end=" "); u.name = "x"
print(get_history(u, "name").has_changes())   # False True
```

### `History.non_added()` { #history-non-added }

```python
History.non_added()
```

**ধরন:** মেথড

`unchanged + deleted`: বদলের **আগের** অবস্থা।

**উদাহরণ:**

```python
u.name = "নতুন"
print(get_history(u, "name").non_added())   # ['রহিম']
```

### `History.non_deleted()` { #history-non-deleted }

```python
History.non_deleted()
```

**ধরন:** মেথড

`added + unchanged`: বদলের **পরের** অবস্থা।

**উদাহরণ:**

```python
u.name = "নতুন"
print(get_history(u, "name").non_deleted())   # ['নতুন']
```

### `History.sum()` { #history-sum }

```python
History.sum()
```

**ধরন:** মেথড

`added + unchanged + deleted`: সব।

**উদাহরণ:**

```python
u.name = "নতুন"
print(get_history(u, "name").sum())   # ['নতুন', 'রহিম']
```

### `History.unchanged` { #history-unchanged }

**ধরন:** অ্যাট্রিবিউট

বদলায়নি এমন মান/সদস্য।

**উদাহরণ:**

```python
print(get_history(u, "name").unchanged)   # ['রহিম']
```

## অ্যাট্রিবিউটে মান বসানো ও পড়া { #set-committed-value-group }

## `set_committed_value()` { #set-committed-value }

```python
from sqlalchemy.orm.attributes import set_committed_value
```

```python
set_committed_value(instance, key, value)
```

**ধরন:** ফাংশন

অ্যাট্রিবিউটে এমনভাবে মান বসায় যেন **ডেটাবেস থেকেই লোড হয়েছে**: কোনো history নেই, ইভেন্ট নেই, flush-এ UPDATE হবে না। নিজের লোডিং কৌশলে (যেমন নিজে কুয়েরি করে একটি relationship ভরে দেওয়া, যাতে আবার lazy load না হয়) কাজে লাগে।

**উদাহরণ:**

```python
extra = session.scalars(select(Address).where(Address.user_id == 1)).all()
u2 = session.get(User, 1)
session.expire(u2, ["addresses"])
set_committed_value(u2, "addresses", extra[:1])      # নিজে ভরে দিলাম
print(len(u2.addresses), session.is_modified(u2))   # 1 False
```

### `set_committed_value()`-এর সব প্যারামিটার { #set-committed-value-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |
| `value` | মান (collection হলে তালিকা)। |

## `set_attribute()` { #set-attribute }

```python
from sqlalchemy.orm.attributes import set_attribute
```

```python
set_attribute(instance, key, value, initiator=None)
```

**ধরন:** ফাংশন

`setattr(obj, key, value)`-এর মতো (ইভেন্ট আর history সহ), কিন্তু নিজের `__setattr__`/property থাকলেও সরাসরি ORM-এর অ্যাট্রিবিউট ব্যবস্থায় যায়। নিজের instrumentation বা `__init__` লিখলে কাজে লাগে।

**উদাহরণ:**

```python
set_attribute(u, "name", "করিম")
print(u.name, get_history(u, "name").deleted)   # করিম ['রহিম']
```

### `set_attribute()`-এর সব প্যারামিটার { #set-attribute-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |
| `value` | নতুন মান। |
| `initiator` | ইভেন্টের উৎস ([`AttributeEventToken`](orm-state.md#attributeeventtoken)), সাধারণত দরকার নেই। |

## `get_attribute()` { #get-attribute }

```python
from sqlalchemy.orm.attributes import get_attribute
```

```python
get_attribute(instance, key)
```

**ধরন:** ফাংশন

`getattr(obj, key)`-এর মতো (দরকার হলে লোড করে), কিন্তু সরাসরি ORM-এর অ্যাট্রিবিউট ব্যবস্থা থেকে।

**উদাহরণ:**

```python
print(get_attribute(u, "name"), len(get_attribute(u, "addresses")))   # রহিম 2
```

### `get_attribute()`-এর সব প্যারামিটার { #get-attribute-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |

## `del_attribute()` { #del-attribute }

```python
from sqlalchemy.orm.attributes import del_attribute
```

```python
del_attribute(instance, key)
```

**ধরন:** ফাংশন

`delattr(obj, key)`-এর মতো (ইভেন্টসহ): অবজেক্ট থেকে মানটি মুছে দেয়, history-তে নতুন মান `None` হিসেবে আসে।

**সাবধান (২.১.৯-এ যাচাই করা):** ডেটাবেসে থাকা (persistent) অবজেক্টের একটি **কলাম** এভাবে মুছে flush করলে SQLAlchemy-র ভেতরে `KeyError` আসে। কলাম `NULL` করতে লিখুন `obj.col = None`; `del` দিয়ে নয়।

**উদাহরণ:**

```python
nu = User(name="x")
del_attribute(nu, "name")
print("name" in nu.__dict__, get_history(nu, "name").added)   # False [None]
```

### `del_attribute()`-এর সব প্যারামিটার { #del-attribute-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |

## `init_collection()` { #init-collection }

```python
from sqlalchemy.orm.attributes import init_collection
```

```python
init_collection(obj, key)
```

**ধরন:** ফাংশন

একটি collection অ্যাট্রিবিউটকে খালি collection দিয়ে শুরু করে তার [`CollectionAdapter`](collections.md#collectionadapter) দেয় (ডেটাবেস থেকে লোড না করে)। সাধারণত `set_committed_value()`-এর সাথে নিজের লোডারে।

**উদাহরণ:**

```python
nu = User(name="নতুন")
adapter = init_collection(nu, "addresses")
print(type(adapter).__name__, list(nu.addresses))   # CollectionAdapter []
```

### `init_collection()`-এর সব প্যারামিটার { #init-collection-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `obj` | অবজেক্ট। |
| `key` | collection অ্যাট্রিবিউটের নাম। |

## অবস্থা ও পরিচয় { #instance-state-group }

## `instance_state(obj)` { #instance-state }

```python
from sqlalchemy.orm.attributes import instance_state
```

**ধরন:** ফাংশন

অবজেক্টের [`InstanceState`](orm-state.md#instancestate) দ্রুততম উপায়ে দেয় (আসলে `operator.attrgetter("_sa_instance_state")`)। ম্যাপ না করা অবজেক্টে `AttributeError`; নিরাপদ রূপ `inspect(obj)` বা `object_state(obj)`।

**উদাহরণ:**

```python
print(instance_state(u) is inspect(u), instance_state(u).persistent)   # True True
```

## `object_state()` { #object-state }

```python
from sqlalchemy.orm.base import object_state
```

```python
object_state(instance)
```

**ধরন:** ফাংশন

অবজেক্টের `InstanceState`; ম্যাপ না করা অবজেক্টে স্পষ্ট এরর (`UnmappedInstanceError`)।

**উদাহরণ:**

```python
print(object_state(u).identity)   # (1,)
try:
    object_state(object())
except Exception as e:
    print(type(e).__name__)   # UnmappedInstanceError
```

### `object_state()`-এর সব প্যারামিটার { #object-state-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |

## `is_instrumented()` { #is-instrumented }

```python
from sqlalchemy.orm.instrumentation import is_instrumented
```

```python
is_instrumented(instance, key)
```

**ধরন:** ফাংশন

অবজেক্টের একটি অ্যাট্রিবিউট ORM-এর পর্যবেক্ষণে (instrumented) আছে কি না: ম্যাপ করা কলাম/relationship হলে `True`, সাধারণ Python অ্যাট্রিবিউট হলে `False`।

**উদাহরণ:**

```python
print(is_instrumented(u, "name"), is_instrumented(u, "__class__"))   # True False
```

### `is_instrumented()`-এর সব প্যারামিটার { #is-instrumented-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `instance` | অবজেক্ট। |
| `key` | অ্যাট্রিবিউটের নাম। |

## `identity_key()` { #identity-key }

```python
from sqlalchemy.orm.util import identity_key
```

```python
identity_key(class_=None, ident=None, *, instance=None, row=None, identity_token=None)
```

**ধরন:** ফাংশন

identity map-এর key বানায়: `(ক্লাস, primary key tuple, identity_token)`। তিনভাবে: ক্লাস + primary key (`identity_key(User, 1)`), একটি অবজেক্ট (`instance=u`), বা একটি ফলের রো (`row=...`)। `session.identity_map.get(key)` দিয়ে "এটা কি সেশনে আছে?" দেখতে।

**উদাহরণ:**

```python
k = identity_key(User, 1)
print(k[0].__name__, k[1], session.identity_map.get(k) is u, identity_key(instance=u) == k)   # User (1,) True True
```

### `identity_key()`-এর সব প্যারামিটার { #identity-key-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `class_` | মডেল ক্লাস। |
| `ident` | primary key-এর মান (একটি, বা composite হলে tuple)। |
| `instance` | অবজেক্ট (তার key বের করতে)। |
| `row` | ফলের রো (primary key কলামসহ)। |
| `identity_token` | sharding-এর identity token। |

## aliased() যা বানায় { #aliasedclass-group }

## `AliasedClass` { #aliasedclass }

```python
from sqlalchemy.orm.util import AliasedClass
```

[`aliased(User)`](loading.md#aliased)-এর ফল: মডেলের একটি "দ্বিতীয় রূপ", যার অ্যাট্রিবিউট (`ua.name`) আলাদা alias-এর কলাম দেখায়। একই টেবিল একটি কুয়েরিতে দুবার লাগলে (self-join, তুলনা)। ফলে আসে আসল `User` অবজেক্টই। এর নিজের সদস্য খুব কম; মডেলের সব অ্যাট্রিবিউট এতে proxy হিসেবে পাওয়া যায়, আর তথ্য পেতে `inspect(ua)` → [`AliasedInsp`](#aliasedinsp)।

**উদাহরণ:**

```python
ua = aliased(User, name="u2")
print(type(ua).__name__, ua.name.expression)   # AliasedClass u2.name
stmt = select(User.name, ua.name).join(ua, ua.id == User.id)
print(session.execute(stmt).all())   # [('রহিম', 'রহিম')]
```

### কনস্ট্রাক্টরের প্যারামিটার { #aliasedclass-params }

```python
AliasedClass(mapped_class_or_ac, alias=None, name=None, flat=False, adapt_on_names=False, with_polymorphic_mappers=None, with_polymorphic_discriminator=None, base_alias=None, use_mapper_path=False, represents_outer_join=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `mapped_class_or_ac` | মডেল ক্লাস (বা আরেকটি aliased)। |
| `alias` | নির্দিষ্ট `Alias`/সাবকুয়েরি। |
| `name` | SQL-এ alias-এর নাম। |
| `flat` | join-ভিত্তিক মডেলে বাইরের alias ছাড়া। |
| `adapt_on_names` | সাবকুয়েরির কলাম নাম ধরে মেলাবে কি না। |
| `with_polymorphic_mappers` | (অভ্যন্তরীণ) polymorphic mapper-গুলো। |
| `with_polymorphic_discriminator` | (অভ্যন্তরীণ)। |
| `base_alias` | (অভ্যন্তরীণ)। |
| `use_mapper_path` | (অভ্যন্তরীণ)। |
| `represents_outer_join` | (অভ্যন্তরীণ)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aliasedclass-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`allows_lambda`](#aliasedclass-allows-lambda) | অ্যাট্রিবিউট (internal) | lambda স্টেটমেন্টে ব্যবহার করা যায় কি না। |
| [`uses_inspection`](#aliasedclass-uses-inspection) | অ্যাট্রিবিউট (internal) | `inspect()` দিয়ে পরীক্ষা করা যায় কি না। |

### `AliasedClass.allows_lambda` { #aliasedclass-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

lambda স্টেটমেন্টে ব্যবহার করা যায় কি না।

**উদাহরণ:**

```python
print(AliasedClass.allows_lambda)   # True
```

### `AliasedClass.uses_inspection` { #aliasedclass-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`inspect()` দিয়ে পরীক্ষা করা যায় কি না।

**উদাহরণ:**

```python
print(AliasedClass.uses_inspection)   # True
```

## `AliasedInsp` { #aliasedinsp }

```python
from sqlalchemy.orm.util import AliasedInsp
```

`inspect(aliased(User))`-এর ফল: alias-টির তথ্য: কোন মডেল, কোন mapper, কোন selectable (alias টেবিল), নাম কী।

**উদাহরণ:**

```python
ai = inspect(aliased(User, name="u2"))
print(type(ai).__name__, ai.class_.__name__, ai.name, ai.is_aliased_class)   # AliasedInsp User u2 True
```

### কনস্ট্রাক্টরের প্যারামিটার { #aliasedinsp-params }

```python
AliasedInsp(entity, inspected, selectable, name, with_polymorphic_mappers, polymorphic_on, adapt_on_names, represents_outer_join, nest_adapters)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entity` | `AliasedClass` অবজেক্ট। |
| `inspected` | মূল মডেলের Mapper (বা আরেকটি AliasedInsp)। |
| `selectable` | alias টেবিল/সাবকুয়েরি। |
| `name` | নাম। |
| `with_polymorphic_mappers` | (অভ্যন্তরীণ)। |
| `polymorphic_on` | (অভ্যন্তরীণ)। |
| `adapt_on_names` | সাবকুয়েরির কলাম নাম ধরে মেলাবে কি না। |
| `represents_outer_join` | outer join-এর ফল কি না। |
| `nest_adapters` | (অভ্যন্তরীণ)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aliasedinsp-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`class_`](#aliasedinsp-class-) | প্রপার্টি | মূল মডেল ক্লাস। |
| [`entity`](#aliasedinsp-entity) | প্রপার্টি | `AliasedClass` অবজেক্টটি নিজে। |
| [`local_table`](#aliasedinsp-local-table) | অ্যাট্রিবিউট (internal) | মূল মডেলের টেবিল (alias নয়)। |
| [`mapper`](#aliasedinsp-mapper) | অ্যাট্রিবিউট | মূল মডেলের Mapper। |
| [`name`](#aliasedinsp-name) | অ্যাট্রিবিউট | alias-এর নাম (না দিলে স্বয়ংক্রিয়)। |
| [`persist_selectable`](#aliasedinsp-persist-selectable) | অ্যাট্রিবিউট (internal) | লেখার জন্য টেবিল (aliased-এ alias-টি)। |
| [`polymorphic_on`](#aliasedinsp-polymorphic-on) | অ্যাট্রিবিউট (internal) | inheritance-এর discriminator কলাম (না থাকলে `None`)। |
| [`represents_outer_join`](#aliasedinsp-represents-outer-join) | অ্যাট্রিবিউট (internal) | outer join থেকে এসেছে কি না (`with_polymorphic(..., aliased=True, flat=True)` ইত্যাদি)। |
| [`selectable`](#aliasedinsp-selectable) | অ্যাট্রিবিউট | SQL-এ যে alias বসে (`users AS u2`): একটি `Alias`, যার `element` মূল টেবিল। |
| [`with_polymorphic_mappers`](#aliasedinsp-with-polymorphic-mappers) | অ্যাট্রিবিউট (internal) | `with_polymorphic()` হলে অন্তর্ভুক্ত subclass-এর mapper-গুলো। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৪টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AliasedInsp`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Mapper` থেকে:** [`allows_lambda`](registry.md#mapper-allows-lambda) · [`entity_namespace`](registry.md#mapper-entity-namespace) · [`inherit_cache`](registry.md#mapper-inherit-cache) · [`path_string()`](registry.md#mapper-path-string) · [`uses_inspection`](registry.md#mapper-uses-inspection)

**`InspectionAttr` থেকে:** [`extension_type`](orm-properties.md#inspectionattr-extension-type) · [`is_aliased_class`](orm-properties.md#inspectionattr-is-aliased-class) · [`is_attribute`](orm-properties.md#inspectionattr-is-attribute) · [`is_bundle`](orm-properties.md#inspectionattr-is-bundle) · [`is_clause_element`](orm-properties.md#inspectionattr-is-clause-element) · [`is_instance`](orm-properties.md#inspectionattr-is-instance) · [`is_mapper`](orm-properties.md#inspectionattr-is-mapper) · [`is_property`](orm-properties.md#inspectionattr-is-property) · [`is_selectable`](orm-properties.md#inspectionattr-is-selectable)

///

### `AliasedInsp.class_` { #aliasedinsp-class- }

**ধরন:** প্রপার্টি

মূল মডেল ক্লাস।

**উদাহরণ:**

```python
print(inspect(aliased(User)).class_ is User)   # True
```

### `AliasedInsp.entity` { #aliasedinsp-entity }

**ধরন:** প্রপার্টি

`AliasedClass` অবজেক্টটি নিজে।

**উদাহরণ:**

```python
ua = aliased(User)
print(inspect(ua).entity is ua)   # True
```

### `AliasedInsp.local_table` { #aliasedinsp-local-table }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল মডেলের টেবিল (alias নয়)।

**উদাহরণ:**

```python
print(inspect(aliased(User)).local_table.name)   # users
```

### `AliasedInsp.mapper` { #aliasedinsp-mapper }

**ধরন:** অ্যাট্রিবিউট

মূল মডেলের Mapper।

**উদাহরণ:**

```python
print(inspect(aliased(User)).mapper)   # Mapper[User(users)]
```

### `AliasedInsp.name` { #aliasedinsp-name }

**ধরন:** অ্যাট্রিবিউট

alias-এর নাম (না দিলে স্বয়ংক্রিয়)।

**উদাহরণ:**

```python
print(inspect(aliased(User, name="boss")).name)   # boss
```

### `AliasedInsp.persist_selectable` { #aliasedinsp-persist-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লেখার জন্য টেবিল (aliased-এ alias-টি)।

**উদাহরণ:**

```python
print(type(inspect(aliased(User)).persist_selectable).__name__)   # Alias
```

### `AliasedInsp.polymorphic_on` { #aliasedinsp-polymorphic-on }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inheritance-এর discriminator কলাম (না থাকলে `None`)।

**উদাহরণ:**

```python
print(inspect(aliased(User)).polymorphic_on)   # None
```

### `AliasedInsp.represents_outer_join` { #aliasedinsp-represents-outer-join }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

outer join থেকে এসেছে কি না (`with_polymorphic(..., aliased=True, flat=True)` ইত্যাদি)।

**উদাহরণ:**

```python
print(inspect(aliased(User)).represents_outer_join)   # False
```

### `AliasedInsp.selectable` { #aliasedinsp-selectable }

**ধরন:** অ্যাট্রিবিউট

SQL-এ যে alias বসে (`users AS u2`): একটি `Alias`, যার `element` মূল টেবিল।

**উদাহরণ:**

```python
sel = inspect(aliased(User, name="u2")).selectable
print(sel.name, sel.element.name)   # u2 users
```

### `AliasedInsp.with_polymorphic_mappers` { #aliasedinsp-with-polymorphic-mappers }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`with_polymorphic()` হলে অন্তর্ভুক্ত subclass-এর mapper-গুলো।

**উদাহরণ:**

```python
print([str(x) for x in inspect(aliased(User)).with_polymorphic_mappers])   # ['Mapper[User(users)]']
```
