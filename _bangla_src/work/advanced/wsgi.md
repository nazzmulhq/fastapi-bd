# WSGI যুক্ত করা - Flask, Django ও অন্যান্য { #including-wsgi-flask-django-others }

[সাব-অ্যাপ্লিকেশন - মাউন্ট](sub-applications.md), [প্রক্সির পেছনে](behind-a-proxy.md)-এ যেমন দেখেছেন, সেভাবে আপনি WSGI অ্যাপ্লিকেশন মাউন্ট করতে পারেন।

এর জন্য আপনি `WSGIMiddleware` ব্যবহার করে আপনার WSGI অ্যাপ্লিকেশন, যেমন Flask, Django ইত্যাদি, মুড়িয়ে নিতে পারেন।

## `WSGIMiddleware` ব্যবহার { #using-wsgimiddleware }

/// note | নোট

এর জন্য আপনার প্রজেক্টে `a2wsgi` যোগ করতে হবে, যেমন `uv add a2wsgi` দিয়ে।

///

আপনাকে `a2wsgi` থেকে `WSGIMiddleware` ইম্পোর্ট করতে হবে।

তারপর মিডলওয়্যার দিয়ে WSGI (যেমন Flask) অ্যাপটি মুড়িয়ে নিন।

আর তারপর সেটি একটি পাথের অধীনে মাউন্ট করুন।

{* ../../docs_src/wsgi/tutorial001_py310.py hl[1,3,23] *}

/// note | নোট

আগে `fastapi.middleware.wsgi` থেকে `WSGIMiddleware` ব্যবহারের পরামর্শ দেওয়া হতো, কিন্তু এটি এখন ডেপ্রিকেটেড।

এর বদলে `a2wsgi` প্যাকেজ ব্যবহারের পরামর্শ দেওয়া হয়। ব্যবহারের পদ্ধতি একই থাকে।

শুধু নিশ্চিত করুন যে আপনার `a2wsgi` প্যাকেজ ইনস্টল করা আছে এবং `a2wsgi` থেকে সঠিকভাবে `WSGIMiddleware` ইম্পোর্ট করছেন।

///

## যাচাই করুন { #check-it }

এখন `/v1/` পাথের অধীনে প্রতিটি রিকোয়েস্ট Flask অ্যাপ্লিকেশন সামলাবে।

আর বাকিগুলো সামলাবে **FastAPI**।

আপনি যদি এটি চালিয়ে [http://localhost:8000/v1/](http://localhost:8000/v1/)-এ যান, তাহলে Flask থেকে রেসপন্স দেখবেন:

⟦CODE1⟧

আর আপনি যদি [http://localhost:8000/v2](http://localhost:8000/v2)-এ যান, তাহলে FastAPI থেকে রেসপন্স দেখবেন:

⟦CODE2⟧
