import sys
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
import os

class TrainingThread(QThread):
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, script_path, settings=None):
        super().__init__()
        self.script_path = script_path
        self.settings = settings or {}

    def run(self):
        try:
            # Delete contents of the models folder before training
            models_dir = os.path.join(self.script_path, "models")
            if os.path.exists(models_dir):
                for filename in os.listdir(models_dir):
                    file_path = os.path.join(models_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        self.progress_update.emit(f"Failed to delete {file_path}: {str(e)}")
                        
            venv_python = os.path.abspath(os.path.join(self.script_path, "venv", "bin", "python3"))
            if not os.path.exists(venv_python):
                venv_python = os.path.abspath(os.path.join(self.script_path, "venv", "bin", "python"))
            if not os.path.exists(venv_python):
                self.finished.emit(False, f"Python executable not found in venv: {venv_python}")
                return

            # Build command with settings
            cmd = [venv_python, '-u', 'train.py']
            if self.settings:
                for k, v in self.settings.items():
                    cmd.append(f"--{k}")
                    cmd.append(str(v))

            process = subprocess.Popen(
                cmd,
                cwd=self.script_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

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