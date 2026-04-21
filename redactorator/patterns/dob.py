"""DOB-related regex configuration and compiled patterns."""

import re

from .base import PatternGroup

# Labels that strongly imply a birthdate (avoid false positives like incident dates).
DOB_LABEL = (
    r"\b(?:d\.?\s*o\.?\s*b\.?|d\/o\/b|dob|date\s*of\s*birth|"
    r"birth\s*date|birthdate|birthday)(?=\b|\W)"
)
# Common phrasing for birthdates.
BORN_PHRASE = r"\b(?:born\s+on|was\s+born(?:\s+on)?|born)\b"

# Numeric date formats.
DATE_NUMERIC_US = r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b"
DATE_NUMERIC_ISO = r"\b\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}\b"

# Month-name based date formats (Jan 1, 1980 | 1 Jan 1980 | January 1st 1980).
MONTH_NAME = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DAY_ORDINAL = r"\d{1,2}(?:st|nd|rd|th)?"
DATE_TEXTUAL_MD = rf"\b{MONTH_NAME}\s+{DAY_ORDINAL},?\s+\d{{2,4}}\b"
DATE_TEXTUAL_DM = rf"\b{DAY_ORDINAL}\s+{MONTH_NAME}\s+\d{{2,4}}\b"

# Only match dates when they appear with birthdate context (label or born-phrase).
DOB_DATE = rf"(?:{DATE_NUMERIC_US}|{DATE_NUMERIC_ISO}|{DATE_TEXTUAL_MD}|{DATE_TEXTUAL_DM})"

DOB_LABELED_PATTERN = re.compile(rf"(?i){DOB_LABEL}\s*[:\-]?\s*{DOB_DATE}")
DOB_BORN_PATTERN = re.compile(rf"(?i){BORN_PHRASE}\s+{DOB_DATE}")

# Capture label/phrase separately to preserve it during redaction.
DOB_LABELED_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{DOB_LABEL}\s*[:\-]?\s*)(?P<value>{DOB_DATE})"
)
DOB_BORN_REDACT_PATTERN = re.compile(
    rf"(?i)(?P<label>{BORN_PHRASE}\s+)(?P<value>{DOB_DATE})"
)

# Aggressive mode: match DOB-like dates without labels.
DOB_UNLABELED_PATTERN = re.compile(rf"(?i){DOB_DATE}")
DOB_UNLABELED_REDACT_PATTERN = re.compile(rf"(?i)(?P<value>{DOB_DATE})")

DOB_GROUP = PatternGroup(
    name="dobs",
    labeled_patterns=[DOB_LABELED_PATTERN, DOB_BORN_PATTERN],
    redact_patterns=[DOB_LABELED_REDACT_PATTERN, DOB_BORN_REDACT_PATTERN],
    unlabeled_pattern=DOB_UNLABELED_PATTERN,
    redact_unlabeled_pattern=DOB_UNLABELED_REDACT_PATTERN,
)
