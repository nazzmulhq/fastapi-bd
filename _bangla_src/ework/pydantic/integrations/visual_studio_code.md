# Visual Studio Code { #visual-studio-code }

/// note | এই পেজে যা শিখবেন

* VS Code-এ Pydantic মডেলের জন্য autocomplete আর টাইপ-এররের পরীক্ষা চালু করা (Pylance, mypy)।
* "কঠোর" টাইপ এরর কেন মাঝে মাঝে ভুল সতর্কতা দেয়, আর সেগুলো এড়ানোর তিনটি উপায়।
* class আর্গুমেন্টে config, আর `Field`-এ `default` লেখার নিয়ম।

///

Pydantic মানক Python টাইপ annotation-এর ওপর তৈরি বলে, বাড়তি সেটআপ ছাড়াই যেকোনো editor বা IDE-তে ভালো কাজ করে।

[Visual Studio Code (VS Code)](https://code.visualstudio.com/) ব্যবহার করলে, কিছু **বাড়তি editor সুবিধা** সমর্থিত, যা [PyCharm plugin](../integrations/pycharm.md)-এর দেওয়া সুবিধার সাথে তুলনীয়।

অর্থাৎ নতুন Pydantic মডেলের instance তৈরির সময়েও আপনি **autocompletion** (বা "IntelliSense") আর টাইপ ও বাধ্যতামূলক আর্গুমেন্টের **এরর পরীক্ষা** পাবেন।

![VS Code-এ pydantic autocompletion](../img/vs_code_01.png)

## VS Code কনফিগার করা { #configure-vs-code }

এই সুবিধাগুলো পেতে, প্রস্তাবিত সেটিংস ব্যবহার করে VS Code ঠিকভাবে কনফিগার করা নিশ্চিত করতে হবে।

আপনার কনফিগারেশন ভিন্ন হলে, এখানে ধাপগুলোর একটি সংক্ষিপ্ত চিত্র।

### Pylance ইনস্টল { #install-pylance }

VS Code-এর জন্য [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension ব্যবহার করা উচিত। এটি Python-এর জন্য প্রস্তাবিত, নতুন প্রজন্মের, অফিসিয়াল VS Code plug-in।

Pylance ডিফল্টভাবে [VS Code-এর Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)-এর অংশ হিসেবে ইনস্টল হয়, তাই সম্ভবত এটি এমনিতেই কাজ করবে। নইলে, এটি আপনার editor-এ ইনস্টল আর চালু আছে কিনা আবার দেখে নিন।

### আপনার environment কনফিগার { #configure-your-environment }

তারপর নিশ্চিত করতে হবে আপনার editor আপনার Python প্রজেক্টের [Python environment](https://code.visualstudio.com/docs/python/python-tutorial#_install-and-use-packages) (সম্ভবত একটি virtual environment) চেনে।

এটি হবে সেই environment যেখানে আপনি Pydantic ইনস্টল করেছেন।

### Pylance কনফিগার { #configure-pylance }

ডিফল্ট কনফিগারেশনে autocompletion-এর সমর্থন পাবেন, কিন্তু Pylance হয়তো টাইপ এরর পরীক্ষা করবে না।

এই ধাপগুলোতে Pylance-এর টাইপ এরর পরীক্ষা চালু করতে পারেন:

* "User Settings" খুলুন
* `Type Checking Mode` খুঁজুন
* `Python › Analysis: Type Checking Mode`-এর নিচে একটি অপশন পাবেন
* এটি `basic` বা `strict` করুন (ডিফল্টভাবে এটি `off`)

![VS Code-এ Type Checking Mode strict করা](../img/vs_code_02.png)

এখন নতুন Pydantic মডেলের instance তৈরির সময় শুধু autocompletion নয়, **বাধ্যতামূলক আর্গুমেন্টের** এরর পরীক্ষাও পাবেন।

![VS Code-এ বাধ্যতামূলক আর্গুমেন্টের এরর পরীক্ষা](../img/vs_code_03.png)

আর **অবৈধ ডেটা টাইপের** এরর পরীক্ষাও পাবেন।

![VS Code-এ অবৈধ ডেটা টাইপের এরর পরীক্ষা](../img/vs_code_04.png)

/// note | কারিগরি খুঁটিনাটি

Pylance হলো VS Code extension, এর source code বন্ধ (closed source), তবে বিনামূল্যে ব্যবহার করা যায়। ভেতরে Pylance একটি open source টুল (এটিও Microsoft-এর) ব্যবহার করে, যার নাম [Pyright](https://github.com/microsoft/pyright), আর ভারী কাজগুলো সেটিই করে।

এ নিয়ে আরও পড়তে পারেন [Pylance-এর প্রায়ই জিজ্ঞাসিত প্রশ্নে](https://github.com/microsoft/pylance-release/blob/main/FAQ.md#what-is-the-relationship-between-pylance-pyright-and-the-python-extension)।

///

### mypy কনফিগার { #configure-mypy }

editor-এর ভেতরেই mypy-র এরর পরীক্ষা পেতে VS Code-এ mypy-ও কনফিগার করতে চাইতে পারেন (Pylance-এর বিকল্প বা পাশাপাশি)।

আপনি [Pydantic mypy plugin](../integrations/mypy.md) কনফিগার করে থাকলে, এতে সেটির ধরা এররগুলোও থাকবে।

VS Code-এ mypy চালু করতে, এগুলো করুন:

* "User Settings" খুলুন
* `Mypy Enabled` খুঁজুন
* `Python › Linting: Mypy Enabled`-এর নিচে একটি অপশন পাবেন
* বক্সে টিক দিন (ডিফল্টভাবে এতে টিক নেই)

![VS Code-এ mypy চালু](../img/vs_code_05.png)

## টিপস আর কৌশল { #tips-and-tricks }

VS Code-এ Pydantic ব্যবহারের সময় ডেভেলপারের অভিজ্ঞতা উন্নত করার আরও কিছু টিপস আর কৌশল।

### কঠোর এরর { #strict-errors }

এই বাড়তি editor সমর্থন যেভাবে কাজ করে তা হলো, Pylance আপনার Pydantic মডেলকে এমনভাবে বিবেচনা করে যেন সেগুলো Python-এর বিশুদ্ধ `dataclasses`।

আর নতুন Pydantic মডেলের instance তৈরির সময় আর্গুমেন্টে দেওয়া ডেটা টাইপ নিয়ে এটি **কঠোর টাইপ এরর পরীক্ষা** দেখাবে।

এই উদাহরণে দেখতে পাচ্ছেন এটি দেখাচ্ছে যে `age` আর্গুমেন্টের জন্য `'23'` মানের একটি `str` বৈধ `int` নয়।

![VS Code-এর কঠোর টাইপ এরর](../img/vs_code_06.png)

এটি `age='23'`-এর বদলে `age=23` আশা করবে।

তবুও, Pydantic-এর নকশা আর এর প্রধান সুবিধাগুলোর একটি হলো এটি **ডেটা টাইপ নিয়ে খুব ছাড় দেয়**।

এটি আসলে `'23'` মানের `str` গ্রহণ করবে আর সেটিকে `23` মানের একটি `int`-এ রূপান্তর করবে।

এই কঠোর এরর পরীক্ষা বেশিরভাগ সময় **খুব কাজের** আর **অনেক বাগ আগেভাগে ধরতে** সাহায্য করে। কিন্তু কিছু ক্ষেত্রে, যেমন `age='23'`-এ, একটি "ভুল সতর্কতা" (false positive) দিয়ে এটি অসুবিধা তৈরি করতে পারে।

/// tip | উদাহরণ দিয়ে বুঝি

editor হলো কড়া শিক্ষক: "সংখ্যার ঘরে লেখা কেন?" Pydantic হলো উদার পরীক্ষক: "লেখাটা তো '23', বুঝে নিচ্ছি সংখ্যা 23"। দুজনের নিয়ম আলাদা বলে মাঝে মাঝে শিক্ষক এমন জায়গায় লাল দাগ দেন, যেখানে আসলে কোনো সমস্যা নেই। নিচের কৌশলগুলো শুধু সেই নির্দিষ্ট জায়গায় দাগ মুছে দেয়।

///

---

ওপরের `age='23'` উদাহরণটি ইচ্ছা করেই সহজ রাখা, এরর আর টাইপের পার্থক্য দেখাতে।

কিন্তু আরও প্রচলিত ক্ষেত্র যেখানে এই কঠোর এরর অসুবিধাজনক হবে, তা হলো আরও জটিল ডেটা টাইপ ব্যবহারের সময়, যেমন `datetime` ফিল্ডে `int` মান, বা Pydantic sub-model-এর জন্য `dict` মান।

যেমন, এটি Pydantic-এর জন্য বৈধ:

⟦CODE1⟧

`knight` ফিল্ডের টাইপ `Knight` ক্লাস (একটি Pydantic মডেল) দিয়ে ঘোষিত, আর কোডটি বদলে একটি literal `dict` দিচ্ছে। এটি Pydantic-এর জন্য তবুও বৈধ, আর `dict`-টি স্বয়ংক্রিয়ভাবে একটি `Knight` instance-এ রূপান্তরিত হবে।

তবুও, এটি একটি টাইপ এরর হিসেবে ধরা পড়বে:

![মডেলসহ VS Code-এর কঠোর টাইপ এরর](../img/vs_code_07.png)

এমন ক্ষেত্রে, কোডের বাকি অংশে কঠোর এরর বজায় রেখে খুব নির্দিষ্ট জায়গায় সেগুলো বন্ধ বা উপেক্ষা করার কয়েকটি উপায় আছে।

নিচে এটি অর্জনের কয়েকটি কৌশল।

#### এক লাইনে টাইপ পরীক্ষা বন্ধ { #disable-type-checks-in-a-line }

একটি নির্দিষ্ট লাইনের এরর বন্ধ করতে পারেন এই মন্তব্য দিয়ে:

```python
# type: ignore
```

অথবা (pylance/pyright-এর জন্য নির্দিষ্ট করে):

```python
# pyright: ignore
```

([pyright](https://github.com/microsoft/pyright) হলো Pylance-এর ব্যবহৃত language server।)।

`age='23'`-এর উদাহরণে ফিরে গেলে, এটি হবে:

⟦CODE2⟧

এভাবে Pylance আর mypy সেই লাইনের এরর উপেক্ষা করবে।

**সুবিধা**: সেখানের এরর সরাতে সেই লাইনে একটি সহজ পরিবর্তন।

**অসুবিধা**: সেই লাইনের অন্য যেকোনো এররও বাদ পড়বে, যেমন টাইপ পরীক্ষা, ভুল বানানের আর্গুমেন্ট, না দেওয়া বাধ্যতামূলক আর্গুমেন্ট ইত্যাদি।

#### একটি variable-এর টাইপ বদলে দেওয়া { #override-the-type-of-a-variable }

যে মান ব্যবহার করতে চান তা দিয়ে একটি variable তৈরি করে, স্পষ্টভাবে এর টাইপ `Any` ঘোষণা করতে পারেন।

⟦CODE3⟧

এভাবে Pylance আর mypy `age_str` variable-টিকে এমনভাবে বুঝবে যেন তারা এর টাইপ জানে না; `int` প্রত্যাশিত জায়গায় এটি `str` বলে জেনে (আর তারপর সংশ্লিষ্ট এরর দেখিয়ে) নয়।

**সুবিধা**: শুধু একটি নির্দিষ্ট মানের জন্য এরর উপেক্ষিত হবে, আর অন্য আর্গুমেন্টের বাড়তি এরর তবুও দেখতে পাবেন।

**অসুবিধা**: এতে `Any` import করতে হয়, আর এরর উপেক্ষার দরকার এমন প্রতিটি আর্গুমেন্টের জন্য নতুন লাইনে একটি নতুন variable লাগে।

#### `cast` দিয়ে একটি মানের টাইপ বদলে দেওয়া { #override-the-type-of-a-value-with-cast }

আগের উদাহরণের একই ধারণা `cast()`-এর সাহায্যে একই লাইনে রাখা যায়।

এভাবে, অন্য variable ছাড়াই মানের টাইপ ঘোষণা সেই লাইনেই বদলে যায়।

⟦CODE4⟧

`cast(Any, '23')` মানটিকে প্রভাবিত করে না, এটি তখনো শুধু `'23'`, কিন্তু এখন Pylance আর mypy ধরে নেবে এটি `Any` টাইপের, অর্থাৎ তারা এমন আচরণ করবে যেন মানটির টাইপ জানে না।

তাই এটি আগের উদাহরণের সমতুল্য, বাড়তি variable ছাড়া।

**সুবিধা**: শুধু একটি নির্দিষ্ট মানের জন্য এরর উপেক্ষিত হবে, আর অন্য আর্গুমেন্টের বাড়তি এরর তবুও দেখতে পাবেন। বাড়তি variable-এর দরকার নেই।

**অসুবিধা**: এতে `Any` আর `cast` import করতে হয়, আর `cast()` ব্যবহারে অভ্যস্ত না হলে প্রথমে একটু অদ্ভুত লাগতে পারে।

### class আর্গুমেন্টে config { #config-in-class-arguments }

Pydantic-এ [মডেল কনফিগারেশনের][pydantic.config.ConfigDict] একটি সমৃদ্ধ সেট পাওয়া যায়।

এই কনফিগারেশনগুলো প্রতিটি মডেলের ভেতরের `class Config`-এ সেট করা যায়:

⟦CODE5⟧

অথবা মডেল ক্লাস সংজ্ঞায়িত করার সময় keyword আর্গুমেন্ট হিসেবে দেওয়া যায়:

⟦CODE6⟧

নির্দিষ্ট কনফিগারেশন **`frozen`** (beta-তে)-এর একটি বিশেষ অর্থ আছে।

এটি একটি মডেলের instance তৈরি হয়ে যাওয়ার পরে অন্য কোডকে সেটি বদলাতে বাধা দেয়, একে **"জমিয়ে" (frozen)** রাখে।

দ্বিতীয় রূপে `frozen=True` ঘোষণা করলে (ক্লাস সংজ্ঞায় **keyword আর্গুমেন্ট** দিয়ে),
Pylance সেটি ব্যবহার করে আপনার কোড পরীক্ষায় সাহায্য করতে পারে আর **এরর ধরতে** পারে যখন কিছু একটি "frozen" মডেলে মান বসানোর
চেষ্টা করে।

![মডেলসহ VS Code-এর কঠোর টাইপ এরর](../img/vs_code_08.png)

## `Field` দিয়ে ডিফল্ট যোগ { #adding-a-default-with-field }

ফিল্ডটি ঐচ্ছিক তা বুঝতে Pylance/pyright-এর দরকার `default`-কে `Field`-এর একটি keyword আর্গুমেন্ট হিসেবে দেওয়া।

⟦CODE7⟧

এটি dataclass transform-এর একটি সীমাবদ্ধতা আর pydantic-এ ঠিক করা যায় না।

/// warning | সাধারণ ভুল

`Field(23)` চলার সময় ঠিকই কাজ করে, কিন্তু editor ভাবে ফিল্ডটি বাধ্যতামূলক আর `Knight()`-এ লাল দাগ দেয়। সবসময় `Field(default=23)` লিখুন।

///

## কারিগরি খুঁটিনাটি { #technical-details }

/// warning | সতর্কতা

একজন Pydantic ব্যবহারকারী হিসেবে নিচের খুঁটিনাটি আপনার দরকার নেই। এই অংশের বাকিটা নিশ্চিন্তে বাদ দিতে পারেন।

এই খুঁটিনাটি শুধু অন্য লাইব্রেরির লেখক ইত্যাদির জন্য কাজের।

///

এই বাড়তি editor সমর্থন কাজ করে [`@dataclass_transform` decorator](https://typing.python.org/en/latest/spec/dataclasses.html#the-dataclass-transform-decorator)
ব্যবহার করে ([PEP 681](https://peps.python.org/pep-0681/) দিয়ে চালু)।

এই মানক Pydantic-এর মতো লাইব্রেরিগুলোকে editor আর টুলকে জানানোর একটি উপায় দেয় যে তারা (editor) যেন এই লাইব্রেরিগুলোকে (যেমন Pydantic) [dataclass][dataclasses]-এর মতো বিবেচনা করে, autocompletion, টাইপ পরীক্ষা ইত্যাদি দিয়ে।
