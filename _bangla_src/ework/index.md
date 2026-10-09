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
    <em>FastAPI ফ্রেমওয়ার্ক: খুব দ্রুত চলে, শেখা সহজ, কোড লেখা দ্রুত, আর সরাসরি আসল কাজে (প্রোডাকশনে) ব্যবহারের উপযোগী</em>
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

**ডকুমেন্টেশন (ইংরেজি মূল সাইট)**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

**সোর্স কোড**: [https://github.com/fastapi/fastapi](https://github.com/fastapi/fastapi)

---

/// note | এই পেজে যা শিখবেন

* FastAPI আসলে কী, আর কেন এত মানুষ এটি ব্যবহার করে।
* মাত্র কয়েক লাইনের কোড দিয়ে কীভাবে নিজের প্রথম API বানাবেন ও চালাবেন।
* ব্রাউজারে কীভাবে আপনার API-এর স্বয়ংক্রিয় ডকুমেন্টেশন দেখবেন ও সেখান থেকেই API পরীক্ষা করবেন।
* FastAPI ইনস্টল করার সময় কোন কোন প্যাকেজ সাথে আসে, আর সেগুলো কী কাজে লাগে।

///

FastAPI হলো Python দিয়ে **API** বানানোর জন্য একটি আধুনিক ও খুব দ্রুত **ওয়েব ফ্রেমওয়ার্ক**। এটি Python-এর সাধারণ **টাইপ হিন্ট** (type hints) ব্যবহার করে কাজ করে।

/// tip | শব্দগুলো সহজ ভাষায়

* **API** (Application Programming Interface): দুটি প্রোগ্রাম একে অপরের সাথে কীভাবে কথা বলবে, তার নিয়ম। যেমন আপনার মোবাইল অ্যাপ সার্ভারের কাছে জিজ্ঞেস করে "এই ইউজারের তথ্য দাও", আর সার্ভার উত্তর পাঠায়। এই প্রশ্ন-উত্তরের ব্যবস্থাটাই API।
* **ওয়েব ফ্রেমওয়ার্ক**: আগে থেকে তৈরি করা একগুচ্ছ টুল ও নিয়ম, যাতে আপনাকে ওয়েব সার্ভারের সব খুঁটিনাটি শূন্য থেকে লিখতে না হয়। আপনি শুধু নিজের কাজের অংশটুকু লেখেন, বাকিটা ফ্রেমওয়ার্ক সামলায়।
* **টাইপ হিন্ট**: Python-এ কোনো ভেরিয়েবলের পাশে লিখে দেওয়া যে এটি কোন ধরনের ডেটা, যেমন `age: int` মানে `age` একটি পূর্ণসংখ্যা। FastAPI এই তথ্য দেখেই ডেটা যাচাই করে, রূপান্তর করে আর ডকুমেন্টেশন বানায়।

একটি রেস্তোরাঁর কথা ভাবুন। আপনি (ক্লায়েন্ট) ওয়েটারকে অর্ডার দেন, ওয়েটার রান্নাঘরে (সার্ভার) নিয়ে যায়, তারপর খাবার (রেসপন্স) এনে দেয়। API হলো সেই ওয়েটার আর মেনুকার্ড। FastAPI আপনাকে খুব সহজে এমন একজন দক্ষ "ওয়েটার" বানাতে সাহায্য করে।

///

এর প্রধান সুবিধাগুলো হলো:

* **দ্রুত**: খুবই উচ্চ পারফরম্যান্স, **NodeJS** ও **Go**-এর সমপর্যায়ের (Starlette ও Pydantic-এর কল্যাণে)। [Python-এর সবচেয়ে দ্রুত ফ্রেমওয়ার্কগুলোর একটি](#performance)। অর্থাৎ একই সময়ে অনেক বেশি রিকোয়েস্ট সামলাতে পারে।
* **কোড লেখা দ্রুত**: নতুন ফিচার বানানোর গতি প্রায় ২০০% থেকে ৩০০% বেড়ে যায়। *
* **কম বাগ**: মানুষের (ডেভেলপারের) হাতে হওয়া ভুল প্রায় ৪০% কমে যায়। *
* **সহজবোধ্য**: এডিটরে দারুণ সাপোর্ট। সব জায়গায় <dfn title="অটো-কমপ্লিট, অটোকমপ্লিশন বা IntelliSense নামেও পরিচিত">কমপ্লিশন</dfn>, মানে কিছু টাইপ করা শুরু করলেই এডিটর বাকিটা সাজেস্ট করে। ফলে ভুল খুঁজতে (ডিবাগ করতে) কম সময় লাগে।
* **সহজ**: ব্যবহার ও শেখা সহজ হবে, এভাবেই এটি ডিজাইন করা। ডকুমেন্টেশন পড়তে কম সময় লাগে।
* **সংক্ষিপ্ত**: একই কোড বারবার লিখতে হয় না। একটি প্যারামিটার একবার ঘোষণা করলেই অনেকগুলো সুবিধা একসাথে পাওয়া যায়। ফলে বাগও কম।
* **মজবুত**: প্রোডাকশনে (আসল ব্যবহারকারীদের জন্য) চালানোর উপযোগী কোড পাবেন। সাথে স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ ডকুমেন্টেশন।
* **স্ট্যান্ডার্ড-ভিত্তিক**: API-এর জন্য প্রচলিত উন্মুক্ত স্ট্যান্ডার্ডের ওপর তৈরি এবং সেগুলোর সাথে পুরোপুরি সামঞ্জস্যপূর্ণ: [OpenAPI](https://github.com/OAI/OpenAPI-Specification) (আগে Swagger নামে পরিচিত ছিল) এবং [JSON Schema](https://json-schema.org/)। স্ট্যান্ডার্ড মানে সবার মেনে চলা একটি নিয়ম, তাই অন্য অনেক টুল আপনার API সহজেই বুঝতে পারে।

<small>* প্রোডাকশন অ্যাপ্লিকেশন বানানো একটি অভ্যন্তরীণ ডেভেলপমেন্ট টিমের পরীক্ষার ভিত্তিতে করা অনুমান।</small>

## স্পন্সর { #sponsors }

যেসব প্রতিষ্ঠান আর্থিক সহায়তা দিয়ে FastAPI-কে টিকিয়ে রাখে ও উন্নত করতে সাহায্য করে:

<!-- sponsors -->

### কিস্টোন স্পন্সর { #keystone-sponsor }

<div class="fastapi-sponsors fastapi-sponsors--keystone">
{% for sponsor in sponsors.keystone -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--keystone" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}"></a>
{% endfor -%}
</div>

### গোল্ড স্পন্সর { #gold-sponsors }

<div class="fastapi-sponsors fastapi-sponsors--gold">
{% for sponsor in sponsors.gold -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--gold" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}" loading="lazy"></a>
{% endfor -%}
</div>

### সিলভার স্পন্সর { #silver-sponsors }

<div class="fastapi-sponsors fastapi-sponsors--silver">
{% for sponsor in sponsors.silver -%}
<a class="fastapi-sponsors__card fastapi-sponsors__card--silver" href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img class="fastapi-sponsors__banner" src="{{ sponsor.img }}" alt="{{ sponsor.title }}" loading="lazy"></a>
{% endfor %}
</div>

<!-- /sponsors -->

[অন্যান্য স্পন্সর](https://fastapi.tiangolo.com/fastapi-people/#sponsors)

## মতামত { #opinions }

বড় বড় প্রতিষ্ঠানের ইঞ্জিনিয়াররা FastAPI সম্পর্কে যা বলেছেন:

<!-- only-mkdocs -->
<div class="fastapi-opinions" data-fastapi-opinions>
  <div class="fastapi-opinions__tabs" role="tablist" aria-label="Companies using FastAPI">
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
    <blockquote class="fastapi-opinions__quote">"আমি আজকাল প্রচুর <strong>FastAPI</strong> ব্যবহার করছি। আসলে আমি আমার টিমের <strong>Microsoft-এর সব ML সার্ভিসে</strong> এটি ব্যবহারের পরিকল্পনা করছি। এগুলোর কিছু মূল <strong>Windows</strong> প্রোডাক্টে আর কিছু <strong>Office</strong> প্রোডাক্টে যুক্ত হচ্ছে।"</blockquote>
    <div class="fastapi-opinions__attr">— Kabir Khan, <strong>Microsoft</strong> <a href="https://github.com/fastapi/fastapi/pull/26">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-uber" role="tabpanel" aria-labelledby="fo-tab-uber" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"আমরা একটি <strong>REST</strong> সার্ভার চালু করতে <strong>FastAPI</strong> লাইব্রেরি গ্রহণ করেছি, যাকে কুয়েরি করে <strong>প্রেডিকশন</strong> (মেশিন লার্নিং মডেলের পূর্বাভাস) পাওয়া যায়।" <em>[Ludwig-এর জন্য]</em></blockquote>
    <div class="fastapi-opinions__attr">— Piero Molino, Yaroslav Dudin, Sai Sumanth Miryala, <strong>Uber</strong> <a href="https://www.uber.com/us/en/blog/ludwig-v0-2/">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-netflix" role="tabpanel" aria-labelledby="fo-tab-netflix" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"<strong>Netflix</strong> আনন্দের সাথে জানাচ্ছে যে আমাদের <strong>সংকট ব্যবস্থাপনা</strong> (crisis management) অর্কেস্ট্রেশন ফ্রেমওয়ার্ক <strong>Dispatch</strong> এখন ওপেন-সোর্স!" <em>[FastAPI দিয়ে তৈরি]</em></blockquote>
    <div class="fastapi-opinions__attr">— Kevin Glisson, Marc Vilanova, Forest Monsen, <strong>Netflix</strong> <a href="https://netflixtechblog.com/introducing-dispatch-da4b8a2a8072">(সূত্র)</a></div>
  </div>
  <div class="fastapi-opinions__panel" id="fo-panel-cisco" role="tabpanel" aria-labelledby="fo-tab-cisco" tabindex="0" hidden>
    <blockquote class="fastapi-opinions__quote">"কেউ যদি প্রোডাকশনের জন্য Python API বানাতে চান, আমি জোরালোভাবে <strong>FastAPI</strong>-এর সুপারিশ করব। এটি <strong>সুন্দরভাবে ডিজাইন করা</strong>, <strong>ব্যবহারে সহজ</strong> এবং <strong>সহজে বড় পরিসরে চালানো যায়</strong>। আমাদের API-কেন্দ্রিক ডেভেলপমেন্ট কৌশলে এটি একটি <strong>গুরুত্বপূর্ণ অংশ</strong> হয়ে উঠেছে।"</blockquote>
    <div class="fastapi-opinions__attr">— Deon Pillsbury, <strong>Cisco</strong> <a href="https://www.linkedin.com/posts/deonpillsbury_cisco-cx-python-activity-6963242628536487936-trAp/">(সূত্র)</a></div>
  </div>
</div>
<!-- /only-mkdocs -->

<div class="only-github" markdown="1">

"_[...] আমি আজকাল প্রচুর **FastAPI** ব্যবহার করছি। [...] আসলে আমি আমার টিমের **Microsoft-এর সব ML সার্ভিসে** এটি ব্যবহারের পরিকল্পনা করছি। এগুলোর কিছু মূল **Windows** প্রোডাক্টে আর কিছু **Office** প্রোডাক্টে যুক্ত হচ্ছে।_"

<div style="text-align: right; margin-right: 10%;">Kabir Khan - <strong>Microsoft</strong> <a href="https://github.com/fastapi/fastapi/pull/26"><small>(সূত্র)</small></a></div>

---

"_আমরা একটি **REST** সার্ভার চালু করতে **FastAPI** লাইব্রেরি গ্রহণ করেছি, যাকে কুয়েরি করে **প্রেডিকশন** পাওয়া যায়। [Ludwig-এর জন্য]_"

<div style="text-align: right; margin-right: 10%;">Piero Molino, Yaroslav Dudin, and Sai Sumanth Miryala - <strong>Uber</strong> <a href="https://www.uber.com/us/en/blog/ludwig-v0-2/"><small>(সূত্র)</small></a></div>

---

"_**Netflix** আনন্দের সাথে জানাচ্ছে যে আমাদের **সংকট ব্যবস্থাপনা** অর্কেস্ট্রেশন ফ্রেমওয়ার্ক **Dispatch** এখন ওপেন-সোর্স! [**FastAPI** দিয়ে তৈরি]_"

<div style="text-align: right; margin-right: 10%;">Kevin Glisson, Marc Vilanova, Forest Monsen - <strong>Netflix</strong> <a href="https://netflixtechblog.com/introducing-dispatch-da4b8a2a8072"><small>(সূত্র)</small></a></div>

---

"_কেউ যদি প্রোডাকশনের জন্য Python API বানাতে চান, আমি জোরালোভাবে **FastAPI**-এর সুপারিশ করব। এটি **সুন্দরভাবে ডিজাইন করা**, **ব্যবহারে সহজ** এবং **সহজে বড় পরিসরে চালানো যায়**। আমাদের API-কেন্দ্রিক ডেভেলপমেন্ট কৌশলে এটি একটি **গুরুত্বপূর্ণ অংশ** হয়ে উঠেছে, এবং আমাদের Virtual TAC Engineer-সহ অনেক অটোমেশন ও সার্ভিস এটি দিয়েই চলছে।_"

<div style="text-align: right; margin-right: 10%;">Deon Pillsbury - <strong>Cisco</strong> <a href="https://www.linkedin.com/posts/deonpillsbury_cisco-cx-python-activity-6963242628536487936-trAp/"><small>(সূত্র)</small></a></div>

---

</div>

## FastAPI মিনি ডকুমেন্টারি { #fastapi-mini-documentary }

২০২৫ সালের শেষে FastAPI নিয়ে একটি [ছোট ডকুমেন্টারি](https://www.youtube.com/watch?v=mpR8ngthqiE) প্রকাশিত হয়েছে। FastAPI কীভাবে শুরু হলো আর কীভাবে এত জনপ্রিয় হলো, তা জানতে অনলাইনে দেখে নিতে পারেন:

<a class="fastapi-feature-banner" href="https://www.youtube.com/watch?v=mpR8ngthqiE"><img src="https://fastapi.tiangolo.com/img/fastapi-documentary.jpg" alt="FastAPI Mini Documentary"></a>

## **Typer**, কমান্ড লাইনের FastAPI { #typer-the-fastapi-of-clis }

<a href="https://typer.tiangolo.com"><img src="https://typer.tiangolo.com/img/logo-margin/logo-margin-vector.svg" style="width: 20%;"></a>

আপনি যদি ওয়েব API-এর বদলে টার্মিনালে চালানোর মতো একটি <abbr title="Command Line Interface - কমান্ড লাইন ইন্টারফেস">CLI</abbr> অ্যাপ বানাতে চান, তাহলে [**Typer**](https://typer.tiangolo.com/) দেখুন। CLI অ্যাপ মানে এমন প্রোগ্রাম যা মাউস-বাটনের বদলে টার্মিনালে কমান্ড লিখে চালানো হয়।

**Typer** হলো FastAPI-এর ছোট ভাই। একই লেখকের তৈরি, একই চিন্তাধারায়। এটিকে বলা হয় **কমান্ড লাইনের FastAPI**। ⌨️ 🚀

## যা যা লাগবে { #requirements }

FastAPI দাঁড়িয়ে আছে দুটি শক্তিশালী লাইব্রেরির কাঁধে:

* ওয়েবের অংশগুলোর জন্য [Starlette](https://starlette.dev/)। রিকোয়েস্ট গ্রহণ করা, রেসপন্স পাঠানো, রাউটিং, এসব কাজ এটি করে।
* ডেটার অংশগুলোর জন্য [Pydantic](https://pydantic.dev/docs/)। ডেটা ঠিক আছে কিনা যাচাই করা আর এক রূপ থেকে আরেক রূপে বদলানো, এসব কাজ এটি করে।

FastAPI এই দুটিকে একসাথে জুড়ে সহজ ও সুন্দর একটি ব্যবস্থা তৈরি করেছে। আপনাকে আলাদা করে এগুলো ইনস্টল করতে হবে না, FastAPI-এর সাথেই চলে আসে।

## ইনস্টলেশন { #installation }

প্রথমে [`uv` ইনস্টল করুন](https://docs.astral.sh/uv/getting-started/installation/)। `uv` হলো Python প্রজেক্ট ও প্যাকেজ সামলানোর একটি দ্রুত টুল। তারপর আপনার প্রজেক্টে FastAPI যোগ করুন:

<div class="termy">

⟦CODE1⟧

</div>

**নোট**: `"fastapi[standard]"` অবশ্যই উদ্ধৃতিচিহ্নের (`" "`) ভেতরে লিখবেন। কিছু টার্মিনালে (যেমন zsh) `[` `]` চিহ্নের বিশেষ অর্থ আছে, উদ্ধৃতিচিহ্ন না দিলে কমান্ডটি ভুলভাবে বোঝা হতে পারে।

/// info | `[standard]` মানে কী?

শুধু `fastapi` লিখলে কেবল মূল লাইব্রেরি ইনস্টল হয়। `fastapi[standard]` লিখলে সাথে দরকারি কিছু অতিরিক্ত প্যাকেজও ইনস্টল হয়, যেমন সার্ভার চালানোর জন্য Uvicorn আর `fastapi` কমান্ড। শুরুতে `standard` দিয়েই ইনস্টল করা সবচেয়ে সহজ। পুরো তালিকা এই পেজের শেষে [ডিপেন্ডেন্সি](#dependencies) অংশে আছে।

///

আপনি যদি `pip` ব্যবহার করতে চান, তাহলে একটি ভার্চুয়াল এনভায়রনমেন্টের ভেতরে `fastapi[standard]` ইনস্টল করুন। বিকল্প ধাপগুলো [ইনস্টলেশন গাইডে](tutorial/#install-fastapi) দেখুন।

## উদাহরণ { #example }

এবার হাতে-কলমে একটি ছোট API বানিয়ে দেখা যাক।

### তৈরি করুন { #create-it }

`main.py` নামে একটি ফাইল তৈরি করে এতে লিখুন:

⟦CODE2⟧

/// info | কোডটি সহজ ভাষায়

* `from fastapi import FastAPI`: FastAPI লাইব্রেরি থেকে `FastAPI` ক্লাসটি নিয়ে আসা হলো।
* `app = FastAPI()`: আপনার পুরো অ্যাপ্লিকেশনের "মূল বস্তু" তৈরি হলো। সব রাউট (ঠিকানা) এর সাথেই যুক্ত হবে।
* `@app.get("/")`: এটি একটি **ডেকোরেটর**। এটি FastAPI-কে বলছে, "কেউ যদি `/` ঠিকানায় `GET` রিকোয়েস্ট পাঠায়, তাহলে ঠিক নিচের ফাংশনটি চালাও"।
* `def read_root(): return {"Hello": "World"}`: এই ফাংশন যা রিটার্ন করে, FastAPI সেটিকে স্বয়ংক্রিয়ভাবে JSON বানিয়ে ক্লায়েন্টকে পাঠায়।
* `@app.get("/items/{item_id}")`: এখানে `{item_id}` একটি **পাথ প্যারামিটার**, মানে ঠিকানার এই অংশটি বদলাতে পারে, যেমন `/items/5` বা `/items/42`।
* `def read_item(item_id: int, q: str | None = None)`:
    * `item_id: int` মানে ঠিকানা থেকে আসা মানটি অবশ্যই পূর্ণসংখ্যা হতে হবে। কেউ `/items/abc` পাঠালে FastAPI নিজেই সুন্দর একটি এরর ফেরত দেবে।
    * `q: str | None = None` মানে `q` একটি ঐচ্ছিক **কুয়েরি প্যারামিটার**। এটি URL-এর `?` চিহ্নের পরে আসে, যেমন `?q=somequery`। না দিলে এর মান হবে `None`।

///

<details markdown="1">
<summary>অথবা <code>async def</code> ব্যবহার করুন...</summary>

আপনার কোড যদি `async` / `await` ব্যবহার করে (যেমন ডেটাবেস বা অন্য API থেকে অপেক্ষা করে ডেটা আনে), তাহলে `async def` ব্যবহার করুন:

⟦CODE3⟧

**নোট**:

এটা কখন লাগে তা নিশ্চিত না হলে, ডকুমেন্টেশনে [`async` ও `await` নিয়ে](https://fastapi.tiangolo.com/async/#in-a-hurry) _"তাড়া আছে?"_ অংশটি দেখুন। শুরুতে সাধারণ `def` ব্যবহার করলেও কোনো সমস্যা নেই।

</details>

### চালান { #run-it }

এই কমান্ড দিয়ে সার্ভার চালু করুন:

<div class="termy">

⟦CODE4⟧

</div>

আউটপুটে দেখবেন `Serving at: http://127.0.0.1:8000`। মানে আপনার কম্পিউটারেই (`127.0.0.1` মানে "এই কম্পিউটার") ৮০০০ নম্বর পোর্টে সার্ভারটি চলছে। থামাতে চাইলে টার্মিনালে `CTRL+C` চাপুন।

<details markdown="1">
<summary><code>fastapi dev</code> কমান্ডটি সম্পর্কে...</summary>

`fastapi dev` কমান্ডটি স্বয়ংক্রিয়ভাবে আপনার `main.py` ফাইল পড়ে, এর ভেতরের **FastAPI** অ্যাপটি খুঁজে বের করে, এবং [Uvicorn](https://uvicorn.dev) ব্যবহার করে একটি সার্ভার চালু করে। Uvicorn হলো সেই সার্ভার প্রোগ্রাম যা আসলে নেটওয়ার্ক থেকে রিকোয়েস্ট গ্রহণ করে আপনার অ্যাপের কাছে পৌঁছে দেয়।

ডিফল্টভাবে `fastapi dev` **অটো-রিলোড** চালু রেখে শুরু হয়। মানে আপনি কোড বদলে ফাইল সেভ করলেই সার্ভার নিজে থেকে নতুন কোড লোড করে নেয়, বারবার বন্ধ-চালু করতে হয় না। এটি নিজের কম্পিউটারে ডেভেলপমেন্টের জন্য।

এ সম্পর্কে আরও পড়ুন [FastAPI CLI ডকুমেন্টেশনে](https://fastapi.tiangolo.com/fastapi-cli/)।

</details>

### পরীক্ষা করুন { #check-it }

ব্রাউজারে খুলুন [http://127.0.0.1:8000/items/5?q=somequery](http://127.0.0.1:8000/items/5?q=somequery)।

আপনি এই JSON রেসপন্স দেখবেন:

```JSON
{"item_id": 5, "q": "somequery"}
```

লক্ষ করুন, URL-এ `5` লেখা ছিল টেক্সট হিসেবে, কিন্তু রেসপন্সে এটি সংখ্যা `5` (উদ্ধৃতিচিহ্ন ছাড়া)। কারণ আপনি `item_id: int` লিখেছিলেন, তাই FastAPI নিজেই এটিকে সংখ্যায় রূপান্তর করেছে।

এর মাধ্যমে আপনি ইতিমধ্যে এমন একটি API বানিয়ে ফেলেছেন যা:

* `/` এবং `/items/{item_id}` এই দুটি _পাথে_ (ঠিকানায়) HTTP রিকোয়েস্ট গ্রহণ করে।
* দুটি _পাথই_ `GET` <em>অপারেশন</em> গ্রহণ করে (যাকে HTTP _মেথড_-ও বলা হয়)। `GET` মানে "তথ্য পড়তে চাই"।
* `/items/{item_id}` _পাথে_ একটি _পাথ প্যারামিটার_ `item_id` আছে, যা একটি `int` হওয়া উচিত।
* `/items/{item_id}` _পাথে_ একটি ঐচ্ছিক `str` _কুয়েরি প্যারামিটার_ `q` আছে।

/// tip | একটু থেমে চেষ্টা করুন

ব্রাউজারে [http://127.0.0.1:8000/items/abc](http://127.0.0.1:8000/items/abc) খুলে দেখুন। `abc` পূর্ণসংখ্যা নয়, তাই FastAPI একটি পরিষ্কার এরর দেখাবে, যেখানে লেখা থাকবে কোন জায়গায় কী ভুল হয়েছে। এই যাচাইয়ের জন্য আপনাকে একটি লাইনও আলাদা করে লিখতে হয়নি।

///

### ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন { #interactive-api-docs }

এবার যান [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ।

আপনি স্বয়ংক্রিয়ভাবে তৈরি হওয়া ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন দেখবেন (যা [Swagger UI](https://github.com/swagger-api/swagger-ui) দিয়ে তৈরি)। এখানে আপনার API-এর সব পাথ, প্যারামিটার আর রেসপন্সের তালিকা থাকে, আর এখান থেকেই সেগুলো চালিয়ে দেখা যায়:

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### বিকল্প API ডকুমেন্টেশন { #alternative-api-docs }

এবার যান [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)-এ।

আপনি আরেকটি বিকল্প স্বয়ংক্রিয় ডকুমেন্টেশন দেখবেন (যা [ReDoc](https://github.com/Redocly/redoc) দিয়ে তৈরি)। এটি পড়ার জন্য বেশি সুবিধাজনক, তবে এখান থেকে API চালানো যায় না:

![ReDoc](https://fastapi.tiangolo.com/img/index/index-02-redoc-simple.png)

/// note | এই ডকুমেন্টেশন কোথা থেকে এলো?

আপনি কোনো ডকুমেন্টেশন লেখেননি। FastAPI আপনার কোড (পাথ, টাইপ হিন্ট, ফাংশন) দেখে **OpenAPI** নামের স্ট্যান্ডার্ড ফরম্যাটে API-এর একটি বিবরণ বানায়। Swagger UI আর ReDoc সেই বিবরণ পড়ে সুন্দর পেজ দেখায়। তাই কোড বদলালে ডকুমেন্টেশনও নিজে থেকে বদলে যায়।

///

## উদাহরণটি আরও উন্নত করা { #example-upgrade }

এবার `main.py` ফাইলটি বদলান, যাতে এটি একটি `PUT` রিকোয়েস্ট থেকে **বডি** গ্রহণ করতে পারে। `PUT` সাধারণত কোনো তথ্য হালনাগাদ (আপডেট) করতে ব্যবহার হয়। বডি হলো রিকোয়েস্টের সাথে পাঠানো মূল ডেটা, সাধারণত JSON আকারে।

Pydantic-এর কল্যাণে বডিটি সাধারণ Python টাইপ দিয়েই ঘোষণা করা যায়।

⟦CODE5⟧

/// info | কোডটি সহজ ভাষায় (নতুন অংশগুলো)

* `from pydantic import BaseModel`: Pydantic থেকে `BaseModel` আনা হলো। এটি দিয়ে ডেটার "ছাঁচ" (মডেল) বানানো হয়।
* `class Item(BaseModel):` এর নিচের তিন লাইন বলছে, একটি `Item`-এ থাকবে:
    * `name: str`: নাম, যা টেক্সট হতে হবে, এবং দিতেই হবে।
    * `price: float`: দাম, যা দশমিক সংখ্যা হতে পারে, এবং দিতেই হবে।
    * `is_offer: bool | None = None`: অফার আছে কিনা (`true`/`false`), এটি ঐচ্ছিক।
* `@app.put("/items/{item_id}")`: `/items/{item_id}` ঠিকানায় `PUT` রিকোয়েস্ট এলে নিচের ফাংশন চলবে।
* `def update_item(item_id: int, item: Item)`: `item_id` আসবে ঠিকানা থেকে, আর `item` আসবে রিকোয়েস্টের বডি থেকে। FastAPI বুঝে নেয় কোনটা কোথা থেকে আসবে: পাথে যার নাম আছে সেটি পাথ প্যারামিটার, আর Pydantic মডেল টাইপের প্যারামিটার হলো বডি।
* `return {"item_name": item.name, "item_id": item_id}`: বডি থেকে পাওয়া নাম আর পাথের আইডি ফেরত পাঠানো হলো।

///

`fastapi dev` সার্ভারটি স্বয়ংক্রিয়ভাবে রিলোড হয়ে যাওয়ার কথা।

### ইন্টারঅ্যাকটিভ API ডকুমেন্টেশনের পরিবর্তন { #interactive-api-docs-upgrade }

এবার যান [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)-এ।

* ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন স্বয়ংক্রিয়ভাবে আপডেট হয়ে যাবে, নতুন বডিসহ:

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

* "Try it out" বাটনে ক্লিক করুন। এতে আপনি প্যারামিটারগুলো পূরণ করে সরাসরি API-এর সাথে কাজ করতে পারবেন:

![Swagger UI interaction](https://fastapi.tiangolo.com/img/index/index-04-swagger-03.png)

* তারপর "Execute" বাটনে ক্লিক করুন। ইউজার ইন্টারফেসটি আপনার API-এর সাথে যোগাযোগ করবে, প্যারামিটারগুলো পাঠাবে, ফলাফল নিয়ে আসবে আর স্ক্রিনে দেখাবে:

![Swagger UI interaction](https://fastapi.tiangolo.com/img/index/index-05-swagger-04.png)

### বিকল্প API ডকুমেন্টেশনের পরিবর্তন { #alternative-api-docs-upgrade }

এবার যান [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)-এ।

* বিকল্প ডকুমেন্টেশনেও নতুন কুয়েরি প্যারামিটার ও বডি দেখা যাবে:

![ReDoc](https://fastapi.tiangolo.com/img/index/index-06-redoc-02.png)

### সংক্ষেপে { #recap }

সারকথা হলো, প্যারামিটার, বডি ইত্যাদির টাইপ আপনি **মাত্র একবার** ঘোষণা করেন, ফাংশনের প্যারামিটার হিসেবে।

এটি করেন সাধারণ আধুনিক Python টাইপ দিয়ে।

কোনো নতুন সিনট্যাক্স, কোনো নির্দিষ্ট লাইব্রেরির বিশেষ মেথড বা ক্লাস আলাদা করে শিখতে হয় না।

শুধু সাধারণ **Python**।

যেমন একটি `int`-এর জন্য:

```Python
item_id: int
```

অথবা আরও জটিল একটি `Item` মডেলের জন্য:

```Python
item: Item
```

...আর ওই একটি ঘোষণা থেকেই আপনি পান:

* এডিটর সাপোর্ট, যার মধ্যে আছে:
    * কমপ্লিশন (লেখার সময় সাজেশন)।
    * টাইপ যাচাই (ভুল টাইপ ব্যবহার করলে এডিটর আগেই সতর্ক করে)।
* ডেটা ভ্যালিডেশন (যাচাই):
    * ডেটা ভুল হলে স্বয়ংক্রিয় ও পরিষ্কার এরর।
    * অনেক স্তরে সাজানো (nested) JSON অবজেক্টের ক্ষেত্রেও যাচাই।
* ইনপুট ডেটার <dfn title="সিরিয়ালাইজেশন, পার্সিং বা মার্শালিং নামেও পরিচিত">রূপান্তর</dfn>: নেটওয়ার্ক থেকে আসা ডেটাকে Python ডেটা ও টাইপে বদলানো। যেসব জায়গা থেকে পড়া যায়:
    * JSON।
    * পাথ প্যারামিটার।
    * কুয়েরি প্যারামিটার।
    * কুকি।
    * হেডার।
    * ফর্ম।
    * ফাইল।
* আউটপুট ডেটার <dfn title="সিরিয়ালাইজেশন, পার্সিং বা মার্শালিং নামেও পরিচিত">রূপান্তর</dfn>: Python ডেটা ও টাইপকে নেটওয়ার্কের ডেটায় (JSON হিসেবে) বদলানো:
    * Python টাইপ রূপান্তর (`str`, `int`, `float`, `bool`, `list` ইত্যাদি)।
    * `datetime` অবজেক্ট।
    * `UUID` অবজেক্ট।
    * ডেটাবেস মডেল।
    * ...এবং আরও অনেক কিছু।
* স্বয়ংক্রিয় ইন্টারঅ্যাকটিভ API ডকুমেন্টেশন, দুটি বিকল্প ইউজার ইন্টারফেসসহ:
    * Swagger UI।
    * ReDoc।

---

আগের কোড উদাহরণে ফিরে গেলে, **FastAPI** যা যা করবে:

* `GET` ও `PUT` রিকোয়েস্টের পাথে একটি `item_id` আছে কিনা যাচাই করবে।
* `GET` ও `PUT` রিকোয়েস্টের `item_id` যে `int` টাইপের, তা যাচাই করবে।
    * না হলে ক্লায়েন্ট একটি কাজের, পরিষ্কার এরর দেখবে।
* `GET` রিকোয়েস্টে `q` নামে একটি ঐচ্ছিক কুয়েরি প্যারামিটার আছে কিনা দেখবে (যেমন `http://127.0.0.1:8000/items/foo?q=somequery`)।
    * `q` প্যারামিটারটি `= None` দিয়ে ঘোষণা করা হয়েছে, তাই এটি ঐচ্ছিক।
    * `None` না থাকলে এটি আবশ্যক হতো (যেমন `PUT`-এর ক্ষেত্রে বডি আবশ্যক)।
* `/items/{item_id}`-এ `PUT` রিকোয়েস্টের বডি JSON হিসেবে পড়বে:
    * যাচাই করবে যে এতে আবশ্যক অ্যাট্রিবিউট `name` আছে, যা একটি `str` হওয়া উচিত।
    * যাচাই করবে যে এতে আবশ্যক অ্যাট্রিবিউট `price` আছে, যা একটি `float` হতে হবে।
    * যাচাই করবে যে ঐচ্ছিক অ্যাট্রিবিউট `is_offer` থাকলে সেটি একটি `bool`।
    * এসবই অনেক স্তরে সাজানো JSON অবজেক্টেও কাজ করবে।
* স্বয়ংক্রিয়ভাবে JSON থেকে ও JSON-এ রূপান্তর করবে।
* সবকিছু OpenAPI দিয়ে ডকুমেন্ট করবে, যা ব্যবহার করা যায়:
    * ইন্টারঅ্যাকটিভ ডকুমেন্টেশন সিস্টেমে।
    * অনেক প্রোগ্রামিং ভাষার জন্য স্বয়ংক্রিয়ভাবে ক্লায়েন্ট কোড তৈরির সিস্টেমে।
* সরাসরি দুটি ইন্টারঅ্যাকটিভ ডকুমেন্টেশন ওয়েব ইন্টারফেস দেবে।

---

আমরা কেবল উপরিভাগটুকু ছুঁয়ে দেখলাম, কিন্তু পুরো ব্যাপারটা কীভাবে কাজ করে তার ধারণা আপনি ইতিমধ্যে পেয়ে গেছেন।

এই লাইনটি বদলে দেখুন:

```Python
    return {"item_name": item.name, "item_id": item_id}
```

...এটি থেকে:

```Python
        ... "item_name": item.name ...
```

...এটিতে:

```Python
        ... "item_price": item.price ...
```

...আর দেখুন আপনার এডিটর কীভাবে অ্যাট্রিবিউটগুলো অটো-কমপ্লিট করে এবং সেগুলোর টাইপ জানে:

![editor support](https://fastapi.tiangolo.com/img/vscode-completion.png)

আরও ফিচারসহ পূর্ণাঙ্গ উদাহরণের জন্য <a href="https://fastapi.tiangolo.com/tutorial/">টিউটোরিয়াল - ইউজার গাইড</a> দেখুন। সেখানে ধাপে ধাপে, একদম শুরু থেকে সবকিছু শেখানো হয়েছে।

**আগাম জানিয়ে রাখি**: টিউটোরিয়াল - ইউজার গাইডে আছে:

* অন্যান্য বিভিন্ন জায়গা থেকে **প্যারামিটার** ঘোষণা, যেমন: **হেডার**, **কুকি**, **ফর্ম ফিল্ড** ও **ফাইল**।
* `maximum_length` বা `regex`-এর মতো **ভ্যালিডেশনের শর্ত** কীভাবে সেট করবেন।
* খুবই শক্তিশালী ও ব্যবহারে সহজ একটি **<dfn title="কম্পোনেন্ট, রিসোর্স, প্রোভাইডার, সার্ভিস বা ইনজেক্টেবল নামেও পরিচিত">ডিপেন্ডেন্সি ইনজেকশন</dfn>** সিস্টেম। সহজ কথায়, একই কোড (যেমন লগইন যাচাই বা ডেটাবেস সংযোগ) অনেক জায়গায় পুনরায় ব্যবহারের একটি সুন্দর ব্যবস্থা।
* সিকিউরিটি ও অথেনটিকেশন (ব্যবহারকারী কে তা যাচাই), **JWT টোকেন**-সহ **OAuth2** এবং **HTTP Basic** auth-এর সাপোর্ট।
* **অনেক স্তরে সাজানো JSON মডেল** ঘোষণার আরও উন্নত (কিন্তু সমান সহজ) কৌশল (Pydantic-এর কল্যাণে)।
* [Strawberry](https://strawberry.rocks) ও অন্যান্য লাইব্রেরির সাথে **GraphQL** ইন্টিগ্রেশন।
* অনেক অতিরিক্ত ফিচার (Starlette-এর কল্যাণে), যেমন:
    * **WebSockets** (সার্ভার ও ব্রাউজারের মধ্যে সারাক্ষণ খোলা থাকা দুই-মুখী সংযোগ)
    * HTTPX ও `pytest`-ভিত্তিক খুব সহজ টেস্ট
    * **CORS** (অন্য ডোমেইনের ওয়েবসাইট থেকে আপনার API ব্যবহারের অনুমতি)
    * **কুকি সেশন**
    * ...এবং আরও অনেক কিছু।

### আপনার অ্যাপ ডিপ্লয় করুন (ঐচ্ছিক) { #deploy-your-app-optional }

**ডিপ্লয়** মানে আপনার অ্যাপকে নিজের কম্পিউটার থেকে ইন্টারনেটের একটি সার্ভারে তুলে দেওয়া, যাতে অন্যরাও ব্যবহার করতে পারে। চাইলে একটিমাত্র কমান্ড দিয়ে আপনার FastAPI অ্যাপ [FastAPI Cloud](https://fastapicloud.com)-এ ডিপ্লয় করতে পারেন। 🚀

<div class="termy">

⟦CODE6⟧

</div>

CLI স্বয়ংক্রিয়ভাবে আপনার FastAPI অ্যাপ্লিকেশন খুঁজে বের করে ক্লাউডে ডিপ্লয় করবে। আপনি লগইন করা না থাকলে অথেনটিকেশন সম্পূর্ণ করতে আপনার ব্রাউজার খুলে যাবে।

ব্যাস! এখন আপনি ওই URL-এ আপনার অ্যাপ ব্যবহার করতে পারবেন। ✨

#### FastAPI Cloud সম্পর্কে { #about-fastapi-cloud }

**[FastAPI Cloud](https://fastapicloud.com)** তৈরি করেছেন **FastAPI**-এর একই লেখক ও টিম।

এটি খুব অল্প পরিশ্রমে একটি API **বানানো**, **ডিপ্লয় করা** এবং **ব্যবহার করার** পুরো প্রক্রিয়াটি সহজ করে দেয়।

FastAPI দিয়ে অ্যাপ বানানোর সেই একই সহজ **অভিজ্ঞতা** এটি ক্লাউডে **ডিপ্লয়** করার ক্ষেত্রেও নিয়ে আসে। 🎉

FastAPI Cloud হলো *FastAPI and friends* ওপেন সোর্স প্রজেক্টগুলোর প্রধান স্পন্সর ও অর্থায়নকারী। ✨

#### অন্য ক্লাউড প্রোভাইডারে ডিপ্লয় করুন { #deploy-to-other-cloud-providers }

FastAPI ওপেন সোর্স এবং স্ট্যান্ডার্ডের ওপর তৈরি। তাই আপনি নিজের পছন্দের যেকোনো ক্লাউড প্রোভাইডারে FastAPI অ্যাপ ডিপ্লয় করতে পারেন।

আপনার ক্লাউড প্রোভাইডারের গাইড অনুসরণ করে সেখানে FastAPI অ্যাপ ডিপ্লয় করুন। 🤓

## পারফরম্যান্স { #performance }

স্বাধীন সংস্থা TechEmpower-এর বেঞ্চমার্ক (গতি মাপার পরীক্ষা) দেখায় যে Uvicorn-এর অধীনে চলা **FastAPI** অ্যাপ্লিকেশন [Python-এর সবচেয়ে দ্রুত ফ্রেমওয়ার্কগুলোর একটি](https://www.techempower.com/benchmarks/#section=test&runid=7464e520-0dc2-473d-bd34-dbdfd7e85911&hw=ph&test=query&l=zijzen-7)। এর ওপরে আছে কেবল Starlette ও Uvicorn নিজেরা, যেগুলো FastAPI ভেতরে ব্যবহার করে। (*)

এ বিষয়ে আরও বুঝতে [বেঞ্চমার্ক](https://fastapi.tiangolo.com/benchmarks/) অংশটি দেখুন।

## ডিপেন্ডেন্সি { #dependencies }

এখানে "ডিপেন্ডেন্সি" মানে অন্য যেসব Python প্যাকেজের ওপর FastAPI নির্ভর করে, অর্থাৎ FastAPI চলতে যেগুলো লাগে।

FastAPI নির্ভর করে Pydantic ও Starlette-এর ওপর।

### `standard` ডিপেন্ডেন্সি { #standard-dependencies }

আপনি যখন `uv add "fastapi[standard]"` দিয়ে FastAPI ইনস্টল করেন, তখন এর সাথে ঐচ্ছিক ডিপেন্ডেন্সির `standard` গ্রুপটি আসে:

Pydantic যেটি ব্যবহার করে:

* [`email-validator`](https://github.com/JoshData/python-email-validator) - ইমেইল ঠিকানা সঠিক কিনা যাচাইয়ের জন্য।

Starlette যেগুলো ব্যবহার করে:

* [`httpx`](https://www.python-httpx.org) - আপনি যদি `TestClient` (API পরীক্ষা করার টুল) ব্যবহার করতে চান, তাহলে লাগবে।
* [`jinja2`](https://jinja.palletsprojects.com) - ডিফল্ট টেমপ্লেট কনফিগারেশন (HTML পেজ বানানো) ব্যবহার করতে চাইলে লাগবে।
* [`python-multipart`](https://github.com/Kludex/python-multipart) - `request.form()` দিয়ে ফর্ম <dfn title="HTTP রিকোয়েস্ট থেকে আসা স্ট্রিংকে Python ডেটায় রূপান্তর করা">"পার্সিং"</dfn> সাপোর্ট করতে চাইলে লাগবে।

FastAPI যেগুলো ব্যবহার করে:

* [`uvicorn`](https://uvicorn.dev) - যে সার্ভার আপনার অ্যাপ্লিকেশন লোড করে চালায়। এর সাথে আছে `uvicorn[standard]`, যাতে উচ্চ গতিতে চালানোর জন্য দরকারি কিছু ডিপেন্ডেন্সি (যেমন `uvloop`) থাকে।
* `fastapi-cli[standard]` - `fastapi` কমান্ডটি দেওয়ার জন্য।
    * এর মধ্যে আছে `fastapi-cloud-cli`, যা দিয়ে আপনি আপনার FastAPI অ্যাপ্লিকেশন [FastAPI Cloud](https://fastapicloud.com)-এ ডিপ্লয় করতে পারেন।

### `standard` ডিপেন্ডেন্সি ছাড়া { #without-standard-dependencies }

আপনি যদি ঐচ্ছিক `standard` ডিপেন্ডেন্সিগুলো না চান, তাহলে `uv add "fastapi[standard]"`-এর বদলে `uv add fastapi` দিয়ে ইনস্টল করতে পারেন। তখন সার্ভার (যেমন Uvicorn) আপনাকে আলাদাভাবে ইনস্টল করতে হবে।

### `fastapi-cloud-cli` ছাড়া { #without-fastapi-cloud-cli }

আপনি যদি স্ট্যান্ডার্ড ডিপেন্ডেন্সিসহ কিন্তু `fastapi-cloud-cli` ছাড়া FastAPI ইনস্টল করতে চান, তাহলে `uv add "fastapi[standard-no-fastapi-cloud-cli]"` দিয়ে ইনস্টল করতে পারেন।

### অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি { #additional-optional-dependencies }

আরও কিছু ডিপেন্ডেন্সি আছে যা আপনি দরকার হলে ইনস্টল করতে পারেন।

Pydantic-এর অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি:

* [`pydantic-settings`](https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/) - সেটিংস (যেমন পাসওয়ার্ড, ডেটাবেস URL) সামলানোর জন্য।
* [`pydantic-extra-types`](https://github.com/pydantic/pydantic-extra-types) - Pydantic-এর সাথে ব্যবহারের জন্য অতিরিক্ত টাইপ (যেমন ফোন নম্বর, রঙ)।

FastAPI-এর অতিরিক্ত ঐচ্ছিক ডিপেন্ডেন্সি:

* [`orjson`](https://github.com/ijl/orjson) - `ORJSONResponse` ব্যবহার করতে চাইলে লাগবে।
* [`ujson`](https://github.com/ultrajson/ultrajson) - `UJSONResponse` ব্যবহার করতে চাইলে লাগবে।

/// check | সংক্ষেপে মনে রাখুন

* FastAPI দিয়ে Python-এ খুব দ্রুত ও সহজে API বানানো যায়।
* ইনস্টল করুন `uv add "fastapi[standard]"` দিয়ে, আর চালান `uv run fastapi dev` দিয়ে।
* টাইপ হিন্ট (`item_id: int`) একবার লিখলেই FastAPI নিজে ডেটা যাচাই, রূপান্তর আর ডকুমেন্টেশন তৈরি করে।
* `/docs` ঠিকানায় গিয়ে ব্রাউজার থেকেই API পরীক্ষা করা যায়।
* এরপর ধাপে ধাপে শিখতে [শিখুন](learn/index.md) অংশ থেকে শুরু করুন। অপরিচিত শব্দের মানে জানতে [সহজ শব্দকোষ](learn/glossary.md) দেখুন।

///

## লাইসেন্স { #license }

এই প্রজেক্টটি MIT লাইসেন্সের শর্তাবলির অধীনে লাইসেন্সপ্রাপ্ত। MIT লাইসেন্স মানে আপনি এটি বিনামূল্যে ব্যবহার, পরিবর্তন ও বাণিজ্যিক কাজে লাগাতে পারেন।
