import requests
import json
import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging
from scipy import stats
from tenacity import retry, stop_after_attempt, wait_fixed

# Logging Configuration
logging.basicConfig(
    filename="backend/ml/train_model.log",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Enhanced Configuration
CONFIG = {
    "data_dir": "backend/ml",
    "api": {
        "properties": ["bdod", "cec", "cfvo", "clay", "nitrogen", "ocd", "ocs", 
                      "phh2o", "sand", "silt", "soc", "wv0010", "wv0033", "wv1500"],
        "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"],
        "values": ["Q0.5", "mean"],
        "timeout": 30
    },
    "model": {
        "test_size": 0.2,
        "random_state": 42,
        "cv_folds": 5,
        "class_weights": "balanced",
        "min_samples_per_class": 3
    }
}

PATHS = {
    "raw_data": os.path.join(CONFIG['data_dir'], "raw_soil_data.json"),
    "processed_data": os.path.join(CONFIG['data_dir'], "augmented_soil_data.csv"),
    "model": os.path.join(CONFIG['data_dir'], "soil_model.pkl"),
    "scaler": os.path.join(CONFIG['data_dir'], "scaler.pkl"),
    "encoder": os.path.join(CONFIG['data_dir'], "encoder.pkl")
}

os.makedirs(CONFIG['data_dir'], exist_ok=True)

# Expanded European locations (lon, lat)
LOCATIONS = [
    (16.8884, 49.0556), (19.2829, 48.0942), (13.4813, 23.2002),
    (31.5189, 2.2091), (7.0920, 46.6426), (35.8888, 57.8238),
    (-2.9289, 54.3428), (12.0497, 47.3810), (-3.6673, 39.7862),
    (19.7499, 51.1784), (30.9311, 66.5789), (25.9734, 42.8452),
    (29.2434, 38.3094), (-5.3550, 34.0901), (20.4883, 41.6849),
    (13.6319, 19.5334), (10.9948, 44.1110), (35.9943, 48.1193),
    (-96.0409, 44.9087), (-73.1511, 4.9307)
]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_soil_data(lon: float, lat: float) -> dict:
    """Fetch soil data from ISRIC API with retry logic."""
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lon": lon,
        "lat": lat,
        "property": CONFIG['api']['properties'],
        "depth": CONFIG['api']['depths'],
        "value": CONFIG['api']['values']
    }
    
    try:
        response = requests.get(url, params=params, timeout=CONFIG['api']['timeout'])
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API Error for ({lon}, {lat}): {str(e)}")
        return None

def collect_dataset(locations: list) -> pd.DataFrame:
    """Collect data from API."""
    dataset = []
    for lon, lat in locations:
        raw_data = fetch_soil_data(lon, lat)
        if not raw_data:
            continue
            
        parsed_data = parse_location_data(raw_data)
        if parsed_data:
            parsed_data.update({'lon': lon, 'lat': lat})
            dataset.append(parsed_data)
    
    return pd.DataFrame(dataset)

def parse_location_data(location_data: dict) -> dict:
    """Enhanced feature engineering with depth profiles and ratios."""
    features = {}
    
    try:
        prop_data = {}
        for layer in location_data['properties']['layers']:
            prop_name = layer['name']
            unit_info = layer['unit_measure']
            conversion = 10 ** (-unit_info['d_factor'] / 10)

            for depth in layer['depths']:
                depth_label = depth['label'].replace('cm', '').replace('-', '_')
                for value_type, value in depth['values'].items():
                    key = f"{prop_name}_{depth_label}_{value_type}"
                    converted_value = float(value) * conversion if value else 0.0
                    prop_data[key] = round(converted_value, 2)
                    features[key] = prop_data[key]

        # Feature engineering
        features['clay_gradient'] = prop_data.get('clay_30_60_mean', 0) - prop_data.get('clay_0_5_mean', 0)
        features['ph_gradient'] = prop_data.get('phh2o_30_60_mean', 0) - prop_data.get('phh2o_0_5_mean', 0)
        
        depth_weights = {'0_5': 0.3, '5_15': 0.25, '15_30': 0.2, '30_60': 0.15, '60_100': 0.1}
        for prop in ['soc', 'cec', 'sand']:
            weighted_sum = sum(
                prop_data.get(f"{prop}_{depth}_mean", 0) * weight
                for depth, weight in depth_weights.items()
            )
            features[f'{prop}_depth_weighted'] = round(weighted_sum, 2)

        features['sand_clay_ratio'] = round(prop_data.get('sand_0_5_mean', 0) / 
                                          (prop_data.get('clay_0_5_mean', 0) + 1e-6), 2)
        features['soc_cec_balance'] = round(prop_data.get('soc_0_5_mean', 0) * 
                                          prop_data.get('cec_0_5_mean', 0), 2)
        features['water_capacity'] = round(prop_data.get('wv0033_0_5_mean', 0) - 
                                         prop_data.get('wv1500_0_5_mean', 0), 2)

        cec_values = [prop_data.get(f'cec_{depth}_mean', 0) for depth in depth_weights]
        features['cec_variability'] = round(np.std(cec_values) / (np.mean(cec_values) + 1e-6), 2)

    except KeyError as e:
        logging.error(f"Missing key: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Parsing error: {str(e)}")
        return None

    return features

