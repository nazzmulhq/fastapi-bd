# Build docs/release-notes.md: Bangla reading guide + translated section headings, English entries kept as-is.
import os,sys,re
sys.path.insert(0,os.path.dirname(__file__))
from common import *
en=open(os.path.join(EN,'release-notes.md'),encoding='utf8').read()
INTRO='''# রিলিজ নোট { #release-notes }

/// note | এই পেজটি কীভাবে পড়বেন

**রিলিজ নোট** হলো FastAPI-এর প্রতিটি নতুন সংস্করণে কী কী বদলেছে তার ধারাবাহিক তালিকা। সবচেয়ে নতুন সংস্করণ সবার ওপরে, পুরনোগুলো নিচে।

প্রতিটি এন্ট্রি GitHub-এর একটি Pull Request (PR) থেকে স্বয়ংক্রিয়ভাবে তৈরি হয়, তাই **এন্ট্রিগুলো মূল ইংরেজিতেই রাখা হয়েছে**। এগুলো কারিগরি লগ, হুবহু রাখলে GitHub-এ খুঁজে পাওয়া সহজ। নিচের নির্দেশিকা দিয়ে আপনি সহজেই বুঝতে পারবেন কোন এন্ট্রি কী নিয়ে।

///

/// info | সংস্করণ নম্বর কীভাবে পড়বেন

যেমন `0.143.0`: মাঝের সংখ্যা (MINOR) বাড়লে নতুন ফিচার আসে আর পুরনো কোড ভাঙতেও পারে। শেষের সংখ্যা (PATCH) বাড়লে সাধারণত শুধু বাগ ঠিক হয়। বিস্তারিত দেখুন [FastAPI সংস্করণ সম্পর্কে](deployment/versions.md) পেজে।

আপগ্রেডের আগে আপনার বর্তমান সংস্করণ থেকে নতুন সংস্করণ পর্যন্ত সব এন্ট্রিতে **💥 Breaking Changes** অংশ আছে কিনা অবশ্যই দেখে নিন।

///

/// tip | অংশের শিরোনামগুলোর অর্থ

| শিরোনাম | অর্থ |
| --- | --- |
| Breaking Changes | এমন পরিবর্তন যা আপনার বিদ্যমান কোড ভেঙে দিতে পারে, আপগ্রেডের আগে অবশ্যই পড়ুন |
| Features | নতুন ফিচার |
| Fixes | বাগ ঠিক করা |
| Security fixes | নিরাপত্তা ত্রুটি ঠিক করা, দ্রুত আপগ্রেড করুন |
| Refactors | ভেতরের কোড সাজানো, ব্যবহারকারীর জন্য আচরণ একই |
| Upgrades | ডিপেন্ডেন্সির (যেমন Starlette, Pydantic) সংস্করণ বদল |
| Docs | ডকুমেন্টেশনের পরিবর্তন |
| Translations | অনুবাদের পরিবর্তন |
| Internal | প্রজেক্টের ভেতরের কাজ (টেস্ট, CI, টুল), সাধারণ ব্যবহারকারীর জন্য প্রভাব নেই |

///

/// tip | ইমোজির অর্থ

✨ নতুন ফিচার · 🐛 বাগ ফিক্স · 💥 ভেঙে দেওয়ার মতো পরিবর্তন · 🔒️ নিরাপত্তা · ♻️ রিফ্যাক্টর · ⬆️ ডিপেন্ডেন্সি আপগ্রেড · ⬇️ ডাউনগ্রেড · 📝 ডকুমেন্টেশন · 🌐 অনুবাদ · ✅ টেস্ট · 👷 CI · 🔧 কনফিগারেশন · 🔥 কোড/ফাইল মুছে ফেলা · 🎨 ফরম্যাটিং · ⚡️ পারফরম্যান্স · 🏷️ টাইপ অ্যানোটেশন · 🗑️ deprecated ঘোষণা · ➕ ডিপেন্ডেন্সি যোগ · ➖ ডিপেন্ডেন্সি বাদ · 🔖 নতুন রিলিজ

///
'''
H={'## Latest Changes':'## সর্বশেষ পরিবর্তন { #latest-changes }',
'### Internal':'### অভ্যন্তরীণ (Internal)','### Docs':'### ডকুমেন্টেশন (Docs)','### Translations':'### অনুবাদ (Translations)',
'### Fixes':'### ফিক্স (Fixes)','### Features':'### ফিচার (Features)','### Refactors':'### রিফ্যাক্টর (Refactors)',
'### Upgrades':'### আপগ্রেড (Upgrades)','### Breaking Changes':'### ভেঙে দেওয়ার মতো পরিবর্তন (Breaking Changes)',
'### Security fixes':'### নিরাপত্তা ফিক্স (Security fixes)','### Highlights':'### প্রধান দিক (Highlights)'}
fm,body=re.match(r'(---\n.*?\n---\n)(.*)',en,re.S).groups()
body=body.replace('# Release Notes\n',INTRO,1)
body='\n'.join(H.get(l,l) for l in body.split('\n'))
out=fm+body
open(os.path.join(BN,'release-notes.md'),'w',encoding='utf8').write(out)
# sanity: all non-heading lines preserved
el=[l for l in en.split('\n') if not l.startswith('#')]; bl=set(out.split('\n'))
miss=[l for l in el if l not in bl]
print('written',len(out),'missing non-heading lines:',len(miss))
