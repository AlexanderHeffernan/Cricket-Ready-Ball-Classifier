# Architecture

## Folder Structure

- `main.py` – Entry point for the GUI application.
- `main_window.py` – Main window logic and tab management.
- `views/` – Contains code for each tabe (Dataset, Training, Prediction, Models).
- `widgets/` – Custom widgets (e.g., `ImageWidge`).
- `threads/` – Background threads for training and prediction.

## Design Principles

- **Modularity:** Each tab and component is in its own file for maintainability.
- **Signals and Slots:** PyQt5 signals are used for communication between threads and the UI.
- **Threading:** Long-running tasks (training, prediction) run in background threads to keep the UI responsive.