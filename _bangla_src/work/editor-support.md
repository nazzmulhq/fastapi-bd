# এডিটর সাপোর্ট { #editor-support }

অফিসিয়াল [FastAPI এক্সটেনশন](https://marketplace.visualstudio.com/items?itemName=FastAPILabs.fastapi-vscode) *পাথ অপারেশন* খুঁজে বের করা, নেভিগেশন, এবং সাথে FastAPI Cloud ডিপ্লয়মেন্ট ও লাইভ লগ স্ট্রিমিং দিয়ে আপনার FastAPI ডেভেলপমেন্ট ওয়ার্কফ্লো উন্নত করে।

এক্সটেনশনটি সম্পর্কে আরও বিস্তারিত জানতে [GitHub রিপোজিটরিতে](https://github.com/fastapi/fastapi-vscode) README দেখুন।

## সেটআপ ও ইনস্টলেশন { #setup-and-installation }

**FastAPI এক্সটেনশন** [VS Code](https://code.visualstudio.com/) ও [Cursor](https://www.cursor.com/) দুটোর জন্যই পাওয়া যায়। প্রতিটি এডিটরের Extensions প্যানেলে "FastAPI" লিখে খুঁজে **FastAPI Labs**-এর প্রকাশিত এক্সটেনশনটি বেছে নিয়ে সরাসরি এটি ইনস্টল করা যায়। এক্সটেনশনটি [vscode.dev](https://vscode.dev) ও [github.dev](https://github.dev)-এর মতো ব্রাউজার-ভিত্তিক এডিটরেও কাজ করে।

### অ্যাপ্লিকেশন খুঁজে বের করা { #application-discovery }

ডিফল্টভাবে এক্সটেনশনটি `FastAPI()` ইনস্ট্যান্সিয়েট করে এমন ফাইল স্ক্যান করে স্বয়ংক্রিয়ভাবে আপনার ওয়ার্কস্পেসে FastAPI অ্যাপ্লিকেশন খুঁজে বের করবে। আপনার প্রজেক্টের কাঠামোর জন্য স্বয়ংক্রিয় শনাক্তকরণ কাজ না করলে, আপনি `pyproject.toml`-এ `[tool.fastapi]` দিয়ে, অথবা মডিউল নোটেশন (যেমন `myapp.main:app`) ব্যবহার করে `fastapi.entryPoint` VS Code সেটিং দিয়ে একটি entrypoint উল্লেখ করতে পারেন।

## ফিচারসমূহ { #features }

- **Path Operation Explorer** - আপনার অ্যাপ্লিকেশনের সব <dfn title="রাউট, এন্ডপয়েন্ট">*পাথ অপারেশনের*</dfn> একটি সাইডবার ট্রি ভিউ। যেকোনো রাউট বা রাউটার সংজ্ঞায় যেতে ক্লিক করুন।
- **Route Search** - <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>E</kbd> (macOS-এ: <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>E</kbd>) দিয়ে পাথ, মেথড বা নাম ধরে খুঁজুন।
- **CodeLens Navigation** - টেস্ট ক্লায়েন্ট কলের (যেমন `client.get('/items')`) ওপরে ক্লিকযোগ্য লিংক, যা মিলে যাওয়া *পাথ অপারেশনে* নিয়ে যায়, ফলে টেস্ট ও বাস্তবায়নের মধ্যে দ্রুত যাতায়াত করা যায়।
- **Deploy to FastAPI Cloud** - এক ক্লিকে আপনার অ্যাপ [FastAPI Cloud](https://fastapicloud.com/)-এ ডিপ্লয়।
- **Stream Application Logs** - লেভেল ফিল্টারিং ও টেক্সট সার্চসহ আপনার FastAPI Cloud-এ ডিপ্লয় করা অ্যাপ্লিকেশন থেকে রিয়েল-টাইম লগ স্ট্রিমিং।

আপনি যদি এক্সটেনশনের ফিচারগুলোর সাথে পরিচিত হতে চান, তাহলে Command Palette খুলে (<kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> বা macOS-এ: <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd>) "Welcome: Open walkthrough..." বেছে নিয়ে তারপর "Get started with FastAPI" walkthrough বেছে নিয়ে এক্সটেনশনের walkthrough দেখতে পারেন।
