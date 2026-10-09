# টেমপ্লেট { #templates }

/// note | এই পেজে যা শিখবেন

* Jinja2 টেমপ্লেট দিয়ে সার্ভার থেকে HTML পেজ তৈরি করে পাঠানো।
* টেমপ্লেটে ডেটা পাঠানো আর `url_for()` দিয়ে লিংক বানানো।
* টেমপ্লেটের সাথে CSS এর মতো স্ট্যাটিক ফাইল ব্যবহার।

///

**FastAPI**-এর সাথে আপনার পছন্দের যেকোনো টেমপ্লেট ইঞ্জিন ব্যবহার করতে পারেন।

**টেমপ্লেট** হলো একটি HTML ফাইল, যাতে কিছু ফাঁকা জায়গা থাকে। সার্ভার সেই জায়গাগুলোতে আসল ডেটা বসিয়ে সম্পূর্ণ পেজ বানিয়ে ব্রাউজারে পাঠায়। অনেকটা একটি চিঠির ছাপানো ফর্মের মতো, যেখানে শুধু নাম আর তারিখের ঘর পূরণ করা হয়।

একটি প্রচলিত পছন্দ হলো Jinja2, Flask আর অন্যান্য টুলও এটিই ব্যবহার করে।

এটি সহজে কনফিগার করার জন্য কিছু টুল আছে, যা আপনি সরাসরি আপনার **FastAPI** অ্যাপ্লিকেশনে ব্যবহার করতে পারেন (Starlette সরবরাহ করে)।

## ডিপেন্ডেন্সি ইনস্টল করুন { #install-dependencies }

আপনার প্রজেক্টে `jinja2` যোগ করুন:

<div class="termy">

⟦CODE1⟧

</div>

## `Jinja2Templates` ব্যবহার { #using-jinja2templates }

* `Jinja2Templates` ইমপোর্ট করুন।
* একটি `templates` অবজেক্ট তৈরি করুন, যা পরে পুনরায় ব্যবহার করতে পারবেন।
* যে *পাথ অপারেশন* একটি টেমপ্লেট ফেরত দেবে, তাতে একটি `Request` প্যারামিটার ঘোষণা করুন।
* আপনার তৈরি `templates` ব্যবহার করে একটি `TemplateResponse` রেন্ডার করে ফেরত দিন। এতে দিন টেমপ্লেটের নাম, রিকোয়েস্ট অবজেক্ট, আর Jinja2 টেমপ্লেটের ভেতরে ব্যবহারের জন্য কী-মান জোড়াসহ একটি "context" ডিকশনারি।

