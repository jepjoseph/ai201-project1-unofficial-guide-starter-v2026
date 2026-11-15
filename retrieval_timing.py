"""Optional stage-level timing for retrieval operations."""

from contextlib import contextmanager
from time import perf_counter


class RetrievalTiming:
    """Collect elapsed milliseconds by named retrieval stage."""

    def __init__(self):
        self._durations = {}

    @contextmanager
    def measure(self, stage):
        started = perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (perf_counter() - started) * 1000
            self._durations[stage] = (
                self._durations.get(stage, 0.0) + elapsed_ms
            )

    def as_dict(self):
        """Return a JSON-compatible snapshot of recorded durations."""
        return {
            stage: round(duration, 3)
            for stage, duration in self._durations.items()
        }