# AWS Lambda { #aws-lambda }

/// note | এই পেজে যা শিখবেন

* AWS Lambda ফাংশনের জন্য `pydantic` সঠিকভাবে ইনস্টল করা (`.zip`, Layer বা container image)।
* সবচেয়ে প্রচলিত এরর `no module named pydantic_core._pydantic_core` কেন হয় আর কীভাবে ঠিক করবেন।
* `email-validator`-এর metadata সমস্যা, আর Lambda-তে যাচাই ব্যর্থতা ডিবাগ করা।

///

`pydantic` AWS Lambda ফাংশনের সাথে ভালোভাবে কাজ করে। এই গাইডে আলোচনা করব একটি AWS Lambda ফাংশনের জন্য `pydantic` কীভাবে সেটআপ করতে হয়।

## AWS Lambda ফাংশনের জন্য Python লাইব্রেরি ইনস্টল { #installing-python-libraries-for-aws-lambda-functions }

AWS Lambda ফাংশনে Python লাইব্রেরি ব্যবহারের অনেক উপায় আছে। [AWS Lambda ডকুমেন্টেশনে](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html) যেমন বলা আছে, সবচেয়ে প্রচলিত উপায়গুলো:

* আপনার কোড আর dependency প্যাকেজ করতে একটি [`.zip` ফাইল archive](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) ব্যবহার
* একাধিক ফাংশনের মধ্যে লাইব্রেরি ভাগ করতে [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html) ব্যবহার
* আপনার কোড আর dependency প্যাকেজ করতে একটি [container image](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html) ব্যবহার

