# কলাম অপারেটর API: ==, in_, like, any, has … { #api-operators }

/// note | এই পেজে যা আছে

* কলামে ব্যবহার করা যায় এমন **সব** অপারেটর: Python-এর `==`, `<`, `+`, `&`, `|`, `~` … আর `ColumnOperators`-এর প্রতিটি মেথড (৪৭টি): `in_()`, `like()`, `ilike()`, `between()`, `is_()`, `contains()`, `regexp_match()`, `op()` …
* মডেলের অ্যাট্রিবিউট (`User.name`, `User.addresses`) আসলে `QueryableAttribute`; তার **সব** সদস্য (৮২টি), বিশেষ করে রিলেশনশিপের `any()`, `has()`, `of_type()`, `and_()`।

///

`User.name == "রহিম"` লিখলে Python সাথে সাথে `True`/`False` হিসাব করে না; একটি **SQL এক্সপ্রেশন** (`users.name = :name_1`) বানায়, যা পরে `where()`-এ বসে। এই পেজের প্রতিটি অপারেটর এভাবেই কাজ করে: কলাম বা এক্সপ্রেশনের ওপর ডাকলে নতুন এক্সপ্রেশন ফেরত দেয়। একই অপারেটর `func.lower(User.name)`, `select(...).scalar_subquery()` বা `literal(5)`-এর মতো যেকোনো SQL এক্সপ্রেশনেও চলে।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str | None]
    age: Mapped[int | None]
    flags: Mapped[int] = mapped_column(default=0)          # বিট-ফ্ল্যাগ
    scores: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    addresses: Mapped[list["Address"]] = relationship(back_populates="user")

class Address(Base):                                       # id, email, city, user_id, user
    ...

class Employee(Base):                                      # joined inheritance: Engineer (lang), Manager
    ...                                                    # company_id → Company.employees
```

| id | name | email | age | flags | scores | ঠিকানা |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ১ | রহিম | `rahim@example.com` | ৩০ | ৫ (`0b101`) | `[80, 90]` | ঢাকা, চট্টগ্রাম |
| ২ | করিম | `NULL` | ২৫ | ২ (`0b010`) | `[50]` | – |
| ৩ | সুমি | `Sumi@Example.COM` | `NULL` | ৭ (`0b111`) | `[95, 100]` | ঢাকা |

দুটি ছোট হেল্পার: `names(শর্ত)` সেই শর্তে মেলা ইউজারদের নাম দেয় (id ক্রমে), আর `pg(এক্সপ্রেশন)` PostgreSQL-এর জন্য তৈরি হওয়া আসল SQL দেখায় (মানগুলো সরাসরি বসিয়ে)। সাধারণ `print(এক্সপ্রেশন)` ডেটাবেস-নিরপেক্ষ রূপ দেখায়, যেখানে মানের জায়গায় `:name_1`-এর মতো প্যারামিটার থাকে। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## `ColumnOperators` { #columnoperators }

```python
from sqlalchemy.sql.operators import ColumnOperators
```

কলাম ও SQL এক্সপ্রেশনের সব অপারেটরের মূল ক্লাস। আপনি এটি সরাসরি কখনো বানাবেন না; `User.name`, `users_table.c.name`, `func.count()`, `literal(5)` সবই এর সাবক্লাস, তাই নিচের প্রতিটি মেথড এদের সবার ওপর চলে।

**Python অপারেটর → SQL** (এগুলো মেথড নয়, সরাসরি চিহ্ন দিয়ে লেখা হয়):

* `==`, `!=` → `=`, `!=`; ডান দিকে `None` দিলে `IS NULL` / `IS NOT NULL`। উদাহরণ: `User.name == "রহিম"`
* `<`, `<=`, `>`, `>=` → তুলনা। উদাহরণ: `User.age >= 18`
* `+`, `-`, `*`, `/`, `//`, `%`, `**` → গাণিতিক; স্ট্রিং কলামে `+` মানে জোড়া লাগানো (SQL-এ `||`)। উদাহরণ: `User.age + 1`, `User.name + "!"`
* `-x` → ঋণাত্মক। উদাহরণ: `-User.age`
* `&`, `|`, `~` → `AND`, `OR`, `NOT` (**প্রতিটি পাশে বন্ধনী দিন**)। উদাহরণ: `(User.age > 20) & (User.age < 40)`
* `<<`, `>>` → বিট শিফট। উদাহরণ: `User.flags << 1`
* `x[i]` → index/slice (ARRAY, JSON কলামে)। উদাহরণ: `User.scores[1]`
* `@` → ম্যাট্রিক্স-গুণ অপারেটর; কাস্টম টাইপে নিজের অর্থ দিতে।

/// warning | সাধারণ ভুল

* `and`, `or`, `not`, `in` (Python-এর কীওয়ার্ড) **কাজ করে না**; ব্যবহার করুন `&` / `and_()`, `|` / `or_()`, `~` / `not_()`, আর `.in_()`।
* `&` আর `|`-এর অগ্রাধিকার `==`-এর চেয়ে বেশি, তাই `User.age > 20 & User.age < 40` ভুল; প্রতিটি শর্ত বন্ধনীতে রাখুন।
* `User.email == None` কাজ করে (`IS NULL` হয়), কিন্তু লিন্টার আপত্তি করে; `User.email.is_(None)` লেখাই পরিষ্কার।

///

**উদাহরণ:**

```python
print(User.name == "রহিম")                        # users.name = :name_1
print(names((User.age > 20) & (User.age < 28)))   # ['করিম']
print(names(User.email == None))                  # ['করিম']
print(names(~(User.name == "রহিম")))              # ['করিম', 'সুমি']
```

**গাণিতিক অপারেটর, স্ট্রিং জোড়া আর index**

