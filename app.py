from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename
import os
import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash('The original image displayed below')
        IMAGE_PATH='static/uploads/' +filename
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(IMAGE_PATH)
        top_left = tuple(result[0][0][0])
        bottom_right = tuple(result[0][0][2])
        text = result[0][1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.imread(IMAGE_PATH)
        spacer = 100
        for detection in result:
            top_left = tuple(detection[0][0])
            bottom_right = tuple(detection[0][2])
            text = detection[1]
            img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
            img = cv2.putText(img, text, (20, spacer), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
            spacer += 15

        plt.figure(figsize=(10, 10))
        plt.imshow(img)
        plt.show()
        return render_template('index.html', filename=filename)



    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
     return redirect(url_for('static', filename='uploads/' +filename), code=301)


if __name__ == "__main__":
    app.run()