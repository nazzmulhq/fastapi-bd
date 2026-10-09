# ক্লাসকে ডিপেন্ডেন্সি হিসেবে ব্যবহার { #classes-as-dependencies }

/// note | এই পেজে যা শিখবেন

* "callable" (ডাকা যায় এমন জিনিস) কী, আর কেন একটি ক্লাসও ডিপেন্ডেন্সি হতে পারে।
* ডিকশনারির বদলে ক্লাস ব্যবহার করে এডিটরের ভালো সাহায্য পাওয়া।
* `Depends()` শর্টকাট, যাতে ক্লাসের নাম দুবার লিখতে না হয়।

///

**ডিপেন্ডেন্সি ইনজেকশন** ব্যবস্থার আরও গভীরে যাওয়ার আগে, আগের উদাহরণটি একটু উন্নত করা যাক।

## আগের উদাহরণের একটি `dict` { #a-dict-from-the-previous-example }

আগের উদাহরণে আমরা আমাদের ডিপেন্ডেন্সি ("dependable") থেকে একটি `dict` ফেরত দিচ্ছিলাম:

{* ../../docs_src/dependencies/tutorial001_an_py310.py hl[9] *}

কিন্তু তাহলে *পাথ অপারেশন ফাংশনের* `commons` প্যারামিটারে আমরা একটি `dict` পাই।

আর আমরা জানি যে এডিটরগুলো `dict`-এর জন্য তেমন সাহায্য (যেমন কমপ্লিশন) দিতে পারে না, কারণ এর কী আর মানের টাইপগুলো এডিটর জানতে পারে না। `commons["limt"]` লিখে ফেললে কেউ ভুল ধরবে না।

আমরা আরও ভালো করতে পারি...

## কোনটা ডিপেন্ডেন্সি হতে পারে { #what-makes-a-dependency }

এখন পর্যন্ত আপনি ফাংশন হিসেবে ঘোষিত ডিপেন্ডেন্সি দেখেছেন।

কিন্তু ডিপেন্ডেন্সি ঘোষণার এটাই একমাত্র উপায় নয় (যদিও সম্ভবত সবচেয়ে প্রচলিত)।

মূল বিষয় হলো, একটি ডিপেন্ডেন্সিকে একটি "callable" হতে হবে।

Python-এ একটি "**callable**" হলো এমন যেকোনো কিছু, যা Python একটি ফাংশনের মতো "ডাকতে" পারে।

তাই আপনার যদি একটি অবজেক্ট `something` থাকে (যা হয়তো একটি ফাংশন _নয়_), আর আপনি এটিকে এভাবে "ডাকতে" (চালাতে) পারেন:

```Python
something()
```

অথবা

```Python
something(some_argument, some_keyword_argument="foo")
```

তাহলে এটি একটি "callable"।

## ক্লাসকে ডিপেন্ডেন্সি হিসেবে ব্যবহার { #classes-as-dependencies_1 }

হয়তো খেয়াল করবেন যে একটি Python ক্লাসের ইনস্ট্যান্স তৈরি করতেও ঠিক এই একই সিনট্যাক্স ব্যবহার হয়।

যেমন:

⟦CODE1⟧

এই ক্ষেত্রে `fluffy` হলো `Cat` ক্লাসের একটি ইনস্ট্যান্স।

আর `fluffy` তৈরি করতে আপনি `Cat`-কে "ডাকছেন"।

তাই একটি Python ক্লাসও একটি **callable**।

তাহলে **FastAPI**-তে একটি Python ক্লাসকে ডিপেন্ডেন্সি হিসেবে ব্যবহার করতে পারেন।

FastAPI আসলে যা যাচাই করে তা হলো এটি একটি "callable" কিনা (ফাংশন, ক্লাস বা অন্য যেকোনো কিছু), আর এতে কী কী প্যারামিটার সংজ্ঞায়িত আছে।

**FastAPI**-তে ডিপেন্ডেন্সি হিসেবে একটি "callable" দিলে, এটি ওই "callable"-এর প্যারামিটারগুলো বিশ্লেষণ করবে, আর একটি *পাথ অপারেশন ফাংশনের* প্যারামিটারের মতোই সেগুলো প্রসেস করবে। সাব-ডিপেন্ডেন্সিসহ।

