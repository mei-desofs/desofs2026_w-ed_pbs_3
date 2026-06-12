from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pathlib import Path
import os

from src.domain.workspace.workspace_name import validate_workspace_name

bp = Blueprint("workspace", __name__)

# BASE FIXA DO SISTEMA
BASE_DIR = Path("/workspaces").resolve()


@bp.route("/create", methods=["POST"])
@jwt_required()
def create_workspace():

    data = request.json

    user_id = str(get_jwt_identity())
    workspace_id = data["workspace_id"]

    name = data.get("name", workspace_id)

    # validação de domínio
    try:
        name = validate_workspace_name(name)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # user vem do JWT (trust boundary)
    safe_user = user_id

    # PATH BUILD SEGURO
    path = (BASE_DIR / safe_user / name).resolve()

    # proteção contra path traversal
    if not str(path).startswith(str(BASE_DIR)):
        return jsonify({"error": "Invalid path detected"}), 400

    # cria diretório
    os.makedirs(path, exist_ok=True)

    return jsonify({
        "path": str(path)
    })