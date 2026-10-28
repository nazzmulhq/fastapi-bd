# Resolving Annotations { #resolving-annotations }

/// note | এই পেজে যা শিখবেন

* Pydantic কীভাবে চলার সময় (runtime) annotation-এর লেখা (যেমন `'MyType'`) আসল টাইপে রূপান্তর করে।
* ক্লাস সংজ্ঞায়িত হওয়ার সময় কোন কোন namespace (নামের তালিকা) কোন ক্রমে খোঁজা হয়।
* সীমাবদ্ধতা, পুরনো আচরণের সাথে সামঞ্জস্যের নিয়ম, আর `model_rebuild()` কীভাবে কাজ করে।

///

/// note | মনে রাখুন

এই অংশটি *ভেতরের কাঠামো* (internals) ডকুমেন্টেশনের অংশ, আর আংশিকভাবে অবদানকারীদের জন্য লেখা।

///

validation, serialization ইত্যাদির schema তৈরি করতে Pydantic চলার সময় [type hint][type hint]-এর ওপর ব্যাপকভাবে নির্ভর করে।

type hint মূলত static type checker-এর (যেমন [Mypy] বা [Pyright]) জন্য চালু হলেও, এগুলো
চলার সময়েও পাওয়া যায় (আর কখনো কখনো মূল্যায়নও হয়)। অর্থাৎ নিচের কোডটি চলার সময় ব্যর্থ হবে,
কারণ বর্তমান মডিউলে `Node` এখনো সংজ্ঞায়িত হয়নি:

⟦CODE1⟧

এই সমস্যা এড়াতে forward reference ব্যবহার করা যায় (annotation উদ্ধৃতিচিহ্নে মুড়ে দিয়ে)।

Python 3.7-এ [PEP 563] *annotation-এর মূল্যায়ন পিছিয়ে দেওয়া* (postponed evaluation) ধারণা চালু করে, অর্থাৎ
`from __future__ import annotations` [future statement] দিলে type hint ডিফল্টভাবে স্ট্রিং হয়ে যায়:

⟦CODE2⟧

/// tip | উদাহরণ দিয়ে বুঝি

স্ট্রিং annotation হলো ঠিকানা লেখা একটি চিরকুট: "`MyType`-এর কাছে যাও"। Pydantic-কে চিরকুট পড়ে আসল বাড়িটি (টাইপ) খুঁজে বের করতে হয়। কোন কোন পাড়ায় (namespace) খুঁজবে আর কোন ক্রমে, এই পেজ সেই নিয়মই বলে।

///

## চলার সময় মূল্যায়নের চ্যালেঞ্জ { #the-challenges-of-runtime-evaluation }

static type checker সংজ্ঞায়িত annotation বিশ্লেষণ করতে <abbr title="Abstract Syntax Tree">AST</abbr> ব্যবহার করে।
আগের উদাহরণের ক্ষেত্রে, এর সুবিধা হলো `Foo`-এর ক্লাস সংজ্ঞা বিশ্লেষণের সময় `MyType` কী বোঝায় তা বোঝা যায়,
চলার সময় `MyType` সংজ্ঞায়িত না হলেও।

তবে Pydantic-এর মতো চলার সময়ের টুলের জন্য এই forward annotation সঠিকভাবে resolve করা বেশি কঠিন।
Python standard library এর জন্য কিছু টুল দেয় ([`typing.get_type_hints()`][typing.get_type_hints],
[`inspect.get_annotations()`][inspect.get_annotations]), কিন্তু সেগুলোর কিছু সীমাবদ্ধতা আছে। তাই
বিশেষ ক্ষেত্রগুলো (edge case) আরও ভালোভাবে সামলাতে Pydantic-এ এগুলো নতুন করে লেখা হচ্ছে।

