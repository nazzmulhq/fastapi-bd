# WebSocket টেস্ট করা { #testing-websockets }

/// note | এই পেজে যা শিখবেন

* সাধারণ HTTP রিকোয়েস্টের মতোই `TestClient` দিয়ে WebSocket টেস্ট করা।
* `with` স্টেটমেন্ট দিয়ে WebSocket সংযোগ খোলা ও বন্ধ করা।

///

WebSocket টেস্ট করতেও আপনি একই `TestClient` ব্যবহার করতে পারেন।

(WebSocket হলো ক্লায়েন্ট আর সার্ভারের মধ্যে খোলা থাকা একটি দুইমুখী সংযোগ। বিস্তারিত দেখুন [WebSockets](websockets.md) পেজে।)

এর জন্য `TestClient`-কে একটি `with` স্টেটমেন্টের ভেতরে ব্যবহার করে WebSocket-এ সংযোগ করুন:

{* ../../docs_src/app_testing/tutorial002_py310.py hl[27:31] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ১৩–১৭: অ্যাপের `/ws` WebSocket রাউট। এটি সংযোগ গ্রহণ (`accept`) করে, একটি JSON বার্তা পাঠায়, তারপর সংযোগ বন্ধ করে।
* লাইন ২৮: `TestClient(app)` দিয়ে একটি টেস্ট ক্লায়েন্ট তৈরি।
* লাইন ২৯: `client.websocket_connect("/ws")` WebSocket সংযোগ খোলে। `with` ব্লক শেষ হলে সংযোগ নিজে থেকেই বন্ধ হয়।
* লাইন ৩০: `websocket.receive_json()` সার্ভারের পাঠানো JSON বার্তা গ্রহণ করে।
* লাইন ৩১: `assert` দিয়ে যাচাই করা হয় যে বার্তাটি ঠিক যা আশা করা হয়েছিল তাই।

///

/// tip | উদাহরণ দিয়ে বুঝি

সাধারণ HTTP টেস্ট হলো চিঠি পাঠিয়ে উত্তর পাওয়ার মতো। WebSocket টেস্ট হলো ফোন কল: আগে কল সংযোগ করেন (`websocket_connect`), তারপর কথা শোনেন বা বলেন (`receive_json`, `send_json`), শেষে ফোন রাখেন (`with` ব্লকের শেষ)।

///

/// note | নোট

আরও বিস্তারিত জানতে Starlette-এর ডকুমেন্টেশনে [WebSocket টেস্ট করা](https://starlette.dev/testclient/#testing-websocket-sessions) দেখুন।

///

/// check | সংক্ষেপে মনে রাখুন

* WebSocket টেস্টে `with client.websocket_connect("/path") as websocket:` ব্যবহার করুন।
* ভেতরে `receive_json()`, `receive_text()`, `send_json()`, `send_text()` দিয়ে বার্তা আদান-প্রদান করুন।
* `assert` দিয়ে পাওয়া ডেটা যাচাই করুন, ঠিক সাধারণ টেস্টের মতো।

///
