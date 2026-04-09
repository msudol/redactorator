"""Generic ID-like identifier patterns (driver's license, passport, member id, etc.).

This module aims to conservatively match labeled identifier values in strict
mode and provide an optional aggressive unlabeled matcher for longer
alphanumeric tokens. Keep the labeled set intentionally broad but favor
explicit forms like "ID", "Member ID", "Passport", "Driver's License",
"DL", and so on to reduce false positives.
"""

import re

from .base import PatternGroup

# Labels indicating an identifier is being presented. Keep these fairly
# explicit to avoid accidental matches.
ID_LABEL = (
    r"\b(?:"
    r"id|"  # id, id number
    r"id\s*number|"
    r"identifier|"
    r"id\s*#|"
    r"id:|"
    r"member\s*id|"
    r"member|"
    r"policy(?:\s*no)?|"
    r"policy\s*#|"
    r"insurance(?:\s*id|\s*member)?|"
    r"passport|"
    r"driver(?:'s)?\s*license|"
    r"dl|"
    r"lic(?:ense)?\b"
    r")(?:\b|\W)"
)

# ID value: allow alphanumeric tokens with common separators. Require a
# minimal length to avoid matching short numeric tokens (like years).
# We keep a raw pattern (without named groups) and only introduce the
# (?P<value>...) capture at the redact patterns to avoid redefinition
# errors when composing patterns.
ID_VALUE_RAW = r"[A-Za-z0-9][A-Za-z0-9\-\s\/.]{2,18}[A-Za-z0-9]"

# Labeled pattern (strict mode): require an explicit label before the value.
ID_LABELED_PATTERN = re.compile(rf"(?i){ID_LABEL}(?:\s*:\s*|\s+|-\s+)(?:{ID_VALUE_RAW})")

# Labeled redact pattern captures the label separately so we keep the label
# text and only replace the value when redacting.
ID_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{ID_LABEL}(?:\s*:\s*|\s+|-\s+))(?P<value>{ID_VALUE_RAW})"
)

# Aggressive (unlabeled) patterns. These are intentionally conservative:
# - Alphanumeric tokens: 8-20 chars (letters+digits, no spaces) to reduce
#   false positives for short tokens.
# - Mostly-numeric tokens: 6-20 digits.
ID_UNLABELED_RAW = r"\b(?:[A-Z0-9]{8,20}|\d{6,20})\b"
ID_UNLABELED_PATTERN = re.compile(rf"(?i){ID_UNLABELED_RAW}")
ID_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>{ID_UNLABELED_RAW})")


IDS_GROUP = PatternGroup(
    name="ids",
    labeled_patterns=[ID_LABELED_PATTERN],
    redact_patterns=[ID_LABELED_REDACT_PATTERN],
    unlabeled_pattern=ID_UNLABELED_PATTERN,
    redact_unlabeled_pattern=ID_UNLABELED_REDACT_PATTERN,
)
