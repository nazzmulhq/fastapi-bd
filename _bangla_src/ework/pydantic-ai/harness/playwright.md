
# Playwright Browser { #playwright-browser }

/// note | এই পেজে যা শিখবেন

* `PlaywrightBrowser` দিয়ে এজেন্টকে একটি আসল, state-রাখা Chromium browser দেওয়া — navigate, click, type, scroll, screenshot, JavaScript।
* আঠারোটি টুল, `snapshot` আর `aria-ref` handle, timeout, tab আর dialog।
* login-করা সাইট (`storage_state`), চলমান browser-এ যুক্ত হওয়া, iframe, ডিবাগিং আর egress/SSRF সুরক্ষা।

///

`PlaywrightBrowser` async [Playwright](https://playwright.dev/python/) দিয়ে একটি এজেন্টকে একটি আসল, state-রাখা Chromium browser দেয়: navigate, click, type, scroll, ইতিহাসে আগে-পিছে যাওয়া, পেজের লেখা বের করা, JavaScript চালানো আর screenshot।

হালকা ওয়েব টুল যথেষ্ট না হলে এটি ধরুন। একটি web search টুল একটি পেজ লোড না করেই একটি গবেষণা প্রশ্নের উত্তর দেয়, আর একটি web-fetch টুল একটি জানা স্থির URL সামলায়। এই capability তা কভার করে যেখানে কোনোটিই পৌঁছাতে পারে না: login বা session cookie-র পেছনের পেজ, JavaScript-রেন্ডার করা SPA, আর interactive বহু-ধাপের flow।

[Source](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness/playwright/)

> Pydantic AI Harness 0.x release-এ থাকা অবস্থায়, minor release-এর মধ্যে API বদলাতে পারে; বদলালে, deprecation warning আর release-note-এর migration নির্দেশনা আপনাকে (বা আপনার এজেন্টকে) ঠিক কীভাবে আপগ্রেড করতে হবে তা বলে দেয়। দেখুন [version policy](index.md#version-policy)।

/// note | কোন browser capability?

এই পেজ host মডেল থেকে browser চালানো আলোচনা করে: টাইপ করা, নির্ধারিত action, একবারে একটি টুল কল। একটি খোলামেলা লক্ষ্য এমন একটি স্বয়ংক্রিয় এজেন্টকে দিতে যা আপনার জন্য browser চালায়, দেখুন [Browser Use](browser-use.md)। একটি এজেন্টকে একটি বা অন্যটি দিন: প্রতিটি capability নিজের browser চালায়, তাই একটির খোলা session অন্যটির কাছে দৃশ্যমান নয়।

///

## ইনস্টলেশন { #installation }

`playwright` extra Playwright টেনে আনে, আর Chromium একটি আলাদা binary ডাউনলোড:

/// tab | pip

```bash
pip install "pydantic-ai-harness[playwright]"
```

///

/// tab | uv

```bash
uv add "pydantic-ai-harness[playwright]"
```

///


/// tab | pip

```bash
playwright install chromium
```

///

/// tab | uv

```bash
uv run playwright install chromium
```

///


রানের সময় Chromium binary অনুপস্থিত থাকলে, browser টুল রান শেষ না করে এর ফল হিসেবে `playwright install chromium` ইঙ্গিত ফেরত দেয়, তাই একটি shell চালাতে পারা একটি এজেন্ট browser ইনস্টল করে চালিয়ে যেতে পারে; ব্যর্থতা মনে রাখা হয় না, তাই পরের কল চালু করে। process একটি `BrowserUnavailableWarning`-ও পায়, কারণ একটি terminal দেখা একজন ডেভেলপার টুলের ফল বা trace কোনোটিই দেখেন না। প্রথম অনুপস্থিতিতে নিজে থেকে binary আনতে `auto_install_chromium=True` সেট করুন।

## ব্যবহার { #usage }

⟦CODE1⟧

`PlaywrightBrowser` একটি [capability](../capabilities/overview.md): এটি browser toolset নিবন্ধন করে, system prompt-এ কখন-ব্যবহার-করবে তার সংক্ষিপ্ত নির্দেশনা বসায়, আর রানের জন্য Chromium lifecycle পরিচালনা করে।

## টুল { #tools }

| টুল | Signature | ফেরত দেয় |
|---|---|---|
| `navigate` | `(url, timeout_ms=None)` | পেজের URL, শিরোনাম আর দৃশ্যমান লেখা (ছাঁটা) |
| `snapshot` | `(timeout_ms=None)` | `aria-ref` handle-সহ accessibility tree (ছাঁটা) |
| `click` | `(selector, timeout_ms=None)` | click-এর পর পেজের লেখা; `selector` একটি CSS selector, একটি `aria-ref=` handle, বা `'x,y'` pixel স্থানাঙ্ক |
| `type_text` | `(selector, text, sequential=False, timeout_ms=None)` | টাইপের পর পেজের লেখা (ফিল্ডের মান বদলায়, submit করে না); `sequential=True` আসল key press পাঠায় |
| `press_key` | `(key, selector=None, timeout_ms=None)` | key press-এর পর পেজের লেখা; `key` একটি Playwright key নাম (`Enter`, `Escape`, `Tab`, `Control+a`) |
| `select_option` | `(selector, values, timeout_ms=None)` | একটি `<select>`-এ অপশন বাছার পর পেজের লেখা |
| `hover` | `(selector, timeout_ms=None)` | hover-এর পর পেজের লেখা, শুধু-hover মেনু প্রকাশ করে |
| `wait_for` | `(selector=None, text=None, gone=False, timeout_ms=None)` | পেজে বা যেকোনো frame-এ element/লেখা দেখা দিলে -- বা, `gone=True`-সহ, চলে গেলে -- পেজের লেখা; `selector`/`text`-এর ঠিক একটি দিন |
| `screenshot` | `(full_page=False, timeout_ms=None)` | পেজের URL-সহ একটি নোট, সাথে image কনটেন্ট হিসেবে PNG |
| `get_text` | `(selector=None, timeout_ms=None)` | element-এর লেখা, বা পুরো পেজের দৃশ্যমান লেখা |
| `scroll` | `(direction, x=None, y=None, timeout_ms=None)` | পেজ এখন কোথায় আছে, আর এর লেখা; `direction` হলো up/down/left/right (এক পর্দা) বা top/bottom |
| `go_back` | `(timeout_ms=None)` | আগের পেজের লেখা |
| `go_forward` | `(timeout_ms=None)` | পরের পেজের লেখা |
| `execute_js` | `(script, timeout_ms=None)` | JavaScript-এর ফল (string যেমন আছে, অবজেক্ট JSON হিসেবে, `null` `undefined` হিসেবে) |
| `console_messages` | `(errors_only=False)` | console আউটপুট আর অধরা script error, পুরনোটি আগে |
| `tabs` | `(action='list', index=None)` | খোলা tab, বা একটি নিশ্চিতকরণ আর সক্রিয় tab-এর লেখা; `action` হলো `list`/`select`/`close`/`new` |
| `handle_next_dialog` | `(accept, prompt_text=None)` | পরের `alert`/`confirm`/`prompt`-এর উত্তর কীভাবে দেওয়া হবে তার একটি নিশ্চিতকরণ |
| `network_requests` | `(url_contains=None, errors_only=False)` | পেজের করা রিকোয়েস্ট এদের status-সহ, egress নীতির প্রত্যাখ্যাতগুলোসহ |

প্রতিটি পেজ action ওই একটি কলের জন্য দুটি ডিফল্টই override করতে একটি ঐচ্ছিক `timeout_ms` নেয়। একটি override 0-এর বেশি হতে হবে: `0` সময়সীমা পুরোপুরি বন্ধ করে, যা একটি capability ডিফল্ট হিসেবে উপলব্ধ থাকে কিন্তু মডেলের বাছা একটি আর্গুমেন্ট হিসেবে নয়।

একটি সময়সীমা পুরো টুল কল সীমিত করে, এর ভেতরের প্রতিটি Playwright কল নয়। একটি `navigate` একটি goto, একটি load state, একটি শিরোনাম, একটি body পড়া আর সম্ভবত একটি screenshot-এর অপেক্ষা করে; প্রতিটি পর্যায় পুরো সংখ্যা আবার না পেয়ে বাজেটের বাকিটা পায়, তাই `timeout_ms` হলো কল সবচেয়ে বেশি যত সময় নিতে পারে।

একটির বদলে দুটি ডিফল্ট, কারণ দুটি ব্যর্থতা ভিন্ন। মিস করা একটি action (`click`, `get_text`, `wait_for`) সাধারণত কিছুই মেলে না এমন একটি selector, আর `action_timeout_ms` (5s) একে একটি আটকানো এজেন্ট মনে হওয়ার মতো লম্বা অপেক্ষার বদলে একটি দ্রুত, পাঠযোগ্য ব্যর্থতায় বদলায়। একটি পেজ লোড ন্যায্যভাবে বেশি সময় নেয়, তাই navigation, load স্থির হওয়া আর browser শুরু বা এতে যুক্ত হওয়া `navigation_timeout_ms` (60s) ব্যবহার করে।

`snapshot` পেজের accessibility tree ফেরত দেয়, মডেলের পেজ পড়ার আর `aria-ref=eN` handle পাওয়ার কম-খরচের কাঠামোবদ্ধ উপায়। একটি element-কে এর `aria-ref=` handle দিয়ে লক্ষ্য করা (`click` বা `type_text`-এ দেওয়া) মডেলের লেখা একটি CSS selector-এর চেয়ে বেশি নির্ভরযোগ্য। snapshot-এ iframe কনটেন্ট থাকে (দেখুন [Embedded content](#embedded-content-iframes))। শুধু দৃশ্যমান যাচাই দরকার হলেই `screenshot` ধরুন (chart, লেআউট)।

/// tip | উদাহরণ দিয়ে বুঝি

একটি পেজে ২০টা "Submit" বাটন থাকতে পারে, আর মডেলের লেখা `button.submit` selector ভুলটায় click করতে পারে। `snapshot` পেজের একটি "সূচিপত্র" দেয়: `[e7] button "Place order"`, `[e12] button "Cancel"`। মডেল তখন `click('aria-ref=e7')` বলে — ঠিক সেই বাটনটিই, কোনো অনুমান ছাড়া।

///

`type_text` একটি ফিল্ড পূরণ করে কিন্তু submit করে না; `press_key('Enter')` করে। একটি নেটিভ `<select>` পেজ কনটেন্ট হিসেবে খোলে না, তাই `click`-এর বদলে `select_option` এটি চালায়। `type_text` এক ধাপে মান সেট করে আর কোনো key event পাঠায় না, যা দ্রুত আর একটি সাধারণ ফর্মের জন্য যথেষ্ট; প্রতিটি keystroke-এ সাড়া দেওয়া একটি ফিল্ডের জন্য `sequential=True` দিন -- autocomplete আর type-ahead widget, মাস্ক করা বা ফরম্যাট করা input, আর সরাসরি সেট করা মান উপেক্ষা করা editor।

`wait_for` কনটেন্ট আসার অপেক্ষা করে; `wait_for(gone=True)` এটি চলে যাওয়ার অপেক্ষা করে, যেভাবে একটি spinner বা একটি overlay পার করা হয় যখন এর জায়গায় কী আসবে তা আগে থেকে জানা নেই।

প্রতিটি টুল সক্রিয় tab-এ কাজ করে। একটি `target="_blank"` লিংক, একটি sign-in popup বা একটি payment ধাপ একটি দ্বিতীয় tab খোলে, যা বন্ধ না হয়ে খোলা থাকে: `tabs('list')` দেখায় কী খোলা আর `tabs('select', index)` সেখানে যায়। একটি session সর্বোচ্চ আটটি tab রাখে: এর বেশি হলে, পেজের খোলা একটি tab বন্ধ করে লেখা হয়, আর `tabs('new')` প্রত্যাখ্যাত হয়ে মডেলকে আগে একটি বন্ধ করতে বলে। একটি পেজ dialog (`alert`, `confirm`, `prompt`) উত্তর না পাওয়া পর্যন্ত পেজ আটকে রাখে, আর এটি খোলা action-এর আগে `handle_next_dialog(accept=True)` ডাকা না হলে বাতিল হয় -- সেই কল একটি dialog কভার করে, রানের বাকিটা নয়।

`screenshot` (আর ঐচ্ছিক `screenshot_on_navigate` সংযুক্তি) ছবিটি একটি base64 string-এর বদলে [`BinaryContent`][pydantic_ai.messages.BinaryContent] হিসেবে ফেরত দেয়, তাই vision মডেল লেখার context-এ base64-এর একটি দেয়ালের বদলে ছবিটি নেটিভভাবে দেখে। 5 MB-এর বেশি একটি capture (সাধারণত একটি লম্বা পেজের একটি পূর্ণ-পেজ screenshot) image কনটেন্টের বদলে একটি সীমিত error হিসেবে ফেরত আসে, কারণ মডেল provider অতিরিক্ত বড় ছবি প্রত্যাখ্যান করে আর ব্যর্থতা অন্যথায় রান বাতিল করত; এর বদলে viewport capture করুন বা স্ক্রল করে অংশ capture করুন।

Browser টুলের ব্যর্থতা -- একটি timeout, কোনো element মেলে না এমন একটি selector, একটি navigation error, বা রানের মাঝে বন্ধ হওয়া একটি browser -- এজেন্ট রান বাতিল করতে তোলা হয় না, বরং মডেলকে এমন error string হিসেবে ফেরত দেওয়া হয় যার ওপর এটি কাজ করতে পারে (retry, অন্য selector চেষ্টা, আবার navigate)।

## অপশন { #options }

| অপশন | ডিফল্ট | উদ্দেশ্য |
|---|---|---|
| `headless` | `True` | একটি দৃশ্যমান window ছাড়া Chromium চালানো (সার্ভার আর CI-র জন্য মানানসই)। |
| `allowed_domains` | `None` | navigation আর ডেটা রিকোয়েস্টের egress allowlist; `None` প্রতিটি পাবলিক host অনুমতি দেয় (দেখুন [Egress](#egress-and-ssrf))। |
| `policy` | `None` | পূর্ণ `EgressPolicy`, এমন নিয়মের জন্য যা দুটি সংক্ষিপ্ত রূপ প্রকাশ করতে পারে না। এদের সাথে পরস্পর-বর্জিত। |
| `block_private_addresses` | `True` | private, loopback, link-local আর অন্য সংরক্ষিত ঠিকানা প্রত্যাখ্যান, একটি IP হিসেবে লেখা হোক বা একটিতে মীমাংসা হওয়া একটি hostname দিয়ে পৌঁছানো (দেখুন [Egress](#egress-and-ssrf))। |
| `screenshot_on_navigate` | `False` | প্রতিটি `navigate` ফলে একটি screenshot যুক্ত করা। |
| `max_content_tokens` | `4000` | প্রতিটি লেখার টুল ফলের আনুমানিক token বাজেট। |
| `action_timeout_ms` | `5000` | element action-এর (click, type, read, wait) ডিফল্ট সময়সীমা। `0` এটি বন্ধ করে। |
| `navigation_timeout_ms` | `60000` | navigation আর load স্থির হওয়া, আর browser শুরু বা এতে যুক্ত হওয়ার ডিফল্ট সময়সীমা। `0` এটি বন্ধ করে। |
| `chromium_sandbox` | `True` | চালু করা Chromium এর renderer sandbox-সহ চালানো। শুধু যেখানে sandbox শুরু হতে পারে না সেখানে বন্ধ করুন (দরকারি kernel অনুমতি ছাড়া একটি container)। `cdp_url`-সহ উপেক্ষিত। |
| `auto_install_chromium` | `False` | binary অনুপস্থিত থাকলে নিজে থেকে Chromium আনা। |
| `storage_state` | `None` | চালুর সময় লোড করা Playwright storage state (cookie + localStorage); দেখুন [Authenticated sites](#authenticated-sites)। |
| `cdp_url` | `None` | একটি চালু না করে এই CDP endpoint-এ ইতিমধ্যে চলমান একটি Chromium-এ যুক্ত হওয়া; দেখুন [Attaching to a running browser](#attaching-to-a-running-browser)। |

## এর দুটি { #two-of-them }

`PlaywrightBrowser` ডিফল্ট `id` `'playwright_browser'` ঘোষণা করে। `id` capability-র instructions-এর key, যাতে এগুলো চিহ্নিত করা যায়, আর একটি ছাড়াই `defer_loading=True` কাজ করতে দেয়। এটি ভাগ করা এক এজেন্টে দুটি `PlaywrightBrowser` একটি browser দুবার বলা: মিললে এরা এক হয়ে যায়, আর ভিন্ন হলে এজেন্ট তৈরির সময় একটি `UserError` তোলে। এর বদলে মেলানো এদের একটিকে দেওয়া egress প্রশস্ত করতে পারত। দুটি রাখতে, প্রতিটিকে নিজের `id` দিন আর এগুলো [PrefixTools](../capabilities/prefix-tools.md)-এ মুড়ুন, কারণ দুটোই একই browser টুল নিবন্ধন করে।

আগের release কোনো ডিফল্ট `id` ঘোষণা করত না, তাই রান শুরুর সময় দুটি সবসময় টুলের নামে ব্যর্থ হতো। এখন দুটি অভিন্ন এক হয়ে যায়, আর ভিন্ন দুটি এজেন্ট তৈরির সময় ব্যর্থ হয়।

## Login-করা সাইট { #authenticated-sites }

ইতিমধ্যে login অবস্থায় browser শুরু করতে `storage_state` দিন। এটি একটি Playwright [storage state](https://playwright.dev/python/docs/auth) অবজেক্ট -- cookie আর localStorage -- চালুর সময় browser context-এ লোড, তাই প্রথম navigation ইতিমধ্যে authenticate করা।

একটি দৃশ্যমান browser দিয়ে login করে, আপনার নিজের কোডে, একবার এটি ধরুন:

⟦CODE2⟧

`playwright codegen https://example.com --save-storage=auth.json` একই কাঠামো একটি ফাইলে লেখে, যা আপনি `json.loads(Path('auth.json').read_text())` দিয়ে লোড করেন। যেকোনোভাবে, অবজেক্টটি capability-কে দিন:

⟦CODE3⟧

অপশনটি একটি path-এর বদলে একটি অবজেক্ট নেয়, কারণ এজেন্ট সাধারণত ভাগ করা environment-এ চলে যেখানে লোকাল filesystem টেকসই কিছু রাখার জায়গা নয়: state কোথায় থাকবে তা আপনার সিদ্ধান্ত, capability-র নয়। একই কারণে `PlaywrightBrowser.from_spec` `storage_state` গ্রহণ করে না -- একটি spec cookie-কে যা-ই এটি রাখে তাতে বহন করত। এর বদলে তৈরি capability-তে এটি সেট করুন।

capability ডিফল্টভাবে headless চলে আর নিজে login flow চালায় না: আপনি আলাদাভাবে state ধরেন। সাধারণ ধরন হলো একবার একটি দৃশ্যমান browser দিয়ে login করা, তারপর headless রানের জন্য state পুনর্ব্যবহার।

state-কে credential হিসেবে ধরুন: এটি অ্যাকাউন্টের ছদ্মবেশ নিতে পারে। এটি source control আর log-এর বাইরে রাখুন, সংরক্ষণ করলে সীমিত অনুমতিতে রাখুন, আর session মেয়াদোত্তীর্ণ হলে ফেলে দিন। এটি Playwright-এর নিজস্ব [auth-guide](https://playwright.dev/python/docs/auth) সতর্কতার প্রতিচ্ছবি। একটি পূর্ণ browser profile পুনর্ব্যবহারের বদলে একটি ন্যূনতম-পরিসরের state পছন্দ করুন (ধরার সময় শুধু লক্ষ্য সাইটে login করুন)।

/// warning | সাধারণ ভুল

`auth.json` (storage state) git repository-তে commit করা। এতে আপনার session cookie থাকে — repo দেখতে পারা যে কেউ আপনার অ্যাকাউন্টে login অবস্থায় ঢুকে পড়তে পারে, password ছাড়াই। এটি `.gitignore`-এ রাখুন আর একটি secret manager-এ সংরক্ষণ করুন।

///

## চলমান browser-এ যুক্ত হওয়া { #attaching-to-a-running-browser }

একটি চালু করার বদলে একটি [Chrome DevTools Protocol](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp) endpoint-এ ইতিমধ্যে চলমান একটি Chromium-এ যুক্ত হতে `cdp_url` সেট করুন:

⟦CODE4⟧

কোনো লোকাল Chromium binary জড়িত নয়, তাই ইনস্টল ইঙ্গিত আর `auto_install_chromium` প্রযোজ্য নয়। managed-browser provider আর benchmark harness এটিই আশা করে: তারা একটি browser শুরু করে আপনাকে এর endpoint দেয়।

রান তবুও নিজস্ব browser context পায়, তাই `storage_state`, domain allowlist আর private-address block একটি চালু করা browser-এর মতোই প্রযোজ্য, আর এজেন্ট সেই Chrome-এ ইতিমধ্যে খোলা session উত্তরাধিকারসূত্রে পায় না। `cdp_url` আপনার ব্যক্তিগত রোজকার browser-এ নির্দেশ করা তবুও উচ্চ-ঝুঁকির পছন্দ -- সেই process আপনার login করা প্রতিটি অ্যাকাউন্ট ধরে রাখে, আর এজেন্ট এর মধ্য দিয়ে যা পৌঁছাতে পারে তা একটি prompt injection-এ পৌঁছানো যায়। একটি scoped `storage_state`-সহ এজেন্টের জন্য শুরু করা একটি browser পছন্দ করুন। Provider endpoint কখনো URL-এ একটি auth token রাখে; সেগুলোকে secret হিসেবে ধরুন।

## Lifecycle { #lifecycle }

Chromium প্রথম browser-টুল কলে অলসভাবে শুরু হয় আর রান শেষ হলে বন্ধ হয় -- সাফল্য, error বা বাতিলে। কখনো একটি browser টুল না ডাকা রান কোনো Playwright খরচ দেয় না (কোনো subprocess নয়, কোনো window নয়)। প্রতিটি এজেন্ট রান নিজের পেজ আর browser পায়, তাই একসাথে চলা `agent.run()` কল কখনো একটি tab ভাগ করে না।

সেই lifecycle থাকে `PlaywrightBrowserSession`-এ, যা capability প্রতি রানে তৈরি করে। এটি রপ্তানি করা সেই ক্ষেত্রের জন্য যেখানে আপনি চারপাশে একটি এজেন্ট ছাড়াই একই পাহারা দেওয়া browser চান -- allowlist, private-address block, service-worker block, tab ট্র্যাকিং আর dialog সামলানো সবই এর সাথে আসে:

⟦CODE5⟧

`PlaywrightBrowserToolset` একই ভিত্তিতে রপ্তানি করা: capability-র hook ছাড়া আঠারোটি টুল পেতে একে একটি session দিন। নীতি session-এ থাকে আর শুধু সেখানেই, তাই session-এর বসানো পাহারা আর টুলের চালানো যাচাই আলাদা হতে পারে না: এরা একটি সিদ্ধান্তের দুটি স্তর, ভিন্ন মুহূর্তে প্রয়োগ।

## Embedded কনটেন্ট (iframe) { #embedded-content-iframes }

পেজ-স্তরের selector frame-এর সীমায় থামে, তাই একটি embedded schedule, checkout ধাপ বা chat widget একটি CSS selector দিয়ে পৌঁছানো যায় না, আর মূলত একটি embed এমন একটি পেজ প্রায় খালি দেখাতে পারে। capability সেই ফাঁক তিন জায়গায় বন্ধ করে:

- পেজের লেখা ফেরত দেওয়া টুল (`navigate`, `click`, selector ছাড়া `get_text` আর বাকিগুলো) লেখা আছে এমন প্রতিটি child frame-এর লেখা যুক্ত করে, একই token বাজেটের ভেতরে।
- `wait_for` পেজ আর প্রতিটি child frame একসাথে দেখে; প্রথম মিল জেতে।
- `snapshot`-এ frame কনটেন্ট থাকে, আর এর ref যে frame থেকে এসেছে তা বহন করে (`e4`-এর বদলে `f1e4`)। এমন একটি ref `click`, `type_text`, `hover` বা `get_text`-এ দিলে সেই frame-এর ভেতরে মীমাংসা হয় -- embedded কনটেন্টে পৌঁছানোর একমাত্র handle।

child frame জুড়ে ঘোরা সীমিত, তাই একটি সাড়া-না-দেওয়া embed action-এর সময়সীমা শেষ করতে পারে না; অন্য frame যা ফেরত দিয়েছে তা রাখা হয়।

## একটি রান ডিবাগ করা { #debugging-a-run }

তিনটি জিনিস একটি browser এজেন্টকে অনুসরণ করা কঠিন করে: পেজ অদৃশ্য, একটি অনুপস্থিত element একটি ধীরটির মতোই দেখায়, আর আকর্ষণীয় ব্যর্থতা টুল কলের মাঝে ঘটে।

- একটি আসল window-এ রান দেখতে `headless=False` সেট করুন।
- প্রতিটি browser কাজ `browser <action>` নামের একটি OpenTelemetry span খোলে (`browser click`, `browser navigate`), `browser.action`, `browser.timeout_ms`, `browser.outcome` আর ফলের `url.full` বহন করে। সেই কাজের সময় পেজ কী করেছে তা span event হিসেবে যুক্ত: console আউটপুট, অধরা script error, response, egress নীতির প্রত্যাখ্যাত রিকোয়েস্ট, পেজের খোলা dialog আর এর খোলা tab। span রানের নিজস্ব tracer-এ যায়, তাই [Logfire](../logfire.md)-এর জন্য instrument করা একটি এজেন্ট বাকি সবকিছুর সাথে এগুলো জানায়।
- এজেন্ট `console_messages` আর `network_requests` দিয়ে একই log পড়তে পারে, যা প্রায়ই HTML-এর বদলে একটি API থেকে রেন্ডার হওয়া একটি পেজ থেকে উদ্ধারের উপায়। শুধু একটি রিকোয়েস্ট চিহ্নিত করা জিনিস লেখা হয়, কখনো একটি response body নয়। একটি ব্যস্ত পেজ token বাজেটে আঁটার চেয়ে বেশি entry তৈরি করে, আর পুরনোগুলো বাদ পড়ে, তাই কলটি ঘটানো ব্যর্থতা টিকে থাকে; `network_requests(errors_only=True)` এটি আরও সংকীর্ণ করে। লেখা URL এদের host, path আর প্যারামিটারের নাম রাখে কিন্তু `user:password@` credential আর credential-বহনকারী প্যারামিটারের মান (`token`, `code`, `signature` আর বাকিগুলো) হারায়, কারণ সেগুলো মডেল আর telemetry backend দুটোতেই পৌঁছায়।
- আটকে যাওয়া মনে হওয়া একটি অপেক্ষা সাধারণত একটি action timeout। `action_timeout_ms`-এর ডিফল্ট 5s, যাতে ব্যর্থতা দ্রুত আসে; ডিবাগের সময় এটি আরও কমান, আর একটি ধীর পেজ আর একটি ভুল selector আলাদা করতে error string-এর timeout মান পড়ুন।

Logfire-এর ডিফল্ট scrubbing `session`, `auth`, `cookie` আর `credit card`-এর মতো pattern মেলানো মান মুছে দেয়, যা প্রত্যাশার চেয়ে বেশিবার পেজের কনটেন্ট মেলায় -- একটি সম্মেলন সাইট যার প্রতিটি শিরোনামে "session" লেখা, `[Scrubbed due to 'session']` হিসেবে ফেরত আসে, আর একটি দামের পেজ `[Scrubbed due to 'credit card']` হিসেবে। বেছে বেছে scrub করে টুলের ফল পাঠযোগ্য রাখুন:

⟦CODE6⟧

`match.value` ফেরত দিলে মূল লেখা থাকে; `None` ফেরত দিলে মোছা জায়গায় থাকে। callback-কে attribute দেওয়া হয়, এটি তৈরি করা টুল নয়, তাই এটি browser-এর ফলে সীমিত করা যায় না -- মোছা ঘটানো শব্দের ওপর সংকীর্ণ করাই `password`, `api_key` আর `jwt`-কে মোছা রাখে, যে টুলই এগুলো ফেরত দিক।

## সীমাবদ্ধতা { #limitations }

- একটি session সর্বোচ্চ আটটি tab খোলা রাখে; আরও খোলা একটি পেজের বাড়তিগুলো বন্ধ হয়, যা event log-এ লেখা হয়।
- আপলোড আর ডাউনলোড প্রকাশিত নয়: context ডাউনলোড প্রত্যাখ্যান করে, আর একটি পেজে একটি ফাইল দেওয়ার কোনো টুল নেই। দুটোর জন্য পেজ আর host filesystem-এর মাঝে একটি artifact চুক্তি লাগে, ট্র্যাক হচ্ছে [#590](https://github.com/pydantic/pydantic-ai-harness/issues/590)-এ।
- CSS selector iframe-এর ভেতরের কনটেন্টে পৌঁছাতে পারে না; সেখানে পড়া আর কাজ করা `snapshot` ref দিয়ে যায় (দেখুন [Embedded content](#embedded-content-iframes))।
- Durable execution (যেমন `TemporalDurability`) এজেন্ট তৈরির সময় প্রত্যাখ্যাত: একটি জীবন্ত Chromium পেজ activity replay বা worker restart টিকতে পারে না।
- মডেল `aria-ref=` handle (`snapshot` থেকে), CSS selector বা pixel স্থানাঙ্ক দিয়ে element লক্ষ্য করে।

## Egress আর SSRF { #egress-and-ssrf }

ডিফল্টভাবে browser বিশ্বব্যাপী রাউটযোগ্য নয় এমন ঠিকানা প্রত্যাখ্যান করে -- `169.254.169.254` (cloud metadata endpoint), `127.0.0.1`, `::1`, `localhost` আর `*.localhost` নাম, আর RFC 1918 private পরিসর -- কোনো allowlist সেট না থাকলেও। একটি hostname আগে মীমাংসা হয়, তাই একটি নামকে ওই ঠিকানার একটিতে নির্দেশ করলে এটি পার হয় না। এজেন্টকে একটি লোকাল অ্যাপ বা একটি অভ্যন্তরীণ dashboard-এ পৌঁছাতে হলে `block_private_addresses=False` সেট করুন।

`allowed_domains=None`-সহ (ডিফল্ট) এজেন্ট যেকোনো পাবলিক URL-এ পৌঁছাতে পারে। এজেন্ট অবিশ্বস্ত input-এর ওপর কাজ করতে পারলে, `allowed_domains` একটি স্পষ্ট allowlist-এ সেট করুন। প্রতিটি entry এর হুবহু host আর যেকোনো subdomain মেলায় -- `example.com` `api.example.com`-এ পৌঁছায় -- Chromium নিজে যে ASCII রূপ ব্যবহার করে তাতে তুলনা করে, তাই একটি আন্তর্জাতিকীকৃত host আর এর `xn--` বানান একই রায় পায়। একটি wildcard (`*.example.com`) হিসেবে লেখা একটি entry তৈরির সময় exception তোলে: এটি কোনো host-ই মেলাত না, যদিও একটি কনফিগার করা allowlist-এর মতো দেখায়।

allowlist কতদূর পৌঁছায় তা নির্ভর করে রিকোয়েস্ট কিসের জন্য তার ওপর:

| রিকোয়েস্ট | `allowed_domains` দিয়ে সীমিত |
|---|---|
| শীর্ষ-স্তরের navigation | হ্যাঁ |
| `fetch`, XHR, EventSource, WebSocket, `sendBeacon` | হ্যাঁ |
| ছবি, stylesheet, script, font, media | না |
| Sub-frame ডকুমেন্ট | না |

ডেটা রিকোয়েস্ট অন্তর্ভুক্ত, কারণ একটি অনুমোদিত পেজের একটি script অন্যথায় যেকোনো জায়গা থেকে পড়তে, বা যেকোনো জায়গায় পাঠাতে পারত; নিষ্ক্রিয় subresource আর sub-frame ডকুমেন্ট নয়, কারণ যে পেজের asset বাতিল হয় তা একটি ভাঙা পেজ হিসেবে রেন্ডার হয় আর একটি অনুমোদিত সাইটের identity-provider আর payment ধাপ frame-এ থাকে। private-address block সেই ভাগ পুরোপুরি উপেক্ষা করে: এটি প্রতিটি frame আর প্রতিটি resource টাইপে প্রযোজ্য। WebSocket সংযোগ, যা একটি network route কখনো দেখে না, নিজস্ব পাহারা পায়, ওপরের টেবিলের বর্ণিত একই নীতি প্রয়োগ করে।

ইতিমধ্যে একটি ঠিকানা নয় এমন একটি host private-address block-এর শ্রেণিবিভাগের আগে মীমাংসা হয়, তাই একটি অভ্যন্তরীণ ঠিকানায় নির্দেশ করা একটি নাম (`169.254.169.254.nip.io` আর অনুরূপ wildcard DNS সার্ভিস) অনুসরণ না হয়ে প্রত্যাখ্যাত হয়। সেই খোঁজ প্রতিটি ধরনের জন্য চলে, আক্ষরিক যাচাইয়ের সাথে মিলে, তাই একটি বানান রায় ঠিক করে না; উত্তর cache হয়, যা একে প্রতি রিকোয়েস্টের বদলে প্রতি আলাদা host-এ একটি খোঁজ বানায়। `resolved_kinds` সেট করে কোন ধরন খোঁজা হবে।

দুই সেকেন্ডের মধ্যে উত্তর না দেওয়া একটি খোঁজ একটি প্রত্যাখ্যান, অনুমতি নয়: যে একটি নাম নিয়ন্ত্রণ করে সে এর খোঁজ উত্তর দেবে কিনা তা নিয়ন্ত্রণ করে, তাই একটি আটকে যাওয়া অন্যথায় block পার হওয়ার একটি উপায় হতো। ব্যর্থতা সৎ হলে এর খরচ সামান্য, কারণ এই process যে নাম মীমাংসা করতে পারে না তাতে browser-ও ব্যর্থ হতে যাচ্ছে। এর কোনোটিই DNS rebinding-এর বিরুদ্ধে প্রমাণ নয়: Chromium যুক্ত হওয়ার আগে নামটি দ্বিতীয়বার মীমাংসা করে, আর মাঝে বদলানো একটি রেকর্ড এটিকে হারায়। নীতিগুলো স্বাধীন আর প্রত্যাখ্যান জেতে -- একটি allowlist করা private ঠিকানা আপনি `block_private_addresses` থেকে বেরিয়ে না আসা পর্যন্ত তবুও প্রত্যাখ্যাত।

প্রয়োগ দুই স্তরে: একটি network route পাহারা একটি প্রত্যাখ্যাত রিকোয়েস্ট বেরোনোর আগেই বাতিল করে (click, `execute_js` আর ইতিহাস-চলাচল কভার করে, শুধু `navigate` নয়), আর প্রতিটি টুল ফলের URL আবার যাচাই করে `about:blank`-এ ফেরত পাঠায়, যাতে অননুমোদিত কনটেন্ট কখনো মডেলে না পৌঁছায়। browser context-এ service worker আটকানো, যাতে এদের ট্রাফিক route পাহারা এড়িয়ে যেতে না পারে।

/// info | এক নজরে: কোন ঠিকানা ডিফল্টভাবে আটকানো

| ঠিকানা | কেন বিপজ্জনক |
|--------|-------------|
| `169.254.169.254` | cloud metadata — সার্ভারের IAM credential চুরি হতে পারে |
| `127.0.0.1`, `localhost`, `::1` | আপনার মেশিনে চলা admin panel, ডেটাবেস |
| `10.x`, `192.168.x`, `172.16-31.x` | অফিস/বাড়ির অভ্যন্তরীণ নেটওয়ার্ক |
| `x.nip.io`-এর মতো ছদ্মবেশী নাম | আগে মীমাংসা করে আসল ঠিকানা যাচাই হয় |

///

### দুটি ফিল্ড প্রকাশ করতে পারে না এমন নিয়ম { #rules-the-two-fields-cannot-express }

`EgressPolicy` পুরো নীতি, আর `PlaywrightBrowser(policy=...)` `allowed_domains` / `block_private_addresses` সংক্ষিপ্ত রূপের বদলে একটি নেয়। এর ফিল্ড কভার করে একটি denylist (`blocked_domains`, যা সবকিছুর ওপর জেতে আর প্রতিটি রিকোয়েস্ট ধরনে পৌঁছায়), শুধু-মূল-domain মেলানো (`include_subdomains=False`), আর allowlist কোন ধরন সীমিত করে (`allowlist_reach`)।

⟦CODE7⟧

ফিল্ড বর্ণনা করে না এমন একটি সিদ্ধান্তের জন্য, subclass করে `refuse` override করুন। এটি URL, ধরন, Playwright-এর নিজস্ব `resource_type`, method আর রিকোয়েস্টটি main frame-এর নিজস্ব ডকুমেন্ট কিনা তা পায়:

⟦CODE8⟧

`None` ফেরত দিলে রিকোয়েস্ট অনুমোদিত; একটি string ফেরত দিলে এটি প্রত্যাখ্যাত হয় আর সেই string কারণ হিসেবে লেখা হয়, যা মডেল `network_requests` দিয়ে পড়তে পারে। `refuse` যা অনুমোদন করে তা সংকীর্ণ করা একটি override-এর `describe`-ও override করা উচিত: `describe` হলো মডেলকে এর নাগাল সম্পর্কে যা বলা হয়, আর এটি শুধু ফিল্ড পড়ে।

কোনো নীতিই একটি সাধারণ নিরাপত্তার সীমা নয়। Microsoft-এর নিজস্ব playwright-mcp একইভাবে এর origin ছাঁকনির দায় অস্বীকার করে। একটি পেজ তবুও allowlist যে রিকোয়েস্ট ধরন ছেড়ে দেয় তা দিয়ে বাইরে সংকেত পাঠাতে পারে -- একটি ছবি বা script URL পেজ যা-ই এতে রাখে তা বহন করে -- আর একটি hostname এই process যে উত্তর পায় তা দিয়ে শ্রেণিবদ্ধ হয়, যখন Chromium যুক্ত হওয়ার আগে এটি আবার মীমাংসা করে, তাই মাঝে বদলানো একটি রেকর্ড (DNS rebinding) তবুও জেতে। সেটি, আর proxy-ভিত্তিক প্রয়োগ মোড যা এটি বন্ধ করে, ট্র্যাক হচ্ছে [#415](https://github.com/pydantic/pydantic-ai-harness/issues/415)-এ।

অবিশ্বস্ত-input পরিস্থিতির জন্য, browser একটি egress firewall-সহ একটি container বা VM-এ চালান, বা একটি proxy দিয়ে সামনে রাখুন, আর গুরুত্বপূর্ণ কাজের জন্য harness-এর tool-approval hook-এর সাথে জুড়ুন। এগুলোকে স্তরে-স্তরে প্রতিরক্ষা হিসেবে ধরুন, নিশ্চয়তা হিসেবে নয়।

## আরও পড়ুন { #further-reading }

- [Browser automation with Pydantic-AI + Playwright](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/browser-automation-with-pydantic-ai--playwright/4547971) (Microsoft) -- এই capability একটি লাইভ সাইটে একটি হাতে-করা QA চালাচ্ছে, Microsoft Foundry মডেলের সাথে যুক্ত, রানের OpenTelemetry trace-সহ।
- [Browser Use](browser-use.md) -- অন্য browser capability। প্রতিটি নিজের browser চালায়, তাই একটি এজেন্টকে একটি বা অন্যটি দিন।
- [Playwright for Python](https://playwright.dev/python/) -- নিচের automation লাইব্রেরি, আর selector syntax-এর রেফারেন্স।
- [Capabilities](../capabilities/overview.md)

## API রেফারেন্স { #api-reference }

⟦CODE9⟧

/// check | সংক্ষেপে মনে রাখুন

* `PlaywrightBrowser()` আঠারোটি টুল দেয়; প্রথমে `playwright install chromium`।
* `snapshot` দিয়ে `aria-ref` handle নিয়ে click/type — CSS selector-এর চেয়ে নির্ভরযোগ্য।
* `action_timeout_ms` (5s) আর `navigation_timeout_ms` (60s) আলাদা; প্রতি কলে `timeout_ms` override।
* login-করা সাইটে `storage_state` — একে credential হিসেবে ধরুন।
* private ঠিকানা ডিফল্টভাবে আটকানো; অবিশ্বস্ত কাজে `allowed_domains` আর container/proxy।
* durable execution সমর্থিত নয়।

///
