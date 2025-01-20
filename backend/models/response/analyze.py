from pydantic import BaseModel

class AnalyzeIndexResponse(BaseModel):
    Mean: float
    StandardDeviation: float
    Minimum: float
    Maximum: float
    HighVegetationPercentage: float
    ModerateVegetationPercentage: float
    LowVegetationPercentage: float

class AnalysisResponse(BaseModel):
    message: str
    file_path: str
    insights: AnalyzeIndexResponse

class IndexValueResponse(BaseModel):
    x: int
    y: int
    index_type: str
    index_value: float