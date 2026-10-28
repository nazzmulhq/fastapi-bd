
# FileSystem { #filesystem }

/// note | এই পেজে যা শিখবেন

* `FileSystem` দিয়ে এজেন্টকে একটি `root_dir`-এ সীমিত, নিরাপদ ফাইল টুল দেওয়া — পড়া, লেখা, সম্পাদনা, তালিকা, খোঁজা।
* দশটি টুল, ripgrep টুল, content hash, working directory আর root।
* টুল kind, event (লেখার আগে veto সহ), নিরাপত্তা মডেল আর pattern ছাঁকনি।

///

`FileSystem` একটি এজেন্টকে একটি নির্দিষ্ট ফাইল টুলের সেট দেয় -- পড়া, লেখা, সম্পাদনা, তালিকা, খোঁজা, সন্ধান, তৈরি আর পরীক্ষা -- সবগুলো রানের workspace-এ একটি একক `root_dir`-এ সীমিত। যেকোনো I/O-র আগে প্রতিটি path মীমাংসা হয়, symlink-সহ, আর সীমার ভেতরে কিনা যাচাই হয়, আর প্রবেশ allow, deny আর read-only glob pattern দিয়ে ছাঁকা হয়।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/filesystem/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## সমস্যাটি { #the-problem }

একটি এজেন্টকে সরাসরি filesystem ছুঁতে দেওয়া ঝুঁকিপূর্ণ: path traversal
(`../../etc/passwd`), `.git` নষ্ট করা, বা `.env` secret ফাঁস। প্রতিটি টুল কলের চারপাশে হাতে পাহারা বানানো পুনরাবৃত্তিমূলক আর সূক্ষ্মভাবে ভুল করা সহজ।

`FileSystem` সেই পাহারাগুলো কেন্দ্রীভূত করে। এটি একটি সীমিত toolset দেয়, যাতে আপনি সীমাটি একবার কনফিগার করে এজেন্ট জুড়ে পুনর্ব্যবহার করেন।

/// tip | উদাহরণ দিয়ে বুঝি

একটি লাইব্রেরির কর্মীর মতো, যাকে একটি নির্দিষ্ট তাকের চাবি দেওয়া হয়েছে (`root_dir`)। তিনি সেই তাকের বই পড়তে, নোট লিখতে পারেন, কিন্তু অন্য ঘরে যেতে পারেন না (`../`)। কিছু বই কাচের আলমারিতে — দেখা যায়, কিন্তু লেখা যায় না (`.git`, `.env` — read-only)। আর কিছু তাক পুরো বন্ধ (`denied_patterns`)।

///

## ব্যবহার { #usage }

আপনার এজেন্টের `capabilities`-এ `FileSystem` যোগ করুন, ফাইলগুলো থাকার জন্য একটি workspace-সহ:

```python
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem

Path('./workspace').mkdir(exist_ok=True)
agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[LocalWorkspace('./workspace'), FileSystem()],
)

result = agent.run_sync('Read config.toml and tell me the package name.')
print(result.output)
```

`root_dir`-এর ডিফল্ট workspace-এর working directory, তাই ওপরের এজেন্ট ফাইল টুল দিয়ে `./workspace`-এ পৌঁছাতে পারে আর এর বাইরে কিছুতে নয়।

## ফাইল কোথায় থাকে { #where-files-live }

`FileSystem` রানের [workspace](../workspace.md)-এ ফাইল পড়ে আর লেখে: `LocalWorkspace`-এ আপনার মেশিন, বা একটি sandbox। workspace ছাড়া একটি রান শুরুতেই ব্যর্থ হয়।

একটি শুধু-পড়া workspace-এ (`LocalWorkspace(..., read_only=True)`), শুধু পড়ার টুল দেওয়া হয়। `list_files` আর `grep` workspace-এর ভেতরে `rg` চালায়; যেখানে এটি কমান্ড চালাতে পারে না, সেখানে এরা এর বদলে ফাইলগুলো হেঁটে দেখে, যেমন `find_files` আর `search_files` করে।

## টুল { #tools }

`FileSystem` ডিফল্টভাবে আটটি টুল দেয়, সাথে দুটি ঐচ্ছিক ripgrep টুল, সবগুলো `root_dir`-এ path-সীমিত:

| টুল | উদ্দেশ্য |
|---|---|
| `read_file` | লাইন নম্বর আর একটি content hash-সহ একটি text ফাইল পড়া। 5 MB পর্যন্ত একটি ছবি (PNG, JPEG, GIF, WebP) বা PDF ফাইল হিসেবেই ফেরত দেওয়া হয়, তাই ফাইল নেয় এমন একটি মডেল এটি দেখে; অন্য binary ফাইল আকার, media type আর hex-এ প্রথম 64 bytes দিয়ে বর্ণনা করা হয়। `offset`/`limit` পাতা ওল্টানো সমর্থন করে, প্রতি কলে সর্বোচ্চ `max_read_lines` লাইন; `max_read_chars`-সহ, পুরো ফল (header আর ইঙ্গিতসহ) সীমার মধ্যে আঁটে যদি না সীমা header আর ইঙ্গিতের চেয়েই ছোট হয়, window শেষ হয় আঁটে এমন শেষ সম্পূর্ণ লাইনে, আর ধারাবাহিকতার ইঙ্গিত না-দেখানো প্রথম লাইনের নাম দেয়। 64 MiB-এর বেশি একটি ফাইল পড়া হয় না, এর আকার দিয়ে বর্ণনা করা হয়। |
| `write_file` | একটি ফাইল তৈরি বা overwrite। ঐচ্ছিক `expected_hash` পুরনো লেখা প্রত্যাখ্যান করে (optimistic concurrency)। |
| `edit_file` | হুবহু-string প্রতিস্থাপন: একটি `old_text`/`new_text` জোড়া, বা ক্রমানুসারে প্রয়োগ করা একটি `replacements` ব্যাচ। প্রতিটি `old_text` ঠিক একবার মিলতে হবে; একটি ব্যাচ মেমরিতে যাচাই হয় আর শুধু প্রতিটি প্রতিস্থাপন মিললেই লেখা হয়। ঐচ্ছিক `expected_hash`। |
| `list_directory` | টাইপ-চিহ্ন আর আকারসহ একটি ডিরেক্টরির entry তালিকা। |
| `search_files` | ফাইলের কনটেন্টে regex সার্চ, ঐচ্ছিকভাবে একটি `include_glob` দিয়ে সরু; 10 MiB-এর বেশি বা অপাঠ্য ফাইল বাদ দেয় আর বাদ পড়া path জানায়। |
| `find_files` | ফাইলের নামে glob সার্চ (যেমন `*.py`, `**/*.json`)। pattern `path`-এর আপেক্ষিক; absolute pattern প্রত্যাখ্যাত। |
| `create_directory` | একটি ডিরেক্টরি আর যেকোনো অনুপস্থিত parent তৈরি। |
| `file_info` | একটি ফাইল বা ডিরেক্টরির metadata: আকার, টাইপ, একটি ফাইল binary কিনা, একটি text ফাইলের লাইন সংখ্যা আর hash, আর symlink লক্ষ্য, যেখানে workspace এগুলো দেয়। 64 MiB-এর বেশি একটি ফাইল শুধু এর আকার জানায়। |
| `list_files` | ঐচ্ছিক, ripgrep-চালিত: একটি ডিরেক্টরির নিচের ফাইল, recursive-ভাবে, path অনুযায়ী সাজানো, একটি ঐচ্ছিক `glob`-সহ। |
| `grep` | ঐচ্ছিক, ripgrep-চালিত: `glob`, `file_type`, `ignore_case`, `literal` আর `context` (0 থেকে 20) অপশনসহ কনটেন্ট সার্চ; একটি `path` একটি ফাইল বা একটি ডিরেক্টরির নাম দিতে পারে। |

