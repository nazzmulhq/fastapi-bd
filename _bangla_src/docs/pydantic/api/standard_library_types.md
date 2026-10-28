# Standard Library Types { #standard-library-types }

/// note | এই পেজে যা পাবেন

* Python-এর নিজস্ব আর standard library-র প্রতিটি সমর্থিত টাইপ (`bool`, `str`, `int`, `datetime`, `list`, `dict`, `UUID`, `Path` ...) Pydantic কীভাবে যাচাই করে।
* প্রতিটির জন্য: কোন ইনপুট গ্রহণযোগ্য (যাচাই), কোন শর্ত দেওয়া যায় (constraint), strict mode-এ কী বদলায়, আর কীভাবে dump হয়।
* প্রতিটি অংশ একই ছাঁচে সাজানো, তাই দরকারি টাইপের অংশে সরাসরি চলে যান।

///


এই অংশে সমর্থিত built-in আর standard library টাইপগুলোর তালিকা দেওয়া হলো: অনুমোদিত মান,
সম্ভাব্য শর্ত, আর কঠোরতা (strictness) কনফিগার করা যায় কিনা।

প্রতিটি টাইপের অনুমোদিত মানের সারসংক্ষেপের জন্য [রূপান্তর সারণি](../concepts/conversion_table.md)-ও দেখুন।

/// tip | কীভাবে পড়বেন

প্রতিটি টাইপের অংশে চারটি ভাগ: **যাচাই** (কোন ইনপুট চলে আর কীভাবে রূপান্তর হয়), **শর্ত** (`Field()`-এ কী দেওয়া যায়), **কঠোরতা** (strict mode-এ কী চলে), আর **সিরিয়ালাইজেশন** (dump-এ কী রূপে বের হয়, যদি আলাদা হয়)।

///

/// note | মনে রাখুন

আলাদা করে বলা না থাকলে, Python আর JSON দুই মোডেই মানগুলো যেমন আছে তেমন সিরিয়ালাইজ হয়।

///

## Boolean { #booleans }

Built-in টাইপ: [`bool`][]

<h3>যাচাই</h3>