এটি কোনো প্যারামিটারই নেই এমন callable-এর ক্ষেত্রেও প্রযোজ্য। ঠিক প্যারামিটারবিহীন *পাথ অপারেশন ফাংশনের* মতো।

তাহলে ওপরের ডিপেন্ডেন্সি "dependable" `common_parameters`-কে আমরা `CommonQueryParams` ক্লাসে বদলে দিতে পারি:

{* ../../docs_src/dependencies/tutorial002_an_py310.py hl[11:15] *}

ক্লাসের ইনস্ট্যান্স তৈরিতে ব্যবহৃত `__init__` মেথডটির দিকে খেয়াল করুন:

{* ../../docs_src/dependencies/tutorial002_an_py310.py hl[12] *}

...এর প্যারামিটারগুলো আমাদের আগের `common_parameters`-এর মতোই:

{* ../../docs_src/dependencies/tutorial001_an_py310.py hl[8] *}

ডিপেন্ডেন্সিটি "সমাধান" করতে **FastAPI** ওই প্যারামিটারগুলোই ব্যবহার করবে।

দুই ক্ষেত্রেই থাকবে:

* একটি ঐচ্ছিক `q` কুয়েরি প্যারামিটার, যা একটি `str`।
* একটি `skip` কুয়েরি প্যারামিটার, যা একটি `int`, ডিফল্ট `0`।
* একটি `limit` কুয়েরি প্যারামিটার, যা একটি `int`, ডিফল্ট `100`।

দুই ক্ষেত্রেই ডেটা রূপান্তর, যাচাই, OpenAPI স্কিমাতে ডকুমেন্ট ইত্যাদি হবে।

/// info | `__init__` সহজ ভাষায়

`__init__` হলো ক্লাসের "জন্মের সময়ের" ফাংশন। `CommonQueryParams(q="book", skip=0, limit=10)` লিখলে Python স্বয়ংক্রিয়ভাবে `__init__` চালায়, আর `self.q = q` এর মতো লাইনগুলো মানগুলো নতুন অবজেক্টের ভেতরে রেখে দেয়। পরে `commons.q`, `commons.skip` দিয়ে সেগুলো পাওয়া যায়।

///

## এটি ব্যবহার করুন { #use-it }

এবার এই ক্লাস দিয়ে আপনার ডিপেন্ডেন্সি ঘোষণা করতে পারেন।

{* ../../docs_src/dependencies/tutorial002_an_py310.py hl[19] *}

**FastAPI** `CommonQueryParams` ক্লাসটি ডাকে। এতে ওই ক্লাসের একটি "ইনস্ট্যান্স" তৈরি হয়, আর সেই ইনস্ট্যান্সটি আপনার ফাংশনে `commons` প্যারামিটার হিসেবে পাঠানো হয়।

/// info | কোডটি সহজ ভাষায় (লাইন ১৯-২৫)

* `commons` এখন একটি `CommonQueryParams` অবজেক্ট, ডিকশনারি নয়।
* তাই `commons.q`, `commons.skip`, `commons.limit` ডট দিয়ে পাওয়া যায়, আর এডিটর এগুলোর নাম আর টাইপ জানে।
* লাইন ২৩: নকল ডেটাবেস থেকে `skip` আর `limit` অনুযায়ী আইটেম কেটে নেওয়া হচ্ছে।

///

## টাইপ অ্যানোটেশন বনাম `Depends` { #type-annotation-vs-depends }

খেয়াল করুন, ওপরের কোডে আমরা `CommonQueryParams` দুবার লিখছি:

//// tab | Python 3.10+

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

////

শেষের `CommonQueryParams`, এখানে:

```Python
... Depends(CommonQueryParams)
```

...ডিপেন্ডেন্সিটি কী তা জানতে **FastAPI** আসলে এটিই ব্যবহার করবে।

FastAPI এটি থেকেই ঘোষিত প্যারামিটারগুলো বের করবে, আর FastAPI আসলে এটিকেই ডাকবে।

---

এই ক্ষেত্রে প্রথম `CommonQueryParams`, এখানে:

//// tab | Python 3.10+

```Python
commons: Annotated[CommonQueryParams, ...
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons: CommonQueryParams ...
```

////

