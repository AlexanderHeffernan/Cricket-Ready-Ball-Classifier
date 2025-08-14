from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def create_prediction_tab(parent):
    """
    Returns the Prediction tab QWidget.
    Expects parent to have: select_prediction_image, run_prediction, show_image_preview, etc.
    """
    prediction_widget = QWidget()
    layout = QVBoxLayout(prediction_widget)
    layout.setSpacing(16)
    
    # Header
    header = QLabel("Model Testing & Prediction")
    header.setFont(QFont("Arial", 16, QFont.Bold))
    layout.addWidget(header)
    
    # File selection
    file_layout = QHBoxLayout()
    parent.selected_file_label = QLabel("No file selected")
    file_layout.addWidget(parent.selected_file_label)
    
    select_file_btn = QPushButton("Select Image")
    select_file_btn.clicked.connect(parent.select_prediction_image)
    file_layout.addWidget(select_file_btn)
    
    parent.predict_btn = QPushButton("Predict")
    parent.predict_btn.clicked.connect(parent.run_prediction)
    parent.predict_btn.setStyleSheet("""
        QPushButton { 
            background-color: #4caf50;
            color: white;
        }

        QPushButton:disabled {
            background-color: #888;
            color: #ccc;
        }
    """)
    parent.predict_btn.setEnabled(False)  # Initially disabled
    file_layout.addWidget(parent.predict_btn)
    
    layout.addLayout(file_layout)

    # Main preview/results area
    main_area = QHBoxLayout()
    main_area.setSpacing(24)
    
    # Image preview
    parent.preview_label = QLabel("Image preview will appear here")
    parent.preview_label.setMinimumSize(300, 300)
    parent.preview_label.setAlignment(Qt.AlignCenter)
    parent.preview_label.setStyleSheet("border: 1px solid gray;")
    main_area.addWidget(parent.preview_label, stretch=1)
    
    # Results
    results_text_layout = QVBoxLayout()
    parent.prediction_result = QLabel("Results will appear here")
    parent.prediction_result.setFont(QFont("Arial", 14))
    results_text_layout.addWidget(parent.prediction_result)
    main_area.addLayout(results_text_layout, stretch=1)
    
    layout.addLayout(main_area, stretch=1)
    
    prediction_widget.setLayout(layout)
    return prediction_widget