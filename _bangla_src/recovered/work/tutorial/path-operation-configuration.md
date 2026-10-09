# পাথ অপারেশন কনফিগারেশন { #path-operation-configuration }

আপনার *পাথ অপারেশন ডেকোরেটরকে* কনফিগার করতে এতে বেশ কয়েকটি প্যারামিটার দিতে পারেন।

/// warning | সতর্কতা

লক্ষ করুন, এই প্যারামিটারগুলো সরাসরি *পাথ অপারেশন ডেকোরেটরে* দেওয়া হয়, আপনার *পাথ অপারেশন ফাংশনে* নয়।

///

## রেসপন্স স্ট্যাটাস কোড { #response-status-code }

আপনার *পাথ অপারেশনের* রেসপন্সে ব্যবহারের জন্য আপনি (HTTP) `status_code` সংজ্ঞায়িত করতে পারেন।

আপনি সরাসরি `int` কোড দিতে পারেন, যেমন `404`।

কিন্তু কোন সংখ্যার কোড কীসের জন্য তা মনে না থাকলে `status`-এর শর্টকাট কনস্ট্যান্টগুলো ব্যবহার করতে পারেন:

{* ../../docs_src/path_operation_configuration/tutorial001_py310.py hl[1,15] *}

ওই স্ট্যাটাস কোডটি রেসপন্সে ব্যবহার হবে এবং OpenAPI স্কিমায় যোগ হবে।

/// note | কারিগরি বিবরণ

আপনি `from starlette import status`-ও ব্যবহার করতে পারতেন।

**FastAPI** শুধু আপনার, অর্থাৎ ডেভেলপারের সুবিধার জন্য একই `starlette.status`-কে `fastapi.status` হিসেবে দেয়। তবে এটি সরাসরি Starlette থেকে আসে।

///

## ট্যাগ { #tags }

আপনি আপনার *পাথ অপারেশনে* ট্যাগ যোগ করতে পারেন, `str`-এর একটি `list` (সাধারণত শুধু একটি `str`) দিয়ে `tags` প্যারামিটার দিন:

{* ../../docs_src/path_operation_configuration/tutorial002_py310.py hl[15,20,25] *}

এগুলো OpenAPI স্কিমায় যোগ হবে এবং স্বয়ংক্রিয় ডকুমেন্টেশন ইন্টারফেসগুলো এগুলো ব্যবহার করবে:

<img src="/img/tutorial/path-operation-configuration/image01.png">

### Enum দিয়ে ট্যাগ { #tags-with-enums }

আপনার যদি একটি বড় অ্যাপ্লিকেশন থাকে, তাহলে শেষ পর্যন্ত আপনার **অনেক ট্যাগ** জমে যেতে পারে, আর আপনি নিশ্চিত করতে চাইবেন যে সম্পর্কিত *পাথ অপারেশনগুলোর* জন্য সবসময় **একই ট্যাগ** ব্যবহার করছেন।

এসব ক্ষেত্রে ট্যাগগুলো একটি `Enum`-এ সংরক্ষণ করা যুক্তিসঙ্গত হতে পারে।

**FastAPI** সাধারণ স্ট্রিংয়ের মতোই এটি সাপোর্ট করে:

{* ../../docs_src/path_operation_configuration/tutorial002b_py310.py hl[1,8:10,13,18] *}

## সারাংশ ও বিবরণ { #summary-and-description }

আপনি একটি `summary` ও `description` যোগ করতে পারেন:

{* ../../docs_src/path_operation_configuration/tutorial003_py310.py hl[17:18] *}

## docstring থেকে বিবরণ { #description-from-docstring }

যেহেতু বিবরণ সাধারণত লম্বা হয় এবং একাধিক লাইন জুড়ে থাকে, তাই আপনি ফাংশনের <dfn title="ডকুমেন্টেশনের জন্য ব্যবহৃত, ফাংশনের ভেতরে প্রথম এক্সপ্রেশন হিসেবে থাকা একটি বহু-লাইনের স্ট্রিং (কোনো ভেরিয়েবলে অ্যাসাইন করা নয়)">docstring</dfn>-এ *পাথ অপারেশনের* বিবরণ ঘোষণা করতে পারেন, আর **FastAPI** সেখান থেকে এটি পড়ে নেবে।

docstring-এ আপনি [Markdown](https://en.wikipedia.org/wiki/Markdown) লিখতে পারেন, এটি সঠিকভাবে ব্যাখ্যা করে দেখানো হবে (docstring-এর ইনডেন্টেশন বিবেচনায় রেখে)।

{* ../../docs_src/path_operation_configuration/tutorial004_py310.py hl[17:25] *}

এটি ইন্টারঅ্যাকটিভ ডকুমেন্টেশনে ব্যবহার হবে:

<img src="/img/tutorial/path-operation-configuration/image02.png">

## রেসপন্সের বিবরণ { #response-description }

`response_description` প্যারামিটার দিয়ে আপনি রেসপন্সের বিবরণ নির্দিষ্ট করতে পারেন:

{* ../../docs_src/path_operation_configuration/tutorial005_py310.py hl[18] *}

/// note | নোট

লক্ষ করুন, `response_description` নির্দিষ্টভাবে রেসপন্সকে বোঝায়, আর `description` সাধারণভাবে *পাথ অপারেশনকে* বোঝায়।

///

/// tip | পরামর্শ

OpenAPI নির্দিষ্ট করে যে প্রতিটি *পাথ অপারেশনের* একটি রেসপন্স বিবরণ প্রয়োজন।

তাই আপনি একটি না দিলে **FastAPI** স্বয়ংক্রিয়ভাবে "Successful response" নামে একটি তৈরি করবে।

///

<img src="/img/tutorial/path-operation-configuration/image03.png">

## একটি *পাথ অপারেশন* ডেপ্রিকেট করুন { #deprecate-a-path-operation }

আপনার যদি একটি *পাথ অপারেশনকে* না সরিয়ে <dfn title="অপ্রচলিত, ব্যবহার না করার পরামর্শ দেওয়া হয়">ডেপ্রিকেটেড</dfn> হিসেবে চিহ্নিত করতে হয়, তাহলে `deprecated` প্যারামিটারটি দিন:

{* ../../docs_src/path_operation_configuration/tutorial006_py310.py hl[16] *}

ইন্টারঅ্যাকটিভ ডকুমেন্টেশনে এটি স্পষ্টভাবে ডেপ্রিকেটেড হিসেবে চিহ্নিত থাকবে:

<img src="/img/tutorial/path-operation-configuration/image04.png">

ডেপ্রিকেটেড ও নন-ডেপ্রিকেটেড *পাথ অপারেশনগুলো* দেখতে কেমন তা দেখুন:

<img src="/img/tutorial/path-operation-configuration/image05.png">

## সংক্ষেপে { #recap }

*পাথ অপারেশন ডেকোরেটরে* প্যারামিটার দিয়ে আপনি সহজেই আপনার *পাথ অপারেশনগুলো* কনফিগার করতে এবং মেটাডেটা যোগ করতে পারেন।
