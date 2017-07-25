import os
import time
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename, redirect

PROJECT_BASE = os.path.dirname(__file__)

UPLOAD_FOLDER = os.path.join(PROJECT_BASE, 'images')
SAMPLES_FOLDER = os.path.join(PROJECT_BASE, 'images')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

SCRIPT = "/root/sxl/models/tutorials/image/imagenet/classify_image.py"


def list_history(results=None):
    history_pictures = []
    uploaded_files = os.listdir(SAMPLES_FOLDER)
    for full_name in uploaded_files:
        file_name, ext = os.path.splitext(full_name)
        short_name, timestamp = os.path.splitext(file_name)
        comments = ""
        if results:
            for result in results:
                if result['name'] == full_name:
                    comments = result['comments']

        history_pictures.append(('{}{}'.format(short_name, ext), full_name, comments))

    return history_pictures


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.jinja_env.globals['static'] = (lambda filename: url_for('static', filename=filename))


@app.route('/sample/<path:filename>')
def sample_static(filename):
    return send_from_directory(SAMPLES_FOLDER, filename)


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
            # 'comments': image_name
        })

    print "MULTIPLE: {}".format(results)
    return render_template('index.html', history_pictures=list_history(results), sample_results=['1'])


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        print "===== execute POST"
        uploaded_files = request.files.getlist("image")
        if not uploaded_files:
            print "===== Empty uploaded!"
            return render_template('index.html', history_pictures=list_history())

        results = []
        for _file in uploaded_files:
            filename = secure_filename(_file.filename)
            short_name, ext = os.path.splitext(filename)
            final_file_name = '{}.{}{}'.format(short_name, int(time.time()), ext)
            image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], final_file_name)
            _file.save(image_file_path)

            print "===== Parse the file: {}".format(final_file_name)
            items = parse_image(final_file_name)
            print "RESULT ITEMS {}".format(items)
            results.append({
                'picture': final_file_name,
                'item_name': items[0]
                # 'item_name': short_name
            })

        return render_template('index.html', items=results, history_pictures=list_history(), sample_results=[])

    return render_template('index.html', history_pictures=list_history(), sample_results=[])


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
