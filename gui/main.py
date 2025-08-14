"""
Entry point for the Cricket Ball Classifier GUI application.
Initializes the QApplication and launches the main window.
"""

import sys
from PyQt5.QtWidgets import QApplication
from main_window import CricketBallClassifierGUI # Main application window

def main():
    # Create the Qt application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("Cricket Ball Classifier")

    # Create a show the main window
    window = CricketBallClassifierGUI()
    window.show()

    # Start the event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()