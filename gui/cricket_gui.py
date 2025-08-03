import sys
import os
import subprocess
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QFileDialog, QListWidget, 
                            QTabWidget, QTextEdit, QProgressBar, QMessageBox, 
                            QComboBox, QGridLayout, QScrollArea, QFrame)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont
import json
import glob

class CricketBallClassifierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nn_classifier_path = "../backend/nn-classifier"
        self.dataset_path = os.path.join(self.nn_classifier_path, "dataset")
        self.models_path = os.path.join(self.nn_classifier_path, "models")

        self.init_ui()
        # self.refresh_data()

    def init_ui(self):
        self.setWindowTitle("Cricket Ball Classifier – Training & Testing Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_dataset_tab()

    def create_dataset_tab(self):
        """Tab for viewing and managing training data"""
        dataset_widget = QWidget()
        layout = QVBoxLayout()

        # Header
        header = QLabel("Training Dataset Management")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application icon and style
    app.setApplicationName("Cricket Ball Classifier")

    window = CricketBallClassifierGUI()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()