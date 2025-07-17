---
id: ulkcc4ab2ws3yjh7zb56tyv
title: Front-End
desc: ''
updated: 1751589961652
created: 1751556253136
---
## Overview

The front-end of the Cricket-Ready Ball Classifier project is a web-app interface that allows users to upload images of cricket balls and receive predictions on whether the ball is match-ready or not. The interface is designed to be user-friendly and responsive, providing immediate feedback based on the uploaded image. It communicates with the back-end API to send the image data and receive the prediction results, which include the classification of the ball and the confidence level of the prediction.

## Technology Stack

- **Framework**: Vue.js
- **Styling**: CSS3
- **Deployment**: GitHub Pages

## User Interface Flow

```mermaid
flowchart TD
    A[User Visits Web-App] --> B[Takes Photo with Camera Interface]
    B --> C[Automatic Upload]
    C --> D[Show Loading State]
    D --> E[Send to Backend API]
    E --> F{API Response}
    F -->|Error| H[Show Error Message]
    H --> J[Show Retry Button]
    H --> I
    F -->|Success| G[Display Results]
    G --> I[Show Take Another Photo Button]
    I --> B
    J --> C
```

## User Experience Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Front-End
    participant B as Backend API
    participant M as NN Model

    U->>F: Visit web-app
    F->>U: Show camera interface
    U->>F: Take photo of cricket ball
    F->>U: Show loading state
    F->>B: POST /predict with image
    B->>M: Process image with ensemble
    M->>B: Return prediction and confidence
    B->>F: Return JSON response
    F->>U: Display results with confidence
    U->>F: Take another photo or retry (optional)
```

## Component Structure

```mermaid
graph TB
    App[App Component] --> Header[Header]
    App --> Main[Main Content]
    
    Main --> Camera[Camera Interface]
    Main --> Results[Results Display]
    Main --> Loading[Loading State]

    Camera --> Preview[Photo Preview]
    Camera --> Capture[Capture Photo]

    Results --> Prediction[Prediction Display]
    Results --> Confidence[Confidence Level]
    Results --> Retry[Retry Button]
    Results --> TakeAnother[Take Another Photo Button]

    Loading --> Spinner[Loading Spinner]
    Loading --> Progress[Progress Status]
```

## Key Features

### Upload and Capture Interface
- **Camera Interface**: Allows users to take photos directly from the web-app
- **Automatic Upload**: Photos are automatically uploaded to the back-end for processing on capture

### Results Display
- **Prediction Display**: Shows whether the ball is match-ready or not
- **Confidence Level**: Displays the confidence level of the prediction
- **Visual Feedback**: Colour-coded results (green for ready, red for not ready)
- **Image Display**: Shows the uploaded image alonside the results
- **Retry and Take Another Photo**: Options for users to retry the upload or take another photo

### User Experience
- **Responsive Design**: The interface is designed to work mainly on mobile devices, providing a seamless experience for users
- **Loading State**: Displays a loading spinner while the image is being processed
- **Error Handling**: Helpful error messages for failed uploads
- **Fast Performance**: Optimized images and minimal loading times for a smooth user experience

### Color Scheme
- **Primary Green**: `#2E7D32` (deep cricket field green)
- **Secondary Green**: `#4CAF50` (lighter green for buttons)
- **Accent Red**: `#C62828` (cricket ball red for "not-ready" states)
- **Background**: `#F8F9FA` (clean off-white)