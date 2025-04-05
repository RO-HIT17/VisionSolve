import google.generativeai as genai
from PIL import Imagev
import os
from dotenv import load_dotenv
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def generate_latex_from_image(image_path, api_key=None):
    if api_key:
        genai.configure(api_key=api_key)

    img = Image.open(image_path)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = (
        "Extract only the LaTeX expression from this handwritten equation. "
        "Do not add any explanations, text, or formatting. Just output raw LaTeX code:"
    )

    response = model.generate_content([prompt, img])

    latex_output = response.text.strip()
    return latex_output