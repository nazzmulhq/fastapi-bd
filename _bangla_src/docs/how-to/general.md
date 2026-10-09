# সাধারণ - কীভাবে করবেন - রেসিপি { #general-how-to-recipes }

/// note | এই পেজটি কী

এটি একটি "কোথায় পাবেন" তালিকা। প্রায়ই জিজ্ঞাসিত প্রশ্নগুলোর উত্তর ডকসের কোন পেজে আছে, তা এখানে এক জায়গায় দেওয়া হলো। প্রতিটি শিরোনামের নিচে এক লাইনে বলা আছে কী শিখবেন আর লিংকে ক্লিক করলে সেই পেজে যাবেন।

///

সাধারণ বা প্রায়ই জিজ্ঞাসিত প্রশ্নের জন্য ডকসের অন্যান্য জায়গার কয়েকটি নির্দেশিকা এখানে দেওয়া হলো।

## ডেটা ফিল্টার করা - নিরাপত্তা { #filter-data-security }

যতটা ফেরত দেওয়া উচিত তার চেয়ে বেশি ডেটা যেন ফেরত না দেন (যেমন ইউজারের পাসওয়ার্ড), তা নিশ্চিত করতে [টিউটোরিয়াল - রেসপন্স মডেল - রিটার্ন টাইপ](../tutorial/response-model.md)-এর ডকস পড়ুন।

## রেসপন্সের পারফরম্যান্স বাড়ানো - রেসপন্স মডেল - রিটার্ন টাইপ { #optimize-response-performance-response-model-return-type }

JSON ডেটা ফেরত দেওয়ার সময় পারফরম্যান্স বাড়াতে একটি রিটার্ন টাইপ বা রেসপন্স মডেল ব্যবহার করুন, এতে Pydantic Python-এর মধ্য দিয়ে না গিয়ে Rust-এর দিকেই JSON-এ সিরিয়ালাইজেশন সামলাবে (যা অনেক দ্রুত)। আরও পড়ুন [টিউটোরিয়াল - রেসপন্স মডেল - রিটার্ন টাইপ](../tutorial/response-model.md)-এর ডকসে।

## ডকুমেন্টেশন ট্যাগ - OpenAPI { #documentation-tags-openapi }

আপনার *পাথ অপারেশনে* ট্যাগ যোগ করতে, আর ডকস UI-তে সেগুলো গ্রুপ করতে, [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - Tags](../tutorial/path-operation-configuration.md#tags)-এর ডকস পড়ুন।

## ডকুমেন্টেশনের সারসংক্ষেপ এবং বর্ণনা - OpenAPI { #documentation-summary-and-description-openapi }

আপনার *পাথ অপারেশনে* একটি সারসংক্ষেপ (summary) আর বর্ণনা (description) যোগ করতে, আর ডকস UI-তে দেখাতে, [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - Summary এবং Description](../tutorial/path-operation-configuration.md#summary-and-description)-এর ডকস পড়ুন।

## ডকুমেন্টেশনে রেসপন্সের বর্ণনা - OpenAPI { #documentation-response-description-openapi }

ডকস UI-তে দেখানো রেসপন্সের বর্ণনা নির্ধারণ করতে, [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - Response description](../tutorial/path-operation-configuration.md#response-description)-এর ডকস পড়ুন।

## ডকুমেন্টেশনে একটি *পাথ অপারেশন* পুরনো (deprecated) চিহ্নিত করা - OpenAPI { #documentation-deprecate-a-path-operation-openapi }

একটি *পাথ অপারেশনকে* পুরনো (deprecated) চিহ্নিত করতে, আর ডকস UI-তে তা দেখাতে, [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - Deprecation](../tutorial/path-operation-configuration.md#deprecate-a-path-operation)-এর ডকস পড়ুন।

## যেকোনো ডেটাকে JSON-উপযোগী করা { #convert-any-data-to-json-compatible }

যেকোনো ডেটাকে (যেমন `datetime` বা Pydantic মডেল) JSON-উপযোগী করতে, [টিউটোরিয়াল - JSON উপযোগী এনকোডার](../tutorial/encoder.md)-এর ডকস পড়ুন।

## OpenAPI মেটাডেটা - ডকস { #openapi-metadata-docs }

আপনার OpenAPI স্কিমায় লাইসেন্স, সংস্করণ, যোগাযোগ ইত্যাদিসহ মেটাডেটা যোগ করতে, [টিউটোরিয়াল - মেটাডেটা এবং ডকস URL](../tutorial/metadata.md)-এর ডকস পড়ুন।

## OpenAPI কাস্টম URL { #openapi-custom-url }

OpenAPI URL নিজের মতো করতে (বা সরিয়ে দিতে), [টিউটোরিয়াল - মেটাডেটা এবং ডকস URL](../tutorial/metadata.md#openapi-url)-এর ডকস পড়ুন।

## OpenAPI ডকস URL { #openapi-docs-urls }

স্বয়ংক্রিয়ভাবে তৈরি ডকস ইউজার ইন্টারফেসের (`/docs`, `/redoc`) URL বদলাতে, [টিউটোরিয়াল - মেটাডেটা এবং ডকস URL](../tutorial/metadata.md#docs-urls)-এর ডকস পড়ুন।

/// check | সংক্ষেপে মনে রাখুন

* কোনো প্রশ্নের উত্তর খুঁজতে আগে এই তালিকাটি দেখুন, সম্ভবত টিউটোরিয়ালেই উত্তর আছে।
* বেশি ডেটা ফাঁস ঠেকাতে আর দ্রুততার জন্য: রেসপন্স মডেল। ডকস সাজাতে: পাথ অপারেশন কনফিগারেশন আর মেটাডেটা।

///
