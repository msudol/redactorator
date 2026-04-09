"""Shared pattern group utilities for matching and redaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Literal, Optional
import re

PatternMode = Literal["strict", "aggressive"]
MaskMode = Literal["fixed", "length"]


@dataclass(frozen=True)
class PatternGroup:
    """A reusable group of related regex patterns for a single identifier
    family.

    Fields:
    - name: logical name for the group (used in `redact.PATTERNS`).
    - labeled_patterns: regexes that only match when an explicit label is
      present (used in strict/default mode).
    - redact_patterns: regexes used for redaction. These should capture a
      named group ``value`` (and optionally ``label``) so redaction can
      preserve the label text while masking only the value.
    - unlabeled_pattern / redact_unlabeled_pattern: optional regexes used
      only when mode="aggressive"; they match values without an explicit
      label and are intentionally conservative to avoid false positives.
    """

    name: str
    labeled_patterns: List[re.Pattern]
    redact_patterns: List[re.Pattern]
    unlabeled_pattern: Optional[re.Pattern] = None
    redact_unlabeled_pattern: Optional[re.Pattern] = None

    def find(self, text: str, mode: PatternMode = "strict") -> List[str]:
        """Return all matched strings for this group.

        Behavior:
        - In "strict" mode (default) returns only matches from
          ``labeled_patterns``.
        - In "aggressive" mode, also returns matches from
          ``unlabeled_pattern`` but only when those matches do not overlap
          any labeled match (to avoid duplicate/overlapping results).

        The return value is a list of raw matched substrings (label + value
        when the labeled pattern includes both).
        """
        labeled_matches = []
        labeled_spans = []
        for pattern in self.labeled_patterns:
            for match in pattern.finditer(text):
                labeled_matches.append(match.group(0))
                labeled_spans.append(match.span())

        if mode == "strict" or not self.unlabeled_pattern:
            return labeled_matches

        unlabeled_matches = []
        for match in self.unlabeled_pattern.finditer(text):
            if not _overlaps_any(match.span(), labeled_spans):
                unlabeled_matches.append(match.group(0))
        return labeled_matches + unlabeled_matches

    def contains(self, text: str, mode: PatternMode = "strict") -> bool:
        """Return True if the text contains any match for this group.

        This is a quick boolean check optimized to stop on the first match.
        In strict mode it checks only the labeled patterns. In aggressive
        mode it will fall back to the unlabeled_pattern if no labeled match
        is found.
        """
        for pattern in self.labeled_patterns:
            if pattern.search(text):
                return True
        if mode == "aggressive" and self.unlabeled_pattern:
            return bool(self.unlabeled_pattern.search(text))
        return False

    def redact(
        self,
        text: str,
        mask: str = "***",
        mask_mode: MaskMode = "fixed",
        mask_char: str = "*",
        mode: PatternMode = "strict",
    ) -> str:
        """Redact all matches for this group from the input text.

        Redaction rules:
        - ``redact_patterns`` are applied first. They are expected to capture
          a named group ``value`` and may capture ``label``. The replacement
          preserves any captured ``label`` and replaces ``value`` with the
          mask (either a fixed string or a length-based mask).
        - If ``mode=="aggressive"`` and ``redact_unlabeled_pattern`` is
          provided, unlabeled matches are also masked.

        Parameters mirror the public API used in `redact.redact_all` so
        callers can control mask shape and mode.
        """
        def replace(match: re.Match) -> str:
            # Extract the captured value (the sensitive portion) and build
            # the replacement mask according to the configured mask_mode.
            value = match.group("value")
            redacted = _build_mask(value, mask, mask_mode, mask_char)
            # If the regex also captured a label group, keep it in the
            # output so redactions remain human-auditable (e.g., "SSN: ***").
            label = match.groupdict().get("label", "")
            return f"{label}{redacted}"

        # Apply the labeled/redact patterns first (this keeps labels intact).
        for pattern in self.redact_patterns:
            text = pattern.sub(replace, text)

        # Optionally apply aggressive unlabeled redaction.
        if mode == "aggressive" and self.redact_unlabeled_pattern:
            text = self.redact_unlabeled_pattern.sub(
                lambda match: _build_mask(match.group("value"), mask, mask_mode, mask_char),
                text,
            )
        return text


def _build_mask(value: str, mask: str, mode: MaskMode, mask_char: str) -> str:
    """Return a mask string for `value`.

    - If mode is "fixed", the provided `mask` string is returned.
    - If mode is "length", the mask is a repeated `mask_char` with the
      same length as the original value (preserving length information).
    """
    if mode == "fixed":
        return mask
    if mode == "length":
        return mask_char * len(value)
    raise ValueError(f"Unsupported mask mode: {mode}")


def _overlaps_any(span: tuple[int, int], spans: Iterable[tuple[int, int]]) -> bool:
    """Return True if `span` overlaps any span in `spans`.

    This is used when combining labeled and unlabeled matches: an unlabeled
    match that overlaps a labeled one should be ignored to avoid duplicate
    or conflicting results.
    """
    return any(span[0] < other[1] and other[0] < span[1] for other in spans)
