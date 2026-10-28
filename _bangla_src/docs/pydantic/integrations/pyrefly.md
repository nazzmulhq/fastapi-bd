# Pyrefly { #pyrefly }

/// note | এই পেজে যা শিখবেন

Pyrefly type checker আর language server কীভাবে বাড়তি সেটআপ ছাড়াই Pydantic-এর বিশেষ নিয়ম বোঝে: IDE-তে সাহায্য আর কোড চালানোর আগেই এরর ধরা।

///

[Pyrefly](https://pyrefly.org/) একটি Python type checker আর language server, যাতে Pydantic-নির্দিষ্ট অনেক সুবিধার নিজস্ব সমর্থন আছে। Pydantic আর Pyrefly ইনস্টল থাকলেই এই সমর্থন কাজ করে, বাড়তি কোনো কনফিগারেশন লাগে না।

Pyrefly একটি [IDE extension](https://pyrefly.org/en/docs/IDE/) আর একটি [কমান্ড-লাইন type checker](https://pyrefly.org/en/docs/installation/) দুই রূপেই পাওয়া যায়।

## IDE extension { #ide-extension }

Pyrefly আপনার Pydantic মডেলে go-to-definition আর autocomplete-এর মতো IDE সুবিধা দেয়।

এখানে signature help-এর একটি উদাহরণ, যা Pyrefly-র Pydantic-নির্দিষ্ট `validation_alias` keyword বোঝার কারণে সম্ভব:

![Pyrefly IDE extension-এ signature help](../img/pyrefly.png)

`Model()` লেখার সময়, Pyrefly ইঙ্গিত দেয় যে `x` ফিল্ড পূরণ করতে আপনাকে `x_` নামটি ব্যবহার করতে হবে।

## Type checker { #type-checker }

কোড চালানোর আগেই Pyrefly আপনার কোডের এরর ধরতে পারে। নিচের উদাহরণটি দেখুন:

```python linenums="1"
from pydantic import BaseModel, ConfigDict


class Model1(BaseModel, frozen=True):
    x: int


class Model2(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int


model1 = Model1(x=0)
model1.x = 1  # validation error: mutating a frozen field

model2 = Model2(x=0)
model2.x = 1  # validation error: mutating a frozen field
```

`Model1` যেহেতু একটি [মানক টাইপ সিস্টেমের সুবিধা](https://typing.python.org/en/latest/spec/dataclasses.html#the-dataclass-transform-decorator) দিয়ে নিজেকে frozen ঘোষণা করে, আপনার পছন্দের যেকোনো type checker `model1.x` বদলানোর যাচাই এরর ধরবে। কিন্তু Pydantic-এর `ConfigDict` ক্লাসের বিশেষ সমর্থন নেই এমন type checker `model2.x` বদলানোর যাচাই এরর ধরতে পারবে না।

Pyrefly দুটো এররই ধরে:

```output
ERROR Cannot set field `x` [read-only]
  --> foo.py:11:1
   |
11 | model1.x = 1  # validation error: mutating a frozen field
   | ^^^^^^^^
   |
  This field belongs to a frozen Pydantic model
ERROR Cannot set field `x` [read-only]
  --> foo.py:14:1
   |
14 | model2.x = 1  # validation error: mutating a frozen field
   | ^^^^^^^^
   |
  This field belongs to a frozen Pydantic model
```

আরও তথ্যের জন্য দেখুন [Pyrefly ডকুমেন্টেশন](https://pyrefly.org/en/docs/pydantic/
)।
