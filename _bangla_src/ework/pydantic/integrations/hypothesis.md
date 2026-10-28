# Hypothesis { #hypothesis }

/// note | এই পেজে যা শিখবেন

Hypothesis (property-based testing লাইব্রেরি) কী, আর Pydantic V2-তে এর plugin-এর বর্তমান অবস্থা।

///

[Hypothesis](https://hypothesis.readthedocs.io/) হলো
[property-based testing](https://increment.com/testing/in-praise-of-property-based-testing/)-এর জন্য Python লাইব্রেরি।
টাইপ annotation দেওয়া ক্লাস কীভাবে তৈরি করতে হয় Hypothesis তা নিজে বুঝে নিতে পারে, আর ডিফল্টভাবে built-in টাইপ,
standard library-র অনেক টাইপ, আর
[`typing`](https://docs.python.org/3/library/typing.html) ও
[`typing_extensions`](https://pypi.org/project/typing-extensions/) মডিউলের generic টাইপ সমর্থন করে।

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ টেস্টে আপনি নিজে কয়েকটি ইনপুট বেছে দেন ("বয়স 25 দিলে কাজ করে কিনা")। property-based testing-এ আপনি একটি নিয়ম লেখেন ("যেকোনো বৈধ বয়সে কাজ করা উচিত"), আর Hypothesis শত শত এলোমেলো ইনপুট বানিয়ে পরীক্ষা করে, এমন কোণাকাঞ্চির ক্ষেত্রও যা আপনার মাথায় আসেনি।

///

Pydantic v2.0 Hypothesis-এর নিজস্ব সমর্থন বাদ দিয়েছে, আর আর সমন্বিত Hypothesis plugin-সহ আসে না।

/// warning | সতর্কতা

ভিন্ন একটি পদ্ধতি নিয়ে গবেষণার জন্য আমরা সাময়িকভাবে Hypothesis plugin সরিয়ে দিচ্ছি। আরও তথ্যের জন্য দেখুন issue [annotated-types/annotated-types#37](https://github.com/annotated-types/annotated-types/issues/37)।

ভবিষ্যতের কোনো রিলিজে Hypothesis plugin ফিরে আসতে পারে। হালনাগাদ খবরের জন্য [pydantic/pydantic#4682](https://github.com/pydantic/pydantic/issues/4682) subscribe করুন।

///
