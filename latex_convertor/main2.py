from PIL import Image
from pix2tex.cli import LatexOCR
import os
import shutil

# Ensure the cache directory exists
cache_dir = "/root/.cache/uv/archive-v0/RKZKlqiMrM89Kt-w7BgsI"
os.makedirs(cache_dir, exist_ok=True)

# Copy model weights to correct location
src_model_path = "/model/mixed_e02_step16298.pth"
dst_model_path = os.path.join(cache_dir, "weights.pth")

if os.path.exists(src_model_path):
    shutil.copy(src_model_path, dst_model_path)
    print(f"Model weights copied to: {dst_model_path}")
else:
    print("Source model weights file not found!")

# Load image
image_path = r"C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\\test_images\\2.png"
img = Image.open(image_path)

# Load model and perform OCR
model = LatexOCR()
cleaned_latex = model(img)

# Print the extracted LaTeX expression
print(cleaned_latex)
