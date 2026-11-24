# SQL এক্সপ্রেশন ফাংশন: and_, or_, case, cast, literal, exists … { #api-expressions }

/// note | এই পেজে যা আছে

`from sqlalchemy import ...` দিয়ে পাওয়া **সব** এক্সপ্রেশন-বানানোর ফাংশন:

* **শর্ত:** `and_()`, `or_()`, `not_()`
* **মান ও প্যারামিটার:** `literal()`, `literal_column()`, `column()`, `bindparam()`, `outparam()`, `null()`, `true()`, `false()`, `tuple_()`
* **টাইপ:** `cast()`, `try_cast()`, `type_coerce()`
* **অন্যান্য এক্সপ্রেশন:** `case()`, `extract()`, `collate()`, `label()`, `between()`, `distinct()`, `any_()`, `all_()`, `bitwise_not()`
* **ORDER BY:** `asc()`, `desc()`, `nulls_first()`, `nulls_last()` (আর পুরোনো নাম `nullsfirst()`, `nullslast()`)
* **সাবকুয়েরি ও FROM:** `exists()`, `table()`, `alias()`, `join()`, `outerjoin()`, `lateral()`, `tablesample()`, `cte()`
* **বিশেষ:** `lambda_stmt()`, `from_dml_column()` (২.১), `tstring()` (২.১), `Nullable()`, `NotNullable()`

এগুলো যে অবজেক্ট ফেরত দেয় (`ColumnElement`, `Case`, `Exists` …) তাদের মেথডগুলো আছে [SQL এক্সপ্রেশন ক্লাস](elements.md) পেজে। `func.count()`-এর মতো SQL ফাংশন আছে [func পেজে](functions.md)।

///

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

`User` (`id`, `name`, `email`, `age`, `joined` তারিখ) আর `Address` (`id`, `city`, `user_id`):

| id | name | email | age | joined | ঠিকানা |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ১ | রহিম | `rahim@example.com` | ৩০ | ২০২৪-০১-১৫ | ঢাকা, চট্টগ্রাম |
| ২ | করিম | `NULL` | ২৫ | ২০২৩-০৬-০১ | – |
| ৩ | সুমি | `sumi@example.com` | `NULL` | ২০২৫-০৩-১০ | ঢাকা |

`names(শর্ত)` শর্তে মেলা নামগুলো দেয় (id ক্রমে); `rows(স্টেটমেন্ট)` চালিয়ে সব রো দেয়; `pg(এক্সপ্রেশন)` PostgreSQL-এর আসল SQL দেখায় (মান বসিয়ে)। সব উদাহরণ PostgreSQL 16-এ চালিয়ে দেখা।

///

## শর্ত জোড়া { #and-group }

## `and_()` { #and }

```python
from sqlalchemy import and_
```

```python
and_(*clauses)
```

**ধরন:** ফাংশন

কয়েকটি শর্তকে `AND` দিয়ে জোড়ে। `where(a, b)` লিখলেও ভেতরে `and_(a, b)` হয়; তবে `or_()`-এর ভেতরে AND বসাতে, বা শর্তের তালিকা রানটাইমে বানাতে `and_(*শর্তগুলো)` কাজে লাগে। `&` অপারেটর একই কাজ করে।

**উদাহরণ:**

```python
print(names(and_(User.age > 20, User.email.is_not(None))))   # ['রহিম']
filters = [User.age >= 25, User.name != "রহিম"]                # রানটাইমে বানানো তালিকা
print(names(and_(*filters)))                                    # ['করিম']
```

### `and_()`-এর সব প্যারামিটার { #and-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | যে শর্তগুলো AND দিয়ে জুড়বে। একটিও না দিলে ২.০ থেকে সতর্কবার্তা দেয়; খালি তালিকা সম্ভব হলে `and_(true(), *filters)` লিখুন। |

## `or_()` { #or }

```python
from sqlalchemy import or_
```

```python
or_(*clauses)
```

**ধরন:** ফাংশন

কয়েকটি শর্তকে `OR` দিয়ে জোড়ে: যেকোনো একটি সত্য হলেই চলবে। `|` অপারেটর একই কাজ করে।

**উদাহরণ:**

```python
print(names(or_(User.age < 26, User.age.is_(None))))   # ['করিম', 'সুমি']
print(or_(User.id == 1, and_(User.age > 20, User.age < 30)))
# users.id = :id_1 OR users.age > :age_1 AND users.age < :age_2
```

### `or_()`-এর সব প্যারামিটার { #or-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | যে শর্তগুলো OR দিয়ে জুড়বে। খালি তালিকা হতে পারলে `or_(false(), *filters)` লিখুন। |

## `not_()` { #not }

```python
from sqlalchemy import not_
```

```python
not_(clause)
```

**ধরন:** ফাংশন

শর্ত উল্টে দেয় (`NOT`)। `~` অপারেটর একই কাজ করে। SQLAlchemy যেখানে পারে সরাসরি উল্টো অপারেটর বসায় (`==` → `!=`, `IN` → `NOT IN`)।

**উদাহরণ:**

```python
print(not_(User.name == "রহিম"))                          # users.name != :name_1
print(names(not_(User.id.in_([1, 2]))))                  # ['সুমি']
```

### `not_()`-এর সব প্যারামিটার { #not-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clause` | যে শর্ত উল্টাতে হবে। |

## মান ও প্যারামিটার { #literal-group }

