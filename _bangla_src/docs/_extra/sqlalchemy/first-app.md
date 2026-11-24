# প্রথম অ্যাপ: ধাপে ধাপে বইয়ের দোকান API { #sqlalchemy-first-app }

/// note | এই পেজে যা শিখবেন

* একটি ফাইলেই পুরো একটি CRUD API: বই যোগ, তালিকা, খোঁজা, আপডেট, মোছা।
* মডেল, engine, session, Pydantic স্কিমা আর ডিপেন্ডেন্সি কীভাবে একসাথে কাজ করে।
* প্রতিটি রিকোয়েস্টে SQLAlchemy আসলে কোন SQL চালায়।
* SQLite থেকে PostgreSQL-এ যাওয়া, শুধু এক লাইন বদলে।

///

এই পেজে আমরা একটি ছোট **বইয়ের দোকান API** বানাব। কোনো ডেটাবেস সার্ভার লাগবে না, কারণ এখানে **SQLite** ব্যবহার করব। পুরো ডেটাবেস থাকবে একটি `books.db` ফাইলে।

শেষে আমাদের API-তে এই এন্ডপয়েন্টগুলো থাকবে:

| মেথড ও পাথ | কাজ |
| :--- | :--- |
| `POST /books` | নতুন বই যোগ |
| `GET /books` | বইয়ের তালিকা (নাম দিয়ে খোঁজা ও pagination সহ) |
| `GET /books/{book_id}` | একটি বই |
| `PATCH /books/{book_id}` | বইয়ের কিছু তথ্য বদলানো |
| `DELETE /books/{book_id}` | বই মুছে ফেলা |

## ইনস্টল { #bn-install }

```bash
pip install "fastapi[standard]" "sqlalchemy[asyncio]" aiosqlite
```

## পুরো কোড { #bn-full-code }

একটি `main.py` ফাইল বানিয়ে নিচের কোড লিখুন। ভয় পাবেন না, নিচে প্রতিটি অংশ আলাদা করে বোঝানো হয়েছে।

```python
# main.py
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ---------- ধাপ ১: ডেটাবেসের সাথে সংযোগ ----------
DATABASE_URL = "sqlite+aiosqlite:///./books.db"

engine = create_async_engine(DATABASE_URL, echo=True)          # echo=True: প্রতিটি SQL টার্মিনালে দেখাবে
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# ---------- ধাপ ২: মডেল (টেবিলের নকশা) ----------
class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]                                          # দাম, টাকায় (পূর্ণসংখ্যা)
    in_stock: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------- ধাপ ৩: Pydantic স্কিমা (API-তে কী আসবে, কী যাবে) ----------
class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)
    in_stock: bool = True


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    price: int | None = Field(default=None, ge=0)
    in_stock: bool | None = None


class BookRead(BookCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)             # ORM অবজেক্ট থেকে পড়তে পারবে


# ---------- ধাপ ৪: অ্যাপ চালুর সময় টেবিল তৈরি ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)           # টেবিল না থাকলে তৈরি করে
    yield
    await engine.dispose()                                      # অ্যাপ বন্ধের সময় কানেকশন বন্ধ


app = FastAPI(title="বইয়ের দোকান API", lifespan=lifespan)


# ---------- ধাপ ৫: সেশন ডিপেন্ডেন্সি ----------
async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_book_or_404(book_id: int, session: AsyncSession) -> Book:
    book = await session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="বইটি পাওয়া যায়নি")
    return book


# ---------- ধাপ ৬: CRUD এন্ডপয়েন্ট ----------
@app.post("/books", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, session: SessionDep):
    book = Book(**data.model_dump())
    session.add(book)
    await session.commit()
    await session.refresh(book)          # ডেটাবেসে তৈরি হওয়া id, created_at আবার পড়ে আনে
    return book


@app.get("/books", response_model=list[BookRead])
async def list_books(
    session: SessionDep,
    q: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    stmt = select(Book).order_by(Book.id).offset(skip).limit(limit)
    if q:
        stmt = stmt.where(Book.title.ilike(f"%{q}%"))   # নামের মধ্যে q আছে এমন বই
    result = await session.scalars(stmt)
    return result.all()


@app.get("/books/{book_id}", response_model=BookRead)
async def read_book(book_id: int, session: SessionDep):
    return await get_book_or_404(book_id, session)


@app.patch("/books/{book_id}", response_model=BookRead)
async def update_book(book_id: int, data: BookUpdate, session: SessionDep):
    book = await get_book_or_404(book_id, session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)      # শুধু যে ফিল্ডগুলো পাঠানো হয়েছে
    await session.commit()
    await session.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, session: SessionDep):
    book = await get_book_or_404(book_id, session)
    await session.delete(book)
    await session.commit()
```

