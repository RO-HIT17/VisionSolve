import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def     ask_gemini(file_path, question):
    context_text = read_text_file(file_path)

    prompt = f"""
    Given the following text:

    {context_text}

    Answer the question concisely:
    {question}
    """

    response = model.generate_content(prompt)
    return response.text