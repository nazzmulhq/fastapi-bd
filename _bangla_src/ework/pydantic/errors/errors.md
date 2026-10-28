# এরর সামলানো { #error-handling }

/// note | এই পেজে যা শিখবেন

* `ValidationError` কী তথ্য দেয়, আর কোন মেথড দিয়ে তা পড়বেন (`errors()`, `error_count()`, `json()`)।
* প্রতিটি এররের ভেতরের অংশ (`type`, `loc`, `msg`, `input`, `ctx`, `url`) কী বোঝায়।
* এররের বার্তা নিজের মতো করা, যেমন বাংলায় অনুবাদ, আর `loc` সুন্দর করে লেখা।

///

যাচাই করা ডেটায় কোনো ভুল পেলেই Pydantic একটি [`ValidationError`][pydantic_core.ValidationError] তুলবে।

/// note | মনে রাখুন

যাচাইয়ের কোড নিজে [`ValidationError`][pydantic_core.ValidationError] তুলবে না,
বরং একটি [`ValueError`][] বা [`AssertionError`][] (বা তাদের subclass) তুলবে, যা
ধরা হয়ে চূড়ান্ত [`ValidationError`][pydantic_core.ValidationError] পূরণে ব্যবহার হবে।

আরও বিস্তারিত জানতে দেখুন validators ডকুমেন্টেশনের [নির্দিষ্ট অংশ](../concepts/validators.md#raising-validation-errors)।

///

সেই [`ValidationError`][pydantic_core.ValidationError]-এ সব এরর আর সেগুলো কীভাবে ঘটল তার তথ্য থাকবে।

/// tip | উদাহরণ দিয়ে বুঝি

`ValidationError` হলো পরীক্ষার খাতার মূল্যায়ন পত্র: প্রথম ভুলেই খাতা ফেরত দেয় না, সব ভুল একসাথে চিহ্নিত করে। প্রতিটি ভুলের পাশে লেখা থাকে কোন প্রশ্নে (`loc`), কী ভুল (`msg`), ভুলের ধরন (`type`), আর ছাত্র কী লিখেছিল (`input`)।

///

এই এররগুলো কয়েকভাবে পড়তে পারেন:

| মেথড                                                       | বর্ণনা                                                                                    |
|--------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| [`errors()`][pydantic_core.ValidationError.errors]           | ইনপুট ডেটায় পাওয়া [`ErrorDetails`][pydantic_core.ErrorDetails] এররের একটি তালিকা ফেরত দেয়। |
| [`error_count()`][pydantic_core.ValidationError.error_count] | এররের সংখ্যা ফেরত দেয়।                                                                  |
| [`json()`][pydantic_core.ValidationError.json]               | এররের তালিকার একটি JSON রূপ ফেরত দেয়।                                              |
| `str(e)`                                                     | এররগুলোর মানুষের পড়ার উপযোগী একটি রূপ ফেরত দেয়।                                         |

[`ErrorDetails`][pydantic_core.ErrorDetails] অবজেক্টটি একটি ডিকশনারি। এতে থাকে:

| property                                    | বর্ণনা                                                                    |
|---------------------------------------------|--------------------------------------------------------------------------------|
| [`ctx`][pydantic_core.ErrorDetails.ctx]     | একটি ঐচ্ছিক অবজেক্ট, যাতে এররের বার্তা তৈরিতে দরকারি মান থাকে (যেমন `{'gt': 42}`)। |
| [`input`][pydantic_core.ErrorDetails.input] | যাচাইয়ের জন্য দেওয়া ইনপুট।                                             |
| [`loc`][pydantic_core.ErrorDetails.loc]     | এররের অবস্থান, একটি তালিকা হিসেবে।                                                |
| [`msg`][pydantic_core.ErrorDetails.msg]     | এররের মানুষের পড়ার উপযোগী ব্যাখ্যা।                                     |
| [`type`][pydantic_core.ErrorDetails.type]   | এররের ধরনের কম্পিউটারের পড়ার উপযোগী পরিচয় (যেমন `'missing'`)।                              |
| [`url`][pydantic_core.ErrorDetails.url]     | এররটি নিয়ে তথ্য দেওয়া ডকুমেন্টেশনের URL।                      |

[`loc`][pydantic_core.ErrorDetails.loc] তালিকার প্রথম আইটেম হবে সেই ফিল্ড যেখানে এররটি ঘটেছে, আর ফিল্ডটি যদি একটি
[sub-model](../concepts/models.md#nested-models) হয়, তাহলে এররের নেস্টেড অবস্থান বোঝাতে পরের আইটেমগুলো থাকবে।

চলমান একটি সার্ভিস জুড়ে ছড়ানো যাচাইয়ের ক্ষেত্রে, [Logfire](troubleshooting.md) প্রতিটি ডাক `try`/`except`-এ না মুড়েই
এই একই গোছানো এররের তালিকা আর আশেপাশের trace context রেকর্ড করে।

একটি প্রদর্শনী হিসেবে:

⟦CODE1⟧

/// info | এররগুলো সহজ ভাষায়

| `loc` | কেন এরর |
| --- | --- |
| `('is_required',)` | ফিল্ডটি দেওয়াই হয়নি (`missing`) |
| `('gt_int',)` | `21` হলো 42-এর চেয়ে ছোট; `ctx`-এ শর্তটি `{'gt': 42}` |
| `('list_of_ints', 2)` | তালিকার ৩য় আইটেম (index 2) `'bad'` সংখ্যা নয়; `'1'` কিন্তু ঠিকই সংখ্যা হয়ে গেছে |
| `('a_float',)` | নিজের validator `ValueError` তুলেছে |
| `('recursive_model', 'lng')` | নেস্টেড মডেলের ভেতরের ফিল্ড; `loc` পুরো পথ দেখায় |

///

/// tip | `type` দিয়ে প্রোগ্রাম লিখুন, `msg` দিয়ে নয়

`msg` পরের সংস্করণে বদলাতে পারে, কিন্তু `type` (`'missing'`, `'greater_than'`...) স্থির। এরর দেখে কোডে সিদ্ধান্ত নিতে হলে সবসময় `error['type']` পরীক্ষা করুন।

///

## এররের বার্তা { #error-messages }

যাচাই আর ব্যবহারের এররের জন্য Pydantic দরকারি ডিফল্ট বার্তা দেওয়ার চেষ্টা করে, যা পাওয়া যাবে এখানে:

* [Validation Errors](validation_errors.md): ডেটা যাচাইয়ের সময় ঘটা এরর।
* [Usage Errors](usage_errors.md): Pydantic ব্যবহারের সময় (ভুল কোড লিখলে) ঘটা এরর।

### এররের বার্তা নিজের মতো করা { #customize-error-messages }

একটি নিজের এরর handler তৈরি করে এররের বার্তা নিজের মতো করতে পারেন।

⟦CODE2⟧

একটি প্রচলিত ব্যবহার হলো এররের বার্তা অনুবাদ করা। যেমন, ওপরের উদাহরণে,
`CUSTOM_MESSAGES` ডিকশনারির জায়গায় অনুবাদের একটি ডিকশনারি দিয়ে
এররের বার্তাগুলো অনুবাদ করা যেত।

/// tip | বাংলায় এররের বার্তা

```python
BANGLA_MESSAGES = {
    'missing': 'এই ঘরটি পূরণ করা বাধ্যতামূলক',
    'int_parsing': 'এখানে একটি পূর্ণসংখ্যা দিন',
    'greater_than': 'মান {gt}-এর চেয়ে বড় হতে হবে',
    'string_too_short': 'কমপক্ষে {min_length} অক্ষর দিন',
}

errors = convert_errors(e, BANGLA_MESSAGES)
```

`{gt}`, `{min_length}` এর মতো ফাঁকা ঘর এররের `ctx` থেকে পূরণ হয়। কোন এরর `type`-এর `ctx`-এ কী থাকে, তা দেখতে [Validation Errors](validation_errors.md) পেজ দেখুন।

///

আরেকটি উদাহরণ হলো একটি এররের `'loc'` মান যেভাবে দেখানো হয় তা নিজের মতো করা।

⟦CODE3⟧

1. ডিফল্টভাবে `e.errors()` এমন এররের তালিকা দেয় যার `loc` মান tuple-এর রূপে থাকে।
2. আমাদের নিজের `loc_to_dot_sep` ফাংশন দিয়ে `loc`-এর রূপ বদলে দিয়েছি।

/// check | সংক্ষেপে মনে রাখুন

* `e.errors()`: প্রতিটি এরর একটি ডিকশনারি (`type`, `loc`, `msg`, `input`, `ctx`, `url`)।
* `loc` বলে এরর কোথায়: ফিল্ডের নাম, তালিকার index, নেস্টেড ফিল্ড।
* প্রোগ্রামে `type` দেখে সিদ্ধান্ত নিন; ব্যবহারকারীকে দেখাতে `msg` বদলে নিজের (বা বাংলা) বার্তা দিন।

///
