from pix2tex.models import get_model
from pix2tex.utils import *
from pix2tex.dataset.transforms import test_transform as get_transform
from PIL import Image
import yaml
import torch
import numpy as np
import os

image_path = "C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\test_images\\H2.png" 

config_path = "config.yaml"  
checkpoint_path = "mixed_e01_step16298.pth" 

with open(config_path, "r") as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

args = parse_args(Munch(params))
args.device = "cuda" if torch.cuda.is_available() else "cpu"
seed_everything(args.seed if "seed" in args else 42)


model = get_model(args).to(args.device)
model.load_state_dict(torch.load(checkpoint_path, map_location=args.device))
model.eval()

def predict_single_image(image_path, model, args):
    image = Image.open(image_path).convert("RGB")
    transform = get_transform(args)  

    transformed = transform(image=np.array(image))["image"]  
    image_tensor = torch.tensor(transformed).unsqueeze(0).to(args.device)  


    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get("temperature", 0.2))

    return output_tokens  

if os.path.exists(image_path):
    result = predict_single_image(image_path, model, args)
    print(f"Predicted LaTeX:\n{result}")
else:
    print("Error: Image file not found!")
