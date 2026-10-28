# Workspace { #workspaces }

/// note | এই পেজে যা শিখবেন

* Workspace কী: এজেন্টের কাজ করার "জায়গা", যেখানে সে কমান্ড চালায় আর ফাইল পড়ে-লেখে।
* `LocalWorkspace` (আপনার কম্পিউটারের একটি ফোল্ডার) বনাম cloud sandbox, আর কোডে না বদলে একটি থেকে আরেকটিতে যাওয়া।
* পরের রানে একই workspace-এ কাজ চালিয়ে যাওয়া, আরেক এজেন্টকে workspace দেওয়া, শুধু-পড়ার অনুমতি।
* টুলে `ctx.workspace` ব্যবহার, নিরাপত্তা, durable execution, আর নিজের backend লেখা।

///

একটি workspace হলো এমন একটি পরিবেশ যা আপনার এজেন্ট ব্যবহার করতে পারে: সে সেখানে কমান্ড চালায় আর ফাইল পড়ে ও লেখে।
এটি আপনার মেশিনের একটি ডিরেক্টরি বা cloud-এর একটি sandbox হতে পারে, আর আপনার টুলের জানার দরকার নেই
কোনটি, কারণ তারা সবাই এটি [`ctx.workspace`][pydantic_ai.tools.RunContext.workspace] দিয়ে ব্যবহার করে।

/// tip | উদাহরণ দিয়ে বুঝি

একজন মিস্ত্রি (এজেন্ট) আর তার কর্মশালা (workspace) ভাবুন। কর্মশালা আপনার নিজের গ্যারেজ হতে পারে (`LocalWorkspace`) বা ভাড়া করা একটি আলাদা ঘর (sandbox)। মিস্ত্রির হাতুড়ি-করাত (টুল) দুই জায়গাতেই একইভাবে কাজ করে। পার্থক্য হলো: গ্যারেজে ভুল হলে আপনার জিনিস ভাঙে, ভাড়ার ঘরে ভাঙলে আপনার বাড়ি নিরাপদ।

///

## এজেন্টকে একটি পরিবেশ দিন { #give-an-agent-an-environment }

```python title="workspace_agent.py"
import asyncio

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.workspaces import WorkspaceError

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[LocalWorkspace('.')],
)


@agent.tool
async def execute(ctx: RunContext, command: list[str]) -> str:
    """Run a command in the project directory."""
    try:
        result = await ctx.workspace.run(command, timeout=60)
    except WorkspaceError as error:  # e.g. a timeout, or a read-only workspace
        raise ModelRetry(str(error))
    return result.stdout if result.exit_code == 0 else f'[exit {result.exit_code}] {result.stderr}'


async def main() -> None:
    result = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
    print(result.output)
    #> fizzbuzz.py is written and runs clean.


if __name__ == '__main__':
    asyncio.run(main())
```

- `LocalWorkspace('.')` প্রতিটি রানকে বর্তমান ডিরেক্টরি দেয়। কমান্ড সেখান থেকে শুরু হয়, আর আপেক্ষিক
  path সেটির সাপেক্ষে ধরা হয়।
- `ctx.workspace.run(...)` কমান্ডের `exit_code`, `stdout` আর `stderr` ফেরত দেয়। একটি ব্যর্থ কমান্ড
  একটি সাধারণ ফল, তাই মডেল দেখে কী ভুল হয়েছে আর তা ঠিক করতে পারে।
- `timeout=60` আটকে যাওয়া একটি কমান্ড একটি
  [`WorkspaceTimeoutError`][pydantic_ai.workspaces.WorkspaceTimeoutError] দিয়ে থামায়। যেকোনো
  [`WorkspaceError`][pydantic_ai.workspaces.WorkspaceError]-কে `ModelRetry`-তে রূপান্তর করলে মডেল রান শেষ না করে
  অন্য কিছু চেষ্টা করতে পারে।

এই টুলগুলো আপনাকে খুব কমই নিজে লিখতে হয়। [Pydantic AI Harness](harness/index.md)-এর
`Coder`, `FileSystem` আর `Shell` capability মডেলকে ফাইল, সার্চ আর shell টুল দেয়, যা রানের যেকোনো
workspace-এ কাজ করে।

## এটিকে একটি sandbox-এ সরান { #move-it-into-a-sandbox }

`LocalWorkspace` মডেলের কমান্ড আপনার মেশিনে, আপনি হিসেবে চালায়। এগুলো কোনো বিচ্ছিন্ন জায়গায় চালাতে,
এটিকে harness-এর একটি sandbox দিয়ে বদলে দিন। আর কিছুই বদলায় না: একই টুল এখন sandbox-এ চলে।

```python
from pydantic_ai import Agent
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.e2b_sandbox import E2BSandbox

agent = Agent('anthropic:claude-opus-5-5', capabilities=[E2BSandbox(), Coder()])
result = agent.run_sync('Clone https://github.com/pydantic/pydantic-ai and run its tests.')
```

