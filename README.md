# Satellite Orbit Simulator

A Python-based satellite orbit simulator that visualizes satellites orbiting Earth using orbital mechanics calculations.

## Features Implemented

### Phase 1 - Physics Module (Completed)
- Satellite class with orbital elements
- Kepler's laws for 2-body problem calculations
- Orbital period and velocity calculations
- J₂ perturbation effects (Earth oblateness)
- Numerical integration methods

### Phase 2 - Data Module (Completed)
- TLE Parser with checksum validation
- Satellite database management
- Support for loading satellites from TLE files

### Phase 3 - Visualization Module (In Progress)
- Live PyQt6 visualization with continuous simulation updates
- Elliptical orbital paths generated from classical orbital elements
- Pause, resume, reverse time, and simulation speed controls
- Satellite telemetry panel
- Custom satellite creation from perigee/apogee and orbital orientation
- Local JSON persistence primitives for custom satellites
- TLE file import and export for the current satellite collection
- Satellite editing and deletion from the GUI
- Display of all orbital paths or only the selected satellite's path
- Mouse-wheel zoom with bounded magnification
- Camera centering on the selected satellite and camera reset
- Physically scaled Earth and orbit display with automatic framing
- Keplerian time propagation using mean anomaly and Newton iteration
- Instantaneous radial/tangential velocity telemetry and velocity vectors
- Perigee/apogee markers and atmospheric-intersection validation
- Click-to-select satellites in the orbital scene
- French/English interface selector
- Configurable scientific units (km, km/s) or metric units (m, m/s)
- Precise simulation time scale from -10,000x to +10,000x
- Interactive 3D globe view using native PyQt6 OpenGL widgets
- Toggle between the 2D orbital map and the 3D globe
- 3D camera rotation with mouse drag, zoom with the wheel, and satellite selection

The visualization work follows TDD: each new orbital or user-facing behavior is
covered by a failing test before its implementation is added. The current
iteration delivers the live 2D and 3D visualization foundations.

## Project Structure

```
satellite_simulator/
├── core/                    # Physics and math calculations
│   ├── __init__.py
│   ├── satellite.py         # Satellite class with orbital elements
│   ├── orbit_calculator.py  # Keplerian and numerical integration methods  
│   └── perturbations.py     # J₂, atmospheric drag calculations
├── data/                    # Data handling and parsing
│   ├── __init__.py
│   ├── tle_parser.py        # TLE file parsing
│   └── satellite_database.py# Satellite database management
├── visualization/           # 3D visualization components
│   ├── __init__.py
│   └── gui.py               # Main GUI application
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── constants.py         # Physical constants
│   └── helpers.py           # Helper functions
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── test_physics.py
│   ├── test_network.py
│   ├── test_data.py
│   └── test_visualization.py
└── main.py                  # Entry point
```

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd satellite_simulator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run tests to verify installation:**
```bash
pytest satellite_simulator/tests/
```

## Running the Simulator

```bash
# Run tests
pytest satellite_simulator/tests/

# Run the simulator GUI
python satellite_simulator/main.py
```

The live view starts automatically. `Charger un fichier TLE` imports standard
three-line TLE records, while `Exporter en TLE` writes the current collection
to a portable `.tle` file. Use `Modifier` or `Supprimer` for the selected
satellite. The satellite selector is synchronized with the local JSON store,
so persisted satellites remain selectable after restart. `Créer un satellite`
opens the orbital-elements workflow; distances are in kilometres and speeds in
km/s by default. Use the orbit-mode button to switch between all orbital paths
and the selected path only. Use the mouse wheel to zoom, `Centrer sur le
satellite` to move the camera to the selected object, and
`Réinitialiser la caméra` to return to the Earth-centered view.
Use `Passer en vue 3D` to switch to the interactive 3D globe. Drag with the
left mouse button to rotate the camera, use the mouse wheel to zoom, and
click a satellite to select it. The 3D view uses the same live simulation
clock and satellite collection as the 2D view.

## Dependencies

- Python 3.7+
- pytest (for testing)
- numpy (for numerical calculations)
- scipy (for scientific computing)
- pandas (for data handling)
- pyqt6 (for GUI and visualization)

## Testing

All modules follow Test-Driven Development principles:
- Tests are written before implementation (RED state)
- Implementation is developed to make tests pass (GREEN state)
- Tests are continuously run to ensure no regressions (BLUE state)

## CI/CD Pipeline

GitHub Actions workflow is configured in `.github/workflows/test.yml` to automatically run tests on every push and pull request.

## Sample Data

The project includes a sample TLE file (`sample_tle.txt`) that demonstrates the format expected by the parser.

## How to Use

1. **Load TLE data:** Use the GUI to load TLE files containing satellite information
2. **Visualize orbits:** See satellites orbiting Earth in 3D visualization
3. **Interactive controls:** Adjust simulation parameters and view different orbital elements

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for your changes
4. Implement your feature following TDD principles
5. Submit a pull request

## License

MIT License - see LICENSE file for details.