## `literal()` { #literal }

```python
from sqlalchemy import literal
```

```python
literal(value, type_=None, literal_execute=False)
```

**ধরন:** ফাংশন

একটি Python মানকে SQL এক্সপ্রেশন বানায় (bound parameter হিসেবে, তাই SQL injection-নিরাপদ)। যেখানে কলামের মতো এক্সপ্রেশন দরকার কিন্তু হাতে শুধু একটি মান, যেমন `select(literal(1))` বা মানের ওপর মেথড ডাকতে (`literal("ক").concat(...)`)।

**উদাহরণ:**

```python
print(session.scalar(select(literal(5) + 3)))                 # 8
print(rows(select(User.name, literal("সক্রিয়").label("status")).where(User.id == 1)))   # [('রহিম', 'সক্রিয়')]
```

### `literal()`-এর সব প্যারামিটার { #literal-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `value` | মান। |
| `type_` | SQL টাইপ (না দিলে Python মান থেকে অনুমান)। |
| `literal_execute` | `True` দিলে মানটি প্যারামিটার না হয়ে চালানোর মুহূর্তে SQL-এ সরাসরি বসে (কিছু ডেটাবেস কিছু জায়গায় প্যারামিটার নেয় না)। |

## `literal_column()` { #literal-column }

```python
from sqlalchemy import literal_column
```

```python
literal_column(text, type_=None)
```

**ধরন:** ফাংশন

একটি **কাঁচা SQL লেখাকে** কলামের মতো ব্যবহার করতে দেয়; লেখাটি হুবহু SQL-এ বসে, কোনো quoting বা প্যারামিটার ছাড়া। **ইউজারের ইনপুট কখনো দেবেন না** (SQL injection)।

**উদাহরণ:**

```python
print(select(literal_column("now()")))   # SELECT now()
print(session.scalar(select(literal_column("2 + 2", Integer))))   # 4
```

### `literal_column()`-এর সব প্যারামিটার { #literal-column-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `text` | কাঁচা SQL লেখা। |
| `type_` | ফলের SQL টাইপ (রেজাল্ট রূপান্তর ও অপারেটরের জন্য)। |

## `column()` { #column }

```python
from sqlalchemy import column
```

```python
column(text, type_=None, is_literal=False)
```

**ধরন:** ফাংশন

একটি "হালকা" কলাম বানায়, কোনো `Table` বা মডেল ছাড়াই: শুধু নাম (আর ঐচ্ছিক টাইপ)। `table()`-এর সাথে বা `text()` কুয়েরির কলাম বর্ণনায় কাজে লাগে। নাম প্রয়োজনে quote হয়।

**উদাহরণ:**

```python
users = table("users", column("id"), column("name"))
print(rows(select(users.c.name).where(users.c.id == 2)))   # [('করিম',)]
```

### `column()`-এর সব প্যারামিটার { #column-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `text` | কলামের নাম। |
| `type_` | SQL টাইপ। |
| `is_literal` | `True` দিলে নামটি quote ছাড়া হুবহু বসে (`literal_column()`-এর মতো)। |

## `bindparam()` { #bindparam }

```python
from sqlalchemy import bindparam
```

```python
bindparam(key, value=_NoArg.NO_ARG, type_=None, unique=False, required=_NoArg.NO_ARG, quote=None, callable_=None, expanding=False, isoutparam=False, literal_execute=False)
```

**ধরন:** ফাংশন

একটি **নামযুক্ত প্যারামিটার** (`:নাম`) বানায়, যার মান পরে `execute()`-এর সময় দেওয়া হয়। একই স্টেটমেন্ট বারবার ভিন্ন মানে চালাতে, `executemany`-তে, আর `IN`-এর তালিকা পরে দিতে (`expanding=True`)।

**উদাহরণ:**

```python
stmt = select(User.name).where(User.age > bindparam("min_age"))
print(session.scalars(stmt, {"min_age": 26}).all())   # ['রহিম']
print(session.scalars(stmt, {"min_age": 20}).all())   # ['রহিম', 'করিম']
```

### `bindparam()`-এর সব প্যারামিটার { #bindparam-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | প্যারামিটারের নাম। |
| `value` | ডিফল্ট মান (execute-এ না দিলে এটি)। |
| `type_` | SQL টাইপ। |
| `unique` | `True` দিলে নামের শেষে সংখ্যা জুড়ে অনন্য করে (একই স্টেটমেন্টে কয়েকবার ব্যবহার হলে)। |
| `required` | `True` হলে execute-এ মান না দিলে এরর। মান না দিলে ডিফল্টে `True`। |
| `quote` | নামটি quote হবে কি না (ডায়ালেক্টের জন্য)। |
| `callable_` | মানের বদলে একটি ফাংশন, যা চালানোর সময় ডেকে মান নেওয়া হয়। |
| `expanding` | `True` দিলে `IN` তালিকার জন্য: execute-এ একটি তালিকা দিন, SQLAlchemy সেটিকে কয়েকটি প্যারামিটারে ভাঙে। |
| `isoutparam` | stored procedure-এর OUT প্যারামিটার (`outparam()` দেখুন)। |
| `literal_execute` | মানটি প্যারামিটার না হয়ে চালানোর সময় SQL-এ সরাসরি বসবে। |

**IN-এর তালিকা পরে দেওয়া (expanding)**

