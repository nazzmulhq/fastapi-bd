# Linting { #linting }

/// note | এই পেজে যা শিখবেন

Flake8-এর জন্য Pydantic plugin দিয়ে Pydantic কোডের প্রচলিত ভুল আগেভাগে ধরা।

///

## Flake8 plugin { #flake8-plugin }

আপনার প্রজেক্টে Flake8 ব্যবহার করলে, একটি [plugin](https://pypi.org/project/flake8-pydantic/) পাওয়া যায়,
যা নিচের মতো করে ইনস্টল করা যায়:

```bash
pip install flake8-pydantic
```

এই plugin-এর দেওয়া lint এররগুলো `PYDXXX` কোডের অধীনে থাকে। অপ্রয়োজনীয় কিছু নিয়ম উপেক্ষা করতে
Flake8 কনফিগারেশন এভাবে বদলানো যায়:

```ini
[flake8]
extend-ignore = PYD001,PYD002
```

/// tip | উদাহরণ দিয়ে বুঝি

linter হলো লেখার বানান-পরীক্ষক: কোড চালানোর আগেই বলে দেয় "এখানে Pydantic-এর নিয়মে সম্ভবত ভুল আছে"। কোনো নিয়ম আপনার প্রজেক্টে না খাটলে, তার কোড `extend-ignore`-এ যোগ করে বন্ধ রাখুন।

///
