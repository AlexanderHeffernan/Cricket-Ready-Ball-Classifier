# Component Reference

## Tabs

### Dataset Tab
- Upload images for "match-ready" and "not-match-ready" classes.
- View and manage image galleries.
- Delete images directly from the GUI.

### Training Tab
- Configure training parameters (epochs, batch size, learning rate, etc.).
- Start model training in the background.
- View real-time training logs and progress.

### Prediction Tab
- Select an image for prediction.
- Preview the selected image.
- Run prediction and view results.

### Models Tab
- View a list of trained models.

## Widgets

- **ImageWidget:** Displays an image with filename and delete button.

## Threads

- **TrainingThread:** Runs model training in the background.
- **PredictionThread:** Runs image prediction in the background.