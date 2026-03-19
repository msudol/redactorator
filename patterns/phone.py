"""Phone-related regex configuration and compiled patterns."""

import re

from .base import PatternGroup

# Labels that indicate a phone number is being presented.
PHONE_LABEL = (
    r"\b(?:"
    r"phone|"
    r"phone\s*#|"
    r"phone\s*number|"
    r"tel|"
    r"tel\.|"
    r"telephone|"
    r"mobile|"
    r"cell"
    r")(?:\b|\W)"
)

# US-style phone formats:
# - 123-456-7890
# - (123) 456-7890
# - 123.456.7890
# - 123 456 7890
# - 1234567890
# - +1 123 456 7890
PHONE_NUMBER = (
    r"(?:\+?1\s*)?"
    r"(?:\(\d{3}\)|\d{3})"
    r"[\s\.-]?"
    r"\d{3}"
    r"[\s\.-]?"
    r"\d{4}"
)

PHONE_LABELED_PATTERN = re.compile(
    rf"(?i){PHONE_LABEL}\s*[:\-]?\s*(?:{PHONE_NUMBER})"
)

PHONE_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{PHONE_LABEL}\s*[:\-]?\s*)(?P<value>{PHONE_NUMBER})"
)

# Aggressive mode: match phone numbers without labels.
PHONE_UNLABELED_PATTERN = re.compile(rf"(?i){PHONE_NUMBER}")
PHONE_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>{PHONE_NUMBER})")

PHONE_GROUP = PatternGroup(
    name="phones",
    labeled_patterns=[PHONE_LABELED_PATTERN],
    redact_patterns=[PHONE_LABELED_REDACT_PATTERN],
    unlabeled_pattern=PHONE_UNLABELED_PATTERN,
    redact_unlabeled_pattern=PHONE_UNLABELED_REDACT_PATTERN,
)