এই সব উপায়ই `pydantic`-এর সাথে ব্যবহার করা যায়। আপনার জন্য সেরা উপায় নির্ভর করবে আপনার নির্দিষ্ট প্রয়োজন আর সীমাবদ্ধতার ওপর। এখানে প্রথম দুটি ক্ষেত্র আরও বিস্তারিত দেখাব, কারণ
container image-এ dependency ব্যবস্থাপনা আরও সরল। container image ব্যবহার করলে, `pydantic` ইনস্টলের জন্য [এই মন্তব্যটি](https://github.com/pydantic/pydantic/issues/6557#issuecomment-1699456562) কাজের মনে হতে পারে।

/// tip | পরামর্শ

একাধিক ফাংশনে `pydantic` ব্যবহার করলে, AWS Lambda Layers বিবেচনা করতে পারেন, যা একাধিক ফাংশনের মধ্যে নির্বিঘ্নে লাইব্রেরি ভাগ করতে দেয়।

///

যে dependency ব্যবস্থাপনার উপায়ই বেছে নিন, ঝামেলামুক্ত dependency ব্যবস্থাপনা নিশ্চিত করতে
এই নির্দেশিকাগুলো মেনে চলা উপকারী।

## AWS Lambda ফাংশনের জন্য `pydantic` ইনস্টল { #installing-pydantic-for-aws-lambda-functions }

কোড আর dependency দিয়ে আপনার `.zip` ফাইল archive তৈরি করার সময়, বা একটি Lambda Layer-এর জন্য `.zip` ফাইল সাজানোর সময়, সম্ভবত আপনি dependency ইনস্টল আর ব্যবস্থাপনার জন্য একটি local virtual environment ব্যবহার করবেন। `pip` ব্যবহার করলে এটি একটু জটিল হতে পারে, কারণ `pip` আপনার নিজের কম্পিউটারের প্ল্যাটফর্মের জন্য compile করা wheel ইনস্টল করে, যা Lambda পরিবেশের সাথে মানানসই না-ও হতে পারে।

/// tip | উদাহরণ দিয়ে বুঝি

`pydantic-core`-এর ভেতরে Rust থেকে compile করা একটি যন্ত্রাংশ আছে, যা প্রতিটি অপারেটিং সিস্টেম আর CPU-র জন্য আলাদা, যেমন মোবাইলের চার্জার প্রতিটি মডেলের জন্য আলাদা। Mac-এ ইনস্টল করা যন্ত্রাংশ Lambda-র Linux সার্ভারে লাগে না। তাই ইনস্টলের সময় `pip`-কে স্পষ্ট বলে দিতে হয় "Linux-এর জন্য নামাও"।

///

তাই আমরা নিচের মতো একটি কমান্ড ব্যবহারের পরামর্শ দিই:

```bash
pip install \
    --platform manylinux2014_x86_64 \  # (1)!
    --target=<your_package_dir> \  # (2)!
    --implementation cp \  # (3)!
    --python-version 3.10 \  # (4)!
    --only-binary=:all: \  # (5)!
    --upgrade pydantic  # (6)!
```

1. আপনার Lambda runtime-এর সাথে মেলে এমন প্ল্যাটফর্ম ব্যবহার করুন।
2. যে ফোল্ডারে প্যাকেজ ইনস্টল করতে চান তা উল্লেখ করুন (Lambda Layer-এর জন্য প্রায়ই `python`)।
3. CPython বাস্তবায়ন ব্যবহার করুন।
4. Python সংস্করণ অবশ্যই Lambda runtime-এর সাথে মানানসই হতে হবে।
5. এই ফ্ল্যাগ নিশ্চিত করে যে প্যাকেজটি আগে থেকে তৈরি (pre-built) binary wheel থেকে ইনস্টল হবে।
6. `pydantic`-এর সর্বশেষ সংস্করণ ইনস্টল হবে।

## সমস্যা সমাধান { #troubleshooting }

### `pydantic_core` মডিউল পাওয়া যাচ্ছে না { #missing-pydantic_core-module }

এই

```output
no module named `pydantic_core._pydantic_core`
```

এররটি একটি প্রচলিত সমস্যা, যা বোঝায় আপনি `pydantic` ভুলভাবে ইনস্টল করেছেন। এই সমস্যা ডিবাগ করতে, নিচের ধাপগুলো চেষ্টা করতে পারেন (ব্যর্থ import-এর আগে):

1. ইনস্টল হওয়া `pydantic-core` প্যাকেজের বিষয়বস্তু পরীক্ষা করুন। compile করা লাইব্রেরি আর তার type stub দুটোই কি আছে?

    ```python
    from importlib.metadata import files
    print([file for file in files('pydantic-core') if file.name.startswith('_pydantic_core')])
    """
    [PackagePath('pydantic_core/_pydantic_core.pyi'), PackagePath('pydantic_core/_pydantic_core.cpython-312-x86_64-linux-gnu.so')]
    """
    ```

    ওপরে print হওয়ার মতো দুটি ফাইল দেখার কথা। compile করা লাইব্রেরি ফাইলের এক্সটেনশন হবে `.so` বা `.pyd`, আর নাম অপারেটিং সিস্টেম আর Python সংস্করণ অনুযায়ী বদলায়।

2. পরীক্ষা করুন আপনার lambda-র Python সংস্করণ ওপরে পাওয়া compile করা লাইব্রেরির সংস্করণের সাথে মানানসই কিনা।

    ```python
    import sysconfig
    print(sysconfig.get_config_var("EXT_SUFFIX"))
    #> '.cpython-312-x86_64-linux-gnu.so'
    ```

এখানে compile করা লাইব্রেরির মতোই একই suffix দেখার কথা, যেমন এখানে দেখছি এই suffix `.cpython-312-x86_64-linux-gnu.so` আসলেই `_pydantic_core.cpython-312-x86_64-linux-gnu.so`-এর সাথে মেলে।

এই দুই পরীক্ষা না মিললে, আপনার build ধাপগুলো আপনার lambda-র লক্ষ্য প্ল্যাটফর্মের জন্য সঠিক native কোড ইনস্টল করেনি। ইনস্টল হওয়া লাইব্রেরির সংস্করণ বদলাতে আপনার build ধাপগুলো ঠিক করা উচিত।

সবচেয়ে সম্ভাব্য এরর:

* আপনার অপারেটিং সিস্টেম বা CPU architecture মেলেনি (যেমন darwin বনাম x86_64-linux-gnu)। আপনার lambda-র dependency ইনস্টলের সময় `pip install`-এ সঠিক `--platform` আর্গুমেন্ট দিয়ে চেষ্টা করুন, অথবা সঠিক প্ল্যাটফর্মের জন্য একটি linux docker container-এর ভেতরে build করুন। এখন সম্ভাব্য প্ল্যাটফর্মের মধ্যে আছে `--platform manylinux2014_x86_64` বা `--platform manylinux2014_aarch64`, তবে Pydantic-এর ভবিষ্যৎ কোনো বড় রিলিজে এগুলো বদলাতে পারে।

* আপনার Python সংস্করণ মেলেনি (যেমন `cpython-310` বনাম `cpython-312`)। `pip install`-এ সঠিক `--python-version` আর্গুমেন্ট দিয়ে চেষ্টা করুন, অথবা আপনার build-এ ব্যবহৃত Python সংস্করণ বদলান।

### `email-validator`-এর জন্য কোনো প্যাকেজ metadata পাওয়া যায়নি { #no-package-metadata-was-found-for-email-validator }

`email-validator`-এর কোন সংস্করণ ইনস্টল আছে তা [পরীক্ষা করতে](https://github.com/pydantic/pydantic/pull/6033) Pydantic `importlib.metadata` থেকে `version` ব্যবহার করে।
প্যাকেজের সংস্করণের এই ব্যবস্থা AWS Lambda-র সাথে কিছুটা অসামঞ্জস্যপূর্ণ, যদিও Python-এ প্যাকেজের সংস্করণ নির্ধারণে এটিই শিল্পের মানক।
এই সমস্যা ঠিক করার কয়েকটি উপায় আছে:

serverless framework দিয়ে আপনার lambda deploy করলে, সম্ভবত আপনার deployment প্যাকেজে `email-validator` প্যাকেজের উপযুক্ত metadata অন্তর্ভুক্ত হচ্ছে না। [`serverless-python-requirements`](https://github.com/serverless/serverless-python-requirements/tree/master)-এর মতো টুল
প্যাকেজের আকার কমাতে metadata সরিয়ে দেয়। আপনার `serverless.yml` ফাইলে `slim` সেটিং false করে এই সমস্যা ঠিক করতে পারেন:

```yaml
pythonRequirements:
    dockerizePip: non-linux
    slim: false
    fileName: requirements.txt
```

এই সমাধান আর প্রাসঙ্গিক হতে পারে এমন অন্য `slim` সেটিংস নিয়ে আরও পড়তে পারেন এই [blog post-এ](https://biercoff.com/how-to-fix-package-not-found-error-importlib-metadata/)।

আপনার কোড আর/অথবা dependency-র জন্য `.zip` archive ব্যবহার করলে, নিশ্চিত করুন আপনার প্যাকেজে প্রয়োজনীয় সংস্করণের metadata আছে। এজন্য `email-validator` প্যাকেজের `dist-info` ফোল্ডারটি আপনার `.zip` archive-এ অন্তর্ভুক্ত করুন।

[`jsonschema`](https://github.com/python-jsonschema/jsonschema/issues/584)-এর মতো অন্যান্য জনপ্রিয় python লাইব্রেরির ক্ষেত্রেও এই সমস্যার খবর পাওয়া গেছে, তাই
সমস্যা আর সম্ভাব্য সমাধান নিয়ে সেখানেও আরও পড়তে পারেন।

## বাড়তি রিসোর্স { #extra-resources }

### আরও ডিবাগিং টিপস { #more-debugging-tips }

আপনার AWS Lambda-র জন্য `pydantic` ইনস্টলে এখনো সমস্যা হলে, [এই issue](https://github.com/pydantic/pydantic/issues/6557) দেখতে পারেন, যেখানে অন্য ডেভেলপারদের মুখোমুখি হওয়া নানা সমস্যা আর সমাধান আছে।

### `event` আর `context` ডেটা যাচাই { #validating-event-and-context-data }

AWS Lambda ফাংশনে `event` আর `context` ডেটা যাচাইয়ে `pydantic` কীভাবে ব্যবহার করবেন তা আরও জানতে আমাদের [blog post](https://pydantic.dev/articles/lambda-intro) দেখুন।

```python
from pydantic import BaseModel, ValidationError


class OrderEvent(BaseModel):
    order_id: int
    amount: float


def handler(event, context):
    try:
        order = OrderEvent.model_validate(event)
    except ValidationError as exc:
        return {'statusCode': 400, 'body': exc.json()}
    return {'statusCode': 200, 'body': f'অর্ডার {order.order_id} গ্রহণ করা হলো'}
```

Lambda-তে যাচাই ব্যর্থতা ডিবাগ করা বিশেষভাবে ঝামেলার: debugger যুক্ত করা যায় না, আর যে
event ব্যর্থতা ঘটাল তা invocation-এর সাথেই হারিয়ে যায়। [Logfire](../integrations/logfire.md) দিয়ে যাচাই রেকর্ড করলে,
প্রতিটি ব্যর্থ যাচাই তার গোছানো এরর আর প্রত্যাখ্যাত মানসহ জমা থাকে, আর এর [AWS Lambda integration](https://pydantic.dev/docs/logfire/integrations/aws-lambda/)
আশেপাশের invocation-ও ধরে রাখে।
