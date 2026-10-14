import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
import pytest
from PyQt6.QtWidgets import QApplication

from satellite_simulator.core.satellite import Satellite
from satellite_simulator.visualization.gui import EarthWidget


@pytest.fixture(scope="module")
def qapplication():
    return QApplication.instance() or QApplication([])


def test_view_can_show_only_selected_or_all_satellites(qapplication):
    widget = EarthWidget()
    first = Satellite("A", 7000, 0.01, 0, 0, 0, 0, 0)
    second = Satellite("B", 8000, 0.01, 0, 0, 0, 0, 0)
    widget.set_satellites([first, second])
    widget.selected_satellite = first

    assert widget.orbit_satellites == [first, second]
    widget.set_show_all_orbits(False)
    assert widget.orbit_satellites == [first]
    widget.set_show_all_orbits(True)
    assert widget.orbit_satellites == [first, second]


def test_view_zoom_and_camera_center_are_controllable(qapplication):
    widget = EarthWidget()
    satellite = Satellite("A", 7000, 0.01, 0, 0, 0, 0, 0)
    widget.set_satellites([satellite])
    widget.selected_satellite = satellite

    widget.set_zoom(2.0)
    assert widget.zoom == pytest.approx(2.0)
    widget.center_on_selected()
    assert widget.camera_center[0] != 0


def test_center_on_selected_keeps_following_satellite(qapplication):
    widget = EarthWidget()
    satellite = Satellite("A", 7000, 0.2, 0, 0, 0, 0, 0)
    widget.set_satellites([satellite])
    widget.selected_satellite = satellite

    widget.center_on_selected()
    first_center = widget.camera_center.copy()
    widget.advance(100)

    assert widget.follow_selected is True
    assert widget.camera_center[0] != pytest.approx(first_center[0])
    widget.reset_camera()
    assert widget.follow_selected is False


def test_2d_marks_far_side_orbit_points_as_behind_earth(qapplication):
    widget = EarthWidget()
    widget.resize(800, 600)
    center_x, center_y, scale = widget._view_geometry()

    assert widget._is_behind_earth(
        np.array([0.0, 0.0, -7000.0]), center_x, center_y, scale
    ) is True
    assert widget._is_behind_earth(
        np.array([0.0, 0.0, 7000.0]), center_x, center_y, scale
    ) is False
