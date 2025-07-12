import os
import joblib
import pandas as pd
from flask import Blueprint, render_template
from sqlalchemy import create_engine

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import io
import base64

analisis_bp = Blueprint('analisis', __name__)

# ─────────────────────────────────────────────
# Base de datos
# ─────────────────────────────────────────────
def get_engine():
    usuario = '410495'
    contraseña = 'Jorger0:v'
    servidor = 'mysql-terravision.alwaysdata.net'
    nombre_bd = 'terravision_socialmedia'
    url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
    return create_engine(url)

# ─────────────────────────────────────────────
# Generación de gráficas
# ─────────────────────────────────────────────
def generar_grafico_barras(valor, titulo):
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.bar([titulo], [valor], color='skyblue')
    ax.set_ylim(0, 10)
    ax.set_ylabel('Valor')
    ax.set_title(titulo)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)
    return base64.b64encode(img.read()).decode('utf-8')

# ─────────────────────────────────────────────
# Calcular modelos y comparar con valores reales
# ─────────────────────────────────────────────
def calcular_modelos(datos_usuario):
    df = pd.DataFrame([datos_usuario])
    df_encoded = pd.get_dummies(df)
    input_columns = joblib.load("modelo/input_extras_columns.pkl")

    for col in input_columns:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    df_final = df_encoded[input_columns].astype(float)

    # Extraer valores reales del usuario
    reales = {
        "Adicción": float(datos_usuario.get("Addicted_Score", 0)),
        "Salud Mental": float(datos_usuario.get("Mental_Health_Score", 0)),
        "Rendimiento Académico": "Sí" if datos_usuario.get("Affects_Academic_Performance(True booleano)") == 1 else "No"
    }

    modelos = {
        "Adicción - Lineal": {
            "archivo": "modelo/modelo_adiccion_LinearRegression.pkl",
            "descripcion": "Predice el nivel de adicción percibido según el uso diario.",
            "tipo": "regresion",
            "campo_real": "Adicción"
        },
        "Salud Mental - Lineal": {
            "archivo": "modelo/modelo_salud_mental_LinearRegression.pkl",
            "descripcion": "Evalúa el bienestar mental percibido con regresión lineal.",
            "tipo": "regresion",
            "campo_real": "Salud Mental"
        },
        "Adicción - RF": {
            "archivo": "modelo/modelo_adiccion_RandomForestRegressor.pkl",
            "descripcion": "Predicción de adicción utilizando modelo de regresión con bosque aleatorio.",
            "tipo": "regresion",
            "campo_real": "Adicción"
        },
        "Salud Mental - RF": {
            "archivo": "modelo/modelo_salud_mental_RandomForestRegressor.pkl",
            "descripcion": "Predice un índice de salud mental usando bosque aleatorio.",
            "tipo": "regresion",
            "campo_real": "Salud Mental"
        },
        "Rendimiento Académico - LR": {
            "archivo": "modelo/modelo_rendimiento_academico_LogisticRegression.pkl",
            "descripcion": "Predice si el rendimiento académico se ve afectado usando regresión logística.",
            "tipo": "clasificacion",
            "campo_real": "Rendimiento Académico"
        },
        "Rendimiento Académico - RF": {
            "archivo": "modelo/modelo_rendimiento_academico_RandomForestClassifier.pkl",
            "descripcion": "Clasifica el impacto académico usando un bosque aleatorio.",
            "tipo": "clasificacion",
            "campo_real": "Rendimiento Académico"
        }
    }

    resultados = []

    for nombre, info in modelos.items():
        try:
            modelo = joblib.load(info["archivo"])
            pred = modelo.predict(df_final)

            # Convertir a valor escalar
            pred_val = float(pred[0]) if hasattr(pred, '__getitem__') else float(pred)

            diagnostico = ""
            grafica_pred = None
            grafica_real = None

            if info["tipo"] == "clasificacion":
                diagnostico = "Impacto negativo en el rendimiento académico" if round(pred_val) == 1 else "Sin impacto aparente"
                # Representación gráfica como texto
                grafica_pred = generar_grafico_barras(pred_val, "Predicción")
            else:
                if "Adicción" in nombre:
                    diagnostico = "Alta adicción" if pred_val >= 8 else "Moderada" if pred_val >= 6 else "Baja"
                else:
                    diagnostico = "Salud mental adecuada" if pred_val >= 6 else "Salud mental comprometida"
                grafica_pred = generar_grafico_barras(pred_val, "Predicción")

            # Gráfico del valor real
            valor_real = reales.get(info["campo_real"], None)
            if isinstance(valor_real, (int, float)):
                grafica_real = generar_grafico_barras(valor_real, "Valor Real")

            resultados.append({
                "nombre": nombre,
                "descripcion": info["descripcion"],
                "diagnostico": diagnostico,
                "grafica": grafica_pred,
                "grafica_real": grafica_real,
                "valor": round(pred_val, 2)
            })

        except Exception as e:
            resultados.append({
                "nombre": nombre,
                "descripcion": info["descripcion"],
                "diagnostico": f"Error: {str(e)}",
                "grafica": None,
                "grafica_real": None,
                "valor": None
            })

    return resultados, reales

# ─────────────────────────────────────────────
# Ruta principal para análisis de modelos
# ─────────────────────────────────────────────
@analisis_bp.route("/analisis_modelos")
def analisis_modelos():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM SocialMediaLectura ORDER BY Student_ID DESC LIMIT 1", con=engine)

    if df.empty:
        return "No hay datos para analizar."

    datos_usuario = df.iloc[0].to_dict()
    resultados, reales = calcular_modelos(datos_usuario)

    return render_template("analisis_modelos.html", resultados=resultados, reales=reales)
