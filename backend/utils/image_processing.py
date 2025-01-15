from PIL import Image, ImageEnhance
import numpy as np

def calculate_ndvi(image: Image.Image, nir_channel=3, red_channel=0) -> Image.Image:
    img_array = np.array(image)

    # Validate image has enough channels
    if img_array.ndim < 3 or img_array.shape[2] <= max(nir_channel, red_channel):
        raise ValueError("Input image does not have sufficient channels for NDVI calculation.")

    nir = img_array[:, :, nir_channel].astype(float)
    red = img_array[:, :, red_channel].astype(float)

    # Avoid division by zero
    denominator = nir + red
    denominator[denominator == 0] = 1e-5

    # Calculate NDVI
    ndvi = (nir - red) / denominator

    # Normalize NDVI to range [0, 255] for visualization
    ndvi_normalized = ((ndvi + 1) / 2 * 255).astype(np.uint8)

    # Apply a color map for better visualization
    ndvi_colorized = apply_colormap(ndvi_normalized)

    return ndvi_colorized


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
