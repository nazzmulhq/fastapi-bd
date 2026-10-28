# devtools { #devtools }

/// note | এই পেজে যা শিখবেন

python-devtools-এর `debug()` দিয়ে Pydantic মডেল সুন্দর, রঙিন আর পড়ার উপযোগী করে দেখা, ফাইল আর লাইন নম্বরসহ।

///

/// note | স্বীকারোক্তি

**স্বীকারোক্তি:** আমি (Pydantic-এর প্রধান ডেভেলপার) python-devtools-ও তৈরি করি।

///

[python-devtools](https://python-devtools.helpmanual.io/) (`pip install devtools`) Python ডেভেলপমেন্টের সময় কাজে লাগে এমন
কয়েকটি টুল দেয়, যার মধ্যে আছে `debug()`, `print()`-এর একটি বিকল্প যা আউটপুট এমনভাবে সাজায় যে
`print`-এর চেয়ে পড়া সহজ হওয়ার কথা, সাথে জানায় print স্টেটমেন্টটি কোন ফাইল/লাইনে
আছে আর কোন মান print হলো।

বেশিরভাগ প্রকাশ্য ক্লাসে `__pretty__` মেথড বাস্তবায়ন করে Pydantic *devtools*-এর সাথে যুক্ত হয়।

বিশেষ করে মডেল পরীক্ষার সময় `debug()` কাজে লাগে:

⟦CODE1⟧

আপনার টার্মিনালে আউটপুট আসবে:

⟦CODE2⟧

should be much easier read than:

user: id=123 name='John Doe' signup_ts=datetime.datetime(2019, 6, 1, 12, 22) friends=[1234, 4567, 7890] address=Address(street='Testing', country='uk', lat=51.5, lng=0.0)</code></pre>
</div>

/// info | আউটপুটটি সহজ ভাষায়

ওপরের অংশটি `debug(user)`-এর আউটপুট: কোন ফাইলের কোন লাইন (`devtools_example.py:30`), তারপর প্রতিটি ফিল্ড আলাদা লাইনে, রঙসহ। নিচের এক লম্বা লাইনটি সাধারণ `print()`-এর আউটপুট; বড় মডেলে এটি পড়া অনেক কঠিন।

///

`debug()` হলো ডেভেলপমেন্টের সময়ের টুল: এটি আপনি যে প্রসেসটি দেখছেন তার টার্মিনালে print করে। চালু (deploy করা)
অ্যাপ্লিকেশনের জন্য এর সবচেয়ে কাছের বিকল্প হলো [Logfire](logfire.md), যেখানে মডেল আর যাচাই
গোছানো আউটপুট হিসেবে দেখা যায়, যা ঘুরে দেখা আর query করা যায়।
