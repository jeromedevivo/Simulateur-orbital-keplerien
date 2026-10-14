"""Display unit conversion for telemetry."""


class UnitSystem:
    """Convert internal kilometres and km/s to a display system."""

    def __init__(self, name: str = "scientific"):
        if name not in {"scientific", "metric"}:
            raise ValueError("Unknown unit system")
        self.name = name
        self.distance_factor = 1.0 if name == "scientific" else 1000.0
        self.speed_factor = self.distance_factor
        self.distance_label = "km" if name == "scientific" else "m"
        self.speed_label = "km/s" if name == "scientific" else "m/s"

    def distance(self, kilometres: float) -> float:
        return kilometres * self.distance_factor

    def speed(self, kilometres_per_second: float) -> float:
        return kilometres_per_second * self.speed_factor
