"""Generic identifier (ID) patterns grouped as a PatternGroup.

This is a conservative set of labeled patterns (e.g., "ID: 12345") plus
some cautious unlabeled heuristics used in aggressive mode. The goal is to
catch common "ID-like" fields without producing many false positives.
"""

import re

from .base import PatternGroup

# Label variants that commonly indicate an identifier field. Keep these
# conservative so we don't match arbitrary words like "idaho".
ID_LABEL = r"\b(?:id|identification|identifier|member\s*id|user\s*id|emp\.?\s*id|passport|driver(?:'s)?\s*license|dl|license)\b"

# Value patterns: alphanumeric tokens of length 4-16, optionally with dashes.
# Avoid matching short numbers (like years) by requiring at least 4 chars.
ID_VALUE = r"[A-Za-z0-9\-]{4,16}"

ID_LABELED_PATTERN = re.compile(rf"(?i){ID_LABEL}(?:\s*[:#]\s*|\s+){ID_VALUE}")
ID_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{ID_LABEL}(?:\s*[:#]\s*|\s+))(?P<value>{ID_VALUE})"
)

# Aggressive unlabeled heuristics: long alphanumeric tokens or tokens with
# a mix of letters and digits often indicate IDs. We restrict length to avoid
# matching years or short codes.
ID_UNLABELED_PATTERN = re.compile(rf"(?i)\b(?:[A-Za-z0-9]{{6,}})\b")
ID_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>[A-Za-z0-9]{{6,}})")

IDS_GROUP = PatternGroup(
    name="ids",
    labeled_patterns=[ID_LABELED_PATTERN],
    redact_patterns=[ID_LABELED_REDACT_PATTERN],
    unlabeled_pattern=ID_UNLABELED_PATTERN,
    redact_unlabeled_pattern=ID_UNLABELED_REDACT_PATTERN,
)
