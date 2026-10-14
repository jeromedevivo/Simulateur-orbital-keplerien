#!/usr/bin/env python3

"""
Simple GUI for satellite orbit visualization using PyQt6
"""

import sys
import math
import numpy as np
from typing import List, Tuple
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QFormLayout, QDoubleSpinBox, QLineEdit,
                             QMessageBox, QSlider, QDialog, QDialogButtonBox,
                             QFileDialog, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

# Import our satellite simulator components
try:
    from satellite_simulator.data.tle_parser import TLEParser, export_tle_file
    from satellite_simulator.data.satellite_database import SatelliteDatabase
    from satellite_simulator.core.satellite import Satellite
    from satellite_simulator.core.orbit_calculator import KeplerOrbit
    from satellite_simulator.core.simulation import SimulationClock
    from satellite_simulator.data.custom_satellite import create_custom_satellite, CustomSatelliteStore
    from satellite_simulator.utils.units import UnitSystem
    from satellite_simulator.visualization.globe3d import Orbit3DWidget
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class EarthWidget(QWidget):
    """Widget to draw Earth and satellites"""

    satellite_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 600)
        self.satellites = []
        self.current_time = 0.0
        self.clock = SimulationClock()
        self.orbit = KeplerOrbit()
        self.selected_satellite = None
        self.language = "fr"
        self.show_all_orbits = True
        self.zoom = 1.0
        self.camera_center = np.zeros(3)
        self.follow_selected = False

    def set_satellites(self, satellites: List[Satellite]):
        """Set the satellites to display"""
        self.satellites = satellites
        self.update()

    def advance(self, elapsed_seconds: float):
        self.current_time = self.clock.advance(elapsed_seconds)
        if self.follow_selected and self.selected_satellite is not None:
            self.camera_center = self._selected_position()
        self.update()

    def set_time_scale(self, value: float):
        self.clock.set_time_scale(value)

    @property
    def orbit_satellites(self):
        if self.show_all_orbits or self.selected_satellite is None:
            return list(self.satellites)
        return [self.selected_satellite]

    def set_show_all_orbits(self, show_all: bool):
        self.show_all_orbits = bool(show_all)
        self.update()

    def set_zoom(self, zoom: float):
        self.zoom = min(10.0, max(0.2, float(zoom)))
        self.update()

    def center_on_selected(self):
        if self.selected_satellite is None:
            return
        self.follow_selected = True
        self.camera_center = self._selected_position()
        self.update()

    def _selected_position(self):
        state = self.orbit.calculate_state_at_time(
            self.selected_satellite.semi_major_axis,
            self.selected_satellite.eccentricity,
            self.selected_satellite.inclination,
            self.selected_satellite.raan,
            self.selected_satellite.arg_perigee,
            self.selected_satellite.true_anomaly,
            self.current_time)
        return state["position"].copy()

    def reset_camera(self):
        self.follow_selected = False
        self.camera_center = np.zeros(3)
        self.zoom = 1.0
        self.update()

    def _view_geometry(self):
        center_x = self.width() / 2
        center_y = self.height() / 2
        view_radius = min(self.width(), self.height()) / 2 - 30
        max_orbit_radius = max(
            [6378.14] + [
                sat.semi_major_axis * (1 + sat.eccentricity)
                for sat in self.orbit_satellites
            ]
        )
        return center_x, center_y, view_radius / max_orbit_radius * self.zoom

    def _project(self, position, center_x, center_y, scale):
        return (
            center_x + (position[0] - self.camera_center[0]) * scale,
            center_y - (position[1] - self.camera_center[1]) * scale,
        )

    def _is_behind_earth(self, position, center_x, center_y, scale):
        earth_x, earth_y = self._project(
            np.zeros(3), center_x, center_y, scale)
        point_x, point_y = self._project(
            position, center_x, center_y, scale)
        earth_radius = 6378.14 * scale
        return bool(
            position[2] < 0.0
            and (point_x - earth_x) ** 2 + (point_y - earth_y) ** 2
            <= earth_radius ** 2
        )

    def mousePressEvent(self, event):
        center_x, center_y, scale = self._view_geometry()
        closest = None
        closest_distance = 14.0
        for satellite in self.satellites:
            state = self.orbit.calculate_state_at_time(
                satellite.semi_major_axis, satellite.eccentricity,
                satellite.inclination, satellite.raan,
                satellite.arg_perigee, satellite.true_anomaly,
                self.current_time)
            satellite_x, satellite_y = self._project(
                state["position"], center_x, center_y, scale)
            distance = math.hypot(
                event.position().x() - satellite_x,
                event.position().y() - satellite_y)
            if distance <= closest_distance:
                closest = satellite
                closest_distance = distance
        if closest is not None:
            self.selected_satellite = closest
            self.follow_selected = False
            self.satellite_selected.emit(closest)
            self.update()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.set_zoom(self.zoom * factor)
        event.accept()

    def paintEvent(self, event):
        """Draw Earth and satellites"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        center_x, center_y, scale = self._view_geometry()
        max_orbit_radius = max(
            [6378.14] + [
                sat.semi_major_axis * (1 + sat.eccentricity)
                for sat in self.orbit_satellites
            ])
        view_radius = min(width, height) / 2 - 30
        earth_radius = 6378.14 * scale
        earth_x, earth_y = self._project(
            np.zeros(3), center_x, center_y, scale)

        # Draw Earth (simplified as a circle)
        painter.fillRect(self.rect(), QColor("#07111f"))
        painter.setBrush(QColor("#164d78"))
        painter.setPen(QPen(QColor("#43b9e8"), 2))
        painter.drawEllipse(QRectF(
            float(earth_x - earth_radius), float(earth_y - earth_radius),
            float(earth_radius * 2), float(earth_radius * 2)))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.setPen(QPen(QColor("#7ee8fa"), 1))
        painter.drawEllipse(QRectF(
            float(earth_x - earth_radius - 5), float(earth_y - earth_radius - 5),
            float(earth_radius * 2 + 10), float(earth_radius * 2 + 10)))
        painter.setBrush(QColor("#2c7a54"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(earth_x - earth_radius * 0.45,
                                   earth_y - earth_radius * 0.35,
                                   earth_radius * 0.5, earth_radius * 0.25))
        painter.drawEllipse(QRectF(earth_x + earth_radius * 0.05,
                                   earth_y - earth_radius * 0.05,
                                   earth_radius * 0.4, earth_radius * 0.3))
        painter.setPen(QPen(QColor("#80d8ff"), 1))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawText(int(earth_x - 25), int(earth_y + earth_radius + 22),
                         "TERRE" if self.language == "fr" else "EARTH")

        # Draw orbital grid rings
        painter.setPen(QPen(QColor("#183a58"), 1, Qt.PenStyle.DotLine))
        for radius_km in (6378.14, max_orbit_radius * 0.25,
                          max_orbit_radius * 0.5, max_orbit_radius * 0.75,
                          max_orbit_radius):
            radius = radius_km * scale
            painter.drawEllipse(QRectF(earth_x - radius, earth_y - radius,
                                       radius * 2, radius * 2))

        for sat in self.orbit_satellites:
            try:
                points = self.orbit.sample_orbit(
                    sat.semi_major_axis, sat.eccentricity, sat.inclination,
                    sat.raan, sat.arg_perigee, samples=180)
                orbit_pen = QColor("#f2a65a") if sat is self.selected_satellite else QColor("#6385a3")
                orbit_width = 2 if sat is self.selected_satellite else 1
                for index, (first, second) in enumerate(
                    zip(points, np.roll(points, -1, axis=0))
                ):
                    first_x, first_y = self._project(first, center_x, center_y, scale)
                    second_x, second_y = self._project(second, center_x, center_y, scale)
                    midpoint = (first + second) / 2.0
                    hidden = self._is_behind_earth(
                        midpoint, center_x, center_y, scale)
                    painter.setPen(QPen(
                        orbit_pen,
                        orbit_width,
                        Qt.PenStyle.DashLine if hidden else Qt.PenStyle.SolidLine,
                    ))
                    painter.drawLine(int(first_x), int(first_y), int(second_x), int(second_y))

                state = self.orbit.calculate_state_at_time(
                    sat.semi_major_axis, sat.eccentricity, sat.inclination,
                    sat.raan, sat.arg_perigee, sat.true_anomaly,
                    self.current_time)
                x_pos, y_pos = self._project(
                    state["position"], center_x, center_y, scale)
                painter.setBrush(QColor("#f2a65a") if sat is self.selected_satellite else QColor("#ff5d73"))
                painter.setPen(QPen(QColor("#ffffff"), 1))
                painter.drawEllipse(QRectF(float(x_pos - 5), float(y_pos - 5), 10.0, 10.0))

                velocity_scale = scale * 120
                painter.setPen(QPen(QColor("#7dffb2"), 2))
                painter.drawLine(
                    int(x_pos), int(y_pos),
                    int(x_pos + state["velocity"][0] * velocity_scale),
                    int(y_pos - state["velocity"][1] * velocity_scale))

                for marker_radius, marker_color in (
                    (sat.semi_major_axis * (1 - sat.eccentricity), "#55d6be"),
                    (sat.semi_major_axis * (1 + sat.eccentricity), "#ffcf56"),
                ):
                    marker_anomaly = 0 if marker_radius < sat.semi_major_axis else 180
                    marker_position = self.orbit.calculate_position_from_elements(
                        sat.semi_major_axis, sat.eccentricity, sat.inclination,
                        sat.raan, sat.arg_perigee, marker_anomaly)
                    marker_x, marker_y = self._project(
                        marker_position, center_x, center_y, scale)
                    painter.setBrush(QColor(marker_color))
                    painter.drawEllipse(QRectF(marker_x - 3, marker_y - 3, 6, 6))

            except Exception as e:
                print(f"Error drawing satellite {sat.name}: {e}")

class SatelliteSimulatorGUI(QMainWindow):
    """Main GUI window for satellite simulator"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satellite Orbit Simulator")
        self.setGeometry(100, 100, 800, 600)

        # Initialize database and parser
        self.parser = TLEParser()
        self.database = SatelliteDatabase()
        self.custom_store = CustomSatelliteStore("custom_satellites.json")
        self.language = "fr"
        self.units = UnitSystem("scientific")

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("Satellite Orbit Simulator")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # 2D and 3D visualization widgets
        self.earth_widget = EarthWidget()
        self.earth_widget.satellite_selected.connect(self.select_satellite_object)
        self.globe_3d_widget = Orbit3DWidget()
        self.globe_3d_widget.satellite_selected.connect(self.select_satellite_object)
        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.earth_widget)
        self.view_stack.addWidget(self.globe_3d_widget)
        layout.addWidget(self.view_stack)

        # Control panel
        control_layout = QHBoxLayout()

        # Load button
        self.load_button = QPushButton()
        load_button = self.load_button
        load_button.clicked.connect(self.load_tle_file)
        control_layout.addWidget(load_button)

        # Refresh button
        self.play_button = QPushButton()
        self.play_button.clicked.connect(self.toggle_animation)
        control_layout.addWidget(self.play_button)

        self.time_scale_spin = QDoubleSpinBox()
        self.time_scale_spin.setRange(-10000.0, 10000.0)
        self.time_scale_spin.setDecimals(2)
        self.time_scale_spin.setSingleStep(0.01)
        self.time_scale_spin.setValue(1.0)
        self.time_scale_spin.setSuffix(" x")
        self.time_scale_spin.valueChanged.connect(self.change_time_scale)
        self.speed_label = QLabel()
        control_layout.addWidget(self.speed_label)
        control_layout.addWidget(self.time_scale_spin)

        self.custom_button = QPushButton()
        custom_button = self.custom_button
        custom_button.clicked.connect(self.create_satellite)
        control_layout.addWidget(custom_button)

        self.edit_button = QPushButton()
        self.edit_button.clicked.connect(self.edit_selected_satellite)
        control_layout.addWidget(self.edit_button)
        self.delete_button = QPushButton()
        self.delete_button.clicked.connect(self.delete_selected_satellite)
        control_layout.addWidget(self.delete_button)
        self.export_button = QPushButton()
        self.export_button.clicked.connect(self.export_tle)
        control_layout.addWidget(self.export_button)
        self.orbit_mode_button = QPushButton()
        self.orbit_mode_button.clicked.connect(self.toggle_orbit_mode)
        control_layout.addWidget(self.orbit_mode_button)
        self.center_button = QPushButton()
        self.center_button.clicked.connect(self.center_selected_satellite)
        control_layout.addWidget(self.center_button)
        self.reset_camera_button = QPushButton()
        self.reset_camera_button.clicked.connect(self.reset_view)
        control_layout.addWidget(self.reset_camera_button)
        self.view_mode_button = QPushButton()
        self.view_mode_button.clicked.connect(self.toggle_view_mode)
        control_layout.addWidget(self.view_mode_button)

        # Satellite selection
        self.satellite_combo = QComboBox()
        self.satellite_combo.addItem("")
        self.satellite_combo.currentTextChanged.connect(self.select_satellite)
        control_layout.addWidget(self.satellite_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItem("Français", "fr")
        self.language_combo.addItem("English", "en")
        self.language_combo.currentIndexChanged.connect(self.change_language)
        control_layout.addWidget(self.language_combo)

        self.units_combo = QComboBox()
        self.units_combo.addItem("km / km/s", "scientific")
        self.units_combo.addItem("m / m/s", "metric")
        self.units_combo.currentIndexChanged.connect(self.change_units)
        control_layout.addWidget(self.units_combo)

        layout.addLayout(control_layout)
        self.telemetry_label = QLabel()
        layout.addWidget(self.telemetry_label)

        # Status bar
        self.status_bar = self.statusBar()
        self.apply_language()

        self.setCentralWidget(central_widget)

        self.timer = QTimer(self)
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.advance_simulation)
        self.timer.start()

        # Load sample data initially
        self.load_sample_tle()
        self.load_custom_satellites()

    def load_sample_tle(self):
        """Load sample TLE data for demonstration"""
        try:
            # Create some sample satellites with realistic orbital elements
            sample_satellites = [
                Satellite(
                    name="ISS",
                    semi_major_axis=6778.14,
                    eccentricity=0.001,
                    inclination=51.6416,
                    raan=247.4627,
                    arg_perigee=130.5360,
                    true_anomaly=45.0,
                    epoch=2459000.0
                ),
                Satellite(
                    name="HST",
                    semi_major_axis=6870.0,
                    eccentricity=0.001,
                    inclination=57.0,
                    raan=180.0,
                    arg_perigee=90.0,
                    true_anomaly=45.0,
                    epoch=2459000.0
                ),
                Satellite(
                    name="SPOT-5",
                    semi_major_axis=6730.0,
                    eccentricity=0.002,
                    inclination=98.0,
                    raan=0.0,
                    arg_perigee=180.0,
                    true_anomaly=45.0,
                    epoch=2459000.0
                )
            ]

            # Add to database
            for sat in sample_satellites:
                self.database.add_satellite(sat)

            # Update combo box
            self.sync_satellite_selector()

            self.status_bar.showMessage(
                self.text("loaded").format(
                    count=len(self.database.get_all_satellites())))
            self.refresh_view()

        except Exception as e:
            self.status_bar.showMessage(self.text("load_error").format(error=e))
            print(f"Error: {e}")

    def toggle_animation(self):
        if self.earth_widget.clock.is_running:
            self.earth_widget.clock.pause()
            self.play_button.setText(self.text("resume"))
        else:
            self.earth_widget.clock.resume()
            self.play_button.setText(self.text("pause"))

    def text(self, key: str) -> str:
        translations = {
            "fr": {
                "title": "Simulateur d'orbites satellitaires",
                "load": "Charger les exemples",
                "load_tle": "Charger un fichier TLE",
                "edit": "Modifier",
                "delete": "Supprimer",
                "export": "Exporter en TLE",
                "all_orbits": "Afficher toutes les orbites",
                "selected_orbit": "Afficher uniquement l'orbite sélectionnée",
                "center": "Centrer sur le satellite",
                "reset_camera": "Réinitialiser la caméra",
                "view_3d": "Passer en vue 3D",
                "view_2d": "Revenir à la vue 2D",
                "pause": "Pause",
                "resume": "Reprendre",
                "speed": "Vitesse du temps",
                "create": "Créer un satellite",
                "select": "Sélectionner un satellite...",
                "none": "Aucun satellite sélectionné",
                "loaded": "{count} satellites chargés",
                "ready": "Prêt",
                "form": "Paramètres orbitaux",
                "name": "Nom",
                "duplicate": "Un satellite portant ce nom existe déjà.",
                "load_error": "Erreur de chargement TLE : {error}",
                "refresh_error": "Erreur de rafraîchissement : {error}",
                "invalid": "Paramètres invalides",
                "altitude": "altitude",
                "speed_value": "vitesse",
                "distance": "distance",
                "radial": "radiale",
                "tangential": "tangentielle",
                "period": "période",
                "perigee": "périgée",
                "apogee": "apogée",
                "confirm_delete": "Supprimer ce satellite ?",
                "exported": "Fichier TLE exporté",
            },
            "en": {
                "title": "Satellite Orbit Simulator",
                "load": "Load examples",
                "load_tle": "Load a TLE file",
                "edit": "Edit",
                "delete": "Delete",
                "export": "Export TLE",
                "all_orbits": "Show all orbits",
                "selected_orbit": "Show selected orbit only",
                "center": "Center on satellite",
                "reset_camera": "Reset camera",
                "view_3d": "Switch to 3D view",
                "view_2d": "Return to 2D view",
                "pause": "Pause",
                "resume": "Resume",
                "speed": "Time speed",
                "create": "Create satellite",
                "select": "Select a satellite...",
                "none": "No satellite selected",
                "loaded": "{count} satellites loaded",
                "ready": "Ready",
                "form": "Orbital parameters",
                "name": "Name",
                "duplicate": "A satellite with this name already exists.",
                "load_error": "TLE loading error: {error}",
                "refresh_error": "Refresh error: {error}",
                "invalid": "Invalid parameters",
                "altitude": "altitude",
                "speed_value": "speed",
                "distance": "distance",
                "radial": "radial",
                "tangential": "tangential",
                "period": "period",
                "perigee": "perigee",
                "apogee": "apogee",
                "confirm_delete": "Delete this satellite?",
                "exported": "TLE file exported",
            },
        }
        return translations[self.language][key]

    def apply_language(self):
        self.setWindowTitle(self.text("title"))
        self.load_button.setText(self.text("load_tle"))
        self.play_button.setText(
            self.text("pause") if self.earth_widget.clock.is_running
            else self.text("resume"))
        self.speed_label.setText(self.text("speed"))
        self.custom_button.setText(self.text("create"))
        self.edit_button.setText(self.text("edit"))
        self.delete_button.setText(self.text("delete"))
        self.export_button.setText(self.text("export"))
        self.center_button.setText(self.text("center"))
        self.reset_camera_button.setText(self.text("reset_camera"))
        self.view_mode_button.setText(
            self.text("view_2d") if self.view_stack.currentIndex() == 1
            else self.text("view_3d"))
        self.update_orbit_mode_label()
        self.telemetry_label.setText(self.text("none"))
        self.status_bar.showMessage(self.text("ready"))
        self.earth_widget.language = self.language
        self.earth_widget.update()

    def change_language(self, index: int):
        self.language = self.language_combo.itemData(index)
        self.apply_language()

    def change_units(self, index: int):
        self.units = UnitSystem(self.units_combo.itemData(index))
        if self.earth_widget.selected_satellite is not None:
            self.update_telemetry(self.earth_widget.selected_satellite)

    def change_time_scale(self, value: float):
        self.earth_widget.set_time_scale(value)

    def update_orbit_mode_label(self):
        self.orbit_mode_button.setText(
            self.text("all_orbits") if not self.earth_widget.show_all_orbits
            else self.text("selected_orbit"))

    def toggle_orbit_mode(self):
        show_all = not self.earth_widget.show_all_orbits
        self.earth_widget.set_show_all_orbits(show_all)
        self.globe_3d_widget.set_show_all_orbits(show_all)
        self.update_orbit_mode_label()

    def center_selected_satellite(self):
        self.earth_widget.center_on_selected()
        self.globe_3d_widget.center_on_selected()

    def reset_view(self):
        self.earth_widget.reset_camera()
        self.globe_3d_widget.reset_camera()

    def toggle_view_mode(self):
        self.view_stack.setCurrentIndex(1 - self.view_stack.currentIndex())
        self.apply_language()

    def load_tle_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, self.text("load_tle"), "", "TLE files (*.tle *.txt);;All files (*)")
        if not filename:
            return
        try:
            self.database.load_from_tle_file(filename)
            self.sync_satellite_selector()
            self.refresh_view()
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, self.text("invalid"), str(error))

    def export_tle(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, self.text("export"), "satellites.tle", "TLE files (*.tle)")
        if not filename:
            return
        try:
            export_tle_file(filename, self.database.get_all_satellites())
            self.status_bar.showMessage(self.text("exported"))
        except OSError as error:
            QMessageBox.warning(self, self.text("invalid"), str(error))

    def sync_satellite_selector(self):
        current = self.satellite_combo.currentText()
        self.satellite_combo.blockSignals(True)
        self.satellite_combo.clear()
        self.satellite_combo.addItem(self.text("select"))
        for satellite in self.database.get_all_satellites():
            self.satellite_combo.addItem(satellite.name)
        index = self.satellite_combo.findText(current)
        self.satellite_combo.setCurrentIndex(max(0, index))
        self.satellite_combo.blockSignals(False)

    def advance_simulation(self):
        self.earth_widget.advance(0.033)
        self.globe_3d_widget.set_current_time(self.earth_widget.current_time)
        current = self.earth_widget.selected_satellite
        if current is not None:
            self.update_telemetry(current)

    def create_satellite(self):
        existing = getattr(self, "_editing_satellite", None)
        dialog = QDialog(self)
        dialog.setWindowTitle(self.text("edit") if existing else self.text("create"))
        form = QWidget(dialog)
        fields = QFormLayout(form)
        name = QLineEdit(existing.name if existing else (
            "Mon satellite" if self.language == "fr" else "My satellite"))
        name.setReadOnly(existing is not None)
        values = {}
        if self.language == "fr":
            form_fields = (("Périgée (km)", 400), ("Apogée (km)", 800),
                           ("Inclinaison (°)", 45), ("RAAN (°)", 0),
                           ("Argument du périgée (°)", 0), ("Anomalie vraie (°)", 0))
        else:
            form_fields = (("Perigee (km)", 400), ("Apogee (km)", 800),
                           ("Inclination (°)", 45), ("RAAN (°)", 0),
                           ("Argument of perigee (°)", 0), ("True anomaly (°)", 0))
        defaults = (
            (existing.semi_major_axis * (1 - existing.eccentricity) - 6378.14,
             existing.semi_major_axis * (1 + existing.eccentricity) - 6378.14,
             existing.inclination, existing.raan, existing.arg_perigee,
             existing.true_anomaly)
            if existing else (400, 800, 45, 0, 0, 0)
        )
        for (label, _), default in zip(form_fields, defaults):
            field = QDoubleSpinBox()
            field.setRange(-36000, 36000)
            field.setValue(default)
            values[label] = field
            fields.addRow(label, field)
        fields.insertRow(0, self.text("name"), name)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(QLabel(self.text("form")))
        dialog_layout.addWidget(form)
        dialog_layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            satellite = create_custom_satellite(
                name.text(),                 values[form_fields[0][0]].value(), values[form_fields[1][0]].value(),
                    values[form_fields[2][0]].value(), values[form_fields[3][0]].value(),
                    values[form_fields[4][0]].value(), values[form_fields[5][0]].value())
            if existing:
                if not self.database.update_satellite(satellite):
                    raise ValueError(self.text("invalid"))
            elif not self.database.add_satellite(satellite):
                QMessageBox.warning(self, self.text("invalid"), self.text("duplicate"))
                return
            self.custom_store.save([
                candidate for candidate in self.database.get_all_satellites()
                if candidate.name not in {"ISS", "HST", "SPOT-5"}
            ])
            self.sync_satellite_selector()
            self.satellite_combo.setCurrentText(satellite.name)
            self._editing_satellite = None
            self.refresh_view()
        except ValueError as error:
            self._editing_satellite = None
            QMessageBox.warning(self, self.text("invalid"), str(error))

    def edit_selected_satellite(self):
        satellite = self.earth_widget.selected_satellite
        if satellite is None:
            return
        self._editing_satellite = satellite
        self.create_satellite()

    def delete_selected_satellite(self):
        satellite = self.earth_widget.selected_satellite
        if satellite is None:
            return
        answer = QMessageBox.question(
            self, self.text("delete"), self.text("confirm_delete"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.database.remove_satellite(satellite.name)
        self.earth_widget.selected_satellite = None
        self.custom_store.save([
            candidate for candidate in self.database.get_all_satellites()
            if candidate.name not in {"ISS", "HST", "SPOT-5"}
        ])
        self.sync_satellite_selector()
        self.refresh_view()

    def load_custom_satellites(self):
        for satellite in self.custom_store.load():
            self.database.add_satellite(satellite)
        self.sync_satellite_selector()
        self.refresh_view()

    def update_satellite_count_status(self):
        """Keep the status bar count synchronized with the database."""
        self.status_bar.showMessage(
            self.text("loaded").format(
                count=len(self.database.get_all_satellites())))

    def refresh_view(self):
        """Refresh the visualization"""
        try:
            # Get all satellites from database
            satellites = []
            for name in self.database.get_all_satellite_names():
                sat = self.database.get_satellite(name)
                if sat:
                    satellites.append(sat)

            # Update visualization
            self.earth_widget.set_satellites(satellites)
            self.globe_3d_widget.set_satellites(satellites)
            self.update_satellite_count_status()

        except Exception as e:
            self.status_bar.showMessage(self.text("refresh_error").format(error=e))
            print(f"Error: {e}")

    def select_satellite(self, name: str):
        satellite = self.database.get_satellite(name) if name != self.text("select") else None
        self.earth_widget.selected_satellite = satellite
        self.earth_widget.follow_selected = False
        self.earth_widget.update()
        self.globe_3d_widget.select_satellite(satellite)
        if satellite is None:
            self.telemetry_label.setText(self.text("none"))
            return
        self.update_telemetry(satellite)

    def select_satellite_object(self, satellite: Satellite):
        index = self.satellite_combo.findText(satellite.name)
        if index >= 0:
            self.satellite_combo.setCurrentIndex(index)

    def update_telemetry(self, satellite: Satellite):
        state = self.earth_widget.orbit.calculate_state_at_time(
            satellite.semi_major_axis, satellite.eccentricity,
            satellite.inclination, satellite.raan, satellite.arg_perigee,
            satellite.true_anomaly, self.earth_widget.current_time)
        distance = self.units.distance(state["radius"])
        altitude = self.units.distance(state["radius"] - 6378.14)
        speed = self.units.speed(state["speed"])
        radial = self.units.speed(state["radial_speed"])
        tangential = self.units.speed(state["tangential_speed"])
        perigee = self.units.distance(
            satellite.semi_major_axis * (1 - satellite.eccentricity) - 6378.14)
        apogee = self.units.distance(
            satellite.semi_major_axis * (1 + satellite.eccentricity) - 6378.14)
        self.telemetry_label.setText(
            f"{satellite.name} | {self.text('altitude')} {altitude:.1f} {self.units.distance_label} | "
            f"{self.text('distance')} {distance:.1f} {self.units.distance_label} | "
            f"{self.text('speed_value')} {speed:.3f} {self.units.speed_label} | "
            f"{self.text('radial')} {radial:.3f} {self.units.speed_label} | "
            f"{self.text('tangential')} {tangential:.3f} {self.units.speed_label} | "
            f"{self.text('period')} {self.earth_widget.orbit.calculate_orbital_period(satellite.semi_major_axis) / 60:.1f} min | "
            f"{self.text('perigee')} {perigee:.1f} {self.units.distance_label} | "
            f"{self.text('apogee')} {apogee:.1f} {self.units.distance_label}")


def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Create and show the main window
    window = SatelliteSimulatorGUI()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
