from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import JWTManager
from src.API.user_routes import user_bp
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.domain.user.entities import User
from src.infrastructure.persistance.userDB import start_mappers, mapper_registry
from src.domain.user.entities import User
from sqlalchemy import text

import os

#Carregar .env
load_dotenv()
url=os.getenv("DATABASE_URL")
print(repr(url))

app = Flask(__name__)

#SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

# inicialização JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=5)
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

#Teste de DB
start_mappers()
mapper_registry.metadata.create_all(engine)

session = SessionLocal()
new_user = User.create(username_str="teste12345679", plain_password_str="123hashed")
session.add(new_user)
session.commit()
print("User inserido com sucesso!")
session.close()



if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = "5003")
