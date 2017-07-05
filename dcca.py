import os
import time
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename, redirect

PROJECT_BASE = os.path.dirname(__file__)

UPLOAD_FOLDER = os.path.join(PROJECT_BASE, 'images')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

SCRIPT = "/root/sxl/models/tutorials/image/imagenet/classify_image.py"


def list_history():
    history_pictures = []
    uploaded_files = os.listdir(UPLOAD_FOLDER)
    for full_name in uploaded_files:
        file_name, ext = os.path.splitext(full_name)
        short_name, timestamp = os.path.splitext(file_name)
        history_pictures.append(('{}{}'.format(short_name, ext), full_name,))

    return history_pictures


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/pic/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def parse_image(image_name):
    _path = os.path.join("/root/dcca/images", image_name)
    p = subprocess.Popen(['python', SCRIPT, '--image_file', _path], stdout=subprocess.PIPE)
    p.wait()
    return p.communicate()

    
@app.route('/multiple', methods=['GET', 'POST'])
def parse_multiple_images():
    if request.method == 'GET':
        return redirect(url_for('upload_image'))

    images = request.form.getlist('image_names')

    results = []
    for image_name in images:
        res = parse_image(image_name) 
        results.append({
            'name': image_name,
            'comments': res[0]
        })

    return render_template('index.html', history_pictures=list_history(), multi_result=results)


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        _file = request.files['image']
        if _file.filename == "":
            return render_template('index.html', history_pictures=list_history())
        filename = secure_filename(_file.filename)
        short_name, ext = os.path.splitext(filename)
        final_file_name = '{}.{}{}'.format(short_name, int(time.time()), ext)
        image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_file_name)
        _file.save(image_file_path)
        
        results = parse_image(final_file_name)
        
        return render_template('index.html', picture=final_file_name, result=results[0], history_pictures=list_history())
    return render_template('index.html', history_pictures=list_history())


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
