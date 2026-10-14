"""
Basic tests for satellite orbit simulator.
"""

def test_imports():
    """Test that core modules can be imported."""
    try:
        from satellite_simulator.core.satellite import Satellite
        from satellite_simulator.core.orbit_calculator import KeplerOrbit
        from satellite_simulator.core.perturbations import J2Perturbation

        # Create instances to make sure they work
        satellite = Satellite("TestSat", 6778.14, 0.001, 55.0, 120.0, 30.0, 45.0, 2459000.0)
        calculator = KeplerOrbit()
        perturbation = J2Perturbation()

        assert satellite is not None
        assert calculator is not None
        assert perturbation is not None

        print("[PASS] All basic imports successful")
    except ImportError as e:
        raise AssertionError(f"Import failed: {e}") from e
    except Exception as e:
        raise AssertionError(f"Other error: {e}") from e

def test_satellite_creation():
    """Test satellite creation."""
    from satellite_simulator.core.satellite import Satellite

    sat = Satellite("TestSat", 6778.14, 0.001, 55.0, 120.0, 30.0, 45.0, 2459000.0)

    assert sat.name == "TestSat"
    assert sat.semi_major_axis == 6778.14
    assert sat.eccentricity == 0.001

    print("[PASS] Satellite creation successful")

def test_orbit_calculator():
    """Test orbit calculator."""
    from satellite_simulator.core.orbit_calculator import KeplerOrbit

    calc = KeplerOrbit()

    # Test orbital period calculation
    period = calc.calculate_orbital_period(6778.14)  # ~6700 km semi-major axis
    assert isinstance(period, (int, float))
    assert period > 0

    print("[PASS] Orbit calculator working")

if __name__ == "__main__":
    print("Running basic tests...")

    test_imports()
    test_satellite_creation()
    test_orbit_calculator()
    print("\n[SUCCESS] All basic tests passed!")