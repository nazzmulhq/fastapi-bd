# Hybrid Attribute API: hybrid_property, hybrid_method, index_property { #api-hybrid }

/// note | এই পেজে যা আছে

* `hybrid_property`: Python-এ আর SQL-এ দুই জায়গাতেই কাজ করা প্রপার্টি; **সব** সদস্য (`expression`, `setter`, `update_expression`, ২.১-এর `bulk_dml`, `inplace`, `overrides` …) আর প্রতিটি প্যারামিটার।
* `hybrid_method`, `Comparator`, `ExprComparator`, `HybridExtensionType`।
* `index_property` (`sqlalchemy.ext.indexable`): JSON/ARRAY কলামের একটি key-কে আলাদা অ্যাট্রিবিউটের মতো ব্যবহার।

///

সাধারণ Python `@property` শুধু অবজেক্টে কাজ করে (`user.full_name`)। **hybrid** একই নামে ক্লাস-স্তরেও কাজ করে: `User.full_name` একটি SQL এক্সপ্রেশন হয়ে যায়, তাই `where(User.full_name == "...")` বা `order_by(User.full_name)` লেখা যায়। একই যুক্তি দুবার লিখতে হয় না। বিস্তারিত উদাহরণ: [ম্যাপিং ও Event অধ্যায়](../advanced-mapping.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str]
    last: Mapped[str]
    balance: Mapped[int] = mapped_column(default=0)
    prefs: Mapped[dict] = mapped_column(JSONB, default=dict)

    @hybrid_property
    def full_name(self) -> str:
        return self.first + " " + self.last
```

ডেটা: রহিম উদ্দিন (balance ৫০০), করিম মিয়া (balance ০), সুমি আক্তার (balance ১২০০)। `names(শর্ত)` শর্তে মেলা প্রথম নামগুলো দেয় (id ক্রমে)। PostgreSQL 16-এ চালিয়ে দেখা।

///

## `hybrid_property` { #hybrid-property }

```python
from sqlalchemy.ext.hybrid import hybrid_property
```

ডেকোরেটর: একটি মেথডকে এমন প্রপার্টি বানায় যা অবজেক্টে Python হিসেবে আর ক্লাসে SQL এক্সপ্রেশন হিসেবে চলে। ভেতরের যুক্তি যদি SQL-এ সরাসরি অনুবাদযোগ্য না হয় (যেমন Python-এর `if`, `len()`), তাহলে আলাদা SQL রূপ `@x.inplace.expression` দিয়ে দিন।

**উদাহরণ:**

```python
u = session.get(User, 1)
print(u.full_name)                                        # রহিম উদ্দিন   (Python)
print(User.full_name == "করিম মিয়া")                      # (users.first || :first_1 || users.last) = :param_1   (SQL)
print(names(User.full_name.like("%আক্তার")))              # ['সুমি']
```

**Python যুক্তি SQL-এ সরাসরি চলে না: আলাদা expression**

```python
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int]

    @hybrid_property
    def tier(self) -> str:
        return "gold" if self.balance >= 1000 else "basic"      # Python-এর if

    @tier.inplace.expression
    @classmethod
    def _tier_expr(cls):
        return case((cls.balance >= 1000, "gold"), else_="basic")   # SQL-এর CASE