```python
row = session.execute(select(User.age + 1, User.age // 7, User.name + "!", User.scores[1])
                      .where(User.id == 1)).one()
print(tuple(row))   # (31, 4, 'রহিম!', 80)   (PostgreSQL ARRAY-র index ১ থেকে শুরু)
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #columnoperators-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`all_()`](#columnoperators-all-) | মেথড | `ALL (array)`: ডান দিকের অ্যারে বা সাবকুয়েরির **সব** মানের সাথে তুলনা। |
| [`any_()`](#columnoperators-any-) | মেথড | `ANY (array)`: অ্যারে বা সাবকুয়েরির **যেকোনো একটি** মানের সাথে তুলনা মিললেই সত্য। |
| [`asc()`](#columnoperators-asc) | মেথড | `ORDER BY`-তে ছোট থেকে বড় ক্রম (ডিফল্টও এটাই)। |
| [`between()`](#columnoperators-between) | মেথড | `BETWEEN a AND b`: মান দুটি সীমার মধ্যে (দুই সীমাসহ)। |
| [`bitwise_and()`](#columnoperators-bitwise-and) | মেথড | বিট-ভিত্তিক AND (`&` SQL অপারেটর)। |
| [`bitwise_lshift()`](#columnoperators-bitwise-lshift) | মেথড | বিট বাঁয়ে সরানো (`<<`)। |
| [`bitwise_not()`](#columnoperators-bitwise-not) | মেথড | সব বিট উল্টে দেয় (`~`; বুলিয়ান `NOT`-এর সাথে গুলিয়ে ফেলবেন না)। |
| [`bitwise_or()`](#columnoperators-bitwise-or) | মেথড | বিট-ভিত্তিক OR (<code>&#124;</code>): বিট চালু করতে, যেমন <code>UPDATE ... SET flags = flags &#124; 8</code>। |
| [`bitwise_rshift()`](#columnoperators-bitwise-rshift) | মেথড | বিট ডানে সরানো (`>>`)। |
| [`bitwise_xor()`](#columnoperators-bitwise-xor) | মেথড | বিট-ভিত্তিক XOR (PostgreSQL-এ `#`, অন্য ডেটাবেসে `^`)। |
| [`bool_op()`](#columnoperators-bool-op) | মেথড | `op()`-এর মতো কাস্টম অপারেটর বানায়, কিন্তু ফলাফল বুলিয়ান ধরে (তুলনা অপারেটর)। |
| [`collate()`](#columnoperators-collate) | মেথড | এক্সপ্রেশনে `COLLATE` বসায়: তুলনা বা সাজানোর সময় কোন ভাষা/নিয়ম মানা হবে। |
| [`concat()`](#columnoperators-concat) | মেথড | স্ট্রিং জোড়া লাগায় (<code>&#124;&#124;</code>)। |
| [`contains()`](#columnoperators-contains) | মেথড | স্ট্রিংয়ের ভেতরে কোথাও আছে কি না: <code>LIKE '%' &#124;&#124; x &#124;&#124; '%'</code>। |
| [`desc()`](#columnoperators-desc) | মেথড | `ORDER BY`-তে বড় থেকে ছোট ক্রম। |
| [`distinct()`](#columnoperators-distinct) | মেথড | কলামের আগে `DISTINCT` বসায়; সাধারণত aggregate-এর ভেতরে: `func.count(col.distinct())`। |
| [`endswith()`](#columnoperators-endswith) | মেথড | স্ট্রিং এই অংশ দিয়ে শেষ হয় কি না (<code>LIKE '%' &#124;&#124; x</code>)। |
| [`icontains()`](#columnoperators-icontains) | মেথড | `contains()`-এর case-insensitive রূপ (ছোট/বড় হাতের পার্থক্য উপেক্ষা)। |
| [`iendswith()`](#columnoperators-iendswith) | মেথড | `endswith()`-এর case-insensitive রূপ। |
| [`ilike()`](#columnoperators-ilike) | মেথড | case-insensitive `LIKE`। |
| [`in_()`](#columnoperators-in-) | মেথড | `IN (...)`: মান তালিকার যেকোনোটির সমান। |
| [`is_()`](#columnoperators-is-) | মেথড | `IS`: প্রধানত `NULL` যাচাইয়ে (`is_(None)`), আর `IS TRUE` / `IS FALSE`-এর জন্য। |
| [`is_distinct_from()`](#columnoperators-is-distinct-from) | মেথড | `IS DISTINCT FROM`: `!=`-এর মতো, কিন্তু NULL-কে সাধারণ মান ধরে তুলনা করে। |
| [`is_not()`](#columnoperators-is-not) | মেথড | `IS NOT`: প্রধানত `IS NOT NULL`। |
| [`is_not_distinct_from()`](#columnoperators-is-not-distinct-from) | মেথড | `IS NOT DISTINCT FROM`: NULL-নিরাপদ সমতা; দুটোই NULL হলেও সত্য। |
| [`isnot()`](#columnoperators-isnot) | মেথড (legacy) | `is_not()`-এর পুরোনো নাম (১.৪-এর আগে)। |
| [`isnot_distinct_from()`](#columnoperators-isnot-distinct-from) | মেথড (legacy) | `is_not_distinct_from()`-এর পুরোনো নাম। |
| [`istartswith()`](#columnoperators-istartswith) | মেথড | `startswith()`-এর case-insensitive রূপ। |
| [`like()`](#columnoperators-like) | মেথড | SQL `LIKE` প্যাটার্ন মিল (case-sensitive): `%` = যেকোনো অক্ষরসমষ্টি, `_` = ঠিক একটি অক্ষর। |
| [`match()`](#columnoperators-match) | মেথড | ডেটাবেসের ফুল-টেক্সট সার্চ অপারেটর। |
| [`not_ilike()`](#columnoperators-not-ilike) | মেথড | `NOT ILIKE`: case-insensitive প্যাটার্নে **না** মেলা। |
| [`not_in()`](#columnoperators-not-in) | মেথড | `NOT IN (...)`। |
| [`not_like()`](#columnoperators-not-like) | মেথড | `NOT LIKE`। |
| [`notilike()`](#columnoperators-notilike) | মেথড (legacy) | `not_ilike()`-এর পুরোনো নাম। |
| [`notin_()`](#columnoperators-notin-) | মেথড (legacy) | `not_in()`-এর পুরোনো নাম। |
| [`notlike()`](#columnoperators-notlike) | মেথড (legacy) | `not_like()`-এর পুরোনো নাম। |
| [`nulls_first()`](#columnoperators-nulls-first) | মেথড | `ORDER BY`-তে NULL মানগুলো সবার আগে। |
| [`nulls_last()`](#columnoperators-nulls-last) | মেথড | `ORDER BY`-তে NULL মানগুলো সবার শেষে (PostgreSQL-এ `DESC`-এর ডিফল্ট উল্টো, তাই কাজে লাগে)। |
| [`nullsfirst()`](#columnoperators-nullsfirst) | মেথড (legacy) | `nulls_first()`-এর পুরোনো নাম। |
| [`nullslast()`](#columnoperators-nullslast) | মেথড (legacy) | `nulls_last()`-এর পুরোনো নাম। |
| [`op()`](#columnoperators-op) | মেথড | যেকোনো কাস্টম বা ডেটাবেস-নির্দিষ্ট **বাইনারি অপারেটর** বানায়: `col.op("অপারেটর")(মান)`। |
| [`operate()`](#columnoperators-operate) | মেথড (internal) | সব অপারেটরের ভেতরের মূল হুক: প্রতিটি অপারেটর শেষ পর্যন্ত `operate(op, other)` ডাকে। |
| [`regexp_match()`](#columnoperators-regexp-match) | মেথড | রেগুলার এক্সপ্রেশন মিল। |
| [`regexp_replace()`](#columnoperators-regexp-replace) | মেথড | রেগুলার এক্সপ্রেশন দিয়ে স্ট্রিংয়ের অংশ বদলায় (`REGEXP_REPLACE`)। |
| [`reverse_operate()`](#columnoperators-reverse-operate) | মেথড (internal) | `operate()`-এর উল্টো দিকের রূপ: Python মান বাম দিকে থাকলে (যেমন `5 + User.age`) ডাকা হয়। |
| [`startswith()`](#columnoperators-startswith) | মেথড | স্ট্রিং এই অংশ দিয়ে শুরু হয় কি না (<code>LIKE x &#124;&#124; '%'</code>)। |
| [`timetuple`](#columnoperators-timetuple) | অ্যাট্রিবিউট (internal) | সবসময় `None`। |

### `ColumnOperators.all_()` { #columnoperators-all- }

```python
ColumnOperators.all_()
```

**ধরন:** মেথড

`ALL (array)`: ডান দিকের অ্যারে বা সাবকুয়েরির **সব** মানের সাথে তুলনা। মান বাম দিকে রেখে লিখুন: `5 < User.scores.all_()`। PostgreSQL ARRAY কলাম বা সাবকুয়েরিতে কাজ করে।

**উদাহরণ:**

```python
print(names(70 < User.scores.all_()))   # ['রহিম', 'সুমি']  (সব স্কোর ৭০-এর বেশি)
```

### `ColumnOperators.any_()` { #columnoperators-any- }

```python
ColumnOperators.any_()
```

**ধরন:** মেথড

`ANY (array)`: অ্যারে বা সাবকুয়েরির **যেকোনো একটি** মানের সাথে তুলনা মিললেই সত্য। "অ্যারেতে এই মানটি আছে কি না" দেখার সহজ উপায়।

**উদাহরণ:**

```python
print(names(90 == User.scores.any_()))   # ['রহিম']
pg(90 == User.scores.any_())             # 90 = ANY (users.scores)
```

### `ColumnOperators.asc()` { #columnoperators-asc }

```python
ColumnOperators.asc()
```

**ধরন:** মেথড

`ORDER BY`-তে ছোট থেকে বড় ক্রম (ডিফল্টও এটাই)।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.age.asc())).all())   # ['করিম', 'রহিম', 'সুমি']  (PostgreSQL-এ NULL শেষে)
```

### `ColumnOperators.between()` { #columnoperators-between }

```python
ColumnOperators.between(cleft, cright, symmetric=False)
```

**ধরন:** মেথড

`BETWEEN a AND b`: মান দুটি সীমার মধ্যে (দুই সীমাসহ)। `symmetric=True` দিলে সীমা দুটি উল্টো দিলেও কাজ করে (`BETWEEN SYMMETRIC`)।

**উদাহরণ:**

```python
print(names(User.age.between(25, 30)))                   # ['রহিম', 'করিম']
print(names(User.age.between(30, 25, symmetric=True)))   # ['রহিম', 'করিম']
```

### `ColumnOperators.bitwise_and()` { #columnoperators-bitwise-and }

```python
ColumnOperators.bitwise_and(other)
```

**ধরন:** মেথড

বিট-ভিত্তিক AND (`&` SQL অপারেটর)। বিট-ফ্ল্যাগ কলামে কোনো নির্দিষ্ট বিট চালু আছে কি না দেখতে। (Python-এর `&` চিহ্ন SQL-এ `AND` বানায়, তাই বিটের জন্য এই মেথড লাগে।)

**উদাহরণ:**

```python
print(names(User.flags.bitwise_and(4) != 0))   # ['রহিম', 'সুমি']  (৪ নম্বর বিট চালু)
```

### `ColumnOperators.bitwise_lshift()` { #columnoperators-bitwise-lshift }

```python
ColumnOperators.bitwise_lshift(other)
```

**ধরন:** মেথড

বিট বাঁয়ে সরানো (`<<`)।

**উদাহরণ:**

```python
print(session.scalar(select(User.flags.bitwise_lshift(1)).where(User.id == 2)))   # 4
```

### `ColumnOperators.bitwise_not()` { #columnoperators-bitwise-not }

```python
ColumnOperators.bitwise_not()
```

**ধরন:** মেথড

সব বিট উল্টে দেয় (`~`; বুলিয়ান `NOT`-এর সাথে গুলিয়ে ফেলবেন না)।

**উদাহরণ:**

```python
print(session.scalar(select(User.flags.bitwise_not()).where(User.id == 2)))   # -3
```

### `ColumnOperators.bitwise_or()` { #columnoperators-bitwise-or }

```python
ColumnOperators.bitwise_or(other)
```

**ধরন:** মেথড

বিট-ভিত্তিক OR (`|`): বিট চালু করতে, যেমন `UPDATE ... SET flags = flags | 8`।

**উদাহরণ:**

```python
print(session.scalar(select(User.flags.bitwise_or(8)).where(User.id == 2)))   # 10
```

### `ColumnOperators.bitwise_rshift()` { #columnoperators-bitwise-rshift }

```python
ColumnOperators.bitwise_rshift(other)
```

**ধরন:** মেথড

বিট ডানে সরানো (`>>`)।

**উদাহরণ:**

```python
print(session.scalar(select(User.flags.bitwise_rshift(1)).where(User.id == 3)))   # 3
```

### `ColumnOperators.bitwise_xor()` { #columnoperators-bitwise-xor }

```python
ColumnOperators.bitwise_xor(other)
```

**ধরন:** মেথড

বিট-ভিত্তিক XOR (PostgreSQL-এ `#`, অন্য ডেটাবেসে `^`)।

**উদাহরণ:**

```python
pg(User.flags.bitwise_xor(1))                                                  # users.flags # 1
print(session.scalar(select(User.flags.bitwise_xor(1)).where(User.id == 1)))   # 4
```

### `ColumnOperators.bool_op()` { #columnoperators-bool-op }

```python
ColumnOperators.bool_op(opstring, precedence=0, python_impl=None)
```

**ধরন:** মেথড

`op()`-এর মতো কাস্টম অপারেটর বানায়, কিন্তু ফলাফল বুলিয়ান ধরে (তুলনা অপারেটর)। ডেটাবেস-নির্দিষ্ট তুলনা অপারেটর (যেমন PostgreSQL-এর `@>`, `~*`) ব্যবহারের সঠিক উপায়।

**উদাহরণ:**

```python
print(names(User.scores.bool_op("@>")([90])))       # ['রহিম']  (অ্যারেতে 90 আছে)
print(names(User.name.bool_op("~*")("^স")))          # ['সুমি']  (রেগুলার এক্সপ্রেশন, case-insensitive)
```

### `ColumnOperators.collate()` { #columnoperators-collate }

```python
ColumnOperators.collate(collation, collation_schema=None)
```

**ধরন:** মেথড

এক্সপ্রেশনে `COLLATE` বসায়: তুলনা বা সাজানোর সময় কোন ভাষা/নিয়ম মানা হবে। যেমন বাইট-ক্রমে সাজাতে `"C"`।

**উদাহরণ:**

```python
pg(User.name.collate("C"))   # users.name COLLATE "C"
print(session.scalars(select(User.email).where(User.email.is_not(None))
                      .order_by(User.email.collate("C"))).all())   # ['Sumi@Example.COM', 'rahim@example.com']
```

### `ColumnOperators.concat()` { #columnoperators-concat }

```python
ColumnOperators.concat(other)
```

**ধরন:** মেথড

স্ট্রিং জোড়া লাগায় (`||`)। স্ট্রিং কলামে `+` লেখাও একই কাজ করে।

**উদাহরণ:**

```python
print(User.name.concat("!"))   # users.name || :name_1
print(session.scalar(select(User.name.concat(" ভাই")).where(User.id == 2)))   # করিম ভাই
```

### `ColumnOperators.contains()` { #columnoperators-contains }

```python
ColumnOperators.contains(other, **kw)
```

**ধরন:** মেথড

স্ট্রিংয়ের ভেতরে কোথাও আছে কি না: `LIKE '%' || x || '%'`। `autoescape=True` দিলে মানের ভেতরের `%` ও `_` আক্ষরিক অর্থে ধরা হয় (ইউজার ইনপুটে নিরাপদ)। স্ট্রিং ছাড়া অন্য টাইপে (যেমন ARRAY, JSONB) টাইপ-নির্দিষ্ট অর্থ হয়। রিলেশনশিপ অ্যাট্রিবিউটে (`User.addresses.contains(obj)`) মানে "এই অবজেক্টটি কালেকশনে আছে"।

**উদাহরণ:**

```python
print(names(User.email.contains("example")))   # ['রহিম']  (case-sensitive; সুমির 'Example' মেলেনি)
print(User.name.contains("50%", autoescape=True))   # users.name LIKE '%' || :name_1 || '%' ESCAPE '/'
```

### `ColumnOperators.desc()` { #columnoperators-desc }

```python
ColumnOperators.desc()
```

**ধরন:** মেথড

`ORDER BY`-তে বড় থেকে ছোট ক্রম।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.id.desc())).all())   # ['সুমি', 'করিম', 'রহিম']
```

### `ColumnOperators.distinct()` { #columnoperators-distinct }

```python
ColumnOperators.distinct()
```

**ধরন:** মেথড

কলামের আগে `DISTINCT` বসায়; সাধারণত aggregate-এর ভেতরে: `func.count(col.distinct())`।

**উদাহরণ:**

```python
print(session.scalar(select(func.count(Address.city.distinct()))))   # 2
```

### `ColumnOperators.endswith()` { #columnoperators-endswith }

```python
ColumnOperators.endswith(other, escape=None, autoescape=False)
```

**ধরন:** মেথড

স্ট্রিং এই অংশ দিয়ে শেষ হয় কি না (`LIKE '%' || x`)। `escape`/`autoescape` দিয়ে `%`, `_` আক্ষরিক ধরা যায়।

**উদাহরণ:**

```python
print(names(User.email.endswith(".com")))   # ['রহিম']  (সুমির '.COM' বড় হাতের)
```

### `ColumnOperators.icontains()` { #columnoperators-icontains }

```python
ColumnOperators.icontains(other, **kw)
```

**ধরন:** মেথড

`contains()`-এর case-insensitive রূপ (ছোট/বড় হাতের পার্থক্য উপেক্ষা)।

**উদাহরণ:**

```python
print(names(User.email.icontains("EXAMPLE")))   # ['রহিম', 'সুমি']
print(User.email.icontains("x"))                # lower(users.email) LIKE '%' || lower(:email_1) || '%'
```

### `ColumnOperators.iendswith()` { #columnoperators-iendswith }

```python
ColumnOperators.iendswith(other, escape=None, autoescape=False)
```

**ধরন:** মেথড

`endswith()`-এর case-insensitive রূপ।

**উদাহরণ:**

```python
print(names(User.email.iendswith(".com")))   # ['রহিম', 'সুমি']
```

### `ColumnOperators.ilike()` { #columnoperators-ilike }

```python
ColumnOperators.ilike(other, escape=None)
```

**ধরন:** মেথড

case-insensitive `LIKE`। PostgreSQL-এ আসল `ILIKE` বসে; অন্য ডেটাবেসে `lower(x) LIKE lower(y)` দিয়ে একই ফল। প্যাটার্নে `%` = যেকোনো অক্ষরসমষ্টি, `_` = একটি অক্ষর।

**উদাহরণ:**

```python
print(names(User.email.ilike("%@example.com")))   # ['রহিম', 'সুমি']
pg(User.email.ilike("s%"))                         # users.email ILIKE 's%'
```

### `ColumnOperators.in_()` { #columnoperators-in- }

```python
ColumnOperators.in_(other)
```

**ধরন:** মেথড

`IN (...)`: মান তালিকার যেকোনোটির সমান। তালিকা, সাবকুয়েরি (`select(...)`), বা `bindparam("ids", expanding=True)` দেওয়া যায়। খালি তালিকা দিলেও নিরাপদ (কোনো রো মেলে না, এরর হয় না)।

**উদাহরণ:**

```python
print(names(User.id.in_([1, 3])))                                   # ['রহিম', 'সুমি']
print(names(User.id.in_(select(Address.user_id))))                  # ['রহিম', 'সুমি']
print(names(User.id.in_([])))                                        # []
```

### `ColumnOperators.is_()` { #columnoperators-is- }

```python
ColumnOperators.is_(other)
```

**ধরন:** মেথড

`IS`: প্রধানত `NULL` যাচাইয়ে (`is_(None)`), আর `IS TRUE` / `IS FALSE`-এর জন্য।

**উদাহরণ:**

```python
print(names(User.age.is_(None)))   # ['সুমি']
print(User.age.is_(None))          # users.age IS NULL
```

### `ColumnOperators.is_distinct_from()` { #columnoperators-is-distinct-from }

```python
ColumnOperators.is_distinct_from(other)
```

**ধরন:** মেথড

`IS DISTINCT FROM`: `!=`-এর মতো, কিন্তু NULL-কে সাধারণ মান ধরে তুলনা করে। `age != 30` NULL রো বাদ দেয়, এটি দেয় না।

**উদাহরণ:**

```python
print(names(User.age != 30))                    # ['করিম']  (সুমির NULL বাদ পড়ল)
print(names(User.age.is_distinct_from(30)))     # ['করিম', 'সুমি']
```

### `ColumnOperators.is_not()` { #columnoperators-is-not }

```python
ColumnOperators.is_not(other)
```

**ধরন:** মেথড

`IS NOT`: প্রধানত `IS NOT NULL`।

**উদাহরণ:**

```python
print(names(User.email.is_not(None)))   # ['রহিম', 'সুমি']
```

### `ColumnOperators.is_not_distinct_from()` { #columnoperators-is-not-distinct-from }

```python
ColumnOperators.is_not_distinct_from(other)
```

**ধরন:** মেথড

`IS NOT DISTINCT FROM`: NULL-নিরাপদ সমতা; দুটোই NULL হলেও সত্য।

**উদাহরণ:**

```python
print(names(User.age.is_not_distinct_from(None)))   # ['সুমি']
```

### `ColumnOperators.isnot()` { #columnoperators-isnot }

```python
ColumnOperators.isnot(other)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`is_not()`-এর পুরোনো নাম (১.৪-এর আগে)। নতুন কোডে `is_not()`।

**উদাহরণ:**

```python
print(names(User.email.isnot(None)))   # ['রহিম', 'সুমি']
```

### `ColumnOperators.isnot_distinct_from()` { #columnoperators-isnot-distinct-from }

```python
ColumnOperators.isnot_distinct_from(other)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`is_not_distinct_from()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(names(User.age.isnot_distinct_from(25)))   # ['করিম']
```

### `ColumnOperators.istartswith()` { #columnoperators-istartswith }

```python
ColumnOperators.istartswith(other, escape=None, autoescape=False)
```

**ধরন:** মেথড

`startswith()`-এর case-insensitive রূপ।

**উদাহরণ:**

```python
print(names(User.email.istartswith("SUMI")))   # ['সুমি']
```

### `ColumnOperators.like()` { #columnoperators-like }

```python
ColumnOperators.like(other, escape=None)
```

**ধরন:** মেথড

SQL `LIKE` প্যাটার্ন মিল (case-sensitive): `%` = যেকোনো অক্ষরসমষ্টি, `_` = ঠিক একটি অক্ষর। `escape="/"` দিলে `/%` মানে আক্ষরিক `%`।

**উদাহরণ:**

```python
print(names(User.email.like("%@example.com")))   # ['রহিম']
print(names(User.name.like("_ুমি")))              # ['সুমি']
```

### `ColumnOperators.match()` { #columnoperators-match }

```python
ColumnOperators.match(other, **kwargs)
```

**ধরন:** মেথড

ডেটাবেসের ফুল-টেক্সট সার্চ অপারেটর। PostgreSQL-এ `to_tsvector(col) @@ plainto_tsquery(x)`; MySQL-এ `MATCH ... AGAINST`। `postgresql_regconfig="english"` দিয়ে ভাষা ঠিক করা যায়।

**উদাহরণ:**

```python
pg(Address.city.match("ঢাকা"))   # addresses.city @@ plainto_tsquery('ঢাকা')
print(session.scalars(select(Address.id).where(Address.city.match("ঢাকা")).order_by(Address.id)).all())   # [1, 3]
```

### `ColumnOperators.not_ilike()` { #columnoperators-not-ilike }

```python
ColumnOperators.not_ilike(other, escape=None)
```

**ধরন:** মেথড

`NOT ILIKE`: case-insensitive প্যাটার্নে **না** মেলা।

**উদাহরণ:**

```python
print(names(User.email.not_ilike("%example%")))   # []  (করিমের NULL কোনো তুলনাতেই আসে না)
```

### `ColumnOperators.not_in()` { #columnoperators-not-in }

```python
ColumnOperators.not_in(other)
```

**ধরন:** মেথড

`NOT IN (...)`। সতর্কতা: কলামে NULL থাকলে সেই রো বাদ পড়ে (SQL-এর নিয়ম)।

**উদাহরণ:**

```python
print(names(User.id.not_in([1])))     # ['করিম', 'সুমি']
print(names(User.age.not_in([30])))   # ['করিম']  (সুমির age NULL, তাই বাদ)
```

### `ColumnOperators.not_like()` { #columnoperators-not-like }

```python
ColumnOperators.not_like(other, escape=None)
```

**ধরন:** মেথড

`NOT LIKE`।

**উদাহরণ:**

```python
print(names(User.name.not_like("র%")))   # ['করিম', 'সুমি']
```

### `ColumnOperators.notilike()` { #columnoperators-notilike }

```python
ColumnOperators.notilike(other, escape=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`not_ilike()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(names(User.name.notilike("র%")))   # ['করিম', 'সুমি']
```

### `ColumnOperators.notin_()` { #columnoperators-notin- }

```python
ColumnOperators.notin_(other)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`not_in()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(names(User.id.notin_([2, 3])))   # ['রহিম']
```

### `ColumnOperators.notlike()` { #columnoperators-notlike }

```python
ColumnOperators.notlike(other, escape=None)
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`not_like()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(names(User.name.notlike("%ম")))   # ['সুমি']
```

### `ColumnOperators.nulls_first()` { #columnoperators-nulls-first }

```python
ColumnOperators.nulls_first()
```

**ধরন:** মেথড

`ORDER BY`-তে NULL মানগুলো সবার আগে। সাধারণত `.desc().nulls_first()`-এর মতো চেইন করা হয়।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.age.asc().nulls_first())).all())   # ['সুমি', 'করিম', 'রহিম']
```

### `ColumnOperators.nulls_last()` { #columnoperators-nulls-last }

```python
ColumnOperators.nulls_last()
```

**ধরন:** মেথড

`ORDER BY`-তে NULL মানগুলো সবার শেষে (PostgreSQL-এ `DESC`-এর ডিফল্ট উল্টো, তাই কাজে লাগে)।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.age.desc().nulls_last())).all())   # ['রহিম', 'করিম', 'সুমি']
```

### `ColumnOperators.nullsfirst()` { #columnoperators-nullsfirst }

```python
ColumnOperators.nullsfirst()
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`nulls_first()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.age.nullsfirst())).first())   # সুমি
```

### `ColumnOperators.nullslast()` { #columnoperators-nullslast }

```python
ColumnOperators.nullslast()
```

**ধরন:** মেথড

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`nulls_last()`-এর পুরোনো নাম।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(User.age.desc().nullslast())).first())   # রহিম
```

### `ColumnOperators.op()` { #columnoperators-op }

```python
ColumnOperators.op(opstring, precedence=0, is_comparison=False, return_type=None, python_impl=None, operator_class=<OperatorClass.BASE: 2>, visit_name=None)
```

**ধরন:** মেথড

যেকোনো কাস্টম বা ডেটাবেস-নির্দিষ্ট **বাইনারি অপারেটর** বানায়: `col.op("অপারেটর")(মান)`। ফলাফল তুলনা (বুলিয়ান) হলে `bool_op()` বা `is_comparison=True` ভালো। প্যারামিটার: `precedence` (অগ্রাধিকার, বন্ধনী ঠিক করতে), `return_type` (ফলের টাইপ), `python_impl` (Python-এ একই হিসাব; ORM-এর in-memory মূল্যায়নের জন্য), আর ২.১-এ নতুন `operator_class` (কোন টাইপে বৈধ তার ইঙ্গিত) ও `visit_name` (ডায়ালেক্টের নিজস্ব কম্পাইলার মেথড বেছে নিতে)।

**উদাহরণ:**

```python
print(session.scalar(select(User.age.op("^")(2)).where(User.id == 2)))   # 625.0  (PostgreSQL-এ ^ মানে ঘাত)
expr = column("x").op("+", python_impl=lambda a, b: a + b)(column("y"))
print(expr.operator(5, 10))                                              # 15
```

### `ColumnOperators.operate()` { #columnoperators-operate }

```python
ColumnOperators.operate(op, *other, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সব অপারেটরের ভেতরের মূল হুক: প্রতিটি অপারেটর শেষ পর্যন্ত `operate(op, other)` ডাকে। কাস্টম comparator বা টাইপ বানাতে override করা হয়।

**উদাহরণ:**

```python
from sqlalchemy.sql import operators
print(User.age.operate(operators.gt, 20))   # users.age > :age_1
```

### `ColumnOperators.regexp_match()` { #columnoperators-regexp-match }

```python
ColumnOperators.regexp_match(pattern, flags=None)
```

**ধরন:** মেথড

রেগুলার এক্সপ্রেশন মিল। PostgreSQL-এ `~` (আর `flags="i"` দিলে `~*`), MySQL-এ `REGEXP`, SQLite-এ `REGEXP` (ফাংশন নিবন্ধন লাগে)।

**উদাহরণ:**

```python
print(names(User.email.regexp_match(r"^[a-z]+@")))          # ['রহিম']
print(names(User.email.regexp_match(r"^sumi", flags="i")))   # ['সুমি']
```

### `ColumnOperators.regexp_replace()` { #columnoperators-regexp-replace }

```python
ColumnOperators.regexp_replace(pattern, replacement, flags=None)
```

**ধরন:** মেথড

রেগুলার এক্সপ্রেশন দিয়ে স্ট্রিংয়ের অংশ বদলায় (`REGEXP_REPLACE`)। `flags="g"` দিলে PostgreSQL-এ সব মিল বদলায়।

**উদাহরণ:**

```python
print(session.scalar(select(User.email.regexp_replace(r"@.*", "@***")).where(User.id == 1)))   # rahim@***
```

### `ColumnOperators.reverse_operate()` { #columnoperators-reverse-operate }

```python
ColumnOperators.reverse_operate(op, other, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`operate()`-এর উল্টো দিকের রূপ: Python মান বাম দিকে থাকলে (যেমন `5 + User.age`) ডাকা হয়।

**উদাহরণ:**

```python
print(5 + User.age)   # :age_1 + users.age
```

### `ColumnOperators.startswith()` { #columnoperators-startswith }

```python
ColumnOperators.startswith(other, escape=None, autoescape=False)
```

**ধরন:** মেথড

স্ট্রিং এই অংশ দিয়ে শুরু হয় কি না (`LIKE x || '%'`)। ইনডেক্স ব্যবহার করতে পারে বলে `contains()`-এর চেয়ে দ্রুত।

**উদাহরণ:**

```python
print(names(User.email.startswith("rahim")))   # ['রহিম']
```

### `ColumnOperators.timetuple` { #columnoperators-timetuple }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সবসময় `None`। Python-এর `datetime` অবজেক্ট বাম দিকে থাকলে (`datetime.now() > User.created`) যাতে Python নিজে তুলনা করে এরর না দিয়ে SQLAlchemy-কে সুযোগ দেয়, সেই কৌশলের অংশ।

## `QueryableAttribute` { #queryableattribute }

```python
from sqlalchemy.orm import QueryableAttribute, InstrumentedAttribute
```

মডেল ক্লাসের অ্যাট্রিবিউট (`User.name`, `User.addresses`) আসলে এই ক্লাসের অবজেক্ট (সঠিকভাবে বললে এর সাবক্লাস `InstrumentedAttribute`, যার সদস্য হুবহু একই)। তাই এরা কলামের সব অপারেটর জানে (উপরের `ColumnOperators`), আর সাথে ORM-এর নিজস্ব কিছু সুবিধা: রিলেশনশিপে `any()`, `has()`, `of_type()`, `and_()`, আর অ্যাট্রিবিউটের তথ্য (`key`, `class_`, `property`)।

**উদাহরণ:**

```python
print(type(User.name).__name__, isinstance(User.name, QueryableAttribute))   # InstrumentedAttribute True
print(User.name.key, User.name.class_.__name__)                             # name User
print(names(User.addresses.any(Address.city == "চট্টগ্রাম")))               # ['রহিম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #queryableattribute-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_to_entity()`](#queryableattribute-adapt-to-entity) | মেথড (internal) | একটি `aliased()` এন্টিটির জন্য এই অ্যাট্রিবিউটের কপি বানায়। |
| [`adapter`](#queryableattribute-adapter) | প্রপার্টি (internal) | alias করা রূপে কলাম-এক্সপ্রেশন বদলানোর ভেতরের ফাংশন। |
| [`allows_lambda`](#queryableattribute-allows-lambda) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না। |
| [`and_()`](#queryableattribute-and-) | মেথড | রিলেশনশিপ ধরে JOIN করার সময় ON শর্তে **অতিরিক্ত শর্ত** জুড়ে দেয়। |
| [`any()`](#queryableattribute-any) | মেথড | **কালেকশন রিলেশনশিপে** (one-to-many, many-to-many): "অন্তত একটি সম্পর্কিত রো শর্ত মানে" → `EXISTS (SELECT ...)`। |
| [`any_op()`](#queryableattribute-any-op) | স্ট্যাটিক মেথড (internal) | `any()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড), কাস্টম comparator-এ ব্যবহারের জন্য। |
| [`class_`](#queryableattribute-class-) | অ্যাট্রিবিউট | এই অ্যাট্রিবিউট যে ক্লাসের। |
| [`comparator`](#queryableattribute-comparator) | অ্যাট্রিবিউট (internal) | অপারেটরগুলো আসলে যে `Comparator` অবজেক্টে যায় (কলামে `ColumnProperty.Comparator`, রিলেশনশিপে `Relationship.Comparator`)। |
| [`expression`](#queryableattribute-expression) | অ্যাট্রিবিউট | এই অ্যাট্রিবিউটের পেছনের আসল SQL এক্সপ্রেশন (সাধারণত টেবিলের `Column`, বা `column_property()`-এর এক্সপ্রেশন), মডেলের লেবেলসহ। |
| [`extension_type`](#queryableattribute-extension-type) | অ্যাট্রিবিউট (internal) | inspection API-র টাইপ-চিহ্ন (hybrid বা association proxy নয়, সাধারণ অ্যাট্রিবিউট)। |
| [`get_history()`](#queryableattribute-get-history) | মেথড | একটি অবজেক্টে এই অ্যাট্রিবিউটের অ-সংরক্ষিত পরিবর্তন: `(added, unchanged, deleted)`। |
| [`has()`](#queryableattribute-has) | মেথড | **একক রিলেশনশিপে** (many-to-one, one-to-one): "সম্পর্কিত অবজেক্টটি শর্ত মানে" → `EXISTS`। |
| [`has_op()`](#queryableattribute-has-op) | স্ট্যাটিক মেথড (internal) | `has()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড)। |
| [`hasparent()`](#queryableattribute-hasparent) | মেথড (internal) | ভেতরের: একটি অবজেক্ট এই রিলেশনশিপের মাধ্যমে কোনো প্যারেন্টের সাথে যুক্ত কি না (delete-orphan হিসাবে ব্যবহার হয়)। |
| [`impl`](#queryableattribute-impl) | অ্যাট্রিবিউট (internal) | অ্যাট্রিবিউটের মান রাখা/পড়ার ভেতরের ব্যবস্থা (`AttributeImpl`)। |
| [`info`](#queryableattribute-info) | প্রপার্টি | অ্যাট্রিবিউটের সাথে যুক্ত নিজের মেটাডেটার dict (`mapped_column(info={...})` বা `relationship(info=...)` থেকে)। |
| [`inherit_cache`](#queryableattribute-inherit-cache) | অ্যাট্রিবিউট (internal) | ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ। |
| [`is_aliased_class`](#queryableattribute-is-aliased-class) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_attribute`](#queryableattribute-is-attribute) | অ্যাট্রিবিউট | `inspect()`-এর ফল একটি অ্যাট্রিবিউট কি না: এখানে `True`। |
| [`is_bundle`](#queryableattribute-is-bundle) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_clause_element`](#queryableattribute-is-clause-element) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`; অ্যাট্রিবিউট নিজে SQL এলিমেন্ট নয়, তার `expression` হলো)। |
| [`is_instance`](#queryableattribute-is-instance) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_mapper`](#queryableattribute-is-mapper) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_property`](#queryableattribute-is-property) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`is_selectable`](#queryableattribute-is-selectable) | অ্যাট্রিবিউট (internal) | inspection টাইপ-ফ্ল্যাগ (`False`)। |
| [`key`](#queryableattribute-key) | অ্যাট্রিবিউট | অ্যাট্রিবিউটের নাম। |
| [`label()`](#queryableattribute-label) | মেথড | এক্সপ্রেশনটিকে একটি নাম দেয় (`AS নাম`), রেজাল্টের রো-তে সেই নামে পাওয়া যায়। |
| [`of_type()`](#queryableattribute-of-type) | মেথড | inheritance থাকা রিলেশনশিপকে একটি নির্দিষ্ট সাবক্লাস (বা `aliased()` / `with_polymorphic()` রূপ) হিসেবে ধরে। |
| [`of_type_op()`](#queryableattribute-of-type-op) | স্ট্যাটিক মেথড (internal) | `of_type()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড)। |
| [`params()`](#queryableattribute-params) | মেথড (internal) | অ্যাট্রিবিউটে প্রযোজ্য নয় (ডাকলে এরর); `ClauseElement`-এর `params()` এখানে বন্ধ রাখা হয়েছে। |
| [`parent`](#queryableattribute-parent) | অ্যাট্রিবিউট | এই অ্যাট্রিবিউট যে mapper বা aliased এন্টিটির inspection অবজেক্টের অংশ। |
| [`prop`](#queryableattribute-prop) | অ্যাট্রিবিউট | `property`-এর ছোট নাম: পেছনের `MapperProperty`। |
| [`property`](#queryableattribute-property) | অ্যাট্রিবিউট | এই অ্যাট্রিবিউটের পেছনের `MapperProperty`: কলাম হলে `ColumnProperty`, রিলেশনশিপ হলে `RelationshipProperty`। |
| [`unique_params()`](#queryableattribute-unique-params) | মেথড (internal) | অ্যাট্রিবিউটে প্রযোজ্য নয় (ডাকলে এরর)। |
| [`uses_inspection`](#queryableattribute-uses-inspection) | অ্যাট্রিবিউট (internal) | ভেতরের ফ্ল্যাগ। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৭টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `QueryableAttribute`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](#columnoperators-all-) · [`any_()`](#columnoperators-any-) · [`asc()`](#columnoperators-asc) · [`between()`](#columnoperators-between) · [`bitwise_and()`](#columnoperators-bitwise-and) · [`bitwise_lshift()`](#columnoperators-bitwise-lshift) · [`bitwise_not()`](#columnoperators-bitwise-not) · [`bitwise_or()`](#columnoperators-bitwise-or) · [`bitwise_rshift()`](#columnoperators-bitwise-rshift) · [`bitwise_xor()`](#columnoperators-bitwise-xor) · [`bool_op()`](#columnoperators-bool-op) · [`collate()`](#columnoperators-collate) · [`concat()`](#columnoperators-concat) · [`contains()`](#columnoperators-contains) · [`desc()`](#columnoperators-desc) · [`distinct()`](#columnoperators-distinct) · [`endswith()`](#columnoperators-endswith) · [`icontains()`](#columnoperators-icontains) · [`iendswith()`](#columnoperators-iendswith) · [`ilike()`](#columnoperators-ilike) · [`in_()`](#columnoperators-in-) · [`is_()`](#columnoperators-is-) · [`is_distinct_from()`](#columnoperators-is-distinct-from) · [`is_not()`](#columnoperators-is-not) · [`is_not_distinct_from()`](#columnoperators-is-not-distinct-from) · [`isnot()`](#columnoperators-isnot) · [`isnot_distinct_from()`](#columnoperators-isnot-distinct-from) · [`istartswith()`](#columnoperators-istartswith) · [`like()`](#columnoperators-like) · [`match()`](#columnoperators-match) · [`not_ilike()`](#columnoperators-not-ilike) · [`not_in()`](#columnoperators-not-in) · [`not_like()`](#columnoperators-not-like) · [`notilike()`](#columnoperators-notilike) · [`notin_()`](#columnoperators-notin-) · [`notlike()`](#columnoperators-notlike) · [`nulls_first()`](#columnoperators-nulls-first) · [`nulls_last()`](#columnoperators-nulls-last) · [`nullsfirst()`](#columnoperators-nullsfirst) · [`nullslast()`](#columnoperators-nullslast) · [`op()`](#columnoperators-op) · [`operate()`](#columnoperators-operate) · [`regexp_match()`](#columnoperators-regexp-match) · [`regexp_replace()`](#columnoperators-regexp-replace) · [`reverse_operate()`](#columnoperators-reverse-operate) · [`startswith()`](#columnoperators-startswith) · [`timetuple`](#columnoperators-timetuple)

///

### `QueryableAttribute.adapt_to_entity()` { #queryableattribute-adapt-to-entity }

```python
QueryableAttribute.adapt_to_entity(adapt_to_entity)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

একটি `aliased()` এন্টিটির জন্য এই অ্যাট্রিবিউটের কপি বানায়। `aliased(User).name` লিখলে ভেতরে এটিই ঘটে।

### `QueryableAttribute.adapter` { #queryableattribute-adapter }

**ধরন:** প্রপার্টি

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

alias করা রূপে কলাম-এক্সপ্রেশন বদলানোর ভেতরের ফাংশন।

### `QueryableAttribute.allows_lambda` { #queryableattribute-allows-lambda }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ: lambda স্টেটমেন্টে ব্যবহারযোগ্য কি না।

### `QueryableAttribute.and_()` { #queryableattribute-and- }

```python
QueryableAttribute.and_(*clauses)
```

**ধরন:** মেথড

রিলেশনশিপ ধরে JOIN করার সময় ON শর্তে **অতিরিক্ত শর্ত** জুড়ে দেয়। loader অপশনেও কাজ করে: শুধু শর্ত মানা সম্পর্কিত অবজেক্ট লোড হবে।

**উদাহরণ:**

```python
stmt = select(User.name, Address.city).join(User.addresses.and_(Address.city == "ঢাকা")).order_by(User.id)
print(session.execute(stmt).all())   # [('রহিম', 'ঢাকা'), ('সুমি', 'ঢাকা')]
u = session.scalars(select(User).options(selectinload(User.addresses.and_(Address.city != "ঢাকা")))
                    .where(User.id == 1)).one()
print([a.city for a in u.addresses])   # ['চট্টগ্রাম']
```

### `QueryableAttribute.any()` { #queryableattribute-any }

```python
QueryableAttribute.any(criterion=None, **kwargs)
```

**ধরন:** মেথড

**কালেকশন রিলেশনশিপে** (one-to-many, many-to-many): "অন্তত একটি সম্পর্কিত রো শর্ত মানে" → `EXISTS (SELECT ...)`। শর্ত না দিলে মানে "অন্তত একটি আছে"। keyword দিয়েও শর্ত দেওয়া যায়: `any(city="ঢাকা")`।

**উদাহরণ:**

```python
print(names(User.addresses.any()))                 # ['রহিম', 'সুমি']
print(names(~User.addresses.any()))                # ['করিম']  (কোনো ঠিকানা নেই)
print(names(User.addresses.any(city="চট্টগ্রাম")))  # ['রহিম']
```

### `QueryableAttribute.any_op()` { #queryableattribute-any-op }

```python
QueryableAttribute.any_op(a, b, **kwargs)
```

**ধরন:** স্ট্যাটিক মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`any()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড), কাস্টম comparator-এ ব্যবহারের জন্য।

### `QueryableAttribute.class_` { #queryableattribute-class- }

**ধরন:** অ্যাট্রিবিউট

এই অ্যাট্রিবিউট যে ক্লাসের।

**উদাহরণ:**

```python
print(Address.city.class_.__name__)   # Address
```

### `QueryableAttribute.comparator` { #queryableattribute-comparator }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অপারেটরগুলো আসলে যে `Comparator` অবজেক্টে যায় (কলামে `ColumnProperty.Comparator`, রিলেশনশিপে `Relationship.Comparator`)।

### `QueryableAttribute.expression` { #queryableattribute-expression }

**ধরন:** অ্যাট্রিবিউট

এই অ্যাট্রিবিউটের পেছনের আসল SQL এক্সপ্রেশন (সাধারণত টেবিলের `Column`, বা `column_property()`-এর এক্সপ্রেশন), মডেলের লেবেলসহ।

**উদাহরণ:**

```python
print(User.name.expression)   # users.name
```

### `QueryableAttribute.extension_type` { #queryableattribute-extension-type }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection API-র টাইপ-চিহ্ন (hybrid বা association proxy নয়, সাধারণ অ্যাট্রিবিউট)।

### `QueryableAttribute.get_history()` { #queryableattribute-get-history }

```python
QueryableAttribute.get_history(instance, passive=symbol('PASSIVE_OFF'))
```

**ধরন:** মেথড

একটি অবজেক্টে এই অ্যাট্রিবিউটের অ-সংরক্ষিত পরিবর্তন: `(added, unchanged, deleted)`। সাধারণত `inspect(obj).attrs.name.history` ব্যবহার সহজ।

**উদাহরণ:**

```python
u = session.get(User, 2)
u.name = "করিম উদ্দিন"
print(User.name.get_history(u))   # History(added=['করিম উদ্দিন'], unchanged=(), deleted=['করিম'])
```

### `QueryableAttribute.has()` { #queryableattribute-has }

```python
QueryableAttribute.has(criterion=None, **kwargs)
```

**ধরন:** মেথড

**একক রিলেশনশিপে** (many-to-one, one-to-one): "সম্পর্কিত অবজেক্টটি শর্ত মানে" → `EXISTS`। কালেকশনে `any()`, একক অবজেক্টে `has()`।

**উদাহরণ:**

```python
stmt = select(Address.city).where(Address.user.has(User.age > 28)).order_by(Address.id)
print(session.scalars(stmt).all())   # ['ঢাকা', 'চট্টগ্রাম']
```

### `QueryableAttribute.has_op()` { #queryableattribute-has-op }

```python
QueryableAttribute.has_op(left, other, **kwargs)
```

**ধরন:** স্ট্যাটিক মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`has()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড)।

### `QueryableAttribute.hasparent()` { #queryableattribute-hasparent }

```python
QueryableAttribute.hasparent(state, optimistic=False)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের: একটি অবজেক্ট এই রিলেশনশিপের মাধ্যমে কোনো প্যারেন্টের সাথে যুক্ত কি না (delete-orphan হিসাবে ব্যবহার হয়)।

### `QueryableAttribute.impl` { #queryableattribute-impl }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটের মান রাখা/পড়ার ভেতরের ব্যবস্থা (`AttributeImpl`)।

### `QueryableAttribute.info` { #queryableattribute-info }

**ধরন:** প্রপার্টি

অ্যাট্রিবিউটের সাথে যুক্ত নিজের মেটাডেটার dict (`mapped_column(info={...})` বা `relationship(info=...)` থেকে)। ফর্ম বা সিরিয়ালাইজার জেনারেটরে কাজে লাগে।

**উদাহরণ:**

```python
print(User.name.info)   # {}
```

### `QueryableAttribute.inherit_cache` { #queryableattribute-inherit-cache }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ক্যাশ-key ব্যবস্থার ভেতরের ফ্ল্যাগ।

### `QueryableAttribute.is_aliased_class` { #queryableattribute-is-aliased-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.is_attribute` { #queryableattribute-is-attribute }

**ধরন:** অ্যাট্রিবিউট

`inspect()`-এর ফল একটি অ্যাট্রিবিউট কি না: এখানে `True`।

**উদাহরণ:**

```python
print(User.name.is_attribute)   # True
```

### `QueryableAttribute.is_bundle` { #queryableattribute-is-bundle }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.is_clause_element` { #queryableattribute-is-clause-element }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`; অ্যাট্রিবিউট নিজে SQL এলিমেন্ট নয়, তার `expression` হলো)।

### `QueryableAttribute.is_instance` { #queryableattribute-is-instance }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.is_mapper` { #queryableattribute-is-mapper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.is_property` { #queryableattribute-is-property }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.is_selectable` { #queryableattribute-is-selectable }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

inspection টাইপ-ফ্ল্যাগ (`False`)।

### `QueryableAttribute.key` { #queryableattribute-key }

**ধরন:** অ্যাট্রিবিউট

অ্যাট্রিবিউটের নাম।

**উদাহরণ:**

```python
print(User.addresses.key)   # addresses
```

### `QueryableAttribute.label()` { #queryableattribute-label }

```python
QueryableAttribute.label(name)
```

**ধরন:** মেথড

এক্সপ্রেশনটিকে একটি নাম দেয় (`AS নাম`), রেজাল্টের রো-তে সেই নামে পাওয়া যায়।

**উদাহরণ:**

```python
row = session.execute(select(User.name.label("full_name")).where(User.id == 1)).one()
print(row.full_name)   # রহিম
```

### `QueryableAttribute.of_type()` { #queryableattribute-of-type }

```python
QueryableAttribute.of_type(entity)
```

**ধরন:** মেথড

inheritance থাকা রিলেশনশিপকে একটি নির্দিষ্ট সাবক্লাস (বা `aliased()` / `with_polymorphic()` রূপ) হিসেবে ধরে। ফলে JOIN বা `any()`-এর শর্তে সাবক্লাসের কলাম (যেমন `Engineer.lang`) ব্যবহার করা যায়।

**উদাহরণ:**

```python
stmt = select(Company.name).where(Company.employees.of_type(Engineer).any(Engineer.lang == "Python"))
print(session.scalars(stmt).all())   # ['টেক লিমিটেড']
stmt = select(Company.name, Engineer.name).join(Company.employees.of_type(Engineer))
print(session.execute(stmt).all())   # [('টেক লিমিটেড', 'আলিফ')]
```

### `QueryableAttribute.of_type_op()` { #queryableattribute-of-type-op }

```python
QueryableAttribute.of_type_op(a, class_)
```

**ধরন:** স্ট্যাটিক মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`of_type()`-এর পেছনের অপারেটর ফাংশন (স্ট্যাটিক মেথড)।

### `QueryableAttribute.params()` { #queryableattribute-params }

```python
QueryableAttribute.params(*optionaldict, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটে প্রযোজ্য নয় (ডাকলে এরর); `ClauseElement`-এর `params()` এখানে বন্ধ রাখা হয়েছে।

### `QueryableAttribute.parent` { #queryableattribute-parent }

**ধরন:** অ্যাট্রিবিউট

এই অ্যাট্রিবিউট যে mapper বা aliased এন্টিটির inspection অবজেক্টের অংশ।

**উদাহরণ:**

```python
print(User.name.parent.class_.__name__)   # User
print(aliased(User, name="u2").name.parent.name)   # u2
```

### `QueryableAttribute.prop` { #queryableattribute-prop }

**ধরন:** অ্যাট্রিবিউট

`property`-এর ছোট নাম: পেছনের `MapperProperty`।

**উদাহরণ:**

```python
print(User.addresses.prop is User.addresses.property)   # True
```

### `QueryableAttribute.property` { #queryableattribute-property }

**ধরন:** অ্যাট্রিবিউট

এই অ্যাট্রিবিউটের পেছনের `MapperProperty`: কলাম হলে `ColumnProperty`, রিলেশনশিপ হলে `RelationshipProperty`। এখান থেকে রিলেশনশিপের দিক, লক্ষ্য মডেল ইত্যাদি জানা যায়।

**উদাহরণ:**

```python
rel = User.addresses.property
print(rel.mapper.class_.__name__, rel.direction.name)   # Address ONETOMANY
```

### `QueryableAttribute.unique_params()` { #queryableattribute-unique-params }

```python
QueryableAttribute.unique_params(*optionaldict, **kwargs)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

অ্যাট্রিবিউটে প্রযোজ্য নয় (ডাকলে এরর)।

### `QueryableAttribute.uses_inspection` { #queryableattribute-uses-inspection }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ফ্ল্যাগ।

/// check | সংক্ষেপে মনে রাখুন

* শর্ত জোড়া: `&` / `and_()`, `|` / `or_()`, `~` / `not_()`; প্রতিটি শর্ত বন্ধনীতে।
* NULL: `is_(None)`, `is_not(None)`; NULL-নিরাপদ তুলনা: `is_distinct_from()`।
* স্ট্রিং: `like()` / `ilike()`, `startswith()`, `contains()`, `icontains()`; ইউজার ইনপুটে `autoescape=True`।
* তালিকা: `in_()`, `not_in()`; অ্যারে: `any_()`, `all_()`।
* রিলেশনশিপে শর্ত: কালেকশনে `any()`, একক অবজেক্টে `has()`; JOIN-এ বাড়তি শর্ত `.and_()`; সাবক্লাস `.of_type()`।
* ডেটাবেস-নির্দিষ্ট অপারেটর: `op()`, তুলনা হলে `bool_op()`।

///
