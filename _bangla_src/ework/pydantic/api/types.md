# Pydantic Types { #pydantic-types }

/// note | এই পেজে যা পাবেন

* Pydantic-এর নিজস্ব তৈরি টাইপগুলো দলে ভাগ করে: শর্তযুক্ত সংখ্যা, strict টাইপ, স্ট্রিংয়ের শর্ত, গোপন মান, তারিখ, ফাইল পথ, UUID, এনকোডিং ইত্যাদি।
* প্রতিটির এক লাইনের বাংলা ব্যাখ্যা আর একটি সম্মিলিত উদাহরণ।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

`int` বলে "সংখ্যা হতে হবে"; `PositiveInt` বলে "ধনাত্মক সংখ্যা হতে হবে"। এই টাইপগুলো হলো আগে থেকে শর্ত বসানো টাইপ, যাতে বারবার `Field(gt=0)` লিখতে না হয়।

///

### সংখ্যা { #bn-numbers }

| টাইপ | শর্ত |
| --- | --- |
| `PositiveInt` / `PositiveFloat` | > 0 |
| `NegativeInt` / `NegativeFloat` | < 0 |
| `NonNegativeInt` / `NonNegativeFloat` | ≥ 0 |
| `NonPositiveInt` / `NonPositiveFloat` | ≤ 0 |
| `FiniteFloat` | `inf`/`nan` নয় |
| `conint(...)`, `confloat(...)`, `condecimal(...)` | `gt`, `ge`, `lt`, `le`, `multiple_of` দিয়ে নিজের শর্ত (নতুন কোডে `Annotated[int, Field(...)]` পছন্দনীয়) |
| `AllowInfNan` | `Annotated` metadata: `inf`/`nan` অনুমোদন |
| `ByteSize` | `'1.5 MiB'`, `'2KB'`-এর মতো লেখা থেকে bytes সংখ্যা; `.human_readable()` |

### strict টাইপ { #bn-strict }

| টাইপ | কী করে |
| --- | --- |
| `StrictInt`, `StrictFloat`, `StrictStr`, `StrictBool`, `StrictBytes` | রূপান্তর ছাড়া শুধু ঠিক সেই টাইপ |
| `Strict()` | `Annotated` metadata: যেকোনো টাইপকে strict করা |

### স্ট্রিং, তালিকা, সেট { #bn-strings }

| টাইপ | কী করে |
| --- | --- |
| `StringConstraints(...)` | `Annotated` metadata: `strip_whitespace`, `to_upper`, `to_lower`, `strict`, `min_length`, `max_length`, `pattern` |
| `constr(...)` | একই শর্ত, পুরনো রূপ |
| `conlist(item_type, min_length, max_length)`, `conset(...)`, `confrozenset(...)`, `conbytes(...)` | আকারের শর্তসহ তালিকা/সেট/bytes |
| `ImportString` | `'math.cos'`-এর মতো লেখা থেকে অবজেক্ট import |
| `Json[T]` | JSON লেখা পার্স করে `T` হিসেবে যাচাই |
| `JsonValue` | যেকোনো বৈধ JSON মান |

### গোপন মান { #bn-secrets }

| টাইপ | কী করে |
| --- | --- |
| `SecretStr`, `SecretBytes` | print, repr আর JSON-এ `'**********'` দেখায়; আসল মান `.get_secret_value()` |
| `Secret[T]` | যেকোনো টাইপকে গোপন করা |

### তারিখ আর সময় { #bn-dates }

| টাইপ | শর্ত |
| --- | --- |
| `PastDate`, `FutureDate` | অতীতের / ভবিষ্যতের তারিখ |
| `PastDatetime`, `FutureDatetime` | অতীতের / ভবিষ্যতের সময় |
| `AwareDatetime`, `NaiveDatetime` | timezone-সহ / timezone-ছাড়া হতে হবে |
| `condate(...)` | `gt`, `ge`, `lt`, `le` দিয়ে তারিখের সীমা |

### ফাইল, পথ, UUID { #bn-paths }

| টাইপ | শর্ত |
| --- | --- |
| `FilePath`, `DirectoryPath` | পথটি থাকতে হবে, আর ফাইল / ফোল্ডার হতে হবে |
| `NewPath` | পথটি এখনো থাকবে না, কিন্তু অভিভাবক ফোল্ডার থাকবে |
| `SocketPath` | একটি বিদ্যমান socket ফাইল |
| `UUID1`, `UUID3`, `UUID4`, `UUID5`, `UUID6`, `UUID7`, `UUID8` | নির্দিষ্ট সংস্করণের UUID |

### এনকোডিং আর অন্যান্য { #bn-others }

| টাইপ | কী করে |
| --- | --- |
| `Base64Str`, `Base64Bytes`, `Base64UrlStr`, `Base64UrlBytes` | base64 লেখা decode করে রাখে, dump-এ আবার encode |
| `EncodedStr`, `EncodedBytes`, `EncoderProtocol` | নিজের এনকোডার বানানোর ভিত্তি |
| `PaymentCardNumber` | কার্ড নম্বর (Luhn পরীক্ষাসহ); নতুন কোডে [extra types-এর Payment](pydantic_extra_types_payment.md) |
| `Discriminator`, `Tag` | callable discriminator দিয়ে union বাছাই |
| `OnErrorOmit` | তালিকায় যে আইটেম ব্যর্থ হয় তা বাদ দেওয়া |
| `FailFast` | তালিকায় প্রথম ভুলেই থামা |
| `GetPydanticSchema` | `Annotated`-এ সরাসরি core schema ফাংশন দেওয়া (অ্যাডভান্সড) |

## উদাহরণ { #bn-example }

```python
from typing import Annotated

from pydantic import BaseModel, ByteSize, Json, PositiveInt, SecretStr, StringConstraints


class Account(BaseModel):
    password: SecretStr
    age: PositiveInt
    size: ByteSize
    meta: Json[dict[str, int]]
    code: Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=2, max_length=3)]


a = Account(password='abc', age='30', size='1.5 MiB', meta='{"x": 1}', code=' bd ')
print(a)
#> password=SecretStr('**********') age=30 size=1572864 meta={'x': 1} code='BD'
print(a.password.get_secret_value(), a.size.human_readable())
#> abc 1.5MiB
print(a.model_dump_json(include={'password'}))
#> {"password":"**********"}
```

বিস্তারিত: [Types](../concepts/types.md), আর standard library টাইপের জন্য [Standard Library Types](standard_library_types.md)।

/// check | সংক্ষেপে মনে রাখুন

* শর্তযুক্ত সংখ্যা: `PositiveInt` ইত্যাদি; strict: `StrictInt` ইত্যাদি।
* পাসওয়ার্ড/টোকেন: `SecretStr`, আসল মান `.get_secret_value()`।
* স্ট্রিংয়ের নিয়ম: `Annotated[str, StringConstraints(...)]`।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
