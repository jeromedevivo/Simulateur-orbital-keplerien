import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from satellite_simulator.core.satellite import Satellite
from satellite_simulator.visualization.globe3d import Orbit3DWidget
from satellite_simulator.visualization.gui import SatelliteSimulatorGUI


@pytest.fixture(scope="module")
def qapplication():
    return QApplication.instance() or QApplication([])


def test_3d_widget_exposes_shared_simulation_and_selection_api(qapplication):
    widget = Orbit3DWidget()
    satellite = Satellite("ISS", 6778.14, 0.001, 51.6, 247.4, 130.5, 45.0, 0.0)

    widget.set_satellites([satellite])
    widget.set_current_time(120.0)
    widget.select_satellite(satellite)

    assert widget.satellites == [satellite]
    assert widget.current_time == pytest.approx(120.0)
    assert widget.selected_satellite is satellite


def test_3d_camera_controls_are_bounded_and_resettable(qapplication):
    widget = Orbit3DWidget()

    widget.set_camera_distance(0.01)
    assert widget.camera_distance == pytest.approx(widget.MIN_CAMERA_DISTANCE)
    widget.rotate_camera(30.0, -15.0)
    assert widget.camera_yaw == pytest.approx(30.0)
    assert widget.camera_pitch == pytest.approx(5.0)

    widget.reset_camera()
    assert widget.camera_distance == pytest.approx(widget.DEFAULT_CAMERA_DISTANCE)
    assert widget.camera_yaw == pytest.approx(0.0)
    assert widget.camera_pitch == pytest.approx(20.0)


def test_3d_widget_can_show_all_or_only_selected_orbits(qapplication):
    widget = Orbit3DWidget()
    first = Satellite("A", 7000, 0.01, 0, 0, 0, 0, 0)
    second = Satellite("B", 8000, 0.01, 0, 0, 0, 0, 0)
    widget.set_satellites([first, second])
    widget.select_satellite(first)

    assert widget.orbit_satellites == [first, second]
    widget.set_show_all_orbits(False)
    assert widget.orbit_satellites == [first]


def test_3d_centering_follows_selected_satellite(qapplication):
    widget = Orbit3DWidget()
    satellite = Satellite("A", 7000, 0.2, 0, 0, 0, 0, 0)
    widget.set_satellites([satellite])
    widget.select_satellite(satellite)

    widget.center_on_selected()
    first_target = widget.camera_target.copy()
    widget.set_current_time(100.0)

    assert widget.follow_selected is True
    assert not (widget.camera_target == first_target).all()
    widget.reset_camera()
    assert widget.follow_selected is False
    assert (widget.camera_target == 0).all()


def test_3d_centering_moves_earth_with_the_orbital_scene(qapplication):
    widget = Orbit3DWidget()
    satellite = Satellite("A", 7000, 0.2, 0, 0, 0, 0, 0)
    widget.resize(800, 600)
    widget.set_satellites([satellite])
    widget.select_satellite(satellite)

    earth_before = widget._project(np.zeros(3))
    widget.center_on_selected()
    earth_after = widget._project(np.zeros(3))

    assert earth_before[0] == pytest.approx(400.0)
    assert earth_before[1] == pytest.approx(300.0)
    assert np.linalg.norm(np.subtract(earth_after[:2], earth_before[:2])) > 0


def test_3d_marks_far_side_orbit_points_as_behind_earth(qapplication):
    widget = Orbit3DWidget()

    assert widget._is_behind_earth(np.array([0.0, 0.0, -Orbit3DWidget.EARTH_RADIUS_KM])) is True
    assert widget._is_behind_earth(np.array([0.0, 0.0, Orbit3DWidget.EARTH_RADIUS_KM])) is False
    assert widget._is_behind_earth(np.array([2.0 * Orbit3DWidget.EARTH_RADIUS_KM, 0.0, 0.0])) is False


def test_main_window_can_switch_between_2d_and_3d_views(qapplication):
    window = SatelliteSimulatorGUI()

    assert window.view_stack.currentIndex() == 0
    window.toggle_view_mode()
    assert window.view_stack.currentIndex() == 1
    window.toggle_view_mode()
    assert window.view_stack.currentIndex() == 0
    window.close()


def test_main_window_synchronizes_orbit_and_center_controls(qapplication):
    window = SatelliteSimulatorGUI()
    satellite = window.database.get_satellite("ISS")
    window.earth_widget.selected_satellite = satellite
    window.globe_3d_widget.select_satellite(satellite)

    window.toggle_orbit_mode()
    assert window.earth_widget.show_all_orbits is False
    assert window.globe_3d_widget.show_all_orbits is False
    window.center_selected_satellite()
    assert window.earth_widget.follow_selected is True
    assert window.globe_3d_widget.follow_selected is True
    window.close()


def test_startup_status_counts_persisted_satellites(qapplication, tmp_path):
    window = SatelliteSimulatorGUI()
    persisted = Satellite("Persisted", 7000, 0.01, 0, 0, 0, 0, 0)
    window.custom_store.path = tmp_path / "custom_satellites.json"
    window.custom_store.save([persisted])
    window.database.remove_satellite("Persisted")

    window.load_custom_satellites()

    assert "satellites" in window.status_bar.currentMessage()
    assert str(len(window.database)) in window.status_bar.currentMessage()
    window.close()


def test_status_count_updates_after_satellite_removal(qapplication):
    window = SatelliteSimulatorGUI()
    initial_count = len(window.database)

    window.database.remove_satellite("ISS")
    window.refresh_view()

    assert window.status_bar.currentMessage().endswith(
        "{} satellites chargés".format(initial_count - 1)
    )
    window.close()
