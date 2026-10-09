# OpenAPI-তে বাড়তি রেসপন্স { #additional-responses-in-openapi }

/// note | এই পেজে যা শিখবেন

* `responses` প্যারামিটার দিয়ে ডকুমেন্টেশনে বাড়তি রেসপন্স (যেমন 404) দেখানো।
* একই রেসপন্সের জন্য একাধিক মিডিয়া টাইপ (JSON অথবা ছবি) ঘোষণা করা।
* আগে থেকে তৈরি সাধারণ রেসপন্সগুলো অনেক পাথ অপারেশনে পুনরায় ব্যবহার করা।

///

/// warning | সতর্কতা

এটি বেশ উন্নত একটি বিষয়।

আপনি যদি সবে **FastAPI** শুরু করে থাকেন, তাহলে হয়তো এটি আপনার দরকার নেই।

///

বাড়তি স্ট্যাটাস কোড, মিডিয়া টাইপ, বিবরণ ইত্যাদিসহ বাড়তি রেসপন্স ঘোষণা করতে পারেন।

ওই বাড়তি রেসপন্সগুলো OpenAPI স্কিমাতে অন্তর্ভুক্ত হবে, তাই API ডকুমেন্টেশনেও দেখা যাবে।

কিন্তু ওই বাড়তি রেসপন্সগুলোর জন্য আপনাকে নিশ্চিত করতে হবে যে আপনার স্ট্যাটাস কোড আর বিষয়বস্তুসহ সরাসরি `JSONResponse`-এর মতো একটি `Response` ফেরত দিচ্ছেন।

/// tip | কেন দরকার?

FastAPI নিজে থেকে শুধু সফল রেসপন্সটি (যেমন ২০০) আর যাচাই-এরর (৪২২) ডকুমেন্টেশনে দেখায়। কিন্তু আপনার পাথ অপারেশন হয়তো ৪০৪ বা ৪০৩-ও দিতে পারে। এগুলো ডকুমেন্টেশনে দেখালে আপনার API ব্যবহারকারীরা আগে থেকেই জানবে কোন কোন উত্তর আসতে পারে।

///

## `model`-সহ বাড়তি রেসপন্স { #additional-response-with-model }

আপনার *পাথ অপারেশন ডেকোরেটরে* একটি `responses` প্যারামিটার দিতে পারেন।

এটি একটি `dict` নেয়: কী-গুলো হলো প্রতিটি রেসপন্সের স্ট্যাটাস কোড (যেমন `200`), আর মানগুলো প্রতিটির তথ্যসহ অন্য `dict`।

ওই রেসপন্স `dict`-গুলোর প্রতিটিতে `response_model`-এর মতোই একটি Pydantic মডেলসহ `model` কী থাকতে পারে।

**FastAPI** ওই মডেলটি নিয়ে এর JSON Schema তৈরি করবে আর OpenAPI-এর সঠিক জায়গায় অন্তর্ভুক্ত করবে।

যেমন, `404` স্ট্যাটাস কোড আর একটি Pydantic মডেল `Message`-সহ আরেকটি রেসপন্স ঘোষণা করতে লিখতে পারেন:

{* ../../docs_src/additional_responses/tutorial001_py310.py hl[18,22] *}

/// info | কোডটি সহজ ভাষায়

* লাইন ১৮: `responses={404: {"model": Message}}` বলছে "এই পাথ ৪০৪-ও দিতে পারে, আর তখন বডির আকার হবে `Message` মডেলের মতো"।
* লাইন ২০-২১: আইটেম পাওয়া গেলে সাধারণ ডেটা ফেরত (২০০)।
* লাইন ২২: না পেলে সরাসরি `JSONResponse(status_code=404, ...)` ফেরত। এটা আপনাকেই করতে হবে, `responses` শুধু ডকুমেন্টেশনের জন্য।

///

/// note | নোট

মনে রাখবেন, আপনাকে সরাসরি `JSONResponse` ফেরত দিতে হবে।

///

/// note | নোট

`model` কী OpenAPI-এর অংশ নয়।

**FastAPI** সেখান থেকে Pydantic মডেলটি নিয়ে JSON Schema তৈরি করবে, আর সঠিক জায়গায় রাখবে।

সঠিক জায়গাটি হলো:

