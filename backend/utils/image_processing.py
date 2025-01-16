from PIL import Image, ImageEnhance
import numpy as np

# def calculate_ndvi(image: Image.Image, nir_channel=3, red_channel=0) -> Image.Image:
#     img_array = np.array(image)

#     # Validate image has enough channels
#     if img_array.ndim < 3 or img_array.shape[2] <= max(nir_channel, red_channel):
#         raise ValueError("Input image does not have sufficient channels for NDVI calculation.")

#     nir = img_array[:, :, nir_channel].astype(float)
#     red = img_array[:, :, red_channel].astype(float)

#     # Avoid division by zero
#     denominator = nir + red
#     denominator[denominator == 0] = 1e-5

#     # Calculate NDVI
#     ndvi = (nir - red) / denominator

#     # Normalize NDVI to range [0, 255] for visualization
#     ndvi_normalized = ((ndvi + 1) / 2 * 255).astype(np.uint8)

#     # Apply a color map for better visualization
#     ndvi_colorized = apply_colormap(ndvi_normalized)

#     return ndvi_colorized

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

    nir = image_array[:, :, 0].astype(float)  # Assuming NIR is the first channel
    red = image_array[:, :, 1].astype(float)  # Assuming Red is the second channel
    blue = image_array[:, :, 2].astype(float)  # Assuming Blue is the third channel

    denominator = nir + C1 * red - C2 * blue + L
    denominator[denominator == 0] = 1e-5

    evi = G * (nir - red) / denominator
    np.save("output/evi_array.npy", evi)

    # Normalize EVI to range [0, 255] for visualization
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

    # Normalize SAVI to range [0, 255] for visualization
    savi_normalized = ((savi + 1) / 2 * 255).clip(0, 255).astype(np.uint8)

    # Apply a color map for better visualization
    savi_colorized = apply_colormap(savi_normalized)

    return savi_colorized


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