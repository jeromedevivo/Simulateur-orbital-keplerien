import numpy as np
from typing import Tuple, List

class Satellite:
    """
    Satellite class to represent a satellite with orbital elements
    """

    def __init__(self, name: str, semi_major_axis: float, eccentricity: float,
                 inclination: float, raan: float, arg_perigee: float, true_anomaly: float,
                 epoch: float):
        """
        Initialize a satellite with orbital elements

        Args:
            name (str): Satellite name
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity (0-1)
            inclination (float): Inclination in degrees
            raan (float): Right Ascension of Ascending Node in degrees
            arg_perigee (float): Argument of perigee in degrees
            true_anomaly (float): True anomaly in degrees
            epoch (float): Epoch time (Julian date)
        """
        self.name = name
        self.semi_major_axis = semi_major_axis
        self.eccentricity = eccentricity
        self.inclination = inclination
        self.raan = raan
        self.arg_perigee = arg_perigee
        self.true_anomaly = true_anomaly
        self.epoch = epoch

        # Validate orbital elements
        if not (0 <= eccentricity < 1):
            raise ValueError("Eccentricity must be between 0 and 1")

        # Convert to radians for calculations
        self.inclination_rad = np.radians(inclination)
        self.raan_rad = np.radians(raan)
        self.arg_perigee_rad = np.radians(arg_perigee)
        self.true_anomaly_rad = np.radians(true_anomaly)

    def position_at_epoch(self) -> np.ndarray:
        """
        Calculate satellite position at epoch using Kepler's laws
        Returns position vector in ECI coordinates (km)
        """
        from satellite_simulator.core.orbit_calculator import KeplerOrbit

        return KeplerOrbit().calculate_position_from_elements(
            self.semi_major_axis, self.eccentricity, self.inclination,
            self.raan, self.arg_perigee, self.true_anomaly
        )

    def get_orbital_elements(self) -> dict:
        """
        Get all orbital elements as a dictionary
        """
        return {
            'name': self.name,
            'semi_major_axis': self.semi_major_axis,
            'eccentricity': self.eccentricity,
            'inclination': self.inclination,
            'raan': self.raan,
            'arg_perigee': self.arg_perigee,
            'true_anomaly': self.true_anomaly,
            'epoch': self.epoch
        }

    def __str__(self):
        return f"Satellite({self.name}, {self.semi_major_axis}km, e={self.eccentricity})"