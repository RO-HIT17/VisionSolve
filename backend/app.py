from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

# Path to static folder (where image and video are stored)
STATIC_DIR = os.path.join(os.getcwd(), 'static')

@app.route('/', methods=['GET', 'POST'])
def index():
    show_video = False
    if request.method == 'POST':
        user_text = request.form['user_text']

        # Overwrite 'data.txt' with the latest text
        with open('data.txt', 'w') as file:
            file.write(user_text)

        show_video = True  # Hide image and show video

    return render_template('index.html', show_video=show_video)

# Route to serve the video dynamically
@app.route('/video')
def get_video():
    return send_from_directory(STATIC_DIR, 'video.mp4')

if __name__ == '__main__':
    app.run(debug=True)
