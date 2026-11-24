# Association Proxy API: সম্পর্ক পেরিয়ে সরাসরি অ্যাট্রিবিউট { #api-association-proxy }

/// note | এই পেজে যা আছে

* `association_proxy()`-এর **প্রতিটি** প্যারামিটার।
* `AssociationProxy`, `AssociationProxyInstance` আর তার রূপ (`ObjectAssociationProxyInstance`, `ColumnAssociationProxyInstance`, `AmbiguousAssociationProxyInstance`, `AliasedAssociationProxyInstance`), `AssociationProxyExtensionType`।

///

রিলেশনশিপের ভেতরের একটি অ্যাট্রিবিউটকে সরাসরি দেখায়। যেমন ইউজার আর কিওয়ার্ডের মাঝে একটি association অবজেক্ট (`UserKeyword`) থাকলে প্রতিবার `[uk.keyword.word for uk in user.user_keywords]` না লিখে শুধু `user.keywords` লেখা যায়, আর `user.keywords.append("python")` লিখলে মাঝের অবজেক্ট নিজে থেকে তৈরি হয়। many-to-many-এর association object প্যাটার্ন দেখুন [Relationship অধ্যায়ে](../relationships.md#s13)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    user_keywords: Mapped[list["UserKeyword"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # user.keywords → ['python', 'sql']; append("x") দিলে নতুন UserKeyword + Keyword তৈরি
    keywords: AssociationProxy[list[str]] = association_proxy(
        "user_keywords", "word", creator=lambda w: UserKeyword(keyword=Keyword(word=w)))

class UserKeyword(Base):      # user_id, keyword_id, level ("expert"/"beginner"), user, keyword
    word: AssociationProxy[str] = association_proxy("keyword", "word")
    ...

class Keyword(Base):          # id, word
    ...

class Address(Base):          # id, city, user_id, user
    user_name: AssociationProxy[str] = association_proxy("user", "name")
```

ডেটা: রহিম (কিওয়ার্ড: python expert, sql beginner; ঠিকানা ঢাকা), করিম (কিওয়ার্ড: sql expert)। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `association_proxy()` { #association-proxy }

```python
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
```

```python
association_proxy(target_collection, attr, *, creator=None, getset_factory=None, proxy_factory=None, proxy_bulk_set=None, info=None, cascade_scalar_deletes=False, create_on_none_assignment=False, init=_NoArg.NO_ARG, repr=_NoArg.NO_ARG, default=_NoArg.NO_ARG, default_factory=_NoArg.NO_ARG, compare=_NoArg.NO_ARG, kw_only=_NoArg.NO_ARG, hash=_NoArg.NO_ARG, dataclass_metadata=_NoArg.NO_ARG)
```

**ধরন:** ফাংশন

একটি association proxy অ্যাট্রিবিউট বানায়: `association_proxy("রিলেশনশিপের নাম", "লক্ষ্য অ্যাট্রিবিউট")`। কালেকশন রিলেশনশিপে একটি "list-এর মতো" অবজেক্ট দেয় (পড়া, যোগ, বাদ সবই চলে), একক রিলেশনশিপে সরাসরি মান। টাইপ হিন্ট: `AssociationProxy[list[str]]`। কুয়েরিতেও ব্যবহার করা যায়: `User.keywords.any(...)`, `Address.user_name == "..."`।

**উদাহরণ:**

```python
rahim = session.scalars(select(User).where(User.name == "রহিম")).one()
print(list(rahim.keywords))                  # ['python', 'sql']
rahim.keywords.append("fastapi")             # নতুন UserKeyword + Keyword নিজে থেকে
session.commit()
print(session.scalar(select(Keyword.word).where(Keyword.word == "fastapi")))   # fastapi
print(session.scalars(select(User.name).where(User.keywords.any(Keyword.word == "sql")).order_by(User.id)).all())
# ['রহিম', 'করিম']
```

### `association_proxy()`-এর সব প্যারামিটার { #association-proxy-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target_collection` | এই ক্লাসের যে রিলেশনশিপের ভেতর দিয়ে যাওয়া হবে। |
| `attr` | লক্ষ্য অবজেক্টের যে অ্যাট্রিবিউট দেখানো হবে (নিজেও আরেকটি proxy হতে পারে, যেমন এখানে `UserKeyword.word`)। |
| `creator` | নতুন মান যোগ করলে মাঝের অবজেক্ট বানানোর ফাংশন: `creator(value)` (dict কালেকশনে `creator(key, value)`)। না দিলে লক্ষ্য ক্লাসকে একটি পজিশনাল আর্গুমেন্টে ডাকে। |
| `getset_factory` | মান পড়া/বসানোর নিজের ফাংশন-জোড়া বানানোর factory (উন্নত ব্যবহার)। |
| `proxy_factory` | কালেকশনের জন্য নিজের proxy-কালেকশন ক্লাস। |
| `proxy_bulk_set` | `proxy_factory`-এর সাথে: পুরো কালেকশন একসাথে বসানোর ফাংশন। |
| `info` | নিজের মেটাডেটার dict (`AssociationProxy.info`)। |
| `cascade_scalar_deletes` | (২.০.১৮) একক proxy-তে `None` বসালে বা `del` করলে মাঝের অবজেক্টটিও মুছে ফেলবে কি না। |
| `create_on_none_assignment` | (২.০.১৮) একক proxy-তে `None` বসালেও মাঝের অবজেক্ট (না থাকলে) তৈরি করবে কি না। |
| `init` | (dataclass মডেলে) `__init__`-এ থাকবে কি না। |
| `repr` | (dataclass) `__repr__`-এ থাকবে কি না। |
| `default` | (dataclass) ডিফল্ট মান। |
| `default_factory` | (dataclass) ডিফল্ট-বানানো ফাংশন। |
| `compare` | (dataclass) `__eq__`-এ থাকবে কি না। |
| `kw_only` | (dataclass) শুধু keyword আর্গুমেন্ট। |
| `hash` | (২.০.৩৬, dataclass) `__hash__`-এ থাকবে কি না। |
| `dataclass_metadata` | (২.০.৪২, dataclass) dataclass field-এর metadata। |

**একক (scalar) রিলেশনশিপের proxy**

```python
a = session.scalars(select(Address)).one()
print(a.user_name)                                                        # রহিম
print(session.scalars(select(Address.city).where(Address.user_name == "রহিম")).all())   # ['ঢাকা']
```

## `AssociationProxy` { #associationproxy }

```python
from sqlalchemy.ext.associationproxy import AssociationProxy
```

`association_proxy()` যে descriptor বানায়: ক্লাসে থাকে। ক্লাস দিয়ে পড়লে (`User.keywords`) একটি `AssociationProxyInstance` পাওয়া যায় (কুয়েরির জন্য), অবজেক্ট দিয়ে পড়লে আসল মান/কালেকশন।

**উদাহরণ:**

```python
desc = inspect(User).all_orm_descriptors["keywords"]
print(type(desc).__name__, type(User.keywords).__name__)   # AssociationProxy ObjectAssociationProxyInstance
# (লক্ষ্য `UserKeyword.word` নিজেই আরেকটি proxy, কলাম নয়; তাই Object…; `Address.user_name`-এ Column…)
```

### কনস্ট্রাক্টরের প্যারামিটার { #associationproxy-params }

```python
AssociationProxy(target_collection, attr, *, creator=None, getset_factory=None, proxy_factory=None, proxy_bulk_set=None, info=None, cascade_scalar_deletes=False, create_on_none_assignment=False, attribute_options=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `target_collection` | রিলেশনশিপের নাম। |
| `attr` | লক্ষ্য অ্যাট্রিবিউট। |
| `creator` | মাঝের অবজেক্ট বানানোর ফাংশন। |
| `getset_factory` | get/set ফাংশন factory। |
| `proxy_factory` | proxy-কালেকশন ক্লাস। |
| `proxy_bulk_set` | পুরো কালেকশন বসানোর ফাংশন। |
| `info` | মেটাডেটার dict। |
| `cascade_scalar_deletes` | একক proxy-তে None দিলে মাঝের অবজেক্ট মোছা। |
| `create_on_none_assignment` | None দিলেও মাঝের অবজেক্ট তৈরি। |
| `attribute_options` | (ভেতরের) dataclass অপশনগুলোর গুচ্ছ। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #associationproxy-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`extension_type`](#associationproxy-extension-type) | অ্যাট্রিবিউট | inspection-এ ধরন: `AssociationProxyExtensionType.ASSOCIATION_PROXY`। |
| [`for_class()`](#associationproxy-for-class) | মেথড | একটি নির্দিষ্ট ক্লাসের (বা সাবক্লাসের) জন্য `AssociationProxyInstance` দেয় (`User.keywords` লেখার সমান)। |
| [`info`](#associationproxy-info) | প্রপার্টি | নিজের মেটাডেটার dict। |
| [`is_aliased_class`](#associationproxy-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_attribute`](#associationproxy-is-attribute) | অ্যাট্রিবিউট | inspection-এ অ্যাট্রিবিউট (`True`)। |
| [`is_bundle`](#associationproxy-is-bundle) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_clause_element`](#associationproxy-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_instance`](#associationproxy-is-instance) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_mapper`](#associationproxy-is-mapper) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_property`](#associationproxy-is-property) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_selectable`](#associationproxy-is-selectable) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |

### `AssociationProxy.extension_type` { #associationproxy-extension-type }

**ধরন:** অ্যাট্রিবিউট

inspection-এ ধরন: `AssociationProxyExtensionType.ASSOCIATION_PROXY`।

**উদাহরণ:**

```python
print(inspect(User).all_orm_descriptors["keywords"].extension_type.name)   # ASSOCIATION_PROXY
```

### `AssociationProxy.for_class()` { #associationproxy-for-class }

```python
AssociationProxy.for_class(class_, obj=None)
```

**ধরন:** মেথড

একটি নির্দিষ্ট ক্লাসের (বা সাবক্লাসের) জন্য `AssociationProxyInstance` দেয় (`User.keywords` লেখার সমান)।

**উদাহরণ:**

```python
ap = inspect(User).all_orm_descriptors["keywords"]
print(type(ap.for_class(User)).__name__)   # ObjectAssociationProxyInstance
```

### `AssociationProxy.info` { #associationproxy-info }

**ধরন:** প্রপার্টি

নিজের মেটাডেটার dict।

**উদাহরণ:**

```python
print(inspect(User).all_orm_descriptors["keywords"].info)   # {}
```

### `AssociationProxy.is_aliased_class` { #associationproxy-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_attribute` { #associationproxy-is-attribute }

**ধরন:** অ্যাট্রিবিউট

inspection-এ অ্যাট্রিবিউট (`True`)।

**উদাহরণ:**

```python
print(inspect(User).all_orm_descriptors["keywords"].is_attribute)   # True
```

### `AssociationProxy.is_bundle` { #associationproxy-is-bundle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_clause_element` { #associationproxy-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_instance` { #associationproxy-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_mapper` { #associationproxy-is-mapper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_property` { #associationproxy-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `AssociationProxy.is_selectable` { #associationproxy-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

## `AssociationProxyInstance` { #associationproxyinstance }

```python
from sqlalchemy.ext.associationproxy import AssociationProxyInstance
```

ক্লাস-স্তরের proxy (`User.keywords`): কুয়েরি বানানোর অবজেক্ট। লক্ষ্য অ্যাট্রিবিউট কলাম হলে `ColumnAssociationProxyInstance`, অবজেক্ট (রিলেশনশিপ) হলে `ObjectAssociationProxyInstance`। কলামের তুলনা-অপারেটরগুলো (`==`, `like()` …) `EXISTS` সাবকুয়েরিতে অনুবাদ হয়।

**উদাহরণ:**

```python
print(isinstance(User.keywords, AssociationProxyInstance))                               # True
print(session.scalars(select(User.name).where(User.keywords.contains("python"))).all())  # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #associationproxyinstance-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`any()`](#associationproxyinstance-any) | মেথড | কালেকশন proxy-তে: অন্তত একটি লক্ষ্য শর্ত মানে → `EXISTS`। |
| [`attr`](#associationproxyinstance-attr) | প্রপার্টি | `(local_attr, remote_attr)` জোড়া; JOIN করতে কাজে লাগে। |
| [`delete()`](#associationproxyinstance-delete) | মেথড (internal) | অবজেক্টে `del obj.proxy` চালানোর ভেতরের মেথড। |
| [`for_proxy()`](#associationproxyinstance-for-proxy) | ক্লাস মেথড (internal) | (ক্লাস মেথড) একটি `AssociationProxy` থেকে সঠিক ধরনের instance বানানোর ফ্যাক্টরি। |
| [`get()`](#associationproxyinstance-get) | মেথড | একটি অবজেক্ট থেকে proxy-র মান পড়ে (`obj.proxy`-এর মতো)। |
| [`has()`](#associationproxyinstance-has) | মেথড | একক proxy-তে: লক্ষ্য অবজেক্ট শর্ত মানে → `EXISTS`। |
| [`info`](#associationproxyinstance-info) | প্রপার্টি | মূল `AssociationProxy`-এর info dict। |
| [`local_attr`](#associationproxyinstance-local-attr) | প্রপার্টি | এই ক্লাসের যে রিলেশনশিপ দিয়ে যাওয়া হয়। |
| [`remote_attr`](#associationproxyinstance-remote-attr) | প্রপার্টি | লক্ষ্য ক্লাসের যে অ্যাট্রিবিউট দেখানো হয়। |
| [`scalar`](#associationproxyinstance-scalar) | প্রপার্টি | একক (many-to-one) রিলেশনশিপের proxy কি না। |
| [`set()`](#associationproxyinstance-set) | মেথড (internal) | অবজেক্টে proxy-র মান বসানোর ভেতরের মেথড (`obj.proxy = value`)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AssociationProxyInstance`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

### `AssociationProxyInstance.any()` { #associationproxyinstance-any }

```python
AssociationProxyInstance.any(criterion=None, **kwargs)
```

**ধরন:** মেথড

কালেকশন proxy-তে: অন্তত একটি লক্ষ্য শর্ত মানে → `EXISTS`। শর্ত লক্ষ্যের ক্লাসে লিখুন।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).where(User.keywords.any(Keyword.word.like("py%")))).all())   # ['রহিম']
```

### `AssociationProxyInstance.attr` { #associationproxyinstance-attr }

**ধরন:** প্রপার্টি

`(local_attr, remote_attr)` জোড়া; JOIN করতে কাজে লাগে।

**উদাহরণ:**

```python
local, remote = Address.user_name.attr
print(local, remote)   # Address.user User.name
```

### `AssociationProxyInstance.delete()` { #associationproxyinstance-delete }

```python
AssociationProxyInstance.delete(obj)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টে `del obj.proxy` চালানোর ভেতরের মেথড।

