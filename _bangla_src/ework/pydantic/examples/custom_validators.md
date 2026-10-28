# নিজের Validator { #custom-validators }

/// note | এই পেজে যা শিখবেন

* `Annotated` metadata আর `__get_pydantic_core_schema__` দিয়ে বারবার ব্যবহারযোগ্য নিজের validator (timezone আর UTC offset যাচাই)।
* নেস্টেড মডেলের ফিল্ড অভিভাবক মডেলের ডেটা দিয়ে যাচাইয়ের দুটি উপায়: বাইরের মডেলে `model_validator`, আর validation context।
* এররের বার্তা ভালো করে লেখা কেন জরুরি।

///

এই পেজে Pydantic-এ আরও জটিল, নিজের বানানো validator তৈরির কিছু উদাহরণ কোড দেওয়া হলো।
এর অনেকগুলো উদাহরণ Pydantic-এর issue আর আলোচনা থেকে নেওয়া, আর এগুলোর উদ্দেশ্য Pydantic-এর
যাচাই ব্যবস্থার নমনীয়তা আর ক্ষমতা দেখানো।

/// tip | আগে যা জানা দরকার

validator-এর মূল ধারণা (*before*, *after*, *wrap*) না জানলে আগে [Validators](../concepts/validators.md) পেজটি পড়ে নিন। এখানের উদাহরণগুলো তার ওপরে দাঁড়ানো।

///

## [`Annotated`][typing.Annotated] metadata দিয়ে নিজের `datetime` validator { #custom-datetime-validator-via-annotated-metadata }

এই উদাহরণে, আমরা একটি [`Annotated`][typing.Annotated] টাইপের সাথে যুক্ত একটি নিজের validator তৈরি করব,
যা নিশ্চিত করে একটি [`datetime`][datetime.datetime] অবজেক্ট একটি নির্দিষ্ট timezone শর্ত মানে।

নিজের validator-টি স্ট্রিং দিয়ে timezone উল্লেখ সমর্থন করে, আর [`datetime`][datetime.datetime] অবজেক্টের timezone সঠিক না হলে এরর তুলবে।

validator-এ আমরা `__get_pydantic_core_schema__` ব্যবহার করি annotation দেওয়া টাইপের (এক্ষেত্রে [`datetime`][datetime.datetime]) schema নিজের মতো করতে, যা দিয়ে নিজের যাচাইয়ের যুক্তি যোগ করা যায়। উল্লেখযোগ্যভাবে, আমরা একটি `wrap` validator ফাংশন ব্যবহার করি, যাতে একটি [`datetime`][datetime.datetime]-এর ডিফল্ট `pydantic` যাচাইয়ের আগে আর পরে দুই সময়েই কাজ করা যায়।

⟦CODE1⟧

1. `handler` ফাংশনটি ডেকেই আমরা সাধারণ `pydantic` যাচাই দিয়ে ইনপুট যাচাই করি
2. এই wrap validator-এ সাধারণ `pydantic` যাচাই দিয়ে ইনপুট যাচাই করতে আমরা `handler` ফাংশন ডাকি

/// info | কোডটি সহজ ভাষায়

* `MyDatetimeValidator(LA)` একটি "লেবেল" যা `Annotated[dt.datetime, ...]`-এ লাগানো হয়েছে। Pydantic টাইপটি দেখার সময় লেবেলের `__get_pydantic_core_schema__` ডাকে।
* সেখানে `no_info_wrap_validator_function` বলে: "`datetime`-এর স্বাভাবিক যাচাইকে (`handler(source_type)`) আমার `tz_constraint_validator` দিয়ে মুড়ে দাও"।
* validator-এর ভেতরে আগে `handler(value)` দিয়ে আসল `datetime` পাওয়া যায়, তারপর তার `tzinfo` মিলিয়ে দেখা হয়।
* `assert` ব্যর্থ হলে Pydantic সেটিকে `assertion_error` ধরনের যাচাই এরর বানায়।

///

একইভাবে আমরা UTC offset-এর শর্তও চাপাতে পারি। ধরে নিচ্ছি আমাদের একটি `lower_bound` আর একটি `upper_bound` আছে; আমরা একটি নিজের validator তৈরি করতে পারি যা নিশ্চিত করে আমাদের `datetime`-এর UTC offset আমাদের নির্ধারিত সীমার ভেতরে (সীমাসহ):

⟦CODE2⟧

/// tip | উদাহরণ দিয়ে বুঝি

`MyDatetimeValidator(-10, -5)` মানে "সময়টি UTC থেকে ৫ থেকে ১০ ঘণ্টা পিছিয়ে থাকা কোনো অঞ্চলের হতে হবে" (যেমন আমেরিকা)। লন্ডনের সময় (offset প্রায় ০) এই সীমার বাইরে, তাই এরর। বাংলাদেশের সময় (`+06:00`) পরীক্ষা করতে চাইলে `MyDatetimeValidator(6, 6)` লিখতেন।

