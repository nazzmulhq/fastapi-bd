# চক্রাকার উল্লেখ (Cyclic references) { #cyclic-references }

/// note | এই পেজে যা শিখবেন

* চক্রাকার উল্লেখ কী: ডেটা যখন ঘুরে ফিরে নিজেকেই নির্দেশ করে (১ → ২ → ৩ → ১)।
* যাচাইয়ের সময় `recursion_loop` এরর ধরে চক্র বাদ দিয়ে ফল তৈরি।
* সিরিয়ালাইজেশনের সময় "Circular reference" এরর ধরে সামলানো।

///

[চক্রাকার উল্লেখ](../concepts/models.md#cyclic-references) অংশে যেমন বলা হয়েছে, Pydantic যাচাইয়ের ইনপুটে চক্রাকার
উল্লেখ শনাক্ত করে আর একটি [`RecursionError`][]-এর বদলে `recursion_loop` এরর ধরনের একটি [`ValidationError`][pydantic_core.ValidationError]
তোলে। সিরিয়ালাইজেশনের সময়েও একই কথা, সেখানে একটি [`ValueError`][] তোলা হয়।

/// tip | উদাহরণ দিয়ে বুঝি

দুটি আয়না মুখোমুখি রাখলে ছবির ভেতরে ছবি অসীম পর্যন্ত চলতে থাকে। ডেটায় যদি নোড ১-এর সন্তান ২, ২-এর সন্তান ৩, আর ৩-এর সন্তান আবার ১ হয়, তাহলে "সব সন্তান দেখাও" কাজটি কখনো শেষ হবে না। Pydantic এটি টের পেয়ে আগেই থামে আর এরর দেয়, যাতে প্রোগ্রাম ঝুলে না যায়।

///

এই উদাহরণে দেখানো হয়েছে কীভাবে validator আর serializer-এ এই এররগুলো ধরে চক্রাকার উল্লেখ বাদ দিয়ে
তবুও একটি ফল তৈরি করা যায়।

এই [`ValidationError`][pydantic_core.ValidationError] আসলে সর্বোচ্চ recursion গভীরতা পার না করেই তোলা হয় বলে,
বাকি থাকা সীমিত recursion গভীরতা নিয়ে চিন্তা না করেই এটি ধরে সামলাতে পারেন:

```python
from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import field

from pydantic import BaseModel, ValidationError, field_validator


def is_recursion_validation_error(exc: ValidationError) -> bool:
    errors = exc.errors()
    return len(errors) == 1 and errors[0]['type'] == 'recursion_loop'


@contextmanager
def suppress_recursion_validation_error() -> Generator[None]:
    try:
        yield
    except ValidationError as exc:
        if not is_recursion_validation_error(exc):
            raise exc


class Node(BaseModel):
    id: int
    children: list[Node] = field(default_factory=list)

    @field_validator('children', mode='wrap')
    @classmethod
    def drop_cyclic_references(cls, children, h):
        try:
            return h(children)
        except ValidationError as exc:
            if not (
                is_recursion_validation_error(exc)
                and isinstance(children, list)
            ):
                raise exc

            value_without_cyclic_refs = []
            for child in children:
                with suppress_recursion_validation_error():
                    value_without_cyclic_refs.extend(h([child]))
            return h(value_without_cyclic_refs)


# Create data with cyclic references representing the graph 1 -> 2 -> 3 -> 1
node_data = {'id': 1, 'children': [{'id': 2, 'children': [{'id': 3}]}]}
node_data['children'][0]['children'][0]['children'] = [node_data]

print(Node.model_validate(node_data))
#> id=1 children=[Node(id=2, children=[Node(id=3, children=[])])]
```

/// info | কোডটি সহজ ভাষায়

* `children` ফিল্ডে একটি *wrap* validator আছে। প্রথমে `h(children)` দিয়ে স্বাভাবিক যাচাইয়ের চেষ্টা।
* `recursion_loop` এরর এলে, প্রতিটি সন্তানকে আলাদা করে (`h([child])`) যাচাই করা হয়; যে সন্তান চক্র তৈরি করে, সেটির এরর চাপা দেওয়া হয় (`suppress_recursion_validation_error`), ফলে সেটি বাদ পড়ে।
* ফল: `1 → 2 → 3`, আর ৩-এর সন্তান তালিকা খালি, কারণ ৩ → ১ উল্লেখটি চক্র তৈরি করছিল।

///

একইভাবে, *সিরিয়ালাইজেশনের* সময় Pydantic একটি recursive উল্লেখ পেলে, সর্বোচ্চ recursion গভীরতা পার হওয়ার জন্য
অপেক্ষা না করে সাথে সাথে একটি [`ValueError`][] তোলে:

```python
from pydantic import TypeAdapter

# Create data with cyclic references representing the graph 1 -> 2 -> 3 -> 1
node_data = {'id': 1, 'children': [{'id': 2, 'children': [{'id': 3}]}]}
node_data['children'][0]['children'][0]['children'] = [node_data]

try:
    # Try serializing the circular reference as JSON
    TypeAdapter(dict).dump_json(node_data)
except ValueError as exc:
    print(exc)
    """
    Error serializing to JSON: ValueError: Circular reference detected (id repeated)
    """
```

চাইলে এটিও সামলানো যায়:

```python
from dataclasses import field
from typing import Any

from pydantic import (
    SerializerFunctionWrapHandler,
    TypeAdapter,
    field_serializer,
)
from pydantic.dataclasses import dataclass


@dataclass
class NodeReference:
    id: int


@dataclass
class Node(NodeReference):
    children: list['Node'] = field(default_factory=list)

    @field_serializer('children', mode='wrap')
    def serialize(
        self, children: list['Node'], handler: SerializerFunctionWrapHandler
    ) -> Any:
        """
        Serialize a list of nodes, handling circular references by excluding the children.
        """
        try:
            return handler(children)
        except ValueError as exc:
            if not str(exc).startswith('Circular reference'):
                raise exc

            result = []
            for node in children:
                try:
                    serialized = handler([node])
                except ValueError as exc:
                    if not str(exc).startswith('Circular reference'):
                        raise exc
                    result.append({'id': node.id})
                else:
                    result.append(serialized)
            return result


# Create a cyclic graph:
nodes = [Node(id=1), Node(id=2), Node(id=3)]
nodes[0].children.append(nodes[1])
nodes[1].children.append(nodes[2])
nodes[2].children.append(nodes[0])

print(nodes[0])
#> Node(id=1, children=[Node(id=2, children=[Node(id=3, children=[...])])])

# Serialize the cyclic graph:
print(TypeAdapter(Node).dump_python(nodes[0]))
"""
{
    'id': 1,
    'children': [{'id': 2, 'children': [{'id': 3, 'children': [{'id': 1}]}]}],
}
"""
```

/// info | কোডটি সহজ ভাষায়

serializer-ও *wrap* মোডে: প্রথমে `handler(children)` দিয়ে স্বাভাবিক সিরিয়ালাইজেশন। "Circular reference" এরর এলে প্রতিটি সন্তান আলাদাভাবে চেষ্টা করা হয়; যেটিতে আবার চক্র, সেটির পুরো বিবরণের বদলে শুধু `{'id': ...}` রাখা হয়। ফলে শেষে `{'id': 1}` দেখা যায়, চক্রটি সেখানেই কেটে দেওয়া।

///

/// check | সংক্ষেপে মনে রাখুন

* যাচাইয়ে চক্র: `ValidationError` যার `type` হলো `'recursion_loop'`; সিরিয়ালাইজেশনে: `ValueError` যার বার্তা `'Circular reference ...'` দিয়ে শুরু।
* wrap validator/serializer-এ এই এরর ধরে, সন্তানগুলো একে একে চেষ্টা করে চক্র তৈরি করা অংশ বাদ দিন বা ছোট রূপে (শুধু `id`) রাখুন।

///
