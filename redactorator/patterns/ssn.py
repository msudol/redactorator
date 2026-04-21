"""SSN/social security number patterns."""

import re

from .base import PatternGroup

# Variants of labels that indicate an SSN or social security number.

SSN_LABEL = r"\b(?:ssn|ss|social\s*security|social\s*security\s*no|social\s*security\s*number|soc\.?\s*sec\.?|soc\s*no)\b"

# SSN value: 3-2-4 with optional separators or 9 digits contiguous.
SSN_VALUE = r"(?:\d{3}[- ]?\d{2}[- ]?\d{4}|\d{9})"

SSN_LABELED_PATTERN = re.compile(rf"(?i){SSN_LABEL}(?:\s*[:#]\s*|\s+){SSN_VALUE}")
SSN_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{SSN_LABEL}(?:\s*[:#]\s*|\s+))(?P<value>{SSN_VALUE})"
)

# Aggressive unlabeled detection (9 digits or 3-2-4).
SSN_UNLABELED_PATTERN = re.compile(rf"(?i)\b{SSN_VALUE}\b")
SSN_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>{SSN_VALUE})")

SSN_GROUP = PatternGroup(
    name="ssns",
    labeled_patterns=[SSN_LABELED_PATTERN],
    redact_patterns=[SSN_LABELED_REDACT_PATTERN],
    unlabeled_pattern=SSN_UNLABELED_PATTERN,
    redact_unlabeled_pattern=SSN_UNLABELED_REDACT_PATTERN,
)
