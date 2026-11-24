# অ্যাডভান্সড কুয়েরি: CTE, Window, Subquery { #sqlalchemy-advanced-queries }

/// note | এই পেজে যা শিখবেন

* CTE (`WITH ...`) দিয়ে বড় কুয়েরিকে নাম দেওয়া ছোট টুকরোয় ভাগ করা।
* recursive CTE দিয়ে এক কুয়েরিতেই পুরো ক্যাটাগরি ট্রি ঘোরা।
* window function: র‍্যাঙ্ক, রানিং টোটাল, রোলিং গড়।
* correlated subquery, `EXISTS`, `LATERAL`, আর `UNION`।
* PostgreSQL-এর JSONB কুয়েরি ও full-text search।

///

এই অধ্যায়ের উদাহরণগুলো [কুয়েরি অধ্যায়ের রেফারেন্স মডেল](querying.md#s25) (`OrderHeader`, `OrderItem`, `ProductCategory` …) ব্যবহার করে। কয়েকটি জায়গায় [CRUD অধ্যায়ের](crud.md#s33) `Order` মডেলও আছে।

## 27. Common Table Expression ও Recursive Tree { #s27 }

/// tip | উদাহরণ দিয়ে বুঝি

অঙ্ক কষার সময় খাতার পাশে একটা ছোট হিসাব আগে করে রাখেন: "ধরি, গত মাসের মোট বিক্রি = ক"। তারপর মূল হিসাবে শুধু "ক" লেখেন। **CTE** ঠিক এটাই: একটি সাবকুয়েরিকে নাম দিয়ে আলাদা করে রাখা, যাতে মূল কুয়েরি পড়তে সহজ হয়।

///

**CTE** (`WITH ... AS (...)`) একটি সাবকুয়েরিকে নাম দিয়ে পুনর্ব্যবহারযোগ্য করে। **Recursive CTE** এক রাউন্ড-ট্রিপে adjacency list (ক্যাটাগরি, অর্গ চার্ট, bill of materials) ঘুরে আসে।

### 27.1 সাধারণ CTE { #s27-1 }
```python
recent = (
    select(Order.customer_id, func.sum(Order.total_amount).label("spend"))
    .where(Order.created_at >= cutoff)
    .group_by(Order.customer_id)
    .cte("recent_spend")
)
stmt = select(Customer.full_name, recent.c.spend).join(recent, recent.c.customer_id == Customer.customer_id)
```

/// info | তৈরি হওয়া SQL

(ধরে নিচ্ছি `Customer` মডেলের টেবিলের নাম `customers`।)

```sql
WITH recent_spend AS (
    SELECT orders.customer_id, sum(orders.total_amount) AS spend
    FROM orders
    WHERE orders.created_at >= $1
    GROUP BY orders.customer_id
)
SELECT customers.full_name, recent_spend.spend
FROM customers JOIN recent_spend ON recent_spend.customer_id = customers.customer_id
```

`recent.c.spend`: CTE-র কলামগুলো পাওয়া যায় `.c` দিয়ে।

///

### 27.2 Recursive CTE: লিফ ক্যাটাগরি থেকে রুট পর্যন্ত { #s27-2 }
```python
from sqlalchemy import literal, select
from sqlalchemy.orm import aliased
from app.models.product import ProductCategory

async def get_category_ancestor_tree(session: AsyncSession, leaf_category_id: str):
    # ১. Anchor member: লিফ থেকে শুরু
    hierarchy = (
        select(
            ProductCategory.product_category_id,
            ProductCategory.primary_parent_category_id,
            ProductCategory.category_name,
            literal(1).label("depth"),
        )
        .where(ProductCategory.product_category_id == leaf_category_id)
        .cte(name="category_hierarchy", recursive=True)
    )

    # ২. Recursive member: প্রতিটি রো-কে তার প্যারেন্টের সাথে join
    parent = aliased(ProductCategory, name="parent")
    recursive_step = (
        select(
            parent.product_category_id,
            parent.primary_parent_category_id,
            parent.category_name,
            (hierarchy.c.depth + 1).label("depth"),
        )
        .join(parent, hierarchy.c.primary_parent_category_id == parent.product_category_id)
    )

    # ৩. Anchor + recursive member-এর UNION ALL
    hierarchy = hierarchy.union_all(recursive_step)

    # ৪. CTE থেকে সিলেক্ট
    stmt = (
        select(hierarchy.c.product_category_id, hierarchy.c.category_name, hierarchy.c.depth)
        .order_by(hierarchy.c.depth)
    )
    return (await session.execute(stmt)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

recursive CTE দুই অংশে চলে:

1. **Anchor**: শুরুর রো। এখানে লিফ ক্যাটাগরি "Laptops" (depth = ১)।
2. **Recursive অংশ**: আগের ধাপে পাওয়া প্রতিটি রো-র প্যারেন্ট খোঁজে, depth এক বাড়ায়। নতুন রো পেলে আবার চলে।
3. প্যারেন্ট না পেলে (রুটে পৌঁছালে) থামে।

ফলাফল, আমাদের পরীক্ষার ডেটায়:

```python
[("LAPTOP", 1), ("ELEC", 2), ("ROOT", 3)]   # Laptops → Electronics → All
```

ট্রি যত গভীরই হোক, ডেটাবেসে যাওয়া-আসা **একবারই**।

///

Recursive member কোনো রো না দিলে রিকার্শন থামে (রুটের `primary_parent_category_id IS NULL`)। **নিচের দিকে** (সব উত্তরসূরি) যেতে join উল্টে দিন: `parent.primary_parent_category_id == hierarchy.c.product_category_id`।

/// danger | বিপদ

চক্রাকার ডেটা (A → B → A) থাকলে recursive CTE অনন্তকাল চলে। Depth সীমা দিন (recursive member-এ `.where(hierarchy.c.depth < 20)`) অথবা PostgreSQL 14-এর `CYCLE` ক্লজ ব্যবহার করুন।

///

## 28. Window Function { #s28 }

/// tip | উদাহরণ দিয়ে বুঝি

একটি ক্লাসের পরীক্ষার ফল:

* **`GROUP BY`** দিলে পাবেন প্রতি সেকশনের **একটি** রো: "সেকশন ক, গড় ৭৫"। ছাত্রদের আলাদা রো আর থাকে না।
* **Window function** দিলে প্রত্যেক ছাত্রের রো থাকে, আর পাশে নতুন কলাম: "রহিম, ৮০, সেকশনে ২য়, সেকশনের গড় ৭৫"।

অর্থাৎ window function রো কমায় না, প্রতিটি রো-র পাশে তার "দলের" তথ্য বসায়।

///

Window function সম্পর্কিত রো-গুলোর উপর হিসাব করে, কিন্তু `GROUP BY`-এর মতো রো-গুলোকে **একত্রিত করে না**।

```python
from sqlalchemy import func, select

async def get_order_line_ranking_report(session: AsyncSession):
    line_total = OrderItem.quantity * OrderItem.unit_price

    stmt = (
        select(
            OrderItem.order_id,
            OrderItem.order_item_seq_id,
            OrderItem.product_id,
            OrderItem.unit_price,
            line_total.label("line_total"),
            # ১. প্রতি অর্ডারের ভেতরে লাইনের র‍্যাঙ্ক (১ = সবচেয়ে দামি)
            func.row_number().over(
                partition_by=OrderItem.order_id,
                order_by=OrderItem.unit_price.desc(),
            ).label("price_rank_in_order"),
            # ২. অর্ডারের ভেতরে রানিং টোটাল (চলতি যোগফল)
            func.sum(line_total).over(
                partition_by=OrderItem.order_id,
                order_by=OrderItem.order_item_seq_id,
            ).label("running_order_total"),
            # ৩. সব লাইনের মধ্যে dense rank
            func.dense_rank().over(order_by=line_total.desc()).label("global_line_rank"),
        )
        .where(OrderItem.status_id == "ITEM_APPROVED")
        .limit(100)
    )
    return (await session.execute(stmt)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

* `.over(partition_by=OrderItem.order_id, ...)`: প্রতিটি অর্ডারকে আলাদা "দল" ধরে হিসাব।
* `row_number()` + `order_by=unit_price.desc()`: প্রতি অর্ডারে সবচেয়ে দামি আইটেম ১, তারপর ২, ৩ …।
* `func.sum(line_total).over(..., order_by=seq_id)`: আইটেম নম্বরের ক্রমে চলতি যোগফল।
* `dense_rank().over(order_by=...)`: `partition_by` নেই, তাই সব আইটেমের মধ্যে র‍্যাঙ্ক।

///

Frame (`rows=` / `range_=`) ঠিক করে কোন পার্শ্ববর্তী রো অন্তর্ভুক্ত হবে:
```python
# গ্রাহকপ্রতি ক্রমবর্ধমান খরচ: ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
func.sum(Order.total_amount).over(
    partition_by=Order.customer_id,
    order_by=Order.created_at,
    rows=(None, 0),
)

# ৭-রো রোলিং গড়: ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
func.avg(Order.total_amount).over(order_by=Order.created_at, rows=(-6, 0))
```

| ফাংশন | কাজ |
| :--- | :--- |
| `row_number()` | প্রতি partition-এ ১, ২, ৩ … ইউনিক |
| `rank()` / `dense_rank()` | সমান মান একই র‍্যাঙ্ক পায় (`rank` ফাঁক রাখে) |
| `lag(col, n)` / `lead(col, n)` | আগের / পরের রো-র মান |
| `first_value()` / `last_value()` | Frame-এর সীমানার মান |
| `ntile(n)` | রো-গুলোকে n ভাগে ভাগ |
| যেকোনো aggregate + `.over()` | রানিং / রোলিং aggregate |

Window-এর ফলাফলের উপর ফিল্টার করতে ("প্রতি অর্ডারের শীর্ষ ৩টি লাইন") কুয়েরিটিকে subquery/CTE-তে মুড়ে বাইরে ফিল্টার করুন: `WHERE price_rank_in_order <= 3`।

## 29. Correlated Subquery ও `LATERAL` Join { #s29 }

### 29.1 Scalar correlated subquery { #s29-1 }
কলাম হিসেবে "প্রতি অর্ডারে আইটেম সংখ্যা":
```python
item_count = (
    select(func.count(OrderItem.order_item_seq_id))
    .where(OrderItem.order_id == OrderHeader.order_id)
    .correlate(OrderHeader)
    .scalar_subquery()
)
stmt = select(OrderHeader.order_id, item_count.label("item_count"))
```

/// info | কোডটি সহজ ভাষায়

প্রতিটি অর্ডারের পাশে তার আইটেম সংখ্যা: `[("ORD_1001", 3), ("ORD_1002", 2)]`।

* `.where(OrderItem.order_id == OrderHeader.order_id)`: ভেতরের কুয়েরি বাইরের রো-র ওপর নির্ভর করে, তাই একে বলে **correlated**।
* `.scalar_subquery()`: ফলাফল একটি মাত্র মান, তাই এটি কলাম হিসেবে বসানো যায়।

একই কাজ `JOIN` + `GROUP BY` দিয়েও হয়। কোনটি দ্রুত তা ডেটার ওপর নির্ভর করে, তাই সন্দেহ হলে `EXPLAIN` দেখুন ([§48.4](performance.md#s48-4))।

///

### 29.2 `EXISTS` { #s29-2 }
```python
from sqlalchemy import exists

has_approved = exists().where(
    OrderItem.order_id == OrderHeader.order_id,
    OrderItem.status_id == "ITEM_APPROVED",
)
stmt = select(OrderHeader).where(has_approved)
```

/// tip | `EXISTS` কেন?

"অন্তত একটি অনুমোদিত আইটেম আছে এমন অর্ডার"-এর জন্য JOIN করলে একাধিক মিল থাকলে অর্ডার একাধিকবার আসে। `EXISTS` শুধু হ্যাঁ/না দেখে, প্রথম মিল পেলেই থেমে যায়। তাই ডুপ্লিকেট নেই, আর প্রায়ই দ্রুততর। উল্টোটা চাইলে `~has_approved` (`NOT EXISTS`)।

///

### 29.3 `LATERAL`: প্রতিটি অর্ডারের সর্বশেষ আইটেম { #s29-3 }
`LATERAL` সাবকুয়েরি তার বামের টেবিলের কলাম রেফার করতে পারে — ইনডেক্স সাপোর্টসহ "প্রতি গ্রুপে top-N"-এর জন্য আদর্শ:
```python
from sqlalchemy import select, true

async def get_orders_with_latest_item_lateral(session: AsyncSession):
    """
    SELECT ... FROM order_header o
    JOIN LATERAL (
        SELECT ... FROM order_item i
        WHERE i.order_id = o.order_id
        ORDER BY i.order_item_seq_id DESC LIMIT 1
    ) latest_item ON TRUE
    """
    latest_item = (
        select(
            OrderItem.order_item_seq_id,
            OrderItem.product_id,
            OrderItem.unit_price,
            OrderItem.quantity,
        )
        .where(OrderItem.order_id == OrderHeader.order_id)
        .order_by(OrderItem.order_item_seq_id.desc())
        .limit(1)
        .correlate(OrderHeader)
        .lateral("latest_item")
    )

    stmt = (
        select(
            OrderHeader.order_id,
            OrderHeader.order_date,
            OrderHeader.grand_total,
            latest_item.c.order_item_seq_id,
            latest_item.c.product_id,
            latest_item.c.unit_price,
        )
        .join(latest_item, true())          # ON TRUE
        .where(OrderHeader.status_id == "ORDER_APPROVED")
        .limit(50)
    )
    return (await session.execute(stmt)).mappings().all()
```

/// tip | উদাহরণ দিয়ে বুঝি

"প্রতিটি অর্ডারের **সর্বশেষ** আইটেম" সাধারণ JOIN দিয়ে করা কঠিন। `LATERAL` মানে: বাঁ দিকের প্রতিটি অর্ডারের জন্য ডান দিকের ছোট কুয়েরিটি একবার করে চালাও, সেই অর্ডারকে মাথায় রেখে। অনেকটা প্রতিটি ফাইল খুলে শুধু শেষ পাতাটা দেখার মতো।

পরীক্ষার ফলাফল: `[("ORD_1001", "00003"), ("ORD_1002", "00002")]`।

///

আইটেম নেই এমন অর্ডারও রাখতে lateral join-এ `isouter=True` দিন। `(order_id, order_item_seq_id)`-এর উপর ইনডেক্স থাকলে প্রতিটি lateral lookup একটি index seek হয়।

## 30. Set Operation (`UNION`, `INTERSECT`, `EXCEPT`) { #s30 }

একই কলাম-আকারের স্বাধীন রেজাল্ট সেট একত্র করা:
```python
from sqlalchemy import literal, select, union_all
from app.models.party import PartyGroup, Person

async def get_all_party_names(session: AsyncSession):
    """ব্যক্তি ও প্রতিষ্ঠান এক ডিরেক্টরিতে।"""
    people = select(
        Person.party_id,
        (Person.first_name + " " + Person.last_name).label("display_name"),
        literal("INDIVIDUAL").label("party_type"),
    )
    groups = select(
        PartyGroup.party_id,
        PartyGroup.group_name.label("display_name"),
        literal("ORGANIZATION").label("party_type"),
    )
    combined = union_all(people, groups).order_by("display_name")
    return (await session.execute(combined)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

ব্যক্তি (`Person`) আর প্রতিষ্ঠান (`PartyGroup`) আলাদা টেবিলে, কিন্তু একটি "ডিরেক্টরি" তালিকায় দুটোই দেখাতে চাই। শর্ত: দুটি কুয়েরির কলাম সংখ্যা ও ধরন একই হতে হবে। `literal("INDIVIDUAL")` প্রতিটি রো-তে একটি স্থির মান বসায়, যাতে বোঝা যায় কোনটা কোথা থেকে এসেছে:

```python
[{"party_id": "G1", "display_name": "Acme Ltd", "party_type": "ORGANIZATION"},
 {"party_id": "P1", "display_name": "Nazmul Haque", "party_type": "INDIVIDUAL"}]
```

///

| ফাংশন | SQL | ডুপ্লিকেট |
| :--- | :--- | :--- |
| `union()` / `union_all()` | `UNION` / `UNION ALL` | বাদ / রাখা হয় (`UNION ALL` দ্রুততর) |
| `intersect()` / `intersect_all()` | `INTERSECT` | দুটোতেই আছে এমন রো |
| `except_()` / `except_all()` | `EXCEPT` | প্রথমটিতে আছে, দ্বিতীয়টিতে নেই |

সম্মিলিত সেট থেকে আরও কুয়েরি করতে এটিকে subquery বানান: `u = union_all(a, b).subquery(); select(u.c.display_name).where(...)`।

## 31. PostgreSQL এক্সট্রা: JSONB ও Full-Text Search { #s31 }

### 31.1 JSONB কুয়েরি { #s31-1 }
```python
from sqlalchemy.dialects.postgresql import JSONB

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    meta_data: Mapped[dict] = mapped_column(JSONB, default=dict)

stmt = select(Product).where(
    Product.meta_data["specs"]["color"].astext == "Midnight Blue",   # ->> টেক্সট এক্সট্র্যাকশন
    Product.meta_data.contains({"warranty_years": 3}),               # @> containment
    Product.meta_data.has_key("dimensions"),                         # ?  key আছে কি না
)
```

/// info | JSONB অপারেটর সহজ ভাষায়

| Python | PostgreSQL | মানে |
| :--- | :--- | :--- |
| `col["specs"]["color"]` | `col -> 'specs' -> 'color'` | ভেতরের মান (JSON হিসেবে) |
| `.astext` | `->>` | মানটি সাধারণ টেক্সট হিসেবে, তুলনার জন্য |
| `col.contains({...})` | `@>` | এই key-value গুলো আছে কি না |
| `col.has_key("x")` | `?` | এই key আছে কি না |

///

Containment কুয়েরি দ্রুত করতে GIN ইনডেক্স: `Index("ix_products_meta", Product.meta_data, postgresql_using="gin")`। JSON কলামের in-place পরিবর্তন ট্র্যাক করতে `MutableDict` দেখুন ([§45.4](advanced-mapping.md#s45-4))।

### 31.2 Full-text search (`tsvector`, `tsquery`) { #s31-2 }
```python
from sqlalchemy import func, select

async def full_text_search_products(session: AsyncSession, search_term: str):
    document = func.to_tsvector(
        "english",
        Product.internal_name + " " + func.coalesce(Product.description, ""),
    )
    query = func.plainto_tsquery("english", search_term)

    stmt = (
        select(
            Product.product_id,
            Product.internal_name,
            func.ts_rank(document, query).label("rank"),
        )
        .where(document.bool_op("@@")(query))
        .order_by(func.ts_rank(document, query).desc())
        .limit(20)
    )
    return (await session.execute(stmt)).mappings().all()
```

/// info | কোডটি সহজ ভাষায়

* `to_tsvector("english", লেখা)`: লেখাকে শব্দের মূল রূপে ভাঙে। যেমন "computers" → "comput"। ফলে "computer" দিয়ে খুঁজলেও মেলে।
* `plainto_tsquery("english", "fast laptop")`: ব্যবহারকারীর লেখা সার্চ টার্মকে কুয়েরিতে বদলায়।
* `@@`: মিলছে কি না। `ts_rank`: কতটা ভালো মিলছে, সেই অনুযায়ী সাজানো।

বাংলা লেখার জন্য PostgreSQL-এ আলাদা ভাষা-কনফিগারেশন নেই। `"simple"` কনফিগারেশন ব্যবহার করুন (শব্দ মূলে ভাঙে না, শুধু হুবহু শব্দ মেলায়), অথবা `pg_trgm` এক্সটেনশন দিয়ে আংশিক মিল খুঁজুন।

///

প্রোডাকশনে ভেক্টরটি একটি generated কলামে সংরক্ষণ করে ইনডেক্স করুন:
```python
from sqlalchemy import Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

search_vector: Mapped[str] = mapped_column(
    TSVECTOR,
    Computed("to_tsvector('english', internal_name || ' ' || coalesce(description, ''))", persisted=True),
)
__table_args__ = (Index("ix_product_search", "search_vector", postgresql_using="gin"),)
```
তারপর `Product.search_vector.match(search_term)` দিয়ে ফিল্টার করুন, যা PostgreSQL-এ `search_vector @@ plainto_tsquery(...)` হিসেবে রেন্ডার হয়।

/// check | সংক্ষেপে মনে রাখুন

* CTE = সাবকুয়েরিকে নাম দেওয়া; `recursive=True` দিলে ট্রি ঘোরা যায়, তবে চক্র থাকলে depth সীমা দিন।
* window function রো কমায় না; `partition_by` = দল, `order_by` = দলের ভেতরের ক্রম।
* "আছে কি না" প্রশ্নে `EXISTS`; "প্রতি দলের শীর্ষ N"-এ `LATERAL`।
* `UNION ALL` দ্রুত, ডুপ্লিকেট বাদ দিতে `UNION`।
* JSONB-তে containment-এর জন্য GIN ইনডেক্স; full-text search-এ সংরক্ষিত `tsvector` + GIN।

///

**পরের ধাপ:** ডেটা তৈরি ও পড়ার সব কৌশল দেখুন [CRUD ১: Create ও Read](crud.md) অধ্যায়ে।
