# Relationship Collection API: write-only, dynamic, dict আর নিজের collection { #api-collections }

/// note | এই পেজে যা আছে

one-to-many / many-to-many `relationship()`-এর "অনেক" দিকটা Python-এ কোন ধরনের জিনিস হবে, তার সব API:

* **বড় collection-এর জন্য:** ২.০-এর `WriteOnlyCollection` (`WriteOnlyMapped`), আর পুরোনো `AppenderQuery` (`DynamicMapped`, `lazy="dynamic"`)।
* **dict collection:** `attribute_keyed_dict()`, `column_keyed_dict()`, `keyfunc_mapping()`, `KeyFuncDict` (আর তাদের পুরোনো নাম)।
* **নিজের collection class:** `collection` ডেকোরেটর, `collection_adapter()`, `CollectionAdapter`, `bulk_replace()`, আর SQLAlchemy যে `InstrumentedList` / `InstrumentedSet` / `InstrumentedDict` ব্যবহার করে।

///

ডিফল্টে `Mapped[list["Post"]]` লিখলে collection একটি সাধারণ `list`-এর মতো (আসলে `InstrumentedList`): প্রথমবার পড়লে **সব** রো লোড হয়। কয়েকশো-কয়েক হাজার রো হলে সেটা ধীর; তখন **write-only** collection নিন, যা কখনো নিজে থেকে সব লোড করে না, বরং কুয়েরি বানিয়ে দেয়। সম্পর্কের মূল ধারণা: [Relationship অধ্যায়](../relationships.md)।

/// info | উদাহরণগুলোর জন্য ধরে নেওয়া সেটআপ

```python
class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: WriteOnlyMapped["Post"] = relationship()        # write-only
    notes: DynamicMapped["Note"] = relationship()          # dynamic (legacy)
    tags: Mapped[dict[str, "Tag"]] = relationship(
        collection_class=attribute_keyed_dict("word"), cascade="all, delete-orphan")

class Post(Base):   # id, title, author_id
class Note(Base):   # id, text, author_id
class Tag(Base):    # id, word, author_id
```

ডেটা: লেখক ১ "রহিম", তাঁর পোস্ট "প্রথম" ও "দ্বিতীয়", নোট "n1" ও "n2", ট্যাগ `py` ও `db`। `a = session.get(Author, 1)`। PostgreSQL 16-এ চালিয়ে দেখা।

///

## বড় collection: write-only ও dynamic { #writeonlycollection-group }

## `WriteOnlyCollection` { #writeonlycollection }

```python
from sqlalchemy.orm import WriteOnlyCollection
```

(২.০) `posts: WriteOnlyMapped["Post"] = relationship()` লিখলে `author.posts` এই অবজেক্ট। নাম যেমন বলে: **লেখা যায়** (`add()`, `remove()`), কিন্তু collection নিজে কখনো রো লোড করে না, তাই `for p in author.posts` বা `len()` চলে না (`TypeError`)। পড়তে হলে `author.posts.select()` দিয়ে একটি `Select` বানিয়ে নিজে চালান: যত বড়ই হোক, শুধু যতটুকু দরকার (WHERE, LIMIT, pagination) ততটুকু আনা যায়। **async-এ খুব কাজের**, কারণ lazy load-এর `MissingGreenlet` সমস্যা হয় না।

**উদাহরণ:**

