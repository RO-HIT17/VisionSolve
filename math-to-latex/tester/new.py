from pix2tex.models import get_model
from pix2tex.utils import *
from pix2tex.dataset.transforms import test_transform as get_transform
from PIL import Image
import yaml
import torch
import numpy as np
import os

# ✅ Set your input image file here
image_path = "C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\test_images\\H2.png"  # Change this to your image file path

# ✅ Load configuration
config_path = "config.yaml"  # Change if needed
checkpoint_path = "mixed_e01_step16298.pth"  # Change if needed

with open(config_path, "r") as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

args = parse_args(Munch(params))
args.device = "cuda" if torch.cuda.is_available() else "cpu"
seed_everything(args.seed if "seed" in args else 42)

# ✅ Load model
model = get_model(args).to(args.device)
model.load_state_dict(torch.load(checkpoint_path, map_location=args.device))
model.eval()

# ✅ Function to process and predict
def predict_single_image(image_path, model, args):
    """
    Predict LaTeX for a single image using the trained pix2tex model.

    Args:
        image_path (str): Path to the image file.
        model (Model): Loaded pix2tex model.
        args: Configuration arguments (device, etc.).

    Returns:
        str: Predicted LaTeX string.
    """
    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")
    transform = get_transform(args)  # Get transformation function

    # Apply transformation correctly
    transformed = transform(image=np.array(image))["image"]  # Ensure correct input format
    image_tensor = torch.tensor(transformed).unsqueeze(0).to(args.device)  # Convert to tensor and add batch dimension

    # Generate output
    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get("temperature", 0.2))

    return output_tokens  # Returning raw tokens instead of converting to string

# ✅ Run prediction
if os.path.exists(image_path):
    result = predict_single_image(image_path, model, args)
    print(f"Predicted LaTeX:\n{result}")
else:
    print("Error: Image file not found!")
