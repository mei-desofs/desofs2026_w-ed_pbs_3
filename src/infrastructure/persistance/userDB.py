from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.orm import registry, sessionmaker
from src.domain.user.entities import User
import os
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
