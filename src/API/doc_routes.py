import uuid
import requests
import os
import re
from urllib.parse import quote

from flask import Blueprint, request, jsonify, send_file, Response
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.persistance.doc_repository import DocumentRepository
from src.infrastructure.persistance.workspace_repository import WorkspaceRepository
from src.infrastructure.persistance.workspace_member_repository import WorkspaceMemberRepository

from src.infrastructure.logging.logger_config import logger, sanitize_log
from src.domain.workspace.workspace_name import sanitize_filename

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

    MAX_DOC_SIZE = 100_000
    MAX_DOCS_PER_USER = 50

    user_id = get_jwt_identity()
    data = request.get_json()

    workspace_id = data.get("workspace_id")
    title = data.get("title")
    content = data.get("content", "")

    doc_count = repo.count_by_user(user_id)

    if doc_count >= MAX_DOCS_PER_USER:
        logger.warning(
            f"event=doc_quota_exceeded | who={sanitize_log(user_id)} | count={doc_count}"
        )
        return jsonify({
            "error": "Document limit reached"
        }), 403

    # ================= VALIDATION =================
    if not workspace_id or not title:
        return jsonify({"error": "missing fields"}), 400

    if len(title) > 200:
        return jsonify({"error": "title too long"}), 400

    if len(content.encode("utf-8")) > MAX_DOC_SIZE:
        logger.warning(
            f"event=doc_rejected_size | who={sanitize_log(user_id)} | size={len(content.encode('utf-8'))}"
        )
        return jsonify({"error": "document too large"}), 413

    logger.info(
        f"event=doc_create_attempt | who={sanitize_log(user_id)} | what=create_document | where=/documents"
    )

    workspace = workspace_repo.get_by_id(workspace_id)

    if not workspace:
        return jsonify({"error": "workspace not found"}), 404

    doc_id = str(uuid.uuid4())

    file_path = f"/workspaces/{user_id}/{workspace_id}/documents/{doc_id}.md"

    # ================= DB =================
    repo.create(
        id=doc_id,
        workspace_id=workspace_id,
        title=title,
        markdown_content=content,
        file_path=file_path,
        created_by=user_id
    )

    # ================= FILE SYSTEM =================
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
        repo.delete(doc_id)
        logger.warning(
            f"event=doc_create_failed | who={sanitize_log(user_id)} | workspace_id={workspace_id}"
        )
        return jsonify({"error": "workspace write failed"}), 500

    logger.info(
        f"event=doc_created | who={sanitize_log(user_id)} | doc_id={doc_id} | workspace_id={workspace_id} | file_path={file_path}"
    )

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


    logger.info(
        f"event=doc_read | who={sanitize_log(user_id)} | doc_id={doc_id}"
    )


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


    if not updated:
        return jsonify({
            "error": "Documento não encontrado"
        }), 404

    logger.info(
        f"event=doc_update | who={sanitize_log(user_id)} | doc_id={doc_id} | what=update_document"
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

    logger.info(
        f"event=doc_delete | who={sanitize_log(user_id)} | doc_id={doc_id}"
    )

    return jsonify({
        "message": "Documento eliminado"
    }), 200


# ================= EXPORT DOCUMENT =================
@doc_bp.route(
    "/document/<doc_id>/export",
    methods=["GET"]
)
@jwt_required()
def export_document(doc_id):

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

    if not role:
        return jsonify({
            "error": "access denied"
        }), 403

    r = requests.post(
        f"{WORKSPACE_URL}/read-document",
        json={
            "user_id": document["created_by"],
            "workspace_id": document["workspace_id"],
            "doc_id": doc_id
        },
        headers={
            "X-Service-Token": SERVICE_TOKEN
        }
    )

    if r.status_code != 200:
        return jsonify({
            "error": "read failed"
        }), 500

    markdown = r.json()["content"]

    safe_filename = sanitize_filename(document["title"])[:100]

    return Response(
        markdown,
        mimetype="text/markdown",
        headers={
            "Content-Disposition":
            f"attachment; filename*=UTF-8''{quote(safe_filename)}.md"
        }
    )