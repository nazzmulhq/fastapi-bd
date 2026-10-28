# Deferred টুল { #deferred-tools }

/// note | এই পেজে যা শিখবেন

* Deferred টুল কী: যে টুল একই রানে সাথে সাথে চালানো যায় না বা উচিত নয় (অনুমোদন লাগে, বা বাইরে চলে)।
* দুই উপায়: `HandleDeferredToolCalls` দিয়ে রানের ভেতরেই মীমাংসা, বা `DeferredToolRequests` দিয়ে রান থামিয়ে পরে চালিয়ে যাওয়া।
* মানুষের অনুমোদন (`requires_approval`, `ApprovalRequired`) আর বাইরে চালানো (`CallDeferred`)।
* কথোপকথন থামানো, আর stream-এ deferred টুল কল দেখা।

///

কয়েকটি পরিস্থিতি আছে যেখানে মডেলের এমন একটি টুল ডাকতে পারা উচিত যা একই Python প্রসেসের ভেতরে একই এজেন্ট রানের সময় চালানো উচিত নয় বা সম্ভব নয়:

- এটি আগে ব্যবহারকারীর অনুমোদন চাইতে পারে
- এটি ফল দিতে একটি upstream সার্ভিস, frontend বা ব্যবহারকারীর ওপর নির্ভর করতে পারে
- ফল তৈরি হতে এজেন্ট প্রসেস চালু রাখার যুক্তিসঙ্গত সময়ের চেয়ে বেশি লাগতে পারে

/// tip | উদাহরণ দিয়ে বুঝি

একজন সহকারী আপনার হয়ে কাজ করছে, কিন্তু "১০ লাখ টাকা পাঠাও"-এর মতো কাজে আপনার স্বাক্ষর লাগে। সে ফর্মটি পূরণ করে আপনার টেবিলে রেখে যায় আর অপেক্ষা করে (deferred)। আপনি স্বাক্ষর দিলে (approve) বা না দিলে (deny), সে কাজটি শেষ করে বা অন্যভাবে এগোয়। একইভাবে কিছু কাজ অন্য কেউ করে দেয় (যেমন ব্রাউজারে চলা একটি টুল), আর ফল এলে সহকারী চালিয়ে যায়।

///

এই ব্যবহারগুলো সমর্থন করতে, Pydantic AI deferred টুলের ধারণা দেয়, যা দুই রকমের, নিচে নথিভুক্ত:

