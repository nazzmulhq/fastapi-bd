# রেফারেন্স { #reference }

/// note | এই অংশটি কী, আর কীভাবে ব্যবহার করবেন

**রেফারেন্স** হলো FastAPI-এর একটি "অভিধান"। এখানে প্রতিটি ক্লাস (যেমন `FastAPI`, `APIRouter`), ফাংশন (যেমন `Query()`, `Depends()`) আর তাদের প্রতিটি প্যারামিটারের বিস্তারিত তালিকা আছে।

* টিউটোরিয়াল হলো গল্পের বই: ধাপে ধাপে শেখায়।
* রেফারেন্স হলো অভিধান: নির্দিষ্ট একটি শব্দ (প্যারামিটার) এর মানে খুঁজতে আসবেন।

যেমন, ভাবছেন "`FastAPI()`-তে `docs_url` প্যারামিটার কী করে?" তখন [`FastAPI` ক্লাস](fastapi.md) পেজে গিয়ে খুঁজুন।

///

এখানে রেফারেন্স বা কোড API দেওয়া হলো: ক্লাস, ফাংশন, প্যারামিটার, অ্যাট্রিবিউট এবং আপনার অ্যাপ্লিকেশনে ব্যবহার করতে পারেন এমন FastAPI-এর সব অংশ।

আপনি যদি **FastAPI শিখতে** চান, তাহলে [FastAPI টিউটোরিয়াল](https://fastapi.tiangolo.com/tutorial/) পড়াই আপনার জন্য অনেক ভালো।

/// tip | রেফারেন্স পেজ কীভাবে পড়বেন

* প্রতিটি পেজের শুরুতে সহজ ভাষায় একটি ব্যাখ্যা আর ছোট উদাহরণ আছে।
* তার নিচে স্বয়ংক্রিয়ভাবে তৈরি বিস্তারিত তালিকা: প্রতিটি প্যারামিটারের নাম, টাইপ, ডিফল্ট মান আর বর্ণনা।
* প্যারামিটারের নাম আর কোড ইংরেজিতেই থাকে, কারণ কোডে ঠিক এভাবেই লিখতে হয়।
* পরিভাষা অচেনা লাগলে [সহজ শব্দকোষ](../learn/glossary.md) দেখুন।

///

/// info | কোন পেজে কী পাবেন

| পেজ | কী আছে |
| --- | --- |
| [`FastAPI` ক্লাস](fastapi.md) | মূল অ্যাপ অবজেক্ট আর এর সব সেটিংস |
| [রিকোয়েস্ট প্যারামিটার](parameters.md) | `Query()`, `Path()`, `Body()`, `Header()`, `Cookie()`, `Form()`, `File()` |
| [স্ট্যাটাস কোড](status.md) | `status.HTTP_404_NOT_FOUND` এর মতো নামযুক্ত কোড |
| [`UploadFile`](uploadfile.md) | আপলোড করা ফাইল নিয়ে কাজ |
| [Exceptions](exceptions.md) | `HTTPException`, `WebSocketException` |
| [Dependencies](dependencies.md) | `Depends()`, `Security()` |
| [`APIRouter`](apirouter.md) | অ্যাপকে একাধিক ফাইলে ভাগ করা |
| [Background Tasks](background.md) | রেসপন্সের পরে চলা কাজ |
| [`Request`](request.md), [`Response`](response.md) | কাঁচা রিকোয়েস্ট আর রেসপন্স অবজেক্ট |
| [WebSockets](websockets.md) | দুইমুখী সংযোগ |
| [Custom Response](responses.md) | `JSONResponse`, `HTMLResponse`, `FileResponse` ইত্যাদি |
| [Middleware](middleware.md) | CORS, GZip ইত্যাদি |
| [Security](security/index.md) | OAuth2, API key, HTTP Basic/Bearer |

///
