import os
import fitz  
import re
from test_generate_video import generate_educational_video  

def generate_latex_from_pdf(pdf_path, output_dir="output"):
    
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    tex_filename = f"{base_name}.tex"
    tex_path = os.path.join(output_dir, tex_filename)
    
    def extract_text_from_pdf(pdf_path):
        doc = fitz.open(pdf_path)
        extracted_text = "\n\n".join([page.get_text("text") for page in doc])
        return extracted_text

    def format_latex(text):
        text = text.replace("%", "\\%")
        text = text.replace("&", "\\&")
        text = text.replace("#", "\\#")
        text = re.sub(r"(\w+)\^(\d+)", r"$\1^{\2}$", text)  
        return text

    def create_latex_document(text):
        return rf"""
\documentclass{{article}}
\usepackage{{amsmath}}
\usepackage{{graphicx}}

\begin{{document}}

{text}

\end{{document}}
"""

    extracted_text = extract_text_from_pdf(pdf_path)
    latex_text = format_latex(extracted_text)
    latex_document = create_latex_document(latex_text)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_document)
    
    print(f"LaTeX document saved as {tex_path}")

    with open(tex_path, "r", encoding="utf-8") as f:
        latex_content = f.read()
    
    video_path = generate_educational_video(latex_content)

    print(f"Video saved as {video_path}")

    return {
        "latex_file": tex_path,
        "video_file": video_path
    }


if __name__ == "__main__":
    pdf_path = "C:\\Rohit\\Projects\\VisionSolveEnhanced\\VisionSolve\\backend\\EMD_U4.pdf"  
    output_files = generate_latex_from_pdf(pdf_path)
    print(output_files)