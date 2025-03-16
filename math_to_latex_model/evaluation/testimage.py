from pix2tex.models import get_model
from pix2tex.utils import *
from pix2tex.dataset.transforms import test_transform as get_transform
from PIL import Image
from pix2tex.dataset.dataset import Im2LatexDataset
import argparse
import logging
import yaml
import torch

def predict_single_image(image_path, model, tokenizer, args):
    
    device = args.device
    model.eval()
    
    image = Image.open(image_path).convert('RGB')
    transform = get_transform(args)
    image_tensor = transform(image).unsqueeze(0).to(device)  

    
    with torch.no_grad():
        output_tokens = model.generate(image_tensor, temperature=args.get('temperature', .2))
    
    latex_code = token2str(output_tokens, tokenizer)[0]  

    latex_code = post_process(latex_code)

    return latex_code

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test model')
    parser.add_argument('--config', default=None, help='path to yaml config file', type=str)
    parser.add_argument('-c', '--checkpoint', default=None, type=str, help='path to model checkpoint')
    parser.add_argument('--image', default=None, type=str, help='Path to single image file for prediction')
    parser.add_argument('--no-cuda', action='store_true', help='Use CPU')
    parser.add_argument('-b', '--batchsize', type=int, default=10, help='Batch size')
    parser.add_argument('--debug', action='store_true', help='DEBUG')
    parser.add_argument('-t', '--temperature', type=float, default=.333, help='sampling temperature')

    parsed_args = parser.parse_args()
    if parsed_args.config is None:
        with in_model_path():
            parsed_args.config = os.path.realpath('config.yaml')
    with open(parsed_args.config, 'r') as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    args = parse_args(Munch(params))
    args.wandb = False
    args.temperature = parsed_args.temperature
    args.device = 'cuda' if torch.cuda.is_available() and not parsed_args.no_cuda else 'cpu'
    logging.getLogger().setLevel(logging.DEBUG if parsed_args.debug else logging.WARNING)
    seed_everything(args.seed if 'seed' in args else 42)
    model = get_model(args).to(args.device)

    if parsed_args.checkpoint is None:
        with in_model_path():
            parsed_args.checkpoint = os.path.realpath('mixed_e01_step16298.pth')
    model.load_state_dict(torch.load(parsed_args.checkpoint, map_location=args.device))

    tokenizer = Im2LatexDataset().tokenizer

    if parsed_args.image is not None:
        latex_result = predict_single_image(parsed_args.image, model, tokenizer, args)
        print(f"Predicted LaTeX:\n{latex_result}")
    else:
        print("Please provide an image path using --image to predict LaTeX.")
