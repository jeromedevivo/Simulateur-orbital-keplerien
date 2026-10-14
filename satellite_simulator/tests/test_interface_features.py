import pytest

from satellite_simulator.core.simulation import SimulationClock
from satellite_simulator.data.satellite_database import SatelliteDatabase
from satellite_simulator.data.custom_satellite import create_custom_satellite
from satellite_simulator.utils.units import UnitSystem


def test_unit_system_converts_distance_and_speed():
    metric = UnitSystem("metric")

    assert metric.distance(6378.14) == pytest.approx(6_378_140)
    assert metric.speed(7.8) == pytest.approx(7_800)
    assert metric.distance_label == "m"
    assert metric.speed_label == "m/s"


def test_unit_system_supports_scientific_kilometres():
    scientific = UnitSystem("scientific")

    assert scientific.distance(6378.14) == pytest.approx(6378.14)
    assert scientific.speed(7.8) == pytest.approx(7.8)
    assert scientific.distance_label == "km"
    assert scientific.speed_label == "km/s"


def test_database_rejects_duplicate_names_without_replacing_satellite():
    database = SatelliteDatabase()
    first = create_custom_satellite("Demo", 400, 800, 0, 0, 0, 0)
    second = create_custom_satellite("Demo", 500, 900, 0, 0, 0, 0)

    assert database.add_satellite(first) is True
    assert database.add_satellite(second) is False
    assert database.get_satellite("Demo") is first


def test_clock_supports_precise_fractional_time_scales():
    clock = SimulationClock(time_scale=0.01)

    clock.advance(100)

    assert clock.time_seconds == pytest.approx(1.0)
