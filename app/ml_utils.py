import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns
from db_config import get_engine
import joblib

def entrenar_y_predecir():
    engine = get_engine()
    df = pd.read_sql("SELECT * FROM socialmedia_lectura", con=engine)

    df = df.dropna()

    features = ['Avg_Daily_Usage_Hours', 'Mental_Health_Score', 'Conflicts_Over_Social_Media', 'Addicted_Score']
    X = df[features]
    y = df['Affects_Academic_Performance_Bool']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Guardar modelo
    joblib.dump(model, 'modelo/modelo_entrenado.pkl') #Se ha creado el directorio para guardar el modelo generado

    # Predecir
    y_pred = model.predict(X_test)

    # Crear gráfica
    df_resultados = pd.DataFrame({
        'Uso_Horas': X_test['Avg_Daily_Usage_Hours'],
        'Real': y_test,
        'Predicho': y_pred
    })

    plt.figure(figsize=(10,6))
    sns.scatterplot(data=df_resultados, x='Uso_Horas', y='Real', label='Real', alpha=0.6)
    sns.scatterplot(data=df_resultados, x='Uso_Horas', y='Predicho', label='Predicho', alpha=0.6)
    plt.title("Predicción vs Realidad - ¿Afecta el rendimiento académico?")
    plt.ylabel("0 = No afecta, 1 = Sí afecta")
    plt.xlabel("Horas de uso diario")
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/images/predicciones_vs_reales.png")
