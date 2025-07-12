import os
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.cluster import KMeans
import joblib

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../modelo/socialmedia_lectura.csv')
COLUMNS_PATH = os.path.join(BASE_DIR, '../modelo/input_columns.pkl')

# Cargar columnas del modelo original
input_columns = joblib.load(COLUMNS_PATH)

# Cargar dataset original
df = pd.read_csv(DATA_PATH)

df_encoded = pd.get_dummies(df)
for col in input_columns:
    if col not in df_encoded.columns:
        df_encoded[col] = 0

df_encoded = df_encoded[input_columns]

# Columnas de salida
X = df_encoded

y_ap = df['Affects_Academic_Performance(True booleano)']
y_add = df['Addicted_Score']
y_mental = df['Mental_Health_Score']

# Entrenamiento de modelos
modelo_lr = LinearRegression().fit(X, y_add)
modelo_logr = LogisticRegression(max_iter=1000).fit(X, y_ap)
modelo_rf_reg = RandomForestRegressor().fit(X, y_add)
modelo_rf_cls = RandomForestClassifier().fit(X, y_ap)
modelo_dt_reg = DecisionTreeRegressor().fit(X, y_add)
modelo_dt_cls = DecisionTreeClassifier().fit(X, y_ap)
modelo_kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

def obtener_predicciones(df_usuario):
    return {
        'Regresión Lineal (Adicción)': round(modelo_lr.predict(df_usuario)[0], 2),
        'Regresión Logística (Impacto Académico)': int(modelo_logr.predict(df_usuario)[0]),
        'Random Forest Regressor (Adicción)': round(modelo_rf_reg.predict(df_usuario)[0], 2),
        'Random Forest Classifier (Impacto Académico)': int(modelo_rf_cls.predict(df_usuario)[0]),
        'Decision Tree Regressor (Adicción)': round(modelo_dt_reg.predict(df_usuario)[0], 2),
        'Decision Tree Classifier (Impacto Académico)': int(modelo_dt_cls.predict(df_usuario)[0]),
        'KMeans Cluster': int(modelo_kmeans.predict(df_usuario)[0])
    }