## চালিয়ে দেখুন { #bn-run }

```bash
fastapi dev main.py
```

ব্রাউজারে [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) খুলুন। Swagger UI-তে প্রতিটি এন্ডপয়েন্ট দেখতে পাবেন। `POST /books` খুলে **Try it out** চাপুন, আর এই বডি পাঠান:

```json
{
  "title": "পথের পাঁচালী",
  "author": "বিভূতিভূষণ বন্দ্যোপাধ্যায়",
  "price": 350
}
```

উত্তরে পাবেন (`201 Created`):

```json
{
  "title": "পথের পাঁচালী",
  "author": "বিভূতিভূষণ বন্দ্যোপাধ্যায়",
  "price": 350,
  "in_stock": true,
  "id": 1,
  "created_at": "2026-11-24T03:43:57"
}
```

আপনার প্রজেক্ট ফোল্ডারে এখন একটি `books.db` ফাইল দেখবেন। এটিই আপনার ডেটাবেস। অ্যাপ বন্ধ করে আবার চালালেও বইটি থেকে যাবে।

## টার্মিনালে SQL দেখা { #bn-echo }

`echo=True` দেওয়ার কারণে টার্মিনালে প্রতিটি SQL দেখতে পাবেন। উপরের `POST`-এর জন্য:

```
BEGIN (implicit)
INSERT INTO books (title, author, price, in_stock) VALUES (?, ?, ?, ?) RETURNING id, created_at
[generated in 0.00018s] ('পথের পাঁচালী', 'বিভূতিভূষণ বন্দ্যোপাধ্যায়', 350, 1)
COMMIT
BEGIN (implicit)
SELECT books.id, books.title, books.author, books.price, books.in_stock, books.created_at
FROM books
WHERE books.id = ?
[generated in 0.00015s] (1,)
ROLLBACK
```

/// info | লগটি সহজ ভাষায়

* `BEGIN (implicit)`: প্রথম SQL-এর আগে নিজে থেকেই একটি ট্রানজ্যাকশন শুরু হয়েছে।
* `INSERT ... RETURNING id, created_at`: বই ঢোকানো হলো, আর ডেটাবেস যে `id` ও `created_at` বানিয়েছে তা সাথে সাথেই ফেরত আনা হলো।
* `?` চিহ্ন: মানগুলো SQL-এর ভেতরে জোড়া লাগানো হয় না, আলাদা পাঠানো হয়। তাই **SQL injection** হতে পারে না।
* `COMMIT`: পরিবর্তন স্থায়ী হলো।
* `SELECT ...`: `session.refresh(book)` রো-টি আবার পড়ে আনল।
* শেষের `ROLLBACK`: চিন্তার কিছু নেই। সেশন বন্ধ হওয়ার সময় শুধু-পড়ার ট্রানজ্যাকশনটি বন্ধ করা হয়েছে। কোনো ডেটা হারায়নি।

প্রোডাকশনে `echo=False` রাখুন, কারণ এত লগ লেখা ধীর আর এতে গোপন তথ্য ফাঁস হতে পারে।

///

## ধাপে ধাপে বোঝা { #bn-step-by-step }

### ধাপ ১: Engine ও Session factory { #bn-step-1 }

