#!/usr/bin/env python3

"""
Main entry point for the satellite orbit simulator
"""

import sys
import os

# Add the project root to Python path (this ensures imports work properly)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Main function to run the simulator"""
    print("Starting Satellite Orbit Simulator...")

    try:
        from satellite_simulator.visualization.gui import SatelliteSimulatorGUI
        from PyQt6.QtWidgets import QApplication

        # Create and show the main window
        app = QApplication(sys.argv)
        window = SatelliteSimulatorGUI()
        window.show()

        print("Satellite Orbit Simulator started successfully!")
        print("Use the GUI to visualize satellite orbits.")
        print("Features:")
        print("- Load TLE data from files")
        print("- Visualize satellite orbits around Earth")
        print("- Interactive controls for simulation")

        # Run the application
        sys.exit(app.exec())

    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed.")
        print("You may need to install PyQt6 with: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"Error starting simulator: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())