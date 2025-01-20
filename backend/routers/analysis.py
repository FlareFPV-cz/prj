from fastapi import APIRouter, Path, UploadFile, File, HTTPException
from PIL import Image
from pydantic import BaseModel
import numpy as np
from fastapi.responses import FileResponse
from typing import Callable


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

@router.get("/get-map/")
async def get_map(index_type: str):
    file_path = "output/"+index_type+"_result.png"
    return FileResponse(file_path, media_type="image/png")
