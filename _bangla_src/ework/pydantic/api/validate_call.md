# Validate Call { #validate-call }

/// note | এই পেজে যা পাবেন

* `@validate_call` decorator-এর প্যারামিটার আর একটি উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

`@validate_call` একটি সাধারণ ফাংশনের আর্গুমেন্টগুলো ফাংশন চলার আগেই তার টাইপ annotation অনুযায়ী যাচাই আর রূপান্তর করে। ধারণা বিস্তারিত: [Validation Decorator](../concepts/validation_decorator.md)।

| প্যারামিটার | ডিফল্ট | কী করে |
| --- | --- | --- |
| `func` | | যে ফাংশন decorate হবে (প্যারামিটার ছাড়া `@validate_call` লিখলে নিজে থেকে) |
| `config` | `None` | `ConfigDict`, যেমন `ConfigDict(strict=True)` বা `arbitrary_types_allowed=True` |
| `validate_return` | `False` | `True` হলে ফেরত মানও ফেরত টাইপ অনুযায়ী যাচাই হয় |

```python
from typing import Annotated

from pydantic import Field, ValidationError, validate_call


@validate_call
def add(a: int, b: Annotated[int, Field(gt=0)] = 1) -> int:
    return a + b


print(add('2', 3))
#> 5
try:
    add(1, 0)
except ValidationError as e:
    print(e.errors()[0]['type'], e.errors()[0]['loc'])
    #> greater_than (1,)
```

`loc`-এর `(1,)` মানে দ্বিতীয় (index 1) positional আর্গুমেন্টে সমস্যা।

/// check | সংক্ষেপে মনে রাখুন

* `@validate_call` বা `@validate_call(config=..., validate_return=True)`।
* ব্যর্থ হলে `ValidationError`; মূল ফাংশন `func.raw_function`-এ।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
