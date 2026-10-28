# Restate দিয়ে Durable Execution { #durable-execution-with-restate }

/// note | এই পেজে যা শিখবেন

* Restate কী আর কীভাবে এটি একটি journal দিয়ে এজেন্টকে durable করে।
* একটি durable এজেন্টের তিনটি অংশ: handler, LLM কল আর টুল চালানো।
* `RestateAgent` দিয়ে একটি সম্পূর্ণ উদাহরণ।

///

[Restate](https://restate.dev) একটি হালকা durable execution runtime, যাতে AI এজেন্টের জন্য প্রথম-শ্রেণির সমর্থন আছে। Pydantic AI ইন্টিগ্রেশন দেওয়া হয় [Restate Python SDK](https://github.com/restatedev/sdk-python/tree/main/python/restate/ext/pydantic)-এর মাধ্যমে।

আরও তথ্যের জন্য দেখুন [Restate ডকুমেন্টেশন](https://docs.restate.dev/ai/patterns/durable-agents)।

## Durable Execution { #durable-execution }

Restate আপনার এজেন্টকে **durable** করে এর চালানোর প্রতিটি ধাপ একটি journal-এ লিখে। চলার মাঝে আপনার process crash করলে, Restate journal replay করে, সম্পন্ন ধাপগুলোর লেখা ফল পুনর্ব্যবহার করে, আর যে ধাপটি চলছিল সেটি আবার চেষ্টা করে।

আপনার এজেন্ট একটি Restate **service**-এর ভেতরে একটি সাধারণ HTTP handler-এ চলে। Restate Server আপনার অ্যাপ্লিকেশনের সামনে বসে আর orchestration, journal রাখা আর retry পরিচালনা করে। Service-গুলো সাধারণ Docker container বা serverless function-এর মতো চলে।

একটি durable এজেন্টের তিনটি গঠন-একক আছে:

1. **Handler**: আপনার এজেন্ট লজিক, একটি Restate service-এ একটি HTTP endpoint হিসেবে প্রকাশিত।
2. **LLM কল**: সংরক্ষিত, যাতে উদ্ধারের সময় response আবার আনতে না হয় — খরচ আর সময় বাঁচায়।
3. **টুল চালানো**: durable ধাপে মোড়ানো, যাতে উদ্ধারের সময় একটি সম্পন্ন ধাপ আবার না চলে।

এর ফল journal-এ লেখার আগে বাধা পাওয়া একটি ধাপ retry-তে আবার চলে, এর বাইরের side effect ইতিমধ্যে ঘটে থাকলেও। side effect-যুক্ত টুল idempotent করুন, যেমন বাইরের সার্ভিসে একটি idempotency key দিয়ে।

```text
                  Clients
              (HTTP, Kafka, etc.)
                     |
                     v
            +---------------------+
            |   Restate Server    |      (Journals execution,
            +---------------------+       retries on failure,
                     ^                    manages state)
                     |
        Journal      |   Replay on
        steps,       |   recovery,
        retries      |   schedule calls
                     v
+------------------------------------------------------+
|               Application Process                    |
|   +----------------------------------------------+   |
|   |         Restate Service Handler              |   |
|   |           (Agent Run Loop)                   |   |
|   |    [ Durable Steps (Tool, MCP, Model) ]      |   |
|   +----------------------------------------------+   |
|         |           |                |               |
+------------------------------------------------------+
          |           |                |
          v           v                v
      [External APIs, services, databases, etc.]
```

দেখুন [Restate-এর durable-agent ডকুমেন্টেশন](https://docs.restate.dev/ai/patterns/durable-agents)।

/// tip | উদাহরণ দিয়ে বুঝি

Restate হলো একজন হিসাবরক্ষক যিনি আপনার অফিসের দরজায় বসে থাকেন। প্রতিটি রিকোয়েস্ট তাঁর হাত দিয়ে আসে, আর আপনার কোড যা যা করে (মডেলকে জিজ্ঞেস, টুল চালানো) তার ফল তিনি খাতায় লেখেন। আপনার সার্ভার পড়ে গেলে, তিনি রিকোয়েস্টটি আবার পাঠান — আর খাতায় লেখা ধাপগুলোর ফল সরাসরি দিয়ে দেন, যাতে সেগুলো আবার করতে না হয়।

///

## Durable এজেন্ট { #durable-agent }

যেকোনো Pydantic AI এজেন্টকে durable করা যায় Restate SDK-এর `RestateAgent` দিয়ে মুড়ে একটি Restate service handler-এর ভেতরে চালিয়ে।

Restate SDK ইনস্টল করুন:

/// tab | pip

```bash
pip install pydantic-ai "restate_sdk[serde]" hypercorn
```

///

/// tab | uv

```bash
uv add pydantic-ai "restate_sdk[serde]" hypercorn
```

///


Restate-সহ একটি durable Pydantic AI এজেন্টের একটি সম্পূর্ণ উদাহরণ:

```python title="restate_agent.py"
import restate
from pydantic_ai import Agent, RunContext
from restate.ext.pydantic import RestateAgent, restate_context

weather_agent = Agent(  # (1)!
    'openai:gpt-6.1-sol',
    instructions='You are a helpful agent that provides weather updates.',
)


@weather_agent.tool()
async def get_weather(_run_ctx: RunContext, city: str) -> dict:
    """Get the current weather for a given city."""

    # Do durable tool steps using the Restate context
    async def call_weather_api(city: str) -> dict:
        return {'temperature': 23, 'description': 'Sunny and warm.'}

    return await restate_context().run_typed(  # (2)!
        f'Get weather {city}', call_weather_api, city=city
    )


restate_agent = RestateAgent(weather_agent)  # (3)!

agent_service = restate.Service('WeatherAgent')


@agent_service.handler()
async def run(_ctx: restate.Context, prompt: str) -> str:  # (4)!
    result = await restate_agent.run(prompt)
    return result.output


app = restate.app(services=[agent_service])  # (5)!

if __name__ == "__main__":  # (6)!
    import asyncio

    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    conf = Config()
    conf.bind = ["0.0.0.0:9080"]
    asyncio.run(serve(app, conf))
```

1. Pydantic AI-তে যেমন সাধারণত করেন, তেমনই আপনার এজেন্ট আর টুল সংজ্ঞায়িত করুন।
2. টুলের চালানো durable করতে তাদের ভেতরে `restate_context()` action ব্যবহার করুন। ফল সংরক্ষিত হয় আর সফল না হওয়া পর্যন্ত retry হয়, আর উদ্ধারের সময় একটি সম্পন্ন ধাপের journal-এ লেখা ফল আবার না চালিয়ে পুনর্ব্যবহৃত হয়। এর ফল journal-এ লেখার আগে বাধা পাওয়া একটি ধাপ আবার চলে, তাই এর side effect idempotent করুন।
3. `RestateAgent` এজেন্টকে মোড়ায়, যাতে প্রতিটি LLM response Restate Server-এ সংরক্ষিত হয় আর উদ্ধারের সময় replay হয়।
4. Restate service handler এজেন্টকে একটি durable execution context দেয় আর একে একটি HTTP endpoint হিসেবে প্রকাশ করে।
5. `restate.app()` এমন অ্যাপ্লিকেশন তৈরি করে যা পরিবেশন করা যায়।
6. Hypercorn-এর মতো একটি ASGI সার্ভার দিয়ে অ্যাপ্লিকেশন চালান।

এজেন্ট কীভাবে চালাবেন তা জানতে দেখুন [Restate agent quickstart](https://docs.restate.dev/ai-quickstart)।

/// check | সংক্ষেপে মনে রাখুন

* Restate একটি journal রাখে; crash-এর পর সম্পন্ন ধাপের ফল পুনর্ব্যবহার করে, চলমানটি আবার চালায়।
* এজেন্টকে `RestateAgent` দিয়ে মুড়ে একটি Restate service handler-এ চালান।
* টুলের ভেতরের I/O `restate_context()` action-এ রাখুন, যাতে তা durable হয়।
* side-effect টুল idempotent রাখুন।
* ইনস্টল: `restate_sdk[serde]` আর একটি ASGI সার্ভার (যেমন Hypercorn)।

///