{* ../../docs_src/templates/tutorial001_py310.py hl[4,11,15:18] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৮: `static` ফোল্ডার mount করা, CSS ইত্যাদির জন্য।
* লাইন ১১: `templates` ফোল্ডার থেকে টেমপ্লেট পড়ার ব্যবস্থা।
* লাইন ১৪: `response_class=HTMLResponse`, তাই ডকুমেন্টেশন জানবে এটি HTML ফেরত দেয়।
* লাইন ১৬-১৮: `item.html` টেমপ্লেট রেন্ডার করা, আর `context={"id": id}` দিয়ে টেমপ্লেটে `id` পাঠানো।

///

/// note | নোট

FastAPI 0.108.0, Starlette 0.29.0-এর আগে `name` ছিল প্রথম প্যারামিটার।

এছাড়া তার আগের সংস্করণগুলোতে `request` অবজেক্টটি Jinja2-এর context-এর কী-মান জোড়ার অংশ হিসেবে পাঠানো হতো।

///

/// tip | পরামর্শ

`response_class=HTMLResponse` ঘোষণা করলে ডকুমেন্টেশন UI জানতে পারবে যে রেসপন্সটি HTML হবে।

///

/// note | কারিগরি বিবরণ

`from starlette.templating import Jinja2Templates`-ও ব্যবহার করতে পারতেন।

**FastAPI** ডেভেলপার হিসেবে আপনার সুবিধার জন্যই একই `starlette.templating`-কে `fastapi.templating` হিসেবে দেয়। কিন্তু উপলব্ধ বেশিরভাগ রেসপন্স সরাসরি Starlette থেকে আসে। `Request` আর `StaticFiles`-এর ক্ষেত্রেও একই কথা।

///

## টেমপ্লেট লেখা { #writing-templates }

তারপর আপনি `templates/item.html`-এ একটি টেমপ্লেট লিখতে পারেন, যেমন:

```jinja hl_lines="7"
{!../../docs_src/templates/templates/item.html!}
```

### টেমপ্লেটের context-এর মান { #template-context-values }

HTML-এর যে অংশে আছে:

{% raw %}

```jinja
Item ID: {{ id }}
```

{% endraw %}

...সেটি আপনার দেওয়া "context" `dict` থেকে নেওয়া `id` দেখাবে:

```Python
{"id": id}
```

যেমন, `42` ID-সহ এটি রেন্ডার করবে:

```html
Item ID: 42
```

অর্থাৎ টেমপ্লেটের জোড়া দ্বিতীয় বন্ধনীর ভেতরের নামটি context ডিকশনারির একই নামের মান দিয়ে বদলে যায়।

### টেমপ্লেটে `url_for`-এর আর্গুমেন্ট { #template-url-for-arguments }

টেমপ্লেটের ভেতরে `url_for()`-ও ব্যবহার করতে পারেন। এটি আর্গুমেন্ট হিসেবে সেই একই আর্গুমেন্টগুলো নেয়, যা আপনার *পাথ অপারেশন ফাংশন* ব্যবহার করত।

তাই এই অংশটি:

{% raw %}

```jinja
<a href="{{ url_for('read_item', id=id) }}">
```

{% endraw %}

...সেই একই URL-এর একটি লিংক তৈরি করবে, যা *পাথ অপারেশন ফাংশন* `read_item(id=id)` সামলাত।

যেমন, `42` ID-সহ এটি রেন্ডার করবে:

```html
<a href="/items/42">
```

`url_for()`-এর সুবিধা হলো, পরে পাথ বদলালেও (যেমন `/items/` থেকে `/products/`) টেমপ্লেটের লিংকগুলো নিজে থেকেই ঠিক থাকবে, কারণ লিংক বানানো হচ্ছে ফাংশনের নাম দিয়ে, হাতে লেখা ঠিকানা দিয়ে নয়।

## টেমপ্লেট আর স্ট্যাটিক ফাইল { #templates-and-static-files }

টেমপ্লেটের ভেতরে `url_for()` ব্যবহার করে, যেমন, `name="static"` দিয়ে mount করা `StaticFiles`-এর সাথেও এটি ব্যবহার করতে পারেন।

```jinja hl_lines="4"
{!../../docs_src/templates/templates/item.html!}
```

এই উদাহরণে এটি `static/styles.css`-এর একটি CSS ফাইলের লিংক দেবে, যাতে আছে:

```CSS hl_lines="4"
{!../../docs_src/templates/static/styles.css!}
```

আর যেহেতু আপনি `StaticFiles` ব্যবহার করছেন, তাই ওই CSS ফাইলটি আপনার **FastAPI** অ্যাপ্লিকেশন `/static/styles.css` URL-এ স্বয়ংক্রিয়ভাবে সার্ভ করবে।

## আরও বিস্তারিত { #more-details }

টেমপ্লেট কীভাবে টেস্ট করতে হয় সহ আরও বিস্তারিত জানতে [টেমপ্লেট নিয়ে Starlette-এর ডকুমেন্টেশন](https://starlette.dev/templates/) দেখুন।

/// check | সংক্ষেপে মনে রাখুন

* `templates = Jinja2Templates(directory="templates")` বানান।
* পাথ অপারেশনে `request: Request` নিয়ে `return templates.TemplateResponse(request=request, name="item.html", context={...})`।
* `response_class=HTMLResponse` দিন, যাতে ডকুমেন্টেশন জানে এটি HTML।
* টেমপ্লেটে লিংক ও CSS-এর ঠিকানা বানাতে `url_for()` ব্যবহার করুন।

///
