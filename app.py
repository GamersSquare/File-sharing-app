from flask import Flask, render_template, request, redirect, url_for
import boto3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
s3 = boto3.client('s3')

# Replace with your bucket name
S3_BUCKET = 'files-bucket-number1'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_content = file.read()

            # Upload to S3
            s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=file_content)
            download_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
            return render_template('index.html', download_url=download_url)

    return render_template('index.html', download_url=None)


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}"
        return redirect(file_url)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
