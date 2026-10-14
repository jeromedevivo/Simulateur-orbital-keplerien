import pytest
import numpy as np
from satellite_simulator.core.satellite import Satellite
from satellite_simulator.core.orbit_calculator import KeplerOrbit

def test_satellite_creation_with_valid_elements():
    """Test that a satellite can be created with valid orbital elements"""
    sat = Satellite(
        name="ISS",
        semi_major_axis=6778.14,
        eccentricity=0.001,
        inclination=51.64,  # ISS inclination
        raan=0.0,
        arg_perigee=0.0,
        true_anomaly=0.0,
        epoch=2459000.0
    )

    assert sat.name == "ISS"
    assert sat.semi_major_axis == 6778.14
    assert sat.eccentricity == 0.001
    assert sat.inclination == 51.64
    assert sat.raan == 0.0
    assert sat.arg_perigee == 0.0
    assert sat.true_anomaly == 0.0
    assert sat.epoch == 2459000.0

def test_satellite_creation_with_invalid_eccentricity():
    """Test that satellite creation fails with invalid eccentricity"""
    with pytest.raises(ValueError):
        Satellite(
            name="InvalidSat",
            semi_major_axis=6778.14,
            eccentricity=1.5,  # Invalid - should be < 1
            inclination=55.0,
            raan=120.0,
            arg_perigee=30.0,
            true_anomaly=45.0,
            epoch=2459000.0
        )

def test_satellite_position_calculation():
    """Test satellite position calculation"""
    sat = Satellite(
        name="ISS",
        semi_major_axis=6778.14,
        eccentricity=0.001,
        inclination=51.64,
        raan=0.0,
        arg_perigee=0.0,
        true_anomaly=0.0,
        epoch=2459000.0
    )

    pos = sat.position_at_epoch()
    assert isinstance(pos, np.ndarray)
    assert len(pos) == 3

def test_kepler_orbit_calculations():
    """Test Kepler orbit calculations"""
    orbit = KeplerOrbit()

    # Test orbital period calculation
    period = orbit.calculate_orbital_period(6778.14)
    assert isinstance(period, float)
    assert period > 0

    # Test velocity calculation
    v_p, v_a = orbit.calculate_velocity(6778.14, 0.001)
    assert isinstance(v_p, float)
    assert isinstance(v_a, float)
    assert v_p > 0 and v_a > 0

def test_orbital_elements_validation():
    """Test validation of orbital elements"""
    orbit = KeplerOrbit()

    # Test valid elements
    assert orbit.validate_orbital_elements(6778.14, 0.001) == True

    # Test invalid semi-major axis
    assert orbit.validate_orbital_elements(-1000, 0.001) == False

    # Test invalid eccentricity
    assert orbit.validate_orbital_elements(6778.14, 1.5) == False

def test_orbital_energy_calculation():
    """Test orbital energy calculation"""
    orbit = KeplerOrbit()

    energy = orbit.calculate_orbital_energy(6778.14, 0.001)
    assert isinstance(energy, float)
    assert energy < 0  # Energy should be negative for bound orbits

def test_mean_motion_calculation():
    """Test mean motion calculation"""
    orbit = KeplerOrbit()

    mean_motion = orbit.calculate_mean_motion(6778.14)
    assert isinstance(mean_motion, float)
    assert mean_motion > 0

def test_position_calculation_with_elements():
    """Test position calculation with orbital elements"""
    orbit = KeplerOrbit()

    pos = orbit.calculate_position_from_elements(
        semi_major_axis=6778.14,
        eccentricity=0.001,
        inclination=51.64,
        raan=0.0,
        arg_perigee=0.0,
        true_anomaly=0.0
    )

    assert isinstance(pos, np.ndarray)
    assert len(pos) == 3

if __name__ == "__main__":
    pytest.main([__file__])