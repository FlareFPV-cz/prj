import os
import json
import logging
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Logging Configuration
logging.basicConfig(
    filename="backend/ml/train_model.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Paths
MODEL_PATH = "backend/ml/models/soil_model.pkl"
SCALER_PATH = "backend/ml/models/scaler.pkl"
DATA_PATH = "backend/ml/models/response.json"

logging.info("Current working directory: %s", os.getcwd())

# =========================== Load & Process Data

def parse_soil_data(json_data):
    """
    Parse soil data from JSON into a DataFrame.
    """
    features = []
    for layer in json_data['properties']['layers']:
        name = layer['name']
        for depth in layer['depths']:
            features.append({
                'layer': name,
                'top_depth': depth['range']['top_depth'],
                'bottom_depth': depth['range']['bottom_depth'],
                **depth['values']
            })
    return pd.DataFrame(features)

if not os.path.exists(DATA_PATH):
    logging.error("Error: %s not found", DATA_PATH)
    raise FileNotFoundError(f"Error: {DATA_PATH} not found")

with open(DATA_PATH, 'r') as file:
    json_data = json.load(file)

# Parse and process the dataset
soil_df = parse_soil_data(json_data)
soil_df['depth'] = soil_df['bottom_depth'] - soil_df['top_depth']
soil_df.fillna(0, inplace=True)

soil_df['crop_recommendation'] = pd.qcut(
    soil_df['mean'], q=4, labels=['Acidic', 'Slightly Acidic', 'Neutral', 'Alkaline']
)

# Remove rare classes
class_counts = soil_df['crop_recommendation'].value_counts()
rare_classes = class_counts[class_counts < 2].index.tolist()
soil_df = soil_df[~soil_df['crop_recommendation'].isin(rare_classes)]

# Prepare features and labels
X = soil_df.drop(columns=['crop_recommendation', 'layer'])
y = soil_df['crop_recommendation']

# Scale the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, SCALER_PATH)
logging.info("Scaler saved at %s", SCALER_PATH)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Debug: Check class distribution before SMOTE
print("Class Distribution Before SMOTE:\n", y_train.value_counts())

# Handle class imbalance using SMOTE
smote = SMOTE(sampling_strategy='not majority', random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# Debug: Check class distribution after SMOTE
print("Class Distribution After SMOTE:\n", y_train.value_counts())

# Model training with GridSearchCV
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_classifier = RandomForestClassifier(random_state=42, class_weight='balanced')
grid_search = GridSearchCV(
    estimator=rf_classifier,
    param_grid=param_grid,
    cv=3,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

# Save the best model
best_model = grid_search.best_estimator_
joblib.dump(best_model, MODEL_PATH)
logging.info("Best model saved at %s", MODEL_PATH)
print("Model training complete and saved!")
