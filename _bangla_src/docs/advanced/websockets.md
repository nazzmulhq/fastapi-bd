# WebSockets { #websockets }

/// note | এই পেজে যা শিখবেন

* WebSocket কী, আর সাধারণ HTTP থেকে এটি কীভাবে আলাদা।
* FastAPI-তে একটি WebSocket এন্ডপয়েন্ট বানানো আর বার্তা পাঠানো-গ্রহণ করা।
* WebSocket-এ `Depends`, `Query`, `Cookie` ব্যবহার।
* সংযোগ বিচ্ছিন্ন হওয়া সামলানো আর একাধিক ব্যবহারকারীকে বার্তা পাঠানো (ছোট একটি চ্যাট রুম)।

///

**FastAPI**-এর সাথে [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) ব্যবহার করতে পারেন।

/// tip | WebSocket সহজ ভাষায়

সাধারণ HTTP হলো চিঠি আদান-প্রদানের মতো: ক্লায়েন্ট একটি প্রশ্ন পাঠায়, সার্ভার একটি উত্তর দেয়, ব্যাস, যোগাযোগ শেষ। নতুন কিছু জানতে আবার চিঠি পাঠাতে হয়।

WebSocket হলো ফোন কলের মতো: একবার সংযোগ হলে লাইন খোলা থাকে, আর দুই পক্ষই যেকোনো সময় কথা বলতে পারে। চ্যাট অ্যাপ, লাইভ গেম, শেয়ার বাজারের লাইভ দাম, এসবে এটি ব্যবহার হয়।

///

## `websockets` ইনস্টল করুন { #install-websockets }

আপনার প্রজেক্টে `websockets` যোগ করুন (একটি Python লাইব্রেরি, যা "WebSocket" প্রোটোকল ব্যবহার সহজ করে):

<div class="termy">

```console
$ uv add websockets

---> 100%
```

</div>

## WebSockets ক্লায়েন্ট { #websockets-client }

### প্রোডাকশনে { #in-production }

আপনার প্রোডাকশন সিস্টেমে সম্ভবত React, Vue.js বা Angular-এর মতো আধুনিক ফ্রেমওয়ার্ক দিয়ে তৈরি একটি ফ্রন্টএন্ড আছে।

আর আপনার ব্যাকএন্ডের সাথে WebSockets দিয়ে যোগাযোগ করতে সম্ভবত আপনার ফ্রন্টএন্ডের টুলগুলো ব্যবহার করবেন।

অথবা আপনার একটি নেটিভ মোবাইল অ্যাপ্লিকেশন থাকতে পারে, যা নেটিভ কোডে সরাসরি আপনার WebSocket ব্যাকএন্ডের সাথে যোগাযোগ করে।

অথবা WebSocket এন্ডপয়েন্টের সাথে যোগাযোগের অন্য যেকোনো উপায় থাকতে পারে।

---

কিন্তু এই উদাহরণের জন্য আমরা কিছু JavaScript-সহ খুবই সহজ একটি HTML ডকুমেন্ট ব্যবহার করব, সবকিছু একটি লম্বা স্ট্রিংয়ের ভেতরে।

অবশ্যই এটি সর্বোত্তম নয়, আর প্রোডাকশনে আপনি এটি ব্যবহার করবেন না।

প্রোডাকশনে ওপরের অপশনগুলোর একটি থাকবে।

কিন্তু WebSocket-এর সার্ভারের দিকে মনোযোগ দিতে আর একটি কাজ করা উদাহরণ পেতে এটিই সবচেয়ে সহজ উপায়:

{* ../../docs_src/websockets_/tutorial001_py310.py hl[2,6:38,41:43] *}

/// info | HTML অংশটি সহজ ভাষায়

* লাইন ১৪-১৭: বার্তা লেখার একটি ঘর আর "Send" বাটন।
* লাইন ২১: `new WebSocket("ws://localhost:8000/ws")` সার্ভারের `/ws` ঠিকানায় একটি WebSocket সংযোগ খোলে। খেয়াল করুন, ঠিকানা `http://` নয়, `ws://` দিয়ে শুরু।
* লাইন ২২-২৮: সার্ভার থেকে বার্তা এলে সেটি তালিকায় যোগ করে দেখায়।
* লাইন ২৯-৩৪: "Send" চাপলে লেখাটি `ws.send(...)` দিয়ে সার্ভারে পাঠায়।

///

## একটি `websocket` তৈরি করুন { #create-a-websocket }

আপনার **FastAPI** অ্যাপ্লিকেশনে একটি `websocket` তৈরি করুন:

