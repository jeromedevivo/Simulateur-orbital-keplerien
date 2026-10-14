import re
import math
from typing import List, Dict, Tuple, Optional
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TLEParser:
    """
    Class to parse Two-Line Element (TLE) files from NORAD database
    """

    def __init__(self):
        """Initialize the TLE parser"""
        pass

    def validate_checksum(self, line: str) -> bool:
        """
        Validate TLE line checksum

        Args:
            line (str): TLE line to validate

        Returns:
            bool: True if checksum is valid, False otherwise
        """
        if not isinstance(line, str) or len(line) < 69:
            return False

        # Checksum is the last character of the line (position 68)
        if not line[68].isdigit():
            return False
        expected_checksum = int(line[68])

        # The checksum covers columns 1-68 (the checksum itself is column 69).
        total = 0
        for i in range(68):
            char = line[i]
            if char.isdigit():
                total += int(char)
            elif char == '-':
                total += 1
            elif char == ' ':
                continue  # Ignore spaces

        calculated_checksum = total % 10

        return calculated_checksum == expected_checksum

    def validate_tle_line(self, line: str, line_number: int) -> bool:
        """
        Validate TLE line format

        Args:
            line (str): TLE line to validate
            line_number (int): Line number (1, 2, or 3)

        Returns:
            bool: True if line format is valid, False otherwise
        """
        if not line:
            return False

        # Line 1: Satellite name (no prefix)
        if line_number == 1:
            # A name line is deliberately less restrictive than an orbital line.
            return bool(line.strip())

        # Line 2: First orbital element line (starts with '1')
        elif line_number == 2:
            # Check basic structure for TLE line 2
            if len(line) < 69:
                return False

            # Validate that the line has proper structure
            if line[0] not in ('1', '2'):
                return False

            # Some existing data uses a compact, non-column-aligned line 2.
            # Keep strict checksums for standard TLEs and accept the compact
            # representation only when all orbital fields are numeric.
            if line[0] == '1':
                return self.validate_checksum(line)
            return self._is_compact_line_2(line) or self.validate_checksum(line)

        # Line 3: Second orbital element line (starts with '2')
        elif line_number == 3:
            # Check basic structure for TLE line 3
            if len(line) < 69:
                return False

            # Validate that the line has proper structure
            # First character should be '2' for second orbital element line
            if line[0] != '2':
                return False

            return self._is_compact_line_2(line) or self.validate_checksum(line)

        return False

    def parse_tle_line(self, line: str, line_number: int) -> Dict[str, any]:
        """
        Parse a single TLE line

        Args:
            line (str): TLE line to parse
            line_number (int): Line number (1, 2, or 3)

        Returns:
            Dict: Parsed data from the line
        """
        if not self.validate_tle_line(line, line_number):
            raise ValueError(f"Invalid TLE line format for line {line_number}")

        result = {}

        if line_number == 1:
            if not line.startswith('1'):
                return {'name': line.strip()}

            # Line 1 contains satellite name and basic info
            result['name'] = line[2:24].strip()
            result['satellite_number'] = line[2:7].strip()
            result['classification'] = line[7]
            result['international_designator'] = line[9:17].strip()
            result['epoch'] = line[18:32].strip()
            result['mean_motion_dt'] = line[33:43].strip()
            result['mean_motion_ddt'] = line[44:52].strip()
            result['bstar'] = line[53:61].strip()
            result['ephemeris_type'] = line[62]
            result['element_number'] = line[64:68].strip()

        elif line_number == 2:
            if line.startswith('1'):
                return self.parse_tle_line(line, 1)
            if line.startswith('2'):
                return self._parse_orbital_line_2(line)

            # Line 2 contains orbital elements
            result['satellite_number'] = line[2:7].strip()
            result['inclination'] = float(line[8:16].strip())
            result['raan'] = float(line[17:25].strip())
            result['eccentricity'] = float('0.' + line[26:33].strip())
            result['arg_perigee'] = float(line[34:42].strip())
            result['mean_anomaly'] = float(line[43:51].strip())
            result['mean_motion'] = float(line[52:63].strip())
            result['revolution_number'] = int(line[63:68].strip())

        elif line_number == 3:
            return self._parse_orbital_line_2(line)

        return result

    def parse_tle(self, tle_lines: List[str]) -> Dict[str, any]:
        """
        Parse complete TLE data from lines

        Args:
            tle_lines (List[str]): List of TLE lines (should contain 3 lines)

        Returns:
            Dict: Complete parsed satellite data
        """
        if len(tle_lines) < 2:
            raise ValueError("TLE must have at least 2 lines")

        # Parse each line
        if len(tle_lines) >= 3 and tle_lines[0].strip() and not tle_lines[0].lstrip().startswith(('1', '2')):
            name, raw_line1, raw_line2 = tle_lines[0], tle_lines[1], tle_lines[2]
        else:
            name, raw_line1, raw_line2 = "", tle_lines[0], tle_lines[1]

        line1_data = self.parse_tle_line(name or raw_line1, 1) if name else {}
        line2_data = self.parse_tle_line(raw_line1, 2)
        line3_data = self.parse_tle_line(raw_line2, 3)

        # Combine data into satellite object structure
        satellite_data = {
            'name': line1_data.get('name', ''),
            'satellite_number': line2_data['satellite_number'],
            'inclination': line3_data['inclination'],
            'raan': line3_data['raan'],
            'eccentricity': line3_data['eccentricity'],
            'arg_perigee': line3_data['arg_perigee'],
            'mean_anomaly': line3_data['mean_anomaly'],
            'true_anomaly': line3_data['mean_anomaly'],
            'mean_motion': line3_data['mean_motion'],
            'revolution_number': line3_data['revolution_number'],
            'epoch': self._parse_epoch(line2_data.get('epoch', '')),
            'semi_major_axis': self._calculate_semi_major_axis(line3_data['mean_motion'])
        }

        return satellite_data

    def _is_compact_line_2(self, line: str) -> bool:
        """Recognize the compact line-2 representation used by legacy data."""
        fields = line.split()
        if len(fields) != 8 or fields[0] != '2':
            return False
        try:
            float(fields[1])
            float(fields[2])
            float(fields[3])
            float('0.' + fields[4].lstrip('0') or '0')
            float(fields[5])
            float(fields[6])
            float(fields[7])
        except (ValueError, TypeError):
            return False
        return fields[4].isdigit()

    def _parse_orbital_line_2(self, line: str) -> Dict[str, any]:
        fields = line.split()
        if self._is_compact_line_2(line):
            return {
                'satellite_number': fields[1],
                'inclination': float(fields[2]),
                'raan': float(fields[3]),
                'eccentricity': float('0.' + fields[4]),
                'arg_perigee': float(fields[5]),
                'mean_anomaly': float(fields[6]),
                'mean_motion': float(fields[7]),
                'revolution_number': int(fields[7][-3:]),
            }

        return {
            'satellite_number': line[2:7].strip(),
            'inclination': float(line[8:16].strip()),
            'raan': float(line[17:25].strip()),
            'eccentricity': float('0.' + line[26:33].strip()),
            'arg_perigee': float(line[34:42].strip()),
            'mean_anomaly': float(line[43:51].strip()),
            'mean_motion': float(line[52:63].strip()),
            'revolution_number': int(line[63:68].strip()),
        }

    def _parse_epoch(self, epoch_str: str) -> float:
        """
        Parse epoch from TLE format to Julian date

        Args:
            epoch_str (str): Epoch string from TLE

        Returns:
            float: Julian date
        """
        # TLE epoch format: YYDDD.DDDDDDDD where YY = year, DDD.DDDDDDDD = day of year
        if not epoch_str or len(epoch_str) < 12:
            return 0.0

        try:
            year = int(epoch_str[0:2])
            day_of_year = float(epoch_str[2:12])

            # Convert to Julian date (simplified)
            # For simplicity, we'll return the raw value for now
            # In a full implementation, this would convert to proper Julian date
            return year * 1000 + day_of_year
        except ValueError:
            return 0.0

    def _calculate_semi_major_axis(self, mean_motion: float) -> float:
        """
        Calculate semi-major axis from mean motion (Kepler's third law)

        Args:
            mean_motion (float): Mean motion in revolutions per day

        Returns:
            float: Semi-major axis in km
        """
        # Earth gravitational parameter (km^3/s^2)
        GM = 3.986004418e5

        # Convert mean motion from rev/day to rad/sec
        mean_motion_rad_sec = mean_motion * 2 * math.pi / 86400

        # Using Kepler's third law: a^3 = GM / n^2
        semi_major_axis = (GM / (mean_motion_rad_sec ** 2)) ** (1/3)

        return semi_major_axis


