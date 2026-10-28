# Fields { #fields }

/// note | এই পেজে যা পাবেন

* `Field()`-এর প্রতিটি প্যারামিটার, কাজ অনুযায়ী দলে ভাগ করে: ডিফল্ট, alias, ডকুমেন্টেশন, সংখ্যা ও স্ট্রিংয়ের শর্ত, dump নিয়ন্ত্রণ, আচরণ।
* `PrivateAttr()`, `@computed_field` আর `FieldInfo`।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

/// tip | উদাহরণ দিয়ে বুঝি

টাইপ (`price: float`) বলে ঘরে কী ধরনের তথ্য যাবে। `Field()` হলো ঘরের পাশে লেখা বাড়তি নির্দেশনা: "শূন্যের বেশি হতে হবে", "না দিলে ১ ধরো", "API-তে নাম হবে `itemPrice`", "ডকসে এই বর্ণনা দেখাও"।

///

```python
from pydantic import BaseModel, Field, PrivateAttr, computed_field


class Item(BaseModel):
    name: str = Field(min_length=2, max_length=20, description='পণ্যের নাম', examples=['কলম'])
    price: float = Field(gt=0, le=100000)
    qty: int = Field(default=1, ge=1)
    sku: str = Field(pattern=r'^[A-Z]{3}-\d{3}$')
    tags: list[str] = Field(default_factory=list)
    secret: str = Field(default='x', exclude=True, repr=False)
    _cache: dict = PrivateAttr(default_factory=dict)

    @computed_field
    @property
    def total(self) -> float:
        return self.price * self.qty


i = Item(name='কলম', price='12.5', qty=2, sku='PEN-001')
print(i)
#> name='কলম' price=12.5 qty=2 sku='PEN-001' tags=[] total=25.0
print(i.model_dump())
#> {'name': 'কলম', 'price': 12.5, 'qty': 2, 'sku': 'PEN-001', 'tags': [], 'total': 25.0}
```

লক্ষ করুন: `secret` print-এ নেই (`repr=False`), dump-এও নেই (`exclude=True`); `_cache` private, তাই কোথাও নেই; `total` হিসাব করা ফিল্ড, dump-এ আছে।

## `Field()` প্যারামিটার { #bn-field }

### ডিফল্ট মান { #bn-defaults }

| প্যারামিটার | কী করে |
| --- | --- |
| `default` | ডিফল্ট মান (প্রথম positional আর্গুমেন্টও এটিই) |
| `default_factory` | প্রতিবার নতুন ডিফল্ট বানানোর ফাংশন, যেমন `list`, `dict`, `datetime.now`; আগে যাচাই হওয়া ডেটা (`data`) নিয়েও বানাতে পারে |
| `validate_default` | ডিফল্ট মানও যাচাই করবে কিনা |

### নাম আর alias { #bn-aliases }

| প্যারামিটার | কী করে |
| --- | --- |
| `alias` | যাচাই আর dump দুই জায়গার বিকল্প নাম |
| `validation_alias` | শুধু ইনপুটে বিকল্প নাম; [`AliasPath`/`AliasChoices`](aliases.md)-ও নেয় |
| `serialization_alias` | শুধু আউটপুটে (`by_alias=True`) বিকল্প নাম |
| `alias_priority` | alias generator আর নিজের alias-এর মধ্যে কোনটি জিতবে |

### ডকুমেন্টেশন (JSON Schema) { #bn-docs }

| প্যারামিটার | কী করে |
| --- | --- |
| `title`, `description` | schema আর `/docs`-এ শিরোনাম ও বর্ণনা |
| `examples` | উদাহরণ মানের তালিকা |
| `json_schema_extra` | schema-তে বাড়তি key (ডিকশনারি বা ফাংশন) |
| `field_title_generator` | ফিল্ডের নাম থেকে শিরোনাম বানানোর ফাংশন |
| `deprecated` | ফিল্ডটি পুরনো বলে চিহ্নিত করা; ব্যবহার করলে সতর্কবার্তা |

### সংখ্যার শর্ত { #bn-number-constraints }

| প্যারামিটার | শর্ত |
| --- | --- |
| `gt` / `ge` | এর চেয়ে বড় / বড় বা সমান |
| `lt` / `le` | এর চেয়ে ছোট / ছোট বা সমান |
| `multiple_of` | এর গুণিতক হতে হবে |
| `allow_inf_nan` | `inf` আর `nan` অনুমোদিত কিনা |
| `max_digits`, `decimal_places` | `Decimal`-এর মোট অঙ্ক আর দশমিকের পরের অঙ্ক |

