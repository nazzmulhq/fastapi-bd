# Validators { #validators }

/// note | এই পেজে যা শিখবেন

* validator কী, আর Pydantic-এর নিজের যাচাইয়ের বাইরে নিজের নিয়ম কীভাবে যোগ করবেন।
* ফিল্ড validator-এর চার ধরন: *after*, *before*, *plain*, *wrap*; আর মডেল validator-এর তিন ধরন।
* annotated pattern নাকি decorator, কোনটি কখন।
* এরর তোলা, `ValidationInfo` (আগে যাচাই হওয়া ডেটা, context), validator-এর ক্রম, আর কিছু বিশেষ টাইপ।

///

Pydantic-এর [নিজস্ব যাচাই ক্ষমতা](./fields.md#field-constraints) ছাড়াও,
আরও জটিল শর্ত চাপাতে আর ডেটার সঠিকতা নিশ্চিত করতে আপনি ফিল্ড আর মডেল পর্যায়ে নিজের (custom) validator ব্যবহার করতে পারেন।

/// tip | উদাহরণ দিয়ে বুঝি

Pydantic হলো বিমানবন্দরের নিরাপত্তা স্ক্যানার: ব্যাগে কী আছে (টাইপ ঠিক আছে কিনা) নিজে থেকেই দেখে। validator হলো আপনার নিজের নিয়োগ দেওয়া বাড়তি পরিদর্শক। তিনি স্ক্যানারের **পরে** দাঁড়াতে পারেন (*after*: "ওজন কি ২০ কেজির কম?"), **আগে** দাঁড়াতে পারেন (*before*: "ব্যাগ খোলা থাকলে আগে বন্ধ করে দিই"), স্ক্যানারের **বদলে** কাজ করতে পারেন (*plain*), বা স্ক্যানারকে **ঘিরে** দাঁড়াতে পারেন (*wrap*: আগে-পরে দুটোই দেখেন, দরকারে স্ক্যানার এড়িয়ে যান)।

///

/// tip | পরামর্শ

সরাসরি দরকারি validator অংশে যেতে চান?

<div class="grid cards" markdown>

*   ফিল্ড validator

    ---

    * [ফিল্ড *after* validator](#field-after-validator)
    * [ফিল্ড *before* validator](#field-before-validator)
    * [ফিল্ড *plain* validator](#field-plain-validator)
    * [ফিল্ড *wrap* validator](#field-wrap-validator)

*   মডেল validator

    ---

    * [মডেল *before* validator](#model-before-validator)
    * [মডেল *after* validator](#model-after-validator)
    * [মডেল *wrap* validator](#model-wrap-validator)

</div>

///

## ফিল্ড validator { #field-validators }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.functional_validators.WrapValidator`][pydantic.functional_validators.WrapValidator]<br>
[`pydantic.functional_validators.PlainValidator`][pydantic.functional_validators.PlainValidator]<br>
[`pydantic.functional_validators.BeforeValidator`][pydantic.functional_validators.BeforeValidator]<br>
[`pydantic.functional_validators.AfterValidator`][pydantic.functional_validators.AfterValidator]<br>
[`pydantic.functional_validators.field_validator`][pydantic.functional_validators.field_validator]<br>

///

সবচেয়ে সহজ রূপে, ফিল্ড validator হলো এমন একটি callable (ফাংশন) যা যাচাই করার মানটি আর্গুমেন্ট হিসেবে নেয় আর
**যাচাই করা মানটি ফেরত দেয়**। এটি নির্দিষ্ট শর্ত পরীক্ষা করতে পারে (দেখুন
[যাচাই এরর তোলা](#raising-validation-errors)) আর মানটি বদলাতেও পারে (রূপান্তর বা পরিবর্তন)।

**চার** ধরনের validator ব্যবহার করা যায়। সবগুলোই
[annotated pattern](./fields.md#the-annotated-pattern) দিয়ে, অথবা একটি [class method][classmethod]-এর ওপর
[`@field_validator`][pydantic.field_validator] decorator বসিয়ে সংজ্ঞায়িত করা যায়:

| ধরন | কখন চলে | ইনপুট কেমন | কখন ব্যবহার |
| --- | --- | --- | --- |
| *after* | Pydantic-এর যাচাইয়ের **পরে** | ইতিমধ্যে সঠিক টাইপের মান | বাড়তি শর্ত পরীক্ষা (সবচেয়ে প্রচলিত, সবচেয়ে নিরাপদ) |
| *before* | Pydantic-এর যাচাইয়ের **আগে** | কাঁচা ইনপুট, যা খুশি হতে পারে | ইনপুট আগে থেকে গুছিয়ে নেওয়া |
| *plain* | Pydantic-এর যাচাইয়ের **বদলে** | কাঁচা ইনপুট | পুরো যাচাই নিজে করা |
| *wrap* | Pydantic-এর যাচাইকে **ঘিরে** | কাঁচা ইনপুট + `handler` | আগে-পরে দুটোই নিয়ন্ত্রণ, এরর ধরে সামলানো |

* ***After* validator**: Pydantic-এর ভেতরের যাচাইয়ের পরে চলে। সাধারণত এগুলো বেশি টাইপ-নিরাপদ, তাই লেখাও সহজ।
{% raw %}{#field-after-validator}{% endraw %}

    /// tab | Annotated pattern

    এখানে একটি validator যাচাই করছে, আর মান না বদলে ফেরত দিচ্ছে।

    ```python
    from typing import Annotated

    from pydantic import AfterValidator, BaseModel, ValidationError


    def is_even(value: int) -> int:
        if value % 2 == 1:
            raise ValueError(f'{value} is not an even number')
        return value  # (1)!


    class Model(BaseModel):
        number: Annotated[int, AfterValidator(is_even)]


    try:
        Model(number=1)
    except ValidationError as err:
        print(err)
        """
        1 validation error for Model
        number
          Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
        """
    ```

    1. মনে রাখুন, যাচাই করা মান ফেরত দেওয়া জরুরি।

    ///

    /// tab | Decorator

    এখানেও একটি validator যাচাই করছে আর মান না বদলে ফেরত দিচ্ছে,
    এবার [`field_validator()`][pydantic.field_validator] decorator দিয়ে।

    ```python
    from pydantic import BaseModel, ValidationError, field_validator


    class Model(BaseModel):
        number: int

        @field_validator('number', mode='after')  # (1)!
        @classmethod
        def is_even(cls, value: int) -> int:
            if value % 2 == 1:
                raise ValueError(f'{value} is not an even number')
            return value  # (2)!


    try:
        Model(number=1)
    except ValidationError as err:
        print(err)
        """
        1 validation error for Model
        number
          Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
        """
    ```

    1. decorator-এর ডিফল্ট মোড `'after'`, তাই এটি না লিখলেও চলে।
    2. মনে রাখুন, যাচাই করা মান ফেরত দেওয়া জরুরি।

    ///

    //// details | মান বদলানোর উদাহরণ
        type: tip

    এখানে একটি validator যাচাই করা মানটি বদলে দিচ্ছে (কোনো এক্সেপশন তোলা হচ্ছে না)।

    /// tab | Annotated pattern

    ```python
    from typing import Annotated

    from pydantic import AfterValidator, BaseModel


    def double_number(value: int) -> int:
        return value * 2


    class Model(BaseModel):
        number: Annotated[int, AfterValidator(double_number)]


    print(Model(number=2))
    #> number=4
    ```

    ///

    /// tab | Decorator

    ```python
    from pydantic import BaseModel, field_validator


    class Model(BaseModel):
        number: int

        @field_validator('number', mode='after')  # (1)!
        @classmethod
        def double_number(cls, value: int) -> int:
            return value * 2


    print(Model(number=2))
    #> number=4
    ```

    1. decorator-এর ডিফল্ট মোড `'after'`, তাই এটি না লিখলেও চলে।

    ///

    ////

* ***Before* validator**: Pydantic-এর ভেতরের পার্সিং আর যাচাইয়ের আগে চলে (যেমন `str` থেকে `int`-এ রূপান্তরের আগে)।
  এগুলো [*after* validator](#field-after-validator)-এর চেয়ে নমনীয়, কিন্তু এদের কাঁচা ইনপুট সামলাতে হয়, যা
  তাত্ত্বিকভাবে যেকোনো অবজেক্ট হতে পারে। validator ফাংশনে পরে [যাচাই এরর](#raising-validation-errors) তুলতে পারেন এমন
  হলে মানটি সরাসরি বদলানো (mutate) এড়িয়ে চলুন, কারণ [union](./unions.md) ব্যবহার করলে বদলানো মান অন্য
  validator-এর কাছে চলে যেতে পারে।
{% raw %}  {#field-before-validator}{% endraw %}

    এই callable যা ফেরত দেয়, Pydantic তারপর সেটিকে দেওয়া টাইপ annotation অনুযায়ী যাচাই করে।

    /// tab | Annotated pattern

    ```python
    from typing import Annotated, Any

    from pydantic import BaseModel, BeforeValidator, ValidationError


    def ensure_list(value: Any) -> Any:  # (1)!
        if not isinstance(value, list):  # (2)!
            return [value]
        else:
            return value


    class Model(BaseModel):
        numbers: Annotated[list[int], BeforeValidator(ensure_list)]


    print(Model(numbers=2))
    #> numbers=[2]
    try:
        Model(numbers='str')
    except ValidationError as err:
        print(err)  # (3)!
        """
        1 validation error for Model
        numbers.0
          Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='str', input_type=str]
        """
    ```

    1. লক্ষ করুন, `value`-এর টাইপ হিসেবে [`Any`][typing.Any] দেওয়া হয়েছে। *Before* validator কাঁচা ইনপুট নেয়, যা
       যেকোনো কিছু হতে পারে।

    2. মনে রাখুন, অন্য sequence টাইপও (যেমন tuple) পরীক্ষা করতে চাইতে পারেন, যেগুলো সাধারণত `list` টাইপের
       বিপরীতে সফলভাবে যাচাই হয়। *Before* validator বেশি নমনীয়তা দেয়, কিন্তু আপনাকে প্রতিটি সম্ভাব্য
       ক্ষেত্র হিসাবে রাখতে হয়।

    3. আমাদের `ensure_list` validator মূল ইনপুটের ওপর যা-ই করুক, Pydantic তারপরও `int` টাইপের বিপরীতে যাচাই করে।

    ///

    /// tab | Decorator

    ```python
    from typing import Any

    from pydantic import BaseModel, ValidationError, field_validator


    class Model(BaseModel):
        numbers: list[int]

        @field_validator('numbers', mode='before')
        @classmethod
        def ensure_list(cls, value: Any) -> Any:  # (1)!
            if not isinstance(value, list):  # (2)!
                return [value]
            else:
                return value


    print(Model(numbers=2))
    #> numbers=[2]
    try:
        Model(numbers='str')
    except ValidationError as err:
        print(err)  # (3)!
        """
        1 validation error for Model
        numbers.0
          Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='str', input_type=str]
        """
    ```

    1. লক্ষ করুন, `value`-এর টাইপ হিসেবে [`Any`][typing.Any] দেওয়া হয়েছে। *Before* validator কাঁচা ইনপুট নেয়, যা
       যেকোনো কিছু হতে পারে।

    2. মনে রাখুন, অন্য sequence টাইপও (যেমন tuple) পরীক্ষা করতে চাইতে পারেন, যেগুলো সাধারণত `list` টাইপের
       বিপরীতে সফলভাবে যাচাই হয়। *Before* validator বেশি নমনীয়তা দেয়, কিন্তু আপনাকে প্রতিটি সম্ভাব্য
       ক্ষেত্র হিসাবে রাখতে হয়।

    3. আমাদের `ensure_list` validator মূল ইনপুটের ওপর যা-ই করুক, Pydantic তারপরও `int` টাইপের বিপরীতে যাচাই করে।

    ///

* ***Plain* validator**: *before* validator-এর মতোই কাজ করে, কিন্তু ফেরত দেওয়ার পরেই **যাচাই সাথে সাথে শেষ** হয়ে যায়,
  ফলে আর কোনো validator চলে না আর Pydantic ফিল্ডের টাইপের বিপরীতে নিজের কোনো যাচাই করে না।
{% raw %}  {#field-plain-validator}{% endraw %}

    /// tab | Annotated pattern

    ```python
    from typing import Annotated, Any

    from pydantic import BaseModel, PlainValidator


    def val_number(value: Any) -> Any:
        if isinstance(value, int):
            return value * 2
        else:
            return value


    class Model(BaseModel):
        number: Annotated[int, PlainValidator(val_number)]


    print(Model(number=4))
    #> number=8
    print(Model(number='invalid'))  # (1)!
    #> number='invalid'
    ```

    1. `'invalid'` `int` টাইপ হিসেবে যাচাই হওয়ার কথা নয়, তবু Pydantic ইনপুটটি গ্রহণ করে।

    ///

    /// tab | Decorator

    ```python
    from typing import Any

    from pydantic import BaseModel, field_validator


    class Model(BaseModel):
        number: int

        @field_validator('number', mode='plain')
        @classmethod
        def val_number(cls, value: Any) -> Any:
            if isinstance(value, int):
                return value * 2
            else:
                return value


    print(Model(number=4))
    #> number=8
    print(Model(number='invalid'))  # (1)!
    #> number='invalid'
    ```

    1. `'invalid'` `int` টাইপ হিসেবে যাচাই হওয়ার কথা নয়, তবু Pydantic ইনপুটটি গ্রহণ করে।

    ///

* ***Wrap* validator**: সবচেয়ে নমনীয়। Pydantic আর অন্য validator ইনপুট প্রক্রিয়া করার আগে বা পরে কোড চালাতে পারেন,
  অথবা আগেভাগে মান ফেরত দিয়ে বা এরর তুলে সাথে সাথে যাচাই শেষ করতে পারেন।
{% raw %}  {#field-wrap-validator}{% endraw %}

    এমন validator-এ একটি **বাধ্যতামূলক** বাড়তি *handler* প্যারামিটার থাকতে হয়: এটি একটি callable যা যাচাই করার মান
    আর্গুমেন্ট হিসেবে নেয়। ভেতরে ভেতরে এই handler মানটির যাচাই Pydantic-এর হাতে তুলে দেয়। handler-এর ডাক আপনি
    একটি [`try..except`][handling exceptions] ব্লকে মুড়ে রাখতে পারেন, অথবা একেবারেই না ডাকতে পারেন।

    [handling exceptions]: https://docs.python.org/3/tutorial/errors.html#handling-exceptions

    /// tab | Annotated pattern

    ```python
    from typing import Any

    from typing import Annotated

    from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, WrapValidator


    def truncate(value: Any, handler: ValidatorFunctionWrapHandler) -> str:
        try:
            return handler(value)
        except ValidationError as err:
            if err.errors()[0]['type'] == 'string_too_long':
                return handler(value[:5])
            else:
                raise


    class Model(BaseModel):
        my_string: Annotated[str, Field(max_length=5), WrapValidator(truncate)]


    print(Model(my_string='abcde'))
    #> my_string='abcde'
    print(Model(my_string='abcdef'))
    #> my_string='abcde'
    ```

    ///

    /// tab | Decorator

    ```python
    from typing import Any

    from typing import Annotated

    from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, field_validator


    class Model(BaseModel):
        my_string: Annotated[str, Field(max_length=5)]

        @field_validator('my_string', mode='wrap')
        @classmethod
        def truncate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> str:
            try:
                return handler(value)
            except ValidationError as err:
                if err.errors()[0]['type'] == 'string_too_long':
                    return handler(value[:5])
                else:
                    raise


    print(Model(my_string='abcde'))
    #> my_string='abcde'
    print(Model(my_string='abcdef'))
    #> my_string='abcde'
    ```

    ///

/// info | কোডটি সহজ ভাষায় (wrap উদাহরণ)

`truncate` প্রথমে `handler(value)` ডেকে Pydantic-কে স্বাভাবিক যাচাই করতে দেয়। লেখা ৫ অক্ষরের বেশি হলে `string_too_long` এরর আসে; তখন validator সেটি ধরে প্রথম ৫ অক্ষর কেটে আবার `handler`-এ পাঠায়। ফলে `'abcdef'` এরর না দিয়ে `'abcde'` হয়ে যায়। অন্য যেকোনো এরর হলে `raise` দিয়ে আবার তুলে দেওয়া হয়।

///

/// note | ডিফল্ট মানের যাচাই

[ফিল্ড ডকুমেন্টেশনে](./fields.md#validate-default-values) যেমন বলা আছে, ফিল্ডের ডিফল্ট মান
কনফিগার না করলে যাচাই *হয় না*, তাই নিজের validator-ও তাদের ওপর প্রয়োগ হয় না।

///

### কোন validator pattern ব্যবহার করবেন { #which-validator-pattern-to-use }

দুটো পদ্ধতি দিয়েই একই কাজ করা যায়, তবে প্রতিটির নিজস্ব সুবিধা আছে।

#### annotated pattern ব্যবহার { #using-the-annotated-pattern }

[annotated pattern](./fields.md#the-annotated-pattern)-এর একটি বড় সুবিধা হলো
validator বারবার ব্যবহার (reuse) করা যায়:

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} is not an even number')
    return value


EvenNumber = Annotated[int, AfterValidator(is_even)]


class Model1(BaseModel):
    my_number: EvenNumber


class Model2(BaseModel):
    other_number: Annotated[EvenNumber, AfterValidator(lambda v: v + 2)]


class Model3(BaseModel):
    list_of_even_numbers: list[EvenNumber]  # (1)!
```

1. [annotated pattern](./fields.md#the-annotated-pattern) ডকুমেন্টেশনে যেমন বলা আছে,
   annotation-এর নির্দিষ্ট অংশের জন্যও validator ব্যবহার করা যায় (এখানে
   যাচাই প্রয়োগ হচ্ছে তালিকার প্রতিটি আইটেমে, পুরো তালিকায় নয়)।

শুধু ফিল্ডের annotation দেখেই বোঝা যায় কোন টাইপে কোন validator প্রয়োগ হচ্ছে, এটিও একটি সুবিধা।

#### decorator pattern ব্যবহার { #using-the-decorator-pattern }

[`field_validator()`][pydantic.field_validator] decorator-এর একটি বড় সুবিধা হলো
একই ফাংশন একাধিক ফিল্ডে প্রয়োগ করা যায়:

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    f1: str
    f2: str

    @field_validator('f1', 'f2', mode='before')
    @classmethod
    def capitalize(cls, value: str) -> str:
        return value.capitalize()
```

decorator ব্যবহার নিয়ে আরও কয়েকটি কথা:

* validator সব ফিল্ডে (subclass-এ সংজ্ঞায়িত ফিল্ডসহ) প্রয়োগ করতে চাইলে, ফিল্ডের নাম হিসেবে
  `'*'` দিন।
* ডিফল্টভাবে, decorator নিশ্চিত করে যে দেওয়া ফিল্ডের নাম(গুলো) মডেলে সংজ্ঞায়িত আছে। ক্লাস তৈরির সময়
  এই পরীক্ষা বন্ধ করতে চাইলে `check_fields` আর্গুমেন্টে `False` দিন।
  এটি কাজে লাগে যখন ফিল্ড validator একটি base class-এ সংজ্ঞায়িত, আর ফিল্ডটি
  subclass-এ থাকবে বলে আশা করা হয়।

/// tip | কোনটি বেছে নেবেন

* একই নিয়ম বহু মডেলে লাগবে (যেমন "জোড় সংখ্যা", "বাংলাদেশি ফোন নম্বর")? → **annotated pattern**, একটি টাইপ বানিয়ে সব জায়গায় ব্যবহার করুন।
* একটি মডেলের কয়েকটি ফিল্ডে একই নিয়ম, বা validator-কে মডেলের সাথেই রাখতে চান? → **decorator**।

///

## মডেল validator { #model-validators }

/// details | API ডকুমেন্টেশন
    type: info

[`pydantic.functional_validators.model_validator`][pydantic.functional_validators.model_validator]<br>

///

[`model_validator()`][pydantic.model_validator] decorator দিয়ে পুরো মডেলের ডেটার ওপরও
যাচাই করা যায়। একাধিক ফিল্ড মিলিয়ে দেখতে হলে (যেমন "পাসওয়ার্ড আর নিশ্চিত-পাসওয়ার্ড একই কিনা") এটিই ঠিক জায়গা।

**তিন** ধরনের মডেল validator ব্যবহার করা যায়:

* ***After* validator**: পুরো মডেল যাচাই হওয়ার পরে চলে। তাই এগুলো
  *instance* মেথড হিসেবে সংজ্ঞায়িত হয়, আর এদের initialization-পরবর্তী hook হিসেবে ভাবা যায়। গুরুত্বপূর্ণ: যাচাই করা
  instance-টি ফেরত দিতে হবে।
{% raw %}  {#model-after-validator}{% endraw %}

    ```python
    from typing_extensions import Self

    from pydantic import BaseModel, model_validator


    class UserModel(BaseModel):
        username: str
        password: str
        password_repeat: str

        @model_validator(mode='after')
        def check_passwords_match(self) -> Self:
            if self.password != self.password_repeat:
                raise ValueError('Passwords do not match')
            return self
    ```

* ***Before* validator**: মডেল তৈরি হওয়ার আগে চলে। এগুলো *after* validator-এর চেয়ে নমনীয়,
  কিন্তু এদের কাঁচা ইনপুট সামলাতে হয়, যা তাত্ত্বিকভাবে যেকোনো অবজেক্ট হতে পারে। validator ফাংশনে পরে
  [যাচাই এরর](#raising-validation-errors) তুলতে পারেন এমন হলে মানটি সরাসরি বদলানো এড়িয়ে চলুন,
  কারণ [union](./unions.md) ব্যবহার করলে বদলানো মান অন্য validator-এর কাছে চলে যেতে পারে।
{% raw %}  {#model-before-validator}{% endraw %}

    ```python
    from typing import Any

    from pydantic import BaseModel, model_validator


    class UserModel(BaseModel):
        username: str

        @model_validator(mode='before')
        @classmethod
        def check_card_number_not_present(cls, data: Any) -> Any:  # (1)!
            if isinstance(data, dict):  # (2)!
                if 'card_number' in data:
                    raise ValueError("'card_number' should not be included")
            return data
    ```

    1. লক্ষ করুন, `data`-এর টাইপ হিসেবে [`Any`][typing.Any] দেওয়া হয়েছে। *Before* validator কাঁচা ইনপুট নেয়, যা
       যেকোনো কিছু হতে পারে।
    2. বেশিরভাগ সময় ইনপুট ডেটা একটি ডিকশনারি হবে (যেমন `UserModel(username='...')` ডাকলে)। তবে
       সবসময় তা নয়। যেমন, [`from_attributes`][pydantic.ConfigDict.from_attributes]
       কনফিগারেশন সেট থাকলে `data` আর্গুমেন্টে যেকোনো ক্লাসের instance আসতে পারে।

* ***Wrap* validator**: সবচেয়ে নমনীয়। Pydantic আর
  অন্য validator ইনপুট ডেটা প্রক্রিয়া করার আগে বা পরে কোড চালাতে পারেন, অথবা আগেভাগে ডেটা ফেরত দিয়ে
  বা এরর তুলে সাথে সাথে যাচাই শেষ করতে পারেন।
{% raw %}  {#model-wrap-validator}{% endraw %}

    ```python
    import logging
    from typing import Any

    from typing_extensions import Self

    from pydantic import BaseModel, ModelWrapValidatorHandler, ValidationError, model_validator


    class UserModel(BaseModel):
        username: str

        @model_validator(mode='wrap')
        @classmethod
        def log_failed_validation(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
            try:
                return handler(data)
            except ValidationError:
                logging.error('Model %s failed to validate with data %s', cls, data)
                raise
    ```

/// note | উত্তরাধিকার (inheritance) নিয়ে

base class-এ সংজ্ঞায়িত মডেল validator subclass-এর instance যাচাইয়ের সময়ও ডাকা হবে।

subclass-এ একই নামের মডেল validator লিখলে (override করলে) base class-এর validator বাতিল হয়, ফলে শুধু subclass-এর সংস্করণটিই ডাকা হবে।

///

## যাচাই এরর তোলা { #raising-validation-errors }

যাচাই এরর তুলতে তিন ধরনের এক্সেপশন ব্যবহার করা যায়:

* [`ValueError`][]: validator-এর ভেতরে সবচেয়ে বেশি এটিই তোলা হয়।
* [`AssertionError`][]: [assert][] স্টেটমেন্টও কাজ করে, তবে মনে রাখুন Python
  [-O][] অপ্টিমাইজেশন ফ্ল্যাগ দিয়ে চালালে এই স্টেটমেন্টগুলো বাদ পড়ে যায়।
* [`PydanticCustomError`][pydantic_core.PydanticCustomError]: একটু বেশি লিখতে হয়, কিন্তু বাড়তি নমনীয়তা দেয়:

    ```python
    from pydantic_core import PydanticCustomError

    from pydantic import BaseModel, ValidationError, field_validator


    class Model(BaseModel):
        x: int

        @field_validator('x', mode='after')
        @classmethod
        def validate_x(cls, v: int) -> int:
            if v % 42 == 0:
                raise PydanticCustomError(
                    'the_answer_error',
                    '{number} is the answer!',
                    {'number': v},
                )
            return v


    try:
        Model(x=42 * 2)
    except ValidationError as e:
        print(e)
        """
        1 validation error for Model
        x
          84 is the answer! [type=the_answer_error, input_value=84, input_type=int]
        """
    ```

/// info | কোডটি সহজ ভাষায়

`PydanticCustomError`-এর তিনটি অংশ: এররের ধরন (`'the_answer_error'`, যা `type=` হিসেবে দেখায়), বার্তার ছাঁচ (`'{number} is the answer!'`), আর ছাঁচের ফাঁকা ঘর পূরণের ডিকশনারি (`{'number': v}`)। ফলে API-র ক্লায়েন্ট এররের ধরন দেখে প্রোগ্রাম দিয়েই বুঝতে পারে কী ভুল হয়েছে।

///

/// warning | সাধারণ ভুল

validator-এর ভেতরে `ValidationError` নিজে তুলবেন না; `ValueError` বা `PydanticCustomError` তুলুন, Pydantic সেটিকে নিজে `ValidationError`-এ মুড়ে দেবে।

///

প্রোডাকশনে কোনো validator ডেটা প্রত্যাখ্যান করলে, [Logfire](../errors/troubleshooting.md) তার গোছানো এরর তথ্যে
প্রত্যাখ্যাত মানটি রেকর্ড করতে পারে, ফলে দেখতে পারবেন কোন নিয়ম ভাঙল।

## যাচাইয়ের তথ্য (Validation info) { #validation-info }

ফিল্ড আর মডেল দুই ধরনের validator callable-ই (সব মোডে) চাইলে একটি বাড়তি
[`ValidationInfo`][pydantic.ValidationInfo] আর্গুমেন্ট নিতে পারে, যা দরকারি বাড়তি তথ্য দেয়, যেমন:

* [ইতিমধ্যে যাচাই হওয়া ডেটা](#validation-data)
* [ব্যবহারকারীর দেওয়া context](#validation-context)
* বর্তমান [যাচাই মোড](./models.md#validating-data): `'python'`, `'json'` অথবা `'strings'` (দেখুন [`mode`][pydantic.ValidationInfo.mode] property)
* বর্তমান ফিল্ডের নাম, যদি [ফিল্ড validator](#field-validators) হয় (দেখুন [`field_name`][pydantic.ValidationInfo.field_name] property)।

### যাচাই হওয়া ডেটা { #validation-data }

ফিল্ড validator-এ, ইতিমধ্যে যাচাই হওয়া ডেটা [`data`][pydantic.ValidationInfo.data]
property দিয়ে পাওয়া যায়। এখানে একটি উদাহরণ, যা ওপরের [*after* মডেল validator](#model-after-validator)
উদাহরণের বিকল্প হিসেবে ব্যবহার করা যায়:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class UserModel(BaseModel):
    password: str
    password_repeat: str
    username: str

    @field_validator('password_repeat', mode='after')
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data['password']:
            raise ValueError('Passwords do not match')
        return value
```

/// warning | সতর্কতা

যাচাই হয় [ফিল্ড যে ক্রমে সংজ্ঞায়িত](./models.md#field-ordering) সেই ক্রমে, তাই
খেয়াল রাখতে হবে যেন এখনো যাচাই হয়নি এমন ফিল্ড পড়তে না যান। যেমন ওপরের কোডে
`username`-এর যাচাই করা মান এখনো পাওয়া যায় না, কারণ এটি `password_repeat`-এর *পরে* সংজ্ঞায়িত।

///

[মডেল validator](#model-validators)-এর ক্ষেত্রে [`data`][pydantic.ValidationInfo.data] property `None` থাকে।

### যাচাইয়ের context { #validation-context }

[যাচাই মেথডগুলোতে](./models.md#validating-data) একটি context অবজেক্ট পাঠাতে পারেন, যা
validator ফাংশনের ভেতরে [`context`][pydantic.ValidationInfo.context] property দিয়ে পাওয়া যায়:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Model(BaseModel):
    text: str

    @field_validator('text', mode='after')
    @classmethod
    def remove_stopwords(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v


data = {'text': 'This is an example document'}
print(Model.model_validate(data))  # no context
#> text='This is an example document'
print(Model.model_validate(data, context={'stopwords': ['this', 'is', 'an']}))
#> text='example document'
```

/// tip | উদাহরণ দিয়ে বুঝি

context হলো পরিদর্শকের হাতে দেওয়া একটি চিরকুট: "আজ এই শব্দগুলো বাদ দিও"। মডেলের গঠন না বদলেই একই validator ভিন্ন ভিন্ন পরিস্থিতিতে ভিন্নভাবে কাজ করে।

///

একইভাবে, [সিরিয়ালাইজেশনেও context ব্যবহার](../concepts/serialization.md#serialization-context) করা যায়।

/// details | সরাসরি মডেল তৈরির সময় context দেওয়া
    type: note

সরাসরি মডেল তৈরির সময় (অর্থাৎ `Model(...)` ডাকলে) এখন context দেওয়া সম্ভব নয়।
একটি [`ContextVar`][contextvars.ContextVar] আর নিজের `__init__` মেথড দিয়ে এর বিকল্প ব্যবস্থা করা যায়:

```python
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from pydantic import BaseModel, ValidationInfo, field_validator

_init_context_var = ContextVar('_init_context_var', default=None)


@contextmanager
def init_context(value: dict[str, Any]) -> Generator[None]:
    token = _init_context_var.set(value)
    try:
        yield
    finally:
        _init_context_var.reset(token)


class Model(BaseModel):
    my_number: int

    def __init__(self, /, **data: Any) -> None:
        self.__pydantic_validator__.validate_python(
            data,
            self_instance=self,
            context=_init_context_var.get(),
        )

    @field_validator('my_number')
    @classmethod
    def multiply_with_context(cls, value: int, info: ValidationInfo) -> int:
        if isinstance(info.context, dict):
            multiplier = info.context.get('multiplier', 1)
            value = value * multiplier
        return value


print(Model(my_number=2))
#> my_number=2

with init_context({'multiplier': 3}):
    print(Model(my_number=2))
    #> my_number=6

print(Model(my_number=2))
#> my_number=2
```

///

## validator-এর ক্রম { #ordering-of-validators }

[annotated pattern](#using-the-annotated-pattern) ব্যবহার করলে validator যে ক্রমে প্রয়োগ হয়
তা এরকম: [*before*](#field-before-validator) আর [*wrap*](#field-wrap-validator) validator
ডান থেকে বামে চলে, তারপর [*after*](#field-after-validator) validator বাম থেকে ডানে চলে:

```python
from pydantic import AfterValidator, BaseModel, BeforeValidator, WrapValidator


class Model(BaseModel):
    name: Annotated[
        str,
        AfterValidator(runs_3rd),
        AfterValidator(runs_4th),
        BeforeValidator(runs_2nd),
        WrapValidator(runs_1st),
    ]
```

/// tip | উদাহরণ দিয়ে বুঝি

পেঁয়াজের খোসার মতো ভাবুন। ডানের *before*/*wrap* হলো বাইরের খোসা, তাই ইনপুট সবার আগে সেখানে পৌঁছায়, তারপর ভেতরের দিকে (বামে) যায়। মাঝখানে Pydantic নিজের যাচাই করে। তারপর *after* validator-গুলো বাম থেকে ডানে, যে ক্রমে লেখা সেই ক্রমেই চলে।

///

ভেতরে ভেতরে, [decorator](#using-the-decorator-pattern) দিয়ে সংজ্ঞায়িত validator-গুলো তাদের annotated
রূপে রূপান্তরিত হয় আর ফিল্ডের আগের metadata-র পরে, সবশেষে যোগ হয়। অর্থাৎ ক্রমের
একই নিয়ম এখানেও খাটে।

## বিশেষ টাইপ { #special-types }

যাচাই নিজের মতো করতে Pydantic কয়েকটি বিশেষ ইউটিলিটি দেয়।

* [`InstanceOf`][pydantic.functional_validators.InstanceOf] দিয়ে যাচাই করা যায় যে একটি মান নির্দিষ্ট ক্লাসের instance কিনা।

    ```python
    from pydantic import BaseModel, InstanceOf, ValidationError


    class Fruit:
        def __repr__(self):
            return self.__class__.__name__


    class Banana(Fruit): ...


    class Apple(Fruit): ...


    class Basket(BaseModel):
        fruits: list[InstanceOf[Fruit]]


    print(Basket(fruits=[Banana(), Apple()]))
    #> fruits=[Banana, Apple]
    try:
        Basket(fruits=[Banana(), 'Apple'])
    except ValidationError as e:
        print(e)
        """
        1 validation error for Basket
        fruits.1
          Input should be an instance of Fruit [type=is_instance_of, input_value='Apple', input_type=str]
        """
    ```

* [`SkipValidation`][pydantic.functional_validators.SkipValidation] দিয়ে একটি ফিল্ডের যাচাই বাদ দেওয়া যায়।

    ```python
    from pydantic import BaseModel, SkipValidation


    class Model(BaseModel):
        names: list[SkipValidation[str]]


    m = Model(names=['foo', 'bar'])
    print(m)
    #> names=['foo', 'bar']

    m = Model(names=['foo', 123])  # (1)!
    print(m)
    #> names=['foo', 123]
    ```

    1. লক্ষ করুন, দ্বিতীয় আইটেমের যাচাই বাদ পড়েছে। টাইপ ভুল হলে সিরিয়ালাইজেশনের সময়
       একটি সতর্কবার্তা দেখাবে।

* [`ValidateAs`][pydantic.functional_validators.ValidateAs] দিয়ে Pydantic নিজে সমর্থন করে এমন একটি টাইপের মাধ্যমে
  নিজের একটি টাইপ যাচাই করা যায়। একাধিক ফিল্ডওয়ালা নিজের টাইপের ক্ষেত্রে এটি বিশেষভাবে কাজে লাগে।

    ```python
    from typing import Annotated

    from pydantic import BaseModel, TypeAdapter, ValidateAs

    class MyCls:
        def __init__(self, a: int) -> None:
            self.a = a

        def __repr__(self) -> str:
            return f"MyCls(a={self.a})"

    class ValModel(BaseModel):
        a: int


    ta = TypeAdapter(
        Annotated[MyCls, ValidateAs(ValModel, lambda v: MyCls(a=v.a))]
    )

    print(ta.validate_python({'a': 1}))
    #> MyCls(a=1)
    ```

* [`PydanticUseDefault`][pydantic_core.PydanticUseDefault] দিয়ে Pydantic-কে জানানো যায় যে ডিফল্ট মানটি
  ব্যবহার করতে হবে।

    ```python
    from typing import Annotated, Any

    from pydantic_core import PydanticUseDefault

    from pydantic import BaseModel, BeforeValidator


    def default_if_none(value: Any) -> Any:
        if value is None:
            raise PydanticUseDefault()
        return value


    class Model(BaseModel):
        name: Annotated[str, BeforeValidator(default_if_none)] = 'default_name'


    print(Model(name=None))
    #> name='default_name'
    ```

## JSON Schema আর ফিল্ড validator { #json-schema-and-field-validators }

[*before*](#field-before-validator), [*plain*](#field-plain-validator) বা [*wrap*](#field-wrap-validator)
ফিল্ড validator ব্যবহার করলে, গ্রহণযোগ্য ইনপুট টাইপ ফিল্ডের annotation থেকে আলাদা হতে পারে।

এই উদাহরণটি দেখুন:

```python
from typing import Any

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    value: str

    @field_validator('value', mode='before')
    @classmethod
    def cast_ints(cls, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)
        else:
            return value


print(Model(value='a'))
#> value='a'
print(Model(value=1))
#> value='1'
```

`value`-এর টাইপ hint `str` হলেও, `cast_ints` validator পূর্ণসংখ্যাও গ্রহণ করে। সঠিক
ইনপুট টাইপ জানাতে `json_schema_input_type` আর্গুমেন্ট দেওয়া যায়:

```python
from typing import Any

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    value: str

    @field_validator('value', mode='before', json_schema_input_type=int | str)
    @classmethod
    def cast_ints(cls, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)
        else:
            return value


print(Model.model_json_schema()['properties']['value'])
#> {'anyOf': [{'type': 'integer'}, {'type': 'string'}], 'title': 'Value'}
```

সুবিধার জন্য, আর্গুমেন্টটি না দিলে Pydantic ফিল্ডের টাইপই ব্যবহার করবে (তবে
[*plain*](#field-plain-validator) validator হলে `json_schema_input_type`-এর ডিফল্ট
[`Any`][typing.Any], কারণ সেক্ষেত্রে ফিল্ডের টাইপ পুরোপুরি উপেক্ষা করা হয়)।

/// check | সংক্ষেপে মনে রাখুন

* বেশিরভাগ ক্ষেত্রে *after* validator: টাইপ ঠিক হওয়ার পরে বাড়তি শর্ত; মান ফেরত দিতে ভুলবেন না।
* কাঁচা ইনপুট গুছাতে *before*, পুরো যাচাই নিজে করতে *plain*, আগে-পরে দুটো নিয়ন্ত্রণে *wrap* (`handler` সহ)।
* বারবার ব্যবহারে `Annotated[..., AfterValidator(...)]`; একাধিক ফিল্ডে `@field_validator('a', 'b')`।
* একাধিক ফিল্ড মিলিয়ে দেখতে `@model_validator(mode='after')`।
* এরর তুলতে `ValueError`; আগের ফিল্ড পেতে `info.data`, বাড়তি তথ্যে `info.context`।

///