```python
stmt = select(User.name).where(User.id.in_(bindparam("ids", expanding=True))).order_by(User.id)
print(session.scalars(stmt, {"ids": [1, 3]}).all())   # ['রহিম', 'সুমি']
```

## `outparam()` { #outparam }

```python
from sqlalchemy import outparam
```

```python
outparam(key, type_=None)
```

**ধরন:** ফাংশন

stored procedure / ফাংশনের **OUT প্যারামিটার** বানায় (যেসব ডেটাবেস সমর্থন করে, মূলত Oracle)। চালানোর পর মান পাওয়া যায় `result.out_parameters` থেকে। PostgreSQL-এ সাধারণত দরকার হয় না (ফাংশন সরাসরি মান ফেরত দেয়)।

**উদাহরণ:**

```python
p = outparam("total", Integer)
print(p.isoutparam, p.key)   # True total
```

### `outparam()`-এর সব প্যারামিটার { #outparam-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `key` | প্যারামিটারের নাম। |
| `type_` | SQL টাইপ। |

## `null()` { #null }

```python
from sqlalchemy import null
```

```python
null()
```

**ধরন:** ফাংশন

SQL `NULL` এক্সপ্রেশন। সাধারণত `None` দিলেই চলে; কিন্তু JSON কলামে `None` মানে JSON `null` হতে পারে, তখন SQL NULL বোঝাতে `null()` লাগে। `select()` বা `case()`-এ স্পষ্ট NULL দরকার হলেও।

**উদাহরণ:**

```python
print(select(null()))                                   # SELECT NULL AS anon_1
print(names(User.email.is_(null())))                    # ['করিম']
```

## `true()` { #true }

```python
from sqlalchemy import true
```

```python
true()
```

**ধরন:** ফাংশন

SQL `true` (যেসব ডেটাবেসে বুলিয়ান নেই সেখানে `1 = 1`)। রানটাইমে শর্তের তালিকা খালি হতে পারলে `and_(true(), *filters)` লিখুন।

**উদাহরণ:**

```python
filters = []
print(names(and_(true(), *filters)))   # ['রহিম', 'করিম', 'সুমি']
```

## `false()` { #false }

```python
from sqlalchemy import false
```

```python
false()
```

**ধরন:** ফাংশন

SQL `false` (বুলিয়ান না থাকলে `0 = 1`)। "কিছুই মিলবে না" শর্ত বা `or_(false(), *filters)`-এর শুরুর মান।

**উদাহরণ:**

```python
print(names(or_(false(), User.id == 2)))   # ['করিম']
print(names(false()))                      # []
```

## `tuple_()` { #tuple- }

```python
from sqlalchemy import tuple_
```

```python
tuple_(*clauses, types=None)
```

**ধরন:** ফাংশন

কয়েকটি এক্সপ্রেশনের SQL tuple `(a, b)`। composite key দিয়ে `IN` করতে, বা "keyset pagination"-এ কয়েকটি কলাম একসাথে তুলনা করতে।

**উদাহরণ:**

```python
print(names(tuple_(User.id, User.name).in_([(1, "রহিম"), (3, "ভুল নাম")])))   # ['রহিম']
print(names(tuple_(User.age, User.id) > (25, 2)))                              # ['রহিম']  (keyset: (৩০, ১) > (২৫, ২))
```

### `tuple_()`-এর সব প্যারামিটার { #tuple--params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `clauses` | tuple-এর এক্সপ্রেশনগুলো। |
| `types` | প্রতিটি অবস্থানের SQL টাইপ (তুলনার মানগুলোর জন্য)। |

## টাইপ বদল { #cast-group }

## `cast()` { #cast }

```python
from sqlalchemy import cast
```

```python
cast(expression, type_)
```

**ধরন:** ফাংশন

`CAST(x AS টাইপ)`: ডেটাবেসে মানের টাইপ বদলায়। রেজাল্টও সেই টাইপে রূপান্তর হয়। এক্সপ্রেশনের মেথড হিসেবেও লেখা যায়: `User.age.cast(String)`।

**উদাহরণ:**

```python
print(cast(User.age, String))                                          # CAST(users.age AS VARCHAR)
print(session.scalar(select(cast("42", Integer) + 1)))                # 43
print(rows(select(cast(User.joined, String)).where(User.id == 1)))    # [('2024-01-15',)]
```

### `cast()`-এর সব প্যারামিটার { #cast-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expression` | যে এক্সপ্রেশন বা মানের টাইপ বদলাবে। |
| `type_` | লক্ষ্য SQL টাইপ। |

## `try_cast()` { #try-cast }

```python
from sqlalchemy import try_cast
```

```python
try_cast(expression, type_)
```

**ধরন:** ফাংশন

`TRY_CAST`: `CAST`-এর মতো, কিন্তু রূপান্তর না হলে এরর না দিয়ে NULL দেয়। বর্তমানে **শুধু SQL Server** ডায়ালেক্টে সমর্থিত; অন্য ডেটাবেসে কম্পাইল এরর।

**উদাহরণ:**

```python
print(try_cast(column("v"), Integer).compile(dialect=mssql.dialect()))   # TRY_CAST (v AS INTEGER)
```

### `try_cast()`-এর সব প্যারামিটার { #try-cast-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expression` | এক্সপ্রেশন। |
| `type_` | লক্ষ্য টাইপ। |

## `type_coerce()` { #type-coerce }

```python
from sqlalchemy import type_coerce
```

