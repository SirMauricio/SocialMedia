from flask import Flask, render_template, request, redirect
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Configuración de conexión al servidor
def get_engine():
    usuario = '410495'
    contraseña = 'Jorger0:v'
    servidor = 'mysql-terravision.alwaysdata.net'
    nombre_bd = 'terravision_socialmedia'
    url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
    return create_engine(url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Datos de entrada del usuario
        age = int(request.form['Age'])
        gender = request.form['Gender']
        academic_level = request.form['Academic_Level']
        country = request.form['Country']
        avg_usage = float(request.form['Avg_Daily_Usage_Hours'])
        platform = request.form['Most_Used_Platform']
        sleep_hours = float(request.form['Sleep_Hours_Per_Night'])
        relationship = request.form['Relationship_Status']
        conflicts = int(request.form['Conflicts_Over_Social_Media'])

        # 💡 Lógica simple de predicción (puedes reemplazarla por un modelo ML real)
        addicted_score = min(100, avg_usage * 12 + conflicts * 2)
        mental_health_score = max(0, 100 - (avg_usage * 5 + conflicts))

        # Afecta el rendimiento si adicción o bajo sueño o alto conflicto
        if addicted_score > 60 or sleep_hours < 6 or conflicts > 2:
            affects = "Sí afecta el rendimiento"
            affects_bool = 1
        else:
            affects = "No afecta el rendimiento"
            affects_bool = 0

        # Diccionario final
        datos = {
            'Age': age,
            'Gender': gender,
            'Academic_Level': academic_level,
            'Country': country,
            'Avg_Daily_Usage_Hours': avg_usage,
            'Most_Used_Platform': platform,
            'Affects_Academic_Performance': affects,
            'Affects_Academic_Performance_Bool': affects_bool,
            'Sleep_Hours_Per_Night': sleep_hours,
            'Mental_Health_Score': int(mental_health_score),
            'Relationship_Status': relationship,
            'Conflicts_Over_Social_Media': conflicts,
            'Addicted_Score': int(addicted_score)
        }

        # Insertar en la base de datos
        df = pd.DataFrame([datos])
        engine = get_engine()
        df.to_sql('socialmedia_lectura', con=engine, if_exists='append', index=False)

        return redirect('/')

    return render_template('formulario.html')


if __name__ == '__main__':
    app.run(debug=True)
