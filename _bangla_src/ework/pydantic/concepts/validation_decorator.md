# Validation Decorator { #validation-decorator }

/// note | এই পেজে যা শিখবেন

* `@validate_call` দিয়ে যেকোনো সাধারণ ফাংশনের আর্গুমেন্ট স্বয়ংক্রিয়ভাবে যাচাই করা।
* টাইপ রূপান্তর, ফেরত মান যাচাই (`validate_return`), আর সব ধরনের প্যারামিটার (`*args`, `**kwargs`, keyword-only...)।
* `Field()` আর alias দিয়ে প্যারামিটারে শর্ত দেওয়া, async ফাংশন, নিজের কনফিগারেশন।
* সীমাবদ্ধতা আর পারফরম্যান্স।

///

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.validate_call_decorator.validate_call`][pydantic.validate_call_decorator.validate_call]<br>

///

[`validate_call()`][pydantic.validate_call] decorator দিয়ে একটি ফাংশনে পাঠানো আর্গুমেন্টগুলো, ফাংশন ডাকার আগেই,
ফাংশনের annotation অনুযায়ী পার্স আর যাচাই করা যায়।

ভেতরে ভেতরে এটি মডেল তৈরি আর initialisation-এর একই পদ্ধতি ব্যবহার করে
(বিস্তারিত জানতে দেখুন [Validators](validators.md)), তবে খুব অল্প বাড়তি কোড লিখে
আপনার কোডে যাচাই যোগ করার অত্যন্ত সহজ উপায় দেয়।

/// tip | উদাহরণ দিয়ে বুঝি

ফাংশন হলো একটি মেশিন, আর `@validate_call` হলো মেশিনের মুখে বসানো একটি ছাঁকনি। ভুল জিনিস (ভুল টাইপের আর্গুমেন্ট) ঢোকার আগেই আটকে যায়, আর "৪" লেখা কাগজ দিলে ছাঁকনি সেটিকে ৪ সংখ্যায় বদলে ভেতরে পাঠায়। ফাংশনের ভেতরে আর `isinstance()` দিয়ে বারবার পরীক্ষা লিখতে হয় না।

///

ব্যবহারের উদাহরণ:

⟦CODE1⟧

/// info | কোডটি সহজ ভাষায়

* `repeat('x', '4', ...)`: `count`-এ স্ট্রিং `'4'` দেওয়া হলেও যাচাই হয়ে `4` হলো।
* `repeat('hello', 'wrong')`: `'wrong'` সংখ্যা নয়, তাই ফাংশন চলার আগেই `ValidationError`। এররে `1` মানে দ্বিতীয় অবস্থানের (index 1) আর্গুমেন্ট।

///

## প্যারামিটারের টাইপ { #parameter-types }

প্যারামিটারের টাইপ ফাংশনের টাইপ annotation থেকে বোঝা হয়, annotation না থাকলে [`Any`][typing.Any] ধরা হয়। [types](types.md)-এ তালিকাভুক্ত সব টাইপ যাচাই করা যায়, Pydantic মডেল আর [নিজের বানানো টাইপসহ](types.md#custom-types)।
Pydantic-এর বাকি অংশের মতোই, আসল ফাংশনে পাঠানোর আগে decorator ডিফল্টভাবে টাইপ রূপান্তর (coerce) করে:

⟦CODE2⟧

1. `include_equal`-এর কোনো টাইপ annotation নেই বলে এটিকে [`Any`][typing.Any] ধরা হবে।
2. `d1` একটি স্ট্রিং হলেও এটি একটি [`date`][datetime.date] অবজেক্টে রূপান্তরিত হবে।

এমন টাইপ রূপান্তর অত্যন্ত কাজের হতে পারে, আবার বিভ্রান্তিকর বা অনাকাঙ্ক্ষিতও হতে পারে (দেখুন [মডেলের ডেটা রূপান্তর](models.md#data-conversion))। [নিজের কনফিগারেশন](#custom-configuration)
দিয়ে [Strict mode](strict_mode.md) চালু করা যায়।

/// note | ফেরত মান যাচাই

ডিফল্টভাবে ফাংশনের ফেরত মান যাচাই **হয় না**। যাচাই করতে decorator-এর `validate_return`
আর্গুমেন্ট `True` করুন।

///

```python
from pydantic import validate_call


