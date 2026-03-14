"""
Lightweight timing helper for RAG pipeline instrumentation.
Uses time.perf_counter() for high-precision timing. Backend-only; no API changes.
"""
import time
from typing import Dict, Optional


class StageTimer:
    """
    Tracks named stages with start/end or single mark (duration from last start/mark).
    Produces a structured dict and readable log string.
    """

    def __init__(self) -> None:
        self._starts: Dict[str, float] = {}
        self._durations_ms: Dict[str, int] = {}

    def start(self, stage_name: str) -> None:
        """Start or restart a stage."""
        self._starts[stage_name] = time.perf_counter()

    def end(self, stage_name: str) -> Optional[int]:
        """
        End a stage and record duration in ms. Returns ms or None if stage was not started.
        """
        if stage_name not in self._starts:
            return None
        elapsed = time.perf_counter() - self._starts[stage_name]
        ms = int(round(elapsed * 1000))
        self._durations_ms[stage_name] = ms
        del self._starts[stage_name]
        return ms

    def mark(self, stage_name: str) -> int:
        """
        Record duration for stage_name from its start to now (same as end but always
        expects stage to have been started). Returns duration in ms.
        """
        ms = self.end(stage_name)
        if ms is None:
            return 0
        return ms

    def duration(self, stage_name: str) -> Optional[int]:
        """Return recorded duration in ms for a stage, or None if not yet recorded."""
        return self._durations_ms.get(stage_name)

    def set_duration(self, stage_name: str, ms: int) -> None:
        """Set a duration directly (e.g. merged from another timer)."""
        self._durations_ms[stage_name] = ms

    def merge(self, other: Dict[str, int]) -> None:
        """Merge in durations from another dict (e.g. from retrieval_service)."""
        for k, v in other.items():
            self._durations_ms[k] = v

    def summary(self) -> Dict[str, int]:
        """Return a copy of all recorded durations (ms)."""
        return dict(self._durations_ms)


def format_timing_summary(summary_dict: Dict[str, int], request_id: Optional[str] = None) -> str:
    """
    Produce a readable, one-metric-per-line log string. Prefix with RAG_TIMING.
    If request_id is provided, include it on the first line.
    """
    lines = []
    prefix = "RAG_TIMING"
    if request_id:
        prefix = f"RAG_TIMING request_id={request_id}"
    lines.append(prefix)
    for k in sorted(summary_dict.keys()):
        lines.append(f"{k}={summary_dict[k]}")
    return "\n".join(lines)
