import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import os

class PredictionThread(QThread):
    """Background thread for single image prediction"""
    result_ready = pyqtSignal(str, str, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, script_path, image_path):
        super().__init__()
        self.script_path = script_path
        self.image_path = image_path

    def run(self):
        try:
            # Run prediction script
            venv_python = os.path.abspath(os.path.join(self.script_path, "venv", "bin", "python3"))
            result = subprocess.run(
                [venv_python, 'nn-classifier/predict.py', self.image_path],
                cwd=os.path.join(self.script_path, '../'),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Parse output: "Prediction: match_ready; Confidence: 0.8542"
                output = result.stdout.strip()
                if "Prediction:" in output and "Confidence:" in output:
                    parts = output.split(";")
                    prediction = parts[0].split(":")[1].strip()
                    confidence = float(parts[1].split(":")[1].strip())
                    self.result_ready.emit(prediction, self.image_path, confidence)
                else:
                    self.error_occurred.emit(f"Unexpected output format: {output}")
            else:
                self.error_occurred.emit(f"Prediction failed: {result.stderr}")

        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")