* `content` কী-তে, যার মান আরেকটি JSON অবজেক্ট (`dict`), যাতে আছে:
    * মিডিয়া টাইপসহ একটি কী, যেমন `application/json`, যার মান আরেকটি JSON অবজেক্ট, যাতে আছে:
        * একটি কী `schema`, যার মান হলো মডেলের JSON Schema, এটাই সঠিক জায়গা।
            * **FastAPI** এখানে সরাসরি অন্তর্ভুক্ত না করে, আপনার OpenAPI-এর অন্য একটি জায়গার গ্লোবাল JSON Schema-গুলোর একটি রেফারেন্স (উল্লেখ) যোগ করে। এভাবে অন্য অ্যাপ্লিকেশন আর ক্লায়েন্টরা সরাসরি ওই JSON Schema-গুলো ব্যবহার করতে পারে, আরও ভালো কোড তৈরির টুল দিতে পারে, ইত্যাদি।

///

এই *পাথ অপারেশনের* জন্য OpenAPI-তে তৈরি হওয়া রেসপন্সগুলো হবে:

```JSON hl_lines="3-12"
{
    "responses": {
        "404": {
            "description": "Additional Response",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/Message"
                    }
                }
            }
        },
        "200": {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/Item"
                    }
                }
            }
        },
        "422": {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/HTTPValidationError"
                    }
                }
            }
        }
    }
}
```

স্কিমাগুলো OpenAPI স্কিমার ভেতরের আরেকটি জায়গার উল্লেখ করে:

```JSON hl_lines="4-16"
{
    "components": {
        "schemas": {
            "Message": {
                "title": "Message",
                "required": [
                    "message"
                ],
                "type": "object",
                "properties": {
                    "message": {
                        "title": "Message",
                        "type": "string"
                    }
                }
            },
            "Item": {
                "title": "Item",
                "required": [
                    "id",
                    "value"
                ],
                "type": "object",
                "properties": {
                    "id": {
                        "title": "Id",
                        "type": "string"
                    },
                    "value": {
                        "title": "Value",
                        "type": "string"
                    }
                }
            },
            "ValidationError": {
                "title": "ValidationError",
                "required": [
                    "loc",
                    "msg",
                    "type"
                ],
                "type": "object",
                "properties": {
                    "loc": {
                        "title": "Location",
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "msg": {
                        "title": "Message",
                        "type": "string"
                    },
                    "type": {
                        "title": "Error Type",
                        "type": "string"
                    }
                }
            },
            "HTTPValidationError": {
                "title": "HTTPValidationError",
                "type": "object",
                "properties": {
                    "detail": {
                        "title": "Detail",
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/ValidationError"
                        }
                    }
                }
            }
        }
    }
}
```

## মূল রেসপন্সের জন্য বাড়তি মিডিয়া টাইপ { #additional-media-types-for-the-main-response }

এই একই `responses` প্যারামিটার ব্যবহার করে একই মূল রেসপন্সের জন্য ভিন্ন মিডিয়া টাইপ যোগ করতে পারেন।

যেমন, `image/png`-এর একটি বাড়তি মিডিয়া টাইপ যোগ করতে পারেন, এই ঘোষণা দিয়ে যে আপনার *পাথ অপারেশন* একটি JSON অবজেক্ট (মিডিয়া টাইপ `application/json`) অথবা একটি PNG ছবি ফেরত দিতে পারে:

{* ../../docs_src/additional_responses/tutorial002_py310.py hl[17:22,26] *}

এখানে `?img=true` দিলে ছবি, না দিলে JSON ফেরত আসে, আর ডকুমেন্টেশনে দুটোই দেখায়।

/// note | নোট

খেয়াল করুন, ছবিটি সরাসরি একটি `FileResponse` দিয়ে ফেরত দিতে হবে।

///

/// note | নোট

আপনার `responses` প্যারামিটারে স্পষ্টভাবে ভিন্ন মিডিয়া টাইপ উল্লেখ না করলে FastAPI ধরে নেবে রেসপন্সের মিডিয়া টাইপ মূল রেসপন্স ক্লাসের মতোই (ডিফল্ট `application/json`)।

কিন্তু আপনি যদি `None` মিডিয়া টাইপসহ একটি কাস্টম রেসপন্স ক্লাস নির্দিষ্ট করে থাকেন, তাহলে মডেলসহ যেকোনো বাড়তি রেসপন্সের জন্য FastAPI `application/json` ব্যবহার করবে।

///

## তথ্য একত্র করা { #combining-information }

একাধিক জায়গার রেসপন্স তথ্যও একত্র করতে পারেন, যার মধ্যে আছে `response_model`, `status_code` আর `responses` প্যারামিটার।

