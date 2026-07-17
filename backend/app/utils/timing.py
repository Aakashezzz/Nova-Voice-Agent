"""Small utilities for measuring and reporting pipeline latency."""
import time
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class StageTimings:
    """Accumulates named stage durations (in milliseconds) for one request."""

    stages: dict[str, float] = field(default_factory=dict)
    _start: float = field(default_factory=time.perf_counter)

    @contextmanager
    def track(self, stage_name: str):
        """Context manager that records how long a block took, in ms."""
        start = time.perf_counter()
        try:
            yield
        finally:
            self.stages[stage_name] = round((time.perf_counter() - start) * 1000, 2)

    @property
    def total_ms(self) -> float:
        return round((time.perf_counter() - self._start) * 1000, 2)

    def as_dict(self) -> dict:
        return {**self.stages, "total_ms": self.total_ms}
