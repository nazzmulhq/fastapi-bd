# Alembic দিয়ে মাইগ্রেশন { #sqlalchemy-alembic }

/// note | এই পেজে যা শিখবেন

* মাইগ্রেশন কী, আর `create_all()` কেন প্রোডাকশনে যথেষ্ট নয়।
* async প্রজেক্টে Alembic সেটআপ, আর `env.py`-কে আপনার `Base` ও `settings`-এর সাথে জোড়া।
* `autogenerate` দিয়ে মাইগ্রেশন তৈরি, `upgrade` / `downgrade`, ইতিহাস দেখা।
* autogenerate কী ধরতে পারে না (যেমন নাম বদল), আর ডেটা মাইগ্রেশন।
* টিমে ও প্রোডাকশনে মাইগ্রেশনের নিয়ম, আর সাধারণ এরর।

///

## মাইগ্রেশন কী? { #bn-what }

আপনার অ্যাপ চলছে, ডেটাবেসে হাজার অর্ডার। এখন `orders` টেবিলে একটি নতুন কলাম `note` লাগবে। `create_all()` এখানে কিছুই করবে না, কারণ টেবিল আগে থেকেই আছে। আর টেবিল মুছে আবার বানালে সব ডেটা হারাবে।

**মাইগ্রেশন** হলো ডেটাবেসের কাঠামো (স্কিমা) ধাপে ধাপে বদলানোর ছোট ছোট স্ক্রিপ্ট, যেমন "`orders`-এ `note` কলাম যোগ করো"। প্রতিটি স্ক্রিপ্টের একটি ভার্সন নম্বর থাকে, আর ডেটাবেস মনে রাখে কোন পর্যন্ত চালানো হয়েছে।

/// tip | উদাহরণ দিয়ে বুঝি

**Alembic হলো ডেটাবেসের জন্য Git।** Git যেমন কোডের প্রতিটি পরিবর্তনের ইতিহাস রাখে, আর আপনি যেকোনো ভার্সনে যেতে পারেন, Alembic তেমনি স্কিমার প্রতিটি পরিবর্তন রাখে। নতুন ডেভেলপার এক কমান্ডে (`alembic upgrade head`) নিজের খালি ডেটাবেসকে একদম সর্বশেষ অবস্থায় আনতে পারেন। প্রোডাকশনেও একই কমান্ড, একই ফল।

///

## ইনস্টল ও শুরু { #bn-init }

```bash
pip install alembic
alembic init -t async migrations
```

`-t async` দিলে async engine-এর উপযোগী টেমপ্লেট তৈরি হয়। দুটি জিনিস পাবেন:

```
alembic.ini              # Alembic-এর কনফিগারেশন
migrations/
├── env.py               # মাইগ্রেশন কীভাবে চলবে (এটা আমরা বদলাব)
├── script.py.mako       # নতুন মাইগ্রেশন ফাইলের টেমপ্লেট
└── versions/            # মাইগ্রেশন ফাইলগুলো এখানে জমা হবে
```

`alembic.ini`-তে `sqlalchemy.url = driver://user:pass@localhost/dbname` লাইনটি যেমন আছে তেমন রাখুন। আসল URL আমরা `env.py`-তে `settings` থেকে বসাব, যাতে পাসওয়ার্ড ফাইলে না থাকে।

## `env.py` কনফিগার করা { #bn-env-py }

`migrations/env.py` পুরোটা এভাবে লিখুন:

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import app.models  # noqa: F401  — সব মডেল লোড হোক, যাতে metadata-তে সব টেবিল থাকে
from app.core.config import settings
from app.core.database import Base