```python
DATABASE_URL = "sqlite+aiosqlite:///./books.db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

/// info | কোডটি সহজ ভাষায়

* **`engine`** হলো ডেটাবেসের সাথে যোগাযোগের কেন্দ্র। এটি কানেকশন খোলে আর একটি পুলে জমা রাখে। পুরো অ্যাপে **একটিই** engine থাকে।
* **`SessionLocal`** একটি "সেশন বানানোর কারখানা"। প্রতিটি রিকোয়েস্টে এখান থেকে নতুন সেশন নেওয়া হয়।
* **`expire_on_commit=False`**: commit-এর পরও অবজেক্টের মানগুলো পড়া যাবে। async-এ এটি প্রায় বাধ্যতামূলক। কেন, তা [MissingGreenlet](engine-session.md#s20) সেকশনে আছে।

///

/// tip | উদাহরণ দিয়ে বুঝি

**Engine** হলো ব্যাংকের শাখা, আর **Session** হলো একজন গ্রাহকের একবারের ভিজিট। শাখা সবসময় খোলা থাকে। গ্রাহক এসে কয়েকটা কাজ করেন (জমা, তোলা), কাউন্টারে সই করে (commit) চলে যান। পরের গ্রাহক নতুন ভিজিট শুরু করেন।

///

### ধাপ ২: মডেল { #bn-step-2 }

`Book` ক্লাসটি হলো `books` টেবিলের নকশা। SQLAlchemy এটি দেখে এই টেবিল বানায়:

```sql
CREATE TABLE books (
    id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    in_stock BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    PRIMARY KEY (id)
)
```

/// info | কোডটি সহজ ভাষায়

* `class Base(DeclarativeBase)`: সব মডেলের "মা" ক্লাস। এটি সব টেবিলের তালিকা (`Base.metadata`) রাখে।
* `__tablename__ = "books"`: ডেটাবেসে টেবিলের নাম।
* `id: Mapped[int] = mapped_column(primary_key=True)`: প্রাইমারি কী। মান না দিলে ডেটাবেস নিজেই ১, ২, ৩ … বসায়।
* `title: Mapped[str] = mapped_column(String(200))`: সর্বোচ্চ ২০০ অক্ষরের টেক্সট। `Mapped[str]` মানে ফাঁকা (NULL) রাখা যাবে না।
* `price: Mapped[int]`: `mapped_column()` ছাড়াই লেখা যায়, টাইপ হিন্ট থেকেই SQLAlchemy বোঝে এটি `INTEGER NOT NULL`।
* `default=True`: বই যোগের সময় মান না দিলে Python নিজে `True` বসাবে।
* `server_default=func.now()`: সময়টা বসাবে **ডেটাবেস** নিজে।

এগুলোর বিস্তারিত পাবেন [Model, Column ও Schema](models.md) অধ্যায়ে।

///

/// warning | টাকার হিসাব

এখানে সহজ রাখার জন্য দাম রাখা হয়েছে পূর্ণসংখ্যায় (টাকা)। পয়সাসহ দাম রাখতে হলে কখনো `float` নয়, `Decimal` আর `Numeric(10, 2)` ব্যবহার করুন। কারণটা দেখুন [কলাম টাইপ ম্যাপিং](models.md#s5-2) সেকশনে।

///

### ধাপ ৩: Pydantic স্কিমা { #bn-step-3 }

মডেল আর স্কিমা দুটো আলাদা জিনিস:

| | SQLAlchemy মডেল (`Book`) | Pydantic স্কিমা (`BookCreate`, `BookRead`) |
| :--- | :--- | :--- |
| কী বোঝায় | ডেটাবেসের টেবিল | API-তে কোন ডেটা আসবে বা যাবে |
| কাজ | ডেটা সংরক্ষণ ও কুয়েরি | ইনপুট ভ্যালিডেশন, আউটপুট সিরিয়ালাইজেশন |
| উদাহরণ | `id`, `created_at` সহ সব কলাম | `BookCreate`-এ `id` নেই, কারণ ক্লায়েন্ট সেটা পাঠায় না |

/// info | কোডটি সহজ ভাষায়

* **`BookCreate`**: নতুন বই যোগের সময় ক্লায়েন্ট যা পাঠাবে। `Field(ge=0)` মানে দাম ঋণাত্মক হতে পারবে না, ভুল হলে FastAPI নিজেই `422` এরর দেবে।
* **`BookUpdate`**: আপডেটের সময় সব ফিল্ড ঐচ্ছিক (`| None = None`), কারণ ক্লায়েন্ট শুধু বদলানো ফিল্ডটি পাঠাবে।
* **`BookRead`**: উত্তরে যা যাবে। `model_config = ConfigDict(from_attributes=True)` থাকার কারণে Pydantic সরাসরি SQLAlchemy অবজেক্ট (`book.title`, `book.id` …) থেকে মান পড়তে পারে।

///

### ধাপ ৪: lifespan-এ টেবিল তৈরি { #bn-step-4 }

`lifespan` ফাংশনের `yield`-এর আগের অংশ অ্যাপ চালুর সময় একবার চলে, আর পরের অংশ বন্ধের সময়। আমরা চালুর সময় `Base.metadata.create_all` দিয়ে টেবিল বানাচ্ছি। আরও জানতে দেখুন [Lifespan Events](../advanced/events.md)।

/// warning | শুধু শেখার জন্য

`create_all()` শুধু **নেই এমন টেবিল** বানায়। পরে মডেলে নতুন কলাম যোগ করলে পুরোনো টেবিলে সেটা যোগ হবে না। আসল প্রজেক্টে টেবিল বানানো ও বদলানোর কাজ করুন [Alembic](alembic.md) দিয়ে।

শেখার সময় মডেল বদলালে সবচেয়ে সহজ উপায় হলো `books.db` ফাইলটি মুছে অ্যাপ আবার চালানো।

///

`conn.run_sync(...)`: `create_all` একটি সাধারণ (sync) ফাংশন। async কানেকশনে sync ফাংশন চালাতে `run_sync` ব্যবহার করতে হয়।

### ধাপ ৫: সেশন ডিপেন্ডেন্সি { #bn-step-5 }

```python
async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

