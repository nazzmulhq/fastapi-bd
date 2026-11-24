# পূর্ণ FastAPI প্রজেক্ট: Repository ও Router { #sqlalchemy-fastapi-project }

/// note | এই পেজে যা শিখবেন

* আগের অধ্যায়গুলোর সব টুকরো জুড়ে একটি পূর্ণ, লেয়ার করা FastAPI প্রজেক্ট।
* `core/config.py`, `core/database.py`, মডেল, স্কিমা, repository, router আর `main.py`, প্রতিটি ফাইলের পুরো কোড।
* একটি জেনেরিক `CRUDBase` repository, যা যেকোনো মডেলকে CRUD দেয়।
* পুরো Order API: তৈরি, পড়া, তালিকা, PUT, PATCH, soft/hard delete।

///

এই পেজের প্রতিটি ফাইল আমরা একসাথে চালিয়ে দেখেছি: `uvicorn` দিয়ে সার্ভার চালু, আসল HTTP রিকোয়েস্ট, আর PostgreSQL 16। [টেস্টিং](testing.md) অধ্যায়ের টেস্টগুলোও এই প্রজেক্টের ওপরেই চলে।

## প্রজেক্টের কাঠামো { #bn-layout }

```
shop/
├── .env
├── alembic.ini                 # Alembic অধ্যায়ে তৈরি হবে
├── migrations/                 # Alembic অধ্যায়ে তৈরি হবে
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── order.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── order.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           └── orders.py
└── tests/
```

একটি রিকোয়েস্ট এই পথে চলে:

```
HTTP রিকোয়েস্ট
   → api/v1/orders.py      (পাথ অপারেশন: ইনপুট নেয়, স্ট্যাটাস কোড ঠিক করে)
   → schemas/order.py      (Pydantic: ইনপুট ভ্যালিডেশন)
   → crud/order.py         (ডেটাবেসের কাজ)
   → models/order.py       (টেবিল)
   → core/database.py      (সেশন, engine)
   → PostgreSQL
```

## ধাপ ১: কনফিগারেশন — `app/core/config.py` { #bn-config }

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """সব কনফিগারেশন এক জায়গায়। মান আসে এনভায়রনমেন্ট ভেরিয়েবল বা .env ফাইল থেকে।"""

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shop"
    DB_ECHO: bool = False          # True দিলে প্রতিটি SQL টার্মিনালে প্রিন্ট হবে
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

## ধাপ ২: ডেটাবেস — `app/core/database.py` { #bn-database }

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# কনস্ট্রেইন্টের নামের নিয়ম — Alembic-এর জন্য জরুরি
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    """সব মডেলের বেস ক্লাস।"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=1800,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,   # async-এ অত্যাবশ্যক
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """প্রতি রিকোয়েস্টে একটি নতুন সেশন; কাজ শেষে নিজে থেকেই বন্ধ হয়।"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# এন্ডপয়েন্টে বারবার Depends(get_db) না লিখে এই টাইপটি ব্যবহার করুন
SessionDep = Annotated[AsyncSession, Depends(get_db)]
```

/// info | কোডটি সহজ ভাষায়

এখানে আগের অধ্যায়গুলোর সব নিয়ম একসাথে: [naming convention](models.md#s3), [পুল সেটিং](engine-session.md#s19-1), [`expire_on_commit=False`](engine-session.md#s20-3), আর [`get_db` ডিপেন্ডেন্সি](engine-session.md#s20-4)। `AsyncAttrs` থাকায় দরকারে `await obj.awaitable_attrs.x` ব্যবহার করা যায়।

///

## ধাপ ৩: মডেল ও স্কিমা { #bn-models-schemas }

* `app/models/order.py`: [CRUD ১ অধ্যায়ের §33.1](crud.md#s33-1)-এর `Order` ও `OrderItem` হুবহু।
* `app/schemas/order.py`: [§33.2](crud.md#s33-2)-এর Pydantic স্কিমাগুলো হুবহু।

`app/models/__init__.py`-এ সব মডেল ইমপোর্ট করুন, যাতে `Base.metadata` আর Alembic সব টেবিল চেনে:

```python
# app/models/__init__.py
from app.models.order import Order, OrderItem

