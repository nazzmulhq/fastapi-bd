# সাধারণ - হাউ-টু - রেসিপি { #general-how-to-recipes }

সাধারণ বা প্রায়ই জিজ্ঞাসিত প্রশ্নের জন্য ডকুমেন্টেশনের অন্যান্য জায়গার কয়েকটি নির্দেশনা এখানে দেওয়া হলো।

## ডেটা ফিল্টার - সিকিউরিটি { #filter-data-security }

যতটুকু রিটার্ন করা উচিত তার বেশি ডেটা যাতে রিটার্ন না করেন তা নিশ্চিত করতে [টিউটোরিয়াল - রেসপন্স মডেল - রিটার্ন টাইপ](../tutorial/response-model.md)-এর ডকুমেন্টেশন পড়ুন।

## রেসপন্স পারফরম্যান্স অপটিমাইজ - রেসপন্স মডেল - রিটার্ন টাইপ { #optimize-response-performance-response-model-return-type }

JSON ডেটা রিটার্ন করার সময় পারফরম্যান্স অপটিমাইজ করতে একটি রিটার্ন টাইপ বা রেসপন্স মডেল ব্যবহার করুন, এভাবে Pydantic Python-এর মধ্য দিয়ে না গিয়ে Rust-এর দিকে JSON-এ সিরিয়ালাইজেশন সামলাবে। আরও পড়ুন [টিউটোরিয়াল - রেসপন্স মডেল - রিটার্ন টাইপ](../tutorial/response-model.md)-এর ডকুমেন্টেশনে।

## ডকুমেন্টেশন ট্যাগ - OpenAPI { #documentation-tags-openapi }

আপনার *পাথ অপারেশনগুলোতে* ট্যাগ যোগ করতে এবং ডকুমেন্টেশন UI-তে সেগুলো দলবদ্ধ করতে [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - ট্যাগ](../tutorial/path-operation-configuration.md#tags)-এর ডকুমেন্টেশন পড়ুন।

## ডকুমেন্টেশন সারাংশ ও বিবরণ - OpenAPI { #documentation-summary-and-description-openapi }

আপনার *পাথ অপারেশনগুলোতে* একটি সারাংশ ও বিবরণ যোগ করতে এবং ডকুমেন্টেশন UI-তে সেগুলো দেখাতে [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - সারাংশ ও বিবরণ](../tutorial/path-operation-configuration.md#summary-and-description)-এর ডকুমেন্টেশন পড়ুন।

## ডকুমেন্টেশনে রেসপন্সের বিবরণ - OpenAPI { #documentation-response-description-openapi }

ডকুমেন্টেশন UI-তে দেখানো রেসপন্সের বিবরণ সংজ্ঞায়িত করতে [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - রেসপন্সের বিবরণ](../tutorial/path-operation-configuration.md#response-description)-এর ডকুমেন্টেশন পড়ুন।

## ডকুমেন্টেশনে একটি *পাথ অপারেশন* ডেপ্রিকেট করা - OpenAPI { #documentation-deprecate-a-path-operation-openapi }

একটি *পাথ অপারেশন* ডেপ্রিকেট করতে এবং ডকুমেন্টেশন UI-তে তা দেখাতে [টিউটোরিয়াল - পাথ অপারেশন কনফিগারেশন - ডেপ্রিকেশন](../tutorial/path-operation-configuration.md#deprecate-a-path-operation)-এর ডকুমেন্টেশন পড়ুন।

## যেকোনো ডেটাকে JSON-সামঞ্জস্যপূর্ণ করুন { #convert-any-data-to-json-compatible }

যেকোনো ডেটাকে JSON-সামঞ্জস্যপূর্ণ করতে [টিউটোরিয়াল - JSON সামঞ্জস্যপূর্ণ এনকোডার](../tutorial/encoder.md)-এর ডকুমেন্টেশন পড়ুন।

## OpenAPI মেটাডেটা - ডকুমেন্টেশন { #openapi-metadata-docs }

লাইসেন্স, ভার্সন, যোগাযোগ ইত্যাদিসহ আপনার OpenAPI স্কিমায় মেটাডেটা যোগ করতে [টিউটোরিয়াল - মেটাডেটা ও ডকুমেন্টেশন URL](../tutorial/metadata.md)-এর ডকুমেন্টেশন পড়ুন।

## OpenAPI কাস্টম URL { #openapi-custom-url }

OpenAPI URL কাস্টমাইজ করতে (বা সরাতে) [টিউটোরিয়াল - মেটাডেটা ও ডকুমেন্টেশন URL](../tutorial/metadata.md#openapi-url)-এর ডকুমেন্টেশন পড়ুন।

## OpenAPI ডকুমেন্টেশন URL { #openapi-docs-urls }

স্বয়ংক্রিয়ভাবে তৈরি হওয়া ডকুমেন্টেশন ইউজার ইন্টারফেসের জন্য ব্যবহৃত URL আপডেট করতে [টিউটোরিয়াল - মেটাডেটা ও ডকুমেন্টেশন URL](../tutorial/metadata.md#docs-urls)-এর ডকুমেন্টেশন পড়ুন।
