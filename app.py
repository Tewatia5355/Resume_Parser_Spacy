import os
import sys
import fitz
import glob
import errno
import spacy
import numpy as np
import filetype
import re
import shutil
from flask import Flask, render_template, request, redirect, url_for, abort, send_file
from werkzeug.utils import secure_filename
from os.path import isfile, join

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024*1024*10
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['OUTPUT_PATH'] = 'output'


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html')


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/parser")
def compress():
    return render_template("compress.html")


@app.route("/process", methods=['POST'])
def process_file():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    output_file = filename
    currr_path = os.getcwd()
    temp = currr_path + "/output"
    if os.path.exists(temp):
        os.chdir(temp)
        files = glob.glob('*')
        for f in files:
            os.remove(f)
    else:
        os.mkdir(temp)
    os.chdir(currr_path)

    success_code = -1
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        if os.path.exists('./'+app.config['UPLOAD_PATH']+'/'+filename):
            os.remove('./'+app.config['UPLOAD_PATH']+'/'+filename)
        uploaded_file.save('./'+app.config['UPLOAD_PATH']+'/'+filename)
        doc = fitz.open('./'+app.config['UPLOAD_PATH']+'/'+filename)
        teext = ""
        for page in doc:
            teext = teext + str(page.getText())

        tx = " ".join(teext.split('\n'))
        nlp_model = spacy.load('nlp_model')
        doc = nlp_model(tx)

        with open("output.txt", "w") as f:
            print("RESUME PARSED USING SPACY - by Yash Kumar -> 101803064 \n\n", file=f)

        f = open("output.txt", "a")
        for ent in doc.ents:
            print(f'{ent.label_.upper():{30}}- {ent.text}', file=f)
        f.close()
        return send_file("output.txt", as_attachment=True, attachment_filename=filename+"__Resume_parsed.txt")


if __name__ == "__main__":
    app.run()
