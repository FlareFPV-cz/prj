from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class HealthMetrics(BaseModel):
    """Model representing detailed health metrics of a crop.
    
    Attributes:
        leaf_color_score (float): Score indicating the health of leaf color (0-255)
        texture_uniformity (float): Measure of texture consistency across the plant
        growth_pattern (str): Description of the plant's growth pattern
        stress_indicators (List[str]): List of detected stress indicators
    """
    leaf_color_score: float
    texture_uniformity: float
    growth_pattern: str
    stress_indicators: List[str]

class DetailedAssessment(BaseModel):
    """Comprehensive crop health assessment response model.
    
    Attributes:
        timestamp (str): ISO format timestamp of the assessment
        metrics (HealthMetrics): Detailed health metrics
        disease_probability (float): Probability of disease presence (0-1)
        health_status (str): Overall health status assessment
        severity_level (str): Severity level of any detected issues
        affected_areas (List[str]): Areas of the plant showing symptoms
        environmental_factors (Dict[str, float]): Environmental measurements
        recommendations (List[str]): Suggested actions based on assessment
        confidence_score (float): Confidence level of the assessment (0-1)
        follow_up_actions (List[str]): Recommended follow-up steps
    """
    timestamp: str
    metrics: HealthMetrics
    disease_probability: float
    health_status: str
    severity_level: str
    affected_areas: List[str]
    environmental_factors: Dict[str, float]
    recommendations: List[str]
    confidence_score: float
    follow_up_actions: List[str]