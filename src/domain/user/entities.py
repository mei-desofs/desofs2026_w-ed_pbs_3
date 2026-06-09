import uuid

from sqlalchemy.orm import reconstructor
from .value_objects import UserName, HashedPassword

class User:
    def __init__(self, user_id: str, user_name: UserName, password: HashedPassword):
        self.id = user_id
        # atributos que o ORM usa (strings)
        self._username = user_name.value
        self._password_hash = password.value

        # Value Objects em memória
        self._username_vo = user_name
        self._password_vo = password

    @classmethod
    def create(cls, username_str: str, plain_password_str: str):
        user_id = str(uuid.uuid4())
        username = UserName.validate_and_create(username_str)
        password_hash = HashedPassword.create_from_plain_text(plain_password_str)
        
        return cls(user_id, username, password_hash)
    
    @reconstructor
    def _reconstruct_from_db(self):
        self._username_vo = UserName(self._username)
        self._password_vo = HashedPassword(self._password_hash)

    @property
    def username(self) -> str:
        return self._username.value

    @property
    def hash_of_password(self) -> str:
        return self._password_hash.value

    def __repr__(self):
        return f"<User {self.id} | {self.username}>"