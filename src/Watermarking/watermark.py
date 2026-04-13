"""
Watermarking Module
====================
Implements various watermarking techniques for images.
"""
import logging
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


# ============================================================================
#                    TEXT-BASED WATERMARK (VISIBLE)
# ============================================================================

def apply_text_watermark(image, watermark_text, font_size=30, position="bottom-right", 
                         text_color=(255, 255, 255), opacity=128):
    """
    Apply a visible text watermark to an image.
    
    This function overlays text onto an image at a specified position.
    The watermark is clearly visible to anyone viewing the image.
    Properly handles images with transparent backgrounds (PNG with alpha).
    
    Algorithm:
    1. Store original image mode to preserve transparency
    2. Create a transparent overlay layer
    3. Draw the watermark text on the overlay
    4. Composite the overlay onto the original image
    5. Return the watermarked image (preserving original format)
    
    Args:
        image (PIL.Image): The input image to watermark
        watermark_text (str): The text to display as watermark
        font_size (int): Size of the watermark text (default: 30)
        position (str): Position of watermark in 3x3 grid:
            - "top-left", "top-center", "top-right"
            - "middle-left", "center", "middle-right"
            - "bottom-left", "bottom-center", "bottom-right"
            (default: "bottom-right")
        text_color (tuple): RGB color of the text (default: white)
        opacity (int): Transparency level 0-255 (default: 128 = semi-transparent)
    
    Returns:
        PIL.Image: Image with the text watermark applied (preserves transparency if original had it)
    
    Example:
        >>> from PIL import Image
        >>> img = Image.open("photo.png")
        >>> watermarked = apply_text_watermark(img, "© My Company", font_size=40, position="center")
        >>> watermarked.save("watermarked_photo.png")
    """
    # Store original mode to preserve transparency if needed
    original_mode = image.mode
    
    # Convert to RGBA for watermark compositing
    # This is needed because we use alpha compositing to blend the watermark
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Get image dimensions
    img_width, img_height = image.size
    
    # Create a transparent overlay for the watermark
    # This allows us to control opacity without modifying original pixels directly
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Try to load a TrueType font, fall back to default if not available
    # Default font is always available but may look basic
    try:
        # Try common system fonts
        font = ImageFont.truetype("arial.ttf", font_size)
    except (IOError, OSError):
        try:
            # Try another common font
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            # Fall back to default PIL font (basic but always works)
            font = ImageFont.load_default()
            # Note: Default font ignores font_size parameter
    
    # Calculate text bounding box to determine its size
    # This is needed to position the text correctly
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position based on user selection
    # Padding adds some space from the edges
    padding = 10
    
    # Support 9-position grid: top, middle, bottom (vertical) × left, center, right (horizontal)
    if position == "top-left":
        x = padding
        y = padding
    elif position == "top-center":
        x = (img_width - text_width) // 2
        y = padding
    elif position == "top-right":
        x = img_width - text_width - padding
        y = padding
    elif position == "middle-left":
        x = padding
        y = (img_height - text_height) // 2
    elif position == "center":
        x = (img_width - text_width) // 2
        y = (img_height - text_height) // 2
    elif position == "middle-right":
        x = img_width - text_width - padding
        y = (img_height - text_height) // 2
    elif position == "bottom-left":
        x = padding
        y = img_height - text_height - padding
    elif position == "bottom-center":
        x = (img_width - text_width) // 2
        y = img_height - text_height - padding
    elif position == "bottom-right":
        x = img_width - text_width - padding
        y = img_height - text_height - padding
    else:
        # Default to bottom-right if invalid position given
        x = img_width - text_width - padding
        y = img_height - text_height - padding
    
    # Create the text color with opacity (RGBA format)
    fill_color = (*text_color, opacity)
    
    # Draw the watermark text onto the overlay
    draw.text((x, y), watermark_text, font=font, fill=fill_color)
    
    # Composite the overlay onto the original image
    # Alpha composite blends the two images based on transparency
    watermarked_image = Image.alpha_composite(image, overlay)
    
    # FIXED: Only convert to RGB if the original image was RGB (no transparency)
    # This preserves transparency for PNG images with alpha channel
    if original_mode == 'RGB':
        # Original had no transparency, safe to convert to RGB
        watermarked_image = watermarked_image.convert('RGB')
    elif original_mode == 'L':
        # Original was grayscale, convert back
        watermarked_image = watermarked_image.convert('L')
    # If original was RGBA or P with transparency, keep as RGBA to preserve transparency
    
    return watermarked_image


