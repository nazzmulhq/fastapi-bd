# Test Client - `TestClient` { #test-client-testclient }

/// note | এই পেজে যা পাবেন

`TestClient` ক্লাসের সব মেথড (`get`, `post`, `put`, `delete`, `websocket_connect` ইত্যাদি), যা দিয়ে সার্ভার না চালিয়েই অ্যাপ টেস্ট করা যায়।

///

আসল HTTP আর সকেট সংযোগ তৈরি না করে, শুধু সরাসরি FastAPI কোডের সাথে যোগাযোগ করে FastAPI অ্যাপ্লিকেশন টেস্ট করতে `TestClient` ক্লাস ব্যবহার করতে পারেন।

এ সম্পর্কে আরও পড়ুন [টেস্টিং নিয়ে FastAPI ডকসে](https://fastapi.tiangolo.com/tutorial/testing/)।

আপনি এটি সরাসরি `fastapi.testclient` থেকে ইম্পোর্ট করতে পারেন:

```python
from fastapi.testclient import TestClient
```

/// tip | উদাহরণ দিয়ে বুঝি

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
def home():
    return {"msg": "Hello"}


client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello"}
```

`pytest` চালালে `test_home` চলবে। `client.get("/")` আসল নেটওয়ার্ক ছাড়াই অ্যাপে রিকোয়েস্ট পাঠায়, তাই টেস্ট খুব দ্রুত হয়।

///

::: fastapi.testclient.TestClient
