# মেটাডেটা ও ডকুমেন্টেশন URL { #metadata-and-docs-urls }

আপনার **FastAPI** অ্যাপ্লিকেশনে আপনি বেশ কয়েকটি মেটাডেটা কনফিগারেশন কাস্টমাইজ করতে পারেন।

## API-এর জন্য মেটাডেটা { #metadata-for-api }

OpenAPI স্পেসিফিকেশন ও স্বয়ংক্রিয় API ডকুমেন্টেশন UI-তে ব্যবহৃত নিচের ফিল্ডগুলো আপনি সেট করতে পারেন:

| প্যারামিটার | টাইপ | বিবরণ |
|------------|------|-------------|
| `title` | `str` | API-এর শিরোনাম। |
| `summary` | `str` | API-এর একটি সংক্ষিপ্ত সারাংশ। <small>OpenAPI 3.1.0, FastAPI 0.99.0 থেকে উপলব্ধ।</small> |
| `description` | `str` | API-এর একটি সংক্ষিপ্ত বিবরণ। এতে Markdown ব্যবহার করা যায়। |
| `version` | `str` | API-এর ভার্সন। এটি আপনার নিজের অ্যাপ্লিকেশনের ভার্সন, OpenAPI-এর নয়। যেমন `2.5.0`। |
| `terms_of_service` | `str` | API-এর সেবার শর্তাবলির একটি URL। দেওয়া হলে এটি অবশ্যই একটি URL হতে হবে। |
| `contact` | `dict` | প্রকাশিত API-এর যোগাযোগের তথ্য। এতে বেশ কয়েকটি ফিল্ড থাকতে পারে। <details><summary><code>contact</code> ফিল্ডসমূহ</summary><table><thead><tr><th>প্যারামিটার</th><th>টাইপ</th><th>বিবরণ</th></tr></thead><tbody><tr><td><code>name</code></td><td><code>str</code></td><td>যোগাযোগের ব্যক্তি/প্রতিষ্ঠানের শনাক্তকারী নাম।</td></tr><tr><td><code>url</code></td><td><code>str</code></td><td>যোগাযোগের তথ্যের দিকে নির্দেশকারী URL। অবশ্যই একটি URL-এর ফরম্যাটে হতে হবে।</td></tr><tr><td><code>email</code></td><td><code>str</code></td><td>যোগাযোগের ব্যক্তি/প্রতিষ্ঠানের ইমেইল ঠিকানা। অবশ্যই একটি ইমেইল ঠিকানার ফরম্যাটে হতে হবে।</td></tr></tbody></table></details> |
| `license_info` | `dict` | প্রকাশিত API-এর লাইসেন্সের তথ্য। এতে বেশ কয়েকটি ফিল্ড থাকতে পারে। <details><summary><code>license_info</code> ফিল্ডসমূহ</summary><table><thead><tr><th>প্যারামিটার</th><th>টাইপ</th><th>বিবরণ</th></tr></thead><tbody><tr><td><code>name</code></td><td><code>str</code></td><td><strong>আবশ্যক</strong> (যদি একটি <code>license_info</code> সেট করা থাকে)। API-এর জন্য ব্যবহৃত লাইসেন্সের নাম।</td></tr><tr><td><code>identifier</code></td><td><code>str</code></td><td>API-এর জন্য একটি [SPDX](https://spdx.org/licenses/) লাইসেন্স এক্সপ্রেশন। <code>identifier</code> ফিল্ডটি <code>url</code> ফিল্ডের সাথে পরস্পর বর্জনীয়। <small>OpenAPI 3.1.0, FastAPI 0.99.0 থেকে উপলব্ধ।</small></td></tr><tr><td><code>url</code></td><td><code>str</code></td><td>API-এর জন্য ব্যবহৃত লাইসেন্সের একটি URL। অবশ্যই একটি URL-এর ফরম্যাটে হতে হবে।</td></tr></tbody></table></details> |

আপনি এগুলো এভাবে সেট করতে পারেন:

{* ../../docs_src/metadata/tutorial001_py310.py hl[3:16, 19:32] *}

/// tip | পরামর্শ

`description` ফিল্ডে আপনি Markdown লিখতে পারেন এবং তা আউটপুটে রেন্ডার হবে।

///

এই কনফিগারেশনসহ স্বয়ংক্রিয় API ডকুমেন্টেশন দেখতে এরকম হবে:

<img src="/img/tutorial/metadata/image01.png">

## লাইসেন্স identifier { #license-identifier }

OpenAPI 3.1.0 ও FastAPI 0.99.0 থেকে আপনি একটি `url`-এর বদলে একটি `identifier` দিয়েও `license_info` সেট করতে পারেন।

যেমন:

{* ../../docs_src/metadata/tutorial001_1_py310.py hl[31] *}

## ট্যাগের জন্য মেটাডেটা { #metadata-for-tags }

`openapi_tags` প্যারামিটার দিয়ে আপনার পাথ অপারেশনগুলো দলবদ্ধ করতে ব্যবহৃত বিভিন্ন ট্যাগের জন্যও অতিরিক্ত মেটাডেটা যোগ করতে পারেন।

এটি প্রতিটি ট্যাগের জন্য একটি করে ডিকশনারি ধারণকারী একটি লিস্ট নেয়।

প্রতিটি ডিকশনারিতে থাকতে পারে:

* `name` (**আবশ্যক**): আপনার *পাথ অপারেশন* ও `APIRouter`-গুলোর `tags` প্যারামিটারে ব্যবহৃত একই ট্যাগ নামসহ একটি `str`।
* `description`: ট্যাগের একটি সংক্ষিপ্ত বিবরণসহ একটি `str`। এতে Markdown থাকতে পারে এবং তা ডকুমেন্টেশন UI-তে দেখানো হবে।
* `externalDocs`: বাহ্যিক ডকুমেন্টেশন বর্ণনাকারী একটি `dict`, যাতে থাকে:
    * `description`: বাহ্যিক ডকুমেন্টেশনের একটি সংক্ষিপ্ত বিবরণসহ একটি `str`।
    * `url` (**আবশ্যক**): বাহ্যিক ডকুমেন্টেশনের URL-সহ একটি `str`।

### ট্যাগের জন্য মেটাডেটা তৈরি করুন { #create-metadata-for-tags }

চলুন `users` ও `items`-এর ট্যাগসহ একটি উদাহরণে এটি চেষ্টা করি।

আপনার ট্যাগগুলোর জন্য মেটাডেটা তৈরি করে `openapi_tags` প্যারামিটারে দিন:

{* ../../docs_src/metadata/tutorial004_py310.py hl[3:16,18] *}

লক্ষ করুন, বিবরণের ভেতরে আপনি Markdown ব্যবহার করতে পারেন, যেমন "login" বোল্ডে (**login**) এবং "fancy" ইটালিকে (_fancy_) দেখানো হবে।

/// tip | পরামর্শ

আপনার ব্যবহৃত সব ট্যাগের জন্য মেটাডেটা যোগ করতে হবে না।

///

### আপনার ট্যাগগুলো ব্যবহার করুন { #use-your-tags }

আপনার *পাথ অপারেশনগুলোকে* (এবং `APIRouter`-গুলোকে) বিভিন্ন ট্যাগে অ্যাসাইন করতে সেগুলোর সাথে `tags` প্যারামিটার ব্যবহার করুন:

{* ../../docs_src/metadata/tutorial004_py310.py hl[21,26] *}

/// note | নোট

ট্যাগ সম্পর্কে আরও পড়ুন [পাথ অপারেশন কনফিগারেশন](path-operation-configuration.md#tags)-এ।

///

### ডকুমেন্টেশন দেখুন { #check-the-docs }

এখন ডকুমেন্টেশন দেখলে সেগুলোতে সব অতিরিক্ত মেটাডেটা দেখা যাবে:

<img src="/img/tutorial/metadata/image02.png">

### ট্যাগের ক্রম { #order-of-tags }

প্রতিটি ট্যাগ মেটাডেটা ডিকশনারির ক্রমই ডকুমেন্টেশন UI-তে দেখানো ক্রম নির্ধারণ করে।

যেমন, বর্ণানুক্রমে `users` `items`-এর পরে আসার কথা হলেও এটি আগে দেখানো হয়, কারণ আমরা লিস্টের প্রথম ডিকশনারি হিসেবে এর মেটাডেটা যোগ করেছি।

## OpenAPI URL { #openapi-url }

ডিফল্টভাবে OpenAPI স্কিমা `/openapi.json`-এ সার্ভ করা হয়।

তবে আপনি `openapi_url` প্যারামিটার দিয়ে এটি কনফিগার করতে পারেন।

যেমন, এটি `/api/v1/openapi.json`-এ সার্ভ করার জন্য সেট করতে:

{* ../../docs_src/metadata/tutorial002_py310.py hl[3] *}

আপনি যদি OpenAPI স্কিমা পুরোপুরি বন্ধ করতে চান, তাহলে `openapi_url=None` সেট করতে পারেন, এতে এটি ব্যবহারকারী ডকুমেন্টেশন ইউজার ইন্টারফেসগুলোও বন্ধ হয়ে যাবে।

## ডকুমেন্টেশন URL { #docs-urls }

অন্তর্ভুক্ত দুটি ডকুমেন্টেশন ইউজার ইন্টারফেস আপনি কনফিগার করতে পারেন:

* **Swagger UI**: `/docs`-এ সার্ভ করা হয়।
    * `docs_url` প্যারামিটার দিয়ে এর URL সেট করতে পারেন।
    * `docs_url=None` সেট করে এটি বন্ধ করতে পারেন।
* **ReDoc**: `/redoc`-এ সার্ভ করা হয়।
    * `redoc_url` প্যারামিটার দিয়ে এর URL সেট করতে পারেন।
    * `redoc_url=None` সেট করে এটি বন্ধ করতে পারেন।

যেমন, Swagger UI-কে `/documentation`-এ সার্ভ করার জন্য সেট করতে এবং ReDoc বন্ধ করতে:

{* ../../docs_src/metadata/tutorial003_py310.py hl[3] *}
