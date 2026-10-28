# Pydantic Logfire { #pydantic-logfire }

/// note | এই পেজে যা শিখবেন

* Logfire দিয়ে প্রোডাকশনের ব্যর্থ যাচাই রেকর্ড করা।
* `record` সেটিং দিয়ে কতটা রেকর্ড হবে তা ঠিক করা (`failure`, `all`, `metrics`, `off`)।
* ওয়েব framework-এর trace যোগ করা, নিজে মডেল লগ করা, আর সাধারণ সমস্যার সমাধান।

///

প্রোডাকশনের `ValidationError`-এর পেছনের ডেটা খুঁজে বের করুন। Logfire ব্যর্থ Pydantic যাচাই তাদের
গোছানো এররসহ রেকর্ড করে, আর সেগুলো আশেপাশের রিকোয়েস্ট বা job trace-এর ভেতরে রাখতে পারে, ফলে দেখতে পারেন
কী ব্যর্থ হলো, ইনপুট কোথা থেকে এল, আর একই সমস্যা বারবার ঘটছে কিনা।

/// tip | উদাহরণ দিয়ে বুঝি

Logfire হলো অ্যাপের কালো বাক্স (flight recorder): কোনো যাচাই ব্যর্থ হলে ঠিক কোন ডেটা, কোন রিকোয়েস্ট থেকে, কখন এসেছিল, সব লিখে রাখে। পরে তদন্তের সময় অনুমান করতে হয় না।

///

## ব্যর্থ যাচাই রেকর্ড করা { #record-failed-validations }

