# routes/prediccion.py
from flask import Blueprint, request, jsonify
import pandas as pd
import joblib

predicciones_bp = Blueprint('predicciones', __name__)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '../modelo/modelo_multioutput.pkl')
COLUMNS_PATH = os.path.join(BASE_DIR, '../modelo/input_columns.pkl')

model = joblib.load(MODEL_PATH)
input_columns = joblib.load(COLUMNS_PATH)


@predicciones_bp.route('/predecir', methods=['POST'])
def predecir():
    datos = request.get_json()
    df_nuevo = pd.DataFrame([datos])
    df_nuevo_encoded = pd.get_dummies(df_nuevo)

    for col in input_columns:
        if col not in df_nuevo_encoded:
            df_nuevo_encoded[col] = 0
    df_nuevo_encoded = df_nuevo_encoded[input_columns]

    pred = model.predict(df_nuevo_encoded)[0]
    resultado = {
        'Affects_Academic_Performance_Bool': int(round(pred[0])),
        'Addicted_Score': round(pred[1], 2),
        'Mental_Health_Score': round(pred[2], 2),
    }
    return jsonify(resultado)
