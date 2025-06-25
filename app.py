from app import create_app

# Crear una instancia de la aplicación Flask
app = create_app()

# Ejecutar el servidor si este archivo se corre directamente
if __name__ == '__main__':
    app.run(debug=True)
