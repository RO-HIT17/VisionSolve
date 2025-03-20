import fitz  
import google.generativeai as genai
import os
from dotenv import load_dotenv
from test_generate_video import generate_educational_video

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def extract_images_from_pdf(pdf_path, output_folder):
    """Extracts images from a PDF file."""
    doc = fitz.open(pdf_path)
    image_paths = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_num in range(len(doc)):
        for img_index, img in enumerate(doc[page_num].get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_path = os.path.join(output_folder, f"page_{page_num+1}_img_{img_index+1}.png")

            with open(image_path, "wb") as f:
                f.write(base_image["image"])

            image_paths.append(image_path)

    return image_paths

def extract_text_from_image(image_path):
    """Uses Gemini AI to extract handwritten text from an image."""
    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()

    response = model.generate_content([{"mime_type": "image/png", "data": img_bytes}])

    extracted_text = response.text if response and response.text else ""
    return extracted_text

def summarize_text(text):
    """Uses Gemini AI to generate a summary of the extracted text."""
    prompt = f"Summarize the following handwritten notes concisely:\n\n{text}.the notes have to be clear and detailed describing each part"
    response = model.generate_content(prompt)

    summary = response.text if response and response.text else "Summary not generated."
    return summary

def process_pdf_to_summary(pdf_path, output_txt_path, summary_txt_path):
    """Extracts handwritten text from a PDF using Gemini AI and generates a summary."""
    image_folder = "temp_images"

    print("[INFO] Extracting images from PDF...")
    image_paths = extract_images_from_pdf(pdf_path, image_folder)

    extracted_text = ""
    print("[INFO] Extracting text from images using Gemini...")
    
    for img_path in image_paths:
        text = extract_text_from_image(img_path)
        extracted_text += text + "\n\n"

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"[SUCCESS] Extracted text saved to: {output_txt_path}")

    print("[INFO] Generating summary using Gemini AI...")
    summary = summarize_text(extracted_text)

    # Save summary
    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"[SUCCESS] Summary saved to: {summary_txt_path}")

    for img_path in image_paths:
        os.remove(img_path)
    os.rmdir(image_folder)

pdf_path = "C:\\Rohit\\Projects\\VisionSolveEnhanced\\VisionSolve\\backend\\handwrittenpdf.pdf"  
output_txt_path = "extracted_text.txt"
summary_txt_path = "summary.txt"

process_pdf_to_summary(pdf_path, output_txt_path, summary_txt_path)

with open(summary_txt_path, "r", encoding="utf-8") as f:
        latex_content = f.read()
video_path = generate_educational_video(latex_content)