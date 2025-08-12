from image_widget import ImageWidget

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

        # Stats
        self.stats_label = QLabel()
        layout.addWidget(self.stats_label)

        # Upload buttons
        upload_layout = QHBoxLayout()

        upload_match_ready_btn = QPushButton("Upload Match-Ready Image")
        upload_match_ready_btn.clicked.connect(lambda: self.upload_images("match_ready"))
        upload_layout.addWidget(upload_match_ready_btn)

        upload_not_ready_btn = QPushButton("Upload Not-Ready Image")
        upload_not_ready_btn.clicked.connect(lambda: self.upload_images("not_match_ready"))
        upload_layout.addWidget(upload_not_ready_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        upload_layout.addWidget(refresh_btn)

        layout.addLayout(upload_layout)

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

        # Not Match Ready Gallery
        not_ready_label = QLabel("Not-Match-Ready Images:")
        not_ready_label.setFont(QFont("Arial", 12, QFont.Bold))
        parent_layout.addWidget(not_ready_label)
        
        self.not_ready_scroll = QScrollArea()
        self.not_ready_widget = QWidget()
        self.not_ready_layout = QGridLayout()
        self.not_ready_widget.setLayout(self.not_ready_layout)
        self.not_ready_scroll.setWidget(self.not_ready_widget)
        self.not_ready_scroll.setWidgetResizable(True)
        self.not_ready_scroll.setMaximumHeight(300)
        parent_layout.addWidget(self.not_ready_scroll)

    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_dataset_stats()
        self.refresh_image_galleries()

    def refresh_dataset_stats(self):
        """Update dataset statistics"""
        match_ready_path = os.path.join(self.dataset_path, "match_ready")
        not_ready_path = os.path.join(self.dataset_path, "not_match_ready")
        
        match_ready_count = len([f for f in os.listdir(match_ready_path) 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(match_ready_path) else 0
        not_ready_count = len([f for f in os.listdir(not_ready_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(not_ready_path) else 0
        
        total = match_ready_count + not_ready_count
        self.stats_label.setText(f"Total Images: {total} | Match-Ready: {match_ready_count} | Not-Match-Ready: {not_ready_count}")

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
                widget = ImageWidget(img_path)
                self.match_ready_layout.addWidget(widget, i // 5, i % 5)

        # Load not_match_ready images
        not_ready_path = os.path.join(self.dataset_path, "not_match_ready")
        if os.path.exists(not_ready_path):
            images = [f for f in os.listdir(not_ready_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for i, img in enumerate(images[:20]):  # Limit display
                img_path = os.path.join(not_ready_path, img)
                widget = ImageWidget(img_path)
                # widget.image_deleted.connect(self.refresh_data)
                self.not_ready_layout.addWidget(widget, i // 5, i % 5)

    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def upload_images(self, class_name):
        """Upload images to the specified class folder"""
        files, _ = QFileDialog.getOpenFileNames(
            self, f"Select {class_name.replace('_', ' ').title()} Images", 
            "", "Images (*.jpg *.jpeg *.png)")
        
        if files:
            target_dir = os.path.join(self.dataset_path, class_name)
            os.makedirs(target_dir, exist_ok=True)
            
            for file_path in files:
                filename = os.path.basename(file_path)
                target_path = os.path.join(target_dir, filename)
                try:
                    shutil.copy2(file_path, target_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to copy {filename}: {str(e)}")
            
            QMessageBox.information(self, "Success", f"Uploaded {len(files)} images to {class_name}")
            self.refresh_data()

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