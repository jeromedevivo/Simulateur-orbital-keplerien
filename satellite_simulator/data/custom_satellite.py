"""Creation and persistence of user-defined satellites."""

import json
from pathlib import Path
from typing import Iterable, List, Union

from satellite_simulator.core.satellite import Satellite


EARTH_RADIUS_KM = 6378.14
ATMOSPHERIC_MARGIN_KM = 100.0


def create_custom_satellite(name: str, perigee_altitude: float, apogee_altitude: float,
                            inclination: float, raan: float, arg_perigee: float,
                            true_anomaly: float) -> Satellite:
    if not name or not name.strip():
        raise ValueError("Satellite name is required")
    if perigee_altitude < 0:
        raise ValueError("Perigee altitude cannot be negative")
    if apogee_altitude < perigee_altitude:
        raise ValueError("Apogee must be greater than or equal to perigee")
    if perigee_altitude < ATMOSPHERIC_MARGIN_KM:
        raise ValueError("Perigee intersects the atmosphere (minimum 100 km)")

    perigee = EARTH_RADIUS_KM + float(perigee_altitude)
    apogee = EARTH_RADIUS_KM + float(apogee_altitude)
    semi_major_axis = (perigee + apogee) / 2
    eccentricity = (apogee - perigee) / (apogee + perigee)
    return Satellite(
        name=name.strip(),
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        inclination=float(inclination),
        raan=float(raan),
        arg_perigee=float(arg_perigee),
        true_anomaly=float(true_anomaly),
        epoch=0.0,
    )


class CustomSatelliteStore:
    """JSON persistence for custom satellite orbital elements."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    def save(self, satellites: Iterable[Satellite]) -> None:
        payload = {
            "satellites": [
                satellite.get_orbital_elements() for satellite in satellites
            ]
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self) -> List[Satellite]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [
            Satellite(**data)
            for data in payload.get("satellites", [])
        ]
