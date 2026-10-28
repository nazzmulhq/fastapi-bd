# Rich { #rich }

/// note | এই পেজে যা শিখবেন

Rich লাইব্রেরি দিয়ে টার্মিনালে Pydantic মডেল রঙিন আর সুন্দর করে দেখানো।

///

Pydantic মডেল [Rich](https://github.com/Textualize/rich) লাইব্রেরি দিয়ে print করা যায়, যা আউটপুটে বাড়তি বিন্যাস আর রং যোগ করে। এখানে একটি উদাহরণ:

![Rich দিয়ে Pydantic মডেল print করা](../img/rich_pydantic.png)

```python
from rich import print

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    tags: list[str] = []


print(User(id=1, name='রহিম', tags=['admin', 'staff']))  # রঙিন, গোছানো আউটপুট
```

আরও তথ্যের জন্য দেখুন [pretty printing](https://rich.readthedocs.io/en/latest/pretty.html) নিয়ে Rich ডকুমেন্টেশন।
