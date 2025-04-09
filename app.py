from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Folder for saving uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions (images only)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Page 0: New Object – Upload Image
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        object_name = request.form.get('object_name')
        file = request.files.get('input_file')
        if not object_name:
            flash('Please enter a name for the object.')
            return redirect(request.url)
        if not file or file.filename == "":
            flash('No file selected.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded.')
            return redirect(url_for('robot', object_name=object_name, filename=filename))
        else:
            flash('Unsupported file format. Please upload a JPG, JPEG, or PNG image.')
            return redirect(request.url)
    return render_template('index.html')

# Page 1: Robot Launch – Show default image after upload
@app.route('/robot', methods=['GET', 'POST'])
def robot():
    object_name = request.args.get('object_name')
    filename = request.args.get('filename')
    if request.method == 'POST':
        flash('Robot launched successfully. Coordinates have been updated.')
        return redirect(url_for('analysis', object_name=object_name))
    return render_template('robot.html', object_name=object_name, filename=filename)

# Page 2: Analysis – Image magnifier effect with lens lock on dblclick
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    object_name = request.args.get('object_name')
    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        flash(f'{analysis_type} analysis completed for object "{object_name}".')
        return redirect(url_for('analysis', object_name=object_name))
    return render_template('analysis.html', object_name=object_name)

if __name__ == '__main__':
    app.run(debug=True)
