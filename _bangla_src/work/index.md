---
include_yaml:
  sponsors: data/sponsors.yml
---

# FastAPI { #fastapi }

<style>
.md-content .md-typeset h1 { display: none; }
</style>

<p align="center">
  <a href="https://fastapi.tiangolo.com"><img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" alt="FastAPI"></a>
</p>
<p align="center">
    <em>FastAPI ফ্রেমওয়ার্ক: উচ্চ পারফরম্যান্স, সহজে শেখা যায়, দ্রুত কোড লেখা যায়, প্রোডাকশনের জন্য প্রস্তুত</em>
</p>
<p align="center">
<a href="https://github.com/fastapi/fastapi/actions?query=workflow%3ATest+event%3Apush+branch%3Amaster">
    <img src="https://github.com/fastapi/fastapi/actions/workflows/test.yml/badge.svg?event=push&branch=master" alt="Test">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/fastapi/fastapi">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/fastapi/fastapi.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/fastapi">
    <img src="https://img.shields.io/pypi/v/fastapi?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/fastapi">
    <img src="https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>

---

**ডকুমেন্টেশন**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

**সোর্স কোড**: [https://github.com/fastapi/fastapi](https://github.com/fastapi/fastapi)

---

FastAPI হলো Python দিয়ে API তৈরির জন্য একটি আধুনিক ও দ্রুত (উচ্চ পারফরম্যান্সের) ওয়েব ফ্রেমওয়ার্ক, যা স্ট্যান্ডার্ড Python টাইপ হিন্টের ওপর ভিত্তি করে তৈরি।

এর প্রধান ফিচারগুলো হলো:

* **দ্রুত**: খুবই উচ্চ পারফরম্যান্স, **NodeJS** ও **Go**-এর সমকক্ষ (Starlette ও Pydantic-কে ধন্যবাদ)। [সবচেয়ে দ্রুত Python ফ্রেমওয়ার্কগুলোর একটি](#performance)।
* **দ্রুত কোডিং**: ফিচার ডেভেলপ করার গতি প্রায় ২০০% থেকে ৩০০% বাড়ায়। *
* **কম বাগ**: মানুষের (ডেভেলপারের) কারণে হওয়া ভুল প্রায় ৪০% কমায়। *
* **সহজবোধ্য**: চমৎকার এডিটর সাপোর্ট। সব জায়গায় <dfn title="অটো-কমপ্লিট, অটোকমপ্লিশন বা IntelliSense নামেও পরিচিত">কমপ্লিশন</dfn>। ডিবাগিংয়ে কম সময়।
* **সহজ**: ব্যবহার ও শেখা সহজ করে ডিজাইন করা। ডকুমেন্টেশন পড়তে কম সময়।
* **সংক্ষিপ্ত**: কোডের পুনরাবৃত্তি কমায়। প্রতিটি প্যারামিটার ঘোষণা থেকে একাধিক ফিচার। কম বাগ।
* **মজবুত**: প্রোডাকশনের জন্য প্রস্তুত কোড পান। সাথে স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ ডকুমেন্টেশন।
* **স্ট্যান্ডার্ড-ভিত্তিক**: API-এর ওপেন স্ট্যান্ডার্ডগুলোর ওপর ভিত্তি করে তৈরি (এবং সেগুলোর সাথে সম্পূর্ণ সামঞ্জস্যপূর্ণ): [OpenAPI](https://github.com/OAI/OpenAPI-Specification) (আগে Swagger নামে পরিচিত ছিল) এবং [JSON Schema](https://json-schema.org/)।

<small>* প্রোডাকশন অ্যাপ্লিকেশন তৈরি করা একটি অভ্যন্তরীণ ডেভেলপমেন্ট টিমের করা পরীক্ষার ভিত্তিতে আনুমানিক হিসাব।</small>

## স্পনসর { #sponsors }

<!-- sponsors -->

### কীস্টোন স্পনসর { #keystone-sponsor }

<div class="fastapi-sponsors fastapi-sponsors--keystone">
{% for sponsor in sponsors.keystone -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--keystone" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}"></a>
{% endfor -%}
</div>

### গোল্ড স্পনসর { #gold-sponsors }

<div class="fastapi-sponsors fastapi-sponsors--gold">
{% for sponsor in sponsors.gold -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--gold" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}" loading="lazy"></a>
{% endfor -%}
</div>

### সিলভার স্পনসর { #silver-sponsors }

<div class="fastapi-sponsors fastapi-sponsors--silver">
{% for sponsor in sponsors.silver -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--silver" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}" loading="lazy"></a>
{% endfor %}
</div>

<!-- /sponsors -->

[অন্যান্য স্পনসর](https://fastapi.tiangolo.com/fastapi-people/#sponsors)

## মতামত { #opinions }

<!-- only-mkdocs -->
<div class="fastapi-opinions" data-fastapi-opinions>
  <div class="fastapi-opinions__tabs" role="tablist" aria-label="FastAPI ব্যবহারকারী প্রতিষ্ঠান">
    <button class="fastapi-opinions__tab" role="tab" type="button" id="fo-tab-microsoft" aria-controls="fo-panel-microsoft" aria-selected="true" tabindex="0">
      <span class="fastapi-opinions__mark"><img src="/img/logos/microsoft.svg" alt="Microsoft" loading="lazy"></span>
    </button>
    <button class="fastapi-opinions__tab" role="tab" type="button" id="fo-tab-uber" aria-controls="fo-panel-uber" aria-selected="false" tabindex="-1">
      <span class="fastapi-opinions__mark"><img src="/img/logos/uber.svg" alt="Uber" loading="lazy"></span>
    </button>
    <button class="fastapi-opinions__tab" role="tab" type="button" id="fo-tab-netflix" aria-controls="fo-panel-netflix" aria-selected="false" tabindex="-1">
      <span class="fastapi-opinions__mark"><img src="/img/logos/netflix.svg" alt="Netflix" loading="lazy"></span>
    </button>
    <button class="fastapi-opinions__tab" role="tab" type="button" id="fo-tab-cisco" aria-controls="fo-panel-cisco" aria-selected="false" tabindex="-1">
      <span class="fastapi-opinions__mark"><img src="/img/logos/cisco.svg" alt="Cisco" loading="lazy"></span>
    </button>
  </div>

  <div class="fastapi-opinions__panel" id="fo-panel-microsoft" role="tabpanel" aria-labelledby="fo-tab-microsoft" tabindex="0">
    <blockquote class="fastapi-opinions__quote">"আমি আজকাল প্রচুর <strong>FastAPI</strong> ব্যবহার করছি। আসলে আমার টিমের সব <strong>ML সার্ভিসের জন্য Microsoft-এ</strong> এটি ব্যবহার করার পরিকল্পনা করছি। এগুলোর কয়েকটি মূল <strong>Windows</strong> প্রোডাক্টে আর কয়েকটি <strong>Office</strong> প্রোডাক্টে যুক্ত হচ্ছে।"</blockquote>
    <div class="fastapi-opinions__attr">— Kabir Khan, <strong>Microsoft</strong> <a href="https://github.com/fastapi/fastapi/pull/26">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-uber" role="tabpanel" aria-labelledby="fo-tab-uber" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"আমরা <strong>FastAPI</strong> লাইব্রেরি গ্রহণ করেছি একটি <strong>REST</strong> সার্ভার চালু করতে, যাকে কুয়েরি করে <strong>প্রেডিকশন</strong> পাওয়া যায়।" <em>[Ludwig-এর জন্য]</em></blockquote>
    <div class="fastapi-opinions__attr">— Piero Molino, Yaroslav Dudin, Sai Sumanth Miryala, <strong>Uber</strong> <a href="https://www.uber.com/us/en/blog/ludwig-v0-2/">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-netflix" role="tabpanel" aria-labelledby="fo-tab-netflix" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"<strong>Netflix</strong> আনন্দের সাথে জানাচ্ছে যে আমাদের <strong>ক্রাইসিস ম্যানেজমেন্ট</strong> অর্কেস্ট্রেশন ফ্রেমওয়ার্ক <strong>Dispatch</strong> এখন ওপেন সোর্স হিসেবে প্রকাশিত হলো!" <em>[FastAPI দিয়ে তৈরি]</em></blockquote>
    <div class="fastapi-opinions__attr">— Kevin Glisson, Marc Vilanova, Forest Monsen, <strong>Netflix</strong> <a href="https://netflixtechblog.com/introducing-dispatch-da4b8a2a8072">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-cisco" role="tabpanel" aria-labelledby="fo-tab-cisco" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"কেউ যদি প্রোডাকশনের জন্য Python API বানাতে চান, আমি জোরালোভাবে <strong>FastAPI</strong>-এর সুপারিশ করব। এটি <strong>সুন্দরভাবে ডিজাইন করা</strong>, <strong>ব্যবহারে সহজ</strong> এবং <strong>অত্যন্ত স্কেলেবল</strong>, আর আমাদের API-ফার্স্ট ডেভেলপমেন্ট কৌশলের একটি <strong>মূল উপাদান</strong> হয়ে উঠেছে।"</blockquote>
    <div class="fastapi-opinions__attr">— Deon Pillsbury, <strong>Cisco</strong> <a href="https://www.linkedin.com/posts/deonpillsbury_cisco-cx-python-activity-6963242628536487936-trAp/">(সূত্র)</a></div>
  </div>
</div>
<!-- /only-mkdocs -->

<div class="only-github" markdown="1">

"_[...] আমি আজকাল প্রচুর **FastAPI** ব্যবহার করছি। [...] আসলে আমার টিমের সব **ML সার্ভিসের জন্য Microsoft-এ** এটি ব্যবহার করার পরিকল্পনা করছি। এগুলোর কয়েকটি মূল **Windows** প্রোডাক্টে আর কয়েকটি **Office** প্রোডাক্টে যুক্ত হচ্ছে।_"

<div style="text-align: right; margin-right: 10%;">Kabir Khan - <strong>Microsoft</strong> <a href="https://github.com/fastapi/fastapi/pull/26"><small>(সূত্র)</small></a></div>

---

"_আমরা **FastAPI** লাইব্রেরি গ্রহণ করেছি একটি **REST** সার্ভার চালু করতে, যাকে কুয়েরি করে **প্রেডিকশন** পাওয়া যায়। [Ludwig-এর জন্য]_"

<div style="text-align: right; margin-right: 10%;">Piero Molino, Yaroslav Dudin, এবং Sai Sumanth Miryala - <strong>Uber</strong> <a href="https://www.uber.com/us/en/blog/ludwig-v0-2/"><small>(সূত্র)</small></a></div>

---

"_**Netflix** আনন্দের সাথে জানাচ্ছে যে আমাদের **ক্রাইসিস ম্যানেজমেন্ট** অর্কেস্ট্রেশন ফ্রেমওয়ার্ক **Dispatch** এখন ওপেন সোর্স হিসেবে প্রকাশিত হলো! [**FastAPI** দিয়ে তৈরি]_"

<div style="text-align: right; margin-right: 10%;">Kevin Glisson, Marc Vilanova, Forest Monsen - <strong>Netflix</strong> <a href="https://netflixtechblog.com/introducing-dispatch-da4b8a2a8072"><small>(সূত্র)</small></a></div>

---

"_কেউ যদি প্রোডাকশনের জন্য Python API বানাতে চান, আমি জোরালোভাবে **FastAPI**-এর সুপারিশ করব। এটি **সুন্দরভাবে ডিজাইন করা**, **ব্যবহারে সহজ** এবং **অত্যন্ত স্কেলেবল**। এটি আমাদের API-ফার্স্ট ডেভেলপমেন্ট কৌশলের একটি **মূল উপাদান** হয়ে উঠেছে এবং আমাদের Virtual TAC Engineer-এর মতো অনেক অটোমেশন ও সার্ভিস চালাচ্ছে।_"

<div style="text-align: right; margin-right: 10%;">Deon Pillsbury - <strong>Cisco</strong> <a href="https://www.linkedin.com/posts/deonpillsbury_cisco-cx-python-activity-6963242628536487936-trAp/"><small>(সূত্র)</small></a></div>

---

</div>

## FastAPI মিনি ডকুমেন্টারি { #fastapi-mini-documentary }

২০২৫ সালের শেষে একটি [FastAPI মিনি ডকুমেন্টারি](https://www.youtube.com/watch?v=mpR8ngthqiE) প্রকাশিত হয়েছে, আপনি এটি অনলাইনে দেখতে পারেন:

<a class="fastapi-feature-banner" href="https://www.youtube.com/watch?v=mpR8ngthqiE"><img src="https://fastapi.tiangolo.com/img/fastapi-documentary.jpg" alt="FastAPI মিনি ডকুমেন্টারি"></a>

## **Typer**, CLI-এর FastAPI { #typer-the-fastapi-of-clis }

<a href="https://typer.tiangolo.com"><img src="https://typer.tiangolo.com/img/logo-margin/logo-margin-vector.svg" style="width: 20%;"></a>

আপনি যদি ওয়েব API-এর বদলে টার্মিনালে ব্যবহারের জন্য একটি <abbr title="Command Line Interface - কমান্ড লাইন ইন্টারফেস">CLI</abbr> অ্যাপ বানান, তাহলে [**Typer**](https://typer.tiangolo.com/) দেখে নিন।

**Typer** হলো FastAPI-এর ছোট ভাই। আর এটিকে **CLI-এর FastAPI** হিসেবে তৈরি করা হয়েছে। ⌨️ 🚀

## প্রয়োজনীয়তা { #requirements }

FastAPI দাঁড়িয়ে আছে বিশালদের কাঁধে:

* ওয়েব অংশের জন্য [Starlette](https://starlette.dev/)।
* ডেটা অংশের জন্য [Pydantic](https://pydantic.dev/docs/)।

## ইনস্টলেশন { #installation }

প্রথমে [`uv` ইনস্টল করুন](https://docs.astral.sh/uv/getting-started/installation/), তারপর আপনার প্রজেক্টে FastAPI যোগ করুন:

<div class="termy">

⟦CODE1⟧

</div>

**নোট**: সব টার্মিনালে যাতে কাজ করে সেজন্য `"fastapi[standard]"` অবশ্যই উদ্ধৃতিচিহ্নের মধ্যে লিখবেন।

আপনি যদি `pip` ব্যবহার করতে চান, তাহলে একটি ভার্চুয়াল এনভায়রনমেন্টের ভেতরে `fastapi[standard]` ইনস্টল করুন। বিকল্প ধাপগুলোর জন্য [ইনস্টলেশন গাইড](tutorial/#install-fastapi) দেখুন।

## উদাহরণ { #example }

### তৈরি করুন { #create-it }

`main.py` নামে একটি ফাইল তৈরি করুন, এতে লিখুন:

⟦CODE2⟧

<details markdown="1">
<summary>অথবা <code>async def</code> ব্যবহার করুন...</summary>

আপনার কোড যদি `async` / `await` ব্যবহার করে, তাহলে `async def` ব্যবহার করুন:

⟦CODE3⟧

**নোট**:

আপনি যদি না জানেন, তাহলে [ডকুমেন্টেশনে `async` ও `await` সম্পর্কে](https://fastapi.tiangolo.com/async/#in-a-hurry) _"তাড়াহুড়োয় আছেন?"_ অংশটি দেখুন।

</details>

### চালান { #run-it }

এই কমান্ড দিয়ে সার্ভার চালান:

<div class="termy">

⟦CODE4⟧

</div>

<details markdown="1">
<summary><code>fastapi dev</code> কমান্ড সম্পর্কে...</summary>

`fastapi dev` কমান্ডটি স্বয়ংক্রিয়ভাবে আপনার `main.py` ফাইল পড়ে, এর ভেতরের **FastAPI** অ্যাপটি খুঁজে বের করে এবং [Uvicorn](https://uvicorn.dev) ব্যবহার করে একটি সার্ভার চালু করে।

ডিফল্টভাবে, লোকাল ডেভেলপমেন্টের জন্য `fastapi dev` অটো-রিলোড চালু রেখে শুরু হয়।

এ সম্পর্কে আরও জানতে [FastAPI CLI ডকুমেন্টেশন](https://fastapi.tiangolo.com/fastapi-cli/) পড়ুন।

</details>

### যাচাই করুন { #check-it }

আপনার ব্রাউজারে [http://127.0.0.1:8000/items/5?q=somequery](http://127.0.0.1:8000/items/5?q=somequery) খুলুন।

আপনি এরকম JSON রেসপন্স দেখতে পাবেন:

⟦CODE5⟧

আপনি ইতিমধ্যে এমন একটি API তৈরি করে ফেলেছেন যা:

* `/` এবং `/items/{item_id}` _পাথে_ HTTP রিকোয়েস্ট গ্রহণ করে।
* দুটি _পাথই_ `GET` <em>অপারেশন</em> (HTTP _মেথড_ নামেও পরিচিত) গ্রহণ করে।
* `/items/{item_id}` _পাথে_ একটি _পাথ প্যারামিটার_ `item_id` আছে, যা একটি `int` হওয়া উচিত।
* `/items/{item_id}` _পাথে_ একটি ঐচ্ছিক `str` _কুয়েরি প্যারামিটার_ `q` আছে।

### ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন { #interactive-api-docs }

এবার [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ যান।

আপনি স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন দেখতে পাবেন (যা [Swagger UI](https://github.com/swagger-api/swagger-ui) সরবরাহ করে):

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### বিকল্প API ডকুমেন্টেশন { #alternative-api-docs }

আর এখন [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)-এ যান।

আপনি বিকল্প স্বয়ংক্রিয় ডকুমেন্টেশন দেখতে পাবেন (যা [ReDoc](https://github.com/Redocly/redoc) সরবরাহ করে):

![ReDoc](https://fastapi.tiangolo.com/img/index/index-02-redoc-simple.png)

## উদাহরণ আপগ্রেড { #example-upgrade }

এবার `main.py` ফাইলটি পরিবর্তন করুন যাতে এটি একটি `PUT` রিকোয়েস্ট থেকে বডি গ্রহণ করে।

Pydantic-এর কল্যাণে স্ট্যান্ডার্ড Python টাইপ ব্যবহার করে বডি ঘোষণা করুন।

⟦CODE6⟧

`fastapi dev` সার্ভারটি স্বয়ংক্রিয়ভাবে রিলোড হওয়া উচিত।

### ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন আপগ্রেড { #interactive-api-docs-upgrade }

এবার [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ যান।

* ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন স্বয়ংক্রিয়ভাবে আপডেট হবে, নতুন বডিসহ:

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

* "Try it out" বাটনে ক্লিক করুন, এটি আপনাকে প্যারামিটারগুলো পূরণ করে সরাসরি API-এর সাথে কাজ করতে দেয়:

![Swagger UI ইন্টারঅ্যাকশন](https://fastapi.tiangolo.com/img/index/index-04-swagger-03.png)

* তারপর "Execute" বাটনে ক্লিক করুন, ইউজার ইন্টারফেসটি আপনার API-এর সাথে যোগাযোগ করবে, প্যারামিটারগুলো পাঠাবে, ফলাফল নিয়ে আসবে এবং স্ক্রিনে দেখাবে:

![Swagger UI ইন্টারঅ্যাকশন](https://fastapi.tiangolo.com/img/index/index-05-swagger-04.png)

### বিকল্প API ডকুমেন্টেশন আপগ্রেড { #alternative-api-docs-upgrade }

আর এখন [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)-এ যান।

* বিকল্প ডকুমেন্টেশনেও নতুন কুয়েরি প্যারামিটার ও বডি দেখা যাবে:

![ReDoc](https://fastapi.tiangolo.com/img/index/index-06-redoc-02.png)

### সংক্ষেপে { #recap }

সংক্ষেপে, আপনি প্যারামিটার, বডি ইত্যাদির টাইপগুলো ফাংশনের প্যারামিটার হিসেবে **একবারই** ঘোষণা করেন।

এটি আপনি করেন স্ট্যান্ডার্ড আধুনিক Python টাইপ দিয়ে।

আপনাকে নতুন কোনো সিনট্যাক্স, কোনো নির্দিষ্ট লাইব্রেরির মেথড বা ক্লাস ইত্যাদি শিখতে হয় না।

শুধু স্ট্যান্ডার্ড **Python**।

যেমন, একটি `int`-এর জন্য:

⟦CODE7⟧

অথবা আরও জটিল একটি `Item` মডেলের জন্য:

⟦CODE8⟧

...আর এই একটি ঘোষণা থেকেই আপনি পান:

* এডিটর সাপোর্ট, যার মধ্যে আছে:
    * কমপ্লিশন।
    * টাইপ চেক।
* ডেটা ভ্যালিডেশন:
    * ডেটা অবৈধ হলে স্বয়ংক্রিয় ও স্পষ্ট এরর।
    * গভীরভাবে নেস্টেড JSON অবজেক্টের জন্যও ভ্যালিডেশন।
* ইনপুট ডেটার <dfn title="সিরিয়ালাইজেশন, পার্সিং, মার্শালিং নামেও পরিচিত">রূপান্তর</dfn>: নেটওয়ার্ক থেকে আসা ডেটাকে Python ডেটা ও টাইপে। যেখান থেকে পড়া যায়:
    * JSON।
    * পাথ প্যারামিটার।
    * কুয়েরি প্যারামিটার।
    * কুকি।
    * হেডার।
    * ফর্ম।
    * ফাইল।
* আউটপুট ডেটার <dfn title="সিরিয়ালাইজেশন, পার্সিং, মার্শালিং নামেও পরিচিত">রূপান্তর</dfn>: Python ডেটা ও টাইপ থেকে নেটওয়ার্ক ডেটায় (JSON হিসেবে) রূপান্তর:
    * Python টাইপ রূপান্তর (`str`, `int`, `float`, `bool`, `list` ইত্যাদি)।
    * `datetime` অবজেক্ট।
    * `UUID` অবজেক্ট।
    * ডেটাবেস মডেল।
    * ...এবং আরও অনেক কিছু।
* স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন, ২টি বিকল্প ইউজার ইন্টারফেসসহ:
    * Swagger UI।
    * ReDoc।

---

আগের কোড উদাহরণে ফিরে গেলে, **FastAPI**:

* `GET` ও `PUT` রিকোয়েস্টের পাথে একটি `item_id` আছে কিনা ভ্যালিডেট করবে।
* `GET` ও `PUT` রিকোয়েস্টের জন্য `item_id`-এর টাইপ `int` কিনা ভ্যালিডেট করবে।
    * যদি না হয়, ক্লায়েন্ট একটি কাজের, স্পষ্ট এরর দেখতে পাবে।
* `GET` রিকোয়েস্টের জন্য `q` নামে একটি ঐচ্ছিক কুয়েরি প্যারামিটার আছে কিনা দেখবে (যেমন `http://127.0.0.1:8000/items/foo?q=somequery`-তে)।
    * `q` প্যারামিটারটি `= None` দিয়ে ঘোষণা করা হয়েছে বলে এটি ঐচ্ছিক।
    * `None` না থাকলে এটি আবশ্যক হতো (যেমন `PUT`-এর ক্ষেত্রে বডি আবশ্যক)।
* `/items/{item_id}`-এ `PUT` রিকোয়েস্টের জন্য বডিকে JSON হিসেবে পড়বে:
    * এতে `name` নামে একটি আবশ্যক অ্যাট্রিবিউট আছে কিনা দেখবে, যা একটি `str` হওয়া উচিত।
    * এতে `price` নামে একটি আবশ্যক অ্যাট্রিবিউট আছে কিনা দেখবে, যা অবশ্যই একটি `float` হতে হবে।
    * এতে `is_offer` নামে একটি ঐচ্ছিক অ্যাট্রিবিউট আছে কিনা দেখবে, যা থাকলে একটি `bool` হওয়া উচিত।
    * এর সবকিছু গভীরভাবে নেস্টেড JSON অবজেক্টের জন্যও কাজ করবে।
* স্বয়ংক্রিয়ভাবে JSON-এ ও JSON থেকে রূপান্তর করবে।
* সবকিছু OpenAPI দিয়ে ডকুমেন্ট করবে, যা ব্যবহার করতে পারে:
    * ইন্টারঅ্যাকটিভ ডকুমেন্টেশন সিস্টেম।
    * অনেক ভাষার জন্য স্বয়ংক্রিয় ক্লায়েন্ট কোড জেনারেশন সিস্টেম।
* সরাসরি ২টি ইন্টারঅ্যাকটিভ ডকুমেন্টেশন ওয়েব ইন্টারফেস দেবে।

---

আমরা কেবল উপরিভাগটুকু ছুঁয়ে দেখলাম, কিন্তু সবকিছু কীভাবে কাজ করে তার ধারণা আপনি ইতিমধ্যে পেয়ে গেছেন।

এই লাইনটি পরিবর্তন করে দেখুন:

⟦CODE9⟧

...এটি থেকে:

⟦CODE10⟧

...এটিতে:

⟦CODE11⟧

...আর দেখুন আপনার এডিটর কীভাবে অ্যাট্রিবিউটগুলো অটো-কমপ্লিট করে এবং সেগুলোর টাইপ জানে:

![এডিটর সাপোর্ট](https://fastapi.tiangolo.com/img/vscode-completion.png)

আরও ফিচারসহ আরও সম্পূর্ণ উদাহরণের জন্য <a href="https://fastapi.tiangolo.com/tutorial/">টিউটোরিয়াল - ইউজার গাইড</a> দেখুন।

**আগাম জানিয়ে রাখি**: টিউটোরিয়াল - ইউজার গাইডে রয়েছে:

* অন্যান্য বিভিন্ন জায়গা থেকে **প্যারামিটার** ঘোষণা, যেমন: **হেডার**, **কুকি**, **ফর্ম ফিল্ড** এবং **ফাইল**।
* `maximum_length` বা `regex`-এর মতো **ভ্যালিডেশন শর্ত** কীভাবে সেট করবেন।
* খুবই শক্তিশালী ও ব্যবহারে সহজ একটি **<dfn title="কম্পোনেন্ট, রিসোর্স, প্রোভাইডার, সার্ভিস, ইনজেক্টেবল নামেও পরিচিত">ডিপেন্ডেন্সি ইনজেকশন</dfn>** সিস্টেম।
* সিকিউরিটি ও অথেনটিকেশন, যার মধ্যে আছে **JWT টোকেন**সহ **OAuth2** এবং **HTTP Basic** অথের সাপোর্ট।
* **গভীরভাবে নেস্টেড JSON মডেল** ঘোষণার আরও অ্যাডভান্সড (কিন্তু সমান সহজ) কৌশল (Pydantic-কে ধন্যবাদ)।
* [Strawberry](https://strawberry.rocks) ও অন্যান্য লাইব্রেরির সাথে **GraphQL** ইন্টিগ্রেশন।
* অনেক অতিরিক্ত ফিচার (Starlette-কে ধন্যবাদ), যেমন:
    * **WebSockets**
    * HTTPX ও `pytest`-ভিত্তিক অত্যন্ত সহজ টেস্ট
    * **CORS**
    * **কুকি সেশন**
    * ...এবং আরও অনেক কিছু।

### আপনার অ্যাপ ডিপ্লয় করুন (ঐচ্ছিক) { #deploy-your-app-optional }

চাইলে আপনি একটিমাত্র কমান্ড দিয়ে আপনার FastAPI অ্যাপ [FastAPI Cloud](https://fastapicloud.com)-এ ডিপ্লয় করতে পারেন। 🚀

<div class="termy">

⟦CODE12⟧

</div>

CLI স্বয়ংক্রিয়ভাবে আপনার FastAPI অ্যাপ্লিকেশন খুঁজে বের করে ক্লাউডে ডিপ্লয় করবে। আপনি লগ ইন করা না থাকলে অথেনটিকেশন প্রক্রিয়া সম্পন্ন করতে আপনার ব্রাউজার খুলবে।

ব্যস! এখন আপনি সেই URL-এ আপনার অ্যাপ অ্যাক্সেস করতে পারবেন। ✨

#### FastAPI Cloud সম্পর্কে { #about-fastapi-cloud }

**[FastAPI Cloud](https://fastapicloud.com)** তৈরি করেছেন **FastAPI**-এর পেছনের একই লেখক ও টিম।

এটি খুব কম পরিশ্রমে একটি API **তৈরি**, **ডিপ্লয়** এবং **অ্যাক্সেস** করার প্রক্রিয়াকে সহজ করে।

FastAPI দিয়ে অ্যাপ তৈরির যে **ডেভেলপার অভিজ্ঞতা**, সেটিই এটি ক্লাউডে **ডিপ্লয়** করার ক্ষেত্রেও নিয়ে আসে। 🎉

FastAPI Cloud হলো *FastAPI and friends* ওপেন সোর্স প্রজেক্টগুলোর প্রধান স্পনসর ও অর্থায়নকারী। ✨

#### অন্যান্য ক্লাউড প্রোভাইডারে ডিপ্লয় { #deploy-to-other-cloud-providers }

FastAPI ওপেন সোর্স এবং স্ট্যান্ডার্ড-ভিত্তিক। আপনি আপনার পছন্দের যেকোনো ক্লাউড প্রোভাইডারে FastAPI অ্যাপ ডিপ্লয় করতে পারেন।

আপনার ক্লাউড প্রোভাইডারে FastAPI অ্যাপ ডিপ্লয় করতে তাদের গাইড অনুসরণ করুন। 🤓

## পারফরম্যান্স { #performance }

স্বাধীন TechEmpower বেঞ্চমার্কে দেখা যায়, Uvicorn-এর অধীনে চলা **FastAPI** অ্যাপ্লিকেশনগুলো [সবচেয়ে দ্রুত Python ফ্রেমওয়ার্কগুলোর একটি](https://www.techempower.com/benchmarks/#section=test&runid=7464e520-0dc2-473d-bd34-dbdfd7e85911&hw=ph&test=query&l=zijzen-7), কেবল Starlette ও Uvicorn-এর নিচে (যেগুলো FastAPI ভেতরে ব্যবহার করে)। (*)

এ সম্পর্কে আরও বুঝতে [বেঞ্চমার্ক](https://fastapi.tiangolo.com/benchmarks/) অংশটি দেখুন।

## ডিপেন্ডেন্সি { #dependencies }

FastAPI নির্ভর করে Pydantic ও Starlette-এর ওপর।

### `standard` ডিপেন্ডেন্সি { #standard-dependencies }

যখন আপনি `uv add "fastapi[standard]"` দিয়ে FastAPI ইনস্টল করেন, তখন এর সাথে ঐচ্ছিক ডিপেন্ডেন্সির `standard` গ্রুপটি আসে:

Pydantic যেগুলো ব্যবহার করে:

* [`email-validator`](https://github.com/JoshData/python-email-validator) - ইমেইল ভ্যালিডেশনের জন্য।

Starlette যেগুলো ব্যবহার করে:

* [`httpx`](https://www.python-httpx.org) - আপনি `TestClient` ব্যবহার করতে চাইলে প্রয়োজন।
* [`jinja2`](https://jinja.palletsprojects.com) - আপনি ডিফল্ট টেমপ্লেট কনফিগারেশন ব্যবহার করতে চাইলে প্রয়োজন।
* [`python-multipart`](https://github.com/Kludex/python-multipart) - আপনি `request.form()` দিয়ে ফর্ম <dfn title="HTTP রিকোয়েস্ট থেকে আসা স্ট্রিংকে Python ডেটায় রূপান্তর করা">"পার্সিং"</dfn> সাপোর্ট করতে চাইলে প্রয়োজন।

FastAPI যেগুলো ব্যবহার করে:

* [`uvicorn`](https://uvicorn.dev) - সেই সার্ভারের জন্য যা আপনার অ্যাপ্লিকেশন লোড করে ও সার্ভ করে। এর মধ্যে `uvicorn[standard]` আছে, যাতে উচ্চ পারফরম্যান্সে সার্ভ করার জন্য প্রয়োজনীয় কিছু ডিপেন্ডেন্সি (যেমন `uvloop`) রয়েছে।
* `fastapi-cli[standard]` - `fastapi` কমান্ড দেওয়ার জন্য।
    * এর মধ্যে আছে `fastapi-cloud-cli`, যা দিয়ে আপনি আপনার FastAPI অ্যাপ্লিকেশন [FastAPI Cloud](https://fastapicloud.com)-এ ডিপ্লয় করতে পারেন।

### `standard` ডিপেন্ডেন্সি ছাড়া { #without-standard-dependencies }

আপনি যদি `standard` ঐচ্ছিক ডিপেন্ডেন্সিগুলো যুক্ত করতে না চান, তাহলে `uv add "fastapi[standard]"`-এর বদলে `uv add fastapi` দিয়ে ইনস্টল করতে পারেন।

### `fastapi-cloud-cli` ছাড়া { #without-fastapi-cloud-cli }

আপনি যদি স্ট্যান্ডার্ড ডিপেন্ডেন্সিসহ কিন্তু `fastapi-cloud-cli` ছাড়া FastAPI ইনস্টল করতে চান, তাহলে `uv add "fastapi[standard-no-fastapi-cloud-cli]"` দিয়ে ইনস্টল করতে পারেন।

### অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি { #additional-optional-dependencies }

আরও কিছু অতিরিক্ত ডিপেন্ডেন্সি আছে যা আপনি ইনস্টল করতে চাইতে পারেন।

Pydantic-এর অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি:

* [`pydantic-settings`](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/) - সেটিংস ব্যবস্থাপনার জন্য।
* [`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types) - Pydantic-এর সাথে ব্যবহারের জন্য অতিরিক্ত টাইপের জন্য।

FastAPI-এর অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি:

* [`orjson`](https://github.com/ijl/orjson) - আপনি `ORJSONResponse` ব্যবহার করতে চাইলে প্রয়োজন।
* [`ujson`](https://github.com/ultrajson/ultrajson) - আপনি `UJSONResponse` ব্যবহার করতে চাইলে প্রয়োজন।

## লাইসেন্স { #license }

এই প্রজেক্টটি MIT লাইসেন্সের শর্তাবলির অধীনে লাইসেন্সপ্রাপ্ত।
