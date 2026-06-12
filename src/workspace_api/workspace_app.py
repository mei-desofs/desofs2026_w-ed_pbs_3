from flask import Flask
from flask_jwt_extended import JWTManager
from src.workspace_api.workspace_routes import bp
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)

app.register_blueprint(bp, url_prefix="/workspace")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)