# ফাইলের ডেটা যাচাই { #validating-file-data }

/// note | এই পেজে যা শিখবেন

* JSON, JSON lines, CSV, TOML, YAML, XML আর INI ফাইল থেকে পড়া ডেটা Pydantic দিয়ে যাচাই করা।
* একটি ফাইলে অনেকগুলো রেকর্ড থাকলে `TypeAdapter(list[...])` দিয়ে একবারে যাচাই।
* ভুল ডেটা থাকলে এরর কেমন দেখায়, আর কোন রেকর্ডে ভুল তা কীভাবে বুঝবেন।

///

বিভিন্ন উৎস থেকে আসা ডেটা যাচাইয়ের জন্য `pydantic` একটি দারুণ টুল।
এই অংশে দেখব বিভিন্ন ধরনের ফাইল থেকে ডেটা কীভাবে যাচাই করতে হয়।

/// tip | উদাহরণ দিয়ে বুঝি

ফাইলের ফরম্যাট যা-ই হোক, কাজের ধাপ সবসময় দুটি: (১) ফাইলটি পড়ে Python ডিকশনারি বা লেখা বানানো, যেটা প্রতিটি ফরম্যাটের নিজের লাইব্রেরি করে (`json`, `csv`, `tomllib`, `yaml`...); (২) সেই ডেটা একই `Person` মডেল দিয়ে যাচাই করা। মডেল একটাই, শুধু "খাম খোলার" উপায় আলাদা।

///

/// note | মনে রাখুন

নিচের কোনো ফাইল ফরম্যাট কনফিগারেশন / সেটিংস পার্স করতে ব্যবহার করলে,
[`pydantic-settings`][pydantic_settings] লাইব্রেরি ব্যবহারের কথা ভাবতে পারেন, যা এই ধরনের ডেটা পার্সের
নিজস্ব সমর্থন দেয়।

///

## JSON ডেটা { #json-data }

মানুষের পড়ার উপযোগী রূপে key / value ডেটা রাখার একটি প্রচলিত উপায় `.json` ফাইল।
এখানে একটি `.json` ফাইলের উদাহরণ:

```json
{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com"
}
```

এই ডেটা যাচাই করতে আমরা একটি `pydantic` মডেল ব্যবহার করতে পারি:

```python
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_string = pathlib.Path('person.json').read_text()
person = Person.model_validate_json(json_string)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

/// info | কোডটি সহজ ভাষায়

* `PositiveInt`: শূন্যের চেয়ে বড় পূর্ণসংখ্যা হতে হবে।
* `EmailStr`: বৈধ ইমেইল ঠিকানা হতে হবে (এর জন্য `pip install "pydantic[email]"` লাগে)।
* `model_validate_json()` লেখা (JSON স্ট্রিং) সরাসরি নিয়ে একবারে পার্স আর যাচাই করে, `json.loads()` আলাদা করে লাগে না।

///

ফাইলের ডেটা বৈধ না হলে, `pydantic` একটি [`ValidationError`][pydantic_core.ValidationError] তুলবে।
ধরুন আমাদের কাছে নিচের `.json` ফাইলটি আছে:

```json
{
    "age": -30,
    "email": "not-an-email-address"
}
```

এই ডেটায় তিনটি ত্রুটি:

1. এতে `name` ফিল্ড নেই।
2. `age` ফিল্ড ঋণাত্মক।
3. `email` ফিল্ড বৈধ ইমেইল ঠিকানা নয়।

এই ডেটা যাচাইয়ের চেষ্টা করলে, `pydantic` ওপরের সব সমস্যাসহ একটি [`ValidationError`][pydantic_core.ValidationError]
তোলে:

```python
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt, ValidationError


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_string = pathlib.Path('person.json').read_text()
try:
    person = Person.model_validate_json(json_string)
except ValidationError as err:
    print(err)
    """
    3 validation errors for Person
    name
    Field required [type=missing, input_value={'age': -30, 'email': 'not-an-email-address'}, input_type=dict]
        For further information visit https://errors.pydantic.dev/2/v/missing
    age
    Input should be greater than 0 [type=greater_than, input_value=-30, input_type=int]
        For further information visit https://errors.pydantic.dev/2/v/greater_than
    email
    value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='not-an-email-address', input_type=str]
    """
