from flask import Blueprint, render_template, request
import pandas as pd
import os
from math import ceil

datos_bp = Blueprint('datos', __name__)

@datos_bp.route('/datos')
def mostrar_datos():
    csv_path = os.path.join('data', 'SocialMediaLectura.csv')
    page = request.args.get('page', 1, type=int)
    per_page = 50

    try:
        datos_csv = pd.read_csv(csv_path)
        total_records = len(datos_csv)
        total_pages = ceil(total_records / per_page)
        
        page = max(1, min(page, total_pages))
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
