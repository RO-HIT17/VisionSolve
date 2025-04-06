from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import shutil
import subprocess

from docx import Document
from pptx import Presentation

from latex_generator import genrate_latex_from_image
from latex_generater import generate_latex_from_image
from test_generate_video import generate_educational_video
from generate_video_for_pdf import generate_latex_from_pdf
from answer import ask_gemini

app = Flask(__name__)
CORS(app)  

STATIC_VIDEOS_FOLDER = 'static/' 
UPLOAD_FOLDER = 'snap'
PDF_UPLOAD_FOLDER = 'pdfs'
STATIC_FOLDER = 'static'
HANDWRITTEN_FOLDER = 'handwritten'
VIDEOS_FOLDER = os.path.join(os.getcwd(), 'videos')
os.makedirs(VIDEOS_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(HANDWRITTEN_FOLDER, exist_ok=True)
os.makedirs(PDF_UPLOAD_FOLDER, exist_ok=True)

def convert_docx_to_pdf(docx_path, pdf_path):
    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", PDF_UPLOAD_FOLDER, docx_path], check=True)
        return pdf_path
    except Exception as e:
        return str(e)
    
def convert_pptx_to_pdf(pptx_path, pdf_path):
    try:
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", PDF_UPLOAD_FOLDER, pptx_path], check=True)
        return pdf_path
    except Exception as e:
        return str(e)
    

def get_latest_text_file(directory):
    try:
        files = [f for f in os.listdir(directory) if f.endswith(".txt")]
        if not files:
            return None
        
        latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
        return os.path.join(directory, latest_file)
    except Exception as e:
        print("Error finding latest file:", e)
        return None
    
@app.route('/api/ask', methods=['POST'])
def handle_question():
    data = request.json
    user_input = data.get('message', '')
    
    vidpath=generate_educational_video(user_input)
    video_url = vidpath.replace('\\', '/')
    
    video_filename = os.path.basename(video_url)
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)
    shutil.move(vidpath, new_video_path)
    video_url = f'/static/{video_filename}'
    
    response = {
        'videoUrl': video_url,
        'message': f'Processed your question: {user_input}'
    }
    return jsonify(response)

@app.route('/api/ask/text', methods=['POST'])
def handle_text_question():
    data = request.json
    user_input = data.get('message', '')
    file_path = get_latest_text_file("output")
    result=ask_gemini(file_path,user_input)
    return jsonify({'message': result})

@app.route('/api/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    latex_equation = genrate_latex_from_image(file_path)
    vidpath=generate_educational_video(latex_equation)
    video_url = vidpath.replace('\\', '/')
    
    video_filename = os.path.basename(video_url)  
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)

    shutil.move(vidpath, new_video_path)  

    video_url = f'/static/{video_filename}'
    
    response = {
        'videoUrl': video_url,
        'message': f'Processed your file: {filename}',
        'latexEquation': latex_equation
    }
    return jsonify(response)

@app.route('/api/upload/pdf', methods=['POST'])
def handle_upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(PDF_UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    pdf_path = os.path.join(PDF_UPLOAD_FOLDER, f"{name}.pdf")
    
    if ext.lower() == ".docx":
        pdf_path = convert_docx_to_pdf(file_path, pdf_path)
    elif ext.lower() == ".pptx":
        pdf_path = convert_pptx_to_pdf(file_path, pdf_path)
    elif ext.lower() != ".pdf":
        return "Unsupported file format", None
    
    result = generate_latex_from_pdf(pdf_path)
    
    vidpath = result['video_file']
    latex_file = result['latex_file']
    
    video_url = vidpath.replace('\\', '/')
    video_filename = os.path.basename(video_url)
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)
    shutil.move(vidpath, new_video_path)
    video_url = f'/static/{video_filename}'
    response = {
        'videoUrl': video_url,
        'message': f'Processed your file: {filename}',
        'latex_file': latex_file
    }  
    return jsonify(response)


@app.route('/api/upload/handwritten', methods=['POST'])
def handle_handwritten_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(HANDWRITTEN_FOLDER, filename)
    file.save(file_path)
    
    latex=generate_latex_from_image(file_path)
    vidpath=generate_educational_video(latex)
    video_url = vidpath.replace('\\', '/')
    video_filename = os.path.basename(video_url)  
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)

    shutil.move(vidpath, new_video_path)  

    video_url = f'/static/{video_filename}'
    
    response = {
        'videoUrl': video_url,
        'message': f'Processed handwritten question: {filename}',
        'latexEquation': latex
    }
    return jsonify(response)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

@app.route('/videos/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEOS_FOLDER, filename)

@app.route("/")
def home():
    return "🔥 Flask app is running!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # 👈 Grab port from environment (Azure sets this!)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)