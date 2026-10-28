# ISBN { #isbn }

/// note | এই পেজে যা পাবেন

* `pydantic-extra-types` প্যাকেজের এই অংশের টাইপগুলো: বইয়ের ISBN নম্বর (ISBN-10 বা ISBN-13), check digit পরীক্ষাসহ।
* প্রতিটি টাইপের ব্যাখ্যা আর একটি উদাহরণ (আউটপুটসহ)।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

এই টাইপগুলো মূল Pydantic-এ নেই, আলাদা প্যাকেজে আছে: `pip install pydantic-extra-types` (কোনো বাড়তি dependency নেই; সব একসাথে পেতে `pip install "pydantic-extra-types[all]"`)।

| টাইপ | কী করে |
| --- | --- |
| `ISBN` | ISBN-10 বা ISBN-13 গ্রহণ করে; ISBN-10 দিলে ISBN-13-এ রূপান্তর করে রাখে। হাইফেন ছাড়া অঙ্ক দিন |

## উদাহরণ { #bn-example }

```python
from pydantic import BaseModel
from pydantic_extra_types.isbn import ISBN


class Book(BaseModel):
    isbn: ISBN


print(Book(isbn='0306406152').isbn)  # ISBN-10 → ISBN-13
#> 9780306406157
```

/// tip | পরামর্শ

`"0-306-40615-2"` এর মতো হাইফেনসহ লেখা এরর দেয়; দরকারে আগে একটি `BeforeValidator` দিয়ে `-` সরিয়ে নিন।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic_extra_types.isbn
    options:
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true
