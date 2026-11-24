# ORM স্টেট ও ইনস্পেকশন: InstanceState, AttributeState, ORMExecuteState … { #api-orm-state }

/// note | এই পেজে যা আছে

ORM ভেতরে ভেতরে প্রতিটি অবজেক্ট আর ক্লাসের হিসাব রাখে। এই পেজ সেই হিসাবের অবজেক্টগুলো:

* **অবজেক্টের অবস্থা:** `inspect(user)` যা দেয় সেই `InstanceState` (transient / pending / persistent / detached / deleted, কী বদলেছে, কী লোড হয়নি), প্রতিটি অ্যাট্রিবিউটের `AttributeState`, সেশনের `IdentityMap`।
* **ক্লাসের দিক:** `ClassManager`, `InstrumentedAttribute` (`User.name` আসলে যা)।
* **ইভেন্ট হুকে যা আসে:** `ORMExecuteState` (`do_orm_execute`), `UserDefinedOption`, `AttributeEventToken`, `QueryContext`, `UOWTransaction`।
* **ধ্রুবক:** `PassiveFlag`, `LoaderCallableStatus`, `SessionTransactionOrigin`, আর `with_loader_criteria()`-এর `LoaderCriteriaOption`।

///

সাধারণ অ্যাপে এদের বেশিরভাগ সরাসরি লাগে না। কাজে লাগে **ডিবাগ** করতে ("এই অবজেক্টটি কি সেশনে আছে? কোন ফিল্ড বদলেছে?"), **অডিট লগ** বানাতে (কে কোন ফিল্ড কী থেকে কী করল), আর ইভেন্ট হুক লিখতে। সাধারণ ব্যবহারকারী-মুখী অংশগুলো (`InstanceState`, `AttributeState`, `ORMExecuteState`) আগে, একেবারে ভেতরের (internal) অংশ পরে।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

[Session API পেজের](session.md) মতো `User` (`id`, `name`, `addresses`) আর `Address` (`id`, `email`, `user_id`, `user`), ডেটা: রহিম (দুটি ঠিকানা), করিম। `insp = inspect(obj)` দিয়ে `InstanceState` পাওয়া যায়। PostgreSQL 16-এ চালিয়ে দেখা।

///

## অবজেক্টের অবস্থা { #instancestate-group }

## `InstanceState` { #instancestate }

```python
from sqlalchemy.orm import InstanceState
```

প্রতিটি ORM অবজেক্টের সাথে লুকিয়ে থাকা "হিসাবের খাতা"। পেতে: `inspect(user)`। এতে আছে অবজেক্টটি কোন অবস্থায় (নিচের পাঁচটির একটি), কোন সেশনে, primary key কী, কোন অ্যাট্রিবিউট বদলেছে, কোনটি এখনো লোড হয়নি।

| অবস্থা | মানে |
| :--- | :--- |
| `transient` | নতুন বানানো, সেশনে নেই, ডেটাবেসেও নেই |
| `pending` | `session.add()` হয়েছে, কিন্তু এখনো flush হয়নি |
| `persistent` | সেশনে আছে আর ডেটাবেসে একটি রো-র সাথে যুক্ত |
| `deleted` | `session.delete()` হয়ে flush হয়েছে, commit বাকি |
| `detached` | ডেটাবেসে আছে, কিন্তু কোনো সেশনে নেই (সেশন বন্ধ হয়েছে) |

**উদাহরণ:**

```python
u = User(name="নতুন")
insp = inspect(u)
print(type(insp).__name__, insp.transient)   # InstanceState True
session.add(u); print(insp.pending)   # True
session.flush(); print(insp.persistent, insp.identity)   # True (3,)
session.close(); print(insp.detached)   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #instancestate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`async_session`](#instancestate-async-session) | প্রপার্টি | অবজেক্টটি কোনো `AsyncSession`-এ থাকলে সেটি, নইলে `None`। |
| [`attrs`](#instancestate-attrs) | প্রপার্টি | প্রতিটি mapped অ্যাট্রিবিউটের [`AttributeState`](#attributestate), নাম ধরে: `insp.attrs.name.value`, `insp.attrs.name.history`। |
| [`callables`](#instancestate-callables) | অ্যাট্রিবিউট (internal) | অ্যাট্রিবিউট-প্রতি "পরে লোড করো" ফাংশনগুলো (deferred/expired কলামের জন্য)। |
| [`class_`](#instancestate-class-) | অ্যাট্রিবিউট | অবজেক্টের ক্লাস। |
| [`committed_state`](#instancestate-committed-state) | অ্যাট্রিবিউট (internal) | বদলানো অ্যাট্রিবিউটগুলোর **আগের** (ডেটাবেসে থাকা) মান, flush না হওয়া পর্যন্ত। |
| [`deleted`](#instancestate-deleted) | প্রপার্টি | অবজেক্টটি "deleted" অবস্থায় কি না: `session.delete()` হয়ে flush হয়েছে, কিন্তু commit বাকি। |
| [`detached`](#instancestate-detached) | প্রপার্টি | অবজেক্টটি detached কি না: ডেটাবেসে আছে কিন্তু কোনো সেশনে নেই। |
| [`dict`](#instancestate-dict) | প্রপার্টি | অবজেক্টের `__dict__` (যেখানে লোড হওয়া মানগুলো থাকে)। |
| [`expired`](#instancestate-expired) | অ্যাট্রিবিউট | পুরো অবজেক্টটি expire হয়েছে কি না (যেমন `commit()`-এর পর বা `session.expire(obj)`)। |
| [`expired_attributes`](#instancestate-expired-attributes) | অ্যাট্রিবিউট | যে অ্যাট্রিবিউটগুলো expire হয়ে আছে (নাম-এর set)। |
| [`get_history()`](#instancestate-get-history) | মেথড (internal) | একটি অ্যাট্রিবিউটের `History` (added, unchanged, deleted), `PassiveFlag` অনুযায়ী লোড করে বা না করে। |
| [`get_impl()`](#instancestate-get-impl) | মেথড (internal) | একটি অ্যাট্রিবিউটের ভেতরের implementation অবজেক্ট। |
| [`has_identity`](#instancestate-has-identity) | প্রপার্টি | primary key-এর পরিচয় (identity key) আছে কি না: persistent, detached বা deleted হলে `True`। |
| [`identity`](#instancestate-identity) | প্রপার্টি | primary key-এর মান tuple হিসেবে (`(1,)`), না থাকলে `None`। |
| [`identity_key`](#instancestate-identity-key) | প্রপার্টি | identity map-এ ব্যবহৃত পূর্ণ key: `(ক্লাস, primary key tuple, identity_token)`। |
| [`identity_token`](#instancestate-identity-token) | অ্যাট্রিবিউট | sharding ইত্যাদিতে একই primary key কয়েক জায়গায় থাকলে আলাদা করার টোকেন; সাধারণত `None`। |
| [`insert_order`](#instancestate-insert-order) | অ্যাট্রিবিউট (internal) | pending অবজেক্টগুলো কোন ক্রমে `add()` হয়েছিল (flush-এ INSERT-এর ক্রম ঠিক রাখতে)। |
| [`key`](#instancestate-key) | অ্যাট্রিবিউট | `identity_key`-এর মতো (persistent অবজেক্টের), নতুন অবজেক্টে `None`। |
| [`load_options`](#instancestate-load-options) | অ্যাট্রিবিউট (internal) | অবজেক্টটি লোড হওয়ার সময় যে লোডার অপশন ছিল (lazy load-এ আবার প্রয়োগের জন্য)। |
| [`load_path`](#instancestate-load-path) | অ্যাট্রিবিউট (internal) | কোন লোড-পথে অবজেক্টটি এসেছে (যেমন `User → addresses`)। |
| [`manager`](#instancestate-manager) | অ্যাট্রিবিউট (internal) | ক্লাসের [`ClassManager`](#classmanager)। |
| [`mapper`](#instancestate-mapper) | প্রপার্টি | অবজেক্টের ক্লাসের `Mapper`। |
| [`modified`](#instancestate-modified) | অ্যাট্রিবিউট | কোনো অ্যাট্রিবিউট বদলানো হয়েছে কি না (flush বাকি)। |
| [`obj`](#instancestate-obj) | অ্যাট্রিবিউট (internal) | অবজেক্টের weak reference; ডাকলে (`insp.obj()`) অবজেক্টটি (garbage collect হলে `None`)। |
| [`object`](#instancestate-object) | প্রপার্টি | মূল অবজেক্টটি (`obj()`-এর সহজ রূপ)। |
| [`parents`](#instancestate-parents) | প্রপার্টি (internal) | কোন অবজেক্ট(গুলো)র collection-এ এটি আছে, তার ভেতরের হিসাব (backref/orphan পরীক্ষার জন্য)। |
| [`pending`](#instancestate-pending) | প্রপার্টি | `session.add()` হয়েছে কিন্তু এখনো flush হয়নি কি না। |
| [`persistent`](#instancestate-persistent) | প্রপার্টি | সেশনে আছে আর ডেটাবেসের একটি রো-র সাথে যুক্ত কি না। |
| [`runid`](#instancestate-runid) | অ্যাট্রিবিউট (internal) | কোন লোড অপারেশনে অবজেক্টটি শেষবার ভরা হয়েছে তার নম্বর (একই লোডে দুবার ভরা এড়াতে)। |
| [`session`](#instancestate-session) | প্রপার্টি | অবজেক্টটি যে `Session`-এ আছে, নইলে `None`। |
| [`session_id`](#instancestate-session-id) | অ্যাট্রিবিউট (internal) | সেশনের ভেতরের নম্বর (`Session.hash_key`), নেই হলে `None`। |
| [`transient`](#instancestate-transient) | প্রপার্টি | একেবারে নতুন, সেশন আর ডেটাবেস দুটোর বাইরে কি না। |
| [`unloaded`](#instancestate-unloaded) | প্রপার্টি | যে অ্যাট্রিবিউটগুলো এখনো লোড হয়নি (lazy relationship, deferred বা expired কলাম)। |
| [`unloaded_expirable`](#instancestate-unloaded-expirable) | প্রপার্টি | `unloaded`-এর আরেক নাম। |
| [`unmodified`](#instancestate-unmodified) | প্রপার্টি | যে অ্যাট্রিবিউটগুলোতে কোনো অসংরক্ষিত বদল নেই। |
| [`unmodified_intersection()`](#instancestate-unmodified-intersection) | মেথড (internal) | দেওয়া নামগুলোর মধ্যে কোনগুলো অপরিবর্তিত (`unmodified & keys`, দ্রুত রূপে)। |
| [`was_deleted`](#instancestate-was-deleted) | প্রপার্টি | অবজেক্টটি কখনো deleted অবস্থায় ছিল (আর রোলব্যাক হয়ে ফেরেনি) কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১০টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `InstanceState`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`InspectionAttr` থেকে:** [`extension_type`](orm-properties.md#inspectionattr-extension-type) · [`is_aliased_class`](orm-properties.md#inspectionattr-is-aliased-class) · [`is_attribute`](orm-properties.md#inspectionattr-is-attribute) · [`is_bundle`](orm-properties.md#inspectionattr-is-bundle) · [`is_clause_element`](orm-properties.md#inspectionattr-is-clause-element) · [`is_instance`](orm-properties.md#inspectionattr-is-instance) · [`is_mapper`](orm-properties.md#inspectionattr-is-mapper) · [`is_property`](orm-properties.md#inspectionattr-is-property) · [`is_selectable`](orm-properties.md#inspectionattr-is-selectable)

**`InspectionAttrInfo` থেকে:** [`info`](orm-properties.md#inspectionattrinfo-info)

///

### `InstanceState.async_session` { #instancestate-async-session }

**ধরন:** প্রপার্টি

অবজেক্টটি কোনো `AsyncSession`-এ থাকলে সেটি, নইলে `None`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).async_session)   # None
```

### `InstanceState.attrs` { #instancestate-attrs }

**ধরন:** প্রপার্টি

প্রতিটি mapped অ্যাট্রিবিউটের [`AttributeState`](#attributestate), নাম ধরে: `insp.attrs.name.value`, `insp.attrs.name.history`। অডিট লগের মূল উৎস।

**উদাহরণ:**

```python
u = session.get(User, 1)
insp = inspect(u)
print(list(insp.attrs.keys()), insp.attrs.name.value)   # ['addresses', 'id', 'name'] রহিম
```

### `InstanceState.callables` { #instancestate-callables }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউট-প্রতি "পরে লোড করো" ফাংশনগুলো (deferred/expired কলামের জন্য)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).callables)   # {}
```

### `InstanceState.class_` { #instancestate-class- }

**ধরন:** অ্যাট্রিবিউট

অবজেক্টের ক্লাস।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).class_.__name__)   # User
```

### `InstanceState.committed_state` { #instancestate-committed-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

বদলানো অ্যাট্রিবিউটগুলোর **আগের** (ডেটাবেসে থাকা) মান, flush না হওয়া পর্যন্ত।

**উদাহরণ:**

```python
u = session.get(User, 1); u.name = "রহিম উদ্দিন"
print(inspect(u).committed_state)   # {'name': 'রহিম'}
```

### `InstanceState.deleted` { #instancestate-deleted }

**ধরন:** প্রপার্টি

অবজেক্টটি "deleted" অবস্থায় কি না: `session.delete()` হয়ে flush হয়েছে, কিন্তু commit বাকি।

**উদাহরণ:**

```python
u = session.get(User, 2); session.delete(u); session.flush()
print(inspect(u).deleted, inspect(u).persistent)   # True False
```

### `InstanceState.detached` { #instancestate-detached }

**ধরন:** প্রপার্টি

অবজেক্টটি detached কি না: ডেটাবেসে আছে কিন্তু কোনো সেশনে নেই। এই অবস্থায় লোড না হওয়া অ্যাট্রিবিউট পড়লে `DetachedInstanceError`।

**উদাহরণ:**

```python
u = session.get(User, 1); session.expunge(u)
print(inspect(u).detached)   # True
```

### `InstanceState.dict` { #instancestate-dict }

**ধরন:** প্রপার্টি

অবজেক্টের `__dict__` (যেখানে লোড হওয়া মানগুলো থাকে)। কোনটি লোড হয়েছে বোঝার সহজ উপায়।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(sorted(k for k in inspect(u).dict if not k.startswith("_")))   # ['id', 'name']
```

### `InstanceState.expired` { #instancestate-expired }

**ধরন:** অ্যাট্রিবিউট

পুরো অবজেক্টটি expire হয়েছে কি না (যেমন `commit()`-এর পর বা `session.expire(obj)`)। পরের বার কোনো অ্যাট্রিবিউট পড়লে ডেটাবেস থেকে আবার আনবে।

**উদাহরণ:**

```python
u = session.get(User, 1); session.expire(u)
print(inspect(u).expired)   # True
```

### `InstanceState.expired_attributes` { #instancestate-expired-attributes }

**ধরন:** অ্যাট্রিবিউট

যে অ্যাট্রিবিউটগুলো expire হয়ে আছে (নাম-এর set)।

**উদাহরণ:**

```python
u = session.get(User, 1); session.expire(u, ["name"])
print(inspect(u).expired_attributes)   # {'name'}
```

### `InstanceState.get_history()` { #instancestate-get-history }

```python
InstanceState.get_history(key, passive)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অ্যাট্রিবিউটের `History` (added, unchanged, deleted), `PassiveFlag` অনুযায়ী লোড করে বা না করে। সাধারণত `insp.attrs.x.history` ব্যবহার করুন।

**উদাহরণ:**

```python
u = session.get(User, 1); u.name = "নতুন"
print(inspect(u).get_history("name", PassiveFlag.PASSIVE_OFF))   # History(added=['নতুন'], unchanged=(), deleted=['রহিম'])
```

### `InstanceState.get_impl()` { #instancestate-get-impl }

```python
InstanceState.get_impl(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অ্যাট্রিবিউটের ভেতরের implementation অবজেক্ট।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(type(inspect(u).get_impl("name")).__name__)   # _ScalarAttributeImpl
```

### `InstanceState.has_identity` { #instancestate-has-identity }

**ধরন:** প্রপার্টি

primary key-এর পরিচয় (identity key) আছে কি না: persistent, detached বা deleted হলে `True`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(User(name="x")).has_identity, inspect(u).has_identity)   # False True
```

### `InstanceState.identity` { #instancestate-identity }

**ধরন:** প্রপার্টি

primary key-এর মান tuple হিসেবে (`(1,)`), না থাকলে `None`। এটা সরাসরি `session.get()`-এ দেওয়া যায়।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).identity, inspect(User(name="x")).identity)   # (1,) None
```

