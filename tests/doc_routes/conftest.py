import pytest
import sys
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# ── SQLite em memória ──────────────────────────────────────────────────────────
# Criamos engine e SessionLocal ANTES de qualquer import do projecto
sqlite_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

SqliteSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sqlite_engine
)

# Mock do módulo connection ANTES de qualquer import do projecto
mock_connection = MagicMock()
mock_connection.engine = sqlite_engine
mock_connection.SessionLocal = SqliteSession
sys.modules["connection"] = mock_connection


# ── Criação do schema ──────────────────────────────────────────────────────────
from sqlalchemy import text

def create_schema():
    with sqlite_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS workspaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                folder_path TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                title TEXT NOT NULL,
                markdown_content TEXT,
                file_path TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
            )
        """))
        conn.commit()

create_schema()


# ── Imports do projecto (só agora, depois do mock estar activo) ────────────────
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from src.API.doc_routes import doc_bp


# ── Fixtures ───────────────────────────────────────────────────────────────────
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_DECODE_ALGORITHMS"] = ["HS256"]
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_DECODE_AUDIENCE"] = None
    app.config["TESTING"] = True

    JWTManager(app)
    app.register_blueprint(doc_bp)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="user-test-uuid")
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def clean_db():
    """Limpa as tabelas antes de cada teste para isolamento."""
    with sqlite_engine.connect() as conn:
        conn.execute(text("DELETE FROM documents"))
        conn.execute(text("DELETE FROM workspaces"))
        conn.commit()
    yield


@pytest.fixture
def seed_workspace():
    """Insere um workspace de teste na BD."""
    with sqlite_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO workspaces (id, name, folder_path, created_by)
            VALUES ('ws-uuid-1', 'Workspace Teste', '/workspaces/user-test-uuid/ws-uuid-1', 'user-test-uuid')
        """))
        conn.commit()


@pytest.fixture
def seed_document(seed_workspace):
    """Insere um documento de teste na BD (depende de seed_workspace)."""
    with sqlite_engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO documents (id, workspace_id, title, markdown_content, file_path, created_by)
            VALUES ('doc-uuid-1', 'ws-uuid-1', 'Doc Teste', '# Olá', '/workspaces/user-test-uuid/ws-uuid-1/documents/doc-uuid-1.md', 'user-test-uuid')
        """))
        conn.commit()