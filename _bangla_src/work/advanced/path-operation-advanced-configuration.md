# পাথ অপারেশনের অ্যাডভান্সড কনফিগারেশন { #path-operation-advanced-configuration }

## OpenAPI operationId { #openapi-operationid }

/// warning | সতর্কতা

আপনি যদি OpenAPI-এর "বিশেষজ্ঞ" না হন, তাহলে সম্ভবত এটি আপনার দরকার নেই।

///

`operation_id` প্যারামিটার দিয়ে আপনি আপনার *পাথ অপারেশনে* ব্যবহৃত OpenAPI `operationId` সেট করতে পারেন।

আপনাকে নিশ্চিত করতে হবে যে এটি প্রতিটি অপারেশনের জন্য অনন্য।

{* ../../docs_src/path_operation_advanced_configuration/tutorial001_py310.py hl[6] *}

### *পাথ অপারেশন ফাংশনের* নামকে operationId হিসেবে ব্যবহার { #using-the-path-operation-function-name-as-the-operationid }

আপনি যদি আপনার API-এর ফাংশনের নামগুলোকে `operationId` হিসেবে ব্যবহার করতে চান, তাহলে `FastAPI`-তে একটি কাস্টম `generate_unique_id_function` দিতে পারেন।

ফাংশনটি প্রতিটি `APIRoute` পায় এবং ওই পাথ অপারেশনের জন্য ব্যবহারযোগ্য `operationId` রিটার্ন করে।

{* ../../docs_src/path_operation_advanced_configuration/tutorial002_py310.py hl[2,5:6,9] *}

/// warning | সতর্কতা

আপনি এটি করলে আপনাকে নিশ্চিত করতে হবে যে আপনার প্রতিটি *পাথ অপারেশন ফাংশনের* নাম অনন্য।

এমনকি সেগুলো ভিন্ন ভিন্ন মডিউলে (Python ফাইলে) থাকলেও।

///

## OpenAPI থেকে বাদ দিন { #exclude-from-openapi }

তৈরি হওয়া OpenAPI স্কিমা থেকে (এবং ফলে স্বয়ংক্রিয় ডকুমেন্টেশন সিস্টেম থেকে) একটি *পাথ অপারেশন* বাদ দিতে `include_in_schema` প্যারামিটার ব্যবহার করে এটি `False` সেট করুন:

{* ../../docs_src/path_operation_advanced_configuration/tutorial003_py310.py hl[6] *}

## docstring থেকে অ্যাডভান্সড বিবরণ { #advanced-description-from-docstring }

OpenAPI-এর জন্য একটি *পাথ অপারেশন ফাংশনের* docstring থেকে কোন লাইনগুলো ব্যবহার হবে তা আপনি সীমিত করতে পারেন।

একটি `\f` (একটি এস্কেপ করা "form feed" অক্ষর) যোগ করলে **FastAPI** OpenAPI-এর জন্য ব্যবহৃত আউটপুট এই জায়গাতেই কেটে দেয়।

এটি ডকুমেন্টেশনে দেখা যাবে না, তবে অন্যান্য টুল (যেমন Sphinx) বাকি অংশটুকু ব্যবহার করতে পারবে।

{* ../../docs_src/path_operation_advanced_configuration/tutorial004_py310.py hl[17:27] *}

## অতিরিক্ত রেসপন্স { #additional-responses }

আপনি সম্ভবত দেখেছেন কীভাবে একটি *পাথ অপারেশনের* জন্য `response_model` ও `status_code` ঘোষণা করতে হয়।

এগুলো একটি *পাথ অপারেশনের* প্রধান রেসপন্স সম্পর্কিত মেটাডেটা সংজ্ঞায়িত করে।

আপনি তাদের মডেল, স্ট্যাটাস কোড ইত্যাদিসহ অতিরিক্ত রেসপন্সও ঘোষণা করতে পারেন।

এখানে ডকুমেন্টেশনে এ নিয়ে একটি পুরো অধ্যায় আছে, তা পড়তে পারেন [OpenAPI-তে অতিরিক্ত রেসপন্স](additional-responses.md)-এ।

## OpenAPI Extra { #openapi-extra }

আপনি যখন আপনার অ্যাপ্লিকেশনে একটি *পাথ অপারেশন* ঘোষণা করেন, তখন **FastAPI** স্বয়ংক্রিয়ভাবে ওই *পাথ অপারেশন* সম্পর্কিত প্রাসঙ্গিক মেটাডেটা তৈরি করে, যা OpenAPI স্কিমায় অন্তর্ভুক্ত হয়।

/// note | কারিগরি বিবরণ

