# টিউটোরিয়াল - ইউজার গাইড { #tutorial-user-guide }

এই টিউটোরিয়ালে ধাপে ধাপে দেখানো হয়েছে কীভাবে **FastAPI**-এর বেশিরভাগ ফিচার ব্যবহার করবেন।

প্রতিটি অংশ আগের অংশগুলোর ওপর ধীরে ধীরে গড়ে উঠেছে। তবে বিষয়গুলো আলাদা আলাদা অংশে ভাগ করা, তাই আপনার নির্দিষ্ট কোনো প্রয়োজন থাকলে সরাসরি সেই অংশে চলে যেতে পারেন।

এটি এমনভাবে তৈরি যাতে পরে রেফারেন্স হিসেবেও কাজে লাগে। দরকার হলে ফিরে এসে ঠিক যা লাগবে তা দেখে নিতে পারবেন।

/// note | এই পেজে যা শিখবেন

* টিউটোরিয়ালের কোড কীভাবে নিজের কম্পিউটারে চালাবেন।
* `uv` দিয়ে কীভাবে একটি প্রজেক্ট তৈরি করে FastAPI ইনস্টল করবেন, আর প্রতিটি কমান্ড কী করে।
* AI কোডিং এজেন্টের জন্য FastAPI-এর অফিসিয়াল "স্কিল" কী।
* এই টিউটোরিয়াল আর অ্যাডভান্সড গাইডের মধ্যে পার্থক্য।

///

## কোড চালান { #run-the-code }

সব কোড ব্লক কপি করে সরাসরি ব্যবহার করা যায় (এগুলো আসলে টেস্ট করা Python ফাইল)।

যেকোনো উদাহরণ চালাতে কোডটি `main.py` নামের একটি ফাইলে কপি করুন, তারপর `uv run` দিয়ে `fastapi dev` চালু করুন:

<div class="termy">

```console
$ <font color="#4E9A06">uv run fastapi</font> dev

  <span style="background-color:#009485"><font color="#D3D7CF"> FastAPI </font></span>  Starting development server 🚀

             Searching for package file structure from directories
             with <font color="#3465A4">__init__.py</font> files
             Importing from <font color="#75507B">/home/user/code/</font><font color="#AD7FA8">awesomeapp</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> module </font></span>  🐍 main.py

     <span style="background-color:#007166"><font color="#D3D7CF"> code </font></span>  Importing the FastAPI app object from the module with
             the following code:

             <u style="text-decoration-style:solid">from </u><u style="text-decoration-style:solid"><b>main</b></u><u style="text-decoration-style:solid"> import </u><u style="text-decoration-style:solid"><b>app</b></u>

      <span style="background-color:#007166"><font color="#D3D7CF"> app </font></span>  Using import string: <font color="#3465A4">main:app</font>

   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Server started at <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000</u></font>
   <span style="background-color:#007166"><font color="#D3D7CF"> server </font></span>  Documentation at <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000/docs</u></font>

      <span style="background-color:#007166"><font color="#D3D7CF"> tip </font></span>  Running in development mode, for production use:
             <b>fastapi run</b>

             Logs:

     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Will watch for changes in these directories:
             <b>[</b><font color="#4E9A06">&apos;/home/user/code/awesomeapp&apos;</font><b>]</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Uvicorn running on <font color="#729FCF"><u style="text-decoration-style:solid">http://127.0.0.1:8000</u></font> <b>(</b>Press CTRL+C
             to quit<b>)</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Started reloader process <b>[</b><font color="#34E2E2"><b>383138</b></font><b>]</b> using WatchFiles
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Started server process <b>[</b><font color="#34E2E2"><b>383153</b></font><b>]</b>
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Waiting for application startup.
     <span style="background-color:#007166"><font color="#D3D7CF"> INFO </font></span>  Application startup complete.
```

</div>

/// info | আউটপুটটি সহজ ভাষায়

* `uv run fastapi dev`: প্রজেক্টের ভার্চুয়াল এনভায়রনমেন্ট থেকে `fastapi` কমান্ড চালিয়ে ডেভেলপমেন্ট সার্ভার চালু করে।
* বাক্সের ভেতরে লেখা থাকে সার্ভার কোথায় চলছে (`http://127.0.0.1:8000`) আর API ডকুমেন্টেশন কোথায় (`/docs`)।
* `Will watch for changes`: কোডে পরিবর্তন হলে সার্ভার নিজে নিজে রিলোড হবে।
* `Application startup complete.`: সার্ভার তৈরি, এখন ব্রাউজারে ঠিকানাটি খুলে দেখতে পারেন।
* থামাতে টার্মিনালে `CTRL+C` চাপুন।

///

