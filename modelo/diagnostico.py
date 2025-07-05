import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

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

# Validación 1: Distribución de los datos objetivo
print("\n🔍 Distribución de variables objetivo:")
for col in target_cols:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False))
    print(df[col].describe())

# Validación 2: Verificar entradas numéricas importantes
print("\n📊 Estadísticas de entradas importantes:")
print(df[['Avg_Daily_Usage_Hours', 'Sleep_Hours_Per_Night']].describe())

# Preprocesamiento
df = df.dropna(subset=target_cols)
input_cols = df.columns.difference(target_cols + ['Affects_Academic_Performance'])
X = pd.get_dummies(df[input_cols])
y = df[target_cols]

# División de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entrenar modelo
model = MultiOutputRegressor(RandomForestRegressor(random_state=42))
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Validación 3: Métricas de rendimiento
print("\n📈 Evaluación del modelo (MSE y R²):")
for i, col in enumerate(target_cols):
    true_vals = y_test[col].values
    pred_vals = [y[i] for y in y_pred]
    mse = mean_squared_error(true_vals, pred_vals)
    r2 = r2_score(true_vals, pred_vals)
    print(f"{col} -> MSE: {mse:.4f} | R²: {r2:.4f}")

# Validación 4: Mostrar primeras predicciones y valores reales
print("\n🧪 Ejemplo de predicciones (primeros 5):")
y_test_reset = y_test.reset_index(drop=True)
for i in range(5):
    print(f"\nEjemplo {i+1}")
    for j, col in enumerate(target_cols):
        print(f"{col}: Real = {y_test_reset.loc[i, col]} | Predicho = {y_pred[i][j]:.2f}")
