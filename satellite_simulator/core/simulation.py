"""Time control primitives for the live orbital simulation."""


class SimulationClock:
    """Deterministic simulation clock driven by elapsed wall-clock seconds."""

    def __init__(self, time_seconds: float = 0.0, time_scale: float = 1.0):
        self.time_seconds = float(time_seconds)
        self.time_scale = float(time_scale)
        self.is_running = True

    def advance(self, elapsed_seconds: float) -> float:
        if self.is_running:
            self.time_seconds += float(elapsed_seconds) * self.time_scale
        return self.time_seconds

    def set_time_scale(self, time_scale: float) -> None:
        if not isinstance(time_scale, (int, float)):
            raise TypeError("time_scale must be numeric")
        self.time_scale = float(time_scale)

    def pause(self) -> None:
        self.is_running = False

    def resume(self) -> None:
        self.is_running = True

    def reset(self) -> None:
        self.time_seconds = 0.0
