import os
import pandas as pd
import numpy as np
import joblib
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error

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
# Cargar y preparar datos
# ──────────────────────────────
engine = get_engine()
df = pd.read_sql('SELECT * FROM SocialMediaLectura', con=engine)
df = df.dropna()

# One-hot encoding de columnas categóricas
df = pd.get_dummies(df, columns=[
    'Gender', 'Academic_Level', 'Country',
    'Most_Used_Platform', 'Relationship_Status'
])

# Definir variables de entrada y salida
target_cols = ['Affects_Academic_Performance(True booleano)', 'Addicted_Score', 'Mental_Health_Score']
columnas_a_eliminar = target_cols + ['Affects_Academic_Performance', 'Student_ID']
X = df.drop(columns=columnas_a_eliminar, errors='ignore')
y_academico = df['Affects_Academic_Performance(True booleano)']
y_adiccion = df['Addicted_Score']
y_salud = df['Mental_Health_Score']
y_multisalida = df[['Addicted_Score', 'Mental_Health_Score']]

# Guardar columnas de entrada para usarlas al predecir
os.makedirs("modelo", exist_ok=True)
joblib.dump(X.columns.tolist(), 'modelo/input_extras_columns.pkl')

# ──────────────────────────────
# Funciones de entrenamiento
# ──────────────────────────────
def entrenar_modelo_clasificacion(nombre, X, y):
    modelos = {
        'LogisticRegression': LogisticRegression(max_iter=1000),
        'RandomForestClassifier': RandomForestClassifier(),
        'DecisionTreeClassifier': DecisionTreeClassifier()
    }
    for nombre_modelo, modelo in modelos.items():
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[{nombre_modelo}] {nombre} - Accuracy: {acc:.2f}")
        joblib.dump(modelo, f"modelo/modelo_{nombre}_{nombre_modelo}.pkl")

def entrenar_modelo_regresion(nombre, X, y):
    modelos = {
        'RandomForestRegressor': RandomForestRegressor(),
        'DecisionTreeRegressor': DecisionTreeRegressor()
    }
    for nombre_modelo, modelo in modelos.items():
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"[{nombre_modelo}] {nombre} - MSE: {mse:.2f}")
        joblib.dump(modelo, f"modelo/modelo_{nombre}_{nombre_modelo}.pkl")

def entrenar_regresion_lineal_multisalida(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    modelo = MultiOutputRegressor(LinearRegression())
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"[LinearRegression] multisalida - MSE total: {mse:.2f}")

    # Guardar el modelo completo multisalida
    joblib.dump(modelo, 'modelo/modelo_adiccion_salud_LinearRegression.pkl')

    # Guardar cada modelo individual por separado
    joblib.dump(modelo.estimators_[0], 'modelo/modelo_adiccion_LinearRegression.pkl')
    joblib.dump(modelo.estimators_[1], 'modelo/modelo_salud_mental_LinearRegression.pkl')

# ──────────────────────────────
# Entrenar modelos
# ──────────────────────────────
entrenar_modelo_clasificacion("rendimiento_academico", X, y_academico)
entrenar_modelo_regresion("adiccion", X, y_adiccion)
entrenar_modelo_regresion("salud_mental", X, y_salud)
entrenar_regresion_lineal_multisalida(X, y_multisalida)

# ──────────────────────────────
# Entrenar modelo de KMeans
# ──────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X_scaled)

joblib.dump(scaler, 'modelo/scaler_kmeans.pkl')
joblib.dump(kmeans, 'modelo/modelo_kmeans.pkl')

print("Todos los modelos fueron entrenados y guardados correctamente en la carpeta /modelo.")
