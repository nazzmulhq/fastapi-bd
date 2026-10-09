# ইভেন্ট টেস্ট করা: lifespan এবং startup - shutdown { #testing-events-lifespan-and-startup-shutdown }

/// note | এই পেজে যা শিখবেন

* টেস্টের সময় অ্যাপের `lifespan` (চালু ও বন্ধ হওয়ার কোড) কীভাবে চালাবেন।
* কেন `TestClient`-কে `with` স্টেটমেন্টের ভেতরে ব্যবহার করতে হয়।
* পুরনো `startup` আর `shutdown` ইভেন্ট টেস্ট করা।

///

অনেক অ্যাপ চালু হওয়ার সময় কিছু প্রস্তুতি নেয় (যেমন ডেটাবেস সংযোগ খোলা, মেশিন লার্নিং মডেল লোড করা) আর বন্ধ হওয়ার সময় পরিষ্কার করে। এগুলো লেখা হয় `lifespan`-এ (বিস্তারিত দেখুন [Lifespan ইভেন্ট](events.md) পেজে)।

টেস্টে যখন `lifespan` চালানো দরকার, তখন `TestClient`-কে একটি `with` স্টেটমেন্টের সাথে ব্যবহার করুন:

{* ../../docs_src/app_testing/tutorial004_py310.py hl[9:15,18,27:28,30:32,41:43] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৯–১৫: `lifespan` ফাংশন। `yield`-এর আগের অংশ (লাইন ১১–১২) অ্যাপ চালু হওয়ার সময় চলে আর `items`-এ ডেটা রাখে। `yield`-এর পরের অংশ (লাইন ১৫) অ্যাপ বন্ধ হওয়ার সময় চলে আর `items` খালি করে।
* লাইন ১৮: `FastAPI(lifespan=lifespan)` দিয়ে অ্যাপকে lifespan জানানো।
* লাইন ২৭–২৮: `with` ব্লকের আগে lifespan এখনো চলেনি, তাই `items` খালি।
* লাইন ৩০–৩২: `with TestClient(app) as client:` ব্লকে ঢুকলেই lifespan শুরু হয়, তাই `items`-এ ডেটা চলে আসে।
* লাইন ৪১–৪৩: `with` ব্লক শেষ হওয়া মানে অ্যাপ বন্ধ হওয়ার অনুকরণ। lifespan-এর শেষ অংশ চলে আর `items` আবার খালি হয়।

///

/// warning | সাধারণ ভুল

শুধু `client = TestClient(app)` লিখলে (`with` ছাড়া) lifespan চলে **না**। তখন চালু হওয়ার সময়ের প্রস্তুতি (যেমন ডেটা লোড) হবে না আর টেস্ট অপ্রত্যাশিতভাবে ব্যর্থ হতে পারে। lifespan দরকার হলে সবসময় `with TestClient(app) as client:` ব্যবহার করুন।

///

আরও বিস্তারিত পড়তে পারেন ["অফিসিয়াল Starlette ডকুমেন্টেশন সাইটে টেস্টে lifespan চালানো"](https://starlette.dev/lifespan/#running-lifespan-in-tests) অংশে।

পুরনো (deprecated) `startup` আর `shutdown` ইভেন্টের জন্য `TestClient` এভাবে ব্যবহার করতে পারেন:

{* ../../docs_src/app_testing/tutorial003_py310.py hl[9:12,20:24] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ৯–১২: `@app.on_event("startup")` দিয়ে অ্যাপ চালু হওয়ার সময় চলার একটি ফাংশন, যা `items`-এ ডেটা রাখে।
* লাইন ২১: এখানেও `with TestClient(app) as client:` ব্যবহার করা হয়েছে, যাতে startup ইভেন্ট চলে।
* লাইন ২২–২৪: এখন `/items/foo` রিকোয়েস্ট করলে startup-এ রাখা ডেটা পাওয়া যায়।

নতুন কোডে `on_event`-এর বদলে `lifespan` ব্যবহার করাই ভালো।

///

/// check | সংক্ষেপে মনে রাখুন

* `with TestClient(app) as client:` ব্লকে ঢুকলে অ্যাপ "চালু" হয়, বের হলে "বন্ধ" হয়।
* lifespan বা startup/shutdown কোড টেস্টে চালাতে চাইলে `with` বাধ্যতামূলক।
* নতুন প্রজেক্টে `lifespan` ব্যবহার করুন, `on_event` পুরনো পদ্ধতি।

///
