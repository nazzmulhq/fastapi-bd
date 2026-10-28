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

| Field Type | Input | Strict | Input Source | Conditions |
| - | - | - | - | - |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bool`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Same allowed values as for `str`. Assumes UTF-8. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0.0, 1.0`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0, 1`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Case-insensitive. Allowed values: `'0'`, `'off'`, `'f'`, `'false'`, `'n'`, `'no'`, `'1'`, `'on'`, `'t'`, `'true'`, `'y'`, `'yes'`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Allowed values: `Decimal(0), Decimal(1)`. |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`bytearray`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Decoded according to the `val_json_bytes` setting (UTF-8 by default). |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Decoded according to the `val_json_bytes` setting (UTF-8 by default). |
| <span style="white-space: nowrap;">`callable`</span> | <span style="white-space: nowrap;">`-`</span> |  | <span style="white-space: nowrap;">JSON</span> | Never valid. |
| <span style="white-space: nowrap;">`callable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `callable()` check must return `True`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`complex`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid complex string, e.g. `1+2j`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid complex string, e.g. `1+2j`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `YYYY-MM-DD`, a datetime with a zero time component, or a unix timestamp. Must be exact date. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`date`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`datetime`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact date, eg. no `H`, `M`, `S`, `f`. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DD`, or a unix timestamp. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DD`, a datetime with a zero time component, or a unix timestamp. Must be exact date. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, `YYYY-MM-DD`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`date`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`datetime`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, `YYYY-MM-DD`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`deque`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid float, e.g. `3.141`, `1e3` or `inf`. Leading and trailing whitespace and underscores are allowed. Assumes UTF-8. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid float, e.g. `3.141`, `1e3` or `inf`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement `__float__()` or `__index__()`. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`frozendict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. The input must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`frozenset`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid integer, e.g. `123`. Leading and trailing whitespace, underscores and a zero fractional part (e.g. `1.0`) are allowed. Assumes UTF-8. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`, raises error for `nan`, `inf`. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid integer, e.g. `123`. Leading and trailing whitespace, underscores and a zero fractional part (e.g. `1.0`) are allowed. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Enum`</span> |  | <span style="white-space: nowrap;">Python</span> | Uses the value of the enum member. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Fraction`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`set`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`bytearray`</span> |  | <span style="white-space: nowrap;">Python</span> | Assumes UTF-8, error on unicode decoding error. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Assumes UTF-8, error on unicode decoding error. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`Enum`</span> |  | <span style="white-space: nowrap;">Python</span> | Uses the value of the enum member. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399.9*`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`time`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds, range `0 - 86399.9*`. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/), (UTF-8). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`timedelta`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`type`</span> | <span style="white-space: nowrap;">`-`</span> |  | <span style="white-space: nowrap;">JSON</span> | Never valid. |
| <span style="white-space: nowrap;">`type`</span> | <span style="white-space: nowrap;">`type`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Any`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Counter`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid decimal, e.g. `3.141` or `1e3`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Decimal tuple form, e.g. `(0, (1, 4, 1), -2)`. |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Any`</span> |  | <span style="white-space: nowrap;">Python</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Enum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid fraction, e.g. `1/3` or `0.5`. |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid fraction, e.g. `1/3` or `0.5`. |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Hashable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `isinstance()` check against `Hashable` must return `True`. |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Network`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP network, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Network`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Validated as the wrapped type. |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `isinstance()` check must return `True`. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be one of the enum values, without type coercion. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`Any`</span> |  | <span style="white-space: nowrap;">Python</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`IntEnum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any object for which `iter()` succeeds. Items are validated lazily. |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Literal`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be equal to one of the literal values. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`None`</span> | <span style="white-space: nowrap;">`None`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`OrderedDict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`Path`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Input must be a valid pattern. Not valid for `Pattern[str]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be a valid pattern. Not valid for `Pattern[bytes]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`Pattern`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | The pattern type (`str` or `bytes`) must match. |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | 16 raw bytes, or a UTF-8 encoded UUID string. |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`UUID`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |

///

/// tab | JSON

| Field Type | Input | Strict | Input Source | Conditions |
| - | - | - | - | - |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bool`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0.0, 1.0`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0, 1`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Case-insensitive. Allowed values: `'0'`, `'off'`, `'f'`, `'false'`, `'n'`, `'no'`, `'1'`, `'on'`, `'t'`, `'true'`, `'y'`, `'yes'`. |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Decoded according to the `val_json_bytes` setting (UTF-8 by default). |
| <span style="white-space: nowrap;">`callable`</span> | <span style="white-space: nowrap;">`-`</span> |  | <span style="white-space: nowrap;">JSON</span> | Never valid. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid complex string, e.g. `1+2j`. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DD`, or a unix timestamp. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DD`, a datetime with a zero time component, or a unix timestamp. Must be exact date. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, `YYYY-MM-DD`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid float, e.g. `3.141`, `1e3` or `inf`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`, raises error for `nan`, `inf`. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid integer, e.g. `123`. Leading and trailing whitespace, underscores and a zero fractional part (e.g. `1.0`) are allowed. |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399.9*`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`type`</span> | <span style="white-space: nowrap;">`-`</span> |  | <span style="white-space: nowrap;">JSON</span> | Never valid. |
| <span style="white-space: nowrap;">`Any`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid decimal, e.g. `3.141` or `1e3`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid fraction, e.g. `1/3` or `0.5`. |
| <span style="white-space: nowrap;">`Hashable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `isinstance()` check against `Hashable` must return `True`. |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP network, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Validated as the wrapped type. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be one of the enum values, without type coercion. |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Literal`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be equal to one of the literal values. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`None`</span> | <span style="white-space: nowrap;">`None`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be a valid pattern. Not valid for `Pattern[bytes]`. |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |

