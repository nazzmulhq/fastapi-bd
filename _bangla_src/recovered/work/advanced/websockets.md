# WebSockets { #websockets }

**FastAPI**-এর সাথে আপনি [WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API) ব্যবহার করতে পারেন।

## `websockets` ইনস্টল করুন { #install-websockets }

আপনার প্রজেক্টে `websockets` (একটি Python লাইব্রেরি যা "WebSocket" প্রোটোকল ব্যবহার সহজ করে) যোগ করুন:

<div class="termy">

⟦CODE1⟧

</div>

## WebSockets ক্লায়েন্ট { #websockets-client }

### প্রোডাকশনে { #in-production }

আপনার প্রোডাকশন সিস্টেমে সম্ভবত React, Vue.js বা Angular-এর মতো আধুনিক ফ্রেমওয়ার্ক দিয়ে তৈরি একটি ফ্রন্টএন্ড আছে।

আর আপনার ব্যাকএন্ডের সাথে WebSockets দিয়ে যোগাযোগ করতে আপনি সম্ভবত আপনার ফ্রন্টএন্ডের ইউটিলিটিগুলো ব্যবহার করবেন।

অথবা আপনার হয়তো একটি নেটিভ মোবাইল অ্যাপ্লিকেশন আছে যা নেটিভ কোডে সরাসরি আপনার WebSocket ব্যাকএন্ডের সাথে যোগাযোগ করে।

অথবা WebSocket এন্ডপয়েন্টের সাথে যোগাযোগের অন্য কোনো উপায় আপনার থাকতে পারে।

---

তবে এই উদাহরণের জন্য আমরা কিছু JavaScript-সহ একটি খুবই সহজ HTML ডকুমেন্ট ব্যবহার করব, সবকিছুই একটি লম্বা স্ট্রিংয়ের ভেতরে।

অবশ্যই এটি আদর্শ নয় এবং আপনি প্রোডাকশনে এটি ব্যবহার করবেন না।

প্রোডাকশনে আপনার কাছে ওপরের অপশনগুলোর একটি থাকবে।

তবে WebSockets-এর সার্ভার-সাইডে মনোযোগ দিতে এবং একটি কার্যকর উদাহরণ পেতে এটিই সবচেয়ে সহজ উপায়:

{* ../../docs_src/websockets_/tutorial001_py310.py hl[2,6:38,41:43] *}

## একটি `websocket` তৈরি করুন { #create-a-websocket }

আপনার **FastAPI** অ্যাপ্লিকেশনে একটি `websocket` তৈরি করুন:

{* ../../docs_src/websockets_/tutorial001_py310.py hl[1,46:47] *}

/// note | কারিগরি বিবরণ

আপনি `from starlette.websockets import WebSocket`-ও ব্যবহার করতে পারতেন।

**FastAPI** শুধু আপনার, অর্থাৎ ডেভেলপারের সুবিধার জন্য একই `WebSocket` সরাসরি দেয়। তবে এটি সরাসরি Starlette থেকে আসে।

///

## মেসেজের জন্য await করুন এবং মেসেজ পাঠান { #await-for-messages-and-send-messages }

আপনার WebSocket রাউটে আপনি মেসেজের জন্য `await` করতে এবং মেসেজ পাঠাতে পারেন।

{* ../../docs_src/websockets_/tutorial001_py310.py hl[48:52] *}

আপনি বাইনারি, টেক্সট ও JSON ডেটা গ্রহণ করতে ও পাঠাতে পারেন।

## চেষ্টা করে দেখুন { #try-it }

আপনার কোড `main.py` নামের একটি ফাইলে রাখুন এবং তারপর আপনার অ্যাপ্লিকেশন চালান:

<div class="termy">

⟦CODE2⟧

</div>

