from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtGui import QFont

def create_models_tab(parent):
    """
    Returns the Model tab QWidget.
    Expects parent to have: models_list.
    """
    models_widget = QWidget()
    layout = QVBoxLayout()
    
    # Header
    header = QLabel("Trained Models")
    header.setFont(QFont("Arial", 16, QFont.Bold))
    layout.addWidget(header)
    
    # Models list
    parent.models_list = QListWidget()
    layout.addWidget(parent.models_list)
    
    models_widget.setLayout(layout)
    return models_widget