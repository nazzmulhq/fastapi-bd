# সহজ বাংলা সংস্করণের লেখার নিয়ম (internal style guide)

Goal: a reader with basic Bangla and little programming background can understand every page.
This is NOT a line-by-line translation. Explain, simplify, add examples.

## Language
- Short sentences. Formal-friendly "আপনি". Everyday words over Sanskritised ones
  (e.g. "ব্যবহার করুন" not "প্রয়োগ করুন"; "দরকার" not "আবশ্যক" where natural).
- Technical terms: keep the common transliteration from llm-prompt.md (রিকোয়েস্ট, রেসপন্স,
  পাথ অপারেশন, ডিপেন্ডেন্সি...). On FIRST use in a page explain it in plain words, and give the
  English word in parentheses when the reader will need it for searching, e.g.
  "রিকোয়েস্ট (request) মানে ক্লায়েন্ট সার্ভারের কাছে যে অনুরোধ পাঠায়"।
- Product/library names, code, file names, commands stay in English.

## Page structure (use admonitions, keep official design)
1. After the H1 (and the banner the build adds): `/// note | এই পেজে যা শিখবেন` with 3-6 bullets.
2. Original sections in the same order with the SAME heading anchors `{ #... }`.
   Rewrite each section in easy Bangla, adding background the English text assumes.
3. After important code (`{* ... *}` includes or fenced code): `/// info | কোডটি সহজ ভাষায়`
   — walk through the lines/parts that matter, what each does and why.
4. Where an idea is abstract: `/// tip | উদাহরণ দিয়ে বুঝি` with a real-life analogy.
5. Pitfalls: `/// warning | সাধারণ ভুল` (only when genuinely useful).
6. End of page: `/// check | সংক্ষেপে মনে রাখুন` with key takeaways (bullets).
   Keep the original "Recap"/"সংক্ষেপে" section if the English has one.
- Avoid adding new `#` headings; if needed give an explicit ASCII anchor `{ #bn-... }`.
- Original admonitions keep their type; titles in Bangla (note→নোট, tip→পরামর্শ, info→তথ্য,
  warning→সতর্কতা, danger→বিপদ, check→যাচাই, "Technical Details"→কারিগরি বিবরণ).

## Must preserve (checked by tools/efinish.py)
- every heading anchor from English, every `{* ... *}` include, every code block,
  every link URL and image, tab blocks `//// tab | ...`, balanced `///` blocks.
