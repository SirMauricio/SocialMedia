import pandas as pd
from sqlalchemy import Integer, Float, String, Boolean
from db_config import get_engine

def detectar_tipos(df: pd.DataFrame):
    tipos_sql = {}
    for columna, tipo in df.dtypes.items():
        if pd.api.types.is_integer_dtype(tipo):
            tipos_sql[columna] = Integer()
        elif pd.api.types.is_float_dtype(tipo):
            tipos_sql[columna] = Float()
        elif pd.api.types.is_bool_dtype(tipo):
            tipos_sql[columna] = Boolean()
        elif pd.api.types.is_object_dtype(tipo):
            tipos_sql[columna] = String(500)  # Tamaño genérico
        else:
            print(f"⚠️ Tipo no reconocido: {columna} -> {tipo}")
    return tipos_sql

def importar_csv():
    ruta_csv = 'data/SocialMediaLectura.csv'
    nombre_tabla = 'socialmedia_lectura'

    try:
        # Leer CSV
        df = pd.read_csv(ruta_csv, na_values=['', ' ', 'NA', 'N/A'])

        print("🔍 Tipos detectados:")
        print(df.dtypes)

        # Reemplazar nulos por 0 o False (opcional)
        df = df.fillna({
            col: 0 if pd.api.types.is_numeric_dtype(dtype) else ''
            for col, dtype in df.dtypes.items()
        })

        # Detectar tipos SQL
        tipos_sql = detectar_tipos(df)

        # Insertar a la BD
        engine = get_engine()
        df.to_sql(nombre_tabla, con=engine, if_exists='replace', index=False, dtype=tipos_sql)

        print(f"\n✅ Importación completa. Tabla '{nombre_tabla}' creada con tipos definidos dinámicamente.")
    except Exception as e:
        print("\n❌ Error al importar el CSV:", e)

if __name__ == "__main__":
    importar_csv()
