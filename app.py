from flask import Flask, render_template
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os

# Importación de Blueprints
from routes.datos import datos_bp
from routes.formulario import formulario_bp
from routes.prediccion import predicciones_bp
from routes.routes import app_routes  # Blueprint que contiene /upload

# ─────────────────────────────────────────────────────────────
# Configuración de la aplicación Flask
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'clave-secreta'  # Requerido para sesiones seguras

# Configuración para uploads
app.config['UPLOAD_FOLDER'] = 'data'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# ─────────────────────────────────────────────────────────────
# Configuración Flask-Mail
# ─────────────────────────────────────────────────────────────
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='mauricio.suv@gmail.com',
    MAIL_PASSWORD='tgnj pnej zvkz zfin',
    MAIL_DEFAULT_SENDER='mauricio.suv@gmail.com'
)

mail = Mail(app)

# ─────────────────────────────────────────────────────────────
# Registro de Blueprints
# ─────────────────────────────────────────────────────────────
app.register_blueprint(datos_bp)
app.register_blueprint(formulario_bp)
app.register_blueprint(predicciones_bp)
app.register_blueprint(app_routes)  # Registra el Blueprint con /upload

# ─────────────────────────────────────────────────────────────
# Ruta principal
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─────────────────────────────────────────────────────────────
# Funciones auxiliares
# ─────────────────────────────────────────────────────────────
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─────────────────────────────────────────────────────────────
# Arranque de la aplicación
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)