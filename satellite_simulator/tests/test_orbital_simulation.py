import math

import numpy as np
import pytest

from satellite_simulator.core.orbit_calculator import KeplerOrbit
from satellite_simulator.core.simulation import SimulationClock


def test_position_uses_full_orbital_orientation():
    orbit = KeplerOrbit()

    position = orbit.calculate_position_from_elements(
        semi_major_axis=10_000,
        eccentricity=0.2,
        inclination=45,
        raan=90,
        arg_perigee=30,
        true_anomaly=0,
    )

    assert np.allclose(np.linalg.norm(position), 8_000)
    assert position[0] == pytest.approx(-2_828.4271, abs=1e-3)
    assert position[1] == pytest.approx(6_928.2032, abs=1e-3)
    assert position[2] == pytest.approx(2_828.4271, abs=1e-3)


def test_state_contains_velocity_that_changes_with_distance():
    orbit = KeplerOrbit()

    periapsis = orbit.calculate_state_from_elements(10_000, 0.2, 0, 0, 0, 0)
    apoapsis = orbit.calculate_state_from_elements(10_000, 0.2, 0, 0, 0, 180)

    assert periapsis["speed"] > apoapsis["speed"]
    assert periapsis["radius"] == pytest.approx(8_000)
    assert apoapsis["radius"] == pytest.approx(12_000)
    assert periapsis["velocity"].shape == (3,)


def test_propagation_uses_kepler_equation_and_preserves_orbital_energy():
    orbit = KeplerOrbit()

    initial = orbit.calculate_state_at_time(10_000, 0.6, 0, 0, 0, 0, 0)
    quarter = orbit.calculate_state_at_time(
        10_000, 0.6, 0, 0, 0, 0,
        orbit.calculate_orbital_period(10_000) / 4,
    )

    assert quarter["radius"] != pytest.approx(initial["radius"])
    assert quarter["speed"] != pytest.approx(initial["speed"])
    assert initial["specific_energy"] == pytest.approx(
        quarter["specific_energy"], abs=1e-10)


def test_propagation_completes_one_orbit():
    orbit = KeplerOrbit()
    period = orbit.calculate_orbital_period(10_000)

    start = orbit.calculate_state_at_time(10_000, 0.2, 10, 20, 30, 45, 0)
    end = orbit.calculate_state_at_time(10_000, 0.2, 10, 20, 30, 45, period)

    assert np.allclose(start["position"], end["position"], atol=1e-6)
    assert np.allclose(start["velocity"], end["velocity"], atol=1e-9)


def test_telemetry_includes_radial_and_tangential_speed():
    telemetry = KeplerOrbit().calculate_telemetry(10_000, 0.2, 45)

    assert telemetry["radial_speed"] > 0
    assert telemetry["tangential_speed"] > 0
    assert telemetry["speed"] == pytest.approx(
        math.hypot(telemetry["radial_speed"], telemetry["tangential_speed"]))


def test_orbital_telemetry_exposes_perigee_apogee_and_period():
    orbit = KeplerOrbit()

    telemetry = orbit.calculate_telemetry(10_000, 0.2, 0)

    assert telemetry["perigee"] == pytest.approx(8_000)
    assert telemetry["apogee"] == pytest.approx(12_000)
    assert telemetry["period"] == pytest.approx(2 * math.pi * math.sqrt(10_000**3 / orbit.GM))


def test_orbit_samples_are_elliptical_and_return_to_start():
    orbit = KeplerOrbit()

    points = orbit.sample_orbit(10_000, 0.2, 0, 0, 0, samples=36)

    assert points.shape == (36, 3)
    radii = np.linalg.norm(points, axis=1)
    assert radii.min() == pytest.approx(8_000)
    assert radii.max() == pytest.approx(12_000)
    assert np.allclose(points[0], points[-1], atol=1_000) is False


def test_simulation_clock_advances_with_time_scale_and_can_pause():
    clock = SimulationClock()

    assert clock.advance(0.5) == pytest.approx(0.5)
    clock.set_time_scale(60)
    assert clock.advance(0.5) == pytest.approx(30.5)
    clock.pause()
    assert clock.advance(1) == pytest.approx(30.5)
    clock.resume()
    clock.set_time_scale(-2)
    assert clock.advance(1) == pytest.approx(28.5)