__all__ = ["Order", "OrderItem"]
```

## 42. জেনেরিক রিইউজেবল CRUD Repository { #s42 }

একটি টাইপড বেস ক্লাস যা প্রতিটি মডেলকে স্ট্যান্ডার্ড CRUD দেয়:
```python
# app/crud/base.py
from typing import Any, Generic, Optional, Sequence, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        return await session.get(self.model, id)

    async def get_multi(self, session: AsyncSession, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        pk = self.model.__mapper__.primary_key[0]           # পেজিংয়ের জন্য নির্দিষ্ট ক্রম
        stmt = select(self.model).order_by(pk).offset(skip).limit(limit)
        return (await session.scalars(stmt)).all()

    async def count(self, session: AsyncSession) -> int:
        return (await session.execute(select(func.count()).select_from(self.model))).scalar_one()

    async def create(self, session: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict[str, Any]],
    ) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await session.get(self.model, id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj
```

/// info | কোডটি সহজ ভাষায়

* `Generic[ModelType, CreateSchemaType, UpdateSchemaType]`: একটি "ছাঁচ" ক্লাস। `CRUDBase(Order)` লিখলে সব মেথড `Order`-এর জন্য কাজ করে, `CRUDBase(Product)` লিখলে `Product`-এর জন্য। টাইপ চেকার আর এডিটরও সঠিক টাইপ দেখায়।
* `self.model.__mapper__.primary_key[0]`: মডেলের primary key কলাম খুঁজে বের করে, যাতে pagination-এর ক্রম সবসময় নির্দিষ্ট থাকে।
* `update()`-এ `exclude_unset=True`: PATCH-এর মতো, শুধু পাঠানো ফিল্ড বদলায়।

///

একটি নির্দিষ্ট রিপোজিটরি ডোমেইন কুয়েরি যোগ করে:
```python
# app/crud/order.py
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdatePartial]):
    async def get_with_items(self, session: AsyncSession, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id, Order.is_deleted.is_(False))
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    async def create_with_items(self, session: AsyncSession, data: OrderCreate) -> Order:
        return await create_order_with_items(session, data)        # §34.3

    async def soft_delete(self, session: AsyncSession, order_id: int) -> bool:
        return await soft_delete_order(session, order_id)           # §37.4

order_crud = CRUDOrder(Order)
```

/// details | `app/crud/order.py` পুরো ফাইল দেখুন

ওপরের ক্লাস যে দুটি ফাংশন ডাকে ([§34.3](crud.md#s34-3)-এর `create_order_with_items` আর [§37.4](crud-update-delete.md#s37-4)-এর `soft_delete_order`), সেগুলোও একই ফাইলে রাখুন:

```python
# app/crud/order.py
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdatePartial


async def create_order_with_items(session: AsyncSession, data: OrderCreate) -> Order:
    order = Order(
        customer_id=data.customer_id,
        order_code=data.order_code,
        status="PENDING",
        total_amount=sum(i.quantity * i.unit_price for i in data.items),
        items=[
            OrderItem(product_sku=i.product_sku, quantity=i.quantity, unit_price=i.unit_price)
            for i in data.items
        ],
    )
    session.add(order)
    await session.commit()
    return order


async def soft_delete_order(session: AsyncSession, order_id: int) -> bool:
    result = await session.execute(
        update(Order)
        .where(Order.order_id == order_id, Order.is_deleted.is_(False))
        .values(is_deleted=True, updated_at=func.now())
    )
    await session.commit()
    return result.rowcount > 0


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdatePartial]):
    async def get_with_items(self, session: AsyncSession, order_id: int) -> Order | None:
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_id == order_id, Order.is_deleted.is_(False))
        )
        return (await session.execute(stmt)).scalar_one_or_none()

    async def create_with_items(self, session: AsyncSession, data: OrderCreate) -> Order:
        return await create_order_with_items(session, data)

    async def soft_delete(self, session: AsyncSession, order_id: int) -> bool:
        return await soft_delete_order(session, order_id)