### `AssociationProxyInstance.for_proxy()` { #associationproxyinstance-for-proxy }

```python
AssociationProxyInstance.for_proxy(parent, owning_class, parent_instance)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) একটি `AssociationProxy` থেকে সঠিক ধরনের instance বানানোর ফ্যাক্টরি।

### `AssociationProxyInstance.get()` { #associationproxyinstance-get }

```python
AssociationProxyInstance.get(obj)
```

**ধরন:** মেথড

একটি অবজেক্ট থেকে proxy-র মান পড়ে (`obj.proxy`-এর মতো)।

**উদাহরণ:**

```python
a = session.scalars(select(Address)).one()
print(Address.user_name.get(a))   # রহিম
```

### `AssociationProxyInstance.has()` { #associationproxyinstance-has }

```python
AssociationProxyInstance.has(criterion=None, **kwargs)
```

**ধরন:** মেথড

একক proxy-তে: লক্ষ্য অবজেক্ট শর্ত মানে → `EXISTS`।

**উদাহরণ:**

```python
print(session.scalars(select(Address.city).where(Address.user_name.has())).all())   # ['ঢাকা']
```

### `AssociationProxyInstance.info` { #associationproxyinstance-info }

**ধরন:** প্রপার্টি

মূল `AssociationProxy`-এর info dict।

**উদাহরণ:**

```python
print(User.keywords.info)   # {}
```

### `AssociationProxyInstance.local_attr` { #associationproxyinstance-local-attr }

**ধরন:** প্রপার্টি

এই ক্লাসের যে রিলেশনশিপ দিয়ে যাওয়া হয়।

**উদাহরণ:**

```python
print(User.keywords.local_attr)   # User.user_keywords
```

### `AssociationProxyInstance.remote_attr` { #associationproxyinstance-remote-attr }

**ধরন:** প্রপার্টি

লক্ষ্য ক্লাসের যে অ্যাট্রিবিউট দেখানো হয়।

**উদাহরণ:**

```python
print(Address.user_name.remote_attr)   # User.name
```

### `AssociationProxyInstance.scalar` { #associationproxyinstance-scalar }

**ধরন:** প্রপার্টি

একক (many-to-one) রিলেশনশিপের proxy কি না।

**উদাহরণ:**

```python
print(Address.user_name.scalar, User.keywords.scalar)   # True False
```

### `AssociationProxyInstance.set()` { #associationproxyinstance-set }

```python
AssociationProxyInstance.set(obj, values)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টে proxy-র মান বসানোর ভেতরের মেথড (`obj.proxy = value`)।

