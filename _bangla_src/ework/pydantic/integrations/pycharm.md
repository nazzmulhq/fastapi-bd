# PyCharm { #pycharm }

/// note | এই পেজে যা শিখবেন

PyCharm-এ Pydantic plugin কী সুবিধা দেয় আর কীভাবে ইনস্টল করবেন।

///

pydantic বাড়তি সেটআপ ছাড়াই যেকোনো IDE-তে ভালো কাজ করলেও, উন্নত pydantic integration দেয় এমন একটি
[PyCharm plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)
PyCharm-এর জন্য JetBrains Plugins Repository-তে পাওয়া যায়।
plugin marketplace থেকে plugin-টি বিনামূল্যে ইনস্টল করতে পারেন
(PyCharm-এর Preferences -> Plugin -> Marketplace -> "pydantic" খুঁজুন)।

plugin-টি এখন নিচের সুবিধাগুলো সমর্থন করে:

* `pydantic.BaseModel.__init__`-এর জন্য:
    * পরিদর্শন (inspection)
    * স্বয়ংক্রিয় পূরণ (autocompletion)
    * টাইপ-পরীক্ষা

* `pydantic.BaseModel`-এর ফিল্ডের জন্য:
    * refactor করে ফিল্ডের নাম বদলালে `__init__` ডাকগুলোও হালনাগাদ হয়, আর sub- ও super-class-এও প্রভাব ফেলে
    * refactor করে `__init__`-এর keyword আর্গুমেন্টের নাম বদলালে ফিল্ডের নামও হালনাগাদ হয়, আর sub- ও super-class-এও প্রভাব ফেলে

/// tip | উদাহরণ দিয়ে বুঝি

plugin ছাড়া PyCharm `User(na` লিখলে জানে না যে `name=` প্রস্তাব করতে হবে। plugin থাকলে মডেলের ফিল্ডগুলো `__init__`-এর আর্গুমেন্ট হিসেবে চেনে, তাই autocomplete দেয় আর ভুল টাইপ দিলে সাথে সাথে দাগ দেয়।

///

আরও তথ্য পাওয়া যাবে
[অফিসিয়াল plugin পেজে](https://plugins.jetbrains.com/plugin/12861-pydantic)
আর [Github repository-তে](https://github.com/koxudaxi/pydantic-pycharm-plugin)।
