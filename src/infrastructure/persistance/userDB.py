from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import registry, sessionmaker
from src.domain.user.entities import User
from src.infrastructure.persistance.workspace_member_repository import WorkspaceMemberRepository
from connection import (engine, SessionLocal,shared_metadata)
import os

class UserPersistanceError(Exception):
    pass
class RegistingUserError(UserPersistanceError):
    pass

mapper_registry = registry()
metadata = shared_metadata  # Usar o mesmo metadata partilhado para todas as tabelas
member_repo = WorkspaceMemberRepository()

# ASVS 5.0: password_hash passa a nullable=True para suportar contas puras de OAuth
user_table = Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("username", String(50), nullable=False, unique=True),
    Column("password_hash", String(256), nullable=True), 
    Column("oauth_provider", String(20), nullable=True),
    Column("oauth_id", String(256), nullable=True),
    extend_existing=True,
)
_mapper_configured = False

def start_mappers():
    global _mapper_configured
    if _mapper_configured:
        return
    # Só mapeia uma vez, agora incluindo as novas propriedades do OAuth
    mapper_registry.map_imperatively(User, user_table, properties={
            "id": user_table.c.id,
            "_username": user_table.c.username,
            "_password_hash": user_table.c.password_hash,
            "oauth_provider": user_table.c.oauth_provider,
            "oauth_id": user_table.c.oauth_id,
        })
    _mapper_configured = True

def create_user(new_user: User):
    start_mappers()
    session = SessionLocal()
    try:
        session.add(new_user)
        session.commit()
        print("User inserido com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"Erro ao inserir utilizador na BD: {e}")
        raise RegistingUserError(f"Erro ao registar utilizador local: {e}")
    finally:
        session.close()

def create_user_oauth(user: User):
    """
    Grava um utilizador via autenticação OAuth na BD
    Garante o mapeamento correto mesmo com password_hash a None
    """
    start_mappers()
    session = SessionLocal()
    try:
        session.add(user)
        session.commit()
        print(f"[DB LOG] Utilizador OAuth ({user.oauth_provider}) guardado com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"[DB ERROR] Falha ao registar utilizador OAuth: {e}")
        raise UserPersistanceError(f"Erro ao persistir conta OAuth: {e}")
    finally:
        session.close()

def get_user_by_oauth(provider: str, oauth_id: str) -> User | None:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User.oauth_provider == provider, User.oauth_id == oauth_id)
            .first()
        )
        if user:
            session.expunge(user)  # desliga o objeto da sessão de forma limpa
        return user
    except Exception as e:
        print(f"Erro ao procurar utilizador via OAuth: {e}")
        raise UserPersistanceError(f"Erro na pesquisa OAuth: {e}")
    finally:
        session.close()

def find_by_username(username: str) -> bool:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User._username == username)
            .first()
        )
        return True if user else False
    except Exception as e:
        print(f"Erro ao procurar utilizador: {e}")
        raise UserPersistanceError(f"Erro ao verificar username: {e}")
    finally:
        session.close()

def get_user(username: str, password_hash: str) -> User | None:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User._username == username, User._password_hash == password_hash)
            .first()
        )
        return user
    except Exception as e:
        print(f"Erro ao procurar utilizador: {e}")
        raise UserPersistanceError(f"Erro ao procurar utilizador: {e}")
    finally:
        session.close()

def get_user_ID_by_username(username: str) -> str | None:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User._username == username)
            .first()
        )
        return user.id if user else None
    except Exception as e:
        print(f"Erro ao procurar utilizador: {e}")
        return None
    finally:
        session.close()

def get_user_by_username(username: str) -> User | None:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User._username == username)
            .first()
        )
        if user:
            session.expunge(user)
        return user
    finally:
        session.close()

def get_user_by_id(user_id: str) -> User | None:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )
        if user:
            session.expunge(user)
        return user
    except Exception as e:
        print(f"Erro ao procurar utilizador: {e}")
        return None
    finally:
        session.close()

def update_password(user: User):
    start_mappers()
    session = SessionLocal()
    try:
        user_id_str = str(user.id)
        current_hash = str(user._password_hash) 
        
        session.query(user_table).filter(user_table.c.id == user_id_str).update(
            {user_table.c.password_hash: current_hash},
            synchronize_session=False 
        )
        
        session.commit()
        print("Password atualizada com sucesso na BD!")
        
    except Exception as e:
        session.rollback()
        print(f"[CRITICAL DATABASE ERROR] Erro ao atualizar password: {e}")
        raise UserPersistanceError(f"Erro ao atualizar password: {e}")
    finally:
        session.close()