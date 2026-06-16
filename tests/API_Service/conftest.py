import sys
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Mock do connection ANTES de qualquer import do projecto ───────────────────
sqlite_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

SqliteSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sqlite_engine
)

mock_connection = MagicMock()
mock_connection.engine = sqlite_engine
mock_connection.SessionLocal = SqliteSession
mock_connection.shared_metadata = MagicMock()
sys.modules["connection"] = mock_connection