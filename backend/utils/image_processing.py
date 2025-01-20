from PIL import Image
import numpy as np
# from fastapi.responses import FileResponse
from typing import Callable
from fastapi import UploadFile, HTTPException
import io


def calculate_ndvi(image: Image.Image, nir_channel=3, red_channel=0) -> Image.Image:
    img_array = np.array(image)
    nir = img_array[:, :, nir_channel].astype(float)
    red = img_array[:, :, red_channel].astype(float)
    denominator = nir + red
    denominator[denominator == 0] = 1e-5
    ndvi = (nir - red) / denominator

    # Save the NDVI array for later use
    np.save("output/ndvi_array.npy", ndvi)

    ndvi_normalized = ((ndvi + 1) / 2 * 255).astype(np.uint8)
    return apply_colormap(ndvi_normalized)

def calculate_evi(image: Image.Image, G: float = 2.5, C1: float = 6, C2: float = 7.5, L: float = 1) -> Image.Image:
    image_array = np.array(image)

    # Validate image dimensions
    if image_array.ndim < 3 or image_array.shape[2] < 3:
        raise ValueError("Input image must have at least three channels for EVI calculation.")

    nir = image_array[:, :, 0].astype(float)  #  NIR is the first channel
    red = image_array[:, :, 1].astype(float)  #  Red is the second channel
    blue = image_array[:, :, 2].astype(float)  #  Blue is the third channel

    denominator = nir + C1 * red - C2 * blue + L
    denominator[denominator == 0] = 1e-5

    evi = G * (nir - red) / denominator
    np.save("output/evi_array.npy", evi)

    evi_normalized = ((evi + 1) / 2 * 255).clip(0, 255).astype(np.uint8)

    evi_colorized = apply_colormap(evi_normalized)

    return evi_colorized

def calculate_savi(image: Image.Image, nir_channel=3, red_channel=0, L: float = 0.5) -> Image.Image:
    img_array = np.array(image)

    # Validate image has enough channels
    if img_array.ndim < 3 or img_array.shape[2] <= max(nir_channel, red_channel):
        raise ValueError("Input image does not have sufficient channels for SAVI calculation.")

    nir = img_array[:, :, nir_channel].astype(float)
    red = img_array[:, :, red_channel].astype(float)

    # Avoid division by zero
    denominator = nir + red + L
    denominator[denominator == 0] = 1e-5

    # Calculate SAVI
    savi = ((nir - red) / denominator) * (1 + L)
    np.save("output/savi_array.npy", savi)

    savi_normalized = ((savi + 1) / 2 * 255).clip(0, 255).astype(np.uint8)

    savi_colorized = apply_colormap(savi_normalized)

    return savi_colorized

def calculate_arvi(image: Image.Image, red_channel=0, blue_channel=2, green_channel=1) -> Image.Image:
    img_array = np.array(image)
    red = img_array[:, :, red_channel].astype(float)
    blue = img_array[:, :, blue_channel].astype(float)
    green = img_array[:, :, green_channel].astype(float)

    denominator = red + (2 * blue) - green
    denominator[denominator == 0] = 1e-5
    arvi = (red - (2 * blue) + green) / denominator

    # Save the ARVI array for later use
    np.save("output/arvi_array.npy", arvi)

    arvi_normalized = ((arvi + 1) / 2 * 255).astype(np.uint8)
    return apply_colormap(arvi_normalized)

def calculate_gndvi(image: Image.Image, nir_channel=3, green_channel=1) -> Image.Image:
    img_array = np.array(image)
    nir = img_array[:, :, nir_channel].astype(float)
    green = img_array[:, :, green_channel].astype(float)

    denominator = nir + green
    denominator[denominator == 0] = 1e-5
    gndvi = (nir - green) / denominator

    # Save the GNDVI array for later use
    np.save("output/gndvi_array.npy", gndvi)

    gndvi_normalized = ((gndvi + 1) / 2 * 255).astype(np.uint8)
    return apply_colormap(gndvi_normalized)

def calculate_msavi(image: Image.Image, nir_channel=3, red_channel=0) -> Image.Image:
    img_array = np.array(image)
    nir = img_array[:, :, nir_channel].astype(float)
    red = img_array[:, :, red_channel].astype(float)

    msavi = (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red))) / 2

    # Save the MSAVI array for later use
    np.save("output/msavi_array.npy", msavi)

    msavi_normalized = ((msavi + 1) / 2 * 255).astype(np.uint8)
    return apply_colormap(msavi_normalized)

def analyze_index(index_array: np.ndarray, index_type: str):
    index_type = index_type.lower()
    if index_type in ["ndvi", "evi", "savi", "arvi", "gndvi", "msavi"]:
        stats = {
            "Mean": float(np.mean(index_array)),
            "StandardDeviation": float(np.std(index_array)),
            "Minimum": float(np.min(index_array)),
            "Maximum": float(np.max(index_array)),
            "HighVegetationPercentage": float((index_array > 0.6).sum()) / index_array.size * 100,
            "ModerateVegetationPercentage": float(((index_array > 0.2) & (index_array <= 0.6)).sum()) / index_array.size * 100,
            "LowVegetationPercentage": float((index_array <= 0.2).sum()) / index_array.size * 100,
        }
        return stats
    else:
        raise ValueError(f"Invalid index type: {index_type}.")

async def perform_analysis(
    file: UploadFile,
    index_name: str,
    calculation_function: Callable[[Image.Image], Image.Image]
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image")

    try:
        image = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not process the image file")

    # Perform the calculation
    result_image = calculation_function(image)
    array_path = f"output/{index_name}_array.npy"
    result_array = np.load(array_path)  # Load the array saved by the calculation function
    insights = analyze_index(result_array, index_name)

    # Save the resulting image
    file_path = f"output/{index_name}_result.png"
    result_image.save(file_path)

    # Return a standardized response
    return {
        "message": f"{index_name.upper()} analysis complete",
        "file_path": file_path,
        "insights": insights
    }

def apply_colormap(ndvi_array: np.ndarray) -> Image.Image:
    colormap = np.zeros((256, 3), dtype=np.uint8)
    for i in range(256):
        if i < 128:  # Low NDVI values (e.g., non-vegetation areas)
            colormap[i] = [255, int(i * 2), 0]  # Gradient from red to yellow
        else:  # High NDVI values (e.g., vegetation areas)
            colormap[i] = [int((255 - i) * 2), 255, int((i - 128) * 2)]  # Gradient from yellow to green

    # Map NDVI values to the colormap
    colorized = colormap[ndvi_array]

    # Return as a PIL Image
    return Image.fromarray(colorized, mode="RGB")