from flask import Blueprint, request, jsonify
from pathlib import Path
import os
import re

bp = Blueprint("workspace", __name__)

BASE_DIR = Path("/workspaces").resolve()

SERVICE_TOKEN = os.getenv("WORKSPACE_SERVICE_TOKEN")


# ================= SECURITY CHECK =================
def verify_internal_request():
    token = request.headers.get("X-Service-Token")
    return token == SERVICE_TOKEN


# ================= NAME VALIDATION =================
def validate_workspace_name(name: str) -> str:
    """
    Segurança:
    - apenas letras, números, _ e -
    - max 32 chars
    - não pode ser vazio
    """

    if not name:
        raise ValueError("Name required")

    name = name.strip()

    if len(name) > 32:
        raise ValueError("Name too long")

    # BLOQUEIA PATH TRAVERSAL E CARACTERES PERIGOSOS
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise ValueError("Invalid characters in workspace name")

    return name


# ================= CREATE WORKSPACE =================
@bp.route("/create", methods=["POST"])
def create_workspace():

    if not verify_internal_request():
        return jsonify({"error": "unauthorized"}), 401

    data = request.json

    user_id = str(data["user_id"])
    workspace_id = str(data["workspace_id"])
    name = data.get("name", "")

    # ================= VALIDATION =================
    try:
        name = validate_workspace_name(name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # ================= PATH (SAFE) =================
    path = (BASE_DIR / user_id / workspace_id).resolve()
    documents_path = path / "documents"

    if not str(path).startswith(str(BASE_DIR)):
        return jsonify({"error": "invalid path"}), 400

    documents_path.mkdir(parents=True, exist_ok=True)

    return jsonify({
        "path": str(path)
    })


# ================= WRITE DOCUMENT =================
@bp.route("/write-document", methods=["POST"])
def write_document():

    if not verify_internal_request():
        return jsonify({"error": "unauthorized"}), 401

    data = request.json

    user_id = str(data["user_id"])
    workspace_id = str(data["workspace_id"])
    doc_id = str(data["doc_id"])
    content = data.get("content", "")

    file_path = (
        BASE_DIR / user_id / workspace_id / "documents" / f"{doc_id}.md"
    ).resolve()

    if not str(file_path).startswith(str(BASE_DIR)):
        return jsonify({"error": "invalid path"}), 400

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    return jsonify({"message": "written"})


# ================= READ DOCUMENT =================
@bp.route("/read-document", methods=["POST"])
def read_document():

    if not verify_internal_request():
        return jsonify({"error": "unauthorized"}), 401

    data = request.json

    user_id = str(data["user_id"])
    workspace_id = str(data["workspace_id"])
    doc_id = str(data["doc_id"])

    file_path = (
        BASE_DIR / user_id / workspace_id /
        "documents" / f"{doc_id}.md"
    ).resolve()

    if not str(file_path).startswith(str(BASE_DIR)):
        return jsonify({"error": "invalid path"}), 400

    if not file_path.exists():
        return jsonify({"error": "document not found"}), 404

    content = file_path.read_text(
        encoding="utf-8"
    )

    return jsonify({
        "content": content
    })