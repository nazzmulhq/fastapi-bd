# টেস্টিং: pytest + আসল ডেটাবেস { #sqlalchemy-testing }

/// note | এই পেজে যা শিখবেন

* ডেটাবেসসহ FastAPI অ্যাপ টেস্ট করার নির্ভরযোগ্য কৌশল: প্রতি টেস্ট শেষে সব rollback।
* `pytest` + `pytest-asyncio` + `httpx` দিয়ে async টেস্ট।
* `app.dependency_overrides` দিয়ে আসল সেশনের বদলে টেস্টের সেশন ঢোকানো।
* ডুপ্লিকেট (409), PATCH, soft delete আর **N+1 কুয়েরি**র টেস্ট।

///

এই পেজের টেস্টগুলো [পূর্ণ FastAPI প্রজেক্ট](fastapi-project.md)-এর Order API-র ওপর লেখা, আর PostgreSQL-এ চালিয়ে সবগুলো পাস করেছে।

## কৌশল: প্রতি টেস্টে একটি ট্রানজ্যাকশন, শেষে rollback { #bn-strategy }

টেস্টের প্রধান সমস্যা: এক টেস্টে তৈরি ডেটা যেন পরের টেস্টে না থাকে। প্রতি টেস্টে টেবিল মুছে নতুন করে বানানো খুব ধীর। তার বদলে:

1. পুরো টেস্ট রানে **একবার** টেবিল তৈরি।
2. প্রতিটি টেস্টের শুরুতে একটি কানেকশনে একটি **বাইরের ট্রানজ্যাকশন** খোলা।
3. অ্যাপের কোড `commit()` করলেও সেটা আসলে শুধু একটি **savepoint** শেষ করে, বাইরের ট্রানজ্যাকশন খোলাই থাকে।
4. টেস্ট শেষে বাইরের ট্রানজ্যাকশন **rollback**। টেস্টের সব ডেটা উধাও, আর খুব দ্রুত।

/// tip | উদাহরণ দিয়ে বুঝি

পেনসিল দিয়ে খসড়া খাতায় অঙ্ক করা। প্রতিটি অঙ্ক শেষে পুরো পাতা মুছে ফেলা হয়, তাই পরের অঙ্ক সবসময় পরিষ্কার পাতায় শুরু হয়। আসল খাতায় (ডেটাবেসে) কখনো কিছু লেখা হয় না।

///

## ইনস্টল ও কনফিগারেশন { #bn-install }

```bash
pip install pytest pytest-asyncio httpx
```

আলাদা একটি টেস্ট ডেটাবেস বানান। কখনো ডেভেলপমেন্ট বা প্রোডাকশনের ডেটাবেসে টেস্ট চালাবেন না:

```bash
createdb shop_test        # অথবা: psql -c "CREATE DATABASE shop_test"
```