[harness](harness/index.md)-এ Modal, E2B, Sprites আর Daytona-র জন্য sandbox আছে, আর একটি লোকাল smolvm microVM। একটি
sandbox তৈরি হয় রান প্রথম যখন এটি ব্যবহার করে (একটি টুল কল, বা রানের শুরুতে `Coder` রিপোর
নির্দেশনা লোড করলে; durable রান শুরুর সময়েই এটি তৈরি করে), আর রানের পরেও চলতে থাকে যতক্ষণ না আপনি বা এর
provider এটি থামায়; দেখুন [Cleaning up](#cleaning-up)। রান যদি এটি কখনো ব্যবহার না করে, তাহলে `ref=None`-সহ একটি রানের পরে `result.workspace`-এ একটি মেথড ডাকলে এমন একটি নতুন sandbox তৈরি হতে পারে যা কোনো বার্তায় রেকর্ড হয় না। একটি রানের পরে workspace ব্যবহারের আগে ref পরীক্ষা করুন, আর আপনার তৈরি যেকোনো নতুন sandbox পরিষ্কারের ব্যবস্থা রাখুন।

/// warning | খরচের দিকে খেয়াল

cloud sandbox রান শেষ হলে নিজে থেকে বন্ধ হয় না, আর চলতে থাকা মানে বিল উঠতে থাকা। প্রতিটি sandbox কখন মুছবেন তা আগে থেকে ঠিক করে রাখুন ([Cleaning up](#cleaning-up))।

///

## যেখানে থেমেছিলেন সেখান থেকে শুরু { #continuing-in-the-same-workspace }

পরের রানে বার্তার ইতিহাস দিন, আর সেটি একই workspace-এ চলতে থাকে। একটি sandbox-এ,
প্রথম রানের ফাইল আর ইনস্টল করা প্যাকেজ তখনো সেখানে থাকে:

```python
from workspace_agent import agent


async def main() -> None:
    first = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
    await agent.run('Now add a test for it.', message_history=first.all_messages())
```

এটি কাজ করে কারণ প্রতিটি মডেল উত্তর যে workspace-এ চলেছে তা রেকর্ড করে, একটি
[`WorkspaceRef`][pydantic_ai.workspaces.WorkspaceRef] হিসেবে
[`workspace_ref`][pydantic_ai.messages.ModelResponse.workspace_ref]-এ। পরের রান সেটি
সর্বশেষ উত্তরে খুঁজে পায় আর সেই workspace-এ যুক্ত হয়। রেফারেন্সটি বার্তার অংশ, তাই আপনি সেগুলো
যেভাবেই সংরক্ষণ করুন, এটি টিকে থাকে:

```python
from pydantic_ai import ModelMessagesTypeAdapter

from workspace_agent import agent


async def main() -> None:
    first = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
    print(first.response.workspace_ref == first.workspace.ref)
    #> True
    saved = first.all_messages_json()  # store it in your database

    history = ModelMessagesTypeAdapter.validate_json(saved)
    await agent.run('Now add a test for it.', message_history=history)
```

ইতিহাস ছাড়া চালিয়ে যেতে, যেমন একই প্রজেক্ট নিয়ে একটি নতুন কথোপকথনে, রানের ব্যবহৃত
রেফারেন্সটি সংরক্ষণ করুন আর `workspace=` হিসেবে দিন:

```python
from workspace_agent import agent


async def main() -> None:
    first = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
    ref = first.workspace.ref  # a small dataclass: `provider` and `id`

    await agent.run('Explain what fizzbuzz.py does.', workspace=ref)
```

- রান প্রথম ব্যবহার না করা পর্যন্ত একটি sandbox-এর `ref` হলো `None`, তাই যে রান কখনো
  workspace ছোঁয়নি সে কোনো রেফারেন্স রেকর্ড করে না। পরের যে দফা এটি ব্যবহার করে না, সে আগের রেফারেন্সই রাখে।
- একটি রেফারেন্স যে sandbox-এর নাম বলে সেটি আর না থাকলে, রানে এর প্রথম ব্যবহার (durable রানে
  রানের শুরুতে) একটি খালি sandbox-এ চুপচাপ নতুন করে শুরু না করে
  [`WorkspaceUnavailableError`][pydantic_ai.workspaces.WorkspaceUnavailableError] তোলে। ইচ্ছা করে নতুন করে শুরু করতে `workspace='new'` দিন।
- [`sanitize_messages`][pydantic_ai.messages.sanitize_messages] আর [UI adapter-গুলো](ui/overview.md)
  একটি ক্লায়েন্টের পাঠানো ইতিহাস থেকে রেফারেন্স সরিয়ে দেয়, যাতে একটি ক্লায়েন্ট আপনার
  এজেন্টের কাজের পরিবেশ বেছে নিতে না পারে। বদলে রেফারেন্সটি আপনার সার্ভারে সংরক্ষণ করে `workspace=` হিসেবে দিন।

## Workspace আরেক এজেন্টের হাতে দিন { #hand-the-workspace-to-another-agent }

`workspace=` একটি চালু workspace-ও নেয়। এখানে কোডিং এজেন্ট একটি দ্বিতীয় এজেন্টকে তার কাজ
পর্যালোচনা করতে বলে। পর্যালোচক একই ফাইল পড়ে, আর
[`ReadOnlyWorkspace`][pydantic_ai.workspaces.ReadOnlyWorkspace] তাকে সেগুলো বদলাতে দেয় না:

```python title="reviewer.py"
from pydantic_ai import Agent, RunContext
from pydantic_ai.workspaces import ReadOnlyWorkspace

from workspace_agent import agent

reviewer = Agent('anthropic:claude-opus-5-5', instructions='Review code. Be brief.')


@reviewer.tool
async def read_file(ctx: RunContext, path: str) -> str:
    return await ctx.workspace.read_text(path)


@agent.tool
async def ask_reviewer(ctx: RunContext, request: str) -> str:
    """Ask a reviewer to check files in this workspace."""
    review = await reviewer.run(request, workspace=ReadOnlyWorkspace(ctx.workspace), usage=ctx.usage)
    return review.output


async def main() -> None:
    result = await agent.run('Write fizzbuzz to fizzbuzz.py and run it.')
    result = await agent.run('Ask the reviewer to check fizzbuzz.py.', message_history=result.all_messages())
    print(result.output)
    #> The reviewer says fizzbuzz.py is correct.
```

পর্যালোচকের নিজের কোনো workspace capability নেই: তাকে যেখানে বলা হয় সেখানেই সে কাজ করে। একই
এজেন্ট এক রানে একটি লোকাল checkout আর পরের রানে একটি sandbox পর্যালোচনা করতে পারে।

## আপনার মেশিন নাকি একটি sandbox { #your-machine-or-a-sandbox }

`LocalWorkspace` একটি sandbox নয়: একটি কমান্ড আপনি যা পারেন তার সবকিছু পড়তে আর বদলাতে পারে, আর আপনার দেওয়া ডিরেক্টরি
শুধু ঠিক করে কমান্ড কোথা থেকে শুরু হবে। ডিরেক্টরিটি আগে থেকেই থাকতে হবে। এটি আপনার নিজের,
বিশ্বস্ত কাজে ব্যবহার করুন, আর যে কোডে বিশ্বাস নেই তার জন্য একটি sandbox।

`LocalWorkspace`-এর কমান্ড আপনার `PATH`, `HOME`, `LANG`, `LC_ALL` আর `LC_CTYPE` পায়, তাই সেগুলো
host-এর টুল আর কনফিগারেশন খুঁজে পায় আর আপনার locale ব্যবহার করে। এজেন্ট প্রসেসের বাকি
environment এরা পায় না: যা দরকার তা `env=` দিয়ে দিন, কখনো পুরো `os.environ` নয়, যা আপনার API
key মডেলের চালানো কমান্ডের হাতে তুলে দেবে:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    capabilities=[LocalWorkspace('.', env={'UV_OFFLINE': '1'})],
)
```

/// warning | সাধারণ ভুল

`env=os.environ` দেওয়া সুবিধাজনক মনে হলেও, এতে আপনার `OPENAI_API_KEY`, ডেটাবেসের পাসওয়ার্ড ইত্যাদি সব মডেলের চালানো কমান্ডের কাছে চলে যায়; একটি `env` কমান্ডই সব ফাঁস করে দিতে পারে। শুধু দরকারি ভ্যারিয়েবলগুলো বেছে দিন।

///

## টুলে workspace ব্যবহার { #using-the-workspace-in-tools }

পরিবেশ যা-ই হোক, `ctx.workspace`-এর মেথড একই:

- [`run`][pydantic_ai.workspaces.Workspace.run] একটি কমান্ড চালায়।
- [`read_text`][pydantic_ai.workspaces.Workspace.read_text] আর
  [`write_text`][pydantic_ai.workspaces.Workspace.write_text] লেখার ফাইল পড়ে আর লেখে;
  [`read_bytes`][pydantic_ai.workspaces.Workspace.read_bytes] আর
  [`write_bytes`][pydantic_ai.workspaces.Workspace.write_bytes] হুবহু বাইট দিয়ে একই কাজ করে। লেখার সময়
  অনুপস্থিত parent ডিরেক্টরি তৈরি হয়।
- [`list_dir`][pydantic_ai.workspaces.Workspace.list_dir], [`stat`][pydantic_ai.workspaces.Workspace.stat],
  [`exists`][pydantic_ai.workspaces.Workspace.exists], [`make_dir`][pydantic_ai.workspaces.Workspace.make_dir]
  আর [`remove`][pydantic_ai.workspaces.Workspace.remove] ডিরেক্টরি আর এন্ট্রি নিয়ে কাজ করে।

```python title="file_tools.py"
from pydantic_ai import ModelRetry, RunContext

from workspace_agent import agent


@agent.tool
async def read_source(ctx: RunContext, path: str) -> str:
    """Read a text file from the project."""
    try:
        return await ctx.workspace.read_text(path)
    except FileNotFoundError:
        raise ModelRetry(f'{path} does not exist.')


@agent.tool
async def save_notes(ctx: RunContext, notes: str) -> str:
    """Save notes for later steps."""
    await ctx.workspace.write_text('NOTES.md', notes)
    return 'Saved to NOTES.md.'
```

আপেক্ষিক path workspace-এর working directory-র সাপেক্ষে ধরা হয়। সেটি একটি শুরুর বিন্দু, সীমানা
নয়: `..` আর পূর্ণ (absolute) path পরিবেশের বাকি অংশে পৌঁছায়। বহনযোগ্য কমান্ডের জন্য আপেক্ষিক path ব্যবহার করুন বা
`working_dir=` সেট করুন: sandbox provider-রা ভিন্ন ভিন্ন ডিফল্ট user আর
working directory ব্যবহার করে।

একটি ভুল path সাধারণ এররটিই তোলে, যেমন `FileNotFoundError` বা `IsADirectoryError`। এটি ধরে
`ModelRetry` তুলুন যাতে মডেল আবার চেষ্টা করতে পারে; না ধরলে এটি রান শেষ করে, শুধু Temporal-এ ছাড়া, যেখানে এটি
activity-র আবার-চেষ্টার নীতি মানে (দেখুন [Durable execution](#durable-execution))। যে পরিবেশ আর নেই,
যেমন একটি কমান্ডের মাঝে মুছে ফেলা একটি sandbox, সেটি `WorkspaceUnavailableError` তোলে আর রান শেষ করে।
পরিবেশ চালু থাকা অবস্থায় একটি signal-এ মারা যাওয়া একটি কমান্ড বদলে তার exit code ফেরত দেয়।

/// info | কোন এরর কী বোঝায়

| ঘটনা | ফল |
| --- | --- |
| কমান্ড ব্যর্থ (exit code শূন্য নয়) | সাধারণ ফল; মডেল `stderr` দেখে ঠিক করে |
| সময় পেরিয়ে গেছে | `WorkspaceTimeoutError` |
| ভুল path | `FileNotFoundError` ইত্যাদি; ধরে `ModelRetry` করুন |
| পরিবেশই নেই | `WorkspaceUnavailableError`; রান শেষ |

///

## শুধু-পড়ার অনুমতি { #read-only-access }

কমান্ড আর পরিবর্তন প্রত্যাখ্যান করে টুলকে ফাইল পড়তে আর তালিকা দেখতে দিতে `read_only=True` দিন:

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace

agent = Agent('anthropic:claude-sonnet-5-5', capabilities=[LocalWorkspace('.', read_only=True)])
```

একটি প্রত্যাখ্যাত পরিবর্তন [`WorkspaceReadOnlyError`][pydantic_ai.workspaces.WorkspaceReadOnlyError] তোলে।
কমান্ডও প্রত্যাখ্যাত হয়, কারণ একটি কমান্ড ফাইল বদলাতে পারে। একটি capability তার লেখার টুল বাদ দিতে
[`ctx.workspace.read_only`][pydantic_ai.workspaces.Workspace.read_only] পরীক্ষা করতে পারে।

একটি একক রানের জন্য, তার workspace `ReadOnlyWorkspace`-এ মুড়ে `workspace=` হিসেবে দিন, যেমন
[ওপরের পর্যালোচক](#hand-the-workspace-to-another-agent) করে। নিজের নীতি লিখতে,
[`WrapperWorkspace`][pydantic_ai.workspaces.WrapperWorkspace]-এর subclass করুন, যে কাজগুলো বদলাতে চান সেগুলো
override করুন, আর বাকিগুলোর জন্য `self.wrapped` ডাকুন। wrapper কমান্ডও override বা প্রত্যাখ্যান না করলে `run()`
ফাইল-মেথডের নীতি পাশ কাটায় (এর ওপর তৈরি shell/grep টুলসহ)। Symlink-ও
একটি ফাইল root-এর বাইরে নিয়ে যেতে পারে; একটি লেখার আগে `realpath` পরীক্ষা করুন, যেমন:

```python
import posixpath

from pydantic_ai.workspaces import WorkspaceReadOnlyError, WrapperWorkspace


class RootedWrites(WrapperWorkspace):
    async def write_bytes(self, path: str, data: bytes) -> None:
        root = await self.wrapped.realpath(await self.working_dir())
        target = await self.wrapped.realpath(await self.resolve(path))
        if posixpath.commonpath((root, target)) != root:
            raise WorkspaceReadOnlyError('outside the allowed root')
        await self.wrapped.write_bytes(path, data)

    async def run(self, command, **kwargs):
        raise WorkspaceReadOnlyError('commands bypass file policy')
```

এটি একটি আগাম পরীক্ষা, একই সময়ে symlink বদলের বিরুদ্ধে কোনো নিরাপত্তা-সীমানা নয়; অবিশ্বস্ত কমান্ডের জন্য
একটি বিচ্ছিন্ন backend ব্যবহার করুন। কমান্ড বা `SupportsRealpath` ছাড়া একটি backend-এ,
`realpath` শুধু লেখা স্বাভাবিক করে; দেখুন [Resolving symlinks](#resolving-symlinks)।

## একটি রানের workspace বাছাই { #choosing-a-runs-workspace }

একটি রান তার workspace বাছে এগুলোর মধ্যে প্রথম যেটি প্রযোজ্য সেটি থেকে:

1. `workspace=` আর্গুমেন্ট।
2. `message_history`-এর সর্বশেষ উত্তরের রেফারেন্স।
3. এজেন্টের workspace capability: `LocalWorkspace`-এর জন্য তার ডিরেক্টরি, একটি sandbox
   provider-এর জন্য একটি নতুন sandbox।

`workspace=` নেয়:

- `'new'`, একটি নতুন পরিবেশ শুরু করতে আর ইতিহাসেরটি উপেক্ষা করতে।
- একটি [`WorkspaceRef`][pydantic_ai.workspaces.WorkspaceRef], যেমন একটি সংরক্ষিত `result.workspace.ref`,
  যাতে এজেন্টের capability যুক্ত হয়।
- একটি workspace বা backend, যেমন আছে তেমন ব্যবহৃত: `result.workspace`, `ctx.workspace`, বা একটি backend যেমন
  `LocalWorkspaceBackend('/tmp/scratch')`।

একটি এজেন্টের একাধিক workspace capability থাকতে পারে। রানে দেওয়াগুলোকে এজেন্টের নিজেরগুলোর আগে
জিজ্ঞেস করা হয়, প্রতিটি ক্রমানুসারে। একটি রেফারেন্স থাকলে, প্রথম যে সেটি চেনে সে workspace দেয়;
না থাকলে, প্রথম যে একটি workspace ফেরত দেয় সে দেয়। এভাবেই পুরনো কথোপকথন না ভেঙে একটি নতুন provider-এ
যাওয়া যায়: নতুন capability প্রথমে রাখুন, যাতে নতুন কথোপকথন সেটি ব্যবহার করে, আর পুরনোটি রেখে দিন,
যাতে সেখানে শুরু হওয়া কথোপকথন সেখানেই চলতে থাকে।

```python title="two_workspaces.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        LocalWorkspace('~/projects/current', id='current'),  # new conversations
        LocalWorkspace('~/projects/archive', id='archive'),  # conversations that started here
    ],
)
```

একটি capability শুধু সেই রেফারেন্সে যুক্ত হয় যা সে চেনে। `LocalWorkspace` শুধু তার নিজের
ডিরেক্টরির রেফারেন্স গ্রহণ করে, অন্য কোনোটি নয়, তাই বার্তার ইতিহাস এজেন্টকে আপনার মেশিনের আরেকটি
ডিরেক্টরিতে পাঠাতে পারে না।

যখন কোনো capability workspace দেয় না:

- `message_history`-এর একটি রেফারেন্স `UserError` তোলে যদি এজেন্টের workspace capability থাকে আর
  কোনোটিই সেটি না চেনে, যেমন provider বদলানোর পরে। `workspace='new'` দিন, বা পুরনো
  capability রেখে দিন। workspace capability নেই এমন একটি এজেন্ট, যেমন যে কথোপকথনের সারাংশ করে,
  রেফারেন্সটি উপেক্ষা করে।
- `workspace=` হিসেবে দেওয়া একটি `WorkspaceRef` `UserError` তোলে, আর `workspace='new'`-ও তোলে।
- রেফারেন্স ছাড়া, রানের কোনো workspace নেই, আর যে টুল এটি ব্যবহার করে তারা `WorkspaceUnavailableError` তোলে।

কোনো পরিবর্তন ছাড়া ফাইল দেখতে, একটি শুধু-পড়ার workspace আর পড়ার টুল ব্যবহার করুন। ফাইলে প্রবেশ ছাড়া
উত্তর দিতে, বদলে ফাইল-টুলহীন একটি এজেন্ট ব্যবহার করুন: workspace-নির্ভর টুলের একটি যুক্ত
workspace লাগে, আর `UnavailableWorkspace` ইচ্ছাকৃতভাবে সব কাজ প্রত্যাখ্যান করে।

## পরিষ্কার করা { #cleaning-up }

Pydantic AI কখনো একটি পরিবেশ মোছে না: একটি sandbox রানের পরেও চলতে থাকে যতক্ষণ না আপনি এটি মোছেন
বা এর provider-এর আয়ুষ্কালের সেটিং এটি থামায়। প্রতিটি sandbox পেজ দেখায় কীভাবে একটি মুছবেন।

একটি সফল রান `result.workspace.ref` ফেরত দেয়, তাই আপনি sandbox-এ চালিয়ে যেতে বা পরে এটি মুছতে
পারেন। একটি ব্যর্থ রান কোনো ফল ফেরত দেয় না, তাই এর sandbox একটি `on_run_error` hook-এ মুছুন, যেখানে
`ctx.workspace.ref` তার নাম বলে। একটি রান ব্যর্থ হলে `after_run` চলে না। প্রতিটি রানের পরে sandbox মুছে দিলে, তার ইতিহাস চালিয়ে যাওয়ার সময় `workspace='new'` দিন; নইলে পরের রান `WorkspaceUnavailableError` তোলে, কারণ রেকর্ড করা পরিবেশটি আর নেই।

## Durable execution { #durable-execution }

[Temporal](durable_execution/temporal.md), [DBOS](durable_execution/dbos.md) বা
[Prefect](durable_execution/prefect.md)-এর অধীনে, এজেন্ট তৈরির সময় durability capability-র পাশে
workspace capability যুক্ত করুন:

```python title="durable_workspace.py"
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.durable_exec.temporal import TemporalDurability

agent = Agent(
    'anthropic:claude-sonnet-5-5',
    name='fizzbuzz',  # names the agent's Temporal activities
    capabilities=[LocalWorkspace('.'), TemporalDurability()],
)
```

`TemporalDurability`-কে `DBOSDurability` বা `PrefectDurability` দিয়ে বদলান, এজেন্টের আর কিছুই
বদলায় না। শুধু রান কোথায় শুরু হয় তাতে পার্থক্য: `PydanticAIPlugin`-সহ একটি worker-এ একটি Temporal workflow ক্লাস,
`DBOS.launch()`-এর পরে একটি `@DBOS.workflow()` ফাংশন, বা একটি Prefect `@flow`, যেমন প্রতিটি
[engine গাইড](durable_execution/overview.md) দেখায়।

টুল `ctx.workspace` ব্যবহার করে যেমন একটি সাধারণ রানে করত। Temporal-এ, যে টুলের
orchestration workflow-তে চালাতে হবে (যেমন, লেখার আগে একটি ফাইল পরিবর্তন অনুমোদন করাতে), সে
তার টুল সংজ্ঞায় `metadata={'temporal': False}` সেট করতে পারে; সে যে workspace কল করে সেগুলো তবুও
activity হিসেবে চলে।

- একটি workflow বা flow-এর ভেতরে, একটি রান শুরুর সময় তার পরিবেশ তৈরি করে বা যুক্ত হয়, এমনকি কোনো
  টুল তা ব্যবহার না করলেও; আবার-চেষ্টা, replay আর পুনরুদ্ধার সেই একই পরিবেশে আবার যুক্ত হয়। সাধারণ রান
  অলস (lazy) থাকে। পরিবেশ তৈরির পরে কিন্তু তা রেকর্ড হওয়ার আগে একটি worker মারা গেলে, আবার-চেষ্টা
  একটি দ্বিতীয় পরিবেশ তৈরি করতে পারে; একটি sandbox-এর ক্ষেত্রে, provider-এর টুল দিয়ে প্রথমটি পরিষ্কার করুন।
- একটি স্পষ্ট `run_id` ছাড়া, একটি workflow বা flow-এর ভেতরের রান Temporal
  execution run ID, DBOS workflow ID বা Prefect flow run ID থেকে বের করা একটি ID পায়, তাই একটি worker পুনরায় চালু
  বা flow আবার-চেষ্টার পরেও এর workspace অবস্থা খুঁজে পাওয়া যায়।
- DBOS-এ, একটি workspace-সহ রান তার টুল কল একটি একটি করে চালায়: DBOS ধাপগুলো শুরুর সাথে সাথে
  নম্বর দেয়, তাই একাধিক workspace কল করা একসাথে চলা টুলগুলো নির্ভরযোগ্যভাবে replay করা যেত না।
- কলের মাঝে একটি worker মারা গেলে একটি workspace কল আবার চলতে পারে: একটি টুলের ভেতরে এটি টুলের সাথে আবার চেষ্টা করে,
  আর workflow কোড থেকে এটি engine-এর activity বা step সেটিং মানে। Temporal আর Prefect-এ,
  workspace timeout, আউটপুট-সীমার ব্যর্থতা, শুধু-পড়ার প্রত্যাখ্যান আর হারানো পরিবেশ কখনো
  আবার চেষ্টা হয় না। অন্য exception, যেমন `FileNotFoundError`, আবার-চেষ্টার নীতি মানে, যা Temporal-এ ডিফল্টভাবে
  সীমাহীন আবার চেষ্টা করে: এগুলো ধরে `ModelRetry` তুলুন, বা `maximum_attempts` সেট করুন।
- Temporal-এ, একটি কমান্ড একটি activity-র `start_to_close_timeout`-এর মধ্যে চলে, ডিফল্ট 60 সেকেন্ড,
  তার নিজের `timeout` যা-ই হোক। একটি টুলের ভেতরে সেটি টুলের activity; এটি বাড়াতে
  `metadata={'temporal': ActivityConfig(start_to_close_timeout=...)}`। workflow কোড থেকে এটি
  `activity_config`; সেটি সেট করলে, তাতে একটি `start_to_close_timeout` রাখুন, যেমন
  `activity_config={'start_to_close_timeout': timedelta(seconds=60), 'retry_policy': RetryPolicy(maximum_attempts=3)}`।
- `workspace=` শুধু একটি রেফারেন্স পাঠায়, আর রান এজেন্টের নিজের capability থেকে workspace আবার
  তৈরি করে। একটি `ReadOnlyWorkspace(...)` আর্গুমেন্ট `UserError` তোলে যদি আবার তৈরিতে তার
  শুধু-পড়ার নীতি বাদ পড়ত, আর তোলে এখনো ref নেই এমন একটি চালু backend বা রানে দেওয়া এমন একটি capability
  যা workspace-এর টাইপ বা নীতি বদলায়। একটি রান-স্তরের workspace capability-র অন্য সেটিং,
  যেমন একটি sandbox image, প্রযোজ্য হয় না: প্রতিটি একক এজেন্টেরটি থেকে workspace আবার তৈরি করে। ref ছাড়া একটি আগের `result.workspace` একটি নতুন workspace শুরু করে। বদলে নীতি এজেন্টের capability-তে রাখুন, যেমন
  `LocalWorkspace(..., read_only=True)`।
- `workspace.backend` workflow কোডে পাওয়া যায় না, যার মধ্যে DBOS-এর ফাংশন টুল আর
  `metadata={'temporal': False}`-সহ Temporal টুল পড়ে। provider-এর নিজস্ব API-তে পৌঁছান এমন একটি টুল থেকে যা
  একটি activity বা task হিসেবে চলে।
- একটি workflow বা flow-এর ভেতরে, deprecated `TemporalAgent`, `DBOSAgent` আর `PrefectAgent` wrapper
  একটি workspace প্রত্যাখ্যান করে; বদলে durability capability ব্যবহার করুন।
- Temporal-এ, `LocalWorkspace` কল যে worker তুলে নেয় তার activity-তে চলে, তাই প্রতিটি
  worker-এর একই পূর্ণ path-এ, তাদের ভাগ করা storage-এ ডিরেক্টরিটি লাগবে।

/// warning | চলমান রান থাকা অবস্থায় workspace যোগ করা

একটি এজেন্টে workspace যোগ করলে তার রান কী রেকর্ড করে তা বদলায়, তাই পরিবর্তনের আগে শুরু হওয়া রান আর
তাদের ইতিহাসের সাথে মেলে না: Temporal replay একটি nondeterminism এরর দিয়ে ব্যর্থ হয়, আর DBOS
workflow পুনরুদ্ধার করতে পারে না। আগে চলমান রানগুলো শেষ হতে দিন, বা পরিবর্তনটি আলাদাভাবে deploy করুন:
Temporal worker versioning বা একটি নতুন task queue দিয়ে, বা একটি নতুন DBOS অ্যাপ্লিকেশন সংস্করণ দিয়ে। Prefect-এ,
deploy করার আগে চলমান flow শেষ হতে দিন। চলমান রান ব্যবহার করছে এমন একটি capability সরালেও
তাদের ইতিহাস একইভাবে বদলায়।

///

### Harness-এর workspace capability { #harness-workspace-capabilities }

workspace-এ কাজ করা [Pydantic AI Harness](harness/index.md) capability, যেমন
[`Coder`](harness/coder.md), [`Shell`](harness/shell.md), [`FileSystem`](harness/filesystem.md),
[`RepoContext`](harness/repo-context.md) আর [`Researcher`](harness/researcher.md), Temporal,
DBOS আর Prefect-এর অধীনে কাজ করে। এগুলো workspace আর durability capability-র পাশে যুক্ত করুন, যেমন
`capabilities=[LocalWorkspace('.'), Coder(), TemporalDurability()]`। পরের যে রান একটি নতুন workflow বা flow-এ
`message_history` থেকে কথোপকথন চালিয়ে যায়, সে
[একই পরিবেশে](#continuing-in-the-same-workspace) কাজ করে।

| সুবিধা | Temporal | DBOS | Prefect |
|---|---|---|---|
| ফাইল টুল: পড়া, লেখা, সম্পাদনা, সার্চ | হ্যাঁ | হ্যাঁ | হ্যাঁ |
| কমান্ড: `run_command`, `shell` | হ্যাঁ, [activity timeout](durable_execution/temporal.md#harness-command-timeouts)-এর মধ্যে | হ্যাঁ | হ্যাঁ |
| Background job: `start_command`, `check_command`, `stop_command` | হ্যাঁ | হ্যাঁ | হ্যাঁ |
| টিকে থাকা `cd`: `Shell(persist_cwd=True)` | হ্যাঁ | হ্যাঁ | হ্যাঁ |
| ফাইল-পরিবর্তন অনুমোদন: [`FileChangeRequestEvent`](harness/filesystem.md#events) | হ্যাঁ | হ্যাঁ | হ্যাঁ |
| সরাসরি টুল event | [শুধু ফাইল-পরিবর্তনের অনুরোধ আর লেখার event](durable_execution/temporal.md#harness-workspace-capabilities) | হ্যাঁ | হ্যাঁ |
| দায়িত্ব অর্পণ: `delegate_task` | [শুধু `self`-কে](durable_execution/temporal.md#harness-workspace-capabilities) | হ্যাঁ | হ্যাঁ |

[Temporal গাইড](durable_execution/temporal.md#harness-workspace-capabilities) Temporal-এর
সীমাবদ্ধতা ব্যাখ্যা করে।

- **টিকে থাকা `cd`** workspace-এ `.pydantic-ai-harness/shell/run-state/`-এর নিচে রাখা হয়, রান ID দিয়ে
  চিহ্নিত, তাই পুনরায় চালুর পরে একটি নতুন worker একই ডিরেক্টরিতে চালিয়ে যায়। রান শেষ হলে
  ফাইলটি মুছে যায়। একটি রানের কমান্ডগুলো ক্রমানুসারে চলা উচিত; ডিরেক্টরি বদলানো একই সময়ের কমান্ড
  একে অপরের অবস্থা মুছে লিখতে পারে।
- **Background job** রান আর টুল-কল ID দিয়ে চিহ্নিত, তাই আবার-চেষ্টা করা একটি `start_command`
  একটি দ্বিতীয় প্রসেস শুরু না করে job-টিতে আবার যুক্ত হয়। job ডিরেক্টরি দাবি করার পরে একটি launch ব্যর্থ হলে,
  আবার-চেষ্টা একটি অপেক্ষমাণ launch জানায়; প্রসেস থেমে গেলে, `.pydantic-ai-harness/shell/`-এর নিচের
  পুরনো job ফাইল মুছে দিন।

বাকিটা engine গাইডে আছে, যেমন Temporal worker-জুড়ে capability মেলানো।

## একটি capability থেকে workspace দেওয়া { #supplying-a-workspace-from-a-capability }

নিজের capability থেকে একটি workspace দিতে,
[`get_workspace`][pydantic_ai.capabilities.AbstractCapability.get_workspace] বাস্তবায়ন করুন। এটি প্রতিটি
ব্যবহারকারীকে তার নিজের ডিরেক্টরিতে পাঠায়, যার নাম রান `deps` হিসেবে যে user ID পায় তা দিয়ে:

```python title="per_user_workspace.py"
from dataclasses import dataclass
from pathlib import Path

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.workspaces import LocalWorkspaceBackend, WorkspaceBackend, WorkspaceRef


@dataclass
class UserDirectory(AbstractCapability[str]):
    base_dir: Path

    def get_workspace(self, ctx: RunContext[str], *, ref: WorkspaceRef | None) -> WorkspaceBackend | None:
        if not ctx.deps.isalnum():  # keeps an ID like '../other-user' from leaving base_dir
            raise ValueError(f'Invalid user ID: {ctx.deps!r}')
        backend = LocalWorkspaceBackend(self.base_dir / ctx.deps)
        if ref is not None and ref != backend.ref:
            return None  # not this user's directory
        return backend
```

`LocalWorkspaceBackend` কখনো তার ডিরেক্টরি তৈরি করে না, আর ডিরেক্টরিটি না থাকা পর্যন্ত প্রতিটি কাজ, পূর্ণ path-সহ,
`WorkspaceUnavailableError` তোলে, তাই ব্যবহারকারী তৈরির সময়েই প্রতিটি ব্যবহারকারীর ডিরেক্টরি তৈরি করুন। এটি ব্যবহারকারীরা কোথা থেকে শুরু করে তা আলাদা করে; `LocalWorkspace`-এর মতো, এটি কিছুই বিচ্ছিন্ন করে না।

- `ref=None` হলে, একটি নতুন বা ডিফল্ট পরিবেশের জন্য backend ফেরত দিন।
- আপনার চেনা একটি `ref` হলে, তাতে যুক্ত হয় এমন একটি backend ফেরত দিন। অন্য যেকোনোটির জন্য `None` ফেরত দিন।
  Ref id সংরক্ষিত বা অবিশ্বস্ত ইতিহাস থেকে আসতে পারে: path বা identifier হিসেবে ব্যবহারের আগে সেগুলো যাচাই করুন।
- একটি নীতি প্রয়োগ করতে, backend-এর চারপাশে একটি `Workspace` ফেরত দিন, যেমন
  `ReadOnlyWorkspace(Workspace(backend))`।
- `get_workspace`-এ I/O করবেন না বা অবস্থা রাখবেন না: এটি প্রতি রানে একাধিকবার ডাকা হতে পারে। backend-এর
  প্রথম কাজে সংযোগ করুন।
- যে capability একটি workspace দেয় সে `defer_loading=True` ব্যবহার করতে পারে না: workspace বাছাই হয়
  রান শুরুর সময়।

যে capability-র একটি workspace লাগে সে `before_run`-এ
[`ctx.workspace.attached`][pydantic_ai.workspaces.Workspace.attached] পরীক্ষা করতে পারে। কিছুই workspace না দিলে
এটি `False`, তাই রানটি প্রথম টুল কলে নয়, শুরুতেই ব্যর্থ হয়, আর কী যুক্ত করতে হবে তার নাম বলে:

```python
from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.exceptions import UserError


class ProjectNotes(AbstractCapability):
    async def before_run(self, ctx: RunContext) -> None:
        if not ctx.workspace.attached:
            raise UserError("`ProjectNotes` needs a workspace. Attach one, such as `LocalWorkspace('.')`.")
```

Realtime session বর্তমানে workspace বাছাই করে না, এজেন্টের একটি workspace capability থাকলেও।
একটি realtime session-এর workspace টুল একটি দ্বিতীয় capability-র পরামর্শ না দিয়ে এই সীমাবদ্ধতা জানায়।

টেস্টের জন্য, `with agent.override(workspace=LocalWorkspaceBackend(path)):` সাময়িকভাবে এজেন্টের capability, ইতিহাসের ref, বা একটি প্রতি-রানের `workspace=`-এর বদলে একটি লোকাল
workspace ব্যবহার করে, যেমন `override(model=)` মডেলের জন্য করে।

## Third-party workspace { #third-party-workspaces }

অন্য প্যাকেজও একই workspace interface বাস্তবায়ন করে। [`pydantic-ai-backend`](https://github.com/vstorm-co/pydantic-ai-backend), [Vstorm](https://vstorm.co/)-এর একটি কমিউনিটি প্যাকেজ, Kubernetes pod, লোকাল Docker container, Daytona, একটি `sandboxd` সার্ভিস যা Docker socket ধরে রাখে যাতে আপনার অ্যাপ্লিকেশন container-কে তা রাখতে না হয়, আর আপনার অ্যাপ্লিকেশন নিজের ডেটাবেসে রাখতে পারে এমন in-memory JSON ডকুমেন্ট-ভিত্তিক workspace দেয়।

এই তালিকায় একটি প্যাকেজ যোগ করতে, একটি pull request খুলুন। নিজেরটি বানাতে, দেখুন [Writing a backend](#writing-a-backend)।

## একটি backend লেখা { #writing-a-backend }

একটি backend হলো সেই অবজেক্ট যা একটি পরিবেশের সাথে কথা বলে; `Workspace` এটিকে মুড়ে টুলকে
`ctx.workspace` মেথড দেয়। একটি [`WorkspaceBackend`][pydantic_ai.workspaces.WorkspaceBackend]
`ref` আর `working_dir` বাস্তবায়ন করে, তারপর যোগ করে [`SupportsCommands`][pydantic_ai.workspaces.SupportsCommands],
[`SupportsFilesystem`][pydantic_ai.workspaces.SupportsFilesystem], বা দুটোই। শুধু কমান্ড থাকলে,
`ctx.workspace` shell দিয়ে ফাইলের কাজগুলো বের করে নেয়। শুধু filesystem থাকলে, ফাইল টুল কাজ করে
আর `ctx.workspace.run` `UserError` তোলে। shell-নির্ভর পড়ার জন্য সাধারণ ফাইল লাগে (FIFO বা device নয়)। এগুলো বড় ফাইল আর ডিরেক্টরির তালিকা সীমিত টুকরোয় স্থানান্তর করে, তবে shell-নির্ভর ফাইলের কাজ provider-এর নিজস্ব ফাইল API-র চেয়ে ধীর। লোকাল আর shell-নির্ভর ফাইলের কাজ workspace root বা তার কোনো পূর্বপুরুষ মুছতে অস্বীকার করে, আর লোকাল লেখা একটি মুছে ফেলা workspace ডিরেক্টরি আবার তৈরি করে না। `LocalWorkspace` শুধু সেই ref-এ চালিয়ে যায় যা তার কনফিগার করা ডিরেক্টরির নাম ঠিক লেখা অনুযায়ী বলে, তাই একটি symlink দিয়ে লেখা ref প্রত্যাখ্যাত হয়।
দুটোই থাকলে, সেগুলোকে একই পরিবেশে পৌঁছাতে হবে। শুধু-filesystem একটি backend, যার storage
symlink রাখতে পারে, তার `SupportsRealpath`-ও বাস্তবায়ন করা উচিত; দেখুন [Resolving symlinks](#resolving-symlinks)।

### Symlink সমাধান করা { #resolving-symlinks }

`Workspace.realpath` উত্তর দেয় "এই path আসলে কোন ফাইলে নিয়ে যায়?"। যে কোড একটি এজেন্টকে একটি
ডিরেক্টরির ভেতরে রাখে তার এই উত্তর লাগে, কারণ একটি symlink ভেতরের মনে হওয়া একটি path-কে
বাইরে নিয়ে যেতে পারে। ফাইল মেথড [`resolve(path)`][pydantic_ai.workspaces.Workspace.resolve] খোলে, যা
`..`-কে লেখা হিসেবে গুটিয়ে নেয়, তাই একটি ফাইল মেথড যে ফাইল খোলে তা পরীক্ষা করতে `realpath(await ws.resolve(path))` ব্যবহার করুন, যেমন
ওপরের `RootedWrites` উদাহরণ করে। কাঁচা path-এ `realpath(path)` kernel-কে মানে, যেখানে `..`
একটি symlink-এর লক্ষ্য থেকে ওপরে ওঠে, তাই এটি কমান্ডের জন্য উত্তর দেয়। যেমন, শুধু `/app`-এর নিচের path অনুমোদন করা একটি পরীক্ষা আর একটি লিংক
`/app/data -> /secrets` থাকলে, `/app/data/key` ভেতরের মনে হয়, কিন্তু খোলে `/secrets/key`।

/// tip | উদাহরণ দিয়ে বুঝি

Symlink হলো একটি দরজায় লাগানো "এই দরজা দিয়ে ভাঁড়ার ঘর" লেখা সাইনবোর্ড, কিন্তু দরজাটি আসলে পাশের বাড়িতে খোলে। শুধু সাইনবোর্ড (path-এর লেখা) দেখে ছাড় দিলে চলবে না; `realpath` দরজা খুলে দেখে আসলে কোথায় গেলেন।

///

Backend এর উত্তর তিনটি উপায়ের একটিতে দেয়:

- `LocalWorkspaceBackend` `os.path.realpath` ব্যবহার করে।
- কমান্ড আছে কিন্তু [`SupportsRealpath`][pydantic_ai.workspaces.SupportsRealpath] নেই এমন একটি backend
  একটি shell বিকল্প পায় যা এক কমান্ডে `readlink` দিয়ে লিংক অনুসরণ করে। যে লিংক সে পড়তে পারে না,
  যেমন `readlink` ছাড়া একটি image-এ, তা অসমাধিত না রেখে `WorkspaceError` তোলে।
- দুটোর কোনোটিই নেই এমন backend শুধু path-টি লেখা হিসেবে স্বাভাবিক করা পায়। symlink রাখতে পারে না
  এমন storage-এ, যেমন একটি object store, এটি নির্ভুল। যেখানে symlink থাকতে পারে, সেখানে harness-এর
  `FileSystem`-এর `root_dir`-এর মতো একটি path পরীক্ষা তখন শুধু লেখাটি দেখে, আর ওপরের উদাহরণটি বাইরে নিয়ে যায়।

পরীক্ষা আর পরের ফাইলের কাজ আলাদা কল, তাই এর মাঝে বদলে দেওয়া একটি লিংক
ধরা পড়ে না; অবিশ্বস্ত কোডের জন্য path পরীক্ষার ওপর নয়, sandbox-এর ওপর ভরসা করুন।

একটি cloud sandbox-এর backend দেখতে এমন (`sandbox_sdk` হলো provider-এর SDK-র প্রতিনিধি):

```python title="my_sandbox.py"
from collections.abc import Mapping

import anyio
import sandbox_sdk

from pydantic_ai.workspaces import (
    CommandResult,
    SupportsCommands,
    WorkspaceBackend,
    WorkspaceCommand,
    WorkspaceRef,
    WorkspaceUnavailableError,
)


class MySandbox(WorkspaceBackend, SupportsCommands):
    def __init__(self, ref: WorkspaceRef | None = None):
        self._ref = ref
        self._sandbox: sandbox_sdk.Sandbox | None = None
        self._lock = anyio.Lock()

    @property
    def ref(self) -> WorkspaceRef | None:
        return self._ref

    async def _connect(self) -> sandbox_sdk.Sandbox:
        async with self._lock:  # concurrent first operations share one sandbox
            if self._sandbox is None:
                if self._ref is None:
                    self._sandbox = await sandbox_sdk.Sandbox.create()
                    self._ref = WorkspaceRef(provider='my-sandbox', id=self._sandbox.id)
                else:
                    try:
                        self._sandbox = await sandbox_sdk.Sandbox.connect(self._ref.id)
                    except sandbox_sdk.NotFound as error:
                        raise WorkspaceUnavailableError(f'sandbox {self._ref.id!r} no longer exists') from error
            return self._sandbox

    async def run(
        self,
        command: WorkspaceCommand,
        *,
        shell: bool = False,
        env: Mapping[str, str] | None = None,
        timeout: float | None = None,
    ) -> CommandResult:
        sandbox = await self._connect()
        result = await sandbox.exec(command, shell=shell, env=env, timeout=timeout)
        return CommandResult(exit_code=result.exit_code, stdout=result.stdout, stderr=result.stderr)

    async def working_dir(self) -> str:
        return (await self._connect()).working_dir
```

- constructor কোনো I/O করে না। প্রথম কাজটি পরিবেশ তৈরি করে, বা `ref` যেটির নাম বলে তাতে
  যুক্ত হয়।
- পরিবেশ না থাকা পর্যন্ত `ref` হলো `None`, তারপর এটি তার নাম বলে আর কখনো বদলায় না। create কল ফেরত আসার
  সাথে সাথে, ব্যর্থ হতে পারে এমন যেকোনো প্রস্তুতির আগে এটি সেট করুন, যাতে একটি ব্যর্থ প্রস্তুতির পরেও পরিষ্কার করার জন্য একটি ref থাকে।
  যেকোনো কাজ শেষ হলেই durable execution-এর এটি সেট থাকা লাগে।
- একসাথে আসা প্রথম কাজগুলো শুধু একটি পরিবেশ তৈরি করবে আর তার ref ভাগ করবে। `Workspace` কোনো
  lock ধরে না, তাই get-or-create lock backend-এর নিজের।
- পরিবেশ তৈরি হওয়ার মাঝে বাতিল হওয়া একটি caller-এর ref হারানো চলবে না: caller চলে গেলেও তা
  রেকর্ড করা শেষ করুন। ওপরের উদাহরণ এটি বাদ দেয়; harness-এর sandbox একটি উপায় দেখায়।
- যে `ref`-এর পরিবেশ আর নেই তা `WorkspaceUnavailableError` তোলে। backend কখনো তার
  বদলি তৈরি করে না।
- একটি রান শেষ হলে backend কখনো পরিবেশ ধ্বংস করে না। যার হাতে ref, সে ঠিক করে কখন
  মুছবে; দেখুন [Cleaning up](#cleaning-up)।
- শূন্য নয় এমন একটি exit একটি ফল, exception নয়। যে প্রোগ্রাম শুরু হতে পারে না তা exit 127 (পাওয়া যায়নি)
  বা 126 (চালানো যায় না), যেমন `sh`-এ। একটি path-স্তরের ব্যর্থতা builtin ফাইল এরর তোলে, আর একটি
  timeout `WorkspaceTimeoutError` তোলে। একটি provider SDK-র নিজের সাময়িক এরর ছড়িয়ে পড়তে দিন, যাতে একটি
  durable engine সেগুলো আবার চেষ্টা করতে পারে।

একটি capability-র `get_workspace` এই backend ফেরত দেয়, আর ব্যবহারকারীরা এর provider-নির্দিষ্ট মেথডে পৌঁছায়
`ctx.workspace.backend` দিয়ে। এটি provider API-তে পৌঁছানোর একটি পালানোর পথ আর `read_only`-এর মতো wrapper নীতি
পাশ কাটায়; নীতি প্রয়োগ হতেই হবে এমন ক্ষেত্রে `ctx.workspace`-এর ফাইল/কমান্ড মেথড ব্যবহার করুন।

### একটি backend পরীক্ষা করা { #checking-a-backend }

আপনার pytest suite-এ [`WorkspaceBackendSuite`][pydantic_ai.workspaces.conformance.WorkspaceBackendSuite]-এর subclass করুন
আর এর `backend` fixture দিন। প্রতিটি টেস্ট backend চুক্তির একটি নিয়ম পরীক্ষা করে:

```python
import pytest
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai.workspaces.conformance import WorkspaceBackendSuite


class TestMyBackend(WorkspaceBackendSuite):
    @pytest.fixture(scope='class')
    @classmethod
    def backend(cls, tmp_path_factory: pytest.TempPathFactory) -> LocalWorkspaceBackend:
        return LocalWorkspaceBackend(working_dir=tmp_path_factory.mktemp('ws'))
```

suite-টির anyio pytest plugin লাগে, যা প্রতিটি নিয়ম প্রতিটি ইনস্টল করা async backend-এ চালায় (asyncio,
আর ইনস্টল থাকলে Trio)। শুধু-asyncio একটি SDK-র জন্য, `anyio_backend` fixture override করে
`'asyncio'` ফেরত দিন, আপনার `backend` fixture class-scoped হলে এটিও class-scoped। একটি class-scoped fixture প্রতি নিয়মে একটির বদলে পুরো
suite-এর জন্য একটি পরিবেশ শুরু করে। durable execution-এর অধীনে প্রতিটি workspace কল আপনার backend তার ref থেকে
আবার তৈরি করে, তাই `attach_backend` দিন, একটি factory যা একটি ref-এর জন্য backend তৈরি করে ঠিক যেভাবে আপনার capability-র
`get_workspace` করে: এটি সেই নিয়ম চালু করে যে ref দিয়ে যুক্ত একটি backend একই ফাইল আর
কমান্ডে পৌঁছায় আর সেই ref রাখে। ধ্বংস পরীক্ষা করতে,
`destroy_environment` আর `destructive_backend`-ও দিন, একটি স্বাধীন পরিবেশের factory।
দেওয়া থাকলে শেষেরটির ডিফল্ট `fresh_backend`। ধ্বংসাত্মক নিয়ম কখনো ভাগ করা `backend` fixture ব্যবহার করে না।

একটি backend প্রকাশের আগে, suite দিয়ে পরীক্ষা করুন:

- একসাথে প্রথম ব্যবহার একটি পরিবেশ তৈরি করে (এই নিয়মের জন্য `fresh_backend` দিন), একটি স্থির ref-সহ।
- কমান্ডের এরর সঠিক টাইপ ব্যবহার করে: অবৈধ আর্গুমেন্ট, অনুপস্থিত path আর অনুপলব্ধ পরিবেশ;
  timeout `WorkspaceTimeoutError` তোলে; EOF-এ থাকা stdin আর শূন্য নয় এমন exit সাধারণ ফল থাকে।
- বাতিল সামনের কমান্ড থামায়, আর আউটপুট pipe ধরে রাখা background child একটি শেষ হওয়া কমান্ডকে
  অনির্দিষ্টকাল দেরি করায় না।
- ফাইলের কাজ বাইট অক্ষুণ্ণ রাখে, যেখানে উপযুক্ত সেখানে symlink অনুসরণ করে, আর path এরর জানায়;
  আটকে রাখার সীমা বুঝুন: একটি working directory একটি জেলখানা নয়, আর symlink root পেরোতে পারে।
- আবার যুক্ত হওয়া, একটি ধ্বংস হওয়া রেফারেন্স, আর একটি কমান্ডের মাঝে ধ্বংস পরীক্ষা করতে `attach_backend`, `destroy_environment` আর একটি স্বাধীন `destructive_backend` দিন। এই ঐচ্ছিক নিয়মগুলো
  তাদের fixture না থাকলে বাদ পড়ে।

বাদ পড়া একটি নিয়ম পাস করা নিয়ম নয়: কী পরীক্ষা হয়নি দেখতে pytest `-rs` দিয়ে চালান। চারটি boolean
fixture, সবগুলোর ডিফল্ট `True`, একটি জানা সীমা ঘোষণা করে; `False` ফেরত দিন শুধু এমন সীমার জন্য যা আপনি
ব্যবহারকারীদের জন্যও নথিভুক্ত করেন:

- `can_detect_exit_with_inherited_output_pipes`: provider একটি কমান্ডের exit জানায় শুধু তার আউটপুট ধরে রাখা
  প্রতিটি প্রসেস বেরোনোর পরে।
- `filesystem_honors_shell_permissions`: provider-এর ফাইল API কমান্ডের user-এর অনুমতি পাশ কাটায়।
- `has_real_posix_shell` আর `enforces_parent_file_errors`: শুধু in-memory test double-এর জন্য।

suite-এর ক্লাস, fixture, switch আর নিয়মের নাম 2.x-এ স্থির, তাই একটির নাম বদলানো একটি breaking
change। minor release-এ নতুন বা আরও কড়া নিয়ম যোগ হতে পারে; একটি নতুন নিয়ম আপনার CI ব্যর্থ করালে সমস্যা হলে `pydantic-ai` pin করুন।

## Timeout আর ঘড়ি { #timeouts-and-clocks }

`run(timeout=...)` তার ঘড়ি চালু করে sandbox প্রস্তুত হওয়ার পরে (আর, লোকালে, working directory
নির্ধারণের পরে)। লোকাল প্রসেস শুরুর সময় কমান্ডের সময় হিসেবে গোনা হয়। সময়সীমা শুধু কমান্ডকে ঢাকে;
`timeout=None`-এ কোনো কমান্ড-সময়সীমা নেই। একটি provider-এর sandbox-আয়ুষ্কাল আর অলস থাকার সীমা
আলাদা। কমান্ড EOF-এ stdin পায়, তাই অ-ইন্টারঅ্যাক্টিভ ফ্ল্যাগ ব্যবহার করুন (যেমন `-y`)। তার
নিজের সময়সীমায় সামনের কমান্ড থামানো হয় আর `WorkspaceTimeoutError` এ পর্যন্ত সংগৃহীত আংশিক
`stdout` আর `stderr` বহন করে। লোকাল backend-এ, কমান্ড-সময়সীমা subprocess শুরুকেও
সীমিত করে; এমনকি `timeout=None`-এও, শুরু আর প্রসেস পরিষ্কারের সীমিত
নিরাপত্তা-সীমা আছে।

## নিরাপত্তার সিদ্ধান্ত { #security-choices }

`LocalWorkspace`-এর host user-এর পূর্ণ ক্ষমতা আছে। `working_dir` বা একটি harness
`FileSystem` root কোনোটিই shell কমান্ডকে আটকে রাখে না। অবিশ্বস্ত workspace-এ `os.environ` দেবেন না:
কমান্ডের যে ভ্যারিয়েবল লাগে তা স্পষ্টভাবে বেছে নিন। workflow-এর দিকের workspace কলের আর্গুমেন্ট,
`env=` আর ফাইলের বিষয়বস্তুসহ, durable ইতিহাসে সংরক্ষিত হয়; উপযুক্ত payload codec ছাড়া সেখানে
গোপন তথ্য দেবেন না।

এজেন্ট রানের span `pydantic_ai.workspace.id` রেকর্ড করে (sandbox id, বা `LocalWorkspace`-এর জন্য
ডিরেক্টরির path), এমনকি `include_content=False`-এও, কারণ এটি পরিবেশ চেনায়, বিষয়বস্তু নয়।

## প্ল্যাটফর্ম { #platforms }

লোকাল background job `run()`-এর পরেও টিকে থাকে; stdout বা stderr উত্তরাধিকারসূত্রে পেলে দুই-সেকেন্ডের drain অপেক্ষা এড়াতে তাদের আউটপুট একটি ফাইলে পাঠান। host বেরোনোর সময় caller-কে job পরিষ্কার করতে হবে।

যে লোকাল কমান্ড 10 MiB-এর মিলিত আউটপুট সীমা পেরোয় তা `WorkspaceOutputLimitError` তোলে, `stdout` আর `stderr`-এ প্রতিটি stream-এর প্রথম 64 KiB-সহ। বদলে বড় আউটপুট একটি ফাইলে পাঠান।

লোকাল backend আর কমান্ড-নির্ভর shell বিকল্পের POSIX লাগে। শুধু-filesystem একটি backend
shell সমর্থন ছাড়াই কাজ করে, তবে কমান্ড চালাতে পারে না।

## সীমাবদ্ধতা { #limits }

- `LocalWorkspace` শুধু POSIX সিস্টেমে (macOS আর Linux) চলে আর কিছুই বিচ্ছিন্ন করে না। আগে এর root
  তৈরি করুন: প্রতিটি কাজের এটি লাগে। এটি থাকা অবস্থায়, এর বাইরের পূর্ণ path অনুমোদিত।
  `defer_loading=True` প্রত্যাখ্যাত হয়, কারণ deferred capability লোড হওয়ার আগেই workspace বাছাই হতে হবে।
  এর ref symlink সমাধান না করে `.` আর `..` স্বাভাবিক করে, তাই ভিন্নভাবে লেখা symlink
  root-এর আলাদা ref থাকে, যদিও তারা একই ডিরেক্টরি দেখায়।
- একটি `LocalWorkspace` backend একটি ফাইলের নিজের পড়া আর লেখা ক্রমানুসারে সাজায়; অন্য রান, প্রসেস আর কমান্ড তবুও এর মাঝে ঢুকে পড়তে পারে।
- একটি রানের একটি workspace।
- non-durable রান শুধু রানের সীমানায় sandbox তৈরি বা মোছে না; durable রান শুরুতেই আগ্রহের সাথে একটি পরিবেশ তৈরি করে বা যুক্ত হয়, টুল ব্যবহার না হলেও। দুই ক্ষেত্রেই, মোছা caller-এর কাজ।
- সময় পেরোনো একটি কমান্ড কীভাবে থামানো হয় তা provider-এর ওপর নির্ভর করে।

/// check | সংক্ষেপে মনে রাখুন

* `Agent(..., capabilities=[LocalWorkspace('.')])`; টুলে `ctx.workspace.run(...)`, `read_text`, `write_text` ইত্যাদি।
* `LocalWorkspace` sandbox নয়; অবিশ্বস্ত কোডে harness-এর sandbox (Modal, E2B, Daytona...) — টুলের কোড একই থাকে।
* `message_history` দিলে একই workspace-এ চালিয়ে যায়; ইতিহাস ছাড়া `workspace=result.workspace.ref`; নতুন করে `workspace='new'`।
* `env=`-এ শুধু দরকারি ভ্যারিয়েবল, কখনো পুরো `os.environ` নয়।
* শুধু পড়তে `read_only=True` বা `ReadOnlyWorkspace(...)`।
* Pydantic AI কখনো sandbox মোছে না; সফল রানে `result.workspace.ref`, ব্যর্থ রানে `on_run_error` hook-এ মুছুন।

///
