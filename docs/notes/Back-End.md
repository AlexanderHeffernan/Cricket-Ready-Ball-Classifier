---
id: 87ckbw69y6e172qqi1z029t
title: Back-End
desc: ''
updated: 1751613965475
created: 1751613762926
---
## Overview

The back-end of the Cricket-Ready Ball Classifier project is responsible for processing image uploads, running predictions using a pre-trained ensemble model, and returning the results to the front-end. It is built using Rust, and runs the pre-trained model with python and extracting the output.

## Technology Stack
- **Language**: Rust
- **Framework**: rusty-api
- **Model Execution**: Python (via subprocess)
- **Deployment**: Raspberry Pi 5
- **Model**: Pre-trained ensemble model
- **API Endpoint**: `/predict` and `/train`

## API Endpoints
### `/predict`
- **Method**: POST
- **Description**: Accepts an image file, processes it, and returns a prediction on whether the cricket ball is match-ready, not match-ready, or not a cricket ball.
- **

### `/train`
- **Method**: POST
- **Description**: Accepts a label and an image file, and saves the image for later manual addition to the training dataset. This endpoint is used to collect data for future model training, and it does not trigger immediate model retraining.