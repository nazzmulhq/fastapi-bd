# Google Cloud { #google-cloud }

/// note | এই পেজে যা শিখবেন

* Google Cloud (Vertex AI) দিয়ে Gemini, Model Garden মডেল আর Claude ব্যবহার।
* প্রমাণীকরণের তিন উপায়: Application Default Credentials, service account, API key।
* location/project নিজের মতো করা।

///

[`GoogleModel`][pydantic_ai.models.google.GoogleModel] দিয়ে Gemini আর অন্য সমর্থিত Model Garden মডেল, বা [`AnthropicModel`][pydantic_ai.models.anthropic.AnthropicModel] দিয়ে Claude ব্যবহার করুন। Google Cloud-এর মডেল API Vertex AI নামেও পরিচিত।

| মডেল | কনফিগারেশন | মডেল বাছাই |
| --- | --- | --- |
| Gemini | [`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider] | `google-cloud:<model-name>` |
| `generateContent` API-সহ Model Garden মডেল | [Model Garden](#model-garden) | `GoogleCloudProvider`-সহ `GoogleModel` |
| Claude | [Vertex AI-র জন্য Anthropic client](#claude-on-google-cloud) | `AnthropicProvider`-সহ `AnthropicModel` |

বদলে Google AI Studio দিয়ে Gemini-র জন্য দেখুন [Google's Gemini API](google.md#api-key-gemini-api)।

## ইনস্টল { #install }

`GoogleModel` ব্যবহার করা Gemini আর Model Garden মডেলের জন্য, `google` ঐচ্ছিক group ইনস্টল করুন:

/// tab | pip

```bash
pip install "pydantic-ai-slim[google]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[google]"
```

///


## প্রমাণীকরণ { #authentication }

Gemini API-র তুলনায়, Google Cloud-এ Gemini-র কয়েকটি সুবিধা আছে:

1. Google Cloud API বেশি enterprise-প্রস্তুতির নিশ্চয়তা দেয়।
2. ক্ষমতা নিশ্চিত করতে Google Cloud-এ [provisioned throughput কিনতে](https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput#purchase-provisioned-throughput) পারেন।
3. Google Cloud-এর ভেতরে Pydantic AI চালালে, প্রমাণীকরণ সেট আপ করতে হয় না, এটি "এমনিতেই কাজ করা" উচিত।
4. কোন region ব্যবহার করবেন তা ঠিক করতে পারেন, যা নিয়ন্ত্রক দৃষ্টিকোণ থেকে গুরুত্বপূর্ণ হতে পারে, আর দেরি কমাতে পারে।

[application default credentials](https://cloud.google.com/docs/authentication/application-default-credentials), একটি service account, বা একটি [API key](https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys?usertype=expressmode) দিয়ে প্রমাণীকরণ করতে পারেন।

যেভাবেই প্রমাণীকরণ করুন, আপনার Google Cloud account-এ Vertex AI API (এখন Google Cloud AI নামে) চালু থাকতে হবে।

/// tip | কোনটি বাছবেন?

* নিজের কম্পিউটারে শেখার সময়: `gcloud auth application-default login` চালিয়ে ADC — সবচেয়ে সহজ।
* সার্ভারে (Google Cloud-এর বাইরে): service account JSON ফাইল।
* দ্রুত পরীক্ষা: Express Mode-এর API key।

///

### Application Default Credentials { #application-default-credentials }

আপনি [application default credentials](https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment) সেট আপ করে থাকলে, যেমন [`gcloud` CLI](https://cloud.google.com/sdk/gcloud) দিয়ে `gcloud auth application-default login` চালিয়ে, বা Google Cloud-এ চালালে, নাম দিয়ে `GoogleCloudProvider` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('google-cloud:gemini-3.8-flash')
...
```

/// tip | পরামর্শ

কণ্ঠের এজেন্টের জন্য, বদলে Vertex AI-তে একটি [realtime session](../realtime/gemini.md)-সহ একটি Gemini Live মডেল ব্যবহার করুন।

///

অথবা স্পষ্টভাবে provider আর মডেল তৈরি করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider()
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

### Service account { #service-account }

একটি service account JSON ফাইল ব্যবহার করতে, স্পষ্টভাবে provider আর মডেল তৈরি করুন:

```python title="google_model_service_account.py"
from google.oauth2 import service_account

from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

credentials = service_account.Credentials.from_service_account_file('path/to/service-account.json')
provider = GoogleCloudProvider(credentials=credentials, project='your-project-id')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

/// note | Credential scope

[`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider] scope চাওয়া credential-এ নিজে থেকে
`https://www.googleapis.com/auth/cloud-platform` প্রয়োগ করে। বিদ্যমান scope রক্ষিত থাকে।

///

### API key { #api-key }

