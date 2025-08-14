# NN-Classifier Training

## How to Train

1. Place your labeled images in `dataset/match_ready/` and `dataset/not_match_ready/`.
2. (Optional) Adjust training parameters in `train.py` or pass via CLI.
3. Run:
   ```bash
   source venv/bin/activate
   python train.py
   ```

## Training Parameters

- --batch_size (default: 16)
- --num_epochs (default: 15)
- --learning_rate (default: 0.001)
- --k_folds (default: 3)
- --patience (default: 5)
- --seed (default: 42)

## Output

- Training logs are printed to stdout and can be captured by the GUI/backend.
- Models are saved in the `models/` directory.