# ============================================================================
#                    LSB WATERMARK (INVISIBLE)
# ============================================================================

def apply_lsb_watermark(image, watermark_data):
    """
    Apply an invisible LSB-based watermark to an image.
    
    TODO: Implement this function
    
    The LSB watermark embeds data in the least significant bits of pixel values.
    This makes the watermark completely invisible to the human eye.
    
    Planned Algorithm:
    1. Convert watermark data to binary
    2. Modify LSB of selected pixels
    3. Embed a pattern or signature that can be detected later
    4. Return the watermarked image
    
    Args:
        image (PIL.Image): The input image to watermark
        watermark_data (str): Data to embed as invisible watermark
    
    Returns:
        PIL.Image: Image with invisible LSB watermark
    
    Raises:
        NotImplementedError: This function is not yet implemented
    """
    # TODO: Implement LSB-based invisible watermarking
    # Steps to implement:
    # 1. Convert watermark_data to binary string
    # 2. Create a unique pattern/signature for detection
    # 3. Embed bits in LSB of pixel values
    # 4. Add error checking/recovery mechanism
    
    raise NotImplementedError(
        "LSB-based invisible watermarking is planned for future implementation. "
        "This will allow embedding invisible watermarks that can be detected "
        "programmatically but are invisible to humans."
    )


# ============================================================================
#                    ALPHA BLENDING WATERMARK (SEMI-VISIBLE)
# ============================================================================

def apply_alpha_blending_watermark(image, watermark_image, alpha=0.3, position="center"):
    """
    Apply a semi-visible watermark using alpha blending.
    
    TODO: Implement this function
    
    Alpha blending overlays a watermark image (like a logo) with transparency.
    The result is a subtle, semi-visible watermark.
    
    Planned Algorithm:
    1. Resize watermark image to appropriate size
    2. Position the watermark on the main image
    3. Blend using alpha compositing formula: result = (1-alpha)*base + alpha*watermark
    4. Return the blended image
    
    Args:
        image (PIL.Image): The base image
        watermark_image (PIL.Image): The watermark/logo image to overlay
        alpha (float): Transparency level 0.0-1.0 (default: 0.3 = 30% visible)
        position (str): Position of watermark - "center", "tile", etc.
    
    Returns:
        PIL.Image: Image with alpha-blended watermark
    
    Raises:
        NotImplementedError: This function is not yet implemented
    """
    # TODO: Implement alpha blending watermark
    # Steps to implement:
    # 1. Load and resize watermark image
    # 2. Convert both images to same mode (RGBA)
    # 3. Calculate blend: output = (1-alpha)*original + alpha*watermark
    # 4. Handle positioning (center, corners, tiled)
    # 5. Return final composited image
    
    raise NotImplementedError(
        "Alpha blending watermark is planned for future enhancement. "
        "This will allow overlaying logo images with adjustable transparency."
    )


# ============================================================================
#                    UTILITY FUNCTIONS
# ============================================================================

def get_available_positions():
    """
    Get list of available watermark positions.
    
    Returns:
        list: Available position options (3x3 grid)
    """
    return [
        "top-left", "top-center", "top-right",
        "middle-left", "center", "middle-right",
        "bottom-left", "bottom-center", "bottom-right"
    ]


def validate_watermark_text(text):
    """
    Validate watermark text input.
    
    Args:
        text (str): The watermark text to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or text.strip() == "":
        return False, "Watermark text cannot be empty"
    
    if len(text) > 200:
        return False, "Watermark text is too long (max 200 characters)"
    
    return True, ""