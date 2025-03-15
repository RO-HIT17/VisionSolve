from PIL import Image
from pix2tex.cli import LatexOCR
import os
import shutil


def generate_latex_from_image(image_path):
    """
    Given an image path, process it using pix2tex and return the LaTeX string.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        str: Extracted LaTeX expression.
    """

    try:
        # Ensure the cache directory exists
        cache_dir = "/root/.cache/uv/archive-v0/RKZKlqiMrM89Kt-w7BgsI"
        os.makedirs(cache_dir, exist_ok=True)

        # Copy model weights to the correct location if not already copied
        src_model_path = "/model/mixed_e03_step16298.pth"
        dst_model_path = os.path.join(cache_dir, "weights.pth")

        if not os.path.exists(dst_model_path):  # Only copy if it doesn't exist
            if os.path.exists(src_model_path):
                shutil.copy(src_model_path, dst_model_path)
                print(f"Model weights copied to: {dst_model_path}")
            else:
                print("Source model weights file not found!")
                # "Error: Model weights not found."
        
        # Load the image
        img = Image.open(image_path)  # Ensure image is in RGB mode

        # Load model and perform OCR
        model = LatexOCR()
        cleaned_latex = model(img)
        print("Latex:",cleaned_latex)
        return cleaned_latex

    except Exception as e:
        print(f"Error processing image: {e}")
        return f"Error: {str(e)}"
