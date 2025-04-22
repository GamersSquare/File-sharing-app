from flask import Flask, render_template, request, redirect
import boto3
from werkzeug.utils import secure_filename
from botocore.exceptions import ClientError

app = Flask(__name__)

# Configuration
S3_BUCKET = 'files-bucket-number1'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}
s3 = boto3.client('s3')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_exists_in_s3(filename):
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=filename)
        return True
    except ClientError:
        return False

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None

    if request.method == 'POST':
        if 'file' not in request.files:
            message = "No file part"
        else:
            file = request.files['file']
            if file.filename == '':
                message = "No selected file"
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if file_exists_in_s3(filename):
                    message = f"⚠️ File '{filename}' already exists!"
                else:
                    s3.put_object(Bucket=S3_BUCKET, Key=filename, Body=file.read())
                    message = f"✅ File '{filename}' uploaded successfully!"

    # List all files
    file_list = []
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        for obj in response.get('Contents', []):
            file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{obj['Key']}"
            file_list.append({'name': obj['Key'], 'url': file_url})
    except Exception as e:
        message = f"Error listing files: {str(e)}"

    return render_template('index.html', message=message, files=file_list)

@app.route('/download/<filename>')
def download_file(filename):
    return redirect(f"https://{S3_BUCKET}.s3.amazonaws.com/{filename}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
