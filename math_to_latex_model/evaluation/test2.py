from pix2tex.models import get_model
from pix2tex.utils import *
from pix2tex.dataset.transforms import test_transform
from PIL import Image
import argparse
import logging
import yaml
import torch
import os
import numpy as np
from munch import Munch  

import albumentations as A

class Transforms:
    def __init__(self, transforms: A.Compose):
        self.transforms = transforms

    def __call__(self, img):
        img = np.array(img) 
        return self.transforms(image=img)['image']

def predict_single_image(image_path, model, args):
    
    device = args.device
    model.eval()

    try:
        image = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return ""

    transform = Transforms(test_transform(args))  
    image_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get('temperature', .2))

    latex_code = post_process(output_tokens[0])

    return latex_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test model')
    parser.add_argument('--image', required=True, help='Path to the input image', type=str)
    parser.add_argument('--config', default=None, help='Path to yaml config file', type=str)
    parser.add_argument('-c', '--checkpoint', default=None, type=str, help='Path to model checkpoint')
    parser.add_argument('--no-cuda', action='store_true', help='Use CPU')
    parser.add_argument('-t', '--temperature', type=float, default=.333, help='Sampling temperature')
    parsed_args = parser.parse_args()

    image_path = parsed_args.image  

    if parsed_args.config is None:
        with in_model_path():
            parsed_args.config = os.path.realpath('C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\\tester\\config.yaml')
    with open(parsed_args.config, 'r') as f:
        params = yaml.load(f, Loader=yaml.FullLoader)

    args = parse_args(Munch(params))
    args.wandb = False  
    args.temperature = parsed_args.temperature
    args.device = 'cuda' if torch.cuda.is_available() and not parsed_args.no_cuda else 'cpu'

    logging.getLogger().setLevel(logging.WARNING)

    model = get_model(args).to(args.device)
    
    if parsed_args.checkpoint is None:
        with in_model_path():
            parsed_args.checkpoint = os.path.realpath('C:\\Rohit\\Projects\\Itrix 25\\math-to-latex\\tester\\mixed_e01_step16298.pth')
    
    model.load_state_dict(torch.load(parsed_args.checkpoint, map_location=args.device))

    print(f"🔄 Processing Image: {image_path}")
    latex_result = predict_single_image(image_path, model, args)

    if latex_result:
        print(f"✅ Predicted LaTeX:\n{latex_result}")
    else:
        print("❌ Prediction failed.")
