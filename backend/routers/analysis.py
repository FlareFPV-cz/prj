from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.image_processing import calculate_ndvi
from PIL import Image
import io

router = APIRouter()


@router.post("/ndvi/")
async def ndvi_analysis(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")
    
    try:
        image = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not process the image file")
    
    ndvi_image = calculate_ndvi(image)
    ndvi_image.save("output/ndvi_result.png")
    return {"message": "NDVI analysis complete", "file_path": "output/ndvi_result.png"}

