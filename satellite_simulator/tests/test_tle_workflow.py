from satellite_simulator.core.satellite import Satellite
from satellite_simulator.data.satellite_database import SatelliteDatabase
from satellite_simulator.data.tle_parser import export_tle_file, load_tle_file


def test_exported_tle_file_can_be_loaded_again(tmp_path):
    satellite = Satellite("Demo", 7_000, 0.02, 45, 20, 30, 10, 0)
    filename = tmp_path / "export.tle"

    export_tle_file(filename, [satellite])
    loaded = load_tle_file(filename)

    assert len(loaded) == 1
    assert loaded[0]["name"] == "Demo"
    assert loaded[0]["semi_major_axis"] > 0


def test_database_can_replace_an_existing_satellite():
    database = SatelliteDatabase()
    original = Satellite("Demo", 7_000, 0.02, 45, 20, 30, 10, 0)
    replacement = Satellite("Demo", 7_500, 0.03, 45, 20, 30, 10, 0)

    assert database.add_satellite(original)
    assert database.update_satellite(replacement)
    assert database.get_satellite("Demo") is replacement


def test_database_import_count_can_be_distinguished_from_total_collection(tmp_path):
    satellites = [
        Satellite("Demo-{0}".format(index), 7_000 + index, 0.02, 45, 20, 30, 10, 0)
        for index in range(12)
    ]
    filename = tmp_path / "collection.tle"
    export_tle_file(filename, satellites)

    database = SatelliteDatabase()
    assert database.load_from_tle_file(str(filename)) == 12
    assert len(database) == 12
