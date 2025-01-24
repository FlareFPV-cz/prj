from typing import List, Optional
from pydantic import BaseModel, Field

class DepthRange(BaseModel):
    top_depth: int
    bottom_depth: int
    unit_depth: str

class DepthValues(BaseModel):
    Q0_05: Optional[float] = Field(None, alias="Q0.05")
    Q0_5: Optional[float] = Field(None, alias="Q0.5")
    Q0_95: Optional[float] = Field(None, alias="Q0.95")
    mean: Optional[float] = None
    uncertainty: Optional[float] = None

class Depth(BaseModel):
    range: DepthRange
    label: str
    values: DepthValues

class UnitMeasure(BaseModel):
    d_factor: Optional[float] = None
    mapped_units: Optional[str] = None
    target_units: Optional[str] = None
    uncertainty_unit: Optional[str] = None

class Layer(BaseModel):
    name: str
    unit_measure: UnitMeasure
    depths: List[Depth]

class Properties(BaseModel):
    layers: List[Layer]

class Geometry(BaseModel):
    type: str
    coordinates: List[float]

class SoilData(BaseModel):
    type: str
    geometry: Geometry
    properties: Properties
    
class SoilResponse(BaseModel):
    message: str
    data: SoilData
