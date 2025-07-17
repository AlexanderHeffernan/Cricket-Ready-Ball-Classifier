---
id: fngpbgwv4wkoi0iek0inakj
title: Training Tool
desc: ''
updated: 1751607469485
created: 1751606967047
---
The front-end will have a optional training tool that allows users to upload images of cricket balls and manually label them as match-ready or not. This tool will be used to grow the dataset for training the neural network model. The user will be able to upload images, view them, and assign labels. The labeled images will be sent to the [[Back-End]] for storage and later manual review by the team.

```mermaid
flowchart TD
    A[User Visits Web-App] --> B[Opens Training Tool]
    B --> C[Takes Photo with Camera Interface]
    C --> D[Assign Label: Match-Ready or Not]
    D --> E[Show Loading State]
    E --> F[Send to Back-End API]
    F --> G{API Response}
    G -->|Success| H[Display Success Message]
    G -->|Error| I[Show Error Message with Retry]
    H --> J[Take Another Photo]
    I --> E
    J --> C
```