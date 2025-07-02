from flask import Blueprint, render_template, request, redirect, send_file
import pandas as pd
from sqlalchemy import create_engine
import joblib
import os
from xhtml2pdf import pisa
from io import BytesIO
import tempfile
from utils.opciones_formulario import paises, niveles_academicos, plataformas_sociales, estados_civiles

formulario_bp = Blueprint('formulario', __name__)

# ──────────────────────────────────────────────
# Traducciones español → inglés
# ──────────────────────────────────────────────
paises_map = {
    "Afganistán": "Afghanistan", "Alemania": "Germany", "Arabia Saudita": "Saudi Arabia", "Argentina": "Argentina",
    "Australia": "Australia", "Austria": "Austria", "Bolivia": "Bolivia", "Brasil": "Brazil", "Bélgica": "Belgium",
    "Canadá": "Canada", "Chile": "Chile", "China": "China", "Colombia": "Colombia", "Corea del Sur": "South Korea",
    "Costa Rica": "Costa Rica", "Cuba": "Cuba", "Dinamarca": "Denmark", "Ecuador": "Ecuador", "Egipto": "Egypt",
    "El Salvador": "El Salvador", "Emiratos Árabes Unidos": "United Arab Emirates", "España": "Spain",
    "Estados Unidos": "United States", "Estonia": "Estonia", "Filipinas": "Philippines", "Finlandia": "Finland",
    "Francia": "France", "Grecia": "Greece", "Guatemala": "Guatemala", "Honduras": "Honduras", "Hungría": "Hungary",
    "India": "India", "Indonesia": "Indonesia", "Irlanda": "Ireland", "Israel": "Israel", "Italia": "Italy",
    "Japón": "Japan", "Kazajistán": "Kazakhstan", "Letonia": "Latvia", "Lituania": "Lithuania", "Malasia": "Malaysia",
    "Marruecos": "Morocco", "México": "Mexico", "Nicaragua": "Nicaragua", "Noruega": "Norway", "Nueva Zelanda": "New Zealand",
    "Países Bajos": "Netherlands", "Panamá": "Panama", "Paraguay": "Paraguay", "Perú": "Peru", "Polonia": "Poland",
    "Portugal": "Portugal", "Puerto Rico": "Puerto Rico", "Reino Unido": "United Kingdom", "República Checa": "Czech Republic",
    "República Dominicana": "Dominican Republic", "Rumanía": "Romania", "Rusia": "Russia", "Sudáfrica": "South Africa",
    "Suecia": "Sweden", "Suiza": "Switzerland", "Tailandia": "Thailand", "Turquía": "Turkey", "Ucrania": "Ukraine",
    "Uruguay": "Uruguay", "Venezuela": "Venezuela", "Vietnam": "Vietnam", "Otro": "Other"
}

niveles_map = {
    "Primaria": "Primary",
    "Secundaria": "High School",
    "Preparatoria / Bachillerato": "High School",
    "Técnico / Tecnológico": "Technical",
    "Licenciatura / Grado": "Bachelor's",
    "Maestría / Posgrado": "Master's",
    "Doctorado": "PhD",
    "Otro": "Other"
}

estados_civiles_map = {
    "Soltero/a": "Single",
    "En una relación": "In Relationship",
    "Casado/a": "Married",
    "Comprometido/a": "Engaged",
    "Separado/a": "Separated",
    "Divorciado/a": "Divorced",
    "Viudo/a": "Widowed",
    "Es complicado": "Complicated",
    "Prefiero no decirlo": "Prefer not to say"
}

gender_map = {
    "Masculino": "Male",
    "Femenino": "Female",
    "Otro": "Other"
}

afectacion_map = {
    "Sí": "Yes",
    "No": "No"
}

# ──────────────────────────────────────────────
# Conexión a la base de datos
# ──────────────────────────────────────────────
def get_engine():
    usuario = '410495'
    contraseña = 'Jorger0:v'
    servidor = 'mysql-terravision.alwaysdata.net'
    nombre_bd = 'terravision_socialmedia'
    url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
    return create_engine(url)