```python
type_coerce(expression, type_)
```

**ধরন:** ফাংশন

SQL-এ **কোনো CAST না বসিয়ে** শুধু SQLAlchemy-কে বলে "এই এক্সপ্রেশনটিকে এই টাইপ হিসেবে ধরো"। ফলে রেজাল্ট রূপান্তর আর অপারেটর সেই টাইপের নিয়মে হয় (যেমন `TypeDecorator`-এর `process_result_value` চলে, বা JSON অপারেটর পাওয়া যায়)।

**উদাহরণ:**

```python
class Upper(TypeDecorator):
    impl = String
    cache_ok = True
    def process_result_value(self, value, dialect):
        return value.upper() if value else value

print(type_coerce(User.email, Upper))                                   # users.email  (SQL-এ কিছু বসেনি)
print(session.scalar(select(type_coerce(User.email, Upper)).where(User.id == 1)))   # RAHIM@EXAMPLE.COM
```

### `type_coerce()`-এর সব প্যারামিটার { #type-coerce-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expression` | এক্সপ্রেশন। |
| `type_` | যে টাইপ হিসেবে ধরা হবে। |

## CASE ও অন্যান্য এক্সপ্রেশন { #case-group }

## `case()` { #case }

```python
from sqlalchemy import case
```

```python
case(*whens, value=None, else_=None)
```

**ধরন:** ফাংশন

SQL `CASE WHEN ... THEN ... ELSE ... END`: শর্ত অনুযায়ী ভিন্ন মান। প্রতিটি `(শর্ত, মান)` tuple একটি `WHEN`। `value=` দিলে "simple CASE": একটি কলামের মানের সাথে মিলিয়ে, তখন `whens` একটি dict হতে পারে।

**উদাহরণ:**

```python
group = case((User.age < 26, "তরুণ"), (User.age >= 26, "অভিজ্ঞ"), else_="অজানা").label("group")
print(rows(select(User.name, group).order_by(User.id)))
# [('রহিম', 'অভিজ্ঞ'), ('করিম', 'তরুণ'), ('সুমি', 'অজানা')]
```

### `case()`-এর সব প্যারামিটার { #case-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `whens` | `(শর্ত, মান)` tuple-গুলো; `value=` দিলে `{মান: ফল}` dict বা `(মান, ফল)` tuple। |
| `value` | simple CASE-এর জন্য যে কলামের সাথে মিলানো হবে। |
| `else_` | কোনো WHEN না মিললে যে মান (না দিলে NULL)। |

**simple CASE: dict দিয়ে**

```python
label = case({1: "এক", 2: "দুই"}, value=User.id, else_="অন্য")
print(session.scalars(select(label).order_by(User.id)).all())   # ['এক', 'দুই', 'অন্য']
```

**CASE দিয়ে কাস্টম ক্রম আর শর্তসাপেক্ষ গণনা**

```python
print(session.scalars(select(User.name).order_by(case((User.name == "সুমি", 0), else_=1), User.id)).all())
# ['সুমি', 'রহিম', 'করিম']
print(session.scalar(select(func.count(case((User.age >= 25, 1))))))   # 2
```

## `extract()` { #extract }

```python
from sqlalchemy import extract
```

```python
extract(field, expr)
```

**ধরন:** ফাংশন

তারিখ/সময় থেকে একটি অংশ বের করে: `EXTRACT(year FROM joined)`। ক্ষেত্রের নাম: `"year"`, `"month"`, `"day"`, `"hour"`, `"minute"`, `"second"`, `"dow"` (সপ্তাহের দিন), `"epoch"` ইত্যাদি।

**উদাহরণ:**

```python
print(names(extract("year", User.joined) >= 2024))           # ['রহিম', 'সুমি']
print(rows(select(extract("month", User.joined)).where(User.id == 2)))   # [(Decimal('6'),)]
```

### `extract()`-এর সব প্যারামিটার { #extract-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `field` | যে অংশ চাই (`"year"`, `"month"` …)। |
| `expr` | তারিখ/সময়ের এক্সপ্রেশন। |

## `collate()` { #collate }

```python
from sqlalchemy import collate
```

```python
collate(expression, collation, collation_schema=None)
```

**ধরন:** ফাংশন

এক্সপ্রেশনে `COLLATE` বসায়: তুলনা ও সাজানোর নিয়ম (যেমন `"C"` = বাইট-ক্রম)। মেথড রূপ: `User.name.collate("C")`।

**উদাহরণ:**

```python
pg(collate(User.name, "C"))   # users.name COLLATE "C"
```

### `collate()`-এর সব প্যারামিটার { #collate-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expression` | এক্সপ্রেশন। |
| `collation` | collation-এর নাম। |
| `collation_schema` | (২.১-এ নতুন) collation যে স্কিমায় আছে, যেমন PostgreSQL-এ `pg_catalog`। |

## `label()` { #label }

```python
from sqlalchemy import label
```

```python
label(name, element, type_=None)
```

**ধরন:** ফাংশন

এক্সপ্রেশনকে একটি নাম দেয়: `expr AS নাম`। মেথড রূপ `expr.label("নাম")` বেশি প্রচলিত।

**উদাহরণ:**

```python
row = session.execute(select(label("years", User.age + 1)).where(User.id == 1)).one()
print(row.years)   # 31
```

