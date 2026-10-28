# Network Types { #network-types }

/// note | এই পেজে যা পাবেন

* URL, ইমেইল, IP ঠিকানা আর ডেটাবেস সংযোগ স্ট্রিংয়ের (DSN) টাইপ, আর তাদের দরকারি অ্যাট্রিবিউট।
* `UrlConstraints` দিয়ে নিজের URL টাইপ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

### URL { #bn-urls }

| টাইপ | কী গ্রহণ করে |
| --- | --- |
| `AnyUrl` | যেকোনো scheme-এর URL |
| `AnyHttpUrl` | `http` বা `https` |
| `HttpUrl` | `http`/`https`, সর্বোচ্চ ২০৮৩ অক্ষর, host বাধ্যতামূলক |
| `WebsocketUrl`, `AnyWebsocketUrl` | `ws` বা `wss` |
| `FileUrl` | `file://` |
| `FtpUrl` | `ftp://` |
| `UrlConstraints(...)` | `Annotated` metadata: `max_length`, `allowed_schemes`, `host_required`, `default_host`, `default_port`, `default_path` |

URL অবজেক্টের দরকারি অ্যাট্রিবিউট: `scheme`, `host`, `port`, `path`, `query`, `fragment`, `username`, `password`, আর `str(url)`।

### ডেটাবেস আর সার্ভিসের DSN { #bn-dsn }

`PostgresDsn`, `MySQLDsn`, `MariaDBDsn`, `CockroachDsn`, `ClickHouseDsn`, `SnowflakeDsn`, `MongoDsn`, `RedisDsn`, `AmqpDsn`, `KafkaDsn`, `NatsDsn`: প্রতিটি নিজের অনুমোদিত scheme যাচাই করে (যেমন `postgres://`, `postgresql+asyncpg://`)। একাধিক host থাকতে পারে বলে কিছু DSN-এ `.hosts()` মেথড আছে।

### ইমেইল আর IP { #bn-email-ip }

| টাইপ | কী করে |
| --- | --- |
| `EmailStr` | বৈধ ইমেইল ঠিকানা (`pip install "pydantic[email]"` লাগে) |
| `NameEmail` | `'রহিম <rahim@example.com>'` রূপ; `.name` আর `.email` |
| `validate_email(value)` | ফাংশন: `(name, email)` ফেরত দেয় |
| `IPvAnyAddress` | IPv4 বা IPv6 ঠিকানা |
| `IPvAnyInterface` | ঠিকানা + prefix, যেমন `192.168.0.1/24` |
| `IPvAnyNetwork` | নেটওয়ার্ক, যেমন `192.168.0.0/24` |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel, HttpUrl, IPvAnyAddress, PostgresDsn


class Settings(BaseModel):
    site: HttpUrl
    db: PostgresDsn
    server_ip: IPvAnyAddress


s = Settings(site='https://example.com/path?q=1', db='postgres://u:p@localhost:5432/app', server_ip='192.168.0.1')
print(s.site.host, s.site.path, s.db.hosts()[0]['port'], s.server_ip)
#> example.com /path 5432 192.168.0.1
```

/// warning | সাধারণ ভুল

URL টাইপগুলো `str` নয়; স্ট্রিং লাগলে `str(s.site)` লিখুন। আর URL স্বাভাবিক করা হয়, তাই `'https://example.com'` dump হলে শেষে `/` যোগ হতে পারে (`'https://example.com/'`)।

///

/// check | সংক্ষেপে মনে রাখুন

* ওয়েবসাইট: `HttpUrl`; ডেটাবেস: `PostgresDsn` ইত্যাদি; ইমেইল: `EmailStr`; IP: `IPvAnyAddress`।
* অংশগুলো পেতে `.host`, `.port`, `.path`; স্ট্রিং পেতে `str(url)`।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.networks
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