```

/// info | এররটি সহজ ভাষায়

Pydantic প্রথম ভুলে থেমে যায় না; তিনটি ভুলই একসাথে জানায়। প্রতিটি অংশে আছে: কোন ফিল্ড (`name`, `age`, `email`), কী সমস্যা (`Field required`, `Input should be greater than 0`), এররের ধরন (`type=missing`), আর কোন মান দেওয়া হয়েছিল (`input_value=-30`)।

///

প্রায়ই একটি `.json` ফাইলে একই ধরনের অনেক ডেটা থাকে।
যেমন, আপনার কাছে মানুষের একটি তালিকা থাকতে পারে:

```json
[
    {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    },
    {
        "name": "Jane Doe",
        "age": 25,
        "email": "jane@example.com"
    }
]
```

এক্ষেত্রে, ডেটাটি একটি `list[Person]` মডেলের বিপরীতে যাচাই করতে পারেন:

```python
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt, TypeAdapter


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


person_list_adapter = TypeAdapter(list[Person])  # (1)!

json_string = pathlib.Path('people.json').read_text()
people = person_list_adapter.validate_json(json_string)
print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

1. `Person` অবজেক্টের একটি তালিকা যাচাই করতে আমরা [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ব্যবহার করি।
[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] হলো একটি Pydantic কাঠামো, যা একটি নির্দিষ্ট টাইপের বিপরীতে ডেটা যাচাইয়ে ব্যবহার হয়।

দুটি রেকর্ড হলে ভুলটি খুঁজে পাওয়া সহজ। হাজার হাজার রেকর্ডের ফাইল প্রক্রিয়া করা একটি pipeline-এ,
এররের `loc` আপনাকে ব্যর্থ রেকর্ডটির index (ক্রমিক নম্বর) দেয়, আর pipeline যদি কারো নজরদারি ছাড়া চলে,
[Logfire](../errors/troubleshooting.md) ব্যর্থ যাচাইগুলো তাদের ফিল্ডের অবস্থান আর
প্রত্যাখ্যাত মানসহ রেকর্ড করে, ফলে চলা শেষে সমস্যার রেকর্ডটি খুঁজে পেতে পারেন।

## JSON lines ফাইল { #json-lines-files }

একটি `.json` ফাইল থেকে অবজেক্টের তালিকা যাচাইয়ের মতোই, একটি `.jsonl` ফাইল থেকেও অবজেক্টের তালিকা যাচাই করতে পারেন।
`.jsonl` ফাইল হলো নতুন লাইন দিয়ে আলাদা করা JSON অবজেক্টের একটি ক্রম, প্রতি লাইনে একটি।

নিচের `.jsonl` ফাইলটি দেখুন:

```json
{"name": "John Doe", "age": 30, "email": "john@example.com"}
{"name": "Jane Doe", "age": 25, "email": "jane@example.com"}
```

`.json` ফাইলের জন্য ব্যবহৃত পদ্ধতির মতোই এই ডেটা যাচাই করা যায়:

```python
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_lines = pathlib.Path('people.jsonl').read_text().splitlines()
people = [Person.model_validate_json(line) for line in json_lines]
print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

/// tip | পরামর্শ

খুব বড় `.jsonl` ফাইলে পুরো ফাইল একবারে না পড়ে লাইন ধরে ধরে পড়ুন: `with open('people.jsonl') as f: for line in f: Person.model_validate_json(line)`। এতে মেমোরি কম লাগে, আর ভুল লাইন পেলে লাইন নম্বরসহ লগ করে বাকিগুলো চালিয়ে যেতে পারেন।

///

## CSV ফাইল { #csv-files }

সারণির (tabular) ডেটা রাখার সবচেয়ে প্রচলিত ফাইল ফরম্যাটগুলোর একটি CSV।
একটি CSV ফাইলের ডেটা যাচাই করতে, Python standard library-র `csv` মডিউল দিয়ে ডেটা লোড করে
একটি Pydantic মডেলের বিপরীতে যাচাই করতে পারেন।

নিচের CSV ফাইলটি দেখুন:

```csv
name,age,email
John Doe,30,john@example.com
Jane Doe,25,jane@example.com
```

এভাবে আমরা সেই ডেটা যাচাই করি:

```python
import csv

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('people.csv') as f:
    reader = csv.DictReader(f)
    people = [Person.model_validate(row) for row in reader]

print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

/// info | কোডটি সহজ ভাষায়

CSV-তে সব মানই লেখা (স্ট্রিং), যেমন `age` আসে `'30'` হিসেবে। Pydantic-এর lax মোড সেটিকে নিজে থেকেই `30` সংখ্যায় বদলে দেয়, তাই আলাদা করে `int()` করতে হয় না।

///

## TOML ফাইল { #toml-files }

সহজ আর পড়ার উপযোগী হওয়ায় TOML ফাইল প্রায়ই কনফিগারেশনের জন্য ব্যবহার হয়।

নিচের TOML ফাইলটি দেখুন:

```toml
name = "John Doe"
age = 30
email = "john@example.com"
```

এভাবে আমরা সেই ডেটা যাচাই করি:

```python
import tomllib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('person.toml', 'rb') as f:
    data = tomllib.load(f)

person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

## YAML ফাইল { #yaml-files }

YAML (YAML Ain't Markup Language) মানুষের পড়ার উপযোগী একটি ডেটা সিরিয়ালাইজেশন ফরম্যাট, যা প্রায়ই কনফিগারেশন ফাইলে ব্যবহার হয়।

নিচের YAML ফাইলটি দেখুন:

```yaml
name: John Doe
age: 30
email: john@example.com
```

[PyYAML](https://pypi.org/project/PyYAML/) দিয়ে এভাবে আমরা সেই ডেটা যাচাই করি:

```python
import yaml

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('person.yaml') as f:
    data = yaml.safe_load(f)

person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

/// warning | সাধারণ ভুল

YAML পড়তে সবসময় `yaml.safe_load()` ব্যবহার করুন, `yaml.load()` নয়। অচেনা উৎসের YAML ফাইলে `yaml.load()` ক্ষতিকর Python অবজেক্ট তৈরি করতে পারে।

///

## XML ফাইল { #xml-files }

XML (eXtensible Markup Language) একটি markup ভাষা, যা এমন একটি নিয়মের সেট সংজ্ঞায়িত করে যাতে ডকুমেন্ট মানুষ আর মেশিন দুজনেরই পড়ার উপযোগী ফরম্যাটে লেখা যায়।

নিচের XML ফাইলটি দেখুন:

```xml
<?xml version="1.0"?>
<person>
    <name>John Doe</name>
    <age>30</age>
    <email>john@example.com</email>
</person>
```

এভাবে আমরা সেই ডেটা যাচাই করি:

```python
import xml.etree.ElementTree as ET

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


tree = ET.parse('person.xml').getroot()
data = {child.tag: child.text for child in tree}
person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

## INI ফাইল { #ini-files }

INI ফাইল হলো section আর key-value জোড়া ব্যবহার করা একটি সহজ কনফিগারেশন ফাইল ফরম্যাট। এগুলো সাধারণত Windows অ্যাপ্লিকেশন আর পুরনো সফটওয়্যারে ব্যবহার হয়।

নিচের INI ফাইলটি দেখুন:

```ini
[PERSON]
name = John Doe
age = 30
email = john@example.com
```

এভাবে আমরা সেই ডেটা যাচাই করি:

```python
import configparser

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


config = configparser.ConfigParser()
config.read('person.ini')
person = Person.model_validate(config['PERSON'])
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

/// check | সংক্ষেপে মনে রাখুন

| ফরম্যাট | পড়ার উপায় | যাচাই |
| --- | --- | --- |
| JSON | `Path(...).read_text()` | `Model.model_validate_json(text)` |
| JSON তালিকা | `Path(...).read_text()` | `TypeAdapter(list[Model]).validate_json(text)` |
| JSON lines | প্রতি লাইন | `Model.model_validate_json(line)` |
| CSV | `csv.DictReader` | প্রতি সারি `Model.model_validate(row)` |
| TOML | `tomllib.load(f)` | `Model.model_validate(data)` |
| YAML | `yaml.safe_load(f)` | `Model.model_validate(data)` |
| XML | `ElementTree` → ডিকশনারি | `Model.model_validate(data)` |
| INI | `configparser` | `Model.model_validate(config['SECTION'])` |

///
