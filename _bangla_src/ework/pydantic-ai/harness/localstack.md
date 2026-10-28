
# LocalStack { #localstack }

/// note | এই পেজে যা শিখবেন

* `LocalStack` দিয়ে এজেন্টকে একটি অনুকৃত AWS environment দেওয়া — আসল অ্যাকাউন্ট না ছুঁয়ে S3, DynamoDB, SQS ইত্যাদি তৈরি আর পরীক্ষা।
* `aws_cli` আর `localstack_health` টুল, সার্ভিস নিয়ন্ত্রণ, container পরিচালনা আর durable execution।

///

`LocalStack` একটি এজেন্টকে একটি অনুকৃত AWS environment-এ প্রবেশ দেয়, যাতে এটি একটি আসল অ্যাকাউন্ট না ছুঁয়ে AWS সার্ভিস তৈরি আর ব্যবহার করতে পারে। এটি AWS CLI-কে একটি চলমান [LocalStack](https://www.localstack.cloud/) instance-এর সাথে জোড়ে, endpoint, region আর credential বসিয়ে, আর ঐচ্ছিকভাবে প্রতিটি রানের জন্য একটি LocalStack Docker container শুরু ও বন্ধ করতে পারে, বা এমন একটি যা `async with agent:`-এর ভেতরের রানগুলো ভাগ করে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/localstack/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

cloud infrastructure তৈরি বা টেস্ট করা এজেন্টদের bucket, table, queue আর function তৈরির একটি জায়গা লাগে। আসল AWS-এ টাকা খরচ হয়, আসল credential এজেন্টের নাগালে দেয়, আর রানের মাঝে রিসেট করা কঠিন। LocalStack লোকালে AWS অনুকরণ করে; এই capability জোড়া-দেওয়ার কাজ সামলায়: endpoint, নকল credential, AWS CLI আর একটি health check।

/// tip | উদাহরণ দিয়ে বুঝি

LocalStack হলো AWS-এর একটি "প্র্যাকটিস ম্যাচের মাঠ"। আসল ম্যাচে (আসল AWS) ভুল করলে টাকা যায় বা প্রোডাকশন ভাঙে; প্র্যাকটিস মাঠে এজেন্ট যত খুশি bucket বানাতে, মুছতে, ভুল করতে পারে — কোনো ক্ষতি নেই, আর প্রতিটি রানের পর মাঠ পরিষ্কার।

///

## ব্যবহার { #usage }

`LocalStack` একটি চলমান LocalStack instance-এর সাথে যুক্ত AWS টুলিং দেয়। এজেন্ট সাধারণ AWS CLI কমান্ড দেয়; capability endpoint, region আর credential বসায়, আর অনুকৃত সার্ভিসের জন্য একটি health check যোগ করে।

⟦CODE1⟧

ডিফল্টভাবে এজেন্ট আপনার আলাদাভাবে চালু করা একটি LocalStack instance-এ যুক্ত হয়, যেমন [`localstack` CLI](https://docs.localstack.cloud/aws/tooling/localstack-cli/) দিয়ে (`localstack start`)। ডিফল্টগুলো LocalStack-এর রীতির সাথে মেলে: edge endpoint `http://localhost.localstack.cloud:4566` (যা `127.0.0.1`-এ মীমাংসা হয়) আর `test` / `test` credential। capability-কে প্রতি রানে একটি নতুন Docker container, বা `async with agent:`-এর ভেতরে একটি ভাগ করা container শুরু আর বন্ধ করাতে `manage_container=True` সেট করুন।

## টুল { #tools }

| টুল | উদ্দেশ্য |
|---|---|
| `aws_cli` | LocalStack-এর বিপরীতে একটি AWS CLI কমান্ড চালায়। শুরুর `aws` **ছাড়া** আর `--endpoint-url` **ছাড়া** কমান্ড দিন; দুটোই বসানো হয়। লেবেল করা stdout/stderr আর ব্যর্থতায় একটি exit code ফেরত দেয়। |
| `localstack_health` | LocalStack-এর health endpoint জিজ্ঞেস করে কোন সার্ভিস (s3, dynamodb, sqs ইত্যাদি) উপলব্ধ তার JSON ফেরত দেয়। |

কমান্ড একটি আর্গুমেন্ট vector হিসেবে চলে (কোনো shell নয়), তাই কমান্ড string-এ shell operator আর redirection-এর কোনো প্রভাব নেই। প্রতিটি কমান্ড stdin বন্ধ রেখে আর `~/.aws/config` ও `~/.aws/credentials`-এর জায়গায় নিজস্ব খালি AWS config আর credential ফাইল নিয়ে চলে, তাই `aws configure` ওই ফেলে-দেওয়া ফাইল পড়ে আর লেখে আর এর সেটিং শুধু সেই এক কমান্ডের জন্য টেকে। আউটপুট `[stdout]` / `[stderr]` চিহ্ন আর অশূন্য exit-এ একটি `[exit code: N]` লাইন দিয়ে লেবেল করা। এটি `max_output_chars` ছাড়ালে **শেষ অংশ** রাখা হয় (শুরু বাদ পড়ে), তাই error ছাঁটাইয়ে টিকে থাকে। সীমা কমান্ডের ফলেই প্রযোজ্য, তাই এর একটি durable execution রেকর্ডও সীমিত।

`aws_cli` একটি ঐচ্ছিক `timeout_seconds` নেয়, যা একটি কমান্ডের জন্য `default_timeout` override করে। এটি শূন্যের বেশি একটি সসীম সংখ্যা হতে হবে। মডেল যেকোনো টুল কল কতক্ষণ চালাতে পারে তা সীমিত করতে, এজেন্টের `tool_timeout` সেট করুন।

AWS CLI `--body`, `file://`, `fileb://` আর `s3 cp`-এর মতো আর্গুমেন্ট দিয়ে লোকাল ফাইল পড়তে আর লিখতে পারে। এই capability-কে AWS-emulator প্রবেশ আর process-এর filesystem-এ AWS CLI প্রবেশ — দুটোই হিসেবে ধরুন।

/// warning | সতর্কতা

`aws s3 cp ~/.ssh/id_rsa s3://bucket/` — এভাবে এজেন্ট আপনার মেশিনের যেকোনো ফাইল LocalStack-এ "আপলোড" করে পড়তে পারে। LocalStack অনুকৃত হলেও AWS CLI আপনার আসল filesystem দেখে। অবিশ্বস্ত কাজে এজেন্টকে OS-স্তরের বিচ্ছিন্নতায় চালান।

///

## সার্ভিস নিয়ন্ত্রণ { #service-controls }

| ফিল্ড | প্রভাব |
|---|---|
| `allowed_services` | খালি না হলে, শুধু এই AWS সার্ভিস ব্যবহার করা যায় (allowlist), যেমন `['s3', 'dynamodb']`। |
| `denied_services` | এই AWS সার্ভিস সবসময় প্রত্যাখ্যাত (denylist)। |

`allowed_services` আর `denied_services` পরস্পর-বর্জিত: একটি সেট করুন, দুটো নয়। সার্ভিস হলো প্রথম token যা কোনো global option বা এর মান নয় (`--output text s3 ls`-এ `s3`)। global option AWS CLI যে prefix গ্রহণ করে তার যেকোনোটি দিয়ে চেনা হয়, তাই `--out text s3 ls`-ও `s3`-এর নাম দেয়। `--endpoint-url`, `--profile`, `--region` বা `--no-sign-request`, বা এদের যেকোনো prefix দেওয়া কমান্ড প্রত্যাখ্যাত, কারণ capability লক্ষ্য আর credential বসায়।

/// warning | সর্বোত্তম-চেষ্টা, নিরাপত্তার সীমা নয়

এই যাচাই এজেন্ট কোন কমান্ড দেয় তা নিয়ন্ত্রণ করে, এটি কোথায় পৌঁছাতে পারে তা নয়। কঠিন নিশ্চয়তার জন্য, রানের দরকারি সবচেয়ে সংকীর্ণ সার্ভিস আর IAM আচরণ দিয়ে LocalStack নিজেই কনফিগার করুন, আর এজেন্টকে OS-স্তরের বিচ্ছিন্নতায় চালান।

///

## Container পরিচালনা { #managing-the-container }

`manage_container=True` সেট করুন আর capability প্রতিটি রানের জন্য একটি LocalStack Docker container শুরু করে আর রান শেষ হলে বন্ধ করে, তাই প্রতিটি রান একটি নতুন environment পায়; `async with agent:`-এর ভেতরের রান এর বদলে একটি ভাগ করে (নিচে দেখুন)। Docker ইনস্টল করা আর চলমান থাকতে হবে।

⟦CODE2⟧

container-এর edge port (`4566`) `endpoint_url`-এর host port-এ প্রকাশিত হয়, আর capability রান শুরুর আগে health endpoint-এর অপেক্ষা করে, তারপর শেষ হলে container বন্ধ করে (রান exception তুললেও)। প্রতিটি রান একই host port-এ নিজের container পায়, তাই একটি এজেন্টের একসাথে চলা রানের একটি ভাগ করতে হয়: `async with agent:`-এর ভেতরে, এজেন্টে প্রবেশ করলে একটি container শুরু হয় যা ভেতরের রানগুলো ভাগ করে, আর বেরোলে এটি বন্ধ হয়। বিকল্পভাবে, এদের একটি বাইরে-পরিচালিত instance-এ নির্দেশ করুন (`manage_container=False`)।

পরিচালিত container ডিফল্টভাবে `127.0.0.1`-এ বাঁধে, `localhost.localstack.cloud` দিয়ে পৌঁছানো। একটি ভিন্ন ঠিকানায় প্রকাশ করতে `host_address` সেট করুন; `127.0.0.1` বা `0.0.0.0` ছাড়া যেকোনো মান তখন টুল endpoint-এর আর instructions যে endpoint-এর নাম দেয় তারও host, শুধু IPv6 bind-all `::` পৌঁছানো হয় `::1`-এ। `fe80::1%eth0`-এর মতো scoped IPv6 ঠিকানা প্রত্যাখ্যাত।

LocalStack 2026.03.0 থেকে, `localstack/localstack` শুরু করতে একটি auth token লাগে (একটি বিনামূল্যের Hobby token কমিউনিটি ব্যবহার কভার করে)। `LOCALSTACK_AUTH_TOKEN`, বা কোনো token সেট না থাকলে পুরনো `LOCALSTACK_API_KEY`, বর্তমান process থেকে Docker CLI environment দিয়ে পাঠানো হয়, কখনো `docker run` আর্গুমেন্টে নয়, যদি না `container_env` আগে থেকেই এদের একটি সেট করে। একটি token ছাড়া চালাতে, `image`-কে একটি `localstack/localstack:4.x` tag-এ pin করুন।

Lambda-র মতো Docker-চালিত সার্ভিসের Docker socket mount করা লাগে, আর কিছু সার্ভিস gateway-এর বাইরে port প্রকাশ করে (LocalStack `4510-4559` সংরক্ষণ করে)। আপনার টেস্ট করা একটি সার্ভিসের এগুলো লাগলে স্পষ্টভাবে চালু করুন:

⟦CODE3⟧

Docker socket mount করলে container host-স্তরের Docker নিয়ন্ত্রণ পায়। অনুকৃত সার্ভিসের এটি না লাগলে আর রান environment আগে থেকে বিশ্বস্ত না হলে `mount_docker_socket=False` রাখুন।

একই lifecycle একটি async context manager হিসেবে আলাদাভাবেও পাওয়া যায়:

⟦CODE4⟧

## Durable execution { #durable-execution }

[durable execution](../durable_execution/overview.md)-এর অধীনে, একটি বাইরের LocalStack instance-এর বিপরীতে প্রতিটি AWS CLI কমান্ড আর health check লেখা হয়, তাই একটি উদ্ধার হওয়া রান কমান্ড আবার না চালিয়ে এর আউটপুট পুনর্ব্যবহার করে। Temporal আর Prefect প্রতিটি টুল কল নিজস্ব activity বা task-এ লেখে। DBOS ফাংশন টুল workflow কোডে চালায়, তাই সেখানে কমান্ড নিজস্ব step হিসেবে চলে।

একটি পরিচালিত container (`manage_container=True`) একটি রান উদ্ধার করা process-এ খালি শুরু হয়, তাই DBOS-এ `LocalStack` এর কমান্ড লেখে না: উদ্ধার এগুলো আবার চালায়, যা container-এর state আবার তৈরি করে। Temporal আর Prefect প্রতিটি টুল কল লেখে, তাই সেখানে উদ্ধার লেখা আউটপুট replay করে আর নতুন container-এ আগের কমান্ডের তৈরি resource থাকে না। ওই engine-এ durable রানের জন্য `endpoint_url` একটি বাইরের LocalStack instance-এ নির্দেশ করুন।

`async with agent:`-এর ভেতরে একটি container ভাগ করা রানগুলো এর state-ও ভাগ করে। এদের একটি DBOS-এ উদ্ধার হলে যখন সেই container তখনও চালু, এর আবার চালানো কমান্ড এটি আর এর সহোদর রানের ইতিমধ্যে তৈরি resource-এর মুখোমুখি হয়, তাই idempotent নয় এমন কমান্ড, যেমন `s3 mb` বা `sqs create-queue`, ব্যর্থ হতে পারে। durable রানের জন্য, একটি বাইরের instance ব্যবহার করুন, বা কমান্ড idempotent রাখুন।

রেকর্ডগুলোর নাম capability-র `id` অনুযায়ী, যার ডিফল্ট `localstack`, তাই durable execution-এ কোনো কনফিগারেশন লাগে না।

## Telemetry { #telemetry }

`LocalStack` নিজের কোনো span তৈরি করে না। Core-এর [instrumentation](../capabilities/instrumentation.md) আগে থেকেই প্রতিটি `aws_cli` আর `localstack_health` কল একটি tool span হিসেবে লেখে। একটি পরিচালিত container শুরু আর বন্ধে span-এর যোগ্য কোনো সিদ্ধান্ত নেই। Docker অনুপস্থিত বা ব্যর্থ হলে, বা LocalStack কখনো প্রস্তুত না হলে, শুরু `LocalStackError` তোলে।

## কনফিগারেশন { #configuration }

⟦CODE5⟧

AWS CLI ইনস্টল করা আর `PATH`-এ থাকতে হবে (বা `aws_cli_path` এতে নির্দেশ করুন)। binary অনুপস্থিত থাকলে, `aws_cli` রান বাতিল না করে একটি স্পষ্ট error ফেরত দেয়। নিজেরটি দিলে capability-র prompt লেখা বাদ দিতে `include_instructions=False` সেট করুন।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`LocalStack` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে:

⟦CODE6⟧

⟦CODE7⟧

`custom_capability_types` দিন, যাতে spec loader জানে `LocalStack` কীভাবে তৈরি করতে হয়।

## আরও পড়ুন { #further-reading }

- [LocalStack documentation](https://docs.localstack.cloud/)
- [Pydantic AI capabilities](../capabilities/overview.md)
- [Toolsets](../toolsets.md)

## API রেফারেন্স { #api-reference }

⟦CODE8⟧

⟦CODE9⟧

⟦CODE10⟧

/// check | সংক্ষেপে মনে রাখুন

* `LocalStack()` = `aws_cli` + `localstack_health`; endpoint, region আর `test`/`test` credential নিজে বসায়।
* `manage_container=True` দিয়ে প্রতি রানে নতুন container (Docker লাগে); LocalStack 2026.03+-এ auth token লাগে।
* `allowed_services`/`denied_services` guardrail, নিরাপত্তার সীমা নয়; AWS CLI আপনার লোকাল ফাইল পড়তে পারে।
* Docker socket mount শুধু দরকার আর বিশ্বস্ত হলে।
* durable রানে বাইরের LocalStack instance বা idempotent কমান্ড।

///
