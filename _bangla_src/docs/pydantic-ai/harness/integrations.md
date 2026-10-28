
# Integration { #integrations }

/// note | এই পেজে যা শিখবেন

* Harness-এর integration capability-গুলো কী — প্রতিটি একটি বাইরের সার্ভিসের টুল এজেন্টকে দেয়।
* বিষয় অনুযায়ী সব integration-এর তালিকা, আর তালিকায় না থাকা সার্ভিস কীভাবে যুক্ত করবেন।

///

প্রতিটি integration হলো একটি [Pydantic AI Harness](index.md) capability, যা একটি এজেন্টকে একটি বাইরের সার্ভিসের টুল দেয়।
বেশিরভাগ সার্ভিসের নিজস্ব হোস্ট করা MCP সার্ভারে যুক্ত হয়, আর আপনার দেওয়া credential ঠিক করে এজেন্ট কোথায় পৌঁছাতে পারবে। অন্য যেকোনো capability-র মতো `capabilities=[...]`-এ একটি যোগ করুন।

/// tip | উদাহরণ দিয়ে বুঝি

integration হলো এজেন্টের জন্য "অফিসের চাবির গোছা" — GitHub-এর চাবি, Slack-এর চাবি, Notion-এর চাবি। আপনি যে চাবি (token) দেন, এজেন্ট শুধু সেই দরজাগুলোই খুলতে পারে। তাই token-এর অনুমতি যত সংকীর্ণ, এজেন্ট তত নিরাপদ।

///

## কোড আর ইঞ্জিনিয়ারিং { #code-and-engineering }

- [GitHub](github.md): repository, issue, pull request আর অন্য GitHub resource পড়া ও বদলানো।
- [Linear](linear.md): Linear issue, project, team আর comment পড়া ও বদলানো।
- [Macroscope](macroscope.md): একটি লোকাল [Macroscope](https://docs.macroscope.com/cli) কোড রিভিউ চালিয়ে ফলাফল এজেন্টকে দেওয়া।
- [LocalStack](localstack.md): একটি আসল অ্যাকাউন্ট ছাড়াই একটি অনুকৃত AWS environment-এ AWS সার্ভিস তৈরি আর ব্যবহার।

## ডকুমেন্ট, মেইল আর chat { #documents-mail-and-chat }

- [Google Workspace](google-workspace.md): Gmail, Calendar, Drive আর অন্য Google Workspace পণ্য ব্যবহার।
- [Notion](notion.md): একটি Notion workspace-এ কনটেন্ট খোঁজা আর বদলানো।
- [Slack](slack.md): Slack বার্তা পড়া ও পাঠানো, চ্যানেল দেখা আর canvas নিয়ে কাজ।

## গ্রাহক, বিক্রয় আর মিটিং { #customers-sales-and-meetings }

- [Day AI](day-ai.md): [Day AI](https://day.ai)-তে CRM রেকর্ড খোঁজা ও হালনাগাদ, মিটিংয়ের context পড়া আর ইমেলের খসড়া।
- [Grain](grain.md): [Grain](https://grain.com)-এ মিটিং, transcript, নোট আর deal খোঁজা ও পড়া, আর clip তৈরি ও মিটিং ট্যাগ।
- [Pylon](pylon.md): [Pylon](https://www.usepylon.com)-এ support issue, account আর contact নিয়ে কাজ।
- [StackOne](stackone.md): [StackOne](https://www.stackone.com) দিয়ে একজন ব্যবহারকারীর যুক্ত ব্যবসায়িক অ্যাপ্লিকেশনে কাজ, যেমন BambooHR, Salesforce বা Zendesk।

## Analytics আর telemetry { #analytics-and-telemetry }

- [PostHog](posthog.md): [PostHog](https://posthog.com)-এ product analytics query আর feature flag, experiment ও dashboard পরিচালনা।
- [Logfire MCP](logfire-mcp.md): [Logfire](https://pydantic.dev/logfire) telemetry query আর Logfire project পরিচালনা।

## সোশ্যাল মিডিয়া { #social-media }

- [Ordinal](ordinal.md): [Ordinal](https://www.tryordinal.com)-এ সোশ্যাল পোস্টের খসড়া, নির্ধারণ আর বিশ্লেষণ।

## এখানে তালিকায় নেই এমন একটি সার্ভিস { #a-service-not-listed-here }

সার্ভিসটি একটি MCP সার্ভার চালালে, core [MCP capability](../capabilities/mcp.md) দিয়ে এটি যুক্ত করুন। অন্য লাইব্রেরির টুলের জন্য, দেখুন [Third-Party Tools](../third-party-tools.md)।

/// check | সংক্ষেপে মনে রাখুন

* প্রতিটি integration একটি capability; বেশিরভাগ সার্ভিসের হোস্ট করা MCP সার্ভারে যুক্ত হয়।
* আপনার দেওয়া credential-ই ঠিক করে এজেন্ট কী ছুঁতে পারবে — সংকীর্ণ অনুমতির token দিন।
* তালিকায় না থাকলে: MCP সার্ভার থাকলে `MCP(url)`, নইলে থার্ড-পার্টি টুল।

///
