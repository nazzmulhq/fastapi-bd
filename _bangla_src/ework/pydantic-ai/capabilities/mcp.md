
# MCP Capability { #mcp-capability }

/// note | এই পেজে যা শিখবেন

* `MCP` capability দিয়ে যেকোনো MCP সার্ভারের টুল এজেন্টে যুক্ত করা — ডিফল্টভাবে লোকালে, ঐচ্ছিকভাবে provider-নেটিভ।
* `id` কীভাবে তৈরি হয় আর কেন একই host-এর দুটি সার্ভারে স্পষ্ট `id` লাগে।
* প্রতি-ব্যবহারকারী credential (প্রতিটি রানে নিজের token)।

///

[`MCP`][pydantic_ai.capabilities.MCP] হলো একটি [provider-অনুযায়ী capability](overview.md#provider-adaptive-tools) আর Pydantic AI-তে [MCP](../mcp/overview.md)-এর প্রধান প্রবেশপথ। এটি ডিফল্টভাবে MCP সার্ভার লোকালে চালায় — credential, hook আর tracing আপনার নিয়ন্ত্রণে রেখে — আর URL-ভিত্তিক সার্ভার আর সরাসরি client / toolset / transport input দুটোই সমর্থন করে।

নেটিভ দিকে এর পেছনে আছে [`MCPServerTool`][pydantic_ai.native_tools.MCPServerTool] (provider সমর্থন আর কনফিগারেশনের জন্য দেখুন [MCP Server Tool](../native-tools.md#mcp-server-tool)) — পূর্ণ নিয়ন্ত্রণ দরকার হলে সরাসরি `native=MCPServerTool(...)` দিন (যেমন capability যা তৈরি করত তার চেয়ে ভিন্ন একটি `id`, `authorization_token` বা `description`)। লোকাল দিকে, `local=` যেকোনো [`MCPToolset`][pydantic_ai.mcp.MCPToolset] input নেয় (URL, `fastmcp.Client`, transport, in-process `FastMCP` সার্ভার, script path, …) — toolset নয় এমন input নিজে থেকে `MCPToolset`-এ মোড়ানো হয়।

/// tip | উদাহরণ দিয়ে বুঝি

MCP (Model Context Protocol) হলো AI টুলের জন্য একটি "USB পোর্ট" — যেকোনো MCP সার্ভার (GitHub, ডেটাবেস, ফাইল সিস্টেম) একই নিয়মে এজেন্টে লাগানো যায়। `MCP('https://mcp.example.com/mcp')` লিখলেই সেই সার্ভারের সব টুল এজেন্ট পেয়ে যায়। ডিফল্টভাবে সংযোগ আপনার সার্ভার থেকে হয় (লোকাল), তাই credential আপনার কাছেই থাকে।

///

একটি স্পষ্ট `id=` ছাড়া, capability সার্ভার URL-এর hostname-কে এর [`id`][pydantic_ai.capabilities.AbstractCapability.id] হিসেবে ব্যবহার করে, যা এর লোকাল toolset আর [durable](../durable_execution/overview.md) operation-এরও নাম দেয়। শুধু hostname ব্যবহৃত হয়, কারণ একটি URL-এর path বা query একটি credential বহন করতে পারে। একই host-এর সার্ভারের জন্য দুটি `MCP` capability একই `id` পেত, তাই এজেন্ট এদের প্রত্যাখ্যান করে আর প্রতিটিতে একটি স্পষ্ট `id=` চায়।

⟦CODE1⟧

## প্রতি-ব্যবহারকারী credential { #per-user-credentials }

একটি অ্যাপে যেখানে প্রতিটি ব্যবহারকারীর MCP সার্ভারের জন্য নিজস্ব credential আছে, একটি এজেন্ট সবাইকে পরিবেশন করে, তাই capability তৈরির সময় `authorization_token` আর `headers` স্থির করা যায় না। এর বদলে একটি ফাংশন দিন: প্রতিটি রানের শুরুতে এটি [run context][pydantic_ai.tools.RunContext] দিয়ে ডাকা হয়, তাই এটি রানের [dependencies](../dependencies.md) থেকে বর্তমান ব্যবহারকারীর token পড়তে পারে:

⟦CODE2⟧

_(এই উদাহরণ চালাতে, নিশ্চিত করুন `asyncio` import করা আছে আর `asyncio.run(main())` যোগ করুন; আর কোনো পরিবর্তন লাগবে না।)_

ফাংশনের ফেরত মান সেই রানের জন্য দুই দিকেই ব্যবহৃত হয়: নেটিভ [`MCPServerTool`][pydantic_ai.native_tools.MCPServerTool] এটি দিয়ে তৈরি হয়, আর লোকাল toolset নিজস্ব একটি MCP session-এ যুক্ত হয়, তাই একসাথে চলা রান কখনো ব্যবহারকারীদের মধ্যে একটি session ভাগ করে না। `None` ফেরত দিলে কোনো `Authorization` header পাঠানো হয় না। `headers` একইভাবে একটি ফাংশন নেয়। প্রতিটি ব্যবহারকারীর কেন নিজস্ব একটি session লাগে তা দেখুন [per-user authentication](../mcp/client.md#per-user-authentication)-এ।

/// warning | সাধারণ ভুল

একটি multi-user অ্যাপে `MCP(url, authorization_token=os.environ['GITHUB_TOKEN'])` লেখা। এতে সব ব্যবহারকারী একই (আপনার!) token দিয়ে GitHub-এ কাজ করবে — একজন ব্যবহারকারী আরেকজনের private repo দেখতে পারে। প্রতি-ব্যবহারকারী token-এর জন্য ওপরের উদাহরণের মতো `RunContext` নেওয়া একটি ফাংশন দিন (`authorization_token=mcp_token`), যা `ctx.deps` থেকে বর্তমান ব্যবহারকারীর token পড়ে।

///

নিচু-স্তরের প্রবেশের জন্য — [`MCPToolset`][pydantic_ai.mcp.MCPToolset]-এর lifecycle সরাসরি পরিচালনা, উন্নত transport / client কনফিগারেশন, বা একটি capability দিয়ে না গিয়ে MCP সার্ভার ব্যবহার — দেখুন [MCP ডকুমেন্টেশন](../mcp/overview.md)।

/// check | সংক্ষেপে মনে রাখুন

* `MCP(url)` — যেকোনো MCP সার্ভারের টুল; ডিফল্টভাবে লোকাল, `native=True` দিয়ে provider-নেটিভ।
* `local=` যেকোনো `MCPToolset` input নেয় (URL, `fastmcp.Client`, transport, script...)।
* `id` ডিফল্টভাবে hostname; একই host-এ দুটি সার্ভার থাকলে প্রতিটিতে স্পষ্ট `id=`।
* প্রতি-ব্যবহারকারী credential: `authorization_token`/`headers`-এ `RunContext` নেওয়া একটি ফাংশন — প্রতিটি রানে নিজস্ব session।

///
