# API Reference

## Endpoints

### `POST /predict`
- **Description:** Predicts if an uploaded image is match-ready.
- **Request:** `multipart/form-data` with an `image` field.
- **Response:** JSON with prediction and confidence.

### `POST /training`
- **Description:** Public contribution submission, not a model-training trigger.
- **Request:** Multipart `image` plus `label` (`match_ready` or `not_match_ready`).
- **Response:** HTTP 200 JSON with `status: success`, `review_status: pending`, filename and label.
- Images go to quarantine and require operator review before dataset inclusion.

Both routes accept only single-frame JPEG/PNG, up to 5 MiB, 4096 per side and
12 million pixels. Invalid input returns 400, oversized fields 413, upload timeout
408, rate limit 429, capacity/quota exhaustion 503, processing timeout 504, and
internal processing failures a generic 500. See [Security](Back-End.Security.md).

## Example Request

```bash
curl -X POST -F "image=@/path/to/image.jpg" https://api.alexheffernan.dev/predict
```

## Example Response

```json
{
  "prediction": "match_ready",
  "confidence": 0.92
}
```
