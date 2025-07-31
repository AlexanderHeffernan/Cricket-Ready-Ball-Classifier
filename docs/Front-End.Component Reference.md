# Front-End Component Reference

## CameraComponent.vue
- **Props**: `isLoading`, `glowClass`, `error`
- **Emits**: `captured`, `cameraError`, `retry`, `ready`
- **Description**: Handles camera access, photo capture, error display, and emits events for parent components.

## LoadingOverlay.vue
- **Props**: `complete`
- **Description**: Displays a loading animation overlay during app/image loading.

## LoadingAnimation.vue
- **Description**: SVG-based cricket-themed loading animation.

## BackgroundImage.vue
- **Emits**: `image-loaded`
- **Description**: Loads and displays the background image with overlay effects.

## PredictView.vue
- **Description**: Main prediction workflow. Integrates camera, handles API calls, displays results.

## TrainView.vue
- **Description**: Training tool for user-labeled data collection.