/// info | কোডটি সহজ ভাষায়

* প্রতিটি রিকোয়েস্ট এলে FastAPI `get_session()` চালায়, একটি নতুন সেশন বানিয়ে পাথ অপারেশন ফাংশনে দেয়।
* `yield`-এর পর রেসপন্স পাঠানো শেষ হলে `async with` ব্লক শেষ হয়, সেশন নিজেই বন্ধ হয়ে কানেকশন পুলে ফেরত যায়।
* `SessionDep` একটি শর্টকাট। প্রতিটি এন্ডপয়েন্টে `session: AsyncSession = Depends(get_session)` না লিখে শুধু `session: SessionDep` লিখলেই হয়।

ডিপেন্ডেন্সি নিয়ে আরও জানতে দেখুন [yield-সহ ডিপেন্ডেন্সি](../tutorial/dependencies/dependencies-with-yield.md)।

///

### ধাপ ৬: CRUD এন্ডপয়েন্ট { #bn-step-6 }

| কাজ | SQLAlchemy কোড | কোন SQL হয় |
| :--- | :--- | :--- |
| যোগ | `session.add(book)` + `await session.commit()` | `INSERT INTO books ...` |
| PK দিয়ে খোঁজা | `await session.get(Book, book_id)` | `SELECT ... WHERE books.id = ?` |
| তালিকা | `await session.scalars(select(Book).order_by(Book.id).offset(skip).limit(limit))` | `SELECT ... ORDER BY books.id LIMIT ? OFFSET ?` |
| খোঁজা | `.where(Book.title.ilike(f"%{q}%"))` | `WHERE lower(books.title) LIKE lower(?)` |
| আপডেট | অ্যাট্রিবিউট বদলে `await session.commit()` | `UPDATE books SET price=? WHERE books.id = ?` |
| মোছা | `await session.delete(book)` + `await session.commit()` | `DELETE FROM books WHERE books.id = ?` |

/// info | কোডটি সহজ ভাষায়

