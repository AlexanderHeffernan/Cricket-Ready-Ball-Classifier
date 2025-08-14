from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QScrollArea, QGridLayout
from PyQt5.QtGui import QFont
from widgets.image_widget import ImageWidget

def create_dataset_tab(parent):
    """
    Returns the Dataset tab QWidget.
    Expects parent to have: upload_images, refresh_data, stats_label, match_ready_layout, not_read_layout.
    """
    dataset_widget = QWidget()
    layout = QVBoxLayout()

    # Header
    header = QLabel("Training Dataset Management")
    header.setFont(QFont("Arial", 16, QFont.Bold))
    layout.addWidget(header)

    # Stats
    parent.stats_label = QLabel()
    layout.addWidget(parent.stats_label)

    # Upload buttons
    upload_layout = QHBoxLayout()

    upload_match_ready_btn = QPushButton("Upload Match-Ready Image(s)")
    upload_match_ready_btn.clicked.connect(lambda: parent.upload_images("match_ready"))
    upload_layout.addWidget(upload_match_ready_btn)

    upload_not_ready_btn = QPushButton("Upload Not-Ready Image(s)")
    upload_not_ready_btn.clicked.connect(lambda: parent.upload_images("not_match_ready"))
    upload_layout.addWidget(upload_not_ready_btn)

    refresh_btn = QPushButton("Refresh")
    refresh_btn.clicked.connect(parent.refresh_data)
    upload_layout.addWidget(refresh_btn)

    layout.addLayout(upload_layout)

    # Image galleries
    create_image_galleries(parent, layout)

    dataset_widget.setLayout(layout)
    return dataset_widget

def create_image_galleries(parent, parent_layout):
    """Create scrollable image galleries for each class"""

    # Match Ready Gallery
    match_ready_label = QLabel("Match Ready Image:")
    match_ready_label.setFont(QFont("Arial", 14, QFont.Bold))
    parent_layout.addWidget(match_ready_label)

    parent.match_ready_scroll = QScrollArea()
    parent.match_ready_widget = QWidget()
    parent.match_ready_layout = QGridLayout()
    parent.match_ready_widget.setLayout(parent.match_ready_layout)
    parent.match_ready_scroll.setWidget(parent.match_ready_widget)
    parent.match_ready_scroll.setWidgetResizable(True)
    parent.match_ready_scroll.setMinimumHeight(300)
    parent_layout.addWidget(parent.match_ready_scroll)

    # Not Match Ready Gallery
    not_ready_label = QLabel("Not-Match-Ready Images:")
    not_ready_label.setFont(QFont("Arial", 12, QFont.Bold))
    parent_layout.addWidget(not_ready_label)
    
    parent.not_ready_scroll = QScrollArea()
    parent.not_ready_widget = QWidget()
    parent.not_ready_layout = QGridLayout()
    parent.not_ready_widget.setLayout(parent.not_ready_layout)
    parent.not_ready_scroll.setWidget(parent.not_ready_widget)
    parent.not_ready_scroll.setWidgetResizable(True)
    parent.not_ready_scroll.setMaximumHeight(300)
    parent_layout.addWidget(parent.not_ready_scroll)