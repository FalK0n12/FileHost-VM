from flask import Flask, request, render_template, send_from_directory
import os
from datetime import datetime
import math

app = Flask(__name__)

fileDirectory = os.path.join(os.getcwd(), "files")
os.makedirs(fileDirectory, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024 * 1024


def get_file_info(filename):
    filepath = os.path.join(fileDirectory, filename)
    if os.path.exists(filepath):
        stat = os.stat(filepath)
        size_bytes = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Format file size
        if size_bytes == 0:
            size_str = "0 B"
        else:
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            size_str = f"{round(size_bytes / p, 1)} {size_names[i]}"
        
        return {
            'name': filename,
            'size': size_str,
            'date': modified_time.strftime('%d/%m/%Y %H:%M'),
            'extension': os.path.splitext(filename)[1].lower()
        }
    return None

def get_files_with_info():
    items = os.listdir(fileDirectory)
    files_info = []
    for item in items:
        info = get_file_info(item)
        if info:
            files_info.append(info)
    files_info.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y %H:%M'), reverse=True)
    return files_info

@app.route("/")
def Index():
    files_info = get_files_with_info()
    last_updated = datetime.now().strftime('%d/%m/%Y %H:%M GMT%z')
    return render_template('index.html', FILES=files_info, last_updated=last_updated)

@app.route("/Upload", methods=["GET","POST"])
def Upload():
    if request.method == "POST":
        if "File" not in request.files:
            return "No file part"
        file = request.files["File"]
        if file.filename == "":
            return "No selected file"
        items = os.listdir(fileDirectory)
        if file.filename in items:
            files_info = get_files_with_info()
            return render_template('index.html', FILES=files_info, ERROR="error", last_updated=last_updated)
        filepath = os.path.join(fileDirectory, file.filename)
        file.save(filepath)
        files_info = get_files_with_info()
        return render_template('index.html', FILES=files_info, filename=file.filename, last_updated=last_updated)
    else:
        files_info = get_files_with_info()
        return render_template('index.html', FILES=files_info, last_updated=last_updated)
    
@app.route("/download/<fileName>")
def Download(fileName: str):
    filepath = os.path.join(fileDirectory, fileName)
    if os.path.exists(filepath):
        return send_from_directory(fileDirectory, fileName, as_attachment=True)
    else:
        return "No such file exists"

if __name__ == '__main__':
    app.run(debug=True)