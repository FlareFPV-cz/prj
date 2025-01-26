from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter, Depends
import joblib
import os
import logging
import pandas as pd  # Added for proper DataFrame transformation
import json  # Added for debugging
from routers.analysis import get_soil_data
from models.user import User
from models.response.pred import PredResponse
from utils.auth import get_current_active_user

router = APIRouter()

# Paths
MODEL_PATH = "./ml/soil_model.pkl"
SCALER_PATH = "./ml/scaler.pkl"

# Load Model & Scaler
if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    logging.info("Model & Scaler loaded successfully")
else:
    model = None
    scaler = None
    logging.error("Model or Scaler not found! Train the model first.")


DEFAULT_DEPTHS = [
    "0-5cm", "0-30cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"
]
DEFAULT_VALUES = ["Q0.5", "Q0.05", "Q0.95", "mean", "uncertainty"]
REQUIRED_FEATURES = ["bdod", "cec", "clay", "nitrogen", "ocd", "phh2o", "sand", "silt"]


@router.get("/predict", response_model=PredResponse,     
            summary="Predict soil condition and recommend crops",
            description="""
            Predicts soil condition based on location (latitude and longitude) using a machine learning model. 
            Returns the predicted condition, confidence score, crop recommendations, and detailed soil data.

            **Inputs:**
            - Longitude (`lon`) and Latitude (`lat`).

            **Outputs:**
            - Predicted condition (e.g., Acidic, Neutral).
            - Confidence score (0-1).
            - Crop recommendations based on condition.
            - Fetched soil data for the location.

            **Error Handling:**
            - Returns an error if the model or soil data is unavailable.
            """)
async def predict_soil(lon: float, 
                       lat: float, 
                       current_user: User = Depends(get_current_active_user)
                       ):
    """Predicts soil condition & provides crop recommendations using real soil data."""
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="⚠️ Model not found! Train it first using `train_model.py`.")


    soil_data = await get_soil_data(lon, lat, REQUIRED_FEATURES, DEFAULT_DEPTHS, DEFAULT_VALUES)
    if "data" not in soil_data:
        raise HTTPException(status_code=500, detail="Failed to fetch soil data.")
    
    # Debug: Print full fetched soil data
    # print("Full Soil Data:", json.dumps(soil_data, indent=4))
    
    try:
        # Fix: Extract actual feature values
        feature_values = []
        for feat in REQUIRED_FEATURES:
            feature = next((layer for layer in soil_data["data"]["properties"]["layers"] if layer["name"] == feat), None)
            mean_value = feature["depths"][0]["values"].get("mean", 0.0) if feature else 0.0
            feature_values.append(mean_value)
        
        # print("Extracted Features after Fix:", feature_values)
        
        # Debug: Check if scaler's feature names match input
        if hasattr(scaler, "feature_names_in_"):
            # print("Scaler Feature Names:", scaler.feature_names_in_)
            
            # Convert to DataFrame to match scaler feature names and avoid warnings
            feature_df = pd.DataFrame([feature_values], columns=scaler.feature_names_in_)
            scaled_data = scaler.transform(feature_df)
        else:
            # Fallback for older scikit-learn versions
            scaled_data = scaler.transform([feature_values])

        # Make prediction with probability estimation
        probabilities = model.predict_proba(scaled_data)
        confidence = max(probabilities[0])
        prediction = model.predict(scaled_data)[0]
        # print("Prediction Output:", prediction, "Confidence:", confidence)

        recommendations = {
            'Acidic': "Recommended: Rice, Blueberries",
            'Slightly Acidic': "Recommended: Apples, Tomatoes",
            'Neutral': "Recommended: Wheat, Corn",
            'Alkaline': "Recommended: Sugar Beets, Barley"
        }

        return {
            "condition": prediction,
            "confidence": confidence,
            "recommendation": recommendations.get(prediction, "Recommended: General Vegetables"),
            "soil_data": soil_data
        }

    except Exception as e:
        logging.error("Prediction error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))