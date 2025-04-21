from flask import Flask, render_template, request, redirect
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
s3 = boto3.client('s3')
S3_BUCKET = 'files-bucket-number1'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=file.read())
            url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
            return render_template('index.html', download_url=url)
    return render_template('index.html', download_url=None)

@app.route('/download/<filename>')
def download_file(filename):
    return redirect(f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
