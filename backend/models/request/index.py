from pydantic import BaseModel

class IndexRequest(BaseModel):
    x: int
    y: int
    index_type: str = "ndvi"