ডিফল্ট স্ট্যাটাস কোড `200` (বা দরকার হলে একটি কাস্টম কোড) ব্যবহার করে একটি `response_model` ঘোষণা করতে পারেন, তারপর ওই একই রেসপন্সের জন্য বাড়তি তথ্য `responses`-এ, সরাসরি OpenAPI স্কিমাতে ঘোষণা করতে পারেন।

**FastAPI** `responses` থেকে বাড়তি তথ্য রাখবে, আর আপনার মডেলের JSON Schema-র সাথে মিলিয়ে দেবে।

যেমন, `404` স্ট্যাটাস কোডসহ একটি রেসপন্স ঘোষণা করতে পারেন যা একটি Pydantic মডেল ব্যবহার করে আর একটি কাস্টম `description` আছে।

আর `200` স্ট্যাটাস কোডসহ একটি রেসপন্স, যা আপনার `response_model` ব্যবহার করে, কিন্তু একটি কাস্টম `example` অন্তর্ভুক্ত করে:

{* ../../docs_src/additional_responses/tutorial003_py310.py hl[20:31] *}

এসব একত্রিত হয়ে আপনার OpenAPI-তে অন্তর্ভুক্ত হবে, আর API ডকুমেন্টেশনে দেখানো হবে:

<img src="/img/tutorial/additional-responses/image01.png">

## আগে থেকে তৈরি রেসপন্স আর কাস্টম রেসপন্স মেলানো { #combine-predefined-responses-and-custom-ones }

আপনি হয়তো চাইবেন কিছু আগে থেকে তৈরি রেসপন্স অনেক *পাথ অপারেশনে* প্রযোজ্য হোক, কিন্তু সেগুলোকে প্রতিটি *পাথ অপারেশনের* দরকারি কাস্টম রেসপন্সের সাথে মেলাতে চান।

এসব ক্ষেত্রে একটি `dict` "আনপ্যাক" করার Python কৌশল `**dict_to_unpack` ব্যবহার করতে পারেন:

```Python
old_dict = {
    "old key": "old value",
    "second old key": "second old value",
}
new_dict = {**old_dict, "new key": "new value"}
```

এখানে `new_dict`-এ থাকবে `old_dict`-এর সব কী-মান জোড়া আর নতুন কী-মান জোড়াটি:

```Python
{
    "old key": "old value",
    "second old key": "second old value",
    "new key": "new value",
}
```

আপনার *পাথ অপারেশনে* কিছু আগে থেকে তৈরি রেসপন্স পুনরায় ব্যবহার করে বাড়তি কাস্টম রেসপন্সের সাথে মেলাতে এই কৌশল ব্যবহার করতে পারেন।

যেমন:

{* ../../docs_src/additional_responses/tutorial004_py310.py hl[11:15,24] *}

এখানে ৪০৪, ৩০২, ৪০৩ একবার লিখে রাখা হয়েছে, আর `{**responses, 200: {...}}` দিয়ে সাথে এই পাথের নিজস্ব ২০০ রেসপন্স জুড়ে দেওয়া হয়েছে।

## OpenAPI রেসপন্স নিয়ে আরও তথ্য { #more-information-about-openapi-responses }

রেসপন্সে ঠিক কী কী অন্তর্ভুক্ত করতে পারেন তা দেখতে OpenAPI স্পেসিফিকেশনের এই অংশগুলো দেখতে পারেন:

* [OpenAPI Responses Object](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#responses-object), এতে `Response Object` অন্তর্ভুক্ত।
* [OpenAPI Response Object](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#response-object), এখান থেকে যেকোনো কিছু সরাসরি আপনার `responses` প্যারামিটারের ভেতরের প্রতিটি রেসপন্সে অন্তর্ভুক্ত করতে পারেন। যার মধ্যে আছে `description`, `headers`, `content` (এর ভেতরেই আপনি বিভিন্ন মিডিয়া টাইপ আর JSON Schema ঘোষণা করেন), আর `links`।

/// check | সংক্ষেপে মনে রাখুন

* `responses={404: {"model": Message, "description": "..."}}` দিয়ে ডকুমেন্টেশনে বাড়তি রেসপন্স দেখান।
* আসলে সেই রেসপন্স পাঠাতে কোডে নিজে `JSONResponse(status_code=404, ...)` ফেরত দিন।
* `"content": {"image/png": {}}` দিয়ে বাড়তি মিডিয়া টাইপ।
* সাধারণ রেসপন্সগুলো একটি ডিকশনারিতে রেখে `{**responses, ...}` দিয়ে পুনরায় ব্যবহার করুন।

///
