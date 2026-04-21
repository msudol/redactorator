"""SSN-related regex configuration and compiled patterns."""

import re

from .base import PatternGroup

# Labels that indicate an SSN is being presented (keep explicit to avoid noise).
SSN_LABEL = (
    r"\b(?:"
    r"ssn|"
    r"ss\s*#|"
    r"soc\s*no|"
    r"soc\s*#|"
    r"social\s*security(?:\s*number)?|"
    r"social\s*security\s*#"
    r")(?:\b|\W)"
)

# 9-digit SSN formats:
# - 123-45-6789
# - 123 45 6789
# - 123456789
SSN_NUMBER = r"\b\d{3}(?:[- ]?\d{2})(?:[- ]?\d{4})\b"

# Only match SSNs when they are clearly labeled (strict mode).
SSN_LABELED_PATTERN = re.compile(rf"(?i){SSN_LABEL}\s*[:\-]?\s*{SSN_NUMBER}")

# Aggressive mode: match the SSN number even without labels.
SSN_UNLABELED_PATTERN = re.compile(rf"(?i){SSN_NUMBER}")

# Capture label separately so only the number is masked.
SSN_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{SSN_LABEL}\s*[:\-]?\s*)(?P<value>{SSN_NUMBER})"
)

# Capture the number for aggressive redaction.
SSN_UNLABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<value>{SSN_NUMBER})"
)

SSN_GROUP = PatternGroup(
    name="ssns",
    labeled_patterns=[SSN_LABELED_PATTERN],
    redact_patterns=[SSN_LABELED_REDACT_PATTERN],
    unlabeled_pattern=SSN_UNLABELED_PATTERN,
    redact_unlabeled_pattern=SSN_UNLABELED_REDACT_PATTERN,
)
