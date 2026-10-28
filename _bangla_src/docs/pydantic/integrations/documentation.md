# ডকুমেন্টেশন { #documentation }

/// note | এই পেজে যা শিখবেন

নিজের প্রজেক্টের ডকুমেন্টেশনে (Sphinx বা MkDocs) Pydantic-এর ক্লাস আর ফাংশনের নাম লিখলে সেগুলো যাতে স্বয়ংক্রিয়ভাবে Pydantic-এর অফিসিয়াল ডকসের লিংক হয়ে যায়।

///

Pydantic ডকুমেন্টেশনের জন্য [MkDocs](https://www.mkdocs.org/) ব্যবহার করে,
[mkdocstrings](https://mkdocstrings.github.io/)-এর সাথে। ফলে Pydantic API ডকুমেন্টেশন cross-reference করতে
Pydantic-এর Sphinx object inventory ব্যবহার করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

inventory হলো একটি লাইব্রেরির সূচিপত্র: কোন নাম (`pydantic.BaseModel`) কোন পাতায় আছে। আপনার ডকস সেই সূচিপত্র পড়ে নিলে, আপনি শুধু নামটি লিখলেই সঠিক পাতার লিংক তৈরি হয়ে যায়।

///

/// tab | Sphinx

আপনার [Sphinx কনফিগারেশনে](https://www.sphinx-doc.org/en/master/usage/configuration.html),
[`intersphinx` extension কনফিগারেশনে](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration) নিচেরটি যোগ করুন:

```python
intersphinx_mapping = {
    'pydantic': ('https://pydantic.dev/docs/validation/latest', None),  # (1)!
}
```

1. সর্বশেষ ডকুমেন্টেশন build-কে লক্ষ্য করতে `latest`-এর বদলে `dev`-ও ব্যবহার করতে পারেন, যা
   [`main`](https://github.com/pydantic/pydantic/tree/main) branch-এর সাথে হালনাগাদ থাকে।

///

/// tab | mkdocstrings

আপনার [MkDocs কনফিগারেশনে](https://www.mkdocs.org/user-guide/configuration/), আপনার
[mkdocstrings plugin কনফিগারেশনে](https://mkdocstrings.github.io/usage/#cross-references-to-other-projects-inventories) নিচের import যোগ করুন:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        import:
        - https://pydantic.dev/docs/validation/latest/objects.inv  # (1)!
```

1. সর্বশেষ ডকুমেন্টেশন build-কে লক্ষ্য করতে `latest`-এর বদলে `dev`-ও ব্যবহার করতে পারেন, যা
   [`main`](https://github.com/pydantic/pydantic/tree/main) branch-এর সাথে হালনাগাদ থাকে।

///
