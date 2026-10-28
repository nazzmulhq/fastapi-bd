# Conversion Table { #conversion-table }

/// note | এই পেজে যা শিখবেন

* যাচাইয়ের সময় Pydantic কোন ইনপুট টাইপকে কোন ফিল্ড টাইপে রূপান্তর করে, strict আর lax দুই মোডেই।
* সারণির প্রতিটি কলাম কীভাবে পড়বেন, আর "Conditions" কলামের প্রচলিত কথাগুলোর বাংলা অর্থ।
* কয়েকটি বাস্তব উদাহরণ, যাতে সারণি মিলিয়ে দেখতে পারেন।

///

নিচের সারণিতে বিস্তারিত দেওয়া আছে, যাচাইয়ের সময় Pydantic strict আর lax দুই মোডে কীভাবে ডেটা রূপান্তর করে।

"Strict" কলামে টিকচিহ্ন (✓) থাকে সেই রূপান্তরগুলোর জন্য, যেগুলো
[Strict Mode](strict_mode.md)-এ যাচাইয়ের সময়ও অনুমোদিত।

## সারণি কীভাবে পড়বেন { #bn-how-to-read }

/// tip | উদাহরণ দিয়ে বুঝি

এটি মুদ্রা বিনিময়ের তালিকার মতো: "কোন মুদ্রা (Input) দিলে কোন মুদ্রায় (Field Type) বদলে দেওয়া হয়, আর কোন শর্তে"। কোনো সারি না থাকলে বুঝবেন সেই বিনিময় হয় না, অর্থাৎ যাচাই এরর।

///

| কলাম | অর্থ |
| --- | --- |
| **Field Type** | মডেলের ফিল্ডে আপনি যে টাইপ লিখেছেন, যেমন `x: int` হলে `int` |
| **Input** | যে ধরনের মান ইনপুট হিসেবে এসেছে, যেমন `'123'` হলে `str` |
| **Strict** | ✓ থাকলে strict mode-এও এই রূপান্তর চলে; ফাঁকা থাকলে শুধু lax (ডিফল্ট) মোডে |
| **Input Source** | `Python` = `model_validate()` দিয়ে Python অবজেক্ট; `JSON` = `model_validate_json()` দিয়ে JSON লেখা; `Python & JSON` = দুটোতেই |
| **Conditions** | রূপান্তর সফল হওয়ার বাড়তি শর্ত |

ওপরের ট্যাবগুলো দিয়ে সারণি ছেঁকে দেখতে পারেন: শুধু JSON, শুধু Python, বা strict mode-এ যা চলে।

### "Conditions" কলামের প্রচলিত কথা { #bn-conditions }

| ইংরেজি | মানে |
| --- | --- |
| Allowed values: ... | শুধু এই মানগুলো গ্রহণযোগ্য, যেমন `bool`-এর জন্য `0, 1` |
| Must be exact int | দশমিক অংশ শূন্য হতে হবে: `3.0` চলবে, `3.5` চলবে না |
| Leading and trailing whitespace, underscores ... are allowed | শুরু/শেষের ফাঁকা জায়গা আর `1_000`-এর মতো আন্ডারস্কোর চলে |
| Assumes UTF-8 | `bytes` হলে UTF-8 হিসেবে লেখায় রূপান্তর করা হয় |
| Format: ... See speedate | তারিখ/সময়ের লেখার নিয়ম; Pydantic `speedate` লাইব্রেরি দিয়ে পড়ে |
| Interpreted as seconds or milliseconds from epoch | সংখ্যাটি ১৯৭০ সাল থেকে কত সেকেন্ড বা মিলিসেকেন্ড, তা হিসেবে ধরা হয় |
| Any iterable except ... and mappings, e.g. generators | তালিকা-জাতীয় যেকোনো জিনিস (যেমন জেনারেটর) চলে, তবে `str`, `bytes`, ডিকশনারি ইত্যাদি নয় |
| Must implement the mapping interface | ডিকশনারির মতো আচরণ করতে হবে |
| Host bits must be zero | IP নেটওয়ার্ক ঠিকানায় host অংশ শূন্য হতে হবে, যেমন `192.168.0.0/24` |
| Input value must be convertible to enum values | মানটি enum-এর কোনো একটি মানে বদলানো যেতে হবে |
| Only if ... is enabled | নির্দিষ্ট কনফিগারেশন চালু থাকলেই |
| Never valid | কখনোই গ্রহণযোগ্য নয় |

## কয়েকটি উদাহরণ { #bn-examples }

```python
from datetime import date

from pydantic import BaseModel, ConfigDict


class Lax(BaseModel):
    n: int
    ok: bool
    d: date
    tags: list[str]


print(Lax(n='1_000', ok='yes', d='2024-03-01', tags=('a', 'b')))
#> n=1000 ok=True d=datetime.date(2024, 3, 1) tags=['a', 'b']


class Strict(BaseModel):
    model_config = ConfigDict(strict=True)

    n: int
    d: date


Strict.model_validate_json('{"n": 5, "d": "2024-03-01"}')  # ✅ JSON-এ তারিখ স্ট্রিং strict-এও চলে
# Strict(n='5', d=date(2024, 3, 1))  ❌ Python-এ strict mode-এ '5' স্ট্রিং int নয়
```

/// info | কোডটি সহজ ভাষায়

* `'1_000'` → `1000`: সারণির `int` ← `str` সারি, শর্ত "underscores are allowed"।
* `'yes'` → `True`: `bool` ← `str` সারি, "Allowed values"-এ `yes` আছে।
* `('a', 'b')` → `['a', 'b']`: `list` ← `tuple` সারি।
* strict mode-এ JSON থেকে তারিখের স্ট্রিং চলে (সারিতে Input Source `JSON`, Strict ✓), কিন্তু Python থেকে `'5'` স্ট্রিং `int` হিসেবে চলে না।

///

/// tab | সব

⟦CODE1⟧

///

/// tab | JSON

⟦CODE2⟧

///

/// tab | JSON - Strict

⟦CODE3⟧

///

/// tab | Python

⟦CODE4⟧

///

/// tab | Python - Strict

⟦CODE5⟧

///

/// check | সংক্ষেপে মনে রাখুন

* প্রথমে Field Type আর Input মিলিয়ে সারিটি খুঁজুন; সারি না থাকলে রূপান্তর হয় না।
* Strict কলামে ✓ না থাকলে সেটি শুধু ডিফল্ট lax মোডে চলে।
* Input Source দেখে নিন: JSON থেকে আসা ডেটার নিয়ম কখনো কখনো আলাদা।

///
