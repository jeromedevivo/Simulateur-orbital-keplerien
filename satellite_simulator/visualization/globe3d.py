"""Interactive 3D-style orbital view rendered by a PyQt OpenGL widget."""

import math
from typing import List, Optional

import numpy as np
from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QPainter, QPen
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from satellite_simulator.core.orbit_calculator import KeplerOrbit
from satellite_simulator.core.satellite import Satellite


class Orbit3DWidget(QOpenGLWidget):
    """Render the Earth and orbital planes with an interactive camera."""

    satellite_selected = pyqtSignal(object)

    EARTH_RADIUS_KM = 6378.14
    MIN_CAMERA_DISTANCE = 1.2
    MAX_CAMERA_DISTANCE = 30.0
    DEFAULT_CAMERA_DISTANCE = 8.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 600)
        self.satellites: List[Satellite] = []
        self.selected_satellite: Optional[Satellite] = None
        self.current_time = 0.0
        self.orbit = KeplerOrbit()
        self.show_all_orbits = True
        self.camera_distance = self.DEFAULT_CAMERA_DISTANCE
        self.camera_yaw = 0.0
        self.camera_pitch = 20.0
        self.camera_target = np.zeros(3)
        self.follow_selected = False
        self._last_mouse_position: Optional[QPoint] = None

    def set_satellites(self, satellites: List[Satellite]):
        self.satellites = list(satellites)
        if self.selected_satellite not in self.satellites:
            self.selected_satellite = None
        self.update()

    def set_current_time(self, current_time: float):
        self.current_time = float(current_time)
        if self.follow_selected and self.selected_satellite is not None:
            self.camera_target = self._state(
                self.selected_satellite)["position"].copy()
        self.update()

    def select_satellite(self, satellite: Optional[Satellite]):
        self.selected_satellite = satellite if satellite in self.satellites else None
        if self.selected_satellite is None:
            self.follow_selected = False
        if self.selected_satellite is not None:
            self.satellite_selected.emit(self.selected_satellite)
        self.update()

    @property
    def orbit_satellites(self):
        if self.show_all_orbits or self.selected_satellite is None:
            return list(self.satellites)
        return [self.selected_satellite]

    def set_show_all_orbits(self, show_all: bool):
        self.show_all_orbits = bool(show_all)
        self.update()

    def set_camera_distance(self, distance: float):
        self.camera_distance = min(
            self.MAX_CAMERA_DISTANCE,
            max(self.MIN_CAMERA_DISTANCE, float(distance)),
        )
        self.update()

    def rotate_camera(self, yaw_delta: float, pitch_delta: float):
        self.camera_yaw = (self.camera_yaw + float(yaw_delta)) % 360.0
        self.camera_pitch = min(89.0, max(-89.0, self.camera_pitch + float(pitch_delta)))
        self.update()

    def reset_camera(self):
        self.camera_distance = self.DEFAULT_CAMERA_DISTANCE
        self.camera_yaw = 0.0
        self.camera_pitch = 20.0
        self.camera_target = np.zeros(3)
        self.follow_selected = False
        self.update()

    def center_on_selected(self):
        if self.selected_satellite is None:
            return
        self.camera_target = self._state(
            self.selected_satellite)["position"].copy()
        self.follow_selected = True
        self.update()

    def _transform(self, position):
        yaw = math.radians(self.camera_yaw)
        pitch = math.radians(self.camera_pitch)
        relative_position = (
            np.asarray(position, dtype=float) - self.camera_target
        )
        x, y, z = relative_position / self.EARTH_RADIUS_KM
        yaw_x = x * math.cos(yaw) - y * math.sin(yaw)
        yaw_y = x * math.sin(yaw) + y * math.cos(yaw)
        return (
            yaw_x,
            y * math.cos(pitch) - z * math.sin(pitch),
            yaw_y * math.cos(pitch) + z * math.sin(pitch),
        )

    def _project(self, position):
        transformed = self._transform(position)
        scale = min(self.width(), self.height()) / (2.0 * self.camera_distance)
        depth = self.camera_distance - transformed[2]
        perspective = self.camera_distance / max(0.2, depth)
        return (
            self.width() / 2 + transformed[0] * scale * perspective,
            self.height() / 2 - transformed[1] * scale * perspective,
            transformed[2],
        )

    def _is_behind_earth(self, position):
        """Return whether a point is behind the projected Earth disk."""
        point_x, point_y, point_depth = self._project(position)
        earth_x, earth_y, earth_depth = self._project(np.zeros(3))
        scale = min(self.width(), self.height()) / (2.0 * self.camera_distance)
        earth_radius = scale * self.camera_distance / max(
            0.2, self.camera_distance - earth_depth
        )
        inside_disk = (
            (point_x - earth_x) ** 2 + (point_y - earth_y) ** 2
            <= earth_radius ** 2
        )
        return bool(point_depth < earth_depth and inside_disk)

    def mousePressEvent(self, event):
        self._last_mouse_position = event.position().toPoint()
        if event.button().name == "LeftButton":
            closest = None
            closest_distance = 16.0
            for satellite in self.satellites:
                state = self._state(satellite)
                x, y, _ = self._project(state["position"])
                distance = math.hypot(event.position().x() - x, event.position().y() - y)
                if distance < closest_distance:
                    closest = satellite
                    closest_distance = distance
            if closest is not None:
                self.select_satellite(closest)
        event.accept()

    def mouseMoveEvent(self, event):
        if self._last_mouse_position is not None and event.buttons():
            current = event.position().toPoint()
            delta = current - self._last_mouse_position
            self.rotate_camera(delta.x() * 0.5, delta.y() * 0.5)
            self._last_mouse_position = current
        event.accept()

    def mouseReleaseEvent(self, event):
        self._last_mouse_position = None
        event.accept()

    def wheelEvent(self, event):
        factor = 0.9 if event.angleDelta().y() > 0 else 1.1
        self.set_camera_distance(self.camera_distance * factor)
        event.accept()

    def _state(self, satellite):
        return self.orbit.calculate_state_at_time(
            satellite.semi_major_axis,
            satellite.eccentricity,
            satellite.inclination,
            satellite.raan,
            satellite.arg_perigee,
            satellite.true_anomaly,
            self.current_time,
        )

    def paintGL(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#050b16"))
        earth_x, earth_y, earth_depth = self._project(np.zeros(3))
        scale = min(self.width(), self.height()) / (2.0 * self.camera_distance)
        perspective = self.camera_distance / max(0.2, self.camera_distance - earth_depth)
        earth_radius = scale * perspective
        painter.setBrush(QBrush(QColor("#164d78")))
        painter.setPen(QPen(QColor("#43b9e8"), 2))
        painter.drawEllipse(
            int(earth_x - earth_radius),
            int(earth_y - earth_radius),
            int(earth_radius * 2),
            int(earth_radius * 2),
        )
        painter.setBrush(QBrush(QtNoBrush))
        painter.setPen(QPen(QColor("#2c7a54"), 2))
        painter.drawArc(
            int(earth_x - earth_radius * 0.75),
            int(earth_y - earth_radius * 0.35),
            int(earth_radius * 1.2),
            int(earth_radius * 0.6),
            20 * 16,
            130 * 16,
        )
        for satellite in self.orbit_satellites:
            points = self.orbit.sample_orbit(
                satellite.semi_major_axis,
                satellite.eccentricity,
                satellite.inclination,
                satellite.raan,
                satellite.arg_perigee,
                96,
            )
            projected = [self._project(point) for point in points]
            orbit_color = QColor(
                "#ffd166" if satellite is self.selected_satellite else "#527da3"
            )
            orbit_width = 2 if satellite is self.selected_satellite else 1
            for index, (first, second) in enumerate(
                zip(projected, projected[1:] + projected[:1])
            ):
                midpoint = (points[index] + points[(index + 1) % len(points)]) / 2.0
                hidden = self._is_behind_earth(midpoint)
                painter.setPen(QPen(
                    orbit_color,
                    orbit_width,
                    Qt.PenStyle.DashLine if hidden else Qt.PenStyle.SolidLine,
                ))
                painter.drawLine(int(first[0]), int(first[1]), int(second[0]), int(second[1]))
            x, y, depth = self._project(self._state(satellite)["position"])
            radius = 7 if satellite is self.selected_satellite else 5
            painter.setBrush(QBrush(QColor("#ffd166" if satellite is self.selected_satellite else "#f2f7ff")))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)
        painter.end()


QtNoBrush = Qt.BrushStyle.NoBrush
