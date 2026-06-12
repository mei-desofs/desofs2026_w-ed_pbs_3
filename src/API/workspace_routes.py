import uuid
import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.persistance.workspace_repository import WorkspaceRepository

from src.domain.workspace.workspace_name import (
    validate_workspace_name,
    InvalidWorkspaceNameError
)

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

    name = data.get("name")

    if not name:
        return jsonify({"error": "Workspace name required"}), 400

    try:
        name = validate_workspace_name(name)
    except InvalidWorkspaceNameError as e:
        return jsonify({"error": str(e)}), 400

    workspace_id = str(uuid.uuid4())

    access_cookie = request.cookies.get("access_token_cookie")

    if not access_cookie:
        return jsonify({
            "error": "Authentication cookie missing"
        }), 401

    r = requests.post(
        f"{WORKSPACE_URL}/create",
        json={
            "workspace_id": workspace_id,
            "name": name
        },
        cookies={
            "access_token_cookie": access_cookie
        }
    )

    print("STATUS:", r.status_code)
    print("BODY:", r.text)

    if r.status_code != 200:
        return jsonify({
            "error": "Workspace service error"
        }), 500

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