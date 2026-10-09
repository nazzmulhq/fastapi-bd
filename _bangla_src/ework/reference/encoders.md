# Encoders - `jsonable_encoder` { #encoders-jsonable-encoder }

/// note | এই পেজে যা পাবেন

`jsonable_encoder` ফাংশনের সব প্যারামিটার। এই ফাংশন যেকোনো ডেটাকে (Pydantic মডেল, `datetime`, `UUID` ইত্যাদি) JSON-এ রাখা যায় এমন সাধারণ রূপে (`dict`, `list`, `str`, সংখ্যা) রূপান্তর করে।

///

/// tip | উদাহরণ দিয়ে বুঝি

```python
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel


class Item(BaseModel):
    title: str
    timestamp: datetime


item = Item(title="বই", timestamp=datetime(2024, 1, 1))
data = jsonable_encoder(item)
# data == {"title": "বই", "timestamp": "2024-01-01T00:00:00"}
```

`datetime` অবজেক্ট সরাসরি JSON-এ রাখা যায় না, তাই এটি ISO ফরম্যাটের স্ট্রিং হয়ে গেল। ডেটাবেসে সংরক্ষণের আগে এটি খুব কাজে লাগে। বিস্তারিত দেখুন [JSON উপযোগী এনকোডার](../tutorial/encoder.md) পেজে।

///

::: fastapi.encoders.jsonable_encoder
