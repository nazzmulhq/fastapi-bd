# WSGI যুক্ত করা - Flask, Django, অন্যান্য { #including-wsgi-flask-django-others }

/// note | এই পেজে যা শিখবেন

* WSGI আর ASGI কী, সহজ ভাষায়।
* একটি পুরনো Flask বা Django অ্যাপকে FastAPI-এর ভেতরে mount করা।
* কেন `a2wsgi` প্যাকেজ ব্যবহার করতে হয়।

///

[সাব অ্যাপ্লিকেশন - Mount](sub-applications.md), [প্রক্সির পেছনে](behind-a-proxy.md)-এ যেমন দেখেছেন, আপনি WSGI অ্যাপ্লিকেশন mount করতে পারেন।

এর জন্য `WSGIMiddleware` ব্যবহার করে আপনার WSGI অ্যাপ্লিকেশনকে (যেমন Flask, Django ইত্যাদি) মুড়ে দিতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

**WSGI** হলো Python ওয়েব অ্যাপ আর সার্ভারের মধ্যে কথা বলার পুরনো নিয়ম (Flask, Django এটি ব্যবহার করে)। **ASGI** হলো নতুন নিয়ম, যা `async` সাপোর্ট করে (FastAPI এটি ব্যবহার করে)। দুটো আলাদা প্লাগের মতো। `WSGIMiddleware` হলো একটি অ্যাডাপ্টার (কনভার্টার প্লাগ), যা দিয়ে পুরনো প্লাগ নতুন সকেটে লাগানো যায়। ফলে পুরনো Flask অ্যাপ পুরোটা নতুন করে না লিখেই ধীরে ধীরে FastAPI-তে সরাতে পারেন।

///

## `WSGIMiddleware` ব্যবহার করা { #using-wsgimiddleware }

/// note | নোট

এর জন্য আপনার প্রজেক্টে `a2wsgi` যোগ করতে হবে, যেমন `uv add a2wsgi` দিয়ে।

///

`a2wsgi` থেকে `WSGIMiddleware` ইমপোর্ট করতে হবে।

তারপর WSGI (যেমন Flask) অ্যাপটিকে middleware দিয়ে মুড়ে দিন।

আর তারপর এটিকে একটি পাথের নিচে mount করুন।

{* ../../docs_src/wsgi/tutorial001_py310.py hl[1,3,23] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ১: `a2wsgi` থেকে `WSGIMiddleware` ইমপোর্ট।
* লাইন ৩, ৬–১২: একটি সাধারণ Flask অ্যাপ, যার `/` রাউট "Hello, World from Flask!" ফেরত দেয়। `escape` ব্যবহার করা হয়েছে যাতে ইউজারের দেওয়া নাম নিরাপদে দেখানো যায়।
* লাইন ১৫–২০: FastAPI অ্যাপ, যার `/v2` রাউট আছে।
* লাইন ২৩: `app.mount("/v1", WSGIMiddleware(flask_app))` মানে "`/v1` দিয়ে শুরু হওয়া সব রিকোয়েস্ট Flask অ্যাপের কাছে পাঠাও।"

///

/// note | নোট

আগে `fastapi.middleware.wsgi` থেকে `WSGIMiddleware` ব্যবহার করার পরামর্শ দেওয়া হতো, কিন্তু এখন সেটি পুরনো (deprecated)।

এর বদলে `a2wsgi` প্যাকেজ ব্যবহার করার পরামর্শ দেওয়া হয়। ব্যবহারের পদ্ধতি একই থাকে।

শুধু নিশ্চিত করুন যে `a2wsgi` প্যাকেজ ইনস্টল করা আছে আর `WSGIMiddleware` সঠিকভাবে `a2wsgi` থেকে ইমপোর্ট করছেন।

///

## যাচাই করুন { #check-it }

এখন `/v1/` পাথের নিচের প্রতিটি রিকোয়েস্ট Flask অ্যাপ্লিকেশন সামলাবে।

আর বাকিগুলো সামলাবে **FastAPI**।

এটি চালিয়ে [http://localhost:8000/v1/](http://localhost:8000/v1/)-এ গেলে Flask-এর রেসপন্স দেখবেন:

```txt
Hello, World from Flask!
```

আর [http://localhost:8000/v2](http://localhost:8000/v2)-এ গেলে FastAPI-এর রেসপন্স দেখবেন:

```JSON
{
    "message": "Hello World"
}
```

/// check | সংক্ষেপে মনে রাখুন

* পুরনো WSGI অ্যাপ (Flask, Django) FastAPI-এর সাথে একসাথে চালানো যায়।
* `uv add a2wsgi` করে `from a2wsgi import WSGIMiddleware` ব্যবহার করুন।
* `app.mount("/পাথ", WSGIMiddleware(পুরনো_অ্যাপ))` দিয়ে একটি পাথ পুরনো অ্যাপকে দিয়ে দিন।

///
