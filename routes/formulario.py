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

# ──────────────────────────────
# Traducciones
paises_map_america = {
    "Argentina": "Argentina",
    "Bolivia": "Bolivia",
    "Brasil": "Brazil",
    "Canadá": "Canada",
    "Chile": "Chile",
    "Colombia": "Colombia",
    "Costa Rica": "Costa Rica",
    "Cuba": "Cuba",
    "Ecuador": "Ecuador",
    "El Salvador": "El Salvador",
    "Estados Unidos": "United States",
    "Guatemala": "Guatemala",
    "Honduras": "Honduras",
    "México": "Mexico",
    "Nicaragua": "Nicaragua",
    "Panamá": "Panama",
    "Paraguay": "Paraguay",
    "Perú": "Peru",
    "Puerto Rico": "Puerto Rico",
    "República Dominicana": "Dominican Republic",
    "Uruguay": "Uruguay",
    "Venezuela": "Venezuela",
    "Otro": "Other"
}

niveles_map = {
    "Preparatoria": "High School",
    "Universidad": "University", 
    "Posgrado ": "Postgrad",
    "Otro": "Other"
}

estados_civiles_map = {
    "Soltero/a": "Single", 
    "En una relación": "In Relationship", 
    "Casado/a": "Married",
    "Otro tipo de relación": "Other"
}

gender_map = {
    "Masculino": "Male", "Femenino": "Female", "Otro": "Other"
}

afectacion_map = {
    "Sí": "Yes", "No": "No"
}

# ──────────────────────────────
# Conexión a la base de datos
# ──────────────────────────────
def get_engine():
    usuario = '410495'
    contraseña = 'Jorger0:v'
    servidor = 'mysql-terravision.alwaysdata.net'
    nombre_bd = 'terravision_socialmedia'
    url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
    return create_engine(url)

# ──────────────────────────────
# Cargar modelo y columnas
# ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '../modelo/modelo_multioutput.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '../modelo/input_columns.pkl')

model = joblib.load(MODEL_PATH)
input_columns = joblib.load(COLUMNS_PATH)

# ──────────────────────────────
# Generación del gráfico
# ──────────────────────────────
def generar_grafico_radar(datos):
    etiquetas = ['Adicción', 'Salud Mental', 'Impacto Académico']
    valores = [
        datos['Addicted_Score'],
        datos['Mental_Health_Score'],
        datos['Affects_Academic_Performance(True booleano)'] * 10
    ]

    valores += valores[:1]
    angulos = np.linspace(0, 2 * np.pi, len(etiquetas), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, color='#2980b9', linewidth=2)
    ax.fill(angulos, valores, color='#2980b9', alpha=0.3)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], color="gray", size=8)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiquetas)
    ax.set_title('Evaluación General', y=1.1)

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# ──────────────────────────────
# Ruta del formulario
# ──────────────────────────────
@formulario_bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        errores = []

        # Validación básica
        try:
            age = int(request.form['Age'])
            if not (14 <= age <= 100):
                errores.append("La edad debe estar entre 14 y 100 años.")
        except:
            errores.append("La edad no es válida.")

        try:
            uso_diario = float(request.form['Avg_Daily_Usage_Hours'])
            if not (0 <= uso_diario <= 24):
                errores.append("Las horas de uso diario deben estar entre 0 y 24.")
        except:
            errores.append("Horas promedio de uso no válidas.")

        try:
            horas_sueno = float(request.form['Sleep_Hours_Per_Night'])
            if not (0 <= horas_sueno <= 24):
                errores.append("Las horas de sueño deben estar entre 0 y 24.")
        except:
            errores.append("Horas de sueño no válidas.")

        try:
            conflictos = int(request.form['Conflicts_Over_Social_Media'])
            if not (0 <= conflictos <= 5):
                errores.append("Los conflictos deben estar entre 0 y 5.")
        except:
            errores.append("Conflictos en redes no válidos.")

        if not request.form.get("Gender"):
            errores.append("Debe seleccionar el género.")
        if not request.form.get("Academic_Level"):
            errores.append("Debe seleccionar el nivel académico.")
        if not request.form.get("Country"):
            errores.append("Debe seleccionar el país.")
        if not request.form.get("Most_Used_Platform"):
            errores.append("Debe seleccionar la plataforma más usada.")
        if not request.form.get("Relationship_Status"):
            errores.append("Debe seleccionar el estado civil.")

        if errores:
            return render_template("formulario.html",
                errores=errores,
                paises=paises,
                niveles=niveles_academicos,
                plataformas=plataformas_sociales,
                estados=estados_civiles
            )

        # Preparar datos
        datos_usuario = {
            'Age': age,
            'Gender': gender_map.get(request.form['Gender']),
            'Academic_Level': niveles_map.get(request.form['Academic_Level'], 'Other'),
            'Country': request.form['Country'],
            'Avg_Daily_Usage_Hours': uso_diario,
            'Most_Used_Platform': request.form['Most_Used_Platform'],
            'Sleep_Hours_Per_Night': horas_sueno,
            'Relationship_Status': estados_civiles_map.get(request.form['Relationship_Status'], 'Other'),
            'Conflicts_Over_Social_Media': conflictos
        }

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

        df_input = pd.DataFrame([datos_usuario])
        df_encoded = pd.get_dummies(df_input)
        columnas_faltantes = [col for col in input_columns if col not in df_encoded.columns]
        df_encoded[columnas_faltantes] = 0
        df_encoded = df_encoded[input_columns].astype(float)

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

        datos_mostrar = {
            **datos_usuario_es,
            'Affects_Academic_Performance': afectacion_texto,
            'Affects_Academic_Performance(True booleano)': afectacion_bool,
            'Addicted_Score': adiccion,
            'Mental_Health_Score': salud_mental
        }

        # Guardar
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

    # GET
    return render_template("formulario.html",
        paises=paises,
        niveles=niveles_academicos,
        plataformas=plataformas_sociales,
        estados=estados_civiles)

# ──────────────────────────────
# Ruta de descarga PDF
# ──────────────────────────────
@formulario_bp.route('/descargar_pdf')
def descargar_pdf():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "PDF no encontrado", 404