...এর **FastAPI**-এর কাছে কোনো বিশেষ অর্থ নেই। FastAPI এটি ডেটা রূপান্তর, যাচাই ইত্যাদির জন্য ব্যবহার করবে না (কারণ এর জন্য এটি `Depends(CommonQueryParams)` ব্যবহার করছে)।

আসলে আপনি শুধু এটুকুও লিখতে পারতেন:

//// tab | Python 3.10+

```Python
commons: Annotated[Any, Depends(CommonQueryParams)]
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons = Depends(CommonQueryParams)
```

////

...যেমন এখানে:

{* ../../docs_src/dependencies/tutorial003_an_py310.py hl[19] *}

তবে টাইপ ঘোষণা করতে উৎসাহিত করা হয়, কারণ এতে আপনার এডিটর জানবে `commons` প্যারামিটার হিসেবে কী আসবে, আর তখন কোড কমপ্লিশন, টাইপ যাচাই ইত্যাদিতে সাহায্য করতে পারবে:

<img src="/img/tutorial/dependencies/image02.png">

/// tip | সহজ কথায়

* প্রথম `CommonQueryParams` (টাইপ) = এডিটরের জন্য, যাতে সে বোঝে `commons` কী জিনিস।
* দ্বিতীয় `CommonQueryParams` (`Depends`-এর ভেতরে) = FastAPI-এর জন্য, যাতে সে জানে কী চালাতে হবে।

///

## শর্টকাট { #shortcut }

কিন্তু দেখছেন যে এখানে কোডের কিছু পুনরাবৃত্তি হচ্ছে, `CommonQueryParams` দুবার লেখা হচ্ছে:

//// tab | Python 3.10+

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

////

যেসব ক্ষেত্রে ডিপেন্ডেন্সিটি *নির্দিষ্টভাবে* একটি ক্লাস, যাকে **FastAPI** "ডেকে" ওই ক্লাসেরই একটি ইনস্ট্যান্স তৈরি করবে, সেসব ক্ষেত্রের জন্য **FastAPI** একটি শর্টকাট দেয়।

ওই নির্দিষ্ট ক্ষেত্রগুলোর জন্য আপনি এভাবে করতে পারেন:

এটা লেখার বদলে:

//// tab | Python 3.10+

```Python
commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons: CommonQueryParams = Depends(CommonQueryParams)
```

////

...লিখুন:

//// tab | Python 3.10+

```Python
commons: Annotated[CommonQueryParams, Depends()]
```

////

//// tab | Python 3.10+ Annotated ছাড়া

/// tip | পরামর্শ

সম্ভব হলে `Annotated` সংস্করণটি ব্যবহার করুন।

///

```Python
commons: CommonQueryParams = Depends()
```

////

আপনি ডিপেন্ডেন্সিটি প্যারামিটারের টাইপ হিসেবে ঘোষণা করেন, আর `Depends(CommonQueryParams)`-এর ভেতরে পুরো ক্লাসটি *আবার* লেখার বদলে কোনো প্যারামিটার ছাড়া `Depends()` ব্যবহার করেন। খালি `Depends()` দেখলে FastAPI টাইপটিকেই ডিপেন্ডেন্সি হিসেবে ধরে নেয়।

তাহলে একই উদাহরণ দেখতে এমন হবে:

{* ../../docs_src/dependencies/tutorial004_an_py310.py hl[19] *}

...আর **FastAPI** জানবে কী করতে হবে।

/// tip | পরামর্শ

এটা যদি সাহায্যের চেয়ে বেশি বিভ্রান্তিকর মনে হয়, তাহলে উপেক্ষা করুন, এটি আপনার *দরকার* নেই।

এটি শুধু একটি শর্টকাট। কারণ **FastAPI** আপনাকে কোডের পুনরাবৃত্তি কমাতে সাহায্য করতে চায়।

///

/// check | সংক্ষেপে মনে রাখুন

* ডাকা যায় এমন যেকোনো কিছু (ফাংশন বা ক্লাস) ডিপেন্ডেন্সি হতে পারে।
* ক্লাস ব্যবহার করলে `__init__`-এর প্যারামিটারগুলোই কুয়েরি প্যারামিটার হয়ে যায়, আর ফলাফল একটি অবজেক্ট, যা নিয়ে এডিটর ভালো সাহায্য করে।
* শর্টকাট: `commons: Annotated[CommonQueryParams, Depends()]`।

///