### `label()`-এর সব প্যারামিটার { #label-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | নাম। |
| `element` | এক্সপ্রেশন। |
| `type_` | ফলের টাইপ (ঐচ্ছিক)। |

## `between()` { #between }

```python
from sqlalchemy import between
```

```python
between(expr, lower_bound, upper_bound, symmetric=False)
```

**ধরন:** ফাংশন

`x BETWEEN a AND b` (দুই সীমাসহ)। মেথড রূপ: `User.age.between(a, b)`।

**উদাহরণ:**

```python
print(names(between(User.joined, datetime.date(2024, 1, 1), datetime.date(2024, 12, 31))))   # ['রহিম']
```

### `between()`-এর সব প্যারামিটার { #between-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | যে এক্সপ্রেশন যাচাই হবে। |
| `lower_bound` | নিচের সীমা। |
| `upper_bound` | ওপরের সীমা। |
| `symmetric` | `True` দিলে `BETWEEN SYMMETRIC` (সীমা উল্টো দিলেও চলে)। |

## `distinct()` { #distinct }

```python
from sqlalchemy import distinct
```

```python
distinct(expr)
```

**ধরন:** ফাংশন

একটি এক্সপ্রেশনের আগে `DISTINCT` বসায়, সাধারণত aggregate-এর ভেতরে: `func.count(distinct(col))`। পুরো SELECT-কে distinct করতে `select(...).distinct()` লিখুন।

**উদাহরণ:**

```python
print(session.scalar(select(func.count(distinct(Address.city)))))   # 2
```

### `distinct()`-এর সব প্যারামিটার { #distinct-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | এক্সপ্রেশন। |

## `any_()` { #any-func }

```python
from sqlalchemy import any_
```

```python
any_(expr)
```

**ধরন:** ফাংশন

`ANY (অ্যারে বা সাবকুয়েরি)`: তুলনার ডান দিকে বসে; যেকোনো একটির সাথে মিললেই সত্য। মেথড রূপ `col.any_()`।

**উদাহরণ:**

```python
sub = select(Address.user_id).scalar_subquery()
print(names(User.id == any_(sub)))   # ['রহিম', 'সুমি']
```

### `any_()`-এর সব প্যারামিটার { #any-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | অ্যারে এক্সপ্রেশন বা সাবকুয়েরি। |

## `all_()` { #all-func }

```python
from sqlalchemy import all_
```

```python
all_(expr)
```

**ধরন:** ফাংশন

`ALL (অ্যারে বা সাবকুয়েরি)`: **সব** মানের সাথে তুলনা সত্য হতে হবে।

**উদাহরণ:**

```python
younger = select(User.age).where(User.age.is_not(None)).scalar_subquery()
print(names(User.age >= all_(younger)))   # ['রহিম']  (সবচেয়ে বেশি বয়স)
```

### `all_()`-এর সব প্যারামিটার { #all-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | অ্যারে এক্সপ্রেশন বা সাবকুয়েরি। |

## `bitwise_not()` { #bitwise-not-func }

```python
from sqlalchemy import bitwise_not
```

```python
bitwise_not(expr)
```

**ধরন:** ফাংশন

বিট-ভিত্তিক NOT (`~`); বুলিয়ান `not_()`-এর সাথে গুলিয়ে ফেলবেন না।

**উদাহরণ:**

```python
print(session.scalar(select(bitwise_not(literal(5)))))   # -6
```

### `bitwise_not()`-এর সব প্যারামিটার { #bitwise-not-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `expr` | পূর্ণসংখ্যার এক্সপ্রেশন। |

## ORDER BY সহায়ক { #asc-func-group }

## `asc()` { #asc-func }

```python
from sqlalchemy import asc
```

```python
asc(column)
```

**ধরন:** ফাংশন

`ORDER BY ... ASC` (ছোট থেকে বড়)। মেথড রূপ `col.asc()`।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(asc(User.joined))).all())   # ['করিম', 'রহিম', 'সুমি']
```

### `asc()`-এর সব প্যারামিটার { #asc-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | যে এক্সপ্রেশন দিয়ে সাজানো হবে। |

## `desc()` { #desc-func }

```python
from sqlalchemy import desc
```

```python
desc(column)
```

**ধরন:** ফাংশন

`ORDER BY ... DESC` (বড় থেকে ছোট)। লেবেলের নাম (স্ট্রিং) দিয়েও দেওয়া যায়: `desc("n")`।

**উদাহরণ:**

```python
stmt = (select(User.name, func.count(Address.id).label("n")).outerjoin(User.addresses)
        .group_by(User.name).order_by(desc("n"), User.name))
print(rows(stmt))   # [('রহিম', 2), ('সুমি', 1), ('করিম', 0)]
```

### `desc()`-এর সব প্যারামিটার { #desc-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | এক্সপ্রেশন বা লেবেলের নাম। |

## `nulls_first()` { #nulls-first-func }

```python
from sqlalchemy import nulls_first
```

```python
nulls_first(column)
```

**ধরন:** ফাংশন

`NULLS FIRST`: NULL মান সবার আগে। সাধারণত `asc()`/`desc()`-এর ফলের ওপর।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(nulls_first(desc(User.age)))).all())   # ['সুমি', 'রহিম', 'করিম']
```

### `nulls_first()`-এর সব প্যারামিটার { #nulls-first-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | সাজানোর এক্সপ্রেশন। |

## `nulls_last()` { #nulls-last-func }

```python
from sqlalchemy import nulls_last
```

