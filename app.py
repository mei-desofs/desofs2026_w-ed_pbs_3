from flask import Flask, request, jsonify, blueprints
from flask_jwt_extended import JWTManager
from src.API.user_routes import user_bp


app = Flask(__name__)

# inicialização JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# definição de blueprints
app.register_blueprint(user_bp)

@app.route('/teste', methods=["GET"])
def get_teste():
    return jsonify("sopa")

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = "5003")

