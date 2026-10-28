# Forward Annotations { #forward-annotations }

/// note | এই পেজে যা শিখবেন

* forward annotation কী: এখনো সংজ্ঞায়িত হয়নি এমন টাইপের নাম annotation-এ লেখা।
* Python 3.14+ আর পুরনো সংস্করণে আচরণের পার্থক্য।
* নিজেকেই উল্লেখ করে এমন (recursive) মডেল, যেমন গাছ বা মন্তব্যের উত্তর।
* দুই ফাইলের মডেল একে অপরকে উল্লেখ করলে (cyclic import) কী করবেন।

///

/// tip | উদাহরণ দিয়ে বুঝি

ধরুন একটি বইয়ের প্রথম অধ্যায়ে লেখা আছে "বিস্তারিত দেখুন অধ্যায় ৫-এ"। পাঠক তখনো অধ্যায় ৫ পড়েননি, তবু উল্লেখটি ঠিক আছে, কারণ পরে খুঁজে নেওয়া যাবে। forward annotation ঠিক এমন: "এই টাইপের নাম এখন লিখছি, আসল সংজ্ঞা পরে পাবে।" Pydantic পরে নামটি খুঁজে বের করে (resolve করে)।

///

## Python 3.14 ও তার ওপরে { #python-314-and-greater }

Python 3.14 থেকে Python আর annotation *সাথে সাথে* (eagerly) মূল্যায়ন করে না, অর্থাৎ annotation লেখার সময়
এখনো সংজ্ঞায়িত হয়নি এমন অবজেক্টও উল্লেখ করতে পারেন:

```python
from typing import Any

from pydantic import BaseModel


def outer():
    def inner():
        class Model(BaseModel):
            ann: List[Dict[Any, int]]

        Dict = dict

        return Model

    List = list

    Model = inner()

    return Model


Model = outer()

Model(ann=[{'key': '1'}])
#> Model(ann=[{'key': 1}])
```

/// info | কোডটি সহজ ভাষায়

`Model` লেখার সময় `List` আর `Dict` নামগুলো তখনো তৈরি হয়নি, পরে তৈরি হয়েছে। Python 3.14-এ annotation পরে মূল্যায়ন হয়, আর Pydantic ঠিক জায়গা থেকে নামগুলো খুঁজে পায়। তাই `'1'` যাচাই হয়ে `1` হলো।

///

## Python 3.13 ও তার নিচে { #python-313-and-lower }

