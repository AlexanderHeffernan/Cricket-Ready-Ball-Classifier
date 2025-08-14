"""
PredictionThread: Runs image prediction in a background thread.
- Uses the project's venv to run predict.py with the selected image.
- Emits result_ready(prediction: str, image_path: str, confidence: float) on success.
- Emits error_occurred(error_message: str) on failure.
"""

import os
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

class PredictionThread(QThread):
    result_ready = pyqtSignal(str, str, float)
    error_occurred = pyqtSignal(str)

    def __init__(self, script_path, image_path):
        """
        Args:
            script_path (str): Path to the nn-classifier directory.
            image_path (str): Path to the image file to predict.
        """
        super().__init__()
        self.script_path = script_path
        self.image_path = image_path

    def run(self):
        try:
            # Find the venv Python interpreter
            venv_python = os.path.abspath(os.path.join(self.script_path, "venv", "bin", "python3"))

            # Run the prediction script in the nn-classifier directory
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