একটি স্পষ্টভাবে অনুপলব্ধ রান workspace একটি লোকাল workspace যুক্ত করার পরামর্শের বদলে এর কনফিগার করা কারণসহ রানের শুরুতে ব্যর্থ হয়।

অনুপস্থিত path (`read_file`-এ দেওয়া ডিরেক্টরিসহ) টুলের ফল হিসেবে `Path not found: <path>` ফেরত দেয়, তাই বারবার খোঁজা মডেলের টুল retry বাজেট শেষ করে না। অবৈধ আর্গুমেন্ট তবুও একটি retry চায়।

দূরের workspace-এর জন্য, একটি shell দিয়ে `cat`-এর বদলে ফাইল টুল (`grep`, `find_files`, `read_file`) ব্যবহার করুন। দ্রুত সার্চের জন্য sandbox image-এ `rg` আর `git` ইনস্টল করুন; এজেন্টের host-এ `rg` ইনস্টল করলে তা একটি দূরের workspace-এ ইনস্টল হয় না। বড় বা তৈরি-করা tree-এর জন্য, `rg -n 'pattern' path`-সহ Shell ব্যবহার করুন আর এর আউটপুট সীমিত করুন। `rg` ছাড়া, কমান্ড-সক্ষম POSIX workspace `grep`, `list_files` আর `search_files`-এর জন্য একটি sandbox-এর-ভেতরের git/grep/find কমান্ড ব্যবহার করে (একটি প্রাথমিক `rg` যাচাইয়ের পর)। শুধু-filesystem আর শুধু-পড়া workspace Python-এ ধীরতর, সীমিত ফাইল-হাঁটা ব্যবহার করে, যার regex engine-এর কোনো সময়-সীমা নেই, তাই এরা একটি পুনরাবৃত্ত group পুনরাবৃত্তি করে এমন regex প্রত্যাখ্যান করে, যেমন `(a+)+`: সেই রূপ exponential সময় নিতে পারে। একটি সীমিত group-এর সীমিত পুনরাবৃত্তি, যেমন `([0-9]{1,3}[.]){3}`, অনুমোদিত। যাচাইটি সেই রূপের জন্য একটি অনুমান, সময়-সীমা নয়: অন্য ধীর রূপ, যেমন overlapping বিকল্প (`(a|aa)+`) বা quantifier-এর সারি (`a*a*a*a*b`), তবুও চলে। POSIX বিকল্প git উপলব্ধ থাকলে repository-তে nested `.gitignore` আর search-root `.ignore` মানে; nested `.ignore` নিয়ম POSIX বিকল্প প্রয়োগ করে না, আর rg-নির্দিষ্ট regex সুবিধার জন্য `rg` লাগে। git ছাড়া, POSIX বিকল্প ignore ফাইল প্রয়োগ করতে পারে না। git-সহ, এটি সেই ফাইলও খোঁজে যা git ট্র্যাক করে যদিও `.gitignore` এগুলো তালিকা করে, যা `rg` বাদ দেয়। একটি workspace-এ বিকল্পে ফিরে যাওয়া প্রথম সার্চ একটি debug বার্তা log করে। স্পষ্টভাবে নাম দেওয়া একটি ফাইল উপেক্ষিত হলেও খোঁজা হয়। সার্চ আংশিক ফলকে সম্পূর্ণ হিসেবে উপস্থাপন না করে আউটপুট আর ফলের সীমা জানায়। একটি সার্চ যে ফাইল পড়তে পারে না (`rg`-সহ, একটি ডিরেক্টরিও) তা বাদ পড়ে, আর ফলের শেষে একটি নোট এর নাম আর কারণ দেয়।

Recursive ফাইল-হাঁটা প্রতিটি আসল ডিরেক্টরি একবার দেখে, তাই একটি ডিরেক্টরির alias এর কনটেন্ট দ্বিগুণ করে না।

### টুল বাছাই আর ripgrep টুল { #tool-selection-and-the-ripgrep-tools }

`tools` নিবন্ধনের টুলের নাম দেয়, `FILE_SYSTEM_TOOL_NAMES` থেকে। ডিফল্ট, `DEFAULT_TOOL_NAMES`, হলো সেই আটটি টুল যাদের শুধু workspace-এর filesystem লাগে। `list_files` আর `grep` workspace-এর ভেতরে `rg` executable চালায় যখন এটি এর `PATH`-এ থাকে, তাই এগুলো নাম দিয়ে ঐচ্ছিক। `coder` extra একটি লোকাল workspace-এর জন্য `rg` ইনস্টল করে। `rg` ছাড়া, দুটোই একটি workspace-এর-ভেতরের POSIX কমান্ড ব্যবহার করে। বিকল্পে ripgrep `file_type` সমর্থন আর কিছু ignore-ফাইল নিয়ম নেই। একটি শুধু-পড়া বা শুধু-filesystem workspace-এ, দুটোই এর বদলে ফাইলগুলো হাঁটে, ignore ফাইল বা `file_type` ছাড়া।

