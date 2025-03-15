from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from latex_generator import generate_latex_from_image
#from main1 import convert_to_latex
from lat import extract_latex_from_image
from test_generate_video import generate_educational_video
import shutil
app = Flask(__name__)
CORS(app)  

STATIC_VIDEOS_FOLDER = 'static/' 
UPLOAD_FOLDER = 'snap'
STATIC_FOLDER = 'static'
HANDWRITTEN_FOLDER = 'handwritten'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(HANDWRITTEN_FOLDER, exist_ok=True)

@app.route('/api/ask', methods=['POST'])
def handle_question():
    data = request.json
    user_input = data.get('message', '')
    
    # Process the question (mock implementation)
    response = {
        'videoUrl': f'/static/video.mp4',
        'message': f'Processed your question: {user_input}'
    }
    return jsonify(response)

@app.route('/api/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save uploaded file
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    latex_equation = generate_latex_from_image(file_path)
    vidpath=generate_educational_video(latex_equation)
    #vidpath="videos\8375c77d.mp4"
    #print("Video path:",vidpath)
    ##print("Latex:",latex_equation)
    video_url = vidpath.replace('\\', '/')
    #video_url = f'/{video_url}'
    #print("Video path:",video_url)
    
    video_filename = os.path.basename(video_url)  # Extract just the filename
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)

    # Move file to static/videos/
    shutil.move(vidpath, new_video_path)  # This physically moves the file

    # ✅ Return URL that can be accessed from frontend
    video_url = f'/static/{video_filename}'
    
    # Process file (mock implementation)
    response = {
        #backend\static\video.mp4
        #backend\videos\8375c77d.mp4
        'videoUrl': video_url,
        'message': f'Processed your file: {filename}',
        'latexEquation': latex_equation
    }
    return jsonify(response)

@app.route('/api/upload/handwritten', methods=['POST'])
def handle_handwritten_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    #latex_equation = generate_latex_from_image(file_path)
    
    
    # Save handwritten file
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(HANDWRITTEN_FOLDER, filename)
    file.save(file_path)
    
    latex=extract_latex_from_image(file_path)
    #print("Latex:",extract_latex_from_image(latex))
    vidpath=generate_educational_video(latex)
    video_url = vidpath.replace('\\', '/')
    video_filename = os.path.basename(video_url)  # Extract just the filename
    new_video_path = os.path.join(STATIC_VIDEOS_FOLDER, video_filename)

    # Move file to static/videos/
    shutil.move(vidpath, new_video_path)  # This physically moves the file

    # ✅ Return URL that can be accessed from frontend
    video_url = f'/static/{video_filename}'
    
    
    # Process handwritten file (mock implementation)
    response = {
        'videoUrl': video_url,
        'message': f'Processed handwritten question: {filename}',
        'latexEquation': extract_latex_from_image(file_path)
    }
    return jsonify(response)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True,use_reloader=False)