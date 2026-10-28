# Validation Errors { #validation-errors }

/// note | এই পেজে যা পাবেন

* যাচাইয়ের সময় Pydantic যে প্রতিটি এরর `type` দিতে পারে, তার অর্থ আর একটি করে উদাহরণ (বর্ণানুক্রমে)।
* কোন এরর কোন দলে পড়ে, তার দ্রুত সারণি, আর এরর পেলে কী করবেন।

///

Pydantic দরকারি যাচাই এরর দেওয়ার চেষ্টা করে। নিচে pydantic নিয়ে কাজের সময় ব্যবহারকারীরা যেসব সাধারণ যাচাই এরর
পেতে পারেন তার বিস্তারিত, আর সেগুলো ঠিক করার কিছু পরামর্শ দেওয়া হলো।

নিচের এন্ট্রিগুলো প্রতিটি এরর টাইপের অর্থ ব্যাখ্যা করে। চলমান একটি সার্ভিসে কোনোটি ঘটলে প্রত্যাখ্যাত মান আর আশেপাশের trace দেখতে,
[Logfire](troubleshooting.md) ব্যর্থ যাচাই তাদের গোছানো এররসহ রেকর্ড করতে পারে। সেটআপ আর
সংবেদনশীল ডেটা নিয়ে ভাবনার জন্য দেখুন [যাচাই এররের সমস্যা সমাধান](troubleshooting.md)।

## এরর কীভাবে খুঁজবেন { #bn-how-to-use }

এরর বার্তার শেষে `[type=...]` অংশে এররের নাম থাকে, যেমন `[type=int_parsing, ...]`। নিচে সেই নামের অংশে গিয়ে অর্থ আর উদাহরণ দেখুন। নাম দেখে দলও চেনা যায়:

| নামের ধরন | মানে | উদাহরণ |
| --- | --- | --- |
| `..._type` | ইনপুটের টাইপই ভুল (যেমন সংখ্যার জায়গায় তালিকা) | `int_type`, `list_type`, `string_type` |
| `..._parsing` | টাইপ লেখা (স্ট্রিং) হলেও পড়ে বোঝা গেল না | `int_parsing`, `date_parsing`, `url_parsing` |
| `greater_than`, `less_than`, `multiple_of` ... | সংখ্যার শর্ত ভাঙা | `gt`, `ge`, `lt`, `le` |
| `..._too_long`, `..._too_short` | দৈর্ঘ্যের শর্ত ভাঙা | `max_length`, `min_length` |
| `missing...` | বাধ্যতামূলক কিছু দেওয়া হয়নি | `missing`, `missing_argument` |
| `frozen_...` | বদলানো নিষেধ এমন কিছু বদলানোর চেষ্টা | `frozen_field`, `frozen_instance` |
| `value_error`, `assertion_error` | আপনার নিজের validator এরর তুলেছে | |

/// tip | উদাহরণ দিয়ে বুঝি

এই পেজটি ডাক্তারের রোগ নির্ণয়ের বইয়ের মতো: উপসর্গের নাম (`type`) দেখে ঠিক পাতায় যান, সেখানে কারণ আর উদাহরণ পাবেন। প্রায় সব ক্ষেত্রে সমাধান দুটির একটি: হয় ইনপুট ঠিক করুন, নয়তো মডেলের টাইপ বা শর্ত আপনার আসল ডেটার সাথে মিলিয়ে নিন।

///

## `arguments_type` { #arguments_type }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি ফাংশনে আর্গুমেন্ট হিসেবে পাঠানো হবে এমন একটি অবজেক্ট
`tuple`, `list` বা `dict` নয়:

⟦CODE1⟧

## `assertion_error` { #assertion_error }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি ব্যর্থ `assert` স্টেটমেন্ট পাওয়া যায়:

⟦CODE2⟧

## `bool_parsing` { #bool_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা boolean-এ রূপান্তরের জন্য বৈধ নয় (যেমন `'yes'`, `'true'`, `'1'` চলে, কিন্তু `'হ্যাঁ'` বা `'maybe'` চলে না):

