# নিজে সার্ভার চালানো { #run-a-server-manually }

/// note | এই পেজে যা শিখবেন

* `fastapi run` দিয়ে প্রোডাকশনে অ্যাপ চালানো।
* ASGI সার্ভার কী, আর Uvicorn, Hypercorn এর মতো বিকল্পগুলো।
* "সার্ভার" শব্দের দুটি অর্থ: মেশিন আর প্রোগ্রাম।
* `uvicorn main:app` কমান্ড কীভাবে পড়তে হয়।

///

## `fastapi run` কমান্ড ব্যবহার করুন { #use-the-fastapi-run-command }

সংক্ষেপে, আপনার FastAPI অ্যাপ্লিকেশন চালাতে (serve করতে) `fastapi run` ব্যবহার করুন:

<div class="termy">

```console
$ <font color="#4E9A06">fastapi</font> run <u style="text-decoration-style:solid">main.py</u>

  <span style="background-color:#009485"><font color="#D3D7CF"> FastAPI </font></span>  Starting production server 🚀

             Searching for package file structure from directories
             with <font color="#3465A4">__init__.py</font> files
             Importing from <font color="#75507B">/home/user/code/</font><font color="#AD7FA8">awesomeapp</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> module </font></span>  🐍 main.py

     <span style="background-color:#007166"><font color="#D3D7CF"> code </font></span>  Importing the FastAPI app object from the module with
             the following code:

             <u style="text-decoration-style:solid">from </u><u style="text-decoration-style:solid"><b>main</b></u><u style="text-decoration-style:solid"> import </u><u style="text-decoration-style:solid"><b>app</b></u>

      <span style="background-color:#007166"><font color="#D3D7CF"> app </font></span>  Using import string: <font color="#3465A4">main:app</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Server started at <font color="#729FCF"><u style="text-decoration-style:solid">http://0.0.0.0:8000</u></font>
   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Documentation at <font color="#729FCF"><u style="text-decoration-style:solid">http://0.0.0.0:8000/docs</u></font>

             Logs:

     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Started server process <b>[</b><font color="#34E2E2"><b>2306215</b></font><b>]</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Waiting for application startup.
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Application startup complete.
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Uvicorn running on <font color="#729FCF"><u style="text-decoration-style:solid">http://0.0.0.0:8000</u></font> <b>(</b>Press CTRL+C
             to quit<b>)</b>
```

</div>

বেশিরভাগ ক্ষেত্রে এটাই যথেষ্ট। 😎

যেমন একটি কন্টেইনারে, একটি সার্ভারে ইত্যাদি জায়গায় আপনার **FastAPI** অ্যাপ চালু করতে এই কমান্ড ব্যবহার করতে পারেন।

## ASGI সার্ভার { #asgi-servers }

চলুন বিস্তারিতে একটু গভীরে যাই।

FastAPI Python ওয়েব ফ্রেমওয়ার্ক আর সার্ভার তৈরির একটি স্ট্যান্ডার্ড ব্যবহার করে, যার নাম <abbr title="Asynchronous Server Gateway Interface">ASGI</abbr>। FastAPI হলো একটি ASGI ওয়েব ফ্রেমওয়ার্ক।

একটি দূরের সার্ভার মেশিনে একটি **FastAPI** অ্যাপ্লিকেশন (বা অন্য যেকোনো ASGI অ্যাপ্লিকেশন) চালাতে আপনার প্রধানত যা দরকার তা হলো **Uvicorn**-এর মতো একটি ASGI সার্ভার প্রোগ্রাম, `fastapi` কমান্ডে এটিই ডিফল্টভাবে আসে।

/// tip | উদাহরণ দিয়ে বুঝি

আপনার FastAPI অ্যাপ হলো রাঁধুনি, যে জানে কোন অর্ডারে কী রান্না করতে হবে। কিন্তু রাঁধুনি নিজে দরজায় দাঁড়িয়ে গ্রাহকের অর্ডার নেয় না। ASGI সার্ভার (যেমন Uvicorn) হলো ওয়েটার: নেটওয়ার্ক থেকে রিকোয়েস্ট (অর্ডার) নেয়, রাঁধুনিকে দেয়, রান্না হলে রেসপন্স (খাবার) গ্রাহকের কাছে পৌঁছে দেয়। ASGI হলো ওয়েটার আর রাঁধুনির মধ্যে কথা বলার নিয়ম।

///

কয়েকটি বিকল্প আছে, যেমন:

