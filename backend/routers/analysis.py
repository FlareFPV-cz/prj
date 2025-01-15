from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.image_processing import calculate_ndvi, calculate_evi
from PIL import Image
import numpy as np
import io

router = APIRouter()


def analyze_index(index_array: np.ndarray, index_type: str):
    if index_type.lower() == "ndvi":
        stats = {
            "Mean NDVI": float(np.mean(index_array)),
            "Standard Deviation": float(np.std(index_array)),
            "Minimum NDVI": float(np.min(index_array)),
            "Maximum NDVI": float(np.max(index_array)),
            "High Vegetation (%)": float((index_array > 0.6).sum()) / index_array.size * 100,
            "Moderate Vegetation (%)": float(((index_array > 0.2) & (index_array <= 0.6)).sum()) / index_array.size * 100,
            "Low Vegetation (%)": float((index_array <= 0.2).sum()) / index_array.size * 100,
        }
    elif index_type.lower() == "evi":
        stats = {
            "Mean EVI": float(np.mean(index_array)),
            "Standard Deviation": float(np.std(index_array)),
            "Minimum EVI": float(np.min(index_array)),
            "Maximum EVI": float(np.max(index_array)),
            "High Vegetation (%)": float((index_array > 0.4).sum()) / index_array.size * 100,
            "Moderate Vegetation (%)": float(((index_array > 0.1) & (index_array <= 0.4)).sum()) / index_array.size * 100,
            "Low Vegetation (%)": float((index_array <= 0.1).sum()) / index_array.size * 100,
        }
    else:
        raise ValueError("Invalid index type. Please specify 'NDVI' or 'EVI'.")

    return stats



@router.post("/ndvi/")
async def ndvi_analysis(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    try:
        image = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not process the image file")

    ndvi_image = calculate_ndvi(image)
    ndvi_array = np.array(ndvi_image)  # Extract numeric data for analysis
    insights = analyze_index(ndvi_array, "ndvi")
    file_path = "output/ndvi_result.png"
    ndvi_image.save(file_path)
    return {"message": "NDVI analysis complete", "file_path": f"output/ndvi_result.png", "insights": insights}

@router.post("/evi/")
async def evi_analysis(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    try:
        image = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not process the image file")

    evi_image = calculate_evi(image)
    evi_array = np.array(evi_image) 
    insights = analyze_index(evi_array, "evi")
    file_path = "output/evi_result.png"
    evi_image.save(file_path)
    return {"message": "EVI analysis complete", "file_path": f"output/evi_result.png", "insights": insights}