Pydantic যত বড় হয়েছে, annotation মূল্যায়নে অনিয়মিত পদ্ধতি দরকার এমন অনেক বিশেষ ক্ষেত্র সমর্থন করতে এটি নিজেকে মানিয়ে নিয়েছে।
এর কিছু ব্যবহার static type checking-এর দৃষ্টিতে সবসময় সঠিক নয়। v2.10-এ ভেতরের
যুক্তি নতুন করে সাজানো হয়েছে (refactor), annotation মূল্যায়ন সহজ আর মানসম্মত করার চেষ্টায়। স্বীকার করতেই হয়, পুরনো কোডের সাথে সামঞ্জস্য
কিছু চ্যালেঞ্জ তৈরি করেছে, আর এর কারণে কোডে এখনো কিছু চোখে পড়ার মতো দাগ রয়ে গেছে। আশা করা হচ্ছে
[PEP 649] (Python 3.14-এ চালু) প্রক্রিয়াটি অনেক সহজ করবে, বিশেষ করে একটি ফাংশনের locals সামলানোর ক্ষেত্রে।

forward reference মূল্যায়ন করতে, Pydantic মোটামুটি
[`typing.get_type_hints()`][typing.get_type_hints] ফাংশনের ডকুমেন্টেশনে বর্ণিত একই যুক্তি মেনে চলে। অর্থাৎ, built-in [`eval()`][eval] ফাংশন ব্যবহার হয়,
এতে forward reference, একটি global আর একটি local namespace দিয়ে। namespace আনার যুক্তি নিচের
অংশগুলোতে সংজ্ঞায়িত।

## ক্লাস সংজ্ঞার সময় annotation resolve করা { #resolving-annotations-at-class-definition }

এই অংশ জুড়ে নিচের উদাহরণটি তথ্যসূত্র হিসেবে ব্যবহার হবে:

⟦CODE3⟧

`Model` ক্লাস তৈরির সময়, বিভিন্ন [namespace][namespace] কাজ করে। `Model`-এর [MRO][method resolution order]-এর প্রতিটি base class-এর
জন্য (উল্টো ক্রমে, অর্থাৎ `Base` থেকে শুরু করে),
নিচের যুক্তি প্রয়োগ হয়:

1. বর্তমান base class-এর `__dict__` থেকে `__annotations__` key আনা হয়, যদি থাকে। `Base`-এর জন্য এটি হবে
   `{'f1': 'MyType'}`।
2. `__annotations__`-এর আইটেমগুলোর ওপর একে একে গিয়ে প্রতিটি annotation মূল্যায়নের চেষ্টা করা হয় [^1], built-in
   [`eval()`][eval] ফাংশনের ওপর একটি নিজস্ব মোড়ক দিয়ে। এই ফাংশন দুটি আর্গুমেন্ট নেয়, `globals` আর `locals`:
     * বর্তমান মডিউলের `__dict__` স্বাভাবিকভাবেই `globals` হিসেবে ব্যবহার হয়। `Base`-এর জন্য এটি হবে
       `sys.modules['module1'].__dict__`।
     * `locals` আর্গুমেন্টের জন্য, Pydantic নিচের namespace-গুলোতে নাম খোঁজার চেষ্টা করবে, সবচেয়ে বেশি অগ্রাধিকার আগে:
         * তাৎক্ষণিকভাবে তৈরি একটি namespace, যাতে বর্তমান ক্লাসের নাম থাকে (`{cls.__name__: cls}`)। এটি করা হয়
           recursive reference (নিজেকে উল্লেখ) সমর্থনের জন্য।
         * বর্তমান ক্লাসের locals (অর্থাৎ `cls.__dict__`)। `Model`-এর জন্য এতে `LocalType` থাকবে।
         * ক্লাসের অভিভাবক namespace, যদি ওপরে বর্ণিত globals থেকে আলাদা হয়। এটি হলো সেই frame-এর
           [locals][frame.f_locals] যেখানে ক্লাসটি সংজ্ঞায়িত হচ্ছে। `Base`-এর ক্ষেত্রে, ক্লাসটি সরাসরি মডিউলে
           সংজ্ঞায়িত হচ্ছে বলে এই namespace ব্যবহার হবে না, কারণ তাতে আবার globals-ই ব্যবহার হতো।
           `Model`-এর ক্ষেত্রে, অভিভাবক namespace হলো `inner()`-এর frame-এর locals।
3. annotation মূল্যায়ন ব্যর্থ হলে, এটি যেমন আছে তেমন রাখা হয়, যাতে পরে মডেলটি আবার তৈরি (rebuild) করা যায়। এটি
   হবে `f5`-এর ক্ষেত্রে।