### `InstanceState.identity_key` { #instancestate-identity-key }

**ধরন:** প্রপার্টি

identity map-এ ব্যবহৃত পূর্ণ key: `(ক্লাস, primary key tuple, identity_token)`।

**উদাহরণ:**

```python
u = session.get(User, 1)
k = inspect(u).identity_key
print(k[0].__name__, k[1], k[2])   # User (1,) None
```

### `InstanceState.identity_token` { #instancestate-identity-token }

**ধরন:** অ্যাট্রিবিউট

sharding ইত্যাদিতে একই primary key কয়েক জায়গায় থাকলে আলাদা করার টোকেন; সাধারণত `None`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).identity_token)   # None
```

### `InstanceState.insert_order` { #instancestate-insert-order }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

pending অবজেক্টগুলো কোন ক্রমে `add()` হয়েছিল (flush-এ INSERT-এর ক্রম ঠিক রাখতে)।

**উদাহরণ:**

```python
a, b = User(name="a"), User(name="b"); session.add_all([a, b])
print(inspect(a).insert_order < inspect(b).insert_order)   # True
```

### `InstanceState.key` { #instancestate-key }

**ধরন:** অ্যাট্রিবিউট

`identity_key`-এর মতো (persistent অবজেক্টের), নতুন অবজেক্টে `None`।

**উদাহরণ:**

```python
print(inspect(User(name="x")).key)   # None
```

### `InstanceState.load_options` { #instancestate-load-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টটি লোড হওয়ার সময় যে লোডার অপশন ছিল (lazy load-এ আবার প্রয়োগের জন্য)।

**উদাহরণ:**

```python
u = session.scalars(select(User).options(selectinload(User.addresses)).where(User.id == 1)).one()
print(type(inspect(u).load_options).__name__)   # tuple
```

### `InstanceState.load_path` { #instancestate-load-path }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন লোড-পথে অবজেক্টটি এসেছে (যেমন `User → addresses`)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).load_path)   # ORM Path[Mapper[User(users)]]
```

### `InstanceState.manager` { #instancestate-manager }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসের [`ClassManager`](#classmanager)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(type(inspect(u).manager).__name__)   # ClassManager
```

### `InstanceState.mapper` { #instancestate-mapper }

**ধরন:** প্রপার্টি

অবজেক্টের ক্লাসের `Mapper`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).mapper)   # Mapper[User(users)]
```

### `InstanceState.modified` { #instancestate-modified }

**ধরন:** অ্যাট্রিবিউট

কোনো অ্যাট্রিবিউট বদলানো হয়েছে কি না (flush বাকি)। মান আগের সমান হলেও "বদলানো" হিসেবে চিহ্নিত হতে পারে; নিশ্চিত হতে `session.is_modified(obj)`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).modified, end=" "); u.name = "নতুন"; print(inspect(u).modified)   # False True
```

### `InstanceState.obj` { #instancestate-obj }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টের weak reference; ডাকলে (`insp.obj()`) অবজেক্টটি (garbage collect হলে `None`)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).obj() is u)   # True
```

### `InstanceState.object` { #instancestate-object }

**ধরন:** প্রপার্টি

মূল অবজেক্টটি (`obj()`-এর সহজ রূপ)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).object is u)   # True
```

### `InstanceState.parents` { #instancestate-parents }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন অবজেক্ট(গুলো)র collection-এ এটি আছে, তার ভেতরের হিসাব (backref/orphan পরীক্ষার জন্য)।

**উদাহরণ:**

```python
a = session.get(Address, 1); a.user
print(type(inspect(a).parents).__name__)   # dict
```

### `InstanceState.pending` { #instancestate-pending }

**ধরন:** প্রপার্টি

`session.add()` হয়েছে কিন্তু এখনো flush হয়নি কি না।

**উদাহরণ:**

```python
u = User(name="x"); session.add(u)
print(inspect(u).pending)   # True
```

### `InstanceState.persistent` { #instancestate-persistent }

**ধরন:** প্রপার্টি

সেশনে আছে আর ডেটাবেসের একটি রো-র সাথে যুক্ত কি না।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).persistent)   # True
```

### `InstanceState.runid` { #instancestate-runid }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কোন লোড অপারেশনে অবজেক্টটি শেষবার ভরা হয়েছে তার নম্বর (একই লোডে দুবার ভরা এড়াতে)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(isinstance(inspect(u).runid, int))   # True
```

### `InstanceState.session` { #instancestate-session }

**ধরন:** প্রপার্টি

অবজেক্টটি যে `Session`-এ আছে, নইলে `None`। (`object_session(obj)`-এর মতো।)

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).session is session, inspect(User(name="x")).session)   # True None
```

### `InstanceState.session_id` { #instancestate-session-id }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সেশনের ভেতরের নম্বর (`Session.hash_key`), নেই হলে `None`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).session_id == session.hash_key)   # True
```

### `InstanceState.transient` { #instancestate-transient }

**ধরন:** প্রপার্টি

একেবারে নতুন, সেশন আর ডেটাবেস দুটোর বাইরে কি না।

**উদাহরণ:**

```python
print(inspect(User(name="x")).transient)   # True
```

### `InstanceState.unloaded` { #instancestate-unloaded }

**ধরন:** প্রপার্টি

যে অ্যাট্রিবিউটগুলো এখনো লোড হয়নি (lazy relationship, deferred বা expired কলাম)। এগুলো পড়লে SQL চলবে।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).unloaded)   # {'addresses'}
```

### `InstanceState.unloaded_expirable` { #instancestate-unloaded-expirable }

**ধরন:** প্রপার্টি

`unloaded`-এর আরেক নাম।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).unloaded_expirable)   # {'addresses'}
```

### `InstanceState.unmodified` { #instancestate-unmodified }

**ধরন:** প্রপার্টি

যে অ্যাট্রিবিউটগুলোতে কোনো অসংরক্ষিত বদল নেই।

**উদাহরণ:**

```python
u = session.get(User, 1); u.name = "নতুন"
print(sorted(inspect(u).unmodified))   # ['addresses', 'id']
```

### `InstanceState.unmodified_intersection()` { #instancestate-unmodified-intersection }

```python
InstanceState.unmodified_intersection(keys)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

দেওয়া নামগুলোর মধ্যে কোনগুলো অপরিবর্তিত (`unmodified & keys`, দ্রুত রূপে)।

**উদাহরণ:**

```python
u = session.get(User, 1); u.name = "নতুন"
print(inspect(u).unmodified_intersection(["id", "name"]))   # {'id'}
```

### `InstanceState.was_deleted` { #instancestate-was-deleted }

**ধরন:** প্রপার্টি

অবজেক্টটি কখনো deleted অবস্থায় ছিল (আর রোলব্যাক হয়ে ফেরেনি) কি না। commit-এর পর detached হলেও `True` থাকে। (`was_deleted(obj)` ফাংশনের মতো।)

**উদাহরণ:**

```python
u = session.get(User, 2); session.delete(u); session.commit()
print(inspect(u).detached, inspect(u).was_deleted)   # True True
```

## `AttributeState` { #attributestate }

```python
from sqlalchemy.orm.state import AttributeState
```

একটি অবজেক্টের **একটি** অ্যাট্রিবিউটের অবস্থা: বর্তমান মান, ডেটাবেস থেকে লোড হওয়া মান, আর কী বদলেছে (history)। পেতে `inspect(user).attrs.name`। কোন ফিল্ড কী থেকে কী হলো, তা লগ করতে সবচেয়ে কাজের।

**উদাহরণ:**

```python
u = session.get(User, 1)
u.name = "রহিম উদ্দিন"
a = inspect(u).attrs.name
print(a.value, "|", a.loaded_value, "|", a.history.deleted, "→", a.history.added)
# রহিম উদ্দিন | রহিম | ['রহিম'] → ['রহিম উদ্দিন']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #attributestate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`history`](#attributestate-history) | প্রপার্টি | flush-এর আগের বদলের হিসাব (`History`: `added`, `unchanged`, `deleted`)। |
| [`key`](#attributestate-key) | অ্যাট্রিবিউট | অ্যাট্রিবিউটের নাম। |
| [`load_history()`](#attributestate-load-history) | মেথড | `history`-এর মতো, কিন্তু অ্যাট্রিবিউট লোড না থাকলে **আগে লোড করে** (দরকার হলে SQL চালায়)। |
| [`loaded_value`](#attributestate-loaded-value) | প্রপার্টি | ডেটাবেস থেকে শেষবার লোড হওয়া মান; লোড না থাকলে `NO_VALUE`। |
| [`state`](#attributestate-state) | অ্যাট্রিবিউট | মূল অবজেক্টের `InstanceState`। |
| [`value`](#attributestate-value) | প্রপার্টি | বর্তমান মান (`getattr(obj, key)`-এর মতো; লোড না থাকলে লোড করে)। |

### `AttributeState.history` { #attributestate-history }

**ধরন:** প্রপার্টি

flush-এর আগের বদলের হিসাব (`History`: `added`, `unchanged`, `deleted`)। **লোড করে না**: অ্যাট্রিবিউট লোড না থাকলে খালি history দেয়। `history.has_changes()` দিয়ে বদল হয়েছে কি না।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.name.history.has_changes(), end=" "); u.name = "x"
print(inspect(u).attrs.name.history.has_changes())   # False True
```

### `AttributeState.key` { #attributestate-key }

**ধরন:** অ্যাট্রিবিউট

অ্যাট্রিবিউটের নাম।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.name.key)   # name
```

### `AttributeState.load_history()` { #attributestate-load-history }

```python
AttributeState.load_history()
```

**ধরন:** মেথড

`history`-এর মতো, কিন্তু অ্যাট্রিবিউট লোড না থাকলে **আগে লোড করে** (দরকার হলে SQL চালায়)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.addresses.history.unchanged, len(inspect(u).attrs.addresses.load_history().unchanged))   # () 2
```

### `AttributeState.loaded_value` { #attributestate-loaded-value }

**ধরন:** প্রপার্টি

ডেটাবেস থেকে শেষবার লোড হওয়া মান; লোড না থাকলে `NO_VALUE`। **নিজে লোড করে না**।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.addresses.loaded_value)   # LoaderCallableStatus.NO_VALUE
```

### `AttributeState.state` { #attributestate-state }

**ধরন:** অ্যাট্রিবিউট

মূল অবজেক্টের `InstanceState`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.name.state is inspect(u))   # True
```

### `AttributeState.value` { #attributestate-value }

**ধরন:** প্রপার্টি

