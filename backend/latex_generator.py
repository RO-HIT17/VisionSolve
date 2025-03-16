from PIL import Image
from pix2tex.cli import LatexOCR
import os
import shutil


def genrate_latex_from_image(image_path):
    try:
        cache_dir = "/root/.cache/uv/archive-v0/RKZKlqiMrM89Kt-w7BgsI"
        os.makedirs(cache_dir, exist_ok=True)

        src_model_path = "/model/mixed_e03_step16298.pth"
        dst_model_path = os.path.join(cache_dir, "weights.pth")

        if not os.path.exists(dst_model_path):  
            if os.path.exists(src_model_path):
                shutil.copy(src_model_path, dst_model_path)
                print(f"Model weights copied to: {dst_model_path}")
            else:
                print("Source model weights file not found!")
                
        img = Image.open(image_path)  

        model = LatexOCR()
        cleaned_latex = model(img)
        
        return cleaned_latex

    except Exception as e:
        print(f"Error processing image: {e}")
        return f"Error: {str(e)}"