`Model` ক্লাস তৈরি হয়ে গেলে, প্রতিটি ফিল্ডের resolve হওয়া টাইপ annotation নিচের সারণিতে দেওয়া হলো:

| ফিল্ডের নাম | resolve হওয়া annotation |
|------------|---------------------|
| `f1`       | [`int`][]           |
| `f2`       | [`str`][]           |
| `f3`       | [`bool`][]          |
| `f4`       | [`bytes`][]         |
| `f5`       | `'UnknownType'`     |

/// info | সারণিটি সহজ ভাষায়

* `f1`: `Base` আছে `module1`-এ, সেখানে `MyType = int`, তাই `int` (যদিও `module2`-এ `MyType = str`)।
* `f2`: `Model` আছে `module2`-এ, সেখানে `MyType = str`।
* `f3`: `InnerType` পাওয়া গেল `inner()` ফাংশনের locals-এ।
* `f4`: `LocalType` পাওয়া গেল ক্লাসের নিজের ভেতরে।
* `f5`: কোথাও নেই, তাই স্ট্রিং হিসেবেই থেকে গেল; মডেলটি অসম্পূর্ণ, পরে `model_rebuild()` লাগবে।

///

### সীমাবদ্ধতা আর পুরনো আচরণের সাথে সামঞ্জস্যের চিন্তা { #limitations-and-backwards-compatibility-concerns }

namespace আনার যুক্তি যতটা সম্ভব নির্ভুল হওয়ার চেষ্টা করলেও, আমরা এখনো কিছু সীমাবদ্ধতার মুখোমুখি:

* বর্তমান ক্লাসের locals-এ (`cls.__dict__`) অপ্রাসঙ্গিক এন্ট্রি থাকতে পারে, যার বেশিরভাগই dunder (`__x__`) অ্যাট্রিবিউট।
  অর্থাৎ এই annotation: `f: '__doc__'` সফলভাবে (আর অপ্রত্যাশিতভাবে) resolve হয়ে যাবে।
* `Model` ক্লাস একটি ফাংশনের ভেতরে তৈরি হলে, আমরা সেই frame-এর [locals][frame.f_locals]-এর একটি কপি রাখি।
  এই কপিতে শুধু `Model` সংজ্ঞায়িত হওয়ার মুহূর্তে locals-এ থাকা নামগুলো থাকে, অর্থাৎ `InnerType2` এতে থাকবে না
  (আর পরে মডেল rebuild করলেও **থাকবে না**!)।
    * memory leak এড়াতে, আমরা ফাংশনের locals-এর [weak reference][weakref] ব্যবহার করি, অর্থাৎ কিছু forward reference
    ফাংশনের বাইরে resolve না-ও হতে পারে[^2]।
    * ফাংশনের locals শুধু Pydantic মডেলের ক্ষেত্রে বিবেচনা করা হয়; dataclass, typed
    dictionary বা named tuple-এ এই পদ্ধতি প্রযোজ্য নয়।

