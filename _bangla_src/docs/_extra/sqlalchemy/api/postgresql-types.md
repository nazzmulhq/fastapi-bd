# PostgreSQL টাইপ API: Range, ENUM, DOMAIN, INET, BIT, INTERVAL … { #api-postgresql-types }

/// note | এই পেজে যা আছে

`sqlalchemy.dialects.postgresql`-এর **সব টাইপ** (JSON/JSONB, ARRAY, HSTORE আছে [PostgreSQL API পেজে](postgresql.md)):

* **Range:** Python-এর `Range` আর `MultiRange` অবজেক্ট, range কলামের অপারেটর, আর ১২টি টাইপ `INT4RANGE` … `TSTZMULTIRANGE`।
* **নামযুক্ত টাইপ:** `ENUM`, `DOMAIN`, তাদের মূল `NamedType`, DDL কনস্ট্রাক্ট `CreateEnumType` / `DropEnumType` / `CreateDomainType` / `DropDomainType`, আর PostgreSQL-এর `Inspector` (`get_enums()`, `get_domains()` …)।
* **নেটওয়ার্ক:** `INET`, `CIDR`, `MACADDR`, `MACADDR8`।
* **অন্যান্য:** `CITEXT`, `MONEY`, `OID`, `REGCLASS`, `REGCONFIG`, `TSQUERY`, `TSVECTOR`, `BIT` আর ২.১-এর নতুন `BitString`, `BYTEA`, `INTERVAL`, `TIMESTAMP`, `TIME`।
* PostgreSQL মডিউল থেকে ইমপোর্ট করা যায় এমন সাধারণ টাইপের (`INTEGER`, `UUID` …) তালিকা পেজের শেষে।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
from sqlalchemy.dialects.postgresql import INT4RANGE, Range

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    room: Mapped[str]
    slot: Mapped[Range[int]] = mapped_column(INT4RANGE)

engine = create_engine("postgresql+psycopg://postgres@127.0.0.1/apiref",
                       connect_args={"prepare_threshold": None})
```

* ডেটা: রুম `A` স্লট `[1,5)`, রুম `B` স্লট `[5,10)`, রুম `C` স্লট `[20,30)`।
* `rooms(শর্ত)`: শর্ত মেলে এমন রুমগুলোর নাম। `rt(টাইপ, মান)`: অস্থায়ী টেবিলে মান লিখে আবার পড়ে যা আসে (round-trip)। `pgt(টাইপ)`: `CREATE TABLE`-এ টাইপটি কী নামে বসে। `ddl(stmt)`: DDL-এর SQL। `user_types()`: ডেটাবেসে থাকা ENUM/DOMAIN টাইপের নাম।
* ড্রাইভার **psycopg 3** (২.১-এ `postgresql://` লিখলে এটাই ডিফল্ট)। `prepare_threshold: None` শুধু এই পরীক্ষার জন্য: একই নামের টেবিল বারবার ভিন্ন টাইপে বানালে psycopg 3-এর প্রস্তুত-করা কুয়েরি "cached plan must not change result type" এরর দেয়।
* PostgreSQL 16-এ চালিয়ে দেখা।

///

## Range: Python-এর পরিসর অবজেক্ট { #range-group }

## `Range` { #range }

```python
from sqlalchemy.dialects.postgresql import Range
```

PostgreSQL range-এর (যেমন `[1,5)`) Python রূপ। range কলাম থেকে পড়লে এটাই আসে, আর লিখতেও এটা দিন। এটি একটি সাধারণ (frozen) dataclass: তুলনা `==` চলে, dict-এর key হতে পারে।

`bounds` দুই অক্ষরের: `[` / `]` মানে প্রান্ত **ভেতরে** (inclusive), `(` / `)` মানে **বাইরে** (exclusive)। ডিফল্ট `"[)"`: নিচেরটা ভেতরে, ওপরেরটা বাইরে। `None` প্রান্ত মানে অসীম। পূর্ণসংখ্যা/তারিখের (discrete) range PostgreSQL নিজে `[)` রূপে বদলে রাখে: `[1,10]` লিখলে ফেরত আসে `[1,11)`।

