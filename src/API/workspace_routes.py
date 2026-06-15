import uuid
import requests
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter

from src.infrastructure.persistance.workspace_repository import WorkspaceRepository
from src.domain.workspace.workspace_name import validate_workspace_name, InvalidWorkspaceNameError
from src.infrastructure.persistance.workspace_member_repository import WorkspaceMemberRepository
from src.infrastructure.persistance.userDB import (
    get_user_by_username
)

workspace_bp = Blueprint("workspace", __name__)
repo = WorkspaceRepository()
member_repo = WorkspaceMemberRepository()

WORKSPACE_URL = "http://workspace:8000/workspace"
SERVICE_TOKEN = os.getenv("WORKSPACE_SERVICE_TOKEN")


# ================= RATE LIMITER =================
def get_user_id():
    return str(get_jwt_identity())


limiter = Limiter(key_func=get_user_id)


# ================= CREATE WORKSPACE =================
@workspace_bp.route("/workspaces/create", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def create_workspace():

    user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name")

    if not name:
        return jsonify({"error": "Workspace name required"}), 400

    # ================= QUOTA CHECK =================
    if repo.count_by_user(user_id) >= 10:
        return jsonify({
            "error": "Workspace limit reached (max 10 per user)"
        }), 403

    # ================= DOMAIN VALIDATION =================
    try:
        name = validate_workspace_name(name)
    except InvalidWorkspaceNameError as e:
        return jsonify({"error": str(e)}), 400

    workspace_id = str(uuid.uuid4())

    access_cookie = request.cookies.get("access_token_cookie")
    if not access_cookie:
        return jsonify({"error": "auth missing"}), 401

    # ================= CALL WORKSPACE SERVICE =================
    r = requests.post(
        f"{WORKSPACE_URL}/create",
        json={
            "user_id": user_id,
            "workspace_id": workspace_id,
            "name": name
        },
        headers={"X-Service-Token": SERVICE_TOKEN},
        cookies={"access_token_cookie": access_cookie}
    )

    if r.status_code != 200:
        return jsonify({"error": "workspace service error"}), 500

    path = r.json()["path"]

    # ================= DB =================
    repo.create(
        id=workspace_id,
        name=name,
        folder_path=path,
        created_by=user_id
    )

    member_repo.add_member(
        workspace_id=workspace_id,
        user_id=user_id,
        role="ADMIN"
    )

    return jsonify({
        "id": workspace_id,
        "name": name
    })


# ================= LIST =================
@workspace_bp.route("/workspaces", methods=["GET"])
@jwt_required()
def list_workspaces():

    user_id = get_jwt_identity()

    return jsonify({
        "workspaces": repo.get_by_user(user_id)
    })


# ================= DELETE =================
@workspace_bp.route("/workspaces/<workspace_id>", methods=["DELETE"])
@jwt_required()
def delete_workspace(workspace_id):

    user_id = get_jwt_identity()

    role = member_repo.get_role(
        workspace_id,
        user_id
    )

    if role != "ADMIN":
        return jsonify({
            "error": "permission denied"
        }), 403

    deleted = repo.delete(workspace_id)

    if not deleted:
        return jsonify({
            "error": "not found"
        }), 404

    return jsonify({
        "message": "deleted"
    })
# ================= ADD MEMBER =================
@workspace_bp.route(
    "/workspaces/<workspace_id>/members",
    methods=["POST"]
)
@jwt_required()
def add_member(workspace_id):

    current_user = get_jwt_identity()

    role = member_repo.get_role(
        workspace_id,
        current_user
    )

    if role != "ADMIN":
        return jsonify({
            "error": "Only admins can add members"
        }), 403

    data = request.get_json()

    username = data.get("username")
    new_role = data.get("role")

    if not username or not new_role:
        return jsonify({
            "error": "Missing fields"
        }), 400

    user = get_user_by_username(username)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    member_repo.add_member(
        workspace_id,
        user.id,
        new_role
    )

    return jsonify({
        "message": "Member added"
    })


# ================= LIST MEMBERS =================
@workspace_bp.route(
    "/workspaces/<workspace_id>/members",
    methods=["GET"]
)
@jwt_required()
def list_members(workspace_id):

    current_user = get_jwt_identity()

    role = member_repo.get_role(
        workspace_id,
        current_user
    )

    if role is None:
        return jsonify({
            "error": "Access denied"
        }), 403

    return jsonify({
        "members": member_repo.get_members(
            workspace_id
        )
    })


# ================= GET ROLE =================

@workspace_bp.route(
    "/workspaces/<workspace_id>/role",
    methods=["GET"]
)
@jwt_required()
def get_role(workspace_id):

    user_id = get_jwt_identity()

    role = member_repo.get_role(
        workspace_id,
        user_id
    )

    if not role:
        return jsonify({
            "error": "access denied"
        }), 403

    return jsonify({
        "role": role
    })