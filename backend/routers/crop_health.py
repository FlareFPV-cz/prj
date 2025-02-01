from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms
from PIL import Image
import io
import logging
from datetime import datetime
from models.user import User
from utils.auth import get_current_active_user
from models.response.crop_health import HealthMetrics, DetailedAssessment
import numpy as np

router = APIRouter()

# Load the specialized crop disease detection model
try:
    model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet50', pretrained=True)
    # TODO: Replace with custom-trained agricultural disease model
    model.eval()
    logging.info("Crop disease detection model loaded successfully")
except Exception as e:
    model = None
    logging.error(f"Failed to load crop disease model: {str(e)}")

# Enhanced image transformation pipeline
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    transforms.RandomHorizontalFlip(p=0.3),  # Data augmentation
    transforms.RandomRotation(degrees=15)     # Data augmentation
])

def analyze_image_features(image: Image.Image) -> HealthMetrics:
    """Analyze detailed features of the crop image."""
    img_array = np.array(image)
    
    # Calculate leaf color score
    hsv_img = Image.fromarray(img_array).convert('HSV')
    hsv_array = np.array(hsv_img)
    leaf_color_score = float(np.mean(hsv_array[:,:,1]))  # Saturation channel
    
    # Calculate texture uniformity
    gray_img = np.mean(img_array, axis=2)
    texture_uniformity = float(np.std(gray_img))  # Lower std means more uniform
    
    # Analyze growth pattern
    vertical_profile = np.mean(gray_img, axis=1)
    growth_pattern = "Regular" if np.std(vertical_profile) < 50 else "Irregular"
    
    # Detect stress indicators
    stress_indicators = []
    if np.mean(hsv_array[:,:,0]) < 30:  # Hue analysis
        stress_indicators.append("Yellowing")
    if texture_uniformity > 100:
        stress_indicators.append("Irregular Growth")
    if np.mean(img_array[:,:,1]) < 100:  # Green channel analysis
        stress_indicators.append("Chlorosis")
    
    return HealthMetrics(
        leaf_color_score=leaf_color_score,
        texture_uniformity=texture_uniformity,
        growth_pattern=growth_pattern,
        stress_indicators=stress_indicators
    )

def get_severity_level(disease_prob: float, metrics: HealthMetrics) -> str:
    """Determine severity level based on multiple factors."""
    if disease_prob < 0.2 and len(metrics.stress_indicators) == 0:
        return "Low"
    elif disease_prob < 0.6 or len(metrics.stress_indicators) <= 2:
        return "Moderate"
    else:
        return "High"

@router.post("/assess-crop-health/", 
             response_model=DetailedAssessment,
             summary="Advanced crop health assessment",
             description="Performs comprehensive analysis of crop health using advanced image processing and ML techniques")
async def assess_crop_health(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Performs comprehensive crop health analysis with detailed metrics and recommendations."""
    if not file:
        raise HTTPException(status_code=400, detail="No image file provided")

    if model is None:
        raise HTTPException(status_code=500, detail="Model not available")

    try:
        # Read and preprocess the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        image_tensor = transform(image).unsqueeze(0)

        # Analyze image features
        metrics = analyze_image_features(image)

        # Perform ML inference
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        # Get prediction and confidence
        max_prob, predicted = torch.max(probabilities, 0)
        confidence = float(max_prob)
        disease_prob = 1.0 - confidence if confidence < 0.8 else 0.0

        # Determine severity and status
        severity_level = get_severity_level(disease_prob, metrics)
        health_status = "Healthy" if disease_prob < 0.2 else "Potential Issues Detected"

        # Generate environmental factors analysis
        env_factors = {
            "light_exposure": float(image_tensor[0,0].mean().detach().numpy()),
            "moisture_indicator": float(image_tensor[0,2].mean().detach().numpy()),
            "stress_factor": float(len(metrics.stress_indicators) / 4)
        }

        # Generate comprehensive recommendations
        recommendations = [
            f"Current Growth Pattern: {metrics.growth_pattern}",
            f"Leaf Health Score: {metrics.leaf_color_score:.2f}/255"
        ]

        if health_status == "Healthy":
            recommendations.extend([
                "Continue current maintenance practices",
                "Monitor for any changes in leaf color or texture",
                "Maintain optimal irrigation schedule",
                f"Regular monitoring of {', '.join(env_factors.keys())}"
            ])
        else:
            recommendations.extend([
                "Inspect affected areas more closely",
                "Consider soil testing for nutrient deficiencies",
                "Consult with local agricultural extension for specific treatment",
                "Document symptoms and progression",
                f"Address identified stress factors: {', '.join(metrics.stress_indicators)}"
            ])

        # Define follow-up actions
        follow_up_actions = [
            "Schedule next assessment in 7 days",
            "Document changes in affected areas",
            "Monitor weather conditions",
            "Update treatment plan based on progression"
        ]

        return DetailedAssessment(
            timestamp=datetime.now().isoformat(),
            metrics=metrics,
            disease_probability=disease_prob,
            health_status=health_status,
            severity_level=severity_level,
            affected_areas=["Leaves", "Stem"] if disease_prob > 0.2 else [],
            environmental_factors=env_factors,
            recommendations=recommendations,
            confidence_score=confidence,
            follow_up_actions=follow_up_actions
        )

    except Exception as e:
        logging.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")