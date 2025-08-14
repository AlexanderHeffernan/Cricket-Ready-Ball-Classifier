# API Reference

## Endpoints

### `POST /predict`
- **Description:** Predicts if an uploaded image is match-ready.
- **Request:** `multipart/form-data` with an `image` field.
- **Response:** JSON with prediction and confidence.

### `POST /train`
- **Description:** Triggers model training (admin only).
- **Request:** JSON with training parameters.
- **Response:** Training status.

## Example Request

```bash
curl -X POST -F "image=@/path/to/image.jpg" https://api.alexheffernan.dev/predict
```

## Example Response

```json
{
  "prediction": "match-ready",
  "confidence": 0.92
}
```