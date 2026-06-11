from flask import Flask
from src.workspace_api.workspace_routes import bp

app = Flask(__name__)

app.register_blueprint(bp, url_prefix="/workspace")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)