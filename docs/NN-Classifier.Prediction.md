# NN-Classifier Prediction

## How to Run a Prediction

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
2. Run:
   ```bash
   python predict.py /path/to/image.jpg
   ```

## Output

- Prints prediction and confidence to stdout, e.g.:
    ```
    Prediction: match_ready; Confidence: 0.92
    ```

## Integration

- The backend and GUI call predict.py as a subprocess and parse the output.