⟦CODE3⟧

## `bool_type` { #bool_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `bool` ফিল্ডের জন্য বৈধ নয়:

⟦CODE4⟧

strict ফিল্ডে ইনপুট মান `bool`-এর instance না হলেও এই এরর ওঠে।

## `bytes_invalid_encoding` { #bytes_invalid_encoding }

এই এরর ওঠে যখন একটি `bytes` মান কনফিগার করা encoding অনুযায়ী অবৈধ।
নিচের উদাহরণে, `'a'` অবৈধ hex (অঙ্কের সংখ্যা বিজোড়)।

⟦CODE5⟧

## `bytes_too_long` { #bytes_too_long }

এই এরর ওঠে যখন একটি `bytes` মানের দৈর্ঘ্য ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

⟦CODE6⟧

## `bytes_too_short` { #bytes_too_short }

এই এরর ওঠে যখন একটি `bytes` মানের দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

⟦CODE7⟧

## `bytes_type` { #bytes_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `bytes` ফিল্ডের জন্য বৈধ নয়:

⟦CODE8⟧

strict ফিল্ডে ইনপুট মান `bytes`-এর instance না হলেও এই এরর ওঠে।

## `callable_type` { #callable_type }

এই এরর ওঠে যখন ইনপুট মান callable (ডাকা যায় এমন, যেমন ফাংশন) হিসেবে বৈধ নয়:

⟦CODE9⟧

