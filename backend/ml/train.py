import pandas as pd
import numpy as np
import joblib
import os
import json
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Logging Configuration
# logging.basicConfig(filename="backend/ml/train_model.log", level=logging.INFO)

# Paths
MODEL_PATH = "backend/ml/soil_model.pkl"
SCALER_PATH = "backend/ml/scaler.pkl"
DATA_PATH = "backend/ml/response.json"

print("////" + os.getcwd())

# =========================== Load & Process Data
def parse_soil_data(json_data):
    features = []
    for layer in json_data['data']['properties']['layers']:
        name = layer['name']
        for depth in layer['depths']:
            features.append({
                'layer': name,
                'top_depth': depth['range']['top_depth'],
                'bottom_depth': depth['range']['bottom_depth'],
                **depth['values']
            })
    return pd.DataFrame(features)

# Load Dataset
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Error: {DATA_PATH} not found")

with open(DATA_PATH, 'r') as file:
    json_data = json.load(file)

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

# Prepare Features & Labels
X = soil_df.drop(columns=['crop_recommendation', 'layer'])
y = soil_df['crop_recommendation']

# Train Scaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, SCALER_PATH)  # ✅ Save scaler

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Handle Class Imbalance
k_neighbors = max(1, min(5, min(y_train.value_counts()) - 1))
smote = SMOTE(k_neighbors=k_neighbors, random_state=42)
X_train, y_train = smote.fit_resample(X_train, y_train)

# Model Training
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Save Best Model
joblib.dump(grid_search.best_estimator_, MODEL_PATH)
logging.info("Model training complete & saved!")
print("Model training complete & saved!")