আপনার দরকার একটি [ফ্রি Logfire অ্যাকাউন্ট](https://logfire.pydantic.dev/login) আর project। আপনার প্রজেক্টের
ফোল্ডার থেকে SDK ইনস্টল করে সাইন ইন করুন:

```bash
pip install logfire
logfire auth
```

যে মডেলগুলো পর্যবেক্ষণ করতে চান সেগুলো সংজ্ঞায়িত বা import করার আগে `instrument_pydantic()` ডাকুন:

```python
from datetime import date

import logfire

from pydantic import BaseModel

logfire.configure()
logfire.instrument_pydantic(record='failure')  # (1)!


class User(BaseModel):
    name: str
    country_code: str
    dob: date


User(name='Anne', country_code='USA', dob='not-a-date')  # (2)!
```

1. সফল যাচাইগুলো সমষ্টিগত metric হিসেবে থাকে। ব্যর্থ যাচাই তাদের গোছানো এররসহ আলাদা warning
   রেকর্ড তৈরি করে।
2. উদাহরণটি চালান আর জিজ্ঞাসা করলে একটি Logfire project বেছে নিন বা তৈরি করুন। অবৈধ তারিখটি
   Logfire-এর Live view-তে একটি warning রেকর্ড তৈরি করে।

/// warning | export করার আগে যাচাইয়ের ডেটা পর্যালোচনা করুন

ব্যর্থ-যাচাইয়ের রেকর্ডে Pydantic-এর গোছানো এরর থেকে প্রত্যাখ্যাত মান থাকে। Logfire
export-এর আগে [প্রচলিত সংবেদনশীল মান মুছে দেয় (scrub)](https://pydantic.dev/docs/logfire/instrument/scrubbing/),
কিন্তু Logfire প্রতিটি প্রত্যাখ্যাত মান সিরিয়ালাইজ করা `errors` অ্যাট্রিবিউটের ভেতরে `input` key-এর নিচে রাখে,
ফিল্ডের পথ থেকে আলাদা করে। সেই মানগুলোতে secret বা ব্যক্তিগত তথ্য থাকতে পারলে,
`logfire.configure()`-এ `scrubbing=logfire.ScrubbingOptions(extra_patterns=[r'(?:^input$|"input"\s*:)'])` দিন।
দুটি বিকল্প প্যাটার্ন scrubber-কে বলে সিরিয়ালাইজ করা যাচাই এরর পরীক্ষা করে যে মানের key হুবহু `input`
সেগুলো মুছে দিতে; কোনোটিই আপনার মডেলের ফিল্ডের নাম উল্লেখ করে না। বিকল্প হিসেবে `record='metrics'` ব্যবহার করুন,
তাহলে আলাদা আলাদা ব্যর্থতা export হবে না।

///

![Logfire live view-তে রেকর্ড হওয়া একটি ব্যর্থ Pydantic যাচাই](../img/logfire-validation-live-view.png)

প্রত্যাখ্যাত মান, এরর টাইপ আর ফিল্ডের পথ, আর যাচাই চলার সময় সক্রিয় থাকা যেকোনো রিকোয়েস্ট বা job
trace দেখতে warning-টি খুলুন। আরও বিস্তারিত জানতে দেখুন
[যাচাই এররের সমস্যা সমাধান](../errors/troubleshooting.md)।

## কতটা রেকর্ড হবে বেছে নিন { #choose-how-much-to-record }

`record` আর্গুমেন্ট বিস্তারিত তথ্য আর ডেটার পরিমাণের মধ্যে ভারসাম্য নিয়ন্ত্রণ করে:

| সেটিং | আলাদা রেকর্ড | metric |
| --- | --- | --- |
| `failure` | শুধু ব্যর্থ যাচাই | সব যাচাই |
| `all` (ডিফল্ট) | প্রতিটি সফল আর ব্যর্থ যাচাই | সব যাচাই |
| `metrics` | কিছুই না | সব যাচাই |
| `off` | কিছুই না | কিছুই না |

প্রোডাকশনে সমস্যা সমাধানের জন্য `failure` ব্যবহার করুন, এতে প্রতিটি সফল যাচাইয়ের জন্য আলাদা রেকর্ড তৈরি হয় না।
ডেভেলপমেন্টের সময় সফল ইনপুট আর যাচাই হওয়া ফলও দেখতে চাইলে `all` ব্যবহার করুন।

```python
import logfire

logfire.instrument_pydantic(record='all')
```

প্রতিটি মডেলের আলাদা সেটিং, তৃতীয় পক্ষের মডেল অন্তর্ভুক্তি, আর environment variable
বা `pyproject.toml` দিয়ে কনফিগারেশনের জন্য দেখুন পূর্ণ
[Logfire Pydantic integration তথ্যসূত্র](https://pydantic.dev/docs/logfire/integrations/pydantic/)।

## আশেপাশের অ্যাপ্লিকেশন trace যোগ করা { #add-the-surrounding-application-trace }

Pydantic বলে কোন মান ব্যর্থ হলো। সেই মান কোথা থেকে এল আর তার আশেপাশে কী ঘটল তা দেখতে আপনার web framework,
ডেটাবেস client বা task queue instrument করুন। যেমন, একটি FastAPI trace একটি সময়রেখায় দেখাতে পারে
আপনার endpoint-এ পৌঁছানো রিকোয়েস্ট, ব্যর্থ মডেল যাচাই, আর caller-কে ফেরত দেওয়া রেসপন্স।

FastAPI, Django, Celery, SQLAlchemy, HTTPX আর আরও অনেকের জন্য দেখুন [Logfire integration](https://pydantic.dev/docs/logfire/integrations/)।

```python
import logfire
from fastapi import FastAPI

app = FastAPI()

logfire.configure()
logfire.instrument_pydantic(record='failure')
logfire.instrument_fastapi(app)  # প্রতিটি রিকোয়েস্ট একটি trace, ব্যর্থ যাচাই তার ভেতরে
```

## যাচাই হওয়া মডেল নিজে লগ করা { #log-a-validated-model-explicitly }

নিজের গোছানো লগ বা span-এও একটি Pydantic মডেল যুক্ত করতে পারেন। Logfire মডেলের
ফিল্ডগুলো রেখে দেয়, ফলে সেগুলো দেখতে আর query করতে পারেন:

```python
from datetime import date

import logfire

from pydantic import BaseModel

logfire.configure()


class User(BaseModel):
    name: str
    country_code: str
    dob: date


user = User(name='Anne', country_code='USA', dob='2000-01-01')
logfire.info('user processed: {user!r}', user=user)
```

## সমস্যা সমাধান { #troubleshooting }

* **কোনো যাচাইয়ের রেকর্ড দেখা যাচ্ছে না:** নিশ্চিত করুন `logfire.configure()` চলছে আর
  মডেল ক্লাস সংজ্ঞায়িত বা import হওয়ার আগে `instrument_pydantic()` চলছে।
* **সফল যাচাই দেখা যাচ্ছে না:** `record='failure'` এগুলো শুধু metric হিসেবে রাখে। প্রতিটি সাফল্যের জন্য
  আলাদা span দরকার হলে `record='all'` ব্যবহার করুন।
* **সফল যাচাইও দেখতে হবে:** `record='all'` ব্যবহার করুন। এটি প্রতিটি যাচাইয়ের জন্য আলাদা
  span তৈরি করে, তাই প্রোডাকশনে ব্যবহারের আগে এর ডেটার পরিমাণ আর গোপনীয়তার প্রভাব ভেবে দেখুন।

/// check | সংক্ষেপে মনে রাখুন

* `logfire.configure()` + `logfire.instrument_pydantic(record='failure')`, মডেল import-এর আগে।
* প্রোডাকশনে `failure`, ডেভেলপমেন্টে `all`।
* framework instrument করলে (যেমন `logfire.instrument_fastapi(app)`) ব্যর্থতার পুরো প্রেক্ষাপট দেখা যায়।

///
