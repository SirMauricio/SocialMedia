import pandas as pd
from db_config import get_engine

def importar_csv():
    ruta_csv = 'data/SocialMediaLectura.csv'
    nombre_tabla = 'socialmedia_lectura'

    try:
        # Cargar CSV, forzar que los errores se manejen como NaN
        df = pd.read_csv(ruta_csv, na_values=['', ' ', 'NA', 'N/A'])

        # Muestra valores faltantes por columna
        print("Valores nulos por columna:")
        print(df.isnull().sum())

        df = df.fillna(0)

        # Conectarse a la BD
        engine = get_engine()

        # Insertar en la tabla
        df.to_sql(nombre_tabla, con=engine, if_exists='replace', index=False)

        print(f"\n Importación exitosa. Tabla '{nombre_tabla}' creada con {len(df)} registros.")
    except Exception as e:
        print("\n Error al importar el CSV:", e)

if __name__ == "__main__":
    importar_csv()
