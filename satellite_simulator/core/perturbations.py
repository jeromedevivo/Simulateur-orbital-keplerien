import numpy as np
from typing import Tuple

class J2Perturbation:
    """
    Class to calculate J2 perturbations (Earth oblateness effects)
    """

    # Earth's J2 coefficient (dimensionless)
    J2 = 1.08263e-3

    # Earth's equatorial radius in km
    earth_radius = 6378.137

    def __init__(self):
        """Initialize J2 perturbation calculator"""
        pass

    def calculate_j2_perturbation(self, semi_major_axis: float, inclination: float) -> float:
        """
        Calculate the J2 perturbation effect on orbital elements

        Args:
            semi_major_axis (float): Semi-major axis in km
            inclination (float): Inclination in degrees

        Returns:
            float: J2 perturbation effect (in radians per day)
        """
        # Simplified calculation - in a full implementation this would be more complex
        # J2 effect depends on orbit altitude and inclination

        # Convert inclination to radians
        i_rad = np.radians(inclination)

        # Simplified formula for demonstration purposes
        # In reality, this involves complex orbital mechanics calculations
        perturbation = self.J2 * (self.earth_radius / semi_major_axis)**2 * np.cos(i_rad)

        return perturbation

    def calculate_omega_dot(self, semi_major_axis: float, eccentricity: float, inclination: float) -> float:
        """
        Calculate rate of change of argument of perigee (dω/dt)

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity
            inclination (float): Inclination in degrees

        Returns:
            float: Rate of change of argument of perigee (radians/day)
        """
        # Simplified calculation
        i_rad = np.radians(inclination)
        e = eccentricity

        # Simplified formula for demonstration
        omega_dot = -1.5 * self.J2 * (self.earth_radius / semi_major_axis)**2 * np.cos(i_rad) * (3/2) * (1 - e**2)

        return omega_dot

    def calculate_omega_raan(self, semi_major_axis: float, eccentricity: float, inclination: float) -> float:
        """
        Calculate rate of change of right ascension of ascending node (dΩ/dt)

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity
            inclination (float): Inclination in degrees

        Returns:
            float: Rate of change of RAAN (radians/day)
        """
        # Simplified calculation
        i_rad = np.radians(inclination)  # Fixed typo
        e = eccentricity

        # Simplified formula for demonstration
        raan_dot = -1.5 * self.J2 * (self.earth_radius / semi_major_axis)**2 * (3/2) * np.sin(i_rad) * (1 - e**2)

        return raan_dot

    def calculate_altitude_perturbation(self, altitude: float) -> Tuple[float, float]:
        """
        Calculate perturbations based on altitude

        Args:
            altitude (float): Satellite altitude in km

        Returns:
            Tuple[float, float]: Perturbation effects for different orbital parameters
        """
        # Simplified calculation - in reality this would be more complex
        if altitude < 2000:  # Low Earth Orbit
            # Stronger J2 effect for LEO
            j2_effect = self.J2 * (self.earth_radius / (self.earth_radius + altitude))**2
        else:
            # Weaker effect for higher orbits
            j2_effect = self.J2 * (self.earth_radius / (self.earth_radius + altitude))**4

        return (j2_effect, 0.0)  # Return J2 effect and other effects