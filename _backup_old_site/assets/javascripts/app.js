/**
 * FastAPI Bangla Documentation - Unified Frontend Engine
 * Provides dark mode switching, code tabs, search modal, copy-to-clipboard,
 * TOC scrollspy, and mobile drawer functionality.
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemePalette();
  initCodeTabs();
  initCodeCopyButtons();
  initSearch();
  initScrollspy();
  initMobileDrawer();
  initTermynal();
  initAnnouncements();
});

// --- Announcements & Sponsor Banner Rotator ---
function initAnnouncements() {
  const announceLeft = document.getElementById('announce-left');
  if (announceLeft) {
    const items = Array.from(announceLeft.querySelectorAll('div.item'));
    if (items.length > 0) {
      let idx = 0;
      const rotate = () => {
        items.forEach((el, i) => { el.style.display = (i === idx ? 'block' : 'none'); });
        idx = (idx + 1) % items.length;
      };
      rotate();
      setInterval(rotate, 5000);
    }
  }

  const announceRight = document.getElementById('announce-right');
  if (announceRight) {
    announceRight.style.display = 'block';
    const items = Array.from(announceRight.querySelectorAll('div.item'));
    if (items.length > 0) {
      let idx = 0;
      const rotate = () => {
        items.forEach((el, i) => { el.style.display = (i === idx ? 'block' : 'none'); });
        idx = (idx + 1) % items.length;
      };
      rotate();
      setInterval(rotate, 7000);
    }
  }
}

// --- 1. Theme Palette (Light / Dark / System) ---
function initThemePalette() {
  const currentScheme = localStorage.getItem('fastapi-theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'slate' : 'default');
  
  applyTheme(currentScheme);

  // Bind to palette radio buttons
  const paletteRadios = document.querySelectorAll('input[name="__palette"]');
  paletteRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
      const scheme = radio.getAttribute('data-md-color-scheme');
      if (scheme) {
        applyTheme(scheme);
        localStorage.setItem('fastapi-theme', scheme);
      }
    });
  });

  // Toggle button click helper
  const paletteLabels = document.querySelectorAll('.md-header__option[data-md-component="palette"] label');
  paletteLabels.forEach(label => {
    label.addEventListener('click', (e) => {
      const current = document.body.getAttribute('data-md-color-scheme');
      const nextScheme = current === 'slate' ? 'default' : 'slate';
      applyTheme(nextScheme);
      localStorage.setItem('fastapi-theme', nextScheme);
    });
  });
}

function applyTheme(scheme) {
  document.body.setAttribute('data-md-color-scheme', scheme);
  document.body.setAttribute('data-md-color-primary', 'teal');
  document.body.setAttribute('data-md-color-accent', 'amber');
  
  const lightLabel = document.querySelector('label[title="Switch to dark mode"]');
  const darkLabel = document.querySelector('label[title="Switch to light mode"]');
  
  if (lightLabel && darkLabel) {
    if (scheme === 'slate') {
      lightLabel.hidden = true;
      darkLabel.hidden = false;
    } else {
      lightLabel.hidden = false;
      darkLabel.hidden = true;
    }
  }
}

// --- 2. Code Tabs Synchronization ---
function initCodeTabs() {
  const tabContainers = document.querySelectorAll('.tabbed-set');
  
  tabContainers.forEach(container => {
    const labels = container.querySelectorAll('.tabbed-labels label');
    const blocks = container.querySelectorAll('.tabbed-content > .tabbed-block');
    
    labels.forEach((label, idx) => {
      label.addEventListener('click', () => {
        const tabText = label.innerText.trim();
        syncAllTabs(tabText);
      });
    });
  });
}

function syncAllTabs(tabName) {
  const tabContainers = document.querySelectorAll('.tabbed-set');
  tabContainers.forEach(container => {
    const labels = container.querySelectorAll('.tabbed-labels label');
    const blocks = container.querySelectorAll('.tabbed-content > .tabbed-block');
    
    labels.forEach((label, idx) => {
      if (label.innerText.trim() === tabName) {
        labels.forEach(l => l.classList.remove('active'));
        blocks.forEach(b => b.classList.remove('active'));
        
        label.classList.add('active');
        if (blocks[idx]) blocks[idx].classList.add('active');
      }
    });
  });
}

// --- 3. Copy to Clipboard for Code Blocks ---
function initCodeCopyButtons() {
  const codeBlocks = document.querySelectorAll('.highlight');
  
  codeBlocks.forEach(block => {
    if (block.querySelector('.code-copy-btn')) return;
    
    const btn = document.createElement('button');
    btn.className = 'code-copy-btn';
    btn.title = 'কোড কপি করুন (Copy code)';
    btn.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M19 21H8V7h11m0-2H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2m-3-4H4a2 2 0 0 0-2 2v14h2V3h12V1z"/></svg>
      <span>কপি</span>
    `;
    
    btn.addEventListener('click', () => {
      const codeElem = block.querySelector('code') || block.querySelector('pre');
      if (!codeElem) return;
      
      const textToCopy = codeElem.innerText;
      navigator.clipboard.writeText(textToCopy).then(() => {
        btn.classList.add('copied');
        btn.querySelector('span').innerText = 'কপি করা হয়েছে!';
        showToast('কোড ক্লিপবোর্ডে কপি করা হয়েছে! ✓');
        
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.querySelector('span').innerText = 'কপি';
        }, 2200);
      });
    });
    
    block.appendChild(btn);
  });
}

function showToast(message) {
  let toast = document.querySelector('.toast-msg');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast-msg';
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 2500);
}

// --- 4. Search System (Bangla & English Search Index) ---
const searchIndex = [
  {
    "title": "১. First Steps (প্রথম পদক্ষেপ)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#first-steps",
    "keywords": "first steps প্রথম পদক্ষেপ first-steps fastapi ইনস্টলেশন এবং প্রথম hello world api তৈরি",
    "excerpt": "প্রথম পদক্ষেপ (First Steps): FastAPI ইনস্টলেশন এবং প্রথম Hello World API তৈরি।"
  },
  {
    "title": "২. Path Parameters (পাথ প্যারামিটার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#path-parameters",
    "keywords": "path parameters পাথ প্যারামিটার path-parameters url পাথে ডায়নামিক ভ্যারিয়েবল ও টাইপ ভ্যালিডেশন",
    "excerpt": "পাথ প্যারামিটার (Path Parameters): URL পাথে ডায়নামিক ভ্যারিয়েবল ও টাইপ ভ্যালিডেশন।"
  },
  {
    "title": "৩. Query Parameters (কুয়েরি প্যারামিটার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#query-parameters",
    "keywords": "query parameters কুয়েরি প্যারামিটার query-parameters url কুয়েরি স্ট্রিং থেকে অপশনাল ও ডিফল্ট মান গ্রহণ",
    "excerpt": "কুয়েরি প্যারামিটার (Query Parameters): URL কুয়েরি স্ট্রিং থেকে অপশনাল ও ডিফল্ট মান গ্রহণ।"
  },
  {
    "title": "৪. Request Body (রিকোয়েস্ট বডি)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#request-body",
    "keywords": "request body রিকোয়েস্ট বডি request-body pydantic মডেল ব্যবহার করে json বডি ডেটা গ্রহণ ও ভ্যালিডেশন",
    "excerpt": "রিকোয়েস্ট বডি (Request Body): Pydantic মডেল ব্যবহার করে JSON বডি ডেটা গ্রহণ ও ভ্যালিডেশন।"
  },
  {
    "title": "৫. Query Parameters and String Validations (কুয়েরি প্যারামিটার ও স্ট্রিং ভ্যালিডেশন)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#query-params-str-validations",
    "keywords": "query parameters and string validations কুয়েরি প্যারামিটার ও স্ট্রিং ভ্যালিডেশন query-params-str-validations query() ফাংশন, min_length, max_length, regex প্যাটার্ন",
    "excerpt": "কুয়েরি প্যারামিটার ও স্ট্রিং ভ্যালিডেশন (Query Parameters and String Validations): Query() ফাংশন, min_length, max_length, regex প্যাটার্ন।"
  },
  {
    "title": "৬. Path Parameters and Numeric Validations (পাথ প্যারামিটার ও নিউমেরিক ভ্যালিডেশন)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#path-params-num-validations",
    "keywords": "path parameters and numeric validations পাথ প্যারামিটার ও নিউমেরিক ভ্যালিডেশন path-params-num-validations path() ফাংশন, ge, le, gt, lt নিউমেরিক সীমাবদ্ধতা",
    "excerpt": "পাথ প্যারামিটার ও নিউমেরিক ভ্যালিডেশন (Path Parameters and Numeric Validations): Path() ফাংশন, ge, le, gt, lt নিউমেরিক সীমাবদ্ধতা।"
  },
  {
    "title": "৭. Query Parameter Models (কুয়েরি প্যারামিটার মডেল)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#query-param-models",
    "keywords": "query parameter models কুয়েরি প্যারামিটার মডেল query-param-models pydantic basemodel দিয়ে কুয়েরি প্যারামিটার গ্রুপ করা",
    "excerpt": "কুয়েরি প্যারামিটার মডেল (Query Parameter Models): Pydantic BaseModel দিয়ে কুয়েরি প্যারামিটার গ্রুপ করা।"
  },
  {
    "title": "৮. Body – Multiple Parameters (বডি – একাধিক প্যারামিটার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#body-multiple-params",
    "keywords": "body – multiple parameters বডি – একাধিক প্যারামিটার body-multiple-params একাধিক বডি মডেল এবং পাথ/কুয়েরি একসাথে সংমিশ্রণ",
    "excerpt": "বডি – একাধিক প্যারামিটার (Body – Multiple Parameters): একাধিক বডি মডেল এবং পাথ/কুয়েরি একসাথে সংমিশ্রণ।"
  },
  {
    "title": "৯. Body – Fields (বডি – ফিল্ডস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#body-fields",
    "keywords": "body – fields বডি – ফিল্ডস body-fields pydantic field() দিয়ে ফিল্ড ভ্যালিডেশন ও মেটাডেটা",
    "excerpt": "বডি – ফিল্ডস (Body – Fields): Pydantic Field() দিয়ে ফিল্ড ভ্যালিডেশন ও মেটাডেটা।"
  },
  {
    "title": "১০. Body – Nested Models (বডি – নেস্টেড মডেল)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#body-nested-models",
    "keywords": "body – nested models বডি – নেস্টেড মডেল body-nested-models লিস্ট, ডিকশনারি এবং নেস্টেড সাব-মডেল ডেটা স্ট্রাকচার",
    "excerpt": "বডি – নেস্টেড মডেল (Body – Nested Models): লিস্ট, ডিকশনারি এবং নেস্টেড সাব-মডেল ডেটা স্ট্রাকচার।"
  },
  {
    "title": "১১. Declare Request Example Data (রিকোয়েস্ট এক্সাম্পল ডেটা ডিক্লেয়ারেশন)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#declare-example-data",
    "keywords": "declare request example data রিকোয়েস্ট এক্সাম্পল ডেটা ডিক্লেয়ারেশন declare-example-data swagger ui-তে প্রদর্শনের জন্য রিকোয়েস্ট উদাহরণের কনফিগারেশন",
    "excerpt": "রিকোয়েস্ট এক্সাম্পল ডেটা ডিক্লেয়ারেশন (Declare Request Example Data): Swagger UI-তে প্রদর্শনের জন্য রিকোয়েস্ট উদাহরণের কনফিগারেশন।"
  },
  {
    "title": "১২. Extra Data Types (অতিরিক্ত ডেটা টাইপস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#extra-data-types",
    "keywords": "extra data types অতিরিক্ত ডেটা টাইপস extra-data-types uuid, datetime, date, time, timedelta, frozenset ইত্যাদি টাইপ",
    "excerpt": "অতিরিক্ত ডেটা টাইপস (Extra Data Types): UUID, datetime, date, time, timedelta, frozenset ইত্যাদি টাইপ।"
  },
  {
    "title": "১৩. Cookie Parameters (কুকি প্যারামিটার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#cookie-parameters",
    "keywords": "cookie parameters কুকি প্যারামিটার cookie-parameters cookie() ফাংশন দিয়ে ব্রাউজার কুকি মান গ্রহণ",
    "excerpt": "কুকি প্যারামিটার (Cookie Parameters): Cookie() ফাংশন দিয়ে ব্রাউজার কুকি মান গ্রহণ।"
  },
  {
    "title": "১৪. Header Parameters (হেডার প্যারামিটার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#header-parameters",
    "keywords": "header parameters হেডার প্যারামিটার header-parameters header() ফাংশন দিয়ে http রিকোয়েস্ট হেডার মান সংগ্রহ",
    "excerpt": "হেডার প্যারামিটার (Header Parameters): Header() ফাংশন দিয়ে HTTP রিকোয়েস্ট হেডার মান সংগ্রহ।"
  },
  {
    "title": "১৫. Cookie Parameter Models (কুকি প্যারামিটার মডেল)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#cookie-param-models",
    "keywords": "cookie parameter models কুকি প্যারামিটার মডেল cookie-param-models basemodel দিয়ে একাধিক কুকি প্যারামিটার একত্রে হ্যান্ডেল করা",
    "excerpt": "কুকি প্যারামিটার মডেল (Cookie Parameter Models): BaseModel দিয়ে একাধিক কুকি প্যারামিটার একত্রে হ্যান্ডেল করা।"
  },
  {
    "title": "১৬. Header Parameter Models (হেডার প্যারামিটার মডেল)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#header-param-models",
    "keywords": "header parameter models হেডার প্যারামিটার মডেল header-param-models basemodel দিয়ে একাধিক হেডার প্যারামিটার একত্রে গ্রহণ",
    "excerpt": "হেডার প্যারামিটার মডেল (Header Parameter Models): BaseModel দিয়ে একাধিক হেডার প্যারামিটার একত্রে গ্রহণ।"
  },
  {
    "title": "১৭. Response Model – Return Type (রেসপন্স মডেল – রিটার্ন টাইপ)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#response-model",
    "keywords": "response model – return type রেসপন্স মডেল – রিটার্ন টাইপ response-model response_model দিয়ে আউটপুট ফিল্টারিং ও ডেটা প্রটেকশন",
    "excerpt": "রেসপন্স মডেল – রিটার্ন টাইপ (Response Model – Return Type): response_model দিয়ে আউটপুট ফিল্টারিং ও ডেটা প্রটেকশন।"
  },
  {
    "title": "১৮. Extra Models (অতিরিক্ত মডেলস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#extra-models",
    "keywords": "extra models অতিরিক্ত মডেলস extra-models ইউজার রেজিস্ট্রেশন, পাবলিক প্রোফাইল ও ইনপুট/আউটপুট মডেল বিভাজন",
    "excerpt": "অতিরিক্ত মডেলস (Extra Models): ইউজার রেজিস্ট্রেশন, পাবলিক প্রোফাইল ও ইনপুট/আউটপুট মডেল বিভাজন।"
  },
  {
    "title": "১৯. Response Status Code (রেসপন্স স্ট্যাটাস কোড)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#response-status-code",
    "keywords": "response status code রেসপন্স স্ট্যাটাস কোড response-status-code status_code=status.http_201_created ইত্যাদি কাস্টম স্ট্যাটাস",
    "excerpt": "রেসপন্স স্ট্যাটাস কোড (Response Status Code): status_code=status.HTTP_201_CREATED ইত্যাদি কাস্টম স্ট্যাটাস।"
  },
  {
    "title": "২০. Form Data (ফর্ম ডেটা)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#form-data",
    "keywords": "form data ফর্ম ডেটা form-data html ফর্ম থেকে form() দিয়ে application/x-www-form-urlencoded ডেটা",
    "excerpt": "ফর্ম ডেটা (Form Data): HTML ফর্ম থেকে Form() দিয়ে application/x-www-form-urlencoded ডেটা।"
  },
  {
    "title": "২১. Form Models (ফর্ম মডেলস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#form-models",
    "keywords": "form models ফর্ম মডেলস form-models pydantic মডেল দিয়ে ফর্ম ফিল্ড গ্রুপ ও ভ্যালিডেশন",
    "excerpt": "ফর্ম মডেলস (Form Models): Pydantic মডেল দিয়ে ফর্ম ফিল্ড গ্রুপ ও ভ্যালিডেশন।"
  },
  {
    "title": "২২. Request Files (রিকোয়েস্ট ফাইলস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#request-files",
    "keywords": "request files রিকোয়েস্ট ফাইলস request-files file() এবং uploadfile ব্যবহার করে ফাইল আপলোড হ্যান্ডলিং",
    "excerpt": "রিকোয়েস্ট ফাইলস (Request Files): File() এবং UploadFile ব্যবহার করে ফাইল আপলোড হ্যান্ডলিং।"
  },
  {
    "title": "২৩. Request Forms and Files (রিকোয়েস্ট ফর্মস ও ফাইলস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#request-forms-and-files",
    "keywords": "request forms and files রিকোয়েস্ট ফর্মস ও ফাইলস request-forms-and-files একই এন্ডপয়েন্টে ফর্ম ফিল্ড এবং আপলোড ফাইল একসাথে গ্রহণ",
    "excerpt": "রিকোয়েস্ট ফর্মস ও ফাইলস (Request Forms and Files): একই এন্ডপয়েন্টে ফর্ম ফিল্ড এবং আপলোড ফাইল একসাথে গ্রহণ।"
  },
  {
    "title": "২৪. Handling Errors (এরর হ্যান্ডলিং)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#handling-errors",
    "keywords": "handling errors এরর হ্যান্ডলিং handling-errors httpexception এবং কাস্টম এক্সেপশন হ্যান্ডলার",
    "excerpt": "এরর হ্যান্ডলিং (Handling Errors): HTTPException এবং কাস্টম এক্সেপশন হ্যান্ডলার।"
  },
  {
    "title": "২৫. Path Operation Configuration (পাথ অপারেশন কনফিগারেশন)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#path-op-config",
    "keywords": "path operation configuration পাথ অপারেশন কনফিগারেশন path-op-config tags, summary, description, response_description কনফিগ",
    "excerpt": "পাথ অপারেশন কনফিগারেশন (Path Operation Configuration): tags, summary, description, response_description কনফিগ।"
  },
  {
    "title": "২৬. JSON Compatible Encoder (JSON কম্প্যাটিবল এনকোডার)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#json-encoder",
    "keywords": "json compatible encoder json কম্প্যাটিবল এনকোডার json-encoder jsonable_encoder() দিয়ে অবজেক্টকে json ফরম্যাটে রূপান্তর",
    "excerpt": "JSON কম্প্যাটিবল এনকোডার (JSON Compatible Encoder): jsonable_encoder() দিয়ে অবজেক্টকে JSON ফরম্যাটে রূপান্তর।"
  },
  {
    "title": "২৭. Body – Updates (বডি – আপডেটস)",
    "category": "FastAPI Tutorial (টিউটোরিয়াল)",
    "url": "../learn/#body-updates",
    "keywords": "body – updates বডি – আপডেটস body-updates put এবং patch দিয়ে পূর্ণাঙ্গ ও আংশিক (partial) আপডেট",
    "excerpt": "বডি – আপডেটস (Body – Updates): PUT এবং PATCH দিয়ে পূর্ণাঙ্গ ও আংশিক (partial) আপডেট।"
  },
  {
    "title": "২৮. Dependencies (ডিপেন্ডেন্সিস)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#dependencies",
    "keywords": "dependencies ডিপেন্ডেন্সিস dependencies fastapi-র শক্তিশালী ডিপেন্ডেন্সি ইনজেকশন সিস্টেমের মূলভিত্তি",
    "excerpt": "ডিপেন্ডেন্সিস (Dependencies): FastAPI-র শক্তিশালী ডিপেন্ডেন্সি ইনজেকশন সিস্টেমের মূলভিত্তি।"
  },
  {
    "title": "২৯. Classes as Dependencies (ক্লাস ডিপেন্ডেন্সি)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#classes-as-deps",
    "keywords": "classes as dependencies ক্লাস ডিপেন্ডেন্সি classes-as-deps ক্লাস ইনস্ট্যান্সকে ডিপেন্ডেন্সি হিসেবে ব্যবহার ও শর্টকাট",
    "excerpt": "ক্লাস ডিপেন্ডেন্সি (Classes as Dependencies): ক্লাস ইনস্ট্যান্সকে ডিপেন্ডেন্সি হিসেবে ব্যবহার ও শর্টকাট।"
  },
  {
    "title": "৩০. Sub-dependencies (সাব-ডিপেন্ডেন্সিস)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#sub-dependencies",
    "keywords": "sub-dependencies সাব-ডিপেন্ডেন্সিস sub-dependencies ডিপেন্ডেন্সির ভেতরে অন্য ডিপেন্ডেন্সির মাল্টি-লেভেল হায়ারার্কি",
    "excerpt": "সাব-ডিপেন্ডেন্সিস (Sub-dependencies): ডিপেন্ডেন্সির ভেতরে অন্য ডিপেন্ডেন্সির মাল্টি-লেভেল হায়ারার্কি।"
  },
  {
    "title": "৩১. Dependencies in Path Operation Decorators (পাথ অপারেশন ডেকোরেটরে ডিপেন্ডেন্সিস)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#deps-in-decorators",
    "keywords": "dependencies in path operation decorators পাথ অপারেশন ডেকোরেটরে ডিপেন্ডেন্সিস deps-in-decorators dependencies=[depends(...)] দিয়ে গ্লোবাল ভ্যালিডেশন",
    "excerpt": "পাথ অপারেশন ডেকোরেটরে ডিপেন্ডেন্সিস (Dependencies in Path Operation Decorators): dependencies=[Depends(...)] দিয়ে গ্লোবাল ভ্যালিডেশন।"
  },
  {
    "title": "৩২. Global Dependencies (গ্লোবাল ডিপেন্ডেন্সিস)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#global-dependencies",
    "keywords": "global dependencies গ্লোবাল ডিপেন্ডেন্সিস global-dependencies সমগ্র অ্যাপ্লিকেশনের সব রুটে ডিপেন্ডেন্সি প্রয়োগ",
    "excerpt": "গ্লোবাল ডিপেন্ডেন্সিস (Global Dependencies): সমগ্র অ্যাপ্লিকেশনের সব রুটে ডিপেন্ডেন্সি প্রয়োগ।"
  },
  {
    "title": "৩৩. Dependencies with yield (yield সহ ডিপেন্ডেন্সিস)",
    "category": "Dependencies (ডিপেন্ডেন্সিস)",
    "url": "../learn/#deps-with-yield",
    "keywords": "dependencies with yield yield সহ ডিপেন্ডেন্সিস deps-with-yield সেটআপ ও টিয়ারডাউন (context manager) ডিপেন্ডেন্সি লজিক",
    "excerpt": "yield সহ ডিপেন্ডেন্সিস (Dependencies with yield): সেটআপ ও টিয়ারডাউন (Context Manager) ডিপেন্ডেন্সি লজিক।"
  },
  {
    "title": "৩৪. Security – First Steps (সিকিউরিটি – প্রথম পদক্ষেপ)",
    "category": "Security (সিকিউরিটি)",
    "url": "../learn/#security-first-steps",
    "keywords": "security – first steps সিকিউরিটি – প্রথম পদক্ষেপ security-first-steps oauth2passwordbearer এবং swagger ui অথেন্টিকেশন ইন্টিগ্রেশন",
    "excerpt": "সিকিউরিটি – প্রথম পদক্ষেপ (Security – First Steps): OAuth2PasswordBearer এবং Swagger UI অথেন্টিকেশন ইন্টিগ্রেশন।"
  },
  {
    "title": "৩৫. Get Current User (বর্তমান ব্যবহারকারী যাচাই)",
    "category": "Security (সিকিউরিটি)",
    "url": "../learn/#get-current-user",
    "keywords": "get current user বর্তমান ব্যবহারকারী যাচাই get-current-user টোকেন ভ্যালিডেশনের মাধ্যমে বর্তমান ব্যবহারকারী অবজেক্ট উদ্ধার",
    "excerpt": "বর্তমান ব্যবহারকারী যাচাই (Get Current User): টোকেন ভ্যালিডেশনের মাধ্যমে বর্তমান ব্যবহারকারী অবজেক্ট উদ্ধার।"
  },
  {
    "title": "৩৬. Simple OAuth2 with Password and Bearer (সিম্পল OAuth2 Password ও Bearer)",
    "category": "Security (সিকিউরিটি)",
    "url": "../learn/#oauth2-password-bearer",
    "keywords": "simple oauth2 with password and bearer সিম্পল oauth2 password ও bearer oauth2-password-bearer ইউজারনেম ও পাসওয়ার্ড দিয়ে bearer টোকেন প্রবাহ",
    "excerpt": "সিম্পল OAuth2 Password ও Bearer (Simple OAuth2 with Password and Bearer): ইউজারনেম ও পাসওয়ার্ড দিয়ে Bearer টোকেন প্রবাহ।"
  },
  {
    "title": "৩৭. OAuth2 with Password, Hashing, Bearer with JWT Tokens (OAuth2 Hashing ও JWT Tokens)",
    "category": "Security (সিকিউরিটি)",
    "url": "../learn/#oauth2-jwt",
    "keywords": "oauth2 with password, hashing, bearer with jwt tokens oauth2 hashing ও jwt tokens oauth2-jwt passlib পাসওয়ার্ড হ্যাশিং এবং pyjwt টোকেন এনকোডিং/ডিকোডিং",
    "excerpt": "OAuth2 Hashing ও JWT Tokens (OAuth2 with Password, Hashing, Bearer with JWT Tokens): Passlib পাসওয়ার্ড হ্যাশিং এবং PyJWT টোকেন এনকোডিং/ডিকোডিং।"
  },
  {
    "title": "৩৮. Middleware (মিডলওয়্যার)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#middleware",
    "keywords": "middleware মিডলওয়্যার middleware রিকোয়েস্ট ও রেসপন্স পাইপলাইনে কাস্টম মিডলওয়্যার প্রসেসিং",
    "excerpt": "মিডলওয়্যার (Middleware): রিকোয়েস্ট ও রেসপন্স পাইপলাইনে কাস্টম মিডলওয়্যার প্রসেসিং।"
  },
  {
    "title": "৩৯. CORS (CORS (ক্রস-অরিজিন শেয়ারিং))",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#cors",
    "keywords": "cors cors (ক্রস-অরিজিন শেয়ারিং) cors corsmiddleware দিয়ে ফ্রন্টএন্ড ডোমেইন অনুমোদনের কনফিগারেশন",
    "excerpt": "CORS (ক্রস-অরিজিন শেয়ারিং) (CORS): CORSMiddleware দিয়ে ফ্রন্টএন্ড ডোমেইন অনুমোদনের কনফিগারেশন।"
  },
  {
    "title": "৪০. SQL (Relational) Databases (SQL রিলেশনাল ডাটাবেস)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#sql-databases",
    "keywords": "sql (relational) databases sql রিলেশনাল ডাটাবেস sql-databases sqlalchemy orm ও sqlite/postgresql ডাটাবেস ইন্টিগ্রেশন",
    "excerpt": "SQL রিলেশনাল ডাটাবেস (SQL (Relational) Databases): SQLAlchemy ORM ও SQLite/PostgreSQL ডাটাবেস ইন্টিগ্রেশন।"
  },
  {
    "title": "৪১. Bigger Applications – Multiple Files (বড় অ্যাপ্লিকেশন – একাধিক ফাইল)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#bigger-applications",
    "keywords": "bigger applications – multiple files বড় অ্যাপ্লিকেশন – একাধিক ফাইল bigger-applications apirouter দিয়ে প্রজেক্টকে মডুলার ও অর্গানাইজড ফাইলে ভাগ করা",
    "excerpt": "বড় অ্যাপ্লিকেশন – একাধিক ফাইল (Bigger Applications – Multiple Files): APIRouter দিয়ে প্রজেক্টকে মডুলার ও অর্গানাইজড ফাইলে ভাগ করা।"
  },
  {
    "title": "৪২. Stream JSON Lines (স্ট্রিম JSON লাইনস)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#stream-json-lines",
    "keywords": "stream json lines স্ট্রিম json লাইনস stream-json-lines বড় ডেটাসেটের জন্য লাইন-বাই-লাইন json স্ট্রিমিং",
    "excerpt": "স্ট্রিম JSON লাইনস (Stream JSON Lines): বড় ডেটাসেটের জন্য লাইন-বাই-লাইন JSON স্ট্রিমিং।"
  },
  {
    "title": "৪৩. Server-Sent Events (SSE) (সার্ভার-সেন্ট ইভেন্টস (SSE))",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#server-sent-events",
    "keywords": "server-sent events (sse) সার্ভার-সেন্ট ইভেন্টস (sse) server-sent-events eventsource দিয়ে ব্রাউজারে রিয়েল-টাইম ইউনিডিরেকশনাল ডাটা পুশ",
    "excerpt": "সার্ভার-সেন্ট ইভেন্টস (SSE) (Server-Sent Events (SSE)): EventSource দিয়ে ব্রাউজারে রিয়েল-টাইম ইউনিডিরেকশনাল ডাটা পুশ।"
  },
  {
    "title": "৪৪. Background Tasks (ব্যাকগ্রাউন্ড টাস্ক)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#background-tasks",
    "keywords": "background tasks ব্যাকগ্রাউন্ড টাস্ক background-tasks backgroundtasks দিয়ে রেসপন্স পাঠানোর পর ইমেইল বা লং-টাস্ক সম্পন্ন করা",
    "excerpt": "ব্যাকগ্রাউন্ড টাস্ক (Background Tasks): BackgroundTasks দিয়ে রেসপন্স পাঠানোর পর ইমেইল বা লং-টাস্ক সম্পন্ন করা।"
  },
  {
    "title": "৪৫. Metadata and Docs URLs (মেটাডাটা ও ডক্স ইউআরএল)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#metadata-docs",
    "keywords": "metadata and docs urls মেটাডাটা ও ডক্স ইউআরএল metadata-docs openapi টাইটেল, ডেসক্রিপশন, লাইসেন্স ও ডক্স ইউআরএল পাথ কাস্টমাইজেশন",
    "excerpt": "মেটাডাটা ও ডক্স ইউআরএল (Metadata and Docs URLs): OpenAPI টাইটেল, ডেসক্রিপশন, লাইসেন্স ও ডক্স ইউআরএল পাথ কাস্টমাইজেশন।"
  },
  {
    "title": "৪৬. Frontend (ফ্রন্টএন্ড ইন্টিগ্রেশন)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#frontend",
    "keywords": "frontend ফ্রন্টএন্ড ইন্টিগ্রেশন frontend html, javascript এবং spa-র সাথে fastapi ব্যাকএন্ড কানেকশন",
    "excerpt": "ফ্রন্টএন্ড ইন্টিগ্রেশন (Frontend): HTML, JavaScript এবং SPA-র সাথে FastAPI ব্যাকএন্ড কানেকশন।"
  },
  {
    "title": "৪৭. Static Files (স্ট্যাটিক ফাইলস)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#static-files",
    "keywords": "static files স্ট্যাটিক ফাইলস static-files staticfiles দিয়ে css, js, ছবি ও অ্যাসেট ফোল্ডার মাউন্ট করা",
    "excerpt": "স্ট্যাটিক ফাইলস (Static Files): StaticFiles দিয়ে CSS, JS, ছবি ও অ্যাসেট ফোল্ডার মাউন্ট করা।"
  },
  {
    "title": "৪৮. Testing (টেস্টিং (pytest))",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#testing",
    "keywords": "testing টেস্টিং (pytest) testing pytest এবং testclient (httpx) দিয়ে ইউনিট ও ইন্টিগ্রেশন টেস্ট",
    "excerpt": "টেস্টিং (pytest) (Testing): pytest এবং TestClient (httpx) দিয়ে ইউনিট ও ইন্টিগ্রেশন টেস্ট।"
  },
  {
    "title": "৪৯. Debugging (ডিবাগিং)",
    "category": "Other Tutorial Topics (অন্যান্য বিষয়)",
    "url": "../learn/#debugging",
    "keywords": "debugging ডিবাগিং debugging vs code ও pycharm-এ uvicorn ব্রেকপয়েন্ট দিয়ে ডিবাগিং কৌশল",
    "excerpt": "ডিবাগিং (Debugging): VS Code ও PyCharm-এ Uvicorn ব্রেকপয়েন্ট দিয়ে ডিবাগিং কৌশল।"
  },
  {
    "title": "৫০. Stream Data (স্ট্রিম ডেটা)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-stream-data",
    "keywords": "stream data স্ট্রিম ডেটা adv-stream-data streamingresponse দিয়ে অডিও, ভিডিও ও লাইভ ডাটা স্ট্রিম",
    "excerpt": "স্ট্রিম ডেটা (Stream Data): StreamingResponse দিয়ে অডিও, ভিডিও ও লাইভ ডাটা স্ট্রিম।"
  },
  {
    "title": "৫১. Path Operation Advanced Configuration (পাথ অপারেশন অ্যাডভান্সড কনফিগারেশন)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-path-config",
    "keywords": "path operation advanced configuration পাথ অপারেশন অ্যাডভান্সড কনফিগারেশন adv-path-config openapi_extra, deprecated, operation_id কাস্টমাইজেশন",
    "excerpt": "পাথ অপারেশন অ্যাডভান্সড কনফিগারেশন (Path Operation Advanced Configuration): openapi_extra, deprecated, operation_id কাস্টমাইজেশন।"
  },
  {
    "title": "৫২. Additional Status Codes (অতিরিক্ত স্ট্যাটাস কোডস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-status-codes",
    "keywords": "additional status codes অতিরিক্ত স্ট্যাটাস কোডস adv-status-codes নির্দিষ্ট কন্ডিশনে সরাসরি ভিন্ন ভিন্ন http স্ট্যাটাস কোড প্রদান",
    "excerpt": "অতিরিক্ত স্ট্যাটাস কোডস (Additional Status Codes): নির্দিষ্ট কন্ডিশনে সরাসরি ভিন্ন ভিন্ন HTTP স্ট্যাটাস কোড প্রদান।"
  },
  {
    "title": "৫৩. Return a Response Directly (সরাসরি রেসপন্স রিটার্ন)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-direct-response",
    "keywords": "return a response directly সরাসরি রেসপন্স রিটার্ন adv-direct-response response ক্লাস ব্যবহার করে সরাসরি হেডার ও কুকি সহ রেসপন্স প্রদান",
    "excerpt": "সরাসরি রেসপন্স রিটার্ন (Return a Response Directly): Response ক্লাস ব্যবহার করে সরাসরি হেডার ও কুকি সহ রেসপন্স প্রদান।"
  },
  {
    "title": "৫৪. Custom Response (কাস্টম রেসপন্স)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-custom-response",
    "keywords": "custom response কাস্টম রেসপন্স adv-custom-response htmlresponse, plaintextresponse, ujsonresponse, orjsonresponse",
    "excerpt": "কাস্টম রেসপন্স (Custom Response): HTMLResponse, PlainTextResponse, UJSONResponse, ORJSONResponse।"
  },
  {
    "title": "৫৫. Additional Responses in OpenAPI (OpenAPI-তে অতিরিক্ত রেসপন্স)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-openapi-responses",
    "keywords": "additional responses in openapi openapi-তে অতিরিক্ত রেসপন্স adv-openapi-responses swagger ডকুমেন্টে 404, 403 এর এরর স্কিমা মডেল ডিক্লেয়ার করা",
    "excerpt": "OpenAPI-তে অতিরিক্ত রেসপন্স (Additional Responses in OpenAPI): Swagger ডকুমেন্টে 404, 403 এর এরর স্কিমা মডেল ডিক্লেয়ার করা।"
  },
  {
    "title": "৫৬. Response Cookies (রেসপন্স কুকিজ)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-response-cookies",
    "keywords": "response cookies রেসপন্স কুকিজ adv-response-cookies response.set_cookie() দিয়ে secure, httponly কুকি সেট করা",
    "excerpt": "রেসপন্স কুকিজ (Response Cookies): Response.set_cookie() দিয়ে Secure, HttpOnly কুকি সেট করা।"
  },
  {
    "title": "৫৭. Response Headers (রেসপন্স হেডার্স)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-response-headers",
    "keywords": "response headers রেসপন্স হেডার্স adv-response-headers response.headers দিয়ে কাস্টম সিকিউরিটি ও মেটাডাটা হেডার সংযোজন",
    "excerpt": "রেসপন্স হেডার্স (Response Headers): Response.headers দিয়ে কাস্টম সিকিউরিটি ও মেটাডাটা হেডার সংযোজন।"
  },
  {
    "title": "৫৮. Response – Change Status Code (রেসপন্স স্ট্যাটাস কোড পরিবর্তন)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-change-status",
    "keywords": "response – change status code রেসপন্স স্ট্যাটাস কোড পরিবর্তন adv-change-status রানটাইমে রেসপন্স স্ট্যাটাস কোড ডায়নামিকালি পরিবর্তন করা",
    "excerpt": "রেসপন্স স্ট্যাটাস কোড পরিবর্তন (Response – Change Status Code): রানটাইমে রেসপন্স স্ট্যাটাস কোড ডায়নামিকালি পরিবর্তন করা।"
  },
  {
    "title": "৫৯. Advanced Dependencies (অ্যাডভান্সড ডিপেন্ডেন্সিস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-dependencies",
    "keywords": "advanced dependencies অ্যাডভান্সড ডিপেন্ডেন্সিস adv-dependencies কলযোগ্য অবজেক্ট, প্যারামিটারাইজড ডিপেন্ডেন্সি ও ক্যাশিং আচরণ",
    "excerpt": "অ্যাডভান্সড ডিপেন্ডেন্সিস (Advanced Dependencies): কলযোগ্য অবজেক্ট, প্যারামিটারাইজড ডিপেন্ডেন্সি ও ক্যাশিং আচরণ।"
  },
  {
    "title": "৬০. OAuth2 Scopes (OAuth2 স্কোপস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-oauth2-scopes",
    "keywords": "oauth2 scopes oauth2 স্কোপস adv-oauth2-scopes securityscopes দিয়ে রোল ও ফাইন-গ্রেইনড পারমিশন ভ্যালিডেশন",
    "excerpt": "OAuth2 স্কোপস (OAuth2 Scopes): SecurityScopes দিয়ে রোল ও ফাইন-গ্রেইনড পারমিশন ভ্যালিডেশন।"
  },
  {
    "title": "৬১. HTTP Basic Auth (HTTP Basic Auth)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-http-basic-auth",
    "keywords": "http basic auth http basic auth adv-http-basic-auth httpbasic এবং httpbasiccredentials দিয়ে সহজ প্রমাণীকরণ",
    "excerpt": "HTTP Basic Auth (HTTP Basic Auth): HTTPBasic এবং HTTPBasicCredentials দিয়ে সহজ প্রমাণীকরণ।"
  },
  {
    "title": "৬২. Using the Request Directly (সরাসরি রিকোয়েস্ট অবজেক্ট ব্যবহার)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-using-request",
    "keywords": "using the request directly সরাসরি রিকোয়েস্ট অবজেক্ট ব্যবহার adv-using-request client ip, host, raw headers ও raw body পড়ার জন্য request অবজেক্ট",
    "excerpt": "সরাসরি রিকোয়েস্ট অবজেক্ট ব্যবহার (Using the Request Directly): Client IP, Host, Raw Headers ও Raw Body পড়ার জন্য Request অবজেক্ট।"
  },
  {
    "title": "৬৩. Using Dataclasses (Dataclasses ব্যবহার)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-dataclasses",
    "keywords": "using dataclasses dataclasses ব্যবহার adv-dataclasses python স্ট্যান্ডার্ড dataclasses দিয়ে রিকোয়েস্ট ও রেসপন্স মডেলিং",
    "excerpt": "Dataclasses ব্যবহার (Using Dataclasses): Python স্ট্যান্ডার্ড dataclasses দিয়ে রিকোয়েস্ট ও রেসপন্স মডেলিং।"
  },
  {
    "title": "৬৪. Advanced Middleware (অ্যাডভান্সড মিডলওয়্যার)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-middleware",
    "keywords": "advanced middleware অ্যাডভান্সড মিডলওয়্যার adv-middleware basehttpmiddleware ও asgi মিডলওয়্যার তৈরির কৌশল",
    "excerpt": "অ্যাডভান্সড মিডলওয়্যার (Advanced Middleware): BaseHTTPMiddleware ও ASGI মিডলওয়্যার তৈরির কৌশল।"
  },
  {
    "title": "৬৫. Sub Applications – Mounts (সাব অ্যাপ্লিকেশন ও মাউন্টস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-sub-apps",
    "keywords": "sub applications – mounts সাব অ্যাপ্লিকেশন ও মাউন্টস adv-sub-apps app.mount() দিয়ে একাধিক স্বাধীন fastapi অ্যাপ একত্রীকরণ",
    "excerpt": "সাব অ্যাপ্লিকেশন ও মাউন্টস (Sub Applications – Mounts): app.mount() দিয়ে একাধিক স্বাধীন FastAPI অ্যাপ একত্রীকরণ।"
  },
  {
    "title": "৬৬. Behind a Proxy (প্রক্সির পেছনে সার্ভার)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-behind-proxy",
    "keywords": "behind a proxy প্রক্সির পেছনে সার্ভার adv-behind-proxy nginx/traefik রিভার্স প্রক্সির জন্য root_path ও প্রক্সি হেডার কনফিগারেশন",
    "excerpt": "প্রক্সির পেছনে সার্ভার (Behind a Proxy): Nginx/Traefik রিভার্স প্রক্সির জন্য root_path ও প্রক্সি হেডার কনফিগারেশন।"
  },
  {
    "title": "৬৭. Templates (টেমপ্লেটস - Jinja2)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-templates",
    "keywords": "templates টেমপ্লেটস - jinja2 adv-templates jinja2templates দিয়ে সার্ভার-সাইড html রেন্ডারিং",
    "excerpt": "টেমপ্লেটস - Jinja2 (Templates): Jinja2Templates দিয়ে সার্ভার-সাইড HTML রেন্ডারিং।"
  },
  {
    "title": "৬৮. WebSockets (ওয়েবসকেটস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-websockets",
    "keywords": "websockets ওয়েবসকেটস adv-websockets websocket দিয়ে রিয়েল-টাইম বাই-ডিরেকশনাল ফুল-ডুপ্লেক্স যোগাযোগ",
    "excerpt": "ওয়েবসকেটস (WebSockets): WebSocket দিয়ে রিয়েল-টাইম বাই-ডিরেকশনাল ফুল-ডুপ্লেক্স যোগাযোগ।"
  },
  {
    "title": "৬৯. Lifespan Events (লাইফস্প্যান ইভেন্টস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-lifespan",
    "keywords": "lifespan events লাইফস্প্যান ইভেন্টস adv-lifespan asynccontextmanager দিয়ে স্টার্টআপ ও শাটডাউন রিসোর্স ম্যানেজমেন্ট",
    "excerpt": "লাইফস্প্যান ইভেন্টস (Lifespan Events): asynccontextmanager দিয়ে স্টার্টআপ ও শাটডাউন রিসোর্স ম্যানেজমেন্ট।"
  },
  {
    "title": "৭০. OpenTelemetry (ওপেনটেলিমეტ্রি)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-opentelemetry",
    "keywords": "opentelemetry ওপেনটেলিমეტ্রি adv-opentelemetry ডিস্ট্রিবিউটেড ট্রেসিং ও মেট্রিক্স মনিটরিং ইন্টিগ্রেশন",
    "excerpt": "ওপেনটেলিমეტ্রি (OpenTelemetry): ডিস্ট্রিবিউটেড ট্রেসিং ও মেট্রিক্স মনিটরিং ইন্টিগ্রেশন।"
  },
  {
    "title": "৭১. Testing WebSockets (ওয়েবসকেট টেস্টিং)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-test-websockets",
    "keywords": "testing websockets ওয়েবসকেট টেস্টিং adv-test-websockets testclient দিয়ে ওয়েবসকেট কানেকশন ও মেসেজ আদান-প্রদান টেস্ট",
    "excerpt": "ওয়েবসকেট টেস্টিং (Testing WebSockets): TestClient দিয়ে ওয়েবসকেট কানেকশন ও মেসেজ আদান-প্রদান টেস্ট।"
  },
  {
    "title": "৭২. Testing Events (ইভেন্ট টেস্টিং)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-test-events",
    "keywords": "testing events ইভেন্ট টেস্টিং adv-test-events অ্যাপ্লিকেশনের লাইফস্প্যান স্টার্টআপ ও শাটডাউন লজিক টেস্টিং",
    "excerpt": "ইভেন্ট টেস্টিং (Testing Events): অ্যাপ্লিকেশনের লাইফস্প্যান স্টার্টআপ ও শাটডাউন লজিক টেস্টিং।"
  },
  {
    "title": "৭৩. Testing Dependencies with Overrides (ডিপেন্ডেন্সি ওভাররাইড টেস্ট)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-test-overrides",
    "keywords": "testing dependencies with overrides ডিপেন্ডেন্সি ওভাররাইড টেস্ট adv-test-overrides app.dependency_overrides দিয়ে টেস্টে মক ডাটাবেস ইনজেকশন",
    "excerpt": "ডিপেন্ডেন্সি ওভাররাইড টেস্ট (Testing Dependencies with Overrides): app.dependency_overrides দিয়ে টেস্টে মক ডাটাবেস ইনজেকশন।"
  },
  {
    "title": "৭৪. Async Tests (অ্যাসিঙ্ক টেস্ট)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-async-tests",
    "keywords": "async tests অ্যাসিঙ্ক টেস্ট adv-async-tests httpx.asyncclient ও pytest-asyncio দিয়ে অ্যাসিঙ্ক এন্ডপয়েন্ট টেস্ট",
    "excerpt": "অ্যাসিঙ্ক টেস্ট (Async Tests): httpx.AsyncClient ও pytest-asyncio দিয়ে অ্যাসিঙ্ক এন্ডপয়েন্ট টেস্ট।"
  },
  {
    "title": "৭৫. Settings and Environment Variables (সেটিংস ও এনভায়রনমেন্ট ভেরিয়েবল)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-settings-env",
    "keywords": "settings and environment variables সেটিংস ও এনভায়রনমেন্ট ভেরিয়েবল adv-settings-env pydantic-settings ও basesettings দিয়ে .env কনফিগারেশন লোড",
    "excerpt": "সেটিংস ও এনভায়রনমেন্ট ভেরিয়েবল (Settings and Environment Variables): pydantic-settings ও BaseSettings দিয়ে .env কনফিগারেশন লোড।"
  },
  {
    "title": "৭৬. OpenAPI Callbacks (OpenAPI কলব্যাকস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-openapi-callbacks",
    "keywords": "openapi callbacks openapi কলব্যাকস adv-openapi-callbacks সাবস্ক্রিপশনের বিপরীতে থার্ড-পার্টি ওয়েবহুক কলব্যাক ডকুমেন্টেশন",
    "excerpt": "OpenAPI কলব্যাকস (OpenAPI Callbacks): সাবস্ক্রিপশনের বিপরীতে থার্ড-পার্টি ওয়েবহুক কলব্যাক ডকুমেন্টেশন।"
  },
  {
    "title": "৭৭. OpenAPI Webhooks (OpenAPI ওয়েবহুকস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-openapi-webhooks",
    "keywords": "openapi webhooks openapi ওয়েবহুকস adv-openapi-webhooks অ্যাপ্লিকেশন যে ইভেন্টগুলো সেন্ড করে তার জন্য webhooks ডকুমেন্টেশন",
    "excerpt": "OpenAPI ওয়েবহুকস (OpenAPI Webhooks): অ্যাপ্লিকেশন যে ইভেন্টগুলো সেন্ড করে তার জন্য Webhooks ডকুমেন্টেশন।"
  },
  {
    "title": "৭৮. Including WSGI – Flask, Django, others (WSGI ইন্টিগ্রেশন – Flask, Django)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-wsgi",
    "keywords": "including wsgi – flask, django, others wsgi ইন্টিগ্রেশন – flask, django adv-wsgi wsgimiddleware দিয়ে পুরাতন flask বা django অ্যাপ মাউন্ট করা",
    "excerpt": "WSGI ইন্টিগ্রেশন – Flask, Django (Including WSGI – Flask, Django, others): WSGIMiddleware দিয়ে পুরাতন Flask বা Django অ্যাপ মাউন্ট করা।"
  },
  {
    "title": "৭৯. Generating SDKs (SDK জেনারেশন)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-sdks",
    "keywords": "generating sdks sdk জেনারেশন adv-sdks openapi স্পেসিফিকেশন থেকে typescript, python ক্লায়েন্ট sdk তৈরি",
    "excerpt": "SDK জেনারেশন (Generating SDKs): OpenAPI স্পেসিফিকেশন থেকে TypeScript, Python ক্লায়েন্ট SDK তৈরি।"
  },
  {
    "title": "৮০. Advanced Python Types (অ্যাডভান্সড পাইথন টাইপস)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-types",
    "keywords": "advanced python types অ্যাডভান্সড পাইথন টাইপস adv-types union, optional, any, annotated ও জেনেরিক টাইপ হিন্টিং",
    "excerpt": "অ্যাডভান্সড পাইথন টাইপস (Advanced Python Types): Union, Optional, Any, Annotated ও জেনেরিক টাইপ হিন্টিং।"
  },
  {
    "title": "৮১. JSON with Bytes as Base64 (Base64 বাইটস সহ JSON)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-base64-bytes",
    "keywords": "json with bytes as base64 base64 বাইটস সহ json adv-base64-bytes json পেলোডে বাইনারি ডেটা base64 এনকোড করে আদান-প্রদান",
    "excerpt": "Base64 বাইটস সহ JSON (JSON with Bytes as Base64): JSON পেলোডে বাইনারি ডেটা Base64 এনকোড করে আদান-প্রদান।"
  },
  {
    "title": "৮২. Strict Content-Type Checking (কঠোর কন্টেন্ট-টাইপ চেকিং)",
    "category": "Advanced (অ্যাডভান্সড)",
    "url": "../learn/#adv-strict-content-type",
    "keywords": "strict content-type checking কঠোর কন্টেন্ট-টাইপ চেকিং adv-strict-content-type রিকোয়েস্ট হেডার content-type কঠোরভাবে যাচাই ও এনফোর্স করা",
    "excerpt": "কঠোর কন্টেন্ট-টাইপ চেকিং (Strict Content-Type Checking): রিকোয়েস্ট হেডার Content-Type কঠোরভাবে যাচাই ও এনফোর্স করা।"
  },
  {
    "title": "৮৩. About FastAPI Versions (FastAPI ভার্সন পরিচিতি)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-versions",
    "keywords": "about fastapi versions fastapi ভার্সন পরিচিতি dep-versions ভার্সন পিনিং, সেমান্টিক ভার্সনিং এবং আপগ্রেড নিরাপত্তা",
    "excerpt": "FastAPI ভার্সন পরিচিতি (About FastAPI Versions): ভার্সন পিনিং, সেমান্টিক ভার্সনিং এবং আপগ্রেড নিরাপত্তা।"
  },
  {
    "title": "৮৪. FastAPI Cloud (FastAPI ক্লাউড)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-cloud",
    "keywords": "fastapi cloud fastapi ক্লাউড dep-cloud fastapi cloud প্ল্যাটফর্মে ওয়ান-ক্লিক ডিপ্লয়মেন্ট এবং সিঙ্ক",
    "excerpt": "FastAPI ক্লাউড (FastAPI Cloud): FastAPI Cloud প্ল্যাটফর্মে ওয়ান-ক্লিক ডিপ্লয়মেন্ট এবং সিঙ্ক।"
  },
  {
    "title": "৮৫. About HTTPS (HTTPS সম্পর্কে)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-https",
    "keywords": "about https https সম্পর্কে dep-https tls/ssl সার্টিফিকেট, let’s encrypt এবং নিরাপদ এনক্রিপশন",
    "excerpt": "HTTPS সম্পর্কে (About HTTPS): TLS/SSL সার্টিফিকেট, Let’s Encrypt এবং নিরাপদ এনক্রিপশন।"
  },
  {
    "title": "৮৬. Run a Server Manually (ম্যানুয়ালি সার্ভার রান করা)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-manual-server",
    "keywords": "run a server manually ম্যানুয়ালি সার্ভার রান করা dep-manual-server uvicorn.run() এবং স্ক্রিপ্ট বা কমান্ড লাইন দিয়ে সার্ভার এক্সিকিউশন",
    "excerpt": "ম্যানুয়ালি সার্ভার রান করা (Run a Server Manually): uvicorn.run() এবং স্ক্রিপ্ট বা কমান্ড লাইন দিয়ে সার্ভার এক্সিকিউশন।"
  },
  {
    "title": "৮৭. Deployment Concepts (ডিপ্লয়মেন্ট কনসেপ্টস)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-concepts",
    "keywords": "deployment concepts ডিপ্লয়মেন্ট কনসেপ্টস dep-concepts প্রসেস রিস্টার্ট, মেমরি ইউটিলাইজেশন, রেপ্লিকেশন ও স্কেলিং ধারণা",
    "excerpt": "ডিপ্লয়মেন্ট কনসেপ্টস (Deployment Concepts): প্রসেস রিস্টার্ট, মেমরি ইউটিলাইজেশন, রেপ্লিকেশন ও স্কেলিং ধারণা।"
  },
  {
    "title": "৮৮. Deploy FastAPI on Cloud Providers (ক্লাউড প্রোভাইডারে ডিপ্লয়)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-cloud-providers",
    "keywords": "deploy fastapi on cloud providers ক্লাউড প্রোভাইডারে ডিপ্লয় dep-cloud-providers aws, gcp, azure, digitalocean, railway, render-এ ডিপ্লয়মেন্ট",
    "excerpt": "ক্লাউড প্রোভাইডারে ডিপ্লয় (Deploy FastAPI on Cloud Providers): AWS, GCP, Azure, DigitalOcean, Railway, Render-এ ডিপ্লয়মেন্ট।"
  },
  {
    "title": "৮৯. Server Workers – Uvicorn with Workers (সার্ভার ওয়ার্কার্স – Uvicorn with Workers)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-server-workers",
    "keywords": "server workers – uvicorn with workers সার্ভার ওয়ার্কার্স – uvicorn with workers dep-server-workers মাল্টিপল cpu কোর ব্যবহারের জন্য gunicorn/uvicorn মাল্টি-প্রসেস কনফিগ",
    "excerpt": "সার্ভার ওয়ার্কার্স – Uvicorn with Workers (Server Workers – Uvicorn with Workers): মাল্টিপল CPU কোর ব্যবহারের জন্য Gunicorn/Uvicorn মাল্টি-প্রসেস কনফিগ।"
  },
  {
    "title": "৯০. FastAPI in Containers – Docker (ডকার কন্টেইনারে FastAPI)",
    "category": "Deployment (ডিপ্লয়মেন্ট)",
    "url": "../learn/#dep-docker",
    "keywords": "fastapi in containers – docker ডকার কন্টেইনারে fastapi dep-docker dockerfile মাল্টি-স্টেজ বিল্ড, অপটিমাইজড ইমেজ ও কন্টেইনারাইজেশন",
    "excerpt": "ডকার কন্টেইনারে FastAPI (FastAPI in Containers – Docker): Dockerfile মাল্টি-স্টেজ বিল্ড, অপটিমাইজড ইমেজ ও কন্টেইনারাইজেশন।"
  },
  {
    "title": "৯১. FastAPI Class (FastAPI Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#fastapi-class",
    "keywords": "fastapi class fastapi class fastapi-class মূল fastapi অ্যাপ্লিকেশন ক্লাসের কনস্ট্রাক্টর, প্যারামিটার ও মেথডস",
    "excerpt": "FastAPI Class (FastAPI Class): মূল FastAPI অ্যাপ্লিকেশন ক্লাসের কনস্ট্রাক্টর, প্যারামিটার ও মেথডস।"
  },
  {
    "title": "৯২. Request Parameters (Request Parameters)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#request-parameters",
    "keywords": "request parameters request parameters request-parameters query, path, body, header, cookie, form, file প্যারামিটার স্পেক্স",
    "excerpt": "Request Parameters (Request Parameters): Query, Path, Body, Header, Cookie, Form, File প্যারামিটার স্পেক্স।"
  },
  {
    "title": "৯৩. Status Codes (Status Codes)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#status-codes",
    "keywords": "status codes status codes status-codes fastapi.status মডিউলের স্ট্যান্ডার্ড http রেসপন্স স্ট্যাটাস কোডসমূহ",
    "excerpt": "Status Codes (Status Codes): fastapi.status মডিউলের স্ট্যান্ডার্ড HTTP রেসপন্স স্ট্যাটাস কোডসমূহ।"
  },
  {
    "title": "৯৪. UploadFile Class (UploadFile Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#uploadfile-class",
    "keywords": "uploadfile class uploadfile class uploadfile-class uploadfile ক্লাসের ফাইল মেথডস (read, write, seek, close) ও প্রোপার্টিজ",
    "excerpt": "UploadFile Class (UploadFile Class): UploadFile ক্লাসের ফাইল মেথডস (read, write, seek, close) ও প্রোপার্টিজ।"
  },
  {
    "title": "৯৫. Exceptions – HTTPException and WebSocketException (Exceptions – HTTPException & WebSocketException)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#exceptions-reference",
    "keywords": "exceptions – httpexception and websocketexception exceptions – httpexception & websocketexception exceptions-reference fastapi এবং starlette এর বিল্ট-ইন এক্সেপশন ক্লাসের রেফারেন্স",
    "excerpt": "Exceptions – HTTPException & WebSocketException (Exceptions – HTTPException and WebSocketException): FastAPI এবং Starlette এর বিল্ট-ইন এক্সেপশন ক্লাসের রেফারেন্স।"
  },
  {
    "title": "৯৬. Dependencies – Depends() and Security() (Dependencies – Depends() and Security())",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#depends-reference",
    "keywords": "dependencies – depends() and security() dependencies – depends() and security() depends-reference depends এবং security ফাংশনের আর্গুমেন্টস, স্কোপস ও ব্যবহারবিধি",
    "excerpt": "Dependencies – Depends() and Security() (Dependencies – Depends() and Security()): Depends এবং Security ফাংশনের আর্গুমেন্টস, স্কোপস ও ব্যবহারবিধি।"
  },
  {
    "title": "৯৭. APIRouter Class (APIRouter Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#apirouter-class",
    "keywords": "apirouter class apirouter class apirouter-class apirouter ক্লাসের কনস্ট্রাক্টর, রাউটিং মেথডস ও ইনক্লুড অপশনস",
    "excerpt": "APIRouter Class (APIRouter Class): APIRouter ক্লাসের কনস্ট্রাক্টর, রাউটিং মেথডস ও ইনক্লুড অপশনস।"
  },
  {
    "title": "৯৮. Background Tasks (Background Tasks)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#background-tasks",
    "keywords": "background tasks background tasks background-tasks starlette.background.backgroundtasks ক্লাসের মেথডস ও বিহেভিয়ার",
    "excerpt": "Background Tasks (Background Tasks): starlette.background.BackgroundTasks ক্লাসের মেথডস ও বিহেভিয়ার।"
  },
  {
    "title": "৯৯. Request Class (Request Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#request-class",
    "keywords": "request class request class request-class starlette.requests.request ক্লাসের অ্যাট্রিবিউটস (client, headers, query_params)",
    "excerpt": "Request Class (Request Class): starlette.requests.Request ক্লাসের অ্যাট্রিবিউটস (client, headers, query_params)।"
  },
  {
    "title": "১০০. WebSockets (WebSockets)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#websockets",
    "keywords": "websockets websockets websockets starlette.websockets.websocket ক্লাসের সেন্ড/রিসিভ api রেফারেন্স",
    "excerpt": "WebSockets (WebSockets): starlette.websockets.WebSocket ক্লাসের সেন্ড/রিসিভ API রেফারেন্স।"
  },
  {
    "title": "১০১. HTTPConnection Class (HTTPConnection Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#http-connection",
    "keywords": "httpconnection class httpconnection class http-connection http রিকোয়েস্ট ও ওয়েবসকেট কানেকশনের কমন বেস ক্লাস",
    "excerpt": "HTTPConnection Class (HTTPConnection Class): HTTP রিকোয়েস্ট ও ওয়েবসকেট কানেকশনের কমন বেস ক্লাস।"
  },
  {
    "title": "১০২. Response Class (Response Class)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#response-class",
    "keywords": "response class response class response-class বেস response ক্লাসের কনস্ট্রাক্টর, হেডার্স ও মিডিয়া টাইপ কনফিগ",
    "excerpt": "Response Class (Response Class): বেস Response ক্লাসের কনস্ট্রাক্টর, হেডার্স ও মিডিয়া টাইপ কনফিগ।"
  },
  {
    "title": "১০৩. Custom Response Classes (Custom Response Classes)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#custom-responses",
    "keywords": "custom response classes custom response classes custom-responses htmlresponse, jsonresponse, streamingresponse, fileresponse স্পেসিফিকেশন",
    "excerpt": "Custom Response Classes (Custom Response Classes): HTMLResponse, JSONResponse, StreamingResponse, FileResponse স্পেসিফিকেশন।"
  },
  {
    "title": "১০৪. Server-Sent Events (Server-Sent Events)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#server-sent-events",
    "keywords": "server-sent events server-sent events server-sent-events eventsourceresponse এবং serversentevent ক্লাসের রেফারেন্স",
    "excerpt": "Server-Sent Events (Server-Sent Events): EventSourceResponse এবং ServerSentEvent ক্লাসের রেফারেন্স।"
  },
  {
    "title": "১০৫. Middleware (Middleware)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#middleware",
    "keywords": "middleware middleware middleware বিল্ট-ইন মিডলওয়্যার ক্লাসসমূহ (corsmiddleware, httpsredirectmiddleware)",
    "excerpt": "Middleware (Middleware): বিল্ট-ইন মিডলওয়্যার ক্লাসসমূহ (CORSMiddleware, HTTPSRedirectMiddleware)।"
  },
  {
    "title": "১০৬. OpenAPI (OpenAPI)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#openapi",
    "keywords": "openapi openapi openapi fastapi.openapi মডিউলের ইউটিলিটি ফাংশন ও স্কিমা জেনারেশন",
    "excerpt": "OpenAPI (OpenAPI): fastapi.openapi মডিউলের ইউটিলিটি ফাংশন ও স্কিমা জেনারেশন।"
  },
  {
    "title": "১০৭. OpenAPI Docs (OpenAPI Docs)",
    "category": "Reference (রেফারেন্স)",
    "url": "../reference/#openapi-docs",
    "keywords": "openapi docs openapi docs openapi-docs swagger ui ও redoc এর কাস্টম html রেন্ডারিং হেল্পার ফাংশনস",
    "excerpt": "OpenAPI Docs (OpenAPI Docs): Swagger UI ও ReDoc এর কাস্টম HTML রেন্ডারিং হেল্পার ফাংশনস।"
  }
];


function initSearch() {
  const searchBtn = document.querySelector('.md-search__button') || 
                    document.querySelector('label[for="__search"]') ||
                    document.querySelector('.md-search');
  
  // Create search modal HTML
  const modal = document.createElement('div');
  modal.className = 'search-modal-backdrop';
  modal.innerHTML = `
    <div class="search-modal-box">
      <div class="search-modal-input-wrap">
        <svg viewBox="0 0 24 24"><path d="M9.5 3A6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.56 4.23l.27.27h.79l5 5-1.5 1.5-5-5v-.79l-.27-.27A6.52 6.52 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3m0 2C7 5 5 7 5 9.5S7 14 9.5 14 14 12 14 9.5 12 5 9.5 5"/></svg>
        <input type="text" class="search-modal-input" placeholder="ডকুমেন্টেশন সার্চ করুন... (Search docs in Bangla/English)" autofocus>
        <button class="search-modal-close" title="Close (Esc)">ESC</button>
      </div>
      <div class="search-results-list"></div>
    </div>
  `;
  document.body.appendChild(modal);

  const input = modal.querySelector('.search-modal-input');
  const resultsContainer = modal.querySelector('.search-results-list');
  const closeBtn = modal.querySelector('.search-modal-close');

  function openSearch() {
    modal.classList.add('open');
    input.value = '';
    renderSearchResults('');
    input.focus();
  }

  function closeSearch() {
    modal.classList.remove('open');
  }

  if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openSearch();
    });
  }

  closeBtn.addEventListener('click', closeSearch);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeSearch();
  });

  // Keyboard shortcut: '/' or 'Cmd+K' / 'Ctrl+K'
  window.addEventListener('keydown', (e) => {
    if ((e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') ||
        ((e.metaKey || e.ctrlKey) && e.key === 'k')) {
      e.preventDefault();
      openSearch();
    } else if (e.key === 'Escape' && modal.classList.contains('open')) {
      closeSearch();
    }
  });

  input.addEventListener('input', (e) => {
    renderSearchResults(e.target.value.trim());
  });

  function renderSearchResults(query) {
    resultsContainer.innerHTML = '';
    const q = query.toLowerCase();

    const filtered = q === '' 
      ? searchIndex.slice(0, 7)
      : searchIndex.filter(item => {
          return item.title.toLowerCase().includes(q) ||
                 item.keywords.toLowerCase().includes(q) ||
                 item.excerpt.toLowerCase().includes(q);
        });

    if (filtered.length === 0) {
      resultsContainer.innerHTML = `
        <div class="search-empty">
          কোন ফলাফল পাওয়া যায়নি ("${query}")। অন্য কোনো শব্দ দিয়ে খুঁজুন।
        </div>
      `;
      return;
    }

    filtered.forEach(item => {
      const a = document.createElement('a');
      a.className = 'search-result-item';
      a.href = item.url;

      // Adjust relative link based on current path
      const currentPath = window.location.pathname;
      let finalUrl = item.url;
      if (currentPath.includes('/learn') && item.url.startsWith('../learn/')) {
        finalUrl = item.url.replace('../learn/', './');
      } else if (currentPath.includes('/reference') && item.url.startsWith('../reference/')) {
        finalUrl = item.url.replace('../reference/', './');
      } else if (!currentPath.includes('/learn') && !currentPath.includes('/reference')) {
        if (item.url.startsWith('../learn/')) finalUrl = item.url.replace('../learn/', './learn/');
        if (item.url.startsWith('../reference/')) finalUrl = item.url.replace('../reference/', './reference/');
      }

      a.href = finalUrl;
      a.addEventListener('click', () => closeSearch());

      let titleHtml = item.title;
      let excerptHtml = item.excerpt;

      if (q !== '') {
        const regex = new RegExp(`(${q.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')})`, 'gi');
        titleHtml = titleHtml.replace(regex, '<mark>$1</mark>');
        excerptHtml = excerptHtml.replace(regex, '<mark>$1</mark>');
      }

      a.innerHTML = `
        <div class="search-result-category">${item.category}</div>
        <div class="search-result-title">${titleHtml}</div>
        <div class="search-result-excerpt">${excerptHtml}</div>
      `;
      resultsContainer.appendChild(a);
    });
  }
}

// --- 5. Scrollspy for Secondary TOC ---
function initScrollspy() {
  const headings = document.querySelectorAll('.md-content h1, .md-content h2, .md-content h3');
  const tocLinks = document.querySelectorAll('.md-nav--secondary .md-nav__link');

  if (headings.length === 0 || tocLinks.length === 0) return;

  window.addEventListener('scroll', () => {
    let currentId = '';
    const scrollPos = window.scrollY + 120;

    headings.forEach(heading => {
      if (heading.offsetTop <= scrollPos) {
        currentId = heading.getAttribute('id');
      }
    });

    tocLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href === `#${currentId}`) {
        tocLinks.forEach(l => l.classList.remove('md-nav__link--active'));
        link.classList.add('md-nav__link--active');
      }
    });
  }, { passive: true });
}

// --- 6. Mobile Drawer Toggle ---
function initMobileDrawer() {
  const drawerToggle = document.getElementById('__drawer');
  const overlay = document.querySelector('.md-overlay');
  const sidebarLinks = document.querySelectorAll('.md-sidebar--primary .md-nav__link');

  if (overlay && drawerToggle) {
    overlay.addEventListener('click', () => {
      drawerToggle.checked = false;
    });
  }

  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 1220 && drawerToggle) {
        drawerToggle.checked = false;
      }
    });
  });
}

// --- 7. Termynal Initialization ---
function initTermynal() {
  const termyElements = document.querySelectorAll('[data-termynal]');
  termyElements.forEach(el => {
    el.style.opacity = '1';
  });
}
