import torch
import yaml
import numpy as np
import os
from PIL import Image
from pix2tex.models import get_model
from pix2tex.utils import parse_args, Munch, seed_everything, post_process
from pix2tex.dataset.transforms import test_transform as get_transform

image_path = "C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\\test_images\\H1.jpeg"  
config_path = "config.yaml"  
checkpoint_path = "mixed_e01_step16298.pth" 


with open(config_path, "r") as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

args = parse_args(Munch(params))
args.wandb = False
args.device = "cuda" if torch.cuda.is_available() else "cpu"
seed_everything(args.seed if "seed" in args else 42)


print("🔹 Loading model...")
model = get_model(args).to(args.device)
model.load_state_dict(torch.load(checkpoint_path, map_location=args.device))
model.eval()
print("✅ Model loaded successfully!")


def predict_single_image(image_path, model, args):
    
    if not os.path.exists(image_path):
        print("❌ Error: Image file not found!")
        return None


    image = Image.open(image_path).convert("RGB")
    transform = get_transform(args)  
    transformed = transform(image=np.array(image))["image"]  
    image_tensor = transform(image=image)["image"].unsqueeze(0)

    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get("temperature", 0.2))


    latex_code = post_process(output_tokens)  

    return latex_code

print("🔹 Predicting LaTeX for image:", image_path)
latex_result = predict_single_image(image_path, model, args)

if latex_result:
    print("\n🎯 Predicted LaTeX Code:\n", latex_result)
else:
    print("❌ Prediction failed.")
