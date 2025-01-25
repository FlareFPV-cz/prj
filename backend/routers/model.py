from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
import joblib
import os
import logging
import numpy as np
from routers.analysis import get_soil_data
# FastAPI App
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

# =========================== Endpoints
DEFAULT_DEPTHS = [
    "0-5cm", "0-30cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"
]
DEFAULT_VALUES = ["Q0.5", "Q0.05", "Q0.95", "mean", "uncertainty"]

@router.get("/predict", summary="Predict soil condition & recommended crops")
async def predict_soil(lon: float, lat: float):
    """Predicts soil condition & provides crop recommendations using real soil data."""
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="⚠️ Model not found! Train it first using `train_model.py`.")

    REQUIRED_FEATURES = ["bdod", "cec", "clay", "nitrogen", "ocd", "phh2o", "sand", "silt"]

    soil_data = await get_soil_data(lon, lat, REQUIRED_FEATURES, DEFAULT_DEPTHS, DEFAULT_VALUES)
    if "data" not in soil_data:
        raise HTTPException(status_code=500, detail="Failed to fetch soil data.")

    try:
        # Extract only the 8 required features
        feature_values = [soil_data["data"].get(feat, {}).get("mean", 0.0) for feat in REQUIRED_FEATURES]
        
        # Convert to NumPy array and reshape
        feature_array = np.array([feature_values]).reshape(1, -1)

        # Scale the data
        scaled_data = scaler.transform(feature_array)

        # Make prediction
        prediction = model.predict(scaled_data)[0]
        print(scaled_data)
        print('\n')
        print(prediction)

        recommendations = {
            'Acidic': "Recommended: Rice, Blueberries",
            'Slightly Acidic': "Recommended: Apples, Tomatoes",
            'Neutral': "Recommended: Wheat, Corn",
            'Alkaline': "Recommended: Sugar Beets, Barley"
        }

        return {
            "condition": prediction,
            "recommendation": recommendations.get(prediction, "Recommended: General Vegetables"),
            "soil_data": soil_data
        }

    except Exception as e:
        logging.error("Prediction error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/train", summary="Retrain the soil model in background")
async def retrain_model(background_tasks: BackgroundTasks):
    """Retrains the model asynchronously."""
    training_script = "./train_model.py"
    if not os.path.exists(training_script):
        logging.error("Training script not found!")
        raise HTTPException(status_code=500, detail="⚠️ Training script not found!")

    background_tasks.add_task(os.system, f"python {training_script}")
    logging.info("Model retraining initiated.")
    return {"message": "Model retraining started in background. Check logs for updates."}