বর্তমান মান (`getattr(obj, key)`-এর মতো; লোড না থাকলে লোড করে)।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.name.value)   # রহিম
```

## `IdentityMap` { #identitymap }

```python
from sqlalchemy.orm import IdentityMap
```

সেশনের "কে কে আছে" তালিকা: identity key (`(ক্লাস, primary key, token)`) → অবজেক্ট। এর জন্যই একই সেশনে `session.get(User, 1)` দুবার ডাকলে **একই** অবজেক্ট আসে, আর দ্বিতীয়বার SQL চলে না। **অবজেক্টগুলো দুর্বলভাবে (weak reference) রাখা হয়:** আপনার কোডে কোনো রেফারেন্স না থাকলে আর অসংরক্ষিত বদল না থাকলে অবজেক্টটি সাথে সাথে map থেকে চলে যায় (নিচে `keys()`-এর উদাহরণ)। তাই `inspect(session.get(User, 1)).persistent` লিখলে `False` আসতে পারে: অবজেক্টটি ধরে রাখার কেউ নেই। আগে `u = session.get(User, 1)`, তারপর `inspect(u)`।

**উদাহরণ:**

```python
u1 = session.get(User, 1)
u2 = session.scalars(select(User).where(User.name == "রহিম")).one()
print(u1 is u2, len(session.identity_map))   # True 1
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #identitymap-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#identitymap-add) | মেথড (internal) | একটি `InstanceState` যোগ করে; আগে থেকে একই key-তে অন্য অবজেক্ট থাকলে এরর। |
| [`all_states()`](#identitymap-all-states) | মেথড | সব অবজেক্টের `InstanceState`-এর তালিকা। |
| [`check_modified()`](#identitymap-check-modified) | মেথড | কোনো অবজেক্টে অসংরক্ষিত বদল আছে কি না। |
| [`contains_state()`](#identitymap-contains-state) | মেথড | নির্দিষ্ট `InstanceState`-টি এখানে আছে কি না। |
| [`fast_get_state()`](#identitymap-fast-get-state) | মেথড (internal) | key দিয়ে `InstanceState` (অবজেক্ট নয়), দ্রুত পথে; না থাকলে `None`। |
| [`get()`](#identitymap-get) | মেথড | identity key দিয়ে অবজেক্ট; না থাকলে `default`। |
| [`has_key()`](#identitymap-has-key) | মেথড | key-টি আছে কি না (`key in session.identity_map`-এর মতো)। |
| [`keys()`](#identitymap-keys) | মেথড | সব identity key। |
| [`replace()`](#identitymap-replace) | মেথড (internal) | একই key-তে নতুন `InstanceState` বসায় (আগেরটি থাকলে ফেরত দেয়)। |
| [`safe_discard()`](#identitymap-safe-discard) | মেথড (internal) | `InstanceState`-টি থাকলে সরায়, না থাকলে চুপ। |
| [`values()`](#identitymap-values) | মেথড | সব অবজেক্ট। |

### `IdentityMap.add()` { #identitymap-add }

```python
IdentityMap.add(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি `InstanceState` যোগ করে; আগে থেকে একই key-তে অন্য অবজেক্ট থাকলে এরর। ORM নিজে ব্যবহার করে।

**উদাহরণ:**

```python
print(callable(session.identity_map.add))   # True
```

### `IdentityMap.all_states()` { #identitymap-all-states }

```python
IdentityMap.all_states()
```

**ধরন:** মেথড

সব অবজেক্টের `InstanceState`-এর তালিকা।

**উদাহরণ:**

```python
u1, u2 = session.get(User, 1), session.get(User, 2)
print(sorted(s.identity for s in session.identity_map.all_states()))   # [(1,), (2,)]
```

### `IdentityMap.check_modified()` { #identitymap-check-modified }

```python
IdentityMap.check_modified()
```

**ধরন:** মেথড

কোনো অবজেক্টে অসংরক্ষিত বদল আছে কি না।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(session.identity_map.check_modified(), end=" "); u.name = "x"
print(session.identity_map.check_modified())   # False True
```

### `IdentityMap.contains_state()` { #identitymap-contains-state }

```python
IdentityMap.contains_state(state)
```

**ধরন:** মেথড

নির্দিষ্ট `InstanceState`-টি এখানে আছে কি না।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(session.identity_map.contains_state(inspect(u)))   # True
```

### `IdentityMap.fast_get_state()` { #identitymap-fast-get-state }

```python
IdentityMap.fast_get_state(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

key দিয়ে `InstanceState` (অবজেক্ট নয়), দ্রুত পথে; না থাকলে `None`।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(session.identity_map.fast_get_state(inspect(u).identity_key).object is u)   # True
```

### `IdentityMap.get()` { #identitymap-get }

```python
IdentityMap.get(key, default=None)
```

**ধরন:** মেথড

identity key দিয়ে অবজেক্ট; না থাকলে `default`। key বানাতে `sqlalchemy.orm.util.identity_key(User, 1)`।

**উদাহরণ:**

```python
from sqlalchemy.orm.util import identity_key
u = session.get(User, 1)
print(session.identity_map.get(identity_key(User, 1)) is u, session.identity_map.get(identity_key(User, 9)))   # True None
```

### `IdentityMap.has_key()` { #identitymap-has-key }

```python
IdentityMap.has_key(key)
```

**ধরন:** মেথড

key-টি আছে কি না (`key in session.identity_map`-এর মতো)।

**উদাহরণ:**

```python
from sqlalchemy.orm.util import identity_key
u = session.get(User, 1)
print(session.identity_map.has_key(identity_key(User, 1)))   # True
```

### `IdentityMap.keys()` { #identitymap-keys }

```python
IdentityMap.keys()
```

**ধরন:** মেথড

সব identity key।

**উদাহরণ:**

```python
session.get(User, 1)                  # ফল কোথাও রাখিনি
print(len(session.identity_map))   # 0  (অবজেক্ট garbage collect হয়ে map থেকে চলে গেল)
u2 = session.get(User, 2)             # এবার রেফারেন্স রাখলাম
print([(k[0].__name__, k[1]) for k in session.identity_map.keys()])   # [('User', (2,))]
```

### `IdentityMap.replace()` { #identitymap-replace }

```python
IdentityMap.replace(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একই key-তে নতুন `InstanceState` বসায় (আগেরটি থাকলে ফেরত দেয়)।

**উদাহরণ:**

```python
print(callable(session.identity_map.replace))   # True
```

### `IdentityMap.safe_discard()` { #identitymap-safe-discard }

```python
IdentityMap.safe_discard(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`InstanceState`-টি থাকলে সরায়, না থাকলে চুপ। (সাধারণ কোডে `session.expunge()`।)

**উদাহরণ:**

```python
u = session.get(User, 1)
session.identity_map.safe_discard(inspect(u))
print(len(session.identity_map))   # 0
```

### `IdentityMap.values()` { #identitymap-values }

```python
IdentityMap.values()
```

**ধরন:** মেথড

সব অবজেক্ট।

**উদাহরণ:**

```python
u = session.get(User, 1)
print([x.name for x in session.identity_map.values()])   # ['রহিম']
```

## ক্লাসের দিক { #instrumentedattribute-group }

## `InstrumentedAttribute` { #instrumentedattribute }

```python
from sqlalchemy.orm import InstrumentedAttribute
```

`User.name` (ক্লাস-লেভেলে) আসলে এই অবজেক্ট: একটি Python descriptor। ক্লাস থেকে পড়লে SQL এক্সপ্রেশন (`User.name == "x"`), অবজেক্ট থেকে পড়লে মান (`user.name`), আর লিখলে বদলের হিসাব রাখে। কুয়েরিতে ব্যবহারের সব অপারেটর তার মূল ক্লাস [`QueryableAttribute`](operators.md#queryableattribute)-এর।

**উদাহরণ:**

```python
print(type(User.name).__name__, isinstance(User.addresses, InstrumentedAttribute))   # InstrumentedAttribute True
print(User.name == "রহিম")   # users.name = :name_1
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`QueryableAttribute`](operators.md#queryableattribute-summary)-এর মতো।

## `ClassManager` { #classmanager }

```python
from sqlalchemy.orm import ClassManager
```

(প্রধানত অভ্যন্তরীণ) ক্লাস-লেভেলের হিসাব: কোন অ্যাট্রিবিউট instrumented, নতুন অবজেক্টের `InstanceState` কীভাবে বসবে, collection কীভাবে বানাবে। এটি একটি `dict`: অ্যাট্রিবিউটের নাম → `InstrumentedAttribute`।

**উদাহরণ:**

```python
m = inspect(User).class_manager
print(type(m).__name__, sorted(m.keys()))   # ClassManager ['addresses', 'id', 'name']
```

**Python `dict`-এর সব মেথড** (`clear()`, `copy()`, `fromkeys()`, `get()`, `items()`, `keys()`, `pop()`, `popitem()`, `setdefault()`, `update()`, `values()`) সাধারণ `dict`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #classmanager-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`MANAGER_ATTR`](#classmanager-MANAGER-ATTR) | অ্যাট্রিবিউট (internal) | ক্লাসে manager যে অ্যাট্রিবিউট-নামে রাখা হয়। |
| [`STATE_ATTR`](#classmanager-STATE-ATTR) | অ্যাট্রিবিউট (internal) | প্রতিটি অবজেক্টে `InstanceState` যে অ্যাট্রিবিউট-নামে রাখা হয়। |
| [`attributes`](#classmanager-attributes) | প্রপার্টি | সব instrumented অ্যাট্রিবিউট (`InstrumentedAttribute`)। |
| [`declarative_scan`](#classmanager-declarative-scan) | অ্যাট্রিবিউট (internal) | declarative ক্লাস স্ক্যান করার ভেতরের অবজেক্টের weak reference (ম্যাপিং শেষ হলে সাধারণত `None`)। |
| [`deferred_scalar_loader`](#classmanager-deferred-scalar-loader) | প্রপার্টি ⚠️ deprecated | (১.৪ থেকে বাতিলের পথে) expired অ্যাট্রিবিউট লোডারের পুরোনো নাম; এখন `expired_attribute_loader`। |
| [`dict_getter()`](#classmanager-dict-getter) | মেথড (internal) | অবজেক্ট থেকে তার `__dict__` বের করার ফাংশন দেয়। |
| [`get_impl()`](#classmanager-get-impl) | মেথড (internal) | অ্যাট্রিবিউটের ভেতরের implementation। |
| [`has_parent()`](#classmanager-has-parent) | মেথড (internal) | অবজেক্টটির কোনো relationship-এ "অভিভাবক" আছে কি না: `delete-orphan` হিসাবের জন্য। |
| [`has_state()`](#classmanager-has-state) | মেথড | অবজেক্টটিতে `InstanceState` বসানো হয়েছে কি না। |
| [`initialize_collection()`](#classmanager-initialize-collection) | মেথড (internal) | একটি collection অ্যাট্রিবিউটের জন্য খালি collection আর তার adapter বানায়। |
| [`install_descriptor()`](#classmanager-install-descriptor) | মেথড (internal) | ক্লাসে একটি descriptor (অ্যাট্রিবিউট) বসায়। |
| [`install_member()`](#classmanager-install-member) | মেথড (internal) | ক্লাসে একটি সাধারণ সদস্য বসায় (instrumentation-এর জন্য)। |
| [`instrument_attribute()`](#classmanager-instrument-attribute) | মেথড (internal) | একটি অ্যাট্রিবিউটকে instrumented হিসেবে নথিভুক্ত করে আর ক্লাসে বসায়। |
| [`instrument_collection_class()`](#classmanager-instrument-collection-class) | মেথড (internal) | একটি collection class-কে instrument করে factory দেয়। |
| [`is_instrumented()`](#classmanager-is-instrumented) | মেথড | নামটি instrumented অ্যাট্রিবিউট কি না। |
| [`is_mapped`](#classmanager-is-mapped) | প্রপার্টি | ক্লাসটি পুরোপুরি ম্যাপ হয়েছে কি না। |
| [`manage()`](#classmanager-manage) | মেথড (internal) | নিজেকে ক্লাসের manager হিসেবে বসায় (ক্লাসে `_sa_class_manager`)। |
| [`manager_getter()`](#classmanager-manager-getter) | মেথড (internal) | ক্লাস থেকে manager বের করার ফাংশন দেয়। |
| [`mapper`](#classmanager-mapper) | প্রপার্টি | ক্লাসের `Mapper`। |
| [`memoized_attribute`](#classmanager-memoized-attribute) | অ্যাট্রিবিউট (internal) | (ভেতরের ডেকোরেটর) একবার হিসাব করে মনে রাখা অ্যাট্রিবিউট। |
| [`memoized_instancemethod()`](#classmanager-memoized-instancemethod) | ক্লাস মেথড (internal) | (ভেতরের ডেকোরেটর) একবার হিসাব করে মনে রাখা মেথড। |
| [`new_instance()`](#classmanager-new-instance) | মেথড (internal) | `__init__` না ডেকে ক্লাসের নতুন অবজেক্ট বানায় (ORM ডেটাবেস থেকে লোডের সময় এভাবে বানায়)। |
| [`original_init`](#classmanager-original-init) | অ্যাট্রিবিউট (internal) | ক্লাসের আসল `__init__` (instrument করার আগের)। |
| [`post_configure_attribute()`](#classmanager-post-configure-attribute) | মেথড (internal) | অ্যাট্রিবিউট কনফিগার হওয়ার পর ইভেন্ট-সংক্রান্ত কাজ। |
| [`registry`](#classmanager-registry) | অ্যাট্রিবিউট | ক্লাসটি যে `registry`-তে ম্যাপ করা। |
| [`setup_instance()`](#classmanager-setup-instance) | মেথড (internal) | একটি অবজেক্টে `InstanceState` বসায়। |
| [`state_getter()`](#classmanager-state-getter) | মেথড (internal) | অবজেক্ট থেকে `InstanceState` বের করার ফাংশন দেয়। |
| [`subclass_managers()`](#classmanager-subclass-managers) | মেথড (internal) | subclass-গুলোর manager (inheritance ম্যাপিংয়ে)। |
| [`teardown_instance()`](#classmanager-teardown-instance) | মেথড (internal) | অবজেক্ট থেকে instrumentation সরায়। |
| [`uninstall_descriptor()`](#classmanager-uninstall-descriptor) | মেথড (internal) | ক্লাস থেকে descriptor সরায়। |
| [`uninstall_member()`](#classmanager-uninstall-member) | মেথড (internal) | ক্লাস থেকে সদস্য সরায়। |
| [`uninstrument_attribute()`](#classmanager-uninstrument-attribute) | মেথড (internal) | অ্যাট্রিবিউটের instrumentation সরায়। |
| [`unregister()`](#classmanager-unregister) | মেথড (internal) | এই manager-এর বসানো সব instrumentation সরায় (`clear_mappers()` ভেতরে)। |

### `ClassManager.MANAGER_ATTR` { #classmanager-MANAGER-ATTR }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসে manager যে অ্যাট্রিবিউট-নামে রাখা হয়।

**উদাহরণ:**

```python
print(ClassManager.MANAGER_ATTR)   # _sa_class_manager
```

### `ClassManager.STATE_ATTR` { #classmanager-STATE-ATTR }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

প্রতিটি অবজেক্টে `InstanceState` যে অ্যাট্রিবিউট-নামে রাখা হয়।

**উদাহরণ:**

```python
print(ClassManager.STATE_ATTR, hasattr(session.get(User, 1), ClassManager.STATE_ATTR))   # _sa_instance_state True
```

### `ClassManager.attributes` { #classmanager-attributes }

**ধরন:** প্রপার্টি

সব instrumented অ্যাট্রিবিউট (`InstrumentedAttribute`)।

**উদাহরণ:**

```python
print(sorted(a.key for a in inspect(User).class_manager.attributes))   # ['addresses', 'id', 'name']
```

### `ClassManager.declarative_scan` { #classmanager-declarative-scan }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

declarative ক্লাস স্ক্যান করার ভেতরের অবজেক্টের weak reference (ম্যাপিং শেষ হলে সাধারণত `None`)।

**উদাহরণ:**

```python
print(inspect(User).class_manager.declarative_scan is None or callable(inspect(User).class_manager.declarative_scan))   # True
```

### `ClassManager.deferred_scalar_loader` { #classmanager-deferred-scalar-loader }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(১.৪ থেকে বাতিলের পথে) expired অ্যাট্রিবিউট লোডারের পুরোনো নাম; এখন `expired_attribute_loader`।

**উদাহরণ:**

```python
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print(callable(inspect(User).class_manager.deferred_scalar_loader))   # True
```

### `ClassManager.dict_getter()` { #classmanager-dict-getter }

```python
ClassManager.dict_getter()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্ট থেকে তার `__dict__` বের করার ফাংশন দেয়।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(User).class_manager.dict_getter()(u)["name"])   # রহিম
```

### `ClassManager.get_impl()` { #classmanager-get-impl }

```python
ClassManager.get_impl(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটের ভেতরের implementation।

**উদাহরণ:**

```python
print(type(inspect(User).class_manager.get_impl("addresses")).__name__)   # _CollectionAttributeImpl
```

### `ClassManager.has_parent()` { #classmanager-has-parent }

```python
ClassManager.has_parent(state, key, optimistic=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টটির কোনো relationship-এ "অভিভাবক" আছে কি না: `delete-orphan` হিসাবের জন্য। অভিভাবক-হিসাব শুধু সেই relationship-এ রাখা হয় যেখানে `delete-orphan` (বা backref-এর কারণে) দরকার; অন্য জায়গায় ডাকলে `AssertionError`।

**উদাহরণ:**

```python
print(callable(ClassManager.has_parent))   # True
```

### `ClassManager.has_state()` { #classmanager-has-state }

```python
ClassManager.has_state(instance)
```

**ধরন:** মেথড

অবজেক্টটিতে `InstanceState` বসানো হয়েছে কি না।

**উদাহরণ:**

```python
print(inspect(User).class_manager.has_state(User(name="x")))   # True
```

### `ClassManager.initialize_collection()` { #classmanager-initialize-collection }

```python
ClassManager.initialize_collection(key, state, factory)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি collection অ্যাট্রিবিউটের জন্য খালি collection আর তার adapter বানায়।

**উদাহরণ:**

```python
print(callable(ClassManager.initialize_collection))   # True
```

### `ClassManager.install_descriptor()` { #classmanager-install-descriptor }

```python
ClassManager.install_descriptor(key, inst)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসে একটি descriptor (অ্যাট্রিবিউট) বসায়।

**উদাহরণ:**

```python
print(callable(ClassManager.install_descriptor))   # True
```

### `ClassManager.install_member()` { #classmanager-install-member }

```python
ClassManager.install_member(key, implementation)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসে একটি সাধারণ সদস্য বসায় (instrumentation-এর জন্য)।

**উদাহরণ:**

```python
print(callable(ClassManager.install_member))   # True
```

### `ClassManager.instrument_attribute()` { #classmanager-instrument-attribute }

```python
ClassManager.instrument_attribute(key, inst, propagated=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অ্যাট্রিবিউটকে instrumented হিসেবে নথিভুক্ত করে আর ক্লাসে বসায়।

**উদাহরণ:**

```python
print(callable(ClassManager.instrument_attribute))   # True
```

### `ClassManager.instrument_collection_class()` { #classmanager-instrument-collection-class }

```python
ClassManager.instrument_collection_class(key, collection_class)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি collection class-কে instrument করে factory দেয়।

**উদাহরণ:**

```python
print(callable(inspect(User).class_manager.instrument_collection_class("addresses", list)))   # True
```

### `ClassManager.is_instrumented()` { #classmanager-is-instrumented }

```python
ClassManager.is_instrumented(key, search=False)
```

**ধরন:** মেথড

নামটি instrumented অ্যাট্রিবিউট কি না।

**উদাহরণ:**

```python
m = inspect(User).class_manager
print(m.is_instrumented("name"), m.is_instrumented("nope"))   # True False
```

### `ClassManager.is_mapped` { #classmanager-is-mapped }

**ধরন:** প্রপার্টি

ক্লাসটি পুরোপুরি ম্যাপ হয়েছে কি না।

**উদাহরণ:**

```python
print(inspect(User).class_manager.is_mapped)   # True
```

### `ClassManager.manage()` { #classmanager-manage }

```python
ClassManager.manage()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নিজেকে ক্লাসের manager হিসেবে বসায় (ক্লাসে `_sa_class_manager`)।

**উদাহরণ:**

```python
print(callable(ClassManager.manage))   # True
```

### `ClassManager.manager_getter()` { #classmanager-manager-getter }

```python
ClassManager.manager_getter()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস থেকে manager বের করার ফাংশন দেয়।

**উদাহরণ:**

```python
print(inspect(User).class_manager.manager_getter()(User) is inspect(User).class_manager)   # True
```

### `ClassManager.mapper` { #classmanager-mapper }

**ধরন:** প্রপার্টি

ক্লাসের `Mapper`।

**উদাহরণ:**

```python
print(inspect(User).class_manager.mapper)   # Mapper[User(users)]
```

### `ClassManager.memoized_attribute` { #classmanager-memoized-attribute }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ভেতরের ডেকোরেটর) একবার হিসাব করে মনে রাখা অ্যাট্রিবিউট।

**উদাহরণ:**

```python
print(ClassManager.memoized_attribute.__name__)   # memoized_attribute
```

### `ClassManager.memoized_instancemethod()` { #classmanager-memoized-instancemethod }

```python
ClassManager.memoized_instancemethod(fn)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ভেতরের ডেকোরেটর) একবার হিসাব করে মনে রাখা মেথড।

**উদাহরণ:**

```python
print(callable(ClassManager.memoized_instancemethod))   # True
```

### `ClassManager.new_instance()` { #classmanager-new-instance }

```python
ClassManager.new_instance(state=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`__init__` না ডেকে ক্লাসের নতুন অবজেক্ট বানায় (ORM ডেটাবেস থেকে লোডের সময় এভাবে বানায়)।

**উদাহরণ:**

```python
u = inspect(User).class_manager.new_instance()
print(type(u).__name__, inspect(u).transient)   # User True
```

### `ClassManager.original_init` { #classmanager-original-init }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাসের আসল `__init__` (instrument করার আগের)।

**উদাহরণ:**

```python
print(callable(inspect(User).class_manager.original_init))   # True
```

### `ClassManager.post_configure_attribute()` { #classmanager-post-configure-attribute }

```python
ClassManager.post_configure_attribute(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউট কনফিগার হওয়ার পর ইভেন্ট-সংক্রান্ত কাজ।

**উদাহরণ:**

```python
print(callable(ClassManager.post_configure_attribute))   # True
```

### `ClassManager.registry` { #classmanager-registry }

**ধরন:** অ্যাট্রিবিউট

ক্লাসটি যে `registry`-তে ম্যাপ করা।

**উদাহরণ:**

```python
print(inspect(User).class_manager.registry is Base.registry)   # True
```

### `ClassManager.setup_instance()` { #classmanager-setup-instance }

```python
ClassManager.setup_instance(instance, state=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টে `InstanceState` বসায়।

**উদাহরণ:**

```python
print(callable(ClassManager.setup_instance))   # True
```

### `ClassManager.state_getter()` { #classmanager-state-getter }

```python
ClassManager.state_getter()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্ট থেকে `InstanceState` বের করার ফাংশন দেয়।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(User).class_manager.state_getter()(u) is inspect(u))   # True
```

### `ClassManager.subclass_managers()` { #classmanager-subclass-managers }

```python
ClassManager.subclass_managers(recursive)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

subclass-গুলোর manager (inheritance ম্যাপিংয়ে)।

**উদাহরণ:**

```python
print(list(inspect(User).class_manager.subclass_managers(True)))   # []
```

### `ClassManager.teardown_instance()` { #classmanager-teardown-instance }

```python
ClassManager.teardown_instance(instance)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্ট থেকে instrumentation সরায়।

**উদাহরণ:**

```python
print(callable(ClassManager.teardown_instance))   # True
```

### `ClassManager.uninstall_descriptor()` { #classmanager-uninstall-descriptor }

```python
ClassManager.uninstall_descriptor(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস থেকে descriptor সরায়।

**উদাহরণ:**

```python
print(callable(ClassManager.uninstall_descriptor))   # True
```

### `ClassManager.uninstall_member()` { #classmanager-uninstall-member }

```python
ClassManager.uninstall_member(key)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস থেকে সদস্য সরায়।

**উদাহরণ:**

```python
print(callable(ClassManager.uninstall_member))   # True
```

### `ClassManager.uninstrument_attribute()` { #classmanager-uninstrument-attribute }

```python
ClassManager.uninstrument_attribute(key, propagated=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটের instrumentation সরায়।

**উদাহরণ:**

```python
print(callable(ClassManager.uninstrument_attribute))   # True
```

### `ClassManager.unregister()` { #classmanager-unregister }

```python
ClassManager.unregister()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই manager-এর বসানো সব instrumentation সরায় (`clear_mappers()` ভেতরে)।

**উদাহরণ:**

```python
print(callable(ClassManager.unregister))   # True
```

## ইভেন্ট হুকে যা আসে { #ormexecutestate-group }

## `ORMExecuteState` { #ormexecutestate }

```python
from sqlalchemy.orm import ORMExecuteState
```

`SessionEvents.do_orm_execute` ইভেন্টের আর্গুমেন্ট: `session.execute()` (বা lazy load ইত্যাদি) যে স্টেটমেন্ট চালাতে যাচ্ছে তার সব তথ্য। হুকে এটি দেখে আপনি স্টেটমেন্ট বদলাতে পারেন (যেমন সব কুয়েরিতে "soft delete" শর্ত যোগ), আবার চালাতে পারেন (`invoke_statement()`, যেমন ক্যাশিং), বা শুধু লগ করতে পারেন। হুক থেকে `Result` ফেরত দিলে সেটাই চূড়ান্ত ফল হয়।

**উদাহরণ:**

```python
log = []
@event.listens_for(session, "do_orm_execute")
def watch(state):
    log.append((state.is_select, state.is_relationship_load, state.bind_mapper.class_.__name__))
u = session.get(User, 1)
u.addresses                                    # lazy load
print(log)   # [(True, False, 'User'), (True, True, 'Address')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #ormexecutestate-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all_mappers`](#ormexecutestate-all-mappers) | প্রপার্টি | স্টেটমেন্টের শীর্ষ স্তরে যত mapper জড়িত (যেমন `select(User, Address)`-এ দুটো)। |
| [`bind_arguments`](#ormexecutestate-bind-arguments) | অ্যাট্রিবিউট | কোন ডেটাবেসে চলবে তা ঠিক করার আর্গুমেন্ট (`mapper`, `clause` …) dict। |
| [`bind_mapper`](#ormexecutestate-bind-mapper) | প্রপার্টি | মূল ("bind") mapper: সাধারণত স্টেটমেন্টের প্রথম entity। |
| [`execution_options`](#ormexecutestate-execution-options) | অ্যাট্রিবিউট | মোট execution options (স্টেটমেন্টের + `execute()`-এ দেওয়া), একসাথে। |
| [`identity_token`](#ormexecutestate-identity-token) | অ্যাট্রিবিউট (internal) | sharding-এর জন্য রাখা একটি slot। |
| [`invoke_statement()`](#ormexecutestate-invoke-statement) | মেথড | স্টেটমেন্টটি (বা বদলানো রূপ) **এখনই চালিয়ে** `Result` দেয়, আর বাকি `do_orm_execute` হুকগুলোও আবার চলে না। |
| [`is_column_load`](#ormexecutestate-is-column-load) | প্রপার্টি | `True` হলে এটা একটি **বিদ্যমান** অবজেক্টের কলাম আবার লোড করা (expired অ্যাট্রিবিউট, `refresh()`, deferred কলাম)। |
| [`is_delete`](#ormexecutestate-is-delete) | প্রপার্টি | স্টেটমেন্টটি DELETE কি না (ORM-enabled `delete()`)। |
| [`is_executemany`](#ormexecutestate-is-executemany) | প্রপার্টি | প্যারামিটার একাধিক dict-এর তালিকা কি না (বাল্ক INSERT/UPDATE)। |
| [`is_from_statement`](#ormexecutestate-is-from-statement) | প্রপার্টি | `select(...).from_statement(text(...))` ধরনের কি না। |
| [`is_insert`](#ormexecutestate-is-insert) | প্রপার্টি | INSERT কি না। |
| [`is_orm_statement`](#ormexecutestate-is-orm-statement) | প্রপার্টি | ORM স্টেটমেন্ট কি না (মডেল/ORM অ্যাট্রিবিউট আছে)। |
| [`is_relationship_load`](#ormexecutestate-is-relationship-load) | প্রপার্টি | relationship লোড করার জন্য (lazy load, `selectinload` ইত্যাদি) কি না। |
| [`is_select`](#ormexecutestate-is-select) | প্রপার্টি | SELECT কি না। |
| [`is_update`](#ormexecutestate-is-update) | প্রপার্টি | UPDATE কি না। |
| [`lazy_loaded_from`](#ormexecutestate-lazy-loaded-from) | প্রপার্টি | lazy load হলে কোন অবজেক্টের (`InstanceState`) জন্য, নইলে `None`। |
| [`load_options`](#ormexecutestate-load-options) | প্রপার্টি (internal) | এই execution-এর ORM লোড-অপশন অবজেক্ট (populate_existing, autoflush ইত্যাদি)। |
| [`loader_strategy_path`](#ormexecutestate-loader-strategy-path) | প্রপার্টি (internal) | relationship লোডের বর্তমান পথ (`PathRegistry`), নইলে `None`। |
| [`local_execution_options`](#ormexecutestate-local-execution-options) | অ্যাট্রিবিউট | শুধু `execute(..., execution_options={...})`-এ দেওয়া অপশন (স্টেটমেন্টেরগুলো বাদে)। |
| [`parameters`](#ormexecutestate-parameters) | অ্যাট্রিবিউট | `execute()`-এ দেওয়া প্যারামিটার (dict বা তালিকা)। |
| [`session`](#ormexecutestate-session) | অ্যাট্রিবিউট | যে `Session`-এ চলছে। |
| [`statement`](#ormexecutestate-statement) | অ্যাট্রিবিউট | যে স্টেটমেন্ট চলবে। |
| [`update_delete_options`](#ormexecutestate-update-delete-options) | প্রপার্টি (internal) | ORM UPDATE/DELETE-এর অপশন (যেমন `synchronize_session`)। |
| [`update_execution_options()`](#ormexecutestate-update-execution-options) | মেথড | এই execution-এর লোকাল অপশন হালনাগাদ করে (হুক থেকে অপশন যোগ করতে)। |
| [`user_defined_options`](#ormexecutestate-user-defined-options) | প্রপার্টি | স্টেটমেন্টে দেওয়া [`UserDefinedOption`](#userdefinedoption)-গুলো: কুয়েরি থেকে হুকে নিজের তথ্য পাঠানোর উপায়। |

### `ORMExecuteState.all_mappers` { #ormexecutestate-all-mappers }

**ধরন:** প্রপার্টি

স্টেটমেন্টের শীর্ষ স্তরে যত mapper জড়িত (যেমন `select(User, Address)`-এ দুটো)।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append([m.class_.__name__ for m in st.all_mappers]))
session.execute(select(User, Address).join(User.addresses))
print(seen)   # [['User', 'Address']]
```

### `ORMExecuteState.bind_arguments` { #ormexecutestate-bind-arguments }

**ধরন:** অ্যাট্রিবিউট

কোন ডেটাবেসে চলবে তা ঠিক করার আর্গুমেন্ট (`mapper`, `clause` …) dict। নিজের শার্ডিং/রিড-রেপ্লিকা লজিকে কাজে লাগে।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(sorted(st.bind_arguments)))
session.execute(select(User))
print(seen)   # [['clause', 'mapper']]
```

### `ORMExecuteState.bind_mapper` { #ormexecutestate-bind-mapper }

**ধরন:** প্রপার্টি

মূল ("bind") mapper: সাধারণত স্টেটমেন্টের প্রথম entity।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.bind_mapper))
session.execute(select(Address))
print(seen[0])   # Mapper[Address(addresses)]
```

### `ORMExecuteState.execution_options` { #ormexecutestate-execution-options }

**ধরন:** অ্যাট্রিবিউট

মোট execution options (স্টেটমেন্টের + `execute()`-এ দেওয়া), একসাথে।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.execution_options.get("yield_per")))
session.execute(select(User).execution_options(yield_per=5))
print(seen)   # [5]
```

### `ORMExecuteState.identity_token` { #ormexecutestate-identity-token }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

sharding-এর জন্য রাখা একটি slot। সাধারণ execution-এ এটি **বসানোই হয় না**, তাই পড়লে `AttributeError`; `getattr(state, "identity_token", None)` লিখুন।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(getattr(st, "identity_token", None)))
session.execute(select(User))
print("identity_token" in ORMExecuteState.__slots__, seen)   # True [None]
```

### `ORMExecuteState.invoke_statement()` { #ormexecutestate-invoke-statement }

```python
ORMExecuteState.invoke_statement(statement=None, params=None, execution_options=None, bind_arguments=None)
```

**ধরন:** মেথড

স্টেটমেন্টটি (বা বদলানো রূপ) **এখনই চালিয়ে** `Result` দেয়, আর বাকি `do_orm_execute` হুকগুলোও আবার চলে না। চাইলে `statement`, `params`, `execution_options`, `bind_arguments` বদলে দিন। হুক থেকে এই ফল ফেরত দিলে সেটাই `session.execute()`-এর ফল (ক্যাশিং রেসিপির মূল)।

**উদাহরণ:**

```python
@event.listens_for(session, "do_orm_execute")
def only_first(state):
    if state.is_select and state.bind_mapper.class_ is User and not state.is_column_load:
        return state.invoke_statement(statement=state.statement.where(User.id == 1))
print([u.name for u in session.scalars(select(User))])   # ['রহিম']
```

### `ORMExecuteState.is_column_load` { #ormexecutestate-is-column-load }

**ধরন:** প্রপার্টি

`True` হলে এটা একটি **বিদ্যমান** অবজেক্টের কলাম আবার লোড করা (expired অ্যাট্রিবিউট, `refresh()`, deferred কলাম)। soft-delete শর্ত যোগ করার হুকে এগুলো সাধারণত বাদ দিতে হয়।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_column_load))
u = session.get(User, 1); session.expire(u); u.name
print(seen)   # [False, True]
```

### `ORMExecuteState.is_delete` { #ormexecutestate-is-delete }

**ধরন:** প্রপার্টি

স্টেটমেন্টটি DELETE কি না (ORM-enabled `delete()`)।

**উদাহরণ:**

```python
from sqlalchemy import delete
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_delete))
session.execute(delete(Address).where(Address.id == 99))
print(seen)   # [True]
```

### `ORMExecuteState.is_executemany` { #ormexecutestate-is-executemany }

**ধরন:** প্রপার্টি

প্যারামিটার একাধিক dict-এর তালিকা কি না (বাল্ক INSERT/UPDATE)।

**উদাহরণ:**

```python
from sqlalchemy import insert
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_executemany))
session.execute(insert(User), [{"id": 8, "name": "ক"}, {"id": 9, "name": "খ"}])
print(seen)   # [True]
```

### `ORMExecuteState.is_from_statement` { #ormexecutestate-is-from-statement }

**ধরন:** প্রপার্টি

`select(...).from_statement(text(...))` ধরনের কি না।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_from_statement))
session.execute(select(User).from_statement(text("SELECT * FROM users")))
print(seen)   # [True]
```

### `ORMExecuteState.is_insert` { #ormexecutestate-is-insert }

**ধরন:** প্রপার্টি

INSERT কি না।

**উদাহরণ:**

```python
from sqlalchemy import insert
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_insert))
session.execute(insert(User).values(id=7, name="নতুন"))
print(seen)   # [True]
```

### `ORMExecuteState.is_orm_statement` { #ormexecutestate-is-orm-statement }

**ধরন:** প্রপার্টি

ORM স্টেটমেন্ট কি না (মডেল/ORM অ্যাট্রিবিউট আছে)। শুধু টেবিল বা `text()` হলে `False`।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_orm_statement))
session.execute(select(User)); session.execute(select(User.__table__))
print(seen)   # [True, False]
```

### `ORMExecuteState.is_relationship_load` { #ormexecutestate-is-relationship-load }

**ধরন:** প্রপার্টি

relationship লোড করার জন্য (lazy load, `selectinload` ইত্যাদি) কি না।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_relationship_load))
session.scalars(select(User).options(selectinload(User.addresses))).all()
print(seen)   # [False, True]
```

### `ORMExecuteState.is_select` { #ormexecutestate-is-select }

**ধরন:** প্রপার্টি

SELECT কি না।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_select))
session.execute(select(User))
print(seen)   # [True]
```

### `ORMExecuteState.is_update` { #ormexecutestate-is-update }

**ধরন:** প্রপার্টি

UPDATE কি না।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.is_update))
session.execute(update(User).where(User.id == 2).values(name="ক"))
print(seen)   # [True]
```

### `ORMExecuteState.lazy_loaded_from` { #ormexecutestate-lazy-loaded-from }

**ধরন:** প্রপার্টি

lazy load হলে কোন অবজেক্টের (`InstanceState`) জন্য, নইলে `None`।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.lazy_loaded_from))
u = session.get(User, 1); u.addresses
print(seen[0], seen[1].object is u)   # None True
```

### `ORMExecuteState.load_options` { #ormexecutestate-load-options }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই execution-এর ORM লোড-অপশন অবজেক্ট (populate_existing, autoflush ইত্যাদি)।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.load_options._populate_existing))
session.execute(select(User).execution_options(populate_existing=True))
print(seen)   # [True]
```

### `ORMExecuteState.loader_strategy_path` { #ormexecutestate-loader-strategy-path }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

relationship লোডের বর্তমান পথ (`PathRegistry`), নইলে `None`।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.loader_strategy_path))
session.execute(select(User))
print(seen)   # [None]
```

### `ORMExecuteState.local_execution_options` { #ormexecutestate-local-execution-options }

**ধরন:** অ্যাট্রিবিউট

শুধু `execute(..., execution_options={...})`-এ দেওয়া অপশন (স্টেটমেন্টেরগুলো বাদে)।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(
    {k: v for k, v in st.local_execution_options.items() if not k.startswith("_")}))   # _ দিয়ে শুরু = ভেতরের অপশন
session.execute(select(User), execution_options={"x": 1})
print(seen)   # [{'x': 1}]
```

### `ORMExecuteState.parameters` { #ormexecutestate-parameters }

**ধরন:** অ্যাট্রিবিউট

`execute()`-এ দেওয়া প্যারামিটার (dict বা তালিকা)।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.parameters))
session.execute(select(User).where(User.id == text(":uid")), {"uid": 1})
print(seen)   # [{'uid': 1}]
```

### `ORMExecuteState.session` { #ormexecutestate-session }

**ধরন:** অ্যাট্রিবিউট

যে `Session`-এ চলছে।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.session is session))
session.execute(select(User))
print(seen)   # [True]
```

### `ORMExecuteState.statement` { #ormexecutestate-statement }

**ধরন:** অ্যাট্রিবিউট

যে স্টেটমেন্ট চলবে। হুকে **নতুন স্টেটমেন্ট বসিয়ে দিলে** সেটাই চলবে: `state.statement = state.statement.where(...)` (বা সাথে `with_loader_criteria()` অপশন)।

**উদাহরণ:**

```python
@event.listens_for(session, "do_orm_execute")
def hide_karim(state):
    if state.is_select and not state.is_column_load and not state.is_relationship_load:
        state.statement = state.statement.options(with_loader_criteria(User, User.name != "করিম"))
print([u.name for u in session.scalars(select(User))])   # ['রহিম']
```

### `ORMExecuteState.update_delete_options` { #ormexecutestate-update-delete-options }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ORM UPDATE/DELETE-এর অপশন (যেমন `synchronize_session`)।

**উদাহরণ:**

```python
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append(st.update_delete_options._synchronize_session))
session.execute(update(User).where(User.id == 2).values(name="ক"))
print(seen)   # ['auto']
```

### `ORMExecuteState.update_execution_options()` { #ormexecutestate-update-execution-options }

```python
ORMExecuteState.update_execution_options(**opts)
```

**ধরন:** মেথড

এই execution-এর লোকাল অপশন হালনাগাদ করে (হুক থেকে অপশন যোগ করতে)।

**উদাহরণ:**

```python
seen = []
@event.listens_for(session, "do_orm_execute")
def add_opt(state):
    state.update_execution_options(my_tag="audit")
    seen.append(state.local_execution_options["my_tag"])
session.execute(select(User))
print(seen)   # ['audit']
```

### `ORMExecuteState.user_defined_options` { #ormexecutestate-user-defined-options }

**ধরন:** প্রপার্টি

স্টেটমেন্টে দেওয়া [`UserDefinedOption`](#userdefinedoption)-গুলো: কুয়েরি থেকে হুকে নিজের তথ্য পাঠানোর উপায়।

**উদাহরণ:**

```python
class Tag(UserDefinedOption):
    pass
seen = []
event.listen(session, "do_orm_execute", lambda st: seen.append([o.payload for o in st.user_defined_options]))
session.execute(select(User).options(Tag("রিপোর্ট")))
print(seen)   # [['রিপোর্ট']]
```

## `UserDefinedOption` { #userdefinedoption }

```python
from sqlalchemy.orm import UserDefinedOption
```

নিজের "অপশন" বানানোর মূল ক্লাস: `select(...).options(MyOption(...))` দিলে SQL-এ কিছু বদলায় না, কিন্তু `do_orm_execute` হুকে `state.user_defined_options`-এ পাওয়া যায়। যেমন "এই কুয়েরি ক্যাশ করো" বা "এটা রিপোর্টের কুয়েরি" চিহ্ন দিতে।

**উদাহরণ:**

```python
class CacheFor(UserDefinedOption):
    pass
opt = CacheFor(60)
print(opt.payload, str(select(User).options(opt)) == str(select(User)))   # 60 True
```

### কনস্ট্রাক্টরের প্যারামিটার { #userdefinedoption-params }

```python
UserDefinedOption(payload=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `payload` | অপশনের সাথে পাঠানো যেকোনো তথ্য। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #userdefinedoption-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get_children()`](#userdefinedoption-get-children) | মেথড (internal) | traversal-এর অংশ। |
| [`payload`](#userdefinedoption-payload) | অ্যাট্রিবিউট | কনস্ট্রাক্টরে দেওয়া তথ্য। |
| [`propagate_to_loaders`](#userdefinedoption-propagate-to-loaders) | অ্যাট্রিবিউট | `True` (ক্লাস-লেভেলে) দিলে অপশনটি lazy load-এর কুয়েরিতেও যায়। |

### `UserDefinedOption.get_children()` { #userdefinedoption-get-children }

```python
UserDefinedOption.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

traversal-এর অংশ।

**উদাহরণ:**

```python
print(list(UserDefinedOption("x").get_children()))   # []
```

### `UserDefinedOption.payload` { #userdefinedoption-payload }

**ধরন:** অ্যাট্রিবিউট

কনস্ট্রাক্টরে দেওয়া তথ্য।

**উদাহরণ:**

```python
print(UserDefinedOption({"ttl": 60}).payload)   # {'ttl': 60}
```

### `UserDefinedOption.propagate_to_loaders` { #userdefinedoption-propagate-to-loaders }

**ধরন:** অ্যাট্রিবিউট

`True` (ক্লাস-লেভেলে) দিলে অপশনটি lazy load-এর কুয়েরিতেও যায়। ডিফল্ট `False`।

**উদাহরণ:**

```python
print(UserDefinedOption.propagate_to_loaders)   # False
```

## `AttributeEventToken` { #attributeeventtoken }

```python
from sqlalchemy.orm import AttributeEventToken
```

অ্যাট্রিবিউট ইভেন্টের (`set`, `append`, `remove` …) `initiator` আর্গুমেন্ট: "কে এই বদল শুরু করেছে"। backref-এর কারণে একই বদল দুই দিকে ইভেন্ট চালায়; টোকেন দেখে বোঝা যায় বদলটি কোন অ্যাট্রিবিউট থেকে এসেছে, আর অসীম লুপ এড়ানো যায়।

**উদাহরণ:**

```python
seen = []
@event.listens_for(Address.user, "set")
def on_set(target, value, oldvalue, initiator):
    seen.append((type(initiator).__name__, initiator.key))
a = Address(email="x@y.com")
a.user = session.get(User, 2)
print(seen)   # [('AttributeEventToken', 'user')]
```

### কনস্ট্রাক্টরের প্যারামিটার { #attributeeventtoken-params }

```python
AttributeEventToken(attribute_impl, op)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attribute_impl` | যে অ্যাট্রিবিউটের ইভেন্ট (ভেতরের implementation)। |
| `op` | অপারেশনের ধরন: `OP_APPEND`, `OP_REMOVE`, `OP_REPLACE`, `OP_BULK_REPLACE`। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #attributeeventtoken-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`hasparent()`](#attributeeventtoken-hasparent) | মেথড (internal) | দেওয়া অবজেক্টটির এই অ্যাট্রিবিউটে অভিভাবক আছে কি না। |
| [`impl`](#attributeeventtoken-impl) | অ্যাট্রিবিউট (internal) | অ্যাট্রিবিউটের implementation অবজেক্ট। |
| [`key`](#attributeeventtoken-key) | প্রপার্টি | যে অ্যাট্রিবিউটের ইভেন্ট তার নাম। |
| [`op`](#attributeeventtoken-op) | অ্যাট্রিবিউট | অপারেশনের ধরন (`attributes.OP_APPEND`, `OP_REMOVE`, `OP_REPLACE`, `OP_BULK_REPLACE`)। |
| [`parent_token`](#attributeeventtoken-parent-token) | অ্যাট্রিবিউট (internal) | একই অ্যাট্রিবিউটের সব ইভেন্টে একই থাকা টোকেন (backref-এর লুপ ধরতে তুলনা করা হয়)। |

### `AttributeEventToken.hasparent()` { #attributeeventtoken-hasparent }

```python
AttributeEventToken.hasparent(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

দেওয়া অবজেক্টটির এই অ্যাট্রিবিউটে অভিভাবক আছে কি না।

**উদাহরণ:**

```python
print(callable(AttributeEventToken.hasparent))   # True
```

### `AttributeEventToken.impl` { #attributeeventtoken-impl }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটের implementation অবজেক্ট।

**উদাহরণ:**

```python
seen = []
event.listen(Address.user, "set", lambda t, v, o, i: seen.append(type(i.impl).__name__))
Address(email="x").user = User(name="y")
print(seen)   # ['_ScalarObjectAttributeImpl']
```

### `AttributeEventToken.key` { #attributeeventtoken-key }

**ধরন:** প্রপার্টি

যে অ্যাট্রিবিউটের ইভেন্ট তার নাম।

**উদাহরণ:**

```python
seen = []
event.listen(User.addresses, "append", lambda t, v, i: seen.append(i.key))
User(name="y").addresses.append(Address(email="z"))
print(seen)   # ['addresses']
```

### `AttributeEventToken.op` { #attributeeventtoken-op }

**ধরন:** অ্যাট্রিবিউট

অপারেশনের ধরন (`attributes.OP_APPEND`, `OP_REMOVE`, `OP_REPLACE`, `OP_BULK_REPLACE`)।

**উদাহরণ:**

```python
seen = []
event.listen(User.addresses, "append", lambda t, v, i: seen.append(i.op is attributes.OP_APPEND))
User(name="y").addresses.append(Address(email="z"))
print(seen)   # [True]
```

### `AttributeEventToken.parent_token` { #attributeeventtoken-parent-token }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একই অ্যাট্রিবিউটের সব ইভেন্টে একই থাকা টোকেন (backref-এর লুপ ধরতে তুলনা করা হয়)।

**উদাহরণ:**

```python
seen = []
event.listen(Address.user, "set", lambda t, v, o, i: seen.append(i.parent_token is not None))
Address(email="x").user = User(name="y")
print(seen)   # [True]
```

## `QueryContext` { #querycontext }

```python
from sqlalchemy.orm.context import QueryContext
```

(অভ্যন্তরীণ) একটি ORM কুয়েরির ফল থেকে অবজেক্ট বানানোর সময়ের অবস্থা। `InstanceEvents.load(target, context)` আর `refresh(target, context, attrs)` ইভেন্টে `context` হিসেবে আসে; সেখান থেকে সেশন, execution options ইত্যাদি পড়া যায়।

**উদাহরণ:**

```python
seen = []
@event.listens_for(User, "load")
def on_load(target, context):
    seen.append((type(context).__name__, context.session is session, target.name))
session.get(User, 1)
print(seen)   # [('QueryContext', True, 'রহিম')]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #querycontext-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`attributes`](#querycontext-attributes) | অ্যাট্রিবিউট (internal) | লোডারদের ভাগ করা কাজের dict। |
| [`autoflush`](#querycontext-autoflush) | অ্যাট্রিবিউট (internal) | কুয়েরির আগে autoflush চালু ছিল কি না। |
| [`bind_arguments`](#querycontext-bind-arguments) | অ্যাট্রিবিউট (internal) | ডেটাবেস বেছে নেওয়ার আর্গুমেন্ট। |
| [`compile_state`](#querycontext-compile-state) | অ্যাট্রিবিউট (internal) | কম্পাইল হওয়া ORM স্টেটমেন্টের অবস্থা। |
| [`create_eager_joins`](#querycontext-create-eager-joins) | অ্যাট্রিবিউট (internal) | ঘোষিত কিন্তু ব্যবহার না হওয়া slot (eager join-এর তালিকা আসলে compile state-এ থাকে)। |
| [`default_load_options`](#querycontext-default-load-options) | অ্যাট্রিবিউট (internal) | লোড-অপশনের ডিফল্ট মানের ক্লাস। |
| [`execution_options`](#querycontext-execution-options) | অ্যাট্রিবিউট | `session.execute(..., execution_options={...})`-এ দেওয়া অপশন। |
| [`identity_token`](#querycontext-identity-token) | অ্যাট্রিবিউট (internal) | sharding-এর identity token। |
| [`invoke_all_eagers`](#querycontext-invoke-all-eagers) | অ্যাট্রিবিউট (internal) | সব eager loader চালাবে কি না। |
| [`load_options`](#querycontext-load-options) | অ্যাট্রিবিউট (internal) | লোড-অপশন অবজেক্ট। |
| [`loaders_require_buffering`](#querycontext-loaders-require-buffering) | অ্যাট্রিবিউট (internal) | লোডারদের সব রো আগে বাফার করা দরকার কি না। |
| [`loaders_require_uniquing`](#querycontext-loaders-require-uniquing) | অ্যাট্রিবিউট (internal) | ফলের ডুপ্লিকেট বাদ দেওয়া দরকার কি না (joined eager loading-এ)। |
| [`params`](#querycontext-params) | অ্যাট্রিবিউট (internal) | কুয়েরির প্যারামিটার। |
| [`partials`](#querycontext-partials) | অ্যাট্রিবিউট (internal) | আংশিকভাবে লোড হওয়া অবজেক্টের হিসাব। |
| [`populate_existing`](#querycontext-populate-existing) | অ্যাট্রিবিউট | সেশনে থাকা অবজেক্টও নতুন মানে ভরবে কি না। |
| [`post_load_paths`](#querycontext-post-load-paths) | অ্যাট্রিবিউট (internal) | লোড শেষে চলার কাজ (যেমন selectin লোড)। |
| [`propagated_loader_options`](#querycontext-propagated-loader-options) | অ্যাট্রিবিউট (internal) | lazy load-এ পৌঁছে দেওয়ার লোডার অপশন। |
| [`query`](#querycontext-query) | অ্যাট্রিবিউট (internal) | যে স্টেটমেন্ট চলছে। |
| [`refresh_state`](#querycontext-refresh-state) | অ্যাট্রিবিউট (internal) | `refresh()` বা expired লোড হলে কোন অবজেক্টের `InstanceState`, নইলে `None`। |
| [`requires_uniquing`](#querycontext-requires-uniquing) | প্রপার্টি (internal) | ফল unique করা লাগবে কি না (প্রপার্টি)। |
| [`runid`](#querycontext-runid) | অ্যাট্রিবিউট (internal) | এই লোড অপারেশনের নম্বর। |
| [`session`](#querycontext-session) | অ্যাট্রিবিউট | যে সেশনে লোড হচ্ছে। |
| [`top_level_context`](#querycontext-top-level-context) | অ্যাট্রিবিউট (internal) | nested লোডে সবচেয়ে বাইরের `QueryContext` (না থাকলে `None`)। |
| [`user_passed_query`](#querycontext-user-passed-query) | অ্যাট্রিবিউট (internal) | ব্যবহারকারী যে স্টেটমেন্ট দিয়েছিল (ORM বদলানোর আগে)। |
| [`version_check`](#querycontext-version-check) | অ্যাট্রিবিউট (internal) | `version_id_col`-এর মান মিলিয়ে দেখবে কি না। |
| [`yield_per`](#querycontext-yield-per) | অ্যাট্রিবিউট (internal) | `yield_per` মান বা `None`। |

### `QueryContext.attributes` { #querycontext-attributes }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোডারদের ভাগ করা কাজের dict।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(type(c.attributes).__name__))
session.get(User, 1); print(seen)   # ['dict']
```

### `QueryContext.autoflush` { #querycontext-autoflush }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কুয়েরির আগে autoflush চালু ছিল কি না।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.autoflush))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.bind_arguments` { #querycontext-bind-arguments }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ডেটাবেস বেছে নেওয়ার আর্গুমেন্ট।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append("mapper" in c.bind_arguments))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.compile_state` { #querycontext-compile-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইল হওয়া ORM স্টেটমেন্টের অবস্থা।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.compile_state is not None))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.create_eager_joins` { #querycontext-create-eager-joins }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ঘোষিত কিন্তু ব্যবহার না হওয়া slot (eager join-এর তালিকা আসলে compile state-এ থাকে)। `QueryContext`-এ পড়লে `AttributeError`।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(hasattr(c, "create_eager_joins")))
session.get(User, 1); print("create_eager_joins" in QueryContext.__slots__, seen)   # True [False]
```

### `QueryContext.default_load_options` { #querycontext-default-load-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোড-অপশনের ডিফল্ট মানের ক্লাস।

**উদাহরণ:**

```python
print(QueryContext.default_load_options._populate_existing)   # False
```

### `QueryContext.execution_options` { #querycontext-execution-options }

**ধরন:** অ্যাট্রিবিউট

`session.execute(..., execution_options={...})`-এ দেওয়া অপশন। **স্টেটমেন্টের** `.execution_options()` এখানে আসে না (সেগুলো `context.query`-এর সাথে থাকে)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.execution_options.get("my")))
session.execute(select(User).where(User.id == 1), execution_options={"my": "x"}).all()
print(seen)   # ['x']
```

### `QueryContext.identity_token` { #querycontext-identity-token }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

sharding-এর identity token।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.identity_token))
session.get(User, 1); print(seen)   # [None]
```

### `QueryContext.invoke_all_eagers` { #querycontext-invoke-all-eagers }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সব eager loader চালাবে কি না।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.invoke_all_eagers))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.load_options` { #querycontext-load-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোড-অপশন অবজেক্ট।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.load_options._populate_existing))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.loaders_require_buffering` { #querycontext-loaders-require-buffering }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোডারদের সব রো আগে বাফার করা দরকার কি না।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.loaders_require_buffering))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.loaders_require_uniquing` { #querycontext-loaders-require-uniquing }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফলের ডুপ্লিকেট বাদ দেওয়া দরকার কি না (joined eager loading-এ)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.loaders_require_uniquing))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.params` { #querycontext-params }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কুয়েরির প্যারামিটার।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.params))
session.execute(select(User).where(User.id == text(":i")), {"i": 1}).all()
print(seen)   # [{'i': 1}]
```

### `QueryContext.partials` { #querycontext-partials }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

আংশিকভাবে লোড হওয়া অবজেক্টের হিসাব।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(type(c.partials).__name__))
session.get(User, 1); print(seen)   # ['dict']
```

### `QueryContext.populate_existing` { #querycontext-populate-existing }

**ধরন:** অ্যাট্রিবিউট

সেশনে থাকা অবজেক্টও নতুন মানে ভরবে কি না।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.populate_existing))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.post_load_paths` { #querycontext-post-load-paths }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

লোড শেষে চলার কাজ (যেমন selectin লোড)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(type(c.post_load_paths).__name__))
session.get(User, 1); print(seen)   # ['dict']
```

### `QueryContext.propagated_loader_options` { #querycontext-propagated-loader-options }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

lazy load-এ পৌঁছে দেওয়ার লোডার অপশন।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.propagated_loader_options))
session.get(User, 1); print(seen)   # [()]
```

### `QueryContext.query` { #querycontext-query }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

যে স্টেটমেন্ট চলছে।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(type(c.query).__name__))
session.get(User, 1); print(seen)   # ['Select']
```

### `QueryContext.refresh_state` { #querycontext-refresh-state }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`refresh()` বা expired লোড হলে কোন অবজেক্টের `InstanceState`, নইলে `None`।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.refresh_state))
session.get(User, 1); print(seen)   # [None]
```

### `QueryContext.requires_uniquing` { #querycontext-requires-uniquing }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ফল unique করা লাগবে কি না (প্রপার্টি)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.requires_uniquing))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.runid` { #querycontext-runid }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই লোড অপারেশনের নম্বর।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(isinstance(c.runid, int)))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.session` { #querycontext-session }

**ধরন:** অ্যাট্রিবিউট

যে সেশনে লোড হচ্ছে।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.session is session))
session.get(User, 1); print(seen)   # [True]
```

### `QueryContext.top_level_context` { #querycontext-top-level-context }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

nested লোডে সবচেয়ে বাইরের `QueryContext` (না থাকলে `None`)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.top_level_context))
session.get(User, 1); print(seen)   # [None]
```

### `QueryContext.user_passed_query` { #querycontext-user-passed-query }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ব্যবহারকারী যে স্টেটমেন্ট দিয়েছিল (ORM বদলানোর আগে)।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(type(c.user_passed_query).__name__))
session.get(User, 1); print(seen)   # ['Select']
```

### `QueryContext.version_check` { #querycontext-version-check }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`version_id_col`-এর মান মিলিয়ে দেখবে কি না।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.version_check))
session.get(User, 1); print(seen)   # [False]
```

### `QueryContext.yield_per` { #querycontext-yield-per }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`yield_per` মান বা `None`।

**উদাহরণ:**

```python
seen = []
event.listen(User, "load", lambda t, c: seen.append(c.yield_per))
session.get(User, 1); print(seen)   # [None]
```

## `UOWTransaction` { #uowtransaction }

```python
from sqlalchemy.orm.unitofwork import UOWTransaction
```

(অভ্যন্তরীণ) একটি `flush()`-এর পুরো কাজের হিসাব: কোন অবজেক্ট INSERT/UPDATE/DELETE হবে, কোন ক্রমে। `SessionEvents.before_flush`, `after_flush`, `after_flush_postexec` ইভেন্টে `flush_context` হিসেবে আসে।

**উদাহরণ:**

```python
seen = []
@event.listens_for(session, "after_flush")
def af(sess, flush_context):
    seen.append((type(flush_context).__name__, flush_context.has_work))
session.get(User, 1).name = "নতুন"
session.flush()
print(seen)   # [('UOWTransaction', True)]
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #uowtransaction-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`execute()`](#uowtransaction-execute) | মেথড (internal) | flush-এর সব কাজ ক্রম অনুযায়ী চালায় (ORM নিজে ডাকে)। |
| [`filter_states_for_dep()`](#uowtransaction-filter-states-for-dep) | মেথড (internal) | একটি dependency processor-এর জন্য প্রাসঙ্গিক অবজেক্টগুলো বেছে নেয়। |
| [`finalize_flush_changes()`](#uowtransaction-finalize-flush-changes) | মেথড (internal) | সফল flush-এর পর অবজেক্টগুলোকে "পরিষ্কার"/"মোছা" হিসেবে চিহ্নিত করে। |
| [`get_attribute_history()`](#uowtransaction-get-attribute-history) | মেথড | flush-এর মাঝে একটি অবজেক্টের অ্যাট্রিবিউটের history (ক্যাশসহ)। |
| [`has_dep()`](#uowtransaction-has-dep) | মেথড (internal) | একটি dependency processor নথিভুক্ত কি না। |
| [`has_work`](#uowtransaction-has-work) | প্রপার্টি | flush-এ কোনো কাজ আছে কি না। |
| [`is_deleted()`](#uowtransaction-is-deleted) | মেথড | অবজেক্টটি এই flush-এ মোছা হচ্ছে কি না। |
| [`memo()`](#uowtransaction-memo) | মেথড (internal) | flush চলাকালীন একবার হিসাব করে মনে রাখার ক্যাশ। |
| [`register_object()`](#uowtransaction-register-object) | মেথড (internal) | একটি অবজেক্টকে flush-এর কাজে যোগ করে। |
| [`register_post_update()`](#uowtransaction-register-post-update) | মেথড (internal) | `post_update=True` relationship-এর পরের UPDATE নথিভুক্ত করে। |
| [`register_preprocessor()`](#uowtransaction-register-preprocessor) | মেথড (internal) | dependency processor নথিভুক্ত করে। |
| [`remove_state_actions()`](#uowtransaction-remove-state-actions) | মেথড (internal) | একটি অবজেক্টের বাকি কাজ সরায়। |
| [`states_for_mapper_hierarchy()`](#uowtransaction-states-for-mapper-hierarchy) | মেথড | একটি mapper (আর তার subclass-গুলো)র যে অবজেক্টগুলো এই flush-এ আছে। |
| [`was_already_deleted()`](#uowtransaction-was-already-deleted) | মেথড (internal) | expired অবজেক্টটি আগেই (অন্য কোথাও) মুছে গেছে কি না। |

### `UOWTransaction.execute()` { #uowtransaction-execute }

```python
UOWTransaction.execute()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

flush-এর সব কাজ ক্রম অনুযায়ী চালায় (ORM নিজে ডাকে)।

**উদাহরণ:**

```python
print(callable(UOWTransaction.execute))   # True
```

### `UOWTransaction.filter_states_for_dep()` { #uowtransaction-filter-states-for-dep }

```python
UOWTransaction.filter_states_for_dep(dep, states)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি dependency processor-এর জন্য প্রাসঙ্গিক অবজেক্টগুলো বেছে নেয়।

**উদাহরণ:**

```python
print(callable(UOWTransaction.filter_states_for_dep))   # True
```

### `UOWTransaction.finalize_flush_changes()` { #uowtransaction-finalize-flush-changes }

```python
UOWTransaction.finalize_flush_changes()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সফল flush-এর পর অবজেক্টগুলোকে "পরিষ্কার"/"মোছা" হিসেবে চিহ্নিত করে।

**উদাহরণ:**

```python
print(callable(UOWTransaction.finalize_flush_changes))   # True
```

### `UOWTransaction.get_attribute_history()` { #uowtransaction-get-attribute-history }

```python
UOWTransaction.get_attribute_history(state, key, passive=symbol('PASSIVE_NO_INITIALIZE'))
```

**ধরন:** মেথড

flush-এর মাঝে একটি অবজেক্টের অ্যাট্রিবিউটের history (ক্যাশসহ)। `before_flush`-এ অডিট হিসাবের জন্য কাজে লাগে।

**উদাহরণ:**

```python
seen = []
@event.listens_for(session, "after_flush")
def af(sess, ctx):
    for st in ctx.states_for_mapper_hierarchy(inspect(User), False, False):
        seen.append(ctx.get_attribute_history(st, "name").added)
session.get(User, 1).name = "নতুন"; session.flush()
print(seen)   # [['নতুন']]
```

### `UOWTransaction.has_dep()` { #uowtransaction-has-dep }

```python
UOWTransaction.has_dep(processor)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি dependency processor নথিভুক্ত কি না।

**উদাহরণ:**

```python
print(callable(UOWTransaction.has_dep))   # True
```

### `UOWTransaction.has_work` { #uowtransaction-has-work }

**ধরন:** প্রপার্টি

flush-এ কোনো কাজ আছে কি না।

**উদাহরণ:**

```python
seen = []
event.listen(session, "before_flush", lambda s, ctx, inst: seen.append(ctx.has_work))
session.add(User(name="নতুন")); session.flush()
print(seen)   # [False]  (before_flush-এ কাজের তালিকা এখনো তৈরি হয়নি)
```

### `UOWTransaction.is_deleted()` { #uowtransaction-is-deleted }

```python
UOWTransaction.is_deleted(state)
```

**ধরন:** মেথড

অবজেক্টটি এই flush-এ মোছা হচ্ছে কি না।

**উদাহরণ:**

```python
seen = []
@event.listens_for(session, "after_flush")
def af(sess, ctx):
    seen.append(ctx.is_deleted(inspect(u)))
u = session.get(User, 2); session.delete(u); session.flush()
print(seen)   # [True]
```

### `UOWTransaction.memo()` { #uowtransaction-memo }

```python
UOWTransaction.memo(key, callable_)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

flush চলাকালীন একবার হিসাব করে মনে রাখার ক্যাশ।

**উদাহরণ:**

```python
print(callable(UOWTransaction.memo))   # True
```

### `UOWTransaction.register_object()` { #uowtransaction-register-object }

```python
UOWTransaction.register_object(state, isdelete=False, listonly=False, cancel_delete=False, operation=None, prop=None)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টকে flush-এর কাজে যোগ করে।

**উদাহরণ:**

```python
print(callable(UOWTransaction.register_object))   # True
```

### `UOWTransaction.register_post_update()` { #uowtransaction-register-post-update }

```python
UOWTransaction.register_post_update(state, post_update_cols)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`post_update=True` relationship-এর পরের UPDATE নথিভুক্ত করে।

**উদাহরণ:**

```python
print(callable(UOWTransaction.register_post_update))   # True
```

### `UOWTransaction.register_preprocessor()` { #uowtransaction-register-preprocessor }

```python
UOWTransaction.register_preprocessor(processor, fromparent)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

dependency processor নথিভুক্ত করে।

**উদাহরণ:**

```python
print(callable(UOWTransaction.register_preprocessor))   # True
```

### `UOWTransaction.remove_state_actions()` { #uowtransaction-remove-state-actions }

```python
UOWTransaction.remove_state_actions(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি অবজেক্টের বাকি কাজ সরায়।

**উদাহরণ:**

```python
print(callable(UOWTransaction.remove_state_actions))   # True
```

### `UOWTransaction.states_for_mapper_hierarchy()` { #uowtransaction-states-for-mapper-hierarchy }

```python
UOWTransaction.states_for_mapper_hierarchy(mapper, isdelete, listonly)
```

**ধরন:** মেথড

একটি mapper (আর তার subclass-গুলো)র যে অবজেক্টগুলো এই flush-এ আছে।

**উদাহরণ:**

```python
seen = []
@event.listens_for(session, "after_flush")
def af(sess, ctx):
    seen.append(len(list(ctx.states_for_mapper_hierarchy(inspect(User), False, False))))
session.add_all([User(name="ক"), User(name="খ")]); session.flush()
print(seen)   # [2]
```

### `UOWTransaction.was_already_deleted()` { #uowtransaction-was-already-deleted }

```python
UOWTransaction.was_already_deleted(state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

expired অবজেক্টটি আগেই (অন্য কোথাও) মুছে গেছে কি না।

**উদাহরণ:**

```python
print(callable(UOWTransaction.was_already_deleted))   # True
```

## ধ্রুবক ও অপশন অবজেক্ট { #passiveflag-group }

## `PassiveFlag` { #passiveflag }

```python
from sqlalchemy.orm import PassiveFlag
```

লোডারকে বলার বিট-ফ্ল্যাগ: অ্যাট্রিবিউটের মান না থাকলে SQL চালানো যাবে কি না, খালি মান বসানো যাবে কি না ইত্যাদি। মূলত `get_history()` আর অ্যাট্রিবিউট-ইভেন্টের ভেতরের ব্যবহার। ফ্ল্যাগ `|` দিয়ে জোড়া যায়; নিচের `PASSIVE_*` তৈরি-করা জোড়া।

**উদাহরণ:**

```python
u = session.get(User, 1)
h = inspect(u).get_history("addresses", PassiveFlag.PASSIVE_NO_INITIALIZE)   # লোড করো না
print(h.unchanged, len(inspect(u).get_history("addresses", PassiveFlag.PASSIVE_OFF).unchanged))   # () 2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #passiveflag-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`CALLABLES_OK`](#passiveflag-CALLABLES-OK) | অ্যাট্রিবিউট | (১) মান না থাকলে লোডার ফাংশন চালানো যাবে। |
| [`DEFERRED_HISTORY_LOAD`](#passiveflag-DEFERRED-HISTORY-LOAD) | অ্যাট্রিবিউট | (২৫৬) অ্যাট্রিবিউটের আগের মানের বিশেষ লোড (`active_history`-এর জন্য)। |
| [`INCLUDE_PENDING_MUTATIONS`](#passiveflag-INCLUDE-PENDING-MUTATIONS) | অ্যাট্রিবিউট | (৫১২) এখনো প্রয়োগ না হওয়া collection বদলও হিসাবে ধরবে। |
| [`INIT_OK`](#passiveflag-INIT-OK) | অ্যাট্রিবিউট | (৮) অন্য কিছু না পেলে খালি মান (`None` বা খালি collection) বসানো যাবে। |
| [`LOAD_AGAINST_COMMITTED`](#passiveflag-LOAD-AGAINST-COMMITTED) | অ্যাট্রিবিউট | (৩২) লোডের সময় primary/foreign key-এর commit-হওয়া (আগের) মান ব্যবহার করবে। |
| [`NON_PERSISTENT_OK`](#passiveflag-NON-PERSISTENT-OK) | অ্যাট্রিবিউট | (১৬) অভিভাবক persistent না হলেও লোডার চালানো যাবে। |
| [`NO_AUTOFLUSH`](#passiveflag-NO-AUTOFLUSH) | অ্যাট্রিবিউট | (৬৪) লোডের সময় autoflush বন্ধ। |
| [`NO_CHANGE`](#passiveflag-NO-CHANGE) | অ্যাট্রিবিউট | (০) কিছুই চালাবে না, কিছুই বদলাবে না। |
| [`NO_RAISE`](#passiveflag-NO-RAISE) | অ্যাট্রিবিউট | (১২৮) লোডার কোনো assertion এরর তুলবে না (`merge()`-এ)। |
| [`PASSIVE_MERGE`](#passiveflag-PASSIVE-MERGE) | অ্যাট্রিবিউট | <code>PASSIVE_OFF &#124; NO_RAISE</code>: `session.merge()`-এর জন্য। |
| [`PASSIVE_NO_FETCH`](#passiveflag-PASSIVE-NO-FETCH) | অ্যাট্রিবিউট | `PASSIVE_OFF` থেকে `SQL_OK` বাদ: সব চলবে, শুধু SQL নয়। |
| [`PASSIVE_NO_FETCH_RELATED`](#passiveflag-PASSIVE-NO-FETCH-RELATED) | অ্যাট্রিবিউট | `PASSIVE_OFF` থেকে `RELATED_OBJECT_OK` বাদ: সম্পর্কিত অবজেক্ট লোড নয়। |
| [`PASSIVE_NO_INITIALIZE`](#passiveflag-PASSIVE-NO-INITIALIZE) | অ্যাট্রিবিউট | লোড বা খালি-মান কিছুই নয়: যা আছে শুধু তাই (না থাকলে `NO_VALUE`)। |
| [`PASSIVE_OFF`](#passiveflag-PASSIVE-OFF) | অ্যাট্রিবিউট | সব অনুমতি: দরকার হলে SQL চালিয়ে লোড করবে (সাধারণ অ্যাট্রিবিউট পড়ার আচরণ)। |
| [`PASSIVE_ONLY_PERSISTENT`](#passiveflag-PASSIVE-ONLY-PERSISTENT) | অ্যাট্রিবিউট | `PASSIVE_OFF` থেকে `NON_PERSISTENT_OK` বাদ: শুধু persistent অভিভাবকের জন্য লোড। |
| [`PASSIVE_RETURN_NO_VALUE`](#passiveflag-PASSIVE-RETURN-NO-VALUE) | অ্যাট্রিবিউট | `PASSIVE_OFF` থেকে `INIT_OK` বাদ: লোড করবে, কিন্তু খালি মান বসাবে না। |
| [`RELATED_OBJECT_OK`](#passiveflag-RELATED-OBJECT-OK) | অ্যাট্রিবিউট | (৪) সম্পর্কিত অবজেক্ট লোড করতেও SQL চালানো যাবে। |
| [`SQL_OK`](#passiveflag-SQL-OK) | অ্যাট্রিবিউট | (২) লোডার অন্তত সাধারণ কলামের জন্য SQL চালাতে পারবে। |

### `PassiveFlag.CALLABLES_OK` { #passiveflag-CALLABLES-OK }

**ধরন:** অ্যাট্রিবিউট

(১) মান না থাকলে লোডার ফাংশন চালানো যাবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.CALLABLES_OK))   # 1
```

### `PassiveFlag.DEFERRED_HISTORY_LOAD` { #passiveflag-DEFERRED-HISTORY-LOAD }

**ধরন:** অ্যাট্রিবিউট

(২৫৬) অ্যাট্রিবিউটের আগের মানের বিশেষ লোড (`active_history`-এর জন্য)।

**উদাহরণ:**

```python
print(int(PassiveFlag.DEFERRED_HISTORY_LOAD))   # 256
```

### `PassiveFlag.INCLUDE_PENDING_MUTATIONS` { #passiveflag-INCLUDE-PENDING-MUTATIONS }

**ধরন:** অ্যাট্রিবিউট

(৫১২) এখনো প্রয়োগ না হওয়া collection বদলও হিসাবে ধরবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.INCLUDE_PENDING_MUTATIONS))   # 512
```

### `PassiveFlag.INIT_OK` { #passiveflag-INIT-OK }

**ধরন:** অ্যাট্রিবিউট

(৮) অন্য কিছু না পেলে খালি মান (`None` বা খালি collection) বসানো যাবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.INIT_OK))   # 8
```

### `PassiveFlag.LOAD_AGAINST_COMMITTED` { #passiveflag-LOAD-AGAINST-COMMITTED }

**ধরন:** অ্যাট্রিবিউট

(৩২) লোডের সময় primary/foreign key-এর commit-হওয়া (আগের) মান ব্যবহার করবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.LOAD_AGAINST_COMMITTED))   # 32
```

### `PassiveFlag.NON_PERSISTENT_OK` { #passiveflag-NON-PERSISTENT-OK }

**ধরন:** অ্যাট্রিবিউট

(১৬) অভিভাবক persistent না হলেও লোডার চালানো যাবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.NON_PERSISTENT_OK))   # 16
```

### `PassiveFlag.NO_AUTOFLUSH` { #passiveflag-NO-AUTOFLUSH }

**ধরন:** অ্যাট্রিবিউট

(৬৪) লোডের সময় autoflush বন্ধ।

**উদাহরণ:**

```python
print(int(PassiveFlag.NO_AUTOFLUSH))   # 64
```

### `PassiveFlag.NO_CHANGE` { #passiveflag-NO-CHANGE }

**ধরন:** অ্যাট্রিবিউট

(০) কিছুই চালাবে না, কিছুই বদলাবে না।

**উদাহরণ:**

```python
print(int(PassiveFlag.NO_CHANGE))   # 0
```

### `PassiveFlag.NO_RAISE` { #passiveflag-NO-RAISE }

**ধরন:** অ্যাট্রিবিউট

(১২৮) লোডার কোনো assertion এরর তুলবে না (`merge()`-এ)।

**উদাহরণ:**

```python
print(int(PassiveFlag.NO_RAISE))   # 128
```

### `PassiveFlag.PASSIVE_MERGE` { #passiveflag-PASSIVE-MERGE }

**ধরন:** অ্যাট্রিবিউট

`PASSIVE_OFF | NO_RAISE`: `session.merge()`-এর জন্য।

**উদাহরণ:**

```python
print(PassiveFlag.PASSIVE_MERGE == PassiveFlag.PASSIVE_OFF | PassiveFlag.NO_RAISE)   # True
```

### `PassiveFlag.PASSIVE_NO_FETCH` { #passiveflag-PASSIVE-NO-FETCH }

**ধরন:** অ্যাট্রিবিউট

`PASSIVE_OFF` থেকে `SQL_OK` বাদ: সব চলবে, শুধু SQL নয়।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_NO_FETCH))   # 29
```

### `PassiveFlag.PASSIVE_NO_FETCH_RELATED` { #passiveflag-PASSIVE-NO-FETCH-RELATED }

**ধরন:** অ্যাট্রিবিউট

`PASSIVE_OFF` থেকে `RELATED_OBJECT_OK` বাদ: সম্পর্কিত অবজেক্ট লোড নয়।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_NO_FETCH_RELATED))   # 27
```

### `PassiveFlag.PASSIVE_NO_INITIALIZE` { #passiveflag-PASSIVE-NO-INITIALIZE }

**ধরন:** অ্যাট্রিবিউট

লোড বা খালি-মান কিছুই নয়: যা আছে শুধু তাই (না থাকলে `NO_VALUE`)।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_NO_INITIALIZE))   # 22
```

### `PassiveFlag.PASSIVE_OFF` { #passiveflag-PASSIVE-OFF }

**ধরন:** অ্যাট্রিবিউট

সব অনুমতি: দরকার হলে SQL চালিয়ে লোড করবে (সাধারণ অ্যাট্রিবিউট পড়ার আচরণ)।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_OFF))   # 31
```

### `PassiveFlag.PASSIVE_ONLY_PERSISTENT` { #passiveflag-PASSIVE-ONLY-PERSISTENT }

**ধরন:** অ্যাট্রিবিউট

`PASSIVE_OFF` থেকে `NON_PERSISTENT_OK` বাদ: শুধু persistent অভিভাবকের জন্য লোড।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_ONLY_PERSISTENT))   # 15
```

### `PassiveFlag.PASSIVE_RETURN_NO_VALUE` { #passiveflag-PASSIVE-RETURN-NO-VALUE }

**ধরন:** অ্যাট্রিবিউট

`PASSIVE_OFF` থেকে `INIT_OK` বাদ: লোড করবে, কিন্তু খালি মান বসাবে না।

**উদাহরণ:**

```python
print(int(PassiveFlag.PASSIVE_RETURN_NO_VALUE))   # 23
```

### `PassiveFlag.RELATED_OBJECT_OK` { #passiveflag-RELATED-OBJECT-OK }

**ধরন:** অ্যাট্রিবিউট

(৪) সম্পর্কিত অবজেক্ট লোড করতেও SQL চালানো যাবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.RELATED_OBJECT_OK))   # 4
```

### `PassiveFlag.SQL_OK` { #passiveflag-SQL-OK }

**ধরন:** অ্যাট্রিবিউট

(২) লোডার অন্তত সাধারণ কলামের জন্য SQL চালাতে পারবে।

**উদাহরণ:**

```python
print(int(PassiveFlag.SQL_OK))   # 2
```

## `LoaderCallableStatus` { #loadercallablestatus }

```python
from sqlalchemy.orm import LoaderCallableStatus
```

লোডার ফাংশন আর `loaded_value`-এর বিশেষ ফেরত-মান: "মান নেই", "লোড করা যায়নি" ইত্যাদি (Python-এর `None` থেকে আলাদা, কারণ `None` নিজেও একটি বৈধ মান)। `NEVER_SET` হলো `NO_VALUE`-এর আরেক নাম।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(inspect(u).attrs.addresses.loaded_value is LoaderCallableStatus.NO_VALUE)   # True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #loadercallablestatus-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`ATTR_EMPTY`](#loadercallablestatus-ATTR-EMPTY) | অ্যাট্রিবিউট | (৩) অ্যাট্রিবিউটে কোনো মান নেই। |
| [`ATTR_WAS_SET`](#loadercallablestatus-ATTR-WAS-SET) | অ্যাট্রিবিউট | (২) লোডার নিজেই মান বসিয়ে দিয়েছে, আর ফেরত দেওয়ার কিছু নেই। |
| [`DONT_SET`](#loadercallablestatus-DONT-SET) | অ্যাট্রিবিউট | (৫) মান বসানো উচিত নয়। |
| [`NO_VALUE`](#loadercallablestatus-NO-VALUE) | অ্যাট্রিবিউট | (৪) মান নেই বা কখনো বসানো হয়নি (`NEVER_SET`-ও এটাই)। |
| [`PASSIVE_CLASS_MISMATCH`](#loadercallablestatus-PASSIVE-CLASS-MISMATCH) | অ্যাট্রিবিউট | (১) প্রত্যাশিত ক্লাসের অবজেক্ট পাওয়া যায়নি (polymorphic লোডে)। |
| [`PASSIVE_NO_RESULT`](#loadercallablestatus-PASSIVE-NO-RESULT) | অ্যাট্রিবিউট | (০) PassiveFlag-এর কারণে লোড করা হয়নি, তাই ফল নেই। |

### `LoaderCallableStatus.ATTR_EMPTY` { #loadercallablestatus-ATTR-EMPTY }

**ধরন:** অ্যাট্রিবিউট

(৩) অ্যাট্রিবিউটে কোনো মান নেই।

**উদাহরণ:**

```python
print(LoaderCallableStatus.ATTR_EMPTY.value)   # 3
```

### `LoaderCallableStatus.ATTR_WAS_SET` { #loadercallablestatus-ATTR-WAS-SET }

**ধরন:** অ্যাট্রিবিউট

(২) লোডার নিজেই মান বসিয়ে দিয়েছে, আর ফেরত দেওয়ার কিছু নেই।

**উদাহরণ:**

```python
print(LoaderCallableStatus.ATTR_WAS_SET.value)   # 2
```

### `LoaderCallableStatus.DONT_SET` { #loadercallablestatus-DONT-SET }

**ধরন:** অ্যাট্রিবিউট

(৫) মান বসানো উচিত নয়।

**উদাহরণ:**

```python
print(LoaderCallableStatus.DONT_SET.value)   # 5
```

### `LoaderCallableStatus.NO_VALUE` { #loadercallablestatus-NO-VALUE }

**ধরন:** অ্যাট্রিবিউট

(৪) মান নেই বা কখনো বসানো হয়নি (`NEVER_SET`-ও এটাই)।

**উদাহরণ:**

```python
print(LoaderCallableStatus.NEVER_SET is LoaderCallableStatus.NO_VALUE)   # True
```

### `LoaderCallableStatus.PASSIVE_CLASS_MISMATCH` { #loadercallablestatus-PASSIVE-CLASS-MISMATCH }

**ধরন:** অ্যাট্রিবিউট

(১) প্রত্যাশিত ক্লাসের অবজেক্ট পাওয়া যায়নি (polymorphic লোডে)।

**উদাহরণ:**

```python
print(LoaderCallableStatus.PASSIVE_CLASS_MISMATCH.value)   # 1
```

### `LoaderCallableStatus.PASSIVE_NO_RESULT` { #loadercallablestatus-PASSIVE-NO-RESULT }

**ধরন:** অ্যাট্রিবিউট

(০) PassiveFlag-এর কারণে লোড করা হয়নি, তাই ফল নেই।

**উদাহরণ:**

```python
print(LoaderCallableStatus.PASSIVE_NO_RESULT.value)   # 0
```

## `SessionTransactionOrigin` { #sessiontransactionorigin }

```python
from sqlalchemy.orm import SessionTransactionOrigin
```

(২.০.২) একটি `SessionTransaction` কীভাবে শুরু হলো: `SessionTransaction.origin` অ্যাট্রিবিউটে থাকে। `after_transaction_create` ইভেন্টে "এটা কি নিজে থেকে শুরু (autobegin), নাকি `begin()`/`begin_nested()`" বুঝতে।

**উদাহরণ:**

```python
session.execute(select(User))
print(session.get_transaction().origin)   # SessionTransactionOrigin.AUTOBEGIN
nested = session.begin_nested()
print(nested.origin)   # SessionTransactionOrigin.BEGIN_NESTED
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #sessiontransactionorigin-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`AUTOBEGIN`](#sessiontransactionorigin-AUTOBEGIN) | অ্যাট্রিবিউট | প্রথম কাজ (কুয়েরি, `add()`)-এর সাথে নিজে থেকে শুরু। |
| [`BEGIN`](#sessiontransactionorigin-BEGIN) | অ্যাট্রিবিউট | `session.begin()` দিয়ে স্পষ্টভাবে শুরু। |
| [`BEGIN_NESTED`](#sessiontransactionorigin-BEGIN-NESTED) | অ্যাট্রিবিউট | `session.begin_nested()` (SAVEPOINT)। |
| [`SUBTRANSACTION`](#sessiontransactionorigin-SUBTRANSACTION) | অ্যাট্রিবিউট | ভেতরের ব্যবহার: একটি চলমান transaction-এর ভেতরে তৈরি "উপ-transaction" (flush ইত্যাদিতে)। |

### `SessionTransactionOrigin.AUTOBEGIN` { #sessiontransactionorigin-AUTOBEGIN }

**ধরন:** অ্যাট্রিবিউট

প্রথম কাজ (কুয়েরি, `add()`)-এর সাথে নিজে থেকে শুরু।

**উদাহরণ:**

```python
session.add(User(name="x"))
print(session.get_transaction().origin.name)   # AUTOBEGIN
```

### `SessionTransactionOrigin.BEGIN` { #sessiontransactionorigin-BEGIN }

**ধরন:** অ্যাট্রিবিউট

`session.begin()` দিয়ে স্পষ্টভাবে শুরু।

**উদাহরণ:**

```python
t = session.begin()
print(t.origin.name)   # BEGIN
```

### `SessionTransactionOrigin.BEGIN_NESTED` { #sessiontransactionorigin-BEGIN-NESTED }

**ধরন:** অ্যাট্রিবিউট

`session.begin_nested()` (SAVEPOINT)।

**উদাহরণ:**

```python
print(session.begin_nested().origin.name)   # BEGIN_NESTED
```

### `SessionTransactionOrigin.SUBTRANSACTION` { #sessiontransactionorigin-SUBTRANSACTION }

**ধরন:** অ্যাট্রিবিউট

ভেতরের ব্যবহার: একটি চলমান transaction-এর ভেতরে তৈরি "উপ-transaction" (flush ইত্যাদিতে)।

**উদাহরণ:**

```python
print(SessionTransactionOrigin.SUBTRANSACTION.value)   # 3
```

## `LoaderCriteriaOption` { #loadercriteriaoption }

```python
from sqlalchemy.orm import LoaderCriteriaOption
```

[`with_loader_criteria()`](loading.md#with-loader-criteria) যে অপশন অবজেক্ট দেয়: একটি entity যেখানেই লোড হোক (মূল কুয়েরি, join, lazy load), সব জায়গায় বাড়তি WHERE শর্ত বসায়। multi-tenant অ্যাপ বা "soft delete" লুকানোর জন্য, সাধারণত `do_orm_execute` হুকে।

**উদাহরণ:**

```python
opt = with_loader_criteria(User, User.name != "করিম")
print(type(opt).__name__, [u.name for u in session.scalars(select(User).options(opt))])   # LoaderCriteriaOption ['রহিম']
```

### কনস্ট্রাক্টরের প্যারামিটার { #loadercriteriaoption-params }

```python
LoaderCriteriaOption(entity_or_base, where_criteria, loader_only=False, include_aliases=False, propagate_to_loaders=True, track_closure_variables=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `entity_or_base` | যে মডেল (বা মূল ক্লাস/মিক্সিন, তখন সব subclass-এ) শর্ত পাবে। |
| `where_criteria` | শর্ত: এক্সপ্রেশন, বা `lambda cls: cls.deleted == False` (মিক্সিনের জন্য)। |
| `loader_only` | `True` হলে শুধু লোডে (UPDATE/DELETE-এ নয়)। |
| `include_aliases` | `True` হলে `aliased()` রূপেও শর্ত বসবে। |
| `propagate_to_loaders` | lazy load ইত্যাদিতেও যাবে কি না (ডিফল্ট `True`)। |
| `track_closure_variables` | lambda-র বাইরের ভেরিয়েবল ক্যাশ-কী-তে ধরবে কি না। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #loadercriteriaoption-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`deferred_where_criteria`](#loadercriteriaoption-deferred-where-criteria) | অ্যাট্রিবিউট (internal) | শর্তটি lambda হলে `True` (প্রতিটি entity-র জন্য পরে বানানো হয়)। |
| [`entity`](#loadercriteriaoption-entity) | অ্যাট্রিবিউট (internal) | নির্দিষ্ট entity হলে তার inspect রূপ (মূল ক্লাস/মিক্সিন হলে `None`)। |
| [`get_children()`](#loadercriteriaoption-get-children) | মেথড (internal) | traversal-এর অংশ। |
| [`get_global_criteria()`](#loadercriteriaoption-get-global-criteria) | মেথড (internal) | কম্পাইলের সময় শর্তটি বৈশ্বিক শর্ত-তালিকায় যোগ করে। |
| [`include_aliases`](#loadercriteriaoption-include-aliases) | অ্যাট্রিবিউট | aliased রূপেও প্রয়োগ হবে কি না। |
| [`inherit_cache`](#loadercriteriaoption-inherit-cache) | অ্যাট্রিবিউট (internal) | SQL ক্যাশ-কী-সংক্রান্ত পতাকা। |
| [`process_compile_state()`](#loadercriteriaoption-process-compile-state) | মেথড (internal) | কম্পাইলের সময় শর্ত প্রয়োগের hook। |
| [`process_compile_state_replaced_entities()`](#loadercriteriaoption-process-compile-state-replaced-entities) | মেথড (internal) | entity বদলানো কুয়েরির জন্য একই hook। |
| [`propagate_to_loaders`](#loadercriteriaoption-propagate-to-loaders) | অ্যাট্রিবিউট | lazy load-এও যাবে কি না। |
| [`root_entity`](#loadercriteriaoption-root-entity) | অ্যাট্রিবিউট (internal) | মূল ক্লাস/মিক্সিন দিলে সেটি, নির্দিষ্ট entity হলে `None`। |
| [`where_criteria`](#loadercriteriaoption-where-criteria) | অ্যাট্রিবিউট | শর্তটি (এক্সপ্রেশন বা lambda-র ভেতরের রূপ)। |

### `LoaderCriteriaOption.deferred_where_criteria` { #loadercriteriaoption-deferred-where-criteria }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

শর্তটি lambda হলে `True` (প্রতিটি entity-র জন্য পরে বানানো হয়)।

**উদাহরণ:**

```python
print(with_loader_criteria(User, lambda cls: cls.id > 0).deferred_where_criteria)   # True
```

### `LoaderCriteriaOption.entity` { #loadercriteriaoption-entity }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

নির্দিষ্ট entity হলে তার inspect রূপ (মূল ক্লাস/মিক্সিন হলে `None`)।

**উদাহরণ:**

```python
print(with_loader_criteria(User, User.id > 0).entity)   # Mapper[User(users)]
```

### `LoaderCriteriaOption.get_children()` { #loadercriteriaoption-get-children }

```python
LoaderCriteriaOption.get_children(*, omit_attrs=(), **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

traversal-এর অংশ।

**উদাহরণ:**

```python
print(type(list(with_loader_criteria(User, User.id > 0).get_children())).__name__)   # list
```

### `LoaderCriteriaOption.get_global_criteria()` { #loadercriteriaoption-get-global-criteria }

```python
LoaderCriteriaOption.get_global_criteria(attributes)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় শর্তটি বৈশ্বিক শর্ত-তালিকায় যোগ করে।

**উদাহরণ:**

```python
print(callable(LoaderCriteriaOption.get_global_criteria))   # True
```

### `LoaderCriteriaOption.include_aliases` { #loadercriteriaoption-include-aliases }

**ধরন:** অ্যাট্রিবিউট

aliased রূপেও প্রয়োগ হবে কি না।

**উদাহরণ:**

```python
print(with_loader_criteria(User, User.id > 0, include_aliases=True).include_aliases)   # True
```

### `LoaderCriteriaOption.inherit_cache` { #loadercriteriaoption-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

SQL ক্যাশ-কী-সংক্রান্ত পতাকা।

**উদাহরণ:**

```python
print(LoaderCriteriaOption.inherit_cache)   # None
```

### `LoaderCriteriaOption.process_compile_state()` { #loadercriteriaoption-process-compile-state }

```python
LoaderCriteriaOption.process_compile_state(compile_state)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কম্পাইলের সময় শর্ত প্রয়োগের hook।

**উদাহরণ:**

```python
print(callable(LoaderCriteriaOption.process_compile_state))   # True
```

### `LoaderCriteriaOption.process_compile_state_replaced_entities()` { #loadercriteriaoption-process-compile-state-replaced-entities }

```python
LoaderCriteriaOption.process_compile_state_replaced_entities(compile_state, mapper_entities)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

entity বদলানো কুয়েরির জন্য একই hook।

**উদাহরণ:**

```python
print(callable(LoaderCriteriaOption.process_compile_state_replaced_entities))   # True
```

### `LoaderCriteriaOption.propagate_to_loaders` { #loadercriteriaoption-propagate-to-loaders }

**ধরন:** অ্যাট্রিবিউট

lazy load-এও যাবে কি না।

**উদাহরণ:**

```python
print(with_loader_criteria(User, User.id > 0).propagate_to_loaders)   # True
```

### `LoaderCriteriaOption.root_entity` { #loadercriteriaoption-root-entity }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

মূল ক্লাস/মিক্সিন দিলে সেটি, নির্দিষ্ট entity হলে `None`।

**উদাহরণ:**

```python
print(with_loader_criteria(Base, lambda cls: True).root_entity is Base)   # True
```

### `LoaderCriteriaOption.where_criteria` { #loadercriteriaoption-where-criteria }

**ধরন:** অ্যাট্রিবিউট

শর্তটি (এক্সপ্রেশন বা lambda-র ভেতরের রূপ)।

**উদাহরণ:**

```python
print(with_loader_criteria(User, User.id > 0).where_criteria)   # users.id > :id_1
```
