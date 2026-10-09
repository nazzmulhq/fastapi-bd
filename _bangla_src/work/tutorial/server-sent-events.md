# সার্ভার-সেন্ট ইভেন্ট (SSE) { #server-sent-events-sse }

**সার্ভার-সেন্ট ইভেন্ট** (SSE) ব্যবহার করে আপনি ক্লায়েন্টের কাছে ডেটা স্ট্রিম করতে পারেন।

এটি [JSON Lines স্ট্রিম করুন](stream-json-lines.md)-এর মতো, তবে `text/event-stream` ফরম্যাট ব্যবহার করে, যা ব্রাউজারগুলো [`EventSource` API](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) দিয়ে স্বাভাবিকভাবেই সাপোর্ট করে।

/// note | নোট

FastAPI 0.135.0-এ যোগ করা হয়েছে।

///

## সার্ভার-সেন্ট ইভেন্ট কী? { #what-are-server-sent-events }

SSE হলো HTTP-এর মাধ্যমে সার্ভার থেকে ক্লায়েন্টে ডেটা স্ট্রিম করার একটি স্ট্যান্ডার্ড।

প্রতিটি ইভেন্ট হলো `data`, `event`, `id` ও `retry`-এর মতো "ফিল্ড"-সহ একটি ছোট টেক্সট ব্লক, যেগুলো ফাঁকা লাইন দিয়ে আলাদা করা।

এটি দেখতে এরকম:

⟦CODE1⟧

SSE সাধারণত AI চ্যাট স্ট্রিমিং, লাইভ নোটিফিকেশন, লগ ও অবজার্ভেবিলিটি, এবং এমন অন্যান্য ক্ষেত্রে ব্যবহার হয় যেখানে সার্ভার ক্লায়েন্টের কাছে আপডেট পাঠায়।

/// tip | পরামর্শ

আপনি যদি বাইনারি ডেটা স্ট্রিম করতে চান, যেমন ভিডিও বা অডিও, তাহলে অ্যাডভান্সড গাইড দেখুন: [ডেটা স্ট্রিম](../advanced/stream-data.md)।

///

## FastAPI দিয়ে SSE স্ট্রিম করুন { #stream-sse-with-fastapi }

FastAPI দিয়ে SSE স্ট্রিম করতে আপনার *পাথ অপারেশন ফাংশনে* `yield` ব্যবহার করুন এবং `response_class=EventSourceResponse` সেট করুন।

`fastapi.sse` থেকে `EventSourceResponse` ইম্পোর্ট করুন:

{* ../../docs_src/server_sent_events/tutorial001_py310.py ln[1:25] hl[4,22] *}

yield করা প্রতিটি আইটেম JSON হিসেবে এনকোড হয় এবং একটি SSE ইভেন্টের `data:` ফিল্ডে পাঠানো হয়।

আপনি যদি রিটার্ন টাইপ `AsyncIterable[Item]` হিসেবে ঘোষণা করেন, তাহলে FastAPI এটি ব্যবহার করে Pydantic দিয়ে ডেটা **ভ্যালিডেট**, **ডকুমেন্ট** ও **সিরিয়ালাইজ** করবে।

{* ../../docs_src/server_sent_events/tutorial001_py310.py ln[1:25] hl[10:12,23] *}

/// tip | পরামর্শ

যেহেতু Pydantic এটি **Rust**-এর দিকে সিরিয়ালাইজ করবে, তাই রিটার্ন টাইপ ঘোষণা না করার তুলনায় আপনি অনেক বেশি **পারফরম্যান্স** পাবেন।

///

### non-async *পাথ অপারেশন ফাংশন* { #non-async-path-operation-functions }

আপনি সাধারণ `def` ফাংশনও (`async` ছাড়া) ব্যবহার করতে পারেন, এবং একইভাবে `yield` ব্যবহার করতে পারেন।

FastAPI নিশ্চিত করবে যে এটি সঠিকভাবে চলে, যাতে ইভেন্ট লুপ ব্লক না হয়।

যেহেতু এক্ষেত্রে ফাংশনটি async নয়, তাই সঠিক রিটার্ন টাইপ হবে `Iterable[Item]`:

{* ../../docs_src/server_sent_events/tutorial001_py310.py ln[28:31] hl[29] *}

### রিটার্ন টাইপ ছাড়া { #no-return-type }

