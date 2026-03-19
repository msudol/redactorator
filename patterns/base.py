"""Shared pattern group utilities for matching and redaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Literal, Optional
import re

PatternMode = Literal["strict", "aggressive"]
MaskMode = Literal["fixed", "length"]


@dataclass(frozen=True)
class PatternGroup:
    name: str
    labeled_patterns: List[re.Pattern]
    redact_patterns: List[re.Pattern]
    unlabeled_pattern: Optional[re.Pattern] = None
    redact_unlabeled_pattern: Optional[re.Pattern] = None

    def find(self, text: str, mode: PatternMode = "strict") -> List[str]:
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
        def replace(match: re.Match) -> str:
            value = match.group("value")
            redacted = _build_mask(value, mask, mask_mode, mask_char)
            label = match.groupdict().get("label", "")
            return f"{label}{redacted}"

        for pattern in self.redact_patterns:
            text = pattern.sub(replace, text)

        if mode == "aggressive" and self.redact_unlabeled_pattern:
            text = self.redact_unlabeled_pattern.sub(
                lambda match: _build_mask(match.group("value"), mask, mask_mode, mask_char),
                text,
            )
        return text


def _build_mask(value: str, mask: str, mode: MaskMode, mask_char: str) -> str:
    if mode == "fixed":
        return mask
    if mode == "length":
        return mask_char * len(value)
    raise ValueError(f"Unsupported mask mode: {mode}")


def _overlaps_any(span: tuple[int, int], spans: Iterable[tuple[int, int]]) -> bool:
    return any(span[0] < other[1] and other[0] < span[1] for other in spans)