- যে টুলের [অনুমোদন লাগে](#human-in-the-loop-tool-approval)
- যে টুল [বাইরে চালানো হয়](#external-tool-execution)

মডেল একটি deferred টুল ডাকলে, এটি মীমাংসার দুটি উপায় আছে:

- **সেখানেই মীমাংসা করুন**, একটি handler-সহ একটি [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] [capability](capabilities/overview.md) দিয়ে, যা অপেক্ষমাণ কলের কিছু বা সব মীমাংসা করে। এজেন্ট রান শেষ আর আবার শুরু না করেই একটি কলে চলতে থাকে — এটি ব্যবহার করুন যখন মীমাংসাকারী (যেমন একটি অনুমোদনের দরজা, একটি বাইরের সার্ভিস client) এজেন্টের একই প্রসেসে থাকে। দেখুন [Resolving deferred calls with a handler](#resolving-deferred-calls-with-a-handler)।
- **রান শেষ করুন** deferred টুল কলের তথ্যসহ একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট অবজেক্ট দিয়ে; caller অনুমোদন/ফল সংগ্রহ করে তারপর মূল রানের [বার্তার ইতিহাস](message-history.md) আর একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] অবজেক্ট দিয়ে একটি নতুন এজেন্ট রান শুরু করে। সেই পরবর্তীটি নিজস্ব [`run_id`](message-history.md#correlating-runs-with-run_id-and-conversation_id)-সহ একটি আলাদা এজেন্ট রান (থেমে থাকা রানেরটি আবার ব্যবহার করবেন না); থামা/আবার শুরুর সম্পর্ক `conversation_id` দিয়ে রাখুন। এটি ব্যবহার করুন যখন মীমাংসাকারী এজেন্ট প্রসেসের বাইরে থাকে — যেমন একটি UI adapter যা অপেক্ষমাণ কল একজন ব্যবহারকারীকে দেখায় আর তাদের উত্তর পেলে একটি পরবর্তী রান শুরু করে।

দুই প্রবাহ একসাথে মেলে: একটি handler কলের একটি উপসেট মীমাংসা করে বাকিগুলো একজন বাইরের caller-এর সামলানোর জন্য `DeferredToolRequests` আউটপুট হিসেবে ওপরে যেতে দিতে পারে।

সব-থামানো প্রবাহে `Agent`-এর [`output_type`](output.md#structured-output)-এ `DeferredToolRequests` থাকতে হবে, যাতে এজেন্ট রানের আউটপুটের সম্ভাব্য টাইপ সঠিকভাবে অনুমিত হয়। আপনার এজেন্ট যদি এমন প্রসঙ্গেও ব্যবহার হতে পারে যেখানে কোনো deferred টুল নেই আর এজেন্ট ব্যবহারের প্রতিটি জায়গায় সেই টাইপ সামলাতে না চান, তাহলে বদলে এজেন্ট চালানোর সময় [`agent.run()`][pydantic_ai.agent.AbstractAgent.run], [`agent.run_sync()`][pydantic_ai.agent.AbstractAgent.run_sync], [`agent.run_stream()`][pydantic_ai.agent.AbstractAgent.run_stream] বা [`agent.iter()`][pydantic_ai.agent.Agent.iter]-এ `output_type` আর্গুমেন্ট দিতে পারেন। মনে রাখবেন চলার সময়ের `output_type` তৈরির সময় নির্দিষ্টটি override করে (টাইপ অনুমানের কারণে), তাই মূল আউটপুট টাইপ স্পষ্টভাবে রাখতে হবে।

## একটি handler দিয়ে deferred কল মীমাংসা { #resolving-deferred-calls-with-a-handler }

deferred টুল কল সামলানোর প্রস্তাবিত উপায় হলো একটি [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] [capability](capabilities/overview.md) নথিভুক্ত করা, যার handler [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] পায় আর এর কিছু বা সব মীমাংসা করা একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] ফেরত দেয়। টুল চালানোর pipeline ফলগুলো সেখানেই প্রয়োগ করে আর এজেন্ট রান একটি কলে চলতে থাকে, যেন deferred টুলগুলো স্বাভাবিকভাবে ফেরত এসেছে।

একটি handler থাকলে, `DeferredToolRequests`-কে আর একটি আউটপুট টাইপ হিসেবে ঘোষণা করতে হয় না — যদি না আপনি অমীমাংসিত কলগুলোও caller পর্যন্ত যেতে দিতে চান (নিচে দেখুন)।

[`DeferredToolRequests.build_results()`][pydantic_ai.tools.DeferredToolRequests.build_results] একটি সুবিধাজনক constructor — এটি যাচাই করে যে প্রতিটি টুল কল ID সঠিক ধরনের একটি অপেক্ষমাণ রিকোয়েস্ট নির্দেশ করে, আর অন্যথায় নির্দিষ্ট নয় এমন যেকোনো অনুমোদনের রিকোয়েস্ট নিজে থেকে অনুমোদন করতে `approve_all=True` নেয়।

⟦CODE1⟧

1. এখানে কখনো পৌঁছায় না — handler এই কল প্রত্যাখ্যান করে, তাই মডেল বদলে প্রত্যাখ্যানের বার্তা দেখে।
2. handler এই বাইরের কলের ফল দেয়, তাই টুলের body শুধু deferral-এর সংকেত দেয়।

handler কিছু বা সব কল মীমাংসা করতে অস্বীকার করলে (ফেরত দেওয়া [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] থেকে সেগুলো বাদ দিয়ে বা `None` ফেরত দিয়ে), পরের [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] (বা [`handle_deferred_tool_calls`][pydantic_ai.capabilities.AbstractCapability.handle_deferred_tool_calls] hook override করা অন্য যেকোনো capability) একটি সুযোগ পায়, আর তখনো অমীমাংসিত কলগুলো একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট হিসেবে ওপরে যায়। সেই ওপরে যাওয়া অনুমোদন করতে, এজেন্টের `output_type`-এ `DeferredToolRequests` রাখুন — যাতে অর্থবহ হলে সেখানেই সামলানোকে সব-থামানো প্রবাহের সাথে মেলাতে পারেন।

আপনি যদি এমন একটি [নিজের capability তৈরি](capabilities/custom.md) করেন যা নিজেই অনুমোদন বা বাইরের কল মীমাংসা করে (যেমন deferred টুল দেখানো একটি sandbox), একটি আলাদা `HandleDeferredToolCalls` নথিভুক্ত না করে আপনার capability-তে সরাসরি [`handle_deferred_tool_calls`][pydantic_ai.capabilities.AbstractCapability.handle_deferred_tool_calls] hook override করুন। একই hook [`Hooks`][pydantic_ai.capabilities.Hooks] capability দিয়েও পাওয়া যায় — দেখুন [Hooks](hooks.md#deferred-tool-call-hook)।

নিচের অংশগুলো handler মীমাংসা করতে পারে এমন দুই ধরনের deferred টুল বর্ণনা করে, আর প্রতিটির জন্য বিকল্প সব-থামানো প্রবাহ। একাধিক capability কীভাবে মেলে, [`WrapperCapability`][pydantic_ai.capabilities.WrapperCapability] আর `capabilities=[...]` তালিকাসহ, তা দেখুন [Capabilities](capabilities/overview.md)-এ।

## Human-in-the-loop টুল অনুমোদন { #human-in-the-loop-tool-approval }

একটি টুল ফাংশনের সবসময় অনুমোদন লাগলে, [`@agent.tool`][pydantic_ai.agent.Agent.tool] decorator, [`@agent.tool_plain`][pydantic_ai.agent.Agent.tool_plain] decorator, [`Tool`][pydantic_ai.tools.Tool] ক্লাস, [`FunctionToolset.tool`][pydantic_ai.toolsets.FunctionToolset.tool] decorator বা [`FunctionToolset.add_function()`][pydantic_ai.toolsets.FunctionToolset.add_function] মেথডে `requires_approval=True` আর্গুমেন্ট দিতে পারেন। ফাংশনের ভেতরে, তখন ধরে নিতে পারেন টুল কলটি অনুমোদিত হয়েছে।

একটি [realtime session](realtime/tools.md#deferred-and-approval-required-tools)-এ, অনুমোদন সেখানেই মীমাংসা হতে হবে, সাধারণত একটি [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] handler দিয়ে (একটি capability hook-ও মীমাংসা করতে পারে); যে কল কিছুই মীমাংসা করে না তা প্রতিবার প্রত্যাখ্যাত হয়।

অনুমোদন টুল কলের আর্গুমেন্ট বা এজেন্টের [run context][pydantic_ai.tools.RunContext]-এর ওপর নির্ভর করলে, যেমন [dependencies](dependencies.md) বা বার্তার ইতিহাস, টুল ফাংশন থেকে [`ApprovalRequired`][pydantic_ai.exceptions.ApprovalRequired] তুলুন। টুল কলটি আগেই অনুমোদিত হলে [`RunContext.tool_call_approved`][pydantic_ai.tools.RunContext.tool_call_approved] property `True` হবে।

টুলের [`args_validator`](tools-advanced.md#args-validator) থেকেও এটি তুলতে পারেন, যা টুল ফাংশনের আগে চলে আর একজন মানুষকে অনুমোদন করতে বলার আগে অবৈধ আর্গুমেন্ট প্রত্যাখ্যান করতে দেয়।

একটি [toolset](toolsets.md)-এর দেওয়া টুলে (যেমন একটি [MCP সার্ভার](mcp/client.md)) কলের জন্য অনুমোদন বাধ্যতামূলক করতে, দেখুন [`ApprovalRequiredToolset` ডকুমেন্টেশন](toolsets.md#requiring-tool-approval)।

/// warning | অনুমোদন একটি অবিশ্বস্ত ক্লায়েন্টের বিরুদ্ধে অনুমতির সীমানা নয়

আপনি একটি [UI adapter](ui/overview.md#trust-model-for-client-submitted-messages)-এর মাধ্যমে একটি এজেন্ট দিলে, অনুমোদনের সিদ্ধান্ত ক্লায়েন্ট রিকোয়েস্টের বাকিটার সাথে পাঠায়, আর adapter-এর কাছে সার্ভারে কোনো রেকর্ড নেই যে এটি কোন টুল কল দিয়েছিল। endpoint-এ পৌঁছাতে পারে এমন একটি ক্লায়েন্ট নিজের বানানো একটি টুল কল অনুমোদন করতে পারে। Human-in-the-loop অনুমোদন মানুষের সম্মতি ছাড়া *মডেলের* কাজের বিরুদ্ধে রক্ষা করে; এটি adapter endpoint প্রমাণীকরণ আর টুল ফাংশনের ভেতরে সংবেদনশীল কাজের অনুমতি প্রয়োগের বিকল্প নয়, যা কলটি ইতিহাসে যেভাবেই ঢুকুক চলে। এটি শুধু adapter নয়, একটি ক্লায়েন্টের `message_history` নেওয়া যেকোনো endpoint-এ প্রযোজ্য — দেখুন [Trust boundary for client-supplied history](message-history.md#trust-boundary-for-client-supplied-history) আর [Trust model for client-submitted messages](ui/overview.md#trust-model-for-client-submitted-messages)।

///

মডেল অনুমোদন লাগে এমন একটি টুল ডাকলে, এজেন্ট রান একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট অবজেক্ট দিয়ে শেষ হবে, যার একটি `approvals` তালিকায় টুলের নাম, যাচাই করা আর্গুমেন্ট আর একটি অনন্য টুল কল ID-সহ [`ToolCallPart`][pydantic_ai.messages.ToolCallPart] থাকে।

ব্যবহারকারীর অনুমোদন বা প্রত্যাখ্যান সংগ্রহ করার পরে, একটি `approvals` dictionary-সহ একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] অবজেক্ট তৈরি করতে পারেন, যা প্রতিটি টুল কল ID-কে একটি boolean, একটি [`ToolApproved`][pydantic_ai.tools.ToolApproved] অবজেক্ট (ঐচ্ছিক `override_args`-সহ), বা একটি [`ToolDenied`][pydantic_ai.tools.ToolDenied] অবজেক্ট (মডেলকে দেওয়ার একটি ঐচ্ছিক নিজের `message`-সহ)-এ ম্যাপ করে। `DeferredToolResults`-এ একটি `metadata` dictionary-ও দিতে পারেন, যা প্রতিটি টুল কল ID-কে metadata-র একটি dictionary-তে ম্যাপ করে যা টুলের [`RunContext.tool_call_metadata`][pydantic_ai.tools.RunContext.tool_call_metadata] attribute-এ পাওয়া যাবে। এই `DeferredToolResults` অবজেক্ট তারপর মূল রানের [বার্তার ইতিহাস](message-history.md) বা এর [কথোপকথনের](#pausing-a-conversation) পাশাপাশি `deferred_tool_results` হিসেবে এজেন্ট রান মেথডগুলোর একটিতে দেওয়া যায়, যা উত্তর পরে এলে রিকোয়েস্টগুলোও রাখে।

এখানে একটি উদাহরণ যা দেখায় সব ফাইল মোছার জন্য, আর নির্দিষ্ট সুরক্ষিত ফাইল হালনাগাদের জন্য কীভাবে অনুমোদন বাধ্যতামূলক করবেন:

⟦CODE2⟧

1. ঐচ্ছিক `metadata` প্যারামিটার deferred টুল কলে যেকোনো প্রসঙ্গ জুড়তে পারে, যা `tool_call_id` দিয়ে key করা `DeferredToolRequests.metadata`-এ পাওয়া যায়।
2. এই দ্বিতীয় এজেন্ট রান প্রথম রান যেখানে থেমেছিল সেখান থেকে চালিয়ে যায়, টুল অনুমোদনের ফল আর ঐচ্ছিকভাবে deferred ফলের পাশাপাশি মডেলকে বাড়তি নির্দেশনা দিতে একটি নতুন `user_prompt` দিয়ে।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

/// info | ধাপগুলো সহজ ভাষায়

1. প্রথম রান: মডেল `delete_file` আর `update_file` ডাকে; অনুমোদন লাগে বলে রান `DeferredToolRequests` দিয়ে থামে।
2. আপনি `requests.approvals` দেখে প্রতিটি কলের জন্য সিদ্ধান্ত নেন: `True`, `False`, `ToolDenied('কারণ')` বা `ToolApproved(override_args=...)`।
3. দ্বিতীয় রান: `message_history=result.all_messages()` আর `deferred_tool_results=results` দিয়ে; অনুমোদিত টুল চলে, প্রত্যাখ্যাতগুলোর বার্তা মডেল দেখে।

///

/// note | টুল ফলের ক্রম

টুল ফল মডেল সংশ্লিষ্ট টুল কল যে ক্রমে দিয়েছে সেই ক্রম মানে। ওপরের বার্তার ইতিহাসে, `.env`-এর জন্য `update_file`-এর ফলের আগে `delete_file`-এর প্রত্যাখ্যাত ফল দেখা দেয়, কারণ মডেল আগে `delete_file` দিয়েছিল। এটি v2-এ একটি ইচ্ছাকৃত আচরণ-পরিবর্তন: ফল আর টুলের ধরন অনুযায়ী দলবদ্ধ নয়, তাই আপনি যে ক্রম দেখেন তা মডেলের দেওয়ার ক্রম প্রতিফলিত করে।

///

## বাইরে টুল চালানো { #external-tool-execution }

একটি টুল কলের ফল যে এজেন্ট রানে ডাকা হয়েছে তার ভেতরে তৈরি করা না গেলে, টুলটি বাইরের বলে ধরা হয়।
বাইরের টুলের উদাহরণ হলো একটি ওয়েব বা অ্যাপ frontend-এর বাস্তবায়ন করা client-পক্ষের টুল, আর ধীর কাজ যা এজেন্ট প্রসেস চালু না রেখে একটি background worker বা বাইরের সার্ভিসে দেওয়া হয়।

একটি টুল কল বাইরে চালানো উচিত কিনা তা যদি টুল কলের আর্গুমেন্ট, এজেন্টের [run context][pydantic_ai.tools.RunContext] (যেমন [dependencies](dependencies.md) বা বার্তার ইতিহাস), বা কাজটি কতক্ষণ নেবে বলে আশা করা হয় তার ওপর নির্ভর করে, তাহলে একটি টুল ফাংশন সংজ্ঞায়িত করে শর্তসাপেক্ষে [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] exception তুলতে পারেন। exception তোলার আগে, টুল ফাংশন সাধারণত কোনো background কাজ নির্ধারণ করে আর [`RunContext.tool_call_id`][pydantic_ai.tools.RunContext.tool_call_id] পাঠিয়ে দেয়, যাতে পরে ফলটি deferred টুল কলের সাথে মেলানো যায়।

অনুমোদনের মতো, টুলের [`args_validator`](tools-advanced.md#args-validator)-ও `CallDeferred` তুলতে পারে, তাই শুধু বৈধ আর্গুমেন্টসহ কলই হস্তান্তর হয়।

একটি টুল সবসময় বাইরে চালানো হলে আর এর সংজ্ঞা এর আর্গুমেন্টের একটি JSON schema-সহ আপনার কোডে দেওয়া হলে, একটি [`ExternalToolset`](toolsets.md#external-toolset) ব্যবহার করতে পারেন। বাইরের টুলগুলো আগে থেকে জানা থাকলে আর আপনার হাতে আর্গুমেন্টের JSON schema না থাকলে, উপযুক্ত signature-সহ একটি টুল ফাংশনও সংজ্ঞায়িত করতে পারেন যা [`CallDeferred`][pydantic_ai.exceptions.CallDeferred] exception তোলা ছাড়া কিছুই করে না।

মডেল একটি বাইরের টুল ডাকলে, এজেন্ট রান একটি [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] আউটপুট অবজেক্ট দিয়ে শেষ হবে, যার একটি `calls` তালিকায় টুলের নাম, যাচাই করা আর্গুমেন্ট আর একটি অনন্য টুল কল ID-সহ [`ToolCallPart`][pydantic_ai.messages.ToolCallPart] থাকে।

টুল কলের ফল তৈরি হলে, একটি `calls` dictionary-সহ একটি [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] অবজেক্ট তৈরি করতে পারেন, যা প্রতিটি টুল কল ID-কে ম্যাপ করে মডেলে ফেরত দেওয়ার একটি যেকোনো মানে, একটি [`ToolReturn`](tools-advanced.md#advanced-tool-returns) অবজেক্টে, বা টুল কল ব্যর্থ হলে একটি exception-এ: মডেলের [আবার চেষ্টা করা](tools-advanced.md#tool-retries) উচিত হলে একটি [`ModelRetry`][pydantic_ai.exceptions.ModelRetry], বা ব্যর্থতা মডেলকে একটি [ব্যর্থ ফল](tools-advanced.md#tool-failed) হিসেবে জানানো উচিত হলে (টুলের retry বাজেট খরচ না করে) একটি [`ToolFailed`][pydantic_ai.exceptions.ToolFailed], যাতে এটি কীভাবে এগোবে তা ঠিক করতে পারে। এই `DeferredToolResults` অবজেক্ট তারপর মূল রানের [বার্তার ইতিহাস](message-history.md) বা এর [কথোপকথনের](#pausing-a-conversation) পাশাপাশি `deferred_tool_results` হিসেবে এজেন্ট রান মেথডগুলোর একটিতে দেওয়া যায়, যা উত্তর পরে এলে রিকোয়েস্টগুলোও রাখে।

এখানে একটি উদাহরণ যা দেখায় সম্পূর্ণ হতে কিছুক্ষণ লাগে এমন একটি কাজ background-এ সরিয়ে কাজ শেষ হলে ফলটি মডেলে কীভাবে ফেরত দেবেন:

⟦CODE3⟧

1. একটি task ID তৈরি করুন যা টুল কল ID থেকে স্বাধীনভাবে ট্র্যাক করা যায়।
2. ঐচ্ছিক `metadata` প্যারামিটার `task_id` পাঠায় যাতে পরে এটি ফলের সাথে মেলানো যায়, `tool_call_id` দিয়ে key করা `DeferredToolRequests.metadata`-এ পাওয়া যায়।
3. বাস্তবে, এটি সাধারণত একটি আলাদা প্রসেসে ঘটত, যা কাজের অবস্থা জানতে নিয়মিত খোঁজ নেয় বা সব অপেক্ষমাণ কাজ শেষ হলে জানানো হয়।

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

## একটি কথোপকথন থামানো { #pausing-a-conversation }

[`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] দিয়ে শেষ হওয়া একটি রান তার কথোপকথন থামিয়েছে: কলগুলোর উত্তর না আসা পর্যন্ত পরের রান এগোতে পারে না, আর উত্তর প্রায়ই পরে আসে — একজন পর্যালোচক কাল refund অনুমোদন করেন, আরেকটি মেশিনে একটি job শেষ হয়। রানের [`conversation`][pydantic_ai.agent.AgentRunResult.conversation] রিকোয়েস্টগুলো [`deferred_tool_requests`][pydantic_ai.conversation.Conversation.deferred_tool_requests] হিসেবে রাখে, তাই আপনার সংরক্ষিত কথোপকথনই আবার শুরু করার জন্য যা দরকার তার সব।

এটি গুরুত্বপূর্ণ কারণ বার্তা থেকে রিকোয়েস্ট পুনর্গঠন করা যায় না। ইতিহাস দেখায় কোন কলগুলোর উত্তর নেই, কিন্তু কোনগুলোর অনুমোদন আর কোনগুলোর একটি বাইরের ফল লাগে, বা defer করার সময় একটি টুল যে metadata জুড়েছিল তা নয়। কথোপকথনটি সংরক্ষণ করুন, আর সেগুলো এর সাথে চলে:

⟦CODE4⟧

1. থেমে থাকা কথোপকথন সংরক্ষণ করুন, যেমন `result.conversation_id` দিয়ে key করে।
2. পরে — আরেকটি রিকোয়েস্টে, কেউ অপেক্ষমাণ কল পর্যালোচনা করার পরে — এটি আবার লোড করুন।
3. [`build_results`][pydantic_ai.tools.DeferredToolRequests.build_results] প্রতিটি উত্তর যে রিকোয়েস্টের উত্তর দেয় তার সাথে পরীক্ষা করে, তাই একটি পুরনো বা ভুল লেখা টুল কল ID রানে নয়, এখানেই ব্যর্থ হয়।
4. রান শেষ হয়েছে, তাই এটি যে কথোপকথন ফেরত দেয় তা কিছুর জন্য অপেক্ষা করছে না।

_(এই উদাহরণ সম্পূর্ণ, "যেমন আছে তেমন" চালানো যায়)_

## একটি stream-এ deferred টুল কল দেখা { #observing-deferred-tool-calls-in-a-stream }

অন্য যেকোনো টুল কলের মতো, একটি deferred টুল কল [event stream](agent.md#streaming-events-and-final-output)-এ একটি [`FunctionToolCallEvent`][pydantic_ai.messages.FunctionToolCallEvent] পাঠায় — কিন্তু সেই event একা একজন stream গ্রাহককে বলে না যে কলটি মিথস্ক্রিয়ার অপেক্ষায় থেমে আছে, বা কোন ধরনের মিথস্ক্রিয়া প্রত্যাশিত। দুটি বাড়তি [`AgentStreamEvent`][pydantic_ai.messages.AgentStreamEvent] সেই প্রসঙ্গ বহন করে:

- [`DeferredToolRequestsEvent`][pydantic_ai.messages.DeferredToolRequestsEvent] — deferred কলের প্রতিটি ব্যাচে একবার পাঠানো হয়, [`DeferredToolRequests`][pydantic_ai.tools.DeferredToolRequests] বহন করে। কোনো [`HandleDeferredToolCalls`][pydantic_ai.capabilities.HandleDeferredToolCalls] handler চলার আগে এটি পাঠানো হয়, তাই একজন গ্রাহক যেমন handler অপেক্ষা করার সময় একটি frontend-কে জানাতে পারে যে ইনপুট দরকার। কোনো handler সব রিকোয়েস্ট মীমাংসা না করলে, রান অপেক্ষমাণ রিকোয়েস্টগুলোকে তার `DeferredToolRequests` আউটপুট হিসেবে নিয়ে শেষ হয়।
- [`DeferredToolResultsEvent`][pydantic_ai.messages.DeferredToolResultsEvent] — একটি handler রিকোয়েস্ট (এর কিছু) মীমাংসা করলে পাঠানো হয়, [`DeferredToolResults`][pydantic_ai.tools.DeferredToolResults] বহন করে। মীমাংসিত কলগুলো তারপর সাধারণ pipeline দিয়ে চলে, প্রতিটি একটি [`FunctionToolResultEvent`][pydantic_ai.messages.FunctionToolResultEvent] পাঠায়। ফল বদলে `deferred_tool_results` দিয়ে একটি নতুন রানে দেওয়া হলে কোনো event পাঠানো হয় না, কারণ সেক্ষেত্রে caller আগেই সেগুলো জানে।

এটি মীমাংসা আর উপস্থাপনাকে আলাদা রাখে: একটি handler বিশুদ্ধ মীমাংসার লজিক ধরতে পারে (যেমন একটি [durable execution](durable_execution/overview.md) workflow-এ একটি সংকেতের অপেক্ষা), অথচ একজন stream গ্রাহক frontend-এর সাথে সব যোগাযোগের মালিক, কোন টুল মিথস্ক্রিয় তার নিজের ম্যাপিং না রেখেই।

ওপরের [handler উদাহরণ](#resolving-deferred-calls-with-a-handler) চালিয়ে যাওয়া:

⟦CODE5⟧

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

## আরও দেখুন { #see-also }

- [Function Tools](tools.md) - টুলের মৌলিক ধারণা আর নথিভুক্তি
- [Advanced Tool Features](tools-advanced.md) - নিজের schema, গতিশীল টুল আর চালানোর বিস্তারিত
- [Toolsets](toolsets.md) - টুলের সংগ্রহ সামলানো, বাইরের টুলের জন্য `ExternalToolset`-সহ
- [Message History](message-history.md) - deferred টুলের জন্য বার্তার ইতিহাস নিয়ে কাজ, [`run_id` / `conversation_id`](message-history.md#correlating-runs-with-run_id-and-conversation_id)-সহ
- [Realtime tools](realtime/tools.md#deferred-and-approval-required-tools) - একটি জীবন্ত কণ্ঠ-session-এ অনুমোদন-প্রয়োজন আর deferred টুল

/// check | সংক্ষেপে মনে রাখুন

* অনুমোদন: `requires_approval=True` বা শর্তসাপেক্ষে `raise ApprovalRequired()`; বাইরে চালানো: `raise CallDeferred()`।
* একই প্রসেসে মীমাংসা: `HandleDeferredToolCalls(handler)` — রান থামে না।
* অন্যথায়: `output_type=[..., DeferredToolRequests]`, রান থামে; পরে `deferred_tool_results=...` দিয়ে নতুন রান।
* `result.conversation` সংরক্ষণ করুন — এতে অপেক্ষমাণ রিকোয়েস্টও থাকে; `build_results()` উত্তর যাচাই করে।
* অনুমোদন ক্লায়েন্টের বিরুদ্ধে নিরাপত্তা নয়; সংবেদনশীল কাজে টুলের ভেতরে অনুমতি পরীক্ষা করুন।

///