{* ../../docs_src/websockets_/tutorial001_py310.py hl[1,46:47] *}

/// note | কারিগরি বিবরণ

`from starlette.websockets import WebSocket`-ও ব্যবহার করতে পারতেন।

**FastAPI** ডেভেলপার হিসেবে আপনার সুবিধার জন্যই সরাসরি একই `WebSocket` দেয়। কিন্তু এটি সরাসরি Starlette থেকে আসে।

///

## বার্তার জন্য অপেক্ষা আর বার্তা পাঠানো { #await-for-messages-and-send-messages }

আপনার WebSocket রাউটে বার্তার জন্য `await` করতে আর বার্তা পাঠাতে পারেন।

{* ../../docs_src/websockets_/tutorial001_py310.py hl[48:52] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৪৬: `@app.websocket("/ws")`: `@app.get` নয়, WebSocket-এর জন্য বিশেষ ডেকোরেটর।
* লাইন ৪৮: `await websocket.accept()`: সংযোগ গ্রহণ করা (ফোন রিসিভ করার মতো)।
* লাইন ৪৯: `while True:` অসীম লুপ, যতক্ষণ সংযোগ খোলা থাকে।
* লাইন ৫০: `await websocket.receive_text()`: ক্লায়েন্টের পরের বার্তার জন্য অপেক্ষা।
* লাইন ৫১: `await websocket.send_text(...)`: উত্তর পাঠানো।

///

আপনি বাইনারি, টেক্সট আর JSON ডেটা গ্রহণ ও পাঠাতে পারেন।

## চেষ্টা করুন { #try-it }

আপনার কোড `main.py` নামের একটি ফাইলে রেখে অ্যাপ্লিকেশন চালান:

<div class="termy">

```console
$ uv run fastapi dev

<span style="color: green;">INFO</span>:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</div>

ব্রাউজারে [http://127.0.0.1:8000](http://127.0.0.1:8000) খুলুন।

এমন একটি সহজ পেজ দেখবেন:

<img src="/img/tutorial/websockets/image01.png">

ইনপুট বক্সে বার্তা লিখে পাঠাতে পারেন:

<img src="/img/tutorial/websockets/image02.png">

আর WebSockets-সহ আপনার **FastAPI** অ্যাপ্লিকেশন উত্তর ফেরত দেবে:

<img src="/img/tutorial/websockets/image03.png">

আপনি অনেক বার্তা পাঠাতে (আর গ্রহণ করতে) পারেন:

<img src="/img/tutorial/websockets/image04.png">

আর এদের সবাই একই WebSocket সংযোগ ব্যবহার করবে।

## `Depends` আর অন্যান্য ব্যবহার { #using-depends-and-others }

WebSocket এন্ডপয়েন্টে `fastapi` থেকে ইমপোর্ট করে এগুলো ব্যবহার করতে পারেন:

* `Depends`
* `Security`
* `Cookie`
* `Header`
* `Path`
* `Query`

এগুলো অন্য FastAPI এন্ডপয়েন্ট/*পাথ অপারেশনের* মতোই কাজ করে:

{* ../../docs_src/websockets_/tutorial002_an_py310.py hl[68:69,82] *}

/// info | কোডটি সহজ ভাষায় (লাইন ৬৬-৯২)

* `get_cookie_or_token` ডিপেন্ডেন্সি: `session` কুকি বা `token` কুয়েরি প্যারামিটারের যেকোনো একটি থাকতে হবে, নইলে `WebSocketException` দিয়ে সংযোগ বন্ধ।
* WebSocket এন্ডপয়েন্টে পাথ প্যারামিটার (`item_id`), ঐচ্ছিক কুয়েরি (`q`) আর ডিপেন্ডেন্সি, সবই সাধারণ পাথ অপারেশনের মতো ঘোষণা করা।

///

/// note | নোট

যেহেতু এটি একটি WebSocket, তাই এখানে `HTTPException` রেইজ করার আসলে কোনো মানে হয় না, এর বদলে আমরা একটি `WebSocketException` রেইজ করি।

[স্পেসিফিকেশনে সংজ্ঞায়িত বৈধ কোডগুলো](https://tools.ietf.org/html/rfc6455#section-7.4.1) থেকে একটি ক্লোজিং কোড ব্যবহার করতে পারেন।

///

### ডিপেন্ডেন্সিসহ WebSockets চেষ্টা করুন { #try-the-websockets-with-dependencies }

আপনার অ্যাপ্লিকেশন চালান:

<div class="termy">

```console
$ uv run fastapi dev

<span style="color: green;">INFO</span>:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

</div>

ব্রাউজারে [http://127.0.0.1:8000](http://127.0.0.1:8000) খুলুন।

সেখানে সেট করতে পারবেন:

* "Item ID", যা পাথে ব্যবহার হয়।
* "Token", যা কুয়েরি প্যারামিটার হিসেবে ব্যবহার হয়।

/// tip | পরামর্শ

খেয়াল করুন, কুয়েরি `token` সামলাবে একটি ডিপেন্ডেন্সি।

///

এর মাধ্যমে আপনি WebSocket সংযোগ করে তারপর বার্তা পাঠাতে ও গ্রহণ করতে পারবেন:

<img src="/img/tutorial/websockets/image05.png">

## সংযোগ বিচ্ছিন্ন হওয়া আর একাধিক ক্লায়েন্ট সামলানো { #handling-disconnections-and-multiple-clients }

একটি WebSocket সংযোগ বন্ধ হলে `await websocket.receive_text()` একটি `WebSocketDisconnect` এক্সেপশন রেইজ করবে, যা আপনি তারপর এই উদাহরণের মতো ধরে সামলাতে পারেন।

{* ../../docs_src/websockets_/tutorial003_py310.py hl[79:81] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৪৪-৬০: `ConnectionManager` হলো চ্যাট রুমের "ব্যবস্থাপক":
    * `active_connections`: এখন যুক্ত সবার তালিকা।
    * `connect`: নতুন কেউ এলে সংযোগ গ্রহণ করে তালিকায় যোগ।
    * `disconnect`: কেউ চলে গেলে তালিকা থেকে বাদ।
    * `send_personal_message`: শুধু একজনকে বার্তা।
    * `broadcast`: সবাইকে বার্তা।
* লাইন ৭৩-৭৮: সংযোগ হলে লুপে বার্তা গ্রহণ, প্রেরককে "You wrote: ..." আর সবাইকে "Client #... says: ..." পাঠানো।
* লাইন ৭৯-৮১: কেউ ট্যাব বন্ধ করলে `WebSocketDisconnect` ধরা হয়, তালিকা থেকে বাদ দিয়ে সবাইকে জানানো হয় যে সে চলে গেছে।

///

চেষ্টা করে দেখতে:

* কয়েকটি ব্রাউজার ট্যাবে অ্যাপটি খুলুন।
* সেগুলো থেকে বার্তা লিখুন।
* তারপর একটি ট্যাব বন্ধ করুন।

এতে `WebSocketDisconnect` এক্সেপশন রেইজ হবে, আর অন্য সব ক্লায়েন্ট এমন একটি বার্তা পাবে:

```
Client #1596980209979 left the chat
```

/// tip | পরামর্শ

ওপরের অ্যাপটি একাধিক WebSocket সংযোগে বার্তা কীভাবে সামলাতে আর সবাইকে পাঠাতে হয় তা দেখানোর জন্য একটি ন্যূনতম আর সহজ উদাহরণ।

তবে মনে রাখবেন, যেহেতু সবকিছু মেমরিতে, একটিমাত্র তালিকায় সামলানো হচ্ছে, তাই এটি শুধু প্রসেসটি চলা অবস্থাতেই কাজ করবে, আর শুধু একটিমাত্র প্রসেসের সাথে কাজ করবে। (একাধিক ওয়ার্কার চালালে একেক ওয়ার্কারের নিজস্ব তালিকা থাকবে, তারা একে অপরের ব্যবহারকারীদের দেখবে না।)

FastAPI-এর সাথে সহজে যুক্ত করা যায় কিন্তু আরও মজবুত, Redis, PostgreSQL বা অন্যদের সাপোর্টসহ কিছু দরকার হলে [encode/broadcaster](https://github.com/encode/broadcaster) দেখুন।

///

## আরও তথ্য { #more-info }

অপশনগুলো সম্পর্কে আরও জানতে Starlette-এর ডকুমেন্টেশন দেখুন:

* [`WebSocket` ক্লাস](https://starlette.dev/websockets/)।
* [ক্লাস-ভিত্তিক WebSocket সামলানো](https://starlette.dev/endpoints/#websocketendpoint)।

/// check | সংক্ষেপে মনে রাখুন

* `@app.websocket("/ws")` আর `async def f(websocket: WebSocket)`।
* `await websocket.accept()`, তারপর লুপে `receive_text()` আর `send_text()`।
* সংযোগ বন্ধ হলে `WebSocketDisconnect` ধরুন।
* এরর দিতে `HTTPException` নয়, `WebSocketException`।
* একাধিক প্রসেসে চ্যাটের জন্য Redis-এর মতো কিছু লাগবে।

///
