from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
import joblib
import os
import logging
import numpy as np

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

@router.get("/predict", summary="Predict soil condition & recommended crops")
def predict_soil():
    """Predicts soil condition & provides crop recommendations."""
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="⚠️ Model not found! Train it first using `train_model.py`.")

    try:
        test_data = np.random.rand(1, scaler.n_features_in_) 
        scaled_data = scaler.transform(test_data)
        prediction = model.predict(scaled_data)[0]

        recommendations = {
            'Acidic': "Recommended: Rice, Blueberries",
            'Slightly Acidic': "Recommended: Apples, Tomatoes",
            'Neutral': "Recommended: Wheat, Corn",
            'Alkaline': "Recommended: Sugar Beets, Barley"
        }

        return {
            "condition": prediction,
            "recommendation": recommendations.get(prediction, "Recommended: General Vegetables")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train", summary="Retrain the soil model in background")
async def retrain_model(background_tasks: BackgroundTasks):
    """Retrains the model asynchronously."""
    if not os.path.exists("./train_model.py"):
        raise HTTPException(status_code=500, detail="⚠️ Training script not found!")

    background_tasks.add_task(os.system, "python train_model.py")
    return {"message": "Model retraining started in background. Check logs for updates."}