```python
nulls_last(column)
```

**ধরন:** ফাংশন

`NULLS LAST`: NULL মান সবার শেষে। PostgreSQL-এ `DESC` করলে ডিফল্টে NULL আগে আসে; তখন এটি কাজে লাগে।

**উদাহরণ:**

```python
print(session.scalars(select(User.name).order_by(nulls_last(desc(User.age)))).all())   # ['রহিম', 'করিম', 'সুমি']
```

### `nulls_last()`-এর সব প্যারামিটার { #nulls-last-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | সাজানোর এক্সপ্রেশন। |

## `nullsfirst()` { #nullsfirst-func }

```python
from sqlalchemy import nullsfirst
```

```python
nullsfirst(column)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`nulls_first()`-এর পুরোনো নাম (একই ফাংশন)।

**উদাহরণ:**

```python
print(nullsfirst is nulls_first)   # True
```

### `nullsfirst()`-এর সব প্যারামিটার { #nullsfirst-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | সাজানোর এক্সপ্রেশন। |

## `nullslast()` { #nullslast-func }

```python
from sqlalchemy import nullslast
```

```python
nullslast(column)
```

**ধরন:** ফাংশন

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`nulls_last()`-এর পুরোনো নাম (একই ফাংশন)।

**উদাহরণ:**

```python
print(nullslast is nulls_last)   # True
```

### `nullslast()`-এর সব প্যারামিটার { #nullslast-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | সাজানোর এক্সপ্রেশন। |

## সাবকুয়েরি ও FROM { #exists-func-group }

## `exists()` { #exists-func }

```python
from sqlalchemy import exists
```

```python
exists()
```

**ধরন:** ফাংশন

`EXISTS (SELECT ...)`: সাবকুয়েরি অন্তত একটি রো দিলে সত্য। দুইভাবে লেখা যায়: `exists().where(...)`, বা একটি `select(...)` থেকে `.exists()`। বাইরের কুয়েরির টেবিলের সাথে নিজে থেকেই correlate হয়। ORM-এ রিলেশনশিপ থাকলে `User.addresses.any()` আরও সহজ।

**উদাহরণ:**

```python
has_dhaka = exists().where(Address.user_id == User.id, Address.city == "ঢাকা")
print(names(has_dhaka))                                           # ['রহিম', 'সুমি']
print(names(~select(Address.id).where(Address.user_id == User.id).exists()))   # ['করিম']
print(session.scalar(select(exists().where(User.age > 100))))   # False
```

## `table()` { #table }

```python
from sqlalchemy import table
```

```python
table(name, *columns, **kw)
```

**ধরন:** ফাংশন

একটি "হালকা" টেবিল (`TableClause`) বানায়, `MetaData` বা পূর্ণ `Table` ছাড়াই: শুধু নাম আর `column()`-গুলো। স্ক্রিপ্ট, মাইগ্রেশনে ডেটা বদলানো (Alembic-এ মডেল ইমপোর্ট না করে), বা দ্রুত কুয়েরির জন্য।

**উদাহরণ:**

```python
addrs = table("addresses", column("id"), column("city"))
print(session.execute(select(addrs.c.city).where(addrs.c.id == 2)).scalar())   # চট্টগ্রাম
```

### `table()`-এর সব প্যারামিটার { #table-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `name` | টেবিলের নাম। |
| `columns` | `column()` অবজেক্টগুলো। |
| `kw` | `schema="নাম"`: টেবিলটি কোন স্কিমায়। |

## `alias()` { #alias-func }

```python
from sqlalchemy import alias
```

```python
alias(selectable, name=None, flat=False)
```

**ধরন:** ফাংশন

Core টেবিল বা selectable-এর ছদ্মনাম (`AS নাম`), একই টেবিল দুবার ব্যবহারের জন্য। মেথড রূপ `table.alias("নাম")`। ORM মডেলে `aliased()` ব্যবহার করুন।

**উদাহরণ:**

```python
u2 = alias(User.__table__, "u2")
print(select(u2.c.name))   # SELECT u2.name FROM users AS u2
```

### `alias()`-এর সব প্যারামিটার { #alias-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | টেবিল বা অন্য FROM। |
| `name` | ছদ্মনাম। |
| `flat` | join-এর ক্ষেত্রে প্রতিটি টেবিলকে আলাদা alias দেয়। |

## `join()` { #core-join }

```python
from sqlalchemy import join
```

```python
join(left, right, onclause=None, isouter=False, full=False)
```

**ধরন:** ফাংশন

দুটি টেবিল/FROM-এর `JOIN` অবজেক্ট বানায় (`select_from()`-এ দিতে)। ON শর্ত না দিলে ফরেন কি থেকে বোঝে। ORM মডেলেও কাজ করে, তবে রিলেশনশিপ নাম দিয়ে ON দিতে [`sqlalchemy.orm.join()`](loading.md#orm-join) লাগে।

**উদাহরণ:**

```python
j = join(User.__table__, Address.__table__)
print(rows(select(User.name, Address.city).select_from(j).where(Address.id == 3)))   # [('সুমি', 'ঢাকা')]
```

### `join()`-এর সব প্যারামিটার { #core-join-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `left` | বাম দিক। |
| `right` | ডান দিক। |
| `onclause` | ON শর্ত। |
| `isouter` | `True` দিলে LEFT OUTER JOIN। |
| `full` | `True` দিলে FULL OUTER JOIN। |

## `outerjoin()` { #core-outerjoin }

```python
from sqlalchemy import outerjoin
```

```python
outerjoin(left, right, onclause=None, full=False)
```

**ধরন:** ফাংশন

LEFT OUTER JOIN (`join(..., isouter=True)`-এর ছোট রূপ)।

**উদাহরণ:**

```python
j = outerjoin(User.__table__, Address.__table__)
print(rows(select(User.name).select_from(j).where(Address.id.is_(None))))   # [('করিম',)]
```

### `outerjoin()`-এর সব প্যারামিটার { #core-outerjoin-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `left` | বাম দিক। |
| `right` | ডান দিক। |
| `onclause` | ON শর্ত। |
| `full` | `True` দিলে FULL OUTER JOIN। |

## `lateral()` { #lateral-func }

```python
from sqlalchemy import lateral
```

```python
lateral(selectable, name=None)
```

**ধরন:** ফাংশন

`LATERAL` সাবকুয়েরি: FROM-এ থাকা অবস্থায় বাইরের কুয়েরির আগের টেবিলের কলাম ব্যবহার করতে পারে। "প্রতিটি ইউজারের সর্বশেষ N টি ঠিকানা"-র মতো কাজে। বিস্তারিত: [অ্যাডভান্সড কুয়েরি](../advanced-queries.md#s29-3)।

**উদাহরণ:**

```python
latest = lateral(select(Address.city).where(Address.user_id == User.id).order_by(Address.id.desc()).limit(1),
                 name="latest")