* একটি বৈধ [`bool`][] instance, অর্থাৎ `True` বা `False`।
* পূর্ণসংখ্যা `0` বা `1`।
* একটি স্ট্রিং, যা ছোট হাতের অক্ষরে বদলালে `'0'`, `'off'`, `'f'`, `'false'`, `'n'`, `'no'`, `'1'`, `'on'` `'t'`, `'true'`, `'y'`, `'yes'`-এর একটি হয়।
* [`bytes`][] অবজেক্ট, যা স্ট্রিংয়ে decode করলে আগের নিয়ম অনুযায়ী বৈধ।

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু boolean মানই বৈধ। [`Strict()` metadata ক্লাস ব্যবহারের](../concepts/strict_mode.md#using-the-strict-metadata-class)
সুবিধাজনক বিকল্প হিসেবে Pydantic [`StrictBool`][pydantic.types.StrictBool] টাইপ দেয়।

<h3>উদাহরণ</h3>

```python
from pydantic import BaseModel, ValidationError


class BooleanModel(BaseModel):
    bool_value: bool


print(BooleanModel(bool_value=False))
#> bool_value=False
print(BooleanModel(bool_value='False'))
#> bool_value=False
print(BooleanModel(bool_value=1))
#> bool_value=True
try:
    BooleanModel(bool_value=[])
except ValidationError as e:
    print(str(e))
    """
    1 validation error for BooleanModel
    bool_value
      Input should be a valid boolean [type=bool_type, input_value=[], input_type=list]
    """
```

## স্ট্রিং { #strings }

Built-in টাইপ: [`str`][]

<h3>যাচাই</h3>

* স্ট্রিং যেমন আছে তেমন গ্রহণ হয়।
* [`bytes`][] আর [`bytearray`][] UTF-8 স্ট্রিংয়ে decode হয়।
* [Enum][enum] রূপান্তর হয় এর [`value`][enum.Enum.value] অ্যাট্রিবিউটে [`str()`][str]
  ডেকে।
* [`coerce_numbers_to_str`][pydantic.ConfigDict.coerce_numbers_to_str] সেট থাকলে, যেকোনো সংখ্যার টাইপ
  ([`int`][], [`float`][] আর [`Decimal`][decimal.Decimal]) একটি স্ট্রিংয়ে রূপান্তর হয়ে যেমন আছে তেমন
  গ্রহণ হবে।

<h3>শর্ত</h3>

স্ট্রিং নিচের শর্তগুলো সমর্থন করে:

| শর্ত         | বর্ণনা                                       | JSON Schema                                                                                                                                   |
| ------------------ | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `pattern`          | স্ট্রিংকে যে regex প্যাটার্নের সাথে মিলতে হবে        | [`pattern`](https://json-schema.org/understanding-json-schema/reference/string#regexp) keyword (নিচের [নোট](#pattern-constraint-note) দেখুন)।  |
| `min_length`       | স্ট্রিংয়ের ন্যূনতম দৈর্ঘ্য                  | [`minLength`](https://json-schema.org/understanding-json-schema/reference/string#length) keyword                                              |
| `max_length`       | স্ট্রিংয়ের সর্বোচ্চ দৈর্ঘ্য                  | [`maxLength`](https://json-schema.org/understanding-json-schema/reference/string#length) keyword                                              |
| `strip_whitespace` | শুরু আর শেষের ফাঁকা জায়গা বাদ দেবে কিনা | প্রযোজ্য নয়                                                                                                                                           |
| `to_upper`         | স্ট্রিং বড় হাতের অক্ষরে বদলাবে কিনা        | প্রযোজ্য নয়                                                                                                                                           |
| `to_lower`         | স্ট্রিং ছোট হাতের অক্ষরে বদলাবে কিনা        | প্রযোজ্য নয়                                                                                                                                           |
| `ascii_only`       | শুধু ASCII অক্ষর অনুমোদন করবে কিনা            | প্রযোজ্য নয়                                                                                                                                           |

এই শর্তগুলো [`StringConstraints`][pydantic.types.StringConstraints] metadata টাইপ দিয়ে, অথবা [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায় (`strip_whitespace`, `to_upper`, `to_lower` আর `ascii_only` ছাড়া)।

[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরিও `MinLen`, `MaxLen` আর `Len` metadata টাইপ দেয়, সাথে
`LowerCase`, `UpperCase`, `IsDigit` আর `IsAscii` predicate (অবশ্যই `str` দিয়ে প্যারামিটার দিতে হবে, যেমন `LowerCase[str]`)।

/// tip | বাংলা লেখা আর দৈর্ঘ্য

`min_length`/`max_length` Unicode অক্ষর (code point) গোনে, bytes নয়। তবে বাংলায় যুক্তাক্ষর আর কার-চিহ্ন আলাদা code point, তাই `'ক্ষ'`-এর দৈর্ঘ্য ৩ (ক + ্ + ষ)। আর `ascii_only=True` দিলে বাংলা লেখা গ্রহণ হবে না।

///

<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#pattern-constraint-note}{% endraw %}

/// note | `pattern` শর্ত

ডিফল্টভাবে, `pattern` শর্ত প্রয়োগে Pydantic Rust-এর [`regex`](https://docs.rs/regex) crate ব্যবহার করবে। regex engine নিয়ন্ত্রণ করা যায়
[`regex_engine`][pydantic.ConfigDict.regex_engine] কনফিগারেশন মান দিয়ে। `pattern`-এ একটি compile করা [regular expression অবজেক্ট][re.Pattern] দিলে,
স্বয়ংক্রিয়ভাবে Python engine ব্যবহার হবে।

JSON Schema specification যদিও [ECMA-262](https://262.ecma-international.org/11.0/index.html#sec-patterns)-এ বর্ণিত dialect অনুযায়ী বৈধ প্যাটার্ন ব্যবহারের
[পরামর্শ দেয়](https://json-schema.org/draft/2020-12/json-schema-core#name-regular-expressions), Pydantic তা জোর করে *না*।

///

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু স্ট্রিং মানই বৈধ। [`Strict()` metadata ক্লাস ব্যবহারের](../concepts/strict_mode.md#using-the-strict-metadata-class)
সুবিধাজনক বিকল্প হিসেবে Pydantic [`StrictStr`][pydantic.types.StrictStr] টাইপ দেয়।

<h3>উদাহরণ</h3>

```python
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class StringModel(BaseModel):
    str_value: str = ""
    constrained_str_value: Annotated[str, StringConstraints(to_lower=True)] = ""


print(StringModel(str_value="test").str_value)
#> test
print(StringModel(constrained_str_value='TEST').constrained_str_value)
#> test
```

## Bytes { #bytes }

Built-in টাইপ: [`bytes`][]।

আরও দেখুন: [`ByteSize`][pydantic.types.ByteSize]।

<h3>যাচাই</h3>

* [`bytes`][] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর [`bytearray`][] instance bytes-এ রূপান্তর হয়, [`val_json_bytes`][pydantic.ConfigDict.val_json_bytes] কনফিগারেশন মান অনুযায়ী
  (নাম যা-ই হোক, এটি Python আর JSON দুই মোডেই প্রযোজ্য)।

<h3>শর্ত</h3>

স্ট্রিং নিচের শর্তগুলো সমর্থন করে:

| শর্ত         | বর্ণনা                     | JSON Schema                                                                                      |
| ------------------ | --------------------------------| -------------------------------------------------------------------------------------------------|
| `min_length`       | bytes-এর ন্যূনতম দৈর্ঘ্য | [`minLength`](https://json-schema.org/understanding-json-schema/reference/string#length) keyword |
| `max_length`       | bytes-এর সর্বোচ্চ দৈর্ঘ্য | [`maxLength`](https://json-schema.org/understanding-json-schema/reference/string#length) keyword |

[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`bytes`][] instance বৈধ। [`Strict()` metadata ক্লাস ব্যবহারের](../concepts/strict_mode.md#using-the-strict-metadata-class)
সুবিধাজনক বিকল্প হিসেবে Pydantic [`StrictBytes`][pydantic.types.StrictBytes] টাইপ দেয়।

JSON মোডে strict mode-এর কোনো প্রভাব নেই।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#number-types}{% endraw %}

## সংখ্যা { #numbers }

Pydantic Python standard library-র নিচের সংখ্যার টাইপগুলো সমর্থন করে:

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#int}{% endraw %}

### পূর্ণসংখ্যা (Integers) { #integers }

Built-in টাইপ: [`int`][]।

<h4>যাচাই</h4>

* পূর্ণসংখ্যা যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes পূর্ণসংখ্যায় রূপান্তরের চেষ্টা করা হয় আর যেমন আছে তেমন যাচাই হয়
  (বিস্তারিত জানতে দেখুন [jiter বাস্তবায়ন](https://docs.rs/jiter/latest/jiter/enum.NumberInt.html#impl-TryFrom%3C%26%5Bu8%5D%3E-for-NumberInt))।
* float পূর্ণসংখ্যা হিসেবে যাচাই হয়, যদি float ইনপুটটি অসীম বা NaN (not-a-number) না হয়
  আর দশমিক অংশ 0 হয়।
* [`Decimal`][decimal.Decimal] instance, যদি সেগুলো [সসীম][decimal.Decimal.is_finite] হয় আর
  হর 1 হয়।
* [`Fraction`][fractions.Fraction] instance, যদি সেগুলো [পূর্ণসংখ্যা][fractions.Fraction.is_integer] হয়।
* [Enum][enum] রূপান্তর হয় এর [`value`][enum.Enum.value] অ্যাট্রিবিউট দিয়ে।

<h4>শর্ত</h4>

পূর্ণসংখ্যা নিচের শর্তগুলো সমর্থন করে (সংখ্যাগুলো পূর্ণসংখ্যায় রূপান্তরযোগ্য হতে হবে):

| শর্ত    | বর্ণনা                                            | JSON Schema                                                                                             |
| ------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `le`          | মান এই সংখ্যার চেয়ে ছোট বা সমান হতে হবে    | [`maximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword          |
| `ge`          | মান এই সংখ্যার চেয়ে বড় বা সমান হতে হবে | [`minimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword          |
| `lt`          | মান এই সংখ্যার চেয়ে কঠোরভাবে ছোট হতে হবে       | [`exclusiveMaximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword |
| `gt`          | মান এই সংখ্যার চেয়ে কঠোরভাবে বড় হতে হবে    | [`exclusiveMinimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword |
| `multiple_of` | মান এই সংখ্যার গুণিতক হতে হবে            | [`multipleOf`](https://json-schema.org/understanding-json-schema/reference/numeric#multiples) keyword   |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt`, `Gt` আর `MultipleOf` metadata টাইপও
ব্যবহার করা যায়।

অনুমোদিত পূর্ণসংখ্যার মান আরও সীমিত করতে Pydantic নিচের টাইপগুলোও দেয়:

* [`PositiveInt`][pydantic.types.PositiveInt]: ইনপুট শূন্যের চেয়ে বড় হতে হবে।
* [`NegativeInt`][pydantic.types.NegativeInt]: ইনপুট শূন্যের চেয়ে ছোট হতে হবে।
* [`NonPositiveInt`][pydantic.types.NonPositiveInt]: ইনপুট শূন্যের চেয়ে ছোট বা সমান হতে হবে।
* [`NonNegativeInt`][pydantic.types.NonNegativeInt]: ইনপুট শূন্যের চেয়ে বড় বা সমান হতে হবে।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু পূর্ণসংখ্যার মান বৈধ। [`Strict()` metadata ক্লাস ব্যবহারের](../concepts/strict_mode.md#using-the-strict-metadata-class)
সুবিধাজনক বিকল্প হিসেবে Pydantic [`StrictInt`][pydantic.types.StrictInt] টাইপ দেয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#float}{% endraw %}

### দশমিক সংখ্যা (Floats) { #floats }

Built-in টাইপ: [`float`][]।

<h4>যাচাই</h4>

* float যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes float-এ রূপান্তরের চেষ্টা করা হয় আর যেমন আছে তেমন যাচাই হয়।
  (বিস্তারিত জানতে দেখুন [Rust বাস্তবায়ন](https://doc.rust-lang.org/src/core/num/float_parse.rs.html))।
* ইনপুটে একটি [`__float__()`][object.__float__] মেথড থাকলে, ইনপুটকে float-এ রূপান্তর করতে সেটি ডাকা হবে।
  `__float__()` সংজ্ঞায়িত না থাকলে, [`__index__()`][object.__index__]-এ ফিরে যায়। এর মধ্যে আছে
  (তবে এগুলোতেই সীমিত নয়) [`Decimal`][decimal.Decimal] আর [`Fraction`][fractions.Fraction] টাইপ।

<h4>শর্ত</h4>

float নিচের শর্তগুলো সমর্থন করে:

| শর্ত      | বর্ণনা                                             | JSON Schema                                                                                             |
| --------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `le`            | মান এই সংখ্যার চেয়ে ছোট বা সমান হতে হবে     | [`maximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword          |
| `ge`            | মান এই সংখ্যার চেয়ে বড় বা সমান হতে হবে  | [`minimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword          |
| `lt`            | মান এই সংখ্যার চেয়ে কঠোরভাবে ছোট হতে হবে        | [`exclusiveMaximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword |
| `gt`            | মান এই সংখ্যার চেয়ে কঠোরভাবে বড় হতে হবে     | [`exclusiveMinimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword |
| `multiple_of`   | মান এই সংখ্যার গুণিতক হতে হবে             | [`multipleOf`](https://json-schema.org/understanding-json-schema/reference/numeric#multiples) keyword   |
| `allow_inf_nan` | NaN (not-a-number) আর অসীম মান অনুমোদন করবে কিনা | প্রযোজ্য নয়                                                                                                     |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।

[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরিও `Le`, `Ge`, `Lt`, `Gt` আর `MultipleOf` metadata টাইপ দেয়,
সাথে `IsFinite`, `IsNotFinite`, `IsNan`, `IsNotNan`, `IsAscii`, `IsInfinite` আর `IsNotInfinite` predicate
(অবশ্যই `float` দিয়ে প্যারামিটার দিতে হবে, যেমন `IsFinite[float]`)। [`AllowInfNan`][pydantic.types.AllowInfNan] টাইপও ব্যবহার করা যায়।

Pydantic সুবিধাজনক alias হিসেবে নিচের টাইপগুলোও দেয়:

* [`PositiveFloat`][pydantic.types.PositiveFloat]: ইনপুট শূন্যের চেয়ে বড় হতে হবে।
* [`NegativeFloat`][pydantic.types.NegativeFloat]: ইনপুট শূন্যের চেয়ে ছোট হতে হবে।
* [`NonPositiveFloat`][pydantic.types.NonPositiveFloat]: ইনপুট শূন্যের চেয়ে ছোট বা সমান হতে হবে।
* [`NonNegativeFloat`][pydantic.types.NonNegativeFloat]: ইনপুট শূন্যের চেয়ে বড় বা সমান হতে হবে।
* [`FiniteFloat`][pydantic.types.FiniteFloat]: NaN (not-a-number) আর অসীম মান আটকায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু float মান আর যে ইনপুটের একটি [`__float__()`][object.__float__]
বা [`__index__()`][object.__index__] মেথড আছে সেগুলো বৈধ।
[`Strict()` metadata ক্লাস ব্যবহারের](../concepts/strict_mode.md#using-the-strict-metadata-class) সুবিধাজনক বিকল্প হিসেবে
Pydantic [`StrictFloat`][pydantic.types.StrictFloat] টাইপ দেয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#enumintenum}{% endraw %}

### পূর্ণসংখ্যার enum { #integer-enums }

Standard library টাইপ: [`enum.IntEnum`][]।

<h4>যাচাই</h4>

* সরাসরি [`enum.IntEnum`][] টাইপ ব্যবহার করলে, যেকোনো [`enum.IntEnum`][] instance যেমন আছে তেমন যাচাই হয়
* একটি [`enum.IntEnum`][] subclass টাইপ হিসেবে ব্যবহার করলে, যেকোনো enum সদস্য বা enum সদস্যের মানের সাথে মেলে এমন
  মান যেমন আছে তেমন যাচাই হয়।

আরও বিস্তারিত জানতে দেখুন [Enum](#enums)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#decimaldecimal}{% endraw %}

### Decimal { #decimals }

Standard library টাইপ: [`decimal.Decimal`][]।

<h4>যাচাই</h4>

* [`Decimal`][decimal.Decimal] instance যেমন আছে তেমন যাচাই হয়।
* [`Decimal`][decimal.Decimal] constructor গ্রহণ করে এমন যেকোনো মান।

<h4>শর্ত</h4>

Decimal নিচের শর্তগুলো সমর্থন করে (সংখ্যাগুলো decimal-এ রূপান্তরযোগ্য হতে হবে):

| শর্ত       | বর্ণনা                                                                                                         | JSON Schema                                                                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `le`             | মান এই সংখ্যার চেয়ে ছোট বা সমান হতে হবে                                                                 | [`maximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword                                 |
| `ge`             | মান এই সংখ্যার চেয়ে বড় বা সমান হতে হবে                                                              | [`minimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword                                 |
| `lt`             | মান এই সংখ্যার চেয়ে কঠোরভাবে ছোট হতে হবে                                                                    | [`exclusiveMaximum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword                        |
| `gt`             | মান এই সংখ্যার চেয়ে কঠোরভাবে বড় হতে হবে                                                                 | [`exclusiveMinimum`](https://json-schema.org/understanding-json-schema/reference/numeric#range) keyword                        |
| `multiple_of`    | মান এই সংখ্যার গুণিতক হতে হবে                                                                         | [`multipleOf`](https://json-schema.org/understanding-json-schema/reference/numeric#multiples) keyword                          |
| `allow_inf_nan`  | NaN (not-a-number) আর অসীম মান অনুমোদন করবে কিনা                                                             | প্রযোজ্য নয়                                                                                                                            |
| `max_digits`     | অনুমোদিত সর্বোচ্চ অঙ্কের সংখ্যা। দশমিক বিন্দুর আগের শূন্য আর শেষের শূন্য গোনা হয় না। | প্রযোজ্য নয় (নিচে দেখুন)                                                                                                           |
| `decimal_places` | দশমিকের পরে অনুমোদিত সর্বোচ্চ অঙ্ক। শেষের শূন্য গোনা হয় না।                                       | প্রযোজ্য নয় (নিচে দেখুন)                                                                                                           |

/// info | v2.12-এ বদলেছে
JSON Schema-তে `max_digits` আর `decimal_places` শর্তের সাথে মেলে এমন একটি [`pattern`](https://json-schema.org/understanding-json-schema/reference/string#regexp)
থাকে।
///

/// info | v2.14-এ বদলেছে
তৈরি হওয়া প্যাটার্ন জটিল হওয়ায় পরবর্তী ব্যবহারকারীদের সমস্যা করতে পারে বলে, JSON Schema-তে ডিফল্টভাবে আর
[`pattern`](https://json-schema.org/understanding-json-schema/reference/string#regexp) থাকে না।

[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema]-এর subclass বানিয়ে
[`get_decimal_pattern()`][pydantic.json_schema.GenerateJsonSchema.get_decimal_pattern] মেথড override করে প্যাটার্নটি যোগ করা যায়:

```python
from decimal import Decimal
from typing import Annotated

from pydantic import Field, TypeAdapter
from pydantic.json_schema import GenerateJsonSchema


class MyGenerateJsonSchema(GenerateJsonSchema):
    def get_decimal_pattern(self, schema):
        return self.build_decimal_pattern(schema)


ta = TypeAdapter(Annotated[Decimal, Field(max_digits=5, decimal_places=2)])
print(
    ta.json_schema(schema_generator=MyGenerateJsonSchema, mode='serialization')
)
"""
{
    'pattern': '^-?(?:(?:0|[1-9][0-9]{0,2})(?:\\.[0-9]{1,2}0*)?|0E[+-][1-9][0-9]*|[1-9](?:\\.[0-9]+)?E\\+[1-2])$',
    'type': 'string',
}
"""
```

তৈরি হওয়া প্যাটার্ন এখন আর lookahead assertion ব্যবহার করে না, আর exponent ও `allow_inf_nan` বিবেচনা করে।
///

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt`, `Gt` আর `MultipleOf` metadata টাইপ
আর [`AllowInfNan`][pydantic.types.AllowInfNan] টাইপও ব্যবহার করা যায়।

/// tip | টাকা-পয়সার হিসাবে

দাম বা টাকার অঙ্কে `float` নয়, `Decimal` ব্যবহার করুন: `0.1 + 0.2` float-এ `0.30000000000000004`, কিন্তু `Decimal`-এ ঠিক `0.3`। যেমন `price: Decimal = Field(max_digits=10, decimal_places=2)`।

///

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`decimal.Decimal`][] instance গ্রহণ হয়। JSON মোডে strict mode-এর কোনো প্রভাব নেই।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`Decimal`][decimal.Decimal] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।
এই আচরণ বদলাতে একটি [serializer](../concepts/serialization.md#field-plain-serializer) ব্যবহার করা যায়:

```python
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, PlainSerializer


class Model(BaseModel):
    f: Annotated[Decimal, PlainSerializer(float, when_used='json')]


my_model = Model(f=Decimal('2.1'))

print(my_model.model_dump())  # (1)!
#> {'f': Decimal('2.1')}
print(my_model.model_dump_json())  # (2)!
#> {"f":2.1}
```

1. Python মোডে, `f` একটি [`Decimal`][decimal.Decimal] instance-ই থাকে।
2. JSON মোডে, `f` একটি float হিসেবে সিরিয়ালাইজ হয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#complex}{% endraw %}

### জটিল সংখ্যা (Complex) { #complex-numbers }

/// info | v2.9-এ যোগ হয়েছে
///

Built-in টাইপ: [`complex`][]।

<h4>যাচাই</h4>

* [`complex`][] instance যেমন আছে তেমন যাচাই হয়।
* Python মোডে, ডেটা [`complex()`][complex] constructor দিয়ে যাচাই হয়।
* JSON মোডে, স্ট্রিং [`complex()`][complex] constructor দিয়ে যাচাই হয়,
   আর সংখ্যা (পূর্ণসংখ্যা আর float) বাস্তব অংশ হিসেবে ব্যবহার হয়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`complex`][] instance গ্রহণ হয়। JSON মোডে শুধু
[`complex()`][complex] constructor গ্রহণ করে এমন স্ট্রিং অনুমোদিত।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`complex`][] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#fractionsfraction}{% endraw %}

### ভগ্নাংশ (Fractions) { #fractions }

/// info | v2.10-এ যোগ হয়েছে
///

Standard library টাইপ: [`fractions.Fraction`][]।

<h4>যাচাই</h4>

* [`Fraction`][fractions.Fraction] instance যেমন আছে তেমন যাচাই হয়।
* float, স্ট্রিং আর [`decimal.Decimal`][] instance [`Fraction()`][fractions.Fraction]
  constructor দিয়ে যাচাই হয়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`Fraction`][fractions.Fraction] instance গ্রহণ হয়। JSON মোডে strict mode-এর কোনো প্রভাব নেই।

<h4>সিরিয়ালাইজেশন</h4>

ভগ্নাংশ [Python](../concepts/serialization.md#python-mode)
আর [JSON](../concepts/serialization.md#json-mode) দুই মোডেই স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#datetime-types}{% endraw %}

## তারিখ আর সময়ের টাইপ { #date-and-time-types }

Pydantic [`datetime`][] standard library-র নিচের [তারিখ আর সময়](https://docs.python.org/library/datetime.html#available-types)
টাইপগুলো সমর্থন করে:

/// warning | বর্তমান সময় নকল (mock) করা

Pydantic [freezegun](https://pypi.org/project/freezegun/)-এর সাথে ভালো কাজ করে না, কারণ freezegun [`datetime`][] ক্লাসগুলোকে
নিজের subclass দিয়ে বদলে দেয়। বদলে আমরা [time-machine](https://pypi.org/project/time-machine/) ব্যবহারের পরামর্শ দিই।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#datetimedatetime}{% endraw %}

### Datetime { #datetimes }

Standard library টাইপ: [`datetime.datetime`][]।

<h4>যাচাই</h4>

* [`datetime`][datetime.datetime] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes দুইভাবে যাচাই হয়:
    * [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) ফরম্যাট মানা স্ট্রিং (datetime আর date দুটোই)।
      আরও বিস্তারিত জানতে দেখুন [speedate](https://docs.rs/speedate/) ডকুমেন্টেশন।
    * Unix timestamp, [epoch](https://en.wikipedia.org/wiki/Unix_time) থেকে সেকেন্ড বা মিলিসেকেন্ড হিসেবে।
      আরও বিস্তারিত জানতে দেখুন [`val_temporal_unit`][pydantic.ConfigDict.val_temporal_unit] কনফিগারেশন মান।
* পূর্ণসংখ্যা আর float (বা পূর্ণসংখ্যা বা float-এ রূপান্তরযোগ্য টাইপ) unix timestamp হিসেবে যাচাই হয়,
  স্ট্রিংয়ের মতো একই নিয়মে।
* [`datetime.date`][] instance গ্রহণ হয়, আর একটি [`datetime`][datetime.datetime] instance-এ রূপান্তরিত হয়
  [`hour`][datetime.datetime.hour], [`minute`][datetime.datetime.minute], [`second`][datetime.datetime.second] আর
  [`microsecond`][datetime.datetime.microsecond] অ্যাট্রিবিউট `0`, আর [`tzinfo`][datetime.datetime.tzinfo] অ্যাট্রিবিউট `None` করে।

/// note | মনে রাখুন

নামযুক্ত timezone-এর সমর্থন ([RFC 9557](https://datatracker.ietf.org/doc/html/rfc9557.html)-এ যেমন বলা আছে, যেমন `[Asia/Dhaka]`)
[এই issue](https://github.com/pydantic/pydantic/issues/12252)-এ অনুসরণ করা যায়।

///

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`datetime`][datetime.datetime] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

<h4>শর্ত</h4>

Datetime নিচের শর্তগুলো সমর্থন করে (শর্তের মান একটি [`datetime`][datetime.datetime] instance-এ রূপান্তরযোগ্য হতে হবে):

| শর্ত | বর্ণনা                                              | JSON Schema |
| ---------- | -------------------------------------------------------- | ----------- |
| `le`       | মান এই datetime-এর চেয়ে ছোট বা সমান হতে হবে    | প্রযোজ্য নয়         |
| `ge`       | মান এই datetime-এর চেয়ে বড় বা সমান হতে হবে | প্রযোজ্য নয়         |
| `lt`       | মান এই datetime-এর চেয়ে কঠোরভাবে ছোট হতে হবে       | প্রযোজ্য নয়         |
| `gt`       | মান এই datetime-এর চেয়ে কঠোরভাবে বড় হতে হবে    | প্রযোজ্য নয়         |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt` আর `Gt` metadata টাইপও
ব্যবহার করা যায়।

অনুমোদিত datetime মান আরও সীমিত করতে Pydantic নিচের টাইপগুলোও দেয়:

* [`AwareDatetime`][pydantic.types.AwareDatetime]: ইনপুটে timezone থাকতে হবে।
* [`NaiveDatetime`][pydantic.types.NaiveDatetime]: ইনপুটে timezone থাকা *চলবে না*।
* [`PastDatetime`][pydantic.types.PastDatetime]: যাচাইয়ের সময় ইনপুট অতীতের হতে হবে।
* [`FutureDatetime`][pydantic.types.FutureDatetime]: যাচাইয়ের সময় ইনপুট ভবিষ্যতের হতে হবে।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`datetime`][datetime.datetime] instance গ্রহণ হয়। JSON মোডে শুধু
[RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) ফরম্যাট মানা স্ট্রিং (*শুধু* datetime) বা unix timestamp গ্রহণ হয়।

<h4>উদাহরণ</h4>

```python
from datetime import datetime
from typing import Annotated

from pydantic import AwareDatetime, BaseModel, Field


class Event(BaseModel):
    dt: Annotated[AwareDatetime, Field(gt=datetime(2000, 1, 1))]


event = Event(dt='2032-04-23T10:20:30.400+02:30')

print(event.model_dump())
"""
{'dt': datetime.datetime(2032, 4, 23, 10, 20, 30, 400000, tzinfo=TzInfo(9000))}
"""
print(event.model_dump_json())
#> {"dt":"2032-04-23T10:20:30.400000+02:30"}
```

/// tip | বাংলাদেশের সময়

`'2024-03-26T10:00:00+06:00'` লিখলে timezone-সহ (aware) datetime পাবেন। প্রোডাকশনে সবসময় timezone-সহ সময় রাখা ভালো; দরকারে `AwareDatetime` টাইপ দিয়ে timezone বাধ্যতামূলক করুন।

///

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#datetimedate}{% endraw %}

### তারিখ (Dates) { #dates }

Standard library টাইপ: [`datetime.date`][]।

<h4>যাচাই</h4>

* [`date`][datetime.date] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes দুইভাবে যাচাই হয়:
    * [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) তারিখ ফরম্যাট মানা স্ট্রিং (`YYYY-MM-DD`)।
      আরও বিস্তারিত জানতে দেখুন [speedate](https://docs.rs/speedate/) ডকুমেন্টেশন।
    * Unix timestamp, [epoch](https://en.wikipedia.org/wiki/Unix_time) থেকে সেকেন্ড বা মিলিসেকেন্ড হিসেবে।
      আরও বিস্তারিত জানতে দেখুন [`val_temporal_unit`][pydantic.ConfigDict.val_temporal_unit] কনফিগারেশন মান।
* যাচাই ব্যর্থ হলে, ইনপুটটি [datetime হিসেবে যাচাই](#datetimes) করা যায় (সংখ্যা হিসেবেও),
  যদি সময়ের অংশ 0 হয় আর timezone না থাকে।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`date`][datetime.date] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

<h4>শর্ত</h4>

Date নিচের শর্তগুলো সমর্থন করে (শর্তের মান একটি [`date`][datetime.date] instance-এ রূপান্তরযোগ্য হতে হবে):

| শর্ত | বর্ণনা                                          | JSON Schema |
| ---------- | ---------------------------------------------------- | ----------- |
| `le`       | মান এই তারিখের চেয়ে ছোট বা সমান হতে হবে    | প্রযোজ্য নয়         |
| `ge`       | মান এই তারিখের চেয়ে বড় বা সমান হতে হবে | প্রযোজ্য নয়         |
| `lt`       | মান এই তারিখের চেয়ে কঠোরভাবে ছোট হতে হবে       | প্রযোজ্য নয়         |
| `gt`       | মান এই তারিখের চেয়ে কঠোরভাবে বড় হতে হবে    | প্রযোজ্য নয়         |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt` আর `Gt` metadata টাইপও
ব্যবহার করা যায়।

অনুমোদিত তারিখের মান আরও সীমিত করতে Pydantic নিচের টাইপগুলোও দেয়:

* [`PastDate`][pydantic.types.PastDate]: যাচাইয়ের সময় ইনপুট অতীতের হতে হবে (যেমন জন্মতারিখ)।
* [`FutureDate`][pydantic.types.FutureDate]: যাচাইয়ের সময় ইনপুট ভবিষ্যতের হতে হবে (যেমন অ্যাপয়েন্টমেন্ট)।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`date`][datetime.date] instance গ্রহণ হয়। JSON মোডে শুধু
[RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) ফরম্যাট মানা স্ট্রিং (*শুধু* date) বা unix timestamp গ্রহণ হয়।

<h4>উদাহরণ</h4>

```python
from datetime import date

from pydantic import BaseModel


class Birthday(BaseModel):
    d: date


my_birthday = Birthday(d=1679616000.0)

print(my_birthday.model_dump())
#> {'d': datetime.date(2023, 3, 24)}
print(my_birthday.model_dump_json())
#> {"d":"2023-03-24"}
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#datetimetime}{% endraw %}

### সময় (Time) { #time }

Standard library টাইপ: [`datetime.time`][]।

<h4>যাচাই</h4>

* [`time`][datetime.time] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) সময় ফরম্যাট অনুযায়ী যাচাই হয়।
* পূর্ণসংখ্যা আর float (বা এমন সংখ্যায় রূপান্তরযোগ্য মান) সেকেন্ড হিসেবে যাচাই হয়। মান 86 399-এর বেশি হওয়া উচিত নয় (একদিনের শেষ সেকেন্ড)।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`time`][datetime.time] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

/// note | মনে রাখুন

[IANA time zone database](https://www.iana.org/time-zones)-এর নামযুক্ত timezone (দেখুন [`zoneinfo`][] মডিউল) time অবজেক্টের সাথে
সিরিয়ালাইজ *হয় না*। এটি [`time.isoformat()`][datetime.time.isoformat] মেথডের সাথে সামঞ্জস্যপূর্ণ।

///

<h4>শর্ত</h4>

Time নিচের শর্তগুলো সমর্থন করে (শর্তের মান একটি [`time`][datetime.time] instance-এ রূপান্তরযোগ্য হতে হবে):

| শর্ত | বর্ণনা                                          | JSON Schema |
| ---------- | ---------------------------------------------------- | ----------- |
| `le`       | মান এই সময়ের চেয়ে ছোট বা সমান হতে হবে    | প্রযোজ্য নয়         |
| `ge`       | মান এই সময়ের চেয়ে বড় বা সমান হতে হবে | প্রযোজ্য নয়         |
| `lt`       | মান এই সময়ের চেয়ে কঠোরভাবে ছোট হতে হবে       | প্রযোজ্য নয়         |
| `gt`       | মান এই সময়ের চেয়ে কঠোরভাবে বড় হতে হবে    | প্রযোজ্য নয়         |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt` আর `Gt` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`time`][datetime.time] instance গ্রহণ হয়। JSON মোডে শুধু
[RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) ফরম্যাট মানা স্ট্রিং গ্রহণ হয়।

<h4>উদাহরণ</h4>

```python
from datetime import time

from pydantic import BaseModel


class Meeting(BaseModel):
    t: time


m = Meeting(t=time(4, 8, 16))

print(m.model_dump())
#> {'t': datetime.time(4, 8, 16)}
print(m.model_dump_json())
#> {"t":"04:08:16"}
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#datetimetimedelta}{% endraw %}

### সময়কাল (Timedelta) { #timedeltas }

Standard library টাইপ: [`datetime.timedelta`][]।

<h4>যাচাই</h4>

* [`timedelta`][datetime.timedelta] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) সময় ফরম্যাট অনুযায়ী যাচাই হয়।
* পূর্ণসংখ্যা আর float (বা এমন সংখ্যায় রূপান্তরযোগ্য মান) সেকেন্ড হিসেবে যাচাই হয়।

<h4>শর্ত</h4>

Timedelta নিচের শর্তগুলো সমর্থন করে (শর্তের মান একটি [`timedelta`][datetime.timedelta] instance-এ রূপান্তরযোগ্য হতে হবে):

| শর্ত | বর্ণনা                                               | JSON Schema |
| ---------- | --------------------------------------------------------- | ----------- |
| `le`       | মান এই timedelta-র চেয়ে ছোট বা সমান হতে হবে    | প্রযোজ্য নয়         |
| `ge`       | মান এই timedelta-র চেয়ে বড় বা সমান হতে হবে | প্রযোজ্য নয়         |
| `lt`       | মান এই timedelta-র চেয়ে কঠোরভাবে ছোট হতে হবে       | প্রযোজ্য নয়         |
| `gt`       | মান এই timedelta-র চেয়ে কঠোরভাবে বড় হতে হবে    | প্রযোজ্য নয়         |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `Le`, `Ge`, `Lt` আর `Gt` metadata টাইপও
ব্যবহার করা যায়।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), [`timedelta`][datetime.timedelta] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয় (যেমন `'PT1H30M'` = দেড় ঘণ্টা)।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`timedelta`][datetime.timedelta] instance গ্রহণ হয়। JSON মোডে শুধু
[RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) ফরম্যাট মানা স্ট্রিং গ্রহণ হয়।

<h4>উদাহরণ</h4>

```python
from datetime import timedelta

from pydantic import BaseModel


class Model(BaseModel):
    td: timedelta


m = Model(td='P3DT12H30M5S')

print(m.model_dump())
#> {'td': datetime.timedelta(days=3, seconds=45005)}
print(m.model_dump_json())
#> {"td":"P3DT12H30M5S"}
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#enum}{% endraw %}

## Enum { #enums }

Standard library টাইপ: [`enum.Enum`][]।

<h3>যাচাই</h3>

* সরাসরি [`enum.Enum`][] টাইপ ব্যবহার করলে, যেকোনো [`enum.Enum`][] instance যেমন আছে তেমন যাচাই হয়।
* একটি [`enum.Enum`][] subclass টাইপ হিসেবে ব্যবহার করলে, যেকোনো enum সদস্য বা enum সদস্যদের [মানের][enum.Enum.value]
  সাথে মেলে এমন মান যেমন আছে তেমন যাচাই হয়।

<h3>সিরিয়ালাইজেশন</h3>

[Python মোডে](../concepts/serialization.md#python-mode), enum instance যেমন আছে তেমন সিরিয়ালাইজ হয়।
যাচাইয়ের সময় enum-এর [মান][enum.Enum.value] ব্যবহার করতে (যাতে সিরিয়ালাইজেশনেও তা-ই ব্যবহার হয়)
[`use_enum_values`][pydantic.ConfigDict.use_enum_values] কনফিগারেশন মান সেট করা যায়।

[JSON মোডে](../concepts/serialization.md#json-mode), enum instance তাদের
[মান][enum.Enum.value] দিয়ে সিরিয়ালাইজ হয়।

<h3>উদাহরণ</h3>

```python
from enum import Enum, IntEnum

from pydantic import BaseModel, ValidationError


class FruitEnum(str, Enum):
    PEAR = 'pear'
    BANANA = 'banana'


class ToolEnum(IntEnum):
    SPANNER = 1
    WRENCH = 2


class CookingModel(BaseModel):
    fruit: FruitEnum = FruitEnum.PEAR
    tool: ToolEnum = ToolEnum.SPANNER


print(CookingModel())
#> fruit=<FruitEnum.PEAR: 'pear'> tool=<ToolEnum.SPANNER: 1>
print(CookingModel(tool=2, fruit='banana'))
#> fruit=<FruitEnum.BANANA: 'banana'> tool=<ToolEnum.WRENCH: 2>
try:
    CookingModel(fruit='other')
except ValidationError as e:
    print(e)
    """
    1 validation error for CookingModel
    fruit
      Input should be 'pear' or 'banana' [type=enum, input_value='other', input_type=str]
    """
```

## None টাইপ { #none-types }

সমর্থিত টাইপ: [`None`][], [`NoneType`][types.NoneType] বা `Literal[None]` (এগুলো [সমতুল্য](https://typing.readthedocs.io/en/latest/spec/special-types.html#none))।

মান হিসেবে শুধু `None` অনুমোদন করে।

## Generic collection টাইপ { #generic-collection-types }

Pydantic অনেক ধরনের generic collection টাইপ সমর্থন করে, built-in (যেমন [`list`][]) আর
[`collections.abc`][] মডিউলের abstract base class (যেমন [`Sequence`][collections.abc.Sequence]) দুটোই।

বেশিরভাগ ক্ষেত্রে abstract টাইপের চেয়ে built-in টাইপ ব্যবহারের পরামর্শ দেওয়া হয়। [ডেটা রূপান্তরের](../concepts/models.md#data-conversion) কারণে,
[`list`][] বা [`tuple`][] ব্যবহার করলেও অন্য বেশিরভাগ iterable ইনপুট হিসেবে চলবে, আরও ভালো পারফরম্যান্সসহ।

/// note | collection টাইপে কঠোরতা

collection টাইপে [strict mode](../concepts/strict_mode.md) প্রয়োগ করলে, কঠোরতা ভেতরের টাইপে প্রযোজ্য
*হয় না*। ভবিষ্যতে এটি বদলাতে পারে, দেখুন [এই issue](https://github.com/pydantic/pydantic/issues/12319)।

///

### তালিকা (Lists) { #lists }

Built-in টাইপ: [`list`][] (পুরনো alias: [`typing.List`][])।

<h4>যাচাই</h4>

* [`list`][], [`tuple`][], [`set`][] আর [`frozenset`][] instance, অথবা এমন যেকোনো iterable যা
  [string][str], [bytes][], [bytearray][], [dict][] বা [mapping][] *নয়*, অনুমোদন করে। একটি [`list`][] instance তৈরি করে।
* একটি generic প্যারামিটার দিলে, তালিকার সব আইটেমে উপযুক্ত যাচাই প্রয়োগ হয়।

<h4>শর্ত</h4>

তালিকা নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                 | JSON Schema                                                                                    |
|--------------|---------------------------------------------|------------------------------------------------------------------------------------------------|
| `min_length` | তালিকায় অন্তত এতগুলো আইটেম থাকতে হবে | [`minItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |
| `max_length` | তালিকায় সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`list`][] instance বৈধ। strict mode তালিকার আইটেমে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপে প্রয়োগ করতে হবে (যেমন `list[StrictInt]`)।

<h4>উদাহরণ</h4>

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    simple_list: list[object] | None = None
    list_of_ints: list[int] | None = Field(default=None, strict=True)


print(Model(simple_list=('1', '2', '3')).simple_list)
#> ['1', '2', '3']
print(Model(list_of_ints=['1', 2, 3]).list_of_ints)
#> [1, 2, 3]
```

### Tuple { #tuples }

Built-in টাইপ: [`tuple`][] (পুরনো alias: [`typing.Tuple`][])।

/// note | মনে রাখুন

[খুলে দেওয়া tuple টাইপ](https://typing.python.org/en/latest/spec/generics.html#unpacking-tuple-types)
([PEP 646](https://peps.python.org/pep-0646/) অনুযায়ী) এখনো সমর্থিত *নয়*, আর
[এই issue](https://github.com/pydantic/pydantic/issues/5952)-এ অনুসরণ করা যায়।

///

<h4>যাচাই</h4>

* [`tuple`][], [`list`][], [`set`][] আর [`frozenset`][] instance, অথবা এমন যেকোনো iterable যা
  [string][str], [bytes][], [bytearray][], [dict][] বা [mapping][] *নয়*, অনুমোদন করে। একটি [`tuple`][] instance তৈরি করে।
* [উপাদানের টাইপ](https://typing.python.org/en/latest/spec/tuples.html#tuple-type-form) দেওয়া থাকলে
  tuple-এর আইটেমে উপযুক্ত যাচাই প্রয়োগ হয় (যেমন `tuple[int, str]` মানে প্রথমটি সংখ্যা, দ্বিতীয়টি লেখা; `tuple[int, ...]` মানে যত খুশি সংখ্যা)।

<h4>শর্ত</h4>

তালিকা নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                  | JSON Schema                                                                                    |
|--------------|----------------------------------------------|------------------------------------------------------------------------------------------------|
| `min_length` | tuple-এ অন্তত এতগুলো আইটেম থাকতে হবে | [`minItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |
| `max_length` | tuple-এ সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

এছাড়া, tuple-এর গঠন অনুযায়ী [`prefixItems`](https://json-schema.org/understanding-json-schema/reference/array#tupleValidation) JSON Schema keyword
ব্যবহার হতে পারে।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`tuple`][] instance বৈধ। strict mode tuple-এর আইটেমে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from pydantic import BaseModel


class Model(BaseModel):
    simple_tuple: tuple | None = None
    tuple_of_different_types: tuple[int, float, bool] | None = None


print(Model(simple_tuple=[1, 2, 3, 4]).simple_tuple)
#> (1, 2, 3, 4)
print(Model(tuple_of_different_types=[3, 2, 1]).tuple_of_different_types)
#> (3, 2.0, True)
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingnamedtuple}{% endraw %}

### Named tuple { #named-tuples }

Standard library টাইপ: [`typing.NamedTuple`][] (আর [`collections.namedtuple()`][collections.namedtuple] factory ফাংশন দিয়ে তৈরি টাইপ
– প্রতিটি ফিল্ডের টাইপ অন্তর্নিহিতভাবে [`Any`][typing.Any])।

<h4>যাচাই</h4>

* [`tuple`][] আর [`list`][] instance অনুমোদন করে। প্রতিটি আইটেম ফিল্ডের সংজ্ঞা অনুযায়ী যাচাই করে।
* [`dict`][] instance অনুমোদন করে। key-গুলো named tuple-এর ফিল্ডের নামের সাথে মিলতে হবে, আর মানগুলো ফিল্ডের সংজ্ঞা অনুযায়ী যাচাই হয়।
* named tuple ক্লাসের instance অনুমোদন করে (ফিল্ডগুলো আবার যাচাই হয়)।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), named tuple tuple হিসেবে সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো array হিসেবে সিরিয়ালাইজ হয়।

<h4>উদাহরণ</h4>

```python
from typing import NamedTuple

from pydantic import BaseModel


class Point(NamedTuple):
    x: int
    y: int


class Model(BaseModel):
    p: Point


model = Model(p=('1', 2))

print(model.model_dump())
#> {'p': (1, 2)}
```

### সেট (Sets) { #sets }

টাইপ: [`set`][] (বা [`collections.abc.MutableSet`][]) আর [`frozenset`][] (বা [`collections.abc.Set`][])
(পুরনো alias: [`typing.Set`][] আর [`typing.FrozenSet`][])।

<h4>যাচাই</h4>

* [`set`][], [`frozenset`][], [`tuple`][] আর [`list`][] instance, অথবা এমন যেকোনো iterable যা
  [string][str], [bytes][], [bytearray][], [dict][] বা [mapping][] *নয়*, অনুমোদন করে। একটি [`set`][] বা [`frozenset`][] instance তৈরি করে (ফলে পুনরাবৃত্ত মান বাদ পড়ে)।
* একটি generic প্যারামিটার দিলে, set/frozenset-এর সব আইটেমে উপযুক্ত যাচাই প্রয়োগ হয়।

<h4>শর্ত</h4>

সেট নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                | JSON Schema                                                                                    |
|--------------|--------------------------------------------|------------------------------------------------------------------------------------------------|
| `min_length` | সেটে অন্তত এতগুলো আইটেম থাকতে হবে | [`minItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |
| `max_length` | সেটে সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`set`][]/[`frozenset`][] instance বৈধ। strict mode সেটের আইটেমে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপে প্রয়োগ করতে হবে।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), সেট যেমন আছে তেমন সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো array হিসেবে সিরিয়ালাইজ হয়।

<h4>উদাহরণ</h4>

```python
from pydantic import BaseModel


class Model(BaseModel):
    simple_set: set | None = None
    set_of_ints: frozenset[int] | None = None


print(Model(simple_set=['1', '2', '3']).simple_set)
#> {'1', '2', '3'}
print(Model(set_of_ints=['1', '2', '3']).set_of_ints)
#> frozenset({1, 2, 3})
```

<h4>JSON Schema</h4>

[`collections.abc.Set`][] instance-এর ডিফল্ট মানগুলো সাজাতে (sort) Pydantic যথাসাধ্য চেষ্টা করে।

### Deque { #deque }

Standard library টাইপ: [`collections.deque`][] (পুরনো alias: [`typing.Deque`][])।

<h4>যাচাই</h4>

যেকোনো iterable (স্ট্রিং, bytes আর mapping ছাড়া) গ্রহণ হয় আর একটি [`deque`][collections.deque]-এ রূপান্তরিত হয়,
প্রতিটি আইটেম প্যারামিটার টাইপের বিপরীতে যাচাই হয়। ইনপুট আগে থেকেই একটি `deque` instance হলে, এর
[`maxlen`][collections.deque.maxlen] অ্যাট্রিবিউট অক্ষুণ্ণ থাকে।

<h4>শর্ত</h4>

Deque নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                  | JSON Schema                                                                                    |
|--------------|----------------------------------------------|------------------------------------------------------------------------------------------------|
| `min_length` | deque-এ অন্তত এতগুলো আইটেম থাকতে হবে | [`minItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |
| `max_length` | deque-এ সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`deque`][collections.deque] instance বৈধ। strict mode deque-এর আইটেমে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপে প্রয়োগ করতে হবে।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), deque যেমন আছে তেমন সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো array হিসেবে সিরিয়ালাইজ হয়।

<h4>উদাহরণ</h4>

```python
from collections import deque

from pydantic import BaseModel


class Model(BaseModel):
    deque: deque[int]


print(Model(deque=[1, 2, 3]).deque)
#> deque([1, 2, 3])
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingsequence}{% endraw %}

### Sequence { #sequences }

Standard library টাইপ: [`collections.abc.Sequence`][] (পুরনো alias: [`typing.Sequence`][])।

বেশিরভাগ ক্ষেত্রে আপনি built-in টাইপ (যেমন [list](#lists) বা [tuple](#tuples)) ব্যবহার করতে চাইবেন, কারণ [টাইপ রূপান্তর](../concepts/models.md#data-conversion)
প্রযোজ্য হবে। সিরিয়ালাইজেশনের সময় ইনপুটের টাইপ অক্ষুণ্ণ রাখতে চাইলে [`Sequence`][collections.abc.Sequence] টাইপ ব্যবহার করা যায়।

<h4>যাচাই</h4>

যেকোনো [`collections.abc.Sequence`][] instance (স্ট্রিং আর bytes ছাড়া) গ্রহণ হয়। এটি [`list()`][list]
constructor দিয়ে একটি তালিকায় রূপান্তরিত হয়, তারপর আবার মূল ইনপুটের টাইপে ফেরত রূপান্তরিত হয়।

/// warning | স্ট্রিংকে sequence ধরা হয় না

কারিগরিভাবে স্ট্রিং বৈধ sequence instance হলেও, প্রায়ই সেটি উদ্দেশ্য থাকে না, আর এটি বাগের একটি প্রচলিত উৎস।

ফলে, Pydantic [`Sequence`][collections.abc.Sequence] টাইপের জন্য স্ট্রিং আর bytes গ্রহণ করবে *না* (নিচের উদাহরণ দেখুন)।

///

<h4>শর্ত</h4>

Sequence নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                     | JSON Schema                                                                                    |
|--------------|-------------------------------------------------|------------------------------------------------------------------------------------------------|
| `min_length` | sequence-এ অন্তত এতগুলো আইটেম থাকতে হবে | [`minItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |
| `max_length` | sequence-এ সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxItems`](https://json-schema.org/understanding-json-schema/reference/array#length) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>সিরিয়ালাইজেশন</h4>

[Python মোডে](../concepts/serialization.md#python-mode), sequence যেমন আছে তেমন সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো array হিসেবে সিরিয়ালাইজ হয়।

<h4>উদাহরণ</h4>

```python
from collections.abc import Sequence

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    sequence_of_strs: Sequence[str]


print(Model(sequence_of_strs=['a', 'bc']).sequence_of_strs)
#> ['a', 'bc']
print(Model(sequence_of_strs=('a', 'bc')).sequence_of_strs)
#> ('a', 'bc')

try:
    Model(sequence_of_strs='abc')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    sequence_of_strs
      'str' instances are not allowed as a Sequence value [type=sequence_str, input_value='abc', input_type=str]
    """
```

### ডিকশনারি { #dictionaries }

Built-in টাইপ: [`dict`][]।

<h4>যাচাই</h4>

* [`dict`][] instance যেমন আছে তেমন গ্রহণ হয়।
* [mapping][mapping] instance গ্রহণ হয় আর একটি [`dict`][]-এ রূপান্তরিত হয়।
* key আর value-র generic প্যারামিটার দিলে (যেমন `dict[str, int]`), উপযুক্ত যাচাই প্রয়োগ হয়।

<h4>শর্ত</h4>

ডিকশনারি নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                       | JSON Schema                                                                                        |
|--------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `min_length` | ডিকশনারিতে অন্তত এতগুলো আইটেম থাকতে হবে | [`minProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |
| `max_length` | ডিকশনারিতে সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`dict`][] instance বৈধ। strict mode ডিকশনারির key আর value-তে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: dict[str, int]


m = Model(x={'foo': 1})
print(m.model_dump())
#> {'x': {'foo': 1}}

try:
    Model(x='test')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      Input should be a valid dictionary [type=dict_type, input_value='test', input_type=str]
    """
```

### Frozen ডিকশনারি { #frozen-dictionaries }

Built-in টাইপ: `frozendict`।

/// info | v2.14-এ যোগ হয়েছে
Python 3.15-এ নতুন আসা `frozendict` টাইপ Pydantic সমর্থন করে।
///

<h4>যাচাই</h4>

* `frozendict` instance যেমন আছে তেমন গ্রহণ হয়।
* [`dict`][] আর [mapping][mapping] instance গ্রহণ হয় আর একটি `frozendict`-এ রূপান্তরিত হয়।
* key আর value-র generic প্যারামিটার দিলে, উপযুক্ত যাচাই প্রয়োগ হয়।

<h4>শর্ত</h4>

[ডিকশনারির](#dictionaries) মতোই, frozen ডিকশনারি নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                       | JSON Schema                                                                                        |
|--------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `min_length` | ডিকশনারিতে অন্তত এতগুলো আইটেম থাকতে হবে | [`minProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |
| `max_length` | ডিকশনারিতে সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু `frozendict` instance বৈধ। strict mode frozen ডিকশনারির key আর value-তে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: frozendict[str, int]


m = Model(x={'foo': 1})
print(m.model_dump())
#> {'x': frozendict({'foo': 1})}

try:
    Model(x='test')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      Input should be a valid frozendict [type=frozen_dict_type, input_value='test', input_type=str]
    """
```

### ক্রমযুক্ত ডিকশনারি (Ordered dictionaries) { #ordered-dictionaries }

Standard library টাইপ: [`collections.OrderedDict`][] (পুরনো alias: [`typing.OrderedDict`][])।

<h4>যাচাই</h4>

* [`OrderedDict`][collections.OrderedDict] instance যেমন আছে তেমন গ্রহণ হয়।
* [`dict`][] আর [mapping][mapping] instance গ্রহণ হয় আর একটি [`OrderedDict`][collections.OrderedDict]-এ রূপান্তরিত হয়।
* key আর value-র generic প্যারামিটার দিলে, উপযুক্ত যাচাই প্রয়োগ হয়।

<h4>শর্ত</h4>

[ডিকশনারির](#dictionaries) মতোই, ক্রমযুক্ত ডিকশনারি নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                       | JSON Schema                                                                                        |
|--------------|---------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `min_length` | ডিকশনারিতে অন্তত এতগুলো আইটেম থাকতে হবে | [`minProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |
| `max_length` | ডিকশনারিতে সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`OrderedDict`][collections.OrderedDict] instance বৈধ। strict mode ক্রমযুক্ত ডিকশনারির key আর value-তে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from collections import OrderedDict

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: OrderedDict[str, int]


m = Model(x={'foo': 1})
print(m.model_dump())
#> {'x': OrderedDict({'foo': 1})}

try:
    Model(x='test')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      Input should be a valid OrderedDict [type=ordered_dict_type, input_value='test', input_type=str]
    """
```

### Counter { #counters }

Standard library টাইপ: [`collections.Counter`][] (পুরনো alias: [`typing.Counter`][])।

<h4>যাচাই</h4>

* [`Counter`][collections.Counter] instance যেমন আছে তেমন গ্রহণ হয়।
* [`dict`][] আর [mapping][mapping] instance গ্রহণ হয় আর একটি [`Counter`][collections.Counter]-এ রূপান্তরিত হয়।
* key-র generic প্যারামিটার দিলে, উপযুক্ত যাচাই প্রয়োগ হয়। value সবসময় [পূর্ণসংখ্যা](#integers) হিসেবে যাচাই হয়।

<h4>শর্ত</h4>

[ডিকশনারির](#dictionaries) মতোই, counter নিচের শর্তগুলো সমর্থন করে:

| শর্ত   | বর্ণনা                                    | JSON Schema                                                                                        |
|--------------|------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `min_length` | counter-এ অন্তত এতগুলো আইটেম থাকতে হবে | [`minProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |
| `max_length` | counter-এ সর্বোচ্চ এতগুলো আইটেম থাকতে পারবে  | [`maxProperties`](https://json-schema.org/understanding-json-schema/reference/object#size) keyword |

এই শর্তগুলো [`Field()`][pydantic.Field] ফাংশন দিয়ে দেওয়া যায়।
[`annotated-types`](https://github.com/annotated-types/annotated-types) লাইব্রেরির `MinLen` আর `MaxLen` metadata টাইপও
ব্যবহার করা যায়।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`Counter`][collections.Counter] instance বৈধ। strict mode counter-এর key আর value-তে প্রযোজ্য *হয় না*।
এটি কাজ করাতে strict শর্তটি প্যারামিটার টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from collections import Counter

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Counter[str]


m = Model(x={'foo': '1'})
print(m.model_dump())
#> {'x': Counter({'foo': 1})}

try:
    Model(x='test')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      Input should be a valid Counter [type=counter_type, input_value='test', input_type=str]
    """
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typeddict}{% endraw %}

### Typed ডিকশনারি { #typed-dictionaries }

Standard library টাইপ: [`typing.TypedDict`][] (আরও দেখুন: [typing specification](https://typing.python.org/en/latest/spec/typeddict.html))।

/// note | মনে রাখুন

চলার সময়ের সীমাবদ্ধতার কারণে, Python 3.12 বা তার নিচে Pydantic [`typing_extensions`][]-এর
[`TypedDict`][typing_extensions.TypedDict] টাইপ ব্যবহার দাবি করবে।

///

[`TypedDict`][typing.TypedDict] এমন একটি ডিকশনারি টাইপ ঘোষণা করে যার প্রতিটি instance-এ নির্দিষ্ট key-এর একটি সেট থাকবে বলে আশা করা হয়,
 আর প্রতিটি key একটি নির্দিষ্ট টাইপের মানের সাথে যুক্ত।

এই টাইপ [কনফিগারেশন সমর্থন করে](../concepts/config.md#configuration-on-other-supported-types)।

<h4>কঠোরতা</h4>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`dict`][] instance বৈধ (lax মোডে mapping-ও চলে, এখানে নয়)।
strict mode typed ডিকশনারির value-তে প্রযোজ্য *হয় না*। এটি কাজ করাতে strict শর্তটি value-র টাইপগুলোতে প্রয়োগ করতে হবে।

<h4>উদাহরণ</h4>

```python
from typing_extensions import TypedDict

from pydantic import TypeAdapter, ValidationError


class User(TypedDict):
    name: str
    id: int


ta = TypeAdapter(User)

print(ta.validate_python({'name': 'foo', 'id': 1}))
#> {'name': 'foo', 'id': 1}

try:
    ta.validate_python({'name': 'foo'})
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    id
      Field required [type=missing, input_value={'name': 'foo'}, input_type=dict]
    """
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingiterable}{% endraw %}

### Iterable { #iterables }

Standard library টাইপ: [`collections.abc.Iterable`][] (পুরনো alias: [`typing.Iterable`][])।

<h4>যাচাই</h4>

Iterable অলসভাবে (lazily) যাচাই হয়, আর একটি ভেতরের ডেটা কাঠামোয় মোড়ানো থাকে যার ওপর লুপ চালানো যায়
(আর লুপ চলার সময় আইটেমের টাইপ যাচাই হয়)। অর্থাৎ তালিকার মতো একটি নির্দিষ্ট
container দিলেও, যাচাই করা টাইপ [`list`][] টাইপের *হবে না*। তবে Pydantic
নিশ্চিত করবে যে ইনপুট মানটি iterable, এর থেকে একটি [iterator][] নিয়ে (মানটিতে
[`iter()`][iter] ডেকে)।

বদলে নির্দিষ্ট collection টাইপ (যেমন [তালিকা](#lists)) ব্যবহারের পরামর্শ দেওয়া হয়, যদি না
আপনি একটি অসীম iterator ব্যবহার করছেন (সেক্ষেত্রে ইনপুট সাথে সাথে যাচাই করলে অসীম লুপ
হতো)।

<h4>উদাহরণ</h4>

```python
from collections.abc import Iterable

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    f: Iterable[str]


m = Model(f=[1, 2])  # Validates fine

try:
    next(m.f)
except ValidationError as e:
    print(e)
    """
    1 validation error for ValidatorIterator
    0
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
    """
```

## Callable { #callable }

Standard library টাইপ: [`collections.abc.Callable`][] (পুরনো alias: [`typing.Callable`][])।

<h3>যাচাই</h3>

Pydantic শুধু যাচাই করে যে ইনপুটটি একটি [callable][] ([`callable()`](https://docs.python.org/3/library/functions.html#callable) ফাংশন দিয়ে)।
এটি প্যারামিটারের সংখ্যা বা তাদের টাইপ, বা ফেরত মানের টাইপ যাচাই করে *না*।

```python
from collections.abc import Callable

from pydantic import BaseModel


class Foo(BaseModel):
    callback: Callable[[int], int]


m = Foo(callback=lambda x: x)
print(m)
#> callback=<function <lambda> at 0x0123456789ab>
```

<h3>সিরিয়ালাইজেশন</h3>

callable যেমন আছে তেমন সিরিয়ালাইজ হয়। callable [JSON মোডে](../concepts/serialization.md#json-mode) সিরিয়ালাইজ করা যায় না
(একটি [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] ওঠে)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#ip-address-types}{% endraw %}

## IP ঠিকানা { #ip-addresses }

Standard library টাইপ:

* [`ipaddress.IPv4Address`][]
* [`ipaddress.IPv4Interface`][]
* [`ipaddress.IPv4Network`][]
* [`ipaddress.IPv6Address`][]
* [`ipaddress.IPv6Interface`][]
* [`ipaddress.IPv6Network`][]

আরও দেখুন: [`IPvAnyAddress`][pydantic.networks.IPvAnyAddress], [`IPvAnyInterface`][pydantic.networks.IPvAnyInterface]
আর [`IPvAnyNetwork`][pydantic.networks.IPvAnyNetwork] Pydantic টাইপ।

<h3>যাচাই</h3>

* instance যেমন আছে তেমন যাচাই হয়।
* অন্য ইনপুট মান সংশ্লিষ্ট ঠিকানা টাইপের constructor-এ পাঠানো হয়।

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু ঠিকানা টাইপগুলো গ্রহণ হয়।
JSON মোডে, strict mode-এ শুধু স্ট্রিং গ্রহণ হয়, আর lax মোডে পূর্ণসংখ্যাও গ্রহণ হয়
(যেমন `3232235521` যাচাই হয় `IPv4Address('192.168.0.1')` হিসেবে)।

<h3>সিরিয়ালাইজেশন</h3>

[Python মোডে](../concepts/serialization.md#python-mode), IP ঠিকানা যেমন আছে তেমন সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

## UUID { #uuid }

Standard library টাইপ: [`uuid.UUID`][]।

<h3>যাচাই</h3>

* [`UUID`][uuid.UUID] instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং আর bytes UUID হিসেবে যাচাই হয়, আর একটি [`UUID`][uuid.UUID] instance-এ রূপান্তরিত হয়।

<h3>শর্ত</h3>

[`UUID`][uuid.UUID] টাইপ একটি `version` শর্ত সমর্থন করে। [`UuidVersion`][pydantic.types.UuidVersion] metadata টাইপ ব্যবহার করা যায়।

Pydantic সুবিধাজনক alias হিসেবে নিচের টাইপগুলোও দেয়: [`UUID1`][pydantic.types.UUID1], [`UUID3`][pydantic.types.UUID3],
[`UUID4`][pydantic.types.UUID4], [`UUID5`][pydantic.types.UUID5], [`UUID6`][pydantic.types.UUID6], [`UUID7`][pydantic.types.UUID7],
[`UUID8`][pydantic.types.UUID8]।

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু [`UUID`][uuid.UUID] instance গ্রহণ হয়।
JSON মোডে strict mode-এর কোনো প্রভাব নেই।

<h3>সিরিয়ালাইজেশন</h3>

[Python মোডে](../concepts/serialization.md#python-mode), UUID যেমন আছে তেমন সিরিয়ালাইজ হয়। [JSON মোডে](../concepts/serialization.md#json-mode),
এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

<h3>উদাহরণ</h3>

```python
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic.types import UUID7, UuidVersion


class Model(BaseModel):
    u1: UUID7
    u2: Annotated[UUID, UuidVersion(4)]


print(
    Model(
        u1='01999b2c-8353-749b-8dac-859307fae22b',
        u2=UUID('125725f3-e1b4-44e3-90c3-1a20eab12da5'),
    )
)
"""
u1=UUID('01999b2c-8353-749b-8dac-859307fae22b') u2=UUID('125725f3-e1b4-44e3-90c3-1a20eab12da5')
"""
```

## Type { #type }

Built-in টাইপ: [`type`][] (পুরনো alias: [`typing.Type`][])।

<h3>যাচাই</h3>

টাইপ আর্গুমেন্টের subclass এমন যেকোনো টাইপ (ক্লাস) অনুমোদন করে। যেমন, `type[str]` দিলে [`str`][]
ক্লাস বা যেকোনো [`str`][] subclass ইনপুট হিসেবে চলে। কোনো টাইপ আর্গুমেন্ট না দিলে (অর্থাৎ annotation হিসেবে শুধু `type`),
যেকোনো ক্লাস অনুমোদিত।

<h3>সিরিয়ালাইজেশন</h3>

টাইপ যেমন আছে তেমন সিরিয়ালাইজ হয়। টাইপ [JSON মোডে](../concepts/serialization.md#json-mode) সিরিয়ালাইজ করা যায় না
(একটি [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] ওঠে)।

```python
from pydantic import BaseModel, ValidationError


class Foo:
    pass


class Bar(Foo):
    pass


class Other:
    pass


class SimpleModel(BaseModel):
    just_subclasses: type[Foo]


SimpleModel(just_subclasses=Foo)
SimpleModel(just_subclasses=Bar)
try:
    SimpleModel(just_subclasses=Other)
except ValidationError as e:
    print(e)
    """
    1 validation error for SimpleModel
    just_subclasses
      Input should be a subclass of Foo [type=is_subclass_of, input_value=<class '__main__.Other'>, input_type=type]
    """
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingliteral}{% endraw %}

## Literal { #literals }

Typing কাঠামো: [`typing.Literal`][] (আরও দেখুন: [typing specification](https://typing.python.org/en/latest/spec/literal.html#literal))।

শুধু নির্দিষ্ট কিছু মান অনুমোদন করতে Literal ব্যবহার করা যায় (যেমন `Literal['pending', 'paid', 'cancelled']`)।

মনে রাখুন, literal মান যাচাইয়ের সময় Pydantic [strict mode](../concepts/strict_mode.md)-এর আচরণ প্রয়োগ করে (দেখুন [এই issue](https://github.com/pydantic/pydantic/issues/9991)); অর্থাৎ `Literal[1]`-এ `'1'` স্ট্রিং চলবে না।

<h3>উদাহরণ</h3>

```python
from typing import Literal

from pydantic import BaseModel, ValidationError


class Pie(BaseModel):
    flavor: Literal['apple', 'pumpkin']
    quantity: Literal[1, 2] = 1


Pie(flavor='apple')
Pie(flavor='pumpkin')
try:
    Pie(flavor='cherry')
except ValidationError as e:
    print(str(e))
    """
    1 validation error for Pie
    flavor
      Input should be 'apple' or 'pumpkin' [type=literal_error, input_value='cherry', input_type=str]
    """

try:
    Pie(flavor='apple', quantity='1')
except ValidationError as e:
    print(str(e))
    """
    1 validation error for Pie
    quantity
      Input should be 1 or 2 [type=literal_error, input_value='1', input_type=str]
    """
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingany}{% endraw %}

## Any { #any }

টাইপ: [`typing.Any`][] বা [`object`][]।

`None`-সহ যেকোনো মান অনুমোদন করে, কোনো যাচাই বা রূপান্তর ছাড়া।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typinghashable}{% endraw %}

## Hashable { #hashables }

Standard library টাইপ: [`collections.abc.Hashable`][] (পুরনো alias: [`typing.Hashable`][])।

<h3>যাচাই</h3>

hash করা যায় এমন যেকোনো মান (`isinstance(value, Hashable)` দিয়ে)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#typingpattern}{% endraw %}

## Regex প্যাটার্ন { #regex-patterns }

Standard library টাইপ: [`re.Pattern`][] (পুরনো alias: [`typing.Pattern`][])।

<h3>যাচাই</h3>

* [`Pattern`][re.Pattern] instance-এর জন্য, পরীক্ষা করে যে [`pattern`][re.Pattern.pattern] অ্যাট্রিবিউটটি
  সঠিক টাইপের ([`Pattern`][re.Pattern] টাইপ প্যারামিটার অনুযায়ী [`str`][] বা [`bytes`][])।
* টাইপ প্যারামিটার [`str`][] বা [`bytes`][] হলে, [`str`][] (বা যথাক্রমে [`bytes`][]) টাইপের ইনপুট মান
  [`re.compile()`][re.compile] দিয়ে compile করার চেষ্টা করা হয়।

<h3>সিরিয়ালাইজেশন</h3>

[Python মোডে](../concepts/serialization.md#python-mode), [`Pattern`][re.Pattern] instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয় (মনে রাখুন, flag
এখন অক্ষুণ্ণ থাকে *না*)।

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
{% raw %}[](){#pathlibpath}{% endraw %}

## Path { #paths }

Standard library টাইপ:

* [`pathlib.Path`][]।
* [`pathlib.PurePath`][]।
* [`pathlib.PosixPath`][]।
* [`pathlib.WindowsPath`][]।
* [`pathlib.PurePosixPath`][]।
* [`pathlib.PureWindowsPath`][]।
* [`os.PathLike`][] (অবশ্যই [`str`][], [`bytes`][] বা [`Any`][typing.Any] দিয়ে প্যারামিটার দিতে হবে)।

<h3>যাচাই</h3>

* Path instance যেমন আছে তেমন যাচাই হয়।
* স্ট্রিং গ্রহণ হয় আর টাইপের constructor-এ পাঠানো হয়। [`os.PathLike`][] ব্যবহার করলে,
  [`bytes`][] টাইপ দিয়ে প্যারামিটার দেওয়া থাকলে bytes গ্রহণ হয়।

<h3>কঠোরতা</h3>

[strict mode](../concepts/strict_mode.md)-এ শুধু Path instance গ্রহণ হয়।
JSON মোডে strict mode-এর কোনো প্রভাব নেই।

<h3>সিরিয়ালাইজেশন</h3>

[Python মোডে](../concepts/serialization.md#python-mode), Path instance
যেমন আছে তেমন সিরিয়ালাইজ হয়।

[JSON মোডে](../concepts/serialization.md#json-mode), এগুলো স্ট্রিং হিসেবে সিরিয়ালাইজ হয়।

/// tip | পথ আসলেই আছে কিনা

`Path` শুধু লেখাটিকে পথ বানায়, ফাইলটি আছে কিনা দেখে না। থাকা বাধ্যতামূলক করতে [`FilePath`][pydantic.types.FilePath] বা [`DirectoryPath`][pydantic.types.DirectoryPath] ব্যবহার করুন (দেখুন [Pydantic Types](types.md))।

///

/// check | সংক্ষেপে মনে রাখুন

* lax মোডে Pydantic যৌক্তিক রূপান্তর করে (`'1'` → `1`, `'2024-01-01'` → `date`, `tuple` → `list`); strict মোডে শুধু ঠিক টাইপ।
* collection-এ strict শুধু বাইরের টাইপে; ভেতরের আইটেমে চাইলে `list[StrictInt]` এর মতো লিখুন।
* JSON মোডে `Decimal`, `UUID`, `datetime`, `timedelta`, `Path`, IP সব স্ট্রিং হয়ে যায়; `set`, `tuple`, `deque` হয় array।
* `Sequence` স্ট্রিং গ্রহণ করে না; টাকার হিসাবে `Decimal`।

///
