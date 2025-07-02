from flask import Flask, render_template
from routes.datos import datos_bp
from routes.formulario import formulario_bp
from routes.prediccion import predicciones_bp
from flask_mail import Mail

# ─────────────────────────────────────────────────────────────
# Configuración de la aplicación Flask
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'clave-secreta'  # Requerido para sesiones seguras

# ─────────────────────────────────────────────────────────────
# Configuración Flask-Mail
# (ajusta estos valores con tus datos reales)
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
# Registro de Blueprints (módulos organizados por funcionalidad)
# ─────────────────────────────────────────────────────────────
app.register_blueprint(datos_bp)
app.register_blueprint(formulario_bp)
app.register_blueprint(predicciones_bp)

# ─────────────────────────────────────────────────────────────
# Ruta principal (carga la plantilla index.html con Bootstrap)
# ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ─────────────────────────────────────────────────────────────
# Arranque de la aplicación
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
