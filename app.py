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

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Datos de entrada del usuario
        age = int(request.form['Age'])
        gender = request.form['Gender']
        academic_level = request.form['Academic_Level']
        country = request.form['Country']
        avg_usage = float(request.form['Avg_Daily_Usage_Hours'])
        platform = request.form['Most_Used_Platform']
        sleep_hours = float(request.form['Sleep_Hours_Per_Night'])
        relationship = request.form['Relationship_Status']
        conflicts = int(request.form['Conflicts_Over_Social_Media'])

        # 💡 Lógica simple de predicción (puedes reemplazarla por un modelo ML real)
        addicted_score = min(100, avg_usage * 12 + conflicts * 2)
        mental_health_score = max(0, 100 - (avg_usage * 5 + conflicts))

        # Afecta el rendimiento si adicción o bajo sueño o alto conflicto
        if addicted_score > 60 or sleep_hours < 6 or conflicts > 2:
            affects = "Sí afecta el rendimiento"
            affects_bool = 1
        else:
            affects = "No afecta el rendimiento"
            affects_bool = 0

        # Diccionario final
        datos = {
            'Age': age,
            'Gender': gender,
            'Academic_Level': academic_level,
            'Country': country,
            'Avg_Daily_Usage_Hours': avg_usage,
            'Most_Used_Platform': platform,
            'Affects_Academic_Performance': affects,
            'Affects_Academic_Performance_Bool': affects_bool,
            'Sleep_Hours_Per_Night': sleep_hours,
            'Mental_Health_Score': int(mental_health_score),
            'Relationship_Status': relationship,
            'Conflicts_Over_Social_Media': conflicts,
            'Addicted_Score': int(addicted_score)
        }

        # Insertar en la base de datos
        df = pd.DataFrame([datos])
        engine = get_engine()
        df.to_sql('socialmedia_lectura', con=engine, if_exists='append', index=False)

        return redirect('/')

    return render_template('formulario.html')


if __name__ == '__main__':
    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True)