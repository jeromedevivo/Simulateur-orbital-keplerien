import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from satellite_simulator.visualization.gui import EarthWidget


@pytest.fixture(scope="module")
def qapplication():
    application = QApplication.instance() or QApplication([])
    return application


def test_earth_widget_exposes_satellite_selection_signal(qapplication):
    widget = EarthWidget()

    assert hasattr(widget, "satellite_selected")
    assert widget.satellite_selected is not None