order_crud = CRUDOrder(Order)
```

///

`create()` পুরো schema মডেল কনস্ট্রাক্টরে পাঠায় — ফ্ল্যাট schema-র জন্য এটি কাজ করে। নেস্টেড schema (যেমন `OrderCreate.items`)-র জন্য `create_with_items`-এর মতো আলাদা মেথড লাগে।

## 43. এন্ড-টু-এন্ড FastAPI Router { #s43 }

```python
# app/api/v1/orders.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.crud.order import order_crud
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdateFull, OrderUpdatePartial

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, session: AsyncSession = Depends(get_db)):
    """নেস্টেড আইটেমসহ অর্ডার তৈরি। একই order_code আবার এলে 409।"""
    try:
        return await order_crud.create_with_items(session, payload)
    except IntegrityError as exc:
        await session.rollback()                     # বাধ্যতামূলক: নইলে সেশন অকেজো থাকে
        if "uq_orders_order_code" in str(exc.orig):
            raise HTTPException(status_code=409, detail=f"Order code '{payload.order_code}' already exists.")
        raise HTTPException(status_code=400, detail="Database integrity constraint violated.")

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(order_id: int, session: AsyncSession = Depends(get_db)):
    """আইটেম eager-load করে একটি অর্ডার (রেসপন্সে items আছে বলে বাধ্যতামূলক)।"""
    order = await order_crud.get_with_items(session, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found.")
    return order

@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """Offset-paginated তালিকা। OrderResponse-এ items থাকায় সেগুলো eager-load করতে হবে।"""
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.is_deleted.is_(False))
        .order_by(Order.order_id.desc())
        .offset(skip)
        .limit(limit)
    )
    return (await session.scalars(stmt)).all()

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_full_endpoint(order_id: int, payload: OrderUpdateFull, session: AsyncSession = Depends(get_db)):
    order = await order_crud.get(session, order_id)
    if not order or order.is_deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    await order_crud.update(session, db_obj=order, obj_in=payload)
    return await order_crud.get_with_items(session, order_id)   # রেসপন্সের জন্য items-সহ রিলোড

@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order_partial_endpoint(order_id: int, payload: OrderUpdatePartial, session: AsyncSession = Depends(get_db)):
    order = await order_crud.get(session, order_id)
    if not order or order.is_deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    await order_crud.update(session, db_obj=order, obj_in=payload)
    return await order_crud.get_with_items(session, order_id)   # রেসপন্সের জন্য items-সহ রিলোড

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    soft: bool = Query(True, description="True = soft delete, False = permanent delete"),
    session: AsyncSession = Depends(get_db),
):
    success = (
        await order_crud.soft_delete(session, order_id)
        if soft
        else bool(await order_crud.remove(session, id=order_id))
    )
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
```

/// info | কোডটি সহজ ভাষায়

| এন্ডপয়েন্ট | কী করে | স্ট্যাটাস কোড |
| :--- | :--- | :--- |
| `POST /api/v1/orders/` | আইটেমসহ অর্ডার তৈরি; একই `order_code` হলে 409 | `201`, `409` |
| `GET /api/v1/orders/{id}` | একটি অর্ডার, আইটেমসহ | `200`, `404` |
| `GET /api/v1/orders/?skip=0&limit=20` | তালিকা, প্রতি পেজে ২টি কুয়েরি (N+1 নেই) | `200` |
| `PUT /api/v1/orders/{id}` | `status` ও `total_amount` দুটোই বদলায় | `200`, `404` |
| `PATCH /api/v1/orders/{id}` | পাঠানো ফিল্ডগুলো বদলায় | `200`, `404` |
| `DELETE /api/v1/orders/{id}?soft=true` | soft delete (ডিফল্ট) বা স্থায়ীভাবে মোছা | `204`, `404` |

* `response_model=OrderResponse`: FastAPI রিটার্ন করা ORM অবজেক্টকে এই স্কিমা দিয়ে JSON বানায়, অতিরিক্ত কিছু যায় না।
* `Query(20, ge=1, le=100)`: ক্লায়েন্ট একবারে ১০০-র বেশি চাইতে পারবে না।
* create-এ `IntegrityError` ধরা হয়েছে: ডুপ্লিকেট কোডে সার্ভার ক্র্যাশ (500) না হয়ে পরিষ্কার `409` যায়।

///

PUT/PATCH কেন `get_with_items()` দিয়ে আবার আনে: `OrderResponse` `items` সিরিয়ালাইজ করে, এবং `lazy="raise"` থাকলে কালেকশনটি স্পষ্টভাবে লোড করতে হয়। `CRUDBase.update()`-এর ভেতরের `refresh()` কলামের মান রিলোড করে কিন্তু `lazy="raise"` কালেকশন eager-load করে না, তাই রিটার্নের আগে এন্ডপয়েন্ট `selectinload(Order.items)` দিয়ে অর্ডারটি আবার লোড করে।

## ধাপ ৪: অ্যাপ — `app/main.py` { #bn-main }

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.orders import router as orders_router
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # অ্যাপ চালুর সময় কিছু করার থাকলে এখানে (টেবিল বানাবে Alembic)
    yield
    # অ্যাপ বন্ধের সময় পুলের সব কানেকশন সুন্দরভাবে বন্ধ
    await engine.dispose()


app = FastAPI(title="Order Service", lifespan=lifespan)
app.include_router(orders_router, prefix="/api/v1")
```

