from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path
import os
import uuid

from src.domain.workspace.workspace_name import validate_workspace_name

bp = Blueprint("workspace", __name__)

# BASE FIXA DO SISTEMA
BASE_DIR = Path("/workspaces").resolve()

SERVICE_TOKEN = os.getenv("WORKSPACE_SERVICE_TOKEN")

@bp.route("/create", methods=["POST"])
def create_workspace():

    # SERVICE AUTH CHECK
    if not verify_internal_request():
        return jsonify({"error": "Unauthorized service request"}), 401

    data = request.json

    user_id = str(data["user_id"])
    name = data.get("name")

    # validações
    name = name.strip()

    if len(name) > 32:
        return jsonify({"error": "Name too long"}), 400

    # PATH TRAVERSAL
    path = (BASE_DIR / user_id / name).resolve()

    if not str(path).startswith(str(BASE_DIR.resolve())):
        return jsonify({"error": "Invalid path"}), 400

    os.makedirs(path, exist_ok=True)

    return jsonify({
        "path": str(path)
    })

def verify_internal_request():
    token = request.headers.get("X-Service-Token")
    if not token or token != SERVICE_TOKEN:
        return False
    return True