from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import JWTManager
from src.API.user_routes import user_bp
from datetime import timedelta
from dotenv import load_dotenv
from connection import engine
from connection import engine,SessionLocal
import os

app = Flask(__name__)

from src.infrastructure.persistance.userDB import (start_mappers,mapper_registry)
# Inicializar ORM
start_mappers()
# Criar tabelas
mapper_registry.metadata.create_all(engine)


# inicialização JWT
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
#Allowlist the algoritmos
app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
# verificação de nbf
app.config["JWT_DECODE_LEEWAY"] = 0
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Strict"
app.config["JWT_REFRESH_COOKIE_PATH"] = "/refresh"
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
# !!!!! Definir TRUE quando for usado HTTPS
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

# definição de blueprints
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = "5003")
