# ইভেন্ট টেস্টিং: lifespan এবং startup - shutdown { #testing-events-lifespan-and-startup-shutdown }

আপনার টেস্টে `lifespan` চালানোর দরকার হলে আপনি একটি `with` স্টেটমেন্টসহ `TestClient` ব্যবহার করতে পারেন:

{* ../../docs_src/app_testing/tutorial004_py310.py hl[9:15,18,27:28,30:32,41:43] *}


আরও বিস্তারিত পড়তে পারেন ["অফিসিয়াল Starlette ডকুমেন্টেশন সাইটে টেস্টে lifespan চালানো" সম্পর্কে](https://starlette.dev/lifespan/#running-lifespan-in-tests)।

ডেপ্রিকেটেড `startup` ও `shutdown` ইভেন্টের জন্য আপনি `TestClient` এভাবে ব্যবহার করতে পারেন:

{* ../../docs_src/app_testing/tutorial003_py310.py hl[9:12,20:24] *}