@validate_call(validate_return=True)
def get_age(text: str) -> int:
    return text.strip()  # ফেরত মানও int হিসেবে যাচাই হবে


print(get_age(' 42 '))
#> 42
```

## ফাংশনের signature { #function-signatures }

[`validate_call()`][pydantic.validate_call] decorator তৈরিই করা হয়েছে সব সম্ভাব্য
[প্যারামিটার ধরন][parameter] আর তাদের সব সম্ভাব্য মিশ্রণের ফাংশনের সাথে কাজ করার জন্য:

* ডিফল্টসহ বা ছাড়া positional বা keyword প্যারামিটার।
* শুধু-keyword প্যারামিটার: `*,`-এর পরের প্যারামিটার।
* শুধু-positional প্যারামিটার: `, /`-এর আগের প্যারামিটার।
* `*` দিয়ে সংজ্ঞায়িত পরিবর্তনশীল positional প্যারামিটার (প্রায়ই `*args`)।
* `**` দিয়ে সংজ্ঞায়িত পরিবর্তনশীল keyword প্যারামিটার (প্রায়ই `**kwargs`)।

/// details | উদাহরণ
    type: tip

⟦CODE3⟧

///

/// note | keyword প্যারামিটারের জন্য [`Unpack`][typing.Unpack]

ফাংশনের পরিবর্তনশীল keyword প্যারামিটারের (`**kwargs`) annotation দিতে [`Unpack`][typing.Unpack] আর typed dictionary
ব্যবহার করা যায়:

⟦CODE4⟧

তথ্যসূত্র হিসেবে দেখুন [সংশ্লিষ্ট specification অংশ][related specification section] আর [PEP 692]।

/// info | v2.10-এ যোগ হয়েছে
///

[related specification section]: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-for-keyword-arguments
[PEP 692]: https://peps.python.org/pep-0692/

///

## ফাংশনের প্যারামিটার বর্ণনায় [`Field()`][pydantic.Field] ফাংশন ব্যবহার { #using-the-field-function-to-describe-function-parameters }

ফিল্ড আর যাচাই নিয়ে বাড়তি তথ্য দিতে decorator-এর সাথেও [`Field()` ফাংশন](fields.md) ব্যবহার করা যায়।
`default` বা `default_factory` প্যারামিটার ব্যবহার না করলে
[annotated pattern](./fields.md#the-annotated-pattern) ব্যবহারের পরামর্শ দেওয়া হয় (যাতে type checker
প্যারামিটারটিকে বাধ্যতামূলক হিসেবে বোঝে)। নাহলে, [`Field()`][pydantic.Field] ফাংশনটি
ডিফল্ট মান হিসেবে ব্যবহার করা যায় (আবারও, type checker-কে বোঝাতে যে প্যারামিটারের একটি ডিফল্ট মান আছে)।

⟦CODE5⟧

decorator-এর সাথে [alias](fields.md#field-aliases) স্বাভাবিকভাবেই ব্যবহার করা যায়:

⟦CODE6⟧

## মূল ফাংশনে পৌঁছানো { #accessing-the-original-function }

decorate করা মূল ফাংশনটি এখনো `raw_function` অ্যাট্রিবিউট দিয়ে পাওয়া যায়।
কিছু ক্ষেত্রে যদি ইনপুট আর্গুমেন্টে আপনার ভরসা থাকে আর সবচেয়ে দক্ষভাবে ফাংশন ডাকতে চান (দেখুন নিচে [পারফরম্যান্স নিয়ে কথা](#performance)), তখন এটি কাজে লাগে:

⟦CODE7⟧

## Async ফাংশন { #async-functions }

[`validate_call()`][pydantic.validate_call] async ফাংশনেও ব্যবহার করা যায়:

⟦CODE8⟧

## type checker-এর সাথে সামঞ্জস্য { #compatibility-with-type-checkers }

[`validate_call()`][pydantic.validate_call] decorator decorate করা ফাংশনের signature অক্ষুণ্ণ রাখে বলে,
এটি type checker-এর (যেমন mypy আর pyright) সাথে মানানসই হওয়ার কথা। তবে Python টাইপ সিস্টেমের বর্তমান সীমাবদ্ধতার কারণে,
[`raw_function`](#accessing-the-original-function) বা অন্য অ্যাট্রিবিউট চেনা যাবে না, আর আপনাকে
এররটি চাপা দিতে হবে (সাধারণত একটি `# type: ignore` মন্তব্য দিয়ে)।