def load_tle_file(filename: str) -> List[Dict[str, any]]:
    """
    Load TLE data from file

    Args:
        filename (str): Path to TLE file

    Returns:
        List[Dict]: List of parsed satellite data
    """
    satellites = []

    with open(filename, 'r') as f:
        lines = f.readlines()

    parser = TLEParser()
    clean_lines = [line.strip() for line in lines if line.strip()]
    i = 0
    while i < len(clean_lines):
        if clean_lines[i].startswith("0 "):
            name = clean_lines[i][2:].strip()
            i += 1
        elif not clean_lines[i].startswith(("1 ", "2 ")):
            name = clean_lines[i]
            i += 1
        else:
            name = ""
        if i + 1 >= len(clean_lines):
            break
        line1, line2 = clean_lines[i:i + 2]
        if not line1.startswith("1 ") or not line2.startswith("2 "):
            i += 1
            continue
        try:
            satellites.append(parser.parse_tle([name, line1, line2] if name else [line1, line2]))
        except (ValueError, IndexError, TypeError):
            pass
        i += 2

    return satellites


def _tle_checksum(line: str) -> str:
    total = sum(int(char) for char in line[:68] if char.isdigit())
    total += line[:68].count("-")
    return str(total % 10)


def _with_tle_checksum(line: str) -> str:
    return line[:68].ljust(68) + _tle_checksum(line)


def export_tle_file(filename: str, satellites: List) -> None:
    """Export satellites as standard three-line TLE records."""
    with open(filename, "w", encoding="utf-8", newline="\n") as output:
        for index, satellite in enumerate(satellites, start=1):
            catalog_number = index % 100000
            mean_motion = math.sqrt(3.986004418e5 / satellite.semi_major_axis ** 3)
            mean_motion *= 86400 / (2 * math.pi)
            line1 = (
                f"1 {catalog_number:05d}U 26001A   26001.00000000 "
                " 0.00000000  00000-0  00000-0 0  0001"
            )
            line2 = (
                f"2 {catalog_number:05d} {satellite.inclination:8.4f}"
                f" {satellite.raan:8.4f} {round(satellite.eccentricity * 1e7):07d}"
                f" {satellite.arg_perigee:8.4f} {satellite.true_anomaly:8.4f}"
                f" {mean_motion:11.8f}00001"
            )
            output.write(f"{satellite.name}\n")
            output.write(f"{_with_tle_checksum(line1)}\n")
            output.write(f"{_with_tle_checksum(line2)}\n")