```python
from pydantic_ai_harness import FileSystem

FileSystem(tools=['read_file', 'edit_file', 'list_files', 'grep'])
```

দুটোই ripgrep-এর ডিফল্ট মানে: একটি git repository-র ভেতরে `.gitignore` আর যেকোনো জায়গায় `.ignore` ফাইল। ripgrep-এর মতো, একটি স্পষ্ট `glob` ওই ignore ফাইলের ওপর অগ্রাধিকার পায়। লুকানো ফাইল একটি স্পষ্ট dotfile glob দিয়ে বাছা যায়, আর লুকানো ডিরেক্টরি এদের সার্চ path হিসেবে নাম দিয়ে। `list_directory` আর walker-চালিত `find_files`/`search_files` যে লুকানো entry দেখেছে কিন্তু বাদ দিয়েছে তা জানায়; ছাঁটা লুকানো ডিরেক্টরি এক entry হিসেবে গোনা হয়, এদের না-দেখা কনটেন্ট নয়। কমান্ড-চালিত সার্চ লুকানো বাদ গোনে না। আউটপুট path অনুযায়ী সাজানো, তাই একটি সীমিত ফল একটি র‍্যান্ডম উপসেট নয়, একটি নির্ধারিত শুরুর অংশ। `grep` মিল জানায় `path:line:text` হিসেবে আর context লাইন `path-line-text` হিসেবে, path working directory-র আপেক্ষিক; `literal` সেট না থাকলে একটি pattern ripgrep-এর regex syntax ব্যবহার করে। ripgrep প্রত্যাখ্যান করা একটি pattern মডেলের কাছে একটি retry হিসেবে ফেরত আসে, যাতে এটি কলটি সংশোধন করতে পারে। ripgrep যে প্রতিটি path ছাপে তা দেখানোর আগে অন্য walker-এর মতো একই সীমা আর pattern যাচাই দিয়ে যায়। 8 MiB-এর বেশি ripgrep আউটপুট কাটা হয়, আর সার্চ ছাঁটা হিসেবে জানানো হয়। `read_only=True` `tools` যা-ই বাছুক তা থেকে শুধু `READ_ONLY_TOOL_NAMES`-এর টুল রাখে।

### Content hash { #content-hashes }

`content_hashes=False` `read_file` header থেকে আর `write_file`/`edit_file`-এর ফল থেকে hash বাদ দেয়, আর ওই দুটি টুল থেকে `expected_hash` প্যারামিটার সরায়। hash একটি মডেলকে এমন একটি workspace-এর ওপর optimistic concurrency নিয়ন্ত্রণ দেয় যা অন্য কিছুও সম্পাদনা করতে পারে; একটি একক-লেখক coding এজেন্টের জন্য এগুলো শুধু প্রতিটি পড়া আর লেখায় token যোগ করে। event যেকোনোভাবে `content_hash` বহন করে।

/// info | `expected_hash` কীভাবে কাজ করে

1. এজেন্ট `read_file('app.py')` করে, ফলের header-এ hash পায় — ধরুন `abc123`।
2. এর মধ্যে আরেকজন (মানুষ বা আরেকটি এজেন্ট) ফাইলটি বদলায়; এখন hash `def456`।
3. এজেন্ট `edit_file(..., expected_hash='abc123')` করে। hash মেলে না, তাই সম্পাদনা প্রত্যাখ্যাত হয় আর এজেন্টকে আবার পড়তে বলা হয় — অন্যের পরিবর্তন নিঃশব্দে মুছে যায় না।

///

### Working directory আর root { #working-directory-and-root }

আপেক্ষিক path workspace-এর working directory থেকে মীমাংসা হয়। মডেলকে absolute path না লিখেই project ডিরেক্টরির বাইরে পৌঁছাতে দিতে `root_dir` আরও ওপরে সেট করুন, যেমন sibling project রাখা একটি parent। `root_dir`-এ working directory থাকতে হবে। একটি সাবডিরেক্টরিতে কাজ করতে, এর বদলে এটি workspace-এ সেট করুন (`LocalWorkspace('./repo')`)।

`list_directory`, `find_files`, `search_files`, `list_files` আর `grep` working directory-র আপেক্ষিক path ফেরত দেয়, একটি সাবডিরেক্টরি খোঁজার সময়ও। এই path সরাসরি পড়া/লেখার টুলে দেওয়া যায়। working directory-র বাইরে কিন্তু `root_dir`-এর ভেতরের ফাইল `..` অংশ ব্যবহার করে। সীমা, প্রবেশ pattern আর event path এদের `root_dir` ভিত্তি রাখে, যেমন রাখে `search_files`-এর `include_glob` ছাঁকনি।

`include_glob` `fnmatch` দিয়ে মেলানো হয়, যেখানে `*` `/`-ও পেরোয়, তাই `src/*.py` `src`-এর সাবডিরেক্টরিও কভার করে। `rg`-সহ, `/` ছাড়া একটি glob যেকোনো গভীরতায় ফাইলের নাম মেলায়, আর শুধু `rg`-এর আছে এমন syntax ব্যবহার করা একটি glob (`**`, `{a,b}`, `!`, একটি শুরুর `/`) `rg --glob`-এ দেওয়া হয়।

### টুল kind { #tool-kinds }