OpenAPI স্পেসিফিকেশনে একে বলা হয় [Operation Object](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#operation-object)।

///

এতে *পাথ অপারেশন* সম্পর্কে সব তথ্য থাকে এবং এটি স্বয়ংক্রিয় ডকুমেন্টেশন তৈরিতে ব্যবহার হয়।

এতে থাকে `tags`, `parameters`, `requestBody`, `responses` ইত্যাদি।

*পাথ অপারেশন*-নির্দিষ্ট এই OpenAPI স্কিমা সাধারণত **FastAPI** স্বয়ংক্রিয়ভাবে তৈরি করে, তবে আপনি এটি বাড়াতেও পারেন।

/// tip | পরামর্শ

এটি একটি নিম্ন-স্তরের সম্প্রসারণ বিন্দু।

আপনার যদি কেবল অতিরিক্ত রেসপন্স ঘোষণা করতে হয়, তাহলে এটি করার আরও সুবিধাজনক উপায় হলো [OpenAPI-তে অতিরিক্ত রেসপন্স](additional-responses.md)।

///

`openapi_extra` প্যারামিটার ব্যবহার করে আপনি একটি *পাথ অপারেশনের* OpenAPI স্কিমা বাড়াতে পারেন।

### OpenAPI এক্সটেনশন { #openapi-extensions }

এই `openapi_extra` কাজে আসতে পারে, যেমন, [OpenAPI এক্সটেনশন](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#specificationExtensions) ঘোষণা করতে:

{* ../../docs_src/path_operation_advanced_configuration/tutorial005_py310.py hl[6] *}

আপনি যদি স্বয়ংক্রিয় API ডকুমেন্টেশন খোলেন, তাহলে আপনার এক্সটেনশনটি নির্দিষ্ট *পাথ অপারেশনের* নিচে দেখা যাবে।

<img src="/img/tutorial/path-operation-advanced-configuration/image01.png">

আর আপনি যদি ফলাফলস্বরূপ OpenAPI দেখেন (আপনার API-এর `/openapi.json`-এ), তাহলে আপনার এক্সটেনশনটিকে নির্দিষ্ট *পাথ অপারেশনের* অংশ হিসেবেও দেখতে পাবেন:

⟦CODE1⟧

### কাস্টম OpenAPI *পাথ অপারেশন* স্কিমা { #custom-openapi-path-operation-schema }

`openapi_extra`-এর ডিকশনারিটি *পাথ অপারেশনের* জন্য স্বয়ংক্রিয়ভাবে তৈরি হওয়া OpenAPI স্কিমার সাথে গভীরভাবে মিলিত (merge) হবে।

তাই আপনি স্বয়ংক্রিয়ভাবে তৈরি হওয়া স্কিমায় অতিরিক্ত ডেটা যোগ করতে পারেন।

যেমন, আপনি হয়তো ঠিক করলেন Pydantic-সহ FastAPI-এর স্বয়ংক্রিয় ফিচারগুলো ব্যবহার না করে নিজের কোড দিয়ে রিকোয়েস্ট পড়বেন ও ভ্যালিডেট করবেন, কিন্তু তবুও OpenAPI স্কিমায় রিকোয়েস্টটি সংজ্ঞায়িত করতে চান।

আপনি এটি `openapi_extra` দিয়ে করতে পারেন:

{* ../../docs_src/path_operation_advanced_configuration/tutorial006_py310.py hl[19:36, 39:40] *}

এই উদাহরণে আমরা কোনো Pydantic মডেল ঘোষণা করিনি। আসলে রিকোয়েস্ট বডি JSON হিসেবে <dfn title="bytes-এর মতো কোনো সাধারণ ফরম্যাট থেকে Python অবজেক্টে রূপান্তরিত">পার্স</dfn>-ও করা হয় না, এটি সরাসরি `bytes` হিসেবে পড়া হয়, আর `magic_data_reader()` ফাংশনটি কোনোভাবে এটি পার্স করার দায়িত্বে থাকবে।

তবুও আমরা রিকোয়েস্ট বডির প্রত্যাশিত স্কিমা ঘোষণা করতে পারি।

### কাস্টম OpenAPI কনটেন্ট টাইপ { #custom-openapi-content-type }

এই একই কৌশল ব্যবহার করে আপনি একটি Pydantic মডেল দিয়ে JSON Schema সংজ্ঞায়িত করতে পারেন, যা তারপর *পাথ অপারেশনের* কাস্টম OpenAPI স্কিমা অংশে অন্তর্ভুক্ত হয়।

আর রিকোয়েস্টের ডেটা টাইপ JSON না হলেও আপনি এটি করতে পারেন।

যেমন, এই অ্যাপ্লিকেশনে আমরা Pydantic মডেল থেকে JSON Schema বের করার জন্য FastAPI-এর অন্তর্ভুক্ত কার্যকারিতা বা JSON-এর জন্য স্বয়ংক্রিয় ভ্যালিডেশন ব্যবহার করি না। আসলে আমরা রিকোয়েস্টের কনটেন্ট টাইপ YAML হিসেবে ঘোষণা করছি, JSON নয়:

{* ../../docs_src/path_operation_advanced_configuration/tutorial007_py310.py hl[15:20, 22] *}

তবুও, যদিও আমরা ডিফল্ট অন্তর্ভুক্ত কার্যকারিতা ব্যবহার করছি না, YAML-এ যে ডেটা গ্রহণ করতে চাই তার JSON Schema নিজে হাতে তৈরি করতে আমরা তবুও একটি Pydantic মডেল ব্যবহার করছি।

তারপর আমরা সরাসরি রিকোয়েস্টটি ব্যবহার করি, এবং বডি `bytes` হিসেবে বের করি। এর মানে FastAPI রিকোয়েস্ট পেলোড JSON হিসেবে পার্স করার চেষ্টাও করবে না।

আর তারপর আমাদের কোডে আমরা সেই YAML কনটেন্ট সরাসরি পার্স করি, এবং তারপর YAML কনটেন্ট ভ্যালিডেট করতে আবার একই Pydantic মডেল ব্যবহার করি:

{* ../../docs_src/path_operation_advanced_configuration/tutorial007_py310.py hl[24:31] *}

/// tip | পরামর্শ

এখানে আমরা একই Pydantic মডেল পুনরায় ব্যবহার করছি।

তবে একইভাবে আমরা অন্য কোনো উপায়েও এটি ভ্যালিডেট করতে পারতাম।

///
