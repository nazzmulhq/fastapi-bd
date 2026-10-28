# Pydantic Settings { #pydantic-settings }

/// note | এই পেজে যা পাবেন

* `pydantic_settings` প্যাকেজের প্রধান ক্লাসগুলোর দ্রুত সারণি: `BaseSettings`, `SettingsConfigDict`, settings source, CLI টুল, annotation।
* সবশেষে স্বয়ংক্রিয়ভাবে তৈরি পূর্ণ API তালিকা।

///

## এক নজরে { #bn-overview }

ধারণা আর বিস্তারিত উদাহরণ: [Settings Management](../concepts/pydantic_settings.md)। এই পেজ দ্রুত খোঁজার জন্য।

### মূল ক্লাস { #bn-core }

| সদস্য | কী করে |
| --- | --- |
| `BaseSettings` | settings মডেলের ভিত্তি; environment, `.env`, secret ইত্যাদি থেকে মান পড়ে |
| `SettingsConfigDict` | `model_config`-এর জন্য `ConfigDict` + settings-এর বাড়তি key (নিচে দেখুন) |
| `settings_customise_sources()` | classmethod; source-গুলোর ক্রম বদলানো, যোগ বা বাদ |
| `settings_cached()` / `settings_clear_cache()` | প্রতি ক্লাসে একটি cache করা instance |

`SettingsConfigDict`-এর প্রচলিত key:

| key | কী করে |
| --- | --- |
| `env_prefix` | সব environment variable-এর prefix, যেমন `'APP_'` |
| `env_file`, `env_file_encoding` | `.env` ফাইল(গুলো) আর encoding |
| `env_nested_delimiter`, `env_nested_max_split` | নেস্টেড মডেলের জন্য বিভাজক, যেমন `'__'` |
| `case_sensitive` | নামে বড়-ছোট হাতের পার্থক্য ধরবে কিনা |
| `env_ignore_empty` | খালি environment variable উপেক্ষা |
| `env_parse_none_str` | কোন লেখা `None` হবে, যেমন `'null'` |
| `secrets_dir` | secret ফাইলের ফোল্ডার |
| `cli_parse_args` | কমান্ড লাইন আর্গুমেন্ট পড়া চালু |
| `json_file`, `toml_file`, `yaml_file`, `pyproject_toml_table_header` | কনফিগ ফাইলের source-এর জন্য |
| `nested_model_default_partial_update` | নেস্টেড ডিফল্টে আংশিক আপডেট |
| `enable_decoding` | জটিল মানে JSON পার্সিং চালু/বন্ধ |

### settings source { #bn-sources }

| ক্লাস | কোথা থেকে পড়ে |
| --- | --- |
| `InitSettingsSource` | `Settings(...)`-এ দেওয়া আর্গুমেন্ট |
| `EnvSettingsSource` | environment variable |
| `DotEnvSettingsSource` | `.env` ফাইল |
| `SecretsSettingsSource`, `NestedSecretsSettingsSource` | secret ফাইলের ফোল্ডার |
| `CliSettingsSource` | কমান্ড লাইন |
| `JsonConfigSettingsSource`, `TomlConfigSettingsSource`, `YamlConfigSettingsSource`, `PyprojectTomlConfigSettingsSource` | কনফিগ ফাইল |
| `AWSSecretsManagerSettingsSource`, `AWSSystemsManagerSettingsSource`, `AzureKeyVaultSettingsSource`, `GoogleSecretManagerSettingsSource` | ক্লাউডের secret store |
| `PydanticBaseSettingsSource` | নিজের source বানানোর ভিত্তি ক্লাস |

### CLI আর annotation { #bn-cli }

| সদস্য | কী করে |
| --- | --- |
| `CliApp.run(model, cli_args=...)`, `CliApp.run_subcommand(model)` | মডেলকে CLI অ্যাপ হিসেবে চালানো |
| `CliSubCommand`, `CliPositionalArg`, `get_subcommand()` | subcommand আর positional আর্গুমেন্ট; পার্স হওয়া subcommand পাওয়া |
| `CliVariadicArg` | একটি অপশনের পরে বাকি সব মান (`--param a b c`) |
| `CliImplicitFlag`, `CliExplicitFlag`, `CliToggleFlag`, `CliDualFlag` | boolean ফ্ল্যাগের ধরন |
| `CliSuppress`, `CLI_SUPPRESS`, `CliUnknownArgs`, `CliMutuallyExclusiveGroup` | help লুকানো, অচেনা আর্গুমেন্ট ধরা, পরস্পর-বর্জনশীল দল |
| `NoDecode`, `ForceDecode` | একটি ফিল্ডে JSON পার্সিং বন্ধ / জোর করে চালু |
| `SettingsError` | settings লোডে সমস্যা হলে (যেমন অবৈধ JSON) |

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='SHOP_', env_file='.env', env_nested_delimiter='__')

    debug: bool = False
    port: int = 8000
    database_url: str


settings = Settings()  # SHOP_DATABASE_URL না থাকলে ValidationError
```

## পূর্ণ API তালিকা { #bn-full-api }

⟦CODE1⟧