///

## নেস্টেড মডেলের ফিল্ড যাচাই { #validating-nested-model-fields }

এখানে, একটি নেস্টেড মডেলের ফিল্ড যাচাইয়ের দুটি উপায় দেখাব, যেখানে validator অভিভাবক মডেলের ডেটা ব্যবহার করে।

এই উদাহরণে, আমরা একটি validator তৈরি করি যা পরীক্ষা করে প্রতিটি ব্যবহারকারীর পাসওয়ার্ড অভিভাবক মডেলে দেওয়া নিষিদ্ধ পাসওয়ার্ডের তালিকায় নেই।

এটি করার একটি উপায় হলো বাইরের মডেলে একটি নিজের validator বসানো:

⟦CODE3⟧

বিকল্প হিসেবে, নেস্টেড মডেল ক্লাসে (`User`) একটি নিজের validator ব্যবহার করা যায়, যেখানে অভিভাবক মডেলের নিষিদ্ধ পাসওয়ার্ডের ডেটা
[validation context](../concepts/validators.md#validation-context) দিয়ে পাঠানো হয়।

/// warning | সতর্কতা

validator-এর ভেতরে context বদলানোর ক্ষমতা নেস্টেড যাচাইয়ে অনেক শক্তি যোগ করে, কিন্তু বিভ্রান্তিকর বা ডিবাগ করা কঠিন কোডের দিকেও নিয়ে যেতে পারে। নিজের দায়িত্বে এই পদ্ধতি ব্যবহার করুন!

///

⟦CODE4⟧

/// info | কোডটি সহজ ভাষায়

* ফিল্ড যাচাই হয় সংজ্ঞার ক্রমে: আগে `forbidden_passwords`, তারপর `users`।
* `add_context` `forbidden_passwords` যাচাইয়ের পরে তালিকাটি context ডিকশনারিতে রেখে দেয়।
* পরে প্রতিটি `User`-এর `password` যাচাইয়ের সময় সেই context থেকে তালিকা পড়া হয়।
* দুই উপায়ের পার্থক্য এররের অবস্থানে: প্রথমটিতে এরর পুরো `Organization`-এ (`loc` খালি), দ্বিতীয়টিতে ঠিক `users.0.password`-এ, যা ব্যবহারকারীকে দেখাতে বেশি কাজের।

///

মনে রাখুন, [`model_validate()`][pydantic.main.BaseModel.model_validate]-এ context property না দিলে, [`context`][pydantic.ValidationInfo.context] হবে `None`,
আর ওপরের বাস্তবায়নে নিষিদ্ধ পাসওয়ার্ডের তালিকা context-এ যোগ হবে না। ফলে `validate_user_passwords()` কাঙ্ক্ষিত পাসওয়ার্ড যাচাই করবে না।

/// warning | সাধারণ ভুল

`Organization(**data)` দিয়ে সরাসরি তৈরি করলে context দেওয়া যায় না, তাই দ্বিতীয় উপায়ে নিষিদ্ধ পাসওয়ার্ড চুপচাপ পার হয়ে যাবে। সবসময় `Organization.model_validate(data, context={})` ব্যবহার করুন।

///

validation context নিয়ে আরও বিস্তারিত পাওয়া যাবে [validators ডকুমেন্টেশনে](../concepts/validators.md#validation-context)।

এই `raise ValueError(...)` ডাকগুলোতে লেখা বার্তা যত্ন করে লেখা উচিত: নিয়মটি যখন একদিন আসল ডেটা প্রত্যাখ্যান করবে,
তখন আপনি এগুলোই পড়বেন। এগুলো গোছানো এরর ব্যবহার করা টুলেও পৌঁছায়: যেমন
[Logfire-এর ব্যর্থ যাচাইয়ের ব্যাখ্যায়](../errors/troubleshooting.md) আপনার নিজের validator-এর বার্তাগুলো থাকে।

/// check | সংক্ষেপে মনে রাখুন

* বারবার ব্যবহারযোগ্য validator: একটি ক্লাসে `__get_pydantic_core_schema__` লিখে `Annotated[টাইপ, MyValidator(...)]`।
* wrap validator-এ `handler(value)` ডেকে আগে স্বাভাবিক যাচাই, তারপর নিজের পরীক্ষা।
* অভিভাবকের ডেটা দিয়ে নেস্টেড যাচাই: বাইরের মডেলে `model_validator(mode='after')`, অথবা context দিয়ে (`model_validate(..., context={})`)।
* এররের বার্তা পরিষ্কার লিখুন; এটিই পরে ডিবাগে আপনার সবচেয়ে বড় সাহায্য।

///
