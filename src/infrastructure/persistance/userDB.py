from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import registry, sessionmaker
from src.domain.user.entities import User
from connection import (engine, SessionLocal)
import os

class UserPersistanceError(Exception):
    pass
class RegistingUserError(UserPersistanceError):pass

mapper_registry = registry()
metadata = MetaData()

user_table = Table(
    "users",
    mapper_registry.metadata,
    Column("id", String(36), primary_key=True),
    Column("username", String(50), nullable=False, unique=True),
    Column("password_hash", String(256), nullable=False),
)

def start_mappers():
    # Só mapeia uma vez
    if not mapper_registry.mappers:
        mapper_registry.map_imperatively(User, user_table, properties={
            "id": user_table.c.id,
            "_username": user_table.c.username,
            "_password_hash": user_table.c.password_hash,
        })

def create_user(new_user:User):
    start_mappers()
    try:
        session = SessionLocal()
        session.add(new_user)
        session.commit()
        print("User inserido com sucesso!")
        session.close()
    except RegistingUserError:
        print("Erro ao inserir utilizado na BD")

def find_by_username(username:str) -> bool:
    start_mappers()
    session = SessionLocal()
    try:
        user = (
            session.query(User)
            .filter(User._username == username)
            .first()
        )
        if user: return True
        else: return False
    except Exception as e:
        print(f"Erro ao procurar utilizador: {e}")
        return None

    finally:
        session.close()
