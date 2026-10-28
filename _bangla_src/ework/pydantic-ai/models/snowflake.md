# Snowflake Cortex { #snowflake-cortex }

/// note | এই পেজে যা শিখবেন

* আপনার Snowflake account-এর ভেতরেই Claude, GPT, Llama ইত্যাদি চালাতে `SnowflakeModel` ব্যবহার।
* account identifier আর token দিয়ে কনফিগারেশন, মডেলের সক্ষমতা আর thinking।

///

## ইনস্টল { #install }


Snowflake Cortex [`service_tier`][pydantic_ai.settings.ModelSettings.service_tier] উপেক্ষা না করে একটি এরর দিয়ে প্রত্যাখ্যান করে, তাই Snowflake মডেলে সেই সেটিং সেট করবেন না।
[`SnowflakeModel`][pydantic_ai.models.snowflake.SnowflakeModel] ব্যবহার করতে, হয় `pydantic-ai` ইনস্টল করুন, নয়তো `snowflake` ঐচ্ছিক group-সহ `pydantic-ai-slim`:

/// tab | pip

```bash
pip install "pydantic-ai-slim[snowflake]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-slim[snowflake]"
```

///


## কনফিগারেশন { #configuration }

[Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api) আপনার Snowflake account-এ হোস্ট করা একটি REST API দিয়ে Claude, GPT, Llama, Mistral, DeepSeek আর Snowflake-এর নিজের মডেল দেয়, তাই ডেটা কখনো Snowflake-এর নিরাপত্তা-সীমানার বাইরে যায় না।

এটি ব্যবহার করতে, আপনার [Snowflake account identifier](https://docs.snowflake.com/en/user-guide/admin-account-identifier) (যেমন `myorg-myaccount`) আর একটি token লাগবে: একটি [programmatic access token](https://docs.snowflake.com/en/user-guide/programmatic-access-tokens) (PAT), OAuth token, বা key-pair JWT। যে role হিসেবে রিকোয়েস্ট চলে — একটি PAT যে role-এ সীমিত, বা অন্যথায় আপনার user-এর ডিফল্ট role — তার `SNOWFLAKE.CORTEX_USER` database role থাকতে হবে, যা [ডিফল্টভাবে `PUBLIC`-কে দেওয়া থাকে](https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql#required-privileges)।

উপলব্ধ মডেলের তালিকার জন্য দেখুন [Cortex REST API ডকুমেন্টেশন](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api)। [Fine-tune করা মডেল](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-finetuning) `database.schema.model` হিসেবে রেফারেন্স দেওয়া যায়।

## Environment variable { #environment-variables }

account identifier আর token পাওয়ার পরে, সেগুলো environment variable হিসেবে সেট করতে পারেন:

⟦CODE1⟧

তারপর নাম দিয়ে [`SnowflakeModel`][pydantic_ai.models.snowflake.SnowflakeModel] ব্যবহার করতে পারেন:

⟦CODE2⟧

অথবা শুধু মডেলের নাম দিয়ে সরাসরি মডেলটি তৈরি করুন:

⟦CODE3⟧

## `provider` আর্গুমেন্ট { #provider-argument }

`provider` আর্গুমেন্ট দিয়ে একটি নিজের `Provider` দিতে পারেন:

⟦CODE4⟧

একটি নিজের `base_url` (যেমন [private connectivity](https://docs.snowflake.com/en/user-guide/private-snowflake-service) দিয়ে সংযোগের সময়) বা `httpx2.AsyncClient` দিয়েও [`SnowflakeProvider`][pydantic_ai.providers.snowflake.SnowflakeProvider] নিজের মতো করতে পারেন:

⟦CODE5⟧

## মডেলের সক্ষমতা { #model-capabilities }

Cortex টুল কলিং আর structured output সমর্থন করে শুধু OpenAI (`openai-*`) আর Claude (`claude-*`) মডেলে; অন্য মডেল পরিবারে, structured output [prompted output](../output.md#prompted-output)-এ ফিরে যায়।

## Thinking { #thinking }

Claude মডেলে thinking চালু করতে, একীভূত [`thinking`][pydantic_ai.settings.ModelSettings.thinking] [মডেল সেটিং](../agent.md#model-run-settings) ব্যবহার করুন, বা reasoning token বাজেট নিয়ন্ত্রণ করতে সরাসরি [`SnowflakeModelSettings.snowflake_reasoning`][pydantic_ai.models.snowflake.SnowflakeModelSettings.snowflake_reasoning] সেট করুন:

⟦CODE6⟧

OpenAI মডেলে, একীভূত `thinking` সেটিং বা [`openai_reasoning_effort`][pydantic_ai.models.openai.OpenAIChatModelSettings.openai_reasoning_effort] ব্যবহার করুন।

/// note | মনে রাখুন

thinking চালু থাকলে Claude-এর `temperature` ঠিক 1 হওয়া চাই, কিন্তু রিকোয়েস্ট একটি না দিলে Cortex একটি ভিন্ন ডিফল্ট প্রয়োগ করে, তাই reasoning চালু থাকলে আর আপনি স্পষ্টভাবে সেট না করলে `SnowflakeModel` নিজে থেকে `temperature` 1-এ সেট করে।

///

/// check | সংক্ষেপে মনে রাখুন

* account identifier আর token (PAT/OAuth/JWT) environment variable-এ, তারপর `Agent('snowflake:<model>')`।
* টুল আর structured output শুধু `openai-*` আর `claude-*` মডেলে; `service_tier` সেট করবেন না।

///
