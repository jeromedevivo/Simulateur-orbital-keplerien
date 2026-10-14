#!/usr/bin/env python3

"""
Satellite database management module
"""

from typing import List, Dict, Optional
import os
import sys

# Add the parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from satellite_simulator.core.satellite import Satellite


class SatelliteDatabase:
    """
    Database class to manage multiple satellites
    """

    def __init__(self):
        """Initialize the satellite database"""
        self._satellites: Dict[str, Satellite] = {}

    def add_satellite(self, satellite: Satellite) -> bool:
        """
        Add a satellite to the database

        Args:
            satellite (Satellite): Satellite object to add

        Returns:
            bool: True if successful, False otherwise
        """
        if not satellite or not satellite.name:
            return False
        if satellite.name in self._satellites:
            return False

        self._satellites[satellite.name] = satellite
        return True

    def get_satellite(self, name: str) -> Optional[Satellite]:
        """
        Get a satellite by name

        Args:
            name (str): Name of the satellite

        Returns:
            Satellite: Satellite object or None if not found
        """
        return self._satellites.get(name)

    def update_satellite(self, satellite: Satellite) -> bool:
        """Replace an existing satellite while preserving its unique name."""
        if not satellite or not satellite.name or satellite.name not in self._satellites:
            return False
        self._satellites[satellite.name] = satellite
        return True

    def remove_satellite(self, name: str) -> bool:
        """
        Remove a satellite from the database

        Args:
            name (str): Name of the satellite to remove

        Returns:
            bool: True if successful, False otherwise
        """
        if name in self._satellites:
            del self._satellites[name]
            return True
        return False

    def get_all_satellites(self) -> List[Satellite]:
        """
        Get all satellites in the database

        Returns:
            List[Satellite]: List of all satellite objects
        """
        return list(self._satellites.values())

    def get_all_satellite_names(self) -> List[str]:
        """
        Get all satellite names in the database

        Returns:
            List[str]: List of all satellite names
        """
        return list(self._satellites.keys())

    def clear_database(self):
        """Clear all satellites from the database"""
        self._satellites.clear()

    def load_from_tle_file(self, filename: str) -> int:
        """Load parsed TLE records into the database and return the count."""
        from satellite_simulator.data.tle_parser import load_tle_file

        loaded = 0
        for data in load_tle_file(filename):
            satellite = Satellite(
                name=data['name'],
                semi_major_axis=data['semi_major_axis'],
                eccentricity=data['eccentricity'],
                inclination=data['inclination'],
                raan=data['raan'],
                arg_perigee=data['arg_perigee'],
                true_anomaly=data.get('true_anomaly', data['mean_anomaly']),
                epoch=data['epoch'],
            )
            if self.add_satellite(satellite):
                loaded += 1
        return loaded

    def __len__(self) -> int:
        """Get number of satellites in database"""
        return len(self._satellites)

    def __str__(self) -> str:
        """String representation of the database"""
        return f"SatelliteDatabase with {len(self._satellites)} satellites"