config = context.config
# ডেটাবেস URL আসবে settings (.env) থেকে; '%' থাকলে configparser-এর জন্য '%%' করতে হয়
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate এই metadata-কে আসল ডেটাবেসের সাথে তুলনা করবে
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: ডেটাবেসে না গিয়ে শুধু SQL স্ক্রিপ্ট তৈরি।"""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,   # server_default বদলালেও ধরবে
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,       # মাইগ্রেশন একবারের কাজ, পুলের দরকার নেই
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)   # Alembic নিজে sync, তাই run_sync
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

/// info | কোডটি সহজ ভাষায়

টেমপ্লেট থেকে আমরা মাত্র তিনটি জিনিস বদলেছি:

1. **`import app.models`**: এটা না থাকলে মডেলগুলো লোডই হয় না, `Base.metadata` খালি থাকে, আর autogenerate ভাবে আপনি সব টেবিল মুছে ফেলতে চান!
2. **`config.set_main_option("sqlalchemy.url", ...)`**: URL আসছে `.env` থেকে, অ্যাপ যেখান থেকে পায় ঠিক সেখান থেকে।
3. **`target_metadata = Base.metadata`**: autogenerate কিসের সাথে তুলনা করবে।

`compare_server_default=True` দিলে `server_default` বদলানোও ধরা পড়ে। কলামের টাইপ বদল Alembic-এর নতুন ভার্সনে নিজে থেকেই ধরা হয়।

///

## প্রথম মাইগ্রেশন { #bn-first-migration }

```bash
alembic revision --autogenerate -m "create orders and order_items"
```

```
INFO  [alembic.autogenerate.compare.tables] Detected added table 'orders'
INFO  [alembic.autogenerate.compare.constraints] Detected added index 'ix_orders_customer_id' on '('customer_id',)'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'order_items'
...
Generating migrations/versions/f61686a6d6ee_create_orders_and_order_items.py ...  done
```

তৈরি হওয়া ফাইলটি খুলে **অবশ্যই পড়ে দেখুন**:

```python
def upgrade() -> None:
    op.create_table('orders',
    sa.Column('order_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('order_code', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('order_id', name=op.f('pk_orders')),
    sa.UniqueConstraint('order_code', name=op.f('uq_orders_order_code'))
    )
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    ...
    op.create_table('order_items',
    ...
    sa.ForeignKeyConstraint(['order_id'], ['orders.order_id'], name=op.f('fk_order_items_order_id_orders'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('item_id', name=op.f('pk_order_items'))
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    ...
    op.drop_table('orders')
```

/// info | কোডটি সহজ ভাষায়

* `upgrade()`: সামনে যাওয়ার ধাপ। `downgrade()`: পেছনে ফেরার ধাপ, ঠিক উল্টো ক্রমে।
* `pk_orders`, `uq_orders_order_code`, `fk_order_items_order_id_orders`: সব নাম এসেছে আমাদের [naming convention](models.md#s3) থেকে। তাই সব পরিবেশে (ডেভ, টেস্ট, প্রোডাকশন) নামগুলো হুবহু একই।
* ফাইলের নামের শুরুর `f61686a6d6ee` হলো ভার্সন id (revision)। ফাইলের ভেতরে `down_revision` বলে দেয় এর আগেরটি কোন।

///

ডেটাবেসে চালান:

```bash
alembic upgrade head
```

```
INFO  [alembic.runtime.migration] Running upgrade  -> f61686a6d6ee, create orders and order_items
```

`head` মানে "সর্বশেষ ভার্সন পর্যন্ত"। Alembic ডেটাবেসে একটি ছোট `alembic_version` টেবিল বানিয়ে সেখানে বর্তমান ভার্সন লিখে রাখে।

## মডেল বদলালে: নতুন কলাম { #bn-add-column }

`Order` মডেলে একটি কলাম যোগ করুন:

```python
note: Mapped[Optional[str]] = mapped_column(String(255))
```

তারপর:

```bash
alembic revision --autogenerate -m "add note to orders"
```

```python
def upgrade() -> None:
    op.add_column('orders', sa.Column('note', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('orders', 'note')
```

```bash
alembic upgrade head
```

পুরোনো সব রো থেকে যায়, শুধু নতুন কলাম যোগ হয় (মান `NULL`)।

## দরকারি কমান্ড { #bn-commands }

| কমান্ড | কাজ |
| :--- | :--- |
| `alembic revision --autogenerate -m "বার্তা"` | মডেল আর ডেটাবেস মিলিয়ে নতুন মাইগ্রেশন ফাইল |
| `alembic revision -m "বার্তা"` | খালি মাইগ্রেশন ফাইল (নিজে লিখবেন) |
| `alembic upgrade head` | সর্বশেষ পর্যন্ত সব চালানো |
| `alembic upgrade +1` | পরের একটি |
| `alembic downgrade -1` | এক ধাপ পেছনে |
| `alembic downgrade base` | সব মাইগ্রেশন উল্টে একদম শুরুতে (সাবধান!) |
| `alembic current` | ডেটাবেস এখন কোন ভার্সনে |
| `alembic history` | সব মাইগ্রেশনের তালিকা |
| `alembic upgrade head --sql > migrate.sql` | ডেটাবেসে না চালিয়ে শুধু SQL ফাইল (DBA-কে রিভিউর জন্য দিতে) |
| `alembic check` | মডেল আর ডেটাবেসে অমিল আছে কি না (CI-তে কাজের) |

`alembic check` সব মিললে বলে `No new upgrade operations detected.`। কেউ মডেল বদলে মাইগ্রেশন বানাতে ভুলে গেলে এটা ফেইল করে।

## autogenerate যা ধরতে পারে না { #bn-autogenerate-limits }

autogenerate খুব কাজের, কিন্তু অন্ধভাবে বিশ্বাস করবেন না:

| পরিবর্তন | autogenerate কী করে | আপনি কী করবেন |
| :--- | :--- | :--- |
| কলাম বা টেবিলের **নাম বদল** | পুরোনোটা মুছে নতুনটা যোগ করে → **ডেটা হারায়!** | নিজে `op.alter_column("orders", "note", new_column_name="remarks")` লিখুন |
| PostgreSQL `ENUM`-এ নতুন মান | ধরে না | `op.execute("ALTER TYPE order_status ADD VALUE 'REFUNDED'")` |
| ডেটা বদলানো (যেমন পুরোনো রো-তে মান বসানো) | কখনো করে না | ডেটা মাইগ্রেশন, নিচে দেখুন |
| মডেল ইমপোর্ট না হলে | ভাবে সব টেবিল মুছে ফেলা হয়েছে | `env.py`-তে `import app.models` |

/// danger | বিপদ

মাইগ্রেশন ফাইলে `op.drop_table` বা `op.drop_column` দেখলে থামুন। নিশ্চিত হন যে সত্যিই ডেটা মুছতে চান, নাকি এটা আসলে একটি নাম বদল যা autogenerate ভুল বুঝেছে।

///

## ডেটা মাইগ্রেশন { #bn-data-migration }

ধরুন নতুন একটি **বাধ্যতামূলক** কলাম `priority` যোগ করতে চান। সরাসরি `nullable=False` দিয়ে যোগ করলে পুরোনো রো-গুলোর মান কী হবে? তাই তিন ধাপে:

```python
def upgrade() -> None:
    # ১. প্রথমে NULL-যোগ্য হিসেবে যোগ
    op.add_column("orders", sa.Column("priority", sa.Integer(), nullable=True))
    # ২. পুরোনো সব রো-তে একটি মান
    op.execute("UPDATE orders SET priority = 0 WHERE priority IS NULL")
    # ৩. এখন বাধ্যতামূলক করা
    op.alter_column("orders", "priority", nullable=False)


def downgrade() -> None:
    op.drop_column("orders", "priority")
```

অথবা এক লাইনে: `sa.Column("priority", sa.Integer(), nullable=False, server_default="0")`।

/// warning | মাইগ্রেশনে মডেল ইমপোর্ট নয়

মাইগ্রেশন ফাইলে `from app.models.order import Order` লিখবেন না। আজকের মডেল ছয় মাস পরে বদলে যাবে, তখন পুরোনো মাইগ্রেশন ভেঙে যাবে। SQL (`op.execute`) অথবা মাইগ্রেশনের ভেতরেই ছোট একটি `sa.table(...)` সংজ্ঞা ব্যবহার করুন।

///

## টিম ও প্রোডাকশনের নিয়ম { #bn-rules }

* **একবার চালানো মাইগ্রেশন আর বদলাবেন না।** ভুল হলে নতুন একটি মাইগ্রেশন লিখে সংশোধন করুন। অন্যদের ডেটাবেসে পুরোনোটা আগেই চলে গেছে।
* **মাইগ্রেশন ফাইল কোডের সাথে Git-এ কমিট করুন।** মডেল বদল আর তার মাইগ্রেশন একই কমিটে।
* **ডিপ্লয়ের সময় আগে মাইগ্রেশন, তারপর নতুন কোড।** যেমন Docker-এ `alembic upgrade head && fastapi run app/main.py`।
* **দুই "head" হলে:** দুজন ডেভেলপার একই সময়ে মাইগ্রেশন বানালে `alembic heads` দুটি দেখাবে। `alembic merge heads -m "merge"` দিয়ে এক করুন।
* **বড় টেবিলে সাবধান:** কোটি রো-র টেবিলে ইনডেক্স বানাতে `op.create_index(..., postgresql_concurrently=True)`, আর মাইগ্রেশনটিকে ট্রানজ্যাকশনের বাইরে চালাতে হয় (`with op.get_context().autocommit_block():`)।
* **`create_all()` বনাম Alembic:** `create_all()` শুধু শেখা বা টেস্টের জন্য। প্রোডাকশনের স্কিমা সবসময় Alembic দিয়ে।

## সাধারণ এরর { #bn-errors }

| এরর | কারণ ও সমাধান |
| :--- | :--- |
| autogenerate সব টেবিল মুছতে চাইছে | `env.py`-তে মডেল ইমপোর্ট হয়নি, বা ভুল `Base` |
| `Target database is not up to date.` | নতুন মাইগ্রেশন বানানোর আগে `alembic upgrade head` চালান |
| `Can't locate revision identified by '...'` | ডেটাবেসে এমন একটি ভার্সন লেখা যার ফাইল আপনার কাছে নেই (অন্য ব্রাঞ্চের)। সঠিক ব্রাঞ্চে যান |
| `Multiple head revisions are present` | `alembic merge heads` |
| `ModuleNotFoundError: No module named 'app'` | প্রজেক্টের রুট থেকে কমান্ড চালান; `alembic.ini`-তে `prepend_sys_path = .` আছে কি না দেখুন |
| `ValueError: invalid interpolation syntax` | URL-এ `%` আছে; `env.py`-এর `.replace("%", "%%")` লাইনটি রাখুন |

/// check | সংক্ষেপে মনে রাখুন

* `alembic init -t async migrations`, তারপর `env.py`-তে মডেল ইমপোর্ট, `settings` থেকে URL, আর `target_metadata = Base.metadata`।
* মডেল বদলান → `alembic revision --autogenerate -m "..."` → ফাইল পড়ে দেখুন → `alembic upgrade head`।
* নাম বদল, enum, ডেটা বদল নিজে লিখুন।
* চালানো মাইগ্রেশন বদলাবেন না; নতুন একটি লিখুন।
* CI-তে `alembic check`।

///

**পরের ধাপ:** প্রজেক্টের জন্য নির্ভরযোগ্য টেস্ট লিখুন [টেস্টিং](testing.md) অধ্যায়ে।
