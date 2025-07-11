from flask import Blueprint, render_template, request, redirect
import pandas as pd
from db_config import get_engine

import os
print("RUTA DE TRABAJO ACTUAL:", os.getcwd())
print("CONTENIDO DE LA CARPETA templates:", os.listdir('templates'))


app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')


@app_routes.route('/datos')
def datos():
    return render_template('datos.html')

@app_routes.route('/upload')
def upload():
    return render_template('upload.html')


@app_routes.route('/formulario', methods=['GET', 'POST'])
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
    'Affects_Academic_Performance(True booleano)': int(request.form['Affects_Academic_Performance(True booleano)']),
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

