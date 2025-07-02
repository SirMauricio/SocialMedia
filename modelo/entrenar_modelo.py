import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
import joblib
from sqlalchemy import create_engine
import os

# Conexión a la base de datos
usuario = '410495'
contraseña = 'Jorger0:v'
servidor = 'mysql-terravision.alwaysdata.net'
nombre_bd = 'terravision_socialmedia'
url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
engine = create_engine(url)

# Leer datos
df = pd.read_sql("SELECT * FROM socialmedia_lectura", con=engine)

# Variables objetivo
target_cols = ['Affects_Academic_Performance(True booleano)', 'Addicted_Score', 'Mental_Health_Score']

# Asegurar que no hay nulos
df = df.dropna(subset=target_cols)

# Columnas de entrada
input_cols = df.columns.difference(target_cols + ['Affects_Academic_Performance'])

# Crear conjuntos de entrada y salida
X = pd.get_dummies(df[input_cols])
y = df[target_cols]

# Dividir datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modelo multi-salida
base_model = RandomForestRegressor(random_state=42)
model = MultiOutputRegressor(base_model)
model.fit(X_train, y_train)

# Ruta de carpeta actual (modelo/)
ruta_guardado = os.path.dirname(os.path.abspath(__file__))
print("Guardando archivos en:", ruta_guardado)

modelo_path = os.path.join(ruta_guardado, 'modelo_multioutput.pkl')
cols_path = os.path.join(ruta_guardado, 'input_columns.pkl')

try:
    joblib.dump(model, modelo_path)
    joblib.dump(X.columns.tolist(), cols_path)
    print("Archivos guardados correctamente en /modelo")
except Exception as e:
    print("Error guardando archivos:", e)