পুরনো কোডের সাথে সামঞ্জস্যের কারণে, আর মডেল rebuild না করেই বৈধ ব্যবহারগুলো সমর্থনের জন্য,
core schema তৈরির ক্ষেত্রে ওপরে বর্ণিত namespace যুক্তি একটু আলাদা।
নিচের উদাহরণটি দেখুন:
{% raw %}{#backwards-compatibility-logic}{% endraw %}

⟦CODE4⟧

`Bar`-এর ফিল্ডগুলো সংগ্রহ হয়ে গেলে (অর্থাৎ annotation resolve হয়ে গেলে), `GenerateSchema` ক্লাস
প্রতিটি ফিল্ডকে একটি core schema-তে রূপান্তর করে। যখন এটি ক্লাস-সদৃশ অন্য একটি ফিল্ড টাইপ পায় (যেমন একটি dataclass), তখন এটি
annotation মূল্যায়নের চেষ্টা করে, মোটামুটি [ওপরে বর্ণিত](#resolving-annotations-at-class-definition) একই যুক্তি মেনে।
তবে `'Bar | None'` annotation মূল্যায়ন করতে globals বা locals-এ `Bar` থাকা দরকার, যা সাধারণত
*থাকে না*: `Bar` তখন তৈরি হচ্ছে, তাই সেই মুহূর্তে এটি বর্তমান মডিউলের `__dict__`-এ "বসানো" হয়নি।

`Bar`-এর ওপর [`model_rebuild()`][pydantic.BaseModel.model_rebuild] ডাকার প্রয়োজন এড়াতে, `Foo`-এর annotation মূল্যায়নের সময়
locals-এ অভিভাবক namespace
(যদি `Bar` একটি ফাংশনের ভেতরে সংজ্ঞায়িত হতো, আর [মডেল rebuild-এর সময় দেওয়া namespace](#model-rebuild-semantics))
আর `{Bar.__name__: Bar}` namespace দুটোই যোগ করা হয়
(সবচেয়ে কম অগ্রাধিকারে) (1)।
{ .annotate }

1. পুরনো আচরণের সাথে সামঞ্জস্যের এই যুক্তি কিছু অসামঞ্জস্য তৈরি করতে পারে, যেমন নিচেরটি:

    ⟦CODE5⟧

## মডেল rebuild করার সময় annotation resolve করা { #resolving-annotations-when-rebuilding-a-model }

একটি forward reference মূল্যায়নে ব্যর্থ হলে, Pydantic চুপচাপ ব্যর্থ হয়ে core schema
তৈরির প্রক্রিয়া থামিয়ে দেয়। একটি মডেল ক্লাসের `__pydantic_core_schema__` পরীক্ষা করলে এটি দেখা যায়:

⟦CODE6⟧

এরপর `MyType` ঠিকভাবে সংজ্ঞায়িত করলে, মডেলটি rebuild করতে পারেন:

⟦CODE7⟧

[`model_rebuild()`][pydantic.BaseModel.model_rebuild] মেথড একটি *rebuild namespace* ব্যবহার করে, নিচের নিয়মে:
{% raw %}{#model-rebuild-semantics}{% endraw %}

* স্পষ্টভাবে একটি `_types_namespace` আর্গুমেন্ট দেওয়া হলে, সেটিই rebuild namespace হিসেবে ব্যবহার হয়।
* কোনো namespace দেওয়া না হলে, যে namespace থেকে মেথডটি ডাকা হয়েছে সেটিই rebuild namespace হিসেবে ব্যবহার হবে।

এই *rebuild namespace* মডেলের অভিভাবক namespace-এর (যদি ফাংশনে সংজ্ঞায়িত হয়ে থাকে) সাথে মিশিয়ে যেমন আছে তেমন ব্যবহার হবে
(দেখুন ওপরে বর্ণিত [পুরনো আচরণের সাথে সামঞ্জস্যের যুক্তি](#backwards-compatibility-logic))।

/// check | সংক্ষেপে মনে রাখুন

* স্ট্রিং annotation `eval()` দিয়ে মূল্যায়ন হয়: globals = ক্লাসের মডিউল; locals = ক্লাসের নাম → ক্লাসের ভেতর → যে ফাংশনে ক্লাসটি লেখা।
* না পাওয়া গেলে annotation স্ট্রিং থেকে যায় আর মডেল অসম্পূর্ণ থাকে (`MockCoreSchema`)।
* পরে নামটি সংজ্ঞায়িত করে `Model.model_rebuild()` ডাকুন, দরকারে `_types_namespace={...}` দিয়ে।
* ফাংশনের ভেতরে ক্লাস বানালে, ক্লাসের পরে সংজ্ঞায়িত নাম পরে আর পাওয়া যায় না।

///

[Mypy]: https://www.mypy-lang.org/
[Pyright]: https://github.com/microsoft/pyright/
[PEP 563]: https://peps.python.org/pep-0563/
[PEP 649]: https://peps.python.org/pep-0649/
[future statement]: https://docs.python.org/3/reference/simple_stmts.html#future

[^1]: এটি শর্তহীনভাবে করা হয়, কারণ [typing specification](https://typing.readthedocs.io/en/latest/spec/annotations.html#string-annotations) অনুযায়ী, forward annotation একটি type hint-এর *অংশ হিসেবেও* থাকতে পারে (যেমন `Optional['int']`)।

[^2]: এখানে একটি উদাহরণ:

    ⟦CODE8⟧
