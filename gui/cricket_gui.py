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

class ImageWidget(QFrame):
    """Custom widget to displat an image with label and delete button"""

    def __init__(self, image_path, class_name):
        super().__init__()
        self.image_path = image_path
        self.class_name = class_name
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)
        self.setMaximumWidth(200)
        
        layout = QVBoxLayout()
        
        # Image display
        self.image_label = QLabel()
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Invalid Image")
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Filename
        filename = os.path.basename(self.image_path)
        filename_label = QLabel(filename)
        filename_label.setWordWrap(True)
        filename_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.image_label)
        layout.addWidget(filename_label)
        self.setLayout(layout)

class CricketBallClassifierGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.nn_classifier_path = "../backend/nn-classifier"
        self.dataset_path = os.path.join(self.nn_classifier_path, "dataset")
        self.models_path = os.path.join(self.nn_classifier_path, "models")

        self.init_ui()
        self.refresh_data()

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

        # Image galleries
        self.create_image_galleries(layout)

        dataset_widget.setLayout(layout)
        self.tabs.addTab(dataset_widget, "Dataset")

    def create_image_galleries(self, parent_layout):
        """Create scrollable image galleries for each class"""

        # Match Ready Gallery
        match_ready_label = QLabel("Match Ready Image:")
        match_ready_label.setFont(QFont("Arial", 14, QFont.Bold))
        parent_layout.addWidget(match_ready_label)

        self.match_ready_scroll = QScrollArea()
        self.match_ready_widget = QWidget()
        self.match_ready_layout = QGridLayout()
        self.match_ready_widget.setLayout(self.match_ready_layout)
        self.match_ready_scroll.setWidget(self.match_ready_widget)
        self.match_ready_scroll.setWidgetResizable(True)
        self.match_ready_scroll.setMinimumHeight(300)
        parent_layout.addWidget(self.match_ready_scroll)

    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_image_galleries()

    def refresh_image_galleries(self):
        """Refresh image galleries"""
        # Clear existing widgets
        self.clear_layout(self.match_ready_layout)

        # Load match_ready images
        match_ready_path = os.path.join(self.dataset_path, "match_ready")
        if os.path.exists(match_ready_path):
            images = [f for f in os.listdir(match_ready_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for i, img in enumerate(images):  # Limit display
                img_path = os.path.join(match_ready_path, img)
                widget = ImageWidget(img_path, "match_ready")
                self.match_ready_layout.addWidget(widget, i // 5, i % 5)

    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

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