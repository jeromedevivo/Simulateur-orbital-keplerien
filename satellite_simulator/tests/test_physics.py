import pytest
import numpy as np
from satellite_simulator.core.satellite import Satellite
from satellite_simulator.core.orbit_calculator import KeplerOrbit

def test_satellite_creation():
    """Test that a satellite can be created with orbital elements"""
    # Test with typical orbital elements
    sat = Satellite(
        name="TestSat",
        semi_major_axis=6778.14,  # km
        eccentricity=0.001,
        inclination=55.0,  # degrees
        raan=120.0,  # degrees
        arg_perigee=30.0,  # degrees
        true_anomaly=45.0,  # degrees
        epoch=2459000.0  # Julian date
    )

    assert sat.name == "TestSat"
    assert sat.semi_major_axis == 6778.14
    assert sat.eccentricity == 0.001
    assert sat.inclination == 55.0

def test_satellite_position_calculation():
    """Test satellite position calculation using Kepler's laws"""
    # Create a satellite with known orbital elements
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

    # Test position calculation at epoch (should be at perigee for this setup)
    pos = sat.position_at_epoch()
    assert isinstance(pos, np.ndarray)
    assert len(pos) == 3

def test_kepler_orbit_calculation():
    """Test Kepler orbit calculations"""
    orbit = KeplerOrbit()

    # Test that the class can be instantiated
    assert orbit is not None

    # Test orbital period calculation
    semi_major_axis = 6778.14  # km
    period = orbit.calculate_orbital_period(semi_major_axis)
    assert isinstance(period, float)
    assert period > 0

def test_orbital_elements_validation():
    """Test validation of orbital elements"""
    # Test valid eccentricity range
    sat = Satellite(
        name="ValidSat",
        semi_major_axis=6778.14,
        eccentricity=0.0,  # Valid
        inclination=55.0,
        raan=120.0,
        arg_perigee=30.0,
        true_anomaly=45.0,
        epoch=2459000.0
    )

    assert sat.eccentricity >= 0
    assert sat.eccentricity < 1  # Valid for elliptical orbits

if __name__ == "__main__":
    pytest.main([__file__])