///

/// tab | JSON - Strict

| Field Type | Input | Strict | Input Source | Conditions |
| - | - | - | - | - |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bool`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Decoded according to the `val_json_bytes` setting (UTF-8 by default). |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid complex string, e.g. `1+2j`. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DD`, or a unix timestamp. Must be exact date. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Any`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Must be a valid fraction, e.g. `1/3` or `0.5`. |
| <span style="white-space: nowrap;">`Hashable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `isinstance()` check against `Hashable` must return `True`. |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Validated as the wrapped type. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> | Input value must be one of the enum values, without type coercion. |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Literal`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be equal to one of the literal values. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`None`</span> | <span style="white-space: nowrap;">`None`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be a valid pattern. Not valid for `Pattern[bytes]`. |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`Array`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`Object`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">JSON</span> |  |

///

/// tab | Python

| Field Type | Input | Strict | Input Source | Conditions |
| - | - | - | - | - |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bool`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Same allowed values as for `str`. Assumes UTF-8. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0.0, 1.0`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Allowed values: `0, 1`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Case-insensitive. Allowed values: `'0'`, `'off'`, `'f'`, `'false'`, `'n'`, `'no'`, `'1'`, `'on'`, `'t'`, `'true'`, `'y'`, `'yes'`. |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Allowed values: `Decimal(0), Decimal(1)`. |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`bytearray`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Decoded according to the `val_json_bytes` setting (UTF-8 by default). |
| <span style="white-space: nowrap;">`callable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `callable()` check must return `True`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`complex`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid complex string, e.g. `1+2j`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `YYYY-MM-DD`, a datetime with a zero time component, or a unix timestamp. Must be exact date. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`date`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`datetime`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact date, eg. no `H`, `M`, `S`, `f`. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DD`, a datetime with a zero time component, or a unix timestamp. Must be exact date. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. Must be exact date. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, `YYYY-MM-DD`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`date`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`datetime`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `YYYY-MM-DDTHH:MM:SS.f`, `YYYY-MM-DD`, or a unix timestamp. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds or milliseconds from epoch, depending on the `val_temporal_unit` setting. |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`deque`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid float, e.g. `3.141`, `1e3` or `inf`. Leading and trailing whitespace and underscores are allowed. Assumes UTF-8. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid float, e.g. `3.141`, `1e3` or `inf`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement `__float__()` or `__index__()`. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`frozendict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. The input must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`frozenset`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`bool`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid integer, e.g. `123`. Leading and trailing whitespace, underscores and a zero fractional part (e.g. `1.0`) are allowed. Assumes UTF-8. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`, raises error for `nan`, `inf`. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid integer, e.g. `123`. Leading and trailing whitespace, underscores and a zero fractional part (e.g. `1.0`) are allowed. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Enum`</span> |  | <span style="white-space: nowrap;">Python</span> | Uses the value of the enum member. |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`Fraction`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`set`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`bytearray`</span> |  | <span style="white-space: nowrap;">Python</span> | Assumes UTF-8, error on unicode decoding error. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Assumes UTF-8, error on unicode decoding error. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Only if `coerce_numbers_to_str` is enabled. |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`Enum`</span> |  | <span style="white-space: nowrap;">Python</span> | Uses the value of the enum member. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). Assumes UTF-8. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399.9*`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds, range `0 - 86399`. |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `HH:MM[:SS[.FFFFFF]]`, with an optional timezone offset. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`time`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds, range `0 - 86399.9*`. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/), (UTF-8). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Format: `ISO8601`. See [speedate](https://docs.rs/speedate/latest/speedate/). |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`timedelta`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Interpreted as seconds. |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`dict_keys`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`dict_values`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`frozenset`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`list`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`set`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> |  | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`type`</span> | <span style="white-space: nowrap;">`type`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Any`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be exact int, e.g. `val % 1 == 0`. |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Counter`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Must be a valid decimal, e.g. `3.141` or `1e3`. Leading and trailing whitespace and underscores are allowed. |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Decimal tuple form, e.g. `(0, (1, 4, 1), -2)`. |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Any`</span> |  | <span style="white-space: nowrap;">Python</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Enum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`float`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> | Must be a valid fraction, e.g. `1/3` or `0.5`. |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`Decimal`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Hashable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `isinstance()` check against `Hashable` must return `True`. |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Network`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP network, must be less than `2**32` |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Network`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`int`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | integer representing the IP address, must be less than `2**128` |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python & JSON</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`tuple`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> |  | <span style="white-space: nowrap;">Python</span> | Host bits must be zero. |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `isinstance()` check must return `True`. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`Any`</span> |  | <span style="white-space: nowrap;">Python</span> | Input value must be convertible to enum values. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`IntEnum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any object for which `iter()` succeeds. Items are validated lazily. |
| <span style="white-space: nowrap;">`Literal`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be equal to one of the literal values. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`None`</span> | <span style="white-space: nowrap;">`None`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`dict`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`OrderedDict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`Path`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Input must be a valid pattern. Not valid for `Pattern[str]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be a valid pattern. Not valid for `Pattern[bytes]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`Pattern`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | The pattern type (`str` or `bytes`) must match. |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`deque`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`Mapping`</span> |  | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`bytes`</span> |  | <span style="white-space: nowrap;">Python</span> | 16 raw bytes, or a UTF-8 encoded UUID string. |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`str`</span> |  | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`UUID`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |

