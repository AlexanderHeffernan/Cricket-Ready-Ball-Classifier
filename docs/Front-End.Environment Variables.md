# Front-End Environment Variables

## VUE_APP_BACKEND_URL
- **Purpose**: Specifies the base URL for the backend API.
- **Location**: `.env.production`, `.env.development`
- **Example**:
  ```
  VUE_APP_BACKEND_URL=https://your-backend-url.com
  ```
- **Usage**: Used in API calls in `PredictView.vue` and `TrainView.vue`.