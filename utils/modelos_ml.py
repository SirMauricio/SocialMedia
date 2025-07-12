import matplotlib.pyplot as plt
import numpy as np
import base64
import joblib
from io import BytesIO

def calcular_modelos(df_input, modelos_cargados):
    resultados = {}

    # Nombres legibles para cada modelo
    nombres_amigables = {
        'regresion_lineal': 'Regresión Lineal',
        'regresion_logistica': 'Regresión Logística',
        'kmeans': 'Clustering KMeans',
        'random_forest_regresion': 'Random Forest (Regresión)',
        'random_forest_clasificacion': 'Random Forest (Clasificación)',
        'decision_tree_regresion': 'Árbol de Decisión (Regresión)',
        'decision_tree_clasificacion': 'Árbol de Decisión (Clasificación)'
    }

    # Corregir df_input para que tenga todas las columnas esperadas
    columnas_esperadas = joblib.load('modelo/input_extras_columns.pkl')
    columnas_faltantes = [col for col in columnas_esperadas if col not in df_input.columns]
    for col in columnas_faltantes:
        df_input[col] = 0
    df_input = df_input[columnas_esperadas].astype(float)

    # Para corregir error de "Student_ID" faltante en regresión lineal salud mental:
    # Vamos a asegurarnos de que el input para este modelo no incluya esa columna
    # y que los modelos entrenados usen las mismas columnas que aquí

    # ───── Regresión Lineal Multisalida ─────
    try:
        y_pred_rl = modelos_cargados['regresion_lineal'].predict(df_input)[0]
        fig, ax = plt.subplots()
        ax.bar(['Adicción', 'Salud Mental'], y_pred_rl, color='#2ecc71')
        ax.set_title("Regresión Lineal")
        ax.set_ylim(0, 10)
        resultados['regresion_lineal'] = {
            'nombre': nombres_amigables['regresion_lineal'],
            'grafica': _convertir_figura_a_base64(fig),
            'descripcion': "La regresión lineal estima cómo variables como edad o uso diario predicen salud mental y adicción.",
            'diagnostico': f"Predicción adicción: {y_pred_rl[0]:.2f}, salud mental: {y_pred_rl[1]:.2f}"
        }
    except Exception as e:
        resultados['regresion_lineal'] = {
            'nombre': nombres_amigables['regresion_lineal'],
            'grafica': None,
            'descripcion': "La regresión lineal estima cómo variables como edad o uso diario predicen salud mental y adicción.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── Regresión Logística ─────
    try:
        y_pred_log = modelos_cargados['regresion_logistica'].predict(df_input)[0]
        resultados['regresion_logistica'] = {
            'nombre': nombres_amigables['regresion_logistica'],
            'grafica': None,
            'descripcion': "Clasifica si hay afectación académica según el perfil del usuario.",
            'diagnostico': "Rendimiento Académico Afectado" if y_pred_log == 1 else "Sin Afectación Académica"
        }
    except Exception as e:
        resultados['regresion_logistica'] = {
            'nombre': nombres_amigables['regresion_logistica'],
            'grafica': None,
            'descripcion': "Clasifica si hay afectación académica según el perfil del usuario.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── KMeans ─────
    try:
        scaler = modelos_cargados['scaler_kmeans']
        df_scaled_kmeans = scaler.transform(df_input)
        cluster = modelos_cargados['kmeans'].predict(df_scaled_kmeans)[0]
        resultados['kmeans'] = {
            'nombre': nombres_amigables['kmeans'],
            'grafica': None,
            'descripcion': "Agrupa al usuario en un clúster con usuarios de características similares.",
            'diagnostico': f"Usuario pertenece al grupo (cluster) #{cluster}"
        }
    except Exception as e:
        resultados['kmeans'] = {
            'nombre': nombres_amigables['kmeans'],
            'grafica': None,
            'descripcion': "Agrupa al usuario en un clúster con usuarios de características similares.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── Random Forest Regressor ─────
    try:
        y_pred_adiccion = modelos_cargados['random_forest_regresion_adiccion'].predict(df_input)[0]
        y_pred_salud = modelos_cargados['random_forest_regresion_salud_mental'].predict(df_input)[0]
        fig, ax = plt.subplots()
        ax.bar(['Adicción', 'Salud Mental'], [y_pred_adiccion, y_pred_salud], color='#f39c12')
        ax.set_title("Random Forest Regressor")
        ax.set_ylim(0, 10)
        resultados['random_forest_regresion'] = {
            'nombre': nombres_amigables['random_forest_regresion'],
            'grafica': _convertir_figura_a_base64(fig),
            'descripcion': "Modelo basado en árboles para predecir adicción y salud mental con alta precisión.",
            'diagnostico': f"Adicción: {y_pred_adiccion:.2f}, Salud Mental: {y_pred_salud:.2f}"
        }
    except Exception as e:
        resultados['random_forest_regresion'] = {
            'nombre': nombres_amigables['random_forest_regresion'],
            'grafica': None,
            'descripcion': "Modelo basado en árboles para predecir adicción y salud mental con alta precisión.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── Random Forest Classifier ─────
    try:
        y_pred_rfc = modelos_cargados['random_forest_clasificacion'].predict(df_input)[0]
        resultados['random_forest_clasificacion'] = {
            'nombre': nombres_amigables['random_forest_clasificacion'],
            'grafica': None,
            'descripcion': "Clasifica si el rendimiento académico está comprometido.",
            'diagnostico': "Afectación Académica Detectada" if y_pred_rfc == 1 else "Sin Afectación Académica"
        }
    except Exception as e:
        resultados['random_forest_clasificacion'] = {
            'nombre': nombres_amigables['random_forest_clasificacion'],
            'grafica': None,
            'descripcion': "Clasifica si el rendimiento académico está comprometido.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── Decision Tree Regressor ─────
    try:
        y_pred_adiccion = modelos_cargados['decision_tree_regresion_adiccion'].predict(df_input)[0]
        y_pred_salud = modelos_cargados['decision_tree_regresion_salud_mental'].predict(df_input)[0]
        fig, ax = plt.subplots()
        ax.bar(['Adicción', 'Salud Mental'], [y_pred_adiccion, y_pred_salud], color='#8e44ad')
        ax.set_title("Árbol de Decisión Regressor")
        ax.set_ylim(0, 10)
        resultados['decision_tree_regresion'] = {
            'nombre': nombres_amigables['decision_tree_regresion'],
            'grafica': _convertir_figura_a_base64(fig),
            'descripcion': "Árbol de decisión que estima valores continuos de adicción y salud mental.",
            'diagnostico': f"Adicción: {y_pred_adiccion:.2f}, Salud Mental: {y_pred_salud:.2f}"
        }
    except Exception as e:
        resultados['decision_tree_regresion'] = {
            'nombre': nombres_amigables['decision_tree_regresion'],
            'grafica': None,
            'descripcion': "Árbol de decisión que estima valores continuos de adicción y salud mental.",
            'diagnostico': f"Error: {str(e)}"
        }

    # ───── Decision Tree Classifier ─────
    try:
        y_pred_dtc = modelos_cargados['decision_tree_clasificacion'].predict(df_input)[0]
        resultados['decision_tree_clasificacion'] = {
            'nombre': nombres_amigables['decision_tree_clasificacion'],
            'grafica': None,
            'descripcion': "Clasificador de árbol que predice afectación académica.",
            'diagnostico': "Afectación Académica Posible" if y_pred_dtc == 1 else "Sin Riesgo Detectado"
        }
    except Exception as e:
        resultados['decision_tree_clasificacion'] = {
            'nombre': nombres_amigables['decision_tree_clasificacion'],
            'grafica': None,
            'descripcion': "Clasificador de árbol que predice afectación académica.",
            'diagnostico': f"Error: {str(e)}"
        }

    return resultados

def _convertir_figura_a_base64(fig):
    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return base64_img
