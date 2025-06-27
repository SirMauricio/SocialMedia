from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from sqlalchemy import create_engine
from math import ceil

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

@app.route('/datos')
def mostrar_datos():
    csv_path = os.path.join('data', 'SocialMediaLectura.csv')
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Registros por página
    
    try:
        # Leer todo el DataFrame
        datos_csv = pd.read_csv(csv_path)
        total_records = len(datos_csv)
        total_pages = ceil(total_records / per_page)
        
        page = max(1, min(page, total_pages))

        # Paginar los datos
        start = (page - 1) * per_page
        end = start + per_page
        datos_paginados = datos_csv.iloc[start:end]
        
        tabla_html = datos_paginados.to_html(classes='table table-striped', index=False)
        
        return render_template('datos.html', 
                            tabla_html=tabla_html,
                            current_page=page,
                            total_pages=total_pages,
                            total_records=total_records,
                            per_page=per_page)
    
        
    except Exception as e:
        return render_template('datos.html', error=str(e))
            
    

if __name__ == '__main__':
    app.run(debug=True)
