from typing import List, Optional
from pydantic import BaseModel, Field
from models.response.soil import SoilResponse

class PredResponse(BaseModel):
    condition: str
    confidence: float
    recommendation: str
    soil_data: SoilResponse
    llm_insights: str
