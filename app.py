from flask import Flask
from app.routes import app_routes

app = Flask(__name__)
app.secret_key = 'clave-secreta'

# Registrar blueprint de rutas
app.register_blueprint(app_routes)

if __name__ == '__main__':
    app.run(debug=True)
