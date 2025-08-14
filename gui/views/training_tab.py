from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QProgressBar, QTextEdit, QSpinBox, QDoubleSpinBox
from PyQt5.QtGui import QFont

def create_training_tab(parent):
    """
    Returns the Training tab QWidget.
    Expects parent to have: start_training, update_training_output, training_finished, etc.
    """
    training_widget = QWidget()
    layout = QVBoxLayout()

    header = QLabel("Model Training")
    header.setFont(QFont("Arial", 16, QFont.Bold))
    layout.addWidget(header)

    # Settings row
    settings_layout = QHBoxLayout()
    parent.epochs_spin = QSpinBox()
    parent.epochs_spin.setRange(1, 100)
    parent.epochs_spin.setValue(15)
    parent.epochs_spin.setPrefix("Epochs: ")
    settings_layout.addWidget(parent.epochs_spin)

    parent.batch_spin = QSpinBox()
    parent.batch_spin.setRange(1, 128)
    parent.batch_spin.setValue(16)
    parent.batch_spin.setPrefix("Batch: ")
    settings_layout.addWidget(parent.batch_spin)

    parent.lr_spin = QDoubleSpinBox()
    parent.lr_spin.setRange(0.0001, 1.0)
    parent.lr_spin.setSingleStep(0.0001)
    parent.lr_spin.setValue(0.001)
    parent.lr_spin.setPrefix("LR: ")
    parent.lr_spin.setDecimals(4)
    settings_layout.addWidget(parent.lr_spin)

    parent.kfold_spin = QSpinBox()
    parent.kfold_spin.setRange(2, 10)
    parent.kfold_spin.setValue(3)
    parent.kfold_spin.setPrefix("Folds: ")
    settings_layout.addWidget(parent.kfold_spin)

    parent.patience_spin = QSpinBox()
    parent.patience_spin.setRange(1, 20)
    parent.patience_spin.setValue(5)
    parent.patience_spin.setPrefix("Patience: ")
    settings_layout.addWidget(parent.patience_spin)

    layout.addLayout(settings_layout)
    
    # Training button
    parent.train_btn = QPushButton("Start Training")
    parent.train_btn.clicked.connect(parent.start_training)
    parent.train_btn.setStyleSheet("QPushButton { background-color: #2e7d32; color: white; font-size: 14px; padding: 10px; }")
    layout.addWidget(parent.train_btn)
    
    # Progress bar
    parent.progress_bar = QProgressBar()
    parent.progress_bar.setVisible(False)
    layout.addWidget(parent.progress_bar)
    
    # Training output
    parent.training_output = QTextEdit()
    parent.training_output.setReadOnly(True)
    layout.addWidget(parent.training_output)
    
    training_widget.setLayout(layout)
    return training_widget