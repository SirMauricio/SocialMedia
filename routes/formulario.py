from flask import Blueprint, render_template, request, redirect, send_file
import pandas as pd
from sqlalchemy import create_engine
import joblib
import os
from xhtml2pdf import pisa
from io import BytesIO
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import base64
from utils.opciones_formulario import paises, niveles_academicos, plataformas_sociales, estados_civiles
from routes.analisis import calcular_modelos  # función que recibe datos_usuario y retorna resultados
from flask import session, redirect, url_for
import io

formulario_bp = Blueprint('formulario', __name__)

# ──────────────────────────────
# Traducciones
paises_map = {
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
    "Sin estudios": "Undergraduate",
    "Preparatoria": "Graduate",
    "Universidad": "Graduate",
    "Posgrado": "Graduate",
    "Otro": "Graduate"
}

estados_civiles_map = {
    "Soltero/a": "Single", 
    "En una relación": "In Relationship", 
    "Es complicado": "Complicated",
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
# Generación del gráfico radar
# ──────────────────────────────
def generar_grafico_radar(datos):
    etiquetas = ['Adicción', 'Salud Mental', 'Impacto Académico']
    valores = [
        float(datos['Addicted_Score']),
        float(datos['Mental_Health_Score']),
        float(datos['Affects_Academic_Performance(True booleano)']) * 10
    ]
    valores += valores[:1]
    angulos = np.linspace(0, 2 * np.pi, len(etiquetas), endpoint=False).tolist()
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angulos, valores, color='#1abc9c', linewidth=2, marker='o')
    ax.fill(angulos, valores, color='#1abc9c', alpha=0.25)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], color="gray", size=8)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiquetas)
    ax.set_title('Evaluación General', y=1.1)

    # Agregar valores numéricos sobre los puntos
    for i, v in enumerate(valores[:-1]):
        ax.text(angulos[i], v + 0.5, f"{v:.1f}", color='black', ha='center', fontsize=8)

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return image_base64

# ──────────────────────────────
# Generación del gráfico barras
# ──────────────────────────────

def generar_grafico_barras(datos):
    labels = ['Adicción', 'Salud Mental', 'Impacto Académico']
    values = [
        float(datos['Addicted_Score']),
        float(datos['Mental_Health_Score']),
        float(datos['Affects_Academic_Performance(True booleano)']) * 10
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    colores = ['#e74c3c', '#2980b9', '#f39c12']
    bars = ax.barh(labels, values, color=colores)

    ax.set_xlim(0, 10)
    ax.set_xlabel('Puntuación')
    ax.set_title("Evaluación de Uso de Redes Sociales")

    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"{values[i]:.2f}", va='center', fontsize=9)

    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return image_base64



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

        # ───────── MODELO PRINCIPAL ─────────
        input_columns = joblib.load('modelo/input_columns.pkl')
        df_input = pd.DataFrame([datos_usuario])
        df_encoded = pd.get_dummies(df_input)

        modelo_prob_path = 'modelo/modelo_prob_afectacion_academica.pkl'
        cols_prob_path = 'modelo/input_prob_afectacion_cols.pkl'
        clf_prob = joblib.load(modelo_prob_path)
        input_cols_prob = joblib.load(cols_prob_path)

        df_input_prob = pd.get_dummies(pd.DataFrame([datos_usuario]))
        for col in input_cols_prob:
            if col not in df_input_prob.columns:
                df_input_prob[col] = 0
        df_input_prob = df_input_prob[input_cols_prob].astype(float)

        prob_afectacion = clf_prob.predict_proba(df_input_prob)[0][1]  # probabilidad clase 1
        afectacion_nivel_continuo = round(prob_afectacion * 10, 2)  # escala 0-10

        for col in input_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[input_columns].astype(float)

        model = joblib.load('modelo/modelo_multioutput.pkl')
        pred = model.predict(df_encoded)[0]
        afectacion_bool = int(round(pred[0]))
        afectacion_texto = 'Sí' if afectacion_bool == 1 else 'No'
        adiccion = round(pred[1], 2)
        salud_mental = round(pred[2], 2)

        datos_completos = {
            **datos_usuario,
            'Affects_Academic_Performance': afectacion_map.get(afectacion_texto, "No"),
            'Affects_Academic_Performance(True booleano)': afectacion_bool,
            'Affects_Academic_Performance_Prob_Score': afectacion_nivel_continuo,
            'Addicted_Score': adiccion,
            'Mental_Health_Score': salud_mental
        }

        datos_para_bd = {k: v for k, v in datos_completos.items() if k != 'Affects_Academic_Performance_Prob_Score'}
        df_final = pd.DataFrame([datos_para_bd])
        engine = get_engine()
        df_final.to_sql('SocialMediaLectura', con=engine, if_exists='append', index=False)

        input_extras_columns = joblib.load('modelo/input_extras_columns.pkl')
        df_encoded_extras = pd.get_dummies(pd.DataFrame([datos_usuario]))

        for col in input_extras_columns:
            if col not in df_encoded_extras.columns:
                df_encoded_extras[col] = 0
        df_encoded_extras = df_encoded_extras[input_extras_columns].astype(float)

        # Guardar en sesión para usar en otras rutas
        session['datos_usuario_es'] = datos_usuario_es
        session['datos_completos'] = datos_completos
        session['df_encoded_extras'] = df_encoded_extras.to_dict(orient='records')[0]

        # Redirigir a página de resultados
        return redirect(url_for('formulario.resultado'))

    # GET
    return render_template("formulario.html",
        paises=paises,
        niveles=niveles_academicos,
        plataformas=plataformas_sociales,
        estados=estados_civiles)