## নিজের কনফিগারেশন { #custom-configuration }

Pydantic মডেলের মতোই, decorator-এর `config` প্যারামিটার দিয়ে নিজের কনফিগারেশন দেওয়া যায়:

⟦CODE9⟧

/// info | কোডটি সহজ ভাষায়

`Foobar` Pydantic চেনে না, তাই `arbitrary_types_allowed=True` দিয়ে বলা হলো "শুধু দেখো এটি `Foobar`-এর instance কিনা"। `add_foobars(1, 2)`-এ দুটো আর্গুমেন্টই `Foobar` নয়, তাই দুটো এরর। strict mode চাইলে একইভাবে `config=ConfigDict(strict=True)`।

///

## বাড়তি কৌশল: ফাংশন ডাকার আগেই আর্গুমেন্ট যাচাই { #extension-validating-arguments-before-calling-a-function }

কিছু ক্ষেত্রে ফাংশনের আর্গুমেন্টের যাচাই আর ফাংশন ডাকা আলাদা করা কাজে লাগতে পারে।
বিশেষ করে যখন ফাংশনটি ব্যয়বহুল বা সময়সাপেক্ষ।

এই ধরনের কাজের জন্য একটি বিকল্প পদ্ধতির উদাহরণ:

⟦CODE10⟧

/// info | কোডটি সহজ ভাষায়

`validate_foo(a=1, b=2)` ডাকামাত্র আর্গুমেন্ট যাচাই হয়ে যায়, কিন্তু আসল কাজ (`foo`) তখনো চলেনি। পরে সুবিধামতো সময়ে `foo()` ডাকলে কাজ হয়। ভুল আর্গুমেন্ট হলে ধীর কাজ শুরুর আগেই জানা যায়।

///

## সীমাবদ্ধতা { #limitations }

### যাচাইয়ের এক্সেপশন { #validation-exception }

এখন যাচাই ব্যর্থ হলে একটি সাধারণ Pydantic [`ValidationError`][pydantic_core.ValidationError] তোলা হয়
(বিস্তারিত জানতে দেখুন [মডেলের এরর সামলানো](models.md#error-handling))। বাধ্যতামূলক আর্গুমেন্ট না দিলেও তাই হয়,
যেখানে Python সাধারণত একটি [`TypeError`][] তোলে।

এররে কোন আর্গুমেন্ট আর কোন মান প্রত্যাখ্যাত হয়েছে তা বলা থাকে। আশেপাশের trace context-এও
সেই তথ্য দরকার হলে, decorate করা ফাংশনের ডাক ব্যর্থ হলে [Logfire](../errors/troubleshooting.md) সেগুলো রেকর্ড করতে পারে।

### পারফরম্যান্স { #performance }

Pydantic-কে যতটা সম্ভব দ্রুত করতে আমরা অনেক চেষ্টা করেছি। decorate করা ফাংশনের বিশ্লেষণ
একবারই হয়, তবু মূল ফাংশনের তুলনায় ফাংশন ডাকার সময় পারফরম্যান্সে কিছু প্রভাব পড়বেই।

অনেক ক্ষেত্রে এর প্রভাব সামান্য বা চোখেই পড়বে না। তবে মনে রাখুন,
[`validate_call()`][pydantic.validate_call] কঠোর টাইপের (strongly typed) ভাষায় ফাংশন সংজ্ঞার
সমতুল্য বা বিকল্প নয়, আর কখনো হবেও না।

/// check | সংক্ষেপে মনে রাখুন

* ফাংশনের ওপরে `@validate_call` দিলে annotation অনুযায়ী আর্গুমেন্ট যাচাই আর রূপান্তর হয়।
* ফেরত মানও যাচাইয়ে `@validate_call(validate_return=True)`।
* শর্তে `Annotated[int, Field(gt=10)]`, কনফিগারেশনে `@validate_call(config=ConfigDict(...))`।
* যাচাই এড়িয়ে দ্রুত ডাকতে `func.raw_function(...)`; async ফাংশনেও চলে।
* ব্যর্থ হলে `ValidationError` (বাদ পড়া আর্গুমেন্টেও, `TypeError` নয়)।

///