`pyproject.toml`-এ pytest-asyncio কনফিগারেশন:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
```

/// info | কনফিগারেশন সহজ ভাষায়

* `asyncio_mode = "auto"`: প্রতিটি `async def test_...`-এর ওপর আলাদা করে `@pytest.mark.asyncio` লিখতে হয় না।
* দুটি `loop_scope = "session"`: সব টেস্ট আর ফিক্সচার **একটি** ইভেন্ট লুপে চলে। async engine যে লুপে তৈরি, সেই লুপেই ব্যবহার করতে হয়। আলাদা লুপ হলে `attached to a different loop` জাতীয় এরর আসে।

///

## `tests/conftest.py` { #bn-conftest }

```python
import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app import models  # noqa: F401  — সব টেবিল metadata-তে লোড
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/shop_test"
)


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """পুরো টেস্ট রানে একবার: টেবিল তৈরি, শেষে মুছে ফেলা।"""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """প্রতিটি টেস্টের জন্য একটি সেশন; টেস্ট শেষে সব পরিবর্তন rollback।"""
    async with engine.connect() as conn:
        outer = await conn.begin()                       # বাইরের transaction — কখনো commit হবে না
        async with AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",    # কোডের commit() আসলে SAVEPOINT release করে
        ) as s:
            yield s
        await outer.rollback()                           # টেস্টের সব ডেটা উধাও


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """আসল get_db-এর বদলে টেস্টের সেশন ঢুকিয়ে দেওয়া HTTP ক্লায়েন্ট।"""

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
```

/// info | কোডটি সহজ ভাষায়

* **`engine` ফিক্সচার** (`scope="session"`): টেস্ট রানের শুরুতে একবার টেবিল বানায়, শেষে মুছে ফেলে। `NullPool` দেওয়ায় টেস্টে কোনো কানেকশন পুলে আটকে থাকে না।
* **`session` ফিক্সচার**: প্রতিটি টেস্টে নতুন।
    * `conn.begin()`: বাইরের ট্রানজ্যাকশন।
    * `join_transaction_mode="create_savepoint"`: সেশনটি ওই খোলা ট্রানজ্যাকশনে "যোগ দেয়"। অ্যাপের `commit()` তখন একটি savepoint শেষ করে, আর `rollback()` শুধু সেই savepoint বাতিল করে। ফলে অ্যাপের কোড একটুও না বদলে টেস্ট করা যায়।
    * শেষে `outer.rollback()`: সব মুছে যায়।
* **`client` ফিক্সচার**: `app.dependency_overrides[get_db] = ...` দিয়ে FastAPI-কে বলা হলো, "`get_db` চাইলে আসলটা নয়, এটা দাও"। `ASGITransport` দিয়ে অ্যাপে সরাসরি রিকোয়েস্ট যায়, আসল সার্ভার চালাতে হয় না।

ডিপেন্ডেন্সি ওভাররাইড নিয়ে আরও পড়ুন [ওভাররাইডসহ ডিপেন্ডেন্সি টেস্ট](../advanced/testing-dependencies.md) পেজে।

///

/// warning | সাধারণ ভুল

conftest-এ `import app.models` লিখবেন না। এই লাইন `app` নামটিকে **প্যাকেজ** বানিয়ে দেয়, ফলে ওপরের `from app.main import app` থেকে পাওয়া FastAPI অ্যাপটি ঢাকা পড়ে যায়। লিখুন `from app import models`।

///

## `tests/test_orders.py` { #bn-tests }

```python
from sqlalchemy import event, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order

ORDER = {
    "customer_id": 7,
    "order_code": "ORD-001",
    "items": [
        {"product_sku": "PEN", "quantity": 2, "unit_price": "10.50"},
        {"product_sku": "BOOK", "quantity": 1, "unit_price": "250.00"},
    ],
}


async def test_create_order(client):
    r = await client.post("/api/v1/orders/", json=ORDER)
    assert r.status_code == 201
    body = r.json()
    assert body["total_amount"] == "271.00"
    assert len(body["items"]) == 2
    assert body["version"] == 1


async def test_each_test_starts_with_empty_db(session: AsyncSession):
    # আগের টেস্টে তৈরি অর্ডার rollback হয়ে গেছে
    count = await session.scalar(select(func.count()).select_from(Order))
    assert count == 0


async def test_duplicate_order_code_returns_409(client):
    assert (await client.post("/api/v1/orders/", json=ORDER)).status_code == 201
    r = await client.post("/api/v1/orders/", json=ORDER)
    assert r.status_code == 409
    # 409-এর পরও একই সেশন ব্যবহারযোগ্য
    assert (await client.get("/api/v1/orders/")).status_code == 200


async def test_patch_changes_only_sent_fields(client):
    order_id = (await client.post("/api/v1/orders/", json=ORDER)).json()["order_id"]
    r = await client.patch(f"/api/v1/orders/{order_id}", json={"status": "PAID"})
    assert r.status_code == 200
    assert r.json()["status"] == "PAID"
    assert r.json()["total_amount"] == "271.00"     # অপরিবর্তিত
    assert r.json()["version"] == 2                 # optimistic-lock ভার্সন বেড়েছে


async def test_soft_delete_hides_order(client):
    order_id = (await client.post("/api/v1/orders/", json=ORDER)).json()["order_id"]
    assert (await client.delete(f"/api/v1/orders/{order_id}")).status_code == 204
    assert (await client.get(f"/api/v1/orders/{order_id}")).status_code == 404