print(Account(balance=1500).tier, select(Account.tier).compile().string.split("\n")[0])
# gold SELECT CASE WHEN (accounts.balance >= :balance_1) THEN :param_1 ELSE :param_2 END AS tier
```

### কনস্ট্রাক্টরের প্যারামিটার { #hybrid-property-params }

```python
hybrid_property(fget, fset=None, fdel=None, expr=None, custom_comparator=None, update_expr=None, bulk_dml_setter=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `fget` | অবজেক্টে মান পড়ার ফাংশন (ডেকোরেটর হিসেবে দেওয়া মেথড)। |
| `fset` | মান সেট করার ফাংশন (`@x.setter`)। |
| `fdel` | মান মোছার ফাংশন (`@x.deleter`)। |
| `expr` | ক্লাস-স্তরের SQL এক্সপ্রেশন বানানোর ফাংশন (`@x.expression`)। |
| `custom_comparator` | নিজের `Comparator` (`@x.comparator`)। |
| `update_expr` | UPDATE/INSERT-এর `values()`-এ hybrid দিলে কোন কলামে কী বসবে তা বানানোর ফাংশন (`@x.update_expression`)। |
| `bulk_dml_setter` | (২.১) বাল্ক INSERT/UPDATE-এর প্রতিটি প্যারামিটার-dict-এ hybrid-এর মান কলামে ভাঙার ফাংশন (`@x.bulk_dml`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hybrid-property-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bulk_dml()`](#hybrid-property-bulk-dml) | মেথড | (২.১-এ নতুন) ডেকোরেটর: `session.execute(insert(User), [{...}, ...])`-এর মতো **বাল্ক** INSERT/UPDATE-এ প্রতিটি প্যারামিটার-dict ধরে hybrid-এর মান আসল কলামে বসায়। |
| [`comparator()`](#hybrid-property-comparator) | মেথড | ডেকোরেটর: hybrid-এর জন্য নিজের `Comparator` দেয়, যাতে `==`, `<` ইত্যাদি অপারেটর নিজের মতো কাজ করে (যেমন case-insensitive তুলনা)। |
| [`deleter()`](#hybrid-property-deleter) | মেথড | ডেকোরেটর: `del obj.x`-এর আচরণ। |
| [`expression()`](#hybrid-property-expression) | মেথড | ডেকোরেটর: ক্লাস-স্তরের SQL রূপ আলাদা করে দেয় (যখন Python যুক্তি সরাসরি SQL হয় না)। |
| [`extension_type`](#hybrid-property-extension-type) | অ্যাট্রিবিউট | inspection-এ এই অ্যাট্রিবিউটের ধরন: `HybridExtensionType.HYBRID_PROPERTY`। |
| [`getter()`](#hybrid-property-getter) | মেথড | ডেকোরেটর: getter বদলে দেয় (সাবক্লাসে override করতে)। |
| [`info`](#hybrid-property-info) | প্রপার্টি | hybrid-এর সাথে নিজের মেটাডেটার dict। |
| [`inplace`](#hybrid-property-inplace) | প্রপার্টি | (২.০.৪) "জায়গাতেই বদলানো" রূপ: `@x.inplace.setter`, `@x.inplace.expression` লিখলে নতুন hybrid কপি না বানিয়ে একই অবজেক্ট বদলায়, ফলে মেথডের নাম ভিন্ন রাখা যায় আর টাইপ-চেকার (mypy) ঠিকঠাক বোঝে। |
| [`is_aliased_class`](#hybrid-property-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_attribute`](#hybrid-property-is-attribute) | অ্যাট্রিবিউট | inspection-এ এটি একটি অ্যাট্রিবিউট (`True`)। |
| [`is_bundle`](#hybrid-property-is-bundle) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_clause_element`](#hybrid-property-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_instance`](#hybrid-property-is-instance) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_mapper`](#hybrid-property-is-mapper) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_property`](#hybrid-property-is-property) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_selectable`](#hybrid-property-is-selectable) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`overrides`](#hybrid-property-overrides) | প্রপার্টি | সাবক্লাসে প্যারেন্টের hybrid override করার সময় ব্যবহার: `@Parent.x.overrides.expression`। |
| [`setter()`](#hybrid-property-setter) | মেথড | ডেকোরেটর: `obj.x = মান` লিখলে কী হবে (যেমন পুরো নাম ভেঙে দুটি কলামে বসানো)। |
| [`update_expression()`](#hybrid-property-update-expression) | মেথড | ডেকোরেটর: `update(User).values({User.full_name: "..."})`-এ hybrid দিলে কোন কলামে কী বসবে তা বানায়; `[(কলাম, মান), ...]` ফেরত দিন। |

### `hybrid_property.bulk_dml()` { #hybrid-property-bulk-dml }

```python
hybrid_property.bulk_dml(meth)
```

**ধরন:** মেথড

(২.১-এ নতুন) ডেকোরেটর: `session.execute(insert(User), [{...}, ...])`-এর মতো **বাল্ক** INSERT/UPDATE-এ প্রতিটি প্যারামিটার-dict ধরে hybrid-এর মান আসল কলামে বসায়। মেথডটি `(cls, mapping, value)` নেয়।

**উদাহরণ:**

```python
class Person(Base):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str]
    last: Mapped[str]

    @hybrid_property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @name.inplace.bulk_dml
    @classmethod
    def _name_bulk(cls, mapping, value):
        mapping["first"], mapping["last"] = value.split(" ", 1)

Base.metadata.create_all(engine)
session.execute(insert(Person), [{"name": "আলিফ হাসান"}, {"name": "বৃষ্টি রায়"}])
print(session.scalars(select(Person.last).order_by(Person.id)).all())   # ['হাসান', 'রায়']
```

### `hybrid_property.comparator()` { #hybrid-property-comparator }

```python
hybrid_property.comparator(comparator)
```

**ধরন:** মেথড

ডেকোরেটর: hybrid-এর জন্য নিজের `Comparator` দেয়, যাতে `==`, `<` ইত্যাদি অপারেটর নিজের মতো কাজ করে (যেমন case-insensitive তুলনা)।

**উদাহরণ:**

```python
class CaseInsensitive(Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)

class Tag(Base):
    __tablename__ = "tags_ci"
    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str]

    @hybrid_property
    def word_ci(self) -> str:
        return self.word.lower()

    @word_ci.inplace.comparator
    @classmethod
    def _word_ci_cmp(cls):
        return CaseInsensitive(cls.word)

print(Tag.word_ci == "PYTHON")   # lower(tags_ci.word) = lower(:lower_1)
```

### `hybrid_property.deleter()` { #hybrid-property-deleter }

```python
hybrid_property.deleter(fdel)
```

**ধরন:** মেথড

ডেকোরেটর: `del obj.x`-এর আচরণ।

**উদাহরণ:**

```python
class Note(Base):
    __tablename__ = "notes_d"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str | None]

    @hybrid_property
    def text(self):
        return self.body

    @text.inplace.deleter
    def _text_del(self):
        self.body = None

n = Note(body="x"); del n.text
print(n.body)   # None
```

### `hybrid_property.expression()` { #hybrid-property-expression }

```python
hybrid_property.expression(expr)
```

**ধরন:** মেথড

ডেকোরেটর: ক্লাস-স্তরের SQL রূপ আলাদা করে দেয় (যখন Python যুক্তি সরাসরি SQL হয় না)। মেথডটি `@classmethod` হিসেবে `inplace`-এর সাথে লেখা সুপারিশকৃত।

**উদাহরণ:**

```python
class U2(Base):
    __tablename__ = "u2_expr"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    @hybrid_property
    def name_length(self) -> int:
        return len(self.name)

    @name_length.inplace.expression
    @classmethod
    def _name_length_expr(cls):
        return func.char_length(cls.name)

print(U2(name="ঢাকা").name_length, U2.name_length > 3)   # 4 char_length(u2_expr.name) > :char_length_1
```

### `hybrid_property.extension_type` { #hybrid-property-extension-type }

**ধরন:** অ্যাট্রিবিউট

inspection-এ এই অ্যাট্রিবিউটের ধরন: `HybridExtensionType.HYBRID_PROPERTY`। ORM অ্যাট্রিবিউট ঘুরে দেখে hybrid আলাদা করতে।

**উদাহরণ:**

```python
desc = inspect(User).all_orm_descriptors["full_name"]
print(desc.extension_type is HybridExtensionType.HYBRID_PROPERTY)   # True
```

### `hybrid_property.getter()` { #hybrid-property-getter }

```python
hybrid_property.getter(fget)
```

**ধরন:** মেথড

ডেকোরেটর: getter বদলে দেয় (সাবক্লাসে override করতে)।

**উদাহরণ:**

```python
h = hybrid_property(lambda self: self.v * 2)
h3 = h.getter(lambda self: self.v * 3)          # নতুন getter-সহ কপি

class Obj:
    v = 2

print(h.fget(Obj()), h3.fget(Obj()))   # 4 6
```

### `hybrid_property.info` { #hybrid-property-info }

**ধরন:** প্রপার্টি

hybrid-এর সাথে নিজের মেটাডেটার dict।

**উদাহরণ:**

```python
User.__dict__["full_name"].info["label"] = "পুরো নাম"
print(inspect(User).all_orm_descriptors["full_name"].info)   # {'label': 'পুরো নাম'}
```

### `hybrid_property.inplace` { #hybrid-property-inplace }

**ধরন:** প্রপার্টি

(২.০.৪) "জায়গাতেই বদলানো" রূপ: `@x.inplace.setter`, `@x.inplace.expression` লিখলে নতুন hybrid কপি না বানিয়ে একই অবজেক্ট বদলায়, ফলে মেথডের নাম ভিন্ন রাখা যায় আর টাইপ-চেকার (mypy) ঠিকঠাক বোঝে। নতুন কোডে এটাই সুপারিশকৃত।

**উদাহরণ:**

```python
print(type(User.__dict__["full_name"].inplace).__name__)   # _InPlace
```

### `hybrid_property.is_aliased_class` { #hybrid-property-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_attribute` { #hybrid-property-is-attribute }

**ধরন:** অ্যাট্রিবিউট

inspection-এ এটি একটি অ্যাট্রিবিউট (`True`)।

**উদাহরণ:**

```python
print(User.__dict__["full_name"].is_attribute)   # True
```

### `hybrid_property.is_bundle` { #hybrid-property-is-bundle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_clause_element` { #hybrid-property-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_instance` { #hybrid-property-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_mapper` { #hybrid-property-is-mapper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_property` { #hybrid-property-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.is_selectable` { #hybrid-property-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `hybrid_property.overrides` { #hybrid-property-overrides }

**ধরন:** প্রপার্টি

সাবক্লাসে প্যারেন্টের hybrid override করার সময় ব্যবহার: `@Parent.x.overrides.expression`। না দিলে ক্লাস-স্তরে `Parent.x` আগে থেকেই SQL অ্যাট্রিবিউট হয়ে যাওয়ায় decorator কাজ করে না।

**উদাহরণ:**

```python
print(User.__dict__["full_name"].overrides is User.__dict__["full_name"])   # True
```

### `hybrid_property.setter()` { #hybrid-property-setter }

```python
hybrid_property.setter(fset)
```

**ধরন:** মেথড

ডেকোরেটর: `obj.x = মান` লিখলে কী হবে (যেমন পুরো নাম ভেঙে দুটি কলামে বসানো)।

**উদাহরণ:**

```python
class P2(Base):
    __tablename__ = "p2_set"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str]
    last: Mapped[str]

    @hybrid_property
    def name(self) -> str:
        return f"{self.first} {self.last}"

    @name.inplace.setter
    def _name_set(self, value: str) -> None:
        self.first, self.last = value.split(" ", 1)

p = P2(); p.name = "নাজমুল হক"
print(p.first, "|", p.last)   # নাজমুল | হক
```

### `hybrid_property.update_expression()` { #hybrid-property-update-expression }

```python
hybrid_property.update_expression(meth)
```

**ধরন:** মেথড

ডেকোরেটর: `update(User).values({User.full_name: "..."})`-এ hybrid দিলে কোন কলামে কী বসবে তা বানায়; `[(কলাম, মান), ...]` ফেরত দিন।

**উদাহরণ:**

```python
class P3(Base):
    __tablename__ = "p3_upd"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str]
    last: Mapped[str]

    @hybrid_property
    def name(self) -> str:
        return self.first + " " + self.last      # f-string নয়: ক্লাস-স্তরে এটি SQL হতে হবে

    @name.inplace.update_expression
    @classmethod
    def _name_upd(cls, value):
        f, l = value.split(" ", 1)
        return [(cls.first, f), (cls.last, l)]

print(update(P3).values({P3.name: "নাজমুল হক"}))   # UPDATE p3_upd SET first=:first, last=:last
```

## `hybrid_method` { #hybrid-method }

```python
from sqlalchemy.ext.hybrid import hybrid_method
```

`hybrid_property`-এর মেথড রূপ: আর্গুমেন্ট নেয়। অবজেক্টে Python, ক্লাসে SQL।

**উদাহরণ:**

```python
class Acc(Base):
    __tablename__ = "acc_hm"
    id: Mapped[int] = mapped_column(primary_key=True)
    balance: Mapped[int]

    @hybrid_method
    def has_at_least(self, amount: int) -> bool:
        return self.balance >= amount

print(Acc(balance=700).has_at_least(500), Acc.has_at_least(500))   # True acc_hm.balance >= :balance_1
print(names(User.balance >= 1000))                                  # ['সুমি']
```

### কনস্ট্রাক্টরের প্যারামিটার { #hybrid-method-params }

```python
hybrid_method(func, expr=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `func` | অবজেক্ট-স্তরের মেথড। |
| `expr` | ক্লাস-স্তরের SQL রূপের মেথড (`@x.expression`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hybrid-method-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`expression()`](#hybrid-method-expression) | মেথড | ডেকোরেটর: আলাদা SQL রূপ। |
| [`extension_type`](#hybrid-method-extension-type) | অ্যাট্রিবিউট | `HybridExtensionType.HYBRID_METHOD`। |
| [`info`](#hybrid-method-info) | প্রপার্টি | নিজের মেটাডেটার dict। |
| [`inplace`](#hybrid-method-inplace) | প্রপার্টি | (২.০.৪) জায়গাতেই বদলানোর রূপ (`@x.inplace.expression`)। |
| [`is_aliased_class`](#hybrid-method-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_attribute`](#hybrid-method-is-attribute) | অ্যাট্রিবিউট | inspection-এ অ্যাট্রিবিউট (`True`)। |
| [`is_bundle`](#hybrid-method-is-bundle) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_clause_element`](#hybrid-method-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_instance`](#hybrid-method-is-instance) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_mapper`](#hybrid-method-is-mapper) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_property`](#hybrid-method-is-property) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |
| [`is_selectable`](#hybrid-method-is-selectable) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ। |

### `hybrid_method.expression()` { #hybrid-method-expression }

```python
hybrid_method.expression(expr)
```

**ধরন:** মেথড

ডেকোরেটর: আলাদা SQL রূপ।

**উদাহরণ:**

```python
class Acc2(Base):
    __tablename__ = "acc_hm2"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    @hybrid_method
    def starts(self, prefix: str) -> bool:
        return self.name.startswith(prefix)

    @starts.inplace.expression
    @classmethod
    def _starts_expr(cls, prefix: str):
        return cls.name.startswith(prefix)

print(Acc2(name="ঢাকা").starts("ঢা"), Acc2.starts("ঢা"))   # True acc_hm2.name LIKE :name_1 || '%'
```

### `hybrid_method.extension_type` { #hybrid-method-extension-type }

**ধরন:** অ্যাট্রিবিউট

`HybridExtensionType.HYBRID_METHOD`।

**উদাহরণ:**

```python
class Acc3(Base):
    __tablename__ = "acc_hm3"
    id: Mapped[int] = mapped_column(primary_key=True)
    @hybrid_method
    def f(self, x): return x
print(Acc3.__dict__["f"].extension_type.name)   # HYBRID_METHOD
```

### `hybrid_method.info` { #hybrid-method-info }

**ধরন:** প্রপার্টি

নিজের মেটাডেটার dict।

**উদাহরণ:**

```python
print(hybrid_method(lambda self: 1).info)   # {}
```

### `hybrid_method.inplace` { #hybrid-method-inplace }

**ধরন:** প্রপার্টি

(২.০.৪) জায়গাতেই বদলানোর রূপ (`@x.inplace.expression`)।

**উদাহরণ:**

```python
hm = hybrid_method(lambda self: 1)
print(hm.inplace is hm)   # True  (hybrid_method-এ inplace নিজেকেই দেয়)
```

### `hybrid_method.is_aliased_class` { #hybrid-method-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_attribute` { #hybrid-method-is-attribute }

**ধরন:** অ্যাট্রিবিউট

inspection-এ অ্যাট্রিবিউট (`True`)।

**উদাহরণ:**

```python
print(hybrid_method(lambda self: 1).is_attribute)   # True
```

### `hybrid_method.is_bundle` { #hybrid-method-is-bundle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_clause_element` { #hybrid-method-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_instance` { #hybrid-method-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_mapper` { #hybrid-method-is-mapper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_property` { #hybrid-method-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

### `hybrid_method.is_selectable` { #hybrid-method-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ।

## `Comparator` { #hybrid-comparator }

```python
from sqlalchemy.ext.hybrid import Comparator
```

hybrid-এর জন্য নিজের অপারেটর-আচরণ বানানোর মূল ক্লাস (`@x.inplace.comparator`-এ ফেরত দিন)। কনস্ট্রাক্টরে মূল এক্সপ্রেশন দিন; `__clause_element__()` সেটি দেয়। ORM অ্যাট্রিবিউটের সব অপারেটর (`any()`, `has()`, `of_type()` …) আর কলামের সব অপারেটর আছে।

**উদাহরণ:**

```python
c = Comparator(User.balance)
print(c.__clause_element__())   # users.balance
```

### কনস্ট্রাক্টরের প্যারামিটার { #hybrid-comparator-params }

```python
Comparator(expression)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expression` | মূল SQL এক্সপ্রেশন। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hybrid-comparator-summary }

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৫৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `Comparator`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`QueryableAttribute` থেকে:** [`adapt_to_entity()`](operators.md#queryableattribute-adapt-to-entity) · [`adapter`](operators.md#queryableattribute-adapter) · [`and_()`](operators.md#queryableattribute-and-) · [`any()`](operators.md#queryableattribute-any) · [`any_op()`](operators.md#queryableattribute-any-op) · [`has()`](operators.md#queryableattribute-has) · [`has_op()`](operators.md#queryableattribute-has-op) · [`info`](operators.md#queryableattribute-info) · [`of_type()`](operators.md#queryableattribute-of-type) · [`of_type_op()`](operators.md#queryableattribute-of-type-op) · [`prop`](operators.md#queryableattribute-prop) · [`property`](operators.md#queryableattribute-property)

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`contains()`](operators.md#columnoperators-contains) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

///

## `ExprComparator` { #exprcomparator }

```python
from sqlalchemy.ext.hybrid import ExprComparator
```

ভেতরের: `@x.expression` দিয়ে বানানো SQL রূপকে মুড়িয়ে রাখার comparator (hybrid-এর নাম ও `info` বজায় রাখতে)। নিজে বানাতে হয় না।

**উদাহরণ:**

```python
print(isinstance(User.full_name.comparator, ExprComparator))   # True
```

### কনস্ট্রাক্টরের প্যারামিটার { #exprcomparator-params }

```python
ExprComparator(expression, hybrid)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `cls` | মালিক ক্লাস। |
| `expression` | SQL এক্সপ্রেশন। |
| `hybrid` | যে hybrid_property। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`Comparator`](#hybrid-comparator-summary)-এর মতো।

## `HybridExtensionType` { #hybridextensiontype }

```python
from sqlalchemy.ext.hybrid import HybridExtensionType
```

inspection-এ hybrid চেনার enum (`all_orm_descriptors`-এর `extension_type`)।

**উদাহরণ:**

```python
kinds = {k: d.extension_type for k, d in inspect(User).all_orm_descriptors.items() if k == "full_name"}
print(kinds["full_name"].name)   # HYBRID_PROPERTY
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #hybridextensiontype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`HYBRID_METHOD`](#hybridextensiontype-HYBRID-METHOD) | অ্যাট্রিবিউট | `hybrid_method`। |
| [`HYBRID_PROPERTY`](#hybridextensiontype-HYBRID-PROPERTY) | অ্যাট্রিবিউট | `hybrid_property`। |

### `HybridExtensionType.HYBRID_METHOD` { #hybridextensiontype-HYBRID-METHOD }

**ধরন:** অ্যাট্রিবিউট

`hybrid_method`।

**উদাহরণ:**

```python
print(HybridExtensionType.HYBRID_METHOD.name)   # HYBRID_METHOD
```

### `HybridExtensionType.HYBRID_PROPERTY` { #hybridextensiontype-HYBRID-PROPERTY }

**ধরন:** অ্যাট্রিবিউট

`hybrid_property`।

**উদাহরণ:**

```python
print(HybridExtensionType.HYBRID_PROPERTY.name)   # HYBRID_PROPERTY
```

## Indexable { #index-property-group }

## `index_property` { #index-property }

```python
from sqlalchemy.ext.indexable import index_property
```

একটি JSON/ARRAY কলামের **একটি key বা index**-কে আলাদা অ্যাট্রিবিউটের মতো দেখায়: `user.theme` পড়লে `user.prefs["theme"]`, লিখলে সেখানে বসায় (আর ORM বদল ধরে)। ক্লাস-স্তরে SQL-এ `prefs['theme']`। এটি একটি `hybrid_property`-এর সাবক্লাস।

**উদাহরণ:**

```python
class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    theme = index_property("data", "theme", default="light")

Base.metadata.create_all(engine)
p = Profile(data={}); session.add(p)
print(p.theme)                       # light   (key নেই, তাই default)
p.theme = "dark"; session.commit()
print(session.scalar(select(Profile.data)))   # {'theme': 'dark'}
```

### কনস্ট্রাক্টরের প্যারামিটার { #index-property-params }

```python
index_property(attr_name, index, default=object(), datatype=None, mutable=True, onebased=True)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attr_name` | যে JSON/ARRAY কলামের নাম। |
| `index` | key (স্ট্রিং) বা index (সংখ্যা)। |
| `default` | key না থাকলে যে মান (না দিলে `AttributeError`)। |
| `datatype` | কলাম খালি (`None`) থাকলে নতুন কী বানাবে (`dict` বা `list`)। |
| `mutable` | `True` (ডিফল্ট) হলে সেট করার সময় নতুন dict কপি বানিয়ে বসায়, যাতে ORM বদল ধরতে পারে। |
| `onebased` | ARRAY-তে SQL index ১ থেকে ধরবে কি না (ডিফল্ট `True`)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #index-property-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`expr()`](#index-property-expr) | মেথড (internal) | ক্লাস-স্তরের SQL রূপ বানানোর মেথড (`কলাম[index]`)। |
| [`fdel()`](#index-property-fdel) | মেথড (internal) | `del obj.x`-এ key মুছে দেওয়ার ভেতরের মেথড। |
| [`fget()`](#index-property-fget) | মেথড (internal) | অবজেক্টে মান পড়ার ভেতরের মেথড। |
| [`fset()`](#index-property-fset) | মেথড (internal) | অবজেক্টে মান বসানোর ভেতরের মেথড। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ১৯টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `index_property`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`hybrid_property` থেকে:** [`bulk_dml()`](#hybrid-property-bulk-dml) · [`comparator()`](#hybrid-property-comparator) · [`deleter()`](#hybrid-property-deleter) · [`expression()`](#hybrid-property-expression) · [`extension_type`](#hybrid-property-extension-type) · [`getter()`](#hybrid-property-getter) · [`info`](#hybrid-property-info) · [`inplace`](#hybrid-property-inplace) · [`is_aliased_class`](#hybrid-property-is-aliased-class) · [`is_attribute`](#hybrid-property-is-attribute) · [`is_bundle`](#hybrid-property-is-bundle) · [`is_clause_element`](#hybrid-property-is-clause-element) · [`is_instance`](#hybrid-property-is-instance) · [`is_mapper`](#hybrid-property-is-mapper) · [`is_property`](#hybrid-property-is-property) · [`is_selectable`](#hybrid-property-is-selectable) · [`overrides`](#hybrid-property-overrides) · [`setter()`](#hybrid-property-setter) · [`update_expression()`](#hybrid-property-update-expression)

///

### `index_property.expr()` { #index-property-expr }

```python
index_property.expr(model)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্লাস-স্তরের SQL রূপ বানানোর মেথড (`কলাম[index]`)।

### `index_property.fdel()` { #index-property-fdel }

```python
index_property.fdel(instance)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`del obj.x`-এ key মুছে দেওয়ার ভেতরের মেথড।

### `index_property.fget()` { #index-property-fget }

```python
index_property.fget(instance, /)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টে মান পড়ার ভেতরের মেথড।

### `index_property.fset()` { #index-property-fset }

```python
index_property.fset(instance, value)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অবজেক্টে মান বসানোর ভেতরের মেথড।

/// check | সংক্ষেপে মনে রাখুন

* Python আর SQL দুই জায়গায় একই নাম: `@hybrid_property`।
* Python যুক্তি SQL-এ অনুবাদ না হলে: `@x.inplace.expression` + `@classmethod`।
* মান সেট: `@x.inplace.setter`; `update().values()`-এ: `update_expression`; বাল্ক dict-এ: `bulk_dml` (২.১)।
* আর্গুমেন্টসহ: `@hybrid_method`।
* JSON-এর একটি key আলাদা অ্যাট্রিবিউট হিসেবে: `index_property("data", "key")`।

///