আপনি রিটার্ন টাইপ বাদও দিতে পারেন। FastAPI ডেটা রূপান্তর করে পাঠাতে [`jsonable_encoder`](./encoder.md) ব্যবহার করবে।

{* ../../docs_src/server_sent_events/tutorial001_py310.py ln[34:37] hl[35] *}

## `ServerSentEvent` { #serversentevent }

আপনার যদি `event`, `id`, `retry` বা `comment`-এর মতো SSE ফিল্ড সেট করতে হয়, তাহলে সাধারণ ডেটার বদলে `ServerSentEvent` অবজেক্ট yield করতে পারেন।

`fastapi.sse` থেকে `ServerSentEvent` ইম্পোর্ট করুন:

{* ../../docs_src/server_sent_events/tutorial002_py310.py hl[4,26] *}

`data` ফিল্ড সবসময় JSON হিসেবে এনকোড হয়। JSON হিসেবে সিরিয়ালাইজযোগ্য যেকোনো ভ্যালু, Pydantic মডেলসহ, আপনি দিতে পারেন।

## কাঁচা ডেটা { #raw-data }

আপনার যদি JSON এনকোডিং **ছাড়া** ডেটা পাঠাতে হয়, তাহলে `data`-এর বদলে `raw_data` ব্যবহার করুন।

এটি আগে থেকে ফরম্যাট করা টেক্সট, লগ লাইন, বা `[DONE]`-এর মতো বিশেষ <dfn title="একটি বিশেষ শর্ত বা অবস্থা নির্দেশ করতে ব্যবহৃত একটি ভ্যালু">"sentinel"</dfn> ভ্যালু পাঠাতে কাজে আসে।

{* ../../docs_src/server_sent_events/tutorial003_py310.py hl[17] *}

/// note | নোট

`data` ও `raw_data` পরস্পর বর্জনীয়। প্রতিটি `ServerSentEvent`-এ আপনি এগুলোর কেবল একটি সেট করতে পারবেন।

///

## `Last-Event-ID` দিয়ে আবার শুরু করা { #resuming-with-last-event-id }

কানেকশন বিচ্ছিন্ন হওয়ার পরে কোনো ব্রাউজার যখন আবার কানেক্ট করে, তখন এটি সর্বশেষ প্রাপ্ত `id`-টি `Last-Event-ID` হেডারে পাঠায়।

আপনি এটি একটি হেডার প্যারামিটার হিসেবে পড়ে ক্লায়েন্ট যেখানে ছেড়েছিল সেখান থেকে স্ট্রিম আবার শুরু করতে ব্যবহার করতে পারেন:

{* ../../docs_src/server_sent_events/tutorial004_py310.py hl[25,27,31] *}

## POST-সহ SSE { #sse-with-post }

SSE শুধু `GET` নয়, **যেকোনো HTTP মেথডের** সাথে কাজ করে।

এটি [MCP](https://modelcontextprotocol.io)-এর মতো প্রোটোকলের জন্য কাজে আসে, যেগুলো `POST`-এর মাধ্যমে SSE স্ট্রিম করে:

{* ../../docs_src/server_sent_events/tutorial005_py310.py hl[14] *}

## কারিগরি বিবরণ { #technical-details }

FastAPI শুরু থেকেই SSE-এর কিছু সর্বোত্তম চর্চা বাস্তবায়ন করে।

* কোনো মেসেজ না থাকলে প্রতি ১৫ সেকেন্ডে একটি **"keep alive" `ping` কমেন্ট** পাঠায়, যাতে কিছু প্রক্সি কানেকশন বন্ধ না করে দেয়, যেমনটা [HTML স্পেসিফিকেশন: Server-Sent Events](https://html.spec.whatwg.org/multipage/server-sent-events.html#authoring-notes)-এ পরামর্শ দেওয়া হয়েছে।
* স্ট্রিমের **ক্যাশিং প্রতিরোধ** করতে `Cache-Control: no-cache` হেডার সেট করে।
* Nginx-এর মতো কিছু প্রক্সিতে **বাফারিং প্রতিরোধ** করতে একটি বিশেষ হেডার `X-Accel-Buffering: no` সেট করে।

এ নিয়ে আপনাকে কিছুই করতে হবে না, এটি শুরু থেকেই কাজ করে। 🤓
