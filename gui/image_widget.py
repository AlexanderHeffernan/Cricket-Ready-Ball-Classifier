from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
import os

class ImageWidget(QFrame):
    """
    Custom widget to display an image with its filename.
    """
    image_deleted = pyqtSignal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.setup_ui()

    def setup_ui(self):
        # Frame styling for modern look
        self.setFrameStyle(QFrame.Box)
        self.setMaximumWidth(200)
        self.setStyleSheet("""
            QFrame {
                border-radius: 12px;
                background: #23272a;
                padding: 8px;
                border: 1px solid #444;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background: transparent; border: none;")
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                150, 150, 
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Invalid Image")
        layout.addWidget(self.image_label)
        
        # Filename display
        filename = os.path.basename(self.image_path)
        filename_label = QLabel(filename)
        filename_label.setWordWrap(True)
        filename_label.setAlignment(Qt.AlignCenter)
        filename_label.setStyleSheet("color: #bbb; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(filename_label)

        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_image)
        delete_btn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def delete_image(self):
        reply = QMessageBox.question(self, 'Confirm Delete',
                                    f'Delete {os.path.basename(self.image_path)}?',
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                os.remove(self.image_path)
                self.image_deleted.emit(self.image_path)
                self.setParent(None)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete image: {str(e)}")