# ──────────────────────────────────────────────
# Cargar modelo y columnas de entrada
# ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, '../modelo/modelo_multioutput.pkl'))
COLUMNS_PATH = os.path.abspath(os.path.join(BASE_DIR, '../modelo/input_columns.pkl'))

model = joblib.load(MODEL_PATH)
input_columns = joblib.load(COLUMNS_PATH)

# ──────────────────────────────────────────────
# Ruta del formulario
# ──────────────────────────────────────────────
@formulario_bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Traducción de campos antes de procesar
        datos_usuario = {
            'Age': int(request.form['Age']),
            'Gender': gender_map.get(request.form['Gender']),
            'Academic_Level': niveles_map.get(request.form['Academic_Level'], 'Other'),
            'Country': request.form['Country'],
            'Avg_Daily_Usage_Hours': float(request.form['Avg_Daily_Usage_Hours']),
            'Most_Used_Platform': request.form['Most_Used_Platform'],
            'Sleep_Hours_Per_Night': float(request.form['Sleep_Hours_Per_Night']),
            'Relationship_Status': estados_civiles_map.get(request.form['Relationship_Status'], 'Other'),
            'Conflicts_Over_Social_Media': int(request.form['Conflicts_Over_Social_Media'])

        }

        # Para mostrar al usuario en español
        datos_usuario_es = {
            'Age': request.form['Age'],
            'Gender': request.form['Gender'],
            'Academic_Level': request.form['Academic_Level'],
            'Country': paises_map.get(request.form['Country'], 'Other'),
            'Avg_Daily_Usage_Hours': request.form['Avg_Daily_Usage_Hours'],
            'Most_Used_Platform': request.form['Most_Used_Platform'],
            'Sleep_Hours_Per_Night': request.form['Sleep_Hours_Per_Night'],
            'Relationship_Status': request.form['Relationship_Status'],
            'Conflicts_Over_Social_Media': request.form['Conflicts_Over_Social_Media']
        }

        # Convertir a DataFrame
        df_input = pd.DataFrame([datos_usuario])
        df_encoded = pd.get_dummies(df_input)

        # Asegurar que todas las columnas del modelo estén presentes
        columnas_faltantes = [col for col in input_columns if col not in df_encoded.columns]
        df_encoded[columnas_faltantes] = 0
        df_encoded = df_encoded[input_columns]
        df_encoded = df_encoded.astype(float)

        # Predicción
        pred = model.predict(df_encoded)[0]
        afectacion_bool = int(round(pred[0]))
        afectacion_texto = 'Sí' if afectacion_bool == 1 else 'No'
        adiccion = round(pred[1], 2)
        salud_mental = round(pred[2], 2)

        datos_completos = {
            **datos_usuario,
            'Affects_Academic_Performance': afectacion_map.get(afectacion_texto, "No"),
            'Affects_Academic_Performance(True booleano)': afectacion_bool,
            'Addicted_Score': adiccion,
            'Mental_Health_Score': salud_mental
        }

        # Para mostrar en la interfaz/PDF
        datos_mostrar = {
            **datos_usuario_es,
            'Affects_Academic_Performance': afectacion_texto,
            'Affects_Academic_Performance(True booleano)': afectacion_bool,
            'Addicted_Score': adiccion,
            'Mental_Health_Score': salud_mental
        }

        # Guardar en base de datos (en inglés)
        df_final = pd.DataFrame([datos_completos])
        engine = get_engine()
        df_final.to_sql('socialmedia_lectura', con=engine, if_exists='append', index=False)

        # Generar PDF
        rendered = render_template("resultado_pdf.html", datos=datos_mostrar)
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_file)

        pdf_path = None
        if not pisa_status.err:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                f.write(pdf_file.getvalue())
                pdf_path = f.name

        return render_template("resultado.html", datos=datos_mostrar, pdf_path=pdf_path)

    # Método GET
    return render_template("formulario.html",
        paises=paises,
        niveles=niveles_academicos,
        plataformas=plataformas_sociales,
        estados=estados_civiles)

# ──────────────────────────────────────────────
# Ruta para descargar el PDF generado
# ──────────────────────────────────────────────
@formulario_bp.route('/descargar_pdf')
def descargar_pdf():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "PDF no encontrado", 404