নিচের মেথডগুলো (`contains()`, `overlaps()` …) **Python-এই** হিসাব করে, ডেটাবেসে যায় না। কুয়েরির ভেতরে একই কাজের জন্য কলামের [অপারেটর](#range-comparator) ব্যবহার করুন।

**উদাহরণ:**

```python
r = Range(1, 5)
print(r, r.contains(3), r.contains(5))   # [1,5) True False
print(rt(INT4RANGE, Range(1, 10, bounds="[]")))   # [1,11)  (PostgreSQL discrete range-কে [) রূপে রাখে)
print(session.get(Booking, 1).slot)   # [1,5)
```

### কনস্ট্রাক্টরের প্যারামিটার { #range-params }

```python
Range(lower=None, upper=None, *, bounds='[)', empty=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `lower` | নিচের প্রান্ত (`None` = অসীম)। |
| `upper` | ওপরের প্রান্ত (`None` = অসীম)। |
| `bounds` | প্রান্ত ভেতরে না বাইরে: `"[)"` (ডিফল্ট), `"[]"`, `"(]"`, `"()"`। |
| `empty` | `True` দিলে খালি range (`empty`), কোনো মান নেই। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #range-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adjacent_to()`](#range-adjacent-to) | মেথড | দুটি range ঠিক গায়ে গায়ে লাগানো কি না (ফাঁক নেই, মিলও নেই)। |
| [`bounds`](#range-bounds) | অ্যাট্রিবিউট | প্রান্তের ধরন, যেমন `"[)"`। |
| [`contained_by()`](#range-contained-by) | মেথড | এই range পুরোটা `other`-এর ভেতরে কি না। |
| [`contains()`](#range-contains) | মেথড | একটি **মান** বা আরেকটি **range** এর ভেতরে কি না। |
| [`difference()`](#range-difference) | মেথড | এই range থেকে `other` বাদ দিয়ে যা থাকে (`-`)। |
| [`empty`](#range-empty) | অ্যাট্রিবিউট | খালি range কি না (`Range(empty=True)` বা ডেটাবেসের `empty`)। |
| [`intersection()`](#range-intersection) | মেথড | দুটি range-এর সাধারণ অংশ (`*`)। |
| [`is_empty`](#range-is-empty) | প্রপার্টি | `empty`-এর আরেক নাম। |
| [`isempty`](#range-isempty) | প্রপার্টি | `empty`-এর আরেক নাম (PostgreSQL ফাংশন `isempty()`-এর মতো নাম)। |
| [`lower`](#range-lower) | অ্যাট্রিবিউট | নিচের প্রান্তের মান (`None` হলে অসীম)। |
| [`lower_inc`](#range-lower-inc) | প্রপার্টি | নিচের প্রান্ত ভেতরে (`[`) কি না। |
| [`lower_inf`](#range-lower-inf) | প্রপার্টি | নিচের দিক অসীম কি না (`lower` `None` আর range খালি নয়)। |
| [`not_extend_left_of()`](#range-not-extend-left-of) | মেথড | এই range `other`-এর বাঁ দিকে ছড়ায় না, অর্থাৎ এর শুরু `other`-এর শুরুর সমান বা পরে। |
| [`not_extend_right_of()`](#range-not-extend-right-of) | মেথড | এই range `other`-এর ডান দিকে ছড়ায় না, অর্থাৎ এর শেষ `other`-এর শেষের সমান বা আগে। |
| [`overlaps()`](#range-overlaps) | মেথড | কোনো সাধারণ বিন্দু আছে কি না। |
| [`strictly_left_of()`](#range-strictly-left-of) | মেথড | পুরোটা `other`-এর বাঁ দিকে কি না (কোনো মিল নেই)। |
| [`strictly_right_of()`](#range-strictly-right-of) | মেথড | পুরোটা `other`-এর ডান দিকে কি না। |
| [`union()`](#range-union) | মেথড | দুটি range জোড়া (`+`)। |
| [`upper`](#range-upper) | অ্যাট্রিবিউট | ওপরের প্রান্তের মান (`None` হলে অসীম)। |
| [`upper_inc`](#range-upper-inc) | প্রপার্টি | ওপরের প্রান্ত ভেতরে (`]`) কি না। |
| [`upper_inf`](#range-upper-inf) | প্রপার্টি | ওপরের দিক অসীম কি না। |

### `Range.adjacent_to()` { #range-adjacent-to }

```python
Range.adjacent_to(other)
```

**ধরন:** মেথড

দুটি range ঠিক গায়ে গায়ে লাগানো কি না (ফাঁক নেই, মিলও নেই)। PostgreSQL-এর `-|-`।

**উদাহরণ:**

```python
print(Range(1, 5).adjacent_to(Range(5, 8)), Range(1, 5).adjacent_to(Range(6, 8)))   # True False
```

### `Range.bounds` { #range-bounds }

**ধরন:** অ্যাট্রিবিউট

প্রান্তের ধরন, যেমন `"[)"`।

**উদাহরণ:**

```python
print(Range(1, 5).bounds, Range(1, 5, bounds="(]").bounds)   # [) (]
```

### `Range.contained_by()` { #range-contained-by }

```python
Range.contained_by(other)
```

**ধরন:** মেথড

এই range পুরোটা `other`-এর ভেতরে কি না। PostgreSQL-এর `<@`।

**উদাহরণ:**

```python
print(Range(2, 3).contained_by(Range(1, 5)))   # True
```

### `Range.contains()` { #range-contains }

```python
Range.contains(value)
```

**ধরন:** মেথড

একটি **মান** বা আরেকটি **range** এর ভেতরে কি না। PostgreSQL-এর `@>`।

**উদাহরণ:**

```python
print(Range(1, 5).contains(4), Range(1, 5).contains(Range(2, 3)), Range(1, 5).contains(Range(4, 9)))   # True True False
```

### `Range.difference()` { #range-difference }

```python
Range.difference(other)
```

**ধরন:** মেথড

এই range থেকে `other` বাদ দিয়ে যা থাকে (`-`)। ফল দুই টুকরো হলে (মাঝখান থেকে কাটা) `ValueError`।

**উদাহরণ:**

```python
print(Range(1, 5).difference(Range(3, 8)))   # [1,3)
try:
    Range(1, 8).difference(Range(3, 5))
except ValueError as e:
    print(e)   # Subtracting a strictly inner range is not implemented
```

### `Range.empty` { #range-empty }

**ধরন:** অ্যাট্রিবিউট

খালি range কি না (`Range(empty=True)` বা ডেটাবেসের `empty`)।

**উদাহরণ:**

```python
print(Range(empty=True).empty, rt(INT4RANGE, Range(3, 3)).empty)   # True True  ([3,3) খালি)
```

### `Range.intersection()` { #range-intersection }

```python
Range.intersection(other)
```

**ধরন:** মেথড

দুটি range-এর সাধারণ অংশ (`*`)।

**উদাহরণ:**

```python
print(Range(1, 5).intersection(Range(3, 8)))   # [3,5)
```

### `Range.is_empty` { #range-is-empty }

**ধরন:** প্রপার্টি

`empty`-এর আরেক নাম।

**উদাহরণ:**

```python
print(Range(empty=True).is_empty)   # True
```

### `Range.isempty` { #range-isempty }

**ধরন:** প্রপার্টি

`empty`-এর আরেক নাম (PostgreSQL ফাংশন `isempty()`-এর মতো নাম)।

**উদাহরণ:**

```python
print(Range(1, 2).isempty)   # False
```

### `Range.lower` { #range-lower }

**ধরন:** অ্যাট্রিবিউট

নিচের প্রান্তের মান (`None` হলে অসীম)।

**উদাহরণ:**

```python
print(Range(1, 5).lower, Range(None, 5).lower)   # 1 None
```

### `Range.lower_inc` { #range-lower-inc }

**ধরন:** প্রপার্টি

নিচের প্রান্ত ভেতরে (`[`) কি না।

**উদাহরণ:**

```python
print(Range(1, 5).lower_inc, Range(1, 5, bounds="(]").lower_inc)   # True False
```

### `Range.lower_inf` { #range-lower-inf }

**ধরন:** প্রপার্টি

নিচের দিক অসীম কি না (`lower` `None` আর range খালি নয়)।

**উদাহরণ:**

```python
print(Range(None, 5).lower_inf)   # True
```

### `Range.not_extend_left_of()` { #range-not-extend-left-of }

```python
Range.not_extend_left_of(other)
```

**ধরন:** মেথড

এই range `other`-এর বাঁ দিকে ছড়ায় না, অর্থাৎ এর শুরু `other`-এর শুরুর সমান বা পরে। PostgreSQL-এর `&>`।

**উদাহরণ:**

```python
print(Range(3, 5).not_extend_left_of(Range(1, 4)), Range(0, 5).not_extend_left_of(Range(1, 4)))   # True False
```

### `Range.not_extend_right_of()` { #range-not-extend-right-of }

```python
Range.not_extend_right_of(other)
```

**ধরন:** মেথড

এই range `other`-এর ডান দিকে ছড়ায় না, অর্থাৎ এর শেষ `other`-এর শেষের সমান বা আগে। PostgreSQL-এর `&<`।

**উদাহরণ:**

```python
print(Range(1, 5).not_extend_right_of(Range(0, 5)), Range(1, 6).not_extend_right_of(Range(0, 5)))   # True False
```

### `Range.overlaps()` { #range-overlaps }

```python
Range.overlaps(other)
```

**ধরন:** মেথড

কোনো সাধারণ বিন্দু আছে কি না। PostgreSQL-এর `&&`। বুকিং-এর সময় মিলে যাচ্ছে কি না দেখতে সবচেয়ে বেশি লাগে।

**উদাহরণ:**

```python
print(Range(1, 5).overlaps(Range(4, 9)), Range(1, 5).overlaps(Range(5, 9)))   # True False
```

### `Range.strictly_left_of()` { #range-strictly-left-of }

```python
Range.strictly_left_of(other)
```

**ধরন:** মেথড

পুরোটা `other`-এর বাঁ দিকে কি না (কোনো মিল নেই)। PostgreSQL-এর `<<`।

**উদাহরণ:**

```python
print(Range(1, 5).strictly_left_of(Range(5, 6)))   # True
```

### `Range.strictly_right_of()` { #range-strictly-right-of }

```python
Range.strictly_right_of(other)
```

**ধরন:** মেথড

পুরোটা `other`-এর ডান দিকে কি না। PostgreSQL-এর `>>`।

**উদাহরণ:**

```python
print(Range(1, 5).strictly_right_of(Range(-3, 1)))   # True
```

### `Range.union()` { #range-union }

```python
Range.union(other)
```

**ধরন:** মেথড

দুটি range জোড়া (`+`)। মাঝে ফাঁক থাকলে (মিল বা গায়ে লাগা নেই) `ValueError`, কারণ ফল একটি range হয় না।

**উদাহরণ:**

```python
print(Range(1, 5).union(Range(5, 8)))   # [1,8)
try:
    Range(1, 3).union(Range(5, 8))
except ValueError as e:
    print(e)   # Adding non-overlapping and non-adjacent ranges is not implemented
```

### `Range.upper` { #range-upper }

**ধরন:** অ্যাট্রিবিউট

ওপরের প্রান্তের মান (`None` হলে অসীম)।

**উদাহরণ:**

```python
print(Range(1, 5).upper, Range(1, None).upper)   # 5 None
```

### `Range.upper_inc` { #range-upper-inc }

**ধরন:** প্রপার্টি

ওপরের প্রান্ত ভেতরে (`]`) কি না।

**উদাহরণ:**

```python
print(Range(1, 5).upper_inc, Range(1, 5, bounds="[]").upper_inc)   # False True
```

### `Range.upper_inf` { #range-upper-inf }

**ধরন:** প্রপার্টি

ওপরের দিক অসীম কি না।

**উদাহরণ:**

```python
print(Range(1, None).upper_inf)   # True
```

## `MultiRange` { #multirange }

```python
from sqlalchemy.dialects.postgresql import MultiRange
```

(২.০.২৬) কয়েকটি `Range`-এর তালিকা, PostgreSQL ১৪-এর **multirange**-এর জন্য। এটি সাধারণ Python `list`; শুধু পার্থক্য: `literal(MultiRange([...]))` লিখলে SQLAlchemy নিজে থেকে ঠিক multirange টাইপ (`INT4MULTIRANGE` ইত্যাদি) বুঝে নেয়। কলামে লিখতে সাধারণ `list`-ও চলে; পড়লে ফেরত আসে `Range`-এর `list`। PostgreSQL গায়ে-লাগা টুকরো জুড়ে দেয়।

**উদাহরণ:**

```python
mr = MultiRange([Range(1, 3), Range(5, 8)])
print(literal(mr).type, rt(INT4MULTIRANGE, mr))   # INT4MULTIRANGE [Range(lower=1, upper=3, bounds='[)', empty=False), Range(lower=5, upper=8, bounds='[)', empty=False)]
print(rt(INT4MULTIRANGE, [Range(1, 3), Range(3, 8)]))   # [Range(lower=1, upper=8, bounds='[)', empty=False)]  (জুড়ে গেছে)
```

**Python `list`-এর সব মেথড** (`append()`, `clear()`, `copy()`, `count()`, `extend()`, `index()`, `insert()`, `pop()`, `remove()`, `reverse()`, `sort()`) সাধারণ `list`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

## Range কলামের অপারেটর { #range-comparator-group }

## `AbstractRange.comparator_factory` { #range-comparator }

```python
from sqlalchemy.dialects.postgresql import INT4RANGE
```

range বা multirange কলামে (`Booking.slot`) যে অপারেটরগুলো পাওয়া যায়। এগুলো SQL বানায়, হিসাব হয় **ডেটাবেসে**। `Range`-এর একই নামের Python মেথডের সাথে মিল আছে, তফাত শুধু কোথায় চলে। সাধারণ `==`, `!=`, `<` ইত্যাদিও চলে (ভাঁজ করা বক্সে)।

**উদাহরণ:**

```python
print(rooms(Booking.slot.overlaps(Range(4, 6))))   # ['A', 'B']
print(select(Booking.id).where(Booking.slot.overlaps(Range(4, 6))).compile(dialect=postgresql.dialect()))
# SELECT bookings.id
# FROM bookings
# WHERE bookings.slot && %(slot_1)s::INT4RANGE
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #range-comparator-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adjacent_to()`](#range-comparator-adjacent-to) | মেথড | <code>col -&#124;- other</code>: কলামের range `other`-এর ঠিক গায়ে লাগানো। |
| [`contained_by()`](#range-comparator-contained-by) | মেথড | `col <@ other`: কলামের range পুরোটা `other`-এর ভেতরে। |
| [`contains()`](#range-comparator-contains) | মেথড | `col @> other`: কলামের range একটি **মান** বা **range** ধারণ করে। |
| [`difference()`](#range-comparator-difference) | মেথড | `col - other`: পার্থক্য, ফল একটি range (মূল ডকস্ট্রিং ভুল করে "union" বলে)। |
| [`intersection()`](#range-comparator-intersection) | মেথড | `col * other`: সাধারণ অংশ (range)। |
| [`not_extend_left_of()`](#range-comparator-not-extend-left-of) | মেথড | `col &> other`: কলামের range `other`-এর বাঁয়ে ছড়ায় না। |
| [`not_extend_right_of()`](#range-comparator-not-extend-right-of) | মেথড | `col &< other`: কলামের range `other`-এর ডানে ছড়ায় না। |
| [`overlaps()`](#range-comparator-overlaps) | মেথড | `col && other`: কোনো সাধারণ বিন্দু আছে। |
| [`strictly_left_of()`](#range-comparator-strictly-left-of) | মেথড | `col << other`: পুরোটা বাঁ দিকে। |
| [`strictly_right_of()`](#range-comparator-strictly-right-of) | মেথড | `col >> other`: পুরোটা ডান দিকে। |
| [`union()`](#range-comparator-union) | মেথড | `col + other`: দুটি range জোড়া। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৪৮টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AbstractRange.comparator_factory`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`ColumnOperators` থেকে:** [`all_()`](operators.md#columnoperators-all-) · [`any_()`](operators.md#columnoperators-any-) · [`asc()`](operators.md#columnoperators-asc) · [`between()`](operators.md#columnoperators-between) · [`bitwise_and()`](operators.md#columnoperators-bitwise-and) · [`bitwise_lshift()`](operators.md#columnoperators-bitwise-lshift) · [`bitwise_not()`](operators.md#columnoperators-bitwise-not) · [`bitwise_or()`](operators.md#columnoperators-bitwise-or) · [`bitwise_rshift()`](operators.md#columnoperators-bitwise-rshift) · [`bitwise_xor()`](operators.md#columnoperators-bitwise-xor) · [`bool_op()`](operators.md#columnoperators-bool-op) · [`collate()`](operators.md#columnoperators-collate) · [`concat()`](operators.md#columnoperators-concat) · [`desc()`](operators.md#columnoperators-desc) · [`distinct()`](operators.md#columnoperators-distinct) · [`endswith()`](operators.md#columnoperators-endswith) · [`icontains()`](operators.md#columnoperators-icontains) · [`iendswith()`](operators.md#columnoperators-iendswith) · [`ilike()`](operators.md#columnoperators-ilike) · [`in_()`](operators.md#columnoperators-in-) · [`is_()`](operators.md#columnoperators-is-) · [`is_distinct_from()`](operators.md#columnoperators-is-distinct-from) · [`is_not()`](operators.md#columnoperators-is-not) · [`is_not_distinct_from()`](operators.md#columnoperators-is-not-distinct-from) · [`isnot()`](operators.md#columnoperators-isnot) · [`isnot_distinct_from()`](operators.md#columnoperators-isnot-distinct-from) · [`istartswith()`](operators.md#columnoperators-istartswith) · [`like()`](operators.md#columnoperators-like) · [`match()`](operators.md#columnoperators-match) · [`not_ilike()`](operators.md#columnoperators-not-ilike) · [`not_in()`](operators.md#columnoperators-not-in) · [`not_like()`](operators.md#columnoperators-not-like) · [`notilike()`](operators.md#columnoperators-notilike) · [`notin_()`](operators.md#columnoperators-notin-) · [`notlike()`](operators.md#columnoperators-notlike) · [`nulls_first()`](operators.md#columnoperators-nulls-first) · [`nulls_last()`](operators.md#columnoperators-nulls-last) · [`nullsfirst()`](operators.md#columnoperators-nullsfirst) · [`nullslast()`](operators.md#columnoperators-nullslast) · [`op()`](operators.md#columnoperators-op) · [`operate()`](operators.md#columnoperators-operate) · [`regexp_match()`](operators.md#columnoperators-regexp-match) · [`regexp_replace()`](operators.md#columnoperators-regexp-replace) · [`reverse_operate()`](operators.md#columnoperators-reverse-operate) · [`startswith()`](operators.md#columnoperators-startswith) · [`timetuple`](operators.md#columnoperators-timetuple)

**`TypeEngine.Comparator` থেকে:** [`expr`](custom-types.md#typeengine-comparator-expr) · [`type`](custom-types.md#typeengine-comparator-type)

///

### `AbstractRange.comparator_factory.adjacent_to()` { #range-comparator-adjacent-to }

```python
AbstractRange.comparator_factory.adjacent_to(other)
```

**ধরন:** মেথড

`col -|- other`: কলামের range `other`-এর ঠিক গায়ে লাগানো।

**উদাহরণ:**

```python
print(rooms(Booking.slot.adjacent_to(Range(10, 20))))   # ['B', 'C']
```

### `AbstractRange.comparator_factory.contained_by()` { #range-comparator-contained-by }

```python
AbstractRange.comparator_factory.contained_by(other)
```

**ধরন:** মেথড

`col <@ other`: কলামের range পুরোটা `other`-এর ভেতরে।

**উদাহরণ:**

```python
print(rooms(Booking.slot.contained_by(Range(0, 10))))   # ['A', 'B']
```

### `AbstractRange.comparator_factory.contains()` { #range-comparator-contains }

```python
AbstractRange.comparator_factory.contains(other, **kw)
```

**ধরন:** মেথড

`col @> other`: কলামের range একটি **মান** বা **range** ধারণ করে।

**উদাহরণ:**

```python
print(rooms(Booking.slot.contains(3)), rooms(Booking.slot.contains(Range(6, 8))))   # ['A'] ['B']
```

### `AbstractRange.comparator_factory.difference()` { #range-comparator-difference }

```python
AbstractRange.comparator_factory.difference(other)
```

**ধরন:** মেথড

`col - other`: পার্থক্য, ফল একটি range (মূল ডকস্ট্রিং ভুল করে "union" বলে)। মাঝখান থেকে কাটলে PostgreSQL এরর দেয়।

**উদাহরণ:**

```python
print(session.scalar(select(Booking.slot.difference(Range(3, 10))).where(Booking.room == "A")))   # [1,3)
```

### `AbstractRange.comparator_factory.intersection()` { #range-comparator-intersection }

```python
AbstractRange.comparator_factory.intersection(other)
```

**ধরন:** মেথড

`col * other`: সাধারণ অংশ (range)।

**উদাহরণ:**

```python
print(session.scalar(select(Booking.slot.intersection(Range(3, 10))).where(Booking.room == "A")))   # [3,5)
```

### `AbstractRange.comparator_factory.not_extend_left_of()` { #range-comparator-not-extend-left-of }

```python
AbstractRange.comparator_factory.not_extend_left_of(other)
```

**ধরন:** মেথড

`col &> other`: কলামের range `other`-এর বাঁয়ে ছড়ায় না।

**উদাহরণ:**

```python
print(rooms(Booking.slot.not_extend_left_of(Range(5, 100))))   # ['B', 'C']
```

### `AbstractRange.comparator_factory.not_extend_right_of()` { #range-comparator-not-extend-right-of }

```python
AbstractRange.comparator_factory.not_extend_right_of(other)
```

**ধরন:** মেথড

`col &< other`: কলামের range `other`-এর ডানে ছড়ায় না।

**উদাহরণ:**

```python
print(rooms(Booking.slot.not_extend_right_of(Range(0, 10))))   # ['A', 'B']
```

### `AbstractRange.comparator_factory.overlaps()` { #range-comparator-overlaps }

```python
AbstractRange.comparator_factory.overlaps(other)
```

**ধরন:** মেথড

`col && other`: কোনো সাধারণ বিন্দু আছে। "এই সময়ে কোনো বুকিং আছে?" ধরনের প্রশ্নে।

**উদাহরণ:**

```python
print(rooms(Booking.slot.overlaps(Range(8, 22))))   # ['B', 'C']
```

### `AbstractRange.comparator_factory.strictly_left_of()` { #range-comparator-strictly-left-of }

```python
AbstractRange.comparator_factory.strictly_left_of(other)
```

**ধরন:** মেথড

`col << other`: পুরোটা বাঁ দিকে।

**উদাহরণ:**

```python
print(rooms(Booking.slot.strictly_left_of(Range(10, 15))))   # ['A', 'B']
```

### `AbstractRange.comparator_factory.strictly_right_of()` { #range-comparator-strictly-right-of }

```python
AbstractRange.comparator_factory.strictly_right_of(other)
```

**ধরন:** মেথড

`col >> other`: পুরোটা ডান দিকে।

**উদাহরণ:**

```python
print(rooms(Booking.slot.strictly_right_of(Range(10, 15))))   # ['C']
```

### `AbstractRange.comparator_factory.union()` { #range-comparator-union }

```python
AbstractRange.comparator_factory.union(other)
```

**ধরন:** মেথড

`col + other`: দুটি range জোড়া। ফাঁক থাকলে PostgreSQL এরর দেয়।

**উদাহরণ:**

```python
print(session.scalar(select(Booking.slot.union(Range(5, 7))).where(Booking.room == "A")))   # [1,7)
```

## Range টাইপ { #abstractrange-group }

## `AbstractRange` { #abstractrange }

```python
from sqlalchemy.dialects.postgresql import AbstractRange
```

সব range আর multirange টাইপের মূল ক্লাস। এর `comparator_factory`-ই [range অপারেটরগুলো](#range-comparator) দেয়। নিজে কলামে ব্যবহার হয় না; `isinstance(t, AbstractRange)` দিয়ে "এটা কি range টাইপ?" জানতে কাজে লাগে।

**উদাহরণ:**

```python
print(isinstance(INT4RANGE(), AbstractRange), isinstance(INT4MULTIRANGE(), AbstractRange))   # True True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `AbstractSingleRange` { #abstractsinglerange }

```python
from sqlalchemy.dialects.postgresql import AbstractSingleRange
```

একটি `Range` ফেরত দেয় এমন টাইপের (`INT4RANGE`, `DATERANGE` …) মূল ক্লাস। নিজের range টাইপ বানাতে (যেমন কাস্টম `CREATE TYPE ... AS RANGE`) এটি subclass করুন আর `__visit_name__` দিন।

**উদাহরণ:**

```python
print(issubclass(DATERANGE, AbstractSingleRange), issubclass(DATEMULTIRANGE, AbstractSingleRange))   # True False
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractRange`](#abstractrange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `AbstractMultiRange` { #abstractmultirange }

```python
from sqlalchemy.dialects.postgresql import AbstractMultiRange
```

`Range`-এর **তালিকা** ফেরত দেয় এমন multirange টাইপের মূল ক্লাস (PostgreSQL ১৪+)।

**উদাহরণ:**

```python
print(issubclass(INT8MULTIRANGE, AbstractMultiRange))   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractRange`](#abstractrange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INT4RANGE` { #int4range }

```python
from sqlalchemy.dialects.postgresql import INT4RANGE
```

`int4range`: সাধারণ `INTEGER`-এর পরিসর। `Mapped[Range[int]]` লিখে `mapped_column(INT4RANGE)` দিন।

**উদাহরণ:**

```python
print(pgt(INT4RANGE()), rt(INT4RANGE, Range(1, 10)))   # INT4RANGE [1,10)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INT8RANGE` { #int8range }

```python
from sqlalchemy.dialects.postgresql import INT8RANGE
```

`int8range`: `BIGINT`-এর পরিসর।

**উদাহরণ:**

```python
print(rt(INT8RANGE, Range(1, 10_000_000_000)))   # [1,10000000000)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `NUMRANGE` { #numrange }

```python
from sqlalchemy.dialects.postgresql import NUMRANGE
```

`numrange`: `NUMERIC`-এর পরিসর (মান `Decimal`)। continuous, তাই PostgreSQL প্রান্ত বদলায় না।

**উদাহরণ:**

```python
print(repr(rt(NUMRANGE, Range(decimal.Decimal("1.5"), None, bounds="[]"))))
# Range(lower=Decimal('1.5'), upper=None, bounds='[)', empty=False)  (অসীম প্রান্ত সবসময় বাইরে)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `DATERANGE` { #daterange }

```python
from sqlalchemy.dialects.postgresql import DATERANGE
```

`daterange`: তারিখের পরিসর (ছুটি, বুকিং)। মান `datetime.date`।

**উদাহরণ:**

```python
r = rt(DATERANGE, Range(datetime.date(2025, 1, 1), datetime.date(2025, 1, 31), bounds="[]"))
print(r)   # [2025-01-01,2025-02-01)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSRANGE` { #tsrange }

```python
from sqlalchemy.dialects.postgresql import TSRANGE
```

`tsrange`: টাইমজোন ছাড়া `TIMESTAMP`-এর পরিসর।

**উদাহরণ:**

```python
r = rt(TSRANGE, Range(datetime.datetime(2025, 1, 1, 9), datetime.datetime(2025, 1, 1, 17)))
print(r.lower.hour, r.upper.hour)   # 9 17
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSTZRANGE` { #tstzrange }

```python
from sqlalchemy.dialects.postgresql import TSTZRANGE
```

`tstzrange`: টাইমজোনসহ `TIMESTAMP`-এর পরিসর। মিটিং/বুকিং-এর সময়ের জন্য সবচেয়ে ভালো (সাথে `ExcludeConstraint` দিয়ে "দুটি বুকিং মিলবে না" নিয়ম)।

**উদাহরণ:**

```python
utc = datetime.timezone.utc
r = rt(TSTZRANGE, Range(datetime.datetime(2025, 1, 1, 9, tzinfo=utc), datetime.datetime(2025, 1, 1, 10, tzinfo=utc)))
print(r.upper - r.lower)   # 1:00:00
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractSingleRange`](#abstractsinglerange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INT4MULTIRANGE` { #int4multirange }

```python
from sqlalchemy.dialects.postgresql import INT4MULTIRANGE
```

`int4multirange` (PostgreSQL ১৪+): কয়েকটি `INTEGER` পরিসর একসাথে। মান `list[Range[int]]` বা `MultiRange`।

**উদাহরণ:**

```python
print([str(r) for r in rt(INT4MULTIRANGE, [Range(1, 3), Range(5, 8)])])   # ['[1,3)', '[5,8)']
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `INT8MULTIRANGE` { #int8multirange }

```python
from sqlalchemy.dialects.postgresql import INT8MULTIRANGE
```

`int8multirange`: `BIGINT` পরিসরের তালিকা।

**উদাহরণ:**

```python
print(pgt(INT8MULTIRANGE()))   # INT8MULTIRANGE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `NUMMULTIRANGE` { #nummultirange }

```python
from sqlalchemy.dialects.postgresql import NUMMULTIRANGE
```

`nummultirange`: `NUMERIC` পরিসরের তালিকা।

**উদাহরণ:**

```python
print(pgt(NUMMULTIRANGE()))   # NUMMULTIRANGE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `DATEMULTIRANGE` { #datemultirange }

```python
from sqlalchemy.dialects.postgresql import DATEMULTIRANGE
```

`datemultirange`: কয়েকটি তারিখ-পরিসর (যেমন একজনের সব ছুটি এক কলামে)।

**উদাহরণ:**

```python
d = datetime.date
v = rt(DATEMULTIRANGE, MultiRange([Range(d(2025, 1, 1), d(2025, 1, 5)), Range(d(2025, 3, 1), d(2025, 3, 3))]))
print(len(v), v[1])   # 2 [2025-03-01,2025-03-03)
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSMULTIRANGE` { #tsmultirange }

```python
from sqlalchemy.dialects.postgresql import TSMULTIRANGE
```

`tsmultirange`: টাইমজোন ছাড়া timestamp পরিসরের তালিকা।

**উদাহরণ:**

```python
print(pgt(TSMULTIRANGE()))   # TSMULTIRANGE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSTZMULTIRANGE` { #tstzmultirange }

```python
from sqlalchemy.dialects.postgresql import TSTZMULTIRANGE
```

`tstzmultirange`: টাইমজোনসহ timestamp পরিসরের তালিকা।

**উদাহরণ:**

```python
print(pgt(TSTZMULTIRANGE()))   # TSTZMULTIRANGE
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`AbstractMultiRange`](#abstractmultirange)-এর মতো, অর্থাৎ [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## নামযুক্ত টাইপ: ENUM ও DOMAIN { #enum-group }

## `ENUM` { #enum }

```python
from sqlalchemy.dialects.postgresql import ENUM
```

PostgreSQL-এর `CREATE TYPE ... AS ENUM`। সাধারণ [`Enum`](types.md#enum) PostgreSQL-এ ভেতরে ভেতরে এটাই ব্যবহার করে; সরাসরি `ENUM` নিলে টাইপ তৈরি/মোছা নিজে নিয়ন্ত্রণ করা যায়, বা আগে থেকে থাকা টাইপ (`create_type=False`) ব্যবহার করা যায়।

**২.১-এ বদল:** টেবিল বানানোর সময় টাইপ না থাকলে আগের মতোই তৈরি হয়। কিন্তু **একটি টেবিলের `drop()`-এ টাইপ আর মোছে না** (অন্য টেবিলও হয়তো ব্যবহার করছে)। মুছতে `ENUM.drop()` বা `MetaData.drop_all()` (সেটি সংশ্লিষ্ট সব টাইপ মোছে)।

**উদাহরণ:**

```python
m = MetaData()
mood = ENUM("happy", "sad", name="mood_t")
t = Table("people", m, Column("id", Integer, primary_key=True), Column("mood", mood))
m.create_all(engine)
print(user_types())   # ['mood_t']
t.drop(engine)
print(user_types())   # ['mood_t']  (২.১: শুধু টেবিল drop করলে টাইপ থাকে)
m.drop_all(engine)
print(user_types())   # []
```

### কনস্ট্রাক্টরের প্যারামিটার { #enum-params }

```python
ENUM(*enums, name=_NoArg.NO_ARG, create_type=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `enums` | অনুমোদিত মানগুলো: কয়েকটি স্ট্রিং, বা একটি Python `enum.Enum` ক্লাস। |
| `name` | ডেটাবেসে টাইপের নাম (PostgreSQL-এ লাগবেই)। |
| `create_type` | `True` (ডিফল্ট): টেবিল তৈরির সময় টাইপ না থাকলে `CREATE TYPE`। `False`: কখনো নিজে তৈরি/মোছে না (টাইপ Alembic মাইগ্রেশনে বা হাতে বানানো হলে)। |
| `kw` | সাধারণ [`Enum`](types.md#enum-params)-এর বাকি সব প্যারামিটার: `schema`, `metadata`, `values_callable`, `validate_strings`, `inherit_schema` ইত্যাদি। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #enum-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`DDLDropper`](#enum-DDLDropper) | অ্যাট্রিবিউট (internal) | `DROP TYPE` চালানোর ভিজিটর ক্লাস; `drop()` আর `drop_all()` ভেতরে এটি ব্যবহার করে। |
| [`DDLGenerator`](#enum-DDLGenerator) | অ্যাট্রিবিউট (internal) | `CREATE TYPE` চালানোর ভিজিটর ক্লাস; `create()` আর `create_all()` ভেতরে এটি ব্যবহার করে (আগে আছে কি না দেখে)। |
| [`adapt_emulated_to_native()`](#enum-adapt-emulated-to-native) | ক্লাস মেথড (internal) | (ক্লাস মেথড) সাধারণ `Enum` থেকে PostgreSQL `ENUM` বানায়। |
| [`adapt_native_to_emulated()`](#enum-adapt-native-to-emulated) | ক্লাস মেথড (internal) | (ক্লাস মেথড) উল্টো দিক: native টাইপ থেকে emulated (সাধারণ) টাইপ। |
| [`adapt_to_emulated()`](#enum-adapt-to-emulated) | মেথড (internal) | এই `ENUM`-কে একটি emulated (সাধারণ `Enum`) টাইপে বদলায়; ভেতরের ব্যবহারের জন্য। |
| [`create()`](#enum-create) | মেথড | `CREATE TYPE` চালায়। |
| [`drop()`](#enum-drop) | মেথড | `DROP TYPE` চালায়। |
| [`inherit_schema`](#enum-inherit-schema) | প্রপার্টি ⚠️ deprecated | (২.১-এ বাতিলের পথে) টাইপটি টেবিলের স্কিমা নেবে কি না। |
| [`native`](#enum-native) | প্রপার্টি | এটি native (ডেটাবেসের নিজস্ব) টাইপ কি না: `ENUM`-এ সবসময় `True`। |
| [`native_enum`](#enum-native-enum) | অ্যাট্রিবিউট | native ENUM কি না: PostgreSQL `ENUM`-এ সবসময় `True` (সাধারণ `Enum`-এ `native_enum=False` দিলে `VARCHAR` হয়)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `ENUM`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `ENUM.DDLDropper` { #enum-DDLDropper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`DROP TYPE` চালানোর ভিজিটর ক্লাস; `drop()` আর `drop_all()` ভেতরে এটি ব্যবহার করে।

**উদাহরণ:**

```python
print(ENUM.DDLDropper.__name__)   # EnumDropper
```

### `ENUM.DDLGenerator` { #enum-DDLGenerator }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CREATE TYPE` চালানোর ভিজিটর ক্লাস; `create()` আর `create_all()` ভেতরে এটি ব্যবহার করে (আগে আছে কি না দেখে)।

**উদাহরণ:**

```python
print(ENUM.DDLGenerator.__name__)   # EnumGenerator
```

### `ENUM.adapt_emulated_to_native()` { #enum-adapt-emulated-to-native }

```python
ENUM.adapt_emulated_to_native(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) সাধারণ `Enum` থেকে PostgreSQL `ENUM` বানায়। PostgreSQL ডায়ালেক্ট `Enum` কলাম কম্পাইল করার সময় (`dialect_impl()`-এর ভেতরে) এটি ডাকে; নিজে সরাসরি ডাকার দরকার পড়ে না।

**উদাহরণ:**

```python
pg_enum = Enum("S", "M", name="size_t").dialect_impl(postgresql.dialect())
print(type(pg_enum).__name__, pg_enum.name, pg_enum.enums)   # ENUM size_t ['S', 'M']
```

### `ENUM.adapt_native_to_emulated()` { #enum-adapt-native-to-emulated }

```python
ENUM.adapt_native_to_emulated(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) উল্টো দিক: native টাইপ থেকে emulated (সাধারণ) টাইপ। SQLAlchemy-র টাইপ-অভিযোজন ব্যবস্থার অংশ।

**উদাহরণ:**

```python
print(callable(ENUM.adapt_native_to_emulated))   # True
```

### `ENUM.adapt_to_emulated()` { #enum-adapt-to-emulated }

```python
ENUM.adapt_to_emulated(impltype, **kw)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

এই `ENUM`-কে একটি emulated (সাধারণ `Enum`) টাইপে বদলায়; ভেতরের ব্যবহারের জন্য। নিজের কোডে সাধারণ রূপ দরকার হলে `as_generic()` ব্যবহার করুন।

**উদাহরণ:**

```python
print(type(ENUM("a", "b", name="ab").as_generic()).__name__)   # Enum
```

### `ENUM.create()` { #enum-create }

```python
ENUM.create(bind, checkfirst=True)
```

**ধরন:** মেথড

`CREATE TYPE` চালায়। `checkfirst=True` (ডিফল্ট): আগে আছে কি না দেখে, থাকলে কিছু করে না। PostgreSQL ছাড়া অন্য ডেটাবেসে কিছুই করে না।

**উদাহরণ:**

```python
mood = ENUM("happy", "sad", name="mood_t")
mood.create(engine)
mood.create(engine)          # দ্বিতীয়বার: আছে, তাই চুপচাপ বাদ
print(user_types())   # ['mood_t']
```

### `ENUM.drop()` { #enum-drop }

```python
ENUM.drop(bind, checkfirst=True)
```

**ধরন:** মেথড

`DROP TYPE` চালায়। `checkfirst=True` (ডিফল্ট): না থাকলে কিছু করে না। কোনো টেবিল টাইপটি ব্যবহার করলে PostgreSQL এরর দেয়।

**উদাহরণ:**

```python
mood = ENUM("happy", "sad", name="mood_t")
mood.create(engine); mood.drop(engine); mood.drop(engine)
print(user_types())   # []
```

### `ENUM.inherit_schema` { #enum-inherit-schema }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.১-এ বাতিলের পথে) টাইপটি টেবিলের স্কিমা নেবে কি না। পড়লেই `SADeprecationWarning`। প্যারামিটার `inherit_schema=` এখনো দেওয়া যায়, শুধু এই প্রপার্টি পড়া বাতিল।

**উদাহরণ:**

```python
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    ENUM("a", name="x").inherit_schema
print(w[0].message)   # The ``inherit_schema`` property is deprecated.
```

### `ENUM.native` { #enum-native }

**ধরন:** প্রপার্টি

এটি native (ডেটাবেসের নিজস্ব) টাইপ কি না: `ENUM`-এ সবসময় `True`।

**উদাহরণ:**

```python
print(ENUM("a", name="x").native)   # True
```

### `ENUM.native_enum` { #enum-native-enum }

**ধরন:** অ্যাট্রিবিউট

native ENUM কি না: PostgreSQL `ENUM`-এ সবসময় `True` (সাধারণ `Enum`-এ `native_enum=False` দিলে `VARCHAR` হয়)।

**উদাহরণ:**

```python
print(ENUM("a", name="x").native_enum)   # True
```

## `DOMAIN` { #domain }

```python
from sqlalchemy.dialects.postgresql import DOMAIN
```

PostgreSQL-এর `CREATE DOMAIN`: একটি মূল টাইপ + নিয়ম (NOT NULL, CHECK, DEFAULT), নাম দিয়ে বারবার ব্যবহারের জন্য। যেমন "ধনাত্মক পূর্ণসংখ্যা" একবার বানিয়ে অনেক কলামে। তৈরি/মোছার নিয়ম `ENUM`-এর মতোই (২.১-এর বদলসহ)। নিয়ম ভাঙলে `IntegrityError`।

**উদাহরণ:**

```python
PositiveInt = DOMAIN("pos_int", Integer, check="VALUE > 0", not_null=True)
m = MetaData()
t = Table("stock", m, Column("id", Integer, primary_key=True), Column("qty", PositiveInt))
m.create_all(engine)
from sqlalchemy.exc import IntegrityError
try:
    with engine.begin() as c:
        c.execute(insert(t).values(qty=-1))
except IntegrityError as e:
    print(type(e.orig).__name__)   # CheckViolation
```

### কনস্ট্রাক্টরের প্যারামিটার { #domain-params }

```python
DOMAIN(name, data_type, *, collation=None, collation_schema=None, default=None, constraint_name=None, not_null=None, check=None, create_type=True, **kw)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | ডেটাবেসে ডোমেইনের নাম। |
| `data_type` | মূল টাইপ, যেমন `Integer`, `Text`। |
| `collation` | স্ট্রিং টাইপের collation (`COLLATE`)। |
| `collation_schema` | (২.১) collation কোন স্কিমায়। |
| `default` | ডিফল্ট মান। স্ট্রিং দিলে **লিটারাল** হিসেবে বসে (`default="00000"` → `DEFAULT '00000'`); SQL এক্সপ্রেশন দিতে `text(...)`। |
| `constraint_name` | CHECK কনস্ট্রেইন্টের নাম (না দিলে PostgreSQL দেয়, যেমন `pos_int_check`)। |
| `not_null` | `True` দিলে `NOT NULL`। |
| `check` | CHECK শর্ত, যেখানে মানকে `VALUE` বলা হয়: `"VALUE > 0"`। |
| `create_type` | `ENUM`-এর মতো: `False` দিলে নিজে তৈরি/মোছে না। |
| `kw` | `schema`, `metadata`, `inherit_schema` ইত্যাদি (`SchemaType`-এর মতো)। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #domain-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`DDLDropper`](#domain-DDLDropper) | অ্যাট্রিবিউট (internal) | `DROP DOMAIN` চালানোর ভিজিটর ক্লাস। |
| [`DDLGenerator`](#domain-DDLGenerator) | অ্যাট্রিবিউট (internal) | `CREATE DOMAIN` চালানোর ভিজিটর ক্লাস। |
| [`check`](#domain-check) | অ্যাট্রিবিউট | CHECK শর্ত (`text()` হিসেবে রাখা)। |
| [`collation`](#domain-collation) | অ্যাট্রিবিউট | collation-এর নাম বা `None`। |
| [`collation_schema`](#domain-collation-schema) | অ্যাট্রিবিউট | (২.১) collation-এর স্কিমা বা `None`। |
| [`constraint_name`](#domain-constraint-name) | অ্যাট্রিবিউট | CHECK কনস্ট্রেইন্টের নাম বা `None`। |
| [`create()`](#domain-create) | মেথড | `CREATE DOMAIN` চালায় (`checkfirst=True` হলে আগে আছে কি না দেখে)। |
| [`create_type`](#domain-create-type) | অ্যাট্রিবিউট | টেবিলের সাথে নিজে তৈরি করবে কি না। |
| [`data_type`](#domain-data-type) | অ্যাট্রিবিউট | মূল টাইপ (টাইপ অবজেক্ট)। |
| [`default`](#domain-default) | অ্যাট্রিবিউট | ডিফল্ট মান বা `None`। |
| [`drop()`](#domain-drop) | মেথড | `DROP DOMAIN` চালায় (`checkfirst=True` হলে না থাকলে কিছু করে না)। |
| [`inherit_schema`](#domain-inherit-schema) | প্রপার্টি ⚠️ deprecated | (২.১-এ বাতিলের পথে) `ENUM.inherit_schema`-এর মতো: পড়লেই সতর্কবার্তা। |
| [`not_null`](#domain-not-null) | অ্যাট্রিবিউট | `NOT NULL` কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `DOMAIN`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `DOMAIN.DDLDropper` { #domain-DDLDropper }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`DROP DOMAIN` চালানোর ভিজিটর ক্লাস।

**উদাহরণ:**

```python
print(DOMAIN.DDLDropper.__name__)   # DomainDropper
```

### `DOMAIN.DDLGenerator` { #domain-DDLGenerator }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`CREATE DOMAIN` চালানোর ভিজিটর ক্লাস।

**উদাহরণ:**

```python
print(DOMAIN.DDLGenerator.__name__)   # DomainGenerator
```

### `DOMAIN.check` { #domain-check }

**ধরন:** অ্যাট্রিবিউট

CHECK শর্ত (`text()` হিসেবে রাখা)।

**উদাহরণ:**

```python
print(DOMAIN("pos_int", Integer, check="VALUE > 0").check)   # VALUE > 0
```

### `DOMAIN.collation` { #domain-collation }

**ধরন:** অ্যাট্রিবিউট

collation-এর নাম বা `None`।

**উদাহরণ:**

```python
print(DOMAIN("code_t", Text, collation="C").collation)   # C
```

### `DOMAIN.collation_schema` { #domain-collation-schema }

**ধরন:** অ্যাট্রিবিউট

(২.১) collation-এর স্কিমা বা `None`।

**উদাহরণ:**

```python
print(DOMAIN("code_t", Text).collation_schema)   # None
```

### `DOMAIN.constraint_name` { #domain-constraint-name }

**ধরন:** অ্যাট্রিবিউট

CHECK কনস্ট্রেইন্টের নাম বা `None`।

**উদাহরণ:**

```python
print(DOMAIN("pos_int", Integer, check="VALUE > 0", constraint_name="pos_ok").constraint_name)   # pos_ok
```

### `DOMAIN.create()` { #domain-create }

```python
DOMAIN.create(bind, checkfirst=True, **kw)
```

**ধরন:** মেথড

`CREATE DOMAIN` চালায় (`checkfirst=True` হলে আগে আছে কি না দেখে)।

**উদাহরণ:**

```python
PositiveInt = DOMAIN("pos_int", Integer, check="VALUE > 0")
PositiveInt.create(engine)
with engine.connect() as c:
    print(c.scalar(text("SELECT 5::pos_int")))   # 5
```

### `DOMAIN.create_type` { #domain-create-type }

**ধরন:** অ্যাট্রিবিউট

টেবিলের সাথে নিজে তৈরি করবে কি না।

**উদাহরণ:**

```python
print(DOMAIN("pos_int", Integer, create_type=False).create_type)   # False
```

### `DOMAIN.data_type` { #domain-data-type }

**ধরন:** অ্যাট্রিবিউট

মূল টাইপ (টাইপ অবজেক্ট)।

**উদাহরণ:**

```python
print(repr(DOMAIN("pos_int", Integer).data_type))   # Integer()
```

### `DOMAIN.default` { #domain-default }

**ধরন:** অ্যাট্রিবিউট

ডিফল্ট মান বা `None`।

**উদাহরণ:**

```python
ddl(CreateDomainType(DOMAIN("zip_t", Text, default="00000")))   # CREATE DOMAIN zip_t AS TEXT DEFAULT '00000'
```

### `DOMAIN.drop()` { #domain-drop }

```python
DOMAIN.drop(bind, checkfirst=True, **kw)
```

**ধরন:** মেথড

`DROP DOMAIN` চালায় (`checkfirst=True` হলে না থাকলে কিছু করে না)।

**উদাহরণ:**

```python
d = DOMAIN("pos_int", Integer)
d.create(engine); d.drop(engine)
print(user_types())   # []
```

### `DOMAIN.inherit_schema` { #domain-inherit-schema }

**ধরন:** প্রপার্টি

/// danger | বাতিলের পথে (deprecated)

ভবিষ্যতের কোনো ভার্সনে এটি সরিয়ে ফেলা হবে। নতুন কোডে ব্যবহার করবেন না; বিকল্প নিচে বলা আছে।

///

(২.১-এ বাতিলের পথে) `ENUM.inherit_schema`-এর মতো: পড়লেই সতর্কবার্তা।

**উদাহরণ:**

```python
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    DOMAIN("d", Integer).inherit_schema
print(len(w))   # 1
```

### `DOMAIN.not_null` { #domain-not-null }

**ধরন:** অ্যাট্রিবিউট

`NOT NULL` কি না।

**উদাহরণ:**

```python
print(DOMAIN("pos_int", Integer, not_null=True).not_null)   # True
```

## `NamedType` { #namedtype }

```python
from sqlalchemy.dialects.postgresql import NamedType
```

`ENUM` আর `DOMAIN`-এর মূল ক্লাস: নাম আছে এমন, আলাদাভাবে `CREATE`/`DROP` করতে হয় এমন টাইপ। নিজের নামযুক্ত টাইপ বানাতে subclass করুন; `isinstance(t, NamedType)` দিয়ে চেনা যায়।

**উদাহরণ:**

```python
print(isinstance(ENUM("a", name="x"), NamedType), isinstance(DOMAIN("d", Integer), NamedType))   # True True
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #namedtype-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`create()`](#namedtype-create) | মেথড | ডেটাবেসে টাইপটি তৈরি করে (`ENUM.create()` / `DOMAIN.create()` দেখুন)। |
| [`drop()`](#namedtype-drop) | মেথড | ডেটাবেস থেকে টাইপটি মোছে। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `NamedType`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `NamedType.create()` { #namedtype-create }

```python
NamedType.create(bind, checkfirst=True, **kw)
```

**ধরন:** মেথড

ডেটাবেসে টাইপটি তৈরি করে (`ENUM.create()` / `DOMAIN.create()` দেখুন)।

**উদাহরণ:**

```python
t: NamedType = DOMAIN("pos_int", Integer)
t.create(engine)
print(user_types())   # ['pos_int']
```

### `NamedType.drop()` { #namedtype-drop }

```python
NamedType.drop(bind, checkfirst=True, **kw)
```

**ধরন:** মেথড

ডেটাবেস থেকে টাইপটি মোছে।

**উদাহরণ:**

```python
t: NamedType = ENUM("a", name="ab_t")
t.create(engine); t.drop(engine)
print(user_types())   # []
```

## `CreateEnumType` { #createenumtype }

```python
from sqlalchemy.dialects.postgresql import CreateEnumType
```

`CREATE TYPE ... AS ENUM` DDL কনস্ট্রাক্ট। `ENUM.create()` এটাই চালায়; নিজে `conn.execute(CreateEnumType(e))` দিলে "আছে কি না" না দেখেই চালায়।

**উদাহরণ:**

```python
ddl(CreateEnumType(ENUM("happy", "sad", name="mood_t")))   # CREATE TYPE mood_t AS ENUM ('happy', 'sad')
```

### কনস্ট্রাক্টরের প্যারামিটার { #createenumtype-params }

```python
CreateEnumType(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `ENUM` তৈরি হবে। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CreateSequence`](ddl.md#createsequence-summary)-এর মতো।

## `DropEnumType` { #dropenumtype }

```python
from sqlalchemy.dialects.postgresql import DropEnumType
```

`DROP TYPE` DDL কনস্ট্রাক্ট।

**উদাহরণ:**

```python
ddl(DropEnumType(ENUM("happy", "sad", name="mood_t")))   # DROP TYPE mood_t
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropenumtype-params }

```python
DropEnumType(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `ENUM` মোছা হবে। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CreateSequence`](ddl.md#createsequence-summary)-এর মতো।

## `CreateDomainType` { #createdomaintype }

```python
from sqlalchemy.dialects.postgresql import CreateDomainType
```

`CREATE DOMAIN` DDL কনস্ট্রাক্ট।

**উদাহরণ:**

```python
ddl(CreateDomainType(DOMAIN("pos_int", Integer, check="VALUE > 0", not_null=True)))
# CREATE DOMAIN pos_int AS INTEGER NOT NULL CHECK (VALUE > 0)
```

### কনস্ট্রাক্টরের প্যারামিটার { #createdomaintype-params }

```python
CreateDomainType(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `DOMAIN` তৈরি হবে। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CreateSequence`](ddl.md#createsequence-summary)-এর মতো।

## `DropDomainType` { #dropdomaintype }

```python
from sqlalchemy.dialects.postgresql import DropDomainType
```

`DROP DOMAIN` DDL কনস্ট্রাক্ট।

**উদাহরণ:**

```python
ddl(DropDomainType(DOMAIN("pos_int", Integer)))   # DROP DOMAIN pos_int
```

### কনস্ট্রাক্টরের প্যারামিটার { #dropdomaintype-params }

```python
DropDomainType(element)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `element` | যে `DOMAIN` মোছা হবে। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`CreateSequence`](ddl.md#createsequence-summary)-এর মতো।

## `PGInspector` { #pginspector }

```python
from sqlalchemy.dialects.postgresql.base import PGInspector
```

PostgreSQL engine-এ `inspect(engine)` যে [`Inspector`](inspection.md#inspector) দেয়, সেটি আসলে এই ক্লাস। সাধারণ সব মেথড (`get_table_names()`, `get_columns()` …) ছাড়াও PostgreSQL-এর বিশেষ পাঁচটি: ENUM, DOMAIN, foreign table আর টেবিলের OID।

**উদাহরণ:**

```python
insp = inspect(engine)
print(type(insp).__name__, insp.get_table_names())   # PGInspector ['bookings']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #pginspector-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`get_domains()`](#pginspector-get-domains) | মেথড | সব DOMAIN-এর তথ্য (dict-এর তালিকা): `name`, `schema`, `visible`, `type`, `nullable`, `default`, `constraints`, `collation` …। |
| [`get_enums()`](#pginspector-get-enums) | মেথড | সব ENUM-এর তথ্য: `name`, `schema`, `visible`, `labels` (মানগুলো ক্রমানুসারে)। |
| [`get_foreign_table_names()`](#pginspector-get-foreign-table-names) | মেথড | `CREATE FOREIGN TABLE` (postgres_fdw ইত্যাদি) দিয়ে বানানো টেবিলের নাম। |
| [`get_table_oid()`](#pginspector-get-table-oid) | মেথড | একটি টেবিলের PostgreSQL OID (অভ্যন্তরীণ সংখ্যা-পরিচয়)। |
| [`has_type()`](#pginspector-has-type) | মেথড | নির্দিষ্ট নামের টাইপ (ENUM/DOMAIN ইত্যাদি) আছে কি না। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৩৫টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `PGInspector`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Inspector` থেকে:** [`clear_cache()`](inspection.md#inspector-clear-cache) · [`default_schema_name`](inspection.md#inspector-default-schema-name) · [`from_engine()`](inspection.md#inspector-from-engine) · [`get_check_constraints()`](inspection.md#inspector-get-check-constraints) · [`get_columns()`](inspection.md#inspector-get-columns) · [`get_foreign_keys()`](inspection.md#inspector-get-foreign-keys) · [`get_indexes()`](inspection.md#inspector-get-indexes) · [`get_materialized_view_names()`](inspection.md#inspector-get-materialized-view-names) · [`get_multi_check_constraints()`](inspection.md#inspector-get-multi-check-constraints) · [`get_multi_columns()`](inspection.md#inspector-get-multi-columns) · [`get_multi_foreign_keys()`](inspection.md#inspector-get-multi-foreign-keys) · [`get_multi_indexes()`](inspection.md#inspector-get-multi-indexes) · [`get_multi_pk_constraint()`](inspection.md#inspector-get-multi-pk-constraint) · [`get_multi_table_comment()`](inspection.md#inspector-get-multi-table-comment) · [`get_multi_table_options()`](inspection.md#inspector-get-multi-table-options) · [`get_multi_unique_constraints()`](inspection.md#inspector-get-multi-unique-constraints) · [`get_pk_constraint()`](inspection.md#inspector-get-pk-constraint) · [`get_schema_names()`](inspection.md#inspector-get-schema-names) · [`get_sequence_names()`](inspection.md#inspector-get-sequence-names) · [`get_sorted_table_and_fkc_names()`](inspection.md#inspector-get-sorted-table-and-fkc-names) · [`get_table_comment()`](inspection.md#inspector-get-table-comment) · [`get_table_names()`](inspection.md#inspector-get-table-names) · [`get_table_options()`](inspection.md#inspector-get-table-options) · [`get_temp_table_names()`](inspection.md#inspector-get-temp-table-names) · [`get_temp_view_names()`](inspection.md#inspector-get-temp-view-names) · [`get_unique_constraints()`](inspection.md#inspector-get-unique-constraints) · [`get_view_definition()`](inspection.md#inspector-get-view-definition) · [`get_view_names()`](inspection.md#inspector-get-view-names) · [`has_index()`](inspection.md#inspector-has-index) · [`has_multi_table()`](inspection.md#inspector-has-multi-table) · [`has_schema()`](inspection.md#inspector-has-schema) · [`has_sequence()`](inspection.md#inspector-has-sequence) · [`has_table()`](inspection.md#inspector-has-table) · [`reflect_table()`](inspection.md#inspector-reflect-table) · [`sort_tables_on_foreign_key_dependency()`](inspection.md#inspector-sort-tables-on-foreign-key-dependency)

///

### `PGInspector.get_domains()` { #pginspector-get-domains }

```python
PGInspector.get_domains(schema=None)
```

**ধরন:** মেথড

সব DOMAIN-এর তথ্য (dict-এর তালিকা): `name`, `schema`, `visible`, `type`, `nullable`, `default`, `constraints`, `collation` …। `schema=` দিলে সেই স্কিমার, `"*"` দিলে সব স্কিমার।

**উদাহরণ:**

```python
DOMAIN("pos_int", Integer, check="VALUE > 0", not_null=True).create(engine)
d = inspect(engine).get_domains()[0]
print(d["name"], d["type"], d["nullable"], d["constraints"])
# pos_int integer False [{'name': 'pos_int_check', 'check': 'VALUE > 0'}]
```

### `PGInspector.get_enums()` { #pginspector-get-enums }

```python
PGInspector.get_enums(schema=None)
```

**ধরন:** মেথড

সব ENUM-এর তথ্য: `name`, `schema`, `visible`, `labels` (মানগুলো ক্রমানুসারে)।

**উদাহরণ:**

```python
ENUM("happy", "sad", name="mood_t").create(engine)
print(inspect(engine).get_enums())   # [{'name': 'mood_t', 'schema': 'public', 'visible': True, 'labels': ['happy', 'sad']}]
```

### `PGInspector.get_foreign_table_names()` { #pginspector-get-foreign-table-names }

```python
PGInspector.get_foreign_table_names(schema=None)
```

**ধরন:** মেথড

`CREATE FOREIGN TABLE` (postgres_fdw ইত্যাদি) দিয়ে বানানো টেবিলের নাম। সাধারণ `get_table_names()`-এ এগুলো আসে না।

**উদাহরণ:**

```python
print(inspect(engine).get_foreign_table_names())   # []
```

### `PGInspector.get_table_oid()` { #pginspector-get-table-oid }

```python
PGInspector.get_table_oid(table_name, schema=None)
```

**ধরন:** মেথড

একটি টেবিলের PostgreSQL OID (অভ্যন্তরীণ সংখ্যা-পরিচয়)। না থাকলে `NoSuchTableError`।

**উদাহরণ:**

```python
oid = inspect(engine).get_table_oid("bookings")
with engine.connect() as c:
    print(c.scalar(select(cast(oid, REGCLASS))))   # bookings
```

### `PGInspector.has_type()` { #pginspector-has-type }

```python
PGInspector.has_type(type_name, schema=None, **kw)
```

**ধরন:** মেথড

নির্দিষ্ট নামের টাইপ (ENUM/DOMAIN ইত্যাদি) আছে কি না। `schema="*"` দিলে সব স্কিমায় খোঁজে।

**উদাহরণ:**

```python
ENUM("happy", name="mood_t").create(engine)
print(inspect(engine).has_type("mood_t"), inspect(engine).has_type("nope_t"))   # True False
```

## নেটওয়ার্ক টাইপ { #inet-group }

## `INET` { #inet }

```python
from sqlalchemy.dialects.postgresql import INET
```

IPv4/IPv6 ঠিকানা (চাইলে সাবনেটসহ, যেমন `192.168.0.1/24`)। **psycopg 3 ও asyncpg** Python-এর `ipaddress` অবজেক্ট (`IPv4Interface` …) ফেরত দেয়, **psycopg2** দেয় স্ট্রিং। সব ড্রাইভারে স্ট্রিং চাইলে `create_engine(..., native_inet_types=False)`।

**উদাহরণ:**

```python
print(repr(rt(INET, "192.168.0.1/24")))   # IPv4Interface('192.168.0.1/24')
e2 = create_engine("postgresql+psycopg://postgres@127.0.0.1/apiref", native_inet_types=False)
with e2.connect() as c:
    print(repr(c.scalar(select(cast("10.0.0.1", INET)))))   # '10.0.0.1'
e2.dispose()
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `CIDR` { #cidr }

```python
from sqlalchemy.dialects.postgresql import CIDR
```

নেটওয়ার্ক (সাবনেট), যেমন `10.0.0.0/8`। হোস্ট-বিট শূন্য হতে হবে (`10.0.0.1/8` দিলে PostgreSQL এরর)। psycopg 3-এ ফেরত `IPv4Network`।

**উদাহরণ:**

```python
print(repr(rt(CIDR, "10.0.0.0/8")))   # IPv4Network('10.0.0.0/8')
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `MACADDR` { #macaddr }

```python
from sqlalchemy.dialects.postgresql import MACADDR
```

৬-বাইটের MAC ঠিকানা। ফেরত আসে স্ট্রিং, PostgreSQL-এর আদর্শ রূপে (ছোট হাতের, `:` দিয়ে)।

**উদাহরণ:**

```python
print(rt(MACADDR, "08-00-2B-01-02-03"))   # 08:00:2b:01:02:03
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `MACADDR8` { #macaddr8 }

```python
from sqlalchemy.dialects.postgresql import MACADDR8
```

৮-বাইটের (EUI-64) MAC ঠিকানা। ৬-বাইটের দিলে মাঝে `ff:fe` বসিয়ে ৮ বাইট করে।

**উদাহরণ:**

```python
print(rt(MACADDR8, "08:00:2b:01:02:03"))   # 08:00:2b:ff:fe:01:02:03
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## অন্যান্য PostgreSQL টাইপ { #citext-group }

## `CITEXT` { #citext }

```python
from sqlalchemy.dialects.postgresql import CITEXT
```

(২.০.৭) ছোট-বড় হাতের পার্থক্য না করা টেক্সট: `'Hello' = 'HELLO'` সত্য। ইমেইল/ইউজারনেমের জন্য ভালো। আগে ডেটাবেসে `CREATE EXTENSION citext` লাগবে।

**উদাহরণ:**

```python
m = MetaData()
t = Table("users", m, Column("id", Integer, primary_key=True), Column("email", CITEXT))
m.create_all(engine)
with engine.begin() as c:
    c.execute(insert(t).values(email="Rahim@Example.com"))
    print(c.scalar(select(t.c.email).where(t.c.email == "rahim@example.com")))   # Rahim@Example.com
```

### কনস্ট্রাক্টরের প্যারামিটার { #citext-params }

```python
CITEXT(length=None, collation=None, collation_schema=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | সর্বোচ্চ দৈর্ঘ্য (PostgreSQL CITEXT-এ সাধারণত দেওয়া হয় না)। |
| `collation` | collation। |
| `collation_schema` | (২.১) collation-এর স্কিমা। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TEXT`](types.md#sql-text)-এর মতো, অর্থাৎ [`String`](types.md#string-summary)-এর মতো।

## `MONEY` { #money }

```python
from sqlalchemy.dialects.postgresql import MONEY
```

PostgreSQL-এর `MONEY`। ফেরত আসে **মুদ্রা-চিহ্নসহ স্ট্রিং** (`'$12.50'`, সার্ভারের `lc_monetary` অনুযায়ী)। psycopg 3-এ `float` দিলে এরর, `Decimal` বা স্ট্রিং দিন। হিসাবের জন্য সাধারণত `Numeric(12, 2)` ভালো; MONEY লাগলে `TypeDecorator` দিয়ে `Decimal`-এ বদলান।

**উদাহরণ:**

```python
print(rt(MONEY, decimal.Decimal("12.50")), rt(MONEY, "1234.5"))   # $12.50 $1,234.50
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `OID` { #oid }

```python
from sqlalchemy.dialects.postgresql import OID
```

PostgreSQL-এর অভ্যন্তরীণ অবজেক্ট আইডি (সংখ্যা)। সিস্টেম ক্যাটালগ কুয়েরিতে কাজে লাগে।

**উদাহরণ:**

```python
print(rt(OID, 5))   # 5
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `REGCLASS` { #regclass }

```python
from sqlalchemy.dialects.postgresql import REGCLASS
```

টেবিলের নাম ↔ OID। `cast("bookings", REGCLASS)` টেবিলের নাম যাচাই করে OID বানায় (না থাকলে এরর); ফেরত আসে নাম (স্ট্রিং)।

**উদাহরণ:**

```python
with engine.connect() as c:
    print(c.scalar(select(cast("bookings", REGCLASS))))   # bookings
    print(c.scalar(select(func.pg_relation_size(cast("bookings", REGCLASS)))) >= 0)   # True
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `REGCONFIG` { #regconfig }

```python
from sqlalchemy.dialects.postgresql import REGCONFIG
```

(২.০) ফুল-টেক্সট সার্চের কনফিগারেশন (`'english'`, `'simple'`)। `to_tsvector()`/`to_tsquery()`-এ ভাষা দিতে; [ফুল-টেক্সট ফাংশনগুলো](postgresql.md#to-tsvector) প্রথম স্ট্রিং আর্গুমেন্ট নিজে থেকেই এই টাইপে বসায়।

**উদাহরণ:**

```python
with engine.connect() as c:
    print(c.scalar(select(func.to_tsvector(cast("english", REGCONFIG), "running cats"))))   # 'cat':2 'run':1
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSQUERY` { #tsquery }

```python
from sqlalchemy.dialects.postgresql import TSQUERY
```

(২.০) ফুল-টেক্সট সার্চের প্রশ্ন (`'cat' & 'rat'`)। `to_tsquery()` ইত্যাদির ফলের টাইপ; ফেরত আসে স্ট্রিং।

**উদাহরণ:**

```python
with engine.connect() as c:
    print(c.scalar(select(cast("cat & rat", TSQUERY))))   # 'cat' & 'rat'
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `TSVECTOR` { #tsvector }

```python
from sqlalchemy.dialects.postgresql import TSVECTOR
```

ফুল-টেক্সট সার্চের জন্য প্রস্তুত শব্দের তালিকা। সাধারণত `Computed("to_tsvector(...)", persisted=True)` কলাম + GIN ইনডেক্স হিসেবে রাখা হয়; ব্যবহার দেখুন [ফুল-টেক্সট সার্চ](postgresql.md#to-tsvector)।

**উদাহরণ:**

```python
print(rt(TSVECTOR, "a fat cat"))   # 'a' 'cat' 'fat'
```

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `BIT` { #bit }

```python
from sqlalchemy.dialects.postgresql import BIT
```

বিটের সারি: `BIT(n)` (ঠিক n বিট) বা `BIT VARYING(n)`। **২.১-এ বদল:** মান এখন [`BitString`](#bitstring) অবজেক্ট (আগে সাধারণ স্ট্রিং)। `BitString` আসলে `str`-এর subclass, তাই পুরোনো স্ট্রিং-তুলনা কোড চলতে থাকে।

**উদাহরণ:**

```python
v = rt(BIT(4), BitString("1010"))
print(repr(v), v == "1010")   # BitString("1010") True
print(pgt(BIT()), pgt(BIT(8, varying=True)))   # BIT(1) BIT VARYING(8)
```

### কনস্ট্রাক্টরের প্যারামিটার { #bit-params }

```python
BIT(length=None, varying=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | বিটের সংখ্যা (`BIT` হলে না দিলে ১; `varying` হলে সর্বোচ্চ)। |
| `varying` | `True` দিলে `BIT VARYING` (দৈর্ঘ্য কম হতে পারে)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TypeEngine`](types.md#typeengine-summary)-এর মতো।

## `BitString` { #bitstring }

```python
from sqlalchemy.dialects.postgresql import BitString
```

(২.১-এ নতুন) `BIT` কলামের Python মান: `'0'`/`'1'` দিয়ে তৈরি একটি `str`। বানাতে `BitString("1010")` (অন্য অক্ষর থাকলে `ValueError`; দ্বিতীয় আর্গুমেন্ট `False` দিলে যাচাই বাদ)। বিট-অপারেটর চলে: `&`, `|`, `^`, `~`, `<<`, `>>` (দৈর্ঘ্য একই থাকে); `+` জোড়া লাগায়। index 0 হলো **সবচেয়ে বাঁয়ের** বিট।

**উদাহরণ:**

```python
b = BitString("1010")
print(b & BitString("0110"), b | BitString("0101"), ~b, b << 1)   # 0010 1111 0101 0100
try:
    BitString("102")
except ValueError as e:
    print(e)   # BitString must only contain '0' and '1' chars
```

**Python `str`-এর সব মেথড** (`capitalize()`, `casefold()`, `center()`, `count()`, `encode()`, `endswith()`, `expandtabs()`, `find()`, `format()`, `format_map()`, `index()`, `isalnum()`, `isalpha()`, `isascii()`, `isdecimal()`, `isdigit()`, `isidentifier()`, `islower()`, `isnumeric()`, `isprintable()`, `isspace()`, `istitle()`, `isupper()`, `join()`, `ljust()`, `lower()`, `lstrip()`, `maketrans()`, `partition()`, `removeprefix()`, `removesuffix()`, `replace()`, `rfind()`, `rindex()`, `rjust()`, `rpartition()`, `rsplit()`, `rstrip()`, `split()`, `splitlines()`, `startswith()`, `strip()`, `swapcase()`, `title()`, `translate()`, `upper()`, `zfill()`) সাধারণ `str`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #bitstring-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`bit_length`](#bitstring-bit-length) | প্রপার্টি | বিটের সংখ্যা (স্ট্রিংয়ের দৈর্ঘ্য)। |
| [`from_bytes()`](#bitstring-from-bytes) | ক্লাস মেথড | (ক্লাস মেথড) `bytes` থেকে বানায়; প্রতি বাইট ৮ বিট। |
| [`from_int()`](#bitstring-from-int) | ক্লাস মেথড | (ক্লাস মেথড) অঋণাত্মক পূর্ণসংখ্যা থেকে, নির্দিষ্ট `length`-এর বিট-সারি (বাঁয়ে শূন্য দিয়ে)। |
| [`get_bit()`](#bitstring-get-bit) | মেথড | `index`-এর বিট, `'0'` বা `'1'` হিসেবে (বাঁ দিক থেকে ০)। |
| [`has_bit()`](#bitstring-has-bit) | মেথড | `index`-এর বিট `1` কি না (`bool`)। |
| [`octet_length`](#bitstring-octet-length) | প্রপার্টি | কত বাইট লাগবে (বিট ÷ ৮, ওপরে গোল করা)। |
| [`set_bit()`](#bitstring-set-bit) | মেথড | `index`-এর বিট বদলে **নতুন** `BitString` দেয় (মূলটি বদলায় না, কারণ `str` অপরিবর্তনীয়)। |
| [`to_bytes()`](#bitstring-to-bytes) | মেথড | `bytes`-এ রূপান্তর (দরকার হলে বাঁয়ে শূন্য বসিয়ে)। |

### `BitString.bit_length` { #bitstring-bit-length }

**ধরন:** প্রপার্টি

বিটের সংখ্যা (স্ট্রিংয়ের দৈর্ঘ্য)।

**উদাহরণ:**

```python
print(BitString("1010").bit_length)   # 4
```

### `BitString.from_bytes()` { #bitstring-from-bytes }

```python
BitString.from_bytes(value, length=-1)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) `bytes` থেকে বানায়; প্রতি বাইট ৮ বিট। `length` দিলে ডান দিকের ততগুলো বিট রাখে।

**উদাহরণ:**

```python
print(BitString.from_bytes(b"\x0f"), BitString.from_bytes(b"\x0f", 4))   # 00001111 1111
```

### `BitString.from_int()` { #bitstring-from-int }

```python
BitString.from_int(value, length)
```

**ধরন:** ক্লাস মেথড

(ক্লাস মেথড) অঋণাত্মক পূর্ণসংখ্যা থেকে, নির্দিষ্ট `length`-এর বিট-সারি (বাঁয়ে শূন্য দিয়ে)। ঋণাত্মক হলে `ValueError`।

**উদাহরণ:**

```python
print(BitString.from_int(5, 4), BitString.from_int(5, 8))   # 0101 00000101
```

### `BitString.get_bit()` { #bitstring-get-bit }

```python
BitString.get_bit(index)
```

**ধরন:** মেথড

`index`-এর বিট, `'0'` বা `'1'` হিসেবে (বাঁ দিক থেকে ০)।

**উদাহরণ:**

```python
print(BitString("1010").get_bit(0), BitString("1010").get_bit(1))   # 1 0
```

### `BitString.has_bit()` { #bitstring-has-bit }

```python
BitString.has_bit(index)
```

**ধরন:** মেথড

`index`-এর বিট `1` কি না (`bool`)।

**উদাহরণ:**

```python
print(BitString("1010").has_bit(2))   # True
```

### `BitString.octet_length` { #bitstring-octet-length }

**ধরন:** প্রপার্টি

কত বাইট লাগবে (বিট ÷ ৮, ওপরে গোল করা)।

**উদাহরণ:**

```python
print(BitString("1010").octet_length, BitString("1" * 9).octet_length)   # 1 2
```

### `BitString.set_bit()` { #bitstring-set-bit }

```python
BitString.set_bit(index, value)
```

**ধরন:** মেথড

`index`-এর বিট বদলে **নতুন** `BitString` দেয় (মূলটি বদলায় না, কারণ `str` অপরিবর্তনীয়)। মান `True`/`False`, `0`/`1` বা `'0'`/`'1'`।

**উদাহরণ:**

```python
b = BitString("1010")
print(b.set_bit(3, 1), b)   # 1011 1010
```

### `BitString.to_bytes()` { #bitstring-to-bytes }

```python
BitString.to_bytes(length=-1)
```

**ধরন:** মেথড

`bytes`-এ রূপান্তর (দরকার হলে বাঁয়ে শূন্য বসিয়ে)। `length` দিলে ততগুলো বাইট।

**উদাহরণ:**

```python
print(BitString("00001111").to_bytes(), BitString("1010").to_bytes(2))   # b'\x0f' b'\x00\n'
```

## `BYTEA` { #bytea }

```python
from sqlalchemy.dialects.postgresql import BYTEA
```

বাইনারি ডেটা (`bytes`)। সাধারণ `LargeBinary` PostgreSQL-এ এটাই হয়; সরাসরি দরকার কম।

**উদাহরণ:**

```python
print(pgt(BYTEA()), pgt(LargeBinary()), rt(BYTEA, b"\x00\x01"))   # BYTEA BYTEA b'\x00\x01'
```

### কনস্ট্রাক্টরের প্যারামিটার { #bytea-params }

```python
BYTEA(length=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `length` | দৈর্ঘ্য (PostgreSQL BYTEA-তে উপেক্ষিত)। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`LargeBinary`](types.md#largebinary-summary)-এর মতো।

## `INTERVAL` { #interval }

```python
from sqlalchemy.dialects.postgresql import INTERVAL
```

সময়ের ব্যবধান, Python `datetime.timedelta`। সাধারণ `Interval` PostgreSQL-এ এটাই হয়। বাড়তি সুবিধা: `fields` (যেমন শুধু `DAY TO SECOND`) আর সেকেন্ডের `precision`।

**উদাহরণ:**

```python
print(rt(INTERVAL, datetime.timedelta(days=2, hours=3)))   # 2 days, 3:00:00
print(rt(INTERVAL(precision=2), datetime.timedelta(seconds=1.2345)))   # 0:00:01.230000  (দুই দশমিক)
print(pgt(INTERVAL(fields="YEAR TO MONTH")))   # INTERVAL YEAR TO MONTH
```

### কনস্ট্রাক্টরের প্যারামিটার { #interval-params }

```python
INTERVAL(precision=None, fields=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `precision` | সেকেন্ডের দশমিক অঙ্ক (০–৬)। |
| `fields` | কোন অংশ রাখবে: `"YEAR"`, `"DAY TO SECOND"`, `"HOUR TO MINUTE"` ইত্যাদি। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #interval-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adapt_emulated_to_native()`](#interval-adapt-emulated-to-native) | ক্লাস মেথড (internal) | (ক্লাস মেথড) সাধারণ `Interval` থেকে PostgreSQL `INTERVAL` বানায় (`second_precision` → `precision`)। |
| [`adapt_native_to_emulated()`](#interval-adapt-native-to-emulated) | ক্লাস মেথড (internal) | (ক্লাস মেথড) native থেকে emulated টাইপে অভিযোজন; ভেতরের ব্যবহারের জন্য। |
| [`fields`](#interval-fields) | অ্যাট্রিবিউট | `fields` প্যারামিটারের মান বা `None`। |
| [`native`](#interval-native) | অ্যাট্রিবিউট | native টাইপ কি না: সবসময় `True`। |
| [`precision`](#interval-precision) | অ্যাট্রিবিউট | সেকেন্ডের precision বা `None`। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ২৬টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `INTERVAL`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`TypeEngine` থেকে:** [`Comparator`](types.md#typeengine-Comparator) · [`adapt()`](types.md#typeengine-adapt) · [`as_generic()`](types.md#typeengine-as-generic) · [`bind_expression()`](types.md#typeengine-bind-expression) · [`bind_processor()`](types.md#typeengine-bind-processor) · [`coerce_compared_value()`](types.md#typeengine-coerce-compared-value) · [`column_expression()`](types.md#typeengine-column-expression) · [`comparator_factory`](types.md#typeengine-comparator-factory) · [`compare_values()`](types.md#typeengine-compare-values) · [`compile()`](types.md#typeengine-compile) · [`copy()`](types.md#typeengine-copy) · [`copy_value()`](types.md#typeengine-copy-value) · [`dialect_impl()`](types.md#typeengine-dialect-impl) · [`evaluates_none()`](types.md#typeengine-evaluates-none) · [`get_dbapi_type()`](types.md#typeengine-get-dbapi-type) · [`hashable`](types.md#typeengine-hashable) · [`literal_processor()`](types.md#typeengine-literal-processor) · [`operator_classes`](types.md#typeengine-operator-classes) · [`python_type`](types.md#typeengine-python-type) · [`render_bind_cast`](types.md#typeengine-render-bind-cast) · [`render_literal_cast`](types.md#typeengine-render-literal-cast) · [`repr_struct()`](types.md#typeengine-repr-struct) · [`result_processor()`](types.md#typeengine-result-processor) · [`should_evaluate_none`](types.md#typeengine-should-evaluate-none) · [`sort_key_function`](types.md#typeengine-sort-key-function) · [`with_variant()`](types.md#typeengine-with-variant)

///

### `INTERVAL.adapt_emulated_to_native()` { #interval-adapt-emulated-to-native }

```python
INTERVAL.adapt_emulated_to_native(interval, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) সাধারণ `Interval` থেকে PostgreSQL `INTERVAL` বানায় (`second_precision` → `precision`)।

**উদাহরণ:**

```python
print(INTERVAL.adapt_emulated_to_native(Interval(second_precision=3)).precision)   # 3
```

### `INTERVAL.adapt_native_to_emulated()` { #interval-adapt-native-to-emulated }

```python
INTERVAL.adapt_native_to_emulated(impl, **kw)
```

**ধরন:** ক্লাস মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

(ক্লাস মেথড) native থেকে emulated টাইপে অভিযোজন; ভেতরের ব্যবহারের জন্য।

**উদাহরণ:**

```python
print(callable(INTERVAL.adapt_native_to_emulated))   # True
```

### `INTERVAL.fields` { #interval-fields }

**ধরন:** অ্যাট্রিবিউট

`fields` প্যারামিটারের মান বা `None`।

**উদাহরণ:**

```python
print(INTERVAL(fields="DAY TO SECOND").fields)   # DAY TO SECOND
```

### `INTERVAL.native` { #interval-native }

**ধরন:** অ্যাট্রিবিউট

native টাইপ কি না: সবসময় `True`।

**উদাহরণ:**

```python
print(INTERVAL().native)   # True
```

### `INTERVAL.precision` { #interval-precision }

**ধরন:** অ্যাট্রিবিউট

সেকেন্ডের precision বা `None`।

**উদাহরণ:**

```python
print(INTERVAL(precision=2).precision)   # 2
```

## `TIMESTAMP` { #timestamp }

```python
from sqlalchemy.dialects.postgresql import TIMESTAMP
```

সাধারণ `TIMESTAMP`-এর PostgreSQL রূপ, বাড়তি `precision` (সেকেন্ডের দশমিক অঙ্ক, ০–৬)।

**উদাহরণ:**

```python
print(pgt(TIMESTAMP(timezone=True, precision=0)))   # TIMESTAMP(0) WITH TIME ZONE
v = rt(TIMESTAMP(precision=0), datetime.datetime(2025, 1, 1, 10, 0, 0, 600000))
print(v)   # 2025-01-01 10:00:01  (গোল হয়ে গেছে)
```

### কনস্ট্রাক্টরের প্যারামিটার { #timestamp-params }

```python
TIMESTAMP(timezone=False, precision=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | `True` দিলে `WITH TIME ZONE` (`timestamptz`)। |
| `precision` | সেকেন্ডের দশমিক অঙ্ক। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TIMESTAMP`](types.md#timestamp)-এর মতো, অর্থাৎ [`DateTime`](types.md#datetime-summary)-এর মতো।

## `TIME` { #time }

```python
from sqlalchemy.dialects.postgresql import TIME
```

সাধারণ `TIME`-এর PostgreSQL রূপ, বাড়তি `precision`।

**উদাহরণ:**

```python
print(pgt(TIME(precision=2)), rt(TIME(precision=1), datetime.time(10, 0, 0, 560000)))   # TIME(2) WITHOUT TIME ZONE 10:00:00.600000
```

### কনস্ট্রাক্টরের প্যারামিটার { #time-params }

```python
TIME(timezone=False, precision=None)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `timezone` | `True` দিলে `WITH TIME ZONE`। |
| `precision` | সেকেন্ডের দশমিক অঙ্ক। |

**সদস্য:** নিজস্ব নতুন কোনো সদস্য নেই; সব মেথড ও অ্যাট্রিবিউট [`TIME`](types.md#sql-time)-এর মতো, অর্থাৎ [`DateTime`](types.md#datetime-summary)-এর মতো।

## সাধারণ টাইপ, PostgreSQL মডিউল থেকে { #generic-reexports }

নিচের নামগুলো `from sqlalchemy.dialects.postgresql import ...` দিয়েও পাওয়া যায়, কিন্তু এগুলো **হুবহু একই** সাধারণ টাইপ (`postgresql.INTEGER is sqlalchemy.INTEGER` → `True`)। ব্যাখ্যা ও সব মেথড [টাইপ পেজে](types.md):

| নাম | কোথায় দেখবেন |
| :--- | :--- |
| `INTEGER`, `SMALLINT`, `BIGINT` | [`INTEGER`](types.md#sql-integer), [`SMALLINT`](types.md#smallint), [`BIGINT`](types.md#bigint) |
| `VARCHAR`, `CHAR`, `TEXT` | [`VARCHAR`](types.md#varchar), [`CHAR`](types.md#char), [`TEXT`](types.md#sql-text) |
| `NUMERIC`, `FLOAT`, `REAL`, `DOUBLE_PRECISION` | [`NUMERIC`](types.md#sql-numeric), [`FLOAT`](types.md#sql-float), [`REAL`](types.md#real), [`DOUBLE_PRECISION`](types.md#double-precision) |
| `DATE`, `BOOLEAN`, `UUID` | [`DATE`](types.md#sql-date), [`BOOLEAN`](types.md#sql-boolean), [`UUID`](types.md#sql-uuid) |
| `JSON`, `JSONB`, `ARRAY`, `HSTORE`, `JSONPATH` | PostgreSQL-এর নিজস্ব রূপ, [PostgreSQL API পেজে](postgresql.md) |
