
# Bubblewrap Sandbox { #bubblewrap-sandbox }

/// note | এই পেজে যা শিখবেন

* কমান্ড যে host-এ চলে সেখানেই (SSH-এ বা লোকালে) একটি Linux [bubblewrap](https://github.com/containers/bubblewrap) (`bwrap`) sandbox-এ এজেন্টের কমান্ড চালানো।
* sandbox কী অনুমতি দেয় (host-এর ফাইল শুধু-পড়া, শুধু working directory লেখা-যোগ্য, নেটওয়ার্ক বন্ধ) আর কী রক্ষা করে না।
* `BubblewrapWorkspace` সরাসরি ব্যবহার।

///

একটি Linux [bubblewrap](https://github.com/containers/bubblewrap) (`bwrap`) sandbox-এ আপনার এজেন্টের কমান্ড চালান, যে host-এ এগুলো আগে থেকেই চলে সেখানেই, SSH-এর মাধ্যমে বা লোকালে।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/bubblewrap_sandbox/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

## ইনস্টল { #install }

/// tab | pip

```bash
pip install "pydantic-ai-harness[anthropic]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[anthropic]"
```

///


sandbox-এর host-কে `bwrap` ইনস্টল করা (`bubblewrap` প্যাকেজ) আর user namespace অনুমোদিত Linux চালাতে হবে; অন্যথায় কমান্ড `WorkspaceUnavailableError` তোলে। `anthropic` extra আছে কারণ উদাহরণগুলো একটি Anthropic মডেল ব্যবহার করে; এটি আপনার মডেল provider-এর extra দিয়ে বদলান।

## দ্রুত শুরু { #quick-start }

`BubblewrapSandbox` আরেকটি workspace capability মোড়ায় আর এর কমান্ড সেই workspace-এর host-এ একটি sandbox-এ চালায়। একটি দূরের host-এ কমান্ড sandbox করতে [`SSHWorkspace`](ssh-workspace.md) মুড়ুন, বা এটিতে করতে `LocalWorkspace`:

⟦CODE1⟧

/// tip | উদাহরণ দিয়ে বুঝি

`LocalWorkspace` একজন কর্মীকে আপনার পুরো অফিসের চাবি দেয়। `BubblewrapSandbox(LocalWorkspace('.'))` একই কর্মীকে একটা কাচের ঘরে বসায়: অফিসের সব কাগজ তিনি কাচের মধ্য দিয়ে **দেখতে** পারেন (শুধু-পড়া), কিন্তু শুধু নিজের টেবিলে (working directory) **লিখতে** পারেন, আর ঘরে কোনো ফোন নেই (নেটওয়ার্ক বন্ধ)। cloud VM-এর চেয়ে হালকা, কিন্তু Linux-এ লাগে।

///

## sandbox কী অনুমতি দেয় { #what-the-sandbox-allows }

মোড়ানো workspace-কে একটি নিয়ন্ত্রণকারী terminal ছাড়াই কমান্ড চালাতে হবে। `BubblewrapWorkspace` `bwrap --new-session` বাদ দেয়, যাতে backend timeout বা বাতিলে foreground উত্তরসূরিদের থামাতে পারে; একটি নিয়ন্ত্রণকারী terminal-সহ, `TIOCSTI` অনুমতি দেওয়া kernel-এ sandbox করা কমান্ড host terminal-এ input ঢোকাতে পারত। `LocalWorkspaceBackend` একটি নতুন session শুরু করে আর `SSHWorkspaceBackend` `ssh -T` ব্যবহার করে। `E2BSandboxBackend` আর `ModalSandboxBackend` তাদের provider-এর non-PTY কমান্ড API দিয়ে কমান্ড চালায়, তাই কোনো terminal যুক্ত থাকে না, image-এ `setsid` থাকুক বা না থাকুক। চারটিই এই শর্ত পূরণ করে; নিজস্ব backend-কেও করতে হবে।

sandbox-এর ভেতরে, কমান্ড host-এর ফাইল শুধু-পড়া দেখে, একটি ব্যক্তিগত `/tmp` আর কোনো নেটওয়ার্ক নয়, আর শুধু working directory-তে লিখতে পারে। `/run` খালি, কারণ Docker-এর মতো host daemon সেখানে socket-এ শোনে, আর একটি শুধু-পড়া mount একটি সংযোগ থামায় না। `bwrap`-কে sandbox-কে নিজস্ব একটি user namespace দিতে পারতে হবে, আর sandbox-এর কোনো capability নেই।

যখন working directory-তে host অ্যাকাউন্টের home ডিরেক্টরি থাকে, যেমন একটি `working_dir` ছাড়া `SSHWorkspace`-এ থাকে, তখন পরের SSH সংযোগ login করার সময়, কমান্ড শুরুর আগে, host যে ফাইল চালায় বা পড়ে সেগুলো শুধু-পড়া mount হয়: `~/.ssh`, `~/.pam_environment`, আর একটি কমান্ডের জন্য একটি login shell যে startup ফাইল চালায় (`~/.bashrc`, `~/.zshenv`, `~/.cshrc`, `~/.tcshrc` আর `~/.config/fish`)। অনুপস্থিতগুলো আগে খালি তৈরি হয়। এর একটি যদি symlink হয়, sandbox শুরু হয় না, কারণ একটি কমান্ড লিংকটি বদলে দিতে পারত।

নেটওয়ার্ক ছাড়া, একটি seccomp ছাঁকনি সেই একই system call আটকায় যা [Codex CLI](https://github.com/openai/codex)-এর Linux sandbox নেটওয়ার্ক প্রবেশ ছাড়া আটকায়: কমান্ড কোনো socket-এ সংযোগ, পরিবেশন বা গ্রহণ করতে পারে না, host-এর ডিস্কের অন্য কোথাও থাকা Unix socket আর sandbox-এর নিজস্ব loopback-সহ, আর `ptrace` বা `io_uring` ব্যবহার করতে পারে না। কমান্ড তবুও stream socket জোড়া তৈরি করতে পারে, যা language runtime তাদের নিজস্ব process-এর মাঝে ব্যবহার করে। Codex-এর বিপরীতে, Unix datagram socket-ও আটকানো, কারণ একটি datagram আগে সংযোগ না করেই যেকোনো socket ফাইলে ঠিকানা দেওয়া যায়। তাই একটি লোকাল server শুরু করা একটি test suite-এর `network=True` লাগে, আর তেমনি `multiprocessing`-এর জন্য Python-এর `forkserver` start method-এর (Python 3.14 থেকে Linux-এ ডিফল্ট), যা একটি socket-এ শোনে: `multiprocessing.get_context('spawn')` বা `'fork'` এটি ছাড়াই কাজ করে। ছাঁকনি x86_64 আর aarch64 host কভার করে; sandbox-এর একটি 32-bit প্রোগ্রাম একটি system call করলে থামানো হয়।

host-এর নেটওয়ার্ক ভাগ করতে `network=True` দিন: কমান্ড এতে পৌঁছাতে পারে, host-এর loopback-এর সার্ভিস আর host যা পৌঁছাতে পারে তার সবকিছুসহ, আর host-এর port-এ শুনতে পারে। `/run`-এর নিচের DNS কনফিগারেশন এর সাথে ফিরে আসে, আর কোনো seccomp ছাঁকনি নেই। `bwrap_args=` দিয়ে `bwrap` আর্গুমেন্ট যোগ করুন: এগুলো ডিফল্টের পরে আসে, তাই `['--bind', path, path]` আরেকটি ডিরেক্টরি লেখা-যোগ্য করে আর `['--tmpfs', path]` একটি লুকায়, যেমন `~/.ssh`। `bwrap` শুরু করা প্রোগ্রাম, আর ছাঁকনি লোডের সময় `base64`, working directory-র বাইরের একটি `PATH` ডিরেক্টরি থেকে নেওয়া হয়। working directory-তে host অ্যাকাউন্টের `~/.ssh` থাকলে, sandbox এটি শুধু-পড়া bind-mount করে, অনুপস্থিত থাকলে ডিরেক্টরি তৈরি করে, কারণ OpenSSH পরের সংযোগের আগে `~/.ssh/rc` চালায়। সেই যাচাই `cd -P` আর `pwd -P` দিয়ে একটি absolute `$HOME` পড়ে, আর `/bin/mkdir` দিয়ে একটি অনুপস্থিত ডিরেক্টরি তৈরি করে, তাই কোনো ধাপ `PATH` খোঁজে না। একটি absolute home ছাড়া sandbox শুরু হয় না। `bwrap_args` সেই mount-এর পরে আসে আর তবুও এটি বদলাতে পারে।

কমান্ড নিজস্ব একটি পাওয়ার বদলে host-এর process তালিকা ভাগ করে, তাই background-এ শুরু হওয়া একটি কমান্ড, যেমন একটি [Shell](shell.md) background job বা একটি dev server, এটি শুরু করা কলের পরেও, আর এজেন্ট রানের পরেও, কিছু না থামানো পর্যন্ত চলতে থাকে। পরের কল এটি যাচাই বা থামাতে পারে। timeout বা বাতিলে, কী থামে তা মোড়ানো backend-এর ওপর নির্ভর করে। `LocalWorkspaceBackend` আর `SSHWorkspaceBackend` কমান্ড আর এর foreground উত্তরসূরিদের থামায়; host আটকে গেলে বা অপ্রাপ্য হলে SSH পরিষ্কার-কাজ সর্বোত্তম-চেষ্টা। E2B আর Modal backend একই করে শুধু তখনই যখন image-এ `setsid` আছে, আর অন্যথায় শুধু কমান্ড নিজে থামায়, তাই এর সন্তানরা চলতে পারে। ইচ্ছাকৃতভাবে নিজস্ব session-এ বিচ্ছিন্ন job প্রতিটি backend-এ চলতে থাকে। মূল্য হলো sandbox করা কমান্ড host-এর process আর তাদের command line দেখতে পারে, আর host ব্যবহারকারীর নিজেরগুলোকে signal দিতে পারে। একটি কলের `env` মান `bwrap --setenv` আর্গুমেন্ট, তাই কমান্ড চলার সময় এগুলো সেই process তালিকায় দেখা যায়।

`write_text`-এর মতো ফাইল মেথড, আর তাই [FileSystem](filesystem.md) আর [Coder](coder.md) ফাইল টুলও, sandbox-এ shell কমান্ড হিসেবে চলে, তাই কমান্ড যা দেখে এগুলোও তা দেখে: এরা working directory-র বাইরে লিখতে পারে না, এমনকি একটি path যাচাইয়ের পর একটি কমান্ডের বদলে দেওয়া একটি symlink দিয়েও। শুধু যখন মোড়ানো workspace শুধু-পড়া, আর তাই কোনো কমান্ড চালায় না, তখনই এর ফাইল সরাসরি host থেকে পড়া হয়। রানের ref হলো মোড়ানো workspace-এর, আর এর `backend` হলো মোড়ানো backend।

/// info | এক নজরে: sandbox-এর ভেতরে

| জিনিস | অবস্থা |
|-------|--------|
| host-এর ফাইল | শুধু-পড়া |
| working directory | লেখা-যোগ্য |
| `/tmp` | ব্যক্তিগত |
| `/run` (Docker socket ইত্যাদি) | খালি |
| নেটওয়ার্ক | বন্ধ (seccomp ছাঁকনিসহ); `network=True` দিয়ে চালু |
| `~/.ssh`, shell startup ফাইল (home লেখা-যোগ্য হলে) | শুধু-পড়া |
| host-এর process তালিকা | দেখা যায় (ভাগ করা) |

///

### যা এটি রক্ষা করে না { #what-it-doesnt-protect }

sandbox একটি এজেন্টকে এর working directory-র বাইরে host বদলানো থেকে রক্ষা করে। এটি host ব্যবহারকারীর ক্ষতি করার চেষ্টা করা একটি এজেন্টের বিরুদ্ধে কোনো সীমা নয়:

- কমান্ড host ব্যবহারকারী পড়তে পারে এমন প্রতিটি ফাইল পড়তে পারে, যেমন SSH key আর cloud credential, আর মডেলকে দেখাতে পারে। `bwrap_args=['--tmpfs', path]` দিয়ে ওই ডিরেক্টরি লুকান।
- কমান্ড host ব্যবহারকারীর অন্য process-কে signal দিতে পারে, আর তাই থামাতে পারে।
- working directory-তে একটি কমান্ড যা লেখে, যেমন Git hook, একটি `Makefile` বা একটি `.envrc`, পরে sandbox-এর বাইরে চালালে sandbox ছাড়াই চলে।
- home ডিরেক্টরি লেখা-যোগ্য হলে, শুধু একটি interactive login যে ফাইল চালায় সেগুলোও লেখা-যোগ্য, যেমন `~/.profile` আর `~/.bash_profile`, আর অন্য প্রতি-ব্যবহারকারী কনফিগারেশন। এর বদলে sandbox-কে এর `working_dir` হিসেবে একটি project ডিরেক্টরি দিন।
- মোড়ানো workspace-এর নিজস্ব সেটিং, `bwrap_args`, আর working directory-র বাইরের host-এর `bwrap` বিশ্বস্ত।

আপনি বিশ্বাস করেন না এমন একটি এজেন্টের জন্য, host-এ একে নিজস্ব একটি ব্যবহারকারী দিন, বা [E2B](e2b-sandbox.md)-এর মতো একটি cloud sandbox ব্যবহার করুন।

/// warning | সাধারণ ভুল

`BubblewrapSandbox(LocalWorkspace('.'))` দিয়ে ভাবা যে `~/.aws/credentials` এখন নিরাপদ। sandbox শুধু **লেখা** আটকায় — পড়া নয়। এজেন্ট `cat ~/.aws/credentials` চালিয়ে মডেলকে দেখাতে পারে। গোপন ডিরেক্টরি `bwrap_args=['--tmpfs', '/home/me/.aws']` দিয়ে লুকান।

///

## workspace সরাসরি ব্যবহার { #use-the-workspace-directly }

capability একটি `BubblewrapWorkspace` তৈরি করে, একটি [`WrapperWorkspace`](../workspace.md#read-only-access), যা আপনি যেকোনো workspace-এর চারপাশে সরাসরিও ব্যবহার করতে পারেন:

⟦CODE2⟧

## Telemetry { #telemetry }

`BubblewrapSandbox` নিজের কোনো span তৈরি করে না। রানের workspace মোড়ানোটির, তাই core-এর [instrumentation](../capabilities/instrumentation.md) এজেন্ট run span-এ এর `pydantic_ai.workspace.provider` আর `pydantic_ai.workspace.id` লেখে, আর প্রতিটি sandbox করা কমান্ড এর tool call-এর span-এর ভেতরে চলে।

## API রেফারেন্স { #api-reference }

/// info | API রেফারেন্স

`pydantic_ai_harness.bubblewrap_sandbox.BubblewrapSandbox`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/bubblewrap-sandbox/)।

///

/// info | API রেফারেন্স

`pydantic_ai_harness.bubblewrap_sandbox.BubblewrapWorkspace`-এর API রেফারেন্স পাওয়া যায় [অফিসিয়াল ডকুমেন্টেশনে](https://pydantic.dev/docs/ai/harness/bubblewrap-sandbox/)।

///

/// check | সংক্ষেপে মনে রাখুন

* `BubblewrapSandbox(LocalWorkspace(...))` বা `BubblewrapSandbox(SSHWorkspace(...))` — একই host-এ Linux `bwrap` sandbox।
* host-এর ফাইল শুধু-পড়া, শুধু working directory লেখা-যোগ্য, নেটওয়ার্ক বন্ধ (`network=True` দিয়ে চালু)।
* এটি **পড়া** আটকায় না — secret ডিরেক্টরি `--tmpfs` দিয়ে লুকান।
* host-এর process তালিকা ভাগ করে; background কমান্ড রানের পরেও চলে।
* অবিশ্বস্ত এজেন্টের জন্য আলাদা ব্যবহারকারী বা cloud sandbox।

///
