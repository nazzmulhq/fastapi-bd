# ইনস্টলেশন { #installation }

/// note | এই পেজে যা জানবেন

* `pip` বা `uv` দিয়ে Pydantic ইনস্টল করা।
* Pydantic কোন কোন প্যাকেজের ওপর নির্ভর করে।
* ঐচ্ছিক বাড়তি অংশ (ইমেইল যাচাই, টাইমজোন) ইনস্টল করা।

///

ইনস্টল করা খুবই সহজ:

/// tab | pip

```bash
pip install pydantic
```

///

/// tab | uv

```bash
uv add pydantic
```

///

(কাজ শুরুর আগে একটি ভার্চুয়াল এনভায়রনমেন্ট তৈরি করে নেওয়া ভালো। কীভাবে, তা দেখুন [ভার্চুয়াল এনভায়রনমেন্ট](../virtual-environments.md) পেজে। আর FastAPI ইনস্টল করে থাকলে Pydantic ইতিমধ্যেই সাথে চলে এসেছে।)

Pydantic-এর কয়েকটি ডিপেন্ডেন্সি (যেসব প্যাকেজ ছাড়া এটি চলে না) আছে:

* [`pydantic-core`](https://pypi.org/project/pydantic-core/): Rust-এ লেখা Pydantic-এর মূল যাচাইয়ের যুক্তি।
* [`typing-extensions`](https://pypi.org/project/typing-extensions/): স্ট্যান্ডার্ড লাইব্রেরির [typing][] মডিউলের নতুন ফিচারগুলো পুরনো Python সংস্করণেও আনার ব্যাকপোর্ট।
* [`annotated-types`](https://pypi.org/project/annotated-types/): [`typing.Annotated`][]-এর সাথে ব্যবহারের জন্য পুনরায় ব্যবহারযোগ্য শর্তের টাইপ (যেমন "০-এর চেয়ে বড়")।
* [`typing-inspection`](https://pypi.org/project/typing-inspection/): চলমান অবস্থায় টাইপ পরীক্ষা করার টুল।

আপনার কাছে Python 3.10+ আর `pip` থাকলেই চলবে।

Pydantic [conda](https://www.anaconda.com)-তেও [conda-forge](https://conda-forge.org)
চ্যানেলে পাওয়া যায়:

```bash
conda install pydantic -c conda-forge
```

## ঐচ্ছিক ডিপেন্ডেন্সি { #optional-dependencies }

Pydantic-এর নিচের ঐচ্ছিক ডিপেন্ডেন্সিগুলো আছে:

* `email`: [email-validator](https://pypi.org/project/email-validator/) প্যাকেজের মাধ্যমে ইমেইল যাচাই (যেমন `EmailStr` টাইপ ব্যবহারের জন্য)।
* `timezone`: [tzdata](https://pypi.org/project/tzdata/) প্যাকেজের মাধ্যমে বিকল্প IANA টাইমজোন ডেটাবেস (যে কম্পিউটারে টাইমজোনের তথ্য নেই, যেমন Windows, সেখানে কাজে লাগে)।

Pydantic-এর সাথে ঐচ্ছিক ডিপেন্ডেন্সি ইনস্টল করতে:

/// tab | pip

```bash
# with the `email` extra:
pip install 'pydantic[email]'
# or with `email` and `timezone` extras:
pip install 'pydantic[email,timezone]'
```

///

/// tab | uv

```bash
# with the `email` extra:
uv add 'pydantic[email]'
# or with `email` and `timezone` extras:
uv add 'pydantic[email,timezone]'
```

///

অবশ্যই, `pip install email-validator tzdata` দিয়ে নিজে হাতেও এগুলো ইনস্টল করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

`pydantic[email]`-এর বর্গবন্ধনীর অংশটিকে "extras" বলে। এটা অনেকটা ফোন কেনার সময় "চার্জার সহ" বেছে নেওয়ার মতো: মূল প্যাকেজের সাথে বাড়তি জিনিসও একসাথে চলে আসে।

///

## রিপোজিটরি থেকে ইনস্টল { #install-from-repository }

আর যদি সরাসরি রিপোজিটরি থেকে (একদম সর্বশেষ, এখনো প্রকাশিত হয়নি এমন কোড) Pydantic ইনস্টল করতে চান:

/// tab | pip

```bash
pip install 'git+https://github.com/pydantic/pydantic@main'
# or with `email` and `timezone` extras:
pip install 'git+https://github.com/pydantic/pydantic@main#egg=pydantic[email,timezone]'
```

///

/// tab | uv

```bash
uv add 'git+https://github.com/pydantic/pydantic@main'
# or with `email` and `timezone` extras:
uv add 'git+https://github.com/pydantic/pydantic@main#egg=pydantic[email,timezone]'
```

///

/// warning | সতর্কতা

রিপোজিটরির `main` শাখার কোড এখনো পরীক্ষাধীন হতে পারে। শেখা আর আসল প্রজেক্টের জন্য PyPI-র প্রকাশিত সংস্করণই (`pip install pydantic`) ব্যবহার করুন।

///

/// check | সংক্ষেপে মনে রাখুন

* `pip install pydantic` বা `uv add pydantic`, ব্যস।
* ইমেইল যাচাই লাগলে `pydantic[email]`, টাইমজোন ডেটা লাগলে `pydantic[timezone]`।
* Python 3.10 বা নতুন সংস্করণ লাগবে।

///