```python
print(type(a.posts).__name__, titles())   # WriteOnlyCollection ['প্রথম', 'দ্বিতীয়']
try:
    list(a.posts)
except TypeError as e:
    print(str(e).split(";")[0])   # WriteOnly collections don't support iteration in-place
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #writeonlycollection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#writeonlycollection-add) | মেথড | একটি অবজেক্ট collection-এ যোগ করে; পরের flush-এ তার FK বসে (INSERT বা UPDATE)। |
| [`add_all()`](#writeonlycollection-add-all) | মেথড | কয়েকটি অবজেক্ট একসাথে যোগ করে। |
| [`attr`](#writeonlycollection-attr) | অ্যাট্রিবিউট (internal) | ভেতরের attribute implementation অবজেক্ট (কোন relationship)। |
| [`delete()`](#writeonlycollection-delete) | মেথড | এই লেখকের পোস্টগুলোর জন্য একটি বাল্ক `DELETE` স্টেটমেন্ট বানায় (`WHERE posts.author_id = 1` আগে থেকেই বসানো); আরও শর্ত `.where()` দিয়ে। |
| [`insert()`](#writeonlycollection-insert) | মেথড | (one-to-many-তে) এই লেখকের জন্য বাল্ক `INSERT` বানায়: `author_id` নিজে থেকে বসে। |
| [`instance`](#writeonlycollection-instance) | অ্যাট্রিবিউট | যে অবজেক্টের collection (এখানে লেখক `a`)। |
| [`remove()`](#writeonlycollection-remove) | মেথড | অবজেক্টটিকে collection থেকে সরায়: পরের flush-এ তার FK `NULL` হয় (মোছে না; মুছতে relationship-এ `cascade="all, delete-orphan"`)। |
| [`select()`](#writeonlycollection-select) | মেথড | এই collection-এর রোগুলোর জন্য একটি `Select` (`WHERE :param = posts.author_id`)। |
| [`update()`](#writeonlycollection-update) | মেথড | এই লেখকের পোস্টগুলোর জন্য বাল্ক `UPDATE` বানায়। |

### `WriteOnlyCollection.add()` { #writeonlycollection-add }

```python
WriteOnlyCollection.add(item)
```

**ধরন:** মেথড

একটি অবজেক্ট collection-এ যোগ করে; পরের flush-এ তার FK বসে (INSERT বা UPDATE)। আগের রোগুলো লোড হয় না।

**উদাহরণ:**

```python
a.posts.add(Post(title="তৃতীয়"))
session.flush()
print(titles())   # ['প্রথম', 'দ্বিতীয়', 'তৃতীয়']
```

### `WriteOnlyCollection.add_all()` { #writeonlycollection-add-all }

```python
WriteOnlyCollection.add_all(iterator)
```

**ধরন:** মেথড

কয়েকটি অবজেক্ট একসাথে যোগ করে।

**উদাহরণ:**

```python
a.posts.add_all([Post(title="ক"), Post(title="খ")])
session.flush()
print(len(titles()))   # 4
```

### `WriteOnlyCollection.attr` { #writeonlycollection-attr }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের attribute implementation অবজেক্ট (কোন relationship)।

**উদাহরণ:**

```python
print(a.posts.attr)   # Author.posts
```

### `WriteOnlyCollection.delete()` { #writeonlycollection-delete }

```python
WriteOnlyCollection.delete()
```

**ধরন:** মেথড

এই লেখকের পোস্টগুলোর জন্য একটি বাল্ক `DELETE` স্টেটমেন্ট বানায় (`WHERE posts.author_id = 1` আগে থেকেই বসানো); আরও শর্ত `.where()` দিয়ে। চালাতে `session.execute()`। ORM ইভেন্ট/cascade চলে না, সরাসরি SQL।

**উদাহরণ:**

```python
session.execute(a.posts.delete().where(Post.title == "দ্বিতীয়"))
print(titles())   # ['প্রথম']
```

### `WriteOnlyCollection.insert()` { #writeonlycollection-insert }

```python
WriteOnlyCollection.insert()
```

**ধরন:** মেথড

(one-to-many-তে) এই লেখকের জন্য বাল্ক `INSERT` বানায়: `author_id` নিজে থেকে বসে। হাজার হাজার রো দ্রুত ঢোকাতে।

**উদাহরণ:**

```python
session.execute(a.posts.insert(), [{"title": "x"}, {"title": "y"}])
print(titles())   # ['প্রথম', 'দ্বিতীয়', 'x', 'y']
```

### `WriteOnlyCollection.instance` { #writeonlycollection-instance }

**ধরন:** অ্যাট্রিবিউট

যে অবজেক্টের collection (এখানে লেখক `a`)।

**উদাহরণ:**

```python
print(a.posts.instance is a)   # True
```

### `WriteOnlyCollection.remove()` { #writeonlycollection-remove }

```python
WriteOnlyCollection.remove(item)
```

**ধরন:** মেথড

অবজেক্টটিকে collection থেকে সরায়: পরের flush-এ তার FK `NULL` হয় (মোছে না; মুছতে relationship-এ `cascade="all, delete-orphan"`)। অবজেক্টটি আগে লোড করা থাকতে হবে।

**উদাহরণ:**

```python
p = session.scalars(a.posts.select().where(Post.title == "প্রথম")).one()
a.posts.remove(p)
session.flush()
print(p.author_id, titles())   # None ['দ্বিতীয়']
```

### `WriteOnlyCollection.select()` { #writeonlycollection-select }

```python
WriteOnlyCollection.select()
```

**ধরন:** মেথড

এই collection-এর রোগুলোর জন্য একটি `Select` (`WHERE :param = posts.author_id`)। এর সাথে যেকোনো `where()`, `order_by()`, `limit()` জুড়ে `session.scalars()` দিয়ে চালান। গোনার জন্য `select(func.count()).select_from(a.posts.select().subquery())`।

**উদাহরণ:**

```python
stmt = a.posts.select().where(Post.title.like("দ%"))
print([p.title for p in session.scalars(stmt)])   # ['দ্বিতীয়']
print(session.scalar(select(func.count()).select_from(a.posts.select().subquery())))   # 2
```

### `WriteOnlyCollection.update()` { #writeonlycollection-update }

```python
WriteOnlyCollection.update()
```

**ধরন:** মেথড

এই লেখকের পোস্টগুলোর জন্য বাল্ক `UPDATE` বানায়।

**উদাহরণ:**

```python
session.execute(a.posts.update().values(title=Post.title + "!").where(Post.title == "প্রথম"))
print(titles())   # ['প্রথম!', 'দ্বিতীয়']
```

## `AppenderQuery` { #appenderquery }

```python
from sqlalchemy.orm import AppenderQuery
```

/// warning | পুরোনো (legacy) API

নতুন কোডে এটি এড়িয়ে চলুন; বিকল্প নিচে বলা আছে।

///

`notes: DynamicMapped["Note"] = relationship()` (বা `lazy="dynamic"`) লিখলে `author.notes` এই অবজেক্ট: একটি legacy [`Query`](query.md), যাতে collection-এর শর্ত আগে থেকে বসানো, আর সাথে `append()`/`remove()`। `author.notes.filter(...).all()`, `.count()` লেখা যায়। **২.০-তে legacy**: নতুন কোডে `WriteOnlyMapped` নিন (async-এ dynamic চলে না)।

**উদাহরণ:**

```python
print(type(a.notes).__name__, a.notes.count())   # AppenderQuery 2
print([n.text for n in a.notes.order_by(Note.id)], a.notes.filter(Note.text == "n2").one().text)   # ['n1', 'n2'] n2
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #appenderquery-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`add()`](#appenderquery-add) | মেথড | একটি অবজেক্ট যোগ করে (`append()`-এর মতো)। |
| [`add_all()`](#appenderquery-add-all) | মেথড | কয়েকটি একসাথে যোগ করে (`extend()`-এর মতো)। |
| [`append()`](#appenderquery-append) | মেথড | `list.append()`-এর মতো নাম; একটি যোগ করে। |
| [`extend()`](#appenderquery-extend) | মেথড | `list.extend()`-এর মতো; কয়েকটি যোগ করে। |
| [`query_class`](#appenderquery-query-class) | অ্যাট্রিবিউট (internal) | কাস্টম `Query` সাবক্লাস (relationship-এ `query_class=` দিলে), নইলে `None`। |
| [`remove()`](#appenderquery-remove) | মেথড | collection থেকে সরায় (FK `NULL`)। |
| [`session`](#appenderquery-session) | প্রপার্টি | যে সেশনে কুয়েরি চলবে (মালিক অবজেক্টের সেশন)। |

/// details | উত্তরাধিকার সূত্রে পাওয়া আরও ৯১টি সদস্য (দেখতে ক্লিক করুন)
    type: info

নিচের সদস্যগুলো `AppenderQuery`-এ হুবহু একই কাজ করে; ব্যাখ্যা ও উদাহরণ মূল ক্লাসের অংশে আছে (লিংকে ক্লিক করুন)।

**`Query` থেকে:** [`add_column()`](query.md#query-add-column) · [`add_columns()`](query.md#query-add-columns) · [`add_entity()`](query.md#query-add-entity) · [`all()`](query.md#query-all) · [`apply_labels()`](query.md#query-apply-labels) · [`as_scalar()`](query.md#query-as-scalar) · [`autoflush()`](query.md#query-autoflush) · [`column_descriptions`](query.md#query-column-descriptions) · [`correlate()`](query.md#query-correlate) · [`count()`](query.md#query-count) · [`cte()`](query.md#query-cte) · [`delete()`](query.md#query-delete) · [`distinct()`](query.md#query-distinct) · [`enable_assertions()`](query.md#query-enable-assertions) · [`enable_eagerloads()`](query.md#query-enable-eagerloads) · [`except_()`](query.md#query-except-) · [`except_all()`](query.md#query-except-all) · [`execution_options()`](query.md#query-execution-options) · [`exists()`](query.md#query-exists) · [`ext()`](query.md#query-ext) · [`filter()`](query.md#query-filter) · [`filter_by()`](query.md#query-filter-by) · [`first()`](query.md#query-first) · [`from_statement()`](query.md#query-from-statement) · [`get()`](query.md#query-get) · [`get_children()`](query.md#query-get-children) · [`get_execution_options()`](query.md#query-get-execution-options) · [`get_label_style`](query.md#query-get-label-style) · [`group_by()`](query.md#query-group-by) · [`having()`](query.md#query-having) · [`instances()`](query.md#query-instances) · [`intersect()`](query.md#query-intersect) · [`intersect_all()`](query.md#query-intersect-all) · [`is_single_entity`](query.md#query-is-single-entity) · [`join()`](query.md#query-join) · [`label()`](query.md#query-label) · [`lazy_loaded_from`](query.md#query-lazy-loaded-from) · [`limit()`](query.md#query-limit) · [`load_options`](query.md#query-load-options) · [`logger`](query.md#query-logger) · [`logging_name`](query.md#query-logging-name) · [`merge_result()`](query.md#query-merge-result) · [`offset()`](query.md#query-offset) · [`one()`](query.md#query-one) · [`one_or_none()`](query.md#query-one-or-none) · [`only_return_tuples()`](query.md#query-only-return-tuples) · [`options()`](query.md#query-options) · [`order_by()`](query.md#query-order-by) · [`outerjoin()`](query.md#query-outerjoin) · [`params()`](query.md#query-params) · [`populate_existing()`](query.md#query-populate-existing) · [`prefix_with()`](query.md#query-prefix-with) · [`reset_joinpoint()`](query.md#query-reset-joinpoint) · [`scalar()`](query.md#query-scalar) · [`scalar_subquery()`](query.md#query-scalar-subquery) · [`select_from()`](query.md#query-select-from) · [`selectable`](query.md#query-selectable) · [`set_label_style()`](query.md#query-set-label-style) · [`slice()`](query.md#query-slice) · [`statement`](query.md#query-statement) · [`subquery()`](query.md#query-subquery) · [`suffix_with()`](query.md#query-suffix-with) · [`tuples()`](query.md#query-tuples) · [`union()`](query.md#query-union) · [`union_all()`](query.md#query-union-all) · [`update()`](query.md#query-update) · [`value()`](query.md#query-value) · [`values()`](query.md#query-values) · [`where()`](query.md#query-where) · [`whereclause`](query.md#query-whereclause) · [`with_entities()`](query.md#query-with-entities) · [`with_for_update()`](query.md#query-with-for-update) · [`with_hint()`](query.md#query-with-hint) · [`with_labels()`](query.md#query-with-labels) · [`with_parent()`](query.md#query-with-parent) · [`with_session()`](query.md#query-with-session) · [`with_statement_hint()`](query.md#query-with-statement-hint) · [`with_transformation()`](query.md#query-with-transformation) · [`yield_per()`](query.md#query-yield-per)

**`Select` থেকে:** [`allows_lambda`](select.md#select-allows-lambda) · [`is_delete`](select.md#select-is-delete) · [`is_dml`](select.md#select-is-dml) · [`is_from_statement`](select.md#select-is-from-statement) · [`is_insert`](select.md#select-is-insert) · [`is_select`](select.md#select-is-select) · [`is_text`](select.md#select-is-text) · [`is_update`](select.md#select-is-update) · [`memoized_attribute`](select.md#select-memoized-attribute) · [`memoized_instancemethod()`](select.md#select-memoized-instancemethod) · [`supports_execution`](select.md#select-supports-execution) · [`uses_inspection`](select.md#select-uses-inspection)

///

### `AppenderQuery.add()` { #appenderquery-add }

```python
AppenderQuery.add(item)
```

**ধরন:** মেথড

একটি অবজেক্ট যোগ করে (`append()`-এর মতো)।

**উদাহরণ:**

```python
a.notes.add(Note(text="n3"))
print(a.notes.count())   # 3  (autoflush হয়ে গোনা হলো)
```

### `AppenderQuery.add_all()` { #appenderquery-add-all }

```python
AppenderQuery.add_all(iterator)
```

**ধরন:** মেথড

কয়েকটি একসাথে যোগ করে (`extend()`-এর মতো)।

**উদাহরণ:**

```python
a.notes.add_all([Note(text="n3"), Note(text="n4")])
print(a.notes.count())   # 4
```

### `AppenderQuery.append()` { #appenderquery-append }

```python
AppenderQuery.append(item)
```

**ধরন:** মেথড

`list.append()`-এর মতো নাম; একটি যোগ করে।

**উদাহরণ:**

```python
a.notes.append(Note(text="n3"))
print([n.text for n in a.notes.order_by(Note.id)])   # ['n1', 'n2', 'n3']
```

### `AppenderQuery.extend()` { #appenderquery-extend }

```python
AppenderQuery.extend(iterator)
```

**ধরন:** মেথড

`list.extend()`-এর মতো; কয়েকটি যোগ করে।

**উদাহরণ:**

```python
a.notes.extend([Note(text="n3")])
print(a.notes.count())   # 3
```

### `AppenderQuery.query_class` { #appenderquery-query-class }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কাস্টম `Query` সাবক্লাস (relationship-এ `query_class=` দিলে), নইলে `None`।

**উদাহরণ:**

```python
print(a.notes.query_class)   # None
```

### `AppenderQuery.remove()` { #appenderquery-remove }

```python
AppenderQuery.remove(item)
```

**ধরন:** মেথড

collection থেকে সরায় (FK `NULL`)।

**উদাহরণ:**

```python
n1 = a.notes.filter_by(text="n1").one()
a.notes.remove(n1)
print(a.notes.count(), n1.author_id)   # 1 None
```

### `AppenderQuery.session` { #appenderquery-session }

**ধরন:** প্রপার্টি

যে সেশনে কুয়েরি চলবে (মালিক অবজেক্টের সেশন)।

**উদাহরণ:**

```python
print(a.notes.session is session)   # True
```

## dict collection { #attribute-keyed-dict-group }

## `attribute_keyed_dict()` { #attribute-keyed-dict }

```python
from sqlalchemy.orm import attribute_keyed_dict
```

```python
attribute_keyed_dict(attr_name, *, ignore_unpopulated_attribute=False)
```

**ধরন:** ফাংশন

collection-কে `dict` বানায়, যার **key হলো সন্তান-অবজেক্টের একটি অ্যাট্রিবিউট**: `relationship(collection_class=attribute_keyed_dict("word"))` দিলে `author.tags["py"]`। মডেলে টাইপ লিখুন `Mapped[dict[str, "Tag"]]`। (২.০-তে নাম বদল; পুরোনো নাম `attribute_mapped_collection` একই ফাংশন।)

**সাবধান:** অবজেক্ট যোগ করার সময় key-অ্যাট্রিবিউটে মান থাকতে হবে, আর পরে `tag.word` বদলালে dict-এর key নিজে থেকে বদলায় না।

**উদাহরণ:**

```python
print(sorted(a.tags), a.tags["py"].word)   # ['db', 'py'] py
a.tags["sql"] = Tag(word="sql")
session.commit()
print(sorted(session.get(Author, 1).tags))   # ['db', 'py', 'sql']
print(attribute_mapped_collection is attribute_keyed_dict)   # True
```

### `attribute_keyed_dict()`-এর সব প্যারামিটার { #attribute-keyed-dict-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attr_name` | যে অ্যাট্রিবিউটের মান key হবে (স্ট্রিং নাম)। |
| `ignore_unpopulated_attribute` | `True` দিলে key-অ্যাট্রিবিউট খালি এমন অবজেক্ট চুপচাপ বাদ; ডিফল্টে (`False`) এরর। |

## `column_keyed_dict()` { #column-keyed-dict }

```python
from sqlalchemy.orm import column_keyed_dict
```

```python
column_keyed_dict(mapping_spec, *, ignore_unpopulated_attribute=False)
```

**ধরন:** ফাংশন

`attribute_keyed_dict()`-এর মতো, কিন্তু key ঠিক হয় একটি **`Column`** অবজেক্ট (বা কয়েকটি কলামের tuple) দিয়ে। (পুরোনো নাম `column_mapped_collection`।)

**উদাহরণ:**

```python
class Writer(Base):
    __tablename__ = "writers"
    id: Mapped[int] = mapped_column(primary_key=True)
    tags: Mapped[dict[str, Tag]] = relationship(collection_class=column_keyed_dict(Tag.__table__.c.word),
                                                primaryjoin="Writer.id == foreign(Tag.author_id)", viewonly=True)
Writer.__table__.create(engine)
session.add(Writer(id=1)); session.flush()
print(sorted(session.get(Writer, 1).tags))   # ['db', 'py']
```

### `column_keyed_dict()`-এর সব প্যারামিটার { #column-keyed-dict-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `mapping_spec` | key-এর কলাম, বা কলামের tuple (তখন key-ও tuple)। |
| `ignore_unpopulated_attribute` | `attribute_keyed_dict()`-এর মতো। |

## `keyfunc_mapping()` { #keyfunc-mapping }

```python
from sqlalchemy.orm import keyfunc_mapping
```

```python
keyfunc_mapping(keyfunc, *, ignore_unpopulated_attribute=False)
```

**ধরন:** ফাংশন

সবচেয়ে নমনীয়: key বানায় **আপনার ফাংশন**, যেটি সন্তান-অবজেক্ট নিয়ে key দেয়। যেমন শব্দের প্রথম অক্ষর। (পুরোনো নাম `mapped_collection`।)

**উদাহরণ:**

```python
factory = keyfunc_mapping(lambda tag: tag.word.upper())
d = factory()
d.set(Tag(word="py"))
print(list(d))   # ['PY']
```

### `keyfunc_mapping()`-এর সব প্যারামিটার { #keyfunc-mapping-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keyfunc` | অবজেক্ট নিয়ে key ফেরত দেয় এমন ফাংশন। |
| `ignore_unpopulated_attribute` | `True` দিলে ফাংশন key দিতে না পারলে (অ্যাট্রিবিউট খালি) বাদ। |

## `KeyFuncDict` { #keyfuncdict }

```python
from sqlalchemy.orm import KeyFuncDict
```

উপরের তিনটি ফাংশন যে dict ক্লাস বানায় তার মূল ক্লাস: একটি সাধারণ `dict`, সাথে ORM-এর জন্য `set()` আর `remove()`। নিজের dict collection বানাতে এটি subclass করুন। (২.০-তে নাম বদল; পুরোনো নাম `MappedCollection` একই ক্লাস।)

**উদাহরণ:**

```python
print(isinstance(a.tags, KeyFuncDict), MappedCollection is KeyFuncDict)   # True True
```

### কনস্ট্রাক্টরের প্যারামিটার { #keyfuncdict-params }

```python
KeyFuncDict(keyfunc, *dict_args, ignore_unpopulated_attribute=False)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `keyfunc` | অবজেক্ট থেকে key বানানোর ফাংশন। |
| `dict_args` | `dict()`-এর মতো শুরুর মান। |
| `ignore_unpopulated_attribute` | key দিতে না পারলে বাদ দেবে কি না। |

**Python `dict`-এর সব মেথড** (`clear()`, `copy()`, `fromkeys()`, `get()`, `items()`, `keys()`, `pop()`, `popitem()`, `setdefault()`, `update()`, `values()`) সাধারণ `dict`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #keyfuncdict-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`remove()`](#keyfuncdict-remove) | মেথড | **মান** দিয়ে মোছে: key নিজে বের করে নেয় (`del d[key]`-এর বিকল্প)। |
| [`set()`](#keyfuncdict-set) | মেথড | **মান** দিয়ে যোগ করে: key নিজে বের করে নেয় (`d[key] = v`-এর বিকল্প; key আর অ্যাট্রিবিউট অমিল হওয়ার ভয় নেই)। |

### `KeyFuncDict.remove()` { #keyfuncdict-remove }

```python
KeyFuncDict.remove(value)
```

**ধরন:** মেথড

**মান** দিয়ে মোছে: key নিজে বের করে নেয় (`del d[key]`-এর বিকল্প)। `delete-orphan` cascade থাকলে flush-এ রোটিও মুছে যায়।

**উদাহরণ:**

```python
a.tags.remove(a.tags["db"])
session.commit()
print(sorted(session.get(Author, 1).tags), session.scalar(select(func.count()).select_from(Tag)))   # ['py'] 1
```

### `KeyFuncDict.set()` { #keyfuncdict-set }

```python
KeyFuncDict.set(value)
```

**ধরন:** মেথড

**মান** দিয়ে যোগ করে: key নিজে বের করে নেয় (`d[key] = v`-এর বিকল্প; key আর অ্যাট্রিবিউট অমিল হওয়ার ভয় নেই)।

**উদাহরণ:**

```python
a.tags.set(Tag(word="sql"))
print(sorted(a.tags))   # ['db', 'py', 'sql']
```

## নিজের collection class { #collection-group }

## `collection` { #collection }

```python
from sqlalchemy.orm.collections import collection
```

নিজের collection class বানাতে (যেমন `list`/`set`-এর বদলে অন্য কিছু, বা অন্য নামের মেথড) এই ডেকোরেটরগুলো দিয়ে SQLAlchemy-কে বলুন কোন মেথড কী কাজ করে, যাতে যোগ-বিয়োগ ধরা পড়ে। `list`, `set`, `dict`-এর subclass হলে সাধারণত কিছুই লাগে না; SQLAlchemy নিজে চেনে।

মডেলে টাইপ-annotation দিয়ে নয়, `relationship(Target, collection_class=MyClass)` দিয়ে ঘোষণা করুন; `Mapped[MyClass]` লিখলে SQLAlchemy `MyClass`-কে টার্গেট মডেল ভাবে।

দুই ধরনের ডেকোরেটর: **চিহ্ন** (`appender`, `remover`, `iterator`, `internally_instrumented`; বন্ধনী ছাড়া) আর **রেসিপি** (`adds()`, `removes()`, `removes_return()`, `replaces()`; বন্ধনীসহ)।

**উদাহরণ:**

```python
class Bag:
    def __init__(self):
        self.items = []
    @collection.appender
    def put(self, item):
        self.items.append(item)
    @collection.remover
    def take(self, item):
        self.items.remove(item)
    @collection.iterator
    def __iter__(self):
        return iter(self.items)

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    box_id: Mapped[int | None] = mapped_column(ForeignKey("boxes.id"))

class Box(Base):
    __tablename__ = "boxes"
    id: Mapped[int] = mapped_column(primary_key=True)
    # Mapped[Bag] লিখবেন না: তাহলে SQLAlchemy Bag-কেই টার্গেট মডেল ভাবে (UnmappedClassError)
    items = relationship(Item, collection_class=Bag)

Base.metadata.create_all(engine)
b = Box(id=7)
b.items.put(Item(name="কলম"))
session.add(b); session.commit()
print(type(session.get(Box, 7).items).__name__, [i.name for i in session.get(Box, 7).items])   # Bag ['কলম']
```

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #collection-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`adds()`](#collection-adds) | স্ট্যাটিক মেথড | (রেসিপি) মেথডটি একটি অবজেক্ট **যোগ করে**; কোন আর্গুমেন্টটি সেই অবজেক্ট তা অবস্থান (০ থেকে, `self` বাদে ১ থেকে) বা নাম দিয়ে বলুন: `@collection.adds(1)` বা `@collection.adds("entity")`। |
| [`appender()`](#collection-appender) | স্ট্যাটিক মেথড | (চিহ্ন) collection-এ একটি অবজেক্ট যোগ করার **প্রধান** মেথড। |
| [`internally_instrumented()`](#collection-internally-instrumented) | স্ট্যাটিক মেথড | (চিহ্ন) মেথডটি নিজেই ইভেন্ট চালায় (ভেতরে অন্য instrumented মেথড ডাকে), তাই SQLAlchemy যেন আবার মুড়ে না দেয়। |
| [`iterator()`](#collection-iterator) | স্ট্যাটিক মেথড | (চিহ্ন) collection-এর সব সদস্য দেয় এমন মেথড। |
| [`remover()`](#collection-remover) | স্ট্যাটিক মেথড | (চিহ্ন) একটি অবজেক্ট সরানোর **প্রধান** মেথড (একটি আর্গুমেন্ট: অবজেক্টটি)। |
| [`removes()`](#collection-removes) | স্ট্যাটিক মেথড | (রেসিপি) মেথডটি একটি **আর্গুমেন্ট হিসেবে দেওয়া** অবজেক্ট সরায়: `@collection.removes(1)`। |
| [`removes_return()`](#collection-removes-return) | স্ট্যাটিক মেথড | (রেসিপি) মেথডটি যে অবজেক্ট **ফেরত দেয়** সেটি সরানো হয়েছে (যেমন `pop()`)। |
| [`replaces()`](#collection-replaces) | স্ট্যাটিক মেথড | (রেসিপি) মেথডটি একটি অবজেক্ট বসায় আর আগেরটি (যা ফেরত দেয়) সরায়, যেমন `__setitem__`: `@collection.replaces(2)`। |

### `collection.adds()` { #collection-adds }

```python
collection.adds(arg)
```

**ধরন:** স্ট্যাটিক মেথড

(রেসিপি) মেথডটি একটি অবজেক্ট **যোগ করে**; কোন আর্গুমেন্টটি সেই অবজেক্ট তা অবস্থান (০ থেকে, `self` বাদে ১ থেকে) বা নাম দিয়ে বলুন: `@collection.adds(1)` বা `@collection.adds("entity")`।

**উদাহরণ:**

```python
class MyList(list):
    @collection.adds("entity")
    def insert_at(self, pos, entity):
        self.insert(pos, entity)
print(MyList.insert_at._sa_instrument_before)   # ('fire_append_event', 'entity')
```

### `collection.appender()` { #collection-appender }

```python
collection.appender(fn)
```

**ধরন:** স্ট্যাটিক মেথড

(চিহ্ন) collection-এ একটি অবজেক্ট যোগ করার **প্রধান** মেথড। ORM ডেটাবেস থেকে লোড করার সময় এটাই ডাকে। list-এ ডিফল্ট `append`।

**উদাহরণ:**

```python
class Stack(list):
    @collection.appender
    def push(self, item):
        self.append(item)
print(Stack.push._sa_instrument_role)   # appender
```

### `collection.internally_instrumented()` { #collection-internally-instrumented }

```python
collection.internally_instrumented(fn)
```

**ধরন:** স্ট্যাটিক মেথড

(চিহ্ন) মেথডটি নিজেই ইভেন্ট চালায় (ভেতরে অন্য instrumented মেথড ডাকে), তাই SQLAlchemy যেন আবার মুড়ে না দেয়। খুব বিশেষ ক্ষেত্রে।

**উদাহরণ:**

```python
class L(list):
    @collection.internally_instrumented
    def append_twice(self, item):
        self.append(item)
print(L.append_twice._sa_instrumented)   # True
```

### `collection.iterator()` { #collection-iterator }

```python
collection.iterator(fn)
```

**ধরন:** স্ট্যাটিক মেথড

(চিহ্ন) collection-এর সব সদস্য দেয় এমন মেথড। ডিফল্ট `__iter__`।

**উদাহরণ:**

```python
class Bag2(list):
    @collection.iterator
    def all_items(self):
        return iter(self)
print(Bag2.all_items._sa_instrument_role)   # iterator
```

### `collection.remover()` { #collection-remover }

```python
collection.remover(fn)
```

**ধরন:** স্ট্যাটিক মেথড

(চিহ্ন) একটি অবজেক্ট সরানোর **প্রধান** মেথড (একটি আর্গুমেন্ট: অবজেক্টটি)। list-এ ডিফল্ট `remove`।

**উদাহরণ:**

```python
class Stack(list):
    @collection.remover
    def drop(self, item):
        self.remove(item)
print(Stack.drop._sa_instrument_role)   # remover
```

### `collection.removes()` { #collection-removes }

```python
collection.removes(arg)
```

**ধরন:** স্ট্যাটিক মেথড

(রেসিপি) মেথডটি একটি **আর্গুমেন্ট হিসেবে দেওয়া** অবজেক্ট সরায়: `@collection.removes(1)`।

**উদাহরণ:**

```python
class L(list):
    @collection.removes(1)
    def zap(self, item):
        self.remove(item)
print(L.zap._sa_instrument_before)   # ('fire_remove_event', 1)
```

### `collection.removes_return()` { #collection-removes-return }

```python
collection.removes_return()
```

**ধরন:** স্ট্যাটিক মেথড

(রেসিপি) মেথডটি যে অবজেক্ট **ফেরত দেয়** সেটি সরানো হয়েছে (যেমন `pop()`)।

**উদাহরণ:**

```python
class L(list):
    @collection.removes_return()
    def pop_last(self):
        return self.pop()
print(L.pop_last._sa_instrument_after)   # fire_remove_event
```

### `collection.replaces()` { #collection-replaces }

```python
collection.replaces(arg)
```

**ধরন:** স্ট্যাটিক মেথড

(রেসিপি) মেথডটি একটি অবজেক্ট বসায় আর আগেরটি (যা ফেরত দেয়) সরায়, যেমন `__setitem__`: `@collection.replaces(2)`।

**উদাহরণ:**

```python
class L(list):
    @collection.replaces(2)
    def put_at(self, index, item):
        old = self[index]
        self[index] = item
        return old
print(L.put_at._sa_instrument_after)   # fire_remove_event
```

## `collection_adapter(collection)` { #collection-adapter }

```python
from sqlalchemy.orm.collections import collection_adapter
```

**ধরন:** ফাংশন

একটি instrumented collection থেকে তার [`CollectionAdapter`](#collectionadapter) বের করে (আসলে `operator.attrgetter("_sa_adapter")`)। নিজের collection class-এর ভেতর থেকে ইভেন্ট চালাতে বা মালিক অবজেক্ট জানতে।

**উদাহরণ:**

```python
ad = collection_adapter(a.tags)
print(type(ad).__name__, ad.owner_state.obj() is a)   # CollectionAdapter True
```

## `CollectionAdapter` { #collectionadapter }

```python
from sqlalchemy.orm.collections import CollectionAdapter
```

collection আর ORM-এর মাঝের সেতু: যেকোনো ধরনের collection (list, set, dict, নিজের class)-কে ORM একই ভাবে চালায় এর মাধ্যমে, আর যোগ-বিয়োগের ইভেন্ট (backref, cascade, flush-এর হিসাব) এখান থেকেই চলে। সাধারণ অ্যাপে সরাসরি দরকার হয় না; নিজের collection class-এ "ইভেন্টসহ যোগ" করতে কাজে লাগে।

**উদাহরণ:**

```python
ad = collection_adapter(a.tags)
print(ad.attr.key, sorted(ad.data), len(list(ad)))   # tags ['db', 'py'] 2
```

### কনস্ট্রাক্টরের প্যারামিটার { #collectionadapter-params }

```python
CollectionAdapter(attr, owner_state, data)
```

| প্যারামিটার | কাজ |
| :--- | :--- |
| `attr` | collection-এর attribute implementation। |
| `owner_state` | মালিক অবজেক্টের `InstanceState`। |
| `data` | আসল collection অবজেক্ট। |

### সব মেথড ও অ্যাট্রিবিউট এক নজরে { #collectionadapter-summary }

| সদস্য | ধরন | কাজ |
| :--- | :--- | :--- |
| [`append_multiple_without_event()`](#collectionadapter-append-multiple-without-event) | মেথড (internal) | কয়েকটি অবজেক্ট **ইভেন্ট ছাড়া** যোগ করে (ORM ডেটাবেস থেকে লোড করার সময় এভাবে বসায়)। |
| [`append_with_event()`](#collectionadapter-append-with-event) | মেথড | ইভেন্টসহ যোগ: যেন `author.tags[...] = t` লেখা হয়েছে (backref বসে, flush-এ লেখা হয়)। |
| [`append_without_event()`](#collectionadapter-append-without-event) | মেথড (internal) | ইভেন্ট ছাড়া যোগ: ORM জানে না, তাই flush-এ কিছু লেখা হয় না। |
| [`attr`](#collectionadapter-attr) | অ্যাট্রিবিউট (internal) | collection-এর attribute implementation (`attr.key` = relationship-এর নাম)। |
| [`bulk_appender()`](#collectionadapter-bulk-appender) | মেথড (internal) | collection-এর appender মেথড (bound) ফেরত দেয়। |
| [`bulk_remover()`](#collectionadapter-bulk-remover) | মেথড (internal) | collection-এর remover মেথড (bound) ফেরত দেয়। |
| [`clear_with_event()`](#collectionadapter-clear-with-event) | মেথড | ইভেন্টসহ সব খালি করে (প্রতিটির জন্য remove ইভেন্ট)। |
| [`clear_without_event()`](#collectionadapter-clear-without-event) | মেথড (internal) | ইভেন্ট ছাড়া খালি করে। |
| [`data`](#collectionadapter-data) | প্রপার্টি | আসল collection অবজেক্ট (এখানে dict)। |
| [`empty`](#collectionadapter-empty) | অ্যাট্রিবিউট (internal) | ভেতরের ব্যবহার: adapter একটি "খালি" অস্থায়ী collection-এর কি না। |
| [`fire_append_event()`](#collectionadapter-fire-append-event) | মেথড (internal) | "একটি অবজেক্ট যোগ হয়েছে" ইভেন্ট চালায় (instrumented মেথড ভেতরে এটি ডাকে)। |
| [`fire_append_wo_mutation_event()`](#collectionadapter-fire-append-wo-mutation-event) | মেথড (internal) | "যোগ করার চেষ্টা হয়েছে কিন্তু আগে থেকেই ছিল" ইভেন্ট (set/dict-এ `append_wo_mutation`)। |
| [`fire_pre_remove_event()`](#collectionadapter-fire-pre-remove-event) | মেথড (internal) | সরানোর **আগে** ইভেন্ট (কোন অবজেক্ট এখনো জানা নেই এমন ক্ষেত্রে, যেমন `pop()`)। |
| [`fire_remove_event()`](#collectionadapter-fire-remove-event) | মেথড (internal) | "একটি অবজেক্ট সরানো হয়েছে" ইভেন্ট চালায়। |
| [`invalidated`](#collectionadapter-invalidated) | অ্যাট্রিবিউট (internal) | `True` হলে এই collection পুরোনো হয়ে গেছে: মালিক অবজেক্ট expire হয়েছে (যেমন `commit()`-এর পর), পরের বার পড়লে নতুন collection লোড হবে। |
| [`owner_state`](#collectionadapter-owner-state) | অ্যাট্রিবিউট | মালিক অবজেক্টের `InstanceState`; `owner_state.obj()` দিলে অবজেক্টটি। |
| [`remove_with_event()`](#collectionadapter-remove-with-event) | মেথড | ইভেন্টসহ সরায় (`delete-orphan` থাকলে flush-এ রো মুছে যাবে)। |
| [`remove_without_event()`](#collectionadapter-remove-without-event) | মেথড (internal) | ইভেন্ট ছাড়া সরায় (ORM জানে না)। |

### `CollectionAdapter.append_multiple_without_event()` { #collectionadapter-append-multiple-without-event }

```python
CollectionAdapter.append_multiple_without_event(items)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

কয়েকটি অবজেক্ট **ইভেন্ট ছাড়া** যোগ করে (ORM ডেটাবেস থেকে লোড করার সময় এভাবে বসায়)।

**উদাহরণ:**

```python
print(callable(CollectionAdapter.append_multiple_without_event))   # True
```

### `CollectionAdapter.append_with_event()` { #collectionadapter-append-with-event }

```python
CollectionAdapter.append_with_event(item, initiator=None)
```

**ধরন:** মেথড

ইভেন্টসহ যোগ: যেন `author.tags[...] = t` লেখা হয়েছে (backref বসে, flush-এ লেখা হয়)।

**উদাহরণ:**

```python
t = Tag(word="sql")
collection_adapter(a.tags).append_with_event(t)
print(sorted(a.tags), t in session)   # ['db', 'py', 'sql'] True
```

### `CollectionAdapter.append_without_event()` { #collectionadapter-append-without-event }

```python
CollectionAdapter.append_without_event(item)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ইভেন্ট ছাড়া যোগ: ORM জানে না, তাই flush-এ কিছু লেখা হয় না।

**উদাহরণ:**

```python
t = Tag(word="tmp")
collection_adapter(a.tags).append_without_event(t)
print(sorted(a.tags), t in session)   # ['db', 'py', 'tmp'] False  (ইভেন্ট নেই, তাই cascade-ও হয়নি)
```

### `CollectionAdapter.attr` { #collectionadapter-attr }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

collection-এর attribute implementation (`attr.key` = relationship-এর নাম)।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).attr.key)   # tags
```

### `CollectionAdapter.bulk_appender()` { #collectionadapter-bulk-appender }

```python
CollectionAdapter.bulk_appender()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

collection-এর appender মেথড (bound) ফেরত দেয়।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).bulk_appender().__name__)   # set
```

### `CollectionAdapter.bulk_remover()` { #collectionadapter-bulk-remover }

```python
CollectionAdapter.bulk_remover()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

collection-এর remover মেথড (bound) ফেরত দেয়।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).bulk_remover().__name__)   # remove
```

### `CollectionAdapter.clear_with_event()` { #collectionadapter-clear-with-event }

```python
CollectionAdapter.clear_with_event(initiator=None)
```

**ধরন:** মেথড

ইভেন্টসহ সব খালি করে (প্রতিটির জন্য remove ইভেন্ট)।

**উদাহরণ:**

```python
collection_adapter(a.tags).clear_with_event()
session.commit()
print(dict(session.get(Author, 1).tags))   # {}
```

### `CollectionAdapter.clear_without_event()` { #collectionadapter-clear-without-event }

```python
CollectionAdapter.clear_without_event()
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ইভেন্ট ছাড়া খালি করে।

**উদাহরণ:**

```python
collection_adapter(a.tags).clear_without_event()
print(len(a.tags))   # 0
```

### `CollectionAdapter.data` { #collectionadapter-data }

**ধরন:** প্রপার্টি

আসল collection অবজেক্ট (এখানে dict)।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).data is a.tags)   # True
```

### `CollectionAdapter.empty` { #collectionadapter-empty }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ভেতরের ব্যবহার: adapter একটি "খালি" অস্থায়ী collection-এর কি না।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).empty)   # False
```

### `CollectionAdapter.fire_append_event()` { #collectionadapter-fire-append-event }

```python
CollectionAdapter.fire_append_event(item, initiator=None, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

"একটি অবজেক্ট যোগ হয়েছে" ইভেন্ট চালায় (instrumented মেথড ভেতরে এটি ডাকে)।

**উদাহরণ:**

```python
print(callable(collection_adapter(a.tags).fire_append_event))   # True
```

### `CollectionAdapter.fire_append_wo_mutation_event()` { #collectionadapter-fire-append-wo-mutation-event }

```python
CollectionAdapter.fire_append_wo_mutation_event(item, initiator=None, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

"যোগ করার চেষ্টা হয়েছে কিন্তু আগে থেকেই ছিল" ইভেন্ট (set/dict-এ `append_wo_mutation`)।

**উদাহরণ:**

```python
print(callable(collection_adapter(a.tags).fire_append_wo_mutation_event))   # True
```

### `CollectionAdapter.fire_pre_remove_event()` { #collectionadapter-fire-pre-remove-event }

```python
CollectionAdapter.fire_pre_remove_event(initiator=None, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

সরানোর **আগে** ইভেন্ট (কোন অবজেক্ট এখনো জানা নেই এমন ক্ষেত্রে, যেমন `pop()`)।

**উদাহরণ:**

```python
print(callable(collection_adapter(a.tags).fire_pre_remove_event))   # True
```

### `CollectionAdapter.fire_remove_event()` { #collectionadapter-fire-remove-event }

```python
CollectionAdapter.fire_remove_event(item, initiator=None, key=<EventConstants.NO_KEY: 4>)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

"একটি অবজেক্ট সরানো হয়েছে" ইভেন্ট চালায়।

**উদাহরণ:**

```python
print(callable(collection_adapter(a.tags).fire_remove_event))   # True
```

### `CollectionAdapter.invalidated` { #collectionadapter-invalidated }

**ধরন:** অ্যাট্রিবিউট

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

`True` হলে এই collection পুরোনো হয়ে গেছে: মালিক অবজেক্ট expire হয়েছে (যেমন `commit()`-এর পর), পরের বার পড়লে নতুন collection লোড হবে। পুরোনো collection-এ বদল করলে SQLAlchemy সতর্ক করে।

**উদাহরণ:**

```python
old = collection_adapter(a.tags)
session.expire(a)
print(old.invalidated, collection_adapter(a.tags) is old)   # True False
```

### `CollectionAdapter.owner_state` { #collectionadapter-owner-state }

**ধরন:** অ্যাট্রিবিউট

মালিক অবজেক্টের `InstanceState`; `owner_state.obj()` দিলে অবজেক্টটি।

**উদাহরণ:**

```python
print(collection_adapter(a.tags).owner_state.obj().name)   # রহিম
```

### `CollectionAdapter.remove_with_event()` { #collectionadapter-remove-with-event }

```python
CollectionAdapter.remove_with_event(item, initiator=None)
```

**ধরন:** মেথড

ইভেন্টসহ সরায় (`delete-orphan` থাকলে flush-এ রো মুছে যাবে)।

**উদাহরণ:**

```python
collection_adapter(a.tags).remove_with_event(a.tags["db"])
session.commit()
print(sorted(session.get(Author, 1).tags))   # ['py']
```

### `CollectionAdapter.remove_without_event()` { #collectionadapter-remove-without-event }

```python
CollectionAdapter.remove_without_event(item)
```

**ধরন:** মেথড

/// note | অভ্যন্তরীণ (internal)

এটি মূলত SQLAlchemy নিজে ব্যবহার করে। সাধারণ অ্যাপ কোডে সাধারণত দরকার হয় না।

///

ইভেন্ট ছাড়া সরায় (ORM জানে না)।

**উদাহরণ:**

```python
collection_adapter(a.tags).remove_without_event(a.tags["db"])
print(sorted(a.tags))   # ['py']
```

## `bulk_replace()` { #bulk-replace }

```python
from sqlalchemy.orm.collections import bulk_replace
```

```python
bulk_replace(values, existing_adapter, new_adapter, initiator=None)
```

**ধরন:** ফাংশন

(অভ্যন্তরীণ) পুরো collection নতুন মানে বদলানোর সময় (`author.tags = {...}`) ORM এটি ডাকে: নতুন collection-এ মানগুলো বসায়, আর শুধু **যেগুলো সত্যিই নতুন** তাদের জন্য append ইভেন্ট, আর বাদ পড়াগুলোর জন্য remove ইভেন্ট চালায়।

**উদাহরণ:**

```python
py = a.tags["py"]
a.tags = {"py": py, "go": Tag(word="go")}          # ভেতরে bulk_replace চলে
session.commit()
print(sorted(session.get(Author, 1).tags))   # ['go', 'py']
```

### `bulk_replace()`-এর সব প্যারামিটার { #bulk-replace-params }

| প্যারামিটার | কাজ |
| :--- | :--- |
| `values` | নতুন সদস্যগুলো। |
| `existing_adapter` | পুরোনো collection-এর adapter। |
| `new_adapter` | নতুন (খালি) collection-এর adapter। |
| `initiator` | ইভেন্টের উৎস (ভেতরের ব্যবহার)। |

## `InstrumentedList` { #instrumentedlist }

```python
from sqlalchemy.orm.collections import InstrumentedList
```

`Mapped[list[X]]` collection আসলে এই ক্লাস: একটি সাধারণ `list`, যার `append()`, `remove()`, `pop()`, `__setitem__` ইত্যাদি মুড়ে দেওয়া, যাতে ORM প্রতিটি বদল ধরতে পারে।

**উদাহরণ:**

```python
class Shelf(Base):
    __tablename__ = "shelves"
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[list[Post]] = relationship(primaryjoin="Shelf.id == foreign(Post.author_id)", viewonly=True)
print(type(Shelf().posts).__name__, isinstance(Shelf().posts, list))   # InstrumentedList True
```

**Python `list`-এর সব মেথড** (`append()`, `clear()`, `copy()`, `count()`, `extend()`, `index()`, `insert()`, `pop()`, `remove()`, `reverse()`, `sort()`) সাধারণ `list`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

## `InstrumentedSet` { #instrumentedset }

```python
from sqlalchemy.orm.collections import InstrumentedSet
```

`Mapped[set[X]]` collection-এর ক্লাস: সাধারণ `set`, মুড়ে দেওয়া। একই অবজেক্ট দুবার যোগ করা যায় না।

**উদাহরণ:**

```python
class Rack(Base):
    __tablename__ = "racks"
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[set[Post]] = relationship(primaryjoin="Rack.id == foreign(Post.author_id)", viewonly=True)
print(type(Rack().posts).__name__)   # InstrumentedSet
```

**Python `set`-এর সব মেথড** (`add()`, `clear()`, `copy()`, `difference()`, `difference_update()`, `discard()`, `intersection()`, `intersection_update()`, `isdisjoint()`, `issubset()`, `issuperset()`, `pop()`, `remove()`, `symmetric_difference()`, `symmetric_difference_update()`, `union()`, `update()`) সাধারণ `set`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

## `InstrumentedDict` { #instrumenteddict }

```python
from sqlalchemy.orm.collections import InstrumentedDict
```

instrumented `dict`-এর মূল ক্লাস। `attribute_keyed_dict()` ইত্যাদি এর ওপর ভিত্তি করে `KeyFuncDict` বানায়।

**উদাহরণ:**

```python
print(issubclass(type(a.tags), InstrumentedDict) or isinstance(a.tags, dict))   # True
```

**Python `dict`-এর সব মেথড** (`clear()`, `copy()`, `fromkeys()`, `get()`, `items()`, `keys()`, `pop()`, `popitem()`, `setdefault()`, `update()`, `values()`) সাধারণ `dict`-এর মতোই কাজ করে; নিচে শুধু নিজস্ব সদস্য।

## কোনটা কখন { #which }

| collection | ঘোষণা | কখন |
| :--- | :--- | :--- |
| list (ডিফল্ট) | `Mapped[list["Post"]] = relationship()` | কয়েকটি থেকে কয়েকশো সন্তান; প্রায়ই সবগুলো লাগে |
| set | `Mapped[set["Post"]]` | ক্রম লাগে না, ডুপ্লিকেট চলবে না |
| dict | `Mapped[dict[str, "Tag"]]` + `attribute_keyed_dict("word")` | নাম/কোড দিয়ে সরাসরি খোঁজা |
| write-only | `WriteOnlyMapped["Post"] = relationship()` | হাজার হাজার সন্তান, pagination, async |
| dynamic (legacy) | `DynamicMapped["Post"]` | পুরোনো কোড; নতুন কোডে write-only |

/// tip | FastAPI-তে write-only collection দিয়ে pagination

```python
@app.get("/authors/{author_id}/posts")
def list_posts(author_id: int, page: int = 1, db: Session = Depends(get_db)):
    author = db.get(Author, author_id)
    stmt = author.posts.select().order_by(Post.id).limit(20).offset((page - 1) * 20)
    return db.scalars(stmt).all()
```

///
