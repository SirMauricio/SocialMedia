from flask import Flask, render_template, request, redirect
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Configuración de conexión
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
        datos = {
            'Student_ID': request.form['Student_ID'],
            'Age': request.form['Age'],
            'Gender': request.form['Gender'],
            'Academic_Level': request.form['Academic_Level'],
            'Country': request.form['Country'],
            'Avg_Daily_Usage_Hours': request.form['Avg_Daily_Usage_Hours'],
            'Most_Used_Platform': request.form['Most_Used_Platform'],
            'Affects_Academic_Performance': request.form['Affects_Academic_Performance'],
            'Affects_Academic_Performance_Bool': int(request.form['Affects_Academic_Performance_Bool']),
            'Sleep_Hours_Per_Night': request.form['Sleep_Hours_Per_Night'],
            'Mental_Health_Score': request.form['Mental_Health_Score'],
            'Relationship_Status': request.form['Relationship_Status'],
            'Conflicts_Over_Social_Media': request.form['Conflicts_Over_Social_Media'],
            'Addicted_Score': request.form['Addicted_Score']
        }

        df = pd.DataFrame([datos])
        engine = get_engine()
        df.to_sql('socialmedia_lectura', con=engine, if_exists='append', index=False)

        return redirect('/')
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)
