import numpy as np
from PIL import Image
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi import APIRouter, Path, UploadFile, File, HTTPException, Depends, Query
import httpx
from httpx import Timeout

from models.user import User
from utils.auth import get_current_active_user
from models.response.soil import SoilResponse
from models.request.index import IndexRequest
from models.response.analyze import AnalysisResponse, IndexValueResponse
from utils.image_processing import (
    calculate_ndvi, 
    calculate_evi, 
    calculate_savi,
    calculate_arvi,
    calculate_gndvi,
    calculate_msavi,
    perform_analysis
)

router = APIRouter()

INDEX_CALCULATIONS = {
    "ndvi": calculate_ndvi,
    "evi": calculate_evi,
    "savi": calculate_savi,
    "arvi": calculate_arvi,
    "gndvi": calculate_gndvi,
    "msavi": calculate_msavi,
}

INDEX_ARRAY_PATHS = {
    "ndvi": "output/ndvi_array.npy",
    "evi": "output/evi_array.npy",
    "savi": "output/savi_array.npy",
    "arvi": "output/arvi_array.npy",
    "gndvi": "output/gndvi_array.npy",
    "msavi": "output/msavi_array.npy",
}

DEFAULT_PROPERTIES = [
    "bdod", "cec", "cfvo", "clay", "nitrogen", "ocd", "ocs",
    "phh2o", "sand", "silt", "soc", "wv0010", "wv0033", "wv1500"
]
DEFAULT_DEPTHS = [
    "0-5cm", "0-30cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"
]
DEFAULT_VALUES = ["Q0.5", "Q0.05", "Q0.95", "mean", "uncertainty"]

SOILGRIDS_API_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

@router.post("/analyze/{index_name}/", response_model=AnalysisResponse, summary="Analyze an image to extract vegetation indices", description="Uploads an image and calculates a vegetation index such as NDVI, EVI, or SAVI.")
async def dynamic_analysis(
    file: UploadFile = File(..., description="Image file for analysis"), 
    index_name: str = Path(..., description="Vegetation index to calculate (e.g., ndvi, evi, savi)"),
    current_user: User = Depends(get_current_active_user)
):
    """Performs vegetation index analysis on the uploaded image."""
    if index_name not in INDEX_CALCULATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid index name '{index_name}'. Supported indices: {', '.join(INDEX_CALCULATIONS.keys())}"
        )

    calculation_function = INDEX_CALCULATIONS[index_name]
    return await perform_analysis(file, index_name, calculation_function)

@router.post("/get-index-value/", response_model=IndexValueResponse, summary="Retrieve an index value from a precomputed array", description="Fetches the value of a specified vegetation index at given x, y coordinates.")
async def get_index_value(
    request: IndexRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Gets the index value from the precomputed vegetation index arrays."""
    x, y, index_type = request.x, request.y, request.index_type.lower()

    if index_type not in INDEX_ARRAY_PATHS:
        raise HTTPException(status_code=400, detail=f"Invalid index type '{index_type}'. Supported indices: {', '.join(INDEX_ARRAY_PATHS.keys())}")

    try:
        index_array = np.load(INDEX_ARRAY_PATHS[index_type])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"The array file for '{index_type}' does not exist.")

    if x < 0 or y < 0 or x >= index_array.shape[1] or y >= index_array.shape[0]:
        raise HTTPException(status_code=400, detail="Coordinates out of bounds.")

    return {"x": x, "y": y, "index_type": index_type.upper(), "index_value": float(index_array[y, x])}

@router.get("/soil-data/", response_model=SoilResponse, summary="Fetch soil properties from SoilGrids API", description="Retrieves soil data based on geographic coordinates, properties, depths, and values.")
async def get_soil_data(
    lon: float = Query(..., description="Longitude of the location"),
    lat: float = Query(..., description="Latitude of the location"),
    properties: list[str] = Query(DEFAULT_PROPERTIES, description="List of soil properties to fetch"),
    depths: list[str] = Query(DEFAULT_DEPTHS, description="Soil depths for data retrieval"),
    values: list[str] = Query(DEFAULT_VALUES, description="Statistical values to retrieve"),
    current_user: User = Depends(get_current_active_user)
):
    """Fetches soil data from SoilGrids API based on provided location and parameters."""
    params = [("lon", lon), ("lat", lat)] + [("property", prop) for prop in properties] + [("depth", depth) for depth in depths] + [("value", val) for val in values]
    try:
        async with httpx.AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.get(SOILGRIDS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching soil data: {str(e)}")
    return {"message": "Soil data fetched successfully", "data": data}

@router.get("/get-map/", summary="Retrieve a generated vegetation index map", description="Returns a PNG image file for a specified vegetation index.")
async def get_map(
    index_type: str = Query(..., description="Type of vegetation index to retrieve"),
    current_user: User = Depends(get_current_active_user)
):
    """Fetches the vegetation index map image file."""
    return FileResponse(f"output/{index_type}_result.png", media_type="image/png")

@router.get("/protected-data", summary="Protected route", description="Returns a message if the user is authenticated.", tags=["Test"])
def get_protected_data(current_user: User = Depends(get_current_active_user)):
    """Endpoint that requires authentication to access."""
    return {"message": f"Hello {current_user.username}, this is protected data."}
