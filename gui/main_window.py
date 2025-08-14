from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QHBoxLayout, QPushButton, QFileDialog, QProgressBar, QTextEdit, QListWidget, QSpinBox, QDoubleSpinBox, QMessageBox, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import os
import shutil

from widgets.image_widget import ImageWidget
from threads.training_thread import TrainingThread
from threads.prediction_thread import PredictionThread

from views.dataset_tab import create_dataset_tab
from views.training_tab import create_training_tab
from views.prediction_tab import create_prediction_tab
from views.models_tab import create_models_tab

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
        self.tabs.addTab(create_dataset_tab(self), "Dataset")
        self.tabs.addTab(create_training_tab(self), "Training")
        self.tabs.addTab(create_prediction_tab(self), "Prediction")
        self.tabs.addTab(create_models_tab(self), "Models")

    def refresh_data(self):
        """Refresh all data displays"""
        self.refresh_dataset_stats()
        self.refresh_image_galleries()
        self.refresh_models_list()

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
                widget.image_deleted.connect(self.refresh_data)
                self.match_ready_layout.addWidget(widget, i // 5, i % 5)

        # Load not_match_ready images
        not_ready_path = os.path.join(self.dataset_path, "not_match_ready")
        if os.path.exists(not_ready_path):
            images = [f for f in os.listdir(not_ready_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            for i, img in enumerate(images[:20]):  # Limit display
                img_path = os.path.join(not_ready_path, img)
                widget = ImageWidget(img_path)
                widget.image_deleted.connect(self.refresh_data)
                self.not_ready_layout.addWidget(widget, i // 5, i % 5)

    def refresh_models_list(self):
        """Refresh models list"""
        self.models_list.clear()
        if os.path.exists(self.models_path):
            models = [f for f in os.listdir(self.models_path) if f.endswith('.pth')]
            for model in models:
                model_path = os.path.join(self.models_path, model)
                size = os.path.getsize(model_path) / (1024 * 1024)  # MB
                self.models_list.addItem(f"{model} ({size:.1f} MB)")
    
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

    def start_training(self):
        """Start model training in background"""
        if not os.path.exists(self.nn_classifier_path):
            QMessageBox.critical(self, "Error", f"nn-classifier directory not found: {self.nn_classifier_path}")
            return
        
        self.train_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.training_output.clear()
        
        # Collect settings
        settings = {
            'num_epochs': self.epochs_spin.value(),
            'batch_size': self.batch_spin.value(),
            'learning_rate': self.lr_spin.value(),
            'k_folds': self.kfold_spin.value(),
            'patience': self.patience_spin.value(),
            'seed': 42  # You can add a spinbox for this too
        }

        self.training_thread = TrainingThread(self.nn_classifier_path, settings)
        self.training_thread.progress_update.connect(self.update_training_output)
        self.training_thread.finished.connect(self.training_finished)
        self.training_thread.start()

    def update_training_output(self, text):
        """Update training output display"""
        self.training_output.append(text)
        self.training_output.ensureCursorVisible()
    
    def training_finished(self, success, message):
        """Handle training completion"""
        self.train_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_models_list()
        else:
            QMessageBox.critical(self, "Error", message)

    def select_prediction_image(self):
        """Select an image for prediction"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image for Prediction", "", "Images (*.jpg *.jpeg *.png)")
        
        if file_path:
            self.selected_file_label.setText(os.path.basename(file_path))
            self.current_prediction_image = file_path
            self.show_image_preview(file_path)
            self.predict_btn.setEnabled(True)  # Enable prediction button

    def test_selected_image(self):
        """Test the selected image from test_images folder"""
        selected = self.test_images_combo.currentText()
        if selected:
            image_path = os.path.join(self.test_images_path, selected)
            self.current_prediction_image = image_path
            self.selected_file_label.setText(selected)
            self.show_image_preview(image_path)
            self.run_prediction()

    def show_image_preview(self, image_path):
        """Show image preview"""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.setText("Invalid Image")
            self.preview_btn.setEnabled(False)

    def run_prediction(self):
        """Run prediction on selected image"""
        self.predict_btn.setEnabled(False)  # Disable button during prediction
        if not hasattr(self, 'current_prediction_image'):
            QMessageBox.warning(self, "Warning", "Please select an image first")
            return
        
        if not os.path.exists(self.nn_classifier_path):
            QMessageBox.critical(self, "Error", f"nn-classifier directory not found: {self.nn_classifier_path}")
            return
        
        self.prediction_result.setText("Running prediction...")
        
        self.prediction_thread = PredictionThread(self.nn_classifier_path, self.current_prediction_image)
        self.prediction_thread.result_ready.connect(self.show_prediction_result)
        self.prediction_thread.error_occurred.connect(self.show_prediction_error)
        self.prediction_thread.start()

    def show_prediction_result(self, prediction, image_path, confidence):
        """Display prediction result"""
        color = "#2e7d32" if prediction == "match_ready" else "#c62828"
        result_text = f"""
        <div style="color: {color}; font-size: 18px; font-weight: bold;">
        Prediction: {prediction.replace('_', ' ').title()}<br>
        Confidence: {confidence:.4f} ({confidence*100:.2f}%)
        </div>
        """
        self.prediction_result.setText(result_text)
    
    def show_prediction_error(self, error_message):
        """Display prediction error"""
        self.prediction_result.setText(f"Error: {error_message}")
        QMessageBox.critical(self, "Prediction Error", error_message)