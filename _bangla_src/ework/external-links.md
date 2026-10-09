---
include_yaml:
  topic_repos: data/topic_repos.yml
---

# বাইরের লিংক { #external-links }

**FastAPI**-এর একটি দারুণ কমিউনিটি আছে যা ক্রমাগত বাড়ছে।

**FastAPI** সম্পর্কিত অনেক পোস্ট, আর্টিকেল, টুল আর প্রজেক্ট আছে।

FastAPI সম্পর্কিত অনেক রিসোর্স খুঁজে পেতে আপনি সহজেই একটি সার্চ ইঞ্জিন বা ভিডিও প্ল্যাটফর্ম ব্যবহার করতে পারেন।

/// note | নোট

আগে এই পেজে বাইরের আর্টিকেলের লিংকের তালিকা থাকত।

কিন্তু এখন যেহেতু FastAPI সব ভাষা মিলিয়ে GitHub-এ সবচেয়ে বেশি স্টার পাওয়া ব্যাকএন্ড ফ্রেমওয়ার্ক, আর Python-এ সবচেয়ে বেশি স্টার পাওয়া ও ব্যবহৃত ফ্রেমওয়ার্ক, তাই এ নিয়ে লেখা সব আর্টিকেলের তালিকা করার চেষ্টা আর অর্থবহ নয়।

///

/// tip | কীভাবে খুঁজবেন

YouTube বা গুগলে "FastAPI tutorial bangla" বা "FastAPI crash course" লিখে খুঁজলে অনেক ভিডিও আর লেখা পাবেন। নিচের তালিকাটি কাজের উদাহরণ খোঁজার জন্য দারুণ: অন্যরা FastAPI দিয়ে আসল প্রজেক্ট কীভাবে সাজিয়েছে তা দেখে অনেক কিছু শেখা যায়।

///

## GitHub রিপোজিটরি { #github-repositories }

[`fastapi` টপিকসহ GitHub রিপোজিটরিগুলোর](https://github.com/topics/fastapi) মধ্যে সবচেয়ে বেশি স্টার পাওয়াগুলো:

{% for repo in topic_repos.repos %}

<a href={{repo.html_url}} target="_blank">★ {{repo.stars}} - {{repo.name}}</a> by <a href={{repo.owner_html_url}} target="_blank">@{{repo.owner_login}}</a>.

{% endfor %}