### স্ট্রিং আর তালিকার শর্ত { #bn-string-constraints }

| প্যারামিটার | শর্ত |
| --- | --- |
| `min_length` / `max_length` | স্ট্রিংয়ের অক্ষর বা তালিকার আইটেমের সর্বনিম্ন/সর্বোচ্চ সংখ্যা |
| `pattern` | regex-এর সাথে মিলতে হবে |
| `coerce_numbers_to_str` | সংখ্যা দিলে স্ট্রিংয়ে বদলে নেবে |

### আচরণ { #bn-behaviour }

| প্যারামিটার | কী করে |
| --- | --- |
| `strict` | এই ফিল্ডে টাইপ রূপান্তর বন্ধ |
| `frozen` | তৈরির পরে মান বদলানো যাবে না |
| `discriminator` | union-এ কোন ফিল্ড দেখে টাইপ বাছবে |
| `union_mode` | `'smart'` (ডিফল্ট) বা `'left_to_right'` |
| `fail_fast` | তালিকায় প্রথম ভুলেই থামবে |
| `init`, `init_var`, `kw_only` | শুধু dataclass-এ: `__init__`-এ থাকবে কিনা, ইত্যাদি |

### dump আর repr নিয়ন্ত্রণ { #bn-output }

| প্যারামিটার | কী করে |
| --- | --- |
| `exclude` | `model_dump()` থেকে সবসময় বাদ (যেমন পাসওয়ার্ড) |
| `exclude_if` | একটি শর্ত-ফাংশন সত্য হলে dump থেকে বাদ, যেমন `exclude_if=lambda v: v == []` |
| `repr` | `print()`/`repr()`-এ দেখাবে কিনা |

```python
from pydantic import ValidationError

try:
    Item(name='x', price=0, sku='bad')
except ValidationError as e:
    print([(er['loc'][0], er['type']) for er in e.errors()])
    #> [('name', 'string_too_short'), ('price', 'greater_than'), ('sku', 'string_pattern_mismatch')]
```

/// tip | `Annotated` রূপ

একই শর্ত `Annotated` দিয়েও লেখা যায়, আর বারবার ব্যবহারের জন্য সেটি ভালো: `Price = Annotated[float, Field(gt=0)]`, তারপর `price: Price`। বিস্তারিত: [Fields](../concepts/fields.md#the-annotated-pattern)।

///

## `PrivateAttr()` { #bn-private-attr }

`_` দিয়ে শুরু হওয়া অ্যাট্রিবিউট ফিল্ড নয়: যাচাই হয় না, dump বা schema-তে থাকে না। শুধু instance-এর ভেতরের অবস্থা রাখতে।

| প্যারামিটার | কী করে |
| --- | --- |
| `default` | ডিফল্ট মান |
| `default_factory` | প্রতিবার নতুন ডিফল্ট বানানোর ফাংশন |

## `@computed_field` { #bn-computed-field }

একটি `@property` (বা `@cached_property`)-কে dump আর serialization schema-তে ফিল্ডের মতো দেখায়। প্যারামিটার: `alias`, `title`, `description`, `examples`, `json_schema_extra`, `repr`, `exclude_if`, `deprecated`, `return_type` (ফেরত টাইপ annotation না থাকলে)।

## `FieldInfo` আর `ComputedFieldInfo` { #bn-fieldinfo }

`Model.model_fields['name']` যা ফেরত দেয়: ফিল্ডের সব তথ্য (`annotation`, `default`, `alias`, `metadata` ইত্যাদি)। নিজে সাধারণত তৈরি করতে হয় না; পড়তে কাজে লাগে, যেমন [গতিশীল মডেল](../examples/dynamic_models.md)-এ। `ModelPrivateAttr` হলো `PrivateAttr()`-এর ফল।

/// check | সংক্ষেপে মনে রাখুন

* `Field(default, gt=..., min_length=..., pattern=..., alias=..., description=..., exclude=...)`।
* পরিবর্তনযোগ্য ডিফল্টে (`list`, `dict`) `default_factory`।
* private অবস্থা: `_x = PrivateAttr()`; হিসাব করা মান: `@computed_field` + `@property`।

///

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