প্রতিটি টুল `file_system` namespace-এ একটি [tool kind](../tools-advanced.md#typed-tool-parts) ঘোষণা করে, টুলের নাম অনুযায়ী: `read_file`-এর kind `file_system.read_file`, `READ_FILE_KIND` হিসেবে রপ্তানি করা, আর একইভাবে
`WRITE_FILE_KIND`, `EDIT_FILE_KIND`, `LIST_DIRECTORY_KIND`, `SEARCH_FILES_KIND`,
`FIND_FILES_KIND`, `CREATE_DIRECTORY_KIND`, `FILE_INFO_KIND`, `LIST_FILES_KIND`
আর `GREP_KIND`। kind টুলের নামের নয়, সংজ্ঞার অংশ, তাই আরেকটি capability বা একটি history processor টুলের নাম তুলনা না করে kind দিয়ে এই টুলগুলো চিনতে পারে। প্রতিটি kind এর টুলের আর্গুমেন্টের রূপ ঘোষণা করে (`ReadFileArgs`, `WriteFileArgs` ইত্যাদি), আর যে কলের আর্গুমেন্ট এতে আঁটে তা একটি রানের বার্তায় আর একটি লোড করা ইতিহাসে একটি টাইপ করা part-এ (`ReadFileCallPart`, `WriteFileCallPart` ইত্যাদি) উন্নীত হয়, `typed_args` হিসেবে যাচাই করা আর্গুমেন্টসহ:

```python
from pydantic_ai.messages import ModelMessage
from pydantic_ai_harness.filesystem import ReadFileCallPart


def paths_read(messages: list[ModelMessage]) -> list[str]:
    return [
        args['path']
        for message in messages
        for part in message.parts
        if isinstance(part, ReadFileCallPart) and (args := part.typed_args) is not None
    ]
```

`read_file`-এর একটি টাইপ করা return part-ও আছে, `ReadFileReturnPart`, একটি return-এর জন্য যার ফলাফল `'success'`, যাতে একটি `Path not found: <path>` ফল আর 64 MiB-এর বেশি একটি ফাইলের জন্য `read_file` যে বর্ণনা ফেরত দেয় তাও অন্তর্ভুক্ত, তাই কোনোটির মানে ফাইলের কনটেন্ট পড়া হয়েছে তা নয়। এর `content` হলো header-সহ লেখা, বা একটি ছবি বা PDF-এর জন্য `[header, BinaryContent]`। kind কোনো কনটেন্ট রূপ ঘোষণা করে না, কারণ `ToolKind` একটি ক্লাস নেয়, union নয়, তাই `typed_content` টাইপহীন। অন্য টুলগুলো পার্স করার ফরম্যাটের বদলে মডেলের জন্য লেখা text ফেরত দেয়, তাই এদের return সাধারণ `ToolReturnPart` থাকে যা kind-কে `tool_kind` হিসেবে বহন করে; [event](#events) এদের ফলাফল কাঠামোবদ্ধ ডেটা হিসেবে বহন করে।

### যে capability `read_file`-এর জন্য সরে দাঁড়ায় { #capabilities-that-step-aside-for-read_file }

কিছু capability-র workspace-এ রাখা ফাইলের জন্য নিজস্ব একটি reader আছে। ওই ফাইল রানের workspace-এ থাকলে, reader-টি `READ_FILE_KIND`-এ সেট করা [`unless_tool_kind`][pydantic_ai.tools.ToolDefinition.unless_tool_kind] দিয়ে চিহ্নিত হয়, তাই `read_file` আছে এমন প্রতিটি run step থেকে এটি বাদ পড়ে। instructions কোনো reader-এর নাম দেয় না, তাই যেকোনোভাবে এগুলো একই থাকে; spill marker আর `Memory`-র প্রতি-কল বিজ্ঞপ্তি `read_file`-এর নাম দেয় রানে যেভাবে ডাকা হয় সেভাবে:

- ডিফল্ট `WorkspaceStore()`-সহ `ToolOutputLimits`-এর `read_tool_result`। `read_file` দিয়ে এর spill ফাইল পড়া আবার কমানো হয় না।
- নিজস্ব `workspace=` নেই আর working directory-র ভেতরে একটি আপেক্ষিক `directory`-সহ একটি `FileStore`-যুক্ত `Memory`-র `read_memory`।
- `RepoContext`-এর inventory টুল, যখন এর asset root working directory-র ভেতরে।

একটি `FileSystem` টুল এখনও একটি নতুন নামে ডাকা যায় না, যেমন `PrefixTools`-এর অধীনে, কারণ Pydantic AI এর capability event প্রত্যাখ্যান করে ([#10927](https://github.com/pydantic/pydantic-ai/issues/10927))। নাম-বদলানো একটি `FileSystem`-এর জন্যও নির্দিষ্ট reader সরে দাঁড়ায়, তাই আপাতত `FileSystem` এর নিজের নামেই রাখুন।

capability নিজের কনফিগারেশন থেকে সিদ্ধান্ত নেয়, `FileSystem`-এর প্রবেশ নিয়ম থেকে নয়। ওই ফাইলগুলো কভার করা `denied_patterns` (spill-এর জন্য `.pydantic-ai-harness/`, memory ডিরেক্টরি, asset root), বা এগুলো বাদ রাখা `allowed_patterns` থাকলে, নির্দিষ্ট reader তবুও বাদ পড়ে আর `read_file` ফাইলগুলো প্রত্যাখ্যান করে। নির্দিষ্ট reader রাখতে, `ToolOutputLimits` বা `Memory`-কে নিজস্ব workspace-সহ একটি store দিন, আর `RepoContext`-এর জন্য asset root পাঠযোগ্য রাখুন বা working directory-র বাইরে একটি asset root ব্যবহার করুন।

## Event { #events }

`FileSystem` `file_system` namespace-এ টাইপ করা capability event তৈরি করে, যাতে একজন host দেখাতে পারে এজেন্ট workspace-এ কী করেছে, বা একটি পরিবর্তন ঘটার আগে বাতিল (veto) করতে পারে, টুলের আর্গুমেন্ট পার্স না করেই:

| Event | Dispatch | কাজ | Payload |
|---|---|---|---|
| `FileChangeRequestEvent` | immediate | `write_file`, `edit_file`, `create_directory` | `path`, `root_dir`, `operation`, `diff`, `truncated`; `cancel(reason)` |
| `FileReadEvent` | stream | `read_file` | `path`, `root_dir`, `content_hash` |
| `DirectoryListedEvent` | stream | `list_directory` | `path`, `root_dir`, `entry_count` |
| `FileWrittenEvent` | stream | `write_file` | `path`, `root_dir`, `content_hash` |
| `FileEditedEvent` | stream | `edit_file` | একটি `FileWrittenEvent`, সাথে `diff`, `truncated` |
| `DirectoryCreatedEvent` | stream | `create_directory` | `path`, `root_dir` |
| `FilesSearchedEvent` | stream | `search_files`, `find_files`, `list_files`, `grep` | `path`, `root_dir`, `pattern`, `search` (`grep` বা `find`), `match_count`, `truncated` |

`FileChangeRequestEvent` একটি সিদ্ধান্ত। এটি চলে path প্রবেশ যাচাই পেরোনোর পরে আর, `write_file` ও `edit_file`-এর জন্য, সংঘর্ষ-যাচাইয়ের পরে, তাই একজন listener শুধু সেই পরিবর্তন দেখে যা অন্যথায় এগিয়ে যেত: একটি প্রত্যাখ্যাত path, `write_file`-এর জন্য একটি অনুপস্থিত parent, একটি parent যা ডিরেক্টরি নয়, একটি বিদ্যমান ফাইলের জন্য একটি পুরনো `expected_hash`, বা একটি ফাইলের সাথে সংঘর্ষ করা একটি ডিরেক্টরি কোনো রিকোয়েস্ট তৈরি করে না, তাই একজন listener নীতি বা filesystem যা প্রত্যাখ্যান করে তা অনুমোদন করতে পারে না। একজন listener সময় নিতে পারে (ধরুন একজন মানুষ diff অনুমোদন করছেন), তাই রিকোয়েস্ট ফেরত আসার পর path আবার মীমাংসা আর যাচাই হয়, আর একটি লেখা বা সম্পাদনা লেখার ঠিক আগে ফাইলটি আবার পড়ে যাচাই করে যে এতে এখনও listener-কে যা দেখানো হয়েছিল তা-ই আছে: মাঝে বদলানো একটি ফাইল overwrite না হয়ে ঘোষণার পর ব্যর্থ হয়, আর একটি সম্পাদনা মাঝে মোছা একটি ফাইল আবার তৈরি করে না। এটি যাচাই আর লেখার মাঝের জানালাকে (দেখুন [Security model](#security-model)) পাঠযোগ্য লক্ষ্যের জন্য listener ছাড়া যেমন তেমনই রাখে। workspace পড়তে পারে না এমন একটি লক্ষ্যের জন্য, একটি অনুমোদিত লেখার কোনো কনটেন্ট পাহারা নেই; এর বদলে `expected_hash` দিলে ঘোষণার আগেই লেখা প্রত্যাখ্যাত হয়। `cancel(reason)` ডাকা একজন listener পরিবর্তনটি ডিস্ক ছোঁয়ার আগে থামায়, আর মডেল কারণটি টুলের ফল হিসেবে পায়। এর বদলে exception তোলা একজন listener রান বাতিল করে, যেকোনো exception-তোলা event listener যেমন করে, আর পরিবর্তন প্রয়োগ হয় না। `diff` হলো বর্তমান কনটেন্ট থেকে প্রস্তাবিত কনটেন্টের unified diff: একটি নতুন ফাইল খালি থেকে diff হয়, workspace পড়তে পারে না এমন একটি ফাইল শুধু file header আর `truncated` সেট করে ঘোষিত হয়, যেহেতু এতে কী আছে দেখানো যায় না, আর একটি `create_directory`-এর কোনো diff নেই। ইতিমধ্যে থাকা একটি ডিরেক্টরিতে একটি `create_directory` কিছুই বদলায় না আর কিছুই তৈরি করে না। অন্য event-গুলো বিজ্ঞপ্তি।

/// tip | উদাহরণ দিয়ে বুঝি

`FileChangeRequestEvent` হলো একটি "লেখার আগে জিজ্ঞেস করো" ঘণ্টা। এজেন্ট `config.py` বদলাতে চায় — ঘণ্টা বাজে, আপনার UI diff দেখায় ("এই 3 লাইন বদলাবে")। ব্যবহারকারী "না" বললে listener `event.cancel('ব্যবহারকারী প্রত্যাখ্যান করেছেন')` ডাকে, আর ফাইলটি অক্ষত থাকে; মডেল কারণটি জেনে অন্য পথ নেয়।

///

`FileEditedEvent` `FileWrittenEvent`-এর subclass, তাই লেখার একজন listener সম্পাদনাও পায় আর একটি থাকলে `diff` পড়তে পারে। এই release-এর আগে `edit_file` একটি সাধারণ `FileWrittenEvent` তৈরি করত, তাই একটি serialize করা সম্পাদনার kind ছিল `file_system.file_written`; এখন এটি `file_system.file_edited`। `FileWrittenEvent`-এর জন্য নিবন্ধিত একজন listener তবুও এটি পায়; serialize করা kind মেলানো কোডকে দুটোই গ্রহণ করতে হবে। Diff `MAX_EVENT_DIFF_CHARS` (8192)-এ একটি `truncated` flag-সহ কাটা হয়, যাতে একটি সংরক্ষিত বা পাঠানো event stream একটি বড় লেখায় ভেসে না যায়, আর যে পরিবর্তনের লেখা যেকোনো পাশে `MAX_DIFF_SOURCE_CHARS` (32768)-এর চেয়ে লম্বা তা একদমই diff হয় না: `diff` হলো দুটি file header আর `truncated` সেট। একই বিকল্প প্রযোজ্য যখন `(old.count("\n") + 1) * (new.count("\n") + 1)` 65536 ছাড়ায়, differ ডাকার আগে লাইন-মেলানোর কাজ সীমিত করে।
newline ছাড়া একটি শেষ লাইন `git diff` যেভাবে চিহ্নিত করে সেভাবে চিহ্নিত হয়, তাই শুধু শেষ newline-এর একটি পরিবর্তন দৃশ্যমান। একটি `FilesSearchedEvent` মডেল যত মিল পেয়েছে তা গোনে; `truncated` বলে সার্চ `max_search_results` বা `max_find_results`-এ থেমেছে।

`path` হলো `root_dir`-এর আপেক্ষিক স্বাভাবিক অবস্থান, কখনো একটি absolute path নয়, তাই এটি মডেল বা একটি UI-তে প্রতিধ্বনিত করা নিরাপদ। `root_dir` হলো তৈরিকারী filesystem-এর root, রানের workspace-এর ভেতরে একটি absolute POSIX path হিসেবে, তাই অন্যত্র root করা একজন subscriber তৈরিকারীর root ভাগ করে ধরে না নিয়ে সেই workspace-এ `posixpath.join(root_dir, path)` হিসেবে ফাইলটি খুঁজে পেতে পারে।

প্রতিটি event path সীমা-যাচাই আর denied pattern পেরিয়েছে। একটি `DirectoryListedEvent` বা `FilesSearchedEvent` হাঁটার root-এর নাম দেয়, যা `allowed_patterns` দিয়ে নিয়ন্ত্রিত নয় (দেখুন [Security model](#security-model)); শুধু এর entry-গুলো নিয়ন্ত্রিত। একটি প্রত্যাখ্যাত বা ব্যর্থ কাজ কোনো event তৈরি করে না, যে `read_file`-এর `offset` ফাইলের শেষের পরে তাসহ।

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem
from pydantic_ai_harness.filesystem import FileChangeRequestEvent

agent = Agent('anthropic:claude-opus-5-5', capabilities=[LocalWorkspace('.'), FileSystem()])

@agent.on_event(FileChangeRequestEvent)
async def hold_migrations(ctx, event):
    if event.path.startswith('migrations/'):
        event.cancel('migrations need a human')
```

অন্য capability একটি মেথডে `@on_event` দিয়ে subscribe করে, যেভাবে `RepoContext` `FileReadEvent` আর `DirectoryListedEvent` অনুসরণ করে। নিজস্ব ফাইল টুলসহ একজন host `pydantic_ai_harness.filesystem` থেকে import করে একই event টাইপ তৈরি করতে পারে, যা subscriber-দের টুলের নাম বা কাঁচা মডেল আর্গুমেন্টের ওপর নির্ভর না করে সাড়া দিতে দেয়।

`FileSystem` নিজের কোনো OpenTelemetry span তৈরি করে না: core tool-call span আগে থেকেই প্রতিটি কাজ আর এর ফল লেখে, আর ওপরের event সেই diff বহন করে যা একটি trace করত না।

মডেল সংশোধন করতে পারে এমন টুল error -- একটি অনুপস্থিত ফাইল, একটি প্রত্যাখ্যাত path, একটি পুরনো সম্পাদনা, একটি বিদ্যমান ফাইলের সাথে সংঘর্ষ করা একটি ডিরেক্টরি, একটি অবৈধ glob pattern, Windows-এর প্রত্যাখ্যাত একটি path নাম, filesystem encode করতে পারে না এমন একটি path নাম, একটি অতি-লম্বা path নাম, একটি symlink loop, একটি FIFO বা অন্য বিশেষ ফাইল -- [`ModelRetry`](../agent.md#reflection-and-self-correction) হিসেবে প্রকাশিত হয়, তাই এজেন্ট রান বাতিল না করে error বার্তা ফেরত পায় আর মানিয়ে নিতে পারে। মডেল যে ব্যর্থতায় কিছুই করতে পারে না, যেমন একটি পূর্ণ ডিস্ক বা চলে যাওয়া একটি workspace, তবুও বাতিল করে।

একটি OS error একটি filename দিলে, `FileSystem` এটি `root_dir`-এর আপেক্ষিক হিসেবে জানায়; `root_dir`-এর বাইরের path হয়ে যায় `<outside-workspace>`। `file_info` absolute symlink লক্ষ্যে একই নিয়ম প্রয়োগ করে।

## নিরাপত্তা মডেল { #security-model }

- **সীমা (Containment)।** প্রতিটি টুল কল এর path মীমাংসা করে, symlink-সহ, আর `root_dir`-এর বাইরে নিয়ে যাওয়া একটি প্রত্যাখ্যান করে, `..`, একটি absolute path বা একটি symlink — যেভাবেই হোক। তালিকা বাইরে নিয়ে যাওয়া একটি লিংকের নাম দিতে পারে, কিন্তু এটি পড়া বা লেখা প্রত্যাখ্যাত হয়, আর ডিরেক্টরি walker এতে নামে না। Pattern `root_dir`-এর আপেক্ষিক path মেলায়; `read_only_patterns` আর `denied_patterns` একটি symlink-এর লক্ষ্যও মেলায়, তাই `.env`-এ একটি লিংক `.env`-এর মতোই শুধু-পড়া। Denied আর read-only pattern case উপেক্ষা করে, তাই একটি case-insensitive filesystem-এ `.GIT/config` `**/.git` এড়িয়ে যেতে পারে না। `root_dir='/'` সীমা বন্ধ করে; pattern তবুও প্রযোজ্য, আর কোনো pattern-ও সেট না থাকলে সীমা-যাচাই পুরোপুরি বন্ধ।
- **Symlink-এর জন্য workspace-এর `realpath` লাগে।** লোকাল আর কমান্ড-চালানো workspace এই যাচাইয়ের জন্য symlink মীমাংসা করে। `SupportsRealpath` ছাড়া একটি শুধু-filesystem backend শুধু path-এর লেখা দেয়: `root_dir`-এর বাইরের `..` আর absolute path তবুও প্রত্যাখ্যাত, কিন্তু বাইরে নিয়ে যাওয়া একটি symlink ধরা পড়ে না, আর `.env`-এ একটি লিংক pattern মেলায় না। symlink ছাড়া storage-এর জন্য এটি সঠিক, যেমন একটি object store।
- **একটি guardrail, বিচ্ছিন্নতা নয়।** সীমা আর allow, deny ও read-only pattern কার্যকরী guardrail। `LocalWorkspace` একটি নিরাপত্তা বিচ্ছিন্নতার সীমা প্রতিষ্ঠা করে না, কমান্ড চালানো বন্ধ থাকলেও। workspace process-এর বিদ্যমান OS কর্তৃত্বের ভেতরে এড়ানো হলো সঠিকতার bug। যাচাই প্রতিটি কাজের আগে চলে, তাই যাচাই আর ব্যবহারের মাঝে বদলানো একটি symlink ধরা পড়ে না, আর `Shell` কমান্ড `root_dir` পুরোপুরি উপেক্ষা করে। বিচ্ছিন্নতার জন্য, একটি sandbox workspace ব্যবহার করুন আর দরকারি resource রক্ষায় এর সীমা কনফিগার করুন। সেই সীমার ভেতরের ফাইল এজেন্টের কাছ থেকে নিজে থেকে গোপন নয়।
- **সীমিত হাঁটা।** `search_files` আর `find_files` 10,000 ডিরেক্টরি বা 100,000 entry-র পর থামে আর তাদের ফল একটি `[... walk cut short ...]` লাইন দিয়ে শেষ করে।
- **Binary শনাক্তকরণ।** `read_file` binary bytes মডেলের context-এ decode করে না। এটি একটি ছবি (PNG, JPEG, GIF, WebP) বা PDF `BinaryContent` হিসেবে ফেরত দেয়, এর extension নয়, শুরুর bytes দিয়ে চিনে, যা Pydantic AI মডেল অনুযায়ী [টুলের ফলের ভেতরে বা user channel-এ](../tools-advanced.md#tool-return-file-provenance) পাঠায়। মডেল সেই ধরনের ফাইল নিতে না পারলে (vision ছাড়া একটি মডেলে একটি ছবি, বা Groq-এ একটি PDF), Pydantic AI পরের রিকোয়েস্ট তৈরির সময় exception তোলে, যা রান শেষ করে ([input support by model](../input.md))। 5 MB-এর বেশি একটি ফাইল, মূলধারার সবচেয়ে কঠোর প্রতি-ছবি সীমা, এর বদলে বর্ণনা করা হয়, যেমন হয় অন্য যেকোনো binary ফাইল।
- **Optimistic concurrency।** `write_file`/`edit_file` একটি `expected_hash` নেয়, যাতে একটি পুরনো পড়ার ওপর কাজ করা এজেন্টকে নতুনতর কনটেন্ট নিঃশব্দে overwrite না করে আবার পড়তে বলা হয়।
- **লেখার লক্ষ্য।** `write_file` একটি ডিরেক্টরি overwrite করবে না। একটি FIFO, socket বা device একটি নিয়মিত ফাইল নয় বলে প্রত্যাখ্যাত।
- **সীমিত পড়া।** `read_file` আর `file_info` এর লাইন সংখ্যা আর hash-এর জন্য একটি ফাইল পুরোটা পড়ে, তাই 64 MiB-এর বেশি একটি ফাইল এর বদলে এর আকার দিয়ে বর্ণনা করা হয়। আকার জানায় না এমন একটি workspace বর্ণনার আগে তবুও এমন একটি ফাইল পড়ে।

/// warning | সাধারণ ভুল

`FileSystem(root_dir='./project')` দিয়ে ভাবা যে এজেন্ট এখন project-এর বাইরে কিছু ছুঁতে পারবে না — অথচ সাথে `Shell`-ও আছে। `Shell` কমান্ড `root_dir` মানে না: `cat ~/.ssh/id_rsa` ঠিকই চলবে। সত্যিকারের বিচ্ছিন্নতা চাইলে একটি sandbox workspace ব্যবহার করুন।

///

### নিজস্ব storage { #custom-storage }

ফাইল অন্য কোথাও রাখতে, `SupportsFilesystem` (আর ripgrep সার্চ ও `file_info` symlink লক্ষ্যের জন্য `SupportsCommands`) বাস্তবায়ন করা একটি `WorkspaceBackend` লিখে রানে যুক্ত করুন। সীমা, pattern, event আর hash অপরিবর্তিত প্রযোজ্য। এটি সরানো `FileSystemToolset.open_read` আর `open_write` hook-এর জায়গা নেয়।

একটি রানের বাইরে নিজে একটি টুল মেথড ডাকতে, workspace দিন:

```python
from pydantic_ai.workspaces import LocalWorkspaceBackend
from pydantic_ai_harness.filesystem import FileSystem, FileSystemToolset


async def main() -> None:
    toolset = FileSystem().get_toolset()
    assert isinstance(toolset, FileSystemToolset)
    print(await toolset.read_file('README.md', workspace=LocalWorkspaceBackend('.')))
```

## Pattern ছাঁকনি { #pattern-filtering }

তিনটি স্বাধীন glob লিস্ট প্রবেশ নিয়ন্ত্রণ করে। Pattern `fnmatch` দিয়ে মেলানো হয়, যার `*` `/` পেরোয়, তাই `*.py` `src/main.py` মেলায় আর আপনার খুব কমই `**` লাগে।

| ফিল্ড | প্রভাব |
|---|---|
| `allowed_patterns` | খালি না হলে, শুধু মিলে যাওয়া path প্রবেশযোগ্য (allowlist)। |
| `denied_patterns` | মিলে যাওয়া path প্রত্যাখ্যাত (denylist), `allowed_patterns` এগুলো মেলালেও। মেলানো case উপেক্ষা করে। |
| `read_only_patterns` | মিলে যাওয়া path শুধু-পড়া: পড়া সফল হয়, লেখা প্রত্যাখ্যাত। মেলানো case উপেক্ষা করে। |

একটি ডিরেক্টরি pattern উত্তরসূরিদেরও প্রযোজ্য: `denied_patterns=['private']` `private`-এর পাশাপাশি `private/notes.txt`-ও প্রত্যাখ্যান করে। শুধু-পড়া ডিরেক্টরি pattern একইভাবে এদের নিচের লেখা রক্ষা করে।

`read_only_patterns`-এর ডিফল্ট `**/.git`, `**/.env`, `**/.env.*`, `*.pem`, `*.key`,
`**/secrets*` আর `**/.pydantic-ai-harness/**`, যা যেকোনো গভীরতায় মেলে। যেমন, `apps/api/.env` আর `sub/.git/config` root-স্তরের ফাইলের সাথে রক্ষিত, আর তেমনি একটি `.git` ফাইল, যা একটি git worktree বা submodule-এ ডিরেক্টরির জায়গায় থাকে। রক্ষিত path পাঠযোগ্য থাকে; একটি path অপাঠ্য করতে `denied_patterns`-এ যোগ করুন। Harness capability নিজেদের ফাইল, যেমন ঢালা টুল আউটপুট আর background job status, `.pydantic-ai-harness/`-এর নিচে রাখে। প্রতিটি path লেখা-যোগ্য করতে একটি খালি লিস্ট দিন।
`protected_patterns` হলো এর অবচিত নাম আর এখনও কাজ করে, একটি সতর্কবার্তাসহ।

```python
from pydantic_ai import Agent
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai_harness import FileSystem

agent = Agent(
    'anthropic:claude-opus-5-5',
    capabilities=[
        LocalWorkspace('.'),
        FileSystem(
            allowed_patterns=['*.py', '*.toml'],
            denied_patterns=['**/node_modules/*'],
        ),
    ],
)
```

### সরাসরি প্রবেশ বনাম walker { #direct-access-vs-walkers }

তিনটি নিয়ম দুটি ভিন্ন সূক্ষ্মতায় প্রযোজ্য:

- **সরাসরি প্রবেশ** (`read_file`, `write_file`, `edit_file`, `file_info`, `create_directory`) কাজের লক্ষ্য path নিয়ন্ত্রণ করে। আপনাকে এমন একটি path-এর নাম দিতে হবে যা pattern অনুমতি দেয়।
- **Walker** (`list_directory`, `search_files`, `find_files`, `list_files`, `grep`) তাদের root নিয়ন্ত্রণ করে denied pattern দিয়ে, কিন্তু `allowed_patterns` দিয়ে **নয়** -- `.`-এর মতো একটি ডিরেক্টরি root কখনো `src/*.py`-এর মতো একটি ফাইল pattern মেলায় না, তাই এটি বাধ্যতামূলক করলে প্রতিটি তালিকা ব্যর্থ হতো। এর বদলে, root হাঁটা হয় আর প্রতিটি **entry** `allowed_patterns` আর `denied_patterns`-এর বিপরীতে পড়ার-স্তরের প্রবেশ দিয়ে ছাঁকা হয়। একটি ডিরেক্টরি তালিকা এমন একটি path প্রকাশ করতে পারে না যা এজেন্ট অন্যথায় পড়তে পারত না।

তাই `allowed_patterns=['*.py']`-সহ, `list_directory('.')` সফল হয় আর শুধু `.py` entry দেখায়; `read_file('notes.md')` প্রত্যাখ্যাত।

শুধু `read_only_patterns` মেলানো একটি entry লুকায় না। allowed, denied আর dotfile ছাঁকনি পেরোনো শুধু-পড়া path walker-এর কাছে দৃশ্যমান থাকে আর `read_file`/`file_info` দিয়ে সরাসরি পাঠযোগ্য; লেখার কাজ এগুলো প্রত্যাখ্যান করে।

/// note | মনে রাখুন

Walker (`list_directory`, `search_files`, `find_files`, `list_files` আর `grep`) dotfile আর dot-ডিরেক্টরি বাদ দেয়, যদি না glob একটির নাম দেয় (`.github/*`) বা সার্চ path একটি হয়।

///

## কনফিগারেশন { #configuration }

```python
from pydantic_ai_harness.filesystem import DEFAULT_TOOL_NAMES, FileSystem

FileSystem(
    root_dir=None,                 # str | Path -- containment boundary (None = the working directory; '/' = no checks)
    allowed_patterns=[],           # allowlist globs (empty = allow all)
    denied_patterns=[],            # denylist globs
    read_only_patterns=[...],      # read-only globs (defaults to secrets/.git)
    max_read_lines=2000,           # most lines one read_file returns, and its default limit
    max_read_chars=50_000,         # cap on a whole read_file result, ending on a complete line
    max_list_results=1000,         # cap for list_directory
    max_search_results=1000,       # cap for search_files and grep
    max_find_results=1000,         # cap for find_files and list_files
    read_only=False,               # keep only READ_ONLY_TOOL_NAMES
    content_hashes=True,           # report hashes and accept expected_hash
    tools=DEFAULT_TOOL_NAMES,      # which tools to register (add 'list_files', 'grep')
    max_retries=None,              # consecutive retries per tool before the run fails (None = the agent's budget)
)
```

পূর্ণসংখ্যার সীমা ধনাত্মক হতে হবে; তৈরির সময় এগুলো যাচাই হয় আর অন্যথায় `ValueError` তোলে। একটি walker এর সীমায় পৌঁছালে এর আউটপুট একটি `[... truncated at N ...]` চিহ্ন দিয়ে শেষ করে, আর শুধু তখনই যখন আরেকটি entry সত্যিই বাদ পড়েছে।

## Agent spec (YAML/JSON) { #agent-spec-yamljson }

`FileSystem` Pydantic AI-এর [agent spec](../agent-spec.md)-এর সাথে কাজ করে:

```yaml
model: anthropic:claude-opus-5-5
capabilities:
  - FileSystem:
      allowed_patterns: ['*.py', '*.toml']
```

```python
from pydantic_ai import Agent
from pydantic_ai_harness import FileSystem

agent = Agent.from_file('agent.yaml', custom_capability_types=[FileSystem])
```

`custom_capability_types` দিন, যাতে spec loader জানে `FileSystem` কীভাবে তৈরি করতে হয়, আর রানে একটি workspace যুক্ত করুন (রান মেথডে `workspace=`, বা Python-এ একটি workspace capability)।

## Durable execution { #durable-execution }

`FileSystem` Temporal, DBOS আর Prefect-এর অধীনে কাজ করে; [workspace guide](../workspace.md#durable-execution) দেখায় প্রতিটি engine-এ কী কাজ করে। Temporal-এ শুধু file-change রিকোয়েস্ট আর লেখার event listener-দের কাছে লাইভ পৌঁছায়; দেখুন [live events on Temporal](../durable_execution/temporal.md#harness-workspace-capabilities)।

## আরও পড়ুন { #further-reading }

- [Pydantic AI capabilities](../capabilities/overview.md)
- [Toolsets](../toolsets.md)
- [the capabilities overview](index.md)

## API রেফারেন্স { #api-reference }

::: pydantic_ai_harness.FileSystem
    options:
        inherited_members: false
        show_if_no_docstring: false
        allow_inspection: false
        docstring_options:
          ignore_init_summary: true
        show_root_heading: true

/// check | সংক্ষেপে মনে রাখুন

* `FileSystem` = `root_dir`-এ সীমিত আটটি ফাইল টুল (+ ঐচ্ছিক `list_files`/`grep` ripgrep টুল); একটি workspace লাগে।
* প্রতিটি path symlink-সহ মীমাংসা হয়ে সীমার ভেতরে কিনা যাচাই হয়; `.git`, `.env`, key, secret ডিফল্টভাবে শুধু-পড়া।
* `expected_hash` দিয়ে পুরনো লেখা আটকানো; একক-লেখক এজেন্টে `content_hashes=False` token বাঁচায়।
* `FileChangeRequestEvent` লেখার আগে চলে — listener `cancel(reason)` দিয়ে পরিবর্তন আটকাতে পারে।
* এটি guardrail, বিচ্ছিন্নতা নয় — `Shell` `root_dir` মানে না; সত্যিকারের বিচ্ছিন্নতায় sandbox।

///
