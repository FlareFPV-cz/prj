from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from models.user import User
from utils.auth import get_current_active_user
import httpx
from httpx import Timeout
import numpy as np
from datetime import datetime

router = APIRouter()

@router.get("/crop-yield/prediction/",
            summary="Predict crop yield potential",
            description="Analyzes soil and environmental factors to predict crop yield potential")
async def predict_crop_yield(
    lon: float = Query(..., description="Longitude of the location"),
    lat: float = Query(..., description="Latitude of the location"),
    crop_type: str = Query(..., description="Type of crop for yield prediction"),
    planting_date: str = Query(..., description="Planned planting date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user)
):
    """Predicts potential crop yield based on soil and environmental conditions."""
    try:
        # Validate planting date
        try:
            datetime.strptime(planting_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Fetch soil data for yield analysis
        async with httpx.AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.get(
                "https://rest.isric.org/soilgrids/v2.0/properties/query",
                params={
                    "lon": lon,
                    "lat": lat,
                    "property": ["nitrogen", "phh2o", "soc", "clay"],
                    "depth": ["0-30cm"],
                    "value": ["mean"]
                }
            )
            response.raise_for_status()
            soil_data = response.json()

        # Calculate yield potential factors
        soil_quality_score = _calculate_soil_quality(soil_data)
        climate_suitability = _assess_climate_suitability(crop_type, planting_date)
        
        # Calculate yield potential (simplified example)
        base_yield = _get_base_yield(crop_type)
        yield_potential = base_yield * soil_quality_score * climate_suitability

        return {
            "crop_type": crop_type,
            "predicted_yield": {
                "value": round(yield_potential, 2),
                "unit": "tons/hectare"
            },
            "confidence_level": "medium",
            "factors": {
                "soil_quality_score": soil_quality_score,
                "climate_suitability": climate_suitability
            },
            "recommendations": _generate_recommendations(soil_quality_score, climate_suitability)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting crop yield: {str(e)}")

def _calculate_soil_quality(soil_data: dict) -> float:
    """Calculate soil quality score based on soil properties."""
    try:
        properties = soil_data.get("properties", {})
        
        # Extract soil properties
        nitrogen = float(properties.get("nitrogen", {}).get("mean", 0))
        ph = float(properties.get("phh2o", {}).get("mean", 7))
        organic_carbon = float(properties.get("soc", {}).get("mean", 0))
        clay_content = float(properties.get("clay", {}).get("mean", 0))

        # Calculate weighted score (simplified)
        score = (
            (nitrogen / 0.2) * 0.3 +  # Nitrogen contribution
            (1 - abs(ph - 6.5) / 6.5) * 0.3 +  # pH optimality
            (organic_carbon / 20) * 0.2 +  # Organic carbon contribution
            (clay_content / 40) * 0.2  # Clay content contribution
        )

        return min(max(score, 0.0), 1.0)  # Normalize between 0 and 1
    except Exception:
        return 0.5  # Default moderate score

def _assess_climate_suitability(crop_type: str, planting_date: str) -> float:
    """Assess climate suitability for the crop (simplified example)."""
    # In a real implementation, this would consider:
    # - Historical climate data
    # - Seasonal patterns
    # - Crop-specific requirements
    # For now, return a simplified suitability score
    return 0.8  # Placeholder for climate suitability

def _get_base_yield(crop_type: str) -> float:
    """Get base yield potential for different crop types."""
    base_yields = {
        "wheat": 8.0,
        "corn": 12.0,
        "soybeans": 4.0,
        "rice": 7.0,
        "potatoes": 35.0
    }
    return base_yields.get(crop_type.lower(), 5.0)

def _generate_recommendations(soil_score: float, climate_score: float) -> List[str]:
    """Generate recommendations based on yield factors."""
    recommendations = []
    
    if soil_score < 0.4:
        recommendations.append("Consider soil amendments to improve soil quality")
    if soil_score < 0.6:
        recommendations.append("Implement crop rotation to enhance soil fertility")
    if climate_score < 0.7:
        recommendations.append("Consider adjusting planting date for better climate conditions")
    
    if not recommendations:
        recommendations.append("Current conditions are favorable for planting")
    
    return recommendations