# ──────────────────────────────
# Ruta para mostrar resultado resumido
# ──────────────────────────────
@formulario_bp.route('/resultado')
def resultado():
    datos_usuario_es = session.get('datos_usuario_es')
    resumen = session.get('datos_completos')

    if not datos_usuario_es or not resumen:
        return redirect(url_for('formulario.formulario'))

    # Datos para radar
    adiccion = resumen.get('Addicted_Score', 0)
    salud_mental = resumen.get('Mental_Health_Score', 0)
    afectacion_academica = resumen.get('Affects_Academic_Performance_Prob_Score', 0)

    # Etiquetas y valores
    labels = ['Adicción', 'Salud Mental', 'Impacto Académico']
    values = [adiccion, salud_mental, afectacion_academica]

    # Normalización a 0-10 por si acaso
    values = [min(max(v, 0), 10) for v in values]

    # Configuración radar
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    values += values[:1]  # cerrar el círculo
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True))

    ax.plot(angles, values, color='tab:blue', linewidth=2)
    ax.fill(angles, values, color='tab:blue', alpha=0.25)

    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, 10)
    ax.set_title("Evaluación Radar de Indicadores")

    # Guardar imagen en base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    plt.close(fig)
    img.seek(0)
    grafico_radar = base64.b64encode(img.read()).decode()

    return render_template('resultado.html', datos=datos_usuario_es, resumen=resumen, grafico_radar=grafico_radar)

# ──────────────────────────────
# Ruta para mostrar gráficas
# ──────────────────────────────
@formulario_bp.route('/graficas')
def graficas():
    df_encoded_extras_dict = session.get('df_encoded_extras')
    if not df_encoded_extras_dict:
        return redirect(url_for('formulario.formulario'))

    df_encoded_extras = pd.DataFrame([df_encoded_extras_dict])

    modelos_cargados = {
        'regresion_lineal': joblib.load('modelo/modelo_adiccion_salud_LinearRegression.pkl'),
        'regresion_logistica': joblib.load('modelo/modelo_rendimiento_academico_LogisticRegression.pkl'),
        'random_forest_clasificacion': joblib.load('modelo/modelo_rendimiento_academico_RandomForestClassifier.pkl'),
        'random_forest_regresion_adiccion': joblib.load('modelo/modelo_adiccion_RandomForestRegressor.pkl'),
        'random_forest_regresion_salud_mental': joblib.load('modelo/modelo_salud_mental_RandomForestRegressor.pkl'),
        'decision_tree_clasificacion': joblib.load('modelo/modelo_rendimiento_academico_DecisionTreeClassifier.pkl'),
        'decision_tree_regresion_adiccion': joblib.load('modelo/modelo_adiccion_DecisionTreeRegressor.pkl'),
        'decision_tree_regresion_salud_mental': joblib.load('modelo/modelo_salud_mental_DecisionTreeRegressor.pkl'),
        'scaler_kmeans': joblib.load('modelo/scaler_kmeans.pkl'),
        'kmeans': joblib.load('modelo/modelo_kmeans.pkl')
    }

    from utils.modelos_ml import calcular_modelos
    resultados_modelos = calcular_modelos(df_encoded_extras, modelos_cargados)
    resultados_list = [{'nombre': nombre, **contenido} for nombre, contenido in resultados_modelos.items()]


    return render_template("analisis_modelos.html", resultados=resultados_list)



# ──────────────────────────────
# Ruta de descarga PDF
# ──────────────────────────────
@formulario_bp.route('/descargar_pdf')
def descargar_pdf():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "PDF no encontrado", 404
