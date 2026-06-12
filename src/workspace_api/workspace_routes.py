from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os

bp = Blueprint("workspace", __name__)


@bp.route("/create", methods=["POST"])
@jwt_required()
def create_workspace():

    data = request.json

    # user_id vem do JWT
    user_id = str(get_jwt_identity())

    workspace_id = data["workspace_id"]
    name = data.get("name", workspace_id)

    # sanitização obrigatória
    safe_user = user_id.replace("..", "").replace("/", "").replace("\\", "")
    safe_name = name.replace("..", "").replace("/", "").replace("\\", "").strip()

    if not safe_name:
        return jsonify({"error": "Invalid name"}), 400

    path = os.path.join(
        "/workspaces",
        safe_user,
        safe_name
    )

    os.makedirs(path, exist_ok=True)

    return jsonify({
        "path": path
    })