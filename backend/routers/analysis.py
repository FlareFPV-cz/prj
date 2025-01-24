import numpy as np
from PIL import Image
# from typing import Callable
from pydantic import BaseModel
from fastapi.responses import FileResponse
from dependencies.auth import get_current_active_user
from fastapi import APIRouter, Path, UploadFile, File, HTTPException, Depends, Query
import httpx
from httpx import Timeout



from models.response.soil import SoilResponse
from models.request.index import IndexRequest
from models.response.analyze import (
    AnalysisResponse,
    IndexValueResponse,
)

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


@router.post("/analyze/{index_name}/", response_model=AnalysisResponse)
async def dynamic_analysis(file: UploadFile = File(...), index_name: str = Path(...)):
    if index_name not in INDEX_CALCULATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid index name '{index_name}'. Supported indices: {', '.join(INDEX_CALCULATIONS.keys())}"
        )

    calculation_function = INDEX_CALCULATIONS[index_name]

    return await perform_analysis(file, index_name, calculation_function)

@router.post("/get-index-value/", response_model=IndexValueResponse)
async def get_index_value(request: IndexRequest):
    x = request.x
    y = request.y
    index_type = request.index_type.lower()

    # Validate index_type
    if index_type not in INDEX_ARRAY_PATHS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid index type '{index_type}'. Supported indices: {', '.join(INDEX_ARRAY_PATHS.keys())}"
        )

    # Load the appropriate index array
    try:
        index_array = np.load(INDEX_ARRAY_PATHS[index_type])
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"The array file for '{index_type}' does not exist. Please ensure the analysis has been performed."
        )

    # Validate coordinates
    if x < 0 or y < 0 or x >= index_array.shape[1] or y >= index_array.shape[0]:
        raise HTTPException(
            status_code=400,
            detail="Coordinates out of bounds. Please provide valid (x, y) coordinates."
        )

    # Retrieve index value at the given coordinates
    index_value = float(index_array[y, x])  # (y, x) for row-column indexing

    return {
        "x": x,
        "y": y,
        "index_type": index_type.upper(),
        "index_value": index_value
    }

@router.get("/soil-data/", response_model=SoilResponse)
async def get_soil_data(
    lon: float,
    lat: float,
    properties: list[str] = Query(DEFAULT_PROPERTIES),
    depths: list[str] = Query(DEFAULT_DEPTHS),
    values: list[str] = Query(DEFAULT_VALUES)
):
    """
    SoilGrids API
    """
    params = [
        ("lon", lon),
        ("lat", lat),
    ]

    params += [("property", prop) for prop in properties]
    params += [("depth", depth) for depth in depths]
    params += [("value", val) for val in values]

    try:
        timeout = Timeout(30.0)  # Increase timeout to 30 seconds
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(SOILGRIDS_API_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error fetching soil data: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}"
        )

    try:
        data = response.json()
    except Exception:
        raise HTTPException(
            status_code=500, detail="Failed to parse JSON response from SoilGrids API"
        )

    return {"message": "Soil data fetched successfully", "data": data}

@router.get("/get-map/")
async def get_map(index_type: str):
    file_path = "output/"+index_type+"_result.png"
    return FileResponse(file_path, media_type="image/png")

@router.get("/protected-data")
def get_protected_data(current_user=Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}, this is protected data."}
