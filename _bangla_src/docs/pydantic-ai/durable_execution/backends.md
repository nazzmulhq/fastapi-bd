# একটি durable execution backend তৈরি { #building-a-durable-execution-backend }

/// note | এই পেজে যা শিখবেন

* একটি নতুন durable execution engine-কে Pydantic AI-তে যুক্ত করার জন্য পাবলিক builder।
* দুটি backend স্তর: `CallableOperationBackend` আর `RegisteredOperationBackend` — কখন কোনটি।
* serialization codec, কনফিগারেশন, অন্য process-এ চলা durable একক, আর সংরক্ষিত নাম ও উদ্ধার।

এই পেজটি **engine ইন্টিগ্রেশন লেখকদের** জন্য। আপনি শুধু Temporal/DBOS/Prefect ব্যবহার করলে এটি দরকার নেই।

///

Pydantic AI-এর durable execution builder একটি ইন্টিগ্রেশনকে মডেল রিকোয়েস্ট, টুল খোঁজা, টুল যাচাই, টুল কল, event সামলানো, message compaction আর
[decorate করা capability operation](../capabilities/custom.md#durable-capability-operations) একটি engine backend দিয়ে পাঠাতে দেয়। এটি ব্যবহার করুন যখন এমন একটি durable execution সিস্টেম যুক্ত করছেন যা আগে থেকে সমর্থিত নয়।

[Temporal][pydantic_ai.durable_exec.temporal.TemporalDurability],
[DBOS][pydantic_ai.durable_exec.dbos.DBOSDurability] আর
[Prefect][pydantic_ai.durable_exec.prefect.PrefectDurability]-এর সম্পূর্ণ বাস্তবায়ন কাজের রেফারেন্স। বাইরের
[Restate](https://github.com/restatedev/sdk-python/tree/main/python/restate/ext/pydantic),
[AWS Lambda](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/aws_lambda),
[Absurd](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/absurd)
আর [pgtask](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/pgtask)
ইন্টিগ্রেশন JSON journal-সহ একই পাবলিক builder দেখায়, আর
[Render Workflows](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/render)
এমন একটি engine দেখায় যার durable একক অন্য একটি process-এ চলে।

## একটি backend স্তর বাছুন { #choose-a-backend-tier }

[`CallableOperationBackend`][pydantic_ai.durable_exec.CallableOperationBackend] subclass করুন যখন
engine SDK প্রতিবার একটি durable একক ডাকার সময় একটি callback নেয়। টাইপ করা operation পরিচয়, নাম, callback, cache পরিচয় আর মীমাংসিত config SDK-তে দিতে `execute` বাস্তবায়ন করুন। operation পরিচয় একটি engine-কে এর সংরক্ষিত নামের ওপর নির্ভর না করে একটি operation ধরনে আচরণ প্রয়োগ করতে দেয়।

[`RegisteredOperationBackend`][pydantic_ai.durable_exec.RegisteredOperationBackend] ব্যবহার করুন যখন
engine-এর worker শুরুর আগে handler নিবন্ধন করা লাগে। একটি বাঁধা caller তৈরি করে এর নিবন্ধন handle ফেরত দিতে `register` বাস্তবায়ন করুন। এর `registrations()` মেথড সংগৃহীত SDK নিবন্ধন handle বাঁধার ক্রমে ফেরত দেয়। এজেন্ট গঠনের সময়, একটি worker শুরু হওয়ার আগেই base চারটি মডেল operation বাঁধে, তাই আগে একটি মডেল রিকোয়েস্ট না চালিয়েই এই নিবন্ধনগুলো উপস্থিত থাকে। worker তৈরির সময় পুরো `registrations()` ফল engine SDK-তে দিন।

দুটি স্তরই [`DurableOperationBackend`][pydantic_ai.durable_exec.DurableOperationBackend] বাস্তবায়ন করে।
engine-নির্দিষ্ট মৌলিক উপাদানের চারপাশে ফল encoding, cache projection, config মীমাংসা আর নামকরণ এরাই সামলায়।

/// info | এক নজরে: কোন স্তর?

| Engine SDK কেমন | স্তর | যা বাস্তবায়ন করবেন |
|----------------|------|---------------------|
| প্রতিটি কলে একটি callback নেয় (যেমন `ctx.step(fn)`) | `CallableOperationBackend` | `execute` |
| worker শুরুর আগে handler নিবন্ধন চায় (যেমন Temporal activity) | `RegisteredOperationBackend` | `register` |

///

## ন্যূনতম callable backend { #minimal-callable-backend }

এই সম্পূর্ণ in-process উদাহরণ প্রতিটি operation সাথে সাথে চালায়। একটি আসল ইন্টিগ্রেশন `ImmediateBackend.execute`-কে এর SDK-এর activity, step বা task কল দিয়ে বদলায় আর engine runtime জিজ্ঞেস করতে `in_durable_context` বদলায়।

```python
from collections.abc import Awaitable, Callable

from pydantic_ai import Agent
from pydantic_ai.durable_exec import (
    JSON_CODEC,
    BaseDurabilityCapability,
    DurabilityEngineSpec,
    DurableOperationId,
    JournalCallableOperationBackend,
    RoleBasedOperationConfig,
)
from pydantic_ai.models.test import TestModel


class TerminalError(Exception):
    pass


class ImmediateBackend(JournalCallableOperationBackend):
    def __init__(self, agent_name: str, default_model_id: str | None) -> None:
        super().__init__(
            agent_name=agent_name,
            default_model_id=default_model_id,
            config=RoleBasedOperationConfig(model=None, event=None, capability=None, tool=None),
        )

    async def execute(
        self,
        *,
        operation_id: DurableOperationId,
        name: str,
        body: Callable[[], Awaitable[object]],
        cache_key: tuple[object, ...],
        config: None,
    ) -> object:
        return await body()


class ImmediateDurability(BaseDurabilityCapability):
    engine_spec = DurabilityEngineSpec(
        engine_name='Immediate',
        durable_unit_noun='operation',
        durable_container_noun='run',
        codec=JSON_CODEC,
        serialization_failure=lambda exc: TerminalError(str(exc)),
    )

    @property
    def in_durable_context(self) -> bool:
        return True

    def get_durable_operation_backend(self) -> ImmediateBackend:
        return ImmediateBackend(self.name, self.default_model_id)


agent = Agent(TestModel(), name='example', capabilities=[ImmediateDurability()])
result = agent.run_sync('hello')
assert result.output == 'success (no tool calls)'
```

পাবলিক [`DurabilityEngineSpec`][pydantic_ai.durable_exec.DurabilityEngineSpec] ঘোষণামূলক engine পৃষ্ঠতলকে একটি অপরিবর্তনীয় অবজেক্টে একত্র করে। এর বাধ্যতামূলক ফিল্ড engine, durable একক আর durable container-এর নাম দেয়। এর ঐচ্ছিক ফিল্ড codec, মোড়ানো toolset-এর ধরন, lifecycle policy, আপগ্রেড সামঞ্জস্য, durable খোঁজা, ক্রমিক টুল চালানো, অসমর্থিত runtime toolset আর প্রতি-টুল কনফিগারেশন key বাছে। ডিফল্ট lifecycle policy প্রতিটি রানে function আর MCP toolset-এ প্রবেশ করে আর dynamic toolset-এ কখনো প্রবেশ করে না।

যে ফিল্ডের engine আচরণ ডিফল্ট থেকে ভিন্ন, তার প্রতিটি সংজ্ঞায়িত করুন। তৈরির সময় spec খালি-নয় এমন বিশেষ্য যাচাই করে আর প্রতিটি মোড়ানো toolset ধরনের জন্য একটি lifecycle চায়, তাই একটি অবৈধ engine ঘোষণা এর ক্লাস সংজ্ঞায়িত হওয়ার সময়ই ব্যর্থ হয়। lifecycle পছন্দ অবশ্যই নিশ্চিত করবে যে সাফল্য, error আর বাতিলে toolset resource বন্ধ হয়।

## Serialization আর কনফিগারেশন { #serialization-and-configuration }

[`IDENTITY_CODEC`][pydantic_ai.durable_exec.IDENTITY_CODEC] ব্যবহার করুন যখন engine SDK Python অবজেক্ট serialization নিজে সামলায়। [`JSON_CODEC`][pydantic_ai.durable_exec.JSON_CODEC] ব্যবহার করুন যখন ইন্টিগ্রেশন নিজেই JSON-সামঞ্জস্যপূর্ণ journal payload লেখে। দুটোই [`DurabilityCodec`][pydantic_ai.durable_exec.DurabilityCodec] বাস্তবায়ন করে। আর্গুমেন্ট, ফল, টুলের control-flow সংকেত আর decorate করা capability operation — সবই বাছা codec সীমা পার হয়।

JSON-journal engine-এর উচিত `DurabilityEngineSpec.serialization_failure` সেট করা, যাতে deterministic codec ব্যর্থতা engine-এর চূড়ান্ত বা retry-অযোগ্য exception টাইপে রূপান্তরিত হয়। এমন মান retry-তে serialize-যোগ্য হয়ে উঠতে পারে না।

[`RoleBasedOperationConfig`][pydantic_ai.durable_exec.RoleBasedOperationConfig] প্রতি operation role-এ একটি config দেয় আর প্রতি-টুল override-এর জন্য একটি ঐচ্ছিক `resolve_tool` callback নেয়। callback পুরো টাইপ করা operation ID, টুল অবজেক্ট আর টুলের নাম পায়।

[`JournalCallableOperationBackend`][pydantic_ai.durable_exec.JournalCallableOperationBackend]
callable backend-কে `JournalOperationNamer`-এর সাথে জোড়ে। বাঁধা capability-র `default_model_id` দিন, যাতে এজেন্টের ডিফল্ট string মডেল মানক প্রত্যয়-ছাড়া সংরক্ষিত নাম রাখে।

backend config অবজেক্ট backend কনফিগারেশন protocol বাস্তবায়ন করে। এর পাবলিক `base` আর `for_tool` মেথড একটি [`OperationConfigRole`][pydantic_ai.durable_exec.OperationConfigRole] আর একটি [`DurableOperationId`][pydantic_ai.durable_exec.DurableOperationId] পায়। মডেল, toolset বা operation অনুযায়ী config ভিন্ন হলে নির্দিষ্ট ID রূপ মেলান। role হলো একটি মোটা config বালতি: `'model'`, `'event'`, `'tool'` বা `'capability'`। operation ID সূক্ষ্ম পরিচয় বহন করে। একটি capability operation ID-তে `@durable_operation(name='...')`-এর স্পষ্ট নাম থাকে। ওই নাম বাধ্যতামূলক, কারণ এটি সংরক্ষিত সামঞ্জস্য-ডেটা হয়ে যায় আর Python মেথডের নাম বদলালেও স্থির থাকতে হবে। ID union ইনস্টল করা Pydantic AI version-এ উপলব্ধ ID-গুলো প্রতিনিধিত্ব করে।
প্রতি-টুল config একটি function বা dynamic টুলকে একটি durable একক থেকে বের করতে `False` ফেরত দিতে পারে।
MCP টুল I/O করে আর সবসময় তাদের durable এককে চলে, তাই একটির জন্য `False` ফেরত দিলে একটি
[`UserError`][pydantic_ai.exceptions.UserError] ওঠে।

বিল্ট-ইন ID-গুলো হলো `ModelRequestId`, `ModelCompactMessagesId`,
`ModelCancelSuspendedResponseId`, `EventStreamHandlerId`, `ToolsetGetToolsId`,
`ToolsetGetInstructionsId`, `ToolsetValidateToolArgumentsId`, `ToolsetCallToolId` আর
`CapabilityOperationId`। এদের Python ক্লাসের নাম সংরক্ষিত operation নাম নির্ধারণ করে না।

### API-র বিবর্তন { #api-evolution }

Pydantic AI durable একক যোগ করার সাথে সাথে [`DurableOperationId`][pydantic_ai.durable_exec.DurableOperationId] minor release-এ বাড়ে। Sandbox operation একটি পরিকল্পিত উদাহরণ। তাই ID মেলানোর সময় engine কনফিগারেশনে একটি ডিফল্ট শাখা থাকতে হবে। ওই শাখা দিয়ে একটি নিরাপদ মূল কনফিগারেশন প্রয়োগ করুন বা একটি কার্যকর অসমর্থিত-operation error তুলুন। এমন একটি সম্পূর্ণ match-এর ওপর নির্ভর করবেন না যা ধরে নেয় বর্তমান union আর কখনো নতুন শাখা পাবে না।

/// warning | সাধারণ ভুল

`match op_id:`-এ শুধু বর্তমান ID-গুলোর `case` লিখে `case _:` বাদ দেওয়া। Pydantic AI-এর পরের minor release একটি নতুন operation ID আনলে আপনার config সেটার জন্য কিছুই ফেরত দেবে না। সবসময় একটি `case _:` রাখুন — হয় নিরাপদ ডিফল্ট দিন, নয়তো স্পষ্ট error তুলুন।

///

## অন্য process-এ durable একক { #durable-units-in-another-process }

কিছু engine একটি durable একক চালায় যে রান এটি পাঠিয়েছে তার চেয়ে ভিন্ন একটি worker-এ, তাই এর প্যারামিটারকে ডেটা হিসেবে সীমা পার হতে হয়। একটি backend-এর
[`parameter_transports`][pydantic_ai.durable_exec.DurableOperationBackend.parameter_transports]
ঠিক করে কীভাবে। ডিফল্ট [`ParameterTransports`][pydantic_ai.durable_exec.ParameterTransports]
প্রতিটি operation-এর প্যারামিটার অপরিবর্তিত পাঠায়। যে engine-এর একক process-এর বাইরে চলে সেটি এটি subclass করে আর `RegisteredOperationBackend.__init__`-এ একটি instance দেয়। প্রতিটি মেথড একটি
[`ParameterTransport`][pydantic_ai.durable_exec.ParameterTransport] ফেরত দেয়, যা পাঠানোর সময় পাবলিক প্যারামিটার টাইপগুলোর একটিকে engine-এর wire ফরম্যাটে dump করে আর worker-পক্ষে আবার load করে:
[`ModelRequestParams`][pydantic_ai.durable_exec.ModelRequestParams],
[`ModelCompactMessagesParams`][pydantic_ai.durable_exec.ModelCompactMessagesParams],
[`ModelCancelSuspendedResponseParams`][pydantic_ai.durable_exec.ModelCancelSuspendedResponseParams],
[`EventStreamHandlerParams`][pydantic_ai.durable_exec.EventStreamHandlerParams],
[`ToolsetGetToolsParams`][pydantic_ai.durable_exec.ToolsetGetToolsParams],
[`ToolsetCallToolParams`][pydantic_ai.durable_exec.ToolsetCallToolParams],
[`DynamicToolsetCallToolParams`][pydantic_ai.durable_exec.DynamicToolsetCallToolParams],
[`CapabilityOperationParams`][pydantic_ai.durable_exec.CapabilityOperationParams] আর
[`WorkspaceCallParams`][pydantic_ai.durable_exec.WorkspaceCallParams]।
backend-এর `register` প্রতিটি [`DurableOperation`][pydantic_ai.durable_exec.DurableOperation] পায়
আর একটি [`BoundDurableOperation`][pydantic_ai.durable_exec.BoundDurableOperation] ফেরত দেয়। এর worker-পক্ষের handler [`durable_unit_scope`][pydantic_ai.durable_exec.durable_unit_scope]-এর ভেতরে চালান, যাতে এককের ভেতর থেকে ডাকা একটি durable operation আরেকটি একক নির্ধারণ না করে সরাসরি চলে।

প্রতিটি প্যারামিটার টাইপ রানের `RunContext` বহন করে (`run_context` হিসেবে, বা toolset প্যারামিটারে `ctx`; একটি রানের বাইরে একটি স্থগিত response বাতিল হলে এটি `None`), আর সেই context এমন অবজেক্ট রাখে যা serialize করা যায় না। এর জন্য [`DurableRunContext`][pydantic_ai.durable_exec.DurableRunContext] ব্যবহার করুন:
`DurableRunContext.serialize_run_context(ctx)` পার হতে পারে এমন ফিল্ডের একটি mapping ফেরত দেয়, যা engine নিজের codec দিয়ে encode করে, আর `DurableRunContext.restore(...)` worker-পক্ষে context আবার তৈরি করে আর worker-এর এজেন্ট ও workspace আবার যুক্ত করে। রানের validation context প্রথমবার পড়ার সময় এজেন্টের `validation_context` সেটিং থেকে আবার তৈরি হয়।

ফাংশন টুলের আর্গুমেন্ট আসে JSON-decode করা মান হিসেবে, টুলের schema যে Python মান তৈরি করে তা হিসেবে নয়। `ParameterTransports.prepare_function_call` override করে [`revalidate_function_call`][pydantic_ai.durable_exec.revalidate_function_call]-এর ফল ফেরত দিন, যা পাঠানো না হলে টুল আবার খোঁজে আর worker-পক্ষে আর্গুমেন্ট যাচাই করে।
বহন করা হয়নি এমন একটি ফিল্ড পড়লে এমন একটি ডিফল্ট ফেরত না দিয়ে একটি `UserError` ওঠে, যাকে রান state ভেবে ভুল করা যেত। আপনার engine-এর জন্য ওই error-এর ভাষা ঠিক করতে `unavailable_field_message` override করুন।
আপনার ব্যবহারকারীরা আপনার context subclass করে আরও ফিল্ড বহন করতে `serialize_run_context` override করতে পারেন।
Temporal-এর [`TemporalRunContext`][pydantic_ai.durable_exec.temporal.TemporalRunContext] এমনই একটি subclass।

একটি process-এর-বাইরের engine অন্য যে গঠন-একক নিয়ে কাজ করে:

- [`DurableOperationConfig`][pydantic_ai.durable_exec.DurableOperationConfig] হলো সেই protocol যা
  `RoleBasedOperationConfig` বাস্তবায়ন করে, সেই engine-এর জন্য যারা নিজের মতো config মীমাংসা করে।
- [`ResultCodec`][pydantic_ai.durable_exec.ResultCodec] আর
  [`CacheIdentity`][pydantic_ai.durable_exec.CacheIdentity] হলো একটি `DurableOperation`-এর `result_codec` আর
  `cache_identity`: এর ফল কীভাবে সীমা পার হয়, আর একটি hash-key ভিত্তিক engine কোন input তার cache key হিসেবে ব্যবহার করে।
- [`CallToolResult`][pydantic_ai.durable_exec.CallToolResult],
  [`DynamicToolsResult`][pydantic_ai.durable_exec.DynamicToolsResult] আর
  [`WorkspaceCallResult`][pydantic_ai.durable_exec.WorkspaceCallResult] হলো টুল কল, dynamic toolset খোঁজা আর workspace operation-এর ফলের টাইপ। একটি capability operation-এর ফলের টাইপ হলো এর [`CapabilityMethodDeclaration`][pydantic_ai.durable_exec.CapabilityMethodDeclaration]-এর `result_type`-এ প্রয়োগ করা [`capability_operation_result_type`][pydantic_ai.durable_exec.capability_operation_result_type]। একটি engine নিজে ফল decode করলে এগুলো আপনার codec-এ দিন।
- [`ModelRequestContextProjection`][pydantic_ai.durable_exec.ModelRequestContextProjection] হলো একটি মডেল রিকোয়েস্ট context-এর serialize-যোগ্য রূপ, যা একটি জীবন্ত মডেল বহন করে যা সীমা পার হতে পারে না।

## সংরক্ষিত নাম আর উদ্ধার { #persisted-names-and-recovery }

Operation-এর নাম হলো সংরক্ষিত সামঞ্জস্য-ডেটা। এগুলো Python ক্লাসের নামের ওপর নির্ভর করে না।
[`JournalOperationNamer`][pydantic_ai.durable_exec.JournalOperationNamer] মানক ক্রম-ভিত্তিক নামকরণ পদ্ধতি দেয়; engine-এর ভিন্ন প্রয়োজন থাকলে
[`DurableOperationNamer`][pydantic_ai.durable_exec.DurableOperationNamer] বাস্তবায়ন করুন। এজেন্টের নাম, model ID, toolset ID, capability ID বা operation নাম refactor করার আগে টেস্টে প্রতিটি তৈরি নাম pin করুন। migration ছাড়া একটি নাম-বদল চলমান execution-কে তাদের লেখা কাজ খুঁজে পেতে বাধা দেয়।

namer টাইপ করা operation ID আর একটি ঐচ্ছিক keyword-only `label` পায়। যে operation-এর একটি invocation-নির্দিষ্ট প্রত্যয় লাগে, সেগুলো ঘোষণার সময় একটি টাইপ করা `invocation_label` callable দেয়। বিল্ট-ইন tool-call আর argument-validation operation টুলের নাম ব্যবহার করে। Namer-দের একটি operation-এর প্যারামিটার অবজেক্ট পরীক্ষা করা উচিত নয়।

একটি durable একক একাধিকবার চলতে পারে, যখন একটি worker এর side effect-এর পরে কিন্তু checkpoint commit হওয়ার আগে ব্যর্থ হয়। তাই টুল আর decorate করা capability operation idempotent হওয়া উচিত, যদি না engine একটি উপযুক্ত at-most-once মোড দেয়। একটি ইন্টিগ্রেশন প্রকাশের আগে replay আর উদ্ধার, resource গুটানো, control-flow exception, সংরক্ষিত-আউটপুট আপগ্রেড আর durable runtime-এর বাইরে সাধারণ চালানো টেস্ট করুন।

একটি replay করা বা উদ্ধার হওয়া রানকে একই পরিচয়ও পেতে হবে। durable context-এর ভেতরে,
[`get_default_run_id()`][pydantic_ai.capabilities.AbstractCapability.get_default_run_id] override করে একটি replay-স্থিতিশীল ID ফেরত দিন, যেমন workflow instance ID থেকে তৈরি একটি, আর
[`get_default_conversation_id()`][pydantic_ai.capabilities.AbstractCapability.get_default_conversation_id] থেকে
[`conversation_id_from_run_id(run_id)`][pydantic_ai.durable_exec.conversation_id_from_run_id] ফেরত দিন,
যেমন Temporal, DBOS আর Prefect capability করে। একই workflow-এর প্রতিটি এজেন্ট রানের নিজের `run_id` লাগে।

capability লেখকরা কীভাবে decorate করা মেথড দেন, যা একই backend দিয়ে আসে, তা দেখুন [durable capability operations](../capabilities/custom.md#durable-capability-operations)-এ।

/// check | সংক্ষেপে মনে রাখুন

* callback-ভিত্তিক SDK → `CallableOperationBackend.execute`; আগে-নিবন্ধন SDK → `RegisteredOperationBackend.register`।
* `DurabilityEngineSpec`-এ engine-এর ঘোষণামূলক বৈশিষ্ট্য; ভুল ঘোষণা ক্লাস সংজ্ঞার সময়ই ধরা পড়ে।
* SDK নিজে serialize করলে `IDENTITY_CODEC`, নিজে JSON journal লিখলে `JSON_CODEC`।
* `DurableOperationId` মেলানোর সময় সবসময় একটি ডিফল্ট শাখা রাখুন।
* অন্য process-এ চললে `ParameterTransports` আর `DurableRunContext` দিয়ে প্যারামিটার পার করুন।
* সংরক্ষিত নাম টেস্টে pin করুন; replay-স্থিতিশীল `run_id` দিন।

///