* [Uvicorn](https://uvicorn.dev): একটি উচ্চ-পারফরম্যান্স ASGI সার্ভার।
* [Hypercorn](https://hypercorn.readthedocs.io/): একটি ASGI সার্ভার, যা অন্যান্য ফিচারের পাশাপাশি HTTP/2 আর Trio সাপোর্ট করে।
* [Daphne](https://github.com/django/daphne): Django Channels-এর জন্য তৈরি ASGI সার্ভার।
* [Granian](https://github.com/emmett-framework/granian): Python অ্যাপ্লিকেশনের জন্য Rust-এ লেখা একটি HTTP সার্ভার।

## সার্ভার মেশিন এবং সার্ভার প্রোগ্রাম { #server-machine-and-server-program }

নাম নিয়ে একটি ছোট বিষয় মাথায় রাখা দরকার। 💡

"**সার্ভার**" শব্দটি সাধারণত দুটো জিনিসই বোঝাতে ব্যবহার হয়: দূরের/ক্লাউড কম্পিউটার (আসল বা ভার্চুয়াল মেশিন), আর সেই মেশিনে চলা প্রোগ্রাম (যেমন Uvicorn)।

শুধু মনে রাখবেন, সাধারণভাবে "সার্ভার" পড়লে এটি এই দুটোর যেকোনো একটিকে বোঝাতে পারে।

দূরের মেশিনকে বোঝাতে সাধারণত একে **সার্ভার** বলা হয়, তবে **মেশিন**, **VM** (ভার্চুয়াল মেশিন), **নোড**-ও বলা হয়। এগুলো সবই কোনো ধরনের দূরের মেশিন বোঝায়, যেটিতে সাধারণত Linux চলে আর যেখানে আপনি প্রোগ্রাম চালান।

## সার্ভার প্রোগ্রাম ইনস্টল করুন { #install-the-server-program }

FastAPI ইনস্টল করলে এর সাথে একটি প্রোডাকশন সার্ভার, Uvicorn, আসে, আর আপনি `fastapi run` কমান্ড দিয়ে এটি চালু করতে পারেন।

তবে আপনি নিজেও একটি ASGI সার্ভার ইনস্টল করতে পারেন।

আপনার প্রজেক্টে সার্ভার অ্যাপ্লিকেশনটি যোগ করুন।

যেমন, Uvicorn ইনস্টল করতে:

<div class="termy">

```console
$ uv add "uvicorn[standard]"

---> 100%
```

</div>

অন্য যেকোনো ASGI সার্ভার প্রোগ্রামের ক্ষেত্রেও একই রকম প্রক্রিয়া প্রযোজ্য।

/// tip | পরামর্শ

`standard` যোগ করলে Uvicorn কিছু প্রস্তাবিত বাড়তি ডিপেন্ডেন্সি ইনস্টল করে ব্যবহার করবে।

এর মধ্যে আছে `uvloop`, `asyncio`-এর একটি উচ্চ-পারফরম্যান্স বিকল্প, যা concurrency-তে বড় পারফরম্যান্স বৃদ্ধি দেয়।

যখন `uv add "fastapi[standard]"` এর মতো কিছু দিয়ে FastAPI যোগ করেন, তখন আপনি ইতিমধ্যে `uvicorn[standard]`-ও পেয়ে যান।

///

## সার্ভার প্রোগ্রাম চালান { #run-the-server-program }

যদি নিজে একটি ASGI সার্ভার ইনস্টল করে থাকেন, তাহলে সাধারণত আপনার FastAPI অ্যাপ্লিকেশন ইমপোর্ট করার জন্য একটি বিশেষ ফরম্যাটে ইমপোর্ট স্ট্রিং দিতে হবে:

<div class="termy">

```console
$ uv run uvicorn main:app --host 0.0.0.0 --port 80

<span style="color: green;">INFO</span>:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)
```

</div>

/// note | নোট

`uvicorn main:app` কমান্ড বোঝায়:

* `main`: `main.py` ফাইল (Python "মডিউল")।
* `app`: `main.py`-এর ভেতরে `app = FastAPI()` লাইন দিয়ে তৈরি করা অবজেক্ট।

এটি এর সমতুল্য:

```Python
from main import app
```

///

প্রতিটি বিকল্প ASGI সার্ভার প্রোগ্রামের একই রকম কমান্ড থাকবে, তাদের নিজ নিজ ডকুমেন্টেশনে আরও পড়তে পারেন।

/// warning | সতর্কতা

Uvicorn আর অন্যান্য সার্ভার একটি `--reload` অপশন সাপোর্ট করে, যা ডেভেলপমেন্টের সময় কাজে লাগে।

`--reload` অপশন অনেক বেশি রিসোর্স খরচ করে, কম স্থিতিশীল, ইত্যাদি।

এটি **ডেভেলপমেন্টে** অনেক সাহায্য করে, কিন্তু **প্রোডাকশনে** এটি ব্যবহার করা **উচিত নয়**।

///

## ডিপ্লয়মেন্টের ধারণা { #deployment-concepts }

এই উদাহরণগুলো সার্ভার প্রোগ্রাম (যেমন Uvicorn) চালায়, **একটি মাত্র প্রসেস** শুরু করে, সব IP-তে (`0.0.0.0`) একটি পূর্বনির্ধারিত পোর্টে (যেমন `80`) শুনতে থাকে।

এটাই মৌলিক ধারণা। কিন্তু আপনি সম্ভবত আরও কিছু বিষয় সামলাতে চাইবেন, যেমন:

* নিরাপত্তা - HTTPS
* কম্পিউটার চালু হলে নিজে থেকে চালু হওয়া
* বন্ধ হয়ে গেলে আবার চালু হওয়া (রিস্টার্ট)
* রেপ্লিকেশন (কতগুলো প্রসেস চলছে)
* মেমোরি
* চালু করার আগের ধাপগুলো

পরের অধ্যায়গুলোতে আমি এই প্রতিটি ধারণা সম্পর্কে, এগুলো নিয়ে কীভাবে ভাবতে হয়, আর এগুলো সামলানোর কৌশলসহ কিছু বাস্তব উদাহরণ নিয়ে আরও বলব। 🚀

/// check | সংক্ষেপে মনে রাখুন

* প্রোডাকশনে সবচেয়ে সহজ: `fastapi run` (ভেতরে Uvicorn চলে)।
* নিজে Uvicorn চালালে `uvicorn main:app --host 0.0.0.0 --port 80` এর মতো কমান্ড লাগে (`main` = ফাইল, `app` = অবজেক্ট)।
* প্রোডাকশনে কখনো `--reload` ব্যবহার করবেন না।
* শুধু সার্ভার চালানোই যথেষ্ট নয়, HTTPS, রিস্টার্ট, রেপ্লিকেশন ইত্যাদিও ভাবতে হয় (পরের পেজ)।

///
