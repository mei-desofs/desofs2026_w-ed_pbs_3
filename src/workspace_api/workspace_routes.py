from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from src.domain.workspace.workspace_name import validate_workspace_name

bp = Blueprint("workspace", __name__)

@bp.route("/create", methods=["POST"])
@jwt_required()
def create_workspace():

    data = request.json

    user_id = str(get_jwt_identity())
    workspace_id = data["workspace_id"]

    name = data.get("name", workspace_id)

    try:
        name = validate_workspace_name(name)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # user_id já vem do JWT → trust boundary OK
    safe_user = user_id  # já validado pelo JWT

    path = os.path.join(
        "/workspaces",
        safe_user,
        name
    )

    os.makedirs(path, exist_ok=True)

    return jsonify({
        "path": path
    })