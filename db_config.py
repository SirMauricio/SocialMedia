from sqlalchemy import create_engine

def get_engine():
    usuario = '410495'
    contraseña = 'Jorger0:v'
    servidor = 'mysql-terravision.alwaysdata.net'
    nombre_bd = 'terravision_socialmedia'

  #Cadena de conexión
    url = f'mysql+pymysql://{usuario}:{contraseña}@{servidor}:3306/{nombre_bd}'
    engine = create_engine(url)
    return engine
