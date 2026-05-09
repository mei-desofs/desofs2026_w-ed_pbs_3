from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import JWTManager
from src.API.user_routes import user_bp
from datetime import timedelta


app = Flask(__name__)

# inicialização JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_SAMESITE"] = "Strict"
app.config["JWT_REFRESH_COOKIE_PATH"] = "/refresh"
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
# !!!!! Definir TRUE quando for usado HTTPS
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

# definição de blueprints
app.register_blueprint(user_bp)

@app.route('/teste', methods=["GET"])
def get_teste():
    return jsonify("sopa")

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = "5003")