def create_target_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Enhanced soil classification with inclusive thresholds."""
    try:
        conditions = [
            # Acidic Organic Rich
            (df['phh2o_0_5_mean'] < 6.2) & (df['soc_0_5_mean'] > 2.0),
            
            # Neutral High Fertility
            (df['phh2o_0_5_mean'].between(6.0, 7.8)) & 
            (df['cec_0_5_mean'] > 18) & 
            (df['clay_0_5_mean'] > 15),
            
            # Sandy Low Fertility
            (df['sand_0_5_mean'] > 65) & 
            (df['soc_0_5_mean'] < 2.0),
            
            # Clayey Poor Drainage
            (df['clay_0_5_mean'] > 35) & 
            (df['wv0033_0_5_mean'] > 30),
            
            # Calcareous
            (df['phh2o_0_5_mean'] > 7.2) & 
            (df['cec_0_5_mean'] > 15)
        ]
        
        choices = [
            'Acidic_Organic',
            'Neutral_HighFertility',
            'Sandy_LowFertility',
            'Clayey_PoorDrainage',
            'Calcareous'
        ]
        
        df['soil_type'] = np.select(conditions, choices, default='Other')
        
        # Log class distribution
        class_dist = df['soil_type'].value_counts().to_dict()
        logging.info(f"Initial class distribution: {class_dist}")
        
        return df
    except KeyError as e:
        logging.error(f"Target creation error: {str(e)}")
        return pd.DataFrame()

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Robust preprocessing with class preservation."""
    if df.empty:
        return df
    
    try:
        # Handle missing values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Iterative imputation
        from sklearn.experimental import enable_iterative_imputer
        from sklearn.impute import IterativeImputer
        
        numeric_cols = df.select_dtypes(include=np.number).columns
        imputer = IterativeImputer(random_state=CONFIG['model']['random_state'])
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # Remove constant columns
        if len(df) > 5:
            df = df.loc[:, df.nunique() > 1]
        
        # Post-preprocessing class check
        if 'soil_type' in df.columns:
            class_dist = df['soil_type'].value_counts().to_dict()
            logging.info(f"Post-preprocessing class distribution: {class_dist}")
        
        return df.round(2)
    except Exception as e:
        logging.error(f"Preprocessing failed: {str(e)}")
        return pd.DataFrame()

def train_model(df: pd.DataFrame):
    """Model training with comprehensive validation."""
    if df.empty or 'soil_type' not in df.columns:
        logging.error("Invalid training data")
        return

    try:
        # Class validation
        unique_classes = df['soil_type'].nunique()
        if unique_classes < 2:
            logging.error(f"Training aborted - Only {unique_classes} class present")
            return
            
        class_counts = df['soil_type'].value_counts()
        if class_counts.min() < CONFIG['model']['min_samples_per_class']:
            logging.error(f"Classes below minimum samples: {class_counts.to_dict()}")
            return

        # Encode target
        le = LabelEncoder()
        y = le.fit_transform(df['soil_type'])
        joblib.dump(le, PATHS['encoder'])
        
        columns_to_drop = ['soil_type', 'lon', 'lat']
        existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
        X = df.drop(columns=existing_columns_to_drop)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=CONFIG['model']['test_size'], 
            random_state=CONFIG['model']['random_state'],
            stratify=y
        )
        
        # Robust pipeline
        pipeline = ImbPipeline([
            ('scaler', StandardScaler()),
            ('smote', SMOTE(
                random_state=CONFIG['model']['random_state'],
                k_neighbors=2,
                sampling_strategy='not majority'
            )),
            ('classifier', GradientBoostingClassifier())
        ])
        
        # Hyperparameter grid
        param_grid = {
            'classifier__n_estimators': [100, 200],
            'classifier__learning_rate': [0.05, 0.1],
            'classifier__max_depth': [3, 5],
            'classifier__subsample': [0.8, 1.0]
        }
        
        grid_search = GridSearchCV(
            pipeline,
            param_grid,
            cv=CONFIG['model']['cv_folds'],
            scoring='f1_weighted',
            n_jobs=-1,
            error_score='raise'
        )
        
        grid_search.fit(X_train, y_train)
        
        # Save artifacts
        joblib.dump(grid_search.best_estimator_, PATHS['model'])
        joblib.dump(grid_search.best_estimator_.named_steps['scaler'], PATHS['scaler'])
        
        # Evaluation
        y_pred = grid_search.predict(X_test)
        logging.info(f"Best Parameters: {grid_search.best_params_}")
        logging.info(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
        logging.info("Classification Report:\n" + classification_report(y_test, y_pred, target_names=le.classes_))
        logging.info("Top Features:\n" + 
                    str(pd.Series(grid_search.best_estimator_.named_steps['classifier'].feature_importances_, 
                                index=X.columns).sort_values(ascending=False).head(10)))
        
    except Exception as e:
        logging.error(f"Training failed: {str(e)}", exc_info=True)

def main():
    """Main execution flow."""
    try:
        # # Data collection
        # logging.info("Starting data collection")
        # df = collect_dataset(LOCATIONS)
        # if df.empty:
        #     logging.error("No data collected")
        #     return
            
        # # Target creation
        # logging.info("Creating target variable")
        # df = create_target_variable(df)
        # if df.empty:
        #     logging.error("Target creation failed")
        #     return
            
        # # Preprocessing
        # logging.info("Preprocessing data")
        # df = preprocess_data(df)
        # if df.empty:
        #     logging.error("Empty data after preprocessing")
        #     return
        
        # # Save and train
        # logging.info("Saving processed data")
        
        # df.to_csv(PATHS['processed_data'], mode='a', header=False, index=False)    
        df = pd.read_csv(PATHS['processed_data'])
        
        logging.info("Starting model training")
        train_model(df)
        logging.info("Training completed")
        
    except Exception as e:
        logging.error(f"Main error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()