## `complex_str_parsing` { #complex_str_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং, কিন্তু complex number হিসেবে পার্স করা যায় না কারণ
এটি Python-এর [নিয়ম](https://docs.python.org/3/library/functions.html#complex) মানে না:

⟦CODE10⟧

## `complex_type` { #complex_type }

এই এরর ওঠে যখন ইনপুট মানকে complex number হিসেবে বোঝা যায় না:

⟦CODE11⟧

## `counter_type` { #counter_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`Counter`][collections.Counter] ফিল্ডের জন্য বৈধ নয়:

⟦CODE12⟧

## `dataclass_exact_type` { #dataclass_exact_type }

এই এরর ওঠে যখন `strict=True` দিয়ে একটি dataclass যাচাই করা হয় আর ইনপুট সেই dataclass-এর instance নয়:

⟦CODE13⟧

## `dataclass_type` { #dataclass_type }

এই এরর ওঠে যখন ইনপুট মান একটি `dataclass` ফিল্ডের জন্য বৈধ নয়:

⟦CODE14⟧

## `date_from_datetime_inexact` { #date_from_datetime_inexact }

এই এরর ওঠে যখন একটি `date` ফিল্ডের জন্য দেওয়া `datetime` ইনপুটের সময়ের অংশ শূন্য নয়।
একটি timestamp `date` টাইপের ফিল্ডে পার্স হতে হলে, সময়ের সব অংশ শূন্য হতে হবে:

⟦CODE15⟧

## `date_from_datetime_parsing` { #date_from_datetime_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `date` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE16⟧

## `date_future` { #date_future }

এই এরর ওঠে যখন একটি `FutureDate` ফিল্ডের জন্য দেওয়া ইনপুট মান ভবিষ্যতের নয়:

⟦CODE17⟧

## `date_parsing` { #date_parsing }

এই এরর ওঠে যখন JSON যাচাইয়ের সময় ইনপুট মান এমন একটি স্ট্রিং যা একটি `date` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE18⟧

## `date_past` { #date_past }

এই এরর ওঠে যখন একটি `PastDate` ফিল্ডের জন্য দেওয়া মান অতীতের নয়:

⟦CODE19⟧

## `date_type` { #date_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `date` ফিল্ডের জন্য বৈধ নয়:

⟦CODE20⟧

strict ফিল্ডে ইনপুট মান `date`-এর instance না হলেও এই এরর ওঠে।

## `datetime_from_date_parsing` { #datetime_from_date_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `datetime` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE21⟧

## `datetime_future` { #datetime_future }

এই এরর ওঠে যখন একটি `FutureDatetime` ফিল্ডের জন্য দেওয়া মান ভবিষ্যতের নয়:

⟦CODE22⟧

## `datetime_object_invalid` { #datetime_object_invalid }

এই এরর ওঠে যখন `datetime` অবজেক্টের কোনো কিছু বৈধ নয়:

⟦CODE23⟧

## `datetime_parsing` { #datetime_parsing }

এই এরর ওঠে যখন মানটি এমন একটি স্ট্রিং যা একটি `datetime` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE24⟧

## `datetime_past` { #datetime_past }

এই এরর ওঠে যখন একটি `PastDatetime` ফিল্ডের জন্য দেওয়া মান অতীতের নয়:

⟦CODE25⟧

## `datetime_type` { #datetime_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `datetime` ফিল্ডের জন্য বৈধ নয়:

⟦CODE26⟧

strict ফিল্ডে ইনপুট মান `datetime`-এর instance না হলেও এই এরর ওঠে।

## `decimal_max_digits` { #decimal_max_digits }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে অঙ্ক খুব বেশি:

⟦CODE27⟧

## `decimal_max_places` { #decimal_max_places }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে দশমিক বিন্দুর পরে অঙ্ক খুব বেশি:

⟦CODE28⟧

## `decimal_parsing` { #decimal_parsing }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মান দশমিক সংখ্যা হিসেবে পার্স করা যায়নি:

⟦CODE29⟧

## `decimal_type` { #decimal_type }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মান ভুল টাইপের:

⟦CODE30⟧

strict ফিল্ডে ইনপুট মান `Decimal`-এর instance না হলেও এই এরর ওঠে।

## `decimal_whole_digits` { #decimal_whole_digits }

এই এরর ওঠে যখন একটি `Decimal`-এর জন্য দেওয়া মানে দশমিক বিন্দুর আগে `max_digits` - `decimal_places`-এর চেয়ে বেশি অঙ্ক থাকে (যদি দুটোই দেওয়া থাকে):

⟦CODE31⟧

## `default_factory_not_called` { #default_factory_not_called }

এই এরর ওঠে যখন একটি [যাচাই হওয়া ডেটা নেওয়া default factory](../concepts/fields.md#default-factory-validated-data)
ডাকা যায় না, কারণ আগের ফিল্ডগুলোতে যাচাই ব্যর্থ হয়েছে:

⟦CODE32⟧

## `deque_type` { #deque_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`deque`][collections.deque] ফিল্ডের জন্য বৈধ নয়:

⟦CODE33⟧

## `dict_type` { #dict_type }

এই এরর ওঠে যখন একটি `dict` ফিল্ডের ইনপুট মানের টাইপ `dict` নয়:

⟦CODE34⟧

## `ellipsis_error` { #ellipsis_error }

এই এরর ওঠে যখন ইনপুটটি [`Ellipsis`][] literal (`...`) নয়:

⟦CODE35⟧

## `enum` { #enum }

এই এরর ওঠে যখন ইনপুট মান একটি `enum` ফিল্ডের সদস্যদের মধ্যে নেই:

⟦CODE36⟧

## `extra_forbidden` { #extra_forbidden }

এই এরর ওঠে যখন ইনপুট মানে বাড়তি ফিল্ড থাকে, কিন্তু `model_config['extra'] == 'forbid'`:

⟦CODE37⟧

`extra` কনফিগারেশন নিয়ে আরও পড়তে পারেন [বাড়তি অ্যাট্রিবিউট][pydantic.config.ConfigDict.extra] অংশে।

## `finite_number` { #finite_number }

এই এরর ওঠে যখন যাচাইয়ের সময় মানটি অসীম, বা 64-bit floating point সংখ্যা হিসেবে প্রকাশ করার জন্য
খুব বড়:

⟦CODE38⟧

## `float_parsing` { #float_parsing }

এই এরর ওঠে যখন মানটি এমন একটি স্ট্রিং যা `float` হিসেবে পার্স করা যায় না:

⟦CODE39⟧

## `float_type` { #float_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `float` ফিল্ডের জন্য বৈধ নয়:

⟦CODE40⟧

## `fraction_parsing` { #fraction_parsing }

এই এরর ওঠে যখন দেওয়া মান ভগ্নাংশ (fraction) হিসেবে পার্স করা যায়নি:

⟦CODE41⟧

## `fraction_type` { #fraction_type }

এই এরর ওঠে যখন একটি [`Fraction`][fractions.Fraction]-এর জন্য দেওয়া মান ভুল টাইপের:

⟦CODE42⟧

## `frozen_dict_type` { #frozen_dict_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `frozendict` ফিল্ডের জন্য বৈধ নয়:

⟦CODE43⟧

## `frozen_field` { #frozen_field }

এই এরর ওঠে যখন `frozen=True` থাকা একটি ফিল্ডে মান বসানোর, বা এমন ফিল্ড মুছে ফেলার চেষ্টা করেন:

⟦CODE44⟧

## `frozen_instance` { #frozen_instance }

এই এরর ওঠে যখন [কনফিগারেশনে](../concepts/config.md) `frozen` সেট করা থাকে আর আপনি যেকোনো ফিল্ড মুছে ফেলার
বা তাতে নতুন মান বসানোর চেষ্টা করেন:

⟦CODE45⟧

## `frozen_set_type` { #frozen_set_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `frozenset` ফিল্ডের জন্য বৈধ নয়:

⟦CODE46⟧

## `get_attribute_error` { #get_attribute_error }

এই এরর ওঠে যখন `model_config['from_attributes'] == True` আর অ্যাট্রিবিউট পড়ার সময় একটি এরর ওঠে:

⟦CODE47⟧

## `greater_than` { #greater_than }

এই এরর ওঠে যখন মানটি ফিল্ডের `gt` শর্তের চেয়ে বড় নয়:

⟦CODE48⟧

## `greater_than_equal` { #greater_than_equal }

এই এরর ওঠে যখন মানটি ফিল্ডের `ge` শর্তের চেয়ে বড় বা সমান নয়:

⟦CODE49⟧

## `int_from_float` { #int_from_float }

এই এরর ওঠে যখন একটি `int` ফিল্ডে দশমিক অংশসহ একটি `float` মান দেন (যেমন `1.5`; কিন্তু `1.0` চলে):

⟦CODE50⟧

## `int_parsing` { #int_parsing }

এই এরর ওঠে যখন মানটি `int` হিসেবে পার্স করা যায় না:

⟦CODE51⟧

## `int_parsing_size` { #int_parsing_size }

এই এরর ওঠে যখন একটি স্ট্রিং থেকে এমন python বা JSON মান পার্সের চেষ্টা করা হয় যা Python-এর
`str` থেকে `int` পার্সিংয়ের অনুমোদিত সর্বোচ্চ সীমার বাইরে:

⟦CODE52⟧

## `int_type` { #int_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `int` ফিল্ডের জন্য বৈধ নয়:

⟦CODE53⟧

## `invalid_key` { #invalid_key }

এই এরর ওঠে যখন এমন একটি `dict` যাচাইয়ের চেষ্টা করা হয় যার একটি key `str`-এর instance নয়:

⟦CODE54⟧

## `is_instance_of` { #is_instance_of }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত টাইপের instance নয়:

⟦CODE55⟧

## `is_subclass_of` { #is_subclass_of }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত টাইপের subclass নয়:

⟦CODE56⟧

## `iterable_type` { #iterable_type }

এই এরর ওঠে যখন ইনপুট মান একটি `Iterable` হিসেবে বৈধ নয়:

⟦CODE57⟧

## `iteration_error` { #iteration_error }

এই এরর ওঠে যখন iteration (একে একে আইটেম নেওয়া)-এর সময় একটি এরর ঘটে:

⟦CODE58⟧

## `json_invalid` { #json_invalid }

এই এরর ওঠে যখন ইনপুট মান একটি বৈধ JSON স্ট্রিং নয়:

⟦CODE59⟧

## `json_type` { #json_type }

এই এরর ওঠে যখন ইনপুট মান এমন টাইপের যা JSON হিসেবে পার্স করা যায় না:

⟦CODE60⟧

## `less_than` { #less_than }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `lt` শর্তের চেয়ে ছোট নয়:

⟦CODE61⟧

## `less_than_equal` { #less_than_equal }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `le` শর্তের চেয়ে ছোট বা সমান নয়:

⟦CODE62⟧

## `list_type` { #list_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `list` ফিল্ডের জন্য বৈধ নয়:

⟦CODE63⟧

## `literal_error` { #literal_error }

এই এরর ওঠে যখন ইনপুট মান প্রত্যাশিত literal মানগুলোর একটি নয়:

⟦CODE64⟧

## `mapping_type` { #mapping_type }

এই এরর ওঠে যখন যাচাইয়ের সময় `Mapping` protocol-এর মেথড, যেমন `.items()`, ডাকতে গিয়ে ব্যর্থতার কারণে
সমস্যা হয়:

⟦CODE65⟧

## `missing` { #missing }

এই এরর ওঠে যখন ইনপুট মানে বাধ্যতামূলক ফিল্ড অনুপস্থিত:

⟦CODE66⟧

/// tip | সমাধান

ফিল্ডটি পাঠান, অথবা ফিল্ডটি ঐচ্ছিক হলে মডেলে একটি ডিফল্ট মান দিন (যেমন `name: str | None = None`)। মনে রাখুন, শুধু `str | None` লিখলে ফিল্ড ঐচ্ছিক হয় না; `= None` ডিফল্টও লাগে।

///

## `missing_argument` { #missing_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক positional-or-keyword আর্গুমেন্ট
দেওয়া হয় না:

⟦CODE67⟧

## `missing_keyword_only_argument` { #missing_keyword_only_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক keyword-only আর্গুমেন্ট দেওয়া হয় না:

⟦CODE68⟧

## `missing_positional_only_argument` { #missing_positional_only_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশনে একটি বাধ্যতামূলক positional-only আর্গুমেন্ট
দেওয়া হয় না:

⟦CODE69⟧

## `missing_sentinel_error` { #missing_sentinel_error }

এই এরর ওঠে যখন `MISSING` sentinel-ই একমাত্র অনুমোদিত মান, কিন্তু যাচাইয়ের সময় সেটি দেওয়া হয়নি:

⟦CODE70⟧

## `model_attributes_type` { #model_attributes_type }

এই এরর ওঠে যখন ইনপুট মান একটি বৈধ ডিকশনারি, মডেল instance, বা এমন instance নয় যা থেকে ফিল্ড বের করা যায়:

⟦CODE71⟧

## `model_type` { #model_type }

এই এরর ওঠে যখন একটি মডেলের ইনপুট সেই মডেলের instance বা dict নয়:

⟦CODE72⟧

## `multiple_argument_values` { #multiple_argument_values }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি আর্গুমেন্টের জন্য একাধিক মান দেন
(যেমন positional হিসেবেও আর keyword হিসেবেও):

⟦CODE73⟧

## `multiple_of` { #multiple_of }

এই এরর ওঠে যখন ইনপুটটি ফিল্ডের `multiple_of` শর্তের গুণিতক নয়:

⟦CODE74⟧

## `named_tuple_type` { #named_tuple_type }

এই এরর ওঠে যখন ইনপুট মান একটি named tuple ফিল্ডের জন্য বৈধ নয়:

⟦CODE75⟧

## `needs_python_object` { #needs_python_object }

এই ধরনের এরর ওঠে যখন এমন একটি ফরম্যাট থেকে যাচাইয়ের চেষ্টা করা হয় যা একটি Python অবজেক্টে রূপান্তর করা যায় না।
যেমন, JSON থেকে আমরা `isinstance` বা `issubclass` পরীক্ষা করতে পারি না:

⟦CODE76⟧

## `no_such_attribute` { #no_such_attribute }

এই এরর ওঠে যখন কনফিগে `validate_assignment=True` থাকে, আর আপনি এমন একটি অ্যাট্রিবিউটে মান বসানোর চেষ্টা করেন
যা বিদ্যমান কোনো ফিল্ড নয়:

⟦CODE77⟧

## `none_required` { #none_required }

এই এরর ওঠে যখন `None` দাবি করে এমন একটি ফিল্ডের ইনপুট মান `None` নয়:

⟦CODE78⟧

/// note | মনে রাখুন

যখন আপনার মডেলে একটি ফিল্ডের নাম আর তার টাইপের নামের মধ্যে সংঘাত থাকে, তখন এই এরর পেতে পারেন। আরও নির্দিষ্টভাবে, সেই ফিল্ডের ডিফল্ট মান `None` হলে এই এরর ওঠার সম্ভাবনা বেশি।

যেমন, নিচের কোডে `none_required` যাচাই এরর আসবে, কারণ `int` ফিল্ডের ডিফল্ট মান `None` আর এর নাম হুবহু তার টাইপের নামের মতো, যা যাচাইয়ে সমস্যা তৈরি করে।

⟦CODE79⟧

///

## `ordered_dict_type` { #ordered_dict_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি [`OrderedDict`][collections.OrderedDict] ফিল্ডের জন্য বৈধ নয়:

⟦CODE80⟧

## `recursion_loop` { #recursion_loop }

এই এরর ওঠে যখন একটি চক্রাকার উল্লেখ শনাক্ত হয় (দেখুন [Cyclic references](../examples/cyclic_references.md)):

⟦CODE81⟧

## `set_item_not_hashable` { #set_item_not_hashable }

এই এরর ওঠে যখন একটি hash করা যায় না এমন মান (যেমন তালিকা বা ডিকশনারি) একটি [`set`][] বা একটি [`frozenset`][]-এর বিপরীতে যাচাই হয়:

⟦CODE82⟧

## `set_type` { #set_type }

এই এরর ওঠে যখন মানের টাইপ একটি `set` ফিল্ডের জন্য বৈধ নয়:

⟦CODE83⟧

## `string_not_ascii` { #string_not_ascii }

এই এরর ওঠে যখন ইনপুট স্ট্রিংয়ে ASCII নয় এমন অক্ষর থাকে (বাংলা অক্ষরও ASCII নয়):

⟦CODE84⟧

## `string_pattern_mismatch` { #string_pattern_mismatch }

এই এরর ওঠে যখন ইনপুট মান ফিল্ডের `pattern` শর্তের সাথে মেলে না:

⟦CODE85⟧

## `string_too_long` { #string_too_long }

এই এরর ওঠে যখন ইনপুট মান এমন একটি স্ট্রিং যার দৈর্ঘ্য ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

⟦CODE86⟧

## `string_too_short` { #string_too_short }

এই এরর ওঠে যখন ইনপুট মান এমন একটি স্ট্রিং যার দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

⟦CODE87⟧

## `string_type` { #string_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `str` ফিল্ডের জন্য বৈধ নয়:

⟦CODE88⟧

strict ফিল্ডে ইনপুট মান `str`-এর instance না হলেও এই এরর ওঠে।

## `string_unicode` { #string_unicode }

এই এরর ওঠে যখন মানটি একটি Unicode স্ট্রিং হিসেবে পার্স করা যায় না:

⟦CODE89⟧

## `time_delta_parsing` { #time_delta_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `timedelta` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE90⟧

## `time_delta_type` { #time_delta_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `timedelta` ফিল্ডের জন্য বৈধ নয়:

⟦CODE91⟧

strict ফিল্ডে ইনপুট মান `timedelta`-এর instance না হলেও এই এরর ওঠে।

## `time_parsing` { #time_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি স্ট্রিং যা একটি `time` ফিল্ডের জন্য পার্স করা যায় না:

⟦CODE92⟧

## `time_type` { #time_type }

এই এরর ওঠে যখন মানের টাইপ একটি `time` ফিল্ডের জন্য বৈধ নয়:

⟦CODE93⟧

strict ফিল্ডে ইনপুট মান `time`-এর instance না হলেও এই এরর ওঠে।

## `timezone_aware` { #timezone_aware }

এই এরর ওঠে যখন একটি timezone-সহ (timezone-aware) `datetime` ফিল্ডের জন্য দেওয়া `datetime` মানে
timezone-এর তথ্য নেই:

⟦CODE94⟧

## `timezone_naive` { #timezone_naive }

এই এরর ওঠে যখন একটি timezone-ছাড়া (timezone-naive) `datetime` ফিল্ডের জন্য দেওয়া `datetime` মানে
timezone-এর তথ্য আছে:

⟦CODE95⟧

## `too_long` { #too_long }

এই এরর ওঠে যখন ইনপুট মানের দৈর্ঘ্য (যেমন তালিকার আইটেম সংখ্যা) ফিল্ডের `max_length` শর্তের চেয়ে বেশি:

⟦CODE96⟧

## `too_short` { #too_short }

এই এরর ওঠে যখন মানের দৈর্ঘ্য ফিল্ডের `min_length` শর্তের চেয়ে কম:

⟦CODE97⟧

## `tuple_type` { #tuple_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি `tuple` ফিল্ডের জন্য বৈধ নয়:

⟦CODE98⟧

strict ফিল্ডে ইনপুট মান `tuple`-এর instance না হলেও এই এরর ওঠে।

## `unexpected_keyword_argument` { #unexpected_keyword_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি positional-only
আর্গুমেন্টের মান keyword দিয়ে দেন:

⟦CODE99⟧

pydantic.dataclasses আর `extra=forbid` ব্যবহার করলেও এটি ওঠে:

⟦CODE100⟧

## `unexpected_positional_argument` { #unexpected_positional_argument }

এই এরর ওঠে যখন `validate_call` দিয়ে decorate করা একটি ফাংশন ডাকার সময় একটি keyword-only
আর্গুমেন্টের মান positional হিসেবে দেন:

⟦CODE101⟧

## `union_tag_invalid` { #union_tag_invalid }

এই এরর ওঠে যখন ইনপুটের discriminator প্রত্যাশিত মানগুলোর একটি নয়:

⟦CODE102⟧

## `union_tag_not_found` { #union_tag_not_found }

এই এরর ওঠে যখন ইনপুট থেকে একটি discriminator মান বের করা সম্ভব নয় (discriminator ফিল্ডটিই নেই):

⟦CODE103⟧

## `url_parsing` { #url_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি URL হিসেবে পার্স করা যায় না:

⟦CODE104⟧

## `url_scheme` { #url_scheme }

এই এরর ওঠে যখন URL-এর scheme (যেমন `http`, `ftp`) ফিল্ডের URL টাইপের জন্য বৈধ নয়:

⟦CODE105⟧

## `url_syntax_violation` { #url_syntax_violation }

এই এরর ওঠে যখন URL-এর গঠন (syntax) বৈধ নয়:

⟦CODE106⟧

## `url_too_long` { #url_too_long }

এই এরর ওঠে যখন URL-এর দৈর্ঘ্য 2083-এর বেশি:

⟦CODE107⟧

## `url_type` { #url_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি URL ফিল্ডের জন্য বৈধ নয়:

⟦CODE108⟧

## `uuid_parsing` { #uuid_parsing }

এই এরর ওঠে যখন ইনপুট মান একটি UUID ফিল্ডের জন্য বৈধ নয় (পার্স করা যায় না):

⟦CODE109⟧

## `uuid_type` { #uuid_type }

এই এরর ওঠে যখন ইনপুট মানের টাইপ একটি UUID ফিল্ডের জন্য বৈধ instance নয় (str, bytes বা UUID):

⟦CODE110⟧

## `uuid_version` { #uuid_version }

এই এরর ওঠে যখন ইনপুট মান UUID-এর সংস্করণের সাথে মেলে না:

⟦CODE111⟧

## `value_error` { #value_error }

এই এরর ওঠে যখন যাচাইয়ের সময় একটি `ValueError` তোলা হয় (সাধারণত আপনার নিজের validator থেকে):

⟦CODE112⟧
