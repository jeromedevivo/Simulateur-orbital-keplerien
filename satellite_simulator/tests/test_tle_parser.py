import pytest
import os
import sys
from unittest.mock import patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satellite_simulator.data.tle_parser import TLEParser


def test_tle_parser_initialization():
    """Test that TLE parser can be initialized"""
    parser = TLEParser()

    assert parser is not None
    assert hasattr(parser, 'validate_checksum')
    assert hasattr(parser, 'parse_tle_line')


def test_valid_tle_checksum_validation():
    """Test TLE checksum validation with valid data"""
    parser = TLEParser()

    # Sample TLE line with valid checksum
    valid_line = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    assert parser.validate_checksum(valid_line) is True


def test_invalid_tle_checksum_validation():
    """Test TLE checksum validation with invalid data"""
    parser = TLEParser()

    # Sample TLE line with invalid checksum (last digit changed)
    invalid_line = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2928"
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


def test_parse_tle_line_1():
    """Test parsing of TLE line 1 (name and basic info)"""
    parser = TLEParser()

    line1 = "ISS (ZARYA)"
    result = parser.parse_tle_line(line1, 1)

    assert 'name' in result
    assert result['name'] == "ISS (ZARYA)"


def test_parse_tle_line_2():
    """Test parsing of TLE line 2 (orbital elements)"""
    parser = TLEParser()

    line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364"
    result = parser.parse_tle_line(line2, 2)

    assert 'satellite_number' in result
    assert 'inclination' in result
    assert 'raan' in result
    assert 'eccentricity' in result
    assert 'arg_perigee' in result
    assert 'mean_anomaly' in result
    assert 'mean_motion' in result
    assert 'revolution_number' in result

    assert result['satellite_number'] == "25544"
    assert result['inclination'] == 51.6416
    assert result['raan'] == 247.4627
    assert result['eccentricity'] == 0.0006703  # Note the decimal point
    assert result['arg_perigee'] == 130.5360
    assert result['mean_anomaly'] == 325.0299
    assert result['mean_motion'] == 15.72125391556364
    assert result['revolution_number'] == 364


def test_parse_tle():
    """Test complete TLE parsing"""
    parser = TLEParser()

    # Sample TLE data for ISS
    tle_lines = [
        "ISS (ZARYA)",
        "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927",
        "2 25544  51.6416 247.4627 0006703 130.5360 325.0299 15.72125391556364"
    ]

    result = parser.parse_tle(tle_lines)

    assert 'name' in result
    assert 'semi_major_axis' in result
    assert 'eccentricity' in result
    assert 'inclination' in result
    assert 'raan' in result
    assert 'arg_perigee' in result
    assert 'mean_anomaly' in result
    assert 'epoch' in result


def test_epoch_parsing():
    """Test epoch parsing"""
    parser = TLEParser()

    # Test with typical epoch format
    epoch_str = "08264.51782528"
    parsed_epoch = parser._parse_epoch(epoch_str)

    assert isinstance(parsed_epoch, float)
    # Should return a value representing year 2008 + day 264.51782528


def test_semi_major_axis_calculation():
    """Test semi-major axis calculation from mean motion"""
    parser = TLEParser()

    # Test with typical mean motion for ISS (15.72125391556364 rev/day)
    mean_motion = 15.72125391556364
    semi_major_axis = parser._calculate_semi_major_axis(mean_motion)

    assert isinstance(semi_major_axis, float)
    assert semi_major_axis > 0


def test_empty_and_invalid_lines():
    """Test handling of empty and invalid lines"""
    parser = TLEParser()

    # Test empty line
    assert parser.validate_tle_line("", line_number=1) is False

    # Test None value
    assert parser.validate_tle_line(None, line_number=1) is False


if __name__ == "__main__":
    pytest.main([__file__])