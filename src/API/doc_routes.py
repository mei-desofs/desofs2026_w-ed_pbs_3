import uuid
import requests
import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.persistance.doc_repository import DocumentRepository
from src.infrastructure.persistance.workspace_repository import WorkspaceRepository
from src.infrastructure.persistance.workspace_member_repository import WorkspaceMemberRepository

doc_bp = Blueprint("documents", __name__)

repo = DocumentRepository()
workspace_repo = WorkspaceRepository()
workspace_member_repo = WorkspaceMemberRepository()

WORKSPACE_URL = "http://workspace:8000/workspace"
SERVICE_TOKEN = os.getenv("WORKSPACE_SERVICE_TOKEN")


# ================= CREATE DOCUMENT =================
@doc_bp.route("/documents", methods=["POST"])
@jwt_required()
def create_document():

    user_id = get_jwt_identity()
    data = request.get_json()

    workspace_id = data.get("workspace_id")
    title = data.get("title")
    content = data.get("content", "")

    if not workspace_id or not title:
        return jsonify({"error": "missing fields"}), 400

    workspace = workspace_repo.get_by_id(workspace_id)

    if not workspace:
        return jsonify({"error": "workspace not found"}), 404

    doc_id = str(uuid.uuid4())

    file_path = f"/workspaces/{user_id}/{workspace_id}/documents/{doc_id}.md"

    # 1. DB
    repo.create(
        id=doc_id,
        workspace_id=workspace_id,
        title=title,
        markdown_content=content,
        file_path=file_path,
        created_by=user_id
    )

    # 2. FILE SYSTEM (OBRIGATÓRIO via workspace-server)
    r = requests.post(
        f"{WORKSPACE_URL}/write-document",
        json={
            "user_id": user_id,
            "workspace_id": workspace_id,
            "doc_id": doc_id,
            "content": content
        },
        headers={
            "X-Service-Token": SERVICE_TOKEN
        }
    )

    if r.status_code != 200:
        return jsonify({"error": "workspace write failed"}), 500

    return jsonify({
        "id": doc_id,
        "title": title
    })


# ================= LIST DOCUMENTS =================
@doc_bp.route("/documents/<workspace_id>", methods=["GET"])
@jwt_required()
def list_documents(workspace_id):

    user_id = get_jwt_identity()

    role = workspace_member_repo.get_role(
        workspace_id,
        user_id
    )

    if not role:
        return jsonify({
            "error": "access denied"
        }), 403

    return jsonify({
        "documents": repo.get_by_workspace(workspace_id)
    })


# ================= GET SINGLE DOCUMENT =================
@doc_bp.route("/document/<doc_id>", methods=["GET"])
@jwt_required()
def get_document(doc_id):

    user_id = get_jwt_identity()

    document = repo.get_by_id(doc_id)

    if document is None:
        return jsonify({
            "error": "Documento não encontrado"
        }), 404

    role = workspace_member_repo.get_role(
        document["workspace_id"],
        user_id
    )

    if not role:
        return jsonify({
            "error": "access denied"
        }), 403

    return jsonify(document), 200


# ================== DOC atualizar ==================
@doc_bp.route("/document/<doc_id>", methods=["PUT"])
@jwt_required()
def update_document(doc_id):

    user_id = get_jwt_identity()

    document = repo.get_by_id(doc_id)

    if not document:
        return jsonify({
            "error": "Documento não encontrado"
        }), 404

    role = workspace_member_repo.get_role(
        document["workspace_id"],
        user_id
    )

    if role not in ["EDITOR", "ADMIN"]:
        return jsonify({
            "error": "permission denied"
        }), 403

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    updated = repo.update(
        doc_id=doc_id,
        title=title,
        markdown_content=content
    )

    return jsonify({
        "message": "Documento atualizado"
    }), 200


# ================= DELETE =================
@doc_bp.route("/document/<doc_id>", methods=["DELETE"])
@jwt_required()
def delete_document(doc_id):

    user_id = get_jwt_identity()

    document = repo.get_by_id(doc_id)

    if not document:
        return jsonify({
            "error": "Documento não encontrado"
        }), 404

    role = workspace_member_repo.get_role(
        document["workspace_id"],
        user_id
    )

    if role != "ADMIN":
        return jsonify({
            "error": "permission denied"
        }), 403

    deleted = repo.delete(
        doc_id,
    )

    if not deleted:
        return jsonify({
            "error": "Documento não encontrado"
        }), 404

    return jsonify({
        "message": "Documento eliminado"
    }), 200