///

/// tab | Python - Strict

| Field Type | Input | Strict | Input Source | Conditions |
| - | - | - | - | - |
| <span style="white-space: nowrap;">`bool`</span> | <span style="white-space: nowrap;">`bool`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`bytes`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`callable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `callable()` check must return `True`. |
| <span style="white-space: nowrap;">`complex`</span> | <span style="white-space: nowrap;">`complex`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`date`</span> | <span style="white-space: nowrap;">`date`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`datetime`</span> | <span style="white-space: nowrap;">`datetime`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`deque`</span> | <span style="white-space: nowrap;">`deque`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`dict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`float`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement `__float__()` or `__index__()`. |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`float`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`frozendict`</span> | <span style="white-space: nowrap;">`frozendict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `frozendict` is only available in Python 3.15 and above. |
| <span style="white-space: nowrap;">`frozenset`</span> | <span style="white-space: nowrap;">`frozenset`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`int`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `bool` is explicitly forbidden. |
| <span style="white-space: nowrap;">`list`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`namedtuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`set`</span> | <span style="white-space: nowrap;">`set`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`str`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`time`</span> | <span style="white-space: nowrap;">`time`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`timedelta`</span> | <span style="white-space: nowrap;">`timedelta`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`tuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`type`</span> | <span style="white-space: nowrap;">`type`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Any`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`int`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`ByteSize`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`Counter`</span> | <span style="white-space: nowrap;">`Counter`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Decimal`</span> | <span style="white-space: nowrap;">`Decimal`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Enum`</span> | <span style="white-space: nowrap;">`Enum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Fraction`</span> | <span style="white-space: nowrap;">`Fraction`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Hashable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | `isinstance()` check against `Hashable` must return `True`. |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Address`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Interface`</span> | <span style="white-space: nowrap;">`IPv4Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv4Network`</span> | <span style="white-space: nowrap;">`IPv4Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Address`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Address`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Interface`</span> | <span style="white-space: nowrap;">`IPv6Interface`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`IPv6Network`</span> | <span style="white-space: nowrap;">`IPv6Network`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`InstanceOf`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | `isinstance()` check must return `True`. |
| <span style="white-space: nowrap;">`IntEnum`</span> | <span style="white-space: nowrap;">`IntEnum`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Iterable`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any object for which `iter()` succeeds. Items are validated lazily. |
| <span style="white-space: nowrap;">`Literal`</span> | <span style="white-space: nowrap;">`Any`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be equal to one of the literal values. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`namedtuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Iterable`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Any iterable except `str`, `bytes`, `bytearray`, `dict` and mappings, e.g. generators. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`Mapping`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Must implement the mapping interface and have an `items()` method. |
| <span style="white-space: nowrap;">`NamedTuple`</span> | <span style="white-space: nowrap;">`NamedTuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`None`</span> | <span style="white-space: nowrap;">`None`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> |  |
| <span style="white-space: nowrap;">`OrderedDict`</span> | <span style="white-space: nowrap;">`OrderedDict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Path`</span> | <span style="white-space: nowrap;">`Path`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`bytes`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | Input must be a valid pattern. Not valid for `Pattern[str]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`str`</span> | ✓ | <span style="white-space: nowrap;">Python & JSON</span> | Input must be a valid pattern. Not valid for `Pattern[bytes]`. |
| <span style="white-space: nowrap;">`Pattern`</span> | <span style="white-space: nowrap;">`Pattern`</span> | ✓ | <span style="white-space: nowrap;">Python</span> | The pattern type (`str` or `bytes`) must match. |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`list`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`Sequence`</span> | <span style="white-space: nowrap;">`tuple`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`TypedDict`</span> | <span style="white-space: nowrap;">`dict`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |
| <span style="white-space: nowrap;">`UUID`</span> | <span style="white-space: nowrap;">`UUID`</span> | ✓ | <span style="white-space: nowrap;">Python</span> |  |

///

/// check | সংক্ষেপে মনে রাখুন

* প্রথমে Field Type আর Input মিলিয়ে সারিটি খুঁজুন; সারি না থাকলে রূপান্তর হয় না।
* Strict কলামে ✓ না থাকলে সেটি শুধু ডিফল্ট lax মোডে চলে।
* Input Source দেখে নিন: JSON থেকে আসা ডেটার নিয়ম কখনো কখনো আলাদা।

///