## চালিয়ে দেখুন { #bn-run }

টেবিল তৈরি করুন [Alembic](alembic.md) দিয়ে (পরের অধ্যায়ে পুরো ধাপ আছে):

```bash
alembic upgrade head
```

তারপর সার্ভার চালু করুন:

```bash
fastapi dev app/main.py
```

একটি অর্ডার তৈরি করুন:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "order_code": "LIVE-1", "items": [{"product_sku": "A", "quantity": 1, "unit_price": "9.99"}]}'
```

রেসপন্স (`201 Created`):

```json
{
  "customer_id": 1,
  "order_code": "LIVE-1",
  "order_id": 1,
  "status": "PENDING",
  "total_amount": "9.99",
  "version": 1,
  "created_at": "2026-11-24T03:45:33.024797Z",
  "updated_at": null,
  "items": [{"product_sku": "A", "quantity": 1, "unit_price": "9.99", "item_id": 1, "order_id": 1}]
}
```

একই কমান্ড আবার চালালে পাবেন `409`: `{"detail": "Order code 'LIVE-1' already exists."}`। বাকি এন্ডপয়েন্টগুলো [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ Swagger UI থেকে চেষ্টা করুন।

/// tip | নতুন একটি রিসোর্স যোগ করতে

ধরুন `Product` যোগ করবেন। প্রতিটি লেয়ারে একটি করে ফাইল:

1. `app/models/product.py`-এ মডেল, আর `app/models/__init__.py`-এ ইমপোর্ট।
2. `app/schemas/product.py`-এ `ProductCreate`, `ProductUpdate`, `ProductResponse`।
3. `app/crud/product.py`-এ `product_crud = CRUDBase[Product, ProductCreate, ProductUpdate](Product)`। বিশেষ কুয়েরি লাগলে সাবক্লাস।
4. `app/api/v1/products.py`-এ router, আর `main.py`-এ `app.include_router(...)`।
5. `alembic revision --autogenerate -m "add products"` আর `alembic upgrade head`।

///

/// check | সংক্ষেপে মনে রাখুন

* লেয়ার: `api` (HTTP) → `schemas` (ভ্যালিডেশন) → `crud` (ডেটাবেস) → `models` (টেবিল) → `core` (সেশন, কনফিগ)।
* `core/database.py`-এ একটি `engine`, একটি `AsyncSessionLocal`, একটি `get_db`।
* `CRUDBase` সাধারণ কাজ দেয়; বিশেষ কুয়েরি সাবক্লাসে।
* রেসপন্সে নেস্টেড ডেটা থাকলে এন্ডপয়েন্টে `selectinload` অথবা `get_with_items`।
* ডেটাবেসের এরর (`IntegrityError`) ধরে সঠিক HTTP কোডে বদলান।

///

**পরের ধাপ:** টেবিল তৈরি ও বদলানো শিখুন [Alembic দিয়ে মাইগ্রেশন](alembic.md) অধ্যায়ে।