async def test_list_orders_has_no_n_plus_1(client, session: AsyncSession):
    for i in range(5):
        await client.post("/api/v1/orders/", json={**ORDER, "order_code": f"ORD-{i}"})

    statements: list[str] = []

    def count_sql(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    sync_engine = session.bind.engine.sync_engine
    event.listen(sync_engine, "before_cursor_execute", count_sql)
    try:
        r = await client.get("/api/v1/orders/")
    finally:
        event.remove(sync_engine, "before_cursor_execute", count_sql)

    assert r.status_code == 200 and len(r.json()) == 5
    selects = [s for s in statements if s.lstrip().upper().startswith("SELECT")]
    assert len(selects) == 2        # orders + এক ব্যাচে সব items (selectinload)
```

চালান:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/shop_test pytest -q
```

```
......                                                                   [100%]
6 passed in 0.27s
```

/// info | টেস্টগুলো সহজ ভাষায়

* **`test_each_test_starts_with_empty_db`**: আগের টেস্টে অর্ডার তৈরি হলেও এখানে সংখ্যা ০, কারণ rollback কাজ করছে।
* **`test_duplicate_order_code_returns_409`**: দ্বিতীয়বার একই কোডে `409`। আর তারপরও `GET` কাজ করছে, মানে router-এর `rollback()` শুধু savepoint বাতিল করেছে, টেস্টের সেশন ভাঙেনি।
* **`test_patch_changes_only_sent_fields`**: শুধু `status` বদলেছে, `total_amount` আগের মতো, আর `version` ১ থেকে ২।
* **`test_list_orders_has_no_n_plus_1`**: SQLAlchemy-র `before_cursor_execute` event দিয়ে ডেটাবেসে যাওয়া প্রতিটি SQL গোনা হয়েছে। ৫টি অর্ডার হোক বা ৫০০টি, SELECT ঠিক ২টি। কেউ ভুল করে `selectinload` সরিয়ে দিলে এই টেস্ট সাথে সাথে ফেইল করবে।

///

## আরও কিছু পরামর্শ { #bn-tips }

* **প্রোডাকশনের মতো ডেটাবেসে টেস্ট।** PostgreSQL-এর বদলে SQLite-এ টেস্ট করলে `ON CONFLICT`, `FOR UPDATE`, JSONB, টাইমজোন সংক্রান্ত বাগ ধরা পড়বে না। CI-তে Docker দিয়ে PostgreSQL চালান।
* **CI-তে মাইগ্রেশনও টেস্ট করুন।** `create_all()`-এর বদলে টেস্টের শুরুতে `alembic upgrade head` চালালে মাইগ্রেশনের ভুলও ধরা পড়ে। সাথে `alembic check`।
* **টেস্ট ডেটা বানানোর হেল্পার।** বারবার একই dict লেখার বদলে ছোট ফাংশন বানান: `async def make_order(session, **overrides) -> Order: ...`।
* **একই সময়ে একাধিক রিকোয়েস্টের টেস্ট** (concurrency) এই rollback কৌশলে হয় না, কারণ সব একই কানেকশনে চলে। সেগুলোর জন্য আলাদা টেস্ট লিখুন, যেখানে আসল commit হয় আর শেষে নিজে পরিষ্কার করেন।

/// check | সংক্ষেপে মনে রাখুন

* আলাদা টেস্ট ডেটাবেস; টেবিল একবার তৈরি।
* প্রতি টেস্টে বাইরের ট্রানজ্যাকশন + `join_transaction_mode="create_savepoint"` + শেষে rollback।
* `app.dependency_overrides[get_db]` দিয়ে টেস্টের সেশন; `httpx.AsyncClient(transport=ASGITransport(app=app))`।
* `before_cursor_execute` দিয়ে কুয়েরি গুনে N+1-এর টেস্ট।
* প্রোডাকশনের মতো একই ডেটাবেসে টেস্ট।

///

**পরের ধাপ:** inheritance, hybrid property আর event শিখুন [অ্যাডভান্সড ম্যাপিং ও Event](advanced-mapping.md) অধ্যায়ে।
