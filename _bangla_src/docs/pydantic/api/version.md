# Version Information { #version-information }

/// note | এই পেজে যা পাবেন

ইনস্টল থাকা Pydantic-এর সংস্করণ জানার উপায়: `pydantic.__version__` আর `pydantic.version.version_info()`।

///

## এক নজরে { #bn-overview }

| সদস্য | কী দেয় |
| --- | --- |
| `pydantic.__version__` / `pydantic.VERSION` | সংস্করণের লেখা, যেমন `'2.14.1'` |
| `pydantic.version.version_short()` | শুধু major.minor, যেমন `'2.14'` |
| `pydantic.version.version_info()` | বাগ রিপোর্টের জন্য বিস্তারিত তথ্য: pydantic, pydantic-core, Python, অপারেটিং সিস্টেম আর সংশ্লিষ্ট প্যাকেজের সংস্করণ |

```bash
python -c "import pydantic.version; print(pydantic.version.version_info())"
```

/// tip | পরামর্শ

GitHub-এ issue খোলার সময় এই কমান্ডের আউটপুট যোগ করুন; রক্ষণাবেক্ষণকারীরা এতে সমস্যা দ্রুত বুঝতে পারেন। দেখুন [সাহায্য পাওয়া](../help_with_pydantic.md)।

///

## পূর্ণ API তালিকা { #bn-full-api }

::: pydantic.__version__
    options:
        show_root_heading: true
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true

::: pydantic.version.version_info
    options:
        show_root_heading: true
        inherited_members: false
        show_if_no_docstring: false
        docstring_options:
          ignore_init_summary: true
