from sqlalchemy import Table, Column, String, Boolean, TIMESTAMP, MetaData, text
from connection import engine, SessionLocal
from datetime import datetime, timezone
import uuid
import hashlib

class RefreshTokenPersistenceError(Exception):
    pass

metadata = MetaData()

refresh_token_table = Table(
    "refresh_tokens",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("user_id", String(36), nullable=False),
    Column("token_hash", String(255), nullable=False),
    Column("created_at", TIMESTAMP),
    Column("expires_at", TIMESTAMP, nullable=False),
    Column("revoked", Boolean, default=False),
)

def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()

def save_refresh_token(user_id: str, raw_token: str, expires_at: datetime) -> None:
    """Persiste um novo refresh token para o utilizador."""
    try:
        with engine.connect() as conn:
            conn.execute(refresh_token_table.insert().values(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token_hash=_hash_token(raw_token),
                expires_at=expires_at,
            ))
            conn.commit()
    except Exception as e:
        raise RefreshTokenPersistenceError(f"Erro ao guardar refresh token: {e}")

def find_valid_token(raw_token: str) -> dict | None:
    """Retorna o token se existir, não estiver revogado e não tiver expirado"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                refresh_token_table.select().where(
                    refresh_token_table.c.token_hash == _hash_token(raw_token),
                    refresh_token_table.c.revoked == False,
                    refresh_token_table.c.expires_at > datetime.now(timezone.utc),
                )
            ).mappings().first()
            return dict(result) if result else None
    except Exception as e:
        raise RefreshTokenPersistenceError(f"Erro ao procurar refresh token: {e}")

def revoke_token(raw_token: str) -> None:
    """Revoga um refresh token (logout)"""
    try:
        with engine.connect() as conn:
            conn.execute(
                refresh_token_table.update()
                .where(refresh_token_table.c.token_hash == _hash_token(raw_token))
                .values(revoked=True)
            )
            conn.commit()
    except Exception as e:
        raise RefreshTokenPersistenceError(f"Erro ao revogar refresh token: {e}")

def revoke_all_user_tokens(user_id: str) -> None:
    """Revoga todos os tokens do utilizador"""
    try:
        with engine.connect() as conn:
            conn.execute(
                refresh_token_table.update()
                .where(refresh_token_table.c.user_id == user_id)
                .values(revoked=True)
            )
            conn.commit()
    except Exception as e:
        raise RefreshTokenPersistenceError(f"Erro ao revogar tokens do utilizador: {e}")