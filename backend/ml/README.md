# Machine Learning Module

## Directory Structure

```
ml/
├── data/           # Data files
│   ├── raw/        # Raw data
│   └── processed/  # Processed data
├── models/         # Saved model files
├── src/           # Source code
│   ├── training/  # Training scripts
│   ├── inference/ # Inference scripts
│   └── utils/     # Utility functions
└── logs/          # Log files
```

## Setup

1. Install required dependencies
2. Place raw data in `data/raw/`
3. Run preprocessing scripts
4. Train models using scripts in `src/training/`

## File Descriptions

- `src/training/train.py`: Main model training script
- `src/utils/augment.py`: Data augmentation utilities
- `src/inference/predict.py`: Model inference script

## Models

- Soil classification model (RandomForest)
- GPT-2 fine-tuned model for soil analysis