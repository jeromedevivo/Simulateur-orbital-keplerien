import pytest
import os
import sys
from unittest.mock import patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satellite_simulator.data.tle_parser import TLEParser
from satellite_simulator.data.satellite_database import SatelliteDatabase
from satellite_simulator.core.satellite import Satellite


def test_tle_parser_initialization():
    """Test that TLE parser can be initialized"""
    parser = TLEParser()

    assert parser is not None
    assert hasattr(parser, 'validate_checksum')
    assert hasattr(parser, 'parse_tle_line')


def test_valid_tle_parsing():
    """Test parsing of a valid TLE line"""
    # Sample ISS TLE data
    tle_line1 = "ISS (ZARYA)"
    tle_line2 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    tle_line3 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364"

    parser = TLEParser()

    # Test parsing
    result = parser.parse_tle([tle_line1, tle_line2, tle_line3])

    assert result is not None
    assert 'name' in result
    assert 'semi_major_axis' in result
    assert 'eccentricity' in result
    assert 'inclination' in result
    assert 'raan' in result
    assert 'arg_perigee' in result
    assert 'true_anomaly' in result
    assert 'epoch' in result


def test_tle_checksum_validation():
    """Test TLE checksum validation"""
    parser = TLEParser()

    # Valid checksum
    valid_line = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    assert parser.validate_checksum(valid_line) is True

    # Invalid checksum
    invalid_line = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2928"  # Changed last digit
    assert parser.validate_checksum(invalid_line) is False


def test_tle_line_format_validation():
    """Test validation of TLE line format"""
    parser = TLEParser()

    # Valid TLE line formats
    valid_line1 = "ISS (ZARYA)"
    valid_line2 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    valid_line3 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364"

    assert parser.validate_tle_line(valid_line1, line_number=1) is True
    assert parser.validate_tle_line(valid_line2, line_number=2) is True
    assert parser.validate_tle_line(valid_line3, line_number=3) is True

    # Invalid format
    invalid_line = "This is not a valid TLE line"
    assert parser.validate_tle_line(invalid_line, line_number=2) is False


def test_satellite_database_initialization():
    """Test that satellite database can be initialized"""
    db = SatelliteDatabase()

    assert db is not None
    assert hasattr(db, 'add_satellite')
    assert hasattr(db, 'remove_satellite')
    assert hasattr(db, 'get_satellite')
    assert hasattr(db, 'load_from_tle_file')


def test_database_add_remove_satellites():
    """Test adding and removing satellites from database"""
    db = SatelliteDatabase()

    # Create a test satellite
    sat = Satellite(
        name="TestSat",
        semi_major_axis=6778.14,
        eccentricity=0.001,
        inclination=55.0,
        raan=120.0,
        arg_perigee=30.0,
        true_anomaly=45.0,
        epoch=2459000.0
    )

    # Add satellite
    db.add_satellite(sat)

    # Check it's there
    retrieved = db.get_satellite("TestSat")
    assert retrieved is not None
    assert retrieved.name == "TestSat"

    # Remove satellite
    db.remove_satellite("TestSat")

    # Check it's gone
    retrieved = db.get_satellite("TestSat")
    assert retrieved is None


def test_load_multiple_satellites_from_tle():
    """Test loading multiple satellites from a TLE file"""
    # Create sample TLE content for testing
    tle_content = """ISS (ZARYA)
1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927
2 25544  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364
COSMOS 2251 DEB
1 30176U 03001A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927
2 30176  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364"""

    parser = TLEParser()
    db = SatelliteDatabase()

    # Test that we can parse and load satellites
    # This will be tested after implementation
    pass


def test_tle_parsing_edge_cases():
    """Test edge cases in TLE parsing"""
    parser = TLEParser()

    # Test empty lines
    assert parser.validate_tle_line("", line_number=1) is False

    # Test None values
    assert parser.validate_tle_line(None, line_number=1) is False


if __name__ == "__main__":
    pytest.main([__file__])