* **`Book(**data.model_dump())`**: Pydantic অবজেক্টকে dict বানিয়ে সেই dict দিয়ে SQLAlchemy অবজেক্ট বানানো হলো।
* **`session.add(book)`**: বইটিকে সেশনের "যোগ করার তালিকায়" রাখল। এখনো কোনো SQL যায়নি।
* **`await session.commit()`**: জমা থাকা সব পরিবর্তন ডেটাবেসে পাঠিয়ে স্থায়ী করল।
* **`select(Book)`**: একটি কুয়েরি *তৈরি* করে, চালায় না। `await session.scalars(stmt)` আসলে চালায়, আর `.all()` সব ফলাফল তালিকায় দেয়।
* **PATCH-এ `exclude_unset=True`**: ক্লায়েন্ট শুধু `{"price": 300}` পাঠালে শুধু `price` বদলাবে, বাকি ফিল্ড যেমন ছিল তেমন থাকবে। PUT ও PATCH নিয়ে বিস্তারিত পাবেন [CRUD ২](crud-update-delete.md#s36-2) অধ্যায়ে।
* **কোনো UPDATE লেখা নেই**: অবজেক্টের অ্যাট্রিবিউট বদলালেই SQLAlchemy সেটা খেয়াল রাখে (dirty tracking) আর commit-এর সময় নিজেই `UPDATE` পাঠায়, শুধু বদলানো কলামের জন্য।

///

## সাধারণ ভুল { #bn-common-mistakes }

/// warning | সাধারণ ভুল

* **`await` ভুলে যাওয়া**: `session.commit()` লিখে `await` না দিলে কিছুই হয় না, শুধু একটি সতর্কবার্তা আসে। সব ডেটাবেস কলে `await` দিন।
* **`commit()` ভুলে যাওয়া**: `session.add()` করে commit না করলে রিকোয়েস্ট শেষে সব পরিবর্তন বাতিল হয়ে যায়।
* **`from_attributes=True` না দেওয়া**: রেসপন্স মডেলে এটা না থাকলে Pydantic SQLAlchemy অবজেক্ট পড়তে পারবে না, এরর দেবে।
* **async URL না দেওয়া**: `sqlite:///./books.db` লিখলে async engine চলবে না। লিখতে হবে `sqlite+aiosqlite:///./books.db`।
* **একটি সেশন সব রিকোয়েস্টে শেয়ার করা**: গ্লোবাল একটি `session` বানিয়ে সব জায়গায় ব্যবহার করবেন না। প্রতি রিকোয়েস্টে নতুন সেশন, ঠিক যেমনটা `get_session` করে।

///

## PostgreSQL-এ যাওয়া { #bn-to-postgresql }

কোড একই থাকবে, শুধু ড্রাইভার ইনস্টল করে URL বদলান:

```bash
pip install asyncpg
```

```python
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/shop"
```

ব্যস! SQLAlchemy এখন PostgreSQL-এর উপযোগী SQL বানাবে (যেমন `?`-এর বদলে `$1`, আর `ILIKE` সরাসরি)।

## নিজে চেষ্টা করুন { #bn-exercises }

1. `Book`-এ `pages: Mapped[int | None]` কলাম যোগ করুন। তিনটি স্কিমাতেই যোগ করতে ভুলবেন না, আর `books.db` মুছে অ্যাপ আবার চালান।
2. `GET /books`-এ `in_stock: bool | None = None` কুয়েরি প্যারামিটার যোগ করুন, যাতে শুধু স্টকে থাকা বই দেখা যায়।
3. `GET /books/count` এন্ডপয়েন্ট বানান। ইঙ্গিত: `await session.scalar(select(func.count()).select_from(Book))`। এই পাথ অপারেশনটি `/books/{book_id}`-এর **আগে** লিখবেন, নইলে FastAPI `"count"`-কে `book_id` ভেবে `422` এরর দেবে।

/// check | সংক্ষেপে মনে রাখুন

* একটি অ্যাপে একটি `engine`, প্রতি রিকোয়েস্টে একটি নতুন `AsyncSession`।
* মডেল (`Book`) = ডেটাবেসের টেবিল; স্কিমা (`BookCreate`, `BookRead`) = API-র ইনপুট ও আউটপুট।
* লেখা: `add()` → `commit()` → দরকারে `refresh()`। পড়া: `get()` অথবা `scalars(select(...))`।
* `create_all()` শুধু শেখার জন্য; আসল প্রজেক্টে Alembic।

///

**পরের ধাপ:** মডেলের সব খুঁটিনাটি শিখুন [Model, Column ও Schema](models.md) অধ্যায়ে।
