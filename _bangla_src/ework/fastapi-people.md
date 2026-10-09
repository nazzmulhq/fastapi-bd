---
include_yaml:
  github_sponsors: data/github_sponsors.yml
  people: data/people.yml
  contributors: data/contributors.yml
  translation_reviewers: data/translation_reviewers.yml
  skip_users: data/skip_users.yml
  members: data/members.yml
  sponsors_badge: data/sponsors_badge.yml
  sponsors: data/sponsors.yml
---

# FastAPI-এর মানুষেরা { #fastapi-people }

/// note | এই পেজটি কী

FastAPI শুধু একটি কোড নয়, এর পেছনে আছেন অনেক মানুষ: নির্মাতা, দলের সদস্য, প্রশ্নের উত্তর দেওয়া বিশেষজ্ঞ, কোড আর অনুবাদে অবদান রাখা স্বেচ্ছাসেবী, আর অর্থ দিয়ে সাহায্য করা স্পনসর। এই পেজ তাদের সম্মান জানায়। নিচের নাম আর ছবিগুলো GitHub থেকে স্বয়ংক্রিয়ভাবে আসে।

///

FastAPI-এর একটি অসাধারণ কমিউনিটি আছে, যা সব ধরনের পটভূমির মানুষকে স্বাগত জানায়।

## নির্মাতা { #creator }

হ্যালো! 👋

এই হলাম আমি:

<div class="user-list user-list-center">
{% for user in people.maintainers %}

<div class="user"><a href="{{ contributors.tiangolo.url }}"><div class="avatar-wrapper"><img src="{{ contributors.tiangolo.avatarUrl }}"/></div><div class="title">@{{ contributors.tiangolo.login }}</div></a> <div class="count">উত্তর: {{ user.answers }}</div><div class="count">Pull Request: {{ contributors.tiangolo.count }}</div></div>
{% endfor %}

</div>

