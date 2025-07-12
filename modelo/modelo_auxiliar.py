import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
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
df = pd.read_sql("SELECT * FROM SocialMediaLectura", con=engine)

# Target binario (0 o 1)
target = 'Affects_Academic_Performance(True booleano)'

# Columnas input (excluir columnas objetivo y no relevantes)
exclude_cols = ['Affects_Academic_Performance', 'Addicted_Score', 'Mental_Health_Score', target]
input_cols = df.columns.difference(exclude_cols)

# Preparamos X y y
X = pd.get_dummies(df[input_cols])
y = df[target].astype(int)

# Dividir en entrenamiento y test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo RandomForestClassifier
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# Evaluar (opcional)
print(f"Accuracy en test: {clf.score(X_test, y_test)}")

# Guardar modelo y columnas
ruta_guardado = os.path.dirname(os.path.abspath(__file__))
modelo_path = os.path.join(ruta_guardado, 'modelo_prob_afectacion_academica.pkl')
cols_path = os.path.join(ruta_guardado, 'input_prob_afectacion_cols.pkl')

joblib.dump(clf, modelo_path)
joblib.dump(X.columns.tolist(), cols_path)

print("Modelo auxiliar guardado correctamente")
