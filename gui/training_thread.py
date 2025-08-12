import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import os

class TrainingThread(QThread):
    """Background thread for model training to prevent GUI freezing"""
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path
    
    def run(self):
        try:
            # Run training script and capture output
            venv_python = os.path.abspath(os.path.join(self.script_path, "venv", "bin", "python3"))
            process = subprocess.Popen(
                [venv_python, '-u', 'train.py'], 
                cwd=self.script_path,
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output in real-time
            for line in iter(process.stdout.readline, ''):
                self.progress_update.emit(line.rstrip())
            
            process.stdout.close()
            process.wait()
            
            if process.returncode == 0:
                self.finished.emit(True, "Training completed successfully!")
            else:
                self.finished.emit(False, f"Training failed with code {process.returncode}")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")