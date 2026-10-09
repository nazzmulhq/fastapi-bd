# Swagger UI কনফিগার করুন { #configure-swagger-ui }

আপনি কিছু অতিরিক্ত [Swagger UI প্যারামিটার](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/) কনফিগার করতে পারেন।

সেগুলো কনফিগার করতে `FastAPI()` অ্যাপ অবজেক্ট তৈরির সময় বা `get_swagger_ui_html()` ফাংশনে `swagger_ui_parameters` আর্গুমেন্ট দিন।

`swagger_ui_parameters` সরাসরি Swagger UI-তে পাঠানো কনফিগারেশনসহ একটি ডিকশনারি গ্রহণ করে।

JavaScript-এর সাথে সামঞ্জস্যপূর্ণ করতে FastAPI কনফিগারেশনগুলো **JSON**-এ রূপান্তর করে, কারণ Swagger UI-এর এটাই দরকার।

## সিনট্যাক্স হাইলাইটিং বন্ধ করুন { #disable-syntax-highlighting }

যেমন, আপনি Swagger UI-তে সিনট্যাক্স হাইলাইটিং বন্ধ করতে পারেন।

সেটিংস না বদলালে ডিফল্টভাবে সিনট্যাক্স হাইলাইটিং চালু থাকে:

<img src="/img/tutorial/extending-openapi/image02.png">

কিন্তু `syntaxHighlight`-কে `False` সেট করে আপনি এটি বন্ধ করতে পারেন:

{* ../../docs_src/configure_swagger_ui/tutorial001_py310.py hl[3] *}

...আর তখন Swagger UI আর সিনট্যাক্স হাইলাইটিং দেখাবে না:

<img src="/img/tutorial/extending-openapi/image03.png">

## থিম বদলান { #change-the-theme }

একইভাবে আপনি `"syntaxHighlight.theme"` কী দিয়ে সিনট্যাক্স হাইলাইটিং থিম সেট করতে পারেন (লক্ষ করুন, এর মাঝখানে একটি ডট আছে):

{* ../../docs_src/configure_swagger_ui/tutorial002_py310.py hl[3] *}

ওই কনফিগারেশন সিনট্যাক্স হাইলাইটিংয়ের রঙের থিম বদলে দেবে:

<img src="/img/tutorial/extending-openapi/image04.png">

## ডিফল্ট Swagger UI প্যারামিটার বদলান { #change-default-swagger-ui-parameters }

FastAPI-তে বেশিরভাগ ব্যবহারের ক্ষেত্রের জন্য উপযুক্ত কিছু ডিফল্ট কনফিগারেশন প্যারামিটার অন্তর্ভুক্ত আছে।

এতে এই ডিফল্ট কনফিগারেশনগুলো আছে:

{* ../../fastapi/openapi/docs.py ln[9:24] hl[18:24] *}

`swagger_ui_parameters` আর্গুমেন্টে একটি ভিন্ন ভ্যালু সেট করে আপনি এগুলোর যেকোনোটি ওভাররাইড করতে পারেন।

যেমন, `deepLinking` বন্ধ করতে আপনি `swagger_ui_parameters`-এ এই সেটিংসগুলো দিতে পারেন:

{* ../../docs_src/configure_swagger_ui/tutorial003_py310.py hl[3] *}

## অন্যান্য Swagger UI প্যারামিটার { #other-swagger-ui-parameters }

আপনি ব্যবহার করতে পারেন এমন অন্য সব সম্ভাব্য কনফিগারেশন দেখতে অফিসিয়াল [Swagger UI প্যারামিটারের ডকুমেন্টেশন](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/) পড়ুন।

## কেবল-JavaScript সেটিংস { #javascript-only-settings }

Swagger UI আরও কিছু কনফিগারেশনকে **কেবল-JavaScript** অবজেক্ট (যেমন JavaScript ফাংশন) হতে দেয়।

FastAPI-তে এই কেবল-JavaScript `presets` সেটিংসগুলোও অন্তর্ভুক্ত আছে:

⟦CODE1⟧

এগুলো **JavaScript** অবজেক্ট, স্ট্রিং নয়, তাই আপনি এগুলো সরাসরি Python কোড থেকে দিতে পারবেন না।

আপনার যদি এরকম কেবল-JavaScript কনফিগারেশন ব্যবহার করতে হয়, তাহলে ওপরের পদ্ধতিগুলোর একটি ব্যবহার করতে পারেন। পুরো Swagger UI *পাথ অপারেশন* ওভাররাইড করে নিজে হাতে আপনার প্রয়োজনীয় যেকোনো JavaScript লিখুন।
