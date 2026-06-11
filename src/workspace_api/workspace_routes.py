from flask import Blueprint, request, jsonify
from src.workspace_api.service import WorkspaceService
import os

bp = Blueprint("workspace", __name__)
service = WorkspaceService()


@bp.route("/create", methods=["POST"])
def create_workspace():

    data = request.json

    user_id = str(data["user_id"])
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

    return jsonify({"path": path})