## `ColumnAssociationProxyInstance` { #columnassociationproxyinstance }

```python
from sqlalchemy.ext.associationproxy import ColumnAssociationProxyInstance
```

লক্ষ্য একটি **কলাম** হলে (`Address.user_name` → `User.name`)। তুলনা (`==`, `like()`, `in_()`) `EXISTS` বা JOIN-এর মাধ্যমে কাজ করে।

**উদাহরণ:**

```python
print(type(Address.user_name).__name__)                                    # ColumnAssociationProxyInstance
print(session.scalars(select(Address.city).where(Address.user_name.like("র%"))).all())   # ['ঢাকা']
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AssociationProxyInstance`](#associationproxyinstance-summary)-এর মতো।

## `ObjectAssociationProxyInstance` { #objectassociationproxyinstance }

```python
from sqlalchemy.ext.associationproxy import ObjectAssociationProxyInstance
```

লক্ষ্য একটি **অবজেক্ট** (রিলেশনশিপ) হলে। `contains(obj)` ও `==` অবজেক্ট দিয়ে তুলনা করে।

**উদাহরণ:**

```python
User.kw_objs = association_proxy("user_keywords", "keyword")
py = session.scalars(select(Keyword).where(Keyword.word == "python")).one()
print(type(User.kw_objs).__name__)                                          # ObjectAssociationProxyInstance
print(session.scalars(select(User.name).where(User.kw_objs.contains(py))).all())   # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #objectassociationproxyinstance-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_to_entity()`](#objectassociationproxyinstance-adapt-to-entity) | মেথড (internal) | `aliased()` এন্টিটির জন্য proxy মানিয়ে নেয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ObjectAssociationProxyInstance`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`AssociationProxyInstance` থেকে:** [`any()`](#associationproxyinstance-any) · [`attr`](#associationproxyinstance-attr) · [`delete()`](#associationproxyinstance-delete) · [`for_proxy()`](#associationproxyinstance-for-proxy) · [`get()`](#associationproxyinstance-get) · [`has()`](#associationproxyinstance-has) · [`info`](#associationproxyinstance-info) · [`local_attr`](#associationproxyinstance-local-attr) · [`remote_attr`](#associationproxyinstance-remote-attr) · [`scalar`](#associationproxyinstance-scalar) · [`set()`](#associationproxyinstance-set)

///

### `ObjectAssociationProxyInstance.adapt_to_entity()` { #objectassociationproxyinstance-adapt-to-entity }

```python
ObjectAssociationProxyInstance.adapt_to_entity(aliased_insp)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`aliased()` এন্টিটির জন্য proxy মানিয়ে নেয়।

## `AmbiguousAssociationProxyInstance` { #ambiguousassociationproxyinstance }

```python
from sqlalchemy.ext.associationproxy import AmbiguousAssociationProxyInstance
```

লক্ষ্য অ্যাট্রিবিউট inheritance-এর কারণে সাবক্লাস-ভেদে ভিন্ন হলে (কোনটা বোঝানো হচ্ছে নিশ্চিত নয়)। এমন proxy দিয়ে কুয়েরি করলে এরর দেয়; অবজেক্ট-স্তরে কাজ করে।

**উদাহরণ:**

```python
print(issubclass(AmbiguousAssociationProxyInstance, AssociationProxyInstance))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AssociationProxyInstance`](#associationproxyinstance-summary)-এর মতো।

## `AliasedAssociationProxyInstance` { #aliasedassociationproxyinstance }

```python
from sqlalchemy.ext.associationproxy import AliasedAssociationProxyInstance
```

`aliased(User).keywords`-এর মতো alias করা ক্লাসের proxy।

**উদাহরণ:**

```python
ua = aliased(User)
print(type(ua.keywords).__name__)   # AliasedAssociationProxyInstance
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #aliasedassociationproxyinstance-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_to_entity()`](#aliasedassociationproxyinstance-adapt-to-entity) | মেথড (internal) | alias এন্টিটির জন্য মানিয়ে নেয়। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AliasedAssociationProxyInstance`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`AssociationProxyInstance` থেকে:** [`any()`](#associationproxyinstance-any) · [`attr`](#associationproxyinstance-attr) · [`delete()`](#associationproxyinstance-delete) · [`for_proxy()`](#associationproxyinstance-for-proxy) · [`get()`](#associationproxyinstance-get) · [`has()`](#associationproxyinstance-has) · [`info`](#associationproxyinstance-info) · [`local_attr`](#associationproxyinstance-local-attr) · [`remote_attr`](#associationproxyinstance-remote-attr) · [`scalar`](#associationproxyinstance-scalar) · [`set()`](#associationproxyinstance-set)

///

### `AliasedAssociationProxyInstance.adapt_to_entity()` { #aliasedassociationproxyinstance-adapt-to-entity }

```python
AliasedAssociationProxyInstance.adapt_to_entity(aliased_insp)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

alias এন্টিটির জন্য মানিয়ে নেয়।

## `AssociationProxyExtensionType` { #associationproxyextensiontype }

```python
from sqlalchemy.ext.associationproxy import AssociationProxyExtensionType
```

inspection-এ association proxy চেনার enum।

**উদাহরণ:**

```python
kinds = [k for k, d in inspect(User).all_orm_descriptors.items()
         if d.extension_type is AssociationProxyExtensionType.ASSOCIATION_PROXY]
print(kinds)   # ['keywords']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #associationproxyextensiontype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`ASSOCIATION_PROXY`](#associationproxyextensiontype-ASSOCIATION-PROXY) | অ্যাট্রিবিউট | association proxy অ্যাট্রিবিউট। |

### `AssociationProxyExtensionType.ASSOCIATION_PROXY` { #associationproxyextensiontype-ASSOCIATION-PROXY }

**ধরন:** অ্যাট্রিবিউট

association proxy অ্যাট্রিবিউট।

**উদাহরণ:**

```python
print(AssociationProxyExtensionType.ASSOCIATION_PROXY.name)   # ASSOCIATION_PROXY
```

/// check | সংক্ষেপে মনে রাখুন

* মাঝের association অবজেক্ট লুকিয়ে সরাসরি মান: `association_proxy("রিলেশনশিপ", "অ্যাট্রিবিউট")`।
* নতুন মান যোগ করলে মাঝের অবজেক্ট বানাতে `creator=` দিন।
* কুয়েরি: `User.keywords.any(...)`, `.contains("x")`, `Address.user_name == "..."`।
* টাইপ হিন্ট: `AssociationProxy[list[str]]`।

///
