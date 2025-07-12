import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import joblib
from utils.modelos_ml import calcular_modelos



def test_modelos_extras():
    print("⏳ Cargando columnas de entrada...")
    columnas = joblib.load('modelo/input_extras_columns.pkl')

    print("📦 Generando datos ficticios de prueba...")
    dummy_data = pd.DataFrame([{
        'Age': 21,
        'Avg_Daily_Usage_Hours': 6.5,
        'Sleep_Hours_Per_Night': 7.0,
        'Conflicts_Over_Social_Media': 2,
        'Gender_Female': 0,
        'Gender_Male': 1,
        'Gender_Other': 0,
        'Academic_Level_Graduate': 1,
        'Academic_Level_Undergraduate': 0,
        'Academic_Level_Other': 0,
        'Country_Mexico': 1,
        'Most_Used_Platform_Instagram': 1,
        'Most_Used_Platform_Facebook': 0,
        'Most_Used_Platform_TikTok': 0,
        'Relationship_Status_Single': 1,
        'Relationship_Status_Complicated': 0,
        'Relationship_Status_In Relationship': 0,
        'Relationship_Status_Other': 0
    }])

    # Asegurar que todas las columnas estén
    for col in columnas:
        if col not in dummy_data.columns:
            dummy_data[col] = 0
    dummy_data = dummy_data[columnas]

    print("🔍 Cargando modelos...")
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

    print("⚙️ Ejecutando cálculos de prueba...")
    resultados = calcular_modelos(dummy_data, modelos_cargados)

    print("\n📊 Resultados de prueba:\n")
    for nombre, datos in resultados.items():
        print(f"🔹 Modelo: {nombre}")
        print(f"    - Descripción: {datos['descripcion']}")
        print(f"    - Diagnóstico: {datos['diagnostico']}")
        print(f"    - Gráfica: {'Sí' if datos['grafica'] else 'No'}\n")

if __name__ == "__main__":
    test_modelos_extras()
