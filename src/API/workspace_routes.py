import uuid
import requests
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.infrastructure.persistance.workspace_repository import WorkspaceRepository
from src.domain.workspace.workspace_name import validate_workspace_name, InvalidWorkspaceNameError

workspace_bp = Blueprint("workspace", __name__)
repo = WorkspaceRepository()

WORKSPACE_URL = "http://workspace:8000/workspace"

SERVICE_TOKEN = os.getenv("WORKSPACE_SERVICE_TOKEN")


# FLASK LIMITER (JWT BASED)
def get_user_id():
    return str(get_jwt_identity())


limiter = Limiter(
    key_func=get_user_id
)


# CREATE WORKSPACE
@workspace_bp.route("/workspaces/create", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def create_workspace():

    user_id = get_jwt_identity()

    # INPUT
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Workspace name required"}), 400

    # QUOTA CHECK (max 10 workspaces)
    current_count = repo.count_by_user(user_id)

    if current_count >= 10:
        return jsonify({
            "error": "Workspace limit reached (max 10 per user)"
        }), 403

    # DOMAIN VALIDATION
    try:
        name = validate_workspace_name(name)
    except InvalidWorkspaceNameError as e:
        return jsonify({"error": str(e)}), 400

    # WORKSPACE CREATION
    workspace_id = str(uuid.uuid4())

    access_cookie = request.cookies.get("access_token_cookie")

    if not access_cookie:
        return jsonify({
            "error": "Authentication cookie missing"
        }), 401

    r = requests.post(
        f"{WORKSPACE_URL}/create",
        json={
            "user_id": user_id,
            "workspace_id": workspace_id,
            "name": name
        },
        headers={
            "X-Service-Token": SERVICE_TOKEN
        },
        cookies={
            "access_token_cookie": access_cookie
        }
    )

    if r.status_code != 200:
        return jsonify({
            "error": "Workspace service error"
        }), 500

    path = r.json()["path"]

    # DB PERSISTENCE
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


# LIST WORKSPACES
@workspace_bp.route("/workspaces", methods=["GET"])
@jwt_required()
def list_workspaces():

    user_id = get_jwt_identity()

    workspaces = repo.get_by_user(user_id)

    return jsonify({
        "workspaces": workspaces
    })

@workspace_bp.route("/workspaces/<workspace_id>", methods=["DELETE"])
@jwt_required()
def delete_workspace(workspace_id: str):
    """
    Remove um workspace do utilizador autenticado.

    Arguments:
        workspace_id: Identificador do workspace.

    Returns:
        Mensagem de sucesso ou erro.
    """

    deleted = repo.delete(workspace_id)

    if not deleted:
        return jsonify({
            "error": "Workspace não encontrado"
        }), 404

    return jsonify({
        "message": "Workspace eliminado com sucesso"
    }), 200