আপনি নিজে কোড লিখুন বা কপি করুন, বদলে দেখুন আর নিজের কম্পিউটারে চালান, এটা **জোরালোভাবে উৎসাহিত** করা হচ্ছে।

এডিটরে ব্যবহার করলেই আসলে FastAPI-এর সুবিধাগুলো বোঝা যায়: কত কম কোড লিখতে হয়, সব টাইপ যাচাই, অটোকমপ্লিশন ইত্যাদি।

---

## FastAPI ইনস্টল করুন { #install-fastapi }

প্রথম ধাপ হলো আপনার প্রজেক্ট সেটআপ করে FastAPI যোগ করা।

[`uv`](https://docs.astral.sh/uv/getting-started/installation/) ইনস্টল করুন, তারপর একটি প্রজেক্ট তৈরি করে FastAPI যোগ করুন:

<div class="termy">

```console
$ uv init awesome-project --bare
$ cd awesome-project
$ uv add "fastapi[standard]"

---> 100%
```

</div>

`uv add` প্রজেক্টের ভার্চুয়াল এনভায়রনমেন্ট `.venv`-এ তৈরি করে, `pyproject.toml`-এ FastAPI যোগ করে, আর `uv.lock` তৈরি করে, যাতে পরে হুবহু একই প্যাকেজ সংস্করণগুলো আবার ইনস্টল করা যায়।

/// details | এই কমান্ডগুলো কী করে

* `uv init`: একটি নতুন Python প্রজেক্ট তৈরি করে।
* `awesome-project`: এই নামে নতুন একটি ফোল্ডারে প্রজেক্টটি তৈরি করে। আপনি নিজের পছন্দের নাম দিতে পারেন।
* `--bare`: শুধু ন্যূনতম `pyproject.toml` ফাইলটি তৈরি করে, নমুনা `main.py`, `README.md` বা অন্য কোনো ফাইল বানায় না। এই টিউটোরিয়ালের পরের ধাপগুলোতে অ্যাপ্লিকেশনের ফাইলগুলো আপনি নিজেই বানাবেন।

তারপর FastAPI যোগ করার আগে `cd awesome-project` দিয়ে নতুন প্রজেক্ট ফোল্ডারে ঢোকা হয়।

আপনার সিস্টেমে ইতিমধ্যে ইনস্টল করা একটি মানানসই Python সংস্করণ `uv` ব্যবহার করবে, না থাকলে দরকার হলে নিজেই ডাউনলোড করে নেবে।

`uv add` চালালে এটি FastAPI আর FastAPI যেসব প্যাকেজের ওপর নির্ভর করে সেগুলোর মানানসই সংস্করণ বেছে নেয়। হুবহু সংস্করণগুলো `uv.lock`-এ লিখে রাখে, যাতে পরে অন্য কম্পিউটারে বা অ্যাপ্লিকেশন ডিপ্লয় করার সময় একই সংস্করণগুলো ইনস্টল করা যায়।

এই ফাইলটি তৈরি বা হালনাগাদ করাকে বলে প্রজেক্টের ডিপেন্ডেন্সি [**লক করা**](https://docs.astral.sh/uv/concepts/projects/sync/)। কোনো প্যাকেজ যোগ করলে `uv` এটি স্বয়ংক্রিয়ভাবে করে।

///

/// tip | ফাইলগুলো সহজ ভাষায়

* `pyproject.toml`: প্রজেক্টের "পরিচয়পত্র"। এখানে প্রজেক্টের নাম আর কোন কোন প্যাকেজ লাগবে তার তালিকা থাকে, যেমন "fastapi লাগবে"।
* `uv.lock`: "হুবহু তালিকা"। কোন প্যাকেজের ঠিক কোন সংস্করণ ইনস্টল হয়েছে, তার নিখুঁত হিসাব। রেসিপির মতো, যাতে অন্য রান্নাঘরে রাঁধলেও স্বাদ একই হয়।
* `.venv`: প্রজেক্টের ভার্চুয়াল এনভায়রনমেন্ট, যেখানে আসলে প্যাকেজগুলো ইনস্টল থাকে। বিস্তারিত [ভার্চুয়াল এনভায়রনমেন্ট](../virtual-environments.md) পেজে।

///

/// details | FastAPI ইনস্টলেশনের বিকল্পগুলো

`uv add "fastapi[standard]"` দিয়ে ইনস্টল করলে কিছু ডিফল্ট ঐচ্ছিক স্ট্যান্ডার্ড ডিপেন্ডেন্সি সাথে আসে, যার মধ্যে `fastapi-cloud-cli`-ও আছে। এটি দিয়ে [FastAPI Cloud](https://fastapicloud.com)-এ ডিপ্লয় করা যায়।

ওই ঐচ্ছিক ডিপেন্ডেন্সিগুলো না চাইলে এর বদলে `uv add fastapi` দিয়ে ইনস্টল করতে পারেন।

স্ট্যান্ডার্ড ডিপেন্ডেন্সিগুলো চান কিন্তু `fastapi-cloud-cli` চান না, এমন হলে `uv add "fastapi[standard-no-fastapi-cloud-cli]"` দিয়ে ইনস্টল করতে পারেন।

///

/// details | এর বদলে `pip` ব্যবহার

আপনি যদি ভার্চুয়াল এনভায়রনমেন্ট আর প্যাকেজ নিজে হাতে সামলাতে চান, তাহলে একটি ভার্চুয়াল এনভায়রনমেন্ট তৈরি ও অ্যাক্টিভেট করে `pip install "fastapi[standard]"` দিয়ে FastAPI ইনস্টল করুন।

বিস্তারিত ধাপের জন্য [ভার্চুয়াল এনভায়রনমেন্ট গাইড](https://tiangolo.com/guides/virtual-environments/) পড়ুন। বাংলায় সংক্ষিপ্ত ধাপগুলো আছে আমাদের [ভার্চুয়াল এনভায়রনমেন্ট](../virtual-environments.md) পেজে।

///

## AI এজেন্ট স্কিল { #ai-agent-skills }

AI কোডিং এজেন্টদের (যেমন Claude Code, Cursor, GitHub Copilot, যারা আপনার হয়ে কোড লিখতে সাহায্য করে) জন্য FastAPI-তে একটি অফিসিয়াল "স্কিল" আছে। স্কিল হলো এজেন্টের জন্য লেখা নির্দেশনা, যাতে এজেন্ট FastAPI-এর সঠিক ও আধুনিক নিয়মে কোড লেখে। এটি প্যাকেজের সাথেই আসে, তাই এর নির্দেশনা আপনার প্রজেক্টে ইনস্টল করা FastAPI সংস্করণের সাথে মিলে থাকে, আর FastAPI আপডেট করলে এটিও আপডেট হয়।

প্রজেক্টে FastAPI ইনস্টল করার পরে <a href="https://library-skills.io">Library Skills</a> দিয়ে স্কিলটি ইনস্টল করতে পারেন:

```bash
uvx library-skills
```

/// note | নোট

`uvx` হলো `uv tool run`-এর একটি সংক্ষিপ্ত নাম। এটি Library Skills-কে একটি অস্থায়ী, আলাদা এনভায়রনমেন্টে চালায়, আর Library Skills আপনার প্রজেক্টে ইনস্টল করা প্যাকেজগুলো স্ক্যান করে।

///

স্কিলটি Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI, Pi, OpenCode এবং অন্যান্য বেশিরভাগ কোডিং এজেন্টের সাথে কাজ করে। Claude Code-এর জন্য, স্কিলটি কোথায় ইনস্টল করবেন জিজ্ঞেস করলে `.claude/skills` বেছে নিন।

## অ্যাডভান্সড ইউজার গাইড { #advanced-user-guide }

একটি **অ্যাডভান্সড ইউজার গাইড**-ও আছে, যা এই **টিউটোরিয়াল - ইউজার গাইড** শেষ করার পরে পড়তে পারেন।

**অ্যাডভান্সড ইউজার গাইড** এটির ওপর ভিত্তি করে তৈরি, একই ধারণা ব্যবহার করে, আর কিছু বাড়তি ফিচার শেখায়।

তবে আগে আপনার **টিউটোরিয়াল - ইউজার গাইড** (যা এখন পড়ছেন) পড়া উচিত।

এটি এমনভাবে সাজানো যে শুধু **টিউটোরিয়াল - ইউজার গাইড** দিয়েই একটি পূর্ণাঙ্গ অ্যাপ্লিকেশন বানাতে পারবেন, তারপর আপনার প্রয়োজন অনুযায়ী **অ্যাডভান্সড ইউজার গাইড**-এর কিছু বাড়তি ধারণা ব্যবহার করে বিভিন্নভাবে সেটি বাড়াতে পারবেন।

/// check | সংক্ষেপে মনে রাখুন

* প্রতিটি উদাহরণ `main.py`-তে রেখে `uv run fastapi dev` দিয়ে চালান।
* নতুন প্রজেক্ট: `uv init awesome-project --bare`, `cd awesome-project`, `uv add "fastapi[standard]"`।
* শুধু পড়বেন না, নিজে চালিয়ে আর বদলে দেখুন।
* আগে এই টিউটোরিয়াল, তারপর অ্যাডভান্সড গাইড।

///
