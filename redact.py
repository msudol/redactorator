"""Human-auditable regex helpers for common sensitive identifiers.

This module focuses on explicit, labeled matches for DOBs and SSNs to reduce
false positives. Helper functions expose a small API for finding or detecting
matches without touching raw regex patterns.
"""

from typing import Dict

from patterns.base import MaskMode, PatternGroup, PatternMode
from patterns.dob import DOB_GROUP
from patterns.phone import PHONE_GROUP
from patterns.ssn import SSN_GROUP
from patterns.ids import IDS_GROUP

PATTERNS: Dict[str, PatternGroup] = {
    "dobs": DOB_GROUP,
    "phones": PHONE_GROUP,
    "ssns": SSN_GROUP,
    "ids": IDS_GROUP,
}

PATTERN_ORDER = (DOB_GROUP, PHONE_GROUP, SSN_GROUP, IDS_GROUP)


def find_all(text: str, mode: PatternMode = "strict") -> Dict[str, list[str]]:
    """Return all matches grouped by type."""
    return {name: group.find(text, mode=mode) for name, group in PATTERNS.items()}


def redact_all(
    text: str,
    mask: str = "***",
    mask_mode: MaskMode = "fixed",
    mask_char: str = "*",
    mode: PatternMode = "strict",
) -> str:
    """Redact all supported identifiers using the configured patterns."""
    for group in PATTERN_ORDER:
        text = group.redact(text, mask=mask, mask_mode=mask_mode, mask_char=mask_char, mode=mode)
    return text

