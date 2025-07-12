import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import os

# ──────────────── Conexión ────────────────
usuario = '410495'
contraseña = 'Jorger0:v'
servidor = 'mysql-terravision.alwaysdata.net'
nombre_bd = 'terravision_socialmedia'
url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
engine = create_engine(url)

# ──────────────── Cargar datos ────────────────
df = pd.read_sql("SELECT * FROM SocialMediaLectura", con=engine)
df = df.dropna()

# ──────────────── Columnas de entrada y salida ────────────────
target_cols = ['Addicted_Score', 'Mental_Health_Score']
input_cols = [
    'Age', 'Gender', 'Academic_Level', 'Country',
    'Avg_Daily_Usage_Hours', 'Most_Used_Platform',
    'Sleep_Hours_Per_Night', 'Relationship_Status',
    'Conflicts_Over_Social_Media'
]

X = pd.get_dummies(df[input_cols])
y = df[target_cols]

# ──────────────── Guardar columnas para predicción ────────────────
ruta_modelo = 'modelo'
os.makedirs(ruta_modelo, exist_ok=True)

input_extras_path = os.path.join(ruta_modelo, 'input_extras_columns.pkl')
joblib.dump(X.columns.tolist(), input_extras_path)

# ──────────────── Entrenar modelo ────────────────
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = MultiOutputRegressor(LinearRegression())
modelo.fit(X_train, y_train)

# ──────────────── Guardar modelo ────────────────
modelo_path = os.path.join(ruta_modelo, 'modelo_adiccion_LinearRegression.pkl')
joblib.dump(modelo, modelo_path)

print("Modelo de regresión lineal multisalida entrenado y guardado correctamente.")