Python 3.14-এর আগের সংস্করণে, এখনো সংজ্ঞায়িত হয়নি এমন অবজেক্টের উল্লেখ forward annotation হিসেবে
(উদ্ধৃতিচিহ্নের ভেতরে) লিখতে হয়, অথবা `from __future__ import annotations` [future statement] ব্যবহার করতে হয়
([PEP563](https://www.python.org/dev/peps/pep-0563/)-এ যেমন চালু হয়েছিল):

```python
from __future__ import annotations

from pydantic import BaseModel


class Model(BaseModel):
    a: MyInt
    # Without the future import, equivalent to:
    # a: 'MyInt'


MyInt = int


print(Model(a='1'))
#> a=1
```

forward annotation resolve করার ভেতরের নিয়ম বিস্তারিত বলা আছে [এই অংশে](../internals/resolving_annotations.md)।

## নিজেকে উল্লেখ করা (বা "Recursive") মডেল { #self-referencing-or-recursive-models }

নিজেকেই উল্লেখ করে এমন ফিল্ডওয়ালা মডেলও সমর্থিত। মডেল তৈরির সময়েই এই annotation-গুলো resolve হয়।

/// tab | Python 3.10 ও তার ওপরে

```python
from pydantic import BaseModel


class Foo(BaseModel):
    a: int = 123
    sibling: 'Foo | None' = None  # (1)!


print(Foo())
#> a=123 sibling=None
print(Foo(sibling={'a': '321'}))
#> a=123 sibling=Foo(a=321, sibling=None)
```

1. `Foo` মডেল সংজ্ঞায়িত হওয়ার সময়েই Python annotation প্রক্রিয়া করে (তখনো এটি পুরোপুরি সংজ্ঞায়িত হয়নি)। তাই
   `Foo` annotation resolve করা যায় না, আর এটিকে forward annotation হিসেবে লিখতে হয়।

///

/// tab | Python 3.14 ও তার ওপরে

```python
from pydantic import BaseModel


class Foo(BaseModel):
    a: int = 123
    sibling: Foo | None = None


print(Foo())
#> a=123 sibling=None
print(Foo(sibling={'a': '321'}))
#> a=123 sibling=Foo(a=321, sibling=None)
```

///

/// tip | কোথায় কাজে লাগে

গাছের মতো গঠন: ফোল্ডারের ভেতর ফোল্ডার, মন্তব্যের উত্তরের উত্তর, কোম্পানির কর্মচারী আর তার ম্যানেজার (যিনিও একজন কর্মচারী)। যেমন `children: list['Category'] = []`।

///

## Cyclic import { #cyclic-imports }

যখন একে অপরকে উল্লেখ করে এমন মডেল আলাদা মডিউলে (ফাইলে) সংজ্ঞায়িত হয়, তখন এক মডিউল থেকে অন্যটির মডেল
ইম্পোর্ট করলে cyclic import হয়: প্রতিটি মডিউলের দরকার অন্যটি আগে পুরোপুরি ইম্পোর্ট হওয়া।

/// tip | উদাহরণ দিয়ে বুঝি

দুই বন্ধু দরজায় দাঁড়িয়ে বলছেন "আপনি আগে যান", "না, আপনি আগে"। কেউই ঢুকতে পারছেন না। সমাধান হলো একজনকে বলা "আপনি আগে ঢুকুন, আমি পরিচয়টা পরে দিচ্ছি"।

///

/// tab | Python 3.15 ও তার ওপরে

Python 3.15-এ এসেছে [lazy import](https://docs.python.org/3.15/reference/simple_stmts.html#lazy),
যেখানে `lazy` keyword আসল ইম্পোর্টকে পিছিয়ে দেয় যতক্ষণ না ইম্পোর্ট করা নামটি প্রথমবার ব্যবহার হয়। Pydantic-এ
lazy import সমর্থিত, আর এটি দিয়ে চক্রটি ভাঙা যায়:

```python title="a.py"
lazy from .b import B

from pydantic import BaseModel


class A(BaseModel):
    b: B | None = None
```

```python title="b.py"
lazy from .a import A

from pydantic import BaseModel


class B(BaseModel):
    a: A | None = None
```

///

/// tab | Python 3.14 ও তার নিচে

আগের সংস্করণগুলোর জন্য প্রস্তাবিত উপায় হলো মডেলগুলোর একটিকে শুধু একটি
[`if TYPE_CHECKING:`][typing.TYPE_CHECKING] ব্লকের ভেতরে ইম্পোর্ট করা, আর forward annotation দিয়ে সেটি উল্লেখ করা:

```python title="a.py"
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from .b import B


class A(BaseModel):
    b: 'B | None' = None
```

```python title="b.py"
from pydantic import BaseModel

from .a import A


class B(BaseModel):
    a: A | None = None
```

`a.py`-তে চলার সময় (runtime) `B` পাওয়া যায় না বলে `A` মডেল অসম্পূর্ণ থাকে। একটি অভিভাবক মডিউলে
(যেমন প্যাকেজের `__init__.py`), দুটো মডেলই ইম্পোর্ট করে অসম্পূর্ণটির ওপর
[`model_rebuild()`][pydantic.BaseModel.model_rebuild] ডাকুন। যেহেতু `B` ডাকা মডিউলের
scope-এ আছে, forward annotation resolve হয়ে যায়:

```python title="__init__.py"
from .a import A
from .b import B

__all__ = ('A', 'B')

A.model_rebuild()
```

///

/// warning | সাধারণ ভুল

`model_rebuild()` না ডেকে অসম্পূর্ণ মডেল ব্যবহার করলে Pydantic এরর দেয় যে মডেলটি "not fully defined"। এরর বার্তায় কোন নাম পাওয়া যায়নি তা বলা থাকে; সেই নামটি scope-এ এনে `model_rebuild()` ডাকুন।

///

[future statement]: https://docs.python.org/3/reference/simple_stmts.html#future

/// check | সংক্ষেপে মনে রাখুন

* Python 3.14+-এ পরে সংজ্ঞায়িত নাম সরাসরি লেখা যায়।
* পুরনো সংস্করণে নামটি উদ্ধৃতিচিহ্নে (`'Foo'`) লিখুন বা `from __future__ import annotations` দিন।
* recursive মডেল: `sibling: 'Foo | None' = None`।
* দুই ফাইলের চক্র: একটিতে `if TYPE_CHECKING:` ইম্পোর্ট, পরে `A.model_rebuild()`; Python 3.15+-এ `lazy from ... import ...`।

///