আমি **FastAPI**-এর নির্মাতা। এ সম্পর্কে আরও পড়তে পারেন [সাহায্য - লেখককে ফলো করুন](help-fastapi.md#follow-the-author)-এ।

## দল { #team }

এটি দলের বর্তমান সদস্যদের তালিকা। 😎

তাদের সম্পৃক্ততা আর অনুমতির স্তর ভিন্ন ভিন্ন, তারা [রিপোজিটরি ব্যবস্থাপনার কাজ](https://tiangolo.com/open-source/management-tasks/) করতে পারেন, আর আমরা একসাথে [FastAPI রিপোজিটরি পরিচালনা করি](./management.md)।

<div class="user-list user-list-center">

{% for user in members["members"] %}

<div class="user"><a href="{{ user.url }}"><div class="avatar-wrapper"><img src="{{ user.avatar_url }}"/></div><div class="title">@{{ user.login }}</div></a></div>

{% endfor %}

</div>

## FastAPI বিশেষজ্ঞ { #fastapi-experts }

দীর্ঘ সময় ধরে, GitHub Discussions-এ কমিউনিটির প্রশ্নের উত্তর দিতেন কমিউনিটির অন্যান্য স্বেচ্ছাসেবীরা।

অনেককে সাহায্য করে তারা প্রমাণ করেছেন যে তারা **FastAPI বিশেষজ্ঞ**। ✨

এই হলো প্রথম দিকের FastAPI বিশেষজ্ঞদের সম্মাননা তালিকা:

<div class="user-list user-list-center">

{% for user in people.experts[:30] %}

{% if user.login not in skip_users.users %}

<div class="user"><a href="{{ user.url }}"><div class="avatar-wrapper"><img src="{{ user.avatarUrl }}"/></div><div class="title">@{{ user.login }}</div></a> <div class="count">উত্তর দেওয়া প্রশ্ন: {{ user.count }}</div></div>

{% endif %}

{% endfor %}

</div>

## শীর্ষ অবদানকারী { #top-contributors }

বর্তমানে FastAPI-এর বেশিরভাগ কোড পরিবর্তন দলই করে।

তবে বছরের পর বছর ধরে অন্যরাও অনেক অবদান রেখেছেন।

তারা সোর্স কোড, ডকুমেন্টেশন ইত্যাদিতে অবদান রেখেছেন। 📦

এই হলো প্রথম দিকের **শীর্ষ অবদানকারীদের** সম্মাননা তালিকা। 👷

<div class="user-list user-list-center">

{% for user in (contributors.values() | list)[:30] %}

{% if user.login not in skip_users.users %}

<div class="user"><a href="{{ user.url }}"><div class="avatar-wrapper"><img src="{{ user.avatarUrl }}"/></div><div class="title">@{{ user.login }}</div></a> <div class="count">Pull Request: {{ user.count }}</div></div>

{% endif %}

{% endfor %}

</div>

আরও শত শত অবদানকারী আছেন, তাদের সবাইকে দেখতে পারেন [FastAPI GitHub Contributors পেজে](https://github.com/fastapi/fastapi/graphs/contributors)। 👷

## শীর্ষ অনুবাদ রিভিউয়ার { #top-translation-reviewers }

বর্তমানে অনুবাদ করা হয় AI টুল দিয়ে, যা পরিচালনা করেন FastAPI দল আর মাতৃভাষীরা।

একসময় FastAPI-এর কিছু ডকুমেন্টেশন পেজ কমিউনিটির সদস্যরা হাতে অন্য ভাষায় অনুবাদ করেছিলেন।

এই হলো প্রথম দিকের **শীর্ষ অনুবাদ রিভিউয়ারদের** সম্মাননা তালিকা। 🕵️

<div class="user-list user-list-center">
{% for user in (translation_reviewers.values() | list)[:30] %}

{% if user.login not in skip_users.users %}

<div class="user"><a href="{{ user.url }}"><div class="avatar-wrapper"><img src="{{ user.avatarUrl }}"/></div><div class="title">@{{ user.login }}</div></a> <div class="count">রিভিউ: {{ user.count }}</div></div>

{% endif %}

{% endfor %}

</div>

## স্পনসর { #sponsors }

**স্পনসররা** **FastAPI** আর সহযোগী প্রজেক্টগুলোকে সমর্থন করেন, মূলত [GitHub Sponsors](https://github.com/sponsors/tiangolo)-এর মাধ্যমে। ✨

{% if sponsors %}

{% if sponsors.gold %}

### গোল্ড স্পনসর { #gold-sponsors }

{% for sponsor in sponsors.gold -%}
<a href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}" style="border-radius:15px"></a>
{% endfor %}
{% endif %}

{% if sponsors.silver %}

### সিলভার স্পনসর { #silver-sponsors }

{% for sponsor in sponsors.silver -%}
<a href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}" style="border-radius:15px"></a>
{% endfor %}
{% endif %}

{% if sponsors.bronze %}

### ব্রোঞ্জ স্পনসর { #bronze-sponsors }

{% for sponsor in sponsors.bronze -%}
<a href="{{ sponsor.url }}" title="{{ sponsor.title }}"><img src="{{ sponsor.img }}" style="border-radius:15px"></a>
{% endfor %}
{% endif %}

{% endif %}

### ব্যক্তিগত স্পনসর { #individual-sponsors }

{% if github_sponsors %}
{% for group in github_sponsors.sponsors %}

<div class="user-list user-list-center">

{% for user in group %}
{% if user.login not in sponsors_badge.logins %}

<div class="user"><a href="{{ user.url }}"><div class="avatar-wrapper"><img src="{{ user.avatarUrl }}"/></div><div class="title">@{{ user.login }}</div></a></div>

{% endif %}
{% endfor %}

</div>

{% endfor %}
{% endif %}

## তথ্য সম্পর্কে - কারিগরি বিবরণ { #about-the-data-technical-details }

এই পেজের মূল উদ্দেশ্য ছিল অন্যদের সাহায্যে কমিউনিটির পরিশ্রম তুলে ধরা, বিশেষ করে এমন পরিশ্রম যা সাধারণত কম চোখে পড়ে আর অনেক ক্ষেত্রে বেশি কষ্টসাধ্য, যেমন অন্যদের প্রশ্নে সাহায্য করা আর অনুবাদসহ Pull Request রিভিউ করা।

এটি স্পনসরদের অবদানও তুলে ধরে।

আগে এই তথ্য প্রতি মাসে নিয়মিত হিসাব করা হতো।

জুলাই ২০২৬ পর্যন্ত, বেশ কিছুদিন ধরে বেশিরভাগ কাজ করছেন দলের (বেতনভুক্ত) সদস্যরা।

GitHub Discussions-এর উত্তর মূলত দলের সদস্যরাই দেন।

বেশিরভাগ কোড পরিবর্তনও দলের সদস্যরাই করেন।

আর পুরো ডকুমেন্টেশনের অনুবাদ একাধিক ভাষায় নিয়মিত করা হয় AI টুল দিয়ে, যা দলের সদস্যরা পরিচালনা করেন।

তা ছাড়া, সাম্প্রতিক মাসগুলোতে বিপুল পরিমাণ AI স্প্যাম এসেছে, মূলত FastAPI বিশেষজ্ঞ ব্যবস্থাকে ফাঁকি দিতে বা যেকোনোভাবে একটি PR মার্জ করিয়ে অবদানকারী হিসেবে গণ্য হতে। এ বিষয়ে দৃষ্টিভঙ্গি নিয়ে আরও পড়তে পারেন [Automated Code and AI](https://tiangolo.com/open-source/contributing/#automated-code-and-ai)-এ।

এই কারণে FastAPI বিশেষজ্ঞ, শীর্ষ অবদানকারী আর শীর্ষ অনুবাদ রিভিউয়ারদের তথ্য আর নিয়মিত আপডেট করা হয় না।

FastAPI-কে আজকের অবস্থানে আনতে যে মানুষেরা সাহায্য করেছেন, তাদের প্রতি শ্রদ্ধা হিসেবে এই অংশটি বর্তমানে রাখা হয়েছে। 🙌
