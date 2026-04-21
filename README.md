# Redactorator

Human-auditable regex helpers for identifying labeled sensitive data like dates of birth (DOB) and Social Security Numbers (SSNs).

## Features

- Labeled DOB detection (e.g., `DOB: 01/02/1980`, `Born on Jan 1, 1980`)
- Labeled SSN detection (e.g., `SSN: 123-45-6789`, `Social Security # 123456789`)
- Labeled phone detection (e.g., `Phone: 123-456-7890`, `Tel: (123) 456-7890`)
- Labeled phone detection (e.g., `Phone: 123-456-7890`, `Tel: (123) 456-7890`)
- Generic labeled ID detection (e.g., `ID: ABC-12345`, `Passport: A1234567`, `Member ID: 123456789`) with an optional aggressive unlabeled mode for long alphanumeric tokens
- Small helper API for matching and detection
- Redaction helpers with fixed or length-based masking

## Usage

```python
import redactorator as redact

text = "DOB: 01/02/1980, Phone: 123-456-7890, SSN: 123-45-6789"

# Find all matches grouped by type
print(redact.find_all(text))

# Redaction (fixed mask)
print(redact.redact_all(text))

# Redaction (length-based mask)
print(redact.redact_all(text, mask_mode="length"))

# Redaction (length-based with custom char)
print(redact.redact_all(text, mask_mode="length", mask_char="#"))

# Pattern groups
dob_group = redact.PATTERNS["dobs"]
print(dob_group.find("DOB: 01/02/1980"))
print(dob_group.contains("DOB: 01/02/1980"))

ssn_group = redact.PATTERNS["ssns"]
print(ssn_group.redact("SSN: 123-45-6789"))
print(ssn_group.find("123-45-6789", mode="aggressive"))

phone_group = redact.PATTERNS["phones"]
print(phone_group.redact("PHONE: 123-456-7890")
print(phone_group.find("123-456-7890", mode="aggressive"))

ids_group = redact.PATTERNS["ids"]
print(ids_group.redact("ID: ABC-12345"))
print(ids_group.find("ABC12345678", mode="aggressive"))
```

## Helper API

- `PATTERNS`: dict of pattern groups (e.g., `PATTERNS["dobs"]`, `PATTERNS["ssns"]`)
- `find_all(text: str, mode: str = "strict") -> Dict[str, List[str]]`
- `redact_all(text: str, mask: str = "***", mask_mode: str = "fixed", mask_char: str = "*", mode: str = "strict") -> str`

### PatternGroup methods

- `find(text: str, mode: str = "strict") -> List[str]`
- `contains(text: str, mode: str = "strict") -> bool`
- `redact(text: str, mask: str = "***", mask_mode: str = "fixed", mask_char: str = "*", mode: str = "strict") -> str`

## Masking options

- `mask_mode="fixed"` uses the provided `mask` string (default: `***`).
- `mask_mode="length"` replaces each character in the matched value with `mask_char`.

## Pattern modes

- `mode="strict"` (default) will only match when a clear label is present.
	(e.g., `DOB:`, `Passport:`, `Phone:`).
- `mode="aggressive"` also matches unlabeled values (DOBs, phones, SSNs).

## Redaction order

`redact_all` applies pattern groups in the order defined by `PATTERN_ORDER` in `redact.py`.

## Adding new pattern modules

1. Create a new module under `patterns/` with a `PatternGroup` instance (e.g., `PHONE_GROUP`).
2. Import and register it in `redact.PATTERNS` and `PATTERN_ORDER`.

## Running tests

```pwsh
C:/Projects/redactorator/.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v
```

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Notes

- Strict mode is the default for all APIs and only matches labeled values.
- To use aggressive mode - call it explicitly:
	- `redact.find_all(text, mode="aggressive")`
	- `redact.redact_all(text, mode="aggressive")`
	- `PATTERNS["dobs"].find(text, mode="aggressive")`
	- `PATTERNS["phones"].contains(text, mode="aggressive")`
	- `PATTERNS["ssns"].redact(text, mode="aggressive")`
	- `PATTERNS["ids"].find(text, mode="aggressive")`
