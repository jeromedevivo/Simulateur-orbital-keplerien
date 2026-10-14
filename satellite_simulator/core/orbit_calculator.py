import numpy as np
from typing import Tuple, List

class KeplerOrbit:
    """
    Class to calculate satellite orbits using Kepler's laws and numerical integration
    """

    # Earth gravitational parameter (km^3/s^2)
    GM = 3.986004418e5

    def __init__(self):
        """Initialize the orbit calculator"""
        pass

    def calculate_orbital_period(self, semi_major_axis: float) -> float:
        """
        Calculate orbital period using Kepler's third law

        Args:
            semi_major_axis (float): Semi-major axis in km

        Returns:
            float: Orbital period in seconds
        """
        # T = 2π * sqrt(a^3 / GM)
        period = 2 * np.pi * np.sqrt((semi_major_axis ** 3) / self.GM)
        return period

    def calculate_velocity(self, semi_major_axis: float, eccentricity: float) -> Tuple[float, float]:
        """
        Calculate orbital velocity at different points in the orbit

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity

        Returns:
            Tuple[float, float]: Velocity at periapsis and apoapsis (km/s)
        """
        # Velocity at periapsis: v_p = sqrt(GM * (2/r_p - 1/a))
        # Velocity at apoapsis: v_a = sqrt(GM * (2/r_a - 1/a))

        # Semi-latus rectum
        a = semi_major_axis
        e = eccentricity

        # Periapsis distance
        r_p = a * (1 - e)
        # Apoapsis distance
        r_a = a * (1 + e)

        v_p = np.sqrt(self.GM * (2/r_p - 1/a))
        v_a = np.sqrt(self.GM * (2/r_a - 1/a))

        return v_p, v_a

    def calculate_position_from_elements(self, semi_major_axis: float, eccentricity: float,
                                       inclination: float, raan: float, arg_perigee: float,
                                       true_anomaly: float, time_since_epoch: float = 0) -> np.ndarray:
        """
        Calculate satellite position using orbital elements

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity
            inclination (float): Inclination in degrees
            raan (float): Right Ascension of Ascending Node in degrees
            arg_perigee (float): Argument of perigee in degrees
            true_anomaly (float): True anomaly in degrees
            time_since_epoch (float): Time since epoch in seconds

        Returns:
            np.ndarray: Position vector in ECI coordinates (km)
        """
        return self.calculate_state_from_elements(
            semi_major_axis, eccentricity, inclination, raan,
            arg_perigee, true_anomaly, time_since_epoch
        )["position"]

    def calculate_state_from_elements(self, semi_major_axis: float, eccentricity: float,
                                      inclination: float, raan: float, arg_perigee: float,
                                      true_anomaly: float,
                                      time_since_epoch: float = 0) -> dict:
        """Calculate ECI position and velocity from classical orbital elements."""
        if not self.validate_orbital_elements(semi_major_axis, eccentricity):
            raise ValueError("Invalid semi-major axis or eccentricity")

        i_rad, raan_rad = np.radians([inclination, raan])
        arg_rad, anomaly_rad = np.radians([arg_perigee, true_anomaly])
        a, e = semi_major_axis, eccentricity
        p = a * (1 - e * e)
        radius = p / (1 + e * np.cos(anomaly_rad))

        position_perifocal = np.array([
            radius * np.cos(anomaly_rad),
            radius * np.sin(anomaly_rad),
            0.0,
        ])
        velocity_perifocal = np.sqrt(self.GM / p) * np.array([
            -np.sin(anomaly_rad),
            e + np.cos(anomaly_rad),
            0.0,
        ])

        rotation = np.array([
            [
                np.cos(raan_rad) * np.cos(arg_rad) -
                np.sin(raan_rad) * np.sin(arg_rad) * np.cos(i_rad),
                -np.cos(raan_rad) * np.sin(arg_rad) -
                np.sin(raan_rad) * np.cos(arg_rad) * np.cos(i_rad),
                np.sin(raan_rad) * np.sin(i_rad),
            ],
            [
                np.sin(raan_rad) * np.cos(arg_rad) +
                np.cos(raan_rad) * np.sin(arg_rad) * np.cos(i_rad),
                -np.sin(raan_rad) * np.sin(arg_rad) +
                np.cos(raan_rad) * np.cos(arg_rad) * np.cos(i_rad),
                -np.cos(raan_rad) * np.sin(i_rad),
            ],
            [
                np.sin(arg_rad) * np.sin(i_rad),
                np.cos(arg_rad) * np.sin(i_rad),
                np.cos(i_rad),
            ],
        ])
        position = rotation @ position_perifocal
        velocity = rotation @ velocity_perifocal
        return {
            "position": position,
            "velocity": velocity,
            "radius": float(np.linalg.norm(position)),
            "speed": float(np.linalg.norm(velocity)),
        }

    def calculate_state_at_time(self, semi_major_axis: float, eccentricity: float,
                                inclination: float, raan: float,
                                arg_perigee: float, true_anomaly: float,
                                time_since_epoch: float) -> dict:
        """Propagate an elliptical orbit using mean anomaly and Kepler's equation."""
        if not self.validate_orbital_elements(semi_major_axis, eccentricity):
            raise ValueError("Invalid semi-major axis or eccentricity")

        e = float(eccentricity)
        true_anomaly_rad = np.radians(true_anomaly)
        eccentric_anomaly = 2 * np.arctan2(
            np.sqrt(1 - e) * np.sin(true_anomaly_rad / 2),
            np.sqrt(1 + e) * np.cos(true_anomaly_rad / 2),
        )
        initial_mean_anomaly = eccentric_anomaly - e * np.sin(eccentric_anomaly)
        mean_anomaly = initial_mean_anomaly + (
            self.calculate_mean_motion(semi_major_axis) * time_since_epoch
        )
        mean_anomaly = (mean_anomaly + np.pi) % (2 * np.pi) - np.pi
        eccentric_anomaly = mean_anomaly if e < 0.8 else np.pi
        for _ in range(50):
            correction = (eccentric_anomaly - e * np.sin(eccentric_anomaly) -
                          mean_anomaly) / (1 - e * np.cos(eccentric_anomaly))
            eccentric_anomaly -= correction
            if abs(correction) <= 1e-10:
                break

        true_anomaly_rad = 2 * np.arctan2(
            np.sqrt(1 + e) * np.sin(eccentric_anomaly / 2),
            np.sqrt(1 - e) * np.cos(eccentric_anomaly / 2),
        )
        state = self.calculate_state_from_elements(
            semi_major_axis, e, inclination, raan, arg_perigee,
            np.degrees(true_anomaly_rad),
        )
        radial_speed = float(np.dot(state["position"], state["velocity"]) /
                             state["radius"])
        state["radial_speed"] = radial_speed
        state["tangential_speed"] = float(np.sqrt(
            max(0.0, state["speed"] ** 2 - radial_speed ** 2)))
        state["specific_energy"] = float(
            state["speed"] ** 2 / 2 - self.GM / state["radius"])
        state["true_anomaly"] = float(np.degrees(true_anomaly_rad))
        return state

    def calculate_telemetry(self, semi_major_axis: float, eccentricity: float,
                            true_anomaly: float) -> dict:
        """Return the stable telemetry values used by the live views."""
        state = self.calculate_state_at_time(
            semi_major_axis, eccentricity, 0, 0, 0, true_anomaly, 0
        )
        return {
            "radius": state["radius"],
            "speed": state["speed"],
            "perigee": semi_major_axis * (1 - eccentricity),
            "apogee": semi_major_axis * (1 + eccentricity),
            "period": self.calculate_orbital_period(semi_major_axis),
            "radial_speed": state["radial_speed"],
            "tangential_speed": state["tangential_speed"],
        }

    def sample_orbit(self, semi_major_axis: float, eccentricity: float,
                     inclination: float, raan: float, arg_perigee: float,
                     samples: int = 180) -> np.ndarray:
        """Return ECI points around a complete orbit for plotting."""
        if samples < 3:
            raise ValueError("samples must be at least 3")
        anomalies = np.linspace(0.0, 360.0, samples, endpoint=False)
        return np.array([
            self.calculate_position_from_elements(
                semi_major_axis, eccentricity, inclination, raan,
                arg_perigee, anomaly
            )
            for anomaly in anomalies
        ])

    def calculate_mean_motion(self, semi_major_axis: float) -> float:
        """
        Calculate mean motion (angular velocity)

        Args:
            semi_major_axis (float): Semi-major axis in km

        Returns:
            float: Mean motion in radians/second
        """
        # n = sqrt(GM / a^3)
        mean_motion = np.sqrt(self.GM / (semi_major_axis ** 3))
        return mean_motion

    def calculate_orbital_energy(self, semi_major_axis: float, eccentricity: float) -> float:
        """
        Calculate orbital energy

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity

        Returns:
            float: Orbital energy in km^2/s^2
        """
        # E = -GM / (2a)
        energy = -self.GM / (2 * semi_major_axis)
        return energy

    def validate_orbital_elements(self, semi_major_axis: float, eccentricity: float) -> bool:
        """
        Validate that orbital elements make sense

        Args:
            semi_major_axis (float): Semi-major axis in km
            eccentricity (float): Orbital eccentricity

        Returns:
            bool: True if elements are valid
        """
        # Check for reasonable values
        if semi_major_axis <= 0:
            return False
        if not (0 <= eccentricity < 1):
            return False
        return True