আপনার ব্রাউজারে [http://127.0.0.1:8000](http://127.0.0.1:8000) খুলুন।

আপনি এরকম একটি সহজ পেজ দেখবেন:

<img src="/img/tutorial/websockets/image01.png">

আপনি ইনপুট বক্সে মেসেজ লিখে পাঠাতে পারেন:

<img src="/img/tutorial/websockets/image02.png">

আর WebSockets-সহ আপনার **FastAPI** অ্যাপ্লিকেশন উত্তর দেবে:

<img src="/img/tutorial/websockets/image03.png">

আপনি অনেক মেসেজ পাঠাতে (এবং গ্রহণ করতে) পারেন:

<img src="/img/tutorial/websockets/image04.png">

আর সেগুলো সবই একই WebSocket কানেকশন ব্যবহার করবে।

## `Depends` ও অন্যান্য ব্যবহার { #using-depends-and-others }

WebSocket এন্ডপয়েন্টে আপনি `fastapi` থেকে ইম্পোর্ট করে এগুলো ব্যবহার করতে পারেন:

* `Depends`
* `Security`
* `Cookie`
* `Header`
* `Path`
* `Query`

এগুলো অন্যান্য FastAPI এন্ডপয়েন্ট/*পাথ অপারেশনের* মতোই কাজ করে:

{* ../../docs_src/websockets_/tutorial002_an_py310.py hl[68:69,82] *}

/// note | নোট

যেহেতু এটি একটি WebSocket, তাই একটি `HTTPException` রেইজ করা আসলে যুক্তিসঙ্গত নয়, এর বদলে আমরা একটি `WebSocketException` রেইজ করি।

আপনি [স্পেসিফিকেশনে সংজ্ঞায়িত বৈধ কোডগুলো](https://tools.ietf.org/html/rfc6455#section-7.4.1) থেকে একটি ক্লোজিং কোড ব্যবহার করতে পারেন।

///

### ডিপেন্ডেন্সিসহ WebSockets চেষ্টা করুন { #try-the-websockets-with-dependencies }

আপনার অ্যাপ্লিকেশন চালান:

<div class="termy">

⟦CODE3⟧

</div>

আপনার ব্রাউজারে [http://127.0.0.1:8000](http://127.0.0.1:8000) খুলুন।

সেখানে আপনি সেট করতে পারেন:

* "Item ID", যা পাথে ব্যবহার হয়।
* "Token", যা কুয়েরি প্যারামিটার হিসেবে ব্যবহার হয়।

/// tip | পরামর্শ

লক্ষ করুন, কুয়েরি `token` একটি ডিপেন্ডেন্সি দিয়ে সামলানো হবে।

///

এর মাধ্যমে আপনি WebSocket কানেক্ট করে তারপর মেসেজ পাঠাতে ও গ্রহণ করতে পারবেন:

<img src="/img/tutorial/websockets/image05.png">

## সংযোগ বিচ্ছিন্নতা ও একাধিক ক্লায়েন্ট সামলানো { #handling-disconnections-and-multiple-clients }

একটি WebSocket কানেকশন বন্ধ হলে `await websocket.receive_text()` একটি `WebSocketDisconnect` এক্সেপশন রেইজ করবে, যা আপনি এই উদাহরণের মতো ধরে সামলাতে পারেন।

{* ../../docs_src/websockets_/tutorial003_py310.py hl[79:81] *}

চেষ্টা করে দেখতে:

* কয়েকটি ব্রাউজার ট্যাবে অ্যাপটি খুলুন।
* সেগুলো থেকে মেসেজ লিখুন।
* তারপর একটি ট্যাব বন্ধ করুন।

এতে `WebSocketDisconnect` এক্সেপশন রেইজ হবে, এবং অন্য সব ক্লায়েন্ট এরকম একটি মেসেজ পাবে:

⟦CODE4⟧

/// tip | পরামর্শ

ওপরের অ্যাপটি একাধিক WebSocket কানেকশনে মেসেজ সামলানো ও সম্প্রচার করার উপায় দেখানোর জন্য একটি ন্যূনতম ও সহজ উদাহরণ।

তবে মনে রাখবেন, যেহেতু সবকিছু মেমরিতে, একটিমাত্র লিস্টে সামলানো হয়, তাই এটি কেবল প্রসেসটি চলার সময় কাজ করবে, এবং কেবল একটিমাত্র প্রসেসের সাথে কাজ করবে।

আপনার যদি FastAPI-এর সাথে সহজে যুক্ত করা যায় কিন্তু আরও মজবুত, Redis, PostgreSQL বা অন্যান্যের সাপোর্টসহ কিছু দরকার হয়, তাহলে [encode/broadcaster](https://github.com/encode/broadcaster) দেখুন।

///

## আরও তথ্য { #more-info }

অপশনগুলো সম্পর্কে আরও জানতে Starlette-এর ডকুমেন্টেশন দেখুন:

* [`WebSocket` ক্লাস](https://starlette.dev/websockets/)।
* [ক্লাস-ভিত্তিক WebSocket হ্যান্ডলিং](https://starlette.dev/endpoints/#websocketendpoint)।
