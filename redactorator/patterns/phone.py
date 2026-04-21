"""Phone number patterns and label-aware regexes."""

import re

from .base import PatternGroup

# Labels that indicate a phone number.
PHONE_LABEL = r"\b(?:phone|phone\s*no|tel|telephone|mobile|cell)\b"

# Common US-style phone numbers with optional country code and separators.
PHONE_VALUE = r"(?:\+?1[\s\-\.]?)?(?:\(\d{3}\)|\d{3})[\s\-\.]?\d{3}[\s\-\.]?\d{4}"


PHONE_LABELED_PATTERN = re.compile(rf"(?i){PHONE_LABEL}(?:\s*[:#]\s*|\s+){PHONE_VALUE}")
PHONE_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{PHONE_LABEL}(?:\s*[:#]\s*|\s+))(?P<value>{PHONE_VALUE})"
)

PHONE_UNLABELED_PATTERN = re.compile(rf"(?i)\b{PHONE_VALUE}\b")
PHONE_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>{PHONE_VALUE})")

PHONE_GROUP = PatternGroup(
    name="phones",
    labeled_patterns=[PHONE_LABELED_PATTERN],
    redact_patterns=[PHONE_LABELED_REDACT_PATTERN],
    unlabeled_pattern=PHONE_UNLABELED_PATTERN,
    redact_unlabeled_pattern=PHONE_UNLABELED_REDACT_PATTERN,
)