print(rows(select(User.name, latest.c.city).join(latest, true()).order_by(User.id)))
# [('রহিম', 'চট্টগ্রাম'), ('সুমি', 'ঢাকা')]
```

### `lateral()`-এর সব প্যারামিটার { #lateral-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | সাবকুয়েরি (একটি `select()`)। |
| `name` | নাম। |

## `tablesample()` { #tablesample-func }

```python
from sqlalchemy import tablesample
```

```python
tablesample(selectable, sampling, name=None, seed=None)
```

**ধরন:** ফাংশন

`TABLESAMPLE`: বড় টেবিলের একটি র‍্যান্ডম অংশ থেকে পড়ে (আনুমানিক পরিসংখ্যানের জন্য)। শতাংশ দিন, বা `func.bernoulli(10)` / `func.system(10)`।

**উদাহরণ:**

```python
sample = tablesample(User.__table__, func.bernoulli(100), name="s", seed=func.random())
print(session.execute(select(func.count()).select_from(sample)).scalar())   # 3  (১০০% নমুনা)
```

### `tablesample()`-এর সব প্যারামিটার { #tablesample-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | টেবিল। |
| `sampling` | নমুনার শতাংশ বা নমুনা-পদ্ধতির ফাংশন। |
| `name` | alias-এর নাম। |
| `seed` | `REPEATABLE (seed)`: একই seed-এ একই নমুনা। |

## `cte()` { #cte-func }

```python
from sqlalchemy import cte
```

```python
cte(selectable, name=None, recursive=False)
```

**ধরন:** ফাংশন

`WITH নাম AS (...)` CTE বানায়; `select(...).cte()`-এর ফাংশন রূপ। CTE-র সব মেথড আছে [Select API পেজের CTE অংশে](select.md#cte)।

**উদাহরণ:**

```python
adults = cte(select(User.id, User.name).where(User.age >= 25), name="adults")
print(session.scalars(select(adults.c.name).order_by(adults.c.id)).all())   # ['রহিম', 'করিম']
```

### `cte()`-এর সব প্যারামিটার { #cte-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `selectable` | `select()` বা DML স্টেটমেন্ট। |
| `name` | CTE-র নাম। |
| `recursive` | `True` দিলে `WITH RECURSIVE`। |

## বিশেষ ফাংশন { #lambda-stmt-group }

## `lambda_stmt()` { #lambda-stmt }

```python
from sqlalchemy import lambda_stmt
```

```python
lambda_stmt(lmb, enable_tracking=True, track_closure_variables=True, track_on=None, global_track_bound_values=True, track_bound_values=True, lambda_cache=None)
```

**ধরন:** ফাংশন

একটি স্টেটমেন্টকে lambda-র ভেতরে বানায়, যাতে SQLAlchemy Python কোডের অবস্থান দেখে কম্পাইল করা SQL ক্যাশ করতে পারে; খুব ঘনঘন চলা কুয়েরিতে স্টেটমেন্ট বানানোর খরচ কমে। lambda-র বাইরের ভেরিয়েবল (যেমন `uid`) নিজে থেকেই bound parameter হয়। `+=` দিয়ে আরও অংশ যোগ করা যায়।

**উদাহরণ:**

```python
def get_name(uid):
    stmt = lambda_stmt(lambda: select(User.name))
    stmt += lambda s: s.where(User.id == uid)
    return session.scalar(stmt)

