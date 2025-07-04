import os
from flask import Flask, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.secret_key = 'tu_clave_secreta'  # Cambia esto en producción

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verifica si se envió un archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Si no se selecciona archivo
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        # Validar extensión
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Procesar el archivo con main.py
            try:
                # Aquí llamarías a main.py (ajusta según tu estructura)
                from main import importar_csv
                importar_csv()  # Asegúrate de modificar main.py para aceptar el nombre del archivo
                flash('¡Archivo subido y procesado con éxito!', 'success')
            except Exception as e:
                flash(f'Error al procesar el archivo: {str(e)}', 'error')
            
            return redirect(url_for('upload_file'))
        
        flash('Formato no válido. Solo se aceptan CSV o XLSX.', 'error')
    
    return render_template('upload.html')