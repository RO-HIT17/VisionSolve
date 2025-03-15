import torch
import yaml
import numpy as np
import os
from PIL import Image
from pix2tex.models import get_model
from pix2tex.utils import parse_args, Munch, seed_everything, post_process
from pix2tex.dataset.transforms import test_transform as get_transform

# ✅ Set your paths here
image_path = "C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\\test_images\\H1.jpeg"  # 🔹 Change to your test image
config_path = "config.yaml"  # 🔹 Change to your model config file
checkpoint_path = "mixed_e01_step16298.pth"  # 🔹 Change to your trained model checkpoint

# ✅ Load configuration
with open(config_path, "r") as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

args = parse_args(Munch(params))
args.wandb = False
args.device = "cuda" if torch.cuda.is_available() else "cpu"
seed_everything(args.seed if "seed" in args else 42)

# ✅ Load trained model
print("🔹 Loading model...")
model = get_model(args).to(args.device)
model.load_state_dict(torch.load(checkpoint_path, map_location=args.device))
model.eval()
print("✅ Model loaded successfully!")

# ✅ Function to predict LaTeX from an image
def predict_single_image(image_path, model, args):
    """
    Predicts LaTeX code from an image using the trained `pix2tex` model.
    
    Args:
        image_path (str): Path to the image file.
        model (Model): Trained `pix2tex` model.
        args: Configuration arguments.

    Returns:
        str: Predicted LaTeX string.
    """
    # Check if image exists
    if not os.path.exists(image_path):
        print("❌ Error: Image file not found!")
        return None

    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")
    transform = get_transform(args)  # Get transformation function
    transformed = transform(image=np.array(image))["image"]  # Apply transformation correctly
    image_tensor = transform(image=image)["image"].unsqueeze(0).to(device)

    #image_tensor = torch.tensor(transformed).unsqueeze(0).to(args.device)  # Convert to tensor

    # Predict LaTeX tokens
    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get("temperature", 0.2))

    # Convert tokens to LaTeX string (if needed)
    latex_code = post_process(output_tokens)  # 🔹 Apply post-processing

    return latex_code

# ✅ Run the prediction
print("🔹 Predicting LaTeX for image:", image_path)
latex_result = predict_single_image(image_path, model, args)

# ✅ Display the result
if latex_result:
    print("\n🎯 Predicted LaTeX Code:\n", latex_result)
else:
    print("❌ Prediction failed.")
