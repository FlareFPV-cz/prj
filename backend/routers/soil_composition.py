from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from models.user import User
from utils.auth import get_current_active_user
from models.response.soil import SoilResponse
import httpx
from httpx import Timeout
import numpy as np

router = APIRouter()

@router.get("/soil-composition/nutrient-analysis/", 
            summary="Analyze soil nutrient composition",
            description="Provides detailed analysis of soil nutrient levels and recommendations")
async def analyze_soil_nutrients(
    lon: float = Query(..., description="Longitude of the location"),
    lat: float = Query(..., description="Latitude of the location"),
    depth: str = Query("0-30cm", description="Soil depth for analysis"),
    current_user: User = Depends(get_current_active_user)
):
    """Analyzes soil nutrient composition and provides recommendations."""
    try:
        # Fetch soil data for nutrient analysis
        async with httpx.AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.get(
                "https://rest.isric.org/soilgrids/v2.0/properties/query",
                params={
                    "lon": lon,
                    "lat": lat,
                    "property": ["nitrogen", "phh2o", "cec"],
                    "depth": [depth],
                    "value": ["mean"]
                }
            )
            response.raise_for_status()
            soil_data = response.json()

        # Extract and analyze nutrient levels
        properties = soil_data.get("properties", {})
        analysis = {
            "nitrogen_level": _analyze_nitrogen(properties),
            "ph_level": _analyze_ph(properties),
            "cec_level": _analyze_cec(properties),
            "recommendations": []
        }

        # Generate recommendations
        if analysis["nitrogen_level"] < 0.15:
            analysis["recommendations"].append("Consider nitrogen fertilization")
        if analysis["ph_level"] < 6.0:
            analysis["recommendations"].append("Soil pH is acidic, consider liming")
        if analysis["cec_level"] < 10:
            analysis["recommendations"].append("Low nutrient retention capacity, consider organic matter addition")

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing soil nutrients: {str(e)}")

@router.get("/soil-composition/texture-analysis/",
            summary="Analyze soil texture composition",
            description="Provides detailed analysis of soil texture and physical properties")
async def analyze_soil_texture(
    lon: float = Query(..., description="Longitude of the location"),
    lat: float = Query(..., description="Latitude of the location"),
    depth: str = Query("0-30cm", description="Soil depth for analysis"),
    current_user: User = Depends(get_current_active_user)
):
    """Analyzes soil texture composition and provides physical property insights."""
    try:
        # Fetch soil texture data
        async with httpx.AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.get(
                "https://rest.isric.org/soilgrids/v2.0/properties/query",
                params={
                    "lon": lon,
                    "lat": lat,
                    "property": ["sand", "silt", "clay"],
                    "depth": [depth],
                    "value": ["mean"]
                }
            )
            response.raise_for_status()
            soil_data = response.json()

        # Calculate texture class and properties
        properties = soil_data.get("properties", {})
        texture_analysis = _calculate_texture_class(properties)
        
        return {
            "texture_class": texture_analysis["class"],
            "composition": {
                "sand": texture_analysis["sand"],
                "silt": texture_analysis["silt"],
                "clay": texture_analysis["clay"]
            },
            "characteristics": {
                "water_retention": texture_analysis["water_retention"],
                "drainage": texture_analysis["drainage"],
                "aeration": texture_analysis["aeration"]
            },
            "management_recommendations": texture_analysis["recommendations"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing soil texture: {str(e)}")

def _analyze_nitrogen(properties: dict) -> float:
    """Analyze nitrogen levels from soil properties."""
    try:
        nitrogen_data = properties.get("nitrogen", {})
        return float(nitrogen_data["mean"])
    except (KeyError, TypeError):
        return 0.0

def _analyze_ph(properties: dict) -> float:
    """Analyze pH levels from soil properties."""
    try:
        ph_data = properties.get("phh2o", {})
        return float(ph_data["mean"])
    except (KeyError, TypeError):
        return 7.0

def _analyze_cec(properties: dict) -> float:
    """Analyze Cation Exchange Capacity from soil properties."""
    try:
        cec_data = properties.get("cec", {})
        return float(cec_data["mean"])
    except (KeyError, TypeError):
        return 0.0

def _calculate_texture_class(properties: dict) -> dict:
    """Calculate soil texture class and related properties."""
    try:
        sand = float(properties.get("sand", {}).get("mean", 0))
        silt = float(properties.get("silt", {}).get("mean", 0))
        clay = float(properties.get("clay", {}).get("mean", 0))

        # Normalize percentages
        total = sand + silt + clay
        if total > 0:
            sand = (sand / total) * 100
            silt = (silt / total) * 100
            clay = (clay / total) * 100

        # Determine texture class (simplified)
        if sand >= 70:
            texture_class = "Sandy"
            water_retention = "Low"
            drainage = "High"
            aeration = "High"
            recommendations = ["Add organic matter to improve water retention"]
        elif clay >= 40:
            texture_class = "Clay"
            water_retention = "High"
            drainage = "Low"
            aeration = "Low"
            recommendations = ["Improve drainage and aeration through tillage"]
        else:
            texture_class = "Loam"
            water_retention = "Medium"
            drainage = "Medium"
            aeration = "Medium"
            recommendations = ["Maintain organic matter content"]

        return {
            "class": texture_class,
            "sand": sand,
            "silt": silt,
            "clay": clay,
            "water_retention": water_retention,
            "drainage": drainage,
            "aeration": aeration,
            "recommendations": recommendations
        }
    except Exception:
        return {
            "class": "Unknown",
            "sand": 0,
            "silt": 0,
            "clay": 0,
            "water_retention": "Unknown",
            "drainage": "Unknown",
            "aeration": "Unknown",
            "recommendations": ["Soil texture analysis failed"]
        }