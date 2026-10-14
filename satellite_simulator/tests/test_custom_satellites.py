import json

import pytest

from satellite_simulator.data.custom_satellite import (
    CustomSatelliteStore,
    create_custom_satellite,
)


def test_custom_satellite_uses_perigee_and_apogee_to_derive_elements():
    satellite = create_custom_satellite(
        name="Demo",
        perigee_altitude=400,
        apogee_altitude=800,
        inclination=51.6,
        raan=10,
        arg_perigee=20,
        true_anomaly=30,
    )

    assert satellite.name == "Demo"
    assert satellite.semi_major_axis == pytest.approx(6_978.14)
    assert satellite.eccentricity == pytest.approx(400 / (2 * 6_978.14))


def test_custom_satellite_rejects_apogee_below_perigee():
    with pytest.raises(ValueError, match="Apogee"):
        create_custom_satellite("Invalid", 800, 400, 0, 0, 0, 0)


def test_custom_satellite_rejects_atmospheric_intersection():
    with pytest.raises(ValueError, match="atmosphere"):
        create_custom_satellite("Low", 50, 400, 0, 0, 0, 0)


def test_custom_satellite_store_round_trips_json(tmp_path):
    store = CustomSatelliteStore(tmp_path / "satellites.json")
    satellite = create_custom_satellite("Demo", 400, 800, 0, 0, 0, 0)

    store.save([satellite])
    restored = store.load()

    assert len(restored) == 1
    assert restored[0].name == "Demo"
    assert json.loads((tmp_path / "satellites.json").read_text())["satellites"]
