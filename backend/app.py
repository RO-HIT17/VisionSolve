from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

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
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    response = {
        'videoUrl': '/static/video.mp4',
        'message': f'Processed your file: {filename}'
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
    
    response = {
        'videoUrl': '/static/video.mp4',
        'message': f'Processed handwritten question: {filename}'
    }
    return jsonify(response)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    app.run(port=5000, debug=True)