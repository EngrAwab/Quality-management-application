from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Folder for saving uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------------------------------------
#   MAIN PAGE (REDESIGNED FIRST PAGE)
# ---------------------------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# ---------------------------------------------
#   COORDINATES FILE UPLOAD (via fetch/JS)
# ---------------------------------------------
@app.route('/upload_coords', methods=['POST'])
def upload_coords():
    object_name = request.form.get('object_name', '').strip()
    if not object_name:
        return jsonify(status='error', message='Object name is required.')

    coords_file = request.files.get('coords_file')
    if not coords_file:
        return jsonify(status='error', message='No file was uploaded.')
    if not coords_file.filename.lower().endswith('.xlsx'):
        return jsonify(status='error', message='Please upload a valid .xlsx file.')

    filename = secure_filename(coords_file.filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    coords_file.save(filepath)

    try:
        import openpyxl
        workbook = openpyxl.load_workbook(filepath)
        # …process workbook…
    except Exception as e:
        return jsonify(status='error', message=f'Error reading xlsx file: {e}')

    return jsonify(
        status='success',
        redirect=url_for('robot', object_name=object_name, filename=filename)
    )


# ---------------------------------------------
#   PAGE 1 (SECOND PAGE): ROBOT INTERFACE
# ---------------------------------------------
@app.route('/robot', methods=['GET', 'POST'])
def robot():
    object_name = request.args.get('object_name', '')
    filename = request.args.get('filename', '')

    if request.method == 'POST':
        # enforce that the box was checked
        if not request.form.get('analyseCheckbox'):
            flash('You must check “Analyse photo after photo” before launching.', 'warning')
            return redirect(url_for('robot', object_name=object_name, filename=filename))

        flash('Robot launched successfully. Coordinates have been updated.', 'success')
        return redirect(url_for('analysis', object_name=object_name))

    return render_template('robot.html', object_name=object_name, filename=filename)


# ---------------------------------------------
#   PAGE 2: ANALYSIS PAGE (MAGNIFIER)
# ---------------------------------------------
@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    object_name = request.args.get('object_name')
    if request.method == 'POST':
        analysis_type = request.form.get('analysis_type')
        flash(f'{analysis_type} analysis completed for object "{object_name}".', 'success')
        return redirect(url_for('analysis', object_name=object_name))
    return render_template('analysis.html', object_name=object_name)


if __name__ == '__main__':
    app.run(debug=True)