একটি API key দিয়ে Google Cloud ব্যবহার করতে, [একটি key তৈরি করুন](https://cloud.google.com/vertex-ai/generative-ai/docs/start/api-keys?usertype=expressmode) আর এটি একটি environment variable হিসেবে সেট করুন:

```bash
export GOOGLE_API_KEY=your-api-key
```

তারপর নাম দিয়ে [`GoogleCloudProvider`][pydantic_ai.providers.google_cloud.GoogleCloudProvider]-এর মাধ্যমে `GoogleModel` ব্যবহার করতে পারেন:

```python
from pydantic_ai import Agent

agent = Agent('google-cloud:gemini-3.8-flash')
...
```

অথবা স্পষ্টভাবে provider আর মডেল তৈরি করতে পারেন:

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(api_key='your-api-key')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

/// note | প্রমাণীকরণের অগ্রাধিকার

স্পষ্ট `credentials` credential-ভিত্তিক প্রমাণীকরণ বাছে। স্পষ্ট `project` বা `location`
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials) বাছে।
`GOOGLE_APPLICATION_CREDENTIALS`-ও environment-এর একটি API key-র ওপর অগ্রাধিকার পায়।
`GOOGLE_CLOUD_PROJECT` আর `GOOGLE_CLOUD_LOCATION` ADC পথ কনফিগার করে কিন্তু নিজে থেকে
environment-এর API key override করে না। স্পষ্ট ADC আর্গুমেন্ট ছাড়া, একটি স্পষ্ট `api_key`
Express Mode বাছে।

///

### Location বা project নিজের মতো করা { #customizing-location-or-project }

Google Cloud ব্যবহারের সময় location আর/বা project নির্দিষ্ট করতে পারেন:

```python title="google_model_location.py"
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(location='global', project='your-google-cloud-project-id')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

[`GoogleCloudLocation`][pydantic_ai.providers.google.GoogleCloudLocation]-এ তালিকাভুক্ত একক-region মানের পাশাপাশি, `GoogleCloudProvider`
`'global'` location আর `'us'`/`'eu'` multi-region নেয়। multi-region মানগুলো
`aiplatform.{us,eu}.rep.googleapis.com` data-residency endpoint-এ পাঠানো হয় — এগুলো ব্যবহার করুন যখন একটি প্রতিষ্ঠানের নীতি data residency-র জন্য
global endpoint আটকায়, বা যখন একটি মডেল শুরুতে একটি একক region নয়, শুধু `global` আর
multi-region-এ পাওয়া যায়। মডেলের প্রাপ্যতা একক region, multi-region
আর `global`-এর মধ্যে আলাদা; দেখুন
[Vertex AI locations ডক](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#available-regions)।

```python title="google_model_multi_region.py"
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(location='us', project='your-google-cloud-project-id')
model = GoogleModel('gemini-3.8-flash', provider=provider)
agent = Agent(model)
...
```

## Model Garden { #model-garden }

`generateContent` API সমর্থন করা আর আপনার Google Cloud project-এর অধীনে উপলব্ধ [Model Garden](https://cloud.google.com/model-garden?hl=en)-এর মডেলে পৌঁছাতে পারেন, Gemini-সহ কিন্তু তাতেই সীমিত নয়, নিচের `model_name` ধরনের একটি দিয়ে:

- Gemini মডেলের জন্য `{model_id}`
- `{publisher}/{model_id}`
- `publishers/{publisher}/models/{model_id}`
- `projects/{project}/locations/{location}/publishers/{publisher}/models/{model_id}`

```python
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

provider = GoogleCloudProvider(
    project='your-google-cloud-project-id',
    location='us-central1',  # the region where the model is available
)
model = GoogleModel('meta/llama-3.3-70b-instruct-maas', provider=provider)
agent = Agent(model)
...
```

## মডেল সেটিং আর সুবিধা { #model-settings-and-features }

Google Cloud-এ Gemini Gemini API-র মতো একই [`GoogleModelSettings`][pydantic_ai.models.google.GoogleModelSettings] ব্যবহার করে। thinking, safety সেটিং, multimodal ইনপুট আর context caching-এর জন্য, দুই সার্ভিসের পার্থক্যসহ, দেখুন [Google model guide](google.md#model-settings)।

Google Cloud [service tier আর provisioned throughput](google.md#service-tier-service_tier-google_cloud_service_tier) আর [Model Armor](google.md#model-armor-google-cloud-only)-ও সমর্থন করে।

## Google Cloud-এ Claude { #claude-on-google-cloud }

Claude-এর জন্য, `anthropic` ঐচ্ছিক group ইনস্টল করুন আর [`AnthropicProvider`][pydantic_ai.providers.anthropic.AnthropicProvider]-এ একটি `AsyncAnthropicVertex` client দিন। সেটআপের উদাহরণের জন্য দেখুন [Claude on Google Cloud](anthropic.md#google-cloud)। এটি Anthropic-এর Messages API ব্যবহার করে, তাই [Anthropic model settings](anthropic.md#model-settings) দিয়ে কনফিগার করুন।

/// check | সংক্ষেপে মনে রাখুন

* `Agent('google-cloud:gemini-...')`; Vertex AI API চালু থাকতে হবে।
* প্রমাণীকরণ: ADC, service account, বা API key (Express Mode)।
* `location='global'`, `'us'`, `'eu'` বা একক region; Model Garden-এর মডেল `publisher/model_id` দিয়ে।
* Claude-এর জন্য `AsyncAnthropicVertex` client-সহ `AnthropicModel`।

///
