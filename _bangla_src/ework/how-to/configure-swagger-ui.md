# Swagger UI কনফিগার করা { #configure-swagger-ui }

/// note | এই পেজে যা শিখবেন

* `swagger_ui_parameters` দিয়ে `/docs` পেজের চেহারা আর আচরণ বদলানো।
* সিনট্যাক্স হাইলাইটিং বন্ধ করা বা রঙের থিম বদলানো।
* FastAPI-এর ডিফল্ট Swagger UI সেটিংস ওভাররাইড করা।

///

আপনি কিছু বাড়তি [Swagger UI প্যারামিটার](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/) কনফিগার করতে পারেন।

এগুলো কনফিগার করতে, `FastAPI()` অ্যাপ অবজেক্ট তৈরির সময় বা `get_swagger_ui_html()` ফাংশনে `swagger_ui_parameters` আর্গুমেন্টটি দিন।

`swagger_ui_parameters` একটি ডিকশনারি নেয়, যাতে থাকা কনফিগারেশনগুলো সরাসরি Swagger UI-তে পাঠানো হয়।

FastAPI কনফিগারেশনগুলোকে JavaScript-এর সাথে মানানসই করতে **JSON**-এ রূপান্তর করে, কারণ Swagger UI-র সেটাই দরকার।

(Swagger UI হলো `/docs`-এ দেখা সেই ইন্টারঅ্যাকটিভ পেজ, যেখানে আপনি "Try it out" চেপে API পরীক্ষা করেন।)

## সিনট্যাক্স হাইলাইটিং বন্ধ করা { #disable-syntax-highlighting }

যেমন, Swagger UI-তে সিনট্যাক্স হাইলাইটিং (কোডের বিভিন্ন অংশ বিভিন্ন রঙে দেখানো) বন্ধ করতে পারেন।

সেটিংস না বদলালে, ডিফল্টভাবে সিনট্যাক্স হাইলাইটিং চালু থাকে:

<img src="/img/tutorial/extending-openapi/image02.png">

কিন্তু `syntaxHighlight`-কে `False` সেট করে এটি বন্ধ করতে পারেন:

{* ../../docs_src/configure_swagger_ui/tutorial001_py310.py hl[3] *}

...আর তারপর Swagger UI আর সিনট্যাক্স হাইলাইটিং দেখাবে না:

<img src="/img/tutorial/extending-openapi/image03.png">

/// tip | কখন কাজে লাগে

খুব বড় JSON রেসপন্স হলে রঙ করতে ব্রাউজারের অনেক সময় লাগে, পেজ ধীর হয়ে যায়। তখন হাইলাইটিং বন্ধ করলে ডকস দ্রুত চলে।

///

## থিম বদলানো { #change-the-theme }

একইভাবে `"syntaxHighlight.theme"` কী দিয়ে সিনট্যাক্স হাইলাইটিংয়ের থিম সেট করতে পারেন (লক্ষ্য করুন, এর মাঝখানে একটি ডট আছে):

{* ../../docs_src/configure_swagger_ui/tutorial002_py310.py hl[3] *}

সেই কনফিগারেশনটি সিনট্যাক্স হাইলাইটিংয়ের রঙের থিম বদলে দেবে:

<img src="/img/tutorial/extending-openapi/image04.png">

## ডিফল্ট Swagger UI প্যারামিটার বদলানো { #change-default-swagger-ui-parameters }

FastAPI-তে বেশিরভাগ ক্ষেত্রের জন্য উপযুক্ত কিছু ডিফল্ট কনফিগারেশন প্যারামিটার আছে।

এতে এই ডিফল্ট কনফিগারেশনগুলো আছে:

{* ../../fastapi/openapi/docs.py ln[9:24] hl[18:24] *}

`swagger_ui_parameters` আর্গুমেন্টে একটি ভিন্ন মান সেট করে এগুলোর যেকোনোটি ওভাররাইড করতে পারেন।

যেমন, `deepLinking` বন্ধ করতে `swagger_ui_parameters`-এ এই সেটিংস দিতে পারেন:

{* ../../docs_src/configure_swagger_ui/tutorial003_py310.py hl[3] *}

/// info | ডিফল্ট সেটিংসগুলো সহজ ভাষায়

* `dom_id`: পেজের কোন HTML উপাদানে Swagger UI বসবে।
* `layout`: পেজের বিন্যাস।
* `deepLinking`: চালু থাকলে কোনো এন্ডপয়েন্ট খুললে URL-এ `#...` যোগ হয়, ফলে সেই লিংক অন্যকে পাঠালে সরাসরি সেই এন্ডপয়েন্টে যাওয়া যায়।
* `showExtensions`, `showCommonExtensions`: OpenAPI-র বাড়তি তথ্য (যেমন `x-` দিয়ে শুরু হওয়া ফিল্ড) দেখানো।

///

## অন্যান্য Swagger UI প্যারামিটার { #other-swagger-ui-parameters }

ব্যবহার করা যায় এমন অন্য সব সম্ভাব্য কনফিগারেশন দেখতে, অফিসিয়াল [Swagger UI প্যারামিটারের ডকস](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/) পড়ুন।

## শুধু-JavaScript সেটিংস { #javascript-only-settings }

Swagger UI আরও কিছু কনফিগারেশনকে **শুধু-JavaScript** অবজেক্ট (যেমন JavaScript ফাংশন) হিসেবে রাখার সুযোগ দেয়।

FastAPI-তে এই শুধু-JavaScript `presets` সেটিংসও আছে:

⟦CODE1⟧

এগুলো **JavaScript** অবজেক্ট, স্ট্রিং নয়, তাই আপনি এগুলো সরাসরি Python কোড থেকে দিতে পারবেন না।

যদি এমন শুধু-JavaScript কনফিগারেশন ব্যবহার করতে হয়, তাহলে ওপরের কোনো একটি পদ্ধতি ব্যবহার করতে পারেন। পুরো Swagger UI *পাথ অপারেশন* ওভাররাইড করে যা JavaScript দরকার তা নিজে হাতে লিখুন। (দেখুন [কাস্টম ডকস UI স্ট্যাটিক অ্যাসেট](custom-docs-ui-assets.md)।)

/// check | সংক্ষেপে মনে রাখুন

* `FastAPI(swagger_ui_parameters={...})` দিয়ে Swagger UI-র সেটিংস দিন।
* `{"syntaxHighlight": False}` হাইলাইটিং বন্ধ করে, `{"syntaxHighlight": {"theme": "obsidian"}}` থিম বদলায়।
* JavaScript ফাংশনের মতো জিনিস Python থেকে দেওয়া যায় না, তখন নিজের `/docs` রাউট বানাতে হয়।

///