print(get_name(1), get_name(3))   # রহিম সুমি
```

### `lambda_stmt()`-এর সব প্যারামিটার { #lambda-stmt-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `lmb` | স্টেটমেন্ট ফেরত দেওয়া lambda। |
| `enable_tracking` | `False` দিলে বাইরের ভেরিয়েবল ট্র্যাক হয় না; lambda প্রতিবার নতুন করে চলে (ক্যাশ নেই)। |
| `track_closure_variables` | বাইরের ভেরিয়েবলগুলো ক্যাশ-key-তে ধরা হবে কি না। |
| `track_on` | ক্যাশ-key-তে বাড়তি কোন অবজেক্টগুলো ধরা হবে (tuple)। |
| `global_track_bound_values` | সব lambda-অংশে bound value ট্র্যাকিং চালু/বন্ধ। |
| `track_bound_values` | এই lambda-তে Python মানগুলো bound parameter হিসেবে ধরা হবে কি না। |
| `lambda_cache` | নিজের ক্যাশ dict (ডিফল্টে গ্লোবাল ক্যাশ)। |

## `from_dml_column()` { #from-dml-column }

```python
from sqlalchemy import from_dml_column
```

```python
from_dml_column(column)
```

**ধরন:** ফাংশন

(২.১-এ নতুন) INSERT/UPDATE-এ অন্য একটি কলামে যে মান বা এক্সপ্রেশন বসানো হচ্ছে, সেটিকেই আরেকটি কলামের মানে আবার ব্যবহার করতে দেয়। মূলত hybrid property-র bulk update আর event hook-এর জন্য।

**উদাহরণ:**

```python
t = User.__table__
stmt = update(t).values(age=t.c.age + 1, name=func.concat(t.c.name, " (", from_dml_column(t.c.age), ")")).where(t.c.id == 2)
session.execute(stmt)
print(session.scalar(select(User.name).where(User.id == 2)))   # করিম (26)
```

### `from_dml_column()`-এর সব প্যারামিটার { #from-dml-column-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `column` | যে কলামের নতুন মান/এক্সপ্রেশন পুনরায় ব্যবহার হবে। |

## `tstring()` { #tstring }

```python
from sqlalchemy import tstring
```

```python
tstring(template)
```

**ধরন:** ফাংশন

(২.১-এ নতুন, **Python 3.14+** লাগবে) Python-এর নতুন template string (`t"..."`) থেকে SQL বানায়। `{}`-এর ভেতরের সাধারণ মান নিরাপদ bound parameter হয়, আর SQLAlchemy অবজেক্ট (কলাম, টেবিল, এক্সপ্রেশন) সঠিক SQL হিসেবে বসে। `text()`-এর আধুনিক, injection-নিরাপদ বিকল্প।

```python
min_age = 25
stmt = tstring(t"SELECT {User.name} FROM {User.__table__} WHERE {User.age} > {min_age}")
session.execute(stmt).all()
# SELECT users.name FROM users WHERE users.age > :param_1
```

(এই উদাহরণটি এই পেজের অন্য উদাহরণের মতো চালিয়ে দেখা হয়নি, কারণ যাচাইয়ের পরিবেশে Python 3.13; t-string সিনট্যাক্স শুধু 3.14-এ আছে।)

### `tstring()`-এর সব প্যারামিটার { #tstring-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `template` | একটি `t"..."` template অবজেক্ট। |

## `Nullable()` { #nullable-func }

```python
from sqlalchemy import Nullable
```

```python
Nullable(val)
```

**ধরন:** ফাংশন

(২.০.২০-এ নতুন) শুধু **টাইপ চেকারের** জন্য: রানটাইমে কিছুই করে না, ইনপুট হুবহু ফেরত দেয়। outer join-এর ফলে যে কলাম/মডেল `None` হতে পারে, তা mypy/pyright-কে জানাতে।

**উদাহরণ:**

```python
stmt = select(User.name, Nullable(Address.city)).outerjoin(User.addresses).order_by(User.id, Address.id)
print(rows(stmt))   # [('রহিম', 'ঢাকা'), ('রহিম', 'চট্টগ্রাম'), ('করিম', None), ('সুমি', 'ঢাকা')]
```

### `Nullable()`-এর সব প্যারামিটার { #nullable-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `val` | কলাম বা মডেল। |

## `NotNullable()` { #notnullable-func }

```python
from sqlalchemy import NotNullable
```

```python
NotNullable(val)
```

**ধরন:** ফাংশন

(২.০.২০-এ নতুন) `Nullable()`-এর উল্টো, শুধু টাইপ চেকারের জন্য: `WHERE col IS NOT NULL` দেওয়ার পর কলামটি আর `None` হবে না, তা জানাতে। রানটাইমে কিছু করে না।

**উদাহরণ:**

```python
stmt = select(NotNullable(User.email)).where(User.email.is_not(None)).order_by(User.id)
print(session.scalars(stmt).all())   # ['rahim@example.com', 'sumi@example.com']
```

### `NotNullable()`-এর সব প্যারামিটার { #notnullable-func-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `val` | কলাম বা মডেল। |

/// check | সংক্ষেপে মনে রাখুন

* শর্তের তালিকা রানটাইমে: `and_(true(), *filters)` / `or_(false(), *filters)`।
* মান নিরাপদে: `literal()` / `bindparam()`; কাঁচা SQL (`literal_column()`, `text()`)-এ কখনো ইউজার ইনপুট নয়।
* `cast()` SQL-এ CAST বসায়; `type_coerce()` শুধু Python দিকের টাইপ বদলায়।
* শর্তসাপেক্ষ মান: `case((শর্ত, মান), ..., else_=...)`।
* অস্তিত্ব যাচাই: `exists().where(...)` বা ORM-এ `rel.any()` / `rel.has()`।
* NULL-এর অবস্থান: `nulls_first()` / `nulls_last()`।

///
