import uuid
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.persistance.workspace_repository import WorkspaceRepository

workspace_bp = Blueprint("workspace", __name__)
repo = WorkspaceRepository()

WORKSPACE_URL = "http://workspace:8000/workspace"


@workspace_bp.route("/workspaces/create", methods=["POST"])
@jwt_required()
def create_workspace():

    user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({"error": "Workspace name required"}), 400

    # validação básica
    name = name.strip()

    if len(name) < 1 or len(name) > 50:
        return jsonify({"error": "Invalid workspace name"}), 400

    workspace_id = str(uuid.uuid4())

    r = requests.post(f"{WORKSPACE_URL}/create", json={
        "user_id": user_id,
        "workspace_id": workspace_id,
        "name": name
    })

    path = r.json()["path"]

    repo.create(
        id=workspace_id,
        name=name,
        folder_path=path,
        created_by=user_id
    )

    return jsonify({
        "id": workspace_id,
        "name": name
    })

@workspace_bp.route("/workspaces", methods=["GET"])
@jwt_required()
def list_workspaces():

    user_id = get_jwt_identity()

    workspaces = repo.get_by_user(user_id)

    return jsonify({
        "workspaces": workspaces
    })