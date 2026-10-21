# Emailvet

Provider-aware email address canonicalization for Python.

```python
canon_email("a.b.c.d+123@gmail.com")
# "abcd@gmail.com"
```

## Install

```bash
pip install emailvet
```

## Usage

```python
from emailvet import canon_email, analyze_email

print(canon_email("a.b.c.d+123@gmail.com"))
# abcd@gmail.com

print(canon_email("John.Smith@EXAMPLE.COM"))
# John.Smith@example.com
```

## Supported providers

Emailvet currently includes provider-specific rules for:

- Gmail / Googlemail
- Outlook.com
- Proton Mail
- Yandex Mail
- Fastmail-owned domains

Unknown providers are handled conservatively: only the domain is lowercased.

## Analysis

Use `analyze_email()` when you want to see what Emailvet changed:

```python
result = analyze_email("A.B+shop@googlemail.com")

print(result.canonical)
print(result.provider)
print(result.rules_applied)
```

Example result:

```text
canonical: ab@gmail.com
provider: gmail
rules_applied:
- lowercase_local_part
- strip_subaddress
- ignore_dots
- canonicalize_domain
```

## Rules and updates

Provider rules are bundled with the package, so normal canonicalization works entirely offline.

```python
import emailvet

print(emailvet.rules_version())
print(emailvet.rules_info())
```

To install a newer trusted `providers.json` rules file:

```python
emailvet.update_rules("https://example.com/providers.json")
```

You can also set `EMAILVET_RULES_URL` and call `emailvet.update_rules()` without passing a URL.

## License

MIT
